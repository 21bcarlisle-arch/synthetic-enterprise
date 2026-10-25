# Who drives how far, and where they park (GB/England, 2002-2025)

**Knowledge:** who-drives-how-far-and-where-they-park

*Written 25 Oct 2026 from the advisor's cited evidence pack
(`docs/staging/advisor/done/DIRECTOR_EVIDENCE_DRIVERS_MILEAGE_AND_PARKING_DISTRIBUTIONS_2026-10-25.md`),
with the DfT tables the advisor's sandbox could not reach fetched and read here. [derived] = our
arithmetic on the cited figures. NTS covers England only; MOT and traffic figures cover GB; the
Census covers England and Wales.*

**NTS 2025 caveat.** The 2025 survey moved to a digital diary that under-records some car-driver
trips (commuting unaffected). Use 2024 trip rates for calibration; 2025 interview items (car
ownership, fuel mix, mileage per car) stand.
https://www.gov.uk/government/statistics/national-travel-survey-2025/nts-2025-introduction-and-main-findings

## 1. Mileage per car

**NTS0901a, England household cars, mean miles a year** (fetched 25 Oct 2026, last updated
10 Sep 2026; https://www.gov.uk/government/statistical-data-sets/nts09-vehicle-mileage-and-occupancy,
file nts0901.ods sha256 64cf068e...e6682):

| Year | Petrol | Diesel | Hybrid | BEV | All cars |
|---|---|---|---|---|---|
| 2016 | 6,500 | 10,200 | – | – | 7,900 |
| 2019 | 6,400 | 9,500 | – | – | 7,600 |
| 2020 | 5,900 | 8,500 | – | – | 6,900 |
| 2021 | 4,700 | 6,600 | – | – | 5,400 |
| 2022 | 6,000 | 8,000 | – | – | 6,800 |
| 2023 | 6,100 | 8,300 | 8,300 | – | 7,000 |
| 2024 | 6,200 | 8,300 | 8,000 | 8,900 | 7,100 |
| 2025 | 6,200 | 8,000 | 8,100 | 9,400 | 7,100 |

PHEV is suppressed ([u]) in every year. **NTS0901b, by purpose, 2025:** business 500, commuting
2,200, other private 4,500. **NTS0901c:** company cars 3.7% of household cars in 2025 (2.7-3.7%
since 2018; 6.3% in 2002).

**NTS0904, mileage bands, England household cars, 2025** (nts0904.ods sha256 4636b948...2de9):
under 5,000 miles 31.3%; 5,000-11,999 55.9%; 12,000 and over 12.8% [derived by summing the 14
published bands]. 2024: 31.9 / 55.4 / 12.7. The pack's MOT-based 34/52/14 (GB private cars, 2011,
RAC Foundation *MOToring Along* https://uwe-repository.worktribe.com/OutputFile/878388) is
consistent in shape.

