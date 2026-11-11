# 02 · Glosario

## Aerodinámica y estructura

| Término | Significado |
|---|---|
| **Cuerda** | Distancia del borde de ataque al de salida del ala (aquí 300 mm) |
| **MAC** | Cuerda media aerodinámica; en un ala rectangular es la propia cuerda. El CG se da en % de MAC |
| **Borde de ataque / de salida** | Parte delantera / trasera del ala o de un timón |
| **Perfil** | Forma de la sección del ala (aquí **Clark Y**, 12 % de grosor) |
| **Envergadura** | Longitud de punta a punta del ala (3 m) |
| **Alargamiento (AR)** | Envergadura² / superficie = 10. Alas largas y estrechas gastan menos energía (más autonomía) |
| **CL, CLmax** | Coeficiente de sustentación y su máximo; CLmax ≈ 1,2 fija la velocidad de pérdida |
| **Pérdida (stall)** | Pérdida brusca de sustentación por falta de velocidad o exceso de ángulo |
| **Ángulo de ataque** | Ángulo entre la cuerda del ala y el aire que llega |
| **Incidencia** | Ángulo con que el ala se **monta** sobre el fuselaje (~4° aquí) |
| **Diedro** | Inclinación en "V" de las semialas; da estabilidad de alabeo |
| **Larguero** | Tubo/viga interior que soporta la flexión del ala |
| **Cuaderna** | Tabique que da forma a la caja del fuselaje |
| **Botalón** | Tubo trasero que sostiene cola y motor |
| **Empenaje** | La cola completa |
| **CG** | Centro de gravedad |
| **MTOW** | Peso máximo al despegue (~7,1 kg; límite de diseño 7,5 kg) |
| **Pusher / tractor** | Hélice que empuja (detrás) / que tira (delante) |
| **Triciclo** | Tren con rueda de morro y dos principales |
| **Hilo caliente** | Alambre de nicromo calentado con corriente que corta el foam |
| **XPS** | Espuma rígida de poliestireno extruido (la de aislamiento) |
| **Película termorretráctil** | Lámina plástica adhesiva que se encoge con calor y forra el avión |
| **CA / epoxi** | Cianoacrilato (pegamento rápido para foam) / resina de dos componentes para uniones de carga |
| **PETG** | Plástico de impresión 3D resistente al calor y a la humedad |

## Electrónica

| Término | Significado |
|---|---|
| **LiPo 6S** | Batería de litio-polímero de 6 celdas en serie (22,2 V nominales; 25,2 V cargada; **nunca por debajo de 3,5 V/celda**) |
| **mAh, Ah, Wh** | Capacidad: 10 000 mAh = 10 Ah; ×22,2 V = 222 Wh de energía |
| **C (tasa C)** | Cuánta corriente puede dar la batería: 10 C × 10 Ah = 100 A |
| **Motor brushless** | Motor sin escobillas, trifásico, el de aeromodelismo (tres cables) |
| **KV** | Revoluciones por minuto por voltio sin carga: 400 KV × 22,2 V ≈ 8 880 rpm |
| **ESC** | Regulador electrónico de velocidad: convierte la señal de gas en corriente trifásica para el motor |
| **BEC** | Regulador que baja la tensión de la batería a 5 V / 6 V para servos y electrónica |
| **Servo** | Motor pequeño que mueve un mando al ángulo que se le indica |
| **PWM** | Señal de pulsos (1000–2000 µs, 50 por segundo) con que se mandan servos y ESC |
| **PCA9685** | Placa que genera 16 señales PWM a partir de órdenes I²C de la ESP32 |
| **ESP32 / Raspberry Pi 5** | Microcontrolador de la fase 1 / ordenador compañero de la fase 2 (visión) |
| **XT60 / XT90** | Conectores de potencia (60 A / 90 A) |
| **Fusible** | Protege contra cortocircuito; aquí 80 A de acción lenta |
| **I²C, UART** | Tipos de conexión entre placas (dos hilos de datos / TX-RX) |
| **GND** | Masa, el cable negativo común |
| **Failsafe** | Acción automática si algo falla (p. ej. si se pierde la señal de la emisora) |

## Vuelo y ArduPilot

| Término | Significado |
|---|---|
| **ArduPilot / ArduPlane** | Software libre de piloto automático; ArduPlane es la versión para aviones |
| **Controladora de vuelo** | La placa que lo ejecuta (Matek H743-Wing) |
| **MANUAL, FBWA, AUTO, RTL** | Modos de vuelo (ver [01](01-como-vuela-y-partes.md)) |
| **Failsafe de batería** | Aviso/acción cuando la batería baja de un umbral (3,5 V por celda → RTL) |
| **EKF** | Filtro que calcula posición y actitud mezclando sensores |
| **Pitot / sensor de velocidad** | Tubito que mide la velocidad del aire (MS4525DO) |
| **GPS / brújula** | Posición y rumbo |
| **AGL** | Altura sobre el suelo |
| **SRTM** | Mapas de elevación del terreno que se guardan en la tarjeta SD |
| **Waypoint** | Punto de la misión |
| **MAVLink** | Protocolo con el que la controladora habla con el ordenador y la estación de tierra |
| **SITL** | Simulador: ejecuta el piloto automático en el ordenador, sin avión |
| **Mission Planner / QGroundControl** | Programas de la estación de tierra (configurar y planificar misiones) |
| **Interlock** | Condiciones de seguridad que deben cumplirse para soltar semillas |
| **STL / G-code** | Archivo de forma 3D / instrucciones que lee la impresora |
| **CMake / ctest** | Herramientas que descargan, compilan y prueban este repositorio |
