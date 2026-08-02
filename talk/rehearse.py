#!/usr/bin/env python3
"""Time a live rehearsal and judge it against the acceptance gate.

This exists because the timings in SPEAKER_OUTLINE.md are budgets computed by summation.
A budget is not a rehearsal. Only a person speaking the talk produces a rehearsal time, so
this records one rather than estimating it.

    python talk/rehearse.py            # run one rehearsal
    python talk/rehearse.py --report   # judge the recorded runs against the gate

Press ENTER to advance a slide. Type 'b' + ENTER to step back (the step is still timed --
a rehearsal you correct mid-run is not an uninterrupted one, and the log records it).
Ctrl-C abandons the run without saving.

Records to talk/rehearsal_log.json. Nothing here touches the deck.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "rehearsal_log.json"

SLIDES = [
    (1, "Title / thesis", 15),
    (2, "Why ordering alone is insufficient", 30),
    (3, "Four obligations outside one dataset", 40),
    (4, "What relational validity means", 60),
    (5, "How Orbit-Evidence operationalises it (4 clicks)", 65),
    (6, "What the two relational checks do", 55),
    (7, "Is L4.7 calibrated before use", 45),
    (8, "Does the unit problem appear in real orbital data", 65),
    (9, "Can the frozen contract be applied externally", 45),
    (10, "Does correcting a violation change the experiment", 55),
    (11, "What is actually new", 35),
    (12, "What the paper does not establish", 30),
    (13, "Takeaway", 15),
]
# Slides that must not be rushed. Sourced from the acceptance criteria, not from taste.
CONCEPTUAL = {4, 5, 6}          # must receive the most conceptual time
MUST_NOT_RUSH = {8, 10, 12, 13}  # real-data limits, intervention, limitations, takeaway
RUSH_FLOOR = 0.55                # under 55% of budget counts as rushed


def fmt(s: float) -> str:
    return f"{int(s // 60)}:{int(s % 60):02d}"


def run() -> int:
    print("\n  REHEARSAL — speak the talk. ENTER advances, 'b' steps back, Ctrl-C abandons.")
    print("  Start speaking when you press ENTER for slide 1.\n")
    input("  ready > ")
    t0 = time.monotonic()
    marks, i, backs = [], 0, 0
    while i < len(SLIDES):
        n, title, budget = SLIDES[i]
        start = time.monotonic()
        cmd = input(f"  [{n:2d}/13] {title}   (budget {fmt(budget)}) > ").strip().lower()
        dur = time.monotonic() - start
        if cmd == "b" and i > 0:
            backs += 1
            marks.append({"slide": n, "seconds": round(dur, 1), "stepped_back": True})
            i -= 1
            continue
        marks.append({"slide": n, "seconds": round(dur, 1), "stepped_back": False})
        i += 1
    total = time.monotonic() - t0

    run_rec = {"total_seconds": round(total, 1), "step_backs": backs, "slides": marks}
    runs = json.loads(LOG.read_text())["runs"] if LOG.exists() else []
    runs.append(run_rec)
    LOG.write_text(json.dumps({"runs": runs}, indent=1) + "\n")
    print(f"\n  total {fmt(total)}   step-backs {backs}   saved as run {len(runs)}\n")
    return report()


def report() -> int:
    if not LOG.exists():
        print("  no rehearsals recorded yet -- run `python talk/rehearse.py`")
        return 1
    runs = json.loads(LOG.read_text())["runs"]
    budget = {n: b for n, _, b in SLIDES}
    print(f"\n  {len(runs)} recorded rehearsal(s)\n")
    totals = []
    for k, r in enumerate(runs, 1):
        t = r["total_seconds"]
        totals.append(t)
        print(f"    run {k}: {fmt(t)}   step-backs {r['step_backs']}")
    print()

    fails = []
    if len(runs) < 3:
        fails.append(f"only {len(runs)} of 3 rehearsals recorded")
    over = [k for k, t in enumerate(totals, 1) if t > 600]
    if over:
        fails.append(f"run(s) {over} exceed 10:00")
    if totals:
        srt = sorted(totals)
        med = srt[len(srt) // 2] if len(srt) % 2 else (srt[len(srt) // 2 - 1]
                                                       + srt[len(srt) // 2]) / 2
        print(f"    median {fmt(med)}   (target 8:30-9:30)")
        if not (510 <= med <= 570):
            fails.append(f"median {fmt(med)} outside 8:30-9:30")

    # Per-slide checks on the most recent run: the gate is about WHERE the time went.
    last = {s["slide"]: s["seconds"] for s in runs[-1]["slides"] if not s["stepped_back"]}
    rushed = sorted(n for n in MUST_NOT_RUSH if last.get(n, 0) < budget[n] * RUSH_FLOOR)
    if rushed:
        fails.append(f"slides {rushed} rushed below {int(RUSH_FLOOR*100)}% of budget "
                     "(real-data limits / intervention / limitations / takeaway)")
    concept = sum(last.get(n, 0) for n in CONCEPTUAL)
    other = sum(v for n, v in last.items() if n not in CONCEPTUAL)
    if concept < other * 0.25:
        fails.append(f"slides 4-6 got {fmt(concept)} of {fmt(concept+other)} -- too little "
                     "conceptual time")

    print()
    if fails:
        print("  REHEARSAL GATE: NOT MET")
        for f in fails:
            print(f"    - {f}")
        return 1
    print("  REHEARSAL GATE: MET -- three runs under 10:00, median in range, "
          "no required slide rushed")
    return 0


if __name__ == "__main__":
    raise SystemExit(report() if "--report" in sys.argv else run())
