# Propulsión y dimensionado eléctrico

Complemento del informe técnico (secciones 1 y 4): reúne en un sitio los datos de la cadena
**batería → fusible → ESC → motor → hélice** y los márgenes que se deducen de ellos. Los números salen de
[`hardware/design/parametros.json`](../hardware/design/parametros.json) y se recalculan con:

```bash
python3 tools/perf_calc.py electrico      # esta página
python3 tools/perf_calc.py empuje         # curva de empuje
```

## Componentes

| Elemento | Dato | Origen |
|---|---|---|
| Motor | **BR4114 KV 400, brushless** (ya lo tienes) | Confirmado por el propietario |
| ESC | **80 A, 2–6S, brushless, con BEC 5 V** (DaMohony, línea 19 del Excel) | Confirmado por el propietario; conector y corriente del BEC por verificar |
| Hélice | APC 18 × 5,5 (ya la tienes) | Informe 1.2 |
| Batería | LiPo 6S 10 000 mAh, 22,2 V nominal = 222 Wh, **1,5 kg** según ficha (el informe usa 1,4) | Excel línea 20 |
| Revoluciones sin carga | 400 KV × 22,2 V ≈ 8 880 rpm (148 rev/s) | Cálculo |
| Velocidad de paso de la hélice | 5,5 in × 148 rev/s ≈ 20,7 m/s ≈ 74 km/h (sin carga) | Informe 1.2 |

## Márgenes eléctricos

| Magnitud | Valor | Comentario |
|---|---|---|
| Corriente a gas pleno (1200 W) | **54 A** a 22,2 V; **57 A** a 21,0 V | 21,0 V = 3,5 V/celda, el umbral del failsafe de batería baja |
| Límite del motor | 60 A | En el peor caso (batería baja) se trabaja al **95 %**: sin margen para subir el gas o la masa |
| ESC (80 A) | ×1,48 sobre 54 A; ×1,40 sobre 57 A | Supera el ×1,25 recomendado |
| Tasa C pedida a la batería | **5,4 C** continuos | Exigir **≥ 10 C** en la ficha (margen ×1,9) |
| Fusible | **80 A de acción lenta** (el informe decía 40 A) | 40 A < 54 A: saltaría en cada despegue. 80 A cubre el pico y no supera al ESC |
| Conector XT60 | 60 A continuos | A gas pleno se usa al 90 %: valorar **XT90** entre batería y ESC |
| Cable batería → ESC | 14 AWG vale en tramos cortos y ráfagas; **12 AWG** si el tramo es largo | Criterio de ingeniería general, no del informe |

## Corriente en vuelo

Las cifras de crucero son las del informe (modelo optimista, ±25 %):

| Velocidad | Potencia | Corriente | Autonomía (178 Wh útiles) |
|---|---:|---:|---:|
| 45 km/h | ~122 W | 5,5 A | ~87 min |
| 50 km/h | ~142 W | 6,4 A | ~75 min |
| 60 km/h | ~201 W | 9,0 A | ~53 min |

En crucero se usa **~10 % de la corriente máxima**: el sobredimensionado del ESC y del fusible solo
importa en el despegue y en un aborto de aterrizaje.

## ESC con ArduPilot

* Señal PWM estándar de 50 Hz y 1000–2000 µs (`SERVO3_MIN/MAX` en
  [`root_plane_base.parm`](../ardupilot/params/root_plane_base.parm)). El ESC brushless debe **calibrarse** con
  el asistente de ArduPilot o con el procedimiento de [9.7](construccion/9.7-pruebas-de-banco.md) antes del
  primer arranque con hélice.
* El sentido de giro se comprueba **sin hélice** ([9.4 punto 7](construccion/9.4-fuselaje-cola-y-motor.md)):
  si el avión es empujado hacia atrás, se intercambian dos cables del motor.
* El corte por batería baja lo decide ArduPilot (`BATT_LOW_VOLT` 21 V → RTL), no el ESC: si la
  calibración del sensor de batería es errónea ([S4](discrepancias-y-pendientes.md)) el motor puede
  seguir pidiendo corriente con la batería agotada.

## Qué falta por confirmar

* Conector real del ESC y de la batería (XT60 frente a XT90) — [C8](discrepancias-y-pendientes.md).
* Corriente que entrega el BEC del ESC — [C3](discrepancias-y-pendientes.md).
* Tasa C continua de la batería SSCYHT (línea 20).
* Datos medidos en banco ([9.7](construccion/9.7-pruebas-de-banco.md)): curva empuje–gas y consumo reales.
  El modelo (figura de mérito 0,7, η motor+ESC 0,8) reproduce el informe, pero **no sustituye a la medida**.
