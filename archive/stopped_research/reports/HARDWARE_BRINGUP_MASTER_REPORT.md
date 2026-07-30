# Hardware Bring-Up Master Report — LR1121 Conducted TX

**Date:** 2026-06-26
**Scope:** Resolve board-side firmware/control to create a deterministic LR1121 conducted TX at 923.200 MHz, lowest TX power, conducted-only.
**Status:** Board B **flashed + serial-verified + conducted-IQ-capture confirmed** for deterministic 923.2 MHz / -17 dBm conducted TX (2026-06-26). First **visible TX-ON** at the target frequency (+41 dB over noise floor). Conducted IQ-level evidence only — no link/packet/OTA/satellite claims.

---

## UPDATE 2026-06-26 (session 3 — FLASH DONE, serial verification PASSED)

**Step 0 — commit:** `11d6725` "hardware: add LR1121 conducted IQ bring-up tooling and Board B firmware inventory" (reports/scripts/recovered firmware/patches/board_inventory text + .gitignore; no raw .bin/.npy).

**Step 1 — compile:** `arduino-cli` → `build/lr1121_det_tx_9232_lowpower.ino.bin` (44.7 KB, 0 errors).

**Step 2 — flash Board B: SUCCESS + VERIFIED.**
- STM32CubeProgrammer v2.21.0, SWD, pinned SN `066CFF3031454D3043073845`, `mode=UR --download 0x08000000 --verify`.
- Download-flow sector erase [0 22] only (no mass erase, no option-byte change). "Download verified successfully."
- Log: `hardware_conducted_iq/board_inventory/board_B_flash_9232_20260626_002829/flash_log.txt`

**Step 3 — post-flash serial verification: PASSED (all required evidence).**
```
BOARD_ID NUCLEO-L476RG SN=066CFF3031454D3043073845
FIRMWARE_NAME lr1121_det_tx_9232_lowpower
FIRMWARE_VERSION 0.1.0
CONFIGURED_FREQUENCY_HZ 923200000
TX_POWER_DBM -17
TX_MODE LR_FHSS_BURST_LOOP
WARNING conducted-only, no antenna, no OTA, attenuator >=50dB inline
INIT beginLRFHSS code 0
TX_START 1378 ... BURST 0..38 (freq_hz=923200000 pwr_dbm=-17) ... TX_DONE 47433 bursts=39 elapsed_ms=46055
DET_TX_SELFTEST_COMPLETE
```
- Logs: `board_B_flash_9232_20260626_002829/post_flash_serial_log.txt` (boot+TX_START+20 bursts) and `post_flash_serial_log_fullwindow.txt` (full window incl. TX_DONE, 39 bursts).
- Board B is now configured at 923.2 MHz / -17 dBm and `beginLRFHSS` returns 0 (LR1121 accepts -17 dBm on the LP PA). The earlier caveat (RadioLib might clamp -17) is **resolved — accepted**.

**Step 4 — conducted IQ capture: DONE — TX-ON VISIBLE.**
- Operator confirmed the conducted RF path: `LR1121 RF → 30 dB → 20 dB → SMA coax → USRP B210 RX2 A`, no antenna, 50 dB inline.
- USRP B210 (serial 8000304, UHD 4.10) via `rx_samples_to_file` fallback (pyuhd absent).
- TX timing automated via `--tx-control command`: noise window with firmware idle, then serial `S` triggers the 45 s LR-FHSS window aligned to the ON capture.
- Run dir: `hardware_conducted_iq/20260626_003643_gain20_50db/` (freq 923.2 MHz, gain 20, attn 50 dB, rate 4 MS/s, off 10 s / on 45 s).

Result (conducted IQ-level only):
| metric | value |
|---|---|
| TX-ON visible | **True** |
| TX-ON − TX-OFF | **41.13 dB** (noise −69.46 → peak −27.54 dB) |
| peak frequency | 923238085.94 Hz (offset +38.09 kHz from center, within LR-FHSS hop grid) |
| noise peak offset | −488 Hz (FFT bin, no signal) |
| clipping / saturation / artifact warnings | False / False / False |
| usable for conducted IQ-level evidence | True |
| CFO / hop-center proxy candidate | True |

