# Director evidence: roofs pv orientation yield and irradiance

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 06:03 GMT: "I'm worried you are using static costs and %. The EV percentage is irrelevant. It should be derived from miles driven and car type etc."
- 06:42 GMT: "NB driveways matter too, as it only really makes sense to have an ev if you can charge from home"

This pack is one of six that supply the attribute distributions for the personalised asset world (`DIRECTOR_STEER_ASSET_DEMAND_IS_DERIVED_PER_HOME_NOT_A_STATIC_PERCENTAGE_2026-10-25.md`). The cover steer is `DIRECTOR_STEER_THE_ASSET_DESIGN_NOTE_HAS_ITS_DISTRIBUTIONS_2026-10-25.md`.

## What to do with it

- Use the "distributions to draw from" table as inputs to the asset design note.
- Use the "population checks" as aggregate calibration claims. Never use them as per-home targets.
- Treat each named gap either as a fetch for you (many were blocked in the advisor's sandbox) or as a design choice you name explicitly.
- Publish it as a Knowledge page. That is drafting work and runs alongside the serial queue.

---

# Evidence pack: GB domestic PV system characteristics and per-home irradiance for Poesys

**Scope.** This pack covers the facts Poesys needs to give each home its own PV array: orientation, tilt, kWp, age and battery, with generation computed half-hourly from that home's weather.

**How this was compiled.** The shared web-search budget ran out before I had covered every source the brief asked for. Several hosts also blocked me: the PVGIS API, zenodo.org, the gated Hugging Face files, CEDA, Copernicus CDS, the nature.com article and gov.uk xlsx downloads.

- I could not query PVGIS or download the OCF / Stowell metadata myself. Where that matters it is listed under Named gaps.
- I did not use one repository page (qmro.qmul.ac.uk). It returned obfuscated script instead of the article.

**Tags.** [derived] means my own arithmetic on the cited figures. [unverified] means a figure from memory that I could not confirm here.

---

## 1. Azimuth and tilt

**There is no GB-wide published azimuth distribution in what I could reach. The best source is the OCF `uk_pv` metadata, which I could not download.**

**The OCF / Sheffield Solar "UK PV" dataset**
- It covers "over 30,000" GB domestic systems from 2010 to 2025, at 30-minute resolution, with a 5-minute subset of about 1,309 systems ([HF card](https://huggingface.co/datasets/openclimatefix/uk_pv)).
- `metadata.csv` holds per-system `orientation` (degrees), `tilt` (degrees) and `kWp`, with lat/lon rounded.
- The licence is CC-BY-4.0, but access is gated behind accepting conditions.
- The card gives **no orientation or tilt summary statistics** ([HF card](https://huggingface.co/datasets/openclimatefix/uk_pv)).
- A discussion thread confirms more than 25,000 IDs in the 30-minute parquet, data back to 2012, and an `llsoacd` area field ([HF discussion](https://huggingface.co/datasets/openclimatefix/uk_pv/discussions/6)).

**Killinger et al. 2018 (*Solar Energy*)**
- It analysed 2,802,797 systems across Europe, the USA, Japan and Australia ([ANU record](https://researchportalplus.anu.edu.au/en/publications/on-the-search-for-representative-characteristics-of-pv-systems-da/)).
- Mean tilt by country ranges from 16.1° (Australia) to 35.6° (Belgium).
- "Almost all countries face the equator."
- The data were clustered by country and size, and distribution functions were fitted per cluster.
- The UK-specific tilt and azimuth parameters are in the paper but not in the abstract I could reach. My recollection is that the UK cluster sits around 30–40° tilt, centred on south [unverified].

**Stowell et al. 2020 (*Scientific Data*)**
- It reports over 260,000 UK installations under the ODbL licence ([Zenodo](https://zenodo.org/record/4059881)).
- The orientation statistics in the paper were not reachable.
- At the time, only **8.5%** of OSM-mapped panels (about 20,000) carried a module-count or orientation (`direction`) tag ([OSM talk-gb, Q3 2020](https://lists.openstreetmap.org/pipermail/talk-gb/2020-October/025238.html)). OSM is therefore a weak source for azimuth shares.

**Yorkshire field evidence (Dhimish et al.)**
- Over 3,600 installations were observed. Tilts in the sample ran 31–46°, with optimum tilt 38–43° (mean 40°) and optimum azimuth −10° to +1° ([White Rose PDF](https://eprints.whiterose.ac.uk/177719/1/Manuscript.pdf)).
- Systems facing −4° to +2° gave the highest four-year output. A −87° (near-east) system gave the lowest ([Clean Energy 2019](https://eprints.whiterose.ac.uk/177716)).

**Roof pitch.** A typical UK traditional pitch is "15° and 30° to 50°". This is cited second-hand from a roofing blog in [Cao & Bukhsh 2024](https://strathprints.strath.ac.uk/93708/1/Cao-Bukhsh-2024-Feasibility-testing-and-costing-study-of-a-UK-domestic-multi-orientation-rooftop-photovoltaic-system.pdf), and is weak evidence. I did not reach the BRE or English Housing Survey (EHS) roof data.

**Multi-plane and east/west splits.** I found no GB prevalence figure, only single-case evidence. On one April day, a London 5.04 kWp east/west split produced about 9 kWh per side, 18.59 kWh in total ([shkspr.mobi](https://shkspr.mobi/blog/?p=34728)).

**Change over time.** Not quantified by any source I reached.

## 2. System size (kWp), DC/AC ratio and clipping

**OCF sample size distribution** ([HF card](https://huggingface.co/datasets/openclimatefix/uk_pv)):

| kWp bin | Systems |
|---|---|
| (1, 2] | 4,809 |
| (2, 3] | 13,203 |
| (3, 4] | 11,854 |
| (10, 50] | 158 |
| > 50 | 16 |

- The range runs from 0.47 to 250 kWp.
- About 84% of the roughly 30,000 systems fall in 2–4 kWp [derived; the denominator is approximate].
- The sample is volunteer-recruited and skewed towards the FiT era.

**Medians and averages by period**
- The UK median is **2.94 kWp**, the smallest of all countries studied ([Killinger, ANU](https://researchportalplus.anu.edu.au/en/publications/on-the-search-for-representative-characteristics-of-pv-systems-da/)).
- In the Yorkshire FiT-era sample, "most systems were 4 kWp", with others 1.9–3.5 kWp ([Dhimish](https://eprints.whiterose.ac.uk/177719/1/Manuscript.pdf)).
- The 2025 average is **4.9 kWp**, attributed to MCS ([Sunsave](https://www.sunsave.energy/solar-panels-advice/installation/east-west-facing-roofs)).
- In August 2026 there were 17,285 residential installs totalling 98 MW, about **5.7 kWp mean** [derived]. Over the past 12 months, more than 1 GW went across more than 195,000 homes, about 5.1 kWp or less [derived] ([Solar Power Portal](https://www.solarpowerportal.co.uk/solar-installations/uk-installs-record-291-000-new-solar-pv-installations-in-12-month-period)).
- In 2026 to August, 404.4 MW was added in the 4–10 kW band against 224.8 MW in the 0–4 kW band ([same](https://www.solarpowerportal.co.uk/solar-installations/uk-installs-record-291-000-new-solar-pv-installations-in-12-month-period)).

**Conflicting claim.** "About 4 kWp" in 2023 against "2.4 kWp" in 2024, with no source given ([Renewable Energy Magazine / Gryd](https://www.renewableenergymagazine.com/pv_solar/gryd-says-shrinking-solar-pv-system-sizes-20250617/)). I treat it as unreliable.

**New-build homes are a distinct sub-population**
- Housebuilders typically fit 3–4 panels, about 1–1.6 kWp, to meet building regulations ([same](https://www.renewableenergymagazine.com/pv_solar/gryd-says-shrinking-solar-pv-system-sizes-20250617/)).
- New builds were **35%** of MCS rooftop installs in 2025 ([MCS](https://mcscertified.com/?p=12517); [Solar Power Portal](https://www.solarpowerportal.co.uk/solar-projects/uk-breaks-yearly-record-for-rooftop-solar-pv-installations)).

**DC/AC ratio**
- A ratio of 1.1–1.3 is described as standard UK domestic practice. The worked example is a 4.62 kWp array on a 3.68 kW inverter (1.26), with summer clipping called "modest" ([squote](https://squote.app/knowledge/solar-pv/solar-pv-system-sizing); a trade source).
- The 3.68 kW figure matches the G98 single-phase limit of 16 A per phase [unverified].

**Clipping and time resolution (NPL)**
- Hourly weather data can overestimate yield and performance ratio by up to about 4% for high DC/AC systems.
- Moving from 1-minute to 1-hour recording dropped the measured temperature-corrected PR (excluding clipped data) by about 3.5% ([Blakesley et al. 2026, EPJ PV](https://www.epj-pv.org/articles/epjpv/pdf/2026/01/pv20250043.pdf)).
- These are utility-style simulations, not residential.

**By house type and region.** Not found.

## 3. Install-year cohorts, degradation and fleet performance

**FiT tariff history** ([Wikipedia FiT](https://en.wikipedia.org/wiki/Feed-in_tariffs_in_the_United_Kingdom))
- The scheme started April 2010.
- Small PV was cut from 43.3p to 21p/kWh on 3 March 2012, to 16p on 1 August 2012, and to 15.44p on 1 November 2012.
- Arrays under 4 kW took a 64% cut in December 2015.
- The scheme closed on 31 March 2019. The term was 25 years for pre-2012 PV and 20 years after.
- Year 1 brought 28,614 solar installations, 28,028 of them domestic.

**FiT register at end of FiT Year 10 (31 March 2020)** ([Ofgem](https://www.ofgem.gov.uk/sites/default/files/docs/2020/12/feed-in_tariff_annual_report_-_year_10.pdf))
- 867,870 installations: 98.89% PV and 95.53% domestic, 6.43 GW in total.
- Year 9 added 28,998 registrations; Year 10 added 19,072.
- Regional counts for all technologies:

| Region | Installations |
|---|---|
| South West | 123,111 |
| South East | 114,073 |
| East of England | 105,949 |
| East Midlands | 87,818 |
| North West | 85,503 |
| Yorkshire and the Humber | 84,268 |
| West Midlands | 71,621 |
| Scotland | 65,036 |
| Wales | 56,546 |
| North East | 47,657 |
| London | 25,650 |

- The FiT load-factor analysis counts 860,252 PV installations commissioned and registered ([DESNZ 2024/25](https://assets.publishing.service.gov.uk/media/69403c4a33c7ace9c4a4220b/Feed-in_Tariff_load_factor_analysis_2024-25.pdf)).
- I did not reach a split by tariff band.

**Post-FiT MCS volumes**
- 138,020 installs in 2022 and 189,826 in 2023; the cumulative total from 2009 to 2023 was 1,441,753 ([Carbon Brief](https://carbonbrief.org/analysis-surge-in-heat-pumps-and-solar-drives-record-for-uk-homes-in-2023)).
- 267,032 in 2025, with the cumulative total "close to 2 million" ([MCS](https://mcscertified.com/?p=12989)).
- 2024 comes out at about 200k [derived from the 1.85m year-to-date figure in [MCS](https://mcscertified.com/?p=12517); rough].
- **Cohort mix [derived]:** about 43% FiT-era (≤ March 2019) and about 57% post-FiT. About a third of the 2023–25 volume is new build.
- Sheffield Solar puts 2010–2019 at about 1 million systems and about 13 GW ([REF 2021 impact case](https://results2021.ref.ac.uk/impact/704fd078-c4db-4ee2-824b-35b8ce2ee1f9/pdf)).

**Degradation**
- Across about 8,400 mostly residential European systems (Belgium-heavy), the performance loss rate is **−0.74 to −0.86%/yr** and the mean PR is **76.7%** ([PEARL PV, U. Twente](https://research.utwente.nl/en/publications/performance-analysis-and-degradation-of-a-large-fleet-of-pv-syste/)).
- Ten-year data from 7 residential systems: England −0.7 to −0.9%/yr, Scotland −1.0%/yr, Ireland −0.4 to −0.6%/yr ([Dhimish 2020](https://eprints.whiterose.ac.uk/177727)).
- PV_Live adjusts capacity for "module degradation and installation date" ([REF case](https://results2021.ref.ac.uk/impact/704fd078-c4db-4ee2-824b-35b8ce2ee1f9/pdf)).

**Inverter failure**
- In a Swiss survey of 2,121 inverters (mostly 10–15 kVA, so not UK domestic), **34.3%** had their first yield-relevant failure by year 15 and more than 65% had none ([pv magazine](http://www.pv-magazine-australia.com/2023/02/10/survey-shows-34-3-failure-rate-for-residential-inverters-over-15-years/)).

**Fleet yield over time**
- The UK average rose from 770 (±100) kWh/kWp in the 2006 field trials to **900 (±70) kWh/kWp by 2015** ([REF case](https://results2021.ref.ac.uk/impact/704fd078-c4db-4ee2-824b-35b8ce2ee1f9/pdf)).

**Share of systems still operating.** No GB figure found. As a weak proxy, only 33% of FiT PV installations returned a valid annual load factor in 2024/25 (282,047 of 860,252). This is a reporting artefact, not a failure rate ([DESNZ 2024/25](https://assets.publishing.service.gov.uk/media/69403c4a33c7ace9c4a4220b/Feed-in_Tariff_load_factor_analysis_2024-25.pdf)).

## 4. Shading

**There is no GB data on how common shading is, or how big the losses are.**

- The MCS method multiplies output by a shade factor SF between 0 and 1 (kWp × Kk × SF) ([OpenSolar](https://support.opensolar.com/hc/en-us/articles/12362712299151-How-to-use-the-MCS-calculator)).
- Killinger et al. derive two empirical shading equations from about 48,000 Uppsala buildings: beam loss as a function of solar elevation, and a diffuse view factor as a function of tilt ([ANU](https://researchportalplus.anu.edu.au/en/publications/on-the-search-for-representative-characteristics-of-pv-systems-da/)). This is the most transferable model I found.
- Indirect: a Dutch house's panels nearer growing trees showed a 0.923%/yr average decline ([Elsevier record](https://researchcollaborations.elsevier.com/en/publications/analysis-of-performance-degradation-of-domestic-monocrystalline-p/)).

## 5. Specific yield by region and orientation, and year-to-year variation

**I could not query PVGIS directly. The values below are PVGIS outputs reported by others, plus fleet measurements.**

**PVGIS orientation set** (Dunsop Bridge, central GB; 35°, 14% losses, 4.9 kWp) ([Sunsave](https://www.sunsave.energy/solar-panels-advice/installation/east-west-facing-roofs)):

| Facing | kWh/kWp [derived] | Relative to south |
|---|---|---|
| South | **921** | 1.00 |
| West | **754** | 0.82 |
| East | **739** | 0.80 |
| North | **526** | 0.57 |

**Vertical façade, PVGIS:** London facing south at 90° gives about 768 kWh/kWp; Inverness facing west at 90° gives about 430 kWh/kWp [derived from 0.8 kWp totals] ([balkon.solar](https://balkon.solar/news/2026/03/27/can-pluginpv-work-in-the-uk/)).

**Indicative trade-source values** (said to be PVGIS-like, not reproducible) ([squote](https://squote.app/knowledge/solar-pv/solar-pv-system-sizing)):

| Location | Orientation | kWh/kWp |
|---|---|---|
| London | S 35° | ~1,000 |
| London | SW 30° | ~970 |
| Midlands | S | ~940 |
| Manchester | S | ~880 |
| Edinburgh | S | ~840 |
| South East | E 35° | ~730 |

**Yorkshire modelled 4 kWp systems:** 3,350 (Keighley) to 4,010 (Hull) kWh/yr, i.e. **838–1,003 kWh/kWp** [derived] ([Dhimish](https://eprints.whiterose.ac.uk/177719/1/Manuscript.pdf)).

**MCS Kk tables:** 21 zones, with values per pitch and orientation, "derived from … PVGIS" ([Payaca](https://payaca.com/uk/solar-yield-calculator)). The tables themselves were not retrieved.

**Measured fleet: FiT median PV load factor by FiT year**

| FiT year | Median LF | kWh/kWp [derived, ×8,760] |
|---|---|---|
| 2011/12 | 10.5% | 920 |
| 2012/13 | 9.6% | 841 |
| 2013/14 to 2015/16 | 10.4% | 911 |
| 2016/17 | 10.1% | 885 |
| 2017/18 | 9.8% | 858 |
| 2018/19 | 10.5% | 920 |
| 2019/20 | 10.3% | 902 |
| 2020/21 | 10.4% | 911 |

Sources: [DESNZ 2020/21](https://assets.publishing.service.gov.uk/media/61c3164c8fa8f54c0e4571b5/Feed-in_Tariff_load_factor_analysis_2020-21.pdf). Later years: 10.2% (2021/22), 10.5% (2022/23) ([DESNZ 2022/23](https://assets.publishing.service.gov.uk/media/6581ad6a23b70a000d234c2c/Feed-in_Tariff_load_factor_analysis_2022-23.pdf)); about 9.6% (2023/24) and **9.2% (2024/25, the series low; 806 kWh/kWp)** ([DESNZ 2024/25](https://assets.publishing.service.gov.uk/media/69403c4a33c7ace9c4a4220b/Feed-in_Tariff_load_factor_analysis_2024-25.pdf)).

- **Year-to-year variation:** across the 14 years, the mean is 10.14% and the standard deviation 0.42 points, so the **CV is about 4.1%** [derived]. This is confounded by fleet ageing.
- Sunshine hours drive the year-to-year change: 2022/23 had about 6% more sun and load factors rose ([DESNZ 2022/23](https://assets.publishing.service.gov.uk/media/6581ad6a23b70a000d234c2c/Feed-in_Tariff_load_factor_analysis_2022-23.pdf)).
- **Regional spread:**
  - 2020/21: South West 11.3% (990 kWh/kWp), London 9.8% (858), Scotland 9.4% (823) [derived].
  - 2022/23: South West and East of England 11.0% (964) [derived].
  - In 2024/25, London was the lowest region ([DESNZ](https://assets.publishing.service.gov.uk/media/69403c4a33c7ace9c4a4220b/Feed-in_Tariff_load_factor_analysis_2024-25.pdf)).
- **Seasonality, 2024/25:** the April–June quarter averaged 13.6% and October–December 4.7% (same source).

## 6. Irradiance data per location, half-hourly

**CM SAF SARAH-3** ([Pfeifroth et al. 2024, ESSD](https://essd.copernicus.org/articles/16/5243/2024/))
- 0.05° grid (about 3.5 × 5.5 km over GB [derived]).
- **30-minute instantaneous** values, 1983 to present.
- Parameters: global (SIS), direct (SID) and DNI. No diffuse product is listed, so diffuse comes from SIS − SID [derived approach].
- Validation: bias within ±2 W/m²; MAD about 5 W/m² monthly and about 11 W/m² daily.
- Free of charge, with "© EUMETSAT" attribution required. The operational interim record (ICDR) usually lands within about 2 days (5 days committed).
- This is the best fit for Poesys.

**ERA5 (Copernicus).** Hourly, 0.25°, with `ssrd` accumulated in J/m², under the Copernicus licence [unverified; the CDS page was blocked].

**Met Office MIDAS (CEDA).** Hourly global radiation at a sparse station network, open-government licence with CEDA registration [unverified; blocked].

**OCF Met Office UK deterministic NWP.** Zarr files on Hugging Face under CC-BY-4.0 ([HF](https://huggingface.co/datasets/openclimatefix/met-office-uk-deterministic-solar/tree/bd354fcfb9ff1ef51c51a4692bfd3f371676756e/data/2023/02/04)). Variables and resolution were not visible.

**Measured PV as a weather proxy.** OCF `uk_pv` gives 30-minute generation for more than 25k systems, CC-BY ([HF](https://huggingface.co/datasets/openclimatefix/uk_pv)). PV_Live gives half-hourly national and regional outturn ([REF](https://results2021.ref.ac.uk/impact/704fd078-c4db-4ee2-824b-35b8ce2ee1f9/pdf)).

**PVGIS** uses SARAH or ERA5 and offers hourly series and monthly yield by tilt and azimuth [unverified; JRC pages blocked].

**Spatial correlation of daily cloudiness between nearby homes.** Nothing found within budget; see Named gaps.

## 7. Batteries

**Size distribution, DESNZ/MCS, April 2024 – March 2025** ([Solar Power Portal](https://www.solarpowerportal.co.uk/energy-storage/desnz-over-22-000-domestic-batteries-installed-in-past-year))
- 22,398 domestic batteries totalling 193.39 MWh, so the **mean is about 8.6 kWh** [derived].

| Size band | Systems | Share [derived] |
|---|---|---|
| 1–5.99 kWh | 9,855 | 44% |
| 6–10.99 kWh | 7,956 | 35.5% |
| 11–29.99 kWh | 4,587 | 20.5% |

- New builds are excluded from these figures.

**Attachment rate over time [derived; an upper bound, because retrofits are included]**

| Year | Solar installs | Batteries | Ratio | Source |
|---|---|---|---|---|
| 2023 | 189,826 | 4,400 | 2.3% | [Carbon Brief](https://carbonbrief.org/analysis-surge-in-heat-pumps-and-solar-drives-record-for-uk-homes-in-2023) |
| May 2025 | 21,125 | ~3,400 | ~16% | [ESS News](https://www.ess-news.com/2025/06/20/uk-set-battery-record-in-may/) |
| 2025 | 267,032 | >40,000 | ≤15% | [MCS](https://mcscertified.com/?p=12989) |

- The cumulative MCS battery total was 59,000 at the end of September 2025 ([MCS](https://mcscertified.com/?p=12517)).

**Attachment by region or system size.** Not found. The FiT-era fleet has essentially no batteries except retrofits [unverified].

---

## (a) Distributions for the simulation to draw from

| Attribute | Draw | Basis |
|---|---|---|
| Cohort | FiT 2010–Mar 2019: ~43% (2011–12 and 2015 peaks); post-FiT 2019–22: ~10%; 2023–26: ~47% [derived] | Ofgem; MCS; Carbon Brief |
| New-build flag | 35% of the 2023+ cohort | MCS |
| kWp \| FiT retrofit | Empirical OCF bins: 1–2 (16%), 2–3 (44%), 3–4 (40%) [derived], capped at 4.0 | HF card; Killinger median 2.94 |
| kWp \| post-2023 retrofit | Lognormal, mean ~5.5, mostly 4–10 [design choice anchored on 5.1–5.7 derived] | SPP |
| kWp \| new build | Uniform 1.0–2.0 | Gryd (weak) |
| Tilt | Normal(37°, 7°), truncated to 15–50° [design choice] | Dhimish 31–46°; Killinger ≤35.6° |
| Azimuth | **Placeholder:** S±22.5° 45%, SE/SW 35%, E/W 15%, other 5% [assumption, no source] | Replace with OCF metadata |
| East/west split share | 10% of E/W draws [assumption] | none |
| DC/AC | 1.0 if ≤3.68 kWp, else kWp/3.68 capped at 1.3; clip per half-hour | squote; G98 [unverified] |
| Performance ratio | Normal(0.80, 0.05) | PEARL 76.7%; trade 80–85% |
| Degradation | −0.8%/yr (sd 0.2); −1.0%/yr in Scotland | PEARL; Dhimish |
| Inverter | Hazard giving 34% first failure by year 15; outage of 1–6 months | Swiss survey |
| Shading SF | Placeholder: 70% at 1.0, 20% at 0.9, 10% at 0.75 [assumption] | MCS SF method |
| Battery (2023+ cohort) | Attach 15%; size 44% 1–6 kWh, 35% 6–11, 21% 11–30; mean 8.6 | DESNZ/MCS |
| Weather | SARAH-3 30-min SIS/SID at the home's 0.05° pixel, real years | ESSD |

## (b) Population checks

1. Fleet median specific yield (kWh/kWp) should fall in 806–920 for each year and track the FiT median load-factor series. The CV should be about 4% (DESNZ).
2. The South West should be about 20% higher than Scotland (11.3% against 9.4% in 2020/21).
3. Quarterly load factor should be about 13.6% in Q2 and about 4.7% in Q4 for 2024/25 weather.
4. An east- or west-only home should get 0.80–0.82 of a south-facing home's yield at the same site (PVGIS via Sunsave).
5. Count roughly 1.2–1.54 million homes with PV ([OS](https://www.ordnancesurvey.co.uk/blog/where-the-most-solar-panels-in-britain-are); [Gryd/gov](https://www.renewableenergymagazine.com/pv_solar/gryd-says-shrinking-solar-pv-system-sizes-20250617/)), on about 5% of English homes, 5.7% in Wales and 6.3% in Scotland (OS).
6. Domestic capacity should be about 5.6 GW (2025, [Gryd/gov](https://www.renewableenergymagazine.com/pv_solar/gryd-says-shrinking-solar-pv-system-sizes-20250617/)).
7. Aggregated half-hourly output should correlate with PV_Live regional outturn.
8. Battery mean should be about 8.6 kWh. The battery count should be about 59k or more by late 2025.

## (c) Named gaps and suggested design choices

1. **GB azimuth and tilt distribution (the biggest gap).** Accept the OCF `uk_pv` terms and compute the empirical joint distribution of orientation × tilt × kWp × install date from `metadata.csv`, then sample from it directly. The sample is volunteer-biased, so reweight it to FiT and MCS cohort shares. Also check the UK cluster parameters in Killinger 2018 (full text) and the orientation analysis in Stowell 2020.
2. **East/west split prevalence.** Use the multi-orientation subset of OCF if it exists. Otherwise keep a flagged parameter and run sensitivity tests.
3. **PVGIS grid.** Re-run on a machine with PVGIS access for about 6 locations (Penzance, Shoreham, London, Birmingham, Manchester, Edinburgh, Aberdeen) × 8 azimuths × 3 tilts (25/35/45°). Use the results only as a calibration target, since generation itself comes from SARAH-3.
4. **Shading.** No GB prevalence data. Use the Killinger beam/diffuse equations with a per-home horizon drawn from a building-density proxy (e.g. LSOA urban/rural class), and calibrate so fleet PR matches about 0.77–0.80.
5. **Spatial correlation of cloudiness.** Not sourced. Let SARAH-3 pixel sharing carry the correlation: homes in the same 0.05° pixel share irradiance. Add independent sub-pixel noise only at sub-hour scale. Check empirically by correlating OCF systems within 5–20 km by distance.
6. **kWp by house type and region, and battery attachment by region or size.** Not found. Condition kWp on roof area from the EHS / OS building footprint when that is sourced. Keep battery attachment conditional on cohort only.
7. **Systems still operating.** No GB rate. Model inverter hazard plus a 1–3% per year "dead and unreported" tail [assumption], and calibrate against PV_Live capacity-adjusted yield.
8. **BRE / EHS roof pitch and type, and the Ofgem FiT register by tariff band and size.** Not retrieved because the search budget ran out. These are the next pulls. The DESNZ ET 6.3 workbook (size bands by month, 2010 to August 2026, OGL) is at [data.gov.uk](https://ckan.publishing.service.gov.uk/dataset/solar-photovoltaics-deployment/resource/87e41f09-5caf-4960-a830-dfab48a2b13a) but the download was blocked here.
9. **Resolution of the weather input.** Keep generation half-hourly or finer. NPL shows hourly inputs overstate yield by up to about 4% for clipped systems ([EPJ PV](https://www.epj-pv.org/articles/epjpv/pdf/2026/01/pv20250043.pdf)).