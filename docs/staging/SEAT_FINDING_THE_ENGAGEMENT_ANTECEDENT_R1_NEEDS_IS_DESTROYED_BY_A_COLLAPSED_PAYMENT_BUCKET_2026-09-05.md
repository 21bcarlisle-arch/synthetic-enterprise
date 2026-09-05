**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** PB4_engagement_separated_from_elasticity

# The engagement antecedent R1 needs is destroyed by a collapsed payment bucket, and the split it says is unpublished is in the next module

**Found:** 2026-09-05, delivery seat, building R1 after the CIM demographic banner
(`docs/market_research/what_a_supplier_can_observe_about_switching_propensity_cim_w6.md`).

---

## What R1 needed, and where it was going to go

The ceiling measurement said there is nothing in our own book to condition on. The CIM banner then
said what a real supplier COULD condition on, and the answer is concentrated in one field:

```
switched supplier in past 6 months, base 5.3%
    standard credit      5.7%      n=438
    direct debit         5.6%      n=2483
    prepayment (all)     3.1%      n=491
      traditional PPM    1.7%      n=158        <- 3.4x against standard credit
```

**And the gate to put it behind already exists.** `simulation/renewal_engagement.rolls_active_renewal`
is *"the WORLD's renewal-engagement physics — whether a household actually shops"*, and it already
takes an `active_probability` seam that `renewals.py` threads from
`household_segments.active_renewal_probability_for_customer`. No new module: PB4 is that function
gaining observable antecedents instead of being a hash.

`household_segments.py` line 60 is explicit that it currently is one:
`random.Random(f"engagement_{customer_id}")` — which is the canon's own claim, verbatim, in code.

## Why the build stops here

**`PaymentChannel` has two members, and the entire published effect lives at the seam it collapses.**

```python
class PaymentChannel(str, Enum):
    DIRECT_DEBIT = "direct_debit"
    STANDARD_CREDIT = "standard_credit"
```

Prepayment is folded into `STANDARD_CREDIT`. In CIM terms that merges a 5.7% population with a 3.1%
one, and the merged bucket's engagement is a weighted average that differs from direct debit's 5.6%
by nothing at all. **Wiring engagement to payment method as the model stands would produce a
multiplier of ~1.0 on every household — a build that runs, passes, and encodes no signal.** That is
the outcome worth stopping for: it would have looked exactly like a completed R1 atom.

## The part that is a knowledge-layer failure, not a modelling one

`household_segments.py` states the reason for the collapse:

