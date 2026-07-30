# Claims and their evidence

Every headline number with its artifact and the command that regenerates it.

**Single source of truth:** `evaluation/results/final_summary.json`. Every number in the
manuscript is generated from that file, and `paper/scripts/check_banlist.py` fails the
build if the manuscript quotes a value the artifact does not contain. Regenerate with:

```
make matrix      # re-runs the suite and rewrites the summary artifact
make gate        # tests + matrix + claim gate + six-page paper build
make gate-twice  # runs the gate twice and asserts the summary reproduces
```

| claim | value | artifact field | regenerate with |
|---|---|---|---|
| contract rules | 19 across four layers | `rule_count` | `make matrix` |
| curated fault classes | 17 | `fault_class_count` | `make matrix` |
| deterministic environments | 3 (PCG64, SFC64, Philox) | `environment_count` | `make matrix` |
| conditions per environment | 18 = 17 faults + 1 clean path | `conditions_per_environment` | `make matrix` |
| injected fault-environment cells | 51 | `injected_cell_count` | `make matrix` |
| clean reference paths | 3, reported separately | `clean_path_count` | `make matrix` |
| chronological baseline coverage | 2/17 (**measured**, not asserted) | `chronological_detected_count` | `make matrix` |
| contract coverage | 17/17, identical in all 3 environments | `contract_detected_count` | `make matrix` |
| clean-path rule firings | 0 | `clean_false_halt_count` | `make matrix` |
| L4.7 clean false-halt rate | **0.042 over 450 clean paths** (nominal α = 0.05) | `l47_calibration` | `python evaluation/scripts/calibrate_l47.py` |
| L4.7 injected detection | 150/150 | `l47_calibration` | as above |
| rules with a demonstrated red fixture | 16 of 19 | `detectors_with_red_fixture` | `make matrix` |
| rules with no red fixture | L2.2, L2.3, L4.5 | `detectors_without_red_fixture` | `make matrix` |
| sweep runtime | **under 2 s** (bound); ≈30 ms per condition | `runtime_seconds` | `make matrix` |
| toolkit size | 833 lines across four modules | `source_loc` | `make matrix` |
| test suite size | 655 lines (regression + fault injection) | `test_suite_loc` | `make matrix` |
| tests | 32 passing | `test_count` | `make test` |

Runtime is the one figure that does **not** reproduce bit-for-bit: it varies by a few
percent between runs and machines. The manuscript therefore states a *bound* (under 2 s),
and the claim gate asserts the artifact still satisfies that bound rather than matching a
string. `make gate-twice` reports the volatile fields explicitly instead of hiding them.

## Distinctions the paper must not blur

**19 rules is not 17 fault classes.** Rules are contract obligations; fault classes are
injected defects. Several faults map to one rule (three state-channel faults all violate
L3.1), and some rules are the target of no injected fault at all.

**18 conditions is not 19 rules.** A condition is one run configuration: 17 fault classes
plus one clean path, per environment.

**"17/17" is regression coverage, not sensitivity.** The denominator is a curated suite,
not a sample from a natural fault distribution. The number says these violations cannot
silently return; it does not estimate the probability of catching a defect nobody
anticipated. See the threats section of the manuscript.

**The initial L4.4 firing was not a detector false positive.** The first matrix run fired
L4.4 on the clean rows because the clean fixture declared it was about to execute a seed
still present in its own evaluation namespace, which is a genuine violation. The detector
was correct; the fixture was not a clean path. The fixture was repaired, no detector was
changed, and both records are retained
(`evaluation/results/matrix_result_prefix_fixture.json`).

**The generalisation claim is withdrawn.** An earlier version reported four "held-out
mutations" as evidence that the contract detects faults it was not designed against.
Review established that this does not hold: two of the four mutate an object consumed only
by their own detector, and a third had its detector rewritten after its outcome was
recorded. One case remains, which supports nothing general. The claim was withdrawn by
author decision; the wording is banned from the manuscript by
`paper/scripts/check_banlist.py` (`WITHDRAWN_CLAIMS`), and the reasoning is recorded in
`evaluation/mutations/PREREGISTRATION.md` and `submission_finalization/CLAIM_LEDGER.md`.
The development / late-specified split survives in the code as **provenance only** and
carries no evidential weight.
