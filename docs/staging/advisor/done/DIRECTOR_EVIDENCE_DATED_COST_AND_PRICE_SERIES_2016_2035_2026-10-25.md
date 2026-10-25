# Director evidence: dated cost and price series 2016 2035

**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 06:03 GMT: "I'm worried you are using static costs and %. The EV percentage is irrelevant. It should be derived from miles driven and car type etc."
- 06:42 GMT: "NB driveways matter too, as it only really makes sense to have an ev if you can charge from home"

This pack is one of six that supply the attribute distributions for the personalised asset world (`DIRECTOR_STEER_ASSET_DEMAND_IS_DERIVED_PER_HOME_NOT_A_STATIC_PERCENTAGE_2026-10-25.md`). The cover steer is `DIRECTOR_STEER_THE_ASSET_DESIGN_NOTE_HAS_ITS_DISTRIBUTIONS_2026-10-25.md`.

## What to do with it

- Use the "distributions to draw from" table as inputs to the asset design note.
- Use the "population checks" as aggregate calibration claims. Never use them as per-home targets.
- Treat each named gap either as a fetch for you (many were blocked in the advisor's sandbox) or as a design choice you name explicitly.
- Publish it as a Knowledge page. That is drafting work and runs alongside the serial queue.

---

# Poesys evidence pack: dated GB household cost and price series, 2016–2025, with projections to 2035

*Compiled 25 Oct 2026. I could not download any files directly (outbound curl was blocked), and gov.uk xlsx links were outside the fetch allowlist, so I read values from gov.uk HTML/CSV previews, PDFs and secondary reports. The web-search budget ran out before ONS CPI/RPI, Auto Trader, DESNZ fossil fuel price assumptions and the Green Book table values were covered. These appear under Named gaps. Tags: [derived] means my own arithmetic. [unverified] means from memory and not confirmed this session.*

---

## 1. Road fuel (petrol and diesel pump prices)

**Weekly road fuel prices** (DESNZ, accredited official statistics). https://gov.uk/government/statistics/weekly-road-fuel-prices
- Frequency is weekly (week commencing Monday). The latest release is 20 Oct 2026, covering the week of 19 Oct 2026.
- Files: Excel `Weekly_Fuel_Prices_19-10-26.xlsx`, CSV 2018–2026, CSV 2003–2017, and XML. Licence is OGL v3.0.
- Columns: ULSP and ULSD pump price (p/litre), the duty rate for each (p/litre), and the VAT % for each. CSV preview: https://www.gov.uk/csv-preview/6aba69e2a9c3d267bcccefa8/CSV__2018_-__.csv
- Granularity is the UK average only. There is no regional breakdown and no spread between forecourts.

| Week | ULSP (petrol) | ULSD (diesel) | Duty |
|---|---|---|---|
| 02/07/2018 | 126.54 | 130.83 | 57.95 |
| 07/01/2019 | 120.27 | 130.33 | 57.95 |
| 04/07/2022 (peak) | 191.55 | 199.22 | 52.95 (cut from 28/03/2022) |
| 06/01/2025 | 136.6 | 143.3 | 52.95 |
| 07/07/2025 | 133.19 | 140.58 | 52.95 |
| 29/12/2025 | 135.34 | 144.59 | 52.95 |
| 12/10/2026 | 175.28 | 200.04 | 52.95 |

Source for every row: the CSV preview above. VAT is 20% throughout.

- QEP Sept 2026 confirms the 2026 spike. Mid-Sept 2026 petrol was 168.8p (+26.1% y/y) and diesel 191.3p (+35.1%). QEP attributes the wider rise in oil prices to the Middle East conflict. https://assets.publishing.service.gov.uk/media/6aba2810fe72ed1e2b02f0e7/Quarterly_Energy_Prices_September_2026.pdf
- I have no 2016 value. The 2003–2017 CSV was not readable here. Around 110p for petrol in mid-2016 is [unverified].

## 2. Retail electricity and gas

**Ofgem price cap levels** (quarterly since Oct 2023, six-monthly before that; started 1 Jan 2019)
- Unit rates and standing charges, with regional tables and payment-method tables: https://www.ofgem.gov.uk/information-consumers/energy-advice-households/energy-price-cap-unit-rates-and-standing-charges
- Regional lookup: https://ofgem.gov.uk/energy-advice-households/get-energy-price-cap-standing-charges-and-unit-rates-region
- Granularity: 14 regions × payment method (direct debit, standard credit, prepayment) × single or multi-rate. Format is HTML tables. The underlying Ofgem cap models are xlsx [unverified that they were reachable].

| Period | Elec unit (p/kWh) | Elec SC (p/day) | Gas unit (p/kWh) | Gas SC (p/day) | Source |
|---|---|---|---|---|---|
| Jan–Mar 2019 | — | — | — | — | Typical dual-fuel bill only: £1,137. Apr–Sep 2019: £1,254 DD, £1,242 PPM. https://www.ofgem.gov.uk/system/files/docs/2019/02/default_tariff_cap_level_-_letter.pdf |
| Apr–Sep 2022 | ~28 | ~45 | ~7 | ~27 | Secondary source, rounded: https://www.uktaxcalculators.co.uk/tax-news/2022/08/10/cost-of-living-crisis-and-current-support/ |
| From 1 Oct 2022 (Energy Price Guarantee) | 34 | 46 | 10.3 | 28 | https://www.which.co.uk/news/article/liz-trusss-energy-guarantee-puts-price-cap-at-2500-for-a-typical-household-for-two-years-aitQB9G0bkD5 |
| Apr–Jun 2023 (cap level; the EPG still applied) | 51 | 53 | 13 | 29 | https://www.ofgem.gov.uk/publications/ofgem-announces-latest-quarterly-price-cap-update |
| Jul–Sep 2025 | 25.73 | 51.37 | 6.33 | 29.82 | https://moneytothemasses.com/news/energy-price-cap-october-2025 |
| Oct–Dec 2025 | 26.35 | 53.68 | 6.29 | 34.03 | Same source |
| Jan–Mar 2026 | 27.69 | 54.75 | 5.93 | 35.09 | https://moneytothemasses.com/news/ofgem-raises-energy-price-cap-jan-26 |
| Oct–Dec 2026 | 26.32 (0% VAT) | 54.83 | 7.97 | 29.68 | Ofgem rates page above |

- The Oct–Dec 2026 typical bill is £1,723. Ofgem says the bill would have been about £45 higher without the VAT change. https://ofgem.gov.uk/press-release/energy-price-cap-will-rise-4-october-2026
- Oct–Dec 2025 electricity without VAT works out at 25.10p [derived: 26.35/1.05]. Use this when comparing with the 0%-VAT period.

**Spread between regions and payment methods** (Jan–Mar 2025, electricity, incl. VAT; Ofgem regional page above)

| Payment method | Standing charge range (p/day) | Unit rate range (p/kWh) |
|---|---|---|
| Direct debit, single rate | London 41.57 to Northern 72.09 | Northern 23.51 to London 26.06 |
| Standard credit | 46.20 to 78.74 | 24.75 to 27.43 |
| Prepayment | Same as direct debit | 22.70 to 25.23 |

**DESNZ Quarterly Energy Prices (QEP)** (quarterly; OGL)
- https://www.gov.uk/government/statistics/quarterly-energy-prices-september-2026
- Domestic tables 2.2.x (electricity) and 2.3.x (gas) give annual bills and unit costs by payment method and region. Tables 2.2.4 and 2.3.4 split each into unit price and fixed charge.
- From the 2026 releases, bills are calculated at fixed consumptions of 3,400 kWh electricity and 11,200 kWh gas (QEP Sept 2026 PDF above).
- Baseline for about 2016 (calendar 2015, from QEP Mar 2016 tables): https://assets.publishing.service.gov.uk/media/5a81b44640f0b62305b9062b/QEP_Mar_2016_Tables_2.pdf
  - Electricity: direct debit 14.71p/kWh including standing charge, regional range 14.17p to 16.13p. Credit 16.20p, prepayment 16.26p. Bill £559 DD on 3,800 kWh.
  - Gas: direct debit 4.54p/kWh, regional range 4.41p to 4.68p. Credit 5.07p. Bill £681 DD on 15,000 kWh.

## 3. Solar PV installed cost

**Solar PV cost data** (DESNZ, using the MCS Installation Database; annual release each late May since 2014; Excel and ODS; OGL)
- https://www.gov.uk/government/statistics/solar-pv-cost-data and https://www.data.gov.uk/dataset/solar-pv-cost-data
- Granularity: £/kW by month within each financial year, split by size band (0–4, 4–10, 10–50 kW).
- It comes on two bases:
  - DNC, comparable back to 2013/14.
  - TIC, available from 2023/24 and labelled "official statistics in development". TIC costs run 6–12% lower than DNC.
- 2024/25 medians: 0–4 kW £1,876/kW (−19% y/y), 4–10 kW £1,780/kW (−21%), 10–50 kW £1,256/kW. https://www.pv-magazine.com/?p=305960
- Back-calculating gives about £2,316/kW for 0–4 kW in 2023/24 [derived: 1,876/0.81].
- I could not open the 2016/17, 2019/20 or 2021/22 medians or the quartiles. The xlsx files were blocked. **Gap.**

## 4. Battery storage installed cost

There is no gov.uk dataset page that I could confirm. A DESNZ/MCS release reported by Solar Power Portal (2 Jun 2025) covers Apr 2024 to Mar 2025: 22,398 systems. https://www.solarpowerportal.co.uk/energy-storage/desnz-over-22-000-domestic-batteries-installed-in-past-year

| Band | Median £/kWh, 2024/25 (DESNZ via SPP) | Median £/kWh, 2025/26 (MCS-derived, secondary) |
|---|---|---|
| 1–5.99 kWh | 1,020 | 1,300 |
| 6–10.99 kWh | 900 | 890 |
| 11–29.99 kWh | 590 | 630 |

The 2025/26 figures come from https://www.energy-review.co.uk/energy-data/home-batteries. That source filters out costs below £100 or above £5,000/kWh, publishes no quartiles, and its provenance is weaker.

The size-band gradient is the most usable spread here. Cost per kWh falls by roughly half from the smallest to the largest band. I have no values for 2016–2022. **Gap.**

## 5. Heat pump installed cost (air source)

**Boiler Upgrade Scheme statistics** (DESNZ; monthly, about four weeks after the month; HTML and xlsx; England and Wales; from May 2022). https://www.gov.uk/government/collections/boiler-upgrade-scheme-statistics
- The monthly tables cover applications and redemptions. Cost data has appeared in two ad hoc releases:
  - ASHP median cost by region, May–Nov 2022 (published 22 Dec 2022): https://www.gov.uk/government/statistics/ad-hoc-request-on-boiler-upgrade-scheme-air-source-heat-pumps-costs-by-region
  - Mode cost and capacity of ASHP redemptions, May 2022 to Jun 2023 (published 27 Jul 2023): https://www.gov.uk/government/statistics/ad-hoc-request-on-the-mode-cost-and-capacity-of-boiler-upgrade-scheme-redemptions-for-air-source-heat-pumps
  - I could not open the values in either release.
- Nesta's analysis of BUS data (30 Apr 2026) gives a real-terms ASHP median of £12,973 in 2024/25 and £13,041 in 2025/26 (+0.4%). That is −11% since the 2022 launch, so the launch-year median was about £14,650 real [derived: 13,041/0.89]. The 4–6 kW band rose 11% y/y. https://www.nesta.org.uk/blog/four-years-boiler-upgrade-scheme-four-charts/
- The current BUS grant is £7,500. Net cost to the household is therefore about £5,500 at the median [derived].
- Before 2022 (2016 and 2019) the scheme was the RHI, and it published no installed-cost series. **Gap.**

## 6. Home chargepoint

**EV charging device grant scheme statistics** (DfT/OZEV; quarterly; HTML with annex tables; official statistics in development). https://www.gov.uk/government/statistics/electric-vehicle-charging-device-grant-scheme-statistics-october-2024/electric-vehicle-charging-device-grant-scheme-statistics-october-2024
- EVHS (Sept 2014 to 31 Mar 2022): £140.8m funded 340,222 devices, about £414 per device [derived]. The current cap is £350. Earlier caps were higher: £500, and £700 before that [unverified].
- EVCG (from 1 Apr 2022, for renters, flat owners and landlords): up to £350 per socket. About £790 per socket [derived: £10.9m / 13,763].
- These are grant amounts, not installed costs. I found no official installed-cost series. **Gap.**

## 7. Insulation (loft and cavity)

| Date | Measure | Cost | Source |
|---|---|---|---|
| Apr 2016 | Loft insulation, 50→270mm, semi-detached, professional | ~£300 (saving ~£35/yr) | EST via DECC factsheet: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/587334/DECC_factsheet_11.11.16_LOFT_INSULATION_LOCKED.pdf |
| Page modified Apr 2025 | Loft, semi-detached | £1,300 | EST Green Heat toolkit: https://greenheattoolkit.energysavingtrust.org.uk/t/insulation-toolkit/why-do-homes-and-commercial-buildings-need-insulation/frequently-asked-questions/ |
| Same | Cavity wall, semi-detached | £1,925 | Same |
| Nov 2024 | Cavity wall, by house type | Paywalled | RICS BCIS via Which?: https://www.which.co.uk/reviews/insulation/article/cavity-wall-insulation/cavity-wall-insulation-costs-and-savings-aME221E0xDYR |

The 2016 and 2025 loft figures may not describe the same job. 2016 is a top-up, while 2025 is probably a full install. EST publishes single point estimates with no dispersion and no regular schedule. Values for 2019 and 2022 are a **gap**.

## 8. Grid carbon

**DESNZ GHG conversion factors** (annual each June; Excel full set plus flat file; OGL). The 2026 set was published 11 Jun 2026 and revised 31 Jul 2026. https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026

Table 9 of the 2026 methodology report: https://assets.publishing.service.gov.uk/media/6a2940543b15d05a7ce3202e/2026-GHG-conversion-factors-methodology-report.pdf

| Reporting year | Data year | Generated (kgCO2e/kWh) | Consumed incl. losses |
|---|---|---|---|
| 2016 | 2014 | 0.41205 | 0.44932 |
| 2017 | 2015 | 0.35156 | 0.38443 |
| 2018 | 2016 | 0.28307 | 0.30720 |
| 2019 | 2017 | 0.25560 | 0.27730 |
| 2020 | 2018 | 0.23314 | 0.25319 |
| 2021 | 2019 | 0.21233 | 0.23112 |
| 2022 | 2020 | 0.19338 | 0.21107 |
| 2023 | 2021 | 0.20707 | 0.22500 |
| 2024 | 2022 | 0.20705 | 0.22535 |
| 2025 | 2023 | 0.17700 | 0.19553 |
| 2026 | 2025 | 0.13096 | 0.14396 |

**Modelling trap:** the reporting year is not the data year. Until 2025 the lag was two years. The 2026 method cuts it to one year, so data year 2024 is skipped. Appendix 2 of the report gives a restated series. Poesys should index by data year.

**NESO Carbon Intensity API** (NESO with EDF Europe, Oxford and WWF; half-hourly; from 26 Sept 2017; 14 DNO regions plus England, Scotland and Wales; forecast 96+ hours ahead; CSV download plus API; CC BY 4.0). https://carbonintensity.org.uk/
- National 2025 average: 129 gCO2e/kWh. This is consistent with the DESNZ 0.13096 generation factor for data year 2025 [derived check].
- Regional annual means, 2024 → 2025 (Hoare Lea analysis of NESO data): https://hoarelea.com/2026/02/25/uk-grid-carbon-emissions-data/

| Region | 2024 (g/kWh) | 2025 (g/kWh) |
|---|---|---|
| North Scotland | 31 | 47 |
| London | 129 | 142 |
| South East | 140 | 161 |
| East Midlands | 208 | 197 |
| South West | 239 | 220 |
| South Wales | 259 | 252 |

- North Scotland had zero-carbon conditions for more than 60% of 2025.
- The half-hourly min/max range was not retrieved. Typical national half-hourly values of roughly 20–300+ g are [unverified]. Pull them from the API.

## 9. Projections to 2035

- **NESO FES 2025** (published 14 Jul 2025). Pathways: Holistic Transition, Electric Engagement, Hydrogen Evolution, and Falling Behind (the only one that misses net zero). https://www.neso.energy/bold-and-sustained-action-clean-energy-imperative-now-and-beyond-2030 and https://www.r-e-a.net/wp-content/uploads/2025/08/NESO-FES-2025-REA-Analysis-Final.pdf
  - 2035 ranges: consumer electricity demand 370–408 TWh, consumer gas 348–363 TWh, solar 56–62 GW. https://www.neso.energy/document/364556/download
  - About 4.8% of homes have storage by 2035.
  - Heat pump SCOP is 3.8→3.5 in Holistic Transition and 3.4→3.1 in the other pathways.
  - Cost assumptions are in the separate *FES 2025 Pathway Assumptions Log*, which I did not retrieve.
  - NESO's cost analysis (Dec 2025) puts energy spend at about 10% of GDP in 2025, falling to 5–6% by 2050. There is no household bill path. https://theenergyst.com/neso-publishes-cost-analysis-of-decarbonisation-pathways/
- **CCC Seventh Carbon Budget** (Feb 2025, via Which?, 14 Mar 2025). EV price parity with petrol and diesel between 2026 and 2028. EV saving about £550/yr and heat pump saving about £100–150/yr averaged over 2025–2050, with the heat pump saving conditional on policy costs moving off electricity. https://www.which.co.uk/news/article/what-the-latest-carbon-budget-means-for-you-and-your-finances-aB0aA7z1xdDC
- **DESNZ "Valuation of energy use and GHG emissions"** (Green Book supplementary). Data tables 1–19 include retail price projections by sector, with low, central and high scenarios [unverified that tables 4–8 are the retail ones]. The gov.uk page shows a last update of 30 Nov 2023. https://www.gov.uk/government/publications/valuation-of-energy-use-and-greenhouse-gas-emissions-for-appraisal
  - Values were not retrieved, because the xlsx was blocked. **Gap.**

## 10. Policy dates that move prices and costs

- **VAT on energy-saving materials:** 0% in GB from 1 Apr 2022 to 31 Mar 2027, then back to the reduced rate unless extended. https://legislation.gov.uk/uksi/2022/361/pdfs/uksiem_20220361_en.pdf
  - Batteries were added to the scheme from Feb 2024 [unverified].
- **VAT on domestic electricity:** 0% from 1 Oct 2026 to 31 Mar 2027, confirmed on Ofgem's rates page. Gas keeps 5% VAT.
- **Budget 2025 (26 Nov 2025)**, effective 1 Apr 2026:
  - Government funds 75% of the Renewables Obligation for 2026/27–2028/29.
  - ECO and GBIS bill funding ends, and the cap allowance goes to zero.
  - About £150 off a typical bill; EST says £154 (RO £88 plus ECO £59).
  - Sources: https://www.ofgem.gov.uk/sites/default/files/2026-01/Treatment%20of%20ECO%20and%20RO%20in%20the%20price%20cap%20from%20April%202026%20%281%29-20260126113009.pdf and https://energysavingtrust.org.uk/budget/
- **BUS grant:**
  - £5,000 ASHP and £6,000 GSHP from May 2022.
  - £7,500 for both from 23 Oct 2023. https://mcscertified.com/prime-minister-announces-boiler-upgrade-scheme-grant-increase-to-7500/
  - £9,000 for homes off oil or LPG, date not given. The budget rises to £625m in 2026/27 (Nesta).
- **EV VED from 1 Apr 2025:** first year £10, then £195/yr. The expensive car supplement applies above £40k (+£425/yr for five years). Petrol and diesel first-year bands doubled. https://www.autotrader.co.uk/content/news/road-tax-for-evs-among-big-ved-changes-coming-in-2025
- **eVED:** 3p/mile for battery EVs from 1 Apr 2028, with a reduced rate for PHEVs. The consultation closed 18 Mar 2026. https://www.vehicle-certification-agency.gov.uk/fuel-consumption-co2/fuel-consumption-guide/electric-vehicle-excise-duty-eved
- **Electric Car Grant:** announced Jul 2025. £3,750 or £1,500 per car, for cars under £37k, from a £650m budget, until 31 Mar 2030. https://www.which.co.uk/news/article/new-electric-car-grant-everything-you-need-to-know-aSoDt6B35O8D
- **Fuel duty:** cut by 5p to 52.95p in Mar 2022 (frozen since 2011).
  - Budget 2025 planned staged rises: +1p on 1 Sep 2026, +2p on 1 Dec 2026, +2p on 1 Mar 2027. https://fullfact.org/politics/fuel-duty-plans-2026/
  - On 20 May 2026 the government extended the 5p cut to 31 Dec 2026. A 3p rise is the default on 1 Jan 2027, to be confirmed at Budget 2026. https://petrolprices.co.uk/fuel-duty-september-rise-cancelled-2026.php
  - The weekly CSV still shows 52.95p on 12 Oct 2026, which is consistent.
- **EVHS:** closed 1 Apr 2022 and replaced by the EVCG (DfT statistics above).

---

## (a) Series register

| Quantity | Source | Frequency | Start | Granularity | Format |
|---|---|---|---|---|---|
| Petrol/diesel pump price, duty, VAT | DESNZ Weekly road fuel prices | Weekly | 2003 | UK average | csv/xlsx/xml |
| Retail elec/gas bills and unit costs | DESNZ QEP 2.2.x/2.3.x | Quarterly/annual | pre-2016 | Region × payment method | xlsx/pdf |
| Cap unit rate and standing charge | Ofgem price cap | Quarterly (6-monthly to 2023) | Jan 2019 | 14 regions × payment × single/multi-rate | html (+xlsx models) |
| PV £/kW | DESNZ Solar PV cost data (MCS) | Annual (May); monthly within year | 2013/14 | Size band; DNC/TIC | xlsx/ods |
| Battery £/kWh | DESNZ/MCS (via SPP) | Annual | 2024/25 confirmed | Size band | unknown |
| ASHP installed cost | DESNZ BUS statistics, ad hoc | Monthly (counts); ad hoc (cost) | May 2022 | Region, capacity | xlsx/ods |
| Chargepoint grant | DfT EV charging grant statistics | Quarterly | 2014 | Scheme, region | html |
| Insulation cost | EST | Irregular | ≤2016 | House type | html |
| Grid factor | DESNZ GHG conversion factors | Annual (June) | ≤2016 | UK | xlsx |
| Half-hourly intensity | NESO Carbon Intensity API | 30-min | 26 Sep 2017 | 14 DNO regions + nations | API/csv |
| Pathways | NESO FES | Annual (July) | — | Pathway | xlsx workbook |
| Appraisal retail prices | DESNZ Valuation of energy use tables | Periodic (last Nov 2023) | — | Sector × low/central/high | xlsx |

## (b) Representative values

| Item | ~2016 | ~2019 | ~2022 | ~2025 |
|---|---|---|---|---|
| Petrol p/l | gap | 120.27 (Jan) | 191.55 (Jul) | 136.6 (Jan) |
| Diesel p/l | gap | 130.33 | 199.22 | 143.3 |
| Elec unit / SC | 14.71p all-in DD (2015) | gap (£1,137 dual-fuel bill) | 28p/45p, then 34p/46p (EPG) | 26.35p / 53.68p (Q4) |
| Gas unit / SC | 4.54p all-in DD (2015) | gap | 7p/27p, then 10.3p/28p | 6.29p / 34.03p |
| PV 0–4 kW £/kW | gap | gap | gap | 1,876 (2024/25) |
| Battery £/kWh | gap | gap | gap | 590–1,020 by band (2024/25) |
| ASHP median | gap | gap | ~£14,650 real [derived] | £12,973 (24/25), £13,041 (25/26) |
| Chargepoint | grant ≤£500 [unverified] | — | £350 grant | install cost gap |
| Loft / cavity | £300 / gap | gap | gap | £1,300 / £1,925 |
| Grid factor (reporting yr) | 0.41205 | 0.25560 | 0.19338 | 0.17700 (2026: 0.13096) |
| Annual intensity, regional | — | — | — | 47 (N Scot) to 252 (S Wales) g/kWh |

## (c) Policy date register

| Date | Change |
|---|---|
| 1 Jan 2019 | Ofgem default tariff cap starts |
| 23 Mar 2022 (effective 28 Mar on CSV) | Fuel duty −5p to 52.95p |
| 1 Apr 2022 | 0% VAT on energy-saving materials (to 31 Mar 2027); EVHS replaced by EVCG |
| May 2022 | BUS opens: £5k ASHP, £6k GSHP |
| 1 Oct 2022 | Energy Price Guarantee: 34p elec, 10.3p gas |
| 23 Oct 2023 | BUS rises to £7,500 |
| 1 Apr 2025 | EVs pay VED; ICE first-year rates doubled |
| Jul 2025 | Electric Car Grant (to 31 Mar 2030) |
| 1 Apr 2026 | ECO off bills; 75% of RO taxpayer-funded (2026/27–28/29) |
| 1 Oct 2026 – 31 Mar 2027 | 0% VAT on domestic electricity |
| 31 Dec 2026 / 1 Jan 2027 | 5p fuel duty cut ends; 3p default rise (subject to Budget 2026) |
| 1 Apr 2027 | Fuel duty RPI uprating resumes (planned); ESM VAT relief ends unless extended |
| 1 Apr 2028 | eVED at 3p/mile for battery EVs |

## (d) Named gaps

1. **PV £/kW and quartiles for 2016/17–2023/24:** need the DNC xlsx (`Solar_Costs_2025-26__DNC_.xlsx`, linked from data.gov.uk), which was blocked. There is no confirmed source for PV quartiles.
2. **BUS cost distribution (quartiles, region):** need the two ad hoc xlsx files above, which were blocked. There is no installed-cost series before 2022.
3. **Ofgem 2019–2021 unit rates and standing charges:** Ofgem published bill levels only. Unit rates have to be derived from the cap models or from QEP tables 2.2.4/2.3.4 for 2019.
4. **2016 pump price:** the 2003–2017 CSV was not read.
5. **Battery cost before 2024/25:** there is also no confirmed gov.uk dataset URL.
6. **Installed chargepoint cost:** only grant amounts per device exist.
7. **Insulation cost for 2019 and 2022, with dispersion:** EST gives point estimates only.
8. **Half-hourly intensity min/max:** pull from the Carbon Intensity API.
9. **Not reached before the search limit:** ONS CPI/RPI (deflators), Auto Trader and ONS used/new car price indices, DESNZ fossil fuel price assumptions, and the Green Book retail price tables.
10. **Projections:** the FES Pathway Assumptions Log (technology capex) and the CCC 7CB technology cost dataset were not retrieved. There is no published household-bill path to 2035 from NESO.

## Done

Published on 25 Oct as the Knowledge page `site/knowledge/dated-household-cost-and-price-series/`, with the note `docs/market_research/dated_household_cost_and_price_series_2026-10-25.md`. The note carries the verification pass that the 25 Oct verify steer asks for: each [unverified] item is marked confirmed, corrected or still open, and no open item is stated on the page as a claim. Counts as recorded: Counts: 15 confirmed, 2 corrected, 4 still open.
