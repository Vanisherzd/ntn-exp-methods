# Validation Status — Ready-to-Paste Text (Slides + Paper)

> Documentation only. The paragraphs below are written for a human to paste into
> `paper/slides_overview.tex` and the paper limitations section. Nothing here was
> auto-applied to the paper or slides.
>
> Scope guardrail: this document describes **receiver-side / bring-up** progress only.
> It deliberately makes **no** claim of RF validation, packet decode, PER/PDR/CRC,
> gateway ACK, satellite link, OTA, or live-satellite validation.

---

## 1. Slide 9 — concise honest status (paste-ready)

> Hardware bring-up has moved to the conducted-IQ stage. The receiver path is
> internally validated: the USRP RX chain and the spectrum-analyzer path were
> verified end-to-end on the receive side. Across the conducted captures taken so
> far — at 60 dB and 50 dB attenuation, with RX gains of 0/10/20, plus a debug
> scan at 922.0 / 923.2 / 924.4 MHz — no LR1121 transmit emission was observed:
> no TX-ON step, no clipping, and no saturation. The remaining blocker is on the
> board side, in deterministic TX / firmware control, not in the USRP or analyzer
> measurement chain. Serial readback from Board B shows its current firmware is
> configured at 868 MHz / 10 dBm, i.e. not the intended Taiwan 923.2 MHz at the
> lowest TX power; Board A's firmware is unresolved and the board is currently
> disconnected. No firmware source tree exists in the repository, so the
> provenance of the 868 MHz / 10 dBm image is external and unknown.

## 2. Paper — limitations / future-work note (paste-ready)

> We report receiver-side and conducted-IQ bring-up results only; we do not claim
> over-the-air or live-satellite validation. The USRP receive chain and the
> spectrum-analyzer path were validated internally, confirming that the
> measurement and capture infrastructure operates correctly. However, no LR1121
> transmit emission was detected in any conducted capture taken to date (60 dB and
> 50 dB attenuation; RX gains 0/10/20; a debug scan at 922.0, 923.2, and
> 924.4 MHz), with no TX-ON transition, clipping, or saturation present in the
> recorded IQ. We attribute this to a board-side limitation in deterministic TX
> and firmware control rather than to the receive measurement chain. Serial
> inspection confirms that the available board firmware is set to 868 MHz / 10 dBm
> rather than the intended 923.2 MHz Taiwan configuration at minimum TX power, and
> no firmware source tree or flashing/control path is present in the repository,
> leaving the image provenance external and unverified. Establishing a
> repeatable, board-side deterministic TX path — and confirming the configured
> frequency and power on the live board — is the prerequisite for any subsequent
> transmit-side or end-to-end RF measurement, and is left to future work.

## 3. Status matrix — validated vs. blocked

**Validated (receiver-side / infrastructure only)**
- USRP RX chain: internally validated.
- Spectrum-analyzer path: internally validated.
- Conducted-IQ capture workflow: operational (TX-ON/TX-OFF spectrum check,
  waterfall check, receiver-chain debug).
- Conducted-IQ bring-up: started.

**Blocked / unresolved (board-side)**
- Deterministic LR1121 TX / firmware control: in progress, not reproducible from
  the repo.
- LR1121 TX emission in conducted captures: not observed (60 dB & 50 dB attn;
  gains 0/10/20; debug scan 922.0 / 923.2 / 924.4 MHz) — no TX-ON, no clipping,
  no saturation.
- Board B firmware config: serial readback = 868 MHz / 10 dBm (NOT Taiwan
  923.2 MHz / lowest TX power). ST-LINK SN 066CFF3031454D3043073845.
- Board A firmware: unresolved; board currently disconnected.
  ST-LINK SN 0670FF3234584D3043215150.
- Firmware provenance: no source tree in repo; 868 MHz / 10 dBm image is
  external / unknown origin.

**Explicitly NOT claimed**
- No RF validation completed.
- No packet decode, no PER / PDR / CRC.
- No gateway ACK, no satellite / OTA / live-satellite link.
