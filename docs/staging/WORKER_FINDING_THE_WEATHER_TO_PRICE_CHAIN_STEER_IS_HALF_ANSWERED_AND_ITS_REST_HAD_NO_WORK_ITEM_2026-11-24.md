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

## Progress, 24 Nov (worker, item 4 build, step B: the curve, the fleet and carbon, shipped)

- **The chain is rebuilt.** `sim/weather_price_chain` now prices from the fleet-aggregate curve,
  fitted on 2016-19 and held flat from its in-record maximum (9.23 m/s; 9 record days). Each record
  day uses its own year's fleet, which `renewable_capacity_trend` matches on the same curve.
  Carbon is CPS plus the allowance price by month, from
  `merit_order_reconstruction.carbon_price_in_month_gbp_per_tonne`, which reads the one UKA auction
  file and refuses past the record. The price leg is refitted with that carbon (`fit_price_leg`,
  reproducing `d424b78095`'s constants). `derive_price` refuses a call without carbon and names why.
  `price_engine`'s own constants are unchanged. Map s.5 conditions 1, 3 and 4 are met, and 5 holds
  because gas is untouched.
- **All six predictions, filed before the measure, held.** Monthly MAE is 6.50 / 17.20 / 8.19
  against arm E's 6.39 / 16.95 / 8.20 and the null's 5.4 / 24.5 / 6.7. The chain beats the null in
  the crisis and loses by about £1-1.5 either side, on the price leg. Wind moves 1.06 / 1.12 / 0.81×
  the record's MW per m/s.
- **Unattributed, said plainly:** post-crisis bias is +1.84 where E's was −1.88. The candidate is
  2025, which the trajectory clamps to 2024's fleet. I cannot yet say.
- **Found in the build:** the chain's windiest day is 12.8 GW against the record's 21.0 GW. The
  over-range at the top has become an under-range. That is the missing noise the arm named.
- **Correction, beside the claim** (`renewable_capacity_trend` A3): the mix-share validator divided
  two fleet scalars. Its "5-8pp above DESNZ" was an artefact of the old curve. It now compares
  generation shares, and AGWS runs 1.5-3.5pp below DESNZ.
- **Still owed under item 4:** the gas-input arm (TTF proxy against the daily SAP splice, map C2),
  and the post-crisis price-leg level gap. **Item 5:** the forward CfD fleet and volumes.
  **Forward years:** a capacity path for the fleet, and the curriculum's carbon band.

## Progress, 24 Nov (worker, item 4: the gas-input arm, map C2)

- **Run, with predictions filed before it.** The result is in
  `docs/staging/records/WORKER_RESULT_ON_THE_REAL_GB_GAS_PRICE_THE_CHAINS_ONE_PRICE_LEG_CANNOT_FIT_THE_CRISIS_AND_THE_YEARS_AFTER_IT_2026-11-24.md`.
  Five of nine predictions held. The misses are code 2 and domain 2.
- **The swap does not ship on its own.** With SAP in the call and in the A0-A2 refit, monthly MAE is
  4.77 / 20.88 / 13.00, against the shipped 6.50 / 17.20 / 8.19. Post-crisis bias goes to +12.3.
  One fitted price leg cannot fit both 2022 and 2023-25 on the real GB gas price. On TTF, the proxy's
  29% premium in 2022 stood in for a missing crisis markup.
- **Correction, beside the step-B note** ("it now beats the gas-only null in the crisis"). That holds
  against a null on TTF. Against a null on SAP (17.44), it is a tie. From here, quote both nulls.
- **Next, still item 4:** the arm that names the 2022 markup, run on SAP. The post-crisis −£8 gap is
  the same question. Item 5's forward CfD fleet and volumes are still owed.

## Progress, 24 Nov (worker, item 4: the interconnector arm)

- **Pre-registered** in `ef4b0ef19`, before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_GB_NET_EXPORT_CARRIES_THE_2022_MARKUP_BUT_LEAVES_TWO_THIRDS_OF_THE_POST_CRISIS_GAP_2026-11-24.md`.
  Five of seven predictions held.
- **The leg's residual demand is INDO, which excludes exports.** Adding the real FUELHH net export, on SAP,
  takes 2022's bias from −10.7 to −1.1. The crisis monthly MAE is 17.02, which beats the shipped chain
  (17.20), null_S (17.44) and null_T (24.53). The 2022 markup was a missing demand: France's, on GB plant.
- **The post-crisis bias only falls from +12.3 to +8.2,** and by year it grows from +5.6 to +11.3. That is a
  second mechanism, not yet attributed. The candidates are a fleet more efficient than the 0.50 constant,
  and SSP against MID.
- **Item 4's interconnector ask is answered "add it".** It ships with SAP once a forward flow mechanism
  exists. Nothing in `sim/` changed. **Next, still item 4:** the K8 section on forward flow, then the
  efficiency arm on X.

## Progress, 24 Nov (worker, item 4: the efficiency arm)

- **Pre-registered** in `ca6f4c1a27`, before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_THE_CCGT_FLEETS_EFFICIENCY_BY_YEAR_DOES_NOT_CARRY_THE_CHAINS_POST_CRISIS_BIAS_2026-11-24.md`.
  Five of five predictions held.
- **Efficiency is ruled out.** With DUKES 5.10.C CCGT efficiency by year in the floor, the post-crisis bias
  moves from +8.23 to +8.16. The published efficiency peaks in 2023 (49.91%), so 2023's bias falls £1.59
  and the growth to 2025 widens. A constant efficiency is absorbed exactly by the no-intercept refit, so
  the 0.50 constant is not a defect the chain can see. 2025's efficiency is a GAP.
- **Correction, beside the previous note's candidate list** ("SSP against MID"). The power grade (§10a)
  already has SSP's post-crisis level within £1.76 of MID, so the price choice cannot carry £8. The real
  question is why GB power cleared about £9.80 below gas-plus-carbon SRMC in 2023-25.
- **Next, still item 4:** a K8 note on that question (imports setting the price, gas marginal less often,
  CCGTs bidding below spot SRMC, each a GAP), then the arm that separates them. The forward-flow K8
  section is still owed, and so is item 5's forward CfD fleet.

## Progress, 24 Nov (worker, item 4: why power sat below gas SRMC after the crisis)

- **K8 first.** The new §1a of the electricity page covers how an average price sits below gas SRMC with
  no plant bidding below cost. **Result** in
  `docs/staging/records/WORKER_RESULT_GB_POWER_SITS_BELOW_GAS_SRMC_AFTER_THE_CRISIS_BECAUSE_GAS_IS_OFF_THE_MARGIN_MORE_OFTEN_AND_HALF_THE_GAP_WAS_THE_CARBON_PROXY_2026-11-24.md`.
  The predictions were hashed before the run but not landed first, and the record says so. Three of seven
  held. The misses stay beside the outcomes.
- **Half the −£9.80 was the carbon proxy.** On UKA auction carbon it is −£4.89. **Correction, beside the
  efficiency note's claim** that the −£9.80 "matches the chain's +8.2". The chain already uses auction
  carbon, so the like-for-like gap is about £5.
- **The rest is gas off the margin more often.** In the top CCGT-output quintile, power clears £14-24 above
  fleet SRMC after the crisis, so below-SRMC bidding is not supported. In the bottom quintile it clears
  £37-42 below. Half-hours with CCGT under 5 GW went from 5-7% (2018-19) to 25-37% (2023-24). Imports cannot
  be separated on this split.
- **Next, still item 4:** the chain's own residual by CCGT band, with its prediction filed first. If the
  post-crisis +8.2 sits in the low-CCGT band, the price leg needs a sub-gas shape that scales with SRMC.
  Still owed: the forward-flow K8 section (§5), and item 5's forward CfD fleet.

## Progress, 24 Nov (worker, item 4: the chain's residual by CCGT band)

- **Pre-registered** in `88c69e12a` and landed on origin before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_THE_CHAINS_POST_CRISIS_BIAS_SITS_MOSTLY_ON_THE_DAYS_GAS_IS_OFF_THE_MARGIN_AND_PARTLY_ON_THE_DAYS_IT_RUNS_HARDEST_2026-11-24.md`.
  Five of seven predictions held.
- **Before the crisis the chain matches the record band by band, within £2.5.** After it, the lowest-CCGT
  fifth of days carries about £5.3 of the £8.64 mean daily residual (+25.2 on those days). There the record
  clears £31 below the floor and the chain clears £6 below it. The highest fifth carries about £1.9 (+9.7).
  This was not predicted: the chain clears £22.8 above its floor where the record clears £13.1. One
  multiplier cannot give a deeper bottom and a flatter top at once.
- **The crisis regime's −1.5 bias is a cancellation** (Q1 +12.1, Q4 −17.7). Quote the bands beside it.
- **The filed rule did not fire (a)**, because its C2 missed on the Q5 leg. Nothing ships.
- **Next, still item 4:** a K8 note on what sets price when gas is not marginal, then a price-leg shape arm. The
  shape needs a low-x depth that scales with the floor and a top that can flatten, with the pre-crisis band fit
  held as a control. Still owed: the forward-flow K8 section (§5) and item 5's forward CfD fleet.

## Progress, 24 Nov (worker, item 5: the forward CfD fleet, read)

- **Read, so it is no longer a GAP.** The page is `docs/market_research/the_forward_cfd_fleet_from_lccc_contract_portfolio_2026-11-24.md`,
  from LCCC's `cfd-contract-portfolio-status` (612 units). The live CfD fleet is 11.1 GW. The forward
  pipeline is 38.7 GW, and 23.5 GW of it is expected to start by the end of 2028.
- **Attrition comes in lumps, not at a rate.** 4-7% of the capacity awarded in AR1-3 and AR5 was
  terminated, against 26% in AR4 (Norfolk Boreas) and AR6 (Hornsea Four). The forward fleet is a band,
  not a percentage. Slippage cannot be measured from one snapshot (page GAP 1).
- **Two things downstream now disagree.** `sim/renewable_capacity_trend` holds the physical fleet flat
  after 2025 (curriculum), so a forward levy built from this pipeline would add CfD volumes that the
  world's price never sees. They must come from one capacity path. Also, the CfD start date is not first
  power. AR3-4 offshore phases carry 2027-29 CfD starts, so the paying fleet and the physical fleet are
  two sets.
- **Still owed under item 5:** strikes for AR4-AR7 (page GAP 2), and the forward price graded first
  (item 4). The capacity path is the director's curriculum, so this page sources the band and does
  not pick a value.

## Progress, 24 Nov (worker, item 4: what sets the price when gas is not marginal)

- **K8 first.** §1b of the electricity page covers what sets GB's price when gas is off the margin: imports
  at the neighbour's own marginal cost, CCGTs bidding below their SRMC to avoid a restart, and subsidised
  output at or below zero. Sources are UCL for Ofgem 2019 (read from the PDF) and Modo's SRMC method.
- **The record, binned on fixed CCGT GW rather than quintiles within each year.** At a given amount of gas
  running, SSP is the same multiple of the floor in every regime, within about 0.05 from 6 to 14 GW, while
  the floor moved fourfold. What changed after the crisis is the mix of days: 241 of 708 run under 6 GW,
  against 59 of 1,918 before it.
- **Correction, beside the CCGT-band note's claim** that the shape needs "a top that flattens as the floor
  rises". In the crisis, at the highest floor, the top held its pre-crisis ratio. The quintiles moved down
  the CCGT axis, and the floor's level did not do it. Marked in the result record and in §1a.
- **So the shape arm is held.** First comes an arm that separates the price leg from the gas-running leg. It
  is pre-registered in
  `docs/staging/records/WORKER_PREREG_IS_THE_CHAINS_POST_CRISIS_MISS_IN_ITS_PRICE_LEG_OR_IN_HOW_MUCH_GAS_IT_RUNS_2026-11-24.md`
  (probe sha256 `3cee2860…`), landed before it runs.

## Progress, 24 Nov (worker, item 4: the separating arm on the record)

- **Result** in `docs/staging/records/WORKER_RESULT_BOTH_LEGS_CARRY_THE_CHAINS_POST_CRISIS_MISS_ITS_RESIDUAL_NEVER_RUNS_GAS_LOW_AND_ITS_PRICE_LEG_HAS_NO_LOW_GAS_DAYS_TO_LEARN_FROM_2026-11-24.md`.
  It was pre-registered in `4f9e788e7` and promoted before the run. Four of six predictions held.
- **Given real gas running, a floor multiple fitted on 2016-21 beats every comparator in every regime.**
  Monthly MAE is 3.06 / 9.44 / 6.97, against X's 4.89 / 17.02 / 10.38. Its post-crisis bias of +6.16 sits
  mostly on the 241 days under 6 GW, which the pre-crisis record barely contains.
- **The chain's own residual never runs gas below 6 GW**, in any regime. After the crisis it overstates gas
  running by 3.1 GW, and the composite's post bias is +11.75. This is the larger term.
- **The filed rule fires (b)**, on a £0.16 bias miss. The shape arm returns, second. First is an arm on gas
  running from residual demand: nuclear by year and storage in x, with K8 first on embedded generation and
  batteries.

## Progress, 24 Nov (worker, item 4: K8 on what decides how much gas runs)

- **K8 first, as the separating arm asked.** §4a of the electricity page covers the supply identity and what
  each series meters: INDO, FUELHH, AGWS and NESO's embedded estimates, plus batteries and pumped storage,
  from Elexon's API definitions, NESO's historic demand data and DUKES 5.6/5.16. Batteries net about
  −0.05 GW on a daily mean, so they do not move a daily identity.
- **The identity closes on the record.** INDO + net export − every non-gas FUELHH fuel gives real CCGT with
  R² 0.993-0.998 and a steady −0.56 to −0.78 GW gap in every regime. Station load fits that gap in size.
  The chain's form (INDO − AGWS wind − AGWS solar) reaches R² 0.74-0.81.
- **Three things sit between the chain's residual and gas running.** None of them is in the chain.
  (1) Demand held flat: the chain's demand leg has no year term, while INDO fell from 30.4 to 26 GW. Its
  residual is 1.4-2.0 GW too high in 2022-24, and this is the largest term for the post-crisis miss.
  (2) Must-run by year: nuclear, coal and biomass fell 2.7 GW. This works against the overstatement, not for it.
  (3) Embedded solar counted twice: INDO is already net of it. **This is the defect EP13 fixed in the
  carbon dispatch on 30 Sep (`295e9ad64b`), and it is still live in `sim/weather_price_chain.residual_demand`
  and in the price leg's refit data.** It is one definition with two implementations, the VAT-rule shape.
- **2025 (part year):** the chain's renewables run 4.9 GW under the record, where the fleet is clamped to 2024.
  This is a candidate for the step-B post-crisis bias that was left unattributed.
- **Nothing in `sim/` changed.** **Next, still item 4:** pre-register the gas-running arm. It moves one
  variable at a time, in size order: a demand year term sourced from NESO ND by year, then must-run by year,
  then solar out of the residual. The pre-registration must state that this section's identity and by-year
  legs were seen before it.

## Progress, 24 Nov (worker, item 4: the gas-running arm, pre-registered)

- Filed before its probe runs: `docs/staging/records/WORKER_PREREG_DOES_THE_CHAINS_RESIDUAL_DECIDE_HOW_MUCH_GAS_RUNS_ONCE_DEMAND_MUST_RUN_AND_SOLAR_ARE_IN_2026-11-24.md`.
  It adds §4a's three terms to leg H one at a time (demand by year, must-run by year, solar out), then tries
  the identity form (slope 1) on the same inputs. The decision rule picks the build. Nothing in `sim/` changes.

## Progress, 24 Nov (worker, item 4: the gas-running arm, on the record)

- Result: `docs/staging/records/WORKER_RESULT_A_DEMAND_YEAR_TERM_TAKES_HALF_THE_CHAINS_GAS_RUNNING_MISS_AND_THE_IDENTITY_FORM_LEAVES_1_9_GW_UNEXPLAINED_2026-11-24.md`.
  Five of seven predictions held.
- **A demand year term halves the post-crisis gas-running miss** (+3.12 to +1.73 GW; composite post bias
  +11.75 to +8.44). It is a build term, but it moves the crisis bias from −1.09 to −6.19.
- **Must-run by year and solar out, in the identity form, still leave +1.86 GW after the crisis.** The step
  comes in 2023. That is not attributed. One candidate is the wind leg's AGWS target, which runs 0.36 GW below
  FUELHH after the crisis.
- **Disclosure:** the pre-registration was gated as `f616ad94e` before the run, but promoted to origin only
  after it.
- **Next, still item 4:** K8 on a forward transmission-demand path, then the wind-target arm, pre-registered.

## Progress, 24 Nov (worker, item 4: K8 on a forward transmission-demand path)

- **K8 first, as the gas-running arm's rule (a) asked.** §8a of the electricity page sources it. FES's annual
  demand is system demand: end-consumer demand gross of embedded generation, plus losses, weather-corrected,
  in fiscal years (NESO, FES 2025 Table 3 footnote and *Modelling Methods* §2). It is not ND. In FY2024 it is
  289.7 TWh against ND's 230.9 TWh. Embedded wind and solar account for 31.0 TWh of that gap, and about 28 TWh
  is not decomposed (GAP 10a).
- **Out of sample, real 2026 (knowledge only, W6):** ND for 1 Jan to 3 Nov was 25.4 GW mean in each of 2023,
  2024, 2025 and 2026, within 0.7%. ND plus embedded rose 4.4%. Since 2023, growth in demand has been met by
  embedded solar.
- **Forward, by FY2030:** FES 2025 pathways put system demand up 11.8% to 19.0% on FY2024. NESO's 2026 Ten Year
  Outlook, now the yearly source since FES went three-yearly, puts it up 11.7%.
- **What the build must respect:** forward ND and the forward embedded fleet are one capacity path. A FES
  demand paired with `renewable_capacity_trend`'s flat post-2025 fleet would raise the chain's residual by a
  definition mismatch. The default the record supports is ND held at its 2023-25 level. The band is curriculum.
- **Correction, beside the claim**, in `scenario_spine_and_friction_anchors_2026-07-23.md` §1.1: "+8-13% by
  2030" is +17-20% on that table's own figures.
- **Nothing in `sim/` changed.** **Next, still item 4:** the wind-target arm (the chain's wind mean-matched to
  FUELHH instead of AGWS, on G4's inputs), pre-registered first. Shipping the demand year term waits on the
  curriculum's joint demand and fleet band.

## Progress, 24 Nov (worker, item 4: the wind-target arm, on the record)

- **Pre-registered** in `5b1589639` and promoted to origin before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_MEAN_MATCHED_TO_FUELHH_THE_CHAINS_WIND_CLOSES_ITS_POST_CRISIS_GAS_RUNNING_MISS_OUTSIDE_2025_2026-11-24.md`.
  Six of seven predictions held. The W0 control reproduced G4 exactly.
- **The wind leg's target was the rest of the gas-running miss.** With the chain's wind mean-matched to FUELHH
  instead of AGWS, and everything else as in G4, the post-crisis miss falls from +1.86 to +0.71 GW, and to
  −0.02 GW without 2025. The crisis miss is −0.12 GW, and pre-crisis R² improves.
- **2025 (part year) carries about +3.25 GW**, and with it all of the +0.71. AGWS runs above FUELHH that year
  and the fleet is clamped. Not attributed.
- **What is left is the price leg.** Outside 2025 the composite post bias (+5.83) is leg P's own on real gas
  running (+5.79).
- **Next, still item 4:** the build of the wind fleet mean-matched to FUELHH, solar out and the demand year
  term on the record, with predictions filed first. Then 2025, and the price-leg shape arm.

## Progress, 24 Nov (worker, gas page GAP 4 measured)

- **§6a of the gas page** measures how far GB SAP moves with the weather on the record. A day colder
  than its month prices 0.24-1.15% higher per °C in calm years and about 3% higher in 2018 (Beast
  from the East) and 2022. The sign holds in both halves of every year. The summer slope matches the
  winter one in five of eight years, so this is the weather of a cold day (wind, gas-for-power), not
  heating alone. It is not attributed. Temperature explains under a fifth of SAP's daily deviation.
  SAP's winter volatility premium is not stable (ratio 0.52-3.5).
- **For item 4.** A forward daily gas price needs a small persistent cold-day premium that switches
  with the regime. Today's world record and forward draw both have a slope of 0. The page's GAP 4
  stays open: no published response was found, so this is a measurement and not a source.

## Progress, 24 Nov (worker, item 4: the build terms on the chain's own price form)

- **Pre-registered** in `f0cfdf4f4`, promoted before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_ON_THE_CHAINS_OWN_FORM_THE_DEMAND_YEAR_TERM_EXPOSES_A_PRICE_LEG_THAT_RUNS_7_POUNDS_LOW_AFTER_THE_CRISIS_2026-11-24.md`.
  Four of eight predictions held, one was half wrong and three were wrong. **Nothing ships.**
- **The earlier arms used a two-leg form the chain does not ship.** On the shipped one-leg form, demand by
  year, then solar out, then FUELHH wind (each with A0-A2 refitted on the matching residual) take monthly
  MAE from 6.50 / 17.20 / 8.19 to 5.13 / 16.31 / 8.62. Demand by year with solar out (B2) is best: 5.28 /
  15.62 / 6.87.
- **The shipped chain's near-zero post-crisis bias is a cancellation.** Its demand runs about 2 GW high after
  the crisis, and its price leg, run on REAL inputs, runs £7.2-8.0 low on every basis. Forward years
  inherit that accident.
- **Nothing ships because the construction check failed in 2016 and 2025.** Both are
  `renewable_capacity_trend`'s end clamps on record years: 2025 prices at 2024's fleet and runs 4.4 GW
  under AGWS wind.
- **Next, still item 4:** (1) the §1b price-leg shape arm, against the leg-on-real rows as its control;
  (2) record years taking their own fleet, not the clamp; (3) then rerun B1-B3.

## Progress, 24 Nov (worker, item 4 step 2: the end-year clamps, measured before building)

- **Result** in `docs/staging/records/WORKER_RESULT_THE_END_YEAR_CLAMP_ARM_MEASURED_BEFORE_ANY_BUILD_2016_CAN_TAKE_ITS_OWN_FLEET_AND_2025_CANNOT_2026-11-24.md`.
  **Nothing ships.**
- **The step's control cannot fail.** A year that takes its own mean-matched fleet reproduces its own
  AGWS wind mean by construction, so B-P4 passes in 2016 and 2025 whatever the fleet. The independent
  check is the fleet over DUKES capacity, which runs 0.417-0.472 in 2017-22.
- **2016 can take its own fleet** (0.415). The clamp to 2017 gives 0.506. **2025 cannot** (0.717). That
  is not the half-year artefact, which I predicted wrongly before the run: a January-June fleet runs
  0.78-1.09 of a full year. 2025's town wind is calm (3.23 m/s against 3.91-4.71), and the 2024 fleet it
  falls back on is itself depressed.
- **New finding:** `docs/staging/WORKER_FINDING_ELEXONS_PUBLISHED_AGWS_WIND_HOLDS_ABOUT_HALF_THE_METERED_WIND_IN_THREE_WINDOWS_2026-11-24.md`.
  Published AGWS loses most offshore wind in April 2017, February-July 2023 and May-October 2024. It
  falls to 0.62-0.64 of DUKES generation in 2023-24, while FUELHH holds about 0.77. Every
  AGWS-basis grade today carries those windows in its 2023-24 rows. That supports the wind-target
  arm's FUELHH basis.
- **Next, still item 4:** (1) the §1b price-leg shape arm, unchanged. (2) Redo step 2 on a FUELHH-basis
  fleet with DUKES-capacity ratio as its control, not B-P4: 2016 on its own fleet, and 2025 held
  explicitly as "calm weather plus a clamped fleet", stated beside every 2025 figure.

## Progress, 24 Nov (worker, item 4: the price leg's shape arm, on the record)

- **Pre-registered** in `8e2faf1a3`, promoted before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_THE_PRICE_LEGS_POST_CRISIS_MISS_IS_A_LEVEL_NOT_A_SHAPE_A_NON_GAS_CONSTANT_HELPS_EVERY_REGIME_2026-11-24.md`.
  Seven of seven predictions held. **Nothing ships.**
- **The leg's post-crisis miss is a level, not a shape.** On real daily x, neither a constant that does not
  scale with gas (b0 about £5-6) nor a floor-scaled low-x depth, nor both, brings the R post bias inside ±£3.
  The best is −5.40, against −7.99.
- **The constant lowers monthly MAE in every regime on both bases** (R: 5.48 / 14.62 / 9.84 → 4.82 / 13.62 / 8.36).
  It is a build candidate only after the level gap is placed, because it would also absorb part of that gap.
- **The level is not one level.** It sits in 2021 (−8.5), 2023 (−10.5) and 2025 (−15.3), with 2024 at −2.7.
  2021 and 2023 are the years gas moved fastest. A lagging gas input is the candidate, not yet an attribution.
- **Next, still item 4:** (1) the leg's inputs by year (the record's gas against the daily SAP splice, and
  carbon) in 2021, 2023 and 2025, pre-registered with the by-year biases as its control. (2) Unchanged: the
  end-year clamps on a FUELHH-basis fleet, then rerun B1-B3.

