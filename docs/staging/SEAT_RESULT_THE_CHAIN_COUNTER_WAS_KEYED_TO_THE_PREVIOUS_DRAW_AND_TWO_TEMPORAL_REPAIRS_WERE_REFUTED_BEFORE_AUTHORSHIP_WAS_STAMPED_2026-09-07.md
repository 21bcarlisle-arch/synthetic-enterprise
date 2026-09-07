**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the self-issued hand-off chain counter)

# The chain counter was keyed to the previous draw, and two temporal repairs were refuted before authorship was stamped

*Seat, 2026-09-07. Lane 0 delivery, drawn ahead of the dial-weighted lanes.*

## The defect, measured

`SELF_HANDOFF_CHAIN_LIMIT = 3` landed 2026-09-06 so the seat's ranked list gets a hearing ahead of
a lane feeding itself. On the first stretch after it the lane drew **six consecutive self-issued
continuations** and `_self_issued_chain` returned **1**. The swap never armed.

The link test asked whether a continuation's `source_written_at` was later than the instant the
item drawn **before it** was handed out. That credits a lane writing exactly one hand-off per turn.
This lane runs **two programmes interleaved**, so the row before is not the parent:

| row (newest first) | written | drawn |
|---|---|---|
| `W2_18-the-frame-has-no-scottish-region` | 748014 | 748577 |
| `a49-builds-the-r3-and-r4-ceiling-instruments` | 744124 | 747128 |
| `W1_14-cut-the-artefact-over-the-drawn-population` | 743284 | 746814 |
| `a49-decides-which-rung-gates-r3-and-r4` | 740951 | 743313 |

`a49-builds` was written at 744124 by the tick holding `a49-decides` (drawn 743313) — self-issued,
two rows back. Against the row *immediately* before it (`W1_14-cut`, drawn 746814) it reads as
"came from somewhere else". A continuation written earlier and drawn later is exactly what a queue
the lane feeds itself produces, and it was the one shape the counter could not see.

## Two temporal repairs, both refuted, both recorded

**(1) Key the link to WRITE ORDER** (`newer` written after `older` was written). Counts the backlog
correctly — and also counts a BATCH, one interactive session writing four hand-offs seconds apart,
which is the case the continuation-first order exists for.

**(2) Add a run ANCHOR** — "the newest write lands after the run's oldest draw". Green against the
existing fixture. Then the production shape was tried: a four-row batch on top of six rows of
history counted **9**. With history behind it the run reaches back to an ancient draw, the anchor
passes, and the batch is credited. *The fixture was what passed, not the mechanism* — the old batch
test used an empty ledger and identical write instants, neither of which the live ledger (94 rows,
writes seconds apart) ever produces.

Both were written, tested, and deleted. Recorded here because a repair that was refuted is worth
more next to the one that replaced it than quietly dropped.

## What landed

Authorship is **stamped at write time**, because it is not recoverable afterwards. A tick holds a
delivery-lane claim while it works; the interactive seat claims in a different store and holds
none. So `seat_continuation.hand_off` records `written_while_holding`, `record_draw` copies the
answer onto the ledger row as `source_self_issued`, and `_self_issued_chain` reads nothing else.
A batch breaks the run wherever it sits, with or without history; an interleaved backlog counts
however far its parent is from the row before it.

**It is inert on rows drawn before the stamp existed** — they carry no authorship and read as not
self-issued, so the chain is 0 until the ledger refills. That is the fail-safe direction (the
continuation source keeps today's priority) and it self-corrects within four draws. Stated because
the fix will *look* like it is not working for its first few ticks, and a reader who does not know
that will re-open it.

## What it still cannot see

The stamp asks whether *anything* was in hand, not *who* held it. A session writing a hand-off
while a tick happens to hold a claim is credited as self-issued. The cost is bounded and is not the
feared one: `next_item` **swaps** the two sources and never suppresses either
(`test_a_chained_lane_STILL_GETS_ITS_CONTINUATION_WHEN_FOCUS_IS_EMPTY`), so an over-count defers a
continuation behind a non-empty focus list for one draw and cannot idle the lane.

## Controls

`tests/background/test_a_self_issued_handoff_chain_yields_to_focus.py`, poison round first. New
legs: the interleaved backlog reaching the limit *and* the swap firing on it; the batch refused
**on top of real history, with distinct write instants**, plus a non-vacuity assertion that the
batch actually reached the head of the ledger — the first draft read 0 because the batch was never
drawn at all, which would have passed every mutation.
