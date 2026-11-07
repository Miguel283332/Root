#!/usr/bin/env python3
"""Valida ficheros .parm de ArduPilot.

Siempre comprueba el formato (NOMBRE,valor), valores numéricos y duplicados.
Con --pdef comprueba además que cada parámetro EXISTE en la metadata de la versión de
ArduPilot que se descarga (apm.pdef.xml); así un parámetro renombrado entre versiones
(p. ej. LAND_PITCH_CD -> LAND_PITCH_DEG) rompe el test en lugar de ignorarse en vuelo.

    python3 tools/check_params.py ardupilot/params/*.parm
    python3 tools/check_params.py --pdef build/ardupilot-pdef/apm.pdef.xml ardupilot/params/*.parm
    python3 tools/check_params.py --genera-pdef EXTERNAL/ardupilot SALIDA.xml   # crea la metadata
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

LINEA = re.compile(r"^([A-Z][A-Z0-9_]*)\s*[, \t=]\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)\s*$")


def leer(ruta: Path) -> tuple[dict[str, float], list[str]]:
    """Devuelve ({parámetro: valor}, [errores])."""
    vals: dict[str, float] = {}
    err: list[str] = []
    for i, bruto in enumerate(Path(ruta).read_text(encoding="utf-8").splitlines(), 1):
        l = bruto.strip()
        if not l or l.startswith("#"):
            continue
        m = LINEA.match(l)
        if not m:
            motivo = " (los comentarios van en línea propia: MAVProxy y Mission Planner rechazan los de final de línea)" if "#" in l else ""
            err.append(f"{ruta}:{i}: línea no válida: {bruto!r}{motivo}")
            continue
        nombre, valor = m.group(1), float(m.group(2))
        if nombre in vals:
            err.append(f"{ruta}:{i}: parámetro duplicado {nombre}")
        vals[nombre] = valor
    return vals, err


def nombres_pdef(xml: Path) -> set[str]:
    return {p.get("name").split(":")[-1] for p in ET.parse(xml).iter("param")}


def rangos_pdef(xml: Path) -> dict[str, tuple[float, float]]:
    out = {}
    for p in ET.parse(xml).iter("param"):
        for f in p.iter("field"):
            if f.get("name") == "Range" and f.text:
                try:
                    lo, hi = f.text.split()[:2]
                    out[p.get("name").split(":")[-1]] = (float(lo), float(hi))
                except ValueError:
                    pass
    return out


def genera_pdef(arbol_ardupilot: Path, salida: Path) -> None:
    """Ejecuta Tools/autotest/param_metadata/param_parse.py del árbol descargado."""
    pm = arbol_ardupilot / "Tools/autotest/param_metadata"
    subprocess.run([sys.executable, "param_parse.py", "--vehicle", "ArduPlane", "--format", "xml"],
                   cwd=pm, check=True, stdout=subprocess.DEVNULL)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_bytes((pm / "apm.pdef.xml").read_bytes())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ficheros", nargs="*", type=Path)
    ap.add_argument("--pdef", type=Path)
    ap.add_argument("--genera-pdef", nargs=2, metavar=("ARDUPILOT", "SALIDA"), type=Path)
    a = ap.parse_args(argv)
    if a.genera_pdef:
        genera_pdef(*a.genera_pdef)
        print(f"metadata -> {a.genera_pdef[1]}")
        return 0
    existentes = nombres_pdef(a.pdef) if a.pdef else None
    rangos = rangos_pdef(a.pdef) if a.pdef else {}
    n_err = 0
    for f in a.ficheros:
        vals, err = leer(f)
        for nombre, v in vals.items():
            if existentes is not None and nombre not in existentes:
                err.append(f"{f}: el parámetro {nombre} no existe en esta versión de ArduPilot")
            elif nombre in rangos and not (rangos[nombre][0] <= v <= rangos[nombre][1]):
                lo, hi = rangos[nombre]
                err.append(f"{f}: {nombre}={v:g} fuera del rango documentado [{lo:g}, {hi:g}]")
        for e in err:
            print("ERROR:", e, file=sys.stderr)
        n_err += len(err)
        print(f"{f}: {len(vals)} parámetros" + ("" if not err else f", {len(err)} errores"))
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
