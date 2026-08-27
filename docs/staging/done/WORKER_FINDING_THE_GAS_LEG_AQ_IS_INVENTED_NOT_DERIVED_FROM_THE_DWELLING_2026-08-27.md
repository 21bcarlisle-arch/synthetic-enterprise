# The gas leg's annual quantity is drawn from a band, and the dwelling's meter disagrees

**Date:** 2026-08-27. **Author:** the delivery seat. **Subject of the defect:** this seat's own
dual-fuel change of 2026-08-26 (`simulation/live_population._gas_leg_for`).
**Status:** MEASURED, NOT FIXED. The control that caught it is left RED on purpose — see
"Disposition".

## The control, and what it found

`tests/tools/test_bill_correctness_addendum_defect4.py::
test_billed_total_never_less_than_gross_margin_for_any_real_customer_year` asserts that a
customer-year can never be billed LESS than its own gross trading margin, because given the
definitions that is arithmetically impossible.

It fires on 18 customer-years. **Every single one is a `...g` account — a gas leg.**

| population | customer-years | inverted | share |
|---|---|---|---|
| gas legs | 611 | **18** | 2.9% |
| electricity | 721 | **0** | 0.0% |

Zero electricity accounts invert. The phenomenon is entirely a property of the legs this seat
added, so it is this seat's defect and not an inherited one.

## The mechanism, measured rather than inferred

A healthy gas leg bills about 2.5x its gross margin (median 2.518 over 532 leg-years) — the
ordinary relationship between an invoice and the trading margin inside it. The 18 run from
0.13 to 0.84, and they are NOT partial acquisition years: `PROS-2022-0047g` inverts in 2022,
2023, 2024 AND 2025, consecutively.

Reading that account directly:

```
PROS-2022-0047g   aq_kwh = 5944.2   band = LOW    (billed ~£15/yr)
PROS-2022-0047    eac_kwh = 1543.1  band = LOW
```

**Two independent numbers describe one home's gas.** `aq_kwh` — which prices the contract and
therefore drives the trading margin — is a uniform draw from Ofgem's published TDCV band. What
the customer is BILLED comes from the world metering the dwelling's own modelled gas demand.
Nothing reconciles them, so for a home whose modelled demand sits well below its band's midpoint
the margin is computed on ~5,900 kWh while the meter reads a small fraction of that.

## Why it happened, and the line in this seat's own test that predicted it

`_gas_leg_for` takes WHETHER a home has gas from `DrawnPremise.commodity` — a property of the
housing stock, correctly — and then takes HOW MUCH from `TDCV_BANDS_KWH["gas"]` keyed on the
home's `consumption_band`. That band is the home's **electricity** consumption band. Using it to
index a GAS table is a proxy, and `tests/simulation/test_dual_fuel_wins.py` says so in as many
words: *"the quantity comes from the published table by the same uniform draw the electricity
EAC uses."*

That was defensible when it landed — `net_new_acquisition.ELECTRICITY_ONLY` had refused to
"invent an annual quantity for a home whose gas consumption nothing has yet modelled", and the
TDCV table was the least-invented number available. **The premise has expired again**: the world
DOES model a dwelling's gas demand (`simulation/phase_d_gas_household_demand`), and that is the
number the meter reads. Drawing a second one beside it was the error.

## The fix, which is not made here

Derive `aq_kwh` from the dwelling's own modelled gas demand rather than from a band-uniform
draw, so the quantity that prices the contract and the quantity that is metered come from ONE
source. That is strictly more faithful — a real supplier's AQ is an estimate OF a specific
property's consumption, not a draw from a national table — and it is an R13-legitimate baseline
change: decided for fidelity, on an arithmetic contradiction, blind to what it does to the P&L.

**It is deliberately not made in the same commit as the finding**, for two reasons. It moves
every dual-fuel account's revenue, margin and lifetime value, so it wants its own before/after
measurement rather than to ride along inside a red-clearing sweep. And this seat has spent one
long session already landing a change whose downstream effects it did not fully measure — the
household-aliasing defect, found the same day, from the same commit.

## Disposition: LEFT RED, deliberately

Not `xfail`. Not a row in `docs/observability/head_red_baseline.json`.

The baseline's own docstring rules this out: *"NOTHING WRITES THIS FILE AUTOMATICALLY: a control
that absorbs its own new failures into its own baseline cannot fail."* An author adding their own
fresh defect to the known-red list is precisely that anti-pattern, whether a script does it or a
person does. An `xfail` would be the same move wearing a decorator.

So the control stays loud and stays failing, and it will keep failing until the AQ is derived.
That is what a control is for.

---

## CORRECTION, 2026-08-27, same day, before any fix was built on it

**The mechanism named above is wrong, and the title overstates it.** Recorded here rather than
edited out: the diagnosis was published, so the correction is published beside it.

### What I got wrong

I wrote that `aq_kwh` and the metered volume are "two independent numbers ... nothing reconciles
them". They are not independent. `simulation/household_demand.HouseholdDemandRegister` takes
`aq_kwh` off the customer record as its BASE and applies a per-date multiplier to it — so the
drawn AQ is precisely what the world meters against. My "derive the AQ from the dwelling instead"
recommendation was therefore aimed at a seam that already exists.

I reached that conclusion from a plausible shape (band-drawn AQ, big divergence) without reading
the demand model. That is the R4 failure: I named a mechanism before I had checked the nearest
working analogue.

