# Conducted IQ Validation Plan

This directory is reserved for a receive-only conducted IQ validation using:

- `NUCLEO-L476RG + LR1121`
- `USRP B210 RX2 A`
- `UHD channel 0`
- receive antenna `RX2`

## Scope Boundary

This is conducted IQ-level evidence only.

- It is not packet decoding.
- It is not PER / PDR / CRC / gateway ACK.
- It is not live-satellite validation.
- It is not OTA.

## Safety Start State

- LR1121 RF port -> `30 dB + 20 dB + 10 dB` attenuators -> SMA coax -> USRP B210 `RX2 A`
- total attenuation = `60 dB`
- USRP RX gain = `0 dB`
- LR1121 TX power = lowest available (`0 dBm` preferred, `5 dBm` only if required by board firmware)
- capture `TX-OFF` first
- then capture a short `TX-ON` burst
- never use USRP TX
- never use the shared `TX/RX` RF port
- never use UHD channel `1`

## Expected Output Files

When the first manual test is completed, this folder should contain:

- `noise_rx2a_gain0_60db.npy`
- `txon_rx2a_gain0_60db.npy`
- `capture_metadata.json`
- `psd_noise.png`
- `psd_txon.png`
- `maxhold_txon_vs_noise.png`
- `waterfall_txon.png`
- `signal_detection_summary.json`
- `README.md`

## Manual Test Plan

### A. TX-OFF capture

- LR1121 connected through `30 + 20 + 10 dB` attenuators
- LR1121 not transmitting
- USRP B210 `RX2 A`
- UHD `channel 0`
- antenna `RX2`
- gain `0 dB`
- duration `5 s`

Example command:

```bash
uv run scripts/usrp_rx2a_capture.py \
  --freq 923200000 \
  --rate 1000000 \
  --gain 0 \
  --duration 5 \
  --antenna RX2 \
  --channel 0 \
  --out hardware_conducted_iq/20260625_205839/noise_rx2a_gain0_60db.npy \
  --metadata hardware_conducted_iq/20260625_205839/capture_metadata.json
```

### B. TX-ON capture

- same wiring
- same USRP settings
- LR1121 TX power at the lowest available setting
- short burst only
- duration `5-10 s`

Example command:

```bash
uv run scripts/usrp_rx2a_capture.py \
  --freq 923200000 \
  --rate 1000000 \
  --gain 0 \
  --duration 5 \
  --antenna RX2 \
  --channel 0 \
  --out hardware_conducted_iq/20260625_205839/txon_rx2a_gain0_60db.npy \
  --metadata hardware_conducted_iq/20260625_205839/capture_metadata.json
```

## Analysis

After both captures:

```bash
uv run scripts/analyze_conducted_iq.py \
  --noise-iq hardware_conducted_iq/20260625_205839/noise_rx2a_gain0_60db.npy \
  --txon-iq hardware_conducted_iq/20260625_205839/txon_rx2a_gain0_60db.npy \
  --rate 1000000 \
  --freq 923200000 \
  --outdir hardware_conducted_iq/20260625_205839
```

Confirm:

- TX-ON differs visibly from TX-OFF in PSD and waterfall
- no clipping warning
- no broad, flat saturation pattern
- IQ capture looks stable

## Escalation Order If TX-ON Is Too Weak

1. Keep `60 dB` attenuation.
2. Increase USRP RX gain: `0 -> 10 -> 20 dB`.
3. Only if still too weak, remove the `10 dB` attenuator and test `50 dB` total attenuation.
4. Do not test `30 dB`-only attenuation.

## Stop Conditions

If clipping or saturation is detected:

- keep `60 dB` attenuation
- reduce USRP RX gain
- reduce LR1121 TX power
- do not proceed to `50 dB` attenuation
