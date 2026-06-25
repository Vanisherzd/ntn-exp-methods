# Firmware Provenance Report — LR1121 + NUCLEO-L476RG (Board B)

Agent 1 (firmware provenance / repo archaeology). Read-only. No board was
flashed, erased, or opened; no serial port was opened; no RF TX was run.

Scope: exhaustive search of the entire repo working tree **and full git
history** (all refs), excluding only `.git/` internals and `.venv/`.

---

## 1. Candidate firmware projects (working tree)

**None found in the repo working tree.**

A full scan found **no** firmware source or project of any kind currently
checked in:

- No `.c` / `.cpp` / `.h` / `.hpp` / `.ino` / `.s` / `.S` source files anywhere.
- No `.ioc` (STM32CubeMX), `Makefile`, `CMakeLists.txt`, `platformio.ini`,
  `mbed_app.json`, or linker (`.ld`) scripts.
- No `SWDM001` / vendor SDK checkout anywhere in the tree
  (`find . -iname '*swdm*'` → nothing).
- `hardware/ota_iq/` now contains only an empty `runs/` dir; all its source was
  removed (see §6).

The only vendor references surviving in the working tree are documentation, not
code:
- `paper/refs.bib:50-55` — `@misc{swdm001 ...}` citing
  `https://github.com/Lora-net/SWDM001`.
- `paper/.claude/settings.local.json` — incidental string match only.

## 2. Candidate firmware projects (recovered from git history)

Firmware sources **did** exist and were deleted in commit `c0e5499`
("chore(repo): remove hardware implementation remnants from submission scope").
Recoverable from `git show c0e5499^:<path>`. **Important:** these are a
host-commanded *modification* of an external vendor demo — they are NOT the
vendor demo itself, and (see §5) NOT the firmware currently running on Board B.

| Path (in history, parent of c0e5499) | What it is |
|---|---|
| `hardware/ota_iq/firmware/arduino/lr1121_host_replay/lr1121_host_replay.ino` | RadioLib Arduino sketch for NUCLEO-L476RG + LR1121; host-commanded per-burst LR-FHSS replay. Emits `REPLAY_READY`/`RDY`/`Packet sent!`/`BURST_DONE`. |
| `hardware/ota_iq/firmware/replay_cmd.c` / `replay_cmd.h` | "REPRESENTATIVE C" UART line-parser meant to be dropped into the Semtech **SWDM001** demo `lr11xx_lr_fhss_ping/` and built in Keil. |
| `hardware/ota_iq/firmware/lr11xx_lr_fhss_ping_host_replay.patch` | A *representative* hand-apply patch against the vendor SWDM001 tree (not the tree itself). |
| `hardware/ota_iq/firmware/README.md` | Build/flash instructions; explicitly states the real firmware lives in an external checkout `~/Desktop/SWDM001/...`. |

## 3. Candidate build commands

**None reproducible from the repo.** No build system is checked in. Build
provenance is described only in prose in the (deleted) firmware README and
patch header:

- Arduino variant FQBN (from `lr1121_host_replay.ino` header, history):
  `STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_L476RG,xserial=generic,usb=none,upload_method=MassStorage`
  — requires the Arduino STM32 core + **RadioLib** library (neither vendored).
- Vendor variant: copy `replay_cmd.{c,h}` into
  `~/Desktop/SWDM001/src/demos/lr11xx_lr_fhss_ping/`, hand-apply the patch in
  **Keil uVision**, add `replay_cmd.c` to the Keil project, rebuild
  (`hardware/ota_iq/firmware/README.md` "Apply / build / flash" steps 1–5,
  history). The SWDM001 source tree is **not in the repo**.

## 4. Candidate flash commands

**None in the repo.** Flashing is described only as manual:
- Arduino: `upload_method=MassStorage` (drag-drop to ST-LINK mass-storage), or
  Arduino IDE upload.
- Vendor: "Rebuild and flash the NUCLEO-L476RG" from Keil
  (`firmware/README.md` step 5, history).
- The live board-inventory probe confirms **no** flash/dump tooling is even
  installed on this host (`st-info`, `st-flash`, `STM32_Programmer_CLI`,
  `pyocd`, `openocd` all absent):
  `hardware_conducted_iq/board_inventory/20260625_234118/board_B/stlink_probe.txt`.

## 5. Binary firmware images

**None found — anywhere — in the working tree or in any git revision.**
No `.bin`, `.elf`, `.hex`, `.dfu`, `.uf2`, or `.axf` exists in the repo or its
history. Independently confirmed by the prior board inventory:
`hardware_conducted_iq/board_inventory/20260625_234118/board_B/repo_firmware_artifacts.txt`
("No `.bin`, `.elf`, `.hex` ... firmware build artifacts were found").
No flash dump of Board B was produced (no STM32 tooling installed), so there is
no image to fingerprint against either.

