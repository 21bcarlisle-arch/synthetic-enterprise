# Australia against GB: what carries over, and what a second market would need

**Knowledge:** other-market-australia

**Status:** knowledge only, not on the roadmap (director, 25 Oct 2026). From the advisor's cited evidence pack `DIRECTOR_EVIDENCE_OTHER_MARKET_AUSTRALIA_VS_GB_2026-10-25.md`, checked on 25 Oct 2026; the outcome of every [unverified] item is in the verification table at the end. Figures marked [unverified] are not claims.

**Published as:** `site/knowledge/other-market-australia/`.

---
# Australia vs GB: household energy evidence pack for Poesys

**Scope.** This pack covers the NEM states (NSW, VIC, QLD, SA, TAS, plus the ACT, which sits inside the NSW region), with short notes on WA (the SWIS/WEM). It is for understanding only, not a build plan. It includes the coordinator's scope addition, dimensions 12–16 (cooling, cooking, switching, home moves, where debt sits).

**Sourcing notes.**
- The AER website blocked automated fetching (robots), so several AER figures come from trade-press reports of AER publications, which are cited.
- The session's web-search budget ran out before I could confirm some figures. Those are marked **[unverified]**.
- My own arithmetic is marked **[derived]**.
- GB comparison figures come from memory and are marked [unverified] unless a URL is given.

---

## 1. Weather and climate

- **Degree-day base.** The BoM publishes degree-day maps with comfort bases of 12/18 °C for heating and 18/24 °C for cooling. https://www.bom.gov.au/climate/maps/averages/degree-days/
- **Cooling load varies by city.** Melbourne has about 250 cooling degree days a year and Brisbane about 1,000 (base 18 °C), same BoM source. GB has close to zero CDD18 in most years [unverified].
- **Heating load:** I could not fetch per-city HDD figures. My understanding is that Melbourne, Canberra and Hobart reach roughly 1,500–2,100 HDD18 against about 2,800–3,000 for southern England. Sydney, Adelaide and Perth are lower, and Brisbane is very low [unverified]. **Gap.**
- **Regional variation is far larger than in GB.** In 2014, 20% of households used no heating: 86% in the NT against 1% in the ACT. 26% used no air conditioning: 48% in Tasmania against 4% in the NT. https://www.abs.gov.au/ausstats/abs@.nsf/Lookup/4602.0.55.001main+features1Mar%202014
- **Energy per dwelling by state.** The colder states (ACT, VIC, TAS) use much more energy per dwelling than QLD and the NT. Victoria uses about 65% of national residential gas with about 25% of the population. https://www.energyrating.gov.au/sites/default/files/2022-12/report-residential-baseline-study-for-australia-2000-2030.pdf
- **Seasonality.** Demand has two peaks: winter evenings in the south and summer air-conditioning peaks in the north. Queensland set a peak demand record of 11,144 MW on 22 January 2025, in midsummer. https://www.aemo.com.au/newsroom/media-release/growing-renewable-capacity-in-nem-drives-fresh-records-as-coal-availability-declines
- **Solar drives the operational minimum.** Rooftop PV pushes the operational minimum to midday in spring:
  - Q4 2025 NEM record low: 9,666 MW.
  - South Australia reached −263 MW.
  - Source: https://www.energymagazine.com.au/renewables-power-half-of-the-grid-as-prices-plummet/
- **Cooling share of space conditioning energy (2014):** heating about 86%, cooling about 11%. That puts cooling at roughly 4% of all residential energy **[derived]** (Baseline Study, above).

## 2. Energy system

**Generation mix**
- **End-2024:** renewables (rooftop, utility solar, wind, hydro, batteries) made up 60% of NEM capacity and supplied 39% of generation. More than 5 GW of new capacity entered in 2024, the most since 1998. Rooftop PV reached 23 GW and home battery installs rose 62% on 2023. https://www.energymagazine.com.au/aer-unveils-state-of-the-energy-market-report/
- **Q4 2025:** renewables supplied 51% of the NEM mix.
  - Coal averaged 11,544 MW, an all-time low.
  - Gas averaged 741 MW, the lowest since 2000.
  - Rooftop solar supplied 17.6% of supply.
  - Batteries averaged 268 MW of discharge; 3,796 MW / 8,602 MWh of large-scale batteries were added since end-2024.
  - Source: https://www.energymagazine.com.au/renewables-power-half-of-the-grid-as-prices-plummet/
