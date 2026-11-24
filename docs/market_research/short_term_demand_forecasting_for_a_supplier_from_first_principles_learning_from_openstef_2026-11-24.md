# Short-term demand forecasting for a supplier, from first principles, learning from OpenSTEF

**Knowledge:** hedging-forward-market

*Worker tick, 2026-11-24. This is the K8 page that the director's steer of 24 Nov asks for first
(`docs/staging/advisor/done/DIRECTOR_STEER_REBUILD_THE_COMPANY_DEMAND_FORECAST_FROM_FIRST_PRINCIPLES_LEARNING_FROM_OPENSTEF_2026-11-24.md`).
It extends the queued forecast benchmark (13 Nov steer, amended 16 Nov: judged by hedge and imbalance cost).
OpenSTEF is reference reading only. Nothing from its code is copied here or anywhere in the repository
(MPL-2.0 is file-level copyleft, and this repository is public).*

## 0. Which decision the forecast feeds today (read from code, not run)

Measure the decision before the forecaster. The steer assumes a short-term (hours-to-days) forecast
whose error costs money. In the code at `origin/main` on 24 Nov there is no such decision yet:

- **The hedge is sized per customer term, on an annual figure.** `simulation/run_phase2b.py` calls
  `hedge_desk.decide_term_hedge(volume_kwh=eac_kwh, ...)`, and `company/trading/hedge_desk.py`
  computes the notional as `volume_kwh / 1000 × hedge_fraction`. The demand input is the customer's
  EAC, the estimated annual consumption, for the whole term. The unhedged share settles at spot.
- **No half-hourly position is taken.** `company/market/imbalance_ledger.py` has no caller anywhere
  in `company/`, `simulation/` or `saas/`. Nothing in the run forecasts tomorrow's half-hours, buys
  against them, and pays imbalance on the miss.
- **The company has no weather-forecast feed.** `EP15_forecast_feed` is at level 0. Its own record
  says a forecast feed is "the ONE legitimate channel through which future-dated data crosses the
  wall" and asks for the leak test to be built before the feed. `B3_published_forecast_error_horizons`
  (also L0) measures the error such a feed would carry. Its evidence is
  `WEATHER_FORECAST_ERROR_BY_HORIZON.md` and `published_forecast_error_by_horizon_neso_2026-11-21.md`.

**So:** a short-term technique cannot yet lower hedge or imbalance cost, because no decision reads
its output. Each technique below is therefore stated twice: at the half-hourly scale OpenSTEF works
at, and at the term scale the hedge actually uses.

**A fact for whoever wires the imbalance ledger.** Its docstring prices a long position at SBP and a
short one at SSP, as two prices. GB has had a single imbalance price since BSC modification P305
(5 Nov 2015), so across the whole 2016–2025 run SBP equals SSP. In-tree source:
`a_new_accounts_first_months_2026-10-30.md` row 310, quoting Elexon's *Imbalance pricing* page.
The ledger is unwired, so nothing is wrong in any output today. Two prices would be wrong the day
it is wired.

## 1. What a GB domestic supplier actually forecasts, 2016–2025

This is practitioner ground, and the published record supports it. A domestic supplier's
half-hourly settled volume is mostly **not** its customers' metered half-hours:

- Until MHHS, every non-half-hourly domestic premise settles on Elexon profiles. Class 1 is
  domestic unrestricted; class 2 is domestic Economy 7. An annual quantity (EAC or Annualised
  Advance) is spread across half-hours by regression coefficients. Source:
  `smart_meters_and_half_hourly_settlement_2026-10-25.md` §2, and Elexon's profiling page. MHHS
  migration starts at M11 (22 Oct 2025), after the run ends.
- **The SVAA computes the daily profile coefficients after the day, from outturn temperatures**
  supplied by the Met Office for each GSP group. The regression also uses sunset time and day-type
  dummies. The coefficients themselves are refreshed twice a year from about 2,500 sample sites.
  Source: Elexon, <https://www.elexon.co.uk/bsc/settlement/profiling/>, read 24 Nov. The page was
  read in part. The guidance note's body, which defines Noon Effective Temperature, could not be
  fetched. **GAP:** the NET definition and the special-day rules.
- **GSP Group Correction** scales each supplier's allocated volumes, per period, so the group's
  total matches the energy entering it. **GAP:** the formula. Elexon's guidance note was not read.
- **Actual reads arrive late.** In-tree (`elexon_settlement_run_timetable_verified.md`): SF runs
  about one month after the day; NHH energy on actual data is about 30% at R1 (two months), 60% at
  R2, 80% at R3 and 97% at RF (about 28 months).

**What this means for the forecaster.** For a profiled book, the settled half-hourly volume is
roughly ∑ EAC × profile coefficient(outturn temperature, sunset, day type) × GSP correction. A
supplier forecasting it day-ahead is mostly forecasting Elexon's own regression with a forecast of
the temperature. The supplier's own "demand lags" at day-ahead are lags of an allocation, available
only at SF, a month late. Its own smart half-hourly reads matter only for half-hourly-settled
customers.

