**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`
**Knowledge:** acquisition-and-retention-economics -- "How far a renewal discount may go", amended in the same commit: the floor is the term's cost, capital charge included

# Writer 1 discounts into the capital charge: the 496 renewals are real, not a probe artefact (2026-10-13)

*Direction `the-pre-arm-struck-rate-sits-below-term-cost-on-496-of-698-renewals`, autonomous worker.*

## The question

`/var/tmp/value_arm_measure_61001.json` (seed 61001, full 2016-2025 book, at 04913b693) has
`unit_rate_before < arm_base_gbp_per_mwh` on 496 of 698 value-arm renewals (median -0.71 GBP/MWh
among the 496). Either writer 1 (`portfolio_premium`) really strikes under the term's own cost, or
the probe reads the rate before a later floor applies.

## Answer: real, and bounded by the capital charge

**Not an artefact of where the probe reads.** `unit_rate_before` on the value-arm entry is the rate
as it ENTERS the arm (`renewal_rate_chain.py`, writer 3b: `rate_before = unit_rate`), so it is
already after writer 1's `_floor_a_discount` (03a0b66da). The tier floor (5c137eb5b) is applied to
the retention offer after the chain returns, and does not touch the rate the arm or the control
contracts. No later floor exists for the probe to have read before.

**Why it sits under the base.** The two numbers measure two different costs:

- writer 1's floor was `own_cost_floor` = forward + locked policy + locked network;
- the arm's base is `pre_margin_unit_rate` = the same three **plus the capital charge** the strike
  prices in (`price_fixed_tariff`: 1.645 x sigma_stressed x 0.15 naked x 10% WACC x forward, so
  1.23% of forward before 2023 and 3.70% from 2023).

A discount floored at the first sits anywhere between the two, under the term's cost. The
artefact bears that out on every one of the 496 rows: the gap `before - base` never exceeds the
capital charge's ceiling (`k x base`, an upper bound since forward <= base). Rows below even that
bound: **0 of 496**. Every one of the 496 has `portfolio_premium` as its only writer, and the gap's
size follows the capital charge's era: median 0.65 before 2023 (max 1.73), 2.74 from 2023
(max 6.03), where capital is three times dearer.

So writer 1 really does strike under the term's own cost, by at most the capital charge. It is the
same omission the value-arm finding named for the arm's base (K2: leaving capital out asserts it
is zero), still live in the floor that 03a0b66da set.

## The fix

`decide_renewal_rate`'s `cost_floor` is now `pre_margin_unit_rate(...)`, the term's cost with its
capital charge, and the arm's base reads the same variable instead of a second call. One number
is now both what a discount stops at and what the arm measures its margin from. It reaches all
three uses: writer 1's floor, the arm's floor and the class refusal where the chain returns. It
is `None` exactly where `own_cost_floor` was, so the fail-closed branch (no discount without a
floor) is unchanged.

Consequence, stated: with the base and the floor now one number, the arm's own floor binds only
on a margin below zero, which no rung offers. It stays as the writer-local half of the class
check. Its test now knocks the base alone on its way into `renewal_margin_uplift`, because
knocking `pre_margin_unit_rate` knocks the floor too.

Controls (`tests/company/pricing/test_a_renewal_discount_stops_at_its_own_cost_floor.py`):
`test_the_floor_is_the_term_cost_with_its_capital_charge` pins the fixture's floor at 137.38
(136.27 + 1.11 capital) and reds if a deep discount lands within GBP 1 of forward + locked costs.
Mutation (floor reverted to `own_cost_floor`): 5 of 11 tests red. The class refusal at the
chain's return (`refuse_discretionary_rate_below_own_cost_floor`) now refuses any renewal
struck below the capital-inclusive cost, whatever writer moved it.

## Before and after across the book (seed 61001, from the artefact)

The arms' contracted rate is unchanged: it was already `base + chosen` with the same base. What
moves is the rate writer 1 leaves, which is what the **control** contracts, and what every arm
receives as its `unit_rate_before`.

| | renewals lifted | median lift GBP/MWh | max |
|---|---|---|---|
| all | **496 / 698 (71.1%)** | 0.71 | 6.03 |
| electricity | 447 / 495 | 0.71 | 6.03 |
| gas | 49 / 203 | 0.57 | 1.58 |
| before 2023 | 351 / 538 | 0.65 | 1.73 |
| from 2023 | 145 / 160 | 2.74 | 6.03 |

The lift is `base - before`, an upper bound where the competitive ceiling struck the term
below its own cost: there `_floor_a_discount` withholds the discount and lifts nothing. The
artefact does not carry the strike, so it cannot say how many rows that covers.

## What this does to the re-take

`retake-the-value-arms-on-the-term-cost-base` must run at or after this commit. Before it, the
control was priced inside the capital band on 71% of renewals, so every arm-vs-control figure
compared the arm with a control that gave away its capital cost. The re-take is now free to run,
once, on the fixed control.

## Same class, not carried across here

The retention offer's floor (`run_phase2b` -> `refuse_retention_offer_below_own_cost_floor`, sized
by `growth_desk`, 5c137eb5b) and the save's price match (`save_offer.py`) still floor at forward +
locked costs, without capital. They are the same rule with a different cost under it. Not changed
in this commit. The knowledge page records it as a GAP.

## Ten-renewal evidence (replay of seed 61001, 2016-2017, at 4e8054786, pre-fix)

`tools.decision_probe.probe(report_end="2017-12-31", roll_seed=61001)` with `decide_renewal` wrapped
to log each call's inputs, every writer's `rate_before -> rate_after` and the contracted rate. The
control (`current`) pass, which is the rate actually billed, since no arm replaces it there. The
first row is the artefact's own first row (C5, before 128.6801 against base 129.4867), so the
replay matches the full run on that renewal.

| customer | fuel | term start | strike | writer 1 % | after writer 1 | other writers | billed (contracted) | fwd+locked floor | term cost incl. capital | billed - term cost |
|---|---|---|---|---|---|---|---|---|---|---|
| C5 | elec | 2016-12-31 | 131.49 | -3.80 | 128.68 | none | 128.68 | 128.68 | 129.49 | -0.81 |
| SYN-2016-029 | elec | 2017-01-24 | 141.38 | -5.00 | 139.06 | none | 139.06 | 139.06 | 139.98 | -0.92 |
| SYN-2016-064 | elec | 2017-02-16 | 123.07 | -2.03 | 120.57 | none | 120.57 | 120.38 | 121.07 | -0.50 |
| SYN-2016-085 | elec | 2017-02-25 | 122.04 | -5.00 | 119.36 | none | 119.36 | 119.36 | 120.04 | -0.68 |
| SYN-2016-119 | elec | 2017-03-09 | 133.98 | -4.54 | 131.15 | none | 131.15 | 131.15 | 131.98 | -0.82 |
| SYN-2016-150 | elec | 2017-03-23 | 134.68 | -5.00 | 131.85 | none | 131.85 | 131.85 | 132.68 | -0.83 |
| SYN-2016-162 | elec | 2017-03-31 | 122.77 | -5.00 | 120.09 | none | 120.09 | 120.09 | 120.77 | -0.69 |
| SYN-2016-168 | elec | 2017-04-03 | 134.53 | -5.00 | 131.77 | none | 131.77 | 131.77 | 132.53 | -0.76 |
| SYN-2016-216 | elec | 2017-05-03 | 120.79 | -5.00 | 118.20 | none | 118.20 | 118.20 | 118.79 | -0.59 |
| PROS-2016-0170 | elec | 2017-06-05 | 108.62 | -5.00 | 106.18 | none | 106.18 | 106.18 | 106.62 | -0.45 |

Over the whole window's control pass: 428 renewals had offer components, and writer 1 fired on 71.
It left 52 of them under the capital-inclusive term cost, 48 exactly at the forward + locked floor
and none below it (23 read below by up to 2e-5, but that is the logged 4-dp rounding against an
unrounded floor). 51 were billed there, each with writer 1 as its only writer. The strike sits
GBP 2 above the term cost and a -5% premium takes off more than that, so the old floor binds and
the rate stops the capital charge short of cost. Since 434d87587 the same renewals stop at the
term cost column, which `test_the_floor_is_the_term_cost_with_its_capital_charge` pins.
