# Development

## Layout

```
paper/          active manuscript, figures, table, build system
src/            orbit_evidence: the contract implementation
tests/          regression (detectors), fault_injection (matrix), fixtures (pipelines)
evaluation/     the fault-injection evaluation and its committed results
docs/           methodology notes and this file
archive/        a stopped research programme, provenance only
```

## The one rule for adding a detector

Every detector must be **two-sided**: a clean-path test that passes and a deliberately
broken fixture that fails, with an error message naming the contract rule. A detector
without a failing fixture is not accepted, because three checks in the predecessor work
were later found incapable of failing — one compared two arrays built from the same
object, one pinned the very parameter whose influence it tested, and one attached no
threshold to the quantity it reported.

Concretely, when adding a rule:

1. register it in `evaluation/scripts/contract_layers.py` with a rule ID, protected
   object, statement and failure action;
2. raise `ContractViolation(rule_id, detail)` — never a bare `assert`;
3. add a fault to `tests/fixtures/pipelines.py` that triggers it;
4. add the expected mapping to `EXPECTED` in `evaluation/scripts/run_matrix.py`;
5. add a two-sided test in `tests/regression/`.

## Before committing

```bash
PYTHONPATH=src pytest tests/regression tests/fault_injection -q
python evaluation/scripts/run_matrix.py
make -C paper verify
```

All three must pass. The paper build additionally refuses to run while a prohibited claim
is present in any source file.

> **Note on the test path.** The repository root `tests/` also holds legacy tests from
> unrelated earlier work streams (they import `torch` and other dependencies this paper does
> not use). The active suite is exactly `tests/regression` and `tests/fault_injection`; the
> commands above name them explicitly rather than relying on `tests/` collecting cleanly.
