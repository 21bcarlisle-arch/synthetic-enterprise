**Severity:** RECORDED · **Lane:** B_commercial · **Atom:** `B8_discovered_price_sensitivity_holdout`

# What made the 2016-17 electricity book beat its 8% target (B8 Q5, owed item 3)

*2026-10-12, delivery seat. Continues
`docs/staging/SEAT_FINDING_B8_Q5_WHY_THE_RENEWAL_FIX_SITS_BELOW_ITS_OWN_COST_FLOOR_2026-10-12.md`,
owed item 3: "this note has NOT established what made it beat 8% in 2016-17 (hedge gains are the
suspect, unmeasured)." That file is uncommitted in the working tree under another lane's claim
(`value-arm-base-assumes-the-strikes-margin-survives-writer-one`) — this is a NEW file, not an
append to it, so as not to collide with that lane's in-flight edit.*

## The question

The strike prices a flat GBP 2/MWh margin (~1.5-2% of the rate,
`saas/tariff_pricing.TARGET_MARGIN_GBP_PER_MWH`). Writer 1 (the portfolio learning premium,
`company/pricing/renewal_rate_chain.py::compute_portfolio_premium`) steers the realised book to
`PORTFOLIO_TARGET_MARGIN_RATE` = 8% of revenue. The premium goes negative (discounts renewals) only
when `recent_margin_rates` — the realised `net_margin_gbp / revenue_gbp` on the company's own
completed electricity terms, read by `PortfolioMarginBook.term_ended`
(`company/pricing/renewal_rate_chain.py:806`) — beats 8%. In the probe rows quoted in this item's
direction, four such readings were 0.2874, 0.2954, 0.3085, 0.237: 24-31%, three to four times
target. Decompose that into what it is made of, and say whether an 8% target against a GBP 2
strike is one policy or two.

## What the source already settles (read before measuring)

`hedged_settlement.py::run_hedged_term`, for a non-pass-through (fixed) term:
- `margin_gbp = revenue_gbp - wholesale_cost_gbp` (hedge-blended: `hedge_fraction` at
  `hedge_price_gbp_per_mwh`, the rest at spot — `sim/hedging.py::settle_hedged_period`), **with
  the period's standing charge (`sc_per_period`) added into BOTH `revenue_gbp` and `margin_gbp`**
  (lines ~185-188).
- `net_margin_gbp = margin_gbp - policy_cost_gbp - network_cost_gbp - capital_cost_gbp`
  (lines 258-262). **The standing charge has no offsetting cost anywhere in this formula.** It is
  pure margin the moment it is billed, and it is not part of the GBP 2/MWh unit-rate strike
  calculation at all (`renewal_desk.strike_fixed_unit_rate` prices a unit rate, not a standing
  charge).
- So the realised margin has (at least) four legs, not two: the GBP 2/MWh **design margin**, the
  **hedge result** (actual hedge-blended cost vs a 0%-hedge/full-spot counterfactual, both GROSS so
  policy/network/capital cancel cleanly), the **standing charge** (margin with no cost leg at all,
  on the unit-rate view), and a **residual** (locked-vs-actual policy/network/capital cost-build
  gaps, plus anything not accounted for above).

## Pre-registration (filed before the probe's result is read)

Probe: `/var/tmp/se-margin-decomp/probe.py`, wrapping `simulation.run_phase2b.run_hedged_term`
(decomposition) AND `company.pricing.renewal_rate_chain.PortfolioMarginBook.term_ended`
(population/value cross-check against what the premium actually read), to `report_end=2017-03-31`
— the same window the two earlier B8 Q5 probes used, for comparability, and the smallest run that
can answer this (R5).

- **Q1 (population check).** The electricity terms my `run_hedged_term` wrapper captures, joined to
  `term_ended` calls by `household_of(customer_id) == billing_account` and matching
  `last_settled_day`, cover the terms that produced the lookback feeding the four quoted premium
  readings. If a material share of `term_ended`'s electricity rows have no matching
  `run_hedged_term` capture, some of the book settles electricity through `run_deemed_term` /
  `run_flex_term` instead, and this probe's decomposition is partial — I will say so rather than
  silently generalise from a subset.
- **Q2 (identity, sanity only).** `design_margin_gbp + hedge_contribution_gbp +
  standing_charge_gbp + residual_gbp == net_actual_gbp` for every captured term, within rounding.
  This holds by construction; failure means the accounting itself is wrong, not a finding about the
  book.
- **Q3 (design margin share).** `design_margin_gbp / revenue_gbp` sits at 1.5-2% across 2016-17
  electricity terms, matching the finding's own estimate.
- **Q4 (the standing charge, the branch the advisor review raised and the earlier note did not
  consider).** I predict the standing charge is a MATERIAL, possibly the LARGEST single leg: a
  domestic electricity customer at ~3-4 MWh/year and a GBP 100-150/MWh unit rate pays a standing
  charge of order GBP 0.20-0.60/day (~GBP 73-220/year) against unit-rate revenue of order
  GBP 300-600/year — a potential 15-35% addition to revenue that is PURE margin. I put 55% on the
  standing charge alone exceeding the design margin's share, and 35% on it exceeding ALL other legs
  combined (i.e. being the single largest contributor to the 16-23 points above 8%).
- **Q5 (hedge vs residual, the original dichotomy).** Conditional on the standing charge NOT being
  the dominant leg, I restate the original P2 in treasury-vs-structural terms: is the remaining
  excess over 8% (after design margin and standing charge) driven more by `hedge_contribution_gbp`
  (a treasury/trading result — the premium would be handing a hedge gain back as price cuts) or by
  `residual_gbp` (a structural locked-vs-actual cost-build gap — the premium would be reacting to a
  mismeasured cost, not a real surplus)? 50/50, genuinely uncertain.
- **Q6 (direction, weak sanity).** `hedge_contribution_gbp` is positive (a gain) for most 2016-17
  terms, consistent with "beat target." Low information — close to the premise.

## What this does NOT try to answer here

Whether discounting renewals on a standing-charge-driven over-achievement, or on hedge gains, is
the policy intended is the design question this item hands to the knowledge page
(`site/data/knowledge_topics.json` -> `acquisition-and-retention-economics`, per the referring
finding) — that page is currently dirty with another lane's uncommitted edit, so the knowledge-page
write is handed on explicitly rather than attempted here. This note answers the MEASUREMENT
question only: what the 24-31% is made of.
