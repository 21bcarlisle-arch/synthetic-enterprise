# [WORKER-REPORT] The fourth wedge of one shape — the derived-artefact class is now closed (2026-08-10)

**Written by:** the scheduled worker tick drawn on the RUNG-1 publish-gate wedge
(56 consecutive failures in the episode, ~436 min, no pass at HEAD `311eb95da`).

**Closes the class filed as** `WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS_2026-08-09`.
(Deliberately not an `**Advances:**` declaration — that form takes an atom ID, and this closes a
filed CLASS, not an atom. Writing prose there mints `unknown_atom` violations into the forward
ledger, which this tick did once and caught with the very control it was building.)

## The cause, in one line (R9: observed, with evidence)

```
FAILED tests/background/test_blocked_atom_visibility.py::test_the_committed_document_agrees_with_the_live_derivation
E   AssertionError: FINDING: DOC DRIFT: docs/design/BLOCKED_ATOM_VISIBILITY.md
    disagrees with the derivation -- rerun with --write
```

`docs/design/BLOCKED_ATOM_VISIBILITY.md` is a PROJECTION of the maturity map. Seven atoms were
minted (249 → 256, all `H_harness`); nothing regenerated the projection; its blocking `--check`
test went red at HEAD. Nothing was *wrong* — only *stale*. Regenerating it changed three lines.

## The suspect list was wrong again — eight for eight, twice running

The alarm cited eight findings to "draw FIRST". **None of them was the cause**, exactly as the
previous tick reported in `WORKER_REPORT_PUBLISH_WEDGE_SUSPECT_DISPOSITION_2026-08-09`. The
finding that *did* name this class — `..._DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS_...` — was
again **not cited**. This tick did not re-litigate the eight; it read the traceback in
`sim-runner-log.md`, which named the cause in one line. That is now the second consecutive
episode where the citation mechanism cost nothing only because the tick ignored it.

**This strengthens, not repeats, the filed complaint:** a suspect list that is 0-for-16 across
two episodes while the correct finding sits uncited is not a weak control, it is an
anti-signal. Its own finding stays QUEUED (SELF_INTERRUPT_DISCIPLINE) — but its rank should now
reflect two measured failures, not one.

## Why an instance fix was not allowed to close it (R10)

Three of this episode's five causes, and now a fourth, are the same shape:

| Date | Projection | What moved its sources |
|---|---|---|
| 2026-08-09 | `FORWARD_ATTACHMENT_LEDGER.md` | a finding archived to `staging/done/` |
| 2026-08-09 | `PULL_FORWARD_PROPOSALS.md` | three findings staged |
| 2026-08-10 | `BLOCKED_ATOM_VISIBILITY.md` | seven atoms minted into the map |

Every one was repaired by a `--write` CLI that already existed and **had no caller**. The
artefact was correct only for as long as nobody touched the machine's normal metabolism.

## What was built

**`background/derived_artefact_register.py`** — the register, with two consumers.

* **Completeness is fail-closed, not a hand-kept list.** `discover()` finds derived artefacts by
  AST-scanning `background/` and `tools/` for a module that both takes `--write` and owns a
  module-level `docs/design/*.md` path. `unregistered()` is the difference against `REGISTER`.
  A hand-maintained index is the fail-open shape this project already has memory of; the next
  derived artefact cannot silently escape this one.
* **Repair renders from HEAD, not from the working tree.** Since
  `DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09` the gate's subject is a clean checkout of
  HEAD. That makes the obvious implementation wrong — rendering in the working tree projects
  *uncommitted* sources, which the gate would then red on. It would have swapped a stale-artefact
  wedge for a phantom-artefact wedge. `repair_from()` renders inside the checkout the gate
  already materialises.
* **Fixed point, and non-convergence is reported as a defect.** `forward_attachment_register`
  scans `docs/design/**`, so repairing one projection can invalidate another. The repair iterates
  and *says so* if it does not settle, rather than looping or silently giving up.

**Wired into the publish path** (`process_run_complete._repair_derived_artefacts_in`), between
the checkout and the gate. The rendering lands in the checkout *and* the tree, so this cycle's
gate sees the repair and `git_commit_push` publishes it in the same cycle — the deadlock
(the gate reds, so the repair can never be committed, so the gate reds) is gone. The commit path
takes its paths from `REGISTER`, so a future artefact is committed automatically.

### The design question the finding left open

It asked whether repair belongs in the publish path or the staging-archive path — "both
defensible, wants a design pass, not a guess". **The publish path**, decided on this wedge's
evidence rather than taste: today's drift came from a *map mint*, not a staging archive, so an
archive-path repair would not have prevented it. The publish path is trigger-agnostic.

### R15 — the control can fail, proven both ways

`tests/background/test_derived_artefact_register.py`, 12 tests, all green:

* **completeness mutation** — a real module planted in `tools/` that takes `--write` and owns a
  `docs/design/*.md` path is NAMED by `unregistered()`; removing it clears. Not a monkeypatch:
  the control scans the source tree, so a fake that bypasses the scan would prove nothing.
* **orphan mutation** — a register entry with no module is named.
* **independence** — emptying `REGISTER` must not change `discover()`. Proven *functionally*; an
  earlier version grepped the function's source text for `"REGISTER"`, which is brittle and
  proves nothing about behaviour.
* **staleness / repair mutations** — a corrupted rendering is named, then cleared, then restored
  to the derivation of committed truth, and repair is idempotent.

Two defects in this work were caught by its own tests and fixed: `repair_from` raised
`SameFileError` when both roots coincide, and the checkout fixture initially produced a tree with
no `.git`, which killed the clock probe's `git blame` — **the same defect that wedged publishing
once already**. The fixture now reuses the production `_make_checkout_a_repo` rather than growing
a weaker second copy.

## Noted, not fixed (queued)

The **pre-gate atom_status fold** (`process_run_complete`, ~line 2610) carries the comment
"Working-tree fold is enough for the gate". That was true when written and is **no longer true**:
the gate's subject moved to a HEAD checkout, so a working-tree fold is invisible to it. Same
class as the bug closed here, different organ. Not touched this tick — it is a live mechanism
whose stated premise died under it, and it deserves its own draw rather than an opportunistic
edit inside a priority-zero unwedge.

## The control caught the class on its own author, within the hour

Writing *this report* into `docs/staging/` immediately turned `FORWARD_ATTACHMENT_LEDGER.md`
stale — the fifth instance, produced by the single act of filing a document. The new
`--check` named it before it could reach a commit, and it was regenerated into the same commit.
Under yesterday's machine this report would itself have wedged the next publish cycle.

It also caught a second, unrelated mistake in the same pass: the report's first draft used the
`**Advances:**` declaration form to point at a filed *class*, and that form takes an ATOM ID, so
it minted two `unknown_atom` violations. Worth recording as its own small lesson — a non-zero
`--check` on this artefact family means "not fresh", which covers **content violations as well as
staleness**. "Stale" must not be read as "regenerating will fix it": a violation needs the
SOURCE corrected, and the repair reports non-convergence rather than pretending otherwise.

## Evidence

* Publish gate at HEAD+repair: `1 failed → 0 failed`; full gate argv run to completion, green.
* `python3 -m background.derived_artefact_register --check` → `3 registered artefact(s), 0 stale,
  0 unregistered, 0 orphaned.` rc=0
* `tests/background/test_derived_artefact_register.py` — 12 passed.
* `tests/background/test_seat_guard_daemons.py` — 23 passed (the new entrypoint is guarded).
* `tests/background/test_process_run_complete.py` — 62 passed.

— Worker tick, 2026-08-10.
