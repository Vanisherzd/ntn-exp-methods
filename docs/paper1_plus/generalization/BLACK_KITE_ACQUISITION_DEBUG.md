# BLACK KITE Acquisition Debug

Date: 2026-07-27
Subject: why the 2026-07-27 06:54Z acquisition wrote 9 of 11 requested objects,
with BLACK KITE-1 (NORAD 66741) and BLACK KITE-2 (NORAD 68474) missing.

No credentials were printed. No NORAD ID was fabricated or substituted. No
alternative object was silently put in BLACK KITE's place.

Scope: acquisition metadata only. `reference_is_measured_truth = false`; no
measured RF truth, and no scientific result is produced or implied here.

---

## 1. Status table

| Item | BLACK KITE-1 | BLACK KITE-2 |
|---|---|---|
| Catalog NORAD | 66741 (pre-filled) | 68474 (pre-filled) |
| Catalog slot | `incumbent_reference` (last regime, last two slots) | same |
| Output directory under `dataraw/spacetrack/` | **none** | **none** |
| `fetch_manifest.json` | **none** | **none** |
| SATCAT resolution | **returned no usable row** | **returned no usable row** |
| GP_HISTORY response | **never requested** | **never requested** |
| Response empty? | yes — almost certainly a rate-limit error payload, see §2a | same |
| Fetcher skipped `incumbent_reference` deliberately? | **No** — see §4 | **No** |
| Parsing/catalog bug caused the skip? | **No parsing bug. Rate limiting caused it; an observability bug hid it.** | same |
| Object exists in Space-Track? | **Undetermined, but no longer implicated** — see §2a | **Undetermined, not implicated** |

---

## 2. What is established from evidence

**All nine bulk downloads completed** in catalog slot order with regular 2–5 s
spacing, ending at 06:54:54Z after ONEWEB-0015 — the last object of the third
regime. The two BLACK KITE slots are the fourth and final regime.

**The `NORAD_CAT_ID` resolution branch works.** ISS is configured exactly like
BLACK KITE — a pre-filled `norad_id` (25544) rather than a name pattern — and it
resolved and downloaded successfully as the very first object. So the code path
BLACK KITE uses is proven functional in the same run.

**No `--plan`-only guard was in effect**, since nine real downloads occurred.

---

## 2a. Smoking gun: the run was rate-limited, starting one query before BLACK KITE

An integrity audit of every preserved response found exactly one corrupted file:

```
dataraw/spacetrack/oneweb_0015_61594/satcat_61594.json   (265 bytes)
[{"error":"You've violated your query rate limit.  Please refer to our
  Acceptable Use guidelines ..."}]
```

This is **not** a satcat record. It is a Space-Track rate-limit error saved to
disk as if it were data, with its SHA256 dutifully recorded in
`fetch_manifest.json`.

Position matters. Each object costs three queries (`gp_history.json`,
`gp_history.tle`, `satcat.json`), plus one resolution query per slot. ONEWEB-0015
was the **ninth and final** object, and its `satcat` call — roughly the 35th
request in about 30 seconds — is the first to be refused. Space-Track's
documented limit is 30 requests per minute.

The **very next** requests in the run would have been the BLACK KITE-1 and
BLACK KITE-2 satcat resolutions. There is every reason to expect they received
the same error payload, and one decisive reason it would then vanish silently:

```python
rows = parsed if isinstance(parsed, list) else []   # [{"error": ...}] IS a list
return [ ... for r in rows[:n] if str(r.get("NORAD_CAT_ID","")).strip() ]
```

An error payload is a JSON *list*, so it passes the `isinstance` check, then
every row is discarded by the `NORAD_CAT_ID` filter — yielding an empty list
that is indistinguishable from "object not found".

**Conclusion: the missing BLACK KITE histories are most likely a rate-limiting
artifact, not evidence that the objects are absent from Space-Track.** The
earlier reading in this document — that the failure was specific to the two
catalogue numbers — is superseded by this evidence.

Two defects, both now confirmed:

1. **No response validation.** The fetcher writes any HTTP 200 body to disk,
   including error payloads, and checksums it as though it were an archive.
2. **Error payloads are silently coerced to "no results"** by `resolve_targets`,
   so a throttled query is reported identically to a missing object.

---

## 3. Mechanism: a silent skip on an empty resolution

`resolve_targets()` builds, for a pre-filled ID:

```
{BASE}/satcat/NORAD_CAT_ID/66741/format/json
```

and returns a list comprehension over the response rows. If Space-Track returns
`[]`, the function returns `[]` — no exception, no warning.

In `main()` the old code was:

```python
try:
    entry["resolved"] = resolve_targets(opener, entry)
except Exception as exc:
    print(f"  resolve failed for {entry['regime']}: {exc}", file=sys.stderr)
    continue
for hit in entry["resolved"]:      # empty list -> body never runs
    fetch_history(...)
```

An empty resolution therefore produced **no message, no warning, no non-zero
exit and no log entry**. The run printed `fetched 9 ...` and appeared
successful. This is the reason the failure was invisible rather than the reason
the objects were missing.

**Fixed in this pass.** `fetch_tle_catalog.py` now distinguishes three outcomes
per slot and prints an `UNRESOLVED SLOTS` summary at the end:

```
resolve EMPTY   [incumbent_reference] BLACK KITE-1 norad=66741: satcat returned 0 rows, nothing fetched
resolve PARTIAL [<regime>] <pattern>: 1/2 objects
resolve FAILED  [<regime>] <label>: <exception>
```

