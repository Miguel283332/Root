"""Órdenes MAVLink hacia ArduPilot (lógica pura, sin dependencias)."""
from __future__ import annotations

from dataclasses import dataclass

MAV_CMD_DO_AUX_FUNCTION = 218     # mismo comando que usa la misión (ardupilot/missions)
AUX_FUNCTION_SEEDS = 300          # RC_Channel::AUX_FUNC::SCRIPTING_1 -> seed_dropper.lua
MAV_RESULT_ACCEPTED = 0

POSICIONES = {"baja": 0, "media": 1, "alta": 2}
SIGNIFICADO = {
    0: "baja: reposo / cancela el lote en curso",
    1: "media: suelta 1 bola (prueba)",
    2: "alta: suelta un lote completo (SEED_BATCH bolas)",
}


@dataclass(frozen=True)
class OrdenSuelta:
    posicion: int

    def __post_init__(self):
        if self.posicion not in SIGNIFICADO:
            raise ValueError(f"posición {self.posicion!r} no válida; usa 0 (baja), 1 (media) o 2 (alta)")

    @property
    def params(self) -> tuple[float, ...]:
        """param1..param7 de COMMAND_LONG."""
        return (float(AUX_FUNCTION_SEEDS), float(self.posicion), 0.0, 0.0, 0.0, 0.0, 0.0)


def enviar_orden(master, orden: OrdenSuelta) -> None:
    """Envía COMMAND_LONG DO_AUX_FUNCTION. `master` es un mavutil.mavlink_connection."""
    master.mav.command_long_send(
        master.target_system, master.target_component,
        MAV_CMD_DO_AUX_FUNCTION, 0, *orden.params,
    )


def es_mensaje_suelta(texto: str) -> bool:
    return texto.startswith("SeedDrop:")


def solicitar_suelta(master, posicion: int, espera_s: float = 3.0, reloj=None) -> list[str]:
    """Pide la suelta y devuelve los mensajes 'SeedDrop: ...' recibidos durante `espera_s`.

    El ACK solo confirma que ArduPilot recibió la orden; si el interlock la rechaza, el motivo
    llega por STATUSTEXT ("SeedDrop: bloqueado (...)"). Por eso se escucha el texto.
    """
    import time
    reloj = reloj or time.monotonic
    enviar_orden(master, OrdenSuelta(posicion))
    fin = reloj() + espera_s
    textos: list[str] = []
    while reloj() < fin:
        msg = master.recv_match(type=["STATUSTEXT", "COMMAND_ACK"], blocking=True, timeout=0.2)
        if msg is None:
            continue
        if msg.get_type() == "COMMAND_ACK" and msg.command == MAV_CMD_DO_AUX_FUNCTION:
            if msg.result != MAV_RESULT_ACCEPTED:
                textos.append(f"ArduPilot rechazó la orden (MAV_RESULT {msg.result})")
        elif msg.get_type() == "STATUSTEXT":
            t = msg.text if isinstance(msg.text, str) else msg.text.decode(errors="replace")
            if es_mensaje_suelta(t):
                textos.append(t)
    return textos
