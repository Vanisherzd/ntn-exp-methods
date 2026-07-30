# S2-FIRST DOSSIER — CAUSAL RESIDUAL-CORRECTION RECOVERY

Lifecycle: EXPERIMENT_RECOVERY. Manuscript FROZEN and untouched. Nothing committed.
Authorized scope executed: E0.5, E1, E2, E3, E4, S2. E5 and E6 not run.

**S2 VERDICT: UNRESOLVED.**
**RECOMMENDATION: HOLD — rebuild E1 before any stop/continue decision.**

The walk-forward ran clean and every pre-registered candidate lost to SGP4
(0 / 279 gates open). I drafted that as S2 FAIL. Independent causality review
then found, and I verified, that **96.58 % of the transmissions in my dataset put
the satellite below the endpoint's horizon** — no visibility gate exists anywhere
in the builder. On the 1.45 % of rows that are actually visible the residual is
**5.6x larger**, and a perfect-foresight bound on feature-based correction rises
from 0.10 % to 9.8 %, i.e. from far below the 5 % gate to above it. A FAIL
computed on that dataset would be a false negative caused by my own defect, so I
am not reporting one. See section 15.

---

## 1. Endpoint provisioning policy (E0.5)

`experiments/exp15_causal_recovery/provisioning_policy.json`

Three notions are separated and never conflated:

| notion | definition |
|---|---|
| globally published | `CREATION_DATE` has passed. A fact about the catalogue, not the device. |
| available to endpoint | provisioned to the device at a refresh event; requires `CREATION_DATE <= t_refresh`. |
| currently held | the single frozen element/model/scaler/gate used until the next refresh. |

**PRIMARY MODEL: PERIODIC PROVISIONING WITH FROZEN OPEN-LOOP OPERATION.** At each
refresh the endpoint receives the latest element with `CREATION_DATE <= t_refresh`
plus a frozen model, scaler and gate, and operates with no downlink beacon, no
newly published element and no label feedback until the next refresh. It never
polls Space-Track.

The E0 statement *"a fresher element was already published, therefore the stale
element could not be used"* is **retracted** as stated: it holds only under
continuous/immediate provisioning, which is not the primary model.

Initial cadence **24 h**, fixed before any model result was inspected.

## 2. Dataset-only cohort counts under three provisioning policies

In-band transmissions (age assigned from **actual** `age_tx = t_tx − EPOCH(stale)`;
refresh interval and TLE age are *not* interchangeable). No model was trained on
the sensitivity variants.

| policy | 8 h | 24 h | 48 h | 72 h | 96 h | 168 h |
|---|---|---|---|---|---|---|
| immediate (WITHDRAWN, see 15/F4) | 271,832 | 337,171 | 4,812 | 562 | 289 | 27 |
| **periodic 24 h** | **47,899** | **115,439** | **19,687** | **1,221** | **391** | **71** |
| periodic 72 h | 5,815 | 17,670 | 22,397 | 17,204 | 2,283 | 57 |

**The `immediate` row is withdrawn.** I hard-coded 24 transmissions at 1 h
spacing for it, so its episodes span 23 h and overlap their own successor refresh
(ISS median inter-publication gap 4.33 h). Under true immediate provisioning ISS
carries an element >= 16 h old only 7.2 % of the time. The row overstates
long-band coverage by roughly 5x and must be rebuilt from the realised gap to the
next refresh. The 24 h and 72 h rows are unaffected: their episodes are bounded by
their own interval.

**FINDING S2-1.** The reachable staleness is set by the provisioning interval plus
the publication lag, not by choice. Under 24 h provisioning the cohort is
concentrated in 8/24/48 h; 72 h is thin (1,221 rows) and 96/168 h are
effectively absent (391 and 71 rows, 4 and 1 satellites). Under 72 h provisioning
the mass moves to 48/72 h. **No realistic provisioning policy naturally produces
a 168 h cohort.** The previous 168 h band existed only because the old pairing
rule matched two elements 168 h apart while ignoring every element published in
between — i.e. it modelled a terminal that receives nothing for a week while the
catalogue publishes daily.

## 3. Selected primary policy and why

`periodic_24h`, availability-enforced, epoch year ≥ 2014. It matches the intended
system (a scheduled provisioning payload, open-loop between refreshes), it is the
only regime where `CREATION_DATE` is a trustworthy availability proxy (E0: 0 %
negative lag from 2014, p50 0.96–5.76 h), and it was fixed before results.
Long-age bands were **not** manufactured by ignoring scheduled refreshes.

## 4. Modern-data qualification