## Progress, 24 Nov (worker, item 4: the leg's inputs arm, on the record)

- **Pre-registered** in `932409f6e`, promoted before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_ON_THE_SAP_SPLICE_THE_PRICE_LEGS_POST_CRISIS_MISS_CHANGES_SIGN_THE_LEVEL_WAS_THE_PROXYS_2022_PREMIUM_2026-11-24.md`.
  Five of seven predictions held. **Nothing ships.**
- **On SAP, the leg's post-crisis miss changes sign.** On real daily x, R L0 goes from −7.99 to +4.08, and its
  MAE from 9.84 to 5.82. Pre-crisis MAE falls from 5.48 to 4.65. Crisis MAE rises from 14.62 to 18.46, with
  2022 at −17.85. 2021, 2023 and 2025 close (−1.2 / +3.3 / −1.2). That is the multiplier rising, not a lagging
  input.
- **Correction, beside the claim:** this replicates the gas-input arm `8be76e9495` (11:15) on the leg's own form.
  The shape result's "Next 1" and my pre-registration both missed it. The build-terms and shape arms' price-leg
  LEVEL conclusions were measured on the TTF proxy. These are the "about £7 low", "a level, not a shape", and
  the £5-6 constant (which goes negative on SAP). They need re-reading on SAP before any build uses them.
- **Next, still item 4:** (1) the leg on real x on SAP plus GB's real net export (`c2f65d9e9`'s term), with this
  record's SAP R L0 row as its control. (2) Build-terms B1-B3 rerun on SAP. (3) The end-year clamps on a
  FUELHH-basis fleet, unchanged.

## Progress, 24 Nov (worker, item 5: strikes AR4-AR7, read)

- **The fleet page's GAP 2 is read.** It is in §4a of `docs/market_research/the_forward_cfd_fleet_from_lccc_contract_portfolio_2026-11-24.md`,
  from LCCC's `auction-outcomes` table (569 rows, AR1-AR7), checked against the DESNZ results PDFs
  for AR4-AR7a. Nothing in `sim/` or `company/` reads any of it, and nothing changed there.
- **LCCC's strike column mixes price bases.** AR1-AR6 are in 2012 prices. AR7 carries DESNZ's 2024
  column, which is 1.3933× on every row. Read as one series, it overstates AR7 by 39%. By round, in
  2012 prices, the capacity-weighted strikes are AR4 40.74, AR6 57.98 and AR7 59.25. AR7's offshore
  wind is 65.25, against AR4's 37.35.
- **For the levy build:** the forward levy is a sum over vintages. The 2027-29 tranche's strikes
  (about £52-82 in 2024 money) sit well below AR7's (about £91). So the vintage mix can change the
  levy's sign at one world price, and averaging the strikes before the sum would hide that.
- **Still owed under item 5:** the join from an outcome row to a portfolio CFD_ID (GAP 2's
  remainder), the negative-hour rules by round (electricity page GAP 3), and the forward price
  graded first (item 4, another lane). The CPI path for indexing forward strikes is a curriculum
  input, like forward carbon.

## Progress, 24 Nov (worker, item 4: the leg on SAP plus net export, on the record)

- **Pre-registered** in `1b2731aac` and promoted to origin before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_ON_SAP_PLUS_GB_NET_EXPORT_THE_PRICE_LEG_TAKES_A_QUARTER_OFF_ITS_CRISIS_MISS_AND_ITS_POST_CRISIS_BIAS_TO_ZERO_2026-11-24.md`.
  Eight of eight predictions held. **Nothing in `sim/` changed.**
