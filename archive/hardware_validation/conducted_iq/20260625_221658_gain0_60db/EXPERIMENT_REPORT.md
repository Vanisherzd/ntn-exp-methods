# Conducted IQ Experiment Report

This report documents a conducted IQ-level capture only.

- Not packet decoding
- Not PER / PDR / CRC / gateway ACK
- Not satellite link validation
- Not live-satellite validation
- Not OTA

## Hardware path

- board: `NUCLEO-L476RG + LR1121`
- RF path: `LR1121 RF port -> 30 dB attenuator -> 20 dB attenuator -> 10 dB attenuator -> SMA coax -> USRP B210 RX2 A`

## Session settings

- Run directory: `/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/20260625_221658_gain0_60db`
- Attenuation: `60 dB`
- USRP channel: `0`
- UHD antenna: `RX2`
- RX gain: `0.0 dB`
- Sample rate: `1000000.0 sps`
- Center frequency: `923200000.0 Hz`
- TX control mode: `manual-countdown`

## Capture files

- TX-OFF: `noise_rx2a_gain0_60db.npy`
- TX-ON: `txon_rx2a_gain0_60db.npy`
- Metadata: `capture_metadata.json`

## TX-ON/TX-OFF spectrum evidence

- noise floor: `-79.037 dB`
- TX-ON peak: `-62.990 dB`
- TX-ON minus TX-OFF: `0.672 dB`
- max_abs_iq: `0.000560`
- clipping_warning: `False`
- saturation_warning: `False`
- TX-ON visible: `False`
- usable for conducted IQ-level evidence: `False`
- CFO / hop-center proxy candidate: `False`
- recommended next step: `TX-ON is too weak at RX gain 0 dB. Continue to the next configured RX gain while keeping 60 dB attenuation.`

## Notes

- `psd_noise.png` and `psd_txon.png` provide TX-ON/TX-OFF spectrum evidence.
- `waterfall_txon.png` provides waterfall evidence.
- This run is limited to conducted IQ-level capture and may support a future CFO / hop-center proxy candidate assessment.
