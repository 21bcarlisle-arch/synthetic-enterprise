# Director evidence: evs charging and savings vs petrol and diesel

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 05:37 GMT: "Also should we do more research on key future topics? How do gas boilers work and how do choices in the sim appear and gas usage and choices for customer and advice that the supplier can offer? E..g condensing or not? Thermostat. Timer and schedule. Flow rate. Radiator modernity and maintenance. . The same for EV purchase. Home charge versus venue. Cost and carbon savings versus petrol and diesel for different mileages. Then the actual charging and usage patterns that occur, based on logic that the SIM knows about the premise and person but the supplier has to figure out or ask about. Then the same for pv and battery. How old, what orientation, what settings. How much would the unit cost and save the customer. Then proving if it did or didn't. Sharing the savings clearly for the customer to enjoy. All these subjects are quite complicated and need knowledge. There may be others too we need for our roadmap??"

This is one of six cited evidence packs researched in the advisor's chat, outside your serial gate. They land in one commit with a cover steer: DIRECTOR_STEER_THE_ADVICE_ROADMAP_NEEDS_ITS_KNOWLEDGE_FIRST_2026-10-25.md. Read the cover steer first. It sets the order of work.

## What to do with it

- Turn this pack into a published Knowledge page, register its concepts, and take its headline bands as candidate world claims.
- Its "world needs to model" list is the hidden-attribute spec for the world, and the observe / infer / ask table is the wall spec for the supplier. The cover steer says when each is built.
- [derived] figures can be re-run. [unverified] figures are not claims until sourced. Named gaps are research tasks, and the research budget ran out on several of them. Close a gap, or record that nothing is published.
- This is drafting work, so it must not displace the serial queue.

---

# Evidence pack: EVs at home in GB (purchase, charging, savings vs petrol and diesel)

*For the Poesys knowledge layer. Compiled 25 Oct 2026. Every figure has its source URL beside it. [derived] means my own arithmetic. [unverified] means from memory and not confirmed by a page I fetched. The shared web-search budget ran out before I could cover some topics. Those are listed in Named gaps.*

---

## 1. Uptake

**New-car share, GB/UK (SMMT figures via the outlets cited)**

| Year | BEV share | PHEV share | Plug-in total | Source |
|---|---|---|---|---|
| 2016 | n/a | n/a | ~36,800 units [derived from "+28%" in 2017] | https://www.zapmap.com/news/electric-cars-take-record-market-share-in-december |
| 2017 | ~0.6% [derived: 29% of plug-ins] | ~1.3% [derived: 71% of plug-ins] | 47,164 units, 1.9% | same |
| 2018 | 0.7% | 1.9% | ~60,000 units | https://www.zapmap.com/news/ev-registrations-set-new-records-in-2019 |
| 2019 | 1.7% | 1.5% | 72,770 units, 3.2% | same |
| 2020 | 6.6% (108,205) | 4.1% (66,877) | 10.7% | https://insideevs.com/news/464853/uk-plugin-electric-car-sales-december-2020/ |
| 2021 | 11.6% (190,727) | 7.0% (114,554) | 18.5% | https://www.greencarguide.co.uk/2022/01/evs-were-25-5-of-new-registrations-in-december-2021/ |
| 2022 | 16.6% (267,203) | ~6.3% [unverified] | – | https://www.zapmap.com/ev-market-statistics/ |
| 2023 | 16.5% (314,687) | ~7.4% | ~23.9% [derived] | https://www.smmt.co.uk/new-car-market-delivers-best-year-since-2019-as-fleets-fuel-growth/ |
| 2024 | 19.6% (381,970) | 8.6% [derived] | 28.2% | https://www.zapmap.com/ev-market-statistics/ |
| 2025 | 23.4% (473,348 of 2,020,520) | 11.1% [derived] | 34.5% | https://www.theevnetwork.com/news/uk-new-car-market-breaches-two-million-as-almost-one-in-four-buyers-go-electric/ ; https://www.zapmap.com/ev-market-statistics/ |
| 2026 (Jan–Sep) | 26.2% (454,947) | – | – | https://www.zapmap.com/ev-market-statistics/ |

