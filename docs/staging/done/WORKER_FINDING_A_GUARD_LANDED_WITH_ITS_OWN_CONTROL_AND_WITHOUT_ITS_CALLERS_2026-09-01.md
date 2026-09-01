**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS1_process_manifest_reconstruction`

# A guard landed with its own control and without its callers' — one new read wedged the publish gate for 80 minutes, and the census cap hid 14 of the 26 reds

**Found:** 2026-09-01, working the PUBLISH-GATE WEDGE self-refill at HEAD `b58b6cedc`.
Not by a control — the controls are what went red. By asking what all 26 had in common.

## What happened

`ea5e66c60` added a divergence read to the publish path: `git_commit_push` now calls
`_divergence_refusal()` before it stages anything, so the loop cannot widen a fork it is already
blocked by. The guard is right, it is fail-closed, and it shipped **with a real-git control of its
own** (`test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py`, 10 tests, green
throughout the wedge).

What it did not ship with is any change to the tests of the **five callers it was inserted in
front of**. Every one of those drives `git_commit_push` (or `_publish_provenance_banner`) through
a `subprocess.run` stub that answers `rc=0` with **empty stdout**. `_commits_origin_is_ahead_by`
reads an empty `rev-list --count` as `None` — correctly, and deliberately: *"missing reads as zero
is the fail-open shape that would let this guard pass in precisely the conditions under which a
commit is least likely to reach origin."* `None` means UNREADABLE, UNREADABLE refuses, and the
refusal returns before the subject of every one of those tests.

So a guard whose own control was green took 26 tests red and blocked all publishing for 80 minutes
across 4 consecutive publish cycles.

**The general shape: a new early return is a change to every test of every caller downstream of
it, and the guard's own control cannot see that.** It passes precisely because it is the one test
that sets the guard's input deliberately.

## The one that was a real defect, not a fixture gap

Four of the five were fixture gaps. One was not.

`_provenance_is_publishable` refuses a false stamp and records this evidence:

> the fail-closed provenance check refused the stamp for git=… **before any git command ran** —
> nothing was staged, no hook chain started and no push was attempted

That sentence became false the moment the divergence read was placed above it: `git fetch` and
`git rev-list` had both already run. `test_the_green_cycle_publish_refuses_a_false_provenance`
asserted exactly this (`assert not calls`) and was one of the 26 — **the control was right and the
code was wrong**, which is the opposite of how the other 25 read.

Repaired by ordering, not by weakening the assertion: the provenance check now runs first. Two
fail-closed refusals in a row cannot mask each other into publishing, so the order is free to be
chosen — and the cheap LOCAL check belongs in front of the one that opens a network round trip
with a 60-second timeout to answer a question we no longer need asked.

## The census named 12 of 26 and nothing said which 14 were missing

`.last_gate_blocking_tests.json` recorded `total_red: 26` beside 12 node ids. That is the citation
cap working as designed (`total_red` is deliberately the size **before** the cap, so a reader can
tell a cap fired) — but the other 14 are written down nowhere, and
`docs/observability/publish_gate_red_census.json` on disk was three weeks stale (2026-08-11,
`b905f467`), so it looked like a census and was not one.

Re-running the gate's own `red_census_argv` was the only way to see the set. It cost 9m37s and
found the 26 were **one cause**, which is the fact that made this a single tick's work instead of
the 252-cycle shape of 2026-08-14. **A count without its members cannot be triaged as a class**,
and a stale artefact with the right filename is worse than an absent one.

## Also disposed in this tick

`WORKER_FINDING_TWO_TEST_FILES_IN_THE_WORKING_TREE_SILENTLY_REVERT_REPAIRS_ALREADY_ON_ORIGIN`
was still live and undisposed. Both files were verified strictly older than `origin/main`
(`test_fork_salvage.py`: origin is a strict superset, −40 lines; `test_tree_divergence.py`: the
worktree copy reverts the `tmp_path` repair) and restored from `origin/main`. Both now byte-identical
to the trunk; 51 tests green.

The `test_tree_divergence.py` revert was the active one — it re-points `write_artifact` at the
**live** `docs/observability/tree_divergence.json`, so every suite run from the working tree
overwrites the real divergence measurement. The census run in this tick would have done exactly
that. It is why `docs/observability` became a protected surface.

## What would have caught it

Nothing in this repository, and I do not think a new control is the answer — a register that
watches for "new early return in a function with N callers" is the file-made-of-rules shape.

What actually worked was **running the gate's own census argv and reading the whole set before
repairing any member of it**. That is already the drawn procedure for a wedge; the failure mode it
guards against is repairing the named red, re-running, and handing the next layer to the next tick.
This tick is evidence the procedure pays: 26 reds, one cause, one tick.

The narrower lesson worth keeping: **a fail-closed guard's own control is the one test that cannot
detect the guard's blast radius**, because it is the only one that sets the guard's input on
purpose. Blast radius is measured in the callers' tests, never in the guard's.
