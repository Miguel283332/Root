#pragma once
#include <cstdint>
struct Adafruit_PWMServoDriver {
  explicit Adafruit_PWMServoDriver(uint8_t = 0x40) {}
  bool begin() { return true; }
  void setPWMFreq(float) {}
  uint8_t writeMicroseconds(uint8_t, uint16_t) { return 0; }
};
