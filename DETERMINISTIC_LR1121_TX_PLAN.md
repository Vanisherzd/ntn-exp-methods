# Deterministic LR1121 TX Test-Mode Plan (DESIGN-ONLY)

**Agent 4 deliverable. This is a design + plan only.**

- Target: LR1121 transceiver on NUCLEO-L476RG (STM32L476RG, Cortex-M4).
- Goal: a deterministic, lowest-power, conducted-only TX test mode at
  **923.200 MHz** for a clean TX-ON / TX-OFF spectrum check.
- Safety: **NO flashing, NO erase, NO RF TX, NO serial port access in this
  step.** Agent 2 owns the serial port. A human operator must complete the
  pre-flash checklist before anything is built or flashed.

Companion file (reference C, NOT-YET-BUILDABLE):
[hardware_conducted_iq/board_inventory/proposed_lr1121_tx_test_mode.c](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/proposed_lr1121_tx_test_mode.c)

---

## 0. Repo-state premise (confirmed)

This repo contains **no firmware source tree** for the board: no `.ioc`,
no LR1121 `.c/.h` driver, no `Makefile`/`CMakeLists.txt`/`platformio.ini`, no
`.bin/.elf/.hex`. The only board-relevant artifact is
[semtech_validation/lr1121_tx_config_example.json](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/semtech_validation/lr1121_tx_config_example.json)
(`center_frequency_hz=923200000`, `tx_power_dbm=0`). Board B currently
self-reports `868000000 Hz` / `10 dBm` over serial — **wrong** for our goal.
Therefore this plan is standalone and must pull in an external SDK.

---

## 1. Correct SDK / driver to base this on

**Primary driver (use this): Semtech LR11xx radio driver**
- Upstream repo: `https://github.com/Lora-net/lr11xx_driver`
- This is the canonical register-level driver and exposes exactly the calls we
  need:
  - `lr11xx_radio_set_rf_freq()`        — set 923.2 MHz
  - `lr11xx_radio_set_pa_cfg()`         — select Low-Power PA path
  - `lr11xx_radio_set_tx_params()`      — set lowest TX power + ramp
  - `lr11xx_radio_set_tx_cw()`          — continuous-wave carrier
  - `lr11xx_radio_set_tx_infinite_preamble()` — alt deterministic carrier
  - `lr11xx_system_set_standby()`       — stop the carrier

**Reference application / example projects (for HAL + project scaffolding):**
- `https://github.com/Lora-net/SWSD001` — "LR11xx applications" (LoRa Basics
  Modem SDK examples), includes ready STM32 board glue and a TX-CW style test
  example you can adapt. Best starting point for the project skeleton.
- `https://github.com/Lora-net/SWSD004` — LR11xx geolocation examples (only if
  you reuse its HAL layer; not required for TX).
- LoRa Basics Modem (`https://github.com/Lora-net/SWL2001`) — embeds the same
  `lr11xx_driver` under `smtc_modem_core/radio_drivers/lr11xx_driver`. Use this
  only if you want a full modem stack; **overkill** for a CW test.

**Recommendation:** scaffold from `SWSD001` (it already wires the LR11xx driver
to an STM32 HAL), strip it to a single CW test app, drop in the function from
the companion `.c` file.

### Missing files that must be added to make this buildable

From the LR11xx driver (`Lora-net/lr11xx_driver/src`):
- `lr11xx_radio.c` / `lr11xx_radio.h`
- `lr11xx_radio_types.h`   (defines `lr11xx_radio_pa_cfg_t`, `LR11XX_RADIO_PA_SEL_LP`, ramp enums)
- `lr11xx_system.c` / `lr11xx_system.h` / `lr11xx_system_types.h`
- `lr11xx_regmem.c` / `lr11xx_regmem.h`
- `lr11xx_hal.h`           (HAL contract — **declarations only**, you implement it)

Board glue (you write, or adapt from SWSD001):
- `lr11xx_hal.c`           — implements `lr11xx_hal_write/read/reset/wakeup`
  over STM32 SPI + the NSS / BUSY / NRESET / DIO9(IRQ) GPIOs.

