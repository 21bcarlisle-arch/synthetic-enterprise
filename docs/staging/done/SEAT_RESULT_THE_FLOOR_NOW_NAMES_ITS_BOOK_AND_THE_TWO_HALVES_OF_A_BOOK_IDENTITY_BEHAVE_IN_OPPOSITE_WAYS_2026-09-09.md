**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — grade the per-leg conditioning pre-registration) · **Class:** controls_that_cannot_fail

# RESULT — the floor names its book, and the two halves of a book identity behave in opposite ways

Discharges the *"what is still owed, and it is the actual repair"* section of
`SEAT_FINDING_THE_NOISE_FLOOR_CARRIES_NO_BOOK_IDENTITY_SO_THE_PAIRING_RULE_IS_A_STAMP_PROXY_WRONG_IN_BOTH_DIRECTIONS_2026-09-09.md`.

## The drawn item's own premise, re-measured first

The Lane 0 draw asked for P1–P6 to be graded against the first three-arm run carrying
`method_skill.fixed_horizon.leg_conditioning`. **That is spent and landed**: `4e393cf563` filed
`SEAT_RESULT_ALL_SIX_LEG_CONDITIONING_PREDICTIONS_HOLD_AND_PUBLISHING_THE_RUN_ALONE_WOULD_COST_THE_PAGE_EVERY_DIRECTIONAL_BOUND_2026-09-09.md`
— six for six, including P5's (37, 40, 3). The draw's remaining leg, *publish the run and check the
column renders*, was **deliberately declined by that turn** and the decision is on the record: Q5
measured that promoting the run alone takes `contrast_bounds` from `available: True` to `False`,
which is what every directional claim on the page is gated on. Ten bounds lost, three gained.

So the item's remaining work is blocked, on purpose, on two runs that are still in flight at the
time of writing:

```
longjob-arms-rerun-20260909b        active 4h53m   -> value_cycle_ab_s1_noise_floor_20260909b.json  (9 seeds)
longjob-three-arm-legcond-20260909c active 38m     -> value_cycle_ab_s1_three_arm_20260909c.json
```

Neither artefact exists on disk yet. Nothing in this turn touches the promotion.

## What was done instead, and why it is the same item

The finding's own closing paragraph names the repair that **retires** the proxy rather than
patching it again, and states why it was not done: it needs a floor re-run. That is a reason not to
*re-measure* today; it is not a reason not to *land the producer*, because the producer change is
what any future floor needs in order to carry the fact at all. Landed now, the two runs in flight
are the last floors that will ever be unpairable-by-construction.

`tools/run_value_cycle_ab.py::noise_floor` now stamps `book_identity` onto its artefact,
reconciled across the floor's own seeds by `floor_book_identity`.

### The measurement that shaped it: a book identity has two halves and they behave oppositely

This is the part that was not obvious and is the reason the repair is not a one-line copy of the
three-arm block. A noise floor re-runs **the same book once per seed**, and the only thing it
varies is the elasticity assignment — which moves who churns, and therefore who settles. So:

| half | fields | across seeds of one floor |
|---|---|---|
| **declared** — what the run was *given* | `served_segments`, `..._resolved_from`, `..._override_env` | identical by construction |
| **realised** — what the seed's churn *did* | `billing_accounts_settled_in_window`, the fuel legs, `dual_fuel`, `accounts_at_end_of_window` | **differs by construction** |

A rule that compared the whole block would refuse **every honest floor ever produced**. A rule that
compared none of it is the stamp proxy again. Both errors are one edit apart from each other, which
is why `test_seeds_whose_REALISED_counts_differ_are_the_normal_case_and_not_a_mixed_floor` asserts
both directions in one place — the declared half survives a churn difference *and* the range is
published rather than reconciled. Widening the key to the realised fields kills that leg; the
obvious repair to make it pass again is loosening the key until the declared half falls out of
scope, and the test says so in its own body so the next reader meets both sides at once.

The artefact says it too, on itself: `how_a_consumer_should_pair_this` — *"Pair on `declared` and
never on `realised_across_seeds`"* — so the rule does not live only in a test the consumer's author
may never read.

