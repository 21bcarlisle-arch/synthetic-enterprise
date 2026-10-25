# Which cars households run, and how much energy each one really uses (UK/GB, 2001-2026)

**Knowledge:** which-cars-households-run-and-what-they-use

*Written 25 Oct 2026 from the advisor's cited evidence pack
(`docs/staging/advisor/done/DIRECTOR_EVIDENCE_VEHICLE_MIX_AND_REAL_WORLD_EFFICIENCY_2026-10-25.md`).
[derived] = our arithmetic. Most sources are UK-wide; NI is ~3% of UK cars (VEH0103, below).*

## 1. The parc

| Metric | Value | Source |
|---|---|---|
| Licensed cars UK, Sep 2025 | 34,486k; ZEV 1,630k (4.7%), +37% y/y | https://www.gov.uk/government/statistics/vehicle-licensing-statistics-july-to-september-2025/vehicle-licensing-statistics-united-kingdom-july-to-september-2025--2 |
| Licensed cars UK, Dec 2024 | 33,967k; ZEV 1,287k (3.8%); average age 10 years | https://www.gov.uk/government/statistics/vehicle-licensing-statistics-2024/vehicle-licensing-statistics-united-kingdom-2024 |
| Private and light goods cars by nation, Q4 2025 (VEH0103, fetched 25 Oct 2026, sha256 aff7bb74...c7cb3) | UK 31,139k; GB 30,189k; England 25,742k; Scotland 2,388k; Wales 1,513k; NI 950k (3.05% of UK [derived]) | https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-tables |
| SMMT cars in use, end 2024 | 36.17m: petrol 58.2%, diesel 32.1%, BEV 3.7% (1.33m); plug-ins 2.16m, so PHEV ~0.83m [derived] | https://cardealermagazine.co.uk/british-motor-parc-grew-to-record-levels-in-2024-as-fiesta-remained-most-common-car-smmt/314319 |
| SMMT cars in use, end 2025 | 36.68m; BEV 1.80m (4.9%) | https://www.am-online.com/news/uk-vehicle-parc-hits-record-425m-as-evs-rise-but-fleet-ages |
| Company keepers | 10.4% of all cars; 55.4% of ZEVs | https://www.fleetnews.co.uk/news/more-vehicles-on-uk-roads-than-ever-before-with-rise-in-evs |
| Age | 9.7 years (2025); 45.7% over 10 | am-online, above |

DfT counts licensed cars; SMMT counts cars in use (incl. SORN). Use DfT for cars households drive.