Re-run from scratch, not assumed. 11 objects discovered; both STARLINK objects
fail on record count (11 and 9 availability-clean elements) and are dropped.
**9 satellites qualify**, spanning 7 orbital regimes: ISS, IRIDIUM 181, IRIDIUM
177, ONEWEB-0015, SENTINEL-6B, FLOCK 4H 1, FLOCK 4H 2, BLACK KITE-1,
BLACK KITE-2. The ≥ 2014 restriction costs ISS 55 % of its elements (20,933 of
46,859 retained) and costs the other eight nothing.

## 5. Causal pair / episode manifest (E1)

`experiments/exp15_causal_recovery/build_causal_dataset.py` → 184,708
transmissions. Per observation the builder persists stale EPOCH, stale
CREATION_DATE, `t_refresh`, `t_tx`, actual `age_tx`, reference EPOCH, reference
CREATION_DATE, `t_close`, band and screen flag.

Reference rule, pre-registered: the first same-object element ordered by
CREATION_DATE that becomes available **strictly after** `t_tx`, with
`|EPOCH(ref) − t_tx| <= 48 h`, SGP4 convergent, and a physically distinct
solution from the stale element. Its EPOCH may precede `t_tx`; it is used only
retrospectively and propagated to `t_tx`. It is called a **later-solution,
model-derived reference**, never ground truth.

## 6. Label-closure audit

`experiments/exp15_causal_recovery/E1_verification.json` — **E1 VERDICT: PASS.**

| assertion | violations |
|---|---|
| A1 `CREATION_DATE(stale) <= t_refresh` | 0 / 184,708 |
| A2 `t_refresh <= t_tx` | 0 / 184,708 |
| A3 `CREATION_DATE(ref) > t_tx` | 0 / 184,708 |
| A4 `t_close == CREATION_DATE(ref)` | 0 / 184,708 |
| A5 feature row invariant to the reference | 0 features moved / 40 probes |

A5 is the same perturbation that exposed the old `t_gap_s` leak: stale element,
transmission UTC, ground station and carrier held fixed, only the reference
swapped. All 9 features stayed bit-identical; the label moved in 40/40 probes.

Closure lead `t_close − t_tx`: n = 184,708, min +0.0003 h, p50 3.94 h, p90 13.53 h,
p99 32.28 h, max 437.44 h, **0 non-positive**.

## 7. Causal historical-feature manifest (E2)

17 historical-state features, pre-registered in `preregistration.json` before any
fit: last-closed residual mean and median, EWMA bias at α ∈ {0.05, 0.2}, EWMA
absolute error at both α, EWMA variance, residual trend over N ∈ {5, 20} closed
episodes, closed-episode count, time since last closed label, TLE inter-arrival
median and last, Δ mean motion, Δ B*, Δ eccentricity, and a `history_valid` flag.
Plus the 9 deployable static features (actual `age_tx`, stale Doppler, sin/cos
phase, elevation, range, mean motion, B*, eccentricity). There is no
stale-to-reference epoch gap.

**Temporal-join test: 0 failures.** No episode's admitted history contains a
label with `t_close > t_refresh(episode)`. History accumulates per satellite,
never crosses satellites, and resets after 30 days without a closed label.

## 8. Pre-registered model and configuration hashes

`preregistration.json` sha256 `5ab2d396d6ef970f…` (recorded in `E4_walk_forward*.json`).
Candidates frozen before E4: M0 SGP4 zero; M1 age-only linear; M2 causal static
ridge; M3 last-closed-residual bias; M4 EWMA bias; M5 RLS bias/drift; M6 two-state
Kalman bias/drift; M7 ridge on static + historical state. No neural network, no
GRU/LSTM/Transformer, no per-satellite hand tuning, no post-result feature.

## 9. Walk-forward results (E4)

One model per satellite, all causally populated bands pooled with `age_tx` as a
feature — matching deployment, where an endpoint is provisioned with one
corrector rather than six. Decision stride 30 episodes, deployment horizon 30
episodes, validation = last 25 % of closed history, γ = 0.95.

**279 decision segments across 9 satellites. Gates open: 0 / 279.**

Validation ratio `MAE_{m*}(V) / MAE_SGP4(V)` — the gate needs < 0.95:

| satellite | min | median |
|---|---|---|
| ISS | 0.9862 | 1.0001 |
| IRIDIUM 181 | 0.9897 | 1.0002 |
| IRIDIUM 177 | 0.9595 | 0.9997 |
| ONEWEB-0015 | 0.9638 | 0.9998 |
| SENTINEL-6B | 1.0004 | 1.0084 |
| FLOCK 4H 1 | 0.9688 | 1.0028 |
| FLOCK 4H 2 | 0.9726 | 1.0010 |
| BLACK KITE-1 | 0.9952 | 1.0024 |
| BLACK KITE-2 | 0.9885 | 1.0002 |

The median is **1.000 to four decimals on every satellite**: the best available
causal corrector is exactly as good as doing nothing. The single best of 279
decisions reached 0.9595, still short of the pre-registered threshold.

