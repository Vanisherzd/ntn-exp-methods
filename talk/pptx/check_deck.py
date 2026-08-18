#!/usr/bin/env python3
"""QA the built .pptx by reading it back, not by trusting the builder.

Six gates, all mechanical:

  1. numbers.tex is current -- regenerating it must change nothing, so no slide can carry a
     figure the artifact no longer supports.
  2. Semantic lint -- the 14 SEMANTIC_LINT rules from talk/gen_ledger.py, with the same
     negation-awareness talk/check_numbers.py uses (a prohibited phrase is legitimate inside a
     clause that negates or prohibits it).
  3. Required qualifiers -- dropping one is how a talk quietly widens a claim.
  4. Typography floors from the academic-pptx skill: body prose >= 20 pt, chart and diagram
     labels >= 16 pt. Citations are exempt at 12-14 pt, identified by POSITION (bottom of the
     slide) rather than by size, so a small run cannot pass by claiming to be a citation.
  5. Body-prose budget -- ~40 words per content slide, counted from runs in the body size band.
  6. Deck architecture -- an action title on every content slide, a References slide, and
     Conclusions as the last non-appendix slide.

Exit 0 only if every gate passes.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

HERE = Path(__file__).resolve().parent
TALK = HERE.parent
ROOT = TALK.parent
DECK = HERE / "orbit_evidence_talk.pptx"

BODY_LO, BODY_HI = 19.0, 22.0   # body prose band (20 pt, and 19 pt right-column variants)
LABEL_FLOOR = 16.0              # skill: chart labels / annotations 16-18 pt
TITLE_FLOOR = 24.0              # skill: action title 24-28 pt
CITE_BAND = (11.5, 14.5)        # skill: source citations 12-14 pt
# slide_patterns.md places the conclusions slide's contact line at y = 4.8, so the foot of the
# slide starts there; anything smaller than 16 pt higher up is a mis-sized diagram label.
CITE_ZONE_TOP = 4.80
WORD_CAP = 40


def fail(msg: str) -> None:
    print("pptx/check: FAIL -- " + msg)


def main() -> int:
    if not DECK.exists():
        fail(f"{DECK.name} not built -- run build_deck.py")
        return 1
    problems = 0

    # ---- 1. numbers.tex currency -----------------------------------------------------------
    before = (TALK / "numbers.tex").read_text()
    # check=False here was a real hole: a generator that CRASHES leaves numbers.tex untouched,
    # so the equality test below passed vacuously and reported the numbers as current. The
    # generator's exit status is part of the evidence, not incidental.
    gen = subprocess.run([sys.executable, str(TALK / "gen_numbers.py")], cwd=ROOT,
                         capture_output=True, text=True, check=False)
    if gen.returncode != 0:
        fail(f"gen_numbers.py exited {gen.returncode} -- numbers cannot be verified:\n"
             f"   {(gen.stderr or gen.stdout).strip()[:400]}")
        return 1
    if (TALK / "numbers.tex").read_text() != before:
        fail("numbers.tex was stale; regenerated -- rebuild the deck and re-check")
        return 1

    # ---- read the deck back ----------------------------------------------------------------
    prs = Presentation(str(DECK))
    slides = list(prs.slides)
    runs = []           # (slide_no, size_pt, top_in, text)
    for i, s in enumerate(slides, start=1):
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            top = Emu(sh.top).inches if sh.top is not None else 0.0
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if not r.text.strip():
                        continue
                    sz = r.font.size.pt if r.font.size is not None else None
                    runs.append((i, sz, top, r.text))

    missing = [(i, t) for i, sz, _, t in runs if sz is None]
    if missing:
        fail(f"{len(missing)} run(s) carry no explicit font size -- e.g. slide {missing[0][0]}: "
             f"{missing[0][1][:50]!r}")
        problems += 1

    flat_all = " ".join(" ".join(t.split()) for _, _, _, t in runs)

    # ---- 2. semantic lint ------------------------------------------------------------------
    spec = importlib.util.spec_from_file_location("gen_ledger", TALK / "gen_ledger.py")
    gl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gl)
    NEG = re.compile(r"\b(never|no claim|not\b|prohibit\w*|do not|must not|rather than|"
                     r"is not|are not|nor\b|refut\w*)", re.I)
    NEG_AFTER = re.compile(r"^[\s?|.,:;—-]{0,6}(no|not|never)\b", re.I)
    hits, permitted = [], 0
    for pat, why in [(r[0], r[1]) for r in gl.SEMANTIC_LINT]:
        for m in re.finditer(pat, flat_all, re.I):
            before_ = flat_all[max(0, m.start() - 90):m.start()]
            after_ = flat_all[m.end():m.end() + 60]
            if NEG.search(before_) or NEG_AFTER.search(after_):
                permitted += 1
                continue
            ctx = flat_all[max(0, m.start() - 60):m.end() + 30]
            hits.append(f"{m.group(0)!r} -- {why}\n        ...{ctx}...")
    if hits:
        fail("semantic lint")
        for h in hits:
            print("   " + h)
        problems += 1

    # ---- 3. required qualifiers -------------------------------------------------------------
    required = {
        "not truth error": "the along-track quantity must be scoped",
        "not estimable": "the downstream endpoint's disposition",
        "rule verdict": "verdicts must be distinguished from dispositions",
        "represented-fault": "curated coverage must be scoped",
    }
    low = flat_all.lower()
    gone = sorted(k for k in required if k not in low)
    if gone:
        fail(f"required qualifier(s) missing: {gone}")
        problems += 1

    # ---- 4. typography floors --------------------------------------------------------------
    tiny = []
    for i, sz, top, t in runs:
        if sz is None or sz >= LABEL_FLOOR:
            continue
        is_cite = CITE_BAND[0] <= sz <= CITE_BAND[1] and top >= CITE_ZONE_TOP
        is_refs = i == REFS_SLIDE
        # slide_patterns.md section 1 sets the title slide's author block at 15 pt and its
        # subtitle at 16 pt, so the skill sanctions sub-16 pt text there.
        is_title_slide = i == 1
        # Section 11 sets the appendix tag ("Appendix B — Robustness Checks") at 14 pt; it is a
        # navigation label read at the lectern during Q&A, not projected content.
        is_appendix_tag = i > REFS_SLIDE and t.strip().startswith("Appendix ") and top < 0.5
        if not (is_cite or is_refs or is_title_slide or is_appendix_tag):
            tiny.append((i, sz, round(top, 2), t[:44]))
    if tiny:
        fail(f"{len(tiny)} run(s) below the {LABEL_FLOOR:.0f} pt chart/diagram-label floor "
             f"and not in the citation zone (top >= {CITE_ZONE_TOP}\")")
        for i, sz, top, t in tiny[:14]:
            print(f"   slide {i:2d}  {sz:4.1f} pt  top={top}\"  {t!r}")
        if len(tiny) > 14:
            print(f"   ... and {len(tiny) - 14} more")
        problems += 1

    # ---- 5. body-prose budget --------------------------------------------------------------
    # The skill's typography table lists "Section header 20-22 pt" separately from "Body bullets
    # 20 pt", so a 22 pt header is structure, not prose; and a bullet glyph is a marker.
    per = {}
    for i, sz, _, t in runs:
        if sz is None or not (BODY_LO <= sz < BODY_HI):
            continue
        if t.strip() in {"•", "•  ", "-", "—"}:
            continue
        per[i] = per.get(i, 0) + len(t.split())
    # content_guidelines.md section 4 names the appendix as the destination for material over
    # the cap ("the material belongs in an appendix or handout"), so the cap governs the main
    # path only. Appendix density is reported below, not gated.
    over = {i: w for i, w in per.items() if w > WORD_CAP and i <= CONCLUSIONS_SLIDE}
    if over:
        fail(f"body prose over the ~{WORD_CAP}-word cap: " +
             ", ".join(f"slide {i}={w}" for i, w in sorted(over.items())))
        problems += 1

    # ---- 6. deck architecture --------------------------------------------------------------
    titled = {i for i, sz, _, _ in runs if sz is not None and sz >= TITLE_FLOOR}
    # slide_patterns.md section 7 gives Conclusions its own pattern -- a 20 pt "Conclusions"
    # label, no action title -- so the action-title rule covers slides 2..12 only.
    content = set(range(2, CONCLUSIONS_SLIDE))
    untitled = sorted(content - titled)
    if untitled:
        fail(f"content slide(s) with no run at >= {TITLE_FLOOR:.0f} pt (no action title): "
             f"{untitled}")
        problems += 1
    refs_text = " ".join(t for i, _, _, t in runs if i == REFS_SLIDE)
    if "References" not in refs_text:
        fail(f"slide {REFS_SLIDE} is not the References slide")
        problems += 1
    concl_text = " ".join(t for i, _, _, t in runs if i == CONCLUSIONS_SLIDE)
    if "Conclusions" not in concl_text:
        fail(f"slide {CONCLUSIONS_SLIDE} is not the Conclusions slide")
        problems += 1
    app = [i for i in range(REFS_SLIDE + 1, len(slides) + 1)
           if "Appendix" not in " ".join(t for j, _, _, t in runs if j == i)]
    if app:
        fail(f"appendix slide(s) not labelled 'Appendix ...': {app}")
        problems += 1

    if problems:
        return 1
    main_max = max((w for i, w in per.items() if i <= CONCLUSIONS_SLIDE), default=0)
    app_max = max((w for i, w in per.items() if i > REFS_SLIDE), default=0)
    print(f"pptx/check: OK -- {len(slides)} slides; "
          f"{len(gl.SEMANTIC_LINT)} lint rules clean ({permitted} negated mention(s)); "
          f"all {len(required)} qualifiers present; "
          f"main-path body prose max {main_max}/{WORD_CAP} words "
          f"(appendix {app_max}, ungated by design); "
          f"no run below {LABEL_FLOOR:.0f} pt outside the citation zone")
    return 0


# Slide roles are fixed by the approved outline; naming them here keeps the architecture gate
# honest -- if the builder reorders slides, the gate fails instead of silently re-labelling.
CONCLUSIONS_SLIDE = 13
REFS_SLIDE = 14

if __name__ == "__main__":
    raise SystemExit(main())
