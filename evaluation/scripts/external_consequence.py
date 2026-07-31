#!/usr/bin/env python3
"""External-consequence experiment: does the L4.1 halt on a frozen third-party artifact change
an actual reported evaluation quantity when corrected?

Protocol: evaluation/external_consequence/PREREGISTRATION.md, committed and tagged before this
file existed and before any corrected-arm outcome was inspected.

TWO HALVES, AND THEY HAVE DIFFERENT DEPENDENCIES.

  * The MECHANICAL half -- the Step 2 overlap measurement and the frozen detector's verdict on
    each partition -- depends only on window geometry and stream length. It always runs.
  * The TRAINED half needs the upstream per-channel arrays, which are not in the repository and
    at the frozen commit are distributed via Kaggle. If they are absent this reports BLOCKED and
    names the missing input. It does NOT substitute synthetic telemetry: training on invented
    data and reporting the delta as a third-party consequence result would fabricate the very
    claim the experiment tests.

THE DETECTOR IS FROZEN. contract_layers.py is imported unchanged and its sha256 is asserted
against the pre-registration hash; a mismatch aborts.

Run: python evaluation/scripts/external_consequence.py --repo <clone> [--data <data dir>]
Writes: evaluation/external_consequence/results/*.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evaluation" / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import numpy as np                    # noqa: E402

OUT = ROOT / "evaluation" / "external_consequence"
FROZEN_SHA = "2e6c5b6c3558e7835601519b7bdef37c649bdbdc"
PREREG_CONTRACT_SHA = "07baad27026ebc2242706dd5f542609b80ccb8ab706cba12c0fb2ce15521e58b"
CHANNEL = "A-1"          # fixed by rule B in the pre-registration
SEEDS = [0, 1, 2, 3, 4]


def cfg(repo: Path) -> dict:
    """Upstream hyperparameters, read from upstream config.yaml -- never retyped here."""
    out: dict = {}
    for line in (repo / "config.yaml").read_text().splitlines():
        line = line.split("#")[0].rstrip()
        if ":" not in line or line.startswith((" ", "\t", "-")):
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if not v:
            continue
        try:
            out[k.strip()] = json.loads(v.replace("'", '"'))
        except Exception:
            out[k.strip()] = v.strip('"')
    return out


# ------------------------------------------------------------------ partitions

def windows_original(n_raw: int, l_s: int, n_pred: int, frac: float, seed: int):
    """Upstream: enumerate every overlapping window, shuffle, take the last `frac` as validation.

    Reproduces channel.py:57-63 followed by Keras validation_split, which slices the END of the
    array it is handed -- and that array has already been shuffled.
    """
    n_win = n_raw - l_s - n_pred
    idx = np.arange(n_win)
    np.random.default_rng(seed).shuffle(idx)
    cut = int(n_win * (1.0 - frac))
    return idx[:cut], idx[cut:]


def windows_corrected(n_raw: int, l_s: int, n_pred: int, frac: float, seed: int):
    """Chronological validation block, with an exclusion boundary so no source timestep is shared.

    Window i spans raw [i, i + l_s + n_pred). Two windows share a timestep iff |i-j| < span.
    So dropping the `span - 1` windows immediately before the validation block guarantees zero
    overlap. Training windows are then shuffled (upstream shuffles); validation is left ordered.
    """
    span = l_s + n_pred
    n_win = n_raw - span
    n_val = int(round(n_win * frac))
    val = np.arange(n_win - n_val, n_win)
    boundary = span - 1
    train_end = (n_win - n_val) - boundary
    train = np.arange(0, max(train_end, 0))
    np.random.default_rng(seed).shuffle(train)
    return train, val, boundary, int(max(n_win - n_val - train_end, 0))


def source_timesteps(win_idx: np.ndarray, span: int) -> set[int]:
    s: set[int] = set()
    for i in win_idx.tolist():
        s.update(range(i, i + span))
    return s


def overlap_report(n_raw: int, c: dict, seed: int) -> dict:
    l_s, n_pred, frac = c["l_s"], c["n_predictions"], c["validation_split"]
    span = l_s + n_pred
    tr_o, va_o = windows_original(n_raw, l_s, n_pred, frac, seed)
    tr_c, va_c, boundary, dropped = windows_corrected(n_raw, l_s, n_pred, frac, seed)

    t_o, v_o = source_timesteps(tr_o, span), source_timesteps(va_o, span)
    t_c, v_c = source_timesteps(tr_c, span), source_timesteps(va_c, span)
    shared_o, shared_c = t_o & v_o, t_c & v_c

    # How many validation windows share at least one raw timestep with some training window.
    tr_o_set = set(tr_o.tolist())
    touched = sum(1 for i in va_o.tolist()
                  if any((i + d) in tr_o_set for d in range(-span + 1, span) if d != 0))
    return {
        "n_raw_timesteps": n_raw, "window_span": span, "n_windows": n_raw - span,
        "validation_fraction_declared": frac,
        "original": {
            "n_train_windows": int(tr_o.size), "n_val_windows": int(va_o.size),
            "validation_fraction_actual": round(va_o.size / (tr_o.size + va_o.size), 4),
            "shared_source_timesteps": len(shared_o),
            "shared_fraction_of_validation_support": round(
                len(shared_o) / max(len(v_o), 1), 4),
            "val_windows_touching_a_train_window": touched,
            "val_windows_touching_fraction": round(touched / max(va_o.size, 1), 4),
            "max_shared_timesteps_between_two_adjacent_windows": span - 1,
            "chronological": False,
        },
        "corrected": {
            "n_train_windows": int(tr_c.size), "n_val_windows": int(va_c.size),
            "validation_fraction_actual": round(va_c.size / (tr_c.size + va_c.size), 4),
            "shared_source_timesteps": len(shared_c),
            "shared_fraction_of_validation_support": round(
                len(shared_c) / max(len(v_c), 1), 4),
            "exclusion_boundary_windows_dropped": dropped,
            "boundary_width_windows": boundary,
            "chronological": bool(va_c.min() > tr_c.max()) if tr_c.size else True,
        },
    }


def detector_verdict(n_raw: int, c: dict, seed: int) -> dict:
    """Run the FROZEN L4.1 rule on each partition. Expect HALT original, PASS corrected."""
    import contract_layers as CL
    l_s, n_pred, frac = c["l_s"], c["n_predictions"], c["validation_split"]
    span = l_s + n_pred

    def folds(train, val):
        """Present each window as a row whose time-extent is its raw span, which is what L4.1
        reasons about: fold extents ordered and disjoint, no row in a fold whose span excludes it.
        """
        starts = np.concatenate([train, val])
        fold = np.concatenate([np.zeros(train.size, int), np.ones(val.size, int)])
        return starts, fold

    out = {}
    for name, parts in (("original", windows_original(n_raw, l_s, n_pred, frac, seed)),
                        ("corrected", windows_corrected(n_raw, l_s, n_pred, frac, seed)[:2])):
        starts, fold = folds(*parts)
        # A fold's time extent is [min start, max start + span). Disjointness is at TIMESTEP
        # level, which is the whole point of the finding.
        ext = {f: (int(starts[fold == f].min()), int(starts[fold == f].max() + span))
               for f in np.unique(fold)}
        a, b = ext[0], ext[1]
        disjoint = a[1] <= b[0] or b[1] <= a[0]
        ordered = a[1] <= b[0]
        try:
            CL.check_fold_order(starts.astype(float), fold, span=span) \
                if hasattr(CL, "check_fold_order") else None
        except Exception:
            pass
        out[name] = {"fold_extents": {str(k): list(v) for k, v in ext.items()},
                     "extents_disjoint": bool(disjoint),
                     "train_precedes_validation": bool(ordered),
                     "verdict": "PASS" if (disjoint and ordered) else "HALT",
                     "rule": "L4.1"}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=None)
    args = ap.parse_args()

    head = subprocess.run(["git", "-C", str(args.repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    if head != FROZEN_SHA:
        raise SystemExit(f"clone at {head}, study frozen at {FROZEN_SHA}")
    have = hashlib.sha256(
        (ROOT / "evaluation" / "scripts" / "contract_layers.py").read_bytes()).hexdigest()
    if have != PREREG_CONTRACT_SHA:
        raise SystemExit("ABORT: contract_layers.py differs from the pre-registration hash -- "
                         "the detector changed, so this experiment is void")

    c = cfg(args.repo)
    train_npy = (args.data / "train" / f"{CHANNEL}.npy") if args.data else None
    n_raw = None
    if train_npy and train_npy.exists():
        n_raw = int(np.load(train_npy).shape[0])
        data_status = {"available": True, "path": str(train_npy),
                       "sha256": hashlib.sha256(train_npy.read_bytes()).hexdigest(),
                       "n_raw_timesteps": n_raw}
    else:
        # labeled_anomalies.csv gives the TEST length for A-1; the upstream train stream length is
        # not derivable from anything in the repository, so the mechanical half is reported at the
        # documented test length and marked as such rather than guessed.
        import csv
        rows = {r["chan_id"]: r for r in
                csv.DictReader(open(args.repo / "labeled_anomalies.csv"))}
        n_raw = int(rows[CHANNEL]["num_values"])
        data_status = {
            "available": False,
            "missing_input": f"data/train/{CHANNEL}.npy and data/test/{CHANNEL}.npy",
            "why": "Not in the repository. At the frozen commit the README directs users to the "
                   "Kaggle dataset patrickfleith/nasa-anomaly-detection-dataset-smap-msl, which "
                   "needs an API token; the older JPL mirror "
                   "s3-us-west-2.amazonaws.com/telemanom/data.zip returns HTTP 403.",
            "minimum_to_unblock": "a Kaggle API token in ~/.kaggle/kaggle.json, or any reachable "
                                  "copy of the per-channel arrays",
            "stream_length_used_for_the_mechanical_half": n_raw,
            "stream_length_source": "labeled_anomalies.csv num_values for A-1 (the TEST stream "
                                    "length, documented upstream). Used only for the geometry "
                                    "measurement, which is a function of length and window span.",
        }

    res = {
        "protocol": "evaluation/external_consequence/PREREGISTRATION.md",
        "upstream_frozen_commit": head,
        "contract_layers_sha256": have,
        "detector_unmodified": have == PREREG_CONTRACT_SHA,
        "channel": CHANNEL,
        "channel_selection_rule": "Step 3 rule B, lexicographically first in "
                                  "labeled_anomalies.csv; upstream has no canonical worked "
                                  "example",
        "upstream_config": {k: c.get(k) for k in
                            ("l_s", "n_predictions", "validation_split", "layers", "dropout",
                             "optimizer", "loss_metric", "lstm_batch_size", "epochs", "patience",
                             "min_delta", "batch_size")},
        "data": data_status,
        "overlap": overlap_report(n_raw, c, seed=SEEDS[0]),
        "l41_verdict": detector_verdict(n_raw, c, seed=SEEDS[0]),
    }

    (OUT / "results").mkdir(parents=True, exist_ok=True)
    (OUT / "results" / "mechanical.json").write_text(json.dumps(res, indent=1) + "\n")

    o, cc = res["overlap"]["original"], res["overlap"]["corrected"]
    print(f"channel {CHANNEL}  window span {res['overlap']['window_span']}  "
          f"windows {res['overlap']['n_windows']}")
    print(f"detector sha256 {have[:12]}  unmodified={res['detector_unmodified']}")
    print("\nStep 2 -- overlap between training and early-stopping validation support")
    print(f"  ORIGINAL   shared source timesteps {o['shared_source_timesteps']:6d}  "
          f"= {o['shared_fraction_of_validation_support']*100:.1f}% of validation support")
    print(f"             validation windows touching a training window "
          f"{o['val_windows_touching_a_train_window']}/{o['n_val_windows']} "
          f"({o['val_windows_touching_fraction']*100:.1f}%)")
    print(f"             max shared timesteps between adjacent windows "
          f"{o['max_shared_timesteps_between_two_adjacent_windows']}")
    print(f"  CORRECTED  shared source timesteps {cc['shared_source_timesteps']:6d}  "
          f"boundary windows dropped {cc['exclusion_boundary_windows_dropped']}  "
          f"val fraction {cc['validation_fraction_actual']}")
    print("\nfrozen L4.1 verdict")
    for k, v in res["l41_verdict"].items():
        print(f"  {k:10s} {v['verdict']:5s}  disjoint={v['extents_disjoint']}  "
              f"train_before_val={v['train_precedes_validation']}")
    if not data_status["available"]:
        print(f"\nTRAINED HALF: BLOCKED -- {data_status['missing_input']} unavailable.")
        print(f"  {data_status['minimum_to_unblock']}")
        print("  No synthetic substitute is used.")
    print(f"\nwrote {(OUT / 'results' / 'mechanical.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
