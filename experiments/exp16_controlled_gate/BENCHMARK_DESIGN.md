# CONTROLLED EVIDENCE-GATE BENCHMARK — DESIGN v2

Branch `workshop-controlled-evidence-gate`, cut clean from `main`.
**Design only. No production simulator written. Nothing committed. Manuscript untouched.**

> ## v2 REVISION — final design-revision cycle
>
> The first independent review returned **HOLD** with 4 BLOCKERs and 8 MAJORs, after
> building a working SGP4 emulation and running the full 27×12 protocol. Findings and
> resolutions: **`REVIEW_RESOLUTION.md`**. Authoritative parameters:
> **`physical_config.json` (v2)**.
>
> Changes that alter the science, not just the wording:
>
> | was | now | why |
> |---|---|---|
> | ×4 magnitude shift | **1.7 cm/s prograde manoeuvre** | `|k−1|/|k| = 0.750` — a magnitude increase *always helps*. Measured 0/324 harmful overrides. Harm needs a direction change. |
> | `t_refresh` undefined | **24 h, pre-registered, untunable** | flipped 9 of 27 cells' floor verdict; with no refresh the staleness axis collapses |
> | M3 observation unspecified | **frozen through the episode** | M3-live gave a 14–31 % gain on N0 (Δ = 0) — a broken benchmark by my own §15 |
> | "V4-repaired" | **V4a purity + V4b truncation** | the v1 assertion is *false* here and would go red on a correct implementation |
> | 9 features | **10, adding Doppler rate** | omitting it made difficulty a free parameter; oracle R² 0.998 vs WP7 reading 0.77 |
> | C3 onset in first 40 % of deployment | **at deployment start** | exposure was 0.75–0.81 vs C2's 1.00 — a confound in the paper's core contrast |
> | 4 "asymmetric" offsets | **3 offsets, declared repeated measures** | measured 0.9986–0.9997; within-pass geometry *cannot* be decorrelated |
> | floor 0.1 %, cells excluded | **0.2 %, all cells retained** | 0.1 % sat below the 0.128 % my own audit condemned |
> | `ΔM₀` | **`Δi`** (out-of-plane) | `ΔM₀` was commensurate with `Δn`, giving an 8.5× swing from a sign draw |
> | seeds 1001–1012 | **`EVALUATION_SEEDS_V2`, never run** | the reviewer inspected outcomes on 1001–1012; they are burned |
> | "gate opens at long staleness" | **short staleness** | SNR ∝ A^(−1/2); measured 187→75→40 |
>
> **C1 is expected to be labelled a CONTROLLED CALIBRATION / SANITY SCENARIO**, because
> with Doppler rate in the feature set M2 is expected to exceed the 0.95
> functional-form-match threshold. Recorded in advance. The paper's scientific weight
> rests on C2 and C3.
>
> ### v2.1 — three further mandatory items
>
> **A. Common random numbers.** My v2 seed rule keyed on `scenario_key` *including the
> condition*, so C1/C2/C3 received **different physical realisations** — silently
> violating the design's central claim and making every condition comparison unpaired.
> Regenerated: `base_seed(regime, staleness, index)`, shared by all three conditions.
> N0 in a separate namespace. The unexecuted v2 manifest is retired at no cost.
>
> **B. The absorption conflict — confirmed fatal, and reported rather than hidden.**
> v2 said a manoeuvre is absorbed at the next refresh. Measured across all six
> condition × staleness combinations:
>
> | condition | staleness | t_shift | t_absorb | verdict |
> |---|---|---|---|---|
> | C2 | 6/24 h | 42.0 | **43.0** | absorbed **inside validation** |
> | C2 | 72 h | 42.0 | **45.0** | absorbed **inside validation** |
> | C3 | 6/24 h | 48.0 | **49.0** | absorbed **mid-deployment** |
> | C3 | 72 h | 48.0 | **51.0** | absorbed **mid-deployment** |
>
> The mismatch vanished before deployment opened in C2 and one day into a twelve-day
> deployment in C3. **C2 was not a valid protection experiment and C3 was not a valid
> boundary experiment.** Simplification adopted: **two truth streams** —
> `e_true_nominal` (no manoeuvre) generates held elements; `e_true_actual` (with
> manoeuvre) generates labels. The burn is **unreported**, never absorbed within the
> run. Declared as a simplification of the operational timeline, not as catalogue
> behaviour. Shortening deployment below the absorption lag would need a window under
> one day; the refresh interval is untunable.
>
> A useful consequence: held elements, pass schedule and **every feature row are now
> bit-identical across C1/C2/C3**, so the conditions differ *only* in labels after
> onset. Maximal pairing, asserted by **W5**.
>
> **C. C2 onset fixed.** No longer randomised over the middle 60 % of validation —
> **fixed at the validation midpoint, exposure exactly 0.500**. v2's randomisation let
> seed variation change evidence *duration* (0.20–0.80), making C2 a continuum rather
> than a condition. Exposure sensitivity is out of scope for this phase.
>
> Timeline, both orderings **SATISFIED**: C2 36 < 42 < 48 = freeze ≤ 48 < 60 < ∞;
> C3 48 = freeze < 48 (first deployment transmission) ≤ 48 < 60 < ∞. Asserted by **W6**.
>
> No v3. If the second review finds a new core-physics BLOCKER, the benchmark is
> simplified or EXP16 stops.