- **On the leg's own form, real net export is the term.** Adding FUELHH net export to INDO, on SAP, takes R L0 from
  4.65 / 18.46 / 5.82 to 4.62 / 13.29 / 5.99 (monthly MAE, pre / crisis / post). The post bias goes from +4.08 to
  −0.30, and 2022 from −17.85 to −8.50. W moves the same way.
- **Rule (a) fires:** the one-leg form on SAP plus net export is the leg a build would ship. It waits on the forward
  net-flow K8 section (§5) and on the DIRECTION `not_now` hold on SAP.
- **Not attributed, stated beside it:** R's 2025 goes to −7.52, while W's is −0.80, so this sits on AGWS. 2021
  goes from −1.20 to −4.21. 2022 keeps about −8.5.
- **Next, still item 4:** (1) B1-B3 rerun on SAP plus net export; (2) the §5 forward-flow K8 section; (3) R's
  2025 residual against the AGWS windows finding.

## Progress, 24 Nov (worker, item 4: K8 on a forward net-flow path)

- **The electricity page's §5a is written.** It reads NESO's FES 2025 ES1 table and the 2026 Ten Year Outlook
  (NESO Data Portal). Interconnector net flow per case: GB stays a net importer to 2028 (9-40 TWh). Every case
  turns it into a net exporter between 2030 and 2032, or close to it (2030 spread −23.8 to +8.1 TWh, about
  3.7 GW). Capacity is 10.3 GW to 2027, then 11.7 GW, then 12.9-20.6 GW by 2035. Ofgem's Window 3 and pilot-OHA
  links behind that are approved in principle only.
