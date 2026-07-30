# Unified Generalization Protocol (Phase 0)

Date: 2026-07-27
Status: **normative for the Paper 1+ campaign.** Every target-specific and
cross-satellite result must be produced by this protocol, through the single
code path in
`experiments/exp14_multisat_generalization_matrix/run_multisat_generalization_matrix.py`.

Scope: software-only. Every residual is model-derived with
`reference_is_measured_truth = false`; there is no measured RF truth, and no
packet, error-rate, receiver-acknowledgement, over-the-air, or on-orbit result.

---

## 0. Why this document exists

The two experiments behind the frozen Paper 1 used **different protocols** while
being reported in one table. The audit
(`TLE_DATA_INVENTORY.md` §5) found:

| Aspect | BK1 target-specific | old BK1→BK2 transfer |
|---|---|---|
| Reject threshold | 1500 Hz | **150 Hz** |
| Feature vector | 10 | **7** |
| Pairing | closest-to-target in band | any pair in window |
| Target-side validation | yes | **none** |
| Model selection | best validation MAE | **min over candidates on BK2 test** |

**The old cross-transfer numbers are therefore NOT reusable in this campaign and
must not appear in any Paper 1+ result table.** They are superseded, not merely
supplemented. The runner records this in
`metadata.supersedes`.

---

## 1. Split semantics

Two cell types, one rule each. No other arrangement is permitted.

```
target-specific   A -> A :   train_A  ->  validation_A  ->  test_A
transfer          A -> B :   train_A  ->  validation_B  ->  test_B
```

**The target validation segment**

- selects the candidate model whenever selection is needed
- tunes every hyper-parameter (ridge α)
- computes the Evidence Gate G for every gate objective
- never contains a target test sample

**The target test segment**

- reports consequences only
- never selects a model
- never tunes a hyper-parameter
- never decides G

For transfer cells the corrector is fitted on the **source** train segment but
selected and gated on the **target** validation segment. That is the deployable
semantics: a terminal can only validate against the satellite it is about to
serve. The old transfer experiment had no target validation window at all, which
is precisely the defect this protocol removes.

### Leakage rules

- Splits are chronological by **reference (newer) TLE epoch**, using two global
  boundaries at the 60 % and 80 % time-quantile of the satellite's record span.
  The same two boundaries gate every staleness band for that satellite.
- The stale TLE in any pair is always older than the reference epoch, so
  training never observes a future TLE.
- For a transfer cell the source and target boundaries are computed
  independently; no target training data is used at all.
- A pair belongs to exactly one split, determined by its reference epoch.

---

## 2. Shared configuration — identical for every cell

| Element | Value | Where |
|---|---|---|
| Pairing rule | for each reference TLE, the older TLE inside the band whose gap is **closest to the target staleness** (not restricted to consecutive TLEs) | `select_stale_partner` |
| Staleness bands (h) | 8:[4,14], 24:[16,36], 48:[36,60], 72:[60,84], 96:[84,120], 168:[144,192] | `STALENESS_BANDS` |
| Samples per pair | 24, spaced over 5700 s (~one orbit), starting at the reference epoch | `K_SAMPLES_PER_PAIR` |
| Feature schema | 10 features: `t_age_s, t_gap_s, stale_doppler_hz, sin_phase, cos_phase, elevation_deg, range_km, stale_mean_motion_rad_min, stale_bstar, stale_ecc` | `FEATURE_NAMES` |
| Reject threshold | default `|r| > 1500 Hz` per pair; swept in Phase 6 | `--reject-hz` |
| Ground station | 24.0°N, 121.0°E, 100 m (representative) | `--gs-lat/lon/alt` |
| Carrier | 868 MHz | `--carrier-hz` |
| Candidate set | references `zero, mean_bias, median_bias`; learned `linear_bias_rate, stale_age_ridge, ridge` | `REFERENCE_MODELS`, `LEARNED_MODELS` |
| Selection metric | pair-level MAE on target validation, among **learned** models only | `evaluate_cell` |
| γ | 0.95 | `--gamma` |
| F_tol | 500 Hz proxy | `--f-tol-hz` |