Artifacts: `psd_noise.png`, `psd_txon.png`, `maxhold_txon_vs_noise.png`, `waterfall_txon.png`, `signal_detection_summary.json`, `EXPERIMENT_REPORT.md`, `capture_metadata.json`. Raw `.npy` (noise 305 MB, txon 1.37 GB) are gitignored.

This empirically confirms the root-cause fix: the prior 868 MHz firmware was ~55 MHz off the 923 MHz capture band (no signal); the reflashed 923.2 MHz firmware produces a clear conducted TX-ON at the target. Minor: USRP logged one USB overflow (dropped samples) at 4 MS/s — benign, TX-ON still clearly resolved.

**Allowed framing:** conducted IQ-level capture, TX-ON/TX-OFF spectrum evidence, waterfall evidence, CFO/hop-center proxy candidate. **Not claimed:** packet decode, PER/PDR/CRC, gateway ACK, link/OTA/satellite validation.

---

---

## UPDATE 2026-06-26 (session 2 — flash dump + firmware recovery + prepared patch)

**Read-only flash dump of Board B: DONE.**
- Tool: STM32CubeProgrammer v2.21.0, connect-under-reset (`mode=UR`, read-only `--upload`, no erase/write).
- Device confirmed: STM32L476 (ID `0x415`, Rev 4), 1 MB flash. 1048576 bytes read.
- Dump: `hardware_conducted_iq/board_inventory/board_B_flash_dump_20260626_001321/board_B_flash_dump.bin`
- **SHA-256:** `c1a7402d6c2429372c57f9cae02e176d7c9b0461c9aae3383be85148a6bc870c`
- Strings evidence for the current 868 MHz / 10 dBm firmware: `LR11XX-LR-FHSS Ping Init`, `RF=%lu Hz, PWR=%d dBm, payload_len=%u`, `Packet sent!`, `Packet to send:`, `lr1121_xtal`. → Board B runs the **stock Semtech SWDM001 `lr11xx_lr_fhss_ping` demo**. The numeric 868000000/10 are runtime format args (`%lu`/`%d`), i.e. compiled constants, not serial-settable — confirming reflash is required.

**Recovered firmware from git `c0e5499^`** → `recovered_firmware_candidates/` (5 files). See `RECOVERED_FIRMWARE_CANDIDATES.md`. Key: the RadioLib `.ino` accepts host-set frequency/power and uses the known-good `transmit()` path; notes that **CW did NOT radiate** on this board.

**Deterministic TX firmware PREPARED + BUILD-VERIFIED (Path A):**
- `firmware_patches/deterministic_lr1121_9232_lowpower/lr1121_det_tx_9232_lowpower.ino` — 923200000 Hz, -17 dBm (LP PA min), 45 s repeated LR-FHSS burst loop, full serial instrumentation, conducted-only warning.
- **Compiled clean** on this machine: arduino-cli 1.5.1 + STM32 core 2.12.0 + RadioLib → 45360 B (4% flash), 0 errors. (Compile only — NOT flashed.)
- Decision rationale in `FIRMWARE_UNBLOCK_DECISION.md`: Path A chosen (only buildable path here; Path B needs Keil/arm-gcc absent on macOS; Path C relies on non-radiating CW).

### Exact next command that would flash Board B — ⛔ STOP / DO NOT RUN WITHOUT USER CONFIRMATION
```bash
# === GATED: writes app flash. Requires explicit user authorization + operator checklist. ===
FQBN="STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_L476RG,xserial=generic,usb=none,upload_method=MassStorage"
# 1) build (SAFE):
arduino-cli compile --fqbn "$FQBN" --output-dir ./build firmware_patches/deterministic_lr1121_9232_lowpower
# 2) flash (⛔ DO NOT RUN until confirmed) — SWD, pinned to Board B ST-LINK:
CLI="/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/Resources/bin/STM32_Programmer_CLI"
"$CLI" -c port=SWD sn=066CFF3031454D3043073845 mode=UR \
  --download ./build/lr1121_det_tx_9232_lowpower.ino.bin 0x08000000 --verify
# NO -e / --erase / --mass-erase / -ob. --download writes application flash only.
```

