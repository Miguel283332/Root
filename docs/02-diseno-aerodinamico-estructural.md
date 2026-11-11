# 2. Diseño aerodinámico y estructural (inspiración MQ-9)

> Convertido del [informe técnico v3](fuentes/informe_tecnico_dron_reforestador_v3.docx), sección 2. La numeración original se conserva (otras secciones la citan). Las notas `⚠` son del repositorio y no estaban en el informe.


## 2.1 Geometría preliminar

| Parámetro            | Valor                           |
|----------------------|---------------------------------|
| Envergadura          | 3,0 m                           |
| Cuerda               | 0,30 m (ala rectangular)        |
| Superficie alar      | 0,90 m2                         |
| Alargamiento (AR)    | 10                              |
| Perfil               | Clark Y, espesor 12 % (36 mm)   |
| Hueco del larguero   | 12 mm, a 25 % de cuerda         |
| Longitud de fuselaje | ~1,5 m                          |
| Empenaje horizontal  | ~0,19 m2 (0,60 × 0,32 m)        |
| Empenaje vertical    | ~0,15 m2 (0,25 × 0,60 m)        |
| Hélice               | pusher, en la cola del fuselaje |
| Incidencia del ala (añadido) | ≈ 4° (ver [Decisiones de diseño](decisiones-de-diseno.md)) |
| Diedro (añadido) | **2° por semiala**: cada punta sube 52 mm; manguito central 20/18 |
| Aleta ventral (añadido) | pequeña, bajo la cola: protege la hélice pusher |

Son dimensiones de partida. Valídalas con XFLR5 y OpenVSP (guía en la sección 9.2).

## 2.2 Distribución de pesos y centro de gravedad (CG)

Objetivo: CG en 25–30 % de la cuerda media (MAC), es decir, a unos 0,08 m detrás del borde de ataque. Positivo = hacia la cola.

```text
MORRO <------------------------------------------------------------> COLA
(esquema de orden de los bloques, NO a escala; las cotas reales están en la tabla)

+---------+ +---------+ +-------+ +----------------+ +---------+ +----------+ +-----------+
| BATERIA | | FC+GPS  | | RPi 5 | | ALA (larguero  | | TOLVA + | | EMPENAJE | | BR4114 +  |
| 6S 1,4kg| | + pitot | | + cam.| | 12 mm carbono) | | BOLAS   | |          | | ESC + hel.|
+---------+ +---------+ +-------+ +----------------+ +---------+ +----------+ +-----------+
                                                          ^
                                                CG = +0,08 m (27 % MAC)
                                 (tolva centrada en el CG: al soltar
                                  bolas, el CG no se desplaza)
```


| Componente                                      | Masa (kg) | x desde borde de ataque (m) | Momento (kg·m)               |
|-------------------------------------------------|-----------|-----------------------------|------------------------------|
| Batería 6S 10 Ah (en el morro, delante del ala) | 1,40      | −0,18                       | −0,252                       |
| Electrónica de vuelo                            | 0,45      | −0,25                       | −0,113                       |
| RPi 5 + cámara                                  | 0,10      | −0,20                       | −0,020                       |
| Ala                                             | 0,80      | +0,15                       | +0,120                       |
| Fuselaje                                        | 0,40      | +0,20                       | +0,080                       |
| Empenaje                                        | 0,20      | +0,70                       | +0,140                       |
| Motor + ESC + hélice                            | 0,42      | +0,90                       | +0,378                       |
| Servos (5)                                      | 0,30      | +0,15                       | +0,045                       |
| Tolva vacía + tambor                            | 0,30      | +0,08                       | +0,024                       |
| Tren principal (2 conjuntos)                    | 0,14      | +0,12                       | +0,017                       |
| Tren de morro                                   | 0,11      | −0,45                       | −0,050                       |
| **Vacío (sin bolas)**                           | **4,62**  |                             | **+0,369 → CG = +0,080 m**   |
| Bolas (2,5 kg)                                  | 2,50      | +0,08                       | +0,200                       |
| **Cargado**                                     | **7,12**  |                             | **CG = +0,080 m (27 % MAC)** |

Idea clave: el motor pesa mucho y está en la cola, así que la batería va en el morro para compensar. La tolva se coloca justo en el CG del avión vacío, así que el CG no cambia cuando se vacía.

> ⚠ **Nota del repositorio:** el diagrama de arriba es un esquema de orden (en el informe original la batería figuraba con 0,7 kg y cotas que no coincidían con la tabla); **manda la tabla**. Recalcula con `python3 tools/perf_calc.py masas`. Con la batería real de 1,5 kg (ficha de la hoja de materiales) el avión vacío pesa 4,72 kg y el CG cae a 74,5 mm (**24,8 % MAC**, por debajo del objetivo); cargado, 7,22 kg y 76,4 mm (25,5 % MAC). Adelantar el CG así es lo seguro, pero queda en el borde: mover la batería ~17 mm hacia atrás (de −0,18 a −0,163 m) devuelve el CG a 80 mm. Hay que pesar el avión real y ajustar según 9.8.

