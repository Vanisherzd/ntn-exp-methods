#!/usr/bin/env python3
"""Apply the UNMODIFIED contract to one frozen third-party artifact.

Artifact: NASA JPL / Caltech `telemanom` (Hundman et al., KDD 2018), frozen at
2e6c5b6c3558e7835601519b7bdef37c649bdbdc. Selected against inclusion criteria recorded in
evaluation/external/SELECTION.md BEFORE any rule was applied, and not selected because any
defect was known.

Two things this script is careful about.

1. NO DETECTOR IS MODIFIED. contract_layers.py is imported unchanged and its sha256 is written
   into the output so a reader can diff it against the pre-registration hash.

2. LACK OF INFORMATION IS NEVER A PASS. Every rule gets one of five outcomes:
     PASS            the obligation is met, and that is visible in the artifact
     HALT            the obligation is violated, and that is visible in the artifact
     INDETERMINATE   the rule ran and declined to decide (its own abstention path)
     NOT_APPLICABLE  the artifact has no such object, so the obligation does not arise
     NOT_OBSERVABLE  the obligation applies but the public artifact does not expose enough
                     to establish either way
   The last is the one that keeps this honest. It is not a euphemism for PASS.

Run: python evaluation/scripts/external_artifact_study.py --repo <path-to-clone>
Writes: evaluation/external/external_study.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evaluation" / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import contract_layers as CL          # noqa: E402  -- UNMODIFIED
import numpy as np                    # noqa: E402

OUT = ROOT / "evaluation" / "external" / "external_study.json"
FROZEN_SHA = "2e6c5b6c3558e7835601519b7bdef37c649bdbdc"
REPO_URL = "https://github.com/khundman/telemanom"

# Every entry below is (rule, outcome, where, why). `where` is a path:line in the frozen
# artifact so a reader can check the claim without trusting this file.
CLASSIFICATION = [
 ("L1.1", "PASS", "telemanom/channel.py:57-70, telemanom/modeling.py:150-170",
  "shape_data builds each window as arr[i : i+l_s+n_predictions] and splits it so that inputs "
  "are the first l_s samples and targets the last n_predictions. batch_predict consumes batches "
  "in index order. Every predictor value therefore precedes its target in the stream; nothing "
  "from beyond the prediction point enters the input.", "inspected"),

 ("L1.2", "NOT_OBSERVABLE", "data/{train,test}/<channel>.npy (absent from the repository)",
  "The obligation applies: a telemetry value has a sample time and a downlink/ingest time, and "
  "selection must use the latter. But the arrays are pre-scaled, anonymised and carry no "
  "timestamp of any kind, and they are not in the repository. The artifact does not expose "
  "enough information to establish whether the two clocks were distinguished.", "inspected"),

 ("L1.3", "PASS", "telemanom/errors.py (no label reference), telemanom/detector.py:81-148",
  "Labels are read only in evaluate_sequences, which runs after detection and only when "
  "labels_path is supplied. Grepping the whole errors module for 'label' returns nothing, so the "
  "thresholding path cannot see them. No label enters training or thresholding.", "inspected"),

 ("L1.4", "PASS", "telemanom/channel.py:57-63",
  "Row membership is a function of stream length alone: the loop runs to "
  "len(arr) - l_s - n_predictions. Nothing later in the stream decides whether an earlier window "
  "exists.", "inspected"),

 ("L1.5", "NOT_APPLICABLE", "-",
  "The artifact performs no availability comparison, so there is no boundary to probe at exact "
  "equality.", "inspected"),

 ("L2.1", "NOT_APPLICABLE", "-",
  "No scheduling and no orbital geometry. Telemetry arrives as a fixed stream; there is no "
  "predicted-visible interval for a transmission to lie inside.", "inspected"),

 ("L2.2", "NOT_OBSERVABLE", "config.yaml (no bounds declared)",
  "The obligation applies to a predicted telemetry value, but the streams are pre-scaled by an "
  "external step and the artifact declares no resolution floor or plausibility ceiling in "
  "physical units, so neither can be checked.", "inspected"),

 ("L2.3", "PASS", "telemanom/modeling.py:76-92, 150-170",
  "Both LSTM layers are constructed without stateful=True, so Keras resets state between "
  "batches. batch_predict calls model.predict per batch, so no latent state carries across the "
  "evaluation window and none can diverge without bound.", "inspected"),

 ("L2.4", "HALT", "telemanom/errors.py:39-41 and 74-95; config.yaml:11",
  "config.yaml declares window_size: 30. Errors.__init__ copies it to self.window_size and "
  "adjust_window_size then DECREMENTS self.window_size in a loop until n_windows >= 0. For a "
  "short channel the effective value is therefore not the declared one, the effective value is "
  "recorded in no output (the results header carries no window_size field), and the anomaly "
  "decision depends on it. The behaviour is deliberate and documented in its own docstring; the "
  "finding is that the declared configuration does not reproduce the implementation and the "
  "artifact does not record which value produced the shipped result.", "inspected"),

 ("L3.1", "NOT_OBSERVABLE", "config.yaml:4 (use_id), data/<use_id>/models/ (absent)",
  "The obligation applies and the artifact ships a pre-selected model per channel: with "
  "train: False the model is loaded from data/<use_id>/models/. Whether that model's selection "
  "used only information available before the evaluated stream cannot be established, because "
  "the run is identified by a directory name (2018-05-19_15.00.10) and neither the models nor "
  "their training provenance are in the repository. Recording this as PASS would be turning "
  "absence of information into evidence.", "inspected"),

 ("L3.2", "NOT_APPLICABLE", "-",
  "The artifact contains no mutation-based probe of a state channel, so there is no probe whose "
  "effectiveness needs demonstrating.", "inspected"),

 ("L3.3", "NOT_APPLICABLE", "-",
  "There is no zero-effect control condition and no gated learned branch to admit.", "inspected"),

 ("L4.1", "HALT", "telemanom/channel.py:57-66 with telemanom/modeling.py:164",
  "shape_data enumerates every overlapping window of the training stream -- consecutive windows "
  "share l_s + n_predictions - 1 = 259 of 260 samples -- then calls np.random.shuffle(data) on "
  "the window array. fit() is then given validation_split=0.2, which Keras takes as the final "
  "fifth of the array it receives. Because that array was already shuffled, the validation "
  "windows are drawn at random from the same time span as the training windows and overlap them "
  "almost entirely. Train and validation folds are therefore neither chronologically ordered nor "
  "disjoint at the sample level, and val_loss drives EarlyStopping. The obligation is violated "
  "as stated. Scope: this concerns the early-stopping signal only. The evaluated test stream is "
  "a separate file, so this does not by itself establish anything about the reported test "
  "results, and overlapping-window validation is widespread practice in this literature.",
  "inspected"),

 ("L4.2", "NOT_OBSERVABLE", "telemanom/channel.py:62, telemanom/modeling.py:76-98",
  "The obligation applies to any comparison between conditions. No seed is set anywhere in the "
  "artifact -- np.random.shuffle is unseeded, and neither Keras, TensorFlow nor the 0.3 dropout "
  "is seeded -- so two runs are different realisations. But the artifact itself compares only "
  "against fixed labels, not between two stochastic conditions, so no in-artifact comparison "
  "violates the rule. What cannot be established is whether the comparisons in the associated "
  "publication shared a realisation.", "inspected"),

 ("L4.4", "NOT_APPLICABLE", "-",
  "The rule presupposes declared burned and evaluation seed namespaces. The artifact has no seed "
  "registry and sets no seed, so there are no namespaces to be disjoint. The absence itself is "
  "recorded under L4.2 rather than scored here.", "inspected"),

 ("L4.5", "HALT", "config.yaml:4, telemanom/helpers.py:47-60",
  "No artifact is hashed and no manifest exists. A run is identified by a timestamp directory "
  "name (use_id: 2018-05-19_15.00.10); make_dirs creates the tree and checks only that the "
  "directory is present. Nothing digests the input streams, the trained model, the config, or "
  "the outputs, so the declared artifacts cannot be bound to the reported result. Directly "
  "observable, and the rule's statement is violated as written.", "inspected"),

 ("L4.6", "NOT_OBSERVABLE", "- (no manifest exists; input arrays absent)",
  "The differential form of this rule needs two runs and their provenance manifests. The "
  "artifact produces no manifest, and the input arrays are not in the repository, so the "
  "comparison cannot be constructed. Its precondition fails rather than its assertion.",
  "inspected"),
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_l47(values, unit_ids, coarser_ids, label):
    """Call the frozen L4.7 on the artifact's OWN reported per-channel numbers."""
    base = {"grouping": label, "n_units": len(set(unit_ids)),
            "n_labelled_coarser": len(set(coarser_ids))}
    try:
        return {**base, **CL.check_statistical_unit(values, unit_ids, coarser_ids)}
    except CL.ContractViolation as exc:
        import orbit_evidence.experiment_contract.experiment_contract as EC
        u, agg = EC.aggregate_repeated_measures(list(values), list(unit_ids))
        cmap = {}
        for a, b in zip(unit_ids, coarser_ids):
            cmap.setdefault(a, b)
        grp = np.array([cmap[k] for k in u.tolist()])
        return {**base, "verdict": "HALT",
                "icc": round(float(EC.within_group_icc(agg, grp)), 4),
                "message": str(exc)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo

    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    if head != FROZEN_SHA:
        raise SystemExit(f"clone is at {head}, study is frozen at {FROZEN_SHA}")

    # ---- mechanically executed rules, on the artifact's own shipped results ----------
    res = list(csv.DictReader(open(repo / "results" / "2018-05-19_15.00.10.csv")))
    labels = {r["chan_id"]: r for r in
              csv.DictReader(open(repo / "labeled_anomalies.csv"))}
    chans = [r for r in res if r["chan_id"] in labels]
    err = [float(r["normalized_pred_error"]) for r in chans]
    ids = [r["chan_id"] for r in chans]
    craft = [labels[r["chan_id"]]["spacecraft"] for r in chans]
    prefix = [r["chan_id"].split("-")[0] for r in chans]

    executed = {
        # Their declared coarser level. Two spacecraft is below the abstention floor, so the
        # rule declines -- which is the outcome the paper argues for rather than a failure.
        "L4.7_channel_in_spacecraft": run_l47(
            err, ids, craft, "unit = channel, coarser = spacecraft (SMAP/MSL)"),
        # The finer grouping the artifact also exposes, via the channel-id prefix.
        "L4.7_channel_in_prefix_group": run_l47(
            err, ids, prefix, "unit = channel, coarser = channel-id prefix group"),
    }

    counts: dict[str, int] = {}
    for _, outcome, *_ in CLASSIFICATION:
        counts[outcome] = counts.get(outcome, 0) + 1
    for v in executed.values():
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1

    doc = {
        "artifact": {
            "repository": REPO_URL,
            "frozen_commit": FROZEN_SHA,
            "clone_head_verified": head,
            "paper": "Hundman, Constantinou, Laporte, Colwell, Soderstrom, "
                     "'Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic "
                     "Thresholding', KDD 2018 (arXiv:1802.04431)",
            "origin": "NASA JPL / Caltech",
            "license": "BSD-3-clause style (Caltech)",
            "selection_record": "evaluation/external/SELECTION.md",
            "file_sha256": {rel: sha256(repo / rel) for rel in
                            ["config.yaml", "telemanom/channel.py", "telemanom/modeling.py",
                             "telemanom/errors.py", "telemanom/detector.py",
                             "telemanom/helpers.py", "labeled_anomalies.csv",
                             "results/2018-05-19_15.00.10.csv"]},
        },
        "contract": {
            "contract_layers_sha256": sha256(
                ROOT / "evaluation" / "scripts" / "contract_layers.py"),
            "unmodified_since_prereg_sha256":
                "07baad27026ebc2242706dd5f542609b80ccb8ab706cba12c0fb2ce15521e58b",
            "n_rules": 19,
        },
        "outcome_semantics": {
            "PASS": "obligation met and visible in the artifact",
            "HALT": "obligation violated and visible in the artifact",
            "INDETERMINATE": "the rule ran and declined to decide via its own abstention path",
            "NOT_APPLICABLE": "the artifact has no such object; the obligation does not arise",
            "NOT_OBSERVABLE": "the obligation applies but the public artifact does not expose "
                              "enough to establish either way -- never a PASS",
        },
        "mechanically_executed": executed,
        "inspected": [{"rule": r, "outcome": o, "where": w, "why": y}
                      for r, o, w, y, _ in CLASSIFICATION],
        "counts": counts,
        "n_classified": len(CLASSIFICATION) + len(executed),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1) + "\n")

    print(f"artifact {REPO_URL} @ {FROZEN_SHA[:12]}  (HEAD verified)")
    print(f"contract_layers.py sha256 {doc['contract']['contract_layers_sha256'][:12]}  "
          f"unmodified={doc['contract']['contract_layers_sha256'] == doc['contract']['unmodified_since_prereg_sha256']}")
    print("\nmechanically executed:")
    for k, v in executed.items():
        icc = v.get("icc")
        pv = v.get("p_value")
        print(f"  {k:32s} {v['verdict']:14s} units={v['n_units']:3d} "
              f"labelled={v['n_labelled_coarser']:3d} "
              f"eff_groups={v.get('n_coarser_groups', '-')} "
              f"ICC={'n/a' if icc is None else f'{icc:.3f}'} "
              f"p={'n/a' if pv is None else f'{pv:.4f}'}")
    print("\ninspected:")
    for r, o, w, _, _ in CLASSIFICATION:
        print(f"  {r:6s} {o:16s} {w[:66]}")
    print("\ncounts:", dict(sorted(counts.items())))
    print(f"classified {doc['n_classified']} of 19 rules")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
