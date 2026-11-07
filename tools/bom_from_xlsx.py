#!/usr/bin/env python3
"""Exporta la hoja 'Lista de compra' de hardware/bom/materiales_dron.xlsx a CSV.

El CSV (hardware/bom/materiales.csv) es la fuente que leen bom.py y los tests;
el .xlsx sigue siendo la hoja editable con fórmulas. Requiere openpyxl
(`pip install openpyxl`); solo hace falta cuando se edita el Excel.

Uso:  python3 tools/bom_from_xlsx.py [entrada.xlsx] [salida.csv]
"""
import csv
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
CAMPOS = ["n", "categoria", "material", "especificacion", "cantidad",
          "precio_unitario_eur", "enlace", "notas", "fase", "incluido"]


def main(argv):
    xlsx = Path(argv[1]) if len(argv) > 1 else ROOT / "hardware/bom/materiales_dron.xlsx"
    out = Path(argv[2]) if len(argv) > 2 else ROOT / "hardware/bom/materiales.csv"
    ws = openpyxl.load_workbook(xlsx)["Lista de compra"]
    filas = []
    for r in range(1, ws.max_row + 1):
        n = ws.cell(r, 1).value
        if not isinstance(n, int):          # solo las líneas numeradas
            continue
        v = [ws.cell(r, c).value for c in range(1, 12)]
        # columnas del Excel: Nº, Cat, Material, Espec, Cant, PU, Subtotal(fórmula),
        # Enlace, Notas, Fase, Incluido
        filas.append({
            "n": v[0], "categoria": v[1], "material": v[2], "especificacion": v[3],
            "cantidad": v[4], "precio_unitario_eur": v[5],
            "enlace": v[7], "notas": v[8], "fase": v[9],
            "incluido": "Sí" if v[10] == "Sí" else "No",
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} líneas -> {out}")


if __name__ == "__main__":
    main(sys.argv)