> *"This codebase's own PaymentChannel collapses prepayment+standard-credit into one
> STANDARD_CREDIT bucket (see the DD-share note above — **the real sub-split isn't published**), so
> the non-DD rate used here is the unweighted mean of the two published non-DD rates
> (22.3+18.5)/2 = 20.4% — an honest blend, not an independently anchored figure, flagged as such."*

**It is published, and this repository already holds it.** `simulation/payment_behaviour_source.py`:

> *"Non-DD sub-split (standard_credit vs prepayment): Ofgem 2026, ~74% DD / 13% standard credit /
> 13% prepayment (recorded in `simulation.dd_attribution`'s own ANCHORS section, 2026-07-13
> DISCOVER pass)."*

One module blends two rates because the split is unavailable; another module in the same package
cites the published split and names the file holding the anchors. Both are careful, both flag their
own uncertainty honestly, and neither can see the other. This is the £55-versus-£150 acquisition
cost shape exactly — *"the answer is usually already here"* — and it has now cost a second thing:
not just a wrong constant, but a **missing dimension** that a downstream atom needs and cannot get.

The `FUEL_POVERTY_RATE_BY_CHANNEL` blend is also downstream of it: 20.4% is an unweighted mean of
22.3% and 18.5% standing in for two categories the tree can populate separately.

## The build this makes, in order

1. **Split `PaymentChannel` three ways** — `DIRECT_DEBIT`, `STANDARD_CREDIT`, `PREPAYMENT` — drawn
   at the published 74/13/13, sourced from `dd_attribution`'s existing anchors rather than a new
   number. `simulation/activation_energy.py` already has an `is_ppm` concept and a `+20` inertia
   uplift, so part of the world is already asking a question the population cannot answer.
2. **Unblend `FUEL_POVERTY_RATE_BY_CHANNEL`** onto the two published rates it currently averages
   (prepayment 22.3%, standard credit 18.5%), which stops being a blend the moment step 1 lands.
3. **Give `active_renewal_probability_for_customer` its observable antecedent**, anchored on the
   CIM ratios, mean-preserving over the 74/13/13 mix so it cannot re-level the book — the same
   discipline `price_elasticity_for_customer` already keeps.
4. **Re-run `tools/r1_inference_ceiling.py`.** It is the falsifier and it is currently at the null;
   if this build works, a full-coverage observable clears it.

## What this does NOT claim

It does not claim the CIM association is causal — traditional-PPM households may shop less because
of the meter or because of who lives behind it. That distinction is not load bearing for building a
world a supplier could learn from, and would become load bearing only if someone proposed changing
a household's meter to change its behaviour.

It also does not claim three categories are enough. CIM separates smart PPM (3.2%) from traditional
PPM (1.7%), and the model has no smart/traditional meter distinction on the prepayment side.

## What would close this

`PaymentChannel` carrying prepayment separately at the published share, and
`tools/r1_inference_ceiling.py` re-run on a book drawn after step 3. Not written as a
**Discharged:** field — nothing has landed yet.

---

## CORRECTION, same day, before any of the build above was written

**Step 1 above is wrong, and the true state is better and worse than it says.** I proposed splitting
`PaymentChannel` three ways as new work. It does not need writing: **`simulation/payment_behaviour_
source.generate_payment_method` already draws the three-way method**, anchored, with
`PREPAYMENT = "prepayment"` and `_PREPAYMENT_SHARE_OF_NON_DD = 0.50` carrying the Ofgem 74/13/13
mix, and a live branch that returns prepayment.

**It has zero consumers.** Outside its own module and its tests, nothing in `simulation/`,
`company/` or `saas/` calls it. Meanwhile the two-way `payment_channel_for_customer` — the one with
no prepayment at all — is wired into six: `arrears_engine`, `final_bill_outcome`, `sim_satisfaction`,
`run_phase2b`, `run_phase4c_on_phase2b` and (by reference) `opex_ledger`.

So the correct three-way draw is dead code and the impoverished two-way draw is the world.

**Measured, because the obvious next worry is whether the two contradict each other in flight:**

```
DD/non-DD agreement over 400 households: 235 agree, 165 disagree (41.2%)
```

They are statistically independent — `paychannel_{cid}_{fuel}` against `_base_seed_for("{cid}::
{fuel}")`, different streams, no coupling — and 58.8% agreement is exactly what chance gives for two
independent draws at a 72% DD share. **But this is NOT a live inconsistency today**, precisely
because one of the two never runs. It would become one the instant a second consumer picked the
other draw, which is exactly what wiring R1's engagement antecedent to `generate_payment_method`
would have done. That is the trap this correction exists to close: the fix is to MIGRATE the live
path onto the anchored draw, never to add a third consumer beside two definitions.

**The build, corrected:**

1. Migrate `payment_channel_for_customer` onto `generate_payment_method`'s draw so there is one
   definition of a household's payment method, and `PaymentChannel` gains `PREPAYMENT`. This is a
   world change with six downstream consumers and it moves households between buckets, so it is
   fidelity work to be done deliberately and measured, not a refactor.
2. Unblend `FUEL_POVERTY_RATE_BY_CHANNEL` onto the two published rates it averages (22.3% / 18.5%).
3. Then the engagement antecedent, mean-preserving over the mix.
4. Then re-run `tools/r1_inference_ceiling.py`.

**Why this is worth more than the atom it blocks.** A correctly anchored, carefully sourced,
prepayment-aware payment model was built and never wired to anything, while the world ran on a
simplification that explicitly records "the real sub-split isn't published". That is the
`no_caller_and_never_runs` class meeting the £55/£150 class in one place, and it cost R1 its
antecedent.