### Post-flash verification plan (in order; no capture before serial proof)
1. Serial `/dev/cu.usbmodem1303` @115200 boot prints `CONFIGURED_FREQUENCY_HZ 923200000` and `TX_POWER_DBM -17` (and `INIT beginLRFHSS code 0`).
2. Serial shows `TX_START … TX_DONE bursts=N` with N>0 → TX actually keyed at the target.
3. ONLY THEN run conducted IQ capture at 923.2 MHz, attenuation **50 dB only**, no antenna.

---

This report consolidates six parallel investigations:
- [FIRMWARE_PROVENANCE.md](FIRMWARE_PROVENANCE.md) (Agent 1)
- [BOARD_B_SERIAL_CONTROL_REPORT.md](BOARD_B_SERIAL_CONTROL_REPORT.md) (Agent 2)
- [READONLY_FLASH_TOOLING_PLAN.md](READONLY_FLASH_TOOLING_PLAN.md) (Agent 3)
- [DETERMINISTIC_LR1121_TX_PLAN.md](DETERMINISTIC_LR1121_TX_PLAN.md) (Agent 4)
- [CONDUCTED_IQ_PIPELINE_READINESS.md](CONDUCTED_IQ_PIPELINE_READINESS.md) (Agent 5)
- [VALIDATION_STATUS_FOR_SLIDES.md](VALIDATION_STATUS_FOR_SLIDES.md) (Agent 6)

---

## 1. Board A status

- ST-LINK SN `0670FF3234584D3043215150`, NUCLEO-L476RG.
- **Currently NOT connected.** ST-LINK enumeration at session start showed only Board B.
- Prior observation: serial boot log produced **zero bytes**; firmware unresolved.
- Flash fingerprint never taken (read-only dump tooling was thought missing — now resolved, see §6).
- **Not verified** for 923.2 MHz LR1121 conducted TX.
- Verdict: unknown firmware, possibly blank / non-printing / different UART config. Cannot be assessed until physically connected and a read-only flash dump is taken.

## 2. Board B status

- ST-LINK SN `066CFF3031454D3043073845`, NUCLEO-L476RG. **Connected now.**
- Serial: `/dev/cu.usbmodem1303` @ 115200 8N1. Readable, free-running.
- Firmware is a **free-running auto-loop** (no CLI, no prompt, no command parser). Each iteration prints:
  ```
  Packet to send: <hex>
  RF=868000000 Hz, PWR=10 dBm, payload_len=N
  Packet sent!
  ```
  `payload_len` increments by one byte each loop (observed 11→24, 33→40 across two passes).
- **Alive, but wrong configuration:** RF = 868000000 Hz, PWR = 10 dBm. This is **not** Taiwan 923.2 MHz and **not** lowest TX power.
- Frequency/power are **firmware constants**, printed unconditionally. **No serial command can change them** — reconfiguration requires re-flashing.
- The firmware **keys RF TX autonomously** every loop (no button, no command). Stopping it requires power-down or re-flash.
- **Not verified** for 923.2 MHz conducted TX (it transmits, but at the wrong frequency/power).

## 3. Why Board B is alive but wrong-frequency firmware

Agent 1 matched Board B's exact banner (`RF=868000000 Hz`, `PWR=10 dBm`, free-running, incrementing payload) to the **stock Semtech SWDM001 `lr11xx_lr_fhss_ping` demo**, whose defaults are `RF_FREQUENCY = 868000000` and `POWER_IN_DBM = 10`. The board was flashed with that vendor demo (EU 868 defaults) and never reconfigured for the TW 923.2 MHz / lowest-power target.

The exact UART banner is **not produced by any code currently in the repo** — it appears only in historical capture logs (e.g. `local_archive/validation_runs/20260609T135342Z/dryrun_001/tx_uart.log:2-3`). The repo's working tree contains **zero firmware source/binary**. Provenance is the external SWDM001 SDK, not this repo.

## 4. Why the current conducted IQ captures failed

