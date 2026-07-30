# Paper 1 — Camera-Ready Polish v2 Report

_Build: `tectonic paper/icc_main.tex` — SUCCESS; 0 overfull boxes, 0 undefined
refs/citations. Slides untouched (no slide figure paths affected)._

## Page count

**6 pages including references — hard-6 holds.** Body ends on p. 5 (Conclusion
and Limitations start p. 5, finish top of p. 6); references end with [13] in the
upper right of p. 6.

**Page-6 whitespace: intentional.** The remaining ~half page is reserved for the
real author block (placeholder → real affiliations) and venue headers/copyright
block; no filler text was added per the hard rules.

## Fig. 1 redesign result (workflow chart → communications architecture)

Now a spatial communications-system diagram:

- **Top-left:** Space-Track TLE update service (ground segment); dashed
  "infrequent TLE update" feed into the endpoint.
- **Top-right:** LEO satellite LR-FHSS receiver on a dashed "LEO pass" orbit
  arc.
- **Bottom:** boxed **IoT endpoint** container split by a dashed boundary into a
  green-tinted *control plane* (stale TLE → SGP4 physics baseline —thick blue
  "default"→ selector/fail-safe; residual history/window V → learned candidate
  (orange, dashed, optional) → **Evidence Gate** → G → selector; selector →
  TX timing guard / hop-bin margin / energy policy) and a gray-tinted *data
  plane* (MCU → LR1121 modem).
- **Uplink:** thick blue "LR-FHSS uplink burst" arrow from the modem to the
  satellite.
- Default SGP4 path visually dominant (thick blue); learned branch visibly
  optional (dashed orange through the gate); no equations in boxes; no icons;
  scope footer retained. Caption explains the architecture, not the boxes.

## Fig. 4 redesign result (reframed as measurement-path sanity check)

Two-panel single-column figure (Option A):

- **(a) Conducted measurement path** — schematic: NUCLEO-L476RG + LR1121
  (923.2 MHz / −17 dBm) → 50 dB att. + coax → USRP B210 RX2 A, with italic
  "conducted only — no antenna, no OTA path".
- **(b) TX-ON vs. TX-OFF max-hold** — committed spectrum pixels (verbatim, title
  strip cropped; no re-analysis) with summary box: 41.25 ± 0.36 dB (4 runs @
  4 MS/s); 2 MS/s: 43.76 dB; no clipping/saturation.
- Caption = the recommended "Conducted measurement-path sanity check…
  Conducted IQ-level evidence only, not packet or link validation." wording.
- Sec. V prose already frames it as measurement-path verification; no
  link-validation implication anywhere.

## Fig. 2/3

Unchanged this pass (already academic-titled in v1); regenerated only as a side
effect of the shared generator — numbers identical (read from committed
CSV/JSON).

## Reference audit status (see `PAPER1_REFERENCE_AUDIT.md`)

- **13/13 externally evidenced** — every row now carries a DOI and/or official
  URL (IEEE Xplore, ScienceDirect, arXiv, CelesTrak, 3GPP dynareport + ATIS
  archive PDF, Semtech/Mouser-hosted AN1200.64), the metadata fields checked,
  and the sentence each reference supports.
- Fixes in `refs.bib` (this campaign): [1] vol. 5, pp. 51–63, 2024 + DOI; [8]
  institution → Aerospace Defense Command.
- **Needs human verification (only item):** [7] optional upgrade to the ACM ToSN
  published version (DOI 10.1145/3694971; reportedly vol. 20, no. 6, Art. 117,
  2024) — ACM page 403-blocked to automated fetch, so per policy the verified
  arXiv citation is kept and the bib carries an upgrade note.

## Citation support audit (see `PAPER1_CITATION_SUPPORT_AUDIT.md`)

PASS — all 8 citation groups have concrete source support; no narrowing
required; one cosmetic grouping note recorded (row 4, [2] inside "analyses").

## No-overclaim scan

**PASS** — post-edit scan leaves 2 hits, both negations/future-work ("explicitly
below any packet-level or over-the-air claim"; "Packet-level conducted PER/PDR …
are future work"). Fig. 4 wording is "sanity check" / "conducted IQ-level
evidence", never "RF/link validation".

## Remaining blockers

1. **Author block placeholder** (pre-existing SUBMISSION BLOCKER) — fill and
   re-check the 6-page count (p. 6 slack absorbs it).
2. Optional: human-confirm [7] ToSN metadata and swap the bib entry.
3. Commits still pending (`PAPER1_FINAL_COMMIT_PLAN.md` D–G; E includes
   `paper/refs.bib`, G includes the v2 audits/reports).
