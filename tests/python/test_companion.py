import math
import unittest
from types import SimpleNamespace

import _ruta  # noqa: F401
from root_companion import commands, telemetry


class MensajeFalso:
    def __init__(self, tipo, **kw):
        self._t = tipo
        self.__dict__.update(kw)

    def get_type(self):
        return self._t


class MasterFalso:
    """Imita lo mínimo de mavutil.mavlink_connection."""
    def __init__(self, respuestas=()):
        self.target_system, self.target_component = 1, 1
        self.enviados = []
        self.respuestas = list(respuestas)
        self.mav = SimpleNamespace(command_long_send=lambda *a: self.enviados.append(a))

    def recv_match(self, type=None, blocking=True, timeout=None):
        return self.respuestas.pop(0) if self.respuestas else None


class PruebasComandos(unittest.TestCase):
    def test_orden_es_do_aux_function_300(self):
        m = MasterFalso()
        commands.enviar_orden(m, commands.OrdenSuelta(2))
        self.assertEqual(m.enviados, [(1, 1, 218, 0, 300.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0)])

    def test_posicion_invalida(self):
        with self.assertRaises(ValueError):
            commands.OrdenSuelta(3)
        self.assertEqual(commands.POSICIONES, {"baja": 0, "media": 1, "alta": 2})

    def test_solicitar_suelta_devuelve_los_textos_del_script(self):
        t = [0.0]

        def reloj():
            t[0] += 0.5
            return t[0]

        m = MasterFalso([
            MensajeFalso("STATUSTEXT", text="EKF3 lane switch 1"),
            MensajeFalso("STATUSTEXT", text="SeedDrop: bloqueado (en tierra)"),
            MensajeFalso("COMMAND_ACK", command=218, result=4),
        ])
        textos = commands.solicitar_suelta(m, 2, espera_s=3, reloj=reloj)
        self.assertEqual(textos[0], "SeedDrop: bloqueado (en tierra)")
        self.assertIn("rechazó", textos[1])
        self.assertEqual(len(m.enviados), 1)


class PruebasTelemetria(unittest.TestCase):
    def test_registro_convierte_unidades(self):
        r = telemetry.Registro()
        r.actualiza(MensajeFalso("GLOBAL_POSITION_INT", lat=-353632610, lon=1491652300, relative_alt=30500))
        r.actualiza(MensajeFalso("VFR_HUD", groundspeed=12.0, airspeed=12.5, heading=90, throttle=30))
        r.actualiza(MensajeFalso("SYS_STATUS", voltage_battery=24500, battery_remaining=87))
        r.actualiza(MensajeFalso("HEARTBEAT", base_mode=129), modo="AUTO")
        r.actualiza(MensajeFalso("STATUSTEXT", text="SeedDrop: lote de 10 bolas"))
        f = r.fila(ahora=100.0)
        self.assertAlmostEqual(f["lat"], -35.363261)
        self.assertAlmostEqual(f["alt_rel_m"], 30.5)
        self.assertEqual((f["bateria_v"], f["bateria_pct"], f["armado"], f["modo"]), (24.5, 87, 1, "AUTO"))
        self.assertEqual(r.textos, ["SeedDrop: lote de 10 bolas"])

    def test_bateria_desconocida_es_nan(self):
        r = telemetry.Registro()
        r.actualiza(MensajeFalso("SYS_STATUS", voltage_battery=0xFFFF, battery_remaining=-1))
        f = r.fila()
        self.assertTrue(math.isnan(f["bateria_v"]) and math.isnan(f["bateria_pct"]))


if __name__ == "__main__":
    unittest.main()
