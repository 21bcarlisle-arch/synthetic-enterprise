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
