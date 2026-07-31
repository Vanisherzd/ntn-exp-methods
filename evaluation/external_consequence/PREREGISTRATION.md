# Pre-registration — external-consequence experiment

Written and committed **before any model was trained** and before any corrected-arm outcome was
inspected. Tagged `external-consequence-preregistered-v1`.

## The one question

> Does an externally detected contract violation change an actual reported evaluation quantity
> when corrected, with the detector itself frozen?

Nothing else is being asked. No claim about the upstream paper's validity is in scope, and none is
permitted by the claim boundary below.

## Subject

| | |
|---|---|
| repository | `https://github.com/khundman/telemanom` |
| frozen commit | `2e6c5b6c3558e7835601519b7bdef37c649bdbdc` |
| paper | Hundman, Constantinou, Laporte, Colwell, Söderström, KDD 2018, arXiv:1802.04431 |
| origin | NASA JPL / Caltech |

Per-file source hashes are in `run_manifest.json`. The clone's `HEAD` is asserted equal to the
frozen commit at the start of every run; a mismatch aborts.

## Target violation — L4.1 only

`L4.1` states: *train, validation and deployment folds must be chronologically ordered and
disjoint.* On this artifact the contract halted because
`telemanom/channel.py:57-66` enumerates every overlapping sliding window — consecutive windows
share `l_s + n_predictions - 1 = 259` of `260` source timesteps — then calls
`np.random.shuffle(data)` on the window array, after which `telemanom/modeling.py:164` passes
`validation_split=0.2` to `fit()`. Keras takes that fraction from the end of the array it is
given, and that array is already shuffled, so the early-stopping validation windows are drawn from
the same time span as the training windows and overlap them almost entirely.

`L2.4` and `L4.5`, the other two halts, are **out of scope** for this experiment and will not be
tested.

## Channel selection, fixed before training

Step 3 rule A does not apply: upstream defines no canonical worked-example channel. The only
channel-specific reference in the code is an anomaly-position carve-out
(`errors.py:62`, `if not channel.id == 'C-2'`), which is not a worked example.

Rule B therefore applies — the lexicographically first channel in the upstream default evaluation
list (`labeled_anomalies.csv`) with complete train/test data and labels:

**Channel `A-1`** (SMAP, `num_values` 8640, one `point` anomaly at `[[4690, 4774]]`).

This channel will not be changed for any reason, including a weak or null result.

## The two arms

Identical in everything except how the early-stopping validation set is formed.

**ORIGINAL** — upstream behaviour preserved exactly: enumerate all overlapping windows,
`np.random.shuffle` the window array, `validation_split=0.2` in `fit()`.

**CORRECTED** — the validation set is carved chronologically from the raw stream *before* any
shuffle, with an exclusion boundary wide enough that no training window and no validation window
share a single source timestep. Concretely, with `W = N - l_s - n_predictions` windows and window
`i` spanning raw indices `[i, i + 260)`:

- validation windows are the last `V` windows, `i in [W - V, W]`;
- training windows are `i in [0, W - V - 260]`, i.e. the `259` windows immediately preceding the
  validation block are **dropped** as the exclusion boundary;
- training windows are then shuffled, because the upstream training procedure shuffles;
- validation windows are left in chronological order and are not shuffled;
- `V` is chosen so the validation fraction is as close as mechanically possible to upstream's
  `0.20`.

The exact number of boundary windows dropped is recorded in `results/`.

Unchanged in both arms: architecture, optimizer, learning rate, batch size, dropout, epoch cap,
early-stopping patience and `min_delta`, thresholding, anomaly scoring, test labels, test split,
feature-scaling semantics, and the evaluation code and metrics.

## Deviation recorded in advance: the port

Upstream pins `keras==2.3.1` / `tensorflow==2.0.1` and imports `keras.layers.recurrent` and
`keras.layers.core`, module paths removed in later Keras; neither pinned version has an arm64
macOS wheel. Both arms therefore run through a **port** that rebuilds the upstream architecture
and training procedure on a modern TensorFlow, reading every hyperparameter from upstream
`config.yaml`. The port is byte-identical between arms, so it cannot favour either. It is
nonetheless a deviation from running upstream code verbatim and is declared here rather than
discovered in the results.

## Data dependency, declared before the outcome is known

