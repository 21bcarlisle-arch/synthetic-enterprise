**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — the re-promotion guard is keyed to a flag a session must remember to type, not to the ledger fact that already proves the work landed inside its own window

Drawn as `bind-the-refuted-knee-draw-to-the-commit-that-actually-landed-it`, for the second time.
**This invocation is the defect.** Its whole drawn instruction was already done, bound and landed
fourteen minutes before the item that dispatched it was written.

## The premise, re-measured at draw: SPENT, both halves

The item asked for one command —
`delivery_lane --landed the-refuted-bill-stress-knee-... --commit 3b01193a8`. Read off the draw
ledger just now:

| row | field | value |
|---|---|---|
| `the-refuted-bill-stress-knee-...` | `last_landing_at` | 2026-09-23 17:54:15 (`3b01193a8`) |
| | `last_landing_paths` | 5 paths, including `company/crm/churn_model.py` |
| | `premise_spent` | stated 2026-09-24 11:39:34, with its reason |
| `bind-the-refuted-knee-...` | `last_landing_at` | **2026-09-24 11:52:31** |
| | `last_drawn_at` | **2026-09-24 11:36:43** |

The bind was made. The generalisation of it landed as `8379e8e0e` ("the delivery lane says when a
bind cannot settle its own window", 3 files, +370) and is on `origin/main`. The `premise_spent`
disposition was stated for the window the bind could not settle. That whole sequence is written up
in `SEAT_FINDING_A_LANDING_BOUND_TO_A_RE_DRAWN_ID_CANNOT_SETTLE_ITS_WINDOW_AND_THE_BIND_REPORTED_SUCCESS_2026-09-24.md`,
which is itself one of the three files `8379e8e0e` landed.

**There was nothing left to do, and the ledger knew it.** `last_landing_at` (11:52:31) is NEWER
than `last_drawn_at` (11:36:43): a landing bound inside the row's own most recent window, which is
precisely the shape that means *drawn, worked, landed*.

## What re-minted it anyway

The continuation store entry for `bind-the-refuted-knee-...` carries `written_at` **12:06:39** and
a `done_means` of `seat_executor.AUTO_PROMOTION_DONE_MEANS` — *"DERIVED, NOT DECLARED — this entry
was promoted automatically by seat_executor at derivation"*. So `seat_executor._promote_to_handoff`
re-derived the identical focus item fourteen minutes after the commit that finished it, and seven
minutes after the tick that did the work wrote its successor. The 12:06:22 worker tick was
dispatched on it. That is this invocation.

## Why the guard that exists for exactly this could not fire

`delivery_lane.hand_off_focus` already carries the repair for this class, added 2026-09-06 under the
heading *"A FINISH SURVIVES THE RE-DERIVATION THAT PRODUCED THIS ROW"* — and its own comment records
the same symptom being measured on its own doorbell, *"promoted again seventeen minutes after the
commit that satisfied it"*. Ours was fourteen.

It refuses when `seat_continuation.retirement_orientation(focus_id) == current_orientation()`.
Measured now:

```
current_orientation:                     2026-09-24T08:20:24.244165+00:00   (in force since before the 11:36 draw)
retirement_orientation(bind-the-...):    None
'bind-the-...' in seat_continuation.retired():  False
```

**The guard is keyed to `--release`, a call a session must remember to type.** The 11:36 tick did
everything the lane insists on — it landed, it ran `--landed` "IMMEDIATELY AFTER EACH COMMIT" as the
doorbell demands in capitals, it stated `--premise-spent` for the subject row, it wrote a successor
— and no retirement was ever recorded for its own id. One missed call out of five, and the item came
straight back round with a fresh six-hour window.

Which of the two ways that happened is NOT established, and the difference does not change the
remedy. Running `--release` from this turn printed *"released NO CLAIM … it is NOT CLAIMED here"*,
whose own text names both readings: the tick released the claim without the retirement landing, or
it never claimed at all and "the work was done unclaimed and the lane could not see it move". The
worker-tick log is consistent with the second — its `lane-0 claim taken at dispatch` line for
10:36:32 UTC names `the-refuted-bill-stress-knee-…`, the subject, not the bind id. Either way the
flag the guard reads was absent while the ledger fact was present.

So the retirement flag and the ledger disagree, and the guard reads the weaker of the two:

- `retired_at_orientation` — written by a **session**, if it remembers, at the end of a turn.
- `last_landing_at > last_drawn_at` — written by **`--landed` from `git show`**, at the moment the
  commit lands, by the one call this lane already makes non-optional.

The second is the stronger fact and it is already in the store the guard is standing next to.

## The remedy — one leg, and its polarity

`hand_off_focus` should refuse a re-promotion when the focus id's **own** draw-ledger row carries a
landing bound inside its most recent window — `last_landing_at > last_drawn_at` — with the same
shape of refusal the retirement check already raises. Fail-open on an absent or unreadable ledger,
matching `current_orientation`'s own rule that every uncertainty answers None and no caller refuses
on it.

**The polarity is the whole trap and it inverts the lane if it is got wrong.** The check must NOT
refuse when `last_landing_at` is `None`, or is `<=` `last_drawn_at`. That is the *unbound* case —
work drawn and not landed, or landed before the window opened — and re-offering it is the entire
reason Lane 0 exists. A guard written as "has this row ever had a landing?" would silence the lane
on exactly the rows it is for. Key it to the two instants' **order**, never to the presence of a
landing.

A control over this wants both sides of the partition asserted on ONE row — the same row reads
promotable with `last_landing_at` before `last_drawn_at` and refused with it after — or a guard that
refuses everything passes every leg. And mutation-prove that an unreadable ledger leaves the
promotion **working**, not refused.

## Why this is NOT the live successor, which I read before writing

`ask-the-landed-unbound-join-before-the-draw-not-only-after-the-sweep` (written 11:59:36, live,
unclaimed) asks a different question of a different store: *does a row's named paths carry a newer
`origin/main` commit than anything bound to it* — a `rev-list`/`diff` join, for work that landed and
nothing bound.

**It would not have stopped this dispatch.** Asked of the bind row just now: the newest
`origin/main` commit on its three bound paths IS `8379e8e0e`, which is what `last_landing_at` names.
Nothing is unbound; the join reads clean. This row's defect is the opposite one — everything was
bound correctly and the promotion route never asked. That check needs no git at all: both instants
are already in the row.

The two are complementary and the successor should not absorb this leg silently.

## Not fixed here, and why

`background/delivery_lane.py` is **10 commits behind `origin/main` in the shared checkout** and the
working copy is clean at that stale HEAD — so `landing_predates_this_window`, landed at 11:52, is
not in the bytes any daemon in this tree is running. Editing the file here would revert `8379e8e0e`.
The honest door is a worktree based on `origin/main` plus `promote_worktree_landing`, which is a full
extra gate cycle, and the checkout itself is already held by a live claim
(`the-checkout-fast-forward-is-blocked-on-two-contested-files-not-on-a-judgement`, contested paths
`background/supervisor.py` and `site/test_the_book_is_bounded_by_compute_reaches_the_reader.py`).

So the remedy is specified above rather than built, and the disposition is taken instead. This id
was `--release`d from this turn, which arms the existing `retirement_orientation` guard under the
orientation still in force and stops the 12:36 derivation minting it a third time. Measured after
the call:

```
retirement_orientation('bind-the-refuted-knee-...'):  2026-09-24T08:20:24.244165+00:00
current_orientation():                                2026-09-24T08:20:24.244165+00:00
```

That holds only until the seat next orients, and only for this one id. It is a plaster on the
instance; the leg above is the fix for the class.

**An ordering caveat, paid for in this turn.** I ran `--release` BEFORE landing, to disarm the 12:36
derivation before it could fire. The cost is that the `--landed` afterwards bound nothing —
*"bound NOTHING … it is NOT CLAIMED -- nothing holds a deadline for it"* — because a released row
has no claim to inform. The doorbell's own sequence is land → `--landed` → `--release`, and it is in
that order for this reason. Nothing was lost here: the row was ALREADY settled in its own window by
`8379e8e0e` (`last_landing_at` 11:52:31 > `last_drawn_at` 11:36:43), so the ledger reads correctly
either way. But a reader taking this disposition on a row that is NOT already settled would release
it, find the bind a no-op, and leave the lane blind to the very landing it was recording — which is
this finding's own subject wearing the other face.
