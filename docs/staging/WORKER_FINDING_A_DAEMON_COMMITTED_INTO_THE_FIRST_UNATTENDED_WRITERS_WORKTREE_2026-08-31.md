**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS1_process_manifest_reconstruction`

# A worktree is isolated from other WRITERS, not from other DAEMONS — and the promotion route was verifying the tip, not the range

**Found:** 2026-08-31, four minutes into the seat executor's first unattended turn. Not by a
control; by looking at what the tick was doing.

## What happened, with timestamps

| time (BST) | event |
|---|---|
| 18:12 | `seat-executor.service` starts its first turn: `RUNNING union-the-departure-routes… in /var/tmp/se-seat-executor on 2f45c3b9c` |
| 18:16 | `background/fork_salvage.py` commits **inside that worktree**: `SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-31T17:16:42Z` |

The salvage commit's content was two observability files (`.human_last_input`,
`.seat_heartbeat.json`) and is harmless in itself. The shape is not.

## Two defects, and the second is the one that mattered

### 0. It happened AGAIN, ninety minutes later, to the fix's own landing worktree

At 19:11 `fork_salvage` committed `8d980bb62 SALVAGE(auto)` into `/var/tmp/se-seat-lane0` — the
worktree in which this very finding and its fix were being prepared, mid-preparation.

**The first version of the fix did not cover it, and the reason is the finding underneath the
finding.** `worktree_is_live` compared the path against `seat_executor.WORKTREE` and nothing else,
so it exempted the executor and left every other writer exposed. **That is the wrong subject.** The
property is *a live writer*, not *this module's path* — and I wrote the narrow version while looking
at the module that had been hit, which is precisely how a class fix becomes an instance fix wearing
a class's clothes.

Any writer can now declare a worktree in use by dropping `seat_executor.OWNER_MARKER` with its pid
in it; the executor writes one every turn, and a session working in a worktree by hand can write one
too. A leg drives it from a path that is *not* the executor's, so the narrow version cannot come
back green.

Recovery was a `git reset --mixed` back to the gated tip: nothing was lost, and the work landed
through the door.

### 1. Salvage treated a LIVE writer's worktree as an abandoned fork

`fork_salvage.scan_worktrees()` returns every worktree that is not `main` and not on a protected
branch. It has no notion of a worktree somebody is *currently working in* — reasonably, because
until today no worktree on this machine had a resident writer. The seat executor is the first, and
it was armed this afternoon.

So the daemon built to rescue what a dead fork left behind became **a second writer inside the one
place isolation was supposed to guarantee there is only ever one**. The executor's entire licence to
exist is "it is not a second writer on the shared tree"; nobody had asked the mirror question.

### 2. `promote_worktree_landing` verified the TIP, not the RANGE

This is the sharp one, and it is my own defect from this morning.

`_refuse_if_ungated` ran `surgical_land --verify` against `HEAD`. Its docstring calls that check
*"the load-bearing one … it makes 'only gated commits reach main' a property of the route rather
than of the caller's discipline."* **A push moves a ref, so the subject is `origin/main..HEAD` and
never the tip alone.**

**AND IT WAS NOT AVERTED — the first live run walked straight through it while I was writing the
fix.** The executor landed `b8e6ba32d` on top of the salvage commit at 18:37, promoted, and pushed.
`origin/main` now reads:

```
b8e6ba32d the two departure routes now share one denominator…   <- gated, receipt verifies
139332d90 SALVAGE(auto): preserve this fork's uncommitted work   <- UNGATED, on main
```

The executor ran its worktree's copy of the route, which was the tip-only version; my fix was
uncommitted in the shared tree. So this is evidence rather than a hypothetical: **an ungated commit
reached `main` through the route whose entire purpose is to prevent that**, on the route's first
unattended use. Its content is two observability files and nothing needs reverting; the record
should say it is there and why.

The route's whole claim is about what reaches `main`, and it was checking one commit of a set.

## Fixed, both halves

* **`tools/promote_worktree_landing._refuse_if_ungated`** now verifies every commit in
  `origin/main..HEAD`, oldest first, and names which one failed and whether it was the landing or
  something beneath it. This is the robust half: it is correct whoever else writes.
  `tests/tools/test_the_promotion_route_refuses.py` gains the ungated-beneath-a-gated-tip leg and
  a blast-radius leg holding that an honest multi-commit landing still promotes — landing an
  increment and landing again is behaviour the executor's own charter asks for.
* **`background/fork_salvage._is_a_live_writers_worktree`** skips the executor's worktree while its
  pid is alive. A **liveness check, not the pid file's existence**: a killed executor leaves its
  file behind, and *that* worktree holds exactly the abandoned work this daemon exists to rescue —
  the 2026-08-03 sweeps found new modules that existed nowhere else. Nothing is lost by skipping a
  live one: `ensure_worktree` resets to `origin/main` every turn, so anything unlanded was by
  design unfinished.

**One mutation survived first and it is worth recording.** Deleting the filter from
`scan_worktrees` left all three of my new legs green — they tested the predicate and not its caller.
A predicate nothing consults is a comment with a test attached. The fourth leg drives the scan.

## What this says beyond the two fixes

**"Isolated" was doing more work in my head than in the machine.** A `git worktree` isolates a
writer from other writers' *uncommitted* state. It does not isolate it from a dozen daemons on the
same box that enumerate worktrees and act on them — `fork_salvage`, `fork_reconciler`,
`tree_divergence`, the orphan-worktree alarm. The first unattended writer is a new kind of subject
for all of them, and only one has been checked.

## The census, run rather than filed — and it found a worse one

Four modules enumerate worktrees and act on them. Asked of each:

| module | what it can do | verdict |
|---|---|---|
| `background/fork_salvage` | commit into a worktree | **collided (above), fixed** |
| `background/fork_reconciler` | **`git worktree remove`** | **would have destroyed it, fixed** |
| `background/disk_headroom` | commit | reads sizes; does not act on a foreign worktree |
| `background/process_run_complete` | commit, `git clean` | operates on its own publish checkout |

**`fork_reconciler`'s worktree reaper is ARMED** (`worktree_reap_enabled()` returns True) and had
not destroyed the executor's worktree only by luck. It refuses a DIRTY worktree, and the executor is
dirty for most of a turn — but `ensure_worktree` resets and cleans that tree at the **start of every
turn**, so there is a window in which it is clean and detached at `origin/main`: MERGED, and by the
classifier's own rules **eligible**. `git worktree remove` on a live writer is the whole turn gone,
and there would have been nothing left to say what happened.

Both reap doors now refuse a live writer — the sweep and `reap_one_worktree`, the one an operator
calls by hand — because a rule enforced at one door and not the other is a rule with a way round it,
which this same file already holds as a principle for detached-HEAD determination.

**The liveness question has ONE home.** `seat_executor.worktree_is_live` owns it, because
`seat_executor` owns `WORKTREE` and `PID_FILE`; `fork_salvage` and `fork_reconciler` both ask it.
Two modules that do not import each other each carrying their own liveness rule is the ontology
defect this project has been paying for all month, and a leg asserts both daemons delegate rather
than answer.

**And it is liveness that spares the tree, never the path.** A killed executor leaves its pid file
and its worktree behind, and that directory is exactly the accretion the reaper exists to remove —
the H24 gap was worktree dirs climbing 2 → 7 in one session. A path exemption would trade one
collision for unbounded accretion; both fixes therefore probe `/proc`, and a leg holds that the same
worktree becomes eligible the moment its writer exits.

## A fourth thing, and it would have taught the writer to distrust its own suite

**The test suite was not runnable in a worktree.** Measured on an unmodified `origin/main` checkout:
running `tests/background/` in a linked worktree produces **31 errors across nine modules** that are
green in the main repo. Every one of them is `GHOST PUSHER (unattributable)` from
`tests/background/conftest.py`'s anti-commit tripwire.

One line causes it. `_real_repo_head()` reads `.git/HEAD` from disk when `.git` is a directory, and
**shells out to `git rev-parse HEAD` when `.git` is a file** — which is exactly the worktree case.
Every test that stubs `subprocess.run` (all 31 of them, before touching the publish path) answers
that call with a Mock, the read comes back empty, HEAD appears to move from a real sha to
`"unreadable"`, and the tripwire fails closed.

**The identical trap was already known and fixed one branch over.** The no-`.git` case has a
six-line comment explaining that a subprocess fallback *"collided with every test that stubs
`subprocess.run`… 9 errors that exist only in the archive, never in the repo"* — and the worktree
branch, four lines below it, was left shelling out. Nobody saw it because everybody worked in the
main tree.

**It matters now because the first unattended writer lives in a worktree and gates its landings
there.** Thirty-one ghost failures would send it chasing nothing, or — much worse — teach it that
reds in its own tree are normal. That is the opposite of what an unattended writer must believe.

Fixed by reading a linked worktree's HEAD from disk: `.git` is `gitdir: <path>`, that directory
holds this worktree's own HEAD, and refs resolve against the COMMON dir two levels up — the same
`--git-common-dir` distinction `tools/surgical_land._object_store` turns on. No subprocess, so no
stub can poison it. `tests/background/test_worktree_isolation.py` gains two legs: the reader
survives a stubbed subprocess, and it agrees with `git rev-parse` in both layouts.
