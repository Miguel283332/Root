# firmware/esp32_fase1 — vuelo manual (fase 1)

Emisora → ESP32 → PCA9685 → servos y ESC (informe técnico 4.1, 4.4 y 9.6).

* `lib/root_safety/root_safety.h` — lógica de seguridad **probada en el PC** (`ctest`):
  failsafe a los 0,5 s, armado por interruptor, límite de gas del 70 %, tambor por flancos,
  decodificador SBUS.
* `src/main.cpp` — conexión con el hardware. **No probado en hardware.** Comprueba los pines I2C
  de tu placa y el mapa de canales antes de conectar nada.

```bash
pio run -d firmware/esp32_fase1         # compilar (necesita PlatformIO)
pio run -d firmware/esp32_fase1 -t upload
```

Pendiente de confirmar con el propietario: **qué protocolo usa su emisora/enlace actual**
(informe 4.6, opción B). Mientras no esté definido, el firmware arranca en FAILSAFE.
