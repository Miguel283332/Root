import math
import re
import unittest

import _ruta  # noqa: F401
import plantilla_perfil as pp


def naca4(m=0.02, p=0.4, t=0.12, n=60):
    """Perfil NACA de 4 cifras (2412 por defecto) en formato Selig: borde de salida -> ataque -> salida."""
    xs = [(1 - math.cos(math.pi * i / n)) / 2 for i in range(n + 1)]
    up, lo = [], []
    for x in xs:
        yt = 5 * t * (0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1036 * x ** 4)
        yc = m / p ** 2 * (2 * p * x - x * x) if x < p else m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x * x)
        dy = 2 * m / p ** 2 * (p - x) if x < p else 2 * m / (1 - p) ** 2 * (p - x)
        th = math.atan(dy)
        up.append((x - yt * math.sin(th), yc + yt * math.cos(th)))
        lo.append((x + yt * math.sin(th), yc - yt * math.cos(th)))
    pts = up[::-1] + lo[1:]
    return "NACA 2412\n" + "\n".join(f"{x:.6f} {y:.6f}" for x, y in pts)


class PruebasPlantilla(unittest.TestCase):
    def setUp(self):
        self.nombre, self.pts = pp.leer_selig(naca4())

    def test_lee_el_formato_selig(self):
        self.assertEqual(self.nombre, "NACA 2412")
        self.assertAlmostEqual(self.pts[0][0], 1.0, places=3)

    def test_espesor_y_hueco_del_larguero(self):
        g = pp.geometria(self.pts, 300.0)
        self.assertAlmostEqual(g["espesor_max_mm"], 36.0, delta=1.0)       # 12 % de 300 mm
        self.assertTrue(g["cabe_larguero"])                                  # 12 mm + 3 mm por cada lado
        self.assertAlmostEqual(g["centro_larguero_mm"][0], 75.0)              # 25 % de la cuerda

    def test_svg_esta_en_milimetros_a_escala_real(self):
        s = pp.svg(self.nombre, self.pts, 300.0)
        m = re.search(r'width="([\d.]+)mm"', s)
        self.assertAlmostEqual(float(m.group(1)), 330.0, delta=0.1)           # cuerda + márgenes
        xs = [float(a.split(",")[0]) for a in re.search(r'polygon points="([^"]+)"', s).group(1).split()]
        self.assertAlmostEqual(max(xs) - min(xs), 300.0, delta=0.1)          # la cuerda mide 300 mm
        self.assertIn('r="6"', s)                                             # círculo de 12 mm de diámetro
        self.assertIn('width="50" height="50"', s)                            # cuadrado de calibración

    def test_rechaza_formato_lednicer(self):
        with self.assertRaises(ValueError):
            pp.leer_selig("Clark Y\n 61. 61.\n" + "\n".join(f"{i * 0.0166 * 60:.3f} 0.0" for i in range(70)))


if __name__ == "__main__":
    unittest.main()
