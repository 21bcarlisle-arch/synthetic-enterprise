# VPPs, third-party flexibility and local network payments for GB households

**Knowledge:** vpps-and-local-flexibility

Written 2026-10-25 from the advisor's cited evidence pack
`docs/staging/advisor/done/DIRECTOR_EVIDENCE_VPPS_THIRD_PARTY_FLEX_AND_LOCAL_NETWORK_PAYMENTS_2026-10-25.md`,
under the director's steer that flexibility and network knowledge is thorough and the simulation is
layered (25 Oct, 06:44: "knowledge should be thorough and then we decide where the minimum viable SIM
is"). This is knowledge, not a build commitment. Figures marked **[derived]** are the pack author's
arithmetic on cited numbers; **[unverified]** items are not claims until sourced. The per-item check
against primary sources made while drafting is in section 9.

The earlier flexibility figures (DFS outturns, Saving Sessions, Capacity Market prices) sit on the
household-flexibility page (`household-flexibility-and-the-advice-roadmap`) and in
`neso_dfs_called_day_response_2026-09-07.md`; they are not repeated here.

## 0. What this project does today (read from code, not run)

- **The world dispatches flexibility on true system stress, with a trivial baseline.**
  `sim/flex_dispatch.py:1-13` dispatches enrolled flex in the tightest-residual periods at the
  observed price; at its first level delivery is perfect and the baseline is the enrolled volume
  (`sim/flex_dispatch.py:289`). Only the dispatch instruction and the settlement line cross the wall
  (`company/interfaces/sim_interface.py:293`). The belief-against-truth gap is scored by
  `background/flex_dispatch_triad.py`.
- **The company's domestic flex book is DFS-only from 2022 and refuses the Capacity Market leg.**
  `company/market/flexibility_revenue_book.py:97-111`; the CM leg returns `None` with a reason
  (`company/market/flexibility_potential.py:147`).
- **Flex kW per asset is the rated power, not the ENA standard baseline.**
  `company/market/flexibility_potential.py:45-47` carries 7.4 kW per EV charger, 3.0 kW per heat
  pump and 5.0 kW per battery. The DNO standard baselines are 1.67 kW per EV charger and 2 kW per heat
  pump (SSEN 2025/26, below). The DFS revenue is anchored on published per-participant payouts, so
  the rated figure does not reach a pound there; it would if DNO flexibility were added.
- **No rival aggregator exists.** Nothing in `company/`, `simulation/` or `sim/` models a VTP or VLP,
  P415 deviation volumes, supplier compensation or the mutualisation levy.
- **The DNO tender register is uncalled.** `company/market/dso_flexibility_tender_register.py` has no
  caller in the run.

## 1. Who aggregates a household's devices

Three routes to market:

1. **The supplier aggregates its own customers** (Octopus/Kraken, OVO/Kaluza, EDF). It optimises
   against wholesale and imbalance prices inside its own portfolio and can register Additional BM
   Units (https://www.elexon.co.uk/about/roles/virtual-lead-party/). Kraken reports 160,000+ EVs under
   optimised charging (https://www.kraken.tech/case-studies/octopus-energy-residential-flexibility).
2. **An independent aggregator as Virtual Lead Party (VLP) or Virtual Trading Party (VTP)** (Axle,
   Flexitricity, Voltalis). A VLP registers Secondary BM Units for the BM; a VTP can also trade in
   the wholesale market under P415. Axle reports 300,000+ connected devices and over 2 GW
   (https://www.uktech.news/energy/virtual-power-plant-firm-axle-energy-raises-20m-20260708).
3. **A device or installer platform partnering with 1 or 2** (Tesla with Octopus; Sunsave; Ohme,
   Pod and Hypervolt with EDF).

**NGED's register, 2025/26** (https://dso.nationalgrid.co.uk/downloads/15155/flexibility-market-insights-report-june-2026.pdf,
fetched 2026-10-25): 309,180 of 309,514 registered assets are domestic, providing 1,193 MW of
3,064 MW (about 39%; about 3.9 kW per domestic asset **[derived]**). EV charge points dominate.

**Standard DNO baselines:** 1.67 kW per EV charger and 2 kW per heat pump (SSEN 2025/26 SLC31E report,
https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/slc31e--ssen-2025-26-flexibility-services-procurement-report.pdf).

**BM baselining (P376):** Elexon's Baselining Methodology Document, method BL01, version 3.0,
effective 7 Nov 2024 (confirmed on https://bscdocs.elexon.co.uk/category-3-documents/baselining-methodology-document,
2026-10-25). The lookback rule was not readable (section 9).

## 2. How the revenue stacks

| Stream | Who can access | Domestic? | Band | Source |
|---|---|---|---|---|
| Time-of-use / wholesale shifting | Supplier | EV, heat pump, battery | Heat pump ~£84/yr; EV £250–610/yr (2022–24 prices); IOG £343/yr charging saving | Cornwall Insight for Nesta (Nov 2024); Baringa/Eaton; Kraken |
| Wholesale via VTP (P415) | VTP, supplier compensated | HH-settled MSIDs | Compensation ~£90/MWh **[derived]**; no £/household published | Elexon P510 IWA |
| Balancing Mechanism | Supplier (AMBU) or VLP (SBMU ≥1 MW) | Relaxed metering from Mar 2026 | ~£10/EV/yr system value **[derived]**; no household figure | Octopus; NESO |
| Quick/Slow Reserve | Aggregator | Aggregated portfolios | Not published | NESO flex onboarding |
| DC/DM/DR | Aggregator | Batteries in practice | Not published | NESO |
| DNO long-term (SAOU) | FSP, ≥10 kW per zone | In a zone | £18.54/MW/h availability (NGED FY24/25) | NGED Jun 2025 |
| DNO short-term / day-ahead | FSP | In a zone | ~£369/MWh (NGED FY25/26) **[derived]**; up to £600/MWh (UKPN); ~£7.8/asset/yr gross at NGED **[derived, upper bound]** | NGED; UKPN |
| DNO household schemes | Supplier | Yes | £120/household flat (SSEN Load Managed Area); free kWh (Octopus Power-ups) | SSEN; Octopus |
| Household VPP payout | Paid to customer | — | £6–25/month, ~£72–300/yr **[derived]** | OVO; Sunsave |

Sources: https://media.nesta.org.uk/documents/Cornwall_Insight_Domestic_heat_pump_flexibility_modelling_November_2024.pdf ·
https://www.baringa.com:443/globalassets/industries/energy-and-resources/low-carbon-solutions/the-value-of-electric-vehicle-charging-flexibility/baringa-eaton-the-value-of-electric-vehicle-charging-flexibility-executive-summary.pdf ·
https://www.neso.energy/industry-information/balancing-services/flex-onboarding ·
https://www.neso.energy/millions-british-households-and-businesses-free-reap-rewards-flexing-energy-use

NESO relaxed BM metering on 19 Mar 2026 so standard domestic equipment can take part through a
supplier or aggregator, for units under 1 MW; a 300 MW derogation for aggregated assets continues.
About 2 million households are signed up to DFS (NESO, Mar 2026).

## 3. The over-the-top model: P415 and the VTP

- P415 approved 6 Oct 2023, live 7 Nov 2024; VTP qualification from Dec 2024
  (https://www.elexon.co.uk/2024/11/07/elexon-implements-landmark-rule-change-to-drive-growth-in-flexibility-and-progress-to-net-zero/).
- An SBMU holds only half-hourly SVA metering systems in one GSP Group; each MSID pair needs an
  import MPAN. So market-wide half-hourly settlement gates participation: more than 12 million meters
  (about 36%) had migrated by June 2026 (Elexon annual report 2025/26).
- Flows: P0278 allocates MSID pairs; P0282 submits delivered volumes per pair per period. The VLP
  carries imbalance exposure on under-delivery. **Where two VLPs claim one MSID, the newer SBMU takes
  it.**
- **Supplier compensation.** Suppliers are compensated for deviation volumes attributed to VTPs at
  the Supplier Compensation Reference Price (methodology v2.0, effective 6 Nov 2025), and the cost is
  mutualised across suppliers by market share. How the reference price is set was not readable (gap).
  In the BM, direct compensation under P444 has been live since Nov 2025.
- **Counts.** 22 VLPs at go-live; 11 VTPs in 2025/26 among 97 companies Elexon registered for new
  roles; eight parties show SBMU compensation volumes Sep 2025–Feb 2026.

**Volumes and money, Sep 2025 – Feb 2026** (P510 IWA slides,
https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-panel-slides/):

| Month | Compensation (£) | SBMU compensation volume (MWh) |
|---|---|---|
| Sep 25 | 668,086 | 7,376 |
| Oct 25 | 1,239,855 | 13,859 |
| Nov 25 | 2,195,129 | 23,719 |
| Dec 25 | 3,734,111 | 38,193 |
| Jan 26 | 5,485,199 | 62,497 |
| Feb 26 | 5,576,308 | 63,827 |
| **Total** | **18,898,688** | **209,471** |

Implied ~£90/MWh **[derived; the two series come from different Elexon reports]**. Volume was
concentrated (Almape 77.9%, Axle 19.0%, EDF 2.9%), and so were receipts (SEFE ~76%, Octopus 13%,
E.ON Next 5%). Customer cost rose from under £0.10/MWh to ~£0.24/MWh by Feb 2026 (Drax,
https://energy.drax.com/intelligence/vtp-activity-builds-through-winter/).

**Rule changes.** P511 (approved 10 Aug 2026, implemented 24 Aug 2026) limits generator
participation by peak export: under 2 MW eligible, over 10 MW ineligible, a 30-day test between.
P510 would make compensation bilateral and direction-dependent, earliest Nov 2026 or Feb 2027.
P509 assesses DSR benefits. Sources: Ofgem P511 and P510 urgency decisions (links in the pack).

**What it means for a supplier's margin and hedge.** A VTP turn-down at its customer's meter leaves
the supplier long, spilled at the imbalance price; today it is made whole at the reference price from
a pot it also pays into by market share, so a supplier with few VTP customers pays a net levy. A
rival can take a customer's flexibility without the supplier's consent, because the newer SBMU wins
the MSID **[derived from the Elexon rule]**.

## 4. Local network flexibility (DNOs)

**Products.** The GB standard products are Peak Reduction (PR), Scheduled Utilisation (SU), Scheduled
Availability + Operational Utilisation (SAOU), Variable Availability + Operational Utilisation (VAOU)
and Operational Utilisation (OU). UKPN states they "replace our previous procurement of Sustain,
Secure and Dynamic" (confirmed on https://dso.ukpowernetworks.co.uk/flexibility, 2026-10-25). The
old-to-new mapping is not published there (section 9).

**Parameters** (ENWL guide): minimum unit 10 kW aggregated within a zone; response up to 15 minutes
for OU and VAOU; minimum utilisation 30 minutes; availability in £/MW/h and utilisation in £/MWh.

**Standard settlement** under the Market Facilitator (FMR-VSM, effective 30 Jan 2026): utilisation
settled per minute; availability reduced by a monthly utilisation performance factor; grace band 5%
(10% for OU); performance multiplier 3 (2 for OU), so payment reaches zero at 63% delivery;
over-delivery unpaid.

**Where the constraints are.** UKPN publishes a postcode-to-flexibility-zone dataset; NGED publishes
flexibility requirements and forecasts by zone; NESO's Local Constraint Market covers only the
England–Scotland border, extended to Jan 2027.

**Results by DNO, 2025/26:**
- NGED: 198 GWh procured, 6.5 GWh dispatched over 110,056 events; 1,239 zones; 43 active FSPs; £2.4m
  utilisation revenue, £756k committed availability (figures confirmed in the June 2026 report,
  2026-10-25). Average utilisation ~£369/MWh **[derived]**; ~£7.8 per domestic asset per year gross,
  an upper bound **[derived]**. FY24/25: SAOU availability £18.54/MW/h; a worked example pays £14.34
  for 1 kW turned down over 4 hours.
- UKPN: historically up to £600/MWh; a day-ahead market (4.4 GWh in its first year) on EPEX
  Localflex; the Oct 2025 tender was 20 MW across 217 zones, EV chargers 63% of capacity.
- SSEN: 66.1 MW contracted against 241.9 MW of unmet need; 1,334.5 MWh dispatched; minimum bid 10 kW
  (2.5 kW for SU); **£120 flat per participating household** in Load Managed Areas.
- SP ENW: 826 MW tendered in spring and 1,588 MW in autumn, 8.06 MW contracted; 8,786 MWh dispatched.
- SPEN: 2024/25 146 MW tendered, 385 MWh dispatched, £3.9m of reinforcement savings.
- Northern Powergrid: 2025/26 figures not retrieved (gap).

**The pattern.** Tendered far exceeds contracted, which far exceeds dispatched. Domestic assets are
nearly all assets by count and under 40% of capacity. For a household, DNO flexibility is a small,
location-gated, occasional stream, except short-notice LV events, where per-kW prices are high.

## 5. The Market Facilitator, 2025–2028

Elexon was appointed Jul 2024 and began operating 12 Dec 2025 under Ofgem's blueprint decision (net
benefit £65m–£442m). Ten Flexibility Market Rules in force from Dec 2025; common verification and
settlement 30 Jan 2026; Flexibility Market Catalogue Mar 2026; standard baselines 1 Apr 2026 (SSEN
1 Jul 2026); Market Data Portal end 2026; common dispatch API early 2027; a single registry for EVs,
heat pumps and batteries (FMAR Phase 1) by 30 Sep 2027.

**Standard baselines:** five methods (Asset Capacity, Fixed Reference, Nomination, Recent History,
Zero). Domestic heat pumps and EV chargers default to Fixed Reference values set by DNOs. Nomination
accuracy tests (10% net, 20% absolute error) apply mainly to I&C. Several devices at one property can
be grouped as one Meterable Unit.

## 6. The customer side

| Provider or scheme | Payment |
|---|---|
| Axle (from Nov 2024) | £1/kWh during stress events, minimum £10/month |
| Sunsave VPP | £15/month guaranteed 12–18 months; average ~£25/month (Sep 2026) |
| OVO Power Move Flex (EV) | £6–8/month on average for staying plugged in |
| SSEN Load Managed Area | £120 flat per household |
| Octopus Power-ups | Free electricity in DNO-called windows, notified day-ahead |
| NGED short-term LV event | £14.34 per kW for 4 hours to the FSP; ~£24 per EV at 1.67 kW **[derived]**, before the aggregator's share |

**Opt-in and fatigue.** Octopus Power-ups in the NPg area (Jan–Mar 2025): 14,477 MPANs signed up,
run as a randomised crossover trial; results not public. CrowdFlex (NESO, Feb 2026): 107,000 OVO
customers in utilisation trials and 33,000 OVO and Ohme customers in availability trials; turn-up drew
more than twice the response of turn-down; 12% of repeat participants reported waning interest;
automation shifted ~30% more energy; lower incentives were more cost-efficient per kWh; escalating
availability payments beat flat ones.

**Load-control licensing.** Ofgem's implementation decision (7 Aug 2026): applications open 1 Mar
2027 with a 12-month transition; the document gives the legal-force date both as "late 2027" and as
March 2028. Load controllers at or above 300 MW are expected to be Operators of Essential Services
under NIS. FSPs must join the Energy Ombudsman. Draft guidance requires explicit consent, the ability
to override, rewards not overstated, warnings against signing with several FSPs for one service, exit
fees no higher than direct economic loss, and identification of vulnerable customers
(https://www.ofgem.gov.uk/sites/default/files/2026-08/SSES-Implementation-Decision.pdf).

## 7. What the world would need, layer by layer

These are the advisor's recommended layers; the director's steer asks the roadmap to rule them.

| Layer | World holds | Supplier can then offer |
|---|---|---|
| L0 (minimum viable) | Per-home devices with kW ratings and plug-in/availability patterns; half-hourly wholesale and imbalance prices | Smart time-of-use shifting for EVs and heat pumps, valued against its own book |
| L1 | DFS and CM as event and annual streams; opt-in, incentive response, fatigue | Event participation and payments |
| L2 | DNO zone map by postcode and primary substation; products, prices, event calls; the performance multiplier | Location-gated local flexibility revenue |
| L3 | Rival VTP/VLP agents: newest SBMU takes the MSID; deviation compensation; mutualisation levy; P510/P511 switches | Retention of flexibility customers; pricing against rival offers |
| L4 | BM access via AMBU or VLP; relaxed metering; BL01 baselines | BM revenue |
| L5 | 2027 standardisation (registry, common dispatch); load-control licensing costs; stacking conflicts | A licensed load-controller role |

## 8. Headline bands (candidate world claims; calibration only, never per-home targets)

- Domestic share of DNO-registered flex: ~99.9% of assets, ~39% of capacity (NGED 2025/26).
- DNO flexibility value to a domestic asset: single-digit pounds a year gross at NGED **[derived]**.
- Household VPP payout: £6–25 a month.
- Supplier time-of-use shifting value: heat pump ~£84/yr; EV £250–610/yr.
- VTP supplier compensation Sep 2025–Feb 2026: £18.9m over 209,471 MWh.

## 9. Verification of the pack's [unverified] items (2026-10-25)

| Item | Outcome | Source |
|---|---|---|
| BL01 lookback "10 of the last 10 like-days" | **still open** — the document's version and date are confirmed (V3.0, effective 07/11/2024) but its body renders only by script and could not be read | https://bscdocs.elexon.co.uk/category-3-documents/baselining-methodology-document |
| Sustain → SU/PR, Secure → SAOU, Dynamic → VAOU, Restore → OU | **still open** — UKPN confirms the standard products replace Sustain, Secure and Dynamic, but publishes no mapping | https://dso.ukpowernetworks.co.uk/flexibility |

Spot checks of sourced figures: NGED 2025/26 asset counts, capacity, GWh, events and £2.4m — confirmed
in the report PDF.

Counts: confirmed 0, corrected 0, still open 2 (of 2 [unverified] items).

## 10. Named gaps

1. How the Supplier Compensation Reference Price is set, and its current value.
2. Realised household £/yr from the BM and from Quick or Slow Reserve: nothing published.
3. UKPN and NPg 2025/26 SLC31E figures (Ofgem zip, not fetched).
4. Piclo marketplace statistics.
5. Current UK figures for Tesla, GivEnergy, Social Energy and Lunar VPPs.
6. Power-ups and CrowdFlex £/kWh incentive levels and measured kW per household.
7. The old-to-new DNO product mapping.
8. The BL01 lookback rule.
9. A study stacking every domestic flexibility revenue stream.
10. Domestic participation in Capacity Market units.

## Second read: the advisor's verification pass, 25 Oct 2026

An independent read by the advisor
(`docs/staging/advisor/DIRECTOR_EVIDENCE_VERIFICATION_OF_THE_GB_PACKS_UNVERIFIED_ITEMS_2026-10-25.md`,
pack 3). Rows follow the section 9 table.

| # | Item | Section 9 | Advisor | Reconciled | Source |
|---|---|---|---|---|---|
| 1 | BL01 lookback "10 of the last 10 like-days" | still open | still open | still open. needs file: the full Elexon Baselining Methodology Document (the rule sits in §3.4.1, Step 1) | https://bscdocs.elexon.co.uk/category-3-documents/baselining-methodology-document |
| 2 | Sustain → SU/PR, Secure → SAOU, Dynamic → VAOU, Restore → OU | still open | still open | still open, and now **contested**: an example tender row in an SSEN manual reads "Operational Utilisation + Variable Availability (Secure)", which puts Secure under VAOU, not SAOU. The section 2 table's "DNO long-term (SAOU)" label rests on this mapping. Next: ENA Open Networks product definitions, or ask SSEN | https://ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/ssen-service-terms-aligned-to-fsa-manualv4.pdf |

No disagreement between the reads.

**Counts: confirmed 0 · corrected 0 · still open 2.**
