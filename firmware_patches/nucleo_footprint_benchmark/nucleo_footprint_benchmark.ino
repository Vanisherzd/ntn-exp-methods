/*
  nucleo_footprint_benchmark.ino
  --------------------------------
  Compile-only PGRL endpoint footprint envelope for NUCLEO-L476RG.

  Purpose:
    - reserve the int8 model-storage envelope implied by exp9_pgrl_footprint;
    - compile a no-radio control/inference-shaped loop for STM32L476RG;
    - print accounting constants if the sketch is flashed in a later gated step.

  Safety boundary:
    - no RadioLib include;
    - no LR1121 initialization;
    - no transmit path;
    - no RF-control pins configured.

  FQBN:
    STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_L476RG,xserial=generic,usb=none,upload_method=MassStorage
*/

#include <Arduino.h>
#include <stdint.h>

static const uint32_t PGRL_PARAMS = 333720UL;
static const uint32_t PGRL_MACS = 332288UL;
static const uint32_t PGRL_FLASH_BYTES_INT8 = PGRL_PARAMS;
static const uint32_t PGRL_WORKING_RAM_BYTES = 768UL;
static const uint32_t N_RUNS = 32UL;

static const uint16_t LAYER_IN[] = {
  262, 256, 256, 256, 256, 256, 256
};
static const uint16_t LAYER_OUT[] = {
  256, 256, 256, 256, 256, 6, 6
};

__attribute__((used, aligned(16), section(".rodata.pgrl_weights")))
static const int8_t pgrl_int8_weight_store[PGRL_FLASH_BYTES_INT8] = {1};

__attribute__((used))
static int8_t activation_a[256];
__attribute__((used))
static int8_t activation_b[256];
__attribute__((used))
static int8_t scratch_io[256];

static volatile int32_t result_sink = 0;

static void seed_inputs() {
  for (uint16_t i = 0; i < 256; ++i) {
    activation_a[i] = (int8_t)((i * 17 + 3) & 0x7f);
    activation_b[i] = 0;
    scratch_io[i] = (int8_t)((i * 5 + 11) & 0x7f);
  }
}

__attribute__((noinline))
static int32_t pgrl_envelope_forward_once() {
  int32_t acc = 0;
  uint32_t w = 0;

  for (uint8_t layer = 0; layer < 7; ++layer) {
    const uint16_t in_dim = LAYER_IN[layer];
    const uint16_t out_dim = LAYER_OUT[layer];
    for (uint16_t o = 0; o < out_dim; ++o) {
      int32_t sum = 0;
      for (uint16_t i = 0; i < in_dim; ++i) {
        const int8_t x = activation_a[i & 0xff];
        const int8_t k = pgrl_int8_weight_store[w % PGRL_FLASH_BYTES_INT8];
        sum += (int16_t)x * (int16_t)k;
        ++w;
      }
      activation_b[o & 0xff] = (int8_t)(sum >> 8);
      acc += sum;
    }
    for (uint16_t i = 0; i < 256; ++i) {
      activation_a[i] = activation_b[i];
    }
  }

  return acc;
}

static void print_accounting(uint32_t elapsed_us) {
  const float latency_ms = ((float)elapsed_us) / (1000.0f * (float)N_RUNS);
  Serial.print(F("PARAMS "));
  Serial.println(PGRL_PARAMS);
  Serial.print(F("MACS "));
  Serial.println(PGRL_MACS);
  Serial.print(F("FLASH_BYTES "));
  Serial.println(PGRL_FLASH_BYTES_INT8);
  Serial.print(F("RAM_BYTES "));
  Serial.println(PGRL_WORKING_RAM_BYTES);
  Serial.print(F("LATENCY_MS "));
  Serial.println(latency_ms, 6);
  Serial.print(F("N_RUNS "));
  Serial.println(N_RUNS);
}

void setup() {
  Serial.begin(115200);
  const uint32_t wait_start = millis();
  while (!Serial && (millis() - wait_start) < 3000UL) { }

  seed_inputs();
  const uint32_t t0 = micros();
  int32_t local = 0;
  for (uint32_t run = 0; run < N_RUNS; ++run) {
    local += pgrl_envelope_forward_once();
  }
  const uint32_t elapsed_us = micros() - t0;
  result_sink = local;

  print_accounting(elapsed_us);
}

void loop() {
  delay(1000);
}
