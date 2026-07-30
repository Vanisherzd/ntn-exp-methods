# Board A Firmware Report

This report covers **read-only board firmware inventory** for **Board A** only.

## What board is connected?

- USB identity shows an **STMicroelectronics STM32 STLink** device with an exposed CDC serial port.
- This is consistent with an STM32 NUCLEO-style board under test, but USB identity alone does **not** prove:
  - the attached RF board is LR1121,
  - the RF port wiring is correct,
  - the flashed application firmware is the intended LR1121 conducted-TX image.

## What ST-LINK serial / USB identity was detected?

- USB product: `STM32 STLink`
- USB vendor: `STMicroelectronics`
- ST-LINK serial: `0670FF3234584D3043215150`
- USB serial candidates:
  - `/dev/tty.usbmodem1303`
  - `/dev/cu.usbmodem1303`

Evidence:

- [usb_devices.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_232608/board_A/usb_devices.txt:170)
- [serial_ports.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_232608/board_A/serial_ports.txt:1)

## What serial port is likely used?

- Most likely active CDC port: `/dev/cu.usbmodem1303`
- Alternate TTY node: `/dev/tty.usbmodem1303`

Reason:

- Both nodes map to the detected ST-LINK CDC device.
- The `cu.*` device is usually the better active-open endpoint on macOS.

## Was a serial boot log captured?

- A read-only serial logging attempt was run twice:
  - [serial_boot_log.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_232608/board_A/serial_boot_log.txt:1) on `/dev/tty.usbmodem1303`
  - [serial_boot_log_cu.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_232608/board_A/serial_boot_log_cu.txt:1) on `/dev/cu.usbmodem1303`
- Both attempts listened across likely baud rates, including `115200`, and captured **zero bytes**.

## Does the boot log mention LR1121?

- No.
- No serial boot text was captured.

## Does the boot log mention 923200000 Hz?

- No.
- No serial boot text was captured.

## Does the flash strings output mention LR1121?

- No direct answer is available because flash dumping was **not possible** with installed tools.
- Placeholder note recorded in:
  - [board_A_flash_strings.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_232608/board_A/board_A_flash_strings.txt:1)

## Does the flash strings output mention 923200000 / 868000000 / 915000000?

- No direct answer is available because flash dumping was **not possible** with installed tools.

## Does the flash strings output mention TX_START / TX_DONE?

- No direct answer is available because flash dumping was **not possible** with installed tools.

## Was flash dumping successful?

- No.

Reason:

- None of the requested read-only STM32 probe tools are installed on this machine:
  - `st-info`
  - `st-flash`
  - `STM32_Programmer_CLI`
  - `pyocd`
  - `openocd`

Evidence:

- [stlink_probe.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_232608/board_A/stlink_probe.txt:1)
- [flash_dump_command.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_232608/board_A/flash_dump_command.txt:1)

## Which repo firmware artifact, if any, matches the current board flash?

- No exact match could be established.
- The repo does **not** contain a flashable candidate firmware image for comparison:
  - no `.bin`
  - no `.elf`
  - no `.hex`
  - no firmware build tree with `Makefile`, `CMakeLists.txt`, or `platformio.ini`
- Therefore there is no candidate artifact to hash-compare against a board flash dump.

Relevant repo-side evidence found:

- [semtech_validation/lr1121_tx_config_example.json](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/semtech_validation/lr1121_tx_config_example.json:1)
  - contains `center_frequency_hz = 923200000`
  - contains `tx_power_dbm = 0`
- historical UART logs:
  - [local_archive/validation_runs/20260609T135342Z/dryrun_001/tx_uart.log](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/local_archive/validation_runs/20260609T135342Z/dryrun_001/tx_uart.log:1)
  - [local_archive/validation_runs/20260609T135342Z/hw_dryrun_001/tx_uart.log](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/local_archive/validation_runs/20260609T135342Z/hw_dryrun_001/tx_uart.log:1)
  - these logs show repeated `RF=868000000 Hz, PWR=10.0 dBm` and `Packet sent!`

See:

- [repo_firmware_artifacts.txt](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/20260625_232608/board_A/repo_firmware_artifacts.txt:1)

## Is the current Board A firmware likely correct for 923.2 MHz LR1121 conducted TX?

- **Not verified.**
- Current evidence is **insufficient** to treat Board A as confirmed-correct for `923200000 Hz` LR1121 conducted TX.

## What evidence supports that conclusion?

- Board A exposes ST-LINK USB + CDC serial, so the board is physically present and enumerated.
- Two read-only serial boot-log attempts captured **no firmware banner, no frequency print, and no TX self-report**.
- No read-only flash dump was possible because the required probe tools are not installed.
- The repo does not contain an actual flashable firmware image or build tree for Board A.
- The strongest historical repo-side TX logs still point to **`868000000 Hz` at `10.0 dBm`**, not proven `923200000 Hz`.

## What is still unknown?

- Whether Board A is running the intended LR1121 application firmware at all.
- Whether Board A is configured for `923200000 Hz`.
- Whether Board A firmware emits serial logs on a different interface or baud rate.
- Whether Board A can deterministically enter TX with a documented local command.
- Whether the connected RF port is the active transmit path.
- Whether Board A and Board B are running different firmware images.

## Current conclusion

- Board A inventory is complete enough to establish **USB/ST-LINK identity**.
- Board A firmware identity is **still unresolved**.
- The current blocker remains **deterministic LR1121 TX blocker on the board side**, not USRP capture setup.

Do not resume conducted IQ capture until Board A firmware provenance or live self-reporting is clarified.
