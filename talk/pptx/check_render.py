#!/usr/bin/env python3
"""Measure the RENDERED deck for overflow, instead of trusting the builder's geometry.

Two failure modes got through the source-level checks and were only visible in pixels:

  * a three-line action title spilling past its box and colliding with the divider rule and the
    slide body (slides 2, 5, 7, 8);
  * a right-hand column running off the bottom edge and over the citation line (slides 7, 8).

Both are measurable. `pdftotext -bbox` reports every word's bounding box in points, so this
script re-reads the exported PDF and fails if any word crosses one of two lines:

  TITLE_RULE   the divider under the action title -- a word starting above it must end above it
  SAFE_BOTTOM  the last usable baseline -- nothing may extend past it

Run render.sh first (it drives the PowerPoint export). Without a PDF this exits 0 with a notice
rather than pretending the deck was verified.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Reusable across decks: pass a .pptx path to check that deck instead of the talk.
_target = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / "orbit_evidence_talk.pptx"
PPTX = _target
PDF = _target.with_suffix(".pdf")

PT = 72.0
SAFE_BOTTOM = 5.50 * PT     # slide is 5.625 in; the citation baseline ends by 5.45
TOL = 2.0                   # points: ignore sub-3-thousandths-of-an-inch rounding
def discover_rules(pptx_path):
    """Find each slide's title divider by MEASURING the deck, not by hardcoding page numbers.

    The divider is the thin full-width bar action_title() and appendix() draw under the title, so
    its geometry identifies it: a shape at least 8" wide and under 0.06" tall. Detecting it beats
    a hardcoded map two ways -- the two title patterns sit at different heights (1.20" and 1.48"),
    and a slide with no action title at all (Conclusions, References, the title slide) correctly
    gets no rule instead of being false-flagged against a line it does not have.
    """
    from pptx import Presentation as _P
    from pptx.util import Emu
    rules = {}
    for i, sl in enumerate(_P(str(pptx_path)).slides, start=1):
        for sh in sl.shapes:
            try:
                w, h, top = Emu(sh.width).inches, Emu(sh.height).inches, Emu(sh.top).inches
            except (TypeError, AttributeError):
                continue
            if w >= 8.0 and h <= 0.06 and 0.5 < top < 2.5:
                rules[i] = top * PT
                break
    return rules


RULE_AT = discover_rules(_target) if _target.exists() else {}


def main() -> int:
    if not PDF.exists():
        print(f"pptx/render: SKIP -- {PDF.name} absent; run render.sh to verify pixels")
        return 0
    if PPTX.exists() and PDF.stat().st_mtime < PPTX.stat().st_mtime:
        print(f"pptx/render: FAIL -- {PDF.name} is older than the .pptx; re-run render.sh")
        return 1

    out = subprocess.run(["pdftotext", "-bbox", str(PDF), "-"],
                         capture_output=True, text=True, check=True).stdout

    pages = re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', out, re.S)
    if not pages:
        print("pptx/render: FAIL -- pdftotext produced no pages")
        return 1

    below, straddle, overlap = [], [], []
    for idx, (_pw, _ph, body) in enumerate(pages, start=1):
        for m in re.finditer(
                r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">'
                r'(.*?)</word>', body):
            x0, y0, x1, y1, w = (float(m.group(1)), float(m.group(2)),
                                 float(m.group(3)), float(m.group(4)), m.group(5))
            if y1 > SAFE_BOTTOM + TOL:
                below.append((idx, round(y1 / PT, 3), w))
            # a word that BEGINS in the title band must also END there; one that begins below it
            # is body text and is unconstrained by the rule.
            rule = RULE_AT.get(idx)
            if rule is not None and y0 < rule - TOL and y1 > rule + TOL:
                straddle.append((idx, round(y0 / PT, 3), round(y1 / PT, 3), w))

        # Two glyph boxes that overlap are a visual collision, whatever their declared
        # geometry said: a right-hand column running under a full-width citation shows up here
        # and nowhere else, because neither element crosses a boundary of its own.
        ws = [(float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)),
               m.group(5)) for m in re.finditer(
                  r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">'
                  r'(.*?)</word>', body)]
        for i, (ax0, ay0, ax1, ay1, aw) in enumerate(ws):
            for bx0, by0, bx1, by1, bw in ws[i + 1:]:
                ix, iy = min(ax1, bx1) - max(ax0, bx0), min(ay1, by1) - max(ay0, by0)
                if ix <= 0 or iy <= 0:
                    continue
                small = min((ax1 - ax0) * (ay1 - ay0), (bx1 - bx0) * (by1 - by0))
                if small > 0 and (ix * iy) / small > 0.25:
                    overlap.append((idx, aw, bw, round(ix * iy / small, 2)))

    problems = 0
    if overlap:
        print(f"pptx/render: FAIL -- {len(overlap)} overlapping word pair(s) "
              f"(two elements colliding):")
        for idx, aw, bw, frac in overlap[:12]:
            print(f"   slide {idx:2d}  {aw!r} x {bw!r}  ({frac:.0%} of the smaller box)")
        problems += 1
    if straddle:
        print(f"pptx/render: FAIL -- {len(straddle)} word(s) cross their title rule "
              f"(a third title line):")
        for idx, y0, y1, w in straddle[:12]:
            print(f'   slide {idx:2d}  y {y0}"-{y1}"  {w!r}')
        problems += 1
    if below:
        print(f"pptx/render: FAIL -- {len(below)} word(s) extend past the safe bottom at "
              f"{SAFE_BOTTOM / PT:.2f}\":")
        for idx, y1, w in below[:12]:
            print(f'   slide {idx:2d}  bottom {y1}"  {w!r}')
        problems += 1
    if problems:
        return 1

    words = sum(len(re.findall(r"<word ", b)) for _, _, b in pages)
    print(f"pptx/render: OK -- {len(pages)} pages, {words} words measured; "
          f"none crossing the title rule, none past the safe bottom")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
