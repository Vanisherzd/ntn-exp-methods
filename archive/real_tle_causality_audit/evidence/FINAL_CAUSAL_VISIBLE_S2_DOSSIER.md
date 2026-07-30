# FINAL CAUSAL-VISIBLE S2 DOSSIER

Branch `exp15-visible-causal-rebuild`. Manuscript untouched and frozen.
No predictive model was fitted.

**VERDICT: UNRESOLVED — label quality gate (R3) failed.**
**RECOMMENDATION: STOP THIS PAPER LINE.**

*Both independent reviewers returned FAIL. Their findings do not change this
verdict; they strengthen its basis and correct three of my own claims — see §14
and §16. Two of my pre-registered tests (V1, V4) were shown to be structurally
incapable of failing, and I verified both defects myself.*

Per the pre-registered hard termination rule, an UNRESOLVED caused by label
quality means *stop this dataset route and report that the available TLE archive
cannot support the required causal test*. That is what happened, and the reason is
structural rather than a defect in the build.

---

## 1. Pre-registration commit and tag

| item | value |
|---|---|
| branch | `exp15-visible-causal-rebuild` |
| pre-registration commit | `a97dab406ef00eca674f8e612133b33cf5ca1a4d` |
| tag | `exp15-visible-causal-preregistered-v1` |
| execution commit | `4bc5c46` |

Committed at pre-registration, before any model could be fitted: `PROTOCOL.md`,
`schedule_config.json`, `label_ensemble_spec.json`, `model_manifest.json`,
`analysis_plan.json`, `tests/test_visible_causal_integrity.py`. No manuscript
files and no model results. Source hashes are recorded in
`loop_engineering/STATE.yaml`:

```
PROTOCOL.md               cae14d18c9a805d7…
schedule_config.json      d658231bd20e6520…
label_ensemble_spec.json  dec6604fe1af1e6d…
model_manifest.json       46ed2fcbe33e3970…
analysis_plan.json        b953ad98be031f10…
test_visible_causal_integrity.py  adf0fe7110e082c5…
```

**One post-pre-registration code change**, disclosed in full. Pre-registered test
V3 caught a real bug: the exit-crossing bisection in `pass_intervals` received its
bracket reversed, so the loop guard `b - a <= tol` was immediately true, the exit
time was never refined, and the coarse 60 s midpoint was returned — placing the
0.90-offset sample up to 30 s past the true threshold exit and therefore
marginally below the mask (observed minimum 9.472°). `refine()` was made
order-agnostic and now returns the above-threshold side of the final bracket.

No pre-registered parameter — threshold, offsets, horizon, cadence, `gamma`,
model setting — was altered; a bisection bracket was corrected so the code does
what the pre-registration already specified. All registries and labels were
regenerated. **The R3 verdict was FAIL both before and after** (max |SMD| 1.312 →
1.307 NOMINAL, 1.557 → 1.552 DEGRADED), so no conclusion rests on it.

## 2. Pass-based transmission-scheduling rule

Transmissions are **generated from predicted-visible passes**, never sampled on a
UTC grid and filtered. For each provisioning episode, using only the held stale
TLE, the transmission UTC and the fixed ground station:

1. vectorized coarse elevation scan at 60 s locates sign changes of
   `elevation − threshold` (a 10° LEO pass lasts ≳ 4 min, so 60 s cannot skip an
   entire pass);
2. each crossing is refined by bisection to 1 s;
3. five instants are emitted per interval at normalized offsets
   **0.10 / 0.30 / 0.50 / 0.70 / 0.90** between threshold entry and exit.

Passes whose exit crossing falls outside the episode window are discarded,
because the normalized offsets are undefined for a truncated interval. Primary
mask **10°**; a **20°** subset is built as a diagnostic. Each pass carries a
`pass_id`, each transmission a permanent `tx_id`. Independent units are the pass,
the deployment episode and the closure day — never the within-pass sample.

Verified outcome:

| registry | transmissions | passes | global min elevation |
|---|---|---|---|
| NOMINAL @10° | 132,585 | 26,517 | **10.034°** |
| NOMINAL @20° | 88,255 | — | **20.067°** |
| DEGRADED @10° | 133,235 | 26,647 | **10.036°** |
| DEGRADED @20° | 88,605 | — | **20.053°** |

**100 % of transmissions are above the mask**, against 96.58 % below the horizon
in the previous pilot.

## 3. Frozen row-registry hashes

The registry is SHA-256 frozen before any reference is queried. Labelling is
asserted not to mutate it (test V5, and an in-run assertion).

