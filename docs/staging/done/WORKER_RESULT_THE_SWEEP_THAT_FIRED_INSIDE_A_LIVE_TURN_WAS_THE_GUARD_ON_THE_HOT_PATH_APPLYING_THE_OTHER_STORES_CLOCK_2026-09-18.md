**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** delivery-lane-claim-clocks

# The sweep that fired inside a live turn was the guard on the hot path applying the other store's clock

**Filed:** 2026-09-18 · **Claim id:** `a-writer-outlives-its-claim-so-a-live-seat-is-reported-as-a-miss`
**Grades:** `ac4f097d4` (HEAD at draw)

---

## State in one line

**Done and landed.** No claim store is now swept on a deadline shorter than a bounded turn, each
store is swept on **its own** deadline rather than on the cross-lane guard's, and `rival_claims`
can see a live holder of the item's own id in the store the draw did not write. The ordering of the
three bounds is controlled, not restated, in
`tests/background/test_a_sweep_cannot_fire_inside_a_live_writers_bound.py`.

## The three clocks, compared for the first time

| bound | was | is | module |
|---|---|---|---|
| a bounded turn, systemd-enforced | 5,400s | 5,400s | `seat_executor.SESSION_TIMEOUT_SECONDS` |
| the cross-lane path guard's store | **2,700s** | **5,400s** | `seat_work_in_hand.STALE_AFTER_SECONDS` |
| the delivery lane's store | 6,000s | 6,000s | `delivery_lane.CLAIM_STALE_SECONDS` |

Both measurements the item carried land in the band the 2,700 opened and the 6,000 did not — the
08:36 writer re-handed at 09:47 (**4,260s**) and pid 2436269 alive at **4,182s** of 5,400 with its
claim already swept. Neither is an edge case. A deadline shorter than the writer's own lifetime
cannot be measuring a stall: the claim it releases is, by construction, held by a process that is
still running and has no way to be told.

## The defect was TWO, and only one of them was a constant

**1. The constant was inside the bound.** `seat_executor` claims its work id in *both* stores at
turn start with `paths=[]`, and `delivery_lane.record_landing` binds paths into the **delivery**
store only. So the `seat_work_in_hand` copy has no observable progress signal for the whole turn
however much the turn lands — `last_progress` is its own `claimed_at` — and at 45 minutes the next
writer to call `refuse_if_duplicated` swept it. `seat_executor.py:468` already records the alarms
that produced; what it did not say is that the turn being alarmed about was still running.

**2. And the sweep on the hot path used one deadline for two stores.** `overlapping_claims` is the
only thing that sweeps during a landing. It read both stores and called `sweep(path=store)` with no
`stale_after`, so `delivery_lane.CLAIM_STALE_SECONDS` was **decorative**: every delivery-lane claim
was in fact released at the shorter of the two, by the duplication check, before the lane's own
sweep could ever see it. Fixing the constant alone would have moved that from 45 minutes to 90 and
left the wrong clock in place.

**This was written down as an obstacle and never as a defect, which is why it stood.**
`tests/tools/test_a_promotion_binds_its_landing_to_the_claim.py:86` builds its fixture claim "TWO
MINUTES AND NOT AN HOUR, because `refuse_if_duplicated` sweeps every store it reads with
`seat_work_in_hand`'s own 45-minute deadline rather than the delivery lane's 100." An exact
description of the bug, in the repository, working around it. A comment that explains how to dodge
a defect is the defect's best hiding place.

## It answers the one thing the finding could not establish

`WORKER_FINDING_A_CLAIM_IS_SWEPT_IN_LESS_THAN_HALF_A_TURN_SO_TWO_WRITERS_WERE_HANDED_ONE_ID` has a
section headed **"What I could NOT establish, and it matters"**. The 45-minute sweep explained the
seat store emptying at 46 minutes, but not the **lane** store, whose row was gone at 62 minutes
while `delivery_lane.sweep_stale` passes 100 explicitly. It named two candidates and refused to
guess between them. The first was:

> a `claims_mod.sweep()` caller that takes the default 45-minute deadline against the lane's store

**That caller exists and is `overlapping_claims`.** It is on the landing hot path, it is called by
every unattended writer through `refuse_if_duplicated`, it read the lane store, and it called
`sweep(path=store, now=now)` with no `stale_after`. Eligible from 09:21; the row was gone by 09:38.

Establishing the *route* is not establishing that it *fired that morning* — nothing logs which
writer's `refuse_if_duplicated` swept which row, and the finding's other candidate (the worktree
seat's own `--release`) is not excluded by this. What is established is that the finding's open
question had an answer in the code, that the answer is a live 45-minute release path against a
store that declares 100, and that it is now closed whichever one fired on the day.

## Where the finding's own remedy was right, and where it was wrong

The finding argues: *"The remedy is not a bigger number: a longer deadline only moves the cliff,
and the next turn that legitimately runs to its budget falls off it again."*

**That is right for an unbounded writer and wrong for this one.** `SESSION_TIMEOUT_SECONDS` is
enforced by systemd. A bounded turn cannot be past 5,400 seconds and alive, so at the bound the
elapsed-time proxy is not an approximation of liveness — it is exact, and the cliff has nowhere
left to move to. That is why the ordering repair closes the measured collision on its own and why
no pid read was needed for it.

It stays right for the **interactive seat**, which has no systemd bound and can legitimately hold a
claim for four hours. That writer is still swept on a clock — at 90 minutes now rather than 45 —
and the finding's first remedy leg (ask `seat_executor.worktree_is_live` / `PID_FILE` before
sweeping) is the only thing that would fix it. **I did not build it and it is owed.** It is not
free: the 45 was set to catch a 263-minute stall, and a liveness read that answers "yes" for a seat
that is idle rather than working would restore the unbounded pass this module removed in August.
That is a design call with a measurement behind it, not a line to add.

The finding's second leg — a same-id question on `rival_claims` — I built, from the **claim stores**
rather than from `seat-executor-log.md`. The stores are single-valued too, they are already read on
that path, and they cover the executor because `run_once` claims in both; a log parse would have
added a second source of truth about who holds what.

## The rival check was blind exactly where the draw already was

`rival_claims` excluded the item's own id in **every** store. `draw()` claims into this lane's
store and nowhere else, so a row under the same id in the seat store was put there by somebody else
— an interactive seat, or a live `seat_executor` turn, which claims in both. And `next_item` filters
`held()` on the delivery store **alone**. So a live holder of the exact id was invisible to the
draw, and the one instrument built to give a second opinion excluded it by name.

It now reports it, by name and with the store that holds it, because a claim record carries no
holder field and the store is the only thing that says which writer puts rows there. The item's own
row **in its own store** is still not a rival — `draw()` claims before it composes, so reporting
that would put a note on every draw ever made.

The same-id leg is returned **through** the `if not others` short circuit rather than after it. The
commonest way to be the only live holder of an id is for there to be no other live claims at all,
so a leg placed after the early return would have looked implemented and been unreachable in its
own ordinary case — this file's own R15 shape.

## What DONE was, and why the control is keyed to the ordering

The director's `done` was: *a sweep cannot fire inside a live writer's bound, proven by a control
that reds if the two constants are reordered.* So no leg pins a value:

```
SESSION_TIMEOUT_SECONDS <= STALE_AFTER_SECONDS < CLAIM_STALE_SECONDS
```

Change any of the three and the control stays green. Move one **across** another — including
raising `SESSION_TIMEOUT_SECONDS`, the direction nobody would check because the number that moved
is in a third module — and it reds. The strict inequality on the right is load-bearing separately:
equal deadlines would make every per-store leg vacuous while reading as green.

`test_ALL_THREE_STATES_OF_A_CLAIMS_LIFE_ARE_REACHABLE` is one assertion over the whole partition
rather than a leg per branch — inside the bound neither store is stale, between the deadlines only
the seat store is, past both are — because a guard that refuses everything passes every
per-branch leg. That is the trap this file has entered three times before.

