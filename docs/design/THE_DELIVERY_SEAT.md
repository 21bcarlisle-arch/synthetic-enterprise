# The delivery seat

**Director, 2026-08-25 (console):** *"You have ticks that execute — wake, draw an atom, commit,
exit — and a seat that works when a human grants a turn. What you don't have is anything that
orients: something that wakes on its own, reads the last stretch across the alerts, the commits,
the map and the site, and decides what actually matters next, what's drifting, and what the next
stretch should be. My advisor and I have been doing that in a chat window, by hand. That's the
most expensive way it could possibly be done and it stops now."*

And with it, a standing duty rather than a task: *"you hold the delivery seat ... The mission and
the direction are mine. Yours is everything between that and the work: translating direction into
priorities, keeping work flowing when it stalls, and holding the trade-offs — speed against
correctness, breadth against depth, shipping against verifying. When something blocks, you unblock
it rather than report it. When priorities conflict, you decide rather than ask."*

---

## 1. Purpose, stated before the mechanism (OPS1)

There are three roles on this machine and only two of them existed.

| | wakes | reads | writes | decides |
|---|---|---|---|---|
| **tick** (`worker_tick.py`) | a timer | one drawn doorbell | code, tests, the map | *what to do about the atom in front of it* |
| **seat** (`worker_seat.py`) | a human turn | whatever the human brought | code, tests, the map | *what the human asked* |
| **delivery seat** (this) | a timer | the whole last stretch | **direction only** | *what the next stretch should be* |

The tick executes. The seat works when granted a turn. Neither ORIENTS, and orientation is not a
gap in either of them — it is a different job, on a different clock, with a different output. It
has been done by hand in a chat window, which is why it has been expensive and why it stopped
whenever the window did.

## 2. The one distinction everything else hangs off

`background/daily_self_note.py` carries a HARD LAW called SEVERANCE: it may measure the machine
and it may never touch the draw, because *a self-measurement that feeds the draw is goal-seeking*.
The delivery seat feeds the draw by design. That is not an exception to the law — it is the other
side of a line the law never drew:

> **The delivery seat may decide WHAT TO WORK ON. It may never decide WHAT COUNTS AS SUCCESS.**

Priority is a judgement about attention and is exactly what a delivery seat is for. A target is a
number the work then bends toward, which is R12's whole subject. So the direction record may name
work, lanes, findings and questions, and it may not contain a metric, a threshold, a target or a
score. That is not a promise; §6 makes it a control.

## 3. What it does, in order