- **Trend:** coal-dominated but falling. Gas is a peaking and firming fuel. There is **no nuclear**.
- **Gas use:** households and small commercial customers took 36% of east-coast domestic gas demand in 2024 (AER SoEM via Energy Magazine, above).
- **WA (WEM):** renewables averaged 41.6% in Q1 2025, with rooftop PV at 20.5% of the fuel mix (AEMO release, above).

**Wholesale market design**
- An energy-only, mandatory gross pool with regional (zonal) pricing in five regions: QLD, NSW+ACT, VIC, SA, TAS.
- Interconnectors: QNI and Terranora (NSW–QLD), Heywood and Murraylink (VIC–SA), Project EnergyConnect (NSW–SA), Basslink (VIC–TAS). There is no interconnection outside Australia.
- Source: https://en.wikipedia.org/wiki/National_Electricity_Market
- **There is no day-ahead market.** Generators bid every 5 minutes into real-time dispatch. Hedging happens through OTC and ASX futures and caps [unverified for the ASX detail].
- **Price bounds:**
  - Floor: −$1,000/MWh (Wikipedia, above).
  - Market price cap 2025-26: $20,300/MWh.
  - Cumulative price threshold: $1,823,600/MWh.
  - Source: https://www.aemc.gov.au/news-centre/media-releases/aemc-updates-market-price-cap-2025-26
- **Prices:** the NEM average was $50/MWh in Q4 2025 (QLD $58, NSW $75, SA $37, VIC $37). 31% of dispatch intervals had negative prices. https://www.energymagazine.com.au/renewables-power-half-of-the-grid-as-prices-plummet/
- **June 2022 crisis:** AEMO suspended the spot market in all regions on 15 June 2022. https://claytonutz.com/insights/2022/june/aemo-takes-action-wholesale-electricity-spot-market-suspended-so-review-energy-purchase-agreements
- **Gas market:** there is no single hub like the NBP. The east coast has the Victorian DWGM, short-term trading markets (Sydney, Adelaide, Brisbane) and the Wallumbilla hub [unverified]. WA has a separate gas market with a domestic gas reservation policy [unverified].

## 3. Grid

**Network businesses**
- One TNSP per region: Powerlink, Transgrid, AusNet, ElectraNet, TasNetworks.
- 13 major DNSPs. https://en.wikipedia.org/wiki/National_Electricity_Market
- By state [unverified]:
  - NSW: Ausgrid, Endeavour, Essential.
  - VIC: CitiPower, Powercor, United Energy, Jemena, AusNet.
  - QLD: Energex, Ergon.
  - SA: SAPN.
  - TAS: TasNetworks.
  - ACT: Evoenergy.
- GB has 14 DNO areas run by 6 groups [unverified].

**Connections**
- Single-phase is common, and three-phase is frequent on newer and larger homes.
- PV export limits are expressed *per phase*. https://help.amber.com.au/hc/en-us/articles/36989656367501-Network-Export-Limits-and-Emergency-Backstop-Mechanisms
- There is no kVA subscription like France's.

**Export limits (as of May 2025, Amber source above)**
- **Static limits:**
  - Typically 5 kW per phase: Endeavour, Essential (5 kW even on three-phase), Energex (2 kW in some regional areas), the Victorian DNSPs.
  - Ausgrid: generally 10 kW per phase.
- **SA Power Networks "Flexible Exports":** a dynamic limit from 0 or 1.5 kW up to 10 kW per phase. The alternative is a fixed 0–1.5 kW per phase. Dynamic-capable inverters have been required for new systems since 1 July 2023, and remote disconnect ("Smarter Homes") since 28 September 2020. https://www.sapowernetworks.com.au/industry/flexible-exports/
- **Emergency backstop (remote PV curtailment):**
  - SA: since 2020.
  - QLD: since February 2023, for systems over 10 kW.
  - VIC: from October 2024.
  - NSW: planned from spring 2025.
  - Source: Amber, above.

**Network tariffs**
- Rules made in December 2014 require cost-reflective network tariffs. 30–50% of residential customers are expected to have retailers facing cost-reflective (ToU or demand) network tariffs by the end of current periods (Energex 22%). The shift from opt-in to opt-out assignment is speeding this up. https://www.aer.gov.au/networks-pipelines/network-tariff-reform
- Network tariffs are charged to the retailer, which can repackage them, so the retail tariff need not mirror the network tariff (same source).
- Two-way (export) network tariffs and solar "export charges" are allowed under the 2021 AEMC access-and-pricing rule [unverified].

