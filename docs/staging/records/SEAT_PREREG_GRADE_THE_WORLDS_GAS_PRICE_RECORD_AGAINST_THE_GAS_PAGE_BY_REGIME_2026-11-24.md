**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `SPINE_3_gas_storage_crisis_regime`

# Pre-registration: grading the world's gas price record against the gas page, by regime (2026-11-24)

Written by the delivery seat on 24 Nov 2026, BEFORE the probe below has run. It answers item 1 of the
05:40 addendum to the director's steer of 24 Nov (signed text `452de5285`), carried by
`docs/staging/WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`
item 1: "grade the world's gas price record and any gas drawing for forward years against it."

## What is graded, and against what

- **The world's record** is what every run reads today: `sim.gas_prices_history.load_nbp_history()`,
  the FRED/IMF monthly TTF proxy at a fixed 1.28 $/£, spread flat over each month's days. The SAP
  splice (`load_gas_baseline_spliced`) has landed but no run reads it, so it is NOT the subject.
- **The forward gas draw** is `sim.scenario.gas_scenario_generator.generate_gas_scenario_prices`,
  scenario `baseline_2025`, seed `"gas_scenario"`, years 2026-2027. It is the only forward-year gas
  generator in `sim/`.
- **The published record** is GB System Average Price, `sim/gas_data/sap_daily.csv` (ONS / National Gas,
  OGL v3), 2018-01-01 onward.
- **Regimes**, fixed by date and the same as the chain grade (`2a24f6c54`) except that SAP starts in
  2018: pre-crisis 2018-01-01..2021-06-30; crisis 2021-07-01..2023-06-30; post-crisis
  2023-07-01..2025-06-07 (the proxy's RECORD_END). The forward draw is graded against post-crisis SAP.

## Each check is one mechanism the gas page names

| # | Mechanism (gas page section) | Statistic |
|---|---|---|
| G1 | Global LNG/TTF sets the level | monthly-mean MAE and bias, world − SAP, £/MWh |
| G2 | Seasonal, weather-driven demand against thin storage | winter (Oct-Mar) / summer (Apr-Sep) ratio of monthly means |
| G3 | Daily balancing, linepack and cold snaps | SD of daily log returns |
| G4 | Cold-snap and supply-shock spikes | share of days > 1.5 × trailing-30-day median |
| G5 | IUK/BBL export limit decouples NBP from TTF | Jun-Sep 2022 mean, (SAP − world)/world |
| G6 | Persistence (storage, contracts) | lag-1 autocorrelation of daily price |

## Predictions, filed before the run

- **G1** pre-crisis MAE ≤ £1.5; crisis MAE £15-35 with bias world ABOVE SAP; post-crisis MAE ≤ £2.
  (Partly known already: the 18 Nov splice table shows annual differences of ≤1% outside 2021-22 and
  −29% in 2022. The monthly MAE is not known.)
- **G2** SAP winter/summer ratio pre-crisis 1.2-1.6; the world's within ±0.10 of SAP pre- and
  post-crisis; in the crisis the world's differs from SAP's by more than 0.20. Forward draw ratio
  1.00 ± 0.03 against post-crisis SAP 1.1-1.4.
- **G3** SAP: pre 0.03-0.08, crisis 0.08-0.20, post 0.03-0.07. World ≤ 0.03 in every regime, and
  ≤ 0.4 × SAP. Forward draw ≥ 0.25, at least 4 × post-crisis SAP.
- **G4** SAP: pre 0.2-2%, crisis 2-8%, post < 1%. World ≤ 0.5% in every regime. Forward draw ≥ 1%.
- **G5** SAP at least 40% below the world in Jun-Sep 2022.
- **G6** SAP ≥ 0.90 in every regime; world ≥ 0.95 (flat months). Forward draw within ±0.05 of 0
  (independent daily draws; this one is known by construction and is a check, not a prediction).

## What would change the reading

If G1 is inside its band everywhere but the crisis, the world's level is right and the fault is
the hub (G5). If G3/G4 fail for the world, the world cannot show any gas mechanism below a month.
If the forward draw fails G2, G3 and G6 together, forward years carry a gas price with none of the
page's mechanisms: no season, no persistence, and noise in their place. The result goes to
`docs/staging/records/SEAT_RESULT_...` beside this file, with each wrong prediction kept.
