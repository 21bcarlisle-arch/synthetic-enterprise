# Director evidence: household flexibility and the advice roadmap

**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 05:37 GMT: "Also should we do more research on key future topics? How do gas boilers work and how do choices in the sim appear and gas usage and choices for customer and advice that the supplier can offer? E..g condensing or not? Thermostat. Timer and schedule. Flow rate. Radiator modernity and maintenance. . The same for EV purchase. Home charge versus venue. Cost and carbon savings versus petrol and diesel for different mileages. Then the actual charging and usage patterns that occur, based on logic that the SIM knows about the premise and person but the supplier has to figure out or ask about. Then the same for pv and battery. How old, what orientation, what settings. How much would the unit cost and save the customer. Then proving if it did or didn't. Sharing the savings clearly for the customer to enjoy. All these subjects are quite complicated and need knowledge. There may be others too we need for our roadmap??"

This is one of six cited evidence packs researched in the advisor's chat, outside your serial gate. They land in one commit with a cover steer: DIRECTOR_STEER_THE_ADVICE_ROADMAP_NEEDS_ITS_KNOWLEDGE_FIRST_2026-10-25.md. Read the cover steer first. It sets the order of work.

## What to do with it

- Turn this pack into a published Knowledge page, register its concepts, and take its headline bands as candidate world claims.
- Its "world needs to model" list is the hidden-attribute spec for the world, and the observe / infer / ask table is the wall spec for the supplier. The cover steer says when each is built.
- [derived] figures can be re-run. [unverified] figures are not claims until sourced. Named gaps are research tasks, and the research budget ran out on several of them. Close a gap, or record that nothing is published.
- This is drafting work, so it must not displace the serial queue.

---

# Poesys knowledge layer: evidence pack on household flexibility and the advice roadmap

**Scope and method.** This pack covers household flexibility and what a supplier can do with it (Part 1), and a scan of advice topics not covered elsewhere (Part 2). It does not cover boilers and controls, EVs, PV and batteries, heat pumps and insulation, or how savings are proven. Every figure has its source beside it.
- **[derived]** marks my own arithmetic.
- **[unverified]** marks figures from memory that no fetched source confirmed.

**Research limit.** The shared web-search budget ran out partway through. Part 1 is almost entirely sourced. Part 2 is mostly [unverified], and the "Named gaps" section lists what still needs a source.

---

## Part 1: Household flexibility and asset optimisation in GB

### 1.1 The Demand Flexibility Service (DFS) over three winters

