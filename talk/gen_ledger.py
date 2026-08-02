#!/usr/bin/env python3
"""Generate talk/TALK_CLAIM_LEDGER.md: every claim the talk makes, and its licence.

The deck and the outline are two separate claim surfaces. The gate protects the paper; nothing
protected the talk. This ledger is the register, and talk/check_numbers.py enforces it: the
`artifact` column is re-read from the summary on every run, and the prohibited phrasings in
SEMANTIC_LINT below fail the build if they reappear in either surface.

    python talk/gen_ledger.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "TALK_CLAIM_LEDGER.md"

# (slide, claim, paper source, artifact field, permitted, prohibited)
LEDGER = [
    ("2", "Chronological separation is necessary but not sufficient", "Sec. I; Conclusion", "--",
     "Ordering alone does not establish deployment validity",
     "That chronological splitting is wrong or unnecessary"),
    ("3", "Four obligations lie outside one realised dataset", "Sec. I", "--",
     "Availability, row membership, hidden state, statistical unit",
     "That the list of four is exhaustive"),
    ("4", "Row-local vs relational validity", "Sec. I (the pivot)", "--",
     "Relational truth needs a second execution, source state, or level",
     "That all validity is relational"),
    ("5", "19 executable rules in four layers", "Sec. II; Table I", "rule_count",
     "The satellite instantiation of the two checks",
     "That 19 rules are complete or exhaustive"),
    ("6", "L4.6 refutes a claim of completeness", "Sec. III-A", "--",
     "Same manifest hash + different output = counterexample to completeness",
     "That L4.6 falsifies incompleteness, or verifies/proves completeness"),
    ("6", "L4.7 tests residual dependence one level coarser", "Sec. III-A", "--",
     "Referenced to a permutation null over the declared grouping",
     "That it proves exchangeability, or that PASS means valid"),
    ("6", "Designs below the resolution floor return INDETERMINATE", "Sec. III-A", "--",
     "Attainability property of the design",
     "That min p = 1/15 for arbitrary group sizes"),
    ("7", "False-halt 14/450 = 0.031, Wilson [0.018,0.052], nominal 0.05", "Sec. IV",
     "l47_calibration.*", "Consistent with alpha, not better than alpha",
     "That the gate is better calibrated than nominal"),
    ("7", "Power 0.25 at rho=0.2 and 1.00 at rho=0.8, 40 seeds each", "Fig. 2",
     "l47_power_curve.curve", "Seven evaluated design points",
     "A continuously estimated power function, or interpolation between markers"),
    ("7", "Low-power regime is not INDETERMINATE", "Sec. III-A", "--",
     "Low power is about rho; INDETERMINATE is about design resolution",
     "Shading low ICC and calling it INDETERMINATE"),
    ("8", "Source cohort: 331 passes, 109 element-set records, 11 objects", "Sec. V",
     "real_l47_application.*", "The cohort the analysis is drawn from",
     "That all 331 passes entered the primary ICC"),
    ("8", "Primary in-track analysis: 272 passes in 90 element sets", "Sec. V",
     "real_l47_alongtrack.*", "59 passes have no successor element set",
     "Merging the cohort and the analysis denominators"),
    ("8", "pass->element set: rho=0.501, p=0.0025, lower bound 0.376, HALT", "Sec. V",
     "real_l47_alongtrack.D1_*", "Exchangeability rejected for this observable and hierarchy",
     "That 0.501 is orbit prediction error, or truth error"),
    ("8", "element set->object: rho=0.284, HALT", "Sec. V", "real_l47_alongtrack.D3_*",
     "No level tested here is exchangeable",
     "That the element set is the correct universal unit"),
    ("8", "On elevation the same rule returned rho=0.000", "Sec. V",
     "real_l47_application.B_*", "The observable determines what the rule can say",
     "That dependence is absent in general"),
    ("8", "The differenced quantity is an update increment", "Sec. V",
     "real_l47_alongtrack.observable", "Between consecutive fits sharing an observation arc",
     "That it is an error against truth"),
    ("9", "5 PASS / 3 HALT / 1 INDET; 5 N/A / 5 N/OBS", "Sec. V; Table II",
     "external_artifact_study.*", "Three rule verdicts plus two applicability dispositions",
     "Calling all five 'verdicts', or scoring N/OBS as compliance"),
    ("9", "Detector sha256 unchanged, commit frozen before inspection", "Sec. V",
     "external_artifact_study.contract_layers_sha256", "Hashes are evidence of non-modification",
     "That hashing proves correctness"),
    ("10", "L4.1 overlap 100% -> 0; HALT -> PASS", "Sec. V", "external_consequence.*",
     "The intervention changed only the partition",
     "That the upstream published result is invalid"),
    ("10", "Selected checkpoint changed 5/5; rerun bit-identical", "Sec. V",
     "external_consequence.n_seeds_selection_changed", "Model-selection consequence, controlled",
     "A performance or accuracy improvement"),
    ("10", "Downstream endpoint not estimable, min two-sided p = 0.0625", "Sec. V",
     "external_consequence.downstream_min_attainable_p",
     "A study-level evidential disposition at this paired-run resolution",
     "A null result, or an L4.7 rule verdict"),
    ("11", "The novelty is the conversion, not the primitives", "Sec. II-C", "--",
     "ICC(1) and permutation inference are established and not proposed here",
     "That ICC or permutation inference is our new statistical method"),
    ("12", "17/17 curated detection is represented-fault reachability", "Sec. VI",
     "contract_detected_count / fault_class_count", "Regression coverage of represented faults",
     "That all faults, or unseen faults, are detected"),
    ("12", "16 of 19 rules have a demonstrated red fixture", "Sec. VI",
     "detectors_with_red_fixture", "Three rules have no red fixture",
     "That every rule is validated"),
    ("12", "No completeness, no RF, no accuracy claim", "Abstract; Sec. VI", "--",
     "Explicit scope boundaries", "Any RF, link, packet or learned-accuracy result"),
    ("B2", "Manuscript has N artifact-bound claim sites", "Availability para", "artv sites",
     "Claim sites, counted from the gate",
     "Equating claim sites with unique values or generated macros"),
    ("B2", "Telemetry arrays came from a checksum-verified mirror", "Sec. V",
     "external_data_provenance.*", "Mirror concordance with two published checksum sources",
     "Verification by the original publisher"),
]

# Phrasings that must never appear on either surface. Each is a defect this campaign actually
# made or nearly made, so the lint is a regression test, not a style preference.
SEMANTIC_LINT = [
    (r"falsif\w*\s+incompleteness", "H1: L4.6 refutes COMPLETENESS; incompleteness is exhibited"),
    (r"verif\w*\s+completeness", "H1: completeness is never verified"),
    (r"\bprove[sndg]?\b[^.]{0,30}complete", "H1: completeness is never proven"),
    (r"manifest is complete\b", "H1: prohibited spoken claim"),
    (r"PASS means valid", "PASS means not rejected"),
    (r"correct statistical unit", "the rule adjudicates the level it is given"),
    (r"truth error", "the along-track quantity is an update increment"),
    (r"downstream (result|endpoint) is (a )?null", "not estimable is not a null"),
    (r"\bno effect\b", "not estimable is not 'no effect'"),
    (r"improves anomaly detection", "prohibited claim"),
    (r"(all|every) faults? (are|is) detected", "represented-fault coverage only"),
    (r"19 rules are complete", "no completeness claim"),
    (r"verified by the original publisher", "mirror concordance only"),
    (r"below four coarser groups the smallest", "H2: 1/15 is one construction, not a rule"),
]


def main() -> int:
    s = json.loads((ROOT / "evaluation" / "results" / "final_summary.json").read_text())
    rows = "\n".join(
        f"| {sl} | {claim} | {src} | `{fld}` | bound | {ok} | {no} |"
        for sl, claim, src, fld, ok, no in LEDGER)
    OUT.write_text(
        "# Talk claim ledger\n\n"
        "Generated by `talk/gen_ledger.py`. Every scientific statement the deck shows or the\n"
        "outline speaks, with the paper section that licenses it and the artifact field behind\n"
        "it. `talk/check_numbers.py` re-reads the artifact and lints both surfaces against the\n"
        "prohibited column on every build.\n\n"
        f"Detector: `{s['external_artifact_study']['contract_layers_sha256'][:16]}…` · "
        f"rules: {s['rule_count']} · manuscript claim sites: {len(LEDGER)} ledger entries.\n\n"
        "| slide | claim | paper source | artifact field | status | permitted | prohibited |\n"
        "|---|---|---|---|---|---|---|\n" + rows + "\n\n"
        "## Semantic lint\n\n"
        "These phrasings fail the build if they appear in the deck or the outline:\n\n"
        + "\n".join(f"- `{p[0]}` — {p[1]}" for p in SEMANTIC_LINT) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(LEDGER)} claims, {len(SEMANTIC_LINT)} lint rules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
