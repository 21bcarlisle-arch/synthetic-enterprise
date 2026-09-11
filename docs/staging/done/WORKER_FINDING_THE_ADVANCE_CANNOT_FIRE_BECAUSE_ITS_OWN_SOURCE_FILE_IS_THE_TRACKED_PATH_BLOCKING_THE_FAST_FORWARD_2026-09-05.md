**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the advance cannot fire because its own source file is the tracked path blocking the fast-forward

**Measured 2026-09-05 00:10–01:15Z, worker tick, on the shared tree.** This extends
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_A_MECHANICAL_ADVANCE_AT_THE_REFUSAL_LETS_A_DRAINED_QUEUE_CLOSE_ITS_EPISODE_2026-09-04.md`,
which is COMPLETE and is not reopened here. Its P1 was refuted at 22:39Z and closed with a stated
residue: *"the advance's next real trial is a publish cycle under a tree that is
behind-and-not-ahead."* **Two such trials have now happened.** This is the answer to them, filed
separately because the pre-registration's own last line says no further re-read is owed — and it is
right.

---

## The two trials the pre-registration could not have

`docs/observability/sim-runner-log.md`, both under `ahead == 0`:

| when (UTC) | behind | advance verdict |
|---|---|---|
| 2026-09-04 23:21 | 9 | `git REFUSED the fast-forward (rc=1)` |
| 2026-09-04 23:50 | 10 | `git REFUSED the fast-forward (rc=1)` |

**`ahead == 0` is proven by the shape of the refusal, not read off the reflog.**
`_advance_to_origin_or_say_why` returns `"this tree holds N commit(s) of its own"` *before* it ever
reaches `git merge --ff-only`. A verdict that quotes git's `rc=1` is therefore a verdict from past
the ahead-check. Using the refusal's own branch as the instrument avoids the reflog's `+0100`
stamps, which is where a five-hour reading error lives.

Running total across the whole life of the mechanism: **9 advance attempts, 0 fires.**
`grep -c "Fork closed by fast-forward"` = **0**.

## What git named, in git's words

Both trials, identically:

```
error: Your local changes to the following files would be overwritten by merge:
	background/process_run_complete.py
error: The following untracked working tree files would be overwritten by merge:
	docs/staging/SEAT_FINDING_THE_DIRECTORS_ONLY_INBOUND_ROUTE_...md
	docs/staging/SEAT_FINDING_THE_RECONCILER_IS_NOT_STARVED_...md
	docs/staging/SEAT_FINDING_THE_STATUS_BOARD_PUBLISHED_A_WIPED_ROSTER_...md
```

At 01:12Z `paths_blocking_fast_forward()` returns **7**: one `FF_MODIFIED` and six `FF_UNTRACKED`.
All six untracked are **provably lossless** — `git hash-object` equals
`git rev-parse origin/main:<path>` exactly, checked one at a time:

```
7f1a97f51  SEAT_FINDING_THE_DIRECTORS_ONLY_INBOUND_ROUTE_...
64f2b11e8  SEAT_FINDING_THE_RECONCILER_IS_NOT_STARVED_...
659ce6877  SEAT_FINDING_THE_STATUS_BOARD_PUBLISHED_A_WIPED_ROSTER_...
c5399728e  SEAT_PREREGISTRATION_WHAT_THE_INBOUND_CHANNELS_...
95cdff7b5  SEAT_PREREGISTRATION_WHETHER_THE_RECONCILER_IS_STARVED_...
739511fe6  SEAT_PREREGISTRATION_WHETHER_THE_STATUS_BOARDS_LOST_ROSTER_...
```

**And removing all six buys nothing**, because the tracked path survives them. That is not a new
guess: the 22:39Z re-read established it by doing the removal and restoring it, and
`advance_shared_tree`'s docstring declines the removal for exactly this reason — *"a deletion bought
for no advance"*. **It is restated here so the next reader does not pay for it a third time.**

## The finding: it is not "the same dirty tree", it is the same FILE

`SEAT_FINDING_THE_MECHANICAL_ADVANCE_IS_BLOCKED_BY_THE_SAME_DIRTY_TREE_THAT_IS_ITS_REASON_FOR_EXISTING_2026-09-04.md`
named the class. Two more trials sharpen it by one word, and the word is load-bearing:

**The single tracked path that has refused every advance is `background/process_run_complete.py` —
the file the advance is defined in.** The lane repairing the advance holds the advance's own source
dirty, and that dirtiness is the whole refusal. Verified: worktree blob `d618e5969`, HEAD
`f99882281`, origin `a1de542ff` — three distinct blobs, so it is live third-lane work and nothing
here may move it. Its uncommitted hunks add a fail-closed provenance re-read at both commit sites,
with new tests staged (`A ` in the index) alongside — a lane mid-landing, not orphaned work.

**Why the sharper form matters.** "A dirty tree blocks the advance" reads as bad luck that any
lane's ordinary work could cause, and waits. "The advance's own source file blocks the advance"
names a loop that closes on itself and cannot drain by waiting: every improvement to the advance
lengthens the window in which the advance cannot run.

## The consequence that is live on the reader's surface right now

`git_commit_push` has been emitting **HEAD's** refusal text since 19:00Z. Origin changed that text
in `a1de542ff`:

```
HEAD    "Reconcile first: `python3 -m tools.surgical_land --merge origin/main`"
origin  "`python3 -m background.origin_reconcile`, which does the gated merge in an ISOLATED
         worktree. Do NOT run `surgical_land --merge origin/main` in the shared tree: it opens
         the shared index, and this refusal's own reason for existing is that routinely three
         lanes have uncommitted work in it"
