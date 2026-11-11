// root_safety.h — lógica de seguridad del vuelo manual (FASE 1): emisora -> ESP32 -> PCA9685.
//
// Es C++ puro (sin Arduino) para poder probarla en el PC: tests/cpp/test_root_safety.cpp.
// Requisitos del informe técnico, sección 4.1 / 9.6:
//   * Pérdida de señal > 0,5 s: gas a cero y superficies a neutro.
//   * Armado con un interruptor de la emisora; sin armado, el canal del motor SIEMPRE a cero.
//   * Límite de gas máximo en las primeras pruebas (por defecto 70 %).
// Añadido por seguridad (no está en el informe, pero sin ello el armado no es fiable):
//   * Tras el arranque o un failsafe hay que VER el interruptor en bajo antes de poder armar.
//   * Para armar, el gas debe estar en reposo (evita que el motor arranque de golpe).
#pragma once

#include <cstddef>
#include <cstdint>

namespace root {

constexpr int kNumInputs = 8;

// Entradas de la emisora, ya en microsegundos (1000..2000). Orden lógico (se mapea en main.cpp).
enum Input { kAileron = 0, kElevator = 1, kThrottle = 2, kRudder = 3, kArmSwitch = 4, kDropSwitch = 5 };
// Canales del PCA9685 (informe 4.4 y 9.6, punto 5).
enum Output { kAileronL = 0, kAileronR = 1, kElevatorOut = 2, kRudderOut = 3, kDrum = 4, kEsc = 5, kNumOutputs = 6 };

struct RcFrame {
  uint16_t us[kNumInputs] = {1500, 1500, 1000, 1500, 1000, 1000, 1500, 1500};
  bool failsafe_flag = false;  // el receptor declara pérdida de enlace (bit failsafe de SBUS)
};

struct SafetyConfig {
  uint32_t failsafe_ms = 500;       // informe 4.1
  uint16_t throttle_limit_pct = 70; // informe 4.1 (primeras pruebas)
  uint16_t arm_on_us = 1700;        // interruptor de armado "alto"
  uint16_t drop_on_us = 1700;       // interruptor de suelta "alto"
  uint16_t throttle_idle_us = 1050; // gas máximo admitido para poder armar
  uint16_t neutral_us = 1500;
  uint16_t esc_min_us = 1000;
  bool reverse_right_aileron = true;  // los dos servos de alerón van enfrentados
  uint8_t drum_cells = 6;           // informe 3.2
  uint16_t drum_rest_us = 1000;     // = SEED_PWM_REST del script de ArduPilot
  uint16_t drum_step_us = 160;      // = SEED_PWM_STEP
  bool drum_ratchet = true;         // = SEED_MODE 1: carrera de avance y vuelta (servo normal + trinquete)
  uint16_t drum_stroke_ms = 300;    // = SEED_STROKE
};

struct Outputs {
  uint16_t us[kNumOutputs] = {1500, 1500, 1500, 1500, 1000, 1000};
  bool armed = false;
  bool failsafe = true;
  uint8_t drum_index = 0;
};

class Safety {
 public:
  explicit Safety(const SafetyConfig& c = SafetyConfig()) : cfg_(c) {}

  // now_ms: reloj monótono. frame: trama nueva o nullptr si en este ciclo no llegó ninguna.
  Outputs update(uint32_t now_ms, const RcFrame* frame) {
    if (frame != nullptr) {
      last_ = *frame;
      last_ms_ = now_ms;
      have_frame_ = true;
    }
    Outputs o;
    o.drum_index = drum_idx_;
    o.us[kDrum] = drum_us(now_ms);

    const bool link_ok = have_frame_ && !last_.failsafe_flag && (uint32_t)(now_ms - last_ms_) <= cfg_.failsafe_ms;
    if (!link_ok) {                    // FAILSAFE: motor a cero, superficies a neutro
      armed_ = false;
      saw_disarm_ = false;
      o.failsafe = true;
      o.armed = false;
      for (int ch = kAileronL; ch <= kRudderOut; ch++) o.us[ch] = cfg_.neutral_us;  // alerones, profundidad, timón
      o.us[kEsc] = cfg_.esc_min_us;
      return o;
    }
    o.failsafe = false;

    const uint16_t* in = last_.us;
    const bool arm_high = in[kArmSwitch] >= cfg_.arm_on_us;
    if (!arm_high) {
      saw_disarm_ = true;
      armed_ = false;
    } else if (!armed_ && saw_disarm_ && in[kThrottle] <= cfg_.throttle_idle_us) {
      armed_ = true;
    }
    o.armed = armed_;

    // superficies: siguen a la emisora aunque no esté armado (así se prueban en tierra)
    o.us[kAileronL] = clamp_us(in[kAileron]);
    o.us[kAileronR] = cfg_.reverse_right_aileron ? clamp_us(3000 - in[kAileron]) : clamp_us(in[kAileron]);
    o.us[kElevatorOut] = clamp_us(in[kElevator]);
    o.us[kRudderOut] = clamp_us(in[kRudder]);

    // motor: sin armado, SIEMPRE al mínimo; armado, limitado a throttle_limit_pct
    if (!armed_) {
      o.us[kEsc] = cfg_.esc_min_us;
    } else {
      const int raw = (int)clamp_us(in[kThrottle]) - 1000;          // 0..1000
      const int max = (int)cfg_.throttle_limit_pct * 10;            // 0..1000
      o.us[kEsc] = (uint16_t)(1000 + (raw < max ? raw : max));
    }

    // tambor: un flanco de subida del interruptor = una celda = una bola (solo armado)
    const bool drop_high = in[kDropSwitch] >= cfg_.drop_on_us;
    if (armed_ && drop_high && !prev_drop_high_) {
      drum_idx_ = (uint8_t)((drum_idx_ + 1) % cfg_.drum_cells);
      stroke_until_ms_ = now_ms + cfg_.drum_stroke_ms;
    }
    prev_drop_high_ = drop_high;   // se actualiza siempre: armar con el interruptor alto no suelta
    o.drum_index = drum_idx_;
    o.us[kDrum] = drum_us(now_ms);
    return o;
  }

