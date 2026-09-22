# PRE-REGISTRATION — what migrating `weather_inputs` onto the per-cell store changes on the book

**Written 2026-09-21 BEFORE the measurement.** Drawn as LANE 1 BUILD,
`W1_14_weather_cells_for_household_heat_load`, level 1→3. The work is step (1) of the three the
atom's `block_reason` names: *"migrate `weather_inputs` onto `sim.weather_world` — the seam must
resolve to a CELL, not to a customer_id with a CSV"*. Step (2) (add Birmingham's cell) is a store
build, step (3) is a coverage judgement; neither is this.

Two legs still read the four per-property CSVs at HEAD: the demand-shape adjustment
(`_weather_adjusted_shape_fn`, 4c-2) and the forward-price temperature lookback
(`lookback_mean_temps`, 4c-3), both fed from `weather_means_for_customer` /
`cloud_cover_for_customer`. The fabric physics leg already reads the store
(`fabric_demand_path.WeatherWorldSource`, 2026-09-17).

## Predictions

1. **Premises with a non-empty daily mean-temperature series TODAY (per-property archive):
   14 of 18.** The four archive sites are London/Manchester/C3/C4; the four I&C premises at
   Birmingham (C_IC1, C_IC2) and Teesside (C_IC3, C_IC3g) match no archive coordinate and
   `cell_matched_site` accepts nothing the book holds, so they fall to step 3 — their own id, no
   CSV, and `load_weather_means` returns `{}`.
2. **Premises with a non-empty series AFTER the migration: 16 of 18**, the two misses being
   C_IC1/C_IC2 (Birmingham, 7.35 km outside `MAX_SNAP_KM`). So the migration is a NET GAIN of the
   two Teesside premises and a loss of none.
3. **The two sources disagree materially where both answer.** The store's temperature is HadUK-Grid
   1 km plus the cell's own `level_c`; the CSVs are ERA5 via Open-Meteo at ~9 km. `weather_world`
   records HadUK reading +1.2 °C warmer than ERA5 at London/Manchester/Glasgow, so I predict a
   **mean absolute daily difference ≥ 0.5 °C at C1 (London)** over the overlapping window, and the
   store reading WARMER on the mean. This is a fidelity change, not an equivalence, and it is
   decided blind to company results (R13: the 1 km observational analysis beats the 9 km reanalysis).
4. **The migration is mutatable on the live book.** Unlike the `_has_archive` repair of 2026-09-20 —
   which was unmutatable because archived ids precede un-archived ones at every shared coordinate —
   pointing the resolver back at the archive changes the VALUES for every premise the store serves,
   so a control keyed to the real roster can see it.

Filed by the worker tick. Result goes to `docs/staging/` as a WORKER_RESULT beside these.
