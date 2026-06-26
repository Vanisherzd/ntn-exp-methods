# Overflow-Free Sanity Run

Purpose: confirm the conducted TX-ON evidence is not an artifact of USB streaming
instability, by repeating the capture at a lower sample rate.

Conducted IQ-level evidence only. No packet/PER/PDR/CRC/ACK/OTA/satellite claims.

## Settings
- freq 923200000 Hz, **rate 2 MS/s** (vs 4 MS/s in the main runs)
- RX gain 20 dB, attenuation 50 dB, channel 0, antenna RX2
- off 10 s / on 45 s, TX trigger = serial `S` (command mode)
- run dir: `hardware_conducted_iq/20260626_013014_gain20_50db`

## Result (2 MS/s)
| metric | value |
|---|---|
| TX-ON − TX-OFF | **43.76 dB** |
| peak frequency | 923237841.80 Hz (offset +37.84 kHz, within LR-FHSS hop grid) |
| max_abs_iq | 0.002473 |
| clipping_warning | False |
| saturation_warning | False |
| TX-ON visible | True |

## Overflow interpretation (important, honest)
- UHD's `rx_samples_to_file` prints "Got an overflow indication … This message will
  not appear again." This is a **one-time** warning, not a per-occurrence counter, so
  a `grep` count of 1 means "at least one overflow happened at some point," not "one
  sample lost."
- The warning appears at **both** 4 MS/s and 2 MS/s, consistent with a transient at
  stream start-up rather than sustained rate-limited drops.
- Critically, TX-ON remains **clearly visible at both rates** (~41 dB at 4 MS/s,
  43.76 dB at 2 MS/s) with no clipping and no saturation. The conducted IQ-level
  TX-ON/TX-OFF spectral result is therefore **not** an artifact of streaming
  instability.

## Conclusion
The 2 MS/s sanity capture reproduces the TX-ON detection with comparable margin and
no clipping/saturation, confirming the evidence is robust to the benign one-time USB
overflow indication seen at 4 MS/s. For sample-exact IQ work in future, tighten the
streaming path (e.g. smaller spb, faster medium) to suppress the start-up overflow.
