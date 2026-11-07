--[[
  seed_dropper.lua — dosificador de bolas de semillas para ArduPlane (tambor de 6 celdas).

  Instalación: copiar a la tarjeta SD de la controladora:
      APM/scripts/seed_dropper.lua
      APM/scripts/modules/seed_logic.lua
  y poner SCR_ENABLE=1 (ver ardupilot/params/root_plane_base.parm). El servo del tambor
  usa SERVOx_FUNCTION=94 (Script 1).

  Cómo se dispara (informe 3.4 + 9.10b):
    * Misión:  DO_AUX_FUNCTION (218), param1 = 300, param2 = 2 (HIGH) -> un lote
               param2 = 0 (LOW) -> fin de la pasada / cancelar
    * Emisora: RCx_OPTION = 300 en un interruptor de 3 posiciones (centro = 1 bola de prueba)
    * MAVLink: COMMAND_LONG MAV_CMD_DO_AUX_FUNCTION (lo usa companion/ en la RPi 5)

  El autopiloto decide SIEMPRE si es seguro soltar (seed_logic.check_interlock); un
  ordenador compañero solo "pide". Si el interlock falla en mitad de un lote, el lote se aborta.

  Parámetros propios (tabla SEED_, se crean al arrancar el script; reiniciar la controladora
  para verlos en la lista de parámetros la primera vez):
    SEED_ENABLE   1 activa el script
    SEED_TEST     1 permite pulsos con el avión DESARMADO (prueba de banco 9.5/9.7). Dejar a 0 en campo
    SEED_MIN_AGL  altura mínima de suelta (m)           [15, informe 3.4]
    SEED_ASPD_MIN velocidad mínima (m/s)                [11.5 = 41 km/h]
    SEED_ASPD_MAX velocidad máxima (m/s)                [16   = 58 km/h]
    SEED_BATCH    bolas por lote                        [10]
    SEED_PERIOD   ms entre pulsos                       [700, informe: 0,5-1 s]
    SEED_CELLS    celdas del tambor                     [6]
    SEED_PWM_REST PWM de la celda 0 (µs)                [1000]
    SEED_PWM_STEP incremento de PWM por celda (µs)      [160 ~ 60° en un servo de 1000-2000 µs/~375°; AJUSTAR]
--]]

local seed = require("seed_logic")

local SCRIPT_NAME = "SeedDrop"
local UPDATE_MS = 50
local AUX_FUNCTION = 300     -- RC_Channel::AUX_FUNC::SCRIPTING_1
local SERVO_FUNCTION = 94    -- SRV_Channel::k_scripting1
local PARAM_TABLE_KEY = 73   -- único entre los scripts de esta controladora
local PARAM_PREFIX = "SEED_"

-- Los STATUSTEXT de MAVLink son ASCII (los acentos llegan como "��") y caben en 50 caracteres;
-- los más largos se parten en dos mensajes. Por eso los textos que van a gcs:send_text no llevan tildes.
local MAV_SEVERITY = { ERROR = 3, WARNING = 4, INFO = 6 }

