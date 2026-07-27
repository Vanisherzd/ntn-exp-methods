# Paper 1+ Generalization Campaign — Master Plan (Phase 9)

Date: 2026-07-27
Frozen dependency: Paper 1 at commit `b529c5e`. **Not edited by this campaign.**

## Research question

> When does model-derived inter-TLE residual structure generalize across LEO
> satellites, and can a validation-gated endpoint policy safely refuse residual
> learning under satellite/domain shift?

The subject is no longer BLACK KITE. **Cross-satellite generalization is itself
the research problem**, and the frozen Paper 1 result becomes one cell in a
larger matrix.

Scope discipline for the whole campaign: software-only, model-derived inter-TLE
residuals, `reference_is_measured_truth = false`. No hardware, RF, USRP,
firmware, or over-the-air work. No packet, error-rate, receiver-acknowledgement,
or on-orbit claim, in any phase, under any result.

---

## Phase status

| Phase | Deliverable | State |
|---|---|---|
| 0 — Unified protocol | `UNIFIED_GENERALIZATION_PROTOCOL.md`, single code path | ✅ done |
| 1 — Data acquisition | `satellite_catalog.yaml`, `fetch_tle_catalog.py`, `DATASET_DESIGN.md`, manifest schema | ✅ prepared, ❌ not executed (no credentials, no archive) |
| 2 — Pair-level data model | pair identity + per-pair metrics + rejected-pair export | ✅ implemented |
| 3 — Models / baselines | zero, mean bias, median bias, linear bias-rate, stale-age ridge, full ridge | ✅ implemented |
| 4 — Target-specific learnability | `TARGET_SPECIFIC_LEARNABILITY.csv` | ✅ implemented, ❌ blocked on data |
| 5 — Cross-satellite matrix | matrix CSV + 3 figures | ✅ implemented, ❌ blocked on data |
| 6 — Reject sensitivity | `REJECT_SENSITIVITY_REPORT.md`, sweep + figure | ✅ implemented, ❌ blocked on data |
| 7 — Tail-aware gating | `TAIL_AWARE_GENERALIZATION_REPORT.md`, 5 objectives + agreement | ✅ implemented, ❌ blocked on data |
| 8 — Interpretation | `GENERALIZATION_CLAIM_MATRIX.md` (pre-committed) | ✅ pre-registered |
| 9 — Paper 1+ outputs | figure plan, paper outline | ✅ drafted, story deferred |
| 10 — Testing | `tests/test_multisat_generalization.py` | ✅ extended |

**Single blocking dependency for every scientific result: Phase 1 acquisition.**

---

## Critical prerequisite, restated

The old BK1 target-specific and BK1→BK2 transfer experiments used different
reject thresholds (1500 vs 150 Hz), feature counts (10 vs 7), pairing rules,
split structures, and selection procedures. **Their cross-transfer numbers are
not reused anywhere in this campaign.** Before any new claim, BK1→BK1, BK2→BK2,
BK1→BK2 and BK2→BK1 are re-derived from scratch under the unified protocol.

Any difference from the frozen paper is reported as a protocol effect, never as
a new learnability finding, and the frozen paper is not edited to match.

---

## Execution order once data lands

1. `fetch_tle_catalog.py` → acquire ≥ 6 satellites over ≥ 3 regimes.
2. Validate `data_manifest.json` against the schema; run the §7 acceptance
   checks in `DATASET_DESIGN.md`. If ≥ 6 satellites or ≥ 3 regimes fail, stop
   and stay in dry-run state.
3. Re-derive the four BLACK KITE cells under the unified protocol. Record
   protocol-effect deltas against the frozen paper.
4. Phase 4 target-specific learnability across all satellites and staleness.
5. Phase 5 full ordered matrix + 3 figures.
6. Phase 6 reject sweep; apply the pre-committed decision table.
7. Phase 7 gate-objective agreement.
8. Phase 8 select the outcome case (A/B/C/D) from
   `GENERALIZATION_CLAIM_MATRIX.md` **after** seeing results.
9. Phase 9 write the paper against the case that actually occurred.

Steps 3–7 are one command; the pipeline is a single code path by design.

---

## Guardrails

- The Phase 8 outcome case is chosen **after** results, never before. All four
  cases are pre-written so none is easier to write than another.
- A figure is never emitted below the satellite threshold, enforced in
  `make_generalization_figures.py`, so a dry run cannot produce something that
  looks like multi-satellite evidence.
- The test suite asserts that the gate is reproducible from validation alone, so
  a future edit cannot silently let test data decide deployment.
- Any negative outcome for the frozen Paper 1 — particularly a Phase 6 result
  showing the screen manufactured the finding — is reported, not buried.

---

## Risks

| Risk | Mitigation |
|---|---|
| Acquisition never happens (no credentials) | Campaign stays honestly in dry-run; nothing is fabricated |
| Fewer than 6 satellites obtainable | Report as transfer study between named objects; do not use "generalization" |
| Short histories drop long-staleness bands | `usable_staleness_bands_h` per satellite; sparse matrices flagged, not interpolated |
| Re-derived BLACK KITE cells contradict the frozen paper | Reported as a protocol effect with the frozen paper left intact; a correction pass is a separate decision |
| Matrix is mostly `insufficient_pairs` | Reported as a sample-size limitation, never as evidence of unlearnability |
| Screening turns out to manufacture the result | Pre-committed decision table in `REJECT_SENSITIVITY_REPORT.md` §4 |
