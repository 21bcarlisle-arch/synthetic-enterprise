# Italy compared with GB: household energy market (knowledge only)

**Knowledge:** other-market-italy

**Status:** knowledge only. The director, 25 Oct 2026 07:17 GMT: "this is not to turn into SIM or supplier action at this stage it just to understand how transferable what we are building in the UK is to other markets and where new SIM and new supplier features would have to be built." Build nothing from this note.

**Provenance:** the advisor's cited evidence pack `docs/staging/advisor/done/DIRECTOR_EVIDENCE_OTHER_MARKET_ITALY_VS_GB_2026-10-25.md`, kept below as written (its [unverified] and [derived] tags stand), followed by the verification pass made while drafting the page.

---

# Italy vs GB: evidence pack for Poesys (knowledge only)

**Scope.** This pack compares Italy's household energy market with Great Britain's, to judge how much of the Poesys GB build carries over. It is not a build plan. It follows the 11 dimensions in the brief, plus dimensions 12–16 added by the coordinator.

**How to read it.**
- Figures confirmed from sources in this session carry a link.
- **[derived]** means my own arithmetic.
- **[unverified]** means it comes from memory and was not confirmed this session.
- GB comparison figures are from memory and are marked [unverified] unless a link is given.
- **Research limit:** the shared web-search budget ran out partway through. Several items stayed [unverified] because of that. They are listed under (d) Named gaps.

---

## 1. Weather and climate

- **No single national figure.** Italy's heating need is set by law through six climate zones, A to F, defined by annual degree days (DPR 412/93) ([luce-gas.it](https://luce-gas.it/guida/riscaldamento/accensione)):

  | Zone | Degree days | Example cities | Heating allowed | Max hours/day |
  |---|---|---|---|---|
  | A | under 600 | Lampedusa | 1 Dec – 15 Mar | 6 |
  | B | 600–900 | Palermo, Reggio Calabria | 1 Dec – 31 Mar | 8 |
  | C | 901–1,400 | Naples, Bari | 15 Nov – 31 Mar | 10 |
  | D | 1,401–2,100 | Rome, Florence, Genoa | 1 Nov – 15 Apr | 12 |
  | E | 2,101–3,000 | Milan, Turin, Bologna | 15 Oct – 15 Apr | 14 |
  | F | over 3,000 | Alpine areas | no limit | no limit |

  The same source says indoor temperature while heating is on must not exceed 20 °C (±2 °C).
