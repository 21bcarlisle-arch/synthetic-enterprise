**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_6_physics_price_signal`

# World models built to their ceiling with no mechanism page beneath them

Found by the delivery seat, 24 Nov 2026, for item 6 of
`docs/staging/WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`
(the 05:40 addendum to the signed steer `452de5285`: "Find any other world model in the same state").
The learning-loop row is in `docs/institutional/ways_of_working.md` W5, dated 24 Nov, class "no
mechanism".

## Two corrections to the premise, beside it

- **"Taken to L4."** The map has `W1_6_physics_price_signal` closed at level 3, target 3. The module's
  docstring says "L4" (`sim/weather_price_chain.py:1`, `:299`). The class is the same: built to its
  ceiling. The docstring overstates the level; that is a one-line correction for the rebuild.
- **"Mention interconnectors 0 times, CfDs 0 times and the merit order 0 times."** Counted on
  24 Nov across the five wholesale feeds (`knowledge_wholesale.json`, `knowledge_gas_wholesale.json`,
  `knowledge_merit_order_residual_demand.json`, `knowledge_gb_electricity_market.json`,
  `knowledge_carbon_price.json`): interconnector 6 mentions, CfD 4, merit order 12. They are passing
  mentions. None explains a mechanism or gives a size, so the advisor's point stands: there is no
  page beneath the chain.

## How the census was taken, and what it cannot see

World models are atoms whose lane starts `W` or whose `file_scope` is in `sim/` or `simulation/`.
None is at level 4 on the live or closed map; 36 are at level 3. For each, the census looked for a
Knowledge topic naming the atom (`topics[].atoms`) and for any `docs/market_research/` page naming it.

**What it cannot see.** A page that names an atom need not explain its mechanism. W1_6 is named by
two topics and three market-research pages, and still has no price-formation page. So the
mechanical census finds only the atoms with nothing at all. Whether a NAMED page carries the
mechanism needs a reading. It was done below only for the price and market models, because those
are the ones forward years will price from.

## Result

**Price and market models, read:**

| Atom | Level | What models it | Mechanism page? |
|---|---|---|---|
| `W1_6_physics_price_signal` | 3 (closed) | `sim/weather_price_chain.py`, `sim/price_engine.py` | **No.** Named by `how-gb-gas-and-power-prices-move` (volatility only) and `electricity-wholesale` (marginal-plant claim, no interconnector, CfD, nuclear or carbon mechanism). |
| `W1_2_generate_futures` | 2 (closed) | `sim/scenario/gas_scenario_generator.py` (the forward gas draw) | **No** until today. The gas page (`how_the_gb_gas_price_forms_nbp_and_sap_2026-11-24.md`) is now beneath it; the generator has none of its mechanisms (see the gas grade). |
| `W1_6b_merit_order_reconstruction` | 2 | `sim/merit_order_reconstruction.py` | **Thin.** `merit-order-residual-demand` explains the stack. It does not cover interconnectors, CfD/RO bidding or nuclear availability. That is the electricity page, the next item. |
| `SPINE_3_gas_storage_crisis_regime` | 0 | not built | Now has the gas page (§4, §7) before any build. That is the K8 order. |

**Level-3 world models with no topic and no market-research page at all** (mechanical; each is a
candidate, not yet read):

- `W1_3_national_weather_signal`, `W1_4_regional_weather_field`: the weather generators. The
  `weather-cells` page may cover them in substance without naming them.
- `G14_half_hourly_grid_carbon_intensity_aligned_to_settlement` (`sim/grid_carbon_history.py`):
  grid carbon intensity. Its mechanism (generation mix, interconnector imports) is the electricity
  page's subject too.
- `W2_1_archetype_layers` (`simulation/household_segments.py`), `CA1_cohort_assignment_live`,
  `CA2_coverage_report_realised_cohort`, `W2_10_dd_attribution_confound`,
  `W2_11_payment_behaviour_source`, `C3_satisfaction_heterogeneity` (`simulation/sim_satisfaction.py`):
  household generators. Several have staging records but no Knowledge page.

## What would close this

The two price rows close with the gas page (landed 24 Nov) and the electricity page (the next
item). Each mechanical candidate needs one read: either name the page that carries its mechanism
in its topic's `atoms`, or file the missing page as a K8 item before that model is next changed.
The proposal for the class: a world model's level may not move above 2 without a Knowledge topic
naming it whose body states the mechanism. That is a rule change and goes to the weekly review,
not into a gate here.
