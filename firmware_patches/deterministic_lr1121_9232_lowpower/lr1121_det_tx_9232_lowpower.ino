/*
  lr1121_det_tx_9232_lowpower.ino
  --------------------------------
  Deterministic LR1121 conducted TX test mode for NUCLEO-L476RG + Semtech LR1121,
  using RadioLib. Derived from the recovered host-replay sketch
  (recovered_firmware_candidates/lr1121_host_replay.ino, git c0e5499^).

  PURPOSE
    Produce a deterministic, repeatable conducted TX at:
      frequency = 923 200 000 Hz  (Taiwan 923.2 MHz)
      TX power  = lowest available LR1121 setting (-17 dBm, Low-Power PA path)
    for a 30-60 s window of repeated LR-FHSS bursts, with fully instrumented
    serial output (board_id, firmware_name/version, configured_frequency_hz,
    tx_power_dbm, tx_mode, TX_START, TX_DONE), so a conducted IQ capture can be
    paired against an unambiguous TX-ON / TX-OFF window.

  WHY NOT CW
    The recovered sketch documents that true CW (transmitDirect()->setTxCw())
    returned OK but did NOT radiate on this exact board (USRP saw only noise
    floor). The known-good RF path is radio.transmit() (LR-FHSS packets). This
    sketch therefore uses repeated LR-FHSS bursts, NOT CW.

  SAFETY (conducted-only bring-up)
    - 50-ohm conducted path with >= 50 dB inline attenuation. NO antenna. NO OTA.
    - Lowest TX power (-17 dBm). Do not raise.
    - This firmware WILL key RF TX when run. Flash + run only after the operator
      checklist in README_build_flash.md is satisfied.

  FQBN:
    STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_L476RG,xserial=generic,usb=none,upload_method=MassStorage

  Pin mapping (known-good from recovered sketch; do NOT change):
    LR1121 Module(NSS=D7, IRQ=D5, RST=A0, BUSY=D3)
    RF switch DIO5/DIO6, MODE_TX => RFO_LP_LF (Low-Power PA)
*/

#include <RadioLib.h>

// ---------------------------------------------------------------------------
// Identity / config
// ---------------------------------------------------------------------------
static const char    BOARD_ID[]          = "NUCLEO-L476RG SN=066CFF3031454D3043073845";
static const char    FIRMWARE_NAME[]      = "lr1121_det_tx_9232_lowpower";
static const char    FIRMWARE_VERSION[]   = "0.1.0";

static const uint32_t TARGET_FREQ_HZ      = 923200000UL;  // Taiwan 923.2 MHz
static const int8_t   TARGET_TX_POWER_DBM = -17;          // LR1121 LP PA minimum
static const char     TX_MODE[]           = "LR_FHSS_BURST_LOOP";

// Deterministic TX window length (seconds). Requirement: 30-60 s.
static const uint32_t TX_WINDOW_S         = 45;

// Run the deterministic TX window automatically once at boot (1) or wait for a
// host 'S' start command (0). Default 1 = self-running deterministic bring-up.
#ifndef DET_SELFTEST_ON_BOOT
#define DET_SELFTEST_ON_BOOT 1
#endif

// ---------------------------------------------------------------------------
// Radio
// ---------------------------------------------------------------------------
LR1121 radio = new Module(D7, D5, A0, D3);

static const uint32_t rfswitch_dio_pins[] = {
  RADIOLIB_LR11X0_DIO5, RADIOLIB_LR11X0_DIO6,
  RADIOLIB_NC, RADIOLIB_NC, RADIOLIB_NC
};
static const Module::RfSwitchMode_t rfswitch_table[] = {
  { LR11x0::MODE_STBY,  { LOW,  LOW  } },
  { LR11x0::MODE_RX,    { HIGH, LOW  } },
  { LR11x0::MODE_TX,    { HIGH, HIGH } },  // RFO_LP_LF (Low-Power PA)
  { LR11x0::MODE_TX_HP, { LOW,  HIGH } },  // RFO_HP_LF
  { LR11x0::MODE_TX_HF, { LOW,  LOW  } },
  { LR11x0::MODE_GNSS,  { LOW,  LOW  } },
  { LR11x0::MODE_WIFI,  { LOW,  LOW  } },
  END_OF_MODE_TABLE,
};

