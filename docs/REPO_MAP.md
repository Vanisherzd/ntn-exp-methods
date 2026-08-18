# Repository map

This tree contains **only** the current Orbit-Evidence project. Historical material was removed
from the active checkout on 2026-08-18 and is recoverable from Git history and the verified
pre-cleanup bundle — see [CLEANUP_RECORD.md](CLEANUP_RECORD.md).

133 tracked files, down from 828.

---

## Two-minute orientation

| Question | Answer |
|---|---|
| Current research | **Orbit-Evidence: Relational Validity Checks for Learning-Assisted Satellite Communication Experiments** |
| Canonical manuscript | `paper/icc_main.tex` · tag `paper/orbit-evidence-workshop-submission-ready-2026-08` |
| Frozen artifact | `evaluation/results/`, `evaluation/real_data/` · tag `artifact/orbit-evidence-workshop-2026-08` |
| Workshop talk | `talk/orbit_evidence_talk.tex` · tag `talk/orbit-evidence-reviewer-proof-2026-08` |
| Advisor-review deck | `talk/advisor_review/advisor_deck.tex` · advisor-only, untagged |
| Stopped research in this tree | **none**, except one retained record — see below |
| Generated files | §3 |
| Reproduce | §4 |
| Must never be edited | `paper/`, `evaluation/`, anything under a frozen tag, and the dated records in §2 |

## 1. The active tree

| Path | Role |
|---|---|
| `paper/icc_main.tex`, `refs.bib`, `figures/`, `tables/`, `sections/` | the manuscript and everything it `\input`s |
| `paper/submission/` | submission metadata; scanned by the claim gate |
| `paper/scripts/check_banlist.py` | the claim + banlist gate — 64 artifact-bound claim sites |
| `evaluation/scripts/` | detector, experiment and verification scripts |
| `evaluation/results/`, `evaluation/real_data/`, `evaluation/external*/`, `evaluation/mutations/` | frozen evidence and pre-registrations |
| `src/orbit_evidence/` | the contract and detector implementation |
| `tests/` | regression and fault-injection suites |
| `scripts/compare_summaries.py` | used by `make gate-twice` |
| `talk/` | the workshop deck, its figures, number generator, ledger and gates |
| `talk/advisor_review/` | the advisor deck, its number generator and 14 gates |
| `talk/pptx/` | a PowerPoint rendering of the workshop deck, with its own gates |
| `docs/` | this map, the tag map, reproducibility, history, cleanup record, case studies |
| `Makefile`, `README.md`, `.gitignore`, `pyproject.toml` | build and repository configuration |

## 2. Generated **and** canonical — regenerable is not disposable

These are produced by `make matrix`, tracked, covered by the artifact tag, and carry the claim sites
the manuscript binds to. Moving one breaks the manuscript gate and all three deck generators at
once.

`evaluation/results/final_summary.json` · `l47_power_curve.json` · `l47_calibration.json` ·
`matrix_result*.json` · `evaluation/real_data/l47_alongtrack.json`

They embed wall-clock timings and the generating commit, so **any run of `make matrix` dirties them**
without changing `matrix_sha256`. That is a property of the artifact format, not a cleanup defect.

### Dated records — retained, never rewritten

| File | Why it stays |
|---|---|
| `archive/KNOWN_INVALID_RESULTS.md` | referenced by `paper/submission/ARTIFACTS.md` and `README.md` |
| `docs/CASE_STUDIES.md` | referenced by `paper/submission/ARTIFACTS.md` |
| `submission_finalization/CLAIM_LEDGER.md` | referenced by `paper/submission/CLAIMS.md` and a pre-registration |
| `submission_finalization/INVALID_RESULT_BANLIST.md` | printed in the claim gate's output |

Their role is current; their origin is historical. They contain references to paths that now exist
only in Git history — declared in [CLEANUP_RECORD.md](CLEANUP_RECORD.md) §6 rather than edited.

## 3. Untracked data — archived outside the repository

The working directory holds **no multi-GB research payload**. The ≈ 18 GB of gitignored material
that was never committed — and so was never in the bundle — was copied out, verified hash-for-hash,
and removed on 2026-08-18. Working directory: 18 GB → **767 MB**.

| Archive (sibling directory) | Contents |
|---|---|
| `../orbit-evidence-raw-archive-2026-08-18/` | `dataraw/` — the Space-Track records behind the committed real-data artifacts |
| `../stopped-research-raw-archive-2026-08-18/` | the stopped line's IQ captures, bench sweeps and HIL captures |
| `../orbit-evidence-historical-output-2026-08-18/` | generated output whose source is gone: two decks, a superseded build, stopped-line runs |

Each has a `README.md` and a `MANIFEST.sha256`; see [CLEANUP_RECORD.md](CLEANUP_RECORD.md) §4 for
counts, byte totals and manifest hashes. **The submission gates do not read any of them** — that was
re-verified from a clean clone after removal. Only `make realdata` needs the current-evidence
archive, and it skips gracefully without it.

What remains untracked in the tree: `.venv/` (the toolchain, reproducible from `uv.lock`), `.git/`,
`.claude/`, `uv.lock`, and `.env.spacetrack` (credentials — never archived, never committed).

## 4. Build command map

| Deliverable | Command | Reads | Writes |
|---|---|---|---|
| Evidence artifacts | `make matrix` | detector, fixtures | `evaluation/results/*.json` |
| Tests | `make test` | `tests/`, `evaluation/` | — |
| Claim gate | `make claims` | manuscript, `final_summary.json` | — |
| Paper | `make paper` / `make verify` | `paper/` | `paper/icc_main.pdf` |
| **Full gate** | `make gate` | all of the above, `matrix → test → claims → verify` | — |
| Determinism | `make gate-twice` | as above, twice | compares two summaries |
| External verification | `make external-consequence-verify` | committed external artifacts | — |
| Real-data re-derivation | `make realdata` | `dataraw/` if present, else skips | real-data artifacts |
| Workshop deck | `make -C talk` / `check` | 3 artifacts + deck source | `numbers.tex`, deck PDF |
| Advisor deck | `make -C talk/advisor_review` / `check` / `render` | 3 artifacts + 2 detector sources | `numbers.tex`, deck PDF, page images |

`make gate` does not regenerate the two external evidence artifacts, because neither input ships
with the repository. It reads their committed artifacts and refuses to build if a contract hash or
frozen commit differs from its pre-registration.
