# FAILURE TAXONOMY — INTERNAL RESEARCH GUIDANCE

Not a paper result and not a contribution. Twelve failure modes found across four
review cycles of a stopped research line, recorded so they are not repeated. Each
entry names the mechanism, what it measured, and the check that catches it.

Every quantitative figure below comes from an invalidated experiment and is cited
only as evidence that the failure mode is real. See
[`../archive/KNOWN_INVALID_RESULTS.md`](../archive/KNOWN_INVALID_RESULTS.md).

---

## 1. Feature availability leakage

A feature computable only after the decision instant. Here: the stale-to-reference
**element epoch gap**, fixed by a future publication, consumed by two of three
candidates. Removing it moved the headline cell from +1.94 % to −0.70 %.

*Catch:* perturb the future quantity and require every feature to be bit-identical.
Deriving the feature list from a manifest is not enough — the leak was in a name that
looked innocuous.

## 2. Element epoch versus publication time

Treating an element's epoch as the moment it became available. Measured 24.3 h apart
on a sampled record; 15.4 % of pairs handed the endpoint an element not yet
published, and 50.3 % sampled transmissions when a fresher element already existed.

*Catch:* select the held state by publication timestamp, never epoch. Audit the
availability field before trusting it — here it was usable only for epochs ≥ 2014
(before that: archive backfill up to 50,337 h, then a regime with 52–94 % negative
lag).

## 3. Transmission scheduling outside visibility

Sampling on a UTC grid and filtering by elevation afterwards. **96.58 %** of one
dataset placed the satellite below the endpoint horizon, median elevation −42.5°;
only 1.45 % were above 10°, and the residual was **5.6× larger** on visible geometry.
The consequence was not a shrink but a reordering — the visible/all ratio ran 0.2 to
19.2 across objects, so the gate's verdict per object could flip.

*Catch:* generate transmissions from passes predicted by the held state. Filtering
cannot repair it: 2,682 usable rows survived from 184,708.

## 4. Future-dependent row membership

Two directions, both real. Rows silently **dropped** when no qualifying later
reference existed — drop rate rising with the study covariate to 100 % for one
object. Rows silently **created** because the schedule's extent ended at the
archive's last entry — 29 % of one object's rows existed only because more data had
been downloaded.

*Catch:* build and hash the registry before consulting any label source; declare the
schedule window as an absolute constant. Later information may change a label's
status, value, uncertainty or closure time — never whether the row exists.

## 5. Label ambiguity and uncertainty

A label defined as "the first qualifying later solution" is arbitrary among several
valid ones. The spread across equally valid references **exceeded the label itself in
51.8 %** of visible cases, ratio 1.81 at short staleness. An ensemble median with
published MAD cut that to 0.06–0.39.

*Residual trap:* when most members lie on the same side in time they share a common
propagation error a mutual MAD cannot see. A split-half by propagation distance found
a hidden systematic **5–16× a 5 % decision margin**. Treat σ as a lower bound and
publish the split-half spread beside it.

## 6. Censoring tied to the scientific covariate

The deepest finding. A publication outage simultaneously makes the held element stale
**and** removes the later elements needed to label it, so missingness and the study
covariate share one cause. Measured |SMD| up to 1.35 on age; censored rows waited
4–13× longer for the next publication.

*Not repairable by restriction:* no age cap made censoring non-differential for all
objects. Inverse-probability weighting cost ≤ 1.3 % effective sample for eight of
nine objects but asked ~10 independent passes to represent 574 rows for the ninth.
Even a generous stratified bound left **six of nine objects with a bound on the
baseline wider than the effect being sought**.

*Catch:* measure standardized differences between labelled and censored rows on
pre-decision covariates only — and **calibrate the threshold**, because a constant
limit fails under genuinely random censoring whenever the censored group is small
(measured P(exceed 0.10 | MCAR) = 0.68–1.00).

## 7. State-channel leakage outside the feature tensor

A canary scoped to "a feature column" cannot see a leak through model, scaler,
tracker, selection or gate state. A tracker permitted to keep observing residuals
produced a **14–31 % gain and 67–92 % admission on a null control**.

*Catch:* six channels, each with an *effective* mutation. A mutation that is a no-op
reports "undetectable" where "ineffective" is true — verify the mutation bites before
trusting its detectability.

## 8. Unpaired condition randomness

Including the condition label in a seed key gives each arm a different physical
realisation, while every surface claim still reads "conditions differ only in the
intervention". Silent, and it invalidates the comparison the design exists to make.

*Catch:* derive one seed per invariant cell; assert the feature matrices are
bit-identical across arms; assert the random stream itself is byte-identical, since
condition-dependent draw *order* breaks pairing without changing any seed.

## 9. Absorption / refresh timeline contradictions

An intervention that a later refresh absorbs may vanish before the window it is meant
to affect. Measured: absorption at day 43–45 against a validation window ending at
48, and day 49–51 against a deployment window of 48–60 — the mismatch was gone in all
six condition × covariate combinations. Separately, "state advances only at refresh"
and "no observation during deployment" cannot both hold when refreshes fall inside
the deployment window.

*Catch:* write every boundary as a number and assert the orderings mechanically,
including that the intervention is still active at window end.

## 10. Negative controls containing hidden deterministic signal

Two independent instances. A leaked tracker state gave 83–92 % admission. A secular
rate mismatch surviving zero injection gave **100 % admission with 57–93 % apparent
gain** — because freezing a growing rate at the element epoch leaves a residual that
is a deterministic function of age, and therefore trivially learnable.

*Catch:* run the control at **every** level of the covariate — the second leak was
monotone in staleness and invisible at the single level where the control had been
scheduled.

## 11. Functional-form matching between generator and learner

If an oracle built from admissible terms reproduces the generator, the scenario is a
calibration control, not evidence of learning. Measured: a single-feature guard read
0.66–0.77 while a two-term oracle reached **0.998**.

The corollary is sharper: the benchmark's *difficulty* was set by which admissible
feature had been left out. Omitting one legal quantity moved explained variance from
0.70 to 0.998. Difficulty must be pre-registered as a physical choice, not inherited
silently from a feature list.

## 12. Fixes that introduce secondary defects

The mode that ended the line. Every fix addressed its named problem and introduced a
new one:

| fix | new defect |
|---|---|
| removed the leaking feature | dataset still 96.58 % below horizon |
| generated from visible passes | exit-crossing bisection bracket reversed |
| stopped absorbing the intervention | error integrated to 5.8 % of signal, 77 km |
| keyed seeds deterministically | condition in the key destroyed pairing |
| froze the rate at element epoch | deterministic mismatch broke the null control |

Four consecutive cycles; in each, an independent check found a defect the author's own
review had missed. **The lesson is procedural, not technical:** a fix is a change, a
change carries its own defect rate, and self-review does not detect it. Budget an
independent adversarial check per fix, and set a hard stop count in advance — the loop
does not converge on its own.

---

## Summary — the two that would have saved the most

**A null control that is genuinely null.** Every leak in this taxonomy would have
surfaced as admission on a zero-effect cell, at any covariate level, before any
headline number was computed.

**Tests that fail.** Three historical tests were unfalsifiable: one compared two
arrays built from the same object, one pinned the parameter carrying the dependence it
tested, one attached no threshold to what it reported. A suite that cannot go red is
not evidence. Prove each test fails against the broken implementation — see
`salvage/orbit-evidence-toolkit/tests/test_regressions.py`, which does exactly that
for all twelve modes.
