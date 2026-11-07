# Arranca SITL, ejecuta tests/sitl/sitl_seed_drop.py y lo cierra. Lo invoca ctest (-DROOT_SITL_TESTS=ON).
# Parámetros: AP, VENV, ROOT, WORK
file(REMOVE_RECURSE "${WORK}")
file(MAKE_DIRECTORY "${WORK}")
set(ENV{PATH} "${VENV}/bin:$ENV{PATH}")
execute_process(COMMAND bash -c
  "nohup bash '${ROOT}/ardupilot/sitl/run_sitl.sh' '${AP}' '${WORK}' --no-mavproxy --speedup 6 > '${WORK}/sitl.log' 2>&1 & echo $! > '${WORK}/sitl.pid'")
execute_process(COMMAND "${VENV}/bin/python" "${ROOT}/tests/sitl/sitl_seed_drop.py" --timeout 400
                RESULT_VARIABLE rc)
execute_process(COMMAND bash -c "pkill -f '${AP}/build/sitl/bin/arduplane' ; pkill -f sim_vehicle.py ; true")
if(NOT rc EQUAL 0)
  message(FATAL_ERROR "La prueba SITL falló (ver ${WORK}/sitl.log)")
endif()
