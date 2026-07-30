# Fault-injection evaluation

Tests the *contract*, not any model's performance.

```
scripts/contract_layers.py   19 rules in four layers; every violation carries a rule ID
scripts/run_matrix.py        runs {2 pipelines} x {19 conditions} x {3 environments}
mutations/PREREGISTRATION.md the frozen fault definitions, written before the detectors
results/matrix_result.json   the committed result
results/matrix_result_prefix_fixture.json   the pre-fix run, retained for audit
results/EVALUATION_RESULT.md the human-readable summary
results/fig2_data.json       coverage data behind Fig. 2

The three environments are defined in `scripts/../../tests/fixtures/pipelines.py`
(`ENVS`) and differ only in pseudo-random generator family: PCG64, SFC64, Philox.
```

## Run

```bash
python evaluation/scripts/run_matrix.py
```

Exits non-zero if any acceptance criterion fails. The same criteria are asserted from
CI by `tests/fault_injection/test_matrix.py`.

## The one thing to read first

`mutations/PREREGISTRATION.md` records why three of the four originally suggested
held-out mutations were **reclassified as development faults**: detectors already existed
for those exact channels, so injecting them would have produced a meaningless 4/4
held-out rate. The four that replaced them include two propositions for which no detector
existed at all.
