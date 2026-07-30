# No-Overclaim Scan (Paper 1 finalization)

## Method

```bash
grep -niE "PER|PDR|packet|CRC|ACK|OTA|live.satellite|RF validation|end-to-end|decoded|gateway" \
  paper/icc_main.tex paper/slides_overview.tex
```

Rule: these terms are allowed **only** in limitations, future work, claim-boundary
statements, "not claimed" negations, or descriptions of *prior* work. Any positive
claim using them requires rewrite.

## paper/icc_main.tex — verdict per occurrence class

| Location (context) | Terms | Verdict |
|---|---|---|
| Abstract, closing sentence | link-layer, over-the-air, live-satellite | **allowed** — explicit "no … result is claimed" |
| Contribution bullet 5 | packet-level, over-the-air | **allowed** — "explicitly below any packet-level or over-the-air claim" |
| §II Related Work | "packet-trace receiver studies" | **allowed** — describes prior art, not our claim |
| Fig. 1 footnote (TikZ) | live-satellite, RF | **allowed** — scope note "no … claim" |
| §IV-C proxies | packet-delivery, packet-error, packet-recovery, gateway search-window | **allowed** — all "not a measured …" negations |
| §IV-D | "End-to-end procedure" heading | **rewritten** → "Per-epoch procedure" (was the controller loop, not a link claim, but could misread) |
| §V-E | "not measured LR-FHSS packet outcomes" | **allowed** — negation |
| §VI Conducted-IQ | "does not constitute packet-level validation or an end-to-end satellite link result"; "not a decoded hop sequence"; "make no packet-decode, PER/PDR/CRC, link-layer, over-the-air, or satellite claim"; "packet-level conducted metrics and authorized over-the-air validation remain future work" | **allowed** — claim boundary + future work |
| Fig. 6 caption | "no packet decode or over-the-air claim" | **allowed** — negation |
| §VII Limitations | PER, BER, CRC, PDR, gateway acknowledgement, decoded, over-the-air, RF validation | **allowed** — limitations section, all negated |
| §VIII Conclusion | "packet-level conducted metrics and authorized over-the-air validation are future work" | **allowed** — future work |

## paper/slides_overview.tex — verdict per occurrence

| Slide | Text | Verdict |
|---|---|---|
| 1 (title) | "no RF, packet, or live-satellite validation is claimed" | **allowed** — scope line |
| 9 (timing) | "not a measured packet outcome" | **allowed** — proxy label |
| 11 (conducted IQ) | "Claim boundary: … no packet decoding, no PER/PDR/CRC, no gateway ACK, no OTA, no live-satellite validation" | **allowed** — visible claim boundary (required) |

## Rewrites performed

1. `icc_main.tex` §IV-D: "End-to-end procedure (compact)" → "Per-epoch procedure
   (compact)" — precautionary; the paragraph describes the control loop, not a
   satellite link.

## Result

**PASS.** After the one precautionary rewrite, zero positive overclaims remain in
paper or slides. Every risky-term occurrence is a negation, a limitation, a
future-work statement, a claim boundary, or a description of prior work.
Supporting docs (`PAPER_HARDWARE_EVIDENCE_TEXT.md`, `VALIDATION_STATUS_FOR_SLIDES.md`)
carry the same permitted/forbidden vocabulary.

## Re-scan after academic-polish pass (title/figure/caption/compression edits)

Re-ran the same grep over `paper/icc_main.tex` (21 hits) and
`paper/slides_overview.tex` (3 hits). Every hit is a negation ("no packet-decode,
PER/PDR/CRC…", "not packet-level validation or an end-to-end satellite link
result", "no over-the-air claim"), a limitations/future-work statement, or a
prior-work description ("packet-trace receiver studies"). New composite figure
captions carry the required markers (software-only proxy / synthetic sanity
check / conducted IQ-level only). **PASS — unchanged.**
