# Director evidence: vpps third party flex and local network payments

**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 06:44 GMT: "Maybe you can also research vpp, over the top flex payments and also network payments in certain post codes for flex. Also EV and heat pump restrictions in certain post codes due to network limitations or at least the process that's required. This may be more complex than we want to build but knowledge should be thorough and then we decide where the minimum viable SIM is and have road map options for more complexity as the supplier matches the evolution of services to match the world."

This is one of two packs. The cover steer is `DIRECTOR_STEER_FLEX_AND_NETWORK_KNOWLEDGE_IS_THOROUGH_AND_THE_SIM_IS_LAYERED_2026-10-25.md`.

## What to do with it

- Publish this pack as a Knowledge page. The page should be thorough, because it is knowledge and not a build commitment.
- The pack's "suggested layering" section is input to the roadmap options described in the cover steer.
- Every gap the pack names is either something for you to fetch or a design choice you make and state.

---

# Poesys Evidence Pack: Virtual Power Plants, Third-Party Flexibility and Local Network Flexibility for GB Households

**Scope:** This pack goes deeper than the earlier pack, which covered DFS outturns, Saving Sessions totals, Capacity Market clearing prices, P415 basics and SSES at headline level. Those figures are not repeated. Every figure has its source beside it. **[derived]** marks my own arithmetic. **[unverified]** marks something from memory that I could not confirm. Research date: 25 Oct 2026.

---

## 1. What a VPP is in GB practice

### 1.1 Who aggregates

There are three routes to market for a household's flexible devices.

