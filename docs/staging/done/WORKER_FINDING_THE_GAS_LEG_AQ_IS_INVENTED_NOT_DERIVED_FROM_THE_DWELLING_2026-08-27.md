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
