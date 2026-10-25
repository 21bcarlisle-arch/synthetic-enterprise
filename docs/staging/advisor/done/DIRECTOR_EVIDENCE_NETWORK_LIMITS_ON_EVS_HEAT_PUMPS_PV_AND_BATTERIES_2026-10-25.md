# Director evidence: network limits on evs heat pumps pv and batteries

**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 06:44 GMT: "Maybe you can also research vpp, over the top flex payments and also network payments in certain post codes for flex. Also EV and heat pump restrictions in certain post codes due to network limitations or at least the process that's required. This may be more complex than we want to build but knowledge should be thorough and then we decide where the minimum viable SIM is and have road map options for more complexity as the supplier matches the evolution of services to match the world."

This is one of two packs. The cover steer is `DIRECTOR_STEER_FLEX_AND_NETWORK_KNOWLEDGE_IS_THOROUGH_AND_THE_SIM_IS_LAYERED_2026-10-25.md`.

## What to do with it

- Publish this pack as a Knowledge page. The page should be thorough, because it is knowledge and not a build commitment.
- The pack's "suggested layering" section is input to the roadmap options described in the cover steer.
- Every gap the pack names is either something for you to fetch or a design choice you make and state.

---

# Evidence pack: network limits on household EVs, heat pumps, batteries and solar in GB

**For:** Poesys simulation team · **Compiled:** 25 Oct 2026 · **Scope:** GB distribution (LV/HV). NIE (Northern Ireland) sources appear only where they compare GB DNOs.

**Conventions:** Each figure carries its source URL. **[derived]** marks my own arithmetic. **[unverified]** marks something from memory that I did not confirm in this session. A figure with neither tag was read from the cited page in this session, sometimes through a summarising fetch. A few sources are vendor blogs or trade press, and they are labelled as such.

---

## 0. Headline findings