**Cars on the road**
- End 2022: 1,113,439 plug-in cars (3.4% of the car parc), of which 664,148 BEV. https://www.zapmap.com/ev-market-statistics/
- DfT, Q3 2025: 1,630,000 licensed zero-emission cars, 4.7% of 34,486,000 licensed cars. Zero-emission cars were 22.7% of new registrations that quarter. https://www.gov.uk/government/statistics/vehicle-licensing-statistics-july-to-september-2025/vehicle-licensing-statistics-united-kingdom-july-to-september-2025--2
- End 2025: 1,834,150 BEVs (+35% year on year), https://www.zapmap.com/sites/default/files/2026-01/Zapmap%20statistics%20EOY%202025%20vF.docx.pdf. Plug-in total 2,817,073 (8.2% of the parc), https://www.zapmap.com/ev-market-statistics/
- End Sep 2026: 3,516,791 plug-in cars, of which over 2.28M BEV (6.6%) and over 1.2M PHEV. https://www.zapmap.com/ev-market-statistics/

**ZEV mandate (car targets)**
- 22% (2024), 28% (2025), 33% (2026), 38% (2027), 52% (2028), 66% (2029), 80% (2030), heading to 100% by 2035. Banking, borrowing and trading of credits are allowed. https://motorway.co.uk/sell-my-car/guides/zev-mandate
- April 2025 changes: the car fine falls from £15,000 to £12,000 per car, hybrids can be sold until 2035, and more flexibility to shift volumes between years. https://www.zemo.org.uk/news-events/news,government-announces-changes-to-zev-mandate_4730.htm
- The 2025 BEV share (23.4%) was below the 28% headline. December 2025 (32.2%) was the only month above it. https://www.theevnetwork.com/news/uk-new-car-market-breaches-two-million-as-almost-one-in-four-buyers-go-electric/

**Parking and home charging access**
- DfT/Ipsos EV Driver Tracker (more than 1,000 drivers):
  - 91% of BEV and 88% of PHEV drivers can charge at home.
  - 90% of BEV drivers have off-street parking (85% via a private driveway or garage).
  - 76% of BEV drivers have a dedicated wallbox, and 74% have a smart charger.
  - 49% are on a bespoke EV tariff.
  - 9% of BEV drivers rely entirely on public charging.
  - https://www.fleetnews.co.uk/news/ev-charging-behaviours-and-experiences-revealed-in-dft-study ; https://forecourttrader.co.uk/news/government-study-finds-90-of-ev-drivers-can-charge-at-home/709930.article
- About 80% of EV drivers charge at home, from around 1.3M home chargers. 51% use the public network at least monthly. https://www.zapmap.com/sites/default/files/2026-01/Zapmap%20statistics%20EOY%202025%20vF.docx.pdf
- All households, not just EV owners: 65.1% of UK homes have off-street parking (7% in Westminster to 84% in Flintshire), https://forecourttrader.co.uk/news/government-study-finds-90-of-ev-drivers-can-charge-at-home/709930.article. Auto Trader puts it at about 60%, and 70% for households earning under £40k, https://plc.autotrader.co.uk/media/z2vh3hnp/ndlb-report-2026-3.pdf. More than 9 million GB households cannot park off-street. https://www.zapmap.com/news/ev-drivers-off-street-parking-research

**Who buys**
- DfT EV driver survey, 2021 (n=848, unweighted):
  - 76% male; 45% aged 55+.
  - Detached 47%, semi-detached 27%, terraced 11%, flats about 14%.
  - 21% earn £83k or more.
  - London 19% of respondents.
  - https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1078871/dft-ev-driver-survey-summary-report.pdf
- Ipsos tracker: 40% of BEVs came through salary sacrifice (57% for drivers aged 17–34). 54% say their EV is a secondary vehicle. Home-charging access is 98% rural vs 89% urban, and 97% Midlands vs 86% South. https://forecourttrader.co.uk/news/government-study-finds-90-of-ev-drivers-can-charge-at-home/709930.article
- Would consider an EV for their next car: 48% of households under £40k, 73% over £40k, 84% over £80k. https://www.am-online.com/news/wealth-divide-risks-excluding-lower-income-buyers-from-ev-market

## 2. Vehicle energy use and mileage

- **Efficiency in winter (What Car? test, cars left outside 15 hours, cabin set to 21°C):**
  - Range of results: 2.6 mi/kWh (Audi Q4) to 3.7 mi/kWh (Tesla Model 3 LR).
  - Cars with heat pumps averaged 3.2 mi/kWh; cars without averaged 2.9.
  - Range fell 15–20% below the summer test.
  - Range fell short of the official figure by 25.4% with a heat pump and 33.6% without.
  - https://www.moveelectric.com/e-cars/revealed-how-winter-weather-affects-real-world-range
