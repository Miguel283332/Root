# 5. Hoja de ruta de construcción

> Convertido del [informe técnico v3](fuentes/informe_tecnico_dron_reforestador_v3.docx), sección 5. La numeración original se conserva (otras secciones la citan). Las notas `⚠` son del repositorio y no estaban en el informe.


| Fase                                 | Horas de trabajo       | Tareas                                                            | Criterio de salida                       |
|--------------------------------------|------------------------|-------------------------------------------------------------------|------------------------------------------|
| 9.2 Diseño                           | 8–10                   | XFLR5 y OpenVSP, plantillas a escala 1:1                          | CG en 25–30 % MAC; hélice elegida        |
| Compras                              | 0 (5–10 días de envío) | Lista de la sección 7; pide primero la batería y la hélice        | Todo recibido                            |
| 9.3 Ala                              | 14–18                  | Cortar con hilo caliente, canal y larguero, unir semialas, cubrir | Ala recta, sin alabeos, peso ≤ 0,8 kg    |
| 9.4 Fuselaje, cola y motor           | 6–8                    | Caja de fuselaje, botalón, cola, soporte del motor                | Cola alineada con el ala; motor centrado |
| 9.5 Tolva y tambor                   | 6–8                    | Imprimir, montar tambor y servo, probar en seco                   | 10 pulsos = 10 bolas                     |
| 9.6 y 9.7 Electrónica fase 1 y banco | 8–10                   | Cableado, ESP32 y PCA9685, calibrar ESC, prueba de empuje         | Curva empuje–gas medida                  |
| 9.8 Ajuste del CG                    | 1–2                    | Pesar, marcar y mover la batería                                  | CG en 27 % MAC                           |
| 9.9 Vuelos manuales                  | 6–10                   | Planeo, vuelos cortos, crucero, prueba con bolas                  | Vuelo estable de 10 min con carga        |
| 9.10 Fase 2 (ArduPilot + RPi 5)      | 12–16                  | Configurar controladora, failsafe, terreno, visión                | Misión corta automática sin incidencias  |
| **Total**                            | **61–84**              |                                                                   |                                          |

> ⚠ **Nota del repositorio:** las filas suman **61–82 h**, no 61–84, y el tren de aterrizaje (9.4b, 2–3 h) no figura en la tabla: con él son **63–85 h**, que cuadra con el «60–85 h» del resumen ([D3](discrepancias-y-pendientes.md)).

---
[← 4. Arquitectura electrónica y vuelo autónomo](04-electronica-y-vuelo-autonomo.md) · [Índice](README.md) · [6. Tests clave →](06-tests.md)
