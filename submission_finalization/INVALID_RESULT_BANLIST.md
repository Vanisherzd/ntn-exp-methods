# INVALID RESULT BANLIST

Machine-checkable ban list for the new paper. Source of truth:
`../archive/KNOWN_INVALID_RESULTS.md`.

**Nothing below may appear in the manuscript, figures, tables, abstract or artifact
description, in any form, including paraphrase or rounded restatement.**

| # | banned content | banned tokens (grep) |
|---|---|---|
| B1 | the withdrawn headline improvement | `1.94`, `1.369`, `3.26 mHz`, `0.16414`, `0.16740`, `0.16857` |
| B2 | old deployment-cell tallies | `0/54`, `0 of 54`, `11/54`, `2/54`, `54 cells`, `279 segments` |
| B3 | old screening opening | `1/270`, `1 of 270`, `18.390`, `5.119`, `270 cells` |
| B4 | EXP16 probe performance rates | `0.42 harm`, `264 helpful`, `60 harmful`, `33 %`, `48 %`, `B/A`, `val_ratio` as a result |
| B5 | endpoint-budget conclusions | `500 Hz` as a requirement, `E_succ`, `guard cost`, `energy per success`, `outage` as a result |
| B6 | any validated-gate claim | "Evidence Gate improves", "validated", "reduces failure", "deployable correction works" |
| B7 | anything from the retired manuscript's results | any number traceable to `archive/retired_manuscript/` |

## What IS permitted, and the distinction that matters

A **performance result** claims a method works. A **defect characterisation** counts a
property of a dataset or pipeline. The first is banned outright. The second may be
cited *as case-study evidence that the defect class occurs in practice*, provided it
is labelled as an observation on an experiment that was subsequently **stopped**, and
provided the paper's primary evidence is the new fault-injection evaluation.

Permitted under that rule, with mandatory framing:

| observation | mandatory framing |
|---|---|
| a UTC-grid schedule placed 96.6 % of transmissions below the horizon | "in one stopped pipeline"; never "typical" |
| labelled-vs-censored standardized mean difference reached 1.35 on the study covariate | "observed in a stopped pipeline"; never a general rate |
| a permitted state channel produced admission on a zero-effect control | "the control detected it"; never a performance figure |
| blind evaluation seeds were never executed | statement of process, not of result |

Every permitted observation must carry a citation to an audit artifact, never to the
retired manuscript.

## Enforcement

`check_banlist.py` greps the manuscript source for every banned token and fails the
build. Run before every compile.
