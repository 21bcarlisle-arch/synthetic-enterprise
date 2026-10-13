**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# The value arm's margin is measured from the term's own cost, not from the rate writer 1 left

*2026-10-13, delivery seat (direction `value-arm-base-assumes-the-strikes-margin-survives-writer-one`).*

## The defect

`renewal_margin_uplift` handed `decide_margin` `base = locked_unit_rate - GBP 2`, where
`locked_unit_rate` is the rate AFTER chain writers 1-3 (portfolio premium, margin surcharge,
profitability uplift) and after the desk's competitive ceiling. The base is only the term's
pre-margin cost when none of those moved it. Every candidate's `p_stay`, revenue, bad debt and
`expected_value_gbp` is scored at `margin = rate - base`, so on a moved term the arm's logged belief
was for a margin it never earned. 03a0b66da stopped the visible symptom (a rate under cost) by
flooring; the base was still wrong.

## Which base, and why

Two candidates were offered: the cost floor (`company_forward + locked_policy + locked_network`)
or the rate before writer 1. Neither is quite right, so the build takes a third:

- **The cost floor omits capital cost.** The strike (`saas/tariff_pricing.price_fixed_tariff`) is
  forward + capital + GBP 2 + policy + network. Measuring margin from the floor would count the
  capital charge (1.645 x sigma x naked fraction x WACC x forward, ~GBP 1.11 at GBP 90 pre-2023) as
  margin. K2: leaving it out asserts it is zero.
- **The rate before writer 1 minus GBP 2** is right only if the competitive ceiling did not bind on
  the strike, and it would still sit on top of writers 2 and 3 had they moved first.
- **Chosen: the strike's own pre-margin rate, recomputed from the term's components** —
  `renewal_desk.pre_margin_unit_rate`, which calls `price_fixed_tariff` with the term's own
  forward and locked costs and takes off its margin. That is exactly what `decide_margin`'s
  docstring says its base is: "wholesale + capital + policy + network, exactly what
  `renewal_desk.strike_fixed_unit_rate` already computes." The arm's contracted rate is then
  `base + chosen`, so the rate it scored is the rate it charged (before the cap, which it already
  searches under).

Consequence, stated: where the value arm or the level arm prices a renewal, its answer now
replaces writers 1-3's moves rather than adding to them. That is the arm's design ("what this
account is worth, rather than what it cost"), and it is what makes `flat_at_level` flat: before
this, a level-L renewal on a term writer 1 discounted by 5% earned L minus the discount.

Where the term carries no offer components (`None` on the typed record), the arm falls back to the
old `locked - GBP 2` and says so per decision (`arm_base_source`).

## Pre-registration (written before the numbers were printed)

On the cost-floor test's own fixture (2017-01-09, forward 90.00, policy 14.27, network 32.00,
NAKED 0.15): predicted capital 1.645 x 0.5 x 0.15 x 0.10 x 90 = 1.1104, so the new base is
137.3804. With writer 1 floored at 136.27, the old base was 134.27 — the old arm overstated its own
margin by 3.11 GBP/MWh. On an unmoved term struck by `price_fixed_tariff`, the new base equals the
old `struck - 2` to within 1e-9.

## Result

Printed after the helper was written: base 137.380375 (predicted 137.3804); `strike - 2 - base`
= 0.0 exactly at EAC 3,100 and 250,000. Both predictions held. The old arm on this fixture
overstated its margin by 137.38 - 134.27 = 3.11 GBP/MWh.

Controls (`tests/company/pricing/test_a_renewal_discount_stops_at_its_own_cost_floor.py`): the
arm's rate is `term cost + level` on a term writer 1 cut to the floor; the fallback base is named
when the record has no offer components; and the chain's own floor on the arm is still reachable
(a base knocked under cost is floored, the honest one is not). Mutation: reverting the base to
`locked - 2` reds two of them.

What the floor 03a0b66da added to the arm now does: with offer components it binds only on a
margin below minus the capital charge (about GBP 1.11 at a GBP 90 forward before 2023), which a
low price-ladder rung can reach (`2 + k x (0.5 - 2)` for k above ~2.7). Kept, for that and for the
fallback base.

**Not yet measured:** how many renewals in a value-cycle arm run change rate, and by how much.
That needs a run; the arms re-take is the B8/value-cycle lane's, and every arm-vs-control figure
published before this commit was scored on the old base.