Mean elements are derived from the TLE lines via `Satrec`, not from Space-Track
JSON columns, so JSON and three-line text archives are treated identically. Units
differ from the Space-Track columns (rad, rad/min); all features are standardized
before fitting, so the fit is unaffected.

A constant bias is **not** a learned residual correction: `mean_bias` and
`median_bias` are reported as references and can never open a gate. This
preserves the Paper 1 rule.

---

## 3. Experimental unit

**The accepted TLE pair, never the individual in-pass sample.**

The 24 samples inside a pair are strongly correlated: they are one propagation
of one TLE pair over one orbit. Treating them as 24 independent observations
inflates effective sample size by ~24×. Therefore:

- every metric is computed per pair first, then averaged across pairs
- every statistical test is paired at pair level
- pair identity is preserved in every export (`pair_id`,
  `stale_epoch_utc`, `ref_epoch_utc`, `actual_staleness_h`, `band_h`,
  first/last sample timestamps)
- rejected pairs are exported too, with a `reject_reason`

`pair_id` format: `<satellite_key>|<band>h|<reference_epoch_iso>`.

---

## 4. Gate objectives

All computed on the **target validation** segment, all with the same margin γ:

| Objective | Test |
|---|---|
| `mae` | MAE_ml(V) < γ·MAE_phys(V) |
| `p95` | p95_ml(V) < γ·p95_phys(V) |
| `p99` | p99_ml(V) < γ·p99_phys(V) |
| `outage` | Pr(\|e\|>F_tol)_ml(V) < γ·Pr(\|e\|>F_tol)_phys(V) |
| `guard_cost` | E_ml(V) < γ·E_phys(V), E = (1+α_g·2·p99/B)(1+ρ) |

Degenerate case: if the physics metric is exactly 0 the learned branch cannot
beat it by a margin, so the gate is recorded **closed**, never "open" and never
a division by zero. This matters in practice because the outage proxy is 0
whenever every residual is below F_tol.

`--primary-gate` (default `mae`) selects which objective drives the reported
`gate_decision` and the deployed policy. All objectives are always recorded, so
Phase 7 can compare them without a rerun. **No objective is asserted superior
before evaluation.**

---

## 5. Reported statistics

Per cell, on the target test segment (consequences only):

- pair-level baseline and learned MAE / p95 / p99 / outage
- degradation %, p95 degradation %, p99 degradation %
- pair win / loss / tie counts and win rate
- mean per-pair MAE delta with a 2000-resample bootstrap 95 % CI
- exact two-sided sign-test p-value on pair wins vs losses

The sign test and bootstrap operate on pairs, so "learned is worse in every row"
can finally be stated with an uncertainty rather than as a bare point estimate.

---

## 6. Mandatory re-derivation before any new claim

Before any Paper 1+ scientific statement, and **once raw data is available**,
these four cells must be re-derived from scratch under this protocol:

1. BK1 → BK1
2. BK2 → BK2
3. BK1 → BK2
4. BK2 → BK1

Purpose: establish whether the frozen Paper 1 conclusion survives a unified,
target-validated protocol. Only after that may additional satellites be folded
into the matrix.

Expected differences from the frozen paper, all of which are protocol effects
rather than contradictions:

- BK1→BK2 will use a 1500 Hz screen instead of 150 Hz, so the accepted
  population changes.
- BK1→BK2 gains a real BK2 validation window, so selection is no longer made on
  BK2 test.
- BK2→BK1 and BK2→BK2 did not exist before.
- All metrics become pair-level rather than sample-level.

Any divergence must be reported as a protocol difference, **not** presented as a
new finding about learnability, and the frozen Paper 1 must not be edited to
match.

---

## 7. Invariants enforced by tests

`tests/test_multisat_generalization.py` asserts, for every populated run:

- `gate_decision` is reproducible from validation metrics alone (Eq. 6), so test
  values cannot have decided it
- validation and test pair-id sets are disjoint within a cell
- transfer cells draw validation and test pairs from the **target** satellite
- pair identity fields are present and non-empty on every exported pair row
- no NaN in any reported metric of an evaluated row
- the dry-run state is explicit when data is unavailable
- generated reports carry no measured-RF claim
