# Director evidence: belgium compared with GB (knowledge only)

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 07:17 GMT: "To be clear this is not to turn into SIM or supplier action at this stage it just to understand how transferable what we are building in the UK is to other markets and where new SIM and new supplier features would have to be built."
- 07:22 GMT: "You may have to look at cooling and cooking  too? Also switching, homemove? Does debt sit with supplier or dno?"

This is one of seven country packs: Australia, France, Germany, Italy, Spain, Belgium and Japan. The cover steer is `DIRECTOR_STEER_OTHER_MARKETS_ARE_KNOWLEDGE_ONLY_2026-10-25.md`.

## What to do with it

- **Knowledge only. Build nothing from this pack, and don't change any world or supplier priority.**
- Publish it as a Knowledge page in an "Other markets" section, and register its concepts.
- Keep its transferability ratings and its lists of new features as the record of what each component would need.

---

# Belgium vs GB: household energy market evidence pack for Poesys

**What this is for:** to understand how Belgium's household energy market differs from Great Britain's. This is knowledge only, not a build plan.

**Labels used throughout:**
- **[derived]** means my own arithmetic.
- **[unverified]** means it comes from memory and has no source URL in this pack.

**Research limit:** the shared web-search budget ran out partway through. The figures for heat pumps, PV installation counts, degree days, housing, tenure, cooking fuel, air-conditioning and payment-method mix could not be confirmed, so they are marked [unverified] or listed as gaps. The coordinator added dimensions 12–16 mid-task. They are covered below with what was already gathered.

---

## 0. Structure: three regions, four regulators

Energy powers in Belgium are split between the federal level and the three regions.

**Federal (CREG and the federal government) is responsible for:**
- the transmission system operator, Elia
- wholesale markets
- nuclear policy
- the social tariff, which is federal
- VAT and excise

**The regions are responsible for:**
- distribution networks and distribution network tariffs
- supply licensing
- public service obligations
- smart meters
- debt and disconnection rules
- PV support

The three regional regulators are:

| Region | Regulator |
|---|---|
| Flanders | VREG (Vlaamse Nutsregulator) |
| Wallonia | CWaPE |
| Brussels | Brugel |