`m*` selection: M6 Kalman 265, M4 EWMA 6, M5 RLS 6, M1 1, M3 1, M2 0, M7 0. The
validation argmin overwhelmingly selects the candidate that perturbs the physics
least.

## 10. Satellite-balanced aggregate analysis (S2 primary)

Statistical unit: the refresh **episode** (the 24 transmissions inside one episode
share one frozen stale element and usually one reference, so they are not
independent). Equal weight per satellite. Hierarchical block bootstrap, 10,000
resamples: satellites, then whole deployment episodes within satellite.

Held-out Δ MAE = MAE_candidate − MAE_SGP4, **negative would mean improvement**:

| candidate | Δ MAE (Hz) | bootstrap 95 % CI | improvement | satellites improved |
|---|---|---|---|---|
| M1 age-only linear | **+2.978** | [+1.075, +5.177] | −67.9 % | 0 / 9 |
| M2 causal static ridge | **+10.089** | [+3.265, +18.672] | −230.0 % | 0 / 9 |
| M3 last-closed bias | **+0.995** | [+0.267, +1.956] | −22.7 % | 0 / 9 |
| M4 EWMA bias | **+0.450** | [+0.106, +0.911] | −10.3 % | 0 / 9 |
| M5 RLS bias/drift | **+0.581** | [+0.104, +1.234] | −13.3 % | 0 / 9 |
| **M6 Kalman (best)** | **+0.0025** | **[+0.0001, +0.0055]** | **−0.06 %** | **1 / 9** |
| M7 static + historical ridge | **+9.446** | [+3.294, +16.929] | −215.4 % | 0 / 9 |

Every candidate is worse than plain SGP4, and every bootstrap interval lies
entirely on the wrong side of zero. Sign stability: the fraction of deployment
episodes in which `m*` beat SGP4 is 0.241–0.545 — a coin flip at best. The gated
system's held-out improvement is **identically zero**, because it never admits.

Screen sensitivity (S2 criterion 6), best-candidate Δ MAE:

| reject_hz | 750 | 1000 | 1500 | 2500 | none |
|---|---|---|---|---|---|
| Δ MAE (Hz) | +0.0025 | +0.0025 | +0.0025 | +0.0025 | +0.0025 |
| gates open / 279 | 1 | 1 | 0 | 0 | 0 |
| verdict | FAIL | FAIL | FAIL | FAIL | FAIL |

The failure is **not** an artifact of one screening threshold.

## 11. Gate admissions and harmful-admission rate

Admitted deployment segments: **0 of 279** at the pre-registered configuration
(1 of 279 at reject_hz 750 and 1000). The pre-registered rule applies: with fewer
than 10 admitted segments, **admission value is UNRESOLVED, not successful**. The
harmful-admission rate is not estimable, and the 20 % limit is untested.

This is the gate behaving exactly as designed: it refuses to deploy a corrector
that cannot demonstrate a 5 % validation margin, and no causal corrector could.

## 12. S2 VERDICT: **UNRESOLVED**

What was measured, on the dataset as built:

| criterion | result on the as-built dataset |
|---|---|
| 1 positive satellite-balanced aggregate | not met — best is +0.0025 Hz (worse) |
| 2 bootstrap interval supports improvement | not met — [+0.0001, +0.0055], wrong side |
| 3 breadth (>1 satellite, >1 regime) | not met — 1 satellite, 1 regime |
| 4 no satellite >50 % of gain | not met |
| 5 sign stable across adjacent segments | not met — episode win rate 0.24–0.55 |
| 6 not dependent on one screening threshold | robustly negative at all five thresholds |
| 7 harmful-admission rate <= 0.20 | UNRESOLVED — 0 admitted segments |

**These results are not certifiable**, because the dataset they were computed on
failed independent causality review on a defect that plausibly suppresses the
signal under test (section 15, F1). The pre-registered verdict is therefore
UNRESOLVED, not FAIL.

## 13. What the data does establish, and what it does not

**Established, and robust to the visibility defect.** No constant offset and no
function of TLE age alone can help. Perfect-foresight bounds, equal weight per
satellite:

| oracle (non-causal, perfect foresight) | all rows | visible rows only |
|---|---|---|
| single global median offset | 0.04 % | 0.22 % |
| optimal median offset per age bin | 0.10 % | 1.14 % |
| in-sample L1 fit on the 9 static features | 0.57 % | **3.96 %** |
| in-sample L1 fit, static + quadratic | 2.31 % | **9.82 %** |
| per-episode median offset (unattainable) | 10.00 % | 83.14 % |

The gate needs 5 %. On all rows the whole family is bounded far below it, which is
why every candidate failed. **On visible rows the feature-based family is no
longer bounded below the gate**, so the negative result does not transfer.

