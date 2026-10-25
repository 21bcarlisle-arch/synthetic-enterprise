# GB household heating behaviour, hot water, comfort and health floors

**Knowledge:** heating-behaviour-comfort-and-health-floors

Written 2026-10-25 for the director's advice-roadmap and asset-world steers of 25 Oct, from the
advisor's cited evidence pack `docs/staging/advisor/done/DIRECTOR_EVIDENCE_HEATING_BEHAVIOUR_COMFORT_AND_HEALTH_FLOORS_2026-10-25.md`. Figures marked **[derived]** are the
pack author's arithmetic on the cited numbers; **[unverified]** items are recollection and not claims
until sourced. Each [unverified] item was checked at its primary source on 25 Oct 2026; the outcomes are
in section "Checks made 2026-10-25" below, and corrections are made beside the claim. The distributions the half-hourly thermal and gas model draws from (setpoints, schedules, hot water), the temperatures homes actually reach, the 2022/23 response, and the health floors that bind advice. How the boiler converts gas is on `gas-boilers-and-heating-controls`.

Headline bands here are calibration for the whole simulated population, never targets for one home.

## What this project does today (read from code, not run)

### The world (simulation/)

- **Setpoint.** `simulation/fabric_physics.py:946-949`: N(20.0, 1.48) clipped 17-24°C, plus an EPC-band
  offset from EFUS-T measured living-room temperatures (`fabric_physics.py:974-976, 1066-1075`), drawn
  once per premise (`heating_schedule_for`, `fabric_physics.py:1086-1142`). Matches EFUS 2017 (median 20,
  IQR 19-21). The clip at 17°C means no home sets below 17°C; SERL 2023 found 15.2% below 18°C and a
  2023 SD of 2.28°C. Not a defect for 2016-21; FLAG for 2022+: the setpoint never moves.
- **The 2022 response scales whole-fuel kWh, not the thermostat.** `simulation/price_response.py`
  (module docstring): per-household SERL elasticity applied to the fuel; "SERL's top quintile cut its
  thermostat, which would reshape the heating day. That shape change is not modelled." So no simulated
  home falls below 18°C because of price, and the "share below 18°C rose 6.7% → 15.2%" check cannot be
  reproduced. FLAG.
- **Schedule.** `fabric_physics.py:1048-1050, 1119-1132`: hours by daytime presence (8.5 / 7.0 / 6.0 h,
  EFUS Table) and twice-daily share by presence (48 / 60 / 77%). Matches EFUS's presence cut.
  - FLAG: **once-a-day homes get one evening block of the same 6-8.5 h** (`fabric_physics.py:1127-1132`:
    "one block from home-time, which is what EFUS's single-period households overwhelmingly report").
    EFUS 2017 Fig 3.6: the once-a-day period's median is **15.0 h** (14.5 h in 2011), and its split is
    39% from wake-up for 11-16 h, 19% from evening for 17 h+, only 17% from home-time for 4-10 h. The
    code's comment and the source disagree; the once-a-day home is under-heated by about half.
  - FLAG: no "three or more periods" (19% of regular heaters), no irregular/manual heating (27% of
    centrally heated homes), no all-year heating (6%). Boiler homes are never `continuous`
    (`fabric_physics.py:1133`: continuous only for weather-compensated systems), so the ~31% measured
    flat profile can only emerge from setback and fabric.
  - Setback 2.5-6.0°C uniform (`fabric_physics.py:1078-1079`): unsourced; the pack has no setback
    distribution either (EST advises 12-15°C setback temperature, i.e. absolute, not offset).
- **Hot water.** `simulation/premise_trace.py:1444-1475`: 36 + 25N L/day (SAP/BREDEM; BRE's adjusted
  line), anchored to DESNZ DHW24's 4.2 kWh/day median gas. Matches the pack. No per-home dispersion
  term found in this read (DHW24 P10-P90 19-222 L/day) - not checked further.
