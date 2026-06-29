# Phase S: Time-of-Use Tariff Profitability Differentiation

**Status:** Draft proposal — 4h opt-out gate.
**Proposed by:** Claude Code (Phase R session), 2026-06-29
**Precondition:** Phase P (EV overnight shape) must be complete.

---

## Context

Phase P gives EV customers an overnight-weighted demand shape (90% periods 47-48, 1-14).
This is exactly the profile that makes EV customers ideal Time-of-Use (ToU) tariff candidates.

Currently, the profitability model (Phase J: CustomerProfitabilityBook) treats all customers
with the same unit rate. A ToU tariff for EV customers has different economics:
- Overnight rate (~10p/kWh): supplier pays low wholesale (overnight = baseload)
- Peak rate (~35p/kWh): supplier pays high wholesale (16:00-19:00)

An EV customer on ToU:
- 90% of EV demand charged at overnight rate (low wholesale, cheap for supplier)
- Standard home load partially at peak rate

An EV customer on standard flat tariff:
- All demand billed at uniform rate, but wholesale cost is overnight-heavy
  → supplier buys cheap overnight, bills at flat rate → margin > standard customer

This distinction matters for product strategy: should EV customers get a dedicated ToU
tariff (lower unit rate in exchange for honest overnight pricing), or is the flat-rate
cross-subsidy from overnight profile valuable to the supplier?

---

## What Phase S does

New module: `company/pricing/tou_tariff_assessor.py`

Assesses the profitability difference between:
1. Standard flat tariff for an EV customer
2. ToU tariff (overnight/peak/standard band rates) for the same customer

Inputs (all observable):
- Customer's annual kWh (from billing history)
- Whether customer has EV (from CRM/smart meter data)
- HH demand shape class: overnight-heavy (EV) vs flat vs peak-heavy
- ToU rate bands: overnight/standard/peak as multipliers on base rate
- Wholesale cost by band: overnight cheaper (~£30/MWh), peak expensive (~£120/MWh 2022)

Key outputs:
- `ToUProfitabilityComparison`: flat_margin_gbp vs tou_margin_gbp vs standard_margin_gbp
- `is_tou_beneficial_for_supplier`: True if ToU gives better margin than flat
- `customer_saving_gbp`: customer benefit from ToU (negative = ToU costs customer more)

---

## Files

- `company/pricing/tou_tariff_assessor.py` (new): ~100 lines
- `tests/company/pricing/test_tou_tariff_assessor.py` (new): ~15 tests

---

## Tests (~15)

- EV customer on flat tariff: margin higher than non-EV (overnight wholesale cheaper)
- EV customer on ToU: customer pays less (overnight is cheap), but supplier margin lower
- Non-EV customer on ToU: no benefit (flat-ish demand doesn't shift costs)
- 2022 crisis: peak rate (35p/kWh) >> overnight (10p/kWh) → ToU spreads risk
- Standard customer on ToU: neutral or slightly worse vs flat
- is_tou_beneficial_for_supplier: False for EV customer (overnight cross-subsidy better)
- customer_saving_gbp: positive for EV customer on ToU (they save on cheap overnight)
- supplier_margin_comparison keys present
- Frozen dataclass: cannot modify assessment after creation
- Wholesale band rates calibrated to 2022 SSP (crisis) vs 2019 (normal)
- ToU rate bands sum correctly (overnight + standard + peak fractions = 1.0)
- ASHP customer: HDD-weighted shape → mostly winter → not a good ToU candidate
- Battery customer: ToU peak = peak export → very different economics
- Rate structure: overnight_multiplier < 1.0 < peak_multiplier
- Portfolio: supplier identifies which EV customers to target for ToU vs retain on flat

---

## Fidelity delta

Ofgem has mandated ToU capability for smart meter customers (SMETS2, MHHS 2024-2025
rollout). EV tariffs are a major market segment: Octopus Go (7p overnight), Ovo Charge
Anytime, British Gas Electric Drivers — all based on overnight cheap electricity. Without
this model, the simulation cannot assess whether the supplier should proactively offer ToU
to EV customers or retain the flat-tariff margin from their overnight profile.

---

## Gate

4h opt-out from proposal time. Proceed when Phase P is complete AND gate has passed.