## 4. Population and households

- **Dwellings (2021 Census):** 10,852,208 private dwellings, of which 1,043,776 were unoccupied. That leaves about 9.81 million occupied **[derived]**. https://www.abs.gov.au/statistics/people/housing/housing-census/latest-release
- **Household size:** about 2.5 persons [unverified]. GB is about 28 million households at about 2.4 persons [unverified].
- **Urbanisation:** highly urbanised and concentrated in coastal capitals [unverified for a figure]. Density is far lower than GB, with long rural SWER feeders (SAPN source, above).

## 5. Housing

- **Dwelling type (2021):** 70% separate houses, 13% townhouses, 16% apartments. **Tenure:** 31% owned outright, 35% mortgaged, 30.6% rented. https://www.abs.gov.au/statistics/people/housing/housing-census/latest-release
- **Main heating fuel (2014):** electricity 38% (mostly reverse-cycle air conditioning, which is an air-to-air heat pump), gas 30%, wood 10%, none 20%.
- **Hot water:** electric 56%, mains gas 38%, solar 10%.
- **Insulation:** 68% of homes have some, 14% none, and 18% didn't know. Queensland is highest without, at about 21%.
- Source for the three bullets above: https://www.abs.gov.au/ausstats/abs@.nsf/Lookup/4602.0.55.001main+features1Mar%202014
- **Victoria:** about 80% of homes are on gas, the highest in Australia. https://hvacrnews.com.au/news/victoria-bans-gas-in-new-homes-from-2024/
- **Typical electricity use.** These are the AER benchmark usages in the 2025-26 DMO, flat rate, no controlled load:

| Zone | Benchmark usage |
|---|---|
| Ausgrid | 3,900 kWh |
| Endeavour | 4,900 kWh |
| Essential | 4,600 kWh |
| Energex | 4,600 kWh |
| SAPN | 4,000 kWh |

  - Controlled-load (off-peak hot water) customers add about 1,800–2,200 kWh on a separate metered circuit. https://wattever.com.au/2025-26-dmo-electricity-price-rise/
  - The Victorian VDO assumes 4,000 kWh. https://www.esc.vic.gov.au/media-centre/independent-regulator-announces-victorian-electricity-default-offer
  - GB's typical domestic consumption value (TDCV) is about 2,700 kWh electricity and 11,500 kWh gas [unverified]. Australian electricity use is about 50% higher **[derived]**.
- **District heating:** essentially absent. **Oil heating:** marginal [unverified].

## 6. Core regulation

**Regulators and framework**
- AEMC makes the rules, AER regulates, AEMO operates the market.
- The National Energy Customer Framework (NERL/NERR) applies in NSW, QLD, SA, TAS and the ACT.
- **Victoria is outside the NECF** and runs its own Energy Retail Code of Practice under the ESC.
- **WA has no retail competition** for households. Synergy and Horizon Power must offer state-set uniform tariffs. A1 is about 32.4 c/kWh plus $1.16/day from 1 July 2025. https://wa.gov.au/organisation/energy-policy-wa/household-electricity-pricing
- Retailers need an AER retailer authorisation (an ESC licence in VIC) [unverified detail].

**Default prices**
- **DMO (NSW, SE QLD, SA):** a safety-net cap on *standing offers* that also acts as the reference price for advertising.
  - 2025-26: NSW +8.3% to +9.7%, SA +2.3% to +3.2%, SEQ +0.5% to +3.7%. https://www.pv-magazine-australia.com/?p=13365
  - 2026-27: NSW −3.4% to −5.0%, SEQ −7.2%, SA +1.4%. Retailers must also offer a regulated "Solar Sharer Offer" with 3 free midday hours for smart-meter customers. https://esdnews.com.au/final-dmo-confirms-electricity-prices-will-fall-in-most-regions/
- **VDO (Victoria):** 2025-26 average +$20 (+1%). About 12% of households (348,000) are on it. https://www.esc.vic.gov.au/media-centre/independent-regulator-announces-victorian-electricity-default-offer
- **Contrast with GB:** unlike the Ofgem cap, the DMO and VDO cover only a minority on standing offers. Most customers are on unregulated market offers benchmarked against the DMO.
- **Government bill credits:** the Energy Bill Relief Fund paid $150 per household in 2025-26, credited as two $75 bill credits by the retailer. https://help.amber.com.au/hc/en-us/articles/38742835037837-Energy-Bill-Relief-2025-26

