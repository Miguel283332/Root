"""Ordenador compañero del dron reforestador Root (Raspberry Pi 5 + ArduPilot por MAVLink).

Reparto de responsabilidades (informe técnico, sección 4.3):
  * ArduPilot (Matek H743) estabiliza el avión, sigue la misión y decide si es SEGURO soltar.
  * La Raspberry Pi 5 observa (cámara, visión), registra telemetría y PIDE soltar.
La Raspberry nunca mueve el servo del tambor directamente.
"""

__version__ = "0.1.0"