Also established: M0-M7 as fitted are genuinely beaten by doing nothing, and not
because of a coding error. Verified at one decision point on IRIDIUM 181: the
static ridge is worse than SGP4 **on its own training set** (7.86 vs 4.81 Hz MAE)
and selects the largest available regularisation (alpha = 1000). That is the
correct behaviour of a squared-loss fit against a target with median \|r\| 0.25 Hz
and maximum 1403 Hz — it optimises the tail and destroys the median.

**Not established.** Whether a causal corrector helps on visible geometry. That
is the actual research question and it remains open.

**Superseded.** My earlier draft findings S2-2 and S2-4 — "the reachable bands
carry a 0.2-1.0 Hz median residual, so there is nothing worth correcting", and
"the old IRIDIUM 181 headline sat on a 0.093 Hz residual" — were computed over a
population that is 96.6 % below the horizon. The visible-only medians are 5.6x
larger. Both claims are withdrawn as stated.

**Still standing.** Finding S2-1 (reachable staleness is set by the provisioning
interval plus publication lag, and no realistic policy naturally produces a 168 h
cohort) does not depend on visibility. Finding S2-3 (MAE is tail-driven; the
tails are manoeuvre and bad-element events that no pre-transmission corrector can
anticipate) also survives, and is reinforced by F9: nothing in the pipeline
detects manoeuvres, and ISS reboosts throughout the record.

**Corrected.** The deep-age bands are not 1,221 / 391 / 71 independent
observations. They are a handful of catalogue-outage incidents: ISS band 168 is
41 rows from 3 refresh events on 2 calendar dates; BLACK KITE-1 band 168 is 30
rows from 1 incident. Effective n there is O(1-10), and outages are exactly when
orbit determination is being re-established. Combined with F1, band 168 contains
**3 visible rows in the entire dataset**.

## 14. RECOMMENDATION: **HOLD**

Not STOP, and not CONTINUE. The stop rule was conditioned on S2 failing; S2 did
not fail, it was invalidated by a defect I introduced. Stopping on a false
negative would discard the programme for the wrong reason, and continuing would
build on a dataset that failed review.

Required before S2 can be re-decided — a bounded rebuild, not a new programme:

1. **Pre-register a visibility-gated transmission schedule.** Transmissions must
   occur during passes above a stated mask (10 deg is the conventional choice).
   The current fixed 1 h grid across the refresh interval yields 1.45 % visible
   rows and cannot be rescued by filtering: only 2,682 rows survive, 34-1,004 per
   satellite, against a walk-forward requirement of 150 train + 50 validation per
   decision point. Sampling must be dense inside passes instead, which is roughly
   a 100x compute increase on a job that currently runs in minutes.
2. **Make row membership independent of the future catalogue.** A row currently
   exists only if a qualifying reference is later published; the drop rate rises
   with age to 100 % for SENTINEL-6B at 96 h. Either report the censoring rate per
   band and treat it as missing-not-at-random, or restrict to intervals where a
   qualifying reference is guaranteed.
3. **Redefine the label as a reference ensemble.** This is the finding I would
   least want to skip. See section 15, F3.
4. Fix the `immediate` provisioning variant (F4); tighten the reference rule to
   closest-epoch with `EPOCH(ref) > EPOCH(stale)` (F7); replace the vacuous
   A1/A2/A4 assertions with one that discriminates (F13); add manoeuvre detection
   or exclusion (F9).

**My honest assessment of the odds, stated before doing the work.** The visible-only
in-sample bound of 9.8 % comes from a quadratic L1 fit scored on the same 59-988
rows it was fitted on, so most of it is overfitting; the linear bound is 3.96 %,
still under the gate. Against that, the residual is genuinely 5.6x larger on
visible geometry, and the per-episode oracle jumps to 83 %, so there is real
structure — it is just per-episode structure, which the walk-forward already
showed is not persistent across episodes. I would put a causal PASS at well under
even odds. But "under even odds" is not "already answered", and the cost of
answering it is one dataset rebuild against work already written.

## 15. Independent review

Two reviewers were dispatched after E1 per the parallel-review requirement. No
implementing agent approved its own output. I verified every finding I report
below rather than relaying it.

### Reviewer A — satellite / NTN causality: **FAIL**

**F1 BLOCKER — no visibility gate. VERIFIED, and it changes the verdict.**
Elevation is computed at `build_causal_dataset.py:189` and stored as feature 4,
and nothing ever gates on it. Over all 184,708 rows: elevation p1 -83.4 deg,
p50 **-42.5 deg**, p90 -11.8 deg, max +86.6 deg; **96.58 % below the horizon**;
6,325 rows (3.42 %) above 0 deg; **2,682 rows (1.45 %) above 10 deg**. Median
\|residual\| is 0.565 Hz below the horizon and **3.178 Hz above 10 deg — 5.63x**.
Above 10 deg per band: 700 / 1,719 / 235 / 20 / 5 / **3**. Per satellite:
0.92 %-3.84 %. The 1500 Hz screen does not help; it is a residual threshold, not
a geometry gate. **The same defect is present in the original pipeline** —
`grep` for elevation gating in `run_multisat_generalization_matrix.py` returns 0
matches — so the frozen manuscript's residual statistics share it.

