# Four front-door domain points from the energy cold read, checked against the published record

**Knowledge:** imbalance-cashout-settlement

Research completed: 2026-10-22, delivery seat, on the item
`front-door-four-domain-points-from-the-cold-read`. The four points were raised by the energy
cold reader of the director's front-door steer (`docs/status/SEAT_STRETCH_LOG.md`, entry "The
front door steer, done", "Not fixed, and why"). Per K4, the reader's points were treated as the
starting point. Each was checked against the published record before the page changed.

| # | The reader said | Verdict | What the page now says |
|---|---|---|---|
| 1 | Domestic supply 2016–2025 was mostly profile-settled, so "each household's metered half hours" overstates what a 2018 supplier had | **Right.** It also exposes a divergence in the run itself (finding filed) | the carbon story is scoped to homes with a half-hourly read; the Settlement line names profile settlement |
| 2 | Triads ended in April 2023 | **Partly right.** The residual left Triad. The locational element stayed on Triad, now small and zero in seven zones | no front-door claim depended on it; the register's docstring and a finding carry it |
| 3 | The 2014 CMA survey has newer Ofgem figures | **Partly right.** Ofgem 2017 is newer for homes with both fuels. No newer whole-population share is published | the story cites both |
| 4 | £273/tCO₂e needs its price base | **Right.** It is DESNZ's 2025 central value in **2022 prices** | "(2025), in 2022 prices" |

## 1. Domestic settlement 2016–2025 was profiled, not half-hourly

**What the rules were.** Under the BSC, a domestic meter in this decade was settled
non-half-hourly (Measurement Class A). The supplier was settled on its Estimated Annual
Consumption spread across the half hours by Elexon's published profile for the meter's Profile
Class: 1 for domestic unrestricted, 2 for domestic Economy 7. GSP Group Correction then scaled the
total to what the grid supply points measured. Reconciliation runs up to RF at 14 months
(`elexon_settlement_run_timetable_verified.md`) corrected the **annual volume** as reads arrived.
They did not correct the **shape**: a profiled home's settled half hours are the profile's, never
its own.

- P272 (2016–17) moved Profile Classes 5–8 to half-hourly settlement. It was non-domestic only.
- P300 created Measurement Class F, so a domestic smart meter could be settled half-hourly
  *electively*. Few were.
- **Elexon, Trading Operations Report (metering data): on 25 May 2022, Measurement Class A (NHH)
  was 98.54% of all SVA metering systems, including domestic smart meters settled under the NHH
  arrangements.**
- Market-wide Half-Hourly Settlement went live centrally on 24 September 2025, after the run's
  `REPORT_END` (2025-06-07). Meters migrate between September 2025 and May 2027, and the two
  regimes run side by side until July 2027 (Elexon, 22 Oct 2025; MHHS programme timetable).

So a 2018 supplier settled almost every home it served on a profile. Most of those homes had no
half-hourly read the supplier could see. Where a smart meter had one, the supplier needed the
household's consent to collect it at half-hourly granularity (`smart_meter_hh_data_consent_2026.md`).

**What the run does.** Two different things, and the front door had run them together.

- *The company's carbon instrument* reads a home's half hours only where it holds a half-hourly
  read. In the published run that is **3 of 963 accounts** (`site/data/explore_carbon.json`,
  `coverage_statement`). The other 960 are profiled, and their timing effect is reported as
  unavailable. This part is faithful. The front-door story "Each household's metered half hours are
  multiplied…" overstated it, as the reader said.
