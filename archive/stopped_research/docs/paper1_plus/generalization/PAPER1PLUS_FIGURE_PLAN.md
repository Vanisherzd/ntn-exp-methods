# Paper 1+ Figure Plan (Phase 9)

Date: 2026-07-27
Status: figure code implemented; no figure rendered (dry run).
All figures carry the scope note: *software-only, model-derived inter-TLE
residuals (`reference_is_measured_truth = false`); not measured RF truth.*

Generator: `experiments/exp14_multisat_generalization_matrix/make_generalization_figures.py`.
It refuses to render below `min_satellites_for_generalization_claim` (default 3,
campaign target 6), so a dry run cannot produce a figure that reads as
multi-satellite evidence.

---

## F1 — Cross-satellite generalization matrix *(headline)*

`fig_cross_satellite_generalization_matrix.pdf/png`

- One panel per staleness (8/24/48/72/96/168 h)
- Rows = **training** satellite, columns = **deployment** satellite
- Diagonal = target-specific, outlined; off-diagonal = cross-satellite transfer
- Cell value = degradation % (positive = learned worse than SGP4)
- Diverging colormap centred at 0, so "learned better" and "learned worse" are
  visually opposite rather than merely different shades
- Gate annotated in-cell: `O` open, `C` closed, `M` mixed across staleness,
  `-` unavailable
- `n/a` printed for cells with insufficient pairs — never blank, never imputed

Reads the whole story at a glance: is the diagonal different from the
off-diagonal, and does the gate track it?

## F2 — Gate decision matrix

`fig_gate_decision_matrix.pdf/png`

Same axes, aggregated over staleness, three-state colormap (closed → mixed →
open). Answers "where would a terminal actually deploy?" without the numeric
clutter of F1. This is the figure for the endpoint-policy argument.

## F3 — Pair-level win-rate matrix

`fig_pair_winrate_matrix.pdf/png`

Fraction of accepted TLE pairs where learned MAE < baseline MAE, per cell.
Distinguishes "loses on average because of a few catastrophic pairs" from
"loses consistently on most pairs" — a distinction the frozen Paper 1 could not
make, because it had no pair-level unit.

## F4 — Reject-threshold sensitivity

`fig_reject_threshold_sensitivity.pdf/png`

Three panels vs threshold (none / 150 / 500 / 1500 / 3000 Hz), one line per
satellite: (a) reject rate, (b) retained residual scale, (c) learnability
(degradation %) with a zero reference line. Panel (c) is the answer to the
"screening manufactured the result" attack; the zero crossing is the whole
point.

## F5 — Gate-objective agreement

`fig_gate_metric_agreement.pdf/png`

Symmetric heatmap of pairwise agreement between the MAE / p95 / p99 / outage /
guard-cost gates over evaluated cells. Disagreement is the finding, not a
defect; no objective is drawn as a reference.

---

## Selection for a Paper 1+ submission

Assuming a 6-page workshop or a short journal note:

| Slot | Figure | Rationale |
|---|---|---|
| Fig. 1 | system/protocol schematic (reuse the Paper 1 architecture figure, re-captioned) | orient the reader; no new work |
| Fig. 2 | **F1** | headline result, whatever the outcome case |
| Fig. 3 | **F4** | pre-empts the strongest reviewer attack |
| Fig. 4 | **F2** or **F5** | F2 if the story is the policy (Cases A/C); F5 if the story is the gate objective (Case B/D) |

F3 goes to backup/appendix unless the win-rate distribution is itself the
finding.

Explicitly **not** planned: any per-satellite learning-curve or model-comparison
leaderboard. The question is whether residual structure is stable enough to
deploy, not which regressor wins.

---

## Style rules

- Colour semantics inherited from the Paper 1 deck: SGP4/physics dark blue
  `#1F4E79`, learned candidate orange `#C46A1A`, gate/safe green `#2E7D32`,
  unsafe red `#B23A3A`, scope/limitation grey `#666666`.
- Positive degradation always means *learned is worse*, in every figure.
- No figure may be emitted from a run whose metadata says `dry_run: true`.
- Every figure keeps the scope note in the footer; it is not optional.
