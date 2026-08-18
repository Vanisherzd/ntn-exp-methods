#!/usr/bin/env python3
"""Build the PowerPoint deck for Orbit-Evidence.

This is a SECOND rendering of the frozen talk, not a replacement for it. The beamer deck at
talk/orbit_evidence_talk.tex (tag talk/orbit-evidence-reviewer-proof-2026-08) stays untouched;
this file produces a .pptx that obeys the academic-pptx skill's content and design standards:
action titles, one exhibit per results slide, a 20 pt body floor, a References slide, and a
Conclusions slide as the last non-appendix slide.

NUMBERS ARE NEVER TYPED HERE. Every figure is read from talk/numbers.tex (itself generated
from evaluation/results/final_summary.json) or from the curve artifact directly. Retyping one
would reintroduce exactly the drift the manuscript's claim gate exists to prevent, and
check_deck.py fails if a macro this file asks for has gone missing.

CLAIM DISCIPLINE. Wording is bound by talk/TALK_CLAIM_LEDGER.md's prohibited column, the
"## Never say" block of talk/SPEAKER_OUTLINE.md, and the 14 SEMANTIC_LINT rules in
talk/gen_ledger.py. No claim in this deck is new; the rebuild changes titles and sequence only.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
TALK = HERE.parent
ROOT = TALK.parent
OUT = HERE / "orbit_evidence_talk.pptx"

# --------------------------------------------------------------------------------------------
# numbers: parsed, never retyped
# --------------------------------------------------------------------------------------------
_MACROS = dict(
    re.findall(r"\\newcommand\{\\N([A-Za-z]+)\}\{([^}]*)\}", (TALK / "numbers.tex").read_text())
)


def n(key: str) -> str:
    """A macro from talk/numbers.tex. Missing key is a hard failure, not a blank on a slide."""
    if key not in _MACROS:
        raise SystemExit(f"build_deck: numbers.tex has no macro N{key} -- run `make -C talk`")
    return _MACROS[key]


CURVE = json.loads((ROOT / "evaluation" / "results" / "l47_power_curve.json").read_text())

# --------------------------------------------------------------------------------------------
# skill design tokens (academic-pptx SKILL.md Step 3 + slide_patterns.md Global Defaults)
# --------------------------------------------------------------------------------------------
BG = RGBColor(0xFF, 0xFF, 0xFF)
PRIMARY = RGBColor(0x1F, 0x4E, 0x79)
ACCENT = RGBColor(0x2E, 0x75, 0xB6)
BODY = RGBColor(0x2D, 0x2D, 0x2D)
MUTED = RGBColor(0x77, 0x77, 0x77)
RULE = RGBColor(0xCC, 0xCC, 0xCC)
HILITE = RGBColor(0xFF, 0xF2, 0xCC)
HILITE_LN = RGBColor(0xE6, 0xC8, 0x00)
HILITE_TX = RGBColor(0x7A, 0x52, 0x00)
PANEL = RGBColor(0xEB, 0xF3, 0xFA)
ONDARK = RGBColor(0xA0, 0xBB, 0xDD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FACE = "Arial"
SZ_TITLE, SZ_HDR, SZ_BODY, SZ_LABEL, SZ_CITE = 26, 22, 20, 16, 13
# Diagram and exhibit labels sit on the skill's chart-label floor (16-18 pt), not in the
# 12-14 pt citation band: they are read from the back of a room, a citation is not.
SZ_DIAG = 16
MARGIN = 0.5
SW, SH = 10.0, 5.625  # skill coordinates assume 16:9 at 10 x 5.625 in

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)
BLANK = prs.slide_layouts[6]

# Body-word budget: the skill caps content-slide body prose at ~40 words. Exhibit labels,
# axis ticks and legend glosses are not prose and are tracked separately -- check_deck.py
# re-counts from the built file and enforces the cap, so this ledger is advisory only.
WORDS: dict[int, int] = {}


# --------------------------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------------------------
def slide(dark: bool = False):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = PRIMARY if dark else BG
    return s


def box(s, x, y, w, h, fill=None, line=None, lw=0.7, shape=MSO_SHAPE.RECTANGLE, radius=None):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.shadow.inherit = False  # python-pptx autoshapes default to a drop shadow; the skill bans decoration
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    sh.text_frame.word_wrap = True
    return sh


def _para_text(para):
    return para if isinstance(para, str) else "".join(t for t, _ in para)


def _fits(paras, w, h, size, space_after):
    """Estimated wrapped height against the declared box. Uses the same conservative advance
    widths as label1(), so it errs toward asking for a taller box."""
    lines = 0
    for para in paras:
        for seg in _para_text(para).split("\n"):
            lines += max(1, math.ceil(est_width(seg, size) / max(w - 0.04, 0.1) - 1e-6))
    need = lines * 1.21 * size / 72.0 + max(0, len(paras) - 1) * space_after / 72.0
    return need <= h + 0.02, need, lines


def text(s, x, y, w, h, runs, size=SZ_BODY, color=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, space_after=0, line_spacing=None, fit=False):
    """runs: str, or list of paragraphs; a paragraph is a str or a list of (text, bold) pairs."""
    _paras = [runs] if isinstance(runs, str) else runs
    if fit:
        ok, need, lines = _fits(_paras, w, h, size, space_after)
        if not ok:
            raise SystemExit(
                f"build_deck: text needs {need:.2f}\" ({lines} line(s) at {size} pt in "
                f"{w:.2f}\") but the box gives {h:.2f}\":\n  "
                f"{_para_text(_paras[0])[:90]!r}")
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    paras = [runs] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if space_after:
            p.space_after = Pt(space_after)
        if line_spacing:
            p.line_spacing = line_spacing
        pieces = [(para, bold)] if isinstance(para, str) else para
        for t, b in pieces:
            r = p.add_run()
            r.text = t
            r.font.name = FACE
            r.font.size = Pt(size)
            r.font.bold = b
            r.font.color.rgb = color
    tf.vertical_anchor = anchor
    return tb


# Arial advance widths as a fraction of point size, coarse but enough to catch a label that will
# wrap out of a fixed box. Capitals and digits are the expensive class -- "INDETERMINATE" needs
# 1.79" at 16 pt and silently broke out of a 1.72" box until this existed. Rendering found it;
# the render gate could not, because it only measures vertical bounds.
# Deliberately CONSERVATIVE: it errs toward "widen the box", which is the safe direction. A
# label it rejects by a few hundredths may in fact fit; a label it accepts will not wrap.
_W_UPPER, _W_LOWER, _W_SPACE = 0.66, 0.52, 0.28


def est_width(t, size):
    total = 0.0
    for ch in t:
        if ch == " ":
            total += _W_SPACE
        elif ch.isupper() or ch.isdigit():
            total += _W_UPPER
        else:
            total += _W_LOWER
    return total * size / 72.0


# content_guidelines.md section 2: "Title length: One to two lines. If more is needed, the point
# is not sharp enough yet." At 26 pt Arial Bold across a 9" box that is ~55 characters a line, so
# a third line is both a skill violation AND an overflow that collides with the slide body --
# rendering caught four of these before this gate existed.
# Calibrated against the render: 95 characters still wrap to two lines at 26 pt, 100 wrap to
# three and collide with the divider. A character count can only approximate this -- digits and
# brackets are narrower than 'm' -- so this is an EARLY WARNING. check_render.py measures the
# exported PDF and is the authority.
TITLE_CHARS = {26: 96, 24: 104}


def action_title(s, sentence, size=SZ_TITLE, h=0.95):
    """A complete sentence stating the takeaway. The skill's single most important rule."""
    cap = TITLE_CHARS[size]
    if len(sentence) > cap:
        raise SystemExit(f"build_deck: title runs to a third line at {size} pt "
                         f"({len(sentence)} > {cap} chars) -- sharpen it:\n  {sentence}")
    text(s, MARGIN, 0.22, SW - 2 * MARGIN, h, sentence, size=size, color=PRIMARY, bold=True)
    box(s, MARGIN, 0.22 + h + 0.03, SW - 2 * MARGIN, 0.025, fill=RULE)
    return 0.22 + h + 0.13


