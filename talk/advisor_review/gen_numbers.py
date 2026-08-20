#!/usr/bin/env python3
"""Emit talk/advisor_review/numbers.tex from the frozen evidence artifacts.

The advisor deck needs a SUPERSET of the workshop deck's numbers: it explains the method rather
than summarising it, so it states the permutation count, the attainability arithmetic, the
regression denominators and the intervention's window geometry, none of which the workshop deck
shows. Every one of them is read from an artifact here. A number typed into a slide has no guard
and is exactly where a stale figure survives a re-run.

Three artifacts, the same three the workshop generator reads:
  evaluation/results/final_summary.json    -- the claim-gated summary
  evaluation/real_data/l47_alongtrack.json -- per-analysis detail (the one-sided bounds live here)
  evaluation/results/l47_power_curve.json  -- the evaluated operating characteristic

Two values are DERIVED rather than read, and both are checked against the artifact:
  * the number of distinct permutation assignments for k groups of m units, which is a pure
    combinatorial fact -- asserted against the artifact's stored minimum attainable p;
  * the permutation count B, parsed from the curve artifact's design string and cross-checked
    against the literal in the detector source, so a change to either side fails the build.

    python talk/advisor_review/gen_numbers.py
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SUMMARY = ROOT / "evaluation" / "results" / "final_summary.json"
ALONGTRACK = ROOT / "evaluation" / "real_data" / "l47_alongtrack.json"
CURVE = ROOT / "evaluation" / "results" / "l47_power_curve.json"
DETECTORS = [ROOT / "evaluation" / "scripts" / "real_l47_alongtrack.py",
             ROOT / "evaluation" / "scripts" / "calibrate_l47.py"]
OUT = HERE / "numbers.tex"


def claim_sites() -> int:
    """Count of \\artv sites the manuscript binds -- read from the gate, never typed."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_banlist", ROOT / "paper" / "scripts" / "check_banlist.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return len(mod.artifact_values())


def fmt(raw, decimals: int) -> str:
    """Presentation rendering of an artifact value. REPRESENTATION ONLY, never value.

    The elevation ICC is stored as 0.0 and reads better on a slide beside 0.501 and 0.284 as
    0.000 -- same value, matched precision. The danger in any such layer is that it becomes a
    place where a number quietly changes, so the invariant is asserted here rather than trusted:
    the rendered string must parse back to the raw value exactly. If the artifact ever held
    0.0004, rendering to three places would silently present it as zero, and this raises instead.
    """
    rendered = f"{float(raw):.{decimals}f}"
    if float(rendered) != float(raw):
        raise SystemExit(
            f"gen_numbers: formatting {raw!r} to {decimals} decimals gives {rendered!r}, which "
            f"parses back as {float(rendered)!r} -- a formatting layer may change representation, "
            f"never value")
    return rendered


def assignments(groups: int, per_group: int) -> int:
    """Distinct assignments of groups*per_group units into `groups` unlabelled groups of equal
    size: (km)! / (m!^k k!). This is the denominator of the smallest attainable permutation
    p-value, so it is arithmetic, not a measurement -- but it must agree with the artifact."""
    n = groups * per_group
    return math.factorial(n) // (math.factorial(per_group) ** groups * math.factorial(groups))


def bootstrap_draws() -> int:
    """n_boot for the one-sided ICC bounds, read from the detector's own default.

    These bounds are a group-level bootstrap, deliberately not the permutation reference ("a
    permutation reference tests a null; it does not bound an effect"). The deck must say so, and
    the draw count must come from the code rather than from memory.
    """
    src = (ROOT / "evaluation" / "scripts" / "real_l47_alongtrack.py").read_text()
    m = re.search(r"n_boot:\s*int\s*=\s*(\d+)", src)
    if not m:
        raise SystemExit("gen_numbers: cannot read n_boot from real_l47_alongtrack.py")
    return int(m.group(1))


def design_field(curve: dict, pattern: str, key: str = "design") -> int:
    """An integer parsed out of the curve artifact's own prose description.

    The calibration geometry and the abstention precondition are recorded as sentences, not
    fields. Parsing them keeps the slide bound to the artifact that produced the curve instead of
    to a number typed beside it -- and a wording change fails the build rather than going stale.
    """
    m = re.search(pattern, curve[key])
    if not m:
        raise SystemExit(f"gen_numbers: {key!r} no longer matches {pattern!r}; the slide would "
                         f"describe a design the artifact does not record")
    return int(m.group(1))


