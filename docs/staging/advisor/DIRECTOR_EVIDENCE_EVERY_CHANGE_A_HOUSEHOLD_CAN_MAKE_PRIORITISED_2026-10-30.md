**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] Every change a household can make: the catalogue, prioritised by cost, ease and remaining market (2026-10-30)

**Type:** EVIDENCE, through the advisor channel, for `DIRECTOR_STEER_TIME_IS_VALUE_A_SUPPLIER_CAN_CREATE_AND_THE_WORLD_MUST_FEEL_HASSLE_2026-10-30.md`. The director's words, from chat on Fri 30 Oct:

- 12:22 GMT: "Do we have a list of the all changes and investments customers can make to save money and carbon?"
- 12:26 GMT: "This needs to be prioritised based on costs, ease and remaining market size (IE existing pentration, and restrictions)"

## How to use this pack

- It comes from an advisor research pass, sourced from the web. Many hassle hours, uptake shares and costs are tagged [unverified]. They are calibration assumptions, not evidence.
- Use the existing §5 of `household_carbon_and_the_measures_that_save_it.md` for £ and carbon wherever it is stronger.
- The scoring formula in §12 is published so that it can be re-weighted. Its carbon value (£250/t) and asset lives are assumptions.
- The pack says the behaviour rows need a persistence haircut. The only GB RCT, on flow temperature, measured 0.4% against a modelled 8–9%.

## Notable points for the world and the supplier

- **Removing hassle is what works.** Ofgem's collective-switch trials, where customers did nothing but make one contact, got 24–29.5% to switch, 7–10 times the baseline. Warm Home Discount automatic matching reaches 96% of recipients. Advice alone barely moves behaviour.
- **The revealed hassle cost is large.** The CMA's £160 detriment persisted among about 70% of customers, which puts the implied hassle value for the marginal non-switcher at about £100–£160 a year.
- **The private rented sector is a landlord market for fabric and heating.** Those homes must reach EPC C by 1 Oct 2030, with a £10k cost cap.
- **Heat pumps are a distress-purchase mismatch.** 48% of boiler purchases are distress purchases, against 13% of heat pump purchases.
- **These measures are bundles:** battery with time-of-use, and induction hob with gas disconnection.

---

# GB Household Energy Measures: Evidence Pack (prioritised catalogue)

**Compiled:** 30 October 2026. **Scope:** Great Britain, domestic. **Convention:** a URL sits beside each sourced claim. **[unverified]** marks anything I could not confirm from a primary or reputable source, including my own stated assumptions. **[derived]** marks my own arithmetic on sourced inputs.

**How this was done:** about 25 web searches plus targeted page reads. Some pages blocked direct fetching: gov.uk's Warm Home Discount and Boiler Upgrade Scheme pages, and Energy Saving Trust's per-technology advice pages. Where that happened I used official statistics releases, Ofgem documents or reputable secondary pages. For the physical measures already mapped elsewhere, I give one £ figure and move on, as briefed.

---

## 0. Baseline facts used throughout

