**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] Primary-source verification of the 21 GB packs' [unverified] items (2026-10-25)

**Type:** EVIDENCE, sent through the advisor channel. The director's words from chat, Sun 25 Oct:

- 21:17 GMT: "Sorry I was delayed. It's 61% now. But time has passed."
- 07:52 GMT: "Why did search budgets run out? How can we solve this?"

The advisor ran three verification passes, at most three at a time, reading primary pages directly and using few searches. Between them they covered every `[unverified]` tag in the 21 GB evidence packs of 25 Oct. **145 items were checked: 75 confirmed, 22 corrected, 42 still open, 6 need a file.**

## What to do with it

1. **Apply the outcomes to the published Knowledge pages and their tallies.** Each item is marked confirmed, corrected, still open or needs-file. Where your own check disagrees with the advisor's, your primary-source read wins, and the record should note the difference.
2. **Corrections that move numbers or rules.** Find these in the pages, world claims, population checks and constants, and fix them:
   - **Smart meter data under MHHS.** New-system domestic meters default to half-hourly data, and the customer can opt out to daily. Old-system meters default to daily. The consent-state model must follow SLC 47 as modified in 2022, not a generic monthly/daily/HH ladder.
   - **Private rented sector.** EPC C by 1 Oct 2030 is confirmed policy (Jan 2026), with a £10k cap and a 10%-of-value exemption below £100k.
   - **Warm Homes Plan.** It is £15bn, not £13.2bn. ECO's end date is contested: Mar 2026 or extended to Dec 2026. Check which.
   - **VAT on public EV charging.** The tribunal in *Charge My Street* [2026] UKFTT 318 held it should be 5%, and HMRC is appealing. Model it as a scenario parameter, not a constant.
   - **RTS switch-off.** It went in groups of meters from 30 Jun 2025, not region by region. The pack's completion figure stands.
   - **Off-street parking.** The 65% figure, Westminster 7% and Flintshire 84% are from the RAC Foundation *Standing Still* report (2021). Its per-local-authority PDF is the lookup to use. The DfT/Ipsos tracker says 91% of BEV drivers can charge at home. No public-only share is published (Zapmap's 2025 survey says 23% have no home charging).
   - **EVHS grant caps.** They ran £900, then £700, then £500, then £350. The early Leaf onboard charger was 3.3 kW.
   - **PHE 2014 review.** The temperature bands recalled earlier are not in the review. The review says 18°C or above poses minimal risk, blood pressure risk rises below 18°C and more so below 16°C, and the evidence is weak. The health-floor rules stand on this basis.
   - **Filter and system clean.** This became mandatory with the 2022 Part L uplift, not Boiler Plus 2018.
   - **Heat pumps and fabric.** Cavity insulation costs £1,000–3,000, so payback is about 12–37 years. A heat pump takes 1–3 days on site. A boiler replacement costs £1,500–3,000.
   - **PV.** Embodied carbon is a median of about 45 g/kWh at 1,700 kWh/m². At UK irradiation that is about 70 g for older modules, so the carbon payback is longer than the 5–12 years stated. FiT indexation moves from RPI to CPI from April 2026.
   - **BS 7671.** The prosumer chapter came in with A2:2022. A3:2024 added bidirectional devices. Battery requirements are slated for A4:2026.
   - **CMA detriment.** It averaged £1.4bn a year over 2012–15, rising to almost £2bn in 2015. The RMR permitted discounts were dual fuel, online account management and dividend payments. Confirm that last point against the PDF.
   - **SLC 27.15.** The 2022 notice's new text still appears to say "all reasonable steps". Check the consolidated licence before treating the duty as absolute.
3. **Needs-file items are fetches for you.** The advisor's sandbox couldn't reach them. Two examples: HMRC MPT_Tab_Sep_26.ods (property transactions) and DfT NTS0901/0904 and TRA0305 (.ods). The full list is in each pass below.
4. **Still-open items stay open.** Where no source exists, record that as a finding.

The other-markets packs are being checked the same way, two countries per pass, and will arrive as a separate file.


---

# Verification pass: Flexibility roadmap, EVs, VPPs

# Verification report: three Poesys evidence packs (25 Oct 2026)

I checked 40 [unverified] items: 19 confirmed, 8 corrected, 11 still open, 2 need a file someone has to download. I used about 33 web searches. The sandbox only allowed fetching URLs that were already in the packs or came back from a search, so several gov.uk pages had to be reached through mirrors or secondary sources. Notes say where that happened.

---

## Pack 1: DIRECTOR_EVIDENCE_HOUSEHOLD_FLEXIBILITY_AND_THE_ADVICE_ROADMAP_2026-10-25.md

| # | Item | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Smart Charge Points Regs 2021: default off-peak hours, random delay up to 600 s, security aligned with ETSI EN 303 645 | CONFIRMED | – | https://legislation.gov.uk/uksi/2021/1467/part/2/made?view=plain ; https://govukdiff.njk.onl/update/2022-10-27T09:45:00+01:00/www.gov.uk/guidance/regulations-electric-vehicle-smart-charge-points | Reg 11: 600 s by default, must be able to delay up to 1,800 s. The Schedule 1 text never names ETSI. The gov.uk guidance (read via a mirror) says the rules are "consistent with ETSI EN 303 645". |
| 2 | About 1.5–2m homes rely mainly on electric heating; about 4m+ on Economy 7-type meters | CONFIRMED (partly) | 1.4m homes have storage heating; about 4m have Profile Class 2 meters | https://sustainabilityfirst.org.uk/images/Economy_7_and_the_price_cap_final_120123_PWP.pdf | Secondary source quoting Ofgem/CMA and the housing surveys. Not every Profile Class 2 meter is on a multi-rate tariff. Total homes with electric main heating (including direct-acting) is not sourced. |
| 3 | RTS switch-off began mid-2025, region by region | CORRECTED | Began 30 Jun 2025, switched off in groups of meters, not all at once. Ofgem does not describe regional phasing. About 300k RTS meters were left in Jul 2025 (about 900k in Jan 2024). | https://www.ofgem.gov.uk/news/support-energy-suppliers-during-rts-switch | – |
| 4 | Quantum-type storage heaters cut running costs (no figure) | CONFIRMED | Manufacturer claims "up to 27% cheaper to run" | https://www.dimplex.co.uk/en-gb/news/mythbusters-quantum-vs-night-storage-heaters | Manufacturer claim only. |
| 5 | Hot water is about 15–20% of home heating energy | STILL OPEN | – | – | No EST or DESNZ page found. |
| 6 | Many cylinders were removed in combi conversions | STILL OPEN | – | – | – |
| 7 | Induction about 85–90% efficient vs gas hob about 40% | STILL OPEN | – | https://www.currys.co.uk/gbuk/techtalk/what-are-the-advantages-of-induction-hobs/ | Only a retailer page backs it (84–90% vs 40%, credited to NEF). |
| 8 | Standby about £50/yr | STILL OPEN | – | https://gloucestershire.gov.uk/planning-and-environment/greener-gloucestershire-dashboard/useful-information/campaigns/current-campaigns/saving-energy-at-home/the-rest-of-the-house | Council page says "up to £70" for an average home and £147 for high users (British Gas). Not EST. |
| 9 | CMA 2016: about £1.4bn/yr detriment | CONFIRMED | £1.4bn/yr more than in a fully competitive market | https://mondovisione.com/news/competition-and-markets-authority-publishes-final-energy-market-reforms-2016624/ | Republished CMA press release. |
| 10 | Data access: monthly by default, daily on opt-out, half-hourly only with opt-in | CORRECTED | The SLC 47 rules for settlement differ: old-system domestic meters are daily by default (customer can opt in to HH or out to monthly); under MHHS, domestic meters are HH by default with opt-out to daily. The pack's monthly/daily/HH ladder may still apply to non-settlement uses, but no fetched source confirms it. | https://www.ofgem.gov.uk/sites/default/files/2022-09/Decision%20on%20Modifying%20SLC%2047%20of%20the%20electricity%20supply%20licence.pdf | Affects the consent-state model in roadmap topic E. |
| 11 | About two-thirds of meters are smart or advanced | CONFIRMED | 39m smart of about 54m domestic meters at large suppliers (73% smart); about 36m in smart mode (about 66%), end Jun 2026 | https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin | Domestic advanced-meter count not given separately. |
| 12 | About 4m+ electricity prepayment meters | CONFIRMED | About 4m GB homes on pay-as-you-go | https://www.which.co.uk/reviews/cutting-your-energy-bills/article/is-a-prepayment-energy-meter-right-for-you | Secondary (Which?, Aug 2026); no split by fuel. |
| 13 | Ofgem tightened involuntary installations in 2023 | CONFIRMED | Code of practice, Apr 2023: bans for over-85s with no other support, people needing continuous supply for health reasons, and others | https://www.wrekin.com/News/money-matters-new-rules-for-the-installation-of-prepayment-energy-meters | Secondary source. Date the licence conditions took effect is not confirmed. |
| 14 | Warm Home Discount is £150 | CONFIRMED | £150 for winter 2026/27 (qualifying date 23 Aug 2026) | https://www.ageuk.org.uk/information-advice/money-legal/benefits-entitlements/warm-home-discount | Secondary; gov.uk was blocked. |
| 15 | Warm Homes Plan about £13.2bn and replaces bill-funded ECO | CORRECTED | £15bn plan launched 20 Jan 2026. £13.2bn was the Spending Review figure. ECO ends and the money moves to general taxation. DESNZ consulted on extending ECO4 to 31 Dec 2026. | https://www.cic.org.uk/news/governments-warm-homes-plan-finally-released ; https://www.elmhurstenergy.co.uk/blog/2025/11/27/eco-scheme-to-end-after-march-2026/ | – |
| 16 | MEES minimum EPC E, £3,500 cap | CONFIRMED | – | https://www.cambridge.gov.uk/minimum-energy-efficiency-standards-in-private-rented-accommodation | – |
| 17 | Proposed path: EPC C by 2030, £10,000 cap | CORRECTED (status) | Confirmed policy (Jan 2026), no longer just proposed: EPC C by 1 Oct 2030, £10k cap, and a property-value exemption capping spend at 10% of value for homes under £100k | https://www.elmhurstenergy.co.uk/blog/2026/01/22/domestic-private-rented-properties-required-to-meet-epc-band-c-by-october-2030/ | Secondary; England and Wales. |
| 18 | Private rented sector about 19% of English households | CONFIRMED | 19% (EHS 2024-25) | https://www.gov.uk/government/statistics/chapters-for-english-housing-survey-2024-to-2025-headline-findings-on-demographics-and-household-resilience/introduction-and-key-findings | – |
| 19 | About 1m+ housing transactions a year | NEEDS-FILE | – | https://gov.uk/government/publications/monthly-property-transactions-completed-in-the-uk-with-value-40000-or-above/uk-monthly-property-transactions-commentary | Sum the last 12 months of residential transactions in MPT_Tab_Sep_26.ods. |
| 20 | EPC required at sale and let | CONFIRMED | Valid for 10 years | https://gov.uk/buy-sell-your-home/energy-performance-certificates | – |
| 21 | New EPC metrics and the Home Energy Model replace SAP from about 2026 | CORRECTED | HEM replaces SAP for new-build Part L compliance (annex says "from 2025"). HEM for existing homes and EPCs is still being developed, with no date. Proposed headline EPC metrics: fabric, heating system, smart readiness, cost. | https://gov.uk/government/consultations/reforms-to-the-energy-performance-of-buildings-regime/technical-annex-for-chapter-2-what-epcs-measure | The timetable may have slipped. |
| 22 | About 14,000 networks serving about 0.5m consumers | CONFIRMED (partly) | 14,000 heat networks (UK) | https://cms.law/en/gbr/legal-updates/regulating-heat-networks-a-new-era | The 0.5m consumer figure is still open. |
| 23 | Ofgem heat network regulation started Jan 2026 | CONFIRMED | 27 Jan 2026 | https://www.ofgem.gov.uk/blog/countdown-launch-new-regulatory-rules-heat-networks | – |
| 24 | About 3–5% of homes have air conditioning | CONFIRMED | 4.3% of English homes (about 1.06m), EHS 2023-24 | https://www.reading.ac.uk/news/2026/Research-News/The-most-at-risk-from-heat-have-the-least-air-con | – |
| 25 | PAS 2035 mandatory for ECO and GBIS | CONFIRMED | Measures need a TrustMark Certificate of Lodgement, which is only issued if PAS 2030/2035 is met | https://www.trustmark.org.uk/tradespeople/quality-assurance-guidance-government-funded-schemes | – |
| 26 | Ofgem Standards of Conduct apply | CONFIRMED | Supply licence condition 0 (domestic) and 0A (non-domestic) | https://www.ofgem.gov.uk/sites/default/files/2023-11/Draft%20Update%20to%20Standards%20of%20Conduct%20Guidance.pdf | – |

**Pack 1 totals:** 26 items. 16 confirmed, 5 corrected, 4 still open, 1 needs a file.

**Also worth noting:** the pack says ECO4 runs to 31 Dec 2026. Elmhurst (Nov 2025) said ECO would end in Mar 2026, and CIC says the extension to Dec 2026 was only consulted on. Someone should check whether the extension was confirmed.

---

## Pack 2: DIRECTOR_EVIDENCE_EVS_CHARGING_AND_SAVINGS_VS_PETROL_AND_DIESEL_2026-10-25.md

| # | Item | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 1 | 2022 PHEV share about 6.3% | CONFIRMED | 6.3% of 1.614m registrations (about 102k) | https://www.fleetnews.co.uk/news/manufacturer-news/2023/01/05/2022-s-new-car-market-ends-2-down | Fleet News reporting SMMT figures. |
| 2 | Efficiency by segment: small cars about 4 mi/kWh, large SUVs about 2.5 | STILL OPEN | – | – | – |
| 3 | About 7,000 miles a year per car (NTS) | NEEDS-FILE | – | https://gov.uk/government/statistical-data-sets/nts09-vehicle-mileage-and-occupancy | Needs table NTS0901 (.ods). The NTS 2024 factsheet only gives 6,082 miles per person across all modes. |
| 4 | Typical household uses 2,700 kWh/yr (Ofgem TDCV) | CORRECTED | **2,500 kWh** electricity (gas 9,500) from 1 Jul 2026; 2,700/11,500 was the 2023 value | https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf | With 2,500 kWh as the base, an EV adds about 70–132%, not 65–120% [derived]. Ofgem's consumer advice page still says 2,900 kWh, which conflicts. |
| 5 | Usual VAT gap: 5% on home electricity vs 20% on public charging | CORRECTED | Home electricity is **0% VAT** from 1 Oct 2026 to 31 Mar 2027 (gas stays 5%). Public charging is 20% under HMRC Notice 701/19, but a tribunal (*Charge My Street v HMRC* [2026] UKFTT 318) held it is in principle 5%. HMRC says it will appeal (Revenue and Customs Brief 4/2026). | https://www.ofgem.gov.uk/publications/changes-energy-price-cap-between-1-october-and-31-december-2026 ; https://www.simmons-simmons.com/en/publications/cmmuhuw5j00jwtvk4jvo7lgpi/supplies-of-public-ev-charging-and-vat | The VAT rate on public charging is unsettled, so model it as a scenario parameter. |
| 6 | Diesel economy 55 mpg | STILL OPEN | – | – | No authoritative fleet-average mpg found. |
| 7 | Gas CCGT marginal factor about 0.35–0.40 kgCO2/kWh; overnight intensity usually below the daily average | CONFIRMED (first part) | CCGT 394 gCO2/kWh (OCGT 651, coal 937) | https://www.neso.energy/document/373951/download | NESO's factor is an average-efficiency generation factor, not a marginal one. The overnight claim is still open. |
| 8 | On-street chargepoint grant details | CONFIRMED | 75% of cost up to £500. Needs a permanent cross-pavement solution, highways approval, and no private off-street parking. Closes 31 Mar 2027. | https://www.find-government-grants.service.gov.uk/grants/electric-vehicle-chargepoint-grant-for-households-with-on-street-parking-1 | – |
| 9 | GB confounders (immersion, storage heaters and so on) | STILL OPEN | – | – | No GB disaggregation study found. |
| 10 | 70–80% of charging energy at home | STILL OPEN | – | – | – |
| 11 | MOT mileage accessible to a supplier | STILL OPEN | – | https://documentation.history.mot.api.gov.uk/ | A DVSA MOT history API exists (JSON, registration required). The fetched pages did not show the odometer field or who is eligible. |
| 12 | VED £195/yr for both EVs and petrol cars after year one, apart from CO2-band differences | CORRECTED | £195 standard rate (2025) is confirmed. But cars registered after Apr 2017 have **no CO2-band difference after year one**; CO2 only sets the first-year rate. Expensive-car supplement over £40k list price. | https://www.westyorkshire.police.uk/ask-the-police/question/Q01278 | Secondary; gov.uk rate tables were blocked. The 2026/27 uprating was not checked. |

**Pack 2 totals:** 12 items. 3 confirmed, 3 corrected, 5 still open, 1 needs a file.

---

## Pack 3: DIRECTOR_EVIDENCE_VPPS_THIRD_PARTY_FLEX_AND_LOCAL_NETWORK_PAYMENTS_2026-10-25.md

| # | Item | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 1 | BL01 lookback is "10 of the last 10 like-days" | STILL OPEN | – | https://bscdocs.elexon.co.uk/category-3-documents/baselining-methodology-document | The page only shows the contents list. The rule sits in §3.4.1 (Step 1) of the downloadable document. |
| 2 | Product mapping: Sustain → SU/PR, Secure → SAOU, Dynamic → VAOU, Restore → OU | STILL OPEN (one source contradicts it) | – | https://ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/ssen-service-terms-aligned-to-fsa-manualv4.pdf | No published mapping found in the ENWL guide or SSEN webinars. An example tender row in an SSEN manual is labelled "Operational Utilisation + Variable Availability (Secure)", which puts Secure under VAOU, not SAOU. Ask flexibilityprocurement@sse.com or check the ENA Open Networks product definitions. |

**Pack 3 totals:** 2 items. 0 confirmed, 0 corrected, 2 still open.

---

## Overall

**40 items: 19 confirmed, 8 corrected, 11 still open, 2 need a file.**

The corrections that change the numbers:
- **Typical household electricity:** 2,500 kWh from 1 Jul 2026, not 2,700.
- **VAT:** 0% on home electricity from Oct 2026 to Mar 2027, and the rate on public charging is being disputed in the tribunal.
- **Warm Homes Plan:** £15bn, not £13.2bn.
- **MEES:** EPC C by 1 Oct 2030 is now confirmed policy.
- **Smart meter data:** the half-hourly consent rules are different under MHHS settlement.
- **RTS switch-off:** done in groups of meters, not region by region.

**Files for someone with network access:**
- HMRC MPT_Tab_Sep_26.ods, from the monthly property transactions page, for item 19 in pack 1.
- DfT NTS0901 and NTS0904, from the nts09-vehicle-mileage-and-occupancy page, for item 3 in pack 2.
- The full Elexon Baselining Methodology Document download, for the BL01 rule.

---

# Verification pass: Drivers, vehicles, roofs, costs, gap closure, payments, accounts, switching, vulnerability

# Verification of [unverified] items, nine Poesys evidence packs (25 Oct 2026)

I checked 49 tagged items. Some packs repeat the same claim in the body and the tables; I list those once. Many sources were off limits: gov.uk ODS/XLSX files, the Carbon Intensity API, Wikipedia and legislation.gov.uk (except one explanatory memorandum).

## 1. DRIVERS_MILEAGE_AND_PARKING_DISTRIBUTIONS

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | "roughly a quarter to a third of workers are hybrid" | CONFIRMED | 28% of working adults in GB were hybrid in autumn 2024 (OPN, 2–27 Oct 2024); 27% in Apr–Jun 2024 | https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/articles/whoarethehybridworkers/latest | Not retrieved: fully remote and fully on-site shares |
| 2 | TRA0305 profile "about ±8–10% amplitude, Jan/Dec trough, summer peak" | NEEDS-FILE | — | https://www.gov.uk/government/statistical-data-sets/road-traffic-estimates-tra (TRA0305 .ods) | |
| 3 | "DfT/OZEV estimate ~65% of homes have off-street parking, 7% Westminster to 84% Flintshire" | CORRECTED | The figures are right but the source is wrong. They come from the RAC Foundation *Standing Still* report (June/July 2021), not DfT/OZEV. It finds 65% of GB's 27.6m households have, or could have, off-street parking (England 68%, London 44%, Wales 75%). By local authority: Westminster 7%, Flintshire 84% (tied with Knowsley and St Helens), City of London 0% | https://www.racfoundation.org/media-centre/cars-parked-23-hours-a-day ; https://www.racfoundation.org/wp-content/uploads/standing_still_off_street_parking_by_LA_A-Z.pdf | The local-authority PDF is the per-LA lookup the simulation needs |
| 4 | Zapmap "about 9m households without off-street parking" | CONFIRMED | More than 9 million GB households (Zapmap, 29 Jul 2022) | https://www.zapmap.com/news/ev-drivers-off-street-parking-research | Zapmap gives no underlying source for the figure |
| 5 | RAC Foundation "Standing Still" parking report (that it exists) | CONFIRMED | June 2021 report; press release 8 Jul 2021 | as #3 | Gives no split by dwelling type or tenure |
| 6 | English Housing Survey (EHS) parking by dwelling type and tenure | STILL OPEN | — | — | Not reached |
| 7 | "DfT EV tracker: ~90% of BEV drivers have off-street parking, ~9% public-only" | CORRECTED | DfT/Ipsos 12-month diary study: 91% of BEV drivers and 88% of PHEV drivers *can charge at home*; 76% of BEV drivers have a wallbox. No public-only share is published. The nearest figure is Zapmap's 2025 survey: 23% of BEV drivers have no home charging | https://forecourttrader.co.uk/news/government-study-finds-90-of-ev-drivers-can-charge-at-home/709930.article ; https://www.zapmap.com/news/ev-charging-survey-2025-results | Measures home-charging access, not parking |
| 8 | Expected direction: detached/semi high, terraces/flats low, owners above renters, rural above urban | STILL OPEN | — | — | Needs EHS data |
| 9 | Long trips "about 6–12 per year per driver" | STILL OPEN | — | — | This is a design assumption |
| 10 | "±8% sinusoid with a summer peak" placeholder | NEEDS-FILE | — | as #2 | Same claim as #2 |
| 11 | "flats and terraces drive most of the variation" | STILL OPEN | — | — | Same gap as #8 |

**Totals:** 3 confirmed, 2 corrected, 4 still open, 2 needs-file (11 items).

## 2. VEHICLE_MIX_AND_REAL_WORLD_EFFICIENCY

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | "Northern Ireland is about 3% of the UK car fleet" | NEEDS-FILE | — | https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-tables (by-nation tables, e.g. VEH1104) | The VLS 2024 HTML page gives only the UK total (33,967k) |
| 2 | Older private parc (Leaf, Zoe, i3) "roughly 22–62 kWh" | CONFIRMED (approx.) | Leaf 2011–13: 24 kWh gross / 22 usable. Leaf 40: 40 / 39. Zoe ZE50: 54.7 / 52. i3 120Ah: 42.2 / 37.9 | https://ev-database.org/uk/car/1011/Nissan-Leaf ; https://ev-database.org/uk/car/1106/Nissan-LEAF-40-kWh ; https://ev-database.org/uk/car/1205/Renault-Zoe-ZE50-R135 ; https://ev-database.org/uk/car/1145/BMW-i3-120-Ah | Not checked: Leaf e+ 62 kWh and the early i3 battery |
| 3 | "parc-weighted mean likely below 60 kWh" | STILL OPEN | — | — | Needs VEH0141 joined to battery specs |
| 4 | EV Database consumption figures "are battery-side" | STILL OPEN (supported) | EV Database says "Rated consumption… include[s] charging losses". It defines "Vehicle consumption" as battery energy only. The real-world figures carry no label either way | https://ev-database.org/uk/car/1106/Nissan-LEAF-40-kWh ; https://ev-database.org/uk/car/1205/Renault-Zoe-ZE50-R135 | Battery-side is a reasonable reading, but the site never states it |
| 5 | Older PHEVs "about 9–14 kWh gross for about 30–60 km WLTP" | CONFIRMED (one model) | Outlander PHEV: 12 kWh (2014–18), 13.8 kWh (2019+), 45 km WLTP / 54 km NEDC | https://www.automobile-propre.com/voitures/mitsubishi-outlander-phev/autonomie | Single-model check only |
| 6 | "Other 2025 top-10 models: all 11 kW" | STILL OPEN | — | — | Only the Model Y is confirmed (in the pack) |
| 7 | "Leaf 6.6 kW (3.6 kW on early cars)" | CORRECTED | The early Leaf had 3.3 kW as standard (6.6 kW optional). Leaf 40 MY18–22 has 6.6 kW | https://ev-database.org/uk/car/1011/Nissan-Leaf ; https://ev-database.org/uk/car/1106/Nissan-LEAF-40-kWh | |
| 8 | "Zoe 22 kW" | CONFIRMED | ZE50 R135: 22 kW AC, needs 3-phase | https://ev-database.org/uk/car/1205/Renault-Zoe-ZE50-R135 | |
| 9 | "i3 7.4–11 kW" | CONFIRMED (partly) | i3 120Ah: 11 kW (3-phase 16 A) | https://ev-database.org/uk/car/1145/BMW-i3-120-Ah | 7.4 kW on earlier i3s not checked |
| 10 | "MG4/MG ZS about 6.6–7 kW" | STILL OPEN | — | — | Fleet News blocked by robots |
| 11 | Single-phase home charging capped at about 7.4 kW (32 A) | CONFIRMED | EV Database: on most single-phase homes "the practical limit is 7.4 kW" | https://ev-database.org/uk/car/1145/BMW-i3-120-Ah | |

**Totals:** 5 confirmed, 1 corrected, 4 still open, 1 needs-file (11 items).

## 3. ROOFS_PV_ORIENTATION_YIELD_AND_IRRADIANCE

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Killinger 2018 UK cluster "around 30–40° tilt, centred on south" | STILL OPEN | — | — | Needs the paper's full text |
| 2 | 3.68 kW = G98 single-phase limit of 16 A per phase | CONFIRMED | 16 A per phase = 3.68 kW single phase (11.04 kW three phase) | https://www.decerna.co.uk/what-is-g98/ | Secondary source. Primary is ENA EREC G98 |
| 3 | ERA5: hourly, 0.25°, ssrd accumulated in J/m², Copernicus licence | CONFIRMED (partly) | Radiation is accumulated in J/m² over a 1-hour period, timestamped at the end of the period | https://forum.ecmwf.int/t/surface-radiation-parameters-joule-m-2-to-watt-m-2/1588 | Not checked: 0.25° grid and the licence |
| 4 | MIDAS: hourly global radiation, OGL, CEDA registration | CONFIRMED | MIDAS Open UK hourly solar radiation: global radiation at all sites, direct and diffuse at some. OGL v3. Free CEDA account required. v202407 runs 1947–2023 | https://catalogue.ceda.ac.uk/uuid/0afba628c2f4462da68b0a81ebf1ff4c | v202407 has been superseded; use the latest version |
| 5 | PVGIS uses SARAH or ERA5 and offers hourly and monthly series | CONFIRMED | PVGIS 5.3 uses SARAH-3 (replacing SARAH-2) and ERA5/ERA5-Land, both covering 2005–2023. Hourly and monthly radiation tools are listed | https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-releases/pvgis-53_en | Tilt/azimuth inputs not confirmed on this page |
| 6 | FiT-era fleet has "essentially no batteries except retrofits" | STILL OPEN | — | — | |

**Totals:** 4 confirmed, 2 still open (6 items).

## 4. DATED_COST_AND_PRICE_SERIES_2016_2035

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Petrol "around 110p mid-2016" | CONFIRMED | 111.79p petrol and 112.41p diesel at end of July 2016 (RAC, 3 Aug 2016) | https://www.mynewsdesk.com/uk/rac/pressreleases/july-brings-an-end-to-four-months-of-rising-fuel-prices-1504393 | This is RAC data. The DESNZ 2003–2017 CSV is still unread |
| 2 | Ofgem cap models in xlsx "reachable" | STILL OPEN | — | https://www.ofgem.gov.uk/information-consumers/energy-advice-households/energy-price-cap-unit-rates-and-standing-charges | The rates page links to no xlsx files; its tables can be downloaded |
| 3 | EVHS caps "£500, and £700 before that" (also "grant ≤£500" in table b) | CORRECTED | £900 at launch (Sep 2014) → £700 from 13 Apr 2015 → later £500 → £350 from 1 Apr 2020 | https://www.zapmap.com/news/olev-to-reduce-cap-on-ev-homecharge-grants-from-13-april-2015 ; https://www.whatcar.com/advice/owning/electric-vehicle-home-charging-scheme-changes-in-2022-what-do-i-need-to-know/n23628 | The pack misses the £900 start. A 2016 grant could have been £700 or £500; the date of the cut to £500 was not confirmed |
| 4 | Green Book "tables 4–8 are the retail ones" | NEEDS-FILE | One file, "Data tables 1 to 19" (xlsx). Page last updated 30 Nov 2023; tables revised 17 Apr 2023 | https://www.gov.uk/government/publications/valuation-of-energy-use-and-greenhouse-gas-emissions-for-appraisal | The page has no table titles |
| 5 | Batteries added to the energy-saving materials (ESM) VAT relief from Feb 2024 | CONFIRMED | From 1 Feb 2024 (SI 2024/24): batteries (storing ESM-generated or grid electricity), water-source heat pumps, diverters and groundworks. 0% to 31 Mar 2027, then 5% | https://legislation.gov.uk/uksi/2024/24/pdfs/uksiem_20240024_en_001.pdf | |
| 6 | Half-hourly national intensity "roughly 20–300+ g" | STILL OPEN | — | api.carbonintensity.org.uk/intensity/stats/{from}/{to} | The proxy blocked the API (403) |

**Totals:** 2 confirmed, 1 corrected, 2 still open, 1 needs-file (6 items).

## 5. GAP_CLOSURE_TDCV_VAT_RTS_CALTRACK_ECO_IUF

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | ASHRAE G14: CV(RMSE) 15% monthly / 30% hourly; NMBE ±5% / ±10% | CONFIRMED | Hourly: NMBE <10%, CV(RMSE) <30% (NREL). Monthly: CV(RMSE) ≤15%, NMBE ≤5% (secondary) | https://www.nrel.gov:443/docs/fy19osti/70865.pdf ; https://unmethours.com/question/15/when-calibrating-an-energy-model-what-are-the-typical-metrics-to-show-proper-calibration/ | The monthly limits come only from a Q&A site |
| 2 | PHE 2014 review bands: <16°C respiratory, 9–12°C blood pressure/cardiovascular, <5°C hypothermia | CORRECTED | The 2014 review does not give these bands. It finds higher blood-pressure risk below 18°C (stronger below 16°C), a suggested 15°C minimum for older people (Collins), the largest BP rise at 6°C, and evidence for COPD benefit at ≥21°C. Headline: ≥18°C "poses minimal risk", on weak evidence | https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf | The recalled bands probably come from older Cold Weather Plan / WHO summaries |
| 3 | Condensing boilers effectively mandatory since 2005 | CONFIRMED | "In 2005 Approved Document L… changed to require the installation of condensing boilers" | https://baxi.co.uk/trade/legislation/boiler-plus | Manufacturer page |
| 4 | EST condensing-boiler in-situ field trial "around 2009" | CONFIRMED | 60 boilers, for EST; published by DECC 19 Jun 2009 | https://www.gov.uk/government/publications/in-situ-monitoring-of-efficiencies-of-condensing-boilers-and-use-of-secondary-heating-trial-final-report-2009 | Its summary does not cover cleaning or sludge, so it does not close Gap 10 |
| 5 | Boiler Plus (2018) requires the system to be cleaned and a filter fitted | CORRECTED | Boiler Plus = ErP ≥92%, time/temperature controls and extra measures for combis. The mandatory filter plus clean-and-flush (BS 7593) came with the 2022 Part L uplift in England | https://baxi.co.uk/trade/legislation/boiler-plus ; https://phpionline.co.uk/feature-articles/part-l-and-water-treatment/ | Both sources are trade press |

**Totals:** 3 confirmed, 2 corrected (5 items).

## 6. PAYMENTS_AND_DIRECT_DEBIT

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | SLC 27.16 refund duty | STILL OPEN | — | https://www.ofgem.gov.uk/sites/default/files/2022-08/Decision%20Standard%20Licence%20ELECTRICITY.pdf | The 2022 notice changes only 27.15. The consolidated SLC PDFs were truncated in fetch. **Bears on the pack's open conflict:** the 2022 notice's *new* (underlined) 27.15 text still begins "The licensee must take all reasonable steps…". Only the Principal Term carve-out appears to be struck out. So the claim that "all reasonable steps" was removed is doubtful |
| 2 | BFY energy DD failure rate 2.2% in 2024, +27% | CONFIRMED (as BFY's claim) | 2.2%, +27% y/y. "BFY Group analysis of ONS and Ofgem data"; no method given | https://www.bfygroup.co.uk/blog/why-is-energy-debt-still-going-up | Not an official statistic |
| 3 | Reasons customers leave DD | STILL OPEN | — | — | |

**Totals:** 1 confirmed, 2 still open (3 items).

## 7. SUPPLIER_ACCOUNTS_AND_CAPITAL

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | IFRS 15 para 35(a): obligation satisfied over time because the customer receives and consumes the benefit as the entity performs | CONFIRMED | Wording quoted exactly | https://www.bdo.com.au/en-au/accounting-news/accounting-news-august-2019/recognising-revenue-under-ifrs-15 | Firm commentary, not the standard text |
| 2 | Unbilled amounts shown as accrued income or contract assets | STILL OPEN | — | — | IFRS 15 paras 105–107 not retrieved |
| 3 | IFRS 9 simplified approach (paragraph reference) | CONFIRMED | IFRS 9.5.5.15: the simplified approach is mandatory for trade receivables and contract assets with no significant financing component | https://ifrscommunity.com/knowledge-base/ifrs-9-impairment/ | Secondary |
| 4 | "~2.4%" EBIT allowance | STILL OPEN | — | — | No source found; the pack's 1.9% → 2.5–2.6% stands |

**Totals:** 2 confirmed, 2 still open (4 items).

## 8. SWITCHING_LOSS_OBJECTIONS_AND_DUAL_FUEL

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Win-back contact governed by general marketing and Standards of Conduct rules | STILL OPEN | — | — | This is an interpretation. Check SLC 0 and SLC 25 in the consolidated licence |

**Totals:** 1 still open (1 item).

## 9. VULNERABILITY_PSR_AND_ABILITY_TO_PAY

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Selectra: "roughly half of registrations sit with a supplier but not with the network" | STILL OPEN | — | — | No primary source found |
| 2 | The exposé was by *The Times*; the contractor was Arvato | CONFIRMED | *The Times* investigation; contractor Arvato Financial Solutions; reported 2 Feb 2023 | https://news.stv.tv/world/british-gas-suspends-breaking-into-homes-to-fit-pre-payment-meters | |

**Totals:** 1 confirmed, 1 still open (2 items).

---

## Overall totals

49 items: **21 confirmed, 6 corrected, 18 still open, 4 needs-file, 0 unpublished.**

**Corrections that change the packs:**
- **Off-street parking (65%, Westminster 7%, Flintshire 84%):** the source is the RAC Foundation *Standing Still* report (2021), not DfT/OZEV.
- **"~90% of BEV drivers off-street":** the DfT/Ipsos figure is 91% *can charge at home*. No public-only share is published.
- **EVHS grant caps:** £900 → £700 → £500 → £350.
- **Early Leaf charger:** 3.3 kW, not 3.6 kW.
- **PHE temperature bands:** the recalled bands are not in the 2014 review.
- **Filter and system clean:** this requirement comes from the 2022 Part L uplift, not Boiler Plus 2018.
- **SLC 27.15 (not tagged, but relevant):** the 2022 licence notice still appears to keep "all reasonable steps" in the new text.

**For someone with network access:**
- the TRA0305 .ods
- the VEH by-nation table (for Northern Ireland's share)
- the Green Book "Data tables 1 to 19" xlsx
- the Carbon Intensity API stats endpoint
- the current consolidated SLC 27 text on Ofgem's licence register

Searches used: about 36.

---

# Verification pass: Heat pumps, PV, proving savings, boilers, network limits, heating behaviour, volatility, tariffs, smart meters

# Verification of [unverified] items: 9 assigned packs (checked 2026-10-25)

I checked 56 tagged items. **35 are confirmed, 8 are corrected and 13 are still open.** None ended up as NEEDS-FILE or UNPUBLISHED. I used about 31 web searches. Several cited URLs that a search had not surfaced were refused by the allowlist, so those items went through secondary pages and are marked that way.

## 1. DIRECTOR_EVIDENCE_HEAT_PUMPS_AND_FABRIC_MEASURES_2026-10-25.md

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Cosy windows and rates (14.7 / 30.0 / 45.0p, 57.1p SC) "not confirmed on Octopus's own site" | CONFIRMED (partial) | Cheap 04–07, 13–16, 22–00 at 51% below the Day rate. Peak 16–19 at 50% above it. | https://octopus.energy/cosy/ | The windows and ratios match the tracker (30 × 0.49 = 14.7; 30 × 1.5 = 45). Octopus shows absolute rates and SC only by postcode, so the 57.1p SC and the VAT basis are still not confirmed. |
| 2 | Gas boiler replacement "about £2,000–3,500" | CORRECTED | £1,500–3,000 | https://www.which.co.uk/reviews/boilers/article/boiler-energy-efficiency | Which? |
| 3 | Boiler counterfactual "about £2,500" (§7 payback) | CONFIRMED | Inside £1,500–3,000 | same | The ~9-yr payback still stands. |
| 4 | Typical scope (radiator upsizing, cylinder, pipework) "unverified as quantities" | STILL OPEN | — | — | No source found. |
| 5 | Install "about 2–5 days on site" | CORRECTED | 1–3 days typical | https://hivehome.com/blog/air-source-heat-pumps/how-are-heat-pumps-installed | Hive quoting "MCS guidance". It is a vendor page. |
| 6 | Modelled savings exceed NEED measured "[as a ratio]" | CONFIRMED | Ratio about 0.73 (solid wall). Gov cavity model £140/yr against ~£80 NEED-derived [derived]. | https://assets.publishing.service.gov.uk/media/5c9234ca40f0b633f24d046c/Closing-the-gap_Pre-post-insulation-field-trial.pdf ; https://cleanenergy.campaign.gov.uk/insulation | BRE trial covered 16 homes. The gov figures assume a semi, EPC D, Oct 2025 cap. |
| 7a | Loft "£~1,000" | CONFIRMED | £400–1,200 | https://cleanenergy.campaign.gov.uk/insulation | Gov campaign page. The figure is for a top-up to 270–300 mm. |
| 7b | Cavity "£~2,000–3,000" | CORRECTED | £1,000–3,000 | same | Cavity payback in §7 becomes about 12–37 yrs [derived]. |
| 7c | External solid wall "£~10,000–15,000+" | CONFIRMED | EST: about £11,000 external, about £7,500 internal | https://www.nerdwallet.com/uk/personal-finance/solid-wall-insulation-can-save-hundreds-a-year | Secondary source quoting EST, 2023. |
| 8 | Immersion spikes "about 3 kW" | CONFIRMED | 3 kW standard element | https://electrical.theiet.org/wiring-matters/years/2025/107-september-2025/can-a-3-kw-immersion-heater-be-connected-to-a-13-a-fused-connection-unit-to-bs-1363-4/ | IET. Taken from the search-result title only; the page was not fetched. |
| 9 | IPMVP Option C details | CONFIRMED | At least 12 months pre (preferably 24+); at least 9 months post (preferably 12); routine and non-routine adjustments | https://www.energy.gov/sites/default/files/2024-10/mv_guide_5_0.pdf | DOE FEMP M&V Guide 5.0 |
| 10 | ASHRAE G14 thresholds | CONFIRMED | Calibrated simulation: monthly CV(RMSE) 15% / NMBE ±5%; hourly 30% / ±10%. Savings uncertainty <50% at 68% confidence. | https://discovery-pp.ucl.ac.uk/10117731/3/Burman_2020_BPA_SimBuild_JainN.pdf ; https://onebuilding.org/archive/equest-users-onebuilding.org/2009-March/001184.html | Secondary quotes of G14 |
| 11 | Prebound (Sunikka-Blank & Galvin 2012) | CONFIRMED | Building Research & Information, 2012 | https://www.cam.ac.uk/research/news/the-prebound-effect | It is framed as poorly rated homes and budget-consciousness, not explicitly "low-income". |

Totals: 13 items. 9 confirmed, 3 corrected, 1 still open.

## 2. DIRECTOR_EVIDENCE_SOLAR_PV_AND_HOME_BATTERIES_2026-10-25.md

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Inverter efficiency about 96–97% | CONFIRMED | Euro-weighted 97%, max 97.6% (GivEnergy 3.6 kW) | https://givenergy.com/wp-content/uploads/2026/03/UK-Datasheet-String-Inverter-3.6-v2.pdf | One manufacturer datasheet |
| 2 | FiT started 2010 | CONFIRMED | 2010; closed to new entrants in 2019 | https://www.ofgem.gov.uk/transparency-document/feed-tariffs-annual-report-scheme-year-15-april-2024-march-2025 | Page gives the year only. |
| 3 | Per-vintage tariffs "far above 21.6p and RPI-linked" | CORRECTED | Early PV paid 43.3p, rising to 45.4p after the RPI uplift. Indexation moves from RPI to **CPI from April 2026**. | https://www.solarpowerportal.co.uk/energy-policy/rpi-increase-45-4p-solar-fit-from-april-1 ; https://www.which.co.uk/reviews/feed-in-tariffs/article/feed-in-tariffs/what-is-the-feed-in-tariff | "Far above" holds. "RPI-linked" is out of date. The full Ofgem tariff tables by vintage were not pulled. |
| 4 | PV embodied carbon about 20–50 gCO2e/kWh | CORRECTED | Harmonised c-Si median 45 g (IQR 39–49) at 1,700 kWh/m²/yr irradiation | https://ideas.repec.org/a/bla/inecol/v16y2012is1ps122-s135.html | NREL (Hsu et al. 2012). At UK irradiation (about 1,000–1,100) that scales to about 70 g for older modules [derived]. Newer modules are lower. The 5–12-year carbon payback is probably short. |
| 5 | Export MPAN registration and settlement mechanics | CONFIRMED (partial) | SEG export MPANs (≤5 MW) are registered and settled under the BSC via BSCP504/514. NHH export follows P081. | https://www.elexon.co.uk/bsc/smg-issue/issue-91/ | Elexon Issue 91 closed in Dec 2021 with no change raised. The share of PV homes with a registered export MPAN is still unknown. |
| 6 | FiT reading frequency "quarterly or six-monthly" | CONFIRMED (partial) | Payments are usually quarterly. Readings are due each period. | https://www.which.co.uk/reviews/feed-in-tariffs/article/feed-in-tariffs/what-is-the-feed-in-tariff | No licensee rule text was found. |
| 7 | Battery signature (evening flatline, 02–05 blocks, 16–19 export) | STILL OPEN | — | — | This is design inference. No published validation exists. |
| 8 | Monthly PV and demand shapes used in (d) | STILL OPEN | — | — | Needs the PVGIS API, which was blocked. |
| 9 | "IPMVP is the usual reference" | CONFIRMED | — | https://www.energy.gov/sites/default/files/2024-10/mv_guide_5_0.pdf | — |

Totals: 9 items. 5 confirmed, 2 corrected, 2 still open.

## 3. DIRECTOR_EVIDENCE_PROVING_AND_SHOWING_HOUSEHOLD_SAVINGS_2026-10-25.md

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | ECO in-use factors about 35% cavity and loft, 33% solid wall | CONFIRMED | CWI 35%, loft 35%. SWI 33% for solid brick built pre-1967 (pre-1965 in Scotland), 25% otherwise. | https://www.ofgem.gov.uk/system/files/docs/2018/01/eco2t_measures_table_-_jan_2018_-_v1.2.pdf | Flat roof, floor, draught-proofing and glazing are 15%. Heat pumps and controls have none. |
| 2 | IPMVP Options A–D definitions | CONFIRMED | As in the table | https://www.energy.gov/sites/default/files/2024-10/mv_guide_5_0.pdf | — |
| 3 | Savings = baseline − reporting ± adjustments; routine vs non-routine | CONFIRMED | Equations 2-1 and 2-2 | same | — |
| 4 | G14 15% monthly CV(RMSE) for calibrated simulation | CONFIRMED | 15% / ±5% monthly; 30% / ±10% hourly | https://discovery-pp.ucl.ac.uk/10117731/3/Burman_2020_BPA_SimBuild_JainN.pdf | The 20% monthly figure in the pack table applies to regression baselines, not simulation. |
| 5 | G14 savings uncertainty <50% at 68% confidence | CONFIRMED | — | https://onebuilding.org/archive/equest-users-onebuilding.org/2009-March/001184.html | Secondary quote of G14 |
| 6 | CalTRACK 365-day baseline | CONFIRMED | max_days = 365 | https://eemeter.readthedocs.io/caltrack_compliance.html | — |
| 7 | CalTRACK about 90% data sufficiency | CONFIRMED | 0.9 coverage, daily and billing | same | — |
| 8 | Daily and billing HDD/CDD models with balance-point search | CONFIRMED | Search 30–90°F with a maximum 3°F gap; at least 10 non-zero and 20 total degree-days | same | — |
| 9 | Hourly time-of-week-and-temperature model with occupancy segmentation | STILL OPEN | — | — | eemeter has "hourly segmented design matrices". docs.caltrack.org redirect was blocked. |
| 10 | CalTRACK aimed at portfolio aggregation | STILL OPEN | — | — | Not found. |
| 11 | Opower "1.4–3.3%" range | CONFIRMED | 1.4–3.3% by utility; average 2.0% | https://www.povertyactionlab.org/evaluation/opower-evaluating-impact-home-energy-reports-energy-conservation-united-states | J-PAL summary of Allcott |
| 12 | CalTRACK 12-month baseline (§1.6) | CONFIRMED | 365 days | https://eemeter.readthedocs.io/caltrack_compliance.html | Duplicate of #6 |
| 13 | Life events (occupancy, EV) as IPMVP non-routine adjustments | CONFIRMED | Non-routine adjustments cover unexpected static changes such as occupancy | https://www.energy.gov/sites/default/files/2024-10/mv_guide_5_0.pdf | — |

Totals: 13 items. 11 confirmed, 0 corrected, 2 still open.

## 4. DIRECTOR_EVIDENCE_GAS_BOILERS_AND_HEATING_CONTROLS_2026-10-25.md

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1a | Condensing mandatory in England and Wales from April 2005 | CONFIRMED | From April 2005 new gas boilers had to be condensing (A/B, ≥86%); from 2010, A-rated (≥90%) | https://www.worcester-bosch.co.uk/professional/installers-choice/whats-on/20th-anniversary-for-condensing-boilers | Manufacturer page. Oil dates not checked. |
| 1b | NI "later" | STILL OPEN | — | — | Not found. |
| 2 | Boiler life 10–15 years | CONFIRMED | 10–15 yrs if serviced annually | https://www.baxi.co.uk/help-and-advice/faqs/how-long-does-a-boiler-last | Manufacturer source only. The gap for an official lifetime distribution stays open. |
| 3 | PRISM / change-point citation | CONFIRMED | PRISM = baseload + slope × HDD at a fitted reference temperature | https://www.aceee.org/files/proceedings/1986/data/papers/SS86_Panel9_Paper_04.pdf | ACEEE 1986. The canonical citation is Fels 1986, Energy & Buildings. |
| 4 | Annual HDD about 2,000 | CONFIRMED | Base 15.5°C, 1985–2004 regional means 1,794 (SW) to 2,638 (NE Scotland); Midlands 2,290 | https://www.open.edu/openlearn/nature-environment/energy-buildings/content-section-2.4.2 | The ~4.4 kWh/HDD slope is plausible. |
| 5 | G band cut-off 70% | CONFIRMED | SEDBUK 2005 G <70% (A ≥90, B 86–90 … F 70–74) | https://nibusinessinfo.co.uk/content/checking-boiler-efficiency | — |

Totals: 6 items. 5 confirmed, 0 corrected, 1 still open.

## 5. DIRECTOR_EVIDENCE_NETWORK_LIMITS_ON_EVS_HEAT_PUMPS_PV_AND_BATTERIES_2026-10-25.md

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | "A3:2024 added prosumer and battery provisions" | CORRECTED | A3:2024 (31 Jul 2024) added Reg 530.3.201 on bidirectional and unidirectional devices. Prosumer Chapter 82 came in **A2:2022**. Stationary secondary battery requirements are slated for **A4:2026**. | https://niceic.com/news/amendment-3-2024-of-bs-7671-update/ ; https://electrical.theiet.org/wiring-matters/years/2025/108-november-2025/prosumer-electrical-installations/ | — |

Totals: 1 item. 0 confirmed, 1 corrected, 0 still open.

## 6. DIRECTOR_EVIDENCE_HEATING_BEHAVIOUR_COMFORT_AND_HEALTH_FLOORS_2026-10-25.md

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | EST headline mean about 122 L/day | STILL OPEN | — | https://assets.publishing.service.gov.uk/media/5a75a29ced915d6faf2b4829/3147-measure-domestic-hot-water-consump.pdf | The gov.uk landing page says about 120 houses. The PDF was refused by the allowlist and needs a direct read. BRE STP09 does not state 122. |
| 2 | Lowering combi hot-water setpoint is low legionella risk "[unverified as formal HSE position]" | STILL OPEN | — | https://hse.gov.uk/Legionnaires/hot-and-cold.htm | HSE says all systems, including non- or low-storage ones, "can present foreseeable risk". It makes no low-risk statement. Next place to look is HSG274 Part 2. Treat the rule as a Poesys assumption. |
| 3 | SERL in-home temperature data via UKDS SN 8666 | STILL OPEN | — | https://doc.ukdataservice.ac.uk/doc/8666/mrdoc/UKDA/UKDA_Study_8666_Information.htm | SN 8666 exists: SERL Observatory 2019–2024, Secure Access, with ERA5 and EPC data. Temperature-sensor content is not confirmed. |

Totals: 3 items. 0 confirmed, 0 corrected, 3 still open.

## 7. DIRECTOR_EVIDENCE_GAS_AND_POWER_PRICE_VOLATILITY_2026-10-25.md

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | TTF/NBP front-month realised volatility >100% annualised in 2022 | STILL OPEN | — | — | No text value found. A 2021 options review charts TTF front-month implied vol on a 0–160% axis, but no readings were extractable. |
| 2 | NBP crisis peak vs pre-crisis baseline (10–25×) | CONFIRMED | About 19× [derived] | https://www.enappsys.com/wp-content/uploads/2023/01/2021_Annual_Market_Summary_GB.pdf | Uses the pack's own EnAppSys pre-2021 average of £14.24/MWh ≈ 41.7 p/th against the 800 p/th peak. |

Totals: 2 items. 1 confirmed, 0 corrected, 1 still open.

## 8. DIRECTOR_EVIDENCE_TARIFFS_AND_THE_DEFAULT_TARIFF_2026-10-25.md

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Share of fixes by length (12/18/24 months) | STILL OPEN | — | — | Not searched for lack of budget. It is most likely only in Ofgem RMI portal data. |
| 2 | Crisis-era exit fees much higher | CONFIRMED | Typical £60 dual fuel (Jun 2021), highest £150. June 2022 highest £600 dual fuel (Outfox 1-yr fix). | https://www.moneysavingexpert.com/pressoffice/2022/energy-exit-fees-are-up-to-10-times-higher-than-last-year--warns/ | The £0–30 per fuel band is only for normal markets. |
| 3 | CMA detriment for 2012–15, "above £2bn in 2015" | CORRECTED | £1.4bn a year average over 2012–15, rising to **almost** £2bn in 2015 | https://www.econ.cam.ac.uk/research/cwpe-abstracts?cwpe=1707 | Littlechild's summary of the CMA |
| 4 | Prepayment joined the default cap from 2021; levelisation from 2024 | CONFIRMED | CMA PPM cap expired 31 Dec 2020, with Ofgem protecting PPM under the default cap after that. PPM/DD standing-charge levelisation from April 2024 (decision 23 Feb 2024). | https://www.ofgem.gov.uk/publications/decision-protecting-energy-consumers-prepayment-meters ; https://ofgem.gov.uk/decision/decision-adjusting-standing-charges-prepayment-customers | Ofgem paused the second phase (debt costs) in Aug 2024. |
| 5a | Agile launched about 2018 | CONFIRMED | 19 Feb 2018 | https://community.openenergymonitor.org/t/my-octopus-agile-go-tariff-comparison-analysis-website/10987 | Community secondary source |
| 5b | Go launched about 2019 | STILL OPEN | — | https://staging4.utilityweek.co.uk/first-ever-time-of-use-tariff-launched-for-ev-users | The article confirms Go was the "first ever" EV ToU tariff, but no date was visible. |
| 6 | Three permitted RMR discounts: dual fuel, online account management, payment method | CORRECTED | Dual fuel, online account management and **dividend payments** | https://www.ofgem.gov.uk/sites/default/files/docs/2016/08/rmr_simpler_removal_stat_con_-_open_letter_august_2016.pdf | Taken from a summarising fetch. Check this against the PDF text before using it as canon. |

Totals: 7 items. 3 confirmed, 2 corrected, 2 still open.

## 9. DIRECTOR_EVIDENCE_SMART_METERS_AND_HALF_HOURLY_SETTLEMENT_2026-10-25.md

| # | Item | Result | Correct value | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Elective domestic HHS "low hundreds of thousands" of MPANs | STILL OPEN | — | — | No published count was found. Elexon's 2018 response says only that numbers were uncertain. |
| 2 | About 30% of energy on actual data at Interim Information | CONFIRMED | II 30%, R1 60%, R2 80%, R3 97%, DF 99% (as extracted) | https://www.ofgem.gov.uk/sites/default/files/docs/2014/06/slides_elexon_0.pdf | The axis mapping is still ambiguous: there is no SF or RF value, and 97% appears at R3, while the RF target is 97%. |

Totals: 2 items. 1 confirmed, 0 corrected, 1 still open.

---

**Overall: 56 items. 35 confirmed, 8 corrected, 13 still open, 0 needs-file, 0 unpublished.**

**Corrections that change numbers already in the packs:**
- **Heat pump pack, cavity payback.** Cavity cost falls to £1,000–3,000, so the cavity payback in §7 moves to about 12–37 years.
- **Heat pump pack, install time.** On site is 1–3 days, not 2–5.
- **Solar pack, PV embodied carbon.** At UK irradiation it is probably about 70 g for older modules, so the 5–12-year carbon payback is likely too short.
- **Solar pack, FiT indexation.** It moves to CPI from April 2026; anything that still assumes RPI needs changing.

**Not checked:** these items are written as "not verified" in the tariffs pack but not tagged [UNVERIFIED]:
- the date the ban on acquisition-only tariffs ended;
- the date the RMR rules were formally removed.

Sources:
- [Cosy Octopus](https://octopus.energy/cosy/)
- [Which? boiler efficiency](https://www.which.co.uk/reviews/boilers/article/boiler-energy-efficiency)
- [Hive heat pump install](https://hivehome.com/blog/air-source-heat-pumps/how-are-heat-pumps-installed)
- [Gov clean energy insulation](https://cleanenergy.campaign.gov.uk/insulation)
- [NerdWallet SWI](https://www.nerdwallet.com/uk/personal-finance/solid-wall-insulation-can-save-hundreds-a-year)
- [IET immersion](https://electrical.theiet.org/wiring-matters/years/2025/107-september-2025/can-a-3-kw-immersion-heater-be-connected-to-a-13-a-fused-connection-unit-to-bs-1363-4/)
- [DOE M&V Guide 5.0](https://www.energy.gov/sites/default/files/2024-10/mv_guide_5_0.pdf)
- [Burman 2020](https://discovery-pp.ucl.ac.uk/10117731/3/Burman_2020_BPA_SimBuild_JainN.pdf)
- [onebuilding G14](https://onebuilding.org/archive/equest-users-onebuilding.org/2009-March/001184.html)
- [energy-data.io G14](https://energy-data.io/standards/ashrae-guideline-14/)
- [Cambridge prebound](https://www.cam.ac.uk/research/news/the-prebound-effect)
- [GivEnergy datasheet](https://givenergy.com/wp-content/uploads/2026/03/UK-Datasheet-String-Inverter-3.6-v2.pdf)
- [Ofgem FIT SY15](https://www.ofgem.gov.uk/transparency-document/feed-tariffs-annual-report-scheme-year-15-april-2024-march-2025)
- [SPP RPI FiT](https://www.solarpowerportal.co.uk/energy-policy/rpi-increase-45-4p-solar-fit-from-april-1)
- [Which? FiT](https://www.which.co.uk/reviews/feed-in-tariffs/article/feed-in-tariffs/what-is-the-feed-in-tariff)
- [Hsu et al. 2012](https://ideas.repec.org/a/bla/inecol/v16y2012is1ps122-s135.html)
- [Elexon Issue 91](https://www.elexon.co.uk/bsc/smg-issue/issue-91/)
- [Ofgem ECO2t measures table](https://www.ofgem.gov.uk/system/files/docs/2018/01/eco2t_measures_table_-_jan_2018_-_v1.2.pdf)
- [eemeter CalTRACK compliance](https://eemeter.readthedocs.io/caltrack_compliance.html)
- [J-PAL Opower](https://www.povertyactionlab.org/evaluation/opower-evaluating-impact-home-energy-reports-energy-conservation-united-states)
- [CEEPR Allcott](https://ceepr.mit.edu/workingpaper/social-norms-and-energy-conservation)
- [Worcester Bosch](https://www.worcester-bosch.co.uk/professional/installers-choice/whats-on/20th-anniversary-for-condensing-boilers)
- [Baxi](https://www.baxi.co.uk/help-and-advice/faqs/how-long-does-a-boiler-last)
- [ACEEE PRISM](https://www.aceee.org/files/proceedings/1986/data/papers/SS86_Panel9_Paper_04.pdf)
- [OpenLearn HDD](https://www.open.edu/openlearn/nature-environment/energy-buildings/content-section-2.4.2)
- [nibusinessinfo SEDBUK](https://nibusinessinfo.co.uk/content/checking-boiler-efficiency)
- [NICEIC A3](https://niceic.com/news/amendment-3-2024-of-bs-7671-update/)
- [IET prosumer](https://electrical.theiet.org/wiring-matters/years/2025/108-november-2025/prosumer-electrical-installations/)
- [gov.uk EST DHW](https://www.gov.uk/government/publications/measurement-of-domestic-hot-water-consumption-in-dwellings)
- [BRE STP09](https://bregroup.com/documents/d/bre-group/stp09-dhw01_analysis_of_est_dhw_data)
- [HSE legionella](https://hse.gov.uk/Legionnaires/hot-and-cold.htm)
- [WaterSafe](https://watersafe.org.uk/advice/common_plumbing_questions1/temperature/what_temperature_should_hot_water_be_stored_at)
- [UKDS SN 8666](https://doc.ukdataservice.ac.uk/doc/8666/mrdoc/UKDA/UKDA_Study_8666_Information.htm)
- [commodityvol 2021](https://commodityvol.com/aux/doc/w9Et788A/WEBSCROLL/UjpK6ECp/YearEnd2021.pdf)
- [MSE exit fees](https://www.moneysavingexpert.com/pressoffice/2022/energy-exit-fees-are-up-to-10-times-higher-than-last-year--warns/)
- [Cambridge CWPE 1707](https://www.econ.cam.ac.uk/research/cwpe-abstracts?cwpe=1707)
- [Ofgem PPM decision](https://www.ofgem.gov.uk/publications/decision-protecting-energy-consumers-prepayment-meters)
- [Ofgem levelisation](https://ofgem.gov.uk/decision/decision-adjusting-standing-charges-prepayment-customers)
- [OEM Agile](https://community.openenergymonitor.org/t/my-octopus-agile-go-tariff-comparison-analysis-website/10987)
- [Utility Week Go](https://staging4.utilityweek.co.uk/first-ever-time-of-use-tariff-launched-for-ev-users)
- [Ofgem RMR letter 2016](https://www.ofgem.gov.uk/sites/default/files/docs/2016/08/rmr_simpler_removal_stat_con_-_open_letter_august_2016.pdf)
- [Elexon 2018 HH response](https://www.ofgem.gov.uk/system/files/docs/2018/09/access_to_hh_data_for_settlement_elexon_responsev1.0_1.pdf)
- [Ofgem/Elexon 2014 slides](https://www.ofgem.gov.uk/sites/default/files/docs/2014/06/slides_elexon_0.pdf)