---

## 1. Research question

> **Can an evidence gate prevent unreliable learned residual corrections from
> overriding a strong SGP4-style physics baseline in a controlled, causally valid
> software benchmark?**

The contribution is **the admission decision and its behaviour**, not a model, not
a dataset, and not a real-world result. The benchmark is an instrument for
observing the gate under known ground truth — the software analogue of testing a
controller against a characterised plant.

### The design risk, stated up front

A simulator built by the same person who wants the gate to work can be tuned until
it works. That would make the paper an advertisement. Three structural defences:

1. **Pre-register exact numeric settings before any model is fitted** — same
   discipline as the archived real-TLE line, which is now the reason we trust its
   negative result.
2. **Include a cell where the gate provably cannot help, and report it.** See §5,
   condition C3. A gate paper that shows only wins is not evidence.
3. **Report the gate's protection boundary as a primary result**, not a
   limitation buried at the end.

## 2. Controlled benchmark specification

Fully observed by construction. Every defect that killed the real-TLE route is
structurally absent:

| real-TLE failure | why it cannot occur here |
|---|---|
| labels missing-not-at-random on TLE age | truth is generated for **every** scheduled transmission; censoring rate is exactly 0 |
| row membership decided by future publications | the schedule is generated **before** any target is computed, and hashed |
| reference ambiguity (σ_ref ≳ \|r\|) | one unambiguous reference trajectory; no ensemble, no σ_ref |
| MAE set by 3–20 tail passes | noise process is specified and bounded; tail concentration is **measured and gated** (§7) |
| below-horizon transmissions | transmissions scheduled inside predicted-visible passes only, reusing the audited pass finder |

### The five distinguished quantities

The simulator keeps these strictly separate, and the code names them apart:

| # | quantity | definition |
|---|---|---|
| 1 | **reference/controlled trajectory** | truth. Propagated from a reference element set with a designed secular perturbation plus a bounded stochastic along-track term. |
| 2 | **stale/degraded orbital state** | what the endpoint holds. The reference element set at an earlier epoch, plus an injected element-error vector. |
| 3 | **model-derived Doppler truth** | Doppler computed from (1) at the fixed ground station. **Never called measured Doppler.** |
| 4 | **SGP4-style predicted Doppler** | Doppler computed from (2), propagated to the transmission instant. This is the physics baseline M0. |
| 5 | **residual target** | `r = (3) − (4)`. |

### Generative mechanism — why a residual is learnable

