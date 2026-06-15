# Physics-First Evidence-Gated LR-FHSS D2S Uplink Control

This repository contains the software-only artifacts for the paper:

**Physics-First Evidence-Gated Uplink Control for LR-FHSS Direct-to-Satellite IoT**

The project studies transmitter-side Doppler pre-compensation for LR-FHSS Direct-to-Satellite IoT under stale orbital information. The core idea is a physics-first controller: stale-TLE SGP4 open-loop Doppler compensation is the default, and a learned residual branch is enabled only when a chronological held-out validation window proves that it beats the physics baseline by a margin.

## Scope

This repository is intentionally scoped to the final software-only paper artifacts.

It includes:

- the IEEE paper source under `paper/`
- the final paper figures under `paper/figures/`
- scripts used to reproduce the final evidence-gate figures
- compact evidence tables and audit reports under `docs/review/`
- software-only experiment scripts under `tools/`

It does **not** claim:

- measured Doppler truth
- live-satellite contact
- RF or hardware validation
- standards-compliant LR-FHSS decoding
- PER / BER / CRC / PDR / gateway acknowledgement
- measured power or battery savings

All Doppler references in the paper are model-derived from SGP4-propagated real TLE histories. The BLACK KITE result is a model-to-model inter-TLE residual study, not an RF measurement.

## Main paper

Build the paper with:

```bash
tectonic paper/icc_main.tex
```

The expected output is a six-page IEEE-style manuscript, including references.

## Final reproducibility artifacts

Important files:

```text
paper/icc_main.tex
paper/refs.bib
paper/figures/fig_bk_residual.pdf
paper/figures/fig_gate_behavior.pdf
paper/figures/generate_evidence_gate_figures.py
docs/review/bk_negative_result_compact.csv
docs/review/bk_negative_result_compact.md
docs/review/gate_stress_compact.csv
docs/review/gate_stress_compact.md
docs/review/claim_evidence_matrix.md
docs/review/paper_rewrite_report.md
```

Regenerate the final paper figures with:

```bash
python paper/figures/generate_evidence_gate_figures.py
```

## Claim boundary

The final manuscript is a software-only, model-derived study. Legacy hardware experiments and raw run artifacts are intentionally excluded from this submission-scope branch to avoid implying hardware evidence that the paper does not claim.

## Backup tag

The final six-page paper checkpoint is tagged as:

```text
paper-final-6page-204a053
```