| Winter | Registered | Events | Delivered | Cost / price | Source |
|---|---|---|---|---|---|
| 2022/23 | 1.6m households and businesses; 31 suppliers and aggregators | 22 (2 live) | >3,300 MWh | Guaranteed acceptance price £3,000/MWh for tests; live bids £3,300–6,500/MWh; total "nearly £11m"; about £3,330/MWh average (Carbon Brief's own calculation) | [NESO](https://www.neso.energy/news/demand-flexibility-service-delivers-electricity-power-10-million-households); [Carbon Brief](https://www.carbonbrief.org/?p=49272) |
| 2023/24 | 2.6m subscribed meters (about 99% domestic); 48 providers | 14 tests (7 competitive), 2 live | about 3,760 MWh | £11.9m in total (£7.1m tests, £4.8m live). Guaranteed price £3,000/MWh for tests 1–7, then £0. Average accepted competitive bid £1,110.9/MWh | [ESO end-of-year report](https://neso.energy/document/319911/download) |
| 2024/25 | 1.98m MPANs; 28 providers | 44 events, 236 settlement periods | 3,917.7 MWh (5,449.6 MWh accepted) | £943,983 paid. Average accepted bid £210/MWh; highest £1,290/MWh. Penalties withheld £76,666 | [NESO winter review](https://www.neso.energy/document/363911/download); [NESO news](https://neso.energy/news/nearly-2-million-households-and-businesses-registered-demand-flexibility-service-dfs-last-winter) |

What this means per unit:
- **Cost per MWh delivered:** about £3,165/MWh in 2023/24 and about £241/MWh in 2024/25. That is a fall of roughly 13 times [derived].
- **Pay per registered meter:** about £4.58 per winter in 2023/24 and about £0.48 per winter in 2024/25 [derived].
- **Delivery split:** in 2024/25, domestic and I&C (industrial and commercial) delivery was about 60/40, and more than 99% of MPANs responded manually ([NESO](https://www.neso.energy/document/363911/download)).

How the service changed in 2024/25 ([NESO](https://www.neso.energy/document/363911/download)):
- It became an all-year "merit-based margin tool" under an Ofgem derogation that runs to 31 March 2027.
- The day-ahead product was removed.
- Revenue can now be stacked with DNO flexibility, the Capacity Market and the Local Constraints Market.
- Asset meters no longer need to be linked to a half-hourly settlement boundary meter. Asset-meter registrations rose from 72 to 5,894.

Proposed next steps from NESO's December 2025 Routes to Market review ([Drax](https://energy.drax.com/intelligence/demand-side-flexibility-winter-boost/)):
- demand turn-up
- buying flexibility by location
- a minimum unit of 0.1 MW

**Modelling implication.** DFS has moved from a scarcity price of about £3/kWh to a merit price of about £0.20/kWh. In the simulated world, DFS should be a low-margin, occasional revenue stream, not a core earner.

### 1.2 Octopus Saving Sessions

| | 2022/23 | 2023/24 (to 22 January 2024) |
|---|---|---|
| Signed up | >700,000 (of 1.4m invited) | >1.2m |
| Sessions / hours | 13 / 14.5 | 9 / 10 |
| Energy turned down | 1.86 GWh | 1.41 GWh |
| Paid out | £5.3m | £4m |
| Average opt-ins per session | 342,272 | 397,000 |

Source for the table: [Octopus press release](https://octopus.energy/press/price-cap-protect-saving-sessions/).

Other figures:
- **2022/23 detail** ([Octopus, "Consumer flexibility – ready to replace coal"](https://fote.octopus.energy/documents/2635/Consumer_flexibility_-_ready_to_replace_coal.pdf)):
  - The average opted-in customer earned about £8; the top 5% earned more than £40.
  - Incentives were £2.25/kWh for test events and £3.69/kWh for live events.
  - Peak reduction was 188 MW, with an average of 128 MW.
  - Octopus extrapolated more than 2.1 GW if all 17.3m smart-meter homes were invited.
- **What customers received:** about £2.85 per kWh turned down in 2022/23 [derived: £5.3m ÷ 1.86 GWh].
- **Opt-in rate fell:** opt-ins were about 49% of sign-ups per session in 2022/23 and about 33% in 2023/24 [derived].
- **Turn-down per opt-in:** about 0.40 kWh per session in 2023/24 [derived: 1.41 GWh ÷ 9 ÷ 397k]. Octopus's "0.7 kWh per session" is a threshold to offset the £24 price-cap rise, not an average.
- **Reward currency:** 8 OctoPoints = 1p ([householdmoneysaving.com](https://www.householdmoneysaving.com/?p=21619)). The same source says sessions were fewer and rewards lower in 2025, but gives no figures, so treat that as weak evidence.

### 1.3 Value streams a supplier can capture

| Stream | Access route | Evidence | Band for Poesys |
|---|---|---|---|
| **Wholesale shaping under half-hourly settlement** | The supplier is settled on actual half-hourly consumption, so moving load to cheap periods lowers its purchase cost | Ofgem put the benefits of market-wide half-hourly settlement (MHHS) at £1.6–4.5bn by 2045 ([Ofgem](https://www.ofgem.gov.uk/blog/major-system-upgrade-hit-net-zero-and-help-cut-energy-bills)). In Q4 2025, shifting off-peak could save over £380/MWh for pass-through customers ([Drax](https://energy.drax.com/intelligence/flexibility-focus-q4-2025/)) | Largest stream. Per-household value scales with shiftable kWh. Example: 1,000 kWh/yr shifted at a £50–150/MWh average spread is £50–150 per household per year [derived; assumed spread] |
| **Imbalance avoidance** | Better forecasting and real-time correction of the supplier's position | Balancing, constraint and reserve costs were £2bn in 2021, or £72 per household ([CrowdFlex Discovery](https://www.neso.energy/document/361021/download)) | Not sized per household. **Gap** |
| **DFS** | Supplier or aggregator as provider; stackable since 2024/25 | Table 1.1 | £0.5–5 per meter per winter [derived]; up to about £8 per active opt-in at 2022/23 prices |
| **Balancing Mechanism** | Small aggregated asset units. Octopus entered EVs in September 2023 with 3 MW registered, and up to 300 MW was allowed under relaxed metering (±2.5% accuracy, 60-second asset refresh) ([NESO trial report](https://neso.energy/document/346171/download)). Since March 2026, standard domestic devices can take part without specialist meters ([NESO](https://www.neso.energy/news/millions-households-and-businesses-free-reap-rewards-flexing-energy-use)) | Kraken has more than 270,000 controllable devices and more than 1.7 GW, mostly EVs, used in the Capacity Market and BM ([Kraken engineering](https://engineering.kraken.tech/news/2025/03/27/building-the-largest-ev-vpp-in-the-world.html)) | No £ figure published. **Gap** |
| **Capacity Market** | Demand-side response units, de-rated | T-4 2029/30 cleared at £27.10/kW/yr; T-1 2026/27 at £5.00/kW/yr. DSR plus storage was 3.8 GW (9.5%) of the T-4 ([Drax](https://energy.drax.com/intelligence/capacity-market-auction-results/)) | £2.50–13.50 per household per year at 0.5 kW de-rated firm capacity [derived; assumed de-rating] |
| **DNO flexibility** | Piclo and DNO tenders using ENA standard contracts | ENA: 4.6 GW tendered and 1.9 GW contracted in 2022/23 ([Enlit](https://www.enlit.world/library/flexibility-record-set-in-gb)); 3.2 GW contracted in 2023 ([Modo](https://modoenergy.com/research/en/oct-24-local-flexibility-markets-dno-enw-nged-ukpn-sse-spen-demand-response-dynamic-sustain-secure-battery-energy-storage-bess)). UKPN's 2020 tender: 123 MW for £14m, about £114k/MW, contracts averaging more than 5 years ([The Energyst](https://theenergyst.com/uk-power-networks-awards-123mw-of-flex-contracts-evs-included/)). ENWL 2025/26: 8.059 MW contracted ([ENWL](https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/document-library/ofgem-dfp-reporting/distribution-flexibility-services-procurement-report-2026.pdf)) | About £23/kW/yr where a constraint exists [derived: £114k/MW ÷ ~5 years]; zero elsewhere. Value depends on location |

**Wholesale competition from independent aggregators.** Elexon modification P415 took effect on 7 November 2024 ([Elexon](https://www.elexon.co.uk/2024/11/07/elexon-implements-landmark-rule-change-to-drive-growth-in-flexibility-and-progress-to-net-zero/)).
- It lets independent aggregators (Virtual Trading Parties) trade a household's flexibility in the wholesale market, competing with the supplier.
- The supplier is compensated at "average supplier sourcing costs", with costs shared across all suppliers ([Ofgem P415 decision](https://www.ofgem.gov.uk/sites/default/files/2023-10/Ofgem%20decision%20P415%20%27Facilitating%20Access%20to%20Wholesale%20Markets%20for%20Flexibility%20Dispatched%20by%20VLPs_0.pdf)).
- P504, implemented 26 February 2026, added these parties to Elexon's performance assurance ([Ofgem](https://www.ofgem.gov.uk/sites/default/files/2026-02/P504-Balancing-and-Settlement-Code-%28BSC%29-changes.pdf)).

**Baselining.** P376 (implemented 23 February 2023) lets aggregators and suppliers in the BM use a baseline instead of a physical notification ([Elexon](https://www.elexon.co.uk/mod-proposal/p376/)).

**Modelling implication.** A third party can now monetise a Poesys customer's flexibility. The world needs an agent for this rival "flex captor", with compensation flowing back to the supplier.

**Whole-household estimates:**
- Up to £137 per household per year (Element Energy, in [CrowdFlex Discovery](https://www.neso.energy/document/361021/download)).
- About £206 per household per year in a 2040 high-electrification scenario (OVO/Imperial 2018, [EV Infrastructure News](https://www.evinfrastructurenews.com/emobility/households-blocked-from-the-benefits-of-residential-flexibility-says-new-report)).
- Intelligent Octopus Go cut charging costs by £343/yr (Centre for Net Zero, via [Kraken](https://www.kraken.tech/case-studies/octopus-energy-residential-flexibility)). This is a saving on the customer's tariff, not revenue to the supplier.

**National targets:**
- 10–12 GW of consumer-led flexibility by 2030 ([DESNZ SSES response](https://assets.publishing.service.gov.uk/media/6a85c2818d785493a9c89811/sses-licensing-consultation-government-response.pdf)).
- Up to 6 GW of demand-side response from smart EV charging by 2030, per the ESO's Future Energy Scenarios ([NESO](https://www.neso.energy/news/domestic-electric-vehicle-charging-help-eso-balance-energy-system-first-time)).
- FES 2025: demand-side measures cut peak demand by up to 54% by 2050 ([REA analysis](https://www.r-e-a.net/wp-content/uploads/2025/08/NESO-FES-2025-REA-Analysis-Final.pdf)).
- CrowdFlex technical potential for 2030: 0.4–6.8 GW of turn-down and 3.8–37 GW of turn-up ([CrowdFlex Phase 1](https://neso.energy/document/353731/download)).

### 1.4 How much households actually shift

**Response size.** Centre for Net Zero's analysis of the 2022/23 Saving Sessions ([BIEE paper](https://www.biee.org/wp-content/uploads/2023/09/46-Saving-Sessions-for-BIEE.pdf)):
- Signed-up customers cut consumption by 24–26% (0.09–0.10 kWh per half-hour).
- Customers who opted in cut 38–40%.
- Against a natural comparison group (Bulb customers), the cut was only 9.4%.
- Use in the hours either side also fell by 1–3%.
- The value-for-money measure (MVPF) was 1.05, rising to 2.63 if the value of lost load is £6,000/MWh.

**Baseline bias.** The ESO's baseline method overstated the domestic reduction by 13%: 1,863 MWh credited against 1,642 MWh estimated ([Utility Week](https://staging4.utilityweek.co.uk/demand-reduction-measured-in-last-winters-dfs-is-too-optimistic)).

**Opt-in and repeat participation:**
- Of those who signed up, 91% opted in at least once, 55% six or more times, and 7% to all 13 sessions ([BIEE](https://www.biee.org/wp-content/uploads/2023/09/46-Saving-Sessions-for-BIEE.pdf)).
- Same-day notice drew 44% opt-in, against 63% for day-ahead ([Octopus](https://fote.octopus.energy/documents/2635/Consumer_flexibility_-_ready_to_replace_coal.pdf)).
- An SMS plus a £1.25 bonus raised opt-in by about 23% ([BIEE](https://www.biee.org/wp-content/uploads/2023/09/46-Saving-Sessions-for-BIEE.pdf)).
- In CrowdFlex (2026 closure report), 107,000 OVO customers ran utilisation trials. Opt-in was 36% with longer notice and 25% with 2-hour notice. 80% shifted manually, and 64% of EV drivers plugged in more often ([NESO CrowdFlex closure](https://www.neso.energy/document/382251/download)).

**Delivery against bids.** In DFS 2024/25, delivered volume was 71.9% of bids overall. By month it ran 64.8–66.7% from December to February and 82.1% in March ([NESO](https://www.neso.energy/document/363911/download)).

**Fatigue.** Few sources measure it directly. The signals are:
- opt-in falling from about 49% to 33% of sign-ups [derived]
- participation thinning across the 13 events
- low winter-round delivery
- re-enrolment in repeated conservation challenges depends on whether households succeeded or failed before, not on the incentive ([Fraser 2023, JAERE](https://ideas.repec.org/a/ucp/jaerec/doi10.1086-721094.html))

**Attitudes:**
- SPEN survey ([SPEN](https://www.spenergynetworks.co.uk/userfiles/file/SPEN_DSO_Customer_Research_Flex_Report.pdf)): 86% would take part in principle, but only 33% actually do. The average payment threshold is £12.70/month, about £152/yr [derived]. 51% of low-carbon-technology users favour opt-out enrolment.
- Ofgem's flexibility survey, June 2025, n=4,385 ([Ofgem FANZ](https://www.ofgem.gov.uk/sites/default/files/2026-05/Flexibility-and-Net-Zero-Survey-Findings-Report-2025.pdf)):
  - 16% are on a time-of-use tariff they can name (53% of EV users).
  - 26% are comfortable with a company controlling EV charging (55% of EV users).
  - Only 16% are comfortable with a company controlling heating; 72% are uncomfortable.

**Modelling implication.** Expectations are about £150/yr, but event payments are now well under £5 per meter. Value has to come from automated, tariff-embedded shifting, not from manual events.

### 1.5 Control, consent and cybersecurity

The Smart Secure Electricity Systems (SSES) programme sets the rules ([DESNZ response](https://assets.publishing.service.gov.uk/media/6a85c2818d785493a9c89811/sses-licensing-consultation-government-response.pdf); [Ofgem decision of 7 August 2026](https://www.ofgem.gov.uk/consultation/smart-secure-electricity-systems-implementing-load-control-licensing-regime); [CMS summary](https://cms.law/en/gbr/legal-updates/smart-secure-electricity-system-sses-programme-the-proposed-load-control-regime-at-a-glance)).

**Who is licensed.** There are two licence roles:
- **Load Controller:** creates or changes control signals to devices.
- **Flexibility Service Provider (FSP):** contracts with the consumer.

There is no capacity threshold for needing a licence, and unlicensed activity becomes a criminal offence after the transition. Exemptions:
- control that benefits only the consumer and is not sold to network operators or traders
- incentive-only tariff signals

Suppliers get reduced-evidence application routes (Pathways B and C).

**Timeline.** Regulations are laid in autumn 2026, applications open in March 2027, and a licence is required from March 2028. This later date replaces the "end-2027" in CMS's December 2025 summary.

**Devices in scope:**
- EV smart charge points
- smart electric heating up to 45 kW thermal
- domestic batteries

Phase 1 of the energy smart appliance regulations requires smart functionality from 31 December 2027.

**Cybersecurity:**
- Below 300 MW of aggregated load: licence conditions and an annual check against a Tier 2 Cyber Assessment Framework (CAF).
- At or above 300 MW: the NIS Regulations under a Tier 1 CAF.
- Significant incidents must be reported to Ofgem and the Secretary of State.

**Consumer terms:**
- products must be suitable
- no pressure selling
- exit fees capped at the provider's actual economic loss
- enhanced safeguards for vulnerable customers
- membership of the Energy Ombudsman

**Existing EV charger rules [unverified].** The Smart Charge Points Regulations 2021 require default off-peak charging, a randomised delay of up to 600 seconds, and security aligned with ETSI EN 303 645.

**Device access in practice.** Kraken integrates devices through manufacturers' cloud APIs and OCPP ([Kraken](https://engineering.kraken.tech/news/2025/03/27/building-the-largest-ev-vpp-in-the-world.html)). How Home Energy Management Systems (HEMS) are treated is still unclear ([Energy Systems Catapult](https://es.catapult.org.uk/?p=21471)).

### 1.6 How suppliers share the value

| Model | Example | Evidence |
|---|---|---|
| Per-kWh pass-through of event payments | Saving Sessions: £2.25–3.69/kWh (2022/23); OctoPoints | [Octopus](https://fote.octopus.energy/documents/2635/Consumer_flexibility_-_ready_to_replace_coal.pdf) |
| Cheaper tariff for ceding control | Intelligent Octopus Go: −£343/yr charging cost | [Kraken](https://www.kraken.tech/case-studies/octopus-energy-residential-flexibility) |
| Bill credits or cash per action | Pod rewards customers with cash per smart charge; NESO cites "lower tariffs, bill credits" | [NESO](https://www.neso.energy/news/millions-households-and-businesses-free-reap-rewards-flexing-energy-use) |
| Asset-for-service | Octopus Power Pack: free charging for V2G discharge | [Kraken](https://www.kraken.tech/case-studies/octopus-energy-residential-flexibility) |
| Pay only for opted-in delivery | CrowdFlex aligned to DFS terms: turn-up volume 48% above control | [NESO CrowdFlex](https://www.neso.energy/document/382251/download) |

**Pass-through share.** In 2022/23, Octopus paid customers about 86% of the average DFS cost per kWh [derived: £2.85 ÷ about £3.33 average across all DFS. This compares Octopus's payout with the market average, so treat it as indicative].

**Exit fees.** Under SSES, an FSP's exit fee is limited to its economic loss, which constrains asset-lock-in models.

---

## Part 2: Roadmap scan of further advice topics

Each topic gives 2–4 figures and a one-line "why". Most figures are [unverified] because the search budget ran out.

**A. Electric resistance and storage heating, Economy 7**
- About 1.5–2m GB homes rely mainly on electric heating, and about 4m+ are on Economy 7-type meters [unverified].
- The radio teleswitch (RTS) switch-off began in mid-2025, region by region [unverified].
- Moving 7% of consumers from direct electric heating to heat pumps saves 18 TWh in 2050 ([NESO FES 2025](https://www.neso.energy/document/365091/download)).
- SSES covers smart electric heating up to 45 kW ([CMS](https://cms.law/en/gbr/legal-updates/smart-secure-electricity-system-sses-programme-the-proposed-load-control-regime-at-a-glance)).
- Modern "Quantum"-type storage heaters are claimed to cut running costs against old storage heaters [unverified, no figure].
- **Why:** these households have the highest bills per kWh of heat and the most thermal storage. They are both the biggest saving case and the biggest flexibility pool, without needing a heat pump.

**B. Hot water cylinders and immersion diverters**
- Hot water is commonly put at about 15–20% of home heating energy [unverified].
- Smart cylinders and immersions fall under the 45 kW smart-heating scope ([CMS](https://cms.law/en/gbr/legal-updates/smart-secure-electricity-system-sses-programme-the-proposed-load-control-regime-at-a-glance)).
- Many cylinders were removed in combi-boiler conversions [unverified].
- **Why:** a cylinder is the cheapest domestic thermal battery. It enables turn-up, which NESO is proposing for DFS ([Drax](https://energy.drax.com/intelligence/demand-side-flexibility-winter-boost/)).

**C. Cooking, appliances and standby**
- Induction is about 85–90% efficient against about 40% for gas hobs [unverified].
- Standby is often put at about £50/yr per household [unverified].
- Smart white goods are excluded from SSES launch scope ([DESNZ](https://assets.publishing.service.gov.uk/media/6a85c2818d785493a9c89811/sses-licensing-consultation-government-response.pdf)).
- **Why:** this is advice every customer can use, but the savings are small. It suits low-cost digital nudges more than flexibility.

**D. Tariff choice and "better deal" advice**
- 16% are on a time-of-use tariff they can name; 49% think one would save them money; 41% are unlikely to switch ([Ofgem FANZ](https://www.ofgem.gov.uk/sites/default/files/2026-05/Flexibility-and-Net-Zero-Survey-Findings-Report-2025.pdf)).
- The CMA (2016) found about £1.4bn/yr of detriment from customers not engaging [unverified].
- **Why:** matching a household to the right tariff, informed by its half-hourly data, is the core personalisation offer and the cheapest saving to prove.

**E. Smart meter and device data access**
- Default data granularity is monthly, daily on an opt-out basis, and half-hourly only with opt-in consent (smart meter Data Access and Privacy Framework) [unverified].
- About two-thirds of meters are smart or advanced [unverified].
- 97% of smart-meter reads arrived on time in the BM trial ([NESO](https://neso.energy/document/346171/download)).
- **Why:** without half-hourly consent there is no personalised modelling. Consent rates are a gating variable.

**F. Prepayment and vulnerable households**
- About 4m+ electricity prepayment meters, including smart pay-as-you-go [unverified].
- Ofgem tightened involuntary installations in 2023 [unverified].
- FSPs must apply enhanced vulnerability safeguards ([CMS](https://cms.law/en/gbr/legal-updates/smart-secure-electricity-system-sses-programme-the-proposed-load-control-regime-at-a-glance)).
- Warm Home Discount is £150 [unverified].
- **Why:** this is the highest-stakes advice group, with self-disconnection, debt and regulatory exposure. Value-sharing must not take value from them.

**G. Grants and schemes**
- ECO4 runs until 31 December 2026 ([Ofgem](https://www.ofgem.gov.uk/environmental-and-social-schemes/energy-company-obligation-eco)).
- GBIS closed on 31 March 2026. It required EPC D–G and council tax A–D in England ([Ofgem](https://www.ofgem.gov.uk/environmental-and-social-schemes/great-british-insulation-scheme)).
- The Boiler Upgrade Scheme pays £7,500, or £9,000 off the gas grid until 31 March 2027, and £2,500 for air-to-air heat pumps ([Ofgem](https://www.ofgem.gov.uk/environmental-and-social-schemes/boiler-upgrade-scheme-bus)).
- The Warm Homes Plan is about £13.2bn and replaces bill-funded ECO [unverified].
- **Why:** grants are the largest single upfront saving a supplier can broker, and ECO's end changes the supplier's own obligations.

**H. Landlords and tenants (MEES, private rented sector)**
- The minimum EPC is E, with a £3,500 cap [unverified].
- The proposed path is EPC C by 2030 with a £10,000 cap [unverified].
- The private rented sector is about 19% of English households [unverified].
- **Why:** the landlord pays for upgrades while the tenant gets the savings, a split-incentive problem. Different decision-makers need different advice.

**I. Home moves**
- About 1m+ housing transactions per year [unverified].
- An EPC is required at sale and let [unverified].
- **Why:** a move is the moment of tariff choice, data consent, and retrofit decisions, when acquisition costs are low.

**J. EPC reform and the Home Energy Model**
- New EPC metrics and the Home Energy Model will replace SAP from about 2026 [unverified].
- GBIS and MEES both hinge on EPC bands ([Ofgem](https://www.ofgem.gov.uk/environmental-and-social-schemes/great-british-insulation-scheme)).
- **Why:** the EPC sets grant and MEES eligibility. The simulation's property model needs to emit EPC-equivalent outputs.

**K. Heat networks**
- About 14,000 networks serve about 0.5m consumers [unverified].
- Ofgem regulation started in January 2026 [unverified].
- **Why:** customers whose heat the supplier does not supply. They are a niche, but common in flats and social housing.

**L. Air conditioning and summer cooling**
- About 3–5% of homes have AC [unverified].
- Air-to-air heat pumps (which also cool) now get £2,500 under BUS ([Ofgem](https://www.ofgem.gov.uk/environmental-and-social-schemes/boiler-upgrade-scheme-bus)).
- DFS is now year-round ([NESO](https://www.neso.energy/document/363911/download)).
- **Why:** a new summer-peak load with flexibility potential, and growing.

**M. Whole-house retrofit sequencing**
- PAS 2035 retrofit coordination is mandatory for ECO and GBIS work [unverified].
- DESNZ flagged "potential issues with ECO and GBIS installations" in January 2025 ([Ofgem](https://www.ofgem.gov.uk/environmental-and-social-schemes/energy-company-obligation-eco)).
- **Why:** doing measures in the wrong order destroys value and trust. Advice must sequence fabric, then controls, then heating.

**N. Trust and advice regulation**
- The BUS requires an MCS-certified installer ([Ofgem](https://www.ofgem.gov.uk/environmental-and-social-schemes/boiler-upgrade-scheme-bus)).
- FSPs must "recommend only suitable products" ([CMS](https://cms.law/en/gbr/legal-updates/smart-secure-electricity-system-sses-programme-the-proposed-load-control-regime-at-a-glance)).
- 17% of those unwilling to take a time-of-use tariff distrust the supplier to price fairly ([Ofgem FANZ](https://www.ofgem.gov.uk/sites/default/files/2026-05/Flexibility-and-Net-Zero-Survey-Findings-Report-2025.pdf)).
- Ofgem's Standards of Conduct apply [unverified].
- **Why:** an advice-led model with a share of the value is exactly what the suitability rules target. Trust is the scarce input.

---

## (a) Headline figures and bands for Part 1

| Item | Figure / band | Status |
|---|---|---|
| DFS registered meters | 1.6m → 2.6m → 1.98m (2022/23 → 2024/25) | Sourced |
| DFS delivered | 3.3 → 3.76 → 3.92 GWh | Sourced |
| DFS cost per MWh delivered | ~£3,330 → ~£3,165 → ~£241 | Carbon Brief estimate / [derived] / [derived] |
| DFS average accepted bid, 2024/25 | £210/MWh | Sourced |
| DFS revenue per registered meter per winter | £4.58 (2023/24) → £0.48 (2024/25) | [derived] |
| DFS delivery vs bid, 2024/25 | 71.9% (64.8–82.1% by month) | Sourced |
| Response, signed-up / opted-in / natural comparison | 24–26% / 38–40% / 9.4% | Sourced |
| Baseline overstatement | 13% | Sourced |
| Opt-in per session | 49% → 33% of sign-ups | [derived] |
| Same-day vs day-ahead opt-in | 44% vs 63%; CrowdFlex 25% vs 36% | Sourced |
| Capacity Market | £5.00 (T-1) to £27.10 (T-4) per kW/yr; £2.50–13.50 per household/yr | Sourced / [derived] |
| DNO flexibility | ~£23/kW/yr where located (UKPN 2020) | [derived] |
| Wholesale shaping | £50–150 per household/yr per 1,000 kWh shifted | [derived, assumed spread] |
| Whole-household flexibility value | £137–206 per household/yr | Sourced (modelled studies) |
| Consumer payment expectation | £12.70/month (~£152/yr) | Sourced / [derived] |
| Comfort with third-party control | EV 26%, heating 16% | Sourced |
| Supplier pass-through example | ~86% of DFS value | [derived, indicative] |
| SSES licence required | March 2028; 300 MW threshold for NIS cyber oversight | Sourced |
| National target | 10–12 GW consumer-led flexibility by 2030 | Sourced |

## (b) Ranked roadmap for Part 2

| Rank | Topic | Why the supplier needs it | What the world must model | Priority |
|---|---|---|---|---|
| 1 | Tariff choice and better-deal advice (D) | Core personalisation saving, cheapest to prove | Tariff catalogue, switching inertia, time-of-use uptake | P1 |
| 2 | Smart data access and consent (E) | Gates all modelling | Consent states (monthly / daily / half-hourly), device API availability | P1 |
| 3 | Electric storage heating and Economy 7 (A) | Highest bills plus large thermal flexibility | Storage heater physics, RTS migration, multi-rate tariffs | P1 |
| 4 | Prepayment and vulnerability (F) | Regulatory risk; must not take value from them | Payment type, debt, self-disconnection, Priority Services Register flags | P1 |
| 5 | Grants and schemes (G) | Biggest upfront saving; ECO ends | Eligibility rules (benefits, EPC, council tax), scheme calendars | P1 |
| 6 | Hot water and immersion (B) | Cheap turn-up storage | Cylinder presence and size, draw profiles | P2 |
| 7 | Trust and advice regulation (N) | Licence and suitability risk | Complaint and trust state per customer; suitability checks | P2 |
| 8 | Landlord / tenant and MEES (H) | Split incentive | Tenure, landlord agent, MEES deadlines | P2 |
| 9 | Home moves (I) | Low-cost decision moment | Move events, tenure churn | P2 |
| 10 | EPC reform / Home Energy Model (J) | Sets eligibility | EPC-equivalent output from the property model | P2 |
| 11 | Retrofit sequencing (M) | Avoids value-destroying order | Measure dependencies, PAS 2035 gate | P3 |
| 12 | Air conditioning / cooling (L) | Emerging summer load and flexibility | Temperature-driven cooling demand | P3 |
| 13 | Cooking / appliances / standby (C) | Small universal savings | Appliance stock and standby baseline | P3 |
| 14 | Heat networks (K) | Niche, not supplied by Poesys | Flag only | P3 |

## (c) Named gaps

1. **Imbalance-avoidance value per household:** no source fetched.
2. **BM revenue for aggregated domestic assets:** no £ figure published by NESO or Kraken in the sources found.
3. **DNO domestic flexibility prices:** no current £/MWh utilisation or £/MW/h availability prices; only UKPN's 2020 figure and ENWL volumes.
4. **Capacity Market de-rating for domestic DSR:** my band assumes 0.5 kW per household.
5. **MHHS current timeline:** the October 2025 date comes from a 2021 Ofgem page; the actual migration status was not verified.
6. **DFS 2025/26 outturn:** not found.
7. **Octopus Saving Sessions 2024/25 and 2025/26:** no primary data.
8. **Not fetched:** Axle Energy, OVO Charge Anytime, Piclo volumes, ENA Open Networks reports, CCC Seventh Carbon Budget flexibility assumptions, and the FES 2025 flexibility figures in GW (data workbook needed).
9. **Direct fatigue measurement:** no study isolates it; the evidence is indirect.
10. **Part 2 figures:** almost all [unverified]. Before use, these need verification against gov.uk and Ofgem sources: Warm Home Discount, Warm Homes Plan, MEES, the English Housing Survey (electric heating, PRS share, cooling), Energy Saving Trust (standby, hot water), heat networks, prepayment counts and the CMA 2016 figure. The search budget ran out mid-task; a follow-up session can verify these.

**Discrepancies to report:**
- The SSES licence date is end-2027 in CMS (December 2025) but March 2028 in the DESNZ response and Ofgem's August 2026 decision. The later sources are used.
- The 2024/25 DFS accepted-tender total is £1,223,312 in one place and £1,233,312 in another within the same NESO document.
- The CrowdFlex closure report's NPV (£337.7m vs £218.2m) and CO2 figures (3.4 vs 6.3 MtCO2e) disagree between sections.