- **A trap, stated before use:** ES1 2025's 2024 column (4.7 TWh net import) is not DUKES's 33.4. FUELHH agrees
  with DUKES. A forward path starts from the 2025 column or splices from the record. It never differences
  against ES1's 2024.
- **FES is annual, and the leg was fitted on the half-hourly joint shape.** Flow follows the spread, so export
  happens in windy hours. The candidate build is an annual level drawn from the band (the director's
  curriculum, like forward carbon), plus the record's within-year shape conditioned on residual demand.
  Leaving the term out asserts about 3.8 GW import every year (K2). **Nothing in `sim/` changed.**
- **Next, still item 4:** (1) the annual-mean arm: refit with net export replaced by its annual mean, to say how
  much of the gain is level and how much is shape, with its prediction filed first. (2) B1-B3 rerun on SAP plus
  net export. (3) R's 2025 residual against the AGWS windows finding.

## Progress, 24 Nov (worker, item 4: the annual-mean arm, on the record)

- **Pre-registered** in `1545ed8b0` and promoted to origin before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_THE_ANNUAL_NET_EXPORT_LEVEL_CARRIES_ALL_OF_2022S_BIAS_BUT_ONLY_HALF_THE_CRISIS_GAIN_2026-11-24.md`.
  Six of eight predictions held. **Nothing in `sim/` changed.**
- **Each year's mean net export, in place of the half-hourly series,** takes R L0's crisis MAE from 18.46 to 16.16,
  not to ne's 13.29. That is a level share of 44% (W: 50%). The predicted share was at least two-thirds, and both
  misses stay beside the outcomes. 2022's bias (−8.43), the post-crisis bias (−0.91) and 2025's bias (−7.64) match
  ne's to within £0.7. The level carries the bias, and the shape carries the crisis spread.
- **Rule (b) fires:** a forward build needs the FES annual level plus a within-year shape. Not predicted: outside
  the crisis the level alone beats the real shape (R pre 4.45 against 4.62, post 5.58 against 5.99).
- **Next, still item 4:** (1) the month-mean arm, to say whether the crisis shape is seasonal (month-level) or
  day-level; (2) B1-B3 on SAP plus net export; (3) R's 2025 residual against the AGWS windows finding.

## Progress, 24 Nov (worker, item 4: the net-export timescale arm, on the record)

- **Pre-registered** in `5a4be139d` and promoted to origin before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_THE_NET_EXPORT_SHAPE_THE_PRICE_LEG_NEEDS_IN_THE_CRISIS_IS_SEASONAL_AND_IT_IS_2022S_SUMMER_OF_EXPORT_2026-11-24.md`.
  Nine of nine predictions held. **Nothing in `sim/` changed.**
