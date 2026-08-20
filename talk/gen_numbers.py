#!/usr/bin/env python3
"""Emit talk/numbers.tex from the evidence artifact.

The manuscript binds every headline number to evaluation/results/final_summary.json through
\\artv sites, and paper/scripts/check_banlist.py refuses to build when one disagrees. A deck
retyped by hand has no such guard and is exactly where a stale number survives: the slide is
written once, the artifact moves, and nobody re-reads the slide. So the deck reads the same
artifact. If a number moves, `make -C talk` regenerates and the slide moves with it.

    python talk/gen_numbers.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "evaluation" / "results" / "final_summary.json"
ALONGTRACK = ROOT / "evaluation" / "real_data" / "l47_alongtrack.json"
CURVE = ROOT / "evaluation" / "results" / "l47_power_curve.json"
OUT = Path(__file__).resolve().parent / "numbers.tex"


def _claim_sites() -> int:
    """Count of \\artv sites the manuscript binds -- read from the gate, never typed.

    A claim site is not a unique value and not a generated macro: several sites carry the
    same number, and this deck defines more macros than the manuscript has sites. Conflating
    the three is how a backup slide came to say "64 numbers are bound this way".
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_banlist", ROOT / "paper" / "scripts" / "check_banlist.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return len(mod.artifact_values())


def _permutation_count(curve: dict) -> int:
    """B, parsed from the curve artifact and cross-checked against the frozen detector.

    The talk previously said "the floor of a 400-permutation test" as a typed literal, and got the
    floor wrong as well (1/400 rather than 1/(B+1)). Binding B here means the deck cannot restate
    a permutation count that neither the artifact nor the detector agrees with.
    """
    import re as _re
    m = _re.search(r"(\d+)\s+permutations", curve["design"])
    if not m:
        raise SystemExit("gen_numbers: curve artifact no longer states a permutation count")
    b = int(m.group(1))
    det = ROOT / "evaluation" / "scripts" / "contract_layers.py"
    if not det.exists():
        raise SystemExit(f"gen_numbers: detector missing, cannot cross-check B: {det}")
    if not _re.search(rf"\b{b}\b", det.read_text()):
        raise SystemExit(f"gen_numbers: artifact says B={b} but the detector lacks that literal")
    return b


def main() -> int:
    s = json.loads(SUMMARY.read_text())
    at = json.loads(ALONGTRACK.read_text())
    curve = {c["icc"]: c["halt_prob"] for c in json.loads(CURVE.read_text())["curve"]}

    c, r = s["l47_calibration"], s["real_l47_application"]
    a, e, x = s["real_l47_alongtrack"], s["external_artifact_study"], s["external_consequence"]
    lo, hi = c["clean_false_halt_wilson_95"]
    d1 = at["analyses"]["D1_pass_in_elementset"]

    v = {
        # calibration
        "Nrate": c["measured_clean_false_halt_rate"],
        "Nwlo": lo, "Nwhi": hi,
        "Nalpha": c["nominal_alpha"],
        "Ncleanpaths": c["clean_paths_evaluated"],
        "Ncleanhalts": c["clean_false_halts"],
        "Nseeds": json.loads(CURVE.read_text())["n_seeds_per_point"],
        "Npowerlo": curve[0.2], "Npowerhi": curve[0.8],
        # real orbital
        "Nobjects": r["n_objects"], "Nelsets": r["n_element_sets"], "Npasses": r["n_passes"],
        "Naticc": a["D1_pass_in_elementset"]["icc"],
        "Natp": d1["p_value"], "Natlo": d1["icc_lower_95_one_sided"],
        "Naticcobj": a["D2_pass_in_object"]["icc"],
        # the headline three are POOLED; the per-object split is what stops the talk reading as
        # "every object shows the effect".
        "Nperobjhalt": r["B_per_object_n_halt"], "Nperobjpass": r["B_per_object_n_pass"],
        "NpermB": _permutation_count(json.loads(CURVE.read_text())),
        "Naticcelset": a["D3_elementset_in_object"]["icc"],
        "Natused": a["n_passes_used"], "Natelsets": a["n_elsets"],
        "Natmedian": a["intrack_abs_km"]["median"], "Natmax": a["intrack_abs_km"]["max"],
        # third-party
        "Nextpass": e["pass"], "Nexthalt": e["halt"], "Nextindet": e["indeterminate"],
        "Nextna": e["not_applicable"], "Nextnobs": e["not_observable"],
        "Nextrules": e["n_rules_classified"],
        "Nconsseeds": x["n_seeds"], "Nconschanged": x["n_seeds_selection_changed"],
        "Nconsminp": x["downstream_min_attainable_p"],
        # contract
        "Nrules": s["rule_count"], "Nfaults": s["fault_class_count"],
        "Nred": s["detectors_with_red_fixture"], "Nloc": s["source_loc"],
        "Nobjprot": s["protected_object_count"],
        # H3: the source cohort and the primary in-track analysis have different
        # denominators. Both are bound so a slide cannot silently merge them.
        "Natgroups": at["analyses"]["D1_pass_in_elementset"]["n_coarser_groups"],
        "Natelsetunits": at["analyses"]["D3_elementset_in_object"]["n_units"],
        "Natelsetgroups": at["analyses"]["D3_elementset_in_object"]["n_coarser_groups"],
        # H6: claim SITES in the manuscript -- not unique values, not macro count.
        "Natdropped": a["n_passes_dropped_no_successor"],
        "Nrealiccab": r["B_pass_in_elementset_pooled"]["icc"],
        "Nconsoverlap": x["overlap_original_pct_of_validation_support"],
        "Nconsoverlapcorr": x["overlap_corrected_shared_timesteps"],
        "Nclaimsites": _claim_sites(),
    }
    # A LaTeX control sequence is letters only: \Natd3units parsed as \Natd followed by the
    # text "3units", which leaked into the preamble and killed the build. Guard it here.
    bad = sorted(k for k in v if not k.isalpha())
    if bad:
        raise SystemExit(f"macro names must be letters only, got {bad}")
    body = "\n".join(rf"\newcommand{{\{k}}}{{{val}}}" for k, val in v.items())
    OUT.write_text(
        "% GENERATED by talk/gen_numbers.py -- do not edit.\n"
        "% Every slide number is read from evaluation/results/final_summary.json, the same\n"
        "% artifact the manuscript's claim gate checks against. Retyping one here would\n"
        "% reintroduce exactly the drift that gate exists to prevent.\n"
        + body + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(v)} values)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