// LR-FHSS params matched to the SWDM001 ping demo measured earlier.
static const uint8_t LRFHSS_BW   = RADIOLIB_LRXXXX_LR_FHSS_BW_1574_2; // 1574.2 kHz
static const uint8_t LRFHSS_CR   = RADIOLIB_LRXXXX_LR_FHSS_CR_5_6;    // 5/6
static const bool    NARROW_GRID = false;  // FCC grid 25391 Hz
static const float   TCXO_V      = 0.0f;   // no TCXO ref (matches known-good board)

static uint8_t payload[19] = {
  0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29,0x2a,
  0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19
};

static bool    radio_ready = false;
static int16_t init_code   = 0;

static float freq_mhz(uint32_t hz) { return (float)((double)hz / 1.0e6); }

static void print_banner() {
  Serial.print(F("BOARD_ID "));               Serial.println(BOARD_ID);
  Serial.print(F("FIRMWARE_NAME "));           Serial.println(FIRMWARE_NAME);
  Serial.print(F("FIRMWARE_VERSION "));        Serial.println(FIRMWARE_VERSION);
  Serial.print(F("CONFIGURED_FREQUENCY_HZ ")); Serial.println(TARGET_FREQ_HZ);
  Serial.print(F("TX_POWER_DBM "));            Serial.println(TARGET_TX_POWER_DBM);
  Serial.print(F("TX_MODE "));                 Serial.println(TX_MODE);
  Serial.print(F("TX_WINDOW_S "));             Serial.println(TX_WINDOW_S);
  Serial.println(F("WARNING conducted-only, no antenna, no OTA, attenuator >=50dB inline"));
}

// Bring the LR1121 up at the target frequency + lowest power.
static bool radio_bringup() {
  radio.setRfSwitchTable(rfswitch_dio_pins, rfswitch_table);
  init_code = radio.beginLRFHSS(freq_mhz(TARGET_FREQ_HZ), LRFHSS_BW, LRFHSS_CR,
                                NARROW_GRID, TARGET_TX_POWER_DBM, TCXO_V);
  radio.setRfSwitchTable(rfswitch_dio_pins, rfswitch_table);
  radio_ready = (init_code == RADIOLIB_ERR_NONE);
  Serial.print(F("INIT beginLRFHSS code ")); Serial.println(init_code);
  if (!radio_ready) {
    Serial.print(F("ERR radio_not_ready code ")); Serial.println(init_code);
  }
  return radio_ready;
}

// Deterministic TX window: repeated LR-FHSS bursts at 923.2 MHz / -17 dBm.
static void run_deterministic_tx_window() {
  if (!radio_ready && !radio_bringup()) return;

  uint32_t t_start = millis();
  Serial.print(F("TX_START ")); Serial.println(t_start);

  uint32_t burst = 0;
  uint32_t t_end = t_start + TX_WINDOW_S * 1000UL;
  while ((int32_t)(millis() - t_end) < 0) {
    int16_t tx = radio.transmit(payload, sizeof(payload));
    if (tx == RADIOLIB_ERR_NONE) {
      Serial.print(F("BURST "));   Serial.print(burst);
      Serial.print(F(" t="));      Serial.print(millis() - t_start);
      Serial.print(F(" freq_hz=")); Serial.print(TARGET_FREQ_HZ);
      Serial.print(F(" pwr_dbm=")); Serial.println(TARGET_TX_POWER_DBM);
      burst++;
    } else {
      Serial.print(F("ERR transmit code ")); Serial.println(tx);
      break;
    }
  }
  radio.standby();
  uint32_t t_done = millis();
  Serial.print(F("TX_DONE ")); Serial.print(t_done);
  Serial.print(F(" bursts=")); Serial.print(burst);
  Serial.print(F(" elapsed_ms=")); Serial.println(t_done - t_start);
}

void setup() {
  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && (millis() - t0) < 3000) { }

  print_banner();
  radio_bringup();
  Serial.println(F("DET_TX_READY"));

#if DET_SELFTEST_ON_BOOT
  // Deterministic conducted-TX window runs once automatically at boot.
  run_deterministic_tx_window();
  Serial.println(F("DET_TX_SELFTEST_COMPLETE"));
#endif
}

void loop() {
  // Host control: 'S' = run one deterministic TX window on demand.
  Serial.println(F("RDY"));
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;
  if (line.charAt(0) == 'S') {
    run_deterministic_tx_window();
  }
  // Any other input is ignored (no host-set frequency/power: locked to target).
}