| scenario | satellite | registry SHA-256 | tx | passes | age p50 (h) | age max (h) |
|---|---|---|---|---|---|---|
| NOMINAL | ISS (ZARYA) | `26fd35e0a0d1f3d2` | 69,970 | 13,994 | 17.51 | 175.0 |
| NOMINAL | IRIDIUM 181 | `c259e0fc8b6fcf66` | 18,335 | 3,667 | 27.27 | 115.5 |
| NOMINAL | IRIDIUM 177 | `c759c6df4330884a` | 16,900 | 3,380 | 26.71 | 115.9 |
| NOMINAL | ONEWEB-0015 | `d6cc69f06f9f8cb3` | 11,755 | 2,351 | 22.19 | 92.4 |
| NOMINAL | SENTINEL-6B | `0aa4a5de62cdad44` | 5,515 | 1,103 | 24.41 | 265.0 |
| NOMINAL | FLOCK 4H 1 | `60cb8ba944dc8624` | 2,850 | 570 | 27.02 | 87.6 |
| NOMINAL | FLOCK 4H 2 | `a5f04bf6a7ef876f` | 2,905 | 581 | 26.96 | 93.9 |
| NOMINAL | BLACK KITE-1 | `f4e976b1eb57695e` | 2,870 | 574 | 33.85 | 1092.6 |
| NOMINAL | BLACK KITE-2 | `5c543a50284d1c0d` | 1,485 | 297 | 23.24 | 94.1 |
| DEGRADED | ISS (ZARYA) | `1d1be955747ef86a` | 70,120 | 14,024 | 42.95 | 223.0 |
| DEGRADED | IRIDIUM 181 | `0144032fdbfb30a9` | 18,405 | 3,681 | 52.26 | 126.6 |
| DEGRADED | IRIDIUM 177 | `22ec287ee46034ae` | 16,940 | 3,388 | 51.02 | 115.9 |
| DEGRADED | ONEWEB-0015 | `aa25f8f47414c8a0` | 11,880 | 2,376 | 46.60 | 140.0 |
| DEGRADED | SENTINEL-6B | `5a44e6c16590e2b5` | 5,560 | 1,112 | 48.88 | 265.0 |
| DEGRADED | FLOCK 4H 1 | `2cb00e8004f1c8fb` | 2,935 | 587 | 51.25 | 135.0 |
| DEGRADED | FLOCK 4H 2 | `8bbc50b654a54309` | 2,960 | 592 | 50.98 | 141.3 |
| DEGRADED | BLACK KITE-1 | `b24aaed4c6878bcc` | 2,920 | 584 | 66.46 | 1140.1 |
| DEGRADED | BLACK KITE-2 | `e4a3cc74ffb1d39a` | 1,515 | 303 | 56.47 | 142.4 |

Test **V1 passes**: truncating the future catalogue leaves the schedule
bit-identical. This is the check the previous attempt lacked — its A5 perturbed
the reference on rows that already existed and so could not detect that row
*membership* was decided by later publications.

## 4. Provisioning scenarios

**NOMINAL** 24 h cadence, **DEGRADED** 72 h cadence (missed or delayed
refreshes). At each event the endpoint receives the latest element with
`CREATION_DATE <= t_refresh` plus a frozen model/scaler/gate, and holds them
open-loop until the next event. Availability clock is `CREATION_DATE` restricted
to element epochs ≥ 2014, per the E0 year-stratified audit.

DEGRADED shifts the age distribution as intended (ISS p50 17.5 → 43.0 h; IRIDIUM
181 27.3 → 52.3 h) without any band being manufactured by skipping fresher
elements. No 168 h scenario was introduced.

## 5. Reference-ensemble specification

Dataset-only feasibility over horizons {24, 48, 72} h × `K_min` ∈ {2, 3}, both
scenarios, inspecting **only** coverage, reference count, ensemble spread and
metadata quality:

| horizon | K_min | COMPLETE mean (N/D) | COMPLETE min | labelled mean | σ_ref p50 |
|---|---|---|---|---|---|
| 24 h | 2 | 0.687 / 0.718 | 0.448 / 0.465 | 0.792 / 0.776 | 0.568 / 0.658 |
| 24 h | 3 | 0.426 / 0.436 | 0.287 / 0.268 | 0.485 / 0.467 | 0.530 / 0.392 |
| **48 h** | **2** | **0.808 / 0.838** | **0.624 / 0.638** | **0.941 / 0.930** | **0.903 / 0.889** |
| 48 h | 3 | 0.760 / 0.792 | 0.528 / 0.567 | 0.880 / 0.878 | 0.866 / 0.879 |
| 72 h | 2 | 0.785 / 0.834 | 0.624 / 0.653 | 0.966 / 0.957 | 1.520 / 1.498 |
| 72 h | 3 | 0.768 / 0.819 | 0.568 / 0.622 | 0.946 / 0.939 | 1.542 / 1.500 |

**Selected: 48 h, K_min = 2**, committed in `R2_selection.json` before labelling.
It wins criterion 1 (highest COMPLETE rate of any grid point), criterion 2
decisively (σ_ref p50 0.903 Hz against 1.520 Hz at 72 h — the longer horizon
admits more distant solutions whose own propagation error inflates the spread),
and criterion 4 (shorter delay). `K_min = 2` dominates `K_min = 3` on coverage at
every horizon while σ_ref is unchanged, so the third reference buys no
uncertainty reduction and costs coverage.

`R2_selection.json` records, **before** the full audit, that the minimum
per-satellite COMPLETE rate of 0.624 was already below the 0.70 floor and that
**no grid point satisfies that floor**. The gate was not relaxed afterwards.

Label definition: `D_ref_ens = median_q D_ref,q(t_tx)`,
`sigma_ref = 1.4826·MAD_q`, `r = D_ref_ens − f_phys(t_tx)`,
`t_close = t_tx + 48 h`. The residual is called the **ensemble-referenced
inter-TLE residual**, never "the SGP4 residual".

## 6. Label-completeness and censoring audit — **R3 FAIL**

| scenario | COMPLETE overall | min per satellite | labelled overall | max \|SMD\| |
|---|---|---|---|---|
| NOMINAL | 0.8016 ✓ (≥0.80) | **0.6307 ✗** (<0.70) | 0.9381 | **1.307 ✗** (>0.10) |
| DEGRADED | 0.8492 ✓ | **0.6599 ✗** | 0.9331 | **1.552 ✗** |