**Segments, 2025 parc (SMMT Motorparc, https://www.smmt.co.uk/?p=70022):** supermini 32.9%, lower
medium 26.2%, dual purpose (SUV) 18.6%, upper medium 8.7%, MPV 4.3%, executive 3.8%, sports 2.8%,
mini 2.3%, luxury 0.5% [derived shares].

**New registrations 2025 (SMMT):** 2,020,520; BEV 23.4%, HEV 13.9%, PHEV 11.1%, ICE incl. MHEV 51.5%.
2024: company keepers took 82% of new ZEVs (DfT 2024).

**Top BEVs:** new 2025: Model Y 24,298; Model 3 21,188; Q4 e-tron 14,433 ...
(https://www.gateway2lease.com/blog/company-fleets/uks-top-10-evs-in-2025). Private parc c.2024
(Cap hpi via Ohme, https://ohme-ev.com/news-and-press/uk-most-popular-evs/): Leaf 39,421; Model 3
39,263; Zoe 20,784; Model Y 18,720; Niro 17,461.

## 2. Battery and AC limit

EV Database usable battery, all listed models: mean 73.4 kWh (21.3-141), not sales-weighted
(https://ev-database.org/uk/cheatsheet/useable-battery-capacity-electric-car). Sales-weighted 2025
new BEVs (top ten less Q6, variant midpoints): ~68 kWh, bounds 59-78 [derived]. Onboard AC limit
11 kW on the Model Y Performance (EV Database); "many EVs max out at 11 kW" (myenergi support).

## 3. Electric energy per mile

- EV Database real-world consumption: average 303 Wh/mi; Model 3 218-243, Model Y 255-277,
  ID.3 256-263, Leaf 265-268, MG4 270-309, Enyaq 266-280, ID.4 276-296, Q4 268-293
  (https://ev-database.org/uk/cheatsheet/energy-consumption-electric-car). The page says only
  "data is based on real-world values"; it does not say battery- or wall-side (checked 25 Oct 2026).
- Temperature: Recurrent, Nov 2025 (>30,000 US vehicles): 78% of ideal range at 0 C, 70% at -7 C;
  a heat pump adds ~10% at 0 C (https://www.recurrentauto.com/research/winter-ev-range-loss).
  Geotab: peak 115% of rated range at 21.5 C, 54% at -15 C (https://www.geotab.com/uk/blog/ev-range/).
  EV Database: +37% consumption at -10 C with heating vs 23 C. What Car? UK winter test (6-11 C):
  real range 21-38% below WLTP; heat pump +5.5% at ~10 C
  (https://whatcar.com/news/electric-car-best-winter-range/n24274).
- Multiplier for the world [derived]: 1.0 near 20-23 C; 1.15-1.2 at 10 C; 1.28 at 0 C; 1.43 at
  -7 C; heat pump reduces the 0 C penalty by 8-10 points. Range-based figures are not identical to
  kWh/mile; treat as a stated belief with that range.
- Charging losses, ADAC (reported Aug 2026, https://thenextweb.com/news/adac-ev-home-charging-losses-wallbox-socket):
  11 kW wallbox 5.1-7.0%; 2.3 kW socket 12.7-24.2%. Wall-to-battery 0.93-0.95 wallbox, 0.76-0.87 socket [derived].

## 4. Plug-in hybrids

- ICCT/Fraunhofer 2022 (~9,000 vehicles): electric share private 45-49%, company 11-15%; WLTP
  assumes 70-85% (https://theicct.org/wp-content/uploads/2022/06/fs-real-world-phev-use-jun22.pdf).
- Fraunhofer/Oeko-Institut 2025, 981,139 OBFCM PHEVs: charge-depleting km share 42.4%; energy-based
  electric share 31.0%; real 5.89 L/100 km vs 1.53 WLTP; CD ~2.8, CS ~7.4 L/100 km
  (https://www.oeko.de/fileadmin/oekodoc/Analyse_PHEV_2025_EN_final.pdf).
- Electric share is driven by charging behaviour and keeper type more than battery size.

## 5. The petrol and diesel counterfactual

- NEDC-era gap (ICCT Lab-to-Road): 8% (2001), 28% (2012), 39% (2015, 2017)
  (https://theicct.org/news/real-world-vehicle-fuel-consumption-gap-europe-stabilizing).
- WLTP-era gap (EC OBFCM, 2022 registrations): petrol +21.1%, diesel +17.1%
  (https://climate.ec.europa.eu/news-other-reads/news/publication-real-world-co2-emissions-and-fuel-consumption-cars-and-vans-collected-2022-2024-07-26_en).
- Full hybrids: ~70% of advertised mpg (Honest John).
- Real ICE fuel use = official figure x gap for registration year and fuel x dated weekly pump price.

## 6. Turnover

Ownership ~62 months (Tesla ~29); used transactions 7.81m in 2025, BEV 3.5%; used 3-5-year-old EV
£18,266 vs petrol £18,731 (Auto Trader, May 2025). What an EV replaces: no GB data; ~a third of EV
owners keep an ICE car (Zapmap, 2022); DfT EV tracker year 2: 48% of BEV drivers also drove petrol.

## 7. Distributions for the world (inputs to the asset design note)

| Attribute | Draw | Conditioned on |
|---|---|---|
| Fuel of household car | Categorical from the parc by year (private keepers) | Mileage, income, parking, year |
| Segment, model | SMMT parc and registrations; Cap hpi private parc | Fuel, income, vehicle age |
| Usable battery, AC limit | Model lookup; fallback ~68 kWh, 11 kW (new) | Model, year |
| BEV base efficiency | Model lookup 218-309 Wh/mi; fallback 303 | Model |
| Temperature multiplier | Piecewise as section 3 | Day's local mean temperature; heat pump |
| Charging efficiency | 0.93-0.95 wallbox; 0.76-0.87 socket | Charger type |
| Home charge power | min(onboard limit, supply) | Supply phase |
| PHEV electric share | Beta, mean ~0.47 private, ~0.13 company | Keeper, home charging |
| ICE real/official | 1.08-1.39 NEDC by year; 1.17/1.21 WLTP | Registration year, fuel |

## 8. Population checks

1. Private BEV share end-2025 below 4.9%. 2. Mean age 9.7-10, ~46% over 10. 3. Supermini + lower
medium + SUV ~77%. 4. BEV 3.0-3.5 mi/kWh battery-side annual. 5. January kWh/mi 1.2-1.3x July.
6. PHEV electric energy share ~31% overall, 45-49% private. 7. Used-market BEV share ~3.5% (2025).

## 9. Named gaps

1. DfT VEH1103/VEH0141/VEH1111 by fuel and model, 2016-2025: not read.
2. Parc-weighted battery and AC-limit distribution.
3. Battery- vs wall-side basis of EV Database consumption: unstated by the source.
4. GB PHEV utility factor by keeper.
5. Fuel an EV replaces.
6. GB cold-weather (0-10 C) consumption evidence.
7. Most GB homes single-phase (home charging capped ~7.4 kW): practitioner fact, retailer-only source.

## Verification pass, 25 Oct 2026

### Verification of the vehicle mix and real-world efficiency pack (25 Oct 2026)

| # | Item marked [unverified] or not retrieved | Outcome | Source / note |
|---|---|---|---|
| 1 | NI about 3% of the UK car fleet | **confirmed** | VEH0103 Q4 2025: NI 950k of 31,139k private and light goods cars = 3.05%. Fetched 25 Oct 2026 |
| 2 | EV Database consumption is battery-side | **still open (finding: source silent)** | Page states only "data is based on real-world values"; no battery/wall statement (checked 25 Oct 2026) |
| 3 | Older private parc batteries ~22-62 kWh; parc-weighted mean likely < 60 kWh | **still open** | Needs VEH0141 make/model joined to specs |
| 4 | Older PHEVs ~9-14 kWh gross, 30-60 km | **still open** | Not checked |
| 5 | All 2025 top-10 BEVs have 11 kW AC | **still open** | Only Model Y Performance confirmed (EV Database) |
| 6 | Leaf 6.6 kW, Zoe 22 kW, i3 7.4-11 kW, MG 6.6-7 kW | **still open** | Not checked |
| 7 | Most GB homes single-phase, home charging capped ~7.4 kW (32 A) | **still open at primary** | Retailer source only (Electric Point: "almost all UK homes have a single-phase 100A supply"); no DNO/ENA or EST statement found |
| 8 | DfT VEH1103/VEH0141/VEH0142/VEH1111 not retrieved | **partly closed** | Table index reachable now; VEH0103 fetched. Fuel-by-year and make/model tables not yet read |

**Counts: confirmed 1 · corrected 0 · still open 7 (one of them, item 2, a finding that the source does not say).**

The pack's other figures carry fetched URLs in the pack itself and were not re-checked here.
VEH0103 sha256 aff7bb74272fde9f45a54162bc320788e0f8e03f582ec2074ecd7f37eb4c7cb3.