**Market structure and failures**
- **Concentration:** Tier 1 retailers (AGL, Origin, EnergyAustralia) held 66% of residential electricity and 85% of gas contracts outside VIC (2019). https://www.energymagazine.com.au/aer-publishes-retail-energy-market-performance-update/ The AER reported concentration falling in 2023-24 as customers moved to smaller retailers. https://www.energymagazine.com.au/aer-annual-market-report-released/
- **Supplier failures, 2022:** Pooled Energy, Weston Energy, Enova, Power Club and Mojo Power East all went into retailer-of-last-resort (RoLR) in May–July 2022, after spot prices surged and retailers were under-hedged. https://reneweconomy.com.au/fifth-small-energy-retailer-fails-in-wake-of-ongoing-market-struggles/
  - QEnergy also failed in 2022. https://esdnews.com.au/electricity-retailers-mojo-power-and-qenergy-collapse/
  - ZEN Energy entered RoLR on 6 July 2026. https://www.energyaustralia.com.au/home/help-support/suspended-retailers

## 7. Smart meters

- **Penetration:** 57% of meters are remotely read NEM-wide:

| Jurisdiction | Remotely read |
|---|---|
| VIC | 99.1% |
| TAS | 78.1% |
| SA | 46.5% |
| QLD | 42.6% |
| ACT | 40.3% |
| NSW | 39.2% |

  - Source: https://www.aemc.gov.au/news-centre/media-releases/aemc-finalises-landmark-reform-accelerate-smart-meter-rollout
- **Universal target:** the AEMC set a target of universal deployment across the NEM by 2030. The accelerated rollout starts in December 2025, with staged reforms from December 2024 to July 2026 (including network access to power-quality data). Same source.
- **Who owns meters (Power of Choice, 1 December 2017):** outside VIC, the *retailer* appoints a competitive **Metering Coordinator**, which arranges the Metering Provider and Metering Data Provider. Victoria kept DNSP-owned AMI. https://aemo.com.au/en/newsroom/news-updates/what-does-power-of-choice-mean-for-consumers GB is the reverse: supplier-procured meters with DCC central communications [unverified].
- **Granularity:** 5-minute interval data is required from new and replacement meters under 5MS [unverified]. Victorian AMI is 30-minute [unverified].
- **Consumer data access:** the Consumer Data Right (energy) [unverified].

## 8. Billing

- **Frequency:** standard contracts must be billed "at least once every 100 days", so quarterly is the norm. Another cycle, such as monthly, needs explicit informed consent (NERR r24).
- **Basis:** bills are based on meter data. Estimates are allowed only in limited cases (r21) and must later be adjusted.
- **Bill smoothing:** optional and opt-in, re-estimated in month 7 (r23).
- **Payment terms:** the pay-by date is at least 13 business days after issue (r26).
- Source for the rules above: https://www.aemc.gov.au/sites/default/files/2020-03/NERR%20v20%20full.pdf
- The 100-day rule came from aligning billing with quarterly meter reads. https://www.aemc.gov.au/sites/default/files/content/5b867428-94c7-46bc-a7b6-d2a0bbce40bf/RRC0006-Information-Sheet-Final-Determination.PDF
- **Model contrast:** Australia bills in arrears on quarterly actuals. GB uses fixed monthly direct debit advances with a credit balance [unverified].
- **Prepayment:** enabling legislation was passed only in SA and TAS. Aurora (Tasmania) has run prepayment meters since 1997 but no longer promotes them. https://www.ewon.com.au/content/Document/PrePayment%20Meter%20Discussion%20Paper%20July%202014.pdf In practice it is marginal (about 0% against GB's ~13% [unverified]).
- **Payment methods:** BPAY, direct debit and card are common, with pay-on-time discounts on market offers [unverified].
- **New in Victoria, 1 October 2026:** at least one payment option with no charges, and an automatic best-offer obligation. https://www.esc.vic.gov.au/sites/default/files/documents/GL%20-%20Guideline-Payment%20Difficulty%20Framework%20-%201%20October%202026%20-%2020261001.pdf
- **Taxes:** GST is 10% [unverified]. GB charges 5% VAT [unverified].
- **Cost stack:** wholesale was about 35% of the residential bill (AEMC 2021 trends). https://energycouncil.com.au/electricity-price-trends-breaking-down-the-costs/ Network is roughly 40–45% [unverified].

