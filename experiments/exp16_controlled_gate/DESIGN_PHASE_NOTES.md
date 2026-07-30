# DESIGN-PHASE NOTES (pre-implementation)

Not results. DEBUG seeds / single realisations only, never reportable as
experimental evidence. Recorded so that nothing found during design review is lost.

## N1 — residual scale floor clears as pre-registered. No tuning performed.

`debug_probe_residual_scale.py`, systematic term only (no OU noise), one
realisation per cell. Floor = median |r| ≥ 0.1 % of median |D_physics|.

| regime | age 6 h | age 24 h | age 72 h |
|---|---|---|---|
| R1 low/SSO | 43.9 Hz (**0.407 %**) | 82.9 Hz (1.055 %) | 268.3 Hz (2.683 %) |
| R2 mid/polar | 21.9 Hz (**0.219 %**) | 43.2 Hz (0.401 %) | 96.4 Hz (0.913 %) |
| R3 upper/polar | 16.3 Hz (**0.192 %**) | 30.0 Hz (0.367 %) | 57.8 Hz (1.040 %) |

**All 9 cells clear the floor at the pre-registered `Δn = 5×10⁻⁵` rev/day. No
parameter was changed.** Adding the zero-mean OU disturbance can only raise
median |r|, so these are lower bounds on the eligibility margin.

Tightest margin: R3 upper/polar at 6 h staleness, **1.9× the floor**. Flagged as
the cell most likely to be labelled `INSUFFICIENT_RESIDUAL_SCALE` if the OU term
behaves unexpectedly. It will be reported and retained either way, never tuned.

Analytic cross-check, along-track drift `ds = 2πa·Δn·age`: **0.54 / 2.16 / 6.49 km**
at 6 / 24 / 72 h. This reproduces the documented behaviour that TLE-based position
degrades a few kilometres per day, which is the evidence that the perturbation
magnitude is physically motivated rather than chosen for convenience.

Sanity against the real archive: the archived real-TLE cohort had median |r| of
0.5–38.7 Hz at ages 17–66 h. The simulated systematic term is 30–96 Hz at 24 h —
the same order of magnitude, 2–6× larger. Being somewhat larger is the intended
direction: it keeps the benchmark clear of the sub-noise-floor pathology
(0.006–0.36 % of Doppler) that made the real archive unable to resolve its own
question, while staying inside physical plausibility.

## N2 — a defect I found in my own probe, and the config ambiguity that caused it

My first probe produced residuals of **5–78 % of the Doppler** — physically absurd.
Cause: I constructed the held element by hand-computing its mean anomaly
(`MA − n·360·age`) instead of letting SGP4 propagate it, which injects a large
arbitrary phase error that swamps `Δ`.

The correct construction, verified above:

```
one element set e0 at epoch ep0
truth   = SGP4(e0,      t)      # SGP4 is self-consistent, so this IS truth
held    = SGP4(e0 + Δ,  t)      # same set, injected OD error
age     = t − ep0               # staleness is the propagation distance
r(t)    = D(truth) − D(held)    # arises PURELY from Δ propagated over age
```

The time-varying truth (`OU_n`, `OU_b` on the true element sequence) then supplies
the second, *unpredictable* mechanism by which truth diverges from any single
frozen element set.

**`physical_config.json` → `generative_chain.step_3` is ambiguous** — "e_held =
e_true(t_refresh − age) with an injected OD error" invites exactly the wrong
construction I fell into. It must be rewritten to state the single-element-set
form explicitly **before the pre-registration commit**. This is a clarification of
construction, not a change of any magnitude, and no model has been fitted and no
evaluation seed run. Held for application together with the reviewer's findings so
the reviewer is not reviewing a moving target.
