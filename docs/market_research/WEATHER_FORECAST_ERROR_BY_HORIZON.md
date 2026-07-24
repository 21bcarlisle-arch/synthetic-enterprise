# Weather/System Forecast Error by Horizon — σ(horizon)

**Purpose:** empirical measurement of UK wind and demand forecast error as a function of lead
time, pulled directly from real published Elexon settlement/forecast data. This is the
prerequisite gather step for `DIRECTOR_STEER_WEATHER_SIM_PURPOSE_2026-07-23`
("gather → correlate → select → simulate — do not pick simulation variables by intuition").
This document GATHERS AND MEASURES ONLY. It decides no simulation variable and tunes no
baseline/curriculum parameter (R13). No simulator or company code was touched; nothing was
committed.

**date**: 2026-07-24
**domain**: weather
**pulled**: 2026-07-24, live Elexon Insights Solution API (network confirmed up this tick,
`data.elexon.co.uk` HTTP 200)

---

## 1. Working endpoints (provenance)

All endpoints below returned HTTP 200 and were probed today. Several sibling paths in the
task brief 404'd — the *working* forms are recorded here so the next tick doesn't have to
re-discover them.

| Series | Working endpoint | Notes |
|---|---|---|
| Wind generation **forecast** | `GET /bmrs/api/v1/datasets/WINDFOR?publishDateTimeFrom=...&publishDateTimeTo=...` | dataset `WINDFOR`. `settlementDateFrom/To` and bare `from/to` do **not** filter this endpoint (returns latest window regardless) — must use `publishDateTimeFrom/To`. Published ~8x/day (observed publish times e.g. 02:30, 04:30, 07:30, 09:30, 11:30, 15:30, 18:30, 22:30 UTC), each publish carries **hourly** resolution generation MW out to **~73 hours ahead**. |
| Wind generation **actual** | `GET /bmrs/api/v1/datasets/FUELINST?publishDateTimeFrom=...&publishDateTimeTo=...` filtered `fuelType=="WIND"` | dataset `FUELINST`, 5-minute resolution, BM-unit-metered generation only. `/generation/outturn/summary` and `/generation/outturn` (also FUELINST-backed) both **ignore** `settlementDateFrom/To` and only return a rolling ~24-48h "latest" window — not usable for historical pulls; had to go through `/datasets/FUELINST` directly with `publishDateTimeFrom/To` instead. |
| Demand **forecast** (day-ahead) | `GET /bmrs/api/v1/forecast/demand/day-ahead/history?publishTime=<ISO>` | datasets `NDF` (National Demand Forecast) + `TSDF` (Transmission System Demand Forecast). Snaps to nearest actual publish (~once/day, observed ~22:46–22:48 UTC), returns 30-min resolution out to ~24–30h ahead. The non-`/history` form (`/forecast/demand/day-ahead`) ignores date filters and only returns the live current forecast — not usable historically. |
| Demand **actual** | `GET /bmrs/api/v1/demand/outturn?settlementDateFrom=...&settlementDateTo=...` | datasets `INDO` (Initial National Demand Outturn) + `ITSDO`. This one **does** correctly respect `settlementDateFrom/To` (unlike the generation-outturn family above) — 30-min resolution. |

404'd / not usable as named in the brief: `/forecast/generation/wind/day-ahead`,
`/forecast/generation/wind-and-solar/day-ahead` (+ `/history`), `/forecast/wind/day-ahead`,
`/datasets/B1440`, `/forecast/demand/national/day-ahead*`, `/generation/actual/per-type*`.
NESO CKAN was not needed this tick — Elexon alone covered both variables with usable horizon
spread.

## 2. Sample windows pulled

Two independent 7–8 day windows, chosen for seasonal contrast (winter vs spring, per the
"high-volatility month" instruction, plus a cross-check to avoid a single-week fluke):

- **Week 1**: 2026-01-01 to 2026-01-08 (winter) — WINDFOR 4,088 forecast rows, FUELINST-WIND
  3,462 actual rows (5-min), demand forecast 480 rows, demand outturn 384 rows (settlement
  periods).
