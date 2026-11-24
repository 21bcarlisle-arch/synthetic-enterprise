**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: a fleet-aggregate power curve, fitted on 2016-19 only, takes the chain's over-coupling out of its wind leg out of sample (2026-11-24)

**Pre-registration.** `WORKER_PREREG_A_FLEET_AGGREGATE_POWER_CURVE_TAKES_THE_CHAINS_OVER_COUPLING_OUT_OF_ITS_WIND_LEG_2026-11-24.md`,
landed on origin as `7c0f6f406` before this ran. **Knowledge:** §6a of
`docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md`.

**How it was run.** The probe ran exactly as carried in the pre-registration, from the shared repo
root. Every loaded `sim/` and `simulation/` module was asserted blob-identical to origin. It took 6 s.
The step-1 refit constants were reproduced, and the chain's own renewable series was reproduced from
its parts, before any arm ran.

## The fitted curve

Fitted on 2016-01-01..2019-12-31 against AGWS wind normalised by its own calendar-year mean (shape
only): **a = 1.665, b = 2.567 m/s, σ = 2.93 m/s**. The transferred speed w′ = a·w + b takes the towns'
10 m daily mean (about 4 m/s) to about 9 m/s, which is the order of a hub-height speed. Daily
correlation with AGWS wind rises from 0.610 (single curve) to 0.693.

Capacity factor relative to its own mean, by national town speed (single / aggregate):

| w (m/s) | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 |
|---|---|---|---|---|---|---|---|---|---|
| single | 0 | 0 | 0 | 0.51 | 1.34 | 2.59 | 6.65 | 13.3 | 23.3 |
| aggregate | 0.19 | 0.38 | 0.66 | 1.01 | 1.36 | 1.65 | 1.95 | 1.97 | 1.54 |

The single curve gives zero output on any day below 3 m/s in town and 13× the mean at 10 m/s. The
aggregate curve is the flatter fleet shape that §6a describes.

## The arms (wind MW per m/s against the record · price slope against the record · monthly MAE, £/MWh)

| Arm | Pre | Crisis (out of sample) | Post (out of sample) |
|---|---|---|---|
| Record: wind MW/(m/s) · price slope | 1,371 · −1.65 | 1,659 · −16.35 | 2,175 · −9.12 |
| A single, whole fleet (the chain) | 3.79× · 4.61× · 6.75 | 2.73× · 1.84× · 24.33 | 2.22× · 1.61× · 9.29 |
| G single, per-year fleet | 3.26× · 4.15× · 5.97 | 3.05× · 2.04× · 22.20 | 3.03× · 2.16× · 7.69 |
| F aggregate, whole fleet | 1.19× · 1.57× · 7.18 | 1.02× · 0.80× · 19.30 | 0.75× · 0.66× · 8.57 |
| **E aggregate, per-year fleet** | **1.04× · 1.44× · 6.39** | **1.15× · 0.87× · 16.95** | **0.96× · 0.77× · 8.20** |
| gas-only null (the grade's) MAE | 5.4 | 24.5 | 6.7 |

Monthly bias, E: −5.20 / +1.91 / −1.88 (A: −5.43 / +12.29 / +5.82).

## Predictions against outcomes (kept as filed)

| Filed | Outcome | Held? |
|---|---|---|
| F1: F's wind MW per m/s ≤ 1.6× the record's, all regimes | 1.19×, 1.02×, 0.75× | **held** |
| F2: F's price slope ≤ 2.0× pre, ≤ 1.3× post | 1.57×, 0.66× | **held** |
| F3: E beats A on monthly MAE, all regimes | 6.39 < 6.75; 16.95 < 24.33; 8.20 < 9.29 | **held** |
| F4: E loses to the null pre (≥ 5.4) and post (≥ 6.7), beats it in the crisis (< 24.5) | 6.39; 8.20; 16.95 | **held** |
| F5: G's wind MW per m/s stays ≥ 2.0×, all regimes | 3.26×, 3.05×, 3.03× | **held** |
| F6: fitted σ > Staffell-Pfenninger's farm σ at mean w′ | 2.93 > 2.46 | **held**, narrowly |
| F7: aggregate daily correlation ≥ single | 0.693 ≥ 0.610 | **held** |

**Seven of seven held, so the obvious question is whether the bounds were too easy.** F1 and F3 were
not. They allowed for the curve not being the excess, and the coupling arm had already shown the
excess could sit in the input series instead (§6a: a town 10 m daily mean). The crisis and post
regimes are out of sample for the curve's three parameters. F6's margin is 0.47 m/s, and σ trades
against a, so F6 is weak evidence. It is not relied on below.

## What it shows

1. **The over-coupling was the curve's shape.** With the curve fitted on 2016-19 alone, the wind leg's
   MW per m/s comes within 0.75-1.19× of the record in every regime, against 2.2-3.8× before. The
   price slope comes within 0.66-1.57×, against 1.6-4.6×. That is about as close as the real-renewable
   arm C got (`64fd7f5f8`).
2. **The per-year fleet alone does nothing for the coupling (G). With the curve, it is the level
   (E against F).** G's slope ratio stays at 3.0-3.3×, so W1_7's fleet was worse in the grade for this
   reason. With the aggregate curve, the per-year fleet cuts the crisis MAE from 19.3 to 17.0 and
   tightens bias in every regime. That level is in sample, by construction, so a forward year needs
   a capacity projection rather than a matched mean (below).
3. **The chain now beats the gas-only null in the crisis by £7.5 and still loses either side** (+£1.0
   pre, +£1.5 post). Those remaining losses belong to the price leg: the coupling arm's real-renewable
   arm C lost by similar margins (5.96 and 7.35). They are not the weather leg.
4. **The correlation with wind is still −0.67 to −0.79 against the record's −0.15 to −0.41.** As the
   coupling arm said, that is missing noise, not strength. No slope fix closes it.

## Caveats a ship must carry

- **The curve falls above about 10 m/s** (1.97 → 1.54 at 12). The transfer takes a 12 m/s town day to
  about 22 m/s, and the world's hard cut-out at 25 m/s then removes the Gaussian's upper tail. The
  record has 2 of 3,337 days above 10 m/s (maximum 11.1), so the fall is unconstrained by data. A
  shipped curve must not extrapolate it into forward storm draws. It should hold the curve at its
  in-record maximum, or replace the hard cut-out with a published high-wind shutdown, with a K8 line
  either way.
- **The per-year fleet is matched in sample.** For forward years it has to come from a capacity path
  (W1_7's ET 6.1 register, with the BM-unit share AGWS covers). It must never come from matched
  output, which a forward year does not have.
- The fit uses AGWS (BM-unit wind) only. Embedded wind stays outside, consistently with the price leg.

## Decision (by the rule filed before the run)

F1 and F3 held, and E beats F. **The next build is the aggregate curve with the per-year fleet in
`sim/weather_price_chain`**, citing §6a, with the two caveats above handled in the build. It should
land with the step-1 refit and its sim carbon series, which is still owed, because each without the
other is worse than either shipped arm. The post-crisis −£8 price-leg level gap stays filed separately.

## What this does NOT do

- **Nothing in the world changed.** `sim/weather_price_chain.py` still uses the single-turbine curve.
- It does not grade forward years. The forward fleet path is a GAP until the build names its source.

## Raw output

Regenerate with the probe in the pre-registration (6 s). Every figure above is copied from its JSON.