## 2.3 Materiales y piezas de corte

La lista completa con precios, enlaces y sumatorio está en [`hardware/bom/materiales_dron.xlsx`](../hardware/bom/materiales_dron.xlsx) (hoja 'Lista de compra') y en [Materiales](materiales.md). Total base: **951,46 €**, sin envíos ni el acelerador Hailo. Supera los 700 € en unos **250 €**; ver la sección 7.

> ⚠ **Nota del repositorio:** el informe original decía «861,46 €… unos 160 €» en esta frase (cifras de una versión anterior de la hoja); se corrigen a las de la hoja actual, que coinciden con el resumen y la sección 7 ([D1](discrepancias-y-pendientes.md)).

| Material                           | Medida (mm)                                                          | Cantidad                  | Uso                                                                                |
|------------------------------------|----------------------------------------------------------------------|---------------------------|------------------------------------------------------------------------------------|
| Foam XPS 40 mm, plancha 1200 × 600 | 750 × 300 × 40 (2 piezas por semiala)                                | 4 planchas (2 de reserva) | Semialas del ala. Cada plancha da 2 piezas de 750 × 300                            |
| Foam XPS 10 mm, plancha 1200 × 600 | Laterales 900 × 120; base y tapa 900 × 150; cuadernas 150 × 120 (x3) | 6 planchas                | Fuselaje (caja de 900 mm)                                                          |
| Foam XPS 5 mm, plancha 1200 × 600  | Horizontal 600 × 320; vertical 250 × 600                             | 1 plancha                 | Empenaje                                                                           |
| Tubo carbono 12/10 mm              | 1000                                                                 | 4                         | Larguero: 2 por semiala, cada uno cruza la junta entre piezas (250 mm en cada una) |
| Tubo carbono 16/14 mm              | Botalón 500 (**el manguito central pasa a ser 20/18 × 150, ver nota**)                                      | 1 tubo de 1000            | Botalón de la cola y manguito de unión central                                     |

> ⚠ **Nota del repositorio:** con 2° de diedro por semiala los tubos de 12 mm entran inclinados en el manguito y necesitan 2,62 mm de holgura radial; el manguito 16/14 solo da 1,0 mm. Se usa un **manguito 20/18 × 150 mm** (tubo de 1 m, línea 32 de la lista; sobra material para repetir) relleno con epoxi espesado ([S10](discrepancias-y-pendientes.md), [Decisiones de diseño](decisiones-de-diseno.md)).
| PETG impreso                       | Tolva 300 × 200 × 100 (2 piezas); tambor Ø180 con 6 celdas de 50 mm  | 1 juego                   | Tolva, tambor, soporte del motor, bujes                                            |

Los cortes del foam salen de las plantillas en escala 1:1 (apartado 9.2). Sobra material en las planchas: guárdalo para repetir piezas si fallan.

**Consejo:** corta el ala en dos semialas con un manguito de carbono en el centro. Así cabe en un taller pequeño y es más fácil de transportar.

## 2.4 Tren de aterrizaje

Triciclo fijo: un tren de morro y dos principales bajo el ala. Con la hélice en la cola (pusher), la hélice no toca el suelo siempre que haya holgura suficiente.

| Parámetro                         | Valor                                                             |
|-----------------------------------|-------------------------------------------------------------------|
| Configuración                     | Triciclo fijo                                                     |
| Posición de las principales       | x = +0,12 m (justo detrás del CG), a ±0,30 m del eje, bajo el ala |
| Posición del morro                | x = −0,45 m, bajo la caja del fuselaje                            |
| Vía (distancia entre principales) | 0,60 m                                                            |
| Ruedas principales                | 80–90 mm de diámetro                                              |
| Rueda de morro                    | 60 mm de diámetro                                                 |
| Masa total                        | ≈ 0,25 kg (0,14 principales + 0,11 morro)                         |
| Holgura de la hélice              | ≥ 50 mm entre la punta inferior de la hélice y el suelo (**ver nota: usar ≥ 70–100 mm**) |

> ⚠ **Nota del repositorio:** con 50 mm de holgura la hélice pusher toca el suelo con solo 3,7° de cabeceo (brazo 0,78 m desde las ruedas principales); 5° exigen 68 mm y 15° (el valor por defecto de ArduPilot) 209 mm. Usa **≥ 70–100 mm**, limita el cabeceo de despegue a 5° y añade una aleta ventral ([S9](discrepancias-y-pendientes.md), [Decisiones de diseño](decisiones-de-diseno.md)).

Materiales: patas de aluminio de 4 mm (perfil en L), soportes de PETG impresos, ruedas de 80–90 mm con eje de 5 mm y tuerca M5. El kit triciclo de 55 mm sirve para probar la rodadura, pero para 7 kg las ruedas de 80–90 mm se comportan mejor en hierba.

---
[← 1. Análisis de viabilidad y planta motriz](01-viabilidad-y-propulsion.md) · [Índice](README.md) · [3. Mecanismo de carga útil (reforestación) →](03-carga-util-reforestacion.md)
