#!/usr/bin/env python3
"""Calculadora de prestaciones del dron reforestador (reproduce las tablas del informe v3).

Los datos salen de hardware/design/parametros.json. Son modelos de primera aproximación
(±25 %): sirven para dimensionar y para detectar errores gordos, no para certificar nada.

    python3 tools/perf_calc.py            # todas las tablas
    python3 tools/perf_calc.py empuje     # 1.1  empuje estático vs. gas
    python3 tools/perf_calc.py crucero    # 1.2/1.3/1.5  pérdida, potencia, autonomía
    python3 tools/perf_calc.py masas      # 1.4/2.2  MTOW y centro de gravedad
    python3 tools/perf_calc.py suelta 30 12.5   # adelanto de suelta (altura m, velocidad m/s)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARAMS = ROOT / "hardware/design/parametros.json"
KMH = 3.6
IN = 0.0254


def cargar(ruta: Path = PARAMS) -> dict:
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- aerodinámica
def peso_n(masa_kg: float, g: float = 9.81) -> float:
    return masa_kg * g


def v_perdida(peso: float, s_m2: float, clmax: float, rho: float = 1.225) -> float:
    """Velocidad de pérdida [m/s]: V_s = sqrt(2W / (rho S CLmax))."""
    return math.sqrt(2 * peso / (rho * s_m2 * clmax))


def cl_vuelo(peso: float, s_m2: float, v: float, rho: float = 1.225) -> float:
    return 2 * peso / (rho * s_m2 * v * v)


def resistencia(peso, s_m2, v, cd0, ar, e, rho=1.225) -> float:
    """Resistencia [N] con polar parabólica CD = CD0 + CL²/(π e AR)."""
    cl = cl_vuelo(peso, s_m2, v, rho)
    cd = cd0 + cl * cl / (math.pi * e * ar)
    return 0.5 * rho * v * v * s_m2 * cd


def potencia_electrica(peso, s_m2, v, cd0, ar, e, eta_helice, eta_motor, rho=1.225) -> float:
    """Potencia eléctrica en crucero nivelado [W]."""
    return resistencia(peso, s_m2, v, cd0, ar, e, rho) * v / (eta_helice * eta_motor)


def autonomia_min(energia_wh: float, p_w: float) -> float:
    return energia_wh / p_w * 60


def alcance_km(v_kmh: float, autonomia_minutos: float) -> float:
    return v_kmh * autonomia_minutos / 60


# ---------------------------------------------------------------- propulsión
def empuje_estatico(p_el_w: float, diametro_m: float, eta=0.8, fm=0.7, rho=1.225) -> float:
    """Empuje estático [N] por teoría del disco: T^1,5 = P·η·FM·sqrt(2ρA)."""
    area = math.pi * (diametro_m / 2) ** 2
    return (p_el_w * eta * fm * math.sqrt(2 * rho * area)) ** (2 / 3)


def v_paso(kv: float, celdas: int, v_celda: float, paso_in: float) -> float:
    """Velocidad teórica de paso [m/s] sin carga: paso × rev/s."""
    return paso_in * IN * kv * celdas * v_celda / 60


def carrera_despegue(masa_kg, v_perdida_ms, empuje_n, mu=0.05, rho=1.225, k=1.2) -> float:
    """Carrera de despegue [m] con aceleración media constante hasta k·V_s."""
    v_lof = k * v_perdida_ms
    a = (empuje_n - mu * peso_n(masa_kg)) / masa_kg
    return v_lof * v_lof / (2 * a)


def adelanto_suelta(altura_m: float, v_ms: float, g: float = 9.81) -> tuple[float, float]:
    """(tiempo de caída [s], distancia recorrida hacia delante [m]) sin viento."""
    t = math.sqrt(2 * altura_m / g)
    return t, v_ms * t


# ---------------------------------------------------------------- masas y CG
def masas_y_cg(comp: list[dict], extra: dict | None = None) -> tuple[float, float]:
    items = list(comp) + ([extra] if extra else [])
    m = sum(c["masa"] for c in items)
    return m, sum(c["masa"] * c["x_m"] for c in items) / m


# ---------------------------------------------------------------- informes
def tabla_empuje(d: dict) -> str:
    p, g = d["propulsion"], d["atmosfera"]["g_m_s2"]
    diam = p["helice_diametro_in"] * IN
    w = peso_n(d["mision"]["masa_calculo_prestaciones_kg"], g)
    filas = [("30 %", 150), ("50 %", 400), ("75 %", 800), ("100 %", p["potencia_max_w"])]
    s = ["Acelerador | P eléctrica | Empuje estático | Empuje/peso (MTOW %.1f kg)" %
         d["mision"]["masa_calculo_prestaciones_kg"]]
    for nom, pw in filas:
        t = empuje_estatico(pw, diam, p["eficiencia_motor_esc"], p["figura_merito"], d["atmosfera"]["rho_kg_m3"])
        s.append(f"{nom:>10} | {pw:>6} W    | {t / g:5.2f} kg       | {t / w:4.2f}")
    s.append(f"Corriente al 100 %: {p['potencia_max_w'] / (p['celdas'] * p['v_nominal_celda']):.0f} A "
             f"(límite del motor {p['corriente_max_a']} A)")
    return "\n".join(s)


def tabla_crucero(d: dict) -> str:
    a, p, b, rho = d["ala"], d["propulsion"], d["bateria"], d["atmosfera"]["rho_kg_m3"]
    w = peso_n(d["mision"]["masa_calculo_prestaciones_kg"], d["atmosfera"]["g_m_s2"])
    vs = v_perdida(w, a["superficie_m2"], a["clmax"], rho)
    vs_f = v_perdida(w, a["superficie_m2"], a["clmax_con_flaps"], rho)
    e_wh = b["capacidad_ah"] * p["celdas"] * p["v_nominal_celda"] * b["energia_util_frac"]
    vp = v_paso(p["kv"], p["celdas"], p["v_nominal_celda"], p["helice_paso_in"])
    s = [f"Pérdida: {vs * KMH:.1f} km/h (CLmax {a['clmax']}), {vs_f * KMH:.1f} km/h con flaps "
         f"(CLmax {a['clmax_con_flaps']}) — el diseño actual no lleva flaps",
         f"Velocidad de paso de la hélice: {vp * KMH:.0f} km/h sin carga",
         f"Energía útil: {e_wh:.0f} Wh",
         "V crucero | V/Vs | CL    | P eléctrica | Autonomía | Alcance"]
    for vk in (40, 45, 50, 60):
        v = vk / KMH
        pw = potencia_electrica(w, a["superficie_m2"], v, a["cd0"], a["alargamiento"], a["e_oswald"],
                                p["eficiencia_helice"], p["eficiencia_motor_esc"], rho)
        mins = autonomia_min(e_wh, pw)
        s.append(f"{vk:>5} km/h | {v / vs:4.2f} | {cl_vuelo(w, a['superficie_m2'], v, rho):4.2f} | "
                 f"{pw:6.0f} W    | {mins:5.0f} min | {alcance_km(vk, mins):4.0f} km")
    t_est = empuje_estatico(p["potencia_max_w"], p["helice_diametro_in"] * IN, p["eficiencia_motor_esc"],
                            p["figura_merito"], rho)
    m = d["mision"]["mtow_diseno_kg"]
    s.append(f"Carrera de despegue (MTOW {m} kg, empuje medio 0,6·estático): "
             f"{carrera_despegue(m, vs, 0.6 * t_est):.0f} m")
    return "\n".join(s)


def tabla_masas(d: dict) -> str:
    comp, carga = d["masas_kg"]["componentes"], d["masas_kg"]["carga_util"]
    m0, x0 = masas_y_cg(comp)
    m1, x1 = masas_y_cg(comp, carga)
    cuerda = d["ala"]["cuerda_m"]
    lo, hi = d["masas_kg"]["objetivo_cg_frac_mac"]
    s = ["Componente                                   masa kg    x m    momento"]
    for c in comp:
        s.append(f"{c['nombre']:<44} {c['masa']:5.2f}  {c['x_m']:+6.2f}  {c['masa'] * c['x_m']:+7.3f}")
    s.append(f"Vacío:   {m0:5.2f} kg  CG = {x0 * 1000:+5.0f} mm  ({x0 / cuerda:5.1%} MAC)")
    s.append(f"Cargado: {m1:5.2f} kg  CG = {x1 * 1000:+5.0f} mm  ({x1 / cuerda:5.1%} MAC)")
    ok = lo <= x1 / cuerda <= hi
    s.append(f"Objetivo {lo:.0%}-{hi:.0%} MAC: {'OK' if ok else 'FUERA'}; "
             f"MTOW de diseño {d['mision']['mtow_diseno_kg']} kg, máximo {d['mision']['mtow_max_kg']} kg")
    return "\n".join(s)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    d = cargar()
    cmd = argv[0] if argv else "todo"
    if cmd == "suelta":
        h, v = float(argv[1]), float(argv[2])
        t, x = adelanto_suelta(h, v)
        print(f"Altura {h:g} m, velocidad {v:g} m/s ({v * KMH:.0f} km/h): caída {t:.2f} s, "
              f"adelanto {x:.1f} m (sin viento)")
        return 0
    tablas = {"empuje": tabla_empuje, "crucero": tabla_crucero, "masas": tabla_masas}
    if cmd == "todo":
        for n, f in tablas.items():
            print(f"=== {n} ===\n{f(d)}\n")
    elif cmd in tablas:
        print(tablas[cmd](d))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
