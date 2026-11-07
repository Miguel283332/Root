#!/usr/bin/env bash
# Lanza ArduPlane SITL con la configuración y los scripts de Root.
#
#   run_sitl.sh <ardupilot_dir> <workdir> [opciones extra de sim_vehicle.py...]
#
# Lo invoca CMake (target ardupilot-sitl-run), pero se puede usar a mano. Requiere que
# ya esté compilado el SITL (./waf plane --board sitl) y que `python3` del PATH tenga las
# dependencias de ArduPilot (CMake crea un venv con ellas).
set -euo pipefail

AP="$(cd "${1:?falta <ardupilot_dir>}" && pwd)"
WORK="${2:?falta <workdir>}"
shift 2
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

mkdir -p "$WORK/scripts/modules"
cp "$ROOT/ardupilot/scripts/seed_dropper.lua" "$WORK/scripts/"
cp "$ROOT/ardupilot/scripts/modules/seed_logic.lua" "$WORK/scripts/modules/"

# base + ajustes de simulador en un solo fichero (las líneas posteriores ganan)
cat "$ROOT/ardupilot/params/root_plane_base.parm" "$ROOT/ardupilot/params/sitl.parm" > "$WORK/root_sitl.parm"

cd "$WORK"
# -w borra la EEPROM simulada para que los parámetros por defecto se apliquen;
# -L CMAC es la localización de pruebas habitual de ArduPilot.
exec python3 "$AP/Tools/autotest/sim_vehicle.py" \
  -v ArduPlane -f plane --no-rebuild -w -L CMAC \
  --add-param-file "$WORK/root_sitl.parm" \
  "$@"
