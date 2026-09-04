**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The path that wedged the publisher was the file the lane repairing the publisher was holding

*Delivery seat, 2026-09-04, claim
`the-publish-refuses-at-the-commit-with-behind-origin-so-a-drained-queue-cannot-close-2026-09-04`.
Answers **P3** of
`SEAT_PREREGISTRATION_WHETHER_CLEARING_THE_PROVABLE_BLOCKERS_LETS_THE_SHARED_TREE_ADVANCE_2026-09-04.md`,
which predicted the untracked-twin class and found this one instead.
Finding class: `publish_gate_and_wedge`.*

## The observation, verbatim

`docs/observability/sim-runner-log.md`, 19:19 UTC and again at 19:49 UTC. The bullet reads:

> Liveness heartbeat is behind origin (origin/main is 1 commit(s) AHEAD of HEAD …). Advance attempt:
> **git REFUSED the fast-forward (rc=1), which is the guard working and not a fault:** error: Your
> local changes to the following files would be overwritten by merge:

and the next lines of the file, which `stderr_tail` returned with embedded newlines so they land
outside the bullet and outside every grep for the message, are:

```
	background/process_run_complete.py
Please commit your changes or stash them before you merge.
error: The following untracked working tree files would be overwritten by merge:
	docs/staging/SEAT_PREREGISTRATION_HOW_WIDE_THE_PUBLISHERS_LOST_RACE_WINDOW_ACTUALLY_IS_2026-09-04.md
Please move or remove them before you merge.
Aborting
```

**The path holding the publisher's fast-forward was `background/process_run_complete.py`** — the
publisher's own source, held dirty in the shared tree by the concurrent lane that is adding the
advance to `_commit_and_push_paths`. A lane repairing the publish path wedged the publish path by
holding its file uncommitted while it worked.

## Why this is a class and not an unlucky afternoon

`origin_reconcile.advance_shared_tree` (staged, uncommitted, 2026-09-04) clears blockers, and its
central safety property is correct and worth keeping:

> *"ALL-OR-NOTHING … Nothing is removed unless removing the twins would leave the fast-forward with
> nothing else to refuse on."*

It clears `FF_UNTRACKED` twins whose bytes origin already holds. It refuses `FF_MODIFIED` — a
lane's real work — and it must, because deciding to discard someone's uncommitted edit is exactly
the judgement that does not belong on a cadence. **So the tracked-file case has no automated
remedy by design, and it takes exactly one of them to hold the tree.** A fast-forward is
conjunctive; nine clearable blockers and one unclearable one advance nothing.

The surface is not marginal. Measured on the shared tree at 22:15 UTC:

| quantity | value |
|---|---|
| tracked files modified in the shared tree | **189** |
| of those, also changed by origin in its last 30 commits | **49** |
| blockers needed to hold the tree | **1** |

Every one of those 49 is a path where "a lane is holding it" and "origin changed it" are both true
right now. `background/process_run_complete.py` is on that list today, and it is the file the
publish path, the liveness heartbeat and the red-cycle banner all live in.

## What it cost, in the currency the mission cares about

* **19:19, 19:49** — liveness heartbeat refused. These are the two surfaces whose entire job is to
  tell the reader the system is alive *when content is not publishing*, silenced in the one state
  they exist for.
* **20:46** — a full simulation and a 672s scoped gate, both green, discarded at the commit step.
  `.publish_gate_state.json` still reads `episode_failures 2`, `episode_clean_publishes 0`,
  `last_clean_publish null`, `wedge_since 19:00:26Z`.

## Two things the record does wrong, and they compound

**1. "which is the guard working and not a fault" is asserted about a state that was never
examined.** `_advance_to_origin_or_say_why` returns one reason for every non-zero `--ff-only` rc.
The docstring's guard argument is sound *as a safety claim* — git will not clobber a lane's edit —
but the reason string converts it into a verdict that there is nothing here to act on. At 19:19 one
of the two holders was an untracked staging note with no owner and no work at stake, of precisely
the kind `identical_untracked_twins` was built an hour later to prove harmless. A refusal that
declares itself not-a-fault is a refusal nobody re-reads.

**2. The paths reached the log and left the record.** `stderr_tail` joins with `\n`; `log()` writes
one `- [ts] [process_run] …` bullet. Every line after the first is orphaned — present in the file,
attached to nothing, invisible to any grep keyed to the message. And the machine-readable side is
worse: at HEAD only `git_commit_push` writes `.publish_gate_state.json`, so these two heartbeat
refusals recorded `cause: behind_origin` with no path anywhere. **Three separate seats have now
re-derived the blocking paths by hand**; this is the fourth.

## The recommendation, and what I deliberately did NOT do

**Do not add a third implementation of the blocker classifier.** `paths_blocking_fast_forward()`
and `_blocking_clause()` are landing in `origin_reconcile` within the hour and they are correct.
The publish path should **call** them rather than grow its own — the rule this project has paid for
repeatedly, most recently as *"a new branch beside an old one must call what the sibling calls, not
copy what it looks like."*

Two changes are wanted at `background/process_run_complete.py`, and **neither was made this turn**:

1. `_advance_to_origin_or_say_why` stops asserting "not a fault" for a dirty-tree collision, and
   renders `origin_reconcile._blocking_clause(paths_blocking_fast_forward())` in the reason.
2. The heartbeat and banner refusals record their cause with the same fidelity `git_commit_push`
   does, so an `FF_MODIFIED` wedge is distinguishable from a hot origin in the state file rather
   than only in an orphaned log line.

**Why not this turn, and this is the finding eating its own tail: `background/process_run_complete.py`
is one of the 189.** Landing a commit that touches it, while the sibling lane holds it dirty, makes
it an `FF_MODIFIED` blocker on the shared tree — manufacturing the exact wedge this document
reports, on the exact file it reports it about. `tools/isolate_hunks.py` solves the *authorship*
collision (my bytes without theirs) and does nothing about this one, because the hazard is not in
the commit's content, it is in the shared tree's working copy afterwards. The honest sequence is:
the sibling lane lands, `process_run_complete.py` goes clean, and then these two changes go in on
top of a tree that can actually receive them.

**So the queued remedy is ordered behind another lane's landing, and the ordering is the finding.**

## The property a control should key to, when there is code to key it against

Not "the blocking set is empty" — that is today's answer and it will be green for the wrong reason
the moment the tree happens to be clean. The property is: **a refusal to advance must name whether
it examined the holders, and must not report a cause it did not establish.** `advance_shared_tree`
already keeps `None` ("I could not look") distinct from `[]` ("nothing collides") all the way up;
the publish path collapses both into "the guard working and not a fault", and that collapse is the
defect.

## Interconnection, which is why this sits with the seat and not with either lane

Three repairs landed or are landing today, and each is right on its own:

* `ab6240611` + `918bab352` — the publisher advances instead of discarding a cycle.
* `826f82a93` — the orienting seat pushes, so its commit stops disabling that advance.
* `origin_reconcile.advance_shared_tree` (in flight) — untracked twins cleared, all-or-nothing.

Together they close the `ahead > 0` door and the `FF_UNTRACKED` door and leave the `FF_MODIFIED`
door open — and `FF_MODIFIED` is manufactured continuously by this project's own working practice of
several lanes editing one shared tree. **Neither lane can see this from inside its own file.** The
first two make the third one load-bearing, and the third one's correct refusal is what turns
ordinary concurrent editing into a publishing outage.
