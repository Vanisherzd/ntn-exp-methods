# Submission package

| field | value |
|---|---|
| **title** | Beyond Chronological Splits: A Deployment-Causality and Falsifiability Contract for Learning-Assisted Satellite Communication Software |
| **entry point** | `paper/icc_main.tex` (sole active manuscript source) |
| **rendered PDF** | `paper/icc_main.pdf` |
| **build** | `make paper` from the repository root; `make gate` runs the full submission gate |
| **expected pages** | 6 |
| **venue class** | flagship workshop |
| **anonymity** | anonymous — author block is `Anonymous Submission`; no acknowledgements, no self-identifying paths in the text |
| **evaluation artifact** | `evaluation/results/final_summary.json`, derived from `matrix_result.json`; regenerate with `make matrix` |

## One-sentence thesis

Orbit-Evidence turns deployment-time availability, row membership, model-state and
statistical-unit assumptions into executable CI checks for satellite communication
experiments; a curated regression suite demonstrates those checks on seventeen known fault
classes that chronological ordering alone is not designed to detect.

## Build invariants, enforced mechanically

`make verify` fails unless the log shows six pages, zero LaTeX errors, zero undefined
references, zero undefined citations and zero overfull boxes. The PDF target additionally
has `scripts/check_banlist.py` as a hard prerequisite, so a build cannot succeed while a
prohibited or withdrawn claim appears in any source file, or while a headline number
disagrees with the summary artifact.

## Allowed claims

- Chronological splitting constrains ordering and does not by itself establish
  availability, row membership, the contents of a learner's hidden state, or that the
  statistical unit is exchangeable.
- On our curated suite, chronological protocol checks detect **2 of 17** fault classes;
  the contract detects **17 of 17** across three deterministic environments (51 injected
  cells).
- Clean reference paths are accepted and clean verdicts are identical across environments.
  For L4.7 the specificity claim is a **measured rate**: 0.042 false halts over 450 clean
  paths against a nominal α = 0.05.
- **16 of 19** rules have a demonstrated broken fixture; L2.2, L2.3 and L4.5 are exercised
  only on the clean path, and the paper says so.
- Two case-study pipelines were halted by a contract rule before any conclusion was drawn,
  and in the second case the pre-registered blind evaluation seeds were never executed.
- The toolkit is 833 lines across four modules plus a 655-line test suite, `numpy` only.
- The sweep runs in under 2 s, cheap enough for a per-commit gate.

## Prohibited claims

Enforced by `paper/scripts/check_banlist.py`; source of truth
`archive/KNOWN_INVALID_RESULTS.md`.

- Any performance figure from the retired residual-Doppler line.
- Any statement that residual Doppler learning, or an evidence gate, improves or degrades
  real link, packet or LR-FHSS performance.
- Any endpoint budget, guard-time or energy conclusion.
- Any claim that the contract is complete, or that it invalidates published work.
- **Any claim of held-out mutations, unseen-fault generalisation, or comprehensive
  coverage.** Withdrawn after review; see `CLAIMS.md`. The suite demonstrates
  represented-fault regression coverage only.
- Any statement that all nineteen rules have a demonstrated broken fixture — 16 do.
- The obsolete 18-fault and 54-cell denominators; the stale 1095/812/739-line counts; the
  stale 0.31 s runtime.