def cite(s, source, w=None):
    """Bottom-of-slide source line. A long one needs two lines, and a one-line box would push
    the overflow off the slide edge. On a slide with a right-hand column, pass w so the second
    line cannot run underneath it -- the overlap gate caught exactly that on slide 8."""
    w = (SW - 2 * MARGIN) if w is None else w
    two = len(source) > int(w * 6.8)
    y = SH - (0.62 if two else 0.42)
    text(s, MARGIN, y, w, 0.5 if two else 0.3, source, size=13, color=MUTED)


def bullets(s, x, y, w, h, items, size=SZ_BODY, space=10):
    """items: list of (lead, rest) -- lead is bolded. '' lead gives an unlabelled bullet."""
    paras = []
    for lead, rest in items:
        pieces = [("\u2022  ", False)]
        if lead:
            pieces.append((lead, True))
        pieces.append((rest, False))
        paras.append(pieces)
    tb = text(s, x, y, w, h, paras, size=size, space_after=space)
    hang = int(Inches(0.26))
    for para in tb.text_frame.paragraphs:
        pPr = para._p.get_or_add_pPr()
        pPr.set("marL", str(hang))
        pPr.set("indent", str(-hang))
    return tb


def words(idx, *strings):
    WORDS[idx] = WORDS.get(idx, 0) + sum(len(t.split()) for t in strings)


def arrow(s, x, y, w, h=0.16, color=ACCENT):
    a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    a.shadow.inherit = False
    a.fill.solid()
    a.fill.fore_color.rgb = color
    a.line.fill.background()
    return a


def label(s, x, y, w, h, t, size=SZ_LABEL, color=BODY, bold=False, align=PP_ALIGN.CENTER):
    return text(s, x, y, w, h, t, size=size, color=color, bold=bold, align=align)


def label1(s, x, y, w, h, t, size=SZ_LABEL, color=BODY, bold=False, align=PP_ALIGN.CENTER,
           pad=0.16):
    """A label that MUST stay on one line inside its box."""
    need = est_width(t, size) * (1.06 if bold else 1.0)
    if need > w - pad:
        raise SystemExit(f"build_deck: label needs {need:.2f}\" but the box gives "
                         f"{w - pad:.2f}\" -- widen it or shorten the text:\n  {t!r}")
    return label(s, x, y, w, h, t, size=size, color=color, bold=bold, align=align)


# ============================================================================================
# 1 -- title slide
# ============================================================================================
s = slide(dark=True)
text(s, 0.7, 1.00, 8.6, 2.1,
     ["Chronological separation is necessary for satellite machine learning,",
      "but it is not sufficient \u2014 and the missing conditions can be made executable"],
     size=30, color=WHITE, bold=True, space_after=6)
box(s, 0.7, 3.36, 2.0, 0.045, fill=ACCENT)
text(s, 0.7, 3.52, 8.6, 0.5,
     "Orbit-Evidence: Relational Validity Checks for Learning-Assisted "
     "Satellite Communication Experiments",
     size=16, color=ONDARK)
text(s, 0.7, 4.35, 8.6, 0.75,
     ["Anonymous Submission", "IEEE flagship workshop submission \u00b7 under review"],
     size=15, color=ONDARK, space_after=3)

# ============================================================================================
# 2 -- motivation / complication
# ============================================================================================
s = slide()
y = action_title(s, "Chronological splitting is right, but it constrains only what is "
                    "inside one realised dataset")
