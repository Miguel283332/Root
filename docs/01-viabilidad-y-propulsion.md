# 1. Análisis de viabilidad y planta motriz

> Convertido del [informe técnico v3](fuentes/informe_tecnico_dron_reforestador_v3.docx), sección 1. La numeración original se conserva (otras secciones la citan). Las notas `⚠` son del repositorio y no estaban en el informe.


## 1.1 Empuje estimado (BR4114 KV 400 + APC 18x5.5, 6S)

| Acelerador | Potencia eléctrica aprox. | Empuje estático aprox. | Empuje/peso (MTOW 6,9 kg) |
|------------|---------------------------|------------------------|---------------------------|
| 30 %       | ~150 W                    | ~1,5 kg                | 0,22                      |
| 50 %       | ~400 W                    | ~2,8 kg                | 0,41                      |
| 75 %       | ~800 W                    | ~4,4 kg                | 0,64                      |
| 100 %      | ~1200 W (~60 A)           | ~5,8 kg                | 0,84                      |

> ⚠ **Nota del repositorio:** la columna de empuje/peso usa **6,9 kg**, pero el MTOW de 1.4 es **7,1 kg** (≈ 7,2 kg con la batería real de 1,5 kg): a gas pleno el empuje/peso es 0,82, no 0,84. A 100 % de gas el sistema consume ~1200 W / 22,2 V ≈ **54 A**: ojo con el fusible de 40 A de la sección 4 ([S1](discrepancias-y-pendientes.md)). Tabla reproducible con `python3 tools/perf_calc.py empuje` (figura de mérito 0,7, η motor+ESC 0,8; salen 1,44 / 2,78 / 4,41 / 5,77 kg).

Método: teoría del disco de actuador. Forma de cálculo:

$$T^{3/2} = P \cdot \eta_{\text{motor-ESC}} \cdot FM \cdot \sqrt{2 \rho A}$$

Con A = pi (0,2286 m)^2 = 0,164 m^2, el disco de la hélice de 18 pulgadas. Confirma el límite de corriente del fabricante: a 60 A el motor trabaja cerca de su máximo.

## 1.2 Velocidad: la 18x5.5 basta

La velocidad teórica de paso es paso × rpm: 0,1397 m × 148 rev/s ≈ 20,7 m/s (74 km/h) sin carga. Con carga el límite real es menor, pero sobra para el crucero.

| Velocidad de vuelo | Relación con la pérdida (V_s ≈ 36 km/h) | Comentario                          |
|--------------------|-----------------------------------------|-------------------------------------|
| 40 km/h            | 1,11                                    | Margen insuficiente: no recomendado |
| 45 km/h            | 1,25                                    | Crucero recomendado                 |
| 50 km/h            | 1,39                                    | Crucero recomendado, con más margen |
| 60 km/h            | 1,67                                    | Solo para tramos de transición      |

**Recomendación:** crucero a 45–50 km/h. La velocidad de pérdida es de unos 36 km/h sin flaps y de unos 32 km/h con flaps.

> ⚠ **Nota del repositorio:** el diseño actual **no tiene flaps** (5 servos: 2 alerones, profundidad, timón y tambor), así que la cifra «con flaps» no es aplicable; la pérdida real de diseño es la de 36 km/h ([S3](discrepancias-y-pendientes.md)).

## 1.3 Autonomía según velocidad (batería 6S 10 Ah)

Energía útil = 80 % de 222 Wh = 178 Wh. Potencias eléctricas estimadas para un MTOW de 6,9 kg.

| Velocidad | Potencia eléctrica aprox. | Autonomía (10 Ah) | Autonomía (5 Ah) | Alcance (10 Ah) |
|-----------|---------------------------|-------------------|------------------|-----------------|
| 45 km/h   | ~120 W                    | ~89 min           | ~45 min          | ~67 km          |
| 50 km/h   | ~140 W                    | ~76 min           | ~38 min          | ~64 km          |
| 60 km/h   | ~200 W                    | ~54 min           | ~27 min          | ~54 km          |

Lectura: 45 km/h da la máxima autonomía con margen sobre la pérdida. Con una hélice de paso bajo, la eficiencia real puede ser menor que 0,6, así que estas cifras son optimistas hasta medirlas en vuelo.

> ⚠ **Nota del repositorio:** el modelo (`tools/perf_calc.py crucero`) usa CD0 = 0,03, e = 0,8 y η hélice × η motor = 0,6 × 0,8, y reproduce las tres filas (122 / 142 / 201 W; 87 / 75 / 53 min). Sigue siendo una estimación de primera aproximación: **medir en banco y en vuelo** ([D10](discrepancias-y-pendientes.md)).

## 1.4 Peso máximo al despegue (MTOW)

| Bloque                                                                                                   | Masa (kg)                                     |
|----------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| Estructura (ala, fuselaje, empenaje, sin tren)                                                           | 1,40                                          |
| Propulsión: BR4114 (~0,30) + ESC 80 A (~0,10) + hélice (~0,02)                                           | 0,42                                          |
| Batería 6S 10000 mAh (1,4–1,5 kg según modelo)                                                           | 1,40                                          |
| Electrónica de vuelo (ESP32, PCA9685, receptor, BEC, cableado; en fase 2 suma controladora, GPS y pitot) | 0,45                                          |
| Ordenador compañero (RPi 5 + cámara)                                                                     | 0,10                                          |
| Servos (5 de 60 g)                                                                                       | 0,30                                          |
| Tolva vacía + tambor                                                                                     | 0,30                                          |
| Tren de aterrizaje (triciclo, ruedas incluidas)                                                          | 0,25                                          |
| **Subtotal sin carga útil**                                                                              | **4,62**                                      |
| Carga útil (250 bolas de 10 g)                                                                           | 2,50                                          |
| **MTOW**                                                                                                 | **≈ 7,1 kg** (diseño con margen hasta 7,5 kg) |

## 1.5 Prestaciones básicas (ala de 3 m, superficie 0,9 m², peso 67 N)

| Parámetro                                    | Valor             | Cálculo                       |
|----------------------------------------------|-------------------|-------------------------------|
| Velocidad de pérdida (CLmax ≈ 1,2)           | ~36 km/h          | V_s = raíz(2W / (ρ S CLmax))  |
| Velocidad de pérdida con flaps (CLmax ≈ 1,5) | ~32 km/h          | CLmax ≈ 1,5                   |
| Velocidad de crucero recomendada             | 45–50 km/h        | Máxima autonomía              |
| Coeficiente de sustentación a 45 km/h        | CL ≈ 0,77         |                               |
| Potencia de crucero a 45 km/h                | ~120 W eléctricos | Incluye eficiencias           |
| Carrera de despegue                          | ~10–20 m          | Empuje medio ≈ 0,6 × estático |

---
[← 0. Resumen ejecutivo](00-resumen-ejecutivo.md) · [Índice](README.md) · [2. Diseño aerodinámico y estructural (inspiración MQ-9) →](02-diseno-aerodinamico-estructural.md)
