# LOOP 1 — FAULT-INJECTION PRE-REGISTRATION

**Frozen before any detector for a held-out mutation is written.** No detector may be
edited after its held-out mutation result is inspected. No mutation may be weakened
after it survives detection.

---

## Integrity problem with the suggested held-out set — surfaced, not worked around

The instruction offered four example held-out mutations. Checking them against the
existing detectors, **three already have a detector written against exactly that
channel**, so injecting them would not test generalisation — it would re-test a
detector on the case it was built for:

| suggested | existing detector | genuinely held out? |
|---|---|---|
| H1 future info via model metadata | `mutation_canary` channel `selected_model_metadata`, exercised by `test_mutation_canary_channels` | **NO** |
| H2 reference-dependent schedule boundary | partially — `assert_membership_independent_of_future` covers membership, not the window | **PARTLY** |
| H3 gate state recomputed from held-out outcomes | `mutation_canary` channel `gate_state` | **NO** |
| H4 within-pass samples counted as independent | `within_group_icc` + `test_within_pass_samples_are_not_independent` | **NO** |

Using them would make the held-out detection rate trivially 4/4 and the number
meaningless. The four suggested faults are therefore **reclassified as development
faults D9–D12** (they are legitimate faults, already covered), and four *genuinely*
held-out mutations are defined below.

A held-out mutation here means: **the specific defect is defined now, and either no
detector exists for it, or the only candidate detector is a general rule that was not
written with this defect in mind.** The question the evaluation answers is whether the
contract *generalises*.

---

## Pipelines

Minimal deterministic fixtures only. **The stopped EXP16 generator is not used as a
scientific simulator** — the fixtures exist solely to exercise contract rules, and
carry no physical claim.

**CASE A — retrospective orbital-label pipeline.** Held orbital state → visible-pass
scheduling → frozen transmission registry → later reference construction → label
closure. Analytic circular-orbit propagator; no SGP4 dependency.

**CASE B — controlled learning/gating pipeline.** Physics baseline → optional learned
branch → validation selection → frozen model/scaler/gate state → held-out deployment.
Closed-form linear target; no orbital dynamics.

---

## Development faults (detectors already exist)

**AMENDMENT, recorded after the fact and disclosed in the paper's threats section.**
Two development faults (D13 fold-order, D14 seed-hygiene) were added after this document
was frozen; both target rules that already existed. One (D12) was later removed on review,
its injector having been the same branch as D3 and producing a byte-identical registry. The
frozen set was eleven development faults; the reported set is thirteen. The withheld set
below is unchanged, but see the threats section for why only one of the four supports the
generalisation claim.

| id | fault | severity |
|---|---|---|
| D1 | future/reference epoch used as a feature | high |
| D2 | element epoch mistaken for publication time | high |
| D3 | future catalogue changes row membership | high |
| D4 | below-horizon transmissions | high |
| D5 | label closes after model refresh | high |
| D6 | scaler/model/tracker receives future state | high |
| D7 | condition seeds not paired | medium |
| D8 | negative control contains deterministic signal | high |
| D9 | future info injected via selected-model metadata | high |
| D10 | gate state recomputed from held-out outcomes | high |
| D11 | within-pass samples counted as independent | medium |
| D12 | reference-dependent schedule boundary | high |

## Held-out mutations — frozen definitions

### HO1 — availability boundary equality
An item whose publication timestamp is **exactly equal** to the decision instant is
admitted. Injection: change the availability comparison from `<=` to `<`, or supply an
item with `published == t_decision` and accept it on the wrong side.
*Channel:* L1 availability, boundary arithmetic. *Existing candidate rule:* the
availability check — written for the strict-ordering case, never for equality.

### HO2 — provenance manifest omits a behaviour-changing input
A configuration value that changes pipeline behaviour (an environment variable, a
default argument) is not included in the provenance manifest, so two runs producing
different results carry identical hashes. Injection: read a behaviour-changing value
from the environment and omit it from the manifest.
*Channel:* L4 reproducibility. *Existing candidate rule:* none. `provenance_manifest`
records what it is given; nothing checks **completeness**.

### HO3 — statistical unit chosen at the wrong nesting level
Within-pass replicates are correctly aggregated, but the resulting passes are then
treated as independent although several share one held state. Injection: aggregate at
the pass level and compute intervals over passes while the true exchangeable unit is
the episode.
*Channel:* L4 independence. *Existing candidate rule:* `within_group_icc` operates at
whatever level it is given; nothing checks that the **chosen** level is the right one.

### HO4 — declared physics silently diverges from implementation
The configuration declares one generative relation while the code implements another
that agrees on the training range and diverges outside it. Injection: declare a linear
relation, implement linear-plus-small-quadratic.
*Channel:* L2 declared-equations-match-implementation. *Existing candidate rule:*
`functional_form_match` measures generator/learner matching, **not** config/code
agreement — a different proposition.

**Two of the four (HO2, HO3) have no existing detector at all.** They are the real test
of whether a general rule can be written that catches a defect it was not designed for.

---

## Evaluation matrix

`{CASE A, CASE B} × {12 development, 4 held-out} × {3 deterministic environments}`

Environments vary only reproducibility-relevant settings — RNG family, array dtype,
declared-config permutation — never a physical parameter.

## Metrics

defect-detection rate · held-out detection rate · clean-path false-positive rate ·
false-negative count · per-detector and total runtime · provenance completeness ·
determinism across repeated clean runs.

## Acceptance criteria

1. every high-severity development fault detected;
2. all four held-out mutations detected;
3. zero false positives on clean reference implementations;
4. identical verdicts across repeated clean runs;
5. runtime measured and reported as CI overhead;
6. every finding names a specific contract rule, never a bare assertion failure.

## Correction budget

A missed held-out mutation permits **one** improvement to the *general* contract rule,
followed by a rerun of the **entire** held-out set. Maximum two correction loops. Still
missed after two → **HOLD, do not draft the paper.** A mutation is never weakened.
