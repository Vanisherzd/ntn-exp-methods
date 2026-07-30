# PROTOCOL — VISIBLE-PASS CAUSAL RESIDUAL TEST (exp15 rebuild)

Final authorized experimental recovery attempt. Written and committed BEFORE any
predictive model is fitted. No parameter in this document or in the accompanying
JSON configurations may change afterwards on the basis of model performance.

## Why this rebuild exists

The previous causal pilot (`experiments/exp15_causal_recovery`) produced
0 / 279 open gates and every candidate worse than SGP4, but the result was
**not certifiable**. Two independent reviewers found, and the implementer
verified:

1. **96.58 %** of its transmissions placed the satellite **below the endpoint
   horizon** (median elevation −42.5°). Only 1.45 % were above 10°. On visible
   geometry the residual is **5.6× larger**, and an in-sample bound on
   feature-based correction rose from 0.10 % to 9.82 % — from far below the 5 %
   gate to above it.
2. **Row membership depended on the future catalogue**: a transmission existed
   only if a qualifying later element was subsequently published. Drop rates rose
   with staleness to 100 % for one satellite.
3. The **single-reference label carried uncertainty comparable to the target**:
   on visible rows the spread across valid alternative references exceeded the
   label itself in 51.8 % of probes (ratio 1.81 at 8 h staleness).

This protocol fixes all three at the source rather than by filtering.

## The three fixes

| defect | fix |
|---|---|
| below-horizon transmissions | transmissions are **generated from visible passes predicted by the held stale TLE**, never generated on a UTC grid and filtered afterwards |
| future-dependent row membership | the transmission **registry is written and hashed before any reference is queried**; later catalogue behaviour may change a label's status, value, uncertainty or closure time but can never delete a row |
| label ambiguity | the label is a **deterministic reference ensemble median** with a published uncertainty `sigma_ref`, not one arbitrarily chosen later element |

## R0 — pass-based transmission generation

For each provisioning episode, using **only** the stale TLE held at
`t_refresh`, the current/future UTC inside the frozen episode, and the fixed
ground-station coordinates:

1. scan the episode window for intervals where the **stale-TLE-predicted**
   elevation exceeds the threshold;
2. refine each threshold crossing by bisection;
3. emit a fixed number of transmission instants inside each predicted-visible
   interval, at pre-registered normalized offsets.

Primary threshold **10°**. A 20° subset is computed as a diagnostic only and is
not trained on before the primary result is known.

The pass finder is event-driven: a coarse vectorized elevation scan locates sign
changes of `elevation − threshold`, then each crossing is bisected. The timeline
is not brute-forced at fine resolution.

No sample position may be chosen using later/reference geometry.

Every pass carries a `pass_id`; every scheduled transmission carries a permanent
`tx_id`. **Independent analysis units are the pass, the deployment episode and
the closure day — never the individual within-pass sample.**

## R1 — frozen row registry

The registry is written, hashed with SHA-256, and frozen before reference-label
construction begins. Persisted per row: `tx_id`, `pass_id`, `episode_id`,
satellite, `t_refresh`, `t_tx`, held-TLE identifier, held-TLE `EPOCH`, held-TLE
`CREATION_DATE`, predicted elevation, predicted range, predicted stale Doppler,
actual stale-TLE age, provisioning policy, and every deployment-feature
dependency.

**No row is ever silently dropped.** Allowed label statuses, all retained:

- `COMPLETE`
- `CENSORED_INSUFFICIENT_REFERENCES`
- `AMBIGUOUS_HIGH_SPREAD`
- `INVALID_SOURCE_METADATA`

## R2 — reference-ensemble label

A dataset-only feasibility analysis runs first over closure horizons
{24, 48, 72} h and `K_min` ∈ {2, 3}. It may inspect **only** label coverage,
reference count, ensemble spread and catalogue metadata quality — never model
performance. One (horizon, `K_min`) pair is then selected by label completeness,
stability of ensemble uncertainty, cross-satellite consistency and closure delay,
and that choice is committed before model training.

