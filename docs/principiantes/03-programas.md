# 03 · Los programas, uno por uno

Todos son gratuitos salvo que se indique. **Los nombres exactos de menús y botones cambian algo entre
versiones**: aquí se explica la idea y la ruta habitual; si un menú no está donde dice, busca el nombre en la
ayuda del programa. No hace falta dominar ninguno: solo la tarea concreta que se describe.

| Programa | Para qué lo usas | Cuándo | Cuánto hay que aprender |
|---|---|---|---|
| **XFLR5** | Calcular el ala (sustentación, pérdida, estabilidad) | Diseño | Poco: una ala y un análisis |
| **OpenVSP** | Ver el avión en 3D y comprobar medidas y CG | Diseño | Poco |
| `tools/plantilla_perfil.py` (este repo) | Plantilla del perfil a 1:1 para cortar | Diseño y ala | Un comando |
| **Tinkercad** (web) o **FreeCAD/Fusion** | Dibujar tolva, tambor y soportes | Impresión | Medio (lo más "nuevo") |
| **PrusaSlicer** o **Cura** | Preparar el archivo para la impresora 3D | Impresión | Poco |
| **Mission Planner** (Windows) o **QGroundControl** | Configurar ArduPilot y planear misiones | Fase 2 | Medio |
| **VS Code + PlatformIO** | Compilar y cargar el firmware de la ESP32 | Fase 1 | Poco (3 comandos) |
| **Terminal, Git, Python, CMake** | Descargar ArduPilot, simular, probar el repositorio | Fase 2 | Poco (copiar comandos) |

## 1. La terminal (donde se pegan los comandos)

Es una ventana de texto. En **Linux/macOS**: "Terminal". En **Windows**: instala **WSL2** (Ubuntu) desde la
Microsoft Store y usa la terminal de Ubuntu. Tres comandos bastan: `cd carpeta` (entrar), `ls` (listar), y
pegar el comando que indica la guía. Si un comando da error, **copia el mensaje completo** y búscalo.

```bash
sudo apt update && sudo apt install -y git cmake g++ python3 python3-venv lua5.4   # Ubuntu/WSL
git clone https://github.com/Miguel283332/Root.git && cd Root
cmake --preset dev && cmake --build --preset dev && ctest --preset dev           # debe acabar en "100% tests passed"
```

Si acaba en `100% tests passed`, el entorno está listo. Para ArduPilot y el simulador:
[ArduPilot](../ardupilot.md).

## 2. XFLR5 — calcular el ala

Descarga desde **xflr5.tech** (hay versiones para Windows, Linux y macOS). Tiene "modos" que se cambian en
el menú principal: *Direct Foil Design*, *XFoil Direct Analysis* y *Wing and Plane Design*. Lo que necesitas:

1. **Conseguir el perfil.** Descarga `clarky.dat` de la base de datos de perfiles del UIUC (busca
   "UIUC airfoil coordinates database", perfil *Clark Y*). En *Direct Foil Design* abre el archivo
   (`File → Open`) y verás el perfil dibujado.
2. **Polar 2D del perfil** (da el CLmax real). En *XFoil Direct Analysis* define una polar tipo 1 con
   Reynolds ≈ **260 000** (= velocidad 13 m/s × cuerda 0,30 m ÷ 0,000015) y haz un análisis de ángulo de
   ataque de −2° a 14°. Un *batch* con Re de 200 000 a 300 000 cubre el rango.
3. **Definir el ala.** En *Wing and Plane Design* → `Wing/Plane → Define a new wing`: envergadura **3000 mm**,
   cuerda **300 mm** en la raíz (y=0) y en la punta (y=1500), torsión 0°, diedro 0° (decisión pendiente, ver
   [Decisiones de diseño](../decisiones-de-diseno.md)), perfil Clark Y en ambas estaciones.
4. **Analizar.** `Analysis → Define an analysis`: método **VLM**, velocidad **13 m/s** (≈ 47 km/h), ángulos de
   −2° a 12° en pasos de 1°. Ejecútalo y mira la curva **CL vs α**.
5. **Qué anotar:** el **CLmax** (debe salir ≥ 1,2: la pérdida queda en torno a 32–36 km/h), el ángulo con el
   que CL = 0,8 (≈ **4–5°**: ése es tu ángulo de incidencia) y la posición del **punto neutro** si usas el
   análisis de estabilidad.

**Cómo saber que va bien:** si el CLmax sale muy por debajo de 1,0 o la curva no es una recta creciente,
revisa que la cuerda esté en mm y el perfil cargado correctamente.

## 3. OpenVSP — ver el avión en 3D

