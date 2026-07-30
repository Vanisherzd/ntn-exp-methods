# CLAIM LEDGER

Every proposed claim, classified by what actually supports it. Four categories:

- **M — DIRECTLY MEASURED** by the new fault-injection evaluation on clean fixtures.
- **R — RECONSTRUCTED** from a stopped pipeline: a defect *characterisation*, sound as
  a count, but observed on an experiment subsequently halted. Citable only as
  case-study evidence with the framing in `INVALID_RESULT_BANLIST.md`.
- **P — DESIGN PRINCIPLE ONLY.** No measurement. Worded as a design position, never a
  finding.
- **X — REJECTED.** Supported only by retired numerical results. Struck.

---

## C1 — Chronological splitting does not protect availability
| | |
|---|---|
| claim | "Chronological train/validation/test splitting enforces temporal ordering but does not by itself establish that a feature was *available* at the decision instant." |
| artifact | `docs/FAILURE_TAXONOMY.md` §1–2; `test_publication_time_not_element_epoch` |
| class | **M** (mechanism demonstrated) + **P** (general position) |
| allowed | "ordering is necessary but not sufficient for availability" |
| prohibited | "prior work is wrong"; "chronological splits are invalid" |

## C2 — A quantity's timestamp is not its availability time
| | |
|---|---|
| claim | "In catalogue-fed pipelines an item carries at least two clocks — when it describes, and when it was published — and conflating them admits data the system could not have held." |
| artifact | `test_publication_time_not_element_epoch`; taxonomy §2 |
| class | **M** for the mechanism; **R** for the field observation that the clocks differed by 24.3 h on a sampled record |
| allowed | "the two clocks are distinct and must be checked separately" |
| prohibited | citing the 15.4 % / 50.3 % pairing rates as a general property of catalogues |

## C3 — Row membership can depend on the future in both directions
| | |
|---|---|
| claim | "Which rows exist can be decided by later data — dropped when a later reference fails to appear, created when a schedule's extent is derived from the data on hand." |
| artifact | `registry/causal_registry.py`; `test_row_membership_independent_of_future_catalogue` |
| class | **M** (both directions reproduced in a fixture); **R** (100 % drop for one object, 29 % creation for another) |
| allowed | "membership must be frozen and hashed before labels are consulted" |
| prohibited | presenting 29 % / 100 % as typical magnitudes |

## C4 — Leakage occurs through state channels outside the feature tensor
| | |
|---|---|
| claim | "Future information can enter through scaler parameters, model coefficients, tracker latent state, selected-model metadata or the gate bit — none of which is a feature column." |
| artifact | `contract.STATE_CHANNELS`, `mutation_canary`; five parametrised channel tests |
| class | **M** (six channels, each with an effective and an inert mutation) |
| allowed | "a canary scoped to the feature tensor misses five of six channels" |
| prohibited | quoting the 14–31 % gain figure as a performance result |

## C5 — A negative control is the highest-yield single check
| | |
|---|---|
| claim | "A control whose injected effect is exactly zero, evaluated at every level of the study covariate, detects the widest range of defects earliest." |
| artifact | `contract.negative_control_verdict`; `test_negative_control_has_no_systematic_signal` |
| class | **M** for the detector; **R** for two independent leaks each surfacing as admission on a zero-effect cell |
| allowed | "in both stopped pipelines the control would have fired before any headline quantity was computed" |
| prohibited | any admission-rate number as a result |

## C6 — Sampling can be temporally valid and physically impossible
| | |
|---|---|
| claim | "A schedule can satisfy every temporal constraint while placing the link in a geometry that cannot carry it; validity must include the physical sampling itself." |
| artifact | `scheduler/visible_pass.py`; `test_transmissions_above_visibility_mask` |
| class | **M** (grid sampling majority-invalid, pass generation not); **R** (96.6 % in one stopped pipeline) |
| allowed | "generate from predicted geometry rather than filtering a clock grid" |
| prohibited | "96.6 % is representative" |

## C7 — Unpaired condition randomness silently invalidates comparisons
| | |
|---|---|
| claim | "Including the condition label in a seed derivation gives each arm a different realisation while every surface claim still reads 'conditions differ only in the intervention'." |
| artifact | `contract.common_random_numbers`, `assert_paired`; `test_common_random_numbers_across_conditions` |
| class | **M** |
| allowed | "pairing must be asserted on the realised arrays, not assumed from the seed rule" |

