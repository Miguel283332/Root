"""Las calculadoras deben reproducir las tablas del informe técnico v3 (tolerancia: modelo ±25 %,
aquí exigimos acuerdo con las cifras redondeadas del informe, <= 5 %)."""
import math
import unittest

import _ruta  # noqa: F401
import perf_calc as pc

D = pc.cargar()
KMH = 3.6


def cerca(test, valor, esperado, tol=0.05):
    test.assertLessEqual(abs(valor - esperado) / esperado, tol, f"{valor} vs {esperado}")


class PruebasPrestaciones(unittest.TestCase):
    def setUp(self):
        self.w = pc.peso_n(D["mision"]["masa_calculo_prestaciones_kg"])
        self.a = D["ala"]
        self.p = D["propulsion"]

    def test_velocidad_de_perdida(self):          # informe 1.5: ~36 km/h y ~32 km/h con flaps
        cerca(self, pc.v_perdida(self.w, self.a["superficie_m2"], self.a["clmax"]) * KMH, 36)
        cerca(self, pc.v_perdida(self.w, self.a["superficie_m2"], self.a["clmax_con_flaps"]) * KMH, 32, 0.03)

    def test_cl_a_45_kmh(self):                   # informe 1.5: CL ~ 0,77
        cerca(self, pc.cl_vuelo(self.w, self.a["superficie_m2"], 45 / KMH), 0.77, 0.03)

    def test_potencia_y_autonomia(self):          # informe 1.3
        e_wh = D["bateria"]["capacidad_ah"] * 6 * 3.7 * D["bateria"]["energia_util_frac"]
        cerca(self, e_wh, 178, 0.01)
        for vk, p_inf, min_inf in ((45, 120, 89), (50, 140, 76), (60, 200, 54)):
            pw = pc.potencia_electrica(self.w, self.a["superficie_m2"], vk / KMH, self.a["cd0"],
                                       self.a["alargamiento"], self.a["e_oswald"],
                                       self.p["eficiencia_helice"], self.p["eficiencia_motor_esc"])
            cerca(self, pw, p_inf)
            cerca(self, pc.autonomia_min(e_wh, pw), min_inf)

    def test_empuje_estatico(self):               # informe 1.1
        diam = self.p["helice_diametro_in"] * pc.IN
        for pw, kg in ((150, 1.5), (400, 2.8), (800, 4.4), (1200, 5.8)):
            t = pc.empuje_estatico(pw, diam, self.p["eficiencia_motor_esc"], self.p["figura_merito"])
            cerca(self, t / 9.81, kg, 0.05)

    def test_velocidad_de_paso(self):             # informe 1.2: ~74 km/h
        cerca(self, pc.v_paso(400, 6, 3.7, 5.5) * KMH, 74, 0.02)

    def test_carrera_de_despegue(self):           # informe 1.5: 10-20 m
        vs = pc.v_perdida(pc.peso_n(7.1), self.a["superficie_m2"], self.a["clmax"])
        t_est = pc.empuje_estatico(1200, 18 * pc.IN, 0.8, 0.7)
        self.assertTrue(10 <= pc.carrera_despegue(7.1, vs, 0.6 * t_est) <= 20)

    def test_adelanto_de_suelta(self):            # informe 3.4: ~2,5 s y ~31 m a 30 m y 45 km/h
        t, x = pc.adelanto_suelta(30, 12.5)
        cerca(self, t, 2.5, 0.03)
        cerca(self, x, 31, 0.03)

    def test_masas_y_cg(self):                    # informe 2.2
        comp = D["masas_kg"]["componentes"]
        m0, x0 = pc.masas_y_cg(comp)
        self.assertAlmostEqual(m0, 4.62, places=2)
        self.assertAlmostEqual(x0, 0.080, places=3)
        m1, x1 = pc.masas_y_cg(comp, D["masas_kg"]["carga_util"])
        self.assertAlmostEqual(m1, 7.12, places=2)
        self.assertAlmostEqual(x1, 0.080, places=3)
        lo, hi = D["masas_kg"]["objetivo_cg_frac_mac"]
        self.assertTrue(lo <= x1 / D["ala"]["cuerda_m"] <= hi)
        self.assertLessEqual(m1, D["mision"]["mtow_max_kg"])

    def test_vaciar_la_tolva_no_mueve_el_cg(self):   # idea clave del informe 2.2
        comp = D["masas_kg"]["componentes"]
        _, x_vacio = pc.masas_y_cg(comp)
        _, x_lleno = pc.masas_y_cg(comp, D["masas_kg"]["carga_util"])
        self.assertAlmostEqual(x_vacio, x_lleno, places=3)

    def test_corriente_a_gas_pleno_supera_un_fusible_de_40_a(self):
        # Hallazgo documentado en docs/discrepancias-y-pendientes.md
        amperios = D["propulsion"]["potencia_max_w"] / (6 * 3.7)
        self.assertGreater(amperios, 40)
        self.assertTrue(math.isclose(amperios, 54, abs_tol=1))

    def test_dimensionado_electrico(self):
        v = self.p["celdas"] * self.p["v_nominal_celda"]
        i_max = pc.corriente_a(self.p["potencia_max_w"], v)
        # el ESC de 80 A deja >= 25 % de margen incluso con la batería en el umbral de failsafe (3,5 V/celda)
        i_baja = pc.corriente_a(self.p["potencia_max_w"], self.p["celdas"] * 3.5)
        self.assertGreaterEqual(self.p["esc_corriente_continua_a"] / i_baja, 1.25)
        # el fusible debe cubrir la corriente máxima con holgura y no superar la capacidad del ESC
        self.assertGreater(self.p["fusible_a"], 1.25 * i_max)
        self.assertLessEqual(self.p["fusible_a"], self.p["esc_corriente_continua_a"])
        # la batería debe poder entregarla con margen
        c_pedida = i_max / D["bateria"]["capacidad_ah"]
        self.assertGreaterEqual(D["bateria"]["tasa_c_continua_min"], 1.5 * c_pedida)
        # el peor caso queda por debajo del límite del motor
        self.assertLess(i_baja, self.p["corriente_max_a"])
        self.assertIn("brushless", self.p["motor_tipo"])
        self.assertIn("brushless", self.p["esc_tipo"])

    def test_bateria_de_la_ficha_adelanta_el_cg_y_se_corrige_moviendola(self):
        comp = [dict(c) for c in D["masas_kg"]["componentes"]]
        comp[0]["masa"] = D["bateria"]["masa_ficha_kg"]
        carga = D["masas_kg"]["carga_util"]
        m_v, x_v = pc.masas_y_cg(comp)
        m_c, x_c = pc.masas_y_cg(comp, carga)
        self.assertAlmostEqual(m_c, 7.22, places=2)
        self.assertLess(x_v / D["ala"]["cuerda_m"], D["masas_kg"]["objetivo_cg_frac_mac"][0])  # 24,8 % < 25 %
        self.assertLessEqual(m_c, D["mision"]["mtow_max_kg"])
        dx = pc.desplazamiento_para_cg(comp, carga, 0, 0.080)
        self.assertAlmostEqual(dx * 1000, 17, delta=1)
        comp[0]["x_m"] += dx
        _, x_nuevo = pc.masas_y_cg(comp, carga)
        self.assertAlmostEqual(x_nuevo, 0.080, places=4)

    def test_cola_convencional_dentro_de_rangos_habituales(self):
        c, a = D["cola"], D["ala"]
        cg = pc.masas_y_cg(D["masas_kg"]["componentes"], D["masas_kg"]["carga_util"])[1]
        lh = c["x_m"] - cg
        self.assertTrue(0.3 <= pc.coef_volumen_horizontal(c["horizontal_m2"], lh, a["superficie_m2"], a["cuerda_m"]) <= 0.6)
        self.assertTrue(0.02 <= pc.coef_volumen_vertical(c["vertical_m2"], lh, a["superficie_m2"], a["envergadura_m"]) <= 0.05)

    def test_cola_en_v_equivalente_no_ahorra_superficie(self):
        s_v, gamma = pc.cola_v_equivalente(0.19, 0.15)
        self.assertAlmostEqual(s_v, 0.34, places=6)
        self.assertAlmostEqual(gamma, 41.6, delta=0.3)
        # comprobación: la V reparte su área en horizontal efectiva y vertical efectiva
        g = math.radians(gamma)
        self.assertAlmostEqual(s_v * math.cos(g) ** 2, 0.19, places=3)
        self.assertAlmostEqual(s_v * math.sin(g) ** 2, 0.15, places=3)

    def test_incidencia_del_ala(self):
        a = D["ala"]
        cl = pc.cl_vuelo(pc.peso_n(6.9), a["superficie_m2"], 45 / KMH)
        self.assertAlmostEqual(pc.incidencia_necesaria_deg(cl, a["alpha0_deg"], a["alargamiento"]), 4.3, delta=0.4)
        self.assertAlmostEqual(pc.pendiente_cl_por_grado(10), 0.090, delta=0.005)

    def test_helice_pusher_golpea_el_suelo_con_la_holgura_del_informe(self):
        brazo = D["tren"]["x_helice_m"] - D["tren"]["x_principales_m"]
        self.assertAlmostEqual(pc.cabeceo_max_sin_golpe_deg(0.050, brazo), 3.7, delta=0.1)
        self.assertGreater(pc.holgura_necesaria_m(15, brazo), 0.2)
        # ida y vuelta
        h = pc.holgura_necesaria_m(6, brazo)
        self.assertAlmostEqual(pc.cabeceo_max_sin_golpe_deg(h, brazo), 6, places=6)

    def test_tablas_se_generan(self):
        for f in (pc.tabla_empuje, pc.tabla_crucero, pc.tabla_masas, pc.tabla_electrico, pc.tabla_diseno):
            self.assertIn("\n", f(D))


if __name__ == "__main__":
    unittest.main()
