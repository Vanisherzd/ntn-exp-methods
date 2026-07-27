# Dataset Qualification Debug Report

Date: 2026-07-27
Scope: qualification debugging only. No target-specific learning, no
cross-satellite learning, no reject-sensitivity science was run. No
pre-registered threshold was changed. Paper 1 and slides untouched.

Source of every number below: the real artifacts
`experiments/exp14_multisat_generalization_matrix/dataset_qualification.{csv,json}`
and the preserved `dataraw/spacetrack/*/` responses. Nothing was inferred from
file size.

All values are orbital metadata with `reference_is_measured_truth = false`; no
measured RF truth is involved and no scientific claim is made.

---

## 1. Acquisition summary

Requested 11 objects across 4 regime slots; **9 histories written**, all in
catalog slot order, between 06:54:25Z and 06:54:54Z:

| Fetched at (UTC) | NORAD | satcat OBJECT_NAME | Archive size |
|---|---:|---|---:|
| 06:54:25 | 25544 | ISS (ZARYA) | 66.86 MB |
| 06:54:28 | 100001 | STARLINK-38128 | 0.01 MB |
| 06:54:30 | 100002 | STARLINK-37711 | 0.01 MB |
| 06:54:33 | 66514 | SENTINEL-6B | 1.07 MB |
| 06:54:37 | 66704 | FLOCK 4H 1 | 0.95 MB |
| 06:54:39 | 66705 | FLOCK 4H 2 | 0.96 MB |
| 06:54:44 | 56726 | IRIDIUM 181 | 3.84 MB |
| 06:54:49 | 56727 | IRIDIUM 177 | 3.87 MB |
| 06:54:54 | 61594 | ONEWEB-0015 | 2.46 MB |

Missing: BLACK KITE-1 (66741), BLACK KITE-2 (68474) — see
`BLACK_KITE_ACQUISITION_DEBUG.md`.

The fetch shows **no truncation**: every slot up to and including
`high_leo_low_drag` completed with regular 2–5 s spacing. The two missing
objects are the final two slots and failed at resolution, not mid-download.

---

## 2. The two failing satellites

**NORAD 100001 (STARLINK-38128) and NORAD 100002 (STARLINK-37711).**
Both retained = false, both with **0 supported bands**.

Root cause: **4.5 days of usable GP history.** Both objects launched
2026-07-14 (satcat `OBJECT_ID` 2026-160A / 2026-160B), and their `gp_history`
begins 2026-07-22. A staleness band needs pairs spanning up to its upper gap
bound, *and* a chronological 60/20/20 split with ≥3 pairs in each of train,
validation and test. Neither is achievable in 4.5 days:

| | 100001 | 100002 |
|---|---|---|
| records | 20 | 18 |
| epoch span | 2026-07-22 → 2026-07-26 (4.499 d) | 2026-07-22 → 2026-07-26 (4.436 d) |
| 8 h band tr/va/te | 12 / **0** / 2 | 8 / **0** / 2 |
| 24 h band tr/va/te | 9 / 2 / 2 | 6 / 2 / 4 |
| 48 h band tr/va/te | 1 / 2 / 2 | 2 / 2 / 2 |
| 72 h band tr/va/te | 0 / 2 / 2 | 0 / 0 / 2 |
| 96 h band | 0 accepted pairs (100 % reject) | 0 accepted pairs (100 % reject) |
| 168 h band | 0 candidate pairs at all | 0 candidate pairs at all |

Every band fails the ≥3-per-split rule; the two longest bands have no accepted
pairs whatsoever. This is a **coverage failure, not a learnability finding**, and
must never be reported as evidence about residual structure.

---

## 3. Full table — all 9 ingested objects

Regimes are derived from ingested elements (altitude × inclination bands), not
from catalog intent. `S` columns are `band_supported` (≥3 train **and** ≥3
validation **and** ≥3 test pairs).

