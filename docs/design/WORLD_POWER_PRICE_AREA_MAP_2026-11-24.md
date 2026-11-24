# The world-power-price area, leg by leg: what each link of the weather-to-price chain reads, what this week's grades said about it, and where the misses sit (2026-11-24)

*Autonomous worker, 24 Nov 2026, Lane-0 item `world-power-price-area-map-before-the-fleet-power-curve`. This follows
`ways_of_working` W1 (`docs/design/THE_LEARNING_LOOP_ON_HOW_WE_WORK.md` §7). The learning loop reads STOP on
world-power-price: 15 held of 22, with 7 misses, 4 of them code-or-reader. W1 puts the area's map before the next fix,
and this page is that map. **No fix is written here.** It was read from the code at origin `53fd13ff8d`. The `sim/`
modules below were checked blob-identical in the shared tree before the probe in s.6 ran. The template is
`LEVEL_DD_AREA_MAP_2026-11-11.md`. This page is organised by **leg**, because each of this week's grades swapped or
graded one leg at a time. The domain is on the K8 page, `docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md`.
This page holds what the code does.*

## 0. Which price, said before any leg

The area has three prices. Most of this week's misses came from reading one as another.

| Price | What it is | Where it lives | Who reads it |
|---|---|---|---|
| **SSP** | Elexon's System Sell Price: the **imbalance** price, half-hourly | `sim/cache/elexon_ssp_full.json` | Every 2016-2025 run settles at it. It is the target that `price_engine`'s A0-A2 were fitted to. It is "the record" in every chain grade. |
| **MID** | Elexon's Market Index price: the **within-day traded** price, half-hourly | read by the 25 Nov grade's probe only | The power-record grade (`25be0c954f`). It is **not** the day-ahead auction, and day-ahead is not held. |
| **Chain price** | `derive_price`: a daily price made from one weather draw | `sim/weather_price_chain.py:297` | No 2016-2025 run reads it. Its readers are in s.2. |

The chain is **daily** (`load_daily_record` averages every half-hourly source to the day, `:108`). Its unit is
£/MWh. A chain grade compares daily or monthly means against daily-mean SSP. It never reads the half-hourly shape.
`intraday_shape` owns that shape (chain grade, cause 4).

## 1. The chain, leg by leg, as the code builds it

`derive_price` (`sim/weather_price_chain.py:297`) composes five legs. The weather draw is `(temperature, wind speed,
cloud, day of year)` plus a gas price. The fitted constants are `fit_chain()` (`:212`), printed at origin `53fd13ff8d`
over the 3,337 record days, 2016-03-01 to 2025-06-07.

| Leg | Function, file:line | Reads | Constants as shipped | What this week's grades said |
|---|---|---|---|---|
| **W0 weather** | `load_national_daily`, `sim/weather_tail_demonstration.py:130` | The Open-Meteo daily mean over **four customer towns** C1-C4 (`:84`), at 10 m | none | It is not a hub-height or national wind field. Median wind speed is 3.83 m/s, and 28.4% of days fall below 3 m/s (s.3, C1). |
| **D demand** | `demand_from_weather`, `:246` | Temperature only | base 23,954 MW, 749 MW/HDD, 506 MW/CDD, R² 0.55 | Swapping in real demand (arm D, `64fd7f5f8`) **moves nothing**. Not this week's gap. |
| **R wind output** | `wind_output_from_speed`, `:272`, then `price_engine.wind_power_output_fraction`, `sim/price_engine.py:217` | Leg W0's wind speed | One turbine's cubic curve, cut-in 3, rated 12, cut-out 25 m/s, times `wind_fleet_mw` = **128,701 MW**, mean-matched to the record (`:229`) | **The over-coupling lives here.** The chain moves 2.3-3.9× the real fleet's MW per m/s (`64fd7f5f8`). A fleet-aggregate curve fitted on 2016-19 brings this to 0.75-1.19× out of sample (`4413f635ab`). The per-year fleet alone leaves it at 3× (arm G). |
| **S solar** | `solar_output_from_weather`, `:287` | Day of year, cloud | `solar_fleet_mw` 12,459 on a cosine envelope, corr 0.76 | Not graded alone. It is subtracted from INDO, which is already net of embedded solar. That double count is deliberate: it was the held-out fit optimum (`price_engine.py:205-208`). |
| **G gas floor** | `gas_floor_price`, `price_engine.py:132` | `rec["gas_price"]`, from `load_nbp_history` (`sim/gas_prices_history.py:120`) | `THERMAL_EFFICIENCY` 0.50; carbon **0.0** (`derive_price` passes none, so the default at `:135`/`:247` applies) | Carbon is the pre-crisis bias: −£12.0 becomes +£3.1 (`2ce49dcd3`). Carbon raises crisis and post-crisis error, because A0-A2 already carry it. The refit fixes that (`d424b7809`). 2022's +£26 is mostly the gas input, TTF over GB gas (s.3, C2). |
| **P residual → price** | `system_margin_price`, `price_engine.py:167` | D − (R + S), over `DISPATCHABLE_CAPACITY_MW` 35,000 | A0/A1/A2 0.327/1.335/3.828, fitted with carbon at zero against SSP; `X_TIGHT` 0.70, p 2.0 | Given real inputs (arm B), it is 0.92-1.35× the record per GW, and it beats the gas-only null in the crisis (`64fd7f5f8`). An unattributed **−£8 post-crisis level gap** remains with real inputs. |
| **L CfD levy** | **no code.** Probed only (`783c0e26e`) | — | — | (Strike − world daily price) × real generation reproduces LCCC's reconciled levy to ±2% a year outside the crisis, and to £33m in 2022. Forward CfD volumes are a GAP (K8 page §13 gap 3). |

