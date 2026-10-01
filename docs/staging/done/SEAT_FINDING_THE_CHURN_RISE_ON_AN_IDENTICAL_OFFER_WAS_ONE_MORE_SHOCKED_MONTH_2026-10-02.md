**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity` — Lane 0 delivery

# The churn rise on an identical offer was one more "shocked" month, and both were bills that fell

Claim `trace-the-churn-hazard-term-that-carries-price-history-into-a-renewal`. It follows
`SEAT_FINDING_THE_LOOK_AHEAD_FIXS_MARGIN_RISE_IS_THE_PORTFOLIO_PREMIUM_..._2026-10-01.md`, which left
"which term in `build_churn_risk` does this" untraced.

**Premise check.** The two cited commits are on origin. That says the arms' code landed. It says
nothing about the untraced mechanism, so the premise was not spent.

## Answer

The term is `saas.churn_model.build_churn_risk`: `p = 0.05 + 0.03 × k`, where k counts the months in
the 12 before the renewal whose household bill differs from the same month a year earlier by more
than 15%. **The test uses `abs()`.** For each customer, `new` added exactly one month to k. **In
both cases it was a bill that fell.** The 2023 bill was identical in both arms. Only last year's
reference changed: `new`'s higher 2022 Q4 electricity rate (£568 against £469/MWh) raised it, so
the same 2023 bill now read as a drop of more than 15%.

| customer, renewal | month | 2023 bill (both arms) | 2022 reference old → new | score old → new | k old → new |
|---|---|---|---|---|---|
| PROS-2022-0010, 2024-01 | 2023-11 | £138.68 | £153.59 → £174.33 | 0.097 → **0.205** | 8 → 9 (0.29 → 0.32) |
| PROS-2022-0097, 2024-03 | 2023-10 | £147.72 | £153.76 → £175.08 | 0.039 → **0.156** | 4 → 5 (0.17 → 0.20) |

The months moved in the other direction do not offset this. In 2023 Q1, gas was dearer under `new`
(£209 or £224 against £185/MWh), but those months were already scored at 2.4 to 11 against a
threshold of 0.15, so they were saturated. In 2023 Q2, the higher 2022 reference shrank real rises
(0.859 → 0.749), but every one stayed above 0.15.

## Pre-registered against what came back

Written to `/var/tmp/se-churn/PREDICTION.md` before either arm ran (kept with the probe and both
JSONs in `/var/tmp/se-churn/keep/`). Arms: `65401d319` and `cd0c7c39c`, one default world each.
`build_churn_risk` was wrapped in `simulation.customer_events` and recomputed the yoy signals for
just these two households at their own renewal months.

| | prediction | result | |
|---|---|---|---|
| P1 | exactly one more shocked month each | +1 each (8 → 9, 4 → 5); reproduces 0.29 → 0.32 and 0.17 → 0.20 | holds |
| P2 | PROS-2022-0097's month is in 2023 Q4 and is a fall | 2023-10, −15.6% | holds |
| P3 | PROS-2022-0010's month is a 2023 Q4 fall, not a 2023 Q1 gas rise | 2023-11, −20.5% | holds |

## Is the 3-point uplift evidenced?

**No. It is a number someone picked.** `CHURN_UPLIFT_PER_BILL_SHOCK = 0.03` and the 0.05 base carry
no source. The domain-constant scan does not see the uplift, because its name contains none of the
five words the scan matches on. The base was in the unsourced-debt baseline with origin `None`.
`docs/market_research/does_a_bill_shock_event_raise_the_odds_a_household_shops.md` searched for
this exact amplitude, P(shop | shock) / P(shop | no shock), on 2026-09-29: **not established**.
The world's engagement leg holds the same amplitude as an honest `None`
(`household_segments.BILL_SHOCK_ENGAGEMENT_MULTIPLIER`) and refuses. The hazard leg asserts it:
1.6× on the bill-shock base, now that `year_level_anchor` sets the level.

The question asked was "is a +3pt churn hazard from past rates 15–20% higher evidenced?". It is a
category error twice over:
1. It is not a price response. It is a fall, read as a shock by `abs()`. Every trigger in
   `what_bill_shock_is.md` is a rise.
2. Even for a rise, the per-month count and the 3 points are unsourced.

## What this changes

- **The world's push-back against the premium was mostly an artefact.** Of the £1,235 lost in the
  look-ahead pair, £1,020 (PROS-2022-0010 and -0097) came from bills that fell. Only £215, the
  SYN-2016-001 knife-edge decided by the higher offer, was a response to price. So the "13%
  give-back" overstates the world's price response by about 5.7×. Measured against the £9,154
  transfer, the true give-back in that pair was **about 2%**. A correction sits beside the claim
  in the look-ahead finding.
- **At HEAD this term no longer drives the hazard.** The PB4 swap (`c3939e7b1`, 2026-10-01)
  replaced the month count with one experienced shock a year, and
  `simulation/experienced_bill_shock.py` states "A FALL IS NOT A SHOCK". The defect traced here is
  therefore already retired, as a class. It is not a live bug. It still rides on every event as
  `sim_month_count_bill_shock_base`, which is informational.
- **What is still live is the amplitude.** The 0.03 / 0.05 pair now sets a 1.6× shocked/unshocked
  ratio on the base. That is the same quantity the engagement leg refuses to price. In this commit
  both constants are labelled a named simplification in `saas/churn_model.py`, which takes the base
  out of the unsourced debt. No number was changed: a replacement would be picked for what it does,
  and nothing published supplies one.
- **Whether the world can defeat a premium** is now a question about the contemporaneous price leg,
  `offer_position_multiplier` (the mirror of the win side), and not about bill-shock history. The
  look-ahead pair cannot answer it at HEAD. Retaking the pair on a post-swap tree would measure it.
  Not done here; it is two 24-minute arms, and it is worth filing only if the premium question is
  reopened.
