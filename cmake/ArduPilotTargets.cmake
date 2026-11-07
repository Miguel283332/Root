# Objetivos para compilar y simular ArduPilot. ArduPilot se construye con su propio sistema (waf),
# así que CMake solo lo descarga y lo orquesta: entorno Python, SITL, firmware de la placa.
include_guard(GLOBAL)

set(AP "${ROOT_ARDUPILOT_DIR}")
set(VENV "${CMAKE_BINARY_DIR}/venv")
set(VENV_PY "${VENV}/bin/python")
set(VENV_STAMP "${VENV}/.root-requirements")

cmake_host_system_information(RESULT _ncores QUERY NUMBER_OF_LOGICAL_CORES)
set(ROOT_JOBS "${_ncores}" CACHE STRING "Procesos paralelos para waf")

# waf debe ejecutarse con el Python del venv (empy==3.3.4 y compañía) y ese Python en el PATH.
set(AP_ENV "${CMAKE_COMMAND}" -E env "PATH=${VENV}/bin:$ENV{PATH}")

# ---- 1. entorno Python ----------------------------------------------------------------------
add_custom_command(
  OUTPUT "${VENV_STAMP}"
  COMMAND "${Python3_EXECUTABLE}" -m venv "${VENV}"
  COMMAND "${VENV_PY}" -m pip install --quiet --upgrade pip
  COMMAND "${VENV_PY}" -m pip install --quiet -r "${CMAKE_SOURCE_DIR}/tools/requirements-ardupilot.txt"
  COMMAND "${CMAKE_COMMAND}" -E touch "${VENV_STAMP}"
  DEPENDS "${CMAKE_SOURCE_DIR}/tools/requirements-ardupilot.txt"
  COMMENT "Creando el entorno Python de ArduPilot en ${VENV}"
  VERBATIM)
add_custom_target(ardupilot-venv DEPENDS "${VENV_STAMP}")

# ---- 2. metadata de parámetros (para validar los .parm contra esta versión) ----------------------
set(PDEF "${CMAKE_BINARY_DIR}/ardupilot/apm.pdef.xml")
add_custom_command(
  OUTPUT "${PDEF}"
  # Con el Python del venv: param_parse.py de ArduPilot necesita lxml, que el Python del sistema
  # (p. ej. el de los runners de GitHub) no suele traer.
  COMMAND "${VENV_PY}" "${CMAKE_SOURCE_DIR}/tools/check_params.py" --genera-pdef "${AP}" "${PDEF}"
  DEPENDS "${VENV_STAMP}"
  COMMENT "Generando la metadata de parámetros de ArduPlane ${ROOT_ARDUPILOT_TAG}"
  VERBATIM)
add_custom_target(ardupilot-pdef DEPENDS "${PDEF}")

# ---- 3. SITL (simulador) ------------------------------------------------------------------------
add_custom_target(ardupilot-sitl-build
  COMMAND ${AP_ENV} "${VENV_PY}" ./waf configure --board sitl
  COMMAND ${AP_ENV} "${VENV_PY}" ./waf plane -j "${ROOT_JOBS}"
  WORKING_DIRECTORY "${AP}"
  DEPENDS ardupilot-venv
  COMMENT "Compilando ArduPlane SITL (unos minutos la primera vez)"
  USES_TERMINAL VERBATIM)

set(ROOT_SITL_ARGS "--no-mavproxy" CACHE STRING
    "Argumentos extra de sim_vehicle.py (con MAVProxy instalado: vacío o --console --map)")
add_custom_target(ardupilot-sitl-run
  COMMAND ${AP_ENV} bash "${CMAKE_SOURCE_DIR}/ardupilot/sitl/run_sitl.sh" "${AP}" "${CMAKE_BINARY_DIR}/sitl" ${ROOT_SITL_ARGS}
  DEPENDS ardupilot-sitl-build
  COMMENT "Lanzando SITL con los parámetros y scripts de Root (Ctrl+C para salir)"
  USES_TERMINAL VERBATIM)

# ---- 4. firmware real para la controladora ----------------------------------------------------
find_program(ARM_GCC arm-none-eabi-gcc)
if(ARM_GCC)
  set(FW_OUT "${CMAKE_BINARY_DIR}/firmware")
  add_custom_target(ardupilot-firmware
    COMMAND ${AP_ENV} "${VENV_PY}" ./waf configure --board "${ROOT_ARDUPILOT_BOARD}"
    COMMAND ${AP_ENV} "${VENV_PY}" ./waf plane -j "${ROOT_JOBS}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${FW_OUT}"
    COMMAND "${CMAKE_COMMAND}" -E copy "${AP}/build/${ROOT_ARDUPILOT_BOARD}/bin/arduplane.apj" "${FW_OUT}/"
    COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${AP}/build/${ROOT_ARDUPILOT_BOARD}/bin/arduplane_with_bl.hex" "${FW_OUT}/"
    WORKING_DIRECTORY "${AP}"
    DEPENDS ardupilot-venv
    COMMENT "Compilando ArduPlane para ${ROOT_ARDUPILOT_BOARD} -> ${FW_OUT}"
    USES_TERMINAL VERBATIM)
else()
  add_custom_target(ardupilot-firmware
    COMMAND "${CMAKE_COMMAND}" "-DMSG=Falta arm-none-eabi-gcc. Instálalo con ${AP}/Tools/environment_install/install-prereqs-ubuntu.sh (ver docs/ardupilot.md) y vuelve a configurar CMake."
            -P "${CMAKE_SOURCE_DIR}/cmake/Fail.cmake"
    COMMENT "ardupilot-firmware necesita la cadena de herramientas ARM"
    VERBATIM)
endif()

# ---- 5. SD de la controladora: scripts Lua y parámetros listos para copiar ----------------------
set(SD "${CMAKE_BINARY_DIR}/sd-card")
add_custom_target(ardupilot-sd-card
  COMMAND "${CMAKE_COMMAND}" -E make_directory "${SD}/APM/scripts/modules" "${SD}/APM/terrain"
  COMMAND "${CMAKE_COMMAND}" -E copy "${CMAKE_SOURCE_DIR}/ardupilot/scripts/seed_dropper.lua" "${SD}/APM/scripts/"
  COMMAND "${CMAKE_COMMAND}" -E copy "${CMAKE_SOURCE_DIR}/ardupilot/scripts/modules/seed_logic.lua" "${SD}/APM/scripts/modules/"
  COMMAND "${CMAKE_COMMAND}" -E copy_directory "${CMAKE_SOURCE_DIR}/ardupilot/params" "${SD}/params"
  COMMAND "${CMAKE_COMMAND}" -E copy_directory "${CMAKE_SOURCE_DIR}/ardupilot/missions" "${SD}/missions"
  COMMENT "Preparando ${SD} (copiar APM/ a la tarjeta SD; añadir los .DAT de SRTM en APM/terrain)"
  VERBATIM)