- **Planning assumptions used by others:**
  - Selectra: UK average about 3.5 mi/kWh, plus about 10% charging losses. https://selectra.co.uk/energy/guides/environment/electric-car-charging-cost
  - Octopus: 0.306 kWh/mile. https://octopus.energy/power-pack
- **Segment split:** no fetched source gives a full split by segment. As a rough guide, small cars run at about 4 mi/kWh and large SUVs at about 2.5 mi/kWh [unverified].
- **Annual mileage:**
  - Cars under three years old, from MOT data, 2024: BEV 10,054, PHEV 9,367, diesel 10,728, petrol 7,585 miles. Zero-emission cars were 3.8% of the fleet but did 5.3% of car miles. https://www.racfoundation.org/?p=5342
  - NTS 2024, car-driver miles per person: women 4,314, men 4,940. Peak age band is 50–59 (men 6,712). https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips
  - The NTS per-car mileage table (NTS0901) and mileage-band distribution (NTS0904) exist, https://www.gov.uk/government/statistical-data-sets/nts09-vehicle-mileage-and-occupancy, but I did not extract their values. The "about 7,000 miles per car" figure is [unverified].
- **Annual home kWh:**
  - 7,000 mi at 3.5 mi/kWh is about 2,000 kWh. https://selectra.co.uk/energy/guides/environment/electric-car-charging-cost
  - Kaluza/OVO models 1,750 kWh a year. https://www.kaluza.com/blog/charging-forward-with-the-uks-smartest-ev-add-on
  - Octopus: 7,500 mi × 0.306 is about 2,300 kWh. https://octopus.energy/power-pack
  - At 10,000 mi and 0.33 kWh/mi at the meter: about 3,300 kWh [derived].
- **Share of household electricity:** compared with a typical 2,700 kWh/yr (the Ofgem TDCV figure) [unverified], an EV adds 65–120% to household electricity use [derived].

## 3. Where charging happens and what it costs

- **Prices (Zapmap Price Index, Sep 2026, weighted PAYG):**
  - Public slow/fast (3–49 kW): 54p/kWh.
  - Rapid/ultra-rapid (50 kW+): 79p/kWh.
  - Home standard: about 26p/kWh.
  - Home EV off-peak: about 8.9p/kWh.
  - Zapmap notes that subscriptions and promotions mean drivers often pay less than PAYG.
  - https://www.zapmap.com/ev-stats/charging-price-index
- **Price cap, Oct–Dec 2026:**
  - Electricity unit rate 26.32p/kWh, standing charge 54.83p/day (direct debit, GB average).
  - Ofgem's page states that VAT has been removed from domestic electricity bills from 1 Oct 2026 to 31 Mar 2027.
  - https://www.ofgem.gov.uk/publications/changes-energy-price-cap-between-1-october-and-31-december-2026
  - The usual 5% domestic vs 20% public VAT gap is [unverified] in this pack. The world model should treat VAT as a time-varying parameter.
- **Pence per mile, AA (Mar 2025 data):** home 5.65p, public slow 11.30p, rapid 16.72p, ultra-rapid 17.63p, petrol 11.86p. https://evfleetworld.co.uk/?p=60069
- **Usage frequency:**
  - Weekly hub use: 32% of BEV drivers. Weekly workplace charging: 27%. https://www.fleetnews.co.uk/news/ev-charging-behaviours-and-experiences-revealed-in-dft-study
  - Fully public-reliant BEV drivers mostly use 22–49 kW chargers (42%) or 50 kW+ (23%). Same source.
- **Network:**
  - End 2025: 87,796 public devices. 17,935 rapid or ultra-rapid. 33,177 on-street.
  - Nearly 4M successful sessions a month.
  - https://www.zapmap.com/sites/default/files/2026-01/Zapmap%20statistics%20EOY%202025%20vF.docx.pdf
- **Share of energy by location:** no fetched source gives this. Indicative figures of 70–80% at home [unverified] are consistent with "about 80% charge at home" (Zapmap, above).

## 4. Charging patterns

- **Electric Nation** (WPD, about 700 drivers, more than 1M charge records, 7 kW BEV / 3.6 kW PHEV):
  - Plug-in peak is 5–7pm on weekdays.
  - Cars stay plugged in for about 12 hours but draw power for about 1.5 hours (average charge 90 minutes).
  - BEV drivers plug in 2–3 times a week. Only 14% charge at home daily.
  - BEVs usually start a charge with 55–70% state of charge.
  - PHEVs charge more often, for shorter periods.
  - https://discoverev.co.uk/ev-news/electric-nation-trial-shows-uksetwork-can-cope-with-extra-load-evs-will-create ; https://www.drive-electric.co.uk/news/smart-charging-insights-electric-nation-trial/
