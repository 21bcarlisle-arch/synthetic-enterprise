# What things cost a GB household, by date: fuel, energy, kit and carbon, 2016-2025, with projections to 2035

**Knowledge:** dated-household-cost-and-price-series

Written 2026-10-25 from the advisor's cited evidence pack
`docs/staging/advisor/done/DIRECTOR_EVIDENCE_DATED_COST_AND_PRICE_SERIES_2016_2035_2026-10-25.md`, one of
six packs behind the personalised asset world (the director, 25 Oct 06:03: "I'm worried you are
using static costs and %"). It is a register of dated series: where each price or cost a household
faces is published, how often, from when, at what granularity, and a few representative values.
**[derived]** marks arithmetic on cited figures; **[unverified]** items are not claims. Each pack
item was re-checked on 2026-10-25 where its source could be fetched (§11).

Neighbouring pages own the mechanisms: `price-cap` (how the cap is built), `non-commodity-costs`
(policy costs in the bill), `household-carbon-and-the-measures-that-save-it` (carbon accounting for a
home), `ev-solar-and-batteries-as-products` (the products). This page owns the DATES: which value
applied when, so that nothing reads a constant where a series exists.

## 0. What the world and the company do today (read from code, not run)

- **No road-fuel price exists anywhere in the code.** No module in `sim/`, `simulation/`, `company/`
  or `saas/` holds a petrol or diesel price, so no EV saving against a petrol or diesel car can be
  computed, dated or otherwise.
- **The retrofit offer book is four undated constants.** `company/pricing/fabric_intervention.py:324-328`
  (`OFFER_BOOK`): insulate £6,000, heat pump £12,000, solar PV £7,000, time-shift £300, the same in
  2016 and 2025. Its own docstring (line 63) calls them "order-of-magnitude UK retrofit capex". Dated
  series now exist for the heat pump (Boiler Upgrade Scheme medians from 2022, net of a grant that
  rose from £5,000 to £7,500 on 23 Oct 2023) and for PV (£/kW by size band from 2013/14); see §3, §5.
- **The cap has two homes, one dated and one not.** `company/pricing/ofgem_price_cap.py:66-90` holds
  an annual table with approximate comments (2019 "Q4 2019 only", though the cap began on 1 Jan 2019)
  and a **fallback of £190/MWh electricity and £52/MWh gas for every year after 2025**. The dated
  windows from the commons (`docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`,
  25 windows to Dec 2026) say 2026 ran at £247-277/MWh electricity and £57-80/MWh gas. Three
  callers read the annual table: `company/pricing/switching_recommendation.py:15-20`,
  `company/crm/market_conditions.py:186-190`, `company/compliance/domain_invariants.py:54-62`.
- **Economy 7 rates are an unsourced annual table nobody calls.** `company/billing/economy7.py:18-25`
  (day 12-34p, night 6.5-19p, 2016-2025, no source); only tests import it.
- **Grid carbon is read by REPORTING year, deliberately.** `company/regulatory/carbon_emissions.py:181-190`
  says a year Y factor set "reflects grid data about two years older; the household's year Y uses the
  year Y set, as a reporting company would". That is a stated choice, not a slip. The level itself
  comes from NESO's measured intensity by year. The pack's trap (§8) bites only where a DESNZ
  factor is read as if it described its own year.
- **Gas is converted at a fixed exchange rate.** `sim/gas_prices_history.py:38` (`GBPUSD = 1.28`).

## 1. Road fuel

Weekly road fuel prices (DESNZ, accredited official statistics; weekly from 9 Jun 2003; UK average
only, no regions and no forecourt spread; CSV 2003-2017 and 2018 on, OGL).

| Week | Petrol p/l | Diesel p/l | Duty p/l |
|---|---|---|---|
| 2016, mean of 52 weeks | 108.9 (101.4-116.6) | 110.4 (100.8-119.0) | 57.95 |
| 02/07/2018 | 126.54 | 130.83 | 57.95 |
| 07/01/2019 | 120.27 | 130.33 | 57.95 |
| 04/07/2022 (weekly peak) | 191.55 | 199.22 | 52.95 |
| 06/01/2025 | 136.6 | 143.3 | 52.95 |
| 12/10/2026 | 175.28 | 200.04 | 52.95 |

VAT 20% throughout. QEP Sept 2026: mid-Sept petrol 168.8p (+26.1% y/y), diesel 191.3p (+35.1%);
QEP's monthly-average petrol peak is 188.8p (July 2022), below the weekly 191.55 because it averages.

## 2. Retail electricity and gas

- Ofgem cap, quarterly since Oct 2023, six-monthly before; started 1 Jan 2019; 14 regions × payment
  method × single or multi-rate.
- Direct debit, GB average, incl. VAT: Jul-Sep 2026 electricity 26.11p and 57.19p/day, gas 7.33p and
  29.04p/day; **Oct-Dec 2026 electricity 26.32p and 54.83p/day at 0% VAT, gas 7.97p and 29.68p/day**;
  typical bill £1,723, about £45 lower than it would have been at 5% VAT (Ofgem, confirmed).
- Earlier points (pack, secondary sources): Jul-Sep 2025 25.73p / 51.37p, 6.33p / 29.82p; Oct-Dec 2025
  26.35p / 53.68p, 6.29p / 34.03p; Jan-Mar 2026 27.69p / 54.75p, 5.93p / 35.09p. EPG from 1 Oct 2022:
  34p / 46p, 10.3p / 28p. 2015 (QEP): electricity 14.71p all-in DD (regions 14.17-16.13p), gas 4.54p
  (4.41-4.68p).
- Regional and method spread, Jan-Mar 2025 electricity DD: standing charge London 41.57p to Northern
  72.09p a day; unit rate Northern 23.51p to London 26.06p; standard credit higher on both;
  prepayment unit rates lower.
- QEP from 2026 computes bills at 3,400 kWh electricity and 11,200 kWh gas; neither is the TDCV.

## 3. Solar PV installed cost

DESNZ Solar PV cost data (MCS; annual each May since 2014; £/kW by month and size band 0-4, 4-10,
10-50 kW; two bases, DNC from 2013/14 and TIC from 2023/24, TIC 6-12% lower). 2024/25 medians:
0-4 kW £1,876/kW (−19% y/y), 4-10 kW £1,780/kW, 10-50 kW £1,256/kW (pv-magazine). Earlier medians and
all quartiles: gap (the xlsx was not opened).

## 4. Battery storage installed cost

2024/25 (DESNZ/MCS via Solar Power Portal, 22,398 systems): median £1,020/kWh at 1-5.99 kWh, £900 at
6-10.99 kWh, £590 at 11-29.99 kWh. Cost per kWh roughly halves from the smallest band to the largest.
Batteries joined the energy-saving-materials zero VAT rate on **1 Feb 2024** (HMRC Notice 708/6,
confirmed). Before 2024/25: gap.

## 5. Heat pump installed cost

Boiler Upgrade Scheme (England and Wales, from May 2022). Real-terms ASHP median **£12,973 (2024/25)
and £13,041 (2025/26)**, down 11% since launch (Nesta, 30 Apr 2026, confirmed); launch-year median
≈£14,650 [derived]. Grant £5,000 ASHP / £6,000 GSHP from May 2022, **£7,500** from 23 Oct 2023;
median net ≈£5,500 [derived]. RHI years before 2022: no installed-cost series. The two ad hoc BUS
cost releases (regional medians; mode and capacity) were not opened.

## 6. Home chargepoint

Grant amounts, not installed costs: EVHS to 31 Mar 2022, up to £350 a device at the end (DfT,
confirmed); £140.8m for 340,222 devices ≈£414 a device [derived]. EVCG from 1 Apr 2022 for renters,
flat owners and landlords, up to £350 a socket (DfT, confirmed). Earlier EVHS caps of £500 and £700
stay **[unverified]**. No installed-cost series exists.

## 7. Insulation

EST point estimates only: loft top-up (50→270 mm, semi) about £300 in Apr 2016; loft £1,300 and
cavity £1,925 for a semi on a page modified Apr 2025. The two loft figures are probably different
jobs (top-up against full install). No dispersion, no schedule; 2019 and 2022 are gaps.

## 8. Grid carbon

**DESNZ conversion factors, Table 9 (as published, confirmed)**, kgCO2e/kWh generated, by data year:
2014 0.41205, 2015 0.35156, 2016 0.28307, 2017 0.25560, 2018 0.23314, 2019 0.21233, 2020 0.19338,
2021 0.20707, 2022 0.20705, 2023 0.17700, 2025 0.13096. The reporting year ran two years after the
data year until the 2025 set; the 2026 set uses data year 2025, so data year 2024 was skipped in the
published sets.

**Correction the pack did not carry:** the 2026 methodology paper also publishes **Table 1.6, a
fully consistent series by data year** recomputed on today's sources, and it differs from the
as-published values: data year 2016 0.29684 (published 0.28307), 2020 0.18803 (0.19338), 2022 0.18666
(0.20705), 2023 0.16155 (0.17700), **2024 0.13707 (never published as a set)**, 2025 0.13096. Indexing
by data year should use Table 1.6, not the published sets.

**NESO half-hourly intensity** (from 26 Sep 2017; national and 14 DNO regions; CC BY 4.0). Pulled
from the API for 2025 (17,520 half-hours): mean **129.2 g/kWh**, minimum **24**, maximum **293**,
5th percentile 51, 95th 231. Regional annual means 2024 → 2025 (Hoare Lea, confirmed): North
Scotland 31 → 47, London 129 → 142, South East 140 → 161, East Midlands 208 → 197, South West
239 → 220, South Wales 259 → 252; North Scotland zero-carbon for more than 60% of 2025.

## 9. Projections to 2035

NESO FES 2025 (four pathways): about 4.7-4.8% of homes with electricity storage by 2035 (REA's
analysis, confirmed as secondary); heat pump SCOP 3.8 → 3.5 (Holistic Transition) or 3.4 → 3.1;
2035 demand ranges (electricity 370-408 TWh, gas 348-363 TWh, solar 56-62 GW) not re-checked. The
Pathway Assumptions Log (technology costs) was not opened. CCC Seventh Carbon Budget via Which?: EV
price parity 2026-2028, EV saving ≈£550 a year, heat pump £100-150 a year averaged 2025-2050. DESNZ
"Valuation of energy use and GHG emissions" data tables 1-19 (last updated 30 Nov 2023, confirmed)
hold sector retail price projections; which tables are retail stays [unverified]. No NESO household
bill path exists.

## 10. Policy dates

| Date | Change | Status |
|---|---|---|
| 1 Jan 2019 | Default tariff cap starts | confirmed (Ofgem letter, pack) |
| 23 Mar 2022 (28 Mar on the CSV) | Fuel duty −5p to 52.95p | confirmed (weekly CSV) |
| 1 Apr 2022 | 0% VAT on energy-saving materials, to 31 Mar 2027; EVHS replaced by EVCG | confirmed (HMRC 708/6; DfT) |
| 1 Feb 2024 | Batteries, water-source heat pumps and smart diverters join the zero rate | confirmed (HMRC 708/6) |
| May 2022 | BUS opens: £5k ASHP, £6k GSHP | pack |
| 1 Oct 2022 | Energy Price Guarantee | pack |
| 23 Oct 2023 | BUS rises to £7,500 | pack |
| 1 Apr 2025 | EVs pay VED; ICE first-year rates doubled | pack |
| Jul 2025 | Electric Car Grant, to 31 Mar 2030 | pack |
| 1 Apr 2026 | ECO/GBIS cap allowance to zero; RO allowance cut by 75% (government-funded) | confirmed (Ofgem, Jan 2026) |
| 1 Oct 2026 - 31 Mar 2027 | 0% VAT on GB domestic electricity; gas stays 5% | confirmed (HMRC Brief 10 (2026); Ofgem rates page) |
| 31 Dec 2026 / 1 Jan 2027 | 5p fuel duty cut ends; 3p default rise subject to Budget 2026 | pack |
| 1 Apr 2027 | ESM relief reverts to 5% unless extended | confirmed (HMRC 708/6) |
| 1 Apr 2028 | eVED 3p/mile for battery EVs | pack |

## 11. Verification (2026-10-25)

| Item | Outcome | Source, accessed 2026-10-25 |
|---|---|---|
| 2016 petrol ≈110p [unverified] | **confirmed**: mid-2016 110.4-111.4p; 2016 mean 108.9p | DESNZ weekly road fuel prices, 2003-2017 CSV |
| Weekly rows 2018-2026 (7 rows, incl. duty and VAT) | **confirmed** | DESNZ weekly CSV, 2018 on |
| QEP Sept 2026: 168.8p, 191.3p, +26.1%, +35.1% | **confirmed** | QEP Sept 2026 pdf |
| Ofgem Oct-Dec 2026 rates and £1,723 | **confirmed** | Ofgem cap rates page (plain fetch returned the tables) |
| DESNZ Table 9 grid factors | **confirmed** | 2026 GHG methodology paper, Table 9 |
| Indexing by data year | **corrected/extended**: use Table 1.6's consistent series (e.g. data year 2023 0.16155, not 0.17700; 2024 0.13707 exists) | same paper, Table 1.6 |
| NESO 2025 national mean 129 | **confirmed**: 129.2 over 17,520 half-hours | carbonintensity.org.uk API |
| Half-hourly range "20-300+" [unverified] | **corrected**: 24 to 293 in 2025 | same API |
| Regional means 2024 → 2025 | **confirmed** | Hoare Lea, Feb 2026 |
| BUS medians £12,973 / £13,041, −11% since launch | **confirmed** | Nesta, Apr 2026 |
| Batteries in ESM relief from Feb 2024 [unverified] | **confirmed**: 1 Feb 2024 | HMRC VAT Notice 708/6 |
| ESM zero rate to 31 Mar 2027, then 5% | **confirmed** | HMRC VAT Notice 708/6 |
| EVHS/EVCG £350 caps | **confirmed** | DfT EV charging grant statistics, Oct 2024 |
| ECO allowance to zero and RO −75% from 1 Apr 2026 | **confirmed** | Ofgem, Jan 2026 |
| FES: 4.7-4.8% of homes with storage by 2035 | **confirmed** (secondary) | REA analysis of FES 2025 |
| Earlier EVHS caps £500/£700 [unverified] | **still open** | — |
| Valuation tables 4-8 are retail [unverified] | **still open**: page and table list confirmed, contents not opened | gov.uk, last updated 30 Nov 2023 |
| Ofgem cap models reachable as xlsx [unverified] | **still open** | — |
| FES 2035 demand and solar ranges | **still open** | — |

**Counts: 15 confirmed, 2 corrected, 4 still open.**

## 12. Named gaps

1. PV £/kW medians and quartiles 2016/17-2023/24 (DNC xlsx).
2. BUS cost distribution: quartiles, regions, capacity (two ad hoc xlsx).
3. Ofgem 2019-2021 unit rates and standing charges by region (cap models or QEP 2.2.4/2.3.4).
4. Battery cost before 2024/25, and a confirmed gov.uk dataset page.
5. Installed chargepoint cost: only grant amounts exist.
6. Insulation cost for 2019 and 2022, with dispersion.
7. ONS CPI/RPI deflators; new and used car price indices.
8. DESNZ fossil fuel price assumptions and Green Book retail price tables (values).
9. FES 2025 Pathway Assumptions Log (technology capex); CCC 7CB cost dataset.
10. A daily dollar-sterling series for the gas conversion (Bank of England).
