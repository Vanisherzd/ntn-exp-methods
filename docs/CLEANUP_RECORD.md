# Cleanup record — 2026-08-18

What the repository cleanup removed, what it deliberately did not, and how to recover anything.

---

## 1. Recovery bundle

Created **before** any deletion, covering every ref (branches, remote-tracking branches, all 36
tags, HEAD).

| | |
|---|---|
| Path | `../orbit-evidence-pre-cleanup-2026-08-18.bundle` (outside the working tree) |
| Size | 91 MB |
| Refs | 51 |
| SHA256 | `fafe1e24d541d3d1b33f3e268345d31f627d4b129fa758ab80a5f2e8c523c22c` |
| Verified | `git bundle verify` — complete history |

Recover anything with:

```sh
git clone ../orbit-evidence-pre-cleanup-2026-08-18.bundle recovered
# or, into the existing repo:
git fetch ../orbit-evidence-pre-cleanup-2026-08-18.bundle 'refs/*:refs/recovered/*'
```

> **The bundle covers tracked content only.** `git bundle --all` captures refs, so files that were
> never committed — gitignored raw captures, local-only data — are **not** in it. This distinction
> drove every decision in §4 below.

## 2. Tracked files removed: 828 → 118

Chosen by building an actual dependency closure from the manuscript, the frozen artifacts, the
build/test targets and the two current decks — not by filename. 710 tracked files removed.

| Count | Category |
|---|---|
| 344 | `archive/stopped_research/` — the halted PGRL / Doppler-residual programme |
| 170 | `archive/hardware_validation/` — RF campaign records |
| 130 | `archive/retired_manuscript/` — superseded manuscript trees and decks |
| 36 | `archive/real_tle_causality_audit/` — the dated audit that stopped the line |
| 24 | `submission_finalization/` — reviewer-loop scratch, review ledgers, state files |
| 3 | `docs/` — `DEVELOPMENT.md`, `FAILURE_TAXONOMY.md`, `FUTURE_MEASUREMENT_PROTOCOL.md` |
| 3 | `THE_PAPER.md` (obsolete once the duplicate `icc_main` copies went), `scripts/__init__.py` (never imported), `talk/orbit_evidence_talk.pdf` (regenerable by `make -C talk`) |

All recoverable from Git history and from the bundle.

## 3. Retained outside the dependency closure — CURRENT ARTIFACT DEPENDENCY, HISTORICAL ORIGIN

Four files are unreachable from the build graph but are referenced by **active submission metadata
or a pre-registration**, so removing them would have created dead references in records that must
not be rewritten:

| File | Referenced by |
|---|---|
| `archive/KNOWN_INVALID_RESULTS.md` | `paper/submission/ARTIFACTS.md`, `paper/submission/README.md` |
| `docs/CASE_STUDIES.md` | `paper/submission/ARTIFACTS.md` |
| `submission_finalization/CLAIM_LEDGER.md` | `paper/submission/CLAIMS.md`, `evaluation/mutations/PREREGISTRATION.md` |
| `submission_finalization/INVALID_RESULT_BANLIST.md` | `paper/scripts/check_banlist.py` (printed in gate output) |

`check_banlist.py` does **not** read `archive/` at runtime — it globs `paper/*.tex`, `*.bib`,
`figures/`, `tables/`, `sections/`, `submission/*.md` and `README.md`. The banlist patterns live in
the script itself.

## 4. Deliberately NOT deleted — irrecoverable untracked material

≈ **17.9 GB** of untracked, gitignored material remains on disk. None of it is in the bundle,
because none of it was ever committed. Deleting it would be permanent loss with no recovery path,
so the cleanup left it in place pending an explicit decision.

| Path | Size | What it is | Why retained |
|---|---|---|---|
| `archive/hardware_validation/` | 12 GB | 28 raw `.npy` conducted-IQ captures + campaign records | never committed; not in bundle |
| `hardware/` | 5.5 GB | OTA IQ replay runs, bench captures, capture tooling | never committed; not in bundle |
| `outputs/` | 305 MB | model outputs from the stopped line | never committed; not in bundle |
| `dataraw/` | 77 MB | **local Space-Track records** | never committed **and an active evidence input** — see below |
| `local_archive/` | 4.4 MB | stopped-line validation runs | never committed; not in bundle |
| `output/` | 1.9 MB | stopped-line decks; `output/pdf/slides_overview.pdf` is the **only** copy, its LaTeX source already gone | never committed; not in bundle |
| `advisor_package/`, `logs/`, `loop_engineering/`, `semtech_validation/` | < 1 MB | local packages and process scratch | never committed; not in bundle |

**`dataraw/` is a special case.** The Makefile documents that `make gate` does *not* regenerate from
it — the real-data artifacts are committed and the gate reads them, verifying contract hashes
against the pre-registration. `make realdata` skips gracefully when `dataraw/spacetrack` is absent,
so **the gates pass without it**. But it is the only copy of the raw input behind committed
evidence, and `evaluation/real_data/PREREGISTRATION.md`, `evaluation/results/publication_lag.json`,
`evaluation/scripts/measure_publication_lag.py` and
`paper/submission/FINAL_SUBMISSION_MANIFEST.md` all name it. It must not be deleted without a
decision about archiving it elsewhere first.

## 5. Generated files removed — all provably regenerable

13 `__pycache__` directories · `.pytest_cache` · 104 LaTeX intermediates (`.aux`, `.log`, `.nav`,
`.snm`, `.toc`, `.out`, `.fls`, `.fdb_latexmk`, `.bbl`, `.blg`, `.synctex.gz`, `.vrb`, `.bcf`,
`.run.xml`) · `paper/build/` · `build/` · `tmp/` (44 MB of render caches) ·
`payload_results_realizations/` (0 files) · `.DS_Store` · deck page-image caches ·
`talk/pptx/` build outputs.

Both decks were rebuilt afterwards and their gates re-run green.

## 6. Dead references into removed material — declared, not rewritten

§22 requires that no active file reference a deleted path, and that any reference into Git history
be explicit. Three retained files are **dated records that must not be rewritten**, and they contain
references to now-removed paths. They are declared here rather than edited:

| Record | References, now only in Git history and the bundle |
|---|---|
| `archive/KNOWN_INVALID_RESULTS.md` | `archive/real_tle_causality_audit/audits/E4_walk_forward_r1500.json`, `S2_analysis_r1500.json`, the phase-2 screening sweep, `docs/FAILURE_TAXONOMY.md`, `docs/FUTURE_MEASUREMENT_PROTOCOL.md` |
| `submission_finalization/CLAIM_LEDGER.md` | `docs/FAILURE_TAXONOMY.md` §1–2 and §12 |

`talk/SPEAKER_OUTLINE.md` names `talk/orbit_evidence_talk.pdf`, which is no longer tracked but is
produced on disk by `make -C talk`, so that reference resolves after a build.

## 7. Verification after cleanup

| Check | Result |
|---|---|
| `paper/scripts/check_banlist.py` | 16 files clean, 64 artifact numbers bound at named claim sites |
| `pytest tests/regression tests/fault_injection` | 61 passed, 1 skipped |
| `make matrix` | regenerates; `matrix_sha256` unchanged (`cb3e9aed…`); only wall-clock timings and the recorded commit differ |
| `paper/icc_main.tex` | builds |
| Bibliography | 22 citations, 22 entries, **0 unresolved, 0 unused** |
| Broken symlinks | none |
| `import orbit_evidence` | OK |
| `make -n gate` | resolves |
| `make -C talk` / `make -C talk/advisor_review` | both rebuild; advisor deck's 14 gates green |
