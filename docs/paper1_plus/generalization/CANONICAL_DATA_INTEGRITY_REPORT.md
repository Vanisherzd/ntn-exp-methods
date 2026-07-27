# Canonical Data Integrity Report

Date: 2026-07-27
Status: **P0-A repaired. P0-B repaired in code; one network action outstanding.**

**No learning science has been run.** No target-specific A→A, no cross-satellite
A→B, no reject-sensitivity study. Not one model has been fitted on real data in
this pass. Everything below is data integrity and dataset qualification.

Scope: software-only orbital metadata, `reference_is_measured_truth = false`.
No hardware, RF, USRP, firmware, or over-the-air activity; no packet,
error-rate, receiver-acknowledgement, or on-orbit content. No preregistered
threshold changed. No NORAD ID fabricated or substituted. No credential value
read, printed, or committed.

---

## 1. P0-A — JSON/TLE double ingestion

### Root cause

`gp_history_<n>.json` and `gp_history_<n>.tle` are **the same element history in
two encodings**. The ingester walked every file in the archive directory and
treated both as independent observation sources.

Deduplication was keyed on `epoch.isoformat()`, but the two paths reconstruct
the epoch differently:

- JSON reads the `EPOCH` text field directly;
- TLE recovers it from the packed epoch field through a floating-point Julian
  date (`jdsatepoch + jdsatepochF` → Unix seconds → `datetime`).

Those disagree in the sub-millisecond digits, so string equality almost never
held and dedup silently failed. Measured overlap before repair: **17 of 638**
distinct epochs for FLOCK 4H 1, **1117 of 46 888** for ISS — i.e. ~97–98 % of
every history was counted twice.

Two visible symptoms, both now explained:

- record counts roughly doubled;
- median inter-TLE gap collapsed to **0.0 h** for six of nine objects, because a
  duplicate sat microseconds from its twin.

### Canonical-input decision

**GP_HISTORY JSON is the sole canonical scientific input.**

The TLE archive remains, unchanged, as:

- an immutable archival copy,
- a provenance/checksum artifact in `fetch_manifest.json`,
- an optional consistency check.

It is **never** ingested as an independent element sequence when a canonical
JSON history exists. `fetch_manifest.json` now records
`canonical_science_input` and `tle_is_archival_only: true` explicitly.
No JSON/TLE merge is attempted — merging two encodings of one history is the
defect, not the fix.

### Canonicalization rules

- deterministic epoch normalization to a **1 ms quantum**, UTC, so the same
  physical element set yields one key regardless of source encoding;
- stable `element_id = NORAD_CAT_ID | normalized_epoch`;
- sort by epoch, then drop repeats by `element_id`, counting them;
- raw record identity, `NORAD_CAT_ID` and `source_path` preserved on every
  retained record.

### Per-satellite before/after

| Satellite | NORAD | raw JSON rows | dup JSON rows | canonical unique | raw TLE rows | TLE used for science | records before | records after | median gap before | median gap after |
|---|---:|---:|---:|---:|---:|:--:|---:|---:|---:|---:|
| ISS (ZARYA) | 25544 | 52538 | 5679 | 46859 | 52538 | **false** | 92659 | **46859** | 0.176 h | **4.518 h** |
| IRIDIUM 181 | 56726 | 3017 | 339 | 2678 | 3017 | **false** | 5347 | **2678** | 0.0 h | **9.982 h** |
| IRIDIUM 177 | 56727 | 3042 | 419 | 2623 | 3042 | **false** | 5243 | **2623** | 0.0 h | **9.735 h** |
| ONEWEB-0015 | 61594 | 1929 | 234 | 1695 | 1929 | **false** | 3393 | **1695** | 0.0 h | **8.000 h** |
| SENTINEL-6B | 66514 | 838 | 111 | 727 | 838 | **false** | 1480 | **727** | 0.0 h | **5.621 h** |
| FLOCK 4H 1 | 66704 | 749 | 135 | 614 | 749 | **false** | 1259 | **614** | 0.0 h | **7.895 h** |
| FLOCK 4H 2 | 66705 | 755 | 120 | 635 | 755 | **false** | 1278 | **635** | 0.0 h | **7.893 h** |
| STARLINK-38128 | 100001 | 11 | 0 | 11 | 11 | **false** | 20 | **11** | 6.083 h | 9.886 h |
| STARLINK-37711 | 100002 | 9 | 0 | 9 | 9 | **false** | 18 | **9** | 0.0 h | 12.927 h |

Machine-readable: `experiments/exp14_multisat_generalization_matrix/ingestion_audit.csv`.

**Every "median gap after" now reflects a plausible GP update cadence
(4.5–12.9 h) and none collapses toward zero.** The 5679 intra-JSON duplicates on
ISS are genuine repeated GP publications within 1 ms, removed by `element_id` —
they are not a JSON/TLE artifact.

### Pair-level independence restored

Contract tests (`tests/test_multisat_generalization.py`) prove structurally:

| Test | Proves |
|---|---|
| `test_json_plus_tle_archive_does_not_double_the_record_count` | the archival TLE copy adds no observations; deleting it changes nothing |
| `test_duplicate_json_rows_collapse_to_one_canonical_element` | duplicated GP rows yield one canonical element and are counted |
| `test_element_id_is_norad_plus_normalized_epoch` | epochs differing below the quantum share one `element_id` |
| `test_pair_ids_are_unique_and_survive_tle_removal` | `pair_id` unique, and pair count invariant to the TLE copy |
| `test_one_reference_element_yields_at_most_one_pair` | one reference element → exactly one pair |
| `test_sign_test_n_counts_pairs_not_sample_rows` | sign-test N equals unique evaluated pair IDs, not 24× that |
| `test_bootstrap_resamples_pairs_not_samples` | every bootstrap draw is of size `n_pairs` |

The 24 in-pass samples remain children of their pair and are never independent
observations.

---

## 2. P0-B — API error payloads treated as data

### Root cause

Space-Track returns errors as HTTP 200 with a JSON **list** body:

```json
[{"error": "You've violated your query rate limit. ..."}]
```

That passes `isinstance(parsed, list)`, then every row is discarded by a
`NORAD_CAT_ID` field filter, producing an empty list **indistinguishable from
"object not found"**. The body was also written to disk and SHA256-checksummed
into `fetch_manifest.json` as though it were a scientific archive.

### Rate-limit incident, 2026-07-27 06:54Z

Three queries per object plus one resolution per slot — roughly 35 requests in
~30 s against a documented 30/min limit. The 27th archive write, ONEWEB-0015's
SATCAT, was refused. The **next** requests in the run were the two BLACK KITE
resolutions, which is the most likely reason both were dropped silently.

Audit of all preserved responses: 18 JSON bodies, **1 corrupted**, all nine
`gp_history` archives valid.

### Validation rules now enforced

Every response is classified before it is accepted, into exactly one state:
`VALID`, `EMPTY`, `RATE_LIMITED`, `API_ERROR`, `PARSE_ERROR`,
`IDENTITY_MISMATCH`, `UNRESOLVED`.

| Response | Must satisfy |
|---|---|
| SATCAT | parses; no `error` key; non-empty; `NORAD_CAT_ID` and `OBJECT_NAME` present; resolved identity matches the requested NORAD |
| GP_HISTORY JSON | parses; no `error` key; non-empty; every row carries `NORAD_CAT_ID` and `EPOCH`; all rows belong to the requested NORAD |
| TLE | not a rate-limit/markup/JSON body; non-empty; contains at least one TLE line-1 record |

Invariants:

- **An API error is never converted into an empty/not-found result.** A
  rate-limit body classifies `RATE_LIMITED`, never `EMPTY`.
- **An error body is never checksummed as a scientific archive.** Only `VALID`
  bodies are written to the archive path and entered in the manifest.
- A diagnostic copy is retained under `_quarantine/` with an `.invalid`
  suffix carrying its state, excluded from ingestion and from the manifest.
- A transport exception becomes `API_ERROR`, not silence.

### Throttling and retry

`RequestScheduler` (`spacetrack_client.py`): default **18 requests/min**
(headroom below the observed 30/min limit), paced so requests never burst;
bounded retries (default 4) on `RATE_LIMITED` only, with increasing backoff
(20 s → 40 s → 80 s …); retry exhaustion returns an explicit `RATE_LIMITED`
state rather than a false empty. Configurable via `--requests-per-minute` and
`--max-retries`. Request status is printed; credential handling is unchanged and
no credential value is ever printed.

Caching: a cached body is reused **only if it classifies VALID**; a cached error
payload never suppresses a re-fetch — which is precisely how the corrupted
OneWeb SATCAT would otherwise have persisted indefinitely.

Mocked tests cover: rate-limit → retry → eventual success (with increasing
backoff), retry exhaustion → explicit `RATE_LIMITED`, pacing interval, transport
exception → `API_ERROR`, valid cache reused, error cache re-fetched.

---

## 3. Corrupted OneWeb SATCAT — disposition

`dataraw/spacetrack/oneweb_0015_61594/satcat_61594.json` classified
`RATE_LIMITED` and was **quarantined**, not deleted:

```
oneweb_0015_61594/_quarantine/satcat_61594.json.RATE_LIMITED.invalid
oneweb_0015_61594/_quarantine/README.txt
```

`fetch_manifest.json` was rewritten to drop it from the file list and now
carries `quarantined_responses: true`. A contract test asserts no manifest
references a quarantined path and that every archived `satcat_*.json` classifies
`VALID`.

**Re-fetch is outstanding** — it requires credentials, which are not present in
this environment. The OneWeb scientific result was **not** altered on the basis
of the corrupted payload; the only consequence is that ONEWEB-0015 still
displays as `TBA - TO BE ASSIGNED`, because its authoritative name lives in the
missing SATCAT record. Its `gp_history` archive is valid and unaffected, so its
1695 canonical elements and full 6-band support stand.

