# Paper 1 — Finalization Status

_Date: 2026-07-10. Scope: submission-ready workshop manuscript + deck. No new
hardware/RF work; no claim beyond conducted IQ-level._

## READY (done, verified)

| Item | State |
|---|---|
| Manuscript `paper/icc_main.tex` | Rewritten to timing/frequency-uncertainty-aware endpoint-control framing; 8-section story (Intro, Related, Background+System Model, Evidence-Gated Endpoint Control, Evaluation incl. exp7/8/9, **Preliminary Conducted-IQ Evidence**, Limitations & Future Work, Conclusion). Stale "HIL halted as inconclusive" limitation replaced with the real committed conducted-IQ result. **Compiles: 6 pages incl. references, 0 major overfull boxes, refs resolve.** |
| Core sentence | "We transform classical PHY-layer Doppler compensation into timing/frequency uncertainty-aware endpoint control for LR-FHSS D2S IoT under stale orbital information and low-power constraints" — in Introduction; abstract carries the recast framing. |
| Paper figures | 6 finals (architecture TikZ, BK negative, gate vs γ, timing sensitivity, ablation, conducted IQ TX-ON/OFF) in `paper/figures_final/` with `FIGURE_SOURCES.md`; generated figures read committed `results.json` only. |
| Slides `paper/slides_overview.tex` | 12 slides matching the 10-point story; stale "Validation Roadmap" replaced by conducted-IQ **result** slide with visible claim boundary; new timing + ablation slides; deck palette per rules. **Compiles.** |
| No-overclaim scan | PASS — `NO_OVERCLAIM_SCAN.md`; one precautionary rewrite ("End-to-end procedure"→"Per-epoch procedure"). |
| Numerical integrity | No result numbers changed. Tables I/II verbatim; exp7/8/9 and hardware numbers match committed artifacts. |
| Honesty invariants | BLACK KITE result stays **negative** (gate closes everywhere); PGRL separations labelled controlled gate-open **synthetic** regime in abstract, Sec. V-E, Fig. 5 caption, slide 10; hardware stays conducted IQ-level; footprint stays conservative (333,720 params, 0.66 MFLOP, 326 KB int8, <1 KB RAM, ~1.07 mJ **estimate**, offline-train/inference-only, mid-range MCU-class w/ sufficient Flash, no M0 claim). |
| Repo docs | `PAPER1_ARTIFACT_MANIFEST.md`, `PAPER1_REPRODUCIBILITY.md`, `PAPER_BUILD_REPORT.md`, `SLIDES_BUILD_REPORT.md`, this file. |

## BLOCKERS before submission (must do, human)

1. **Author policy** — `icc_main.tex` now uses an anonymous placeholder. If the
   target venue is non-anonymous, replace it with the real author/affiliation
   list before submission.
2. **Commits** — Commits D/E/F/G in `PAPER1_FINAL_COMMIT_PLAN.md` are prepared
   but **not executed** (per instruction).

## OPTIONAL (nice-to-have, not blocking)

- Nudge "TLE 168 h" annotation on Fig. 4 / slide 9.
- Speaker notes for the deck.
- Cosmetic underfull-hbox cleanup (2 paragraphs).
- Add a waterfall thumbnail to the paper if a page frees up (currently referenced
  in text; committed PNG exists).

## Explicitly NOT done (by design)

- No new hardware experiments, no reflash, no USRP capture, no OTA.
- No PER/PDR/CRC/packet/gateway/live-satellite claims anywhere.
- No Paper 2 / Paper 3 work.
