# Root — dron reforestador de ala fija

Dron de ala fija (3 m de envergadura, ~7 kg al despegue, inspiración MQ-9) que siembra con **bolas de
semillas** soltadas por un tambor dosificador. Objetivo de diseño: **máxima autonomía** (76–89 min a
45–50 km/h según el informe), construcción artesanal en foam y carbono, y vuelo autónomo con
**ArduPilot**.

Este repositorio reúne **la documentación** (informe técnico, materiales, proceso de construcción) y
**la base del código** (configuración de ArduPilot, script de suelta de semillas, simulación, ordenador
compañero y firmware del vuelo manual).

## Empezar

```bash
# 1. Solo lo propio del proyecto (rápido, sin red): calculadoras, presupuesto, pruebas
cmake --preset dev && cmake --build --preset dev && ctest --preset dev

# 2. Con ArduPilot: descarga Plane-4.7.2 (≈ 1,7 GB), verifica el commit y habilita el simulador
cmake --preset ardupilot
cmake --build --preset ardupilot -t ardupilot-sitl-build     # 3-5 min la primera vez
cmake --build --preset ardupilot -t ardupilot-sitl-run       # simulador con los parámetros y scripts de Root
ctest --preset ardupilot
```

Las pruebas Lua necesitan un intérprete (`apt install lua5.4`); sin él se omiten. Más objetivos
(`ardupilot-firmware`, `ardupilot-sd-card`, `docs-bom`…) en [docs/ardupilot.md](docs/ardupilot.md).

## Mapa del repositorio

| Carpeta | Contenido |
|---|---|
| [`docs/`](docs/README.md) | Informe técnico por secciones, [materiales](docs/materiales.md), [proceso de elaboración](docs/proceso-de-elaboracion.md), [guía de construcción](docs/construccion/README.md), [ArduPilot](docs/ardupilot.md), [propulsión](docs/propulsion.md) y [**discrepancias y pendientes**](docs/discrepancias-y-pendientes.md) |
| [`hardware/`](hardware/) | `bom/` lista de materiales (Excel + CSV) y `design/parametros.json` (datos de diseño: geometría, masas, CG) |
| [`ardupilot/`](ardupilot/) | Parámetros `.parm`, script Lua `seed_dropper.lua` (suelta con interlock), misión de ejemplo, lanzador SITL |
| [`companion/`](companion/README.md) | Paquete Python de la Raspberry Pi 5: telemetría MAVLink y petición de suelta |
| [`firmware/esp32_fase1/`](firmware/esp32_fase1/README.md) | Vuelo manual (emisora → ESP32 → PCA9685) con failsafe, armado y límite de gas |
| [`tools/`](tools/) | `perf_calc.py` (prestaciones, masas y dimensionado eléctrico), `bom.py` (presupuesto), `check_params.py` (validación de `.parm`) |
| [`tests/`](tests/) | Python, Lua, C++ y la prueba de extremo a extremo en SITL |
| [`cmake/`](cmake/) | Descarga y orquestación de ArduPilot, versión fijada |

## Dos fases

| Fase 1 — vuelo manual | Fase 2 — autónomo |
|---|---|
| Emisora → ESP32 → PCA9685 → servos y ESC | Matek H743-Wing (ArduPilot) + GPS + pitot; Raspberry Pi 5 por MAVLink |
| Aprender el avión, probar la tolva | Estabilización, misiones, terreno, RTL, suelta con interlock |
| ≈ 709 € de materiales | + ≈ 213 € |

## Estado de verificación

Lo que se ha comprobado de verdad y lo que no:

| Pieza | Comprobado | **No** comprobado |
|---|---|---|
| Calculadoras (`perf_calc.py`) | Reproducen las tablas del informe (empuje, potencia, autonomía, pérdida, CG) con ≤ 5 % de error | — |
| Presupuesto (`bom.py`) | Total 921,46 € = hoja Excel; categorías y fases suman | Precios y enlaces (se importan tal cual; el 50 % son estimaciones) |
| Parámetros `.parm` | Todos existen en ArduPlane 4.7.2 y respetan su rango | Que sean buenos valores para el avión real |
| Script Lua `seed_dropper.lua` | 32 pruebas de lógica + 20 con API simulada + **vuelo completo en SITL 4.7.2**: despegue, misión, lote de 10 bolas, 10 movimientos del servo, bloqueo en tierra y por velocidad | Hardware real; el simulador vuela otro avión |
| `companion` | Pruebas unitarias; `estado`, `soltar` y `telemetria` contra SITL | UART de la Raspberry Pi 5 |
| Firmware ESP32 | 40 pruebas de la lógica de seguridad en el PC; `main.cpp` compila contra stubs | PlatformIO, ESP32 real, protocolo de la emisora |
| CMake | Descarga con verificación de commit, venv, metadata, compilación SITL, `ctest -L sitl`, SD, docs | `ardupilot-firmware` (no hay `arm-none-eabi-gcc` en el entorno de desarrollo) |

Los resultados de la verificación también destaparon problemas del propio diseño (fusible de 40 A frente
a ~54 A de consumo —ya corregido a 80 A en la lista—, tambor de 360° con servo de 180°…): están en
[Discrepancias y pendientes](docs/discrepancias-y-pendientes.md). **Léelo antes de comprar.**

## Licencia

MIT, ver [LICENSE](LICENSE).
