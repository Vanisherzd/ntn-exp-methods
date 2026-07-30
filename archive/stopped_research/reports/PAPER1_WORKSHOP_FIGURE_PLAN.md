# Paper 1 — Workshop Figure Plan

> Figure inventory for the workshop/short version. Each entry lists the source
> script/asset and the one-line claim it supports. Software-only unless marked
> [HW]. No figure may imply packet/PER/OTA/satellite results.

## Core figures

| # | Figure | Source | Supports |
|---|---|---|---|
| F1 | Architecture (predictor → evidence gate → control proxies) | `paper/icc_main.tex` (TikZ) | system framing |
| F2 | Real BLACK KITE negative result (MAE vs staleness; degradation) | `paper/figures/fig_bk_residual.pdf` | **headline**: gate closes 8–168 h |
| F3 | Gate behaviour (open vs closed regimes) | `paper/figures/fig_gate_behavior*.pdf` | when learning is admissible |
| F4 | Timing-offset sensitivity (4-panel) | `experiments/exp7_timing_sensitivity/figures/fig_timing_sensitivity.pdf` | miss/guard/energy vs σ_t and TLE age |
| F5 | Control ablation (4-panel bars) | `experiments/exp8_control_ablation/figures/fig_control_ablation.pdf` | timing+freq+PGRL → ~90% success, ~100× energy |
| F6 | PGRL footprint (table/inset, not a plot) | `experiments/exp9_pgrl_footprint/footprint_report.md` | embeddable: 326 KB int8, 1.07 mJ/inference |
| F7 [HW] | Conducted IQ TX-ON/TX-OFF spectrum | `paper/figures/hardware/…` + `output/conducted_hil/` | controlled transmission, +41 dB |
| F8 [HW] | Waterfall / spectrogram of TX window | conducted-IQ capture (`scripts/analyze_conducted_iq.py`) | hopping burst structure (qualitative) |

## Slide-only / talk figures

- `paper/figures/fig_bk_residual_talk.pdf`, `paper/figures/fig_gate_behavior_talk.pdf`
  — large-font talk variants (already generated).
- `paper/slide_figures/` + `paper/figures/generate_slide_evidence_figures.py`
  — slide evidence figures generator.

## Caption guardrails

- F4/F5 captions must read "software-only guard-coverage / hop-bin-tolerance
  proxy"; F5 PGRL bar labelled "gate-open synthetic regime".
- F7/F8 captions must say "conducted IQ-level", "no antenna", "no clipping/
  saturation", "CFO / hop-center proxy candidate"; **never** packet/PER/OTA.
- F2 caption keeps "software-only, model-derived; no measured Doppler".

## Regeneration

```bash
source .venv/bin/activate
python experiments/exp7_timing_sensitivity/run_timing_sensitivity.py   # F4
python experiments/exp8_control_ablation/run_control_ablation.py       # F5
python experiments/exp9_pgrl_footprint/run_footprint.py                # F6
# F2/F3 + talk variants: paper/figures/generate_slide_evidence_figures.py
```
