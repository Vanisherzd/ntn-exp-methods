# Conducted IQ Repeatability Summary

Deterministic LR1121 firmware `lr1121_det_tx_9232_lowpower` 0.1.0, 923.2 MHz / -17 dBm.
Settings: freq 923200000 Hz, rate 4 MS/s, RX gain 20 dB, attenuation 50 dB, channel 0, antenna RX2, off 10 s / on 45 s, TX trigger = serial `S` (command mode).

Conducted IQ-level evidence only. No packet/PER/PDR/CRC/ACK/OTA/satellite claims.

| label | run_dir | TXON-noise (dB) | peak (Hz) | offset (Hz) | max_abs_iq | clip | sat | visible | overflow |
|---|---|---|---|---|---|---|---|---|---|
| canonical_reference | 20260626_003643_gain20_50db | 41.13 | 923238085.9375 | 38085.938 | 0.002888 | False | False | True | 1 |
| repeat_1 | 20260626_010100_gain20_50db | 40.741 | 923238085.9375 | 38085.938 | 0.003263 | False | False | True | 1 |
| repeat_2 | 20260626_011318_gain20_50db | 41.416 | 923466113.28125 | 266113.281 | 0.002829 | False | False | True | 1 |
| repeat_3 | 20260626_012205_gain20_50db | 41.709 | 923466113.28125 | 266113.281 | 0.003276 | False | False | True | 1 |

**TX-ON−TX-OFF delta:** mean 41.249 dB, population stdev 0.358 dB across 4 runs.
**Visibility:** TX-ON visible in every run (delta far above the 6 dB threshold); no clipping/saturation in any run.
**Peak frequency:** alternates between two LR-FHSS hop bins (~+38 kHz and ~+266 kHz from the 923.2 MHz center). This is hop-dependent max-hold peak behavior, consistent with LR-FHSS frequency hopping — a hop-center proxy candidate, NOT a decoded hop sequence.
**Overflow:** each 4 MS/s run logs one benign USB overflow indication (dropped samples); does not affect the TX-ON/TX-OFF spectral result. See `overflow_sanity_summary.md` for the 2 MS/s overflow-free confirmation.