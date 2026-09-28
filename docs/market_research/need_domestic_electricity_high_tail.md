# External anchor: the HIGH TAIL of domestic annual electricity consumption

**Knowledge:** none -- no knowledge page covers the distribution of domestic consumption; the nearest, metering-and-reads, covers how reads arrive and not how large a household's year is

**Question:** is a domestic account drawing 19–26 MWh/yr of electricity a real household, or a
defect? Asked of the world account PROS-2016-0098. Sister to `need_domestic_gas_high_tail.md`.
**Measured 2026-09-28** from the publisher's files, blind to any company or value-arm result.

## Source

DESNZ, National Energy Efficiency Data-Framework (NEED) 2026, published 11 June 2026. England and
Wales. `anon2026_50k.csv` is a stratified random sample of 50,000 domestic properties, one row per
dwelling. `NEED-2026-anonymised-dataset-metadata.ods` is its metadata. The population is the
HMRC council tax database (Oct 2025), so every row is a listed dwelling.

The metadata defines the fields used here, verbatim:

> `Econs2005,…,Econs2024` — Annual electricity consumption (not weather corrected) rounded to the
> nearest 100 kWh. Blank values are either missing or removed due to being too large (over 25,000
> kWh) or too small (under 500 kWh). … the 2024 electricity year refers to the months February 2024
> to January 2025.
>
> `ElecValFlag` … G = annual consumption over 25,000 kWh

> `MAIN_HEAT_FUEL` … 1 = gas is the main heating fuel; 2 = gas is not the main heating fuel

`PROP_AGE_BAND 1` = before 1930. `FLOOR_AREA_BAND` 1 ≤50, 2 51–100, 3 101–150, 4 151–200,
5 >200 m². The EPC field is banded `A/B, C, D, E, F/G, No EPC`.

## THE CENSORING FACT — and why it is NOT a domestic ceiling

DESNZ suppresses domestic electricity readings above **25,000 kWh/yr**, so every percentile above
the censored share is unmeasurable. That share is not negligible: **0.34% of all domestic
properties** are flagged G, and so are **1 in 17 of a large pre-1930 detached house without mains
gas**. For gas, the 50,000 kWh cut sat above almost all of the stock and could serve as an
absurdity line (`need_domestic_gas_high_tail.md`). This 25,000 kWh electricity cut is a
statistics filter inside a real domestic tail. **Annual volume cannot tell you where domestic
electricity ends.**

## Measurement — 2024 electricity year

Percentiles are over valid readings (`V`). "n" counts V plus G. **G share** is the share above
25,000 kWh, a floor on the true exceedance.

| class | n | median | p90 | p95 | p99 | **G >25k** |
|---|---:|---:|---:|---:|---:|---:|
| all domestic | 45,369 | 2,600 | 6,400 | 8,600 | 14,300 | **0.34%** |
| gas-heated | 37,043 | 2,500 | 5,600 | 7,300 | 12,200 | 0.17% |
| gas not main heating fuel | 8,326 | 3,200 | 9,600 | 12,100 | 18,200 | 1.10% |
| … detached | 1,111 | 4,450 | 12,710 | 16,000 | 22,500 | 4.59% |
| … detached, pre-1930 | 499 | 4,900 | 13,540 | 17,395 | 23,274 | 7.01% |
| **… detached, pre-1930, 151–200 m²** | **118** | 4,500 | 9,100 | 13,700 | *19,240* | **5.93%** |
| … detached, pre-1930, >200 m² | 204 | 6,500 | 16,020 | 18,360 | *23,646* | 12.75% |
| … detached, pre-1930, EPC F/G | 83 | 5,500 | 14,220 | 15,720 | *18,912* | 4.82% |
| … semi, pre-1930, 51–100 m² | 112 | 3,450 | 11,750 | 13,680 | 17,146 | 0.00% |

*Italicised p99s lie above the censored share and are biased LOW.* The bold row's G share is
stable across years: 5.83% in 2018, 5.74% in 2019, 5.69% in 2021, 6.35% in 2022.

**The bias runs against the conclusion.** "Gas not main heating fuel" includes oil, LPG and solid
fuel homes, which use far less electricity than a direct-electric home. So the tail of a
direct-electric class is heavier than these rows show.

## What it settles for PROS-2016-0098 and PROS-2016-0092

The world drew both premises (`simulation.live_population._live_homes`, base seed):

| account | dwelling | heating | world annual use (billed, full years) | class position |
|---|---|---|---|---|
| PROS-2016-0098 | detached, pre-1919, 6 bed, floor band 4 (151–200 m²), EPC F, poor insulation, no mains gas, no EV/PV | direct electric | 26,345 (2017), 21,406 (2018), 18,781 (2019) | ~p93 (2019) up to the class's top 5.9%, above the 25k cut (2017) |
| PROS-2016-0092 | semi, pre-1919, 2 bed, floor band 2 (51–100 m²), EPC F, poor insulation, no mains gas | direct electric | 10,889 (2016, 10 months) | ~p90 of its class |

Both are **genuine domestic tails**: direct-electric heating in poorly insulated old stock, with a
heating-shaped year. PROS-2016-0098 bills 200–500 kWh in each summer month and 4,000–5,100 kWh in
January. A business load does not have that shape.

## Consequence for the company's ceilings (recorded, not acted on here)

`RESI_CONSUMPTION_ENVELOPE_ELEC` (15,000/yr) and `_ELEC_MONTHLY` (2,100 per ~30 days) come from
"observed sim population plus headroom", not from a source. Both sit inside the published domestic
tail, and the national scalar is the wrong shape for the reason the gas doc gives. They are left as
they are because they are the SCREEN. What was missing was the step a real supplier takes after it:
confirming the premise. That step is `company/billing/pre_bill_validation.release_confirmed_domestic`.

## Sources

- [NEED anonymised data 2026 (DESNZ, 11 June 2026)](https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-anonymised-data-2026)
  — `anon2026_50k.csv`, `NEED-2026-anonymised-dataset-metadata.ods`
