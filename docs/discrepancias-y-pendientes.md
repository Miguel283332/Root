# Discrepancias y pendientes

Al volcar el informe técnico (v3) y la hoja de materiales al repositorio, y al comprobar el código
contra ArduPilot 4.7.2, han aparecido incoherencias entre los dos documentos y puntos que **hay que
resolver antes de comprar, cablear o volar**. Esta página los recoge todos. Nada de esto se ha
corregido "en silencio" en los documentos de origen: donde el texto convertido se desvía del
original, lo dice una nota `⚠ Nota del repositorio`.

**Prioridad:** 🔴 seguridad o diseño (resolver antes de volar) · 🟠 antes de comprar · 🟡 documentación.
**Estado:** todos están **abiertos** salvo los que dicen *resuelto en el repositorio*.

## 🔴 Seguridad y diseño

| # | Qué pasa | Dónde | Qué hacer |
|---|---|---|---|
| S1 | **El fusible de 40 A saltaría a gas pleno.** A 100 % de gas el sistema consume ~1200 W / 22,2 V ≈ **54 A** (57 A si la batería cae a 21 V, el umbral del failsafe; el informe lo redondea a ~60 A en la tabla 1.1). **Corregido en la lista de materiales: fusible de 80 A de acción lenta** (margen ×1,5 sobre el consumo y ≤ el ESC). **Sigue abierto:** el conector XT60 admite 60 A continuos y aquí trabajaría al 90 % (valorar XT90 entre batería y ESC), y el cable batería→ESC debe ser de 12 AWG si el tramo es largo. | Informe 4.4 y 4.5; Excel línea 18; `python3 tools/perf_calc.py electrico` | Elegir fusible concreto (70–80 A, acción lenta), decidir XT60 frente a XT90 y confirmar la **tasa C ≥ 10 C** de la batería (piden 5,4 C continuos). |
| S2 | **El tambor de 6 celdas a 60° por pulso necesita 360° de giro**, y un servo normal de 20 kg gira ~180° (a lo sumo ~270°). Con un servo estándar solo caben 3–4 celdas por vuelta. | Informe 3.2, 3.3, 9.5; `seed_logic.lua` (el tambor vuelve a la celda 0 tras la última) | Decidir el mecanismo: servo de **rotación continua** o paso a paso, **trinquete** que convierta el vaivén en avance, o **reductor 2:1**. El script Lua y el firmware del ESP32 ya parametrizan el paso (`SEED_PWM_STEP`, `drum_step_us`), pero el valor correcto depende del mecanismo. |
| S3 | **Flaps citados pero inexistentes.** El informe da la pérdida con flaps (32 km/h, CLmax 1,5), pero el diseño solo tiene 5 servos (2 alerones, profundidad, timón, tambor) y la lista de compra tampoco incluye servos para flaps. | Informe 1.2, 1.5 | Quitar la cifra "con flaps" de las decisiones o añadir flaps (otro servo, otra salida, otro peso). El diseño actual vuela con la pérdida de **36 km/h**. |
| S4 | **Calibración de la batería sin confirmar.** El informe cita `BATT_AMP_PERVLT = 66,7` y un divisor 1:20 "según la ficha de Matek". Los valores por defecto de ArduPilot para esta placa (`hwdef.dat`) son tensión ×11 y corriente 40 A/V. Un valor erróneo desactiva en silencio el failsafe de batería baja. | Informe 9.10 punto 5; `matek_h743_wing_v3.parm` | Contrastar con la ficha de la H743-Wing **V3**; calibrar tensión con multímetro y corriente con vatímetro **antes** del primer vuelo. El `.parm` deja esos dos parámetros sin fijar a propósito. |
| S5 | **Con `TERRAIN_FOLLOW` activo, ArduPlane no deja armar hasta tener datos de terreno** (`PreArm: waiting for terrain data`; lo vimos en el simulador). | Informe 9.10 punto 8; `root_plane_base.parm` | Copiar los ficheros `.DAT` de SRTM de la zona a `APM/terrain/` en la SD **antes** de ir al campo (o que la estación de tierra los envíe). Añadirlo a la lista de revisión prevuelo. El `.parm` de SITL lo desactiva. |
| S6 | **En la fase 1 nada impide soltar semillas en tierra.** El informe exige que "con el avión en tierra nunca debe soltar", pero la ESP32 no tiene GPS ni altura: solo sabe si está armada. | Informe 3.4 punto 4, 4.1 | En fase 1 la protección es el armado por interruptor + disciplina del piloto (el tambor solo responde con el avión armado). El **interlock real** (armado, AUTO, ≥ 15 m, velocidad estable) existe únicamente en fase 2 (`seed_dropper.lua`). Documentarlo en el procedimiento de campo. |
| S7 | **La suelta desde la misión no reintenta.** El interlock se evalúa en el instante en que la misión ejecuta `DO_AUX_FUNCTION`; si falla (p. ej. velocidad alta justo tras despegar, que ocurrió en SITL con 17–24 m/s), esa pasada **no suelta nada** y queda solo en el log. Es un fallo seguro, pero se pierde la pasada. | `seed_dropper.lua`; `docs/ardupilot.md` | Diseñar las misiones con un **tramo de estabilización** (≥ 30–40 s en vuelo recto o en círculo) antes del pasillo de siembra, como hace `sitl_siembra.waypoints`. Si resulta molesto, añadir un reintento con plazo corto (decisión de diseño, no implementada). |
| S8 | **Peso real de la batería: 1,5 kg, no 1,4 kg.** El informe usa 1,40 kg; la ficha de la línea 20 del Excel dice 1,5 kg. | Informe 1.4 y 2.2; Excel línea 20 | MTOW ≈ **7,2 kg** (aún bajo el máximo de 7,5 kg) y el CG se adelanta a **24,8 % MAC** vacío / 25,5 % cargado (objetivo 25–30 %); mover la batería ~17 mm hacia atrás lo corrige. Los cálculos de prestaciones usan 6,9 kg (ver D4). Cifras reproducibles con `python3 tools/perf_calc.py masas`. Pesar el avión real y actualizar `hardware/design/parametros.json`. |
| S9 | **La hélice pusher tocaría el suelo al despegar.** Con 50 mm de holgura (informe 2.4) solo caben 3,7° de cabeceo y ArduPilot sube a 15° por defecto (exigiría 209 mm). Además el informe no define la **incidencia del ala** (≈ 4° para volar nivelado y despegar casi sin rotar). | Informe 2.4, 4.7; `python3 tools/perf_calc.py diseno` | Montar el ala con ~4° de incidencia, holgura ≥ 70–100 mm y aleta ventral. Parámetros ya ajustados (`TKOFF_LVL_PITCH=5`, misión a 5°). Detalle en [Decisiones de diseño](decisiones-de-diseno.md). |
| S10 | **Diedro del ala sin definir.** El informe monta el ala recta (diedro 0°) con un larguero recto cruzando el centro. En la fase 1 no hay estabilización electrónica y un ala sin diedro es poco estable en alabeo. | Informe 2.1, 9.2, 9.3 | Decidir antes de cortar: 2–3° por semiala (exige cortar las juntas inclinadas y cambiar la unión central) o aceptar un ala recta y confiar en la fase 2 (FBWA). Ver [Decisiones de diseño](decisiones-de-diseno.md). |

