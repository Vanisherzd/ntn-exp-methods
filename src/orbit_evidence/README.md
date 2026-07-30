# orbit-evidence-toolkit

Engineering assets salvaged from a stopped research line. **No scientific result from
that line is valid** — see [`../../archive/KNOWN_INVALID_RESULTS.md`](../../archive/KNOWN_INVALID_RESULTS.md).

What is here is the machinery, with every numerical constant stripped. What is *not*
here: the generative model, the model pipeline, any performance claim, any manuscript
figure, any constant presented as a validated value.

## Modules

| module | purpose |
|---|---|
| `scheduler/visible_pass.py` | event-driven pass discovery, bisected threshold crossings, fixed within-pass sampling, pass/tx identifiers, geodetic elevation |
| `registry/causal_registry.py` | rows created and hashed *before* labels exist; immutable identifiers; declared freeze window; future-truncation invariant |
| `ensemble/reference_ensemble.py` | deterministic canonicalisation, ensemble median, MAD uncertainty, closure timestamps, four label statuses |
| `contract/experiment_contract.py` | seed registries, deterministic derivation, common random numbers, provenance manifests, temporal checks, six-channel mutation canaries, negative-control and physical-scale checks, functional-form audit, repeated-measure aggregation |

## Tests

`tests/test_regressions.py` — 23 tests, one per discovered defect. **Each is
two-sided:** it reconstructs the broken historical behaviour and asserts the check
catches it, then asserts the fixed behaviour passes. Three historical tests were
unfalsifiable, so a test that only exercises the fixed path is not accepted here.

```
pytest tests/regression/test_regressions.py
```

## The three rules the toolkit exists to enforce

1. **Generate from geometry the endpoint can predict**, never filter a clock grid.
   Filtering left 96.58 % of one dataset below the horizon.
2. **Freeze row membership before labels exist.** Later information may change a
   label's status, value, uncertainty or closure time — never whether the row exists.
3. **Run a null control at every covariate level, first.** Two separate leaks would
   have been caught by that alone, before any headline number existed.

Dependencies: `numpy`. Optional: a propagator with the `sgp4_array` signature — the
tests use a dependency-free analytic stand-in.
