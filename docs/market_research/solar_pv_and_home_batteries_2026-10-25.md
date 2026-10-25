# Rooftop solar and home batteries in a GB home: generation, self-use, settings, cost, carbon and what a supplier can see

**Knowledge:** solar-pv-and-home-batteries

Written 2026-10-25 from the advisor's cited evidence pack
`docs/staging/advisor/done/DIRECTOR_EVIDENCE_SOLAR_PV_AND_HOME_BATTERIES_2026-10-25.md` (director's chat,
25 Oct 05:37), one of six advice-roadmap packs under the cover steer
`DIRECTOR_STEER_THE_ADVICE_ROADMAP_NEEDS_ITS_KNOWLEDGE_FIRST_2026-10-25.md`. Figures marked
**[derived]** are arithmetic on cited numbers; **[unverified]** items are not claims until sourced.
Every [unverified] item was checked on 2026-10-25 under the director's steer of the same day; the
outcomes are in §9. The supplier-side view (what solar and a battery do to a supplier's margin,
export competition, EV tariffs) is already on `ev-solar-and-batteries-as-products`; this note is the
home side: what the kit generates, how much the home uses itself, how a battery's settings decide
its value, what it costs and saves, and what the supplier can observe, infer or must ask. Roof
orientation, tilt and the distribution of systems across the fleet are on
`pv-roofs-orientation-and-yield`; the network rules for connecting PV and batteries are on
`network-limits-on-home-electrification`.

## 0. What this project's world and company do today (read from code, not run)

- **The half-hourly generation ignores the home's own array.** `simulation/demand_model.py:1017-1025`
  converts horizontal irradiance to output with a fixed `SOLAR_KWP = 3.5` and a 0.85 performance
  factor; both callers (`demand_model.py:1139`, `run_phase2b.py:735`) take the default, so a home
  drawn at 2.5 or 4.5 kWp generates as 3.5 kWp. There is no tilt, azimuth, shading, degradation or
  inverter clipping.
- **The annual figure is a separate, older constant.** `simulation/household.py:301-309` gives
  `kWp × 850`; the company's own estimator (`company/regulatory/seg_export_estimator.py:28-39`)
  records that 850 cited a source that does not state it and uses 882 plus five sunshine bands.
- **Kit arrives by flat yearly odds.** `simulation/life_events.py:107-118` (solar 0.23-0.40% a year
  per eligible home), `:163-174` (battery 0.2-4.5% a year per solar home), `:512` (kWp uniform
  2.5-4.5 in every year) and `:526` (battery uniform 4.0-13.5 kWh). The drawn population starts with
  no solar at all (`simulation/premise_population.py:94-98, 972`) except where NEED's PV flag is set
  (`:1069`), which takes an inherited 3.8 kWp (`:999`).
- **The battery has one mode.** `simulation/run_phase2b.py:617-652` charges only from surplus solar,
  outside 16:00-20:00, at a fixed 90% round trip, and discharges 16:00-20:00. No grid charging, no
  reserve floor, no tariff awareness, no idle winter, no capacity fade.
- **The company assumes 50% self-use without a battery and 70% with one**
  (`seg_export_estimator.py:88-89`). Measured GB self-use without a battery is 37-57% and typically
  37-45% (§3); SAP gives 0.40 for a 2.5 kWp / 3,100 kWh home. 0.50 is at the upper end.
- **The SEG price is one number per year** (`company/billing/seg_portfolio.py:15-22`, 5.5p-15p,
  unsourced). Published SEG tariffs ran 1-25p in Sep 2026; the realised average in SEG Year 5 was
  12.9p across all registered generators (§5).

## 1. Stock

- DESNZ to August 2026: 23.2 GW across about 2,131,000 installations of all sizes; 291,000 new in
  the last 12 months, the most since 2012. (Solar Power Portal citing DESNZ, 1 Oct 2026.)
- DESNZ Solar PV cost data, 28 May 2026 (MCS basis, GB, fetched 2026-10-25): 265,682 installations
  in the 2025/26 analysis, a record and 28% up on 2024/25; 176,894 domestic, 60.6% of those 0-4 kW
  and 36.5% 4-10 kW **[derived from the workbook]**; over 85% of domestic retrofits.
  https://assets.publishing.service.gov.uk/media/6a1709cc65bc5f798327f404/Solar_Costs_2025-26__DNC_.xlsx
- Feed-in Tariffs, end of Scheme Year 15 (Mar 2025): 869,659 accredited installations, 6.49 GW,
  99.56% PV, 95.38% domestic; the scheme opened 1 April 2010 and closed to new applicants from
  1 April 2019 (Ofgem, fetched 2026-10-25). FiT systems are about 41% of today's installations
  **[derived]**. https://www.ofgem.gov.uk/transparency-document/feed-tariffs-annual-report-scheme-year-15-april-2024-march-2025