## C8 — Generator/learner form matching makes a scenario a calibration control
| | |
|---|---|
| claim | "If an oracle built from admissible terms reproduces the generator out of sample, the scenario tests calibration, not learning; a single-feature guard cannot see this." |
| artifact | `contract.functional_form_match`; `test_generator_matches_declared_physics` |
| class | **M** (fixture: single-feature guard < 0.95 while a two-term oracle exceeds it) |
| allowed | "difficulty must be pre-registered as a physical choice, not inherited from a feature list" |
| prohibited | quoting EXP16's oracle R² as a paper result |

## C9 — Repeated measures inflate precision
| | |
|---|---|
| claim | "Samples within one physical event are replicates; treating them as independent overstates precision by roughly the square root of the group size." |
| artifact | `contract.aggregate_repeated_measures`, `within_group_icc`; `test_within_pass_samples_are_not_independent` |
| class | **M** for the detector; **R** for measured ICC 0.59–0.79, up to 0.999 between symmetric positions |
| allowed | "aggregate before any metric, interval or count" |

## C10 — Fixes carry their own defect rate
| | |
|---|---|
| claim | "Each corrective change is itself a change and can introduce a new defect; self-review does not reliably detect this, so a fix budget and an independent check per fix are needed." |
| artifact | `docs/FAILURE_TAXONOMY.md` §12 — five fix→new-defect pairs over four review cycles |
| class | **R** (process observation, not a measurement) |
| allowed | "we observed five successive corrective changes each introduce a new defect across four independent review cycles" |
| prohibited | generalising a defect *rate*; claiming universality |

---

## Rejected

| # | claim | why struck |
|---|---|---|
| X1 | residual Doppler learning improves prediction | retired results (B1) |
| X2 | the Evidence Gate reduces communication failure | never established (B6) |
| X3 | "the gate admitted/refused in N of M cases" | EXP16 probe performance (B4) |
| X4 | any endpoint budget, guard-time or energy conclusion | B5; no PHY simulation was run |
| X5 | "the toolkit shows published studies invalid" | unsupported, out of scope |
| X6 | "the contract is complete" | no completeness argument exists; must be a limitation |

---

## FINAL THESIS

> **Chronological splitting protects the order of data but not its availability, its
> membership, or the hidden state of a learner; we give an executable experiment
> contract that mechanically detects deployment-causality, label-availability and
> hidden-state defects a chronological split alone cannot prevent.**

## EXACTLY THREE CONTRIBUTIONS

1. **A threat model and contract.** Six protected objects — decision time, feature
   availability, row membership, label closure, state channels, statistical units —
   and the deployment-causality violations each admits, organised as four mechanically
   checkable layers (L1 availability, L2 physical/scheduling validity, L3 model-state
   causality, L4 independence and reproducibility).

2. **Orbit-Evidence, an executable implementation.** A dependency-light toolkit
   (1,095 LOC, `numpy` only): visible-pass scheduler, freeze-then-label transmission
   registry, reference-ensemble labelling with published uncertainty, six-channel
   mutation canary, seed and provenance controls — every detector backed by a
   two-sided test that fails on a broken fixture and passes on the clean path.

3. **A fault-injection evaluation with genuinely held-out mutations.** Eight
   development faults plus four mutations specified before their detectors were
   written, injected into two clean pipelines across three deterministic environments,
   reporting detection rate, held-out detection rate, clean-path false positives,
   determinism and CI runtime — plus two case studies in which chronology-compliant
   experiments were halted by a contract rule.

---

## Loop-0 gate: does this still sound like a failed Doppler-learning paper?

**No — because the unit of evidence changed.** In the retired line the evidence was a
*model's* performance on satellite data, and every claim died with the dataset. Here
the evidence is a *detector's* behaviour on injected faults, which is independent of
whether any residual learner works. The satellite setting supplies the threat model
and two case studies; it supplies no performance claim.

The real risk is different and worth naming: that this reads as an internal bug report
dressed as methodology. Three things separate it. The threat model is **not
satellite-specific** — availability-versus-timestamp and state-channel leakage arise in
any online-learning system fed by a published data source. The evaluation is a **tool
evaluation with held-out mutations**, the standard form for methodology work, not a
retrospective. And the artifact is **externalisable**: 1,095 LOC, one dependency, no
proprietary data.

What the paper must not do is lean on the stopped project for authority. The stopped
project is the *source* of the threat model and of two case studies. The *evidence* is
the fault-injection matrix.
