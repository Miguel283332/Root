# Descarga ArduPilot (con sus submódulos) en ROOT_ARDUPILOT_DIR al configurar.
# Si el directorio ya existe y es un repositorio Git, no se vuelve a descargar.
include_guard(GLOBAL)
include(ArduPilotVersion)

set(ROOT_ARDUPILOT_DIR "${CMAKE_SOURCE_DIR}/external/ardupilot" CACHE PATH
    "Dónde está (o se descargará) el código de ArduPilot")

if(ROOT_FETCH_ARDUPILOT AND NOT EXISTS "${ROOT_ARDUPILOT_DIR}/.git")
  find_package(Git REQUIRED)
  message(STATUS "Descargando ArduPilot ${ROOT_ARDUPILOT_TAG} en ${ROOT_ARDUPILOT_DIR}")
  message(STATUS "  (clon superficial + submódulos: unos cientos de MB; solo ocurre una vez)")
  include(FetchContent)
  FetchContent_Declare(ardupilot
    GIT_REPOSITORY   "${ROOT_ARDUPILOT_REPO}"
    GIT_TAG          "${ROOT_ARDUPILOT_TAG}"
    GIT_SHALLOW      TRUE
    GIT_PROGRESS     TRUE
    GIT_SUBMODULES_RECURSE TRUE
    SOURCE_DIR       "${ROOT_ARDUPILOT_DIR}"
    UPDATE_DISCONNECTED TRUE          # no tocar la red en reconfiguraciones
  )
  FetchContent_MakeAvailable(ardupilot)   # ArduPilot no tiene CMakeLists.txt: solo se descarga
endif()

if(NOT EXISTS "${ROOT_ARDUPILOT_DIR}/Tools/autotest/sim_vehicle.py")
  message(FATAL_ERROR
    "No encuentro ArduPilot en ${ROOT_ARDUPILOT_DIR}.\n"
    "  - Descargar automáticamente:  cmake -DROOT_FETCH_ARDUPILOT=ON ...\n"
    "  - Usar un clon propio:        cmake -DROOT_FETCH_ARDUPILOT=OFF -DROOT_ARDUPILOT_DIR=/ruta ...")
endif()

# Comprobar que es exactamente el commit esperado (solo si lo hemos descargado nosotros).
find_package(Git QUIET)
if(GIT_FOUND AND EXISTS "${ROOT_ARDUPILOT_DIR}/.git")
  execute_process(COMMAND "${GIT_EXECUTABLE}" -C "${ROOT_ARDUPILOT_DIR}" rev-parse HEAD
                  OUTPUT_VARIABLE _ap_head OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
  if(_ap_head AND NOT _ap_head STREQUAL ROOT_ARDUPILOT_COMMIT)
    # Si lo gestiona CMake, un commit distinto del fijado es un error (las etiquetas se pueden mover).
    # Si es un clon del usuario solo se avisa: puede estar trabajando con otra versión a propósito.
    if(ROOT_FETCH_ARDUPILOT)
      set(_sev FATAL_ERROR)
    else()
      set(_sev WARNING)
    endif()
    message(${_sev}
      "ArduPilot en ${ROOT_ARDUPILOT_DIR} está en ${_ap_head}, no en ${ROOT_ARDUPILOT_COMMIT} "
      "(${ROOT_ARDUPILOT_TAG}). Los parámetros de ardupilot/params están verificados contra la versión fijada.")
  else()
    message(STATUS "ArduPilot ${ROOT_ARDUPILOT_TAG} (${_ap_head}) verificado")
  endif()
endif()
set(ROOT_HAVE_ARDUPILOT TRUE)