- Smart Export Guarantee, end of Year 5 (Mar 2025): 270,395 registered installations, 1,585 MW,
  99.98% PV (Ofgem, fetched 2026-10-25). Against about 2.1m installations, most PV homes are not on
  a SEG tariff. https://www.ofgem.gov.uk/transparency-document/smart-export-guarantee-annual-report-april-2024-march-2025
- Batteries: MCS-certified 20,044 in 2024 and over 40,000 in 2025; DESNZ Apr 2024-Mar 2025,
  newbuild excluded, n = 22,398: 9,855 at 1-5.99 kWh, 7,956 at 6-10.99, 4,587 at 11-29.99; total
  193.4 MWh, mean about 8.6 kWh **[derived]** (Solar Power Portal citing DESNZ and MCS; the DESNZ
  battery release itself was not located on gov.uk). Attachment about 15-20 per 100 new PV systems
  in 2025, about 2.5 in 2023 **[derived]**.

## 2. Generation physics

- Fleet yield: about 770 ± 100 kWh/kWp in the 2006 field trial, about 900 ± 70 by 2015 (Sheffield
  Solar, REF2021). FiT median load factor 9.2% in 2024/25, the series low (806 kWh/kWp), against a
  10.1% mean over 14 years (DESNZ, fetched; detail on `pv-roofs-orientation-and-yield`).
- Orientation and tilt: east or west about 0.76-0.84 of south, north about 0.50-0.65, any pitch
  15-50° within about 10% of the best for its azimuth (PVGIS grid run 2026-10-25 and trade sources;
  see the roofs page).
- Degradation: median 0.5%/yr, mean 0.8%/yr over 2,128 reported rates (NREL, Jordan and Kurtz);
  IEA PVPS assumes 0.7%/yr. Panels 30 years, inverter 15 years (IEA PVPS), so about one inverter
  replacement per panel life **[derived]**.
- Inverter conversion about 96-97% **[unverified; still open]**; Tesla quotes 97% solar-to-grid.
- Season: a south-facing 35° array in London gives about 35% of its year in April-June and about 15%
  in October-December (PVGIS-SARAH2 2005-2020, run 2026-10-25) **[derived]**; the FiT fleet's
  2024/25 quarters were 13.6% and 4.7% load factor (DESNZ).
- At grid level solar was 18.5 TWh, 6.5% of GB generation, in 2025, peaking at 42.9% of supply in
  one half-hour (Energy Dashboard).

## 3. Self-consumption and export

| Evidence | Self-consumption | Source |
|---|---|---|
| 302 UK homes, 1-min data | 45% of generation (855 kWh/yr) | McKenna, Pless and Darby 2018 |
| Oxford policy brief | ~37%; homes export 55-63%, more than FiT's deemed 50% | Oxford |
| GB subset of an international set, n = 751 months | ~57% **[derived]** | McKenna et al. eceee 2019 |
| SAP 10.2, 3,100 kWh home, 2.5 kWp | 0.40 no battery; 0.65 with 5 kWh; 0.86 with 10 kWh | BRE S10TP-07 |
| Review | battery of 0.5-1 kWh/kWp adds 13-24 points; demand shifting 2-15 | Luthander et al. 2015 |
| SE England trial, 2 kWh | ~44% → ~50% summer, ~40% → ~49% winter | Bruce-Konuah and Gupta |

- SAP's monthly self-use factor β = exp(−C1·(C2·E/D)^C3), E monthly generation, D monthly demand:
  C1 = 1.610 − 0.0973·Cbat, C2 = 0.415 − 0.00776·Cbat, C3 = 0.511 + 0.0866·Cbat, Cbat usable
  battery kWh capped at 15 (BRE S10TP-07 v1.4, fetched and confirmed 2026-10-25).
  https://bregroup.com/documents/d/bre-group/s10tp-07-pv-self-use-factor-calculation_v1_4
- Who is home matters most: at generation equal to demand, self-use is about 20% when 10% of demand
  is in daytime and about 80% when 60% is (eceee 2019). EST paybacks: London 10 years home all day vs
  12 out until 6pm; Belfast 13 vs 21 (MoneyWeek citing EST, Apr 2026).
- SAP does not model diverters; no measured GB uplift from a diverter or an EV was found.

## 4. Battery behaviour and settings