## 🟠 Antes de comprar

| # | Qué pasa | Dónde | Qué hacer |
|---|---|---|---|
| C2 | **Dos BEC distintos con el mismo papel.** El informe 9.6 habla de un "BEC 6 V / 10 A (HENGE)"; la lista de compra incluye un "UBEC Switch 6/7,4/8,4 V". | Informe 9.6; Excel línea 22 | Fijar el modelo, confirmar los 6 V (los servos admiten 6,8 V máx.) y que 10 A cubra 5 servos + PCA9685. |
| C3 | **Alimentación de ESP32 y PCA9685 desde el BEC del ESC.** El informe 9.6 punto 2 los alimenta con el BEC interno del ESC (5 V / 5 A), pero la ficha del ESC en el Excel no especifica la corriente del BEC. | Informe 9.6 punto 2; Excel línea 19 | Confirmar la corriente del BEC del ESC o alimentar ESP32 + PCA9685 (lógica) desde el BEC de 6 V con un regulador a 5 V. |
| C4 | **Medidas y material del foam no coinciden.** Excel: plancha **1250** × 600 mm; informe: **1200** × 600. Excel: foam de **9,7 mm** del fuselaje en un anuncio que es de **5 mm** y de "cartón pluma / plancha interior de cartón"; informe: **XPS 10 mm**. | Excel líneas 1–3; informe 2.3 | Confirmar tipo (XPS frente a cartón pluma), grosor y medida antes de pedir. Las piezas del ala (750 × 300) caben en ambas medidas. |
| C5 | **El 50 % del presupuesto son estimaciones.** 19 de las 30 líneas incluidas (**462,95 €**) no tienen precio verificado (sin precio visible o sin enlace). | Excel, columna "Notas"; `python3 tools/bom.py` | Verificar en tienda, empezando por las líneas grandes: batería (85 €), controladora (verificada), ESC, tubos 16/14, servos. |
| C6 | **El presupuesto supera los 700 € disponibles en 221,46 €.** Total 921,46 €; solo la fase 1 ya cuesta 708,77 €. | Informe 7; Excel `G37:G39` | Opciones del propio informe: aplazar cámara y pitot a fase 2 (~70 €), servos más ligeros en alerones (30–40 €), buscar tubos de 12 mm más baratos. No hay plan que baje de 700 € sin recortar. |
| C7 | **El Excel se contradice sobre la batería.** La nota final dice "No incluido: … la batería de 10 Ah" pero la línea 20 la incluye (85 €) y está en el total. | Excel `Lista de compra` filas de notas | Se cuenta dentro del total (921,46 €). Corregir la nota en el Excel. |
| C8 | **La hoja "Supuestos" menciona piezas que ya no están.** Los puntos 5 y 6 hablan de un ESC SunnySky X80A "60A" y de una batería HRB con XT90, que no aparecen en la lista actual. | Excel `Supuestos` | Borrar o actualizar esos dos puntos. Lo que sí sigue vigente: comprobar el conector XT60 del ESC y de la batería (línea 20: "elegir la versión XT60"). |
| C9 | **Protocolo de la emisora sin confirmar.** Para la opción B del informe 4.6 (mantener la emisora actual con la ESP32 como receptor SBUS/CRSF) hace falta saber qué protocolo usa el enlace actual. | Informe 4.6 | Indicar el protocolo. El firmware de la fase 1 arranca en FAILSAFE mientras no haya uno definido (`-DRC_SBUS` para SBUS). |
| C10 | **Faltan herramientas en la lista de compra**: soldador y estaño, multímetro, cargador LiPo 6S con balanceo, bolsa ignífuga, vatímetro, báscula, servo tester (la guía 9.1 las pide o la soldadura las exige). | Informe 9.1; Excel | Añadirlas al presupuesto: ~150–300 € orientativos si se parte de cero ([04 principiantes](principiantes/04-taller-herramientas-y-practica.md)). |
| C11 | **Normativa sin resolver**: registro de operador, formación del piloto, zona de vuelo y, sobre todo, soltar objetos desde un dron (en categoría abierta no suele estar permitido; la siembra probablemente exige categoría específica). | — | Consultar a AESA y a un club antes de volar fuera de un campo de aeromodelismo ([06 principiantes](principiantes/06-aprender-a-volar-y-normativa.md)). |