- **The £2.87 crisis gain the annual level leaves is seasonal.** With net export as a day mean, R L0's crisis MAE is
  13.30, and as a month mean 13.53, against ne's 13.29 and am's 16.16. Within the day the part is £0.01, day to
  day £0.23, and month to month £2.63 (92%; W 86%). The biases match ne in every arm.
- **The season is one event.** GB exported 1.3-3.0 GW from April to November 2022. In every other month of the
  record it imported, apart from one. Outside the crisis the monthly profile makes the leg worse (R post 5.58
  under am against 6.16 under mm). This was seen after the run and is not yet attributed.
- **For forward years:** the forward net-flow term is the FES annual level alone. Every forward figure states that a
  2022-type neighbour shortfall (about £2.6/MWh of crisis monthly MAE here) is outside it, until a mechanism prices
  a neighbour's shortfall.
- **Next, still item 4:** (1) a leave-one-year-out monthly climatology, rule (a)'s arm. It is predicted in the result
  record to carry under a quarter of the £2.63. (2) B1-B3 on SAP plus net export. (3) R's 2025 residual against the
  AGWS windows finding.

## Progress, 24 Nov (worker, item 4: the leave-one-year-out profile arm, on the record)

- **Pre-registered** in `7f08d5309` and promoted to origin before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_A_NET_EXPORT_PROFILE_LEARNT_FROM_OTHER_YEARS_CARRIES_NONE_OF_THE_CRISIS_SHAPE_2026-11-24.md`.
  Five of six predictions held. **Nothing in `sim/` changed.**
- **A profile from the other years carries none of the crisis shape.** Each year's mean plus a leave-one-year-out
  monthly profile gives R L0 a crisis MAE of 16.21, against 16.16 for the annual level alone and 13.53 for the
  year's own months (W: 15.43, 15.32, 13.15). Rule (a) fires: the crisis shape is 2022's event, not a GB season.
- **Wrong, kept beside it:** CL-P2 predicted that the profile would cost pre-crisis accuracy. It helps instead
  (R 4.45 → 4.32). Post-crisis it costs R £0.37 ex-2025. This is not attributed.
- **For forward years:** the net-flow term is the FES annual level alone. Every forward figure states that a
  2022-type neighbour shortfall (about £2.6/MWh of crisis monthly MAE on R) is outside it.
- **Next, still item 4:** (1) B1-B3 on SAP plus net export; (2) R's 2025 residual against the AGWS windows
  finding; (3) a K8 section on the neighbour-shortfall mechanism (French nuclear availability as GB export
  demand), before any build of it.

**Also, the land10 reader (lane 0), 24 Nov ~18:55Z:** `/var/tmp/se-msc-land10-ended.txt` had been written by the
EXIT trap of the land10 instance that was stopped for the 18:48Z re-arm. It was not an outcome, but it fired
the file hold on `land10-outcome-is-read-and-msc-lands-or-is-re-cut`. It was moved aside to
`/var/tmp/se-msc-land10-ended.rearm-2026-11-24T1848Z.txt` (reverse: move it back), and the note is in
`land10.log`. The live land10 waits on rankq's pid 1718490. A re-arm that writes the end file through its trap
will re-fire the hold, so the next re-arm should move the file aside itself.

## Progress, 24 Nov (worker, item 4: the build terms rerun on SAP plus the annual net-export level)

- **Pre-registered** in `df7cd4297` and pushed to origin before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_ON_SAP_PLUS_THE_ANNUAL_NET_EXPORT_LEVEL_DEMAND_BY_YEAR_AND_SOLAR_OUT_THE_CHAIN_BEATS_THE_GAS_ONLY_NULL_IN_EVERY_REGIME_2026-11-24.md`.
  Five of eight predictions held. **Nothing in `sim/` changed.**