Per satellite, NOMINAL:

| satellite | n | COMPLETE | labelled | σ_ref p50 | \|r\| p50 | max \|SMD\| |
|---|---|---|---|---|---|---|
| ISS (ZARYA) | 69,970 | 0.863 | 0.990 | 2.080 | 13.83 | 0.895 |
| IRIDIUM 181 | 18,335 | 0.826 | 0.963 | 0.525 | 2.00 | 0.767 |
| IRIDIUM 177 | 16,900 | 0.815 | 0.968 | 0.942 | 5.43 | 0.724 |
| ONEWEB-0015 | 11,755 | 0.746 | 0.983 | 1.896 | 5.74 | 0.399 |
| SENTINEL-6B | 5,515 | 0.841 | 0.947 | 0.162 | 0.52 | 1.192 |
| FLOCK 4H 1 | 2,850 | 0.877 | 0.981 | 0.869 | 5.94 | 0.529 |
| FLOCK 4H 2 | 2,905 | 0.861 | 0.978 | 0.955 | 6.14 | 1.312 |
| BLACK KITE-1 | 2,870 | **0.632** | 0.737 | 1.177 | 8.39 | 1.245 |
| BLACK KITE-2 | 1,485 | 0.756 | 0.899 | 1.104 | 3.99 | 0.324 |

**The failure is not diffuse — it is concentrated in exactly two variables.**
Maximum |SMD| across satellites, by variable:

| variable | NOMINAL | DEGRADED | gate |
|---|---|---|---|
| **episode_time_s** (calendar) | **1.312** | **1.557** | 0.10 |
| **age_tx_s** | **1.245** | **1.351** | 0.10 |
| sin_phase | 0.454 | 0.350 | 0.10 |
| pred_range_km | 0.285 | 0.137 | 0.10 |
| cos_phase | 0.284 | 0.296 | 0.10 |
| abs_pred_stale_doppler_hz | 0.203 | 0.089 | 0.10 |
| pred_elevation_deg | **0.163** | **0.094** | 0.10 |

Geometry is essentially balanced — the visibility fix worked. What is
catastrophically unbalanced is **TLE age**, the primary covariate of the entire
study, and calendar time.

### Mechanism — verified, not assumed

A catalogue publication outage does two things at once: it makes the held element
stale, *and* it removes the later solutions needed to label that staleness.
Censoring and the covariate share a single cause.

| satellite | censored % | age p50: labelled → censored | hours to next publication: labelled → censored |
|---|---|---|---|
| ISS | 1.0 | 17.3 → **30.8** | 2.88 → **44.63** |
| IRIDIUM 181 | 3.8 | 26.8 → 33.3 | 6.08 → 25.52 |
| IRIDIUM 177 | 3.2 | 26.7 → 34.1 | 6.55 → 25.29 |
| ONEWEB-0015 | 1.8 | 22.2 → 27.6 | 5.30 → 28.40 |
| SENTINEL-6B | 5.3 | 24.3 → **68.8** | 4.28 → **43.23** |
| FLOCK 4H 1 | 1.9 | 27.0 → 33.3 | 5.05 → 22.36 |
| FLOCK 4H 2 | 2.2 | 27.0 → 32.2 | 4.51 → 30.90 |
| BLACK KITE-1 | **26.4** | 29.9 → **222.0** | 4.94 → **63.90** |
| BLACK KITE-2 | 10.1 | 23.2 → 34.2 | 5.10 → 23.42 |

Censored rows wait **4–13× longer** for the next publication. This is
missing-not-at-random on the study covariate.

### Restriction does not rescue it

Completeness declines monotonically with age beyond ~30 h (86.6 % at 24–30 h,
85.2 % at 36–48 h, 81.8 % at 48–72 h, 60.8 % at 72–120 h, **26.8 % beyond
120 h**). But capping age does not make censoring non-differential:

|SMD| on `age_tx_s` after restricting to age ≤ X:

| satellite | ≤30 h | ≤36 h | ≤48 h | ≤72 h |
|---|---|---|---|---|
| ISS | 0.012 | 0.325 | 0.622 | 0.833 |
| IRIDIUM 181 | 0.147 | 0.057 | 0.279 | 0.415 |
| IRIDIUM 177 | 0.067 | 0.245 | 0.460 | 0.484 |
| ONEWEB-0015 | 0.325 | 0.299 | 0.487 | 0.426 |
| SENTINEL-6B | 0.067 | 0.001 | 0.095 | 0.496 |
| FLOCK 4H 1 | **0.391** | 0.324 | 0.308 | 0.421 |
| FLOCK 4H 2 | 0.244 | 0.426 | 0.202 | 0.073 |
| BLACK KITE-1 | **0.755** | **0.536** | 0.566 | 0.952 |
| BLACK KITE-2 | 0.085 | 0.386 | 0.712 | 0.354 |

**No cap passes the 0.10 gate for all satellites.** At the tightest useful cap
(≤30 h, retaining 75.2 %) four satellites still fail, BLACK KITE-1 at 0.755.

## 7. Visibility-disagreement audit (R4)

Reference-ensemble elevation is computed after labelling as a diagnostic only and
never creates or deletes a row. Predicted-visible rows whose reference consensus
places the satellite below the horizon: **0.0–1.1 %** (ISS 0.000, IRIDIUM 181
0.001, ONEWEB-0015 0.011 DEGRADED, BLACK KITE-1 0.005–0.009). Stale-TLE-predicted
visibility and reference-consensus visibility agree almost perfectly, so the
operational inclusion rule is sound.

