# Director evidence: heat pumps and fabric measures

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

# Evidence pack: heat pumps and fabric measures in GB homes

**What this covers:** performance, cost, savings, and what a supplier can know. Written for the Poesys world and supplier knowledge layer.
**Compiled:** 2026-10-25.
**Labels:** **[derived]** marks my own arithmetic. **[unverified]** marks anything from memory that I did not confirm against a fetched source in this session.
**Search limit:** the web-search budget for this session ran out partway through. Some fabric-cost, tariff and literature points are therefore [unverified]; section (e) lists them.

---

## 1. Heat pump stock and uptake

**Installs per year.** The three series below count different things, so pick one and don't mix them.

| Year | Figure | What it counts | Source |
|---|---|---|---|
| 2020 | 11,196 | DESNZ retrofit, hydronic ≤45 kW | [Renewable Energy Magazine on DESNZ Dec 2025 stats](https://www.renewableenergymagazine.com/miscellaneous/uk-heat-pump-deployment-statistics-for-2025-20260312) |
| 2022 | >30,000 (≈19% of 163,341 MCS installs) | MCS-certified | [Solar Power Portal / MCS](https://www.solarpowerportal.co.uk/solar-installations/mcs-announces-2022-as-record-year-for-certified-heat-pump-installations) |
| 2023 | 40,426 | MCS-certified | [PHPI / MCS](https://phpionline.co.uk/news/2024-becomes-best-year-on-record-for-uk-certified-heat-pump-installations/) |
| 2023 / 2024 | 55,000 / 84,000 | Basis not stated; likely includes new build | [CIBSE Journal](https://www.cibsejournal.com/news/warm-homes-plan-cuts-heat-pump-target-by-25/) |
| 2024 | 48,677 | DESNZ retrofit | [REM / DESNZ](https://www.renewableenergymagazine.com/miscellaneous/uk-heat-pump-deployment-statistics-for-2025-20260312) |
| 2025 | 51,886, later revised to 53,265 | DESNZ retrofit | [REM](https://www.renewableenergymagazine.com/miscellaneous/uk-heat-pump-deployment-statistics-for-2025-20260312); [pv magazine Jun 2026](https://www.pv-magazine.com/2026/06/11/uk-heat-pump-installations-stall-despite-subsidy-boost/) |
| 2025 | >60,000 | MCS-certified, all types | [Express & Star / MCS](https://www.expressandstar.com/news/installations-of-solar-panels-heat-pumps-and-batteries-hit-highs-in-2025-5637781) |
| Q1 2026 | 10,693 (−22% on Q1 2025) | DESNZ retrofit | [pv magazine](https://www.pv-magazine.com/2026/06/11/uk-heat-pump-installations-stall-despite-subsidy-boost/) |

- **Cumulative MCS heat pumps:** "nearly 260,000" by October 2024 ([PHPI](https://phpionline.co.uk/news/2024-becomes-best-year-on-record-for-uk-certified-heat-pump-installations/)).
- **Subsidy-backed installs:** 183,294 from January 2018 to September 2025, 43% of them since January 2024 ([pv magazine Dec 2025](https://www.pv-magazine.com/2025/12/15/uk-government-backs-more-than-180000-heat-pump-installations/)).
- **Air-source vs ground-source:** air-source was 99% of 2025 retrofit installs, up from 92% in 2020 ([REM](https://www.renewableenergymagazine.com/miscellaneous/uk-heat-pump-deployment-statistics-for-2025-20260312)). It was 98% of subsidised installs in the year to September 2025, up from 87% ([pv magazine](https://www.pv-magazine.com/2025/12/15/uk-government-backs-more-than-180000-heat-pump-installations/)).

**Boiler Upgrade Scheme (BUS)**
- **Grant levels:**
  - £7,500 for air-source or ground-source, raised in October 2023 ([HEE detailed release Mar 2026](https://assets.publishing.service.gov.uk/media/69ba6cf126909a14239612ed/HEE_Stats_Detailed_Release_March_2026.pdf)).
  - £2,500 for air-to-air and biomass.
  - £9,000 for homes heated by oil or LPG.
  - Hybrids are not eligible ([pv magazine](https://www.pv-magazine.com/2026/06/11/uk-heat-pump-installations-stall-despite-subsidy-boost/)).
- **Scheme Year 4 (April 2025 to March 2026):**
  - 45,880 applications, up 19%.
  - 39,435 vouchers issued.
  - £233.1m paid on 31,104 systems.
  - Cumulative since May 2022: £560.3m on 80,098 systems.
  - Air-source share of payments: 97.6%. Fossil-fuel replacements: 76.3% ([Ofgem BUS SY4](https://www.ofgem.gov.uk/transparency-document/boiler-upgrade-scheme-annual-report-april-2025-march-2026)).
- **Scheme Year 3:**
  - 25,331 grants paid.
  - Cumulative technology shares: air-source 97.0%, ground-source 2.3%, biomass 0.6%.
  - Systems replaced: gas 52.6%, oil 18.1%, direct electric 9.0%.
  - Regions: South East 20.0% and South West 17.9% highest; North East 2.9% lowest ([Ofgem BUS SY3 PDF](https://www.ofgem.gov.uk/sites/default/files/2025-07/BUS_Annual_Report_2024_to_2025.pdf)).
- **Vouchers redeemed and paid:** about 73,100 to end-December 2025 ([HEE Mar 2026](https://assets.publishing.service.gov.uk/media/69ba6cf126909a14239612ed/HEE_Stats_Detailed_Release_March_2026.pdf)).

**Targets**
- **Old target:** 600,000 a year by 2028, from the 2021 Heat and Buildings Strategy.
- **Warm Homes Plan (21 January 2026):** ">450,000 a year by 2030" including new build ([CIBSE Journal](https://www.cibsejournal.com/news/warm-homes-plan-cuts-heat-pump-target-by-25/)).
- **Funding:** BUS gets £2.7bn to 2030 ([MCS Foundation](https://mcsfoundation.org.uk/wp-content/uploads/2026/03/What-the-Warm-Homes-Plan-means-for-home-decarbonisation-The-MCS-Foundation.pdf)). The plan totals £15bn ([Hansard WS 21 Jan 2026](https://hansard.parliament.uk/html/Commons/2026-01-21/WrittenStatements)).
- **Gap to target:** 2025 retrofit ran at about 12% of the 2030 target [derived: 53,265 / 450,000].

## 2. Performance

**Electrification of Heat (EoH) trial, interim results**
- **Sample:** 742 installs, November 2020 to August 2022, with the best 12-month window per home ([UKDS 9050 interim insights](https://doc.ukdataservice.ac.uk/doc/9050/mrdoc/pdf/9050_eoh_Interim_insights_from_heat_pump_performance_data.pdf)).
- **Air-source, n=291:**
  - SPFH2 median 2.94 (IQR 2.66–3.20).
  - SPFH4 median 2.80 (IQR 2.53–3.09).
- **Hybrids, n=58:** SPFH4 2.37 (IQR 2.01–2.81).
- **By refrigerant (SPFH4):** R32 2.94, R290 2.89, R410a 2.66.
- **Flow temperature:** the mean was 38.2 °C. Higher flow temperature goes with lower SPF.
- **By house type:** detached homes score significantly higher than semis. House age has no significant effect.
- **Unexplained spread:** "much of this variation is difficult to explain."
- **Coldest day** (mean −0.4 °C): median COP(H4) 2.44 (IQR 2.20–2.70) (same source). The Catapult summary says 2.44 on days "as low as −6 °C" ([ESC](https://es.catapult.org.uk/news/heat-pumps-shown-to-be-three-times-more-efficient-than-gas-boilers/)).
- **High-temperature units:** performed comparably to low-temperature units. Weather compensation rarely called for high flow temperatures (ESC).
- **Hot water:** the trial did not meter domestic hot water separately.

**RHPP (2013–15), the older baseline** ([DECC RHPP final report](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/606818/DECC_RHPP_161214_Final_Report_v1-13.pdf))

| Boundary / use | Air-source (n≈292) | Ground-source (n≈92) |
|---|---|---|
| SPFH2 median (IQR) | 2.65 (2.33–2.95) | 2.81 (2.63–3.14) |
| SPFH4 median (IQR) | 2.44 (2.15–2.67) | 2.71 (2.48–3.02) |
| Hot water SPFH2 median | **2.31** | 2.71 |
| Space heating SPFH2 median | 2.74 | 2.89 |
| Share with SPFH2 ≥ 2.5 | 62% | 80% |

- **Immersion heaters:** about 12% of electricity on average. More than half of sites with SPFH4 below 2 used the immersion for over 20% of their electricity.
- **Cycling:** many air-source units showed a 10-minute on-to-on cycle, with no clear link to COP.
- **Oversizing:** low load factor from oversizing reduced SPF.
- **Metering error:** heat meters calibrated for water rather than glycol overstate SPF by 4–7%.

**heatpumpmonitor.org (enthusiast, self-selected)**
- **All MID-metered systems** with a full year (November 2024 to November 2025, n=213): SPF 3.83.
- **Air-source on the H4 boundary, no summer cooling** (n=170): SPFH4 3.86 ([OEM docs](https://docs.openenergymonitor.org/heatpumpmonitor/introduction.html)).
- **Published version:** an *Energy and Buildings* paper with Rosenow (169 air-source systems) compares these results with EoH ([OEM forum](https://community.openenergymonitor.org/t/heatpumpmonitor-orgs-first-academic-paper/29509)). I could not fetch the paper itself.

**Industry in-situ study (1,717 installs, 2017–22)**
- 8% of air-source and 33% of ground-source systems reached SPF ≥ 3.5.
- EoH average air-source efficiency was 293%, against 84% for a typical fossil system ([H&V News / HPA](https://www.heatingandventilating.net/improvement-in-heat-pump-performance-highlighted-by-new-electrification-of-heat-demonstration-report)).

**Defrost:** no fetched source quantifies defrost losses [gap]. They show up implicitly in the cold-day COP.

## 3. Running cost and carbon vs a gas boiler

**Prices: Ofgem price cap, 1 October to 31 December 2026, direct debit** ([Ofgem](https://ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026))
- **Electricity:** 26.32 p/kWh, standing charge 54.83 p/day. VAT is 0% from 1 October 2026 to 31 March 2027.
- **Gas:** 7.97 p/kWh, standing charge 29.68 p/day, including 5% VAT.
- **Typical consumption (TDCV):** electricity 2,500 kWh, gas 9,500 kWh ([Ofgem summary PDF](https://www.ofgem.gov.uk/sites/default/files/2026-08/Summary-of-changes-to-energy-price-cap-1-October-to-31-December-2026.pdf)).

**Price ratio and break-even**
- The electricity-to-gas price ratio is **3.30** [derived].
- Against an 84%-efficient boiler, a heat pump breaks even on unit cost at **SPF 2.77** [derived]. When electricity VAT returns at 5%, break-even rises to SPF 2.91 [derived].
- **The EoH median (2.80) sits almost exactly at break-even** on the cap.

**Cosy Octopus (time-of-use tariff)**
- National-average rates from a third-party tracker, VAT basis unclear ([agilebuddy](https://agilebuddy.uk/latest/cosy)):
  - Cheap 14.7p: 04:00–07:00, 13:00–16:00, 22:00–00:00.
  - Standard 30.0p.
  - Peak 45.0p: 16:00–19:00.
  - Standing charge 57.1 p/day.
- These are not confirmed on Octopus's own site [unverified].
- A 60/40 cheap/standard load split gives a blended rate of 20.82p [derived, assumed split]. Break-even then drops to SPF 2.19 [derived].

**Levy rebalancing**
- **Autumn Budget 2025:** 75% of Renewables Obligation costs moved to taxation, and ECO ends in April 2026. Octopus estimates about £134 a year off a typical bill from 1 April 2026 ([Octopus](https://octopus.energy/blog/autumn-budget-2025-explained/)). The government gives "£150 off" ([Hansard](https://hansard.parliament.uk/html/Commons/2026-01-21/WrittenStatements)).
- The MCS Foundation wants all remaining levies off electricity ([MCS Foundation](https://mcsfoundation.org.uk/wp-content/uploads/2026/03/What-the-Warm-Homes-Plan-means-for-home-decarbonisation-The-MCS-Foundation.pdf)). The HPA says the price ratio is the key barrier to adoption ([H&V](https://www.heatingandventilating.net/improvement-in-heat-pump-performance-highlighted-by-new-electrification-of-heat-demonstration-report)).

**Carbon factors** ([greencalculus summary of DESNZ factors](https://greencalculus.com/data/defra-emission-factors/))
- **Grid electricity, generation only:** 0.177 kgCO₂e/kWh (2025 set, using 2023 data); 0.13096 (2026 set, using 2025 data).
- **Natural gas, gross CV:** 0.18296 (2025); 0.18231 (2026).
- **Other measures:** Hoare Lea gives a 2025 load-weighted average of 129 g/kWh, with regions ranging from 47 (North Scotland) to 252 (South Wales) ([Hoare Lea](https://hoarelea.com/2026/02/25/uk-grid-carbon-emissions-data/)).
- **Winter weighting:** heat pump load is winter- and evening-weighted, so its effective intensity is above the annual average. That premium is not quantified here [gap].

The worked table is in (d) below.

## 4. Installation

**Cost**
- **BUS average quotes** (gross, including grant, trimmed ±10%) ([Ofgem SY3](https://www.ofgem.gov.uk/sites/default/files/2025-07/BUS_Annual_Report_2024_to_2025.pdf)):
  - Air-source £13,433; most common band £10,001–12,500.
  - Ground-source £27,924.
- **Net of £7,500:** air-source about £5,933 [derived]. The MCS Foundation says "roughly £5k" after BUS, with costs down 11% in real terms since 2022 ([MCS Foundation](https://mcsfoundation.org.uk/wp-content/uploads/2026/03/What-the-Warm-Homes-Plan-means-for-home-decarbonisation-The-MCS-Foundation.pdf)).
- **Gas boiler replacement**, as the counterfactual: about £2,000–3,500 [unverified].

**Design**
- MCS heat-loss surveys follow MCS 031 / MIS 3005-D. The HPA is updating MCS 031 because of the gap between design SCOP and in-situ SPF ([H&V](https://www.heatingandventilating.net/improvement-in-heat-pump-performance-highlighted-by-new-electrification-of-heat-demonstration-report)).
- RHPP designs: 34% below 40 °C flow, 17% at 50–60 °C ([RHPP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/606818/DECC_RHPP_161214_Final_Report_v1-13.pdf)).
- Typical scope: some radiator upsizing, a new cylinder for combi homes, and often new pipework [unverified as quantities].

**Suitability:** EoH concluded heat pumps suit all house types and ages ([H&V](https://www.heatingandventilating.net/improvement-in-heat-pump-performance-highlighted-by-new-electrification-of-heat-demonstration-report)). Detached homes performed best ([UKDS](https://doc.ukdataservice.ac.uk/doc/9050/mrdoc/pdf/9050_eoh_Interim_insights_from_heat_pump_performance_data.pdf)).

**Time to install:** about 2–5 days on site [unverified]. Lead time from survey to commissioning runs to weeks.

**Satisfaction:** 90–95% among BUS owners ([MCS Foundation](https://mcsfoundation.org.uk/wp-content/uploads/2026/03/What-the-Warm-Homes-Plan-means-for-home-decarbonisation-The-MCS-Foundation.pdf)). 85% of EoH participants would recommend one ([ESC](https://es.catapult.org.uk/report/electrification-of-heat-summary-reports-and-datasets/)).

## 5. Fabric measures

**GB coverage at end-December 2025** ([HEE detailed release Mar 2026](https://assets.publishing.service.gov.uk/media/69ba6cf126909a14239612ed/HEE_Stats_Detailed_Release_March_2026.pdf))

| Measure | Insulated | Not insulated |
|---|---|---|
| Cavity walls (of 21.8m homes) | 15.4m (71%) | 5.0m: 3.7m easy to treat, 1.3m hard to treat (plus 1.3m uncertain) |
| Lofts (of 26.3m homes; "insulated" means ≥125 mm) | 17.7m (67%) | 7.7m: 5.5m easy, 2.2m hard or unfillable (plus 0.8m uncertain) |
| Solid walls (of 8.5m homes) | 0.909m (11%) | 7.6m (89%) |

**English Housing Survey 2023–24** ([EHS ch.2](https://gov.uk/government/statistics/chapters-for-english-housing-survey-2023-to-2024-headline-findings-on-housing-quality-and-energy-efficiency/chapter-2-energy-efficiency))
- **Cavity wall insulation by tenure:** private rented 60%, owner-occupied 73%, local authority 78%, housing association 80%.
- **Solid wall insulation by tenure:** owner-occupied 9%, private rented 10%.
- **Lofts:** 40% have ≥200 mm.
- **Glazing:** 89% fully double-glazed.
- **EPC bands:** 52% of the stock is band A–C (23% in 2013). Mean SAP is 67.

**EPC register band shares, England** (registrations, not the whole stock) ([UK Housing Review table 24c](https://www.ukhousingreview.org.uk/ukhr26/tables-figures/pdf/26-024.pdf))

| Year | A–B | C | D | E | F–G |
|---|---|---|---|---|---|
| 2025 | 15.3% | 48.3% | 29.8% | 5.1% | 1.5% |

- **Register coverage:** about 60% of England's stock and 55% of Wales ([MHCLG EPB release Q4 2025](https://www.gov.uk/government/statistics/energy-performance-of-building-certificates-in-england-and-wales-october-to-december-2025/energy-performance-of-buildings-certificates-statistical-release-october-to-december-2025-england-and-wales)). The ONS puts addresses with at least one EPC at about 71%, with the lowest coverage for pre-1930 homes (UKHR).
- **Certificate rules:** issued on build, sale or let, and valid for 10 years.

**Measured gas savings (NEED)**
NEED uses a weather-corrected comparison group, excludes flats and is weighted to the stock.

| Measure | Median gas saving | Source |
|---|---|---|
| Cavity wall | 7.3% (~1,000 kWh), 2015 gas year; 9.5% in 2014 | [NEED 2018 summary](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/720047/National_Energy_Efficienct_Data-Framework__NEED__Summary_2018.pdf) |
| Cavity by fill type (2013–15) | Bead 7.8–11.5%, mineral wool 5.7–10.0% | [DESNZ bead vs mineral wool](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/853563/Gas_consumption_savings_from_bead_and_mineral_wool_cavity_wall_insulation.pdf) |
| Loft (top-up dominated) | 2.2% (300 kWh) in 2015; 4.2% (2017 installs); 3–4% (2018 installs) | NEED [2018](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/720047/National_Energy_Efficienct_Data-Framework__NEED__Summary_2018.pdf), [2020](https://assets.publishing.service.gov.uk/media/5ef3ac02e90e075c5674daca/National_Energy_Efficiency_Data_Framework_NEED_report_summary_of_analysis_2020.pdf), [2021](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/996223/need-report-2021.pdf) |
| Solid wall | 18.9% (2017); 10% (2021); 16% (2022); 17% (2023 installs) | NEED [2020](https://assets.publishing.service.gov.uk/media/5ef3ac02e90e075c5674daca/National_Energy_Efficiency_Data_Framework_NEED_report_summary_of_analysis_2020.pdf), [2024](https://assets.publishing.service.gov.uk/media/667c2ca85b0d63b556a4b3ca/NEED-report-june-2024.pdf), [2025](https://assets.publishing.service.gov.uk/media/685bf0d30433072fce0e1000/need-report-june-2025.pdf), [2026](https://assets.publishing.service.gov.uk/media/6a2925376d178a6fb7e31fe8/NEED-report-june-2026.pdf) |
| Cavity + loft | 9% | [NEED 2025](https://assets.publishing.service.gov.uk/media/685bf0d30433072fce0e1000/need-report-june-2025.pdf) |
| Solid wall + loft | 14% | [NEED 2026](https://assets.publishing.service.gov.uk/media/6a2925376d178a6fb7e31fe8/NEED-report-june-2026.pdf) |
| Condensing boiler | 7.4% (~1,000 kWh) in 2015; 2–3% recently (Scotland), trending down | NEED 2018, 2026 |

**How savings decay**
- **Cavity and solid wall:** savings are sustained over 5 years, and may even rise.
- **Loft and condensing boiler:** savings fall by about a tenth between year 1 and year 5 ([NEED 2025](https://assets.publishing.service.gov.uk/media/685bf0d30433072fce0e1000/need-report-june-2025.pdf)), and by just over a fifth by year 7 ([NEED 2020](https://assets.publishing.service.gov.uk/media/5ef3ac02e90e075c5674daca/National_Energy_Efficiency_Data_Framework_NEED_report_summary_of_analysis_2020.pdf)).

**Modelled vs measured:** modelled savings (SAP/EST) are typically larger than NEED's measured savings [unverified as a ratio]. NEED notes that loft savings may be underestimated and that low-insulation homes save more than the median.

**Costs:** I could not fetch EST cost tables. Indicative figures: loft £~1,000, cavity £~2,000–3,000, external solid wall £~10,000–15,000 or more [all unverified].

**ECO / GBIS**
- **ECO:** 2.6m households upgraded since 2013; 271,700 measures in 2025. ECO4 averaged about 4 measures per household.
- **GBIS:** 92,700 households to December 2025 ([HEE Mar 2026](https://assets.publishing.service.gov.uk/media/69ba6cf126909a14239612ed/HEE_Stats_Detailed_Release_March_2026.pdf)).
- **ECO ends:** April 2026 ([Octopus](https://octopus.energy/blog/autumn-budget-2025-explained/)).

## 6. What shows in the data

**Heat pump signature.** These follow from the physics rather than from a cited dataset.
- Gas half-hourly reads drop to zero, or to cooking load only, from the switch date.
- Electricity rises by roughly heat ÷ SPF (about 2,000–3,200 kWh a year for a TDCV home [derived]).
- The increase is strongly winter-weighted and correlated with heating degree-days.
- On a time-of-use tariff, load shifts into cheap windows.
- A hot-water cycle shows as a daily block. Immersion use shows as spikes of about 3 kW [unverified].

**Heat-loss estimation from smart meter data (SMETER, DESNZ)**
- **Trial:** 30 homes in north-west England, compared against co-heating tests ([SMETER exec summary](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1050880/smeter-innovation-competition-report-executive-summary.pdf)).
- **Accuracy (CVRMSE):** best products 13–17%, against about 18–20% for RdSAP. Bias (NMBE) ranged from −27% to +10%.
- **Data needed:** 7 to 311 days.
- **Indoor sensors:** products using them did better.
- **Validated only for C/D homes:** not for A/B homes or heat pumps.
- **Implication for Poesys:** a meter-only, EPC-informed estimate of the heat transfer coefficient (HTC) carries roughly ±20–40% uncertainty per home [derived from the table].

**Insulation effect**
- Fit monthly or daily gas against heating degree-days before and after the measure. The slope (kWh per degree-day) drops; the base-load intercept should not.
- The NEED medians imply detectable slope changes of about 3% (loft) to about 17% (solid wall) [derived]. A 3% change is below what one home's year-to-year noise will reveal, so loft savings can only be "proved" across portfolios.

**EPC as a prior**
- The public EPC gives wall and roof type, insulation descriptions, glazing, main heating, floor area and SAP.
- Limits: coverage is about 60–71%, certificates may be 10 years old, and RdSAP inputs are assumed defaults.

**Must ask the customer:** occupancy and hours, thermostat setpoint, rooms heated, cylinder or combi, radiator count and sizes, works since the EPC, cooking fuel, secondary heating (wood or electric), and tenure.

## 7. Advice economics

**Heat pump payback against a boiler on the cap**
- At SPF 2.8 or below, annual unit savings are about zero [derived].
- Dropping gas entirely also removes the £108 gas standing charge [derived].
- On Cosy at SPF 3.5: saving ≈ £757 + £108 − £475 − £8 (extra electricity standing charge) ≈ **£382 a year** [derived].
- Net capex is about £5,900 against a boiler counterfactual of about £2,500 [unverified], so the increment is about £3,400. Simple payback ≈ **9 years** [derived].
- On the standard cap at SPF 2.8, savings are about £107 a year (from dropping the gas standing charge), so payback is about 30 years or more [derived].

**Fabric payback**
- **Cavity:** about 1,000 kWh × 7.97p ≈ £80 a year [derived]. At about £2,000–3,000 [unverified], simple payback is 25–35 years at current gas prices.
- **Loft:** about 300 kWh ≈ £24 a year [derived].
- These measured paybacks are far longer than the EST-style modelled claims [gap: EST figures not fetched].

**Sequencing**
- **Fabric first** cuts the peak heat loss, so the heat pump can be smaller and the flow temperature lower (higher SPF).
- **Heat pump first** gives a larger CO₂ cut per pound and keeps the price-ratio risk in view. It also argues for a time-of-use tariff and weather compensation over fabric at low NEED savings.
- **Modelling rule:** combined savings are less than additive (cavity + loft is 9%, against 7.3% + 2–4% separately).

**Who benefits**
- Owner-occupiers capture both the capex and the bill savings.
- Private landlords must reach EPC C, on two metrics, by October 2030 unless exempt ([MCS Foundation](https://mcsfoundation.org.uk/wp-content/uploads/2026/03/What-the-Warm-Homes-Plan-means-for-home-decarbonisation-The-MCS-Foundation.pdf)), but the tenant pays the bills (split incentive).
- Private rented homes have the lowest cavity insulation rate (60%) ([EHS](https://gov.uk/government/statistics/chapters-for-english-housing-survey-2023-to-2024-headline-findings-on-housing-quality-and-energy-efficiency/chapter-2-energy-efficiency)).

## 8. Proving savings

**NEED method**
- Weather-corrected consumption (temperature and wind) for treated homes, two years apart (e.g. 2022 vs 2024), minus the change in a comparator group with no measures. The result is reported as a median.
- Flats and outliers are excluded.
- Measures installed outside government schemes are largely unobserved, which may bias savings down ([NEED 2025](https://assets.publishing.service.gov.uk/media/685bf0d30433072fce0e1000/need-report-june-2025.pdf)).
- NEED does not weather-correct electricity, so heat pump electricity needs a degree-day model of its own.

**IPMVP Option C** [unverified details]
- Whole-facility meter data and a regression baseline on degree-days (12 months or more before and after), with the adjusted baseline projected into the reporting period.
- Savings = adjusted baseline − actual.
- Uncertainty is reported via CV(RMSE). ASHRAE Guideline 14 thresholds are commonly cited [unverified].

**Comparison groups:** a supplier can build matched controls from its own book (same EPC band, region, pre-period consumption) using a difference-in-differences design. That replicates NEED.

**Pitfalls**
- **Rebound / comfort-taking:** a likely cause of loft and boiler savings decaying ([NEED](https://assets.publishing.service.gov.uk/media/685bf0d30433072fce0e1000/need-report-june-2025.pdf)).
- **Prebound:** low-income homes underheat relative to the SAP model, so the measured baseline is below the modelled one [unverified literature: Sunikka-Blank & Galvin 2012].
- **Attribution:** other works, occupancy changes, price shocks (2022) and COVID all confound results. Comparator groups absorb only common shocks.
- **Self-selection:** heatpumpmonitor's SPF 3.86 against EoH's 2.80 shows how far self-selected samples can drift above representative ones.

---

## (a) Headline figures and bands to check a simulated world against

| Quantity | Target band | Source |
|---|---|---|
| Air-source SPFH4, representative stock | median 2.8 (IQR 2.53–3.09); RHPP-era 2.44 | EoH, RHPP |
| Air-source SPF, well-designed tail | ~3.8–3.9 | heatpumpmonitor |
| Air-source hot-water SPFH2 | ~2.3 | RHPP |
| Coldest-day air-source COP | ~2.44 | EoH |
| Hybrid SPFH4 | ~2.4; heat pump meets ~39% of space heat | EoH |
| Share of homes with cavity insulation (of cavity homes) | 71% | HEE |
| Share of homes with ≥125 mm loft insulation | 67% | HEE |
| Share of solid walls insulated | 11% | HEE |
| EPC bands A–B / C / D / E / F–G (registrations, England 2025) | 15 / 48 / 30 / 5 / 1.5% | UKHR / MHCLG |
| Stock A–C (EHS 2023) | 52% | EHS |
| Measured median gas saving: loft / cavity / solid wall | ~2–4% / ~7–10% / ~16–19% | NEED |
| Loft savings at year 5 vs year 1 | −10% | NEED |
| Air-source share of new installs | 97–99% | BUS, DESNZ |
| Retrofit installs, 2025 | ~52–53k | DESNZ |
| Air-source gross cost | ~£13.4k (net ~£5.9k [derived]) | Ofgem BUS |
| Price ratio / break-even SPF (cap, Q4 2026) | 3.30 / 2.77 [derived] | Ofgem |

## (b) What the world needs to model (hidden attributes per home)

**Building**
- Heat transfer coefficient (W/K), built up from the fabric elements:
  - wall type (cavity filled/unfilled/hard-to-treat; solid insulated/not)
  - loft depth (mm)
  - floor type
  - glazing
  - air permeability
- Floor area, archetype (detached/semi/terrace/flat), age band.
- Thermal mass (time constant).

**Heating system**
- Boiler efficiency in use.
- Emitter capacity (radiator output at ΔT50), achievable flow temperature, weather compensation on/off.
- Heat pump sizing relative to design heat loss, which drives cycling and load factor.
- Refrigerant / unit quality.
- Cylinder size and losses, immersion use, defrost behaviour.

**Occupants**
- Setpoint and schedule, rooms heated, occupancy count.
- Hot-water demand.
- Underheating / prebound tendency, rebound response to a measure.
- Secondary heating, cooking fuel.
- Price sensitivity, tenure, ability to pay.

**Data quality**
- Whether the EPC is accurate (true vs lodged values).
- Undeclared works since the EPC.

**Environment**
- Local weather (degree-days, design temperature).
- Regional grid carbon intensity.

## (c) What the supplier can observe / infer / must ask

| Attribute | Observe | Infer | Must ask / survey |
|---|---|---|---|
| Gas and electricity consumption (half-hourly where smart) | yes | — | — |
| Heat pump present / switch date | — | yes, gas → 0 and winter electricity rises | confirm |
| HTC | — | yes, ±20–40% via SMETER-type regression on reads + weather | survey for MCS sizing |
| Wall / loft / glazing type | EPC (if present, ≤10 years old) | partly from the degree-day slope | yes, post-EPC works |
| Floor area, archetype | EPC | — | if no EPC |
| SPF of an installed heat pump | — | only with a heat meter or an assumed heat demand | heat meter / installer data |
| Setpoint, schedule, occupancy | — | weakly from the load shape | yes |
| Emitters, cylinder, flow temperature | — | — | yes / survey |
| Tenure | — | partly (change-of-tenancy patterns) | yes |
| Payment stress | yes | — | — |
| Secondary heating | — | anomalies in the gas–degree-day fit | yes |

## (d) Worked heat pump vs boiler table (TDCV home)

**Assumptions**
- Gas use 9,500 kWh a year with an 84%-efficient boiler, so heat delivered = 7,980 kWh [derived].
- Prices: Ofgem cap for Q4 2026. Electricity 26.32p excludes VAT; gas 7.97p includes 5%.
- Cosy blend 20.82p from an assumed 60/40 cheap/standard split.
- Carbon: DESNZ 2026 factors, generation only.

| System | Electricity kWh | Units, cap | Units, Cosy | Standing-charge change if gas is capped off | kgCO₂e (0.13096) | kgCO₂e (0.177, 2025 factor) |
|---|---|---|---|---|---|---|
| Gas boiler | — | £757 (gas) + £108 gas standing charge | — | — | 1,732 (gas 0.18231) | 1,738 (gas 0.18296) |
| Heat pump, SPF 2.5 | 3,192 | £840 | £665 | −£108 (−£100 on Cosy) | 418 | 565 |
| Heat pump, SPF 2.8 | 2,850 | £750 | £593 | as above | 373 | 504 |
| Heat pump, SPF 3.0 | 2,660 | £700 | £554 | as above | 348 | 471 |
| Heat pump, SPF 3.5 | 2,280 | £600 | £475 | as above | 299 | 404 |
| Heat pump, SPF 4.0 | 1,995 | £525 | £415 | as above | 261 | 353 |

- All heat pump figures are [derived].
- **Carbon:** the heat pump cuts CO₂ by **67–85%** at every SPF [derived].
- **Cost on the standard cap:** savings are marginal at SPF ≤ 2.8. **Most of the cost advantage comes from the tariff and from dropping the gas standing charge.**

## (e) Named gaps

1. **MCS install series 2016–2021:** not fetched. The three counting bases (MCS, DESNZ retrofit, all-incl-new-build) disagree (2024: 48.7k vs 84k).
2. **EoH final report:** gated. I used interim figures, so there is no final SPF distribution and no metered hot-water SPF.
3. **heatpumpmonitor paper:** *Energy and Buildings* paper not fetched. No numbers for cycling, defrost or the flow-temperature-to-SPF curve.
4. **Fabric costs and modelled savings:** EST costs and modelled savings, and SAP 10.2 values, were not fetched. All fabric cost figures are [unverified].
5. **NEED kWh medians:** recent cavity and loft kWh medians appear only in charts or data tables. The latest text-stated kWh figures are from 2015.
6. **Heat pump savings in NEED / electricity uplift:** no measured uplift in electricity after a heat pump install was found in NEED.
7. **Cosy rates:** from a third party, with the VAT basis unclear. No other heat pump tariffs (OVO, EDF) were checked.
8. **Electricity carbon factors:** T&D losses and seasonal/marginal intensity for heat pump load are not quantified.
9. **CCC / NESO FES:** heat pump pathways, the CCC 2030 figure and any FES scenarios were not fetched.
10. **IPMVP / ASHRAE 14 thresholds and the prebound/rebound literature:** [unverified].
11. **Install duration and boiler-replacement counterfactual cost:** [unverified].
12. **SMETER for heat pump homes and A/B-rated homes:** not validated in the source.