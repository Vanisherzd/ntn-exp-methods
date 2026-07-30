# Final dossier — workshop-salvage loop

Generated 2026-07-31. Numbers are from `evaluation/results/final_summary.json`; the paper
build fails if it quotes a value that artifact does not carry.

## 1. Final title

> **Beyond Chronological Splits: A Deployment-Causality and Falsifiability Contract for
> Learning-Assisted Satellite Communication Software**

Retained. R6 assessed it as accurate for what the paper delivers and judged
"Falsifiability" earned by real machinery (L3.2 canary-effectiveness, Table I's
clean+red / clean-only distinction, the 16/19 disclosure). Its only concrete objection was
that the manual line breaks did not hold, orphaning "A" — rebroken.

## 2. Final one-sentence thesis

> Orbit-Evidence turns deployment-time availability, row membership, model-state and
> statistical-unit assumptions into executable CI checks for satellite communication
> experiments; a curated regression suite demonstrates those checks on seventeen known fault
> classes that chronological ordering alone is not designed to detect.

## 3. The three contributions

1. **A deployment-causality threat model and contract.** Six protected objects — decision
   time, feature availability, row membership, label closure, state channels, statistical
   units — as **19 executable rules** in four mechanically checkable layers: availability and
   closure (L1), physical and scheduling validity (L2), model-state causality (L3),
   statistical independence and reproducibility (L4).
2. **Orbit-Evidence, an implementation.** A dependency-light toolkit, **833 lines** across
   four modules, `numpy` only: visible-pass scheduling, freeze-then-label row registry,
   reference-ensemble labelling with published uncertainty, canaries over six state channels,
   and seed, provenance and statistical-unit controls.
3. **A curated fault-injection regression evaluation.** 17 curated fault classes in two
   minimal pipelines and three deterministic environments. Reported as **represented-fault
   regression coverage**, not sensitivity and not generalisation.

## 4. Final evaluation counts

