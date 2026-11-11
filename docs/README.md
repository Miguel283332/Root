# Documentación del proyecto Root

**Root** es un dron reforestador de ala fija (3 m de envergadura, ~7 kg al despegue, inspiración MQ-9)
que lanza bolas de semillas con un tambor dosificador. Esta carpeta contiene el informe técnico, la
lista de materiales, el proceso de construcción y la documentación del software.

## Por dónde empezar

| Quiero… | Leer |
|---|---|
| Entender el proyecto en un minuto | [00 Resumen ejecutivo](00-resumen-ejecutivo.md) |
| Saber **qué comprar** y cuánto cuesta | [Materiales](materiales.md) |
| Saber **cómo se construye**, en qué orden y cuántas horas | [Proceso de elaboración](proceso-de-elaboracion.md) y [Guía de construcción](construccion/README.md) |
| **Nunca he hecho esto**: conceptos, programas y paso a paso explicados desde cero | [Guía para principiantes](principiantes/README.md) |
| Entender **por qué** motor detrás y cola convencional | [Decisiones de diseño](decisiones-de-diseno.md) |
| Descargar **ArduPilot**, simular y configurar la controladora | [ArduPilot](ardupilot.md) |
| Ver qué hay que **resolver antes de comprar o volar** | [Discrepancias y pendientes](discrepancias-y-pendientes.md) |

## El informe técnico (v3), por secciones

La numeración es la del informe original (otras secciones se citan entre sí). El original está en
[`fuentes/`](fuentes/informe_tecnico_dron_reforestador_v3.docx).

| Sección | Contenido |
|---|---|
| [00 Resumen ejecutivo](00-resumen-ejecutivo.md) | Objetivo, hélice, batería, tren, empuje, control, carga, presupuesto, tiempo |
| [Propulsión y dimensionado eléctrico](propulsion.md) | Datos del motor BR4114, ESC, batería, fusible y márgenes (complemento del informe) |
| [01 Viabilidad y propulsión](01-viabilidad-y-propulsion.md) | Empuje estático, velocidad, autonomía, MTOW, prestaciones |
| [02 Diseño aerodinámico y estructural](02-diseno-aerodinamico-estructural.md) | Geometría, centro de gravedad, piezas de corte, tren de aterrizaje |
| [03 Carga útil de reforestación](03-carga-util-reforestacion.md) | Bolas de semillas, tolva y tambor, lógica de liberación |
| [04 Electrónica y vuelo autónomo](04-electronica-y-vuelo-autonomo.md) | Fase 1 y fase 2, Raspberry Pi frente a ESP32, diagramas, alimentación, ArduPilot, despegue y aterrizaje |
| [05 Hoja de ruta](05-hoja-de-ruta.md) | Fases, horas y criterios de salida |
| [06 Tests clave](06-tests.md) | Banco de empuje, planeo, tolva, failsafe |
| [07 Presupuesto](07-presupuesto.md) | Costes y cómo bajar de 700 € |
| [08 Tiempo estimado](08-tiempo.md) | Horas y calendario |
| [09 Guía de construcción](construccion/README.md) | Paso a paso (9.1 a 9.11) |

## Herramientas del repositorio que cuelgan de estos documentos

| Herramienta | Para qué | Documento |
|---|---|---|
| `python3 tools/perf_calc.py` | Reproduce las tablas de empuje, crucero, masas y CG desde `hardware/design/parametros.json` | [01](01-viabilidad-y-propulsion.md), [02](02-diseno-aerodinamico-estructural.md) |
| `python3 tools/bom.py` | Totales, comprobaciones y tablas Markdown del presupuesto | [Materiales](materiales.md) |
| `python3 tools/check_params.py` | Valida los `.parm` contra la versión de ArduPilot descargada | [ArduPilot](ardupilot.md) |
| `ardupilot/` | Parámetros, script Lua del dosificador, misión de ejemplo, SITL | [ArduPilot](ardupilot.md) |
| `companion/` | Paquete Python de la Raspberry Pi 5 (MAVLink) | [companion](../companion/README.md) |
| `firmware/esp32_fase1/` | Vuelo manual (ESP32 + PCA9685) con failsafe | [9.6](construccion/9.6-electronica-fase-1.md) |
