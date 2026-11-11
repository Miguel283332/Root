// Pruebas de firmware/esp32_fase1/lib/root_safety/root_safety.h (sin framework: solo asserts).
#include <cstdio>
#include <cstring>

#include "root_safety.h"

using namespace root;

static int g_total = 0, g_fail = 0;
#define CHECK(cond)                                                      \
  do {                                                                   \
    g_total++;                                                           \
    if (!(cond)) {                                                       \
      g_fail++;                                                          \
      std::printf("FALLO %s:%d: %s\n", __FILE__, __LINE__, #cond);       \
    }                                                                    \
  } while (0)

static RcFrame frame(uint16_t ail, uint16_t ele, uint16_t thr, uint16_t rud, uint16_t arm, uint16_t drop = 1000) {
  RcFrame f;
  f.us[kAileron] = ail; f.us[kElevator] = ele; f.us[kThrottle] = thr; f.us[kRudder] = rud;
  f.us[kArmSwitch] = arm; f.us[kDropSwitch] = drop;
  return f;
}

// Arma el sistema siguiendo el procedimiento correcto; devuelve el tiempo actual.
static uint32_t arma(Safety& s, uint32_t t = 0) {
  RcFrame bajo = frame(1500, 1500, 1000, 1500, 1000);
  s.update(t, &bajo);
  RcFrame alto = frame(1500, 1500, 1000, 1500, 2000);
  s.update(t + 20, &alto);
  return t + 20;
}

int main() {
  // --- antes de recibir nada: failsafe, motor a cero
  { Safety s; Outputs o = s.update(0, nullptr);
    CHECK(o.failsafe && !o.armed && o.us[kEsc] == 1000); }

  // --- sin armado, el motor SIEMPRE a cero aunque el stick esté arriba
  { Safety s; RcFrame f = frame(1500, 1500, 2000, 1500, 1000);
    Outputs o = s.update(0, &f);
    CHECK(!o.failsafe && !o.armed && o.us[kEsc] == 1000); }

  // --- armado correcto y límite del 70 %
  { Safety s; uint32_t t = arma(s);
    RcFrame f = frame(1500, 1500, 2000, 1500, 2000);
    Outputs o = s.update(t + 20, &f);
    CHECK(o.armed && o.us[kEsc] == 1700);                       // 70 % de 1000..2000
    f = frame(1500, 1500, 1300, 1500, 2000);
    o = s.update(t + 40, &f);
    CHECK(o.us[kEsc] == 1300); }                                // por debajo del límite pasa tal cual

  // --- no se arma con el interruptor ya alto al arrancar (hay que verlo bajo antes)
  { Safety s; RcFrame f = frame(1500, 1500, 1000, 1500, 2000);
    Outputs o = s.update(0, &f);
    CHECK(!o.armed);
    f = frame(1500, 1500, 1000, 1500, 1000); s.update(20, &f);
    f = frame(1500, 1500, 1000, 1500, 2000); o = s.update(40, &f);
    CHECK(o.armed); }

  // --- no se arma con el gas arriba; se arma al bajarlo
  { Safety s; RcFrame f = frame(1500, 1500, 1000, 1500, 1000); s.update(0, &f);
    f = frame(1500, 1500, 1500, 1500, 2000); Outputs o = s.update(20, &f);
    CHECK(!o.armed && o.us[kEsc] == 1000);
    f = frame(1500, 1500, 1000, 1500, 2000); o = s.update(40, &f);
    CHECK(o.armed); }

  // --- failsafe: a los 500 ms exactos aún vale; a los 501 ms, motor a cero y neutro
  { Safety s; uint32_t t = arma(s);
    RcFrame f = frame(1800, 1200, 1600, 1700, 2000); Outputs o = s.update(t + 10, &f);
    CHECK(o.armed && o.us[kEsc] == 1600 && o.us[kAileronL] == 1800);
    o = s.update(t + 10 + 500, nullptr);
    CHECK(!o.failsafe && o.armed);
    o = s.update(t + 10 + 501, nullptr);
    CHECK(o.failsafe && !o.armed && o.us[kEsc] == 1000);
    CHECK(o.us[kAileronL] == 1500 && o.us[kAileronR] == 1500 && o.us[kElevatorOut] == 1500 && o.us[kRudderOut] == 1500);
    // al volver la señal NO se rearma solo: hay que bajar y subir el interruptor
    f = frame(1500, 1500, 1000, 1500, 2000);
    o = s.update(t + 700, &f);
    CHECK(!o.failsafe && !o.armed && o.us[kEsc] == 1000);
    f = frame(1500, 1500, 1000, 1500, 1000); s.update(t + 720, &f);
    f = frame(1500, 1500, 1000, 1500, 2000); o = s.update(t + 740, &f);
    CHECK(o.armed); }

  // --- failsafe declarado por el receptor (bit de SBUS) aunque lleguen tramas
  { Safety s; uint32_t t = arma(s);
    RcFrame f = frame(1500, 1500, 1500, 1500, 2000); f.failsafe_flag = true;
    Outputs o = s.update(t + 10, &f);
    CHECK(o.failsafe && o.us[kEsc] == 1000); }

  // --- desbordamiento del reloj de 32 bits (cada ~49 días)
  { Safety s; RcFrame f = frame(1500, 1500, 1000, 1500, 1000);
    uint32_t t0 = 0xFFFFFF00u; s.update(t0, &f);
    Outputs o = s.update(t0 + 400, nullptr);   // cruza el cero
    CHECK(!o.failsafe);
    o = s.update(t0 + 501, nullptr);
    CHECK(o.failsafe); }

  // --- alerones enfrentados y recorte a 1000..2000
  { Safety s; RcFrame f = frame(1800, 900, 1000, 2100, 1000);
    Outputs o = s.update(0, &f);
    CHECK(o.us[kAileronL] == 1800 && o.us[kAileronR] == 1200);
    CHECK(o.us[kElevatorOut] == 1000 && o.us[kRudderOut] == 2000); }

  // --- tambor con trinquete (servo normal): carrera de 160 us durante 300 ms y vuelta a reposo
  { Safety s; uint32_t t = arma(s);
    RcFrame f = frame(1500, 1500, 1000, 1500, 2000, 1000); Outputs o = s.update(t + 20, &f);
    CHECK(o.us[kDrum] == 1000);
    f = frame(1500, 1500, 1000, 1500, 2000, 2000); o = s.update(t + 40, &f);
    CHECK(o.us[kDrum] == 1160 && o.drum_index == 1);
    o = s.update(t + 40 + 299, &f); CHECK(o.us[kDrum] == 1160);
    o = s.update(t + 40 + 300, &f); CHECK(o.us[kDrum] == 1000);            // vuelve a reposo aunque el interruptor siga alto
    f = frame(1500, 1500, 1000, 1500, 2000, 1000); o = s.update(t + 400, &f); CHECK(o.us[kDrum] == 1000 && o.drum_index == 1); }

  // --- tambor indexado: un flanco = una celda; 6 celdas = vuelta completa; solo armado
  { SafetyConfig cfg; cfg.drum_ratchet = false; Safety s(cfg); uint32_t t = arma(s);
    RcFrame f = frame(1500, 1500, 1000, 1500, 2000, 1000); Outputs o = s.update(t + 20, &f);
    CHECK(o.us[kDrum] == 1000);
    for (int i = 1; i <= 6; i++) {
      f = frame(1500, 1500, 1000, 1500, 2000, 2000); o = s.update(t + 40 * i, &f);       // sube
      CHECK(o.drum_index == i % 6 && o.us[kDrum] == 1000 + (i % 6) * 160);
      f = frame(1500, 1500, 1000, 1500, 2000, 1000); s.update(t + 40 * i + 20, &f);      // baja
    }
    f = frame(1500, 1500, 1000, 1500, 2000, 2000);                                       // mantener alto
    o = s.update(t + 400, &f); uint8_t idx = o.drum_index;
    o = s.update(t + 420, &f);
    CHECK(o.drum_index == idx); }                                                        // no repite sin flanco
  { Safety s; RcFrame f = frame(1500, 1500, 1000, 1500, 1000, 2000);                    // desarmado
    s.update(0, &f); f = frame(1500, 1500, 1000, 1500, 1000, 1000); s.update(20, &f);
    f = frame(1500, 1500, 1000, 1500, 1000, 2000); Outputs o = s.update(40, &f);
    CHECK(o.drum_index == 0); }                                                          // desarmado no suelta
  { Safety s; RcFrame f = frame(1500, 1500, 1000, 1500, 1000, 2000);                    // armar con suelta alta
    s.update(0, &f); f = frame(1500, 1500, 1000, 1500, 2000, 2000);
    Outputs o = s.update(20, &f);
    CHECK(o.armed && o.drum_index == 0); }                                               // no cuenta como flanco

  // --- PCA9685: 1500 us a 50 Hz = 307 ticks de 4096
  CHECK(us_to_ticks(1500, 50) == 307);
  CHECK(us_to_ticks(1000, 50) == 204);
  CHECK(us_to_ticks(60000, 50) == 4095);   // saturación

  // --- SBUS: trama construida a mano
  { uint8_t b[25] = {0};
    b[0] = 0x0F;
    const uint16_t v[8] = {992, 172, 1811, 992, 172, 1811, 992, 992};   // 1500, 987, 2012, 1500...
    int bit = 0;
    for (int ch = 0; ch < 8; ch++)
      for (int k = 0; k < 11; k++, bit++)
        if (v[ch] >> k & 1) b[1 + bit / 8] |= (uint8_t)(1 << (bit % 8));
    RcFrame f;
    CHECK(sbus_decode(b, 25, f));
    CHECK(f.us[0] == 1500 && f.us[1] == 987 && f.us[2] == 2011 && f.us[5] == 2011);
    CHECK(!f.failsafe_flag);
    b[23] = 0x08; CHECK(sbus_decode(b, 25, f) && f.failsafe_flag);
    b[23] = 0x04; CHECK(sbus_decode(b, 25, f) && f.failsafe_flag);
    b[24] = 0x01; CHECK(!sbus_decode(b, 25, f));      // pie inválido
    b[24] = 0x00; b[0] = 0x00; CHECK(!sbus_decode(b, 25, f));   // cabecera inválida
    CHECK(!sbus_decode(b, 24, f)); }                   // trama corta

  std::printf("%d/%d comprobaciones correctas\n", g_total - g_fail, g_total);
  return g_fail == 0 ? 0 : 1;
}
