# hardware/ — NOT CURRENT EVIDENCE, NOT TRACKED

> **The current paper claims no RF, packet, or link-layer result of any kind.**
>
> Everything here belongs to a stopped research line. It is **untracked** — no file in this tree is
> in Git, so it is also **not in the pre-cleanup bundle**. It exists only on this machine.

Current research: *Orbit-Evidence* — `../paper/icc_main.tex`. See `../docs/HISTORY.md`.

## Why this tree was left in place

The repository cleanup removed stopped-research material from the active checkout because Git
history and the pre-cleanup bundle preserve it. **That guarantee does not apply here.** These are
raw IQ captures and bench artifacts that were never committed, so deleting them would be permanent
loss with no recovery path. They were therefore left untouched, pending an explicit decision.

If this material is wanted long-term, it needs its own archival copy outside this repository. If it
is not wanted, it can be deleted — but that is irreversible and is not something the cleanup did on
its own authority.

## Related

`../dataraw/` holds the local Space-Track records behind the committed real-data artifacts. It is
also untracked, also absent from the bundle, and `make realdata` skips gracefully when it is not
present — so the gates do not need it, but it is the only copy of that input.