## 9. Settlement

- **Interval:** 5-minute settlement replaced 30-minute averaging in October 2021. https://en.wikipedia.org/wiki/National_Electricity_Market The AEMC's original commencement date was 1 July 2021, later deferred [unverified].
- **Global settlement (full from 1 May 2022)** replaced "settlement by difference", under which the local retailer absorbed residual load.
  - UFE = TME − DDME − ADME.
  - UFE is allocated to all retailers in each local area pro rata to their accounted-for energy.
  - Sources: https://www.aemo.com.au/-/media/files/electricity/nem/5ms/gs-faqs.pdf?la=en and https://www.aemc.gov.au/rule-changes/global-settlement-and-market-reconciliation
- **Accumulation meters:** basic (type 6) meters are still profiled into intervals. Interval meters are settled on actuals [unverified for profile mechanics]. This is the same concept as GB's MHHS migration, but Australia's profiling disappears through meter replacement rather than a programme cutover.
- **Balance responsibility:** the retailer is the Market Customer (FRMP) and pays the spot price for its customers' load. There is **no separate imbalance price**: the spot price *is* the settlement price.
- **Reconciliation:** preliminary, final and revision runs over roughly 20–30 weeks [unverified]. MSATS is the registry: NMI standing data and the FRMP role [unverified detail].

## 10. Debt and vulnerability

- **Hardship programs:** retailers must run AER-approved hardship policies. They must offer payment plans to hardship customers and to anyone who reports payment difficulty (r33).
- **Victoria's Payment Difficulty Framework:** "standard assistance" for everyone, and "tailored assistance" once any arrears exist (more than $55 triggers an information duty within 21 business days). Arrears can be repaid over up to 2 years. Customers complying with assistance cannot be disconnected, and debt cannot be sold. ESC guideline, above.
- **Arrears prevalence (2023-24):**
  - About 2.9% of residential customers have debt over 90 days.
  - 1.9% of electricity customers are in hardship programs.
  - Average debt on entry to hardship rose 23.7%.
  - About one-third of indebted customers are on neither a plan nor hardship.
  - Source: https://www.energymagazine.com.au/aer-annual-market-report-released/
- **Disconnections** for non-payment are about 0.06% of small customers. https://www.energymagazine.com.au/aer-unveils-state-of-the-energy-market-report/
- **No winter disconnection ban.** Instead, the rules bar disconnection at certain times (Fridays, before public holidays, extreme heat days) and protect customers on life-support registers [unverified; NERR r116 and Part 7 text not retrieved].
- **Concessions** are state-funded rebates applied to bills by retailers [unverified detail].

## 11. EV, rooftop PV, home batteries, heat pumps

- **Rooftop PV:** 4.3 million systems and 28.3 GW, with 254,664 installed in 2025. The average new system is 10.6–11.6 kW. QLD has the most installations (1.16 million). https://cleanenergycouncil.org.au/getmedia/16ed1cff-8ddb-423a-b3ad-3f9fa8e4d594/rooftop-solar-and-storage-biannual-report_july-december-2025.pdf
  - 4.3m divided by about 9.8m occupied dwellings is about 44% **[derived]**. That is an upper bound because some systems are non-residential. The commonly cited "about 1 in 3 homes" is [unverified].
- **Home batteries:** 454,473 cumulative by end-2025, against 185,798 at end-2024. CEC report, above.
  - The **Cheaper Home Batteries Program** started 1 July 2025: a discount of about 25% (around $252 per usable kWh) via SRES certificates, tapering from 1 January 2027. https://solarcalculator.com.au/blog/cheaper-home-batteries-program/
  - WA's battery scheme requires VPP participation (CEC report, above).
- **Feed-in tariffs:** retailer-set and unregulated in most of the NEM. Victoria has a minimum FiT [unverified]. There is no net metering.
- **EVs:** 12.1% of new-car sales in H1 2025 and more than 410,000 on the road (about 2% of the fleet). Supported by the New Vehicle Efficiency Standard and the Electric Car Discount. https://electricvehiclecouncil.com.au/media-releases/australia-makes-gains-in-ev-uptake-but-faces-steep-road-ahead-report-finds/
- **Heat pumps:** reverse-cycle air conditioning is the most common cooling system (49% of households in 2014; ABS, above), so air-to-air heat pump stock is already large. Heat-pump hot water is subsidised through VEU and NSW schemes [unverified for numbers].
- **Electrification policy:**
  - Victoria: no gas for new homes needing planning permits from January 2024. https://hvacrnews.com.au/news/victoria-bans-gas-in-new-homes-from-2024/
  - ACT: no new gas network connections since 8 December 2023, with the goal of electrifying Canberra by 2045. https://www.climatechoices.act.gov.au/policy-programs/preventing-new-gas-network-connections

