# 4. Arquitectura electrónica y vuelo autónomo

> Convertido del [informe técnico v3](fuentes/informe_tecnico_dron_reforestador_v3.docx), sección 4. La numeración original se conserva (otras secciones la citan). Las notas `⚠` son del repositorio y no estaban en el informe.


## 4.1 Fase 1: vuelo manual con tu sistema actual

Tu emisora se conecta a la ESP32, que envía las órdenes al PCA9685 y este mueve los servos y el ESC. Sirve para el vuelo manual, las pruebas de tierra y las de tolva. No estabiliza el avión, no tiene GPS ni retorno automático.

Requisitos mínimos de seguridad en la ESP32:

- Si se pierde la señal más de 0,5 s: gas a cero y superficies a neutro.

- Armado con un interruptor de la emisora; sin armado, el canal del motor siempre a cero.

- Límite de gas máximo en las primeras pruebas, por ejemplo 70 %.

## 4.2 Comparativa: Raspberry Pi 5 + IA frente a ESP32 + sensores/internet

| Criterio                                    | Raspberry Pi 5 16 GB + cámara              | ESP32 + sensores + datos online                                |
|---------------------------------------------|--------------------------------------------|----------------------------------------------------------------|
| Control de actitud en tiempo real           | Malo: Linux no es tiempo real              | Justo: FreeRTOS, pero hay que escribir todo el estimador (EKF) |
| Modos de vuelo (RTL, misiones, failsafe)    | Hay que programarlos                       | Ya los trae ArduPilot                                          |
| Visión por IA (zona de siembra, obstáculos) | Excelente con acelerador Hailo (AI HAT+)   | Imposible o muy limitado                                       |
| Altitud mínima sobre el terreno             | Con mapa SRTM offline                      | Depende de internet: riesgo en vuelo                           |
| Dependencia de internet                     | Ninguna si el mapa está en la SD           | Alta, si el enlace 4G cae                                      |
| Consumo                                     | 5–12 W + cámara                            | Menos de 1 W                                                   |
| Coste adicional                             | 0 € (ya la tienes); AI HAT ~110 € opcional | ~10 €                                                          |
| Tiempo de desarrollo                        | Alto                                       | Muy alto (reinventar el piloto)                                |

## 4.3 Veredicto: ruta en dos fases

- Fase 1 (manual): emisora → ESP32 → PCA9685. Sirve para aprender el avión, probar la tolva y volar a mano. No necesitas nada más.

- Fase 2 (autónomo): añade una controladora ArduPilot (Matek H743 o similar, ~80 €) con GPS y pitot. ArduPilot estabiliza el avión, sigue misiones, mantiene la altura sobre el terreno y vuelve a casa. La RPi 5 se conecta a la controladora por UART con MAVLink para la visión.

> ⚠ **Nota del repositorio:** el informe estima la controladora en ~80 €; la hoja de materiales la lista a **102,69 €** (Rotorama, en stock). Usa la placa `MatekH743` de ArduPilot ([D6](discrepancias-y-pendientes.md)).

- La ESP32 no estabiliza el avión en fase 2. Reescribir el estimador de actitud y el piloto automático es el riesgo más grande del proyecto. Puede quedarse como controlador de la tolva o eliminarse.

- Altitud mínima: el seguimiento de terreno de ArduPilot usa datos SRTM guardados en la tarjeta SD. No necesita internet en vuelo.

## 4.4 Diagramas de conexiones

Fase 1 (manual):

```text
Emisora propia --radio--> ESP32 --I2C--> PCA9685 --+--> CH0 alerón izq.
                                                   +--> CH1 alerón der.
                                                   +--> CH2 profundidad
                                                   +--> CH3 timón
                                                   +--> CH4 tambor (bolas)
                                                   +--> CH5 ESC -> BR4114
```


Fase 2 (automático):

```text
            Receptor de la emisora
                     | CRSF / SBUS
 +-----------+       |        +-----------------------+       +-------------------+
 | GPS M10 + |------>+------->| CONTROLADORA DE VUELO |<----->| RPi 5 16 GB       |
 | compás    |                | ArduPilot (H743)      | UART  | + AI HAT (Hailo)  |
 +-----------+                | IMU - baro - EKF      |MAVLink| + cámara CSI      |
 +-----------+                |                       |       +-------------------+
 | Pitot     |--------------->| Salidas PWM:          |
 | MS4525DO  |   (I2C)        |  S1 alerón izq.       |
 +-----------+                |  S2 alerón der.       |
                              |  S3 profundidad       |
                              |  S4 timón             |
                              |  S5 tambor (bolas)    |
                              |  M1 -> ESC 80 A -> BR4114
                              +-----------^-----------+
                                          | (VBAT)
 BATERIA 6S --[fusible 40 A + interruptor de armado]--+--> ESC (potencia)
                                                      +--> BEC 6 V / 10 A -> servos
                                                      +--> BEC 5 V / 5 A  -> RPi 5 y cámara
```


> ⚠ **Nota del repositorio:** el diagrama de fase 2 pone un «fusible 40 A», pero a gas pleno el consumo es ~54 A: se fundiría en el despegue ([S1](discrepancias-y-pendientes.md)). El reparto ESC / BEC 6 V / BEC 5 V sigue la lista de compra; los modelos de BEC no coinciden con los del texto de 9.6 ([C2, C3](discrepancias-y-pendientes.md)).

## 4.5 Alimentación: puntos críticos