```

The 23:50Z log line still carries the HEAD wording. **So the daemon is instructing every reader to
perform the exact act a landed repair explicitly forbids** — and it cannot stop, because PUSHED IS
NOT IMPORTED and the fast-forward that would import the corrected wording is refused by the same
file. The wrong advice and the thing that would fix it are blocked on each other.

This is the third leg and it is the one with a cost outside the mechanism: a reader who obeys opens
the shared index against three lanes' uncommitted work.

## Episode state, for the record

`.publish_gate_state.json` at 01:12Z: `episode_clean_publishes: 0`, `episode_failures: 3`,
`last_clean_publish: null`, `wedge_since: 1788548426` (19:00:26Z) — **frozen for 6h 12m**. Its most
recent recorded failure still reads `"this tree holds 1 commit(s) of its own"` and `"2 commit(s)
AHEAD"`; the tree now holds 0 of its own and is 11 behind. The artefact is a snapshot of a state
that has moved twice since.

## What I did NOT do, and why

- **Did not remove the six lossless twins.** Established above as bought-for-no-advance, twice paid
  for already.
- **Did not touch `background/process_run_complete.py`.** Live third-lane work with staged tests.
  `isolate_hunks` exists so a lane can land *its own* hunks without waiting; it is not a licence to
  land someone else's mid-flight change under my name.
- **Did not hand-close the 11-commit behind-ness.** Same reason the 22:39Z read gave: it destroys
  the only condition under which the advance can be observed, and `origin_reconcile` closes it
  unaided (41 real forks, measured 2026-09-04). `gate_is_running()` was `True` at 01:12Z, so it is
  standing down for the gate, not starved.
- **Did not make the REUSE repair** (`_advance_to_origin_or_say_why` calling
  `origin_reconcile.advance_shared_tree` instead of hand-rolling `merge --ff-only`). Two reasons,
  and the second is the disqualifying one: the contested file again, **and
  `advance_shared_tree`/`paths_blocking_fast_forward` do not exist at HEAD or on origin** — they are
  themselves uncommitted. A landed call to an uncommitted function is an ImportError on the publish
  path. *The pre-registration and the tick doorbell both cite these functions as though they were
  committed; they are working-tree-only, and that is worth knowing before anyone writes against
  them.*

## The correction this turn owes

The drawn item told me the ff was blocked *"by untracked staging twins in the shared tree, NOT by the
tracked tree"*. That was false when written and is false now — git named the tracked path first in
every refusal. I checked it against git rather than adopting it, which is the only reason this
finding exists. **A doorbell's stated preconditions are a hypothesis; the tree is the evidence.**

## What I DID clear, and the discriminator that made it safe

`finding_classes --check` was refusing at rc=1 on three TWO ROOMS pairs — unrelated to this finding
and blocking every landing in the tree:

```
SEAT_PREREGISTRATION_WHAT_THE_INBOUND_CHANNELS_THREE_UNASKED_CARRIERS_MUST_SHOW_2026-09-04.md
SEAT_PREREGISTRATION_WHETHER_THE_RECONCILER_IS_STARVED_OF_WINDOWS_..._2026-09-04.md
SEAT_PREREGISTRATION_WHETHER_THE_STATUS_BOARDS_LOST_ROSTER_..._2026-09-05.md
```

**Both rooms were untracked** — HEAD carries neither copy. That is the state where "which room is
canonical" cannot be answered from this tree at all, and **the discriminator is the remote**:
origin/main carries the ROOT copy of all three and no `records/` copy of any. So the `records/`
duplicates are an unlanded archive move, and root is where origin says these live.

Removal was proven lossless before it happened, not after: for each file
`git hash-object` on the root copy, on the `records/` copy, and `git rev-parse origin/main:<root>`
returned **one identical blob** — so the bytes survive in two other places, one of them the remote.
Each path was also checked with `git status --porcelain` for an `A`/`M`/`R` index entry first, so a
lane's staged move would have been skipped rather than swept. None was staged.

This is stable across the pending fast-forward — root becomes tracked, `records/` stays gone —
which is the test that matters, because *a gate that passes because you deleted one room is not a
gate that passed*. Removing the ROOT copies would have been the unstable choice: they would return
with the ff and the pair would re-form.

Gate after: `check: PASS (0 failures)`.

## What would close this

Not a new mechanism. The lane holding `background/process_run_complete.py` lands its hunks — its
tests are already written and staged. The advance then gets its first trial against a tree whose
only blockers are lossless twins, which is the state `advance_shared_tree`'s twin-clearing repair
was built for and has never once been handed. **Until then P1 stays refuted on a cause that is not
the advance's own logic, and no amount of work on the advance can change that.**
