**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** publish_gate_and_wedge

# RESULT: the publish gate's own suite was red on one incidental live write, and the seventeenth failure was the extract itself

Delivery seat, 2026-09-17. Claim
`the-publish-gates-own-tests-are-red-at-head-and-the-finished-repair-is-unlanded`.
Pre-registration: `docs/staging/records/SEAT_PREREGISTRATION_THE_PUBLISH_GATES_OWN_SUITE_IS_RED_ON_ONE_INCIDENTAL_LIVE_WRITE_2026-09-17.md`,
written before the edit. **Landed: `159a2d4fc` (the repair), `1258b89b8` (the room move).**

## The predictions, graded

| | Prediction | Outcome |
|---|---|---|
| **P1** | One line in `_LEAKING_STATE_CONSTANTS` turns all 14 green | **HELD.** 78 passed, 0 failed across the five files plus the marker's own test |
| **P2** | It costs ZERO other controls | **HELD, and measured by one-variable swap** — see below |
| **P3** | `test_the_liveness_heartbeat_took_the_tree_from_the_content_publish.py` stays wholly green, including the lexical `with`-block control | **HELD** |
| **P4** | The guard is still CALLED on every path; only the destination moves | **HELD.** `_reroot` preserves the repo-relative path, so the write lands at `tmp_path/docs/observability/...`, outside `LIVE_RECORD_DIR`, and `guard_live_ledger_write` returns it unchanged |

**P2 was measured, not asserted, because it is the leg that could have cost 43 controls.** A full
`tests/background/` run gave `16 failed, 5582 passed` — so I removed my one tuple entry and re-ran
the eight files carrying those 16: **identical, 16 failed, 191 passed, both with and without the
line.** The change causes none of them. (The first full run was additionally contaminated — I ran
`surgical_land` in the same worktree while it was going, moving HEAD mid-run — so it was re-measured
on a stable tree before the swap. It reproduced identically, so the contamination changed nothing,
but the first measurement was not one I could have attributed.)

## The item's "17 failures, one cause" was two numbers, and both were slightly wrong

Not a criticism of the item — a reconciliation, because the discrepancy is informative.

    git archive f0af86639 (parent)   -> 17 failed, 53 passed
    git archive 1258b89b8 (HEAD)     ->  3 failed, 67 passed
    real checkout 1258b89b8          ->  0 failed, 78 passed

**The item and `delivery.json` both say "17 failed, 53 passed, one cause". The 17 is right and the
one cause is not.** 14 were the ledger guard. The other **3 are the extract**: `git archive`
produces no `.git`, so `test_published_provenance_is_real.py`'s three live-state tests fail with
`meta.git_commit names no commit in this repo: '770497ddd'` — they cannot pass in a bare extract at
ANY commit, before or after this repair, because the thing they check requires a repository. My own
14-vs-17 confusion had the same root: I measured in a worktree, the item measured in an extract.

**The lesson is the measuring instrument, not the code.** "Green in a clean `git archive` extract"
is the project's standard bar and it is the right one for most things, but it silently fails every
control whose subject is the repository itself. A done-condition written as "green in a clean
extract" cannot be met by this file and never could be.

## The cause, and why the obvious repair was refused

`c9c4339b8` correctly closed the publish/heartbeat race with `_landing_in_flight_marker`, writing
`docs/observability/.publish_landing_in_flight.json` — a path `is_live_record_path` returns True
for. Every test driving the publish path end-to-end reached it incidentally.

**The carve-out was available and is wrong.** A landing marker is not a measurement ledger, so
narrowing `is_live_record_path` looks arguable. But a marker written by a test makes
`_landing_in_flight()` answer "live" to the real heartbeat and suppresses the liveness publish for a
full throttle interval — Fault #1 (2026-07-25) re-manufactured through a new door. The guard is
right; the destination moves.

The mechanism was already parked: `_LEAKING_STATE_CONSTANTS`, whose docstring defines its population
as constants written as an incidental side-effect where *"the live file is nobody's subject"*, and
closes *"a new leak is one line plus a re-run of this directory"*. Its admission test — **is the live
artefact any control's subject?** — was answered by grep, not assumption: one module, one test, and
that test already re-roots the same constant in its own body.

## The defect I committed while fixing one

`159a2d4fc` put the pre-registration in the TRACKED staging root.
`finding_classes.self_refuelling_root_documents` refused — correctly — and its docstring names the
history: `4a4ac598b` untracked the one instance in front of it, and *"fifty-six minutes later
`197261a2d` committed a NEW preregistration into the tracked root and the identical wedge came
back, because the fix was to an instance and the class had no control."* **I am the third
instance, and I hit it one hour after the class control was written.** `1258b89b8` moves both
root-tracked preregistrations to `records/` — mine and the weather one the same control names —
because fixing only mine leaves the tree wedged on a file I had just proven I could see.

Worth recording plainly: the class control worked. It caught its own author's successor within the
hour, which is what a class fix is supposed to do and what the two instance fixes before it could
not.

## What is NOT done, and it is the item's second half

`.publish_gate_state.json` still reads `last_clean_publish: None`, `wedge_since` unchanged, and
`blocking_tests` now lists **12** — every one of them from the set this commit repairs. That state
is STALE, written before the fix landed; it clears only when a publisher cycle re-grades it. **I
predicted I could not force that inside one turn and I could not.** The figure must be graded by the
publisher on a real cycle, never typed in.

The shared tree at `/home/rich/synthetic-enterprise` was checked for the inert-daemon shape (a
landed repair the daemon cannot see because it imports the WORKING tree): its working copy carries
the line at `tests/background/conftest.py:71` and `origin/main` has the commit, so the fix is live
there, not inert. Its HEAD is a local sibling commit that has not yet reconciled — ordinary, and
nothing to repair.

**The second fault the item warned about is untouched and expected to survive**, exactly as
pre-registered: the last `liveness_surface_refusal` ends `fatal: cannot lock ref 'HEAD': is at
aff4b153f but expected 56d746816` — the publisher losing the HEAD ref lock to another lane
mid-commit. If the gate does not go green after a cycle, that is the reason and it is not evidence
this repair failed.

`delivery.json`'s `corrected: false` row is on the append-only decisions record and is superseded by
a later orientation rather than rewritten — deliberately not edited here.

## Leg (b) of the drawn item was SPENT

The item asked for 207 uncommitted insertions to be landed via `isolate_hunks` and the finding
archived. `9c4ce323f` had already landed the reachability verdict and the finding was already in
`docs/staging/done/`. This worktree was clean at `f0af86639`, so `isolate_hunks` had no subject. The
premise check's warning was correct for leg (b) and I did not do it twice.