## 8. Coverage gate (R6) — **PASS**

| requirement | minimum | NOMINAL | DEGRADED |
|---|---|---|---|
| qualified satellites | 6 | **9** ✓ | **9** ✓ |
| orbital regimes | 2 | **6** ✓ | **6** ✓ |
| COMPLETE episodes per satellite | 30 | **95** ✓ | **35** ✓ |
| closure-day blocks per satellite | 10 | **95** ✓ | **96** ✓ |
| COMPLETE visible transmissions | 500 | **110,699** ✓ | **118,785** ✓ |

Coverage is not the problem. The archive has ample data; what it lacks is
*unbiased labels*.

## 9. Reference-uncertainty analysis (R7) — the ensemble label worked

Uncertainty ratio `sigma_ref / max(|r|, eps)` over labelled rows, NOMINAL:

| satellite | \|r\| p50 (Hz) | σ_ref p50 (Hz) | ratio p50 | ratio p90 | frac σ>\|r\| |
|---|---|---|---|---|---|
| IRIDIUM 177 | 5.453 | 0.939 | 0.192 | 1.513 | 0.158 |
| ONEWEB-0015 | 5.785 | 1.900 | 0.390 | 2.430 | 0.240 |
| SENTINEL-6B | 0.515 | 0.163 | 0.351 | 1.102 | 0.112 |
| FLOCK 4H 1 | 6.019 | 0.869 | 0.163 | 1.012 | 0.104 |
| FLOCK 4H 2 | 6.078 | 0.948 | 0.164 | 1.228 | 0.125 |
| BLACK KITE-1 | 8.459 | 1.172 | 0.141 | 1.459 | 0.142 |
| BLACK KITE-2 | 3.993 | 1.104 | 0.307 | 1.552 | 0.159 |

Compare the previous single-reference construction, where the spread across
equally valid references **exceeded the label itself in 51.8 % of visible probes**
and the ratio at 8 h staleness was **1.81**. Here the ratio is **0.06–0.39** at
the median and `sigma_ref > |r|` in only **6–24 %** of rows.

**The target is now identifiable.** Two of the three defects that invalidated the
previous attempt are genuinely fixed; the visible-geometry residual is also
physically material at last (|r| p50 0.5–38.7 Hz, against 0.2–1.0 Hz below the
horizon).

## 10. Element-chaining audit (R8)

Within-pass intra-class correlation of `|r|`: **0.51–0.83** across satellites.
The five samples inside one pass are strongly dependent, confirming the
pre-registered decision to treat the **pass**, not the sample, as the independent
unit. Episode-level lag-1 autocorrelation of the signed episode-mean residual:
**−0.05 to +0.64** (NOMINAL), materially better than the **−0.543** seen in the
previous chained construction, but still large enough for ONEWEB-0015 (0.457
DEGRADED), SENTINEL-6B (0.636 NOMINAL / 0.552 DEGRADED) and BLACK KITE-1 (0.381 /
0.415) that the pre-registered moving-block bootstrap — not i.i.d. episode
resampling — would have been required.

## 11–13. Walk-forward, headroom diagnostics, S2 analysis — **NOT RUN**

R9 (model fitting), R10 (walk-forward) and R11 (cross-fitted headroom) were not
executed, and no candidate M1–M7 was fitted to this dataset. The pre-registered
R3 rule is explicit: *"If this fails: return UNRESOLVED and stop before model
training."*

Running them would have produced numbers, and those numbers would have been
uninterpretable: with label availability differential on TLE age at |SMD| 1.25,
any measured age→residual relationship is confounded with the probability of
being labelled at all. That is precisely the class of error this programme has
been correcting for three rounds, and it would have been the fourth.

## 14. Independent reviewer reports

Reviewer A (satellite visibility, timing, availability causality) and Reviewer B
(selection bias, censoring, label uncertainty) were dispatched against commit
`4bc5c46`. Reviewers C and D are not applicable: their remit is post-walk-forward
statistics and adversarial review of results, and no results exist.

*Findings are appended in §16 when returned.*

## 15. Final verdict and recommendation

**VERDICT: UNRESOLVED** — pre-registered label-quality gate R3 failed
(criterion 8 of the eleven S2 criteria). Criteria 1–7 and 9–11 were not
evaluated, by design.

**RECOMMENDATION: STOP THIS PAPER LINE.**

The pre-registered rule for this outcome: *stop this dataset route; report that
the available TLE archive cannot support the required causal test; do not keep
iterating on the same archive.*

### Why this is the right stop, and not a fourth iteration

Three rounds of review found three defects. This rebuild fixed all three:

| defect | status |
|---|---|
| `t_gap_s` future-dependent feature | **fixed** — absent from the manifest, test V8 enforces |
| 96.58 % below-horizon transmissions | **fixed** — 100 % above mask, min 10.034° |
| future-dependent row membership | **partly fixed** — no reference *content* reaches the schedule, but the grid still ends at the archive's last publication, so future *extent* creates rows (A-B1, verified: 29 % for BLACK KITE-2). My V1 test could not detect this. |
| single-reference label ambiguity | **reduced ~3–4×, not fixed** — σ_ref omits the common back-propagation error; the honest ambiguity is 5–16× the 5 % margin (A-B3) |

**Correction, after independent review.** I originally wrote that the remaining
obstacle is "not a defect at all". That is too strong, and Reviewer A disproved
it: my *fixed* 48 h closure window is a design choice, and a data-dependent
"next K = 2 published solutions" rule cuts censoring by up to **76×** at a
*shorter* median closure delay (BLACK KITE-1 26.48 % → 0.35 %). Censoring as I
measured it is partly self-inflicted.

