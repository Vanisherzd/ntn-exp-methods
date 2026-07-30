# Recovered Firmware Candidates

**Date:** 2026-06-26
**Source:** git commit `c0e5499` ("remove hardware implementation remnants") deleted
the firmware tree. Recovered from parent `c0e5499^` into `recovered_firmware_candidates/`.

## Recovery commands used
```
git diff --diff-filter=D --name-only c0e5499^ c0e5499        # list deleted files
git show c0e5499^:<path> > recovered_firmware_candidates/<file>   # per file
```

## Deleted firmware files recovered
| Recovered file | Original path (at c0e5499^) | Lines |
|---|---|---|
| `lr1121_host_replay.ino` | `hardware/ota_iq/firmware/arduino/lr1121_host_replay/lr1121_host_replay.ino` | 187 |
| `lr11xx_lr_fhss_ping_host_replay.patch` | `hardware/ota_iq/firmware/lr11xx_lr_fhss_ping_host_replay.patch` | 144 |
| `replay_cmd.c` | `hardware/ota_iq/firmware/replay_cmd.c` | 95 |
| `replay_cmd.h` | `hardware/ota_iq/firmware/replay_cmd.h` | 64 |
| `firmware_README.md` | `hardware/ota_iq/firmware/README.md` | 85 |

(Non-firmware deletions in the same commit — `replay_driver.py`, `ota_common.py`,
`generate_real_replay_schedule.py`, analysis scripts, replay YAML configs — are the
host-side OTA replay tooling; recoverable the same way if needed.)

---

## Candidate 1 — `lr1121_host_replay.ino`  ★ BEST
| Attribute | Finding |
|---|---|
| Targets LR1121? | YES — `#include <RadioLib.h>`, `LR1121 radio = new Module(...)`, `radio.beginLRFHSS(...)` |
| Targets NUCLEO-L476RG? | YES — FQBN `STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_L476RG,...` in header comment |
| Frequency constant | NONE hard-coded as target; **host-commanded per burst** (`B <idx> <rf_freq_hz> <pwr> <delay>`). Default bring-up at 868.0 MHz, overwritten per burst. Accepts arbitrary Hz → **923200000 is directly settable**. |
| TX power constant | Host-commanded per burst (`int8_t pwr`). Bring-up default 10 dBm, overwritten. → lowest (-17 dBm) settable. |
| TX mode | LR-FHSS burst via `radio.transmit()` (BW 1574.2 kHz, CR 5/6, FCC grid 25391 Hz). Also a `C` GFSK/CW-fallback diagnostic. **Documents that true CW (`setTxCw`) did NOT radiate on this board — use `transmit()`.** |
| Serial logging | `REPLAY_READY` at boot, `RDY` per prompt, `Packet sent!`, `BURST_DONE <idx> <freq> <pwr>` |
| Build system | Arduino: arduino-cli + STM32 core + RadioLib. **All present on this machine.** |
| Pin map | NSS=D7, IRQ=D5, RST=A0, BUSY=D3 (known-good; D10/D3/D8/D9 gave -707 SPI_CMD_FAILED) |

## Candidate 2 — `lr11xx_lr_fhss_ping_host_replay.patch` (+ `replay_cmd.c/.h`)
| Attribute | Finding |
|---|---|
| Targets LR1121? | YES — patches Semtech SWDM001 `lr11xx_lr_fhss_ping` demo (LR11xx/sxlib) |
| Targets NUCLEO-L476RG? | YES — SWDM001 NUCLEO-L476RG port |
| Frequency constant | Stock demo `RF_FREQUENCY = 868000000`; patch replaces it with host-commanded `rf_freq_hz`. → 923200000 settable via `B` command or by editing `_init()` seed. |
| TX power constant | Stock `POWER_IN_DBM = 10`; patch → host-commanded `tx_power_dbm`. |
| TX mode | LR-FHSS (GMSK_488, CR 5/6, BW 1574219 Hz, hopping, grid 25391 Hz) |
| Serial logging | `REPLAY_READY`, `RDY`, existing `Packet to send:` / `Packet sent!`, `BURST_DONE` |
| Build system | **Keil uVision** + sxlib (vendor). Checkout exists at `~/Desktop/SWDM001/...` but **Keil / arm-gcc / CubeIDE are NOT installed on this Mac** → not buildable here. |

## Direct match to Board B's running firmware
The flash dump strings (`hardware_conducted_iq/board_inventory/board_B_flash_dump_*/board_B_flash_strings.txt`)
contain `LR11XX-LR-FHSS Ping Init` and `RF=%lu Hz, PWR=%d dBm, payload_len=%u` —
the **stock SWDM001 `lr11xx_lr_fhss_ping` demo**, the UNpatched ancestor of
Candidate 2. So Board B currently runs the stock demo (Candidate 2 minus the patch).
The numeric `868000000` / `10` do not appear as strings because they are runtime
format args (`%lu` / `%d`), confirming they are compiled constants, not editable
over serial in the current image.

## Recommendation
Use **Candidate 1 (RadioLib `.ino`)** — only path buildable on this machine today,
already accepts 923.2 MHz / -17 dBm. See `firmware_patches/deterministic_lr1121_9232_lowpower/`
and `FIRMWARE_UNBLOCK_DECISION.md`.
