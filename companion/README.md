# companion — ordenador compañero (Raspberry Pi 5)

Paquete Python mínimo para la **fase 2**: la Raspberry Pi 5 habla MAVLink 2 con la
controladora ArduPilot por UART (`SERIAL2`, 921600 baudios).

| Orden | Qué hace |
|---|---|
| `python -m root_companion estado` | conecta y muestra modo de vuelo |
| `python -m root_companion telemetria -o vuelo.csv` | guarda posición, velocidades, batería, modo, armado (1 Hz) |
| `python -m root_companion soltar alta` | pide un lote de bolas; **ArduPilot decide si es seguro** |

```bash
pip install -e companion            # instala pymavlink
python -m root_companion -c tcp:127.0.0.1:5760 estado     # contra el simulador SITL
python -m root_companion -c /dev/ttyAMA0 telemetria -o vuelo.csv   # en el avión
```

La visión (cámara IMX708 + Hailo) irá en un módulo aparte; empieza **solo detectando y
registrando**, sin actuar (informe 9.10, punto 11). Cableado y alimentación (BEC 5 V / 5 A
independiente para la RPi): `docs/04-electronica-y-vuelo-autonomo.md`.