| Satellite | NORAD | Records | Epoch start | Epoch end | Median gap | Regime | S8 | S24 | S48 | S72 | S96 | S168 | #bands | Status |
|---|---:|---:|---|---|---:|---|:--:|:--:|:--:|:--:|:--:|:--:|---:|---|
| ISS (ZARYA) | 25544 | 92659 | 1998-11-20 | 2026-07-26 | 0.176 h | alt300-500 / inc0-60 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 | **retained** |
| IRIDIUM 181 | 56726 | 5347 | 2023-05-22 | 2026-07-26 | 0.0 h | alt700-900 / inc60-90 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 | **retained** |
| IRIDIUM 177 | 56727 | 5243 | 2023-05-22 | 2026-07-26 | 0.0 h | alt500-700 / inc60-90 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 | **retained** |
| ONEWEB-0015 | 61594 | 3393 | 2024-10-24 | 2026-07-26 | 0.0 h | alt900-1400 / inc60-90 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 | **retained** |
| SENTINEL-6B | 66514 | 1480 | 2025-11-17 | 2026-07-26 | 0.0 h | alt900-1400 / inc60-90 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 | **retained** |
| FLOCK 4H 1 | 66704 | 1259 | 2025-12-18 | 2026-07-26 | 0.0 h | alt500-700 / inc90-100 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 | **retained** |
| FLOCK 4H 2 | 66705 | 1278 | 2025-12-18 | 2026-07-26 | 0.0 h | alt500-700 / inc90-100 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 | **retained** |
| STARLINK-38128 | 100001 | 20 | 2026-07-22 | 2026-07-26 | 6.083 h | alt300-500 / inc60-90 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 0 | **dropped** |
| STARLINK-37711 | 100002 | 18 | 2026-07-22 | 2026-07-26 | 0.0 h | alt300-500 / inc60-90 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 0 | **dropped** |

### Train / validation / test pairs and reject rate, by band

| Satellite | Band | Accepted | Rejected | Reject % | train | val | test |
|---|---:|---:|---:|---:|---:|---:|---:|
| ISS 25544 | 8 h | 88150 | 137 | 0.16 | 54052 | 15657 | 18441 |
| | 24 h | 90802 | 1461 | 1.58 | 55054 | 16720 | 19028 |
| | 48 h | 88111 | 4245 | 4.60 | 53347 | 16463 | 18301 |
| | 72 h | 84182 | 8097 | 8.77 | 50799 | 16046 | 17337 |
| | 96 h | 79823 | 12584 | 13.62 | 47952 | 15597 | 16274 |
| | 168 h | 66095 | 26340 | **28.50** | 38929 | 14056 | 13110 |
| IRIDIUM 181 56726 | 8 h | 3798 | 0 | 0.00 | 1816 | 688 | 1294 |
| | 24 h | 5158 | 0 | 0.00 | 2683 | 966 | 1509 |
| | 48 h | 5210 | 6 | 0.12 | 2698 | 991 | 1521 |
| | 72 h | 5173 | 12 | 0.23 | 2676 | 982 | 1515 |
| | 96 h | 5275 | 20 | 0.38 | 2736 | 1006 | 1533 |
| | 168 h | 5271 | 47 | 0.88 | 2722 | 1012 | 1537 |
| IRIDIUM 177 56727 | 8 h | 3757 | 0 | 0.00 | 1731 | 712 | 1314 |
| | 24 h | 5087 | 2 | 0.04 | 2660 | 949 | 1478 |
| | 48 h | 5059 | 4 | 0.08 | 2641 | 943 | 1475 |
| | 72 h | 5084 | 18 | 0.35 | 2644 | 949 | 1491 |
| | 96 h | 5166 | 34 | 0.65 | 2688 | 981 | 1497 |
| | 168 h | 5091 | 126 | 2.42 | 2613 | 987 | 1491 |
| ONEWEB-0015 61594 | 8 h | 2672 | 6 | 0.22 | 1249 | 746 | 677 |
| | 24 h | 3214 | 94 | 2.84 | 1572 | 830 | 812 |
| | 48 h | 3117 | 214 | 6.42 | 1462 | 839 | 816 |
| | 72 h | 3005 | 308 | 9.30 | 1362 | 833 | 810 |
| | 96 h | 2987 | 376 | 11.18 | 1326 | 837 | 824 |
| | 168 h | 2789 | 568 | 16.92 | 1126 | 839 | 824 |
| SENTINEL-6B 66514 | 8 h | 996 | 0 | 0.00 | 588 | 244 | 164 |
| | 24 h | 1403 | 0 | 0.00 | 813 | 332 | 258 |
| | 48 h | 1399 | 0 | 0.00 | 799 | 336 | 264 |
| | 72 h | 1386 | 15 | 1.07 | 790 | 336 | 260 |
| | 96 h | 1394 | 28 | 1.97 | 790 | 336 | 268 |
| | 168 h | 1365 | 31 | 2.22 | 755 | 336 | 274 |
| FLOCK 4H 1 66704 | 8 h | 931 | 2 | 0.21 | 558 | 230 | 143 |
| | 24 h | 1191 | 0 | 0.00 | 726 | 267 | 198 |
| | 48 h | 1222 | 5 | 0.41 | 737 | 275 | 210 |
| | 72 h | 1203 | 6 | 0.50 | 724 | 275 | 204 |
| | 96 h | 1224 | 8 | 0.65 | 735 | 275 | 214 |
| | 168 h | 1180 | 32 | 2.64 | 689 | 275 | 216 |
| FLOCK 4H 2 66705 | 8 h | 962 | 6 | 0.62 | 587 | 230 | 145 |
| | 24 h | 1211 | 6 | 0.49 | 727 | 273 | 211 |
| | 48 h | 1229 | 12 | 0.97 | 739 | 277 | 213 |
| | 72 h | 1224 | 16 | 1.29 | 735 | 278 | 211 |
| | 96 h | 1224 | 14 | 1.13 | 732 | 281 | 211 |
| | 168 h | 1202 | 28 | 2.28 | 702 | 281 | 219 |
| STARLINK-38128 100001 | 8 h | 14 | 0 | 0.00 | 12 | **0** | 2 |
| | 24 h | 13 | 4 | 23.53 | 9 | 2 | 2 |
| | 48 h | 5 | 6 | 54.55 | 1 | 2 | 2 |
| | 72 h | 4 | 3 | 42.86 | 0 | 2 | 2 |
| | 96 h | 0 | 4 | **100.00** | 0 | 0 | 0 |
| | 168 h | 0 | 0 | — | 0 | 0 | 0 |
| STARLINK-37711 100002 | 8 h | 10 | 0 | 0.00 | 8 | **0** | 2 |
| | 24 h | 12 | 4 | 25.00 | 6 | 2 | 4 |
| | 48 h | 6 | 6 | 50.00 | 2 | 2 | 2 |
| | 72 h | 2 | 6 | 75.00 | 0 | 0 | 2 |
| | 96 h | 0 | 4 | **100.00** | 0 | 0 | 0 |
| | 168 h | 0 | 0 | — | 0 | 0 | 0 |

