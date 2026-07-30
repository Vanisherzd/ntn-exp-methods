# TLE Aging Methodology (Paper 1)

> Clarifies how TLE staleness is modelled and how timing / Doppler residuals are
> derived. Software-only and model-derived; no measured RF, no live-satellite
> data. This document exists to forestall the common reviewer misreading that the
> staleness study is "just additive Gaussian drift."

## 1. Historical-TLE / SGP4-based staleness — not synthetic noise

Staleness is constructed from **real historical Two-Line Element sets** of the
same physical object (the BLACK KITE satellites, BK1/BK2) pulled across multiple
epochs, propagated with the standard SGP4/SDP4 analytical propagator
(python-SGP4). A "stale" prediction is a genuine SGP4 propagation from an **older**
TLE epoch forward to the evaluation time; the staleness axis (8, 24, 48, 72, 96,
168 h) is the propagation gap between the TLE epoch and the evaluation epoch.

This is fundamentally different from adding `N(0, σ²)` to a clean state. The error
arises from the propagator + element-set physics: SGP4 fits mean elements through
an observation arc, and drag/`B*`, third-body, and fit artifacts accumulate with
propagation time. The result is **structured, monotone, and object-specific**, not
white noise.

## 2. Stale-vs-fresh, same-object reference

For each staleness we form a **same-object** comparison:

- `f_phys` : SGP4 propagation from the **stale** TLE epoch to evaluation time.
- `D_ref`  : SGP4 propagation from a **fresh** TLE epoch (near the evaluation
  time) of the **same object**, used as the reference state.

The residual `D_ref − f_phys` is therefore a **model-to-model inter-TLE residual**
of one physical satellite — the quantity a terminal would have to correct if it
only held a stale TLE. It is explicitly **not** a measured RF-channel residual;
`reference_is_measured_truth = false`. Both sides are SGP4 propagations, so any
"truth" here is the fresh-TLE propagation, not an observation.

## 3. Timing and Doppler residual derivation

From the same-object state residual we derive the two control-relevant quantities:

- **Doppler residual [Hz].** Project the relative position/velocity onto the
  ground-station line of sight to get radial velocity `v_r`, then
  `Δf_D = (Δv_r / c) · f_c` at `f_c = 868 MHz`. The held-out Doppler MAE vs.
  staleness (icc_main.tex Table `tab:bk`, BK1: 0.24 Hz @ 8 h → 26.9 Hz @ 168 h) is
  exactly this residual — small against the 500 Hz hop-bin tolerance, which is the
  paper's central negative result (SGP4 is already good enough; learning does not
  help and the evidence gate closes).

- **Timing residual [s].** The dominant SGP4 staleness error is **along-track**
  (phase) error. We convert along-track position error to a timing offset via
  `σ_t = Δs_along / v_orbital` (orbital speed ≈ 7.67 km/s). For the control
  proxies (exp7/exp8) the open-loop along-track growth is taken as the documented
  ~1.5 km/day rule-of-thumb (literature range 1–3 km/day), giving σ_t on the order
  of 0.07 s @ 8 h to 1.4 s @ 168 h. This timing residual sizes the guard band and
  drives the TX-window coverage proxy.

## 4. Why this is NOT simple Gaussian drift

1. **Source.** Errors come from propagating a real fitted element set, not from a
   sampled noise process. Two terminals holding the same stale TLE see the **same
   deterministic** offset, not independent random draws.
2. **Structure.** The error is dominated by a deterministic along-track phase term
   that grows with propagation time; the Doppler residual is monotone in staleness
   and object-specific (BK1 ≠ BK2, and BK1→BK2 transfer is actively harmful).
3. **Mean behaviour.** The held-out inter-TLE residual is near zero-mean but
   **weakly structured**, mixing model-fit artifacts, drag mismatch, and
   occasional maneuver-/bad-fit events — which is precisely why an always-on
   learner overfits validation noise and the evidence gate is the safe design.
4. **Bounded by physics, not variance.** At 168 h the BK1 baseline Doppler MAE is
   still only 26.9 Hz; a Gaussian-drift model with a free σ would not reproduce the
   sub-tolerance, satellite-specific saturation seen in the real data.

## 5. What the staleness model is used for

| Use | Where | Nature |
|---|---|---|
| Real negative result (gate closes) | icc_main.tex §V, Table `tab:bk` | historical TLE, SGP4-derived, held-out |
| Open-loop SGP4 timing-σ vs staleness | exp7 (B) | along-track rule-of-thumb proxy |
| Control ablation residual σ values | exp8 | exp2/exp3 calibrated residuals |

The first row is the **empirical headline**; rows two and three are **transparent
proxies** that characterise the control mechanism *when the gate opens*. None of
them is a Gaussian-drift surrogate, and none involves measured RF.
