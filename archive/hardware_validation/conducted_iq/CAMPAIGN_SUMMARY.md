# Conducted IQ Evidence Campaign — Summary

**Date:** 2026-06-26
**Scope:** conducted IQ-level evidence ONLY. No packet decoding, PER/PDR/CRC, gateway
ACK, OTA, or live-satellite validation. No full RF-link validation claim.

## What was established
A NUCLEO-L476RG + Semtech LR1121 board (Board B) was reflashed from a stock
868 MHz / 10 dBm demo to a deterministic firmware fixed at **923.2 MHz / -17 dBm**
(Low-Power PA). Over a conducted, 50 dB-attenuated coax path (no antenna) into a
USRP B210 (RX2 A), the transmit-on capture shows a clear emission ~41 dB above the
transmit-off noise floor at the target channel.

## Evidence pillars
1. **Serial verification** — configured frequency 923200000 Hz, power -17 dBm,
   `INIT beginLRFHSS code 0`, `TX_START` → 39 LR-FHSS bursts → `TX_DONE`.
2. **Repeatability** (4 runs, 4 MS/s) — TX-ON−TX-OFF = **41.25 ± 0.36 dB**, visible in
   every run, no clipping/saturation. (`repeatability_summary.md/.csv`)
3. **Overflow-free sanity** (2 MS/s) — **43.76 dB**, visible, confirming the result is
   not a USB-streaming artifact. (`overflow_sanity_summary.md`)
4. **Artifact masking** — after masking the ±5 kHz DC/LO center spike, TX-ON stays
   **41.13 dB** above TX-OFF at a genuine hop bin → the detection is the board, not the
   artifact. (`20260626_003643_gain20_50db/artifact_masked_signal_detection_summary.json`)
5. **Hop-center proxy peaks** — 8 spectral peaks extracted from the TX-ON max-hold after
   baseline removal, 47+ dB excess, none present in TX-OFF; hop-center proxy candidates,
   NOT a decoded hop sequence. (`…/hop_center_peak_table.csv`)
6. **Before/after negative control** — same RX chain: pre-reflash 868 MHz firmware gave
   ~0.48 dB (not visible); post-reflash 923.2 MHz gave 41.13 dB. Root cause of the earlier
   null = board frequency mismatch, not a receiver fault. (`before_after_reflash_summary.md`)

## Peak-frequency behavior
The max-hold peak alternates between LR-FHSS hop bins near 923.2 MHz (e.g. +38 kHz,
+266 kHz, and on the canonical run −369 kHz after artifact masking), consistent with
frequency hopping. Reported as hop-center proxy candidates only.

## Claim boundary (explicit)
Allowed: conducted IQ-level capture, TX-ON/TX-OFF spectrum evidence, waterfall evidence,
CFO / hop-center proxy candidate. NOT claimed: packet decode, PER/PDR/CRC, gateway ACK,
OTA, satellite / live-satellite link, "RF validation completed".

## Future work
Packet-level conducted PER/PDR and authorized OTA validation are left for future work.

See `MANIFEST.md` for the full file inventory and commit-safe vs raw classification.
