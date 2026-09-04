**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING — the seat that orients commits without pushing, and that one commit disables the publisher's mechanical advance

**Filed:** 2026-09-04, delivery seat (isolated worktree). **Repaired in the same commit.**

**Discharged:** `tests/background/test_delivery_seat.py::test_every_push_verdict_is_REACHABLE_and_they_say_DIFFERENT_things`,
`tests/background/test_delivery_seat.py::test_a_PHANTOM_rc0_that_left_the_commit_LOCAL_is_not_reported_as_pushed`,
`tests/background/test_delivery_seat.py::test_a_REJECTED_push_is_attempted_ONCE_and_never_retried`,
`tests/background/test_delivery_seat.py::test_a_push_that_could_not_RUN_loses_neither_the_record_nor_the_reason`,
`tests/background/test_delivery_seat.py::test_the_direction_commit_is_PUSHED_and_the_row_still_reports_the_COMMIT`

LATENT rather than BLOCKING: nothing published is wrong because of this, and the repair landed
today (`ab6240611`) is not wrong either. What it did was make a correct repair unable to fire, by
manufacturing — from a different lane entirely — the exact state that repair correctly refuses.

---

## The observation

`background/delivery_seat.commit_direction` has always ended at the commit:

```python
commit = subprocess.run(["git", "commit", "-m", "delivery seat: direction ...", "--", *present], ...)
return commit.returncode == 0, f"commit rc={commit.returncode}"
```

Nothing pushes it. That is not an inference — `origin_reconcile.commits_ahead`'s own docstring
says so in as many words: *"Nothing else pushes a `surgical_land` landing. The publish path pushes
its OWN commits and carries whatever else is on the branch, so a landing reaches origin only when
a publish happens to follow it."* The direction commit is not even a `surgical_land` landing; it
is a plain commit with nothing at all responsible for sending it.

So every orientation that changes direction leaves the shared tree one commit AHEAD of origin,
indefinitely. Observed live, 2026-09-04 20:36Z:

```
git rev-list --count origin/main..HEAD  = 1   →  b096b2389 "delivery seat: direction for the next stretch"
git rev-list --count HEAD..origin/main  = 3
```

## Why that one commit matters more than it looks

`ab6240611` landed the publisher's mechanical advance at 18:56Z: when the publish path finds
itself behind origin, fast-forward and re-read rather than throw away a 672s cycle at the door.
It refuses, correctly, when this machine holds commits of its own — that fork is real and needs
the gated merge door.

`docs/observability/sim-runner-log.md`, 2026-09-04 19:59Z, verbatim:

> Liveness heartbeat is behind origin (...). Advance attempt: **this tree holds 1 commit(s) of its
> own, so the fork is REAL and closing it is a judgement**: it needs the gated merge door
> (`python3 -m tools.surgical_land --merge origin/main`), which is longer than a publish cycle.
> Left to origin_reconcile on the deadman cadence, which is where it belongs

Every word of that is right. The `1` in it was written by this seat, and it was never going
anywhere. And the case it hands off — `origin_reconcile` — stands down while a gate is running,
which is most of the time on a 672s cycle. That is
`SEAT_FINDING_THE_RECONCILER_AND_THE_PUBLISHER_EACH_STAND_DOWN_FOR_THE_OTHER...` again, with a
third party quietly refuelling it.

**The shape worth carrying:** two mechanisms that each correctly stand down for the other were
being fed the deadlock condition by a component that is not part of the argument at all, and
nothing in either of their diagnostics could point at it — each names the *state*, and neither
can name who made it. Teaching either mechanism a new exception would have been the wrong repair;
removing the cause is one function.

## The repair

`_push_direction_or_say_why()` — one attempt, no retry, and its returned reason rides out in
`orient`'s log line.

Four things it deliberately does, each carrying an incident already paid for in this repository:

* **Success is ground truth, never the push's own rc.** It re-reads `commits_ahead` afterwards and
  asks the question the defect is about: *does this tree still hold a commit of its own?*
  `_push_reached_origin`'s lesson — a phantom "Everything up-to-date" recorded as a publish
  through a 3.5h origin freeze.
* **One attempt, never a loop.** `_divergence_refusal`'s lesson: on 2026-09-01 a rejected push was
  re-attempted identically and every attempt widened the fork. Being behind origin is a STATE.
* **It reuses `origin_reconcile._push`** rather than re-spelling `git push origin HEAD:main`, so
  the remote, the branch and the timeout stay in one place.
* **`ok` stays keyed to the COMMIT.** A rejected push must not make the row read
  `committed: false`, because the direction record does exist.

**No tree lock**, and that is not an oversight: a push writes neither the working tree nor the
index, so it cannot sweep a concurrent lane's work the way a merge could.

**It may carry another lane's gated landing to origin, and that is the point.**
`origin_reconcile.reconcile` already does exactly this ("pushed N gated landing(s) that were
sitting local-only"), for the reason `commits_ahead` records: a landing that never leaves the
machine reads as landed and is not.

## What this does NOT fix

The live fork. At the time of writing the shared tree is 1 ahead / 3 behind, which is a real
divergence and needs the gated merge door — this repair stops the *next* one being manufactured,
and cannot retire the one already open. That belongs to `origin_reconcile`, and the reason it has
not run is the gate, not this.

Nor does it establish that P1 of
`SEAT_PREREGISTRATION_WHETHER_A_MECHANICAL_ADVANCE_AT_THE_REFUSAL_LETS_A_DRAINED_QUEUE_CLOSE_ITS_EPISODE_2026-09-04.md`
holds. The answers written into that file are what they are; this finding is the *cause* of one of
them, not a substitute for the measurement.
