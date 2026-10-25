# Director evidence: gas boilers and heating controls

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

# Evidence pack: how GB gas boilers and heating controls work, and how they show up in gas data

*For the Poesys knowledge layer. Compiled 25 Oct 2026. Every figure has its source beside it. **[derived]** means my own arithmetic. **[unverified]** means I recalled it and no source I fetched confirmed it.*

**Limits of this pack.** The web-search budget ran out before the end of research. Several primary sources were blocked or only partly readable: the Nesta evidence-summary PDF, the Nesta Energy House PDF, the EST "replacing your boiler" page, the Ofgem TDCV page, Hanmer 2019 and the DESNZ factor spreadsheet. Where that happened, a secondary source is used and named.

---

## 0. Baseline constants

| Constant | Value | Source |
|---|---|---|
| Ofgem medium gas TDCV (before 1 Jul 2026) | 11,500 kWh/yr. Low is 7,500 and high is 17,000 | [Selectra summary of Ofgem](https://selectra.co.uk/energy/guides/consumption/average-consumption-uk) |
| **Ofgem medium gas TDCV (from 1 Jul 2026)** | **9,500 kWh/yr.** Gas TDCVs fell 15–20% across all bands | [Ofgem summary of changes, Jul–Sep 2026](https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf); [Energy UK](https://www.energy-uk.org.uk/wp-content/uploads/2026/05/Energy-UK-Explains-Typical-Domestic-Consumption-Values.pdf) |
| Gas cap unit rate (1 Apr–30 Jun 2026, Direct Debit, GB average) | 5.74 p/kWh, plus a standing charge of 29.09 p/day | [Selectra](https://selectra.co.uk/energy/guides/consumption/average-consumption-uk) (third party, may be out of date) |
| Gas carbon factor (DESNZ 2025, gross CV) | 0.18231 kgCO2e/kWh. The grid biogas blend is 0.18296 | [greencalculus](https://greencalculus.com/glossary/natural-gas/); [Climatiq](https://www.climatiq.io/data/emission-factor/989715b3-8736-4500-8929-bf09a1b44dfa) (both transcriptions; the spreadsheet itself was not read) |

**The brief's 11,500 kWh figure is out of date.** Ofgem moved to 9,500 kWh from 1 July 2026. The worked figures below use **11,500 kWh at 5.74p and 0.183 kg/kWh** [derived assumptions]. To rescale to 9,500 kWh, multiply by 0.83.

**Gas end-use split** (DECC, *Estimates of heat use in the UK in 2013*, [Energy Trends Dec 2014](https://assets.publishing.service.gov.uk/media/5a7d5c80e5274a3356f2bc0e/Estimates_of_heat_use.pdf)):

| End use | Share of domestic gas heat |
|---|---|
| Space heating | ~77% |
| Water heating | ~21% |
| Cooking | ~2% |

The percentages were calculated by the fetch tool from ktoe values. Nesta uses 75% for space heating, citing government national statistics table U3, 2021 ([Nesta MSBC evidence](https://www.nesta.org.uk/report/money-saving-boiler-challenge-supporting-evidence-october-2022/)).

On the TDCV that split gives [derived]:
- Space heating about 8,850 kWh
- Hot water about 2,415 kWh, or 6.6 kWh/day
- Cooking about 230 kWh, or 0.6 kWh/day

---

## 1. Boiler types and stock

**Types.**
- A **combi** heats water on demand with no cylinder.
- A **system** or **regular (heat-only)** boiler feeds a stored cylinder. That cylinder often has an immersion heater as well.

Shares:
- **EFUS 2017:** combis were 62% of boilers and standard/regular were 38%. Between 49% and 60% of the regular-boiler homes have an immersion. About 22% of all central-heating homes have one ([EFUS heating patterns](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf)).
- **English Housing Survey 2023–24:** condensing-combi boilers rose from 28% of homes in 2001 to 55% in 2023. "Combination" boilers, a separate category, rose from 10% to 19%. Central heating is in 93% of homes. 7–19% of homes have no boiler, depending on tenure ([EHS ch.2](https://gov.uk/government/statistics/chapters-for-english-housing-survey-2023-to-2024-headline-findings-on-housing-quality-and-energy-efficiency/chapter-2-energy-efficiency)). The definition of the 19% category needs checking: it reads as non-condensing combis, which looks high.

**Stock and age.**
- About 22 million UK homes have gas central heating.
- 1.67 million boilers were sold in 2019.
- About 4 million old, inefficient "zombie" boilers remain in use.

All three figures are from HHIC via [Builders Merchants News, Jan 2020](https://www.buildersmerchantsnews.co.uk/news/merchants/boiler-sales-zombie-boilers-survive). Condensing boilers have effectively been mandatory since 2005. Which? suggests replacement is worthwhile mainly for "non-condensing boilers installed before 2005" ([Which?](https://www.which.co.uk/reviews/boilers/article/boiler-energy-efficiency)). The exact regulatory dates (England and Wales from April 2005, NI later) are [unverified].

**Lifetime.** No authoritative GB source was found. A 10–15 year working life is commonly cited [unverified]. One modelling framework assumes 25 years with no source given ([DEM docs](https://dem-documentation.readthedocs.io/en/latest/modelling_method/gen_conv_techs/gas_boiler.html)). This is listed as a gap.

**Rated vs measured efficiency.**
- Since Boiler Plus (April 2018, England), new gas boilers must reach 92% ErP on their own label ([BEIS Boiler Plus factsheet](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/718569/Boiler_Plus_Factsheet_v3.pdf)).
- SAP 10 does not use ErP directly. ErP's 85/15 part-load weighting implies an average return temperature of 34.5°C. Hourly analysis supports 47.6°C, so ErP overstates in-use efficiency ([BRE S10TP-12](https://bregroup.com/documents/d/bre-group/s10tp-12-seasonal-efficiency-of-condensing-boilers-v1-2)).

**In-situ field trial** (GASTEC for EST, 2009; 43 boilers with a full year of data; [final report](https://assets.publishing.service.gov.uk/media/5a75149be5274a3cb28697f7/In-situ_monitoring_of_condensing_boilers_final_report.pdf)):

| Boiler | Measured | Rated / notes |
|---|---|---|
| Regular | 85.3% | SEDBUK 90.4%. About 80.3% once ~900 kWh/yr of primary pipework and cylinder losses are included |
| Combi | 82.5% | Includes SAP's 600 kWh/yr combi loss allowance |
| Combi hot water | ~73% | Very short draw-offs are much worse |
| CPSU | 64–77% | — |

Other findings from the same trial:
- Oversizing alone did not reduce efficiency.
- Efficiency was independent of load above a monthly load factor of about 5%.
- The report recommends an in-use correction of about **0.95** for condensing boilers.

**The real-world gap: condensing depends on return temperature.**
- Gas boilers start condensing below a return of about 55°C ([BRE for BEIS, 2017](https://assets.publishing.service.gov.uk/media/5a81f66ced915d74e62350ca/heating-controls-compensation-tpi-bre.pdf)). Nesta gives about 54°C.
- Typical UK flow settings are 70–80°C ([Nesta](https://www.nesta.org.uk/report/money-saving-boiler-challenge-supporting-evidence-october-2022/)). Many boilers ship at 80°C ([Which?](https://www.which.co.uk/reviews/boilers/article/boiler-energy-efficiency)).
- So many "condensing" boilers seldom condense.

SAP 10 modelled seasonal efficiency for a modulating gas boiler with no compensation, by design flow/return temperature ([BRE S10TP-12](https://bregroup.com/documents/d/bre-group/s10tp-12-seasonal-efficiency-of-condensing-boilers-v1-2)):

| Design flow/return (°C) | 80/60 | 55/47 | 45/39 | 35/30 |
|---|---|---|---|---|
| Seasonal efficiency | 87.1% | 89.3% | 92.8% | 95.3% |

With ideal compensation the figures are 89.9%, 93.1%, 94.9% and 96.3%. An on/off boiler with no compensation is 85.3% at 80/60.

---

## 2. Flow temperature

**Nesta Money Saving Boiler Challenge (Oct 2022)** ([evidence](https://www.nesta.org.uk/report/money-saving-boiler-challenge-supporting-evidence-october-2022/)). Results from Salford Energy House tests, reducing flow temperature from 80°C to 60°C:
- About 9% of the total gas bill, or 12% of heating gas.
- 1,092 kWh/yr on a 12,000 kWh home, which is £112 at 10.3p.

Other results and estimates:
- 55°C saved about 12% and 50°C saved about 17.4%.
- HHIC estimates 6–8% of total gas.
- Cambridge Architectural Research estimates 8% for 75→60°C. **That 8% is split: 3.6% from boiler efficiency and 4.4% from lower heat demand**, meaning cooler rooms.

Trade-offs found by Nesta:
- Warm-up takes 17 minutes longer.
- Rooms average 0.5°C cooler over 24 hours.
- Starting the heating 30 minutes earlier to compensate removes 3–4 percentage points of the saving (Energy Systems Catapult modelling).

**EST** ([flow temperature advice, May 2026](https://energysavingtrust.org.uk/should-i-turn-boilers-flow-temperature-down/)):
- Claims of "up to 9%" on gas bills should be read in context. Nesta found that 60°C raises boiler efficiency by "nearly 4%".
- **Cylinder systems should not go below 65°C**, because of Legionella risk.
- Combis can go to about 60°C, or 50–55°C in mild weather.
- Gas use can fall "for reasons other than efficiency", such as slower heating or cooler rooms.

**Measured field result.** The Nesta/Loop randomised controlled trial (April 2022, 3,502 treatment vs 3,500 control) gives the only measured result found ([Nesta RCT](https://www.nesta.org.uk/report/helping-homeowners-optimise-their-boiler-flow-temperatures-with-step-by-step-advice-results-of-a-randomised-controlled-trial/)):
- 34% of the treatment group reported lowering flow temperature, against 19% of the control group.
- The intention-to-treat gas change was −0.36 kWh/day, about **−1.4%, not significant** (p = 0.059).
- The trial ran in spring.

**Radiator sizing.** SAP 10 assumes emitters sized at about 1.2 times heat loss. It gives boilers extra heating hours on the coldest days because 11-hour heating "can't deliver the required heat" ([BRE S10TP-12](https://bregroup.com/documents/d/bre-group/s10tp-12-seasonal-efficiency-of-condensing-boilers-v1-2)). Lower flow temperature therefore stops working first in homes with undersized radiators.

---

## 3. Controls

**Setpoint.**
- EFUS 2017: median setpoint 20.0°C, mean 20.4°C, interquartile range 19–21°C ([EFUS](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf)).
- SERL panel (4,202 homes): mean reported setpoint fell from 20.2°C (2019–21) to 19.2°C (2023). The share below 18°C rose from 6.7% to 15.2%. Households with someone over 65 were less likely to cut ([Hanmer & Zapata-Webborn, NEA 2024](https://nea.org.uk/wp-content/uploads/2024/11/Hanmer_Zapata-Webborn_ColderHomes.pdf)).

**Saving per °C.**
- EST: turning down from 22°C to 21°C saves £120/yr in GB. Recommended settings are 18–21°C, with a setback of 12–15°C when out or asleep ([EST heating controls, Sep 2026](https://energysavingtrust.org.uk/advice/thermostats-and-heating-controls/)).
- Which?, citing EST: each degree adds about 10% to heating cost ([Which?](https://www.which.co.uk/news/article/smart-thermostats-can-you-save-what-the-companies-claim-aPhUI1z1HPCX)).
- My check [derived]: 10% of 8,850 kWh is about 885 kWh, which is about £51 at 5.74p and about 162 kgCO2. EST's £120 implies about 2,090 kWh at 5.74p. EST's price and home assumptions are not stated, so **treat the £120 as an upper figure**.

**Timers and schedules.**
- Median heating time is 7h on weekdays and 8h at weekends.
- 58% heat twice a day on weekdays, 23% once a day.
- Heating season averages 5.7 months, and 6% heat all year.
- 46% use a timer and 34% only a manual thermostat.
- Main room thermostat in 87% of homes. TRVs on all or most radiators in 79%.

All from [EFUS](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf).

**Full controls package (programmer, room thermostat, TRVs).** EST says it saves about £100/yr. It costs about £600 from scratch, or about £370 for TRVs alone ([EST](https://energysavingtrust.org.uk/advice/thermostats-and-heating-controls/)).

**Evidence quality is weak.**
- A systematic review of 67 studies found low or no evidence of savings for most controls. It found **moderate evidence that smart thermostats do not save energy** compared with a standard thermostat and programmer, and may increase demand. Zonal control has moderate evidence of saving ([Munton/Lomas et al. review, Strathprints](https://strathprints.strath.ac.uk/78355)).
- A BEIS-commissioned review found evidence for controls "limited". Theoretical savings of 5–15% from programmable thermostats are not borne out in practice. A US field study found 10–15% from weather compensation ([UWE/BSRIA for BEIS, 2017](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/650840/heating-controls-international-evidence.pdf)).

**Weather compensation, load compensation and TPI** ([BRE for BEIS](https://assets.publishing.service.gov.uk/media/5a81f66ced915d74e62350ca/heating-controls-compensation-tpi-bre.pdf)):

| Control | Evidence | Saving |
|---|---|---|
| Weather compensation | Manufacturer claims | 10–40% |
| Weather compensation | Viessmann test house | 15–45%. BRE judged it unrepresentative |
| Load compensation | Chamber test | 10–14% |
| TPI | EST field trial (2010) | **0–0.5%, not significant** |

BRE warns all of these are likely upper bounds. In SAP, condensing gas boilers get a 3% credit for weather or enhanced load compensation. SAP 10 credits only 50% of the predicted improvement for weather compensation alone, and 90% for weather compensation with a room sensor. Many "load compensators" on sale do not actually limit flow temperature ([BRE S10TP-12](https://bregroup.com/documents/d/bre-group/s10tp-12-seasonal-efficiency-of-condensing-boilers-v1-2)).

**Boiler Plus (England, April 2018).**
- Minimum 92% ErP.
- A timer and room thermostat are mandatory.
- **Combis must also have one of:** flue gas heat recovery, weather compensation, load compensation, or smart controls with automation and optimisation. Compliance can cost "as little as £50".

([BEIS factsheet](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/718569/Boiler_Plus_Factsheet_v3.pdf))

**Smart thermostats.** The Behavioural Insights Team evaluation of the Nest Learning Thermostat in the UK ([BIT](https://www.bi.team/wp-content/uploads/2017/11/311013-Evaluating-Nest-BIT-Exec-Tech-Summaries.pdf)):

| Study design | Saving on household gas |
|---|---|
| Matched comparison, 2,248 homes each side | 5.8% (±3.2%) |
| RCT, 276 homes, vs a full modern controls suite | 4.5–5.0% a year (±4–6%), not robust |
| Seasonal Savings add-on | 2.8% |

Manufacturer claims, as reviewed by Which? ([Which? 2021](https://www.which.co.uk/news/article/smart-thermostats-can-you-save-what-the-companies-claim-aPhUI1z1HPCX)):
- **tado:** "up to 31%".
- **Hive:** "up to £110", based on 16,489 kWh/yr of use.
- **Nest:** 8.4–16.5%, measured against homes heating 17+ hours a day. BEIS data shows typical heating time is 7.5–8 hours.

**Heating on all day vs on/off.**
- EST says on/off is cheaper for boilers ([EST](https://energysavingtrust.org.uk/when-to-put-heating-on/)).
- A Salford Energy House test in a solid-wall end terrace compared 24-hour heating with 9 hours split 2h + 7h. **The 24-hour schedule used 31% more gas**, much less than the extra run time would suggest. The authors say the result does not generalise ([Salford, 2023](https://www.salford.ac.uk/news/researcher-wins-prize-for-research-on-domestic-gas-central-heating-energy-use)).

---

## 4. Emitters and maintenance

**Radiator sizing.** SAP assumes about 1.2 times heat loss ([BRE](https://bregroup.com/documents/d/bre-group/s10tp-12-seasonal-efficiency-of-condensing-boilers-v1-2)).
- Oversized radiators allow low flow temperature and condensing.
- Undersized radiators force high flow temperature.

No GB stock distribution of radiator oversizing was found. This is a gap.

**Sludge, flushing and inhibitor.**
- Fernox says that, after Carbon Trust verification, its cleaner plus inhibitor gives "up to 15%" gas saving per room heated, about 90 kgCO2e per home per year. No sample size or funding is disclosed ([Construction Index](https://www.theconstructionindex.co.uk/news/view/carbon-trust-verifies-carbon-savings-using-fernox-protector-f1-and-cleaner-f3)). **Treat this as an industry claim.**
- Costs: power flush £300–400 for a 2-bed, £400–550 for a 3-bed, £550–700+ for a 4-bed. A magnetic filter adds £100–150. A chemical flush is £200–400 ([Homebuilding, 2025](https://homebuilding.co.uk/advice/power-flushing-costs)).
- BS 7593 is the code of practice for water treatment ([BSI](https://knowledge.bsigroup.com/products/code-of-practice-for-the-preparation-commissioning-and-maintenance-of-domestic-central-heating-and-cooling-water-systems-1)).
- **No independent GB field trial was found that measures gas savings from flushing, filters, balancing or bleeding.** This is a gap.

**Servicing.** No published efficiency gain was found. This is a gap.

---

## 5. Hot water

- Water heating is about 21% of domestic gas heat ([DECC 2014](https://assets.publishing.service.gov.uk/media/5a7d5c80e5274a3356f2bc0e/Estimates_of_heat_use.pdf)).
- EST says hot water is about 12% of a typical household's *total* energy bill ([EST water tips](https://energysavingtrust.org.uk/wp-content/uploads/2022/03/Water-saving-tips.pdf)).

**Combis** heat on demand. Hot water efficiency is about 73%, and short draws (such as hand-washing) are inefficient ([GASTEC/EST](https://assets.publishing.service.gov.uk/media/5a75149be5274a3cb28697f7/In-situ_monitoring_of_condensing_boilers_final_report.pdf)).

**Cylinders.**
- Standing losses dominate. **As little as half the heat delivered to the cylinder reached the taps.**
- Primary and cylinder losses are about 900 kWh/yr.

(Same GASTEC/EST report.)

- EST recommends a cylinder thermostat at 60°C ([EST](https://energysavingtrust.org.uk/advice/thermostats-and-heating-controls/)).
- Daily immersion use in central-heating homes is 15% in summer and 6% in winter ([EFUS](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf)). This moves hot water from the gas meter to the electricity meter.

---

## 6. What shows in the data

**Daily gas vs heating degree days (HDD).** The standard model is daily gas = baseload + slope × HDD, above a balance-point temperature. This is the PRISM / change-point family [unverified as citation].
- **The slope** is roughly the heat transfer coefficient (HTC) × 24/1000 ÷ boiler efficiency, net of internal gains [derived].
- **Typical slope:** about 8,850 kWh ÷ about 2,000 HDD a year ≈ 4.4 kWh/HDD [derived; the annual HDD figure is unverified].
- **The intercept** is hot water plus cooking, about 7 kWh/day on the TDCV home [derived].

What each choice does to the profile [derived from the physics; no published validation found unless cited]:

| Choice | Signature |
|---|---|
| Setpoint cut | Slope falls and the balance point moves lower |
| Flow-temperature cut | Slope falls a little (efficiency plus cooler rooms). Daily data cannot tell this apart from a setpoint cut |
| Timed heating | Half-hourly morning and evening peaks, plus a large burst at warm-up |
| Always-on | Flatter daily profile, higher total (Salford: +31%) |
| Weather compensation | Long, low-rate burns. Less difference between peak and average within the day |
| Combi hot water | Short spikes in single half-hours, clearest in summer. A 10-minute shower uses about 4 kWh of gas [derived: 8 L/min × 10 min × 35 K ÷ 0.8 efficiency] |
| Cylinder | Timed reheat blocks, and standing loss shows as extra baseload. If the immersion is used, summer gas falls while electricity rises |

**Published methods.**

*SMETER* ([BEIS executive summary](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1050880/smeter-innovation-competition-report-executive-summary.pdf)). Algorithms estimated HTC from smart meter data and were checked against co-heating tests in 30 homes:

| Method | Mean bias error (NMBE) | Scatter (CVRMSE) |
|---|---|---|
| Best (SMETER H) | −0.7% | 13.4% |
| Worst (SMETER A) | −26.9% | 38.9% |
| Expert RdSAP | — | 18.2% |

Other findings and limits:
- **Methods using internal temperature sensors did better than meter-only methods.**
- The sample was mostly combis in EPC band C–D homes.
- Detecting a change after retrofit was not tested.

*SERL* ([McKenna et al., 2022](https://eprints.soton.ac.uk/451751)). Daily-demand mixed models on 1,418 and 682 households explained 63–80% of variance using HDD, setpoint, building and household data.

*Living Lab* ([Energy Systems Catapult, 2022](https://es.catapult.org.uk/report/measuring-the-consumer-response-to-the-energy-crisis-in-the-living-lab/)). With internal temperature sensors, 36 homes cut weather-normalised gas by about 30% in Sep–Oct 2022 vs 2021. Space heating fell about 40% while rooms were about 0.6°C cooler.

**Not found:** any published, validated method for inferring flow temperature, boiler efficiency or setpoint from smart meter gas data alone.

---

## 7. Advice economics

All rows assume 11,500 kWh at 5.74p and 0.183 kg/kWh unless the source says otherwise.

| Action | Published saving | Per TDCV home [derived] | Cost / payback |
|---|---|---|---|
| Thermostat −1°C | ~10% of heating ([Which?/EST](https://www.which.co.uk/news/article/smart-thermostats-can-you-save-what-the-companies-claim-aPhUI1z1HPCX)). EST says £120 ([EST](https://energysavingtrust.org.uk/advice/thermostats-and-heating-controls/)) | ~885 kWh, £51, 162 kg | Free |
| Flow 80→60°C | 9% of total in a test house ([Nesta](https://www.nesta.org.uk/report/money-saving-boiler-challenge-supporting-evidence-october-2022/)). RCT: 1.4%, not significant ([RCT](https://www.nesta.org.uk/report/helping-homeowners-optimise-their-boiler-flow-temperatures-with-step-by-step-advice-results-of-a-randomised-controlled-trial/)) | 1,035 kWh, £59, 189 kg (test house). 160 kWh, £9 (RCT) | Free |
| Full controls / TRVs | £100/yr ([EST](https://energysavingtrust.org.uk/advice/thermostats-and-heating-controls/)) | — | £600 (or £370 for TRVs). Payback 4–6 yrs at EST's figure |
| Smart thermostat | 4.5–5.8% ([BIT](https://www.bi.team/wp-content/uploads/2017/11/311013-Evaluating-Nest-BIT-Exec-Tech-Summaries.pdf)). Possibly zero ([review](https://strathprints.strath.ac.uk/78355)) | 520–670 kWh, £30–38, 95–122 kg | Device price not sourced |
| Weather compensation | 10–15% (US field) to 10–40% (claims) ([BRE](https://assets.publishing.service.gov.uk/media/5a81f66ced915d74e62350ca/heating-controls-compensation-tpi-bre.pdf)). SAP credit 3% | 3%: ~350 kWh, £20 | ~£50 under Boiler Plus ([BEIS](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/718569/Boiler_Plus_Factsheet_v3.pdf)) |
| Power flush + inhibitor | "Up to 15%" (industry claim) | Not credible as a central figure | £300–700+ |
| Servicing | Nothing found | — | — |
| Replace G-rated with A-rated | £420/yr GB ([EST heating](https://energysavingtrust.org.uk/energy-at-home/heating-your-home/)). An earlier EST figure was £580 ([iheat](https://iheat.co.uk/boiler-help/how-much-can-a-new-boiler-save-me)) | Physics check, about 70%→89% in use [the 70% G-band cut-off is unverified]: ~2,450 kWh, £140, 450 kg | £1,500–3,000 ([Which?](https://www.which.co.uk/reviews/boilers/article/boiler-energy-efficiency)) or £1,845–3,299 ([iheat](https://iheat.co.uk/boiler-help/how-much-can-a-new-boiler-save-me)). Payback 11–20 yrs on the physics check, 4–8 yrs on EST's figure |

EST's £ figures run about 2–3 times higher than my own calculations at the Q2 2026 cap rate. Ask EST for the unit price and consumption behind them before using them as world truth.

---

## 8. Rebound, prebound and the gap between modelled and measured savings

- **Prebound.** In 3,400 German homes, actual heating use was about 30% below calculated on average. The gap was about 40% for the least efficient homes and about 17% for efficient ones, and use varied sixfold within a band. The UK shows the same pattern ([Cambridge](https://www.cam.ac.uk/research/news/the-prebound-effect)). Savings modelled from ratings are overstated most for poor homes.
- **Measured vs modelled.**
  - Flow temperature: the test house gave 9%, the RCT gave 1.4% and not significant.
  - TPI: claims of 6–10%, field result 0–0.5%.
  - Smart thermostats: claims up to 31%, measured about 5%, possibly zero.
- **Comfort take-back.** About half the "flow temperature saving" is cooler rooms rather than efficiency (CAR: 4.4 of 8 points). Pre-heating 30 minutes earlier gives back 3–4 points ([Nesta](https://www.nesta.org.uk/report/money-saving-boiler-challenge-supporting-evidence-october-2022/)). The smart thermostat review suggests some may increase demand ([review](https://strathprints.strath.ac.uk/78355)).
- **Underheating.** The 2022–23 setpoint cuts were concentrated among the fuel-poor (odds ratio 2.39) ([NEA/SERL](https://nea.org.uk/wp-content/uploads/2024/11/Hanmer_Zapata-Webborn_ColderHomes.pdf)). A falling slope can be harm, not success.

---

## (a) Headline figures and bands to check a simulated world against

| Metric | Band | Source |
|---|---|---|
| Combi share of boilers | 62% (EFUS 2017). About 55% condensing-combi plus 19% "combination" (EHS 2023) | EFUS; EHS |
| Homes with central heating | 93% | EHS |
| Non-condensing ("zombie") boilers | About 4m (2020) | HHIC |
| Medium gas use | 11,500 kWh until Jun 2026, 9,500 kWh after | Ofgem |
| Space heating / hot water / cooking | 77 / 21 / 2% | DECC 2014 |
| Mean setpoint | 20.0–20.4°C (2017). 19.2°C (2023) | EFUS; SERL |
| Heating hours | 7h weekday, 8h weekend. 58% twice daily | EFUS |
| Heating season | 5.7 months. 6% heat all year | EFUS |
| TRV / room thermostat / timer | 79% / 87% / 46% | EFUS |
| Measured condensing efficiency | Regular 85% (80% with losses). Combi 82.5% | GASTEC/EST |
| Combi hot water efficiency | About 73% | GASTEC/EST |
| Cylinder delivery efficiency | Can be as low as 50% at taps. About 900 kWh/yr losses | GASTEC/EST |
| Condensing threshold | Return below about 55°C | BRE |
| Seasonal efficiency at 80/60 vs 55/47 | 87.1% vs 89.3% (no compensation) | BRE SAP10 |
| Saving per °C | About 10% of heating | EST via Which? |
| Flow temp 80→60°C | 9% (test house), 1.4% n.s. (RCT) | Nesta |
| Smart thermostat | 0 to about 6% | BIT; review |
| Always-on vs 9h | +31% gas (one house) | Salford |
| Prebound | About 30% average, 17–40% by rating | Sunikka-Blank & Galvin |

## (b) What the simulation's world needs to model (hidden attributes per home)

**The heating system**
- Boiler type: combi, system or regular. Condensing or not. Install year. Rated ErP/SEDBUK.
- In-use efficiency, as a function of return temperature (use the SAP10 curve) and of draw-off length for hot water.

**Settings**
- Flow temperature setting, which defaults high (70–80°C).
- Weather or load compensation fitted and commissioned (yes/no). Boiler Plus compliance by install date.
- Controls present: timer, room thermostat, TRVs, smart thermostat. Whether each is actually *used*.

**Heat demand and emitters**
- HTC (W/K), balance-point temperature, internal gains.
- Radiator oversizing ratio. This sets the lowest flow temperature that still delivers comfort.
- Sludge/fouling state as a parameter, with an *uncertain* effect.

**Household behaviour**
- Setpoint and setback. Schedule type: once, twice, three or more periods, or always-on. Heating-season months.
- Hot water demand: shower count and duration, baths, short draws.
- Cylinder volume, thermostat setting, standing loss, immersion use by season.
- Cooking gas.
- Secondary heating, about 4% of space heat (GASTEC/EST).

**Response to advice**
- Comfort take-back: pre-heating, raising the setpoint back up.
- Vulnerability flags: over-65s, fuel poverty, risk of underheating.

## (c) What the supplier can observe, infer, or must ask

| Item | Observe | Infer (and how reliably) | Must ask |
|---|---|---|---|
| Annual / daily gas | Smart half-hourly, or periodic reads | — | — |
| Baseload (hot water + cooking) | — | Summer intercept. Good with smart data | — |
| Weather sensitivity (slope) | — | HDD regression. Good, but it mixes HTC, efficiency and setpoint | — |
| HTC | — | SMETER-style. CVRMSE 13–39%; worse without internal temperature | Floor area, home type |
| Schedule type | — | Half-hourly peaks. Plausible but not validated in published work | Confirm |
| Combi vs cylinder | — | Spikes vs reheat blocks. Plausible, not validated | **Ask** |
| Setpoint | — | Weak: confounded with HTC | **Ask** (or use a connected thermostat) |
| Flow temperature, compensation | — | Not separable from daily data | **Ask** or get an engineer's view |
| Boiler age / efficiency | — | Very weak | **Ask** (model, year) |
| TRVs, smart controls | — | — | **Ask** |
| Sludge, balancing | — | — | Engineer only |
| Immersion use | Electricity half-hourly, if the same supplier | Summer gas/electricity swap | Confirm |
| Did the advice work? | Gas before and after | Weather-normalised difference against a control group. Needs an RCT-scale design (Nesta was underpowered at about 7,000 homes over 2 weeks) | Comfort outcome |

## (d) Named gaps

1. **Boiler lifetime:** no authoritative GB distribution found.
2. **Stock by age band:** no figure found. The EHS category definitions for "combination" vs "condensing-combination" need checking.
3. **Sludge, power flush, filters, inhibitor, balancing, bleeding:** no independent GB field measurement of gas savings found. Only an industry "up to 15%" claim.
4. **Servicing:** no published efficiency gain found.
5. **Flow temperature in winter:** the only RCT ran in spring and was underpowered. Nesta said a winter trial was planned; no result was found.
6. **Weather compensation in GB homes:** no independent field trial found. Evidence is US data, test houses or manufacturer claims.
7. **Inferring flow temperature, efficiency, setpoint or schedule from meter-only half-hourly gas data:** no validated published method found. SMETER covers HTC only, and works better with internal temperature.
8. **Radiator oversizing distribution** in the GB stock: not found.
9. **Rebound size after controls advice:** not quantified for the GB stock.
10. **Basis of EST's £ figures:** the unit price and consumption behind EST's figures are not stated, and they run about 2–3 times higher than my calculations at the Q2 2026 cap rate.
11. **Carbon factor:** confirmed only through third-party copies; the DESNZ spreadsheet itself was not read.
12. **Gas unit rate:** confirmed only through a third party for Q2 2026, and may be out of date.

---

**Notes for the project:**
- **Ofgem's medium gas figure changed from 11,500 to 9,500 kWh on 1 July 2026.** Any canon or simulation constant using 11,500 needs updating.
- Published measured savings consistently come in at a quarter to a half of modelled or claimed savings. The supplier's proof-of-saving logic should expect small effects and needs large comparison groups.