b = [("Availability \u2014 ", "it existed, but was it fetchable at decision time?"),
     ("Row membership \u2014 ", "which rows exist at all, and who decided"),
     ("Hidden state \u2014 ", "information that is not a column"),
     ("Statistical unit \u2014 ", "are two rows really independent?")]
label(s, MARGIN, y, 6.2, 0.32, "Four obligations a split cannot establish",
      size=SZ_HDR, color=ACCENT, bold=True, align=PP_ALIGN.LEFT)
bullets(s, MARGIN, y + 0.42, 6.2, 2.4, b, space=13)
words(2, *[lead + rest for lead, rest in b])

# the split, drawn as a line inside one table -- the exhibit, right-hand column
ex = 6.95
label(s, ex, y, 2.55, 0.28, "one realised dataset", size=SZ_LABEL, color=MUTED, bold=True)
for i in range(5):
    box(s, ex, y + 0.42 + 0.30 * i, 2.55, 0.24, fill=RGBColor(0xF2, 0xF4, 0xF7), line=RULE, lw=0.5)
sp = ex + 1.32
ln = box(s, sp, y + 0.36, 0.022, 1.72, fill=PRIMARY)
label(s, ex, y + 2.14, 1.3, 0.26, "train", size=SZ_DIAG, color=MUTED)
label(s, sp, y + 2.14, 1.25, 0.26, "test", size=SZ_DIAG, color=MUTED)
label(s, ex, y + 2.44, 2.55, 0.5,
      "a split is a predicate over these rows \u2014 none of the four is in this frame",
      size=SZ_DIAG, color=MUTED, align=PP_ALIGN.LEFT)
cite(s, "Bergmeir & Ben\u00edtez (2012), Inf. Sci.; Kaufman et al. (2012), TKDD; "
        "Kapoor & Narayanan (2023), Patterns")

# ============================================================================================
# 3 -- research question (its own slide, per the skill)
# ============================================================================================
s = slide()
y = action_title(s, "This work asks which obligations lie outside one realised dataset")
q = ("Which deployment-validity conditions lie outside one realised dataset \u2014 and can "
     "they become checks that fail loudly and abstain when the design cannot decide?")
