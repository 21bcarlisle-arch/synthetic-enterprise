**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `W2_17_dual_fuel_leg_clv_attribution`

# The dual-fuel netting repair has nothing to net on a gas-only account, and its own reasoning covers electricity singletons but not gas ones

**Found:** 2026-08-30, verifying the blast radius of the segment-dial and label repair. Newly red
and it is not caused by that repair — the repair changed which accounts exist, and this account is
now among them.

**No published figure is known to be wrong.** This is a control's coverage gap, exposed by a
roster change.

## The red

```
tests/tools/test_bill_correctness_addendum_defect4.py
  ::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year

1 customer-year(s) billed LESS than their own gross trading margin, which cannot happen
given the definitions: [('SYN-2016-014', 2016, 199.18, 241.81)]
```

## Why the existing repair does not cover it

The control was repaired on 2026-08-27 by aggregating from the supply point to the **billing
account**, and its comment records the measurement that justified it:

> after the 2026-08-26 dual-fuel draw, 18 customer-years inverted at supply-point level — 18 of
> 611 gas-leg years, and 0 of 721 electricity years. Aggregated to the billing account, **all 18
> go away**. The money was never missing; only its attribution between two legs of one home was.

That reasoning is sound **and it assumes the gas leg has an electricity sibling to net against.**
Its own closing sentence reaches for the singleton case and reaches for the wrong fuel:

> The single-fuel case is untouched: for an account with no sibling leg the billing account IS the
> supply point, which is 703 of the 721 electricity years.

Electricity singletons, considered. **Gas singletons, not.**

Measured on the live roster:

```
SYN-2016-014   commodity=gas   segment=resi   acquisition_type=synthetic_draw
legs found for the billing account: 1
```

One leg, and it is the gas one. `_base_id` folds `X` and `Xg` together, so a gas-only account
aggregates to itself and there is nothing to net. The inversion the 2026-08-27 repair explained as
mis-attribution *between* legs has no second leg to be attributed to.

## So is the inversion real?

**Unresolved, and that is the honest answer.** Two candidates, and they need different repairs:

1. **A timing gap, not an attribution one.** 2016 is the account's first year: settlement margin
   accrues from the acquisition date while invoices start at the first billing period, so a
   part-year of margin can precede the first bill. If so the same effect exists inside every
   single-leg first year and the control's premise — *"cannot happen given the definitions"* —
   is too strong for a partial opening period.
2. **A genuine single-leg break**, in which case the 18 dual-fuel cases were also masking it and
   aggregation cured a symptom.

Distinguishing them is one measurement: whether the inversion survives outside the acquisition
year, and whether other gas-only accounts show it. Not run here — this is `D_billing_metering`'s
control and its subject, found while verifying an unrelated repair, and fixing another lane's
control on the way past is what SELF_INTERRUPT_DISCIPLINE exists to stop.

## Why it appeared now

The segment-dial and label repair (`7e598a84b`) changed which accounts the world draws, so the
roster now contains this gas-only drawn account in a position it did not previously occupy. **The
repair did not create the gap; it moved the population past it.** A control whose coverage argument
holds only for the roster that happened to exist when it was written will do this again, which is
the more useful half of this finding.

## What is owed

Establish which of the two candidates it is, then either widen the control's premise to exclude a
partial opening period — stating that exclusion, not silently skipping the year — or fix the
single-leg accrual. **Not "aggregate harder"**: there is nothing left to aggregate.

The control should also say what it covers. Its comment enumerates 721 electricity years and 611
gas-leg years; the population it silently does not reason about is gas accounts with no
electricity sibling, and naming that number would have made this visible before a roster change
found it.
