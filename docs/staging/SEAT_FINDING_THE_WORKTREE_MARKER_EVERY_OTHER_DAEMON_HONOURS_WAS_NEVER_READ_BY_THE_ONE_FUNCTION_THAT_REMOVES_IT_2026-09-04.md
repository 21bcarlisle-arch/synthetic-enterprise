**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# The worktree marker every other daemon honours was never read by the one function that removes it

**Found by doing the drawn work, not by reading for it.** The Lane 0 item was *"close the live
fork"*; closing it the sanctioned way is what produced the collision, on real disk, in three
minutes.

---

## What happened, measured

`background/origin_reconcile` closes the fork with origin by merging in a throwaway worktree at one
fixed path — `WORKTREE = /var/tmp/se-origin-reconcile`. It runs on the deadman's five-minute
cadence, and `MERGE_TIMEOUT_SECONDS = 25 * 60`, so a merge may legitimately occupy that path for
twenty-five minutes.

At **2026-09-04 23:39Z** the shared tree was 1 ahead / 9 behind and the deadman's reconcile was
~40 seconds into `surgical_land --merge origin/main` in that worktree. This seat then ran
`python3 -m background.origin_reconcile`. Measured from `ps` at 23:40Z:

```
3923979  ppid 3659340 (deadmans_switch.py)   python3 -m tools.surgical_land --merge origin/main   101s
3930845  ppid 3930824 (origin_reconcile)     python3 -m tools.surgical_land --merge origin/main    26s
```

Two `surgical_land --merge` processes, one directory. The second one's `_fresh_worktree` had
already run `git worktree remove --force` and `git worktree add` on the first one's cwd. Measured
three minutes later, after the second was killed:

```
/var/tmp/se-origin-reconcile/.se_worktree_owner  →  3930824   (dead: the killed second reconciler)
pid 3923979 (the deadman's merge)                →  still running, 322s elapsed
```

The live writer's checkout was rebuilt underneath it, and the marker in that directory now names a
process that no longer exists.

## Why the isolation argument did not cover it

The module's docstring argues its safety at length and every clause is true — of the **shared
tree**. It never opens the shared index; `gate_is_running` stands it down for the publish gate;
`_run_merge` inherits `surgical_land`'s conflict refusal. Not one of those is about *another
reconciler*, and there is no lock:

* one fixed path for every invocation, from a module-level constant;
* no `tree_lock`, deliberately and correctly — the merge is isolated, so it does not need one;
* `gate_is_running()` answers about the publish gate's run lock, never about this module.

**And it is reachable by following the machine's own printed instruction.**
`process_run_complete._divergence_refusal` tells every reader of a publish refusal, verbatim:
*"Reconcile first: `python3 -m background.origin_reconcile`"*. A seat that reads a refusal and does
what it says is the collision. That is not a hand-working accident to be more careful about next
time; it is the documented route.

## The control that was there, and why it was green throughout

`_fresh_worktree` writes an owner marker one line after the remove, and its own comment states the
purpose exactly: *"`fork_reconciler`'s reaper is armed ... `fork_salvage` sweeps dirty worktrees; a
merge in progress is exactly the state both are built to clean up after. The marker is the one
sanctioned way to say 'a writer is here'."*

Both of those daemons honour it, through `seat_executor.worktree_is_live` — which is documented as
*"THE ONE HOME FOR THE QUESTION ... because two daemons outside this module have to ask it"*, and
lists exactly two askers. **The function that owns the only path either of them would sweep was not
one of them.** It wrote the claim and never read one.

The control over that was `tests/background/test_a_staged_document_no_longer_blocks_every_landing.py
::test_the_worktree_is_declared_in_use_while_the_merge_runs`:

```python
src = inspect.getsource(orc._fresh_worktree)
assert "OWNER_MARKER" in src and OWNER_MARKER
```

