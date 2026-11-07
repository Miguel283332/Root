# Versión de ArduPilot fijada para este proyecto.
#
# Se usa Plane-4.7.2 (estable en noviembre de 2026; ArduPlane-stable apunta a este commit).
# El informe técnico pedía "ArduPlane 4.2.0 o posterior"; los nombres de parámetros de
# ardupilot/params/*.parm están verificados contra ESTA versión (ctest -R params_vs_ardupilot).
#
# Para cambiar de versión: edita las dos líneas, ejecuta `ctest` y corrige los parámetros
# que hayan cambiado de nombre. El commit se comprueba tras la descarga porque las etiquetas
# de Git se pueden mover.
set(ROOT_ARDUPILOT_TAG    "Plane-4.7.2"                              CACHE STRING "Etiqueta de ArduPilot")
set(ROOT_ARDUPILOT_COMMIT "fb773567896014da007bca58358704d4a0d8516f" CACHE STRING "Commit esperado de esa etiqueta")
set(ROOT_ARDUPILOT_REPO   "https://github.com/ArduPilot/ardupilot.git" CACHE STRING "Repositorio de ArduPilot")
# Placa de la controladora (la Matek H743-Wing V1/V2/V3 comparten la placa "MatekH743").
set(ROOT_ARDUPILOT_BOARD  "MatekH743" CACHE STRING "Placa ArduPilot para el firmware real")