The injected element error (2) is a **persistent** offset in mean motion and drag:
`Δn` and `ΔB*`. Propagating a mean-motion offset for a duration `a` produces an
along-track phase error growing as `Δn·a`, which maps into a Doppler residual that
is a smooth deterministic function of `(age, orbital phase, elevation, range)` —
all computable at the transmission instant from the held element and UTC alone.
That is a genuinely causal, genuinely learnable structure.

Learnability is then controlled by the ratio of that systematic term to a bounded
stochastic term (Ornstein–Uhlenbeck along-track perturbation on (1)). **Staleness
is the natural SNR knob**: longer age ⇒ larger systematic residual ⇒ higher SNR.

**Pre-registered expectation — CORRECTED in v2, and my v1 version was wrong.**
The systematic term grows as `A`, but the OU-induced along-track error grows as
`A^1.5`, so **SNR ∝ A^(−1/2)**: predicted 87/43/25 at 6/24/72 h, reviewer measured
187/75/40. The gate should therefore be **most** likely to admit at **short**
staleness. v1 predicted the opposite, and was falsified before a line of production
code was written — which is the value of stating a prediction at all.

### Causality contract

Every deployed feature must be computable from: the held element set, the
transmission UTC, the fixed ground-station configuration, static config, and
frozen model/scaler/gate state. Feature list (9, deliberately identical in spirit
to the audited real-TLE manifest, with no epoch-gap term):

`age_s`, `pred_doppler_hz`, `sin_phase`, `cos_phase`, `elevation_deg`,
`range_km`, `stale_mean_motion`, `stale_bstar`, `stale_ecc`.

**Reused code is quarantined until re-verified, and two ported tests must be
repaired before they are trusted.** Independent review of the archived build found
that two of its six integrity tests were structurally incapable of failing, and I
verified both:

- **V1 pinned the parameter carrying the dependence** it was meant to test, so it
  could not detect that the schedule's *extent* depended on later publications.
  The repaired version must truncate the future and compare against an
  independently rebuilt schedule. Here the defect cannot arise at all — the
  benchmark's time span is a pre-registered constant, not `avail[-1]` — but the
  test must still be able to fail, and W2 below is the version that can.
- **V4 compared two feature vectors built from the same object** — literally
  identical expressions — so it passed under a mutation that piped the reference
  value straight into a deployable feature column. The repaired version rebuilds
  the registry independently under a re-drawn truth realisation and compares those.

Ported and repaired: V3 (all transmissions above mask), **V4-repaired** (features
invariant when the truth realisation is re-drawn, from independently rebuilt
registries), V8 (no forbidden feature). Plus three new:

- **W1 — label completeness is exactly 1.0.** Every scheduled row has a target.
- **W2 — target generation cannot alter the schedule.** Hash the schedule, generate
  truth, re-hash, assert equality. This is V1's proposition in a form that can fail.
- **W3 — mutation canary.** Deliberately leak the truth into a feature column and
  assert the suite goes red. A test suite that cannot detect an injected defect is
  not evidence, which is exactly the lesson V4 taught.

Four repairs also carry into the scheduler: declare the minimum pass duration as
part of the visibility criterion (the archived config justified a 60 s coarse step
with a "≥ 4 min pass" claim that is false — the true minimum above-10° pass is
**15 s**, so the operative criterion was really "≥ 60 s above 10°" and was
undeclared); use the **geodetic** local vertical rather than the geocentric radius
(a 0.143° error at 24 °N); handle passes straddling a window boundary rather than
dropping them from both sides; and record within-pass correlation rather than
assuming sample independence.

## 3. Scenario and configuration table

Orbital regimes use **real object element ranges** for domain realism, verified
against the archived cohort:

| regime | altitude | inclination | mean motion | real analogue |
|---|---|---|---|---|
| **R1 low / SSO-like** | 500 km | 97.42° | 15.21 rev/d | FLOCK 4H, BLACK KITE-1 |
| **R2 mid / near-polar** | 750 km | 86.45° | 14.43 rev/d | IRIDIUM 181 |
| **R3 upper / near-polar** | 1200 km | 87.89° | 13.11 rev/d | ONEWEB-0015 |