- **Implied session energy:** 1.5 h × 7 kW is about 10.5 kWh [derived]. Octopus: more than 80% of sessions take under 6 hours, i.e. under about 42 kWh at 7 kW [derived]. https://octopus.energy/blog/intelligent-octopus-go-smarter-charging-for-a-greener-grid/
- **DfT diary (2 weeks):** about 4 home charges and 1.8 public charges per BEV driver. Charging to 70% is the most common habit (73%). 86% of BEV drivers charge overnight at least 1–2 times a week. https://www.fleetnews.co.uk/news/ev-charging-behaviours-and-experiences-revealed-in-dft-study
- **2021 survey:** 18% charge overnight every day; 78% at least weekly. 76% of smart-charger owners use the smart functions always or mostly. https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1078871/dft-ev-driver-survey-summary-report.pdf
- **Under smart control:** 97.5% of OVO Charge Anytime charging was smart-scheduled, and 0.33 GWh was shifted away from peak in the first months. https://www.kaluza.com/blog/charging-forward-with-the-uks-smartest-ev-add-on
- **Electric Nation on ToU:** ToU incentives were "highly effective" at moving load out of the evening peak, but no effect size was published. https://www.drive-electric.co.uk/news/smart-charging-insights-electric-nation-trial/
- **Regulation (Smart Charge Points Regulations 2021):**
  - New chargers must ship with default charging hours outside peak, defined as weekdays 08:00–11:00 and 16:00–22:00.
  - Each charge gets a random delay of up to 600 s. The charger must be able to delay up to 1,800 s, and that maximum can be changed remotely.
  - Chargers must be capable of demand-side response, with an owner override.
  - https://legislation.gov.uk/uksi/2021/1467/part/2/made?view=plain
- **Street-level diversity:** no fetched ADMD figure (see gaps). The roughly 8:1 ratio of plug-in time to charging time in Electric Nation is the main source of flexibility [derived].

## 5. Cost and carbon inputs

- **Fuel prices:**
  - Week ending 27 Sep 2026: petrol E10 173.8p/l, diesel B7 198.9p/l (Fuel Finder open data, each station weighted equally). https://www.fuel-finder.uk/fuel-price-pulse/weekly/2026-09-27/
  - Earlier 2026 assumption for comparison: petrol £1.34/l and 45 mpg. https://selectra.co.uk/energy/guides/environment/electric-car-charging-cost
  - Prices are volatile, so the worked table shows a sensitivity line.
- **Diesel economy:** 55 mpg [unverified].
- **Carbon factors (DESNZ 2026, published June 2026):**
  - Grid electricity, location-based: 0.13096 kgCO2e/kWh. Transmission and distribution losses: 0.01299.
  - Petrol: 2.075 kgCO2e/l. Diesel: 2.58354 kgCO2e/l (average biofuel blend).
  - https://greencalculus.com/data/defra-emission-factors/
  - The electricity factor fell about 26% from 2025, partly because of a method change. https://circularecology.com/news/desnz-2026-uk-ghg-conversion-factors
  - The 2026 factor reflects more recent generation data (one-year lag, previously two). https://www.theema.org.uk/new-defra-desnz-2026-greenhouse-gas-conversion-factors-released/
- **Marginal factor:** gas CCGT is about 0.35–0.40 kgCO2/kWh [unverified]. Overnight average intensity is typically below the daily average [unverified].
- **Lifecycle (ICCT, EU, 2025 medium cars):**
  - BEV 63 gCO2e/km vs petrol 235 (73% lower). HEV 188. PHEV 163.
  - BEV production emissions are about 40% higher than a petrol car's, paid back after about 17,000 km.
  - https://theicct.org/publication/electric-cars-life-cycle-analysis-emissions-europe-jul25/
