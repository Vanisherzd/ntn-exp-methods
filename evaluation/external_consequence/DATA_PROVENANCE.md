# Data provenance — upstream telemanom A-1 arrays

## DATA_SOURCE_STATUS = `CHECKSUM_VERIFIED_MIRROR`

The strongest of the three tiers, reached because **independently published per-file checksums were
found and matched exactly** — not merely because structural checks agreed.

## Honest note on ordering

The paired training runs were started **before** this document existed. What had been done first
was substantive, and is recorded in `environment_manifest.json`: both per-file sha256 computed and
compared against the LFS oid of an unrelated mirror, `labeled_anomalies.csv` compared byte-for-byte
against the live official copy, shapes checked against upstream's documented `num_values`, and the
upstream loader exercised. The formal gate below was then written and run in full. It passed, so no
run is discarded. Had it failed, the runs would have been discarded rather than reinterpreted —
but the correct order was gate first, and it is recorded here that this is not what happened.

## Mirror

| | |
|---|---|
| repository | `https://huggingface.co/datasets/appleparan/telemanom` |
| file URL pattern | `.../resolve/main/data/data/{train,test}/<channel>.npy` |
| credentials | none; `gated:false`, `private:false` |
| licence | BSD-3-clause; bundled notice is the original Caltech / NASA JPL 2018 text |
| attribution on the card | `khundman/telemanom`, Hundman et al., KDD 2018 |
| downloaded | 2026-07-31 (UTC timestamp in `results/data_gate.json`) |
| files taken | `data/data/train/A-1.npy`, `data/data/test/A-1.npy`, `labeled_anomalies.csv` |

## A. Per-file checksum evidence — the decisive test

Two **unrelated** third-party repositories store these arrays in Git LFS. An LFS pointer file is a
plain-text record of `oid sha256:<hash>` and `size`, published in each repository independently of
the Hugging Face mirror. I fetched both pointer files directly and compared.

| file | sha256 | bytes | `Monisha325/…LSTM-Autoencoders` | `Nagarohit29/Satellite-Telemetry-…` | downloaded file |
|---|---|---|---|---|---|
| `train/A-1.npy` | `ae426533f9d4c6247a5cc1eab89438fed8bf768b0a41d60d42f3a65a7ebc80b0` | 576128 | match | match | **match** |
| `test/A-1.npy` | `7509b72cd170003c3135e12d1f4c67b263dc5be58aabedf12ed14e7561fe6dc2` | 1728128 | match | match | **match** |

Three sources agree on both files. Neither GitHub repository is derived from the Hugging Face
mirror, and `Nagarohit29`'s LFS budget is exhausted so its bytes are unfetchable — its *pointer* is
still readable, which is precisely what makes it independent evidence rather than a copy.

**On the whole-archive anchor.** TimeSeAD documents the original archive as
`SHA256(data.zip) = b4d66deb492d9b0a353b51879152687ed9313897e8e19320d2dc853d738ed8a7` from
`s3-us-west-2.amazonaws.com/telemanom/data.zip`. That URL returns **HTTP 403** on the path-style
URL, the virtual-host URL and the bucket listing, so the archive cannot be retrieved and that
anchor cannot be evaluated. It is **not** used to claim anything here. The per-file checksums above
stand on their own and are stronger for this purpose, since they pin the two files actually used
rather than a container.

## B. Structural invariants — all pass

| check | result |
|---|---|
| `test/A-1.npy` shape `(8640, 25)` as publicly documented | pass |
| `train/A-1.npy` shape `(2880, 25)` | pass |
| second dimension identical across train and test | pass (25) |
| dtype `float64` in both | pass |
| no NaN, no Inf | pass |
| all values within ±1, as the paper documents (pre-scaled) | pass |
| columns 1.. are binary `{0.0, 1.0}` command one-hot | pass |

## C. Labels match the frozen upstream commit

`labeled_anomalies.csv` from the mirror is **byte-identical** to the copy in the frozen
`telemanom` commit `2e6c5b6c`, and identical to the live official copy on `master`. The A-1 row is
`spacecraft SMAP`, `anomaly_sequences [[4690, 4774]]`, `class [point]`, `num_values 8640`, and the
downloaded test array has exactly 8640 rows.

## D. Upstream code consumes the arrays unchanged

Upstream `telemanom/channel.py::shape_data` was run on the downloaded arrays as-is and produced
`X_train (2620, 250, 25)`, `y_train (2620, 10)`, `X_test (8380, 250, 25)` — consistent with
`l_s = 250` and `n_predictions = 10`. No reconstruction from Parquet, no renormalisation, no column
reordering, no regeneration of command fields, no interpolation, no resampling. The `.npy` files
are used exactly as downloaded.

## A finding about the channel, not the mirror

The gate initially failed one check because I had asserted that column 0 — the regression target —
would contain more than 100 distinct values. It does not, and the assertion was invalid: that is
not a provenance property, and removing it is a correction to the gate rather than a relaxation to
admit a failing mirror. Identity is settled by the per-file checksums.

What the check surfaced is worth recording prominently, because it bounds the whole experiment:

> **A-1's telemetry column is near-degenerate.** In the training stream it takes a *single* value
> (0.999, variance 1.2e-32). In the test stream it takes *two* (−1.0 and +1.0).

So the LSTM is trained to predict a constant, which is why validation loss sits around 3e-5, and
the reported detection metric has almost no headroom: on a channel whose label set is one point
anomaly, F1 comes out either exactly 1.0 or undefined (when zero sequences are predicted).

**A-1 is therefore a weak probe for a downstream consequence.** It is the channel the
pre-registered rule selected, and it is not being changed — switching channels after seeing this
is exactly the cherry-picking Step 3 forbids, and the stop rule forbids adding another. The
limitation is reported instead, and it is the main caveat on the consequence classification.

## Acceptance gate

| requirement | result |
|---|---|
| A. mirror explicitly traces to original telemanom data | pass — card attributes to `khundman/telemanom` and Hundman et al. |
| B. A-1 structural invariants match upstream/public documentation | pass |
| C. labels match the frozen upstream labels | pass — byte-identical |
| D. upstream code consumes the arrays unchanged | pass |
| E. hashes and provenance recorded permanently | pass — here and in `results/data_gate.json` |
| F. no preprocessing transformation required | pass |
| independent per-file checksum found and matched | **pass — two sources, both files** |

`DATA_SOURCE_STATUS = CHECKSUM_VERIFIED_MIRROR`
