# Pre-registration — real-data L4.7 application

Written and committed **before** the analysis script existed and before any result was seen.
Its purpose is to make one claim auditable: that no detector, threshold, grouping, or
observable was chosen after seeing an outcome.

Committed at: see the commit that adds this file. The analysis script is added in a **later**
commit, and `evaluation/scripts/contract_layers.py` is **not touched by either**.

## What is frozen

`check_statistical_unit` (L4.7) in `evaluation/scripts/contract_layers.py` is imported
unchanged. Its parameters keep their defaults: `alpha=0.05`, `n_perm=400`,
`min_coarser_groups=4`, `seed=0`. No argument is overridden. If a run abstains, that is the
result; the floor will not be lowered to obtain a decision.

## Data

`dataraw/spacetrack/` — Space-Track GP_HISTORY records already present in this repository,
11 objects, 63,727 records. No new data is fetched.

**Analysis window: 2026-07-22 (inclusive) to 2026-07-27 (exclusive), on `EPOCH`.**

Chosen because it is the only window in which all eleven objects have element sets: the two
Starlink objects have records only from 2026-07-22. Element-set counts in this window are 7 to
14 per object, 109 in total. The window was fixed by data coverage, not by any outcome.

## Ground station (Analysis B only)

Declared before running: latitude 24.7961 N, longitude 120.9967 E, altitude 100 m
(Hsinchu, Taiwan). Elevation mask 10 deg. Sample interval 30 s. Propagation horizon 24 h
from each element set's own epoch. Geodetic normal, WGS-84.

SGP4 is used for **geometry only** — to decide when an object is visible above the mask and at
what elevation. No propagation error, no truth reference, no residual, no model is computed.
Nothing here reopens the stopped residual-learning line.

## The three analyses, with the observable fixed in advance

| | unit | coarser level | observable per sample | aggregation |
|---|---|---|---|---|
| **A** | element set | object | publication lag, `CREATION_DATE - EPOCH`, hours | one value per element set (no aggregation needed) |
| **B** | visible pass | element set that generated it | elevation at each 30 s sample, degrees | mean elevation over the pass |
| **C** | visible pass | object | elevation at each 30 s sample, degrees | mean elevation over the pass |

**A** asks whether the element set is exchangeable across objects for an availability quantity.
**B** asks the paper's own §I-A(v) question directly: are passes exchangeable within the element
set that produced them? **C** is the declared sensitivity analysis for the cross-cutting problem
— the same units under a *different* declared coarser level.

B and C are run **per object** as well as pooled, because pooling records across objects is
exactly the unit error this cycle corrected elsewhere.

## Predictions recorded in advance

Stated so they can be wrong. These are expectations, not requirements; the result is whatever
the frozen rule returns.

- **A**: expect HALT. Objects differ in operational cadence, so an element set drawn from one
  object is not exchangeable with one from another for publication lag. If it PASSes, that is
  evidence against a claim this paper makes.
- **B**: expect HALT for objects with enough element sets. Consecutive element sets of one
  object are issued hours apart, so passes derived from one element set fall in a narrow time
  span and share geometry.
- **C**: no prediction. This is the sensitivity check.
- The two Starlink objects have 9 and 11 element sets and may yield too few passes; if so the
  correct outcome is INDETERMINATE and it will be reported as such, not worked around.

## What will be reported regardless of outcome

Group structure, number of units, number of effective coarser groups, observed ICC, permutation
p-value, verdict, abstention status, and the sensitivity of the verdict to the declared grouping
level. A PASS, a HALT and an INDETERMINATE are all publishable results here; the question is
whether the gate produces an interpretable decision on real data, not whether it fires.

## What is prohibited in this analysis

No new detector. No new fault class. No change to L4.7 or any other rule. No model training.
No performance claim of any kind. No RF or packet-level quantity. If the analysis is
uninformative, that is the finding.
