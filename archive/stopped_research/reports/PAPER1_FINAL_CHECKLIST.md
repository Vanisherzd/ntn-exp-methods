# Paper 1 — Final Checklist (scope + reproducibility)

> Pre-submission gate. Every box must hold before the camera-ready. Software-only
> claims and the conducted-IQ hardware ceiling are non-negotiable.

## 1. Claim ceiling (must ALL be true)

- [x] No packet decoding claim anywhere.
- [x] No PER / PDR / CRC claim.
- [x] No gateway ACK / link-layer success claim.
- [x] No OTA / over-the-air claim.
- [x] No live-satellite / end-to-end satellite link claim.
- [x] No "full RF validation" / "RF validation completed" claim.
- [x] Hardware sentences stay at conducted IQ-level measurement-path evidence.
- [x] PGRL proxy separations always labelled "gate-open synthetic regime".

## 2. Empirical headline integrity

- [x] Central result is the **negative** BLACK KITE finding (gate closes,
      8–168 h, target-specific + cross-satellite).
- [x] `reference_is_measured_truth = false` stated for the inter-TLE residual.
- [x] Staleness described as historical-TLE / SGP4-derived, **not Gaussian drift**
      (`docs/TLE_AGING_METHODOLOGY.md`).

## 3. Software analyses present + reproducible

| Item | Script | Output | Status |
|---|---|---|---|
| Timing-offset sensitivity | `experiments/exp7_timing_sensitivity/run_timing_sensitivity.py` | `results.json`, `figures/fig_timing_sensitivity.{pdf,png}` | [x] runs |
| Control ablation (5-way) | `experiments/exp8_control_ablation/run_control_ablation.py` | `results.json`, `figures/fig_control_ablation.{pdf,png}` | [x] runs |
| PGRL footprint | `experiments/exp9_pgrl_footprint/run_footprint.py` | `results.json`, `footprint_report.md` | [x] runs |
| Shared proxy model | `experiments/paper1_proxy_model.py` | constants from exp2/exp3 | [x] |

- [x] All three import shared constants from `experiments/paper1_proxy_model.py`
      (consistent with exp2/exp3 and icc_main.tex §V).
- [x] Each `results.json` carries `_reproducibility` + `limitations`.

## 4. Key numbers locked (regenerate to verify)

- PGRL: **333,720** params · **332,288** MACs · **0.66** MFLOP/inference ·
  **≈326 KB** int8 Flash · **<1 KB** RAM · **~1.07 mJ**/inference (estimated, not
  measured on-device). MCU-class feasible with sufficient Flash; no M0-class claim.
- Ablation joint success: no-control 0.03% → timing+freq(SGP4) 15.8% →
  +PGRL **90.4%**; energy/success **25.7 J → 11.2 mJ**.
- Timing sweep: energy/success **~10 mJ → ~246 mJ** as σ_t 16 ms → 2 s.
- PGRL inference = **6.4%** of one LR-FHSS burst TX-draw, **0.3%** per pass.

## 5. Hardware evidence committed (Paper 1 reproducibility)

- [x] Deterministic LR1121 923.2 MHz / −17 dBm firmware **source** committed.
- [x] Build/flash README committed.
- [x] Serial verification logs (TX_START → bursts → TX_DONE) committed.
- [x] Conducted IQ TX-ON/TX-OFF + repeatability + artifact-mask + before/after
      control reports + figures committed.
- [x] Does **not** require the physical board to currently hold Paper-1 firmware
      (board may be reflashed for Paper 2/3).
- [x] Reproducibility note present (reflash archived firmware + rerun IQ scripts).

## 6. Docs cross-checked

- [x] `PAPER1_REVISED_CORE_TEXT.md` — paste-ready core paragraphs.
- [x] `PAPER1_WORKSHOP_FIGURE_PLAN.md` — figure list + sources.
- [x] `VALIDATION_STATUS_FOR_SLIDES.md` — slide status incl. software gap closure.
- [x] `PAPER_HARDWARE_EVIDENCE_TEXT.md` — permitted/forbidden vocabulary.
- [x] `docs/TLE_AGING_METHODOLOGY.md` — staleness methodology.
