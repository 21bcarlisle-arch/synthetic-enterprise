**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B10_competitor_switching_response`
**Discharged:** `tests/simulation/test_competitor_reference.py::test_MUTATION_a_price_ADVANTAGE_DECAYS_and_that_is_the_whole_point` -- the FRAME was amended in place (see its appended AMENDMENT section) and B10 was then built to the AMENDED target, not the 2026-07-29 one. That test is the amended target's own acceptance: a price advantage must DECAY against a reference that follows the company down, and it must fail at chase=0, which is the world as it stood when this finding was written.

# B10's FRAME would build the half that already landed, and leave the half C2 is about

Filed before writing a line of B10, because the FRAME is dated **2026-07-29** and the thing it
identifies as the gap was **closed on 2026-08-27** — the day before the director's guidance. Its
design is still mostly right; its *target* is not, and building to it would spend a cycle
producing something the tree already has while leaving C2 exactly as true as it is now.

`observed-with-evidence` throughout (R9).

---

## What the FRAME says the gap is

`docs/design/B10_COMPETITOR_SWITCHING_RESPONSE_FRAME.md` §1.2, on
`market_switching_multiplier(renewal_year)`:

> *"it answers 'how much did the market as a whole want to switch this year,' identically for
> every customer and every possible company price… there is no company price input for it to be
> relative to. Two companies charging different prices in the same year get an identical
> `market_switching_multiplier`. This is the single clearest confirmation of the gap this atom
> exists to close."*

And §2.1, the purpose: *"a switching probability that responds to the live gap between the
company's own price and that tariff — so that overpricing costs customers and underpricing wins
them."*

## That gap is closed

`simulation/customer_events.py` now computes, per customer, inside the churn decision:

```
differential = _price_differential_vs_market(new_rate_gbp_per_mwh, term_start_str)
if differential is None:
    differential = price_differential_pct          # PRICE_DIFFERENTIAL_PCT, now only a fallback
...
elasticity = price_elasticity_for_customer(billing_account, run_base_seed())
felt = perceived_price_differential(differential, elasticity)
```

`_price_differential_vs_market` takes **this customer's own offered rate** against the published
SVT and returns a per-customer differential. `churn_position_multiplier` turns it into churn.
The module's own comment states the property the FRAME wanted:

> *"PER CUSTOMER, NOT PER RUN, and that difference is what makes per-customer pricing testable at
> all. A run-level constant would move the whole book together and could never distinguish a
> supplier that prices two customers differently from one that prices them the same."*

Two companies charging different prices now get different churn, per customer, symmetrically —
`m(d) * m(-d) == 1` is proven in `offer_position_multiplier`'s own docstring. **Overpricing
already costs customers and underpricing already wins them.** §1.2's "single clearest
confirmation" no longer holds, and §2.1's purpose is met.

## The half that is left is the half C2 is actually about

C2's sentence is not about the gap. It is about the *other side* of the gap:

> *"nothing in the world responds to what the company does. Nobody undercuts it, nobody defends,
> nobody targets its book."*

The reference the differential is measured against is `simulation/svt_rates.py` — a literal
`dict[(year, quarter) -> pence/kWh]` of Ofgem cap figures. The FRAME's own proposed replacement,
`MARKET_SAVINGS_BY_YEAR`, is the same shape: one anchored figure per calendar year. **Both are
tables keyed on the calendar. Neither can move in response to anything the company does.**

So a supplier can price 40% above the market for a decade and the market's price is identical to
the one it would have been at 40% below. The population reacts; **the opponent does not.** That
is the whole of C2, and building B10 to its current FRAME would not touch it.

**And the same table is doing double duty, which is why the maximiser's answer came out the way
it did.** `company/pricing/renewal_desk._apply_competitive_ceiling` caps a struck resi rate at the
*published SVT* — so the ceiling the company prices against and the reference the population
churns against are **the same immovable calendar table**. An expected-value maximiser facing a
fixed ceiling and a fixed churn reference correctly discovers that charging right up to the cap is
close to free, because in this world it is: nothing above it is reachable and nothing below it is
contested. That is not a defect in the arm. It is the arm reading a world with one price in it.

## The amendment

**B10's deliverable is a competitor that REPRICES, not a relative-price gap.** Concretely, the
one new thing, stated so it can be argued with:

> A competitor reference price that is a function of the company's own observed position, with a
> lag, bounded below by a cost floor built from the same wholesale stack the company faces.

Three properties that make it a competitor rather than a curve:

1. **It undercuts.** When the company's book-average offer sits above the reference, the
   reference drifts down toward undercutting it — over quarters, not periods, because a real
   rival re-prices on its own hedging cycle and not on ours.
2. **It cannot undercut below its own costs.** The floor is the wholesale stack plus policy and
   network costs — the same inputs the company's own cost stack reads. This is what stops the
   mechanism becoming an unbounded punishment dial and is why the maximiser's answer changes:
   charging the cap stops being close to free, and charging below cost stops being safe.
3. **It has a lag the company does not control.** That is the difference between an opponent and
   a constraint, and it is where SURVIVE gets its teeth in the competition leg C3 names.

**R13, and I want this on the record because it is the line that matters here.** This is a
**BASELINE** change and it is decided blind to company P&L: real GB rivals undercut, which is
what a switching market *is*, and a world where they cannot is less faithful, not easier. The
direction is against the company — it introduces a way to lose that did not exist and no way to
gain any. What stays **CURRICULUM** and therefore the director's is the *aggressiveness*: how
fast the reference chases, and how thin a margin a rival will accept. Those are difficulty
values, they are named and versioned, and they are not mine.

## What this changes in the sequence

Nothing in the wave order (`docs/design/THE_WORLD_MUST_PRESS_SEQUENCE.md`) — P1 is still first
and still the invalidator. What changes is **what P1's build actually is**, and it is smaller
than the FRAME implies: the per-customer gap machinery, the elasticity weighting, the £-scale
conversion and the symmetry proof all already exist and are tested. B10 adds a reprice rule and
a floor to a reference that is currently a constant.

**The FRAME's two R15 controls survive the amendment and one gets sharper.** Control A (the wall:
no company path may reach the world's switching function) is unaffected. Control B was *"hardcode
`f(relative_price_gap_pct)` to a constant and the test must go red"* — under the amendment the
killer mutation becomes **"freeze the competitor reference at its calendar value and the test
must go red"**, which is a strictly better mutation because *that is the current state of the
world*. A control whose killer mutation reproduces today's behaviour is a control that would have
caught C2.

## WORK THIS CREATES

1. This amendment recorded against B10's FRAME so a BUILD pass reads the corrected target, not
   the 2026-07-29 one.
2. `B10` built to the amended target: a repricing reference with a cost floor and a lag.
3. The aggressiveness parameters named as R13 curriculum and put to the director with their
   effect, in the same shape as the P9 menu.

## Still live