## 12. Cooling (coordinator addition)

- **Air-conditioning prevalence:**
  - About 6 in 10 dwellings had a cooler in 2005. https://www.abs.gov.au/AUSSTATS/ABS@.NSF/a9ca4374ed453c6bca2570dd007ce0a4/850C57021C2D381ECA2573D20010621A
  - By 2014, 74% had some cooling: reverse-cycle 49%, evaporative 13%, refrigerated cooling-only 10% (ABS 2014, above).
  - GB domestic air-conditioning is a few percent [unverified].
- **Cooling share of energy:** about 11% of space-conditioning energy, roughly 4% of all residential energy **[derived]**. Its share of *electricity* is higher, and highest in QLD [unverified for a figure].
- **Summer peak behaviour:** heatwaves drive the annual peak in QLD and SA [unverified for SA] (QLD record 22 January 2025, AEMO above). Evening peaks after sunset are made worse by PV drop-off. High-price events above $5,000/MWh are linked to low generation and outages (AER SoEM via Energy Magazine, above).

## 13. Cooking (coordinator addition)

- Natural gas and electricity are the main cooking fuels, but the ABS gave no shares (ABS 2008, above).
- The VIC and ACT new-build gas bans make new homes electric or induction by default (sources in section 11).
- LPG matters off the mains-gas network [unverified].
- **Named gap:** current cooking fuel shares and cooking's share of household energy.

## 14. Switching (coordinator addition)

- **Who initiates:** the gaining retailer, with the customer's explicit informed consent, through MSATS (NERR r57; text not retrieved).
- **Cooling-off:** a period exists for market contracts (r47; I believe 10 business days [unverified]).
- **Timescale:** on a smart meter, a switch can complete within days. On an accumulation meter it waits for the next scheduled read or a special read [unverified].
- **Debt does not block switching** in the NECF, as far as I know [unverified]. A designated retailer may not refuse a residential customer under a standing offer because of old debt, but may add that debt to the new contract (r18(5)–(6)).
- **Switching rates:**
  - 16% of households switched in the year to June 2025 (NSW 19%, VIC 17%, SA 17%, QLD 15%). https://www.roymorgan.com/findings/9918-electricity-switching-june-2025
  - Quarterly switching ranges from about 3% (ACT) to about 7% (VIC). https://www.energymagazine.com.au/aer-annual-market-report-released/
- **WA households cannot switch.**

## 15. Home moves (coordinator addition)

- **Default supply.** A move-in customer who has not chosen a retailer can request a standing offer from the designated retailer for the area. That retailer must act by the next business day (r17–19).
- **Consuming without a contract.** Someone who takes supply without arranging a contract is on a *deemed* arrangement with the retailer currently responsible for the premises (r53–54, r115; text not retrieved [unverified]).
- **Final bills:** the retailer must use best endeavours to arrange a final read and final bill on request (r35).
- **Vacant premises:** these stay with the current FRMP. The DNSP may de-energise them [unverified].
- **Contrast with GB:** GB's "deemed contract with the incumbent supplier" model is close in concept.

## 16. Where debt sits (coordinator addition)

- **Retailer bears arrears risk.** The retailer pays network charges (DUoS) to the DNSP whether or not the customer pays, and pays AEMO for energy. Retailers lodge credit support with AEMO, and with DNSPs under NER chapter 6B [unverified].
- **Who disconnects:** the retailer *requests* de-energisation for non-payment and the DNSP or metering provider carries it out [unverified], subject to r109–111 notices.
- **Bad debt** is funded in the retailer's margin. The DMO and VDO include a retail cost allowance [unverified for an explicit bad-debt component].
- **Retailer failure:** RoLR transfers customers to designated retailers, usually AGL, Origin or EnergyAustralia (RenewEconomy, above). The failed retailer's receivables stay with its administrator [unverified].
- **Debt does not follow the customer** to the new retailer. The old retailer pursues it, subject to hardship rules. The exception is r18(5), which lets a designated retailer add the customer's own debt to a new standard contract.
- Australia has **no network-held or centrally held household debt** [unverified], unlike GB's supplier-of-last-resort (SoLR) levy socialisation through network charges [unverified].

