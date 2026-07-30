# Dataset Design (Phase 1)

Date: 2026-07-27
Status: **acquisition prepared, not executed.** No data was downloaded. No
credentials are present in this workspace. Nothing below is a result.

Scope: software-only orbital input. Every archive described here carries
`reference_is_measured_truth = false` and supports no packet, error-rate,
receiver-acknowledgement, over-the-air, or on-orbit claim.

---

## 1. Why the current dataset cannot answer the research question

The campaign asks *when* inter-TLE residual structure generalizes across LEO
satellites. The available history is two BLACK KITE objects:

| | BK1 | BK2 |
|---|---|---|
| NORAD | 66741 | 68474 |
| Records | 415 | 184 |
| Median gap | 6.3 h | 6.4 h |
| Span | 2025-12-18 → 2026-06-12 | 2026-04-13 → 2026-06-13 |

Same family, same cadence to within 0.1 h, overlapping ~2 months, one orbit
regime. A matrix over these two objects has four cells and one off-diagonal
direction per ordering — it can measure *transfer between two similar objects*,
which is not generalization. Additionally both raw archives are absent from this
workspace (`dataraw/`, `data_raw/` are git-ignored and empty).

**Requirement: ≥ 6 satellites, preferably 8–12, spanning ≥ 3 distinct regimes.**

---

## 2. Diversity axes

Generalization is only meaningful if the satellite set actually varies along the
axes that plausibly drive inter-TLE residual structure:

| Axis | Why it should matter | Target spread |
|---|---|---|
| **Altitude** | sets drag magnitude and therefore how fast mean elements go stale | ≥ 3 bands across 300–1400 km |
| **Inclination** | changes J2 secular rates and ground-station pass geometry | ≥ 3 bands, include polar/SSO and mid-inclination |
| **Eccentricity** | near-circular vs mildly eccentric changes the along-track error signature | ≥ 1 object with e > 0.01 if obtainable |
| **B\*** | direct drag-coefficient proxy; the term most likely to carry learnable structure | ≥ 1 decade of spread |
| **Update cadence** | sets how stale a "stale" TLE really is and how many long-staleness pairs exist | ≥ 2 bands (sub-8 h vs 24 h+) |
| **Manoeuvre behaviour** | station-keeping objects generate the outlier pairs the reject rule screens | include both manoeuvring and passive objects |

The last axis is deliberate: Phase 6 asks whether screening manufactures the
negative result, and that question is only answerable if the dataset contains
objects that actually manoeuvre.

---

## 3. Regime slots

Defined in `experiments/exp14_multisat_generalization_matrix/satellite_catalog.yaml`.
Four regimes, 8 slots, 11 requested objects:

| Regime | Intent | Slots |
|---|---|---|
| `very_low_high_drag` | large residuals, frequent OD updates, active station-keeping | ISS, Starlink ×2 |
| `sun_synchronous_mid` | the workhorse D2S IoT regime; stable drag | Sentinel ×1, Planet Flock ×2 |
| `high_leo_low_drag` | weak drag, slow element evolution, smallest residuals | Iridium ×2, OneWeb ×1 |
| `incumbent_reference` | the two frozen-Paper-1 objects, re-derived from scratch | BK1, BK2 |

**Catalogue-number honesty.** Apart from ISS (25544) and the two BLACK KITE
objects, `norad_id` is `null` in the catalog and is resolved at fetch time from
the Space-Track satcat by `OBJECT_NAME`. No NORAD ID in that file is asserted as
verified until `fetch_tle_catalog.py` writes the resolved value into
`data_manifest.json`. Do not cite an ID from the catalog before resolution.

Including BK1/BK2 is deliberate: it makes the frozen Paper 1 result a *cell in
the new matrix* rather than an incomparable precedent, and it is the only way to
tell a protocol effect apart from a real finding.

---

## 4. History requirements

| Requirement | Value | Reason |
|---|---|---|
| Minimum epoch span | 120 days | a 168 h band needs gaps up to 192 h plus a 60/20/20 split on top |
| Preferred span | 365 days | seasonal drag variation enters the training distribution |
| Minimum records | 150 | ~3 pairs per split at the longest band is the hard floor |

Short histories do not fail loudly — they silently drop long-staleness rows. The
runner therefore records `usable_staleness_bands_h` per satellite in
`data_manifest.json`; a band missing from that list cannot appear as an
evaluated matrix row, and the analysis must check this before interpreting a
sparse matrix.

---

## 5. Manifest

Schema: `data/schemas/tle_data_manifest.schema.json`.
Emitted as `data_manifest.json` by the runner, one entry per satellite:

satellite name · NORAD ID · constellation/family · source path · TLE record
count · epoch span (start, end, days) · median/mean/p10/p90/max update gap ·
altitude summary (mean/min/max, from the SGP4 mean motion) · inclination
summary · eccentricity summary · B\* summary · usable staleness bands ·
`reference_is_measured_truth: false`.

Altitude is derived as `(μ/n²)^(1/3) − R_earth` from the Kozai mean motion; it
is a mean-element summary for dataset description, not a precise orbital
altitude.

---

## 6. Acquisition

`experiments/exp14_multisat_generalization_matrix/fetch_tle_catalog.py`

- reads the catalog, flattens regime slots into fetch intents
- resolves names to NORAD IDs via the satcat
- downloads `gp_history` JSON + TLE and `satcat` per object into the git-ignored
  `dataraw/spacetrack/<slug>_<norad>/`
- writes a per-object `fetch_manifest.json` with sizes and SHA256
- reuses the authentication and download helpers already in
  `tools/fetch_spacetrack_object_family.py` rather than duplicating them

Credentials: `SPACETRACK_USERNAME` / `SPACETRACK_PASSWORD`, from the environment
or `.env.spacetrack`. Neither is present here.

`--plan` prints the acquisition plan and exits **without touching the network**:

```
catalog: satellite_catalog.yaml  slots=8  requested_objects=11  minimum=6  regimes=4
  [very_low_high_drag] ISS (ZARYA) x1 norad=25544 -- ~400 km, 51.6 deg, ...
  ...
```

Without credentials the script downloads nothing and exits non-zero. **No data
was fabricated and none will be.**

---

## 7. Post-acquisition acceptance checks

Before any analysis is run on a newly acquired set:

1. `data_manifest.json` validates against the schema.
2. ≥ 6 satellites present.
3. ≥ 3 distinct altitude bands and ≥ 3 distinct inclination bands populated.
4. B\* spread ≥ 1 decade across the set.
5. ≥ 2 update-cadence bands populated.
6. Each satellite lists ≥ 4 usable staleness bands, or is documented as
   short-history.
7. BK1 and BK2 present, so the frozen result is re-derivable in-matrix.

If check 2 or 3 fails, the campaign stays in dry-run state and the word
"generalization" is not used.