  const SafetyConfig& config() const { return cfg_; }

 private:
  static uint16_t clamp_us(int v) { return (uint16_t)(v < 1000 ? 1000 : (v > 2000 ? 2000 : v)); }
  // Modo trinquete: carrera de `step` us durante drum_stroke_ms y vuelta a reposo (el trinquete avanza el
  // tambor una celda en la carrera de ida). Modo indexado: el servo se coloca en la celda.
  uint16_t drum_us(uint32_t now_ms) const {
    if (cfg_.drum_ratchet) {
      const bool en_carrera = stroke_until_ms_ != 0 && (int32_t)(stroke_until_ms_ - now_ms) > 0;
      return (uint16_t)(cfg_.drum_rest_us + (en_carrera ? cfg_.drum_step_us : 0));
    }
    return (uint16_t)(cfg_.drum_rest_us + drum_idx_ * cfg_.drum_step_us);
  }

  SafetyConfig cfg_;
  RcFrame last_;
  uint32_t last_ms_ = 0;
  bool have_frame_ = false, armed_ = false, saw_disarm_ = false, prev_drop_high_ = false;
  uint8_t drum_idx_ = 0;
  uint32_t stroke_until_ms_ = 0;
};

// Conversión a "ticks" del PCA9685 (12 bits, periodo = 1/freq_hz).
inline uint16_t us_to_ticks(uint16_t us, uint16_t freq_hz = 50) {
  const uint32_t t = (uint32_t)((uint64_t)us * 4096ull * freq_hz / 1000000ull);
  return (uint16_t)(t > 4095 ? 4095 : t);
}

// Decodifica una trama SBUS de 25 bytes (0x0F ... 0x00) a microsegundos.
// SBUS: 11 bits por canal (172..1811), us = 0,625·v + 880. Flags (byte 23): bit 2 trama perdida,
// bit 3 failsafe del receptor. Devuelve false si la trama no es válida.
inline bool sbus_decode(const uint8_t* b, size_t len, RcFrame& out) {
  if (len < 25 || b[0] != 0x0F || b[24] != 0x00) return false;
  uint16_t ch[8];
  ch[0] = (uint16_t)((b[1] | b[2] << 8) & 0x07FF);
  ch[1] = (uint16_t)((b[2] >> 3 | b[3] << 5) & 0x07FF);
  ch[2] = (uint16_t)((b[3] >> 6 | b[4] << 2 | b[5] << 10) & 0x07FF);
  ch[3] = (uint16_t)((b[5] >> 1 | b[6] << 7) & 0x07FF);
  ch[4] = (uint16_t)((b[6] >> 4 | b[7] << 4) & 0x07FF);
  ch[5] = (uint16_t)((b[7] >> 7 | b[8] << 1 | b[9] << 9) & 0x07FF);
  ch[6] = (uint16_t)((b[9] >> 2 | b[10] << 6) & 0x07FF);
  ch[7] = (uint16_t)((b[10] >> 5 | b[11] << 3) & 0x07FF);
  for (int i = 0; i < 8; i++) out.us[i] = (uint16_t)(ch[i] * 5 / 8 + 880);
  out.failsafe_flag = (b[23] & 0x0C) != 0;   // trama perdida o failsafe
  return true;
}

}  // namespace root