## 6. Source of the "RF=868000000 Hz, PWR=10.0 dBm" / "Packet sent!" UART strings

**Logs-only in this repo. No repo code (working tree or any git revision)
emits the free-running banner.**

- The exact free-running line
  `RF=868000000 Hz, PWR=10.0 dBm, payload_len=12` followed by `Packet sent!`
  appears ONLY in captured log/report files, never in source. Representative:
  - `local_archive/validation_runs/20260609T135342Z/dryrun_001/tx_uart.log:2-3`
  - `local_archive/validation_runs/20260609T135342Z/hw_dryrun_001/tx_uart.log:2-3`
  - (re-quoted in the inventory report
    `hardware_conducted_iq/board_inventory/20260625_234118/board_B/repo_firmware_artifacts.txt`)
- A history search for the format tokens across all C/C++/INO blobs
  (`git grep ... payload_len|RF=.*PWR|Packet sent` over `git rev-list --all`)
  matches **only** the Arduino sketch's literal `Packet sent!`
  (`...lr1121_host_replay.ino:136`) — and that sketch does **not** print the
  `RF=... PWR=... payload_len=...` banner, nor does it free-run: it is
  host-command-gated (`RDY` → read `B ...` line → TX → `BURST_DONE`).
- The deleted firmware README names the true source explicitly:
  the **stock** Semtech SWDM001 `lr11xx_lr_fhss_ping` demo "free-runs at a fixed
  `RF_FREQUENCY = 868000000`" and its existing logs are `Packet to send: ...` /
  `Packet sent!` (`hardware/ota_iq/firmware/README.md`, history). The
  `POWER_IN_DBM` / `RF_FREQUENCY` macros (10 dBm / 868000000) match Board B's
  self-report.

Conclusion: Board B's banner is produced by the **stock (or lightly
instrumented) Semtech SWDM001 `lr11xx_lr_fhss_ping` synchronous demo**, whose
source is external and was never committed. The repo only ever held a
host-commanded *override* of that demo (patch + representative parser +
RadioLib alternate), which is a different, non-free-running program.

## 7. Definitive verdict

**No.** The repo does **not** contain the path that produced Board B's current
firmware.

- Board B free-runs `RF=868000000 Hz, PWR=10 dBm` autonomously (no host command
  needed — confirmed by the inventory: "board was already emitting packet-send
  logs ... No host TX command was sent",
  `hardware_conducted_iq/board_inventory/20260625_234118/board_B/BOARD_FIRMWARE_REPORT.md`).
  This behavior matches the **stock SWDM001 free-running demo**, not the
  host-gated replay code that the repo briefly contained.
- The repo never contained the vendor SWDM001 source, a build system, or any
  binary image. The only firmware code that ever existed (now deleted in
  `c0e5499`) was a host-commanded modification layer that (a) is not the running
  firmware and (b) still depends on the external vendor tree to build.

### External provenance that is MISSING (required to reproduce/identify Board B)

1. **Vendor SDK:** Semtech / LoRa-net **SWDM001** ("LR-FHSS Transmission Demo",
   `https://github.com/Lora-net/SWDM001`) — not vendored; referenced only in
   `paper/refs.bib:50` and the deleted firmware README.
2. **Example app:** the `lr11xx_lr_fhss_ping` demo, **synchronous** variant
   (`lr11xx_lr_fhss_ping_sync.c`), with default macros `RF_FREQUENCY =
   868000000` and `POWER_IN_DBM = 10`. Expected external location per docs:
   `~/Desktop/SWDM001/src/demos/lr11xx_lr_fhss_ping/`.
3. **Underlying radio driver:** Semtech `lr11xx` driver / `sxlib`
   (`lr11xx_radio_set_rf_freq`, `lr11xx_comp_set_tx_cfg`, `SXLIB_LOG`).
4. **Build toolchain:** **Keil uVision** (ARM Compiler) project for SWDM001 —
   no Keil project, Makefile, or CMake in repo.
5. **Alternate toolchain (for the deleted Arduino variant only):** Arduino +
   STMicroelectronics STM32 core + **RadioLib** library — also not vendored.
6. **Flash toolchain:** ST-LINK mass-storage / Keil flash; none of
   `st-flash` / `STM32_Programmer_CLI` / `openocd` / `pyocd` installed.
7. **Board B flash image / dump:** none exists; cannot fingerprint the running
   image to confirm exact build.

### Bottom line for bring-up

To control or re-flash Board B for the intended 923.2 MHz LR1121 conducted TX,
the team must obtain the external SWDM001 checkout (or rebuild the RadioLib
sketch), apply the host-replay change, and flash via Keil/ST-LINK — none of
which is reproducible from this repo alone. The repo's
`semtech_validation/lr1121_tx_config_example.json` (923200000 Hz, 0 dBm) is a
*target config*, not firmware, and does not match the 868 MHz/10 dBm image
currently on the board.