**Interconnectors, nuclear availability and CfD/RO negative bidding have no leg.** The K8 page (§10) lists them. The
coupling arm gives the reason interconnectors are not the next build: the price leg is within ±30% per GW after the
crisis.

## 2. Who reads the chain, and who does not

| Reader | file:line | What it takes |
|---|---|---|
| `flex_dispatch._load_record` | `sim/flex_dispatch.py:220-224` | `derive_price_on_record()`'s `residual_mw`, used as the world's true scarcity for flexibility (`true_scarcity_mask`, `:227`) |
| `weather_price_triad.measure` | `background/weather_price_triad.py:46`, `:102` | The chain as ground truth against `company/pricing/weather_price_belief.py`. Harness only. |
| `ssp_tail_model.model_ssp_series` | `sim/ssp_tail_model.py:32` | Leg P alone (`synthetic_price`) on **real** drivers, not the weather legs |
| `weather_demand_chain` | `sim/weather_demand_chain.py:54` | `load_daily_record` only |

**What does not read it:** every 2016-2025 run, which settles at real SSP; and `sim/forward_curve.py`, which reads
`weather_price_sensitivity`, not the chain. **No forward-years generator is built**
(`docs/design/curriculum/forward_years.json`, `consumed_by: NOTHING YET`). "Forward years will price from it" is
therefore the chain's *intended* reader. No present reader prices forward years from it. That does not lower the
steer's urgency. It means a fix to the chain today changes flexibility's scarcity mask and the weather-price triad's
score, and nothing a book shows.

## 3. What the census found that no item asked for

**C1. The wind fleet scalar is 128,701 MW, six times the record's windiest day (20,977 MW).** It is a
mean-match, not a fleet. On a 10 m town wind, the single-turbine curve's mean fraction is 0.043, so the scalar is
whatever makes 0.043 × scalar equal the record's 5.5 GW mean. The scalar is then multiplied into a cubic:

- 28.4% of record days are below the 3 m/s cut-in and give exactly zero wind;
- the record's windiest day (11.1 m/s in town) gives 100,807 MW;
- on 5.8% of days the chain makes more wind than the record's true maximum day (20,977 MW).

That is the mechanism behind `64fd7f5f8`'s 2.3-3.9×, in the code's own constants. The fleet arm cured it by
changing the curve, and the scalar is then refitted against the new curve. **A build that swaps the curve and keeps
the old scalar would be catastrophic.** The scalar is fitted inside `fit_chain` (`:229`), so swapping the curve there
refits it automatically. There is a second caller, and it does not refit: `renewable_capacity_trend.py:200`
mean-matches the **per-year** fleet (`capacity_wind`, the W1_7 scalar arm E uses) against the same single-turbine
curve. If the curve is swapped in the chain only, the per-year fleet stays fitted to the old curve.

