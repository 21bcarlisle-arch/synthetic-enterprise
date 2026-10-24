# Forward years: the G9 recommendation before any build (2026-10-24)

*Owed by the director's ruling of 24 Oct 17:22 BST, "after that we probably want weather and simple
wholesale prices and forward products for hedging simualted for some future years"
(`docs/staging/advisor/done/DIRECTOR_RULING_FORWARD_YEARS_COME_RIGHT_AFTER_THE_BASICS_2026-10-24.md`,
work item 3). This waits for his go (G9). Nothing here is built. The basics come first: 0 of 7 atoms
were at target on 24 Oct (stretch log, a730bebe1), and forward runs do not start before they are.*

**What I need from him:** a yes, or a change to any of the six numbered choices in §8. Two of them
are his alone because they are curriculum: the fuel path range (§2b) and the fleet path (§3).

---

## 0. What already exists, measured today, not recalled

| Piece | State on origin 6216a1655 | Measured |
|---|---|---|
| Forward weather | `WeatherWorld.extended_by_analogue_years`: each forward year replays one whole record year, a seeded permutation | It is a replay, which is what the ruling says not to do. The analogue year is independent of the price beside it (its own docstring names this) |
| Forward prices | `sim/scenario/bimodal_generator.py` (two-regime Markov) + `gas_scenario_generator.py`, wired by `simulation/run_scenario.forward_world` | Price is drawn **independently of weather**. A cold, still year does not move price |
| Weather to price chain | `sim/weather_price_chain.py` (W1_6, L4): weather -> demand and renewables -> residual demand -> price on a gas floor | **0.29 ms per run year.** Daily-mean MAE £24/MWh against a real mean of £78 over 3,337 days. Cold-and-still days price at 2.2x the rest |
| Synthetic weather engine | `sim/weather_engine.py`: AR1 with regime-switching covariance, 4 locations | Reproduces the 2016-2025 means, std and cross-site correlation (0.952 vs 0.952). It is keyed to 4 sites, not to the world's cells |
| Forward quotes | `sim/forward_curve.generate_forward_price`: EWMA of past spot x seasonal shape x term premium | Backward-looking. Over a generated future it is a lagging quote, not a market expectation |
| Bid-offer | `company/trading/hedge_decision.py` BID_ASK_* 0.5% + 0.2%/yr, cap 1.5%, cited "industry knowledge" | It sits on the company side. No published source is attached |
| Fuel anchor | DESNZ *Fossil Fuel Price Assumptions 2025*, A/B/C, in `docs/market_research/scenario_spine_and_friction_anchors_2026-07-23.md` §1.3 | NBP p/therm (real 2024): 2030 = 42 / 71 / 120, 2035 = 37 / 69 / 114. Confidence H |
| Full-book run cost | `.launch_records.json`, 2016 to mid-2025 book runs of 20-24 Oct | **55-65 min, peak 7.0-7.5 GB**, on a guest of 24.0 GB (15.6 GB available at 21:01Z) |
| Forward runs of the production book | launch records, all 276 | **None has ever been launched.** Every forward cost below is a prediction |
| Checkpoint and resume | `run_phase2b._main` docstring | Absent: "the run's state is these locals, so there is nothing to save". The director asked for this to be raised "when it next costs real work" |

The earlier frames (`SYNTHETIC_FUTURES_GENERATION_FRAME.md`, `SCENARIO_SPINE_AND_TRADING_FRICTION_FRAME.md`)
built a curriculum of named stress worlds for the tournament. This is a different question: futures
nobody designed, to judge decisions that pay back over years. The machinery is reused. The framing
is not.

## 1. Horizon: 2026 to 2035, ten forward years