Descarga desde **openvsp.org**. Se trabaja con un panel de componentes ("geometry browser"): añade un
**Wing** (3000 × 300 mm, perfil Clark Y), un **Fuselage** (~1400 mm incluido el motor), un estabilizador
horizontal (600 × 320 mm) y uno vertical (250 × 600 mm), colócalos con las cotas de la tabla 2.2 del
[informe](../02-diseno-aerodinamico-estructural.md) y mira el modelo desde arriba y de lado. Sirve para
**detectar a simple vista** errores de colocación (cola desalineada, hélice demasiado baja). No necesitas
más.

## 4. Plantilla del perfil a escala 1:1 (este repositorio)

Una vez tengas `clarky.dat`:

```bash
python3 tools/plantilla_perfil.py clarky.dat --cuerda 300 -o plantilla_clarky.svg
```

Abre el SVG en un navegador o en **Inkscape**, imprímelo **al 100 %** (sin "ajustar a página") en papel A3 o
llévalo a una copistería ("plano a escala 1:1"). **Mide con regla el cuadrado de 50 mm** y la cuerda de
300 mm antes de usarlo. Verás marcado el círculo de 12 mm del larguero al 25 % de la cuerda. Pega la hoja
sobre un tablero fino (contrachapado de 3 mm, cartón pluma) y recórtalo: ésa es tu **plantilla de corte**.

## 5. Diseñar las piezas impresas

* **Tinkercad** (tinkercad.com, gratis, en el navegador) es lo más fácil: arrastras cajas y cilindros y
  restas huecos. Tolva: caja de **300 × 200 × 100 mm** con embudo inferior a 45°; tambor: disco de
  **Ø180 mm** con **6 celdas de 50 mm** y eje de 8 mm. **El tambor lleva un trinquete** (rueda libre) para que
  un servo normal lo haga avanzar ([S2](../discrepancias-y-pendientes.md)).
* **FreeCAD** (gratis) o **Fusion** (gratis para uso personal) son más potentes y más difíciles.
* Exporta cada pieza como **STL**.

**Slicer (PrusaSlicer o Cura):** importa el STL, elige impresora y filamento **PETG**, y guarda el *G-code* en
la tarjeta o envíalo a la impresora. Valores típicos de PETG (**mira la caja de tu filamento**, mandan sus
datos): boquilla 230–250 °C, cama 70–85 °C, capa 0,2 mm, 3 perímetros, relleno 25–40 % en piezas que cargan
(soportes del motor y del tren), sin ventilador o muy bajo. Imprime una pieza de prueba pequeña antes de las
grandes. Piezas que no caben (tolva de 300 mm): divídelas en dos con tornillos M3 (ya previsto en
[9.5](../construccion/9.5-tolva-y-tambor.md)).

## 6. Mission Planner / QGroundControl — configurar ArduPilot

* **Mission Planner** (ardupilot.org; solo Windows) es el más completo. **QGroundControl** funciona en
  Windows, macOS y Linux. Con cualquiera de los dos conectas la controladora **por USB**.
* Ruta típica en Mission Planner: *Setup → Install Firmware* (elige **ArduPlane 4.7.2**, placa `MatekH743`);
  *Setup → Mandatory Hardware* para calibrar acelerómetro, brújula, radio y modos de vuelo; *Config → Full
  Parameter List → Load from file* para cargar los `.parm` del repositorio; *Plan* para dibujar la misión.
* **Orden y valores exactos:** [ArduPilot §6](../ardupilot.md#6-pasar-de-simulador-a-avión-real). **Nunca**
  vueles sin haber calibrado y comprobado cada mando en tierra.

## 7. VS Code + PlatformIO — firmware de la ESP32

Instala **Visual Studio Code**, añade la extensión **PlatformIO IDE**, abre la carpeta
`firmware/esp32_fase1`, conecta la ESP32 por USB y pulsa *Upload* (o `pio run -t upload`). Antes lee su
[README](../../firmware/esp32_fase1/README.md): arranca en **FAILSAFE** (motor a cero) hasta que se define el
protocolo de tu emisora. **Primera prueba siempre sin hélice.**

## 8. El simulador (para ensayar la fase 2 sin riesgo)

El proyecto trae un simulador de ArduPilot que ejecuta el mismo script de suelta que irá en el avión:

```bash
cmake --preset ardupilot                                       # descarga ArduPilot (≈ 1,7 GB)
cmake --build --preset ardupilot -t ardupilot-sitl-build       # compila (3–5 min)
ctest --preset ardupilot                                       # pruebas, incluida una misión simulada
```

Es la mejor forma de aprender ArduPilot **sin poner un avión en riesgo**.
