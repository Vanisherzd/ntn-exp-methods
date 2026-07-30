#!/usr/bin/env python3
"""Assert the submission invariants against the LaTeX log. Non-zero exit on failure."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LOG = HERE / "build" / "icc_main.log"
EXPECTED_PAGES = 6


def main() -> int:
    if not LOG.exists():
        print(f"verify_build: {LOG} not found; build first")
        return 1
    log = LOG.read_text(errors="ignore")
    pages = re.findall(r"Output written on .*\((\d+) pages", log)
    checks = {
        "pages": (int(pages[-1]) if pages else -1, EXPECTED_PAGES),
        # `.latexmkrc` passes -file-line-error, which reformats errors as
        # "./file.tex:NNN: message" and DROPS the "! " prefix. Matching only "^! "
        # therefore reported zero errors on a genuinely broken build -- the invariant
        # advertised as mechanically enforced never fired. Both forms are matched now.
        "latex_errors": (len(re.findall(r"^(?:! |\./.*?:\d+: )", log, re.M)), 0),
        "undefined_refs": (len(re.findall(r"LaTeX Warning: Reference", log)), 0),
        "undefined_cites": (len(re.findall(r"Citation .* undefined", log)), 0),
        "overfull_boxes": (len(re.findall(r"Overfull \\hbox", log)), 0),
    }
    ok = True
    for name, (got, want) in checks.items():
        good = got == want
        ok &= good
        print(f"  {name:16s} {got!s:>4}  (want {want})  {'OK' if good else 'FAIL'}")
    print("verify_build:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