**F2 BLOCKER — row membership depends on the future catalogue. VERIFIED as a
mechanism.** `reference_for` requires a publication after `t_tx` whose epoch is
within 48 h; when none exists the transmission is silently dropped
(`build_causal_dataset.py:241-244`). Reviewer-measured drop rate by band:
ISS 0.002 / 0.002 / 0.012 / 0.103 / 0.172; SENTINEL-6B 0.002 / 0.003 / 0.021 /
0.245 / **1.000**; BLACK KITE-1 0.000 / 0.019 / 0.127 / 0.435 / 0.447 / 0.762.
The reviewer attempted to measure the direction of the resulting bias and
reported it inconclusive — two satellites disagreed in sign — and flagged it as
SUSPECTED rather than asserting it. I am carrying that forward with the same
caveat. The selection is real; its effect on the measured residual is not
established. Bands 8/24/48 have drop rates of 0.000-0.127, so the bulk of the
data is only lightly affected; the deep bands are not usable.

Note this is the sharp limit of A5. A5 swaps the reference on rows that already
exist and confirms the feature values do not move. It cannot test **which rows
exist**. The claim "leakage is now structurally impossible" rested on A5 and was
too strong: the feature vector is clean (independently confirmed, F12 below), but
the reference still reaches the result through row membership.

**F3 BLOCKER — the label's definitional noise rivals the label. VERIFIED, and
worse on visible rows.** The residual depends on which future element is chosen
as reference, and the pre-registered rule picks the *first* qualifying
publication, which is arbitrary among several valid ones. Recomputing on
**visible rows only** (elev > 10 deg, 514 probes, mean 6.1 valid references per
probe):

| band | n | median \|label\| | median spread across references | ratio |
|---|---|---|---|---|
| 8 h | 152 | 4.961 Hz | **8.987 Hz** | **1.812** |
| 24 h | 269 | 6.438 Hz | 4.571 Hz | 0.710 |
| 48 h | 37 | 5.397 Hz | 2.253 Hz | 0.418 |

**51.8 % of visible probes have a reference-choice spread larger than the label
itself** (the reviewer measured 40.5 % over all rows; restricting to visible
geometry makes it worse, not better). At 8 h the arbitrariness of the reference
moves the target nearly twice as far as the target's own magnitude.

This is the deepest finding in the programme and it is not fixed by a visibility
gate. "The SGP4 residual" is not a well-defined quantity under this construction:
a large fraction of what any model is asked to predict is the label-construction
choice, not orbital physics. The fix is to define the label as a **reference
ensemble** — the median over all qualifying references, with the inter-reference
spread published as label uncertainty and any band rejected where the spread
exceeds the label median. On current numbers the 8 h band would be rejected. The
alternative, a real measured Doppler reference, is the hardware path and is out
of scope.

**F4 MAJOR — the `immediate` sensitivity row is mis-implemented. ACCEPTED.**
My defect: `n_tx` and `step` are hard-coded to 24 x 1 h regardless of policy, so
immediate-provisioning episodes span 23 h and overrun their own successor
refresh. Row withdrawn in section 2.

**F5 MAJOR — deep bands are a few catalogue-outage incidents. ACCEPTED**, folded
into section 13.

**F6 MAJOR — no independence accounting in the builder. PARTLY PRE-EMPTED.**
Correct that the builder and verifier record no clustering. The S2 analysis the
reviewer had not been given does use the refresh episode as the statistical unit
with a hierarchical block bootstrap over satellites then episodes, which is the
remedy they recommend. Their per-row figure of ~21 rows per held element and
8,497 episodes for 184,708 rows is consistent with my own accounting.

**F7 MAJOR — tighten the reference rule. ACCEPTED for the rebuild.** Reference
propagation distance grows with band (median \|EPOCH(ref) - t_tx\| 2.13 h at 8 h
rising to 10.23 h at 96 h), so the reference's own SGP4 error is correlated with
the covariate under study; within-band Spearman is only -0.09, so it is not
currently driving anything, but it is untested where n is smallest. Also 0.25 %
of rows (462) use a reference whose epoch precedes the stale element's — not a
"later solution" at all. Adopt closest-epoch selection with
`|EPOCH(ref) - t_tx| <= 6 h` and `EPOCH(ref) > EPOCH(stale)`, with pre-registered
sensitivity at 12/24/48 h.

