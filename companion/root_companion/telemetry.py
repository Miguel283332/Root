"""Registro de telemetría en CSV a partir de mensajes MAVLink."""
from __future__ import annotations

import csv
import time
from dataclasses import dataclass, asdict, fields
from pathlib import Path

TIPOS = ["GLOBAL_POSITION_INT", "VFR_HUD", "SYS_STATUS", "HEARTBEAT", "STATUSTEXT"]
MAV_MODE_FLAG_SAFETY_ARMED = 128


@dataclass
class Estado:
    t: float = 0.0
    lat: float = float("nan")
    lon: float = float("nan")
    alt_rel_m: float = float("nan")
    vel_suelo_ms: float = float("nan")
    vel_aire_ms: float = float("nan")
    rumbo_deg: float = float("nan")
    gas_pct: float = float("nan")
    bateria_v: float = float("nan")
    bateria_pct: float = float("nan")
    armado: int = 0
    modo: str = ""


class Registro:
    """Acumula el último valor de cada mensaje; `fila()` devuelve una foto del estado."""

    def __init__(self):
        self.estado = Estado()
        self.textos: list[str] = []

    def actualiza(self, msg, modo: str | None = None) -> None:
        tipo = msg.get_type()
        e = self.estado
        if tipo == "GLOBAL_POSITION_INT":
            e.lat, e.lon = msg.lat / 1e7, msg.lon / 1e7
            e.alt_rel_m = msg.relative_alt / 1000.0
        elif tipo == "VFR_HUD":
            e.vel_suelo_ms, e.vel_aire_ms = msg.groundspeed, msg.airspeed
            e.rumbo_deg, e.gas_pct = msg.heading, msg.throttle
        elif tipo == "SYS_STATUS":
            # voltage_battery en mV (UINT16_MAX = desconocido); battery_remaining en % (-1 = desconocido)
            e.bateria_v = msg.voltage_battery / 1000.0 if msg.voltage_battery != 0xFFFF else float("nan")
            e.bateria_pct = msg.battery_remaining if msg.battery_remaining >= 0 else float("nan")
        elif tipo == "HEARTBEAT":
            e.armado = int(bool(msg.base_mode & MAV_MODE_FLAG_SAFETY_ARMED))
            if modo is not None:
                e.modo = modo
        elif tipo == "STATUSTEXT":
            t = msg.text if isinstance(msg.text, str) else msg.text.decode(errors="replace")
            self.textos.append(t)

    def fila(self, ahora: float | None = None) -> dict:
        self.estado.t = round(time.time() if ahora is None else ahora, 3)
        return asdict(self.estado)


CAMPOS = [f.name for f in fields(Estado)]


def registrar_csv(master, salida: Path, periodo_s: float = 1.0, duracion_s: float | None = None) -> int:
    """Escribe una fila por `periodo_s` hasta `duracion_s` (o hasta Ctrl+C). Devuelve nº de filas."""
    reg, filas, ultimo = Registro(), 0, 0.0
    inicio = time.monotonic()
    with Path(salida).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        try:
            while duracion_s is None or time.monotonic() - inicio < duracion_s:
                msg = master.recv_match(type=TIPOS, blocking=True, timeout=0.5)
                if msg is not None:
                    reg.actualiza(msg, modo=getattr(master, "flightmode", None))
                    if msg.get_type() == "STATUSTEXT":
                        print("[autopiloto]", reg.textos[-1])
                if time.monotonic() - ultimo >= periodo_s:
                    w.writerow(reg.fila())
                    f.flush()
                    filas += 1
                    ultimo = time.monotonic()
        except KeyboardInterrupt:
            pass
    return filas