## 🟡 Documentación

| # | Qué pasa | Dónde | Estado |
|---|---|---|---|
| D1 | El informe cita `materiales_dron_v2.xlsx` y en 2.3 dice **861,46 €** (supera en ~160 €); el resumen y la sección 7 dicen **921 €** (supera en ~220 €), que coincide con el Excel. | Informe 0, 2.3, 7 | *Resuelto en el repositorio*: 2.3 se corrigió a 921,46 € y se apunta al fichero real, con nota. |
| D2 | El Excel entregado se llama `…_v3.xlsx` pero su hoja dice "versión 4, con tren de aterrizaje". | Excel | Se guarda como `hardware/bom/materiales_dron.xlsx` (sin versión). |
| D3 | Las horas no suman lo que dice la tabla: la hoja de ruta (sección 5 / 8) suma **61–82 h** sin el tren de aterrizaje; dice "61–84". Con el tren (9.4b, 2–3 h) son **63–85 h**, que cuadra con el "60–85" del resumen. | Informe 0, 5, 8 | Anotado en `05-hoja-de-ruta.md` y `08-tiempo.md`. |
| D4 | La tabla 1.1 calcula el empuje/peso con **6,9 kg**; la sección 1.4 da un MTOW de **7,1 kg** (7,2 con la batería real). | Informe 1.1, 1.4, 1.5 | Anotado en `01-viabilidad-y-propulsion.md`. Con 7,1 kg el empuje/peso a gas pleno es 0,82 (no 0,84). |
| D5 | El diagrama de 2.2 mostraba "BATERIA 6S 0,7 kg" y cotas del morro que no coinciden con la tabla (batería a −0,18 m). | Informe 2.2 | *Resuelto en el repositorio*: diagrama corregido a 1,4 kg y marcado como esquema sin escala; manda la tabla. |
| D6 | El informe pide "ArduPlane 4.2.0 o posterior" y usa el nombre `LAND_PITCH_CD`. En 4.7.2 el parámetro es **`LAND_PITCH_DEG`** y la placa de ArduPilot para la Matek H743-Wing es **`MatekH743`**. | Informe 4.7, 9.10 | *Resuelto en el repositorio*: versión fijada 4.7.2; nombres verificados contra su metadata (`ctest -R params_vs_ardupilot`). |
| D7 | El informe nombra las salidas con el rotulado de la placa (S1–S5, M1); ArduPilot numera `SERVOn`. | Informe 4.4, 4.6 | `root_plane_base.parm` usa el reparto estándar: 1 alerón izq., 2 profundidad, 3 gas, 4 timón, 5 alerón der., 6 tambor. **Confirmar la correspondencia con los rótulos de la placa antes de cablear.** |
| D8 | Los pasos de 9.10b proponen soltar con `DO_SET_SERVO` + espera. El repositorio usa `DO_AUX_FUNCTION` (300) porque así el script Lua aplica el interlock; `DO_SET_SERVO` mueve el servo directamente y se salta toda la seguridad. | Informe 9.10b punto 7 | Decisión de diseño documentada en `docs/ardupilot.md`. |
| D9 | Longitud del fuselaje: ~1,5 m (2.1) frente a 1400 mm incluido el motor (9.2 punto 5). | Informe 2.1, 9.2 | Menor; coherente si "1,5 m" incluye el botalón. Confirmar en OpenVSP. |
| D10 | Las prestaciones (76–89 min de autonomía, 120–140 W de crucero) salen de un modelo con η_hélice ≈ 0,6 y CD0 = 0,03 que el propio informe califica de optimista. | Informe 1.3 | El modelo está en `tools/perf_calc.py` y reproduce las cifras del informe (±5 %). **Medirlo en el banco y en vuelo** antes de planificar misiones largas. |
| D11 | La controladora se estima en ~80 € en el informe (4.3); la hoja de materiales la lista a **102,69 €** (Rotorama) y el presupuesto de la sección 7 usa 103 €. | Informe 4.3 | Anotado en `04-electronica-y-vuelo-autonomo.md`. |
| D12 | El informe no justifica motor pusher ni cola convencional frente a V o T, y no incluye aleta ventral ni incidencia del ala. | Informe 2.1 | *Resuelto en el repositorio*: [Decisiones de diseño](decisiones-de-diseno.md). Falta aplicarlo en el informe y en las plantillas. |

