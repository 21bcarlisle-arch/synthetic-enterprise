**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] Checks against primary sources of the seven other-market packs' [unverified] items (2026-10-25)

**Type:** EVIDENCE, through the advisor channel. The director's words, from chat on Sun 25 Oct:

- 21:17 GMT: "Sorry I was delayed. It's 61% now. But time has passed."
- 07:17 GMT: "To be clear this is not to turn into SIM or supplier action at this stage it just to understand how transferable what we are building in the UK is to other markets"

Four passes, two countries each (Spain on its own), checked every `[unverified]` tag in the seven other-market packs. They checked each country's own figures first. **302 items were checked: 115 confirmed, 34 corrected, 147 still open (mostly GB comparison rows), 6 need a file.** These packs are knowledge only. Nothing here changes a priority.

## What to do with it

1. **Apply each outcome to the Other markets Knowledge pages and their tallies.** If your primary-source read disagrees with the advisor's, yours wins, and the disagreement should be recorded.
2. **Country corrections worth carrying into the pages:**
   - **Germany:** disconnection must be announced **8 working days** ahead under §19 StromGVV, not 3 (this line was not tagged in the pack). Also correct "new features (c)5" to match. About 18% of households have air conditioning (Verivox survey). 94.6% cook on electricity (Destatis). The instalment-offer duty (Abwendungsvereinbarung, §19 Abs. 5) is confirmed.
   - **France:**
     - EDF's 1 kVA limit applies **all year**, and EDF stopped residential cut-offs from 1 Apr 2022.
     - A switch is allowed with debt, but the new supplier can ask for a deposit of up to €600 or refuse for a legitimate reason, so the GB debt objection has a partial equivalent.
     - About 70% of homes are on 6 kVA. There are about 130 electricity local distribution companies (ELDs).
     - A backup supplier exists, set by the 2019 law: EDF for electricity, TotalEnergies for gas. Its costs are recovered by a capped surcharge on the customers transferred to it, not through a levy.
   - **Belgium:** Wallonia has had mandatory two-rate network tariffs since 1 Jan 2026 (peak 07–11 and 17–22). In Flanders the notice to switch supplier is at most 3 weeks. Flanders bans gas connections in new builds from 2025.
   - **Italy:** settling non-hourly households on hourly data starts from 1 Jan 2026 (ARERA 535/2024). Cooling degree days were 365 (2024). Hobs: 75.5% mains gas, 17.6% LPG. The arrears scheme for switching customers (CMOR) is run by the SII manager and covers the last 3 months, capped at about 2 months' billing.
   - **Spain:**
     - Spain did have supplier failures: six retailers were barred in Oct 2021, and Holaluz (about 250k contracts) faced proceedings in Jul 2026. Barring plus transfer to a regulated retailer (COR) is Spain's supplier-of-last-resort route.
     - Imbalance has been settled in 15-minute periods since 1 Dec 2024.
     - Since 2022 the bono social has been funded by the whole chain (RDL 6/2022), not just retailers.
     - France interconnection is 2.8 GW, rising to 5 GW in 2028.
     - The air-conditioning share is uncertain (sources give 31–43%).
   - **Australia:**
     - Unpaid network charges from a retailer insolvency can pass through to network tariffs (an AEMC rule), so part of the cost is socialised.
     - Protected periods also include Fridays, the day before a public holiday, 20–31 Dec, and extreme weather.
     - Network is 33–48% of DMO prices. 8.2% of customers in DMO regions are on standing offers.
     - The ABS counts 9.28m occupied dwellings.
   - **Japan:** Okinawa is excluded from the 2020 unbundling. The ampere-based areas are confirmed (Hokkaido, Tohoku, TEPCO, Chubu, Hokuriku, Kyushu).
3. **GB comparison rows: one conflict to resolve.** Three passes used Ofgem's 1 Jul 2026 decision for typical consumption: **2,500 kWh electricity / 9,500 kWh gas**. The Spain pass used Ofgem's consumer page (2,900 / 12,000), which has no date, and two other passes reported that page as out of date. **The decision is the authority.** Flag the consumer page as stale and do not use it. Other GB rows confirmed:
   - smart meters about 71–73% of domestic meters
   - zero VAT on domestic electricity, Oct 2026–Mar 2027
   - RF settlement run: 14 → 7 → 4 months
   - next-day switching live since Jul 2022
4. **Needs-file items** (Eurostat nrg_chdd_a and ilc_lvho01; the English Housing Survey annex tables) are fetches for you. Do them only if they are cheap. This is knowledge only.


---

# Verification pass: France and Belgium

# Verification results: France and Belgium vs GB packs (2026-10-25)

About 32 web searches were used. The country's own figures were checked first. GB figures were checked only where both packs depend on them (Ofgem TDCV, smart meter share). Several hosts (DBnomics, Eurostat, energie-info.fr, the DGCCRF page) were blocked or failed to load. Where a figure is sourced from a commercial site, the Note column says so.

## DIRECTOR_EVIDENCE_OTHER_MARKET_FRANCE_VS_GB_2026-10-25.md

