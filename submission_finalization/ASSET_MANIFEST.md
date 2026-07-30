# ASSET MANIFEST

Only these assets may support the paper. Verified present on
`paper/orbit-evidence-contract` and passing.

| asset | path | LOC | status |
|---|---|---|---|
| visible-pass scheduler | `src/orbit_evidence/pass_scheduler/visible_pass.py` | 212 | imported, tested |
| causal transmission registry (freeze-then-label) | `src/orbit_evidence/causal_registry/causal_registry.py` | 141 | imported, tested |
| reference-ensemble + uncertainty | `src/orbit_evidence/label_ensemble/reference_ensemble.py` | 114 | imported, tested |
| experiment-contract utilities | `src/orbit_evidence/experiment_contract/experiment_contract.py` | 299 | imported, tested |
| regression suite | `tests/regression/test_regressions.py` | 490 | **32 passed** |
| failure taxonomy | `docs/FAILURE_TAXONOMY.md` | 173 | 12 modes |
| provenance + seed control | inside `contract/experiment_contract.py` | — | `SeedRegistry`, `derive_seed`, `common_random_numbers`, `provenance_manifest` |
| invalid-result banlist | `archive/KNOWN_INVALID_RESULTS.md` | — | 6 banned results |

Toolkit total: **1,095 LOC** including tests. Dependencies: `numpy` only; the tests use
a dependency-free analytic propagator stand-in.

## Explicitly NOT available as evidence

The EXP16 generative simulator, the M0–M7 model pipeline, every gate performance
figure, every manuscript figure, and every numerical constant presented as validated.
The retired manuscript may be consulted for **domain motivation and notation only**.


> **Line counts and the test count are authoritative only in `evaluation/results/final_summary.json`** (`source_loc`, `test_suite_loc`, `test_count`). The figures in the table above were hand-copied and had drifted by up to 91 lines; regenerate with `make matrix` and read them there rather than here.
