#!/usr/bin/env python3
"""Lista de materiales (BOM) del dron reforestador: totales, comprobaciones y Markdown.

Lee hardware/bom/materiales.csv (exportado de materiales_dron.xlsx).

    python3 tools/bom.py                       # resumen por categoría, fase y estado del precio
    python3 tools/bom.py --check               # comprueba coherencia; código de salida != 0 si falla
    python3 tools/bom.py --markdown            # tablas Markdown por categoría a stdout
    python3 tools/bom.py --update-docs docs/materiales.md     # reescribe el bloque BOM del doc
    python3 tools/bom.py --check-docs docs/materiales.md      # falla si el doc está desactualizado
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_DEFECTO = ROOT / "hardware/bom/materiales.csv"
PRESUPUESTO_EUR = 700.0
INICIO, FIN = "<!-- BOM:START (generado con tools/bom.py --update-docs) -->", "<!-- BOM:END -->"
YA_TIENES = ("motor BR4114 KV 400, hélice APC 18x5.5, emisora y transmisor, ESP32, "
             "PCA9685 y Raspberry Pi 5 16 GB")


@dataclass(frozen=True)
class Linea:
    n: int
    categoria: str
    material: str
    especificacion: str
    cantidad: float
    precio_unitario: float
    enlace: str
    notas: str
    fase: int
    incluido: bool

    @property
    def subtotal(self) -> float:
        return round(self.cantidad * self.precio_unitario, 2)

    @property
    def tiene_enlace(self) -> bool:
        return self.enlace.startswith("http")

    @property
    def es_estimacion(self) -> bool:
        """Precio sin verificar: sin enlace, o el propio Excel lo marca como estimación."""
        return (not self.tiene_enlace) or "estimaci" in self.notas.lower()


def cargar(ruta: Path = CSV_DEFECTO) -> list[Linea]:
    with Path(ruta).open(newline="", encoding="utf-8") as f:
        return [
            Linea(n=int(r["n"]), categoria=r["categoria"], material=r["material"],
                  especificacion=r["especificacion"], cantidad=float(r["cantidad"]),
                  precio_unitario=float(r["precio_unitario_eur"]), enlace=r["enlace"],
                  notas=r["notas"], fase=int(r["fase"]), incluido=r["incluido"] == "Sí")
            for r in csv.DictReader(f)
        ]


def total(lineas, **filtros) -> float:
    def ok(l):
        return all(getattr(l, k) == v for k, v in filtros.items())
    return round(sum(l.subtotal for l in lineas if l.incluido and ok(l)), 2)


def por_categoria(lineas) -> "OrderedDict[str, float]":
    cats: "OrderedDict[str, float]" = OrderedDict()
    for l in lineas:
        if l.incluido:
            cats[l.categoria] = round(cats.get(l.categoria, 0) + l.subtotal, 2)
    return cats


def por_fase(lineas) -> dict[int, float]:
    return {f: total(lineas, fase=f) for f in sorted({l.fase for l in lineas if l.incluido})}


def comprobar(lineas) -> list[str]:
    """Devuelve la lista de problemas encontrados (vacía = BOM coherente)."""
    err = []
    nums = [l.n for l in lineas]
    if nums != list(range(1, len(nums) + 1)):
        err.append("los números de línea no son 1..N consecutivos")
    for l in lineas:
        if l.cantidad <= 0 or l.precio_unitario <= 0:
            err.append(f"línea {l.n}: cantidad o precio no positivos")
        if l.fase not in (1, 2):
            err.append(f"línea {l.n}: fase {l.fase} no válida (1 o 2)")
        if l.enlace and not l.tiene_enlace and not l.enlace.startswith("(sin enlace"):
            err.append(f"línea {l.n}: enlace con formato inesperado: {l.enlace!r}")
    if total(lineas) <= 0:
        err.append("el total es cero")
    return err


def _eur(x: float) -> str:
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def markdown(lineas) -> str:
    out: list[str] = []
    t = total(lineas)
    est = round(sum(l.subtotal for l in lineas if l.incluido and l.es_estimacion), 2)
    out.append(f"**Total (líneas incluidas): {_eur(t)}** · presupuesto {_eur(PRESUPUESTO_EUR)} · "
               f"diferencia {_eur(PRESUPUESTO_EUR - t)} · "
               f"{_eur(est)} ({est / t:.0%}) son precios **sin verificar** (estimación o sin enlace).\n")
    cats = por_categoria(lineas)
    out.append("| Categoría | Subtotal |\n|---|---:|")
    out += [f"| {c} | {_eur(v)} |" for c, v in cats.items()]
    out.append(f"| **Total** | **{_eur(t)}** |\n")
    fases = por_fase(lineas)
    out.append("| Fase | Subtotal | Qué cubre |\n|---|---:|---|")
    out.append(f"| 1 — vuelo manual | {_eur(fases.get(1, 0))} | estructura, herramientas, propulsión, servos, BEC 6 V |")
    out.append(f"| 2 — autónomo | {_eur(fases.get(2, 0))} | controladora ArduPilot, GPS, pitot, cámara, BEC 5 V |\n")
    for cat in OrderedDict.fromkeys(l.categoria for l in lineas):
        out.append(f"#### {cat}\n")
        out.append("| Nº | Material | Especificación / uso | Cant. | P. unit. | Subtotal | Fase | Precio | Enlace |")
        out.append("|--:|---|---|--:|--:|--:|:-:|:-:|---|")
        for l in (x for x in lineas if x.categoria == cat):
            enlace = f"[enlace]({l.enlace})" if l.tiene_enlace else "—"
            precio = "estimado" if l.es_estimacion else "verificado"
            inc = "" if l.incluido else " *(opcional, fuera del total)*"
            out.append(f"| {l.n} | {l.material}{inc} | {l.especificacion} | {l.cantidad:g} | "
                       f"{_eur(l.precio_unitario)} | {_eur(l.subtotal)} | {l.fase} | {precio} | {enlace} |")
        out.append("")
    out.append(f"**Ya lo tienes (no incluido en el total):** {YA_TIENES}.  ")
    out.append("**No incluido:** envíos, IVA en tiendas fuera de la UE y aranceles de importación. "
               "(La nota del Excel original dice que tampoco incluye la batería de 10 Ah, pero la "
               "línea 20 sí la contabiliza: aquí se cuenta en el total. Ver "
               "[discrepancias](discrepancias-y-pendientes.md).)")
    return "\n".join(out)


def _bloque(doc: str, nuevo: str) -> str:
    i, j = doc.index(INICIO), doc.index(FIN)
    return doc[: i + len(INICIO)] + "\n\n" + nuevo + "\n\n" + doc[j:]


def resumen(lineas) -> str:
    t = total(lineas)
    s = [f"Líneas: {len(lineas)} ({sum(l.incluido for l in lineas)} incluidas en el total)"]
    s += [f"  {c:<13} {v:>9.2f} €" for c, v in por_categoria(lineas).items()]
    s.append(f"  {'TOTAL':<13} {t:>9.2f} €   (presupuesto {PRESUPUESTO_EUR:.0f} €, "
             f"diferencia {PRESUPUESTO_EUR - t:+.2f} €)")
    s += [f"  Fase {f}: {v:.2f} €" for f, v in por_fase(lineas).items()]
    est = [l for l in lineas if l.incluido and l.es_estimacion]
    s.append(f"  Líneas con precio sin verificar: {len(est)} de {sum(l.incluido for l in lineas)} "
             f"({sum(l.subtotal for l in est):.2f} €)")
    return "\n".join(s)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, default=CSV_DEFECTO)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--update-docs", type=Path, metavar="DOC")
    ap.add_argument("--check-docs", type=Path, metavar="DOC")
    a = ap.parse_args(argv)
    lineas = cargar(a.csv)

    if a.markdown:
        print(markdown(lineas))
    elif a.update_docs:
        doc = a.update_docs.read_text(encoding="utf-8")
        a.update_docs.write_text(_bloque(doc, markdown(lineas)), encoding="utf-8")
        print(f"actualizado {a.update_docs}")
    elif a.check_docs:
        doc = a.check_docs.read_text(encoding="utf-8")
        if _bloque(doc, markdown(lineas)) != doc:
            print(f"{a.check_docs} está desactualizado: ejecuta "
                  f"python3 tools/bom.py --update-docs {a.check_docs}", file=sys.stderr)
            return 1
        print(f"{a.check_docs} al día")
    elif a.check:
        err = comprobar(lineas)
        for e in err:
            print("ERROR:", e, file=sys.stderr)
        if not err:
            print(f"BOM coherente: {len(lineas)} líneas, total {total(lineas):.2f} €")
        return 1 if err else 0
    else:
        print(resumen(lineas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
