**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# B8 Q5: the renewal cut sized by price match, against the risk tiers, over 2016-2025 across seeds

*2026-10-11, delivery seat (direction `b8-q5-price-match-as-the-standing-renewal-cut`).*

`d06b039e7` built `DecisionPolicy.retention_cut_sizing = "price_match"`, off by default. On one seed
to 2019, with the holdout on, it offered in 15 places where the tiers offered in 41. Mean cut was
3.1% against 4.0%, offer cost GBP 332 against 932, and net was +GBP 577. That is not a result. This
is the standing-policy test: `CURRENT_POLICY` with only the sizing changed, holdout off, full window.

## Pre-registration (filed before any run)

**Arms.** `CURRENT_POLICY` with `retention_cut_sizing` set to `risk_tiers` (as now) or `price_match`.
Nothing else changes. Driver: `/var/tmp/se-b8-q5-full/arm.py`, one process per arm, `report_end=None`.

**Seeds.** `base` is the unpatched world. `11111` and `22222` are the first two of the value arms'
churn-roll floor seeds. They re-draw `churn_roll_for_renewal` by the floors' own stream
(`floor{seed}_{account}_{term}`) at every `simulation.*` binding of the function, so one renewal
reads one roll everywhere. The value arms' floor patches only `customer_events`'s binding, and this
re-draw is wider than that, on purpose. The book is the default book, because book seeds are the
director's.

**What is counted, per arm and seed:**

- the renewals reaching the value test;
- offers made, by year;
- offers retained;
- mean cut;
- offer cost, by year;
- total net;
- under the match, every no-offer split by its cause:
  - `input_missing`, with which input;
  - `market_had_nothing_cheaper_than_the_default` (gap at or below 0);
  - `our_cost_floor_is_at_or_above_the_fix`;
  - `the_fix_already_meets_the_best_published_deal` (the market's match is at or above our re-fix).

**Predictions:**

1. Under the match, offers are at most half the tiers' offers, on every seed.
2. The match's mean cut is at or below the tiers' mean cut, on every seed. (The 2019 run refuted
   "deeper". I now expect narrower, not deeper.)
3. The match's offer cost is lower, on every seed.
4. `the_fix_already_meets_the_best_published_deal` is the commonest no-offer cause, on every seed.
   `input_missing` is at most 5% of the no-offers.
5. `market_had_nothing_cheaper_than_the_default` falls only on terms starting 2021-10 to 2023-06.
   That is the zero-gap quarters.
6. Net, match minus tiers, lies within ±GBP 2,000 on every seed. That is under 1% of a full-window
   net. **I predict its sign is not the same on all three seeds.** In other words, I expect the
   sizing not to be distinguishable on money.

**Decision rule, fixed now.**

- **Recommend the switch** if, on every seed, the match spends less on offers and net is not lower
  by more than one seed-spread of the noise. A narrower rule that pays a cut only where the market
  can undercut us moves less value from the company to households who would not have left for
  price. That is the mission's created-versus-transferred test.
- **Do not recommend the switch** if net falls on every seed. Then the tiers' extra offers bought
  retention worth more than they cost.

## Result

*(to follow, beside the predictions above, unedited)*
