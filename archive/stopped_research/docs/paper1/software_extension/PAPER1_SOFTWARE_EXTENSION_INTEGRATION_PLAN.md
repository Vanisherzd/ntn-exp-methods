# Paper 1 Software Extension Integration Plan

## Safe for the current workshop artifact

- Keep the existing real BK1/BK2 negative-result summary unchanged.
- Index the stronger-baseline artifact as supporting audit evidence: zero,
  median-bias, ridge, RF, GBR, and MLP all remain worse than SGP4 in the
  reported BK1 rows.
- State that the current extension is summary-level and does not add independent
  sample-level or tail evidence.

## Keep out of the current paper

- Do not claim residual autocorrelation, sign stability, PSD, or train/validation
  shift from absent arrays.
- Do not claim p95/p99 or cost-aware gate closure on real BLACK KITE.
- Do not add the dry-run matrix as a new multi-satellite result.

## Paper 1+ material

The raw-TLE rerun should export pair-level predictions, validation/test tails,
pair identifiers, and satellite-aware splits. That is the correct basis for
tail-aware gates and a multi-satellite generalization matrix.

## Candidate paragraph after a raw-data rerun confirms the artifact

> Across the available lightweight residual baselines, including constant-bias,
> ridge, random-forest, gradient-boosting, and small-MLP candidates, no reported
> BK1 staleness row improved over zero-residual SGP4. This auxiliary audit is
> summary-level and model-derived; it does not establish universal
> unlearnability, and tail-aware deployment remains future work until
> per-sample validation and test errors are archived.

## Slide recommendation

Use one backup slide only: "Stronger baselines: same safe decision." Keep the
real negative result as the main peak and label all added material
software-only/model-derived. Do not add another main-slide table unless a raw
rerun produces independent evidence.
