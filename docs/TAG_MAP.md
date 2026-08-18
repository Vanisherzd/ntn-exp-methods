# Tag map

**7 tags.** Each one is referenced by tracked documentation, so none is a dangling pointer.
**No tag has ever been created, moved, or rewritten** — that rule still holds. 29 redundant tags
were *deleted*, which removes a pointer without touching the commit it named; every one of those
commits is reachable from retained history or from the verified pre-cleanup bundle, and each deleted
name is recorded in [CLEANUP_RECORD.md](CLEANUP_RECORD.md) §13.

| Class | Tag | Commit | Date | What it is | Why retained |
|---|---|---|---|---|---|
| **MANUSCRIPT** | `paper/orbit-evidence-workshop-submission-ready-2026-08` | `76f53d3f` | 2026-08-01 | the submission-ready manuscript | canonical; named in `README.md` and the submission metadata |
| **ARTIFACT** | `artifact/orbit-evidence-workshop-2026-08` | `f751a3b5` | 2026-08-01 | the frozen evidence bundle the manuscript's claim sites bind to | canonical; the artifact the paper is verified against |
| **TALK** | `talk/orbit-evidence-reviewer-proof-2026-08` | `ff0c58b8` | 2026-08-02 | the reviewer-proof workshop deck | the released deck |
| **PRE-REGISTRATION** | `external-consequence-preregistered-v1` | `9745c149` | 2026-07-31 | the pre-registration behind the paper's **pre-registered intervention** | load-bearing: the external-consequence gate checks the artifact against it |
| **PRE-REGISTRATION** | `exp15-visible-causal-preregistered-v1` | `a97dab40` | 2026-07-30 | the pre-registration for a line later stopped | a pre-registration is a dated commitment and is never deleted, whatever its outcome |
| **EVIDENCE FREEZE** | `evidence/formal-seeds-never-executed-2026-07` | `4f18073b` | 2026-07-31 | a **negative** evidence record: seeds specified but never run | needed to interpret what the artifact does *not* contain |
| **STOP RECORD** | `stop/exp15-visible-causal-rebuild-2026-07` | `4bc5c463` | 2026-07-30 | the stop record paired with the pre-registration above | a pre-registration without its stop record is a dangling commitment; the pair is kept together |

The advisor-review deck (`talk/advisor_review/`) is **deliberately untagged** — a working deliverable
for supervision discussion, not a frozen artifact.

---

## Why these seven and nothing else

The two pre-registrations and the stop record are the subtle ones. `exp15-visible-causal-preregistered-v1`
names a research line that was **stopped**, and it would be easy to read as historical clutter. It is
not: deleting the pre-registration of an experiment that failed is precisely the deletion that makes
a pre-registration worthless. It is retained *because* the outcome was negative, and its paired
`stop/` tag records what happened.

`external-consequence-preregistered-v1` is the opposite trap — its name gives no hint that it is the
pre-registration behind the paper's pre-registered intervention. Do not mistake it for a stopped-line
tag. `paper/scripts/check_banlist.py` fails the build if the artifact's frozen commit or detector
hash disagrees with it.

## How to check a tag without trusting its name

```
git log -1 --format='%ad %s' --date=short <tag>            # when, and the commit subject
git show --stat <tag> -- paper/icc_main.tex                # did the manuscript exist, in what state
git show <tag>:evaluation/results/final_summary.json | head -20   # which artifact it carried
git tag --contains <commit>                                # which retained tags reach a commit
```

## Recovering a deleted tag

The pointers are gone; the commits are not.

```
git clone ../orbit-evidence-pre-cleanup-2026-08-18.bundle recovered
cd recovered && git tag        # all 36 pre-cleanup tags
```

Bundle SHA256 and verification are recorded in [CLEANUP_RECORD.md](CLEANUP_RECORD.md) §1.
