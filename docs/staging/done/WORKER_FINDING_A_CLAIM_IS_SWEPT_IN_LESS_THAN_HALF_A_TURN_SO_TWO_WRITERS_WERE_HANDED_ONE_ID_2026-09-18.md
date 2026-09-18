**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** none — Lane 0

*BLOCKING because it is a live cost, not a risk: the tick filing this document was handed work that
another writer had finished eleven minutes earlier, and the mechanism that exists to warn about
exactly this cannot see it by construction.*

# A claim is released in less than half a turn, so one id was handed to two writers at once

**Filed:** 2026-09-18 · **Claim id:**
`the-product-gate-census-answers-per-record-while-the-guard-refuses-per-term`
**Found by:** the 09:47 UTC worker tick drawn on that id, orienting before building.

---

## What happened, in one line

`background/seat_executor.run_once` claimed the id at **08:36 UTC** and spawned a bounded worktree
seat on it; the claim was gone from the lane's store by **09:38 UTC** while that seat was still
running; the dispatcher re-minted it at **09:47:33 UTC** and handed the identical WORK text to a
second writer. At that instant the first writer had already committed the whole of it.

## The timeline, from three logs that do not know about each other

All times UTC. Local stamps in the stores are BST (+1) and are converted here.

| when | what, and where it is recorded |
|---|---|
| 08:22 → 08:36 | `supervisor-log.md`: the ~2-minute watchdog draw names this id on **every** tick — it is the free head of the queue |
| 08:36 | `seat-executor-log.md`: `RUNNING the-product-gate-census-... in /var/tmp/se-seat-executor on 47d3115f7`. `run_once` claims in both stores (`_claim_stores`) |
| 08:36 → 09:38 | the id vanishes from the watchdog draw for **62 minutes**. This is the claim doing its job |
| 09:22 | `.seat_work_in_hand.json` is written and is now `{}` — **46 minutes** after the claim |
| 09:36:40 | the worktree seat commits `2f436602b` — the drawn work, done |
| 09:38 → 09:46 | the id **reappears** in the watchdog draw on every tick. `next_item` now finds it unclaimed |
| 09:47:33 | `claim_dispatched` mints the claim afresh and dispatches the doorbell to a second writer (this tick) |
| 09:48:26 | the worktree seat commits `ed8724fae`, merging its work onto the lane's other landing |
| 09:52 | measured: PID 2158951 still alive, 1h17m into a 5400s turn, still holding the worktree |

The second writer's first act was to check `ps`, which is the only reason this is a finding and not
a second turn spent re-deriving a finished repair.

## The arithmetic nobody did

Three constants, each defensible alone, and their relation was never stated:

* `background/seat_work_in_hand.py:149` — `STALE_AFTER_SECONDS = 45 * 60`
* `background/delivery_lane.py:205` — `CLAIM_STALE_SECONDS = 100 * 60`
* `seat_executor`'s bounded turn — **5400s**, i.e. **90 minutes**, the number its own log prints
  when a turn runs out (`did not finish inside 5400s`, five times in today's log alone)

**A writer is given 90 minutes and its claim is given 45.** Every executor turn that runs longer
than half its budget has its own claim swept out from under it while it is still working — and
today's log shows those turns routinely run 46–90 minutes (`04:21→05:51`, `06:39→08:09`, and the
one measured here). The `45` was not chosen to be shorter than the turn; nothing compared them.

**This is the picked-number shape, on the harness's own clock.** The remedy is not a bigger number:
a longer deadline only moves the cliff, and the next turn that legitimately runs to its budget falls
off it again.

## What I could NOT establish, and it matters

The 45-minute sweep explains `.seat_work_in_hand.json` emptying at 09:22 — 46 minutes after the
claim, which is the deadline plus one sweep interval. **It does not explain the lane store.**
`delivery_lane.sweep_stale` passes `stale_after=CLAIM_STALE_SECONDS` (100 minutes) explicitly, and
the lane row was gone at 62 minutes. So a second release path reached
`.delivery_lane_claims.json` between 08:36 and 09:38 and I have not identified it. Candidates I did
not separate: a `claims_mod.sweep()` caller that takes the default 45-minute deadline against the
lane's store, and the worktree seat running the `--release` its own doorbell instructs it to run
"when you judge it finished". **I am not guessing between them**: whichever it is, the defect below
stands, because both amount to a claim being released while its writer is demonstrably alive.

