# Branch and tag inventory

Taken 2026-07-31, after `git fetch --all --tags --prune`.
Remote: `origin` → `https://github.com/Vanisherzd/PGRL-LRFHSS-D2S.git`

Every branch was classified by four measurements before any deletion decision:
unique commit count, containing tags, merged status, remote status.

## Local branches

| branch | tip | unique vs main+active | merged into active | merged into main | tags containing tip | upstream | classification |
|---|---|---|---|---|---|---|---|
| `submission/orbit-evidence-workshop` (was `paper/orbit-evidence-contract`) | see PUSH_LOG | 18 vs main | — | NO | — | to be set | **ACTIVE SUBMISSION — protected** |
| `main` | 9e3380c | 0 | YES | — | 5 tags | `origin/main` (local **ahead 25**) | **PROTECTED, untouched** |
| `archive/residual-learning-stop-2026-07` | 964e04f | **2** | NO | NO | **none** | none | **PROTECTED — unique archival evidence** |
| `exp15-visible-causal-rebuild` | 4bc5c46 | **2** | NO | NO | **none at tip** | none | **PRESERVE — unique stop evidence** |
| `workshop-controlled-evidence-gate` | 9e3380c | **0** | YES | YES | 5 tags | none | **OBSOLETE — pure alias of `main`** |

### Notes on the non-obvious cases

**`main` is 25 commits ahead of `origin/main`.** This is a pre-existing condition, not
created by this finalization. It is recorded because it means `origin/main` does **not**
yet contain the retired-manuscript archival commits. Per the governing rules, `main` is
neither modified nor pushed here; resolving the divergence is a separate, human decision.

**`archive/residual-learning-stop-2026-07` carries 2 commits reachable from nowhere else**
and no tag points at its tip:

```
964e04f archive: record final archive hashes
4f18073 archive: stop both residual-learning lines; salvage reusable engineering assets
```

It is explicitly protected by rule 6. It must also be pushed so the archive is *remotely*
reachable — currently it exists only locally, which is the single largest archival risk in
this repository.

**`exp15-visible-causal-rebuild` carries 2 commits reachable from nowhere else:**

```
4bc5c46 exp15: visible-pass registry, ensemble labels, R3 censoring gate FAILS
a97dab4 exp15: pre-register visible-pass causal residual protocol
```

`exp15-visible-causal-preregistered-v1` is an **ancestor** of the tip, not the tip, so the
tag does not make the failing-gate commit reachable. That commit is the record of *why* the
real-TLE line was stopped, which is archival evidence. Retained, and tagged (see below) so
its evidence survives independently of the branch ref.

**`workshop-controlled-evidence-gate` is the only genuine deletion candidate.** Its tip is
byte-identical to `main` (both 9e3380c), it has zero unique commits, it is an ancestor of
both `main` and the active branch, five tags contain its tip, and it has no remote. Nothing
is lost by removing the ref.

## Remote branches

| branch | tip | unique vs active | classification |
|---|---|---|---|
| `origin/main` | 9e3380c − 25 | — | **PROTECTED** |
| `origin/claude/leo-dtf-experiment-prep-ksnesg` | d253708 | **18** | **PRESERVE — unique work, not in this submission** |

`origin/claude/leo-dtf-experiment-prep-ksnesg` is **not** an ancestor of the active branch
and is not superseded by it. It holds a hardware-in-the-loop package that exists nowhere
else: LR1121 pre-compensated hop-beacon firmware for NUCLEO-L476RG, a USRP B210
residual-Doppler monitor, a Doppler emulator, a bench runner, HIL tests, bring-up guides,
and a GitHub Actions CI pipeline. None of it belongs to this workshop submission, and none
of it may be deleted. Left exactly as it is.

## Tags — all 21 preserved, none deleted

Protected by rule 6 (`stop/*`, `evidence/*`, pre-registration tags, archival tags):

| tag | role |
|---|---|
| `stop/real-tle-line-2026-07` | terminates the real-TLE line |
| `stop/exp16-qualification-2026-07` | terminates the controlled-benchmark line |
| `evidence/formal-seeds-never-executed-2026-07` | attests the blind seeds were never run |
| `exp15-visible-causal-preregistered-v1` | human-gated pre-registration |
| `pre-finalization/orbit-evidence-workshop-2026-07` | safety tag taken before this finalization |
| `archive/*` (9 tags) | historical repository states |
| `paper1-preRewrite-2026-07-27`, `paper-final-6page-204a053`, `paper-hardening-safe-20260604`, `globecom-prehw-2026-05`, `legacy-full-research-state`, `stage3e-uncertainty-calibrated`, `submission-clean-main-31da77b` | historical checkpoints |

### Tag added by this finalization

| tag | points at | why |
|---|---|---|
| `stop/exp15-visible-causal-rebuild-2026-07` | `4bc5c46` | makes the failing-censoring-gate commit reachable by tag, so the stop evidence survives independently of the branch ref |

No tag was moved, renamed or deleted.
