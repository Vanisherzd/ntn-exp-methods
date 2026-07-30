# PRE-IMPLEMENTATION REVIEW — FINDINGS AND RESOLUTION

Independent reviewer: physical-simulator and falsifiability. Verdict **HOLD**,
4 BLOCKERs and 8 MAJORs. The reviewer built a working scratch emulation with real
SGP4 and ran the full protocol over 27 cells × 12 seeds before writing.

No production simulator code has been written. Nothing committed.

I verified the two decisive findings myself rather than accepting them:
`debug_probe_shift_harm.py` and `debug_probe_manoeuvre.py`.

---

## BLOCKER 1 — the pre-registered shift cannot produce harm. **CONFIRMED. Design changed.**

The reviewer's arithmetic: post-shift `r_dep = k·r`; a corrector trained pre-shift
predicts `r̂ ≈ r`; therefore

```
MAE_alwayson / MAE_physics = E|k·r − r| / E|k·r| = |k−1| / |k|
harm  ⟺  |k−1| > |k|  ⟺  k < 0.5
```

My reproduction:

| shift | k | B/A | verdict |
|---|---|---|---|
| **magnitude ×4 (as pre-registered)** | 4.00 | **0.750** | **helps** |
| magnitude ×2 | 2.00 | 0.500 | helps |
| magnitude ×10 | 10.0 | 0.900 | helps |
| magnitude ×0.49 | 0.49 | 1.041 | HARM |
| **sign flip** | −1.00 | **2.000** | **HARM** |

A magnitude *increase* leaves an under-scaled correction still pointing the right
way, which always helps. The reviewer measured the consequence over the full grid:
**0/324 harmful overrides, gate open 324/324, C2 validation ratio 0.60–0.65** —
validation *improves* after the shift. My §5 headline number was 0/0, my §8 success
criterion 2 was unmeetable, and Fig. 2's harmful quadrant was empty by
construction. My stated C2 mechanism ("validation degrades ⇒ close ⇒ fall back")
was **inverted**.

### Resolution — a manoeuvre, with harm that emerges rather than being imposed

The shift becomes an **impulsive in-plane Δv applied to the true orbit at onset** —
a station-keeping or reboost burn, which is what the archived real-data audit
identified as the source of the unpredictable residual tail (finding S2-3).

```
tangential burn:  δa = 2a·Δv/v ,  δn_true = −1.5·n·δa/a
pre-shift  gap g0 = s·Δn      (s = ±1, drawn per seed)
post-shift gap g1 = g0 − δn_true ,  k = g1/g0
```

**Δv = +1.7 cm/s prograde**, direction **fixed by physics**, never tied to `s`:

| regime | δn_true (rev/day) | s = +1 → k | s = −1 → k |
|---|---|---|---|
| R1 low/SSO | −1.019e−4 | +3.04 helps | **−1.04 HARM** |
| R2 mid/polar | −9.840e−5 | +2.97 helps | **−0.97 HARM** |
| R3 upper/polar | −9.231e−5 | +2.85 helps | **−0.85 HARM** |

Measured at R1: `s = −1` → MAE_A 0.829, MAE_B 1.627, **B/A = 1.963 HARM**;
`s = +1` → B/A = 0.671 helps.

Three properties matter. **Harm emerges** from whether the burn happens to oppose
the pre-existing OD error — about half of seeds — and is never forced. **The
direction is physical**, not chosen against the error sign; tying it to `s` would
be rigging and is explicitly forbidden. **1.7 cm/s is modest**: real
station-keeping burns are 0.1–1 m/s, so this is an order of magnitude *below*
routine.

The expected harmful-override rate is therefore ≈ 50 %, not 0 % and not 100 % —
which makes the gate's job non-trivial and the number informative.

---

## BLOCKER 2 — refresh policy undefined, and it decides the floor verdict for 9 of 27 cells. **ACCEPTED.**

`t_refresh` appeared twice and was never defined. The reviewer measured the
consequence: the whole S1 staleness row flips between `INSUFFICIENT_RESIDUAL_SCALE`
and eligible on this undeclared parameter (3.4–4.3e−4 at 6 h refresh versus
1.04–1.36e−3 at 24 h — a 3.9× swing). With no refresh at all, age spans 1440 h,
the three staleness levels differ by ≤ 5 % and **the staleness factor of the grid
collapses to noise**. If age were constant, `age_s` would have zero variance and
M1 would degenerate to a constant.

