# Fault-injection evaluation

Tests the *contract*, not any model's performance.

```
scripts/contract_layers.py   19 rules in four layers; every violation carries a rule ID
scripts/chronological_baseline.py  the baseline protocol property, implemented and run
scripts/run_matrix.py        runs {2 pipelines} x {18 conditions} x {3 environments}
mutations/PREREGISTRATION.md the frozen fault definitions, written before the detectors
results/matrix_result.json   the committed result
results/matrix_result_prefix_fixture.json   the pre-fix run, retained for audit
results/EVALUATION_RESULT.md the human-readable summary
results/fig2_data.json       coverage data behind Fig. 2

The three environments are defined in `tests/fixtures/pipelines.py`
(`ENVS`) and differ only in pseudo-random generator family: PCG64, SFC64, Philox.
```

## Run

```bash
python evaluation/scripts/run_matrix.py
```

Exits non-zero if any acceptance criterion fails. The same criteria are asserted from
CI by `tests/fault_injection/test_matrix.py`.

## The one thing to read first

`mutations/PREREGISTRATION.md` opens with a **withdrawal notice**. That document
pre-registered four mutations as held-out evidence of generalisation; adversarial review
established the claim does not hold, and it has been withdrawn. What this suite measures
is **represented-fault regression coverage** — the implemented rules catch the violations
the suite contains, and those violations cannot silently return. It does not estimate
sensitivity to faults the suite does not contain.

Consequences worth knowing before reading any number here:

- The 17/17 detection figure has a **curated** denominator, not a sample from a natural
  fault distribution. It is a regression result, not a sensitivity.
- The faults and the rules share an author, so for most classes the figure measures
  detector *reachability*.
- `DEV_FAULTS` vs `LATE_SPECIFIED` in `tests/fixtures/pipelines.py` is **provenance only**
  and carries no evidential weight.
