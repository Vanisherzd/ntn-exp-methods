/*
 * proposed_lr1121_tx_test_mode.c
 *
 * STATUS: NOT-YET-BUILDABLE REFERENCE SNIPPET (DESIGN-ONLY)
 * ---------------------------------------------------------------------------
 * This file is a STANDALONE reference for a deterministic, lowest-power,
 * conducted-only LR1121 TX test mode on a NUCLEO-L476RG (STM32L476RG).
 *
 * It WILL NOT COMPILE as-is. It depends on the Semtech LR11xx driver and an
 * STM32 HAL project that are NOT present in this repository. See
 * DETERMINISTIC_LR1121_TX_PLAN.md for the exact list of missing files/SDK and
 * the build/flash plan.
 *
 * SAFETY: Conducted-only. NO antenna. Inline attenuator >= 50 dB required.
 *         Lowest available LR1121 TX power. Do NOT build/flash/TX from this
 *         design step. A human operator must complete the pre-flash checklist.
 * ---------------------------------------------------------------------------
 *
 * Driver API basis (Semtech LR11xx driver, github Lora-net/lr11xx_driver):
 *   - lr11xx_radio_set_rf_freq()
 *   - lr11xx_radio_set_pa_cfg()
 *   - lr11xx_radio_set_tx_params()
 *   - lr11xx_radio_set_tx_cw()             (continuous wave - most deterministic)
 *   - lr11xx_radio_set_tx_infinite_preamble()  (alt deterministic carrier)
 *   - lr11xx_system_set_standby()          (used to STOP the CW carrier)
 */

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

/* ---- These headers come from the (currently MISSING) LR11xx driver ---- */
#include "lr11xx_radio.h"
#include "lr11xx_radio_types.h"
#include "lr11xx_system.h"
#include "lr11xx_system_types.h"
#include "lr11xx_hal.h"   /* user-provided HAL: SPI + NSS/BUSY/RESET/IRQ glue */

/* ---- STM32 HAL (currently MISSING project) ---- */
/* #include "main.h"  // CubeMX-generated; provides HAL_GetTick(), huart2, etc. */

/* ===========================================================================
 * Test-mode constants
 * ======================================================================== */
#define BOARD_ID_STR              "NUCLEO-L476RG_LR1121_BOARD_B"
#define FIRMWARE_VERSION_STR      "lr1121-txtest-0.1.0-DESIGN"

#define TEST_FREQ_HZ              923200000UL   /* 923.2 MHz target          */

/*
 * LOWEST available LR1121 TX power.
 *
 * The LR1121 has three PA paths selected by pa_sel in lr11xx_radio_pa_cfg_t:
 *   - LR11XX_RADIO_PA_SEL_LP : Low-Power PA   -> power range -17 .. +15 dBm
 *   - LR11XX_RADIO_PA_SEL_HP : High-Power PA  -> power range  -9 .. +22 dBm
 *   - LR11XX_RADIO_PA_SEL_HF : 2.4 GHz HF PA  -> not used in sub-GHz
 *
 * The lowest deterministic setting in the sub-GHz band is the Low-Power PA
 * with SetTxParams power = -17 dBm. That is what this test mode uses.
 */
#define TEST_TX_POWER_DBM         (-17)          /* lowest LP-PA setting      */

/* Sustained carrier window (30-60 s). 45 s chosen as midpoint. */
#define TEST_TX_DURATION_MS       45000U

/* RF path note printed to serial for the operator record. */
#define RF_PATH_NOTE_STR          "CONDUCTED ONLY: SMA -> >=50 dB inline atten -> SA/SDR. NO ANTENNA."

/* ===========================================================================
 * Low-Power PA configuration for LOWEST power, sub-GHz.
 *
 * pa_cfg fields (lr11xx_radio_pa_cfg_t):
 *   .pa_sel        = LR11XX_RADIO_PA_SEL_LP   // low-power PA path
 *   .pa_reg_supply = LR11XX_RADIO_PA_REG_SUPPLY_VREG  // LP PA fed from VREG
 *   .pa_duty_cycle = 0x00   // minimum duty cycle (Semtech LP optimal, low pwr)
 *   .pa_hp_sel     = 0x00   // HP-only field; ignored on LP path, set to 0
 *
 * These match Semtech's "LR11xx PA optimal settings" for the Low-Power PA at
 * the bottom of its range. Combined with SetTxParams power = -17 dBm this is
 * the lowest deterministic conducted output the part exposes.
 * ======================================================================== */
static const lr11xx_radio_pa_cfg_t k_pa_cfg_lowpower = {
    .pa_sel        = LR11XX_RADIO_PA_SEL_LP,
    .pa_reg_supply = LR11XX_RADIO_PA_REG_SUPPLY_VREG,
    .pa_duty_cycle = 0x00,
    .pa_hp_sel     = 0x00,
};

/* PA ramp time for the TX ramp-up. 48 us is a safe conservative default. */
#define TEST_TX_RAMP_TIME         LR11XX_RADIO_RAMP_48_US