---

## (a) Contrast table: Australia vs GB

| # | Dimension | Australia (NEM) | GB | Difference that matters |
|---|---|---|---|---|
| 1 | Weather | Strong north–south gradient; Brisbane ~1,000 CDD18 | Heating-dominated, near-zero CDD [unverified] | Needs a multi-climate world with a cooling model |
| 2 | Energy system | 51% renewables (Q4 2025); coal falling; no nuclear; 5 regional prices; 5-min real-time pool, no day-ahead; MPC $20,300/MWh | Gas at the margin; day-ahead and intraday; single national price | Price replay must handle regional 5-min prices, frequent negatives, extreme cap events |
| 3 | Grid | 13 DNSPs; per-phase PV export limits, dynamic exports, backstop | 14 DNO areas; export limits rarer [unverified] | A connection/export limit becomes a binding household constraint |
| 4 | Households | ~9.8m occupied dwellings [derived] | ~28m [unverified] | Smaller market, larger homes |
| 5 | Housing | 70% detached; heating split electric/gas/wood; VIC 80% gas | Mostly gas boilers [unverified] | Gas-heavy VIC vs electric QLD means state-specific archetypes |
| 6 | Regulation | DMO/VDO cap standing offers only (~12% in VIC); NECF vs VIC code; WA no competition; 2022 RoLR wave | Cap covers most default tariffs | Pricing is a reference-price/advertising regime, not universal cap compliance |
| 7 | Smart meters | 57% remotely read (VIC 99%, NSW 39%); retailer-appointed Metering Coordinator; universal by 2030 | Supplier-led + DCC [unverified] | Mixed fleet: profiled accumulation + interval meters for years yet |
| 8 | Billing | Quarterly in arrears on reads; ≥ every 100 days; prepayment ~absent | Monthly DD advances; prepayment significant [unverified] | Cash-flow and debt dynamics are inverted |
| 9 | Settlement | 5-min, global settlement since May 2022, UFE shared; spot price = settlement price | 30-min, MHHS migration | Clock changes to 5 min; no separate imbalance price |
| 10 | Debt/vulnerability | Hardship programs, payment plans, VIC PDF; no winter ban; disconnections ~0.06% | Winter protections; PPM-based [unverified] | Duties are plan-based, not prepayment-based |
| 11 | DER | 4.3m PV systems, 28.3 GW; 454k batteries; EVs 12% of sales | Lower PV/battery penetration [unverified] | PV and batteries are the default customer, not an edge case |
| 12 | Cooling | ~74% have cooling; summer peaks in QLD | Negligible [unverified] | New end-use and peak driver |
| 13 | Cooking | Gas/electric split unquantified; new-build bans | Gas/electric [unverified] | Minor, but affects the gas disconnection pathway |
| 14 | Switching | Gaining-retailer led via MSATS; cooling-off; debt no block [unverified]; 16%/yr | Debt can block prepayment switches [unverified] | Faster churn on smart meters; acquisition engine needs regional DMO-referenced quotes |
| 15 | Home moves | Standing offer from designated retailer; deemed arrangements | Deemed contract with incumbent [unverified] | Conceptually transferable |
| 16 | Debt location | Retailer bears it; pays DNSP regardless; RoLR to Tier 1; debt stays with the old retailer | Supplier bears it; SoLR costs socialised [unverified] | Similar, but no levy socialisation to model [unverified] |

## (b) Transferability of the GB build

**World components**

| Component | Rating | Why |
|---|---|---|
| Weather-driven demand | Medium | Engine reusable, but needs multi-climate and cooling response |
| Building thermal model | Medium | Physics transfers; archetypes (lightweight, uninsulated, reverse-cycle air conditioning) differ |
| Household behaviour/finances | Medium | Quarterly bills and lack of prepayment change payment behaviour |
| Wholesale price replay | Low | 5-min regional prices, no day-ahead, $20,300 cap, −$1,000 floor |
| Settlement clock and reconciliation | Low | 5-min clock, global settlement UFE, profiled + interval mix |
| Smart-meter data feed | Medium | Interval feeds transfer; needs a quarterly-read accumulation path and 5-min data |
| Network/connection limits | Low | Per-phase export limits, dynamic envelopes, backstop all new |