- *The world's settlement* charges each home's **own** modelled half hours
  (`simulation/run_phase2b.py`, the per-customer `shape_fn`: the fabric trace where the weather
  store covers a home, otherwise the PC1 shape weather-adjusted and levelled to the home's EAC).
  That is what MHHS does, not what 2016–2025 did. For a legacy home without fabric coverage, the
  difference is small, because its shape is the PC1 profile. For a fabric home, or one with a
  battery or a shifted load, the run's wholesale and imbalance cost carry a timing difference a
  real supplier of the period would not have been charged. **Filed as
  `SEAT_FINDING_THE_RUN_SETTLES_EACH_HOMES_OWN_HALF_HOURS_WHERE_THE_PERIOD_SETTLED_A_PROFILE_2026-10-22.md`.**
  The direction favours the thesis (F11), and its size is not measured.

`company/regulatory/settlement_reconciliation.py` already carries the profile-class distinction as
a reconciliation variance band (±4% NHH, ±0.5% HH). That models the volume true-up, not the shape,
so it is consistent with the above and is not itself in error.

## 2. Triad after the Targeted Charging Review (April 2023)

**Source read directly:** NESO, *Final TNUoS Tariffs for 2023/24* (January 2023),
`https://neso.energy/document/275736/download`, §8 and Tables 8–10.

- "Through the approval and decision of CMP343 the demand residual tariff will no longer exist and
  will not be included in locational tariffs. The revenue to be recovered through the demand
  residual will now be recovered by a new set of p/site/day charges on final demand users (both
  HH and NHH), based on site specific banded charges starting April 2023."
- "Demand customers will continue paying the locational elements of demand tariffs, based on
  their triad demand for HH demand or their aggregated annual consumption during 4-7pm each day for
  their NHH demand. As per CMP343, HH and NHH demand locational tariffs are floored at zero from
  2023/24".

**So Triad did not end in April 2023. What ended was Triad carrying the residual.** The element
still charged on Triad demand, for half-hourly-settled sites only, is the locational one:

| 2023/24 final | Value |
|---|---|
| Average gross HH demand tariff (Triad, locational only) | **£5.59/kW** |
| HH demand tariff, zones 1–7 (Scotland, North, NW, Yorkshire, N Wales & Mersey, E Midlands) | **£0/kW** (floored) |
| HH demand tariff, highest zone (14, South Western) | £7.65/kW |
| HH demand tariff, zone 12 (London) | £4.37/kW |
| Average NHH locational tariff (4–7pm kWh) | 0.27 p/kWh |
| **Domestic** demand residual, one band for all domestic sites | **£0.119264/site/day** (≈ £43.53/yr) |

Against 2022/23's HH demand tariff of about £63.75/kW in zone 14
(`network_charges_uk_2016_2024.md` §6a), the Triad signal fell by roughly an order of magnitude.
Drax gives the locational element as about 3% of the old total
(`https://energy.drax.com/insights/end-of-triads-tnuos-charges-changing/`).

**Two errors this exposes in our own record:**

- `network_charges_uk_2016_2024.md` §3b gave the domestic residual as five consumption bands
  (£44–£119/yr). NESO's Table 10 has **one** domestic band at £0.119264/site/day. The banded
  structure belongs to non-domestic sites (LV_NoMIC_1–4, LV1–4, HV, EHV, T-Demand). The research
  doc is corrected beside the claim.
- `company/market/triad_notification_book.py` (`_TNUOS_TRIAD_RATE_GBP_PER_KW`: 2023 £66.30, 2024
  £70.10, 2025 £73.50) carries the pre-TCR Triad charge rising straight through April 2023, and
  `company/trading/triad_exposure_register.py` defaults its tariff to £80/kW, labelled "typical
  residential". Residential sites were never charged per kW of Triad demand. **Filed as
  `SEAT_FINDING_THE_TRIAD_RATE_TABLES_CARRY_THE_PRE_TCR_CHARGE_PAST_APRIL_2023_2026-10-22.md`.**
  Industrial and commercial supply is suspended, so no current run reads these rates through a
  live account. That is why the finding is filed and not fixed in this turn.

The register's 2023-24 and 2024-25 seasons are not wrong as seasons. NESO still identifies
Triads, and HH sites are still charged on them.

## 3. Dual-fuel share: the newest published figures

The full table is in `how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md`
§2. This check asked only whether anything newer than it exists.

- **CMA/GfK customer survey, fieldwork September 2014** (n = 6,999): 72% of all households on one
  supplier for both fuels; 72/81 ≈ 89% of homes with gas.
- **Ofgem Consumer Engagement Survey 2017** (Ipsos MORI, n = 4,001): 91% "bought gas and
  electricity from the same supplier". It is the newest Ofgem survey found that **publishes** the
  share.
- Ofgem's 2018, 2019 and 2020 Consumer Surveys still ask it (Q150, "Gas and electricity from same
  supplier", filter F173 in the 2019 and 2020 technical reports). The technical reports and the
  2020 "Update on Engagement" summary do not print the result, and the 2018–2020 *Consumer
  Perceptions* tracker defines "Dual Fuel" without reporting its share. **GAP:** the data tables
  that would hold the 2018–2020 figures were not found. DESNZ publishes no dual-fuel share. The
  supplier-accounts evidence in the existing doc (§5: British Gas 2023, Octopus FY24/25 G/E) is
  newer, but it covers individual books, not the market.

So the front door now cites the CMA's 2014 share of all homes alongside Ofgem's 2017 figure for
homes with both fuels. The draw's own anchors (`dual_share_of_gas_homes` 0.90) already rest on
Ofgem 2017, and nothing changes in the code.

## 4. The £273/tCO₂e yardstick's price base

- BEIS, *Valuation of greenhouse gas emissions: for policy appraisal and evaluation* (September
  2021), Annex 1, "Carbon values in £2020 prices per tonne of CO2": 2025 low £130, **central £260**,
  high £390.
- DESNZ, *Valuation of energy use and greenhouse gas emissions for appraisal*, November 2023
  data tables (Table 3), rebased to **2022 prices**: 2024 central £268.97 (as reproduced by the
  `greenbook` R package's vignette). A 2025 central of **£273** is consistent with both:
  it is £260 uplifted by about 5%, roughly the 2020→2022 GDP deflator, and it sits on the path
  between £268.97 (2024) and £294.50 (2030). It was not read off the DESNZ table itself here, so
  that check is inferred, not read. The range is about ±50%.

So **£273/tCO₂e is the 2025 central value in 2022 prices**. That is what
`docs/design/E5_EMISSIONS_FACTOR_REGISTER_DISCOVER.md` already recorded ("2025, 2022 prices,
±50%"), and the front door left the price base out. The page now says "(2025), in 2022 prices".

## What is still not known (GAP)

- The 2025 row of DESNZ's November 2023 Table 3 itself, read directly (§4 is two-sided inference).

- The size of the settlement-shape divergence in §1 for fabric homes. A measurement is owed, and
  it is named in the finding.
- The Ofgem 2018–2020 dual-fuel share (§3).
- How many domestic MPANs were electively half-hourly settled in 2016–2025. The 98.54% NHH share
  is of all SVA metering systems on one date. A count per year would need Elexon's TOR CSVs.