What survives the correction is stronger than the censoring argument and does not
depend on it. Two independent findings bind regardless of the closure rule:

- **Label ambiguity exceeds the margin.** 83–95 % of ensemble members have epochs
  *after* `t_tx`, so they share a common back-propagation error that σ_ref cannot
  see. The propagation-distance split-half spread is **5–16× the 5 % gate margin**
  (A-B3). S2 criterion 11 is not satisfiable on this label.
- **The baseline itself is not determined to 5 %.** Under a *generous* stratified
  imputation, six of nine satellites have a bound on the baseline MAE wider than
  the margin the test is trying to detect — up to 527 % (B-blocker analysis).

And beneath both: the residual is **0.006–0.36 % of the Doppler being
pre-compensated** — 0.18 mm/s of range rate for SENTINEL-6B, finer than any
TLE-derived quantity resolves. For some objects "the residual" is the catalogue's
own orbit-determination jitter. That is the property of the instrument, and no
construction on this archive removes it.

The only escape is a label that does not come from the catalogue: **measured
Doppler from actual RF reception**. That is the hardware path, explicitly outside
this authorization.

### What is worth keeping

Not as a paper — the pre-registration forbids rewriting the manuscript as a
negative or leakage result, and that instruction is correct, because a negative
about a premise is not a contribution. But as an internal research audit the
following are durable and reusable:

1. **The visible-pass scheduler.** Generating transmissions from stale-TLE-predicted
   passes is the correct construction for any endpoint-side study, and it is now
   implemented, tested and committed.
2. **The freeze-then-label discipline.** Hashing row membership before querying
   labels makes an entire class of leakage structurally impossible, and test V1
   detects it mechanically.
3. **The reference-ensemble label with published uncertainty.** This is the honest
   way to use catalogue elements as a reference, and it quantifies for the first
   time how uncertain that reference actually is.
4. **The censoring finding itself.** That inter-TLE residual labels are MNAR on
   staleness is a real methodological result about a construction used in the
   literature, and the measurement (|SMD| 1.25 on age; 4–13× publication-gap
   difference) is specific and reproducible.

Items 1–3 transfer directly to the SDR measurement campaign, where the label
comes from received signal rather than from a later element — and where this
entire class of bias does not arise.

### Standing state

Manuscript frozen and untouched. No E5, no E6, no PHY simulator, no neural
network, no favourable-cell search. Nothing committed to any manuscript branch.
Two commits on `exp15-visible-causal-rebuild`: `a97dab4` (pre-registration,
tagged) and `4bc5c46` (execution through R8).

## 16. Reviewer findings

### Reviewer B — selection bias, censoring, label uncertainty: **FAIL**

Reviewer B agrees the STOP is correct and the protocol's terminal action is the
right one, but judges my stated reason to capture **"perhaps 40 % of the actual
case"**. Three findings are more severe than anything I reported, and two are
corrections to my own gate design.

**B-BLOCKER 1 — the primary metric is a tail statistic. S2 could not resolve 5 %
even with perfect labels.** Independently computed: 50 % of a satellite's total
Σ|r| is carried by **3–20 passes**. IRIDIUM 181 — 14 rows of 17,647 (0.079 %),
**6 passes**; FLOCK 4H 2 — **3 passes**; FLOCK 4H 1 — 6; SENTINEL-6B — 16;
BLACK KITE-1 — 20. Mean/median |r| ratios run to **446×** (SENTINEL-6B) and 99×
(BLACK KITE-1). A "5 % improvement" would be one pass moving. This is
independent of censoring and I did not report it.

**B-BLOCKER 3 — my SMD ≤ 0.10 gate is uncalibrated.** Under a pass-level
permutation null with censoring forced MCAR, the observed max SMD exceeds 0.10
with probability **0.68–1.00** across satellites. The constant 0.10 sits below the
MCAR expectation ≈ 0.8/√(censored passes) for 6 of 9 objects. So the gate as I
pre-registered it partly measures sample size. Reviewer B's recalibration
separates the real signal from the noise: **genuinely imbalanced on age** —
ISS 0.897 vs null p95 0.164, SENTINEL-6B 1.192 vs 0.253, BLACK KITE-1 1.238 vs
0.189, both IRIDIUMs; **noise, not imbalance** — FLOCK 4H 1/2 and BLACK KITE-2.
Critically, **my headline number was the least trustworthy one**: 1.307/1.552 is
FLOCK 4H 2's *calendar-time* SMD on 13/18 censored passes (bootstrap CI
[0.772, 1.886]), and that satellite's *age* SMD is 0.031. Excluding calendar
time, the max is **1.238 (BLACK KITE-1 age) / 1.351 (SENTINEL-6B age)** — still a
12–14× breach, now attributable to the variable that matters. My MNAR-on-age
claim holds for 5 of 9 satellites; for FLOCK 4H 1/2 and BLACK KITE-2 the
censoring is calendar-time and partly end-of-archive.

**B-MAJOR 4 — my COMPLETE status is defined on the outcome.** `COMPLETE ⇔
σ_ref ≤ |r|`, so every completeness rate in the R3 and R6 gates is computed on a
subset selected by the *magnitude of the target*. Median |r| is inflated 4–11× in
COMPLETE versus AMBIGUOUS, and the mean baseline moves −21 % to +14 % — up to
**2.9× the entire 5 % gate margin**. Completeness as I gated it is partly an
inverse measure of how small the target is. This is a design error on my part.

