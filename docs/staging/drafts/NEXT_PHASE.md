# Phase H: Electricity EAC Multiplier at Term Signing

Status: PROPOSED (2026-06-29)

## The gap

`eac_multiplier_for_date()` in `household_demand.py` was built in Phase F and computes:

    epc * (1 + ev_fraction + ashp_fraction) * max(0, 1 - solar_fraction)

It has ZERO production call sites for electricity. Compare:
- Gas (Phase D): `gas_eac_multiplier_for_date()` applied to `aq_kwh` at term signing (line 1236)
- Electricity: `eac_multiplier_for_date()` never called

The settlement SHAPE correctly reflects EV, solar, ASHP (Phases C/G/25a).
But the company's EAC ESTIMATE at term signing does not.
Effect: the company under-hedges EV customers (EAC understates electricity need)
and over-hedges solar customers (EAC ignores self-generation offset).

## What Phase H does

Modify `_company_eac_estimate()` to accept a `base_eac_override` kwarg:
    return estimated if estimated > 0 else (base_eac_override or EFFECTIVE_EAC_KWH.get(cid, 0.0))

At electricity term signing (run_phase2b.py ~line 1102):
    _elec_mult = household_demand_register.eac_multiplier_for_date(cid, term_start_str)
    _adj_base = max(1, round(EFFECTIVE_EAC_KWH.get(cid, 0.0) * _elec_mult))
    eac_kwh = _company_eac_estimate(cid, term_start_str, all_records, base_eac_override=_adj_base)

Logic:
- First term (no billing history): base_eac_override is used → adjusted for EV/solar/ASHP ✓
- Renewal terms (billing history exists): billing history used unchanged → no double-counting ✓

## Expected effects on run output

EV customers (C2, C4): electricity EAC higher on first term → company hedges more volume,
prices to recover margin over true annual consumption. Imbalance risk reduced.

Solar customers (C4): electricity EAC lower on first term → company expects lower volume,
prices correctly for net-import-only customer.

ASHP customers: electricity EAC higher on first term (5,500 kWh uplift captured),
matching Phase G's settlement effect. Completes dual-fuel ASHP picture: gas -88% at term
signing (Phase D) + electricity +ASHP at term signing (Phase H).

## Scope

Files to change:
- simulation/run_phase2b.py: 4 lines (compute _elec_mult, _adj_base, call with override)
- simulation/run_phase2b.py: 2 lines (_company_eac_estimate kwarg + fallback line)

Tests to add (~12):
- eac_estimate uses adjusted base on first term with EV
- eac_estimate uses billing history on renewal term (no override applied)
- eac_estimate uses adjusted base on first term with solar (reduction)
- eac_estimate uses adjusted base on first term with ASHP
- multiplier applied when household_demand_register present
- no multiplier applied when household_demand_register absent (guard)
- eac_kwh consistent with gas side (Phase D parallel)
