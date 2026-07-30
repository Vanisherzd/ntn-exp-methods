# Reproducibility

## Full reproduction from a clean checkout

```bash
pip install numpy pytest
PYTHONPATH=src pytest tests/regression tests/fault_injection -q   # 23 regression + 4 fault-injection
python evaluation/scripts/run_matrix.py         # regenerates evaluation/results/matrix_result.json
make -C paper verify                            # builds paper/icc_main.pdf and asserts 6 pages
```

Requires `numpy`, `pytest`, and a TeX distribution with `latexmk` and `IEEEtran`. No
network access, no external data.

## Determinism

Every seed is derived by SHA-256 from a declared string, so results are reproducible
without storing random state. The evaluation runs three environments differing only in
pseudo-random generator family (PCG64, SFC64, Philox) and asserts identical clean-path
verdicts across all three.

Runtime is the one quantity that varies between runs (observed 0.16–0.19 s for the full
sweep on a commodity laptop). The manuscript therefore states a bound rather than a point
value.

## Ignored artifacts and how to regenerate them

Broad ignores of `*.json`, `*.csv` and `*.npz` are deliberately **not** used, because
several such files are scientific artifacts that must stay tracked. Only the following
are ignored, each regenerable:

| ignored path | what it is | regenerate with |
|---|---|---|
| `paper/build/` | LaTeX intermediates | `make -C paper` |
| `**/__pycache__/`, `*.pyc` | Python bytecode | automatic |
| `.pytest_cache/` | pytest state | automatic |
| `experiments/exp15_causal_recovery/causal_dataset/` | derived arrays from the stopped line, ~10 MB | `python experiments/exp15_causal_recovery/build_causal_dataset.py` (archived; not used by the active paper) |
| `experiments/exp15_visible_causal/{registry,labels}/` | derived arrays from the stopped line, ~50 MB | `python experiments/exp15_visible_causal/build_visible_registry.py` (archived; not used by the active paper) |

The two `experiments/` entries belong to the stopped research programme. They are
regenerable, not required by the active paper, and their scientific status is governed by
`archive/KNOWN_INVALID_RESULTS.md`.

## Tracked artifacts that are NOT regenerable in place

| path | why it is tracked |
|---|---|
| `evaluation/results/matrix_result.json` | the paper's evidence; regenerating overwrites it, so the committed copy is the citable record |
| `evaluation/results/matrix_result_prefix_fixture.json` | the pre-fix run, retained so the fixture-repair sequence is auditable rather than asserted |
| `archive/**` | provenance for a stopped programme; never regenerated |

> **Note on the test path.** The repository root `tests/` also holds legacy tests from
> unrelated earlier work streams (they import `torch` and other dependencies this paper does
> not use). The active suite is exactly `tests/regression` and `tests/fault_injection`; the
> commands above name them explicitly rather than relying on `tests/` collecting cleanly.
