# Phase 29b: Network Charge Calibration (Ofgem Annex 9)

## Motivation

Phase 29a introduced network charges with mid-range estimates (£35-46/MWh resi 2016-2024).
R&D agent found Ofgem Annex 9 data showing significantly higher figures, particularly
post-2022 due to BSUoS (Balancing Services Use of System) moving 100% to demand side:

| Year   | Phase 29a table | Annex 9 actual | Difference |
|--------|----------------|----------------|------------|
| 2016   | £35/MWh        | ~£42-44/MWh    | +£7-9      |
| 2020   | £38/MWh        | £45.89/MWh     | +£7.9      |
| 2021   | £38/MWh        | £49.42/MWh     | +£11.4     |
| 2022   | £43/MWh        | £66.24/MWh     | +£23.2     |  ← BSUoS shock
| 2023   | £44/MWh        | £74.56/MWh     | +£30.6     |
| 2024   | £46/MWh        | £68.95/MWh     | +£22.9     |

The 2022-2024 gap (£23-30/MWh) is material — for 3 GWh I&C volume, this is
£70-90k of annual cost that should be visible in P&L (and in the tariff pass-through).

Note: Ofgem Annex 9 NC total includes BSUoS. Whether to include BSUoS:
- **Include**: More realistic total network cost; Ofgem price cap methodology includes it
- **Exclude**: BSUoS is a balancing charge, not strictly "network"; would need its own line
- **Decision**: Include in combined network cost (consistent with how Ofgem treats it in price cap)

## Scope

**One file change only**: `simulation/policy_costs.py`

Update `_NETWORK_COST_RESI_SME_BY_YEAR` from:
```python
_NETWORK_COST_RESI_SME_BY_YEAR = {
    2016: 35.0,  2017: 36.0,  2018: 37.0,  2019: 38.0,  2020: 38.0,
    2021: 38.0,  2022: 43.0,  2023: 44.0,  2024: 46.0,
}
```
To Ofgem Annex 9 calibrated values (converting Apr-Mar year to calendar year, rounding):
```python
_NETWORK_COST_RESI_SME_BY_YEAR = {
    2016: 43.0,   # 2016/17 est from Annex 9 trend
    2017: 44.0,   # 2017/18: £43.67/MWh
    2018: 42.0,   # 2018/19: £42.41/MWh
    2019: 45.0,   # 2019/20: £44.96/MWh
    2020: 46.0,   # 2020/21: £45.89/MWh
    2021: 49.0,   # 2021/22: £49.42/MWh
    2022: 66.0,   # 2022/23: £66.24/MWh (BSUoS 100% demand-side from Apr 2022)
    2023: 75.0,   # 2023/24: £74.56/MWh (RIIO-ED2 start)
    2024: 69.0,   # 2024/25: £68.95/MWh
}
```

I&C DUoS table: already directionally correct (£11-14/MWh). Calibration optional.

## Test changes needed

- Update `test_phase29a_network_charges.py` test_resi_network_cost_2020 (38→46)
- Update test_ic_rate_lower_than_resi (assertion still valid, just verify)
- Update test_2022_step_up (still true: 66 > 49)
- Add test_2022_bsuos_step_change: rate_2022 > rate_2021 * 1.3 (significant step)

## Expected P&L impact

- 2022 network cost deducted from net_margin increases by +£23/MWh × consumed MWh
- Tariff pass-through ALSO increases by same amount → net margin impact is basis risk only
- BUT: if prior terms were priced at old rates and delivered under new rates, cross-year
  contracts (July 2021 start, June 2022 delivery) would experience margin compression
- This creates a NEW visible effect: 2022 cross-year contracts took a network charge shock
  ON TOP of the CfD rebate story — this is authentic (real suppliers faced this too)

## Source

`docs/market_research/network_charges_uk_2016_2024.md` Section 1a (Ofgem Annex 9 v1.10)