Staleness levels (age of the held element at the start of its deployment window):

| level | age |
|---|---|
| **S1 short** | 6 h |
| **S2 medium** | 24 h |
| **S3 long** | 72 h |

Conditions — **three, not two.** The user's spec named nominal and shift; the shift
case splits into two structurally different cases, and the split is the scientific
core of the paper:

| condition | element-error process | what the gate should do |
|---|---|---|
| **C1 nominal mismatch** | `Δn`, `ΔB*` drawn once per run, then **stationary** | open where SNR is sufficient; admission should help |
| — | *and the residual must be physically meaningful: see the scale floor below* | — |
| **C2 shift observable pre-freeze** | error magnitude changes by a fixed factor at a changepoint **inside the validation window** | validation degrades ⇒ **close** ⇒ fall back to physics ⇒ damage avoided |
| **C3 shift latent post-freeze** | error changes **strictly after validation ends**, before the deployment window | validation is clean ⇒ gate **opens** ⇒ harm occurs. **The gate cannot help here.** |

**C3 is not a failure of the design; it is the result.** The gate is a
validation-time instrument, so it can only prevent harm that is observable before
the freeze. Quantifying that boundary is more useful to a reviewer than another
win, and it is the honest answer to "does fallback under distribution shift reduce
damage?" — yes if the shift is observable pre-freeze, no otherwise.

Grid: **3 regimes × 3 staleness × 3 conditions = 27 cells × 12 seeds = 324 runs.**
Compact enough to run in minutes; large enough to show variation. Exact numeric
values for `Δn`, `ΔB*`, the OU parameters, the shift factor and the changepoint
offsets are fixed in `scenario_config.json` before evaluation.

Fixed across all runs: ground station 24.0 °N / 121.0 °E / 100 m; carrier 868 MHz;
10° elevation mask; chronological 60/20/20 train/validation/deployment split;
γ = 0.95.

**Transmission offsets — 3 offsets, declared as repeated measures.** My v1 claim
that asymmetric offsets 0.15/0.35/0.55/0.80 "break the symmetry" was **measured
false**: pairs correlate at **0.9986–0.9997**, the exact pathology the change was
meant to fix. The mirror of 0.80 is 0.20, only 0.05 of a pass from 0.15, and slant
range is dominated by the pass's maximum elevation, which all offsets share.

Within a single pass, elevation and range trace one smooth unimodal curve and
**cannot** be decorrelated by choosing sample positions. So: **0.20 / 0.50 / 0.80,
declared as repeated numerical samples, not independent geometry.** Geometric
diversity comes from *across-pass* variation in maximum elevation. Aggregation is
strictly `time samples → pass → seed/cell → regime`, and measured within-pass
correlations are documented without a pass/fail threshold attached — a threshold on
a quantity known to sit at 0.999 would be theatre.

## 4. Candidate family

| id | model |
|---|---|
| **M0** | physics baseline, zero residual (not gate-eligible) |
| **M1** | linear age correction |
| **M2** | causal ridge on the 9 static features |
| **M3** | causal bias/drift tracker (two-state Kalman on pass-mean residual) |

No neural networks. The paper is about admission, not capacity. A larger family
would invite "you just needed a better model", which is the wrong axis.

## 5. Gate evaluation protocol

```
train (60%)         fit M1, M2, M3
validation (20%)    select m* = argmin val MAE;  G = 1[MAE_m*(V) < γ·MAE_M0(V)]
FREEZE              model, scaler and G frozen before the deployment window opens
deployment (20%)    evaluate, never re-selecting and never re-gating
```

Three arms compared on the deployment window — **this comparison is load-bearing**:

| arm | predictor |
|---|---|
| **A physics** | `f_phys` |
| **B always-on** | `f_phys + r̂_m*` regardless of validation evidence |
| **C evidence-gated** | `f_phys + G·r̂_m*` |

