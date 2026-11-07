cmake_minimum_required(VERSION 3.24)
project(Root
  VERSION 0.1.0
  DESCRIPTION "Dron reforestador de ala fija (inspiración MQ-9) con ArduPilot"
  LANGUAGES CXX)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

option(ROOT_FETCH_ARDUPILOT "Descargar ArduPilot (con submódulos) al configurar" ON)
option(ROOT_SITL_TESTS      "Registrar la prueba lenta de extremo a extremo en SITL" OFF)

find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)

enable_testing()

# Con ROOT_FETCH_ARDUPILOT=OFF y sin ROOT_ARDUPILOT_DIR solo se construyen/prueban las partes
# propias del proyecto (rápido, sin red): cmake --preset dev
if(ROOT_FETCH_ARDUPILOT OR DEFINED ROOT_ARDUPILOT_DIR)
  include(FetchArduPilot)
  include(ArduPilotTargets)
else()
  set(ROOT_HAVE_ARDUPILOT FALSE)
  message(STATUS "Sin ArduPilot: solo pruebas propias. Para descargarlo: cmake --preset ardupilot")
endif()

include(RootTests)

# ---- Documentación ---------------------------------------------------------------------------
add_custom_target(docs-bom
  COMMAND "${Python3_EXECUTABLE}" tools/bom.py --update-docs docs/materiales.md
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
  COMMENT "Regenerando las tablas de docs/materiales.md desde hardware/bom/materiales.csv")
add_custom_target(design-report
  COMMAND "${Python3_EXECUTABLE}" tools/perf_calc.py
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
  COMMENT "Tablas de prestaciones (empuje, crucero, masas y CG)")
