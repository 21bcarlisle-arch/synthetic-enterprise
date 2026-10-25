# Director evidence: drivers mileage and parking distributions

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

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

I've written the evidence pack below. Some of the core tables could not be pulled, so a few things are still open:

- **No NTS mileage-band shares (NTS0904):** the session couldn't reach the data tables (the downloads were refused and bash had no route out), so the band distribution comes from MOT-based analyses, not NTS0904.
- **No other ODS tables either:** NTS0901, the TRA0305/0306 monthly and day-of-week indices, the VEH company-keeper counts and Census TS045 all failed the same way. Their exact values are listed as gaps.
- **Parking was added mid-task, after the search allowance was used up:** only NTS overnight-parking shares are confirmed. The 65%, Westminster/Flintshire, Zapmap and EV-tracker figures were never checked. They are in the pack marked [unverified].

A follow-up turn with fresh searches, or the ODS files themselves, would close most of these. Areas covered: England (NTS), England and Wales (Census) and GB (MOT, traffic).

---

# Poesys Evidence Pack: Who drives how far in GB, and how

**Purpose:** give Poesys distributions it can sample for each driver, plus checks for the simulated population, so that each home's EV demand comes from its occupants rather than a percentage uplift.
**Conventions:** [derived] = my arithmetic on the cited figures. [unverified] = from memory or the coordinator's brief, not confirmed by a fetched source. NTS = National Travel Survey, which covers **England only**. MOT-based figures cover GB. Census 2021 covers England and Wales.

