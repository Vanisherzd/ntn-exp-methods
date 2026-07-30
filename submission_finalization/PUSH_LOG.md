# Push log

Pushed 2026-07-31, after the evidence gate and camera-ready gate both passed.
No force-push. No history rewritten. `main` neither modified nor pushed.

## Pushed

| ref | kind | why |
|---|---|---|
| `submission/orbit-evidence-workshop` | branch (new remote) | the active submission, 33 commits ahead of `main` |
| `archive/residual-learning-stop-2026-07` | branch (new remote) | **2 commits reachable from nowhere else**, and until now local-only. This was the single largest archival risk in the repository |
| `exp15-visible-causal-rebuild` | branch (new remote) | 2 unique commits; its pre-registration tag is an *ancestor*, so the tag alone did not make the failing-censoring-gate commit reachable |
| `stop/real-tle-line-2026-07` | tag | terminates the real-TLE line |
| `stop/exp16-qualification-2026-07` | tag | terminates the controlled-benchmark line |
| `stop/exp15-visible-causal-rebuild-2026-07` | tag (new) | pins the failing-gate commit independently of the branch ref |
| `evidence/formal-seeds-never-executed-2026-07` | tag | attests the blind seeds were never run |
| `exp15-visible-causal-preregistered-v1` | tag | human-gated pre-registration |
| `pre-finalization/orbit-evidence-workshop-2026-07` | tag | state before this finalization |
| `paper/orbit-evidence-workshop-review-ready-2026-07` | tag (new) | the reviewed state |

**Not pushed, deliberately:** `main`, and any submission tag. The final submission tag awaits
explicit human approval, per the governing instruction.

## Verification

```
local  HEAD  9fc5d7de9941177e8e28fd52840626674e3dc0dd
remote HEAD  9fc5d7de9941177e8e28fd52840626674e3dc0dd     MATCH

local main   9e3380c        origin/main  31da77b
local main is 25 commits ahead of origin/main -- unchanged by this push
```

Present remotely on the submission branch: `paper/icc_main.tex`, `paper/refs.bib`,
`evaluation/results/final_summary.json`, `Makefile`, `archive/KNOWN_INVALID_RESULTS.md`,
`tests/fault_injection/test_claim_gate.py`.

`paper/icc_main.pdf` is **not** tracked and therefore not remote — it is a regenerable build
product, gitignored along with `paper/build/`. `make paper` reproduces it.

Remotely reachable after the push: the archive branch, the exp15 branch, and every `stop/*`,
`evidence/*`, pre-registration and finalization tag.

## Two things a human should decide

**1. The remote has been renamed.** Every push printed:

```
remote: This repository moved. Please use the new location:
remote:   https://github.com/Vanisherzd/LEO-PGRL.git
```

The configured URL is still `PGRL-LRFHSS-D2S.git` and GitHub is redirecting. Pushes succeed,
but the redirect is a courtesy, not a guarantee. Updating it is a one-liner and is left to
you because it changes where this repository publishes:

```
git remote set-url origin https://github.com/Vanisherzd/LEO-PGRL.git
```

**2. `main` and `origin/main` have diverged by 25 commits.** This predates the finalization and
was not created by it. It means the remote default branch does not contain the archival commits
that local `main` carries. `main` was left untouched on purpose; reconciling it is a separate
decision, not a cleanup step.
