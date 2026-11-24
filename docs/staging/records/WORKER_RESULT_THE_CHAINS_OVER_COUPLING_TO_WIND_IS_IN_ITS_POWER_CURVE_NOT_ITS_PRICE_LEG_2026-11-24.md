**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the chain's over-coupling to wind sits in its power curve, not its price leg, and an interconnector term is not the next build (2026-11-24)

**Pre-registration.** `WORKER_PREREG_WHICH_LEG_OF_THE_WEATHER_TO_PRICE_CHAIN_CARRIES_ITS_OVER_COUPLING_TO_WIND_2026-11-24.md`,
landed on origin as `8e8790de4` before this ran.

**How it was run.** The probe ran exactly as carried in that record. It ran from the shared repo root,
whose nine `sim/` and `simulation/` modules were checked blob-identical to origin first. It took
4 s. The step-1 refit constants (0.2916 / 1.0792 / 2.8242) were reproduced before any arm ran.

Coupling is a **slope**: £/MWh of daily price anomaly per m/s of national wind-speed anomaly, within
the month.

## The renewable leg: the chain's wind output moves 2.3 to 3.9 times as much as the fleet's

| Regime | Real renewable, mean MW | Chain, mean MW | Real MW per m/s | Chain MW per m/s | Ratio |
|---|---|---|---|---|---|
| Pre | 6,067 | 7,103 | 1,298 | 5,115 | 3.9× |
| Crisis | 7,062 | 6,426 | 1,608 | 4,501 | 2.8× |
| Post | 8,617 | 6,441 | 2,095 | 4,732 | 2.3× |

## The price leg: given real inputs, it is within 0.92 to 1.35 times the record

£/MWh per GW of real renewable anomaly. Record against arm B (real demand and real renewable through
the refitted price function):

| Regime | Record | Arm B | Ratio |
|---|---|---|---|
| Pre | −1.66 | −2.23 | 1.35× |
| Crisis | −8.16 | −8.67 | 1.06× |
| Post | −3.70 | −3.40 | 0.92× |

## The arms (monthly, demand-weighted, £/MWh)

| Arm | Pre: MAE · bias · slope/(m/s) | Crisis: MAE · bias · slope | Post: MAE · bias · slope |
|---|---|---|---|
| **Record slope** | — · — · **−1.65** | — · — · **−16.3** | — · — · **−9.12** |
| A: chain (step-1 refit) | 6.75 · −5.43 · −7.62 | 24.33 · +12.29 · −30.1 | 9.29 · +5.82 · −14.6 |
| B: real demand + real renewable | 5.51 · −3.08 · −2.91 | 14.44 · −2.74 · −13.8 | 9.89 · −8.06 · −7.34 |
| C: real renewable only | 5.96 · −5.33 · −2.26 | 17.16 · +2.29 · −12.3 | 7.35 · −3.72 · −6.87 |
| D: real demand only | 6.49 · −2.80 · −8.50 | 21.45 · +7.28 · −31.5 | 8.71 · +1.14 · −14.8 |
| gas-only null (the grade's) | 5.4 | 24.5 | 6.7 |

Correlation with wind (record / A / B): pre −0.15 / −0.84 / −0.62; crisis −0.33 / −0.84 / −0.63; post
−0.41 / −0.87 / −0.74. Monthly std (record / A / C): pre 13.2 / 14.8 / 13.3; crisis 65.8 / 82.2 / 71.7;
post 16.1 / 22.5 / 12.1.

## Predictions against outcomes (kept as filed)

| Filed | Outcome | Held? |
|---|---|---|
| W1: A's slope at least 1.5× the record's, pre and post | 4.6× pre, 1.6× post | **held** |
| W2: chain mean renewable above the record's pre, below it post | 7,103 > 6,067; 6,441 < 8,617 | **held** |
| W3: B's price leg at least 1.3× the record's per GW, pre and post | 1.35× pre, 0.92× post | **missed**. Held pre; refuted post (within ±30%) |
| W4: C beats A on monthly MAE, pre and post | 5.96 < 6.75; 7.35 < 9.29 | **held** |
| W5: B's correlation with wind at or below −0.6 pre | −0.623 | **held** |

## What it shows

1. **The grade's "too strong" is real as a slope, and nearly all of it sits in one link:** wind
   speed to wind output. Swapping in the real fleet output (C) takes the pre-crisis slope from −7.6
   to −2.3 against the record's −1.65. The crisis slope goes from −30 to −12 against −16, and the
   post-crisis one from −14.6 to −6.9 against −9.1. Swapping in real demand (D) moves nothing. The
   link is `wind_power_output_fraction`: one idealised turbine's cubic curve, cut-in 3 and rated 12
   m/s, applied to a **national mean** wind speed and scaled by one whole-window fleet. A fleet of
   turbines spread across the country does not ramp like one turbine at the country's average wind.
   Some sites are at rated output while others are below cut-in. Its aggregate curve is flatter.
   That is a candidate, stated here, not yet measured.
2. **An interconnector term is not the next build.** The price leg is within ±30% of the record per
   GW after the crisis and 6% steep in it. Before the crisis it is 35% steep. That leaves room for a
   damping term later, but it is the smaller gap. Steer item 4 says "add interconnector coupling or
   state why not". This is the why not, for now.
3. **The whole-window fleet misallocates by year (W2).** The chain over-supplies renewables before
   the crisis by 1.0 GW and under-supplies after it by 2.2 GW. Part of the post-crisis +£5.8 bias in
   A is this shortfall cancelling a price-leg level gap. With real inputs (B), the post-crisis bias
   is **−£8.1**. That is a separate level error in the price leg after 2023, not yet attributed.
   CfD-driven negative hours and the gas input are the first candidates.
4. **With real inputs, the price leg beats the gas-only null in the crisis (14.4 against 24.5) and
   ties it before (5.51 against 5.4).** After the crisis it still loses (9.89 against 6.7), on that
   level error. So the chain's month error is mostly its weather-to-generation leg, not its pricing.
5. **The correlation gap is mostly missing drivers (W5), and no slope fix closes it.** B with real
   inputs still correlates −0.62 to −0.74 against the record's −0.15 to −0.41. The grade's
   correlation statistic will stay FAIL-low after any coupling fix. It should be read as "the chain
   has no noise", not as strength.

## What this does NOT do

- **Nothing in the world changed.** `sim/weather_price_chain.py` still maps wind through the
  single-turbine curve.
- **The next build is the generation leg, knowledge first (K8):** a fleet-aggregate power curve and a
  per-year fleet. What published evidence says a GB fleet's aggregate curve looks like against a
  reanalysis or national wind speed is not yet on a page. The renewables.ninja validation work
  (Staffell and Pfenninger, 2016) is the place to start. Then one arm: the chain with an
  aggregate curve fitted on the record, with its prediction filed first. The year-aware fleet
  (W1_7) was worse in the grade, so the fleet-by-year fix must come with the curve, not alone.
- The post-crisis −£8 level gap with real inputs is filed here as the next unattributed residual.

## Raw output

Regenerate it with the probe in the pre-registration (4 s). The headline JSON values are the tables above.
