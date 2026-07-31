# Reproducibility

## Full reproduction from a clean checkout

One command, from the repository root:

```bash
pip install -e '.[test]'    # numpy + pytest; numpy is the only runtime dependency
make gate                   # tests, fault matrix, claim gate, six-page paper build
```

`make gate` runs in this order — evidence first, then the claims that quote it, then the
document:

| step | what it does |
|---|---|
| `make test` | 30 tests: `tests/regression` (two-sided, one per historical defect) + `tests/fault_injection` |
| `make matrix` | re-runs the 17-class fault matrix, regenerates `evaluation/results/final_summary.json`, `EVALUATION_RESULT.md` and `fig2_data.json` |
| `make claims` | banned invalid results, withdrawn claims, and every headline number checked against the summary artifact |
| `make verify` | builds `paper/icc_main.pdf` and asserts 6 pages, 0 errors, 0 undefined refs/cites, 0 overfull boxes |

To check repeatability rather than just success:

```bash
make gate-twice             # runs the gate twice, asserts the summary artifact reproduces
```

Requires a TeX distribution with `latexmk` and `IEEEtran` for the paper build. No network
access and no external data at any step.

## Where the numbers come from

`evaluation/results/final_summary.json` is the single source of truth. It is a pure function
of the committed matrix artifact plus the source tree, and `make claims` fails the build if
the manuscript quotes a value it does not contain. `EVALUATION_RESULT.md` and `fig2_data.json`
are generated from it and must not be hand-edited — the hand-maintained version of the former
had silently drifted to claiming 14 development faults, 57 rows and 0.187 s long after all
three had changed.

## Determinism, and the one thing that is not deterministic

Every seed is derived by SHA-256 from a declared string, so results reproduce without storing
random state. The evaluation runs three environments differing only in pseudo-random generator
family (PCG64, SFC64, Philox) and asserts identical clean-path verdicts across all three.

**Runtime is the only quantity that does not reproduce bit-for-bit.** Observed 1.39–1.55 s for
the full sweep on a commodity laptop (≈26–29 ms per condition), dominated by L4.7's
400-permutation null. The manuscript therefore states a *bound* — under 3 s — and `make claims`
asserts the artifact still satisfies that bound rather than matching a string. `make gate-twice`
prints the volatile fields explicitly instead of hiding them; `scripts/compare_summaries.py`
records exactly which fields are excluded and why.

## Ignored artifacts and how to regenerate them

Broad ignores of `*.json`, `*.csv` and `*.npz` are deliberately **not** used, because several
such files are scientific artifacts that must stay tracked. Only the following are ignored,
each regenerable:

| ignored path | what it is | regenerate with |
|---|---|---|
| `paper/build/` | LaTeX intermediates | `make paper` |
| `**/__pycache__/`, `*.pyc` | Python bytecode | automatic |
| `.pytest_cache/` | pytest state | automatic |
| `tmp/`, `outputs/`, `build/`, `logs/`, `local_archive/`, `dataraw/`, `hardware/`, `validation_runs/` | scratch from the stopped programme; **no tracked files** | not needed by the active paper |
| `archive/stopped_research/experiments/exp15_causal_recovery/causal_dataset/` | derived arrays, ~10 MB | archived; not used by the active paper |
| `archive/stopped_research/experiments/exp15_visible_causal/{registry,labels}/` | derived arrays, ~50 MB | archived; not used by the active paper |

The archived entries belong to the stopped research programme. They are regenerable, not
required by the active paper, and their scientific status is governed by
`archive/KNOWN_INVALID_RESULTS.md`.

## Tracked artifacts that are NOT regenerable in place

| path | why it is tracked |
|---|---|
| `evaluation/results/matrix_result.json` | the paper's evidence. Re-running overwrites it, so the committed copy is the citable record; `tests/fault_injection/test_matrix.py` asserts a re-run reproduces its verdict and detection counts |
| `evaluation/results/matrix_result_prefix_fixture.json` | the pre-fix run, retained so the fixture-repair sequence is auditable rather than asserted |
| `evaluation/mutations/PREREGISTRATION.md` | a pre-registration is worthless if revised after its outcomes are known. Not edited; a withdrawal notice bounds it instead |
| `archive/**` | provenance for a stopped programme; never regenerated |

## Test layout

The active suite is exactly `tests/regression` and `tests/fault_injection`, with the two
pipelines and fault injectors in `tests/fixtures`. `testpaths` in `pyproject.toml` names them,
so a bare `pytest` collects the right thing. Legacy tests from the stopped programme (which
import `torch` and other dependencies the active artifact does not use) live under
`archive/stopped_research/tests/` and are not collected.
