# ArduPilot: descarga, compilación, simulación y configuración

Todo el código de la fase 2 (vuelo autónomo) se apoya en **ArduPilot / ArduPlane**. Este proyecto
**no modifica ArduPilot**: lo descarga en una versión fijada y le añade configuración (`.parm`), un
script Lua, misiones y pruebas.

| Qué | Valor |
|---|---|
| Versión fijada | `Plane-4.7.2` (commit `fb773567…`), definida en [`cmake/ArduPilotVersion.cmake`](../cmake/ArduPilotVersion.cmake) |
| Placa de la controladora | `MatekH743` (cubre la Matek H743-Wing V1/V2/V3) |
| Tamaño de la descarga | ≈ 1,7 GB (con submódulos) en `external/ardupilot/`, ignorado por Git |
| Sistema de compilación de ArduPilot | `waf` (CMake solo lo descarga y lo orquesta) |

## 1. Requisitos

* Linux o macOS (en Windows, WSL2). `git`, `cmake ≥ 3.24`, `python3 ≥ 3.10`, compilador de C++ (`build-essential`).
* Para el **simulador** (SITL) no hace falta nada más: CMake crea un entorno Python con las dependencias
  de ArduPilot (`tools/requirements-ardupilot.txt`).
* Para el **firmware real** de la placa hace falta la cadena ARM `arm-none-eabi-gcc` (versión de
  ArduPilot: `gcc-arm-none-eabi-10-2020-q4-major`). La instala el propio script de ArduPilot:

  ```bash
  external/ardupilot/Tools/environment_install/install-prereqs-ubuntu.sh -y
  ```

## 2. Descargar y compilar con CMake

```bash
cmake --preset ardupilot                       # descarga ArduPilot 4.7.2 y verifica el commit
cmake --build --preset ardupilot -t ardupilot-sitl-build    # compila el simulador (3-5 min con 4 núcleos)
ctest --preset ardupilot                       # pruebas (incluye parámetros contra ArduPilot)
```

Si ya tienes un clon de ArduPilot: `cmake -DROOT_FETCH_ARDUPILOT=OFF -DROOT_ARDUPILOT_DIR=/ruta/ardupilot -B build`
(solo avisa, no falla, si no es el commit fijado). Sin red, `cmake --preset dev` configura solo las
partes propias del proyecto.

| Objetivo (`cmake --build <dir> -t …`) | Qué hace |
|---|---|
| `ardupilot-venv` | Crea `build/…/venv` con `empy==3.3.4`, `pymavlink`, etc. |
| `ardupilot-pdef` | Genera la metadata de parámetros de ArduPlane 4.7.2 (la usan los tests) |
| `ardupilot-sitl-build` | `waf configure --board sitl` + `waf plane` |
| `ardupilot-sitl-run` | Arranca el simulador con los parámetros y scripts de Root (`-DROOT_SITL_ARGS=` para MAVProxy) |
| `ardupilot-firmware` | Compila `arduplane.apj` y `arduplane_with_bl.hex` para `MatekH743` en `build/…/firmware/` (necesita `arm-none-eabi-gcc`) |
| `ardupilot-sd-card` | Prepara `build/…/sd-card/` con `APM/scripts`, `APM/terrain` y las carpetas `params/` y `missions/` |
| `docs-bom` | Regenera las tablas de [`materiales.md`](materiales.md) |
| `design-report` | Imprime las tablas de empuje, crucero, masas y CG |

> **Atajo para el avión real:** no hace falta compilar nada. El firmware estándar *ArduPlane 4.7.2 /
> MatekH743* que instalan Mission Planner o QGroundControl ya incluye Lua. Compilar solo es necesario
> si quieres modificar ArduPilot.

## 3. Qué hay en `ardupilot/`

```text
ardupilot/
├── params/
│   ├── root_plane_base.parm        # velocidades, despegue, aterrizaje, failsafes, modos, servos
│   ├── matek_h743_wing_v3.parm     # cableado de la placa: RPi, GPS, receptor, pitot, batería
│   ├── primeros_vuelos.parm        # capa conservadora (gas máx. 80 %) para los primeros vuelos
│   └── sitl.parm                   # solo simulador
├── scripts/
│   ├── seed_dropper.lua            # dosificador de semillas con interlock de seguridad
│   └── modules/seed_logic.lua      # su lógica pura (la que prueban los tests)
├── missions/sitl_siembra.waypoints # despegue, estabilización, pasillo de siembra, RTL
└── sitl/run_sitl.sh                # lanza SITL con todo lo anterior
```

### Parámetros y su origen

Cada valor de `root_plane_base.parm` lleva un comentario con la sección del informe de la que sale.
Los más importantes:

| Parámetro | Valor | De dónde sale |
|---|---|---|
| `AIRSPEED_MIN / CRUISE / MAX` | 12,5 / 13 / 18 m/s | 45 km/h = 1,25 × pérdida; crucero 45–50 km/h; hélice llega a ~74 km/h (informe 1.2) |
| `TKOFF_ROTATE_SPD` | 12 m/s | "unos 12 m/s para este avión" (4.7) |
| `TKOFF_ALT`, `TKOFF_LVL_ALT`, `TKOFF_THR_MAX` | 30 m, 10 m, 100 % | 4.7 (valores de partida) |
| `LAND_FLARE_ALT`, `LAND_FLARE_SEC`, `TECS_LAND_ARSPD` | 3 m, 2 s, 12 m/s | enderezado 2–3 m, aproximación 40–45 km/h (4.7) |
| `BATT_LOW_VOLT` / `BATT_CRT_VOLT` / `BATT_ARM_VOLT` | 21 / 19,8 / 22,8 V | 3,5 / 3,3 / 3,8 V por celda × 6 (9.10 y 9.11) |
| `FS_LONG_ACTN`, `BATT_FS_LOW_ACT` | RTL | "pérdida de radio → RTL; batería baja → RTL" (9.10) |
| `RTL_AUTOLAND` | 0 | RTL vuelve y **vuela en círculo**; el aterrizaje automático solo tras 10 aterrizajes manuales limpios (9.10b) |
| `TERRAIN_FOLLOW` | 1 | 9.10 punto 8 (**exige los datos SRTM en la SD**, ver §6) |

Cambios de nombre respecto al informe: `LAND_PITCH_CD` → **`LAND_PITCH_DEG`**. No se fija porque el
informe no da valor: ajustar tras los primeros aterrizajes manuales.

El validador comprueba que **todos** los parámetros existen en 4.7.2 y que sus valores están en rango:

```bash
ctest --preset ardupilot -R params_vs_ardupilot
python3 tools/check_params.py --pdef build/ardupilot/ardupilot/apm.pdef.xml ardupilot/params/*.parm
```

> Los `.parm` **no admiten comentarios al final de línea** (MAVProxy y Mission Planner los rechazan):
> el comentario va en la línea anterior. El validador lo impone.

## 4. Simulador (SITL)

```bash
cmake --build --preset ardupilot -t ardupilot-sitl-run          # deja SITL escuchando en tcp:5760
python3 -m pip install pymavlink -e companion                    # en otra terminal
python3 tests/sitl/sitl_seed_drop.py                             # prueba completa de extremo a extremo
python3 -m root_companion -c tcp:127.0.0.1:5760 estado           # el paquete de la Raspberry Pi contra el simulador
```

Para verlo en un mapa: instala `MAVProxy` y arranca con `-DROOT_SITL_ARGS="--console --map"`.

`sitl_seed_drop.py` (también `ctest -L sitl` tras `cmake --preset ardupilot-sitl-tests` y compilar el SITL; ~30 s):

1. comprueba que el script Lua está cargado (`SEED_ENABLE=1`);
2. en tierra, pide una suelta y exige que **se bloquee con motivo** (`SeedDrop: bloqueado (en tierra)`);
3. sube la misión, arma, pasa a AUTO y vuela: despegue → 40 s de estabilización → pasillo;
4. exige `lote de 10 bolas` + `lote completo (10 bolas)` y **exactamente 10 movimientos** del servo del
   tambor (`SERVO6`), con la secuencia de PWM esperada `1160, 1320, 1480, 1640, 1800, 1000, 1160, …`.

Resultado de la última ejecución: **correcto**. Esto prueba la lógica y la integración con
ArduPlane 4.7.2, **no** el comportamiento del avión real (el modelo del simulador es otro avión).

## 5. El dosificador de semillas

`seed_dropper.lua` es la pieza que convierte "soltar bolas" en algo seguro. Reglas del informe 3.4,
implementadas en `seed_logic.check_interlock` (y probadas en `tests/lua/`):

| Condición | Regla |
|---|---|
| Avión armado | Obligatorio (excepto prueba de banco, ver abajo) |
| Modo | Solo **AUTO** |
| Altura | ≥ `SEED_MIN_AGL` (15 m); sobre el **terreno** si hay datos SRTM, si no sobre casa |
| Velocidad | Entre `SEED_ASPD_MIN` (11,5 m/s) y `SEED_ASPD_MAX` (16 m/s) |
| AHRS | Sano |
| Cualquier dato que falte | **Bloquea** (ante la duda no se suelta) |
| En mitad de un lote | El interlock se evalúa **en cada pulso**; si falla, el lote se aborta |

**Cómo se dispara** (función auxiliar de RC 300, "Scripting 1"):

