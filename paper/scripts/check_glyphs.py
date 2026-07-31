#!/usr/bin/env python3
"""Assert no text in the built PDF renders below the declared legibility floor.

WHY THIS EXISTS. Three figures are drawn on an oversized tikz canvas and squeezed into the
column with \\resizebox, which scales declared font sizes by the width ratio. A font declared
\\scriptsize can therefore reach the page at 4.6 pt. Two such defects shipped and were caught by
eye rather than by the build:

  * Fig. 2's single-character axis markers at 4.56 pt;
  * Fig. 3's small-caps WOULD HALT at 5.28 pt.

An earlier ad-hoc check missed both because it filtered to lowercase words longer than three
characters -- so single glyphs and small caps, exactly the shrunk cases, were skipped. This
measures every text span, and the effective size is the declared size times the span's
transformation matrix scale, which is what \\resizebox changes.

Not measured from ink bounding boxes: a box's height is the glyph's ink extent, so a lowercase
word without ascenders reports roughly its x-height (~0.45x the font size) and a run of digits
reports its cap height. Both understate, and the first understates by more than the margin
being checked.

Run: python paper/scripts/check_glyphs.py [--floor 6.4]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PDF = Path(__file__).resolve().parents[1] / "icc_main.pdf"
FLOOR_PT = 6.4

# Two sizes below the floor are set by IEEEtran and by LaTeX's own math sizing, not by this
# paper, and appear in every submission using this class:
#
#   6.38 pt -- small caps inside a caption. IEEEtran sets table captions in small caps
#              wholesale, so ~85 spans on the Table I page land here by class default.
#   5.98 pt -- a math subscript inside a \footnotesize caption ($t_d$ in Fig. 1), which is
#              LaTeX's standard scriptstyle reduction of the caption size.
#
# They are exempted by EXACT value, never by a lowered floor. A lowered floor would also
# admit a genuinely shrunk figure label at 5.99 or 6.37 pt -- which is the defect class this
# script exists to catch, and the one it did catch: \textsc{halt} declared \scriptsize inside
# Fig. 2's \resizebox reached the page at 5.55 pt. Widening the rule to accommodate a
# measurement is the detector-design cycle the contract in this paper exists to prevent; the
# author-controlled figure text was raised to clear the floor instead.
CLASS_SIZES = frozenset({6.38, 5.98})


def spans(pdf: Path):
    """Yield (page_number, effective_pt, text) for every non-blank text span."""
    import fitz  # PyMuPDF

    with fitz.open(pdf) as doc:
        for pno, page in enumerate(doc, start=1):
            for block in page.get_text("rawdict")["blocks"]:
                for line in block.get("lines", ()):
                    # span["size"] is already the size as rendered, i.e. the declared size
                    # after the \resizebox scale -- which is the number that matters here.
                    for span in line.get("spans", ()):
                        text = "".join(c["c"] for c in span.get("chars", ())).strip()
                        if not text:
                            continue
                        yield pno, round(float(span["size"]), 2), text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", type=float, default=FLOOR_PT)
    ap.add_argument("--pdf", type=Path, default=PDF)
    ap.add_argument("--show", type=int, default=6, help="how many smallest spans to print")
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"check_glyphs: {args.pdf} not built", file=sys.stderr)
        return 2
    try:
        found = sorted(spans(args.pdf))
    except ImportError:
        # Visible, never silent: an invariant that quietly stops being checked is how the
        # two defects above shipped in the first place.
        print("  min_glyph_pt      SKIP (PyMuPDF absent; pip install pymupdf to enforce)")
        return 0

    by_size = sorted(found, key=lambda r: r[1])
    smallest = by_size[0][1]
    under = [r for r in by_size if r[1] < args.floor and r[1] not in CLASS_SIZES]

    print(f"  min_glyph_pt      {smallest}  (want >= {args.floor} or class-set)  "
          f"{'FAIL' if under else 'OK'}")
    for pno, pt, text in by_size[:args.show]:
        mark = "<<" if pt < args.floor and pt not in CLASS_SIZES else "  "
        print(f"      {mark} {pt:5.2f} pt  p{pno}  {text[:58]!r}")
    if under:
        print(f"check_glyphs: FAIL -- {len(under)} author-set span(s) below {args.floor} pt",
              file=sys.stderr)
        return 1
    exempt = sum(1 for r in by_size if r[1] in CLASS_SIZES)
    print(f"check_glyphs: PASS -- {len(found)} spans; "
          f"{len(found) - exempt} author-set, all >= {args.floor} pt; "
          f"{exempt} class-set at {sorted(CLASS_SIZES)} pt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
