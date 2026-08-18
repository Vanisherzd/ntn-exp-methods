# archive/

This directory retains exactly one file:

**`KNOWN_INVALID_RESULTS.md`** — the record of results from the stopped research line that must
never be reused. It is retained because active submission metadata references it by this path
(`paper/submission/ARTIFACTS.md`, `paper/submission/README.md`).

Its role is current; its origin is historical.

Everything else formerly in this directory — the halted PGRL / Doppler-residual programme, the
retired manuscript trees, the causality audit, and the RF validation campaign — was removed from
the active checkout. The committed parts remain recoverable from Git history and the verified
pre-cleanup bundle. The parts that were **never committed** — 12 GB of conducted-IQ captures under
`hardware_validation/`, and the exp14 output under `stopped_research/` — were not in the bundle at
all, so they were archived outside the repository first and only then deleted:
`../../stopped-research-raw-archive-2026-08-18/` and
`../../orbit-evidence-historical-output-2026-08-18/`.

See [../docs/HISTORY.md](../docs/HISTORY.md) and [../docs/CLEANUP_RECORD.md](../docs/CLEANUP_RECORD.md) §4.