/* ===========================================================================
 * Helper: serial status line printer.
 *
 * Assumes printf is retargeted to USART2 (NUCLEO-L476RG ST-LINK VCP, 115200).
 * If not retargeted, replace with HAL_UART_Transmit(&huart2, ...).
 * ======================================================================== */
static void print_status_header(void)
{
    printf("=== LR1121 TX TEST MODE (DESIGN REFERENCE) ===\r\n");
    printf("board_id=%s\r\n", BOARD_ID_STR);
    printf("firmware_version=%s\r\n", FIRMWARE_VERSION_STR);
    printf("configured_frequency_hz=%lu\r\n", (unsigned long)TEST_FREQ_HZ);
    printf("tx_power_dbm=%d\r\n", (int)TEST_TX_POWER_DBM);
    printf("tx_mode=CW_CONTINUOUS\r\n");
    printf("rf_path_note=%s\r\n", RF_PATH_NOTE_STR);
}

/* ===========================================================================
 * Primary test mode: 923.2 MHz, lowest-power, continuous-wave (CW).
 *
 * CW is the MOST DETERMINISTIC option for a TX-ON / TX-OFF spectrum check:
 * a single unmodulated carrier appears at exactly 923.200 MHz when ON and is
 * gone when OFF, with no packet timing / hopping / framing ambiguity.
 *
 * `radio` is the LR11xx driver context (SPI handle + GPIO descriptors), which
 * comes from the currently MISSING lr11xx_hal.c board glue.
 *
 * Returns 0 on success, non-zero on first driver error.
 * ======================================================================== */
int tx_cw_test_923_lowpower(const void *radio)
{
    lr11xx_status_t st;
    uint32_t t_start_ms, t_done_ms;

    print_status_header();

    /* 1) Put radio in a known STANDBY state (RC clock) before configuring. */
    st = lr11xx_system_set_standby((void *)radio, LR11XX_SYSTEM_STANDBY_CFG_RC);
    if (st != LR11XX_STATUS_OK) { printf("ERR set_standby=%d\r\n", (int)st); return 1; }

    /* 2) Program the RF frequency = 923.200 MHz. */
    st = lr11xx_radio_set_rf_freq((void *)radio, TEST_FREQ_HZ);
    if (st != LR11XX_STATUS_OK) { printf("ERR set_rf_freq=%d\r\n", (int)st); return 2; }

    /* 3) Select the Low-Power PA path (lowest available output). */
    st = lr11xx_radio_set_pa_cfg((void *)radio, &k_pa_cfg_lowpower);
    if (st != LR11XX_STATUS_OK) { printf("ERR set_pa_cfg=%d\r\n", (int)st); return 3; }

    /* 4) Set TX power to the lowest LP-PA setting (-17 dBm) + ramp. */
    st = lr11xx_radio_set_tx_params((void *)radio, TEST_TX_POWER_DBM, TEST_TX_RAMP_TIME);
    if (st != LR11XX_STATUS_OK) { printf("ERR set_tx_params=%d\r\n", (int)st); return 4; }

    /* 5) Start continuous wave. CW runs until we command STANDBY again. */
    t_start_ms = 0; /* = HAL_GetTick(); on real STM32 build */
    st = lr11xx_radio_set_tx_cw((void *)radio);
    if (st != LR11XX_STATUS_OK) { printf("ERR set_tx_cw=%d\r\n", (int)st); return 5; }
    printf("TX_START timestamp_ms=%lu\r\n", (unsigned long)t_start_ms);

    /* 6) Hold the carrier for the test window (30-60 s). */
    /* HAL_Delay(TEST_TX_DURATION_MS);  // real STM32 build */
    (void)TEST_TX_DURATION_MS;

    /* 7) Stop the carrier by returning to STANDBY. This is the TX_DONE point
     *    for a CW test (CW has no automatic TxDone IRQ). */
    st = lr11xx_system_set_standby((void *)radio, LR11XX_SYSTEM_STANDBY_CFG_RC);
    if (st != LR11XX_STATUS_OK) { printf("ERR stop_standby=%d\r\n", (int)st); return 6; }
    t_done_ms = t_start_ms + TEST_TX_DURATION_MS; /* = HAL_GetTick(); on real build */
    printf("TX_DONE timestamp_ms=%lu\r\n", (unsigned long)t_done_ms);

    printf("=== TX TEST COMPLETE ===\r\n");
    return 0;
}

/* ===========================================================================
 * ALTERNATIVE A: infinite-preamble carrier (also deterministic, slightly more
 * spectral spreading than pure CW). Same setup; swap the start call.
 *   st = lr11xx_radio_set_tx_infinite_preamble((void *)radio);
 * Stop the same way: lr11xx_system_set_standby(...).
 *
 * ALTERNATIVE B: packet loop. Configure LR-FHSS / LoRa modulation params with
 * lr11xx_radio_set_pkt_type() + lr11xx_radio_set_..._mod_params(), then loop
 * lr11xx_radio_set_tx() and wait on the TxDone IRQ for 30-60 s. More realistic
 * but LESS deterministic for an ON/OFF spectrum check (duty-cycled, framed,
 * harder to see a clean carrier). Prefer CW for first TX-ON/TX-OFF bring-up.
 * ======================================================================== */
