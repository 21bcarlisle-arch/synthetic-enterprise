# Director evidence: vehicle mix and real world efficiency

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

# Evidence pack: what cars GB households own and buy, and how much energy each uses

**For:** Poesys household EV/ICE personalisation. **Compiled:** 25 Oct 2026. **Tags:** [derived] means my own arithmetic on the cited figures. [unverified] means I recalled it and did not confirm it from a fetched source in this session. **Scope caveat:** most sources are UK-wide, not GB. Northern Ireland is about 3% of the UK car fleet [unverified], so the UK figures are close to GB but not equal to it.

**Access note:** the DfT ODS data tables (VEH1103, VEH0141, VEH0142, VEH1111) could not be downloaded. The session proxy blocked assets.publishing.service.gov.uk and www.gov.uk returned a 403. The table index is at https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-tables, and the make/model files are at https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-files. As a result, the fuel-by-year series for 2016–2025 and the BEV make/model parc counts below come from secondary sources and are incomplete (see Named gaps).

---

## 1. Car parc mix

### 1.1 Totals and fuel shares

| Metric | Value | Source |
|---|---|---|
| Licensed cars, UK, Sep 2025 | 34,486k. Zero-emission cars 1,630k (4.7%), up 37% year on year | https://www.gov.uk/government/statistics/vehicle-licensing-statistics-july-to-september-2025/vehicle-licensing-statistics-united-kingdom-july-to-september-2025--2 |
| Licensed cars, UK, Dec 2024 | 33,967k. Zero-emission cars 1,287k (3.8%) | https://www.gov.uk/government/statistics/vehicle-licensing-statistics-2024/vehicle-licensing-statistics-united-kingdom-2024 |
| SMMT "cars in use", end 2024 | 36,165,401. Petrol 58.2% (about 21m), diesel 32.1% (about 11.6m), BEV 3.7% (1.33m). Plug-ins (BEV+PHEV) 2,157,360, which implies PHEV ≈ 0.83m [derived] | https://cardealermagazine.co.uk/british-motor-parc-grew-to-record-levels-in-2024-as-fiesta-remained-most-common-car-smmt/314319 |
| SMMT cars in use, end 2025 | 36,676,185. BEV 1,797,809 (+34.7%), which is 4.90% of cars [derived] | https://www.am-online.com/news/uk-vehicle-parc-hits-record-425m-as-evs-rise-but-fleet-ages |
| Electrified share, 2025 (BEV+PHEV+HEV+FCEV, all vehicles) | 4.6m (10.9%) | SMMT Motorparc 2025 (https://www.smmt.co.uk/?p=70022) |
| Company-registered share | 10.4% of all cars, but 55.4% of zero-emission cars | https://www.fleetnews.co.uk/news/more-vehicles-on-uk-roads-than-ever-before-with-rise-in-evs |

The two counts differ. DfT counts licensed cars (about 34.0–34.5m), while SMMT counts all cars "in use" (about 36.2–36.7m), apparently including SORN or unlicensed vehicles. Use DfT for "cars households drive". The SMMT HEV and PHEV parc counts for 2025 were not stated in the sources fetched.

### 1.2 Segment mix of the parc, 2025 (SMMT)

| Segment | Cars | Share [derived, of 36.36m segment sum] |
|---|---|---|
| Supermini | 11,946,020 | 32.9% |
| Lower medium | 9,528,133 | 26.2% |
| Dual purpose (SUV) | 6,748,745 | 18.6% |
| Upper medium | 3,149,167 | 8.7% |
| MPV | 1,548,337 | 4.3% |
| Executive | 1,377,380 | 3.8% |
| Specialist sports | 1,028,828 | 2.8% |
| Mini | 851,020 | 2.3% |
| Luxury saloon | 179,073 | 0.5% |

Source: https://www.smmt.co.uk/?p=70022. Fleet News confirms that the top three segments make up 77% of the parc. Most common models in the parc: Fiesta 1,368,335, Corsa 992,919, Golf 981,882, Focus 948,212, Qashqai 725,575 (same source).

New-market trend: SUVs were 52.2% of models on sale in 2025, against 26.2% in 2016–22 and 17.7% in 2011–15. MPV model count is down more than 70% from its peak. These are shares of models offered, not registrations. Source: https://www.am-online.com/news/suvs-continue-to-dominate-uk-market-as-body-style-hits-25-year-high

### 1.3 New registrations, 2025 (SMMT)

| Metric | Value | Source |
|---|---|---|
| Total | 2,020,520 | https://www.smmt.co.uk/uk-new-car-market-breaches-two-million-as-almost-one-in-four-buyers-go-electric/ |
| BEV / HEV / PHEV / ICE incl. MHEV | 23.4% (473,348) / 13.9% / 11.1% / 51.5% | same |
| Petrol excluding full hybrids | 46.4% | https://www.yahoo.com/news/articles/car-sales-hit-two-million-000100127.html |
| Private / fleet / business | 779,587 (38.6%) / 1,194,545 / 46,388 | SMMT, as above |
| 2024 new ZEV share | 19% (382k). Company keepers take 82% of new ZEVs, 77% of PHEVs and 58% of petrol | DfT 2024 release (above) |
| Top 10 overall, 2025 | Puma 55,488; Sportage 47,788; Qashqai 41,141; Corsa 35,947; Juke 34,773; Golf 32,478; XC40 30,404; MG HS 30,191; Tiguan 29,857; Tucson 28,613 | https://www.whatcar.com/news/most-popular-cars/n14754 |

### 1.4 Top BEV models

**New registrations, 2025 (SMMT, via Gateway2Lease):** Model Y 24,298; Model 3 21,188; Audi Q4 e-tron 14,433; Audi Q6 e-tron 13,148; Ford Explorer 12,237; BMW i4 12,158; Škoda Enyaq 11,940; Kia EV3 11,188; Škoda Elroq 10,713; Volvo EX30 10,289. Source: https://www.gateway2lease.com/blog/company-fleets/uks-top-10-evs-in-2025. The top 10 total 141,592, which is 29.9% of BEV registrations [derived].

**Privately purchased EVs on the road (Cap hpi, about 2024):** Leaf 39,421; Model 3 39,263; Zoe 20,784; Model Y 18,720; Niro 17,461; ID.3 15,789; MG ZS 13,916; MINI 13,529; I-Pace 13,123; i3 12,859. Source: https://ohme-ev.com/news-and-press/uk-most-popular-evs/. This is the best available proxy for the household BEV parc. A full parc-by-model count needs the DfT VEH0141 or make/model files.

### 1.5 Usable battery capacity

EV Database average across listed models: **73.4 kWh** usable (minimum 21.3, maximum 141). Source: https://ev-database.org/uk/cheatsheet/useable-battery-capacity-electric-car. This average is not sales-weighted.

Model ranges from the same page (kWh usable):

| Model | Usable kWh |
|---|---|
| Model Y | 60–79 |
| Model 3 | 60–79 |
| Q4 | 59–79 |
| Explorer | 58–79 |
| i4 | 67.1–81.3 |
| Enyaq | 58–77 |
| Elroq | 58–77 |
| EV3 | 55–78 |
| EX30 | 49–65 |
| MG4 | 41.9–74.4 |
| ID.3 | 50–79 |
| Renault 5 | 40–52 |
| BYD Dolphin | 30–60.5 |
| Kona | 65.4 |
| Leaf (new) | 52.9–75.1 |

**Sales-weighted estimate for 2025 new BEVs**, using the top 10 excluding the Q6 (whose capacity was not fetched) and assuming a variant-midpoint mix: **68.2 kWh**, bounded 58.7–77.7 kWh [derived].

The older private parc (Leaf, Zoe, i3) carries smaller batteries, roughly 22–62 kWh [unverified]. A parc-weighted mean is therefore likely below 60 kWh [derived inference, unverified].

---

## 2. Real-world BEV efficiency and temperature

### 2.1 Baseline efficiency by model

EV Database "real" combined consumption, averaged across all models: **303 Wh/mi (about 3.3 mi/kWh)**. Range runs from 218 Wh/mi (Model 3 RWD) to 473 Wh/mi (G 580). Source: https://ev-database.org/uk/cheatsheet/energy-consumption-electric-car

| Model | Wh/mi |
|---|---|
| Model 3 | 218–243 |
| Model Y | 255–277 |
| ID.3 | 256–263 |
| Leaf | 265–268 |
| MG4 | 270–309 |
| Enyaq | 266–280 |
| ID.4 | 276–296 |
| Q4 | 268–293 |

Same source. The page does not state whether charging losses are included. I infer these figures are battery-side [unverified].

### 2.2 Temperature dependence

| Source | Finding |
|---|---|
| EV Database methodology (Model Y Performance page) | "Mild" = 23°C, no A/C. "Cold" = −10°C with heating. Highway = 110 km/h. Combined consumption is 156 Wh/km mild and 214 Wh/km cold, so **+37% consumption at −10°C** [derived]. Range is 480 km mild and 350 km cold (−27%). https://www.ev-database.org/car/1183/Tesla-Model-Y-Performance |
| Recurrent, Nov 2025 (more than 30,000 US vehicles, 34 models) | **78% of ideal range at 0°C** (best model 88%, worst 69%). **70% at −7°C.** A heat pump adds about 10% range at 0°C, and the benefit shrinks towards −18°C. https://www.recurrentauto.com/research/winter-ev-range-loss%20 |
| Recurrent, Jan 2025 (more than 18,000 vehicles) | With a heat pump, the average EV kept 83% of range. Without one, 75%. Model-level retention: Model 3 87%, Model Y 86%, Ioniq 5 85%, Kona 84%, Leaf 78%, ID.4 64%, Mach-E 66%. https://www.carscoops.com/2025/01/evs-lose-20-range-on-average-in-freezing-conditions-study-finds/ |
| Geotab (4,200 EVs, 5.2m trips, 102 make/model/years) | Peak at **21.5°C = 115% of rated range**. **−15°C = 54%.** The 90th percentile vehicle gets 32% more range than average. https://www.geotab.com/uk/blog/ev-range/ |
| What Car? 2024 winter test (UK, 6–11°C) | Real range was 21–38% below WLTP. Mean shortfall 29.9% [derived]. Efficiency 2.5–3.9 mi/kWh (Model 3 LR 3.9, MG4 3.1, ID.7 3.5). The ID.7 with a heat pump went 268 mi against 254 mi without, i.e. **+5.5% at about 10°C** [derived]. https://whatcar.com/news/electric-car-best-winter-range/n24274 |

**Design reading [derived]:** treat the efficiency multiplier as a U-curve with its minimum near 20–23°C. Cold-side anchors relative to mild: about 1.15–1.2× consumption at 10°C (What Car?, after allowing for the WLTP optimism), about 1.28× at 0°C (1/0.78), about 1.43× at −7°C (1/0.70) and about 1.37× at −10°C (EV Database). Apply a heat-pump flag of about −8 to −10 points of penalty at 0°C. Note that the Recurrent and Geotab figures are range against a rated or ideal baseline, which is not identical to kWh/mi.

### 2.3 Charging losses (AC, wall to battery)

ADAC tests (reported Aug 2026), loss as a share of wall energy:

| Car | 11 kW wallbox | 2.3 kW socket |
|---|---|---|
| Mercedes CLA | 6.9% | 24.2% |
| Tesla Model Y | 6.1% | 12.7% |
| Renault 5 | 5.1% | 13.7% |
| Volvo EX30 | 7.0% | 14.2% |
| VW ID.7 | 6.9% | 15.3% |

Source: https://thenextweb.com/news/adac-ev-home-charging-losses-wallbox-socket. On a wallbox, the wall-to-battery efficiency is **about 93–95%** [derived]. On a granny lead it falls to **about 76–87%**.

---

## 3. PHEV

| Metric | Value | Source |
|---|---|---|
| Real electric driving share, ICCT/Fraunhofer 2022 (about 9,000 vehicles, Europe incl. UK) | **Private 45–49%, company 11–15%**, against a WLTP assumption of 70–85% | https://theicct.org/wp-content/uploads/2022/06/fs-real-world-phev-use-jun22.pdf ; https://www.isi.fraunhofer.de/content/dam/isi/dokumente/cce/2022/PHEV_ISI-ICCT_Fact_Sheet_ENG-Update-2022.pdf |
| Real fuel use, same study | Private 4.0–4.4 L/100 km and company 7.6–8.4 L/100 km, against 1.6–1.7 WLTP | same |
| OBFCM, Fraunhofer/Öko-Institut 2025 (981,139 PHEVs registered 2021–23) | km share in charge-depleting mode **42.4% mean**. Engine-off electric share 30.9%. Energy-based electric share **31.0%**. Real 5.89 L/100 km against 1.53 WLTP (3.85×) [derived]. CD mode about 2.8 L/100 km, CS mode about 7.4 L/100 km. No private/company split | https://www.oeko.de/fileadmin/oekodoc/Analyse_PHEV_2025_EN_final.pdf |
| Electric share against range | UF rises only slightly up to about 80 km of range, then flattens. Fitted utility-factor scaling distance d_n is about 4,730–5,890 km, against the EU's 800 km (to 2024), 2,200 km (2025–26) and 4,260 km (from 2027) | same |
| EC OBFCM 2022 data | Real CO2 was 3.5× type approval for 2021 PHEVs (+99 g/km) and +314% for 2022 PHEVs | https://climate.ec.europa.eu/news-other-reads/news/publication-real-world-co2-emissions-and-fuel-consumption-cars-and-vans-collected-2022-2024-07-26_en |
| Battery size trend | Superb iV 25.7 kWh and 135 km (up from 56 km). VW eHybrid 19.7 kWh, more than 100 km. MG HS PHEV 121 km. Rafale 100 km | https://motorillustrated.com/surge-in-plug-in-hybrid-electric-vehicle-phev-ranges-ahead-of-new-eu-rules/136610/ |

Older parc PHEVs (2016–2021) typically carry about 9–14 kWh gross for about 30–60 km WLTP [unverified]. **Implication:** the electric share is driven mainly by charging behaviour and keeper type, not battery size.

---

## 4. ICE counterfactual

| Metric | Value | Source |
|---|---|---|
| WLTP-era gap (OBFCM, 2022 registrations) | Petrol +21.1% (+1.3 L/100 km). Diesel +17.1% (+1.0 L/100 km). 2021 registrations: petrol +19.8%, diesel +18.2% | EC OBFCM release (above) |
| NEDC-era gap (ICCT Lab-to-Road) | 8% in 2001, 28% in 2012, **39% in 2015 and 2017**. More than 1.3m vehicles from 8 countries; UK sources include Allstar and Emissions Analytics | https://theicct.org/news/real-world-vehicle-fuel-consumption-gap-europe-stabilizing |
| Emissions Analytics EQUA, 2016 | Real 42.3 mpg against 60.7 official (gap 29%), i.e. about 6.7 L/100 km [derived, UK gallons] | https://www.emissionsanalytics.com/news/the-equa-mpg-gap-increases-further-in-2016 |
| HEVs (Honest John Real MPG) | Average 70% of the advertised mpg | https://am-online.com/news/market-insight/2018/06/05/real-mpg-data-reveals-98-of-hybrids-cannot-deliver-advertised-fuel-economy-says-honest-john |

**Gap by age [derived from the above]:** cars of the 2001 model year run about 8% over NEDC. Cars from 2012–2017 run about 28–39% over NEDC. Post-2018 WLTP cars run about 17–21% over WLTP. Real consumption therefore does not fall as fast as the official figures suggest for 2010–2017 cars. That is the cohort that dominates the 45.7% of the parc aged over 10 years.

---

## 5. Turnover

| Metric | Value | Source |
|---|---|---|
| Average car age | 9.7 years in 2025 (9.5 in 2024). 45.7% over 10 years old | https://www.am-online.com/news/uk-vehicle-parc-hits-record-425m-as-evs-rise-but-fleet-ages |
| DfT average age, licensed cars | 10 years at Dec 2024 (8 years in 2019) | DfT 2024 release (above) |
| Ownership duration | 62 months on average. Tesla 29.1, Kia 51.1, Toyota and Honda 80.3 (carVertical 2024 checks) | https://www.lovemoney.com/news/amp/442156/car-brands-longest-shortest-ownership-times-uk-tesla-kia-rover-vauxhall |
| Used transactions, 2025 | 7,807,872. BEV 274,815 (3.5%, +45.7%). PHEV 88,032. HEV 407,531. Petrol 56.7%, diesel 33.1% | https://www.smmt.co.uk/evs-power-up-used-car-market-in-three-year-growth-run/ |
| New vs used | New cars are 20.6% of all transactions. Private new buys (779,587) are about 10% of used volume [derived] | SMMT (above) |
| Top used BEVs, 2025 | Model 3 about 10% of used BEVs, then Leaf (about half the Model 3's volume), ID.3, Niro, Model Y | https://www.electrifying.com/blog/article/used-ev-market-up-a-massive-46-in-2025 |
| Used prices (Auto Trader, May 2025) | Used EV average £24,370 (−7.4% year on year). 3–5-year-old EV £18,266 against petrol £18,731. All-car index £16,825 | https://www.fleetnews.co.uk/news/used-electric-vehicle-prices-drop-below-petrol-and-diesel |
| What an EV replaces | No published GB shares by prior fuel were found. Zapmap: about one-third of EV owners also keep an ICE car. Dual-fuel households use the EV for 85% of local trips and 67% of trips over 100 mi (n=4,300, 2022) | https://www.zapmap.com/news/dual-fuel-drivers-choose-electric |

---

## 6. AC onboard charger limits

- **Model Y Performance:** 11 kW AC, confirmed. Source: https://www.ev-database.org/car/1183/Tesla-Model-Y-Performance
- **Many EVs top out at about 11 kW AC**; myenergi names no 22 kW models. Source: https://support.myenergi.com/hc/en-gb/articles/28401995738001-Understanding-Why-Many-EVs-Max-Out-at-11kW-Charging-Despite-the-zappi-s-22kW-Capability
- **Other 2025 top-10 models:** all 11 kW [unverified].
- **Older private parc:** Leaf 6.6 kW (3.6 kW on early cars), Zoe 22 kW, i3 7.4–11 kW, MG4/MG ZS about 6.6–7 kW [unverified].

**Key point [unverified, but standard]:** most GB homes have a single-phase supply, so home charging is capped at about 7.4 kW (32 A) whatever the onboard charger rating. 11 and 22 kW only matter for three-phase supplies or public AC chargers.

---

## (a) Distributions for the simulation to draw from

| Attribute | Distribution | Conditioning | Source |
|---|---|---|---|
| Fuel of household car | Categorical. 2024 parc: petrol 58.2%, diesel 32.1%, BEV 3.7%, PHEV about 2.3% [derived], HEV the remainder (about 3–4% [derived]). Roll BEV forward to 4.7–4.9% in 2025 | Year. Private keepers only (company cars hold 55.4% of ZEVs, so the private BEV share is lower) | SMMT 2024/2025, DfT Q3 2025 |
| Segment | Categorical from the 2025 parc table (supermini 32.9% … luxury 0.5%) | Fuel: BEV and new cars skew to SUVs (52% of models on sale) | SMMT Motorparc 2025 |
| BEV model | Weighted by the Cap hpi private-parc list (older stock) and by SMMT 2025 registrations (new) | Vehicle age, household income | Cap hpi via Ohme; SMMT via Gateway2Lease |
| Usable battery | Look up by model and variant. Fallback: normal with mean 68 kWh, bounds 59–78 (new); lower for older stock | Model, registration year | EV Database |
| BEV mild efficiency | Model lookup (218–309 Wh/mi for mainstream models). Fallback 303 Wh/mi | Model | EV Database |
| Temperature multiplier | Piecewise: 1.0 at about 21°C; about 1.15–1.2 at 10°C; 1.28 at 0°C; 1.43 at −7°C. Heat pump reduces the penalty by about 8–10 points at 0°C | Daily mean temperature, heat-pump flag | Recurrent, Geotab, EV Database, What Car? |
| AC charging efficiency | 0.93–0.95 on a wallbox; 0.76–0.87 on a 3-pin socket | Charger type | ADAC |
| Onboard AC limit | Point mass at 11 kW for 2021+ models; 6.6/7.4 kW for older Leaf/MG/i3; 22 kW for Zoe | Model | EV Database (partly [unverified]) |
| Effective home charge power | min(onboard, 7.4 kW single-phase) | Supply phase | [unverified] |
| PHEV electric km share | Beta with mean about 0.47 for private keepers and 0.13 for company. OBFCM pooled mean is 0.31 by energy | Keeper type, charging access | ICCT 2022, OBFCM 2025 |
| PHEV fuel use | CD mode 2.8 L/100 km, CS mode 7.4 L/100 km | Mode | OBFCM 2025 |
| ICE real/official ratio | NEDC cars: 1.08 (2001) rising to 1.39 (2015+). WLTP cars: 1.17 diesel, 1.21 petrol | Registration year, fuel | ICCT, EC OBFCM |
| HEV real/official | about 1/0.70 = 1.43 on the mpg basis [derived] | — | Honest John |
| Vehicle age | Mean 9.7 years; 45.7% older than 10 | Fuel (BEVs much younger) | SMMT |
| Holding period | Mean about 62 months; Tesla about 29 | Brand | carVertical |
| Acquisition channel | Used about 79%, new about 21% of transactions; private new about 10% of private-relevant volume | — | SMMT [derived] |

## (b) Population checks

1. The simulated private BEV share at end-2025 should land below the 4.9% all-keeper share, because company keepers hold more than half of ZEVs.
2. The simulated used-market BEV share for 2025 should be about 3.5%.
3. The mean simulated BEV annual efficiency in GB weather should be about 3.0–3.5 mi/kWh battery-side, or about 2.8–3.3 mi/kWh at the wall [derived].
4. Simulated January BEV kWh/mi should be roughly 1.2–1.3 times July [derived from the curve].
5. The PHEV fleet's electric energy share should be about 31% overall (OBFCM), and about 45–49% if restricted to private keepers.
6. Mean car age should be about 9.7–10 years, with about 46% of cars over 10.
7. The segment mix should show supermini + lower medium + dual purpose ≈ 77%.

## (c) Named gaps and suggested design choices

| Gap | Suggested design choice |
|---|---|
| **DfT time series 2016–2025 by fuel and by make/model** (VEH1103/VEH0141/VEH1111), not retrieved because the host was blocked | Fetch from origin outside this sandbox. Until then, interpolate the fuel shares linearly and mark them as provisional. |
| **Sales-weighted or parc-weighted battery and AC-limit distribution** | Build it once from the VEH0141 make/model counts joined to EV Database specs, and store it as a lookup table. |
| **GB-specific PHEV utility factor by keeper**: no UK split exists | Use ICCT private/company shares, conditioned on whether the household has home charging. |
| **Real-world mpg distribution by segment**: only fleet-mean gaps were found | Apply the age/fuel gap ratio to VCA official figures per model. |
| **What fuel an EV replaces**: no GB data found | Assume the replaced car follows the used-parc fuel mix of the household's age and income band. Expose this as a declared assumption. |
| **Heat-pump fitment by model** | Use the EV Database per-model flag, with model-year defaults. |
| **US bias in winter studies** (Recurrent, Geotab) | Calibrate to the What Car? UK test and EV Database −10°C/23°C anchors. GB winters sit mainly at 0–10°C, where the evidence is thinnest. |

## Done

Published on 25 Oct as the Knowledge page `site/knowledge/which-cars-households-run-and-what-they-use/`, with the note `docs/market_research/which_cars_households_run_and_what_they_use_2026-10-25.md`. The note carries the verification pass that the 25 Oct verify steer asks for: each [unverified] item is marked confirmed, corrected or still open, and no open item is stated on the page as a claim. Counts as recorded: Counts: confirmed 1 · corrected 0 · still open 7 (one of them, item 2, a finding that the source does not say).