def permutation_count(curve: dict) -> int:
    """B, parsed from the curve artifact's design string and cross-checked against the detector.

    B lives in two places -- prose in the artifact and a literal in the detector -- and the deck
    must not pick one and hope. Disagreement is a build failure.
    """
    m = re.search(r"(\d+)\s+permutations", curve["design"])
    if not m:
        raise SystemExit("gen_numbers: the curve artifact's design string no longer states a "
                         "permutation count; B cannot be bound")
    b = int(m.group(1))
    for src in DETECTORS:
        if not src.exists():
            raise SystemExit(f"gen_numbers: detector source missing, cannot cross-check B: {src}")
        if not re.search(rf"\b{b}\b", src.read_text()):
            raise SystemExit(f"gen_numbers: artifact says B={b} but {src.name} does not contain "
                             f"that literal -- one of them moved")
    return b


def main() -> int:
    s = json.loads(SUMMARY.read_text())
    at = json.loads(ALONGTRACK.read_text())
    curve_doc = json.loads(CURVE.read_text())
    curve = {c["icc"]: c["halt_prob"] for c in curve_doc["curve"]}

    cal, app = s["l47_calibration"], s["real_l47_application"]
    alo, ext, con = s["real_l47_alongtrack"], s["external_artifact_study"], s["external_consequence"]
    floor = alo["attainability_floor"]
    d1 = at["analyses"]["D1_pass_in_elementset"]
    wlo, whi = cal["clean_false_halt_wilson_95"]

    # attainability: derive the assignment counts, then hold them to the artifact's stored minima
    a3, a4 = assignments(3, 2), assignments(4, 2)
    for count, stored, label in ((a3, floor["min_p_3_groups_of_2"], "3 groups of 2"),
                                 (a4, floor["min_p_4_groups_of_2"], "4 groups of 2")):
        if abs(1.0 / count - stored) > 5e-4:
            raise SystemExit(f"gen_numbers: {label} gives 1/{count} = {1.0/count:.4f} but the "
                             f"artifact stores {stored} -- the arithmetic and the artifact "
                             f"disagree")

    v = {
        # ---- the contract and its curated regression evaluation
        "Nrules": s["rule_count"],
        "Nfaults": s["fault_class_count"],
        "Ncontract": s["contract_detected_count"],
        "Nred": s["detectors_with_red_fixture"],
        "Nnored": s["rule_count"] - s["detectors_with_red_fixture"],
        "Nchrono": s["chronological_detected_count"],
        "Nenvs": s["environment_count"],
        "Nconds": s["conditions_per_environment"],
        "Nstatechannels": s["state_channel_count"],
        # ---- calibrating the gate before trusting it
        "Ncleanhalts": cal["clean_false_halts"],
        "Ncleanpaths": cal["clean_paths_evaluated"],
        "Nrate": cal["measured_clean_false_halt_rate"],
        "Nwlo": wlo, "Nwhi": whi,
        "Nalpha": cal["nominal_alpha"],
        "Nseeds": curve_doc["n_seeds_per_point"],
        "Nrholo": 0.2, "Nrhohi": 0.8,
        # Npowerhi is deliberately absent: 40/40 halts is shown as a count, and binding the
        # same fact twice invites the two forms to disagree.
        "Npowerlo": curve[0.2],
        "Nhaltslo": int(round(curve[0.2] * curve_doc["n_seeds_per_point"])),
        "Nhaltshi": int(round(curve[0.8] * curve_doc["n_seeds_per_point"])),
        "NpermB": permutation_count(curve_doc),
        # B2: the operating characteristic was quoted with no grouping geometry, which is this
        # deck's own thesis turned on itself -- attainability is a property of the geometry, so a
        # curve without it cannot be related to the real-data analyses. Parsed from the artifact's
        # design string so it cannot drift from the curve it labels.
        "Ncalgroups": design_field(curve_doc, r"(\d+)\s+coarser groups"),
        "Ncalunits": design_field(curve_doc, r"coarser groups of (\d+)\s+units"),
        # the deterministic abstention precondition, which reconciles the exhaustive denominator
        # in A3 with the Monte-Carlo denominator in A2: the rule never runs below this
        "Nmingroups": design_field(curve_doc, r"n_coarser_groups < (\d+)", key="abstention_boundary"),
        "Nminunits": design_field(curve_doc, r"n_units < (\d+)", key="abstention_boundary"),
        # B3: the bounds are a group-level bootstrap, NOT the permutation reference
        "Nbootdraws": bootstrap_draws(),
        # ---- abstention: attainability, not power
        "Nassignthree": a3, "Nminpthree": floor["min_p_3_groups_of_2"],
        "Nassignfour": a4, "Nminpfour": floor["min_p_4_groups_of_2"],
        # ---- real orbital data: cohort, then primary analysis
        "Npasses": app["n_passes"], "Nelsets": app["n_element_sets"], "Nobjects": app["n_objects"],
        "Natused": alo["n_passes_used"], "Natelsets": alo["n_elsets"],
        "Natdropped": alo["n_passes_dropped_no_successor"],
        "Naticc": alo["D1_pass_in_elementset"]["icc"],
        "Natp": alo["D1_pass_in_elementset"]["p_value"],
        "Natlo": d1["icc_lower_95_one_sided"],
        "Natupper": alo["D1_pass_in_elementset"]["icc_upper_95_one_sided"],
        # D2 was omitted from the deck while the title said "both tested levels" -- three
        # along-track analyses ran and all three HALTed, so the omission made the title false
        "Naticcobj": alo["D2_pass_in_object"]["icc"],
        "Naticcelset": alo["D3_elementset_in_object"]["icc"],
        # rendered to three decimals to sit beside \Naticc and \Naticcelset; fmt() refuses any
        # rendering that does not parse back to the artifact's own value
        "Nelevicc": fmt(app["B_pass_in_elementset_pooled"]["icc"], 3),
        # the p-value was suppressed to an em dash on the slide, which hid that the control
        # PASSed at p = 1.000 by ties rather than by evidence of independence
        "Nelevp": fmt(app["B_pass_in_elementset_pooled"]["p_value"], 3),
        # the elevation control is a THIRD denominator, distinct from the cohort and the
        # along-track analysis set; a deck whose discipline is "never merge denominators" must
        # show it rather than leave it off the slide
        "Nelevunits": app["B_pass_in_elementset_pooled"]["n_units"],
        "Nelevgroups": app["B_pass_in_elementset_pooled"]["n_coarser_groups"],
        # the pooled result is the headline; the per-object split is what stops it reading as
        # "all 11 objects show the effect".
        "Nperobjhalt": app["B_per_object_n_halt"], "Nperobjpass": app["B_per_object_n_pass"],
        "Natmedian": alo["intrack_abs_km"]["median"],
        # ---- the two clocks, for the availability teaching slide. The advisor deck previously
        # asserted that a past-dated element set can still be unpublished without ever showing the
        # measured gap, so the claim rested on the audience's trust rather than on the artifact.
        # Object-level, not record-pooled: one object supplies most records, which is the same
        # statistical-unit error the paper's own L4.7 is about.
        "Nlagmedian": fmt(s["publication_lag"]["median_lag_h_object_level"], 2),
        "Nlagobjects": s["publication_lag"]["n_objects"],
        # ---- the frozen third-party artifact
        "Nextrules": ext["n_rules_classified"],
        "Nextpass": ext["pass"], "Nexthalt": ext["halt"], "Nextindet": ext["indeterminate"],
        "Nextna": ext["not_applicable"], "Nextnobs": ext["not_observable"],
        # a reviewer counted what the deck showed and what it did not: 9 rules adjudicated,
        # 10 produced no verdict. The second number belongs on the slide beside the first.
        "Nextadjudicated": ext["pass"] + ext["halt"] + ext["indeterminate"],
        "Nextnoverdict": ext["not_applicable"] + ext["not_observable"],
        # ---- the pre-registered intervention
        "Nconsseeds": con["n_seeds"],
        "Nconschanged": con["n_seeds_selection_changed"],
        "Nconsoverlap": con["overlap_original_pct_of_validation_support"],
        "Nconsoverlapcorr": con["overlap_corrected_shared_timesteps"],
        "Nwindowspan": con["window_span"],
        "Nboundarydropped": con["boundary_windows_dropped"],
        "Nconsminp": con["downstream_min_attainable_p"],
        # ---- reproducibility surface
        "Nclaimsites": claim_sites(),
        "Nloc": s["source_loc"],
    }

    bad = sorted(k for k in v if not k.isalpha())
    if bad:
        raise SystemExit(f"gen_numbers: macro names must be letters only (a digit terminates a "
                         f"LaTeX control sequence), got {bad}")

    body = ["% GENERATED by talk/advisor_review/gen_numbers.py -- do not edit.",
            "% Sources: evaluation/results/final_summary.json,",
            "%          evaluation/real_data/l47_alongtrack.json,",
            "%          evaluation/results/l47_power_curve.json",
            "% Retyping any of these into a slide removes the only guard against a stale figure."]
    body += [f"\\newcommand{{\\{k}}}{{{val}}}" for k, val in v.items()]
    OUT.write_text("\n".join(body) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(v)} values)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
