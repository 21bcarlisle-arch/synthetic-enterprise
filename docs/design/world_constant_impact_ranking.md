# World constants in impact order

Direction item `anchor-the-446-bare-world-constants-in-impact-order` (director's reading 19 Oct 16:28,
relayed in `docs/staging/advisor/done/DIRECTOR_READING_USAGE_5PCT_MONDAY_PM_2026-10-19.md`). The
register (`world_constant_anchor_register.txt`) is the exact set of constants not yet anchored. This
page gives the order in which to anchor them. Pre-registration:
`docs/staging/records/SEAT_PREREG_WHICH_BARE_WORLD_CONSTANTS_THE_PRODUCTION_RUN_READS_2026-10-19.md`.

## What "impact" means here

Two instruments, each named for what it can and cannot see.

1. **The book draw** (measured, 19 Oct). `live_population()` was traced with `sys.monitoring`. A
   registered constant counts as *read by the draw* when a line that loads it ran. That held for 65
   of 446, plus 20 that were derived at import or used only as a default argument. Each
   read constant was then moved one at a time, in a fresh process, through three arms: x0.8, x1.2,
   and a +/-20% alternating tilt (renormalised wherever the original summed to 1, so that shares stay
   shares). The 773-record book was redrawn each time and compared with the seed's own draw, which is
   byte-deterministic. **Impact** is the largest move across the book's aggregates: total variation
   of each categorical share (region, home type, EPC, fuel, band, tariff, payment, smart, acquisition
   year), and the relative change in mean `eac_kwh`, `aq_kwh`, `cv_factor` and `cf`.
   `location.output_area` is excluded. With 438 levels it reads about 0.15-0.35 under ANY reshuffle,
   so it measures that the draw re-sequenced, not how far it moved.
2. **The production run** (owed, launched 19 Oct ~18:10, about 95 min): the same line trace over
   `tools.run_annual_report`, the entry `background/sim_runner.py` launches. It sorts the other
   ~380 into READ / NOT READ by the run. A constant the run never reads can move no published figure,
   so it ranks last whatever it is.

### What the book-draw instrument cannot see

The book is **saas-shaped**: it is what the company is handed, and it carries no ground truth. A
constant that shapes the world's own household (its true consumption from `fabric_physics`, its
cars, its NS-SEC) moves nothing visible here. The zeros below therefore mean "does not move the
company-visible book". They do not mean "moves nothing". The `fabric_physics` U-values register
only as a re-shuffle of which region is drawn, because their real effect is on settled consumption,
which only the production run shows. Ranking those is the run's job, not this table's.

## The book-draw ranking

