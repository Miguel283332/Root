-- Pruebas de ardupilot/scripts/modules/seed_logic.lua con un Lua 5.4 estándar:
--   lua tests/lua/test_seed_logic.lua            (desde la raíz del repositorio)
local script_dir = (arg and arg[0] or ""):match("^(.*)/tests/lua/") or "."
package.path = script_dir .. "/ardupilot/scripts/modules/?.lua;" .. package.path
local seed = require("seed_logic")

local fallos, total = 0, 0
local function check(cond, nombre)
  total = total + 1
  if not cond then
    fallos = fallos + 1
    print("FALLO: " .. nombre)
  end
end

local P = { enable = 1, test = 0, min_agl = 15, aspd_min = 11.5, aspd_max = 16 }
local NADA = {} -- marcador: en Lua pairs() ignora los nil, así que {agl = nil} no sobrescribiría
local function S(over)
  local s = { armed = true, mode = 10, agl = 30, airspeed = 12.5, ahrs_ok = true }
  for k, v in pairs(over or {}) do
    if v == NADA then s[k] = nil else s[k] = v end
  end
  return s
end
local function perm(s, p) local ok = seed.check_interlock(s, p or P); return ok end
local function razon(s, p) local _, r = seed.check_interlock(s, p or P); return r end

-- ---- interlock: caso feliz y cada condición por separado ----
check(perm(S()), "vuelo normal en AUTO a 30 m y 45 km/h debe permitir")
check(not perm(S({ mode = 5 })), "FBWA no debe permitir")
check(not perm(S({ mode = 0 })), "MANUAL no debe permitir")
check(not perm(S({ mode = 11 })), "RTL no debe permitir")
check(not perm(S({ agl = 14.9 })), "14,9 m (< 15) no debe permitir")
check(perm(S({ agl = 15 })), "exactamente 15 m sí permite")
check(not perm(S({ agl = NADA })), "sin altura bloquea")
check(not perm(S({ airspeed = 11.4 })), "velocidad baja bloquea")
check(not perm(S({ airspeed = 16.1 })), "velocidad alta bloquea")
check(not perm(S({ airspeed = NADA })), "sin velocidad bloquea")
check(not perm(S({ ahrs_ok = false })), "AHRS no sano bloquea")
check(not perm(S({ armed = true, agl = 0, airspeed = 0 })), "armado en tierra bloquea")

-- ---- en tierra / prueba de banco ----
check(not perm(S({ armed = false })), "desarmado sin SEED_TEST bloquea")
check(perm(S({ armed = false }), { enable = 1, test = 1, min_agl = 15, aspd_min = 11.5, aspd_max = 16 }),
      "desarmado con SEED_TEST=1 permite (banco)")
check(not perm(S({ armed = true, agl = 0 }), { enable = 1, test = 1, min_agl = 15, aspd_min = 11.5, aspd_max = 16 }),
      "SEED_TEST=1 NO salta el interlock si está armado")
check(not perm(S(), { enable = 0, test = 1, min_agl = 15, aspd_min = 11.5, aspd_max = 16 }), "SEED_ENABLE=0 bloquea siempre")
check(razon(S({ mode = 5 })) == "no esta en AUTO", "el motivo se informa")

-- ---- tambor: 6 celdas, vuelve a la 0 ----
local d = seed.new_dispenser(6, 1000, 160)
check(d:pwm() == 1000, "celda 0 = reposo")
local posiciones = {}
for i = 1, 7 do posiciones[i] = d:advance() end
check(posiciones[1] == 1160 and posiciones[5] == 1800, "avanza 160 us por celda")
check(posiciones[6] == 1000, "tras 6 pulsos vuelve a la celda 0")
check(posiciones[7] == 1160, "y sigue")

-- ---- lote: cadencia y conteo ----
local b = seed.new_batch(3, 700, 1000)
check(seed.batch_due(b, 1000), "el primer pulso sale enseguida")
seed.batch_pulse(b, 1000)
check(not seed.batch_due(b, 1699), "no antes de 700 ms")
check(seed.batch_due(b, 1700), "a los 700 ms toca el siguiente")
seed.batch_pulse(b, 1700); seed.batch_pulse(b, 2400)
check(b.done == 3 and b.remaining == 0, "3 pulsos = 3 bolas (criterio 9.5: 10 pulsos = 10 bolas)")
check(not seed.batch_due(b, 99999), "lote terminado no vuelve a salir")
local b2 = seed.new_batch(10, 700, 0)
seed.batch_pulse(b2, 0); seed.batch_abort(b2)
check(not seed.batch_due(b2, 10000) and b2.done == 1, "abortar detiene el lote")

-- ---- decodificación del interruptor ----
check(seed.decode_trigger(2, nil, 10) == 10, "HIGH = lote completo")
check(seed.decode_trigger(1, 0, 10) == 1, "MIDDLE = 1 bola")
check(seed.decode_trigger(0, 2, 10) == 0, "LOW = cancelar")
check(seed.decode_trigger(2, 2, 10) == nil, "sin cambio no dispara otra vez")
check(seed.decode_trigger(nil, nil, 10) == nil, "sin dato no hace nada")

print(string.format("%d/%d comprobaciones correctas", total - fallos, total))
os.exit(fallos == 0 and 0 or 1)
