"""Conexión MAVLink con la controladora."""
from __future__ import annotations

# Raspberry Pi 5: UART0 de los GPIO 14/15 (activar con dtoverlay=uart0-pi5 en config.txt).
# Cableado: TX(RPi)->RX(telem2), RX(RPi)->TX(telem2), GND con GND; sin alimentar la placa desde la RPi.
CONEXION_RPI5 = "/dev/ttyAMA0"
BAUDIOS_RPI5 = 921600           # = SERIAL2_BAUD,921 en matek_h743_wing_v3.parm
CONEXION_SITL = "tcp:127.0.0.1:5760"


def conectar(dispositivo: str = CONEXION_RPI5, baudios: int = BAUDIOS_RPI5, espera_s: float = 10.0):
    """Abre la conexión y espera el primer HEARTBEAT del autopiloto."""
    from pymavlink import mavutil  # import perezoso: los tests de lógica no lo necesitan

    master = mavutil.mavlink_connection(dispositivo, baud=baudios, source_system=200, source_component=191)
    if master.wait_heartbeat(timeout=espera_s) is None:
        raise TimeoutError(f"sin HEARTBEAT de la controladora en {dispositivo} tras {espera_s:g} s")
    return master
