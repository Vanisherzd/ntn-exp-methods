# Review B - Orbit / Machine Learning Reviewer

## Recommendation

Score: 3/5, weak reject / borderline. The paper's strongest point is methodological honesty: chronological splits, stale-TLE pairing, and a gate that refuses a learned residual when validation does not beat SGP4. The weakness is that the ML component never improves the real task and the synthetic gate-open case is too clean to establish usefulness.

## Major Concerns

1. The real-data result is negative across all tested staleness values and cross-satellite transfer. This is valuable, but the paper should own it as a negative-result workshop paper. As written, the title and abstract still invite the reader to expect a useful learned controller.

2. The model-derived reference Doppler `D_ref` is a later-TLE SGP4 propagation, not measured truth. The paper discloses `reference_is_measured_truth = false`, which is good, but the implications are large: the learned residual is learning inter-TLE differences, not true satellite Doppler error.

3. The synthetic experiments verify the gate logic under a constructed systematic residual, but they do not show that such structure exists for the target data distribution. The phrase "gate-open synthetic regime" should be treated as a sanity check, not evidence that PGRL-like learning will help real D2S LR-FHSS.

4. The gate criterion uses MAE improvement with `gamma = 0.95`, but the operational loss is framed around hop-bin miss and energy proxy. A learned residual might reduce MAE without improving tail risk, or vice versa. The paper should explain why MAE is the gate metric instead of p99 residual or `Pr(|e| > F_tol)`.

5. The PGRL footprint claim is not yet credible enough for the amount of visual emphasis it gets in Fig. 3. The paper gives parameters, MACs, Flash, and energy estimates, but the algorithm is not sufficiently specified and the real-data gate never deploys it.

## Minor Fixes

- Define PGRL on first use in the abstract or remove the acronym if space is tight.
- Add a compact feature list for the learned residual models; "TLE age, epoch gap, stale Doppler, orbital phase, geometry, and stale orbital elements" is helpful but still broad.
- Clarify whether the MLP/PGRL inference footprint corresponds to the same model used in synthetic Fig. 3 or a separate representative predictor.
- Report validation window sizes next to the gate decisions or in Table I/II.
- Avoid "safe fallback" implying safety beyond the validation metric; it is a conservative fallback.

## Must Fix Before Submission

- Make the negative real-data ML result explicit in the title/abstract framing.
- Explain why MAE is the gate loss, or add a tail-risk gate result aligned to `F_tol`.
- Downgrade the synthetic result language to "gate sanity check" wherever it could be read as empirical support for deployment.
- Either specify the PGRL model enough to evaluate its footprint or reduce the PGRL claim to an illustrative MCU estimate.

## Overreach Check

The paper does not claim measured Doppler truth, and that restraint is important. The main overreach risk is not packet/link validation; it is ML validation: the paper may appear to validate a learning-based controller when the real-data evidence validates only that the gate rejects it.