- **Purchase and tax:**
  - Electric Car Grant: up to £3,750 (Band 1) or £1,500 (Band 2) on cars at or below £37,000. Runs 15 Jul 2025 – 31 Mar 2030, £2bn budget. The dealer applies it. https://find-government-grants.service.gov.uk/grants/electric-car-grant-1
  - VED from April 2025: £10 first year, then £195 a year. Expensive car supplement for EVs: £620/yr for five years, with the EV threshold raised to £50k from 1 Apr 2026. https://www.electrifying.com/blog/article/uk-ev-road-tax-changes-2025-everything-you-need-to-know
  - eVED (pay-per-mile) from 1 Apr 2028: 3p/mile for BEV, still subject to consultation. https://www.vehicle-certification-agency.gov.uk/fuel-consumption-co2/fuel-consumption-guide/electric-vehicle-excise-duty-eved. PHEV rate quoted as 1.5p/mile. https://www.electrifying.com/blog/article/uk-ev-road-tax-changes-2025-everything-you-need-to-know
- **Used market (Auto Trader, 2025):**
  - Only 5% of used EV stock is priced at or under £10k, vs about 35% of used petrol stock.
  - The average 5–10-year-old EV costs £14,654.
  - About 60% of households earning under £40k budget £10k or less for a car.
  - Running-cost saving of "up to £1,500/yr" with home charging (attributed to DfT 2025).
  - https://plc.autotrader.co.uk/media/z2vh3hnp/ndlb-report-2026-3.pdf
- **Servicing, insurance and depreciation:** not fetched (see gaps).

## 6. What the supplier can see or infer

- **Signature:** a block of roughly 7 kW (BEV) or 3.6 kW (PHEV) lasting about 1.5 hours, 2–3 times a week (Electric Nation, above). On a smart tariff it moves into the 23:30–05:30 window or into supplier-dispatched slots. A 30-minute meter read averages the power within each half hour, so partial half-hours look smaller.
- **Detection accuracy:**
  - NZ (Vector/Otago), half-hourly data, XGBoost on about 150 features:
    - With one year of data: precision 0.87, recall 0.81 for all chargers; 0.91 and 0.96 for fast chargers.
    - With one month: 0.55 and 0.62.
    - https://www.otago.ac.nz/__data/assets/pdf_file/0028/330985/detection-of-electric-vehicles-at-household-level-from-half-hourly-smart-meter-data-0237729.pdf
  - Norway (SINTEF), hourly data: 90% of EVs detected at a 10% false-positive rate, or 75% at 35%. Models "may be confused by baseline consumption patterns". https://sintef.brage.unit.no/sintef-xmlui/handle/11250/2618624
  - Bidgely, 15-minute data, at least 180 days of history: Level-2 charger precision 75%, recall 88%. Precision rises above 95% when survey answers are added. Water heaters (3–7 kW) and HVAC (3–6 kW) overlap the EV signature. https://go.bidgely.com/rs/492-VKN-623/images/EV-Intelligence-Info-Sheet.pdf?version=0
- **GB confounders:** immersion heaters (about 3 kW), storage heaters (overnight Economy 7 blocks), heat pumps in winter, electric showers (short, 8–10 kW), and home batteries charging overnight [unverified as GB-specific evidence]. Granny-lead charging at 2.3 kW looks like an immersion heater [derived].
- **Consented data:** car and charger APIs. Intelligent Octopus Go integrates with more than 280 car models and selected chargers, and prefers the car connection when both are available, https://octopus.energy/intelligent-go-faqs/. These APIs provide state of charge, the ready-by time and session kWh. The smart-charge regulations require chargers to be able to provide demand-side response. https://legislation.gov.uk/uksi/2021/1467/part/2/made?view=plain

## 7. Advice and products

- **Intelligent Octopus Go:**
  - Off-peak 23:30–05:30 for the whole home, plus dispatched slots outside that window.
  - From 2026 there is a cap of 6 hours a day at off-peak price, measured midday to midday. Time beyond 6 hours is billed at peak.
  - Needs a half-hourly smart meter and a compatible car or charger.
  - Customers cannot use other flexibility services while on it.
  - https://octopus.energy/blog/intelligent-octopus-go-smarter-charging-for-a-greener-grid/ ; https://octopus.energy/intelligent-go-faqs/
  - Rate quoted as 7–8p/kWh (the page is inconsistent). https://www.energyplus.co.uk/octopus-ev-tariff
- **Other tariffs:** E.ON Next Drive 8.5p, British Gas EV Power about 9p. https://www.energyplus.co.uk/octopus-ev-tariff. EDF EV tariff: not captured (gap).
- **OVO Charge Anytime:**
  - Covers EV charging only, at 13.33p/kWh, scheduled by Kaluza. The rest of the home stays on the normal tariff.
  - Bundles from £26.50/month (about 700 mi/month) or pay as you go.
  - https://www.bestchargers.co.uk/ev-tariffs/ovo-charge-anytime/
  - Realised savings early on: £66 per customer over about 2.5 months, £5.85 per session. https://www.kaluza.com/blog/charging-forward-with-the-uks-smartest-ev-add-on
