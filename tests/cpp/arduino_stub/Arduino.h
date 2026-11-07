// Stub MÍNIMO de Arduino.h solo para comprobar en el PC que firmware/esp32_fase1/src/main.cpp
// compila (sintaxis y tipos). No ejecuta nada; no sustituye a compilar con PlatformIO.
#pragma once
#include <cstdint>
#include <cstddef>
#include <cstdio>
#define SERIAL_8E2 0x800001e
inline uint32_t millis() { return 0; }
inline void delay(uint32_t) {}
struct HardwareSerial {
  void begin(unsigned long, uint32_t = 0, int8_t = -1, int8_t = -1, bool = false) {}
  void println(const char*) {}
  int available() { return 0; }
  int read() { return -1; }
  template <typename... A> void printf(const char* f, A... a) { std::printf(f, a...); }
};
extern HardwareSerial Serial, Serial2;
void setup();
void loop();
