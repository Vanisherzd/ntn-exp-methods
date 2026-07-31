# Final verdict — external-consequence experiment

## OUTCOME B — SELECTION-ONLY CONSEQUENCE

> The violation materially affected model selection, but we did not observe a stable downstream
> change in the reported test metric.

That is the pre-registered wording for outcome B and it is what the data support. Outcome A was
not obtained and is not claimed.

## What was run

| | |
|---|---|
| subject | `khundman/telemanom` @ `2e6c5b6c3558e7835601519b7bdef37c649bdbdc` |
| target | `L4.1` only |
| channel | `A-1`, fixed by pre-registered rule B before training |
| seeds | 5 paired, `{0,1,2,3,4}`, none replaced |
| detector | `contract_layers.py` sha256 `07baad27…`, identical to both pre-registrations |
| upstream code | ran verbatim; the clone is byte-identical and `git status` on it is empty |
| data | `CHECKSUM_VERIFIED_MIRROR`, see `DATA_PROVENANCE.md` |

## The intervention did exactly one thing, and it is verified

| | shared source timesteps | of validation support | `L4.1` |
|---|---|---|---|
| ORIGINAL | 2867 | **100.0%** | **HALT** |
| CORRECTED | **0** | 0% | **PASS** |

All 524 of 524 validation windows in the original arm touch a training window. Adjacent windows
share up to 259 of 260 timesteps. The corrected arm drops 259 boundary windows and lands at a
validation fraction of 0.2219 against upstream's declared 0.20.

## Endpoint A — model selection: changed in 5 of 5 seeds

| seed | arm | stopped | selected | best val loss | checkpoint |
|---|---|---|---|---|---|
| 0 | original | 21 | 18 | 0.000030 | `9f6d076a` |
| 0 | corrected | 14 | 13 | 0.000036 | `f04b8500` |
| 1 | original | 13 | 12 | 0.000041 | `13d45ed9` |
| 1 | corrected | 21 | 19 | 0.000027 | `890a912f` |
| 2 | original | 17 | 16 | 0.000056 | `bd64a8bd` |
| 2 | corrected | 13 | 12 | 0.000099 | `52cb2d44` |
| 3 | original | 16 | 16 | 0.000093 | `7bbb22e3` |
| 3 | corrected | 26 | 22 | 0.000023 | `dbd608ba` |
| 4 | original | 14 | 14 | 0.000062 | `a6da6abb` |
| 4 | corrected | 16 | 12 | 0.000046 | `2479ff8a` |

Every checkpoint hash differs. Selected-epoch delta spans −5 to +7; stopped-epoch delta −7 to +10.
This is a large, reproducible effect: correcting the partition changes which model early stopping
picks, every time.

## Endpoint B — reported test metric: moves, but not stably

Upstream's own `evaluate_sequences` and `Errors`, unmodified.

| seed | original TP/FN | corrected TP/FN | Δ predicted sequences | Δ recall |
|---|---|---|---|---|
| 0 | 1 / 0 | 1 / 0 | 0 | 0 |
| 1 | 1 / 0 | **0 / 1** | −1 | **−1.0** |
| 2 | 1 / 0 | 1 / 0 | 0 | 0 |
| 3 | **0 / 1** | 1 / 0 | +1 | **+1.0** |
| 4 | **0 / 1** | 1 / 0 | +1 | **+1.0** |

Anomaly detected: **original 3 of 5, corrected 4 of 5.**

Paired summary: Δ recall median 0, range [−1, +1], signs {+2, 0:2, −1}. Δ predicted sequences
median 0, range [−1, +1]. Δ`normalized_pred_error` median +0.0027, range [−0.0077, +0.0070],
signs {+4, −1}. Precision is 1.0 whenever anything is predicted and undefined otherwise, so its
delta is 0 in the two comparable seeds.

The metric changes on three of five seeds and **in both directions**. The median is zero and the
sign is not consistent, so this is within paired stochastic variation. That is outcome B, not A.

## The principal caveat: A-1 is a weak probe, and we say so

The channel the pre-registered rule selected has a **near-degenerate target**. Its telemetry column
— index 0, the regression target — holds a *single* value in the training stream (0.999, variance
1.2e-32) and *two* in the test stream (−1.0, +1.0).

Consequences, all of which bound this result:

- the LSTM is trained to predict a constant, which is why every validation loss lands near 3e-5;
- the label set for A-1 is one point anomaly, so the reported metric is effectively binary — F1 is
  either exactly 1.0 or undefined, with no intermediate values available;
- an endpoint with two attainable states cannot express a small stable shift. A-1 can register
  "detected / not detected" and nothing finer.

So the absence of a stable downstream change is **weak evidence of absence**. A channel with a
continuous target and several labelled anomalies would be a far more sensitive probe.

The channel is not being changed. Rule B selected it before any training, and switching after
seeing the ceiling effect is precisely the cherry-picking Step 3 forbids; the stop rule bars adding
another channel or more seeds. The right response is to report the limitation, which is what this
section does.

## What is claimed, and what is not

**Claimed.** On a frozen third-party spacecraft-telemetry artifact, Orbit-Evidence identified
overlapping training and early-stopping-validation support. A pre-registered correction that
changed only that partition altered the selected checkpoint in all five paired seeds. On the one
pre-registered channel we did not observe a stable change in the reported detection metric.

**Not claimed, and prohibited by the pre-registration:** that telemanom's published results are
invalid; that Orbit-Evidence improves telemetry anomaly detection; that chronological validation
improves F1; that this shows general effectiveness across satellite ML. None of those follow from
one channel, five seeds and a bimodal endpoint.

## Protocol compliance

| requirement | status |
|---|---|
| pre-registered and tagged before any model was trained | yes — `external-consequence-preregistered-v1` |
| detector code frozen throughout | yes — sha256 asserted at every run, aborts on mismatch |
| all pre-registered paired runs completed | yes — 5 of 5, none replaced |
| channel not switched after seeing a result | yes |
| no seeds added, no hyperparameters touched, no alternative split widths | yes |
| intervention not tuned toward outcome A | yes — outcome B reported as found |
| only `L4.1` tested | yes — `L2.4` and `L4.5` untouched |
| result reported faithfully, including against our own interest | yes — see the caveat above and the two conduct notes in `AMENDMENT 2` |

Two departures are recorded rather than hidden: the paired runs were started before the formal data
gate was written (the gate then passed in full; had it failed the runs would have been discarded),
and the first version of that gate contained an invalid check of my own writing, whose removal is a
correction rather than a relaxation because identity is settled by two independently published
per-file checksums.