Primary questions and how each is answered:

1. *How often does an always-on branch harm held-out performance?* — fraction of
   the 324 runs where arm B's deployment MAE exceeds arm A's.
2. *How many harmful overrides does the gate prevent?* — runs where B harms **and**
   `G = 0`, as a fraction of all runs where B harms. This is the headline number.
3. *When a stable residual exists, can the gate still admit useful corrections?* —
   within C1, the admission rate and the realised benefit of arm C over arm A.
4. *Under distribution shift, does fallback reduce damage?* — C2 versus C3,
   reported separately. The contrast **is** the answer.

Statistical unit: the **run** (one regime × staleness × condition × seed). Within a
run, aggregate samples → passes → deployment window. Uncertainty by bootstrap over
seeds within cell and over cells; no per-sample inference. Reviewer B's finding
that intra-pass ICC reached 0.59–0.79 on real data is the reason this is fixed in
advance rather than discovered later.

## 6. Metrics

Primary: residual-frequency **MAE** (Hz); validation improvement (%); held-out
improvement (%); **gate-open rate**; **harmful-override rate**; **fallback rate**.

Secondary, driven directly by Reviewer B's B-BLOCKER 1: a **robust central metric**
(trimmed mean at 5 %, and median absolute residual) reported alongside MAE, plus
the **top-1 % share of Σ|r|** as a well-posedness check. On the real archive that
share reached 0.76 and 50 % of the metric sat in 3 passes; a benchmark that
reproduces that pathology is not measuring the gate.

Optional, clearly labelled if included: **one** software frequency-control proxy —
the fraction of transmissions whose residual exceeds a stated tolerance. Labelled a
proxy, in software, with no packet, PER or PHY interpretation. No LR-FHSS
simulator.

## 7. Well-posedness self-checks (run before any gate result is interpreted)

| check | requirement |
|---|---|
| label completeness | exactly 1.000 (test W1) |
| top-1 % share of Σ\|r\| | < 0.10 in every cell |
| passes carrying 50 % of Σ\|r\| | ≥ 10 % of the cell's passes |
| C1 residual autocorrelation | stationary across train/validation/deployment |
| feature causality | tests V1/V3/V4/V8/W1/W2 all pass |

If the tail check fails, the noise process is mis-specified and must be fixed
**before** any model is fitted — a benchmark whose metric is hostage to three
passes cannot demonstrate a 5 % admission margin either.

**Residual scale floor — added on review evidence.** The sharpest finding against
the archived line was that its residual was **0.006–0.36 % of the Doppler being
pre-compensated** (0.18 mm/s of range rate for one object), i.e. finer than the
instrument resolves, so for some objects "the residual" was catalogue jitter. A
simulator can trivially reproduce that pathology and then "learn" it. Therefore, as
a pre-run check: in every cell the median |r| must be **≥ 0.1 % of the median
|predicted Doppler|**, and the pre-registered `Δn`/`ΔB*` magnitudes must correspond
to a stated, physically defensible element-error size. A cell below the floor is labelled **`INSUFFICIENT_RESIDUAL_SCALE`** and
**retained**. The floor is **diagnostic only**: it must not exclude a cell, exclude
a seed, alter model fitting, alter success criteria, or trigger retuning.
Threshold raised to **0.2 %** — v1's 0.1 % sat *below* the 0.128 % that my own
archived audit identified as unresolvable. `Δn` stays at 5×10⁻⁵ rev/day.

**Pre-registered expectation: the S1 (6 h) row may fall below the floor.** That
would be a *finding* — short-staleness residuals not worth correcting, mirroring
the archived real-data result — not something to rescue by raising `Δn`.

## 8. Minimum success gate

The paper proceeds only if **both** hold:

1. ≥ 1 scenario where a causal residual is learnable **and the gate admits it**
   (expected: C1 at S3 long staleness);
2. ≥ 1 shift scenario where always-on **harms** and the gate **retains physics**
   (expected: C2).