That assertion is true of a function that WRITES a marker and never reads one, so it was green for
the entire life of the defect. **A source-text control cannot tell "declares a claim" from "honours
a claim", and those are opposite halves of the same mechanism.** The generalisation is the one this
project keeps paying for from a new direction: a claim is only a claim if somebody checks it, and
the check has to be over behaviour.

## The repair, landed with this finding

`_fresh_worktree` asks `seat_executor.worktree_is_live(path)` before the force-remove, and refuses
with a named reason if a writer is there. `reconcile` already renders that as `ERROR` with the
reason attached, so the deadman's log line carries the cause.

**A refusal and never a wait.** Blocking would hold the cadence up to `MERGE_TIMEOUT_SECONDS`, and
a reconciler stuck waiting is one that is not there when its own window opens. The deadman returns
in five minutes.

**It cannot wedge on a crash**, which is the failure mode a naive "is the file there" guard would
have. `worktree_is_live` is two leased legs: a marker whose pid must be ALIVE and whose claim must
be younger than `OWNER_LEASE_SECONDS`, or an explicit `git worktree lock`. A killed reconciler
leaves a dead pid, which fails leg 1, and the next cadence rebuilds normally. The live state
observed above — a dead pid in the marker — is exactly the state that must *not* refuse, and does
not.

Control:
`tests/background/test_a_second_reconciler_does_not_rebuild_the_worktree_under_a_running_merge.py`,
three tests, **four mutations fired**:

| mutation | what went red |
|---|---|
| delete the `worktree_is_live` call | the LIVE leg — the remove happens again |
| `return False` unconditionally | the DEAD leg — no worktree is ever built, so no fork ever closes |
| drop `why` from `reconcile`'s ERROR detail | the refusal stops reaching a reader |
| drop the worktree in the refusal branch | the stand-down tears down the writer's checkout anyway |

The first two are **one test over the whole partition**, not a leg each — a guard that refuses
everything passes every "does it refuse correctly" assertion ever written, and here that guard
would mean no fork is ever closed again.

## What this does NOT fix, stated so it is not read as more than it is

* **It does not close tonight's fork.** The shared tree was 1 ahead / 9 behind when this was
  written, and the deadman's merge — the one that survived — is what closes it. This stops the next
  seat from breaking that merge; it does not perform it.
* **It does not clear the fast-forward blocker.** `paths_blocking_fast_forward()` returns 7 paths:
  six untracked staging twins, all verified byte-identical to what origin brings
  (`git hash-object` == `git rev-parse origin/main:<path>`), and one tracked file,
  `background/process_run_complete.py`, which a third lane holds dirty (worktree `d618e5969`, HEAD
  and index `f99882281`, origin `a1de542ff`). `advance_shared_tree` is right to leave all seven
  alone: clearing six of seven is *"a deletion bought for no advance"*. That is the subject of
  `SEAT_FINDING_THE_MECHANICAL_ADVANCE_IS_BLOCKED_BY_THE_SAME_DIRTY_TREE_THAT_IS_ITS_REASON_FOR_EXISTING_2026-09-04.md`
  and is not touched here.
* **It does not make the two reconcilers cooperate.** The second one stands down and says so. If
  the answer should instead be "wait for the window", that is a different design and it needs a
  measurement of how often the collision happens, which does not exist.

## The correction I owe, beside the claim rather than over it

I caused this. The drawn work said *"close the live fork ... `origin_reconcile`'s ... `gate_is_running`
was False at 20:50Z so it has a window"*, and I read that as an invitation to run the reconciler by
hand. I checked `gate_is_running()` — False — and did not check whether **a reconciler** was
already running, because the module's own stand-down list does not contain that question and I took
the list for the partition.

The evidence was one `ps` away and I ran `ps` only afterwards, to find out what I had hit. **A
stand-down list is not a partition of the ways a thing can already be in progress**, and I graded
the guard by reading what it refuses rather than by asking what it does not look at. Kept here
because the defect and the way I found it are the same shape, and the second half is the part that
would have been lost in a tidier write-up.

---

*Discharged in the commit that carries it: the guard, the control, and the four mutations above.*
