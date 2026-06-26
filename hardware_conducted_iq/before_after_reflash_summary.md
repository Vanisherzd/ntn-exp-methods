# Before / After Reflash — Negative Control Summary

Conducted IQ-level evidence only. No packet/PER/PDR/CRC/ACK/OTA/satellite claims.

## Setup held constant

USRP B210 RX2 A, channel 0, RX gain 20 dB, attenuation 50 dB, capture center 923.2 MHz, conducted path (no antenna). Only the **board firmware** changed.

| phase | firmware | TXON-noise (dB) | TX-ON visible | run |
|---|---|---|---|---|
| before_reflash | stock SWDM001 868 MHz / 10 dBm | 0.482 | False | `20260625_223023_gain20_50db` |
| after_reflash | lr1121_det_tx_9232_lowpower 923.2 MHz / -17 dBm | 41.13 | True | `20260626_003643_gain20_50db` |

## Interpretation
- **Before reflash:** Board B ran the stock SWDM001 demo transmitting at 868 MHz / 10 dBm. With the USRP listening around 923 MHz, TX-ON − TX-OFF was ~0.48 dB and not visible across RX gains 0/10/20 — no clipping, no saturation. The board WAS transmitting, but ~55 MHz outside the analyzed span.
- **After reflash:** With deterministic 923.2 MHz / -17 dBm firmware, the same receive chain resolves a clear TX-ON at +41.13 dB.
- **Root cause:** frequency mismatch (board TX band vs capture band), NOT a USRP or analyzer failure. The receive chain was correct all along; reflashing the board to 923.2 MHz unblocked the evidence.

This is a negative-control confirmation that the measurement path is sound and the post-reflash TX-ON is a genuine board emission.