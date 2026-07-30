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

- Run directory: `/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/20260626_003643_gain20_50db`
- Attenuation: `50 dB`
- USRP channel: `0`
- UHD antenna: `RX2`
- RX gain: `20.0 dB`
- Sample rate: `4000000.0 sps`
- Center frequency: `923200000.0 Hz`
- TX control mode: `command`

## Capture files

- TX-OFF: `noise_rx2a_gain20_50db.npy`
- TX-ON: `txon_rx2a_gain20_50db.npy`
- Metadata: `capture_metadata.json`

## TX-ON/TX-OFF spectrum evidence

- noise floor: `-69.460 dB`
- TX-ON peak: `-27.538 dB`
- TX-ON minus TX-OFF: `41.130 dB`
- peak frequency: `923238085.938 Hz`
- peak offset: `38085.938 Hz`
- max_abs_iq: `0.002888`
- clipping_warning: `False`
- saturation_warning: `False`
- TX-ON visible: `True`
- usable for conducted IQ-level evidence: `True`
- CFO / hop-center proxy candidate: `True`
- recommended next step: `TX-ON/TX-OFF spectrum evidence and waterfall evidence are usable at the current setting. This run is a CFO / hop-center proxy candidate.`

## Notes

- `psd_noise.png` and `psd_txon.png` provide TX-ON/TX-OFF spectrum evidence.
- `waterfall_txon.png` provides waterfall evidence.
- This run is limited to conducted IQ-level capture and may support a future CFO / hop-center proxy candidate assessment.
