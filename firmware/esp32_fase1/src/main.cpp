// Fase 1 — vuelo manual: emisora -> ESP32 -> PCA9685 -> servos y ESC.
// Informe técnico 4.1 y 9.6. La lógica de seguridad está en lib/root_safety/root_safety.h
// (probada en el PC); este fichero solo conecta el hardware.
//
// ESTADO: compila contra stubs en el PC (ver tests/cpp) pero NO se ha probado en hardware.
// Primera prueba: SIN hélice, con la emisora apagada (el motor no debe girar, 9.6 punto 9).
//
// Protocolo de la emisora: el informe dice que el enlace propio puede ser propietario.
// Aquí hay SBUS (build_flags -DRC_SBUS en platformio.ini). Sin protocolo definido no llega
// ninguna trama y el sistema se queda en FAILSAFE (motor a cero): es el estado seguro.
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#include "root_safety.h"

namespace {
constexpr int kSdaPin = 21;        // confirmar en tu placa ESP32 (informe 9.6 punto 4)
constexpr int kSclPin = 22;
constexpr int kSbusRxPin = 16;     // UART2 RX
constexpr uint16_t kPwmFreqHz = 50;

// Canal SBUS (0 = canal 1) de cada entrada lógica: A, E, T, R, armado, suelta. AJUSTAR a tu emisora.
constexpr int kChannelMap[root::kNumInputs] = {0, 1, 2, 3, 4, 5, 6, 7};

Adafruit_PWMServoDriver pca(0x40);
root::Safety safety;
uint8_t sbus_buf[25];
size_t sbus_len = 0;

#ifdef RC_SBUS
// Lee bytes de UART2 y devuelve true cuando completa una trama SBUS válida.
bool read_rc(root::RcFrame& f) {
  bool got = false;
  while (Serial2.available()) {
    const uint8_t c = (uint8_t)Serial2.read();
    if (sbus_len == 0 && c != 0x0F) continue;   // sincroniza con el byte de cabecera
    sbus_buf[sbus_len++] = c;
    if (sbus_len == 25) {
      root::RcFrame raw;
      if (root::sbus_decode(sbus_buf, 25, raw)) {
        for (int i = 0; i < root::kNumInputs; i++) f.us[i] = raw.us[kChannelMap[i]];
        f.failsafe_flag = raw.failsafe_flag;
        got = true;
      }
      sbus_len = 0;
    }
  }
  return got;
}
#else
bool read_rc(root::RcFrame&) { return false; }   // sin protocolo: siempre failsafe
#endif
}  // namespace

void setup() {
  Serial.begin(115200);
  Wire.begin(kSdaPin, kSclPin);
  pca.begin();
  pca.setPWMFreq(kPwmFreqHz);
#ifdef RC_SBUS
  Serial2.begin(100000, SERIAL_8E2, kSbusRxPin, -1, /*invert=*/true);
#else
  Serial.println("AVISO: sin protocolo de emisora (define RC_SBUS). Quedará en FAILSAFE.");
#endif
}

void loop() {
  static uint32_t last_print = 0;
  root::RcFrame frame;
  const bool new_frame = read_rc(frame);
  const root::Outputs out = safety.update(millis(), new_frame ? &frame : nullptr);

  for (int ch = 0; ch < root::kNumOutputs; ch++) pca.writeMicroseconds(ch, out.us[ch]);

  if (millis() - last_print > 1000) {
    last_print = millis();
    Serial.printf("armado=%d failsafe=%d gas=%u us tambor=%u\n", out.armed, out.failsafe,
                  out.us[root::kEsc], out.drum_index);
  }
  delay(5);   // ~200 Hz; los servos analógicos van a 50 Hz
}