---

## 4. BLACK KITE recovery — **not performed**

The documented diagnostic could not be run: **no Space-Track credentials exist
in this environment** (presence probe only; no value read or printed). The
hardened fetcher was invoked and exited 2 with:

> No Space-Track credentials found (SPACETRACK_USERNAME / SPACETRACK_PASSWORD or
> `.env.spacetrack`). Nothing was downloaded and no result is claimed.

Therefore, for both **BLACK KITE-1 (66741)** and **BLACK KITE-2 (68474)**:

| Item | State |
|---|---|
| SATCAT identity | not queried — no credentials |
| GP_HISTORY response validity | not queried |
| record count / epoch span / median gap | unavailable |
| SHA256 archive manifest | none |
| API error payload | none (no request made) |

**No substitute satellite was used, and no NORAD ID was invented.** The exact
blocking reason is credential absence, not an API rejection. Once credentials
exist, the three diagnostic queries in `BLACK_KITE_ACQUISITION_DEBUG.md` §6 run
first; with validation and throttling now active, a rate-limit response will be
retried and reported as `RATE_LIMITED` instead of vanishing.

---

## 5. Qualification on canonical data

Reported separately, never merged into one ambiguous state.

### A. Heterogeneous dataset qualification

| Check | Required | Observed | Result |
|---|---:|---:|:--:|
| Retained satellites | ≥ 6 | **7** | ✅ |
| Retained regimes | ≥ 3 | **5** | ✅ |
| Retention rule applied | invariant | 9 ingested → 7 retained, 2 dropped | ✅ |

All seven retained objects support **all six** staleness bands after
canonicalization, with a minimum train-pair count of 275 (FLOCK 4H 1) against a
threshold of 3:

| Satellite | Records | Median gap | Bands supported | Min train pairs |
|---|---:|---:|:--:|---:|
| ISS (ZARYA) | 46859 | 4.518 h | 6/6 | 19702 |
| IRIDIUM 181 | 2678 | 9.982 h | 6/6 | 924 |
| IRIDIUM 177 | 2623 | 9.735 h | 6/6 | 876 |
| ONEWEB-0015 | 1695 | 8.000 h | 6/6 | 568 |
| SENTINEL-6B | 727 | 5.621 h | 6/6 | 290 |
| FLOCK 4H 1 | 614 | 7.895 h | 6/6 | 275 |
| FLOCK 4H 2 | 635 | 7.893 h | 6/6 | 291 |
| STARLINK-38128 | 11 | 9.886 h | 0/6 | — dropped |
| STARLINK-37711 | 9 | 12.927 h | 0/6 | — dropped |

Halving the record counts did not cost a single band. The two Starlink objects
remain dropped for the same reason as before — ~4.5 days of history from a
2026-07-14 launch — which is a coverage limitation, never a learnability
finding.

### B. Paper-1 continuity (BLACK KITE)

| Object | Canonical history | Bands | Phase-0 ready |
|---|:--:|---:|:--:|
| NORAD 66741 (BK1) | ❌ | 0 | ❌ |
| NORAD 68474 (BK2) | ❌ | 0 | ❌ |

Blocking reason: no canonical history for NORAD 66741, 68474.

### Final verdict

```
DATASET QUALIFIED - BLACK KITE CONTINUITY BLOCKED
```

---

## 6. Statement of scientific status

**No learning science has been run at any point in this campaign.** No
target-specific A→A cell, no cross-satellite A→B cell, no reject-sensitivity
sweep, no gate evaluation on real data. No model has been fitted to any real
satellite history. The frozen Paper 1 at `b529c5e` is untouched, and
`git diff -- paper/` is empty.

Phase-0 continuity remains the gate: BK1→BK1, BK2→BK2, BK1→BK2 and BK2→BK1 must
be re-derived under the unified protocol before any Paper 1+ scientific
statement, so that a protocol effect can be distinguished from a real finding.

---

## 7. Next actions, in order

1. Supply Space-Track credentials via environment or a git-ignored
   `.env.spacetrack`.
2. Run the BK diagnostic queries (`BLACK_KITE_ACQUISITION_DEBUG.md` §6) to
   establish whether 66741/68474 resolve.
3. Re-run the hardened fetcher — it will re-fetch the quarantined OneWeb SATCAT,
   skip everything already `VALID`, and report any `RATE_LIMITED` explicitly.
4. Re-run `qualify_dataset.py` and confirm
   `DATASET QUALIFIED - BLACK KITE CONTINUITY QUALIFIED`.
5. Only then begin Phase-0: the four BLACK KITE cells, followed by the full
   matrix.

If BK1/BK2 prove genuinely unrecoverable, the matrix may proceed on the
heterogeneous seven-satellite set alone, and the paper must state plainly that
the frozen Paper 1 objects could not be re-derived under the unified protocol.
No substitute satellite will be put in their place.