**B-MAJOR 6/7 — the COMPLETE/AMBIGUOUS boundary is contaminated.**
`physical_element_key` excludes the epoch while `element_id` quantizes it to 1 ms,
so near-duplicate re-publications survive as "distinct" references: 2.3–16.6 % of
labelled rows have ≥2 members within 1 s. Smoking gun — SENTINEL-6B's n=2 rows
have σ_ref p50 = **0.048 Hz**, 15–70× smaller than any other satellite's, with
15.9 % of them containing a member pair < 600 s apart. Two re-fits of one solution
were counted as independent evidence. Separately, `1.4826·MAD` is parity-biased at
small n (E[σ̂] = 0.837/0.673/0.735 at n = 2/3/4; sd(σ̂)/σ = 0.63 at n=2), and the
data show exactly that zig-zag in AMBIGUOUS rate by reference count. The quantity
the gate is denominated in is partly set by the parity of how many elements
Space-Track happened to publish.

**B-MAJOR 8 — R8 was not actually performed.** Correct. I recorded within-pass ICC
and episode ACF but none of the four pre-registered chaining measurements.
Reviewer B measured them: `held(k+1) ∈ ensemble(k)` in **58.9–97.2 %** of adjacent
episode pairs (NOMINAL), 67.1–99.2 % (DEGRADED); adjacent-pass ensemble Jaccard
**0.67–0.80**; pass-mean ACF1 up to **0.896**. This is not causal leakage — the
`t_close ≤ t_refresh` rule is honoured — but the residual series is autocorrelated
by construction, and the plan's default block length of 4 should have been **18
passes** for SENTINEL-6B.

**B-MAJOR 9/10 — two further gaps.** R6's "independent closure-day blocks" share
47 of 48 hours of reference window, so R6 passed on a definition R8 forbids
treating as independent. And the **20° diagnostic arm was never labelled** — S2
criterion 9 is unaddressed even at gate level.

**Where Reviewer B says I was too harsh.** On the availability reading the gate
*passes*: labelled rate 0.938/0.933 ≥ 0.80 and min per-satellite 0.735/0.730
≥ 0.70. Only BLACK KITE-1 fails on genuine censoring (26.5 %); for ISS the
shortfall is 1.0 % censored against 12.6 % ambiguous. So the completeness failure
is substantially an *ambiguity* artifact of my outcome-dependent COMPLETE
definition, not censoring.

**Recoverability — Reviewer B tested all four routes I named, quantitatively.**
- **IPW**: positivity holds; costs ≤ 1.3 % of effective sample for 8 of 9
  satellites — routine. But BLACK KITE-1 loses 38 % ESS with weights to 10.2×, and
  its two deepest age deciles retain ~10 independent passes asked to represent 574
  rows. **Adopt as routine; does not recover the claim.**
- **Age restriction**: no cap gives age SMD < 0.10 for more than one or two
  satellites at once, because tightening the cap shrinks the censored arm and the
  calibrated null rises faster than the statistic falls. A 24 h cap keeps 30.7 % of
  BLACK KITE-1 and deletes most of DEGRADED. **No.**
- **Interval censoring**: unavailable — 62 % of BLACK KITE-1's and 45 % of ISS's
  censored rows have **zero** candidates in the window. Reaching the 2nd later
  element needs ~25-day horizons, which inflates σ_ref (0.568 → 0.903 → 1.520 Hz
  for 24 → 48 → 72 h) and, with BLACK KITE-2's archive only 102 days long, leaves
  ≤ 3 non-overlapping decision blocks. **No.**
- **Bounds**: the decisive analysis. Even a *generous* stratified [p5, p95]
  imputation gives bound widths on the baseline MAE of 2.4 / 5.3 / 5.6 / 7.3 /
  8.9 / 12.6 / 33.4 / 206 / **527 %**. **Six of nine satellites have a bound on the
  baseline itself wider than the 5 % margin the test is trying to detect.**

Reviewer B notes a narrower study *would* be defensible (7 objects, age ≤ 48 h,
IPW, labelled set, robust loss, ~10–15 % margin) but explicitly does not
recommend it, because reaching it means iterating on this archive — which the
pre-registration forbids. **REVIEWER B VERDICT: FAIL.** The conclusion of this
dossier is unchanged; its supporting case is stronger than I stated.

### Reviewer A — satellite visibility, timing, availability causality: **FAIL**

Three blockers, two of which are defects in **my own tests**. I verified both
myself rather than relaying them.

**A-B1 BLOCKER — row membership still depends on the future catalogue, and my V1
test was structurally incapable of detecting it. VERIFIED.** The provisioning grid
ends at the archive's *last* `CREATION_DATE` (`build_visible_registry.py:227`,
`last = t_end or avail[-1]["creation_dt"]`), and `main()` calls `build_registry`
with **no** `t_end` (`:366`). So publishing more elements creates more rows. My V1
test passes `t_end=t_end` on *both* arms, pinning the exact parameter that carries
the dependence.

I re-ran the production path (`t_end=None`) against an archive truncated by 30
days:

| satellite | rows, full archive | rows, −30 d | rows created by future publications |
|---|---|---|---|
| BLACK KITE-2 | 1,485 | 1,055 | **430 (29.0 %)** |
| BLACK KITE-1 | 2,870 | 2,480 | **390 (13.6 %)** |

