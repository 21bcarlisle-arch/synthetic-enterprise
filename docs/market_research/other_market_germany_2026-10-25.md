# Germany compared with GB: household energy market (knowledge only)

**Knowledge:** other-market-germany

**Status:** knowledge only. The director, 25 Oct 2026 07:17 GMT: "this is not to turn into SIM or supplier action at this stage it just to understand how transferable what we are building in the UK is to other markets and where new SIM and new supplier features would have to be built." Build nothing from this note.

**Provenance:** the advisor's cited evidence pack `docs/staging/advisor/done/DIRECTOR_EVIDENCE_OTHER_MARKET_GERMANY_VS_GB_2026-10-25.md`, kept below as written (its [unverified] and [derived] tags stand), followed by the verification pass made while drafting the page.

---

# Germany vs GB: household energy market evidence pack for Poesys

**Purpose:** To set out how Germany's household energy market differs from GB's, and so how well the GB build would transfer. This pack is for understanding only. It is not a build plan.
**Prepared:** 25 Oct 2026.

**How to read the tags:**
- **[derived]** means my own arithmetic.
- **[unverified]** means a figure from memory that I could not check in this session.

**Research limits:**
- The shared web-search allowance ran out before the work was finished. Some items rest on fewer sources than planned and are marked.
- The statute site gesetze-im-internet.de and Eurostat's data API were blocked in this session, so some legal and climate details come from secondary sources.
- I did not re-check the GB comparison figures in this session. They are marked [unverified] and should be checked against Ofgem and DESNZ sources.

---

## 1. Weather and climate

- **Cooling degree days (CDD):** Germany had **19.3 CDD in 2024**, from Eurostat dataset nrg_chdd_a via https://db.nomics.world/Eurostat/nrg_chdd_a. One secondary source says German CDD fell 63% between 2018 and 2024 (https://germanpedia.com/?p=23501). That shows how much one hot summer moves a small number.
- **Heating degree days (HDD):** I could not get Germany's annual HDD from Eurostat in this session. Germany is roughly **~3,000 HDD per year** in Eurostat's method, about the same as or slightly above GB [unverified].
- **Climate differences from GB:**
  - Germany is more continental than GB, especially in the east and south (Bavaria and Saxony). Winters are colder and summers warmer [unverified].
  - The spread between regions is wider than in GB. Mountain and southern-interior sites run colder than the North Sea coast [unverified].
  - Solar resource is clearly better in the south, which matters for photovoltaic (PV) yield [unverified].
- **Seasonal demand:** Demand is strongly winter-led because 56% of homes heat with gas and 17% with oil (see §5). Electricity demand is flatter across the year than gas demand. Heat-pump growth will steepen electricity's winter peak.
- **Cooling load:** Small, as in GB. See §12.

**What this means for Poesys:** GB's weather-driven demand model can be re-parameterised for Germany, but it needs a wider regional spread and a continental temperature range. It also needs a solar-irradiance driver, because self-consumed PV takes a large and visible share of household demand.

## 2. Energy system