## ✅ Resueltos

| # | Qué era | Cómo se resolvió |
|---|---|---|
| C1 | **¿ESC con escobillas?** La dirección del enlace de la línea 19 decía `controlador-velocidad-escobillas`. | **Confirmado por el propietario: el ESC es brushless, igual que el motor BR4114 400 KV.** Anotado en el Excel (nota de la línea 19), en `hardware/design/parametros.json` y en [Propulsión](propulsion.md). Con él: 80 A frente a 54 A de consumo (×1,48, ×1,40 con la batería en 21 V). Quedan por confirmar su conector (XT60) y la corriente de su BEC (C3). |
| CI | El check «Parámetros contra ArduPilot 4.7.2» fallaba: `ModuleNotFoundError: lxml`. | La metadata de parámetros se genera ahora con el Python del entorno virtual del proyecto (que instala `lxml`); `check_params.py` avisa con un mensaje claro si falta. |

## Hallazgos de la verificación en simulador

Cosas que solo se vieron al ejecutar el código contra ArduPilot SITL; ya están corregidas, pero
conviene recordarlas al tocar el script:

* Los mensajes de `gcs:send_text` deben ser **ASCII y de ≤ 50 caracteres**: los acentos llegan
  corruptos (`est��`) y los textos largos se parten en dos mensajes. Un test lo vigila.
* Sin emisora, el failsafe de gas manda al avión a RTL y no deja armar: el simulador necesita
  `RC_CHANNELS_OVERRIDE` (lo hace `tests/sitl/sitl_seed_drop.py`).
* ArduPlane SITL asume el reparto estándar de canales (1 alerón, 2 profundidad, 3 gas, 4 timón);
  por eso `root_plane_base.parm` lo adopta también para el avión real.

## Qué NO se ha podido comprobar

* **Nada en hardware real**: ni el firmware de la ESP32, ni el script en la Matek, ni la UART de la
  Raspberry Pi. Ver el estado de verificación en el [README](../README.md#estado-de-verificación).
* **La compilación del firmware real** (`ardupilot-firmware`) necesita `arm-none-eabi-gcc`, que no
  estaba disponible; el objetivo está definido pero no se ha ejecutado.
* **Los precios y enlaces** del Excel: se importan tal cual, sin volver a consultar las tiendas.
