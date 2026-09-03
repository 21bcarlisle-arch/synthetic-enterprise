**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS1_process_manifest_reconstruction`

# The promotion route's only runner is a prompt, and the freeze that unblocked it calls it dormant

**Found:** 2026-09-01, working the LANE 0 reconciliation. Not by a control — by checking a drawn
premise before acting on it, for the second time in two ticks on the same class.

## What I was told to decide, and why there was nothing to decide

The direction said the orphan-ratchet was refusing `tools.promote_worktree_landing` as *"work that
nothing runs"*, named the two legal moves, and ruled between them in advance:

> freezing the project's own promotion route as deliberately-dormant is the flattering answer and is
> probably wrong; a subprocess-visible runner is the honest one.

**Both halves of that were already out of date, and the second one would have manufactured a lie.**

**The decision was taken hours before the direction was written.** `promote_worktree_landing` is in
`docs/design/orphan_baseline.json` at `0bc78cf14`, the same commit that added the tool — the frozen
form, taken deliberately, in the commit the ratchet fired on. It is on **both** sides of the fork
(`git show origin/main:docs/design/orphan_baseline.json` carries it too). The ratchet has not
refused a commit over it since. The three publish failures the direction attributed to it were a
**non-fast-forward push**, which is a different thing wearing the same log line.

## The premise the ruling rested on is false

The direction says the tool *"is run — by `background/seat-executor.service`, committed in
`0bc78cf14`, which invokes it as a subprocess the ratchet's import graph cannot follow."*

Nothing invokes it as a subprocess. Every occurrence in the tree, checked:

```
background/seat_executor.py:309   inside CHARTER, a triple-quoted string:
    2. `python3 -m tools.promote_worktree_landing . --work-id <your claim id>` — gets the
       landing onto origin/main, or refuses with a named cause.
```

`CHARTER` is the prompt handed to a Claude turn. **The runner is an agent reading an instruction.**
There is no `subprocess.run`, no systemd unit, no timer and no git hook that reaches it. The other
matches are its own docstring, its tests, and two docstrings elsewhere that *describe* it — the
shape `799944f53` had already fixed once, when the invoker control fired on a docstring explaining
the thing it guards.

**So "wire it so the runner is visible" had no honest implementation.** The only way to make a
subprocess visible is to write a subprocess, and the only caller that would have justified one is
the ratchet itself. That is `WORKER_FINDING_THE_REUSE_CONVENTION_MANUFACTURES_FALSE_CALLERS` with
the sign flipped: a caller written so a control goes green is not a caller, and the control is worth
less afterwards than before.

## What is actually wrong, which is smaller and real

The freeze records the right OUTCOME under a MISLEADING REASON. The ratchet's own message offers
`--freeze` for something *"deliberately dormant"*, and the baseline carries no other vocabulary. But
`promote_worktree_landing` is **not dormant** — it ran twice by hand before it was a tool, it is the
second half of the only sanctioned route off an isolated writer, and `background/seat_executor.py`
tells every unattended turn to use it. A future reader who greps the baseline for what is safe to
delete will find the project's promotion route filed as dead.

**The gap is in the ratchet's vocabulary, not in this entry.** Its two categories are "something
runs it" and "nothing runs it, on purpose". This project now has a third that is neither: *run by an
agent, from a committed instruction* — the seat-executor's charter, the staging protocol, the
skills under `.claude/skills/`. That class will grow, because the unattended writer is new and
every instruction it is given has this shape.

**Not fixed here, and not proposed as a subsystem.** A third baseline category is a change to a
control's meaning and belongs to whoever owns the ratchet, on evidence of more than one instance.
What is owed is one line: the entry saying *which* of the three it is. I am recording the instance
rather than minting the category from a sample of one — which is the error the previous tick's
prediction was refuted for, two documents ago.

## The pattern this is the second instance of, in two ticks

Both ticks were handed a direction whose premise the tree had already falsified, and in both cases
acting on the premise would have put something false into the repository:

| tick | the premise | the truth | what acting on it would have produced |
|---|---|---|---|
| 2026-09-01 earlier | `production_surface_guard`'s widening is uncommitted, land it or park it | on `origin/main` since `22aaaa494` | a parked patch file and a decision record for a decision already taken |
| this one | the ratchet refuses the promotion route; wire a visible runner | frozen in `0bc78cf14`, on both sides; and there is no subprocess to make visible | a subprocess written so a control would go green |

The common cause is the one the reconciliation just fixed: **direction was written against a base
twenty commits stale.** The leg landed in `16fe54aa4` makes that visible on the surface every
publish cycle — `HEAD is 22 behind origin/main … so this count is measured against a stale base` —
which is the cheapest thing that would have stopped either instance. It does not stop a *direction*
being written stale, and nothing here does; what it does is make the staleness the first thing a
reader of the tree sees rather than something they discover by acting.
