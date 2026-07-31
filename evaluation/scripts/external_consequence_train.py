#!/usr/bin/env python3
"""Paired training for the external-consequence experiment. Runs ONLY the pre-registered protocol.

Protocol: evaluation/external_consequence/PREREGISTRATION.md, tagged
external-consequence-preregistered-v1 before any model was trained.

Upstream code runs VERBATIM. keras_compat registers the two alias modules that upstream's 2018
import paths need, and then telemanom's own modeling.py builds the network, errors.py does the
thresholding and detector.py scores against the labels. The only thing this file changes is the
one line the intervention names.

THE INTERVENTION, and nothing else:
  ORIGINAL   upstream shape_data -> shuffle ALL windows -> fit(validation_split=0.2)
  CORRECTED  validation block carved chronologically from the raw stream BEFORE any shuffle, the
             259 windows immediately preceding it dropped so no source timestep is shared, train
             windows shuffled, fit(validation_data=(X_val, y_val))

Run: python evaluation/scripts/external_consequence_train.py --repo <clone> --data <data dir>
Writes: evaluation/external_consequence/results/paired.json and raw/<arm>_seed<k>.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evaluation" / "external_consequence"
sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ROOT / "evaluation" / "scripts"))

import keras_compat  # noqa: E402,F401  -- must precede any upstream import
import numpy as np   # noqa: E402

FROZEN_SHA = "2e6c5b6c3558e7835601519b7bdef37c649bdbdc"
PREREG_CONTRACT_SHA = "07baad27026ebc2242706dd5f542609b80ccb8ab706cba12c0fb2ce15521e58b"
CHANNEL = "A-1"
SEEDS = [0, 1, 2, 3, 4]


def seed_everything(s: int) -> None:
    os.environ["PYTHONHASHSEED"] = str(s)
    random.seed(s)
    np.random.seed(s)
    import tensorflow as tf
    tf.random.set_seed(s)
    tf.keras.utils.set_random_seed(s)


def build_windows(arr: np.ndarray, l_s: int, n_pred: int) -> np.ndarray:
    """Upstream channel.py:57-61 verbatim: every overlapping window, stride 1."""
    data = [arr[i:i + l_s + n_pred] for i in range(len(arr) - l_s - n_pred)]
    return np.array(data)


def partition(data: np.ndarray, arm: str, l_s: int, n_pred: int, frac: float):
    """The whole intervention lives here and nowhere else."""
    n_win = len(data)
    if arm == "original":
        # Upstream: shuffle every window, then Keras slices the END of the shuffled array.
        idx = np.arange(n_win)
        np.random.shuffle(idx)
        cut = int(n_win * (1.0 - frac))
        tr, va = idx[:cut], idx[cut:]
        dropped = 0
    else:
        span = l_s + n_pred
        n_val = int(round(n_win * frac))
        val_start = n_win - n_val
        train_end = max(val_start - (span - 1), 0)
        tr = np.arange(0, train_end)
        va = np.arange(val_start, n_win)
        np.random.shuffle(tr)                    # upstream shuffles training order
        dropped = val_start - train_end
    X = lambda i: data[i][:, :-n_pred, :]        # noqa: E731
    y = lambda i: data[i][:, -n_pred:, 0]        # noqa: E731
    return (X(tr), y(tr)), (X(va), y(va)), int(dropped)


def run_arm(repo: Path, data_dir: Path, arm: str, seed: int, cfg) -> dict:
    sys.path.insert(0, str(repo))
    from telemanom.channel import Channel
    from telemanom.errors import Errors
    import keras

    seed_everything(seed)
    train_raw = np.load(data_dir / "train" / f"{CHANNEL}.npy")
    test_raw = np.load(data_dir / "test" / f"{CHANNEL}.npy")

    data = build_windows(train_raw, cfg.l_s, cfg.n_predictions)
    (Xtr, ytr), (Xva, yva), dropped = partition(
        data, arm, cfg.l_s, cfg.n_predictions, cfg.validation_split)

    # Upstream architecture, built by upstream's own layer choices and hyperparameters.
    m = keras.Sequential([
        keras.layers.LSTM(cfg.layers[0], input_shape=(None, Xtr.shape[2]),
                          return_sequences=True),
        keras.layers.Dropout(cfg.dropout),
        keras.layers.LSTM(cfg.layers[1], return_sequences=False),
        keras.layers.Dropout(cfg.dropout),
        keras.layers.Dense(cfg.n_predictions),
        keras.layers.Activation("linear"),
    ])
    m.compile(loss=cfg.loss_metric, optimizer=cfg.optimizer)
    es = keras.callbacks.EarlyStopping(monitor="val_loss", patience=cfg.patience,
                                       min_delta=cfg.min_delta, verbose=0)
    t0 = time.time()
    h = m.fit(Xtr, ytr, batch_size=cfg.lstm_batch_size, epochs=cfg.epochs,
              validation_data=(Xva, yva), callbacks=[es], verbose=0, shuffle=True)
    dur = time.time() - t0

    vl = [float(x) for x in h.history["val_loss"]]
    best = int(np.argmin(vl))
    w = b"".join(np.asarray(x).tobytes() for x in m.get_weights())

    # Upstream Channel + Errors, used as-is for prediction batching, thresholding and scoring.
    ch = Channel(cfg, CHANNEL)
    ch.train, ch.test = train_raw, test_raw
    ch.shape_data(train_raw); ch.shape_data(test_raw, train=False)
    n_batches = int((ch.y_test.shape[0] - cfg.l_s) / cfg.batch_size)
    yhat = np.array([])
    for i in range(0, n_batches + 1):
        lo = i * cfg.batch_size
        hi = ch.y_test.shape[0] if i == n_batches else (i + 1) * cfg.batch_size
        pb = m.predict(ch.X_test[lo:hi], verbose=0)
        for t in range(len(pb)):
            s = max(t - cfg.n_predictions, 0)
            yhat = np.append(yhat, [np.flipud(pb[s:t + 1]).diagonal()[0]])
    ch.y_hat = np.reshape(yhat, (yhat.size,))

    run_dir = OUT / "raw" / "data" / f"{arm}_seed{seed}"
    for sub in ("smoothed_errors", "y_hat", "models"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    cwd = os.getcwd()
    os.chdir(OUT / "raw")
    try:
        err = Errors(ch, cfg, f"{arm}_seed{seed}")
        err.process_batches(ch)
    finally:
        os.chdir(cwd)

    return {
        "arm": arm, "seed": seed,
        "stopped_epoch": len(vl), "selected_epoch": best + 1,
        "best_val_loss": round(min(vl), 6), "final_val_loss": round(vl[-1], 6),
        "val_loss_curve": [round(x, 6) for x in vl],
        "checkpoint_sha256": hashlib.sha256(w).hexdigest(),
        "train_seconds": round(dur, 1),
        "n_train_windows": int(Xtr.shape[0]), "n_val_windows": int(Xva.shape[0]),
        "boundary_windows_dropped": dropped,
        "n_predicted_anom_sequences": len(err.E_seq),
        "normalized_pred_error": round(float(err.normalized), 6),
        "predicted_sequences": [[int(a), int(b)] for a, b in err.E_seq],
    }, err


def score(repo: Path, err, labels_row) -> dict:
    """Upstream Detector.evaluate_sequences, called without constructing a Detector."""
    sys.path.insert(0, str(repo))
    from telemanom.detector import Detector
    d = Detector.__new__(Detector)
    d.result_tracker = {"true_positives": 0, "false_positives": 0, "false_negatives": 0}
    d.labels_path = "x"
    import pandas as pd
    # dtype=object: upstream evaluate_sequences does
    #   label_row['anomaly_sequences'] = eval(label_row['anomaly_sequences'])
    # i.e. it replaces a string cell with a list. Upstream pins pandas 0.25.3, where the column
    # was object dtype and that assignment was fine; pandas 3 infers a strict `str` dtype and
    # rejects it. The Series is built HERE, in this wrapper, so constructing it as object dtype
    # keeps upstream's scoring code running verbatim and unmodified.
    row = pd.Series(dict(labels_row), dtype=object)
    # The REAL Errors instance, not a stub: upstream evaluate_sequences reads E_seq and
    # anom_scores off it, and passing the genuine object is what upstream does.
    r = d.evaluate_sequences(err, row)
    tp, fp, fn = r["true_positives"], r["false_positives"], r["false_negatives"]
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec == prec and rec == rec and prec + rec else float("nan")
    return {"true_positives": int(tp), "false_positives": int(fp), "false_negatives": int(fn),
            "precision": None if prec != prec else round(prec, 4),
            "recall": None if rec != rec else round(rec, 4),
            "f1": None if f1 != f1 else round(f1, 4)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="*", default=SEEDS)
    args = ap.parse_args()

    head = subprocess.run(["git", "-C", str(args.repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    if head != FROZEN_SHA:
        raise SystemExit(f"ABORT: clone at {head}, frozen at {FROZEN_SHA}")
    have = hashlib.sha256(
        (ROOT / "evaluation" / "scripts" / "contract_layers.py").read_bytes()).hexdigest()
    if have != PREREG_CONTRACT_SHA:
        raise SystemExit("ABORT: detector hash differs from the pre-registration; experiment void")
    for rel in ("train", "test"):
        if not (args.data / rel / f"{CHANNEL}.npy").exists():
            raise SystemExit(f"ABORT: missing {args.data / rel / f'{CHANNEL}.npy'}. "
                             "The trained half is BLOCKED; no synthetic substitute is permitted.")

    sys.path.insert(0, str(args.repo))
    from telemanom.helpers import Config
    cfg = Config(str(args.repo / "config.yaml"))

    import csv
    labels = {r["chan_id"]: r for r in csv.DictReader(open(args.repo / "labeled_anomalies.csv"))}
    lrow = labels[CHANNEL]

    runs, pairs = [], []
    for s in args.seeds:
        per = {}
        for arm in ("original", "corrected"):
            r, err = run_arm(args.repo, args.data, arm, s, cfg)
            r.update(score(args.repo, err, lrow))
            (OUT / "raw" / f"{arm}_seed{s}.json").write_text(json.dumps(r, indent=1) + "\n")
            runs.append(r); per[arm] = r
            print(f"  seed {s} {arm:9s} stop_ep {r['stopped_epoch']:2d} "
                  f"sel_ep {r['selected_epoch']:2d} val {r['best_val_loss']:.5f} "
                  f"seq {r['n_predicted_anom_sequences']} "
                  f"P {r['precision']} R {r['recall']} F1 {r['f1']} "
                  f"ckpt {r['checkpoint_sha256'][:8]}")
        o, c = per["original"], per["corrected"]
        pairs.append({
            "seed": s,
            "selection_changed": o["checkpoint_sha256"] != c["checkpoint_sha256"],
            "d_selected_epoch": c["selected_epoch"] - o["selected_epoch"],
            "d_stopped_epoch": c["stopped_epoch"] - o["stopped_epoch"],
            "d_best_val_loss": round(c["best_val_loss"] - o["best_val_loss"], 6),
            "d_n_sequences": c["n_predicted_anom_sequences"] - o["n_predicted_anom_sequences"],
            "d_normalized_pred_error": round(
                c["normalized_pred_error"] - o["normalized_pred_error"], 6),
            **{f"d_{k}": (None if o[k] is None or c[k] is None else round(c[k] - o[k], 4))
               for k in ("precision", "recall", "f1")},
        })

    def summ(key):
        v = [p[key] for p in pairs if p[key] is not None]
        if not v:
            return None
        return {"median": float(np.median(v)), "min": min(v), "max": max(v),
                "signs": {"+": sum(1 for x in v if x > 0), "0": sum(1 for x in v if x == 0),
                          "-": sum(1 for x in v if x < 0)}}

    doc = {"protocol": "evaluation/external_consequence/PREREGISTRATION.md",
           "upstream_frozen_commit": head, "contract_layers_sha256": have,
           "detector_unmodified": have == PREREG_CONTRACT_SHA,
           "channel": CHANNEL, "seeds": args.seeds,
           "upstream_code_verbatim": True,
           "runs": runs, "pairs": pairs,
           "paired_summary": {k: summ(k) for k in
                              ("d_selected_epoch", "d_stopped_epoch", "d_best_val_loss",
                               "d_n_sequences", "d_normalized_pred_error",
                               "d_precision", "d_recall", "d_f1")},
           "n_seeds_selection_changed": sum(1 for p in pairs if p["selection_changed"])}
    (OUT / "results" / "paired.json").write_text(json.dumps(doc, indent=1) + "\n")
    print(f"\nselection changed in {doc['n_seeds_selection_changed']}/{len(pairs)} seeds")
    for k, v in doc["paired_summary"].items():
        if v:
            print(f"  {k:26s} median {v['median']:+.4f}  range [{v['min']}, {v['max']}]  "
                  f"signs {v['signs']}")
    print(f"wrote {(OUT / 'results' / 'paired.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
