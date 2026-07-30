#!/usr/bin/env python3
"""Fail the build if any banned result appears in the manuscript source.

Source of truth: ../INVALID_RESULT_BANLIST.md. Run before every compile.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

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

def main() -> int:
    srcs = sorted(HERE.glob("*.tex")) + sorted(HERE.glob("*.bib"))
    if not srcs:
        print("check_banlist: no source files found")
        return 1
    bad: list[str] = []
    for p in srcs:
        text = p.read_text()
        for pat, label in BANNED_PATTERNS:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                line = text[:m.start()].count("\n") + 1
                bad.append(f"{p.name}:{line}: [{label}] matched {m.group(0)!r}")
    if bad:
        print("BANLIST VIOLATION -- build refused:")
        for b in bad:
            print("  " + b)
        return 1
    print(f"check_banlist: {len(srcs)} file(s) clean, "
          f"{len(BANNED_PATTERNS)} patterns checked")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
