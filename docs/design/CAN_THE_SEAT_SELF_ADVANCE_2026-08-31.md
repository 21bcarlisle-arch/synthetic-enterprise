# Can the delivery seat self-advance? Asked, answered NO on a measurement, then the blocker was FIXED — now yes

> **READ THE REVISIT AT THE BOTTOM BEFORE QUOTING THIS.** The first answer was NO and the reason
> was `surgical_land` being unable to commit from a worktree. **That was fixed the same day and
> proven end to end**, so the answer is now a qualified YES with two named residuals. The original
> reasoning is kept intact above the revisit because it is the record of how the decision was
> made, not because it still stands.

**Director, 2026-08-31:** *"CLAUDE.md line 47 says finishing a piece of work is where the next one
starts. This seat is built not to self-advance, because two writers on a shared tree caused most of
August's damage. Both are right and they contradict — and since the heaviest work happens in this
seat, the contradiction resolves onto me pressing enter. That has been the biggest single drag on
this project for a fortnight… Decide, build it, and tell me afterwards which you chose and why."*

**The answer is NO, and the reason is one command's worth of evidence rather than caution.**

---

## What I expected to find, and why

The contradiction dissolves if the seat stops being a second writer *on the shared tree*. Give it
its own `git worktree`, let it land through `tools/surgical_land`, and every control is preserved
while the collision surface disappears. Both of the director's premises survive: the seat advances,
and there is no second writer where the damage happens.

**And the evidence for that shape was strong.** Today's session ran **twelve landings** through
`surgical_land`. One lost a race to another lane mid-gate, re-gated against the new base and landed.
Every receipt verified. Nothing swept another lane's work. **Commit-layer collisions: zero.**

Every problem I actually hit came from the *working tree*:

| what happened | where |
|---|---|
| C1b's uncommitted work across 5 files blocked a sim change from landing — all day, twice | shared tree |
| a 430-line extension appeared mid-turn and reddened a landed control tree-wide | shared tree |
| the ruff baseline moved twice mid-measurement | shared tree |
| `git stash` nearly popped another lane's parked work | shared tree |
| `cd` drift wrote edits into the wrong repo copy, twice | shared tree |
| a duplicate finding, because neither writer could see the other's claim | needs a claim |
| **commit collisions** | **none** |

The door is solved. The tree is not.

## What killed it

I tested the load-bearing assumption before building on it. **`surgical_land` cannot commit from a
worktree at all:**

```
$ git worktree add --detach /tmp/.../seat-wt HEAD
$ cd /tmp/.../seat-wt && python3 -m tools.surgical_land -m "probe" <path>
[surgical-land] REFUSED: git read-tree <sha> failed rc=128:
error: unable to normalize alternate object path: /tmp/.../seat-wt/.git/objects
fatal: failed to unpack tree object <sha>
```

A linked worktree's `.git` is a *file*, not a directory; the door builds its would-be tree assuming
a normal repo layout. It refuses rather than mis-committing, which is the right failure — but it
means **an isolated writer has no legal way to commit**, and `--no-verify` is a wall, not a
judgement call.

So a self-advancing seat would necessarily be a second writer **on the shared tree** — the exact
configuration the restriction exists to prevent, and the one that produced all six of today's
collisions. Building it would have been trading a known-safe constraint for a known-unsafe one on
the strength of an assumption I had not checked.

Filed with the repro, consolidated into `CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` (instance 55).
**Fixing it is a real turn's work on the door every lane commits through, and it wants a tree that
is not being written by two other sessions at the time.** When it is fixed, the other answer becomes
available and should be revisited.

## What I built instead, and why it needs no second writer at all

**The pipeline already existed end to end** and nobody had noticed the one missing wire. The
periodic seat writes `focus` into `DIRECTION.yaml`; `delivery_lane.next_item` offers the first
unclaimed item; a worker tick does the code and lands it. `delivery_lane` says so itself:

> *"It is NOT the delivery seat writing code… what changed is that the TICKS, which have landed real
> work all day every day, can now be handed the seat's judgement."*

**The gap was that the INTERACTIVE seat's judgement never entered it.** The periodic seat
*re-derives* focus from the state of the tree every three hours — it does not inherit what a session
that just did four hours of work already knew. That continuation died at the turn boundary, and the
director restarted it by hand. That is the drag, exactly.

`background/seat_continuation.py` closes it. When this seat finishes a piece and knows what comes
next, it writes it down; `next_item` offers it **ahead of** the periodic focus list, because a
continuation is minutes old and written with the whole context where a focus item is up to three
hours old and re-derived. Claims, staleness sweeps and the doorbell are the existing machinery,
untouched.

**Continuations expire after six hours, and that is the load-bearing property, not tidying.** A
continuation is reasoning about a tree, and the tree moves — measured today: C3's result was taken
on a book of 465 renewal decisions and a landing in between cut it to 144, a different and
*selected* population. The numbers survived and described nothing. **A stale continuation is worse
than none, because it arrives with the authority of a decision and none of its context.**