- **Week 2**: 2026-03-15 to 2026-03-22 (spring) — identical row counts (WINDFOR 4,088,
  FUELINST-WIND 3,462, demand forecast 480, demand outturn 384).

Matched forecast→actual pairs (nearest-timestamp join, ≤1h tolerance):
- Wind: 3,248 matched pairs per week (6,496 total).
- Demand: 468 matched pairs per week (936 total).

Compact per-horizon-bucket CSVs (not the raw firehose) saved alongside this document:
- `docs/market_research/weather_forecast_error_wind_by_horizon.csv`
- `docs/market_research/weather_forecast_error_demand_by_horizon.csv`

---

## 3. σ(horizon) — Demand (National Demand Forecast vs INDO outturn)

**confidence: M** (cross-referenced two independent weeks, consistent order of magnitude)

| Horizon (h) | Week1 (Jan) MAE | Week1 stdev(err) | Week1 MAE% | Week2 (Mar) MAE | Week2 stdev(err) | Week2 MAE% |
|---|---|---|---|---|---|---|
| 0–6 | 607 MW | 640 MW | 2.27% | 498 MW | 616 MW | 2.11% |
| 6–12 | 552 MW | 651 MW | 1.73% | 1,060 MW | 1,426 MW | 4.19% |
| 12–24 | 836 MW | 1,018 MW | 2.22% | 858 MW | 1,121 MW | 3.05% |
| 24–48 | 549 MW | 589 MW | 2.02% | 548 MW | 663 MW | 2.31% |
| 48–73 | no data | no data | — | no data | no data | — |

**Finding:** demand day-ahead forecast error is small (MAE ≈ 1.7–4.2% of mean national
demand, stdev(err) ≈ 590–1,430 MW on a mean demand of ~25,000–29,000 MW) and **shows no clean
monotonic growth with horizon in this 2-week sample** — the 6–12h bucket in week 2 is
actually the noisiest, likely a single volatile day (weather front) dominating a small-n
bucket (n=96) rather than a horizon effect. Bias is small and sign-flips between weeks
(no persistent over/under-forecast). **This is a usable, well-behaved signal** but the
sample is too short (2 weeks) to fit a smooth σ(horizon) curve with confidence — recommend
a longer multi-month pull (the endpoint is proven to work; it's a volume question, not a
discovery question) before this feeds a BUILD decision.

**Coverage gap, honestly flagged:** demand day-ahead forecast is only published ~once/day
covering ~24–30h ahead, so the 48–73h bucket has **no data** — Elexon's day-ahead demand
forecast simply does not reach that far. A weather-layer horizon beyond ~30h for demand
would need a different (e.g. NESO CKAN, or intraday-updated) series — named as an ungathered
horizon, not fabricated.

## 4. σ(horizon) — Wind (WINDFOR forecast vs FUELINST metered outturn)

**confidence: L→M** (two weeks agree on the *shape* of the anomaly below, but the headline
numbers are confounded — see caveat)

| Horizon (h) | Week1 (Jan) MAE | Week1 bias | Week1 MAE% | Week2 (Mar) MAE | Week2 bias | Week2 MAE% |
|---|---|---|---|---|---|---|
| 0–6 | 1,857 MW | +1,063 MW | 14.6% | 2,007 MW | +1,918 MW | 24.9% |
| 6–12 | 1,884 MW | +1,211 MW | 15.2% | 2,008 MW | +1,858 MW | 25.3% |
| 12–24 | 1,933 MW | +1,563 MW | 16.7% | 1,990 MW | +1,857 MW | 27.0% |
| 24–48 | 1,642 MW | +1,256 MW | 15.0% | 1,945 MW | +1,792 MW | 32.0% |
| 48–73 | 1,405 MW | +256 MW | 12.9% | 1,468 MW | +1,227 MW | 26.3% |