STM32 project (CubeMX-generated, currently missing entirely):
- `*.ioc` CubeMX project (SPI1 master, USART2 VCP @115200, GPIO for NSS/BUSY/RESET/IRQ)
- `Core/Src/main.c` (calls `tx_cw_test_923_lowpower()`)
- `Core/Src/stm32l4xx_hal_msp.c`, `Core/Src/system_stm32l4xx.c`
- `Core/Inc/stm32l4xx_hal_conf.h`, `Core/Inc/main.h`
- `startup_stm32l476xx.s`
- Linker script `STM32L476RGTx_FLASH.ld`
- STM32CubeL4 HAL/CMSIS drivers (`Drivers/STM32L4xx_HAL_Driver`, `Drivers/CMSIS`)
- `Makefile` (or STM32CubeIDE `.project`/`.cproject`)
- `printf` retarget (`_write()` -> `HAL_UART_Transmit(&huart2, ...)`) for serial.

---

## 2. Test-mode function (lowest-power, 923.2 MHz)

See the full reference in
[proposed_lr1121_tx_test_mode.c](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/proposed_lr1121_tx_test_mode.c).
Key, load-bearing values:

| Setting | Value | API call |
| --- | --- | --- |
| Frequency | `923200000` Hz | `lr11xx_radio_set_rf_freq(ctx, 923200000)` |
| PA path | Low-Power PA | `lr11xx_radio_set_pa_cfg(ctx, &pa_cfg)` |
| `pa_sel` | `LR11XX_RADIO_PA_SEL_LP` | (in `pa_cfg`) |
| `pa_reg_supply` | `LR11XX_RADIO_PA_REG_SUPPLY_VREG` | (in `pa_cfg`) |
| `pa_duty_cycle` | `0x00` (minimum) | (in `pa_cfg`) |
| `pa_hp_sel` | `0x00` (HP-only field, ignored on LP) | (in `pa_cfg`) |
| **TX power** | **`-17` dBm (LOWEST available)** | `lr11xx_radio_set_tx_params(ctx, -17, ramp)` |
| Ramp | `LR11XX_RADIO_RAMP_48_US` | (arg to `set_tx_params`) |
| Mode | Continuous wave (CW) | `lr11xx_radio_set_tx_cw(ctx)` |
| Stop | back to STANDBY | `lr11xx_system_set_standby(ctx, LR11XX_SYSTEM_STANDBY_CFG_RC)` |
| Duration | 45 s (in the 30-60 s band) | host `HAL_Delay` |

### Why these are the lowest power

The LR1121 sub-GHz output has two PA paths:
- **Low-Power PA (`LR11XX_RADIO_PA_SEL_LP`)**: usable range **-17 .. +15 dBm**.
- High-Power PA (`LR11XX_RADIO_PA_SEL_HP`): range **-9 .. +22 dBm**.

The Low-Power PA bottoms out lower than the HP PA, so the lowest deterministic
conducted output is **LP PA + `SetTxParams` power = -17 dBm**. The
`pa_duty_cycle = 0x00` matches Semtech's LP-PA optimal-settings table for the
low end of the range. `pa_hp_sel` only affects the HP PA, so it is set to `0`.

### TX-mode tradeoff (CW vs infinite-preamble vs packet loop)

- **CW (`set_tx_cw`) — recommended, MOST deterministic.** A single unmodulated
  carrier sits at exactly 923.200 MHz while ON and vanishes when OFF. No
  framing, hopping, or duty-cycle ambiguity — ideal for a TX-ON/TX-OFF
  spectrum/waterfall check and for confirming the board is actually radiating.
- **Infinite preamble (`set_tx_infinite_preamble`)** — also deterministic,
  continuous, but with modulation sidebands; slightly harder to read as a clean
  tone. Use only if you specifically need a modulated continuous signal.
- **Packet loop (`set_tx` + TxDone IRQ in a loop)** — most realistic
  (LR-FHSS / LoRa framing) but **least deterministic** for an ON/OFF check: the
  carrier is duty-cycled and framed, so "is it transmitting?" is harder to
  judge. Keep as a later-stage option, not for first bring-up.

### Serial output (printed by the function)