- **A legal heating season is a structural difference.** GB has no rule on when central heating may run. Poesys would need a regulatory calendar layered on top of weather demand.
- **Comparators.** The Eurostat EU average is 3,199 HDD over 1979–2022 ([Eurostat SE](https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/92378.pdf)). Ireland, the nearest proxy for GB, averages 2,833 HDD and has CDD close to 0.03 (same source). Italy's national HDD is roughly 1,800–2,000 and its CDD roughly 200–450 [unverified: the Eurostat series could not be retrieved].
- **Regional spread.** Hours of heating use vary widely: 10h25 a day on average in the North-East against 6h34 in the South ([ISTAT 2021](https://www.istat.it/it/files/2022/06/REPORT-CONSUMI-ENERGETICI-FAMIGLIE-2021-DEF.pdf)).
- **Summer peak.** July 2026 set a monthly demand record of 32.5 TWh (+8.3% year on year). Peak demand was about 58 GW on 15 July, and the article credits air conditioning for the rise ([greenme/Terna](https://www.greenme.it/energia/record-di-consumi-elettrici-a-luglio-2026-in-italia-e-la-dipendenza-energetica-supera-il-75/)). Italy has a real summer electricity peak; GB's peak is in winter.

## 2. Energy system

**Electricity, 2024** ([Il Sole 24 Ore/Terna](https://en.ilsole24ore.com/art/consumi-elettrici-boom-rinnovabili-traino-idroelettrico-e-fotovoltaico-AG2nW2KC)):
- Demand was 312.3 TWh.
- Renewables covered 41.2% of demand.
- Net imports covered 16.3%.
- Solar produced more than 36 TWh.
- Coal output fell 71%.
- 7.48 GW of new capacity was added.

**Electricity, 2025** ([ARERA RA 2025 press release](https://www.arera.it/fileadmin/allegati/com_stampa/26/Comunicato_stampa_ARERA__I_numeri_della_Relazione_Annuale_2025.pdf)):
- Consumption was 312.4 TWh.
- Gross domestic production was 277.4 TWh, with renewables at 48% of the mix.
- Gas-fired generation rose 7%, solar rose 25% and hydro fell 21%.
- Renewable incentives cost about €9.3bn.

**Gas, 2025** (same source):
- Consumption was 62.1 bcm, and import dependence was 94.3%.
- LNG was 21.2 bcm, about a third of imports.
- Main suppliers: Algeria 36.1%, Azerbaijan 16.2%, the US 15.9%.

**Nuclear.** Italy has none [unverified: plants closed after the 1987 referendum]. Gas sets the marginal price far more often than in GB.

**Wholesale market design.**
- The day-ahead market (MGP), run by GME, is zonal.
- Final customers have been settled on zonal prices since 1 January 2025 (Decree 151/2024). During the transition, GME publishes a "PUN Index" and a perequation mechanism between dispatching users keeps settlement at PUN level, at least until 31 December 2025 ([QualEnergia](https://www.qualenergia.it/articoli/superamento-pun-gazzetta-avviso-mase/); [Argus](https://www.argusmedia.com/ja/news-and-insights/latest-market-news/2772776-italy-to-update-power-dispatching-rules)).
- ARERA Delibera 372/2025 cleared the way for 15-minute products in the day-ahead market ([ARERA](https://arera.it/atti-e-provvedimenti/dettaglio/25/372-25)).
- The bidding zones are Nord, Centro-Nord, Centro-Sud, Sud, Calabria, Sicilia and Sardegna [unverified].
- Italy also has a capacity market and MACSE storage auctions [unverified].
- The gas hub is the PSV [unverified].
- **Contrast with GB:** GB has a single national price, half-hourly settlement and the NBP gas hub.

## 3. Grid

**Operators.**
- Terna is the TSO.
- The page listing ARERA-approved 2G rollout plans names about 10 large DSOs: e-distribuzione, areti, Unareti, Ireti, Edyna, Deval, Inrete, V-reti, SET and AcegasApsAmga ([ARERA smart metering](https://www.arera.it/area-operatori/smartmetering)).
- e-distribuzione serves about 85% of delivery points [unverified].
- In total there are about 120 electricity DSOs and about 190 gas DSOs [unverified].
- GB has 14 licence areas run by 6 DNO groups.

**Household connection.** The defining feature is contracted capacity (*potenza impegnata*) ([ARERA](https://www.arera.it/en/consumatori/potenza-del-contatore)):
- The typical contract is 3 kW.
- Steps are 0.5 kW up to 6 kW, then 1 kW up to 10 kW.
- The meter allows 10% headroom and briefly cuts supply above about 3.3 kW.
- Each kW costs about €26 a year including VAT.
- Raising from 3 to 4 kW costs about €100.68.
- Most households are single-phase ([e-distribuzione guide](https://www.e-distribuzione.it/content/dam/e-distribuzione/documenti/open-meter/nuove-guide-open-meter/Una_Guida_su_cui_contare_Vademecum.pdf)). Three-phase is typical above about 6–10 kW [unverified].
- **Contrast with GB:** a GB home has a 60–100 A fuse, about 14–23 kW, and no capacity charge [unverified].

**Network tariff for households.**
- Since the 2017 reform the tariff is non-progressive, with three parts: a fixed charge per delivery point, a charge per kW, and a charge per kWh [unverified].
- The network tariff has no time-of-use element; time bands (F1/F2/F3) are a retail construct [unverified].
- In 2025 network costs were 5.87 c€/kWh of a 35.12 c€/kWh total price ([ARERA](https://www.arera.it/fileadmin/allegati/com_stampa/26/Comunicato_stampa_ARERA__I_numeri_della_Relazione_Annuale_2025.pdf)).

## 4. Population and households

| | Italy | GB |
|---|---|---|
| Households | 24,130,319 resident households (2024 survey universe) ([ISTAT](https://www.istat.it/wp-content/uploads/2025/10/Report_Dotazioni-energetiche-delle-famiglie_Anno-2024.pdf)) | about 28m [unverified] |
| Average size | 2.2 (2024) ([ISTAT](https://www.istat.it/news-dati-alla-mano/litalia-e-un-paese-per-single/)) | about 2.36 [unverified] |
| One-person households | more than a third (same source) | — |

- Italy has more domestic electricity delivery points than households: just over 30.5 million ([ARERA](https://www.arera.it/fileadmin/allegati/com_stampa/26/Comunicato_stampa_ARERA__I_numeri_della_Relazione_Annuale_2025.pdf)). This is consistent with second homes [derived]. **A household is not the same as a meter point in Italy**; second homes are a large population with distinct load and tariff treatment.

## 5. Housing

**Heating systems, 2024** ([ISTAT 2024](https://www.istat.it/wp-content/uploads/2025/10/Report_Dotazioni-energetiche-delle-famiglie_Anno-2024.pdf)):
- Autonomous (individual boiler or system): 79.0%.
- Centralised (building-level): 15.4%.
- Single appliances used: 44.8%.
- More than one heating system: 43.2%.
- Firewood: 16.0%; pellets: 7.8%.

**Heating fuel, 2021** ([ISTAT 2021](https://www.istat.it/it/files/2022/06/REPORT-CONSUMI-ENERGETICI-FAMIGLIE-2021-DEF.pdf)):
- Methane was the main fuel for 68% of heating systems and 81.9% of centralised or autonomous systems.
- Biomass: 15%. Electricity: 8.5%.
- Sardinia has no methane network, and 61.9% of its homes rely on single appliances.

**Centralised heating.** 15.4% of homes have building-level (*condominio*) heating. In those homes the gas customer is the building, not the household; in 2025, 99.4% of condominium gas volume was on the free market ([ARERA](https://www.arera.it/fileadmin/allegati/com_stampa/26/Comunicato_stampa_ARERA__I_numeri_della_Relazione_Annuale_2025.pdf)).

**District heating.** Average price was €113/MWh in 2024, and gas fuels 70.5% of it (same source).

**Typical consumption.**
- ARERA's "typical customer" uses 2,700 kWh a year at 3 kW and 1,100 Smc of gas ([luce-gas.it](https://luce-gas.it/guida/glossario/cliente-domestico-tipo)).
- 1,100 Smc is about 11,600 kWh [derived, at about 10.57 kWh/Smc]. That is close to the GB Ofgem gas TDCV of 11,500 kWh [unverified], and the electricity figure matches GB's 2,700 kWh.
- ARERA's vulnerable reference customer uses 2,000 kWh at 3 kW ([ARERA](https://www.arera.it/fileadmin/allegati/com_stampa/26/Comunicato_stampa_ARERA__I_numeri_della_Relazione_Annuale_2025.pdf)).

**Tenure and building type.** Owner-occupation is about 70–75% and most people live in flats [unverified: the Eurostat check was blocked by the search limit]. A large share of the stock is pre-1976 [unverified].

## 6. Core regulation

**End of regulated default prices.**
- Gas tutela ended for non-vulnerable households in January 2024.
- Electricity *maggior tutela* ended for non-vulnerable households on 1 July 2024.
- Those customers who had not chosen a supplier moved to the Servizio a Tutele Graduali (STG). STG was auctioned in 26 territorial areas and runs from 1 July 2024 to 31 March 2027 ([ARERA 95/2025](https://arera.it/fileadmin/allegati/docs/25/95-2025-E-eel.pdf)).
- About 4.5 million non-vulnerable households were in scope. The auctions saved about €130 a year against tutela, more than 20% of the typical bill ([QualEnergia](https://www.qualenergia.it/articoli/aste-stg-arera-conferma-sconto-130-euro-anno-rispetto-tutela/)).

**Who remains protected.**
- Vulnerable customers stay on maggior tutela, or could opt into STG until 30 June 2025. Vulnerability categories include low income or bonus holders, serious health conditions, disability, residents of non-interconnected islands, people in emergency housing, and the over-75s ([ARERA 95/2025](https://arera.it/fileadmin/allegati/docs/25/95-2025-E-eel.pdf)).
- In gas, vulnerable customers are on the "tutela della vulnerabilità" service: 13.6% of household points in 2025 ([ARERA](https://www.arera.it/fileadmin/allegati/com_stampa/26/Comunicato_stampa_ARERA__I_numeri_della_Relazione_Annuale_2025.pdf)).

**Domestic electricity points, 2025** (same source):

| Service | Points | Share of points | Share of consumption |
|---|---|---|---|
| Free market | about 24.3m | 79.7% | 83% |
| Maggior tutela (vulnerable) | 3.2m | 10.4% | 8.2% |
| STG | 3.0m | 9.9% | 9.9% |

- On 1 January 2026, for a vulnerable 2,000 kWh/3 kW household, tutela cost 25.2 c€/kWh and STG 22.8 c€/kWh, both before tax (same source).
- **Free-market offers cost more than tutela in every consumption class** (same source). This is the reverse of the GB assumption that a competitive fix beats the default.

**Suppliers and concentration** (same source):
- 769 electricity sellers in 2025 (710 on the free market) and 493 gas sellers.
- Electricity retail: Enel 22.3% (down from 33.5% in 2023), A2A 10%, Edison 7.5%; top three 38.6%.
- Gas retail: Edison 16.8%, Eni 12.7%, Enel 9.7%.
- GB has about 25–30 suppliers [unverified].
- Supplier licensing and capital-adequacy rules ("Elenco Venditori", operative since 2024) were not researched this session [unverified].

## 7. Smart meters

**Electricity.**
- DSOs install and run the meters. Each DSO files a 2G rollout plan (PMS2) that ARERA approves, with penalties for slippage ([ARERA](https://www.arera.it/area-operatori/smartmetering)).
- At 31 December 2023 the 10 large DSOs had installed about 34.8 million 2G meters, with about 32.7 million in service (same source).
- Italy is on its second generation. The first generation was rolled out in the 2000s [unverified]; 2G started in 2017.
- Open Meter records **15-minute load curves for all customers**, and sellers can receive them daily ([e-distribuzione](https://www.e-distribuzione.it/content/dam/e-distribuzione/documenti/open-meter/nuove-guide-open-meter/Una_Guida_su_cui_contare_Vademecum.pdf)). Readings are routed to sellers through the SII hub run by Acquirente Unico [unverified].
- "Chain 2" is an in-home channel over the house wiring. It gives instantaneous power every second and energy every 15 minutes to a device the customer buys for €80–200 ([bolletta-energia](https://bolletta-energia.it/utenze/guida/contatori/chain-2)).
- The meter can limit power remotely, to 15% of available power ([luce-gas](https://luce-gas.it/guida/bolletta/morosita)).

**Gas.**
- Gas smart meters for domestic classes G4–G6 are being rolled out by DSOs, using either point-to-point links or 169 MHz radio ([ARERA](https://www.arera.it/area-operatori/smartmetering)).

**Contrast with GB.** GB meters are supplier-led SMETS1/2 through the DCC, with half-hourly data and partial coverage. Italy's meters are DSO-owned, near-universal, read at 15 minutes and can limit power.

## 8. Billing

**Frequency and timing** ([ARERA 463/16 summary](https://www.arera.it/allegati/schede/463-16st.pdf)):
- Domestic electricity is billed every two months.
- Gas is billed every four months below 500 Smc a year, every two months between 500 and 5,000 Smc, and monthly above that.
- Bills must be issued within 45 days of the last day billed, with automatic indemnities of €6 to €60 if late.
- Readings are used in this order: actual distributor reading, then validated customer self-reading, then estimate.

**Basis.** Bills are mostly based on readings, not estimated monthly advances; smart meters make actual reads routine.

**Two-year limitation.** Consumption more than two years old cannot be billed (*prescrizione biennale*, Law 205/2017) [unverified].

**Payment methods.** Customers pay by SEPA direct debit (*domiciliazione*), postal payment slip or card. **There is no prepayment meter product**; power limitation does that job [unverified for the payment mix].

**Taxes and charges.**
- 2024 domestic electricity: €35.70/kWh gross against 25.92 c€/kWh net [corrected: 35.70 c€/kWh gross], so taxes, charges and fees were about 9.8 c€/kWh, about 27% of the price [derived] ([ARERA 2025 release on 2024](https://www.arera.it/fileadmin/allegati/com_stampa/25/comunicato_stampa_I_NUMERI_DEI_SERVIZI_ENERGIA_E_AMBIENTE.pdf)).
- 2025 domestic gas: taxes and charges were 3.75 of 13.71 c€/kWh, about 27% [derived] ([ARERA](https://www.arera.it/fileadmin/allegati/com_stampa/26/Comunicato_stampa_ARERA__I_numeri_della_Relazione_Annuale_2025.pdf)).
- Domestic VAT is 10%. For gas, the 10% rate covers only the first 480 Smc a year and 22% applies above that [unverified].
- GB charges 5% VAT [unverified].

## 9. Settlement

**Interval.**
- The balancing timeframe moved to 15 minutes in 2025 under TIDE, the new dispatching code. The provisional version has applied since early 2025, and the consolidation phase runs from 1 February 2026 to 2028 ([Argus](https://www.argusmedia.com/ja/news-and-insights/latest-market-news/2772776-italy-to-update-power-dispatching-rules)).
- TIDE creates Balance Responsible Parties (BRPs) and Balancing Service Providers (BSPs).

**Profiling.**
- Historically, households without hourly metering were settled using **load profiling by time band** (*load profiling per fasce*) [unverified].
- 2G meters allow hourly or 15-minute treatment, but whether every low-voltage household is already settled on actual intervals is not confirmed [unverified].

**Reconciliation.** Monthly settlement is followed by annual and multi-year adjustment sessions run by Terna and the SII [unverified].

**Contrast with GB.** GB is mid-way through moving everyone to half-hourly settlement (MHHS), with reconciliation runs out to about 14 months [unverified].

## 10. Debt and vulnerability

**Disconnection procedure for electricity** (TIMOE) ([luce-gas TIMOE](https://luce-gas.it/guida/mercato/timoe); [luce-gas morosità](https://luce-gas.it/guida/bolletta/morosita)):
1. The supplier sends a formal notice (*costituzione in mora*) by registered letter or certified email (PEC). The deadline must be more than 20 days from issue and more than 15 days from sending.
2. The supplier may ask the DSO to act only 3 working days after that deadline.
3. The meter is limited to 15% of available power for 15 days.
4. Supply is then suspended.

**Restrictions on suspension** (same sources):
- No suspension on Fridays, Saturdays, public holidays or the days before them.
- No suspension while a written complaint about billing or a faulty meter is pending, or if the debt is time-barred.
- Customers on life-support equipment, hospitals, care homes, schools and prisons can never be disconnected.
- Reconnection must happen within one working day of request, with indemnities of €35, €70 or €105 for delays.
- Instalment plans can be requested up to 10 days after the due date.
- **No winter disconnection ban was found** [unverified].
- Gas follows a parallel code (TIMG).

**Social tariffs** ([ARERA](https://www.arera.it/fileadmin/allegati/com_stampa/26/Comunicato_stampa_ARERA__I_numeri_della_Relazione_Annuale_2025.pdf)):
- The *bonus sociale* has been automatic since 2021, triggered by the household's means-test declaration (ISEE), with no application needed.
- Eligibility is ISEE up to €9,530, or €20,000 for households with four or more children.
- In 2025 it reached 4.3 million households: 2.7 million for electricity and 1.6 million for gas. Electricity bonuses cost about €840m and gas about €165m.
- About 4.2 million households with ISEE between €9,530 and €25,000 received a one-off €200 contribution.
- 86,010 physical-hardship bonuses were active (for households using medical equipment).

**Arrears prevalence** has no national figure in the sources found. "Arrears and suspension" made up 11% of information requests to ARERA's consumer desk (same source).

## 11. EV, PV, batteries, heat pumps

**Solar PV** ([QualEnergia/Italia Solare](https://www.qualenergia.it/articoli/fotovoltaico-italiano-installato-fine-2025/)):
- 43.5 GW installed across 2,092,088 plants at end 2025.
- Plants of 6 kWp or less are 62% of all plants, about 1.3 million [derived].
- 5.6 GW and 211,013 connections were added in 2025, down 25.9%, with the fall concentrated in small residential systems.

**Net metering ended.**
- *Scambio sul posto* (SSP, net metering) closed to new plants: applications were accepted until 26 September 2025, only for plants in operation by 29 May 2025.
- Existing 15-year contracts run until they expire.
- New plants use *ritiro dedicato* (GSE purchase at a guaranteed minimum of 4.64 c€/kWh in 2025, or the hourly zonal price) or join a renewable energy community ([QualEnergia](https://www.qualenergia.it/articoli/fine-scambio-posto-cosa-cambia-impianto-fotovoltaico/)).

**Renewable energy communities (CER)** ([QualEnergia](https://www.qualenergia.it/articoli/comunita-energetiche-rinnovabili-tratti-salienti-incentivi-criticita/)):
- They pay an incentive on *virtually* shared energy within the area of one primary substation.
- The incentive is up to €60–120/MWh for 20 years, with an extra €10/MWh in the North and €4/MWh in the Centre.
- Each plant can be up to 1 MW.
- In towns under 5,000 people, the national recovery fund (PNRR) gives a grant of up to 40% of investment cost.

**Superbonus 110%** ([ItaliaOggi/ENEA](https://www.italiaoggi.it/diritto-e-fisco/superbonus-110-la-spesa-pubblica-supera-i-127-miliardi-di-euro-lavori-completati-al-96-bdbvua0b)):
- €121.99bn admitted for tax deduction across 500,651 buildings, as of 31 August 2025.
- That includes 138,118 condominiums (€83.6bn) and 245,143 single-family houses.
- It drove PV, heat-pump and insulation installs in 2021–23.

**Heat pumps and EVs.**
- 40.4% of households have hot/cold heat pumps, mostly air-to-air split units that also cool ([ISTAT 2024](https://www.istat.it/wp-content/uploads/2025/10/Report_Dotazioni-energetiche-delle-famiglie_Anno-2024.pdf)). GB's heat pumps are mostly air-to-water and few.
- In 2025, battery EVs were 6.2% of new cars and plug-in hybrids 6.5%, of 1.53m registrations ([Italpress/UNRAE](https://www.italpress.com/?p=624397)). GB's BEV share is about 20% [unverified].
- The 3 kW contracted-capacity limit is a binding constraint on EV charging at home [derived from §3].
- Home battery stock was not found [gap].

## 12. Cooling

- 56.0% of households have at least one cooling system, up from 29.4% in 2013. Ownership is 71.2% in the Islands and 63.2% in large cities ([ISTAT 2024](https://www.istat.it/wp-content/uploads/2025/10/Report_Dotazioni-energetiche-delle-famiglie_Anno-2024.pdf); [dellevittorie](https://m.dellevittorie.it/istat-dotazione-energetiche-famiglie-2024/)).
- The July 2026 peak of about 58 GW and record demand were credited to air conditioning ([greenme/Terna](https://www.greenme.it/energia/record-di-consumi-elettrici-a-luglio-2026-in-italia-e-la-dipendenza-energetica-supera-il-75/)).
- No source quantified cooling's share of household electricity [gap].
- GB has near-zero domestic cooling.

## 13. Cooking

- No figures were found [gap].
- Gas hobs dominate wherever there is a methane network. LPG cylinders are common in Sardinia and rural areas. Induction is rising but is limited by the 3 kW contract [all unverified].

## 14. Switching

**Rates** ([ARERA](https://www.arera.it/fileadmin/allegati/com_stampa/26/Comunicato_stampa_ARERA__I_numeri_della_Relazione_Annuale_2025.pdf); [comparasemplice](https://www.comparasemplice.it/informazioni/energia/cambio-fornitore-luce-cosa-dicono-i-dati-arera-sul-2025)):
- Domestic electricity: 20.8% of customers in 2025 (23.8% in 2024).
- Domestic gas: 18.8%.
- These are far above GB's post-2021 rates [unverified].

**Process.**
- Switches run through the SII hub. From 1 January 2026, the technical SII step takes 24 hours ("switching lampo"). The whole process must take no more than three weeks under Directive 2019/944 ([Sky TG24](https://tg24.sky.it/economia/2025/08/13/bollette-luce-gas-cambio-fornitore-novita)).
- **Blocks:** debt does not block a switch. However, an incoming supplier may revoke a switch request on seeing prior arrears (TIMOE para 6.3), and in gas a switch can be withdrawn if the point is suspended for arrears ([luce-gas TIMOE](https://luce-gas.it/guida/mercato/timoe)).
- **Cooling-off:** 14 days under the Consumer Code [unverified].

## 15. Home moves

- Italy has three distinct transactions [all unverified]:
  - **voltura**: change of account holder on a live point;
  - **subentro**: reactivating a deactivated point;
  - **prima attivazione / allaccio**: new connection.
- The outgoing occupant usually terminates the contract and the point is deactivated. The new occupant must actively contract with a supplier of their choice, through that supplier; the SII records the change [unverified].
- **There is no GB-style "deemed contract" in electricity.**
- In gas, when a customer is left without a contract through no fault of their own, the supplier of last resort (Fornitore di Ultima Istanza, FUI) or the DSO-run default service takes over ([luce-gas TIMOE](https://luce-gas.it/guida/mercato/timoe)).

## 16. Where debt sits

**Supplier.** The supplier holds the debt and starts the notice-and-suspension process. The DSO carries out power limitation and suspension at the supplier's request ([luce-gas](https://luce-gas.it/guida/bolletta/morosita)).

**CMOR: arrears follow the customer.**
- When a customer switches leaving arrears, the old supplier can have a "Corrispettivo CMOR" added to the new supplier's bill, under the TISIND rules.
- It can be claimed only 6 to 12 months after the switch, after prior notice, and for at least €10 ([luce-gas TIMOE](https://luce-gas.it/guida/mercato/timoe)).
- The scheme is the *Sistema Indennitario*, run by Acquirente Unico [unverified].
- **This has no GB equivalent.** GB's debt-objection rule applies only to prepayment debt assignment.

**Who funds bad debt.**
- Mainly suppliers.
- System charges left unpaid by customers can be recovered by sellers through an ARERA mechanism [unverified].
- Unpaid bills in last-resort and default services are socialised through regulated components [unverified].

**Last resort.**
- Electricity: the *servizio di salvaguardia* serves non-domestic customers without a supplier; households fall to maggior tutela (vulnerable) or STG [unverified for salvaguardia details].
- Gas: FUI and the default service ([luce-gas TIMOE](https://luce-gas.it/guida/mercato/timoe)).
- This differs from GB's Supplier of Last Resort (SoLR) process for failed suppliers. No Italian supplier-failure data was found [gap].

---

## (a) Contrast table: Italy vs GB

| # | Dimension | Italy | GB | Difference that matters |
|---|---|---|---|---|
| 1 | Weather | Zones A–F (under 600 to over 3,000 degree days); legal heating calendar; summer AC peak | Uniform moderate heating need, no legal calendar, winter peak | Two-season demand plus regulatory heating windows |
| 2 | Energy system | 48% renewables (2025), no nuclear, 94% gas import dependence, zonal prices since 2025 | Single price, nuclear plus wind, NBP hub | Zonal price replay; price set by gas and solar |
| 3 | Grid | Contracted kW (3 kW typical), 10% headroom, meter trips; e-distribuzione dominant | 60–100 A fuse, no capacity charge | Capacity is a household constraint and a tariff line |
| 4 | Households | 24.1m, 2.2 people; 30.5m domestic electricity points | about 28m, about 2.36 | Second homes: points outnumber households |
| 5 | Housing | 79% autonomous / 15% centralised heating; methane 68%; biomass 16–22% | Gas combi boilers, houses dominate | Condominium heating; wood; flats |
| 6 | Regulation | 769 sellers; tutela ended; STG auctions to Mar 2027; tutela for vulnerable; free market dearer than tutela | Price cap for all; about 25–30 suppliers | Auctioned default service, not a cap formula |
| 7 | Smart meters | DSO-owned 2G, about 33m, 15-minute curves, remote power limit | Supplier-led SMETS/DCC, half-hourly, partial | Universal 15-minute data plus remote limitation |
| 8 | Billing | Every 2 months on readings; 45-day issue rule; 2-year limit; no prepayment | Monthly direct debit on estimates; prepayment | Reading-based bimonthly cycle; no prepayment |
| 9 | Settlement | 15-minute balancing under TIDE; BRPs; legacy profiling by time band | Half-hourly, MHHS in progress | 15-minute clock; zonal |
| 10 | Debt | Formal notice → 15% power → suspension; automatic ISEE bonus | Prepayment, winter protections, WHD | Power limitation replaces prepayment |
| 11 | Assets | 43.5 GW PV, 2.09m plants; net metering closed; energy communities; Superbonus; BEV 6.2% | Smart Export Guarantee (SEG), BEV about 20% | Energy-community virtual sharing; 3 kW limits EVs |
| 12 | Cooling | 56% have AC; about 58 GW July peak | Negligible | Summer load model needed |
| 13 | Cooking | Gas or LPG, rising induction [unverified] | Mixed gas and electric | Induction collides with 3 kW |
| 14 | Switching | About 21% a year; 24-hour SII step; switch revocable for arrears | Low; 5-working-day switch | Very high churn |
| 15 | Home moves | Voltura / subentro; no deemed contract | Deemed contract on move-in | Points are deactivated, then actively reactivated |
| 16 | Debt location | Supplier holds it; DSO limits; CMOR follows customer | Supplier holds it; no CMOR | Arrears can be billed through the new supplier |

## (b) Transferability of the GB build

**World components**

| Component | Rating | Why |
|---|---|---|
| Weather-driven demand | Medium | Same engine, but needs climate zones, a cooling term and legal heating windows |
| Building thermal model | Medium | Physics transfers; stock (flats, centralised heating, wood stoves, split heat pumps) needs re-parameterising |
| Household behaviour/finances | Medium | ISEE means test and second homes are new; the core model transfers |
| Wholesale price replay | Low | Zonal 15-minute market, PUN Index perequation, PSV |
| Settlement clock and reconciliation | Low | 15 minutes, not 30; TIDE BRP roles; profiling rules differ |
| Smart-meter data feed | Medium | Richer (15-minute, universal) but delivered by DSOs through the SII |
| Network/connection limits | Low | Contracted kW with meter trip has no GB analogue |

**Supplier components**

| Component | Rating | Why |
|---|---|---|
| Tariffs and price-regulation compliance | Low | No cap; F1/F2/F3 band structure; separate vulnerable tutela and STG regimes |
| Quoting/acquisition and switching | Medium | SII flows differ; about 21% churn; arrears-based switch revocation |
| Billing and payments | Low | Bimonthly reading-based billing, 45-day rule, 10%/22% VAT split, 2-year limit |
| Direct debit/collections and debt | Low | TIMOE/TIMG timeline, 15% power limit, CMOR |
| Vulnerability duties | Medium | Automatic bonus sociale, non-disconnectable list; GB-style principles carry over |
| Hedging and wholesale buying | Medium | Same discipline; zonal basis risk and gas dependence |
| Settlement and imbalance | Low | 15-minute imbalance under TIDE, BRP/BSP split |
| Capital/financial rules | Low | Elenco Venditori regime not researched |
| Advice and asset offers | Medium | Products transfer; incentives (energy communities, ritiro dedicato, Superbonus) and the kW limit change the economics |

## (c) New features needed

**New simulation ("world") features**
1. Climate-zone map (A–F) with legally permitted heating hours and dates.
2. A cooling-demand model with AC ownership by region and a summer peak.
3. Contracted kW per point, with 10% headroom, meter-trip events and changes to contracted power.
4. A 15-minute settlement clock.
5. Zonal day-ahead prices plus PUN Index perequation; PSV gas prices.
6. Second-home points (non-resident tariff, sparse load).
7. Condominium (building-level) heating customers.
8. Biomass, wood-stove and LPG heating; areas with no methane (Sardinia).
9. ISEE income distribution that triggers automatic bonuses.
10. Energy-community perimeters by primary substation, with virtual shared-energy accounting.
11. DSO-run meter data flowing through the SII hub, including remote power limitation.
12. Home-move transactions: deactivation, voltura and subentro.

**New supplier features**
1. Time-band (F1/F2/F3) and 15-minute tariff products; a contracted-kW fixed charge.
2. A compliance path for vulnerable tutela and STG, including the auction logic.
3. Bimonthly reading-based billing with the 45-day rule and late-bill indemnities.
4. TIMOE/TIMG debt workflow: formal notice, 15% power limit, suspension, reconnection SLAs and indemnities.
5. Issuing and receiving CMOR, and using switch revocation.
6. Applying the bonus sociale on bills from SII/ISEE data.
7. A switching engine sized for high churn and the 24-hour SII step.
8. Zonal hedging and imbalance management under TIDE as a BRP.
9. Offers for energy communities and ritiro dedicato; advice on raising contracted kW for EVs and heat pumps.
10. Handling FUI and default-service transitions.

## (d) Named gaps

- **Search limit:** the web-search budget ran out partway through. Every [unverified] item above remains to be confirmed.
- Italy national HDD/CDD series (Eurostat).
- Tenure, flats-vs-houses and building-age shares.
- Number of electricity and gas DSOs, and e-distribuzione's share.
- Network tariff structure (TD, ASOS/ARIM components) and whether it has any time-of-use element.
- Exact F1/F2/F3 band hours.
- Whether household settlement uses actual 15-minute or hourly data or profiles, and the reconciliation calendar.
- Payment-method mix and the deposit regime.
- Disconnection and limitation volumes, arrears prevalence, and any winter protection.
- Mechanisms for socialising bad debt and recovering unpaid system charges.
- Details of the Sistema Indennitario and CMOR amounts.
- Electricity salvaguardia, and the history of supplier failures and last-resort handling.
- Supplier licensing (Elenco Venditori) capital requirements.
- Cooking fuel mix.
- Cooling share of household consumption.
- Home battery stock; heat-pump split (air-to-air vs air-to-water).
- Number of energy communities in operation.
- Home-move process rules (voltura/subentro) from ARERA primary sources.

---

## Verification of [unverified] items (drafting pass, 25 Oct 2026)

Per the director's steer of 25 Oct 07:52 GMT: each [unverified] item is confirmed, corrected or left open. Other-markets packs are the lowest priority, so only the headline items were fetched; the rest stay open and the page does not use them as claims.

- [unverified]** means it comes from memory and was not confirmed this session.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB comparison figures are from memory and are marked [unverified] unless a link is given.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Research limit:** the shared web-search budget ran out partway through. Several items stayed [unverified] because of that. They are listed under (d) Named gaps.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Comparators.** The Eurostat EU average is 3,199 HDD over 1979–2022 ([Eurostat SE](https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/92378.pdf)). Ireland, the nearest proxy for GB, averages 2,833 HDD and has CDD close to 0.03 (same source). Italy's...
  - **corrected: Eurostat HDD 1,678-2,025 and CDD 224-365 over 2020-2025 (2024: HDD 1,678, CDD 365); Eurostat nrg_chdd_a via the dissemination API (unit NR), dataset updated 2026-05-08, accessed 2026-10-25**
- Nuclear.** Italy has none [unverified: plants closed after the 1987 referendum]. Gas sets the marginal price far more often than in GB.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- The bidding zones are Nord, Centro-Nord, Centro-Sud, Sud, Calabria, Sicilia and Sardegna [unverified].
  - **still open: the GME results page names a zonal-prices tab but lists no zones (fetched 2026-10-25)**
- Italy also has a capacity market and MACSE storage auctions [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- The gas hub is the PSV [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- e-distribuzione serves about 85% of delivery points [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- In total there are about 120 electricity DSOs and about 190 gas DSOs [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Most households are single-phase ([e-distribuzione guide](https://www.e-distribuzione.it/content/dam/e-distribuzione/documenti/open-meter/nuove-guide-open-meter/Una_Guida_su_cui_contare_Vademecum.pdf)). Three-phase is typical above about 6–10 kW [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Contrast with GB:** a GB home has a 60–100 A fuse, about 14–23 kW, and no capacity charge [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Since the 2017 reform the tariff is non-progressive, with three parts: a fixed charge per delivery point, a charge per kW, and a charge per kWh [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- The network tariff has no time-of-use element; time bands (F1/F2/F3) are a retail construct [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Households | 24,130,319 resident households (2024 survey universe) ([ISTAT](https://www.istat.it/wp-content/uploads/2025/10/Report_Dotazioni-energetiche-delle-famiglie_Anno-2024.pdf)) | about 28m [unverified]
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Average size | 2.2 (2024) ([ISTAT](https://www.istat.it/news-dati-alla-mano/litalia-e-un-paese-per-single/)) | about 2.36 [unverified]
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- 1,100 Smc is about 11,600 kWh [derived, at about 10.57 kWh/Smc]. That is close to the GB Ofgem gas TDCV of 11,500 kWh [unverified], and the electricity figure matches GB's 2,700 kWh.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Tenure and building type.** Owner-occupation is about 70–75% and most people live in flats [unverified: the Eurostat check was blocked by the search limit]. A large share of the stock is pre-1976 [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB has about 25–30 suppliers [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Supplier licensing and capital-adequacy rules ("Elenco Venditori", operative since 2024) were not researched this session [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Italy is on its second generation. The first generation was rolled out in the 2000s [unverified]; 2G started in 2017.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Open Meter records **15-minute load curves for all customers**, and sellers can receive them daily ([e-distribuzione](https://www.e-distribuzione.it/content/dam/e-distribuzione/documenti/open-meter/nuove-guide-open-meter/Una_Guida_su_cui_contare_Vademecum.pdf)...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Two-year limitation.** Consumption more than two years old cannot be billed (*prescrizione biennale*, Law 205/2017) [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Payment methods.** Customers pay by SEPA direct debit (*domiciliazione*), postal payment slip or card. **There is no prepayment meter product**; power limitation does that job [unverified for the payment mix].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Domestic VAT is 10%. For gas, the 10% rate covers only the first 480 Smc a year and 22% applies above that [unverified].
  - **still open: the ARERA tax page and the Agenzia delle Entrate page both returned 404 on 2026-10-25**
- GB charges 5% VAT [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Historically, households without hourly metering were settled using **load profiling by time band** (*load profiling per fasce*) [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- 2G meters allow hourly or 15-minute treatment, but whether every low-voltage household is already settled on actual intervals is not confirmed [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Reconciliation.** Monthly settlement is followed by annual and multi-year adjustment sessions run by Terna and the SII [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Contrast with GB.** GB is mid-way through moving everyone to half-hourly settlement (MHHS), with reconciliation runs out to about 14 months [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- No winter disconnection ban was found** [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- In 2025, battery EVs were 6.2% of new cars and plug-in hybrids 6.5%, of 1.53m registrations ([Italpress/UNRAE](https://www.italpress.com/?p=624397)). GB's BEV share is about 20% [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Gas hobs dominate wherever there is a methane network. LPG cylinders are common in Sardinia and rural areas. Induction is rising but is limited by the 3 kW contract [all unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- These are far above GB's post-2021 rates [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Cooling-off:** 14 days under the Consumer Code [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Italy has three distinct transactions [all unverified]:
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- The outgoing occupant usually terminates the contract and the point is deactivated. The new occupant must actively contract with a supplier of their choice, through that supplier; the SII records the change [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- The scheme is the *Sistema Indennitario*, run by Acquirente Unico [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- System charges left unpaid by customers can be recovered by sellers through an ARERA mechanism [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Unpaid bills in last-resort and default services are socialised through regulated components [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Electricity: the *servizio di salvaguardia* serves non-domestic customers without a supplier; households fall to maggior tutela (vulnerable) or STG [unverified for salvaguardia details].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- 13 | Cooking | Gas or LPG, rising induction [unverified] | Mixed gas and electric | Induction collides with 3 kW
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Search limit:** the web-search budget ran out partway through. Every [unverified] item above remains to be confirmed.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**

**Counts:** confirmed 0, corrected 1, still open 42.