- **On the form a build would ship, the chain beats the gas-only null on SAP in every regime at the month.** That
  form is SAP, the annual net-export level, demand by year, and solar out. Monthly MAE is 4.22 / 16.81 / 6.18,
  against null_S's 4.97 / 17.44 / 9.84 and the shipped chain's 6.50 / 17.20 / 8.19. Against null_T it loses only
  post-crisis without 2025 (5.47 against 4.81). Rule (a) fires. FUELHH wind is worse than AGWS here.
- **Stated plainly:** on the record, the demand and net-flow year levels are each year's own real level. A forward
  figure adds the error of the published path it takes them from. The quarter was not measured.
- **Not built.** The build waits on the DIRECTION `not_now` hold on SAP, a forward demand path (§8a), and the FES
  net-flow level (§5). **Next, still item 4:** pre-register a forward year's demand level from FES system demand.
  Then the neighbour-shortfall K8 section, and R's 2025 residual.

## Progress, 24 Nov (worker, what the build still waits on, re-read against the tree)

- **Correction, beside the claim.** Five records, the last being the build-terms result above, say the build waits
  on "the DIRECTION `not_now` hold on SAP". That hold is gone. The `not_now` row left DIRECTION.yaml at `7852dd77ff`
  (18 Nov 18:53). Its condition, skip1 and skip0 read, was met on 19 Nov (`a2c848965`, `9a361e3562`). The continuation
  that carried the world's switch to SAP, `world-gas-baseline-switch-readers-to-spliced-sap`, expired untaken. So the
  18 Nov decision to splice is unowned, and the switch-order census of 24 Nov leaves it out. Filed:
  `docs/staging/WORKER_FINDING_THE_SAP_SPLICE_WAS_DECIDED_ITS_HOLD_LAPSED_ON_19_NOV_AND_NO_QUEUE_CARRIES_THE_SWITCH_2026-11-24.md`.