### Orbital summary

| Satellite | Mean alt [km] | Mean inc [deg] | Mean ecc | Mean B\* |
|---|---:|---:|---:|---:|
| ISS 25544 | 388.5 | 51.637 | 0.000683 | 2.08e-4 |
| IRIDIUM 181 56726 | 743.5 | 86.623 | 0.000231 | 1.46e-4 |
| IRIDIUM 177 56727 | 628.6 | 86.209 | 0.000238 | 2.38e-4 |
| ONEWEB-0015 61594 | 1114.7 | 87.662 | 0.000286 | **−2.98e-2** |
| SENTINEL-6B 66514 | 1335.9 | 66.041 | 0.000841 | 1.49e-4 |
| FLOCK 4H 1 66704 | 507.1 | 97.425 | 0.000243 | 3.58e-4 |
| FLOCK 4H 2 66705 | 506.5 | 97.424 | 0.000188 | 4.04e-4 |
| STARLINK-38128 100001 | 334.2 | 70.001 | 0.000451 | 4.96e-4 |
| STARLINK-37711 100002 | 334.0 | 70.000 | 0.000448 | 1.52e-3 |

---

## 4. Secondary findings (recorded, not acted on as science)

1. **ISS 168 h reject rate is 28.5 %** — by far the highest of any retained
   object, consistent with a frequently manoeuvring, low-altitude, high-drag
   target. This is exactly the population Phase 6 exists to study. It is
   *recorded here only*; no reject-sensitivity science was run.
2. **ONEWEB-0015 has mean B\* = −0.0298**, negative and two decades larger in
   magnitude than every other object. Negative B\* appears in TLEs as an
   orbit-determination fit artifact, often on manoeuvring or
   high-area-to-mass objects. Flag for Phase 1 data-quality review; it does not
   affect qualification.
3. **Regime imbalance**: `alt900-1400 / inc60-90` holds two objects
   (ONEWEB-0015, SENTINEL-6B) whose altitudes differ by 221 km, and
   SENTINEL-6B at 66.0° inclination is **not** sun-synchronous — the
   `sun_synchronous_mid` slot did not deliver an SSO object. The two genuine
   near-polar SSO objects are the Flocks at 97.4°. Regime *labels* in the
   catalog therefore do not match the *ingested* regimes; only the ingested
   ones are used for qualification, which is the intended safeguard.
