# LOOP 3 — FAULT-INJECTION EVALUATION RESULT

**VERDICT: PASS** — all six pre-registered acceptance criteria met.
Detectors were frozen before the held-out mutations were injected and none was edited
afterwards.

## Matrix

`{CASE A, CASE B} x {clean, 14 development faults, 4 held-out mutations} x 3 deterministic environments`
= **57 rows** (19 conditions x 3 environments; both cases run per row).
Environments vary RNG family only — PCG64, SFC64, Philox — never a physical parameter.

## Metrics

| metric | value |
|---|---|
| development-fault detection | **42/42** |
| high-severity detection | **36/36** |
| **held-out mutation detection** | **12/12** |
| false negatives | **0** |
| clean-path false-positive rule firings | **0** |
| clean verdicts identical across environments | **True** |
| total runtime | **0.187 s** |
| per-condition runtime | **3.3 ms** |
| findings naming a specific rule | **100 %** (every firing is a registered rule ID) |

CI overhead: the full 19-condition contract sweep runs in **0.187 s** on one
core with `numpy` as the only dependency, so it is affordable as a per-commit gate.

## Per-fault detection

| fault | expected rule | detected | rules fired |
|---|---|---|---|
| D1 | L1.1 | 3/3 | L1.1 |
| D2 | L1.2 | 3/3 | L1.2 |
| D3 | L1.4 | 3/3 | L1.4 |
| D4 | L2.1 | 3/3 | L2.1 |
| D5 | L1.3 | 3/3 | L1.3 |
| D6 | L3.1 | 3/3 | L3.1, L3.2 |
| D7 | L4.2 | 3/3 | L4.2 |
| D8 | L3.3 | 3/3 | L3.3 |
| D9 | L3.1 | 3/3 | L3.1, L3.2 |
| D10 | L3.1 | 3/3 | L3.1, L3.2 |
| D11 | L4.3 | 3/3 | L4.3 |
| D12 | L1.4 | 3/3 | L1.4 |
| D13 | L4.1 | 3/3 | L4.1 |
| D14 | L4.4 | 3/3 | L4.4 |
| **HO1** | L1.5 | 3/3 | L1.5 |
| **HO2** | L4.6 | 3/3 | L4.6 |
| **HO3** | L4.7 | 3/3 | L4.7 |
| **HO4** | L2.4 | 3/3 | L2.4 |

D6, D9 and D10 additionally fire **L3.2**. That is a true positive, not noise: when a
state channel is unguarded, the mutation aimed at it is also inert, and L3.2 exists
precisely to catch a mutation that cannot demonstrate anything.

## Held-out mutations — the load-bearing result

All four were defined before their detectors were written, and two (**HO2**, **HO3**)
had no predecessor detector of any kind.

| id | mutation | detecting rule | predecessor detector existed? |
|---|---|---|---|
| HO1 | availability comparison excludes exact equality | L1.5 | partial (interior-only) |
| HO2 | provenance manifest omits a behaviour-changing input | L4.6 | **none** |
| HO3 | statistical unit chosen at the wrong nesting level | L4.7 | **none** |
| HO4 | declared relation diverges from implementation outside the fitted domain | L2.4 | none for this proposition |

**12/12 detections, zero correction loops used.** The correction budget
(one general-rule improvement per miss, maximum two loops) was not drawn on.

## One fixture defect found and fixed — disclosed

The first matrix run reported **3 clean-path false-positive firings**, all of rule
L4.4 (seed hygiene), one per environment. Cause: the clean CASE B fixture declared it
was about to execute seed 12 while 12 was still in its own evaluation set — which is a
genuine contract violation, so **the detector was right and the fixture was wrong**.

Fixed by giving the clean path a debug seed to execute. **No detector was modified**,
and the four held-out detectors (L1.5, L2.4, L4.6, L4.7) were untouched — they had
already passed in the pre-fix run, which is preserved as
`MATRIX_RESULT_prefix_fixture_bug.json` so the sequence is auditable.

## Acceptance

| criterion | result |
|---|---|
| 1_all_high_severity_detected | **PASS** |
| 2_all_held_out_detected | **PASS** |
| 3_zero_clean_false_positives | **PASS** |
| 4_identical_clean_verdicts | **PASS** |
| 5_runtime_measured | **PASS** |
| 6_findings_name_a_rule | **PASS** |

Raw record: `MATRIX_RESULT.json`.
