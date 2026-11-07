# Proceso de elaboración

Cómo se construye el dron de principio a fin, en qué orden, cuánto cuesta cada paso y **qué parte
del repositorio ayuda en cada uno**. Es el resumen operativo del informe técnico (secciones 5, 8 y 9);
el detalle de cada paso está en la [guía de construcción](construccion/README.md).

> Haz las fases **en orden**. Cada una termina con una comprobación: si no se cumple, no se sigue.

```mermaid
flowchart LR
  A[0 Decidir y comprar] --> B[1 Diseño 8-10 h]
  B --> C[2 Ala 14-18 h]
  C --> D[3 Fuselaje, cola, motor, tren 8-11 h]
  D --> E[4 Tolva y tambor 6-8 h]
  E --> F[5 Electrónica fase 1 y banco 8-10 h]
  F --> G[6 Ajuste del CG 1-2 h]
  G --> H[7 Vuelos manuales 6-10 h]
  H -->|10 min estables con carga| I[8 Fase 2: ArduPilot + RPi 5 12-16 h]
  I --> J[9 Misión corta automática]
```

## Calendario y horas

Supone que es tu **primer avión** (incluye aprender las herramientas).

| # | Fase | Horas | Guía | Criterio de salida | Ayuda del repositorio |
|--:|---|---:|---|---|---|
| 0 | Compras y resolución de pendientes | 0 (5–10 días de envío) | [Materiales](materiales.md), [pendientes](discrepancias-y-pendientes.md) | Todo recibido | `hardware/bom/`, `tools/bom.py`; **pedir primero batería y hélice** (más plazo) |
| 1 | Diseño | 8–10 | [9.2](construccion/9.2-diseno-xflr5-openvsp.md) | CLmax ≥ 1,2 y CG entre 25 y 30 % MAC | `tools/perf_calc.py`, `hardware/design/parametros.json` |
| 2 | Ala | 14–18 | [9.3](construccion/9.3-ala.md) | Ala recta, sin alabeo > 3 mm, ≤ 0,8 kg | — |
| 3 | Fuselaje, cola, motor y tren | 6–8 + 2–3 | [9.4](construccion/9.4-fuselaje-cola-y-motor.md), [9.4b](construccion/9.4b-tren-de-aterrizaje.md) | Cola alineada, motor centrado (< 1°); holgura de hélice ≥ 50 mm | — |
| 4 | Tolva y tambor | 6–8 | [9.5](construccion/9.5-tolva-y-tambor.md) | 10 pulsos = 10 bolas | `seed_logic.lua` (cadencia, 6 celdas); **resolver [S2](discrepancias-y-pendientes.md)** |
| 5 | Electrónica fase 1 y banco | 8–10 | [9.6](construccion/9.6-electronica-fase-1.md), [9.7](construccion/9.7-pruebas-de-banco.md) | Curva empuje–gas medida; motor no gira con la emisora apagada | `firmware/esp32_fase1/` |
| 6 | Ajuste del CG | 1–2 | [9.8](construccion/9.8-ajuste-del-cg.md) | CG en 27 % MAC con tolva llena | `tools/perf_calc.py masas` |
| 7 | Vuelos manuales | 6–10 | [9.9](construccion/9.9-primeros-vuelos-manuales.md) | **10 min de vuelo estable con carga completa a 45–50 km/h** | [lista prevuelo](construccion/9.11-checklist-prevuelo.md) |
| 8 | Fase 2: ArduPilot + RPi 5 | 12–16 | [9.10](construccion/9.10-fase-2-ardupilot-y-rpi5.md), [9.10b](construccion/9.10b-despegue-y-aterrizaje-autonomos.md) | Misión corta automática sin incidencias | `ardupilot/`, `companion/`, SITL ([ardupilot.md](ardupilot.md)) |

**Total: 63–85 h** con el tren de aterrizaje (el informe indica 61–84 h sin contarlo; ver
[D3](discrepancias-y-pendientes.md)).

