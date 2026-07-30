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

---

# FINAL CLAIM SET — human-authorized reframing, 2026-07-31

This section supersedes every contribution list above. Earlier sections are retained as a
record of what was claimed and when; they are **not** the current claim set.

## The withdrawal

Contribution 3 was previously *"a fault-injection evaluation with genuinely held-out
mutations."* Adversarial review (R1–R4) established that the evidence does not support it:

| mutation | rule | finding |
|---|---|---|
| HO1 | L1.5 | mutated object consumed **only** by its own detector — reachability, not pipeline detection |
| HO4 | L2.4 | same defect |
| HO3 | L4.7 | detector **rewritten after** its outcome was recorded; withheld status void |
| HO2 | L4.6 | survives: specified before its detector, injected through the pipeline, untouched |

One surviving case. Restoring the claim would require newly frozen, independently authored
mutations — new evidence generated after reviewer feedback, which the governing rules
forbid. The claim was therefore **withdrawn by human decision**, not repaired.

## Final one-sentence thesis

> Orbit-Evidence turns deployment-time availability, row membership, model-state and
> statistical-unit assumptions into executable CI checks for satellite communication
> experiments; a curated regression suite demonstrates those checks on seventeen known
> fault classes that chronological ordering alone is not designed to detect.

## Final three contributions

1. **A deployment-causality threat model and contract.** Six protected objects — decision
   time, feature availability, row membership, label closure, state channels, statistical
   units — organised as **19 executable rules** in four mechanically checkable layers:
   availability and closure (L1), physical and scheduling validity (L2), model-state
   causality (L3), statistical independence and reproducibility (L4).

2. **Orbit-Evidence, an implementation.** A dependency-light toolkit (**780 lines** across
   four modules, `numpy` only): visible-pass scheduling, freeze-then-label row registry,
   reference-ensemble labelling with published uncertainty, canaries over six state
   channels, and seed, provenance and statistical-unit controls.

3. **A curated fault-injection regression evaluation.** **17** curated fault classes in two
   minimal pipelines and three deterministic environments: chronological protocol checks
   detect **2/17**, the contract detects **17/17** (51 injected cells), clean reference
   paths are accepted, the sweep is deterministic and runs in **under 2 s**, and two case
   studies show defects chronology does not constrain. Reported as **represented-fault
   regression coverage**, not sensitivity or generalisation.

## Numbers, and where they come from

Every manuscript number is generated from `evaluation/results/final_summary.json`.
`paper/scripts/check_banlist.py` fails the build if the manuscript quotes a value the
artifact does not contain, and separately if any withdrawn wording is reachable.

| quantity | value |
|---|---|
| contract rules | 19 |
| curated fault classes | 17 (was 18 until D12 was found identical to D3) |
| injected cells | 51 |
| chronological baseline | 2/17, measured |
| contract detection | 17/17 |
| rules with a demonstrated red fixture | **16 of 19** (L2.2, L2.3, L4.5 clean-path only) |
| L4.7 clean false-halt rate | 0.042 over 450 clean paths, nominal α = 0.05 |
| L4.7 injected detection | 150/150 |
| runtime | under 2 s (bound; wall-clock varies run to run) |
| toolkit / tests | 780 / 490 lines |
| tests passing | 30 |

## Retired claims — must not reappear

- "four held-out mutations", "genuinely held-out", "mutations withheld from the detector
  authors"
- any generalisation to unseen fault classes
- "all nineteen rules have two-sided red/green tests" (16 do)
- the 18-fault and 54-cell denominators
- 1095 / 812 / 739-line toolkit counts; 0.31 s runtime

All are enforced mechanically by `WITHDRAWN_CLAIMS` in `paper/scripts/check_banlist.py`.
The `DEV_FAULTS` / `LATE_SPECIFIED` split survives in code as provenance only, with an
explicit comment that it carries no evidential weight.