`trunc ⊂ full` in both cases, so "no row is ever silently dropped" holds in the
letter while R1's substance fails. This is the previous pilot's defect re-expressed
as row *creation* instead of row *deletion*, and the commit message for `a97dab4`
singles out V1 as "the check the earlier work lacked". **That claim was wrong.** The
schedule is invariant to future *content* — no reference-derived quantity reaches
pass detection or sample placement, which Reviewer A confirms independently — but
not to future *extent*.

**A-M4 MAJOR — my test V4 is a tautology, and Reviewer A proved it by mutation.
VERIFIED by inspection.** `tests/test_visible_causal_integrity.py:134-135`:

```python
        fa = np.array([reg[n][i] for n in names])
        fb = np.array([reg[n][i] for n in names])
```

Both arrays are built from identical expressions reading the same object, so
`moved.sum() == 0` cannot fail. Reviewer A monkeypatched `label_row` to write
`ref_ensemble_hz` directly into the deployable feature column
`pred_stale_doppler_hz` and ran V4's body verbatim: **it passed under blatant
reference leakage.** The module docstring claims "Unlike the old A1/A2/A4 — which
asserted things true by construction and could not fail — every test here can
fail." V4 reproduces exactly the defect it disclaims. V5's hash check would have
caught that specific mutation, but nothing in the suite tests the proposition V4
names.

**A-B2 BLOCKER — `COMPLETE` is outcome-defined, and the one frozen decision was
made on it.** Independently reaching Reviewer B's B-MAJOR 4 from a different
direction, and going further: 48 h beats 72 h **only** on `complete_rate`, an
outcome-dependent statistic. On the coverage statistic that does not touch |r|,
72 h wins on both mean (0.9656 vs 0.9409) and minimum (0.7920 vs 0.7520) labelled
rate. So `R2_selection.json`'s assertion that "no model performance of any kind
was computed or inspected before this choice" is **not** satisfied in substance:
|r| is M0's error, and criterion 1 was read as "the horizon where the target is
largest relative to reference noise". Also confirmed: `frac_sigma_gt_r` is
*identically* `n_AMBIGUOUS/n_labelled`, so R7's headline is a tautology.

**A-B3 BLOCKER — σ_ref does not measure the label's uncertainty; the hidden
systematic exceeds the 5 % margin by 5–16×.** The strongest new finding. 83–95 % of
ensemble members have epochs **after** `t_tx` (median +15 to +22 h), so every
member is back-propagated in the same direction from the same OD lineage — their
errors share a common component that a mutual MAD cannot see. Splitting each
ensemble by propagation distance (< 12 h vs > 24 h) exposes it:

| satellite | \|D_near − D_far\| p50 | σ_ref p50 | 5 % of \|r\| p50 | ambiguity / margin |
|---|---|---|---|---|
| SENTINEL-6B | 0.405 Hz | 0.173 Hz | 0.026 Hz | **15.7×** |
| IRIDIUM 181 | 1.255 Hz | 0.590 Hz | 0.100 Hz | **12.6×** |
| ISS | 4.370 Hz | 2.201 Hz | 0.693 Hz | **6.3×** |
| BLACK KITE-1 | 2.101 Hz | 1.123 Hz | 0.423 Hz | **5.0×** |

Swapping the label from "ensemble median" to "the reference nearest `t_tx`" moves
the target by more than the target itself in 11.5–17.6 % of rows. And at K_min = 2
σ_ref is *anti-correlated with trustworthiness*: BLACK KITE-1's n_ref = 2 rows have
σ_ref 2.79 Hz against |r| 31.65 Hz, while its n_ref ≥ 5 rows have σ_ref 1.04 Hz
against |r| 7.41 Hz. The sparsest-publication rows — longest propagation, least
trustworthy label — are admitted COMPLETE with the largest residual. S2 criterion
11 is therefore **not satisfiable on this label**, and the previous pilot's
label-ambiguity defect was reduced ~3–4×, not eliminated as I claimed.

**A-M5 MAJOR — my censoring diagnosis is half right, and my two headline numbers
are wrong.** Confirmed: censoring is forward-looking and coincides with backward
staleness inside long outages (backward gap censored vs labelled — ISS 13.67 vs
3.12 h, BLACK KITE-1 47.22 vs 4.82 h; archive-tail censoring negligible at 20 of
716 ISS rows). **Refuted:** my `episode_time_s` variable is implemented as absolute
UNIX calendar time (`build_ensemble_labels.py:305`, `x = reg["t_refresh"]`), not
time *within* the episode. Under the intended reading (`t_tx − t_refresh`, a real
pre-transmission covariate) the worst SMD is **0.472**, not 1.307. Worse, in the
two cells driving my headline the staleness mechanism *does not hold*: FLOCK 4H 2
DEGRADED censored rows are **fresher** than labelled ones (46.70 vs 51.74 h) while
its calendar-time SMD reads 1.552.

**And the censoring is not irreducible — Reviewer A measured the fix.** Replacing
the fixed 48 h window with "the next K = 2 distinct solutions published after
`t_tx`", with data-dependent `t_close`:

| satellite | censored, fixed 48 h | censored, next-K | closure delay p50 |
|---|---|---|---|
| ISS | 1.02 % | **0.03 %** | 8.24 h |
| SENTINEL-6B | 5.26 % | **0.36 %** | 13.57 h |
| BLACK KITE-2 | 10.10 % | **0.34 %** | 16.51 h |
| BLACK KITE-1 | **26.48 %** | **0.35 %** | 20.93 h |

