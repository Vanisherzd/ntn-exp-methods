# Board Selection Report

This report compares Board A and Board B for the next **board-side TX verification** step.

No RF capture was run during this inventory work.

## Inventory Records

- Board A report:
  - [20260625_232608/board_A/BOARD_FIRMWARE_REPORT.md](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_232608/board_A/BOARD_FIRMWARE_REPORT.md:1)
- Board B report:
  - [20260625_234118/board_B/BOARD_FIRMWARE_REPORT.md](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/BOARD_FIRMWARE_REPORT.md:1)

## ST-LINK Identity

| Board | ST-LINK serial | Likely CDC port |
| --- | --- | --- |
| Board A | `0670FF3234584D3043215150` | `/dev/cu.usbmodem1303` |
| Board B | `066CFF3031454D3043073845` | `/dev/cu.usbmodem1303` |

The serial numbers differ, so the Board B inventory reflects a physically different connected board.

## Serial Output Status

| Board | Serial output |
| --- | --- |
| Board A | CDC port present, but boot-log capture produced zero bytes across tested baud rates. |
| Board B | CDC port present; readable application output at `115200` baud. |

Board B serial output includes:

- `Packet to send: ...`
- `RF=868000000 Hz, PWR=10 dBm, payload_len=...`
- `Packet sent!`

## Firmware Evidence

| Board | Firmware evidence |
| --- | --- |
| Board A | Firmware unresolved. No serial self-report, no flash dump, no matching repo firmware artifact. |
| Board B | Firmware self-reports packet activity, but reports `868000000 Hz` and `10 dBm`, not `923200000 Hz` and lowest TX power. |

## Flash Fingerprint Status

| Board | Flash fingerprint |
| --- | --- |
| Board A | Not yet taken (board disconnected). |
| Board B | **Captured 2026-06-26 (read-only)**: STM32L476 (ID `0x415`, Rev 4), 1 MB. SHA-256 `c1a7402d6c2429372c57f9cae02e176d7c9b0461c9aae3383be85148a6bc870c`. Dump: `board_B_flash_dump_20260626_001321/board_B_flash_dump.bin`. Strings confirm stock SWDM001 `lr11xx_lr_fhss_ping` demo (`LR11XX-LR-FHSS Ping Init`, `RF=%lu Hz, PWR=%d dBm`). |

Tooling correction: **STM32CubeProgrammer v2.21.0 IS installed** (`STM32_Programmer_CLI` under `/Applications/STMicroelectronics/...`) and was used for the read-only dump (connect-under-reset `--upload`, no erase). `st-info`/`st-flash`/`pyocd`/`openocd` remain absent but are not needed.

## Repo Firmware Artifact Match

No flashable firmware image was found in the repo for either board:

- no `.bin`
- no `.elf`
- no `.hex`
- no firmware build tree with `Makefile`, `CMakeLists.txt`, or `platformio.ini`

Relevant repo-side artifacts are config/log evidence only:

- `semtech_validation/lr1121_tx_config_example.json` contains `923200000` and `tx_power_dbm = 0`.
- Historical UART logs show `868000000 Hz` and `10.0 dBm`.
- Board B live serial output resembles the historical `868000000 Hz` logs.

## Which board is safer to use next?

For **non-RF board-side debugging**, Board B is the better next target because it emits readable serial status.

For **923.2 MHz LR1121 conducted TX**, neither board is verified:

- Board A firmware is unresolved.
- Board B firmware appears to be configured for `868000000 Hz` and `10 dBm`.

## Is either board verified for 923.2 MHz LR1121 TX?

- Board A: **not verified**
- Board B: **not verified**

## Recommended Next Step

Resolve the board-side firmware path before any conducted capture:

- identify the firmware source or binary provenance for Board B,
- determine whether Board B has a documented safe non-TX query command,
- establish a deterministic way to configure or confirm `923200000 Hz`,
- establish a deterministic way to confirm lowest available TX power,
- only then decide whether a controlled firmware update is needed.

Current blocker:

- board-side TX remains blocked for `923200000 Hz` LR1121 testing **until an authorized reflash**.

Update 2026-06-26: a deterministic 923.2 MHz / -17 dBm TX firmware (Path A,
RadioLib) is prepared and **build-verified** at
`firmware_patches/deterministic_lr1121_9232_lowpower/`. Flash is gated — see
`HARDWARE_BRINGUP_MASTER_REPORT.md` and `FIRMWARE_UNBLOCK_DECISION.md`.