**F8 MAJOR — the label cannot reach the best solution for its epoch. ACCEPTED.**
Same-epoch revision groups are collapsed to the earliest-published member before
`availability_index` ever sees them. That is right for the *held* element (an
availability argument) and backwards for a *retrospective* label, which should
use the most refined solution. Separately, `physical_key` collides across
distinct epochs (ISS 20,933 records to 20,814 keys; BLACK KITE-1 446 to 397), so
the distinct-solution guard both over-rejects and under-protects.

**F9 MAJOR — no manoeuvre handling anywhere. ACCEPTED.** Zero matches for
manoeuvre/reboost/thrust across both experiment directories. ISS reboosts
throughout; the two alpha-5 STARLINK entries are in active orbit-raising. Under
frozen open-loop operation a manoeuvre inside an episode invalidates the held
element outright, and the residual then measures the manoeuvre while being filed
into a staleness band. This is the mechanism behind finding S2-3.

**F10 MAJOR — four real-system details assumed away. ACCEPTED as limitations.**
The provisioning model itself was judged coherent and the E0 retraction correct.
Assumed away: (i) visibility, which is F1; (ii) zero provisioning latency — an
element published one second before `t_refresh` is treated as held, whereas real
payload delivery takes hours, so every `age_tx` is biased low; (iii) a perfect
endpoint clock — at ISS altitude 1 s of along-track timing error is about 7.7 km
of position, which perturbs range rate by more than the sub-Hz residuals being
modelled at short staleness; (iv) perfect endpoint position. Point (iii) is a
serious independent objection to modelling short-staleness residuals at all.

**F12 MINOR — the feature vector is clean. INDEPENDENTLY CONFIRMED.** Reviewed
line by line: `age_tx_s`, `stale_doppler_hz`, `elevation_deg`, `range_km`,
`sin_phase`/`cos_phase` (mean-motion extrapolation from the stale element's own
mean anomaly), `stale_mean_motion_rad_min`, `stale_bstar`, `stale_ecc` are all
endpoint-computable; `d_ref` is computed into a separate variable used only for
the label. This is the one thing the rebuild got right. Noted nit: `phase` uses
`no_kozai` while `stale_doppler_hz` uses full SGP4 with `no_unkozai`, so the two
are mutually inconsistent — not a causality defect, worth aligning.

**F13 MINOR — three of the five assertions are vacuous. ACCEPTED, my error.**
A4 in the builder reads `t_close = ref["creation_dt"]` then
`assert t_close == ref["creation_dt"]` — a tautology; in the verifier it only
checks finiteness. A1 and A2 are true by construction of `held_element` and
`t_tx = t_refresh + m*step`. Only **A3 and A5 discriminate**, and A5 tests row
content rather than row membership (F2). Calling this "five mechanical
assertions" overstated the guarantee; section 6 should be read as two real checks
plus three restatements of construction.

**F11/F14/F15/F16 MINOR — accepted.** The refresh grid is anchored on the first
CREATION_DATE present in the local archive, so it is a property of the download
rather than the device and differs per satellite. The >= 2014 filter is applied
to EPOCH but used to certify the AVAILABILITY clock, and no row is ever asserted
to satisfy `CREATION_DATE >= EPOCH`. `held_element` returns the last-published
element, which in 13 of 8,497 refresh transitions has an *earlier* epoch than the
one already held. Both alpha-5 STARLINK entries are genuine catalogue objects,
not fabrications, but contribute 5 episodes each and were correctly dropped by
the record-count gate.

### Reviewer B — dataset / statistics: **FAIL**

Reviewer B independently found the visibility blocker with no knowledge of
Reviewer A's report: 96.58 % below horizon, 2,682 rows above 10 deg, and
**84.52 % of the total MAE mass sitting in below-horizon rows**. Two independent
FAILs on the same defect is why I am not certifying the S2 result. Their
per-satellite visible/all MAE ratio runs from **0.2 (SENTINEL-6B) to 19.2
(FLOCK 4H 2)** — the gate is not a monotone shrink, so adding it can flip
individual satellite signs. STARLINK-37711 has **zero** rows above 10 deg. The
usable design is **2,682 rows in 2,259 episodes**, not 184,708 in 8,508.

**B2 BLOCKER — element chaining. VERIFIED, and new.** The label element of episode
k becomes the held element of episode k+1, so
`residual_{k+1} = D(ref_{k+1}) - D(ref_k)` — the residual series is a first
difference over a shared element sequence, which manufactures negative lag-1
dependence. Fraction of distinct stale elements that also serve as a reference:

| satellite | stale elements | also used as reference | episode-mean signed ACF lag 1 |
|---|---|---|---|
| ISS | 4,532 | 4,403 (**97.2 %**) | +0.007 |
| IRIDIUM 181 | 1,116 | 1,108 (**99.3 %**) | +0.130 |
| FLOCK 4H 1 | 212 | 211 (**99.5 %**) | **-0.250** |
| BLACK KITE-1 | 155 | 148 (**95.5 %**) | **-0.543** |