Censoring falls up to **76×** at a *shorter* median closure delay than 48 h,
trading MNAR censoring for measured heteroskedasticity. So my §14 claim that the
obstacle "is not a defect at all" is **too strong**: the fixed-horizon closure rule
is a design choice, and a better one exists. What survives is that fixing it does
not rescue the test — Reviewer B's independent finding that six of nine satellites
have a bound on the *baseline* wider than the 5 % margin, and Reviewer A's B3
showing label ambiguity at 5–16× the margin, both bind regardless.

**A-M6/M7/M8 MAJOR — three further overstatements.** (i) My "6 orbital regimes" is
6 mission labels over ~4 orbits: FLOCK 4H 1, FLOCK 4H 2 and BLACK KITE-1 have
semi-major axes agreeing to 0.93 km and periods to 19 ms — and my own
`analysis_plan.json` already merges them into one leave-one-out cluster, so R6
contradicts the analysis plan. (ii) My `coarse_step_justification` ("a 10° LEO pass
lasts ≥ ~4 min") is factually wrong: that is the *culminating* duration. Brute-force
1 s scanning found the minimum above-10° ISS pass is **15.0 s**, with 1.09 % under
60 s, and 3 of 366 passes were missed by the coarse scan. The dataset is internally
consistent only because `MIN_PASS_S = 60` discards the same set — which makes the
operative criterion "≥ 60 s above 10°", nowhere declared. (iii) `PROTOCOL.md:59`
claims the pass is an independent unit; within-pass ICC is **0.586–0.792** and
symmetric offsets (0.10/0.90) correlate up to **0.999**, so 5 samples are ~1.2–1.5
independent observations and the design yields 3 distinct geometry levels, not 5.
Within-episode ICC is 0.61–0.98, and BLACK KITE-1 has 220 episodes on 168 distinct
held elements with up to **23 consecutive episodes sharing one element**. My
`analysis_plan.json` is right; my protocol text is wrong.

**A-Q8 — the deepest point, which neither I nor Reviewer B made.** The residual is
operationally below the noise floor of the stated application. Median |stale
Doppler| is 10,860 Hz (ISS) against median |r| of 13.86 Hz — **0.128 %** — and for
SENTINEL-6B 8,475 Hz against 0.515 Hz, **0.006 %**, which is a range-rate
discrepancy of ~0.18 mm/s. No TLE-derived quantity is accurate to 0.18 mm/s. For
that satellite "the residual" is the archive's own orbit-determination jitter, not
a pre-compensation error. Also: my two provisioning scenarios are **not independent
replicates** — ISS yields 13,994 NOMINAL and 14,024 DEGRADED passes over the *same*
physical passes with the same `t0`, so the cross-scenario aggregate double-counts
geometry.

**Minor items accepted:** both ends of the provisioning grid are properties of the
download (`avail[0]`, `avail[-1]`), and nothing attests the archive snapshot or the
`MULTISAT_SAME_EPOCH_POLICY` environment variable (m9). Episode-boundary pass loss
is small but deterministic and scenario-asymmetric — 0.43 % NOMINAL vs 0.15 %
DEGRADED, always at one fixed UTC hour (m10). Epoch regression occurs at 4.88 % of
ISS records but only 0.26 % of realized refreshes (m11). My R4 disagreement rate is
understated 2–67× because rows with reference elevation in [0°, 10°) fall in
neither bucket — same defect Reviewer B found (m12). Elevation uses the geocentric
rather than geodetic vertical, a 0.143° error at 24 °N putting 192 ISS rows below
the true mask (m13). The `cid in held_key` self-exclusion test is dead code (0 of
28,252 candidates) and is an epoch-equality test with a weak tie-breaker, not an
identity test (m14a). Reviewer A also **corrects Reviewer B** on key collisions:
they are not "across distinct epochs" but 864 µs duplicate publications
(= 1e-8 day, the TLE epoch print quantum) that my upstream 1 ms *truncation* failed
to collapse — so ensemble distinctness is adequate, but the availability sequence is
inflated up to 12.05 %, which feeds B1's `avail[-1]`, `held_element` and the
interarrival features (m14b).

**Verified clean by Reviewer A.** No reference-derived quantity influences pass
detection or sample placement. The reversed-bracket fix is correct with no second
bug: `[entry, exit]` ⊂ the true visible interval, minimum elevation 10.034–10.142°
at the 10° mask and 20.05–20.29° at 20°, zero interval overlaps or inversions in
1,336 checked intervals, every pass carrying exactly 5 rows. No negative
`age_tx_s`; every `t_tx − t_refresh` inside `[0, interval)`. **Pre-registration
integrity holds**: `git diff a97dab4 HEAD` on all six pre-registered files is
empty. And the R3 failure was not hidden — `R3_VERDICT: FAIL` is in both audits and
`R2_selection.json` recorded the risk before labelling.

### What both reviewers confirmed sound

No future-dependent row membership — `build_registry` consults only the held
element, UTC and the fixed ground station; the defect that killed the previous
pilot is genuinely fixed. Registry immutability is asserted mechanically and
holds. The SMD implementation matches the pre-registered formula to 4 decimals.
The R2 horizon/`K_min` selection is honest and self-incriminating: 72 h scores
*better* on the lenient reading that would have let the gate pass, and I chose
48 h and pre-recorded the risk. The ensemble label is a real, large improvement —
at 8 h staleness the uncertainty ratio is 5.4× better and the exceedance rate
2.4× better than the single-reference construction.
