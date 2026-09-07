**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — drawn and never landed)

# Two finished repairs reached origin, and the ledger fact that would have caught them now reaches the orientation

*Seat, 2026-09-07. Lane 0 delivery.*

## What was wrong

Two Lane 0 items were drawn, done, tested, correct — and never committed.

| id | drawn | landed |
|---|---|---|
| `the-lane-0-chain-counter-reads-1-across-four-consecutive-continuation-draws` | 04:11 | — |
| `six-dd-level-collection-controls-are-red-at-head-and-are-still-red-at-this-orientation` | 04:41 | — |

Both sat in the shared working tree through four orientations. `record_draw` had written each a
`first_drawn_at`; `_remember_landing` never wrote either a `last_landing_at`. **The whole finding
was on disk in `docs/observability/.delivery_lane_claims.draws.json` hours before anybody noticed,
and nothing read it.**

`sweep_stale` returned both claims to the pool at 100 minutes, correctly and silently, which is the
only thing that happens to a window that closes empty.

## The landing

`ee3498cc0`, merged to origin as `2c4f91b48`. Both repairs verified present at `origin/main`.

- **The chain counter.** `_self_issued_chain` keyed the link to the PREVIOUS DRAW, which credits a
  lane writing one hand-off per turn and misreads a lane working through its own backlog: six
  consecutive self-issued continuation draws, counter returned **1**, the swap never armed. Two
  purely temporal re-keyings were tried and refuted (write-order counts a batch; the empty-ledger
  anchor that repaired the batch case counted **9** over real history — the fixture passed, not the
  mechanism). Authorship is now **stamped at write time** by `seat_continuation.hand_off`
  (`written_while_holding`) and copied onto the row by `record_draw` (`source_self_issued`).
  Inert on rows drawn before the stamp existed, which is the fail-safe direction.
- **The DD level collection book.** `build_dd_balance_book` stopped opening customers from their
  first issued bill on 2026-09-02, taking the suite to 6 failed / 4 passed. Two of the four
  survivors assert an ABSENCE and were passing **vacuously over an empty book** — any upstream
  refusal made `n_customers == 0` true for every input. Both now assert a presence alongside the
  absence.

## The hole, closed

`background/delivery_lane.drawn_without_landing()` — Lane 0 ids whose most recent draw is inside a
24-hour horizon, whose claim window has closed, and which have **no landing bound at or after that
draw**. Keyed to the draw, not to `last_landing_at` being null: an id drawn, landed, and drawn again
carries a landing instant that a null test reads as healthy, and its second window is exactly as
empty as a first one.

It reaches the seat by three legs, because a key inside a 60k-truncated JSON dump is not the same
thing as a sentence:

1. `build_brief` carries it as the **second** key, ahead of `commits`, out of the truncation's reach;
2. `is_material` returns True naming the ids — placed with the machine faults, above the
   "did something happen" clauses, because a lane that is drawing and producing nothing is invisible
   to the commit count;
3. `_prompt` prints them **above** the JSON, telling the seat the work may already be on disk and to
   check `git status` before starting anything new.

Horizon is a day, not a stretch: three hours is shorter than the fact is interesting, and an item
drawn at 04:11 falls out of a stretch-scoped read by the 08:00 orientation.

## Reachability

`tests/background/test_a_drawn_item_that_landed_nothing_reaches_the_next_orientation.py`, 9 passed.
**Poison round run before the claim**, seven mutations, every one fires:

| mutation | result |
|---|---|
| drop the window clause | 3 failed |
| key the landing to `last_landing_at` being null | 1 failed |
| drop the horizon | 1 failed |
| report every row | 2 failed |
| delete the `is_material` clause | 1 failed |
| move the prompt sentence below the JSON dump | 1 failed |
| drop the brief key | 1 failed |

Baseline re-run green after each. The 2026-09-07 leg replays the two real draw instants at 06:00,
between the two windows closing, so it is a discriminator rather than a count.

## What this surfaced that I did not fix

The live reading at the time of writing names **six** ids drawn in the last day with no landing, not
two. Four of them are other lanes' — `the-decision-instrument-is-electricity-only-on-a-book-that-is-half-gas`,
`the-four-contradicted-rows-move-or-the-check-that-named-them-is-wrong`,
`the-level-zero-check-is-blind-to-twenty-nine-of-the-rows-it-grades`, and a row literally keyed
`some-id`, which is a **test fixture id that has leaked into the live draw ledger**. Each is now
visible to the next orientation rather than to nobody; that last one is a separate defect and is not
touched here.
