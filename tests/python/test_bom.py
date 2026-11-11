import unittest

import _ruta  # noqa: F401
import bom


class PruebasBOM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lineas = bom.cargar()

    def test_total_coincide_con_el_excel(self):
        # materiales_dron.xlsx (hoja 'Lista de compra', celda G37): 951,46 EUR
        self.assertEqual(bom.total(self.lineas), 951.46)

    def test_categorias_suman_el_total(self):
        self.assertAlmostEqual(sum(bom.por_categoria(self.lineas).values()), bom.total(self.lineas), places=2)

    def test_fases_suman_el_total(self):
        self.assertAlmostEqual(sum(bom.por_fase(self.lineas).values()), bom.total(self.lineas), places=2)

    def test_hailo_es_opcional_y_no_cuenta(self):
        hailo = [l for l in self.lineas if "Hailo" in l.material]
        self.assertEqual(len(hailo), 1)
        self.assertFalse(hailo[0].incluido)

    def test_supera_el_presupuesto_de_700(self):
        self.assertGreater(bom.total(self.lineas), bom.PRESUPUESTO_EUR)

    def test_bom_coherente(self):
        self.assertEqual(bom.comprobar(self.lineas), [])

    def test_estimaciones_se_detectan(self):
        sin_enlace = [l for l in self.lineas if not l.tiene_enlace]
        self.assertTrue(sin_enlace)
        self.assertTrue(all(l.es_estimacion for l in sin_enlace))
        # la línea 1 (Leroy Merlin, precio visible) es un precio verificado
        self.assertFalse(self.lineas[0].es_estimacion)

    def test_comprobar_detecta_errores(self):
        mala = [bom.Linea(1, "X", "m", "e", 0, 5.0, "http://x", "", 1, True)]
        self.assertTrue(any("no positivos" in e for e in bom.comprobar(mala)))
        mala = [bom.Linea(1, "X", "m", "e", 1, 5.0, "http://x", "", 3, True)]
        self.assertTrue(any("fase" in e for e in bom.comprobar(mala)))

    def test_documentacion_al_dia(self):
        doc = _ruta.RAIZ / "docs/materiales.md"
        self.assertEqual(bom.main(["--check-docs", str(doc)]), 0)


if __name__ == "__main__":
    unittest.main()
