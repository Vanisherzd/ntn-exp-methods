# LR1121 Board TX Status

## Current Status

Deterministic LR1121 TX control is **not yet reproducible from this repo alone**.

What is present:

- [semtech_validation/lr1121_tx_config_example.json](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/semtech_validation/lr1121_tx_config_example.json)
  - user-facing example config
  - currently set to:
    - `center_frequency_hz = 923200000`
    - `tx_power_dbm = 0`
- historical UART logs under [hardware/captures](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware/captures) and [local_archive/validation_runs](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/local_archive/validation_runs)
  - examples contain lines like:
    - `RF=868000000 Hz, PWR=10.0 dBm, payload_len=12`
    - `Packet sent!`
- historical sweep summaries that explicitly note:
  - `firmware_tx_reported_but_no_rf_detected`
  - `signal_detected`
  - `weak_signal_candidate`

What is not present:

- no firmware source tree for the NUCLEO-L476RG + LR1121 board
- no board build instructions
- no upload/flash script
- no serial-console TX control script
- no repo-local command that deterministically starts or stops LR1121 TX
- no repo-local command that proves the live board is configured at `923200000 Hz`
- no repo-local command that prints:
  - `configured_frequency_hz`
  - `tx_power_dbm`
  - `tx_start_timestamp`
  - `tx_done_timestamp`

## Evidence Found

1. Historical UART output exists, but only as logs.
   - Example files:
     - [local_archive/validation_runs/20260609T135342Z/dryrun_001/tx_uart.log](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/local_archive/validation_runs/20260609T135342Z/dryrun_001/tx_uart.log)
     - [local_archive/validation_runs/20260609T135342Z/hw_dryrun_001/tx_uart.log](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/local_archive/validation_runs/20260609T135342Z/hw_dryrun_001/tx_uart.log)
   - These logs show repeated TX attempts at `868000000 Hz` and `10 dBm`.

2. Historical 923 MHz sweep summaries exist.
   - Example:
     - [hardware/captures/auto_sweep_20260603_231940/sweep_summary.csv](/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware/captures/auto_sweep_20260603_231940/sweep_summary.csv)
   - This shows `923000000 Hz` entries with notes such as `firmware_tx_reported_but_no_rf_detected` and `noise_floor_only`.

3. No code path in the repo emits the UART lines above.
   - A repo search for `Packet to send`, `Packet sent`, and the historical `RF=... Hz, PWR=... dBm` strings found logs only, not source code.

## Practical Meaning

The current conducted IQ workflow can verify the receive chain and record IQ, but it cannot yet guarantee that LR1121 TX was actually commanded on the live board during the intended capture window.

That is why the recent `60 dB` and `50 dB` conducted IQ sessions should be treated as:

- conducted IQ bring-up
- TX-ON/TX-OFF spectrum check
- waterfall check
- receiver-chain debug

and not as deterministic LR1121 TX verification.

## Next Required Board-Side Capability

To unblock deterministic bring-up, the repo needs one of the following:

1. A board control script or executable that:
   - sets frequency to `923200000 Hz`
   - sets LR1121 TX power to the lowest available setting
   - starts repeated TX for `30-60 s`
   - stops TX on command
   - prints serial status lines with timestamps

2. A documented firmware build + flash + serial-control path that can be run from this repo.

Until that exists, the board-side state remains a bring-up blocker.