```
=== LR1121 TX TEST MODE (DESIGN REFERENCE) ===
board_id=NUCLEO-L476RG_LR1121_BOARD_B
firmware_version=lr1121-txtest-0.1.0-DESIGN
configured_frequency_hz=923200000
tx_power_dbm=-17
tx_mode=CW_CONTINUOUS
rf_path_note=CONDUCTED ONLY: SMA -> >=50 dB inline atten -> SA/SDR. NO ANTENNA.
TX_START timestamp_ms=<HAL_GetTick at start>
TX_DONE timestamp_ms=<HAL_GetTick at stop>
=== TX TEST COMPLETE ===
```

This covers all required fields: board_id, firmware_version,
configured_frequency_hz, tx_power_dbm, tx_mode, TX_START timestamp,
TX_DONE timestamp, and the RF path note.

---

## 3. Proposed build command (TEXT ONLY — do not run in this step)

**Option A — STM32CubeIDE (GUI):** import the SWSD001-derived project, select
the `NUCLEO-L476RG` / `STM32L476RGTx` target, Project > Build All. Output:
`Debug/<project>.elf` (+ `.bin`, `.hex`).

**Option B — make + arm-none-eabi-gcc (headless):**

```text
# from the firmware project root (once the missing files above exist):
make -j8 \
  TARGET=lr1121_tx_test \
  MCU="-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard" \
  CFLAGS+="-DSTM32L476xx -DUSE_HAL_DRIVER -Os" \
  LDSCRIPT=STM32L476RGTx_FLASH.ld
# toolchain: arm-none-eabi-gcc (e.g. Arm GNU Toolchain 13.x)
# produces: build/lr1121_tx_test.elf and build/lr1121_tx_test.bin
```

---

## 4. Proposed flash command (TEXT ONLY — do not run in this step)

```text
# STM32CubeProgrammer CLI, SWD via the NUCLEO on-board ST-LINK.
# Target Board B by its ST-LINK serial to avoid flashing the wrong board:
STM32_Programmer_CLI \
  --connect port=SWD sn=066CFF3031454D3043073845 \
  --download build/lr1121_tx_test.bin 0x08000000 \
  --verify \
  --start 0x08000000
```

- `0x08000000` = STM32L4 main flash base.
- `sn=066CFF3031454D3043073845` is Board B's ST-LINK serial (from
  BOARD_SELECTION.md) — pin the flash to the intended physical board.
- `STM32_Programmer_CLI` is **not installed** on this machine yet
  (see BOARD_TX_STATUS.md); installing it is a prerequisite, not part of this
  design step.

---

## 5. Operator pre-flash checklist (human-gated, mandatory)

Do not proceed past any unchecked item.

1. **Frequency verified in code**: `TEST_FREQ_HZ == 923200000` and
   `lr11xx_radio_set_rf_freq(ctx, 923200000)` — grep the source, confirm no
   `868000000` remains anywhere in the build.
2. **Lowest power verified in code**: `pa_sel == LR11XX_RADIO_PA_SEL_LP`,
   `pa_duty_cycle == 0x00`, and `lr11xx_radio_set_tx_params(ctx, -17, ...)`.
   Confirm no `+10`/`+22` dBm or HP-PA path is selected.
3. **Conducted path / attenuation**: an inline attenuator of **>= 50 dB** is
   physically connected between the board SMA and the analyzer/SDR input, rated
   for the input power. Verify the attenuator value and connector torque.
4. **No antenna**: confirm there is **no antenna** anywhere on the RF chain —
   conducted only, into the attenuator.
5. **Board identity confirmed**: ST-LINK serial reads
   `066CFF3031454D3043073845` (Board B) before download; the flash command pins
   this serial. Confirm you are not on Board A
   (`0670FF3234584D3043215150`).
6. **Serial owner clear**: Agent 2 / the serial logger is **not** holding the
   CDC port during flash; coordinate handoff.
7. **Receiver ready**: analyzer/SDR centered near 923.2 MHz, ready to record the
   TX-ON vs TX-OFF transition before the 30-60 s window starts.
8. **Stop path known**: confirm the firmware returns to STANDBY (CW stop) after
   the duration, and you know how to power-cycle if needed.

Only after all eight items are checked may a human run the build, then the
flash, then the test.

---

=== STOP BEFORE FLASH ===

This design step ends here. No build, no flash, no erase, no RF TX, and no
serial port access were performed. Proceeding requires a human operator,
the missing SDK/files from Section 1, and a completed Section 5 checklist.
