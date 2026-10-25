# France against GB: a regulated tariff only the incumbent sells, a power limit in every home, and electric heating

**Knowledge:** other-market-france

**Status:** knowledge only, not on the roadmap (director, 25 Oct 2026). From the advisor's cited evidence pack `DIRECTOR_EVIDENCE_OTHER_MARKET_FRANCE_VS_GB_2026-10-25.md`, checked on 25 Oct 2026; the outcome of every [unverified] item is in the verification table at the end. Figures marked [unverified] are not claims.

**Published as:** `site/knowledge/other-market-france/`.

---
# France vs Great Britain: household energy market evidence pack for Poesys

**Purpose:** knowledge only. This pack explains how the French household energy market differs from GB's, so you can judge how much of the GB build carries over.
**Conventions:** a source URL sits next to each figure. Own arithmetic is marked [derived]. Anything taken from memory and not checked in this session is marked [unverified]. GB comparison figures are mostly [unverified]: no GB sources were fetched in this session.
**Research limit:** the shared web-search budget for this turn ran out partway through (200 calls). Everything after that point, including most of the coordinator's added dimensions 12 to 16, comes from pages already fetched or is flagged [unverified]. A follow-up session could confirm the flagged items.

---

## 1. Weather and climate

- France counts heating need in degree-days (DJU) with a 17 °C threshold. It also computes a 15 °C series. Since the 2024 update these are weighted by commune population. SDES publishes national, regional and département series from 1990 to 2025: https://www.statistiques.developpement-durable.gouv.fr/indice-de-rigueur-degres-jours-unifies-aux-niveaux-national-regional-et-departemental. The national values sit in spreadsheets that could not be opened from here.
- Mainland France usually sees 2,000 to 3,000 DJU a year. Building regulations divide the country into three climate zones, H1 (coldest), H2 and H3 (warmest): https://opera-energie.com/dju/. The range runs from Alsace and Lorraine (continental, cold) to the Mediterranean (mild winters, hot summers). It is wider than GB's range [unverified].
- **Seasonality is the defining feature.** Winter demand rises by about **2,400 MW for each 1 °C drop** in temperature. Summer demand rises by about **400 MW per °C**, measured at the early-afternoon peak and driven by air conditioning: https://www.connaissancedesenergies.org/le-reseau-electrique-ne-craint-pas-la-chaleur-estivale-241104.
- Q1 2025 was about 1.2 °C colder than normal, which added nearly 6 TWh of consumption in the quarter (RTE Bilan électrique 2025: https://assets.rte-france.com/analyse-et-donnees/2026-03/BE2025%20-%20Rapport%20Complet.pdf). The 2025 peak was 88 GW, the highest since 2021: https://assets.rte-france.com/prod/public/2026-02/Bilan-electrique-2025-principaux-resultats.pdf.
- EU cooling degree days reached 140 in 2022, against a 1979–2022 average of 75. Provence-Alpes-Côte d'Azur averaged 91.6 CDD over that period: https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/92378.pdf.
- **GB comparison:** GB's electricity sensitivity to temperature is much smaller, because GB heats mainly with gas. Its peak is about 45 to 50 GW [unverified]. GB cooling load is negligible.

## 2. Energy system

**Electricity generation, 2025** (RTE: https://assets.rte-france.com/prod/public/2026-02/Bilan-electrique-2025-principaux-resultats.pdf; full report: https://assets.rte-france.com/analyse-et-donnees/2026-03/BE2025%20-%20Rapport%20Complet.pdf)

| Item | 2025 figure |
|---|---|
| Total generation | 547.5 TWh |
| Nuclear | 373.0 TWh, about **68%** [derived] |
| Hydro | 62.4 TWh |
| Wind | 49.6 TWh, of which 43.9 onshore |
| Solar | 32.9 TWh |
| Gas | 16.4 TWh, from 12.4 GW of plant |
| Low-carbon share | 95.2% |
| Renewable share | 27% |
| Net exports | 92.3 TWh (record) |
| Consumption, weather-corrected | 451.2 TWh |
| Average spot price | 61 €/MWh |
| Negative-price hours | 513 |
| Installed solar | 30.4 GW |
| Installed wind | 25.8 GW, of which 1.9 GW offshore |

- **Gas sets the price far less often than in GB.** France is usually a net exporter and is price-coupled with its neighbours.

**Wholesale market design**
- France is a single bidding zone in the EU's coupled day-ahead and intraday markets (EPEX) [unverified].
- The imbalance settlement period has been **15 minutes since January 2025**.
- Intraday cross-zonal gate closure stays at one hour before delivery until 1 January 2029 under a derogation: https://www.cre.fr/fileadmin/Documents/Deliberations/2025/250723_2025-198_Derogation_RTE.pdf.
- France has a capacity mechanism. The new design held its first auction on 6 July 2026: https://www.connaissancedesenergies.org/afp/le-regulateur-de-lenergie-cre-propose-une-hausse-de-25-des-tarifs-reglementes-de-lelectricite-au-1er-aout-260716.

**ARENH ended and the VNU replaced it**
- ARENH ended on 31 December 2025. In 2025 it covered 43.8% of a regulated-tariff customer's energy at 42 €/MWh: https://www.cre.fr/fileadmin/Documents/Deliberations/2026/260114_2026-06_TRVE_2026.pdf.
- Since 1 January 2026 the **Versement Nucléaire Universel (VNU)** applies. The state captures 50% of EDF's nuclear revenue above 78 €/MWh and 90% above 110 €/MWh. The thresholds are fixed for 2026–2028 and indexed to inflation. The money goes back to all consumers as a separate bill line, delivered through their supplier, by default spread over April to October: https://www.edf.fr/entreprises/decryptages/normes-et-reglementations/versement-nucleaire-universel-les-cles-pour-tout-comprendre.
- At current forward prices (2026 calendar baseload 63.9 €/MWh, per the CRE source above), the VNU pays nothing [derived].

**Gas**
- France trades gas at a single hub, PEG [unverified].
- Regulated gas tariffs (TRVG) ended on 30 June 2023: https://selectra.info/energie/guides/comprendre/bouclier-tarifaire. In their place the CRE publishes a non-binding reference price, the "prix repère" [unverified].

## 3. Grid and household connection

**Network operators**
- RTE is the transmission operator.
- **Enedis** distributes electricity to about 95% of mainland customers. The rest are served by local distributors (ELDs): about 130 for electricity, over 160 counting gas (corrected 25 Oct, second read).
- The CRE observatory names six main ELDs. Alternative suppliers hold only about 0.74% of residential sites in ELD areas: https://www.cre.fr/fileadmin/Documents/Rapports_et_etudes/2026/Observatoire_T4_2025.pdf.
- GRDF distributes most gas, alongside about 20 gas ELDs [unverified].

**Household connection**
- Most homes are single-phase. Three-phase is available [unverified].
- **The key difference from GB is the subscribed power (puissance souscrite), chosen in 3 kVA steps from 3 to 36 kVA.** The customer pays for it in the standing charge, and the Linky meter trips if the home draws more. About 70% of households subscribe 6 kVA; no 9 kVA share was found (corrected 25 Oct, second read).
- The subscription is a hard per-home power limit and a pricing variable in its own right.
- GB has no subscription. A typical home has a 60–100 A fuse, roughly 14–23 kVA [unverified].

**Network tariff (TURPE)**
- TURPE 7 took effect on 1 August 2025 (CRE, via https://www.photovoltaique.info/fr/actualites/detail/turpe-7/).
- It charges by subscribed power and by time of use, with peak/off-peak periods that differ by season [unverified detail].
- TURPE rose on 1 August 2026: +3.04% for distribution, +3.34% for transmission: https://www.connaissancedesenergies.org/afp/le-regulateur-de-lenergie-cre-propose-une-hausse-de-25-des-tarifs-reglementes-de-lelectricite-au-1er-aout-260716.

**Off-peak hours (heures creuses) are being moved**
- Enedis sets each home's off-peak hours, and the network tariff is lower inside them: https://www.connaissancedesenergies.org/reforme-des-heures-creuses-ce-quil-vous-faut-savoir-241104.
- From 1 November 2025, about 11 million peak/off-peak households are moving to five night hours plus three daytime hours, mainly between 11h and 17h. The rollout runs to end-2027, zone by zone. Linky meters are reprogrammed remotely: https://www.journaldeleconomie.fr/?p=41532.
- Each home therefore has its own off-peak timetable, and that timetable changes over time.

## 4. Population and households

- France had **30.9 million households** in 2022 (30.1 million in mainland France). Average size is 2.1 people. 38.5% of households are one person [derived: 17.0 + 21.5]: https://www.insee.fr/fr/statistiques/2012714.
- GB has about 28 million households with an average of about 2.4 people [unverified].
- France is less urban and less dense than England [unverified].

## 5. Housing, heating and consumption

**Tenure, 2022:** 57.1% owner-occupied, 24.8% private rental, 18.0% social rental: https://www.statistiques.developpement-durable.gouv.fr/residences-principales-en-france-quelles-sont-les-caracteristiques-des-logements-et-de-leurs.
- 80% of owner-occupiers live in houses. 69.6% of private renters live in flats.
- 28–36% of private housing was built before 1949.

**Main heating energy, mainland France, 1 January 2020** (https://www.statistiques.developpement-durable.gouv.fr/les-energies-de-chauffage-des-menages-en-france-metropolitaine)

| Heating energy | Share of main residences |
|---|---|
| **Electricity** | **37.2%**, of which heat pumps 5.1% |
| Mains gas | 35.8% |
| Wood | 10.5% |
| Heating oil | 9.6% |
| District heating | 5.3% |
| LPG | 1.5% |

- Flats lean on gas (44%) and district heating (12%). Houses lean on wood, oil and heat pumps.
- Many flats have collective heating: one boiler per building, billed through service charges. Those households are not a supplier's gas customers.
- GB, for comparison: about 85% of homes have gas central heating and about 8–10% use electric heating [unverified].

**Consumption**
- The CRE's reference household uses **4.5 MWh of electricity a year**: https://www.cre.fr/fileadmin/Documents/Communiques_de_presse/2026/260120_CP_CRE_TRVE_Fev26.pdf. Ofgem's typical domestic consumption is 2,500 kWh electricity and 9,500 kWh gas from 1 Jul 2026 (corrected 25 Oct, second read; Ofgem's undated consumer page still shows 2,900 / 12,000 and is stale).
- Electrically heated homes often use 8–15 MWh a year [unverified].
- Heat pumps used just over 10 TWh in 2023, a little under 3% of residential energy. Fossil fuels still supplied 43% of residential heating energy (RTE BE2025).
- No sourced figure for average gas use per household was found. About 10–12 MWh is plausible [unverified].

## 6. Core regulation

**Regulated tariffs (TRVE) still dominate**
- At 31 December 2025, France had 35.02 million residential electricity sites: **19.54 million (55.8%) on the regulated tariff** and 15.48 million on market offers. Alternative suppliers held 31.8% of sites: https://www.cre.fr/fileadmin/Documents/Rapports_et_etudes/2026/Observatoire_T4_2025.pdf.
- The regulated-tariff base kept falling, to 19.37 million by end-March 2026 (connaissancedesenergies Aug-2026 piece above).
- On average, 26 suppliers offered 81 residential electricity offers in Q4 2025.
- Residential switching ran at 2.78% in Q4 2025 (the quarterly rate as the CRE reports it). Alternative suppliers gained 556,000 net sites in 2025.

**Gas**
- 10.34 million residential sites, all on market offers. Alternative suppliers hold 46.9%. Switching ran at 3.6% in Q4. On average, 15 suppliers made 39 offers (same source).

**Who can have the regulated tariff, and who sells it**
- All households, plus micro-businesses (fewer than 10 staff and no more than €2m turnover) and small local authorities.
- Only EDF and the ELDs sell it.
- The CRE proposes each tariff change. The government decides, after an opinion from the Conseil supérieur de l'énergie: https://www.cre.fr/fileadmin/Documents/Deliberations/2026/260114_2026-06_TRVE_2026.pdf.

**How the regulated tariff is built (cost stack, February 2026, same source)**
- **Energy:** baseload and peak forward products bought evenly over 24 months; load-shape cost smoothed over 12 months. The 2026 calendar baseload price was 63.9 €/MWh, against 103.0 in 2025.
- **Capacity:** 4,401 €/MW.
- **Balancing costs:** 0.50 €/MWh.
- **Retail costs:** 18.11 €/MWh for residential, of which energy-saving certificates (CEE) 9.80 €/MWh.
- **Margin:** a "normal" margin of 2.5%.
- **Catch-up:** adjustments for past under- or over-recovery.
- **Network:** TURPE.
- **Taxes:** excise 30.85 €/MWh (30.62 from August 2026), the CTA network levy (15%) and VAT.

**Recent tariff moves**
- February 2025: −15%.
- February 2026: −0.83% (household bill 1,051 € → 1,042 €).
- August 2026 proposal: +2.5% (bill → 1,072 €).
- Sources: CRE press release above; connaissancedesenergies Aug-2026 piece.
- **Market offers are benchmarked against the regulated tariff**, often as "regulated tariff minus x%". The regulated tariff is effectively the price anchor for the whole market [unverified as a share of offers].

**Tariff options**
- **Base** (flat rate), **HP/HC** (peak/off-peak) and **Tempo**.
- Tempo prices vary by day colour, blue, white or red, with 22 red days a year [unverified]. In February 2026 Tempo rates rose 6.2% to bring them closer to cost (CRE deliberation).
- The Base option is being withdrawn for 18–36 kVA homes from February 2026 (CRE press release).
- HP/HC was extended down to 3 kVA from August 2026 (connaissancedesenergies Aug-2026 piece).

**2022–23 tariff shield (bouclier tarifaire)**
- Regulated-tariff rises were capped at 4% in February 2022, 15% in February 2023 and 15% in February 2024.
- The electricity excise was cut to 1 €/MWh.
- Regulated gas prices were frozen from November 2021 to June 2023.
- The CRE puts the net cost at about €20.4bn: https://selectra.info/energie/guides/comprendre/bouclier-tarifaire.
- Suppliers selling market offers were compensated through the regulated-tariff mechanism and an "amortisseur" scheme for small businesses [unverified].

**Licensing, supplier failures, concentration**
- Suppliers need a ministerial authorisation, not an Ofgem-style licence [unverified].
- Several suppliers failed or stopped selling in 2021–22: Hydroption failed; E.Leclerc Énergies and Cdiscount Énergie suspended sales [unverified]. Losses on GB's scale did not happen.
- EDF still holds about 68% of residential sites [derived: (19.54m regulated + some of the 4.35m incumbent market offers) / 35.02m; incumbent share including ELDs = 68.2%].
- The CRE uses HHI thresholds of 1,000 and 2,000. Its exact values appear only in charts.

## 7. Smart meters

**Electricity (Linky)**
- At 31 August 2024, **37.3 million Linky meters** were installed and about 2.1 million old meters remained: https://www.connaissancedesenergies.org/questions-et-reponses-energies/linky-que-faut-il-savoir-sur-le-compteur-communicant.
- Rollout cost: €4.6bn according to the Cour des comptes, about €4bn according to the CRE (same source).
- Enedis and the ELDs install and operate the meters. Local authorities own them.
- Homes that refuse a Linky pay 38.88 € excluding VAT a year, or up to 63.72 € if they also submit no readings (same source).

**Data granularity and consent**
- Daily readings are sent by default.
- The half-hourly load curve needs the customer's consent (opt-in). **Only about 30% of meters have it switched on.** In February 2026 the CRE floated switching to opt-out: https://selectra.info/energie/actualites/marche/donnees-linky-transfert-par-defaut-cre.
- The meter-reading data flows from distributor to supplier. There is no central data body like GB's DCC.

**Gas (Gazpar)**
- About 11 million meters, rollout finished in 2023 (source inconsistent on dates and counts). GRDF collects readings daily through concentrators: https://www.totalenergies.fr/particuliers/gaz/compteur-gazpar/calendrier-compteur-gazpar.

**GB comparison:** in GB the supplier is responsible for the meter, and data flows through the DCC. About 73% of meters run by large suppliers were smart at end June 2026 (corrected 25 Oct, second read).

## 8. Billing and payment

**Billing basis**
- The common model is **monthly instalments ("mensualisation") based on estimated annual use, with an annual true-up invoice**. The other option is a bill every two months based on actual readings, which Linky now supplies [unverified].
- Direct debit is the main payment method. Payment by TIP, cheque and card also exist [unverified].
- **France has no prepayment market** [unverified]. GB has about 4 million prepayment meters [unverified].
- The VNU will appear as its own bill line (EDF page above).

**Taxes and levies**
- Excise: 30.85 €/MWh in 2026.
- CTA: 15% of the fixed network component.
- VAT: 20%. The reduced 5.5% rate on the standing charge was removed in August 2025 [unverified].
- Taxes are about a quarter to a third of the bill [unverified].
- The energy-saving certificate cost (9.80 €/MWh) sits inside retail costs: CRE deliberation above.

## 9. Settlement

**Who does what**
- The **distributor (Enedis) rebuilds each site's consumption at 30-minute resolution** in a process called "reconstitution des flux". It allocates that consumption to the **balance responsible party (responsable d'équilibre, RE)** that each supplier names.
- RTE settles imbalances, now at 15 minutes (2025 derogation deliberation above). Distributors convert data between 30- and 15-minute steps where needed: https://cre.fr/fileadmin/Documents/Deliberations/2025/250213_2025-52_Remontee_des_donnees.pdf.

**Profiling** (https://www.sia-partners.com/fr/publications/publications-de-nos-experts/la-reconstitution-des-flux-denergie-quel-interet-et-quel)
- **Households are profiled, not settled on their actual half-hourly data.** France uses 29 profiles in four families; homes up to 36 kVA form one family.
- About 90% of sites (99% of profiled energy) use dynamic profiles, updated at least weekly from a panel of meters.
- Linky daily readings by tariff period feed the calculation.
- In 2020, only about 50,000 sites were settled from their own load curves.

**Reconciliation timeline**
- Settlement results are published in runs from S+2 (two weeks) to M+14 (14 months), with a target of moving to S+1 (one week).
- **GB comparison:** GB is moving to half-hourly settlement for all sites (MHHS) on actual readings, with a shorter reconciliation window [unverified detail].

## 10. Debt and vulnerability

**Winter truce (trêve hivernale)**
- From 1 November to 31 March, suppliers may not cut off a main residence.
- They may still reduce its supply power.

**Debt procedure** (decree 2008-780; https://selectra.info/energie/actualites/marche/decret-impayes-2026-coupures-services-sociaux)
- **Day 14 after the bill or due date:** the supplier sends a first letter. The customer then has 15 days to pay or agree a plan.
- **No agreement:** the supplier sends a second letter at least 20 days before reducing power or cutting off.
- **Five days into a cut-off or reduction:** social services are told, unless the customer objects.
- A draft 2026 decree would lengthen these steps.

**Scale of arrears** (https://www.connaissancedesenergies.org/afp/electricite-les-interventions-pour-factures-impayees-en-baisse-mais-toujours-elevees-en-2025-260303)
- More than **1.2 million debt interventions in 2025**, 79% more than in 2019.
- Power reductions have grown 3.5-fold since 2019. Cut-offs have fallen 49% over the same period.
- 36% of households reported difficulty paying an energy bill (2020: 18%).

**Chèque énergie** (https://www.lafinancepourtous.com/2025/04/02/cheque-energie-versement-en-novembre-2025/)
- A means-tested payment of 48 to 277 €, average about 150 €, to about 5.6 million households.
- The state sends it. The household uses it to pay a supplier. From 2025 it is tied to the home's meter point.

**Fuel poverty, 2024** (SDES: https://www.ecologie.gouv.fr/sites/default/files/publications/statistiques_sdes_essentiel_08_preecarite_%20energeetique_2024_sept%202026.pdf)
- 11.5% of households (3.5 million) before the chèque, 10.3% after it.
- Rates are highest for oil and district heating (16–18%).

**Vulnerability registers:** there is no direct equivalent of GB's Priority Services Register [unverified].

## 11. EVs, rooftop PV, batteries and heat pumps

**Rooftop PV and self-consumption** (RTE BE2025)
- About **838,000 households and small businesses self-consume** solar power: 3.7 GW, or 18% of all solar capacity.
- Self-consumed solar energy was about 2.9 TWh in 2025, up about 45% on 2024.

**Self-consumption rules**
- Surplus power is sold under a purchase obligation (EDF OA) at a regulated tariff. That tariff was cut sharply in 2025 for systems up to 9 kWc, and the investment bonus was reduced [unverified].
- France has no net metering.
- Collective self-consumption is allowed between sites close to each other [unverified].

**Heat pumps:** 5.1% of main residences in 2020, about 9% of houses (SDES heating source). Sales are high, roughly 1 million units a year including air-to-air [unverified].

**EVs:** RTE gives no fleet figure. The fleet is about 1.4 million battery EVs: 3.5% of 40.0 million cars at 1 January 2026 [derived] (corrected 25 Oct, second read).

**GB comparison:** GB pays for exported power through the Smart Export Guarantee (supplier-set export tariffs), and EV-specific time-of-use tariffs are widespread [unverified].

## 12. Cooling

- Summer demand rises about 400 MW per °C at the afternoon peak (connaissancedesenergies source above).
- About 25% of households had air conditioning in 2020, and the share is rising [unverified; ADEME study].
- Summer peaks run around 55–60 GW, well below the 88 GW winter peak [unverified].
- Cooling is a real load in southern France and minor nationally. In GB it is close to zero.

## 13. Cooking

- Electric cooking dominates, with induction hobs common. Gas hobs are declining and are concentrated in gas-connected flats. Bottled LPG is used in rural areas [unverified; no source fetched].
- For a GB gas home, cooking is a small gas load. In France, cooking mostly adds to electricity demand.

## 14. Switching

- The new supplier starts the switch. Enedis or GRDF carries it out, usually within days, and a switch can be dated as early as the next day with Linky [unverified].
- Households pay no exit fees and can switch at any time [unverified].
- Distance and doorstep sales carry a 14-day withdrawal right [unverified].
- Debt does not block a switch as such. But the new supplier may ask a deposit of up to 600 € or refuse for a legitimate reason, such as debt over 50 € in the ARPE file, and a cut-off already started can continue after the switch. GB's debt objection therefore has a partial French equivalent (corrected 25 Oct, second read).
- Rates: residential electricity 2.78% and gas 3.6% in Q4 2025 (CRE observatory, quarterly as reported).
- Inactive regulated-tariff customers are a large pool to win, especially for suppliers offering a discount on the regulated tariff.

## 15. Home moves

- **France has no "deemed contract" for a new occupant.** The incoming occupant chooses a supplier, which asks the distributor to energise the supply ("mise en service"). With Linky this is often done remotely within a day or so [unverified].
- The outgoing occupant cancels their contract ("résiliation"). The final bill uses a remote Linky reading or a reading the customer submits [unverified].
- An empty home with no contract can be cut off by the distributor after a set period. Nobody supplies it by default [unverified].
- **GB comparison:** in GB the incumbent supplier automatically supplies the new occupant on a deemed contract.

## 16. Where debt sits

- **The supplier carries the bad-debt risk.** The supplier signs a single combined contract with the customer ("contrat unique") and pays the network tariff to Enedis or GRDF whether or not the customer pays [unverified].
- The supplier asks for a power reduction or cut-off. **The distributor carries it out**, remotely through Linky. EDF caps power at 1 kVA all year, and stopped asking for residential cut-offs from 1 April 2022 (corrected 25 Oct, second read).
- Debt stays with the old supplier and does not follow the customer on a switch [unverified].
- The chèque énergie (state-funded) and local solidarity funds for housing costs (FSL) are the outside safety nets [unverified].
- When a supplier fails, a backup supplier ("fournisseur de secours") is appointed through a designated scheme created under the 2019 Énergie-Climat law. The minister designates it for 5 years after a CRE call: EDF for electricity in the Enedis area, TotalEnergies for gas in the GRDF area (confirmed 25 Oct, second read). A separate supplier of last resort ("fournisseur de dernier recours") covers gas customers who have no supplier [unverified].
- No GB-style levy spreads failure costs across all bills. The backup supplier recovers extra costs, including unpaid bills, through a capped surcharge on the transferred customers only: for households at most 10 €/site/month (confirmed 25 Oct, second read; CRE deliberation 2021-315).

---

## (a) Contrast table: France vs GB

| # | Dimension | France | GB | Difference that matters |
|---|---|---|---|---|
| 1 | Weather | 2,000–3,000 DJU; wide range across H1/H2/H3 zones | Mild maritime climate | Wider regional spread |
| 2 | Energy system | 68% nuclear, net exporter, 61 €/MWh, VNU; gas hub PEG | Gas sets the price; NBP | Prices are lower and less gas-driven; VNU bill credit |
| 3 | Grid | Enedis about 95% plus about 130 electricity ELDs (corrected 25 Oct, second read); subscribed kVA; per-home off-peak hours | 14 regional DNOs; fuse, no subscription | kVA limit and per-home off-peak schedule |
| 4 | Households | 30.9m, 2.1 people each | about 28m, 2.4 people | More single-person homes |
| 5 | Housing and heat | 37% electric heating; 57% owners; collective heating in flats | about 85% gas | **About 2.4 GW/°C winter sensitivity on electricity** |
| 6 | Regulation | 56% on the regulated tariff; EDF about 68% | Ofgem price cap applies to all default tariffs | Regulated tariff is a product only EDF sells, and the market anchors to it |
| 7 | Smart meters | 37m Linky (distributor-operated); load curve opt-in at about 30% | Supplier-led, through the DCC | Daily data by default; half-hourly data mostly missing |
| 8 | Billing | Monthly instalments + annual true-up; no prepayment | Direct debit plus about 4m prepayment meters | No prepayment; VNU bill line |
| 9 | Settlement | Distributor rebuilds 30-min consumption from profiles; 15-min imbalance; S+2 to M+14 | MHHS, half-hourly on actual readings | Households stay profiled |
| 10 | Debt | Winter truce; remote power reduction; chèque énergie | Winter moratorium; prepayment; Warm Home Discount | Power reduction instead of prepayment |
| 11 | Assets | 838k self-consuming PV homes; purchase obligation for surplus | Smart Export Guarantee | Regulated buy-back of surplus |
| 12 | Cooling | About 25% have air conditioning; 400 MW/°C in summer | Negligible | Summer load in the south |
| 13 | Cooking | Mostly electric | Gas common in gas homes | Cooking load moves to electricity |
| 14 | Switching | About 2.8% a quarter; a new supplier may ask a deposit or refuse for debt (corrected 25 Oct, second read) | Debt objection possible | Inactive regulated-tariff base to win |
| 15 | Home moves | New occupant must contract; no deemed contract | Deemed contract | Empty-home gap |
| 16 | Where debt sits | Supplier; distributor executes the reduction; backup supplier scheme | Supplier; levy socialises failure costs | Reduction is carried out by the distributor |

## (b) Transferability of the GB build

**World components**

| Component | Rating | Why |
|---|---|---|
| Weather-driven demand | Medium | The mechanics carry over. Electric heating and cooling responses need recalibrating. |
| Building thermal model | Medium | The physics carries over. Housing stock, collective heating and electric radiators need new data. |
| Household behaviour and finances | Medium | Instalment billing, the chèque énergie and tenure mix differ. |
| Wholesale price replay | Medium | The EPEX feed and capacity price carry over. VNU and the different price levels need adding. |
| Settlement clock and reconciliation | Low | Distributor-run profiling, 15-min imbalance and runs from S+2 to M+14 replace GB's process. |
| Smart-meter data feed | Medium | Daily data from the distributor; the half-hourly load curve depends on consent. |
| Network and connection limits | Low | The subscribed-kVA cap and per-home off-peak hours have no GB counterpart. |

**Supplier components**

| Component | Rating | Why |
|---|---|---|
| Tariffs and price regulation compliance | Low | Price against the regulated tariff, not a cap. Base/HP/HC/Tempo options plus a kVA grid. |
| Quoting, acquisition and switching | Medium | The flow is similar. Quotes need the kVA and option, and the target is regulated-tariff customers. |
| Billing and payments | Medium | Monthly instalments with an annual true-up; no prepayment. |
| Direct debit, collections and debt | Medium | French procedure timeline, winter truce, distributor-executed power reduction. |
| Vulnerability duties | Low | The chèque énergie and social-services notification replace PSR-style duties. |
| Hedging and wholesale buying | Medium | Same tools. Benchmark against the CRE's 24-month smoothed purchasing, plus capacity obligations. |
| Settlement and imbalance | Low | Responsable d'équilibre perimeter and profiled allocation. |
| Capital and financial rules | Medium | Authorisation regime; no GB-style capital adequacy rules seen [unverified]. |
| Advice and asset offers | Medium | Purchase-obligation surplus buy-back, kVA upsizing for EVs and heat pumps, Tempo. |

## (c) New features needed

**New simulation ("world") features**
1. A subscribed-kVA attribute for each home, with breaker trips when demand exceeds it.
2. Per-home off-peak schedules that Enedis changes over time (the 2025–27 reform).
3. Tempo day colours (blue/white/red) set by grid stress.
4. A profiled 30-min reconstitution engine run by the distributor, with dynamic profiles, plus 15-min imbalance settlement.
5. Settlement runs from S+2 to M+14.
6. Linky consent: a share of homes (about 30%) that provide a half-hourly load curve.
7. An electric-heating stock with about 2.4 GW/°C sensitivity, and an air-conditioning cooling load.
8. Collective heating in apartment buildings.
9. A cash-flow engine for the VNU and the capacity mechanism.
10. The winter truce calendar and chèque énergie events.
11. Empty-home and new-occupant states (no deemed contract).
12. The purchase-obligation surplus buy-back for rooftop PV.

**New supplier features**
1. Price offers relative to the regulated tariff, recalculated at each February and August change.
2. A Base/HP/HC/Tempo × kVA tariff matrix.
3. Monthly instalments with an annual true-up.
4. Handling of the VNU credit line.
5. Debt workflow on the French timeline: letters, distributor-executed power reduction, winter truce, social-services notification.
6. Acceptance of chèque énergie payments.
7. Management of a responsable d'équilibre perimeter.
8. Capacity obligation purchasing.
9. kVA-change advice for EVs and heat pumps.
10. PV self-consumption offers.
11. Energy-saving certificate (CEE) obligation costs.

## (d) Named gaps

1. The national DJU series and the regional range: values sit in SDES spreadsheets that could not be opened.
2. GB comparison figures were not sourced in this session.
3. The full TURPE 7 household tariff grid.
4. Customer counts by subscribed kVA and by tariff option, including the number of Tempo customers.
5. Average gas use per household.
6. EV fleet, heat pump stock and home battery numbers.
7. Self-consumption buy-back tariffs and VAT rules after 2025.
8. Air-conditioning prevalence and cooking fuel mix.
9. Details of the switching, home-move, backup-supplier and supplier-of-last-resort rules (dimensions 14–16 are mostly [unverified]).
10. The VAT change on the standing charge and the tax share of the bill.
11. The billing and payment-method mix.
12. Supplier failure history and HHI values.
13. Current status of profiling and settlement-run timing: the source is from 2020.
14. Enedis's 2025–26 Linky figures.

---

## Verification, 25 Oct 2026

Confirmed 0, corrected 0, open 55. Corrections and checks:

- L31 `- Mainland France usually sees 2,000 to 3,000 DJU a year. Building regulations divide the country into three climate zones, H1 (coldest), H2` -- open: Eurostat nrg_chdd_a gives France 2,036-2,413 HDD in 2020-24 (read 2026-10-25), inside the pack's 2,000-3,000 range on France's 17°C basis; the GB comparison is not in the series after 2019.
- L167 `- Tempo prices vary by day colour, blue, white or red, with 22 red days a year [unverified]. In February 2026 Tempo rates rose 6.2% to bring` -- open: EDF's Tempo page and two encyclopaedia pages gave no count or 404 on 2026-10-25.
- L213 `- VAT: 20%. The reduced 5.5% rate on the standing charge was removed in August 2025 [unverified].` -- open (gas leg confirmed): Selectra (read 2026-10-25) states gas VAT is 20% on subscription and consumption since 1 August 2025; it does not state the electricity leg.

## Second read: the advisor's verification pass, 25 Oct 2026

The advisor checked the same tags independently (`docs/staging/advisor/DIRECTOR_EVIDENCE_VERIFICATION_OF_THE_OTHER_MARKET_PACKS_2026-10-25.md`). This page's own pass did not number items, so the rows use the advisor's numbers with this page's line. Item 22 is split in two, which gives 54 items: the 53 tagged lines of sections 1–16 and (b). The earlier "open 55" also counted the gap-list mention of [unverified]. "Secondary" marks a commercial or reporting site, not the regulator or the state.

| # | Item (line) | Prior | Advisor | Reconciled | Source |
|---|---|---|---|---|---|
| 1 | Regional range wider than GB's (L21) | open (own read: Eurostat 2,036–2,413 HDD, inside 2,000–3,000) | open | still open | — |
| 2 | GB peak 45–50 GW (L25) | open | open | still open | — |
| 3 | Single bidding zone (L51) | open | open | still open | — |
| 4 | Single gas hub PEG (L62) | open | confirmed | confirmed (secondary): single zone since 1 Nov 2018 | https://selectra.info/energie/guides/comprendre/points-echange-gaz |
| 5 | CRE "prix repère" (L63) | open | confirmed | confirmed: published since June 2023, indicative | https://www.cre.fr/fileadmin/Documents/Deliberations/2024/240523_2024-92_Decision_Methodologie_PRVG.pdf |
| 6 | About 140 ELDs (L69) | open | corrected | corrected (secondary): about 130 electricity ELDs | https://www.choisir.com/energie/articles/104108/les-entreprises-locales-de-distribution-eld-delectricite |
| 7 | About 20 gas ELDs (L71) | open | open | still open | — |
| 8 | Single-phase; three-phase available (L74) | open | confirmed | confirmed (secondary): three-phase not usually offered below 9 kVA | https://selectra.info/energie/guides/compteurs/puissance/6-kva |
| 9 | 6 and 9 kVA most common (L75) | open | corrected | corrected (secondary, citing Enedis Open Data): about 70% on 6 kVA | same as #8 |
| 10 | GB fuse 60–100 A (L77) | open | open | still open | — |
| 11 | TURPE seasonal periods (L81) | open | open | still open | — |
| 12 | GB 28m households, 2.4 people (L92) | open | open | still open | — |
| 13 | France less urban than England (L93) | open | open | still open | — |
| 14 | GB 85% gas heating, 8–10% electric (L114) | open | open | still open | — |
| 15 | GB typical use 2.7 MWh (L117) | open | corrected | corrected: 2,500 kWh elec / 9,500 kWh gas from 1 Jul 2026; the consumer page's 2,900 / 12,000 is stale | https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf |
| 16 | Electric-heated homes 8–15 MWh (L118) | open | open | still open | — |
| 17 | Gas use 10–12 MWh (L120) | open | open | still open | — |
| 18 | Offers as "regulated minus x%" (L153) | open | open | still open | — |
| 19 | Tempo 22 red days (L157) | open (EDF page gave no count) | confirmed | confirmed (secondary): 22 red, 43 white, 300 blue | https://selectra.info/energie/actualites/marche/tempo-2026-2027-nouvelle-saison-jours-rouges |
| 20 | "Amortisseur" compensation (L166) | open | open | still open | — |
| 21 | Ministerial authorisation (L169) | open | confirmed | confirmed (secondary, citing the Journal officiel order) | https://opera-energie.com/media/hydroption-faillite/ |
| 22a | Hydroption failed (L170) | open | confirmed | confirmed (secondary): liquidated Dec 2021 | same as #21 |
| 22b | Leclerc and Cdiscount suspended sales (L170) | open | open | still open | — |
| 23 | GB 65–70% smart (L190) | open | corrected | corrected: 73% at end Jun 2026 | https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin |
| 24 | Instalments plus true-up (L195) | open | open | still open | — |
| 25 | Payment-method mix (L196) | open | open | still open | — |
| 26 | No prepayment market (L197) | open | open | still open | — |
| 27 | GB 4m prepayment meters (L197) | open | open | still open | — |
| 28 | 5.5% standing-charge VAT removed Aug 2025 (L203) | open (gas leg confirmed) | confirmed | confirmed (secondary, citing ruling BOI-RES-TVA-000209): 20% from 1 Aug 2025 | https://www.journaldeleconomie.fr/?p=39654 |
| 29 | Taxes a quarter to a third (L204) | open | open | still open | — |
| 30 | GB MHHS detail (L221) | open | open | still open | — |
| 31 | No PSR equivalent (L248) | open | open | still open | — |
| 32 | Purchase-obligation tariff cut (L257) | open | confirmed | confirmed (secondary): ≤9 kWc surplus 0.04 €/kWh, bonus 80 €/kWc | https://www.hellowatt.fr/blog/mise-a-jour-tarifs-primes-solaire-t4-2025/ |
| 33 | Collective self-consumption (L259) | open | confirmed | confirmed: 2 km, 3 MW; up to 10/20 km by exception | https://www.cre.fr/fileadmin/Documents/Deliberations/2024/241218_2024-231_Projet_Arrete_Autoconso_Collective.pdf |
| 34 | Heat pump sales about 1m (L261) | open | confirmed (approx.) | confirmed (secondary, Uniclima via Effy): over 800k air-to-air plus air-to-water | https://www.effy.fr/pro/actualite/bilan-uniclima-quels-equipements-ont-ete-plebisicites-en-2025 |
| 35 | About 1.5m battery EVs (L263) | open | corrected | corrected: about 1.4m, 3.5% of 40.0m cars [derived] | https://www.statistiques.developpement-durable.gouv.fr/40-millions-de-voitures-en-circulation-en-france-au-1er-janvier-2026 |
| 36 | GB SEG and EV tariffs (L265) | open | open | still open | — |
| 37 | 25% air conditioning in 2020 (L270) | open | confirmed | confirmed (ADEME via a secondary site) | https://www.hellowatt.fr/pompe-a-chaleur/climatisation/etude-climatisation |
| 38 | Summer peaks 55–60 GW (L271) | open | confirmed | confirmed (RTE via Connaissance des Énergies): about 60 GW in 2026 | https://www.connaissancedesenergies.org/electricite-rte-detaille-les-impacts-des-vagues-de-chaleur-exceptionnelles-cet-ete |
| 39 | Cooking mostly electric (L276) | open | open | still open | — |
| 40 | Switch within days (L281) | open | open | still open | — |
| 41 | No exit fees (L282) | open | confirmed | confirmed (secondary) | https://selectra.info/energie/guides/factures/impaye/changement-de-fournisseur |
| 42 | 14-day withdrawal right (L283) | open | open | still open | — |
| 43 | No debt objection equivalent (L284) | open | corrected | corrected (secondary): deposit up to 600 € or refusal for "motif légitime" | same as #41 |
| 44 | Remote energisation in a day (L290) | open | confirmed | confirmed (secondary, supplier blog): 24 working hours | https://ekwateur.fr/blog/ma-consommation-d-energie/delais-mise-en-service-linky/ |
| 45 | Final bill reading (L291) | open | open | still open | — |
| 46 | Empty home cut off (L292) | open | open | still open | — |
| 47 | Supplier carries bad debt (L297) | open | open | still open | — |
| 48 | EDF 1 kVA in winter (L298) | open | corrected | corrected: 1 kVA all year; no residential cut-offs from 1 Apr 2022 | https://www.edf.fr/groupe-edf/espaces-dedies/journalistes/tous-les-communiques-de-presse/edf-ne-demandera-plus-la-coupure-d-electricite-pour-ses-clients-particuliers |
| 49 | Debt stays with old supplier (L299) | open | confirmed | confirmed (secondary) | same as #41 |
| 50 | Chèque énergie and FSL (L300) | open | confirmed | confirmed (secondary, thin) | same as #41 |
| 51 | Backup supplier (L301) | open | confirmed | confirmed: 2019 law; EDF electricity, TotalEnergies gas. The gas "dernier recours" leg stays unconfirmed | https://www.cre.fr/content/download/24578/file/211014_2021-315_Fourniture_de_secours.pdf |
| 52 | No GB-style failure levy (L302) | open | confirmed | confirmed: capped surcharge on transferred customers only | same as #51 |
| 53 | No capital adequacy rules (L352) | open | open | still open | — |

No item disagrees with this page's own read. This page's own read of #1 (Eurostat HDD inside the range) and #28 (gas leg) stands beside the advisor's.

**Counts: confirmed 18 · corrected 7 · still open 29.**
