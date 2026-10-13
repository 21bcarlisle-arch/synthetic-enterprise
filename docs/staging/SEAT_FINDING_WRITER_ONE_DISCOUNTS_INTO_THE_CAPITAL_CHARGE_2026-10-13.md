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

## Ten-renewal evidence

To follow below this line: per-writer rates for ten of the renewals, from a replay of seed 61001 at
origin (pre-fix) code. The replay is queued behind the memory gate's "landings come before
experiments" rule.
