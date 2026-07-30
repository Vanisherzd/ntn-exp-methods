# Path A — Deterministic LR1121 923.2 MHz lowest-power TX (RadioLib / Arduino)

Build + flash instructions for `lr1121_det_tx_9232_lowpower.ino`.
**Verified compilable** on this machine: arduino-cli 1.5.1, STM32 core 2.12.0,
RadioLib present. Compile produced 45360 bytes (4% of 1 MB flash), zero errors.

> ⚠️ This firmware keys RF TX when run. Build is safe; **flashing is gated**.
> Do not flash or run until the operator checklist below is satisfied and the
> user has explicitly confirmed.

## Target behavior
- frequency = 923 200 000 Hz
- TX power = -17 dBm (LR1121 Low-Power PA minimum)
- repeated LR-FHSS bursts for a 45 s window (`TX_WINDOW_S`)
- self-runs once at boot (`DET_SELFTEST_ON_BOOT=1`), then accepts `S` to repeat
- NOT CW (CW did not radiate on this board historically; uses `radio.transmit()`)

## Serial output (115200 8N1)
```
BOARD_ID NUCLEO-L476RG SN=066CFF3031454D3043073845
FIRMWARE_NAME lr1121_det_tx_9232_lowpower
FIRMWARE_VERSION 0.1.0
CONFIGURED_FREQUENCY_HZ 923200000
TX_POWER_DBM -17
TX_MODE LR_FHSS_BURST_LOOP
TX_WINDOW_S 45
WARNING conducted-only, no antenna, no OTA, attenuator >=50dB inline
INIT beginLRFHSS code 0
DET_TX_READY
TX_START <ms>
BURST 0 t=<ms> freq_hz=923200000 pwr_dbm=-17
...
TX_DONE <ms> bursts=<n> elapsed_ms=<~45000>
DET_TX_SELFTEST_COMPLETE
```

## Requirements (all present on this machine)
- arduino-cli 1.5.1 (`/opt/homebrew/bin/arduino-cli`)
- core `STMicroelectronics:stm32` 2.12.0
- library RadioLib (`~/Documents/Arduino/libraries/RadioLib/`)
- STM32CubeProgrammer (for SWD flash, alternative to MassStorage)

## Build (safe — no hardware writes)
The sketch folder name must match the `.ino` basename. Build from a folder
named `lr1121_det_tx_9232_lowpower/` containing the `.ino`:
```bash
FQBN="STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_L476RG,xserial=generic,usb=none,upload_method=MassStorage"
arduino-cli compile --fqbn "$FQBN" \
  --output-dir ./build \
  firmware_patches/deterministic_lr1121_9232_lowpower
```
(If arduino-cli rejects the folder/sketch-name mismatch, copy the `.ino` into a
temp dir named `lr1121_det_tx_9232_lowpower/` and compile that.)

Produces `build/lr1121_det_tx_9232_lowpower.ino.bin`.

---

## === STOP_BEFORE_FLASH ===
Everything below WRITES to the board and/or transmits RF. Do NOT run without
explicit user confirmation. Verify the operator checklist first.

## Operator checklist (all must be YES before flash)
1. [ ] Source confirms `TARGET_FREQ_HZ = 923200000` (not 868 / 915).
2. [ ] Source confirms `TARGET_TX_POWER_DBM = -17` (lowest; not raised).
3. [ ] `TX_MODE` is LR-FHSS burst loop, NOT CW.
4. [ ] Inline conducted attenuation >= 50 dB on the LR1121 RF output.
5. [ ] NO antenna attached. NO OTA.
6. [ ] Board identity = Board B, ST-LINK SN 066CFF3031454D3043073845.
7. [ ] No USRP capture running yet (serial verify precedes any capture).
8. [ ] User has explicitly authorized this specific flash.

## Flash (GATED — DO NOT RUN WITHOUT CONFIRMATION)
Option 1 — Arduino MassStorage (NUCLEO drag-drop, matches FQBN):
```bash
# arduino-cli upload --fqbn "$FQBN" -p /dev/cu.usbmodem1303 \
#   firmware_patches/deterministic_lr1121_9232_lowpower
```
Option 2 — STM32CubeProgrammer SWD, pinned to Board B ST-LINK serial:
```bash
# CLI="/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/Resources/bin/STM32_Programmer_CLI"
# "$CLI" -c port=SWD sn=066CFF3031454D3043073845 mode=UR \
#   --download ./build/lr1121_det_tx_9232_lowpower.ino.bin 0x08000000 \
#   --verify
# (NO -e / --erase / --mass-erase / -ob. --download writes app flash only.)
```

## Post-flash verification (before any RF capture)
1. Open serial `/dev/cu.usbmodem1303` @ 115200. Confirm boot prints
   `CONFIGURED_FREQUENCY_HZ 923200000` and `TX_POWER_DBM -17`.
2. Confirm `TX_START` ... `TX_DONE bursts=N` with N>0 (serial proves TX keyed).
3. ONLY THEN run the conducted IQ capture, tuned to 923.2 MHz, attenuation
   >= 50 dB, no antenna.
