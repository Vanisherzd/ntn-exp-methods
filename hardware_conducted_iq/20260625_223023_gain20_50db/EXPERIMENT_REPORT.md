# Conducted IQ Experiment Report

This report documents a conducted IQ-level capture only.

- Not packet decoding
- No link-layer outcome claim
- No end-to-end link claim
- No live-satellite claim
- Not OTA

## Hardware path

- board: `NUCLEO-L476RG + LR1121`
- RF path: `LR1121 RF port -> 30 dB attenuator -> 20 dB attenuator -> SMA coax -> USRP B210 RX2 A`

## Session settings

- Run directory: `/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/20260625_223023_gain20_50db`
- Attenuation: `50 dB`
- USRP channel: `0`
- UHD antenna: `RX2`
- RX gain: `20.0 dB`
- Sample rate: `1000000.0 sps`
- Center frequency: `923200000.0 Hz`
- TX control mode: `manual-countdown`

## Capture files

- TX-OFF: `noise_rx2a_gain20_50db.npy`
- TX-ON: `txon_rx2a_gain20_50db.npy`
- Metadata: `capture_metadata.json`

## TX-ON/TX-OFF spectrum evidence

- noise floor: `-75.006 dB`
- TX-ON peak: `-59.547 dB`
- TX-ON minus TX-OFF: `0.482 dB`
- peak frequency: `923199633.789 Hz`
- peak offset: `-366.211 Hz`
- max_abs_iq: `0.000780`
- clipping_warning: `False`
- saturation_warning: `False`
- TX-ON visible: `False`
- usable for conducted IQ-level evidence: `False`
- CFO / hop-center proxy candidate: `False`
- recommended next step: `TX-ON is still weak after RX gain 20 dB at 50 dB attenuation. Likely next debug targets: LR1121 not actually transmitting during capture; wrong RF port; firmware TX frequency mismatch; TX timing missed the capture window; or rx_samples_to_file sample format / antenna / tuning issue.`

## Notes

- `psd_noise.png` and `psd_txon.png` provide TX-ON/TX-OFF spectrum evidence.
- `waterfall_txon.png` provides waterfall evidence.
- This run is limited to conducted IQ-level capture and may support a future CFO / hop-center proxy candidate assessment.
