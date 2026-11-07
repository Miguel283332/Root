"""Línea de órdenes:  python -m root_companion {estado,telemetria,soltar} [...]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import link
from .commands import POSICIONES, SIGNIFICADO, solicitar_suelta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="root-companion", description=__doc__)
    ap.add_argument("-c", "--conexion", default=link.CONEXION_RPI5,
                    help=f"dispositivo o URL MAVLink (por defecto {link.CONEXION_RPI5}; SITL: {link.CONEXION_SITL})")
    ap.add_argument("-b", "--baudios", type=int, default=link.BAUDIOS_RPI5)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("estado", help="muestra versión del autopiloto, modo y armado")
    t = sub.add_parser("telemetria", help="guarda telemetría en CSV")
    t.add_argument("-o", "--salida", type=Path, default=Path("telemetria.csv"))
    t.add_argument("-d", "--duracion", type=float, help="segundos (por defecto hasta Ctrl+C)")
    s = sub.add_parser("soltar", help="pide al autopiloto soltar semillas (él decide si es seguro)")
    s.add_argument("posicion", choices=sorted(POSICIONES, key=POSICIONES.get),
                   help="; ".join(f"{k}" for k in POSICIONES))
    a = ap.parse_args(argv)

    master = link.conectar(a.conexion, a.baudios)
    if a.cmd == "estado":
        print(f"autopiloto sistema {master.target_system}, modo {master.flightmode}")
        return 0
    if a.cmd == "telemetria":
        from .telemetry import registrar_csv
        n = registrar_csv(master, a.salida, duracion_s=a.duracion)
        print(f"{n} filas -> {a.salida}")
        return 0
    pos = POSICIONES[a.posicion]
    print("Petición:", SIGNIFICADO[pos])
    for texto in solicitar_suelta(master, pos) or ["(sin respuesta del script: ¿SCR_ENABLE=1 y seed_dropper.lua en la SD?)"]:
        print(" ", texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