If the gate never opens in controlled learnable scenarios → debug or revise the
method before writing. If the gate always opens, or never prevents harm → **stop**.

## 9. Claims allowed and prohibited

**Allowed:**
- an evidence gate can be specified so selection and admission read validation only;
- in a controlled software benchmark with known ground truth, an always-on learned
  residual branch harms held-out accuracy in *X* of 324 runs;
- the gate prevents *Y* % of those harmful overrides while retaining useful
  corrections in the learnable scenarios;
- the gate's protection is bounded to shifts observable before the freeze, and the
  C2/C3 contrast quantifies that boundary;
- sensitivity of admission and harm to γ;
- orbital regimes and element ranges are taken from real catalogue objects.

**Prohibited:**
- validated on-device deployment;
- real measured Doppler correction of any kind;
- LR-FHSS PER, packet, CRC, gateway-ACK or PHY improvement;
- OTA or SDR validation;
- complete real-TLE causal evaluation;
- operational Space-Track provisioning;
- calling simulator output "measured";
- any quantitative claim carried over from exp14, deployable_v1 or the S2 lines;
- any reuse of the retracted figure values.

## 10. Implementation scope

| component | new lines | reuse | risk |
|---|---|---|---|
| trajectory + degradation simulator | ~350 | — | medium: the OU + secular error process must be physically sane |
| visible-pass scheduler | ~90 | archived `build_visible_registry.py`, **with four repairs** | medium |
| target generation + freeze/hash | ~120 | — | low |
| candidates M0–M3 | ~150 | archived, after re-verification | low |
| gate protocol runner (3 arms) | ~220 | — | low |
| analysis + bootstrap | ~200 | — | low |
| causality/integrity tests | ~220 | ported V1/V3/V4/V8 + new W1/W2 | low |
| three figures | ~320 | — | medium: Fig. 2 operating map needs design iteration |
| **total** | **≈1 600** | | |

Runtime: 324 runs, minutes on one core. Realistic effort: **2–3 focused sessions** —
one for simulator + tests + pre-registration commit, one for the protocol run and
analysis, one for figures and text. The dominant risk is not compute; it is
designing the noise process so the C1 cells are genuinely learnable without being
trivially so.

## 11. Figures

**Fig. 1 — signal flow.** Physics branch, optional learned residual branch,
summing junction, gate with fallback path. A mature communications/control block
diagram: summing junction not an equation box, no satellite clipart, white-knocked
signal labels. Reuses the *style* validated in the frozen manuscript's Fig. 1, none
of its values.

**Fig. 2 — operating map.** Validation evidence (x: validation improvement vs
physics) against held-out consequence (y: deployment ΔMAE), one marker per run,
324 markers. Always-on versus gated overlaid; γ as a vertical line; the harmful
quadrant shaded. This figure *is* the paper: the gate's job is to keep points out
of the lower-right harmful region, and the reader sees whether it does.

**Fig. 3 — three compact panels.** (a) useful admission in a learnable C1 cell;
(b) fallback under C2 versus the unprotected C3, side by side; (c) harmful-override
rate against γ.

## 12. Recommendation: **GO**, with one scope condition

GO. The question is legitimate, small, and answerable with the tooling already
audited. The design removes every defect that ended the real-TLE line by
construction rather than by hope, and the two hardest lessons from that line —
tail-dominated metrics and outcome-dependent gate denominators — are encoded as
pre-run well-posedness checks.

**Scope condition:** the paper must present the gate's **protection boundary**
(C2 versus C3) as a primary result, not a limitation. Without it this is a
mechanism demonstration on a simulator the authors designed, and a workshop
reviewer would be right to discount it. With it, the paper says something falsifiable
and non-obvious: *validation-time admission prevents exactly the class of harm that
is visible at validation time, and no other* — which is a genuine, if modest,
contribution, and it is honest about what an evidence gate is for.

