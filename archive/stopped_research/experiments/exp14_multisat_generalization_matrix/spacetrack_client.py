#!/usr/bin/env python3
"""Validated, throttled Space-Track access for the Paper 1+ campaign.

Two jobs, both learned the hard way from the 2026-07-27 acquisition:

1. **Never convert an API error into an empty result.** Space-Track returns
   rate-limit and other errors as HTTP 200 with a JSON *list* body such as
   ``[{"error": "You've violated your query rate limit. ..."}]``. That passes an
   ``isinstance(x, list)`` check, then loses every row to a field filter,
   yielding an empty list indistinguishable from "object not found". One such
   payload was archived and checksummed as if it were a SATCAT record, and the
   same failure most likely dropped the two BLACK KITE objects.

2. **Never burst.** The previous run issued ~35 requests in ~30 s against a
   documented 30/min limit and was throttled on its 27th archive write.

No credential value is ever read into a log, printed, or returned.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class ResponseState(str, Enum):
    """Explicit classification of every API response."""

    VALID = "VALID"
    EMPTY = "EMPTY"
    RATE_LIMITED = "RATE_LIMITED"
    API_ERROR = "API_ERROR"
    PARSE_ERROR = "PARSE_ERROR"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    UNRESOLVED = "UNRESOLVED"


RETRYABLE = {ResponseState.RATE_LIMITED}
# States that must never be archived as scientific data.
INVALID_STATES = {
    ResponseState.RATE_LIMITED,
    ResponseState.API_ERROR,
    ResponseState.PARSE_ERROR,
    ResponseState.IDENTITY_MISMATCH,
    ResponseState.UNRESOLVED,
}

RATE_LIMIT_MARKERS = ("rate limit", "violated your query", "throttle")


@dataclass
class Response:
    """One classified API response."""

    state: ResponseState
    body: bytes = b""
    rows: list[dict[str, Any]] = field(default_factory=list)
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.state is ResponseState.VALID

    @property
    def archivable(self) -> bool:
        """Only VALID bodies may enter the scientific manifest."""
        return self.state is ResponseState.VALID


def _classify_json(body: bytes) -> tuple[ResponseState, list[dict], str]:
    try:
        parsed = json.loads(body.decode("utf-8", errors="replace"))
    except Exception as exc:
        return ResponseState.PARSE_ERROR, [], f"json decode failed: {exc}"
    rows = parsed if isinstance(parsed, list) else [parsed]
    rows = [r for r in rows if isinstance(r, dict)]
    for row in rows:
        if "error" in row:
            message = str(row["error"])
            low = message.lower()
            state = (
                ResponseState.RATE_LIMITED
                if any(m in low for m in RATE_LIMIT_MARKERS)
                else ResponseState.API_ERROR
            )
            return state, [], message[:300]
    if not rows:
        return ResponseState.EMPTY, [], "response contained zero rows"
    return ResponseState.VALID, rows, ""


def classify_satcat(body: bytes, expected_norad: int | None = None) -> Response:
    """SATCAT must be a non-empty row list carrying a consistent identity."""
    state, rows, detail = _classify_json(body)
    if state is not ResponseState.VALID:
        return Response(state, body, [], detail)
    for field_name in ("NORAD_CAT_ID", "OBJECT_NAME"):
        if not any(str(r.get(field_name, "")).strip() for r in rows):
            return Response(
                ResponseState.API_ERROR, body, [], f"missing field {field_name}"
            )
    if expected_norad is not None:
        got = {str(r.get("NORAD_CAT_ID", "")).strip() for r in rows}
        if str(expected_norad) not in got:
            return Response(
                ResponseState.IDENTITY_MISMATCH,
                body,
                rows,
                f"requested NORAD {expected_norad}, response carried {sorted(got)}",
            )
    return Response(ResponseState.VALID, body, rows, "")


def classify_gp_history(body: bytes, expected_norad: int | None = None) -> Response:
    """GP_HISTORY must be element rows with at least NORAD_CAT_ID and EPOCH."""
    state, rows, detail = _classify_json(body)
    if state is not ResponseState.VALID:
        return Response(state, body, [], detail)
    missing = [
        f
        for f in ("NORAD_CAT_ID", "EPOCH")
        if not all(str(r.get(f, "")).strip() for r in rows)
    ]
    if missing:
        return Response(
            ResponseState.API_ERROR, body, [], f"rows missing {','.join(missing)}"
        )
    if expected_norad is not None:
        got = {str(r.get("NORAD_CAT_ID", "")).strip() for r in rows}
        if got != {str(expected_norad)}:
            return Response(
                ResponseState.IDENTITY_MISMATCH,
                body,
                rows,
                f"requested NORAD {expected_norad}, response carried {sorted(got)}",
            )
    return Response(ResponseState.VALID, body, rows, "")


def classify_tle(body: bytes) -> Response:
    """A TLE body must actually contain TLE lines, not an API error page."""
    text = body.decode("utf-8", errors="replace")
    low = text.lower()
    if any(m in low for m in RATE_LIMIT_MARKERS):
        return Response(ResponseState.RATE_LIMITED, body, [], "rate-limit text body")
    stripped = text.lstrip()
    if stripped.startswith(("{", "[", "<")):
        return Response(
            ResponseState.API_ERROR, body, [], "body is markup/JSON, not TLE text"
        )
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return Response(ResponseState.EMPTY, body, [], "empty TLE body")
    if not any(ln.startswith("1 ") for ln in lines):
        return Response(
            ResponseState.API_ERROR, body, [], "no TLE line-1 record found"
        )
    return Response(ResponseState.VALID, body, [], "")


class RequestScheduler:
    """Conservative throttle with bounded retry and increasing backoff."""

    def __init__(
        self,
        requests_per_minute: float = 18.0,
        max_retries: int = 4,
        initial_backoff_s: float = 20.0,
        backoff_factor: float = 2.0,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        # Headroom below the documented 30/min service limit.
        self.min_interval_s = 60.0 / max(1e-6, requests_per_minute)
        self.max_retries = max_retries
        self.initial_backoff_s = initial_backoff_s
        self.backoff_factor = backoff_factor
        self._sleep = sleep
        self._clock = clock
        self._last: float | None = None
        self.stats = {"requests": 0, "retries": 0, "waits": 0}

    def _pace(self) -> None:
        if self._last is not None:
            wait = self.min_interval_s - (self._clock() - self._last)
            if wait > 0:
                self.stats["waits"] += 1
                self._sleep(wait)
        self._last = self._clock()

    def fetch(
        self,
        do_request: Callable[[], bytes],
        classify: Callable[[bytes], Response],
        label: str = "",
    ) -> Response:
        """Paced request with bounded retry on retryable states."""
        backoff = self.initial_backoff_s
        response = Response(ResponseState.UNRESOLVED, detail="no attempt made")
        for attempt in range(self.max_retries + 1):
            self._pace()
            self.stats["requests"] += 1
            try:
                response = classify(do_request())
            except Exception as exc:
                response = Response(
                    ResponseState.API_ERROR, detail=f"transport error: {exc}"
                )
            if response.state not in RETRYABLE:
                if label:
                    print(f"    {response.state.value:<18} {label}")
                return response
            if attempt < self.max_retries:
                self.stats["retries"] += 1
                print(
                    f"    {response.state.value:<18} {label} "
                    f"-- retry {attempt + 1}/{self.max_retries} in {backoff:.0f}s"
                )
                self._sleep(backoff)
                backoff *= self.backoff_factor
        if label:
            print(f"    {response.state.value:<18} {label} -- retries exhausted")
        return response


def cached_response(
    path: Path, classify: Callable[[bytes], Response]
) -> Response | None:
    """Reuse a cached body only when it classifies VALID.

    A cached error payload must never suppress a re-fetch -- that is exactly how
    the corrupted OneWeb SATCAT would have persisted forever.
    """
    if not path.is_file():
        return None
    response = classify(path.read_bytes())
    return response if response.ok else None
