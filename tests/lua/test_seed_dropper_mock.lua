-- Prueba de ardupilot/scripts/seed_dropper.lua contra una API de ArduPilot SIMULADA.
-- No sustituye al SITL (ver docs/ardupilot.md), pero comprueba el "pegamento": interruptor,
-- interlock en cada pulso, aborto a mitad de lote y tolerancia a datos nil.
--   lua tests/lua/test_seed_dropper_mock.lua      (desde la raíz del repositorio)
local root = (arg and arg[0] or ""):match("^(.*)/tests/lua/") or "."
package.path = root .. "/ardupilot/scripts/modules/?.lua;" .. package.path

-- ---------------------------------------------------------------- API simulada
local now_ms = 0
local aux = nil
local vehiculo = { armed = true, mode = 10, agl = 30, arspd = 12.5, home = true, terrain = false }
local mensajes, pwm_log, log_rows, params = {}, {}, {}, {}

function millis() return { tofloat = function() return now_ms end } end
gcs = { send_text = function(_, sev, txt) mensajes[#mensajes + 1] = txt end }
logger = { write = function(...) log_rows[#log_rows + 1] = { ... } end }
rc = { get_aux_cached = function(_, f) assert(f == 300); return aux end }
arming = { is_armed = function() return vehiculo.armed end }
vehicle = { get_mode = function() return vehiculo.mode end }
terrain = { enabled = function() return vehiculo.terrain end, height_above_terrain = function() return nil end }
ahrs = {
  home_is_set = function() return vehiculo.home end,
  get_relative_position_D_home = function() return -vehiculo.agl end,
  airspeed_EAS = function() return vehiculo.arspd end,
  healthy = function() return true end,
}
SRV_Channels = {
  find_channel = function(_, f) assert(f == 94); return 5 end,
  set_output_pwm = function(_, f, pwm) assert(f == 94); pwm_log[#pwm_log + 1] = pwm end,
}
param = {
  add_table = function() return true end,
  add_param = function(_, _, _, name, default) params["SEED_" .. name] = default; return true end,
}
function Parameter()
  local o = {}
  function o:init(n) self.n = n; return params[n] ~= nil end
  function o:get() return params[self.n] end
  return o
end
-- los métodos se llaman con ":" en ArduPilot; el mock acepta (self, ...)
for _, t in ipairs({ gcs, logger, rc, arming, vehicle, terrain, ahrs, SRV_Channels, param }) do
  for k, f in pairs(t) do
    local fn = f
    t[k] = function(self, ...) return fn(self, ...) end
  end
end

-- ---------------------------------------------------------------- cargar el script
local update_fn, update_ms = assert(loadfile(root .. "/ardupilot/scripts/seed_dropper.lua"))()
assert(type(update_fn) == "function" and update_ms == 50, "el script devuelve (función, 50 ms)")

local function avanza(ms)            -- ejecuta el bucle cada 50 ms durante `ms`
  for _ = 1, ms // 50 do
    now_ms = now_ms + 50
    update_fn = (update_fn() or update_fn)
  end
end
local function dispara(pos) aux = pos; avanza(50) end
local function contiene(txt)
  for _, m in ipairs(mensajes) do if m:find(txt, 1, true) then return true end end
  return false
end

local fallos, total = 0, 0
local function check(c, n) total = total + 1; if not c then fallos = fallos + 1; print("FALLO: " .. n) end end

-- 1) en reposo no mueve nada más allá del arranque
check(#pwm_log == 1 and pwm_log[1] == 1000, "al arrancar deja el tambor en reposo (1000 us)")
avanza(1000)
check(#pwm_log == 1, "sin orden no hay pulsos")

-- 2) lote completo en vuelo: 10 pulsos separados 700 ms
dispara(2)
avanza(7500)
check(#pwm_log == 11, "un lote HIGH = 10 pulsos (+1 de reposo) -> " .. #pwm_log)
check(pwm_log[2] == 1160 and pwm_log[7] == 1000, "avanza 160 us por celda y vuelve a la 0 tras 6")
check(contiene("lote completo (10 bolas)"), "avisa al GCS cuando termina")
check(#log_rows == 10 and log_rows[1][2] == "SEED", "registra cada pulso en el log")

-- 3) bloqueado en FBWA: no suelta y avisa UNA vez
local antes = #pwm_log
vehiculo.mode = 5
dispara(0); dispara(2); dispara(0); dispara(2); avanza(2000)
check(#pwm_log == antes, "en FBWA no suelta")
check(contiene("bloqueado (no esta en AUTO)"), "explica por qué")
-- (se vuelve a comprobar al final con TODOS los mensajes de la sesión)
vehiculo.mode = 10

-- 4) aborto a mitad de lote si baja de la altura mínima
dispara(0)
antes = #pwm_log
dispara(2)
avanza(1500)                       -- unos 3 pulsos
vehiculo.agl = 10                  -- por debajo de 15 m
avanza(3000)
local sueltas = #pwm_log - antes
check(sueltas >= 2 and sueltas <= 4, "se aborta a mitad del lote (pulsos: " .. sueltas .. ")")
check(contiene("abortado en"), "avisa del aborto")
vehiculo.agl = 30

-- 5) LOW cancela el lote en curso
dispara(0)
antes = #pwm_log
dispara(2); avanza(800); dispara(0); avanza(5000)
check(#pwm_log - antes <= 3, "LOW cancela el lote en curso")

-- 6) un dato que falta (sin velocidad) bloquea sin romper el script
vehiculo.arspd = nil
dispara(0); antes = #pwm_log; dispara(2); avanza(1000)
check(#pwm_log == antes, "sin velocidad no suelta")
check(not contiene("error interno"), "y no hay error interno")
vehiculo.arspd = 12.5

-- 7) en tierra (desarmado) solo con SEED_TEST=1
vehiculo.armed = false
dispara(0); antes = #pwm_log; dispara(1); avanza(500)
check(#pwm_log == antes, "desarmado sin SEED_TEST no suelta")
params["SEED_TEST"] = 1
dispara(0); dispara(1); avanza(500)
check(#pwm_log == antes + 1, "desarmado con SEED_TEST=1 suelta 1 bola (MIDDLE)")
params["SEED_TEST"] = 0

check(not contiene("error interno"), "ningún error interno en toda la sesión")
for _, m in ipairs(mensajes) do
  check(#m <= 50, "mensaje <= 50 caracteres (STATUSTEXT): " .. m)
  check(not m:find("[\128-\255]"), "mensaje solo ASCII (los acentos se corrompen en MAVLink): " .. m)
end
print(string.format("%d/%d comprobaciones correctas", total - fallos, total))
os.exit(fallos == 0 and 0 or 1)