- USRP RX chain + spectrum analyzer path are **internally validated** (Agent 5: scripts compile, RX-only constrained, correct TX-OFF→TX-ON sequencing, no over-claim of `signal_detected`).
- All conducted captures (60 dB & 50 dB attenuation, gains 0/10/20; debug scan at 922.0 / 923.2 / 924.4 MHz) showed **no TX-ON, no clipping, no saturation**.
- Root cause is now explained: **Board B transmits at 868 MHz**, while the conducted captures were tuned around **923 MHz**. The USRP was listening on the wrong band — Board B's energy is ~55 MHz away, outside the analyzed span. There was nothing to see at 923.2 MHz because the board never transmitted there.
- Therefore the blocker is **board-side firmware**, confirmed — not the USRP, not the analyzer, not attenuation.
- One analysis caveat (Agent 5): `analyze_conducted_iq.py` uses `max(tx_db - noise_db)` over all FFT bins for the visibility delta — positively biased, a single bin can clear the 6 dB threshold by chance. Tighten to a noise-statistics-aware threshold before trusting any future "visible" verdict.

## 5. Was a deterministic TX firmware/control path found?

**Partially — a recoverable path exists in git history.** Commit `c0e5499` ("remove hardware implementation remnants") **deleted** a firmware modification layer that is fully recoverable:

| Deleted file (recover via `git show c0e5499^:<path>`) | What it is |
|---|---|
| `hardware/ota_iq/firmware/arduino/lr1121_host_replay/lr1121_host_replay.ino` | RadioLib sketch, host-commanded per-burst TX (`RDY`→`B …`→`BURST_DONE`) |
| `hardware/ota_iq/firmware/lr11xx_lr_fhss_ping_host_replay.patch` | Hand-apply patch for the SWDM001 demo |
| `hardware/ota_iq/firmware/replay_cmd.{c,h}` | Host replay command layer |
| `hardware/ota_iq/firmware/README.md` | Build/flash notes |

These are **command-gated** (not the free-running stock demo on Board B), but the RadioLib `.ino` is the **shortest path to a deterministic TX**: change two constants (frequency → 923200000, power → lowest) and reflash. Caveat: it still requires the external Arduino STM32 core + RadioLib to build, and it is a *modification* layer — not a turnkey, ready-to-flash image.

Agent 4 independently designed a clean-room alternative: a CW (continuous-wave) test mode on the Semtech LR11xx driver (`Lora-net/lr11xx_driver` + `SWSD001` example), with **lowest power = LP PA at -17 dBm** (`pa_sel=LP`, `pa_reg_supply=VREG`, `set_tx_params(-17, RAMP_48_US)`), 45 s window, full serial instrumentation (board_id, fw_version, configured_frequency_hz=923200000, tx_power_dbm=-17, tx_mode, TX_START/TX_DONE). See [proposed_lr1121_tx_test_mode.c](hardware_conducted_iq/board_inventory/proposed_lr1121_tx_test_mode.c) (intentionally NOT-YET-BUILDABLE — SDK headers absent; the clang errors are expected).

## 6. Flash tooling — premise corrected

The assumption "STM32 read tools are missing" is **partly wrong**: **STM32CubeProgrammer v2.21.0 is already installed**:
```
/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/Resources/bin/STM32_Programmer_CLI
```
- Read-only fingerprint: `STM32_Programmer_CLI -c port=SWD mode=HOTPLUG` (prints device ID 0x415, flash size, UID — no erase).
- Read-only dump: `… -c port=SWD mode=HOTPLUG --upload 0x08000000 0x100000 <out.bin>` (reads MCU→host; never writes the chip).
- **WARNING:** even a read-only connect **halts the running CPU**. Run a dump only when the board's TX/serial loop is not needed; power-cycle to resume. Forbidden flags enumerated in the tooling plan: `-e`, `--mass-erase`/`-me`, `-w`/`--download`/`-d`, `-ob`/`--rdp`, `mode=UR`, `mode=POWERDOWN`.

(st-info/st-flash/openocd/pyocd remain absent; not needed — Cube covers it. `brew install stlink` / `uv tool install pyocd` documented as optional fallback.)

---

## 7. Exact next action

Two viable unblock paths. **Both require a flash, which is gated — STOP and get explicit confirmation before executing.**

**Recommended (fastest): adapt the recovered RadioLib sketch.**
1. (Read-only, do now) Take a flash dump of Board B for provenance before any change:
   `STM32_Programmer_CLI -c port=SWD mode=HOTPLUG --upload 0x08000000 0x100000 hardware_conducted_iq/board_inventory/board_b_flash_dump_<ts>.bin`
   — do this while no capture is running; it halts the CPU. **This is read-only and within gates.**
