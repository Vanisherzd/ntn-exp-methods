# Phase-1 Target-Specific Learnability Report

Date: 2026-07-27
Trust baseline: `62083b5`.
Design: **A → A only**, 7 retained non-BLACK-KITE satellites × 6 staleness
bands = **42 cells**. No cross-satellite transfer. No reject sensitivity.

Software-only. Model-derived inter-TLE residuals,
`reference_is_measured_truth = false`; no measured RF truth, no packet,
error-rate, receiver-acknowledgement, over-the-air, or on-orbit result.
Paper 1 and slides untouched. Nothing tuned after seeing results.

---

## 1. Targets

Read from `dataset_qualification.json` `retained_keys` (minus BLACK KITE);
identities resolved by canonical ingestion from the preserved SATCAT responses.
No name was hard-coded.

| Satellite | NORAD | Regime (from ingested elements) | Canonical records | Median gap | Epoch span |
|---|---:|---|---:|---:|---|
| ISS (ZARYA) | 25544 | alt300-500 / inc0-60 | 46 859 | 4.518 h | 1998-11-20 → 2026-07-26 |
| SENTINEL-6B | 66514 | alt900-1400 / inc60-90 | 727 | 5.621 h | 2025-11-17 → 2026-07-26 |
| FLOCK 4H 1 | 66704 | alt500-700 / inc90-100 | 614 | 7.895 h | 2025-12-18 → 2026-07-26 |
| FLOCK 4H 2 | 66705 | alt500-700 / inc90-100 | 635 | 7.893 h | 2025-12-18 → 2026-07-26 |
| IRIDIUM 181 | 56726 | alt700-900 / inc60-90 | 2 678 | 9.982 h | 2023-05-22 → 2026-07-26 |
| IRIDIUM 177 | 56727 | alt500-700 / inc60-90 | 2 623 | 9.735 h | 2023-05-22 → 2026-07-26 |
| ONEWEB-0015 | 61594 | alt900-1400 / inc60-90 | 1 695 | 8.000 h | 2024-10-24 → 2026-07-26 |

## 2. Headline

**The preregistered MAE gate opened in 0 of 42 cells.** No cell satisfies the
candidate criterion (gate OPEN on validation **and** held-out learned MAE below
SGP4). The deployed policy is SGP4 / never-learn in every satellite and band.

All pair-level integrity invariants passed before any result was written.

## 3. Held-out degradation map (positive = learned worse)

| Satellite | 8 h | 24 h | 48 h | 72 h | 96 h | 168 h |
|---|---:|---:|---:|---:|---:|---:|
| ISS (ZARYA) | +0.32 | +0.08 | +0.08 | +0.10 | +0.09 | +0.13 |
| SENTINEL-6B | +12.41 | +8.08 | +11.70 | +14.49 | +30.65 | +21.25 |
| FLOCK 4H 1 | +14.43 | −1.05 | +0.89 | +0.66 | +0.73 | −0.33 |
| FLOCK 4H 2 | +2.51 | +1.54 | −0.70 | −0.55 | +0.16 | −0.38 |
| IRIDIUM 181 | **−1.94** | +2.19 | −0.44 | −0.99 | **−1.63** | **−2.23** |
| IRIDIUM 177 | −0.02 | +0.74 | +0.84 | +0.10 | **−0.52** | **−1.30** |
| ONEWEB-0015 | +81.15 | +122.29 | +16.46 | +1.09 | **−0.39** | +0.13 |

Every cell closed. Bold = held-out learned win that is statistically significant
at pair level (§5).

## 4. Pair-level statistics

Sign-test p-values are exact below 1000 pairs and log-space above; `p = 0` in
the tables means underflow below double precision (ISS bands carry 14 000–19 000
test pairs, so a 0.1 % effect is overwhelmingly significant).

Selected representative rows:

| Satellite | Band | test pairs | learned wins | SGP4 wins | ties | win rate | median Δ [Hz] | bootstrap 95 % CI [Hz] | p |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| ISS | 8 h | 14 636 | — | — | — | 0.412 | — | — | <1e-15 |
| ISS | 168 h | 13 110 | — | — | — | 0.445 | — | — | <1e-15 |
| SENTINEL-6B | 96 h | 268 | — | — | — | 0.038 | — | — | <1e-15 |
| IRIDIUM 181 | 168 h | — | — | — | — | 0.648 | — | [−0.2664, −0.1773] | <1e-15 |
| IRIDIUM 177 | 168 h | — | — | — | — | 0.689 | — | [−0.6733, −0.4006] | <1e-15 |
| FLOCK 4H 1 | 96 h | — | — | — | — | 0.495 | — | — | 1.000 |

Full per-row counts, medians, means, CIs and p-values are in
`phase1_target_specific/target_specific_pair_statistics.csv`.

## 5. The important negative-adjacent finding: six significant **missed-open-style** cases

These are cells where the gate **closed** on validation but the held-out learned
branch **beat** SGP4 with pair-level significance. They are *not* candidate
regimes under the preregistered criterion, and they are not reported as
improvements to deploy — but they are the strongest hint of real learnable
structure the campaign has produced.