- **What that changes for item 4.** On record years, the shippable form (SAP, the annual net-export level, demand by
  year, solar out) uses each year's real levels, so no forward band blocks it. It waits on one thing only: the world's
  gas readers moving to SAP in the same change. Moving the chain alone would price it on a gas record the world does
  not settle on. That change is ordered by the switch order (one change per book), not by this finding.
- **What forward years wait on, by name.** `docs/design/curriculum/forward_years.json` (ruled 25 Oct) carries two
  bands, gas level and renewable fleet. It carries no band for the three other levels the shippable form needs:
  (1) transmission demand (ND), sourced in electricity page §8a, where the record supports ND held at its 2023-25
  level, jointly with the fleet band; (2) the interconnector net-flow level, sourced in §5a from FES 2025 ES1, a 2030
  spread of −23.8 to +8.1 TWh; (3) carbon. Carbon has no sourced forward band: the page names forward carbon as
  the curriculum's and cites no path. Item 5's forward levy also needs the CfD fleet. Its band is the renewable fleet
  band, so it shares one capacity path (fleet page).
- **Next, still items 4-5:** K8 first on a forward UK carbon band (UK ETS cap and auction path, DESNZ traded carbon
  values, CPS policy). Then one `for_the_director` row that proposes all three missing bands for `forward_years.json`,
  with a recommendation for each. Asking before carbon is sourced would hand him an unsourced number.

## Progress, 24 Nov (worker, K8 on forward carbon)

- **§2a of the electricity page sources the band.** It is DESNZ's *Traded carbon values used for modelling
  purposes, 2025* (3 Feb 2026, OGL), £/tCO2e real 2025. For 2030, Low / Central / High is 25 / 50 / 66; for 2035,
  45 / 70 / 92. The Market column is 44 in 2025, against the record's 2025 auction VWAP of £48.05. The band models
  the standalone UK ETS and excludes UK-EU linking.