**Finding — flagged, not resolved this tick:** the wind comparison is **confounded by an
apparent metering-scope mismatch**, not a clean forecast-error curve. Evidence
(observed-with-evidence): (a) there is a large, *persistent, same-sign* bias in every
horizon bucket in both weeks (WINDFOR forecast running +250 to +1,918 MW **above** FUELINST
actual — i.e. the forecast is not centred on the outturn at any lead time, including the
shortest 0–6h bucket where a competent forecast should be near-unbiased); (b) MAE-as-%-of-mean
does **not** grow monotonically with horizon the way genuine forecast skill degradation would
predict — it is closer to flat/noisy (12.9–16.7% in week 1, 24.9–32.0% in week 2), and the
*longest*-horizon bucket (48–73h) is not the worst in either week.

**Inferred (not confirmed from Elexon documentation this tick):** WINDFOR is understood
(NESO/Elexon publish it as a system-wide balancing forecast) to forecast **total GB wind
output including embedded/distribution-connected wind capacity**, whereas `FUELINST`
`fuelType=WIND` is **BM-unit-metered generation only** (transmission-connected wind reporting
into settlement) — embedded wind (rooftop/smaller distribution-connected turbines, roughly
in the right ballpark of the observed 15–25% of mean-actual bias here) is not separately
metered in real time and is excluded from FUELINST. If correct, the bias is a **definitional
scope gap between the two series**, not evidence that WINDFOR under/over-predicts physical
wind output. This inference is plausible and internally consistent (bias scales with total
wind output as embedded capacity would) but is **not verified against an Elexon/NESO
methodology document** — flagged as a gap, not asserted as fact.

**Action warranted (FRAME, not BUILD):** before wind σ(horizon) can be trusted as a weather-
engine calibration input, the next DISCOVER pass should either (a) find the correct
outturn comparator for WINDFOR's declared scope (NESO may publish a "wind forecast accuracy"
series already computed on a like-for-like basis), or (b) demean each bucket by its own
mean bias and treat `stdev(err)` (which is far more horizon-stable: 1,570–2,023 MW week 1,
1,623–1,755 MW week 2 — genuinely close to flat across 0–73h in both weeks) as the safer
volatility signal rather than raw MAE. Do not feed the raw biased MAE curve into a simulation
variable.

---

## 5. Tail / worst-cell discipline

Largest single-observation absolute errors found (not just averages), per R12/judge-on-tail
discipline:

- Wind, week 1, 24–48h bucket: forecast 9,547 MW vs actual 3,494 MW (**6,053 MW** absolute
  error, forecast >2.7x actual) — a genuine large miss, not explained by the scope-bias
  alone (bias direction here is forecast-too-high, consistent with the systematic offset,
  but the magnitude is a real outlier worth flagging for any tail-risk-sensitive downstream
  use, e.g. imbalance cost exposure).
- Demand, week 2, 12–24h bucket: worst absolute error 2,862 MW on a ~26,000 MW mean demand
  (~11%) — the single largest demand miss found in either week, sitting inside the bucket
  that also had the highest stdev(err), consistent with one volatile weather event dominating
  a still-thin sample.

Both weeks' worst cells are in the **12–48h range**, not at the extremes (neither shortest
nor longest horizon) — again inconsistent with a simple "error grows linearly with lead time"
model; more data would be needed to say whether this is a genuine hump or small-sample noise.

---

## 6. Downstream FRAME (named, not executed)

Per the task brief, the next drawable item is the **§2.2 correlate/select step**: given the
gathered σ(horizon) data above (and the wind scope-confound flag), judge candidate weather/
system variables (wind forecast error, demand forecast error, and — ungathered this tick —
any temperature/solar forecast error series) on **tail explanatory power and parsimony**
before any variable is selected for the weather-engine BUILD. This step is **pre-BUILD** and
is explicitly NOT executed here — it requires (a) resolving the wind scope-confound above,
and (b) a longer sample (weeks not months minimum) to distinguish genuine horizon-growth from
single-week noise, both named as prerequisites rather than worked around.

---

## 7. Confirmation

- No simulation code (`sim/`, `simulation/`, `company/`, `saas/`) was read or touched.
- No simulation variable was selected, tuned, or calibrated — this document measures and
  flags only.
- Nothing was committed. Files written: this document, the two CSVs named in §2, and (pending)
  an `ASSUMPTIONS.md` entry.