**C2. The gas leg is the monthly TTF proxy, flat within every month.** `load_nbp_history`
(`gas_prices_history.py:120`) returns `nbp_sap.csv`, the IMF/FRED TTF monthly price expanded to days (`:91`). The field
is named `systemSellPrice`, which is the name of the power price. Measured: one distinct gas value per month, on all
3,337 days. The daily GB SAP spliced from 2018, `load_gas_baseline_spliced` (`:218`), exists, and the chain does not
read it. The chain grade's gas-only null read the same `rec["gas_price"]`. Both sides of "loses to a gas-only null"
therefore share the proxy, and the comparison is fair. But every chain figure in 2022 carries TTF's 29% premium over
GB gas (`d424b7809`'s record, point 4). The steer's gas page graded the world's gas record. The chain's own gas input
was never swapped on its own. **That is a one-variable arm not yet filed.**

**C3. The record's AGWS wind double-counts republished half-hours.** `aggregate_wind_generation`
(`sim/generation_demand_history.py`) sums every publish of a key. 1,040 wind keys have 2-4 publishes, and two have
564. One half-hour, 2022-03-26 period 45, reads **1,480,896 MW**, so that day's mean reads 35,458 MW on a 2.6 m/s day.
Across the window, the duplicates raise the mean from 5,482 to 5,509 MW (0.5%), and the fleet scalar moves by 0.16%.
This has been known since the phase-3b recalibration (`docs/calibration/price-engine.md:171`). The recalibration
script deduplicated its own copy (latest `publishTime`), and the shared aggregator was never fixed. **Every chain grade
this week used the undeduplicated record** through `load_daily_record`. Their means and slopes move by under 1%. Any
reader of a maximum or a top percentile reads the artefact, and it caught this page's own M1 (s.6).

**C4. Carbon is zero in two places, and they cancel.** The call passes none, and A0-A2 were fitted against SSP with
carbon at zero, so the multiplier absorbed it. Adding carbon to the call alone makes the crisis 53.2 and post-crisis
23.4 (`2ce49dcd3`). Refitting with carbon makes them 24.3 and 9.3 (`d424b7809`). **The two must ship together**, and
shipping the refit also needs a sim carbon series that the chain passes. `merit_order_reconstruction` still names
2022-24 as allowance gap years, so one table must hold the allowance price, not two.

## 4. This week's grades, each placed on a leg

The learning loop reads **one** of the seven grading commits. Only `25be0c954f` carries a `Graded:` trailer. Counted
from each record's own prediction table:

| Commit (pre-registered in) | Graded | Held · missed | Misses and their cause | Leg |
|---|---|---|---|---|
| `25be0c954f` (`6c828bc2c`), SSP record against MID and SRMC | 22 | 15 · 7 | **reader 4**: day-ahead priors applied to MID (E3 early years, E3 ratio, E4 MID pre, E4 ratio). **domain 3**: E1 crisis, E2 post, E6 Ireland | s.0, the instrument |
| `3589e04c7` (`2a24f6c54`), the chain against the record | 6 | 1 (half) · 5 | **code 4**: P1/P2 pass pre/post, daily vol low, lag-1 low, 99.9th low in the crisis. Each assumed a chain without leg R's over-coupling. **domain 1**: the cold-still premium is 1.78-1.99×, against a 1.3-1.6× prior | R (P, F) |
| `2ce49dcd3`, carbon arm | 3 | 1 · 2 | **code 1**: crisis and post errors rise, because A0-A2 carry carbon. **width 1**: MAE missed by £0.14 | G, P |
| `d424b7809`, refit with carbon | 3 | 2 · 1 | **other 1**: pre-crisis bias −5.43 against ±5, unattributed | G, P |
| `783c0e26e` (pre-registered before summing), CfD levy | 6 | 4 · 2 | **reader 1**: A1 used `Market_Reference_Price` where `Weighted_IMRP` is the paid reference. **domain 1**: A3, the 2022 quarters swung back faster | L |
| `64fd7f5f8` (`8e8790de4`), which leg over-couples | 5 | 4 · 1 | **code 1**: W3, the price leg is not steep after the crisis (0.92×) | P |
| `4413f635ab` (`7c0f6f406`), fleet-aggregate curve | 7 | 7 · 0 | — | R |
| **Total** | **52** | **34 · 18** | **code 6, reader 5, domain 5, other 2** | |

**What the loop reads against what happened.** The loop reads 22 graded, 7 missed and 4 code-or-reader. The week
holds 52 graded, 18 missed and **11 code-or-reader**. The area would have tripped STOP from the chain grade alone, at
06:01, three hours before the map was drawn. A grade without a trailer is invisible to the loop, and six of seven
were. It is not a defect in the loop, because the trailer is optional by design. It is the cost of leaving the trailer
off. Every grading commit in this area from here carries one.

**Which of the 4 counted misses came from misreading the code or the reader.** All four are **reader** misses, and
none is about the chain's code. The grader took priors from the day-ahead auction (no negatives before Dec 2019, few
spikes) and applied them to MID, the within-day traded price, which has its own negatives and spikes. Their cure is
s.0 of this page, naming which price before measuring it. The **code** misses, the ones about our model of the chain,
are all in uncounted commits, and five of the six sit on leg R or on A0-A2 carrying carbon. Both are now on this map
as C1 and C4.

