# Dataset Qualification Report

Date: 2026-07-27 (attempt 3 — real acquisition, post-debug)
Verdict: **DATASET QUALIFIED** — with BLACK KITE Phase-0 re-derivation still
blocked, and two data-integrity defects to clear before the science rerun.

Scope: software-only orbital metadata. `reference_is_measured_truth = false`.
No hardware, RF, USRP, firmware, or over-the-air activity. No packet,
error-rate, receiver-acknowledgement, or on-orbit content. No credential value
was printed, logged, or committed at any point. No target-specific,
cross-satellite, or reject-sensitivity science was run.

---

## 1. Verdict

Computed by `qualify_dataset.py` (exit 0) over 9 ingested objects:

| Check | Required | Observed | Result |
|---|---:|---:|:--:|
| Retained satellites | ≥ 6 | **7** | ✅ |
| Distinct regimes among retained | ≥ 3 | **5** | ✅ |
| Retention rule correctly applied | invariant | 9 ingested → 7 retained, 2 dropped | ✅ |

Retained: `NORAD25544` (ISS), `NORAD56726` (IRIDIUM 181), `NORAD56727`
(IRIDIUM 177), `NORAD61594` (ONEWEB-0015), `NORAD66514` (SENTINEL-6B),
`NORAD66704` (FLOCK 4H 1), `NORAD66705` (FLOCK 4H 2).

Dropped: `NORAD100001` (STARLINK-38128), `NORAD100002` (STARLINK-37711) —
4.5-day histories, 0 supported bands.

Regime coverage among retained:

| Regime (derived from ingested elements) | Satellites |
|---|---:|
| alt300-500 km / inc0-60° | 1 |
| alt500-700 km / inc60-90° | 1 |
| alt500-700 km / inc90-100° | 2 |
| alt700-900 km / inc60-90° | 1 |
| alt900-1400 km / inc60-90° | 2 |

**Thresholds were not weakened.** `MIN_SATELLITES=6`, `MIN_REGIMES=3`,
`MIN_BANDS_PER_SATELLITE=2`, `MIN_PAIRS_PER_SPLIT=3` are unchanged, and a test
asserts their values.

---

## 2. Implementation audit — the code was stricter than the preregistration

The first run reported FAIL despite 7 retained and 5 regimes. Cause: a
dataset-level check that has no basis in the preregistered rule.

**Before:**

```python
"min_bands_per_satellite": {
    ...
    "pass": bool(per_sat) and len(retained) == len(per_sat),   # ALL must pass
},
```

This required **every ingested satellite to be retained**, so acquiring one weak
candidate could fail an otherwise-qualifying dataset. The preregistered rule is
a *retention* rule: satellites failing the per-satellite band test are simply
dropped, and qualification is judged on what remains.

**After** — the rule is now exactly as preregistered, in a testable pure
function `evaluate_qualification()`:

- `retained` = satellites with ≥ `MIN_BANDS_PER_SATELLITE` supported bands,
  where a band counts only with ≥ `MIN_PAIRS_PER_SPLIT` train **and**
  validation **and** test pairs
- `qualified` = `len(retained) ≥ MIN_SATELLITES` **and** distinct regimes among
  **retained** ≥ `MIN_REGIMES`
- the third check became `retention_rule_applied`: an *invariant* that nothing
  below the band rule ever enters the retained set, plus transparency fields
  (`satellites_ingested`, `satellites_retained`, `satellites_dropped`,
  `dropped_keys`)

Only the aggregation logic changed. No constant, band definition, or outcome
criterion was touched.

Tests added (`tests/test_multisat_generalization.py`):

| Test | Asserts |
|---|---|
| `test_preregistered_thresholds_are_unchanged` | 6 / 3 / 2 / 3 |
| `test_nine_ingested_seven_retained_three_regimes_qualifies` | the real shape → PASS |
| `test_nine_ingested_five_retained_fails` | 5 retained → FAIL |
| `test_seven_retained_but_only_two_regimes_fails` | 2 regimes → FAIL |
| `test_satellite_below_band_rule_cannot_count_toward_retention` | a 1-band satellite is neither retained nor counted toward regimes |
| `test_retention_invariant_rejects_a_corrupted_retained_flag` | a forced-retained 1-band satellite fails the invariant |

---

## 3. Outstanding blockers before the science rerun

| # | Blocker | Effect |
|---|---|---|
| **B1** | BLACK KITE-1/-2 not acquired | Phase-0 re-derivation of the frozen Paper 1 cells impossible; see `BLACK_KITE_ACQUISITION_DEBUG.md` |
| **B2** | Every history ingested twice (JSON + TLE, dedup fails on epoch precision) | record counts and pair counts inflated ~2×; violates the one-pair-one-observation rule |
| **B3** | One stored response is a rate-limit error, not data | `oneweb_0015_61594/satcat_61594.json`; needs re-fetch |

B2 and B3 are detailed in `DATASET_QUALIFICATION_DEBUG_REPORT.md` §4a. The
qualification verdict is robust to B2 (retained objects hold 638–46 888 distinct
solutions after dedup, still far above every threshold), but the per-satellite
statistics reported in the debug table are inflated until it is fixed.

---

## 4. Deliverables

| Deliverable | State |
|---|---|
| `dataset_qualification.csv` | ✅ 54 rows, 9 satellites × 6 bands |
| `dataset_qualification.json` | ✅ machine-readable passing verdict |
| `fig_dataset_coverage.pdf/png` | ✅ emitted |
| `DATASET_QUALIFICATION_DEBUG_REPORT.md` | ✅ full per-object/per-band table |
| `BLACK_KITE_ACQUISITION_DEBUG.md` | ✅ root-cause analysis |

---

## 5. Next action

**Do not start target-specific or cross-satellite science yet.** In order:

1. Fix B2 (single-format ingestion or epoch-tolerant dedup) and re-run
   qualification to obtain honest per-satellite statistics.
2. Throttle the fetcher and add response validation (B3), then re-fetch the
   corrupted satcat file.
3. Run the credentialed BLACK KITE diagnostic in
   `BLACK_KITE_ACQUISITION_DEBUG.md` §6 and, if recoverable, fetch BK1/BK2.
4. Only then: Phase-0 re-derivation of BK1→BK1, BK2→BK2, BK1→BK2, BK2→BK1,
   followed by the full matrix.

If BLACK KITE proves unrecoverable, the matrix may proceed on the heterogeneous
7-satellite set alone, and the paper must state plainly that the frozen Paper 1
objects could not be re-derived under the unified protocol. No substitute
satellite will be put in their place.
