# Uso: cmake -DMSG="texto" -P Fail.cmake   -> termina con error y muestra el mensaje.
message(FATAL_ERROR "${MSG}")
