# Generalization Campaign — Status (Phase 10)

Date: 2026-07-27
Campaign state: **infrastructure complete, science blocked on data acquisition.**
Frozen Paper 1 at `b529c5e` — untouched, and `git diff -- paper/` is empty.

Scope: software-only. No hardware, RF, USRP, firmware, or over-the-air activity.
Every residual is model-derived with `reference_is_measured_truth = false`. No
packet, error-rate, receiver-acknowledgement, or on-orbit claim exists anywhere
in this campaign.

---

## 1. Phase completion

| Phase | Deliverable | State |
|---|---|---|
| 0 — Unified protocol | `UNIFIED_GENERALIZATION_PROTOCOL.md`; one code path for every cell | ✅ complete |
| 1 — Data acquisition | `satellite_catalog.yaml`, `fetch_tle_catalog.py`, `DATASET_DESIGN.md`, `data/schemas/tle_data_manifest.schema.json` | ✅ prepared · ❌ not executed |
| 2 — Pair-level data model | pair identity, per-pair metrics, `rejected_pairs.csv` with reasons | ✅ implemented |
| 3 — Models | zero, mean bias, median bias, linear bias-rate, stale-age ridge, full ridge | ✅ implemented |
| 4 — Target-specific learnability | `TARGET_SPECIFIC_LEARNABILITY.csv` + bootstrap CI + sign test | ✅ implemented · ⛔ blocked |
| 5 — Cross-satellite matrix | matrix CSV + F1/F2/F3 figures | ✅ implemented · ⛔ blocked |
| 6 — Reject sensitivity | `REJECT_SENSITIVITY_REPORT.md`, full re-run per threshold + F4 | ✅ implemented · ⛔ blocked |
| 7 — Tail-aware gating | `TAIL_AWARE_GENERALIZATION_REPORT.md`, 5 objectives + agreement + F5 | ✅ implemented · ⛔ blocked |
| 8 — Interpretation | `GENERALIZATION_CLAIM_MATRIX.md` pre-registered, 4 cases | ✅ pre-registered |
| 9 — Paper 1+ outputs | master plan, figure plan, paper outline | ✅ drafted, story deferred |
| 10 — Testing | `tests/test_multisat_generalization.py` | ✅ 22 tests |

**Single blocking dependency: Phase 1 acquisition.** Everything downstream is
one command away once an archive exists.

---

## 2. What was actually built this session

**Protocol (Phase 0).** One normative document plus a single code path. The
target validation segment selects the model *and* decides every gate; the test
segment reports consequences only. Transfer cells fit on source-train but
validate and gate on the **target**, which the old BK1→BK2 experiment did not
do. The old cross-transfer numbers are declared superseded in
`metadata.supersedes` and are not reused anywhere.

**Pair-level model (Phase 2).** The accepted TLE pair is now the experimental
unit. Every export carries `pair_id`, both epochs, actual staleness, band, first
and last sample timestamps, per-pair MAE / median / p95 / p99 / max / outage
proxy for both branches, and a `pair_outcome`. Rejected pairs are exported
separately with a `reject_reason`. This is what makes pair-clustered statistics
and tail-aware gates possible at all — both were structurally impossible before.

**Statistics (Phase 4).** Paired pair-level sign test (exact two-sided binomial)
plus a 2000-resample bootstrap CI on the mean per-pair MAE delta. "Learned is
worse in every row" can finally carry an uncertainty instead of being a bare
point estimate.

**Five gate objectives (Phase 7).** MAE, p95, p99, outage proxy, guard cost, all
on validation, all with the same γ, plus a pairwise agreement matrix. No
objective is asserted superior. A degenerate zero-baseline metric records
`closed`, never a false open.

**Reject sweep (Phase 6).** Each threshold re-runs the *entire* cell — rebuild,
refit, reselect, regate, re-evaluate — not just the pair count, so the sweep
answers the learnability question rather than only the retention question. A
decision table is committed in advance, including the outcome where the answer
is "yes, screening manufactured the result".