- Round trip 89% (Tesla Powerwall 3 datasheet, solar to battery to grid, beginning of life, 25°C).
- Usable vs nominal differ on older or cheaper units (a 2 kWh trial unit ~60% usable).
- Warranty: at least 70% usable at 10 years; unlimited cycles for self-consumption and time-of-use,
  37,800 kWh throughput cap under third-party or wholesale use (SolarQuotes on the Tesla warranty).
- Levers: self-consumption mode, timed grid charge to a target state of charge, timed export, a
  reserve floor; schedules by start, end and target (GivEnergy).
- Supplier-run optimisation: Octopus Flux (1 Jul 2026) peak 16:00-19:00, off-peak 02:00-05:00;
  Intelligent Flux sets import equal to export and Octopus controls the battery (SunSave).
- Settings decide value: one full 5 kWh cycle a day, off-peak charge and peak export on Flux, is
  about 57p a day; charged from solar that would export at 10.11p it is about 90p; £210-330 a year
  from arbitrage alone **[derived, 89% round trip]**. A battery idle in winter or held at a high
  reserve loses most of this.

## 5. Economics

- DESNZ median £/kW (DNC basis, cash prices; fetched 2026-10-25):

| Year | 0-4 kW | 4-10 kW | 10-50 kW | Installations analysed |
|---|---|---|---|---|
| 2013/14 | 1,897 | 1,564 | 1,332 | 58,916 |
| 2016/17 | 1,667 | 1,412 | 1,150 | 26,094 |
| 2019/20 | 1,481 | 1,574 | 1,023 | 29,332 |
| 2021/22 | 1,732 | 1,532 | 1,016 | 75,507 |
| 2022/23 | 2,250 | 2,080 | 1,232 | 161,258 |
| 2023/24 | 2,263 | 2,206 | 1,375 | 177,206 |
| 2024/25 | 1,884 | 1,780 | 1,257 | 208,049 |
| 2025/26 | 1,780 | 1,697 | 1,262 | 265,682 |

  Inflation-adjusted medians fell 9%, 8% and 3% in 2025/26; 0-4 and 4-10 kW are at record lows in
  real terms. Costs include VAT where applicable and exclude batteries. Domestic 2025/26 mean
  £2,096/kW (0-4 kW) and £1,785/kW (4-10 kW).
- MCS average solar install £9,994 (2023), £8,198 (2024), just over £7,000 (2025).
- Battery: MCS average £9,343 (2023), £8,035 (2024); DESNZ median £/kWh £1,020 (1-5.99 kWh), £900
  (6-10.99), £590 (11-29.99) (Solar Power Portal citing DESNZ).
- VAT: zero-rated on roof-mounted solar since the 2022 Spring Statement and on retrofit and
  standalone batteries from 1 Feb 2024, reverting to 5% after 31 Mar 2027 (ICAEW; Wind & Sun).
- SEG: tariffs 1.05p-25p (Sep 2026): open-to-all mostly 3-6p, own-customer 8-18p, install-tied up
  to 20-25p. SEG Year 5: 443.1 GWh exported, £56.97m paid, 50 tariffs from 11 licensees (Ofgem,
  fetched), an average of 12.9p/kWh **[derived]**. That average covers every registered generator
  up to 5 MW, not homes alone, so it is not a domestic export price.
- FiT legacy: SY15 just under 8.0 TWh generated across all FiT technologies, £1.73bn generation
  payments, 1.5 TWh exported for about £94.1m (Ofgem, fetched). Export from PV up to 30 kW without
  an export meter is deemed at 50% of generation. Tariff by vintage **[unverified; still open]**.
- EST paybacks (Apr 2026): London 10-12 years, Manchester 11-13, Stirling 12-15, Belfast 13-21.

## 6. Carbon

- GB average 128.8 gCO₂/kWh in 2025 (Energy Dashboard). A 4 kWp system at 3,800 kWh/yr displaces
  about 490 kg a year at that average **[derived]**.
- Midday PV and exports displace gas at the margin, so a marginal factor would be higher; the Green
  Book long-run marginal factors were not extracted (gap).
- A battery saves carbon only if the evening margin is dirtier than the night margin by more than
  its ~11% round-trip loss **[derived]**.
- Embodied carbon about 20-50 gCO₂e/kWh and a 5-12 year carbon payback **[unverified; still open]**.

## 7. What a supplier can see, infer and must ask