**MOT quartiles, GB, tests Dec 2024-Dec 2025** (commercial analysis of DVSA anonymised MOT data,
not official statistics; https://www.motcheckup.co.uk/research/real-uk-car-mileage-2026): petrol
P25 2,708, median 4,931, P75 7,849; diesel 4,113 / 6,879 / 10,449. Lognormal fits [derived]:
petrol mu 8.503, sigma 0.79; diesel mu 8.836, sigma 0.69. The MOT median sits below the NTS mean
because a lognormal's mean exceeds its median and the MOT population includes every GB car.

**By age** (MOToring Along, 2011 private cars): 0-3 years 8,711 mi (index 1.00) falling to 13+
years 4,448 (0.51); full table in the pack.

**By fuel, new cars under three years** (RAC Foundation, Jul 2025, from >1.2m MOT tests): 2024
petrol 7,585, diesel 10,728, PHEV 9,367, BEV 10,054, all 8,460. BEVs 3.8% of the fleet, 5.3% of
car miles. https://racfoundation.org/media-centre/at-least-one-in-twenty-car-miles-driven-is-now-zero-emission
(our fetch was refused, 403; the figures stand on the pack's reading and are consistent with
NTS0901's BEV 8,900-9,400).

**Selection, not causation.** High-mileage drivers choose diesel or BEV; the fuel does not cause
the miles (motcheckup, above; Wadud et al. 2022, TRD 109, https://eprints.whiterose.ac.uk/190402,
on the predictors of excess driving: sex, employment, income, company car, location, density,
multiple cars, business travel).

**Company vs private** (NTS 2010 ch.9): 19,190 vs 7,910 miles, about 2.4x [derived].
https://assets.publishing.service.gov.uk/media/5a798e7fed915d04220695c1/nts2010-09.pdf.
HMRC benefit-in-kind company cars: 920k in 2024-25, 51% zero-emission.
https://www.gov.uk/government/statistics/benefits-in-kind-statistics-july-2026/benefit-in-kind-statistics-commentary-july-2026

## 2. Households and drivers

Cars per household, England: 0 / 1 / 2+ = 22 / 44 / 34% (2024), 25 / 42 / 33% (2025). Lowest
income quintile 40% no car, highest 14%; two or more cars 15% vs 46% (NTS 2024).
https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips.
No-car households by area (2017/18): London 45%, most rural 7%.
Licence holding 17+: men 80%, women 71% (NTS Factsheet 2024).
Car miles per person 2024: women 4,314, men 4,940; peak 50-59.
Census 2021 (England and Wales): 31.2% mainly worked from home; 45.1% drove to work.
https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/bulletins/traveltoworkenglandandwales/census2021

## 3. When

**TRA0305, GB cars and taxis, all roads, monthly index, 5-year average 2021-2025** (fetched 25 Oct
2026, sha256 a3556849...accea; https://www.gov.uk/government/statistical-data-sets/road-traffic-estimates-tra):
Jan 85.4, Feb 92.4, Mar 97.0, Apr 100.4, May 103.7, Jun 105.9, Jul 104.9, Aug 104.7, Sep 104.9,
Oct 103.2, Nov 101.4, Dec 95.6.

**TRA0306, GB cars and taxis, all roads, day-of-week index, 2025** (sha256 46ccdddf...52ae):
Mon 99.4, Tue 101.9, Wed 102.1, Thu 104.1, Fri 109.1, Sat 96.6, Sun 86.7.

## 4. Parking and home charging

**NTS0908, where household vehicles are parked overnight, England 2024** (sha256 49f60443...a1fe):
garage 8.8%, private property not garaged 63.6%, street 24.6%, other 2.9%; so about 72% off-street
[derived], per vehicle not per home. By area: urban nearer a major town 8.2 / 60.2 / 28.6%
street; smaller rural nearer a town 14.4 / 75.0 / 7.8% street. 2002: garage 22.5%, street 24.1%.

**DfT EV driver behaviours and attitudes tracker** (Ipsos for DfT;
https://www.gov.uk/government/publications/electric-vehicle-ev-driver-behaviours-and-attitudes-tracker):
- Year 2 (published 30 Jul 2026, dft-ev-tracker-year-2.pdf): BEV drivers with off-street parking
  87% (PHEV 80%); 86% of those park on a driveway or garage beside the home; 89% can charge at home;
  72% have a dedicated charger; about 11% rely on public charging; 57% of home chargers on an EV
  tariff; 44% acquired through salary sacrifice; half make a 100-mile-plus trip needing a charge
  about once a month or less.
- Year 1 (published 25 Sep 2025): 90% / 88% off-street; 91% BEV home charging; 9% public-only;
  76% dedicated charger; 49% on an EV tariff; home access 97% Midlands, 98% rural, 86% South,
  89% urban.

**All homes, not EV owners:** 65.1% of UK homes have off-street parking (68% outside London),
from 7% in Westminster to 84% in Flintshire, attributed to the RAC Foundation (2020), read through
Forecourt Trader, 29 Sep 2025
(https://forecourttrader.co.uk/news/government-study-finds-90-of-ev-drivers-can-charge-at-home/709930.article).
The Foundation's own site refused our fetch (403). **Secondary only.**

## 5. Distributions for the world to draw from (inputs to the asset design note)

| Attribute | Draw | Conditioned on | Source |
|---|---|---|---|
| Driver's annual mileage | Lognormal on the MOT quartiles, scaled to the NTS0901 year mean | Person: age, sex, work, income, area, company car, cars in household | NTS0901/0904; MOT; Wadud 2022 |
| Age of car | Multiplier 1.00 (0-3 yrs) to 0.51 (13+) | Vehicle age | MOToring Along |
| Company car | ~3.7% of household cars; ~2.4x miles | Employment, income | NTS0901c; NTS 2010 |
| Month and weekday | TRA0305 / TRA0306 indices above | Date | DfT |
| Off-street parking | Draw per home | Dwelling type, tenure, area (NTS0908 by area) | NTS0908; RAC (secondary) |
| Fuel given mileage | Draw the car after the mileage | Mileage, income, parking | see the vehicle page |

Design choices to be named, not published: year-to-year persistence (a person factor times a
yearly shock, plus a regime change on a move, job change or retirement); long-trip frequency.

## 6. Population checks (calibration, never per-home targets)

1. Household car mean 7,100 mi (2024-25); 7,900 (2016); 5,400 (2021).
2. Bands 31 / 56 / 13% (<5k / 5-12k / >=12k), 2025.
3. Cars per household 22 / 44 / 34% (2024).
4. ~72% of vehicles off-street overnight (2024); street share ~29% urban, ~8% small rural.
5. ~87-91% of BEV drivers able to charge at home; ~9-11% public-only.
6. Monthly traffic index 85 (Jan) to 106 (Jun).

## 7. Named gaps

1. Year-to-year mileage persistence per driver: unpublished (Wilson et al. 2012 assume a Gamma
   usage factor; no measured value).
2. Homes (not vehicles) with off-street parking by dwelling type and tenure: no English Housing
   Survey table found; RAC Foundation 2020 figures read only through a secondary report.
3. Driver miles by age x sex x employment x income: NTS0605/9902 family not read.
4. Long trips (>100 mi) per driver per year: only "half of BEV drivers about monthly or less".
5. Hybrid working shares after 2021.
6. Company-car mileage after 2010.

## Verification pass, 25 Oct 2026

### Verification of the drivers, mileage and parking pack (25 Oct 2026)

Per DIRECTOR_STEER_VERIFY_THE_PACKS_UNVERIFIED_ITEMS_AS_YOU_DRAFT. Items marked [unverified] in the
pack, and the tables it named as not retrieved. Accessed 2026-10-25 unless stated.

| # | Item in the pack | Outcome | Source / note |
|---|---|---|---|
| 1 | NTS0904 mileage bands not retrieved | **confirmed (fetched)** | nts0904.ods: 2025 <5k 31.3%, 5-12k 55.9%, >=12k 12.8%. Shape agrees with the MOT 34/52/14 |
| 2 | NTS0901 company/private/fuel/purpose not retrieved | **confirmed (fetched)** | nts0901.ods: all cars 7,100 (2025); BEV 9,400; company 3.7%; business/commute/other 500/2,200/4,500 |
| 3 | "about 7,000 miles per car" (EV pack, same claim) | **confirmed** | NTS0901a 2024 and 2025: 7,100 |
| 4 | TRA0305 seasonal profile "about +/-8-10%, Jan/Dec trough, summer peak" | **corrected** | Old: +/-8-10% symmetric. New: Jan 85.4 to Jun 105.9 (2021-25 avg) -- trough -15%, peak +6%. TRA0305 |
| 5 | TRA0306 day-of-week values | **confirmed (fetched)** | 2025: Mon 99.4 ... Fri 109.1, Sat 96.6, Sun 86.7 |
| 6 | NTS0908 overnight parking by area | **confirmed (fetched)** | 2024: garage 8.8, private 63.6, street 24.6, other 2.9; street 28.6% urban-near to 7.8% small rural |
| 7 | 64% private property + 9% garage (2024) | **confirmed** | NTS0908 (8.8% rounds to 9) |
| 8 | About 90% of BEV drivers have off-street parking | **corrected (updated)** | Year 1: 90% (confirmed). Year 2 (30 Jul 2026): 87%. DfT EV tracker |
| 9 | About 9% of BEV drivers public-only | **corrected (updated)** | Year 1: 9% (confirmed). Year 2: about 11%. DfT EV tracker |
| 10 | 65% of homes off-street; Westminster 7%, Flintshire 84% | **still open at primary** | Confirmed only via Forecourt Trader (29 Sep 2025) citing RAC Foundation 2020 (65.1%; 68% outside London). RAC Foundation site returned 403 |
| 11 | Zapmap: about 9m households without off-street parking | **still open** | Not fetched; secondary in the EV pack |
| 12 | EHS parking by dwelling type and tenure | **still unpublished (as found)** | gov.uk search and DfT's Oct 2026 tenants consultation cite EHS qualitatively only; no table found |
| 13 | Direction: detached/semi high, flats/terraces low; owners above renters | **still open** | Qualitative support only (DfT consultation, 20 Oct 2026: "access ... greatest amongst owner-occupied households") |
| 14 | Hybrid working roughly a quarter to a third | **still open** | ONS OPN not fetched |
| 15 | Long trips about 6-12 per driver per year | **still open** | Nearest: EV tracker Y2, half of BEV drivers make a 100-mi+ trip needing a charge about monthly or less |
| 16 | NTS driver miles by age/sex/employment/income (NTS0605/9902/9904) | **still open** | Not fetched |
| 17 | Year-to-year mileage persistence | **still unpublished (finding)** | No source; design choice |
| 18 | Census TS045 0/1/2/3+ car counts | **still open** | Not fetched |

**Counts: confirmed 6 (1, 2, 3, 5, 6, 7), corrected 3 (4, 8, 9), still open 9 (10, 11, 12, 13, 14, 15, 16, 17, 18), of which 2 are findings that nothing is published (12, 17).**

Tally for the index: confirmed 6 · corrected 3 · open 9 (incl. 2 unpublished).

Files fetched (kept outside the repo; hashes so the integrator can re-fetch and compare):
nts0901.ods 64cf068efd9c47096249c360f9682c227bef37941adbae331ddb1236ea2e6682;
nts0904.ods 4636b948571cd5db7ca94cc8213fb7b59e3dfb65ccf30f17805221a95c622de9;
nts0908.ods 49f6044306df47428c8fd3a93053e8f01dae23425d6eb8c045d9ebc773a1a1fe;
tra0305 a3556849e98533fbdfb908ccf0a077431a093787aabca221023ccc5db7daccea;
tra0306 46ccdddf8939e8adc8d09ef3e150ddfe6714ad94367d8b7afdb311f8c9ed52ae.
