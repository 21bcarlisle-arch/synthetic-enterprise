# The roster and the world draw a household's payment method on two independent streams, and they agree for 60% of households

**Fate (2026-10-26):** DONE -- e35ce23f6 made the roster read the world's channel; re-graded in `SEAT_RESULT_B8_THE_HOLDOUT_RE_GRADED_ON_ONE_PAYMENT_METHOD_2026-10-26.md`: pooled unchanged to the digit, and the world's true per-channel effect differs by 0.0001, so there was no difference to dilute.

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (found closing cold-read item 6 of the switching and payments pages)

*Delivery seat, 2026-10-26.*

## What was measured

`simulation/population_draw.py` writes `payment_method` on each roster customer: `"direct_debit"`
with probability 0.72, else `"other"` (line 555, its own cohort substream).
`simulation/household_segments.payment_channel_for_customer` draws the method again: 0.72
electricity / 0.75 gas direct debit, the rest split 50/50 prepayment and standard credit, on stream
`paychannel_<household>_electricity`. This second draw is the one the world's payments run on
(`simulation/arrears_engine.payment_method`) and the one the company is told
(`LiveSimInterface.get_payment_method`, read by the debt objection at `run_phase2b.py:4440`).

`draw_population(42, acquisitions_per_year_lambda=500)`, 2,435 households, roster label against the
electricity channel:

| roster \ channel | direct_debit | prepayment | standard_credit |
|---|---|---|---|
| direct_debit | 1,270 | 246 | 243 |
| other | 481 | 94 | 101 |

Agreement on DD/non-DD: (1,270 + 195) / 2,435 = **60.2%**. Two independent draws at 72% give
0.72² + 0.28² = 59.7%. The two labels are independent.

## Why it matters

The roster label reaches `simulation/coin_drawn_decision_set.py`'s rows (`"payment_method":
c.payment_method`), and `company.pricing.discovered_price_sensitivity.estimate_offer_effect_by_channel`
groups by it in `tools/grade_coin_drawn_holdout.py`. A "per payment method" offer effect is read
on a label that is, for 40% of households, not how they pay in the world. A per-channel difference
there is therefore diluted toward none. It is not wrong in the sense of being biased toward a false
effect, but it cannot find a real one.

## Proposal

Make the roster's `payment_method` read `payment_channel_for_customer` (or delete the field and
have the decision set ask it), so a household has one method. The coupling note in
`household_segments.py` (2026-09-29) already rejected a migration *the other way* because it would
reshuffle 41% of the book. That argument does not apply here: no world payment runs on the roster
label. Before changing it, re-grade `tools/grade_coin_drawn_holdout.py` with a prediction written
first: the per-channel effects separate more than they do today, and the pooled effect does not move.

The payments Knowledge page now says this (theory, "What the simulated world does").
