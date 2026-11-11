# 7. Presupuesto

> Convertido del [informe técnico v3](fuentes/informe_tecnico_dron_reforestador_v3.docx), sección 7. La numeración original se conserva (otras secciones la citan). Las notas `⚠` son del repositorio y no estaban en el informe.


Ya tienes: motor BR4114 KV 400, hélice APC 18x5.5, emisora y transmisor, ESP32, PCA9685 y Raspberry Pi 5 16 GB. La lista incluye solo lo que falta. Precios de Amazon.es o Leroy Merlin cuando existen; los marcados como estimación no tienen precio visible. Detalle en [Materiales](materiales.md) (generado desde `hardware/bom/materiales_dron.xlsx`).

| Partida                                                                             | Coste aprox.      | Notas                                      |
|-------------------------------------------------------------------------------------|-------------------|--------------------------------------------|
| Tubos de carbono (12 y 16 mm)                                                       | 144 €             | Mayor partida del ala                      |
| Servos 20 kg·cm (5)                                                                 | 105 €             | Puedes usar servos más ligeros en alerones |
| Controladora ArduPilot (fase 2)                                                     | 103 €             | Solo para el vuelo autónomo                |
| Batería 6S 10 Ah                                                                    | 85 € (estimación) | Define la autonomía                        |
| ESC 80 A                                                                            | 50 €              |                                            |
| Tren de aterrizaje (triciclo y ruedas)                                              | 60 € (estimación) | Kit de prototipo y ruedas de 80–90 mm      |
| Resto (foam, películas, adhesivos, herramientas, GPS, pitot, cámara, BEC, cableado) | 375 €             |                                            |
| **Total (sin acelerador Hailo)**                                                    | **921 €**         | Supera los 700 € en unos 220 €             |

> ⚠ **Nota del repositorio:** (ver la nota siguiente: la cifra de esta tabla, 921 €, es la del informe original; la hoja de materiales vigente suma 951,46 €).

> ⚠ **Nota del repositorio:** con el manguito 20/18 que exige el diedro (línea 32, 30 € estimados) el total pasa a **951,46 €**; el 52 % (492,95 €) son precios sin verificar y se supera el presupuesto en **251,46 €**; solo la fase 1 cuesta 738,77 € ([C5, C6](discrepancias-y-pendientes.md)). Total y desglose reproducibles con `python3 tools/bom.py`.

Para bajar de 700 € sin tocar el objetivo de autonomía: retrasar la cámara y el pitot hasta la fase 2 (unos 70 €), usar servos más ligeros en los alerones (estimado 30–40 €) y buscar tubos de carbono de 12 mm más baratos. Son estimaciones; hay que compararlas en tienda.

---
[← 6. Tests clave](06-tests.md) · [Índice](README.md) · [8. Tiempo estimado de elaboración →](08-tiempo.md)
