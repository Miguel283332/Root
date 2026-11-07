# Pruebas del proyecto (ctest). Todas funcionan sin descargar ArduPilot salvo las marcadas.
include_guard(GLOBAL)

# ---- Python: BOM, calculadoras, validador de parámetros, paquete companion -------------------
add_test(NAME python_unit
  COMMAND "${Python3_EXECUTABLE}" -m unittest discover -s tests/python -v
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_test(NAME bom_check COMMAND "${Python3_EXECUTABLE}" tools/bom.py --check
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_test(NAME bom_docs_al_dia COMMAND "${Python3_EXECUTABLE}" tools/bom.py --check-docs docs/materiales.md
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
file(GLOB ROOT_PARM_FILES "${CMAKE_SOURCE_DIR}/ardupilot/params/*.parm")
add_test(NAME params_formato COMMAND "${Python3_EXECUTABLE}" tools/check_params.py ${ROOT_PARM_FILES}
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")

# ---- Lua (necesita un intérprete Lua 5.4: `apt install lua5.4`) -------------------------------
find_program(LUA_EXE NAMES lua5.4 lua54 lua)
if(LUA_EXE)
  foreach(t IN ITEMS test_seed_logic test_seed_dropper_mock)
    add_test(NAME lua_${t} COMMAND "${LUA_EXE}" tests/lua/${t}.lua WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
  endforeach()
else()
  message(STATUS "Lua no encontrado: se omiten las pruebas lua_* (apt install lua5.4)")
endif()

# ---- C++: lógica de seguridad del ESP32 (y comprobación de que main.cpp compila) -------------
add_executable(test_root_safety tests/cpp/test_root_safety.cpp)
target_include_directories(test_root_safety PRIVATE firmware/esp32_fase1/lib/root_safety)
target_compile_features(test_root_safety PRIVATE cxx_std_17)
target_compile_options(test_root_safety PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME cpp_root_safety COMMAND test_root_safety)

# main.cpp contra stubs de Arduino: solo comprueba que compila (no sustituye a PlatformIO).
add_library(esp32_main_syntax OBJECT firmware/esp32_fase1/src/main.cpp tests/cpp/arduino_stub/stub_defs.cpp)
target_include_directories(esp32_main_syntax PRIVATE tests/cpp/arduino_stub firmware/esp32_fase1/lib/root_safety)
target_compile_definitions(esp32_main_syntax PRIVATE RC_SBUS)
target_compile_features(esp32_main_syntax PRIVATE cxx_std_17)
target_compile_options(esp32_main_syntax PRIVATE -Wall -Wextra)

# ---- Contra ArduPilot descargado ---------------------------------------------------------------
if(ROOT_HAVE_ARDUPILOT)
  # Los nombres y rangos de los parámetros deben existir en la versión fijada (4.7.2).
  add_test(NAME ardupilot_pdef COMMAND "${CMAKE_COMMAND}" --build "${CMAKE_BINARY_DIR}" --target ardupilot-pdef)
  add_test(NAME params_vs_ardupilot
    COMMAND "${Python3_EXECUTABLE}" tools/check_params.py --pdef "${PDEF}" ${ROOT_PARM_FILES}
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
  set_tests_properties(ardupilot_pdef PROPERTIES FIXTURES_SETUP pdef)
  set_tests_properties(params_vs_ardupilot PROPERTIES FIXTURES_REQUIRED pdef)
endif()

# ---- Simulador completo (lento: arranca SITL y vuela una misión) ---------------------------------
if(ROOT_SITL_TESTS AND ROOT_HAVE_ARDUPILOT)
  add_test(NAME sitl_seed_drop
    COMMAND "${CMAKE_COMMAND}" -DAP=${AP} -DVENV=${VENV} -DROOT=${CMAKE_SOURCE_DIR} -DWORK=${CMAKE_BINARY_DIR}/sitl-test
            -P "${CMAKE_SOURCE_DIR}/cmake/RunSitlTest.cmake")
  set_tests_properties(sitl_seed_drop PROPERTIES TIMEOUT 900 LABELS sitl)
endif()