| # | constant | impact | what moved most | status |
|---|---|---|---|---|
| 1 | `simulation/live_population.py::GAS_CV_FACTOR` | 0.198 | mean:cv_factor | anchored |
| 2 | `simulation/live_population.py::GAS_CORRECTION_FACTOR` | 0.198 | mean:cf | anchored |
| 3 | `simulation/population_draw.py::DEFAULT_BAND_WEIGHTS` | 0.080 | share:consumption_band | anchored |
| 4 | `simulation/arrival_route.py::EHS_HOUSEHOLDS_BY_TENURE_MILLIONS` | 0.065 | share:tariff_type | anchored |
| 5 | `simulation/live_population.py::_FOUNDER_DRAW_HEADROOM` | 0.056 | share:location.region | open |
| 6 | `simulation/fabric_physics.py::_WALL_U_BY_ERA` | 0.050 | share:location.region | open |
| 7 | `simulation/acquisition_funnel.py::CREDIT_CHECK_TO_ONBOARDING` | 0.050 | share:location.region | open |
| 8 | `simulation/fabric_physics.py::_INSULATION_U_MULTIPLIER` | 0.050 | share:location.region | open |
| 9 | `simulation/fabric_physics.py::_WINDOW_U_BY_ERA` | 0.049 | share:location.region | open |
| 10 | `simulation/fabric_physics.py::_WINDOW_AREA_RATIO` | 0.048 | share:location.region | open |
| 11 | `simulation/premise_population.py::PUBLISHED_EPC_BAND_SHARE` | 0.047 | share:location.region | anchored |
| 12 | `simulation/fabric_physics.py::_WALL_AREA_RATIO` | 0.046 | share:location.region | open |
| 13 | `simulation/fabric_physics.py::_ROOF_U_BY_ERA` | 0.045 | share:location.region | open |
| 14 | `simulation/fabric_physics.py::_ROOF_U_FLOOR` | 0.043 | share:location.region | open |
| 15 | `simulation/premise_population.py::_SMART_SHARE_2024` | 0.043 | share:smart_meter | anchored |
| 16 | `simulation/acquisition_funnel.py::ONBOARDING_TO_COOLING_OFF_SURVIVAL` | 0.043 | share:location.region | open |
| 17 | `simulation/arrival_route.py::EHS_MOVES_INTO_TENURE_MILLIONS` | 0.042 | share:tariff_type | anchored |
| 18 | `simulation/acquisition_funnel.py::QUOTE_TO_APPLICATION` | 0.042 | share:location.region | open |
| 19 | `simulation/fabric_physics.py::_EXPOSED_ENVELOPE_FRACTION` | 0.042 | share:location.region | open |
| 20 | `simulation/fabric_physics.py::_WALL_U_FLOOR` | 0.040 | share:location.region | open |
| 21 | `simulation/acquisition_funnel.py::STAGE_COST_SHARE` | 0.040 | share:location.region | open |
| 22 | `simulation/fabric_physics.py::_FLOOR_AREA_PER_BEDROOM_M2` | 0.035 | share:location.region | open |
| 23 | `simulation/population_draw.py::_KNUTH_EXACT_LAMBDA_CEILING` | 0.028 | share:consumption_band | open |
| 24 | `simulation/fabric_physics.py::_INFILTRATION_ACH_BY_ERA` | 0.027 | share:acquisition_date | open |
| 25 | `simulation/fabric_physics.py::_GROUND_U_BY_ERA` | 0.027 | share:consumption_band | open |
| 26 | `simulation/household_segments.py::TENURE_POPULATION_SHARE` | 0.014 | share:tariff_type | open |
| 27 | `simulation/population_draw.py::DD_SHARE_GAS` | 0.003 | share:payment_method | open |
| 28 | `simulation/sme_payment_behaviour.py::_LATE_RELATIVE_BY_TIER` | 0.000 | -- | open |
| 29 | `simulation/sme_payment_behaviour.py::SME_TARGET_LATE_RATE` | 0.000 | -- | open |
| 30 | `simulation/sme_payment_behaviour.py::SME_DISPUTE_PROB` | 0.000 | -- | open |
| 31 | `simulation/sme_payment_behaviour.py::SME_BEHIND_FAILURE_RATE` | 0.000 | -- | open |
| 32 | `simulation/premise_population.py::_STORAGE_SHARE_OF_ELECTRIC` | 0.000 | -- | open |
| 33 | `simulation/premise_population.py::_SMART_COMMUNICATING_RATE` | 0.000 | -- | open |
| 34 | `simulation/premise_population.py::_MONTHLY_SHARE_OF_TRADITIONAL` | 0.000 | -- | open |
| 35 | `simulation/premise_population.py::_HEAT_PUMP_SHARE` | 0.000 | -- | open |
| 36 | `simulation/premise_population.py::_GAS_FIRED_SHARE` | 0.000 | -- | open |
| 37 | `simulation/premise_population.py::_ELECTRIC_HEAT_SHARE` | 0.000 | -- | open |
| 38 | `simulation/premise_population.py::_COMBI_SHARE_OF_GAS` | 0.000 | -- | open |
| 39 | `simulation/premise_population.py::_BEDROOM_WEIGHTS_BY_PROPERTY_TYPE` | 0.000 | -- | open |
| 40 | `simulation/premise_population.py::MAX_PUBLISHED_ROUNDING_SLACK` | 0.000 | -- | open |
| 41 | `simulation/premise_population.py::INHERITED_DOMESTIC_PV_KWP` | 0.000 | -- | open |
| 42 | `simulation/population_draw.py::_NSSEC_TILT_BY_TENURE` | 0.000 | -- | open |
| 43 | `simulation/population_draw.py::_NSSEC_NATIONAL` | 0.000 | -- | open |
| 44 | `simulation/population_draw.py::_HEATING_FUEL_TILT_BY_REGION` | 0.000 | -- | open |
| 45 | `simulation/population_draw.py::_HEATING_FUEL_NATIONAL` | 0.000 | -- | open |
| 46 | `simulation/population_draw.py::_CARS_TILT_BY_TENURE` | 0.000 | -- | open |
| 47 | `simulation/population_draw.py::_CARS_NATIONAL` | 0.000 | -- | open |
| 48 | `simulation/population_draw.py::_ACCOMMODATION_TILT_BY_TENURE` | 0.000 | -- | open |
| 49 | `simulation/population_draw.py::_ACCOMMODATION_NATIONAL` | 0.000 | -- | open |
| 50 | `simulation/net_new_acquisition.py::ELECTRICITY_ONLY` | 0.000 | -- | open |
| 51 | `simulation/fabric_physics.py::_STOREY_HEIGHT_M` | 0.000 | -- | open |
| 52 | `simulation/fabric_physics.py::_SOLAR_TRANSMITTANCE` | 0.000 | -- | open |
| 53 | `simulation/fabric_physics.py::_OVERSIZE_FACTOR` | 0.000 | -- | open |
| 54 | `simulation/fabric_physics.py::_MODULATION_MIN_FRACTION` | 0.000 | -- | open |
| 55 | `simulation/fabric_physics.py::_MINIMUM_VENTILATION_ACH` | 0.000 | -- | open |
| 56 | `simulation/fabric_physics.py::_MASS_CAPACITY_KJ_PER_M2K` | 0.000 | -- | open |
| 57 | `simulation/fabric_physics.py::_INTERNAL_TEMPERATURE_BY_EPC_C` | 0.000 | -- | open |
| 58 | `simulation/fabric_physics.py::_INTERNAL_SURFACE_H_W_PER_M2K` | 0.000 | -- | open |
| 59 | `simulation/fabric_physics.py::_INTERNAL_SURFACE_AREA_RATIO` | 0.000 | -- | open |
| 60 | `simulation/fabric_physics.py::_INTERNAL_GAIN_W_PER_M2` | 0.000 | -- | open |
| 61 | `simulation/fabric_physics.py::_GROUND_U_FLOOR` | 0.000 | -- | open |
| 62 | `simulation/fabric_physics.py::_FRAME_FACTOR` | 0.000 | -- | open |
| 63 | `simulation/fabric_physics.py::_AIR_CAPACITY_KJ_PER_M2K` | 0.000 | -- | open |
| 64 | `simulation/customer_events.py::PRICE_DIFFERENTIAL_PCT` | 0.000 | -- | open |