| Origen | Cómo |
|---|---|
| Misión | `DO_AUX_FUNCTION` (218) con `param1 = 300` y `param2 = 2` (HIGH) → lote; `param2 = 0` (LOW) → fin/cancelar. Ver `sitl_siembra.waypoints`. |
| Emisora | `RCx_OPTION = 300` en un interruptor de 3 posiciones (centro = 1 bola de prueba) |
| Raspberry Pi | `python -m root_companion soltar alta` (MAVLink `COMMAND_LONG DO_AUX_FUNCTION`); el autopiloto decide, la RPi solo pide |

Reglas de diseño de misiones:

* **Tramo de estabilización antes del pasillo** (≥ 30–40 s en círculo o en recta): justo tras despegar la
  velocidad pasa de 17–24 m/s y el interlock bloquea (observado en SITL).
* Cerrar cada pasillo con `param2 = 0`. El disparo es por **flanco**: dos `HIGH` seguidos sin `LOW` entre
  medias solo disparan el primero.
* Si el interlock rechaza la orden **no reintenta**: la pasada se pierde (fallo seguro) y el motivo queda
  en el GCS y en el registro. Ver [S7](discrepancias-y-pendientes.md).
* Adelanto de suelta: a 30 m y 45 km/h las bolas caen ~31 m por delante (`python3 tools/perf_calc.py suelta 30 12.5`);
  coloca el comando antes del punto objetivo. El viento lo modifica.

**Prueba de banco** (informe 9.5 y 9.7: "10 pulsos = 10 bolas"): con el avión **desarmado** y la hélice
quitada, `SEED_TEST = 1` permite pulsos desde el interruptor. `SEED_TEST` **no salta nada si el avión está
armado**. Dejarlo a 0 en campo.

**Parámetros del script** (se crean al primer arranque con `SCR_ENABLE=1`; reiniciar la controladora
para verlos): `SEED_ENABLE`, `SEED_TEST`, `SEED_MIN_AGL`, `SEED_ASPD_MIN`, `SEED_ASPD_MAX`, `SEED_BATCH`
(10), `SEED_PERIOD` (700 ms), `SEED_CELLS` (6), `SEED_PWM_REST` (1000 µs), `SEED_PWM_STEP` (160 µs).
`SEED_PWM_REST` debe coincidir con `SERVO6_TRIM`. `SEED_PWM_STEP` depende del mecanismo (**ver [S2](discrepancias-y-pendientes.md)**).

Registro: cada pulso escribe una línea `SEED` en el log de la controladora (`Pulse, AGL, Arsp, Armed`).

> **Alternativa del informe (9.10b punto 7):** `DO_SET_SERVO` + espera + `DO_SET_SERVO`. Funciona con un
> servo "libre", pero mueve el tambor **sin ningún interlock**. Por eso no es la opción por defecto.

## 6. Pasar de simulador a avión real

1. **Firmware.** Mission Planner → *Install Firmware* → ArduPlane 4.7.2 para `MatekH743` (o `ardupilot-firmware`).
2. **Parámetros**, en este orden: `root_plane_base.parm`, `matek_h743_wing_v3.parm`, y (primeros vuelos)
   `primeros_vuelos.parm`. Después, calibrar: acelerómetro (6 posiciones), compás al aire libre, radio, ESC y
   sentido de los servos (`SERVO5_REVERSED`).
3. **Calibrar el sensor de batería** (tensión con multímetro, corriente con vatímetro). Es lo que habilita
   el failsafe de 3,5 V por celda. Ver [S4](discrepancias-y-pendientes.md).
4. **Tarjeta SD:** `cmake --build … -t ardupilot-sd-card` y copiar `build/…/sd-card/APM/` a la SD. Añadir en
   `APM/terrain/` los `.DAT` de SRTM de la zona de vuelo: **sin ellos no se puede armar** con `TERRAIN_FOLLOW`
   activo (`PreArm: waiting for terrain data`). Ver [S5](discrepancias-y-pendientes.md).
5. Reiniciar la controladora: aparecen los parámetros `SEED_*` y el mensaje `SeedDrop: listo (6 celdas)`.
6. **Prueba de banco del tambor** (sin hélice, desarmado, `SEED_TEST=1`), después `SEED_TEST=0`.
7. Seguir [9.10 Fase 2](construccion/9.10-fase-2-ardupilot-y-rpi5.md) y
   [9.10b Despegue y aterrizaje autónomos](construccion/9.10b-despegue-y-aterrizaje-autonomos.md).

La conexión de la Raspberry Pi 5 (`SERIAL2`, 921600 baudios, TX↔RX cruzados) y la alimentación están
en [04 Electrónica](04-electronica-y-vuelo-autonomo.md); el paquete Python en [`companion/`](../companion/README.md).
