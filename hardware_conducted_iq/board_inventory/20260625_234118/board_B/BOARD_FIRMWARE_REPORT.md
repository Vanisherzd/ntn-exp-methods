# Board B Firmware Report

This report covers **read-only board firmware inventory** for **Board B** only.

## What board is connected?

- USB identity shows an **STMicroelectronics STM32 STLink** device with an exposed CDC serial port.
- This is consistent with an STM32 NUCLEO-style board under test.
- The serial output shows an application that prints packet-send status and RF configuration.

USB identity alone does not prove the attached RF path or LR1121 hardware revision, but the serial output confirms that Board B is running firmware that reports RF packet activity.

## ST-LINK serial / USB identity

- USB product: `STM32 STLink`
- USB vendor: `STMicroelectronics`
- ST-LINK serial: `066CFF3031454D3043073845`
- USB serial candidates:
  - `/dev/tty.usbmodem1303`
  - `/dev/cu.usbmodem1303`

Evidence:

- [usb_devices.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/usb_devices.txt:170)
- [serial_ports.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/serial_ports.txt:1)
- [serial_port_candidates.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/serial_port_candidates.txt:1)

## Likely CDC serial port

- Most likely active CDC port: `/dev/cu.usbmodem1303`
- Alternate TTY node: `/dev/tty.usbmodem1303`

Both ports identify the ST-LINK CDC interface for Board B.

## Was a serial boot log captured?

- Yes.
- Read-only serial logging captured readable output at `115200` baud.
- Logs:
  - [serial_boot_log.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/serial_boot_log.txt:1)
  - [serial_boot_log_cu.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/serial_boot_log_cu.txt:1)

Important observation:

- The board was already emitting packet-send logs when the serial logger listened.
- No host TX command was sent.

## Does the boot log mention LR1121?

- No explicit `LR1121` string appears in the captured serial logs.

## Does the boot log mention 923200000?

- No.
- The captured serial output mentions `868000000 Hz`, not `923200000 Hz`.

## Does the boot log mention TX_START / TX_DONE?

- No literal `TX_START` or `TX_DONE` strings appear.
- It does print:
  - `Packet to send: ...`
  - `RF=868000000 Hz, PWR=10 dBm, payload_len=...`
  - `Packet sent!`

Evidence:

- [serial_boot_log.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/serial_boot_log.txt:13)
- [serial_boot_log_cu.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/serial_boot_log_cu.txt:13)

## Did flash dump succeed?

- No.

Reason:

- None of the requested read-only STM32 probe tools are installed on this machine:
  - `st-info`
  - `st-flash`
  - `STM32_Programmer_CLI`
  - `pyocd`
  - `openocd`

Evidence:

- [stlink_probe.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/stlink_probe.txt:1)
- [flash_dump_command.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/flash_dump_command.txt:1)

## Do flash strings mention LR1121?

- Unknown.
- Flash strings are unavailable because no flash dump was produced.

See:

- [board_B_flash_strings.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/board_B_flash_strings.txt:1)

## Do flash strings mention 923200000 / 868000000 / 915000000?

- Unknown from flash strings.
- Serial output does mention `868000000 Hz`.
- Serial output does not mention `923200000` or `915000000`.

## Does any repo firmware artifact match?

- No exact match could be established.
- The repo does not contain a flashable candidate firmware image for hash comparison:
  - no `.bin`
  - no `.elf`
  - no `.hex`
  - no firmware build tree with `Makefile`, `CMakeLists.txt`, or `platformio.ini`

Relevant repo-side artifacts:

- [semtech_validation/lr1121_tx_config_example.json](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/semtech_validation/lr1121_tx_config_example.json:1)
  - contains `center_frequency_hz = 923200000`
  - contains `tx_power_dbm = 0`
- historical UART logs:
  - [local_archive/validation_runs/20260609T135342Z/dryrun_001/tx_uart.log](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/local_archive/validation_runs/20260609T135342Z/dryrun_001/tx_uart.log:1)
  - [local_archive/validation_runs/20260609T135342Z/hw_dryrun_001/tx_uart.log](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/local_archive/validation_runs/20260609T135342Z/hw_dryrun_001/tx_uart.log:1)
  - these resemble Board B's live serial output and show `RF=868000000 Hz, PWR=10.0 dBm`

See:

- [repo_firmware_artifacts.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_234118/board_B/repo_firmware_artifacts.txt:1)

## Is Board B likely correct for LR1121 923.2 MHz conducted TX?

- **Board B is not verified for LR1121 923.2 MHz TX.**
- Based on the captured serial self-report, the currently flashed firmware is likely configured for:
  - `868000000 Hz`
  - `10 dBm`
  - repeated packet-send behavior

This does not match the desired Board B state for the next conducted setup:

- `923200000 Hz`
- lowest available TX power
- deterministic board-side TX timing verification

## Evidence supporting the conclusion

- Board B ST-LINK serial differs from Board A, confirming a different connected board:
  - Board B: `066CFF3031454D3043073845`
  - Board A: `0670FF3234584D3043215150`
- Board B produced readable application serial output at `115200`.
- Board B live serial output reports `RF=868000000 Hz, PWR=10 dBm`.
- No serial output mentions `923200000`.
- No repo-local flashable firmware image was found.
- No flash fingerprint is available.

## What remains unknown?

- Whether the Board B RF chip is LR1121 or another compatible Semtech radio without an explicit boot banner.
- Whether Board B can be configured to `923200000 Hz` without flashing.
- Whether the active physical RF connector matches the intended conducted RF path.
- Whether Board B's current firmware has a safe non-TX query command.
- Whether Board B and the historical UART logs are from the exact same firmware build.

## Current conclusion

- Board B has stronger board-side evidence than Board A because it emits serial RF status.
- Board B is **not verified** for `923200000 Hz` LR1121 conducted TX.
- Board-side TX remains blocked until firmware can be identified, controlled, or replaced under an explicit flashing procedure.
