**Severity:** RECORDED · **Lane:** C_customer_ops · **Atom:** `C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv`

# Pre-registration: on the world's own renewals, how many advice cases does a sharing rise bring to zero once the rise is capped at the default?

Written 2026-10-17, before the count below was run. Claim
`retention-rise-rescue-counted-per-account-under-the-default-headroom`; page
`docs/market_research/a_retention_price_that_shares_the_value_an_action_creates.md` §4 and §4a;
director's open row `c34-now-ranks-next-best-action-on`. This file is not edited after the count.

## The instrument

The same probe output §4a graded (`/var/tmp/retention_rise/probe_default.json`, default book, 260
renewals, 192 accounts). For each renewal, with V its annual MWh:

- **m**, our monthly margin with no action: (stayer's billed rate at the flat offer − base) × V / 12.
- **h0**, the monthly hazard: 1 − P(stay at flat)^(1/12), the constant monthly hazard with the
  world's one-year survival. (1 − P)/12, §4a's reading, is run as a sensitivity.
- **A rise of £d/month** is placed at flat + 12d/V £/MWh. The world's P(stay) there is interpolated on
  the level grid, and **collected(d)** is what a stayer is actually billed over flat at that offer (the
  decline-a-fix-above-the-default rule caps it at the default).
- **Our side** = `next_best_action.value_change` (imported unchanged), horizon 48, with margin change
  −g + collected(d) and hazard change −c + (h(d) − h0), for the page's three effects
  (g, c) = (£2, 0.1pt), (£2, 0.3pt), (£3, 0.3pt). Benefit 12g a year.
- **Rescued**: some d on the grid, £0–50/month in £0.01 steps, brings our side to ≥ 0.
  **Clears the floor**: collected(d) × forward_value(1, h with action, 48) ≤ 4g × 12.
- Two arms: **world** (h(d) from the grid) and **module** (h(d) = h0, the price's own effect left
  out, as `value_change` does). A renewal off the grid at d = 0 is ungraded and counted as such.

Unit: a renewal × effect (≤ 780). Accounts with ≥ 1 rescued renewal are reported beside it.

## Predictions

The world's flat margin is £1.33/month at the median and h0 ≈ 4%/month, so a 0.3pt hazard cut is
worth very little to us, and the rise needed is close to g itself. The room under the default
admits £2 in 43% and £2.73 in 37% of renewals (§4a).

- **Q1.** Module arm: rescued in 35–50% of renewals for each (£2, ·) effect and 28–42% for (£3, 0.3pt).
- **Q2.** World arm: within 6 points below the module arm in every effect (the slope is 0.00065).
- **Q3.** Of rescued cases, ≥ 90% clear the household's floor in both arms.
- **Q4.** The share rescued is higher among renewals whose flat margin is below the median than above
  it (a low flat sits further under the default).
- **Q5.** Fewer than 10% of renewals need no rise at all (our side ≥ 0 unaided); those are the
  negative-margin renewals, where a lost month costs us nothing.