**Acquisition (Phase 1).** Catalog-driven fetcher reusing the existing
Space-Track helpers. 4 regimes, 8 slots, 11 requested objects. `--plan` prints
the plan without touching the network; without credentials nothing downloads and
the script exits non-zero.

---

## 3. Verification

| Check | Result |
|---|---|
| `pytest tests/test_multisat_generalization.py` | ✅ **22 passed** |
| `pytest tests/test_slides_claims.py` | ✅ 6 passed |
| `pytest tests/test_paper1_software_extension.py` | ✅ 6 passed |
| `uvx ruff check exp14 + test` | ✅ All checks passed (only the pre-existing project-level `'select' -> 'lint.select'` warning) |
| `git diff -- paper/` | ✅ empty — frozen manuscript and slides untouched |
| Runner, empty state | ✅ `insufficient_data`, `dry_run: true`, `satellites_found: 0`, empty CSVs |
| Figure generator, empty state | ✅ refuses to render: *"0 satellite(s) < 3 required"* |
| `fetch_tle_catalog.py --plan` | ✅ 8 slots / 11 objects / 4 regimes, no network contact |

### Populated-path verification

Contract tests that are vacuous on empty data were re-run against a **populated**
run to confirm the invariants actually hold: 3 satellites, 27 evaluated cells,
3240 pair rows, both gate branches exercised, all 22 tests passed. The dry-run
artifacts were then regenerated, and the committed state is the real
`insufficient_data` one.

That populated run used **synthetic** TLE histories written to a scratchpad. It
is a code-path check on fabricated orbits, is not committed, and carries no
physical meaning whatsoever. No synthetic number appears in any repository
artifact.

---

## 4. Scientific status — unchanged

**No new scientific result was produced, and none can be until data lands.**

| Question | Status |
|---|---|
| Does residual learning generalize across satellites? | Unanswerable — 0 usable archives; 2 same-family objects known from reports |
| Does target-specific training help? | Not re-derived under the unified protocol |
| Does cross-satellite transfer fail? | Old numbers superseded; new ones not computed |
| Does the gate refuse unsafe transfers? | Not re-tested |
| Did screening manufacture the negative result? | **Still open.** The sharpest attack on Paper 1 remains unanswered |
| Do tail-aware gates agree with MAE? | Not evaluated |

The frozen Paper 1 conclusion stands exactly as published, with exactly the
limitations it already discloses.

---

## 5. Next action

1. Obtain Space-Track credentials.
2. `uv run .../fetch_tle_catalog.py` — acquire ≥ 6 satellites over ≥ 3 regimes.
3. Validate `data_manifest.json` against the schema; run the `DATASET_DESIGN.md`
   §7 acceptance checks. Below 6 satellites or 3 regimes, stay in dry run and do
   not use the word "generalization".
4. Re-derive BK1→BK1, BK2→BK2, BK1→BK2, BK2→BK1 under the unified protocol and
   record protocol-effect deltas against the frozen paper.
5. Run Phases 4–7 (one command), then select the Phase 8 case from the
   pre-registered claim matrix — **after** seeing results.

---

## 6. Open risks

1. **Acquisition may never happen.** No credentials in this workspace. The
   campaign then stays permanently in dry run; nothing will be fabricated to
   fill the gap.
2. **The re-derived BLACK KITE cells may disagree with the frozen paper.** Any
   difference is a protocol effect and is reported as such; the frozen paper is
   not edited to match, and whether it needs a correction note is a separate
   decision.
3. **Phase 6 may invalidate the negative finding.** The pre-committed decision
   table exists precisely so that outcome is reportable rather than negotiable.
4. **Fewer than 6 obtainable satellites.** Then the work is a transfer study
   between named objects, not a generalization study, and must be titled that
   way.
5. **The P1 Table I wording defect** from the previous audit is still open in
   the frozen paper: the cross rows used a 150 Hz screen, 7 features, and
   test-set selection. No result changes, and the fix belongs to the next
   natural paper pass alongside a page-budget trim.
