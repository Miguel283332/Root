# 0. Resumen ejecutivo

> Convertido del [informe técnico v3](fuentes/informe_tecnico_dron_reforestador_v3.docx), sección 0. La numeración original se conserva (otras secciones la citan). Las notas `⚠` son del repositorio y no estaban en el informe.


| Tema               | Conclusión                                                                              | Impacto                                                                         |
|--------------------|-----------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| Objetivo           | Máxima autonomía. Los 80 km/h no son necesarios                                         | Crucero a 45–50 km/h                                                            |
| Hélice             | Se mantiene la APC 18x5.5 (ya la tienes)                                                | Su paso limita la velocidad a unos 74 km/h teóricos, suficiente para el crucero |
| Batería            | 6S 10000 mAh (1,4–1,5 kg)                                                               | 76–89 min de vuelo a 45–50 km/h                                                 |
| Tren de aterrizaje | Triciclo fijo: morro y 2 principales, unos 0,25 kg                                      | Ruedas de 80–90 mm; ver 2.4 y 9.4b                                              |
| Empuje             | BR4114 KV 400 + 18x5.5 en 6S: unos 5,8 kg al 100 %                                      | Suficiente para un MTOW de 7,1 kg                                               |
| Control            | Emisora + ESP32 + PCA9685 para el vuelo manual; controladora ArduPilot para el autónomo | Ver sección 4                                                                   |
| Carga útil         | 250 bolas de 10 g (2,5 kg) en una tolva de unos 6 L                                     | Tambor de 6 celdas accionado por servo                                          |
| Presupuesto        | ≈ 921 € con los precios encontrados (hoja de cálculo)                                   | Supera 700 € en unos 220 €; ver sección 7                                       |
| Tiempo             | Unas 60–85 horas de trabajo                                                             | Ver sección 8                                                                   |

> Supuestos: BR4114 KV 400, batería 6S nominal 22,2 V (8S = 29,6 V), densidad del aire a nivel del mar 1,225 kg/m3, eficiencia de la hélice ~0,6 a estas velocidades, eficiencia motor+ESC ~0,8. Son estimaciones de primera aproximación (±25 %). Hay que medirlas en banco y en vuelo.

> ⚠ **Nota del repositorio:** Los pendientes que condicionan la compra y la seguridad (fusible de 40 A frente a ~54 A de consumo, mecanismo del tambor, ESC, calibración de la batería, datos de terreno…) están recogidos en [Discrepancias y pendientes](discrepancias-y-pendientes.md). Las cifras de presupuesto de esta tabla (921 €) coinciden con `hardware/bom/materiales_dron.xlsx`; la sección 2.3 del informe original decía 861,46 € por un error de versión.

---
[← Índice](README.md) · [Índice](README.md) · [1. Análisis de viabilidad y planta motriz →](01-viabilidad-y-propulsion.md)