### The three refusals, and which way each fails

1. **Seeds drawn over different books** → refused outright, same argument the `clock` reconciliation
   one block up already rests on: repeated draws over two populations are not repeated draws of one
   quantity, so no error bar can be taken from them.
2. **Any seed that recorded no book** → `declared: None` with `unavailable_because` naming *n of m*.
   Fails closed. Taking the book from the seeds that did declare would pair the whole spread on a
   book part of it never ran over — and the part that did not is exactly the part a reader cannot
   check.
3. **Every seed silent** (every floor on disk today, and both in flight) → the same `None`. The
   consumer's inability to pair on the book is stated on the artefact rather than inferred from a
   missing key.

The world digest is **not** this and the code says why: the digest is the departure level, and the
book can change without it moving — which is the 2026-08-31 defect the ordering guard was extended
for. Two questions, two fields, asked separately.

## Controls: six mutations, six kills, no survivors

Reachability over the whole partition asserted **first**
(`test_the_book_block_can_be_populated_AND_withheld_over_the_whole_partition`), because a producer
that populates nothing passes every "it withheld correctly" leg and one that populates
unconditionally passes every "it named the book" leg, and neither is separable from the working
mechanism without a control over both.

| mutation | killed by |
|---|---|
| drop the mixed-book refusal | `..._DIFFERENT_books_are_refused_rather_than_reconciled` |
| widen the key to the realised fields | `..._REALISED_counts_differ_are_the_normal_case` (+1) |
| pair on the seeds that *did* declare | `..._PARTIAL_record_does_not_pair_on_the_seeds_that_did_declare` |
| never populate the block | 5 legs, reachability first |
| drop the per-seed count the range is taken over | `..._each_seed_row_carries_the_book_size_...` |
| read `value_arm` where the consumer reads `control_arm` | 6 legs |

`tests/tools/test_value_cycle_ab_noise_floor.py` 43 passed;
`tests/tools/test_run_value_cycle_ab.py` + `tests/tools/test_generate_value_arms_data.py`
326 passed. **No mutation survived, so nothing is recorded here as an equivalence.**

## Two things this does NOT do, stated because both look done from the outside

1. **`_seed_spreads` does not yet pair on the book.** The consumer half is what actually retires the
   stamp proxy, and it cannot be written honestly today: **no artefact on disk can reach the branch
   that would read a floor's `book_identity`**, because no floor carries one until the next re-run.
   Writing it now would create a second instance of the exact class the same turn filed as a thread
   to pull — *a branch a landed producer cannot reach from any feed*. The producer half is the half
   that has to come first, in that order, and this is why.
2. **Nothing on the live page moves.** `docs/observability/value_cycle_ab_s1_noise_floor.json` is
   untouched; `contrast_bounds` still reads `seeds: 3` and `available: True`; the caveat's composed
   clause from the same finding is unchanged. The floor's severity was LATENT for that reason and
   still is.

## What is next

1. **The pair promotion** when the two jobs above land, as
   `SEAT_RESULT_ALL_SIX_LEG_CONDITIONING_PREDICTIONS_HOLD...` sets out: floor and three-arm to the
   canonical paths **together**, plus `CURRENT_WORLD_NOISE_FLOOR_PATH` — three pointers, per
   `SEAT_FINDING_THE_NINE_SEED_FLOORS_STATED_PUBLISH_PATH_DOES_NOT_REACH_THE_LEG_THE_RUN_EXISTS_TO_SETTLE_2026-09-09.md`,
   not one file copy.
2. **`_seed_spreads` pairs on `declared`** the first time a floor carries one — refusing a floor
   whose declared book is not the figure's, and *dropping* the caveat's "cannot be shown to have
   been drawn over the decisions this figure is made of" clause when it is. That is the direction
   the stamp rule gets wrong today in the flattering direction, and it is one turn's work once
   there is a feed that can reach it.
3. **The floors in flight will be the last unpairable ones.** Worth saying out loud so the next
   session does not read their `declared: null` as a defect in this repair.