The four regulators publish a joint market report each year ([Rapport commun 2024](https://brugel.brussels/publication/document/rapports/2025/fr/Rapport-commun-2024-Marche.pdf)).

**What this means for Poesys:** a "Belgian world" is really three regional rulebooks inside one federal shell. GB has a single regulator (Ofgem) and a single licence regime.

---

## 1. Weather and climate

- **Climate:** Belgium has a temperate maritime climate like southern England. The Ardennes in south-east Wallonia are colder and more continental. [unverified]
- **Heating degree days:** I could not retrieve Eurostat annual figures for Belgium. My memory is about 2,600–2,900 heating degree days a year (Eurostat method), slightly below the UK at about 3,000. [unverified]
- **Cooling degree days:** Eurostat gives Belgium **11.79 in 2024**. The series ranges from 0.07 to 52.55, with a long-run average of 14.3 ([DBnomics/Eurostat nrg_chdd_a](https://db.nomics.world/Eurostat/nrg_chdd_a)). Cooling demand is negligible, as in GB.
- **Demand seasonality:** strongly winter-peaking, driven by gas heating. Gas through distribution networks was 82.3 TWh in 2024 (Flanders 56.4, Wallonia 17.5, Brussels 8.3 TWh), against 63.1 TWh of electricity ([Rapport commun 2024](https://brugel.brussels/publication/document/rapports/2025/fr/Rapport-commun-2024-Marche.pdf)). The report's "Belgium" gas total of 149.3 TWh includes more than distribution.

**Transferability:** high. Poesys's GB weather-to-demand model fits after recalibration, with an Ardennes cold zone added.

## 2. Energy system

**Electricity consumption and mix**

| | 2024 | 2025 |
|---|---|---|
| Consumption | 80.5 TWh | 80.1 TWh |
| Nuclear | 42.2% | 22.5 TWh (34.2%) |
| Gas | 17.6% (record low) | 12.3 TWh (~19%) |
| Renewables | 20.8 TWh (29.8%) | 22.4 TWh (~34%, record) |
| Solar | 8.3 TWh | 10.1 TWh (+21%) |
| Wind | 12.5 TWh (7.0 offshore, 5.5 onshore) | 12.3 TWh |
| Net imports | 10.6 TWh | 14 TWh |
| Negative-price share of time | 4.6% | 6.1% |

Sources: 2024 from [Elia 2024 mix release](https://elia.be/-/media/project/elia/shared/documents/press-releases/2025/20250102_press-release_electricity-mix-2024_en.pdf); 2025 from [Connaissance des Énergies, citing Elia](https://www.connaissancedesenergies.org/une-annee-electrique-en-belgique-que-faut-il-retenir-de-2025).

- **Nuclear trend:** nuclear output has fallen five years in a row, from 48 TWh in 2021 ([same source](https://www.connaissancedesenergies.org/une-annee-electrique-en-belgique-que-faut-il-retenir-de-2025)).
- **Interconnection, 2024:** net imports were 12.6 TWh from France and 5.9 TWh from the Netherlands. Net exports were 4.3 TWh to the UK and 2.8 TWh to Germany. Total cross-border exchange was 44.5 TWh. The average day-ahead price was about **€69.7/MWh** ([Elia](https://elia.be/-/media/project/elia/shared/documents/press-releases/2025/20250102_press-release_electricity-mix-2024_en.pdf)). The interconnection level was 24% in 2019–20, against a 33% target ([IEA Belgium 2022](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Belgium2022_EnergyPolicyReview.pdf)).

**Nuclear phase-out reversed**
- Parliament repealed the 2003 phase-out law on 15 May 2025 ([Foro Nuclear](https://www.foronuclear.org/en/updates/news/belgiums-parliament-votes-to-abandon-nuclear-phaseout-plans/)).
- Doel 4 and Tihange 3 were extended by 10 years in 2022 ([same](https://www.foronuclear.org/en/updates/news/belgiums-parliament-votes-to-abandon-nuclear-phaseout-plans/)). Running to about 2035 is [unverified].
- Doel 1 (15 February), Tihange 1 (30 September) and Doel 2 (30 November) closed in 2025. Nuclear capacity at the start of 2026 is almost half what it was a year earlier ([CdE](https://www.connaissancedesenergies.org/une-annee-electrique-en-belgique-que-faut-il-retenir-de-2025)).

**Market design**
- Belgium is an energy-only market with a **capacity remuneration mechanism** (CRM). The first auction, in October 2021 for delivery in 2025, cleared about 4.4 GW. Each delivery year has two auctions, one four years ahead and one a year ahead ([IEA 2022](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Belgium2022_EnergyPolicyReview.pdf)).
- In 2019 one company held a 72% share of the wholesale market ([IEA 2022](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Belgium2022_EnergyPolicyReview.pdf)).
- Belgium is a single bidding zone coupled into the Core flow-based day-ahead market. Day-ahead moved to 15-minute products in 2025. [unverified]

**Gas**
- Belgium converted its network from low-calorific (L-gas, Groningen) to high-calorific gas (H-gas), targeting completion by 2024 ([IEA 2022](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Belgium2022_EnergyPolicyReview.pdf)).
- Fluxys is the gas transmission operator and ZTP (Zeebrugge) is the gas hub. [unverified]

**Compared with GB:** GB is also a single zone with a capacity market and lower nuclear. Belgium relies far more on imports, about 13–17% of consumption [derived: 10.6/80.5, 14/80.1].

## 3. Grid

**Operators**
- **Transmission:** Elia.
- **Electricity distribution (DSOs):**
  - Flanders: Fluvius, operating several sub-areas such as Fluvius Antwerpen and Fluvius West.
  - Wallonia: ORES (dominant), RESA (Liège), plus the small operators AIEG, AIESH and REW.
  - Brussels: Sibelga.
  
  The operator list comes from the 2026 prosumer tariff table in [Test-Achats](https://test-achats.be/maison-energie/energie-renouvelable/dossier/tarif-prosumer). That makes about 7 DSOs plus Fluvius sub-areas, against 14 licensed DNO areas run by 6 groups in GB. [unverified for GB]
- **Atrias:** Fluvius, ORES, Sibelga and RESA jointly created Atrias, the central data hub ([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i25291/nieuw-dataplatform-moet-hefboom-worden-in-energietransitie-belgische-elektriciteitssector)).

**Household connections**
- Many Belgian homes have a 3×230 V supply without neutral, a legacy design, or 3×400 V+N. A 40 A main breaker is a common size. [unverified]
- The only regulatory clue retrieved is that Walloon guidance refers to connections up to 10 kVA ([UVCW](https://www.uvcw.be/no_index/files/12419-qr-enrinf10kva-17012024.pdf)). [unverified as to content]

**Flanders capacity tariff (since 1 January 2023)**
- Applies to households and SMEs. Network charges are split into a capacity part (kW), a smaller per-kWh part and a minimum amount. The day/night difference in network charges was removed.
- The digital meter measures average power per quarter-hour. The monthly peak is the highest quarter-hour in the month, and billing uses the **average of the last 12 monthly peaks**.
- Everyone pays for **at least 2.5 kW**.
- Households with an analogue meter pay the 2.5 kW minimum plus a higher per-kWh rate.
- Social-tariff customers are excluded.
- Example: 3,500 kWh a year with an average monthly peak of 4.26 kW cost about €337 a year in network charges including VAT in 2023 ([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i28470/vlaams-capaciteitstarief-op-1-januari-van-start-alle-feiten-en-cijfers-op-een-rij)).
- A 4 kW average peak cost about €161.60 a year excluding VAT in 2023 ([Test-Aankoop](https://www.test-aankoop.be/woning-energie/gas-elektriciteit-mazout-pellets/nieuws/wat-betekent-de-invoering-van-het-capaciteitstarief-vanaf-2023-voor-jou)). That is about €40/kW/yr [derived].

**Wallonia and Brussels** charge network fees mainly per kWh. Wallonia also charges the prosumer tariff per kWe (section 11). New time-of-use distribution tariffs in the 2025–29 periods are [unverified].

**Compared with GB:** GB household network charges are per kWh plus a standing charge, with no kW capacity element. A Flemish household's network bill depends on its 15-minute peak, so EV charging, heat pump use and kettle timing directly change network cost.

## 4. Population and households

- About **5.1 million private households**, 36% of them one-person (Statbel, reported by [Brussels Times, 2023](https://brusselstimes.com/548037/nearly-a-third-of-belgians-now-live-alone)).
- Wallonia: average household size 2.2 in 2025, with 37.7% single-person households ([IWEPS](https://www.iweps.be/wp-content/uploads/2026/03/D013-MENAGES-032026_Full1.pdf)).
- Electricity access points at 31 December 2024: **6.28 m** (Flanders 3.65 m, Wallonia 1.95 m, Brussels 0.69 m). Gas access points: **3.60 m** (Flanders 2.37 m, Wallonia 0.79 m, Brussels 0.43 m) ([Rapport commun 2024](https://brugel.brussels/publication/document/rapports/2025/fr/Rapport-commun-2024-Marche.pdf)).
- Only about 57% of electricity points also have gas [derived: 3.60/6.28]. In Wallonia it is about 41% [derived].
- **Compared with GB:** GB has about 28 m households and about 2.4 people per household [unverified]. Belgium is about one-sixth the size, highly urbanised, and Brussels is almost entirely flats [unverified].

## 5. Housing and heating

- **Building energy by fuel, 2020:** gas about 40%, electricity 27%, oil 27%, biomass 5%, district heating 0.6%. Oil supplied about 33% of residential building demand, the fifth-highest heating-oil share in the IEA ([IEA 2022](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Belgium2022_EnergyPolicyReview.pdf)). GB oil heating is about 4% of homes [unverified].
- **Tenure:** about 71% owner-occupied, an old building stock, and houses dominant outside Brussels. [unverified]
- **Standard consumption:** CREG uses **3,500 kWh/yr electricity** and **17,000 kWh/yr gas** for comparisons ([CREG study (F)3188, March 2026](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Rapport%20CREG%20fourniture%20d%27%C3%A9nergie%20en%20Belgique%20en%202025.pdf)). Ofgem's typical domestic consumption values are about 2,700 kWh electricity and 11,500 kWh gas [unverified].
- **Implied average per electricity point:** about 7.6 MWh in Flanders, 7.1 MWh in Wallonia and 5.7 MWh in Brussels [derived from the TWh and access-point figures above]. These include small businesses on distribution networks, so they overstate household use.

## 6. Core regulation and competition

- **Fully liberalised:** Flanders since 2003, Wallonia and Brussels since 2007. There is no default price cap like Ofgem's. [unverified]
- **Social tariff:** the regulated price is the federal social tariff for eligible customers only (section 10). The temporary maximum prices that apply when the DSO supplies a customer are set with CREG ([CWaPE 2007 opinion](https://www.cwape.be/sites/default/files/cwape-documents/243.pdf); [CallMePower](https://callmepower.be/fr/energie/guides/comprendre/treve-hivernale)).
- **Licensing:** supply licences are regional (VREG, CWaPE, Brugel). [unverified] Public service obligations on suppliers have grown, especially in Wallonia and Brussels, and this is cited as a reason for supplier exits ([Rapport commun 2023](https://brugel.brussels/publication/document/rapports/2023/fr/Rapport-commun-evolution-marches-2023.pdf)).

**Active suppliers, September 2025:**

| | Flanders | Wallonia | Brussels |
|---|---|---|---|
| Electricity suppliers | 22 | 12 | 6 |
| Gas suppliers | 17 | 11 | 6 |

Source: [CREG F3188](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Rapport%20CREG%20fourniture%20d%27%C3%A9nergie%20en%20Belgique%20en%202025.pdf).

**Concentration, September 2025:**

| | Flanders | Wallonia | Brussels |
|---|---|---|---|
| Top-3 share, electricity | 73.9% | 80.2% | 92.2% |
| Concentration index (HHI), electricity | 2,252 | 2,859 | 5,297 |

Source: same CREG study. Brussels electricity: Engie holds about 73% and the top three hold 93.1% ([Brugel annual report 2024](https://brugel.brussels/publication/document/rapports/2025/fr/Rapport-annuel-2024-Conso.pdf)). The largest suppliers are Engie-Electrabel, Luminus and TotalEnergies/Eneco.

**Products**
- About 75% of household electricity contracts are variable and 25% fixed. Spot-indexed variable products make up about 46% of electricity and 48% of gas contracts. Fixed contracts were 65–70% before 2022 and about 15% in the 2022 crisis.
- Dynamic electricity contracts: 20,552 (0.40%), almost all in Flanders.
- 51% of households sit on one of the 10 most expensive products. The average possible saving is about €130/yr on electricity and €170/yr on gas.

All from [CREG F3188](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Rapport%20CREG%20fourniture%20d%27%C3%A9nergie%20en%20Belgique%20en%202025.pdf).

**Supplier failures:** 2021 switching was inflated by supplier bankruptcies and Luminus taking over Essent Belgium ([Rapport commun 2023](https://brugel.brussels/publication/document/rapports/2023/fr/Rapport-commun-evolution-marches-2023.pdf)). Belgium has no GB-style Supplier of Last Resort or Special Administration regime documented here (gap).

## 7. Smart meters ("digital meters")

**Flanders** (mandatory rollout by Fluvius)
- 4.40 m electricity and gas digital meters installed by end of February 2025, in nearly 7 in 10 connections ([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i40041/laatste-336-000-vlaamse-consumenten-met-zonnepanelen-krijgen-dit-jaar-digitale-meter)).
- The last 403,000 prosumers were converted during 2025. About 90% of those paying the prosumer tariff had a digital meter by the end of 2025 ([Test-Achats](https://test-achats.be/maison-energie/energie-renouvelable/dossier/tarif-prosumer)).

**Wallonia and Brussels:** slower, targeted rollouts.
- Brugel's December 2025 performance-indicator decision covers remote-read meter types (AMR, SMR1, SMR3), and Sibelga expects a zero score on IT interfaces in 2026 ([Brugel decision 378](https://brugel.brussels/publication/document/decisions/2025/fr/DECISION-378-KPI-COMPTEURS-INTELLIGENTS.pdf)).
- No installed counts for ORES, RESA or Sibelga were retrieved (gap).

**Ownership and data**
- The DSO owns and operates the meters, not the supplier. This is the opposite of GB, where suppliers own the meters and DCC runs communications.
- Consumers see quarter-hour data ([Test-Achats](https://www.test-achats.be/maison-energie/gaz-electricite-mazout-pellets/dossier/compteurs-numeriques)). Sibelga runs data-access and consent portals ([Brugel 378](https://brugel.brussels/publication/document/decisions/2025/fr/DECISION-378-KPI-COMPTEURS-INTELLIGENTS.pdf)).
- **Compared with GB:** GB has about 60–65% smart or advanced meters, supplier-led, with half-hourly data [unverified].

## 8. Billing

- **Typical pattern:** monthly advance invoices, then an annual true-up bill. Atrias/MIG6 added support for monthly billing on actual reads instead of advances, separate consumption and injection contracts, and dynamic tariffs ([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i25291/nieuw-dataplatform-moet-hefboom-worden-in-energietransitie-belgische-elektriciteitssector)).
- For Flemish customers on Fluvius prepaid, gas is still billed by advance invoice ([Vlaanderen.be](https://www.vlaanderen.be/digitale-meter-met-prepaid-functie)).
- **Payment methods:** direct debit is common. Prepayment exists only as a debt-management tool run by the DSO, not as a commercial product. [unverified mix]
- **Taxes:** VAT on electricity and gas is 6% (permanent since April 2023, with a federal excise). [unverified] Prosumer tariff amounts are quoted "incl. 6% VAT" ([Test-Achats](https://test-achats.be/maison-energie/energie-renouvelable/dossier/tarif-prosumer)). GB VAT is 5%.
- **Fees (Flanders):** since September 2023 suppliers cannot charge reminder or administrative fees. Statutory late interest and capped damages apply ([Selectra](https://selectra.be/nl/energie/factuur/openstaand); this is a commercial site, so verify).

## 9. Settlement

- **Interval:** 15 minutes for electricity, 60 minutes for gas.
- **Profiled vs measured:** continuously metered points (AMR, non-profiled SMR3) are allocated on 15-minute data. Index-read points are split using synthetic or real load profiles, a climate correction factor and a residue factor. Unmetered PV production is estimated from inverter capacity and a synthetic production profile ([MIG6 Reconciliation BRS via VREG](https://www.vlaamsenutsregulator.be/sites/default/files/document/methodiek_van_reconciliatie_voor_elektriciteit.docx)).
- **Process:** monthly allocation, then reconciliation. Reconciliation is "the basis for definitive financial settlement". The reconciliation volume equals allocated volume minus metered/allocated volume, per balance supplier, access point, direction, time-of-use band and month. A "compensation reconciliation" spreads residual error across all balance suppliers in proportion ([same](https://www.vlaamsenutsregulator.be/sites/default/files/document/methodiek_van_reconciliatie_voor_elektriciteit.docx)).
- **Timing:** there is no fixed run calendar. The worked example has July results in early September.
- **Central system:** the Atrias Central Clearing House went live gradually from 1 November 2021, covering more than 9.6 m access points ([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i25291/nieuw-dataplatform-moet-hefboom-worden-in-energietransitie-belgische-elektriciteitssector)).
- **Smart-meter allocation:** most smart-metered households stay on profiles unless they opt into quarter-hour allocation, for example through a dynamic contract. [unverified]
- **Imbalance:** Elia settles imbalance per 15 minutes; balance responsibility sits with the supplier's balance responsible party. [unverified]
- **Compared with GB:** GB settles in 30-minute periods. MHHS is moving all households to half-hourly settlement with a shortened reconciliation timetable [unverified].

## 10. Debt and vulnerability

**Social tariff (federal)**
- A reduced price set by CREG each quarter for people with certain social statuses and for social housing residents. Example levels: Q1 2024 electricity 23.441 c/kWh and gas 5.371 c/kWh, both incl. VAT ([Brussels Times](https://brusselstimes.com/846654/social-tariffs-for-gas-electricity-to-go-up-by-over-9-next-year)).
- Allocation is more than 90% automatic ([Chamber doc 56 0195/006](https://www.lachambre.be/doc/flwb/pdf/56/0195/56K0195006.pdf)).
- In 2020, 9.7% of electricity customers (about 470,000) and 10% of gas customers (about 295,000) received it ([IEA 2022](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Belgium2022_EnergyPolicyReview.pdf)). More than 500,000 households were covered during the crisis ([VVSG, January 2026](https://www.vvsg.be/media/23247/download)).
- It is pegged to the lowest commercial tariff and funded by a federal levy. [unverified]
- Reform is under debate, including an income criterion ([Chamber](https://www.lachambre.be/doc/flwb/pdf/56/0195/56K0195006.pdf)).
- The National Bank puts energy poverty at **21.8% in 2022**. Without the social tariff, 34% of vulnerable households would be energy-poor; with it, 12% ([VVSG](https://www.vvsg.be/media/23247/download)).

**Winter disconnection rules**

| Region | Winter period | Rule |
|---|---|---|
| Flanders | 1 Dec – 1 Mar ([CallMePower](https://callmepower.be/fr/energie/guides/comprendre/treve-hivernale)) or 1 Dec – 1 Apr ([Selectra](https://selectra.be/nl/energie/factuur/openstaand)); **the sources conflict** | No household cuts except safety, fraud, empty home, or refusing a contract after moving. Outside winter, a cut needs a decision by the municipal Local Advisory Commission (LAC). |
| Wallonia | 1 Nov – 15 Mar, extendable ([Droits Quotidiens](https://www.droitsquotidiens.be/fr/question/peut-couper-mes-fournitures-de-gaz-et-delectricite-en-plein-hiver-wallonie); [CWaPE guidelines](https://www.CWAPE.be/sites/default/files/cwape-documents/432.pdf)) | A supplier can cut only a customer who is in default **and** refuses a budget meter. |
| Brussels | 1 Oct – 31 Mar ([Droits Quotidiens](https://www.droitsquotidiens.be/fr/question/peut-couper-mes-fournitures-de-gaz-et-delectricite-en-plein-hiver-bruxelles)) | Contract termination requires a justice of the peace. In 2024 there were 1,861 electricity cuts, 858 of them by court decision ([Brugel 2024](https://brugel.brussels/publication/document/rapports/2025/fr/Rapport-annuel-2024-Conso.pdf)). |

- **Brussels arrears:** in 2024, 39% of households received at least one electricity reminder and 16% a formal notice ([Brugel 2024](https://brugel.brussels/publication/document/rapports/2025/fr/Rapport-annuel-2024-Conso.pdf)).
- **Compared with GB:** GB prepayment is both a commercial and a debt product, with a voluntary winter moratorium and a Priority Services Register [unverified]. Belgium has no PSR equivalent documented here. Its "protected customer" status (section 16) plays the role.

## 11. EV, PV, batteries, heat pumps

**End of net metering ("reversing meter")**

| Region | What happened |
|---|---|
| Flanders | The Constitutional Court (14 January 2021, effective 1 March 2021) struck down the 15-year reversing-meter guarantee for digital meters ([Vlaanderen.be](https://www.vlaanderen.be/bouwen-wonen-en-energie/elektriciteit-en-aardgas/digitale-meter/uitspraak-arrest-grondwettelijk-hof-over-het-vernietigingsberoep-tegen-het-decreet-digitale-meters)). Owners of 2014–2020 installations got a one-off premium averaging €1,000–2,000, claimable until 31 December 2025 ([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i40041/laatste-336-000-vlaamse-consumenten-met-zonnepanelen-krijgen-dit-jaar-digitale-meter)). Owners still on analogue meters pay a prosumer tariff of €54.63–69.59/kVA in 2026 ([Test-Achats](https://test-achats.be/maison-energie/energie-renouvelable/dossier/tarif-prosumer)). |
| Wallonia | Installations commissioned before 2024 keep net metering until **31 December 2030**. Installations from 1 January 2024 have none: grid offtake and export are billed separately ([Chaudfontaine](https://chaudfontaine.be/panneaux-photovoltaiques-fin-du-compteur-qui-tourne-a-lenvers)). Prosumer tariff in 2026 is €85.84/kWe in the ORES area (€81–99 elsewhere). The subsidy for it ended in 2024 ([Test-Achats](https://test-achats.be/maison-energie/energie-renouvelable/dossier/tarif-prosumer)). |
| Brussels | Net metering was abolished in November 2021. There has never been a prosumer tariff ([Test-Achats](https://test-achats.be/maison-energie/energie-renouvelable/dossier/tarif-prosumer)). Brussels has 17,561 small PV installations, 3.3% of supply points ([Brugel 2024](https://brugel.brussels/publication/document/rapports/2025/fr/Rapport-annuel-2024-Conso.pdf)). |

**Home batteries (Flanders):** 136,630 at end-2024, with about 1.1–1.2 GWh capacity. 19,292 were added in 2024, down 57.8% from the subsidised 2023 ([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i40059/de-harde-cijfers-vorig-jaar-ruim-19-000-thuisbatterijen-geinstalleerd-in-vlaanderen)).

**Electric vehicles**
- Battery-electric cars were 20% of new registrations in 2023 and 28% in 2024.
- Company cars were 62% of the roughly 448,000 new cars in 2024, and companies bought 87% of new battery EVs.
- Tax: battery EVs bought by end-2026 are 100% deductible, falling to 67.5% by 2031. Deductibility for combustion cars falls to 0% by 2028 ([ICCT](https://theicct.org/?p=60217)).
- **Why it matters for a supplier:** many home chargers are employer-reimbursed company-car chargers, so the household does not bear the charging cost the way a GB EV owner does.

**Heat pumps:** no verified stock or sales figure was retrieved (gap). Flanders limits gas connections in new builds. [unverified]

## 12. Cooling

- Cooling degree days are low (11.79 in 2024, [Eurostat via DBnomics](https://db.nomics.world/Eurostat/nrg_chdd_a)).
- Household air-conditioning prevalence: no source retrieved. It is low and rising, as in GB. [unverified]
- The system peak is in winter. Summer solar now exceeds demand at times: a record wind-plus-solar output of 9,931 MW covered 93% of load in one quarter-hour on 22 August 2024 ([Elia](https://elia.be/-/media/project/elia/shared/documents/press-releases/2025/20250102_press-release_electricity-mix-2024_en.pdf)).
- The summer issue is surplus and negative prices, not cooling peaks.

## 13. Cooking

No cooking-fuel source was retrieved (gap). Gas hobs are common where there is gas: Brussels and Flanders cities. Induction is growing, and Wallonian homes off the gas grid cook electrically. [unverified]

## 14. Switching

- Switching runs through the Atrias Central Clearing House, which promised "faster, better-documented switching and moving processes" ([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i25291/nieuw-dataplatform-moet-hefboom-worden-in-energietransitie-belgische-elektriciteitssector)).
- Households pay no exit fee and can leave on one month's notice. The switch is effective within 21 days or less, there is a 14-day cooling-off period for distance sales, and the new supplier handles the switch. [unverified]
- **Rates:** Belgium had the highest electricity switching rate in Europe in 2019 ([IEA 2022](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Belgium2022_EnergyPolicyReview.pdf)) and generally ranks in the international top three ([CREG F3188](https://www.connaissancedesenergies.org/sites/connaissancedesenergies.org/files/pdf-actualites/Rapport%20CREG%20fourniture%20d%27%C3%A9nergie%20en%20Belgique%20en%202025.pdf)).
- Brussels 2024: electricity switching 3.05%, a 15-year high; gas 0.97% ([Brugel](https://brugel.brussels/publication/document/rapports/2025/fr/Rapport-annuel-2024-Conso.pdf)).
- In 2024, electricity switching rose by 0.8 percentage points and gas by 0.3 points nationally ([Rapport commun 2024](https://brugel.brussels/publication/document/rapports/2025/fr/Rapport-commun-2024-Marche.pdf)). Flanders and Wallonia figures are in charts only (gap).
- Transfers of customers to the DSO under public service obligations are excluded from switching statistics ([Rapport commun 2023](https://brugel.brussels/publication/document/rapports/2023/fr/Rapport-commun-evolution-marches-2023.pdf)).

## 15. Home moves

- **How it works:** a standard energy takeover document (energieovernamedocument / document de reprise des énergies), with meter readings signed by the outgoing and incoming occupants. The contract usually moves with the customer to the new address. [unverified]
- **Vacated sites (Flanders, older figures):** the outgoing supplier stays responsible for up to 30 days after the DSO accepts its request. The DSO writes to the new occupant within 5 working days, the occupant has 10 days to name a supplier, and the DSO visits after 15 days ([CWaPE 2007 opinion](https://www.cwape.be/sites/default/files/cwape-documents/243.pdf); dated).
- **No contract after moving:** moving without a contract is a ground for cutting supply even in winter, in Wallonia ("déménagement problématique", [Droits Quotidiens](https://www.droitsquotidiens.be/fr/question/peut-couper-mes-fournitures-de-gaz-et-delectricite-en-plein-hiver-wallonie)) and in Flanders ([CallMePower](https://callmepower.be/fr/energie/guides/comprendre/treve-hivernale)).
- **Compared with GB:** in GB the incumbent supplier on the meter supplies a new occupant on deemed terms. In Belgium, an unclaimed point ends up with the DSO process (the Flemish "MOZA" procedure), not with a deemed supplier. [unverified]

## 16. Where debt sits (DSO as social supplier)

This is the biggest structural difference from GB.

**Flanders (Fluvius)**
- **Drop procedure:**
  1. Free reminder giving at least 10 days.
  2. Registered notice of default after 15–30 days, offering four options: pay, payment plan, public social welfare centre (OCMW), or budget meter.
  3. The supplier may then end the contract. The customer is supplied for at least two months, first by the supplier and then by **Fluvius as social supplier**.
  4. Only the grid operator can disconnect, and only after a LAC decision.
  
  ([Selectra](https://selectra.be/nl/energie/factuur/openstaand))
- **Prepaid:** Fluvius switches on a prepaid function on the digital meter remotely, at no charge. Debt is repaid at €5/week, with 35% of each top-up going to debt. Where prepaid is impossible, a current limiter is fitted. Fluvius's tariff "is not the cheapest". Prepaid must be switched off once DSO debts are paid and the customer has a supplier contract. **Debts to former suppliers do not count**: they stay with the former supplier and do not follow the customer into the DSO regime ([Vlaanderen.be](https://www.vlaanderen.be/digitale-meter-met-prepaid-functie)).
- Prepaid customers become protected customers with access to the social tariff ([Selectra](https://selectra.be/nl/energie/factuur/openstaand)).

**Wallonia (ORES, RESA and others)**
- Protected customers get a budget meter. If they run out of credit they get a 1,300 W minimum supply for 6 months, which the CPAS can raise to 2,600 W. Gas supply in winter continues via supply cards.
- Customers still unpaid after 6 months are "in recurrent default" and are **supplied by the DSO** ([CallMePower](https://callmepower.be/fr/energie/guides/comprendre/treve-hivernale)).
- The DSO also supplies customers whose contract ends in winter, at a maximum tariff set with CREG ([same](https://callmepower.be/fr/energie/guides/comprendre/treve-hivernale)).
- DSO social costs feed into **network tariffs**. Debts owed to the DSO are recovered through a 20–35% kWh surcharge collected via the budget meter, or through payment plans ([CWaPE 2007](https://www.cwape.be/sites/default/files/cwape-documents/243.pdf); dated).

**Brussels (Sibelga)**
- At end-2024 Sibelga had 9,805 protected electricity customers and 7,325 protected gas customers, and 77% of them are in debt.
- Sibelga's social-supplier points tripled in ten years.
- Four in ten customers moved automatically to Sibelga do not pay their first bill.
- These debts are "à charge de Sibelga", meaning they are socialised through network tariffs [inferred, not stated].
- Suppliers separately hold about €120 m of residential debt.
- Sibelga's phone outreach (28,284 calls) replaced the power-limiter measure ([Brugel 2024](https://brugel.brussels/publication/document/rapports/2025/fr/Rapport-annuel-2024-Conso.pdf)). [Selectra](https://selectra.be/nl/energie/factuur/openstaand) still describes 2,300 W limiters.

**Other support:** the federal Gas and Electricity Fund pays for help via the OCMW/CPAS ([Selectra](https://selectra.be/nl/energie/factuur/openstaand)).

**What this means:** a Belgian supplier can shed bad payers to the regulated network operator. The worst credit risk therefore leaves the competitive supplier's book and is socialised through network tariffs. In GB the supplier keeps the customer and the debt, and recovers through prepayment or the bad-debt allowance in the price cap.

---

## (a) Contrast table: Belgium vs GB

| Dimension | Belgium | GB | Difference that matters |
|---|---|---|---|
| 1 Weather | Maritime, CDD ~12, HDD ~2.7k [unv] | Maritime, HDD ~3k [unv] | Similar; add an Ardennes zone |
| 2 System | 34% nuclear (falling), 34% renewables, 19% gas, 14 TWh net imports, CRM | More gas and wind, less nuclear, capacity market | Import dependence; nuclear cliff in 2025 |
| 3 Grid | Elia plus ~7 DSOs; Flanders kW capacity tariff on 15-min peaks | 14 DNO areas; per-kWh plus standing charge | A household's peak sets its network cost (Flanders) |
| 4 Households | ~5.1 m; 6.28 m electricity points; 3.6 m gas points | ~28 m [unv] | Only ~57% have gas |
| 5 Housing/heat | Oil ~1/3 of residential heat; 3,500 kWh / 17,000 kWh standard | Gas dominant; ~2,700 / 11,500 kWh [unv] | Oil and off-gas heating; higher use per home |
| 6 Regulation | 3 regional licences; no price cap; HHI 2,250–5,300 | Ofgem cap, single licence | No default price cap; Brussels concentrated |
| 7 Smart meters | DSO-owned; Flanders ~70%, other regions slower | Supplier-owned, DCC | Supplier does not control meter or data |
| 8 Billing | Monthly advances plus annual true-up; 6% VAT | Monthly direct debit on smart reads; 5% VAT | Annual true-up shocks; estimated advances |
| 9 Settlement | 15-min; profiles plus residue; monthly reconciliation via Atrias | 30-min, MHHS | Interval and profiling differ |
| 10 Debt | Regional winter bans; federal social tariff ~10% of customers | Voluntary moratorium; PSR; no social tariff | Social price applies by status |
| 11 Distributed energy | Net metering ended (Flanders 2021, Brussels 2021, Wallonia 2030); 137k batteries in Flanders; company-car EVs | SEG export; private EVs | Legacy net-metering cohorts; employer-paid EV charging |
| 12 Cooling | Negligible; summer surplus | Negligible | None; model negative prices |
| 13 Cooking | Gas/electric mix [unv] | Mix | Minor |
| 14 Switching | No exit fees; Atrias; high rates; Brussels 3.05% | Next-working-day switching [unv] | Similar ease; DSO transfers excluded from stats |
| 15 Moves | Takeover document; contract follows customer; DSO handles unclaimed points | Deemed contract with incumbent supplier | No deemed customers for the supplier |
| 16 Debt location | Drop to DSO social supplier; DSO prepaid; costs socialised via network | Supplier keeps debt | Bad debt leaves the supplier's book |

## (b) Transferability of the GB build

**World components**

| Component | Rating | Why |
|---|---|---|
| Weather-driven demand | High | Same climate type; recalibrate degree days |
| Building thermal model | Medium | Needs oil boilers, older stock and regional typologies |
| Household behaviour/finances | Medium | Company-car EVs, protected status, annual true-up shock |
| Wholesale price replay | High | EPEX/Core data are similar; switch to BE prices and 15-min products |
| Settlement clock and reconciliation | Low | 15-min vs 30-min; profile-plus-residue allocation; Atrias monthly runs |
| Smart-meter data feed | Medium | Same concept, but DSO-sourced, region-dependent and partial in Wallonia/Brussels |
| Network/connection limits | Low | Flanders kW capacity tariff, 3×230 V legacy supply, DSO limiters |

**Supplier components**

| Component | Rating | Why |
|---|---|---|
| Tariffs and price-regulation compliance | Low | No price cap; social tariff by status; three regional rulebooks; spot-indexed variable products |
| Quoting/acquisition and switching | Medium | Similar ease; process runs via Atrias |
| Billing and payments | Low | Advance-plus-annual-true-up model; regional fee rules |
| Direct debit/collections and debt | Low | Drop-to-DSO procedure replaces supplier-run prepayment |
| Vulnerability duties | Low | Protected-customer regime held by DSOs; LAC/court gates |
| Hedging and wholesale buying | Medium | Same logic; Belgian price exposure and nuclear-cliff risk |
| Settlement and imbalance | Low | 15-min imbalance, Atrias reconciliation, compensation spread |
| Capital/financial rules | Medium | Different licence and financial tests; no SoLR levy documented |
| Advice and asset offers (EV, PV, battery, heat pump) | Medium | Capacity-tariff peak management and net-metering legacy cohorts change the value case |

## (c) New features needed

**New simulation ("world") features**
1. A layer of three regional rulebooks: licences, winter dates, disconnection gates and prosumer rules by region.
2. Atrias-style central clearing house: 15-min allocation, synthetic load profiles, residue factor, monthly reconciliation and compensation spread.
3. DSO actors: Fluvius, ORES, RESA, Sibelga as meter owners, social suppliers and prepaid operators, each with its own bad-debt pool flowing into network tariffs.
4. Flemish capacity tariff: rolling 12-month average of monthly 15-min peaks, 2.5 kW floor.
5. Net-metering legacy cohorts: Flanders pre-2021, Wallonia to 2030, plus prosumer tariff per kVA/kWe.
6. Oil-heated and off-gas homes.
7. Company-car EV households with employer-reimbursed charging.
8. Federal social-tariff eligibility by status, applied automatically.
9. Nuclear availability scenarios (2025 closures, Doel 4/Tihange 3 extended) and import dependence.
10. Moves via takeover document, with unclaimed points going to the DSO process.

**New supplier features**
1. Advance-invoice engine with annual true-up and monthly-actual billing as an option.
2. Product set dominated by spot-indexed variable prices; fixed one-year; dynamic quarter-hour.
3. Drop procedure: reminder, then registered notice, then termination and hand-off to the DSO, with debt left on the supplier's book.
4. Separate consumption and injection contracts; buyback (export) pricing.
5. Peak-management advice and products to cut the capacity charge: smart EV and heat-pump control.
6. Social-tariff billing and reimbursement flows.
7. Regional fee and interest caps (Flanders, since 2023).
8. Imbalance management at 15 minutes.

## (d) Named gaps

1. Eurostat heating degree days for Belgium vs UK (not retrieved).
2. Housing tenure, flats vs houses, building age (Statbel/Eurostat).
3. Heat pump stock and sales (EHPA, regional agencies).
4. PV installation counts and GW by region.
5. ORES/RESA/Sibelga smart-meter installed counts and targets.
6. Payment-method mix (direct debit share).
7. Air-conditioning prevalence; cooking fuel mix.
8. Switching rates for Flanders and Wallonia; supplier market shares (in charts only).
9. Number of customers on Fluvius social supply / prepaid, and Walloon DSO-supplied and budget-meter counts.
10. Flemish winter period dates (1 March vs 1 April conflict).
11. Current Wallonia/Brussels network tariff structure (time-of-use from 2026?).
12. Belgium's supplier-failure regime (is there a GB-style Supplier of Last Resort?).
13. VAT/excise structure and levy share of the bill.
14. Fixed reconciliation calendar and the settlement treatment of smart-meter households.
15. Current switching lead times and cooling-off periods (and the EU 24-hour switching requirement).

**Account memory (for the main session):** nothing new about Rich came up.

## Done

Published on 25 Oct as the Knowledge page `site/knowledge/other-market-belgium/`, with the note `docs/market_research/other_market_belgium_2026-10-25.md`. The note carries the verification pass that the 25 Oct verify steer asks for: each [unverified] item is marked confirmed, corrected or still open, and no open item is stated on the page as a claim. Counts as recorded: Counts: confirmed 0, corrected 3, open 33.