- **No electric shower anywhere** (`grep electric_shower` in simulation/ finds nothing). EFUS: 37% of
  showers, 47% in fuel-poor homes, on the electricity meter. FLAG (pack gap 7's design choice).
- **No indoor-temperature output graded against EFUS-T.** The thermal model produces
  `indoor_air_c` per half hour (`FabricDayResult`, `fabric_physics.py:1155-1170`), so comfort is already
  an output; nothing reads it against the February 18.5 / 18.1°C means or the 15.7 / 15.0°C deciles.

### The company (company/)

- `company/pricing/fabric_intervention.py:216` `HEALTH_FLOOR_INDOOR_C = 18.0` (WHO / NICE NG6), with
  `turn_down_clears_the_health_floor` (`:290-318`) refusing a 1°C turn-down where the EPC band's
  measured temperature minus 1 is below 18, and refusing on an unknown band (fail closed). The band
  never arrives (`:246-255`), so no household is offered a turn-down today.
- `TURN_DOWN_DEMAND_REDUCTION = 0.06` of fabric heat (`:267`). The pack: EST ~10% of heating per °C;
  SERL observational -3.8% of total gas per °C (2022/23). 6% of fabric heat sits between them; OK as a
  conservative figure, and its docstring says so.

### Health-floor rules the advice code would need and does not have

1. A **higher floor for over-65s, chronic illness and PSR households** ("a little above 18°C", 18°C
   overnight; COPD ≥21°C for ≥9 h) - PHE 2014. Today one 18°C floor for all.
2. **Never advise a cut to a household already below 18°C or self-rationing; route to support** (SLC 27A,
   NG6). Today the band proxy catches EPC E-G by construction but nothing reads the household's own
   rationing state; `simulation/self_rationing.py` models rationing in the world, and the company has
   no observable of it wired to advice.
3. **Flag any room-hour below 16°C** as elevated risk (PHE, UKHSA). Needs the world's indoor
   temperature graded first (above).
4. **Infant sleeping rooms 16-20°C** (PHE).
5. **Stored hot water ≥60°C; outlets 50°C within a minute; >44°C a scald risk for the vulnerable** (HSE).
   No hot-water advice exists yet, so nothing to violate; the rule must arrive with the first one.
6. Lowered flow temperature must still reach the setpoint at design-cold conditions.
Ofgem sets no temperature rule; these are Poesys policy resting on WHO, PHE, NICE and HSE, and the
advice build should say so where it cites them.

## Checks made 2026-10-25

Each [unverified] item in `DIRECTOR_EVIDENCE_HEATING_BEHAVIOUR_COMFORT_AND_HEALTH_FLOORS_2026-10-25.md`,
plus the figures that feed its population checks, checked at the primary source. Accessed 2026-10-25.

### Items feeding world claims and population checks (priority 1)

| # | Item | Outcome | Source |
|---|---|---|---|
| 1 | EFUS-T: Feb 2018 living 18.5°C / bedroom 18.1°C; coldest 10% <15.7 / <15.0°C; coldest week coldest 20% <16.1 / <15.6°C; EPC F/G 17.2°C living, 15.7°C bedroom; 12% uncomfortably cold, fuel poor 23% vs 11% | **confirmed** | EFUS 2017 Thermal comfort report |
| 2 | EFUS-HP setpoint, schedules (58/23/19%), hours 7:00 (5-10) / 8:00 (6-12), by presence 6:00 / 7:00 / 8:30, season 5.7 months, all year 6%, controls 87/79/46%, electric showers 37%, immersion main 8% | **confirmed**. Once-daily median period 14.5 h (2011) / 15.0 h (2017) on Fig 3.6, which the pack's 39%/19%/17% split implies but does not state | EFUS 2017 Heating patterns & occupancy |
| 3 | SERL 2023: mean 19.2°C, below 18°C 15.2%; income <£10k 28%; over-65 13%, OR 0.82; over-85 OR 0.67 | **confirmed** (table rows) | Hanmer & Zapata-Webborn (NEA 2024) |
| 4 | Hot water: 39+27N fitted, 36+25N adjusted; delivery 52.2°C | **confirmed** | BRE STP09/DHW01 |
| 5 | DHW24: median 90 L/day, P10-P90 19-222; hot water 19% of heat demand; delivered 48.7°C (42.6-53.7) | **confirmed** | DESNZ Domestic hot-water use (2024) |
| 6 | EST 2008 headline mean ~122 L/day [unverified]; DHW24 cites 104 L | **confirmed**: "The estimated mean consumption is 122 litres/day with a 95% confidence interval of ±18". DHW24's "104 litres ... (2008, based on occupancy of 2.4 persons)" is a different figure (likely the occupancy-standardised mean); the two are not in conflict, but DHW24 does not say how 104 was derived | EST/EA, Measurement of domestic hot water consumption in dwellings (2008) |
| 7 | PHE 2014: 18°C minimal risk; infants 16-20°C; <16°C OR 4.92; COPD 9 h ≥21°C | **confirmed** | PHE Minimum home temperature thresholds (2014) |
| 8 | WHO 2018: 18°C | **still open at primary**: the NCBI Bookshelf page returned a captcha and WHO IRIS returned HTML, not the PDF. Not promoted beyond what PHE (which confirms 18°C) carries | — |
| 9 | HSE: store ≥60°C, 50°C at outlets within 1 min (55°C healthcare), cold <20°C, scald >44°C | **confirmed** | HSE Legionella: hot and cold water systems |
| 10 | NICE NG6 names energy suppliers in its recommendations | **confirmed** (energy suppliers named as an audience and in recommendations; recommendation numbers not re-checked) | NICE NG6 PDF |

### Other [unverified] items

| # | Item | Outcome |
|---|---|---|
| 11 | Lowering a combi's hot-water setpoint is low legionella risk "as a formal HSE position" | **still unpublished as an HSE position**: the HSE page sets storage and outlet temperatures, says nothing about combis. Finding: the advice build must not cite HSE for it |
| 12 | SERL in-home temperature sensor data available through UKDS SN 8666 | **still open**: the UKDS catalogue page did not render. Finding |
| 13 | Design choice: ~10% of homes true 24-hour heating | not a fact; stays a named design assumption, not promoted |

### Counts

confirmed 9 (1, 2, 3, 4, 5, 6, 7, 9, 10) · corrected 0 · still open 3 (8, 11, 12) · design assumption not promoted 1 (13)

---

**Scope:** distributions the half-hourly thermal and gas model can sample from. **Conventions:** every figure has a link to its source next to it. **[derived]** means my own arithmetic on cited figures. **[unverified]** means recalled from memory and not confirmed in this session. Sources I could open and read are cited directly. Where a secondary page reports a primary study, the pack says so.

Key sources used throughout:
- **EFUS-HP**: [BEIS EFUS 2017, Heating patterns & occupancy](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf)
- **EFUS-T**: [BEIS EFUS 2017, Thermal comfort](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018726/efus-thermal.pdf)
- **EFUS11**: [EFUS 2011, Main heating systems](https://assets.publishing.service.gov.uk/media/5a7ca92aed915d6969f46736/4_Main_heating_systems.pdf)
- **H13**: [Huebner et al. 2013, *Heating patterns in English homes*, B&E 70](https://discovery-pp.ucl.ac.uk/1402869/1/1-s2.0-S0360132313002540-main.pdf)
- **H15**: [Huebner et al. 2015, *The shape of warmth*, BRI 43(2)](https://discovery-pp.ucl.ac.uk/id/eprint/1436128/1/Huebner_shape%20of%20warmth%20temperature%20profiles%20in%20living%20rooms.pdf)
- **SERL-CW**: [Hanmer & Zapata-Webborn, *Settling for colder homes*, BEHAVE 2023](https://nea.org.uk/wp-content/uploads/2024/11/Hanmer_Zapata-Webborn_ColderHomes.pdf)
- **SERL-ZW**: [Zapata-Webborn et al. 2024, E&B 305:113869](https://discovery.ucl.ac.uk/10185918/1/1-s2.0-S037877882301099X-main.pdf)
- **SERL-S2**: [SERL Stats Report Vol 2 (2024)](https://discovery.ucl.ac.uk/id/eprint/10189780/7/SERL_Stats_Report_Vol_2_rev.pdf)
- **DHW24**: [DESNZ 2024, *Domestic hot-water use: observations from connected devices*](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf)
- **BRE-DHW**: [Shorrock, BRE STP09/DHW01, analysis of the EST DHW data](https://bregroup.com/documents/d/bre-group/stp09-dhw01_analysis_of_est_dhw_data)
- **PHE14**: [PHE 2014, *Minimum home temperature thresholds for health in winter*](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf)
- **WHO18**: [WHO Housing & Health Guidelines 2018, ch. 4](https://www.ncbi.nlm.nih.gov/books/NBK535294/)
- **HSE**: [HSE, Legionella: hot and cold water systems](https://hse.gov.uk/Legionnaires/hot-and-cold.htm)

---

## 1. Thermostat setpoints and measured indoor temperatures

**Setpoint (self-reported)**
- **EFUS 2017**, 957 centrally heated homes that set one temperature ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) §3.2.3):
  - median 20.0°C, mean 20.4°C, IQR 19–21°C, range 10–35°C;
  - 61% keep one setpoint and 39% vary it.
- **EFUS 2011**, 1,763 homes ([EFUS11](https://assets.publishing.service.gov.uk/media/5a7ca92aed915d6969f46736/4_Main_heating_systems.pdf)): mean 20.1°C, SD 3.3°C, half set between 18 and 21°C.
- **SERL sign-up surveys 2019–21**: mean 20.49, 20.46 and 20.35°C. In the 2023 survey (n=4,202 matched homes) the mean was 19.2°C ([SERL-CW](https://nea.org.uk/wp-content/uploads/2024/11/Hanmer_Zapata-Webborn_ColderHomes.pdf)).

**Setpoint inferred from measurements**
- CaRB, 248 centrally heated homes, Nov 2007–Jan 2008 ([H13](https://discovery-pp.ucl.ac.uk/1402869/1/1-s2.0-S0360132313002540-main.pdf)):
  - demand temperature mean 20.47°C (SD 2.47), range about 13–27°C;
  - mean living-room temperature while heating was on: 19.52°C (SD 2.39), about 1°C below the demand temperature.

**Measured temperatures, winter 2017/18** ([EFUS-T](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018726/efus-thermal.pdf))
- Lowest monthly mean, February 2018: living room 18.5°C, main bedroom 18.1°C.
- Coldest 10% of homes: living room below 15.7°C, bedroom below 15.0°C.
- Coldest week (late Jan 2019): about 1°C below the winter mean. The coldest 20% had living rooms below 16.1°C and bedrooms below 15.6°C.
- The report gives no overall mean, median or share of homes below 18°C or 16°C.

**Conditioning (all EFUS-T)**

| Factor | Living room | Bedroom |
|---|---|---|
| Pensioner present / not | 19.3 / 18.4°C | – |
| HRP 75+ / HRP 16–34 | 19.8 / 18.4°C | – |
| EPC F/G | 17.2°C (A–D: 18.6–19.3°C) | 15.7°C (others: 17.8–18.9°C) |
| Pre-1919 / post-1990 | 17.7 / 19.1°C | – |
| No insulation / ≥2 measures | 17.5 / 18.8–19.0°C | 17.1 / 18.5–18.6°C |
| Flat / house | 19.5 / 18.5°C | n.s. |
| Rural / urban | – | 17.0 / 18.4°C |
| Non-central / central heating | – | 17.2 / 18.3°C |

- Children, household size and fuel poverty: no significant difference in mean temperature ([EFUS-T](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018726/efus-thermal.pdf)).
- Income: the highest quintile was coldest (18.1°C) and the second quintile warmest (19.5°C) ([EFUS-T](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018726/efus-thermal.pdf)).
- Self-reported cold ([EFUS-T](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018726/efus-thermal.pdf)):
  - 12% say the living room is uncomfortably cold often or always, and 9% say the same of the bedroom;
  - those reporting cold measured 1.2°C lower in the living room and 2.4°C lower in the bedroom;
  - fuel poor 23% vs others 11%.

**Long-run context** ([Vadodaria, Loveday & Haines review](https://repository.lboro.ac.uk/articles/Measured_winter_and_spring-time_indoor_temperatures_in_UK_homes_over_the_period_1969-2010_A_review_and_synthesis/9347381/files/16956446.pdf))
- Winter living-room averages barely changed over 40 years: EHCS 18.0°C (1986), 18.6°C (1991), 18.1°C (1996); CALEBRE evenings 18.7°C (2010).
- Bedrooms rose: 14.6°C in 1978 to 18.1°C at night in 2010.

## 2. Heating schedules, hours and season

**Regular vs non-regular** ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) §3.4)
- 73% of centrally heated homes heat regularly; 27% of centrally heated and 40% of non-centrally heated homes do not.
- Among regular central-heating users:

| Heating periods | Weekday | Weekend |
|---|---|---|
| Once a day | 23% | 27% |
| Twice a day | 58% | 49% |
| Three or more | 19% | 18% |

- As a share of all centrally heated homes on weekdays [derived]: once 16.8%, twice 42.3%, 3+ 13.9%, irregular/manual 27%.
- Twice-daily: 89% are a wake-up burst (median 2 h) plus a home-time block (median 5 h).
- The most common single pattern (31% of regular users) is a wake-up burst under 4 h plus a home-time block of 4–10 h.
- Once-daily patterns:
  - 39% start at wake-up and run 11–16 h;
  - 19% start in the evening and run 17 h or more;
  - 17% start at home time and run 4–10 h.

**Control mode** ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf))
- Timer is the main control for 46%; manual thermostat for 34%.
- Boost: 13% of timer users boost daily, 53% at least weekly.

**Daily hours** ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) Table 3.1, §4)
- Weekday median 7:00 (IQR 5:00–10:00); weekend median 8:00 (IQR 6:00–12:00).
- 69% keep the same hours at weekends. The 40% who change them add about 1.5 h.
- By group:
  - pensioner present 9:00 vs 6:15;
  - single person under 60: 5:30;
  - lowest income quintile 6:00;
  - long-term sick or disabled 8:00;
  - detached 8:00 vs flats 6:00.
- By weekday daytime occupancy: occupied all day 8:30, variable 7:00, empty 6:00.
- Who is home all day on weekdays: 43% of households overall, 63% with a pensioner present, 57% of fuel-poor households.

**Measured** ([H13](https://discovery-pp.ucl.ac.uk/1402869/1/1-s2.0-S0360132313002540-main.pdf))
- About 10 h on both weekdays and weekends, against the BREDEM assumption of 9 h and 16 h.
- Peak probability that heating is on at any moment: 0.74.
- 16% of homes had at least 5 unheated days in 92.

**Continuous heating**
- No source measures 24-hour heating directly. Proxies:
  - **"Flat-line" living-room profile**: 30.9% of 275 homes ([H15](https://discovery-pp.ucl.ac.uk/id/eprint/1436128/1/Huebner_shape%20of%20warmth%20temperature%20profiles%20in%20living%20rooms.pdf)). These over-represent flats, social renters and night-storage heating.
  - **Other profiles** in the same study: two-peak 40.0%, steady rise 15.3%, steep rise 13.8% (older households).
- Evening-start runs of 17 h or more: about 4.4% of regular users [derived: 23% × 19%].
- Heating all year round: 6% in 2017 ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf)) and 2% in 2011 ([EFUS11](https://assets.publishing.service.gov.uk/media/5a7ca92aed915d6969f46736/4_Main_heating_systems.pdf)).
- Overnight: SERL gas falls to 0.06 kWh/h at 02:30 (median), implying that at least half of homes do not heat overnight ([SERL-S2](https://discovery.ucl.ac.uk/id/eprint/10189780/7/SERL_Stats_Report_Vol_2_rev.pdf)).

**Season** ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) §3.3)
- Mean length 5.7 months.
- 39% start in October; 68% stop in March or April; October–April is the modal season (23%).
- No link with fuel poverty.
- Summer space heating still appears: median 16% of summer heat demand in combi homes ([DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf)).

## 3. Flow temperature, TRVs and room-by-room heating

**Flow temperature**
- Field telemetry from 4,503 boilers, winters 2021/22–2022/23 ("Rossi" study, reported in [CIBSE Journal Feb 2024](https://www.cibsejournal.com/cibsejournal-magazine/202402/26/page.html)):
  - most boilers were set at 72–75°C;
  - mean peak setpoint fell from 74 to 70°C;
  - share at 60°C rose from 3% to 6%;
  - about 10% of combi users lowered the setting for the whole season.
- The primary paper was not located.
- Nesta trial, 60,468 households ([Nesta](https://www.nesta.org.uk/report/the-impact-of-boiler-optimisation-on-gas-consumption-and-household-comfort)):
  - default settings are often 70–80°C;
  - 64% of survey respondents say they have lowered flow temperature at some point (likely a biased sample);
  - month-specific advice saved 0.209 kWh/day, about 0.4% of gas;
  - modelling cites 8–9% savings from moving 80°C to 60°C;
  - no change in comfort.
- Nesta/Salford Energy House: 16–23% heating-gas savings at about 48°C flow ([ClimateXChange 2023](https://www.climatexchange.org.uk/publications/reductions-in-maximum-flow-temperatures-in-scottish-domestic-heating/)).
- Scottish stock suitable for 55°C flow at winter peak: 15% today, 55% with low-cost retrofit ([ClimateXChange 2023](https://www.climatexchange.org.uk/publications/reductions-in-maximum-flow-temperatures-in-scottish-domestic-heating/)).
- Combi hot-water setpoint: median 55°C, mostly 54–57°C; 71% never change it ([DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf)).

**Controls** ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) §3.2)

| Controls present | Share |
|---|---|
| Room thermostat | 87% |
| TRVs on all or most radiators | 79% |
| Both | 77% |
| Thermostat only | 10% |
| TRVs only | 11% |
| Neither | 2% |

**Partial heating** ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) §3.5–3.6)
- 38% turn heating off in at least one room; 26–27% in a habitable room, 87% of which are bedrooms.
- Unheated habitable rooms by group:
  - HRP 75+ 29% vs 14% for HRP 16–34;
  - one- or two-person homes 27–28%;
  - no children 27% vs 16% with children;
  - under-occupiers 32%.
- Supplementary heaters: 39% use one in at least one room, mainly the living room, median 4 h on weekdays.
- Living Lab: 85% of 100 households with room-by-room control "chose to heat less than half of their home" ([ESC](https://es.catapult.org.uk/report/the-delight-of-better-control/)). The page does not say whether this was at any one time or overall.

## 4. Hot water

**Volume**
- EST field trial of 112 dwellings, fitted line 39 + 27N L/day (R² = 0.138), adjusted to 36 + 25N ([BRE-DHW](https://bregroup.com/documents/d/bre-group/stp09-dhw01_analysis_of_est_dhw_data)).
  - This gives 66 / 93 / 120 / 147 L/day for N = 1–4 [derived].
  - The low R² means wide scatter within each occupancy level.
  - Mean delivery temperature 52.2°C (combi 50.0°C); cold feed 15.3°C.
- EST headline mean of about 122 L/day: [unverified]. DHW24 instead cites the EST study as 104 L/day at about 2.4 occupants ([DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf)).
- Connected-combi data, 45,000 homes 2021–22 ([DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf)):
  - median 90 L/day, P10–P90 19–222 L/day;
  - decile medians 37.9 to 197.8 L/day;
  - winter about 5 L/day above summer;
  - delivered median 48.7°C (P10–P90 42.6–53.7°C);
  - hot water is about 19% of domestic heat demand;
  - the sample is skewed towards high-demand homes.

**End use** ([DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf))

Share of hot-water volume:

| End use | Share of volume |
|---|---|
| Showers and baths | ~45% |
| Small tappings | ~34% |
| Long tappings | ~20% |

Events:

| Event | Share of events | Median duration | Median volume |
|---|---|---|---|
| Small tapping | 85.2% | 20 s | 2 L |
| Long tapping | 9.8% | 108 s | 11 L |
| Shower | 3.7% | 348 s | 37 L |
| Bath | 0.8% | 657 s | 69 L |

**Bathing frequency** ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) §5)
- Homes with both bath and shower: median 0.83 showers and 0.07 baths per person per day.
- Bath-only homes: 0.36 baths per person per day.
- Fewer than one wash per person per day: 46% of homes; exactly one: 30%; more than one: 23%.

**Showers**
- Electric showers ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf)): 37% of showers overall, 47% in fuel-poor homes. Mains or system showers are 63%, including 16% pumped.
- Immersion as main hot-water source: 8% ([EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf)).
- Duration:
  - Unilever logger study, 100 families, 2,600 showers: 8 min and 62 L, about 7.75 L/min [derived] ([UKERC](https://ukerc-observatory.ac.uk/case_study/unilever-showering-practices-survey/));
  - Anglian Water: 8 min ([Anglian](https://anglianwater.co.uk/news/lengthy-showers-are-costing-households-in-the-east-of-england-over-260-million-a-year));
  - EST 2013: 7.3–7.5 min; Atkins/SES 2022: 7.9 min (both as cited in [DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf));
  - combi telemetry median 5.8 min ([DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf));
  - Surrey student trial: 6.7 min, and higher pressure gave shorter showers ([Freethink](https://www.freethink.com/energy/water-pressure), preprint).
- Hot-water flow on combis: 37 L / 348 s ≈ 6.4 L/min [derived].
- Electric shower, 9.5 kW heating water from 15 to 40°C: about 5.5 L/min [derived from physics; the rating is an assumption].

**Timing**
- Peaks at 06:00–08:00 and 17:00–19:00; Sunday is the weekly peak and 24 December the annual peak ([DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf)).

## 5. Comfort response and adaptation

**Comfort benchmarks**
- Adaptive comfort, EN 16798-1 (as implemented in [pythermalcomfort](https://pythermalcomfort.readthedocs.io/en/latest/_modules/pythermalcomfort/models/adaptive_en.html)):
  - T_cmf = 0.33·T_rm + 18.8;
  - Category II band −4/+3 K;
  - valid only for running-mean outdoor temperatures of about 10°C or more and for buildings running without heating, so it does not apply in the heating season.
- Comfortable temperature for sedentary people at 1.0 clo: 21.1 ± 2.9°C (Collins & Hoinville, via [PHE14](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf)).
- The EU "comfort zone" is about 21°C ([NICE NG6](https://www.nice.org.uk/guidance/ng6/resources/excess-winter-deaths-and-illness-and-the-health-risks-associated-with-cold-homes-pdf-51043484869) §1.8).

**Response to price, winter 2022/23**
- Setpoints ([SERL-CW](https://nea.org.uk/wp-content/uploads/2024/11/Hanmer_Zapata-Webborn_ColderHomes.pdf)):
  - mean fell 20.2 to 19.2°C; about a quarter did not change;
  - share below 18°C rose from 6.7% to 15.2%.
- Share of homes with a setpoint below 18°C, 2023 ([SERL-CW](https://nea.org.uk/wp-content/uploads/2024/11/Hanmer_Zapata-Webborn_ColderHomes.pdf)):

| Group | Below 18°C |
|---|---|
| Feel fuel poor | 34% (mean 18.24°C) |
| Income under £10k | 28% |
| Struggling to pay | 24% |
| Single person | 20% |
| Over-65 member | 13% |
| All homes | 15.2% |

- Members over 65 and over 85 were less likely to cut their setpoint (OR 0.82 and 0.67) ([SERL-CW](https://nea.org.uk/wp-content/uploads/2024/11/Hanmer_Zapata-Webborn_ColderHomes.pdf)).
- Gas use ([SERL-ZW](https://discovery.ucl.ac.uk/10185918/1/1-s2.0-S037877882301099X-main.pdf), n=5,594):
  - median 10.8% cut (IQR 1.2–22.4%);
  - each 1°C setpoint reduction is associated with about 3.8% less gas;
  - over half heated for fewer hours;
  - the biggest reducers were 2.25 times more likely to report being unable to keep warm (21.7% vs 9.6%);
  - price elasticity of gas demand −0.071.
- About 12% could not keep the living room comfortably warm, and wellbeing was lower in that group ([Huebner et al., eceee 2024](https://www.eceee.org/library/conference_proceedings/eceee_Summer_Studies/2024/1-dynamics-of-consumption/cost-of-living-crisis-underheating-and-wellbeing-insights-from-a-large-survey-study-in-great-britain/)).
- Living Lab, autumn 2022 vs 2021, weather-corrected ([ESC](https://es.catapult.org.uk/report/measuring-the-consumer-response-to-the-energy-crisis-in-the-living-lab/)):
  - room temperatures 0.6°C lower (85 homes);
  - heating gas about 40% lower (36 homes).

**Take-back after efficiency measures**
- Warm Front upgrades: living rooms +1.6°C, bedrooms +2.8°C ([Vadodaria review](https://repository.lboro.ac.uk/articles/Measured_winter_and_spring-time_indoor_temperatures_in_UK_homes_over_the_period_1969-2010_A_review_and_synthesis/9347381/files/16956446.pdf)).
- 13 social homes after external wall insulation ([Love 2014](https://discovery.ucl.ac.uk/id/eprint/1433401/)):
  - nobody raised their thermostat, and most cut heating hours;
  - the temperature rise came mainly from slower cooling and from systems that had previously been unable to deliver enough heat.

**Coping behaviour**
- Boost button use is covered in §2. No numbers were found for extra clothing, heating one room, or going to bed early (see gaps).

## 6. Health guidance

**Cold**
- **WHO (strong recommendation)**: 18°C "has been proposed as a safe and well-balanced indoor temperature" ([WHO18](https://www.ncbi.nlm.nih.gov/books/NBK535294/)).
  - Vulnerable groups may need more: older people, children, and people with cardiorespiratory disease.
  - Certainty of evidence: moderate.
- **PHE 2014** ([PHE14](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf)):
  - at least 18°C poses minimal risk to sedentary, suitably clothed people;
  - the threshold is particularly important for people over 65 or with existing conditions, for whom slightly above 18°C may help and 18°C overnight may be beneficial;
  - healthy, active people aged 1–64 may go slightly below;
  - infants' rooms 16–20°C;
  - risks: below 18°C, raised blood pressure; below 16°C, higher risk again (OR 4.92 for high blood pressure);
  - COPD benefit with at least 9 h at 21°C or more in the living room;
  - the evidence is weak, so this should not be framed as a strong recommendation.
- **Earlier Cold Weather Plan**: 21°C living room and 18°C bedroom ([PHE14](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf)).
- **UKHSA AWHP evidence** ([AWHP](https://assets.publishing.service.gov.uk/media/65fdb71af1d3a0001d32ae74/Adverse_Weather_and_Health_Plan_supporting_evidence__1_.pdf)):
  - health effects begin below 18 ± 0.5°C indoors and at outdoor means of 4–8°C;
  - 13,400 excess winter deaths in 2021/22;
  - 5,533 deaths attributed to extreme cold in winter 2022/23.
- **NICE NG6** (2015, minor changes 2019) ([NG6](https://www.nice.org.uk/guidance/ng6/resources/excess-winter-deaths-and-illness-and-the-health-risks-associated-with-cold-homes-pdf-51043484869)):
  - sets no temperature threshold;
  - at-risk groups: over-65s, young children, pregnant women, people with cardiovascular, respiratory or mental-health conditions, disabled people, and people on low incomes;
  - Recommendations 3, 6 and 10 name energy suppliers.

**Hot water** ([HSE](https://hse.gov.uk/Legionnaires/hot-and-cold.htm))
- Store at 60°C or above; reach 50°C at outlets within one minute (55°C in healthcare); cold water below 20°C.
- Scald risk above 44°C; Type 3 thermostatic mixing valves limit to 44°C where the risk is significant.
- Building Regs Part G3 (new dwellings) ([GreenSpec](https://greenspec.co.uk/building-design/water-part-g/)):
  - bath outlets capped at 48°C;
  - a mixing valve limits to 60°C where stored water could exceed 80°C;
  - solar-heated stored water raised to 65°C for 1 h a week.
- WaterSafe notes that 55°C distribution may not be achievable with combis ([WaterSafe](https://watersafe.org.uk/advice/common_plumbing_questions1/temperature/what_temperature_should_hot_water_be_stored_at)).

**Ofgem**
- No obligation on suppliers to advise on temperature.
- SLC 27A (from 15 Dec 2020) ([Ofgem decision](https://www.ofgem.gov.uk/system/files/docs/2020/10/self-disconnection_and_self-rationing_decision.pdf)):
  - suppliers must identify prepayment customers who self-disconnect;
  - additional support credit for vulnerable customers who are self-rationing;
  - Ability to Pay principles apply;
  - energy-efficiency information under SLC 27.6(b) and 31G.

---

## (a) Distributions for the simulation to draw from

| Attribute | Distribution | Conditioning | Source |
|---|---|---|---|
| Setpoint (pre-2022) | Normal, μ 20.4, σ ≈ 1.5 [derived from IQR 19–21], clip 14–26°C | +0 for pensioners (more hours, not a higher setpoint) | [EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf), [H13](https://discovery-pp.ucl.ac.uk/1402869/1/1-s2.0-S0360132313002540-main.pdf) |
| Setpoint (2023+) | μ 19.2°C; P(<18°C) 15.2% | Feel fuel poor 34%, income under £10k 28%, over-65 13% | [SERL-CW](https://nea.org.uk/wp-content/uploads/2024/11/Hanmer_Zapata-Webborn_ColderHomes.pdf) |
| Achieved living temperature vs setpoint | about −1°C while heating is on | Lower in EPC F/G and pre-1919 homes | [H13](https://discovery-pp.ucl.ac.uk/1402869/1/1-s2.0-S0360132313002540-main.pdf), [EFUS-T](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018726/efus-thermal.pdf) |
| Schedule type (central heating, weekday) | Once 16.8% / twice 42.3% / 3+ 13.9% / irregular 27% [derived] | Weekend: once 27%, twice 49% of regular users | [EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) |
| Near-continuous ("flat") profile | ~30% (measured profile) vs ~4% (reported 17 h+) | Flats, social rent, storage heating | [H15](https://discovery-pp.ucl.ac.uk/id/eprint/1436128/1/Huebner_shape%20of%20warmth%20temperature%20profiles%20in%20living%20rooms.pdf), [EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) |
| Daily hours | Weekday median 7 h (IQR 5–10); weekend 8 h (IQR 6–12) | Pensioner 9 h; single under 60: 5.5 h; occupied all day 8.5 h | [EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) |
| Season | Mean 5.7 months; start Oct 39%; end Mar/Apr 68%; all year 6% | None by fuel poverty | [EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) |
| Flow temperature | Mode 72–75°C; ~6% at 60°C or below (2023) | Rises after advice campaigns | [CIBSE J](https://www.cibsejournal.com/cibsejournal-magazine/202402/26/page.html) |
| Combi hot-water setpoint | Median 55°C (54–57) | 71% fixed all year | [DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf) |
| Controls | Thermostat + TRVs 77%, thermostat only 10%, TRVs only 11%, neither 2% | – | [EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) |
| Unheated habitable room | 24–27% (mostly a bedroom) | HRP 75+ 29%; 1–2 person homes 27–28%; with children 16% | [EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) |
| Hot-water volume | Mean 39 + 27N L/day; lognormal spread, P10–P90 19–222 L/day | By occupants N | [BRE-DHW](https://bregroup.com/documents/d/bre-group/stp09-dhw01_analysis_of_est_dhw_data), [DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf) |
| Showers per person per day | Median 0.83; baths 0.07 | Bath-only homes 0.36 baths | [EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) |
| Shower duration and flow | Median 5.8–8 min; 6.4–7.75 L/min [derived] | Electric showers ≈5.5 L/min [derived] | [DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf), [UKERC](https://ukerc-observatory.ac.uk/case_study/unilever-showering-practices-survey/) |
| Electric shower present | 37% | Fuel poor 47% | [EFUS-HP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf) |
| Hot-water timing | Peaks 06–08 h and 17–19 h; Sunday peak | – | [DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf) |
| Price response | −1.1°C setpoint; −3.8% gas per °C; median −10.8% gas | Over-65s cut less (OR 0.82) | [SERL-ZW](https://discovery.ucl.ac.uk/10185918/1/1-s2.0-S037877882301099X-main.pdf) |

## (b) Population checks

The simulated population should reproduce these figures:
- Gas (SERL, 2023, not weather-normalised) ([SERL-S2](https://discovery.ucl.ac.uk/id/eprint/10189780/7/SERL_Stats_Report_Vol_2_rev.pdf)):
  - median 26.0 kWh/day (IQR 17.3–37.0); annual median 9,490 kWh;
  - EPC A/B 18.2 vs E 29.9 kWh/day;
  - one occupant 18.5 vs six or more 39.8 kWh/day;
  - half-hourly peak at 18:30, minimum at 02:30.
- Winter 2022/23 predicted counterfactual median of about 47.9 kWh/day ([SERL-ZW](https://discovery.ucl.ac.uk/10185918/1/1-s2.0-S037877882301099X-main.pdf)).
- February living room about 18.5°C and bedroom about 18.1°C; coldest decile below 15.7 and 15.0°C ([EFUS-T](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018726/efus-thermal.pdf)).
- EPC F/G living room about 1.5–2°C colder than A–D ([EFUS-T](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018726/efus-thermal.pdf)).
- 12% report an uncomfortably cold living room ([EFUS-T](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018726/efus-thermal.pdf)).
- Hot water is about 19% of heat demand, with a median of 90 L/day in combi homes ([DHW24](https://assets.publishing.service.gov.uk/media/65f43b919d99de001d03df8a/domestic-hot-water-use-insights.pdf)).
- Peak probability that heating is on is 0.74 or below at any half-hour ([H13](https://discovery-pp.ucl.ac.uk/1402869/1/1-s2.0-S0360132313002540-main.pdf)).
- At least about 50% of homes use no heating gas overnight ([SERL-S2](https://discovery.ucl.ac.uk/id/eprint/10189780/7/SERL_Stats_Report_Vol_2_rev.pdf)).

## (c) Health floor rules for advice

1. Never advise a living-room setpoint below 18°C ([WHO18](https://www.ncbi.nlm.nih.gov/books/NBK535294/), [PHE14](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf)).
2. For over-65s, chronic illness, or homes on a priority services register:
   - keep 18°C overnight and a living-room target a little above 18°C ([PHE14](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf));
   - for COPD, allow 21°C or more for at least 9 h ([PHE14](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf)).
3. Infants' sleeping rooms: 16–20°C ([PHE14](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf)).
4. Flag any simulated room-hour below 16°C as elevated risk, and below 18°C as a health-relevant shortfall ([PHE14](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf), [AWHP](https://assets.publishing.service.gov.uk/media/65fdb71af1d3a0001d32ae74/Adverse_Weather_and_Health_Plan_supporting_evidence__1_.pdf)).
5. Do not advise a setpoint cut to households already below 18°C or self-rationing. Route them to support instead ([SLC 27A](https://www.ofgem.gov.uk/system/files/docs/2020/10/self-disconnection_and_self-rationing_decision.pdf), [NG6](https://www.nice.org.uk/guidance/ng6/resources/excess-winter-deaths-and-illness-and-the-health-risks-associated-with-cold-homes-pdf-51043484869)).
6. Stored hot water: never advise a cylinder setting below 60°C; outlets must reach 50°C within 1 minute ([HSE](https://hse.gov.uk/Legionnaires/hot-and-cold.htm)).
7. Flow-temperature advice applies to combi space heating only. Lowering the combi hot-water setpoint is low legionella risk because nothing is stored [unverified as a formal HSE position]. Leave the hot-water setting alone where a cylinder is present.
8. Delivered temperature above 44°C is a scald risk for vulnerable occupants; bath delivery in new dwellings is capped at 48°C ([HSE](https://hse.gov.uk/Legionnaires/hot-and-cold.htm), [Part G](https://greenspec.co.uk/building-design/water-part-g/)).
9. Advice that lowers flow temperature must still achieve the setpoints above at design-cold conditions. Only about 15% of homes manage 55°C flow at peak without retrofit ([ClimateXChange](https://www.climatexchange.org.uk/publications/reductions-in-maximum-flow-temperatures-in-scottish-domestic-heating/)).

## (d) Named gaps and suggested design choices

1. **No cited distribution of measured winter temperatures.** EFUS-T gives deciles and means by group, but no overall histogram or share below 18°C. *Choice:* calibrate the thermal model so the simulated deciles match EFUS-T (coldest decile below 15.7°C living, below 15.0°C bedroom). Pull the SERL in-home temperature sensor data through UKDS SN 8666, which I did not confirm exists for this purpose [unverified].
2. **24-hour heating share is uncertain** (reported about 4%, measured "flat" profile about 31%). *Choice:* treat "flat" as a temperature-profile outcome of low setback combined with long hours, rather than a separate schedule type. Draw around 10% of homes as true 24-hour heating [design assumption], biased towards flats and social rent.
3. **No national primary source for the flow-temperature distribution.** The CIBSE secondary report is the only field telemetry found. *Choice:* triangular distribution, mode 74°C, range 55–80°C, with 6% at 60°C or below.
4. **Hot-water volume by occupancy has only a mean line.** The R² of 0.14 means huge scatter. *Choice:* lognormal around 39 + 27N, with a dispersion that reproduces the DHW24 P10–P90 spread.
5. **No GB numbers on coping behaviours** (extra clothing, heating one room, early bed, pre-heating). *Choice:* model them as a comfort-deficit response, without fixed rates, and expose the parameters for sensitivity analysis.
6. **No GB measurement of TRV use** (what valves are set to, not just that they are fitted). *Choice:* default unheated rooms to the EFUS rates, and treat TRVs as fixed per-room caps.
7. **Electric-shower and immersion use are not in DHW24** (combi-only sample). *Choice:* attach electric showers to 37% of homes (47% of fuel-poor) on the electricity meter, and derive their flow from kW rating and inlet temperature.
8. **Ofgem says nothing on temperature advice.** *Choice:* adopt rules (c)1–5 as Poesys policy and state that they rest on WHO, PHE and NICE guidance, not on an Ofgem requirement.
9. **Primary-paper gaps:**
   - the EST 2008 report's own headline figure: the PDF was blocked, and DHW24 is internally inconsistent on 104 L;
   - the "Rossi" flow-temperature paper behind the CIBSE Journal report;
   - the full Living Lab zoning data.