- **Carbon Price Support (CPS) is not in the band.** It is £18 to 31 Mar 2028, and a GAP after that.
- **Found:** DESNZ's Low carbon case is its high-fossil-price case. Drawing carbon independently of the gas band
  would produce futures DESNZ does not model. That pairing is the director's.
- **Next:** one `for_the_director` row proposing the three missing `forward_years.json` bands (ND, net flow,
  carbon), with a recommendation for each.

## Progress, 24 Nov (worker, item 4: K8 on the neighbour shortfall)

- **Electricity page §5b** defines a neighbour shortfall (GB's monthly net flow with France at or below zero),
  measures it on the world's own FUELHH cache (annual totals reconcile with DUKES 5.13 to within 0.6 TWh), and
  counts 16 of 120 months in five runs: Oct 2016-Jan 2017, Nov 2017, Jul 2020, Nov-Dec 2021 and Apr-Nov 2022.
  Two are dated to the French nuclear fleet (the 2016 Le Creusot checks; 2022's 279 TWh at 54% availability,
  RTE). Nov 2017 and Jul 2020 are counted and not attributed. **Nothing in `sim/` changed.**
- **For forward years.** The FES annual level cannot carry an event, and leaving it out asserts none in any year
  (K2) where the record shows runs in five of ten. The page names three ways to carry it and builds none. Whether
  forward years draw such an event is the director's curriculum, beside the bands in row
  `the-forward-world-has-bands-for-gas`.
- **Next, still item 4:** (1) read the chain's pre-crisis residual in Oct 2016-Jan 2017 for the event (page GAP
  13c), with a prediction filed first; (2) R's 2025 residual against the AGWS windows finding. The record-years
  build is carried by the SAP splice finding, and its placement in the switch order is the seat's.

## Progress, 24 Nov (worker, item 4: GAP 13c, the pre-crisis shortfall runs on the record)

- **Pre-registered** in `b981dbbcf` and pushed to origin before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_THE_PRE_CRISIS_FRANCE_SHORTFALL_RUNS_PRICED_AGAINST_SAP_AND_NET_EXPORT_CARRIES_39_PERCENT_2026-11-24.md`.
  Five of seven predictions held. **Nothing in `sim/` changed.**
- **Two of the three pre-crisis runs priced.** Record SSP over the floor was 1.48 against 1.11 in Oct 2016-Jan 2017,
  and 1.19 against 1.11 in Jul 2020. Nov 2017 did not price. C3 (the shippable form) runs £5.24 low in the six months
  against its own calendar months, and Nov 2016 alone is −£22.7.
- **Rule (c) fires.** Each month's own net export takes out 39% of the gap, not half. The rest is not attributed.
  §5b's GAP 13c is updated. For the director row: the record shows a neighbour shortfall pricing in 2016, 2020 and
  2022, not only 2022.
- **Next, still item 4:** R's 2025 residual against the AGWS windows finding. The record-years build is carried by
  the SAP splice finding.

## Progress, 24 Nov (worker, item 4: 2025's residual against the AGWS windows)

- **Pre-registered** in `42ec42e7c`, promoted before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_THE_CHAINS_2025_MISS_IS_MOSTLY_THE_BASIS_OF_THE_FLEET_IT_IS_CLAMPED_TO_2026-11-24.md`.
  Seven of seven predictions held. **Nothing in `sim/` changed.**
- **2025's +3.27 GW gas-running miss was mostly a basis mismatch.** W1 scaled 2025 by 2025's FUELHH ÷ AGWS ratio
  (0.812), but 2025's wind is 2024's clamped fleet on 2024's basis (1.221). Carrying the fleet's own basis takes
  2025 to +1.40 GW, and the post-crisis gas-running miss to +0.29 GW (composite bias 8.29 → 7.04). Build rule: a
  clamped year inherits its source year's fleet and its basis together. The remaining +1.4 GW is wind level
  (the calm-year curve and fleet growth after 2024). It stays beside 2025's number until a 2025 fleet exists
  outside AGWS.
- **With 2025's gas running set right, its price miss is the price leg's** (+6.27, against +5.83 in 2023-24). Step B's
  unattributed 2025 candidate is closed.
- **Next, still item 4:** the price-leg shape arm on low-gas days (§1b), now the largest post-crisis term in every
  year. The shippable record-years build, with this rule in it, is carried by the SAP splice finding.

## Progress, 24 Nov (worker, item 4: the price leg's low-gas shape on SAP, on the record)

- **Pre-registered** in `1df5c3237` and pushed to origin before the run. **Result** in
  `docs/staging/records/WORKER_RESULT_A_LOW_GAS_HINGE_LEARNT_BEFORE_THE_CRISIS_TAKES_60_PERCENT_OF_THE_PRICE_LEGS_POST_CRISIS_MISS_ON_SAP_2026-11-24.md`.
  Eight of eight predictions held. They were informed by §1b's table, and the record says so. **Nothing in `sim/` changed.**
- **The low-gas depth is a stable multiple of the floor, learnable before the crisis.** One hinge below 6 GW
  of CCGT (about −0.10 of the floor per GW) is fitted on pre-crisis days only. On real gas running it takes leg P's
  post-crisis bias from +6.16 to +2.44, and MAE from 6.97 to 4.89. Pre-crisis MAE moves by £0.01. Its coefficient is
  −0.096 to −0.109 with any one year left out. Rule (a) fires, so it is a build term.
- **Costs and what is left.** The crisis bias goes from −1.78 to −3.14. The post-crisis remainder sits at the top: on
  107 days above 14 GW the leg prices at 1.27 of the floor, where the record clears at 1.17. On the chain's own gas
  running, the composite post bias goes from +7.04 to +3.63 (+1.57 without 2025), but MAE barely moves.
- **Next, still item 4:** (1) the post-crisis top above 14 GW, pre-registered first. (2) The shippable record-years
  build now carries the hinge too. It is carried by the SAP splice finding.