- **Saving vs a flat tariff:**
  - About 2,000 kWh: £490 at the cap vs £140 at 7p, a saving of about £350/yr. https://selectra.co.uk/energy/guides/environment/electric-car-charging-cost
  - At the Oct 2026 cap: 2,640 kWh × (26.32 − 7)p is about £510/yr [derived].
- **V2G, Octopus Power Pack:**
  - EV charging is credited back (effectively free) up to 210 kWh a month.
  - Conditions: plugged in at least 12 hours a day on 20 days a month, minimum state of charge below 30%, BYD Dolphin with a Zaptec Pro only, and G99 export approval (10–45 working days).
  - Claimed saving: £620/yr vs Flexible Octopus and £161/yr vs Intelligent Octopus Go, at 7,500 mi.
  - https://octopus.energy/power-pack
- **Charger install:**
  - Installation about £500–1,000, plus a similar amount for the unit. Example: £1,249 installed. Three-phase upgrades cost £3,000 to over £15,000. https://carwow.co.uk/guides/buying/electric-car-charger-installation-cost
  - OZEV grant for renters and flat owners: 75% of the cost, up to £500, until 31 Mar 2027. Homeowners in houses are not eligible. https://www.find-government-grants.service.gov.uk/grants/electric-vehicle-chargepoint-grant-for-renters-and-flat-owners-1. Carwow says £350; the gov.uk page wins.
  - A separate on-street parking grant exists. https://www.find-government-grants.service.gov.uk/grants/electric-vehicle-chargepoint-grant-for-households-with-on-street-parking-1 (not fetched, details [unverified]).
- **System flexibility (NESO FES 2025):**
  - Smart charging: 10 GW of flexibility in Holistic Transition (down from 16 GW in FES 2024 because larger batteries mean fewer sessions).
  - V2G: 41 GW in 2050; about 1.2 GW by 2030.
  - 31–36M EVs by 2050.
  - https://www.evinfrastructurenews.com/ev-technology/neso-s-future-energy-scenarios-ev-uptake-most-credible-way-to-reduce-emissions-in-the-short-term ; https://www.r-e-a.net/wp-content/uploads/2025/08/NESO-FES-2025-REA-Analysis-Final.pdf

## 8. Proving savings

- **Fuel counterfactual:** EV miles × (petrol or diesel p/mile from the customer's previous car's mpg and the weekly Fuel Finder price) minus the actual cost of charging. Requires mileage (ask, or infer from kWh ÷ efficiency) and the previous car.
- **Tariff counterfactual:** metered EV kWh × the flat rate (the cap) minus the actual charging cost. This only needs the EV load separated out: either a sub-meter or API session data, or a disaggregation estimate.
- **Pitfalls:**
  1. *Inflated baselines.* OVO compared against 30p and 34p/kWh in different footnotes. https://www.kaluza.com/blog/charging-forward-with-the-uks-smartest-ev-add-on. Its 2023 release claimed an average saving of "£129/month" against a modelled 1,750 kWh/yr, which caps the possible saving at about £350/yr. https://www.kaluza.com/press-releases/ovo-saves-customers-over-1-million-in-just-six-months-through-smart-ev-charging. The two do not reconcile [derived].
  2. *Whole-home tariffs.* Intelligent Octopus Go also discounts other overnight load, so the "EV saving" absorbs shifted immersion or battery load.
  3. *Public charging is invisible.* About 51% use public chargers monthly. Ignoring that energy overstates the home share and understates cost.
  4. *Selection bias.* Early EV-tariff customers are high-mileage, have driveways and are tech-engaged.
  5. *Rebound.* A cheaper fuel cost can increase mileage.
  6. *Average vs marginal carbon factor.* The two differ by a factor of 2.5 or more (see table d).
  7. *Moving prices.* VAT, the cap and fuel prices all change, and the 2028 eVED will reduce fuel savings by 3p/mile.

---

## (a) Headline figures and bands to check a simulated world against