**Generation mix, 2025** (Fraunhofer ISE, https://www.ise.fraunhofer.de/content/dam/ise/en/documents/press-releases/2026/0126_ISE_e_PR_Net%20electricity%20generation%202025.pdf, and https://www.ise.fraunhofer.de/en/press-media/press-releases/2026/german-public-electricity-generation-in-2025-wind-and-solar-power-take-the-lead.html):
- Renewables were **55.9%** of net public generation, the same as in 2024.
- **Wind** produced 132 TWh: about 106 TWh onshore and about 26 TWh offshore.
- **Solar** produced about 87 TWh, of which 16.9 TWh was self-consumed. That is up 21% and, for the first time, ahead of lignite.
- **Lignite** produced 67.2 TWh and **hard coal** 26.7 TWh.
- **Public gas** produced 52.4 TWh, plus 26.1 TWh of industrial gas generation.
- **Biomass** produced about 41 TWh and **hydro** about 17.8 TWh.
- **Nuclear** produced nothing; Germany's last plants closed in April 2023 [unverified date].
- **Trade:** Germany imported 76.2 TWh and exported 54.3 TWh, a **net import of 21.9 TWh**. The main sources were Denmark, France, the Netherlands and Norway.
- **Capacity:** Installed PV was **116.8 GW DC** at the end of 2025. Batteries totalled just under 25 GWh, of which about 20 GWh was **home storage**.

**Comparison with GB:**
- Germany still burns coal and lignite (about 94 TWh); GB has none since its last coal plant closed in 2024 [unverified].
- Gas sets the marginal price in both countries.
- Germany's distributed PV fleet is several times larger than GB's [unverified].

**Wholesale market:**
- **Market design:** An energy-only market with a single bidding zone shared by Germany and Luxembourg (DE-LU), coupled with neighbouring zones. Germany has no nodal pricing, which mirrors GB's single national price [unverified on DE-LU detail].
- **Prices:** The 2025 average day-ahead price was **€86.55/MWh** and the average intraday price was €89.38/MWh (Fraunhofer, above).
- **Trading interval:** The day-ahead market has traded in **15-minute products since October 2025** (https://www.innobu.com/en/articles/zsg-quarter-hour-balancing-2026.html). GB trades in half-hours.
- **Gas hub:** Germany's single gas market area, **Trading Hub Europe (THE)**, was formed in October 2021 by merging the two earlier areas, NCG and Gaspool (https://www.eex.com/fileadmin/Global/News/EEX/EEX_Press_Release/2021/20211004_EEX_PR_THE.pdf). It plays the role GB's NBP plays.
- **Household price caps:** There is no Ofgem-style cap. The 2023 crisis brakes are covered in §6.

## 3. Grid

- **Network structure:** Germany has **four transmission system operators (TSOs)**. **819 distribution system operators (DSOs)** took part in the BNetzA (Bundesnetzagentur, the federal regulator) 2025 monitoring survey (https://data.bundesnetzagentur.de/Bundesnetzagentur/SharedDocs/Mediathek/Monitoringberichte/MonitoringberichtEnergie2025.pdf). The often-quoted "~850+" includes operators that did not respond. GB has 1 system operator, 3 TSOs and 14 licensed DNO areas plus IDNOs [unverified]. Many German DSOs are municipal companies (*Stadtwerke*) that are linked to the local default supplier.
- **Household connection:**
  - Three-phase supply (*Drehstrom*, 230/400 V) is the norm for German homes [unverified as a national statistic].
  - One DSO's technical connection rules show service boxes rated up to 80 A and direct metering up to **63 A** (42 kW intermittent). Continuous loads such as chargers are limited to 44 A (https://www.gipsprojekt.de/featureGips/sw_gt/EnwgTool/Stromnetz/Netzanschluss/Technische_Mindestanforderungen/Techn-Anschlussbed-Niederspannung-November2022.pdf).
  - GB homes are typically single-phase with a 60–100 A service fuse [unverified].
  - Germany has **no contracted-capacity (kVA) subscription** of the French or Italian kind.
- **Network tariffs:**
  - Household network charges are a standing charge plus a per-kWh charge. In 2025 the average was **10.72 ct/kWh** for households using 2,500–5,000 kWh (BNetzA Monitoringbericht 2025, above). Charges vary widely by DSO.
  - Under **§14a EnWG** (Energy Industry Act), heat pumps, wallboxes, batteries and air conditioners above **4.2 kW** that are commissioned from 1 Jan 2024 are automatically "controllable". The DSO may dim them to 4.2 kW but not switch them off. Existing devices have a transition period to the end of 2028.
  - In exchange the household gets a network-fee reduction, in one of three forms:
    - **Module 1:** a flat €110–190 per year.
    - **Module 2:** 60% off the per-kWh network charge, which needs a separate meter point.
    - **Module 3:** time-of-use network charges, which DSOs must offer from **April 2025**. Module 3 needs a smart meter and can only be combined with Module 1.
  - Source: https://ema-energiewelt.de/wissen/netzentgelte-paragraph-14a-steuerbare-verbraucher-2026.
  - At 31 Dec 2024 there were **264,874** market locations under the new §14a regime: 239,825 on Module 1 and 25,049 on Module 2. About **1.92 million** older devices were controllable voluntarily under the previous rules (BNetzA Monitoringbericht 2025).
  - GB has no comparable statutory control-for-discount regime for network charges [unverified]. Its time-of-use network signal comes through DUoS charges [unverified].

## 4. Population and households

- **Households:** **40.8 million** private households, averaging **2.02 persons**. **41.6%** are single-person households, about 17.0 million (Destatis Mikrozensus 2024, via https://www.drweb.de/41-millionen-haushalte-wie-deutschland-wirklich-wohnt/).
- **Population:** About 84.4 million (2025), from https://knoema.com/atlas/Germany/topics/Climate/datasets.
- **GB comparison:** About 28 million households averaging about 2.4 persons [unverified]. German households are about 45% more numerous and smaller.
- **Urbanisation:** The settlement pattern is polycentric. Many medium-sized towns have their own *Stadtwerk* [unverified].

## 5. Housing and heating

- **Tenure:** **53% of Germans are tenants**, the highest share in the EU, where the average is 32% (Eurostat 2024, https://ec.europa.eu/eurostat/web/interactive-publications/housing). GB's figure is about 35% [unverified]. Germany's high renting share matters for:
  - who controls heating and appliances;
  - landlord-tenant split incentives;
  - *Mieterstrom* (landlord-to-tenant PV supply);
  - shared building heating billed through service charges (*Nebenkosten*) rather than an energy contract [unverified].
- **Flats vs houses:** Germany's split was not visible in the source. Germany has one of the EU's higher shares of people living in flats [unverified].
- **Heating fuel**, housing stock 2025, 43.8 million dwellings (BDEW, https://www.bdew.de/media/documents/Wohnungsbestand_Beheizungsstruktur_2025_online_o_dw_jaehrlich_CMi_19062026.pdf):

| Heating fuel | Share of dwellings |
|---|---|
| Gas | 56.1% |
| Heating oil | 17.2% |
| District heating | 15.5% |
| Heat pumps plus solar thermal and geothermal | 4.5% |
| Wood | 4.1% |
| Direct electric and night storage | 2.5% |

  - **GB comparison:** About 85% gas, very little district heating and about 4% oil [unverified]. Oil and district heating together cover **about one third of German homes** [derived: 17.2 + 15.5 = 32.7%].
- **Boiler stock:**
  - **14.8 million** gas boilers and **4.7 million** oil boilers.
  - More than 86% of non-condensing oil boilers are over 20 years old.
  - Source: chimney-sweep data, https://www.solarserver.de/2026/05/22/heizungsbestand-2025-waermewende-stockt/.
- **New homes:** About three-quarters of new one- and two-family houses use heat pumps. In new multi-family buildings, heat pumps plus district heating make up about 70% (https://www.solarserver.de/2025/10/22/waermepumpe-und-fernwaerme-ueberwiegen-im-neubau-bestand-bleibt-problem/).
- **Electricity consumption:**
  - BDEW guideline values by household size: 1 person 1,900 kWh, 2 persons 2,890, 3 persons 3,720, 4 persons 4,085 (https://www.bdew.de/presse/pressemappen/faq-energieeffizienz/).
  - **3,500 kWh** is the standard reference household for price statistics.
  - Check24 contracts, which are not representative: about 3,150 kWh electricity and about 19,000 kWh gas in 2023 (https://www.cio.de/article/3696617/haushalte-haben-2023-mehr-strom-und-gas-verbraucht.html).
  - **GB comparison:** Ofgem's typical domestic consumption values are about 2,700 kWh electricity and 11,500 kWh gas [unverified]. German gas homes appear to use materially more gas.

## 6. Core regulation

- **Competition:** The market is fully liberalised. In 2024 households could choose from **139 electricity suppliers** and **108 gas suppliers** (https://www.bundesnetzagentur.de/SharedDocs/Pressemitteilungen/DE/2025/20251126_Monitoringbericht.html).
- **Market structure:** Concentration is low nationally but high locally, because the incumbent default supplier holds most customers in its own area. Household consumption in 2024 split three ways (Monitoringbericht 2025):

| Contract type | Share of household consumption, 2024 |
|---|---|
| Basic supply (*Grundversorgung*) | ~22% (2023: 25%) |
| Other contract with the local default supplier | ~38% |
| Contract with a different supplier | ~40% |

  - One BNetzA press release gives 23% for basic supply on a different base (https://www.bundesnetzagentur.de/SharedDocs/Pressemitteilungen/DE/2025/20250714_MB2025.html).
- **Default supplier and basic supply (§36 EnWG, https://lxgesetze.de/enwg/36):**
  - In each network area, the supplier with the **most household customers** is the default supplier (*Grundversorger*). The DSO re-determines this every three years.
  - The default supplier must supply any household on published general terms and prices.
  - **Since 2022 it may not set different prices by contract start date.** This ended the split pricing between old and new basic-supply customers used in 2021–22.
  - **Prices are not set by the regulator.** They are reviewable only for fairness under civil law. This is unlike GB's Ofgem cap.
- **Fallback supply (*Ersatzversorgung*):** Covers customers who start taking energy without a contract, or whose supplier drops out. It lasts up to **three months**, after which the customer moves to basic supply (§36 exception, same source).
- **Supplier failures:** In late December 2021, Stromio and gas.de stopped supplying. **"Hundreds of thousands"** of customers fell to default suppliers, some at special prices such as **54.29 ct/kWh** against 28.99 ct/kWh basic supply (https://www.zfk.de/unternehmen/nachrichten/enviam-stromio-kunden-ersatzversorgung).
  - Germany has **no Supplier of Last Resort (SoLR) auction and no mutualised levy for failures** like GB's. The local default supplier simply absorbs the customers [unverified on the absence of a levy].
  - Supplier entry needs only notification to BNetzA, which can prohibit a supplier for unreliability. There is no GB-style financial-resilience licence regime [unverified].
- **Crisis price brakes, 2023:**
  - Electricity was capped at **40 ct/kWh** and gas at **12 ct/kWh**, on **80%** of reference consumption. District heating was capped at 9.5 ct/kWh.
  - They started in March 2023 and were backdated to January (https://www.igmetall.de/politik-und-gesellschaft/umwelt-und-energie/so-funktioniert-die-strom-und-gaspreisbremse).
  - They ended on 31 Dec 2023 [unverified].
  - Suppliers worked the relief out per customer and claimed it back from the state. GB's Energy Price Guarantee was a per-unit discount instead [unverified].
- **Removal of the renewables levy:** Renewables support under the EEG (Renewable Energy Sources Act) has been paid from the federal Climate and Transformation Fund (KTF) since **1 July 2022**, so the EEG levy on bills fell to zero (https://www.bundesfinanzministerium.de/Content/DE/Pressemitteilungen/Finanzpolitik/2022/07/2022-07-27-klima-und-transformationsfonds.html).

## 7. Smart meters

- **The law:** The 2023 law restarting energy digitisation (GNDEW) set:
  - a rollout path of 20% of mandatory cases by 2025, 50% by 2028 and 95% by 2030;
  - mandatory installation for homes using more than 6,000 kWh, PV above 7 kW, and §14a devices;
  - a household price cap of about €20 per year [all unverified; the primary source could not be fetched].
- **Rollout status:** At 30 June 2026 there were **3,172,579 smart metering systems**, **5.9% of 54.1 million metering points**. BNetzA has opened proceedings against **434 meter operators** that missed the 20% quota. The target is 90% of mandatory cases by 2032 (https://www.bundesnetzagentur.de/SharedDocs/Pressemitteilungen/DE/2026/20260921_Rollout.html). GB has about two-thirds of meters smart [unverified].
- **Technology:** An *intelligentes Messsystem* is a digital meter plus a BSI-certified smart meter gateway, which is the secure communications hub. A *moderne Messeinrichtung* is a digital meter with no communications.
- **Who owns and runs the meter:** The **meter operator** (*Messstellenbetreiber*). By default this is the DSO acting as the "basic responsible" meter operator. The customer can choose a competitive meter operator instead. This differs from GB, where the supplier is responsible for meters [unverified on detail].
- **Data granularity:** 15-minute data with a smart meter. Without one, an annual read.

## 8. Billing

- **Billing basis:** The norm is **estimated monthly advance payments (*Abschlag*) plus an annual true-up bill (*Jahresabrechnung*)**, based on an annual meter reading. Customers may opt for monthly, quarterly or half-yearly bills, and smart-meter customers get more frequent billing information under §40b EnWG [unverified; the statute could not be fetched]. GB bills monthly or quarterly on actual or estimated reads, and direct debit amounts are reviewed periodically [unverified].
- **Price build-up, 2025:** A new-customer household on 3,500 kWh pays **39.6 ct/kWh** (BDEW, https://www.bdew.de/media/documents/BDEW_Strompreisanalyse_102025.pdf):

| Component | ct/kWh | Share |
|---|---|---|
| Energy procurement and supplier margin | 16.0 | 40.4% |
| Network charges | 10.9 | 27.6% |
| Taxes, levies and surcharges | 12.7 | **32.0%** |

  - The taxes and levies break down as:
    - VAT (19%): 6.33 ct/kWh
    - Electricity tax (*Stromsteuer*): 2.05 ct/kWh
    - Concession fee to the municipality: 1.67 ct/kWh
    - §19 grid surcharge: 1.56 ct/kWh
    - Offshore grid levy: 0.82 ct/kWh
    - CHP levy: 0.28 ct/kWh
  - The annual bill comes to about **€1,386** [derived].
  - The BNetzA average across all households was **40.1 ct/kWh** in April 2025. The gas average was 12.13 ct/kWh.
  - GB electricity is roughly 25 p/kWh with 5% VAT [unverified].
- **Payment methods:** SEPA direct debit and bank transfer dominate [unverified]. **Prepayment is marginal**: only **11,985** basic-supply households were on prepayment (*Vorkasse*) systems in 2024 (Monitoringbericht 2025). GB has about 4 million prepayment meters [unverified].

## 9. Settlement

- **Settlement interval:** Electricity balancing uses **15-minute** periods, against GB's 30 minutes.
- **Household profiling:** Most households are settled on **standard load profiles (SLP, e.g. H0)**, which spread one annual volume across the quarter-hours.
- **Measured settlement:** Measured quarter-hour settlement for smart-metered customers began on **6 June 2025** under BNetzA ruling BK6-24-174 (https://www.innobu.com/en/articles/zsg-quarter-hour-balancing-2026.html).
- **Balance responsibility:**
  - Suppliers sit in **balancing groups (*Bilanzkreise*)** run by a balance-responsible party. There are about 900 balancing groups.
  - Today **each DSO aggregates the settlement data** for its own area, and the four TSOs settle imbalances.
  - A central settlement hub (the MaBiS-Hub, run by the TSO consortium) is planned. Test systems are expected from July 2028 and parallel running from January 2029, but this is not yet decided (https://www.innobu.com/en/articles/mabis-hub-balancing-settlement-2028.html).
  - **GB comparison:** Elexon centralises settlement, and the MHHS move to half-hourly settlement for all is under way [unverified timings].
- **Reconciliation:** Differences between profiled and actual volumes are trued up after the annual read through DSO volume-difference billing (*Mehr-/Mindermengenabrechnung*) [unverified on detail; timeline not found]. GB's equivalent runs through its reconciliation runs up to about 14 months [unverified].

## 10. Debt and vulnerability

- **Scale, electricity, 2024** (Monitoringbericht 2025):
  - **4.6 million disconnection threats**, up from 3.8 million.
  - **981,000** disconnection orders.
  - **239,269 disconnections actually carried out by network operators**, up from 204,441.
- **Gas, 2024:** 33,700 disconnections (https://www.bundesnetzagentur.de/SharedDocs/Pressemitteilungen/DE/2025/20250714_MB2025.html).
- **Ratios [derived]:** About 21% of threats become orders, and about 5.2% end in a disconnection.
- **Disconnection rules in basic supply (§19 StromGVV, the basic-supply regulation, via a secondary source):**
  - Arrears must be at least **€100**.
  - A reminder, then a written threat, then a **four-week** wait.
  - The disconnection date must be announced **three working days** ahead.
  - Disconnection is barred where it would be disproportionate, for example health risks or vulnerable occupants, or where the customer shows a realistic prospect of paying (https://anwalt-kg.de/insolvenzrecht/rechtlichen-handlungsoptionen-bei-stromschulden/).
  - The law since 2022 also requires an instalment offer that would avoid disconnection (*Abwendungsvereinbarung*) [unverified].
- **Winter:** There is **no statutory winter ban** [unverified]. GB has voluntary winter protections and a ban on forced prepayment installs [unverified].
- **Social support:** Germany has **no social tariff and no Warm Home Discount equivalent** [unverified].
  - Electricity is covered inside the welfare benefit's standard rate (*Bürgergeld*), about €50 per month for a single adult in 2025.
  - Heating, including electric heating, is paid as housing costs.
  - Job centres may lend money to prevent a disconnection (https://www.gegen-hartz.de/news/buergergeld-wann-muss-das-jobcenter-die-stromkosten-zahlen).
- **Vulnerable-customer register:** No PSR-style register was found [unverified].

## 11. EVs, PV, batteries and heat pumps

- **Electric vehicles:** **2,034,260 battery EVs** (4.1% of 49.5 million cars) and 1,122,958 plug-in hybrids at 1 Jan 2026 (https://www.electrive.net/2026/02/27/endlich-ueber-zwei-millionen-elektroautos-auf-deutschen-strassen/).
- **PV:**
  - **5.71 million PV systems** are registered, of which about 4.47 million are on buildings.
  - **2.4 million home batteries** (over 25 GWh), with about 600,000 added in 2025.
  - **1.22 million balcony PV units** (about 1.2 GW).
  - PV supplied 16.8% of net generation.
  - Source: https://strom-report.com/photovoltaik/.
  - GB comparison: about 1.5–2 million PV homes [unverified].
- **Balcony solar (*Balkonkraftwerk*):** Under the 2024 Solar Package I:
  - inverters may run at up to **800 W**, with modules up to 2,000 W;
  - registration is only a simplified entry in the national plant register (*Marktstammdatenregister*), with no separate DSO registration;
  - older meters without a backstop may temporarily run backwards;
  - standard household (Schuko) plugs are to be allowed.
  - Source: https://t3n.de/news/balkonkraftwerke-regeln-2024-800-watt-schukostecker-solarpaket-boom-1596828/.
- **Feed-in tariff:** About **7.94 ct/kWh** for systems up to 10 kWp from Feb 2025.
- **"Solar peaks" law (*Solarspitzengesetz*, from 25 Feb 2025):**
  - New systems get **no payment during negative-price hours**; the lost hours are added at the end of the 20-year term.
  - New systems without a smart meter may feed in at most **60%** of rated power.
  - Source: https://www.co2online.de/modernisieren-und-bauen/photovoltaik/solarspitzengesetz/.
- **Support model:** Self-consumption plus a feed-in tariff, with **no net metering**. GB has the Smart Export Guarantee, which is set by suppliers [unverified].
- **Heat pumps:**
  - **299,000** heating heat pumps were sold in 2025, up 55%.
  - KfW (the state development bank) made **288,000** funding commitments.
  - About 80% go into existing buildings.
  - Source: https://www.solarserver.de/2026/01/27/bwp-waermepumpen-absatz-um-55-prozent-in-2025-gestiegen/.
  - GB sells roughly 60–100k a year [unverified].

## 12. Cooling (added scope)

- CDD were **19.3 in 2024** (DBnomics/Eurostat, above), which is small.
- Residential air-conditioning is uncommon, single-digit to low-teens percent of homes [unverified]. There is no figure from a national statistics source in this pack.
- The national peak is in winter [unverified]. Summer midday is dominated by surplus PV and negative prices rather than cooling demand.
- Air conditioners above 4.2 kW count as §14a controllable devices (§3).
- **Difference from GB:** Slightly more cooling load in the south and east. It is not material for the model, but heat-wave years should be represented.

## 13. Cooking (added scope)

- German household cooking is predominantly electric, with ceramic or glass hobs and a growing share of induction. Gas cooking is far less common than in GB [unverified; no source fetched].
- **Difference from GB:** GB gas homes often also cook with gas [unverified]. A German "gas customer" is mainly a heating and hot-water load, and cooking adds to baseline electricity.

## 14. Switching (added scope)

- **Process:** The **new supplier starts** the switch, as in GB.
- **24-hour switching:** Since **6 June 2025** (*LFW24*), the network operator, supplier and meter operator confirm a switch **within one working day**, down from up to three weeks before. It becomes fully mandatory from 1 Jan 2026. It covers **electricity only** for now (https://www.yello.de/wissen/energiemarkt/24-h-lieferantenwechsel/ ; https://vdiv.de/news-details/lfw24-neuer-24h-lieferantenwechsel-ab-6-juni-2025-aenderungen-und-handlungsbedarf-fuer-immobilienverwaltungen).
- **Contract notice periods are unchanged:**
  - Basic supply can be ended at **two weeks'** notice [unverified].
  - Special contracts often have a 12-month minimum term, then monthly notice [unverified].
  - Distance contracts carry a **14-day withdrawal right (*Widerruf*)** [unverified].
- **Blocking:** No GB-style objection right for debt was found [unverified].
- **Switching rates, 2024:**
  - Electricity: about **14%** (7.1 million switches), plus 3.3 million contract changes with the existing supplier.
  - Gas: about **17–18%** (2.2–2.3 million).
  - Source: Monitoringbericht 2025.
- **Channel:** Comparison sites such as Check24 and Verivox drive the market. New-customer bonuses are widespread [unverified].

## 15. Home moves (added scope)

- **Who supplies a new occupant:** The new occupant needs a contract **by the move-in day at the latest**. Otherwise the supply point falls automatically into **basic supply** with the local default supplier, which is usually dearer.
- **No backdating:** Since LFW24, backdated registrations are no longer allowed. Move-in, move-out and supplier change have become one uniform process. Every supply point needs a market location ID (MaLo-ID), which the DSO must give within two hours on request.
- **Meter reads:** Readings at move-out and move-in should be exact to the day (vdiv source, above).
- **Final bills:** Issued after the move-out read. The legal deadline is about six weeks [unverified].
- **Empty properties:** Supply to vacant properties sits with the landlord or property manager.
- **Difference from GB:** Germany's default is a legally defined tariff of the local incumbent, rather than "deemed" supply by whichever supplier holds the meter point.

## 16. Where debt sits (added scope)

- **Who carries arrears risk:** The **supplier**. Arrears are a supplier receivable.
- **Who disconnects:** The **network operator** carries out the cut-off **on the supplier's instruction**. BNetzA counts 239,269 disconnections "carried out by network operators" in 2024 (Monitoringbericht 2025).
- **Disconnection rights outside basic supply:** For special contracts, the right to have supply cut depends on the contract. Suppliers often terminate the contract instead, which sends the customer back to basic supply. In 2024 there were **236,195** such terminations, 20,146 of them within basic supply (Monitoringbericht 2025).
- **Who funds bad debt:** The supplier, through its margin. There is **no central bad-debt mechanism and no allowance in a regulated price** like GB's cap allowance [unverified on absence]. Network charges billed through the supplier are owed by the supplier to the DSO whatever the customer pays [unverified].
- **Does debt follow the customer?** No. The old supplier keeps the debt and pursues it through collections or the courts [unverified]. There is no GB-style transfer of prepayment debt.
- **Credit checks:** Suppliers commonly run SCHUFA credit checks before taking a customer [unverified], which shifts risky customers toward basic supply.

---

## (a) Contrast table: Germany vs GB

| Dimension | Germany | GB | Difference that matters |
|---|---|---|---|
| 1. Weather | Continental; CDD 19.3 (2024); HDD ~3,000 [unverified] | Maritime; similar HDD [unverified] | Wider regional and temperature spread; strong solar driver |
| 2. Energy system | 55.9% renewables; coal and lignite remain; no nuclear; DE-LU zone; THE gas hub | No coal; nuclear; NBP | 15-min day-ahead market; PV-driven negative prices |
| 3. Grid | 4 TSOs, ~820–880 DSOs; 3-phase; §14a dimming plus fee modules | 14 DNO areas; 1-phase | Controllable-device regime and DSO-specific tariffs |
| 4. Households | 40.8m, 2.02 people, 41.6% single-person | ~28m, ~2.4 [unverified] | More, smaller households |
| 5. Housing | 53% tenants; gas 56%, oil 17%, district heating 15.5% | ~65% owners, ~85% gas [unverified] | Oil and district heating, landlord-run heating |
| 6. Regulation | Default-supplier basic supply, not price-capped; 139 suppliers | Ofgem price cap; SoLR | No cap to comply with; local incumbent default |
| 7. Smart meters | 5.9% of meters; DSO or chosen meter operator; secure gateway | ~65% [unverified]; supplier-led | Low coverage; supplier does not control the meter |
| 8. Billing | Monthly advance plus annual true-up; taxes and levies 32%; 19% VAT | Monthly or quarterly; 5% VAT | Annual true-up cycle; tax-heavy price |
| 9. Settlement | 15-min; SLP profiles; DSO-level aggregation | 30-min; Elexon; MHHS | Profiled household settlement and decentralised data |
| 10. Debt | 239k electricity disconnections; no social tariff | Prepayment-centric; WHD | Disconnection is a real tool; prepayment is negligible |
| 11. Assets | 2.0m BEVs; 5.7m PV; 2.4m batteries; 1.2m balcony PV; 299k heat pumps a year | Smaller [unverified] | Prosumers are mainstream |
| 12. Cooling | Small, south and east tilt | Small | Minor |
| 13. Cooking | Mostly electric [unverified] | Gas common [unverified] | Gas load is heat-only |
| 14. Switching | 24h back-end (electricity); ~14% switch rate | 5-day [unverified]; lower rate [unverified] | High churn, bonus-driven |
| 15. Home moves | No contract means basic supply; no backdating | Deemed contract | Default tariff is the incumbent's |
| 16. Where debt sits | Supplier; DSO disconnects on instruction; no mutualisation | Supplier; cap allowance | Bad debt not socialised |

## (b) Transferability of the GB build

**World components**

| Component | Rating | Why |
|---|---|---|
| Weather-driven demand | Medium | The method transfers; it needs a continental range, solar irradiance and German regions. |
| Building thermal model | Medium | The physics transfers; the stock mix (oil, district heating, multi-family) and German construction years differ. |
| Household behaviour and finances | Low–Medium | Renters, smaller households, an annual true-up shock, credit checks and bonus-chasing switchers. |
| Wholesale price replay | High | Swap in DE-LU and THE price series; resample to 15 minutes. |
| Settlement clock and reconciliation | Low | 15-min periods, SLP profiling, DSO-level aggregation and volume-difference billing. |
| Smart-meter data feed | Low | 5.9% coverage; most homes have one read a year; data comes through the meter operator. |
| Network and connection limits | Low–Medium | Three-phase connections, §14a 4.2 kW dimming, ~850 DSO tariffs. |

**Supplier components**

| Component | Rating | Why |
|---|---|---|
| Tariffs and price-regulation compliance | Low | No cap; the basic-supply equality rule; mandatory dynamic and fixed tariffs under §41a. |
| Quoting, acquisition and switching | Medium | Similar logic; needs 24h switching, comparison-site bonuses and a Widerruf window. |
| Billing and payments | Low | The Abschlag plus annual true-up cycle and a different tax stack. |
| Direct debit, collections and debt | Medium | Direct debit transfers; the disconnection route via the DSO and §19 steps are new. |
| Vulnerability duties | Low | No PSR or social tariff; proportionality tests and job-centre interplay instead. |
| Hedging and wholesale buying | Medium–High | Same instruments; 15-min shape and PV cannibalisation. |
| Settlement and imbalance | Low | Balancing-group model and SLP versus measured 15-min settlement. |
| Capital and financial rules | Low–Medium | No Ofgem financial-resilience regime [unverified]; failures land on the incumbent. |
| Advice and asset offers | Medium | Rich market, but §14a, the Solarspitzengesetz, balcony PV and KfW subsidies differ. |

## (c) New features needed

**New simulation (world) features**

1. 15-minute settlement clock and a 15-minute wholesale price series (DE-LU).
2. Standard load profile (H0) settlement path alongside measured settlement, with the share switching as smart meters roll out.
3. DSO-level settlement aggregation and volume-difference true-up after annual reads.
4. A DSO and network-area layer: ~850 tariffs, each area's default supplier, and municipal *Stadtwerke*.
5. §14a controllable devices: 4.2 kW dimming events, and Modules 1/2/3 with time-of-use network windows.
6. Three-phase connection model with per-phase and continuous-load limits.
7. Heating stock with oil tanks, district heating (billed outside the supplier) and multi-family central heating.
8. A tenure layer: landlord-controlled heating, service-charge billing, landlord-to-tenant PV.
9. Prosumer layer: rooftop PV, home batteries, balcony PV, the 60% feed-in cap, unpaid negative-price hours.
10. Annual meter-read events and an advance-payment true-up shock in household finances.
11. A separate meter-operator actor, the smart meter gateway, and data-access permissions.
12. Credit-check gating and a disconnection pipeline run by the DSO.
13. Stochastic supplier exits that move customers into fallback and basic supply.

**New supplier features**

1. Advance-payment setting and annual true-up billing at 19% VAT, with the full levy stack (electricity tax, concession fee, §19 and offshore surcharges).
2. Basic-supply mode, when the supplier is the default supplier, with published general prices and no pricing by contract start date. Fallback supply for up to three months.
3. Mandatory product set: a dynamic tariff for smart-meter customers (§41a), plus a 12-month fixed tariff for larger suppliers.
4. 24-hour switching, Widerruf handling, and move-in by the move-in day with no backdating.
5. Collections under §19: €100 threshold, four-week threat, three-working-day notice, instalment offer, proportionality check, and the instruction to the DSO.
6. Termination of special contracts, sending customers back to basic supply.
7. Balancing-group management and 15-min imbalance exposure.
8. Pass-through of §14a network modules and heat-pump tariffs.
9. Advice offers: PV, battery, balcony PV, heat pump with a KfW grant, wallbox, dynamic tariff with the smart-meter cost cap.
10. Billing district-heating and oil homes out of scope, with an electricity-only relationship.

## (d) Named gaps

1. **Heating degree days for Germany vs GB** on a like-for-like basis (Eurostat nrg_chdd_a, or DWD German weather service degree days) were not retrieved.
2. **Statute texts** were not read first-hand: §§13 and 19 StromGVV, §§38, 40b and 40c EnWG.
3. **GNDEW primary text** was not fetched: the 20/50/95% path, the €20 cap and mandatory groups are [unverified].
4. **Reconciliation timeline** for volume-difference billing and balancing deadlines was not found.
5. **Air-conditioning prevalence and cooking fuel mix:** no national statistics source was found.
6. **Flats vs houses split** and building age bands for Germany.
7. **Payment-method mix** (direct debit vs transfer) and arrears prevalence beyond the disconnection counts.
8. **Supplier concentration metrics:** the market shares of the largest suppliers.
9. **Supplier failure counts** for 2021–22, and whether any mutualisation applies.
10. **Gas disconnection threats** and gas prepayment.
11. **Dynamic tariff uptake** and actual Module 3 take-up.
12. **Heat-pump installed base**, which the chimney-sweep survey does not capture fully.
13. **All GB comparison figures** need re-checking against Ofgem and DESNZ sources.
14. **2026 levy and tax changes** were not verified: a possible federal subsidy of transmission charges, the gas storage levy, and any electricity-tax cut.

The shared web-search allowance for this turn ran out partway through. The items above can be followed up in a further pass.

---

## Verification of [unverified] items (drafting pass, 25 Oct 2026)

Per the director's steer of 25 Oct 07:52 GMT: each [unverified] item is confirmed, corrected or left open. Other-markets packs are the lowest priority, so only the headline items were fetched; the rest stay open and the page does not use them as claims.

- [unverified]** means a figure from memory that I could not check in this session.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- I did not re-check the GB comparison figures in this session. They are marked [unverified] and should be checked against Ofgem and DESNZ sources.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Heating degree days (HDD):** I could not get Germany's annual HDD from Eurostat in this session. Germany is roughly **~3,000 HDD per year** in Eurostat's method, about the same as or slightly above GB [unverified].
  - **corrected: ~3,000 -> 2,583 (2024); 2,580-3,130 over 2020-2025; Eurostat nrg_chdd_a via the dissemination API (unit NR), dataset updated 2026-05-08, accessed 2026-10-25**
- Germany is more continental than GB, especially in the east and south (Bavaria and Saxony). Winters are colder and summers warmer [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- The spread between regions is wider than in GB. Mountain and southern-interior sites run colder than the North Sea coast [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Solar resource is clearly better in the south, which matters for photovoltaic (PV) yield [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Nuclear** produced nothing; Germany's last plants closed in April 2023 [unverified date].
  - **confirmed: last three plants (Emsland, Isar II, Neckarwestheim II) shut 15 April 2023; Wikipedia 'Nuclear power in Germany', accessed 2026-10-25 (secondary source)**
- Germany still burns coal and lignite (about 94 TWh); GB has none since its last coal plant closed in 2024 [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Germany's distributed PV fleet is several times larger than GB's [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Market design:** An energy-only market with a single bidding zone shared by Germany and Luxembourg (DE-LU), coupled with neighbouring zones. Germany has no nodal pricing, which mirrors GB's single national price [unverified on DE-LU detail].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Network structure:** Germany has **four transmission system operators (TSOs)**. **819 distribution system operators (DSOs)** took part in the BNetzA (Bundesnetzagentur, the federal regulator) 2025 monitoring survey (https://data.bundesnetzagentur.de/Bundesnetz...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Three-phase supply (*Drehstrom*, 230/400 V) is the norm for German homes [unverified as a national statistic].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB homes are typically single-phase with a 60–100 A service fuse [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB has no comparable statutory control-for-discount regime for network charges [unverified]. Its time-of-use network signal comes through DUoS charges [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB comparison:** About 28 million households averaging about 2.4 persons [unverified]. German households are about 45% more numerous and smaller.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Urbanisation:** The settlement pattern is polycentric. Many medium-sized towns have their own *Stadtwerk* [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Tenure:** **53% of Germans are tenants**, the highest share in the EU, where the average is 32% (Eurostat 2024, https://ec.europa.eu/eurostat/web/interactive-publications/housing). GB's figure is about 35% [unverified]. Germany's high renting share matters for...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- shared building heating billed through service charges (*Nebenkosten*) rather than an energy contract [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Flats vs houses:** Germany's split was not visible in the source. Germany has one of the EU's higher shares of people living in flats [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB comparison:** About 85% gas, very little district heating and about 4% oil [unverified]. Oil and district heating together cover **about one third of German homes** [derived: 17.2 + 15.5 = 32.7%].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB comparison:** Ofgem's typical domestic consumption values are about 2,700 kWh electricity and 11,500 kWh gas [unverified]. German gas homes appear to use materially more gas.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Germany has **no Supplier of Last Resort (SoLR) auction and no mutualised levy for failures** like GB's. The local default supplier simply absorbs the customers [unverified on the absence of a levy].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Supplier entry needs only notification to BNetzA, which can prohibit a supplier for unreliability. There is no GB-style financial-resilience licence regime [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- They ended on 31 Dec 2023 [unverified].
  - **confirmed: ended 31 December 2023; caps 40 ct/kWh electricity and 12 ct/kWh gas on 80% of reference use, district heating 9.5 ct/kWh; bundesregierung.de Strom- und Gaspreisbremse page, accessed 2026-10-25**
- Suppliers worked the relief out per customer and claimed it back from the state. GB's Energy Price Guarantee was a per-unit discount instead [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- a household price cap of about €20 per year [all unverified; the primary source could not be fetched].
  - **corrected: the cap the regulator's page gives is 30 euros a year gross for an intelligent metering system up to 6,000 kWh (40 euros from 6,000-10,000 kWh), and 25 euros for a modern metering device; mandatory groups (>6,000 kWh, section 14a devices, generation >7 kW) confirmed; the 20/50/95% path is not on that page and stays open; bundesnetzagentur.de Vportal Metering page, accessed 2026-10-25**
- Rollout status:** At 30 June 2026 there were **3,172,579 smart metering systems**, **5.9% of 54.1 million metering points**. BNetzA has opened proceedings against **434 meter operators** that missed the 20% quota. The target is 90% of mandatory cases by 2032 (...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Who owns and runs the meter:** The **meter operator** (*Messstellenbetreiber*). By default this is the DSO acting as the "basic responsible" meter operator. The customer can choose a competitive meter operator instead. This differs from GB, where the supplier ...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Billing basis:** The norm is **estimated monthly advance payments (*Abschlag*) plus an annual true-up bill (*Jahresabrechnung*)**, based on an annual meter reading. Customers may opt for monthly, quarterly or half-yearly bills, and smart-meter customers get mo...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB electricity is roughly 25 p/kWh with 5% VAT [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Payment methods:** SEPA direct debit and bank transfer dominate [unverified]. **Prepayment is marginal**: only **11,985** basic-supply households were on prepayment (*Vorkasse*) systems in 2024 (Monitoringbericht 2025). GB has about 4 million prepayment meters...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB comparison:** Elexon centralises settlement, and the MHHS move to half-hourly settlement for all is under way [unverified timings].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Reconciliation:** Differences between profiled and actual volumes are trued up after the annual read through DSO volume-difference billing (*Mehr-/Mindermengenabrechnung*) [unverified on detail; timeline not found]. GB's equivalent runs through its reconciliat...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- The law since 2022 also requires an instalment offer that would avoid disconnection (*Abwendungsvereinbarung*) [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Winter:** There is **no statutory winter ban** [unverified]. GB has voluntary winter protections and a ban on forced prepayment installs [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Social support:** Germany has **no social tariff and no Warm Home Discount equivalent** [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Vulnerable-customer register:** No PSR-style register was found [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB comparison: about 1.5–2 million PV homes [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Support model:** Self-consumption plus a feed-in tariff, with **no net metering**. GB has the Smart Export Guarantee, which is set by suppliers [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB sells roughly 60–100k a year [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Residential air-conditioning is uncommon, single-digit to low-teens percent of homes [unverified]. There is no figure from a national statistics source in this pack.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- The national peak is in winter [unverified]. Summer midday is dominated by surplus PV and negative prices rather than cooling demand.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- German household cooking is predominantly electric, with ceramic or glass hobs and a growing share of induction. Gas cooking is far less common than in GB [unverified; no source fetched].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Difference from GB:** GB gas homes often also cook with gas [unverified]. A German "gas customer" is mainly a heating and hot-water load, and cooking adds to baseline electricity.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Basic supply can be ended at **two weeks'** notice [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Special contracts often have a 12-month minimum term, then monthly notice [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Distance contracts carry a **14-day withdrawal right (*Widerruf*)** [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Blocking:** No GB-style objection right for debt was found [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Channel:** Comparison sites such as Check24 and Verivox drive the market. New-customer bonuses are widespread [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Final bills:** Issued after the move-out read. The legal deadline is about six weeks [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Who funds bad debt:** The supplier, through its margin. There is **no central bad-debt mechanism and no allowance in a regulated price** like GB's cap allowance [unverified on absence]. Network charges billed through the supplier are owed by the supplier to th...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Does debt follow the customer?** No. The old supplier keeps the debt and pursues it through collections or the courts [unverified]. There is no GB-style transfer of prepayment debt.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Credit checks:** Suppliers commonly run SCHUFA credit checks before taking a customer [unverified], which shifts risky customers toward basic supply.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- 1. Weather | Continental; CDD 19.3 (2024); HDD ~3,000 [unverified] | Maritime; similar HDD [unverified] | Wider regional and temperature spread; strong solar driver
  - **confirmed (as a range): Eurostat still publishes UK degree days: UK HDD 2,710-2,961 over 2018-2025 (2024: 2,812) and CDD 0.1-7.0 (2024: 0.43); Eurostat nrg_chdd_a via the dissemination API (unit NR), dataset updated 2026-05-08, accessed 2026-10-25**
- 4. Households | 40.8m, 2.02 people, 41.6% single-person | ~28m, ~2.4 [unverified] | More, smaller households
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- 5. Housing | 53% tenants; gas 56%, oil 17%, district heating 15.5% | ~65% owners, ~85% gas [unverified] | Oil and district heating, landlord-run heating
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- 7. Smart meters | 5.9% of meters; DSO or chosen meter operator; secure gateway | ~65% [unverified]; supplier-led | Low coverage; supplier does not control the meter
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- 11. Assets | 2.0m BEVs; 5.7m PV; 2.4m batteries; 1.2m balcony PV; 299k heat pumps a year | Smaller [unverified] | Prosumers are mainstream
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- 13. Cooking | Mostly electric [unverified] | Gas common [unverified] | Gas load is heat-only
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- 14. Switching | 24h back-end (electricity); ~14% switch rate | 5-day [unverified]; lower rate [unverified] | High churn, bonus-driven
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Capital and financial rules | Low–Medium | No Ofgem financial-resilience regime [unverified]; failures land on the incumbent.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- 3. **GNDEW primary text** was not fetched: the 20/50/95% path, the €20 cap and mandatory groups are [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Eurostat CDD 2024 for Germany (sourced in the pack as 19.3 via DBnomics)
  - **corrected (sourced item, not tagged): 19.3 -> 19.02 (2024) in Eurostat's current release; Eurostat nrg_chdd_a via the dissemination API (unit NR), dataset updated 2026-05-08, accessed 2026-10-25**

**Counts:** confirmed 3, corrected 3, still open 57.