## Mutations, all five run in a clean extract

| mutation | what reds |
|---|---|
| `STALE_AFTER_SECONDS` back to `45 * 60` | the ordering leg **and** the partition leg |
| drop `stale_after=deadline` from `overlapping_claims`' sweep | the per-store-deadline leg |
| exclude `mine` in every store (the pre-repair line) | both same-id legs |
| short circuit returns `{}` again | both same-id legs |
| drop `work_id in stale` from the same-id leg | the stale-holder leg |

None is an equivalence and none needed a second test written to catch it. The mirror leg
(`THE_SEAT_STORE_KEEPS_THE_SHORTER_DEADLINE_IT_DECLARES`) exists so the repair cannot be satisfied
by giving every store the longest deadline, which would leave a dead cross-lane writer holding a
path for an extra hour.

## The same-id leg fired on a real collision within the hour, before it was committed

Not predicted, and worth more than the fixture that proves it can. The daemons run the **working
copy**, so the new leg was live the moment it was written. At 16:31 a delivery seat (pid 3516304)
was dispatched into an isolated worktree with this in its doorbell:

> DUPLICATE-WORK CHECK (live claims, run at draw time): 1 other live claim(s) may be this work
> under another name — `re-run-the-noise-floor-over-the-09-18-book-so-the-error-bar-stops-refusing`
> (**is ALREADY HELD under this very id in `.seat_work_in_hand.json`, which this draw does not
> write — another writer has it in hand right now**).

A genuine instance, on the first live application, of the exact shape the finding called "the
commonest collision, not a rare one". The id was held in the seat store and **not** in the lane's,
which is why `next_item` offered it — the blind spot the leg was built for, hit on its first day
without being looked for. The note is advisory and the seat carried on, which is right: two live
claims on one subject are sometimes correct and this one has a reader who can see both.

It is evidence of reachability, not of correctness, and it does not replace the fixture — a leg
that fires is not yet a leg that fires *only* when it should, which is what
`THE_DRAWS_OWN_CLAIM_IN_ITS_OWN_STORE_IS_STILL_NOT_A_RIVAL` and
`A_STALE_HOLDER_OF_THIS_ID_IS_NOT_A_LIVE_RIVAL` bound.

## Where the repair actually breaks the measured chain

Traced against the finding's own timeline, and the break is at the sweep and not at the notice:

| when | then | now |
|---|---|---|
| 09:21 | `overlapping_claims` sweeps the lane row at 45 min | survives to 100 min — past the turn's end |
| 09:22 | the seat row swept at 45 min | survives to 90 min — the bound |
| 09:38–09:46 | `next_item` finds the id unclaimed and offers it | `held()` contains it, so it is filtered out |
| 09:47 | `claim_dispatched` mints it and dispatches to a second writer | the doorbell never names it |

Worth stating because the same-id leg would **not** have caught this one: by 09:47 both rows were
gone, so there was no holder for it to see. The two legs are genuinely independent — the sweep fix
stops the collision, the same-id leg makes a collision visible when the sweep fix is not what is
protecting you, which is the case `next_item` cannot cover because it filters on **one** store
while a live holder may be in the other.

And `claim_dispatched` is still not a refusal — its `held()` branch protects the deadline and
dispatches anyway, as its own comment says. That is unchanged and deliberate: with the row present,
the item never reaches it.

## What this does NOT claim

The 100 minutes now stands only 600 seconds clear of the 90, where it used to stand 3,300 clear of
the 45. That margin no longer matters — each store is graded on its own clock, so the gap between
them is not what protects either — but the *reason* for `CLAIM_STALE_SECONDS`' value is now a
different reason than the one its docstring gives ("longer than the interactive seat's 45
minutes"). It is not re-derived here and no number was picked to make it look derived. If the
delivery lane wants a margin over the bound rather than over the other store, that is a separate
measurement and it is owed.

Nor does this touch `_landing_grace_seconds`, which is derived from the gate timeout and is about a
commit arriving after the window rather than about the window's length.
