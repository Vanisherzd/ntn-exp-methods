#!/usr/bin/env python3
"""Catalog-driven historical TLE acquisition for the Paper 1+ campaign (Phase 1).

Reads `satellite_catalog.yaml`, resolves each regime slot to concrete NORAD IDs
via the Space-Track satcat, and downloads `gp_history` per object into
`dataraw/spacetrack/<slug>_<norad>/`.

This script FETCHES ONLY. It computes no residual and makes no claim. It reuses
the authentication and download helpers already in
`tools/fetch_spacetrack_object_family.py` rather than duplicating them.

Credentials come from the environment or `.env.spacetrack`:
  SPACETRACK_USERNAME / SPACETRACK_PASSWORD
Nothing is written to the repository except under the git-ignored `dataraw/`.

Without credentials the script prints the resolved acquisition plan and exits
non-zero WITHOUT downloading anything, so it is safe to run in CI or offline.

  uv run experiments/exp14_multisat_generalization_matrix/fetch_tle_catalog.py --plan
"""

from __future__ import annotations

import argparse
import datetime as dt
import http.cookiejar
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import fetch_spacetrack_object_family as st  # noqa: E402

DEFAULT_CATALOG = HERE / "satellite_catalog.yaml"
DEFAULT_OUT = ROOT / "dataraw" / "spacetrack"
BASE = "https://www.space-track.org/basicspacedata/query/class"


def load_catalog(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def acquisition_plan(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten regime slots into concrete fetch intents."""
    plan: list[dict[str, Any]] = []
    for regime in catalog.get("regimes", []):
        for target in regime.get("targets", []):
            plan.append(
                {
                    "regime": regime["id"],
                    "object_name": target.get("object_name"),
                    "object_name_pattern": target.get("object_name_pattern"),
                    "norad_id": target.get("norad_id"),
                    "family": target.get("family", "unknown"),
                    "expected_regime": target.get("expected_regime", ""),
                    "sample_count": int(target.get("sample_count", 1)),
                    "resolved": [],
                }
            )
    return plan


def _open_session() -> Any:
    st.load_dotenv(ROOT / ".env.spacetrack")
    user = os.environ.get("SPACETRACK_USERNAME") or os.environ.get("SPACETRACKUSER")
    pwd = os.environ.get("SPACETRACK_PASSWORD") or os.environ.get("SPACETRACKPASS")
    if not user or not pwd:
        return None
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    body = urllib.parse.urlencode({"identity": user, "password": pwd}).encode()
    req = urllib.request.Request(
        "https://www.space-track.org/ajaxauth/login",
        data=body,
        headers={"User-Agent": "LEO-Hybrid-PGRL paper1plus fetch"},
    )
    with opener.open(req, timeout=90) as resp:
        resp.read()
    return opener


def resolve_targets(opener, entry: dict[str, Any]) -> list[dict[str, str]]:
    """Resolve one plan entry to concrete satcat records."""
    if entry["norad_id"]:
        query = f"{BASE}/satcat/NORAD_CAT_ID/{entry['norad_id']}/format/json"
    elif entry["object_name"]:
        name = urllib.parse.quote(entry["object_name"])
        query = f"{BASE}/satcat/OBJECT_NAME/{name}/format/json"
    else:
        pattern = urllib.parse.quote(entry["object_name_pattern"].replace("*", "~~"))
        query = (
            f"{BASE}/satcat/OBJECT_NAME/{pattern}/CURRENT/Y/DECAY/null-val"
            "/orderby/LAUNCH%20desc/format/json"
        )
    parsed = json.loads(st.open_url(opener, query).decode())
    rows = parsed if isinstance(parsed, list) else []
    return [
        {
            "norad": str(r.get("NORAD_CAT_ID", "")).strip(),
            "object_name": str(r.get("OBJECT_NAME", "")).strip(),
        }
        for r in rows[: entry["sample_count"]]
        if str(r.get("NORAD_CAT_ID", "")).strip()
    ]


def fetch_history(opener, norad: str, object_name: str, out_root: Path) -> Path:
    slug = f"{st.safe_slug(object_name)}_{norad}"
    outdir = out_root / slug
    outdir.mkdir(parents=True, exist_ok=True)
    queries = {
        f"gp_history_{norad}.json": (
            f"{BASE}/gp_history/NORAD_CAT_ID/{norad}"
            "/orderby/EPOCH%20asc/format/json"
        ),
        f"gp_history_{norad}.tle": (
            f"{BASE}/gp_history/NORAD_CAT_ID/{norad}"
            "/orderby/EPOCH%20asc/format/tle"
        ),
        f"satcat_{norad}.json": f"{BASE}/satcat/NORAD_CAT_ID/{norad}/format/json",
    }
    for fname, url in queries.items():
        st.fetch_to(opener, url, outdir / fname)
    manifest = {
        "object_name": object_name,
        "norad_cat_id": norad,
        "fetched_at_utc": dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "source": "Space-Track basicspacedata API",
        "credentials_not_stored": True,
        "reference_is_measured_truth": False,
        "claim_scope": "orbital input only; not hardware or RF evidence",
        "files": [
            {
                "path": str(p),
                "bytes": p.stat().st_size,
                "sha256": st.sha256_file(p),
            }
            for p in sorted(outdir.iterdir())
            if p.is_file() and p.name != "fetch_manifest.json"
        ],
    }
    (outdir / "fetch_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return outdir


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--plan",
        action="store_true",
        help="print the acquisition plan and exit without contacting the network",
    )
    args = parser.parse_args(argv)

    catalog = load_catalog(args.catalog)
    plan = acquisition_plan(catalog)
    print(
        f"catalog: {args.catalog.name}  slots={len(plan)}  "
        f"requested_objects={sum(e['sample_count'] for e in plan)}  "
        f"minimum={catalog.get('minimum_satellites')}  "
        f"regimes={len(catalog.get('regimes', []))}"
    )
    for entry in plan:
        label = entry["object_name"] or entry["object_name_pattern"]
        print(
            f"  [{entry['regime']}] {label} x{entry['sample_count']} "
            f"norad={entry['norad_id'] or 'resolve-at-fetch'} "
            f"-- {entry['expected_regime']}"
        )
    if args.plan:
        return 0

    opener = _open_session()
    if opener is None:
        print(
            "\nNo Space-Track credentials found "
            "(SPACETRACK_USERNAME / SPACETRACK_PASSWORD or .env.spacetrack).\n"
            "Nothing was downloaded and no result is claimed. "
            "Set credentials and rerun to acquire the archive.",
            file=sys.stderr,
        )
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)
    fetched = 0
    for entry in plan:
        try:
            entry["resolved"] = resolve_targets(opener, entry)
        except Exception as exc:  # network / query failures are not fatal
            print(f"  resolve failed for {entry['regime']}: {exc}", file=sys.stderr)
            continue
        for hit in entry["resolved"]:
            fetch_history(opener, hit["norad"], hit["object_name"], args.out_dir)
            fetched += 1
    print(f"fetched {fetched} object histories into {args.out_dir}")
    if fetched < int(catalog.get("minimum_satellites", 6)):
        print(
            f"WARNING: {fetched} objects is below the catalog minimum "
            f"({catalog.get('minimum_satellites')}). No generalization claim "
            "may be made from this set.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