1. **Read the stretch.** Since the last orientation: commits (substantive vs mechanical, reusing
   `daily_self_note`'s own classifier rather than a second one), staging findings by severity,
   repeating alarms, map level moves, publish freshness, the coupled-triad gaps, the deadman's
   stall clock, and anything the director said.
2. **Decide whether to orient at all.** Nothing material changed → record a skip with its reason
   and exit. A skip is recorded, never silent (R5).
3. **Judge.** One bounded `claude -p` session, Opus, with the delivery-seat charter as its
   preamble and the assembled brief as its prompt. It writes the direction record itself.
4. **Validate.** Schema, non-empty `not_now`, no target-shaped content, focus keys resolvable.
   Invalid → the previous direction stands, the failure is recorded and paged. Fail-closed on
   the artefact: a malformed direction record is not a direction record.
5. **Record.** Append one row to `docs/direction/decisions.jsonl` — what it chose, what it
   rejected, and whether the PREVIOUS stretch's focus was actually drawn.
6. **Commit by pathspec**, and the pathspec is a constant.

## 4. What it may write, and how "never a second writer on the tree" is real

    docs/direction/DIRECTION.yaml     the current direction, overwritten each orientation
    docs/direction/decisions.jsonl    append-only; every orientation, including skips
    site/data/delivery.json           the page's data

That tuple is a module constant and it is what the seat passes to `git add`. Anything else the
session touched is simply not committed by it — the pathspec, not a promise, is the mechanism
(the same reason CLAUDE.md gives for committing by pathspec under concurrent writers). Out-of-scope
modifications attributable to the seat are recorded and paged rather than reverted: reverting
would be a second writer stamping on the first, which is the thing being prevented.

## 5. How direction reaches the ticks — a weight, never a gate

`supervisor._maturity_map_draw_concurrent` picks the primary atom with
`picker.choices(candidates, weights=[max(1, dial_inherited)])`. Direction multiplies those
weights. It does not filter, exclude, or reorder the candidate list.

That choice is the whole of Rule 0 in one line: **a direction record can never empty the feasible
set.** Every atom keeps a weight above zero, so the worst a wrong or stale direction can do is
make the machine slower to reach something — never unable to.

Three consequences, all deliberate:

* **Missing, stale or malformed direction is not an error.** The reader returns "no focus" and
  the draw behaves exactly as it does today. A direction record is advice; the draw is the
  authority.
* **A focus that never gets drawn is VISIBLE.** Every orientation records whether the previous
  one's focus was actually drawn. `d7d36b46a` records the lesson this is guarding against: *two
  SOFT guards composed into a no-op* and nobody noticed for 1,307 draws. A soft steer that
  quietly does nothing is the failure mode of this design, so it is the thing measured.
* **It expires.** A direction record older than `FOCUS_MAX_AGE_HOURS` stops biasing anything.
  Stale direction is worse than none — it steers toward what mattered yesterday with all the
  confidence of what matters now.

## 6. Controls (R15 — each names the mutation that must fire)

| control | mutation that must red it |
|---|---|
| direction cannot zero a candidate's weight | return 0.0 for a non-focus atom |
| direction cannot shorten the candidate list | filter instead of weight |
| a missing/malformed record leaves the draw byte-identical | raise instead of returning no-focus |
| an expired record stops steering | drop the age check |
| the record may contain no target | add a `target:`/threshold key and watch the schema refuse |
| `not_now` may not be empty | write a record that rejects nothing |
| the write pathspec is closed | add a code path outside the three declared paths |
| a focus that never drew is reported | stop recording the previous focus's draw outcome |

## 7. Cadence

Every three hours, via `delivery-seat.timer`, declared in `background/schedule_manifest.yaml` like
every other unit (IaC: nothing behaviour-determining outside the readable repo).

Three hours rather than the tick's thirty minutes because orientation is not execution: a stretch
has to be long enough to have a shape. The skip rule means a quiet three hours costs one cheap
read and no model turn at all, so the cadence is bounded by material change and not by the clock —
which is what the token budget requires and what R5 requires for the same reason.

## 8. The other half: one page

Director: *"I can't see any of this without someone reading git logs to me. I want to open one
page and know what the machine did, what it decided, what it got wrong, and what it's doing next.
Harness was meant to be that and isn't."*

`/harness/` is rebuilt around exactly those four questions, in that order, above the doctrine
sections it already carries. It is not a sixth tab: the page he already opens becomes the page
that answers.

The same page carries the director-delta section that `SITE9`'s overturned ruling asked for
(*"SITE9's director-record block is overturned. Rebuild the delta as a section on /harness/"*) —
`site/data/director_delta.json` has been generated every cycle with nothing rendering it. Its
honest caveat travels with it: the last-look stamp reads
`bootstrap-at-build-time (not a director read receipt)` and the page says so rather than
implying he has read anything.

## 9. What was considered and rejected

**A new page instead of rebuilding `/harness/`.** Rejected: he asked for ONE page and named the
one he already opens. A sixth tab would answer the request by adding to the problem.

**Letting the orienting session edit code when it sees something small.** Rejected, and it is the
constraint he stated. The value of this seat is that its output is *direction*, which is cheap to
be wrong about and easy to correct. A second writer on the tree is expensive to be wrong about and
collides with the concurrent-writer problem CLAUDE.md already documents three times over.

**Making direction a filter on the draw** (only focus atoms are drawable). Rejected as a Rule-0
violation: an empty feasible set is a defect in the dials, and a filter is a dial that can empty
it. A weight cannot.

**A hand-maintained priority list instead of a periodic session.** That is `PRIORITIES.md`, and it
already exists. It is a record of what was decided, not a mechanism that decides; it goes stale in
exactly the way the chat window went stale. The seat writes into the same world PRIORITIES.md
describes rather than replacing it.

**Scoring the stretch** (a number for how the last stretch went). Rejected under §2 and R12: the
moment orientation produces a score, the next stretch optimises the score.

**Letting the publisher commit the record instead of the seat.** `site/data/*.json` is already
globbed into every publish commit, so `delivery.json` reaches origin either way, and adding
`docs/direction/` to that list would take the seat out of the committing business entirely — a
strictly stronger reading of "never a second writer". Rejected on one property: if the seat's own
commit fails, its recorded `committed: false` is the only thing that says so, and a publisher
quietly carrying the file anyway would mask a broken seat as a working one. The gate cost that
made this tempting turns out not to exist — `pre_commit_test_gate` selects tests by changed path,
and a `docs/direction/**` + `site/data/delivery.json` commit selects the site suite, which is ten
seconds.

**Running it on the tick's thirty-minute clock.** Rejected on both cost and sense: orientation
every half hour is mostly re-reading, and the token budget is the binding constraint (director,
twice). Three hours with a material-change skip.
