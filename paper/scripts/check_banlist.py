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


def _norm(rendered: str) -> str:
    r"""Reduce a rendered LaTeX value to a comparable string.

    Strips \num{}, thin spaces and whitespace, and maps a spelled-out count to its digits,
    so `\num{450}`, `450` and `four hundred and fifty` all compare equal to 450.
    """
    s = re.sub(r"\\num\{([^}]*)\}", r"\1", rendered)
    s = s.replace(r"\,", "").replace(r"\%", "%")
    s = re.sub(r"\s+", "", s).strip()
    low = s.lower().rstrip(".")
    for n, w in _WORDS.items():
        if low == w:
            return str(n)
    return s


def artifact_values() -> dict[str, str]:
    """key -> the value the manuscript must render at the \artv site carrying that key.

    Read from the summary artifact, never typed here.
    """
    s = json.loads(SUMMARY.read_text())
    n, c = s["fault_class_count"], s["l47_calibration"]
    lo, hi = c["clean_false_halt_wilson_95"]
    g = s["publication_lag"]
    ot, rl, ex = (s["object_level_timing"], s["real_l47_application"],
                  s["external_artifact_study"])
    return {
        "lag_objects": str(ot["n_objects"]),
        "timing_outlier_objects": str(ot["n_objects_with_any_epoch_after_creation"]),
        "real_objects": str(rl["n_objects"]),
        "real_elsets": str(rl["n_element_sets"]),
        "real_passes": str(rl["n_passes"]),
        "real_pass": str(rl["B_per_object_n_pass"]),
        "at_passes": str(s["real_l47_alongtrack"]["n_passes_used"]),
        "at_icc_d1": str(s["real_l47_alongtrack"]["D1_pass_in_elementset"]["icc"]),
        "at_icc_d1_up": str(s["real_l47_alongtrack"]["D1_pass_in_elementset"]["icc_upper_95_one_sided"]),
        "at_icc_d3": str(s["real_l47_alongtrack"]["D3_elementset_in_object"]["icc"]),
        "real_halt": str(rl["B_per_object_n_halt"]),
        "ext_classified": str(ex["n_rules_classified"]),
        "ext_pass": str(ex["pass"]),
        "ext_halt": str(ex["halt"]),
        "ext_indet": str(ex["indeterminate"]),
        "ext_na": str(ex["not_applicable"]),
        "ext_nobs": str(ex["not_observable"]),
        "cons_seeds": str(s["external_consequence"]["n_seeds"]),
        "cons_sel_changed": str(s["external_consequence"]["n_seeds_selection_changed"]),
        "cons_overlap_pct": str(s["external_consequence"]["overlap_original_pct_of_validation_support"]),
        "cons_det_orig": str(s["external_consequence"]["detected_original"]),
        "cons_det_corr": str(s["external_consequence"]["detected_corrected"]),
        "lag_records": str(g["n_records"]),
        "lag_object_median_h": str(g["median_lag_h_object_level"]),
        # DELIBERATELY NOT REQUIRED: the record-pooled epoch-ahead percentage, the largest
        # object's record share, and the record-pooled median lag. The manuscript no longer
        # quotes any of them, because pooling over records across eleven objects with unequal
        # record counts is the wrong unit -- the largest object supplies most of the records, so
        # a pooled figure is that object's. They remain in the artifact
        # (publication_lag.{frac_epoch_ahead_record_pooled, largest_object_record_share,
        # median_lag_h_record_pooled}) so the object-level figures can be checked against them.
        # Removing a key here is how a number could silently stop being claimed, so the reason
        # is recorded rather than left to a reader to infer from a diff.
        "rule_count": str(s["rule_count"]),
        "fault_class_count": str(n),
        "chronological": f"{s['chronological_detected_count']}/{n}",
        "contract": f"{s['contract_detected_count']}/{n}",
        "injected_cells": f"{s['injected_cell_count']}/{s['injected_cell_count']}",
        "source_loc": str(s["source_loc"]),
        "red_fixture": str(s["detectors_with_red_fixture"]),
        "l47_clean_paths": str(c["clean_paths_evaluated"]),
        "l47_false_halts": str(c["clean_false_halts"]),
        "l47_rate": str(c["measured_clean_false_halt_rate"]),
        "l47_alpha": str(c["nominal_alpha"]),
        "l47_wilson": f"[{lo},{hi}]",
    }


# \artv{key}{rendered}. The rendered argument may itself contain braces (\num{450}), so
# match one level of nesting rather than [^}]*.
_ARTV = re.compile(r"\\artv\{([a-z0-9_]+)\}\{((?:[^{}]|\{[^{}]*\})*)\}")


def _strip_tex_comments(tex: str) -> str:
    """Drop % comments, keeping escaped \% intact."""
    out = []
    for line in tex.splitlines():
        i, n = 0, len(line)
        while i < n:
            if line[i] == "\\" and i + 1 < n:
                i += 2
                continue
            if line[i] == "%":
                line = line[:i]
                break
            i += 1
        out.append(line)
    return "\n".join(out)