Not perturbed (derived at import, or used only as a default argument, so `setattr` cannot reach the
value the draw uses): `_ELEC_FALLBACK`, `_GAS_FALLBACK`, `WORLD_MAX_CHURN_PROBABILITY`, `DAYTIME_SHAPE_BIAS_TOL`, `EFUS_DAYTIME_RATE_ALL_HOUSEHOLDS`, `EFUS_DAYTIME_RATE_ALL_UNEMPLOYED`, `EFUS_DAYTIME_RATE_NO_PENSIONER`, `EFUS_DAYTIME_RATE_PENSIONER_PRESENT`, `EFUS_DAYTIME_RATE_SOMEONE_EMPLOYED`, `SOLAR_KWP`, `VOLUME_FACTOR_BIAS_TOL`, `DEFAULT_DEADBAND_C`, `STORAGE_HEATER_HIGH_RATE_FRACTION`, `_MAX_RATE`, `_POST_BAN_STRUCTURAL_FACTOR`, `HARD_TO_READ_MONTHLY_READ_RATE`, `TRADITIONAL_DELAY_MEAN_DAYS`, `DEFAULT_ACQUISITIONS_PER_YEAR_LAMBDA`, `_POST_1990_PUBLISHED_SHARE`, `_SHARE_OF_POST_1990_BUILT_IN_THE_1990S`.

`PUBLISHED_EPC_BAND_SHARE` takes only the tilt arm, because x0.8 and x1.2 are refused at the door:
"published marginal ... sums to 1.2012 ... a wrong share, not a rounded one". That is correct.

## Read this way

- **`GAS_CV_FACTOR`, `GAS_CORRECTION_FACTOR`** move every gas kWh one for one, which is the largest
  real effect a single constant has on the drawn book. CF is statutory. CV is a daily LDZ value and
  is now an EVIDENCE RANGE with a named GAP.
- **`DEFAULT_BAND_WEIGHTS`**: a 20% tilt moves the book's band mix by 8 points. Ofgem cites the band
  locations (TDCV = lower quartile / median / upper quartile). Nothing publishes the weights.
- **The EHS tenure tables, `PUBLISHED_EPC_BAND_SHARE` and `_SMART_SHARE_2024`** were already sourced.
  The scan read them as bare. See
  `docs/staging/SEAT_FINDING_THE_WORLD_ANCHOR_SCAN_READS_SOURCED_CONSTANTS_AS_BARE_BECAUSE_ITS_PUBLISHER_LIST_IS_THE_COMPANYS_2026-10-19.md`.
- **A move read only as `share:location.region` at 0.04-0.06 cannot yet be told from a reshuffle.**
  Fourteen of the top 25 move nothing else, and no placebo arm (a re-seeded draw with every constant
  at its value) was run, so their order among themselves is not established. *(Correction added by
  the next seat on the same claim, 19 Oct 21:30.)*
- **`_FOUNDER_DRAW_HEADROOM`, `_KNUTH_EXACT_LAMBDA_CEILING` and the three acquisition-funnel rates**
  move the book's region mix by 3-6 points. That is through which homes are drawn, not what any home
  is. They are machine and curriculum quantities as much as world facts, and come next.

## Also anchored on this claim (comments only, no value moves)

`sim/gas_prices_history.py::MWH_PER_MMBTU` (NIST SP 811), `sim/weather_hdd.py::HDD_BASE_TEMP_C` and
`simulation/demand_model.py::HEATING_BASE_TEMP_C` (the DESNZ Energy Trends section 7 base of 15.5 C).
Unit and convention constants, not ranked: anchoring them takes one line each.

## The production-run screen (next increment)

The book draw cannot see settled consumption or money. `tools/world_constant_reach.py --arm` scales
every reached bare constant in one module by 1.1 and reruns the short window, read against the
published figures (`total_gross`, `total_bad_debt`, churn, summed kWh). Pre-registered (P6-P9) in
`docs/staging/records/SEAT_PREREG_WHICH_OF_THE_446_BARE_WORLD_CONSTANTS_A_PRODUCTION_RUN_READS_2026-10-19.md`.
Its ranking replaces this table's order for everything outside the book draw.