**Resolution:** `refresh_interval_h = 24.0`, pre-registered as a numeric constant,
and **added to the forbidden-tuning list**. Staleness is then implemented as the
element's age at the *start* of its holding interval, so age at transmission spans
`[S, S + 24 h)` and `age_s` retains variance without the levels overlapping.

---

## BLOCKER 3 — M3's observation model unspecified; one reading breaks the negative control. **ACCEPTED.**

A Kalman filter on the residual must observe the residual, which is
`D_reference − D_physics` — i.e. **truth**. The reviewer ran both readings under
N0, where Δ = 0 exactly and my §15 asserts a broken benchmark if a gain appears:

| cell | physics | M3 frozen | **M3 live** | live/phys | gate-open |
|---|---|---|---|---|---|
| R1/S3 | 2.572 | 2.639 | **2.209** | 0.859 | 0.67 |
| R2/S3 | 1.974 | 2.019 | **1.561** | 0.791 | 0.92 |
| R3/S3 | 1.354 | 1.378 | **0.928** | 0.685 | 0.92 |

M3-live yields a **14–31 % stable held-out gain and 67–92 % gate-open rate on a
null cell**. Not a coding error: the OU is mean-reverting with τ = 48 h, so the
pass-mean residual is an autocorrelated bias a tracker legitimately predicts — if
allowed to keep observing truth. And **no test in my suite covers this channel**:
W3 leaks truth into "a feature column"; model state is not a feature column. This
is the V4 failure mode again — the test's scope does not cover the leak's channel.

**Resolution:** M3 observes **only labels closed before the freeze**; its state is
frozen with the model and scaler, and it receives no observation during
deployment. Declared explicitly in the config. **W3 is extended to model and
scaler state**, not only feature columns, and a new W4 asserts the deployment
predictor's state is byte-identical before and after the deployment window.

---

## BLOCKER 4 — my "repaired" V4 asserts an invariance that is FALSE here. **ACCEPTED.**

Three of nine features are `stale_mean_motion`, `stale_bstar`, `stale_ecc`, and the
held element is a *sample of the truth process*, so
`stale_mean_motion = n0 + ndot·t_ep + OU_n(t_ep) + Δn` contains the OU realisation
exactly. Re-drawing the truth realisation *legitimately* moves it — and moves the
geometry features with it, since the schedule is found from the held element. On a
correct implementation **V4-repaired goes red**. Both natural repairs are fatal:
pinning the OU seed recreates V1's exact defect, and dropping the columns empties
the test. It also falsifies my claim that the schedule is "seed-independent by
construction" — it is not.

**Resolution:** V4 is replaced by the invariance that is actually true and
load-bearing —

- **V4a (purity):** features are recomputed from `e_held` alone in an *independent
  code path* and compared bitwise. Proposition: features are a pure function of
  `(e_held, t_tx, GS config, static config)`.
- **V4b (truncation):** features are recomputed with the OU path **and the shift
  onset** truncated at `t`, asserting bit-identity. This is V1's proposition in the
  form that can fail here.

**V9** (config-versus-code offset equality), **V10b** (gate source touches no
deployment data) and **V2** (registry builder contains no label machinery) are
**re-instated** — the reviewer notes these were among the tests previously verified
sound, and dropping the sound ones while porting the two that failed inverts the
selection.

---

## MAJORS — resolutions

**M5 — C2/C3 differ in three things, only one being timing.** Measured deployment
exposure 1.00 (C2) vs 0.75–0.81 (C3); model selection flips M2→M1 in 2/9 C2 cells
and 0/9 C3; C2's own validation exposure varies 4× across seeds. **Fix:** C3 onset
moves to the **deployment-window start**, giving exposure 1.00 in both;
validation-exposure fraction becomes a pre-registered reported covariate; and the
shift is declared to apply **from the next refresh adoption**, not retroactively.

**M6 — the asymmetric offsets do not decorrelate.** Measured 0.9986–0.9997 — the
exact pathology the change was meant to fix, because the mirror of 0.80 is 0.20,
only 0.05 from 0.15. Range is worse: all six pairs above 0.994, since slant range
is dominated by the pass's maximum elevation, shared by all offsets. **Fix:** I
withdraw the claim that offsets "break the symmetry" — within a single pass,
elevation and range trace one smooth unimodal curve and *cannot* be decorrelated by
choosing sample positions. Reduced to **3 offsets (0.20/0.50/0.80)**, declared as
**replicates within a pass, not independent geometry**. Geometric diversity comes
from *across-pass* variation in maximum elevation, and WP9's threshold moves there.