| Attribute | Observe | Infer (method, error) | Ask |
|---|---|---|---|
| PV present | export reads if an export MPAN is registered | midday dip in net import (Chen et al. arXiv 2105.08122) | confirm |
| kWp | FiT or MCS record if held | from net load, rough | yes |
| Orientation and tilt | – | within 4.5°/4.3° with generation data (Meng et al. 2020); coarse from net load | yes |
| Generation | FiT generation meter if the licensee; inverter API with consent | disaggregation | – |
| Export | half-hourly if registered | FiT's deemed 50% is biased low (Oxford) | – |
| Battery present and size | API with consent | evening flat import, charge blocks **[unverified pattern]** | yes |
| Battery settings | API with consent | partly from timing | yes |
| Inverter brand | – | – | yes (decides smart-tariff eligibility) |
| Install date | FiT records if the licensee | – | yes |
| Occupancy | – | daytime base load | yes |

## 8. Proving savings

- A generation meter or inverter API gives true generation; without one, generation is inferred and
  its error carries into the claim.
- A before-and-after bill comparison is confounded by weather, occupancy and tariff; normalise
  generation to PV_Live regional yield or irradiance and demand to degree days, and compare with a
  matched group of non-adopters in the supplier's own book.
- Attribute separately: self-use, export income, battery shift and tariff change. A Flux switch
  alone changes the bill with no hardware.
- No GB measurement-and-verification protocol for PV and batteries was found; IPMVP is the usual
  reference **[unverified; still open]**.

## Headline bands for checking the world

| Quantity | Band | Basis |
|---|---|---|
| GB PV installations, Aug 2026 | ~2.13m; 23.2 GW all sizes | DESNZ via SPP |
| FiT share of installations | ~41% | Ofgem SY15 **[derived]** |
| New domestic system | 60% at 0-4 kW, 36% at 4-10 kW (2025/26) | DESNZ cost data |
| Fleet specific yield | 806-920 kWh/kWp by year | DESNZ FiT load factors |
| Degradation | 0.5-0.8%/yr | NREL |
| Self-use, no battery | 37-57%, typically 37-45% | §3 |
| Self-use, ~5 kWh battery | +13-25 points (SAP 0.40 → 0.65) | BRE |
| Battery attachment, new PV, 2025 | ~15-20% | MCS, SunWiz **[derived]** |
| Battery size, mean | ~8.6 kWh | DESNZ via SPP |
| Round trip | ~89% | Tesla |
| PV cost, 0-4 kW median | £1,780/kW (2025/26), £2,263 at the 2023/24 peak | DESNZ |
| Battery £/kWh | £590-1,020 by size band | DESNZ via SPP |
| SEG tariffs | 1-25p; all-generator realised average 12.9p | SunSave; Ofgem **[derived]** |

## 9. Verification of the pack's [unverified] items (2026-10-25)

| Item | Outcome | Source |
|---|---|---|
| FiT start in 2010 | confirmed: introduced 1 April 2010, closed to new applicants 1 April 2019 | Ofgem FIT scheme page, accessed 2026-10-25 |
| Inverter efficiency 96-97% | still open | no primary fleet source fetched |
| FiT generation tariff by vintage | still open | Ofgem tariff tables not fetched |
| Export MPAN registration and settlement mechanics | still open | Elexon not fetched |
| FiT meter-reading frequency | still open | Ofgem FIT guidance not read |
| Battery evening-flatline signature | still open (pattern logic, not a figure) | – |
| Embodied carbon 20-50 g/kWh and carbon payback | still open | IEA PVPS figure unreadable |
| Monthly PV and demand shapes in the payback table | PV half now sourced (PVGIS monthly, London south 35°); demand half still open | PVGIS v5.2 API, accessed 2026-10-25 |
| IPMVP as the reference protocol | still open | – |

Counts: 9 items; 1 confirmed, 0 corrected, 8 still open (one of them half closed). Sourced figures
re-read at source on the same day and confirmed: DESNZ cost series and 2025/26 counts, SAP β
coefficients, SEG Year 5 counts and payments, FiT SY15 counts and payments, FiT 2024/25 load
factor. Two named-gap fetches were closed: the DESNZ absolute £/kW series and the PVGIS grid.

## Named gaps

1. Inverter efficiency and real-world battery round trip and standby losses, measured in GB homes.
2. FiT generation tariff by vintage; reading frequency a FiT licensee receives.
3. Elexon detail on export MPAN registration and the share of PV homes with registered export.
4. Day-to-day cloud variability (PV_Live distribution) and fleet shading prevalence.
5. Measured self-use uplift from diverters and EVs; the occupancy-archetype distribution.
6. Marginal emission factors (Green Book) and DESNZ absolute 2026 factors; embodied carbon.
7. Battery and inverter API specifications and VPP payment levels (VPP page owns the latter).
8. NESO FES projections for domestic PV and batteries.
9. A GB measurement-and-verification protocol for PV and battery savings.
10. The DESNZ domestic battery cost release itself (figures read through Solar Power Portal).
11. Which?, Solar Energy UK and Energy Systems Catapult field data.
