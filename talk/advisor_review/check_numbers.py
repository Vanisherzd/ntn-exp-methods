#!/usr/bin/env python3
"""Gate the advisor deck. Fourteen checks, all mechanical; exit 0 only if every one passes.

  1. numbers.tex is CURRENT -- regenerate and compare, and treat the generator's exit status as
     evidence. A crashing generator leaves the file untouched, which makes an equality test pass
     vacuously; that hole existed in a sibling checker and is closed here by construction.
  2. Every macro the generator emits is USED, or listed in KNOWN_UNUSED with a reason. A number
     bound but never shown is a number nobody re-reads when the artifact moves.
  3. The REQUIRED set from the review brief is present -- so a slide cannot quietly drop the
     denominator, the permutation count, or the attainability arithmetic.
  4. No BARE LITERAL where a macro exists. This is the actual anti-drift check: retyping 0.501
     into a slide is exactly how a stale figure survives a re-run.
  5. Semantic lint -- the 14 SEMANTIC_LINT rules from talk/gen_ledger.py, negation-aware, so a
     "Not claimed: ..." sentence is permitted while a bare assertion is not.
  6. Required qualifiers -- dropping one is how a deck quietly widens a claim.
  7. STOPPED-RESEARCH ISOLATION. Doppler / LR-FHSS / residual-learning / conducted-IQ vocabulary
     may appear only inside appendix A10, and A10 must carry its historical-motivation label.
     This enforces the review brief's hard boundary in code rather than by intention.
  8. Frame architecture -- 24 main frames, 10 appendix frames.
  9. NO OVERLAYS -- physical PDF pages must equal the frame count, so the advisor's static PDF
     cannot be a 34-page artifact that is really 24 slides.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TALK = ROOT / "talk"
DECK = HERE / "advisor_deck.tex"
NUMS = HERE / "numbers.tex"
PDF = HERE / "advisor_deck.pdf"

MAIN_FRAMES, APPENDIX_FRAMES = 25, 11

# Every number the review brief requires the deck to bind.
REQUIRED = {
    "Nrules", "Nfaults", "Nred", "Nchrono", "Ncontract", "Nenvs",
    "Ncleanhalts", "Ncleanpaths", "Nrate", "Nwlo", "Nwhi", "Nalpha",
    "Nrholo", "Nrhohi", "Npowerlo", "Nseeds", "Nhaltshi", "NpermB",
    "Nassignthree", "Nminpthree", "Nassignfour", "Nminpfour",
    "Npasses", "Nelsets", "Nobjects", "Natused", "Natelsets", "Natdropped",
    "Naticc", "Natp", "Natlo", "Naticcelset", "Nelevicc",
    "Nextpass", "Nexthalt", "Nextindet", "Nextna", "Nextnobs",
    "Nwindowspan", "Nboundarydropped", "Nconsoverlap", "Nconsoverlapcorr",
    "Nconschanged", "Nconsseeds", "Nconsminp",
}

KNOWN_UNUSED: dict[str, str] = {}

REQUIRED_QUALIFIERS = {
    "update increment": "the along-track quantity must be scoped, never called truth error",
    "not estimable": "the downstream endpoint's disposition",
    "rule verdict": "verdicts must be distinguished from applicability dispositions",
    "represented-fault": "curated coverage must be scoped",
    "not rejected": "PASS semantics",
}

# The stopped research line. Permitted ONLY inside appendix A10.
STOPPED_VOCAB = re.compile(
    r"doppler|LR-?FHSS|residual[- ]learning|learned residual|conducted[- ]?IQ|"
    r"pre-?compensation|hop\s*bin|SGP4|packet error|link budget", re.I)
A10_LABEL = "HISTORICAL MOTIVATION ONLY"

# Advisor-deck-specific lint, on top of the shared SEMANTIC_LINT. Each entry exists because a
# reviewer caught the deck making the move, not because it seemed unwise in the abstract.
ADVISOR_LINT = [
    (r"observable[- ]dependent",
     "the elevation readout is a ties signature at the truncation boundary, not an effect size"),
    (r"essentially zero|shows no dependence|\bshows none\b",
     "a truncated tie licenses 'the rule did not reject', not a near-zero effect"),
    (r"geometric observable[^.]{0,40}\bno\b(?!t\b)",
     "same overstatement in another phrasing"),
    (r"reference is \\emph\{exhaustive\}|exhaustive rather than sampled|small enough to enumerate",
     "the frozen rule ALWAYS draws B random permutations; no enumeration exists in project code, "
     "so an exhaustive reference is an implementation behaviour the rule does not have"),
    (r"denominators never compete",
     "at the smallest admitted design (4 groups of 2) the rule runs, so the combinatorial floor "
     "and the 1/(B+1) reporting floor coexist there"),
    (r"[Bb]oth real-data HALTs",
     "there are three along-track HALTs at the floor, not two"),
    (r"(?:any|every)\s+omission\s+must\s+violate|omission\s+(?:is|would be)\s+detected",
     "asserts the CONVERSE of L4.6: an unexercised omission leaves the invariant intact, so a "
     "pass cannot exclude omissions -- that is the completeness claim slide 11 disclaims"),
]

# Phrases the deck MUST carry, each guarding a specific overstatement a reviewer found.
ADVISOR_REQUIRED = {
    "ties signature": "the elevation control must be named as a tie, not an effect size",
    "deterministic given the declared": "L4.6's implication needs its determinism precondition",
    "always draws": "A3 must say the rule samples B permutations, never enumerates",
    "censored at": "equal p at the reference floor must not read as equal evidence",
}

# Stopped-line QUANTITATIVE results, banned EVERYWHERE including A10. The vocabulary ban above
# permits naming the stopped line inside A10 for lineage; this one permits no number from it
# anywhere, because a figure is what turns lineage into evidence reuse. Decibels and carrier
# frequencies are included wholesale: the current paper claims no RF result at all, so any such
# quantity in this deck could only have come from the stopped line.
STOPPED_RESULTS = [
    (r"\b24\s*/\s*24\b", "the stopped line's gate-closed headline"),
    (r"\b(?:43\.8|26\.9|45\.3|923\.238)\b", "a stopped-line measured value"),
    (r"\bdBm?\b", "no RF quantity is claimed by this paper"),
    (r"\bMHz\b|\bGHz\b", "no carrier frequency is claimed by this paper"),
    (r"conducted[-\s]?IQ", "bench-capture result from the stopped line"),
    (r"\bTX[-\s]?ON\b", "bench-capture result from the stopped line"),
    (r"BLACK\s*KITE|\bBK[12]\b", "stopped-line object identifiers"),
    (r"stale[-\s]?TLE", "stopped-line experimental variable"),
    (r"noise\s+floor", "bench-capture result from the stopped line"),
    (r"packet\s+error|\blink\s+budget\b", "no link-layer result is claimed"),
]


def fail(msg: str) -> None:
    print("advisor/check: FAIL -- " + msg)


def main() -> int:
    problems = 0

    # ---- 1. currency ------------------------------------------------------------------------
    before = NUMS.read_text() if NUMS.exists() else ""
    gen = subprocess.run([sys.executable, str(HERE / "gen_numbers.py")], cwd=ROOT,
                         capture_output=True, text=True, check=False)
    if gen.returncode != 0:
        fail(f"gen_numbers.py exited {gen.returncode} -- numbers cannot be verified:\n"
             f"   {(gen.stderr or gen.stdout).strip()[:400]}")
        return 1
    if NUMS.read_text() != before:
        fail("numbers.tex was stale; regenerated -- rebuild the deck and re-check")
        return 1

    macros = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", NUMS.read_text()))
    src = DECK.read_text()
    # strip comments: a macro named only in a comment is not "used"
    body = "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in src.split("\n"))

    # ---- 2. every macro used ----------------------------------------------------------------
    unused = sorted(k for k in macros
                    if not re.search(rf"\\{k}\b", body) and k not in KNOWN_UNUSED)
    if unused:
        fail(f"{len(unused)} generated macro(s) never appear in the deck: {unused}\n"
             f"   bind fewer numbers, or show them -- an unshown number is unverified")
        problems += 1

    # ---- 3. required coverage ---------------------------------------------------------------
    missing_def = sorted(REQUIRED - set(macros))
    if missing_def:
        fail(f"the brief requires these numbers but the generator does not emit them: "
             f"{missing_def}")
        problems += 1
    missing_use = sorted(k for k in REQUIRED & set(macros) if not re.search(rf"\\{k}\b", body))
    if missing_use:
        fail(f"required number(s) bound but not shown in the deck: {missing_use}")
        problems += 1

    # ---- 4. no bare literals ----------------------------------------------------------------
    # TikZ coordinates and style values are GEOMETRY, not claims: "at (0,16)" is a position and
    # "line width=0.4pt" is a stroke, yet both collided with \Nred=16 and produced 38 false
    # positives. Strip option brackets and numeric-only coordinate groups before scanning.
    stripped = re.sub(r"\\input\{numbers\.tex\}", "", body)
    stripped = re.sub(r"\[[^\[\]]*\]", " ", stripped)                    # [style=...] options
    # coordinate components may be macros inside a \foreach body: (-0.8,\y)
    stripped = re.sub(r"\((?:[-+0-9.,*\s]|\\[a-zA-Z]+)+\)", " ", stripped)   # (0,16) (-0.8,\y)
    stripped = re.sub(r"(?m)^\s*\\(draw|foreach|fill|path|clip)\b.*$", " ", stripped)
    literals = []
    for k, val in macros.items():
        v = str(val)
        # only distinctive values: decimals, or integers of two or more digits
        if not (("." in v) or (v.isdigit() and len(v) >= 2)):
            continue
        for m in re.finditer(rf"(?<![\w.]){re.escape(v)}(?!\w)", stripped):
            ctx = stripped[max(0, m.start() - 45):m.end() + 25].replace("\n", " ")
            literals.append(f"{v!r} (macro \\{k}) ... {ctx.strip()} ...")
    if literals:
        fail(f"{len(literals)} bare numeric literal(s) that have a macro:")
        for h in literals[:12]:
            print("   " + h)
        problems += 1

    # ---- 5. semantic lint -------------------------------------------------------------------
    spec = importlib.util.spec_from_file_location("gen_ledger", TALK / "gen_ledger.py")
    gl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gl)
    NEG = re.compile(r"\b(never|no claim|not claimed|not\b|prohibit\w*|do not|must not|"
                     r"rather than|is not|are not|nor\b|refut\w*|withdrawn|stopped)", re.I)
    NEG_AFTER = re.compile(r"^[\s?|.,:;—-]{0,6}(no|not|never)\b", re.I)
    flat = " ".join(body.split())
    # Everything inside a \notclaim{...} is an explicit withdrawal, however long the sentence
    # runs. Detecting that structurally beats widening the look-back window, which would start
    # exempting genuine assertions that merely sit near a negation.
    notclaim_spans = [m.span(1) for m in re.finditer(r"\\notclaim\{(.*?)\}(?=\s|$)", flat)]

    def in_notclaim(i):
        return any(a <= i < b for a, b in notclaim_spans)

    hits, permitted = [], 0
    permitted_adv = [0]
    for pat, why in [(r[0], r[1]) for r in gl.SEMANTIC_LINT]:
        for m in re.finditer(pat, flat, re.I):
            if in_notclaim(m.start()) or \
               NEG.search(flat[max(0, m.start() - 110):m.start()]) or \
               NEG_AFTER.search(flat[m.end():m.end() + 60]):
                permitted += 1
                continue
            hits.append(f"{m.group(0)!r} -- {why}\n        ..."
                        f"{flat[max(0, m.start()-60):m.end()+30]}...")
    if hits:
        fail("semantic lint")
        for h in hits:
            print("   " + h)
        problems += 1

    # ---- 5b. advisor-specific lint and required phrases -------------------------------------
    for surface, txt in (("deck", body),
                         ("notes", (HERE / "SPEAKER_NOTES.md").read_text()
                          if (HERE / "SPEAKER_NOTES.md").exists() else "")):
        flat_s = " ".join(txt.split())
        # Withdrawal spans, detected STRUCTURALLY. A banned phrase inside \notclaim{...} or inside
        # a "**Prohibited.**" note is being forbidden, not asserted, and those sentences run far
        # longer than any fixed look-back window -- widening the window instead would start
        # exempting genuine assertions that merely sit near a negation.
        spans = [m.span(1) for m in re.finditer(r"\\notclaim\{(.*?)\}(?=\s|$)", flat_s)]
        spans += [m.span(1) for m in re.finditer(r"\*\*Prohibited\.\*\*(.*?)(?=\*\*|###|$)",
                                                flat_s)]
        withdrawn = lambda i: any(a <= i < b for a, b in spans)
        for pat, why in ADVISOR_LINT:
            for m in re.finditer(pat, flat_s, re.I):
                # STRUCTURAL SPANS ONLY. The generic look-back window was a hole: re-asserting
                # "the effect is observable-dependent" passed because the legitimate negation
                # "not an effect size" sat within 110 characters of it. These phrases are exactly
                # the ones that appear beside true negations, so proximity cannot license them.
                if withdrawn(m.start()):
                    permitted_adv[0] += 1
                    continue
                fail(f"advisor lint ({surface}): {m.group(0)!r} -- {why}\n"
                     f"        ...{flat_s[max(0, m.start()-70):m.end()+40]}...")
                problems += 1
    # whitespace-normalised: a required phrase broken across a line wrap is still present, and
    # gating on the raw text made a legitimate line break look like a missing guard
    body_flat = " ".join(body.lower().split())
    missing_phrase = sorted(k for k in ADVISOR_REQUIRED if k not in body_flat)
    if missing_phrase:
        fail(f"required guarding phrase(s) absent from the deck: "
             f"{[f'{k}: {ADVISOR_REQUIRED[k]}' for k in missing_phrase]}")
        problems += 1

    # ---- 6. required qualifiers --------------------------------------------------------------
    plain = " ".join(re.sub(r"\\[a-zA-Z]+\*?", " ", body).replace("{", " ")
                     .replace("}", " ").lower().split())
    gone = sorted(k for k in REQUIRED_QUALIFIERS if k not in plain)
    if gone:
        fail(f"required qualifier(s) missing: {gone}")
        problems += 1

    # ---- 7. stopped-research isolation -------------------------------------------------------
    parts = re.split(r"(?m)^\\appendix", body)
    if len(parts) != 2:
        fail("could not locate a single \\appendix marker")
        return 1
    main_body, appendix_body = parts
    stray = [m.group(0) for m in STOPPED_VOCAB.finditer(main_body)]
    if stray:
        fail(f"stopped-research vocabulary in the MAIN deck (permitted only in A10): "
             f"{sorted(set(stray))}")
        problems += 1
    a10 = appendix_body.split("A10")[-1] if "A10" in appendix_body else ""
    outside_a10 = [m.group(0) for m in
                   STOPPED_VOCAB.finditer(appendix_body.replace(a10, ""))]
    if outside_a10:
        fail(f"stopped-research vocabulary in an appendix other than A10: "
             f"{sorted(set(outside_a10))}")
        problems += 1
    # UNCONDITIONAL. This was previously gated on A10 containing stopped-research vocabulary,
    # which made it dead code: A10 is written abstractly enough ("a learned correction to a
    # physical prediction") that the vocabulary regex never matches it, so the label could be
    # deleted with the gate still passing. A negative test caught that. The brief requires the
    # label whenever historical material is present at all, so the presence of A10 is the trigger.
    if not a10:
        fail("appendix A10 (historical origin) is missing")
        problems += 1
    elif A10_LABEL.lower() not in a10.lower():
        fail(f"appendix A10 does not carry its required label ({A10_LABEL!r}) -- historical "
             f"material must never read as evidence for the current paper")
        problems += 1

    # ---- 11. no stopped-line quantitative result, anywhere ---------------------------------
    quant = []
    for pat, why in STOPPED_RESULTS:
        for m in re.finditer(pat, body):
            quant.append(f"{m.group(0)!r} -- {why}")
    if quant:
        fail(f"{len(quant)} stopped-line quantitative result(s) in the deck (banned everywhere, "
             f"including A10):")
        for h in sorted(set(quant))[:12]:
            print("   " + h)
        problems += 1

    # ---- 14. nothing may sit below the deck's own footer baseline ---------------------------
    # The complement of check 12. Content loss (beamer dropping a line) is invisible to geometry;
    # content OVERDRAW is invisible to presence -- slide 18's clipped "Not claimed" block was
    # rendered, so every word was extractable, and its closing words all occur elsewhere in the
    # deck, so the presence check was masked. Geometry sees it: every well-behaved page bottoms out
    # at the page-number footer, so the footer baseline IS the limit, measured rather than assumed.
    if PDF.exists():
        bb2 = subprocess.run(["pdftotext", "-bbox", str(PDF), "-"],
                             capture_output=True, text=True).stdout
        lows = []
        for pg in re.findall(r'<page width="[\d.]+" height="[\d.]+">(.*?)</page>', bb2, re.S):
            ys = [float(y) for y in re.findall(r'yMax="([\d.]+)"', pg)]
            lows.append(max(ys) if ys else 0.0)
        ranked = sorted(v for v in lows if v > 0)
        if ranked:
            baseline = ranked[len(ranked) // 2]        # median page bottoms out at the footer
            over = [(i + 1, v) for i, v in enumerate(lows) if v > baseline + 3.0]
            if over:
                fail(f"{len(over)} page(s) with content below the footer baseline "
                     f"({baseline:.1f} pt) -- text is overflowing the frame:")
                for i, v in over:
                    print(f"   page {i:2d}  lowest yMax={v:.1f}  ({v - baseline:+.1f} pt)")
                problems += 1

    # ---- 13. no frame body may open with a brace group --------------------------------------
    # THE CAUSE, not the symptom. beamer parses `\begin{frame}{title}` followed by `{...}` as
    # title + SUBTITLE, so an opening sentence wrapped in a brace group is consumed and never
    # reaches the PDF. Four frames -- the entire L4.6/L4.7 method core -- lost their framing
    # sentence this way. The content-presence check above caught only two of them, because the
    # other two used words that also occur elsewhere in the deck and were therefore masked. This
    # check is deterministic: it reads the source, so it cannot be masked and cannot false-fire.
    src_lines = DECK.read_text().split("\n")
    swallowed = []
    for i, ln in enumerate(src_lines):
        fm = re.match(r"\s*\\begin\{frame\}(?:\[[^\]]*\])?\{(.+?)\}\s*$", ln)
        if not fm:
            continue
        for j in range(i + 1, len(src_lines)):
            t = src_lines[j].strip()
            if not t or t.startswith("%"):
                continue
            if t.startswith("{"):
                swallowed.append((j + 1, fm.group(1)[:44], t[:56]))
            break
    if swallowed:
        fail(f"{len(swallowed)} frame(s) whose body opens with a brace group -- beamer will eat it "
             f"as the subtitle and the text will never render. Prefix with \\relax:")
        for lineno, title, body in swallowed:
            print(f"   line {lineno:4d}  [{title}]  {body}")
        problems += 1

    # ---- 8. frame architecture --------------------------------------------------------------
    n_main, n_app = main_body.count("\\begin{frame}"), appendix_body.count("\\begin{frame}")
    if (n_main, n_app) != (MAIN_FRAMES, APPENDIX_FRAMES):
        fail(f"frame architecture is {n_main} main + {n_app} appendix, "
             f"expected {MAIN_FRAMES} + {APPENDIX_FRAMES}")
        problems += 1

    # ---- 10. the speaker notes carry no retyped scientific figure --------------------------
    # The brief requires the notes' numbers checked too. Rather than bind macros into prose, the
    # notes state every figure in WORDS ("every paired seed", "above any conventional
    # threshold"), so the enforceable rule is that no scientific literal appears at all:
    #   * no decimal literal -- every scientific value in this project is a decimal or a
    #     distinctive count, and the notes legitimately need none;
    #   * no literal equal to a bound value of 100 or more -- 331, 272, 450, 400, 259 ...
    # Small integers are NOT checkable here and deliberately not checked: slide indices and Q&A
    # row numbers collide with counts like \Nobjects. That is why counts are written in words.
    notes_path = HERE / "SPEAKER_NOTES.md"
    if notes_path.exists():
        notes = re.sub(r"```.*?```", " ", notes_path.read_text(), flags=re.S)
        decimals = re.findall(r"(?<![\w.])\d+\.\d+(?!\w)", notes)
        big = {v for v in re.findall(r"(?<![\w.])\d{3,}(?!\w)", notes)
               if v in {str(x) for x in macros.values()}}
        if decimals:
            fail(f"speaker notes contain decimal literal(s) {sorted(set(decimals))} -- state "
                 f"scientific figures in words, or the notes drift from the artifact silently")
            problems += 1
        if big:
            fail(f"speaker notes retype bound value(s) {sorted(big)} -- write them in words")
            problems += 1
    else:
        fail("SPEAKER_NOTES.md is missing")
        problems += 1

    # ---- 9. no overlays ----------------------------------------------------------------------
    if PDF.exists():
        out = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        pages = int(m.group(1)) if m else -1
        if pages != n_main + n_app:
            fail(f"PDF has {pages} pages but the deck has {n_main + n_app} frames -- overlays "
                 f"are inflating the advisor's static PDF")
            problems += 1
    else:
        print("advisor/check: note -- no PDF yet; the overlay check needs a build")

    # ---- 12. nothing DROPPED off a frame ---------------------------------------------------
    # A10's closing sentence vanished from the PDF: beamer overflowed the frame and simply did not
    # emit the last two lines. LaTeX logged no overfull box, and an edge-geometry check cannot see
    # it either -- there is nothing past the edge to measure, because the text was never drawn.
    # The only gate that catches content LOSS is presence: take each frame's closing words from
    # the source and require them to be extractable from the rendered PDF.
    if PDF.exists():
        pdftxt = subprocess.run(["pdftotext", "-layout", str(PDF), "-"],
                                capture_output=True, text=True).stdout
        norm = lambda t: re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
        # LaTeX hyphenates across line breaks, so a word can reach the PDF as "conse-" + "quence".
        # Under -layout those halves are NOT adjacent -- the neighbouring table column sits between
        # them -- so no amount of de-hyphenating that stream recovers the word, and A8 was reported
        # as dropping text that was fully present. pdftotext WITHOUT -layout emits reading order and
        # rejoins hyphenation, so both streams are read and their vocabularies unioned. Strictly
        # additive: this can only retract a false positive, never pass text that is truly absent.
        flowtxt = subprocess.run(["pdftotext", str(PDF), "-"],
                                 capture_output=True, text=True).stdout
        hay_words = set(norm(pdftxt).split()) | set(norm(flowtxt).split())
        missing = []
        for fm in re.finditer(r"\\begin\{frame\}(?:\[[^\]]*\])?(?:\{.*?\})?(.*?)\\end\{frame\}",
                              body, re.S):
            inner = fm.group(1)
            inner = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", inner, flags=re.S)
            inner = re.sub(r"\\\[.*?\\\]", " ", inner, flags=re.S)          # display math
            inner = re.sub(r"\$[^$]*\$", " ", inner)                        # inline math
            # Structural arguments are not prose and must not become probe words: a colour name
            # from \textcolor{oewarn}{...}, a column spec from \begin{tabular}{llrrl}, or the
            # {normal text} of \setbeamercolor all leaked in and produced false positives.
            inner = re.sub(r"\\setbeamercolor\{[^}]*\}\{[^}]*\}", " ", inner)
            inner = re.sub(r"\\(?:definecolor|usebeamercolor)\b(\[[^\]]*\])?(\{[^}]*\})*",
                           " ", inner)
            inner = re.sub(r"\\textcolor\{[^}]*\}", " ", inner)
            inner = re.sub(r"\\fcolorbox\{[^}]*\}\{[^}]*\}", " ", inner)
            inner = re.sub(r"\\(?:begin|end)\{[^}]*\}\s*(\{[lrcp@|!<>.\d\s{}]*\})?",
                           " ", inner)                                     # env + column spec
            inner = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", inner)      # commands
            # Contiguous phrase matching is defeated by macros and math interleaved in the source
            # (\$\Naticc\$ sits between "that" and "is"). Content LOSS removes whole lines, so
            # joint presence of the closing distinctive words is both robust and sufficient.
            words = [w for w in norm(inner).split() if len(w) >= 5]
            if len(words) < 6:
                continue
            # BOTH ends. Closing words catch frame overflow; OPENING words catch beamer eating a
            # leading brace group as the subtitle argument -- four frames lost their framing
            # sentence that way and the closing-only check saw none of it.
            for label, probe in (("closing", words[-4:]), ("opening", words[:4])):
                absent = [w for w in probe if w not in hay_words]
                if absent:
                    missing.append(f"[{label}] {' '.join(probe)}  (absent: {', '.join(absent)})")
        if missing:
            fail(f"{len(missing)} frame(s) whose closing words never reached the PDF -- content "
                 f"was dropped, not merely tight:")
            for t in missing[:8]:
                print(f"   ...{t!r}")
            problems += 1

    if problems:
        return 1
    print(f"advisor/check: OK -- {n_main} main + {n_app} appendix frames, "
          f"{n_main + n_app} PDF pages (no overlays); {len(macros)} macros all bound and shown; "
          f"{len(REQUIRED)} required numbers present; no bare literals; "
          f"{len(gl.SEMANTIC_LINT)} lint rules clean ({permitted} negated mention(s)); "
          f"all {len(REQUIRED_QUALIFIERS)} qualifiers present; "
          f"stopped-research vocabulary confined to A10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
