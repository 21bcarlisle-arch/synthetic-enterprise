**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `G14_half_hourly_grid_carbon_intensity_aligned_to_settlement` · **Claim:** `g14-l3-explain-neso-2020-step-and-take-expert-hour`

# What NESO's 2020-04-28 level step in G14's carbon series is

At draw time the duplicate-work note named this same id as already held. The only holder was this
invocation: `ps` showed no rival seat and no `surgical_land` on G14. The note was the draw's own write.

## Pre-registration (written 2026-10-05 before any measurement in this turn)

The step is in the RATIO of NESO's published `actual` to our fuel-mix arithmetic. Both are computed
over the same half hour's outturn. So **a real fleet change cannot make the ratio step**, because it
moves both sides. "Real fleet change" is refuted by construction unless one of our own inputs changed
on that date (FUELHH coverage, or NESO's embedded estimate). The live candidates:

- **H1. NESO revised one or more generation factors.** Predicted signature: after the step, the
  ratio change scales with the share of the revised fuel. Regressing published × total MW on per-fuel
  MW before and after shows one or two implied factors moving, and the rest holding.
- **H2. NESO changed its denominator or its embedded/consumption basis.** Predicted signature: a
  near-uniform multiplicative drop. Any dependence runs with embedded wind and solar share, not with
  fossil share.
- **H3. One of our inputs changed on that date.** Predicted signature: a discontinuity in a FUELHH
  fuel or embedded series at 2020-04-28 by itself.

Prediction before running: **H1**, with the gas (CCGT) implied factor falling. I hold this weakly,
because a ~10% drop with gas near 40% of the mix needs a large gas revision. If the implied factors
all fall together, H1 is refuted in favour of H2.

## Result: a methodology change in the API's live calculation. My prediction (H1) was wrong.

- **The step is one half hour: 2020-04-27, P33 → P34.** The API actual goes 210 → 195 g while CCGT
  rises 860 MW and the arithmetic rises 191 → 198 g. Embedded generation, FUELHH and imports are
  smooth across it. **H3 refuted.**
- **H1 (a factor revision, gas) refuted.** On a year either side, the implied factors are CCGT
  430 → 400, coal 1,066 → 984 and biomass 165 → 122, against the table's 394 / 937 / 120. Every
  well-identified factor is 9-14% high before the step, which is a uniform multiplier. The gas-only
  prediction is kept here as written.
- **H2 in its "embedded left out" form refuted.** Dropping embedded fits the pre-step API worse
  (SD 0.076 → 0.083, slope on embedded share +0.35 → -0.84).
- **The deciding reading.** NESO's Open Data Portal *Historic GB Generation Mix* (`df_fuel_ckan.csv`,
  half-hourly from 2009) has its own `CARBON_INTENSITY`, and it is continuous across the cut. Over
  28 days either side, historic-mix/arithmetic goes 0.961 → 0.959 and API/historic-mix goes
  1.151 → 1.048. A placebo cut on 2019-04-27 moves neither (0.978 → 0.970, 1.130 → 1.125).
- **The mechanism is likely and not established.** NESO's methodology says the API is "corrected to
  account for transmission losses", the one uniform multiplier of this size. NESO's FOI/25/152 says
  it holds no historical series of that multiplier. The classification stands without it.

## What it means for G14, and the next item

The shipped series changes basis at 2020-04-27 P34. 2018-05 to 2020-04 and the pre-2018 estimate,
whose scale of 1.1287 was fitted to join it, sit about 11% above the rest. So part of the published
2019 → 2021 decline is the calculation and not the fleet. The 2018-2020 rows of the weather fit's
per-year table carry the same share. The futures fit (2024-25 window) does not.

**Recommendation, handed on as the next item:** rebase G14's whole history onto NESO's Historic GB
Generation Mix `CARBON_INTENSITY`. It is one publisher on one basis from 2009, and after the step it
agrees with the API within 1-3%. That removes the fitted scale and the pre-2018 estimate. The API
stays as the cross-check. This is within the director's own words ("take the published series ...
if it doesn't cover 2016, fill the gap"): a published NESO series covers 2016. The fuel-mix
arithmetic stays as the fill for half hours the historic mix lacks.

Recorded in `docs/market_research/g14_grid_carbon_history_and_weather_fitted_future_2026-10-05.md`
§"The 2020-04-27 step" and in `sim/grid_carbon_history.py` finding 3.

## Expert Hour, taken after the step was explained: FAIL (2 MAJOR, 6 MINOR)

This was a fresh-context cold-eyes pass: a veteran GB grid-carbon analyst persona, with priors written
before reading. It is recorded on the map row and in `trust_ledger.json` as `needs_work`.

- **MAJOR-1, which this finding had not drawn: since the step the series is GENERATION basis, but
  five labels say it is loss-corrected.** After 2020-04-27 P34 the API actual is 0.97× the
  generation-only arithmetic (2021-25 mean, measured above), with its implied factors on NESO's
  table. A loss correction would put it near 1.08×. The pre-step ×1.10-1.14 is the loss correction,
  and the step is where it stopped. Five labels still say "loss-corrected … no further loss
  adjustment": `sim/neso_carbon_intensity.PUBLISHED_BASIS`, `tools/generate_grid_intensity_feed`
  `ANNUAL_LEVEL_BASIS` and its named gap, and `company/carbon/half_hourly_footprint`
  `FOOTPRINT_BASIS` / `ELECTRICITY_LEG_BASIS`. So does the "corrected 2026-10-05" note in
  `household_carbon_and_the_measures_that_save_it.md`. That correction read NESO's methodology text,
  which the data has not matched since 2020-04-27. **The text and the series disagree, and the series
  is what the household is shown.** A household's electricity since 2020-05 is about 8-10% low
  against "per kWh consumed". The DESNZ T&D factor needed to add losses as a named, separate line is
  already sourced in that page (0.01853 kgCO2e/kWh, 2025 set).
- **MAJOR-2**, the basis step itself, is above. The reviewer graded the rebase onto the Historic
  Generation Mix sound, with three conditions:
  - settle MAJOR-1 in the same move;
  - check how the historic mix treats embedded generation and imports;
  - record that the CKAN file is a later, revised edition no supplier could have seen in 2019, as a
    point-in-time caveat on the feed.
- **MINOR:**
  - Pre-step `fuelmix_fill` half hours sit about 20 g below their neighbours, because they are
    unscaled.
  - The feed's `named_gaps` still calls the step "not established".
  - The feed ends 2025-06-07, because it is INDO-weighted; FUELHH true demand would reach 2025-12-31.
  - The futures `level_error` (11.3 g, in-sample) understates the out-of-sample annual error
    (-40 to +23 g). Imports and nuclear availability are the missing regressor.
  - Electricity is CO2 under a `co2e` name and is added to gas CO2e.
  - Import factors are NESO's fixed defaults, not "the exporting country's intensity".
- **Held up:**
  - settlement keys and clock-change days (best correlation at lag 0);
  - the FUELHH P48 fix;
  - no zeroed gaps, and only 42 true gaps in a decade;
  - futures with no absurd floor;
  - embedded and biomass variants measured, not asserted;
  - 35 tests, including partition reachability.

G14 stays at L2. L3 is unearned, and the Expert Hour itself is now taken.
