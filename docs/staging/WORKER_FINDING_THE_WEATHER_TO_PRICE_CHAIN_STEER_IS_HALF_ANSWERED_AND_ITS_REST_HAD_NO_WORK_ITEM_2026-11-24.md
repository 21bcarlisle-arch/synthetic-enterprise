**Severity:** BLOCKING · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# The weather-to-price chain steer is half answered, and the rest of it had no work item

Found by the worker, 24 Nov 2026, while archiving the advisor steer
`docs/staging/advisor/done/DIRECTOR_STEER_GRADE_THE_WEATHER_TO_PRICE_CHAIN_ON_THE_RECORD_NOW_SO_FORWARD_YEARS_ARE_NOT_HELD_BY_IT_2026-11-24.md`.

**Which text has authority.** The ruling is the advisor-signed staging commit `452de5285`. The later
edit `3589e04c7` is unsigned. It appends only a worker's progress note, with no new ask. That note's
claims were checked against the tree: the pre-registration landed in `2a24f6c54`, and the result is
in `docs/staging/records/WORKER_RESULT_THE_WEATHER_TO_PRICE_CHAIN_LOSES_TO_A_GAS_ONLY_NULL_AT_THE_MONTH_IN_EVERY_REGIME_2026-11-24.md`.

**Why this is filed.** The steer lives in the advisor room, and the work system does not derive items
from that room. No item in `docs/work/items/` names the chain, the gas page or the carbon arm. Once
the steer is archived, nothing would carry the remaining asks. This finding carries them, at the
steer's own BLOCKING grade. **What it blocks:** `sim/weather_price_chain.py` loses to a gas-only
null at the month and the quarter in every regime, and forward years will price from it.

## Done (steer §1-2)

- Bands pre-registered before the run (`2a24f6c54`).
- Graded by regime on the record. Monthly MAE is £12.4, £31.5 and £10.2 against a gas-only null's
  £5.4, £24.5 and £6.7. Five of six predictions were wrong, and they stay beside the outcomes.

## Owed, in the 05:40 addendum's order (it supersedes the first section's order)

1. **K8 deep gas page.** How NBP/SAP forms: UKCS, Norwegian flows, LNG and the global LNG market,
   storage and the loss of Rough in 2017, IUK/BBL and TTF coupling, weather-driven demand, and the
   2021-23 shock. Then grade the world's gas record (start from the 18 Nov daily SAP splice) and
   any forward gas draw against it. `docs/market_research/how_gb_gas_and_power_prices_move_2026-10-25.md`
   is the nearest existing page. It is short, and it is where to start rather than a substitute.
2. **K8 deep electricity page.** Merit order: gas SRMC with carbon (CPS plus UK/EU ETS), CfD/RO and
   negative prices, nuclear, interconnectors by year (FR, BE, NL, NO, DK, IE) including the 2022
   exports, the Capacity Market, scarcity and the BM, and weather-driven demand. Mechanism, not only
   numbers.
3. **Carbon arm.** Grade with and without CPS plus the traded allowance price. File the predicted
   improvement first. Find a UKA market series, or state the gap: the civil-penalty price is not
   the market price (`docs/market_research/eu_uk_ets_carbon_price_series_2026-08-03.md`). The result
   shows a pre-crisis bias of −£12/MWh that grows year by year. That fits missing carbon, but it is
   not yet attributed.
4. **Rebuild in order of the largest gap.** The grade names weather coupling two to five times too
   strong (wind above all), the pre-crisis bias, and crisis mis-scaling at high gas. Add
   interconnector coupling or state why not. If the fix is not made, every forward figure carries
   the known error beside it.
5. **Endogenous CfD levy for forward years.** Strike against the simulated reference price, times
   volumes. Check it on the record against LCCC's Interim Levy Rate, including the negative 2022
   rate. The supplier sees the levy only. The same applies to any price-dependent policy cost.
   Forward carbon is a drawn input in a sourced band, and the band is the director's curriculum.
6. **Learning loop.** File "a world model built to L4 with no knowledge page beneath it", and find
   the other world models in the same state.
7. **Placement.** First in the feature third at Sunday's weekly review, or earlier if the third has
   room this week.

Close this when 1-6 have landed or been ruled out with a reason. Moving this document does not
close it.

## Progress, 24 Nov (delivery seat)