| Metric | Band | Source |
|---|---|---|
| BEV share of new cars, 2025 / 2026 YTD | 23.4% / 26.2% | Zapmap market stats |
| Plug-in share of the car parc, end 2025 | 8.2% (BEV about 5.3% [derived]) | Zapmap |
| EV drivers able to charge at home | 88–93% | DfT tracker; DfT 2021 |
| EV drivers fully reliant on public charging | about 9% of BEV drivers | DfT tracker |
| Annual BEV mileage (cars under 3 years) | about 10,000 (petrol about 7,600) | RAC Foundation |
| Efficiency at the meter | 0.28–0.38 kWh/mi; winter 15–20% worse | What Car?/Move Electric; Selectra |
| Home charging kWh/yr | 1,750–3,500 (central about 2,300) | Kaluza; Octopus; [derived] |
| Plug-ins per week (BEV) | 2–3; only about 14–18% daily | Electric Nation; DfT 2021 |
| Session energy | about 10 kWh mean; more than 80% under 6 h | Electric Nation [derived]; Octopus |
| Hours plugged in vs hours charging | about 12 h vs about 1.5 h | Electric Nation |
| Unmanaged plug-in peak | 17:00–19:00 on weekdays | Electric Nation |
| Share smart-scheduled on a smart EV tariff | about 97% | Kaluza |
| Share of energy charged at home | 70–80% [unverified] | gap |
| Saving from smart tariff vs flat | £350–510/yr at about 2,000–2,640 kWh | Selectra; [derived] |
| Detection precision/recall, 1 yr of half-hourly data | 0.87/0.81 (fast chargers 0.91/0.96) | Otago/Vector |

## (b) What the world needs to model (hidden attributes)

**Per person**
- Owns or leases an EV (BEV or PHEV) and when they got it.
- Salary sacrifice or company car.
- Annual mileage and its distribution (commute, leisure, long trips about monthly).
- Plug-in habit: frequency, arrival-time distribution, state-of-charge threshold for plugging in, target charge (usually 70%).
- Whether they override or boost charges.
- Price sensitivity and tech engagement.
- Use of public, workplace and rapid chargers (share of energy, price paid).
- Previous or alternative car's fuel type and mpg.
- Intent to buy, budget (new or used), income band.

**Per vehicle**
- Model, usable battery kWh, efficiency curve vs temperature, heat pump yes or no.
- Maximum AC charge rate (3.6, 7 or 11 kW).
- V2G capability.
- API availability.

**Per home**
- Off-street parking (driveway, garage, communal, none).
- Charger: none, granny lead, untimed, timed, or smart (and brand).
- Single or three-phase supply.
- Tenure (owner vs renter or flat, for grant eligibility and permission).
- House type, region, urban or rural.
- Competing large loads: immersion, storage heaters, heat pump, battery, solar.
- Feeder or substation headroom.

**Exogenous**
- Weekly fuel prices.
- Cap rates and VAT regime.
- Public PAYG prices.
- Grid average and marginal intensity by half hour.
- VED and eVED.
- Grants (ECG, OZEV).

## (c) What the supplier can observe, infer or must ask

| Item | Observe | Infer | Must ask or get via consent |
|---|---|---|---|
| EV presence | – | Yes, from half-hourly blocks; needs 6–12 months of data for good accuracy | Confirm at signup or tariff switch |
| Home charging kWh and timing | Yes, if on a smart tariff with an API | Approximate, by disaggregation | – |
| Charger power and type | – | Partly, from the block height | Charger make (smart or not) |
| Car model, battery, efficiency | – | – | Ask, or car API |
| Annual mileage | – | Home kWh ÷ efficiency (a lower bound) | Ask; MOT mileage [unverified as supplier-accessible] |
| Public or workplace charging share | – | No | Ask; app or roaming data if bundled |
| Parking and tenure | – | Weak signals from address or EPC | Ask |
| Previous car and mpg (for the counterfactual) | – | – | Ask |
| Plug-in behaviour | API | Partial (only charging is seen, not idle plug-in time) | – |
| Confounding loads (immersion, heat pump, storage) | – | Partly | Ask |
| Willingness to be smart-controlled | Tariff choice, overrides | – | Consent |

## (d) Worked cost and carbon table [derived]

**Assumptions**
- EV uses 0.30 kWh/mi at the battery. Home charging adds 10% losses, giving 0.33 kWh/mi at the meter (Selectra; Move Electric). Public charging is billed at 0.30.
- Prices:
  - Home standard: 26.32p (Ofgem, Oct 2026, VAT 0%).
  - Intelligent Octopus Go: 7p (EnergyPlus).
  - Public rapid: 79p (Zapmap).
  - Mixed case: 85% of energy at home off-peak, 15% rapid (a modelling assumption).
