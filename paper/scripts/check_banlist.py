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


# The ban is on ASSERTING a withdrawn claim, not on denying it: the paper is required to
# bound its own scope, and doing so means naming the claim it does not make ("does not
# estimate completeness on unseen faults"). Two exemptions are therefore allowed, both
# narrow, and both REPORTED rather than applied silently.
#
# An earlier version of this exemption was defeated in review. It treated only "." ";"
# and a blank line as clause boundaries and allowed a negation up to 120 characters
# back, so "We do not overstate this: the contract generalises to unseen faults." passed
# the gate -- the negation belonged to a different clause entirely. The comment claimed
# the rule "over-reports rather than under-reports when it is wrong"; it under-reported,
# which is the unsafe direction for a gate whose whole purpose is to make a withdrawn
# claim unreachable. Boundaries now include ":" "," and an em-dash, and the negation must
# sit within NEGATION_WINDOW characters of the match.
CLAUSE_BOUNDARY = re.compile(r"[.;:,]|---|\n\n")
NEGATION_WINDOW = 60

NEGATION = re.compile(
    r"\b(not|no|neither|nor|never|without|cannot|can't|withdrawn|rather than|"
    r"instead of|makes? none)\b", re.IGNORECASE)


def _clause_before(text: str, pos: int) -> str:
    """The text from the nearest clause boundary up to the match."""
    start = 0
    for m in CLAUSE_BOUNDARY.finditer(text, 0, pos):
        start = m.end()
    return text[start:pos]


def _exempt(text: str, pos: int, is_manuscript: bool) -> str | None:
    """Return the reason this match is permitted, or None to flag it.

    (a) a negation governs it inside its own clause and within the window; or
    (b) DOCS ONLY: the enclosing paragraph documents the withdrawal or lists prohibited
        claims, which is how CLAIMS.md, the submission README and the pre-registration
        notice are allowed to name the claim they retract.

    (b) is deliberately unavailable in the manuscript. A self-check found that
    `fig_contract.tex` contains the figure label \textsc{prohibited} inside a TikZ block
    with no blank lines, so the whole block counted as a "prohibition context" and would
    have exempted any withdrawn claim planted in that figure. The manuscript never needs
    the exemption -- it states its scope under negation -- so it does not get one.
    """
    clause = _clause_before(text, pos)
    if len(clause) <= NEGATION_WINDOW and NEGATION.search(clause):
        return "negated in-clause"
    if is_manuscript:
        return None
    para_start = text.rfind("\n\n", 0, pos) + 1
    para_end = text.find("\n\n", pos)
    para = text[para_start:para_end if para_end != -1 else len(text)]
    if re.search(r"withdraw|prohibit|banned|retract", para, re.IGNORECASE):
        return "withdrawal/prohibition context (doc)"
    return None


# Spelled forms, derived from the artifact rather than hardcoded beside the digit. The
# previous version accepted `\b19\b|nineteen`, so the manuscript's word "nineteen"
# satisfied the check no matter what the artifact said and the value could drift freely.
_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
          8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
          13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen",
          17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty",
          51: "fifty-one", 450: "four hundred and fifty"}


def _digit_or_word(n: int) -> str:
    r"""Regex matching n written the way the manuscript writes a COUNT.

    Deliberately EXCLUDES the bare digit. `\b19\b` also matches a TikZ coordinate, a
    figure row index and a BibTeX `number = {12}` field, so a required-presence check
    built on it passes for arbitrary drifted values -- which is exactly how two counts
    stayed unguarded through review. Counts in this manuscript are written `\num{N}` or
    spelled out, and those are what we require.
    """
    alts = [rf"num\{{{n}\}}"]
    if n in _WORDS:
        w = _WORDS[n]
        alts.append(rf"[{w[0].upper()}{w[0]}]{w[1:]}\b")
    return "|".join(alts)


def artifact_numbers() -> list[tuple[str, str]]:
    """Headline values the manuscript must quote, read from the summary artifact."""
    s = json.loads(SUMMARY.read_text())
    n, c = s["fault_class_count"], s["l47_calibration"]
    return [
        (_digit_or_word(s["rule_count"]), f"rule_count={s['rule_count']}"),
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
        (_digit_or_word(c["clean_paths_evaluated"]),
         f"L4.7 clean paths={c['clean_paths_evaluated']}"),
        (_digit_or_word(s["detectors_with_red_fixture"]),
         f"detectors_with_red_fixture={s['detectors_with_red_fixture']}"),
    ]


def main() -> int:
    # The manuscript is not the only claim surface. paper/submission/*.md and the root
    # README restate every headline number, and paper/submission/README.md advertises this
    # very check as enforcing the prohibited-claim list -- so they must be inside it.
    srcs = (sorted(PAPER.glob("*.tex")) + sorted(PAPER.glob("*.bib"))
            + sorted(PAPER.glob("figures/*.tex")) + sorted(PAPER.glob("tables/*.tex"))
            + sorted(PAPER.glob("sections/*.tex"))
            + sorted(PAPER.glob("submission/*.md")) + [ROOT / "README.md"])
    srcs = [p for p in srcs if p.exists()]
    if not srcs:
        print("check_banlist: no source files found")
        return 1
    if not SUMMARY.exists():
        print(f"check_banlist: missing {SUMMARY.relative_to(ROOT)}; run "
              "evaluation/scripts/make_final_summary.py first")
        return 1

    bad: list[str] = []
    exempt: list[str] = []
    for p in srcs:
        text = p.read_text()
        rel = p.relative_to(ROOT)
        for pat, label in BANNED_PATTERNS + WITHDRAWN_CLAIMS:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                line = text[:m.start()].count("\n") + 1
                why = _exempt(text, m.start(), p.suffix in (".tex", ".bib"))
                if why:
                    exempt.append(f"{rel}:{line}: [{label}] {m.group(0)!r} ({why})")
                    continue
                bad.append(f"{rel}:{line}: [{label}] matched {m.group(0)!r}")

    # The runtime claim is a BOUND, not a wall-clock string: timings vary between runs
    # and machines, so pinning an exact figure would make the build fail elsewhere.
    # Assert instead that the artifact still satisfies the bound the paper states.
    s = json.loads(SUMMARY.read_text())
    if s["runtime_seconds"] >= 2.0:
        bad.append(f"RUNTIME: artifact reports {s['runtime_seconds']} s, but the "
                   "manuscript claims the sweep runs in under 2 s")

    # Required-presence applies to the MANUSCRIPT only; a doc need not restate every
    # number, but nothing anywhere may contradict the artifact (handled by the pattern
    # scans above plus the runtime bound).
    manuscript = "\n".join(p.read_text() for p in srcs
                           if p.suffix == ".tex" or p.suffix == ".bib")
    for pat, label in artifact_numbers():
        if not re.search(pat, manuscript):
            bad.append(f"MISSING: [{label}] nothing matches {pat!r} -- the manuscript "
                       "does not quote the current artifact value")

    if bad:
        print("BANLIST / CLAIM GATE VIOLATION -- build refused:")
        for b in bad:
            print("  " + b)
        return 1
    for e in exempt:
        print(f"  permitted: {e}")
    print(f"check_banlist: {len(srcs)} file(s) clean; {len(BANNED_PATTERNS)} banned + "
          f"{len(WITHDRAWN_CLAIMS)} withdrawn patterns, "
          f"{len(artifact_numbers())} artifact numbers bound to the artifact, "
          f"{len(exempt)} permitted mention(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