- **Item 1 landed.** The gas page is `docs/market_research/how_the_gb_gas_price_forms_nbp_and_sap_2026-11-24.md`,
  served from `site/data/knowledge_gas_wholesale.json`. The grade was pre-registered in `4abe9cf16`, with
  the result in `docs/staging/records/SEAT_RESULT_GRADING_THE_WORLDS_GAS_PRICE_RECORD_AGAINST_THE_GAS_PAGE_BY_REGIME_2026-11-24.md`.
  The world's level is right outside the crisis (monthly MAE £0.58 and £1.27). The crisis error
  (£16.40) is the interconnector decoupling of 2022. Within a month the world's gas price does not
  move at all. The forward gas draw is independent daily noise:
  `docs/staging/SEAT_FINDING_THE_FORWARD_GAS_DRAW_IS_INDEPENDENT_DAILY_NOISE_WITH_NO_SEASON_OR_PERSISTENCE_2026-11-24.md`.
- **Item 6 landed.** The learning-loop row is in `docs/institutional/ways_of_working.md` W5. The census is
  `docs/staging/SEAT_FINDING_WORLD_MODELS_BUILT_TO_THEIR_CEILING_WITH_NO_MECHANISM_PAGE_BENEATH_THEM_2026-11-24.md`.
- **Item 2 landed.** The electricity page is `docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md`,
  served as the electricity-wholesale page from `site/data/knowledge_wholesale.json`. The grade was
  pre-registered in `6c828bc2c`, with the result in
  `docs/staging/records/SEAT_RESULT_GRADING_THE_WORLDS_POWER_RECORD_AGAINST_THE_ELECTRICITY_PAGE_BY_REGIME_2026-11-24.md`.
  The world's SSP record has the right monthly level (within £2 of the traded price outside the crisis).
  It carries 1.8-2.1× the traded price's within-day swing:
  `docs/staging/SEAT_FINDING_THE_WORLD_SETTLES_AT_THE_IMBALANCE_PRICE_WHICH_CARRIES_TWICE_THE_TRADED_PRICES_WITHIN_DAY_NOISE_2026-11-24.md`.
  Gas plus carbon explains the traded price before the crisis with nothing fitted: monthly MAE £2.80, against £17.58
  for gas alone.
- **For item 3, the carbon arm's prediction is filed** in that result record, before the arm runs: the
  chain's pre-crisis bias moves from −£12.0 to within ±£4, and its MAE falls from £12.4 to ≤ £7.
- **Correction to item 5, beside the claim.** "The negative 2022 rate" is wrong. The Interim Levy Rate
  cannot be set below £0/MWh (Ofgem, *Decision on the CfD allowance methodology*, June 2022). The 2022
  benefit to suppliers came through reconciliation and generator paybacks. An endogenous levy must
  produce a negative NET payment, not a negative ILR (page §3).
- **Next: item 3**, the carbon arm. It needs a UKA market series first (page GAP 1). Items 4-5 follow.

## Progress, 24 Nov (worker)

- **Item 3 landed.** The UKA market series is held: 116 UK ETS auctions, May 2021 to Dec 2025, from the
  UK ETS Authority's reports, in `docs/market_research/uk_ets_allowance_auction_clearing_prices_2021_2025.json`.
  The electricity page's GAP 1 is closed. The arm's result is
  `docs/staging/records/WORKER_RESULT_CARBON_EXPLAINS_THE_CHAINS_PRE_CRISIS_BIAS_AND_ITS_MULTIPLIER_ALREADY_CARRIES_IT_AFTER_2021_2026-11-24.md`.
  Pre-crisis, carbon takes the chain's bias from −£12.0 to +£3.1 (held) and its MAE to £7.14 (≤ £7
  missed by £0.14). The chain still loses to the gas-only null. After mid-2021 the term makes the chain
  much worse (MAE 31.5 → 53.2, 10.3 → 23.4; filed as "fall by less", wrong in sign). The leading
  explanation is that the reduced form's multiplier was fitted with carbon at zero and already carries it.
- **Next: item 4.** Its first step is the refit that tests that explanation, with its prediction already
  filed in the result record. The same step fills `merit_order_reconstruction`'s 2022-2024 allowance gap
  years, which can now be sourced.

## Progress, 24 Nov (worker, item 4 step 1)