**A 2025 NTS caveat that matters:** in 2025 the NTS moved to a digital travel diary. It "appears to be associated with a lower rate of recording for certain types of trips", including car driver trips. Commuting trips were not affected, and trip length was not systematically affected ([NTS 2025 main findings](https://www.gov.uk/government/statistics/national-travel-survey-2025/nts-2025-introduction-and-main-findings)). **Use 2024 NTS trip rates for calibration.** For 2025, use only the interview-based items (car ownership, fuel mix).

---

## 1. Annual mileage per car: distribution and modifiers

### 1.1 Shape of the distribution (MOT-based)

The NTS table of annual mileage by band (NTS0904, England, 2002 onwards) exists ([NTS09 index](https://gov.uk/government/statistical-data-sets/nts09-vehicle-mileage-and-occupancy)), but its values could not be retrieved. The best band evidence obtained is below.

**MOToring Along, RAC Foundation 2017 (Cairns, Anable, Chatterton, Wilson, Morton). GB private cars, 2011 MOT data** ([PDF](https://uwe-repository.worktribe.com/OutputFile/878388)):
- Under 5,000 mi/yr: about 34%. 5,000–12,000: about 52%. 12,000 or more: about 14%.
- The regional share doing over 12k ranges from 10% to 16%. The share under 5k ranges from below 24.7% to above 45.7% across area deciles.

**Field Dynamics, GB light vehicles, 2021 MOT data** ([PDF](https://www.field-dynamics.co.uk/wp-content/uploads/2017/04/GBMOTMileageReport-FieldDynamics-HighQuality.pdf)). This is a COVID-depressed year, and Ford Transit appears among its models, so vans are included:

| Band | 0–5k | 5–10k | 10–15k | 15–20k | 20k+ (three bands combined) |
|---|---|---|---|---|---|
| % vehicles | 53.6 | 32.5 | 9.4 | 2.6 | 1.9 |

- Its national average was 7,124 mi in 2019, 6,201 in 2020 and 5,506 in 2021.
- 57% of vehicles did under 100 mi/week and 87% under 200 mi/week.

**DVSA anonymised MOT, tests from 30 Dec 2024 to 30 Dec 2025, 28.6m vehicles with two readings at least 300 days apart.** This is a commercial blog analysis, not official statistics, though the method is transparent ([motcheckup](https://www.motcheckup.co.uk/research/real-uk-car-mileage-2026)). Annual mileage taken between consecutive readings:

| Fuel | P25 | Median | P75 |
|---|---|---|---|
| Petrol | 2,708 | 4,931 | 7,849 |
| Diesel | 4,113 | 6,879 | 10,449 |

**Fitted lognormals [derived]:**
- Petrol: μ = ln(4,931) = 8.503, σ = ln(P75/P25)/1.349 = 0.79. Implied mean ≈ 6,730 mi.
- Diesel: μ = 8.836, σ = 0.69. Implied mean ≈ 8,740 mi.

DfT's own description of MOT annual mileage is "highly skewed". At age 4 the modal band is 5–10k; at age 20 the modal band is 250–2,000 ([DfT experimental MOT statistics](https://assets.publishing.service.gov.uk/media/5a7c729c40f0b626628ac212/experimental-statistics-mot-data.pdf)).

### 1.2 By vehicle age

Average annual mileage of private cars, 2011 ([MOToring Along](https://uwe-repository.worktribe.com/OutputFile/878388)):

| Age (years) | 0–3 | 3–4 | 4–5 | 5–6 | 6–7 | 7–8 | 8–9 | 9–10 | 10–11 | 11–12 | 12–13 | 13+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Miles | 8,711 | 9,074 | 8,763 | 8,378 | 8,020 | 7,597 | 7,210 | 6,892 | 6,506 | 6,136 | 5,844 | 4,448 |
| Index vs 0–3 [derived] | 1.00 | 1.04 | 1.01 | 0.96 | 0.92 | 0.87 | 0.83 | 0.79 | 0.75 | 0.70 | 0.67 | 0.51 |

- Average car age by mileage band: 10.0 years for under 5k, 7.3 for 5–12k, 6.3 for 12k or more (same source).
- Average UK licensed car age at end-2024 was 10 years ([VLS 2024](https://www.gov.uk/government/statistics/vehicle-licensing-statistics-2024/vehicle-licensing-statistics-united-kingdom-2024)).

### 1.3 By fuel type (EV-relevant)

Cars under 3 years old, estimated average annual mileage. RAC Foundation, more than 1.2m MOT tests ([RAC Foundation, Jul 2025](https://racfoundation.org/media-centre/at-least-one-in-twenty-car-miles-driven-is-now-zero-emission)):

| Year | Petrol | Diesel | PHEV | BEV | All |
|---|---|---|---|---|---|
| 2024 | 7,585 | 10,728 | 9,367 | 10,054 | 8,460 |
| 2023 | 7,005 | 9,903 | 8,943 | 9,032 | 7,740 |
| 2019 | 7,170 | 11,451 | 11,608 | 8,868 | 8,413 |
| 2015 | 7,267 | 12,107 | 11,257 | 5,966 | 9,648 |

- In 2024 new BEVs averaged 1.33× the mileage of new petrol cars [derived] and 94% of new diesel mileage (source).
- BEVs were 3.8% of the fleet but drove 5.3% of car miles at end-2024 (source).
- 2011 private cars: diesel 10,699 vs petrol 6,418. Diesels were 24% of cars and 31% of miles ([MOToring Along](https://uwe-repository.worktribe.com/OutputFile/878388)).
- **Selection effect:** the fuel gap "reflects who bought which fuel type" ([motcheckup](https://www.motcheckup.co.uk/research/real-uk-car-mileage-2026)). High-mileage drivers choose diesel or BEV; the fuel itself does not cause the mileage.
- England fleet mix, 2025: petrol 57%, diesel 28%, hybrid 8%, BEV 5%, PHEV 2% ([NTS 2025 car availability](https://www.gov.uk/government/statistics/national-travel-survey-2025/nts-2025-household-car-availability-and-trends-in-car-trips)).

### 1.4 Company vs private

| Measure | Company cars | Private cars | All cars |
|---|---|---|---|
| NTS 2010, mi/yr ([NTS 2010 ch.9](https://assets.publishing.service.gov.uk/media/5a798e7fed915d04220695c1/nts2010-09.pdf)) | 19,190 | 7,910 | 8,430 |
| NTS 2009 ([BusinessCar](https://www.businesscar.co.uk/news/fleet-travel-plummeting/)) | 18,380 | 7,970 | – |

- That is a ratio of about 2.4× [derived].
- In 2010 company cars did 7,490 business miles and 6,450 commuting miles (NTS 2010 ch.9).
- MOT data, ages 0–3: company 13,565 vs private 8,711 ([MOToring Along](https://uwe-repository.worktribe.com/OutputFile/878388)).
- Current NTS0901 values (by ownership, fuel and purpose) were not retrieved. **Gap.**

### 1.5 Rural vs urban

- Per-car mileage is higher in rural areas and lower in urban ones, including a belt of low usage from London to the south coast. No numeric split is published in [MOToring Along](https://uwe-repository.worktribe.com/OutputFile/878388).
- Regional averages ran from 6,428 to 7,757 mi in 2011. Area deciles have cut-points at 6,181, 6,557, 6,809, 7,030, 7,243, 7,462, 7,711, 8,016 and 8,471 (same source).
- 2021 MOT: Scotland is highest at 5,863 and the South West lowest at 5,231 ([Field Dynamics](https://www.field-dynamics.co.uk/wp-content/uploads/2017/04/GBMOTMileageReport-FieldDynamics-HighQuality.pdf)).
- Traffic, 2019, cars and taxis: rural roads 160.2bn vehicle-miles vs urban 102.6bn, so 61% rural [derived] ([Road Traffic Estimates 2021](https://stalbans.gov.uk/sites/default/files/documents/publications/planning-building-control/Park%20Street%20Inquiry/CD11/CD11.31%20Road%20Traffic%20Estimates%20Great%20Britain%202021.pdf)). This counts where cars are driven, not where their owners live.

---

## 2. Driver and household level

### 2.1 Car miles per person (driver plus passenger), by sex and age, England

| | 2023 ([NTS 2023](https://www.gov.uk/government/statistics/national-travel-survey-2023/nts-2023-car-availability-and-trends-in-car-trips)) | 2024 ([NTS 2024](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips)) | 2025 ([NTS 2025](https://www.gov.uk/government/statistics/national-travel-survey-2025/nts-2025-household-car-availability-and-trends-in-car-trips)) |
|---|---|---|---|
| Female | 4,340 | 4,314 | 3,885 |
| Male | 5,042 | 4,940 | 4,640 |
| Peak male group (miles) | 50–59: 7,306 (as driver) | 50–59: 6,712 | 50–59: 6,190 |
| Peak female group (miles) | 40–49: 5,814 (as driver) | 50–59: 5,423 | 50–59: 5,084 |

- Car driver trips per person: 363 in 2023, 357 in 2024, 323 in 2025. The 2025 fall is partly the diary change.
- Car driver trips peak at 584 for men aged 50–59 and 570 for women aged 40–49, both in 2024 ([NTS 2024 purpose](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-trips-by-purpose-age-mode-and-sex)).
- Licence holding is 75% of people aged 17+: 80% of men and 71% of women ([NTS Factsheet 2024](https://assets.publishing.service.gov.uk/media/68e8f5af57038b5739b98656/NTS_Factsheet_2024.pdf)).
- The average English adult drives about 5,680 mi/yr. The top 5% "excess" users drive about 4.8× that, roughly 27,300 mi [derived]. Excess mileage is predicted by sex, employment, socio-economic status, high income, company car access, residential location, density, owning several cars, business travel and diesel ([Wadud et al. 2022, TRD 109](https://eprints.whiterose.ac.uk/190402)).
- Full NTS tables of driver miles by age, sex, employment, income and household type (NTS0605/9902/9904 family) were not retrieved. **Gap.**

### 2.2 Cars per household

| Cars | England 2023 | England 2024 | England 2025 |
|---|---|---|---|
| 0 | 22% | 22% | 25% |
| 1 | 44% | 44% | 42% |
| 2+ | 34% | 34% | 33% |

Sources: [2023](https://www.gov.uk/government/statistics/national-travel-survey-2023/nts-2023-car-availability-and-trends-in-car-trips), [2024](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips), [2025](https://www.gov.uk/government/statistics/national-travel-survey-2025/nts-2025-household-car-availability-and-trends-in-car-trips). The NTS publishes no separate 3+ split in these chapters.

- Census 2021, England: 24% of households have no car and 35% have two or more ([GMCA briefing](https://greatermanchester-ca.gov.uk/media/9704/car-availability-gmca-census-2021-briefing-final.pdf)). The TS045 0/1/2/3+ counts exist but were not retrieved.

**By income quintile, England 2024** ([NTS 2024](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips)):

| | No car | 2+ cars | Adults who are main drivers |
|---|---|---|---|
| Lowest quintile | 40% | 15% | 41% |
| Highest quintile | 14% | 46% | 66% |

**By area type, England 2017/18, households with no car** ([NTS 2018](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/823068/national-travel-survey-2018.pdf)):
- Urban conurbations 34% (London 45%), urban cities and towns 21%, rural towns and fringe 14%, most rural 7%.
- More than half of the most rural households have two or more cars or vans.

**Household with a car vs without** (2019, per person): 7,303 car miles in a household with a car vs 2,835 without ([NTS 2019 factsheets](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/906847/nts-2019-factsheets.pdf)).

---

## 3. Trip structure

### 3.1 Purpose

- **Commuting:** 111 trips and 1,007 mi per person in 2024, the purpose with the most miles. That is about 9.1 mi per trip [derived]. In 2025 it was 112 trips and 1,031 mi ([NTS 2024](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-trips-by-purpose-age-mode-and-sex); [NTS 2025](https://www.gov.uk/government/statistics/national-travel-survey-2025/nts-2025-trips-by-purpose-age-mode-and-sex)).
- **Visiting friends:** 892 mi in 2024.
- **Shopping:** 167 trips and 620 mi in 2024 (same source).
- **Commuting trips by sex, 2024:** 125 for men and 98 for women, down 23% and 17% respectively on 2019 ([Factsheet 2024](https://assets.publishing.service.gov.uk/media/68e8f5af57038b5739b98656/NTS_Factsheet_2024.pdf)).
- **Business:** 567 mi per person in 2018 ([NTS 2018](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/823068/national-travel-survey-2018.pdf)).
- **Per car:** average annual mileage fell from 9,200 to 7,600 between 2002 and 2018. About 900 mi of the 1,600 mi fall was business (same source).
- Shares of **car** miles by purpose (NTS0901 by purpose, NTS0409) were not retrieved. **Gap.**

### 3.2 Weekday vs weekend (older baseline)

GB, NTS 2010, trips per person per year by day ([NTS 2010 ch.5](https://assets.publishing.service.gov.uk/media/5a796f44e5274a3864fd6f46/nts2010-05.pdf)):
- Average weekday 149 (Friday 154), Saturday 137, Sunday 108.
- Commuting is about 27–29 trips on each weekday. Shopping is 44 on Saturday vs 26 on an average weekday.
- Car-driver trips peak at 17:00–17:59 on weekdays. At weekends the single peak is 11:00–11:59.
- Car traffic in 2024 peaked at 4–6pm on weekdays and 12–2pm at weekends ([RTE 2024 by vehicle type](https://www.gov.uk/government/statistics/road-traffic-estimates-in-great-britain-2024/road-traffic-estimates-in-great-britain-2024-traffic-in-great-britain-by-vehicle-type)).
- TRA0306 (day-of-week index) exists ([TRA index](https://www.gov.uk/government/statistical-data-sets/road-traffic-estimates-tra)); its values were not retrieved.

### 3.3 Trip length and long trips

- Average car trip is 8.4 mi, unchanged from 2002 to 2019 ([NTS 2019](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/906276/national-travel-survey-2019.pdf)).
- 2018: 25% of all trips were under 1 mi, 68% under 5 mi, and 58% of car-driver trips were under 5 mi ([NTS 2018](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/823068/national-travel-survey-2018.pdf)).
- Trips of 50–150 mi are about 80% by car (2014–18 average, same source).
- Trips over 50 mi by purpose, 2006/10: visiting friends 22%, business 18% ([NTS 2010 ch.4](https://assets.publishing.service.gov.uk/media/5a78d72ce5274a277e68fe12/nts2010-04.pdf)).
- **The number of trips over 100 mi per driver per year was not obtained. Gap.**

### 3.4 Commute distance and working from home: Census 2021, England and Wales

Source: [ONS Travel to work](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/bulletins/traveltoworkenglandandwales/census2021). Taken during lockdown restrictions; ONS advises care when using these figures.

| Band | <2 km | 2–5 | 5–10 | 10–20 | 20–30 | 30–40 | 40–60 | 60+ |
|---|---|---|---|---|---|---|---|---|
| % of all employed | 11.0 | 12.6 | 11.8 | 10.5 | 4.1 | 1.7 | 1.3 | 1.4 |
| % of fixed-distance commuters [derived, ÷54.4] | 20.2 | 23.2 | 21.7 | 19.3 | 7.5 | 3.1 | 2.4 | 2.6 |

- **Mainly working from home:** 31.2% of employed people (London 42.1%, North East 24.8%).
- **Other:** the remaining 14.4% [derived] is mostly no fixed place of work.
- **Car or van driver to work:** 45.1% (London 20.6%, East Midlands 53.2%, Wales 56.5%).
- Hybrid-working shares after 2021 (ONS Opinions and Lifestyle Survey) were not retrieved. **Gap** [unverified: roughly a quarter to a third of workers are hybrid].

---

## 4. Seasonality

- TRA0305 ("Average daily traffic flow by month, 5-year average") is the right table ([TRA index](https://www.gov.uk/government/statistical-data-sets/road-traffic-estimates-tra)). Its indices were not retrieved.
- Car traffic was 256.1bn vehicle-miles in 2024, 2.6% below 2019. Monthly levels ran from +1% to −4% against the same month of 2019, influenced by "weather, holiday periods" ([RTE 2024](https://www.gov.uk/government/statistics/road-traffic-estimates-in-great-britain-2024/road-traffic-estimates-in-great-britain-2024-traffic-in-great-britain-by-vehicle-type)).
- Year to March 2025: 255.4bn ([provisional estimates](https://www.gov.uk/government/statistics/provisional-road-traffic-estimates-great-britain-april-2024-to-march-2025)).
- NTS 2006/10 trips per person per month: highest in March and May (87), lowest in February and December (76). Education trips collapse in August while holiday trips peak ([NTS 2010 ch.5](https://assets.publishing.service.gov.uk/media/5a796f44e5274a3864fd6f46/nts2010-05.pdf)).
- [unverified] The usual TRA0305 profile has about ±8–10% amplitude, with a January/December trough and a summer peak.

---

## 5. Persistence: how stable is one driver's mileage from year to year?

- No published, fetched source quantifies how one car's mileage correlates between consecutive MOT intervals. MOToring Along says longitudinal analysis is a "future opportunity" ([PDF](https://uwe-repository.worktribe.com/OutputFile/878388)). DfT's 2013 MOT release describes the pairing method but gives no results ([DfT](https://assets.publishing.service.gov.uk/media/5a7c729c40f0b626628ac212/experimental-statistics-mot-data.pdf)).
- Wilson et al. (2012) **assume** a per-vehicle usage factor ~ Gamma(shape 2, scale ½) with mean 1, plus day-to-day noise ~ U[0, 2]. They note that MOT data cannot identify the noise. They also report average per-vehicle use falling about 1.5% a year, from 7,840 mi in 2007 to 7,620 in 2009 ([ISTTT paper](https://aura.abdn.ac.uk/server/api/core/bitstreams/75d95063-404e-4e2d-8397-45ccf49f9784/content)).
- **Gap. Design choice in §(c).**

---

## 6. Company cars and salary sacrifice

**HMRC benefit-in-kind recipients** ([HMRC BiK commentary, Jul 2026](https://www.gov.uk/government/statistics/benefits-in-kind-statistics-july-2026/benefit-in-kind-statistics-commentary-july-2026)):
- 760k in 2022-23, 840k in 2023-24, and 920k in 2024-25 (provisional, likely an undercount because of payrolling).
- 2024-25 zero-emission cars: 467k, which is 51% of recipients.
- 1–50 g/km (mostly PHEVs): 220k.
- Fuel benefit recipients: 40k.
- 2023-24: 342k electric. 2022-23: about 29% ([BVRLA](https://www.bvrla.co.uk/resource/govt-reports-further-year-of-company-car-growth.html)).
- Benefit-in-kind company cars are about 2.7% of the 33.97m licensed UK cars [derived; [VLS 2024](https://www.gov.uk/government/statistics/vehicle-licensing-statistics-2024/vehicle-licensing-statistics-united-kingdom-2024)].

**Company-registered new cars, 2024:** zero-emission 82%, PHEV 77%, diesel 60%, petrol 58%, hybrid 54% ([VLS 2024](https://www.gov.uk/government/statistics/vehicle-licensing-statistics-2024/vehicle-licensing-statistics-united-kingdom-2024)). "Company" here includes lessors, so it also covers leased private cars.

**Salary sacrifice:** deliveries rose 47% year on year, and 84% of new salary-sacrifice cars in Q4 2023 were BEVs ([Fleet News/BVRLA](https://www.fleetnews.co.uk/news/salary-sacrifice-boom-shows-ev-incentives-work-for-private-buyers)). No absolute count was found. **Gap.**

**Mileage:** company cars average about 2.4× private cars (NTS 2010; §1.4). This predates the shift to EVs and recent business-mileage cuts.

---

## 7. Off-street parking and home charging (added scope)

**Confirmed:**
- England vehicles parked overnight, 2024: 64% on private property excluding garages (50% in 2002), 9% in garages (22% in 2002) ([NTS 2024](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips)).
- 2022: 62% and 10% ([NTS 2023](https://www.gov.uk/government/statistics/national-travel-survey-2023/nts-2023-car-availability-and-trends-in-car-trips)).
- So about 72–73% of **vehicles** are kept off-street [derived]. This is per vehicle, not per home, and it over-represents homes with several cars.
- NTS0908 gives where vehicles are parked overnight by rural–urban classification ([NTS09 index](https://gov.uk/government/statistical-data-sets/nts09-vehicle-mileage-and-occupancy)). Its values were not retrieved.

**Not confirmed in this session (search allowance used up), all [unverified]:**
- DfT/OZEV estimate that about 65% of homes have off-street parking, ranging from 7% in Westminster to 84% in Flintshire (coordinator-supplied).
- Zapmap: about 9m households without off-street parking.
- English Housing Survey parking by dwelling type and tenure, and the RAC Foundation "Standing Still" parking report.
- DfT EV driver tracker: about 90% of BEV drivers have off-street parking and about 9% rely on public charging only.
- Expected direction [unverified]: detached and semi-detached homes are high, terraces and flats low; owner-occupiers above renters; rural above urban, and London lowest.

---

## (a) Distributions for the simulation to draw from

| Attribute | Distribution / bands | Conditioning variables | Source |
|---|---|---|---|
| Car annual mileage (ICE) | Lognormal. Petrol μ 8.503, σ 0.79. Diesel μ 8.836, σ 0.69 [derived] | Fuel; then scale by age index | [motcheckup DVSA](https://www.motcheckup.co.uk/research/real-uk-car-mileage-2026) |
| Mileage bands (calibration target) | <5k 34%, 5–12k 52%, ≥12k 14% (2011) | Region (≥12k share 10–16%) | [MOToring Along](https://uwe-repository.worktribe.com/OutputFile/878388) |
| Age multiplier | 1.00 at 0–3 years down to 0.51 at 13+ (table §1.2) | Vehicle age | same |
| BEV mileage | Mean 10,054 for cars under 3 years (2024); about 1.33× petrol [derived] | Fuel, newness; selection by driver type | [RAC 2025](https://racfoundation.org/media-centre/at-least-one-in-twenty-car-miles-driven-is-now-zero-emission) |
| Company car flag | About 2.7% of cars [derived]; 51% of them ZEV | Income, employment | [HMRC](https://www.gov.uk/government/statistics/benefits-in-kind-statistics-july-2026/benefit-in-kind-statistics-commentary-july-2026) |
| Company mileage multiplier | About 2.4× private (2010) | Company flag | [NTS 2010](https://assets.publishing.service.gov.uk/media/5a798e7fed915d04220695c1/nts2010-09.pdf) |
| Cars per household | 0: 22%, 1: 44%, 2+: 34% | Income (0-car 40%→14%; 2+ 15%→46%); area (0-car 7–45%) | [NTS 2024](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips), [NTS 2018](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/823068/national-travel-survey-2018.pdf) |
| Licence holder | M 80%, F 71% (17+) | Sex, age | [Factsheet 2024](https://assets.publishing.service.gov.uk/media/68e8f5af57038b5739b98656/NTS_Factsheet_2024.pdf) |
| Commute mode/WFH | WFH 31.2%; car driver 45.1% | Region (WFH: London 42.1%, NE 24.8%) | [ONS Census](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/bulletins/traveltoworkenglandandwales/census2021) |
| Commute distance | 8 bands, renormalised (§3.4) | Region, area | same |
| Weekday/weekend trips | Weekday 149, Sat 137, Sun 108 (2010 index) | Day | [NTS 2010 ch.5](https://assets.publishing.service.gov.uk/media/5a796f44e5274a3864fd6f46/nts2010-05.pdf) |
| Monthly factor | TRA0305 (values pending) | Month | [TRA index](https://www.gov.uk/government/statistical-data-sets/road-traffic-estimates-tra) |
| Year-to-year persistence | Not published; see (c) | – | – |
| Off-street parking (home) | Vehicles: 64% private property + 9% garage. Homes: about 65% [unverified] | Dwelling type, tenure, LA (7–84%) [unverified] | [NTS 2024](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips) |
| BEV ownership given parking | About 90% of BEVs at homes with off-street parking [unverified] | Parking flag | DfT EV tracker [unverified] |

## (b) Population checks the simulated book should reproduce

1. GB car and taxi traffic: 256.1bn vehicle-miles in 2024 ([RTE 2024](https://www.gov.uk/government/statistics/road-traffic-estimates-in-great-britain-2024/road-traffic-estimates-in-great-britain-2024-traffic-in-great-britain-by-vehicle-type)). Divided by 33.97m UK cars, that is about 7,540 mi per car [derived, a rough check that mixes UK and GB].
2. Under-3-year-old cars by fuel, 2024: 8,460 all; petrol 7,585; diesel 10,728; PHEV 9,367; BEV 10,054.
3. BEVs are 3.8% of cars and 5.3% of car miles ([RAC](https://racfoundation.org/media-centre/at-least-one-in-twenty-car-miles-driven-is-now-zero-emission)).
4. Household cars 0/1/2+ = 22/44/34 (England, 2024).
5. Car miles per person, driver plus passenger: F 4,314, M 4,940 (2024).
6. 31.2% working from home and 45.1% driving to work (Census 2021).
7. Commuting is about 1,000 mi per person per year at about 9 mi per trip [derived].
8. About 920k company cars, 51% of them ZEV (2024-25).
9. About 72% of vehicles parked off-street overnight [derived].
10. Top 5% of drivers average about 4.8× the mean adult mileage ([Wadud 2022](https://eprints.whiterose.ac.uk/190402)).

## (c) Named gaps and suggested design choices

| Gap | Suggested design choice |
|---|---|
| Current NTS0904 bands and NTS0901 company/private/fuel/purpose | Fetch the ODS; until then, calibrate the lognormal to the MOT quartiles and the 34/52/14 bands. |
| Persistence of individual mileage | Use a two-part draw: a persistent person factor ~ lognormal (most of the variance) times a yearly shock ~ lognormal with σ ≈ 0.15–0.25 (assumed). Add a regime-change probability (job or house move, retirement) of about 10%/yr (assumed). Validate later against paired-MOT panels. |
| Driver miles by age × sex × employment × income | Build the driver as household mileage × main-driver share. Condition the age/sex profile on the NTS peak figures (§2.1). Fetch NTS0605/9902. |
| Long-trip (>100 mi) frequency | Model a separate Poisson stream of long trips (assumed about 6–12 per year per driver [unverified]). This matters for EV public rapid charging, not home kWh. |
| Monthly and day-of-week indices | Fetch TRA0305/0306. Placeholder: ±8% sinusoid with a summer peak [unverified]. |
| Hybrid working after 2021 | Model a commute-days-per-week distribution (0–5). Calibrate to ONS Opinions and Lifestyle Survey once fetched. |
| Off-street parking by dwelling type and tenure | Fetch the English Housing Survey parking tables. Condition on dwelling type first, because flats and terraces drive most of the variation [unverified]. |
| BEV uptake by parking access and public-only costs | Draw BEV ownership with strong parking dependence. For public-only BEVs, move charging out of the home load (zero home kWh) and apply public tariffs. |
| Selection effect between fuel and mileage | Draw mileage **from the person first**, then fuel choice given mileage. Do not apply the RAC fuel ratios as causes. |

## Done

Published on 25 Oct as the Knowledge page `site/knowledge/who-drives-how-far-and-where-they-park/`, with the note `docs/market_research/who_drives_how_far_and_where_they_park_2026-10-25.md`. The note carries the verification pass that the 25 Oct verify steer asks for: each [unverified] item is marked confirmed, corrected or still open, and no open item is stated on the page as a claim. Counts as recorded: Tally for the index: confirmed 6 · corrected 3 · open 9 (incl. 2 unpublished).
