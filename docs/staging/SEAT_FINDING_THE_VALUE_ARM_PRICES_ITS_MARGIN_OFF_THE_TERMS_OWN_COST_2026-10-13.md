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

## Book-level pre-registration (written before the run)

Measuring the shift on one seed of `tools.decision_probe` (default book, full 2016-2025 record,
`--roll-seed 61001`): every priced renewal under the value arm, and under each `flat_at_level`
grid rung, now carries `arm_base_source` and `arm_base_gbp_per_mwh` on its chain entry
(`company/pricing/renewal_rate_chain.py`'s `components` list names which of writers 1-3
-- `portfolio_premium`, `margin_surcharge`, `profitability_uplift` -- fired on that renewal
before the arm, in firing order).

**Predicted `arm_base_source` share.** The fallback (`BASE_STRIKE_LESS_FLAT_MARGIN`) fires only
where `pre_margin_unit_rate` has no offer to read (no company forward/policy/network on the
term) -- the same condition that already disables writer 1. The probe only compares renewals that
reach the arm with a struck rate at all, so I predict `BASE_TERM_COST` on at least 90% of priced
renewals, fallback on the rest.

**Predicted delta (`arm_base_gbp_per_mwh - (unit_rate_before - 2)`).** Where none of writers 1-3
fired: ~0.00 GBP/MWh (the identity the cost-floor fixture already proved at real inputs). Where
one or more fired: a GBP few/MWh in the direction that writer moved the rate -- a positive
writer-1 premium or writer-2/3 uplift makes the old base too LOW (positive delta, the old arm
*understated* its margin and so overstated p_stay less than it should have); a writer-1 discount
makes the old base too HIGH (negative delta, matching the fixture's own writer-1-floored case,
which overstated margin by 3.11 GBP/MWh at NAKED 0.15, GBP 90 forward).

**Decision threshold, fixed now.** If the median `|delta|` among renewals where ANY writer fired
is at or above 1.11 GBP/MWh (the capital charge the finding above already named as the smallest
material move, since a shift of that size alone can change which price-ladder rung a renewal
clears) OR writer-moved renewals are more than 10% of the priced book, this is a RE-TAKE: every
arm-vs-control figure already published is scored on a margin basis that moved by a material,
non-uniform amount and must be re-run on the new base. Below both bars, it is a FOOTNOTE: note
the base changed, but the prior arm-vs-control comparisons stand because the shift did not move
enough of the book by enough to change a conclusion. One seed on an ~80-100 decision book cannot
bound this tightly; it decides which of the two the B8 lane does next, not the exact size.
## Measurement in flight (delivery seat, 2026-10-13 07:16 BST)

`longjob-value-arm-measure-61001b` (one roll-seed, full 2016-2025 book, `/tmp/value_arm_measure.py`
against this commit) is RUNNING, not stuck: `active` since 05:52:44 BST, CPU 1h44m, memory 2.5G
(peak 6G), log progressing through settlement periods with no traceback. No artefact yet at
`/var/tmp/value_arm_measure_61001.json` — the run has not written its result.

Schema check (read before waiting on it): the script captures one row per value-arm-policy
renewal with `delta_gbp_per_mwh` and `writers`, plus a `summary` that medians over ALL captured
rows, not just moved ones. The pre-registered test (median |delta| >= 1.11 GBP/MWh among moved
renewals, or moved-renewal share > 10%) needs filtering the raw rows to `delta_gbp_per_mwh != 0`
first — the summary block alone cannot answer it. Confirmed the rows carry everything needed to do
that filter once the file exists; nothing further needs changing in the script.

Premise note: `04913b693` (this finding's own commit, floor + rebase of the value-arm's base) is
already an ancestor of origin/main. That does not spend this item's premise — 04913b693 is the
*subject* the run measures, not the deliverable. The deliverable is the run's numbers and the
re-take-vs-footnote call on B8, still open.
