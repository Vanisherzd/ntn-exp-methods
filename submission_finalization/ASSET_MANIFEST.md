# ASSET MANIFEST

Only these assets may support the paper. Verified present on
`paper/orbit-evidence-contract` and passing.

| asset | path | LOC | status |
|---|---|---|---|
| visible-pass scheduler | `salvage/orbit-evidence-toolkit/scheduler/visible_pass.py` | 183 | imported, tested |
| causal transmission registry (freeze-then-label) | `salvage/orbit-evidence-toolkit/registry/causal_registry.py` | 141 | imported, tested |
| reference-ensemble + uncertainty | `salvage/orbit-evidence-toolkit/ensemble/reference_ensemble.py` | ~135 | imported, tested |
| experiment-contract utilities | `salvage/orbit-evidence-toolkit/contract/experiment_contract.py` | ~237 | imported, tested |
| regression suite | `salvage/orbit-evidence-toolkit/tests/test_regressions.py` | 399 | **23 passed, 0.14 s** |
| failure taxonomy | `docs/FAILURE_TAXONOMY.md` | 173 | 12 modes |
| provenance + seed control | inside `contract/experiment_contract.py` | — | `SeedRegistry`, `derive_seed`, `common_random_numbers`, `provenance_manifest` |
| invalid-result banlist | `archive/KNOWN_INVALID_RESULTS.md` | — | 6 banned results |

Toolkit total: **1,095 LOC** including tests. Dependencies: `numpy` only; the tests use
a dependency-free analytic propagator stand-in.

## Explicitly NOT available as evidence

The EXP16 generative simulator, the M0–M7 model pipeline, every gate performance
figure, every manuscript figure, and every numerical constant presented as validated.
The retired manuscript may be consulted for **domain motivation and notation only**.