4. **Median gap 0.0 h for six objects** — these archives contain multiple
   records per epoch instant (Space-Track publishes several element sets with
   identical or near-identical epochs). Deduplication is by exact epoch, so
   near-duplicates survive. Worth reviewing before the science rerun, since it
   inflates record counts relative to distinct orbit solutions. It does not
   affect qualification, because pairing selects by epoch gap band.
5. **`satellite_name` was "TBA - TO BE ASSIGNED" for 7 of 9 objects** in the
   first qualification pass. Cause: `gp_history` carries the OBJECT_NAME in
   force at each epoch, and newly catalogued objects read "TBA" for their
   earliest records. Fixed — identity now comes from the preserved
   `satcat_<norad>.json`, which is authoritative. No NORAD ID was affected.
   ONEWEB-0015 still reads "TBA" because its satcat file is corrupted (§6).

---

## 4a. BLOCKING data-integrity defects found during this pass

Both must be resolved **before** the unified science rerun. Neither was fixed
here: each changes every reported statistic and deserves a deliberate pass.

### D1 — Every history is ingested twice (JSON + TLE of the same object)

`discover_satellites` walks all files under the archive directory and ingests
both `gp_history_<n>.json` and `gp_history_<n>.tle` — the **same records in two
formats**. Deduplication is by exact epoch ISO string, but the JSON path reads
the `EPOCH` field while the TLE path recovers the epoch from the TLE line via
floating-point Julian date, so sub-second representations differ and dedup
almost entirely fails:

| Object | JSON records | TLE records | Unique JSON epochs | Unique TLE epochs | Overlap | Ingested union |
|---|---:|---:|---:|---:|---:|---:|
| FLOCK 4H 1 (66704) | 749 | 749 | 638 | 638 | **17** | 1259 |
| ISS (25544) | 52538 | 52538 | 46888 | 46888 | **1117** | 92659 |

So ~97–98 % of records are duplicated. Consequences:

- **Record counts in §3 are inflated ~2×.** ISS holds 46 888 distinct orbit
  solutions, not 92 659.
- **"Median gap 0.0 h" is an artifact**, not a real cadence: a duplicate sits
  microseconds from its twin. The genuine ISS cadence is the p90 of 7.58 h.
- **Pair counts are inflated.** Duplicates fall below every band's lower bound
  (≥ 4 h) so they are rarely selected as stale partners, but each duplicated
  *reference* epoch generates a near-identical extra pair. This violates the
  campaign's core "one accepted TLE pair = one independent observation" rule and
  would inflate bootstrap CIs and sign-test significance in Phase 4/5.

**Fix:** ingest one format per object (prefer JSON, which carries the
authoritative `EPOCH`), or deduplicate on rounded epoch plus mean motion rather
than the ISO string.

**Does this overturn qualification?** No. After dedup the retained objects still
hold 638–46 888 distinct solutions over 220–10 110 days; every band would retain
roughly half its current pairs, which is still far above the ≥3-per-split rule.
The verdict is robust; the per-satellite *statistics* in §3 are not.

### D2 — Error payloads are stored as if they were data

`dataraw/spacetrack/oneweb_0015_61594/satcat_61594.json` is not a catalogue
record. It is a Space-Track rate-limit error, written to disk and checksummed in
`fetch_manifest.json` as though valid. Full audit: 18 preserved JSON responses,
**1 corrupted**, all `gp_history` files valid. See
`BLACK_KITE_ACQUISITION_DEBUG.md` §2a — this is also the most likely reason the
BLACK KITE slots resolved to nothing.

---

## 5. Qualification verdict

See `DATASET_QUALIFICATION_REPORT.md` for the final verdict after the
implementation fix described in the audit section of that file. The debug facts
above are the input to it:

- ingested: **9**
- retained (≥2 supported bands): **7**
- dropped: **2** (both Starlink, 4.5-day histories)
- distinct regimes among retained: **5**
- **verdict: QUALIFIED**, subject to defects D1 and D2 above being cleared
  before the science rerun

---

## 6. Corrupted-response audit

| Preserved JSON responses | 18 |
| Valid | 17 |
| **Corrupted** | **1** — `oneweb_0015_61594/satcat_61594.json` (rate-limit error payload) |
| `gp_history` archives affected | **none** — all 9 parse cleanly |

Re-fetch that one satcat file. No orbital data is lost; only ONEWEB-0015's
authoritative identity is currently unavailable, which is why it still displays
as "TBA - TO BE ASSIGNED".
