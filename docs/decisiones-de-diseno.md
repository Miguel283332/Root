# Decisiones de diseño: motor, cola y despegue

Preguntas: ¿motor delante o detrás?, ¿cola en V o en T?, y ¿qué hace falta para parecerse al MQ-9 sin
complicar el primer avión? Las cifras salen de `python3 tools/perf_calc.py diseno`
(datos en [`hardware/design/parametros.json`](../hardware/design/parametros.json)); son
estimaciones de primera aproximación que hay que validar en XFLR5/OpenVSP.

## Resumen

| Decisión | Recomendación | Por qué, en una línea |
|---|---|---|
| Motor | **Detrás (pusher), como el MQ-9** — pero solo si se diseña el despegue para él (abajo) | Morro libre para batería/cámara y silueta MQ-9; la hélice en cola es el punto delicado |
| Cola | **Convencional (horizontal + vertical)** para el Mk. 1; **V invertida** como mejora del Mk. 2 | Mínimo riesgo y ArduPilot la trae resuelta; la V no ahorra superficie |
| Cola en T | **No** | Aleta pesada y flexible en foam, riesgo de entrada en pérdida profunda y no es del MQ-9 |
| Ala | **Incidencia de ~4°** (no estaba en el informe) | Con el fuselaje nivelado en crucero el ala ya da la sustentación |
| Diedro | **2° por semiala** (4° en total), con manguito central **20/18** | Sin estabilización electrónica en la fase 1, un ala recta es poco estable en alabeo; 2° es lo habitual en un avión estable con alerones |
| Despegue | **Sin rotación brusca**: cabeceo ≤ 5° y holgura de hélice ≥ 70–100 mm | Con 50 mm la hélice toca el suelo a solo 3,7° |
| Aleta ventral | **Añadir una pequeña** bajo la cola | Protege la hélice (el MQ-9 la lleva por esa razón) |

## 1. Motor delante (tractor) o detrás (pusher)

El diseño actual es **pusher**: motor BR4114 y hélice 18 × 5,5 al final de un botalón de carbono de 500 mm,
batería y electrónica en el morro.

| Criterio | Pusher (actual, como el MQ-9) | Tractor (motor delante) |
|---|---|---|
| Parecido al MQ-9 | **Sí** | No |
| Morro | **Libre** para batería, RPi y cámara con vista despejada | Ocupado por motor y hélice |
| Flujo sobre el ala | **Limpio** (la estela no la perturba) | La estela aumenta algo la resistencia del fuselaje |
| Aire sobre la cola a baja velocidad | **No hay**: los mandos de cola son flojos al empezar a rodar | **Sí**: más control en la carrera de despegue |
| Golpe de hélice al rotar/aterrizar | **Riesgo real** (ver §3) | Casi nulo en cola; la hélice va delante de las ruedas |
| Refrigeración del motor | Peor: sin chorro de aire directo | Mejor |
| Centro de gravedad | El motor pesa 0,42 kg a +0,90 m: obliga a poner la batería de 1,4–1,5 kg en el morro | Motor delante: la batería se coloca cerca del CG, fuselaje más corto |
| Aterrizaje en el campo | Una hélice trasera se rompe con un mal aterrizaje de panza | La hélice delantera también, pero es más fácil reponer |
| Eficiencia | Puede ganar unos pocos % al aspirar la capa límite del fuselaje; **no es una ventaja demostrada** para este avión | Equivalente |

**Veredicto.** Para un **primer avión** el tractor sería más fácil y más perdonador. Pero el proyecto pide la
forma del MQ-9 y todo el sistema (batería y cámara en el morro, motor ya calculado en la cola) está
dimensionado para el pusher. **Se mantiene el pusher**, con tres condiciones que el informe no recogía:

1. **Despegar sin rotar** (incidencia del ala ≈ 4°, §2) y limitar el cabeceo a ≤ 5°.
2. **Holgura de hélice ≥ 70–100 mm**, no 50 mm (§3).
3. **Aleta ventral o patín de cola** que toque el suelo antes que la hélice (§4).

Si al construir el tren y medir la holgura no se consiguen, la alternativa limpia es pasar a tractor: se
reutilizan ala, tren, tolva y electrónica; solo cambian fuselaje y posición de batería.

## 2. Incidencia del ala (dato que faltaba)

El informe define el perfil y el CLmax pero **no el ángulo de incidencia** (el ángulo con que el ala se monta
respecto al eje del fuselaje). Con el Clark Y (sustentación nula a ≈ −4,5°) y un ala de alargamiento 10 la
pendiente es ≈ 0,090 por grado:

| Situación | CL necesario | Ángulo de ataque del perfil |
|---|---:|---:|
| Crucero a 45 km/h | 0,79 | **≈ 4,3°** |
| Despegue a 1,2 × pérdida (43 km/h) | 0,83 | ≈ 4,8° |

Si el ala se monta con **~4° de incidencia**, el avión vuela **con el fuselaje nivelado** en crucero (menos
resistencia) y **despega casi sin rotar** (solo ~1° más). Sin incidencia habría que cabecear ~4–5° en vuelo y
~5° al despegar. Pasos: fijar 4° en XFLR5/OpenVSP ([9.2](construccion/9.2-diseno-xflr5-openvsp.md)), marcarlo en
las plantillas y montar el ala con calzos que den esos 4° ([9.3](construccion/9.3-ala.md)).

### Diedro: decisión (S10)

**Decisión: 2° de diedro por semiala** (cada punta sube **52 mm** sobre la raíz).

