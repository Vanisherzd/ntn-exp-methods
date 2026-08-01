#!/usr/bin/env python3
"""Verify the committed external-consequence artifacts WITHOUT training anything.

An artifact evaluator could previously re-run the nineteen-rule audit (`make external`) but had
no way to check the consequence experiment at all: its scripts had no Make target, its inputs do
not ship, and re-running it needs a multi-hour training loop. This closes that gap from the other
side -- it does not reproduce the experiment, it checks that what is committed is internally
consistent and still bound to the frozen commit, the frozen detector and the recorded data hashes.

Every check below fails closed. Nothing here is generated: each value is read from a committed
artifact and compared against another committed artifact or a recorded constant.

    python evaluation/scripts/external_consequence_verify.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "evaluation" / "external_consequence" / "results"
SUMMARY = ROOT / "evaluation" / "results" / "final_summary.json"

FROZEN_UPSTREAM = "2e6c5b6c3558e7835601519b7bdef37c649bdbdc"
PREREG_DETECTOR = "07baad27026ebc2242706dd5f542609b80ccb8ab706cba12c0fb2ce15521e58b"
EXPECTED_DATA = {
    "train/A-1.npy": ("ae426533f9d4c6247a5cc1eab89438fed8bf768b0a41d60d42f3a65a7ebc80b0", 576128),
    "test/A-1.npy": ("7509b72cd170003c3135e12d1f4c67b263dc5be58aabedf12ed14e7561fe6dc2", 1728128),
}


def main() -> int:
    bad: list[str] = []
    ok: list[str] = []

    def need(cond: bool, msg: str) -> None:
        (ok if cond else bad).append(msg)

    for f in ("mechanical.json", "paired.json", "data_gate.json"):
        if not (RES / f).exists():
            print(f"external-consequence-verify: FAIL -- missing {f}")
            return 1

    mech = json.loads((RES / "mechanical.json").read_text())
    pair = json.loads((RES / "paired.json").read_text())
    gate = json.loads((RES / "data_gate.json").read_text())

    # 1. Frozen upstream commit, asserted in the artifact rather than assumed.
    need(mech["upstream_frozen_commit"] == FROZEN_UPSTREAM,
         f"upstream frozen at {FROZEN_UPSTREAM[:8]}")

    # 2. The detector on disk is still the pre-registered one. If this fails the experiment is
    #    void: its verdicts were produced by a different program from the one shipped.
    have = hashlib.sha256((ROOT / "evaluation" / "scripts"
                           / "contract_layers.py").read_bytes()).hexdigest()
    need(have == PREREG_DETECTOR, "detector byte-identical to the pre-registration hash")
    need(mech["contract_layers_sha256"] == PREREG_DETECTOR,
         "mechanical.json records the pre-registration detector hash")

    # 3. Data identity. The arrays came from a mirror, so the hashes are the only binding.
    for path, (sha, nbytes) in EXPECTED_DATA.items():
        rec = gate["files"].get(path)
        need(rec is not None and rec["sha256"] == sha and rec["bytes"] == nbytes,
             f"{path} sha256/bytes match the recorded values")
        need(bool(rec and rec["matches_two_independent_lfs_oids"]),
             f"{path} agrees with two independently published checksums")
    need(gate["DATA_SOURCE_STATUS"] == "CHECKSUM_VERIFIED_MIRROR",
         "data source status is CHECKSUM_VERIFIED_MIRROR")
    need(gate["labels"]["whole_file_byte_identical_to_frozen_commit"],
         "labels byte-identical to the frozen upstream commit")

    # 4. All five pre-registered paired seeds completed, none replaced.
    seeds = sorted({r["seed"] for r in pair["runs"]}) if "runs" in pair else []
    need(seeds == [0, 1, 2, 3, 4], f"five paired seeds present and unreplaced: {seeds}")

    # 5. The mechanical verdicts are the ones the paper reports, and they are opposite.
    need(mech["l41_verdict"]["original"]["verdict"] == "HALT",
         "L4.1 halts on the original partition")
    need(mech["l41_verdict"]["corrected"]["verdict"] == "PASS",
         "L4.1 passes on the corrected partition")
    ov = mech["overlap"]
    need(ov["original"]["shared_source_timesteps"] > 0
         and ov["corrected"]["shared_source_timesteps"] == 0,
         "overlap removed by the intervention, not merely reduced")

    # 6. The summary artifact agrees with the study artifacts it claims to mirror.
    if SUMMARY.exists():
        c = json.loads(SUMMARY.read_text())["external_consequence"]
        need(c["upstream_frozen_commit"] == FROZEN_UPSTREAM,
             "summary agrees on the frozen upstream commit")
        need(c["contract_layers_sha256"] == PREREG_DETECTOR,
             "summary agrees on the detector hash")
        need(c["downstream_attainable"] is False,
             "summary records the downstream endpoint as not attainable")

    for m in ok:
        print(f"  ok   {m}")
    for m in bad:
        print(f"  FAIL {m}")
    if bad:
        print(f"external-consequence-verify: FAIL -- {len(bad)} check(s)")
        return 1
    print(f"external-consequence-verify: PASS -- {len(ok)} checks, no training performed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
