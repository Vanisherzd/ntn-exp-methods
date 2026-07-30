# Firmware Unblock Decision

**Date:** 2026-06-26
**Goal:** deterministic LR1121 conducted TX at 923.200 MHz, lowest TX power, 30-60 s window.
**Decision: Path A (RadioLib `.ino`).** Verified buildable on this machine.

## Path comparison

| | Path A — RadioLib `.ino` | Path B — patch SWDM001 demo | Path C — standalone LR11xx driver TX |
|---|---|---|---|
| Files exist | YES — recovered `lr1121_host_replay.ino`; deterministic variant prepared | YES — recovered patch + `replay_cmd.c/.h`; vendor checkout at `~/Desktop/SWDM001` | NO — only a NOT-buildable reference snippet (`proposed_lr1121_tx_test_mode.c`) |
| Missing deps | none (arduino-cli 1.5.1, STM32 core 2.12.0, RadioLib all present) | **Keil uVision** (Windows-only) or arm-gcc/CMake port; none installed here | full CubeMX project + LR11xx driver sources + arm-gcc/CubeIDE; none present |
| Buildable now? | **YES — compiled, 45360 B (4%), 0 errors** | NO (no Keil/arm-gcc/CubeIDE on macOS) | NO |
| Flashable safely after confirm? | YES — STM32CubeProgrammer SWD `--download` (gated) or Arduino MassStorage | YES once built elsewhere | only after a build exists |
| 923.2 MHz / -17 dBm reachable? | YES — set in source; verified to compile | YES via host `B` cmd / `_init()` edit | YES in theory |
| TX mode risk | LOW — uses `radio.transmit()` (known-good); avoids CW | LOW — same LR-FHSS path as stock demo | **HIGH — designed around CW, which historically did NOT radiate on this board** |
| Effort | LOW | HIGH (toolchain) | HIGHEST (from scratch) |
| Risk level | **LOW** | MEDIUM-HIGH | HIGH |

## Why Path A
1. Only path that builds on this machine today (proven — clean compile).
2. Reuses the known-good pin map + RF-switch table from the working board.
3. Uses `radio.transmit()` (LR-FHSS), the empirically radiating path — not CW,
   which the recovered notes show did NOT radiate on this exact board.
4. Deterministic self-running 45 s window + full serial instrumentation
   (board_id, firmware name/version, configured_frequency_hz, tx_power_dbm,
   tx_mode, TX_START, TX_DONE, conducted-only warning).

## Why not B / C now
- **B:** requires Keil (Windows) or a non-trivial sxlib→arm-gcc port. Good
  fallback / reference (it is literally the patched form of Board B's current
  firmware), but not buildable here.
- **C:** no toolchain present AND it leans on CW, which is the one mode shown not
  to radiate on this board. Highest risk, lowest readiness.

## Open caveat to validate empirically (after authorized flash)
RadioLib must accept -17 dBm on the LP PA for LR-FHSS; if it clamps, the boot
`INIT beginLRFHSS code` will be non-zero — read it before trusting the window.
If -17 is rejected, step up to the next-lowest accepted value and re-verify.
