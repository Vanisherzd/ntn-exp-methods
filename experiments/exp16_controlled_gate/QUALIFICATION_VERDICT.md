# FINAL MECHANICAL QUALIFICATION PROBE — VERDICT

# STOP EXP16

Probe: `probe_v22.py` against `sim_v22.py` and frozen `physical_config.json` v2.2.
Burned reviewer seeds 1001–1012 only. No `EVALUATION_SEEDS_V2` value was executed —
asserted mechanically at probe start against the full 216-value manifest.
No physical or model parameter was tuned in response to any output.

| check | result |
|---|---|
| Q1 null control | **FAIL** |
| Q2 paired identity | FAIL (partly a probe artifact — see below) |
| Q3 timeline | PASS |
| Q4 mutation channels | FAIL (probe artifact — see below) |
| Q5 physical bounds | **FAIL** |
| Q7 repeated measures | PASS |
| Q8 grid uniformity | PASS (canary correctly does not fire) |
| non-degeneracy | PASS |

**Two failures are genuine benchmark defects and either alone triggers the stop rule.**

---

## Q1 — the negative control is not a null. Decisive.

N0 sets `Δ = 0` exactly. Measured over 12 burned seeds × 9 cells:

| cell | gate-open | B/A | deployment \|r\|/\|D\| |
|---|---|---|---|
| R1 low/SSO S1 | **1.00** | 0.272 | 0.254 % |
| R1 low/SSO S2 | **1.00** | 0.161 | 0.968 % |
| R1 low/SSO S3 | **1.00** | **0.074** | 4.477 % |
| R2 mid/polar S1 | **1.00** | 0.426 | 0.015 % |
| R2 mid/polar S2 | **1.00** | 0.378 | 0.033 % |
| R2 mid/polar S3 | **1.00** | 0.302 | 0.088 % |
| R3 upper/polar S1 | **1.00** | 0.336 | 0.014 % |
| R3 upper/polar S2 | **1.00** | 0.210 | 0.046 % |
| R3 upper/polar S3 | **1.00** | 0.104 | 0.197 % |

Gate-open **1.00 in all nine cells** against a pre-registered ceiling of 0.20, with
the learned corrector cutting MAE by **57–93 % on a cell that contains no injected
error at all**. `negative_control_N0.if_it_fails` in the frozen config: *"the
benchmark is broken and no headline result may be reported from it."*

## Q5 — physical bounds exceeded

Deployment-fold median |r| / median |D_physics|, ceiling 2 %:

- **R1 low/SSO S3: 6.40 %**
- **R2 mid/polar S3: 2.9 %**
- max over all burned runs: **7.909 %**

`pre_implementation_probe.pass_criteria.Q5_physical_bounds` and the standing
instruction: *"If the 2 % ceiling fails: STOP EXP16. Do not reduce the perturbation
after inspection."* No perturbation was reduced.

One sub-check passed: late/early |r| within deployment is 0.92 (p50) and 1.01 (max),
so there is **no unbounded integration** — the OD-error step behaves as intended and
the 77 km divergence of the rejected v2.1 design does not recur.

## Root cause — one defect explains both failures

`held_element()` sets `n_held = n0 + ndot_sec·t_epoch` — the truth's secular mean
motion *evaluated at the element epoch* — and then lets SGP4 propagate with that
value held constant, while the truth's mean motion continues to grow as
`ndot_sec·t`. A rate mismatch of `ndot_sec · age` therefore survives even when
`Δ = 0`, accumulating along-track error as `age²`.

That mismatch is a **deterministic function of age and Doppler rate**, so the ridge
predicts it almost exactly — which is why N0's B/A reaches 0.074 — and it is largest
at the longest staleness, which is why exactly the S3 row breaches the residual
ceiling.

The frozen config asserts the opposite: *"The held element also carries the truth's
secular ndot, so no ndot mismatch survives Delta = 0"*
(`true_element_process.secular_ndot_mismatch: "ZERO"`). **My simulator does not
implement the specification it was written against.**

## Why this is a stop and not a fix

