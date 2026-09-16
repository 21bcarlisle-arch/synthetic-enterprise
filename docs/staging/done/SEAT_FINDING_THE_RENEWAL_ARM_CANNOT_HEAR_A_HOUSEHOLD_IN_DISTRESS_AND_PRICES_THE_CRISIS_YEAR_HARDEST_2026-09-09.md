**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — find where the renewal rule prices up the households it then loses) · **Class:** controls_that_cannot_fail

# FINDING — `max()` makes exactly one churn channel live, so the arm cannot hear a household in distress, and prices the crisis year hardest

Reproduced at HEAD by `python3 -m tools.renewal_rule_price_response`. Measured and graded in
`docs/staging/SEAT_RESULT_THE_ARM_PRICES_UP_A_YEAR_NOT_A_HOUSEHOLD_AND_CANNOT_HEAR_DISTRESS_AT_ALL_2026-09-09.md`.

## The defect

`company/crm/enriched_churn_estimate.enriched_churn_estimate` combines its two channels as

```python
result = max(rate_est, payment_est) × market_pressure × payment_method_engagement
```

**That is a switch, not a combination.** Exactly one channel reaches the answer and the other
reaches nothing, and which one wins is decided by the price and the year — never by the household.

Two consequences, both measured, both live at HEAD:

**1. The distress channel is dead at every price the arm chooses.** `bill_shock_count` and
`satisfaction_score` are documented arguments of `decide_margin`, are described in its own
docstring as company observables it prices against, and **cannot move the chosen margin by a single
penny at any value** — spread 0.00 GBP/MWh across 0, 1, 2, 3 and 5 shocks and across satisfaction
0.1 to 0.9. At the margins this arm selects, `rate_est` exceeds `payment_est` always, so `max()`
discards the household entirely. A customer sliding into arrears before departing is invisible to
their own renewal price. `enriched_churn_estimate`'s docstring says the payment channel exists
because *"a passive customer sliding into arrears before departing showed no estimate movement"* —
the fix that comment describes is silenced by the reduction it was added to.

**2. The same switch, the other way, prices the crisis year hardest.** `market_rate_move_pct` is
netted off inside `rate_est`, so in a year whose published cap moved a long way a large increase
reads as this supplier becoming *cheaper than the market*. The rate channel collapses, the flat
payment floor wins, and the belief goes flat in the arm's own price over a wide band of the very
grid the maximiser searches:

| year | market move | belief flat to | chosen margin | believed p_retain |
|---:|---:|---:|---:|---:|
| 2019 | 0.00 | 12.0 | 88.25 | 0.5034 |
| **2022** | **0.67** | **130.0** | **160.00** | **0.9574** |

Same household, same rule, and the chosen margin is **1.8× higher in 2022**, with the arm believing
it will lose 4% of them.

## Why BLOCKING

This is not a latent code smell. It is inside the decision rule behind a **published** figure that
this project has called its most valuable measurement: the value arm gave the departure the higher
margin in 73% of departure-against-survivor pairs
(`SEAT_RESULT_THE_ESTIMANDS_INVERSION_IS_NOT_THE_TIE_MASS_IT_IS_THE_ARM_PRICING_UP_THE_CUSTOMERS_IT_LOST_2026-09-09.md`).
The inversion **survives conditioning on the arm's own belief** — margin-against-departure AUC
0.6667 pooled, 0.6513 within belief quartiles — so the belief is not a sufficient statistic for the
arm's own price, which is precisely what discarding the price channel produces. Anything that
quotes the arm's margins, its beliefs, or the inversion is quoting this.

It is also a fidelity defect at the wall's own standard: a real supplier's retention desk can see
arrears and dissatisfaction, and this one is constructed so that it cannot.

## What is NOT claimed

- **The netting is not itself wrong.** A supplier who raised prices by less than the market did not
  become less competitive, and `company/crm/market_conditions.py` argues that correctly. The defect
  is the composition: netting, plus `max()`, plus an objective with no departure term.
- **No repair is priced here.** Whether combining the channels rather than switching between them
  improves the realised book is a three-arm question needing its own run, and a response surface
  cannot answer it. Do not read this as "combining would earn more".
- **Direction, not magnitude**, on every book-side figure: one world, one seed, 123 scored
  decisions clustered on 88 accounts.

## Reproduction

```
python3 -m tools.renewal_rule_price_response
python3 -m pytest tests/tools/test_renewal_rule_price_response.py
```

`test_the_household_distress_channel_cannot_reach_the_price` **pins this defect deliberately** and
is keyed to the mechanism, not to today's numbers: it asserts the two fields are silenced AND that
the payment channel is the loser of the `max()` AND that the fields were swept over at least three
distinct values. **When the combination is repaired that test goes red — that is intended, and it
is the point at which this finding closes.** Delete it then, having read this.

## What is next

1. **Combine rather than switch.** `max()` over two probabilities of the same event is not a
   combination of evidence under any reading; a noisy-OR (`1 − (1−a)(1−b)`) is the shape the two
   channels' own docstrings describe. **This changes every churn estimate in the tree**, so it is
   an arm behind its own run and a three-arm comparison, not an edit.
2. **Give the objective a departure term.** `expected_value_gbp` is
   `p_retain × contribution × annuity` — losing a customer costs exactly zero, while
   `saas/opex_ledger.py` carries sourced `CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER` and
   `CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER` against
   `docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md`. **Try this one first**: it composes a
   sourced constant already in the tree with a rule already in the tree, and it needs no new
   knowledge — the shape `saas/opex_ledger.py` was written for and stayed unwired seven weeks.
3. **Ask the practitioner.** A retention desk that cannot see arrears is odd against how the trade
   actually works, and no published source will say so. That is the third side of the knowledge
   layer and it is a question for the director, not a thing to build on.
