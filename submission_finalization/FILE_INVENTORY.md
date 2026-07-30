# FILE INVENTORY (pre-cleanup)

Safety tag: `pre-finalization/orbit-evidence-workshop-2026-07` at `4fa7444`

## SHA-256 of key artifacts

| role | path | sha256 |
|---|---|---|
| active_tex | `submission_recovery/manuscript/main.tex` | `dda7bf59a37600d739c93c0babb5c839` |
| active_pdf | `submission_recovery/manuscript/main.pdf` | `479d3a79024baa189e0700a509006cee` |
| refs_bib | `submission_recovery/manuscript/refs.bib` | `cae1c39c380fcc3f56aacb536eb8b144` |
| banlist_checker | `submission_recovery/manuscript/check_banlist.py` | `8f75c0252ba9f3ceaca24a633c74d1a2` |
| eval_result | `submission_recovery/evaluation/MATRIX_RESULT.json` | `03e4a889489180288087e9db7ea3093a` |
| eval_runner | `submission_recovery/evaluation/run_matrix.py` | `1d214fdc7647d3735084a135cdff66d6` |
| contract_layers | `submission_recovery/evaluation/contract_layers.py` | `4fdd543e4f5cbcd2cd72891ef78b3480` |
| pipelines | `submission_recovery/evaluation/pipelines.py` | `0018ea855b445a78e609ad6067831114` |
| retired_manifest | `archive/retired_manuscript/snapshot/MANIFEST.sha256` | `MISSING` |
| invalid_banlist | `archive/KNOWN_INVALID_RESULTS.md` | `114093bf9b66946ccf59c3734588981b` |

## Duplicate files found (macOS copy artifacts)

| file | status | action |
|---|---|---|
| `salvage/orbit-evidence-toolkit/__init__ 2.py` | byte-identical to `__init__.py` (both 0 B) | OBSOLETE_DUPLICATE, delete |
| `salvage/orbit-evidence-toolkit/ensemble/reference_ensemble 2.py` | byte-identical to base (4363 B) | OBSOLETE_DUPLICATE, delete |

Both are untracked, byte-identical to their originals, and referenced by nothing.
Verified with `diff -q` before classification.

## Untracked directories

| path | category | disposition |
|---|---|---|
| `experiments/exp15_causal_recovery/` | ARCHIVAL_EVIDENCE | already mirrored under `archive/real_tle_causality_audit/`; keep out of the active tree |
| `experiments/exp15_visible_causal/` | ARCHIVAL_EVIDENCE | same |
| `submission_recovery/` | ACTIVE_PAPER + ACTIVE_EVALUATION | to be split across `paper/`, `evaluation/`, `submission_finalization/` |