A fix exists and the second reviewer had already named it — carry `ndot` as a *rate*
in the held element, or set `secular_ndot = 0`. Neither is authorized:

- Setting `secular_ndot = 0` changes a **physical parameter after observing probe
  output**, explicitly forbidden.
- Carrying `ndot` as a rate is a **simulator change after observing probe output**.
  The authorization states: *"No v2.3, v3, or additional simulator redesign is
  authorized."*

I could argue the second is mere code-correctness rather than tuning. I am not going
to, because the record does not support my judgement here. Across this session three
of my own "this only implements what was already specified" fixes each introduced a
fresh defect: the reversed bisection bracket in exp15, condition-keyed seeds in v2,
and the unbounded rate step in v2.1. Two more surfaced inside this probe alone — the
held element's mean anomaly diverging over the whole run rather than the propagation
distance, and the truth grid not covering the earliest held epoch. The stop rule
exists because that loop was not converging, and this is the fourth consecutive
cycle in which an independent check found a defect my own review had missed.

## Findings that were probe artifacts, recorded for accuracy

**Q2 (row identifiers).** Pre-onset feature matrices are **bit-identical** —
`max|X_C1 − X_C2| = 0.000e+00` — and rng-state hashes match, so common random
numbers work. The failure is that I compared row identifiers over *all* rows. Post
onset the held element legitimately differs, and since the pass schedule is derived
from the held element, post-onset pass identifiers must differ too. That is not a
pairing violation; my check was wrong.

It does expose a real structural tension worth recording: an intervention on the
held element necessarily perturbs the schedule, so "identical deployment rows across
C1/C2/C3" is **unsatisfiable** — the alternative (intervening on the truth) was
already rejected in v2.1 for unbounded integration. Any future attempt must resolve
that, not assume it away.

**Q4 (tracker / selmeta / gate channels).** My mutations were no-ops: M2 was the
selected candidate, so poking M3's latent state changed nothing; and the
deployment-conditioned selection and gate both happened to choose what the clean run
chose. I measured "mutation produced no change" and reported it as "leak
undetectable". The scaler, coefficient and feature-tensor channels were genuinely
detected. A correct Q4 needs mutations that are effective before their detectability
means anything.

## Results that were sound

- **Q3 timeline PASS.** Both orderings hold; deployment post-onset exposure is 1.000
  in every C2 and C3 run; **zero** C3 post-onset samples leak into validation.
- **Q6.** Oracle affine on (Ḋ, Ḋ·age) reaches out-of-sample R² **0.9985–0.9992**, so
  C1 is permanently classified **CONTROLLED CALIBRATION / SANITY SCENARIO** — as
  pre-registered before the run. Candidate R²: age only 0.03–0.25, Doppler rate only
  0.61–0.95, age + rate 0.87–0.98, full set 0.87–0.98.
- **Q7 PASS.** Within-pass ICC of |r| = 0.124 (p50), aggregation collapses 93
  deployment samples to 31 passes before any metric.
- **Q8 PASS.** Canary correctly does not fire: gate-open spans 0.58–1.00 and
  validation ratio 0.051–0.566 across cells.
- **Non-degeneracy PASS.** 264 helpful and **60 harmful** realizations, harm arising
  from the fair sign draw — C1 harm 0.00 everywhere, C2/C3 harm 0.42 in six of nine
  cells. The manoeuvre shift does what BLOCKER 1 required.

## Provenance

```
physical_config.json  sha256 1e07d768d6339f4f… (v2.2, frozen before the probe)
sim_v22.py            sha256 recorded in PROBE_RESULT.json
evaluation_seeds_v2.json  216 values, none executed (asserted at probe start)
burned seeds          1001–1012, 90001–90003, 7, 11, 777001–777012, 811001–811012
```

Full numeric record: `PROBE_RESULT.json`.

## Verdict

# STOP EXP16

The workshop benchmark is not qualified. Its negative control admits a corrector in
100 % of runs on a cell containing no error, and its residual exceeds the
pre-registered physical ceiling by up to 4×. No further design revision or simulator
redesign is authorized, and none is recommended.

Manuscript untouched. Nothing committed.