- La RPi 5 necesita 5 V / 5 A estables. Un BEC débil provoca reinicios en vuelo. Usa un BEC independiente para ella.

- Los servos necesitan 6 V y buena corriente. Aliméntalos desde un BEC de 6 V, no desde la ESP32 ni desde la controladora.

- El PCA9685 se alimenta con 6 V para los servos y con 3,3 o 5 V para su lógica, según tu módulo. Comparte masa (GND) con la batería.

- Pon un sensor de tensión y un failsafe por batería baja (3,5 V por celda).

## 4.6 Servos, ESC y emisora con ArduPilot

En fase 2 la controladora genera sus propias señales PWM. Los servos y el ESC se conectan a sus salidas, y el PCA9685 ya no hace falta.

| Función                | Salida de la controladora | Función en ArduPilot (SERVOx_FUNCTION)                 |
|------------------------|---------------------------|--------------------------------------------------------|
| Alerón izquierdo       | S1                        | Aileron (4)                                            |
| Alerón derecho         | S2                        | Aileron, con el sentido invertido si hace falta        |
| Profundidad (elevador) | S3                        | Elevator (19)                                          |
| Timón                  | S4                        | Rudder (21)                                            |
| Tambor de bolas        | S5                        | Salida libre, controlada con DO_SET_SERVO en la misión |
| Motor BR4114 (ESC)     | M1                        | Throttle (70)                                          |

Los números son los de ArduPilot en la versión que uses; comprueba cada uno en la pestaña Setup > Servo Output de Mission Planner.

> ⚠ **Nota del repositorio:** el repositorio usa el reparto estándar de ArduPlane: **SERVO1** alerón izq. · **SERVO2** profundidad · **SERVO3** gas (ESC) · **SERVO4** timón · **SERVO5** alerón der. · **SERVO6** tambor (función 94, «Script 1»). Los rótulos S1–S5 / M1 de la tabla son los del informe: confirma la correspondencia con la serigrafía de la placa antes de cablear ([D7](discrepancias-y-pendientes.md)). Todo está en [`root_plane_base.parm`](../ardupilot/params/root_plane_base.parm).

**Emisora: dos opciones**

- **A. Receptor estándar** (ELRS, FrSky o similar) conectado al puerto RC de la controladora (CRSF o SBUS). ArduPilot lee los canales en tiempo real y el modo de vuelo se asigna a un interruptor de tres posiciones: MANUAL, FBWA (estabilizado) y AUTO. RTL va en un cuarto modo o en un interruptor aparte.

- **B. Tu emisora actual con la ESP32**: la ESP32 puede actuar de receptor y enviar señal SBUS (o CRSF) a la entrada RC de la controladora, así mantienes tu emisora. Esto exige un firmware SBUS para la ESP32. Si tu enlace es propietario, hay que traducirlo: dime qué protocolo usa para confirmar la vía.

Los servos se alimentan desde el BEC de 6 V y la controladora se alimenta de la batería. Comparte masa en todo el sistema.

## 4.7 Despegue y aterrizaje autónomos

**Despegue: relativamente sencillo.** ArduPilot tiene un comando TAKEOFF que acelera en línea recta a gas máximo, rota al alcanzar una velocidad y sube hasta la altitud objetivo. Requisitos:

- Sensor de velocidad (pitot) y GPS con fijación 3D y más de 8 satélites.

- Brújula calibrada, lejos de cables y del motor.

- Pista recta, horizontal, con viento de cara.

- Parámetros de despegue: TKOFF_ALT (altitud objetivo), TKOFF_THR_MAX (gas máximo), TKOFF_ROTATE_SPD (velocidad de rotación, unos 12 m/s para este avión) y TKOFF_LVL_ALT (altura a la que nivela). Verifica los nombres en tu versión.

**Aterrizaje: el más difícil.** Hay que llegar a baja velocidad, con la altura y el rumbo bien controlados, y el viento y el error del GPS pesan más. Requisitos:

- Pista larga (60 m o más) alineada con el viento, y punto de umbral bien medido.

- Aproximación a unos 40–45 km/h (unas 1,25 veces la pérdida), con altura de aproximación de 30–40 m.

- Parámetros de aterrizaje: LAND_FLARE_ALT (altura de enderezado, unos 2–3 m), LAND_FLARE_SEC (duración del enderezado) y LAND_PITCH_DEG (cabeceo objetivo al tocar; el informe usa el nombre antiguo `LAND_PITCH_CD`). Comprueba los nombres en tu versión.

> ⚠ **Nota del repositorio:** con ArduPilot 4.7.2 se verificó que `TKOFF_ALT`, `TKOFF_LVL_ALT`, `TKOFF_THR_MAX`, `TKOFF_ROTATE_SPD`, `LAND_FLARE_ALT`, `LAND_FLARE_SEC` y `LAND_PITCH_DEG` existen. Valores de partida en [`root_plane_base.parm`](../ardupilot/params/root_plane_base.parm).

- Gas de aborto configurado: si la aproximación no es estable, ArduPilot da gas y sube de nuevo.

**Recomendación:** los primeros aterrizajes, siempre en modo FBWA con piloto al mando. El aterrizaje automático se activa cuando el manual sale bien varias veces seguidas. El RTL es el modo de emergencia: vuelve al punto de inicio y aterriza ahí.

---
[← 3. Mecanismo de carga útil (reforestación)](03-carga-util-reforestacion.md) · [Índice](README.md) · [5. Hoja de ruta de construcción →](05-hoja-de-ruta.md)
