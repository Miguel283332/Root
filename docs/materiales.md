# Materiales

Todo lo que hay que comprar, con medidas, uso, precio y enlace. La **fuente de verdad** es la hoja
de cálculo [`hardware/bom/materiales_dron.xlsx`](../hardware/bom/materiales_dron.xlsx) (editable, con
fórmulas); de ella sale [`hardware/bom/materiales.csv`](../hardware/bom/materiales.csv) y de este
CSV, las tablas de abajo.

```bash
python3 tools/bom_from_xlsx.py        # tras editar el Excel: regenera el CSV
python3 tools/bom.py                  # resumen en la terminal
cmake --build build/dev -t docs-bom   # regenera las tablas de este documento
```

> **Precios.** Son orientativos (euros, sin envío ni IVA fuera de la UE). Los marcados **estimado**
> no tienen precio visible en el enlace o no tienen enlace: hay que confirmarlos en tienda antes de
> comprar. Antes de pedir, repasa [las discrepancias y pendientes](discrepancias-y-pendientes.md):
> varias líneas (ESC, fusible, servos, conectores) tienen una comprobación pendiente.

## Lista de compra

<!-- BOM:START (generado con tools/bom.py --update-docs) -->

**Total (líneas incluidas): 921,46 €** · presupuesto 700,00 € · diferencia -221,46 € · 462,95 € (50%) son precios **sin verificar** (estimación o sin enlace).

| Categoría | Subtotal |
|---|---:|
| Estructura | 348,76 € |
| Herramientas | 75,09 € |
| Cableado | 29,99 € |
| Propulsión | 134,98 € |
| Servos | 104,95 € |
| Alimentación | 25,00 € |
| Sensores | 162,69 € |
| Electrónica | 40,00 € |
| **Total** | **921,46 €** |

| Fase | Subtotal | Qué cubre |
|---|---:|---|
| 1 — vuelo manual | 708,77 € | estructura, herramientas, propulsión, servos, BEC 6 V |
| 2 — autónomo | 212,69 € | controladora ArduPilot, GPS, pitot, cámara, BEC 5 V |

#### Estructura