- **Why ten.** The levers the ruling puts after forward years pay back over years ("Payback is often
  years"). CLV is a multi-year quantity. Five years would cut the tail most of that value lives in.
  *GAP: no published payback distribution for domestic batteries or EV smart charging is in the
  knowledge layer yet. The K8 page for the levers owes it, and it could move the horizon.*
- **Why not further.** The fuel anchor is published to 2035 at named points and flat from 2040. Past
  2035 every input is the fleet and policy guess the walls warn about.
- **Where it starts.** The record ends mid-2025 (`REPORT_END = 2025-06-07`), so the forward period
  starts the next day. A forward run lives through the real record first, because nothing can
  checkpoint the book at the record's end (§5). **Fallback, if §5's probe says a run is too dear:**
  2026 to 2030, which DESNZ also anchors.

## 2. How weather and fuel are drawn, and anchored on 2016-2025

**(a) Weather: drawn, not replayed. Seeded block draws from the record, the same source day in every cell.**
- Each forward block (I propose 7 to 14 days) takes its weather from a record block. The record
  block is drawn from any record year within ±15 days of the same calendar date.
- Every cell reads the same source day, so the spatial structure between cells is the record's own,
  exactly. The seasonal shape is kept by the calendar window.
- Sequences the record never had are possible: a cold week of 2018 can follow a still week of 2021.
- **Cost: negligible.** It is the same mapping `extended_by_analogue_years` already builds, at block
  rather than year granularity. It reuses that function, and it does not need a second engine.
- **Rejected:** the AR1 engine. It is keyed to 4 sites, not to cells, and refitting it per cell is
  a world build with its own grading.
- **Named limits, both erring against us (F11):**
  - No weather outside the 2016-2025 envelope. A 1-in-50 cold winter cannot occur. A stress overlay
    is the curriculum's tool, and it is his.
  - No warming trend. *GAP: a published UK trend (UKCP18 or Met Office) is not in the knowledge
    layer. The K8 page fetches it, and states it as a range or as an explicit zero with the reason.*

**(b) Fuel: a gas path between DESNZ's low and high cases, with the record's volatility. This is his choice.**
- **The year level:** each future draws a point inside the DESNZ A to C band for each anchored year,
  interpolated between them. W8 asks for "a labelled range, not a number", and the band is that
  range.
- **The daily path around the level:** log-returns with the record's volatility and mean reversion,
  fitted on 2016-2025 NBP, crisis included because 2022 is a fact.
- **Grading:** the path model is graded on whether it reproduces the record's moments on 2016-2025.
  `sim/scenario/fidelity_check.py` exists for exactly this.
- **Why this is his:** choosing the band is choosing how hard the futures are. **I recommend the full
  A to C band, uniform**, because DESNZ itself does not weight its cases.

## 3. Wholesale formation: the existing weather chain, not the independent generator

- **Price:** `derive_price(temp, wind, cloud, day, gas)` on the drawn weather and the drawn gas path,
  with `sim/scenario/intraday_shape.py` for the half-hours.
- **Cost:** 0.29 ms per run year, so nothing beside a run of about an hour.
- **Why not the bimodal generator.** It cannot do what the ruling asks ("formed from that weather and
  fuel prices"), because its price ignores the weather.
- **Why not the full merit-order rebuild** (`sim/merit_order_reconstruction.py`, W1_6b). It is more
  faithful on ordinary days. But it needs a plant stack for 2026-2035, and every plant row past 2025
  is an unanchored constant.
- **Known error:** £24/MWh daily MAE on the record. It is published beside every forward figure.
- **The fleet path is curriculum, so his.** `sim/renewable_capacity_trend.py` holds the wind and solar
  fleet flat past 2025, and K2 says flat asserts a value we know is wrong. NESO FES has wind plus solar
  at 2.3-2.5x from 2024 to 2030 (49 GW to 113-124 GW, same research file §1.2).
  - **I recommend** the FES range as a labelled band, drawn per future like the gas level.
  - **Until he rules:** fleet held flat, stated on every forward figure.

## 4. Forward products: quoted by the world from what the market would expect, with a spread and a liquidity edge

**Products,** baseload, power and NBP gas:
- month-ahead, M+1 to M+3;
- quarter-ahead, Q+1 and Q+2;
- season-ahead, the next four seasons (Summer is Apr-Sep, Winter Oct-Mar).

Peak products come later, with time-of-use.

**The quote is the generator's conditional expectation over the delivery period**, from the state on
the trade date, with the sourced term premium (`uk_power_forward_curves_2016_2025.md` §4: 1-3% month,
3-5% quarter, 6-10% year). A market prices what it expects, not what will happen, so the gap between
quote and outcome is the forecast error the hedge programme lives with. The EWMA in
`generate_forward_price` stays as the replay-period quote, where the record supplies real prices.

**Bid-offer is quoted by the world.** The company pays it. It does not assume it.
- Today the spread is a company constant with no source attached. A real supplier is quoted a spread;
  it does not pick one.
- *GAP: the spread by tenor. Ofgem's wholesale market monitoring is the first place to look (K4,
  Ofgem first). Until it is sourced, the existing 0.5% + 0.2%/yr carries its "unsourced" origin label
  on the world side.*

**Liquidity:**
- **Beyond the four seasons:** no quote, and the hedge desk is refused with that reason. The research
  file: liquidity "thins rapidly beyond 2 years".
- **Volume impact: zero, stated as a belief.** A book of hundreds to low thousands of homes trades
  volumes a few orders of magnitude below GB traded volume, so no price impact is near-certain. That
  is stated, not omitted.

## 5. Futures per question, and the cost in memory and run time

**Design.** Paired futures: both arms of a question live through the same N futures (common random
numbers), and the book seed is fixed. That is the cheapest design that can see a decision's effect
past the noise of the future itself.
- **Start at N = 5**, the count the s14 and C30 seed intervals were read on this week.
- Then size N from the paired spread the first question measures (R5).

**Cost, filed as predictions before the probe (R7, R9).** At 55-65 min and 7.0-7.5 GB for 2016 to
mid-2025:

| | Predicted |
|---|---|
| One run, 2016-2035 | **2-3 h**. Per-year cost rises as the book grows |
| Peak memory | **9-15 GB**. Unknown whether memory grows with years: this is the number most likely to be wrong |
| Concurrency at 15.6 GB available | 1, possibly 2 |
| One question, 5 futures x 2 arms | **20-30 machine-hours serial, about 1 to 1.5 days.** Machine time costs no usage points |

**The probe comes first:** one 2016-2027 forward run of the production book, about 1.5 h. It measures
the marginal minutes and MB per forward year. If a question costs more than about 20 machine-hours,
that is the "real work" the director asked to have raised for **checkpoint and resume**. One 2016-2025
book state forked into N futures would cut each run to the forward years alone, about half. It is a
refactor of the 3,400-line runner, size unknown, and I do not recommend it until the probe says so.

## 6. How the supplier stays blind to each future (W1)

What crosses is what a supplier sees in a future: days as they pass, and quotes. Nothing else.

- **What the company never sees:**
  - the seed, the drawn DESNZ level or fleet path, the block map, the generator parameters, and the
    future's name;
  - the replay-period `weather_analogue_years` provenance. It stays in the world's run output.
- **Forecast error is the wall on the future.** The company prices from quotes (a conditional
  expectation) and from its own forecasts. The realised path differs from both, by construction.
- **Records:** every record carries `data_regime: synthetic` past the record's end (the epistemic-wall
  rule). Reporting reads that label and nothing more.