| Fact | Value | Source |
|---|---|---|
| Price cap, 1 Oct to 31 Dec 2026, Direct Debit: electricity | 26.32p/kWh; standing charge 54.83p/day (excludes VAT, which is removed from electricity bills 1 Oct 2026 to 31 Mar 2027) | [Ofgem](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026) |
| Price cap, Oct to Dec 2026: gas | 7.97p/kWh; standing charge 29.68p/day (includes 5% VAT) | [Ofgem](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026) |
| Typical dual-fuel Direct Debit bill, Oct 2026 | £1,723/yr (secondary source) | [PayPlan](https://www.payplan.com/blog/ofgem-energy-price-cap-hits-three-year-high/) |
| Gas standing charge per year | 29.68p × 365 = **£108.33** [derived] | [Ofgem](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026) |
| Policy costs from 1 Apr 2026 | ECO funding ended and 75% of RO costs removed from bills, about £150 average saving, applied to **unit rates** | [gov.uk](https://www.gov.uk/government/news/your-energy-bill-from-april-whats-changing); [Ofgem](https://www.ofgem.gov.uk/sites/default/files/2026-01/Treatment%20of%20ECO%20and%20RO%20in%20the%20price%20cap%20from%20April%202026%20%281%29-20260126113009.pdf) |
| GB households | about 27.8m (UK about 28.6m less NI) **[unverified]** | none found in budget |
| Tenure (England, 2024-25) | Owner-occupied 65% (36% outright, 29% mortgage); private rented (PRS) 19%; social 16%. **Applied to GB [unverified assumption]** | [EHS](https://www.gov.uk/government/statistics/chapters-for-english-housing-survey-2024-to-2025-headline-findings-on-demographics-and-household-resilience/introduction-and-key-findings) |
| Homes with no gas meter | 18% → gas-connected share about 82% → about 22.8m homes [derived] | [DESNZ smart meter stats](https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin) |
| Smart electricity meter | 75% of homes (71% in smart mode, 3.8% in traditional mode) | [DESNZ](https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin) |
| Smart gas meter | 57% of homes (50% in smart mode) | [DESNZ](https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin) |
| EPC bands, England 2024 | A to C 56%; D 35%; E to G 9%; average cost to reach C £7,480 | [EHS energy efficiency](https://www.gov.uk/government/statistics/chapters-for-english-housing-survey-2024-to-2025-headline-findings-on-housing-quality-and-energy-efficiency/introduction-and-key-findings) |
| Main heating | 75% use a gas boiler | [DESNZ Public Attitudes Tracker (PAT) Winter 2025](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-heat-and-energy-use-in-the-home-winter-2025-uk) |
| Carbon value used in ranking | £250/tCO2 **[unverified assumption]**, roughly the scale of UK appraisal values | none |

**Observability key** (what the supplier can see from half-hourly smart data):
- **HH-visible:** inferable from the load shape.
- **Account:** known from billing and CRM.
- **Ask:** needs a survey, EPC lookup or customer declaration.

**Ease score (1 to 5):**
- 5 = under 1 hour, no third party.
- 4 = 1 to 3 hours, or one visit.
- 3 = one trade, one day, some disruption.
- 2 = multiple parties, survey plus install, or weeks of lead time.
- 1 = multi-trade, multi-day disruption, scarce installers, or consents.

The scores are my judgement, informed by the hassle evidence in §9 **[unverified]**.

---

## A. Commercial and money levers

### A1. Value, cost, applicability, uptake and remaining market

| Measure | £/yr saving (carbon) | Upfront / ongoing | Applicability | Current uptake | Remaining addressable (arithmetic) | Ease |
|---|---|---|---|---|---|---|
| Switch from standard credit to Direct Debit | **£136** (typical bill gap, Jan to Mar 2026 cap). No carbon effect | £0 / none | Anyone with a bank account and credit meter | Standard credit share about 11% **[unverified]** | 27.8m × 11% ≈ **3.1m** [unverified] | 5 |
| Prepayment (smart PAYG) vs Direct Debit | PPM was **£47 cheaper** than DD at the Jan 2026 cap | £0 | Smart meter needed for remote mode switch | Not found | Not a recommended switch for most: a niche and vulnerability issue | 4 |
| Fixed tariff vs standard variable tariff (SVT) | Market-dependent. Historically about £160 (2015 CMA dual-fuel detriment); now **£0 to £150 [unverified]** | £0; exit fees on some fixes | All except some PPM or legacy meters | 70% on SVT in 2015; current share not found **[unverified]** | Assume 65% still on SVT or cap-tracking → 27.8m × 65% ≈ **18m [unverified]** | 5 |
| Supplier switching | Ofgem collective-switch trials: average projected saving **£150 to £298** per switcher | £0 | Anyone without debt blocks (debt over 28 days can block a switch) **[unverified]** | 18% switched supplier in the prior 12 months (2018) | Same pool as fixed tariff | 5 |
| Economy 7 / time-of-use (ToU) | Depends on shiftable load. Gains only if off-peak share is above about 40% **[unverified]** | £0 if smart; old E7 needs a meter swap | Storage heater, EV or heat pump homes, or homes with high shiftable load | Not found | Assume 4m with large shiftable load lacking ToU **[unverified]** | 4 |
| EV tariff | £300 to £600/yr vs flat rate for about 8,000 miles **[unverified]** | £0 if a smart charger is present | EV owners with home charging. 93% of EV drivers can charge at home | 52% of EV drivers have smart chargers; EV tariff take-up not published | 1.737m zero-emission cars × 95% home charge × 50% not on EV tariff **[unverified]** ≈ **0.8m** | 4 |
| Heat pump tariff | £100 to £250/yr vs flat rate **[unverified]** | £0 | Heat pump homes (80,098 BUS-funded plus earlier installs) | Not found | about 0.4m heat pump homes × 60% not on HP tariff ≈ **0.25m [unverified]** | 4 |
| Export tariff / SEG choice | Market range **2p to 25p/kWh**. Moving from 2p to 15p on 1,500 kWh exported ≈ **£195** [derived; export volume unverified] | £0. Better rates often need supply with the same firm | PV owners with an export-capable smart meter | MCS-certified PV about 120,000 installs in H1 2025 alone | about 1.7m PV homes × 50% on a poor rate ≈ **0.85m [unverified]** | 5 |
| Dual fuel / paperless | Typically £0 to £30/yr discount **[unverified]** | £0 | Gas homes | Not found | Small | 5 |
| Warm Home Discount (WHD) | **£150** rebate | £0 | Pension Credit Guarantee Credit (Core Group 1, about 983k); other means-tested benefits (Core Group 2, 4.53m E&W, expanded 2025/26) | **5.52m** core rebates in 2025/26; about 5.7m incl. Scotland; **96% automatic** | Under 0.3m, mostly Scotland Broader Group and data-match failures **[unverified]** | 4 to 5 |
| Supplier hardship funds | Case by case; usually several hundred £ of debt relief **[unverified]** | £0; application plus income evidence | Struggling households; often open to non-customers | Not found | Linked to debt pool: £4.4bn arrears | 3 |
| Ofgem debt relief scheme | Write-off of arrears for people on means-tested benefits owing over £100 | £0 | about 195,000 households, first phase early 2026 | Phase 1 rolling out | about 0.2m | 4 (supplier-led) |
| Priority Services Register (PSR) | Non-financial: passwords, meter reads, outage notice, tailored comms | £0 | People in vulnerable situations, incl. temporary vulnerability; networks also cover under-5s | About 13% of customers per fuel (2015, the latest figure I found) | Unknown; likely under-registered **[unverified]** | 5 |

Sources for A1 rows:
- Direct Debit vs standard credit and prepayment: [Ofgem Jan 2026 cap summary](https://www.ofgem.gov.uk/sites/default/files/2025-11/Summary-of-changes-to-energy-price-cap-1-January-to-31-March-2026.pdf)
- 70% on SVT and £160 detriment: [CMA](https://www.gov.uk/government/news/cma-sets-out-case-for-energy-market-reform)
- 18% switched supplier: [Ofgem Consumer Engagement Survey 2018](https://www.ofgem.gov.uk/system/files/docs/2018/10/consumer_engagement_survey_2018_report_0.pdf)
- Collective-switch savings: [Ofgem collective switch slides](https://www.ofgem.gov.uk/sites/default/files/docs/2019/09/collective_switch_slides_for_publication.pdf)
- EV home charging and smart chargers: [DfT EV driver survey](https://assets.publishing.service.gov.uk/media/628f5603d3bf7f037097bd73/dft-ev-driver-survey-summary-report.pdf)
- 1.737m zero-emission cars: [DfT vehicle licensing 2025](https://www.gov.uk/government/statistics/vehicle-licensing-statistics-2025/vehicle-licensing-statistics-united-kingdom-2025)
- 80,098 BUS-funded systems: [Ofgem BUS annual report](https://www.ofgem.gov.uk/transparency-document/boiler-upgrade-scheme-annual-report-april-2025-march-2026)
- SEG range and same-supplier conditions: [MSE SEG table](https://www.moneysavingexpert.com/utilities/best-solar-rates-seg-tariffs)
- 120,000 PV installs H1 2025: [MCS](https://mcscertified.com/record-number-of-renewables-being-installed-into-uk-homes/)
- WHD: [DESNZ WHD statistics 2025/26](https://www.gov.uk/government/statistics/warm-home-discount-statistics-2025-to-2026/warm-home-discount-statistics-2025-to-2026)
- Hardship funds: [MSE grants](https://www.moneysavingexpert.com/family/grant-grabbing)
- Debt relief and £4.4bn arrears: [Big Issue on Ofgem debt relief](https://www.bigissue.com/news/social-justice/ofgem-energy-bill-debt-relief-scheme/)
- PSR: [Ofgem PSR](https://www.ofgem.gov.uk/press-release/more-customers-vulnerable-situations-receive-help-under-priority-services-register)

**Social tariffs:** GB has no mandated energy social tariff as of this pack. WHD is the main bill rebate. I found no 2026 source confirming any new social tariff **[unverified]**.

**Debt allowance:** unpaid balances are recovered through a debt allowance of about **£52/yr** on every capped bill ([Big Issue](https://www.bigissue.com/news/social-justice/ofgem-energy-bill-debt-relief-scheme/)).

### A2. Grants (the gateway layer)

| Scheme | Status (Oct 2026) | Value | Eligibility / applicability | Delivered | Source |
|---|---|---|---|---|---|
| Boiler Upgrade Scheme (BUS), E&W | Confirmed to **2030**. Being expanded to **air-to-air heat pumps and heat batteries (TESS)** | Up to £7,500 heat pump; MCS installer applies | Owners only (incl. landlords); MCS installer required | Scheme Year 4 (2025/26): 39,435 vouchers issued; £233.1m paid for 31,104 systems. Cumulative **80,098 systems, £560.3m; 97.6% air-source** | [MCS](https://mcscertified.com/warm-homes-plan-key-takeaways-for-the-small-scale-renewables-sector/); [MSE](https://www.moneysavingexpert.com/family/grant-grabbing); [Ofgem BUS annual report](https://www.ofgem.gov.uk/transparency-document/boiler-upgrade-scheme-annual-report-april-2025-march-2026) |
| ECO4 | Extended to **31 Dec 2026** for orderly close; no new funding; **no successor supplier obligation** | Full measures for low-income homes | Low income plus poor EPC | about 949,800 measures in about 280,100 households to Sep 2025; 4.4m measures in 2.6m homes since 2013 | [DESNZ government response](https://assets.publishing.service.gov.uk/media/697258453f2908a34904057c/extending-eco4-end-date-government-response.pdf) |
| Great British Insulation Scheme (GBIS) | **Ended 31 Mar 2026**; delivery "not met expectations" | Single insulation measures | Council tax A to D/E plus low income | No figures given | [DESNZ](https://assets.publishing.service.gov.uk/media/697258453f2908a34904057c/extending-eco4-end-date-government-response.pdf) |
| Warm Homes Plan | Launched 20 Jan 2026; about £15bn. **£5bn** for no-cost upgrades for low-income homes; £1.5bn extra low-income grant; government-backed **zero and low interest loans**; "universal offer" | Varies | Low-income detail due Spring 2026, so a funding gap is possible | Target up to 1m families out of fuel poverty by 2030 | [CIC](https://www.cic.org.uk/news/governments-warm-homes-plan-finally-released); [MCS](https://mcscertified.com/warm-homes-plan-key-takeaways-for-the-small-scale-renewables-sector/); [DESNZ](https://assets.publishing.service.gov.uk/media/697258453f2908a34904057c/extending-eco4-end-date-government-response.pdf) |
| Warm Homes: Local Grant (England) | Live via councils | Insulation, heat pumps, solar, smart controls | Low income, EPC D to G, eligible postcodes | Not found | [MSE](https://www.moneysavingexpert.com/family/grant-grabbing) |
| Home Energy Scotland Grant and Loan | Live | Up to **£7,500** heat pump (**£9,000** rural or island) plus optional interest-free loan | Homeowners | Not found | [MSE](https://www.moneysavingexpert.com/family/grant-grabbing) |
| Warmer Homes Scotland | Live | Up to £7,500 (£9,000 rural); one MSE section says £10,000, so check the current amount | Certain benefits, or over 75 with no working heating | Not found | [MSE](https://www.moneysavingexpert.com/family/grant-grabbing) |
| Nest (Wales) | Live | Free insulation, solar or heat pump | Owner or PRS, EPC D or below, low income plus means-tested benefit plus a respiratory, circulatory or mental health condition | Not found | [MSE](https://www.moneysavingexpert.com/family/grant-grabbing) |

**Quality warning:** the NAO estimated **98%** of homes with external wall insulation under ECO4 and GBIS had major issues needing remediation, as reported by [CIC](https://www.cic.org.uk/news/governments-warm-homes-plan-finally-released). This is a trust barrier for any supplier-badged fabric offer.

**PRS rules (England & Wales):** all domestic private rented tenancies must reach **EPC C equivalent by 1 Oct 2030**.
- The landlord cost cap is **£10,000**. Homes worth under £100k have a cap of 10% of value.
- Compliance needs fabric performance, plus either heating efficiency or smart readiness.
- The maximum fine is £30,000 per property.
- Landlord spend from Oct 2025 counts toward the cap.
- Source: [Elmhurst](https://www.elmhurstenergy.co.uk/blog/2026/01/22/domestic-private-rented-properties-required-to-meet-epc-band-c-by-october-2030/).

This turns about 19% of homes ([EHS](https://www.gov.uk/government/statistics/chapters-for-english-housing-survey-2024-to-2025-headline-findings-on-demographics-and-household-resilience/introduction-and-key-findings)) into a **landlord-decided** market for fabric and heating. Renters keep control of tariff, behaviour and plug-in measures.

### A3. Barriers, hassle, observability, supplier role, evidence

| Measure | Main barriers | Household time and hassle | Supplier can observe | Supplier role | Evidence |
|---|---|---|---|---|---|
| Direct Debit switch | Fear of overdraft; irregular income | about 10 to 20 min online **[unverified]** | Account | Tariff (default offer, prompt) | Regulated price gap (cap methodology) |
| Fixed or switch | Hassle, distrust, uncertainty about savings (see the 47% and 25% figures in §9) | Process: 21 days actual, 17 days perceived. Effort: 20 to 40 min **[unverified]** | Account | Tariff; retention; auto-roll to best tariff | Trial-measured: collective switch RCT |
| ToU / EV / HP tariff | Fear of peak penalties; need a smart meter; complexity | 30 min to choose; ongoing scheduling unless automated **[unverified]** | HH-visible: EV and heat pump signatures, off-peak share | Tariff; device integration | Modelled or claimed **[unverified]** |
| SEG choice | Lock-in to supply; rates change every 12 months | 20 to 60 min plus MCS certificate retrieval **[unverified]** | HH-visible: export registers; Account | Tariff; bundle | Market data (MSE) |
| WHD | Data-match failure; Scotland needs applications | Usually 0 (automatic); about 30 min helpline otherwise **[unverified]** | Account (core list) | Grant gateway (mandated) | Administrative stats |
| Hardship / debt | Stigma; evidence burden | 1 to 3 h incl. income and expenditure form **[unverified]** | Account: arrears, self-disconnection on PPM | Advise; fund; refer | Administrative |
| PSR | Unawareness | 5 to 10 min | Ask (health); HH-visible: self-disconnection | Register; data share with network | Administrative |
| BUS / grants | Eligibility confusion, installer scarcity, scheme churn (GBIS ended; ECO closing) | See heat pumps (§E) | Ask: tenure, EPC | Grant gateway; installer partner | Administrative |

---

## B. Behaviour at zero capital

### B1. Value and market

| Measure | £/yr (carbon) | Applicability | Current uptake | Remaining addressable | Ease |
|---|---|---|---|---|---|
| Thermostat down 1°C | **£90** (EST, 2024 prices) | Any home with a room thermostat or controllable heating | Not found | Assume half have headroom: 27.8m × 50% ≈ **13.9m [unverified]** | 4 (comfort cost) |
| Heating schedule (shorter or matched to occupancy) | 5 to 10% of heating **[unverified]** | Programmer or smart controls | Not found | about 13.9m [unverified] | 4 |
| Room-by-room heating via TRVs | Linked to the TRV installation saving (£35; §C) | Rooms with TRVs | Not found | — | 4 |
| Boiler flow temperature to 50 to 60°C | Lab and modelled: **8 to 9%** gas saving (80→60°C). RCT measured only **0.4%** because the control group had often already lowered it. At about 11,500 kWh gas **[unverified]** × 7.97p, 8% ≈ £73 ceiling [derived]; working figure £40 **[unverified]** | Condensing gas boiler homes (about 22.8m gas-connected) | **64%** of survey respondents had lowered it at some point (self-selected sample) | 22.8m × 36% ≈ **8.2m** [derived; the 64% may be biased upward] | 4 |
| Hot water timing and cylinder setpoint (60°C, legionella-safe) | £20 to £40 **[unverified]** | Homes with a cylinder | Not found | 40% of homes have a cylinder **[unverified]** → about 11m | 4 |
| Shower time to 4 min | £50 to £70 per household of four **[unverified]** | All | Not found | about 13.9m [unverified] | 4 |
| Wash at 30°C / fewer cycles | £15 to £30 **[unverified]** | All | Not found | about 13.9m [unverified] | 5 |
| Tumble dryer avoidance (line or airer) | £50 to £100 for regular users **[unverified]** | Homes with dryer plus drying space (flats limited; damp risk) | Not found | Dryer ownership about 55% **[unverified]** → about 7m | 4 |
| Cooking (microwave, air fryer, lids) | £20 to £50 **[unverified]** | All | Not found | — | 5 |
| Standby off | £40 to £55 **[unverified]**; an EST figure is commonly cited but I could not fetch it | All | Not found | about 13.9m [unverified] | 5 |
| Close curtains at night | Not quantified by EST | All | Not found | — | 5 |
| Load shifting / Demand Flexibility Service (DFS) events | **Small.** 2024/25: 1.98m registrations, 44 events, 3,917.7 MWh shifted, £943,983 to providers ≈ **£0.48 per registrant** [derived]. Over 620 tCO2 saved | Smart meter in smart mode (71% of homes) | 1.98m registered | 27.8m × 71% − 1.98m ≈ **17.8m** [derived] | 4 |

Sources:
- Thermostat, curtains, standby: [EST](https://energysavingtrust.org.uk/energy-saving-budget?loc=wales)
- Flow temperature: [Nesta RCT](https://www.nesta.org.uk/report/the-impact-of-boiler-optimisation-on-gas-consumption-and-household-comfort)
- Gas price: [Ofgem](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026)
- Gas-connected homes and smart mode: [DESNZ](https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin)
- DFS: [NESO](https://www.neso.energy/nearly-2-million-households-and-businesses-registered-demand-flexibility-service-dfs-last-winter)

**DFS behaviour evidence** ([NESO consumer research](https://www.neso.energy/news/demand-flexibility-service-consumers-have-their-say)), covering 2022/23:
- About 1.6m participated.
- 62% were satisfied and 83% would take part again.
- 85% heard via their supplier.
- The main motive was bills: 65% of struggling households and 43% of comfortable ones.
- Strategies were roughly equal between cutting use (38.7%) and planning around events (38.3%).

DFS became a year-round, merit-based service in 2024/25 ([NESO](https://www.neso.energy/nearly-2-million-households-and-businesses-registered-demand-flexibility-service-dfs-last-winter)).

### B2. Barriers, hassle, observability, role, evidence

| Measure | Barriers | Hassle (one-off / ongoing) | Supplier can observe | Supplier role | Evidence |
|---|---|---|---|---|---|
| Thermostat −1°C | Comfort; health risk for vulnerable people | 1 min / ongoing comfort | HH-visible: gas profile shape and degree-day regression | Advise; nudge | Modelled (EST) |
| Flow temperature | Knowledge; fear of breaking the boiler; combi vs system differences | 15 to 30 min with a guide **[unverified]** | HH-visible: changes in gas cycling may be detectable **[unverified]** | Advise; engineer visit | **Trial-measured** (60,468-customer RCT: 0.4%) vs lab 8 to 9% |
| Hot water / shower | Habit; household negotiation | Minutes; ongoing | HH-visible: electric showers and immersions show as spikes; gas showers are blurred | Advise; feedback | Modelled **[unverified]** |
| Laundry / dryer / cooking | Habit; space for drying | Ongoing minutes | HH-visible: dryer and oven signatures (disaggregation) | Advise; appliance insights | Modelled **[unverified]** |
| Standby | Low salience | 30 min audit with smart plugs | HH-visible: overnight baseload | Advise; baseload alert | Modelled **[unverified]** |
| DFS / load shift | Low reward; effort at teatime peak | Per event 5 to 15 min manual; near zero if automated **[unverified]** | HH-visible (settlement-grade) | Tariff; aggregator; automation | **Trial-measured** (NESO delivery data) |

---

## C. Low-cost measures

| Measure | £/yr | Upfront | Applicability | Uptake | Remaining addressable | Ease |
|---|---|---|---|---|---|---|
| Draught-proofing (windows and doors) | **£40**; plus £55 for a chimney excluder | £50 to £250 DIY **[unverified]** | All. Renters can do reversible strips | Not found | 27.8m × 50% ≈ **13.9m [unverified]** | 4 |
| LEDs | £2 to £3 per bulb per year **[unverified]** | £2 to £5 per bulb **[unverified]** | All | High; most homes partial **[unverified]** | 30% of homes with material non-LED stock ≈ 8m **[unverified]** | 5 |
| Cylinder jacket | **£40** | £15 to £25 **[unverified]** | Homes with an uninsulated cylinder | Most cylinders already factory-foamed **[unverified]** | about 0.6m **[unverified]** | 5 |
| Radiator reflector panels | £10 to £25 **[unverified]** | £20 to £50 **[unverified]** | Radiators on uninsulated external walls | Not found | — | 4 |
| Smart thermostat | Claims 5 to 10% of heating **[unverified]**. Compare EST full controls: £860 cost, about £110/yr | £150 to £250 plus install **[unverified]** | Boiler or heat pump homes; renter needs consent for wired units | Not found | — | 3 to 4 |
| TRVs (if programmer and thermostat exist) | **£35** | about £510 installed | Wet systems | Not found | — | 3 |
| Smart plugs | £5 to £30 **[unverified]** | £10 to £15 each | All | Not found | — | 5 |
| Efficient shower head (mixer/combi only, not electric showers) | £20 to £70 incl. water bills on a water meter **[unverified]** | £15 to £40; often free from water companies **[unverified]** | Mixer showers | Not found | — | 5 |
| Thermal or heavy curtains | Not quantified by EST | £30 to £150 **[unverified]** | All | Not found | — | 5 |
| Working smart meter plus in-home display (IHD) | 2 to 3% via feedback **[unverified]**; mainly an **enabler** for ToU, DFS and SEG | £0 (supplier-funded) | All supply points; some comms dead-spots | Electricity: **75%** smart, 71% in smart mode; 3.1m smart meters (all fuels) in traditional mode | Electricity: 25% non-smart + 3.8% traditional mode ≈ 28.8% × 27.8m ≈ **8.0m** [derived] | 4 |

Sources:
- Draught-proofing, cylinder jacket, controls, TRVs: [EST](https://energysavingtrust.org.uk/energy-saving-budget?loc=wales)
- Smart meters: [DESNZ](https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin)

**Barriers and hassle (C group):**
- **DIY confidence and the "small saving, not worth it" effect.** These items are low-salience. Hassle is 0.5 to 3 hours DIY **[unverified]**.
- **Smart meter:** half-day appointment window plus install time, about 2 hours **[unverified]**, and recurring trust or health myths **[unverified]**.
- **Observability:** baseload drop (LEDs, standby) is HH-visible. Heating savings from draught-proofing are visible only via weather-normalised gas regression. Cylinder, jacket and shower type must be asked.
- **Supplier role:** advise; ship kits (draught strips, smart plugs, shower heads) bundled with outreach; install smart meter (a core obligation); offer a smart thermostat as a tariff bundle.
- **Evidence:** modelled (EST) for most rows; claimed (manufacturer) for smart thermostats.

---

## D. Fabric

One £ figure each, per brief.

| Measure | £/yr | Upfront | Applicability | Uptake | Remaining addressable (arithmetic) | Ease |
|---|---|---|---|---|---|---|
| Loft insulation (0→270mm) | **£230** (top-ups from 100 to 200mm save much less: blended £60 **[unverified]**) | up to £950 | Houses and top-floor flats with an accessible loft | **42%** of dwellings have over 200mm | (80% with loft **[unverified]** − 42%) × 27.8m ≈ **10.6m** | 3 (loft clearance is the hidden hassle) |
| Cavity wall insulation | **£240** | up to £1,700 | Unfilled cavities, not exposed or flood-risk | Walls insulated (cavity + solid) **54%** | Unfilled easy cavities about 2.5m **[unverified]**; HEE statistics not fetched | 3 (1 day, outside work) |
| Solid wall: internal (IWI) or external (EWI) | £300 **[unverified]** | £8k to £15k EWI; IWI £7k to £14k plus room loss **[unverified]** | Solid-wall homes. EWI is restricted in conservation areas and on listed buildings; IWI is disruptive. 98% of ECO/GBIS EWI had major issues | Low (under 10% of solid-wall homes) **[unverified]** | about 7m solid-wall × 93% ≈ **6.5m [unverified]** | 1 |
| Floor insulation (suspended timber) | £50 to £100 **[unverified]** | £1k to £3k **[unverified]**; robotic spray options | Suspended timber floors | Low **[unverified]** | Not estimated | 2 |
| Double/triple glazing (replacing single) | £100 to £150 **[unverified]** | £5k to £10k **[unverified]** | Single-glazed remainder; listed buildings need consent | **89%** fully double-glazed | 11% × 27.8m ≈ **3.1m** | 2 |
| Secondary glazing | £50 to £100 **[unverified]** | £300 to £800 per window **[unverified]** | Listed or conservation homes; renters (removable film) | Not found | Subset of 3.1m | 3 |
| Insulated external doors | £20 to £50 **[unverified]** | £500 to £1,500 **[unverified]** | All houses | Not found | Not estimated | 3 |

Sources:
- Loft and cavity figures: [EST](https://energysavingtrust.org.uk/energy-saving-budget?loc=wales)
- Loft, wall and glazing shares: [EHS](https://www.gov.uk/government/statistics/chapters-for-english-housing-survey-2024-to-2025-headline-findings-on-housing-quality-and-energy-efficiency/introduction-and-key-findings)
- EWI quality: [CIC/NAO](https://www.cic.org.uk/news/governments-warm-homes-plan-finally-released)

**Applicability modifiers:**
- **Tenure:** in PRS the landlord decides; the 2030 EPC C rule now creates a deadline ([Elmhurst](https://www.elmhurstenergy.co.uk/blog/2026/01/22/domestic-private-rented-properties-required-to-meet-epc-band-c-by-october-2030/)). Social homes are decided by housing associations.
- **Flats:** shared walls and roofs need freeholder and building consent **[unverified]**.
- **Barriers:** cost; disruption (loft clearance, decorating after IWI); trust after the ECO and Green Deal problems ([CIC](https://www.cic.org.uk/news/governments-warm-homes-plan-finally-released)); split incentives; scheme churn. GBIS ended and ECO4 closes Dec 2026 ([DESNZ](https://assets.publishing.service.gov.uk/media/697258453f2908a34904057c/extending-eco4-end-date-government-response.pdf)).
- **Hassle [unverified]:** about 3 to 6 h of research and quotes; 1 visit for survey; 0.5 to 1 day install for loft or cavity; 3 to 10 days for EWI with scaffolding; 1 to 3 weeks of room disruption for IWI.
- **Observability:** weather-normalised gas reduction is HH-visible after the event. The pre-state must be **asked** or taken from the EPC register.
- **Supplier role:** grant gateway (Warm Homes Plan low-income, Local Grant referrals); partner with a vetted installer; finance via government-backed low-interest loans ([MCS](https://mcscertified.com/warm-homes-plan-key-takeaways-for-the-small-scale-renewables-sector/)); landlord compliance service for the 2030 PRS deadline.
- **Evidence:** NEED-measured savings exist for loft and cavity (NEED dataset not fetched **[unverified]**); others are modelled.

---

## E. Heating systems

| Measure | £/yr (carbon) | Upfront (net of grant) | Applicability | Uptake | Remaining addressable | Ease |
|---|---|---|---|---|---|---|
| Boiler service / optimisation | £0 to £50 **[unverified]** | £80 to £120/yr **[unverified]** | Gas or oil boiler homes | Not found | — | 4 |
| Replace non-condensing boiler | £200 to £300 **[unverified]** | £2.5k to £4k **[unverified]** | Pre-2005 boilers | Small residual **[unverified]** | about 1.5m **[unverified]** | 3 |
| Full heating controls | **£110** | about £860 | Wet systems without full controls | Not found | about 3m **[unverified]** | 3 |
| Air-source heat pump (ASHP) | Running cost vs gas about −£100 to +£300, highly tariff- and design-dependent **[unverified]**; carbon about 2 tCO2/yr **[unverified]** | Gross £10k to £14k **[unverified]**, minus £7,500 BUS → £3k to £6k net | Owner-occupied (BUS); outdoor space needed. EoH: 8% lacked external space; 15% needed efficiency upgrades | Cumulative BUS-funded **80,098 (97.6% air-source)**; about 30,000 MCS heat pump installs in H1 2025. Owner-occupiers likely to install: 22% | Owner-occupied 65% × gas 82% × 27.8m ≈ 14.8m × 90% feasible ≈ 13.3m − about 0.3m installed ≈ **13.0m** [derived; feasibility unverified] | 1 |
| Ground-source heat pump (GSHP) | Higher efficiency than ASHP **[unverified]** | £20k to £35k gross **[unverified]** | Land for loops or boreholes | Small share of BUS (non-ASHP 2.4% incl. biomass) | Under 2m **[unverified]** | 1 |
| Hybrid heat pump | Partial gas displacement **[unverified]** | £6k to £10k **[unverified]** | Gas homes where full heat pump is hard | Not found; awareness 52%, likely 14% | — | 2 |
| Heat battery (e.g. Sunamp) | Enables ToU shifting for hot water **[unverified]** | £2k to £4k **[unverified]** | Combi homes lacking cylinder space | Not found; **being added to BUS** | — | 3 |
| High-heat-retention storage heaters | Vs old storage heaters about £150 to £400 on ToU **[unverified]** | £1k to £2k per room **[unverified]** | Electric-heated flats; off-gas; PRS | Not found | about 1.5m electric-heated homes **[unverified]** | 3 |
| District heat connection | Regulated by Ofgem from 2026 **[unverified]** | Usually developer-led | Heat network zones; flats | about 2 to 3% **[unverified]** | Not estimated | 1 (no household choice in most cases) |
| Air-to-air heat pump | Cooling plus heating **[unverified]** | £1.5k to £4k per head **[unverified]** | Flats or electric-heated homes | Not found; **BUS eligibility being added** | — | 3 |
| Remove gas entirely (cap the meter) | Gas standing charge **£108.33/yr** [derived] plus boiler servicing; needs heat pump plus induction | £0 to £500 disconnection **[unverified]** | Only after full electrification | Not found | about 0.3m heat pump homes still on gas **[unverified]** | 2 |

Sources:
- Heating controls: [EST](https://energysavingtrust.org.uk/energy-saving-budget?loc=wales)
- BUS: [Ofgem BUS annual report](https://www.ofgem.gov.uk/transparency-document/boiler-upgrade-scheme-annual-report-april-2025-march-2026); [MCS](https://mcscertified.com/warm-homes-plan-key-takeaways-for-the-small-scale-renewables-sector/)
- Electrification of Heat (EoH) project findings: [Homebuilding/EoH](https://www.homebuilding.co.uk/news/disruption-during-heat-pump-installation-is-main-barrier-to-uptake-says-report)
- MCS installs H1 2025: [MCS](https://mcscertified.com/record-number-of-renewables-being-installed-into-uk-homes/)
- Awareness and likelihood to install: [PAT](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-heat-and-energy-use-in-the-home-winter-2025-uk)
- Tenure and gas share: [EHS](https://www.gov.uk/government/statistics/chapters-for-english-housing-survey-2024-to-2025-headline-findings-on-demographics-and-household-resilience/introduction-and-key-findings); [DESNZ](https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin)
- Gas standing charge: [Ofgem](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026)

**Heat pump barriers (owner-occupiers unlikely to install)** ([PAT Winter 2025](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-heat-and-energy-use-in-the-home-winter-2025-uk)):

| Barrier | Share |
|---|---|
| Installation cost | 51% |
| Not feasible in their home | 36% |
| Running costs | 35% |
| Waiting for the technology to develop | 34% |
| Content with current system | 34% |
| Performance concerns | 31% |
| Lack of knowledge | 29% |

- 30% "don't know enough" to decide on air-source, up from 21% in 2021.
- About 60 to 64% of renters say the decision is not theirs.

**Disruption:** 47% of EoH decliners cited disruption as the main barrier ([EoH](https://www.homebuilding.co.uk/news/disruption-during-heat-pump-installation-is-main-barrier-to-uptake-says-report)).

**Lead time and problems** ([Nesta user survey](https://nesta.org.uk/report/heat-pumps-a-user-survey)):
- Most common time from agreement to installation: 1 to 2 months for a heat pump, vs under a month for a boiler.
- 63% of heat pump users reported installation problems (vs 24% for boilers). Of those, 36% cited disruption and 19% delays.
- 13% of heat pump purchases were distress purchases, vs 48% for boilers. This is the core mismatch: boilers are mostly replaced in a breakdown.
- 73% were as satisfied or more satisfied than with the old system ([Nesta](https://nesta.org.uk/report/heat-pumps-a-user-survey)); [Which?](https://www.which.co.uk/reviews/ground-and-air-source-heat-pumps/article/what-its-really-like-to-have-a-heat-pump-aa4Ek3X3T7qI) cites 81% for owners who had their own installed.

**Hassle estimate for an ASHP [unverified]:**
- 10 to 20 h research, surveys and quotes.
- 1 to 2 home surveys.
- 2 to 5 days install, longer if radiators are changed.
- Ongoing: learning low-and-slow operation.

**Observability:** heat pump signature (cold-weather electricity load, defrost cycles) is HH-visible; gas drop to zero is HH-visible. Boiler age and controls must be asked.

**Supplier role:** install directly or via a partner (an obligated-supplier model exists in the market), HP tariff, BUS gateway (the installer applies), finance (government-backed loans), and **distress-purchase readiness**: pre-surveyed homes so a broken boiler can become a heat pump.

**Evidence:** EoH field trial (742 installs); Nesta survey; savings largely modelled.

---

## F. Generation and storage

| Measure | £/yr | Upfront | Applicability | Uptake | Remaining addressable | Ease |
|---|---|---|---|---|---|---|
| Solar PV (about 4 kWp) | £300 to £500 incl. SEG **[unverified]**; SEG spread 2p to 25p | £5k to £8k **[unverified]**; new builds solar by default (Future Homes Standard) | Owner-occupied; suitable roof (orientation, shading); conservation-area and listed limits; flats rarely | about 120,000 MCS installs H1 2025 (+36% year on year; record); stock about 1.7m **[unverified]** | 65% owner × 75% houses **[unverified]** × 60% suitable roof **[unverified]** × 27.8m ≈ 8.1m − 1.7m ≈ **6.4m [unverified]** | 2 |
| Solar diverter | £50 to £150 **[unverified]** | £300 to £500 **[unverified]** | PV plus hot water cylinder | Not found | Under 0.5m **[unverified]** | 4 |
| Home battery | £150 to £400 with ToU arbitrage **[unverified]** | £3k to £6k **[unverified]** | PV or ToU homes; space | about 20,000 MCS installs H1 2025 (+130%) | PV homes without battery about 1.5m **[unverified]** | 3 |
| Solar thermal | £50 to £100 **[unverified]** | £3k to £6k **[unverified]** | Cylinder; competes with PV plus diverter | Low **[unverified]** | Niche | 2 |
| Vehicle-to-grid (V2G) | £300 to £800 on V2G tariffs **[unverified]** | Bidirectional charger £3k to £6k **[unverified]** | Compatible EV plus off-street parking | Very low **[unverified]** | Niche | 2 |

Sources:
- SEG spread: [MSE](https://www.moneysavingexpert.com/utilities/best-solar-rates-seg-tariffs)
- Future Homes Standard: [MCS](https://mcscertified.com/warm-homes-plan-key-takeaways-for-the-small-scale-renewables-sector/)
- PV and battery installs: [MCS](https://mcscertified.com/record-number-of-renewables-being-installed-into-uk-homes/)

**Barriers:** upfront cost (now eligible for government-backed loans ([MCS](https://mcscertified.com/warm-homes-plan-key-takeaways-for-the-small-scale-renewables-sector/))); mis-selling distrust **[unverified]**; DNO notification for larger systems or batteries **[unverified]**; and SEG lock-in to supply, since the best rates require taking supply from the same firm ([MSE](https://www.moneysavingexpert.com/utilities/best-solar-rates-seg-tariffs)).

**Hassle [unverified]:** 5 to 10 h research and quotes; 1 to 2 days install with scaffolding; ongoing app monitoring.

**Observability:** export and import half-hourly data make PV and battery behaviour HH-visible. Roof suitability needs an aerial or LiDAR lookup or a question.

**Supplier role:** install or partner (Type 1 installer-linked SEG at 15 to 25p ([MSE](https://www.moneysavingexpert.com/utilities/best-solar-rates-seg-tariffs))); export tariff; battery optimisation as a service (VPP); finance.

**Evidence:** deployment is administrative; savings are modelled.

---

## G. Transport

| Measure | £/yr (carbon) | Upfront | Applicability | Uptake | Remaining addressable | Ease |
|---|---|---|---|---|---|---|
| Switch to EV | Fuel saving £600 to £1,000 at home off-peak **[unverified]**; about 1.5 tCO2/yr **[unverified]** | Premium over ICE about £0 to £5k **[unverified]** (used EVs narrow it) | Car-owning households; **68%** of English households have or could have off-street parking | **1,737,000** zero-emission cars = 5.0% of 34.5m; ZEV share of new registrations 23% (2025) | Car households about 77% **[unverified]** × 68% × 27.8m ≈ 14.6m − about 1.6m EV households ≈ 13m; at the ownership-change rate ≈ **10m [unverified]** | 2 |
| Home charger | Enables EV tariffs | £800 to £1,200 **[unverified]** | Off-street parking; flats need freeholder consent | **93%** of EV drivers can charge at home; 52% have a smart charger; 28% a non-smart charger | EV drivers without a smart charger ≈ 48% × 1.7m ≈ **0.8m** [derived] | 3 |
| Smart charging (managed) | £300 to £600 vs peak or flat **[unverified]** | £0 with smart charger | Smart charger plus smart meter | **76%** of smart-charger owners use it always or mostly | about 0.2m **[derived]** | 5 |
| Public charging | Higher cost per kWh than home **[unverified]** | £0 | 32% without off-street parking | Not found | — | 3 (ongoing hassle) |

Sources:
- Off-street parking 68%: [RAC Foundation](https://www.racfoundation.org/research/mobility/still-standing-still)
- EV stock and registrations: [DfT vehicle licensing](https://www.gov.uk/government/statistics/vehicle-licensing-statistics-2025/vehicle-licensing-statistics-united-kingdom-2025)
- Home charging and smart chargers: [DfT EV survey](https://assets.publishing.service.gov.uk/media/628f5603d3bf7f037097bd73/dft-ev-driver-survey-summary-report.pdf). The survey is non-probability and unweighted.
- Off-street parking among EV drivers: 95% vs 68% in the general population, so adoption is concentrated where parking exists ([DfT](https://assets.publishing.service.gov.uk/media/628f5603d3bf7f037097bd73/dft-ev-driver-survey-summary-report.pdf); [RAC Foundation](https://www.racfoundation.org/research/mobility/still-standing-still)).

**Observability:** an EV charging signature (7 kW blocks) is HH-visible, so the supplier can **detect** EV owners not on an EV tariff.

**Supplier role:** EV tariff; charger install partner; managed-charging API; V2G pilots.

**Evidence:** DfT survey for behaviour; savings modelled.

---

## H. Appliances (usually only at end of life)

| Measure | £/yr | Upfront | Applicability | Remaining addressable | Ease |
|---|---|---|---|---|---|
| A-rated fridge-freezer (replacing a 15-year-old unit) | £40 to £80 **[unverified]** | £400 to £800 **[unverified]** | Old units | about 3m **[unverified]** | 4 |
| Induction hob (gas homes) | About neutral to slightly negative vs gas at the Oct 2026 cap (26.32p vs 7.97p/kWh); value is via **gas disconnection** (£108/yr standing charge), plus air quality | £400 to £1,000 plus possible wiring **[unverified]** | Gas hob homes | about 5m **[unverified]** | 3 |
| Heat-pump tumble dryer | £40 to £80 vs vented or condenser for regular users **[unverified]** | about £300 premium **[unverified]** | Dryer replacers | about 3m/yr pool **[unverified]** | 4 |

Sources:
- Unit rates: [Ofgem](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026)
- Gas standing charge: [Ofgem](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026), derived

**Notes for the H group:**
- **Observability:** fridge cycling and dryer use are HH-visible via disaggregation **[unverified]**.
- **Supplier role:** advise, plus retail partner or finance.
- **Evidence:** modelled or claimed.

---

## 9. GB evidence on time and hassle in energy decisions

### Hassle as a stated barrier
- **Ofgem Consumer Engagement Survey 2018** ([Ofgem](https://www.ofgem.gov.uk/system/files/docs/2018/10/consumer_engagement_survey_2018_report_0.pdf)):
  - 47% agree "switching is a hassle that I've not got time for".
  - 28% say switching takes too long.
  - Among the non-engaged, 25% cite "too much hassle" (15% in the Key facts section) and 7% "too complicated".
  - 46% had not switched supplier or tariff in four years.
- **CMA (2015 provisional findings):**
  - About 70% were on SVTs.
  - Over 34% had "never considered switching".
  - Barriers included perceived difficulty of switching and confusing bills.
  - Source: [CMA](https://www.gov.uk/government/news/cma-sets-out-case-for-energy-market-reform).
- **DESNZ PAT Winter 2025:** for low-carbon heating, 29% cite lack of knowledge and 30% "don't know enough" ([PAT](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-heat-and-energy-use-in-the-home-winter-2025-uk)). The page does not report disruption as a coded barrier.
- **EoH project:** disruption is the main barrier for 47% of those who declined a heat pump ([EoH](https://www.homebuilding.co.uk/news/disruption-during-heat-pump-installation-is-main-barrier-to-uptake-says-report)).
- **Nesta / BIT:** no explicit GB "hassle factor" quantification found within budget **[gap]**.

### Quantified time costs
- **Switching process:** 21 days actual (2018), 17 days perceived. 42% of never-switchers don't know how long it takes. 86% of switchers found it easy ([Ofgem 2018](https://www.ofgem.gov.uk/system/files/docs/2018/10/consumer_engagement_survey_2018_report_0.pdf)).
- **Heat pump lead time:** typically 1 to 2 months from agreement to installation, vs under a month for a boiler. 63% report installation problems ([Nesta](https://nesta.org.uk/report/heat-pumps-a-user-survey)).
- **Not found within budget [gap]:** call-centre waiting times; installation disruption days.

### Removing hassle works: trial evidence
- **Ofgem collective switch RCTs** (55k to 105k customers per trial) ([Ofgem](https://www.ofgem.gov.uk/sites/default/files/docs/2019/09/collective_switch_slides_for_publication.pdf)):
  - Design: customers did not need to sign up or supply data; they only had to make one contact.
  - Results: switching reached 24 to 29.5% vs control, about 7 to 10 times the baseline. Average savings were £150 to £298.
  - 72% used the phone, which suggests "done for you" must not be digital-only. It worked nearly as well for PSR customers.
- **WHD automatic matching** delivers to 96% of recipients with zero household effort ([DESNZ](https://www.gov.uk/government/statistics/warm-home-discount-statistics-2025-to-2026/warm-home-discount-statistics-2025-to-2026)).
- **The April 2026 levy cut** needed no customer action ([gov.uk](https://www.gov.uk/government/news/your-energy-bill-from-april-whats-changing)).
- **Advice alone does little:** month-specific flow-temperature advice gave only a 0.4% effect, and one-off advice no significant effect ([Nesta](https://www.nesta.org.uk/report/the-impact-of-boiler-optimisation-on-gas-consumption-and-household-comfort)).

### Willingness to pay to avoid hassle
- Commercial auto-switching services existed, such as Look After My Bills, which charged fees or took commission. The search surfaced reports that one service is no longer operating, but I did not verify fee levels or closure from a primary source **[unverified]**.
- I found no published GB stated-preference willingness-to-pay figure for avoiding energy hassle **[gap]**.
- The implicit evidence is strong: the CMA's £160 detriment ([CMA](https://www.gov.uk/government/news/cma-sets-out-case-for-energy-market-reform)) persisted for years among about 70% of customers. That implies a revealed hassle cost of at least £100 to £160/yr for the marginal non-switcher [derived inference].

---

## 10. Ranked shortlist: biggest value per hour of household effort

Value per hour = (£/yr, plus carbon at £250/t) ÷ one-off household hours. All hour figures are **[unverified]** assumptions.

| Rank | Measure | £/yr | Hours | £ per hour (yr 1) |
|---|---|---|---|---|
| 1 | Standard credit → Direct Debit | £136 | 0.25 | about £540 |
| 2 | Choose a better SEG tariff (PV owners) | about £195 | 0.75 | about £260 |
| 3 | EV owner moves to an EV tariff | about £400 | 1 | about £400 |
| 4 | Thermostat −1°C | £90 (+£60 carbon) | 0.1 setup, plus comfort | very high |
| 5 | Claim WHD where not automatic | £150 | 0.5 | about £300 |
| 6 | Move from SVT to a beating fix, or collective switch | £80 to £150 | 0.5 | about £160 to £300 |
| 7 | Boiler flow temperature | £20 to £70 | 0.5 | £40 to £140 |
| 8 | Register on the PSR (non-£, safety value) | — | 0.1 | n/a |
| 9 | Cylinder jacket | £40 | 0.5 | about £80 |
| 10 | DIY draught-proofing | £40 to £95 | 2 to 3 | about £20 to £40 |
| 11 | Loft top-up or cavity via grant | £60 to £240 | 4 to 8 | about £15 to £40 |
| 12 | ASHP | about £100 + £500 carbon | 20 to 40 | about £15 to £30 |

Sources for the £ figures:
- Rank 1: [Ofgem](https://www.ofgem.gov.uk/sites/default/files/2025-11/Summary-of-changes-to-energy-price-cap-1-January-to-31-March-2026.pdf)
- Rank 2 (rate spread): [MSE](https://www.moneysavingexpert.com/utilities/best-solar-rates-seg-tariffs)
- Rank 4: [EST](https://energysavingtrust.org.uk/energy-saving-budget?loc=wales)
- Rank 5: [DESNZ](https://www.gov.uk/government/statistics/warm-home-discount-statistics-2025-to-2026/warm-home-discount-statistics-2025-to-2026)
- Rank 6: [Ofgem trial](https://www.ofgem.gov.uk/sites/default/files/docs/2019/09/collective_switch_slides_for_publication.pdf)
- Rank 7: [Nesta](https://www.nesta.org.uk/report/the-impact-of-boiler-optimisation-on-gas-consumption-and-household-comfort)
- Rank 9: [EST](https://energysavingtrust.org.uk/energy-saving-budget?loc=wales)

## 11. Measures where the supplier creates value mainly by saving the household time

1. **Auto-optimised tariff:** default the customer onto the cheapest eligible tariff, including Direct Debit and EV or heat pump detection from half-hourly data. This mirrors the collective-switch effect ([Ofgem](https://www.ofgem.gov.uk/sites/default/files/docs/2019/09/collective_switch_slides_for_publication.pdf)).
2. **Automated DFS and flexibility participation** via smart charger, battery or heat pump APIs. Cash value per household is under £1 ([NESO](https://www.neso.energy/nearly-2-million-households-and-businesses-registered-demand-flexibility-service-dfs-last-winter)), so the only scalable version is zero-effort.
3. **Grant gateway concierge:** eligibility pre-check, plus the BUS, Local Grant, Home Energy Scotland or Nest paperwork. Scheme churn (GBIS ended, ECO4 closing, Warm Homes Plan detail pending) multiplies research time ([DESNZ](https://assets.publishing.service.gov.uk/media/697258453f2908a34904057c/extending-eco4-end-date-government-response.pdf); [MCS](https://mcscertified.com/warm-homes-plan-key-takeaways-for-the-small-scale-renewables-sector/)).
4. **Pre-surveyed "heat pump-ready" homes**, so a boiler failure (48% of boiler purchases are distress purchases ([Nesta](https://nesta.org.uk/report/heat-pumps-a-user-survey))) can be converted without a 1 to 2 month lead time.
5. **One-stop heat pump or PV install with a single point of accountability**, given that 63% of heat pump users report installation problems ([Nesta](https://nesta.org.uk/report/heat-pumps-a-user-survey)).
6. **Remote flow-temperature and controls optimisation** for connected boilers or heat pumps. Advice alone moved gas use by only 0.4% ([Nesta](https://www.nesta.org.uk/report/the-impact-of-boiler-optimisation-on-gas-consumption-and-household-comfort)).
7. **SEG and export handling bundled with supply** ([MSE](https://www.moneysavingexpert.com/utilities/best-solar-rates-seg-tariffs)).
8. **PSR, WHD and debt-relief auto-enrolment** from data signals such as arrears and prepayment self-disconnection ([DESNZ](https://www.gov.uk/government/statistics/warm-home-discount-statistics-2025-to-2026/warm-home-discount-statistics-2025-to-2026); [Big Issue](https://www.bigissue.com/news/social-justice/ofgem-energy-bill-debt-relief-scheme/)).
9. **Landlord compliance service for EPC C by 2030:** survey, works and a lodged post-works EPC ([Elmhurst](https://www.elmhurstenergy.co.uk/blog/2026/01/22/domestic-private-rented-properties-required-to-meet-epc-band-c-by-october-2030/)).
10. **Smart meter fix-up** for the 3.1m smart meters in traditional mode, which are already installed but not working remotely ([DESNZ](https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin)).

---

## 12. Prioritised catalogue: market-size ranking (separate from §10)

### Scoring formula (re-weightable)

`Score_m = N_rem,m × max(NAV_m, 0) × (Ease_m / 5)^α`

where:
- `NAV_m = £_m + λ · tCO2_m − Upfront_m / L_m` is the net annual value per household.
- `N_rem` is remaining addressable households in millions (eligible × (1 − penetration), from the tables above).
- `λ` = £250/tCO2 **[unverified]**.
- `L` = asset life in years **[unverified]**.
- `α` = 1.

To re-weight:
- Set λ = 0 for a pure-£ view.
- Raise α to penalise hassle more.
- Replace `Upfront/L` with a household discount-rate annuity for a "household-realistic" view; a high implicit discount rate strongly penalises capex.

**Key assumptions behind the inputs (all [unverified] unless sourced above):**
- Carbon values per measure.
- Upfront costs for EV premium (£5k), PV (£7k), battery (£4.5k) and solid wall insulation (£12k).
- Lives: insulation 35 to 40 years, heat pump 15, PV 25, battery 12.

| Rank | Measure | N_rem (m) | NAV £/hh/yr | Ease | Score (£m-equivalent/yr) |
|---|---|---|---|---|---|
| 1 | EV switch (off-street parking, at ownership change) | 10.0 | 475 | 2 | 1,900 |
| 2 | Thermostat −1°C | 13.9 | 152 | 4 | 1,696 |
| 3 | Move off SVT to a beating fix / switch | 18.0 | 80 | 5 | 1,440 |
| 4 | Shower to 4 min / hot water timing | 13.9 | 75 | 4 | 834 |
| 5 | Standby and appliance habits | 13.9 | 52 | 5 | 730 |
| 6 | ASHP after BUS (gas, owner-occupied) | 13.0 | 267 | 1 | 693 |
| 7 | DIY draught-proofing | 13.9 | 50 | 4 | 556 |
| 8 | Loft top-up to 270mm | 10.6 | 85 | 3 | 541 |
| 9 | Cavity wall insulation | 2.5 | 348 | 3 | 521 |
| 10 | Solar PV | 6.4 | 195 | 2 | 499 |
| 11 | Boiler flow temperature | 8.2 | 65 | 4 | 426 |
| 12 | Standard credit → Direct Debit | 3.1 | 136 | 5 | 422 |
| 13 | EV tariff for existing EV owners | 0.8 | 400 | 4 | 256 |
| 14 | Smart meter install (enabler; value understated) | 8.0 | 38 | 4 | 240 |
| 15 | Full heating controls / TRVs | 3.0 | 128 | 3 | 230 |
| 16 | Solid wall insulation | 6.5 | 157 | 1 | 204 |
| 17 | Heat-pump tumble dryer (at replacement) | 3.0 | 42 | 4 | 102 |
| 18 | DFS-type event participation | 17.8 | 6 | 4 | 78 |
| 19 | Remove gas connection after heat pump | 0.3 | 93 | 2 | 11 |
| 20 | Induction hob (gas homes) | 5.0 | negative | 3 | 0 |
| 21 | Battery added to existing PV | 1.5 | negative at £4.5k / 12 yr | 3 | 0 |
| 22 | Glazing for the single-glazed remainder | 3.1 | negative | 2 | 0 |

**Interpretation notes:**
- The behaviour rows (2, 4, 5) score high on breadth, but their £ figures are modelled and persistence is unproven. The only GB RCT in this pack (flow temperature) measured far below modelled savings ([Nesta](https://www.nesta.org.uk/report/the-impact-of-boiler-optimisation-on-gas-consumption-and-household-comfort)). Apply a persistence haircut of 50% or more before using these in the simulation **[unverified]**.
- Enabler measures (smart meter, smart charger) are understated, because their value is the downstream ToU, DFS and SEG measures they unlock.
- Battery and induction become positive when paired: battery with ToU arbitrage, induction with gas disconnection. Model them as bundles.
- The EV rank is driven by an assumed £5k premium and fuel savings, both **[unverified]**. Sensitivity is high.

---

## 13. Gaps

1. **GB household count** and **GB-wide tenure split.** English Housing Survey shares were applied to GB, and the 27.8m total is unverified.
2. **Current share of customers on fixed vs SVT** and **standard credit share** (Ofgem retail market indicators not fetched).
3. **HEE / NEED statistics** for unfilled cavities, solid-wall insulated share, and NEED-measured savings by measure (HEE release found but not read).
4. **Stock totals** for domestic PV, batteries and heat pumps (only H1 2025 MCS flows and BUS cumulative found).
5. **EST per-measure £ and carbon** for heat pumps, PV, solid wall, glazing, LEDs, standby, showers and laundry (pages not reachable). These are covered by the separate £/carbon page.
6. **Tariff savings** for EV, heat pump and ToU tariffs from a neutral or primary source.
7. **Quantified hassle:** hours to research and arrange measures, call-centre wait times, installation disruption days, and GB willingness-to-pay to avoid hassle. None was found in Nesta, BIT or Citizens Advice within budget.
8. **Current PSR registrations** (latest found is 2015: about 13%).
9. **Warm Homes Plan low-income delivery detail** (due Spring 2026, not confirmed), the loan product terms, and BUS air-to-air and heat battery start dates.
10. **District heat regulation start date and customer numbers; storage-heater stock.**
11. **Off-street parking for GB** (the 68% figure is England only); renters' and flat-dwellers' charge-point consent rules.
12. **Persistence of behavioural savings** in GB trials beyond 90 days.
13. **Conservation-area and listed-building shares** of the stock relevant to EWI, PV and glazing.

---

**Notes for the coordinator:**
- **Blocked pages:** gov.uk's WHD and BUS pages and EST's per-technology advice pages were blocked by the fetch allowlist.
- **Embedded instruction ignored:** the CIC Warm Homes Plan page had an instruction hidden in its metadata, asking the reader to add an email address to an analytics account. I ignored it and used only the page's factual content.
- **Memory:** nothing from memory was used. No new memory items.
- **Scoring script:** `/tmp/claude-0/-home-claude/90c98f50-d921-54a8-854d-66c80c7b13b3/scratchpad/rank.py` holds the inputs and formula. Change the inputs there to re-run the ranking.