The totals line also became `fetched N/M object histories`, so a shortfall is
visible without counting directories.

This is an observability fix. It changes no threshold, no protocol, no
qualification rule and no catalog entry.

---

## 4. Was `incumbent_reference` skipped on purpose?

**No.** `acquisition_plan()` flattens every regime in `satellite_catalog.yaml`
without filtering, and the printed plan from the same script lists both BLACK
KITE entries as slots 7 and 8 of 8:

```
[incumbent_reference] BLACK KITE-1 x1 norad=66741 -- LEO, ~6.3 h update cadence
[incumbent_reference] BLACK KITE-2 x1 norad=68474 -- LEO, ~6.4 h update cadence
```

Both were requested. Neither was excluded by configuration.

---

## 5. Why resolution most likely returned zero rows

Candidate causes, re-ranked after the §2a evidence:

1. **Query rate limiting (now strongly supported).** The immediately preceding
   satcat call was refused with an explicit rate-limit error, and the fetcher
   converts such a payload into an empty result. ~35 requests in ~30 s against a
   documented 30/min limit. This alone explains both misses.
2. **The objects are absent from `satcat` under those NORAD IDs.** Still
   possible but no longer needed to explain the observation. `satcat` is
   curated; some objects appear in `gp_history` but not `satcat`.
3. **The catalogue numbers changed.** `docs/review/black_kite_family_spacetrack_inventory.md`
   recorded 66741/68474 from a **name-based** query during the earlier campaign.
   If the objects were re-catalogued, the stored IDs would now resolve to
   nothing while the names still resolve.

The earlier observation that "name-pattern slots succeeded and stored-ID slots
failed" is **confounded by ordering**: the two stored-ID BLACK KITE slots are
also the last two in the run, i.e. the most rate-limited position. ISS is a
stored-ID slot and it succeeded — because it ran first.

**This cannot be settled without a credentialed query, which this session cannot
make** — no Space-Track credentials are present in this shell (verified by
presence probe; no value read or printed).

---

## 6. Diagnostic to run next (credentialed, read-only)

With credentials exported in the shell, these three queries settle it. They are
metadata lookups only — no science, no bulk download:

```bash
# 1. Does the ID exist in satcat at all?
curl -s -b cookies.txt \
  "https://www.space-track.org/basicspacedata/query/class/satcat/NORAD_CAT_ID/66741/format/json"

# 2. Does the NAME still resolve, and to which ID?
curl -s -b cookies.txt \
  "https://www.space-track.org/basicspacedata/query/class/satcat/OBJECT_NAME/BLACK~~KITE~~/format/json"

# 3. Does gp_history exist even if satcat does not?
curl -s -b cookies.txt \
  "https://www.space-track.org/basicspacedata/query/class/gp_history/NORAD_CAT_ID/66741/limit/1/format/json"
```

Interpretation:

| Result | Meaning | Action |
|---|---|---|
| (1) returns a row | satcat has it; the earlier empty response was a rate-limit artifact | re-run the fetcher **with throttling**; the new EMPTY warning will confirm |
| (1) empty, (3) returns a record | object exists in `gp_history` but not `satcat` | change `resolve_targets` to fall back to a `gp_history` existence check when a NORAD ID is pre-filled |
| (1) empty, (2) returns a different NORAD | the object was re-catalogued | update the catalog with the **authoritatively resolved** ID and record the change; never guess it |
| (1), (2) and (3) all empty | the objects are not retrievable under these identifiers | escalate: the frozen Paper 1's dataset is not currently re-derivable, which is a significant campaign finding |

---

## 7. Consequence for the campaign

**Phase-0 BLACK KITE re-derivation remains blocked.**

The unified protocol requires BK1→BK1, BK2→BK2, BK1→BK2 and BK2→BK1 to be
re-derived from scratch before any Paper 1+ scientific statement, precisely so
that a protocol effect can be told apart from a real finding. Without the raw
BLACK KITE histories that comparison cannot be made.

This does **not** invalidate the heterogeneous 7-satellite dataset, and it does
not affect the frozen Paper 1, which stands on its own previously-computed
artifacts. It means the *bridge* between the frozen result and the new matrix is
missing.

Two options once the diagnostic resolves:

- **BK recoverable** → fetch, re-derive the four cells, proceed as planned.
- **BK unrecoverable** → the Paper 1+ matrix proceeds on the heterogeneous set
  alone, and the paper must state plainly that the frozen Paper 1 objects could
  not be re-derived under the unified protocol, with the reason. That is a
  reportable limitation, not something to paper over by substituting a different
  satellite.

No substitution will be made either way.

---

## 8. Required fixes before re-fetching

1. **Throttle the fetcher** to stay under 30 requests/min (Space-Track's
   documented limit) — a sleep between queries, not just between objects.
2. **Validate every response** before writing: reject a body that parses to a
   dict or list containing an `error` key, and retry with backoff instead of
   checksumming an error message as an archive.
3. **Re-fetch `satcat_61594.json`** (ONEWEB-0015), which is currently a stored
   rate-limit error rather than a catalogue record.
4. Keep the new EMPTY/PARTIAL/FAILED slot reporting added in this pass, so the
   next occurrence is loud.

Items 1 and 2 are acquisition-robustness fixes; they touch no threshold, no
protocol, and no qualification rule. They were **not** applied in this debug
pass because re-fetching is a network operation outside its scope.