**GAP:** how quickly a supplier receives DCC half-hourly reads for its smart customers, and what
share of a 2016–2025 domestic book was half-hourly settled. The smart-meter page has penetration
figures, not settlement shares.

## 2. The techniques, one at a time

Each entry has five parts: what OpenSTEF does, why it works, what we can observe, what is GAP, and
the term-scale analogue. Unless marked, the OpenSTEF facts come from its v4 documentation, read
24 Nov:

- <https://openstef.github.io/openstef/user_guide/guides/feature_engineering_tutorial.html>
- `.../probabilistic_forecasting.html`
- `.../concepts/component_splitting.html`
- `.../concepts/beam.html`

The repository (<https://github.com/OpenSTEF/openstef>) is an LF Energy project under MPL-2.0. Its
v4.0.0 is "a complete architectural refactor" into `openstef-core`, `-models`, `-beam`, `-meta` and
`-foundation-models`. The advisor believed it came from Alliander. No page read names Alliander,
though the sample loader is `load_liander_dataset`. **Unconfirmed.**

### 2.1 Lags

- **OpenSTEF.** `LagsAdder` drops every lag shorter than the lead time. Its documented example uses
  a 7-day lag. `RollingAggregatesAdder` adds a rolling mean, median, min or max (the example uses
  24 h mean and max), and it too respects the horizon. **Unconfirmed:** the default lag set and what
  "trivial lags" contains, because `lags_adder.py` was not read. The advisor's "1 day and 7 days"
  is plausible but not verified.
- **Why it works.** Demand is strongly autocorrelated at the daily and weekly periods. A lag carries
  everything slow about the load that no feature names.
- **What we can observe.** At half-hourly scale, the book's settled volumes are held from SF, about
  a month after the day, so a 1-day or 7-day lag of *settled* volume does not exist at day-ahead.
  The lag that exists is the supplier's own record of what it allocated or metered, at its real
  delay. At term scale, the lags are last year's settled Annualised Advances and the EAC history.
  These are what `how_far_a_settled_eac_sits_from_next_years_use.md` measures.
- **GAP:** the supplier-side latency of DCC half-hourly data (see §1).

### 2.2 Calendar

- **OpenSTEF.** Sine and cosine encodings for time of day, day of week, month and season. Weekday
  and weekend flags. Public holidays by country code, with bridge days. School holidays from the
  OpenHolidays API, fetched once at training and stored so that forecasting never calls out.
  **Unconfirmed:** how it handles clock changes; its example data is in UTC.
- **Why it works.** Behaviour follows the calendar, and the calendar is known in advance without
  error, so it is the cheapest honest input.
- **What we can observe.** Everything, in advance: bank holidays, school terms and clock-change days
  (46 and 50 settlement periods). Elexon's profiles already carry day-type dummies, so for a
  profiled book this mostly re-learns the allocation.
- **Wall note.** The company may not open a socket (W6). Any calendar is committed data, read the
  way OpenSTEF reads its stored export.

### 2.3 Weather

- **OpenSTEF.** Wind speed is scaled to hub height and passed through a sigmoid power curve. DNI
  and GTI come from horizontal radiation via solar geometry. Dew point, air density and vapour
  pressure are derived, plus a daylight feature. No heating-degree transform is listed in its
  `weather_domain`.
- **Why it works.** Raw weather variables relate to load non-linearly. A physics transform hands
  the model the shape instead of making it learn one.
- **What matters for domestic demand.** Temperature, for heating, dominates. Radiation matters only
  for PV-holding homes. Wind matters for a supplier's generation, not for household load. This is
  exactly what Elexon's regression uses (temperature, sunset).
- **What we can observe.** Only a **published forecast as it stood at the decision time**. The
  company has none (EP15, L0). Beyond roughly two weeks, weather forecasts have little skill, so at
  term scale the honest input is climatology: a degree-day normal, not a forecast.
- **The trap.** Training or backtesting on outturn weather flatters every model and here breaches
  the wall. Settlement itself uses outturn temperature after the day (§1). That is the world's
  truth, which the forecaster must not see at decision time.
- **Blocked on** EP15's leak test and feed. This step cannot start before them.

### 2.4 Quantiles (probabilistic forecasts)

- **OpenSTEF.** One model outputs all quantiles at once, not one model per quantile:
  - XGBoost uses a multi-output pinball objective;
  - GBLinear uses `reg:quantileerror`;
  - LightGBM uses a multi-quantile regressor.

  The documented example asks for P5, P10, P30, P50, P70, P90 and P95, with P50 as the point
  forecast. Post-processing sorts the quantiles and calibrates them, isotonic or conformal.
  Evaluation reports pinball loss, coverage, sharpness and calibration error. BEAM adds relative
  CRPS. **Unconfirmed:** whether that quantile set is the default.
- **Why it works.** A hedge is sized against the band, not the centre. An over-confident band
  under-prices the volume risk.
- **What we can observe.** Our own forecast errors against settled outturn, at the real delay.
- **Term-scale analogue.** This is where the technique bites first for us. `decide_term_hedge`'s VaR
  uses price volatility only; volume uncertainty does not enter it. A calibrated band on term volume
  is a candidate input. **GAP:** no decision consumes a volume band today, so this step must name
  the consumer before it can be scored.

### 2.5 Splitting net demand into components

- **OpenSTEF.** Splitting runs **after** the forecast. It divides total load into solar, wind and
  other, with the parts summing to the total. Its documentation says it "does **not** improve
  forecast accuracy". The linear splitter ships pre-trained ("from OpenSTEF V3.4.24"), driven by
  radiation and 100 m wind speed.
- **Why it might still matter.** Explanation, and hedging by component: PV export and import
  respond to different prices.
- **What we can observe.** Asset data a supplier legitimately holds: export registrations (FiT,
  SEG), declared EVs and heat pumps, and tariff choice. These depend on the 10 Nov asset-range steer.
- **Order.** Last. A cost gain from this step would contradict the source's own statement, so treat
  it as suspect until explained.

### 2.6 Input validation

- **OpenSTEF.** A completeness check refuses to train below a threshold; the example uses 0.8, and
  the default is **unconfirmed**. A flatliner check refuses a stuck series; a model summary reports
  a 6-hour threshold, **unconfirmed**. An outlier handler learns bounds at fit time (the example
  clips at 3σ). The imputer fills features but never the target.
- **Why it works.** A model trained on a stuck meter learns a constant. Imputing the target invents
  the answer being scored.
- **What we can observe.** A stuck or faulty meter is a real supplier observable. The world's model
  of wrong reads is `what_a_wrong_meter_read_is_and_how_often_the_record_says_it_happens_2026-11-12.md`.
- **Order.** Alongside the first step that trains on the company's own volumes (lags).

### 2.7 Point-in-time backtesting (not on the advisor's list; the most important to learn)

- **OpenSTEF.** BEAM versions every input series by `available_at`, so a backtest sees only values
  published before the simulated now. This explicitly covers weather-forecast revisions and late
  meter readings. Training and prediction are scheduled events, and results are scored by lead
  time.
- **For us.** This is the steer's leakage rule, and the wall, written as a data structure. Our
  existing tool is `PointInTimeView` over the bitemporal log (`run_phase2b.py` builds the price
  history for `decide_term_hedge` through it). The test the steer asks for is:
  - outturn weather reaching the forecaster fails;
  - demand not yet available reaching the forecaster fails.

  The natural form of that test is "every input row's `available_at` ≤ decision time", which can
  fail by construction. It comes before any arm is scored.

## 3. The wider literature

These were not re-read this tick, so they are cited as pointers, not evidence.

- **GEFCom2012 and GEFCom2014** (Hong, Pinson, Fan and others, *International Journal of
  Forecasting*, 2014 and 2016). GEFCom2014 moved load forecasting to probabilistic scoring by
  pinball loss.
- **Hong and Fan, "Probabilistic electric load forecasting: a tutorial review"** (*IJF* 2016).
- **The "vanilla" benchmark** (Hong, 2010) regresses load on a temperature polynomial and
  hour-by-weekday and month terms. It is the standard yardstick that every technique above must
  beat, and it is close to Elexon's own profile regression.

**GAP:** a read of these three, to grade them, before the first arm is scored.

## 4. What the page argues about the order

The steer's order is lags, calendar, weather, quantiles, component split, with validation alongside.
It holds "unless the page argues otherwise". This page argues three changes. None changes his
ruling; each follows from §0.

1. **Step 0: name the consumer.** Each arm must state which decision reads it: the term hedge's
   volume (EAC), or a day-ahead position that does not exist yet. Scored at term scale today, a
   half-hourly technique has nothing to change, and "it did not lower cost" would be recorded
   against the technique when it is really a fact about the decision.
2. **Weather waits for EP15.** Its feed and leak test come first, as EP15's own record says. Until
   then the honest weather input at term scale is climatology.
3. **Quantiles before weather at term scale.** A volume band is the one technique that has an
   immediate consumer: the VaR sizing, which today ignores volume risk.

**Predictions, filed before any run.**

- (a) Lags and calendar on the term volume will not beat seasonal-naive on hedge cost by more than
  the forward sample's bound. The world's term demand is EAC-driven, and EAC is already a lag.
- (b) The component split will show no accuracy gain, per its own source.
- (c) The leakage test will find at least one outturn-weather route into some existing demand
  estimate. `SEAT_FINDING_SEVERAL_CONSUMPTION_FORECASTS_A_WALL_LEAK_IN_HEDGE_VOLUME...` (11 Oct)
  found one in hedge volume before.

All three are falsifiable by the benchmark's first arms.

## 5. GAPs, in one list

- The default lag set and the meaning of "trivial lags" (OpenSTEF's `lags_adder.py`).
- The default quantiles, flatliner threshold and completeness threshold.
- How OpenSTEF handles clock changes.
- The Noon Effective Temperature definition, Elexon's special-day rules and the GSP Group
  Correction formula.
- Supplier-side DCC half-hourly latency, and the half-hourly-settled share of the domestic book,
  2016–2025.
- Grading of the GEFCom papers, Hong and Fan, and the vanilla benchmark.
- Whether OpenSTEF originated at Alliander.
