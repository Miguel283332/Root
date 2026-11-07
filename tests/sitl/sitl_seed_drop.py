#!/usr/bin/env python3
"""Prueba de extremo a extremo en SITL: despegue automático, suelta en misión y bloqueo del interlock.

Requisitos: SITL en marcha (ardupilot/sitl/run_sitl.sh o `cmake --build build -t ardupilot-sitl-run`)
escuchando en tcp:127.0.0.1:5760, y `pip install pymavlink`.

Comprueba:
  1. el script seed_dropper.lua está cargado (existe el parámetro SEED_ENABLE);
  2. en MANUAL y en tierra, pedir una suelta NO mueve el tambor y el script explica por qué;
  3. la misión ardupilot/missions/sitl_siembra.waypoints despega, suelta un lote de 10 bolas
     en el pasillo y el servo del tambor (SERVO6) se mueve exactamente 10 veces;
  4. el log de ArduPilot recibe mensajes "SeedDrop: ..." coherentes.

    python3 tests/sitl/sitl_seed_drop.py [--conexion tcp:127.0.0.1:5760] [--timeout 420]
Código de salida 0 = todo correcto.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from pymavlink import mavutil

RAIZ = Path(__file__).resolve().parents[2]
MISION = RAIZ / "ardupilot/missions/sitl_siembra.waypoints"
MAV_CMD_DO_AUX_FUNCTION = 218
SERVO_TAMBOR = 6          # SERVO6_FUNCTION=94 en root_plane_base.parm


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def lee_mision(ruta: Path):
    items = []
    for linea in ruta.read_text().splitlines()[1:]:
        c = linea.split("\t")
        seq, cur, frame, cmd = int(c[0]), int(c[1]), int(c[2]), int(c[3])
        p = [float(x) for x in c[4:8]]
        lat, lon, alt = float(c[8]), float(c[9]), float(c[10])
        items.append((seq, frame, cmd, p, int(lat * 1e7), int(lon * 1e7), alt))
    return items


def sube_mision(m, items):
    m.mav.mission_clear_all_send(m.target_system, m.target_component)
    m.recv_match(type="MISSION_ACK", blocking=True, timeout=5)
    m.mav.mission_count_send(m.target_system, m.target_component, len(items))
    fin = time.time() + 30
    while time.time() < fin:
        r = m.recv_match(type=["MISSION_REQUEST_INT", "MISSION_REQUEST", "MISSION_ACK"], blocking=True, timeout=5)
        if r is None:
            raise TimeoutError("la controladora no pide los elementos de la misión")
        if r.get_type() == "MISSION_ACK":          # la última petición se responde con el ACK
            if r.type != mavutil.mavlink.MAV_MISSION_ACCEPTED:
                raise RuntimeError(f"misión rechazada: {r}")
            return
        seq, frame, cmd, p, lat, lon, alt = items[r.seq]
        # el elemento 1 (despegue) es el "actual"; el 0 es la casa
        m.mav.mission_item_int_send(m.target_system, m.target_component, seq, frame, cmd, 1 if seq == 1 else 0, 1,
                                    p[0], p[1], p[2], p[3], lat, lon, alt)
    raise TimeoutError("la subida de la misión no terminó")


def parametro(m, nombre, espera=5):
    m.mav.param_request_read_send(m.target_system, m.target_component, nombre.encode(), -1)
    fin = time.time() + espera
    while time.time() < fin:
        r = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=0.5)
        if r is not None and r.param_id.rstrip("\x00") == nombre:   # puede llegar otro parámetro antes
            return r.param_value
    return None


_ultimo_rc = 0.0


def emisora(m, ch5=1500):
    """El simulador no tiene emisora: sin esto salta el failsafe de gas y el avión pasa a RTL.
    Gas en reposo (1000), mandos centrados, ch5 = interruptor de modo (1500 = FBWA)."""
    global _ultimo_rc
    if time.time() - _ultimo_rc >= 0.2:
        m.mav.rc_channels_override_send(m.target_system, m.target_component,
                                        1500, 1500, 1000, 1500, ch5, 1000, 1000, 1000)
        _ultimo_rc = time.time()


def pide_suelta(m, posicion):
    m.mav.command_long_send(m.target_system, m.target_component, MAV_CMD_DO_AUX_FUNCTION, 0,
                            300, posicion, 0, 0, 0, 0, 0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conexion", default="tcp:127.0.0.1:5760")
    ap.add_argument("--timeout", type=float, default=420, help="segundos máximos esperando la misión")
    a = ap.parse_args(argv)

    fallos: list[str] = []

    def comprueba(cond, texto):
        log(("OK    " if cond else "FALLO ") + texto)
        if not cond:
            fallos.append(texto)

    m = mavutil.mavlink_connection(a.conexion)
    m.wait_heartbeat(timeout=60)
    log("conectado, sistema", m.target_system)

    # 1) el script está cargado
    v = None
    for _ in range(30):
        v = parametro(m, "SEED_ENABLE")
        if v is not None:
            break
        time.sleep(1)
    comprueba(v == 1.0, f"el script seed_dropper.lua está cargado (SEED_ENABLE={v})")
    comprueba(parametro(m, "SEED_BATCH") == 10.0, "SEED_BATCH=10 por defecto")
    if v is None:
        return 1

    comprueba(parametro(m, "TERRAIN_FOLLOW") == 0.0, "sitl.parm se aplica después de la base (TERRAIN_FOLLOW=0)")

    # 2) en tierra y desarmado, pedir suelta no hace nada y se explica
    m.mav.request_data_stream_send(m.target_system, m.target_component, mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
    pide_suelta(m, 2)
    textos, t0 = [], time.time()
    while time.time() - t0 < 4:
        emisora(m)
        r = m.recv_match(type="STATUSTEXT", blocking=True, timeout=0.5)
        if r is not None:
            textos.append(r.text)
    comprueba(any("SeedDrop: bloqueado (en tierra)" in t for t in textos),
              f"en tierra la suelta se bloquea con motivo (mensajes: {[t for t in textos if 'Seed' in t]})")
    pide_suelta(m, 0)

    # 3) misión completa
    items = lee_mision(MISION)
    sube_mision(m, items)
    log(f"misión de {len(items)} elementos subida")

    # armar (reintenta mientras el EKF/GPS no estén listos)
    armado, t0, prearm = False, time.time(), set()
    while not armado and time.time() - t0 < 240:
        emisora(m)
        m.mav.command_long_send(m.target_system, m.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                                0, 1, 0, 0, 0, 0, 0, 0)
        ack = m.recv_match(type="COMMAND_ACK", blocking=True, timeout=3)
        armado = ack is not None and ack.command == 400 and ack.result == 0
        while (r := m.recv_match(type="STATUSTEXT", blocking=False)) is not None:
            if r.text.startswith(("PreArm", "Arm")) and r.text not in prearm:
                prearm.add(r.text)
                log("  [autopiloto]", r.text)
        if not armado:
            time.sleep(2)
    comprueba(armado, "armado")
    if not armado:
        return 1
    en_auto = False
    for _ in range(10):                      # el cambio de modo puede tardar un par de ciclos
        m.set_mode("AUTO")
        h = m.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
        if h is not None and m.flightmode == "AUTO":
            en_auto = True
            break
        emisora(m)
    comprueba(en_auto, f"modo AUTO activo (modo actual: {m.flightmode})")
    if not en_auto:
        return 1

    pulsos, ultimo_pwm, vio_inicio, vio_fin, textos, secuencia = 0, None, False, False, [], []
    maxalt, t0, t_fin = 0.0, time.time(), None
    while time.time() - t0 < a.timeout and (t_fin is None or time.time() - t_fin < 2.0):
        emisora(m)
        r = m.recv_match(type=["SERVO_OUTPUT_RAW", "STATUSTEXT", "GLOBAL_POSITION_INT"], blocking=True, timeout=1)
        if r is None:
            continue
        t = r.get_type()
        if t == "SERVO_OUTPUT_RAW":
            pwm = getattr(r, f"servo{SERVO_TAMBOR}_raw")
            if ultimo_pwm is not None and pwm != ultimo_pwm:
                pulsos += 1
                secuencia.append(pwm)
            ultimo_pwm = pwm
        elif t == "GLOBAL_POSITION_INT":
            maxalt = max(maxalt, r.relative_alt / 1000.0)
        else:
            textos.append(r.text)
            if "SeedDrop" in r.text:
                log("  [autopiloto]", r.text)
            vio_inicio |= "lote de 10 bolas" in r.text
            if "lote completo (10 bolas)" in r.text:
                vio_fin, t_fin = True, time.time()   # seguir leyendo 2 s: el último PWM llega después del texto
    comprueba(maxalt > 15, f"despega y supera la altura mínima de suelta (máx {maxalt:.0f} m)")
    comprueba(vio_inicio, "el script acepta el lote de 10 bolas en AUTO")
    comprueba(vio_fin, "el script informa 'lote completo (10 bolas)'")
    comprueba(pulsos == 10, f"el servo del tambor se mueve 10 veces ({pulsos}; PWM: {secuencia})")
    comprueba(not any("error interno" in t for t in textos), "ningún 'error interno' del script")

    log("RESULTADO:", "CORRECTO" if not fallos else f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
