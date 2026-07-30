# KNOWN INVALID RESULTS — DO NOT CITE

**Machine-discoverable notice. Every archived experiment README links here.**

The results listed below are **permanently invalid as scientific evidence**. They
must never be cited, quoted, plotted, carried into a manuscript, or used to justify
a design decision. Each entry records where it came from, what defect invalidated
it, whether a valid replacement exists, and — critically — whether formal blind
seeds were ever run.

Two research lines are permanently stopped: the **real-TLE archive route** and the
**EXP16 controlled software benchmark**. No result from either is usable.

---

## 1. IRIDIUM-181 @ 8 h: "+1.94 % held-out improvement, 3.26 mHz"

| field | value |
|---|---|
| originating artifact | `experiments/exp14_multisat_generalization_matrix/` phase-2/3 outputs; the frozen manuscript's headline result |
| invalidating defect | The feature `t_gap_s` — the stale-to-reference **element epoch gap** — is fixed by the *future* reference element's publication and is not computable at the transmission epoch. Two of three learned candidates consumed it. |
| evidence | `loop_engineering/evidence/T1_reference_epoch_perturbation.py`: holding stale element, transmission UTC, ground station and carrier fixed and swapping only the reference changed exactly feature index 1, on 9/9 satellites |
| replacement status | **NONE.** The deployable rerun gave **−0.702 %** held-out at the same cell (SGP4 0.16740 Hz vs learned 0.16857 Hz), win rate 0.450, Holm p = 1.000, bootstrap CI on the wrong side |
| formal blind seeds run? | not applicable (real data); the deployable rerun was executed and reported |

## 2. "0 / 54 primary cells preserved" and the deployable-rerun cell statistics

| field | value |
|---|---|
| originating artifact | `archive/real_tle_causality_audit/audits/E4_walk_forward_r1500.json`, `S2_analysis_r1500.json` |
| invalidating defect | Computed on a dataset in which **96.58 % of transmissions placed the satellite below the endpoint horizon** (median elevation −42.5°); only 1.45 % were above 10°. On visible geometry the residual is 5.6× larger. |
| additional defects | row membership depended on the future catalogue; single-reference label uncertainty exceeded the label in 51.8 % of visible probes |
| replacement status | **NONE.** The visible-pass rebuild that fixed all three failed its label-censoring gate (max \|SMD\| 1.307/1.552 against a 0.10 limit) and **no model was ever fitted to it** |
| formal blind seeds run? | not applicable |

## 3. "1 / 270 screening opening" (IRIDIUM-177 @ 168 h @ 150 Hz)

| field | value |
|---|---|
| originating artifact | `archive/real_tle_causality_audit/audits/` phase-2 screening sweep |
| invalidating defect | Same below-horizon and future-dependent-membership defects as item 2. Independently, the 168 h staleness band is unreachable under any realistic provisioning policy — it existed only because the old pairing rule matched elements 168 h apart while ignoring every element published in between. Under 24 h provisioning the band holds 71 rows from 1 satellite; **3 of them are above the visibility mask in the entire dataset.** |
| replacement status | **NONE** |
| formal blind seeds run? | not applicable |

## 4. All EXP16 qualification-probe outcome rates

| field | value |
|---|---|
| originating artifact | `experiments/exp16_controlled_gate/PROBE_RESULT.json` |
| invalidating defect | The probe's own **negative control failed**: with the injected error set to exactly zero, the gate opened in **1.00 of runs in all nine cells** and the corrector cut MAE by 57–93 %. Root cause: `held_element()` froze the truth's secular mean motion at the element epoch, leaving a deterministic `ndot·age` mismatch that survives Δ = 0 and is trivially learnable. The residual also breached the pre-registered 2 % physical ceiling (max **7.909 %**). |
| specifically invalid | the 264 helpful / 60 harmful realization counts; the 0.42 harm rates; the 0.58–1.00 gate-open rates; all B/A and val_ratio figures; the "33 % / 48 % harm prevented" figures from the reviewer's emulation |
| replacement status | **NONE.** No simulator repair is authorized |
| formal blind seeds run? | **NO. `EVALUATION_SEEDS_V2` (216 values) were never executed.** Asserted mechanically at probe start; verified again in this archive pass |

## 5. Endpoint-budget conclusions (guard time, energy per success, outage)

| field | value |
|---|---|
| originating artifact | manuscript §endpoint-value proxy; `g = 2·p99(\|e\|)`, `ρ = Pr(\|e\|>F_tol)`, `P_f`, `S`, `E_succ` |
| invalidating defect | Every input is a residual statistic from item 2's dataset, so all propagate the below-horizon defect. Independently, the 500 Hz tolerance was a **representative figure, never a standard requirement**, and no PHY simulation was ever run to connect residual frequency error to packet success. |
| replacement status | **NONE.** The LR-FHSS PHY simulator was never authorized or built |
| formal blind seeds run? | not applicable |

## 6. "The Evidence Gate has been validated for deployable Doppler correction"

| field | value |
|---|---|
| originating artifact | manuscript abstract, introduction and conclusion framing |
| invalidating defect | **The claim was never established at any point.** On real data no admissible causal corrector was ever found (0 of 279 walk-forward segments opened the gate). In software the benchmark built to test the mechanism failed its own qualification. The gate's *refusal* behaviour was never validated because the negative control was not null. |
| replacement status | **NONE.** No validated claim about the Evidence Gate exists |
| formal blind seeds run? | **NO** |

---

## What may legitimately be said

Only these, and only as internal research notes:

- Two independent reviewers confirmed that the *feature-level* causality fix in the
  visible-pass rebuild was sound: no reference-derived feature, verified by
  perturbation, and the old age-versus-gap affine dependence eliminated.
- The reference-ensemble label measurably reduced label ambiguity: the
  uncertainty ratio fell from 1.81 to 0.06–0.39 at the median.
- Inter-TLE residual labels are **missing-not-at-random with respect to TLE age**,
  because a publication outage simultaneously makes the held element stale and
  removes the later elements needed to label it. Measured \|SMD\| up to 1.35 on age;
  censored rows wait 4–13× longer for the next publication.
- Under realistic periodic provisioning, no staleness band beyond ~72 h is naturally
  reachable.

None of these is a validated performance result, and none supports a claim about the
Evidence Gate's deployed value.

## Reuse policy

Reusable *engineering* assets are extracted to `salvage/orbit-evidence-toolkit/`
with the numerical constants stripped. The defects above are encoded as regression
tests in `salvage/orbit-evidence-toolkit/tests/`, each of which genuinely fails
against the corresponding broken historical implementation.

See also `docs/FAILURE_TAXONOMY.md` and `docs/FUTURE_MEASUREMENT_PROTOCOL.md`.
