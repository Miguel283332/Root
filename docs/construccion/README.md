# Guía de construcción

Guía paso a paso para empezar desde cero (sección 9 del informe técnico). Cada apartado termina con una
comprobación: **si no se cumple, no se sigue**. Los números (9.2, 9.4b…) son los del informe original y se
citan desde otras secciones.

> Haz las fases en orden. Cada fase termina con una comprobación: si no la cumples, no sigas.

| Apartado | Horas | Qué se hace | Comprobación de salida |
|---|---:|---|---|
| [9.1 Herramientas, materiales y seguridad](9.1-herramientas-y-seguridad.md) | — | Herramientas, hilo caliente, LiPo | — |
| [9.2 Diseño con XFLR5 y OpenVSP](9.2-diseno-xflr5-openvsp.md) | 8–10 | Perfil, ala, plantillas 1:1 | CLmax ≥ 1,2; CG 25–30 % MAC |
| [9.3 Ala](9.3-ala.md) | 14–18 | Corte con hilo caliente, larguero, unión, cubierta | Alabeo ≤ 3 mm; ≤ 0,8 kg |
| [9.4 Fuselaje, cola y motor](9.4-fuselaje-cola-y-motor.md) | 6–8 | Caja, botalón, empenaje, soporte del motor | Sin holgura; motor alineado (< 1°) |
| [9.4b Tren de aterrizaje](9.4b-tren-de-aterrizaje.md) | 2–3 | Triciclo fijo, ruedas 80–90 mm | Nivelado; hélice ≥ 50 mm del suelo |
| [9.5 Tolva y tambor](9.5-tolva-y-tambor.md) | 6–8 | Imprimir, montar, probar en seco | 10 pulsos = 10 bolas |
| [9.6 Electrónica de fase 1](9.6-electronica-fase-1.md) | 8–10 | ESP32 + PCA9685, failsafe, armado | Emisora apagada → motor parado |
| [9.7 Pruebas de banco](9.7-pruebas-de-banco.md) | (incl.) | ESC, servos, tolva, empuje, corriente | Curva empuje–gas medida |
| [9.8 Ajuste del CG](9.8-ajuste-del-cg.md) | 1–2 | Pesar y mover la batería | CG en 27 % MAC |
| [9.9 Primeros vuelos manuales](9.9-primeros-vuelos-manuales.md) | 6–10 | Planeo, crucero, carga progresiva | 10 min estables con carga |
| [9.10 Fase 2: ArduPilot y Raspberry Pi 5](9.10-fase-2-ardupilot-y-rpi5.md) | 12–16 | Controladora, failsafes, terreno, misión | Misión corta automática |
| [9.10b Despegue y aterrizaje autónomos](9.10b-despegue-y-aterrizaje-autonomos.md) | (incl.) | SITL, parámetros, FBWA → AUTO | 10 aterrizajes manuales limpios |
| [9.11 Lista de revisión antes de cada vuelo](9.11-checklist-prevuelo.md) | — | Checklist | — |

¿Nunca has hecho algo así? Lee antes la [guía para principiantes](../principiantes/README.md) (más detalle, glosario y errores típicos).

Ver también: [Proceso de elaboración](../proceso-de-elaboracion.md) · [Materiales](../materiales.md) ·
[Discrepancias y pendientes](../discrepancias-y-pendientes.md).