box(s, 1.35, y + 0.22, 7.3, 1.62, fill=PANEL, line=ACCENT, lw=1.5,
    shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
text(s, 1.6, y + 0.42, 6.8, 1.25, q, size=19, color=PRIMARY,
     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
contrib = ("two relational checks inside a " + n("rules") +
           "-rule executable contract, tested on real and third-party data.")
text(s, MARGIN, y + 2.16, SW - 2 * MARGIN, 0.8,
     [[("Contribution: ", True), (contrib, False)]], size=SZ_BODY)
words(3, q, "Contribution: " + contrib)

# ============================================================================================
# 4 -- the pivot: row-local vs relational
# ============================================================================================
s = slide()
y = action_title(s, "Row-local validity is decidable from one run; "
                    "relational validity is not")
panels = [("across executions", "run A", "run B",
           "same recorded inputs, different result \u21d2 something unrecorded changed it"),
          ("across source states", "source\nat decision", "source\nlater",
           "present in the later source, past-dated, unavailable at decision time"),
          ("across aggregation levels", "declared\nunit", "coarser\nlevel",
           "rows sharing a parent still resemble each other \u21d2 not independent samples")]
pw = 2.85
for i, (hdr, a, bx, note) in enumerate(panels):
    x0 = MARGIN + i * (pw + 0.28)
    label(s, x0, y, pw, 0.3, hdr, size=SZ_LABEL, color=PRIMARY, bold=True)
    for j, t in enumerate((a, bx)):
        bb = box(s, x0 + j * 1.62, y + 0.42, 1.23, 0.82, fill=PANEL, line=PRIMARY, lw=0.7)
        label(s, x0 + j * 1.62, y + 0.42, 1.23, 0.82, t, size=SZ_LABEL, color=PRIMARY)
    arrow(s, x0 + 1.26, y + 0.75, 0.33, 0.16)
    label(s, x0, y + 1.40, pw, 1.1, note, size=SZ_DIAG, color=MUTED, align=PP_ALIGN.LEFT)
    if i < 2:
        box(s, x0 + pw + 0.13, y + 0.05, 0.012, 2.2, fill=RULE)
words(4, *[p[0] + " " + p[3] for p in panels])

# ============================================================================================
# 5 -- methods 1: the contract
# ============================================================================================
s = slide()
y = action_title(s, "Orbit-Evidence encodes the four obligations as " + n("rules") +
                    " executable rules in four layers")
stages = ["published\nstate", "predicted\nvisibility", "frozen\nregistry",
          "model,\nselection", "deployment", "label\nclosure"]
sw_, gap = 1.42, 0.13
for i, t in enumerate(stages):
    x0 = MARGIN + i * (sw_ + gap)
    box(s, x0, y, sw_, 0.66, fill=PANEL, line=PRIMARY, lw=0.7)
    label(s, x0, y, sw_, 0.66, t, size=SZ_DIAG, color=PRIMARY)
    if i < len(stages) - 1:
        arrow(s, x0 + sw_ + 0.005, y + 0.27, gap - 0.01, 0.12, color=MUTED)
layers = [("L1", "availability, membership", 0), ("L2", "physical, scheduling", 1),
          ("L3", "model-state causality", 3), ("L4", "independence, reproducibility", 4)]
ly = y + 1.15
box(s, MARGIN - 0.06, ly - 0.12, SW - 2 * MARGIN + 0.12, 1.26, fill=None, line=RULE, lw=0.5)
for tag, desc, col in layers:
    x0 = MARGIN + col * (sw_ + gap)
    box(s, x0, ly, sw_ + 0.55, 1.02, fill=RGBColor(0xF2, 0xF4, 0xF7), line=MUTED, lw=0.6)
    text(s, x0 + 0.08, ly + 0.10, sw_ + 0.39, 0.85,
         [[(tag + " ", True)], [(desc, False)]], size=SZ_DIAG, color=BODY)
    box(s, x0 + sw_ / 2, y + 0.68, 0.012, 0.45, fill=MUTED)
gloss = ("L1\u2013L4 are the four obligation layers the contract observes; the two relational "
         "checks live in L4")
text(s, MARGIN, ly + 1.30, SW - 2 * MARGIN, 0.6, gloss, size=SZ_BODY, color=BODY)
words(5, gloss)

# ============================================================================================
# 6 -- methods 2: the two relational checks + the three-valued verdict
# ============================================================================================
s = slide()
y = action_title(s, "L4.6 refutes declared completeness; L4.7 tests dependence one level "
                    "coarser, and abstains")
b6 = [("L4.6 \u2014 ", "same manifest hash, different output: a counterexample to declared "
                       "completeness"),
      ("L4.7 \u2014 ", "does dependence survive one declared level coarser, against a "
                       "permutation null?")]
bullets(s, MARGIN, y, 5.75, 2.2, b6, space=14)
text(s, MARGIN, y + 2.32, 5.75, 0.5,
     [[("Failure is evidence; success is not certification.", True)]],
     size=SZ_BODY, color=PRIMARY)
words(6, *[lead + rest for lead, rest in b6], "Failure is evidence; success is not certification.")

vx = 6.55
label1(s, vx, y - 0.04, 2.95, 0.3, "one of three verdicts", size=SZ_DIAG,
       color=MUTED, bold=True, align=PP_ALIGN.LEFT, pad=0.0)
verdicts = [("PASS", "not rejected"), ("HALT", "obligation violated"),
            ("INDETERMINATE", "the design cannot decide")]
for i, (v, g) in enumerate(verdicts):
    yy = y + 0.34 + i * 0.72
    box(s, vx, yy, 2.95, 0.62, fill=BG, line=PRIMARY, lw=0.7)
    text(s, vx + 0.12, yy + 0.07, 2.7, 0.5,
         [[(v, True)], [(g, False)]], size=SZ_DIAG, color=PRIMARY)

# ============================================================================================
# 7 -- result 1: calibration  [designated cut if running long]
# ============================================================================================
s = slide()
y = action_title(s, "The gate halts on " + n("cleanhalts") + " of " + n("cleanpaths") +
                    " clean evaluations \u2014 Wilson [" + n("wlo") + ", " + n("whi") +
                    "] contains the nominal " + n("alpha"))

# exhibit: the operating characteristic, from the curve artifact
px0, px1 = MARGIN + 0.45, MARGIN + 5.25
py0, py1 = y + 3.05, y + 0.18          # py0 = halt_prob 0, py1 = halt_prob 1
XMAX = 0.85


def cx(icc):
    return px0 + (px1 - px0) * (icc / XMAX)


def cy(p):
    return py0 - (py0 - py1) * p


box(s, px0, py1, 0.014, py0 - py1, fill=MUTED)                 # y axis
box(s, px0, py0, px1 - px0, 0.014, fill=MUTED)                 # x axis
for v in (0.0, 0.2, 0.4, 0.6, 0.8):
    box(s, cx(v), py0, 0.01, 0.07, fill=MUTED)
    label(s, cx(v) - 0.22, py0 + 0.09, 0.44, 0.22, f"{v:.1f}", size=SZ_DIAG, color=MUTED)
for v, t in ((0.0, "0"), (0.5, "0.5"), (1.0, "1.0")):
    box(s, px0 - 0.06, cy(v), 0.06, 0.01, fill=MUTED)
    label(s, px0 - 0.52, cy(v) - 0.11, 0.42, 0.22, t, size=SZ_DIAG, color=MUTED,
          align=PP_ALIGN.RIGHT)
label(s, px0, py0 + 0.34, px1 - px0, 0.26,
      "within-group resemblance (ICC)", size=SZ_DIAG, color=MUTED)
label(s, px0 + 0.12, py1 + 0.02, 1.6, 0.26, "P(HALT)", size=SZ_DIAG, color=MUTED,
      align=PP_ALIGN.LEFT)

alpha = float(n("alpha"))
box(s, px0, cy(alpha), px1 - px0, 0.01, fill=RGBColor(0xB0, 0xB0, 0xB0))
label(s, px1 - 2.05, cy(alpha) - 0.32, 2.05, 0.26, "nominal \u03b1 = " + n("alpha"),
      size=SZ_DIAG, color=MUTED, align=PP_ALIGN.RIGHT)

pts = sorted(((e["icc"], e["halt_prob"]) for e in CURVE["curve"]), key=lambda t: t[0])
for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
    c = s.shapes.add_connector(1, Inches(cx(x1)), Inches(cy(y1)),
                               Inches(cx(x2)), Inches(cy(y2)))
    c.line.color.rgb = RGBColor(0x9A, 0x9A, 0x9A)
    c.line.width = Pt(1.1)
for xv, yv in pts:
    d = 0.115
    m = box(s, cx(xv) - d / 2, cy(yv) - d / 2, d, d, fill=BG, line=PRIMARY, lw=1.4,
            shape=MSO_SHAPE.OVAL)
box(s, cx(0.5) + 0.16, cy(0.8) - 0.12, 1.55, 0.5, fill=HILITE, line=HILITE_LN, lw=1,
    shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
label(s, cx(0.5) + 0.16, cy(0.8) - 0.12, 1.55, 0.5,
      n("seeds") + "/" + n("seeds") + " halts\nat \u03c1 = 0.8", size=SZ_DIAG, color=HILITE_TX,
      bold=True)
label(s, cx(0.2) + 0.10, cy(0.25) - 0.14, 2.35, 0.26,
      "only " + n("powerlo") + " at \u03c1 = 0.2", size=SZ_DIAG, color=BODY, align=PP_ALIGN.LEFT)

hx = 6.35
label(s, hx, y + 0.06, 3.15, 0.3, "What to take away", size=SZ_HDR, color=ACCENT, bold=True,
      align=PP_ALIGN.LEFT)
b7 = [("", n("cleanhalts") + " halts in " + n("cleanpaths") + " clean evaluations \u2014 "
           + n("rate") + ", Wilson [" + n("wlo") + ", " + n("whi") + "]"),
      ("", "the interval, not the point, is the claim"),
      ("", "seven evaluated points, " + n("seeds") +
           " seeds each; the line guides the eye")]
bullets(s, hx, y + 0.46, 3.15, 2.6, b7, size=SZ_BODY - 1, space=13)
words(7, *[r for _, r in b7])
cite(s, "Wilson (1927), JASA; Shrout & Fleiss (1979), Psychol. Bull.; "
        "Winkler et al. (2014), NeuroImage", w=5.7)

# ============================================================================================
# 8 -- result 2: the unit problem in real catalogue data
# ============================================================================================
s = slide()
y = action_title(s, "The unit problem is real: \u03c1\u0302 = " + n("aticc") + " (p = " +
                    n("atp") + ") on " + n("atused") +
                    " in-track passes, and the gate halts")

# exhibit: the two denominators, then the verdict
ey = y + 0.10
label(s, MARGIN, ey, 5.5, 0.28, "cohort \u2192 primary analysis", size=SZ_DIAG, color=MUTED,
      bold=True, align=PP_ALIGN.LEFT)
coh = [("passes", n("passes")), ("element-set records", n("elsets")), ("objects", n("objects"))]
for i, (lab, val) in enumerate(coh):
    x0 = MARGIN + i * 1.86
    box(s, x0, ey + 0.34, 1.72, 0.94, fill=RGBColor(0xF2, 0xF4, 0xF7), line=MUTED, lw=0.6)
    text(s, x0 + 0.1, ey + 0.42, 1.52, 0.82, [[(val, True)], [(lab, False)]],
         size=SZ_DIAG, color=BODY)
arrow(s, MARGIN, ey + 1.42, 0.45, 0.14, color=MUTED)
label(s, MARGIN + 0.58, ey + 1.34, 4.9, 0.30,
      "\u2212" + n("atdropped") + " with no successor element set", size=SZ_DIAG, color=MUTED,
      align=PP_ALIGN.LEFT)
box(s, MARGIN, ey + 1.76, 5.5, 0.80, fill=PANEL, line=PRIMARY, lw=1.0)
text(s, MARGIN + 0.14, ey + 1.86, 5.2, 0.64,
     [[(n("atused") + " passes in " + n("atelsets") + " element sets", True)],
      [("primary in-track analysis", False)]], size=SZ_DIAG, color=PRIMARY)
# Two deliberate lines: the one-line guard showed the estimate, the bound, the p value and the
# verdict need 6.0" and the strip has 5.3".
box(s, MARGIN, ey + 2.62, 5.5, 0.80, fill=HILITE, line=HILITE_LN, lw=1.0)
label1(s, MARGIN, ey + 2.68, 5.5, 0.34,
       "\u03c1\u0302 = " + n("aticc") + "  \u00b7  p = " + n("atp") + "  \u2192  HALT",
       size=SZ_LABEL, color=HILITE_TX, bold=True)
label1(s, MARGIN, ey + 3.02, 5.5, 0.34,
       "one-sided lower bound " + n("atlo"), size=SZ_LABEL, color=HILITE_TX)

hx = 6.35
label(s, hx, y + 0.06, 3.15, 0.3, "What to take away", size=SZ_HDR, color=ACCENT, bold=True,
      align=PP_ALIGN.LEFT)
b8 = [("", n("atdropped") + " of the " + n("passes") +
           " passes have no successor, so the primary analysis uses " + n("atused")),
      ("", "the differenced quantity is an update increment between consecutive fits \u2014 "
           "not truth error"),
      ("", "for this observable and declared hierarchy only")]
bullets(s, hx, y + 0.46, 3.15, 2.7, b8, size=SZ_BODY - 1, space=13)
words(8, *[r for _, r in b8])
cite(s, "Data: U.S. Space Force, Space-Track GP/GP_HISTORY API; CCSDS 502.0-B-3",
     w=5.7)

# ============================================================================================
# 9 -- result 3: the frozen contract on a third-party artifact
# ============================================================================================
s = slide()
y = action_title(s, "The frozen contract runs unchanged externally: three rule "
                    "verdicts, two dispositions")
ey = y + 0.12
label(s, MARGIN, ey, 5.5, 0.28, "three rule verdicts", size=SZ_DIAG, color=PRIMARY, bold=True,
      align=PP_ALIGN.LEFT)
vd = [("PASS", n("extpass"), PANEL, 0.00, 1.45),
      ("HALT", n("exthalt"), HILITE, 1.52, 1.45),
      ("INDETERMINATE", n("extindet"), RGBColor(0xF2, 0xF4, 0xF7), 3.04, 2.46)]
for lab, val, fill, dx, bw in vd:
    x0 = MARGIN + dx
    box(s, x0, ey + 0.34, bw, 0.74, fill=fill, line=PRIMARY, lw=0.8)
    label1(s, x0 + 0.12, ey + 0.40, bw - 0.24, 0.30, val, size=SZ_DIAG, color=PRIMARY,
           bold=True, align=PP_ALIGN.LEFT, pad=0.0)
    label1(s, x0 + 0.12, ey + 0.70, bw - 0.24, 0.30, lab, size=SZ_DIAG, color=PRIMARY,
           align=PP_ALIGN.LEFT, pad=0.0)
label(s, MARGIN, ey + 1.30, 5.5, 0.28, "two applicability dispositions \u2014 not verdicts",
      size=SZ_DIAG, color=MUTED, bold=True, align=PP_ALIGN.LEFT)
# Stacked, not side by side: the one-line guard showed "5   N/OBS  not observable" needs 2.72"
# and a half-width box gives 2.44".
dp = [("N/A  not applicable", n("extna")), ("N/OBS  not observable", n("extnobs"))]
for i, (lab, val) in enumerate(dp):
    yy = ey + 1.64 + i * 0.50
    box(s, MARGIN, yy, 5.5, 0.44, fill=None, line=MUTED, lw=0.6)
    label1(s, MARGIN + 0.14, yy, 5.2, 0.44, val + "   " + lab, size=SZ_DIAG,
           color=MUTED, align=PP_ALIGN.LEFT, pad=0.0)

hx = 6.35
label(s, hx, y + 0.06, 3.15, 0.3, "What to take away", size=SZ_HDR, color=ACCENT, bold=True,
      align=PP_ALIGN.LEFT)
b9 = [("", "commit chosen before inspection; detector sha256 unchanged"),
      ("", "N/OBS is never scored as compliance"),
      ("", "hashes evidence non-modification, not correctness")]
bullets(s, hx, y + 0.46, 3.15, 2.5, b9, size=SZ_BODY - 1, space=13)
words(9, *[r for _, r in b9])
cite(s, "Artifact under study: Hundman et al. (2018), Proc. ACM SIGKDD", w=5.7)

# ============================================================================================
# 10 -- result 4: does correcting a violation change the experiment?
# ============================================================================================
s = slide()
y = action_title(s, "Correcting the violation changed the selected checkpoint " +
                    n("conschanged") + "/" + n("consseeds") +
                    "; downstream is not estimable")
ey = y + 0.18
label(s, MARGIN, ey, 5.5, 0.28, "pre-registered L4.1 correction", size=SZ_DIAG, color=MUTED,
      bold=True, align=PP_ALIGN.LEFT)
ba = [("before", n("consoverlap") + "%", "train/test overlap", HILITE, HILITE_LN),
      ("after", n("consoverlapcorr") + "%", "train/test overlap", PANEL, PRIMARY)]
for i, (tag, val, lab, fill, line) in enumerate(ba):
    x0 = MARGIN + i * 3.05
    box(s, x0, ey + 0.34, 2.35, 0.88, fill=fill, line=line, lw=0.9)
    text(s, x0 + 0.12, ey + 0.44, 2.1, 0.72,
         [[(val, True)], [(lab + "  (" + tag + ")", False)]], size=SZ_DIAG, color=PRIMARY)
arrow(s, MARGIN + 2.42, ey + 0.68, 0.55, 0.16)
box(s, MARGIN, ey + 1.34, 5.4, 0.6, fill=None, line=PRIMARY, lw=0.8)
label1(s, MARGIN, ey + 1.34, 5.4, 0.6, "rule verdict  HALT  \u2192  PASS", size=SZ_LABEL,
       color=PRIMARY, bold=True)
box(s, MARGIN, ey + 2.06, 5.4, 0.6, fill=HILITE, line=HILITE_LN, lw=1.0)
label1(s, MARGIN, ey + 2.06, 5.4, 0.6,
       "checkpoint changed " + n("conschanged") + "/" + n("consseeds") +
       " \u00b7 rerun bit-identical", size=SZ_LABEL, color=HILITE_TX, bold=True)

hx = 6.35
label(s, hx, y + 0.06, 3.15, 0.3, "What to take away", size=SZ_HDR, color=ACCENT, bold=True,
      align=PP_ALIGN.LEFT)
b10 = [("", "the intervention changed only the partition"),
       ("", "downstream endpoint not estimable at this paired-run resolution; min two-sided "
            "p = " + n("consminp")),
       ("", "no claim the upstream result is invalid, none that detection improved")]
bullets(s, hx, y + 0.46, 3.15, 2.7, b10, size=SZ_BODY - 1, space=13)
words(10, *[r for _, r in b10])
cite(s, "Artifact under study: Hundman et al. (2018), Proc. ACM SIGKDD", w=5.7)

# ============================================================================================
# 11 -- discussion 1: what is actually new
# ============================================================================================
s = slide()
y = action_title(s, "The contribution is the conversion: identify, falsify, encode \u2014 "
                    "and let the undecidable abstain")
steps = [("identify", "which obligation is relational rather than row-local"),
         ("choose", "the counterfactual that would falsify it"),
         ("encode", "it as a rule that can HALT \u2014 or abstain")]
for i, (verb, rest) in enumerate(steps):
    x0 = MARGIN + i * 3.10
    box(s, x0, y + 0.16, 2.9, 1.38, fill=PANEL, line=PRIMARY, lw=0.8)
    text(s, x0 + 0.14, y + 0.26, 2.62, 1.18,
         [[(verb, True)], [(rest, False)]], size=SZ_DIAG, color=PRIMARY, fit=True)
    if i < 2:
        arrow(s, x0 + 2.92, y + 0.78, 0.16, 0.14, color=MUTED)
b11 = [("", "ICC(1) and permutation inference are established, and neither is proposed here"),
       ("", "what is new: the permutation reference calibrates a gate \u2014 with an operating "
            "characteristic and an abstention state")]
bullets(s, MARGIN, y + 1.72, SW - 2 * MARGIN, 1.6, b11, space=14)
words(11, *[r for _, r in b11])
cite(s, "Shrout & Fleiss (1979), Psychol. Bull.; Winkler et al. (2014), NeuroImage")

# ============================================================================================
# 12 -- discussion 2: what this does not establish
# ============================================================================================
s = slide()
y = action_title(s, "A validity method must apply the same discipline to its own claims: "
                    "three named limits")
b12 = [("Represented faults only \u2014 ", n("faults") + "/" + n("faults") +
        " detection is represented-fault regression coverage"),
       ("Partial validation \u2014 ", n("red") + " of " + n("rules") +
        " rules have a demonstrated red fixture"),
       ("No performance claim \u2014 ", "no completeness, no RF or link result, no learned "
        "accuracy")]
bullets(s, MARGIN, y + 0.22, SW - 2 * MARGIN, 2.6, b12, space=18)
words(12, *[lead + rest for lead, rest in b12])
cite(s, "Just et al. (2014), FSE; Jia & Harman (2011), IEEE TSE")

# ============================================================================================
# 13 -- conclusions (last non-appendix slide; stays on screen during Q&A)
# ============================================================================================
s = slide(dark=True)
text(s, MARGIN, 0.28, SW - 2 * MARGIN, 0.42, "Conclusions", size=20, color=ONDARK)
box(s, MARGIN, 0.76, SW - 2 * MARGIN, 0.045, fill=ACCENT)
concl = [[("1.  Chronological separation is necessary, ", True), ("not sufficient.", False)],
         [("2.  Some validity is relational, ", True),
          ("and can be made executable, falsifiable, and allowed to refuse.", False)],
         [("3.  ", True),
          ("The unit gate fires on real orbital data; the contract runs unchanged on a "
           "third-party artifact.", False)]]
text(s, MARGIN, 1.02, SW - 2 * MARGIN, 3.5, concl, size=SZ_BODY, color=WHITE, space_after=22)
text(s, MARGIN, 4.82, SW - 2 * MARGIN, 0.4,
     "Anonymous Submission \u00b7 contact withheld for review",
     size=14, color=ONDARK)

# ============================================================================================
# 14 -- references
# ============================================================================================
s = slide()
text(s, MARGIN, 0.22, SW - 2 * MARGIN, 0.5, "References", size=24, color=PRIMARY, bold=True)
box(s, MARGIN, 0.76, SW - 2 * MARGIN, 0.025, fill=RULE)
REFS = [
    "Bergmeir, C. & Ben\u00edtez, J.M. (2012). On the use of cross-validation for time series "
    "predictor evaluation. Information Sciences, 191.",
    "CCSDS (2023). Orbit Data Messages, Recommended Standard CCSDS 502.0-B-3.",
    "Hundman, K. et al. (2018). Detecting spacecraft anomalies using LSTMs and nonparametric "
    "dynamic thresholding. Proc. ACM SIGKDD.",
    "Hurlbert, S.H. (1984). Pseudoreplication and the design of ecological field experiments. "
    "Ecological Monographs, 54(2).",
    "Jia, Y. & Harman, M. (2011). An analysis and survey of the development of mutation "
    "testing. IEEE Trans. Software Engineering, 37(5).",
    "Just, R. et al. (2014). Are mutants a valid substitute for real faults in software "
    "testing? Proc. ACM SIGSOFT FSE.",
    "Kapoor, S. & Narayanan, A. (2023). Leakage and the reproducibility crisis in "
    "machine-learning-based science. Patterns, 4(9).",
    "Kaufman, S. et al. (2012). Leakage in data mining: formulation, detection, and "
    "avoidance. ACM TKDD, 6(4).",
    "Shrout, P.E. & Fleiss, J.L. (1979). Intraclass correlations: uses in assessing rater "
    "reliability. Psychological Bulletin, 86(2).",
    "U.S. Space Force. Space-Track GP and GP_HISTORY API: general perturbations element sets.",
    "Vallado, D.A. et al. (2006). Revisiting Spacetrack Report #3. AIAA/AAS Astrodynamics "
    "Specialist Conference.",
    "Wilson, E.B. (1927). Probable inference, the law of succession, and statistical "
    "inference. J. American Statistical Association, 22(158).",
    "Winkler, A.M. et al. (2014). Permutation inference for the general linear model. "
    "NeuroImage, 92.",
]
half = (len(REFS) + 1) // 2
colw = (SW - 2 * MARGIN - 0.35) / 2
text(s, MARGIN, 0.88, colw, 4.4, REFS[:half], size=12, color=BODY, space_after=4)
text(s, MARGIN + colw + 0.35, 0.88, colw, 4.4, REFS[half:], size=12, color=BODY, space_after=4)

# ============================================================================================
# appendix
# ============================================================================================
def appendix(tag, title, size=SZ_TITLE - 2):
    s = slide()
    text(s, MARGIN, 0.16, SW - 2 * MARGIN, 0.34, tag, size=14, color=MUTED)
    text(s, MARGIN, 0.56, SW - 2 * MARGIN, 0.85, title, size=size, color=PRIMARY, bold=True)
    box(s, MARGIN, 1.48, SW - 2 * MARGIN, 0.025, fill=RULE)
    return s, 1.62


# A -- INDETERMINATE is not low power
s, y = appendix("Appendix A \u2014 abstention",
                "INDETERMINATE is a property of the design's resolution, not of the effect size")
rows = [("3 coarser groups of 2 units", "15", "0.067"),
        ("4 coarser groups of 2 units", "105", "0.0095")]
COLX, COLW = (0.15, 4.55, 6.35), (4.20, 1.60, 2.55)
for j, t in enumerate(("coarser grouping", "assignments", "smallest attainable p")):
    label1(s, MARGIN + COLX[j], y, COLW[j], 0.30, t, size=SZ_DIAG, color=MUTED, bold=True,
           align=PP_ALIGN.LEFT, pad=0.0)
for i, (design, na, pv) in enumerate(rows):
    yy = y + 0.38 + i * 0.62
    box(s, MARGIN, yy, 8.9, 0.54, fill=PANEL if i else RGBColor(0xF2, 0xF4, 0xF7),
        line=MUTED, lw=0.6)
    for j, t in enumerate((design, na, pv)):
        label1(s, MARGIN + COLX[j], yy, COLW[j], 0.54, t, size=SZ_LABEL,
               color=PRIMARY if j == 2 else BODY, bold=(j == 2), align=PP_ALIGN.LEFT, pad=0.0)
bullets(s, MARGIN, y + 1.78, SW - 2 * MARGIN, 1.6,
        [("", "at three groups of two the design cannot reject at the nominal level for any "
              "effect size \u2014 so the rule abstains rather than PASSing"),
         ("", "low power is about \u03c1; this is about what the grouping geometry can attain")],
        space=13)

# B -- the four obligations in full
s, y = appendix("Appendix B \u2014 scope",
                "Each of the four obligations has a counterexample that lies outside the "
                "realised dataset")
gaps = [("Availability", "it existed \u2014 but could anyone fetch it at the decision time?"),
        ("Row membership", "which rows exist at all, and who decided"),
        ("Hidden state", "information that is not a column"),
        ("Statistical unit", "are two rows really independent?")]
for i, (t, d) in enumerate(gaps):
    x0 = MARGIN + (i % 2) * 4.55
    yy = y + (i // 2) * 1.32
    box(s, x0, yy, 4.35, 1.14, fill=RGBColor(0xFF, 0xF8, 0xEE),
        line=RGBColor(0xC8, 0x7A, 0x1E), lw=0.8)
    text(s, x0 + 0.16, yy + 0.14, 4.05, 0.9, [[(t, True)], [(d, False)]],
         size=SZ_LABEL, color=BODY)
label(s, MARGIN, y + 2.78, 8.9, 0.3,
      "A chronological split adjudicates everything inside one table. None of the four is "
      "inside it.", size=SZ_DIAG, color=MUTED, align=PP_ALIGN.LEFT)

# C -- other observables and levels
s, y = appendix("Appendix C \u2014 what the rule can and cannot say",
                "The observable and the declared hierarchy determine the verdict \u2014 not the "
                "data alone")
tbl = [("in-track increment", "pass \u2192 element set", "\u03c1\u0302 = " + n("aticc"), "HALT"),
       ("in-track increment", "element set \u2192 object",
        "\u03c1\u0302 = " + n("aticcelset"), "HALT"),
       ("elevation", "pass \u2192 element set", "\u03c1\u0302 = " + n("realiccab"), "PASS")]
hdr = ("observable", "declared grouping", "estimate", "verdict")
CX, CW = (0.15, 2.65, 5.65, 7.35), (2.40, 2.90, 1.60, 1.40)
for j, t in enumerate(hdr):
    label1(s, MARGIN + CX[j], y, CW[j], 0.30, t, size=SZ_DIAG, color=MUTED, bold=True,
           align=PP_ALIGN.LEFT, pad=0.0)
for i, row in enumerate(tbl):
    yy = y + 0.36 + i * 0.62
    box(s, MARGIN, yy, 8.9, 0.54, fill=RGBColor(0xF2, 0xF4, 0xF7) if i % 2 == 0 else BG,
        line=RULE, lw=0.5)
    for j, t in enumerate(row):
        label1(s, MARGIN + CX[j], yy, CW[j], 0.54, t, size=SZ_LABEL,
               color=PRIMARY if j == 3 else BODY, bold=(j == 3), align=PP_ALIGN.LEFT, pad=0.0)
bullets(s, MARGIN, y + 2.30, SW - 2 * MARGIN, 1.4,
        [("", "no level tested here is exchangeable for the in-track increment, so the element "
              "set is not offered as a universal unit"),
         ("", "on elevation the same rule returned \u03c1\u0302 = " +
              n("realiccab"))], space=13)

# D -- reproduction and provenance
s, y = appendix("Appendix D \u2014 reproduction",
                "Every number is regenerated from one artifact; the borrowed data's "
                "provenance is stated")
bullets(s, MARGIN, y, SW - 2 * MARGIN, 3.4,
        [("Numbers \u2014 ", "read from evaluation/results/final_summary.json; " +
          n("claimsites") + " artifact-bound claim sites in the manuscript"),
         ("Detector \u2014 ", "contract layers sha256 07baad27\u2026 unchanged across the "
          "external study; the commit was chosen before inspection"),
         ("Telemetry \u2014 ", "the arrays came from a checksum-verified mirror after the "
          "upstream endpoint became unavailable; per-file hashes matched two independently "
          "published checksum sources"),
         ("", "that is mirror concordance \u2014 not verification by the original publisher")],
        space=14)

# E -- pre-built Q&A
s, y = appendix("Appendix E \u2014 anticipated questions",
                "Five questions this design invites, answered inside what the paper licenses")
qa = [("Why a communications paper?",
       "Two clocks, predicted-geometry rows, retrospective labels and repeated measures "
       "nesting inside an element set \u2014 generic tooling has none of these."),
      ("Is L4.6 merely metamorphic testing?",
       "The relation is metamorphic; the target is not. It is applied to declared provenance."),
      ("Is L4.7 merely ICC plus permutation?",
       "Both are established. What is new is calibrating a gate with an abstention state."),
      ("Why not always choose object as the unit?",
       "The rule adjudicates the level it is given; element-set \u2192 object halts too."),
      ("How is PASS useful if it proves nothing?",
       "It is a regression guard: a represented violation cannot silently return.")]
paras = []
for q, a in qa:
    paras.append([("\u2022  ", False), (q + "  ", True), (a, False)])
text(s, MARGIN, y, SW - 2 * MARGIN, 3.5, paras, size=SZ_LABEL, color=BODY, space_after=11)

# --------------------------------------------------------------------------------------------
prs.save(OUT)
over = {k: v for k, v in WORDS.items() if v > 40}
print(f"wrote {OUT.relative_to(ROOT)}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
print("body words per content slide: " +
      "  ".join(f"s{k}={v}" for k, v in sorted(WORDS.items())))
if over:
    print(f"NOTE: over the skill's ~40-word body cap: {over}", file=sys.stderr)
