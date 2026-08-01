#!/usr/bin/env python3
"""Refuse a deck whose numbers have drifted from the evidence artifact.

Three checks:
  1. numbers.tex is current -- regenerating it changes nothing.
  2. every \\N... macro a slide uses is actually defined.
  3. the figures the speaker outline repeats in prose, where no macro protects them,
     still match the artifact.

    python talk/check_numbers.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUMMARY = HERE.parent / "evaluation" / "results" / "final_summary.json"


def main() -> int:
    before = (HERE / "numbers.tex").read_text() if (HERE / "numbers.tex").exists() else ""
    subprocess.run([sys.executable, str(HERE / "gen_numbers.py")], capture_output=True)
    after = (HERE / "numbers.tex").read_text()
    if before != after:
        print("talk/check: FAIL -- numbers.tex was stale; regenerated, now rebuild the deck")
        return 1

    src = ((HERE / "orbit_evidence_talk.tex").read_text()
           + "".join(p.read_text() for p in sorted((HERE / "figures").glob("*.tex"))))
    used = set(re.findall(r"\\(N[A-Za-z]+)\b", src))
    have = set(re.findall(r"\\newcommand\{\\(N[A-Za-z]+)\}", after))
    missing = sorted(used - have)
    if missing:
        print(f"talk/check: FAIL -- slides use undefined artifact macros {missing}")
        return 1

    a = json.loads(SUMMARY.read_text())
    d1 = a["real_l47_alongtrack"]["D1_pass_in_elementset"]
    must = {
        "rule count": str(a["rule_count"]),
        "clean false halts": str(a["l47_calibration"]["clean_false_halts"]),
        "clean paths": str(a["l47_calibration"]["clean_paths_evaluated"]),
        "along-track ICC": str(d1["icc"]),
        "along-track p": str(d1["p_value"]),
        "seeds changed": f'{a["external_consequence"]["n_seeds_selection_changed"]}/'
                         f'{a["external_consequence"]["n_seeds"]}',
    }
    out = (HERE / "SPEAKER_OUTLINE.md").read_text()
    absent = sorted(k for k, v in must.items() if v not in out)
    if absent:
        print(f"talk/check: FAIL -- SPEAKER_OUTLINE.md has drifted from the artifact: {absent}")
        return 1

    print(f"talk/check: PASS -- {len(used)} artifact-bound values in the deck, "
          f"{len(must)} verified in the outline, none stale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
