# LOOP 4 — CASE-STUDY ANALYSIS

Two software pipelines from a stopped research programme. Both were built with
chronological train/validation/deployment splitting and both passed it. Neither
reports a model-performance number here; the finding in each case is *which contract
rule halted the experiment, and why ordinary checks did not*.

---

## Case study 1 — retrospective orbital-label pipeline

### Apparently valid structure

An endpoint holds a stale orbital element set and predicts a link parameter open-loop.
Labels are formed retrospectively by comparing the held prediction against a later,
better-determined element set from the same catalogue. Folds are split
chronologically by reference time; no label from the future of a fold enters its
training data; every feature is drawn from the held element and the transmission
timestamp.

### Hidden defects

Three, in sequence, each found only after the previous was fixed.

1. **A feature was temporally past but not yet available.** The interval between the
   held element's epoch and the *reference* element's epoch was used as a feature. It
   is a difference of two past timestamps, so it survives every ordering check — but
   the second timestamp belongs to an element the endpoint had not yet received.
2. **Row membership depended on the future catalogue.** A transmission entered the
   dataset only if a qualifying later element was subsequently published. The drop
   rate rose with the study covariate.
3. **Label availability was coupled to the covariate.** A catalogue publication outage
   simultaneously makes the held element stale *and* removes the later elements needed
   to label that staleness, so missingness and the covariate share one cause.

### Why chronological splitting did not catch them

Chronology constrains the *order* of quantities that are already in the dataset. It
says nothing about (i) whether a past-dated quantity had been *published*, (ii) which
rows exist at all, or (iii) whether the *probability of having a label* depends on the
covariate under study. All three defects are invisible to an ordering test because
none of them violates ordering.

### Contract rules that detected them

**L1.1** feature availability (truncation test), **L1.2** availability clock,
**L1.4** row membership (future-truncation invariant), and the censoring diagnostic
that compares labelled against censored rows on pre-decision covariates only.
**L2.1** additionally halted an intermediate version whose transmissions were
scheduled on a clock grid rather than inside predicted-visible geometry.

### Consequence if evaluation had continued

The defects would invalidate any deployment interpretation of the result: a reported
improvement could not be attributed to information an endpoint would actually hold.
Under the third defect the comparison is not merely biased but **undetermined** — the
baseline itself is not pinned down more tightly than the effect being sought, so no
margin is resolvable at any sample size. The contract prevented formal evaluation from
proceeding.

---

## Case study 2 — controlled learning and gating pipeline

### Apparently valid structure

A physics baseline, an optional learned residual branch, candidate selection on a
chronologically prior validation window, an admission decision frozen before the
deployment window opens, and fallback to the baseline when the decision is negative.
Selection and admission read validation quantities only. A negative control with the
injected effect set to zero is included.

### Hidden defects

1. **Future information entered through a non-feature state channel.** The feature
   tensor was clean and verified so by perturbation. But a stateful tracker continued
   to advance at refresh events that fell *inside* the deployment window, so the learner
   kept observing outcomes after its own freeze. The leak was in latent state, not in
   any column.
2. **The negative control contained undeclared deterministic signal.** A secular rate
   was frozen at the element epoch while the reference continued to evolve, leaving a
   residual that is a deterministic function of the covariate — and therefore trivially
   learnable — even with the injected effect at exactly zero.
3. **Compared conditions did not share a realisation.** The condition label entered
   the seed derivation, so each arm received different randomness while every surface
   description still read "the conditions differ only in the intervention".

### Why chronological splitting did not catch them

The split governs *rows*. Defect 1 lives in model state, which no row-level split
constrains; the tracker's update was chronologically forward at every step and still
wrong, because it crossed the freeze. Defect 2 involves no leakage at all — the
control's rows are perfectly ordered and its target is simply not null, which an
ordering check has no means to notice. Defect 3 is a property of the random stream,
not of time.

### Contract rules that detected them

**L3.1** state channels (a six-channel canary; a canary scoped to the feature tensor
misses five of the six), **L3.2** canary effectiveness — which distinguishes an
undetected leak from an *inert* mutation, a distinction that had previously been
reported the wrong way round — **L3.3** negative control, and **L4.2** paired
randomness.

### Consequence if evaluation had continued

Negative controls exposed undeclared deterministic signal, so any admission observed
on a treatment cell could not be attributed to the treatment. Blind evaluation seeds
remained unexecuted after qualification failed: the contract halted the programme
before the pre-registered seeds were run, so no result exists to be misread.

---

## What the two cases have in common

Both pipelines satisfied the standard remedy and both were nonetheless
uninterpretable. In case 1 the defects concern *which data exists and when it became
knowable*; in case 2 they concern *what the learner's state has seen* and *whether the
control is a control*. Chronological splitting addresses neither category, because
neither is an ordering property.

Both cases also show the same procedural failure, and it is the one worth carrying
forward: **each corrective change introduced a new defect.** Five successive fixes,
four independent review cycles, and in every cycle a defect the implementer's own
review had missed. That is an argument for a *fix budget* and an independent check per
fix, not for more careful fixing.

## Externalisability

Neither case study depends on the stopped programme's data or generative model. Case 1
generalises to any pipeline whose labels come from a published feed that lags the
quantity it describes; case 2 to any online-learning system with a frozen deployment
state and a stateful component. The contract rules that halted them are the same rules
the fault-injection evaluation exercises on clean fixtures.