**Supplier components**

| Component | Rating | Why |
|---|---|---|
| Tariffs and price regulation compliance | Low | DMO/VDO reference-price, Solar Sharer, network-tariff pass-through |
| Quoting/acquisition and switching | Medium | Similar logic; MSATS and explicit informed consent rules |
| Billing and payments | Low | Quarterly in-arrears billing, ≥ every 100 days, smoothing opt-in |
| DD/collections and debt | Medium | Payment-plan and hardship flows replace PPM/DD-advance logic |
| Vulnerability duties | Medium | Life support, hardship, PDF; concept overlap |
| Hedging and wholesale buying | Low | Cap/swap products against 5-min prices; RoLR lessons |
| Settlement and imbalance | Low | No imbalance price; UFE allocation |
| Capital/financial rules | Medium | Credit support with AEMO/DNSPs, no GB capital floor [unverified] |
| Advice and asset offers | High | Asset economics even stronger (PV, batteries, VPP, EVs) |

## (c) New features needed

**Simulation (world)**
1. Five-region, 5-minute price and dispatch replay with negative prices and cap/administered pricing.
2. Multi-climate weather (BoM stations) with heating *and* cooling response.
3. Reverse-cycle air-conditioning and evaporative cooling end-uses.
4. Rooftop PV on ~40% of homes, with per-phase static and dynamic export limits and an emergency backstop.
5. Home battery fleet growth (Cheaper Home Batteries) and VPP dispatch.
6. Controlled-load circuits (off-peak hot water).
7. Mixed meter fleet: accumulation with quarterly reads, 30-min AMI (VIC), 5-min new meters.
8. Global settlement UFE per local area.
9. Gas-to-electric transition in VIC and ACT.
10. Minimum-system-load events.
11. State concessions and federal bill credits.

**Supplier**
1. DMO/VDO reference-price advertising and Solar Sharer offers.
2. Network-tariff pass-through (ToU, demand, two-way).
3. Quarterly in-arrears billing with estimation and adjustment rules.
4. Hardship/PDF payment-plan engine.
5. RoLR receiving and failure modelling.
6. AEMO/DNSP credit support.
7. Cap-and-swap hedging against 5-minute volatility.
8. PV export optimisation and VPP offers.
9. MSATS transfer and Metering Coordinator appointment.

## (d) Named gaps

- City-level HDD and CDD values.
- Current heating, cooking and heat-pump shares (the ABS data is from 2014).
- Settlement revision timeline and NSLP mechanics.
- NERR text for disconnection timing, life support, cooling-off, transfer and deemed contracts (rules 47, 53, 57, 109–116).
- Current Tier 1 market share (the latest figure I have is 2019).
- Credit support and bad-debt treatment.
- Share of customers on standing vs market offers outside VIC.
- Network share of the bill.
- GST and levies breakdown.
- Smart meter data granularity by meter type.
- Feed-in tariff levels.
- GB comparison figures, all marked [unverified].

These gaps remain because the search budget ran out. Another round of searching could close most of them.

---

## Verification, 25 Oct 2026

Confirmed 0, corrected 0, open 59. Corrections and checks:

- L64 `- **There is no day-ahead market.** Generators bid every 5 minutes into real-time dispatch. Hedging happens through OTC and ASX futures and ` -- open: Wikipedia names exchange-traded futures but not the ASX product detail; AEMC/ASX not reached.
- L193 `- **Taxes:** GST is 10% [unverified]. GB charges 5% VAT [unverified].` -- open: the tax office page returned 403 on 2026-10-25.
- L198 `- **Interval:** 5-minute settlement replaced 30-minute averaging in October 2021. https://en.wikipedia.org/wiki/National_Electricity_Market ` -- open (part confirmed): Wikipedia, National Electricity Market (read 2026-10-25) says half-hourly averaging ran until October 2021; the deferral from 1 July 2021 was not confirmed (AEMC and AEMO pages returned 403).
- L254 `- **Cooling-off:** a period exists for market contracts (r47; I believe 10 business days [unverified]).` -- open: AER and Energy Made Easy pages returned a timeout or 404 on 2026-10-25.
- L256 `- **Debt does not block switching** in the NECF, as far as I know [unverified]. A designated retailer may not refuse a residential customer ` -- open: AER and Energy Made Easy pages unreachable on 2026-10-25.
