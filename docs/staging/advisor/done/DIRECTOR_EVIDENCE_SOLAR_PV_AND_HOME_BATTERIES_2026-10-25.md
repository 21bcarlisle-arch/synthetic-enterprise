# Director evidence: solar pv and home batteries

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

# Evidence pack: rooftop PV and home batteries in GB, for the Poesys knowledge layer

*Compiled 2026-10-25. Every figure has its source beside it. **[derived]** means my own arithmetic on sourced figures. **[unverified]** means it comes from memory or is an assumption no fetched source confirmed. The shared web-search budget ran out partway through, so some preferred sources (PVGIS direct, Elexon, NESO FES, Which?, the Tesla, Solis and Axle API docs) could not be reached. They are listed under Named gaps rather than filled in.*

---

## 1. Stock

**Fleet size.** DESNZ data to August 2026 shows 23.2 GW across about 2,131,000 installations of all sizes. Over the last 12 months there were 291,000 new installations, the most in any 12-month period since 2012. Domestic additions were over 1 GW across more than 195,000 homes in that year. August 2026 alone added 17,285 residential installations totalling 98 MW, which is about 5.7 kWp each **[derived]**. In 2026 to date, the 4–10 kW band added 404.4 MW and the up-to-4 kW band added 224.8 MW. The largest regions are the South West (~4.6 GW), South East (3.8 GW) and East (3.7 GW). ([Solar Power Portal, citing DESNZ, 1 Oct 2026](https://www.solarpowerportal.co.uk/solar-installations/uk-installs-record-291-000-new-solar-pv-installations-in-12-month-period))

**MCS-certified rooftop installations by year:**

| Year | Installs | Source |
|---|---|---|
| 2023 | 198,362 | [SPP/MCS](https://www.solarpowerportal.co.uk/battery-storage/mcs-bess-and-heat-pumps-drive-record-year-for-small-scale-renewables-in-2024) |
| 2024 | ~184,462 | same |
| 2025 | 267,032 (record, 31% above 2011) | [MCS](https://mcscertified.com/the-2026-low-carbon-landscape/) |

The MCS scheme total is "close to 2 million" ([MCS](https://mcscertified.com/the-2026-low-carbon-landscape/)). More than 36% of 2025 solar installations were on new builds (same source).

**FiT legacy vs post-2019.** At the end of FiT Scheme Year 15 (to March 2025) there were 869,659 accredited installations totalling 6.49 GW. Of these, 99.56% are PV and 95.38% are domestic. The scheme closed to new entrants in 2019 ([Ofgem FIT annual report SY15](https://www.ofgem.gov.uk/transparency-document/feed-tariffs-annual-report-scheme-year-15-april-2024-march-2025)). That puts the FiT share of today's ~2.13 m installations at about 41% **[derived]**. Those systems are 6–16 years old, given the scheme ran 2010–2019 **[derived; 2010 start unverified]**. The post-FiT cohort is mostly under 4 years old, because 2023–2026 volumes dominate it. SEG registrations stood at 270,395 installations and 1,585 MW in March 2025, an average of 5.9 kW **[derived]**. Of these, 99.98% are PV ([Ofgem SEG Year 5](https://www.ofgem.gov.uk/transparency-document/smart-export-guarantee-annual-report-april-2024-march-2025)).

**Size distribution.** In 2025/26, almost two-thirds of installations were domestic, 60% of those were 0–4 kW, and over 85% of domestic installations were retrofits ([SPP citing DESNZ cost data, May 2026](https://www.solarpowerportal.co.uk/solar-installations/uk-solar-installations-continue-rising-as-costs-per-kw-drop)). Older FiT systems cluster at 2–4 kWp, and the McKenna study's typical system is 2.9 kWp ([Oxford INET](https://www.inet.ox.ac.uk/publications/solar-photovoltaic-self-consumption-in-the-uk-residential-sector-new-estimates-from-a-smart-grid-demonstration-project)).

**Batteries.**
- MCS-certified battery installations were 20,044 in 2024, more than four times 2023 ([SPP/MCS](https://www.solarpowerportal.co.uk/battery-storage/mcs-bess-and-heat-pumps-drive-record-year-for-small-scale-renewables-in-2024)). In 2025 there were more than 40,000, and more than half of all MCS batteries ever certified were installed that year ([MCS](https://mcscertified.com/the-2026-low-carbon-landscape/)).
- Attachment rate: about 20 batteries per 100 PV systems in the MCS database, per SunWiz. SunWiz argues the true rate is higher because of non-MCS and retrofit installs ([SPP, Nov 2025](https://www.solarpowerportal.co.uk/battery-storage/uk-battery-attachment-rate-far-greater-than-previously-thought-)). On 2025 MCS counts, 40k batteries against 267k PV gives at least 15% **[derived]**. In 2023 it was about 2.5% (~4.9k / 198k) **[derived]**.
- Capacity distribution, DESNZ for April 2024 to March 2025, n = 22,398, newbuild excluded: 9,855 at 1–5.99 kWh, 7,956 at 6–10.99 kWh and 4,587 at 11–29.99 kWh. Total 193.4 MWh, mean about 8.6 kWh ([SPP/DESNZ](https://www.solarpowerportal.co.uk/energy-storage/desnz-over-22-000-domestic-batteries-installed-in-past-year)).

## 2. Generation physics

**Specific yield.**
- The average UK system produced about 770 ± 100 kWh/kWp/yr in the 2006 field trial, rising to about 900 ± 70 kWh/kWp by 2015 (Sheffield Solar, [REF2021 impact case](https://results2021.ref.ac.uk/impact/704fd078-c4db-4ee2-824b-35b8ce2ee1f9/pdf)).
- Regional ranges, unsourced in the original: SE England 1,050–1,200, London/East 950–1,050, Midlands 900–1,000, NW England/NI 850–950, Scotland 800–900 kWh/kWp ([Reonic](https://reonic.com/en-gb/blog/sun-hours-table-solar-pv-potential/); treat as indicative).
- About 1,200 in Cornwall/Kent vs 850–900 in northern Scotland ([Independent via AOL](https://www.aol.com/news/much-electricity-does-solar-panel-090651059.html)).
- IEA PVPS uses 975 kWh/kWp for a European rooftop reference ([IEA PVPS T12](https://iea-pvps.org/wp-content/uploads/2024/05/IEA-PVPS-Task-12-Life-Cycle-Assessment-Fact-Sheet.pdf)).
- A modelled 4 kWp south-facing system in the Midlands gives 3,800 kWh/yr, or 3,040 kWh with moderate shading, a 20% loss ([AOL/Independent](https://www.aol.com/news/much-electricity-does-solar-panel-090651059.html)).

**Orientation and tilt**, relative to south at 30–40°: SE/SW about 90–95%, E/W about 80–85% (EST quotes 15–20% less), NE/NW about 65–75%, N about 55–65% ([EvoEnergy, attributing EST/MCS](https://evoenergy.co.uk/news-updates/best-directions-for-solar-panels/)). A measured north array gave 54% of south (2,457 vs 4,556 kWh) ([SunSave](https://www.sunsave.energy/solar-panels-advice/installation/north-vs-south-facing)). Optimum tilt is 37–38° in southern England and 39–43° further north. Any pitch from 15° to 50° gives over 90% of the maximum for that azimuth ([EvoEnergy](https://evoenergy.co.uk/news-updates/best-directions-for-solar-panels/)). Another source puts the E/W loss at 10–15% ([AOL](https://www.aol.com/news/much-electricity-does-solar-panel-090651059.html)).

**Degradation.** Median 0.5%/yr and mean 0.8%/yr across 2,128 reported rates; about 80% of rates are below 1%/yr ([NREL Jordan & Kurtz](https://www.nrel.gov/docs/fy13osti/56690.pdf)). IEA PVPS assumes 0.7%/yr linear ([IEA PVPS](https://iea-pvps.org/wp-content/uploads/2024/05/IEA-PVPS-Task-12-Life-Cycle-Assessment-Fact-Sheet.pdf)).

**Lifetimes.** Panels 30 years, inverter 15 years ([IEA PVPS](https://iea-pvps.org/wp-content/uploads/2024/05/IEA-PVPS-Task-12-Life-Cycle-Assessment-Fact-Sheet.pdf)). That implies one inverter replacement over a panel life **[derived]**. Inverter conversion efficiency is about 96–97% **[unverified]**. Tesla quotes 97% solar-to-grid ([Powerwall 3 datasheet](https://digitalassets.tesla.com/tesla-contents/image/upload/Powerwall_3_Datasheet_Rev-1_03312023.pdf)).

**Seasonal and daily profile.**
- Winter output is roughly 60–70% below summer. A 400 W panel gives about 0.4–0.6 kWh/day in December–January and 2–3 kWh/day in July ([AOL](https://www.aol.com/news/much-electricity-does-solar-panel-090651059.html)).
- April yield is "surprisingly good", second only to August, in UK solar-farm data ([Palmer et al. 2017, Energies 10:1220](https://dspace.lboro.ac.uk/2134/26255)).
- At grid level, solar was 18.5 TWh and 6.5% of GB generation in 2025, peaking at 42.9% of supply in one half-hour on 12 July 2025 ([Energy Dashboard](https://www.energydashboard.co.uk/insights/2025-review)).
- Day-to-day cloud variability: no fetched GB statistic. See gaps; PV_Live is the instrument for it.

## 3. Self-consumption and export

| Evidence | Self-consumption | Source |
|---|---|---|
| 302 UK homes, 1-min data | 45% of generation (855 kWh/yr); modelled 2.9 kWp / 4,000 kWh home: 966 ± 38 kWh | [McKenna, Pless & Darby 2018](https://www.inet.ox.ac.uk/publications/solar-photovoltaic-self-consumption-in-the-uk-residential-sector-new-estimates-from-a-smart-grid-demonstration-project) |
| Oxford policy brief | ~37%; homes export 55–63%, more than FiT's 50% deemed | [Oxford brief](https://www.renewableenergy.ox.ac.uk/wp-content/uploads/PVSelfConsumption_PolicyBrief.pdf) |
| International, GB subset n = 751 months | GB ~57% (169 of 298 kWh/month) **[derived]**; all countries ~46–49% | [McKenna et al. eceee 2019](https://www.eceee.org/library/conference_proceedings/eceee_Summer_Studies/2019/4-monitoring-and-evaluation-for-greater-impact/analysis-of-international-residential-solar-pv-self-consumption/2019/4-114-19_McKenna.pdf/) |
| SAP 10.2, 3,100 kWh home, 2.5 kWp | 0.40 no battery; 0.65 with 5 kWh; 0.86 with 10 kWh | [BRE S10TP-07](https://bregroup.com/documents/d/bre-group/s10tp-07-pv-self-use-factor-calculation_v1_4) |
| Review | Battery of 0.5–1 kWh/kWp adds 13–24 percentage points; demand-side management adds 2–15 pp | [Luthander et al. 2015](https://ideas.repec.org/a/eee/appene/v142y2015icp80-94.html) |
| SE England trial, 2 kWh battery | ~44% → ~50% (summer), ~40% → ~49% (winter) | [Bruce-Konuah & Gupta](https://radar.brookes.ac.uk/radar/file/ae262e31-b55a-413b-be04-ca07c3ce56b4/1/Using%20smart%20energy%20storage%20to%20increase%20self-consumption%20of%20solar-generated%20electricity.pdf) |

**Usable models.** SAP gives a monthly self-use factor β = exp(−C1·(C2·E/D)^C3), where E is monthly PV generation and D is monthly demand. With no battery, C1 = 1.610, C2 = 0.415 and C3 = 0.511. Each coefficient moves linearly with usable battery kWh: −0.0973, −0.00776 and +0.0866 per kWh. Cap the battery at 15 kWh ([BRE](https://bregroup.com/documents/d/bre-group/s10tp-07-pv-self-use-factor-calculation_v1_4)). The GB empirical regression is self-consumption ≈ 0.626 × daytime demand + 0.390 × generation (kWh/month, R² 0.877).

Occupancy has a large effect. At cover factor 1 (generation equal to demand), self-consumption is about 20% when 10% of demand falls in daytime, and about 80% when 60% does ([eceee 2019](https://www.eceee.org/library/conference_proceedings/eceee_Summer_Studies/2019/4-monitoring-and-evaluation-for-greater-impact/analysis-of-international-residential-solar-pv-self-consumption/2019/4-114-19_McKenna.pdf/)). EST payback tables show the same effect: in London, 10 years for "home all day" vs 12 years for "out until 6pm"; in Belfast, 13 vs 21 years ([MoneyWeek citing EST, Apr 2026](https://moneyweek.com/solar-panels-cost)).

**Diverters and EVs.** A diverter costs £300+ ([MoneyWeek](https://moneyweek.com/solar-panels-cost)). SAP does not model diverters ([BRE](https://bregroup.com/documents/d/bre-group/s10tp-07-pv-self-use-factor-calculation_v1_4)). No fetched figure quantifies the self-consumption uplift from a diverter or an EV (gap).

## 4. Battery behaviour and settings

- **Round-trip efficiency.** Tesla Powerwall 3: 89% solar-to-battery-to-grid at beginning of life and 25 °C. It is 13.5 kWh, 11.5 kW discharge, 5 kW charge, with a 10-year warranty ([datasheet](https://digitalassets.tesla.com/tesla-contents/image/upload/Powerwall_3_Datasheet_Rev-1_03312023.pdf)).
- **Usable vs nominal.** GivEnergy All-in-One: 13.5 kWh usable, 100% depth of discharge, 12-year warranty ([GivEnergy](https://givenergy2025.zohodesk.eu/portal/en/kb/articles/all-in-one-6kw-ac-coupled-datasheet)). An older 2 kWh trial unit had only about 60% usable ([Brookes](https://radar.brookes.ac.uk/radar/file/ae262e31-b55a-413b-be04-ca07c3ce56b4/1/Using%20smart%20energy%20storage%20to%20increase%20self-consumption%20of%20solar-generated%20electricity.pdf)). Nominal and usable are often different on older or cheaper units.
- **Degradation.** The Powerwall warranty guarantees at least 70% of usable capacity at 10 years. Cycles are unlimited for solar self-consumption and time-of-use shifting. Third-party VPP or wholesale use caps the warranty at 37,800 kWh throughput ([SolarQuotes](https://www.solarquotes.com.au/blog/tesla-powerwall-warranty/)). How a battery is set up therefore changes its warranty exposure. A general figure of 2–4%/yr capacity loss and a 10–15-year life is given by [Heatable](https://heatable.co.uk/solar/advice/battery-storage-costs) (secondary source).
- **Modes.** The levers are self-consumption ("eco"), timed grid charge to a target state of charge, timed export, and a reserve floor. GivEnergy schedules are start/end time plus target SoC, set via the portal or app, and portal settings override the app ([GivEnergy KB](https://givenergy2025.zohodesk.eu/portal/en/kb/articles/how-do-i-set-a-charge-schedule)). Third-party control exists through aggregators such as Enode, which publishes a battery-control OpenAPI ([Enode spec](https://enode-api.production.enode.io/openapi/latest.json)); its contents were not inspected.
- **Supplier-controlled optimisation.** Octopus Flux (as of 1 Jul 2026) runs peak 16:00–19:00 and off-peak 02:00–05:00. Birmingham rates: import 37.05 / 15.88p and export 27.81 / 4.39p ([SunSave](https://sunsave.energy/solar-panels-advice/exporting-to-the-grid/octopus-flux)). A later page lists Flux export at 4.99p off-peak, 10.11p other times and 29.32p peak ([SunSave SEG list, 16 Sep 2026](https://sunsave.energy/solar-panels-advice/exporting-to-the-grid/best-seg-rates)). The day import rate is about 26.5p, inferred from off-peak = 0.6 × day and peak = 1.4 × day **[derived]**. Intelligent Octopus Flux sets import equal to export (Birmingham 29.03p peak, 21.77p off-peak). Octopus controls the battery using weather forecasts. Eligible brands: AlphaESS, EcoFlow, Enphase, Fox ESS, GivEnergy, Hanchu, Huawei, Sigenergy, SolarEdge, SunPower, Tesla ([SunSave](https://sunsave.energy/solar-panels-advice/exporting-to-the-grid/intelligent-octopus-flux)).
- **How settings change value.** One full 5 kWh cycle per day, grid-charged off-peak and exported at peak, is worth about 57p/day. Charged from solar that would otherwise export at 10.11p, it is worth about 90p/day. Over a year that is roughly £210–330 from arbitrage alone **[derived, 89% RTE]**. Settings that leave the battery idle in winter, or a high reserve floor, lose most of this.

## 5. Economics

**Installed costs.**
- MCS average solar install: £9,994 (2023), £8,198 (2024), and "just over £7,000" (2025) ([SPP/MCS](https://www.solarpowerportal.co.uk/battery-storage/mcs-bess-and-heat-pumps-drive-record-year-for-small-scale-renewables-in-2024); [MoneyWeek/MCS](https://moneyweek.com/solar-panels-cost)).
- DESNZ median £/kW fell between 2024/25 and 2025/26: −9% (0–4 kW), −8% (4–10 kW), −3% (10–50 kW). Values are inflation-adjusted, and retrofits cost more than newbuild ([SPP](https://www.solarpowerportal.co.uk/solar-installations/uk-solar-installations-continue-rising-as-costs-per-kw-drop)). The absolute £/kW values are in the [DESNZ xlsx](https://ckan.publishing.service.gov.uk/dataset/solar-pv-cost-data/resource/3eb78a5b-a54c-4c33-96f1-2888afd0c9fe), which was not fetchable here.
- Indicative 4 kW cost: £6,000–8,000 ([Heatable](https://heatable.co.uk/solar/advice/solar-costs-government-data); secondary).
- Battery: MCS average £9,343 (2023) and £8,035 (2024) ([SPP/MCS](https://www.solarpowerportal.co.uk/battery-storage/mcs-bess-and-heat-pumps-drive-record-year-for-small-scale-renewables-in-2024)). DESNZ median £/kWh: £1,020 (1–5.99 kWh), £900 (6–10.99 kWh), £590 (11–29.99 kWh) ([SPP/DESNZ](https://www.solarpowerportal.co.uk/energy-storage/desnz-over-22-000-domestic-batteries-installed-in-past-year)).

**VAT.** Roof-mounted solar and other energy-saving materials have been zero-rated since the 2022 Spring Statement. From 1 February 2024 this covers retrofit and standalone batteries. The zero rate ends 31 March 2027 and reverts to 5% ([Wind & Sun](https://www.windandsun.co.uk/blogs/blog/20-vat-scrapped-for-storage); [ICAEW](https://icaew.com/insights/tax-news/2023/dec-2023/energy-saving-materials-relief-extended-from-february-2024)).

**Import price.** The price cap for October–December 2026 is 26.32p/kWh with a 54.83p/day standing charge ([CreditLadder](https://creditladder.co.uk/blog/energy-price-cap-october-2026); the Ofgem page failed to load).

**SEG rates (Sep 2026).** Rates run from 1.05p to 25p ([SunSave](https://sunsave.energy/solar-panels-advice/exporting-to-the-grid/best-seg-rates)):
- Open-to-all tariffs: mostly 3–6p (e.g. Octopus SEG 4.1p, EDF 3p).
- Customer-only tariffs: 8–18p (e.g. Outgoing Octopus 12p, EDF 15p).
- Install-tied tariffs: up to 20–25p, sometimes limited to 12 months.

Realised SEG revenue was £56.97m for 443.1 GWh in Year 5, an average of 12.9p/kWh **[derived]**. Volume has shifted to premium tariffs. There were 50 tariffs from 11 licensees ([Ofgem SEG Y5](https://www.ofgem.gov.uk/transparency-document/smart-export-guarantee-annual-report-april-2024-march-2025)).

**FiT legacy income.** In SY15 there was 8.0 TWh of generation, £1.73bn in generation payments and £94.1m in export payments for 1.5 TWh ([Ofgem](https://www.ofgem.gov.uk/transparency-document/feed-tariffs-annual-report-scheme-year-15-april-2024-march-2025)). That averages 21.6p/kWh for generation and 6.3p/kWh for export **[derived]**. PV up to 30 kW without an export meter is deemed to export 50% of generation-meter readings. Export is valued at the average time-weighted BSC system sell price ([FIT determinations Y16](https://gov.uk/government/publications/feed-in-tariffs-fits-determinations/feed-in-tariffs-fits-determinations-year-16-1-april-2025-to-31-march-2026-accessible-webpage)). Per-vintage generation tariffs (the early tariffs were far above 21.6p and RPI-linked) are **[unverified]**.

**Payback benchmarks.** EST (April 2026) paybacks: London 10–12 years, Manchester 11–13, Stirling 12–15, Belfast 13–21, depending on occupancy ([MoneyWeek](https://moneyweek.com/solar-panels-cost)). An MCS study cited by Heatable puts savings at about £380/yr for PV alone and about £840/yr with a battery ([Heatable](https://heatable.co.uk/solar/advice/battery-storage-costs); secondary).

## 6. Carbon

- **Grid average.** GB intensity was 128.8 gCO₂/kWh in 2025, up 2.1% on 2024 ([Energy Dashboard](https://www.energydashboard.co.uk/insights/2025-review)). DESNZ GHG reporting factors fell about 15% (2025 vs 2024) and about 26% (2026 vs 2025); absolute values were not retrieved ([DESNZ 2025 changes](https://assets.publishing.service.gov.uk/media/6846b6d04d039a010411f0c9/2025-GHG-CF-major-changes-document.pdf); [Circular Ecology](https://circularecology.com/news/desnz-2026-uk-ghg-conversion-factors)).
- A 4 kWp system producing 3,800 kWh/yr displaces about 490 kgCO₂/yr at the 2025 average factor **[derived]**.
- **Average vs marginal.** Midday PV and exports mostly displace gas at the margin, which suggests a higher marginal factor. The Green Book long-run marginal factors ([DESNZ appraisal guidance](https://www.gov.uk/government/publications/valuation-of-energy-use-and-greenhouse-gas-emissions-for-appraisal)) were not extracted. Treat the marginal value as a gap.
- **Battery carbon depends on timing.** Charging at 02:00–05:00 and discharging at 16:00–19:00 saves carbon only if the evening margin is dirtier than the night margin by more than the ~11% round-trip loss **[derived]**.
- **Embodied carbon and carbon payback.** The IEA PVPS reference uses a 3 kWp system, 975 kWh/kWp, 0.7%/yr degradation and a 30-year life ([IEA PVPS](https://iea-pvps.org/wp-content/uploads/2024/05/IEA-PVPS-Task-12-Life-Cycle-Assessment-Fact-Sheet.pdf)), but its numeric gCO₂e/kWh was unreadable in the fetched files. A literature range of about 20–50 gCO₂e/kWh **[unverified]** would give a carbon payback of very roughly 5–12 years at 128.8 g. That payback lengthens as the grid decarbonises **[derived from unverified]**.

## 7. What the supplier can see, infer and must ask

- **See.**
  - Half-hourly import from the smart meter.
  - Half-hourly export only if an export MPAN is registered. SEG tariffs generally need a smart meter plus an MCS or Flexi-Orb certificate ([SunSave](https://sunsave.energy/solar-panels-advice/exporting-to-the-grid/best-seg-rates)). The mechanics of export MPAN registration and settlement are **[unverified; Elexon not fetched]**.
  - As FiT licensee, it receives generation-meter readings and pays deemed export at 50% ([FIT determinations](https://gov.uk/government/publications/feed-in-tariffs-fits-determinations/feed-in-tariffs-fits-determinations-year-16-1-april-2025-to-31-march-2026-accessible-webpage)). Reading frequency (meter reads typically quarterly or six-monthly) is **[unverified]**.
- **Infer.**
  - PV shows as a midday dip in net import that follows irradiance, plus export on clear days.
  - Behind-the-meter disaggregation from net load works with city-level weather and a few proxy PV sites. It infers tilt, orientation and DC rating via SolarTK, though only roughly, and cuts solar nRMSE by 16–32% versus baselines ([Chen et al., arXiv 2105.08122](https://arxiv.org/pdf/2105.08122)).
  - With generation data and off-site irradiance, curve-matching recovers azimuth and tilt to within 4.5° and 4.3° MAE, up to 195 km from the irradiance site, using hourly data ([Meng et al. 2020, Solar Energy 211](https://research.tue.nl/en/publications/data-driven-inference-of-unknown-tilt-and-azimuth-of-distributed-/)).
  - Regional generation (PV_Live) gives a normalised-yield reference ([Sheffield](https://results2021.ref.ac.uk/impact/704fd078-c4db-4ee2-824b-35b8ce2ee1f9/pdf)).
  - A battery shows as near-flat zero import through the evening, square charging blocks in the 02:00–05:00 window, and export spikes at 16:00–19:00 **[unverified pattern logic]**.
- **Must ask or get consent for.** Install date (FiT vintage), kWp, panels per roof plane and azimuth, shading, inverter brand and model (which determines API eligibility), battery usable kWh, mode and reserve, diverter, EV and charger, occupancy, and consent to device-level data.

## 8. Proving savings

- **Metered vs modelled baseline.** A generation meter or inverter API gives true generation. Without one, generation is inferred, and its error carries into the savings claim (see §7 error bounds).
- **Bill comparison.** Before and after net import is confounded by weather, occupancy and tariff changes. Normalise generation to PV_Live regional normalised yield or irradiance. Normalise demand with heating degree days. Compare against a matched control group of non-adopters from the supplier's own book.
- **Attribution.** Separate savings by source: PV self-use, export income, battery shift and tariff change. The Flux switch alone changes bills without any hardware change.
- **Rebound and behaviour change.** Households that shift load into daytime raise self-consumption, but may also raise total use.
- **Deemed vs measured export.** Measured export of 55–63% in [Oxford](https://www.renewableenergy.ox.ac.uk/wp-content/uploads/PVSelfConsumption_PolicyBrief.pdf) means FiT's deemed 50% is biased.

No GB-specific measurement-and-verification protocol was fetched (gap; IPMVP is the usual reference **[unverified]**).

---

## (a) Headline figures and bands to check a simulated world against

| Quantity | Band | Source |
|---|---|---|
| GB PV installations (Aug 2026) | ~2.13 m; 23.2 GW all sizes | DESNZ via [SPP](https://www.solarpowerportal.co.uk/solar-installations/uk-installs-record-291-000-new-solar-pv-installations-in-12-month-period) |
| FiT share of installations | ~41% (869,659) | [Ofgem](https://www.ofgem.gov.uk/transparency-document/feed-tariffs-annual-report-scheme-year-15-april-2024-march-2025) **[derived]** |
| New domestic system size 2026 | ~5–6 kWp mean; 60% ≤4 kW (2025/26) | [SPP](https://www.solarpowerportal.co.uk/solar-installations/uk-solar-installations-continue-rising-as-costs-per-kw-drop) |
| Specific yield | 800–1,200 kWh/kWp; fleet ~900 ± 70 | [Sheffield](https://results2021.ref.ac.uk/impact/704fd078-c4db-4ee2-824b-35b8ce2ee1f9/pdf), [Reonic](https://reonic.com/en-gb/blog/sun-hours-table-solar-pv-potential/) |
| E/W, N factor vs S | 0.80–0.85; 0.54–0.65 | [EvoEnergy](https://evoenergy.co.uk/news-updates/best-directions-for-solar-panels/) |
| Degradation | 0.5–0.8 %/yr | [NREL](https://www.nrel.gov/docs/fy13osti/56690.pdf) |
| Self-consumption, no battery | 28–57% (typically 37–45%) | §3 |
| Self-consumption, with ~5 kWh | +13–25 pp (SAP: 0.40 → 0.65) | [BRE](https://bregroup.com/documents/d/bre-group/s10tp-07-pv-self-use-factor-calculation_v1_4) |
| Battery attachment, new PV | ~15–20%+ (2025) | [SPP](https://www.solarpowerportal.co.uk/battery-storage/uk-battery-attachment-rate-far-greater-than-previously-thought-) |
| Battery size, mean | ~8.6 kWh | [DESNZ](https://www.solarpowerportal.co.uk/energy-storage/desnz-over-22-000-domestic-batteries-installed-in-past-year) |
| Round-trip efficiency | ~89% | [Tesla](https://digitalassets.tesla.com/tesla-contents/image/upload/Powerwall_3_Datasheet_Rev-1_03312023.pdf) |
| PV cost (avg install) | ~£7k (2025) | [MCS/MoneyWeek](https://moneyweek.com/solar-panels-cost) |
| Battery £/kWh | £590–1,020 | [DESNZ](https://www.solarpowerportal.co.uk/energy-storage/desnz-over-22-000-domestic-batteries-installed-in-past-year) |
| SEG rate | 1–25p; realised avg 12.9p | [SunSave](https://sunsave.energy/solar-panels-advice/exporting-to-the-grid/best-seg-rates), [Ofgem](https://www.ofgem.gov.uk/transparency-document/smart-export-guarantee-annual-report-april-2024-march-2025) **[derived]** |
| EST payback | 10–21 yr | [MoneyWeek/EST](https://moneyweek.com/solar-panels-cost) |
| Grid average intensity 2025 | 128.8 g/kWh | [Energy Dashboard](https://www.energydashboard.co.uk/insights/2025-review) |

## (b) What the world needs to model (hidden attributes per home)

- **Per roof plane:** kWp, azimuth, tilt, shading profile (monthly or hourly loss).
- **System:** install date (FiT tariff vintage or SEG), panel degradation rate, inverter efficiency, inverter install and failure date, inverter AC clip limit.
- **Location:** irradiance cell or region, plus a daily cloud series correlated across nearby homes.
- **Battery:** nominal and usable kWh, charge and discharge kW, round-trip efficiency, capacity fade, mode, reserve SoC, charge and export windows, controller (none, app, or supplier/aggregator), and whether it has API access.
- **Other kit:** diverter, hot-water tank, EV and charger schedule, heat pump.
- **Household:** occupancy archetype (home all day through out until 6pm), annual demand and its half-hourly shape.
- **Metering and tariffs:** generation meter present, export MPAN registered, tariff (flat, SEG rate, Flux or iFlux), FiT licensee.

## (c) What the supplier can observe, infer and must ask

| Attribute | Observe | Infer (method, error) | Ask |
|---|---|---|---|
| PV present | Export reads if registered | Midday net-import dip ([arXiv 2105.08122](https://arxiv.org/pdf/2105.08122)) | Confirm |
| kWp | FiT/MCS record if held | From net load, rough | Yes |
| Orientation/tilt | – | ±4.5°/4.3° with generation data ([Meng 2020](https://research.tue.nl/en/publications/data-driven-inference-of-unknown-tilt-and-azimuth-of-distributed-/)); coarse from net load | Yes |
| Generation | FiT generation meter (if licensee); inverter API (consent) | Disaggregation | – |
| Export | HH export (if MPAN) | Deemed 50% (FiT) is biased | – |
| Battery present/size | API (consent) | Evening flatline, charge blocks **[unverified]** | Yes |
| Battery settings | API (consent) | Partly from timing | Yes |
| Inverter brand | – | – | Yes (determines iFlux eligibility) |
| Install date / FiT | FiT records if licensee | – | Yes |
| Occupancy | – | Daytime base load | Yes |

## (d) Worked payback archetypes **[derived]**

Assumptions:
- Generation: 950 kWh/kWp, so 3,800 kWh for 4 kWp south. E/W is 0.82× that.
- Demand: 3,100 or 4,200 kWh. Monthly PV and demand shapes are **[unverified]**.
- Self-consumption: SAP β model applied monthly.
- Import: 26.32p flat. Standing charge excluded.
- Costs: PV £7,000; 5 kWh battery £5,100 (DESNZ median).
- Flux case: Birmingham rates, one 5 kWh cycle per day, 1.5 kWh/day home use in the peak window, round-trip efficiency 89%.
- Not included: degradation, inverter replacement, price drift.

| Archetype (3,100 kWh home) | Self-use | Saving/yr | Simple payback |
|---|---|---|---|
| 4 kWp S, no battery, SEG 4.1p | 28% | £394 | 17.8 yr |
| 4 kWp S, no battery, SEG 12p | 28% | £609 | 11.5 yr |
| 4 kWp S + 5 kWh, SEG 4.1p | 50% | £575 | 21.0 yr |
| 4 kWp S + 5 kWh, SEG 12p | 50% | £726 | 16.7 yr |
| 4 kWp S + 5 kWh, Flux | – | £857 | 14.1 yr |
| 4 kWp E/W, no battery, SEG 12p | 32% | £515 | 13.6 yr |
| 4 kWp E/W + 5 kWh, SEG 12p | 56% | £622 | 19.4 yr |
| 4 kWp E/W + 5 kWh, Flux | – | £768 | 15.8 yr |
| 4,200 kWh home: S no battery SEG 12p / S + 5 kWh Flux | 34% / – | £639 / £892 | 11.0 / 13.6 yr |

What the table shows:
- The export tariff matters as much as the hardware. Moving from 4.1p to 12p cuts payback by about 6 years.
- A battery adds only about £150–180/yr on flat SEG. Most of its value comes from tariff arbitrage (Flux).
- E/W loses about 15% of savings but has slightly higher self-use.

These paybacks are longer than EST's 10–13 years for England. That gap is a calibration item: it may come from EST's assumptions, from the SAP β model under-stating self-use for E/W profiles, or from the costs used.

## (e) Named gaps

1. PVGIS per-region, per-azimuth yields: the API was blocked. Re-run it for a proper orientation and tilt matrix and monthly profiles. The monthly shares used above are **[unverified]**.
2. Absolute DESNZ median £/kW time series (xlsx not fetchable) and a battery cost time series before 2023.
3. Elexon or BSC detail on export MPAN registration, SVA settlement of export, and the share of PV homes with registered export (SEG has 270k registered, against roughly 2.1 m installations in total).
4. Day-to-day cloud variability statistics (PV_Live distribution); fleet shading prevalence.
5. Measured GB self-consumption uplift from diverters and EVs; occupancy-archetype distribution.
6. Marginal emission factors (Green Book) and DESNZ 2026 absolute factors; numeric PV embodied carbon (IEA PVPS value unreadable).
7. Tesla, Solis and GivEnergy API specifications and rate limits; Axle and other VPP payment levels; Intelligent Flux realised savings; Demand Flexibility Service values.
8. NESO FES projections for domestic PV and battery uptake.
9. FiT generation tariff by vintage, and the reading frequency the FiT licensee receives.
10. A GB-specific measurement-and-verification protocol for PV and battery savings claims; field measurements of battery standby losses and real-world round-trip efficiency.
11. Which? independent cost and satisfaction survey data. The search budget was exhausted before Which?, Solar Energy UK, BRE field data beyond SAP, and Energy Systems Catapult could be reached. A follow-up turn could fill these.

**Files:** the payback model is at /tmp/claude-0/-home-claude/90c98f50-d921-54a8-854d-66c80c7b13b3/scratchpad/calc/pb.py.

## Done

Published on 25 Oct as the Knowledge page `site/knowledge/solar-pv-and-home-batteries/`, with the note `docs/market_research/solar_pv_and_home_batteries_2026-10-25.md`. The note carries the verification pass that the 25 Oct verify steer asks for: each [unverified] item is marked confirmed, corrected or still open, and no open item is stated on the page as a claim. Counts as recorded: Counts: 9 items; 1 confirmed, 0 corrected, 8 still open (one of them half closed). Sourced figures
