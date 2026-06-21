# UK Energy Consumption Profiles — Research Findings

Sources: DESNZ NEED 2026 report, Ofgem TDCV 2026 review, HoC Library CBP-9768, Elexon BSC docs

## Residential Gas Consumption (NEED 2026 — England & Wales, 2024 metered data)

| Percentile | kWh/year |
|------------|----------|
| P25 | 6,500 |
| Median (P50) | 10,000 |
| P75 | 14,400 |
| Mean | 11,200 |

By property type (NEED 2019 detailed tables, last published disaggregation):

| Property type | Approx median gas (kWh/yr) |
|---------------|---------------------------|
| Purpose-built flat | 5,500–6,500 |
| Mid-terrace house | 8,000–9,000 |
| Semi-detached | 10,000–12,000 |
| Detached | 14,000–17,000 |

**Ofgem TDCV bands (from 1 July 2026):** Low 6,000 / Medium 9,500 / High 14,000 kWh/year  
_(Revised down from 2023: 7,500 / 11,500 / 17,000 — reflects measured consumption falls post-crisis)_

## Residential Electricity Consumption (NEED 2026)

| Percentile | kWh/year |
|------------|----------|
| P25 | 1,600 |
| Median (P50) | 2,500 |
| P75 | 4,100 |
| Mean | 3,300 |

**Ofgem TDCV bands (from 1 July 2026):** Low 1,600 / Medium 2,500 / High 3,800 kWh/year  
_(Down from 2023: 1,800 / 2,700 / 4,100)_

## Time-of-Use Profile (Residential)

Classic morning–evening dual peak:
- Morning peak: ~07:00–09:00 (kettle, shower, toaster)
- Evening peak: ~17:00–21:00 (cooking, TV, heating, lighting) — **dominant**, ~2–3× overnight baseload
- Winter: peaks higher and wider; overnight baseload also higher
- Elexon Profile Class 1 (domestic unrestricted) captures this shape

Economy 7 (Profile Class 2): load shifts to 00:00–07:00 for storage heaters and hot water.

## SME Electricity Consumption (Ofgem / Bionic 2023)

| Tier | Annual electricity | Annual gas |
|------|-------------------|------------|
| Microbusiness | up to 15,000 kWh | up to 10,000 kWh |
| Small business | 15,000–25,000 kWh | 10,000–25,000 kWh |
| Medium business | 25,000–50,000 kWh | 25,000–45,000 kWh |

Sector medians (Bionic broker data): 8,500 kWh (professional services) to 15,000 kWh (retail).

## SME Time-of-Use Profile

Elexon Profile Classes 3–8 (non-domestic). Opposite shape to residential:
- Weekday business hours 09:00–17:00 dominate
- Near-flat overnight and weekends (office/retail)
- Hospitality/catering: evening and weekend peaks significant
- Morning ramp (HVAC, IT boot) steeper than residential

## Dual-Fuel Customer Proportions

~75% of UK residential customers take both gas and electricity from same supplier:
- ~70% of electricity customers have dual-fuel accounts
- ~80% of gas customers have dual-fuel accounts
- Electricity-only: ~20% of resi (flats off gas grid, all-electric new builds)
- Gas-only: <5%
- Source: House of Commons Library CBP-9768 (October 2025)

## Smart Meter Coverage (end-2024)

| Segment | Smart meter % |
|---------|--------------|
| Domestic (in-smart-mode) | ~65–67% |
| Non-domestic / SME | ~64% |
| All meters combined | ~66% |

- Market-wide HH Settlement (MHHS) still rolling out 2025–26
- ~13% of installed smart meters had reverted to dumb mode (SMETS1 migration issues)
- HH data truly available for billing: ~30–60% of SME by late 2025 (expanding)

## Implications for Simulation Customer Profiles

Current fixed kWh/year vs NEED-calibrated targets:

| Customer | Current sim kWh/yr | NEED calibrated |
|----------|-------------------|-----------------|
| C1 (resi flat, elec) | ~2,800 | 2,500 median (Ofgem TDCV medium) |
| C1g (gas leg) | ~8,000 | 7,500–10,000 (terrace/semi) |
| C2 (resi semi, elec) | ~3,500 | 2,500–4,100 (P50–P75 range) |
| C2g (gas leg) | ~10,000 | 10,000–12,000 (semi median) |
| C5 (SME small, elec) | ~15,000 | 8,500–15,000 (Bionic microbiz/small) |
| C6 (SME med, elec) | ~45,000 | 25,000–50,000 (medium band) |
| C7–C9 (HH large SME) | ~80,000 | 50,000–100,000 (large non-dom) |

Overall: current sim consumption estimates are in the right order of magnitude.  
Biggest discrepancy: C1 electricity (2,800 vs 2,500 median) is ~12% high;  
C5 (15,000 vs ~10,000 typical micro) is ~50% high.

### Sources

- NEED 2026: https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026/
- Ofgem TDCV 2026: https://www.ofgem.gov.uk/consultation/review-typical-domestic-consumption-values
- HoC Library CBP-9768: https://commonslibrary.parliament.uk/research-briefings/cbp-9768/
- DESNZ Q4 2024 Smart Meters: https://assets.publishing.service.gov.uk/media/67d95f7c4ba412c67701ed58/Q4_2024_Smart_Meters_Statistics_Report.pdf
- Bionic SME consumption: https://bionic.co.uk/business-energy/guides/average-energy-usage-for-businesses/
