import tempfile
import unittest
from pathlib import Path

import _ruta  # noqa: F401
import check_params as cp

PARMS = sorted((_ruta.RAIZ / "ardupilot/params").glob("*.parm"))


def fichero(texto):
    d = tempfile.mkdtemp()
    p = Path(d) / "x.parm"
    p.write_text(texto, encoding="utf-8")
    return p


class PruebasParametros(unittest.TestCase):
    def test_los_parm_del_repositorio_son_validos(self):
        self.assertTrue(PARMS)
        for f in PARMS:
            _, err = cp.leer(f)
            self.assertEqual(err, [], f)

    def test_acepta_formatos_de_mission_planner_y_mavproxy(self):
        v, err = cp.leer(fichero("# comentario\nA_B,1.5\nC_D 2\nE_F=3\nG,-4e-1\n\n"))
        self.assertEqual(err, [])
        self.assertEqual(v, {"A_B": 1.5, "C_D": 2, "E_F": 3, "G": -0.4})

    def test_rechaza_comentarios_al_final_de_linea(self):
        _, err = cp.leer(fichero("AIRSPEED_MIN,12.5   # m/s\n"))
        self.assertEqual(len(err), 1)
        self.assertIn("comentarios", err[0])

    def test_rechaza_duplicados_y_basura(self):
        _, err = cp.leer(fichero("A,1\nA,2\nesto no es un parametro\nB,abc\n"))
        self.assertEqual(len(err), 3)

    def test_ningun_parm_activo_usa_nombres_obsoletos(self):
        # El informe 4.7 usa LAND_PITCH_CD; en ArduPilot 4.7.2 se llama LAND_PITCH_DEG.
        for f in PARMS:
            activas = [l for l in f.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("#")]
            self.assertFalse([l for l in activas if "LAND_PITCH_CD" in l], f)


if __name__ == "__main__":
    unittest.main()