**M7 — WP7 cannot detect the degeneracy that matters.** An oracle two-parameter
model on `(Ḋ, Ḋ·age)` reaches **R² = 0.997–0.999** while WP7's single-feature
maximum reads only 0.66–0.77. The residual is `r ≈ −Ḋ_physics(t)·(c₁·age + c₀)`,
and Doppler *rate* is trivially computable by any terminal that computes Doppler —
so my nine-feature list made the benchmark's difficulty a free parameter disguised
as an inheritance. **Fix:** `doppler_rate_hz_per_s` is **added** as a tenth
feature. Excluding it had no physical justification. C1 becomes strongly learnable,
which is the honest outcome and sharpens the paper: the contribution is admission,
not whether learning is hard. New **WP10** checks the R² of an oracle built from
admissible quantities, replacing single-feature correlation as the anti-circularity
guard.

**M8 — my SNR expectation was backwards.** The OU-induced along-track error grows
as `A^1.5` while the systematic term grows as `A`, so `SNR ∝ A^(−1/2)`. Predicted
87→43→25 at 6/24/72 h; reviewer measured **187→75→40**. **Fix:** the pre-registered
expectation is **inverted** — the gate should be *most* likely to admit at **short**
staleness, where SNR is highest, and the systematic term's growth does not
outrun the noise.

**M9 — "magnitudes fixed, only signs drawn" gave an 8.5× swing.** `Δn` at 6 h
contributes 0.54 km of along-track error and `ΔM₀ = 0.005°` contributes 0.60 km —
commensurate, so independent sign draws give |0.54·s_n + 0.60·s_M| ∈ {1.14, 0.06}
km, a 19× ratio from a coin flip, flipping the floor verdict per seed. **Fix:**
`delta_mean_anomaly` is **removed** — it is redundant with `Δn` and was the sole
source of the commensurability. A small **out-of-plane `delta_incl_deg`** is added
instead, which also answers MINOR 14 by making the residual genuinely
two-dimensional rather than a scalar time offset.

**M10 — the floor was set below the magnitude the project's own audit condemned.**
The floor was 0.1 % while the archive's pathological ISS case was 0.128 %. **Fix:**
floor raised to **0.2 %**, with the resolution argument stated numerically. I
pre-register the expectation that **the S1 (6 h) row may fail this floor and be
labelled `INSUFFICIENT_RESIDUAL_SCALE`** — and that is a finding, not a failure:
it would say short-staleness residuals are not worth correcting, mirroring the real
archive. Recorded now so it cannot later be rescued by raising `Δn`.

**M11 — five sound tests were dropped.** V9, V10b, V2, V10, V5 re-instated (V5
subsumed by W2). Notably V10b was the only test asserting the gate reads validation
only — the paper's entire claim.

**M12 — truth element-sequence continuity unspecified.** If mean anomaly is not
integrated continuously and RAAN/argp are not advanced at SGP4's secular rates, an
SSO node precessing ~1 °/day injects ~15 km cross-track discontinuities every 6 h
that would raise median |r| (helping every cell clear the floor) while passing
every stated check. **Fix:** the construction is specified explicitly — continuous
mean-anomaly integration and SGP4 secular rates — and a new **WP11** asserts truth
Doppler continuity across every element-grid boundary to a numeric tolerance.

**Minor items accepted:** boundary-straddling passes must not place validation
samples after the freeze instant (M13 — deployment assignment is by *entry* window
but samples after the freeze instant are dropped); the minimum-pass declaration is
inert here (shortest pass 72.5–171 s, 0 % under 60 s) but retained as a
declaration; coarse step and bisection tolerance are added to the config; a
geodetic-vertical assertion test is added, since reverting to geocentric currently
goes undetected; and two false statements are withdrawn — the OU *is* partially
observable through `stale_mean_motion`, and the schedule is *not* seed-independent.

---

## What I am NOT doing

The reviewer notes the grid varies regime, staleness and condition, **none of which
is a correctness axis** — so a defect in the simulator, feature list or shift
specification is invariant across all 324 runs and appears as a uniform result
rather than as variation. Their emulation produced exactly that: 27/27 cells
identical in both reported quantities.

**Uniformity across the grid is therefore added as a pre-registered failure
signal.** If every cell returns the same answer, the benchmark is replicating one
measurement 324 times, not measuring anything.

I am also recording, per the reviewer's Q1, that `Δ` applied identically to every
held element for 60 days is **not** what a real catalogue does, and is the sole
reason C1 is learnable. That is now stated as a declared limitation rather than
described as realism.
