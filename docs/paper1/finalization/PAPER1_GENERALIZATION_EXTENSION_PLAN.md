# Paper 1 Generalization Limitation and Extension Plan

Date: 2026-07-11

## Current Limitation

Paper 1 uses real Space-Track TLE history for BLACK KITE-1 and BLACK KITE-2.
That is enough to establish a real-data negative control: under strict
chronological validation, the learned residual does not beat the SGP4 stale-TLE
baseline for the tested BLACK KITE conditions.

It is not enough to prove constellation-wide generalization. Two satellites from
one operating family cannot establish that a learned residual model will transfer
across other spacecraft, orbital regimes, tracking cadences, drag environments,
or TLE update behaviors.

This is not a failure of the Evidence Gate story. It is the motivation for the
gate. Paper 1 should be framed as local chronological deploy/no-deploy
validation, not train-once-deploy-everywhere generalization. The Evidence Gate
asks whether a candidate learned residual earns deployment on a recent held-out
window for the target operating condition. If not, the endpoint keeps the SGP4
physics baseline.

## Framing Guidance

- Claim: real BLACK KITE evidence shows always-on residual learning is unsafe in
  the tested setting.
- Claim: the gate closes on the tested real data and opens only in a controlled
  synthetic systematic regime.
- Do not claim: constellation-wide transfer, universal learned residual
  usefulness, measured Doppler truth, packet/link validation, or deployment
  validation.
- Preferred framing: local chronological validation is the safety mechanism; poor
  cross-satellite transfer is a reason to gate, not a reason to abandon the
  method.

## Experiment 10 - Cross-Satellite Transfer Matrix

Goal: quantify whether residual models trained on one satellite transfer to
another, and whether the Evidence Gate blocks unsupported transfer.

Design:

- Rows: train satellite.
- Columns: test satellite.
- Each cell uses the same stale-TLE pairing, feature construction, chronological
  split, and gate rule as Paper 1.
- Include diagonal cells for target-specific training/testing and off-diagonal
  cells for transfer.

Report per cell:

- SGP4 baseline MAE.
- Learned residual MAE.
- Degradation percentage.
- Gate decision.

Primary output:

- Heatmap of learned-vs-baseline degradation or improvement.
- Gate overlay: open/closed marker per cell.
- Separate heatmaps by stale-TLE age band if page budget allows in a future
  paper.

Expected interpretation:

- Transfer cells where ML worsens the baseline should close.
- Any open transfer cell should require held-out evidence, not assumed
  constellation similarity.

## Experiment 11 - Gate Closure Under Domain Shift

Goal: measure how often the gate protects against learned residuals under
increasing domain shift.

Groups:

- Same satellite.
- Same constellation.
- Different constellation.
- Different altitude/inclination.
- Stale TLE age bands.

Report:

- Gate open rate.
- Gate close rate.
- False-open risk.
- Learned-worse rate.
- Optional: learned-better-but-gate-closed rate as a conservatism cost.

Primary output:

- Grouped bar chart or table of open/close rates and learned-worse rates.
- Risk plot versus domain-shift category and stale-TLE age.

Expected interpretation:

- A useful gate should close more often as domain shift increases unless there is
  direct held-out evidence of a transferable residual.

## Experiment 12 - Failure Taxonomy

Goal: explain why learned residual transfer fails or succeeds.

Taxonomy axes:

- Drag / B* mismatch.
- Orbital phase mismatch.
- Altitude / inclination mismatch.
- Maneuver-like TLE updates.
- Training-data sparsity.

Analysis:

- Cluster failed transfer cases by orbital and TLE-update metadata.
- Compare residual sign/shape stability across train/test satellites.
- Identify whether failures are noise-dominated, phase-shifted, biased, or sparse.

Primary output:

- Failure taxonomy table with representative cases.
- Residual-shape examples for each failure mode.
- Guidance for when the gate should be expected to close.

## Future-Paper Positioning

The natural extension is not "make ML always work." The stronger contribution is
to evaluate the Evidence Gate as a constellation-scale safeguard: a local,
chronological validation rule that prevents unsupported residual learning under
cross-satellite and cross-regime domain shift.
