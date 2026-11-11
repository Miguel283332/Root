--[[
  seed_logic.lua — lógica PURA del dosificador de bolas de semillas.

  No llama a ninguna API de ArduPilot (gcs, rc, ahrs...), así que se puede probar con
  un Lua 5.4 normal:  lua tests/lua/test_seed_logic.lua

  Va en APM/scripts/modules/ (la SD de la controladora) y la carga seed_dropper.lua con
  require("seed_logic"). Reglas de diseño: informe técnico 3.4 "Lógica de liberación".
--]]

local M = {}

-- Números de modo de ArduPlane (ArduPlane/mode.h)
M.MODE_AUTO = 10

--[[
  Interlock de seguridad (informe 3.4, puntos 1 y 4).

  s = estado del avión:  armed (bool), mode (int), agl (m|nil), airspeed (m/s|nil), ahrs_ok (bool)
  p = parámetros:        enable, test, min_agl, aspd_min, aspd_max

  Devuelve  ok (bool), motivo (string).

  - En vuelo (armado): solo en AUTO, por encima de min_agl y con velocidad estable.
  - En tierra (desarmado): bloqueado, salvo la prueba de banco explícita (SEED_TEST=1).
  - Armado en tierra: bloqueado (la altura no llega a min_agl).
  Cualquier dato que falte BLOQUEA: ante la duda no se suelta nada.

  Los motivos van al GCS en un STATUSTEXT: ASCII PURO (sin acentos, ArduPilot los corrompe)
  y cortos (50 caracteres por mensaje).
--]]
function M.check_interlock(s, p)
  if p.enable ~= 1 then
    return false, "SEED_ENABLE=0"
  end
  if not s.armed then
    if p.test == 1 then
      return true, "prueba de banco (desarmado)"
    end
    return false, "en tierra"
  end
  -- armado a partir de aquí: reglas de vuelo
  if not s.ahrs_ok then
    return false, "AHRS no sano"
  end
  if s.mode ~= M.MODE_AUTO then
    return false, "no esta en AUTO"
  end
  if s.agl == nil then
    return false, "sin altura"
  end
  if s.agl < p.min_agl then
    return false, string.format("altura %.0f m < %.0f m", s.agl, p.min_agl)
  end
  if s.airspeed == nil then
    return false, "sin velocidad"
  end
  if s.airspeed < p.aspd_min or s.airspeed > p.aspd_max then
    -- los mensajes del GCS (STATUSTEXT) caben en 50 caracteres: motivo corto
    return false, string.format("velocidad %.1f m/s", s.airspeed)
  end
  return true, "ok"
end

--[[
  Tambor indexado: N celdas, cada pulso avanza una celda y suelta una bola.
  La posición i del servo es  pwm_rest + i * pwm_step  (µs). Tras la última celda
  vuelve a la 0. OJO MECÁNICO: un servo de ~180° no da vueltas completas; con
  6 celdas a 60° hace falta trinquete, reductor 2:1 o servo de rotación continua
  (ver docs/discrepancias-y-pendientes.md).
--]]
function M.new_dispenser(cells, pwm_rest, pwm_step, mode)
  local d = { cells = cells, rest = pwm_rest, step = pwm_step, index = 0, mode = mode or 0 }
  -- Modo 0 (indexado): el servo se coloca en la celda i (rest + i*step); vale un servo de rotación
  --   continua con realimentación o un reductor, y vuelve a la celda 0 tras la última.
  -- Modo 1 (trinquete): un servo normal da una carrera de `step` µs y vuelve a `rest`; un trinquete
  --   (rueda libre) convierte la carrera de ida en 1/cells de vuelta del tambor y la de vuelta no lo
  --   mueve. Es la solución para un servo de ~180° (ver docs/discrepancias-y-pendientes.md, S2).
  function d:pwm()
    if self.mode == 1 then return self.rest end
    return self.rest + self.index * self.step
  end
  function d:advance()
    self.index = (self.index + 1) % self.cells
    if self.mode == 1 then return self.rest + self.step end   -- carrera de avance
    return self:pwm()
  end
  function d:return_pwm()      -- solo modo 1: posición a la que vuelve tras la carrera
    return self.rest
  end
  function d:needs_return()
    return self.mode == 1
  end
  return d
end

--[[
  Lote: n pulsos separados por period_ms (informe 3.4 punto 3: un pulso cada 0,5-1 s).
  El primer pulso sale inmediatamente.
--]]
function M.new_batch(n, period_ms, now_ms)
  return { remaining = n, period = period_ms, next_ms = now_ms, done = 0 }
end

function M.batch_due(b, now_ms)
  return b.remaining > 0 and now_ms >= b.next_ms
end

function M.batch_pulse(b, now_ms)
  b.remaining = b.remaining - 1
  b.done = b.done + 1
  b.next_ms = now_ms + b.period
end

function M.batch_abort(b)
  b.remaining = 0
end

--[[
  Interpreta la posición del interruptor auxiliar (función de RC 300 "Scripting1"):
    0 (LOW)    -> reposo: cancela el lote en curso
    1 (MIDDLE) -> 1 bola (prueba)
    2 (HIGH)   -> un lote completo (SEED_BATCH bolas)
  En la misión: DO_AUX_FUNCTION (218) con param1 = 300 y param2 = posición (0/1/2).
  Devuelve el nº de bolas pedidas, o nil si no hay flanco nuevo.
--]]
function M.decode_trigger(pos, last_pos, batch_size)
  if pos == nil or pos == last_pos then
    return nil
  end
  if pos == 2 then
    return batch_size
  elseif pos == 1 then
    return 1
  end
  return 0 -- LOW: cancelar
end

return M