-0.543 is close to the -0.5 expected from a pure random-walk difference. M3-M6 are
exactly the family that exploits lag-1 structure, so **a win by any bias tracker
would have been indistinguishable from this artifact.** In this run they all lost,
so no false positive was produced — but the pre-registration's stated plan to
report a constant winner as "the learnable structure is an offset" would have been
wrong. Any rebuild must either enforce `stale_{k+1} != ref_k` (reporting the
retention cost) or include a control that denies lag-1 access.

**B3 MAJOR — MAE is single-row-fragile at segment level. ACCEPTED.** IRIDIUM 181:
**62 rows of 26,529 (0.23 %) hold 99.33 % of the sum of squares.** In one segment,
removing a single row (n 24 to 23) moved `dep_mae_sgp4` from 13.7156 to 10.3091 Hz
— **-24.8 %**. A metric that fragile cannot satisfy criterion 6 for any model.
This sharpens finding S2-3 from "tail-driven" to "individual-row-driven".

**B4 MAJOR — effective independent satellites is about 6, not 11. ACCEPTED.**
FLOCK 4H 1, FLOCK 4H 2 and BLACK KITE-1 share a December-2025 rideshare with
orbital periods agreeing to **0.4 s** (1.5792 / 1.5789 / 1.5790 h) and
daily-median-residual Spearman 0.45-0.54. Clusters: {ISS}, {IRIDIUM 177, 181},
{ONEWEB-0015}, {SENTINEL-6B}, {FLOCK 4H 1, FLOCK 4H 2, BLACK KITE-1},
{BLACK KITE-2}. Kish effective n_satellites is 3.14 row-weighted / 2.31
pair-weighted. Equal weighting hands 27 % of the aggregate to one rideshare.
Adopt leave-one-cluster-out in the rebuild.

**B5 MAJOR — episodes are serially correlated, so my bootstrap is too tight.
ACCEPTED.** Episode-RMS lag-1 ACF: ONEWEB-0015 **0.82** (still 0.51 at lag 20),
BLACK KITE-1 **0.75**, SENTINEL-6B 0.55, IRIDIUM 181 0.46, ISS 0.41.
Integrated-ACF effective episode counts: ONEWEB-0015 640 to **46**, BLACK KITE-1
168 to **16**, ISS 4,582 to 1,393; total about **2,384 episode-equivalents**. My
i.i.d.-episode resampling understates the interval by roughly 3.7x for ONEWEB-0015
and 3.3x for BLACK KITE-1 — the two satellites a breadth claim would lean on.
Replace with a moving-block bootstrap, block length at or above the integrated-ACF
scale (>= 14 episodes for ONEWEB-0015).

**B6 MAJOR — calendar trend aligned with the walk-forward direction. ACCEPTED.**
Spearman(t_tx, residual magnitude) and median residual first-to-last quarter:
ONEWEB-0015 **-0.386**, 3.79 to 0.42 Hz (**0.11x**); BLACK KITE-1 **-0.309**,
3.98 to 0.40 Hz (**0.10x**); FLOCK pair about -0.17, 0.45x. Walk-forward trains
early and deploys late, so for those two the deployment window is 9-10x *easier*
than training. Note the direction: this biases the comparison **in favour** of the
learned candidates, and they still lost. It does not explain the negative result,
but it does invalidate criterion 5 as a measure of model quality — it is partly
measuring commissioning ramp-down.

**B7 MAJOR — provenance. VERIFIED and PARTLY CORRECTED.** Nothing in
`experiments/exp15_causal_recovery/` is committed, so
`"written_before_any_model_fit": true` is an unverifiable self-declaration. On
mtimes the ordering does hold — `preregistration.json` 16:01:09 precedes the first
fit at 16:03:39 — but a third party cannot confirm that without a commit predating
the results. **Recommend committing this directory at the human gate** (no commit
made here, per instruction).

Reviewer B is right that `run_walk_forward.py` (16:06:24) postdates the original
`E4_walk_forward.json` (16:03:39) and `S2_analysis.json` (16:04:46), so those two
are not reproducible from the current code. I have renamed both to `.SUPERSEDED`
rather than delete them. Their further claim that **criterion 6 mixes two code
versions is incorrect**: the whole threshold family (r750 16:06:48, r1000 16:07:01,
r1500 16:07:13, r2500, noscreen) postdates the patch and carries the
`screen_reject_hz` key, and every headline number in this dossier comes from
`E4_walk_forward_r1500.json` plus `S2_analysis_r1500.json` (16:08:05) — one
consistent version. Only the two superseded files were stale.