| Nº | Material | Especificación / uso | Cant. | P. unit. | Subtotal | Fase | Precio | Enlace |
|--:|---|---|--:|--:|--:|:-:|:-:|---|
| 1 | Foam XPS 40 mm, plancha 1250 x 600 mm (Chovafoam T-IV) | Semialas del ala: 4 planchas (cada una da 2 piezas de 750 x 300 mm) | 4 | 3,29 € | 13,16 € | 1 | verificado | [enlace](http://www.leroymerlin.es/leroyMerlinWebsite/productos/construccion/aislantes/ficha.html?idCat=85153&sku=10403666) |
| 2 | Plancha foam 100 x 70 cm, 9,7 mm (fuselaje) | Laterales, base y tapa del fuselaje (caja de 900 mm) | 6 | 8,00 € | 48,00 € | 1 | estimado | [enlace](https://www.amazon.es/Plancha-interior-cart%C3%B3n-diferentes-grosores/dp/B08N1KHLRS) |
| 3 | Plancha foam 100 x 70 cm, 5 mm (empenaje) | Empenaje horizontal 600 x 320 mm y vertical 250 x 600 mm | 1 | 8,00 € | 8,00 € | 1 | estimado | [enlace](https://www.amazon.es/Plancha-interior-cart%C3%B3n-diferentes-grosores/dp/B08N1KHLRS) |
| 4 | Tubo de carbono mate 12 x 10 x 1000 mm | Larguero: 4 tubos (2 por semiala, cada uno cruza la junta) | 4 | 27,99 € | 111,96 € | 1 | verificado | [enlace](https://www.amazon.es/Tubo-Fibra-Carbono-Matte-1000mm/dp/B08C7ZD63T) |
| 5 | Tubo de carbono mate 16 x 14 x 1000 mm | Botalón (500 mm) y 2 manguitos de 150 mm para la unión central | 1 | 31,95 € | 31,95 € | 1 | estimado | [enlace](https://www.amazon.es/Tubo-Fibra-Carbono-Matte-1000mm/dp/B08C8198Y6) |
| 6 | Película termoretráctil Hensons, 2 m x 0,62 m | Acabado del ala, fuselaje y empenaje (unos 3 m² en total) | 2 | 15,00 € | 30,00 € | 1 | estimado | [enlace](https://www.amazon.es/Pel%C3%ADcula-cobertura-pel%C3%ADcula-cubierta-termorretr%C3%A1ctil/dp/B0DHGY868S) |
| 7 | Filamento PETG 1,75 mm, 1 kg (GEEETECH) | Tolva, tambor, soportes de servo y motor, bujes | 1 | 15,19 € | 15,19 € | 1 | verificado | [enlace](https://www.amazon.es/GEEETECH-Filamento-Impresora-Precisi%C3%B3n-Dimensional/dp/B08C2FXGZ1) |
| 8 | Cianoacrilato 50 g + acelerante 200 ml | Uniones rápidas de foam y carbono | 1 | 16,50 € | 16,50 € | 1 | verificado | [enlace](https://www.leroymerlin.es/productos/pegamento-cianoacrilato-50-gr-con-acelerante-200ml-especial-materiales-porosos-multiusos-plasticos-maderas-porcelana-86300736.html) |
| 9 | Epoxi de curado 5 min (2 tubos de 15 ml) | Unión de tubos de carbono en el larguero y los manguitos | 1 | 6,00 € | 6,00 € | 1 | estimado | [enlace](https://www.leroymerlin.es/productos/pegamento-epoxi-rapido-2-tubos-de-15-ml-68944092.html) |
| 10 | Cinta de bisagra y cinta adhesiva | Bisagras de alerones, profundidad y timón | 1 | 8,00 € | 8,00 € | 1 | estimado | — |
| 28 | Kit tren de aterrizaje triciclo (BESSTUUP, aluminio y plástico) | Prototipo del tren: morro + 2 principales (ruedas de 55 mm) | 1 | 30,00 € | 30,00 € | 1 | estimado | [enlace](https://www.amazon.es/BESSTUUP-Upgrade-Accesorios-Triciclo-aterrizaje/dp/B0BY7WBBP8) |
| 29 | Ruedas 80–90 mm (2 principales) y 60 mm (1 de morro) | Ruedas para hierba o pista de tierra | 3 | 6,00 € | 18,00 € | 1 | estimado | — |
| 30 | Perfil de aluminio 4 mm, 1 m | Patas del tren (2 principales de 180 mm y 1 de morro de 200 mm) | 1 | 12,00 € | 12,00 € | 1 | estimado | — |

#### Herramientas

| Nº | Material | Especificación / uso | Cant. | P. unit. | Subtotal | Fase | Precio | Enlace |
|--:|---|---|--:|--:|--:|:-:|:-:|---|
| 11 | Hilo de nicromo 0,5 mm, 10 m | Hilo caliente para cortar las planchas de foam | 1 | 11,00 € | 11,00 € | 1 | estimado | [enlace](https://www.amazon.es/SHHMA-Resistencia-Alambre-Redondo-Diameter/dp/B0991SWXM9) |
| 12 | Fuente de alimentación 12 V, 5 A | Alimentar el hilo caliente | 1 | 11,81 € | 11,81 € | 1 | verificado | [enlace](https://www.amazon.es/Fuente-Alimentaci%C3%B3n-Conmutada-Transformadores-para/dp/B0925CF5PV) |
| 13 | Cutter retráctil 9 mm (Dexter) | Cortes rectos y acabados | 1 | 5,19 € | 5,19 € | 1 | verificado | [enlace](https://www.leroymerlin.es/productos/cutter-dexter-9-mm-autoretractil-82945690.html) |
| 14 | Regla de corte de acero 1000 mm | Guía para cortes rectos del foam | 1 | 15,00 € | 15,00 € | 1 | estimado | [enlace](https://leroymerlin.es/productos/herramientas/herramientas-de-medicion/escuadras-reglas-y-compases/regla-de-corte-w40mm-x-l1000mm-86401917.html) |
| 15 | Bloques de lijado y esponjas (pack de 16, 120 x 220) | Acabado de piezas de foam y PETG | 1 | 17,09 € | 17,09 € | 1 | verificado | [enlace](https://www.leroymerlin.es/productos/herramientas/herramientas-de-mano/herramientas-manuales-para-lijar-desbastar/lijas-de-mano/bloques-de-lijado-p.html) |
| 16 | Pistola termofusible | Pegado rápido de piezas | 1 | 15,00 € | 15,00 € | 1 | estimado | — |

#### Cableado

| Nº | Material | Especificación / uso | Cant. | P. unit. | Subtotal | Fase | Precio | Enlace |
|--:|---|---|--:|--:|--:|:-:|:-:|---|
| 17 | Kit XT60 con cable de silicona 14 AWG (5 pares) | Conexiones de la batería y de potencia | 1 | 9,99 € | 9,99 € | 1 | verificado | [enlace](https://www.amazon.es/conectores-hembra-alambre-silicona-bater%C3%ADa/dp/B085HF31K7) |
| 18 | Fusible 80 A de acción lenta, tornillería M2/M3 y termorretráctil surtido | Montaje y protecciones | 1 | 20,00 € | 20,00 € | 1 | estimado | — |

#### Propulsión

| Nº | Material | Especificación / uso | Cant. | P. unit. | Subtotal | Fase | Precio | Enlace |
|--:|---|---|--:|--:|--:|:-:|:-:|---|
| 19 | ESC 80 A, 2–6S, con BEC 5 V (DaMohony) | Controlador del BR4114 (versión 80 A) | 1 | 49,98 € | 49,98 € | 1 | verificado | [enlace](https://www.amazon.es/Controlador-velocidad-escobillas-Quadcopter-Helic%C3%B3ptero/dp/B08HLZ5LWY) |
| 20 | Batería LiPo 6S 10000 mAh 22,2 V (SSCYHT, XT60) | Alimentación principal para máxima autonomía (1,5 kg) | 1 | 85,00 € | 85,00 € | 1 | estimado | [enlace](https://www.amazon.es/SSCYHT-10000mAh-Bater%C3%ADas-Repuesto-22-2v10000mah/dp/B0FYDLHB18) |

#### Servos

| Nº | Material | Especificación / uso | Cant. | P. unit. | Subtotal | Fase | Precio | Enlace |
|--:|---|---|--:|--:|--:|:-:|:-:|---|
| 21 | Servo digital metal 20 kg (ANNIMOS, 6,8 V máx.) | 4 servos de control (alerones, profundidad, timón) + 1 para el tambor | 5 | 20,99 € | 104,95 € | 1 | verificado | [enlace](https://www.amazon.es/ANIMOO-Completo-Engranaje-Impermeable-controlar/dp/B0769DFJVK) |

#### Alimentación

| Nº | Material | Especificación / uso | Cant. | P. unit. | Subtotal | Fase | Precio | Enlace |
|--:|---|---|--:|--:|--:|:-:|:-:|---|
| 22 | BEC 6 V / 10 A (UBEC Switch 6/7,4/8,4 V) | Alimenta los servos y el PCA9685 | 1 | 15,00 € | 15,00 € | 1 | estimado | [enlace](https://www.amazon.es/Regulator-Controlador-Quadcopter-Protecci%C3%B3n-Sobrecorriente/dp/B0G4FHGR61) |
| 23 | BEC 5 V / 5 A (SPARKHOBBY UBEC-5A) | Alimenta la Raspberry Pi 5 (fase 2) | 1 | 10,00 € | 10,00 € | 2 | estimado | [enlace](https://www.amazon.es/multiprop%C3%B3sito-alimentaci%C3%B3n-reductora-blindaje-completo/dp/B0D7MPQ8PB) |

#### Sensores

| Nº | Material | Especificación / uso | Cant. | P. unit. | Subtotal | Fase | Precio | Enlace |
|--:|---|---|--:|--:|--:|:-:|:-:|---|
| 24 | Controladora de vuelo Matek H743-Wing V3 (ArduPilot) | Piloto automático: estabilización, GPS, failsafe, seguimiento de terreno | 1 | 102,69 € | 102,69 € | 2 | verificado | [enlace](https://www.rotorama.com/product/matek-h743-wing-v3) |
| 25 | GPS M10 con brújula (HGLRC M100-5883) | Posición y rumbo para misiones | 1 | 30,00 € | 30,00 € | 2 | estimado | [enlace](https://www.amazon.es/HGLRC-GPS-M100-5883-actualizado-generaci%C3%B3n/dp/B0CB5N8RQ8) |
| 26 | Sensor de velocidad diferencial MS4525DO + pitot (Hobbypower) | Velocidad aerodinámica para ArduPilot (I2C) | 1 | 30,00 € | 30,00 € | 2 | estimado | [enlace](https://www.amazon.es/Hobbypower-Airspeed-diferencial-PX4-Pixhawk-Autom%C3%A1tico/dp/B01J7NCML0) |

#### Electrónica

| Nº | Material | Especificación / uso | Cant. | P. unit. | Subtotal | Fase | Precio | Enlace |
|--:|---|---|--:|--:|--:|:-:|:-:|---|
| 27 | Cámara InnoMaker IMX708 12 MP con autofoco | Visión por ordenador (fase 2), compatible con Raspberry Pi 5 | 1 | 40,00 € | 40,00 € | 2 | estimado | [enlace](https://www.amazon.es/innomaker-Modules-Raspberry-Compatible-CAM-IMX708AF/dp/B0DJ6R67CY) |
| 31 | Acelerador Hailo AI HAT+ (opcional) *(opcional, fuera del total)* | Inferencia de IA en tiempo real para la Raspberry Pi 5 | 1 | 110,00 € | 110,00 € | 2 | estimado | — |

**Ya lo tienes (no incluido en el total):** motor BR4114 KV 400, hélice APC 18x5.5, emisora y transmisor, ESP32, PCA9685 y Raspberry Pi 5 16 GB.  
**No incluido:** envíos, IVA en tiendas fuera de la UE y aranceles de importación. (La nota del Excel original dice que tampoco incluye la batería de 10 Ah, pero la línea 20 sí la contabiliza: aquí se cuenta en el total. Ver [discrepancias](discrepancias-y-pendientes.md).)

<!-- BOM:END -->

## Qué se corta con cada material (informe 2.3)

| Material | Medida (mm) | Cantidad | Uso |
|---|---|---|---|
| Foam XPS 40 mm, plancha ~1200–1250 × 600 | 750 × 300 × 40 (2 piezas por semiala) | 4 planchas (2 de reserva) | Semialas del ala. Cada plancha da 2 piezas de 750 × 300 |
| Foam 10 mm, plancha 1200 × 600 (≈ 9,7 mm en la lista) | Laterales 900 × 120; base y tapa 900 × 150; cuadernas 150 × 120 (×3) | 6 planchas | Fuselaje (caja de 900 mm) |
| Foam 5 mm, plancha 1200 × 600 | Horizontal 600 × 320; vertical 250 × 600 | 1 plancha | Empenaje |
| Tubo carbono 12/10 mm | 1000 | 4 | Larguero: 2 por semiala, cada uno cruza la junta entre piezas (250 mm en cada una) |
| Tubo carbono 16/14 mm | Botalón 500; manguitos 150 (×2) | 1 tubo de 1000 | Botalón de la cola y manguito de unión central |
| PETG impreso | Tolva 300 × 200 × 100 (2 piezas); tambor Ø180 con 6 celdas de 50 mm | 1 juego | Tolva, tambor, soporte del motor, bujes, soportes del tren |
| Perfil de aluminio 4 mm | Patas principales 180 mm (×2), pata de morro 200 mm | 1 m | Tren de aterrizaje (informe 2.4 / 9.4b) |

Los cortes del foam salen de las plantillas a escala 1:1 que se exportan en [9.2](construccion/9.2-diseno-xflr5-openvsp.md).
Sobra material en las planchas: guárdalo para repetir piezas si fallan.

## Para qué sirve cada material

| Material | Por qué se eligió |
|---|---|
| **Foam XPS** (ala, fuselaje, empenaje) | Ligero, barato y se corta con hilo caliente: permite hacer un ala de 3 m en un taller pequeño. |
| **Tubo de carbono** (larguero, botalón) | El foam no aguanta la flexión de 3 m de envergadura con 7 kg; el larguero de 12 mm a 25 % de la cuerda lleva la carga. El botalón de 16 mm sostiene el motor y la cola. |
| **Película termorretráctil** (Hensons) | Sella y endurece el foam y deja una superficie lisa. |
| **PETG impreso** | Tolva, tambor y soportes: resistente a humedad y a temperatura (más resistente al calor que el PLA (un avión que se queda al sol)). |
| **CA + acelerante, epoxi de 5 min** | CA para foam; epoxi para todo lo que lleva carga (tubos de carbono, soportes del tren). |
| **LiPo 6S 10 Ah** | La batería es el 20 % de la masa y define la autonomía (76–89 min a 45–50 km/h según el informe). |
| **Servos metálicos de 20 kg** | Para los mandos y el tambor; ojo, el límite es 6,8 V: alimentarlos con el BEC de 6 V. |

## Propulsión y alimentación: datos confirmados

* **Motor BR4114 KV 400 y ESC de 80 A: ambos brushless** (confirmado por el propietario).
* **Fusible de 80 A de acción lenta** en lugar del de 40 A del informe: a gas pleno se consumen ~54 A.
* **Batería: tasa de descarga ≥ 10 C continuos** (se piden 5,4 C); 1,5 kg según la ficha.

Cálculos y márgenes en [Propulsión](propulsion.md).

## Ya lo tienes (no incluido en el presupuesto)

Motor **BR4114 KV 400**, hélice **APC 18 × 5,5**, emisora y transmisor, **ESP32**, **PCA9685** y
**Raspberry Pi 5 de 16 GB**.

## Balance de masas (informe 1.4)

| Bloque | Masa (kg) |
|---|---:|
| Estructura (ala, fuselaje, empenaje, sin tren) | 1,40 |
| Propulsión: BR4114 (~0,30) + ESC 80 A (~0,10) + hélice (~0,02) | 0,42 |
| Batería 6S 10000 mAh | 1,40 |
| Electrónica de vuelo (en fase 2 suma controladora, GPS y pitot) | 0,45 |
| Ordenador compañero (RPi 5 + cámara) | 0,10 |
| Servos (5 de 60 g) | 0,30 |
| Tolva vacía + tambor | 0,30 |
| Tren de aterrizaje | 0,25 |
| **Subtotal sin carga útil** | **4,62** |
| Carga útil (250 bolas de 10 g) | 2,50 |
| **MTOW** | **≈ 7,1 (diseño con margen hasta 7,5)** |

`python3 tools/perf_calc.py masas` recalcula esta tabla y el centro de gravedad desde
[`hardware/design/parametros.json`](../hardware/design/parametros.json). Si pesas las piezas reales,
actualiza ese fichero.

## Herramientas y seguridad

La lista de herramientas, el hilo caliente y las normas de seguridad con LiPo están en
[9.1 Herramientas, materiales y seguridad](construccion/9.1-herramientas-y-seguridad.md).
