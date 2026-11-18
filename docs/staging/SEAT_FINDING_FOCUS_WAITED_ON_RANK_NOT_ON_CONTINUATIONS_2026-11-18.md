**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `focus-outranks-a-continuation-chain-of-any-author`)

# The 17–18 Nov focus wait was not caused by continuation chains. Replaying the new any-author leg shows no focus draw it would have brought forward (2026-11-18)

*Claim `focus-outranks-a-continuation-chain-of-any-author`. The leg landed anyway because it closes
a real hole: `_focus_waited_through` in `background/delivery_lane.py`, controlled by
`tests/background/test_focus_outranks_a_continuation_chain_of_any_author.py`.*

## What the item predicted

The item's premise: focus "has gone undrawn through four records", and focus reached the draw once,
behind two queued continuations. So a leg that counts continuation draws of any author since
`oriented_at` should have drawn focus earlier.

## The replay

Draws come from the `RUNNING` lines in `seat-executor-log.md`. Each draw's source comes from the draw
ledger. `the-claude-md-trial-...` has dropped out of the 400-row ledger, so it is read as focus: it
was `focus[0]` in the 18:22 record and was promoted at 18:26. Records come from the git history of
`DIRECTION.yaml`. Limit 3.

| draw | record | run before the draw | leg armed? | drawn |
|---|---|---|---|---|
| 15:26, 16:56 | 15:22 | 0 | no | d5 book (focus; **corrected:** a continuation, see below) |
| 18:37, 20:07 | 18:22 | 0 | no | d5 book (focus; **corrected:** a continuation, see below) |
| 20:58 | 18:22 | 0 | no | claude-md trial (focus) |
| 21:05 | 18:22 | 0 | no | row7-three-leavers (continuation) |
| 22:26 | 21:20 | 0 | no | walk-counter (continuation) |
| 22:55 | 21:20 | 1 | no | row7-graded (continuation) |
| 23:15 | 21:20 | 2 | no (yes at limit 2) | retention-offer-gate (focus; the self-issued leg was already armed) |
| 23:25 | 21:20 | 0 | no | row7-grade-when (continuation, not self-issued) |
| 23:36 | 21:20 | 1 | no | retention-threshold (continuation) |

**Answer: none.** The leg would not have drawn any focus item earlier. At limit 2 it arms only at
23:15, and focus was drawn at 23:15 anyway.

## What actually kept focus waiting

- **Rank and cadence.** Five of the eleven draws were focus draws. The d5 book alone took four of
  them, each about 90 minutes long. `focus-outranks-...` sat at `focus[2]` or `focus[3]` in every
  record, behind items that were being drawn.
- **Filters, not order.** `the-contact-cause-steer-...` was `focus[0]` of the 15:22 record and was
  never drawn: `_focus` skipped it, and `d5` (`focus[1]`) won. That is a held, finished or stretch
  refusal, not the source order. Its skip note would name which one.
  **Corrected 2026-11-18:** wrong on both counts. D5 was promoted to a continuation by the 15:17
  stand-down, so `_continuation` won before `_focus` was asked, and the steer itself was landed by
  the 15:26 D5 tick through the advisor rung-zero prefix (6f0b5eb1c). See
  `SEAT_FINDING_THE_D5_ROW_TOOK_FOUR_TICKS_BECAUSE_TWO_OF_THEM_ONLY_WAITED_2026-11-18.md`.

## What follows

The leg stays, because it closes a gap that does exist: a batch written by an interactive seat
never arms the self-issued leg. But it was not this stretch's bottleneck. The next lever is
throughput per focus row, not ordering. The question to answer is why one focus item absorbed
four 90-minute ticks under two records.