def check_artifact_sites(manuscript: str) -> list[str]:
    """Assert every headline number AGREES with the artifact at its own claim site.

    This replaced a required-PRESENCE check that asked only whether the artifact's value
    appeared somewhere in the sources. A reviewer defeated that twice in one sitting: the
    count 17 was satisfied by the seventeen fault classes regardless of what it was meant to
    report, and after the measured false-halt rate moved to 0.038 the check still passed
    because Fig. 2 contains the ICC coordinate (0.038,0.05). A number is bound to the
    sentence that claims it, or it is not bound.
    """
    want = artifact_values()
    bad: list[str] = []
    seen: set[str] = set()
    # Commented-out text is not a claim. Without this the gate matched the preamble comment
    # that documents the \artv convention and reported its literal placeholder as a bad key.
    manuscript = _strip_tex_comments(manuscript)
    for m in _ARTV.finditer(manuscript):
        key, rendered = m.group(1), m.group(2)
        if key not in want:
            bad.append(f"ARTIFACT SITE: \\artv{{{key}}} names no artifact field; "
                       f"expected one of {sorted(want)}")
            continue
        seen.add(key)
        got, expect = _norm(rendered), _norm(want[key])
        # Numeric equality where both sides parse as numbers, so 100 and 100.0 agree. String
        # comparison still applies to intervals, ratios and spelled-out counts.
        same = got == expect
        if not same:
            try:
                same = float(got) == float(expect)
            except ValueError:
                same = False
        if not same:
            bad.append(f"ARTIFACT SITE: \\artv{{{key}}} renders {rendered!r} "
                       f"(= {got}) but the artifact says {want[key]!r}")
    for key in sorted(set(want) - seen):
        bad.append(f"ARTIFACT SITE: no \\artv{{{key}}} anywhere in the manuscript -- "
                   f"the artifact reports {want[key]!r} and nothing claims it")
    return bad


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
    ex = s["external_artifact_study"]
    co = s["external_consequence"]
    if not co["detector_unmodified"]:
        bad.append("CONSEQUENCE: the detector hash differs from the pre-registration, so the "
                   "external-consequence experiment is void")
    if co["data_source_status"] not in ("CHECKSUM_VERIFIED_MIRROR", "ORIGINAL_SOURCE"):
        bad.append(f"CONSEQUENCE: data source status is {co['data_source_status']}, not a "
                   "qualified source")
    if (co["l41_original"], co["l41_corrected"]) != ("HALT", "PASS"):
        bad.append(f"CONSEQUENCE: L4.1 went {co['l41_original']} -> {co['l41_corrected']}, not "
                   "HALT -> PASS, so the intervention did not do what the paper says")
    if not ex["detector_unmodified"]:
        bad.append("EXTERNAL: contract_layers.py sha256 differs from the pre-registration hash "
                   "-- a detector was changed after the external artifact was inspected, which "
                   "invalidates the external study")
    if ex["frozen_commit"] != "2e6c5b6c3558e7835601519b7bdef37c649bdbdc":
        bad.append(f"EXTERNAL: frozen third-party commit is {ex['frozen_commit']}, not the "
                   "commit the study was registered against")
    if s["real_l47_application"]["contract_layers_sha256"] != ex["contract_layers_sha256"]:
        bad.append("EXTERNAL: the real-data application and the external study ran against "
                   "different versions of the contract")
    if s["runtime_seconds"] >= 2.0:
        bad.append(f"RUNTIME: artifact reports {s['runtime_seconds']} s, but the "
                   "manuscript claims the sweep runs in under 2 s")
    # 40 ms, not 30. The measured figure ranges about 26-31 ms across runs on the same machine,
    # so a 30 ms bound is not a bound -- it passed on a quiet machine and failed once the machine
    # was busy, which the gate caught. A stated bound has to hold under the load the measurement
    # actually sees, and re-running until a tight bound passes would be tuning a claim to a
    # measurement rather than the other way round.
    if s["runtime_ms_per_condition"] >= 40.0:
        bad.append(f"RUNTIME: artifact reports {s['runtime_ms_per_condition']} ms per "
                   "condition, but the manuscript claims under 40 ms")

    # The banlist permits citing the labelled-vs-censored SMD observation ONLY with its
    # framing (INVALID_RESULT_BANLIST.md): a stopped pipeline, never a general rate. Grepping
    # for the banned rate cannot enforce that the framing is PRESENT, so require it directly --
    # and require it in the SAME FILE. A first version checked the concatenation of all
    # eleven sources, so the word "stopped" anywhere in the README satisfied a claim made in
    # the manuscript; stripping the framing from the manuscript alone did not fire it.
    for q in srcs:
        text = q.read_text()
        if re.search(r"standardi[sz]ed mean difference", text) \
                and not re.search(r"\bstopped\b", text):
            bad.append(f"FRAMING: {q.relative_to(ROOT)} cites the labelled-vs-censored SMD "
                       "observation without the mandatory 'stopped pipeline' framing "
                       "(submission_finalization/INVALID_RESULT_BANLIST.md)")

    # Required-presence applies to the MANUSCRIPT only; a doc need not restate every
    # number, but nothing anywhere may contradict the artifact (handled by the pattern
    # scans above plus the runtime bound).
    manuscript = "\n".join(p.read_text() for p in srcs
                           if p.suffix == ".tex" or p.suffix == ".bib")
    bad += check_artifact_sites(manuscript)

    if bad:
        print("BANLIST / CLAIM GATE VIOLATION -- build refused:")
        for b in bad:
            print("  " + b)
        return 1
    for e in exempt:
        print(f"  permitted: {e}")
    print(f"check_banlist: {len(srcs)} file(s) clean; {len(BANNED_PATTERNS)} banned + "
          f"{len(WITHDRAWN_CLAIMS)} withdrawn patterns, "
          f"{len(artifact_values())} artifact numbers bound at named claim sites, "
          f"{len(exempt)} permitted mention(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