| # | Item | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Regional climate range "wider than GB's" | STILL OPEN | | | Qualitative; no DJU/HDD data opened |
| 2 | GB peak about 45–50 GW | STILL OPEN | | | GB figure, not checked |
| 3 | France is a single bidding zone (EPEX) | STILL OPEN | | | Not checked against a fetched source |
| 4 | France has a single gas hub, PEG | CONFIRMED | Single zone (Trading Region France) since 1 Nov 2018 | https://selectra.info/energie/guides/comprendre/points-echange-gaz | Commercial site; a CRE source would be better |
| 5 | CRE publishes a non-binding "prix repère" for gas | CONFIRMED | PRVG published since June 2023; indicative; for GRDF residential customers; method updated from 1 Jul 2024 | https://www.cre.fr/fileadmin/Documents/Deliberations/2024/240523_2024-92_Decision_Methodologie_PRVG.pdf | |
| 6 | About 140 local distributors (ELDs) | CORRECTED | About 130 electricity ELDs (over 160 ELDs counting gas); Enedis covers 95% of the territory | https://www.choisir.com/energie/articles/104108/les-entreprises-locales-de-distribution-eld-delectricite | Secondary source |
| 7 | About 20 gas ELDs | STILL OPEN | | same | Page says only "fewer" |
| 8 | Most homes single-phase; three-phase available | CONFIRMED | Three-phase is generally not offered below 9 kVA | https://selectra.info/energie/guides/compteurs/puissance/6-kva | Commercial site |
| 9 | 6 and 9 kVA are the most common subscriptions | CORRECTED | About 70% of households are on 6 kVA; no 9 kVA share found | same | Selectra cites Enedis Open Data |
| 10 | GB fuse 60–100 A | STILL OPEN | | | GB |
| 11 | TURPE peak/off-peak periods differ by season | STILL OPEN | | | |
| 12 | GB about 28m households, 2.4 people each | STILL OPEN | | | GB |
| 13 | France less urban and dense than England | STILL OPEN | | | |
| 14 | GB about 85% gas central heating, 8–10% electric | STILL OPEN | | | GB |
| 15 | GB typical use 2.7 MWh electricity | CORRECTED | Ofgem TDCV is **2,500 kWh electricity / 9,500 kWh gas from 1 Jul 2026** (was 2,700 / 11,500) | https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf | Ofgem's consumer page still shows 2,900 / 12,000, so Ofgem's own pages disagree |
| 16 | Electrically heated homes use 8–15 MWh | STILL OPEN | | | |
| 17 | Average gas use about 10–12 MWh | STILL OPEN | | | |
| 18 | Market offers priced as "regulated tariff minus x%" (share of offers) | STILL OPEN | | | |
| 19 | Tempo has 22 red days | CONFIRMED | 22 red, 43 white, 300 blue; 2026–27 season unchanged | https://selectra.info/energie/actualites/marche/tempo-2026-2027-nouvelle-saison-jours-rouges | |
| 20 | Market-offer suppliers compensated; "amortisseur" scheme | STILL OPEN | | | |
| 21 | Suppliers need a ministerial authorisation | CONFIRMED | Hydroption's authorisation was withdrawn by ministerial order in the Journal officiel | https://opera-energie.com/media/hydroption-faillite/ | |
| 22a | Hydroption failed | CONFIRMED | Liquidated by the Toulon commercial court, Dec 2021 | same | |
| 22b | E.Leclerc Énergies and Cdiscount Énergie suspended sales | STILL OPEN | | | A search result shows Leclerc's offer ended 15 Oct 2021, but the page was not fetched |
| 23 | GB about 65–70% smart meters | CORRECTED | 73% of meters run by large suppliers were smart at end Jun 2026; 92% of those in smart mode | https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin | |
| 24 | Monthly instalments plus annual true-up; option of bi-monthly bills | STILL OPEN | | | |
| 25 | Direct debit dominant; TIP, cheque and card also used | STILL OPEN | | | |
| 26 | France has no prepayment market | STILL OPEN | | | Consistent with the 1 kVA practice (#48), but not confirmed |
| 27 | GB about 4m prepayment meters | STILL OPEN | | | Not in the DESNZ bulletin |
| 28 | 5.5% VAT on the standing charge removed Aug 2025 | CONFIRMED | Standing-charge VAT went from 5.5% to 20% on 1 Aug 2025 (tax ruling BOI-RES-TVA-000209) | https://www.journaldeleconomie.fr/?p=39654 | |
| 29 | Taxes are a quarter to a third of the bill | STILL OPEN | | | |
| 30 | GB MHHS detail | STILL OPEN | | | GB |
| 31 | No equivalent of GB's Priority Services Register | STILL OPEN | | | |
| 32 | Purchase-obligation tariff cut in 2025 for ≤9 kWc; bonus reduced | CONFIRMED | Q3/Q4 2025, ≤9 kWc: surplus 0.04 €/kWh, bonus 80 €/kWc (capped at 720 €) | https://www.hellowatt.fr/blog/mise-a-jour-tarifs-primes-solaire-t4-2025/ | Pre-cut values not in this source |
| 33 | Collective self-consumption allowed between nearby sites | CONFIRMED | Within 2 km, 3 MW cap; exceptions up to 10 km (peri-urban) and 20 km (rural) | https://www.cre.fr/fileadmin/Documents/Deliberations/2024/241218_2024-231_Projet_Arrete_Autoconso_Collective.pdf | |
| 34 | Heat pump sales about 1m a year including air-to-air | CONFIRMED (approx.) | Over 800k air-to-air units (<17.5 kW) in 2025, plus air-to-water | https://www.effy.fr/pro/actualite/bilan-uniclima-quels-equipements-ont-ete-plebisicites-en-2025 | Uniclima data via Effy; no total given |
| 35 | About 1.5m battery EVs | CORRECTED | About 1.4m: 3.5% of 40.0m cars at 1 Jan 2026 [derived] | https://www.statistiques.developpement-durable.gouv.fr/40-millions-de-voitures-en-circulation-en-france-au-1er-janvier-2026 | |
| 36 | GB Smart Export Guarantee; EV time-of-use tariffs widespread | STILL OPEN | | | GB |
| 37 | About 25% of households had air conditioning in 2020 (ADEME) | CONFIRMED | 25% in 2020 (about 8m main residences); 14% in 2017, 22% in 2019 | https://www.hellowatt.fr/pompe-a-chaleur/climatisation/etude-climatisation | ADEME CODA "Stratégie été 2020", seen via a secondary site |
| 38 | Summer peaks around 55–60 GW | CONFIRMED | Summer 2026 peak about 60 GW, similar to 2019 | https://www.connaissancedesenergies.org/electricite-rte-detaille-les-impacts-des-vagues-de-chaleur-exceptionnelles-cet-ete | RTE via CdE |
| 39 | Cooking mostly electric | STILL OPEN | | | |
| 40 | Switch carried out within days; next day possible with Linky | STILL OPEN | | | DGCCRF and energie-info pages failed |
| 41 | No exit fees; switch at any time | CONFIRMED | | https://selectra.info/energie/guides/factures/impaye/changement-de-fournisseur | Commercial site |
| 42 | 14-day withdrawal right | STILL OPEN | | | |
| 43 | Debt does not block a switch; no equivalent of GB's debt objection | CORRECTED | A switch is allowed, but a new supplier may ask a deposit of up to 600 € or refuse for "motif légitime" (e.g. debt over 50 € in the ARPE file). A cut-off already started can continue after the switch | same | Partial equivalent to the GB objection exists |
| 44 | Remote energisation on move-in, within a day or so | CONFIRMED | Linky: 24 working hours; new builds 10 working days (5 express) | https://ekwateur.fr/blog/ma-consommation-d-energie/delais-mise-en-service-linky/ | Supplier blog |
| 45 | Final bill uses a remote or customer reading | STILL OPEN | | | |
| 46 | Distributor cuts off an empty home with no contract after a set period | STILL OPEN | | | |
| 47 | Supplier carries bad debt; "contrat unique"; pays TURPE regardless | STILL OPEN | | | |
| 48 | EDF caps power at about 1 kVA in winter | CORRECTED | EDF caps at 1 kVA **all year** and stopped residential cut-offs from 1 Apr 2022 | https://www.edf.fr/groupe-edf/espaces-dedies/journalistes/tous-les-communiques-de-presse/edf-ne-demandera-plus-la-coupure-d-electricite-pour-ses-clients-particuliers | |
| 49 | Debt stays with the old supplier | CONFIRMED | | https://selectra.info/energie/guides/factures/impaye/changement-de-fournisseur | |
| 50 | Chèque énergie and housing solidarity funds (FSL) are outside safety nets | CONFIRMED | Recipients of either are excluded from the ARPE file and deposits | same | Thin source |
| 51 | Backup supplier details | CONFIRMED | Created by the Énergie-Climat law of 8 Nov 2019; minister designates after a CRE call, for 5 years; EDF (Enedis area, electricity), TotalEnergies (GRDF area, gas); gas article L.443-9-3 | https://selectra.info/energie/actualites/marche/fournisseur-energie-faillite-fournisseur-secours ; https://www.cre.fr/content/download/24578/file/211014_2021-315_Fourniture_de_secours.pdf | The separate gas "dernier recours" supplier is not confirmed |
| 52 | No GB-style levy spreading failure costs across bills | CONFIRMED | Extra costs, including unpaid bills, are recovered through a capped surcharge on transferred customers only: residential ≤10 €/site/month for 6 months, applied for 12 months at most | https://www.cre.fr/content/download/24578/file/211014_2021-315_Fourniture_de_secours.pdf | Gas deliberation |
| 53 | No GB-style capital adequacy rules | STILL OPEN | | | |

**France totals:** 54 rows (item 22 split into two). 18 confirmed, 7 corrected, 29 still open, 0 needs-file.

## DIRECTOR_EVIDENCE_OTHER_MARKET_BELGIUM_VS_GB_2026-10-25.md

| # | Item | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 1 | Maritime climate; Ardennes colder | STILL OPEN | | | |
| 2 | Heating degree days about 2,600–2,900; UK about 3,000 | NEEDS-FILE | | https://ec.europa.eu/eurostat/databrowser/view/nrg_chdd_a/default/table (or DBnomics nrg_chdd_a, series A.HDD.BE / A.HDD.UK) | DBnomics and Eurostat blocked here |
| 3 | Doel 4 and Tihange 3 run to about 2035 | CONFIRMED | 10-year extension to 2035; target restart by Nov 2025 | https://nuclear.engie-electrabel.be/en/nuclear-energy/key-questions-about-nuclear-power-plants/if-end-2021-it-turns-out-we-still-need | |
| 4 | Single Core bidding zone; day-ahead moved to 15-min products in 2025 | CONFIRMED (part) | SDAC 15-min market time unit live for delivery day 1 Oct 2025 | https://www.epexspot.com/en/news/market-coupling-steering-committee-confirms-go-live-15-minute-mtu-sdac-trading-day-30 | Single-zone/Core point not separately fetched |
| 5a | Fluxys is the gas transmission operator | CONFIRMED | Also: L-gas to H-gas conversion finished end of summer 2024 | https://en.wikipedia.org/wiki/Fluxys | Wikipedia |
| 5b | ZTP (Zeebrugge) is the gas hub | STILL OPEN | | | |
| 6 | GB has 14 DNO areas run by 6 groups | STILL OPEN | | | GB |
| 7 | 3×230 V supply without neutral; 40 A main breaker common | STILL OPEN | | | |
| 8 | Walloon guidance on connections up to 10 kVA (content) | STILL OPEN | | | |
| 9a | Wallonia new time-of-use network tariffs | CONFIRMED | From 1 Jan 2026, mandatory two-rate: peak 07–11 and 17–22 every day; off-peak 11–17 and 22–07; no weekend distinction. Optional five-band "Impact" tariff (needs active smart meter, ≤56 kVA) | https://www.cwape.be/sites/default/files/cwape-documents/2025.11.03-Tarifs%20distribution%202026_CP.pdf | |
| 9b | Brussels new time-of-use tariffs 2025–29 | STILL OPEN | | | |
| 10 | GB about 28m households | STILL OPEN | | | GB |
| 11 | Brussels almost entirely flats | STILL OPEN | | https://ibsa.brussels/sites/default/files/publication/documents/Mini-Bru_2025_FR.pdf | Only found: 81.7% of 2023 resales were flats |
| 12 | GB oil heating about 4% of homes | STILL OPEN | | | GB |
| 13 | About 71% owner-occupied | STILL OPEN | | https://www.iweps.be/wp-content/uploads/2023/03/Communique-de-presse-RS08-propriete.pdf | Only found: Wallonia 56.5% of dwellings owner-occupied (2011 census), a different measure |
| 14 | Ofgem typical use about 2,700 kWh / 11,500 kWh | CORRECTED | 2,500 / 9,500 kWh from 1 Jul 2026 | Ofgem PDF (France #15) | |
| 15 | Liberalised: Flanders 2003, Wallonia and Brussels 2007 | CONFIRMED | Wallonia and Brussels on 1 Jan 2007 | https://callmepower.be/fr/energie/guides/comprendre/liberalisation-marche | Source does not discuss a price cap |
| 16 | Supply licences are regional | STILL OPEN | | | |
| 17 | GB about 60–65% smart or advanced meters | CORRECTED | 73% (end Jun 2026) | DESNZ bulletin (France #23) | |
| 18 | Prepayment only as a DSO debt tool; payment-method mix | STILL OPEN | | | |
| 19 | VAT 6% permanent since April 2023, with federal excise | CONFIRMED | Permanent from 1 Apr 2023; excise moves inversely with prices | https://www.vrt.be/vrtnws/en/2023/03/31/reduction-in-vat-on-gas-and-electricity-becomes-permanent-from-1 | |
| 20 | Smart-metered households stay profiled unless they opt in | CONFIRMED (data side) | Default regime 1 (monthly volumes) since 1 Apr 2024; quarter-hour data (regime 3) needs explicit consent through the supplier | https://vlaamsenutsregulator.be/sites/default/files/uploads/parlementaire_vragen/2024-2025/antwoord_2.pdf | The link to settlement treatment is inferred |
| 21 | Elia settles imbalance per 15 minutes with balance responsible parties | CONFIRMED | Invoiced per quarter-hour, two months in arrears | https://www.elia.be/customers/invoicing-and-tariffs/imbalance-invoice | |
| 22 | GB MHHS | STILL OPEN | | | GB |
| 23a | Social tariff pegged to the lowest commercial tariff | CONFIRMED | Energy component is based on the lowest commercial tariff; quarterly; rise caps of 10%/20% (electricity) and 15%/25% (gas) | https://selectra.be/fr/energie/tarifs/tarif-social | Commercial site |
| 23b | Social tariff funded by a federal levy | STILL OPEN | | | |
| 24 | GB voluntary winter moratorium and PSR | STILL OPEN | | | GB |
| 25 | Flanders limits gas connections in new builds | CONFIRMED (stronger) | General ban on gas connections for new builds from 2025; large projects banned since 2021 (5+ units from 2023) | https://www.vlaanderen.be/bouwen-wonen-en-energie/verwarming-koeling-en-ventilatie/nieuwe-verwarmingsinstallatie-kiezen/geen-aardgasaansluitingen-meer-bij-nieuwbouw-en-nieuwe-grote-projecten | |
| 26 | Air conditioning low and rising | STILL OPEN | | | |
| 27 | Cooking fuel mix | STILL OPEN | | | |
| 28 | No exit fee; new supplier handles switch; within 21 days; 14-day cooling-off | CONFIRMED (part) | Flanders: new supplier arranges everything; no termination fee; notice at most 3 weeks | https://www.vlaanderen.be/eenvoudig-veranderen-van-energieleverancier/stappenplan-veranderen-van-energieleverancier | The pack's "one month's notice" is not supported; cooling-off still open |
| 29 | GB next-working-day switching | STILL OPEN | | | GB |
| 30 | Takeover document signed by both occupants; contract follows the customer | CONFIRMED | Both sign and send to their own supplier within 7 days; the document is not a contract, and the supplier sets up the contract at the new address | https://www.fluvius.be/sites/fluvius/files/2025-08/zorgeloos-verhuizen-met-het-energieovernamedocument.pdf | |
| 31 | Unclaimed points go to the DSO ("MOZA") procedure | STILL OPEN | | | Fluvius document does not cover it |

**Belgium totals:** 34 rows (items 5, 9 and 23 split). 12 confirmed, 2 corrected, 1 needs-file, 19 still open.

**Overall:** 88 rows. 30 confirmed, 9 corrected, 1 needs-file, 48 still open (most are GB comparisons, cooking or air-conditioning items, or French switching and home-move procedure details).

**Corrections that matter most:**
- **Ofgem TDCV:** the typical-use values are now 2,500 kWh electricity and 9,500 kWh gas from 1 Jul 2026. This changes the GB figure in both packs and may affect other Poesys documents.
- **GB smart meters:** 73% of meters are smart, higher than either pack says.
- **EDF 1 kVA cap:** it applies all year, not only in winter.
- **French switching with debt:** a new supplier can ask for a deposit or refuse, so this is closer to GB's debt objection than the France pack says.
- **Flanders switching:** notice is at most 3 weeks, not one month.

No new account memory came up.

---

# Verification pass: Australia and Japan

# Verification report: Australia and Japan vs GB evidence packs

I checked every [unverified] item in both packs. I did the country figures first and then the GB comparisons. I used about 39 web searches, so the shared budget is spent and the remaining items are marked STILL OPEN. Most Australian sources had to be found through search because they weren't on the fetch allowlist. The AEMC NERR v20 PDF in the pack came back as unreadable binary, so the rule text was confirmed from other NERR versions (v12 and v17) and from AER pages.

Four findings change the packs' content:
- **Ofgem has revised the GB typical consumption values (TDCV).** From 1 July 2026 they are **2,500 kWh electricity and 9,500 kWh gas**, down from 2,700 and 11,500. Both packs use the old values. The Australia pack's derived "Australian use ~50% higher" therefore becomes about 60% or more.
- **The ABS reports 9,275,217 occupied private dwellings for 2021.** The Australia pack derived ~9.81m by taking unoccupied dwellings away from the total, which doesn't give the ABS figure. This changes the derived PV share and the household figure in the contrast table.
- **Network costs are 33–48% of the bill in the DMO regions,** not the 40–45% the Australia pack assumed. The same AER source shows **8.2%** of residential customers on standing offers in the DMO regions, which closes one of the pack's named gaps.
- **Retailer failure does reach network charges in Australia.** The AEMC's final rule on retailer default lets distributors pass unpaid network charges from a retailer insolvency through to network tariffs, with no materiality threshold. So the pack's claim that Australia has "no network-held or centrally held debt" needs qualifying: part of the cost is spread across customers.

---

## Pack 1: DIRECTOR_EVIDENCE_OTHER_MARKET_AUSTRALIA_VS_GB_2026-10-25.md

| # | Item | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 1 | GB near-zero CDD18 | STILL OPEN | | | GB, lower priority |
| 2 | Melb/Canberra/Hobart HDD18 1,500–2,100; S England 2,800–3,000 | STILL OPEN | | | BoM city HDD not reached |
| 3 | Hedging via OTC and ASX futures and caps | CONFIRMED | | https://www.asxenergy.com.au/products/au_electricity | Base load futures, $300 caps and options for NSW, VIC, QLD, SA. Peak futures added mid-2025 |
| 4 | East-coast gas: DWGM, STTM (Sydney, Adelaide, Brisbane), Wallumbilla hub | CONFIRMED | Gas Supply Hub covers Wallumbilla **and Moomba** | https://aemo.com.au/learn/energy-markets-and-systems | Pipeline capacity trading and a day-ahead auction also exist |
| 5 | WA domestic gas reservation policy | CONFIRMED | 15% of each LNG project's production | https://wa.gov.au/government/publications/wa-domestic-gas-policy | WA has a contestable gas retail market (AEMO page above) |
| 6 | DNSPs by state | CONFIRMED | | https://www.energymadeeasy.gov.au/frequently-asked-questions/who-is-my-energy-distributor ; https://selectra.com.au/energy/network/distributors | 13 in the NEM; VIC has 5 |
| 7 | GB 14 DNO areas, 6 groups | CONFIRMED | | https://en.wikipedia.org/wiki/Distribution_network_operator | Secondary source. ENWL is now Iberdrola-owned (as is SPEN), so the group count may now be 5 |
| 8 | Two-way export tariffs allowed under the 2021 AEMC rule | STILL OPEN | | | AEMC rule page not on the allowlist |
| 9 | Household size ~2.5 | CONFIRMED | 2.5 (2021) | https://www.abs.gov.au/census/find-census-data/quickstats/2021/AUS | |
| 9b | [derived] ~9.81m occupied dwellings | CORRECTED | 9,275,217 occupied private dwellings | same ABS QuickStats | Changes the derived PV share to about 46% |
| 9c | GB ~28m households at ~2.4 | STILL OPEN | | | GB |
| 10 | Urbanisation figure | STILL OPEN | | | |
| 11 | GB TDCV 2,700 / 11,500 kWh | CORRECTED | **2,500 / 9,500 kWh from 1 Jul 2026** | https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf | Changes the "~50% higher" derived figure |
| 12 | District heating absent; oil marginal | STILL OPEN | | | |
| 13 | AER retailer authorisation; ESC licence in VIC | STILL OPEN | | | Not confirmed in time |
| 14 | GB supplier-procured meters + DCC | STILL OPEN | | | GB |
| 15 | 5-min data from new and replacement meters; VIC AMI 30-min | CORRECTED (partly) | New/replacement type 4 meters must be 5-min capable from 1 Dec 2018 (type 4A from 1 Dec 2019) and configured by 1 Dec 2022. Types 5/6 are profiled | https://wattclarity.com.au/?p=18102 | VIC AMI 30-min still open |
| 16 | Consumer Data Right (energy) | CONFIRMED | Product data from 1 Oct 2022; consumer data from 15 Nov 2022 (AGL, Origin, EA first); retailers with 10k+ customers from 1 Nov 2023 | https://cdr.gov.au/rollout/cdr-energy-sector | |
| 17 | GB monthly DD advances | STILL OPEN | | | GB |
| 18 | GB prepayment ~13% | STILL OPEN | | | GB |
| 19 | BPAY / DD / card; pay-on-time discounts | STILL OPEN | | | |
| 20 | GST 10% | CONFIRMED | | https://www.ato.gov.au/businesses-and-organisations/international-tax-for-business/in-detail/trans-tasman-rules/comparing-the-new-zealand-and-australian-tax-system/goods-and-services-tax | GB 5% VAT still open |
| 21 | Network ~40–45% of the bill | CORRECTED | 33–48% of DMO prices, varying by region and customer type | https://www.aer.gov.au/system/files/2025-05/AER%20-%20Final%20determination%20-%20Default%20market%20offer%20prices%202025%E2%80%9326%20-%2026%20May%202025_0.pdf | |
| 22 | 5MS originally 1 Jul 2021, deferred | CONFIRMED | Deferred 3 months to 1 Oct 2021 | https://www.aemc.gov.au/rule-changes/delayed-implementation-five-minute-and-global-settlement ; https://wattclarity.com.au/?p=18102 | |
| 23 | Type 6 profiled into intervals | CONFIRMED | Converted to intervals in MSATS using the NSLP for each distribution network area | https://wa.aemo.com.au/-/media/files/electricity/nem/settlements_and_payments/prudentials/nem-settlement-process.pdf | |
| 24 | Revisions over ~20–30 weeks; MSATS as registry | CONFIRMED | Preliminary within 5 business days; final within 18 business days; routine revisions at ~20 and ~30 weeks | same AEMO PDF | |
| 25 | Disconnection barred on Fridays, before public holidays, extreme heat; life support | CORRECTED (detail) | r116 bars it for life-support premises, complaints, customers keeping to a payment plan, pending concessions, "extreme weather event" (for r111 non-payment), and protected periods. Protected periods (r108) are before 8am or after 3pm on business days, Fridays, the day before a public holiday, weekends and public holidays, and 20–31 Dec | https://www.aemc.gov.au/sites/default/files/2019-01/NRR%20-%20v17%20-%20Part%206.PDF ; https://www.aer.gov.au/system/files/AER%20Compliance%20Check%20Protected%20Periods.pdf | The rule says "extreme weather", not specifically heat. The 20–31 Dec ban is new to the pack |
| 26 | Concessions state-funded, applied by retailers | STILL OPEN | | | |
| 27 | "~1 in 3 homes" have PV | STILL OPEN | | https://cleanenergycouncil.org.au/news-resources/australia-powers-ahead-on-rooftop-solar-as-nation-set-to-achieve-2030-rooftop-target-new-report | CEC: more than 4.2m homes and small businesses (Jun 2025); no share given |
| 28 | Victoria has a minimum FiT | CONFIRMED | 2025-26 flat rate 0.04 c/kWh; time-varying 0–6.57 c/kWh | https://esc.vic.gov.au/media-centre/solar-minimum-feed-tariffs-2025-26 | The government signalled it may deregulate. Status for 2026-27 still open |
| 29 | Heat-pump hot water subsidised via VEU and NSW schemes | STILL OPEN (partial) | Solar Victoria $1,000 rebate; ~20,000 installed | https://onestepoffthegrid.com.au/demand-surges-for-heat-pump-rebates-as-households-go-electric/ | VEU and NSW ESS not confirmed directly |
| 30 | Heatwaves drive the SA annual peak | CONFIRMED | SA record 3,623 MW on 16 Dec 2024 (previous 3,511 MW, Feb 2024) | https://reneweconomy.com.au/wind-and-solar-output-records-tumble-as-grid-demand-hits-new-highs-in-midst-of-heatwave | Trade press. VIC record 9,851 MW the same day |
| 31 | Cooling's electricity share highest in QLD | STILL OPEN | | | |
| 32 | LPG matters off-grid | STILL OPEN | | | |
| 33 | Cooling-off 10 business days | CONFIRMED | NERR r47(2) | https://www.aemc.gov.au/sites/default/files/2018-04/NRR%20-%20v12%20-%20Part%202.PDF | |
| 34 | Accumulation-meter switch waits for a read | STILL OPEN | | | |
| 35 | Debt does not block switching | STILL OPEN | | https://markets-portal-help.docs.public.aemo.com.au/Content/MSATSTechnicalGuide/Objections.htm | The objection code list is in the CATS Procedures, not fetched. r18(6) is confirmed: a designated retailer can't refuse a residential customer for debt |
| 36 | Deemed arrangements (r53–54) | CONFIRMED | r53: FRMP must give contract info; r54: may treat a move-in or carry-over customer as on the standing offer | NRR v12 Part 2 (above); https://aemc.gov.au/regulation/energy-rules/NECF-ACL/mapping/contract-terms | |
| 37 | Vacant premises stay with the FRMP; DNSP may de-energise | STILL OPEN | | | |
| 38 | Credit support with AEMO and DNSPs | CORRECTED (nuance) | AEMC kept the existing regime. A distributor can request credit support only after payment failures in the past 12 months. Main protection is a retailer-insolvency cost pass-through | https://www.aemc.gov.au/sites/default/files/content/dc8219f0-3e81-4d74-a659-1cfb26362d36/Information-sheet-final-determination.pdf | AEMO prudential side not fetched |
| 39 | Retailer requests de-energisation; DNSP carries it out | CONFIRMED | NERR r119(1)(a); restrictions in r120 | NRR v17 Part 6 (above) | |
| 40 | DMO retail cost allowance includes bad debt | CONFIRMED | Bad and doubtful debt is part of "retail and other costs", a weighted average of what retailers report | AER DMO 2025-26 final (above) | Also: 8.2% of residential customers on standing offers |
| 41 | Failed retailer's receivables stay with its administrator | STILL OPEN | | | |
| 42 | No network-held household debt; GB SoLR levy | CORRECTED (AU part) | Unpaid network charges from a retailer insolvency can be passed through to network tariffs (no materiality threshold) | AEMC info sheet (#38) | This is partial spreading of the cost. GB part still open |
| 43 | GB export limits rarer | STILL OPEN | | | GB |
| 44 | GB capital floor | STILL OPEN | | | GB |
| 45 | GB debt can block prepayment switches | STILL OPEN | | | GB |
| 46 | GB smart meters (table row) | CONFIRMED | ~65% of 54m+ domestic meters were smart in smart mode at end-2025 | https://assets.publishing.service.gov.uk/media/69b80e30b84f01b2be53a2b1/Q4_2025_Smart_Meters_Statistics_Report.pdf | |

**Australia totals:** 48 rows (45 items plus three sub-rows). 19 CONFIRMED, 8 CORRECTED (2 of them partial), 21 STILL OPEN (one partial). 0 NEEDS-FILE, 0 UNPUBLISHED.

---

## Pack 2: DIRECTOR_EVIDENCE_OTHER_MARKET_JAPAN_VS_GB_2026-10-25.md

| # | Item | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 1 | GB 4–6 °C January, 15–17 °C summer | STILL OPEN | | | GB |
| 2 | GB HDD 2,000–2,300 (base 15.5) | STILL OPEN | | | GB |
| 3 | LNG mostly oil-indexed | STILL OPEN | | https://aperc.or.jp/file/2025/7/3/1355-1405_JPN_OGSN_updates.pdf | APERC: ~80% of LNG is bought on long-term contracts; pricing basis not stated |
| 4 | A capacity market and a balancing market exist | CONFIRMED | | https://www.iea.org/reports/japan-2021 | No dates given |
| 5 | Okinawa may be exempt from unbundling | CONFIRMED | Okinawa Electric is listed as excluded (対象外) | https://www.meti.go.jp/shingikai/enecho/denryoku_gas/denryoku_gas/pdf/017_07_01.pdf | |
| 6 | GB one TSO and 14 DNO areas | CONFIRMED | 14 DNO areas, 6 groups | https://en.wikipedia.org/wiki/Distribution_network_operator | Secondary source |
| 7 | Single-phase three-wire 100/200 V | STILL OPEN | | | |
| 8 | Kansai, Chugoku, Shikoku, Okinawa use minimum charges | CONFIRMED | Ampere-based: Hokkaido, Tohoku, TEPCO, Chubu, Hokuriku, Kyushu | https://enechange.jp/articles/electricity-basic-rate | |
| 9 | Household size 2.21 (2020) | CONFIRMED | 2.21 per general household (2.33 in 2015) | https://www.stat.go.jp/info/guide/asu/pdf/2023asu_3-2.pdf | |
| 10 | GB ~28m households | STILL OPEN | | | GB |
| 11 | GB ~20% flats | STILL OPEN | | | GB |
| 12 | GB TDCV 2,700 / 11,500 | CORRECTED | **2,500 / 9,500 kWh from 1 Jul 2026** | https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf | Update section 5 and contrast row 5 |
| 13 | ~700+ registered retailers | STILL OPEN | | https://www.meti.go.jp/press/2025/12/20251224001/20251224001-1.pdf | No total stated. 94 took part in the 2025 ranking (104 in 2024) |
| 14 | GB about two-thirds smart | CONFIRMED | ~65% in smart mode, end-2025 | https://assets.publishing.service.gov.uk/media/69b80e30b84f01b2be53a2b1/Q4_2025_Smart_Meters_Statistics_Report.pdf | |
| 15 | Card and convenience-store payment common; no prepayment | STILL OPEN | | | |
| 16 | No social tariff and no PSR equivalent | STILL OPEN | | | |
| 17 | Balancing-group plans changeable until 1 hour before delivery | CONFIRMED | Plans changeable up to 1 hour before delivery; intraday market also closes then | https://www.issoh.co.jp/column/details/16831/ | Secondary source |
| 18 | GB MHHS 2025–27 | STILL OPEN | | | GB |
| 19 | GB BEV share ~19% | STILL OPEN | | | GB |
| 20 | GB air conditioning <5% | STILL OPEN | | | GB |
| 21 | Gas cookers in the majority, IH a minority | STILL OPEN | | https://www.env.go.jp/content/900516264.pdf | The MoE survey asks cooktop type but doesn't publish shares in this PDF |
| 22 | GB mostly gas hobs | STILL OPEN | | | GB |
| 23 | GB switching 5 working days, 14-day cooling-off, debt objection | STILL OPEN | | | GB |
| 24 | Final bill on the stop-date smart read | STILL OPEN | | | |
| 25 | Retailer owns debt; T&D charges the retailer network fees | STILL OPEN | | | |
| 26 | No mutualisation of bad debt | STILL OPEN | | | |
| 27 | GB SoLR credit balances protected; levy | STILL OPEN | | | GB |

**Japan totals:** 27 items. 8 CONFIRMED, 1 CORRECTED, 18 STILL OPEN. 0 NEEDS-FILE, 0 UNPUBLISHED.

---

**Overall:** 75 rows. 27 CONFIRMED, 9 CORRECTED, 39 STILL OPEN. 0 NEEDS-FILE, 0 UNPUBLISHED.

These sources would close the main remaining gaps:
- **NERR text:** a readable NERR version, for vacant premises and r115.
- **MSATS CATS Procedures:** the objection code list, for whether debt can block a switch.
- **The AEMC DER access-and-pricing rule page:** for two-way export tariffs.
- **The MoE household CO2 survey data tables:** for Japan's cooking-fuel shares.
- **The ANRE registered-retailer list:** for Japan's retailer count.

---

# Verification pass: Germany and Italy

# Verification results: Germany and Italy packs (25 Oct 2026)

**What happened:**
- I used about 38 web searches; the cap was about 40.
- I checked each country's own figures first and GB figures only where budget was left.
- Direct fetches were allowlist-only, so lxgesetze.de, gesetze-im-internet.de and new DBnomics series URLs could not be opened. The DBnomics/Eurostat API was also blocked by the proxy (403).
- **Findings that affect both packs:**
  - Ofgem revised the GB typical consumption figures (TDCVs) on 1 Jul 2026 to **2,500 kWh electricity and 9,500 kWh gas**. Both packs still use 2,700 and 11,500.
  - GB smart-meter coverage is **73%**, not "about two-thirds".
  - The Germany pack has a material error in a line that was not tagged: under §19 StromGVV the disconnection must be announced **8 working days** ahead, not 3.

---

## 1. DIRECTOR_EVIDENCE_OTHER_MARKET_GERMANY_VS_GB_2026-10-25.md

| # | Item (short quote of the claim) | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 1 | "~3,000 HDD per year" | NEEDS-FILE | — | https://ec.europa.eu/eurostat/databrowser/view/nrg_chdd_a (series A.NR.HDD.DE) | DBnomics API blocked by proxy. The Eurostat SE PDF gives Bayern 3,357 HDD and EU 3,199 (1979–2022), but no national DE figure. |
| 2 | "more continental… colder winters, warmer summers" | STILL OPEN | — | — | — |
| 3 | "regional spread wider than GB" | STILL OPEN | — | https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/92378.pdf | Bayern 3,357 HDD hints at a colder south, but there is no DE-wide comparison. |
| 4 | "solar resource clearly better in the south" | STILL OPEN | — | — | — |
| 5 | Last nuclear plants closed April 2023 | CONFIRMED | 15 Apr 2023 | https://www.enerdata.net/publications/daily-energy-news/germany-shuts-down-its-last-remaining-nuclear-reactors-4-gw.html | — |
| 6 | GB last coal plant closed 2024 | CONFIRMED | Ratcliffe-on-Soar, 30 Sep 2024 | https://www.iom3.org/resource/last-uk-coal-fired-power-station-closes.html | — |
| 7 | DE distributed PV "several times larger than GB's" | STILL OPEN | — | — | GB figure not checked. |
| 8 | DE-LU single bidding zone | CONFIRMED | DE-LU since the DE-AT split; first delivery day 1 Oct 2018 | https://epexspot.com/en/news/epex-spot-publish-separate-prices-and-volumes-austrian-and-german-day-ahead-markets | — |
| 9 | GB 1 system operator, 3 TSOs, 14 DNO areas plus IDNOs | STILL OPEN | — | — | GB. |
| 10 | Three-phase is the norm in German homes | STILL OPEN | — | — | — |
| 11 | GB single-phase, 60–100 A fuse | STILL OPEN | — | — | GB. |
| 12 | GB has no statutory control-for-discount regime | STILL OPEN | — | — | GB. |
| 13 | GB time-of-use network signal via DUoS | STILL OPEN | — | — | GB. |
| 14 | GB ~28m households, ~2.4 persons | STILL OPEN | — | — | GB. |
| 15 | Polycentric settlement; Stadtwerk per town | STILL OPEN | — | — | — |
| 16 | GB renting ~35% | STILL OPEN | — | — | GB. |
| 17 | Shared heating billed through Nebenkosten | STILL OPEN | — | — | — |
| 18 | Germany has a high share living in flats | NEEDS-FILE | — | https://ec.europa.eu/eurostat/databrowser/view/ilc_lvho01 | The Eurostat housing page shows only EU 48% flats (2024); the country chart could not be extracted. |
| 19 | GB ~85% gas, ~4% oil | STILL OPEN | — | — | GB. |
| 20 | Ofgem TDCV ~2,700 kWh electricity / 11,500 kWh gas | CORRECTED | **2,500 kWh / 9,500 kWh from 1 Jul 2026** (2,700/11,500 were the 2023 values) | https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf | — |
| 21 | No SoLR auction or mutualised levy | STILL OPEN | — | — | — |
| 22 | Entry by notification only; no GB-style financial-resilience regime (§6 and table row) | CONFIRMED | — | https://gesetze.legal/bund/enwg/5 | Nuance: under §5 EnWG suppliers must show personnel, technical and economic capacity and reliability, and electricity suppliers must keep hedging strategies (Abs. 4a). BNetzA may prohibit a supplier. There are no capital thresholds. |
| 23 | Price brakes ended 31 Dec 2023 | CONFIRMED | — | https://vdiv.de/news-details/preisbremsen-werden-nicht-verlaengert | — |
| 24 | GB Energy Price Guarantee was a per-unit discount | STILL OPEN | — | — | GB. |
| 25 | GNDEW: 20/50/95% path; >6,000 kWh, PV >7 kW, §14a mandatory; ~€20 cap | CONFIRMED | Bands are 6,000–100,000 kWh and 7–100 kW | https://www.zfk.de/digitalisierung/smart-city-energy/smart-meter-rollout-kann-erneut-starten | §14a group not mentioned in this source. |
| 26 | GB ~two-thirds smart (table: ~65%) | CORRECTED | **73%** of meters run by large suppliers were smart, end Jun 2026 (39m domestic) | https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin | — |
| 27 | Meter operator (DSO by default) vs GB supplier-responsible | STILL OPEN | — | — | — |
| 28 | §40b EnWG billing choice; more frequent information for smart customers | CONFIRMED | Monthly, quarterly or half-yearly billing on request; billing period at most 1 year; free monthly billing information with remote transmission | https://gesetze.legal/bund/enwg/40b | — |
| 29 | GB billing monthly or quarterly; DD reviewed periodically | STILL OPEN | — | — | GB. |
| 30 | GB ~25 p/kWh, 5% VAT | STILL OPEN | — | — | GB. |
| 31 | SEPA direct debit and transfer dominate | STILL OPEN | — | — | — |
| 32 | GB ~4m prepayment meters | STILL OPEN | — | — | The DESNZ bulletin has no prepayment figure. |
| 33 | GB MHHS timings | STILL OPEN | — | — | GB. |
| 34 | Mehr-/Mindermengenabrechnung trues up profiled volumes after the read | CONFIRMED (mechanism) | — | https://bet-consulting.de/fileadmin/redaktion/PDF/Veroeffentlichungen/2009/BET-Artikel_Mehr-Mindermengenabrechnung_0906.pdf | DSO calculates forecast minus actual from the reading. Timeline still open. |
| 35 | GB reconciliation runs to ~14 months | STILL OPEN | — | — | GB. |
| 36 | Abwendungsvereinbarung (instalment offer) required since 2022 | CONFIRMED | §19 Abs. 5 StromGVV; amendment dated 1 Dec 2021 | https://www.gegen-hartz.de/urteile/schulden-keine-gebuehren-bei-stromschulden-und-mehr-zeit-fuer-ratenzahlungen ; https://www.buzer.de/gesetz/7424/al162357-0.htm (title only) | Interest-free monthly instalments, offered no later than the disconnection announcement. |
| 36a | (Not tagged) "disconnection date announced three working days ahead" | CORRECTED | **8 working days** | https://www.ggew.de/uploads/Downloads/Abwendungsvereinbarung_Muster_19Strom-_GasGVV.pdf ; gegen-hartz (above) | Material: feature list (c)5 also needs changing. |
| 37 | No statutory winter ban | CONFIRMED | — | https://dserver.bundestag.de/btd/20/026/2002686.pdf | Bundestag motion, Jul 2022: no general ban, only hardship cases. Later changes not checked. |
| 38 | GB voluntary winter protections; forced-PPM ban | STILL OPEN | — | — | GB. |
| 39 | No social tariff or WHD equivalent | STILL OPEN | — | same Bundestag doc | Indirect only: it lists social tariffs abroad, not in DE. |
| 40 | No PSR-style register | STILL OPEN | — | — | — |
| 41 | GB ~1.5–2m PV homes | STILL OPEN | — | — | GB. |
| 42 | GB SEG set by suppliers | STILL OPEN | — | — | GB. |
| 43 | GB heat-pump sales ~60–100k/yr | STILL OPEN | — | — | GB. |
| 44 | Residential AC "single-digit to low-teens %" | CORRECTED | **~18% of households** (Verivox representative survey) | https://www.zfk.de/energie/strom/klimaanlagen-kein-hitzeschock-fuers-stromnetz | Survey, not official statistics; Destatis EVS has no AC line. |
| 45 | National peak is in winter | STILL OPEN | — | — | — |
| 46 | Cooking mostly electric; gas rare | CONFIRMED | Electric cooker 94.6%, gas cooker 4.4% of households (2023) | https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Einkommen-Konsum-Lebensbedingungen/Ausstattung-Gebrauchsgueter/Tabellen/a-evs-haushaltsgeraete-d.html | — |
| 47 | GB gas homes often cook with gas | STILL OPEN | — | — | GB. |
| 48 | Basic supply terminable at two weeks' notice | CONFIRMED | §20(1) StromGVV | https://gesetze.legal/bund/stromgvv/20 | — |
| 49 | Special contracts: 12-month minimum, then monthly notice | CONFIRMED (secondary) | — | https://www.check24.de/strom-gas/ratgeber/faire-verbrauchervertraege | Monthly notice after the initial term. |
| 50 | 14-day Widerruf for distance contracts | STILL OPEN | — | — | Not fetched. |
| 51 | No GB-style debt objection on switching | STILL OPEN | — | https://www.verivox.de/strom/ratgeber/strom-trotz-schufa-1000811/ | Old debts make it harder to find a new supplier, but no formal block was found. |
| 52 | New-customer bonuses widespread | CONFIRMED | Bonuses up to €800 via Check24 | https://www.check24.de/strom-gas/ratgeber/faire-verbrauchervertraege | — |
| 53 | Final bill deadline ~6 weeks | STILL OPEN | — | — | §40c not readable. |
| 54 | No central bad-debt mechanism | STILL OPEN | — | — | — |
| 55 | Network charges owed by supplier regardless of customer payment | STILL OPEN | — | — | — |
| 56 | Debt stays with old supplier | STILL OPEN | — | — | — |
| 57 | Suppliers commonly run SCHUFA checks | CONFIRMED (qualified) | — | https://www.verivox.de/strom/ratgeber/strom-trotz-schufa-1000811/ | "Not every supplier checks." The default supplier must supply anyway. |
| 58 | GB 5-day switching; lower switch rate | STILL OPEN | — | — | GB. |

**Germany totals (59 rows, including untagged 36a):** 15 confirmed · 4 corrected · 2 needs-file · 38 still open (most of these are GB items).

---

## 2. DIRECTOR_EVIDENCE_OTHER_MARKET_ITALY_VS_GB_2026-10-25.md

| # | Item (short quote of the claim) | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 1a | Italy national HDD ~1,800–2,000 | NEEDS-FILE | — | https://ec.europa.eu/eurostat/databrowser/view/nrg_chdd_a (A.NR.HDD.IT) | API blocked. |
| 1b | Italy CDD ~200–450 | CONFIRMED (secondary) | 365 CDD in 2024, 4th-highest in EU | https://germanpedia.com/?p=24200 | Cites Eurostat. |
| 2 | No nuclear; plants closed after 1987 referendum | CONFIRMED | Referendum Nov 1987; Caorso and Trino shut Jul 1990 | https://world-nuclear.org/information-library/country-profiles/countries-g-n/italy.aspx | — |
| 3 | Zones Nord, Centro-Nord, Centro-Sud, Sud, Calabria, Sicilia, Sardegna | CONFIRMED | — | https://storico.mercatoelettrico.org/En/Mercati/MercatoElettrico/Zone.aspx | GME list. |
| 4 | Capacity market plus MACSE storage auctions | CONFIRMED (MACSE) | First MACSE auction 30 Sep 2025: 10 GWh, South and islands | https://www.teleborsa.it/AMP/News/2025/10/01/terna-conclusa-la-prima-asta-macse-assegnati-10-gwh-di-capacita-di-accumulo-di-energia-155.html | Capacity market itself still open. |
| 5 | Gas hub is the PSV | STILL OPEN | — | — | — |
| 6 | e-distribuzione ~85% of points | CONFIRMED (approx., proxy) | 86.5% of kWh distributed by the 11 largest DSOs, 2024 [derived: 219.35/253.65 TWh] | https://www.arera.it/fileadmin/allegati/operatori/elettricita/241022_impreseEE.pdf | Volume share, not points. |
| 7 | ~120 electricity and ~190 gas DSOs | STILL OPEN | — | same | The ARERA list has only the 11 large electricity DSOs. |
| 8 | Three-phase typical above ~6–10 kW | STILL OPEN | — | — | — |
| 9 | GB fuse ≈14–23 kW, no capacity charge | STILL OPEN | — | — | GB. |
| 10 | 2017 reform: non-progressive, three-part tariff | CONFIRMED | Trinomial "TD" tariff from 1 Jan 2017; fully non-progressive for all domestic customers in 2018 | https://www.arera.it/schede-tecniche/dettaglio/it/schedetecniche/16/782-16st | — |
| 11 | Network tariff has no time-of-use element | CONFIRMED (by absence) | — | same | The ARERA fact sheet mentions no ToU element. |
| 12 | GB ~28m households, ~2.36 | STILL OPEN | — | — | GB. |
| 13 | GB gas TDCV 11,500 kWh (and "matches GB's 2,700 kWh") | CORRECTED | **9,500 kWh gas / 2,500 kWh electricity from 1 Jul 2026** | https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf | Italy's typical customer (2,700 kWh / ~11,600 kWh) is now above GB's. |
| 14a | Owner-occupation ~70–75% | CONFIRMED | 75% (OECD) | https://en.ilsole24ore.com/art/in-eu-countries-68-per-cent-of-households-live-at-home-AI82F8ZB | Year not stated. |
| 14b | Most people live in flats | NEEDS-FILE | — | https://ec.europa.eu/eurostat/databrowser/view/ilc_lvho01 | — |
| 15 | Large share of stock pre-1976 | STILL OPEN | — | — | — |
| 16 | GB ~25–30 suppliers | STILL OPEN | — | — | GB. |
| 17 | Elenco Venditori licensing and capital rules | CONFIRMED (qualitative) | — | https://luce-gas.it/fornitori/eve-elenco-venditori-elettricita | Share capital proportionate to volume, guarantees and good-standing tests; no amounts given. |
| 18 | First generation rolled out in the 2000s | CONFIRMED | Enel Telegestore 2001–2005, ~30m meters | https://www.enel.com/content/dam/enel-com/pressrelease/porting_pressrelease_IT/554779-1_PDF-1.pdf | — |
| 19 | Readings routed to sellers via the SII hub | CONFIRMED | — | https://www.e-distribuzione.it/content/dam/e-distribuzione/documenti/open-meter/nuove-guide-open-meter/Una_Guida_su_cui_contare_Vademecum.pdf | Data is managed "within the SII". |
| 20 | Two-year billing limit, Law 205/2017 | CONFIRMED | Electricity catch-up bills from Mar 2018; gas from Jan 2019 (ARERA 97/2018) | https://tariffe.segugio.it/news-tariffe/bollette-luce-e-gas-quando-vanno-in-prescrizione-00031986.aspx | Secondary source. |
| 21 | No prepayment meter product | CONFIRMED | — | e-distribuzione guide (row 19) | Payment mix still open. |
| 22 | Gas VAT 10% on first 480 Smc, 22% above | CONFIRMED | 22% also applies to fixed charges; a temporary 5% rate ran Oct 2022–Dec 2023 | https://www.enel.it/content/dam/asset/documenti/assistenza/luce-gas/articoli/faq-bollette-enel-energia/Totale%20imposte.pdf ; https://www.money.it/bollette-gas-senza-iva-agevolata-1-gennaio-2024-paga-in-piu | Electricity 10% also confirmed. |
| 23 | GB 5% VAT | STILL OPEN | — | — | GB. |
| 24 | Households without hourly metering settled by load profiling | CONFIRMED (nuance) | Non-hourly points use a conventional profile from the Profilo Residuo di Area (PRA); reform to hourly-data settlement set for 1 Jan 2026 | https://www.arera.it/fileadmin/allegati/docs/24/535-2024-R-eel.pdf | — |
| 25 | Whether every LV household is settled on actual intervals | STILL OPEN | — | same | The non-hourly share is "sharply reduced"; no completion date given. |
| 26 | "Annual and multi-year adjustment sessions" | CORRECTED (terminology) | The named mechanism is the **"sessione di conguaglio load profiling"** | same | Multi-year calendar still open. |
| 27 | GB MHHS; ~14-month reconciliation | STILL OPEN | — | — | GB. |
| 28 | No winter disconnection ban | STILL OPEN | — | — | — |
| 29 | GB BEV share ~20% | STILL OPEN | — | — | GB. |
| 30 | Gas hobs dominate; LPG common | CONFIRMED | Hobs 75.5% mains gas, 17.6% LPG (2021) | https://www.istat.it/it/files/2022/06/REPORT-CONSUMI-ENERGETICI-FAMIGLIE-2021-DEF.pdf | Induction share not given. |
| 31 | Switching rates far above GB | STILL OPEN | — | — | Italy's 20.8%/18.8% are confirmed in ARERA RA 2025; GB side not checked. |
| 32 | 14-day cooling-off | CONFIRMED | Since 13 Jun 2014 (ARERA 266/2014), up from 10 days | https://www.arera.it/comunicati-stampa/dettaglio/it/com-stampa/14/140611 | — |
| 33 | Voltura / subentro / prima attivazione | CONFIRMED (voltura, subentro) | — | https://www.money.it/voltura-o-subentro-differenze-costi-e-tempi | Secondary source; prima attivazione not covered. |
| 34 | New occupant must actively contract with a chosen supplier | CONFIRMED (subentro) | — | same | Nuance: a voltura takes over the existing contract, with no interruption. |
| 35 | Sistema Indennitario run by Acquirente Unico | CONFIRMED (partly) | Run by the "Gestore del SII"; claim 6–12 months after switch; covers unpaid bills for the last 3 months; capped at the average of 2 months' billing | https://arera.it/operatore-elettricita/faq-chiarimenti-sul-sistema-indennitario | Acquirente Unico not named on the page; the €10 minimum was not found. |
| 36 | Unpaid system charges recoverable via an ARERA mechanism | STILL OPEN | — | — | — |
| 37 | Default/last-resort bad debt socialised | STILL OPEN | — | — | — |
| 38 | Salvaguardia serves non-domestic; households go to tutela/STG | CONFIRMED | — | https://bolletta-energia.it/fornitore/enel/salvaguardia | Secondary source. |

**Italy totals (40 rows):** 21 confirmed · 2 corrected · 2 needs-file · 15 still open (most are GB items).

---

**Overall (99 rows):** 36 confirmed · 6 corrected · 4 needs-file · 53 still open · 0 unpublished.

**Edits the packs need:**
- **Germany pack:** change "three working days" to "8 working days" in §10 and in feature (c)5. Change residential AC to "~18% (Verivox survey)".
- **Both packs:** change the GB TDCVs to 2,500 / 9,500 kWh (from 1 Jul 2026) and GB smart coverage to 73%.
- **Italy §5:** the claim that Italy's electricity figure "matches GB's 2,700 kWh" is now out of date.

**Needs someone with network access:** Eurostat `nrg_chdd_a` (HDD for DE and IT) and `ilc_lvho01` (share living in flats, DE and IT).

---

# Verification pass: Spain

# Verification results: Spain vs GB evidence pack

I checked all 40 [unverified] items in the pack, Spain's own figures first. Five table rows that only repeat a body item are folded into that item, and table-only GB claims are listed separately (items 37–40). About 40 web searches and 35 page fetches.

## DIRECTOR_EVIDENCE_OTHER_MARKET_SPAIN_VS_GB_2026-10-25.md

### Spain's own figures

| # | Item | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 2 | "OMIE operates the day-ahead and intraday auctions plus continuous intraday" | CONFIRMED | — | https://cdn.document360.io/01edfa70-9a6e-4b53-9d36-c28ae0819f3a/Images/Documentation/20240201_Presentaci%C3%B3n%20AM%20IDA_20240201_final.pdf | OMIE seminar deck. Three EU intraday auctions (IDA1–3) replaced the six MIBEL sessions; planned go-live 13 Jun 2024. Gate closures 15:00, 22:00 and 10:00 D+1. Continuous trading pauses around each auction. |
| 3 | France interconnection "about 3 GW or about 3% of capacity" | CORRECTED | 2,800 MW today. Bay of Biscay link takes it to 5,000 MW, expected 2028. 2.8/130 GW ≈ 2% [derived] | https://www.renewableenergymagazine.com/panorama/el-bei-inyecta-1-600-millones-para-20250616 | The EU 2030 target is 15%. |
| 4 | "about 330 DSOs" | CORRECTED | Nearly 350 (CNMC census), "more than 300" | https://www.renewableenergymagazine.com/panorama/los-estados-de-china-argelia-catar-e-20221223 ; https://roams.es/energia/luz/distribucion-electrica/ | Both cite the CNMC distributor list (sede.cnmc.gob.es/listado/censo/1). Article dated Dec 2023. |
| 6 | "smart meter trips if contracted power is exceeded" | CONFIRMED | — | https://selectra.es/energia/noticias/potencia-contratada-2026-potencia-maxima-contador ; https://www.endesa.com/es/blog/blog-de-endesa/luz/icp-que-es-por-que-salta | The power limiter (ICP) is built into the meter. No official tolerance margin is published. |
| 7 | "Most homes are single-phase" | CONFIRMED | — | https://www.endesa.com/es/blog/blog-de-endesa/luz/instalacion-monofasica-trifasica | Qualitative only ("lo habitual… monofásica"). No percentage found. |
| 12 | Electricity "about 3,000–3,500 kWh/yr per household" | CONFIRMED | 3,272 kWh (REE); 3,487 kWh (IDAE, *Consumos del Sector Residencial*) | https://www.xatakahome.com/iluminacion-y-energia/comparar-tu-consumo-luz-media-espana-tu-vecindario-asi-puedes-hacerlo | Secondary article quoting both publishers. |
| 14 | Spain's licence bar is lower than GB's licence plus capital rules | CONFIRMED (qualitative) | — | https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/distribuidores/comercializadores.html ; https://osborneclarke.com/insights/ofgem-announces-gb-energy-market-reforms | Spain needs only a filed declaration plus REE/OMIE guarantees. GB has a capital floor of £0 and a target of £115 per dual-fuel customer from 31 Mar 2025 (Osborne Clarke). |
| 15 | "no wave of failures, and no SoLR… equivalent was needed" | CORRECTED | Spain did have failures. MITECO barred six retailers in Oct 2021 (e.g. Secom, Another Energy Option). In Jul 2026 it opened proceedings against Holaluz (~250k contracts) | https://www.rastreator.com/tarifas-energia/articulos-destacados/quiebra-comercializadoras-subida-luz ; https://www.merca2.es/2026/07/20/holaluz-suspendida-cotizacion-expediente-2421058/ | Not a GB-scale wave. Barring a retailer followed by transfer to a COR works as Spain's SoLR. Holaluz details are from a secondary source; check in the BOE. |
| 16 | Fallback "transfer to a COR" | CONFIRMED | — | https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/distribuidores/comercializadores.html ; https://derecholocal.es/?p=16832 | RD 88/2026 art. 8.3 keeps the transfer to the COR "under the legally established procedure". Customers move onto the PVPC. The detailed procedure is still not found. |
| 18 | "Monthly billing is now common" | STILL OPEN | — | — | The RD 88/2026 summaries seen don't state a billing period. Needs the full Reglamento text in the BOE. |
| 19 | No fixed monthly direct debit building a credit balance, no prepayment meters | STILL OPEN | — | https://derecholocal.es/?p=16832 | RD 88/2026 art. 6.1.q mentions "sistemas de pago anticipado" only to cap their charges. No prepayment-meter regime found. |
| 21 | 15-min imbalance settlement period "[unverified date]" | CONFIRMED (date found) | Since 1 Dec 2024 | https://www.smartgridsinfo.es/2025/02/13/consulta-procedimientos-operacion-electricos-negociacion-cuarto-horaria | The EU deadline was 1 Jan 2025 ([CNMC resolution](https://www.cnmc.es/sites/default/files/editor_contenidos/Energia/Consulta%20Publica/1_DCOOR_DE_008_21_Resolucion_cuarto_horario.pdf)). |
| 22 | Profiling is only a fallback | CONFIRMED | — | https://laadministracionaldia.inap.es/noticia.asp?id=1261830 | 2026 profiles cover type 4 and 5 points without hourly records. Resolution of 22 Dec 2025 (BOE 30 Dec 2025), applies from 1 Jan 2026. |
| 24 | How self-consumption exports are valued | CONFIRMED | PVPC: hourly market price minus imbalance cost, published daily by REE on eSios. Free market: the price agreed in the contract | https://www.energias-renovables.com/fotovoltaica/ya-hay-precio-para-el-excedente-de-20190514 ; https://selectra.es/autoconsumo/normativa/compensacion | — |
| 25 | Virtual batteries are commercial, not regulatory | CONFIRMED | — | https://selectra.es/autoconsumo/normativa/compensacion | Described as retailer offers, outside the RD 244/2019 mechanism. |
| 28 | AC "today it is likely over 50%" | CORRECTED (provisional) | No source supports >50%. INE living-conditions survey: 31% of households have AC (survey year not given). Triodos survey: about 40% use AC in summer | https://www.elindependiente.com/economia/2025/07/01/el-aire-acondicionado-la-bomba-climatica-que-tiene-en-su-sala-y-no-lo-sabe/amp/ ; https://www.corresponsables.com/actualidad/social/menos-de-la-mitad-de-los-hogares-espanoles-ponen-el-aire-acondicionado-en-verano | These conflict with the CNMC 2015 figure of 42.8% (different definitions). Keep as a gap. |
| 29 | Summer peak rivals winter, both near 40 GW | CONFIRMED (approx.) | 2025 peninsular peak 40,070 MW (15 Jan, 20:57). June 2025 instantaneous max 37,872 MW | https://www.ree.es/sites/default/files/2025-12/1912-np-datos-cierre-2025-en.pdf ; https://www.ree.es/sites/default/files/publication/2025/07/downloadable/Boletin%20mensual%20Junio%202025.pdf | July/August 2025 bulletins not checked. |
| 30 | Butane "about several million households" | CONFIRMED | About 8m homes. Price set by formula (DGPEM), published in the BOE, max ±5% per revision; 12.5 kg cylinder €17.83 (Jul 2026) | https://www.merca2.es/2026/07/20/subida-bombona-butano-2026-2421056/ | Press source only. |
| 31 | 14-day cooling-off under general consumer law | CONFIRMED (partial) | — | https://derecholocal.es/?p=16832 | RD 88/2026 art. 6.1.z gives a withdrawal right under RDL 1/2007. The 14-day length (art. 71 of that law) was not re-fetched. |
| 32 | No debt block on switching | STILL OPEN | — | https://www.boe.es/eli/es/rd/2026/02/11/88/con | No block found. But under RD 88/2026 a customer in arrears cannot stop the distributor's database from showing that status, so gaining retailers can screen for it. |
| 33 | Home move: change of holder (cambio de titular) or reactivation (alta), with DSO fees | CONFIRMED | Change of holder is free. A new connection, or one dormant over 3 years, pays regulated extension, access and connection fees plus a deposit (2019: €17.37, €19.70 and €9.04 per kW) | https://www.ocu.org/vivienda-y-energia/gas-luz/noticias/alta-suministro-luz | Article from 2019. RD 88/2026 requires distributors to return old deposits within 4 months. |
| 34 | No deemed contract; supply stays in the previous occupant's name | CONFIRMED | — | https://www.ocu.org/vivienda-y-energia/gas-luz/noticias/alta-suministro-luz | The contract stays with the previous holder until a change is requested. |
| 35 | Bono social "paid by electricity groups and retailers" | CORRECTED | Since RDL 6/2022, every link in the supply chain pays: producers (per MWh), transmission (per € remunerated), distributors (per supply point), retailers (per customer) and direct consumers (per MWh) | https://ga-p.com/wp-content/uploads/2022/04/Financiacion_Bono_Social.pdf | The Supreme Court (2022, following the EU Court of Justice) annulled the retailer-only regime. CNMC proposes the split; MITECO approves it. |
| 36 | Debt stays with the old retailer | STILL OPEN | — | https://www.ocu.org/vivienda-y-energia/gas-luz/noticias/alta-suministro-luz | One nuance: a new holder who takes over a contract inherits its obligations, so debt can pass to that person. |

### GB comparison figures (lower priority)

| # | Item | Result | Correct value (if corrected) | Source URL | Note |
|---|---|---|---|---|---|
| 1 | GB "about 2,800–3,100 HDD… CDD close to zero" | CONFIRMED (approx.) | Long-term HDD by city: London 2,800, Manchester 3,073, Birmingham 3,518, Edinburgh 3,393. CDD 0–58 | https://www.eurima.org/uploads/files/modules/articles/1576835588_EURIMA-ECOFYS_VII_report_p66-104_ANNEXES1.pdf | Eurostat-method HDD on long-term weather data. Northern GB runs above 3,100. |
| 5 | GB "14 licensed DNO areas under 6 groups, plus IDNOs" | CONFIRMED | — | https://www.ofgem.gov.uk/sites/default/files/docs/2013/11/css_overview_1213_0.pdf | Ofgem 2013; ownership groups may have changed since. IDNOs not checked. |
| 8 | GB fuse "typically 60–100 A" | CONFIRMED | — | https://meteroperators.org.uk/?p=18550 | Energy Networks Association: 60 A is the default fuse for cut-outs rated up to 100 A. |
| 9 | GB "about 28m households of 2.4 people" | CORRECTED | 28.6m households, 2.35 people (UK, 2024) | https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/bulletins/familiesandhouseholds/2024 | These are UK figures, not GB. A newer ONS release exists. |
| 10 | GB "about 20% flats" | NEEDS-FILE | — | https://www.gov.uk/government/statistics/english-housing-survey-2023-to-2024-climate-resilient-homes-fact-sheet/english-housing-survey-2023-to-2024-climate-resilient-homes-fact-sheet | The fact sheet gives only 24% (1945–2012 stock) and 27% (post-2012). The all-dwellings share is in the English Housing Survey annex tables (xlsx). |
| 11 | GB gas "about 11,500 kWh" | CORRECTED | Ofgem typical use: 12,000 kWh gas, 2,900 kWh electricity | https://www.ofgem.gov.uk/information-consumers/energy-advice-households/average-gas-and-electricity-use-explained | The page gives no effective date. |
| 13 | GB "about 85%" on gas | CONFIRMED (approx.) | Gas is the main heating fuel in 89% (pre-1945), 85% (1945–2012) and 78% (post-2012) of homes | https://www.gov.uk/government/statistics/english-housing-survey-2023-to-2024-climate-resilient-homes-fact-sheet/english-housing-survey-2023-to-2024-climate-resilient-homes-fact-sheet | England only. Measures main heating fuel, not mains-gas connection. |
| 17 | GB "about two-thirds smart, many not working in smart mode" | CORRECTED | End-2025: 71% of domestic meters smart or advanced (~38m of 54m+). 92.3% of all smart and advanced meters run in smart mode; roughly 65% of all domestic meters do | https://assets.publishing.service.gov.uk/media/69b80e30b84f01b2be53a2b1/Q4_2025_Smart_Meters_Statistics_Report.pdf | DESNZ Q4 2025 report. |
| 20 | GB VAT 5% | CORRECTED | Domestic electricity is at 0% from 1 Oct 2026 to 31 Mar 2027. Gas stays at 5% | https://www.icaew.com/insights/tax-news/2026/sep-2026/vat-cut-on-domestic-electricity-bills-confirmed | Live now, and it affects Poesys's own GB billing too. |
| 23 | GB MHHS "about 4 months to its final run (RF)" | CORRECTED | RF is 14 months today. It drops to 7 months from 1 Apr 2027 and to 4 months from 2 Jul 2027 | https://www.elexon.co.uk/bsc/article/new-settlement-timetable-reducing-from-14-months-to-seven-months-from-april-2027/ | The first payment run (SF) also goes from 15 to 7 working days. |
| 26 | Smart Export Guarantee "with no cap tied to the import bill" | CONFIRMED | — | https://www.ofgem.gov.uk/environmental-programmes/smart-export-guarantee-seg/electricity-suppliers | The rate must be above zero. Mandatory for suppliers with 150k+ domestic customers. No link to import. |
| 27 | GB EV share "about 20% or more" | CONFIRMED | 2025 new cars: battery-electric 23.4%, plug-in hybrid 11.1% | https://www.smmt.co.uk/uk-new-car-market-breaches-two-million-as-almost-one-in-four-buyers-go-electric/ | Battery-electric share was below the 28% zero-emission mandate. |
| 37 | (Table 2) GB 30-min settlement | CONFIRMED | — | https://www.elexon.co.uk/bsc/article/new-settlement-timetable-reducing-from-14-months-to-seven-months-from-april-2027/ | Half-hourly settlement period. Page not re-fetched for this point. |
| 38 | (Table 3) GB "unit-rate network charges" | STILL OPEN | — | — | Possibly out of date: since 2022, residual network costs are thought to be recovered through fixed daily charges. Not checked. |
| 39 | (Table 13) GB cooking "gas and electric" | STILL OPEN | — | — | Not checked. |
| 40 | (Table 14) GB "fast switching, lower rates post-2022" | CONFIRMED (speed only) | Next-day switching went live 18 Jul 2022 (previously up to 15 working days) | https://www.idoxgroup.com/news/reliable-next-day-energy-switching-goes-live-after-eight-years-in-the-making/ | Switching rates not checked; needs Ofgem's retail market indicators. |

**Pack totals:** 40 items. 22 CONFIRMED, 10 CORRECTED, 7 STILL OPEN, 1 NEEDS-FILE, 0 UNPUBLISHED. For Spain's own figures alone: 14 confirmed, 5 corrected, 4 still open.

**Overall:** 40 items: 22 confirmed, 10 corrected, 7 still open, 1 needs-file.

### Other findings for the pack
- **Gap (d)3, REE 2025 mix, now has figures** ([REE 2025 year-end note](https://www.ree.es/sites/default/files/2025-12/1912-np-datos-cierre-2025-en.pdf)):
  - Renewables about 56% (57% counting self-consumption): wind 22%, solar PV about 19% (a record).
  - Nuclear about 19%, gas combined cycle about 17%.
  - Demand about 256 TWh (+2.6%). Net exports about 13 TWh, the fourth year in a row.
- **Complaints deadline:** RD 88/2026 sets 15 *business* days. §6 says "15 days" ([GA-P](https://ga-p.com/wp-content/uploads/2026/02/Energia_electrica.pdf)).
- **Dates on the new rules:** several RD 88/2026 articles (6, 13, 28–30 and 43–45) only took effect four months after 12 Feb 2026. §6's "in force 12 Feb 2026" needs that caveat.
- **Debt and guarantees, July 2026:** CNMC is reportedly asking retailers to top up guarantees to cover about €250m of unpaid bills ([merca2](https://www.merca2.es/2026/07/17/cnmc-comercializadoras-garantias-impagos-2419511/), headline only, unverified). Relevant to §16.

### Worth remembering
- GB domestic electricity VAT is 0% from 1 Oct 2026 to 31 Mar 2027.
- Elexon's final reconciliation run (RF) is 14 months now, 7 months from Apr 2027 and 4 months from Jul 2027.
- Ofgem's typical household use is now 12,000 kWh gas and 2,900 kWh electricity.

These touch Poesys's GB simulation, not just this pack.
## Done

Applied 25 Oct 2026, 22:20-22:40 GMT. This is knowledge only, as the director said on 25 Oct at
07:17: nothing here becomes SIM or supplier action. Three readers each took disjoint notes (France
and Belgium; Australia and Japan; Germany, Italy and Spain). The seat applied the page edits.

1. **Notes.** Each of the seven `other_market_*` notes ends with a "Second read" table and a
   superseding counts line. The census now reads, for the other markets: Germany 19/10/35,
   Australia 19/8/33, France 18/7/29, Belgium 10/7/22, Italy 17/4/22, Japan 9/2/19 and Spain 23/15/11
   (confirmed/corrected/open). Those figures were 0-3 confirmed per country before. Across all 28
   packs: 232 confirmed (+3 partly), 92 corrected, 227 open.
2. **Country corrections, carried into the note bodies and the published pages:**
   - Germany: the disconnection notice is 8 working days, in §10 and feature (c)5. Air conditioning
     is about 18%.
   - France: about 130 ELDs; about 70% of homes on 6 kVA; EDF's 1 kVA limit applies all year; the
     deposit-or-refuse route for a customer in debt; the backup suppliers.
   - Belgium: Flanders notice is at most 3 weeks; Wallonia has two-rate network tariffs; Flanders
     bans gas in new builds.
   - Italy, Spain, Australia, Japan: as listed in the file. Spain's M+11 reconciliation is shorter
     than GB's 14 months today, not longer.
   Sixteen prose replacements were made in `site/data/knowledge_topics.json`.
3. **The GB TDCV conflict** is resolved for Ofgem's 1 Jul 2026 decision (2,500 / 9,500) in every
   GB comparison row. The undated consumer page (2,900 / 12,000) is recorded as stale and is not
   used.
4. **Disagreements, where the note's own primary read stands:**
   - Germany's smart-meter cap: EUR 30 from BNetzA, against the advisor's EUR 20 from trade press.
   - Belgium's social tariff: CREG's own wording, against a commercial site's.
5. **Corrected by the seat, outside the advisor's scope.** The Italy note said GB's debt objection
   applies only to prepayment debt assignment. That is wrong. SLC 14 objection covers debt over 28
   days on any meter, and the DAP is the separate prepayment route.
6. **Left undone.** The "Still missing" lists on the Germany, Italy and Spain pages still name
   items the second read has since found. Trimming them is cosmetic and goes with the needs-file
   continuation `fetch-the-packs-needs-file-sources-and-settle-eco4-and-slc-27-15`.
