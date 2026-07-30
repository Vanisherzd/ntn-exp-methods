# Path B — Patch Semtech SWDM001 `lr11xx_lr_fhss_ping` demo (host-commanded freq/power)

This is the recovered host-replay patch for the vendor SWDM001 demo. It makes the
demo accept per-burst frequency + power over UART instead of free-running at the
stock `RF_FREQUENCY = 868000000` / `POWER_IN_DBM = 10` (which is exactly Board B's
current behavior — confirmed by the flash-dump strings `LR11XX-LR-FHSS Ping Init`,
`RF=%lu Hz, PWR=%d dBm, payload_len=%u`).

> ⚠️ NOT BUILDABLE ON THIS MACHINE. See "Toolchain status" below. Prefer Path A.

## Files
- `lr11xx_lr_fhss_ping_host_replay.patch` — apply BY HAND (Keil) to the vendor tree
- `replay_cmd.c` / `replay_cmd.h` — new UART line parser to copy into the demo dir

## Vendor checkout status
EXISTS at `~/Desktop/SWDM001/src/demos/lr11xx_lr_fhss_ping/`
(`lr11xx_lr_fhss_ping.c/.h`, `_async.c`, `_sync.c`, `_start.c` present). The patch
targets the SYNCHRONOUS variant (`_sync.c`), which is the one currently flashed.

## What the patch changes (per recovered firmware/README.md)
- `lr11xx_lr_fhss_ping.h` — add `rf_freq_hz`, `tx_power_dbm`, `burst_index` to state.
- `lr11xx_lr_fhss_ping.c` — use state fields instead of `RF_FREQUENCY`/`POWER_IN_DBM` macros.
- `lr11xx_lr_fhss_ping_sync.c` — replace auto-ping loop with command-gated loop.
- add `replay_cmd.c` to the build; provide `replay_uart_getchar()` on the VCP UART.

For deterministic 923.2 MHz / lowest power: host sends `B <idx> 923200000 -17 <delay>`
per burst (loop for 30-60 s via `hardware/ota_iq/replay_driver.py`, recoverable from
git c0e5499^), OR additionally hard-set the defaults in `_init()` and clamp power.

## Toolchain status (BLOCKER for Path B)
- Keil uVision: NOT installed (macOS; Keil is Windows-only). ✗
- arm-none-eabi-gcc: NOT found. ✗
- STM32CubeIDE: NOT installed. ✗
=> The SWDM001/sxlib project cannot be rebuilt on this Mac as-is. Path B requires
   either a Windows+Keil environment or porting the sxlib build to CMake +
   arm-none-eabi-gcc. This is substantially more work than Path A.

## Build / flash (only on a Keil-capable host)
1. Copy `replay_cmd.{c,h}` into `~/Desktop/SWDM001/src/demos/lr11xx_lr_fhss_ping/`.
2. Apply the patch by hand in the Keil editor to `.h`, `.c`, `_sync.c`.
3. Implement `replay_uart_getchar()` bound to the ST-LINK VCP USART.
4. Add `replay_cmd.c` to Keil sources; rebuild.

## === STOP_BEFORE_FLASH ===
5. Flash (gated): `STM32_Programmer_CLI -c port=SWD sn=066CFF3031454D3043073845 mode=UR --download <demo>.bin 0x08000000 --verify` — NO erase/option-byte flags. DO NOT RUN WITHOUT USER CONFIRMATION.
6. Operator checklist identical to Path A (923.2 MHz verified, -17 dBm/lowest, >=50 dB attenuation, no antenna, Board B identity, no USRP yet, explicit authorization).
