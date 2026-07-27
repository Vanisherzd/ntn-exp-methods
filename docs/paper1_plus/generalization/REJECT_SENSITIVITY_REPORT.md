# Reject-Sensitivity Study (Phase 6)

Date: 2026-07-27
Status: **method fixed and implemented; results blocked on data acquisition.**
No sweep has been executed on real data because no raw TLE archive exists in
this workspace.

Scope: software-only, model-derived inter-TLE residuals,
`reference_is_measured_truth = false`; no measured RF truth.

---

## 1. The attack this study must answer

> "Did screening remove the most learnable manoeuvre/outlier structure and make
> the negative finding self-fulfilling?"

This is the sharpest available objection to the frozen Paper 1 result, and it is
currently **unanswered**. Paper 1 discloses that its finding is conditional on
accepted non-outlier pairs under a `|r| > 1500 Hz` screen, but never measures
what the screen removes.

The objection is credible for a specific reason: manoeuvres and bad
orbit-determination epochs are exactly the *systematic, physically caused*
events a learner could in principle predict. Removing them and then reporting
that the remainder is unlearnable risks assuming the conclusion.

**If the answer turns out to be yes, it will be reported as yes.** That outcome
would materially weaken the frozen Paper 1 claim, and this document commits in
advance to reporting it.

---

## 2. What is already known (from committed artifacts, BK1 only)

The removed-pair magnitudes survive in the BK1 report:

| Staleness | Removed pairs | Largest removed max\|residual\| [Hz] |
|---:|---:|---|
| 8 h | 0 | — |
| 24 h | 6 | 2326, 2194, 2194, 2072, 2072 |
| 48 h | 5 | 14457, 3028, 2208, 1549, 1549 |
| 72 h | 11 | 26210, 11386, 8388, 8388, 6855 |
| 96 h | 13 | 14755, 14078, 14078, 12500, 6890 |
| 168 h | 19 | 30574, 28081, 22768, 19454, 19263 |

Removed pairs sit **1.4×–20× above the threshold**, not just over the line. That
is consistent with manoeuvre / bad-OD rather than borderline drift, and it is a
partial defence — the screen is not shaving a marginal tail.

It is **not** a complete defence, because two things remain unmeasured:

1. the residual **energy** those pairs carry relative to the retained population
2. whether the removed population is itself **learnable** — a large residual is
   not automatically a predictable one

Nothing in the committed artifacts can settle either. Only a sweep can.

---

## 3. Method (implemented)

`run_multisat_generalization_matrix.py --reject-sweep 150 500 1500 3000 inf`

For every satellite × staleness × threshold the pipeline **re-runs the entire
cell**, not just the pair count: rebuild pairs, refit correctors on train,
reselect on target validation, recompute every gate, re-evaluate on test. This
matters — a study that only reported retained pair counts would not answer the
learnability question at all.

Thresholds: `none` (∞), 150 Hz (the old transfer value), 500 Hz (= F_tol),
1500 Hz (the Paper 1 value), 3000 Hz.

Recorded per combination, in `reject_sensitivity_summary.csv`:

| Column | Meaning |
|---|---|
| `accepted_pairs`, `rejected_pairs`, `reject_rate_pct` | how much the screen removes |
| `residual_mae_hz`, `residual_p99_hz` | residual scale of the **retained** population |
| `status`, `selected_model` | whether the cell is evaluable and what wins on validation |
| `gate_decision` | does the gate flip when the screen is relaxed? |
| `degradation_pct` | does learning become *less* bad, or actually good, with outliers retained? |
| `pair_win_rate` | pair-level win rate under each threshold |
| `top_rejected_max_abs_hz` | the five largest magnitudes removed |

Per-pair identity is preserved throughout, and every rejected pair is exported
separately to `rejected_pairs.csv` with a `reject_reason`
(`residual_cap`, `sgp4_propagation_error`, `tle_parse_error`), so the removed
population can be studied directly rather than inferred from counts.

Figure: `fig_reject_threshold_sensitivity.pdf/png` — three panels, (a) reject
rate, (b) retained residual scale, (c) learnability (degradation %) vs
threshold, one line per satellite, with a zero reference line on (c).

---

## 4. Decision rule agreed in advance

| Observation across thresholds | Conclusion |
|---|---|
| Degradation stays positive at every threshold including `none` | The negative result is **not** an artifact of screening. The strongest possible answer to the objection. |
| Degradation shrinks but stays positive as the screen relaxes | Screening is mildly favourable to the negative result; must be disclosed with the magnitude. |
| Degradation crosses zero, or the gate opens, at a looser threshold | **The screen was manufacturing the result.** The frozen Paper 1 claim must be restated as conditional on nominal-only pairs, and the manoeuvre-aware case becomes the actual finding. |
| Cells become non-evaluable at tight thresholds | A sample-size effect, not a learnability effect; must not be read as either. |

Committing to this table before seeing the data is the point of writing it now.

---

## 5. Current state

| Item | State |
|---|---|
| Sweep implemented | ✅ |
| Sweep executed on real data | ❌ blocked — no raw TLE archive |
| `reject_sensitivity_summary.csv` | present, header only |
| `rejected_pairs.csv` | present, header only |
| `fig_reject_threshold_sensitivity` | not emitted (below satellite threshold) |
| Objection answered | **No.** Still open. |

Blocking requirement: restore `dataraw/spacetrack/` and acquire the Phase 1
catalog. Until then the frozen Paper 1's reject-rule limitation stands as
disclosed-but-unquantified, and the advisor answer remains: *concede the
screening, name the follow-up, do not defend it as neutral.*