1. **Most homes connect by notifying, with a few hard gates.** An EV charger or heat pump can be fitted and then notified within 28 days if all of these hold: one new device, a known cut-out rating, no looped service, and whole-premises maximum demand ≤60 A per phase (13.8 kVA). A heat pump must also be ≤32 A and marked "Connect and Notify" in the ENA database. Anything else needs an application first. (https://www.enwl.co.uk/globalassets/evcp-and-hp-v3.3-ena-form.pdf)
2. **Looped services are the biggest single household-level blocker, and they are far more common than the "up to 1.5m" figure in the brief.** DESNZ's 2026 research puts the GB central estimate at **3.9m looped connections (range 3.1–4.7m, 11–17% of stock)**. (https://assets.publishing.service.gov.uk/media/6949772372075a1d4a508a14/unlooping-electricity-network-connections-research-summary-report.pdf)
3. **For most domestic demand upgrades, the household pays nothing for reinforcement.** Since 1 April 2023 (Access SCR), demand customers pay only for extension assets. Three-phase upgrades are still often chargeable: ENWL's average is **£5,370**. (https://cms.law/en/gbr/legal-updates/distribution-connection-charges-to-be-reduced-ofgem-publishes-its-decision-on-the-access-and-forward-looking-charges-significant-code-review ; https://enwl.co.uk/Get-connected/apply-for-a-new-connection/heat-pumps2)
4. **Time, not cost, is the main supplier-facing friction.** Published delays include fuse upgrades of up to 12 weeks, unlooping of 3–12 weeks (6–12 months with neighbour disputes), and SPEN site surveys taking up to 90 days. Sources are in §2.
5. **There is little published LV and secondary-substation headroom.** Primary/BSP headroom is open data, but secondary-level data comes mostly as bands or utilisation, and coverage differs by DNO (§3).

---

## 1. The process: who notifies or applies, thresholds, forms, response times

### 1.1 EV chargers and heat pumps (ENA "connect and notify" vs "apply to connect")

All DNOs use a common ENA form for EV charge points (EVCP) and heat pumps (HP), currently v3.3. The installer completes it, with the customer's details and a declaration. (https://www.enwl.co.uk/globalassets/evcp-and-hp-v3.3-ena-form.pdf)

**Connect and notify** is allowed only if *every* applicable Section B criterion is met. The equipment can then be connected and the DNO notified within **28 days of installation**. The criteria (same source) are:
- **One** additional device only.
- A known cut-out rating.
- A metered supply.
- **Not a looped service.**
- No safety concerns with DNO equipment.
- Maximum demand below the cut-out rating, **and** below **13.8 kVA per phase** (60 A), or CT-metered, or load-limited.
- **Heat pumps:** a single controller, total HP maximum demand **≤32 A** including boost, immersion and back-up heaters, and the model marked "Connect and Notify" in the ENA HP database.
- **EVCPs on CT-metered premises:** AC output ≤30% of maximum import capacity.
- **V2G:** generation ≤3.68 kW (16 A) per phase, and installed to G98.

The DNO flow-chart notes add that a combined HP+EVCP install requires an application. So do multiple HPs over 3.68 kW aggregate under one controller, a looped service, and generation over 3.68 kW per phase. A cut-out with more than one DNO service cable is the tell-tale of a looped service. (https://www.nationalgrid.co.uk/downloads-view-reciteme/669829)

**Load-limiter route.** Where existing maximum demand is above 60 A, connect and notify is still allowed if a fail-safe whole-premises load limiter holds the premises at ≤60 A. (same source)

**Apply to connect: response times**
- Where 60 A < maximum demand ≤ 100 A (23 kVA), the DNO should say within **10 working days** of a complete form whether the supply can be connected. (https://www.enwl.co.uk/globalassets/evcp-and-hp-v3.3-ena-form.pdf)
- Above 100 A, Guaranteed Standards of Performance timescales apply. (same)
- The form warns that reinforcement costs "may be charged". Since April 2023 that is rare for LV demand (§5).
- Guaranteed Standards for a single LV metered demand service:
  - Quotation in **5 working days**, with £20 per day late.
  - Budget estimate in 10 working days (£80).
  - Contact to schedule within 7 working days of acceptance.
  - Completion on the agreed date (£45 per day late).
  - (https://enwl.co.uk/globalassets/get-connected/apply-for-a-new-connection/gsop/dno-metered-connections-nor-april-2025_final_v.pdf)
- Guaranteed Standards **do not apply to unlooping**. (DESNZ report, URL above)

**ENA Connect Direct (digital portal)**
- Launched May 2024. It offers "instant approvals for most routine applications" using AI. (https://www.solarpowerportal.co.uk/solar-technology/ena-launches-ai-tool-for-connecting-low-carbon-technologies)
- By 3 Oct 2025 it had handled **over 185,000** applications, and a platform update raised auto-approvals by 33% on its first day. (https://transportandenergy.com/2025/10/03/over-185000-clean-energy-connections-facilitated-by-enas-connect-direct-service)
- As of May 2026 it covers PV, batteries and heat pumps. It includes AI cut-out recognition from photos and auto-commissioning, and it is free to installers across GB and NI. Householders do not use it directly. (https://www.installershow.com/news/ena-connect-direct-free-tool-fast-track-domestic-grid-connection-approvals)
- At one DNO, Connect Direct carried **40% of LCT applications** by Nov 2024. (DESNZ unlooping report, URL above)

**DNO-specific precedents**
- **UKPN Smart Connect (2021–22):** 983 of 1,720 EV applications (~57%) were approved instantly. Auto-approvals also covered 234 HPs, 765 PV and 66 batteries. (https://www.evinfrastructurenews.com/ev-networks/low-carbon-technology-install-applications-approved-in-record-time-via-ai-driven-ukpn-portal)
- **WPD/NGED (Oct 2021):** "same or next day" approval in most cases, with remedial works scheduled after connection rather than before. WPD was receiving >200 LCT applications per day and projected ~500,000 installs a year by 2030. (https://transportandenergy.com/2021/10/14/news-wpd-pledges-same-day-or-next-day-connection-for-domestic-ev-chargers-and-heat-pumps/)
- **SPEN:**
  - After an office review, a service partner "aims to complete" a site survey **within 90 days** of the ENA form.
  - A design proposal follows within 10 days.
  - Works take: cut-out up to half a day; fuse upgrade up to 1 day; service upgrade up to 3 days; unlooping 5–10 days (plus up to 90 days if a highway permit is needed).
  - All of this is free to customer and installer.
  - Customer and neighbours must be present, and works must finish before the LCT is used.
  - (https://www.spenergynetworks.co.uk/userfiles/file/Connecting_your_low_carbon_technology.pdf)

**What triggers a site visit** (synthesised from the sources above):
- The cut-out rating is unknown or mislabelled (Nesta says this moves a job from quick approval to "weeks to months": https://www.nesta.org.uk/project-updates/the-challenges-of-distribution-network-operator-applications-for-heat-pump-installers/).
- A looped service is suspected.
- Maximum demand exceeds 60 A per phase.
- There are safety or condition concerns about the service.
- More than one device is being added.

### 1.2 Solar PV and batteries (EREC G98, G99, G100)

- **G98 (connect and notify):** type-tested generation ≤**16 A per phase** (≈3.68 kW single-phase; ≈11 kW three-phase, i.e. 3×3.68 = 11.04 kW **[derived]**). The installer notifies within **28 days of commissioning**. (https://www.autarc.energy/gb/knowledge/g98-vs-g99-solar-battery-application, a vendor guide citing EREC G98 Issue 2, 2025)
- **G99 (apply first):** above 16 A per phase. The full process can take up to **45 working days**. The vendor guide gives ~20 business days for Fast Track. (same)
  - Northern Powergrid's LV G99 guaranteed standard is reported as 45 days, with an average of ~18 weeks from payment to connection where works are needed. (https://payaca.com/uk/blog/dno-g99-applications-solar, vendor blog)
- **G99 Fast Track (ENWL):** intrinsic design capacity ≤32 A and aggregate registered capacity ≤60 A, using Form A1-2. (https://enwl.co.uk/Get-connected/apply-for-a-new-connection/generation-and-storage/g99-fast-track-process)
- **G100 (export and import limitation):**
  - A customer limitation scheme must cut flow to the agreed limit typically within **15 s, with a maximum of 60 s**, and must fail safe.
  - Settings are locked against customer change.
  - The CLS forms run: Form A with the application, then Form C within 28 days of commissioning.
  - Registered capacity follows the software limit (e.g. a 5 kW inverter limited to 3.68 kW is registered at 3.68 kW).
  - DC-coupled batteries count only the inverter capacity; AC-coupled batteries count both inverters.
  - Export limits are set per connection by study, covering thermal, voltage rise (≤2%, ~4.6 V above the statutory upper limit), protection and power quality.
  - (https://connections.nationalgrid.co.uk/customer-export-limitation-schemes)
- **SPEN relaxation:** combined PV+storage with export locked to 3.68 kW per phase is allowed via G99 Fast Track, provided total capacity is ≤**7.36 kW**. Above 3.68 kW per phase needs full G99 with an export-limitation appendix. "Supply upgrades may still be required even with export limitation." (https://www.spenergynetworks.co.uk/pages/export_limitation.aspx)
- **Plug-in ("balcony") solar:**
  - Regulations were laid on 17 Jul 2026 and come into force **27 Aug 2026**, capped at **800 VA**.
  - A G98 notification is still required for now; government is "considering" simplifying it.
  - (https://cep.org.uk/information-pages/plug-in-solar-systems-faqs/, a community-energy FAQ, not a primary source)

### 1.3 Installation standards (customer side)

- **IET Code of Practice for EV Charging Equipment Installation, 5th ed.:** published 12 Sep 2023 and aligned to BS 7671:2018+A2:2022. It expands DNO notification guidance for V2G/V2H and covers the Smart Charge Point Regulations. (https://professionalbooks.co.uk/iet-code-practice-electric-vehicle-charging-equipment-installation-5th-edition-9781839538575)
  - The Code covers managed and load-curtailed charging (Section 12 in the 4th ed.). (https://electrical.theiet.org/wiring-matters/years/2020/80-may-2020/the-iet-code-of-practice-for-electric-vehicle-charging-equipment-installation-4th-edition/)
- **BS 7671 Reg 722.411.4.1:** direct use of a PME earth for an EV charger is allowed only if the PME terminal cannot rise above 70 V rms on an open PEN. Otherwise the installer needs an open-PEN detection device or a TT earth. (same IET source)
  - Simulation relevance: PME versus TT affects installer cost, not the DNO decision **[derived]**.
- **BS 7671:2018+A4:2026** exists. The IET/BSI press release is dated 15 Jan 2026 (https://www.theiet.org/media/press-releases/press-releases-2026/press-releases-2026-january-march/15-january-2026-iet-and-bsi-publish-amendment-4-2026-to-bs-76712018-iet-wiring-regulations). I could not read its content. A3:2024 added prosumer and battery provisions **[unverified]**.

---

## 2. Physical limits at the home

### 2.1 Supply capacity and phase

**Cut-out fuses**
- SPEN cites 30 A or 60 A main fuses in older homes, upgradable to 80 A. (https://www.spenergynetworks.co.uk/userfiles/file/Connecting_your_low_carbon_technology.pdf)
- New single-phase supplies are fused at 80 A or 100 A. (Regen/MCS via https://staging4.utilityweek.co.uk/nearly-half-of-primary-substations-could-hit-max-capacity-by-2035, paywalled summary)
- SSEN treats ≤100 A per phase as a "typical household supply". (https://www.ssen.co.uk/our-services/existing-electricity-supplies/looped-service/)

**Reference loads, as amps per phase at 230 V [derived]**
- 60 A ≈ 13.8 kVA; 100 A ≈ 23 kVA.
- A 7 kW charger ≈ 32 A.
- ENWL's ED2 paper treats an EV charger as ~7.5 kW (~32 A) and a heat pump as 5–15 kW (~20–60 A). (https://www.enwl.co.uk/globalassets/about-us/regulatory-information/riio2/july-2021-submission/ejps/lre_ejp8__service_unlooping_programme.pdf)

**Three phase**
- Most UK homes are single-phase (https://www.homebuilding.co.uk/news/one-in-three-homes-might-need-electricity-upgrade-for-heat-pumps-to-work).
- **I found no published share of GB homes with three-phase supply** (gap). The ENA has said three-phase would help with high LCT uptake but adds cost, and called for public debate on who pays (2018). (https://www.solarpowerportal.co.uk/battery-storage/three-phase-connections-for-all-urges-rea-as-networks-call-for-open-and-public-discussion-)

### 2.2 Looped services

**How common**
- **GB:** central **3.9m** (3.1–4.7m), 11–17% of housing stock, ~14% of 28.5m connections. (DESNZ, https://assets.publishing.service.gov.uk/media/6949772372075a1d4a508a14/unlooping-electricity-network-connections-research-summary-report.pdf; landing page https://www.gov.uk/government/publications/unlooping-electricity-network-connections, published 21 Jan 2026)
- **By anonymised DNO group:** 805k, 820k, 500k, 417k, 810k and 569k. Shares are ~6%, 10%, 17%, 21%, 22% and 25%; the report codes counts and shares differently, so they cannot be matched to each other. (same)
- **ENWL:** ~20% of domestic premises, ~500k households. (ENWL EJP8 URL above)
- **SSEN:** ~0.5m homes (16%). (https://www.ssen.co.uk/news-views/2026/Pilot-begins-to-help-improve-homes-electricity-connections/)
- **Where they occur:** looped services are common in 1970s–80s estates, rural areas and terraces. (https://www.nationalgrid.co.uk/downloads-view-reciteme/669829)
- **Discrepancy:** the brief's "up to 1.5m" is contradicted by DESNZ (3.9m). ENWL and SSEN alone total ~1.0m **[derived]**. Treat 1.5m as outdated or partial.

**How DNOs treat a looped service**
- A looped service rules out connect and notify. (ENA form)
- One DNO lets the first LCT onto 2-, 3- or 4-house loops without unlooping and says this covers >90% of cases. Two LCTs are allowed only on 2-house loops, with conditions.
- Three DNOs use load limiters as an interim measure; three unloop instead.
- (DESNZ report)

**Cost of unlooping**
- Ofgem industry median **£1,900** per property.
- ENWL full unloop **£2,639**, partial **£943**.
- Other DNOs: £2,500–6,000 typical, or £3,500–4,000; complex jobs £10–15k.
- Proactive unlooping is ~25–30% cheaper.
- DNOs fund standard unlooping through bills; consumers may pay for extras such as moving to three-phase or meter relocation.
- (DESNZ report; ENWL EJP8)
- SSEN and SPEN state there is no charge for typical cases. (SSEN looped page; SPEN guide)

**Time to unloop**
- **3–12 weeks** uncomplicated; **6 months to 1 year+** with neighbour disputes.
- Disputes at one DNO rose from 3 (2021) to 30 (2024).
- One housing association achieved 24 unloops from 900 applications since 2023. (DESNZ report)

**Progress**
- Under 1% of looped connections had been unlooped by Jan 2025.
- About 187k (~5%) are projected by the end of ED2. (DESNZ report)
- ENWL plans 32,018 ED2 interventions against ~500k looped, i.e. ~6.4% **[derived]**. (EJP8)
- Programmes under way:
  - ENWL Lancaster (263 properties, Jun–Aug 2026) and a £4m trial covering ~1,500 properties. (https://www.enwl.co.uk/about-us/networkinvestment/unlooping/)
  - SSEN pilot offered to up to 1,200 homes (Jul 2026). (SSEN pilot URL)

### 2.3 Fuse, cut-out and service upgrades: cost, time, frequency

**Cost**
- Pre-2023 charges: NPg £120 for a fuse upgrade; SSEN up to £200 for a cut-out. Both moved to free, socialised upgrades from April 2023. (https://www.homebuilding.co.uk/news/one-in-three-homes-might-need-electricity-upgrade-for-heat-pumps-to-work, Feb 2022)
- SPEN: free. (SPEN guide)
- **Three-phase upgrade:**
  - ENWL average **£5,370** (80 A per phase), chargeable. (https://enwl.co.uk/Get-connected/apply-for-a-new-connection/heat-pumps2)
  - Regen/MCS: typically £3,000–7,000. (utilityweek summary URL above)
  - Press reports of up to £15,000. (homebuilding.co.uk citing *The Telegraph*)

**Time**
- Octopus: DNO fuse upgrades "add delays of up to 12 weeks" before a heat pump can be switched on. (https://committees.parliament.uk/writtenevidence/123898/html)
- UKPN: up to 30 days in some areas. Octopus engineers were trained to do fuse upgrades during the heat pump install (pilot Feb 2022–Feb 2023, then extended to EV). (https://www.ukpowernetworks.co.uk/news/an-offer-you-can-t-refuse-octopus-energy-makes-switching-to-heat-pumps-easier)

**How often an upgrade is needed**
- **45% of Octopus heat pump customers needed a fuse upgrade.** (Octopus written evidence, URL above)
- WPD said "around a third" of homes could need supply upgrades for heat pumps (2022). (homebuilding.co.uk)
- DESNZ survey: 64 of 73 unlooped respondents had an LCT. No national rate of LCT-triggered upgrades exists. (DESNZ report)
- Citizens Advice (Jul 2026) gives no quantified upgrade share either, but recommends cost transparency at survey stage and proactive unlooping in ED3. (https://www.citizensadvice.org.uk/policy/publications/navigating-the-network-how-to-improve-the-consumer-journey-when-installing-low-carbon-technology/)
- ED2 metric evidence: WMID's cut-out and fuse additions exceeded unlooped properties by 30%, and SP ENW's cut-out additions by 22%. This suggests fuse and cut-out work outruns unlooping. (https://www.ofgem.gov.uk/sites/default/files/2026-02/RIIO-ED2%20Load%20Related%20Expenditure%20volume%20drivers.pdf)
- Ofgem median LV service unit costs (£k, 2020/21 prices): underground **1.60 → proposed 2.65**, overhead 0.35 → 1.44. (same)

---

## 3. Where constraints bite: feeder, substation and clustering

### 3.1 Design demand (ADMD) and how LCTs move it

**Current NIE ADMD per dwelling (kVA)**
- 1 connection: detached 5.3, semi 4.9, terrace 4.1.
- 100 connections: 3.0, 2.7 and 2.3.
- Proposed per-dwelling additions: **+2.5 kVA for an EV charger and +2.5 kVA for a heat pump**.
- (https://videos.nienetworks.co.uk/documents/consultations/design-demand-consultation-jun22.aspx)

**EV diversity factors used by GB DNOs** (same NIE source)
- SSEN: no diversity up to 20 chargers, then 0.5.
- WPD: 0.5.
- UKPN: 0.5, falling to 0.22 above 140 chargers per circuit.
- SPEN: 2.5 kVA per 32 A charger (~0.34).

**SPEN ADMD calculator, per home, 300-home private development (kVA) [derived from totals]**
- Gas-heated: 1.5.
- Gas + standard EV: 4.8.
- Heat pumps: 3.6.
- Heat pumps + standard EV: 6.9.
- Heat pumps + smart EV: 5.1.
- In other words, smart EV charging removed ~1.8 kVA per home **[derived]**.
- (https://gov.scot/publications/research-electricity-network-constraints-2024-new-build-heat-standard/pages/11)

**Cost scale from the same Scottish study**
- An LV substation costs £54k–148k.
- Moving from ~10% to 30% LCT at one site triggered a ~£7.5m HV substation. (same)

**Electric Nation (WPD, 2016–19)**
- 673 drivers and >140,000 charging events. Cars were plugged in >12 h on average, started charging >50% full, and charged ~3 times a week. (https://www.fleetnews.co.uk/news/environment/2019/02/08/smart-charging-key-to-ev-growth-says-electric-nation)
- With 40–70% of households having EVs, "at least 32%" of LV networks would need intervention. (https://eatechnology.com/sea/resources/projects/wpd-s-electric-nation-project/)
- My Electric Avenue: ≥30% of LV networks need investment by 2050, about £2.2bn. (https://www.nationalgrid.co.uk/downloads/34180)

**UKPN Shift**
- Only **20% of home plug-in time** is needed to meet charging needs. (https://innovation.ukpowernetworks.co.uk/projects/shift/)

### 3.2 How many substations need reinforcement

- **Regen/MCS Foundation (May 2024):** without investment, **23%** of GB primary substations are at maximum capacity by 2030 and **45% by 2035**. These are illustrative figures under DFES Consumer Transformation, not forecasts. (https://staging4.utilityweek.co.uk/nearly-half-of-primary-substations-could-hit-max-capacity-by-2035 ; https://regen.co.uk/insights/electrification-the-local-grid-challenge)
- **No GB-wide published count of secondary substations needing reinforcement by 2030 or 2035** (gap).

**ED2 LCT forecasts to 2028**
- WPD: 1.5m EVs and 600k HPs.
- SSEN: 1.3m EVs and 800k HPs.
- NPg: 941k EVs and 309k HPs.
- ENWL: 630k+ EVs.
- (https://www.solarpowerportal.co.uk/solar-technology/dnos-commit-to-billions-in-investment-in-final-riio-ed2-business-plans)
- UKPN: up to 3.6m EVs by 2030. (https://ed2.ukpowernetworks.co.uk)
- Ofgem ED2 allowed totex is £22.2bn (2020/21 prices), including £3.2bn for LCT-related upgrades (with £0.4bn Access SCR). LV services and secondary reinforcement are funded through volume drivers. (https://www.ofgem.gov.uk/press-release/ofgem-confirms-local-electricity-networks-price-control-2023-2028 ; https://www.ofgem.gov.uk/sites/default/files/2022-11/RIIO-ED2%20Final%20Determinations%20Overview%20document.pdf)
- Actual LCT uptake is lagging DFES, and some secondary reinforcement allowances are barely used (SSES spent 0.94%). (Ofgem LRE VD URL above)

**Installed base**
- England, 2023: ~1.5m homes with PV (6%), 276k with a heat pump as primary heating (1%), ~930k with an exclusive-use charge point. (https://www.gov.uk/government/statistics/english-housing-survey-2023-to-2024-low-carbon-technologies-in-english-homes-fact-sheet/english-housing-survey-2023-to-2024-low-carbon-technologies-in-english-homes-fact-sheet)
- 2025: ~52k heat pump retrofits (+7%). (Citizens Advice URL)

### 3.3 Published capacity data

- **NGED Network Capacity Map:** BSP and primary demand/generation headroom only, not secondary. (https://connecteddata.nationalgrid.co.uk/dataset/nged-network-capacity)
- **UKPN Secondary Site Utilisation:**
  - A utilisation **band** per secondary site (FY2024/25), mixing measured and profiled data.
  - Sites with ≤5 customers are excluded.
  - It is not committed capacity, and login is required.
  - (https://opennetzero.org/uk-power-networks/uk-power-networks-secondary-site-utilisation)
- **SPEN SPEN_015:**
  - Per-secondary-substation rating, expected peak utilisation (per unit), customer count and upstream primary.
  - Ground-mounted transformer figures come from LV monitoring or MDI; pole-mounted figures come from ADMD.
  - There is no explicit headroom field.
  - (https://www.spenergynetworks.co.uk/userfiles/file/Secondary_Network_Data_SPEN_015_Methodology.pdf)
- SSEN publishes a secondary substation dataset (data-api.ssen.co.uk). I did not inspect its fields (gap).

### 3.4 Export limits for PV and batteries

- Export limits are set per connection by network study, not by area rule. (NGED CLS URL)
- SPEN's standard cap is 3.68 kW per phase, with a 7.36 kW total relaxation. (SPEN URL)
- I found no published statistics on how many domestic G99 applications are export-capped, how low the caps are, or how often applications are refused (gap).
  - A vendor reports most rejections stem from application quality rather than network capacity. (Payaca URL)

---

## 4. How DNOs manage instead of reinforcing

- **Connect first, fix later.** WPD's 2021 move to approve first and schedule remedials afterwards. (WPD URL)
- **Load limiters:**
  - A fail-safe limiter keeps premises at ≤60 A and allows connect and notify. (https://www.nationalgrid.co.uk/downloads-view-reciteme/669829)
  - Three DNOs use limiters as an interim measure on looped services. (DESNZ)
  - This is the closest thing to a "domestic flexible connection" in the evidence.
- **Supplier-delivered upgrades:** Octopus doing UKPN fuse upgrades (UKPN URL), and a 2024 Octopus–NGED partnership covering upgrades including three-phase (https://www.homebuilding.co.uk/news/octopus-and-national-grid-join-forces-to-upgrade-homes-to-three-phase-electric-as-part-of-heat-pump-and-ev-charger-rollout; not read in full).
- **Local flexibility markets:**
  - NGED DSO procured **9.8 GWh** in Apr 2024–Mar 2025; **90%** of registered assets were domestic and half of connected EV charge points were registered.
  - Delivery: household demand 100%, EV chargers 89.6%; 6% of agreed deliveries did not respond.
  - (https://www.evinfrastructurenews.com/ev-technology/ev-chargers-most-responsive-technology-in-national-grid-dso-s-flexibility-provision)
  - UKPN Shift (2019–21, with Octopus, Kaluza and ev.energy) built a market-led smart-charging procurement mechanism. (Shift URL)
- **Smart Charge Point Regulations 2021** (SI 2021/1467):
  - Default charging outside **08:00–11:00 and 16:00–22:00 weekdays**, which the owner can override.
  - Randomised delay up to **600 s by default**, up to 1,800 s remotely.
  - DSR capability, per-second power measurement, and keeping smart function across a supplier switch.
  - (https://legislation.gov.uk/uksi/2021/1467/part/2/made?view=plain)
- **Load control licensing (SSES):**
  - Ofgem decision of 7 Aug 2026. Applications open **1 Mar 2027** with a 12-month transition.
  - Covers flexibility service providers and load controllers for domestic EVs, heat, batteries.
  - Load controllers ≥**300 MW** go into the Tier 1 / NIS cyber regime.
  - Suppliers get partial derogations.
  - Fee £1,100 for one activity, £1,650 for both.
  - (https://www.ofgem.gov.uk/sites/default/files/2026-08/SSES-Implementation-Decision.pdf)
  - The extract did not describe a DNO direct-interruption right over domestic devices.
- **LV monitoring and smart meter data:**
  - SSEN plans ~19,000 LV monitors (~19% of ~100k secondary substations) by 2027 at £64.28m, publishing LV data every 10 minutes. It uses smart meter data (penetration >50%) for load models and phase mapping. (https://pre-dxp.ssen.co.uk/globalassets/about-us/stakeholder-engagement/annual-engagement-plans-and-reports/ssen-network-visibility-strategy-feb-2024.pdf)
  - ENWL aggregates half-hourly smart meter data by LV feeder or feeder section with a **minimum group of 5**; 97.7% of customers sit on feeders with ≥5 meters. (https://enwl.co.uk/globalassets/innovation/enwl-dpp-2024-v5.1-redacted.pdf)
- **Connections reform (TMO4+/Gate 2):**
  - Applies to generation and storage **≥1 MW** needing a transmission impact assessment.
  - Embedded *demand* is not covered.
  - Effectively irrelevant to single homes, except via community or aggregated schemes.
  - (https://www.enwl.co.uk/Get-connected/connections-reform/what-is-connections-reform-and-why-is-it-needed/)

---

## 5. What this means for a supplier selling EVs, heat pumps, PV and batteries

- **Cost to the customer.**
  - Under Access SCR (decision 3 May 2022, effective 1 Apr 2023), LV demand customers pay only extension assets, with a high-cost cap of **£1,720/kVA**.
  - Generation pays reinforcement at the connection voltage, capped at £200/kW.
  - (CMS URL)
  - In practice, fuse, cut-out and unlooping work is free at most DNOs, and three-phase work is the main customer-paid item (£3–7k).
- **Delay is the real cost.**
  - Connect and notify: no delay.
  - Apply 60–100 A: about 10 working days.
  - Fuse upgrade: up to 30 days (UKPN) to 12 weeks (Octopus).
  - SPEN survey: up to 90 days.
  - Unlooping: 3–12 weeks, or 6–12 months if disputed.
  - G99: up to 45 working days, or ~18 weeks with works (NPg, vendor-reported).
- **Refusals** are rare for demand. The outcome is usually "connect plus remedial work" or "connect with a limiter". For PV and batteries the main risk is an export cap rather than an outright refusal, but no rates are published (gap).
- **Regional differences.**
  - Looped share varies about 6–25% by DNO group.
  - Charging for three-phase varies.
  - Survey lead times vary (SPEN's 90-day aim stands out).
  - Willingness to allow the first LCT on a loop varies.
  - Upgrade delegation to the supplier exists at UKPN and NGED for Octopus.
- **Bundling.** Combined HP+EV, or more than one device, forces "apply". This penalises the bundled offers suppliers like to sell **[derived from ENA rules]**.

---

## (a) Process map

| Asset | Threshold | Process | Who | Typical time / cost | Source |
|---|---|---|---|---|---|
| EV charger | Premises MD ≤60 A per phase (13.8 kVA), single device, known cut-out, not looped | Connect and notify within 28 days | Installer | 0 days delay; free | https://www.enwl.co.uk/globalassets/evcp-and-hp-v3.3-ena-form.pdf |
| EV charger | MD >60 A, ≤100 A | Apply to connect | Installer | DNO answer in 10 working days; fuse upgrade free at most DNOs | same |
| EV charger | MD >60 A but fail-safe limiter ≤60 A | Connect and notify | Installer | As notify; limiter cost to customer | https://www.nationalgrid.co.uk/downloads-view-reciteme/669829 |
| Heat pump | ≤32 A incl. back-up heaters, single controller, ENA-listed "C&N", MD ≤60 A | Connect and notify within 28 days | Installer (MCS) | 0 days delay | ENA form |
| Heat pump | >32 A, unlisted, or MD >60 A | Apply | Installer | 10 working days; ~45% needed a fuse upgrade (Octopus), up to 12 weeks | https://committees.parliament.uk/writtenevidence/123898/html |
| HP + EV together / >1 device | Any | Apply | Installer | As above | NGED flowchart |
| Any LCT on looped service | Looped | Apply; unloop or limiter | Installer → DNO | 3–12 weeks (6–12 months disputed); £1,900 median, DNO-funded | DESNZ report |
| Three-phase upgrade | Needs >100 A single-phase | Apply (new connection quote) | Customer/installer | Quote 5 working days (GSoP); £5,370 average (ENWL), £3–7k (Regen) | https://enwl.co.uk/Get-connected/apply-for-a-new-connection/heat-pumps2 |
| PV / battery | ≤16 A per phase (≈3.68 kW 1-ph) type-tested | G98 notify within 28 days | Installer | 0 delay | https://www.autarc.energy/gb/knowledge/g98-vs-g99-solar-battery-application |
| PV + battery | Export locked ≤3.68 kW per phase, total ≤7.36 kW (SPEN) / ≤60 A aggregate (ENWL) | G99 Fast Track + G100 | Installer | ~20 business days (vendor) | https://www.spenergynetworks.co.uk/pages/export_limitation.aspx |
| PV / battery | >16 A per phase | Full G99 | Installer | Up to 45 working days; possible export cap; witness fees | https://payaca.com/uk/blog/dno-g99-applications-solar |
| Plug-in solar | ≤800 VA | G98 notify (for now) | Householder | From 27 Aug 2026 | https://cep.org.uk/information-pages/plug-in-solar-systems-faqs/ |
| V2G charger | ≤3.68 kW per phase generation | Notify (G98); else apply/G99 | Installer | As G98/G99 | ENA form |

## (b) Constraint facts to check a simulated world against

1. Looped share of homes is 11–17% nationally (central ~14%), and 6–25% by DNO group (DESNZ).
2. Under 1% of looped services had been unlooped by Jan 2025; ~5% are projected by 2028 (DESNZ).
3. About 45% of heat pump installs need a fuse upgrade (Octopus); WPD said "about a third" of homes could need supply upgrades.
4. A connect-and-notify share near the ~57% instant EV approvals at UKPN (2021) is plausible; a 100% rate is not.
5. The fuse upgrade delay distribution should have a tail to about 12 weeks, and unlooping a tail to 6–12 months.
6. A home with gas heating has ADMD of ~1.5–3 kVA; adding a heat pump plus an unmanaged EV gives ~6–7 kVA; smart EV charging gives ~5 kVA (SPEN/NIE).
7. At 40–70% EV penetration, at least 32% of LV networks need intervention (Electric Nation).
8. Primary substations at capacity without investment: ~23% by 2030 and ~45% by 2035 (Regen, illustrative).
9. Reinforcement charged to domestic demand customers after Apr 2023 should be ~0 except above £1,720/kVA.
10. EV charging needs only ~20% of plug-in time (Shift).
11. Domestic flex delivery is ~90%, EVs 89.6%, and ~6% of dispatches see no response (NGED).

## (c) What the simulation's world would need to model

- **Per home:**
  - DNO region.
  - Cut-out rating (30/60/80/100 A) and whether it is known or labelled.
  - Phases (1 or 3).
  - Looped flag and loop size (2/3/4).
  - Earthing type (PME/TT).
  - Existing maximum demand.
  - Installed LCTs by kW and per phase.
  - Smart meter present.
  - Neighbour-cooperation propensity, for loops.
- **Per LV feeder or secondary substation:** rating (kVA), customer count, utilisation/headroom, an ADMD model by house type and LCT mix, and a voltage-rise headroom for export.
- **Per primary:** demand and generation headroom (from public data).
- **DNO behaviour by region:**
  - Rules for notify versus apply.
  - Policy on the first LCT on a loop.
  - Whether limiters are used.
  - Upgrade delegation to suppliers.
  - Response-time distributions (approval, survey, fuse, unloop, three-phase).
  - Charging rules (three-phase).
  - Export-cap policy.
- **Device behaviour:** Smart Charge Point Regulation defaults (off-peak defaults, random delay), and flexibility participation and delivery rates.
- **Regulatory clock:** Access SCR from 2023, Connect Direct from 2024, SSES licensing from 2027, plug-in solar from 2026.

## (d) Suggested layering: minimum viable → richer

1. **MVS:**
   - Per-home attributes are cut-out amps, phase and looped flag, sampled from regional priors.
   - A deterministic ENA rule engine decides notify or apply.
   - Delay and cost are drawn from published distributions (above).
   - The supplier sees install lead time and conversion loss.
2. **Layer 2:** DNO-specific policies (first-LCT-on-loop, limiters, three-phase charging, supplier-delegated fuse upgrades) and G98/G99/G100 export logic for PV and batteries.
3. **Layer 3:** a feeder/substation layer with ADMD aggregation. Street clustering of LCTs drives remedial work and reinforcement queues, and export caps follow voltage-rise headroom.
4. **Layer 4:** flexibility markets (DNO tenders, delivery rates), smart-charging defaults and supplier load control under SSES licensing.
5. **Layer 5:** DNO planning loop (ED2/ED3 allowances, volume drivers, proactive unlooping programmes, LV monitoring rollout) and public capacity data feeding supplier targeting.

## (e) Named gaps

- No published GB share of homes on three-phase supply, or distribution of cut-out ratings (60/80/100 A).
- No national rate of EV or heat pump installs that trigger DNO upgrades (only Octopus's 45% and WPD's "a third").
- No GB count of secondary substations or LV feeders needing reinforcement by 2030/2035.
- No statistics on domestic G99 export caps or refusals.
- Original source of the "up to 1.5m looped" figure not found; DESNZ's 3.9m supersedes it.
- An NGED "Heat pump readiness" project was not found. The DESNZ Heat Pump Ready programme exists but its network findings were not read. UKPN Heat Street (2020–21, £318,652) reported no LV clustering results on its project page.
- Electric Nation's per-EV diversified peak kW was not confirmed in this session.
- No explicit DNO right to interrupt domestic devices was found; the SSES decision extract did not cover DNOs.
- BS 7671 A3/A4 content was not confirmed.
- SSEN and NPg secondary-substation datasets were not inspected.
- The NGED–Octopus 2024 partnership terms were not read in full.

---

**Possible memory note for the main session:** the DESNZ unlooping research (published 21 Jan 2026) puts GB looped connections at 3.9m (range 3.1–4.7m). This contradicts "up to 1.5m" and is useful as canon for the Poesys network layer.

## Done

Published on 25 Oct as the Knowledge page `site/knowledge/network-limits-on-home-electrification/`, with the note `docs/market_research/network_limits_on_home_electrification_2026-10-25.md`. The note carries the verification pass that the 25 Oct verify steer asks for: each [unverified] item is marked confirmed, corrected or still open, and no open item is stated on the page as a claim. Counts as recorded: Counts: 1 item; 0 confirmed, 0 corrected, 1 still open. Figures the pack read through summaries or