- **The refit ran.** The result is in
  `docs/staging/records/WORKER_RESULT_REFITTED_WITH_CARBON_IN_ITS_FLOOR_THE_CHAIN_STOPS_DOUBLE_COUNTING_CARBON_AFTER_2021_2026-11-24.md`.
  It changes one variable: A0/A1/A2 are refitted with carbon in the floor, on the shipped window and
  grid point. The constants go from 0.327 / 1.335 / 3.828 to 0.292 / 1.079 / 2.824. Monthly MAE by
  regime moves from 12.4 / 31.5 / 10.3 to 6.75 / 24.3 / 9.29. Post-crisis ≤ £11 **held**. Pre-crisis
  bias within ±£5 **missed**, at −£5.43. Explanation (a), that the multiplier already carries carbon,
  is not refuted.
- **The chain ties the gas-only null in the crisis (24.3 against 24.5) and still loses either side**
  (6.75 against 5.4, and 9.29 against 6.7). Carbon was one gap. Weather coupling is next.
- **Correction, beside the previous note.** That note said this step would also fill
  `merit_order_reconstruction`'s 2022-2024 allowance gap years. It did not. That belongs with the
  carbon series the sim will read, so that one table holds the allowance price.
- **Next, still item 4.** (i) Ship the refit. The sim needs a time-indexed historical carbon series,
  built from the UKA auction file, the EUA table and CPS, and the chain must pass it. The refitted
  constants without carbon in the call are worse than either shipped arm, so the two land together. Forward
  carbon waits on item 5's curriculum band. (ii) The weather-coupling arm (wind first), with its
  prediction filed before it runs.

## Progress, 24 Nov (worker, item 5 on the record)

- **The on-the-record check ran.** It was pre-registered in
  `docs/staging/records/WORKER_PREREG_THE_CFD_LEVY_FROM_STRIKE_AGAINST_THE_WORLDS_PRICE_ON_THE_RECORD_2026-11-24.md`.
  The result is in `docs/staging/records/WORKER_RESULT_THE_CFD_LEVY_BUILT_FROM_THE_WORLDS_PRICE_MATCHES_THE_RECORD_TO_A_FEW_PERCENT_2026-11-24.md`.
  The data is LCCC's own: per-unit daily CfD payments and reconciled levy rates, 2016-2026, OGL.