| quantity | value | artifact field |
|---|---|---|
| contract rules | 19 | `rule_count` |
| curated fault classes | 17 | `fault_class_count` |
| deterministic environments | 3 (PCG64, SFC64, Philox) | `environment_count` |
| conditions per environment | 18 (17 faults + clean) | `conditions_per_environment` |
| injected fault-environment cells | 51 | `injected_cell_count` |
| **distinct injected computations** | **17** — the environment axis is inert for 14 of 17 | measured |
| clean reference paths | 3 | `clean_path_count` |
| chronological baseline | **2/17**, measured not asserted | `chronological_detected_count` |
| contract | **17/17**, identical in all 3 environments | `contract_detected_count` |
| clean-path rule firings | 0 | `clean_false_halt_count` |
| rules with a demonstrated red fixture | **16 of 19** | `detectors_with_red_fixture` |
| rules with none | L2.2, L2.3, L4.5 | `detectors_without_red_fixture` |
| L4.7 clean false-halt rate | **19/450 = 0.042**, Wilson [0.027, 0.065], nominal α = 0.05 | `l47_calibration` |
| L4.7 injected detection | 150/150 | `l47_calibration` |
| discarded fixed-threshold null size | 0.17 at 8 groups of 3 (0.00 at this fixture's 96) | `l47_calibration` |
| runtime | under 2 s; under 30 ms per condition — both **bounds**, both gated | `runtime_seconds` |
| toolkit / test suite | 833 / 877 lines | `source_loc`, `test_suite_loc` |
| tests | **51** passing | `test_count` |

## 5. Exact limitations, as the paper states them

- **The faults and the rules share an origin.** 17/17 measures detector *reachability*, not
  mutation adequacy. Only one fault was specified before any detector for it existed and left
  untouched, far too few to support a claim about faults the suite lacks — so none is made.
- **Injection is at contract-input level; the fixtures are check-scoped.** Of 17 mutated
  objects only **six** reach more than one consumer. For the other **eleven** the object is
  consumed by its own detector alone, so those conditions show a rule firing on a broken
  input, not catching a defect inside a working pipeline. This is the sharpest limit.
- **L4.3 still ships the uncalibrated construction the paper criticises** — a fixed 0.2
  correlation threshold gated on a self-reported flag, null size 0.17 at eight groups of
  three. Disclosed, not repaired: editing a detector after its outcome is known is precisely
  what voided L4.7's standing.
- **Two objects the contract names but does not check.** No rule detects covariate-coupled
  label missingness (found by an *ad hoc* thresholded diagnostic, never promoted). And `t_d`
  is declared, not checked; L1.2 enforces a necessary-not-sufficient catalogue clock.
- **Three rules fire in no condition** (L2.2, L2.3, L4.5).
- **The case studies are retrospective accounts, not executed runs** — both predate the
  released contract, no artifact survives for the second, and they are not independent of the
  coverage matrix.
- **Axes of variation are narrow.** Both fixtures from one programme; environments differ in
  generator family alone.
- **No RF, packet-level, deployed-system or learned-method result** anywhere.

## 6. Reviewer verdict table

| reviewer | scope | verdict | BLOCKERs |
|---|---|---|---|
| R3F | experimental methodology | WEAK ACCEPT | none |
| R4F | artifact / reproducibility | WEAK ACCEPT | none |
| R5 | adversarial reject advocate | WEAK REJECT → **WEAK ACCEPT** (R5V) | none remaining |
| R6 | six-page camera-ready | WEAK ACCEPT, **2 blockers** | cleared |
| R5V | verification of R5's six items | WEAK ACCEPT, *no remaining rejection argument* | **NONE** |
| R6V | verification of R6's blockers | WEAK ACCEPT, 5 blockers found | **all 5 cleared** |

All six independently described the contribution as an executable deployment-causality
contract with a curated regression suite. **None described it as an internal bug report** —
the framing test the previous round failed.

## 7. BLOCKER / MAJOR resolutions

No reviewer raised a scientific BLOCKER at any point in this loop.

**MAJORs, all resolved.** Full detail in `REVIEW_LEDGER.md`.

| # | finding | resolution |
|---|---|---|
| 1 | The sentence bounding the evaluation understated its own weakness 3–5×: it conceded two detector-local injections, the true count is eleven | measured count stated; criterion named |
| 2 | L4.3 still ships the fixed threshold the paper criticises | disclosed with measured null-size curve; not repaired, and the reason given |
| 3 | No rule detects covariate-coupled missingness, yet it is called "the harder failure" | named as a gap |
| 4 | "plus several written for propositions no predecessor detector covered" restated the withdrawn claim in words the banlist missed | deleted |
| 5 | **Claim gate defeatable three ways** without touching a detector | all closed, 19 regression tests |
| 6 | `matrix_sha256` was permanently unmatchable (hashed embedded wall-clock) and its divergence hidden | hashes the timing-stripped result; compared |
| 7 | Scheduler: provenance claimed in prose, implemented nowhere; one solver parameter fixed, siblings not | `provenance()` + tests; all three swept |
| 8 | §V asserted executed detection that `ARTIFACTS.md` denied | restated as retrospective accounts |
| 9 | A case-study defect attributed to L4.7 with no record anywhere | removed |
| 10 | Fig. 1's caption contradicted the 2/17 headline | fixed — **on both surfaces this time** |
| 11 | The missingness gap misdescribed as "found by inspection" | corrected, with the banlist's mandated framing, now gate-enforced |
| 12 | 51/51 offered as a coverage denominator while the axis is inert for 14/17 | 17 distinct computations; dead `Env` fields deleted |
| 13 | Fig. 1 at 2.8–5.1 pt, Fig. 3 at 3.2–4.5 pt | rebuilt; **nothing renders below 6.0 pt** |
| 14 | Wilson interval mixed two conventions | uncorrected [0.027, 0.065], bound to the artifact |
| 15 | `build_label`'s COMPLETE conflated checked / unchecked / non-finite | five statuses, each meaning one thing |
| 16 | `latex_errors` invariant never fired (`-file-line-error` drops the `! ` prefix) | both forms matched |
| 17 | No availability statement; ref [8] had no venue | added; `@article` with pages |

**Two I introduced and fixed myself:** the claim-gate tests made `make gate` take seven
minutes by copying the repo 17 times, in a paper claiming per-commit affordability (now 38 s
for 51 tests); and the withdrawal-context exemption initially let a figure exempt itself,
because a TikZ block has no blank lines.

## 8. Final repository tree

```
paper/          14   manuscript, figures, tables, submission docs, Makefile, scripts
src/            10   orbit_evidence: pass_scheduler, causal_registry, label_ensemble,
                     experiment_contract
tests/           5   regression, fault_injection, fixtures
evaluation/     12   contract layers, baseline, matrix runner, results, pre-registration
docs/            5   CASE_STUDIES, DEVELOPMENT, FAILURE_TAXONOMY,
                     FUTURE_MEASUREMENT_PROTOCOL, REPRODUCIBILITY
scripts/         2   compare_summaries.py, __init__.py
submission_
  finalization/ 15   this loop's records
archive/       681   stopped research, hardware validation, retired manuscripts,
                     KNOWN_INVALID_RESULTS.md
(root)           4   README.md, Makefile, pyproject.toml, .gitignore
```

**Not created, deliberately:** `evaluation/configs/` and `paper/sections/` would be empty
decoration. **`LICENSE` is absent and was not invented** — choosing one is the author's
decision, not a finalization step. This is the one item in the requested target tree that is
intentionally unmet.

## 9. Branch and SHAs

| | |
|---|---|
| active branch | `submission/orbit-evidence-workshop` |
| local HEAD | `9fc5d7d` (33 commits ahead of `main`) |
| remote HEAD | `9fc5d7d` — **matches local** |
| `main` | `9e3380c`, **untouched and not pushed**; `origin/main` is `31da77b`, 25 behind |

## 10. Preserved archive branches and tags

| ref | why preserved |
|---|---|
| `main` | protected. **25 commits ahead of `origin/main`** — pre-existing, not created here |
| `archive/residual-learning-stop-2026-07` | 2 commits reachable from nowhere else, no tag at tip. **Local only — the largest archival risk in this repository** |
| `exp15-visible-causal-rebuild` | 2 unique commits; the pre-registration tag is an *ancestor*, not the tip |
| `origin/claude/leo-dtf-experiment-prep-ksnesg` | **18 commits not in this branch**: LR1121 firmware, USRP B210 monitor, Doppler emulator, CI. Unique work, untouched |

**23 tags, none deleted.** All `stop/*`, `evidence/*`, pre-registration and `archive/*` tags
intact. Two added: `stop/exp15-visible-causal-rebuild-2026-07` (makes the failing-gate commit
reachable by tag) and `paper/orbit-evidence-workshop-review-ready-2026-07`.

## 11. Deleted branches

**One, local only:** `workshop-controlled-evidence-gate`. Zero unique commits, tip
byte-identical to `main` (9e3380c), ancestor of both `main` and the active branch, 7 tags
contain that commit, no remote counterpart. Deleted with `git branch -d` — not `-D` — so git
would have refused had the premise been wrong. Verified after: commit still exists, 7 tags
still contain it, `main` unchanged.

**No remote branch was deleted. No tag was deleted. No file was deleted.**

## 12. Logical commits

17 on this branch in this loop. Separated as required, with one exception recorded honestly:

| group | commits |
|---|---|
| evidence / claim corrections | `b83aaf2` |
| toolkit contract fixes | `36ac770`, `125ec7d`, `34740ce` |
| manuscript reframing | `5b4c71b`, `017ffe7`, `99d2ef9`, `f7a6945` |
| figure / table updates | `219d818` |
| gate hardening | `98a512c`, `e8fff4b`, `489f22a` |
| tests | `c070841` |
| documentation | `b0a9bc6`, `3899f63`, `585cbe1`, `57e3658` |
| review records | `7b7d0dd`, `e669eba` |
| repository moves | `b08d52c` |

**Recorded rather than hidden:** `3899f63` is labelled `docs:` but carries 241 lines of
manuscript change, because a `git add -A` swept the working tree. History is not rewritten, so
the mislabel stands and is noted here and in `REVIEW_LEDGER.md`.

## 13–14. Paths

- `paper/icc_main.tex` — sole active manuscript entry point
- `paper/icc_main.pdf` — built by `make paper`; **not tracked** (regenerable, `paper/build/`
  and the PDF are gitignored)

No `main.tex`, `main.pdf`, `main(N).pdf` or `icc_main(N).pdf` exists in the active tree. The
two retired manuscripts remain under `archive/retired_manuscript/`.

## 15. Six-page build result

```
pages               6  (want 6)  OK
latex_errors        0  (want 0)  OK
undefined_refs      0  (want 0)  OK
undefined_cites     0  (want 0)  OK
overfull_boxes      0  (want 0)  OK
verify_build: PASS
```

**Figure legibility, measured** across all six pages against a 10 pt body reference: **no
lowercase word renders below 6.0 pt**; the smallest is 6.4 pt in Fig. 2. Before this round
Fig. 1 ran 2.8–5.1 pt and Fig. 3 3.2–4.5 pt. Both of R6's camera-ready blockers are therefore
cleared by measurement rather than by assertion.

## 16. Test and evaluation result

51 tests pass in ~12 s (19 of them two-sided tests of the claim gate itself). Matrix verdict
PASS on all six pre-registered acceptance criteria; 2/17 baseline, 17/17 contract, 0
clean-path firings, verdicts identical across environments.

## 17. Double-run reproducibility

`make gate-twice` passes. **25 summary fields reproduce identically, including
`matrix_sha256` and `commit`.** Only `runtime_seconds` and `runtime_ms_per_condition` vary,
and they are printed rather than silently excluded.

## 18. Banlist result

```
check_banlist: 11 file(s) clean; 11 banned + 17 withdrawn patterns,
               11 artifact numbers bound to the artifact, 6 permitted mention(s)
```

11 files scanned (was 6 — `README.md` and `paper/submission/*.md` were outside the gate while
one of them advertised the gate). Every permitted mention is printed with its reason.
**Verified adversarially:** 11 planted attacks all fire, three of which previously passed.

## 19. Push verification

**Pushed.** Full detail in `PUSH_LOG.md`.

- `submission/orbit-evidence-workshop` — remote HEAD `9fc5d7d` **matches local**
- `archive/residual-learning-stop-2026-07` — **now remote**, closing the archival risk
- `exp15-visible-causal-rebuild` — now remote
- 7 tags: 3 `stop/*`, 1 `evidence/*`, the pre-registration, the pre-finalization safety tag,
  and `paper/orbit-evidence-workshop-review-ready-2026-07`
- `main` untouched and not pushed; **no force-push, no history rewritten**
- `paper/icc_main.pdf` is not tracked (regenerable; `make paper`)

**No submission tag was created** — that awaits explicit human approval.

Two items left for a human, both recorded in `PUSH_LOG.md`: the remote has been **renamed** to
`LEO-PGRL.git` and every push is being redirected, and `main` is 25 commits ahead of
`origin/main` — both predate this loop.

## 20. Recommendation

**READY FOR FLAGSHIP WORKSHOP SUBMISSION**, against the stated threshold:

| condition | status |
|---|---|
| R3F and R4F report no BLOCKER | ✅ both WEAK ACCEPT, none |
| R6 reports no camera-ready BLOCKER | ✅ 2 raised then 5 more on re-verification; **all 7 cleared** (§15) |
| R5's remaining rejection argument limited to external-validity scale | ✅ R5V: *no remaining rejection argument at all* |
| no unresolved scientific MAJOR fixable only with new evidence | ✅ all resolved without new evidence |
| the manuscript explicitly bounds generalisation | ✅ §VI, plus mechanical enforcement |

Two caveats a reader of this dossier should carry:

1. **This is submittability, not acceptance.** The paper rests on a curated regression suite
   whose faults and rules share an author. It says so, in the section where a reader will find
   it. A reviewer preferring independently authored faults may still decline it, and that
   preference is legitimate.
2. **Seven camera-ready blockers were found across two passes, and four of the last five were
   my own damage from holding the paper to six pages** — two figure layers measured below the
   legibility floor because my own check filtered them out, an orphaned float created by
   removing a false claim, and two published reference titles I truncated for space, which made
   them unresolvable. The paper is fixed and the checks that missed them are fixed. But the
   pattern is worth carrying: the page budget was where the errors came from, not the science.
