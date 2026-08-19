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

    # Checking that every macro USED is defined does not stop someone hard-coding a number over
    # a macro: the macro simply disappears and nothing complains. These must stay on the slides.
    REQUIRED = {
        "Nrate", "Nwlo", "Nwhi", "Nalpha", "Ncleanpaths", "Ncleanhalts", "Nseeds",
        "Npowerlo", "Nobjects", "Nelsets", "Npasses", "Naticc", "Natp", "Natlo",
        "Naticcobj", "Naticcelset", "Natused", "Natgroups", "Natdropped",
        "Natelsetunits", "Natelsetgroups", "NpermB",
        "Nextpass", "Nexthalt", "Nextindet", "Nextna", "Nextnobs", "Nextrules",
        "Nconsseeds", "Nconschanged", "Nconsminp", "Nrules", "Nclaimsites",
        "Nconsoverlap", "Nconsoverlapcorr", "Nrealiccab",
    }
    # Deliberately NOT required, each for a recorded reason -- so a future reader does not
    # reinstate them as literals thinking the guard simply missed them:
    #   Nfaults, Nred  -- the curated fault matrix is never introduced on a main slide, so its
    #                     17/17 and 16/19 were a limitation on a claim the audience never heard.
    #   Npowerhi       -- "power -> 1.0" is now stated as the count it is, 40/40 via Nseeds.
    dropped = sorted(REQUIRED - used)
    if dropped:
        print(f"talk/check: FAIL -- artifact macro(s) no longer used on any slide: {dropped}\n"
              "   a literal was probably hard-coded over one of them")
        return 1

    # And the converse: the denominators most likely to be mistyped must never appear as bare
    # literals in the deck body. They come from the artifact or not at all.
    body = re.sub(r"(?m)^\s*%.*$", "", (HERE / "orbit_evidence_talk.tex").read_text())
    body = re.sub(r"\\newcommand\{[^}]*\}(\[\d\])?\{[^}]*\}", "", body)
    art = json.loads(SUMMARY.read_text())
    guarded = {str(art["real_l47_alongtrack"]["n_passes_used"]),
               str(art["real_l47_alongtrack"]["n_elsets"]),
               str(art["real_l47_application"]["n_passes"]),
               str(art["real_l47_application"]["n_element_sets"]),
               str(art["rule_count"])}
    bare = sorted(n for n in guarded if re.search(rf"(?<![\w.\\{{]){n}(?![\w.}}])", body))
    if bare:
        print(f"talk/check: FAIL -- bare literal(s) {bare} in the deck; use the bound macro")
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

    # ---- semantic lint over BOTH claim surfaces -------------------------------------------
    # Each pattern is a defect this campaign made or nearly made. Wording, not style.
    #
    # The outline's "Never say" block quotes the prohibited claims verbatim, which is the point
    # of having it. Excise that declared block before linting -- and require it to exist, so the
    # exemption cannot be obtained by simply deleting the list.
    if "## Never say" not in out:
        print("talk/check: FAIL -- SPEAKER_OUTLINE.md has no '## Never say' block")
        return 1
    lint_out = re.sub(r"## Never say.*?(?=\n## )", "", out, flags=re.S)

    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_ledger", HERE / "gen_ledger.py")
    gl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gl)
    # A prohibited phrase is legitimate when the surrounding clause NEGATES or PROHIBITS it --
    # the outline's do-not-say list and the deck's "no claim that ..." sentences are the whole
    # point. Same distinction the manuscript's banlist draws between a claim and a withdrawal.
    # BEFORE: any negating or prohibiting clause. "without" is deliberately absent -- "falsifies
    # incompleteness without enumerating..." must still fail, and an earlier version exempted it.
    NEG = re.compile(r"\b(never|no claim|not\b|prohibit\w*|do not|must not|rather than|"
                     r"is not|are not|nor\b|refut\w*|textbf\{not\})", re.I)
    # AFTER: only an IMMEDIATE strong negator, for the Q&A shape "...truth error? | No. It is..."
    NEG_AFTER = re.compile(r"^[\s?|.,:;—-]{0,6}(no|not|never)\b", re.I)
    surfaces = {"deck": src, "outline": lint_out}
    hits, permitted = [], 0
    for name, text in surfaces.items():
        flat = " ".join(text.split())
        for rule in gl.SEMANTIC_LINT:
            pat, why = rule[0], rule[1]
            for m in re.finditer(pat, flat, re.I):
                # Look both ways: a Q&A row negates AFTER the phrase ("...measure orbit truth
                # error? | No. It is an update increment..."), a slide negates before it.
                before = flat[max(0, m.start() - 90):m.start()]
                after = flat[m.end():m.end() + 60]
                if NEG.search(before) or NEG_AFTER.search(after):
                    permitted += 1
                    continue
                ctx = flat[max(0, m.start() - 60):m.end() + 30]
                hits.append(f"{name}: {m.group(0)!r} -- {why}\n        ...{ctx}...")
    if hits:
        print("talk/check: FAIL -- semantic lint")
        for h in hits:
            print("   " + h)
        return 1

    # ---- required qualifiers: dropping one is how a talk quietly widens a claim ------------
    required = {
        "not truth error": "the along-track quantity must be scoped",
        "not estimable": "the downstream endpoint's disposition",
        "rule verdict": "verdicts must be distinguished from dispositions",
        "represented-fault": "curated coverage must be scoped",
    }
    # strip LaTeX markup before looking for a phrase: "\\textbf{not} truth error" renders as
    # the qualifier but does not contain it as a literal substring.
    plain = re.sub(r"\\\\[a-zA-Z]+\\*?(\\{[^{}]*\\})?", " ", src + " " + out)
    plain = " ".join(plain.replace("{", " ").replace("}", " ").lower().split())
    gone = sorted(k for k in required if k not in plain)
    if gone:
        print(f"talk/check: FAIL -- required qualifier(s) missing: {gone}")
        return 1

    # ---- projected legibility ---------------------------------------------------------------
    # A slide is read from the back of a room, not at arm's length, so the paper's 6.4 pt print
    # floor is far too low here. \tiny at an 11 pt base renders 6 pt: the deck carried 38 such
    # spans, including the verdict gloss and the pipeline markers, before this check existed.
    # Floor is 8 pt (\scriptsize); math sub/superscripts are exempt by exact size, as in the
    # manuscript's own glyph gate.
    SLIDE_FLOOR, MATH_CLASS = 8.0, {7.0}
    pdf = HERE / "orbit_evidence_talk.pdf"
    if pdf.exists():
        sys.path.insert(0, str(HERE.parent / "paper" / "scripts"))
        import check_glyphs as G
        tiny = [(p, round(sz, 1), t) for p, sz, t in G.spans(str(pdf))
                if sz < SLIDE_FLOOR - 0.05 and round(sz, 1) not in MATH_CLASS]
        if tiny:
            print(f"talk/check: FAIL -- {len(tiny)} span(s) below the {SLIDE_FLOOR} pt slide "
                  "floor; \\tiny is never legible projected")
            for p, sz, t in tiny[:6]:
                print(f"    {sz} pt  p{p}  {t[:40]!r}")
            return 1

    # ---- content presence: beamer DROPS an overflowing line with no overfull-box warning ------
    # Twice in one session a footnote on the real-data slide was silently truncated mid-sentence:
    # the source was correct, the gate was green, and the sentence simply never reached the PDF.
    # Geometry checks cannot see this and the glyph check cannot either -- absent text has no size.
    # The advisor deck has carried this check for a while; the talk did not, which is why it took a
    # human reading the rendered page to notice. Both pdftotext modes are read and their
    # vocabularies unioned, because -layout leaves hyphenated words split across column text.
    if pdf.exists():
        import subprocess as _sp
        lay = _sp.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
        flow = _sp.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
        _n = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower())
        seen = set(_n(lay).split()) | set(_n(flow).split())
        dropped = []
        deck_src = (HERE / "orbit_evidence_talk.tex").read_text()
        for fm in re.finditer(r"\\begin\{frame\}(?:\[[^\]]*\])?(?:\{.*?\})?(.*?)\\end\{frame\}",
                              deck_src, re.S):
            inner = fm.group(1)
            inner = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", inner, flags=re.S)
            inner = re.sub(r"\$[^$]*\$", " ", inner)
            inner = re.sub(r"\\(?:begin|end)\{[^}]*\}\s*(\{[lrcp@|!<>.\d\s{}]*\})?", " ", inner)
            inner = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", inner)
            words = [w for w in _n(inner).split() if len(w) >= 5]
            if len(words) < 6:
                continue
            absent = [w for w in words[-4:] if w not in seen]
            if absent:
                dropped.append(f"{' '.join(words[-4:])}  (absent: {', '.join(absent)})")
        if dropped:
            print(f"talk/check: FAIL -- {len(dropped)} frame(s) whose closing words never reached "
                  "the PDF; content was dropped, not merely tight:")
            for d in dropped[:6]:
                print("   ..." + d)
            return 1

    # ---- main-frame count is derived, never hard-coded -------------------------------------
    # Anchor to line start: a preamble COMMENT mentioning \appendix split the file at the
    # comment and reported zero main frames.
    deck = (HERE / "orbit_evidence_talk.tex").read_text()
    main_src = re.split(r"^\\appendix\s*$", deck, flags=re.M)[0]
    n_main = len(re.findall(r"^\\begin\{frame\}", main_src, flags=re.M))
    if n_main != 13:
        print(f"talk/check: FAIL -- {n_main} main frames, deck is specified at 13")
        return 1

    print(f"talk/check: PASS -- {len(used)} artifact-bound values in the deck, "
          f"{len(must)} verified in the outline, {n_main} main frames, "
          f"{len(gl.SEMANTIC_LINT)} lint rules clean ({permitted} negated mention(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
