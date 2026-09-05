**Severity:** BLOCKING — lane 0 is the delivery seat's own decisions, and for this item the lane's
only feedback channel returned "bound NOTHING" against a commit that had just passed the gate ·
**Lane:** H_harness · **Epoch:** 3 · **Atom:** none — RUNG 1 lane-0 delivery · **Class:**
controls_that_cannot_fail

# The drawn lane-0 item was never claimed, so the bind instruction the doorbell itself gives is inert

Filed 2026-09-05 by the autonomous worker, on the tick that drew
`weather-cells-phase1-finish-and-receipt-the-daily-pull`.

## 1. What was measured

The doorbell drew the item and carried its own instruction verbatim:

> IMMEDIATELY AFTER EACH COMMIT, run `python3 -m background.delivery_lane --landed
> weather-cells-phase1-finish-and-receipt-the-daily-pull`: that binds the paths that commit touched
> to your claim, and it is the ONLY way this lane can see your work moving. Skip it and the claim is
> swept back into the pool in 100 minutes however much you landed.

I landed `5c1f809b8` (4 paths, gated, from the shared tree — not a linked worktree) and ran exactly
that. It answered:

```
bound NOTHING to weather-cells-phase1-finish-and-receipt-the-daily-pull: it is NOT CLAIMED --
nothing holds a deadline for it, so there is nothing to inform.
```

Three stores were then read from the shared tree:

| Store | Holds this id? |
|---|---|
| `docs/observability/.delivery_lane_claims.json` | **no** — one unrelated id |
| `docs/observability/.delivery_lane_claims.draws.json` | **no** — never recorded a draw |
| `docs/direction/DIRECTION.yaml` `focus:` | **yes** — the item, with its full what/why |

So this is not the worktree trap (`_store_is_worktree_local`), and not the promoted-item trap
(§9.1, claimed in `seat_work_in_hand` and released here). It is a third state: **the item was
composed into a tick's doorbell straight from `focus:` without any claim or draw being recorded at
all.** `refusal_reason` already names this case in its last clause — *"if it never claimed, the work
was done unclaimed and the lane could not see it move"* — which is the reading that applies, and
nothing turns that reading into a signal anybody sees.

## 2. Why it is worse than an unrecorded landing

The obvious cost is bookkeeping: the lane cannot see the work move. That is real but survivable.

The cost that bit is the second one. **An unclaimed item stays drawable while its runner is still
running.** The claim is the only thing that hides an item from the next draw, and there is no claim.
This item's work is a two-hour detached HadUK-Grid pull, deliberately launched to survive the tick
that started it (`systemd-run --user --unit=haduk-pull-2026-09-05`). Every 30-minute tick between
now and its finish can draw the same item, read the same "resume the pull" instruction, and launch a
second puller over the same cache.

Two pullers do not crash. They append to the same `.part` file and produce a grid of the right name
and the wrong bytes; the size check then records it as a `failed` row, and the receipt publishes a
gap row for a heating-season month. **The analysis reads that as "the archive did not have this
month".** Fabricated evidence, from two processes each behaving correctly, arriving through a
bookkeeping hole.

## 3. What was done about it here, and what was not

Fixed, in `5c1f809b8`'s successor: `tools/fetch_haduk_grid.py` takes a single-instance lock keyed to
**pid plus the process start time from `/proc/<pid>/stat`**, not the pid alone — a recycled number
would otherwise hold the lock for the rest of the machine's uptime, which is a worse failure than
the concurrency it guards and looks exactly like the guard working. A lock naming a dead pid does
not block the resumption, which is the whole point of a resumable puller. The lock was written for
the run already in flight and a second `python3 -m tools.fetch_haduk_grid` was then **observed
refusing**, live, before this was filed. Four mutations, four named tests.

**Not fixed, and the reason this is filed rather than closed:** the lock is a guard on ONE item's
work. Every other lane-0 item drawn by this route has the same hole and its own version of the
consequence, and I cannot see from here which of `next_item`'s routes composed this doorbell without
claiming. The repair belongs where the draw is made:

- **Either** a doorbell may not carry a `--landed` instruction for an id it did not claim — the
  instruction is the tell, and an instruction that cannot succeed is worse than none, because the
  worker runs it, reads "bound NOTHING", and has no way to know whether that is the expected
  post-`--release` reading or this;
- **or** composing an item into a doorbell IS the claim, and the two cannot come apart.

The second is the smaller mechanism. The first is a control over the first.

## 4. The control that would have caught it

None exists, and the shape is the familiar one: **a guard whose subject comes from the register it
guards.** `--landed` can only bind what the claims store holds, so an item that never entered the
store is outside its subject by construction, and its refusal is indistinguishable from the ordinary
already-released reading. The control has to be keyed to the **doorbell** — *every id named in a
dispatched doorbell is claimed at dispatch* — because that is the only place both halves are
visible at once.
