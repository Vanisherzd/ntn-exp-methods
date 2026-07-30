# Artifacts

## What a reviewer needs

```
src/orbit_evidence/          the contract implementation (4 modules, 833 lines)
tests/regression/            two-sided detector tests, one per historical defect
tests/fault_injection/       tests asserting the committed matrix reproduces
tests/fixtures/              the two pipelines and the 17 fault injectors
evaluation/scripts/          contract layers (19 rules), baseline, matrix runner
evaluation/mutations/        the fault pre-registration, with its withdrawal notice
evaluation/results/          final_summary.json, the matrix result, its pre-fix predecessor
paper/                       manuscript, figures, table, build system
```

## Reproduce everything

```bash
pip install -e '.[test]'    # numpy + pytest; numpy is the only runtime dependency
make gate                   # tests, fault matrix, claim gate, six-page paper build
make gate-twice             # runs the gate twice and asserts the summary reproduces
```

Counts are deliberately not repeated in this file. `evaluation/results/final_summary.json`
is the single source of truth, `paper/submission/CLAIMS.md` maps each claim to its artifact
field and regeneration command, and `paper/scripts/check_banlist.py` fails the build if the
manuscript or this submission package quotes a value the artifact does not contain. This
file previously carried hand-copied test counts and went stale; it now states none.

No network access, no external data, no proprietary inputs. The pass scheduler is exercised
through a dependency-free analytic propagator, so no orbital-propagation library is required
to run the tests.

## Relationship between the fixtures and the case studies

`tests/fixtures/pipelines.py` defines CASE A and CASE B. These are **not** independent of
the case studies in the manuscript: the fixtures were modelled on the two pipelines the case
studies describe, and the fault classes were derived from the defects found in them. The
case studies are retrospective accounts, recorded in `docs/CASE_STUDIES.md`; they are not
executed runs and produce no artifact. The coverage matrix and the case studies therefore
share an origin and must not be read as two independent lines of evidence.

## Injection level — read this before interpreting 17/17

The fixtures are **check-scoped by construction**: each contract rule receives its own
pre-shaped input attribute (`feature_fn`, `admit_fn`, `control_rates`,
`declared`/`implemented`, `unit_ids`/`coarser_ids`, and so on). Only six of the seventeen
mutated objects reach more than one consumer — the schedule, closure and fold arrays also
feed the chronological baseline, and `run_fn` feeds both L3.1 and L3.2.

Consequently 17/17 is **represented-fault regression coverage**: it establishes that these
violations cannot silently return, and for most classes it does *not* establish that the
rule would catch the defect inside a working pipeline. The manuscript states this in its
threats section. Do not read the ratio as a detection probability.

## Not part of the active artifact

`archive/` holds a stopped research programme, retained for provenance only. Nothing under
`archive/` is read by the build or by any test, and `archive/KNOWN_INVALID_RESULTS.md` lists
the results that may never be cited.