**(a) The supplier aggregates its own customers.** Examples are Octopus/Kraken, OVO/Kaluza and EDF.
- The supplier optimises against wholesale and imbalance prices inside its own portfolio. It can also register Additional BM Units for its meters ([Elexon VLP role](https://www.elexon.co.uk/about/roles/virtual-lead-party/)).
- Kraken says it controls 160,000+ EVs under optimised charging. It also says it has "over 700 MW sold to network operators through the grid balancing mechanism", though it does not explain that figure further ([Kraken case study](https://www.kraken.tech/case-studies/octopus-energy-residential-flexibility)).

**(b) An independent aggregator registered as a Virtual Lead Party (VLP) or Virtual Trading Party (VTP).** Examples are Axle, Flexitricity and Voltalis.
- A VLP can register Secondary BM Units (SBMUs) for the Balancing Mechanism and TERRE. A VTP can also trade in the wholesale market under P415.
- Flexitricity became the first VLP in the BM in April 2020. It aggregated the first domestic EV unit in the BM in early 2021, with ev.energy ([EVIN](https://www.evinfrastructurenews.com/ev-technology/kaluza-and-flexitricity-to-utilise-evs-in-balancing-mechanism)).
- Axle reports 300,000+ connected devices and more than 2 GW of flexible capacity. It raised a $25m Series A in July 2026 ([UKTN](https://www.uktech.news/energy/virtual-power-plant-firm-axle-energy-raises-20m-20260708)).

**(c) A device or installer platform that partners with (a) or (b).** Examples are Tesla with Octopus, Sunsave, Ohme, Pod and Hypervolt with EDF.
- Tesla's UK VPP launched with Octopus as its retail partner ([SPP 2020](https://www.solarpowerportal.co.uk/energy-policy/highest-seg-tariff-launched-as-tesla-energy-plan-expanded-to-solar-and-powerwall-systems)).
- Sunsave runs its own VPP for its battery customers ([Sunsave](https://www.sunsave.energy/solar-panels-advice/sunsave-plus/vpp)).
- Moixa, the GridShare platform, was acquired by a Sunrun/SK venture, which became Lunar ([SPP](https://www.solarpowerportal.co.uk/energy-storage/moixa-acquired-by-us-residential-solar-leader-sunrun-s-new-smart-home-business-with-sk)).
- Social Energy won the first fully domestic FFR contract ([Current±](https://current-news.co.uk/social-energy-wins-first-ever-fully-domestic-ffr-contract)). I did not find current revenue figures.

### 1.2 Assets and baselines

The NGED register for 2025/26 shows how domestic flexibility actually looks ([NGED Market Insights Jun 2026](https://dso.nationalgrid.co.uk/downloads/15155/flexibility-market-insights-report-june-2026.pdf)):
- 309,180 of 309,514 registered assets are domestic.
- They provide 1,193 MW of 3,064 MW, or about 39% of capacity.
- That is about 3.9 kW per domestic asset **[derived]**.
- There are more than 10,000 heat pumps, about 500 storage heaters and more than 40,000 vulnerable households.
- EV charge points are the dominant asset type.

The year before (FY24/25) ([NGED Jun 2025](https://dso.nationalgrid.co.uk/downloads/15112/june-2025-market-insights-report.pdf)):
- Accepted trades were 80–88% EV charge points, 4–16% air-source heat pumps and 3–7% household demand.
- Delivery against instruction was 89.6% for EVs and 100% for household demand.

SSEN uses the ENA standard baselines: 1.67 kW per EV charger and 2 kW per heat pump ([SSEN 2025/26 report](https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/slc31e--ssen-2025-26-flexibility-services-procurement-report.pdf)).

**Baselining by market:**
- **BM (P376):** Elexon's Baselining Methodology Document, method BL01, version 3.0, effective 7 Nov 2024 ([Elexon](https://bscdocs.elexon.co.uk/category-3-documents/baselining-methodology-document)). It uses historical days plus an in-day adjustment. I could not read the lookback rule; my recollection is "10 of the last 10 like-days" **[unverified]**.
- **P375 asset metering:** Lets a meter behind the boundary point be used in settlement, through the new AMVLP and AMHHDC roles. Data has been submittable since 30 Jun 2022 ([SPP](https://www.solarpowerportal.co.uk/battery-storage/countdown-to-go-live-of-reforms-which-will-help-smaller-asset-owners-to-provide-balancing-services)).
- **DNO markets:** Standard baselines under the Market Facilitator are covered in §4.

### 1.3 How revenues stack

**Wholesale and time-of-use shifting is the largest domestic value pool.**
- Heat pumps: flexing is worth about **£84/yr** on a pass-through tariff and £82/yr on a tri-rate tariff, compared with not flexing on the same tariff ([Cornwall Insight for Nesta, Nov 2024](https://media.nesta.org.uk/documents/Cornwall_Insight_Domestic_heat_pump_flexibility_modelling_November_2024.pdf)).
- EVs: basic smart charging saves **£250–610 per EV per year** compared with a flat-price baseline, at 2022–24 average prices. Adding V2X and system services takes it to £1,020–1,410 ([Baringa/Eaton](https://www.baringa.com:443/globalassets/industries/energy-and-resources/low-carbon-solutions/the-value-of-electric-vehicle-charging-flexibility/baringa-eaton-the-value-of-electric-vehicle-charging-flexibility-executive-summary.pdf)).
- Intelligent Octopus Go cuts charging costs by **£343/yr**, according to Centre for Net Zero as quoted by Kraken ([Kraken](https://www.kraken.tech/case-studies/octopus-energy-residential-flexibility)).

**Balancing Mechanism.**
- Octopus's seven-month BM trial with EVs extrapolates to almost £100m/yr of system savings if 10m EVs took part ([Octopus](https://octopus.energy/press/more-news-press-releases/Octopus-leads-the-charge-National-Grid-welcomes-more-electric-cars-to-Balancing-Mechanism/)). That is about £10 per EV per year in system value **[derived]**, not household income.
- On 19 Mar 2026 NESO relaxed BM metering so that "standard domestic equipment" can take part through a supplier or a third-party aggregator ([NESO](https://www.neso.energy/millions-british-households-and-businesses-free-reap-rewards-flexing-energy-use)). The relaxed rules apply to units under 1 MW ([ESS News](https://www.ess-news.com/?p=8450)).
- A permanent derogation of 300 MW for aggregated assets continues. Further relaxation of telemetry and latency rules is planned by 2028 ([New Power](https://www.newpower.info/?p=14109)).
- No published figure gives realised BM £/household. This is a gap.

**Ancillary services.** NESO's onboarding page says ([NESO](https://www.neso.energy/industry-information/balancing-services/flex-onboarding)):
- DFS has "low entry requirements: ideal for domestic aggregators".
- Slow Reserve suits aggregated domestic loads.
- For Quick Reserve, "aggregators can bundle domestic assets".
- Dynamic Containment, Moderation and Regulation are the most demanding services. Aggregators "may help unlock" access for them.
- An SBMU must be at least 1 MW and sit within a single GSP Group ([Elexon](https://www.elexon.co.uk/about/roles/virtual-lead-party/)).

**Capacity Market and DFS.** Prices are in the earlier pack. NESO confirms aggregators can access the CM and combine it with DFS ([NESO](https://www.neso.energy/industry-information/balancing-services/flex-onboarding)). About 2 million households are signed up to DFS ([NESO, Mar 2026](https://www.neso.energy/millions-british-households-and-businesses-free-reap-rewards-flexing-energy-use)).

**DNO flexibility.** Covered in §3. Gross value per asset is in single-digit pounds per year at NGED **[derived, §3]**.

---

## 2. The over-the-top model (P415 and the VTP)

### 2.1 Mechanics

**Timeline.**
- Ofgem approved P415 on 6 Oct 2023. It went live on 7 Nov 2024 ([Elexon](https://www.elexon.co.uk/2024/11/07/elexon-implements-landmark-rule-change-to-drive-growth-in-flexibility-and-progress-to-net-zero/); [P510 form](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-proposal-form/)).
- VTP qualification began in Dec 2024 ([P510 form](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-proposal-form/)).

**Metering requirements.**
- An SBMU can contain only half-hourly SVA metering systems in one GSP Group, with no CVA meters.
- Each MSID pair needs an import MPAN. An export MPAN is optional ([Elexon VLP](https://www.elexon.co.uk/about/roles/virtual-lead-party/)).
- So MHHS migration is a real gating factor. More than 12 million meters (about 36%) had migrated by June 2026 ([Elexon annual report](https://www.elexon.co.uk/2026/06/30/elexon-publishes-bsc-annual-report-2025-2026/)).

**Data flows.**
- The VLP allocates MSID pairs using flow P0278.
- After delivery it submits Delivered Volumes per MSID pair per settlement period using flow P0282.
- The SVAA uses HHDA meter data to allocate those volumes to individual MSIDs.
- The VLP is exposed to the imbalance price on volume it fails to deliver. Over-delivery carries no trading charge.
- If two VLPs claim the same MSID, the newer SBMU takes ownership of it ([Elexon VLP](https://www.elexon.co.uk/about/roles/virtual-lead-party/)).

**Supplier compensation.**
- Suppliers are compensated only for Deviation Volumes attributed to VTPs. The cost is mutualised across all suppliers by market share ([P510 form](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-proposal-form/); [Drax](https://energy.drax.com/intelligence/vtp-activity-builds-through-winter/)).
- A deviation volume is the gap between baseline and actual consumption during a VTP action ([Drax](https://energy.drax.com/intelligence/vtp-activity-builds-through-winter/)).
- The price comes from the Supplier Compensation Reference Price Methodology, version 2.0, effective 6 Nov 2025 ([Elexon](https://bscdocs.elexon.co.uk/category-3-documents/supplier-compensation-reference-price-methodology-document)). I could not read how that price is set, so the price-setting method is a gap.
- In the BM, direct supplier compensation under P444 has been live since Nov 2025 ([P510 form](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-proposal-form/)).

### 2.2 How many VLPs and VTPs

- Nov 2024: 22 VLPs registered, and 7 companies interested in becoming VTPs ([Elexon](https://www.elexon.co.uk/2024/11/07/elexon-implements-landmark-rule-change-to-drive-growth-in-flexibility-and-progress-to-net-zero/)).
- 2025/26: 11 VTPs, out of 97 companies Elexon helped register for new roles ([Elexon annual report](https://www.elexon.co.uk/2026/06/30/elexon-publishes-bsc-annual-report-2025-2026/)).
- "Over a dozen" VTPs had qualified by March 2026 ([P510 form](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-proposal-form/)).
- **Actually active:** 8 parties show SBMU compensation volumes from Sep 2025 to Feb 2026. They are Almape Holdings, Axle, EDF, Zenobe Rental 1, Flexitricity, Flexivolt, Capture Energy and Voltalis ([P510 IWA slides](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-panel-slides/)).

### 2.3 Volumes and money (Sep 2025 – Feb 2026)

All figures from the [P510 IWA](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-panel-slides/):

| Month | Compensation (£) | SBMU compensation volume (MWh) |
|---|---|---|
| Sep 25 | 668,086 | 7,376 |
| Oct 25 | 1,239,855 | 13,859 |
| Nov 25 | 2,195,129 | 23,719 |
| Dec 25 | 3,734,111 | 38,193 |
| Jan 26 | 5,485,199 | 62,497 |
| Feb 26 | 5,576,308 | 63,827 |
| **Total** | **18,898,688** | **209,471** |

**What the figures show:**
- The implied average is about **£90/MWh** **[derived]**: £18.9m divided by 209,471 MWh. The two series come from different Elexon reports (MR1A and SAA-I014), so treat this as indicative.
- Volume was concentrated: Almape 77.9%, Axle 19.0%, EDF 2.9% ([IWA](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-panel-slides/)).
- So were receipts. SEFE received about 76% (£14.3m), Octopus 13% (£2.5m) and E.ON Next 5% ([IWA](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-panel-slides/)).
- The cost to customers rose from under £0.10/MWh for most of 2025 to about £0.24/MWh in Feb 2026. Drax thinks it could reach about £0.50/MWh ([Drax](https://energy.drax.com/intelligence/vtp-activity-builds-through-winter/)).
- The proposer of P510 projects more than £60m/yr if volumes continue ([Ofgem P510 urgency](https://www.ofgem.gov.uk/sites/default/files/2026-04/P510-Balancing-and-Settlement-Code-BSC-urgency-decision.pdf)).

### 2.4 Rule changes now under way

**P511 (Axle): limits on generator participation.** Approved 10 Aug 2026 and implemented 24 Aug 2026 ([Ofgem P511](https://www.ofgem.gov.uk/sites/default/files/2026-08/P511-Balancing-and-Settlement-Code-BSC-changes.pdf)). Eligibility is based on the peak half-hourly export of an MSID pair over the past 365 days:
- Under 2 MW: eligible.
- Over 10 MW: ineligible.
- 2–10 MW: a 30-day net-export behavioural test applies.

The proposer estimated it avoids £35m–£500m of cost over 12 months, which is £1.10–£17.10 per bill. The concentration figures above suggest that much of the early VTP volume came from generators, not households **[derived inference]**.

**P510 (Flexitricity): direct, two-way compensation.** VTPs would pay suppliers for demand turn-down, and suppliers would pay VTPs for demand turn-up. It is on a non-urgent path, with the earliest release in Nov 2026 or Feb 2027 ([P510 form](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-proposal-form/); [Ofgem](https://www.ofgem.gov.uk/sites/default/files/2026-04/P510-Balancing-and-Settlement-Code-BSC-urgency-decision.pdf)).

**P509 (Voltalis): benefit assessments of DSR.** Non-urgent ([Ofgem](https://www.ofgem.gov.uk/sites/default/files/2026-04/P510-Balancing-and-Settlement-Code-BSC-urgency-decision.pdf)).

### 2.5 One supplier, a different flexibility provider

- A household keeps its supplier and contracts separately with an aggregator. NESO says explicitly: if your supplier is not in the BM, "look for an aggregator that does and keep their current supplier" ([NESO](https://www.neso.energy/millions-british-households-and-businesses-free-reap-rewards-flexing-energy-use)).
- The household gets its reward from the aggregator. Examples are Axle's £1/kWh plus £10/month minimum, or Sunsave's £15/month ([Sunsave explainer](https://www.sunsave.energy/solar-panels-advice/exporting-to-the-grid/virtual-power-plants)).
- From 2027–28 the aggregator will need a load-control licence (§5).

**What this means for Poesys's margin and hedging:**
1. The supplier hedges against a forecast. A VTP turn-down at its customer's meter leaves it long, and the spill is valued at the imbalance price ([Drax](https://energy.drax.com/intelligence/vtp-activity-builds-through-winter/)).
2. Today the supplier is made whole at the reference price from a pot, and also pays into that pot in proportion to its market share. So a supplier with few VTP customers pays a net levy (a third-party-cost line item).
3. If P510 passes, the cost becomes bilateral and depends on the direction of the action. Turn-up actions would flow money from supplier to VTP.
4. In the BM, P444 already compensates directly.
5. Because the MSID goes to the newer SBMU, a rival can take over a customer's flexibility without the supplier's consent **[derived from the Elexon rule]**.

---

## 3. Local network flexibility (DNOs)

### 3.1 Products, payments and settlement

**Old and new product names.**
- The GB standard products are Peak Reduction (PR), Scheduled Utilisation (SU), Scheduled Availability + Operational Utilisation (SAOU), Variable Availability + Operational Utilisation (VAOU) and Operational Utilisation (OU) ([ENWL guide](https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/document-library/helpful-guides/flexible-services-products-and-parameters-2024.pdf)).
- UKPN says these "replace the previous Sustain, Secure and Dynamic products" ([UKPN DSO](https://dso.ukpowernetworks.co.uk/flexibility)).
- The likely mapping is Sustain → SU/PR, Secure → SAOU, Dynamic → VAOU and Restore → OU **[unverified mapping]**.

**Product parameters** ([ENWL guide](https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/document-library/helpful-guides/flexible-services-products-and-parameters-2024.pdf)):
- Minimum unit: 10 kW, aggregated within a zone.
- Response time: up to 15 minutes for OU and VAOU.
- Minimum utilisation: 30 minutes.
- Pricing: availability in £/MW/h, utilisation in £/MWh. PR and OU are paid for utilisation only.

**Legacy payment rules** ([SSEN Flexible Power](https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/service-documentation/ssen-flexible-power---payment-calculations.pdf)):
- Availability is paid only for Secure and Dynamic, per 30-minute period.
- Utilisation is calculated per minute.

**Standard settlement under the Market Facilitator** (FMR-VSM, effective 30 Jan 2026) ([Elexon](https://www.elexon.co.uk/elexondocuments/about/consultations/2025-consultations/mf/fmr-vsm-verification-settlement-methodology/)):
- Utilisation is settled per minute.
- Availability is reduced by a Monthly Utilisation Performance Factor.
- Grace bands are 5% (10% for OU). The performance multiplier is 3 (2 for OU). With a 5% grace band and a multiplier of 3, payment reaches zero at 63% delivery.
- Over-delivery is not paid.

**Contracts.**
- UKPN contracts last up to 2.5 years ([UKPN](https://dso.ukpowernetworks.co.uk/flexibility)).
- ENWL contracts run Oct 2025 – Mar 2028 ([ENWL 2026](https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/document-library/ofgem-dfp-reporting/distribution-flexibility-services-procurement-report-2026.pdf)).
- SSEN's overarching agreement runs 8 years ([SSEN](https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/slc31e--ssen-2025-26-flexibility-services-procurement-report.pdf)).
- SPEN uses the V3 standard flexibility agreement ([SPEN prospectus](https://www.spenergynetworks.co.uk/userfiles/file/SPEN_Market_Prospectus_2025-26.pdf)).

### 3.2 Where the constraints are

- **UKPN:** publishes a postcode-to-flexibility-zone dataset in JSON, CSV and shapefile formats. It approximates eligibility; final checks are done per MPAN ([Open Net Zero](https://opennetzero.org/uk-power-networks/flexibility-tender-data-by-postcode)).
- **NGED:** publishes a flexibility requirements dataset with all zones ([NGED connected data](https://connecteddata.westernpower.co.uk/dataset/flexibility-requirements/resource/c70e485e-7715-4e98-87d8-46fdd1684a21)) and flexibility forecasts ([NGED](https://connecteddata.nationalgrid.co.uk/dataset/flexibility-forecasts)). Historic CMZ tranches are on Open Net Zero ([CMZ 6a](https://opennetzero.org/dataset/constraint-management-zone-cmz-6a)).
- **NESO and Piclo:** the Local Constraint Market covers only the England–Scotland border area ([NESO](https://www.neso.energy/industry-information/balancing-services/flex-onboarding)). It has been extended to Jan 2027 ([Piclo](https://www.piclo.com/press-releases/piclo-and-neso-extend-the-local-constraint-market-to-january-2027)).

### 3.3 Results by DNO

**NGED, FY25/26** ([Jun 2026](https://dso.nationalgrid.co.uk/downloads/15155/flexibility-market-insights-report-june-2026.pdf)):
- Volumes: 198 GWh procured, 6.5 GWh dispatched across 110,056 dispatch events.
- Market: 1,239 zones; 43 active FSPs (38 onboarded via Piclo).
- Money: £2.4m utilisation revenue and £756k committed availability spend.
- The average utilisation price works out at about **£369/MWh** **[derived]**: £2.4m divided by 6.5 GWh.
- If all utilisation revenue went to domestic assets, it would be about **£7.8 per asset per year gross** before the aggregator's share **[derived, upper bound]**.
- The 2025 long-term round awarded 196 GWh, of which FlexUp (turn-up) was 52 GWh across 23 zones ([SPP](https://www.solarpowerportal.co.uk/energy-policy/national-grid-dso-procures-196gwh-of-flexibility-largest-ever-annual-tender)).

**NGED, FY24/25** ([Jun 2025](https://dso.nationalgrid.co.uk/downloads/15112/june-2025-market-insights-report.pdf)):
- SAOU availability averaged **£18.54/MW/h**, with utilisation at £1,113/MW/h. Short-term SU utilisation averaged **£3,584/MW/h**.
- The worked example: 1 kW turned down for 4 hours earns £14.34.
- Long-term awards cleared 34% below ceiling (HV) and 18% below (LV).
- Volumes: 2.9 GWh dispatched over 70,000 events.

**UKPN** (all from UKPN DSO and news pages):
- Prices: historically up to £600/MWh, varying by location ([UKPN](https://dso.ukpowernetworks.co.uk/flexibility)).
- Day-ahead market: 4.4 GWh in its first year from Apr 2024, more than 150 competitions, more than 40 zones, more than 90,000 assets. It runs on EPEX Localflex and allows stacking without exclusivity ([UKPN](https://www.ukpowernetworks.co.uk/news/uk-power-networks-dso-boosts-local-and-national-flexibility-coordination-through-day-ahead-market); [pv-mag](http://www.pv-magazine.com/2025/04/23/ai-helps-uk-dso-deliver-4-4-gwh-of-day-ahead-flexibility-in-one-year/)).
- Early-2024 tender: 327 MW from 127 sites, with 17 providers ([UKPN](https://www.ukpowernetworks.co.uk/news/uk-power-networks-dso-broadens-flexibility-market-with-contract-announcement)).
- Oct 2025 tender: 20 MW across 217 zones from 9 providers, all low-carbon. More than 9,000 assets; EV chargers were 63% of capacity; Axle was named ([UKPN](https://www.ukpowernetworks.co.uk/news/customers-drive-first-100-low-carbon-flexibility-tender-with-uk-power-networks)).

**SSEN, 2025/26** ([report](https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/slc31e--ssen-2025-26-flexibility-services-procurement-report.pdf)):
- 66.1 MW contracted, against 241.9 MW of need that was not met.
- 1,334.5 MWh dispatched, of which demand was 722.8 MWh.
- 192 long-term zones.
- Minimum bid cut to 10 kW, and to 2.5 kW for SU at HV/LV.
- A **£120 flat payment per participating household** in Load Managed Areas, with three suppliers taking part.

**SP ENW, 2025/26** ([report](https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/document-library/ofgem-dfp-reporting/distribution-flexibility-services-procurement-report-2026.pdf)):
- 826 MW tendered in spring and 1,588 MW in autumn, but only 8.06 MW contracted.
- 8,786 MWh dispatched, mostly Peak Reduction, up from 4,349 MWh.
- 46 contracted bids.

**SPEN** ([prospectus](https://www.spenergynetworks.co.uk/userfiles/file/SPEN_Market_Prospectus_2025-26.pdf)):
- 2024/25: 146 MW tendered, 385 MWh dispatched, £3.9m of reinforcement savings.
- EV registrations rose from 971 to 27,000.
- 2025/26 need: 101 MW (SP Distribution) and 142 MW (SP Manweb), each across 26 locations.

**Northern Powergrid:** I could not retrieve its 2025/26 figures (gap). It does host Octopus Power-ups (§5).

**What the pattern says.** Tendered volume far exceeds what is contracted, which in turn far exceeds what is dispatched. Domestic assets make up nearly all assets by count but under 40% of capacity, and dispatch is sparse. For a household, DNO flexibility is a **small, location-gated, occasional** stream. The exception is short-notice LV events, where per-kW prices are high.

---

## 4. The Market Facilitator (Elexon), 2025–2028

**Status.** Elexon was appointed in Jul 2024 ([SPP](https://www.solarpowerportal.co.uk/battery-storage/ofgem-appoints-elexon-as-market-facilitator-for-local-energy)) and started operating on 12 Dec 2025 under Ofgem's direction ([Elexon](https://www.elexon.co.uk/flexibility-markets/2025/12/12/elexon-starts-operations-in-new-market-facilitator-role-to-transform-flexibility-markets/); [Ofgem decision](https://www.ofgem.gov.uk/sites/default/files/2025-12/Market_Facilitator_Blueprint_decision.pdf)).
- New licence conditions oblige DNOs and NESO to comply with the Flexibility Market Rules.
- Ofgem's impact assessment puts the net benefit at £65m–£442m ([Ofgem](https://www.ofgem.gov.uk/sites/default/files/2025-12/Market_Facilitator_Blueprint_decision.pdf)).

**What changes for domestic flexibility:**

| When | Change | Source |
|---|---|---|
| Dec 2025 | 10 Flexibility Market Rules in force; delivery plan runs Jan 2026 – Mar 2028 | [Elexon](https://www.elexon.co.uk/flexibility-markets/2025/12/12/elexon-starts-operations-in-new-market-facilitator-role-to-transform-flexibility-markets/) |
| 30 Jan 2026 | Common verification and settlement method (per-minute utilisation, performance multiplier) | [FMR-VSM](https://www.elexon.co.uk/elexondocuments/about/consultations/2025-consultations/mf/fmr-vsm-verification-settlement-methodology/) |
| Mar 2026 | Flexibility Market Catalogue launched | [Elexon AR](https://www.elexon.co.uk/2026/06/30/elexon-publishes-bsc-annual-report-2025-2026/) |
| 1 Apr 2026 (SSEN 1 Jul 2026) | Standard baselines (see below) | [FMR-SBM](https://www.elexon.co.uk/elexondocuments/about/consultations/2025-consultations/mf/fmr-sbm-standardised-baselining-methodologies/) |
| End 2026 | Better market and product definitions; Market Data Portal for DNO procurement and dispatch data | [Elexon](https://www.elexon.co.uk/flexibility-markets/2025/12/12/elexon-starts-operations-in-new-market-facilitator-role-to-transform-flexibility-markets/) |
| Early 2027 | Common dispatch API across DNOs, later extended to NESO; consistent reallocation of assets between FSPs | [Elexon](https://www.elexon.co.uk/flexibility-markets/2025/12/12/elexon-starts-operations-in-new-market-facilitator-role-to-transform-flexibility-markets/) |
| 30 Sep 2027 | FMAR Phase 1: single registry for EVs, heat pumps and batteries (moved from 1 Jul 2027) | [Ofgem](https://www.ofgem.gov.uk/sites/default/files/2025-12/Market_Facilitator_Blueprint_decision.pdf) |
| Undated | "Risk of Conflict" reporting, capacity release, stacking roadmap; alignment of performance management deprioritised | [Plan at a glance](https://www.elexon.co.uk/flexibility-markets/documents/about/delivery-plan/market-facilitator-delivery-plan-at-a-glance/) |

**Standard baselines (from 1 Apr 2026).**
- Five methods exist: Asset Capacity, Fixed Reference, Nomination, Recent History and Zero.
- Domestic heat pumps and EV chargers default to **Fixed Reference** values set by DNOs.
- Accuracy tests on nominations apply mainly to I&C sites: 10% net error and 20% absolute error.
- Several devices at one property can be grouped into one Meterable Unit ([FMR-SBM](https://www.elexon.co.uk/elexondocuments/about/consultations/2025-consultations/mf/fmr-sbm-standardised-baselining-methodologies/)).

---

## 5. The customer side

**What households are paid:**

| Provider or scheme | Payment | Source |
|---|---|---|
| Axle (from Nov 2024) | £1/kWh during stress events, with a guaranteed minimum of £10/month | [Sunsave explainer](https://www.sunsave.energy/solar-panels-advice/exporting-to-the-grid/virtual-power-plants) |
| Sunsave VPP | £15/month guaranteed for 12–18 months; average payout about £25/month (Sep 2026) | [Sunsave explainer](https://www.sunsave.energy/solar-panels-advice/exporting-to-the-grid/virtual-power-plants) |
| OVO Power Move Flex (EV) | £6–8/month on average "just for staying plugged in"; groups are randomised | [OVO](https://www.ovoenergy.com/power-move-flex-for-charge-anytime) |
| SSEN Load Managed Area | £120 flat per household | [SSEN](https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/slc31e--ssen-2025-26-flexibility-services-procurement-report.pdf) |
| Octopus Power-ups (UKPN and NPg turn-up events) | Free electricity in DNO-called windows, notified day-ahead | [Octopus](https://octopus.energy/press/free-whizz-octopus-launches-power-ups-free-energy-when-the-sun-shines-and-the-wind-blows/) |
| NGED short-term LV event | £14.34 per kW for a 4-hour turn-down, paid to the FSP. That is about £24 per EV at the 1.67 kW baseline **[derived]**, before the aggregator's share | [NGED](https://dso.nationalgrid.co.uk/downloads/15112/june-2025-market-insights-report.pdf) |

That gives about £72–300/yr per household from VPP payments **[derived]**: £6–25/month × 12.

**Opt-in rates and fatigue:**
- **Octopus Power-ups in the NPg area (29 Jan – 31 Mar 2025):**
  - 14,477 MPANs signed up across Spennymoor and Ferrybridge B.
  - About 24 events were planned, each lasting 1–4 hours.
  - Only a minority of signed-up customers were invited to each event: 2,400 of 9,000, and 1,857 of 5,477. This was done as a randomised crossover trial ([AEA registry](https://www.socialscienceregistry.org/trials/15455)).
  - Results are not public (gap).
- **CrowdFlex:**
  - 107,000 OVO customers took part in utilisation trials, and 33,000 OVO and Ohme customers in availability trials ([NESO Feb 2026](https://www.neso.energy/news/crowdflex-innovation-project-announces-final-domestic-flexibility-trial-results-whole-project-trials-analysis-and-model-development-success)).
  - Turn-up events drew more than twice the response of turn-down events.
  - 12% of repeat participants reported waning interest. Customers who formed a habit were 8% less likely to disengage.
  - Automation shifted about 30% more energy.
  - Lower incentives were more cost-efficient per kWh, with diminishing returns at higher incentives ([NESO Jul 2025](https://neso.energy/news/crowdflex-publishes-latest-results-and-insights-large-scale-domestic-flexibility-trials)).
  - Escalating availability payments beat flat payments ([NESO Feb 2026](https://www.neso.energy/news/crowdflex-innovation-project-announces-final-domestic-flexibility-trial-results-whole-project-trials-analysis-and-model-development-success)).
  - Habit formation rose from 22% to 39% of respondents.

**Consumer protection (load-control licensing, deeper than the SSES headline):**
- **Timeline:** Ofgem's implementation decision (7 Aug 2026) sets the application window to open on 1 Mar 2027, followed by a 12-month transition. Applications must be made within 3 months to be sure of continuity. The legal-force date is given inconsistently in the document, as "late 2027" and as March 2028 ([Ofgem](https://www.ofgem.gov.uk/sites/default/files/2026-08/SSES-Implementation-Decision.pdf)).
- **Tiers:** Load controllers are split at 300 MW. At or above 300 MW they are expected to be designated Operators of Essential Services under NIS.
- **Fees:** £1,650 for FSP plus load-controller activities.
- **Obligations:** FSPs must join the Energy Ombudsman scheme. Suppliers can be derogated from some conditions only when they are the same legal entity as the FSP ([Ofgem](https://www.ofgem.gov.uk/sites/default/files/2026-08/SSES-Implementation-Decision.pdf)).
- **Draft guidance** ([Ofgem Annex D](https://www.ofgem.gov.uk/sites/default/files/2025-12/Annex-D-Draft-load-control-consumer-protection-guidance.pdf)):
  - Explicit consent is required.
  - Customers should be able to override control.
  - Rewards must not be overstated.
  - Customers must be warned against signing up with several FSPs for the same service.
  - Exit fees must not exceed the provider's direct economic loss.
  - Vulnerable customers must be identified.

---

## (a) Value streams table

| Stream | Who can access | Domestic eligibility | Band | Source |
|---|---|---|---|---|
| Time-of-use / wholesale shifting (supplier) | Supplier | Yes: EV, heat pump, battery | Heat pump about £84/hh/yr; EV £250–610/EV/yr (2022 prices); IOG £343/yr | [Cornwall](https://media.nesta.org.uk/documents/Cornwall_Insight_Domestic_heat_pump_flexibility_modelling_November_2024.pdf), [Baringa](https://www.baringa.com:443/globalassets/industries/energy-and-resources/low-carbon-solutions/the-value-of-electric-vehicle-charging-flexibility/baringa-eaton-the-value-of-electric-vehicle-charging-flexibility-executive-summary.pdf), [Kraken](https://www.kraken.tech/case-studies/octopus-energy-residential-flexibility) |
| Wholesale via VTP (P415) | VTP plus a compensated supplier | Yes, with HH-settled MSIDs (P511 caps generators) | Supplier compensation about £90/MWh **[derived]**; no £/household published | [P510 IWA](https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-panel-slides/) |
| Balancing Mechanism | Supplier (Additional BMU) or VLP (SBMU of at least 1 MW) | Yes; relaxed metering from Mar 2026 for units under 1 MW | System value about £10/EV/yr **[derived]**; no realised household figure | [Octopus](https://octopus.energy/press/more-news-press-releases/Octopus-leads-the-charge-National-Grid-welcomes-more-electric-cars-to-Balancing-Mechanism/), [NESO](https://www.neso.energy/millions-british-households-and-businesses-free-reap-rewards-flexing-energy-use) |
| Quick or Slow Reserve | Aggregator | Aggregated domestic portfolios | Not published | [NESO](https://www.neso.energy/industry-information/balancing-services/flex-onboarding) |
| Dynamic Containment / Moderation / Regulation | Aggregator | Batteries only in practice | Not published for domestic | [NESO](https://www.neso.energy/industry-information/balancing-services/flex-onboarding) |
| DFS / CM | Supplier or aggregator | Yes | See earlier pack | — |
| DNO long-term (SAOU) | FSP, at least 10 kW per zone | Yes, if inside a zone | £18.54/MW/h availability (NGED FY24/25) | [NGED](https://dso.nationalgrid.co.uk/downloads/15112/june-2025-market-insights-report.pdf) |
| DNO short-term / day-ahead | FSP | Yes, if inside a zone | £369/MWh average (NGED FY25/26) **[derived]**; up to £600/MWh (UKPN); about £7.8/asset/yr gross at NGED **[derived]** | [NGED](https://dso.nationalgrid.co.uk/downloads/15155/flexibility-market-insights-report-june-2026.pdf), [UKPN](https://dso.ukpowernetworks.co.uk/flexibility) |
| DNO household schemes | Supplier | Yes | £120/hh flat (SSEN LMA); free kWh (Power-ups) | [SSEN](https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/slc31e--ssen-2025-26-flexibility-services-procurement-report.pdf) |
| Household VPP payout (all streams combined) | Paid to the customer | — | £6–25/month, about £72–300/yr **[derived]** | [OVO](https://www.ovoenergy.com/power-move-flex-for-charge-anytime), [Sunsave](https://www.sunsave.energy/solar-panels-advice/exporting-to-the-grid/virtual-power-plants) |

## (b) What the simulated world would need, layer by layer

1. **Assets:** a device inventory per household (EV, heat pump, battery, PV). Each device needs a kW rating, a plug-in or availability profile, and an ENA baseline (1.67 kW for EVs, 2 kW for heat pumps). Some homes need an HH-settled flag; MHHS is about 36% complete.
2. **Wholesale and time-of-use:** half-hourly prices and spreads; the supplier's hedge book; imbalance prices.
3. **Third-party rivals:** VTP and VLP agents that recruit Poesys customers. They need a takeover rule (the newest SBMU wins the MSID); deviation volumes at a reference price; a mutualisation levy by market share; a P510 switch for bilateral compensation; and a P511 generator cap.
4. **BM:** an SBMU minimum of 1 MW per GSP Group; the 300 MW derogation; a BL01 baseline; acceptances and their prices.
5. **DNO layer:** a zone map keyed by postcode and primary substation, with a seasonal MW requirement for each zone. Products (PR, SU, SAOU, VAOU, OU) with availability and utilisation prices. The tendered-to-contracted-to-dispatched funnel. Event calls and notice periods. The performance multiplier (zero at 63% delivery).
6. **Customers:** opt-in rates and the incentive response curve; turn-up responding at more than twice turn-down; 12% fatigue among repeat participants; the effect of habit; automation adding 30%; override events; vulnerable households.
7. **Regulation:** load-control licence dates and tiers; FMAR registration from Sep 2027; the common dispatch API from 2027.

## (c) Suggested layering: minimum viable to richer

- **L0, minimum viable:** the supplier runs smart time-of-use for EVs and heat pumps against half-hourly wholesale prices. Value comes from shifting only, using the Cornwall Insight and Baringa bands. No third parties.
- **L1:** add DFS and CM as event and annual streams (from the earlier pack), plus customer opt-in and fatigue.
- **L2:** add the DNO layer. A synthetic zone map covering about 10–20% of customers, seasonal event calls, NGED-style prices and the performance multiplier.
- **L3:** add rival VTP and VLP agents. Customer churn of flexibility only, deviation and compensation cash flows, the mutualisation levy, and P510 and P511 as switchable rules.
- **L4:** add BM participation through an Additional BMU or VLP, with relaxed metering, baselines and SBMU aggregation per GSP Group.
- **L5:** add the 2027 standardisation (FMAR registry, common dispatch, reallocation of assets), load-control licensing costs and conflicts from stacking revenues.

## (d) Named gaps

1. How the Supplier Compensation Reference Price is set, and its current value. The document would not render.
2. Realised household £/yr from the BM and from Quick or Slow Reserve. Nothing is published.
3. UKPN and NPg 2025/26 SLC31E figures. The Ofgem ZIP download was blocked; the datasets are linked from [Ofgem](https://www.ofgem.gov.uk/data/electricity-distribution-standard-licence-condition-31e-flexibility-procurement-reports-and-supporting-data-2025-2026).
4. Piclo marketplace statistics (registered GW, competitions by DNO). Not retrieved.
5. Current UK figures for Tesla, GivEnergy, Social Energy and Lunar VPPs.
6. Power-ups and CrowdFlex £/kWh incentive levels and measured kW per household.
7. The mapping from Sustain/Secure/Dynamic/Restore to the new product names. **[unverified]**
8. The lookback rule in BL01. **[unverified]**
9. A Cornwall Insight or LCP study that stacks all revenue streams for domestic flexibility. Not found; only heat-pump time-of-use modelling.
10. Domestic participation in Capacity Market units. Not found.