### What the evidence actually says

`gas_eac_multiplier_for_date` on the four inverting accounts I sampled:

| account | 2020 | 2022 | 2024 | 2025 | inverts in |
|---|---|---|---|---|---|
| PROS-2022-0047g | 1.25 | **0.12** | **0.12** | **0.12** | 2022, 2023, 2024, 2025 |
| PROS-2023-0126g | 1.00 | 1.00 | **0.12** | **0.12** | 2023, 2025 |
| PROS-2021-0044g | **0.12** | **0.12** | **0.12** | **0.12** | 2021 |
| PROS-2016-0011g | 1.25 | 1.25 | 1.25 | 1.25 | 2020, by £0.52 |

`GAS_HEAT_PUMP_RESIDUAL_FRACTION = 0.12`. **Three of the four are heat-pump adopters**, and the
years they invert are the years after the pump goes in. The inversion tracks a DEMAND SHOCK, not
a drawing method — a home whose gas use collapses to 12% while the contract it is priced on does
not.

The fourth has no pump, a flat 1.25 multiplier, and inverts by 52 pence. That is a different and
much smaller case, and it is not explained here either.

### What is still true, and it is the part that matters

Unchanged and re-verified: 18 of 611 gas-leg customer-years invert, 0 of 721 electricity ones.
The phenomenon belongs exclusively to the legs this seat added on 2026-08-26, so it remains this
seat's defect to close.

### What is NOT yet established

Which side uses which volume. `annual_pnl` publishes `gross_gbp` and `net_gbp` but no
`revenue_gbp`, so the comparison that would settle it — billed revenue against the volume the
margin was computed on — was not made. Note also that `gross_gbp` goes NEGATIVE for a gas leg in
2022 (PROS-2016-0011g, −£542.39), so any account of this must survive a year where the margin is
a loss.

**No fix should be built on the paragraph above the correction line.** The next step is to read
how a gas leg's `gross_gbp` is derived and compare it against the invoiced volume for one
heat-pump account across the year the pump lands. The control stays RED until that is done, for
the same reason as before: it is a real arithmetic contradiction in this seat's own work, and
absorbing it into a baseline or an xfail is the anti-pattern that file's own docstring names.

---

## RESOLVED, 2026-08-27, and it was neither of my two guesses

**The money was never missing. Only its attribution between the two legs of one household was.**

### The measurement that settled it

Aggregate the 18 inverted supply-point-years to the BILLING ACCOUNT — the leg plus its
electricity sibling — and compare the household's invoices against the household's margin:

```
leg-level inversions:                                    18
of those, still inverted at HOUSEHOLD level (leg+base):   0
```

All eighteen. Not most, not a residue — every one.

### Why

A dual-fuel household is **one billing account with two supply points**. That is not incidental:
it is the property `tests/simulation/test_dual_fuel_wins.py::test_the_two_legs_are_one_billing_account`
asserts, and the entire reason dual fuel reaches cost-to-serve, churn and lifetime value rather
than merely adding rows.

Its INVOICES are cut per billing account. Its SETTLEMENT margin accrues per supply point
(`annual_report`: `gross_gbp = sum(r["margin_gbp"] for r in crecs)`, over settlement records).
Comparing one leg's invoices against that leg's margin compares a part against a
**differently-cut** part, and the remainder surfaces as an arithmetic impossibility.

The heat-pump correlation in the correction above is real and is the AMPLIFIER, not the cause: a
home whose gas demand collapses to 12% has a tiny gas invoice beside an untouched electricity
one, so the mis-split is most visible there. It is why 3 of the 4 sampled accounts had a pump,
and why the fourth — no pump, 52 pence — looked like a different phenomenon. It was the same one,
smaller.

### The fix

The control now compares at the billing account. That is not a loosening: the billing account is
the unit at which billing actually HAPPENS, so it is the only unit at which "billed less than the
margin inside it" is a well-formed claim at all. For a single-fuel account the billing account IS
the supply point, so 703 of the 721 electricity customer-years are compared exactly as before.

Two partners pin both directions, because aggregating makes the haystack bigger and that is how a
comparison quietly stops discriminating:

* `test_the_gate_still_fires_when_a_DUAL_FUEL_HOUSEHOLD_total_inverts` — £60 billed against £500
  of combined margin is still caught.
* `test_one_leg_covering_for_the_other_is_NOT_reported_as_a_break` — the household reconciles,
  the split does not, and the gate stays quiet. That is the shape of the 18.

### What this cost, and the lesson

Two wrong mechanisms before the right one, both published:

1. "The AQ is invented and unreconciled" — wrong; `household_demand` uses `aq_kwh` as its base.
2. "It is heat pumps" — a real correlation, and still not the cause.

Both were plausible shapes reasoned from a distribution. Neither survived one cheap aggregation.
**The measurement that resolved it took thirty seconds and was available from the start**: sum
the two legs. The lesson is not "diagnose more carefully" — it is that when a quantity is split
across a seam, the first question is whether the SPLIT is the defect, before any question about
either side of it. That is the third time in one day this seat has met the same shape: the
household register minting two Households per property, the citation reader stat-ing a label,
and now a control comparing across a cut that billing does not make.

**The control is GREEN and its teeth are intact.** Nothing was absorbed into a baseline and
nothing was xfailed.