- **(Strike − world's daily price) × real generation gives each year's net CfD cost within ±2%
  outside the crisis.** 2021 is +3.3%, and 2022 is off by £33m (−£313m against −£346m). The
  definition matches LCCC's reconciled rate in 46 of 46 quarters. Four of six predictions held. The
  misses stay beside the outcomes.
- **Correction to the earlier correction, beside it.** The ILR is floored at zero, but LCCC's
  reconciled daily levy rate was negative on 238 days of 2022 (low −£22.68/MWh). So the steer's
  "negative 2022 rate" is right of the reconciled rate. The world should produce that rate.
- **What remains of item 5:** the forward CfD fleet and volumes (LCCC publishes them; not yet read,
  so it is a GAP), and a forward price graded before a levy is built on it (item 4's). The
  negative-hour rules wait on the Standard Terms (page GAP 3). Forward strikes and carbon are the
  director's curriculum band.


## Progress, 24 Nov (worker, item 4 step ii: the weather-coupling arm)

- **Pre-registered** in `docs/staging/records/WORKER_PREREG_WHICH_LEG_OF_THE_WEATHER_TO_PRICE_CHAIN_CARRIES_ITS_OVER_COUPLING_TO_WIND_2026-11-24.md`
  (`8e8790de4`, before the run). **Result** in
  `docs/staging/records/WORKER_RESULT_THE_CHAINS_OVER_COUPLING_TO_WIND_IS_IN_ITS_POWER_CURVE_NOT_ITS_PRICE_LEG_2026-11-24.md`.
  Four of five predictions held.
- **Coupling is now measured as a slope, not a correlation.** The chain's wind slope is 4.6× the
  record's before the crisis and 1.6× after it. Nearly all of the excess is in wind speed → wind
  output: the chain's renewable MW moves 2.3–3.9× the real fleet's per m/s. Swapping in real
  renewable output brings the slope to within 0.75–1.4× of the record. The price leg, given real
  inputs, is 0.92–1.35× the record per GW.
- **Interconnectors: why not, for now.** The price leg is not the over-coupled link. A damping term
  is the smaller gap.
- **Next, still item 4.** A K8 section on the GB fleet's aggregate power curve, with a per-year
  fleet. Then the arm with its prediction filed first. Separately, the post-crisis −£8 level gap the
  price leg shows with real inputs. Shipping the step-1 refit with a sim carbon series ((i) above)
  is still owed.

## Progress, 24 Nov (worker, item 4 step iii: the fleet power curve, knowledge then pre-registration)

- **K8 first.** §6a of `docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md` covers how
  a fleet turns wind into output, from Staffell and Pfenninger 2016, read in full. Their method is per
  farm: hub-height extrapolation, a Gaussian-smoothed curve (σ = 0.6 + 0.2·w), and corrected speeds
  w′ = αw + β. On that method, GB hourly R² is 0.935. The world uses one turbine curve on a 10 m daily
  mean over four customer towns, which averages 3.7-4.6 m/s. It differs from the published chain at all
  four stages. New gap 8: a GB national-aggregate curve and a farm register.
- **Pre-registered** in `docs/staging/records/WORKER_PREREG_A_FLEET_AGGREGATE_POWER_CURVE_TAKES_THE_CHAINS_OVER_COUPLING_OUT_OF_ITS_WIND_LEG_2026-11-24.md`:
  curve {single, aggregate} × fleet {whole, per-year}. The curve is fitted on 2016-19 only. Seven
  predictions and the decision rule are filed before the run.
- **Next, still item 4:** run it and put the result beside the predictions. Still owed and separate:
  shipping the step-1 refit with a sim carbon series, and the post-crisis −£8 level gap.

## Progress, 24 Nov (worker, item 4 step iii on the record)

- **Result** in `docs/staging/records/WORKER_RESULT_A_FLEET_AGGREGATE_POWER_CURVE_TAKES_THE_CHAINS_OVER_COUPLING_OUT_OF_ITS_WIND_LEG_2026-11-24.md`.
  Seven of seven pre-registered predictions held. The curve was fitted on 2016-19 only.
- **The over-coupling was the curve's shape.** The aggregate curve puts the wind leg at 0.75-1.19×
  the record's MW per m/s, against 2.2-3.8×. The price slope moves to 0.66-1.57×, against 1.6-4.6×.
  With the per-year fleet (E), monthly MAE is 6.39 / 16.95 / 8.20, against the chain's
  6.75 / 24.33 / 9.29 and the null's 5.4 / 24.5 / 6.7. The chain now beats the null in the crisis and
  loses by about £1-1.5 either side, on the price leg.
- **Next, still item 4: the build.** Put the aggregate curve and per-year fleet into
  `sim/weather_price_chain`, landed with the step-1 refit and its sim carbon series. It carries two
  caveats: hold the curve above 10 m/s, and source the forward fleet from a capacity path. Separately,
  the post-crisis −£8 level gap is still owed.

## Progress, 24 Nov (worker, item 4 build, step A: the map's condition 2)

- **The build is split into two one-variable steps** so each move can be attributed. Step A is
  the AGWS dedup (map C3). Step B is the aggregate curve, the per-year fleet, and the carbon refit
  shipped together (map conditions 1, 3 and 4).
- **Step A landed.** `sim/generation_demand_history.latest_publish_per_key` keeps the latest
  publish per (date, period, psrType) before every AGWS sum: wind, solar and renewable. The two
  recalibration scripts' local copies were already correct and are unchanged.
- **Measured on the chain's daily record, predictions filed before the run.** Mean wind went from
  5,519.3 to 5,491.8 MW. A1 held on the drop (−27.5, filed −27) and missed its ±5 level band,
  because the map's 5,509 was not this record's figure. The maximum day went from 35,458 to
  20,977 MW (held). The fleet scalar went from 128,701 to 128,061 MW, −0.50%. A2's < 0.5% held
  at its edge; the map's 0.16% was wrong. Chain-vs-SSP daily MAE went from 23.989 to 23.965 (A3
  held). The wind correlation rose from 0.610 to 0.619.
- **Next, step B:** the curve and the per-year fleet, refitted against the deduplicated record,
  with carbon in the call and in A0-A2 together. The carbon series must sit in the one table
  `merit_order_reconstruction` already holds (map C4).