## 5. The fleet power-curve arm the drawn item asks for is already spent

The item asks for the map first, and "only then pre-register the fleet aggregate power-curve arm". That arm was
pre-registered in `7c0f6f406` (09:28) and run in `4413f635ab` (09:35) by the steer's own lane, before this map was
drawn. Seven of seven held. It is not pre-registered a second time. The order the item asked for did not happen. The
arm's bounds were filed before its run and allowed for the curve not being the excess, so the result stands. The cost
was that the arm ran against a model of the code that did not yet know C1-C3.

**What the map adds to the build that arm names.** The build is the aggregate curve plus the per-year fleet in
`sim/weather_price_chain`, shipped with the refit and its carbon series. It must, by this map:

1. **Refit both fleet scalars against the new curve**: `fit_chain`'s whole-window scalar and
   `renewable_capacity_trend`'s per-year one (`:200`). Never carry 128,701 MW over (C1).
2. **Read the deduplicated AGWS record** (latest `publishTime` per key). Fix it in the shared aggregator, so that the
   fit and every grade read one record (C3).
3. **Hold the curve at its in-record maximum above 10 m/s**, as `4413f635ab` already requires.
4. **Ship carbon in the call and in A0-A2 together** (C4).
5. **Leave the gas input as it is in that build.** Swapping TTF for the spliced daily SAP is its own one-variable arm
   (C2). Bundled with the curve, neither change could be attributed.

## 6. This page's own pre-registration, graded

Filed at 10:11 UTC in `/var/tmp/wppmap/PREDICTION.txt`, before `/var/tmp/wppmap/probe.py` ran. The output is in
`/var/tmp/wppmap/probe_out.txt`.

| Filed | Outcome | Held? |
|---|---|---|
| M1: the chain's daily wind exceeds the record's maximum day on 4-15% of days; the chain's maximum is ≥ 4× the record's | 1.56%; 2.84× | **missed** (reader). The "record maximum" was the C3 artefact, 35,458 MW. Against the true maximum day, 20,977 MW, it reads 5.8% and 4.81×, both inside. The filed grade stands. |
| M2: scarcity live (x > 0.70) on 15-40% of days, and on ≥ 2× as many winter days as summer days | 38.4%; 61.3% against 1.3% | **held** |
| M3: corr(chain price, wind speed) ≤ −0.5 in ≥ 8 of 10 years, and 2022 the weakest | 7 of 10 (2020 −0.498, 2021 −0.185, 2025 −0.451); the weakest is 2021, and 2022 is −0.714 | **missed** (code). Leg G multiplies leg P. In 2021 the monthly gas input rose fivefold within the year (£19.5 in January, £99.6 in December), and that swamps the wind term. In 2022 it moved between £74 and £187, a smaller ratio around a high level. |

One held, two missed: one reader miss and one code miss. Both misses are of the classes this page names, and that is
the evidence the map was needed.

## 7. What this changes

- **The STOP is spent when this page lands.** The loop's `misses_since_map` judges it from here.
- **The order of the remaining steer item 4 is unchanged:** build the curve per s.5's five conditions, then the gas
  input arm (C2), then the −£8 post-crisis price-leg gap.
- **Two defects found here are owned by that build, not filed as new items:** C3 (fix the aggregator) and C1's second
  caller (`renewable_capacity_trend.py:200`). They are conditions of the build. Each is a few lines of code that no separate item would reach sooner.