For each `tx_id`: collect distinct same-object solutions with `CREATION_DATE` in
`(t_tx, t_tx + horizon]`; canonicalize same-epoch revisions by the pre-existing
deterministic rule; propagate each to `t_tx`; then

```
D_ref_ens(t_tx) = median_q D_ref,q(t_tx)
sigma_ref       = 1.4826 * MAD_q D_ref,q(t_tx)
r(t_tx)         = D_ref_ens(t_tx) - f_phys(t_tx)
t_close         = t_tx + closure_horizon
```

A label may enter training or validation only when `t_close <= t_refresh` of the
model being fitted. The later solution that minimizes residual error is never
selected. Rows are never deleted for large spread — they are marked
`AMBIGUOUS_HIGH_SPREAD` and keep their uncertainty value.

`r` is **not** called "the SGP4 residual". It is the
**ensemble-referenced inter-TLE residual**.

## R3 — censoring and selection-bias gate

Reported per satellite and provisioning regime: scheduled transmissions,
COMPLETE, censored, ambiguous, completion rate, reference-count distribution,
uncertainty distribution.

Requirement: completeness **≥ 80 % overall** and **≥ 70 % for every qualified
satellite**.

Labelled and censored rows are compared on pre-transmission quantities only
(predicted elevation, stale age, range, Doppler magnitude, orbital phase,
satellite/regime, episode time) using the absolute standardized mean difference.
Gate: **|SMD| ≤ 0.10** on the principal continuous variables. Failure returns
**UNRESOLVED** and stops before model training. Censoring is never hidden behind
complete-case counts.

## R4 — visibility semantics

Operational inclusion depends **only** on stale-TLE predicted visibility, which
is what the endpoint could decide before transmitting. Reference-ensemble
elevation is computed after labelling as a **diagnostic only** and never creates
or deletes a row. Reported: predicted-visible and reference-consensus-visible;
predicted-visible but reference-consensus-below-horizon; the disagreement rate.

S2 may pass only if its conclusion is not reversed between the primary 10°
schedule and the 20° diagnostic.

## R5 — operational provisioning scenarios

Two pre-registered scenarios, no others:

- **NOMINAL** — 24 h provisioning cadence.
- **DEGRADED** — 72 h cadence, representing missed or delayed refreshes.

The endpoint receives the latest globally available element only at the scheduled
provisioning event and freezes it until the next. No 168 h scenario is included
unless it arises naturally from the fixed degraded policy.

Actual TLE age at transmission is treated as a **continuous** quantity and its
distribution is reported. Age bands are derived after schedule generation from
pre-declared boundaries, for summaries only, and are never manufactured by
skipping fresher elements.

Primary S2 result is the satellite-balanced aggregate across both scenarios; each
scenario is also reported separately. A result present only in DEGRADED does not
by itself establish normal operational value.

## R6 — pre-flight coverage gate

Reported before fitting M1–M7: visible passes per satellite, COMPLETE labelled
passes, deployment episodes, closure-day blocks, actual age distribution,
reference-ensemble size, label uncertainty.

Minimum coverage — these are **coverage minima, not success criteria**:

- ≥ 6 qualified satellites
- ≥ 2 orbital regimes
- ≥ 30 COMPLETE deployment episodes per qualified satellite
- ≥ 10 independent closure-day blocks per satellite
- ≥ 500 COMPLETE predicted-visible transmissions overall

Failure returns **UNRESOLVED**. Thresholds are not lowered after inspecting model
results.

## R7 — reference-uncertainty analysis

Before predictive modelling, for COMPLETE rows: `|r|` against `sigma_ref`, and
the uncertainty ratio `sigma_ref / max(|r|, eps)`. Reported: median, p90,
fraction with `sigma_ref > |r|`, broken out by satellite and stale-age range.

Pre-registered sensitivity that does not discard uncertain rows:

- **A** primary unweighted evaluation
- **B** secondary uncertainty-weighted training and evaluation
- **C** secondary low-uncertainty diagnostic subset

**C may not be used for model selection or for the primary S2 claim.**

## R8 — element-chaining control

All stale and reference element identifiers are persisted. Measured: whether
`stale(episode k+1)` appears in reference ensemble `k`; shared element IDs across
adjacent episodes; residual autocorrelation by episode; element overlap across
training, validation and deployment windows.

All statistical resampling is grouped/blocked by at least satellite, deployment
episode and closure day. No intra-pass or overlapping-element row is treated as
independent. The chaining relationship is exposed to the audit but is **never** a
predictive feature.

## R9 — model family (unchanged)

M0 SGP4 zero correction · M1 age-only linear · M2 causal static ridge ·
M3 last-closed residual bias · M4 EWMA residual bias · M5 recursive least
squares bias/drift · M6 Kalman bias/drift · M7 static + closed historical-state
ridge. **No models added.** Every historical feature must satisfy
`source label closure <= model refresh`. Persisted per candidate: train,
validation and deployment metrics; selected hyperparameters; feature manifest;
scaler state; selection reason.

## R10 — walk-forward evaluation

closed history → training → validation → select candidate → decide Evidence Gate
→ freeze model/scaler/`G` → deployment episode → labels close later → next
refresh.

Gate margin fixed at 5 % (`gamma = 0.95`); `gamma` is not changed after results.
Metrics aggregate samples into passes, passes into episodes, episodes into
satellite-level effects. The primary comparison is satellite-balanced.

## R11 — cross-fitted headroom diagnostic

The previous 9.82 % figure was in-sample and is **not** evidence of achievable
benefit. Replaced by cross-fitted diagnostics — constant offset, age-bin offset,
linear static, quadratic static — each fitted on the training/validation
chronology and **scored out of sample on later episodes**. These are
**cross-fitted headroom diagnostics**, not oracle bounds, and none is a
deployable candidate unless it already appears in M1–M7.

If even the cross-fitted quadratic diagnostic fails to approach the 5 % margin
consistently across satellites, the record states that the studied observable
state has little reachable headroom.

## S2 pass criteria — all eleven required

1. satellite-balanced aggregate improvement over SGP4
2. hierarchical/block 95 % interval supports improvement
3. ≥ 2 satellites improve
4. ≥ 2 orbital regimes improve
5. no satellite contributes > 50 % of the aggregate benefit
6. effect sign stable across adjacent walk-forward episodes
7. not dependent on one screen setting
8. label-completeness and censoring gates pass
9. conclusion not reversed at the 20° diagnostic threshold
10. harmful-admission rate ≤ 20 %, with enough admissions to estimate it
11. improvement larger than, or demonstrably robust to, ensemble-reference
    uncertainty

Finding one positive pass, episode, satellite or provisioning scenario is not a
pass.

## Hard termination rule

This is the final dataset rebuild.

**If S2 FAILS** — stop the residual-learning paper line. Do not redesign
features, change provisioning cadence, lower the visibility threshold, change the
reference ensemble, build E5/E6, or rewrite the manuscript as a negative or
leakage paper.

**If S2 is UNRESOLVED because coverage or label quality fails** — stop this
dataset route and report that the available TLE archive cannot support the
required causal test. Do not keep iterating on the same archive.

**If S2 PASSES** — freeze code, config and artifacts; request human approval
before E5; do not edit the manuscript.

## Independent review

At most two concurrent agents. After registry and label construction: Reviewer A
(satellite visibility, timing and availability causality) and Reviewer B
(selection bias, censoring, label uncertainty). After walk-forward evaluation:
Reviewer C (hierarchical statistics and independence) and Reviewer D (adversarial
communications). No implementing agent may approve its own output.

## Standing constraints

No Space-Track calls. No credential access. No manuscript or figure edits. No
raw data committed. No E5 robustness sweep. No LR-FHSS PHY simulator. No neural
networks. No searching for a favourable cell.