- Petrol: 173.8p/l at 45 mpg, i.e. 9.90 mi/l (Fuel Finder; Selectra).
- Diesel: 198.9p/l at 55 mpg [unverified], i.e. 12.10 mi/l.
- Carbon:
  - Grid average 0.144 kg/kWh including losses (DESNZ 2026).
  - Marginal 0.37 [unverified].
  - Petrol 2.075 kg/l and diesel 2.584 kg/l (tailpipe plus biofuel blend, DESNZ 2026).

**Per-mile costs and carbon**

| | Home standard | Intelligent Octopus Go | Mixed (85/15) | Rapid only | Petrol | Diesel |
|---|---|---|---|---|---|---|
| p/mile | 8.7 | 2.3 | 5.5 | 23.7 | 17.6 (13.5 at 134p/l) | 16.4 |
| kgCO2e/mile | 0.048 average / 0.122 marginal | same | same | same | 0.210 | 0.214 |

**Annual fuel cost (£) and carbon (kg) by mileage**

| Miles/yr | Home kWh | EV home std £ | IOG £ | Mixed £ | Rapid £ | Petrol £ | Diesel £ | EV kg (average / marginal) | Petrol kg | Diesel kg |
|---|---|---|---|---|---|---|---|---|---|---|
| 4,000 | 1,320 | 347 | 92 | 221 | 948 | 702 | 658 | 190 / 488 | 838 | 854 |
| 8,000 | 2,640 | 695 | 185 | 442 | 1,896 | 1,405 | 1,315 | 380 / 977 | 1,677 | 1,709 |
| 12,000 | 3,960 | 1,042 | 277 | 662 | 2,844 | 2,107 | 1,973 | 570 / 1,465 | 2,515 | 2,563 |
| 20,000 | 6,600 | 1,737 | 462 | 1,104 | 4,740 | 3,512 | 3,288 | 950 / 2,442 | 4,192 | 4,272 |

**Notes**
- From April 2028, eVED adds £120, £240, £360 and £600 a year at these four mileages [derived from 3p/mi].
- VED is £195/yr for both EVs and petrol cars after year one, apart from CO2-band differences for petrol and diesel [unverified].
- The standing charge is unchanged on any tariff, so it is excluded.
- A public-only (rapid) EV driver pays more than a petrol driver at September 2026 prices.

## (e) Named gaps

1. **Share of charging energy by location.** No primary source was fetched for home, work, public and rapid kWh shares. Candidates: Element Energy, ChargeUK, Field Dynamics.
2. **NTS per-car mileage.** NTS0901/0904 values (mean, and the band distribution for distance driven) were not extracted. The 7,000-mile figure is [unverified].
3. **Street-level diversity and ADMD.** Electric Nation and DNO ADMD values for EVs, managed vs unmanaged, were not obtained.
4. **Effect size of ToU vs flat.** Off-peak share without automation (timer-only ToU) is not quantified. Octopus Intelligent Go customer numbers and off-peak share are not published on the pages fetched.
5. **GB disaggregation evidence.** All detection accuracy figures are from NZ, Norway and Bidgely (US). There is no GB half-hourly study, and none tests heat-pump or storage-heater confounding.
6. **Total cost of ownership.** Servicing, insurance, depreciation curves and Which? or EST total-cost comparisons were not fetched.
7. **Carbon factors.** Marginal and time-of-day grid factors (NESO Carbon Intensity API) are [unverified]. The DESNZ 2025 values were not captured for the year-on-year comparison.
8. **Tariffs and VAT.** EDF's EV tariff was not captured, and the IOG rate (7p vs 8p) conflicts between sources. The VAT holiday on domestic electricity (Oct 2026–Mar 2027, per Ofgem) and the public-charging VAT rate need confirming.
9. **Market and vehicle data.** 2016 and 2022 PHEV shares need SMMT originals. Diesel mpg and kWh/mile by segment are [unverified]. The OZEV on-street grant was not fetched. Fuel prices conflict across 2026 sources (134p vs 174p/l), so treat them as a scenario input.
10. **Searches stopped early.** The shared web-search limit ran out, so gaps 1, 2 and 6 and the TDCV figure were left open. A follow-up message can resume.

**For memory (suggested):** the Poesys EV evidence pack is complete, with open gaps in the energy-share-by-location data, GB-specific disaggregation evidence, and total cost of ownership.