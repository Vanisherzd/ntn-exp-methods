# Artifacts

## What a reviewer needs

```
src/orbit_evidence/          the contract implementation (4 modules)
tests/regression/            23 two-sided detector tests
tests/fault_injection/       4 tests asserting the matrix reproduces
tests/fixtures/              the two case-study pipelines and fault injectors
evaluation/scripts/          contract layers (19 rules) and the matrix runner
evaluation/mutations/        the frozen fault pre-registration
evaluation/results/          the committed matrix result and its pre-fix predecessor
paper/                       manuscript, figures, table, build system
```

## Reproduce everything

```bash
pip install numpy pytest
PYTHONPATH=src pytest tests -q                     # 27 tests
python evaluation/scripts/run_matrix.py            # regenerates the matrix result
make -C paper verify                               # builds and asserts 6 pages
```

No network access, no external data, no proprietary inputs. The pass scheduler is
exercised through a dependency-free analytic propagator, so no orbital-propagation
library is required to run the tests.

## Not part of the active artifact

`archive/` holds a stopped research programme, retained for provenance only. Nothing
under `archive/` is read by the build or by any test, and
`archive/KNOWN_INVALID_RESULTS.md` lists the results that may never be cited.
