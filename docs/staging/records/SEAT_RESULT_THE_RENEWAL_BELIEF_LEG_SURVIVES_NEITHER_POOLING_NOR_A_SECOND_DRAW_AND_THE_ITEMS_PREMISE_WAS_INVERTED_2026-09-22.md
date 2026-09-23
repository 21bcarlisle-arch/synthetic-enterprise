**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `renewal-churn-belief`

# The renewal-belief leg survives neither pooling nor a second draw, and the item's own premise was inverted

*Lane 0 delivery, claim `the-headline-belief-reading-earns-its-two-missing-controls`. Both controls
were built and both came back negative. The page's most direct claim about what the company knows
is a property of one stratification choice and one roll of the dice.*

Landed: `13b02eafd` (control a), and the commit this document lands with (control b).

---

## The drawn item's premise was refuted, and the defect it was drawn for is real from the other side

The item asked for *"the WITHIN-YEAR decomposition its 384 pairs do not carry"*, reasoning that a
pooled AUC on this book is substantially a year effect and that this page withdrew a claim on
2026-09-10 for exactly that shape.

`measure_churn_heterogeneity.report` computes **every** reading inside `by_year_and_route`
(`within_strata_auc`'s default stratum; `belief_readings` is handed route-filtered rows, so within a
route it collapses to year-only). The renewal route's 384 pairs already **are** same-year pairs and
the published 0.6706 is already the within-year figure. **The twin that was missing is the pooled
one** — the same defect mirrored, and the direction matters because the numbers disagree.

## (a) It does not survive pooling

Committed capture, world `39a192ce04c1eda8`, 102 renewal decisions, 41 departures:

| reading | within-year (published) | pooled |
|---|---|---|
| `company_churn_estimate` | **0.6706** | 0.5940 |
| the world's own hazard (the ceiling) | **0.5911** | 0.6717 |
| pairs | 384 same-stratum | 2,501 comparable (15.4%) |

Stratifying moves the belief **up** and the ceiling **down**, and they **cross**. The block's
headline verdict — `the_belief_ordered_these_departures_and_the_world_did_not` — holds within-year
and **reverses** pooled.

## (b) It does not survive a second draw

Same world, same record, same tariffs, same hazards, same company code. Only
`churn_roll_for_renewal` was replaced, by a substitute drawing from the same uniform distribution on
a different stream (`capture_departure_factors --roll-seed 20260922`). Nothing about the world
moved; only which side of its own hazard each household landed on.

| | draw 1 (production) | draw 2 (roll seed 20260922) |
|---|---|---|
| decisions / departures | 102 / 41 | 138 / 42 |
| `company_churn_estimate` | **0.6706**, null [0.3685, 0.6328] → **clears** | **0.5847**, null [0.3928, 0.6216] → **does not** |
| the ceiling | 0.5911, null [0.362, 0.638] → does not clear | 0.6486, null [0.382, 0.618] → **clears** |
| verdict | the belief ordered them, the world did not | **the exact mirror** |

Never averaged: two AUCs over two different books have no mean that describes anything. The books
differ in size because who leaves decides who reaches a later renewal — a property of the world, not
a fault in the control.

**The answer the item asked for is "it does not hold".** The first draw's clear is 0.038 wide on 384
pairs, and a permutation null cannot speak to this: it asks whether this *ordering of these fixed
rows* could have arisen by chance, never whether these rows would have come out this way again.
Same shape as `SEAT_FINDING_THE_NARROW_WIDTH_BEHIND_THE_PUBLISHED_SELECTION_SIGN_IS_A_REPEATED_DRAW_2026-09-22`,
one surface over.

## What the page now says

Both clauses are in the **headline `sentence`** — the one bold line of the panel — not in a
footnote, and both are derived from the figures rather than typed:

> ... It is computed only between decisions taken in the same year and on the same route — 384 of
> the 2,501 comparable pairs on this route, 15%. **AND IT DOES NOT SURVIVE POOLING** ... **AND IT
> DOES NOT SURVIVE A SECOND DRAW.** Rolling the same world's renewal dice again — nothing else
> changed — the belief reads 0.5847 inside its null against a ceiling of 0.6486 that now CLEARS:
> the exact mirror of the first draw ... Which of the two orders these departures is decided by the
> roll, so across draws we cannot tell.

Keyed to the property throughout: `the_verdict_survives_pooling` and `the_leg_holds_across_draws`
are derived comparisons, and the repeat grades are found by **glob**, so a third draw reaches this
surface without anyone editing the producer.

## What a reader of this should act on

1. **The claim is withdrawn, not tuned.** Nothing here is an instruction to make the belief
   discriminate. A belief that cannot order its departures reproducibly is a complete answer.
2. **`background/process_run_complete` regenerates `site/data/value_arms.json` from the WORKING
   TREE.** The shared tree's `docs/observability/svt_drift_belief_grade.json` and
   `docs/reports/ladder_churn_factors.json` both **predate their own landings** (mtime 08-31 and
   09-22 10:24 against a 09-22 20:09 commit) and are another lane's stale reverts. `refresh_to_head`
   refuses them. While they sit there the new blocks fail closed and publish their re-take commands
   instead of the figures — correct, but not the published reading. **Clearing those two reverts is
   what puts these figures on the page.**
3. **A third draw is cheap now** and would say whether draw 2's ceiling-clears/belief-doesn't is
   itself reproducible. The mechanism is landed; one command.
