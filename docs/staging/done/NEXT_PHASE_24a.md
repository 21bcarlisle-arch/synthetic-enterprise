# Phase 24a: I&C Customer — First Industrial Account

## Status: PROPOSED

## Motivation

All five hollow gaps are addressed at a basic level. The next significant fidelity
improvement is adding an Industrial & Commercial (I&C) customer segment. Real UK energy
suppliers hold a significant I&C portfolio alongside residential and SME customers.
I&C accounts differ in ways that stress-test the simulation architecture:

- Annual consumption 10-100× higher than residential (2-50GWh vs 3-15MWh)
- HH smart-meter data required (already have the path — C7-C9)
- Bill shock is measured in tens of thousands of pounds, not hundreds
- Company's churn model bill-stress signal fires much sooner (Phase 13c logic already
  supports this: `annual_consumption_kwh` param triggers at high-spend thresholds)
- Retention economics are very different (larger CLV, larger retention cost justified)
- Lays the groundwork for flex hedging (Phase 24b)

## What Phase 24a builds

**Add 1 I&C electricity customer: C_IC1**

Consumption: 2,000,000 kWh/year (2 GWh) — large commercial, not mega-industrial
Contract: fixed-price annual contract (12-month term)
Metering: HH (half-hourly smart meter) — real HH data scaled up from existing C7-C9 profiles
Fuel: electricity only (gas in a later phase)
Acquisition: 2017-01-01 (2 years into the simulation, after price feeds established)
Tariff: company tariff engine prices it like a large SME — no special I&C logic yet

## What does NOT change

- No flex hedging yet (follow-on Phase 24b)
- No gas I&C (follow-on)
- No negotiated-rate contract engine
- Existing settlement/hedging engine handles the higher volume without code changes
- Existing churn model handles it (bill-stress signal already fires for high kWh)

## Implementation steps

1. **Add C_IC1 to ELEC_CUSTOMERS** in `simulation/customers.py` or `simulation/run_phase2b.py`
   - `customer_id: "C_IC1"`, `eac_kwh: 2000000`, `acquisition_date: "2017-01-01"`
   - `profile_class: 8` (HH, like C7-C9) — use scaled HH shape
   - `tariff: "fixed"`, `commodity: "electricity"`

2. **HH shape for C_IC1**: scale C7 or C8 shape by factor (C7 ≈ 2,000 kWh/year;
   scaling factor ≈ 1000×). Shape stays the same; volume is higher.

3. **Bill-stress threshold check**: Phase 13c uses £3,000/year as the stress threshold.
   C_IC1 at 2GWh and £150/MWh = £300,000/year annual bill — stress signal fires immediately
   and stays elevated. Verify it doesn't saturate the churn model.

4. **Retention economics**: retention offer cost is `unit_rate × eac_kwh × discount_pct`.
   For C_IC1 at 5% discount: £15,000 cost per offer. Guard condition
   `expected_margin > ret_cost` may fire differently — verify math is scale-invariant.

5. **Treasury sizing**: C_IC1 adds £300k+ revenue per year. Starting treasury should
   absorb first-term working capital (90-day DSO + collateral). Check STARTING_TREASURY_GBP
   is adequate or note if run shows treasury going negative in first period.

6. **Report sections**: C_IC1 should appear in per-customer P&L ranking, retention
   durability, churn avoidability — all are data-driven and scale-invariant.

7. **Tests (8 new)**:
   - C_IC1 appears in ELEC_CUSTOMERS
   - `_company_eac_estimate` works for C_IC1 (high-volume billing records)
   - Bill-stress term fires for C_IC1 at £150/MWh with 2GWh consumption
   - Retention offer cost is proportionally larger for C_IC1
   - `demand_estimation_log` includes C_IC1 entries from 2nd term onwards
   - Annual report P&L ranking includes C_IC1 with large revenue figure
   - `_section_demand_estimation` correctly summarises C_IC1 renewals
   - SIM fast-mode produces C_IC1 records in all_records output

## Expected impact on simulation output

- Revenue: +£250k-£350k/year (depending on pricing and settlement)
- Gross margin: volatile — large volume means large swing in basis risk
- EV: depends on pricing accuracy; first term likely loss (tariff error magnified by scale)
- Crisis 2021-22: C_IC1 will show dramatic losses at 2GWh × £400/MWh spot vs £150/MWh tariff
  — this is realistic (this is what actually killed I&C-heavy suppliers in 2021-22)
- 2023-24: tariff engine with adaptive lookback + regime detection should partially recover

## Dependencies

- Phase 23a: demand estimation (DONE) ✅
- HH data path (DONE — C7-C9) ✅  
- Event lifecycle (DONE — Phase 12b+) ✅
- Company tariff engine with adaptive lookback + regime detection (DONE — 14c/18a) ✅

## Token estimate

~1.5 frontier sessions (design + implementation + tests + run verification)
