# Conducted IQ Debug Report

This report documents receiver-chain debug only.

- conducted IQ bring-up
- TX-ON/TX-OFF spectrum check
- waterfall check
- receiver-chain debug
- LR1121 TX timing verification

## Configuration

- run directory: `/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/20260625_224417_debug_scan_50db/f922000000_gain20_50db`
- center frequency: `922000000 Hz`
- sample rate: `4000000 sps` if unchanged from the scan command, otherwise see summary JSON
- RX gain: `20.0 dB`
- attenuation: `50 dB`
- RF path: `LR1121 RF port -> 30 dB attenuator -> 20 dB attenuator -> SMA coax -> USRP B210 RX2 A`

## Summary

- TX-ON minus TX-OFF: `0.205 dB`
- peak_frequency_hz: `921999511.719`
- noise_peak_frequency_hz: `921999511.719`
- max_abs_iq: `0.001455`
- clipping_warning: `False`
- saturation_warning: `False`
- visible_txon: `False`
- likely_artifact_warning: `True`

## Notes

- `psd_noise.png` and `psd_txon.png` provide the TX-ON/TX-OFF spectrum check.
- `waterfall_txon.png` provides the waterfall check.
- This report does not make any packet, link-layer, OTA, or live-satellite claim.
