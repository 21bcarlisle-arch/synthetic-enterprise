# Director evidence: gap closure tdcv vat rts caltrack eco iuf

**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

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

# Poesys research gap-closure pack, October 2026

I worked through all ten gaps. Five are closed (1, 3, 7, 8, and 5 with a caveat), four are partly closed (2, 4, 6, 9) and one is still open (10). The web-search budget for this turn ran out before I finished. The gaps still marked open or partly closed can be continued in a follow-up message.

Three access problems limited the work. The shell could not reach gov.uk, assets.publishing.service.gov.uk or ons.gov.uk (the proxy refused them). WebFetch would not open the NTS `.ods` table files, legislation.gov.uk, the LBNL acceptance-criteria PDF or Ofgem's 2019 TDCV letter.

Tags used below: **[derived]** is my own arithmetic. **[unverified]** is from memory and was not confirmed against a source this session.

---

## Gap 1: CalTRACK, IPMVP Options A to D, ASHRAE Guideline 14 uncertainty

**Status: CLOSED for CalTRACK. PARTLY closed for IPMVP and ASHRAE Guideline 14.**

**CalTRACK** (section numbers are from [CalTRACK Methods](https://caltrack-technical-documentation.readthedocs.io/en/latest/methods.html)):

- **Baseline length:** 365 days, ending when the intervention starts (2.2.1.1, 3.1.3).
- **Data sufficiency, daily and billing:**
  - No more than 37 missing days, which is 10% (2.2.1.2).
  - Interval data can be turned into a daily value only if no more than 50% of the readings are missing (2.2.2.1, 2.2.2.3).
  - Temperature data must cover at least 90% of each billing period (2.2.3.2).
  - Zero readings count as missing for electricity but not for gas (2.2.1.4).
- **Data sufficiency, hourly:**
  - More than 90% of hours must be present in the target calendar month and in each neighbouring month of the previous year (2.2.1.2).
  - Temperature gaps of up to 6 hours in a row may be filled by interpolation. Longer gaps are not allowed (2.2.4.1).
- **Billing data rules:**
  - Off-cycle reads shorter than 25 days are dropped (2.2.3.4).
  - Monthly-style periods longer than 35 days, and two-monthly periods longer than 70 days, are dropped (2.2.3.5).
  - Estimated reads are merged into the next period, up to 70 days.
  - Billing models are fitted by weighted least squares, weighted by the number of days in each period. Daily models use ordinary least squares (3.4.1, 3.4.2).
- **Daily and billing model forms (3.4.3.1):**
  - Intercept only
  - Heating degree days (HDD) only
  - Cooling degree days (CDD) only, for electricity only
  - HDD plus CDD, for electricity only
  - Coefficients must not be negative. The model with the highest adjusted R² is chosen. The document sets no p-value test.
- **Balance-point search (3.2):**
  - The search runs from 30°F to 90°F, with no more than 3°F between candidate values.
  - The cooling balance point must be at or above the heating one.
  - Each year needs at least 10 days with non-zero degree days (not required for billing data) and at least 20 degree days in total.
  - Cooling models are not tried for gas.
- **Hourly model (3.7 to 3.12):**
  - Uses a time-of-week and temperature model, with 168 hourly time-of-week slots starting on Monday.
  - Up to 12 month-by-month models are fitted. Data from the same month gets weight 1, and data from neighbouring months gets weight 0.5.
  - Temperature bin edges are at 30, 45, 55, 65, 75 and 90°F. A bin with fewer than 20 hours is merged into the next one.
  - Occupancy is decided by a fixed balance-point model (50°F heating, 65°F cooling). A time-of-week slot counts as occupied if the model underpredicts more than 65% of its points.
  - A single 365-day model is allowed if the monthly normalised mean bias error (NMBE) stays within 1% for all but two months.
- **Uncertainty (section 4):**
  - Fractional savings uncertainty (FSU) is calculated with a t-statistic, usually at 90% confidence.
  - Billing coefficients: a = −0.00022, b = 0.03306, d = 0.94054. Daily coefficients: a = −0.00024, b = 0.03535, d = 1.00286.
  - The default limit on CV(RMSE) per building is 100%, and the buyer can waive it.
  - The buyer sets the FSU limit. Examples given: under 15% for non-wires alternatives and 25% for pay-for-performance.
  - Site FSUs are combined across a portfolio by root-sum-of-squares.
  - No FSU method is given for hourly models, and annualising partial periods is not supported.
  - The specification has some internal inconsistencies. For example, 3.4.3.2 says "not negative" but then writes strict ">0" inequalities, and 3.8.3 refers to a section 3.6.5 that does not exist.

**IPMVP Options A to D.** These are a secondary summary from the [NSW M&V Guide Module 2 (Aug 2023)](https://www.energy.nsw.gov.au/sites/default/files/2023-09/Measurement_and_Verification_Guide_Module2_Aug_2023.pdf). It cites IPMVP Core Concepts EVO 10000-1:2022 and is not EVO's own wording.
- **A, retrofit isolation with key-parameter measurement:** key parameters are measured, and the rest are estimated.
- **B, retrofit isolation with all-parameter measurement:** short-term or continuous measurement of energy in both the baseline and the reporting period.
- **C, whole facility:** analysis of the utility meter data for the whole site.
- **D, calibrated simulation:** a simulation calibrated to hourly or monthly billing data.
- **Non-routine adjustment:** "an adjustment made when determining energy savings to account for a non-routine event." A non-routine event is "an unexpected change that causes energy use within the measurement boundary to change."
- **Routine adjustment:** the NSW guide does not define it. Changes driven by the model's independent variables are handled inside the model. EVO's own wording was not retrieved.

**ASHRAE Guideline 14.** The [EVO M&V Focus #5 article](https://evo-world.org/en/news-media/m-v-focus/868-m-v-focus-issue-5/1164-why-r2-doesn-t-matter) states: "ASHRAE Guideline 14 requires that the savings uncertainty be less than 50% of the annual savings at 68% confidence." I could not confirm the CV(RMSE) and NMBE limits. From memory, they are about 15% monthly and 30% hourly CV(RMSE) for calibrated simulation, with NMBE of ±5% monthly and ±10% hourly [unverified].

---

## Gap 2: Share of EV charging energy by location in GB

**Status: PARTLY.** I found no source giving the split by **energy** (kWh) across home, workplace, public slow and rapid. Everything found measures access or how often drivers use each location.

- **DfT/Ipsos diary study** (more than 1,000 drivers, 12 months; [Forecourt Trader](https://forecourttrader.co.uk/news/government-study-finds-90-of-ev-drivers-can-charge-at-home/709930.article)):
  - 91% of battery-electric drivers and 88% of plug-in hybrid drivers can charge at home.
  - 76% of battery-electric drivers have a home wallbox.
  - 27% use workplace charging at least weekly, and 32% use public hubs at least weekly.
  - Drivers usually charge once or twice a week.
- **Zapmap survey 2025** (3,976 battery-electric drivers, Sept to Oct 2025; [Zapmap](https://www.zapmap.com/news/ev-charging-survey-2025-results)):
  - 23% have no home charging, up from 21% in 2024.
  - 70% use charging hubs, and 49% use the public network less than once a month.
- **Zenith EVXperience 2025** (more than 3,600 drivers; [Fleet World](https://fleetworld.co.uk/eight-in-10-ev-drivers-still-reliant-on-home-charging-in-driveway-divide)):
  - 80% charge off-street at home, 4% on-street and 29% at public hubs.
  - In London, 60% charge off-street at home and 22% on-street.
- **Public network energy** ([Zapmap x GFI utilisation report 2026](https://www.zapmap.com/sites/default/files/2026-10/Zapmap%20x%20GFI%20utilisation%20report%202026.pdf)):
  - About 350 GWh was delivered in Q4 2025, up from 289 GWh in Q4 2024.
  - Ultra-rapid chargers (150 kW and above) delivered 52% of public energy, up from 44%.
  - Multiplying Q4 by four gives about 1.4 TWh a year of public charging [derived]. This is an upper-end run-rate, because the network is growing and earlier quarters were lower.
- **Forecast** ([Field Dynamics via Zapmap](https://www.zapmap.com/news/field-dynamics-forecasts-future-ev-energy-demands-and-infrastructure-growth-new-report)): total demand from cars and vans of 18 TWh by 2030 and 80 TWh by 2050, with 21 TWh of on-street public charging by 2050. That makes on-street about 26% in 2050 [derived].
- **Still missing:** a measured current home share by energy. The obvious next step is to divide public kWh by total EV kWh.

---

## Gap 3: Restricted-meter count, storage-heating homes, radio teleswitch switch-off

**Status: CLOSED for the radio teleswitch switch-off. PARTLY for the meter and heater counts.**

- **Restricted meters:**
  - About 4 million of 29 million GB domestic electricity customers have restricted (Profile Class 2) meters. Fewer than 500,000 are non-Economy 7 restricted meters, down from 700,000 in 2015 according to the CMA. Source: [Ofgem statutory consultation, 1 Sept 2020](https://www.ofgem.gov.uk/system/files/docs/2020/08/statutory_consultation_extending_protections_for_non-e7_restricted_meter_customers_slc_22g.pdf).
  - About 3 million GB households, roughly 10%, are on Economy 7 or similar tariffs, as of early 2023. Of these, about 1.5 million have no storage heating. Source: [Sustainability First](https://sustainabilityfirst.org.uk/blog/443-economy-7-blog-frerk).
  - DESNZ subnational statistics give only the combined total of 29.3 million domestic meters in 2024, not split by profile class ([DESNZ 2024](https://www.gov.uk/government/statistics/subnational-electricity-and-gas-consumption-summary-report-2024/subnational-electricity-and-gas-consumption-summary-report-2024--2)).
  - A count for 2025 or 2026 is still open.
- **Storage heating:**
  - The English Housing Survey 2023-24 does not separate out storage heaters. It reports "2 million households (8%) used an electrical system for heating" in England ([EHS LCT fact sheet](https://www.gov.uk/government/statistics/english-housing-survey-2023-to-2024-low-carbon-technologies-in-english-homes-fact-sheet/english-housing-survey-2023-to-2024-low-carbon-technologies-in-english-homes-fact-sheet)).
  - "Over 1.7 million UK homes" use storage heaters. This is a secondary figure from [Sunamp](https://sunamp.com/blog/electric-storage-heaters-in-social-housing-challenges/), which cites an Octopus press release.
- **Radio teleswitch switch-off:**
  - About 600,000 meters were still in place in January 2025, and the original end date was 30 June 2025 ([Ofgem letter, 11 Feb 2025](https://www.ofgem.gov.uk/sites/default/files/2025-02/2025.02.11%20RTS%20Licence%20Modification%20-%20Open%20letter%20-%20Policy%20consultation-20250210104928.pdf)).
  - The switch-off was done region by region from 30 June 2025. Fewer than 154,000 meters were left in January 2026. It paused over winter, restarted in England and Wales on 2 March 2026, and was due to restart in Scotland in early April 2026 ([Ofgem, March 2026](https://www.ofgem.gov.uk/sites/default/files/2026-03/Ofgem%20Radio%20Teleswitch%20%28RTS%29%20policy%20consultation%20decision%20and%20update%20on%20phase-out.pdf)).
  - The minister reported it switched off for good at the end of June 2026, with a "small number" of meters left ([Express & Star, 16 July 2026](https://www.expressandstar.com/uk-news/rts-switch-off-completed-successfully-says-minister-8803190)).

---

## Gap 4: UKHSA minimum indoor temperature guidance

**Status: PARTLY.**

- **The 18°C recommendation:** "at least 18°C (65°F)" is a broad recommendation for everyone. It replaced the earlier advice of 21°C for living rooms and 18°C for bedrooms. People who are vulnerable through illness or poor mobility may want their homes warmer than 18°C, and active, healthy people may be comfortable cooler. Source: [UKHSA blog, 21 Oct 2014](https://ukhsa.blog.gov.uk/2014/10/21/preventing-avoidable-deaths-this-winter/), published with the Cold Weather Plan.
- **Current advice:** heat the rooms you use most, such as the living room and bedroom, "to at least 18°C". This is attributed to UKHSA, with a link to the gov.uk "Keep warm keep well" leaflet ([Healthwatch Kingston, Jan 2026](https://www.healthwatchkingston.org.uk/blog/2026-01-07/keeping-warm-and-well-staying-safe-cold-weather)). I could not open the gov.uk page itself.
- **No separate vulnerable-group threshold:** none was found. The guidance asks vulnerable people to heat above 18°C rather than giving them a different number.
- **Health-effect bands [unverified]:** from memory, the 2014 PHE minimum-temperature evidence review links temperatures below about 16°C with respiratory effects, about 9 to 12°C with higher blood pressure and cardiovascular risk, and below about 5°C with high hypothermia risk.

---

## Gap 5: ECO in-use factors by measure

**Status: CLOSED for ECO1. The ECO3 and ECO4 equivalents are still open.**

Source: [Ofgem ECO Measures Table v1.6, 2 Dec 2014](https://www.ofgem.gov.uk/ofgem-publications/83100/energycompaniesobligation-measures-pdf). The table says the factors are set in Schedule 3 of the Order and are "only applied to measures installed under CERO and CSCO." The in-use factor is a percentage cut to the modelled savings. The DECC Golden Rule note gives the cavity example: "reduced by an 'in-use factor' of 35%" ([DECC, withdrawn](https://assets.publishing.service.gov.uk/media/5a78d0e340f0b62b22cbd063/Golden_Rule_29_1.pdf)).

| Measure | In-use factor |
|---|---|
| Cavity wall: standard, hard-to-treat, party wall; internal or external insulation on cavity walls | 35% |
| Loft: virgin, top-up, rafter | 35% |
| Solid brick wall, internal or external insulation, built before 1967 (E&W) / 1965 (Scotland) | 33% |
| Solid brick wall built after those dates; non-brick solid wall; park home external insulation | 25% |
| Room-in-roof | 25% |
| Flat roof, underfloor, cylinder jacket, pipework, draught-proofing, glazing, doors | 15% |
| District heating connections and heat meters | 10% |
| Boilers, storage heaters, controls, heat pumps, solar PV and other generation | none given |

ECO3 and ECO4 use deemed scores with a "percentage of property treated" adjustment instead. I found no current in-use factor values for them ([ECO3 deemed scores methodology](https://www.ofgem.gov.uk/system/files/docs/2018/04/eco3_deemed_scores_methodology_document.pdf)).

---

## Gap 6: NTS annual mileage per car (NTS0901 and NTS0904)

**Status: PARTLY.**

- **Latest tables exist but were not read:** NTS0901 and NTS0904 were updated on 10 Sept 2026 with 2025 data ([DfT NTS09 tables](https://gov.uk/government/statistical-data-sets/nts09-vehicle-mileage-and-occupancy)). The download links are on that page.
- **Older figures, secondary source:** the average car did 7,600 miles in 2018, down from 9,200 in 2002. Diesel cars averaged 9,400 miles and petrol cars 6,600. Source: [NimbleFins](https://www.nimblefins.co.uk/average-car-mileage-uk). These figures are probably from NTS0901, but the page does not say so.
- **Context only:**
  - People travelled 6,082 miles each in 2024, across all modes. Cars made up 76% of miles in both 2024 and 2025 ([NTS 2024 factsheet](https://assets.publishing.service.gov.uk/media/68e8f5af57038b5739b98656/NTS_Factsheet_2024.pdf)).
  - The 2024 car fleet was 59% petrol, 30% diesel and 4% battery-electric ([NTS 2024](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips)).
- **Still needed:** the 2024 and 2025 per-car mean and the mileage-band distribution, which need someone to open the two table files directly.

---

## Gap 7: Ofgem typical domestic consumption values, 2016 to 2026

**Status: CLOSED.** The 2026 change is confirmed: gas medium 9,500 kWh and electricity medium 2,500 kWh.

All values are kWh per year, shown as low / medium / high.

| Values in use | Gas | Electricity, single-rate | Electricity, multi-rate (Economy 7) | Source |
|---|---|---|---|---|
| 2015 to Aug 2017 | 8,000 / 12,500 / 18,000 | 2,000 / 3,100 / 4,600 | 2,500 / 4,300 / 7,200 | [Ofgem letter, 22 Jun 2017](https://www.ofgem.gov.uk/system/files/docs/2017/08/tdcvs_2017_open_letter.pdf) ("current" column) |
| 1 Sept 2017 (proposed) | 8,000 / 12,000 / 17,000 | 1,900 / 3,100 / 4,600 | 2,500 / 4,200 / 7,100 | Same letter. It was adopted: the 2020 letter lists these as the previous values [derived] |
| 1 Apr 2020 ("2019 TDCV"; decided 6 Jan 2020) | 8,000 / 12,000 / 17,000 | 1,800 / 2,900 / 4,300 | 2,400 / 4,200 / 7,100 | [Ofgem decision letter](https://www.ofgem.gov.uk/sites/default/files/docs/2020/01/tdcvs_2020_decision_letter_0.pdf) |
| 1 Oct 2023 ("2023 TDCV") | 7,500 / 11,500 / 17,000 | 1,800 / 2,700 / 4,100 | 2,200 / 3,900 / 6,700 | [2026 decision](https://www.ofgem.gov.uk/sites/default/files/2026-05/Review%20of%20typical%20domestic%20consumption%20values%20decision.pdf) ("2023" column); [Oct 2023 cap letter](https://www.ofgem.gov.uk/sites/default/files/2023-10/Energy%20Price%20Cap%20Letter%20for%201%20October%202023%20%28new%20TDCV%29%20%281%29.pdf) |
| 1 Jul 2026 (decided 27 May 2026) | 6,000 / 9,500 / 14,000 | 1,600 / 2,500 / 3,800 | 1,900 / 3,400 / 6,100 | [Ofgem 2026 decision](https://www.ofgem.gov.uk/sites/default/files/2026-05/Review%20of%20typical%20domestic%20consumption%20values%20decision.pdf) |

- **No revision took effect in 2016.** The 2015 values stayed in use.
- **Economy 7 day/night split:** 58% peak and 42% off-peak, unchanged in 2026. Ofgem proposed 60/40 in 2023 and did not adopt it ([2023 call for input](https://www.ofgem.gov.uk/sites/default/files/2023-02/TDCV%202023_Call%20for%20Input.pdf)).
- **Typical bills at the 2026 values:**
  - July to September 2026, Direct Debit: £1,663 ([Ofgem summary](https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf)).
  - October to December 2026, Direct Debit: £1,723. Standard credit is £1,861, prepayment £1,678, and Economy 7 £1,046.

---

## Gap 8: Zero VAT on domestic electricity, 1 Oct 2026 to 31 Mar 2027

**Status: CLOSED.**

- **Ofgem's wording:** "reduce the level of VAT from all electricity bills from 5% to zero… from 1 October 2026 to 31 March 2027… VAT will remain unchanged for gas bills at 5%" ([Ofgem cap summary, Oct to Dec 2026](https://www.ofgem.gov.uk/sites/default/files/2026-08/Summary-of-changes-to-energy-price-cap-1-October-to-31-December-2026.pdf)).
- **HMRC guidance** ([Revenue and Customs Brief 10 (2026)](https://www.gov.uk/government/publications/revenue-and-customs-brief-10-2026-temporary-zero-rate-of-vat-for-domestic-electricity-in-great-britain/temporary-zero-rate-of-vat-for-domestic-electricity-in-great-britain), published 8 Sept 2026 and updated 30 Sept 2026):
  - The relief applies in Great Britain only. Northern Ireland stays at 5%.
  - It covers electricity qualifying for domestic or charity non-business use under VAT Notice 701/19. "Other fuel types are not affected."
  - For bills that span 1 Oct 2026, suppliers may set the VAT by the date the energy was used. Meter readings are recommended for the split.
  - The measure was announced on 21 July 2026.
- **Legal basis:** The Value Added Tax (Supplies of Domestic Electricity) Order 2026, SI 2026/987. It was made by the Treasury on 7 Sept 2026, laid on 8 Sept and came into force on 1 Oct 2026. It changes Schedule 8 of the VAT Act 1994 (zero-rating), with knock-on changes to Schedule 7A Group 1 ([lookuptax summary](https://lookuptax.com/tax-changes/united-kingdom/domestic-electricity-si-987-2026)). The specific enabling section was not confirmed, because legislation.gov.uk could not be fetched.
- **Policy reason:** cost of living. The cut takes about £45 a year off the typical capped bill. This year's cost is paid for by cancelling the £1.8bn Digital ID programme, and the measure will be reviewed at the Spring Budget ([Zemo](https://www.zemo.org.uk/news-events/news,government-cuts-rate-of-vat-on-domestic-electricity-to-zero-to-help-tackle-_4867.htm)).
- **Public chargepoints:** electricity sold at public chargepoints stays at 20% VAT (same Zemo source).

---

## Gap 9: Boiler lifetime and age profile in GB

**Status: PARTLY.** No survey of the installed stock or of age at replacement was found.

- **Which?** ([Sept 2025](https://www.which.co.uk/policy-and-insight/article/from-panic-to-planned-why-homeowners-and-the-government-need-a-boiler-retirement-plan-aslRL7e6Golw); Yonder survey, June 2025):
  - Among 938 homeowners whose system is 8 or more years old, 35% have one aged 8 to 10 years and 65% one over 10 years. 87% of these are gas.
  - It quotes industry guidance of a 10 to 15 year lifespan.
  - Among recent replacers, 39% of those who had not planned ahead faced an emergency replacement, against 19% of planners.
  - 27% of owners of older systems say they will wait for a breakdown.
- **HomeServe** ([9 Mar 2026](https://www.homeserve.co.uk/about/homeserve-media-centre/oabs); no method given): 18% of UK households (5.1 million) have a boiler over 10 years old, and 1.3 million have one over 20 years old.
  - This conflicts sharply with the Which? sample shares above, so treat both with caution.
- **English Housing Survey 2023** ([headline report](https://doc.ukdataservice.ac.uk/doc/9441/mrdoc/pdf/9441_2023-24_ehs_headline_report_on_housing_quality_and_energy_efficiency.pdf)): condensing combination boilers are in 55% of homes, up from 28% in 2001. Condensing boilers have been effectively mandatory since 2005, which gives a rough age proxy [unverified].
- **Still missing:** a lifetime distribution, for example a survival curve.

---

## Gap 10: Savings from power flushing, magnetic filters and inhibitor

**Status: STILL OPEN.** Searches returned only manufacturer and retailer pages, and no independent field study. Candidates to look for next [unverified]: the Energy Saving Trust condensing-boiler in-situ field trial (around 2009) and any BRE or BEIS evidence behind the Boiler Plus (2018) requirement to clean the system and fit a filter.

---

**Things worth recording for the project:**
- The 2026 TDCVs and the full revision history in gap 7.
- The radio teleswitch switch-off finished on 30 June 2026.
- Zero VAT on GB domestic electricity runs from 1 Oct 2026 to 31 Mar 2027 under SI 2026/987, with gas staying at 5%.
## Done

Actioned on 25 Oct as amendments to existing pages, not a new page. A1 and A2: the price cap page carries the dated TDCV history and zero VAT on domestic electricity from 1 Oct 2026 to 31 Mar 2027 (SI 2026/987, HMRC Brief 10 (2026)), and its route note is corrected. A3: the metering page carries the radio teleswitch switch-off. A4: the house page carries ECO1 in-use factors. A5: `docs/market_research/ons_consumption_profiles.md` carries the TDCV history. The CalTRACK, ASHRAE G14 and IPMVP material went to the proving-savings page. Counts: 10 confirmed, 0 corrected, 5 open. A6, a dated VAT exception in the regulation commons, is drafted and held back, as are the code constants that read an undated TDCV or VAT. Both are listed in `docs/staging/SEAT_FINDING_THE_WORLD_READS_STATIC_ASSET_FIGURES_WHERE_THE_25_OCT_PACKS_GIVE_DISTRIBUTIONS_AND_DATED_RULES_2026-10-25.md`.
