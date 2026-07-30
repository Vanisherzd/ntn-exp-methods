# Delete plan

Conservative by construction: a ref is deleted only when its entire history is already
reachable through `main`, the active submission branch, a protected archive branch, or a
verified archival tag. Anything uncertain is kept. Nothing is force-pushed; no history is
rewritten.

## Branches to delete — 1

### `workshop-controlled-evidence-gate` (local only)

| check | result |
|---|---|
| tip | `9e3380c` — byte-identical to `main` |
| unique commits vs `main` + active | **0** |
| ancestor of `main` | YES |
| ancestor of active submission branch | YES |
| tags containing tip | 5 (`stop/real-tle-line-2026-07`, `stop/exp16-qualification-2026-07`, `evidence/formal-seeds-never-executed-2026-07`, `exp15-visible-causal-preregistered-v1`, `pre-finalization/orbit-evidence-workshop-2026-07`) |
| remote counterpart | none |
| working tree / worktree in use | no |

The ref is a pure alias for `main`. Deleting it removes a name, not a commit.

```
git branch -d workshop-controlled-evidence-gate     # -d, not -D: refuses if unmerged
```

`-d` is deliberate. If git refuses, the premise is wrong and the branch stays.

## Branches explicitly NOT deleted

| ref | why kept |
|---|---|
| `main` | protected; also 25 commits ahead of `origin/main`, so the remote does not yet hold its archival commits |
| `submission/orbit-evidence-workshop` | the active submission |
| `archive/residual-learning-stop-2026-07` | protected by rule 6; **2 commits reachable from nowhere else, no tag at tip** |
| `exp15-visible-causal-rebuild` | **2 commits reachable from nowhere else**; the pre-registration tag is an ancestor, not the tip, so the failing-gate commit is unique archival evidence |
| `origin/claude/leo-dtf-experiment-prep-ksnesg` | **18 commits not in the active branch**: HIL firmware, USRP B210 monitor, Doppler emulator, bench guides, CI. Unique work, unrelated to this submission |

## Tags to delete — none

All 21 tags are retained. `stop/*`, `evidence/*`, pre-registration and `archive/*` tags are
protected by rule; the historical checkpoint tags cost nothing and are the only handle on
several earlier repository states.

## Files deleted — none by this plan

No verified duplicate active manuscript was found: `paper/icc_main.tex` is the sole
manuscript source in the active tree, and the two retired manuscripts live under
`archive/retired_manuscript/{snapshot,paper_tree_committed}` where they are protected. No
`main.tex`, `main.pdf`, `main(N).pdf` or `icc_main(N).pdf` variant exists in the active
tree. A previously git-tracked macOS duplicate (`reference_ensemble 2.py`) was removed in
an earlier commit and is already absent.

## Post-deletion verification

```
git branch -vv                        # workshop-controlled-evidence-gate absent
git rev-parse --verify 9e3380c        # commit still exists
git tag --contains 9e3380c            # still 5+ tags
git log --oneline main -1             # main unchanged at 9e3380c
make gate                             # evidence and paper unaffected
```
