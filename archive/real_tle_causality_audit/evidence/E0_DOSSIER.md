# LOOP E0 — AVAILABILITY-TIME AND SAMPLING AUDIT
Lifecycle: EXPERIMENT_RECOVERY. Manuscript editing FROZEN.
Verdict: **STOP AND REPORT** — transmission anchoring changes cohort membership
substantially, and no trustworthy availability field exists before 2014.

## 1. The seven clocks, separated

| # | clock | present in code? | what the code actually uses |
|---|-------|------------------|------------------------------|
| 1 | element epoch | YES | `EPOCH` field -> `r["epoch"]` |
| 2 | availability time | **NO** | never consulted (`CREATION_DATE` was read only for same-epoch revision resolution) |
| 3 | `epochs[j]` | YES | the reference element's **EPOCH**, *not* a publication time |
| 4 | pair reference time | YES | `= epochs[j]` (anchors the sample window) |
| 5 | model-refresh time | **NOT REPRESENTED** | the pipeline has no refresh clock at all |
| 6 | transmission time | YES | `t_abs = epochs[j] + k*step` |
| 7 | label-closure time | **NOT REPRESENTED** | labels are treated as instantly available |

FINDING E0-1. `epochs[j]` is an ELEMENT EPOCH. Calling it a publication time was
wrong. Confirmed directly: IRIDIUM-181 record 0 has
EPOCH 2023-05-22T16:28:54 vs CREATION_DATE 2023-05-23T16:46:12 -> **24.3 h apart**.

FINDING E0-2. Clocks 5 and 7 do not exist in the pipeline. Any walk-forward
protocol (E4) must introduce them; they cannot be recovered from current outputs.

## 2. Is CREATION_DATE a usable availability timestamp?  PARTLY — only from 2014.

Whole archive, lag = CREATION_DATE - EPOCH, n = 56,529 elements:
  min -7.7 h | p10 -5.59 h | p50 1.55 h | p90 13,397 h | p99 46,772 h | max 50,337 h
  negative lag: 15,332 of 56,529 = 27.1 %

Decomposed by element-epoch year, three distinct regimes appear:

| epoch years | p50 lag | negative % | interpretation |
|-------------|---------|-----------|----------------|
| 1998-2003 | +8,821 to +49,899 h | 0 % | **archive backfill** (entered years later) |
| 2004-2013 | -5.2 to -2.2 h | 52-94 % | **different convention** (creation stamped before epoch) |
| 2014-2026 | +0.96 to +5.76 h | **0 %** | **physically plausible publication latency** |

Within 2014-2026 the lag is well behaved: p50 2.39 h, p90 9.75 h, p99 23.63 h.

FINDING E0-3. CREATION_DATE is a defensible availability proxy **only for element
epochs >= 2014**. Before that it is contaminated. GATE S1 therefore cannot be
certified over the current cohort as constructed.

## 3. Causality of the CURRENT pairing rule (taking CREATION_DATE at face value)

Across all bands, 332,085 candidate pairs:
  stale element NOT YET AVAILABLE at the first sampled transmission : 51,226 = **15.43 %**
  reference element ALREADY AVAILABLE by the last sampled transmission: 166,983 = **50.28 %**

Worst cells: ISS @8 h 20.93 % stale-unavailable / 60.45 % reference-already-out;
IRIDIUM-177 @8 h 20.11 %; BLACK KITE-2 @8 h 18.03 %.

FINDING E0-4. Two independent defects, both from using EPOCH as availability:
  (a) ~15 % of pairs give the terminal an element it could not yet hold;
  (b) ~50 % of sampled transmissions occur when a fresher element is ALREADY
      published, i.e. the modelled staleness is not the staleness a terminal
      would actually experience. This is the anchoring artifact, now quantified.

## 4. Cohort cost of the availability-clean restriction (epoch >= 2014)

| satellite | retained |
|-----------|----------|
| ISS (ZARYA) | 20,933 / 46,859 = **44.67 %** |
| IRIDIUM 181/177, ONEWEB-0015, SENTINEL-6B, FLOCK 4H 1/2, BLACK KITE-1/2, both STARLINK | **100 %** |

FINDING E0-5. The restriction costs ISS's deep history only. Eight of nine
retained objects are unaffected. Qualification (>=6 satellites, >=3 regimes,
>=2 bands, >=3 pairs/split) is very likely still satisfiable, but must be
re-executed, not assumed.

## 5. Transmission-anchored prototype

  current : t_abs = epoch_reference + k*step         (window opens AT the reference)
  causal  : t_tx  = epoch_stale + target_age + delta_k, delta_k pre-registered,
                    spanning one orbital period, independent of the reference

Retention vs the reference-anchored cohort, availability-clean elements only:

| target | ref-anchored pairs | tx-anchored, epoch condition | tx-anchored, availability enforced |
|--------|--------------------|------------------------------|------------------------------------|
| 8 h | 26,783 | 6,996 (26.1 %) | 14,976 (**55.9 %**) |
| 24 h | 30,104 | 4,747 (15.8 %) | 18,562 (**61.7 %**) |
| 48 h | 30,168 | 5,190 (17.2 %) | 18,446 (**61.1 %**) |
| 72 h | 30,125 | 5,087 (16.9 %) | 18,367 (**61.0 %**) |
| 96 h | 30,314 | 5,539 (18.3 %) | 18,547 (**61.2 %**) |
| 168 h | 30,308 | 6,388 (21.1 %) | 18,653 (**61.5 %**) |

The availability-enforced variant is the scientifically correct one: the label may
use a reference whose EPOCH precedes the transmission provided it was not yet
AVAILABLE, since the terminal could not have used it. (That also yields a better
reference: less propagation from its own epoch.)

FINDING E0-6. Transmission anchoring retains only **56-62 %** of pairs. Combined
with the >=2014 restriction this is a **substantial cohort change**, not a
refinement. Per the stated stop rule, E1 does not begin without human sign-off.

## GATE VERDICTS
S1 CAUSALITY   : **FAIL as currently constructed.** Availability clock absent;
                 15 % stale-unavailable; 50 % reference-already-available; no
                 trustworthy availability field before 2014.
                 A causal construction IS available (>=2014 + tx-anchored +
                 availability-enforced) at 56-62 % pair retention.
S2..S5         : NOT REACHED — they require the E1-E6 dataset that S1 must gate.
