# Slides Advisor Revision Report

Date: 2026-07-10

## Scope

- Edited only `paper/slides_overview.tex`.
- Did not edit `paper/icc_main.tex`.
- Did not change paper results or numerical values.
- Did not run experiments, touch hardware, or commit.

## Slides Changed

- Slide 1: retitled to match the final paper:
  "Evidence-Gated Timing/Frequency Control for LR-FHSS Direct-to-Satellite IoT".
- Slide 4: replaced the old workflow with a final-paper architecture diagram:
  Space-Track/TLE -> stale onboard TLE -> SGP4 baseline -> selector/gate ->
  TX timing guard, hop-bin margin, and energy policy.
- Slide 7: replaced the older gate/fallback visual with a clean closed-gate
  diagram for the real BLACK KITE result.
- Slide 8: retitled and labeled as a software-only synthetic sanity check.
- Slides 9-10: kept timing sensitivity and ablation figures, but made the proxy
  boundary explicit in titles, footers, and takeaways.
- Slide 11: revised hardware slide to match paper Table IV framing: conducted
  setup, sanity checklist, and a small spectrum as supporting trace only.
- Slide 12: revised contributions to match the final paper:
  evidence-gated endpoint control; real-data negative control plus synthetic
  gate-open condition; timing/frequency endpoint proxies; bounded conducted-IQ
  sanity evidence.

## Build Status

- Command run: `tectonic paper/slides_overview.tex`
- Build result: success
- Output: `paper/slides_overview.pdf`
- Slide count: 12

Remaining TeX warnings:

- Minor overfull/underfull box warnings on dense Beamer frames.
- Included PDF version warnings for existing figure assets.

## Visual QA

- Rendered all 12 slides with `pdftoppm`.
- Inspected the revised/problem slides and surrounding deck flow.
- Remaining visual issues: none observed that block advisor use. Slide 6 remains
  visually dense but readable; this preserves the existing result figure.

## Claim-Boundary Check

- Synthetic result is labeled software-only and not a real BLACK KITE
  improvement.
- Timing and ablation slides say proxy/not packet result.
- Hardware slide states conducted IQ-level only and excludes packet/PER/PDR/CRC,
  gateway ACK, OTA, live-satellite, and link-layer validation.
- No link-validation or spectrum-as-validation claim was added.
