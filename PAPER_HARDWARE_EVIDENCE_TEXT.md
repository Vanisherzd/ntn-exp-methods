# Paper — Hardware Conducted-IQ Evidence (paste-ready, conservative)

> For a human to paste into the paper. Conducted IQ-level evidence only.
> Forbidden: packet decode, PER/PDR/CRC, gateway ACK, OTA, live-satellite,
> "RF validation completed".

## Short version (one paragraph)

> This preliminary conducted-IQ experiment verifies the measurement path and
> provides a CFO / hop-center proxy candidate. It does not constitute packet-level
> validation or an end-to-end satellite link result. A NUCLEO-L476RG + LR1121 board
> was flashed with a deterministic firmware configured for 923.2 MHz at the lowest
> available transmit power (-17 dBm, Low-Power PA), verified over its serial console
> (configured frequency and power, TX_START → repeated LR-FHSS bursts → TX_DONE).
> Over a conducted, 50 dB-attenuated coaxial path into a USRP B210 (no antenna), the
> transmit-on capture shows a clear emission approximately 41 dB above the
> transmit-off noise floor, peaking within the LR-FHSS hop grid of the target
> channel, with no clipping or saturation.

## Expanded version (methods + results + limitations)

> **Setup.** Board B (NUCLEO-L476RG + Semtech LR1121) was reflashed from a stock
> 868 MHz / 10 dBm demo to a deterministic firmware fixed at 923.2 MHz and the
> lowest LR1121 transmit power (-17 dBm, Low-Power PA). Serial readback confirmed
> the configured frequency and power and a complete transmit window. The RF output
> was routed conductively through 30 dB + 20 dB attenuators (50 dB total) and coax
> into a USRP B210 (RX2 A), with no antenna and no over-the-air path. Each run
> captured a transmit-off (noise) window followed by a transmit-on window.
>
> **Results.** Transmit-on is clearly visible over transmit-off. Across four
> 4 MS/s captures the transmit-on minus transmit-off spectral difference was
> 41.25 ± 0.36 dB (mean ± s.d.), with no clipping or saturation in any run; a 2 MS/s
> control reproduced the result (43.76 dB), confirming the evidence is not an
> artifact of USB streaming. After masking a DC/LO center artifact present in the
> transmit-off capture, the transmit-on emission remains 41.1 dB above transmit-off
> at a genuine hop bin offset from center, i.e. the detection is not the DC/LO
> spike. A before/after negative control with the receive chain held fixed shows the
> pre-reflash 868 MHz firmware produced no visible emission in the 923 MHz span
> (~0.5 dB), isolating the earlier null result to a board-side frequency mismatch
> rather than a receiver fault.
>
> **Limitations.** This is conducted IQ-level spectral evidence of a controlled
> transmission and a CFO / hop-center proxy candidate; the observed spectral peaks
> are hop-center proxy candidates, not a decoded LR-FHSS hop sequence. We make no
> packet-decode, PER/PDR/CRC, link-layer, over-the-air, or satellite claim. Packet
> recovery and link metrics remain future work.

## Evidence types (what we are allowed to show)

The committed hardware evidence is strictly **measurement-path** evidence:

1. **Conducted IQ-level measurement-path evidence.** Board B → 50 dB attenuated
   coax → USRP B210 (no antenna). Verifies the capture/analysis path end to end.
2. **TX-ON / TX-OFF spectrum evidence.** Paired captures; TX-ON emission ~41 dB
   above the TX-OFF noise floor in the analyzed span, with no clipping/saturation.
3. **Waterfall evidence.** Time–frequency (spectrogram/waterfall) of the TX-ON
   capture shows the LR-FHSS burst structure hopping within the target channel's
   grid over the transmit window — qualitative, not a decoded hop sequence.
4. **CFO / hop-center proxy candidate.** The per-burst spectral peaks land at
   hop-grid bin offsets near 923.2 MHz and are reported as a CFO / hop-center
   *proxy candidate* only.

## Claim vocabulary — permitted vs forbidden

**Permitted wording:** "conducted IQ-level measurement-path evidence",
"TX-ON/TX-OFF spectrum evidence", "waterfall / spectrogram evidence",
"CFO / hop-center proxy candidate", "controlled transmission",
"serial-verified configured frequency and power", "no clipping or saturation".

**Forbidden wording (do NOT claim):** packet decoding · PER / PDR · CRC ·
gateway ACK · link-layer success · OTA / over-the-air · live-satellite or
end-to-end satellite link · "full RF validation" / "RF validation completed".
Every hardware sentence must stay at or below the IQ-spectral ceiling.

## Future work (paste-ready)

> Packet-level conducted PER/PDR and authorized OTA validation are left for future work.

## Numbers (for tables / captions)
- Repeatability (4 runs, 4 MS/s): TX-ON − TX-OFF = 41.25 ± 0.36 dB; visible in all.
- 2 MS/s sanity: 43.76 dB, visible, no clip/sat.
- Artifact-masked (canonical run): 41.13 dB at a real hop bin after masking ±5 kHz DC/LO.
- Before/after control: 868 MHz firmware ~0.48 dB (not visible) → 923.2 MHz firmware 41.13 dB (visible).
- Peak frequency: alternates between LR-FHSS hop bins near 923.2 MHz (e.g. +38 kHz, +266 kHz).