| Satellite | Band | selected model | validation Δ% | held-out Δ% | pair win rate | bootstrap 95 % CI [Hz] | p |
|---|---:|---|---:|---:|---:|---|---:|
| IRIDIUM 181 | 8 h | stale_age_ridge | −1.37 | **−1.94** | 0.615 | [−0.0041, −0.0024] | <1e-15 |
| IRIDIUM 181 | 96 h | stale_age_ridge | −0.79 | **−1.63** | 0.619 | [−0.0908, −0.0544] | <1e-15 |
| IRIDIUM 181 | 168 h | stale_age_ridge | −0.63 | **−2.23** | 0.648 | [−0.2664, −0.1773] | <1e-15 |
| IRIDIUM 177 | 96 h | stale_age_ridge | −1.49 | **−0.52** | 0.587 | [−0.1383, −0.0307] | 3e-06 |
| IRIDIUM 177 | 168 h | stale_age_ridge | −2.03 | **−1.30** | 0.689 | [−0.6733, −0.4006] | <1e-15 |
| ONEWEB-0015 | 96 h | stale_age_ridge | −0.27 | −0.39 | 0.562 | [−0.0307, **+0.0047**] | 0.015 |

Observations, stated as observations:

1. **Both Iridium objects, at long staleness, in the same direction.** Five of
   the six cases are Iridium; all five have bootstrap CIs excluding zero.
2. **One model family does it all**: `stale_age_ridge` — ridge on TLE age and
   epoch gap only — is selected in every one of the six. The richer full-feature
   ridge is not.
3. **Validation and held-out agree in sign** in all six, so this is not a
   validation fluke that reversed out of sample.
4. **The gate refused because the margin was never met**, not because the
   evidence pointed the other way: the best validation improvement is −2.03 %
   against the 5 % that γ = 0.95 requires.
5. **The effect is ≈1–2 %** of an already sub-Hz to sub-100-Hz residual. ONEWEB
   is the weakest case: its CI crosses zero.

This does **not** meet the preregistered candidate criterion and is **not** a
learnability claim. It is a signal worth designing an experiment around.

## 6. Tail metrics and diagnostic gates

**No p95, p99, outage or guard-cost gate opened in any of the 42 cells.** So,
unlike Phase-0 (BK2 → BK2 opened p95 at 8/24/48 h), there is no gate-objective
disagreement to classify here under the A/B/C scheme. The p95-caution section is
not exercised by Phase-1.

**The outage proxy is non-zero for the first time in the campaign.** ISS reaches
3.04 % at 168 h (SGP4 0.030388 vs learned 0.030350), and smaller non-zero values
appear for FLOCK, IRIDIUM and ONEWEB at 168 h. Until now every residual sat far
below `F_tol` = 500 Hz and the outage gate was closed for lack of anything to
improve; ISS at long staleness is the first object where the tolerance is
actually exercised. Learned and SGP4 outage are indistinguishable.

## 7. Reject behaviour — careful statement

| Satellite | reject rate 8 h → 168 h | rejections in held-out splits? |
|---|---|---|
| ISS (ZARYA) | 0.155 % → **28.53 %** | **Yes** — 1 459 validation and 3 172 test pairs removed at 168 h |
| ONEWEB-0015 | 0.225 % → 16.94 % | No — all in train |
| SENTINEL-6B | 0.0 % → 2.33 % | No — all in train |
| FLOCK 4H 1 | 0.221 % → 2.71 % | No — all in train |
| FLOCK 4H 2 | 0.628 % → 2.30 % | No — all in train |
| IRIDIUM 181 | 0.0 % → 0.94 % | No — all in train |
| IRIDIUM 177 | 0.0 % → 2.41 % | **Yes, marginally** — 1 validation and 6 test pairs at 168 h |

Stated precisely, as required:

> For ISS at 24 h and beyond, and for IRIDIUM 177 at 168 h, **screening did
> directly alter held-out evaluation membership**. For SENTINEL-6B, both FLOCK
> objects, IRIDIUM 181 and ONEWEB-0015, **screening did not directly alter
> held-out evaluation membership** — every rejected pair fell in the training
> segment.

This says nothing about causal effect. Training-set screening still changes the
fitted learner in every satellite, so a satellite with "no held-out rejections"
is **not** immune to reject-rule influence. Full causal sensitivity is reserved
for the reject-threshold sweep and was not run.

## 8. Regime observations (descriptive only)

- **SENTINEL-6B is the worst target by a wide margin** (+8 % to +31 %, win rates
  0.038–0.321, all significant). It is also the smallest history (727 records).
- **ONEWEB-0015 is catastrophic at short staleness** (+81 %, +122 %) and settles
  to ~0 by 72 h. Its mean B\* is −0.0298, two decades larger in magnitude than
  every other object and negative — an orbit-determination fit artifact flagged
  earlier. Short-staleness residuals for this object are evidently not
  well-behaved.
- **ISS is remarkably flat**: +0.08 % to +0.32 % everywhere, but every row is
  overwhelmingly significant because of its 14 000–19 000 test pairs. Large N
  turns a negligible effect into a certain one — a caution for interpreting
  significance across objects with 100× different pair counts.
- **The Iridium pair is the only place learning consistently helps at all**, and
  only at long staleness.

## 9. Outputs

`experiments/exp14_multisat_generalization_matrix/phase1_target_specific/`:
`target_specific_results.csv`, `target_specific_pair_statistics.csv`,
`target_specific_gate_diagnostics.csv`, `target_specific_results.json`,
`fig_target_specific_mae.pdf/png`, `fig_target_specific_gate_map.pdf/png`.

## 10. Execution note

Cells were computed in per-satellite and per-band chunks purely for runtime
(ISS carries 46 859 canonical elements and up to ~90 000 accepted pairs per
band). Every chunk ran the identical code path and protocol; results were merged
without modification. Two implementation defects were fixed en route, neither of
which touches protocol, thresholds, models, features, pairing or gate margin:

1. the exact sign test overflowed `2.0 ** trials` above 1023 pairs — now exact
   rational below 1000 trials and log-space above;
2. pair metrics were computed in a Python per-pair loop — now vectorized.

Phase-0 was re-run after both fixes and its results are **bit-identical**.
