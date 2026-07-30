# BUILD LOG

| when | action | pages | errors | undef refs | undef cites | overfull | banlist |
|---|---|---|---|---|---|---|---|
| after restructure into paper/ | `make -C paper verify` | 6 | 0 | 0 | 0 | 0 | clean (6 files) |
| after LOC/runtime correction | `make -C paper verify` | 6 | 0 | 0 | 0 | 0 | clean |
| after Fig. 1 contradiction fix | `make -C paper verify` | 6 | 0 | 0 | 0 | 0 | clean |

Canonical build, from repository root:

```bash
make -C paper clean && make -C paper && make -C paper verify
```

`verify` reads `paper/build/icc_main.log` and fails unless pages == 6 and every error
count is zero. The PDF target has `scripts/check_banlist.py` as a hard prerequisite, so a
build cannot succeed while a prohibited claim is present in any source file.

## Test and evaluation state at each build

```
PYTHONPATH=src pytest tests/regression tests/fault_injection -q   -> 27 passed
python evaluation/scripts/run_matrix.py                          -> VERDICT: PASS
```

Matrix: development detection 42/42, held-out 12/12, clean-path false positives 0,
verdicts identical across three environments, sweep under 0.2 s.
