# ARCHIVE — REAL-TLE CAUSALITY AUDIT

> **INVALID RESULTS NOTICE — read first: [`../KNOWN_INVALID_RESULTS.md`](../KNOWN_INVALID_RESULTS.md)**
> No numerical result in this directory may be cited as scientific evidence.

**The Space-Track archive route was not used as primary workshop evidence because
reference availability is missing-not-at-random with respect to TLE age. No
predictive model was fitted after this gate failed.**

Status: **FROZEN**. Retained in full for provenance. Not deleted, not extended,
and **not the novelty of the workshop paper**.

---

## What this archive is

A record of three successive attempts to build a causally valid, deployable
residual-correction benchmark from a historical Space-Track GP archive, and of the
audit that ended the line. Each attempt was independently reviewed; each review
found a defect the implementer had missed; the final attempt fixed every defect
found and was stopped by a property of the data source rather than by a bug.

The line is closed. It is archived because the negative result is genuine and the
tooling is reusable, not because it is publishable.

## Why the route was abandoned

Labels for stale-TLE prediction error must come from later-published elements. But
the same catalogue publication outage that makes a held element stale also removes
the later elements needed to label that staleness. Censoring and the primary
covariate therefore share a single cause.

Measured on the final, defect-free build (9 satellites, 2 provisioning scenarios,
~133 k predicted-visible transmissions):

| quantity | value | pre-registered gate |
|---|---|---|
| max abs standardized mean difference, labelled vs censored | **1.307** NOMINAL / **1.552** DEGRADED | ≤ 0.10 |
| driven by | TLE age (≤ 1.35), calendar time (≤ 1.56) | — |
| geometry variables (elevation, range, Doppler) | ≤ 0.28, mostly < 0.10 | ≤ 0.10 |
| time to next publication, labelled → censored | 4–13× larger (ISS 2.88 → 44.63 h) | — |
| minimum per-satellite COMPLETE rate | 0.631 / 0.660 | ≥ 0.70 |

No age restriction removes the imbalance (BLACK KITE-1 |SMD| 0.755 at age ≤ 30 h,
0.536 at ≤ 36 h), and no closure horizon or `K_min` in the pre-registered
feasibility grid satisfies the per-satellite floor.

## What was genuinely fixed before the stop

The final build is not a failed build. It corrected every defect that independent
review had raised:

| defect found by review | fix, verified |
|---|---|
| `t_gap_s` feature knowable only after the future element is published | removed; absent from the manifest; test V8 enforces |
| 96.58 % of transmissions below the endpoint horizon | transmissions generated from stale-TLE-predicted visible passes; **100 % above mask**, global min 10.034° |
| row membership decided by which elements were later published | registry SHA-256 frozen before any reference query; **test V1** confirms the schedule is bit-identical when the future catalogue is truncated |
| single arbitrary reference whose choice moved the target more than the target | reference-ensemble median with published `sigma_ref = 1.4826·MAD`; ratio **1.81 → 0.06–0.39**. Reduced ~3–4×, **not eliminated**: 83–95 % of members are back-propagated from the same lineage, so σ_ref misses a common error worth **5–16× the 5 % margin**. |
| coverage unknown | R6 **PASS**: 9 satellites, 6 orbital regimes, 110,699 / 118,785 COMPLETE transmissions |

## Why the stop holds even after the review corrections

Both reviewers returned **FAIL**, and both corrected claims of mine. The censoring
I measured is partly self-inflicted — a data-dependent closure rule cuts it up to
**76×**. But two findings bind regardless of any closure rule: label ambiguity runs
**5–16×** the 5 % gate margin, and six of nine satellites have a bound on the
*baseline* MAE wider than that margin. Beneath both, the residual is
**0.006–0.36 %** of the Doppler being pre-compensated — 0.18 mm/s for SENTINEL-6B,
finer than any TLE-derived quantity resolves. The archive cannot resolve the
question, independent of model or construction.

Two of the six pre-registered integrity tests (V1, V4) were shown to be structurally
incapable of failing. Anyone reusing `code/` must repair them first: V1 must
truncate the future with `t_end=None`, and V4 must compare independently rebuilt
registries.

## Reusable, and where it goes

Three components transfer to any endpoint-side study and to the future SDR
measurement campaign, where the label comes from received signal and this bias
class does not arise:

1. **`code/build_visible_registry.py`** — event-driven visible-pass scheduler.
   Generating transmissions from stale-TLE-predicted passes is the correct
   construction; filtering a UTC grid by elevation is not.
2. **The freeze-then-label discipline** — hashing row membership before querying
   labels makes a whole class of leakage structurally impossible, and test V1
   detects it mechanically.
3. **`code/build_ensemble_labels.py`** — reference-ensemble label with published
   uncertainty. The honest way to use catalogue elements as a reference.

## Frozen git state

| item | reference |
|---|---|
| branch | `exp15-visible-causal-rebuild` |
| pre-registration commit (tagged) | `a97dab406ef00eca674f8e612133b33cf5ca1a4d` |
| pre-registration tag | `exp15-visible-causal-preregistered-v1` |
| execution commit (R0–R8) | `4bc5c46` |
| earlier real-TLE work | commits `9e3380c`, `62083b5`, `93af583`, `017f37e` on `main` |
| manuscript snapshot | `loop_engineering/snapshots/manuscript_freeze_20260730T072500Z/` (62 files, 4.7 MB, `MANIFEST.sha256`) |

Bulk derived arrays (~50 MB of `.npz`) are gitignored and regenerate from
`code/`. The JSON summaries and every audit report are archived here.

## Contents

```
specs/     pre-registered protocol, schedule config, label spec, model manifest,
           analysis plan, horizon/K_min selection; plus the earlier
           provisioning_policy.json and preregistration.json
audits/    R1 registry summaries, R2 feasibility grid, R3 censoring audits
           (both scenarios), R6/R7/R8 diagnostics, and the earlier E1
           verification, E4 walk-forward and S2 analysis
evidence/  E0_DOSSIER.md (availability-clock audit), S2_FIRST_DOSSIER.md,
           FINAL_CAUSAL_VISIBLE_S2_DOSSIER.md, loop-engineering state files
code/      visible-pass registry builder, ensemble labeller, integrity tests
```

## Audit trail of verdicts

| stage | verdict |
|---|---|
| exp14 / original headline | invalidated — result was a `t_gap_s` artifact |
| deployable_v1 rerun | 0/54 primary cells preserved; every learned candidate lost to SGP4 |
| S2-first pilot | **UNRESOLVED** — dataset 96.58 % below horizon; both reviewers FAIL |
| exp15 visible-causal rebuild | **UNRESOLVED** — R3 label-censoring gate FAIL; R6 PASS; no model fitted. Reviewer A **FAIL**, Reviewer B **FAIL**. |

Independent reviewers were dispatched at each stage; no implementing agent
approved its own output. Both reviewers of the final build returned FAIL; their
findings are integrated in `evidence/FINAL_CAUSAL_VISIBLE_S2_DOSSIER.md` §16,
with the three corrections to the implementer's own claims recorded in §14.

## Standing constraints on this archive

Do not repair, extend or re-run this route. Do not present it as the workshop
paper's novelty. Do not delete it.