* **Por qué:** en la fase 1 el avión se vuela sin estabilización electrónica; el diedro hace que un alabeo
  involuntario se corrija solo. 2° es un valor habitual para un avión estable con alerones y poca complicación
  de construcción; más (3° o más) acopla demasiado guiñada y alabeo.
* **Consecuencia estructural (calculada con `python3 tools/perf_calc.py diseno`):** los tubos de 12 mm de las
  dos semialas entran inclinados ±2° en el manguito central. Pivotan en el centro, así que en cada boca del
  manguito (75 mm) se desplazan **2,62 mm**. El manguito 16/14 del informe solo da **1,0 mm** de holgura (no
  admite ni 1°, que exigiría 1,31 mm). Hace falta un **manguito 20/18 × 150 mm** (3,0 mm de holgura), que se
  rellena con epoxi espesado (fibras o microbalones). Añadido a la lista de materiales (línea 32,
  30 € estimados, sin enlace).
* **Plan B si el manguito 20/18 no se consigue o la unión no inspira confianza:** construir el ala recta
  (0°) y hacer los **primeros vuelos con ArduPilot en FBWA** (que estabiliza el alabeo), lo que obliga a
  adelantar la controladora (línea 24) a la fase 1.
* **Efecto aerodinámico:** la pérdida de sustentación vertical es cos 2° = 0,9994: despreciable.
* **No validado:** la resistencia de la unión central no se ha calculado ni ensayado. Hay que hacer la
  **prueba de carga** de [9.3](construccion/9.3-ala.md) antes del primer vuelo.

## 3. El problema de la hélice pusher en el despegue

Al rotar, el avión pivota sobre las ruedas principales (x = +0,12 m) y la hélice (x = +0,90 m) baja. Con un brazo de
0,78 m:

| Cabeceo | Holgura necesaria |
|---:|---:|
| 3,7° | 50 mm (**la del informe**) |
| 5° | 68 mm |
| 10° | 137 mm |
| 15° | 209 mm |

El valor por defecto de ArduPilot para subir tras rotar es **15°** (en la misión, `TAKEOFF` param1). Con 50 mm
de holgura la hélice se destrozaría. Cambios hechos en el repositorio: `TKOFF_LVL_PITCH = 5` y la misión de
ejemplo despega a 5° (`ardupilot/params/root_plane_base.parm`, `ardupilot/missions/sitl_siembra.waypoints`).
Para el avión real, además: patas principales más largas o motor elevado sobre el botalón hasta tener
**≥ 100 mm** de holgura a cabeceo nulo. El mismo cálculo vale para el **aterrizaje** (el enderezado a
`LAND_FLARE_ALT` = 3 m levanta el morro): conviene tocar con las ruedas principales y poco cabeceo.

## 4. Cola: convencional, V o T

Volúmenes de cola del diseño actual (brazo 0,62 m desde el CG):

| Coeficiente | Valor | Rango habitual |
|---|---:|---|
| Horizontal V_H | 0,44 | 0,3–0,6 ✔ |
| Vertical V_V | 0,034 | 0,02–0,05 ✔ |

La cola actual **está bien dimensionada**. Comparación de configuraciones:

| | Convencional (actual) | V invertida (MQ-9) | En T |
|---|---|---|---|
| Parecido al MQ-9 | Poco | **Sí** | No |
| Superficie necesaria | 0,19 + 0,15 = 0,34 m² | **0,34 m² a ~42°** (igual: no ahorra nada) | ≥ 0,34 m² y aleta más reforzada |
| Servos | 2 (profundidad, timón) | 2 (con mezcla) | 2 |
| Control | Independiente en cabeceo y guiñada | Mezclado: cada mando mueve las dos superficies; acopla guiñada y alabeo | Independiente |
| ArduPilot | Estándar | Soportado (`SERVOx_FUNCTION` 79/80 con `VTAIL_OUTPUT`; hay ejemplo `plane-vtail.parm`) | Estándar |
| Construcción en foam | **La más fácil** | Bisagras y ángulos más difíciles; más sensible a errores | Aleta alta y larga: se flexa; riesgo de flameo |
| Riesgo de pérdida profunda | No | No | **Sí** (el estabilizador queda en la estela del ala) |
| Protección de la hélice | No (añadir aleta ventral) | **Sí**: las superficies inferiores protegen la hélice | No |

**Veredicto.** **Mk. 1: cola convencional + pequeña aleta ventral.** Es lo más seguro para un primer avión de 7 kg
y no cambia ni una línea del código de ArduPilot. **Mk. 2 (opcional): V invertida**, que es lo que más se
parece al MQ-9 y da protección natural a la hélice pusher, una vez probado el avión y con el mezclador
validado en SITL. **T: descartada.**

## Qué hay que cambiar en el informe

| Dónde | Cambio |
|---|---|
| 2.1 Geometría | Añadir **incidencia del ala ≈ 4°** y la **aleta ventral** |
| 2.4 Tren | Holgura de hélice **≥ 70–100 mm** (no 50 mm) y cabeceo de rotación ≤ 5° |
| 9.2 Diseño | Fijar y comprobar la incidencia en XFLR5/OpenVSP |
| 9.4b Tren / 9.9 Vuelos | Comprobar la holgura con el avión inclinado 5° (calzar la cola) |
| ArduPilot | `TKOFF_LVL_PITCH` = 5 y `TAKEOFF` de la misión a ≤ 5° (hecho) |

Estas incoherencias están registradas como [S9, S10 y D12](discrepancias-y-pendientes.md).
