# Phase 29a: Network Charges (DUoS + TNUoS) in Settlement P&L

## Context

The simulation currently includes:
- Commodity cost (Elexon SSP)
- Policy costs: RO levy (Phase 21a), CfD levy (Phase 21a), CCL for business (Phase 27b)

Missing: Network charges, which are ~£32-46/MWh for residential/SME (2016-2024).
Source data is in `docs/market_research/historical_policy_costs_2016_2024.md` Section 3.

This makes our absolute P&L numbers ~£32-46/MWh too low on both cost and revenue. The
commodity P&L is internally consistent, but the full tariff stack doesn't match real UK
supply economics.

## Network charge architecture

**Residential/SME (LV connected):**
- DUoS: ~£20-25/MWh (distribution use of system)  
- TNUoS: ~£12-14/MWh (transmission use of system, unit rate for domestic)
- Combined: ~£32-46/MWh rising 2016→2024
- Source: Ofgem price cap Annex 3 (post-2019); historical estimates (pre-2019)

**I&C HV connected (C_IC1, C_IC2):**
- DUoS: ~£8-12/MWh (HV rate, lower than LV)
- TNUoS: Triad-based annual charge (already tracked in Phase 27d — NOT per-period)
- For settlement records: only add DUoS (~£10/MWh) 
- Triad TNUoS remains as annual exposure tracker (not per-period)

## Year-indexed table (residential, mid-point estimates)

| Year | Network cost (£/MWh) |
|------|---------------------|
| 2016 | 35.0 |
| 2017 | 36.0 |
| 2018 | 37.0 |
| 2019 | 38.0 |
| 2020 | 38.0 |
| 2021 | 38.0 |
| 2022 | 43.0 |
| 2023 | 44.0 |
| 2024 | 46.0 |

I&C DUoS only (approx 30% of residential rate):
| Year | I&C DUoS (£/MWh) |
|------|-----------------|
| 2016-2020 | 11.0 |
| 2021-2022 | 12.0 |
| 2023-2024 | 13.5 |

## Implementation scope

### `simulation/policy_costs.py`
Add `get_electricity_network_cost_per_mwh(date_str, segment="resi")`:
- Returns combined DUoS + TNUoS for resi/SME segment
- Returns DUoS-only for I&C segment (Triad TNUoS tracked separately)
- Year lookup uses calendar year from date_str

### `simulation/hedged_settlement.py`
Add `network_cost_gbp` field to settlement records:
- `network_cost_per_mwh = get_electricity_network_cost_per_mwh(settlement_date, segment)`
- `network_cost_gbp = consumption_kwh / 1000 × network_cost_per_mwh`
- Separate from `policy_cost_gbp` (which has RO + CfD + CCL) 
- `net_margin_gbp = margin_gbp - policy_cost_gbp - network_cost_gbp - capital_cost_gbp`

### `saas/tariff_pricing.py`
Add `network_cost_per_mwh` parameter to `price_fixed_tariff()`:
- Included in unit rate alongside existing `policy_cost_per_mwh`

### `simulation/renewals.py`
Call `get_electricity_network_cost_per_mwh(term_start_str, segment=cust_segment)` at
tariff build time.

### `saas/reporting/annual_report.py`
`_section_policy_costs()`: add Network column alongside RO, CfD, CCL columns.
Show total cost stack: commodity + network + policy = full supply cost.

## Expected impact

- Gross revenue increases by £32-46/MWh
- Settlement cost increases by £32-46/MWh  
- Net margin % approximately unchanged (internally consistent)
- Absolute P&L numbers become meaningful for real-world comparison
- Gross margin % shifts from ~-3% to show more realistic structure

## Estimated scope
~8 new tests, 2-3 hours. Backward compatible (pre-29a runs use network_cost_gbp=0.0).