## Why the mechanism that exists for this could not fire

`delivery_lane.rival_claims` is the duplicate-work check, and its docstring says plainly:

> THE ITEM'S OWN CLAIM IS NOT A RIVAL, and both spellings of it are excluded

`mine = {focus_id}` — so it answers "is somebody holding this work **under another name**" and is
blind, by construction, to somebody holding it **under this one**. That is the commonest collision,
not a rare one: two routes draw from the same ordered queue, so the ordinary way for two writers to
meet is on the *same* id, not on a synonym. The check fired for the worktree seat at 08:36 (its
doorbell names `reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch`) and printed
nothing at all for the 09:47 dispatch, which is the one that needed it.

`claim_dispatched` does read `held()`, and it is worth being exact about what that read is for:

```python
if focus_id in claims_mod.held(path=store):
    # Already in hand -- a re-dispatch of a live claim must not restart its deadline
    return focus_id
```

It protects the **deadline** and then dispatches anyway. It is not a refusal and does not claim to
be one. So there is no point on the dispatch path where a live turn on the same id stops a second
one — and on the day it mattered the claim was not held anyway.

## The remedy, and it is one leg

**A claim whose writer is provably alive must not be swept.** The evidence already exists and is
already read: `seat_executor` writes `PID_FILE` and drops `OWNER_MARKER` (the owning pid) into the
worktree, and `seat_executor.worktree_is_live` already answers "is a writer still working in here".
*Nothing on the sweep path asks it.* The sweep's subject should be an abandoned writer, and it
currently measures elapsed time as a proxy for that — a proxy the turn budget outlives by design.

**A second, independent and cheaper leg**, for the dispatch rather than the sweep: `rival_claims`
should gain a same-id question, answered from `seat-executor-log.md`, which is single-valued and
already records precisely this — a `RUNNING <id>` line with no `FINISHED`/`LANDED NOTHING` line for
that id after it means a bounded turn is working it right now. Both legs are worth having: the first
stops the collision, the second makes it visible when the first is wrong.

Keying the note to the property (**is a writer alive on this id**) rather than to today's answer is
the point. A deadline comparison is keyed to the clock and goes wrong every time the budget moves.

## The disposition of this claim, and why it is NOT `--release`

The doorbell's own duplicate-work instruction says: take the disposition rather than the work —
`--landed-under` when the rival has landed, else `--release`. **Neither applies and `--release`
would be actively harmful here**, because the rival holds the *same* id rather than another one:

* `--landed-under <this id> <that id>` credits one id with another's landing. There is no other id.
* `--release` pops the claims row. The worktree seat's landing route is
  `promote_worktree_landing --work-id <this id>`, which binds the paths it pushed **to this row**.
  Release it and that binding finds nothing, the turn is logged `LANDED NOTHING`, and the finished
  work is re-offered as unstarted — the exact failure the executor's own `_hand_back` docstring
  warns about, arriving through the other door.

So the claim is **left standing on purpose** for the rival's promotion to bind, and this document is
the record of that decision. It is bound to the same claim, which is correct: it is the disposition
of the collision, filed by the writer who lost it.

## What would refute this

A reader showing the lane store's row was released by the worktree seat's own deliberate `--release`
*after* it judged the work finished, rather than by a sweep. That would make the 62-minute release a
correct act with a race behind it (release-then-promote) rather than a premature sweep — a different
defect in the same place, with a different remedy (release must come after promotion, not before).
It would **not** rescue the 45-versus-90 arithmetic, which is measured on its own store and stands
either way.

## Stranding risk, live at filing

`2f436602b` and `ed8724fae` exist **only** in `/var/tmp/se-seat-executor` on a detached HEAD and are
in no ref on the shared tree or origin. If that turn is killed at its 5400s teardown before
`promote_worktree_landing` runs, the entire drawn repair is stranded in a worktree the reaper sweeps.
Recovery, should the next reader find it there:
`python3 -m tools.promote_worktree_landing /var/tmp/se-seat-executor --work-id the-product-gate-census-answers-per-record-while-the-guard-refuses-per-term`