* A **12 h por semana** (dos tardes de 6 h): 6–8 semanas. A **20 h por semana**: 3–4 semanas.
* **Cómo acortarlo:** (1) imprime las plantillas y las piezas de PETG el primer día, mientras llegan los
  envíos; (2) **vuela la fase 1 antes de terminar la fase 2**: el primer vuelo manual valida el avión;
  (3) compra batería y hélice primero; (4) si quieres ahorrar diseño y corte, compra un ala de foam ya
  cortada de 3 m y añade solo el larguero y la tolva.

## Qué se puede hacer ya, sin esperar al material

Mientras llegan los pedidos (5–10 días) el repositorio permite avanzar:

1. **Cerrar los pendientes de compra** ([C2–C9, S1–S8](discrepancias-y-pendientes.md)) y decidir el mecanismo del tambor.
2. **Diseñar en XFLR5/OpenVSP** ([9.2](construccion/9.2-diseno-xflr5-openvsp.md)) y comprobar con
   `python3 tools/perf_calc.py` que las masas y el CG cuadran.
3. **Imprimir en PETG** la tolva, el tambor, los bujes, los soportes del motor y del tren.
4. **Ensayar toda la fase 2 en el simulador**: `cmake --preset ardupilot`, compilar SITL y ejecutar
   `tests/sitl/sitl_seed_drop.py`. Es la mejor forma de aprender ArduPilot sin riesgo
   (informe 9.10b punto 1: "simula antes de volar").
5. **Montar el entorno de la Raspberry Pi 5** (`pip install -e companion`).

## Ruta en dos fases

| | Fase 1 — manual | Fase 2 — autónomo |
|---|---|---|
| Cadena | Emisora → ESP32 → PCA9685 → servos y ESC | Receptor → Matek H743 (ArduPilot) → servos y ESC; RPi 5 por MAVLink |
| Sirve para | Aprender el avión, probar tolva, volar a mano | Estabilización, misiones, terreno, RTL, soltar con interlock |
| Seguridad | Failsafe 0,5 s, armado por interruptor, gas ≤ 70 % (`root_safety.h`) | Failsafes de ArduPilot, interlock Lua, RTL |
| Coste (líneas del Excel) | 708,77 € | + 212,69 € |
| Código | `firmware/esp32_fase1/` | `ardupilot/`, `companion/` |

La ESP32 **no** estabiliza el avión en fase 2: reescribir el estimador de actitud y el piloto
automático es el mayor riesgo del proyecto, y ArduPilot ya lo resuelve (informe 4.3).

## Pruebas clave (informe 6)

| Prueba | Cuándo | Cómo |
|---|---|---|
| Banco de empuje: curva empuje–gas y consumo | Antes de montar en el fuselaje | [9.7](construccion/9.7-pruebas-de-banco.md); comparar con `python3 tools/perf_calc.py empuje` (desvío > 30 % → revisar ESC y hélice) |
| Planeo: CG y estabilidad con el motor apagado | Primeros vuelos | [9.9](construccion/9.9-primeros-vuelos-manuales.md) |
| Tolva en tierra: bolas soltadas = pulsos enviados | Antes de volar con carga | 10 pulsos = 10 bolas; `SEED_TEST=1` en fase 2 |
| Failsafe en tierra: apagar la emisora con el motor **sin hélice** | Cada vez que se cambie el cableado | Gas debe bajar a cero (`tests/cpp/test_root_safety.cpp` prueba la lógica; esto prueba el cableado) |

## Reglas de seguridad que no se negocian

* **Quitar siempre la hélice** en las pruebas de tierra.
* LiPo: nunca cargar sin vigilancia; en bolsa ignífuga; a 1 C como máximo; lejos de material inflamable.
* El foam caliente desprende humos tóxicos y el hilo quema: ventilación y no tocar el hilo conectado.
* Aterrizaje automático **solo** tras 10 aterrizajes manuales limpios; los primeros, siempre en FBWA con piloto al mando.
* Soltar semillas solo en AUTO, ≥ 15 m y a velocidad estable; ante la duda, el sistema **no** suelta.
