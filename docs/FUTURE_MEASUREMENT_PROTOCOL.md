# FUTURE MEASUREMENT PROTOCOL — DESIGN NOTE

**Not a commitment to begin SDR work.** A design note describing how the salvaged
toolkit would apply *if* real RF Doppler measurements became available. Nothing here
is authorized, scheduled or resourced.

Why it exists: the stopped line failed on the *label*, not the method. Inter-TLE
residual labels are missing-not-at-random with respect to staleness, because one
publication outage causes both the staleness and the missingness. A measured label
does not have that property — which is the single reason a measurement route could
succeed where the archive route could not.

---

## 1. Pre-register visible passes

Predict passes from the element the endpoint **holds**, using
`salvage/orbit-evidence-toolkit/scheduler/visible_pass.py`. Declare mask, coarse step,
bisection tolerance and minimum pass duration as numbers. Never sample on a clock grid
and filter afterwards.

## 2. Freeze the transmission schedule before any measurement exists

Build and hash the registry (`registry/causal_registry.py`) with an absolute declared
window. `tx_id`, `pass_id` and `episode_id` are permanent. A measurement may later
change a row's label status, value, uncertainty or closure time; it may never change
whether the row exists. A missed reception is a **censored row**, retained and
reported — not a deleted one.

## 3. Record actual RF timestamps

Persist the commanded transmit instant, the realised transmit instant, and the
receiver timestamp separately. Endpoint clock error maps directly into apparent
Doppler: at LEO altitude a 1 s along-track timing error is ≈ 7.7 km of position, which
perturbs range rate by more than the residuals of interest at short staleness. Record
the clock offset as data, not as an assumption.

## 4. Separate oscillator CFO from orbital Doppler

The received frequency offset is orbital Doppler **plus** transmitter/receiver
oscillator error plus drift. A residual-learning target must isolate the orbital part.
Minimum: characterise the oscillator against a stationary reference across the
temperature range, and carry a per-transmission CFO estimate with its own uncertainty
into the label. Without this, "residual" means "orbital error plus oscillator drift"
and any model will partly learn the crystal.

## 5. Measurement quality controls, declared in advance

SNR floor for an admissible measurement; maximum accepted CFO-estimate uncertainty;
rejection rules for multipath and interference; a physical **floor and ceiling** on
the residual (`contract.physical_scale_check`). Both bounds — a floor alone permitted
a 5.8 %-of-signal excursion in software. Out-of-range rows are labelled and retained.

## 6. Close labels only after measurement

Closure time is the **reception** timestamp, not a catalogue publication. This is the
structural improvement: closure no longer depends on the catalogue, so the censoring
mechanism of failure mode 6 does not arise. Report the censoring rate anyway —
non-reception has its own selection structure (a deep fade correlates with low
elevation, which correlates with geometry).

## 7. Pass- and episode-level statistical units

Within-pass samples are repeated measures; measured ICC 0.59–0.79, and up to 0.999
between symmetric positions in a pass. Aggregate with
`contract.aggregate_repeated_measures` before any metric, interval, win count or
harm count. Block resampling over satellite, then contiguous episodes, with block
length from the measured autocorrelation scale — i.i.d. episode resampling understated
intervals by 3–4× on real data.

## 8. Retain SGP4 as the physics baseline

Unchanged and un-tuned. The comparison is against propagating the held element, which
is what an endpoint would actually do.

## 9. Run a negative control before any residual learning

A cell whose injected effect is zero, at **every** staleness level. If the gate opens
there, stop and find the leak. Two separate leaks in the stopped line would have been
caught by this alone, before any headline number existed.

## 10. Do not reuse any result from the stopped archive experiments

No constant, threshold, cell, improvement figure or endpoint-budget number from
exp14, the deployable rerun, the visible-pass rebuild or EXP16 may be carried forward.
See `../archive/KNOWN_INVALID_RESULTS.md`. Any quantity needed must be re-derived from
measurements.

---

## Honest assessment

A measurement campaign removes the label defect that stopped this line. It does not
make the underlying hypothesis more likely. The archive evidence, weak as it is,
pointed one way: on well-maintained objects at the staleness a realistic provisioning
policy actually reaches, SGP4 propagation of a held element already leaves a residual
that is a small fraction of the Doppler being compensated, and the remaining error is
concentrated in manoeuvre and bad-element events no pre-transmission corrector can
anticipate.

A measurement route should therefore be justified by what it establishes about the
*link* — real CFO, real reception, real packet outcomes — and not by an expectation
that residual learning will succeed. If it is run, run the negative control first.