**Honest assessment of ceiling:** this is a workshop paper, not a conference paper.
The contribution is a mechanism and its behavioural characterisation under
synthetic conditions. It does not establish operational value, and the limitations
section must say so plainly.

**What the archived line taught that this design encodes.** Four rounds of
independent review produced four transferable lessons, each now a structural
feature rather than an aspiration: (1) a test that cannot fail is not evidence —
hence W3, the mutation canary; (2) a status or subset boundary must never be
defined by the outcome being measured — hence no σ-versus-|r| classification here,
labels are complete by construction; (3) a metric hostage to a handful of tail
observations cannot resolve a 5 % margin — hence the §7 tail checks run before any
model is fitted; (4) declare the operative criterion, not a flattering
approximation of it — hence the minimum-pass-duration and residual-scale-floor
declarations. The reason to trust this benchmark's negative results, if it produces
any, is that the same discipline produced a negative result on real data and
reported it.

## 13. Physical generative chain (mandated, and the core correctness property)

Full parameters in `physical_config.json`. The residual is **never** prescribed in
the frequency domain. It exists only as a difference between two independently
propagated Doppler predictions:

```
 true element sequence  e_true(t_k),  n(t) = n0 + ndot·t + OU_n(t),  B*(t) = B*0·(1+OU_b(t))
        │
        ├─ truth:     SGP4(e_true(nearest epoch), t)  →  D_reference(t)        (1)(3)
        │
        └─ held:      e_held = e_true(t_refresh − age) + Δ   (injected OD error) (2)
                      SGP4(e_held, t)                  →  D_physics(t)          (4)

                      r(t) = D_reference(t) − D_physics(t)                      (5)
```

`Δ` is an **orbit-determination error vector on the mean elements** — which is
exactly what a real catalogue element set carries. Nothing is ever added to `r(t)`
directly, and no condition modifies `r(t)`: C1/C2/C3 change physical state or its
timing only.

**Why C1 is learnable for a physical reason.** An injected mean-motion error `Δn`
produces an along-track position error growing as `ds ≈ 2πa·Δn·age`. Along-track
error maps into range-rate error through the pass geometry, so the residual is a
smooth function of `(age, phase, elevation, range)`. That is Keplerian phase drift,
not a formula picked to suit a candidate. At `Δn = 5×10⁻⁵` rev/day and
`a = 6878` km this gives ≈ 2 km of drift per day, reproducing the documented
behaviour that TLE-based position degrades a few kilometres per day.

**Why it is not candidate-matched.** The map `Δ → r` passes through SGP4 and the
nonlinear range-rate projection. M1 is affine in age; M2 is linear in nine
standardised features; M3 is a two-state tracker. Each captures *part* of the
structure; none can represent it exactly. Check **WP7** rejects any cell where a
single feature correlates with `r` above 0.999 — the signature a candidate-matched
target would leave.

**Why the OU term is the honest noise floor.** `OU_n` and `OU_b` model drag varying
with solar activity and attitude (15 % 1-σ on B*, 3-day correlation time). They are
zero-mean, they are **not** functions of any deployable feature, and they set the
floor against which the systematic term must be detected. Staleness is the SNR
knob: longer age ⇒ larger systematic term ⇒ higher SNR.

## 14. C2 versus C3 — identical perturbation, timing alone differs

Enforced by construction, not by convention: **one** shift specification, **one**
magnitude (4× the injected error), **one** code path, with onset time as the only
differing argument.

| condition | onset |
|---|---|
| **C2** | uniform within the middle 60 % of the **validation** window |
| **C3** | uniform within the first 40 % of the **deployment** window (strictly post-freeze) |

There is no hidden difficulty parameter distinguishing them, and **C3 is not tuned
to fail**. If C3 happens not to produce harm, that is reported as-is. The point is
that the same configuration produces protection or exposure *depending only on
when the evidence arrives relative to the freeze* — which is why this is one
experiment with a timing variable, not two unrelated scenario generators.

## 15. N0 — negative control

