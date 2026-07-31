# Curated fault-injection regression evaluation -- result

GENERATED FILE. Do not edit by hand; run `make matrix`.
Source: `evaluation/results/matrix_result.json` -> `final_summary.json`.

**VERDICT: PASS** -- every pre-registered acceptance criterion met.

## Scope of the claim

This suite measures **represented-fault regression coverage**: the implemented rules catch
the violations the suite contains, and those violations cannot silently return. It does
**not** estimate sensitivity to faults the suite does not contain, and no generalisation
claim is made -- see the withdrawal notice in `../mutations/PREREGISTRATION.md`.

## Matrix

`{CASE A, CASE B} x {clean, 17 curated fault classes} x 3 deterministic environments`
= **54 rows** (18 conditions x 3 environments; both cases run per row).
Environments vary RNG family only -- PCG64, SFC64, Philox -- never a physical parameter,
so they are not independent systems or populations.

## Metrics

| metric | value |
|---|---|
| contract rules | 19 |
| curated fault classes | 17 |
| injected fault-environment cells | 51 |
| contract detection | **17/17** |
| chronological baseline detection | **2/17** (checks B1, B2, B3) |
| clean reference paths | 3 |
| clean-path rule firings | **0** |
| clean verdicts identical across environments | **True** |
| rules with a demonstrated red fixture | **16/19** |
| rules with no red fixture | L2.2, L2.3, L4.5 |
| total runtime | 1.592 s (claim: under 2 s) |
| per-condition runtime | 29.5 ms |
| toolkit source lines | 833 |
| test suite lines | 988 |

## L4.7 size control

The statistical-unit rule is referenced to a permutation null, so its specificity is a
measured **rate**, not a single clean run:

| quantity | value |
|---|---|
| nominal alpha | 0.05 |
| clean paths evaluated | 450 (150 seeds x 3 envs) |
| **measured clean false-halt rate** | **0.031** |
| injected detection rate | 1.0 over 150 paths |

Reproduce with `python evaluation/scripts/calibrate_l47.py`.

## Acceptance criteria

| criterion | result |
|---|---|
| 1_all_high_severity_detected | **PASS** |
| 2_all_late_specified_detected | **PASS** |
| 3_zero_clean_false_positives | **PASS** |
| 4_identical_clean_verdicts | **PASS** |
| 5_runtime_measured | **PASS** |
| 6_findings_name_a_rule | **PASS** |
