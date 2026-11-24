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
