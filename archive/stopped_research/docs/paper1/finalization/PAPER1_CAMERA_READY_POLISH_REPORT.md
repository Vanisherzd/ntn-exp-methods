# Paper 1 — Camera-Ready Polish Report

_Build: `tectonic paper/icc_main.tex` — SUCCESS, 0 overfull boxes, 0 undefined
refs. Slides not rebuilt (no slide figure paths affected)._

## Page count

**6 pages including references — hard-6 still satisfied.** Body ends p. 5;
references end mid-p. 6. Remaining p. 6 whitespace intentionally left (no
filler); it absorbs the real author block when added.

## Fig. 1 redesign (flowchart → communications-system architecture)

Rebuilt as a wide two-column, three-swimlane diagram (in-TeX TikZ):

- **Lane 1 — Orbital / pass context:** Space-Track/TLE history → stale onboard
  TLE → SGP4 propagation → predicted pass timing & Doppler.
- **Lane 2 — Endpoint control plane:** residual history / validation window V →
  learned residual candidate (optional, orange) → **Evidence Gate** (green) →
  selector / fail-safe fallback → uncertainty estimator → outputs (TX timing
  guard · freq. pre-comp / hop-bin margin · energy policy).
- **Lane 3 — LR-FHSS data plane:** IoT endpoint MCU → LR1121 LR-FHSS modem —
  "LR-FHSS uplink burst" → LEO satellite receiver.
- Default path = thick blue "default: physics baseline" (pred → selector);
  learned branch = dashed orange into the gate; gate output = green G;
  control→data drop = dotted "configure" into the modem.
- No equations in boxes; thin 0.5 pt borders; no icons; tinted lane bands with
  rotated lane labels; scope footer "Software/model-derived control; conducted
  IQ evidence reported separately (Sec. V)."
- Caption replaced with the requested system-view caption verbatim.

## Fig. 2 / Fig. 3 changes

- Fig. 2 panel titles now academic: (a) Real-data held-out MAE, (b) Real-data
  degradation, (c) Synthetic gate decision, (d) Synthetic deployed MAE; small
  italic in-axes tags "real BLACK KITE" / "synthetic sanity check"; the
  conversational "all >0: gate closes" annotation removed (caption carries it).
- Fig. 3 unchanged data/layout; slightly smaller titles, slightly larger tick
  labels; "software-only coverage proxies" stays in the caption.
- All regenerated from committed CSV/JSON only — zero numeric change.

## Fig. 4 changes (visual weight)

- Canvas 3.45×2.35 → 3.6×2.6 in, fonts 8→9 pt, inset text enlarged; TeX width
  0.85 → 0.98\columnwidth. Keeps max-hold TX-ON/TX-OFF, 41.25 ± 0.36 dB (4
  runs), no clipping/saturation, 50 dB attenuated coax, and the no-packet/no-OTA
  caption boundary. No waterfall added.

## Reference audit (see `PAPER1_REFERENCE_AUDIT.md`)

- **13/13 VERIFIED against IEEE Xplore / publishers / arXiv / CelesTrak / 3GPP /
  Semtech. No fabricated or unverifiable references.**
- 2 metadata fixes applied: [1] Ullah et al. OJ-COMS → vol. 5, pp. 51–63, 2024,
  DOI added; [8] SPACETRACK Report No. 3 institution → Aerospace Defense
  Command.
- Optional, non-blocking: [7] arXiv preprint now also published in ACM ToSN
  (DOI 10.1145/3694971) — swap only after confirming vol/pages (human check).

## Citation support audit (see `PAPER1_CITATION_SUPPORT_AUDIT.md`)

PASS — all 8 citation groups support their sentences; one harmless soft grouping
noted ([2] inside "analyses"), no overbroad claims.

## No-overclaim scan

**PASS** — re-run post-polish; 2 residual hits, both negation ("explicitly below
any packet-level or over-the-air claim") or future work.

## Remaining blockers before commit/submission

1. **Author block placeholder** (pre-existing SUBMISSION BLOCKER) — fill real
   authors; p. 6 slack absorbs it; re-verify page count after.
2. Optional: [7] ACM ToSN upgrade (needs human metadata confirmation).
3. Commits still pending per `PAPER1_FINAL_COMMIT_PLAN.md` (D–G; commit E now
   also includes `paper/refs.bib` and the audit/polish reports fold into G).
