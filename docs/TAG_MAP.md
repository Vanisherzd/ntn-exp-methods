# Tag map

36 tags. **None has been created, moved, or deleted** by any consolidation work.

Ten tags predate the `prefix/` naming convention, so their class cannot be read from the name.
That is why this file exists. They are **documented rather than renamed**: renaming a git tag means
deleting and recreating it, and the repository's rule is that tags never move.

---

## Current — the three that matter

| Class | Tag | Date | Object | What it is |
|---|---|---|---|---|
| **MANUSCRIPT** | `paper/orbit-evidence-workshop-submission-ready-2026-08` | 2026-08-01 | `0827afec` | the submission-ready manuscript (commit `76f53d3`) |
| **ARTIFACT** | `artifact/orbit-evidence-workshop-2026-08` | 2026-08-01 | `af7fbb2b` | the frozen evidence bundle the manuscript's claim sites bind to |
| **WORKSHOP TALK** | `talk/orbit-evidence-reviewer-proof-2026-08` | 2026-08-02 | `cd3c7d2d` | the reviewer-proof workshop deck |

The advisor-review deck (`talk/advisor_review/`) is **not tagged** — it is a working deliverable for
pre-submission discussion, not a frozen artifact.

## Frozen evidence

| Tag | Date | What it records |
|---|---|---|
| `evidence/formal-seeds-never-executed-2026-07` | 2026-07-31 | a negative evidence record: seeds that were specified but never run |

## Superseded manuscript candidates — **not the submission**

Ten tags, all `paper/orbit-evidence-*`. Read them as a revision trail, not as alternatives.

| Tag | Date |
|---|---|
| `paper/orbit-evidence-pre-external-validation-2026-07` | 2026-07-31 |
| `paper/orbit-evidence-workshop-submittable-baseline-2026-07` | 2026-07-31 |
| `paper/orbit-evidence-workshop-submission-2026-07` | 2026-07-31 |
| `paper/orbit-evidence-workshop-review-ready-2026-07` | 2026-07-31 |
| `paper/orbit-evidence-workshop-candidate-polish-2026-07` | 2026-07-31 |
| `paper/orbit-evidence-workshop-candidate-visual-2026-07` | 2026-07-31 |
| `paper/orbit-evidence-workshop-candidate-narrative-2026-08` | 2026-08-01 |
| `paper/orbit-evidence-workshop-candidate-geometry-2026-08` | 2026-08-01 |
| `paper/orbit-evidence-workshop-final-candidate-2026-08` | 2026-08-01 |
| `paper/orbit-evidence-workshop-hardened-final-2026-08` | 2026-08-01 |

## Stopped research — **not current evidence**

| Tag | Date | What stopped |
|---|---|---|
| `stop/real-tle-line-2026-07` | 2026-07-31 | the real-TLE residual line |
| `stop/exp15-visible-causal-rebuild-2026-07` | 2026-07-30 | the visible-causal rebuild |
| `stop/exp16-qualification-2026-07` | 2026-07-31 | the qualification experiment |

## Historical repository states

Nine `archive/*` tags from 2026-06, covering the hardware-validation and paper-hardening period.

| Tag | Date |
|---|---|
| `archive/hardware-validation` | 2026-06-04 |
| `archive/paper-hardening-vtc-icc` | 2026-06-06 |
| `archive/uncertainty-head-experiment` | 2026-06-08 |
| `archive/hardware-rx-per-validation` | 2026-06-08 |
| `archive/real-hardware-per-run` | 2026-06-09 |
| `archive/final-repo-clean` | 2026-06-10 |
| `archive/paper-final-polish` | 2026-06-10 |
| `archive/repo-clean-only` | 2026-06-10 |
| `archive/submission-cleanup-workshop-scope` | 2026-06-10 |

## Legacy, unprefixed — **class not readable from the name**

These ten predate the convention. This table is the only place their class is recorded.

| Tag | Date | Class | Note |
|---|---|---|---|
| `globecom-prehw-2026-05` | 2026-05-30 | HISTORICAL | pre-hardware GLOBECOM-era state |
| `paper-hardening-safe-20260604` | 2026-06-06 | HISTORICAL | same object as `archive/paper-hardening-vtc-icc` |
| `stage3e-uncertainty-calibrated` | 2026-06-07 | STOPPED RESEARCH | uncertainty-head line |
| `legacy-full-research-state` | 2026-06-10 | HISTORICAL | the full pre-cleanup tree |
| `paper-final-6page-204a053` | 2026-06-16 | SUPERSEDED MANUSCRIPT | an earlier 6-page state |
| `submission-clean-main-31da77b` | 2026-06-16 | HISTORICAL | a clean `main` snapshot |
| `paper1-preRewrite-2026-07-27` | 2026-07-27 | SUPERSEDED MANUSCRIPT | before the Orbit-Evidence rewrite |
| `pre-finalization/orbit-evidence-workshop-2026-07` | 2026-07-27 | SUPERSEDED MANUSCRIPT | prefixed, but with a class name no other tag uses |
| `exp15-visible-causal-preregistered-v1` | 2026-07-30 | PRE-REGISTRATION | the pre-registration for a line later stopped |
| `external-consequence-preregistered-v1` | 2026-07-31 | PRE-REGISTRATION | the pre-registration for the intervention reported in the paper |

The last one is load-bearing: **`external-consequence-preregistered-v1` is the pre-registration
behind the paper's pre-registered intervention**, and its name gives no hint of that. Do not
mistake it for a stopped-line tag.

---

## How to check a tag without trusting its name

```
git log -1 --format='%ad %s' --date=short <tag>     # when, and the commit subject
git show --stat <tag> -- paper/icc_main.tex          # did the manuscript exist, and what state
git show <tag>:evaluation/results/final_summary.json | head -20   # which artifact it carried
```
