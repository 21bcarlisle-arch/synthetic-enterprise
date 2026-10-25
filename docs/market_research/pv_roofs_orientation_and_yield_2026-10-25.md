# A GB roof's solar array: orientation, tilt, size, age, shading and the half-hourly sky it sees

**Knowledge:** pv-roofs-orientation-and-yield

Written 2026-10-25 from the advisor's cited evidence pack
`docs/staging/advisor/done/DIRECTOR_EVIDENCE_ROOFS_PV_ORIENTATION_YIELD_AND_IRRADIANCE_2026-10-25.md`
(director's chat, 25 Oct 06:03 and 06:42), one of six packs supplying the attribute distributions for
the personalised asset world (cover steer `DIRECTOR_STEER_THE_ASSET_DESIGN_NOTE_HAS_ITS_DISTRIBUTIONS_2026-10-25.md`).
Population checks here are aggregate calibration claims, never per-home targets. **[derived]** is
arithmetic on cited figures; **[unverified]** is not a claim until sourced; outcomes of the checks
made on 2026-10-25 are in §8. What the kit does inside the home (self-use, batteries, cost, carbon)
is on `solar-pv-and-home-batteries`.

**Attribution.** Where this note uses the Open Climate Fix `uk_pv` dataset, the data are © Open
Climate Fix, made possible by Sheffield Solar, licensed CC-BY-4.0, DOI 10.57967/hf/0878
(https://huggingface.co/datasets/openclimatefix/uk_pv). The director accepted its access terms on
25 Oct 2026 06:47; the metadata itself has not been downloaded, because no Hugging Face read token is
held. PVGIS results are © European Union, JRC. SARAH-3 is © EUMETSAT (CM SAF).

## 0. What this project's world does today (read from code, not run)

- **Orientation is a label by house type, not a distribution.** `simulation/household.py:433-447`
  maps rural detached to "south", suburban semi to "east_west", flats to "na", anything else to
  "east_west"; the drawn population sets every non-flat to "east_west" (`simulation/premise_population.py:983, 1106`).
  The label only gates eligibility (`simulation/life_events.py:508`: north and flats cannot install);
  it never reaches generation. These are the placeholder orientation shares, and they are
  unsourced.
- **Generation is horizontal and uniform.** `simulation/demand_model.py:1017-1025` turns horizontal
  irradiance from a clear-sky envelope times a cloud factor (`sim/weather_engine.py:281-296`,
  `SOLAR_CLOUD_ATTENUATION_K = 0.446`) into output at a fixed 3.5 kWp and 0.85 performance factor.
  No tilt or azimuth transposition, no shading, no degradation, no clipping; the home's drawn kWp is
  not used at the half hour.
- **Size and age.** kWp is drawn uniform 2.5-4.5 in every install year (`life_events.py:512`);
  NEED-flagged homes inherit 3.8 kWp and no install year (`premise_population.py:999`). The record
  shows a FiT-era fleet clustered at 2-4 kWp and a 2023+ cohort near 5-6 kWp (§2).
- **The company's yield is sunshine-banded.** `company/regulatory/seg_export_estimator.py:39-64`
  holds an 882 kWh/kWp national level and five bands 835-947 keyed on Met Office sunshine hours. The
  DESNZ FiT median series (806-920 by year) is the fleet's measured counterpart and sits mostly
  below 882 in recent years.

## 1. Azimuth and tilt

- **No GB-wide published azimuth distribution was found.** The best source is the Open Climate Fix
  `uk_pv` metadata (per-system orientation, tilt and kWp for over 30,000 systems, 2010-2025;
  CC-BY-4.0; gated). Its card gives no orientation or tilt statistics.
- Killinger et al. 2018: 2.8m systems in Europe, the US, Japan and Australia; mean tilt by country
  16.1° (Australia) to 35.6° (Belgium); "almost all countries face the equator"; UK median size
  2.94 kWp. The UK cluster's tilt and azimuth parameters are in the full text, which was not read.
- Stowell et al. 2020: over 260,000 UK installations (ODbL); only 8.5% of OSM-mapped panels then
  carried an orientation tag, so OSM is weak for azimuth shares.
- Yorkshire field evidence (Dhimish et al.): tilts 31-46°, optimum 38-43°; systems facing within a
  few degrees of south gave the most, a near-east (−87°) one the least.
- Roof pitch "15° and 30° to 50°" is second-hand (roofing blog via Cao and Bukhsh 2024). BRE and EHS
  roof data were not reached.
- Multi-plane and east/west split prevalence: no GB figure.

## 2. System size, DC/AC ratio and clipping

- OCF card, kWp bins (fetched 2026-10-25): [0,1] 473; (1,2] 4,809; (2,3] 13,203; (3,4] 11,854;
  (4,10] 247; (10,50] 158; (50,100] 6; (100,150] 2; (150,200] 2; (200,250] 3; total 30,757. So
  81.5% of the sample is 2-4 kWp **[derived]**. Volunteer-recruited and FiT-heavy.
- Recent cohorts: about 4.9 kWp mean in 2025 (Sunsave citing MCS); 17,285 residential installs and
  98 MW in Aug 2026, about 5.7 kWp **[derived]**; 2026 to August, 404.4 MW in 4-10 kW against 224.8
  MW in 0-4 kW (Solar Power Portal citing DESNZ). DESNZ cost data 2025/26: 60.6% of domestic
  installs at 0-4 kW, 36.5% at 4-10 kW (fetched).
- New builds are their own population: typically 3-4 panels, about 1-1.6 kWp (weak, trade); 35% of
  MCS rooftop installs in 2025.
- DC/AC 1.1-1.3 is described as standard (trade source). The 3.68 kW single-phase inverter matches
  the 16 A per phase limit for connect-and-notify generation (confirmed in the ENA form; see the
  network page).
- Hourly weather can overstate yield by up to about 4% for high DC/AC systems (NPL, Blakesley et al.
  2026), so generation should be computed half-hourly or finer.

## 3. Install cohorts, degradation and fleet performance

- FiT ran 1 Apr 2010 to 31 Mar 2019 (Ofgem). Small PV tariffs were cut from 43.3p to 21p (Mar
  2012), 16p (Aug 2012) and 15.44p (Nov 2012), with a 64% cut for under 4 kW in Dec 2015
  (Wikipedia, secondary).
- FiT register at end of Year 10 (Mar 2020): 867,870 installations, 98.89% PV, 95.53% domestic,
  6.43 GW; regional counts from 123,111 (South West) to 25,650 (London) (Ofgem).
- Post-FiT MCS volumes: 138,020 (2022), 189,826 (2023), about 200k (2024), 267,032 (2025);
  cumulative close to 2 million. Cohort mix about 43% FiT-era and 57% post-FiT; about a third of
  the 2023-25 volume is new build **[derived]**.
- Degradation: −0.74 to −0.86%/yr across ~8,400 European residential systems, mean PR 76.7% (PEARL
  PV); England −0.7 to −0.9%/yr, Scotland −1.0%/yr over ten years (Dhimish 2020).
- Inverters: 34.3% had a first yield-relevant failure by year 15 in a Swiss survey of larger units
  (not UK domestic).
- Share of systems still operating: no GB figure. Only 33% of FiT PV installations (282,047 of
  860,252) returned a valid load factor in 2024/25; that is a reporting artefact, not a failure rate
  (DESNZ, fetched).

## 4. Shading

- No GB data on prevalence or size of shading losses.
- MCS multiplies output by a shade factor between 0 and 1. Killinger et al. give empirical beam and
  diffuse shading equations from ~48,000 Uppsala buildings, the most transferable model found.

## 5. Specific yield by place and orientation, and year to year

**PVGIS grid, run 2026-10-25** (PVGIS v5.2, PVGIS-SARAH2 2005-2020, 1 kWp, 14% system losses;
calibration only, never a runtime input). Annual kWh/kWp facing south, and other facings as a share
of south at the same site and tilt:

| Site | S 25° | S 35° | S 45° | E/W at 35° | N at 35° | interannual SD, S 35° |
|---|---|---|---|---|---|---|
| Penzance | 1,079 | 1,099 | 1,094 | 0.78 / 0.81 | 0.54 | 45 |
| Shoreham | 1,119 | 1,145 | 1,145 | 0.76 / 0.78 | 0.50 | 35 |
| London | 1,002 | 1,025 | 1,025 | 0.80 / 0.78 | 0.53 | 40 |
| Birmingham | 947 | 969 | 969 | 0.80 / 0.78 | 0.54 | 34 |
| Manchester | 869 | 886 | 885 | 0.81 / 0.79 | 0.56 | 32 |
| Edinburgh | 891 | 916 | 921 | 0.78 / 0.77 | 0.52 | 36 |
| Aberdeen | 867 | 893 | 899 | 0.77 / 0.77 | 0.51 | 33 |

Across all seven sites and three tilts, east or west is 0.73-0.84 of south (0.81-0.84 at 25°,
0.76-0.81 at 35°, 0.73-0.78 at 45°); north is 0.41-0.65; south-east and south-west 0.92-0.96. The
interannual standard deviation is 3.4-4.1% of the annual yield. These are modelled, unshaded,
well-maintained arrays, so they sit above the fleet's measured median. Raw output:
168 rows, kept with the draft.

- Earlier reported PVGIS set (Dunsop Bridge, 35°, via Sunsave): S 921, W 754 (0.82), E 739 (0.80),
  N 526 (0.57).
- **Measured fleet, DESNZ FiT median PV load factor**: 10.5% (2011/12) … 10.3% (2019/20), 10.4%
  (2020/21), 10.2% (2021/22), 10.5% (2022/23), 9.6% (2023/24), 9.2% (2024/25, lowest in the series,
  806 kWh/kWp **[derived]**; weighted mean 8.3%); 2024/25 sun hours lowest since 2012/13; London the
  lowest region in 2024/25; spring quarter 13.6%, Oct-Dec 4.7% (DESNZ 2024/25, fetched). CV across
  14 years about 4.1% **[derived]**, confounded by ageing.
- Regional spread 2020/21: South West 11.3% (~990), London 9.8%, Scotland 9.4% (~823) **[derived]**.

## 6. Irradiance per home, half-hourly

- **CM SAF SARAH-3** (Pfeifroth et al. 2024): 0.05° grid (~3.5 × 5.5 km over GB **[derived]**),
  30-minute instantaneous global and direct, 1983 to present; bias within ±2 W/m²; free with
  "© EUMETSAT" attribution; interim record within about 2-5 days. The best fit for per-home sky:
  homes in one pixel share their sky.
- PVGIS uses SARAH (confirmed: the API reports PVGIS-SARAH2, 2005-2020 for GB sites).
- ERA5 (hourly, 0.25°) **[unverified; still open, not needed while SARAH-3 is the choice]**; its
  radiation is accumulated in J/m² over each hour, stamped at the hour's end (ECMWF forum).
- Met Office MIDAS Open: hourly global radiation at all sites, direct and diffuse at some; OGL v3;
  free CEDA account (confirmed 25 Oct, second read; CEDA catalogue, use the latest version, not v202407).
- OCF `uk_pv` 30-minute generation (>25k systems) and Sheffield Solar PV_Live regional outturn are
  measured cross-checks.
- Spatial correlation of daily cloudiness between nearby homes: not sourced.

## 7. Batteries on the fleet

- DESNZ/MCS Apr 2024-Mar 2025, n = 22,398, newbuild excluded: 44% at 1-6 kWh, 35.5% at 6-11, 20.5%
  at 11-30; mean about 8.6 kWh **[derived]**. Attachment about 2.3% (2023) to about 15% (2025) of
  new PV **[derived; upper bound, retrofits included]**; 59,000 MCS batteries cumulative by Sep 2025.
- FiT-era systems have essentially no batteries except retrofits **[unverified; still open]**.

## Distributions for the world to draw from (inputs to the asset design note)

| Attribute | Draw | Basis |
|---|---|---|
| Cohort | FiT 2010-Mar 2019 ~43%; post-FiT 2019-22 ~10%; 2023-26 ~47% **[derived]** | Ofgem, MCS, DESNZ |
| New-build flag | 35% of the 2023+ cohort | MCS |
| kWp, FiT retrofit | OCF bins: 1-2 16%, 2-3 44%, 3-4 40% of the 1-4 kWp sample **[derived]**, capped at 4 | OCF card; Killinger 2.94 median |
| kWp, 2023+ retrofit | 60% 0-4 kW / 36% 4-10 kW, mean ~5-5.7 | DESNZ cost data; SPP **[derived]** |
| kWp, new build | 1.0-2.0 | trade (weak) |
| Tilt | design choice: normal(37°, 7°) truncated 15-50° | Dhimish; Killinger |
| Azimuth | **named assumption until OCF metadata is read**: S±22.5° 45%, SE/SW 35%, E/W 15%, other 5% | none |
| East/west split | named assumption: 10% of E/W draws | none |
| DC/AC | 1.0 up to 3.68 kWp, else kWp/3.68 capped at 1.3; clip each half hour | trade; ENA 16 A per phase |
| Performance ratio | normal(0.80, 0.05) | PEARL 76.7%; trade |
| Degradation | −0.8%/yr (sd 0.2); −1.0%/yr Scotland | PEARL; Dhimish |
| Inverter | first-failure hazard reaching 34% by year 15; outage 1-6 months | Swiss survey |
| Shading | named assumption: 70% at 1.0, 20% at 0.9, 10% at 0.75 | MCS method |
| Battery, 2023+ | attach 15%; 44/35/21% by size band; mean 8.6 kWh | DESNZ/MCS |
| Sky | SARAH-3 30-minute global and direct at the home's 0.05° pixel, real years | ESSD |

## Population checks

1. Fleet median yield 806-920 kWh/kWp in each year, tracking the FiT median series; CV about 4%.
2. South West about 20% above Scotland (11.3% vs 9.4% load factor, 2020/21).
3. Quarterly load factor about 13.6% in Q2 and 4.7% in Q4 under 2024/25 weather.
4. An east- or west-only home at the same site and tilt gets 0.76-0.81 of south at 35° (0.81-0.84
   at 25°) under PVGIS. **Corrected from the pack's 0.80-0.82**, which was one site.
5. About 1.2-1.5m homes with PV; about 5% of English, 5.7% of Welsh and 6.3% of Scottish homes (OS).
6. Domestic capacity about 5.6 GW (2025).
7. Aggregate half-hourly output correlates with PV_Live regional outturn.
8. Battery mean about 8.6 kWh; about 59k or more MCS batteries by late 2025.

## 8. Verification of the pack's [unverified] items (2026-10-25)

| Item | Outcome | Source |
|---|---|---|
| Killinger UK cluster 30-40°, centred south | still open | full text not read |
| G98 3.68 kW = 16 A per phase | confirmed | ENA EVCP/HP form v3.3 (ENWL copy), accessed 2026-10-25 |
| ERA5 hourly 0.25° | still open | CDS not fetched |
| MIDAS hourly radiation | still open | CEDA not fetched |
| PVGIS uses SARAH or ERA5 | confirmed: PVGIS-SARAH2, 2005-2020, for all seven GB sites | PVGIS v5.2 API, accessed 2026-10-25 |
| FiT-era fleet has essentially no batteries | still open | – |

Counts: 6 items; 2 confirmed, 0 corrected, 4 still open. Sourced and derived figures re-checked at
source the same day: **corrected** 3 — the OCF 2-4 kWp share (81.5%, not ~84%; the pack's bin table
left out the [0,1] and (4,10] bins), the east/west factor (0.76-0.84 by tilt over seven sites, not
0.80-0.82 at one) and the north factor (0.50-0.56 at 35°, not 0.57); **confirmed** 5 — FiT 2024/25
median 9.2%, quarterly 13.6% and 4.7%, London lowest, 282,047 of 860,252 reporting, the DESNZ 0-4 kW
domestic share. Named-gap fetch closed: the PVGIS grid.

## Named gaps and design choices

1. **GB azimuth and tilt joint distribution (the largest gap).** Compute azimuth × tilt × kWp ×
   install date from OCF `uk_pv` metadata, reweighted to FiT and MCS cohort shares. Blocked on a
   read token: the director accepted the terms; a token is his to provide.
2. East/west split prevalence: use OCF's multi-orientation subset if present; otherwise keep the
   flagged parameter and test sensitivity.
3. Shading: Killinger beam and diffuse equations with a horizon drawn from building density,
   calibrated so fleet PR sits near 0.77-0.80.
4. Spatial correlation of cloudiness: let SARAH-3 pixel sharing carry it; check against OCF systems
   5-20 km apart.
5. kWp by house type and region, battery attachment by region or size: not found.
6. Systems still operating: inverter hazard plus a named 1-3% a year dead-and-unreported tail,
   calibrated against PV_Live.
7. BRE and EHS roof pitch and type; FiT register by tariff band and size; the DESNZ ET 6.3
   deployment workbook (not fetched this pass).
8. Keep generation half-hourly or finer (NPL).

## Second read: the advisor's verification pass, 25 Oct 2026

An independent read by the advisor
(`docs/staging/advisor/DIRECTOR_EVIDENCE_VERIFICATION_OF_THE_GB_PACKS_UNVERIFIED_ITEMS_2026-10-25.md`,
roofs pack). Rows follow the §8 table.

| # | Item | §8 | Advisor | Reconciled | Source |
|---|---|---|---|---|---|
| 1 | Killinger UK cluster 30-40°, centred south | still open | still open | still open (needs the paper's full text) | – |
| 2 | G98 3.68 kW = 16 A per phase | confirmed | confirmed | **confirmed** (§8 read the ENA form; the advisor's source is secondary) | https://www.decerna.co.uk/what-is-g98/ |
| 3 | ERA5 hourly 0.25° | still open | confirmed (partly) | still open: hourly J/m² accumulation confirmed; the 0.25° grid and the licence not checked | https://forum.ecmwf.int/t/surface-radiation-parameters-joule-m-2-to-watt-m-2/1588 |
| 4 | MIDAS hourly radiation | still open | confirmed | **confirmed:** hourly global radiation at all sites, OGL v3, CEDA registration; v202407 runs 1947-2023 and is superseded. §6 updated | https://catalogue.ceda.ac.uk/uuid/0afba628c2f4462da68b0a81ebf1ff4c |
| 5 | PVGIS uses SARAH or ERA5 | confirmed | confirmed | **confirmed.** The advisor adds that PVGIS 5.3 uses SARAH-3 and ERA5, 2005-2023; the grid here was run on v5.2 (SARAH-2, 2005-2020) | https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-releases/pvgis-53_en |
| 6 | FiT-era fleet has essentially no batteries | still open | still open | still open | – |

No disagreement between the reads.

**Counts: confirmed 3 · corrected 0 · still open 3.**