**B8 MINOR — band 24 h is age-confounded across satellites. ACCEPTED.** Median
`age_tx` inside band 24 h spans 22.40 h (ISS) to 26.64 h, because ISS publishes
about 4.5 elements/day against about 2/day for the others. Given
`dlog10(residual)/d(age h)` of 0.005-0.030, the 3.7 h offset implies a 4-29 %
difference in residual magnitude — acceptable for a relative per-band comparison,
not for absolute per-band MAE. Bands are also entangled with the within-episode
offset index.

**B9 MINOR — degeneracy confirmed clean.** 0 exact duplicate feature rows; full
rank 9 for all satellites; condition number 12.7-20.4 after z-scoring; the old
age-versus-gap affine dependence **confirmed gone**. Largest pairwise correlation is
elevation versus range at 0.982-0.989 (VIF 30-45), absorbed by ridge but making
those two coefficients uninterpretable. Within a single episode the design matrix
has **rank 7** in 100 % of episodes, because mean motion, B* and eccentricity are
frozen-element constants — harmless for the pooled per-satellite fit used here,
fatal for any per-episode fit.

**B10 MINOR — walk-forward feasibility. CONFIRMED adequate.** 200 closed rows are
available by episode 10-11 and 20 closed episodes by episode 21-22 for all 9 real
satellites, so the minimum-history rule is sound. Both STARLINK objects can never
satisfy it (5 episodes, max 90 closed rows) and contributed nothing — they should
be excluded explicitly rather than vanishing silently. Only ISS, IRIDIUM 177,
IRIDIUM 181 and ONEWEB-0015 have 10 or more decision points, so criterion 7 would
have been decided by 4 objects even had the gate opened.

**B11 MINOR — no measurable bias exists to learn. INDEPENDENT CONFIRMATION.**
One-sample t-test on episode-mean signed residual: **no satellite differs from
zero** (all p > 0.07), and mean/RMS is 0.15-3.0 %. This corroborates my
global-median oracle result of 0.04 % from a completely different direction.

**B12 OK — what checks out.** Band populations match the summary exactly for all
11 satellites; the `screened` flag equals `|residual| > 1500` with **0 mismatches
in 184,708 rows** and the raw residual is retained as claimed; label closure is
strictly retrospective (0 non-positive); features are reference-free. The policy's
phase-decorrelation claim is **TRUE** — `|r(age_tx, sin/cos phase)| <= 0.039`
across all satellites, so the 1 h against 1.583 h incommensurability works as
stated. Caveat: it is not uniform, so within a 24-offset episode there are
near-phase-duplicate rows at fixed lags (ISS repeats phase to 4.0 deg at offsets
17 apart), producing a non-decaying within-episode ACF (SENTINEL-6B lag 2 = 0.83,
FLOCK 4H 1 lag 7 = 0.78). Phase is decorrelated from age in aggregate; rows within
an episode are not phase-independent.

**Where I disagree with Reviewer B.** They call criterion 4 ("no satellite above
50 % of the aggregate gain") arithmetically unreachable under equal weighting. That
is wrong as implemented: `analyze_s2.py` computes the share among the *improving*
satellites only, so with two improvers at 0.6 and 0.4 the share is 60 % and the
criterion binds. Their underlying point stands, though — with 11 nominal but about
6 independent objects the criterion is weak, and their proposed replacement
(leave-one-satellite-out and leave-one-cluster-out sign stability) is better.
Adopt it in the rebuild.

### Combined review outcome

Both reviewers returned **FAIL**, independently, on the same primary defect.
Neither disputed the feature-level causality fix: the A5 perturbation, the absence
of any reference-derived feature, and the removal of the old age-versus-gap affine
dependence were confirmed by both. The defect is that E1 fixed *what the features
may read* and left unfixed *which rows exist* (F2) and *whether the rows are
physically transmittable at all* (F1/B1).

### Artifacts

```
experiments/exp15_causal_recovery/
  provisioning_policy.json          E0.5 operational model
  preregistration.json              E2/E3/E4/S2, frozen before any fit (5ab2d396d6ef970f)
  build_causal_dataset.py           E1 builder
  verify_e1.py  E1_verification.json  A1-A5 (see F13 on A1/A2/A4)
  run_walk_forward.py               E2 + E3 + E4
  analyze_s2.py                     S2 decision analysis
  causal_dataset/periodic_24h/*.npz 184,708 transmissions (96.58 % below horizon)
  E4_walk_forward_r{750,1000,1500,2500}.json, _noscreen.json
  S2_analysis_r750.json, _r1500.json, _noscreen.json
loop_engineering/evidence/
  E0_DOSSIER.md                     availability / anchoring audit
  S2_FIRST_DOSSIER.md               this document
```

Manuscript untouched. Nothing committed. E5 and E6 not run.
