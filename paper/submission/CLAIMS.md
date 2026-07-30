# Claims and their evidence

Every headline number with its artifact, the script that produces it, and how to
reproduce it. Recomputed after the repository restructure.

| claim | value | artifact | regenerate with |
|---|---|---|---|
| fault classes | 17 (13 development + 4 withheld; only 1 supports generalisation, see threats) | `evaluation/results/matrix_result.json` | `python evaluation/scripts/run_matrix.py` |
| contract rules | 19 across four layers | `evaluation/scripts/contract_layers.py` (`RULES`) | `python -c "import contract_layers as C; print(len(C.RULES))"` |
| conditions per environment | 18 = 17 faults + 1 clean path | same artifact, `n_rows / 3` | as above |
| deterministic environments | 3 (PCG64, SFC64, Philox) | same artifact, `environments` | as above |
| development detection | 39/39 | same artifact | as above |
| withheld detection | 12/12 (4 mutations x 3 environments); generalisation evidence n=1 | same artifact | as above |
| fault-environment cells | 51/51 | 17 x 3 | as above |
| clean-path false halts | 0 at the committed seed; **0.042 over 450 clean paths** (nominal 0.05) | same artifact | as above |
| chronological baseline coverage | 2/17 (**measured**) | `evaluation/results/matrix_result.json` -> `chronological_baseline`; `evaluation/results/fig2_data.json` | `python evaluation/scripts/run_matrix.py` |
| sweep runtime | under 2 s, about 28 ms per condition (1.461 s measured) | same artifact, `total_runtime_s` | as above |
| toolkit size | 739 lines in four modules + 399-line test suite | `src/orbit_evidence/`, `tests/regression/` | `find src/orbit_evidence -name '*.py' \| xargs wc -l` (710 total incl. five `__init__.py`; 696 excl.) |
| regression tests | 23 passing | `tests/regression/` | `PYTHONPATH=src pytest tests/regression -q` |
| fault-injection tests | 4 passing | `tests/fault_injection/` | `PYTHONPATH=src pytest tests/fault_injection -q` |

## Distinctions the paper must not blur

**19 rules is not 18 fault classes.** Rules are contract obligations; fault classes are
injected defects. Several faults map to one rule (three state-channel faults all violate
L3.1), and some rules were never the target of an injected fault.

**Nineteen conditions is not nineteen rules.** A condition is one run configuration:
eighteen fault classes plus one clean path, per environment.

**The initial L4.4 firing was not a detector false positive.** The first matrix run fired
L4.4 on the clean rows because the clean fixture declared it was about to execute a seed
still present in its own evaluation namespace, which is a genuine violation. The detector
was correct; the fixture was not a clean path. The fixture was repaired, no detector was
changed, and both records are retained
(`evaluation/results/matrix_result_prefix_fixture.json`).

**Held out means held out from the detector, not from the paper.** Each of HO1–HO4 was
defined in `evaluation/mutations/PREREGISTRATION.md` before the corresponding rule was
written, and no rule was edited after its held-out outcome was inspected. HO2 and HO3 had
no predecessor detector of any kind.
