# Third-party artifact selection — frozen before the contract was applied

One artifact. Selected against the criteria below, then frozen, then the contract was run. The
selection was made without inspecting any candidate for defects, because a repository chosen
because a violation was already visible would make the study worthless.

## Selected

| | |
|---|---|
| repository | `https://github.com/khundman/telemanom` |
| frozen commit | `2e6c5b6c3558e7835601519b7bdef37c649bdbdc` |
| default branch | `master` |
| origin | NASA JPL / Caltech |
| paper | Hundman, Constantinou, Laporte, Colwell, Söderström, *Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic Thresholding*, KDD 2018 (arXiv:1802.04431) |
| license | BSD-3-clause style, Caltech |
| size | 18 tracked files; 6-module package, ~1,300 LOC Python |
| last commit | 2025-01-17 |

Reproduce the clone:

```
git clone https://github.com/khundman/telemanom.git
cd telemanom && git checkout 2e6c5b6c3558e7835601519b7bdef37c649bdbdc
```

## Inclusion criteria, declared before searching

1. **Public source, open licence.** — LICENSE.txt, BSD-3-clause style from Caltech.
2. **A learning component applied to satellite communications, NTN, or satellite
   orbit/telemetry prediction.** — a Keras LSTM regressor (`telemanom/modeling.py`) fitted per
   telemetry channel to NASA SMAP satellite and MSL rover streams.
3. **A temporal train/evaluate workflow.** — separate per-channel `data/train/<id>.npy` and
   `data/test/<id>.npy` streams; the model is fitted on the train stream then generates
   step-ahead predictions across the test stream, with errors accumulated along the time axis.
4. **Enough code and config to inspect how data is split, how features are built, and how state
   is managed.** — `config.yaml` holds every knob (`l_s: 250`, `n_predictions: 10`,
   `validation_split`, `window_size`, `smoothing_perc`, `p`); `channel.py` holds the windowing;
   `detector.py` the run loop; `errors.py` the thresholding state.
5. **No relation to this project.** — different institution, different authors, different domain
   (spacecraft telemetry anomaly detection, not LR-FHSS MAC or PPO), repository created
   2018-06-01. No PPO, RL, MAC, LR-FHSS or orbit-propagation code anywhere in it.
6. **Characterisable size.** — six modules, one driver, one config.

## Candidates considered and why they were not selected

| candidate | why not |
|---|---|
| `SPEAR-Research-Lab/Horizon-Predicting-Starlink-Performance` | fails 6: ~400+ files, mostly a Vue/TypeScript map viewer unrelated to the learning component |
| `ahmd-mohsin/Spectrum-Sharing-Hierarchical-DRL` | fails 4: synthetic environment only, no dataset ingestion or split code to inspect |
| `ConnectedSystemsLab/StarNet` | fails 1: no LICENSE file |
| `YasinSonmez/Satellite-Orbit-Prediction` | fails 1 (no licence) and 4 (notebook-only, last touched 2021) |
| `kplabs-pl/ESA-ADB` | fails 6: a large TimeEval-derived benchmark framework |

`telemanom` was the only candidate satisfying all six without qualification.

## Selection was blind to outcomes

The selecting pass was instructed to report descriptively and to record no assessment of
correctness, quality or validity — and it did not. The three HALTs the contract later returned
were not known when the commit was frozen. The frozen SHA in this file predates
`evaluation/scripts/external_artifact_study.py` in the commit history, and
`evaluation/scripts/contract_layers.py` is byte-identical before and after the study
(`07baad27026ebc2242706dd5f542609b80ccb8ab706cba12c0fb2ce15521e58b`, the hash recorded in
`evaluation/real_data/PREREGISTRATION.md`).

## A note on what this study is not

It is not a criticism of the KDD 2018 paper, and the contract cannot support one. The artifact
is a well-organised, licensed, documented release that exposes more of its mechanics than most —
which is precisely why it can be studied at all. Where provenance is incomplete the finding is
recorded as *the artifact does not expose enough information to establish X*, never as an error
by its authors. The one HALT with methodological weight (`L4.1`) concerns the early-stopping
validation signal, not the reported test-set results, and the practice it names is widespread in
the time-series deep-learning literature.
