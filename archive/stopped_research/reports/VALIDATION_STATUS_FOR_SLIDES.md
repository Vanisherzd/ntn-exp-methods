# Validation Status — Ready-to-Paste Text (Slides + Paper)

> Documentation only. The paragraphs below are written for a human to paste into
> `paper/slides_overview.tex` and the paper limitations section. Nothing here was
> auto-applied to the paper or slides.
>
> Scope guardrail: this document describes **receiver-side / bring-up** progress only.
> It deliberately makes **no** claim of RF validation, packet decode, PER/PDR/CRC,
> gateway ACK, satellite link, OTA, or live-satellite validation.

---

## 1. Slide 9 — "Conducted IQ bring-up result" (paste-ready)

> **Conducted IQ bring-up result**
> - Board B reflashed from the 868 MHz stock demo to a deterministic 923.2 MHz / -17 dBm conducted-TX firmware (serial-verified: configured frequency + power, TX_START → 39 LR-FHSS bursts → TX_DONE).
> - TX-ON is clearly visible over TX-OFF: **+41.13 dB** on the canonical run; **41.25 ± 0.36 dB** across four repeat captures; **43.76 dB** on a 2 MS/s overflow-sanity control.
> - Peak near **923.238 MHz** (within the LR-FHSS hop grid); after masking the DC/LO artifact, TX-ON stays 41 dB above TX-OFF at a real hop bin — the signal is the board, not the artifact.
> - Negative control: pre-reflash 868 MHz firmware gave ~0.5 dB (not visible) with the same RX chain — the earlier null was a board frequency mismatch, not a receiver fault.
> - No clipping or saturation in any run.
> - **Claim boundary:** conducted IQ only; no packet decoding, PER/PDR/CRC/gateway ACK, OTA, or live-satellite validation.
> - **Future work:** packet-level conducted PER/PDR and authorized OTA validation are left for future work.

## 2. Paper — limitations / future-work note (paste-ready)

> We report receiver-side and conducted-IQ bring-up results only; we do not claim
> over-the-air, packet-level, or live-satellite validation. The USRP receive chain
> and spectrum-analyzer path were validated internally. We then built and flashed a
> deterministic LR1121 transmit firmware on the NUCLEO-L476RG board, configured for
> the 923.2 MHz Taiwan channel at the lowest available TX power (-17 dBm, Low-Power
> PA); serial readback confirmed the configured frequency and power and a complete
> transmit window. A conducted capture over a 50 dB attenuated coaxial path (no
> antenna) into a USRP B210 resolved a TX-ON emission approximately 41 dB above the
> TX-OFF noise floor, peaking within the LR-FHSS hop grid of the target channel,
> with no clipping or saturation. We emphasize that this is conducted IQ-level
> spectral evidence of a controlled transmission, not a decoded-packet, PER/PDR, or
> end-to-end link result. An earlier set of conducted captures saw no emission
> because the board then ran a stock 868 MHz firmware, roughly 55 MHz outside the
> analyzed 923 MHz span; reflashing to the 923.2 MHz configuration resolves this.
> Packet-level decoding, link metrics, and any over-the-air or satellite
> measurement remain future work.

## 3. Status matrix — validated vs. blocked

**Validated / achieved**
- USRP RX chain: internally validated.
- Spectrum-analyzer path: internally validated.
- Conducted-IQ capture workflow: operational.
- Deterministic LR1121 TX firmware: built, flashed (Board B), serial-verified at
  923.2 MHz / -17 dBm (TX_START → 39 LR-FHSS bursts → TX_DONE, INIT code 0).
- Conducted IQ-level TX-ON evidence: TX-ON visible, +41.13 dB over TX-OFF noise,
  peak ~923.24 MHz, no clipping/saturation (run `20260626_003643_gain20_50db`).

**Open / future work**
- Board A firmware: unresolved; board currently disconnected.
  ST-LINK SN 0670FF3234584D3043215150.
- Packet-level decode, PER/PDR/CRC, link metrics: not attempted.
- OTA / satellite measurement: not attempted.
- Minor: one USRP USB overflow (dropped samples) at 4 MS/s during capture —
  benign for the TX-ON/TX-OFF spectral result; tighten streaming for sample-exact
  work.

**Explicitly NOT claimed**
- No RF validation completed (in the link-layer sense).
- No packet decode, no PER / PDR / CRC.
- No gateway ACK, no satellite / OTA / live-satellite link.

(Board B identity: ST-LINK SN 066CFF3031454D3043073845. Firmware now
`lr1121_det_tx_9232_lowpower` 0.1.0, replacing the prior stock 868 MHz / 10 dBm
SWDM001 demo.)

---

## 4. Software gap closure — slide status (paste-ready)

> **Software-only control analyses (no hardware involved)**
> - **Timing-offset sensitivity (exp7):** residual timing σ_t and TLE staleness
>   (8–168 h) sized the guard and the per-burst energy; energy per successful
>   burst rises ~10 mJ → ~246 mJ as σ_t grows 16 ms → 2 s, while the 3σ-guard miss
>   rate stays ≈0.3%. Stale timing is paid in reserved guard energy.
> - **Timing / frequency / PGRL ablation (exp8):** joint success climbs
>   no-control 0.03% → SGP4 timing+frequency 15.8% → +PGRL **90.4%**; energy per
>   successful burst falls **25.7 J → 11.2 mJ** (~100× over SGP4 timing+freq).
> - **PGRL footprint (exp9):** **333,720** params, **0.66 MFLOP/inference**,
>   **≈326 KB** int8 Flash, **<1 KB** RAM; offline-trained, **endpoint
>   inference-only**; MCU-class feasible when sufficient Flash is available (no
>   M0-class claim without on-device validation). Estimated inference ≈ **6.4%** of
>   one LR-FHSS burst's TX draw (≈0.3% per pass) — bounded, and outweighed by
>   avoiding missed/repeated transmissions. MCU energy is an estimate, not measured.
> - **Claim boundary:** these are software-only guard-coverage / hop-bin-tolerance
>   proxies, **not** measured LR-FHSS packet outcomes. The PGRL separation is the
>   gate-open synthetic regime; the real-data headline remains the BLACK KITE
>   negative result (the evidence gate closes — learning does not beat SGP4).

## 5. Reproducibility note (Paper 1 hardware)

> Paper 1 hardware evidence can be reproduced by reflashing the archived
> deterministic LR1121 923.2 MHz firmware and rerunning the conducted IQ scripts.
> The physical board is **not** required to currently hold the Paper-1 firmware;
> reproduction relies on the committed firmware source, build/flash README, serial
> logs, reports, and figures. The board may be reflashed for Paper 2 / Paper 3.