2. Recover the sketch: `git show c0e5499^:hardware/ota_iq/firmware/arduino/lr1121_host_replay/lr1121_host_replay.ino > recovered_sketch.ino`
3. Edit: frequency → `923200000`, power → lowest LR1121 setting; confirm conducted-only, no antenna.
4. **STOP — explicit flash confirmation required.**
5. Build (Arduino STM32 core + RadioLib) → flash to Board B (ST-LINK SN `066CFF3031454D3043073845`).
6. Verify over serial: configured frequency = 923200000 Hz, lowest power, TX_START/TX_DONE present — **before** any RF.
7. Only then run the conducted IQ capture, tuned to 923.2 MHz, attenuation ≥ 50 dB, no antenna.

**Alternative (cleaner instrumentation): build Agent 4's CW test mode** from `Lora-net/lr11xx_driver` + `SWSD001`. Higher effort (full CubeMX project), but gives exact `tx_mode`/timestamp telemetry and a deterministic single-tone CW for an unambiguous TX-ON/TX-OFF check. Same flash gate applies.

## 8. Blocker list (if not proceeding to flash)

1. Board B firmware is EU 868/10 dBm; cannot be reconfigured without flashing (no serial control path).
2. No turnkey 923.2 MHz / lowest-power firmware image exists; nearest asset is the recoverable-but-modification-only RadioLib sketch (needs Arduino STM32 core + RadioLib) or a from-scratch build on the LR11xx SDK.
3. Board A firmware unresolved and board disconnected — cannot fingerprint until reconnected.
4. Flashing is required to unblock and is behind the safety gate (needs explicit confirmation).

---

## 9. Safety gate status

All gates **respected** this session: no flash, no erase, no option-byte change, no RF TX initiated by us, no OTA, no antenna, no USRP capture/TX, attenuation untouched. Board B's autonomous 868 MHz TX is **pre-existing firmware behavior**, not initiated by this session (Agent 2 was 100% passive read-only; zero bytes written to the port).

## 10. Forbidden vs. allowed claims

- **Not claimed:** RF validation success, packet decode, PER, PDR, CRC, gateway ACK, satellite/live-satellite link, OTA validation.
- **Claimed (accurate):** board firmware inventory, board-side TX blocker identified, conducted IQ debug, receiver-chain + analyzer validation, recoverable firmware provenance.

---

## 11. Git policy — recommendations (NOT auto-committed)

See live `git status --short` / `git diff --stat` printed in the session.

**Recommend committing** (text reports + safe pipeline):
- `HARDWARE_BRINGUP_MASTER_REPORT.md`, `FIRMWARE_PROVENANCE.md`, `BOARD_B_SERIAL_CONTROL_REPORT.md`, `READONLY_FLASH_TOOLING_PLAN.md`, `DETERMINISTIC_LR1121_TX_PLAN.md`, `CONDUCTED_IQ_PIPELINE_READINESS.md`, `VALIDATION_STATUS_FOR_SLIDES.md`, `BOARD_TX_STATUS.md`, `BOARD_TX_BLOCKER.md`
- `scripts/{analyze_conducted_iq,run_conducted_iq_session,run_conducted_iq_debug_scan,usrp_rx2a_capture,lr1121_serial_logger}.py`
- `hardware_conducted_iq/board_inventory/` (BOARD_SELECTION.md, proposed_lr1121_tx_test_mode.c — reference snippet)
- `.gitignore` (raw-IQ ignore additions)

**Keep untracked / local-only** (raw evidence, large binaries):
- `hardware_conducted_iq/**/*.npy` and per-run raw captures (already gitignored)
- `hardware_conducted_iq/board_inventory/board_b_serial_raw.log` (raw serial dump — decide; small, but it's raw evidence)
- any future `board_b_flash_dump_*.bin` (raw flash image — never commit)
- `tmp/`, `output/`

**Decide case-by-case:** `paper/slides_overview.*`, `paper/slide_figures/`, `paper/assets_external/`, `paper/figures/*.pdf`, `paper/nthu_logo.png` — slide assets unrelated to this bring-up.