Seven mutations proven: the draw ignoring continuations (the drag restored), the cutoff dropped, a
stale item offered, expiry made invisible, an incomplete handoff stored, appending instead of
replacing, and claims ignored. An unreadable store degrades to *no handoff* and never to a broken
lane — `delivery_lane.draw` documents that a lane which can throw takes every other lane down.

## What still would not work, said plainly

1. **This does not make the seat autonomous.** It makes the seat's *judgement* survive the turn
   boundary. The heavy work still happens in a tick, bounded, one piece at a time — which is
   strictly less capable than an unattended seat and is the honest trade for not having isolation.
2. **Duplication is not fixed by any of this.** Today I filed a duplicate of another lane's finding
   because neither of us could see the other's in-flight claim. Continuations are claimed, so two
   ticks cannot take one item — but two *writers* can still independently choose the same work.
3. **An unattended writer can be confidently wrong for hours.** I was wrong four times today and
   caught each by measuring. Nothing structural guarantees the next run does. Every landing is
   gated and every finding filed, and the director reviews retrospectively — but that is a
   mitigation, not a proof, and it belongs in the decision rather than under it.
4. **`.seat_work_in_hand.json` is `{}`.** The interactive seat's own claim store has never been
   used. The handoff is the same idea one step further on, and if continuations also go unwritten
   the mechanism will be as empty as that file. `--list` printing EXPIRED items is what makes that
   visible instead of quiet.

## The decision in one line, AS IT STOOD BEFORE THE FIX

**The seat cannot self-advance because the only legal commit door does not work outside the shared
working tree — so the seat's continuation moves into the ticks, which are already writers and need
no new one.** When `surgical_land` learns about worktrees, the better answer is available and this
document is the record of why it was not taken today.

*It learned, within the hour. See the revisit.*

---

# REVISITED, same day, after fixing the door — the answer is now YES, with two named residuals

**Director: *"Fix surgical_land for worktrees, then revisit self-advancing."*** Done, and the
revisit follows.

## The fix

One line, and it was exactly where the error said. `_make_standalone_repo` wrote its alternates
line from `root / ".git" / "objects"`; a linked worktree's `.git` is a file, so that path never
existed. It now **asks** — `git rev-parse --git-common-dir` — and `Path(root, common)` is correct
for both layouts, because an absolute right-hand side wins and a relative one joins.

**`--git-common-dir`, not `--git-dir`**, and that distinction is the whole of it: a worktree's own
gitdir (`.git/worktrees/<name>`) holds its HEAD and index and **no objects at all**. Lending that
would fail the same way one directory down.

**Proven end to end, not just at the unit.** A real linked worktree ran a real land through the
full pre-commit gate and committed: `[surgical-land] landed 6d1916736 (1 path(s))`. Four mutations
fire on `tests/tools/test_the_door_works_from_a_worktree.py`, including a blast-radius leg that
holds the ordinary main-repo answer unchanged — this is the door every lane commits through and a
quiet change to the normal case would be worse than the gap it closed.

## What the probe also showed, which I had not predicted

**A worktree land commits to the worktree's own detached HEAD. `main` was untouched.** That is
*more* isolation than the design assumed, and it is the good kind: an isolated writer cannot move
the shared branch by committing. Integration is a separate, deliberate step.

## So: can the seat self-advance safely now? YES — and the residuals are no longer the commit

The blocker is gone and the evidence for the rest already existed: twelve landings in a day, one
race auto-re-gated, every receipt verified, zero commit-layer collisions, and every real collision
on the shared working tree — which a worktree removes.

**Two residuals, and neither is hypothetical:**

1. **Integration to `main` is a route, not a command.** The worktree commits to a detached HEAD;
   getting there means `git push origin HEAD:main` (rejected, correctly, if `main` moved — fetch,
   re-gate, retry) and the shared tree fast-forwarding afterwards. I have now done that route by
   hand twice today and it worked both times, including once when the shared tree was too dirty for
   any in-place merge. **It is not yet a tool**, and hand-rolled git on a shared tree is precisely
   where `git stash` nearly took another lane's parked work this morning.
2. **Duplication is still unsolved and is now the larger risk.** Continuations are claimed, so two
   ticks cannot take one item — but two *writers* can still independently choose the same work. I
   filed a duplicate of another lane's finding today for exactly this reason. An unattended seat
   raises the rate at which that can happen.

**And the honest one that no fix reaches:** an unattended writer can be confidently wrong for hours.
I was wrong four times today and caught each by measuring. Nothing structural guarantees the next
run does.

## What I am doing about it, and why not all of it now

The correct next step is the integration route as a tool, then the seat tick that uses it. **I am
handing that to the ticks through the mechanism built for exactly this** rather than building it in
the same turn that changed the commit door — a door fix and a new autonomous writer are two
independent risks and landing them together would make a bad result unattributable.

`background/seat_continuation.py` now carries it. That is also the first non-trivial test of the
handoff: if it is picked up and done, the mechanism works; if it expires unclaimed, `--list` says
so, and that is the drag made visible rather than quiet.

