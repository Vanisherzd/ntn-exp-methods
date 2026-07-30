#!/usr/bin/env python3
"""Fail the build if a banned result, a withdrawn claim, or a stale number appears.

Three independent gates, all hard prerequisites of the PDF target:

  1. BANNED_PATTERNS   -- results permanently invalidated (../INVALID_RESULT_BANLIST.md
                          and archive/KNOWN_INVALID_RESULTS.md).
  2. WITHDRAWN_CLAIMS  -- wording for the held-out-mutation generalisation claim, which
                          was withdrawn after review because the evidence base could not
                          support it. Those words must not be reachable in the
                          manuscript; they remain only in internal review records.
  3. ARTIFACT_NUMBERS  -- every headline count must match
                          evaluation/results/final_summary.json. Stale denominators
                          survived two review cycles by being invisible, so a mismatch
                          is now a build error rather than a reviewer's job.

Run before every compile.
"""
import json
import re
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
ROOT = PAPER.parent
SUMMARY = ROOT / "evaluation" / "results" / "final_summary.json"

# B1 withdrawn headline; B2 old cell tallies; B3 old screening opening;
# B4 EXP16 probe rates; B5 endpoint budget; B6 validated-gate claims.
BANNED_PATTERNS: list[tuple[str, str]] = [
    (r"1\.94", "B1 withdrawn headline improvement"),
    (r"1\.369", "B1 withdrawn validation improvement"),
    (r"3\.26\s*mHz", "B1 withdrawn effect size"),
    (r"0\.164\d*|0\.1674\d*|0\.1685\d*", "B1 withdrawn MAE values"),
    (r"\b0\s*/\s*54\b|\b0 of 54\b|\b54 cells\b|\b279 segments\b", "B2 old cell tallies"),
    (r"\b1\s*/\s*270\b|\b1 of 270\b|\b270 cells\b|18\.390|5\.119", "B3 old screening"),
    (r"264 helpful|60 harmful|harm(ful)? rate of 0\.42", "B4 EXP16 probe rates"),
    (r"E_\{?succ|energy per success|guard cost", "B5 endpoint budget"),
    (r"500\s*Hz\s+(requirement|tolerance is|standard)", "B5 tolerance as requirement"),
    (r"(Evidence Gate|gate) (is |has been )?validated", "B6 validated-gate claim"),
    (r"(improves|reduces) (real |actual )?(LR-FHSS|packet|communication) (performance|failure)",
     "B6 performance claim"),
]

# Withdrawn by human decision after review established that the generalisation claim
# rested on a single fault. See submission_finalization/CLAIM_LEDGER.md.
WITHDRAWN_CLAIMS: list[tuple[str, str]] = [
    (r"held[-\s]?out mutation", "W1 withdrawn held-out-mutation claim"),
    (r"genuinely held[-\s]?out", "W1 withdrawn held-out-mutation claim"),
    (r"mutations? withheld", "W1 withdrawn held-out-mutation claim"),
    (r"withheld from the detector", "W1 withdrawn held-out-mutation claim"),
    (r"withheld mutation", "W1 withdrawn held-out-mutation claim"),
    (r"\bfour withheld\b|\bfour held[-\s]?out\b", "W1 obsolete withheld count"),
    (r"unseen fault", "W2 generalisation to unseen faults"),
    (r"generalis(es|ation) to (unseen|faults)", "W2 generalisation to unseen faults"),
    (r"comprehensive coverage", "W3 completeness overclaim"),
    (r"[Dd]etectors are two-sided", "W4 universal two-sided claim"),
    (r"(all|every) (nineteen|19) rules?[^.]{0,40}(two-sided|broken fixture)",
     "W4 universal two-sided claim"),
    # Obsolete denominators from the pre-merge eighteen-fault suite.
    (r"\b2\s*/\s*18\b|\b2 of 18\b|\b18\s*/\s*18\b|\b18 of 18\b",
     "W5 obsolete 18-fault set"),
    (r"\b54\s*/\s*54\b|\b54 of 54\b", "W5 obsolete 54-cell count"),
    (r"thirteen development faults and four", "W5 obsolete development/withheld split"),
    (r"\b1095 lines\b|\b812 lines\b|\b710 lines\b|\b739 lines\b",
     "W6 stale source line count"),
    (r"0\.31\s*(\\,)?s\b|qty\{0\.31\}\{\\second\}", "W6 stale runtime"),
    (r"nineteen conditions", "W7 undefined condition denominator"),
]