-- ---------------------------------------------------------------- parámetros
local DEFAULTS = {
  { "ENABLE", 1 }, { "TEST", 0 }, { "MIN_AGL", 15 }, { "ASPD_MIN", 11.5 }, { "ASPD_MAX", 16 },
  { "BATCH", 10 }, { "PERIOD", 700 }, { "CELLS", 6 }, { "PWM_REST", 1000 }, { "PWM_STEP", 160 },
}
assert(param:add_table(PARAM_TABLE_KEY, PARAM_PREFIX, #DEFAULTS), SCRIPT_NAME .. ": no se pudo crear la tabla de parámetros")
local P = {}
for i, d in ipairs(DEFAULTS) do
  assert(param:add_param(PARAM_TABLE_KEY, i, d[1], d[2]), SCRIPT_NAME .. ": no se pudo crear SEED_" .. d[1])
  P[d[1]] = Parameter()
  assert(P[d[1]]:init("SEED_" .. d[1]), SCRIPT_NAME .. ": no se encuentra SEED_" .. d[1])
end

local function params()
  return {
    enable = P.ENABLE:get(), test = P.TEST:get(), min_agl = P.MIN_AGL:get(),
    aspd_min = P.ASPD_MIN:get(), aspd_max = P.ASPD_MAX:get(),
  }
end

-- ---------------------------------------------------------------- estado
local servo_channel = SRV_Channels:find_channel(SERVO_FUNCTION)
if servo_channel == nil then
  gcs:send_text(MAV_SEVERITY.ERROR, SCRIPT_NAME .. ": ningun SERVOx_FUNCTION=94 (tambor)")
end

local dispenser = seed.new_dispenser(P.CELLS:get(), P.PWM_REST:get(), P.PWM_STEP:get())
local batch = nil
local last_aux_pos = nil
local last_block_reason = nil

local function altura_agl()
  -- Mejor: altura sobre el terreno (SRTM). Si no, altura sobre el punto de casa.
  if terrain:enabled() then
    local h = terrain:height_above_terrain(true)
    if h ~= nil then return h end
  end
  if ahrs:home_is_set() then
    return -ahrs:get_relative_position_D_home()
  end
  return nil
end

local function estado_avion()
  return {
    armed = arming:is_armed(),
    mode = vehicle:get_mode(),
    agl = altura_agl(),
    airspeed = ahrs:airspeed_EAS(),   -- velocidad equivalente (nil si no hay sensor)
    ahrs_ok = ahrs:healthy(),
  }
end

local function mover_tambor(pwm)
  if servo_channel ~= nil then
    SRV_Channels:set_output_pwm(SERVO_FUNCTION, math.floor(pwm))
  end
end

local function avisa_bloqueo(motivo)
  if motivo ~= last_block_reason then   -- no inundar el GCS
    gcs:send_text(MAV_SEVERITY.WARNING, SCRIPT_NAME .. ": bloqueado (" .. motivo .. ")")
    last_block_reason = motivo
  end
end

-- ---------------------------------------------------------------- bucle principal
local function update()
  local now = millis():tofloat()

  -- 1) ¿Nueva orden por el interruptor auxiliar?
  local pos = rc:get_aux_cached(AUX_FUNCTION)
  local pedidas = seed.decode_trigger(pos, last_aux_pos, P.BATCH:get())
  last_aux_pos = pos
  if pedidas ~= nil then
    if pedidas == 0 then
      if batch ~= nil and batch.remaining > 0 then
        gcs:send_text(MAV_SEVERITY.INFO, string.format("%s: lote cancelado (%d de %d)", SCRIPT_NAME, batch.done, batch.done + batch.remaining))
      end
      if batch ~= nil then seed.batch_abort(batch) end
    else
      local ok, motivo = seed.check_interlock(estado_avion(), params())
      if ok then
        batch = seed.new_batch(pedidas, P.PERIOD:get(), now)
        last_block_reason = nil
        gcs:send_text(MAV_SEVERITY.INFO, string.format("%s: lote de %d bolas", SCRIPT_NAME, pedidas))
      else
        avisa_bloqueo(motivo)
      end
    end
  end

  -- 2) Ejecutar el lote en curso (el interlock se vuelve a evaluar en CADA pulso)
  if batch ~= nil and seed.batch_due(batch, now) then
    local s = estado_avion()
    local ok, motivo = seed.check_interlock(s, params())
    if not ok then
      gcs:send_text(MAV_SEVERITY.WARNING, string.format("%s: abortado en %d (%s)", SCRIPT_NAME, batch.done, motivo))
      seed.batch_abort(batch)
    else
      mover_tambor(dispenser:advance())
      seed.batch_pulse(batch, now)
      logger:write("SEED", "Pulse,AGL,Arsp,Armed", "BffB", batch.done, s.agl or -1, s.airspeed or -1, s.armed and 1 or 0)
      if batch.remaining == 0 then
        gcs:send_text(MAV_SEVERITY.INFO, string.format("%s: lote completo (%d bolas)", SCRIPT_NAME, batch.done))
      end
    end
  end
end

-- Si update() falla se avisa y se reintenta a 1 Hz; el script no se detiene.
local function protected_wrapper()
  local success, err = pcall(update)
  if not success then
    gcs:send_text(MAV_SEVERITY.ERROR, SCRIPT_NAME .. " error interno: " .. tostring(err))
    return protected_wrapper, 1000
  end
  return protected_wrapper, UPDATE_MS
end

mover_tambor(dispenser:pwm())  -- celda 0 = reposo
gcs:send_text(MAV_SEVERITY.INFO, SCRIPT_NAME .. ": listo (" .. P.CELLS:get() .. " celdas)")
return protected_wrapper, UPDATE_MS
