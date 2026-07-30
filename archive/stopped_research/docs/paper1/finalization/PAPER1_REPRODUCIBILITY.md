# Paper 1 — Reproducibility Guide

> Everything in the manuscript regenerates from committed sources. No hardware
> action is required for the software results; the hardware evidence reproduces
> from archived firmware + scripts (board need not currently hold Paper-1
> firmware).

## 0. Environment

```bash
cd LEO-Hybrid-PGRL
source .venv/bin/activate    # numpy / matplotlib / scipy / torch present
```

Builder: `tectonic` (repo default; latexmk/pdflatex also work).

## 1. Software results

```bash
# Timing sensitivity (Fig. 4 data)
python experiments/exp7_timing_sensitivity/run_timing_sensitivity.py
# Control ablation (Fig. 5 data)
python experiments/exp8_control_ablation/run_control_ablation.py
# PGRL footprint (Sec. V-E numbers)
python experiments/exp9_pgrl_footprint/run_footprint.py
```

Each writes `results.json` with a `_reproducibility` block (script, constants,
limitations). Shared constants: `experiments/paper1_proxy_model.py` (consistent
with exp2/exp3 and the paper's F_tol = 500 Hz proxy). BLACK KITE negative-result
tables regenerate per `docs/review/` reports; evidence-gate figures via
`paper/figures/generate_evidence_gate_figures.py`.

## 2. Paper figures + manuscript

```bash
python paper/figures_final/generate_paper_final_figures.py  # reads committed results.json only
tectonic paper/icc_main.tex                                 # 7 pages incl. references
```

Figure provenance: `paper/figures_final/FIGURE_SOURCES.md`.

## 3. Slides

```bash
tectonic paper/slides_overview.tex                          # 12-slide 16:9 deck
```

## 4. Hardware conducted-IQ evidence

Paper 1 hardware evidence can be reproduced by reflashing the archived
deterministic LR1121 923.2 MHz firmware and rerunning the conducted IQ scripts.
The physical board is **not** required to currently hold the Paper-1 firmware
(it may be reflashed for Paper 2 / Paper 3); reproduction relies on:

- committed firmware source + build/flash README (hardware evidence commits)
- serial verification logs (TX_START → 39 bursts → TX_DONE)
- capture/analysis scripts: `scripts/run_conducted_iq_session.py`,
  `scripts/analyze_conducted_iq.py`, `scripts/analyze_conducted_iq_artifact_masked.py`,
  `scripts/extract_conducted_iq_peaks.py`
- committed run reports/summaries under `hardware_conducted_iq/`

Expected result envelope (committed): TX-ON − TX-OFF = 41.25 ± 0.36 dB (4 runs,
4 MS/s); 43.76 dB at 2 MS/s; artifact-masked 41.1 dB at a hop bin; pre-reflash
868 MHz control ~0.5 dB; no clipping/saturation. Claim ceiling: conducted
IQ-level only.

## 5. Integrity rules

- Never edit `results.json` by hand; rerun the script.
- Figures read committed JSON — regenerating figures cannot change numbers.
- Any new claim must map to a committed artifact (see
  `docs/review/claim_evidence_matrix.md`) and pass `NO_OVERCLAIM_SCAN.md` rules.
