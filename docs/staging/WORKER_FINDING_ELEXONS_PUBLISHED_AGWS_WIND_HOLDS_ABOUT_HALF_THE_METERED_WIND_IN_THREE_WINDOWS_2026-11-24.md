**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_6_physics_price_signal`

# Elexon's published AGWS wind holds about half the metered wind in three windows, and the world fits its wind fleet to it

Found by the worker, 24 Nov 2026, while measuring item 4 step 2 of the weather-to-price steer before
building it. Numbers are in
`docs/staging/records/WORKER_RESULT_THE_END_YEAR_CLAMP_ARM_MEASURED_BEFORE_ANY_BUILD_2016_CAN_TAKE_ITS_OWN_FLEET_AND_2025_CANNOT_2026-11-24.md`
§3 and §5.

**What.** Month by month, Elexon's AGWS wind (`sim/cache/elexon_agws_full.json`) holds 0.8-1.2 of
FUELHH `WIND` from mid-2017 to January 2023. In three windows it falls to between 0.41 and 0.6 of
FUELHH:

- April 2017;
- late January to early August 2023;
- mid-April to mid-November 2024.

Offshore wind is what goes missing. In May 2024 AGWS offshore averages 504 MW. Against DUKES annual
generation, AGWS falls from 0.705-0.764 (2017-22) to 0.624 (2023) and 0.643 (2024), while FUELHH holds
0.77-0.79. A live API probe returns the same bytes as the cache, so this is the published series and
not our ingestion.

**Who reads it.** These are the places that read AGWS today; none of them has been re-measured:

- `sim/renewable_capacity_trend.fleet_trajectory` sets the 2023-24 wind fleets at 0.376 and 0.372 of
  DUKES capacity, the only full years below 0.417.
- `sim/weather_price_chain.load_daily_record` uses it as "the record's wind" in every chain grade.
- `sim/generation_demand_history.aggregate_renewable_generation`, the renewable input to
  `sim.price_engine`.
- `tools/generate_grid_intensity_feed.py`.
- The `tools/ep13_*` bounds.
- The `simulation/run_phase3b_*` and `run_merit_order_reconstructibility` runs.

**Owed, in order.**

1. Say why the windows exist from what Elexon or NESO publish: the AGWS (B1630) data notes, the
   Insights release notes, or ENTSO-E transparency submission notices for GB offshore. If nothing is
   published, say so plainly. Do not invent a reason.
2. Name the one basis the world's record wind should use. FUELHH has no holes, but it leaves out
   embedded wind. The wind-target arm already argues for FUELHH on the chain's side. A decision for the
   whole world belongs on the electricity page (its GAP 9) before any code changes (K8).
3. Re-measure each reader above on that basis. A reader whose published figure moves gets its own row.

**Not done here.** No series was patched or masked. A hand-masked window would be a constant picked
to fill a gap.

Reverse: delete this file.