The experiment needs the upstream per-channel arrays `data/train/A-1.npy` and `data/test/A-1.npy`.
They are **not** in the repository. At the frozen commit the README directs users to Kaggle
(`patrickfleith/nasa-anomaly-detection-dataset-smap-msl`); the older JPL S3 mirror
`s3-us-west-2.amazonaws.com/telemanom/data.zip` returns HTTP 403, which is what the frozen
commit's own message (`fix/data_source_documentation`) records.

If the arrays cannot be obtained without credentials, then:

- the **mechanical half** of this study still runs and is still reported: the overlap
  measurement of Step 2 and the frozen detector's verdict on both partitions, which depend only
  on the windowing geometry and the stream length, not on the telemetry values;
- the **paired-training half** is reported as **BLOCKED**, with the exact missing input named;
- **no synthetic substitute is used for the trained arms.** Training a model on invented telemetry
  and reporting the delta as a third-party consequence result would fabricate the headline claim
  this experiment exists to test. That is prohibited outright, whatever the cost to the outcome.

## Endpoints, both pre-registered

**A. Model-selection consequence.** Stopped epoch, best validation loss, checkpoint `sha256`,
training duration. *Does correcting L4.1 change which model is selected?*

**B. Reported test consequence.** The upstream quantities only, computed by upstream code:
true positives, false positives, false negatives, precision, recall, F1, number of predicted
anomaly sequences, and `normalized_pred_error`. No new metric is introduced, and the primary
consequence claim rests on these, not on training loss.

## Variability

Five paired seeds `{0,1,2,3,4}`, minimum three. Per metric: original value, corrected value, and
the paired delta, reported with the median paired delta, the range and the sign consistency. No
significance test — with five seeds descriptive paired evidence is the honest presentation.

## Outcome classes, all three publishable

- **A — CONSEQUENTIAL**: selection changes *and* a reproducible change appears in an upstream
  reported test quantity.
- **B — SELECTION-ONLY**: selection changes; downstream metrics stay within paired variation.
- **C — NO OBSERVED CONSEQUENCE**: `L4.1` passes after correction but neither selection nor
  downstream metrics move materially.

The intervention will not be tuned toward A. If the result is C it is reported with the same
prominence A would have received.

## Claim boundary

Permitted if consequential: *on a frozen third-party spacecraft-telemetry artifact,
Orbit-Evidence identified overlapping training and early-stopping-validation support, and a
pre-registered correction that changed only that partition altered the selected checkpoint and the
reported metric.*

Prohibited, whatever the result: that the upstream published results are invalid; that
Orbit-Evidence improves telemetry anomaly detection; that chronological validation improves F1;
that this shows general effectiveness across satellite ML.

## Stop rule

After the pre-registered paired runs the experiment stops. No further channels, no additional
seeds, no hyperparameter changes, no alternative split widths, no new metrics, no detector
changes, no second repository. If the frozen detector's source hash changes at any point the
experiment aborts.

---

# AMENDMENT 2 — DATA SOURCE

The original upstream data endpoint documented by the frozen repository is inaccessible. A
provenance-qualified mirror of the original Telemanom A-1 `.npy` arrays is used solely as a
transport substitute. No transformation of the arrays is permitted.

Qualification is recorded in `DATA_PROVENANCE.md` and `results/data_gate.json`:
`DATA_SOURCE_STATUS = CHECKSUM_VERIFIED_MIRROR`, reached because the per-file `sha256` of both
arrays match checksums published independently by two unrelated third-party repositories, and
`labeled_anomalies.csv` is byte-identical to the frozen commit's own copy.

**This amendment changes data access only.** It does not alter: the A-1 selection, the
original/corrected arms, the five paired seeds, the endpoints, the early-stopping procedure, the
test set, the anomaly labels, the detector code, or the stopping rule. All remain exactly as
registered above.

Two facts are recorded against my own conduct rather than buried. First, the paired runs were
started before `DATA_PROVENANCE.md` was written; the substantive checks had been done and recorded
in `environment_manifest.json`, but the formal gate came afterwards, and it passed. Had it failed
the runs would have been discarded. Second, the gate surfaced that **A-1's telemetry column is
near-degenerate** — a single value in training, two values in test — so the model is trained to
predict a constant and the reported metric has almost no headroom. That bounds this experiment's
sensitivity and is the principal caveat on the consequence classification. The channel is not being
changed: the selection rule was pre-registered and switching after seeing this would be the
cherry-picking Step 3 exists to prevent.