# The ban is on ASSERTING a withdrawn claim, not on denying it -- the paper is required
# to bound its own scope, and doing so means naming the claim it does not make ("does
# not estimate completeness on unseen faults"). A match preceded by a negation inside
# the same clause is therefore permitted. Kept deliberately blunt: the failure mode
# worth preventing is a positive claim sneaking back, and a blunt rule over-reports
# rather than under-reports when it is wrong.
NEGATION = re.compile(
    r"\b(not|no|neither|nor|never|without|cannot|can't|withdrawn|rather than|"
    r"instead of|makes? none|does not|do not|is not|are not)\b[^.;]{0,120}$",
    re.IGNORECASE)


def _is_negated(text: str, pos: int) -> bool:
    """True when a negation governs the match within its clause."""
    clause_start = max(text.rfind(".", 0, pos), text.rfind(";", 0, pos),
                       text.rfind("\n\n", 0, pos))
    return bool(NEGATION.search(text[clause_start + 1:pos]))


def artifact_numbers() -> list[tuple[str, str]]:
    """Headline values the manuscript must quote, read from the summary artifact."""
    s = json.loads(SUMMARY.read_text())
    n, c = s["fault_class_count"], s["l47_calibration"]
    return [
        (rf"\b{s['rule_count']}\b|nineteen", f"rule_count={s['rule_count']}"),
        (rf"{s['chronological_detected_count']}\s*/\s*{n}",
         f"baseline {s['chronological_detected_count']}/{n}"),
        (rf"{s['contract_detected_count']}\s*/\s*{n}",
         f"contract {s['contract_detected_count']}/{n}"),
        (rf"{s['injected_cell_count']}\s*/\s*{s['injected_cell_count']}",
         f"injected cells {s['injected_cell_count']}/{s['injected_cell_count']}"),
        (rf"num\{{{s['source_loc']}\}}|\b{s['source_loc']} lines\b",
         f"source_loc={s['source_loc']}"),
        (re.escape(str(c["measured_clean_false_halt_rate"])),
         "L4.7 measured clean false-halt rate"),
        (re.escape(str(c["nominal_alpha"])), "L4.7 nominal alpha"),
        (rf"\b{c['clean_paths_evaluated']}\b|num\{{{c['clean_paths_evaluated']}\}}",
         f"L4.7 clean paths={c['clean_paths_evaluated']}"),
        (rf"\b{s['detectors_with_red_fixture']}\b|[Ss]ixteen",
         f"detectors_with_red_fixture={s['detectors_with_red_fixture']}"),
    ]


def main() -> int:
    srcs = (sorted(PAPER.glob("*.tex")) + sorted(PAPER.glob("*.bib"))
            + sorted(PAPER.glob("figures/*.tex")) + sorted(PAPER.glob("tables/*.tex"))
            + sorted(PAPER.glob("sections/*.tex")))
    if not srcs:
        print("check_banlist: no source files found")
        return 1
    if not SUMMARY.exists():
        print(f"check_banlist: missing {SUMMARY.relative_to(ROOT)}; run "
              "evaluation/scripts/make_final_summary.py first")
        return 1

    bad: list[str] = []
    for p in srcs:
        text = p.read_text()
        for pat, label in BANNED_PATTERNS + WITHDRAWN_CLAIMS:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                if _is_negated(text, m.start()):
                    continue
                line = text[:m.start()].count("\n") + 1
                bad.append(f"{p.relative_to(PAPER)}:{line}: [{label}] matched {m.group(0)!r}")

    # The runtime claim is a BOUND, not a wall-clock string: timings vary between runs
    # and machines, so pinning an exact figure would make the build fail elsewhere.
    # Assert instead that the artifact still satisfies the bound the paper states.
    s = json.loads(SUMMARY.read_text())
    if s["runtime_seconds"] >= 2.0:
        bad.append(f"RUNTIME: artifact reports {s['runtime_seconds']} s, but the "
                   "manuscript claims the sweep runs in under 2 s")

    body = "\n".join(p.read_text() for p in srcs)
    for pat, label in artifact_numbers():
        if not re.search(pat, body):
            bad.append(f"MISSING: [{label}] nothing matches {pat!r} -- the manuscript "
                       "does not quote the current artifact value")

    if bad:
        print("BANLIST / CLAIM GATE VIOLATION -- build refused:")
        for b in bad:
            print("  " + b)
        return 1
    print(f"check_banlist: {len(srcs)} file(s) clean; {len(BANNED_PATTERNS)} banned + "
          f"{len(WITHDRAWN_CLAIMS)} withdrawn patterns, "
          f"{len(artifact_numbers())} artifact numbers verified")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