- **The control, keyed to the property:** two futures that share a prefix must produce byte-identical
  company decisions until the first day they differ. This one leg fails on any leak of the future,
  through any channel, without enumerating channels. It is mutation-proven by planting a one-day
  look-ahead.

## 7. Cost estimate (the estimate-the-cost steer)

Classes and rates are from `tools/work_cost_estimate.py`: 0.19-0.49 points per landed session, pooled
median 0.27, 531 sessions over 14 days. **Sessions per piece are my estimate.** Sessions per level step
are not yet measured (that steer's item 3), so the range is wide on purpose.

| Piece | Class | Sessions | Points |
|---|---|---|---|
| K8 page: forward weather, fuel band, fleet band, forward products, bid-offer (fetches UKCP, Ofgem spreads) | knowledge_page | 2-4 | 0.4-2.0 |
| Block-drawn weather (extends `extended_by_analogue_years`) + control | world_build | 2-4 | 0.4-2.0 |
| Gas path in the DESNZ band, graded on 2016-2025 moments | world_build | 2-4 | 0.4-2.0 |
| Chain price on drawn weather and gas, half-hourly shape, `data_regime` | world_build | 3-5 | 0.6-2.5 |
| Forward quotes M/Q/S, bid-offer and liquidity edge, through the seam; prefix-blindness control | world_build | 4-8 | 0.8-3.9 |
| The run-cost probe (§5) | grading_run | 1-2 | 0.2-1.0 |
| First pre-registered forward question, N=5 paired | grading_run | 2-4 | 0.4-2.0 |
| **Total** | | **16-31** | **3.2-15.4 points**, central about 6 (at 0.27) |

- The week holds 100 points, so the whole is up to 15% of a week. **Flagged under the steer's 10%
  rule:** split, as the table already is. No single piece exceeds 4 points at the high end.
- Machine time (§5) costs no points, but it competes for memory with every other book run.
- **Not in the total:** checkpoint and resume, raised only if the probe shows it is needed.

## 8. What I recommend, for his yes or change

1. **Horizon 2026-2035.** Fallback 2026-2030 if the probe says a run costs more than 3 h.
2. **Weather** by seeded block draws from the record, the same source day in every cell. No trend
   until the K8 page sources one.
3. **Gas** in the full DESNZ A to C band, uniform, with the record's volatility. *His: curriculum.*
4. **Price** from the existing weather chain. **Fleet** in the NESO FES band, held flat until he
   rules. *His: curriculum.*
5. **Forward products** M+1..3, Q+1..2 and S+1..4 baseload power and gas, quoted at the conditional
   expectation plus the sourced term premium. The world quotes the bid-offer, and nothing is quoted
   past two years.
6. **N = 5 paired futures per question**, re-sized from the first question's spread, after a one-run
   cost probe. Checkpointing is raised only if the probe prices a question above about 20 machine-hours.

**Holding position until he answers:** nothing forward-years is built. The K8 page (§7 row 1) and the
EP16 anchoring the ruling allows in parallel (item 4) can proceed, because both are knowledge and
grading on the record, not forward runs. **What would change this:** the probe's memory figure; a
published payback distribution that moves the horizon; or his choice of band.