Δ = 0 **exactly**, OU processes retained at their pre-registered amplitudes as the
explicitly unpredictable zero-mean disturbance. Reference and held dynamics are
otherwise identical.

Expected: no stable held-out gain, gate normally closed, no false claim of
learnability. N0 is a **benchmark integrity test** — it does not expand the 27-cell
grid. If N0 shows a stable learned gain or frequent gate openings, the benchmark is
broken and no headline result may be reported from it.

N0 is the check that would have caught a simulator quietly leaking truth into a
feature, and it is the one result I would look at first.

## 16. Seed hygiene

| set | seeds | rule |
|---|---|---|
| **DEBUG_SEEDS** | 90001, 90002, 90003 | implementation and smoke testing only. **Never reported as experimental evidence.** |
| **EVALUATION_SEEDS** | 1001–1012 | committed before formal evaluation; 12 locked seeds |

A seed drives the OU realisations and the sign draws of `Δ`. **Magnitudes are
fixed; only signs are drawn**, so a magnitude sweep cannot be smuggled in as seed
variation. The transmission schedule is seed-independent by construction.

Persisted per run: seed list, configuration hash, simulator source hash, model
manifest hash, gate configuration hash. **After the first formal evaluation run
begins, no parameter changes without invalidating the run and issuing a new
pre-registration version.**

## 17. Well-posedness checks (all cells, before any model evaluation)

| id | check |
|---|---|
| WP1 | visible transmission geometry — every row above the declared mask |
| WP2 | fixed row membership — schedule hashed before targets are generated |
| WP3 | causal features — none reads truth, the reference, or any future quantity |
| WP4 | label completeness exactly 1.000 |
| WP5 | residual magnitude and units recorded; scale floor evaluated and labelled |
| WP6 | no target formula matched to a candidate model |
| WP7 | no single feature with \|corr(feature, r)\| > 0.999; no perfect affine identity |
| WP8 | no single sample dominating residual energy — top-1 % share of Σ\|r\| < 0.10 |
| WP9 | no symmetric duplicated geometry — max \|corr\| between offset pairs reported |

Failures are **reported, not tuned away**.

## 18. Aggregation

`seed → scenario cell → orbital regime`. Within a run: samples → passes →
deployment window. **Individual time samples are never independent experimental
units** — measured within-pass ICC on real data was 0.586–0.792, which is why this
is fixed in advance. Uncertainty by bootstrap over seeds within cell and over
cells.

## 19. Success requirements

| requirement | criterion |
|---|---|
| **C1** | useful admission across ≥ 2 orbital regimes, ≥ 2 staleness levels, multiple seeds |
| **C2** | gated policy avoids or reduces harm versus always-on across multiple cells and seeds |
| **C3** | protection boundary reported: the gate cannot react to a post-freeze shift. **Not required to fail by construction.** |
| **N0** | no stable learned gain, no frequent false gate openings |
| **all** | no result depending on one seed or one hand-picked cell |

## 20. Implementation checkpoints

| # | scope | independent verification |
|---|---|---|
| 1 | simulator mechanics and scheduler tests | reviewer or mutation test |
| 2 | physical residual-generation audit | reviewer |
| 3 | N0 and smoke-seed behaviour | reviewer or mutation test |
| 4 | formal configuration freeze | reviewer |
| 5 | 324-run evaluation | reviewer |

**The implementing agent does not self-certify at any checkpoint.** This is the
rule that produced every real finding in the archived line — four rounds of review
found four defects I had missed, two of them in my own tests.

## 21. Pre-registration plan

Before any model is fitted, commit on `workshop-controlled-evidence-gate`:
`BENCHMARK_DESIGN.md` (this file), `scenario_config.json` with all exact numeric
settings, `model_manifest.json`, `gate_protocol.json`, `analysis_plan.json`, and
the test file. Tag `exp16-controlled-gate-preregistered-v1`. No manuscript files,
no results. Same discipline that makes the archived negative result credible.
