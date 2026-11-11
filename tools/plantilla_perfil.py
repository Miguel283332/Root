#!/usr/bin/env python3
"""Plantilla del perfil alar a escala 1:1 (SVG en milímetros) para cortar el ala con hilo caliente.

Lee un fichero de coordenadas en formato Selig (.dat de la base de datos del UIUC: primera línea =
nombre, después pares "x y" desde el borde de salida por el extradós hasta el borde de ataque y de
vuelta por el intradós; x e y entre 0 y 1) y dibuja el perfil con la cuerda indicada.

    python3 tools/plantilla_perfil.py clarky.dat --cuerda 300 -o plantilla_clarky.svg

El SVG lleva ancho y alto en mm: ábrelo en un navegador o en Inkscape e imprime al 100 % ("tamaño
real", sin "ajustar a página"). Con 300 mm de cuerda hace falta papel A3 o un plano en una copistería.
Comprueba SIEMPRE con una regla el cuadrado de calibración de 50 mm antes de cortar.
Incluye: línea de cuerda, marcas cada 10 % de cuerda, hueco del larguero (círculo de 12 mm a un 25 %
de la cuerda, centrado en el espesor del perfil) y el espesor máximo.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path


def leer_selig(texto: str) -> tuple[str, list[tuple[float, float]]]:
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]
    nombre, pts = lineas[0], []
    for l in lineas[1:]:
        partes = l.replace(",", " ").split()
        try:
            x, y = float(partes[0]), float(partes[1])
        except (ValueError, IndexError):
            continue
        pts.append((x, y))
    if len(pts) < 10:
        raise ValueError("el fichero no tiene suficientes puntos")
    if any(x > 1.5 for x, _ in pts):
        raise ValueError("parece formato Lednicer (cabecera con nº de puntos): descarga la versión Selig "
                         "o quita la línea de recuento y ordena de borde de salida a borde de salida")
    return nombre, pts


def _y_en(pts: list[tuple[float, float]], x0: float, superior: bool) -> float:
    """y interpolada del extradós/intradós en x0 (el borde de ataque separa ambas ramas)."""
    i_le = min(range(len(pts)), key=lambda i: pts[i][0])
    rama = pts[: i_le + 1][::-1] if superior else pts[i_le:]   # ambas de x creciente
    for (xa, ya), (xb, yb) in zip(rama, rama[1:]):
        if xa <= x0 <= xb and xb > xa:
            return ya + (yb - ya) * (x0 - xa) / (xb - xa)
    raise ValueError(f"x={x0} fuera del perfil")


def geometria(pts, cuerda_mm: float, larguero_mm: float = 12.0, pos_larguero: float = 0.25) -> dict:
    esp_max = max(_y_en(pts, x / 100, True) - _y_en(pts, x / 100, False) for x in range(1, 100))
    yu, yl = _y_en(pts, pos_larguero, True), _y_en(pts, pos_larguero, False)
    return {
        "espesor_max_mm": esp_max * cuerda_mm,
        "espesor_en_larguero_mm": (yu - yl) * cuerda_mm,
        "centro_larguero_mm": (pos_larguero * cuerda_mm, (yu + yl) / 2 * cuerda_mm),
        "cabe_larguero": (yu - yl) * cuerda_mm > larguero_mm + 6,  # >= 3 mm de foam por cada lado
    }


def svg(nombre, pts, cuerda_mm=300.0, larguero_mm=12.0, pos_larguero=0.25, margen=15.0) -> str:
    g = geometria(pts, cuerda_mm, larguero_mm, pos_larguero)
    ys = [y * cuerda_mm for _, y in pts]
    y_min, y_max = min(ys), max(ys)
    ancho = cuerda_mm + 2 * margen
    alto = (y_max - y_min) + 2 * margen + 70            # +70: cuadrado de calibración y texto debajo
    sx = lambda x: margen + x * cuerda_mm               # noqa: E731
    sy = lambda y: margen + (y_max - y * cuerda_mm)     # noqa: E731 (SVG: y crece hacia abajo)
    ruta = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in pts)
    cx, cy = g["centro_larguero_mm"]
    y_ejes = sy(0)
    marcas = "".join(
        f'<line x1="{sx(p / 10):.2f}" y1="{y_ejes - 3:.2f}" x2="{sx(p / 10):.2f}" y2="{y_ejes + 3:.2f}" stroke="#555" stroke-width="0.3"/>'
        f'<text x="{sx(p / 10):.2f}" y="{y_ejes + 8:.2f}" font-size="3" text-anchor="middle" fill="#555">{p * 10}%</text>'
        for p in range(0, 11))
    base = margen + (y_max - y_min) + 20
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{ancho:.1f}mm" height="{alto:.1f}mm" viewBox="0 0 {ancho:.1f} {alto:.1f}">
  <title>Plantilla {nombre} - cuerda {cuerda_mm:g} mm - escala 1:1</title>
  <polygon points="{ruta}" fill="none" stroke="#000" stroke-width="0.4"/>
  <line x1="{sx(0):.2f}" y1="{y_ejes:.2f}" x2="{sx(1):.2f}" y2="{y_ejes:.2f}" stroke="#999" stroke-width="0.2" stroke-dasharray="2,1"/>
  {marcas}
  <circle cx="{sx(pos_larguero):.2f}" cy="{sy(cy / cuerda_mm):.2f}" r="{larguero_mm / 2:g}" fill="none" stroke="#c00" stroke-width="0.4"/>
  <line x1="{sx(pos_larguero):.2f}" y1="{sy(cy / cuerda_mm) - 12:.2f}" x2="{sx(pos_larguero):.2f}" y2="{sy(cy / cuerda_mm) + 12:.2f}" stroke="#c00" stroke-width="0.2"/>
  <text x="{margen}" y="{base:.1f}" font-size="4">{nombre} - cuerda {cuerda_mm:g} mm - espesor maximo {g["espesor_max_mm"]:.1f} mm - hueco del larguero {larguero_mm:g} mm al {pos_larguero:.0%}</text>
  <text x="{margen}" y="{base + 6:.1f}" font-size="3.2">IMPRIMIR AL 100 %. Comprueba con regla: el cuadrado mide 50 x 50 mm y la cuerda {cuerda_mm:g} mm.</text>
  <rect x="{margen}" y="{base + 10:.1f}" width="50" height="50" fill="none" stroke="#00c" stroke-width="0.4"/>
</svg>
'''


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dat", type=Path, help="fichero de coordenadas Selig (.dat)")
    ap.add_argument("--cuerda", type=float, default=300.0, help="cuerda en mm (por defecto 300)")
    ap.add_argument("--larguero", type=float, default=12.0, help="diámetro del tubo del larguero en mm")
    ap.add_argument("--posicion", type=float, default=0.25, help="posición del larguero (fracción de cuerda)")
    ap.add_argument("-o", "--salida", type=Path, help="SVG de salida (por defecto <perfil>_plantilla.svg)")
    a = ap.parse_args(argv)
    nombre, pts = leer_selig(a.dat.read_text(encoding="utf-8", errors="replace"))
    g = geometria(pts, a.cuerda, a.larguero, a.posicion)
    salida = a.salida or a.dat.with_name(a.dat.stem + "_plantilla.svg")
    salida.write_text(svg(nombre, pts, a.cuerda, a.larguero, a.posicion), encoding="utf-8")
    print(f"{nombre}: espesor máximo {g['espesor_max_mm']:.1f} mm; en el larguero {g['espesor_en_larguero_mm']:.1f} mm "
          f"-> {'cabe el tubo de %g mm con foam a cada lado' % a.larguero if g['cabe_larguero'] else 'NO cabe el tubo con margen: revisa'}")
    print(f"plantilla -> {salida}  (imprime al 100 %)")
    return 0 if g["cabe_larguero"] else 1


if __name__ == "__main__":
    sys.exit(main())
