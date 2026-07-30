"""Causal transmission registry: row membership frozen BEFORE labels exist.

The discipline this encodes is the second most reusable asset from the stopped line.
Its purpose is to make one class of leakage structurally impossible rather than
merely tested for.

Rule: the registry is built and hashed before any label source is consulted. Later
information may change a row's label STATUS, VALUE, UNCERTAINTY or CLOSURE TIME. It
may never change WHETHER THE ROW EXISTS.

Two historical failures this prevents:
  * rows silently dropped when no qualifying later reference existed -- the drop rate
    rose with the study covariate to 100 % for one object, making membership a
    function of the future catalogue;
  * rows silently CREATED because the schedule's extent ended at the archive's last
    entry, so 29 % of one object's rows appeared only because more data had been
    downloaded.

The second is why `freeze_window` is a required argument and not an optional one.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping

import numpy as np


class LabelStatus(str, Enum):
    """Every scheduled row carries exactly one. None is ever removed."""
    COMPLETE = "COMPLETE"
    CENSORED_INSUFFICIENT_REFERENCES = "CENSORED_INSUFFICIENT_REFERENCES"
    AMBIGUOUS_HIGH_SPREAD = "AMBIGUOUS_HIGH_SPREAD"
    INVALID_SOURCE_METADATA = "INVALID_SOURCE_METADATA"


@dataclass(frozen=True)
class FreezeWindow:
    """Absolute schedule bounds, declared in advance.

    Deriving either bound from the data on hand (first/last available entry) makes
    the schedule a property of the download rather than of the system. Pass explicit
    values.
    """
    t_start: float
    t_end: float

    def __post_init__(self) -> None:
        if not self.t_end > self.t_start:
            raise ValueError("freeze window must have positive extent")


@dataclass
class Registry:
    """Immutable-by-convention row set. Hash it, then never mutate it."""
    columns: dict[str, np.ndarray]
    freeze_window: FreezeWindow
    id_columns: tuple[str, ...] = ("tx_id", "pass_id", "episode_id")
    _frozen_hash: str | None = field(default=None, repr=False)

    def __len__(self) -> int:
        first = next(iter(self.columns.values()))
        return int(np.asarray(first).shape[0])

    def content_hash(self) -> str:
        h = hashlib.sha256()
        for k in sorted(self.columns):
            h.update(k.encode())
            a = np.asarray(self.columns[k])
            if a.dtype == object or a.dtype.kind in "US":
                h.update("\x00".join(map(str, a.tolist())).encode())
            else:
                h.update(np.ascontiguousarray(a).tobytes())
        h.update(json.dumps([self.freeze_window.t_start,
                             self.freeze_window.t_end]).encode())
        return h.hexdigest()

    def freeze(self) -> str:
        self._frozen_hash = self.content_hash()
        return self._frozen_hash

    def assert_unmodified(self) -> None:
        """Call after label construction. Raises if the registry moved."""
        if self._frozen_hash is None:
            raise RuntimeError("registry was never frozen")
        if self.content_hash() != self._frozen_hash:
            raise AssertionError("registry mutated after freeze")

    def assert_ids_unique(self) -> None:
        for col in self.id_columns:
            if col not in self.columns:
                continue
            a = np.asarray(self.columns[col])
            if col == "tx_id" and len(set(a.tolist())) != a.shape[0]:
                raise AssertionError(f"{col} is not unique")

    def assert_within_window(self, time_column: str = "t_tx") -> None:
        t = np.asarray(self.columns[time_column], dtype=float)
        if t.size and (t.min() < self.freeze_window.t_start
                       or t.max() > self.freeze_window.t_end):
            raise AssertionError("row outside the declared freeze window")


def build_registry(rows: Iterable[Mapping[str, Any]], freeze_window: FreezeWindow,
                   ) -> Registry:
    """Assemble and freeze. Nothing here may consult a label source."""
    rows = list(rows)
    if not rows:
        raise ValueError("no scheduled rows")
    keys = list(rows[0])
    cols: dict[str, np.ndarray] = {}
    for k in keys:
        vals = [r[k] for r in rows]
        cols[k] = (np.array(vals, dtype=object)
                   if isinstance(vals[0], str) else np.asarray(vals, dtype=float))
    reg = Registry(cols, freeze_window)
    reg.freeze()
    reg.assert_ids_unique()
    return reg


def assert_membership_independent_of_future(build_fn, freeze_window: FreezeWindow,
                                            full_source, truncated_source) -> None:
    """The falsifiable form of "row membership does not depend on the future".

    `build_fn(source, freeze_window) -> Registry`. Both arms use the SAME declared
    window; only the source data differ. The historical version of this test pinned
    the window on both arms, which is precisely the parameter carrying the
    dependence -- so it could not fail.
    """
    a = build_fn(full_source, freeze_window)
    b = build_fn(truncated_source, freeze_window)
    ta = np.asarray(a.columns["tx_id"]).tolist()
    tb = np.asarray(b.columns["tx_id"]).tolist()
    if ta != tb:
        raise AssertionError(
            f"row membership changed with future data: {len(ta)} vs {len(tb)} rows")
