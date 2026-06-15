# Forward curve overpricing — root cause and proposed fix

**Status: propose-before-build (REPORTING_BACKLOG item 16).** Recalibrating
this changes the price environment the Phase 5c hedging mandate was tuned
against, so this is a proposal, not a build, pending Rich's steer.

## Rich's framing vs what the data shows

Rich's hypothesis was that forwards trade at a 5-15% premium to realised spot
in normal conditions (per UK power literature), with the premium compressing
during the 2021-22 crisis — and that our ~116% average premium is a
crisis-specific distortion.

The data says otherwise. I computed `generate_forward_price()`'s output vs
the realised 12-month-forward mean SSP for every Jan-1/Jul-1 from 2016 to
2024 (18 points, using the real Elexon SSP history,
`sim.system_prices_history`):

```
2016-01-01: fwd= 120.49  realized_12m=  39.37  premium= 206.1%
2016-07-01: fwd=  68.81  realized_12m=  43.23  premium=  59.2%
2017-01-01: fwd= 151.62  realized_12m=  44.27  premium= 242.5%
2017-07-01: fwd=  99.88  realized_12m=  49.52  premium= 101.7%
2018-01-01: fwd=  80.90  realized_12m=  57.35  premium=  41.1%
2018-07-01: fwd=  79.37  realized_12m=  53.35  premium=  48.8%
2019-01-01: fwd=  95.24  realized_12m=  42.00  premium= 126.8%
2019-07-01: fwd=  70.68  realized_12m=  33.36  premium= 111.9%
2020-01-01: fwd=  71.74  realized_12m=  34.96  premium= 105.2%
2020-07-01: fwd=  51.01  realized_12m=  54.87  premium=  -7.0%
2021-01-01: fwd= 104.54  realized_12m= 113.29  premium=  -7.7%
2021-07-01: fwd= 169.91  realized_12m= 166.05  premium=   2.3%
2022-01-01: fwd= 394.97  realized_12m= 200.06  premium=  97.4%
2022-07-01: fwd= 253.49  realized_12m= 167.88  premium=  51.0%
2023-01-01: fwd= 368.11  realized_12m=  94.57  premium= 289.3%
2023-07-01: fwd= 149.37  realized_12m=  71.96  premium= 107.6%
2024-01-01: fwd= 158.03  realized_12m=  71.28  premium= 121.7%
2024-07-01: fwd= 118.30  realized_12m=  82.64  premium=  43.2%
```

The systematic 40-290% overpricing is pervasive across nearly the entire
2016-2024 window — it is **not** a crisis artefact. The only period with
realistic (near-zero/negative) premiums is **2020-07 to 2021-07**, which is
actually the *anomaly*: that's the run-up into the 2021-22 crisis, when
trailing-90-day prices happened to sit close to where the market was about to
go. Everywhere else, the model overprices.

## Root cause

`sim/forward_curve.py:generate_forward_price()`:

```python
base_price = mean(SSP over 90-day lookback)
volatility_premium = pstdev(SSP over 90-day lookback) * risk_factor  # risk_factor=1.2
forward_price = (base_price + volatility_premium) * seasonal_multiplier  # ~1.05
```

`system_price_records` is **half-hourly settlement-period data** (48 records
per day). `statistics.pstdev()` over this is the standard deviation of
*intraday* prices — which mixes in the normal day/night price spread (SSP
routinely swings from ~£20 overnight to ~£150-300+ at evening peak), not
year-ahead price *uncertainty*.

Verified directly for the 2016-01-01 lookback window (90 days, 2,641
half-hourly records, 56 days):

```
mean (half-hourly):        38.86
pstdev (half-hourly):      63.24   <- what the code uses
pstdev (daily means):      14.81   <- what a "year-ahead uncertainty" sigma should look like
```

`forward_base = 38.86 + 1.2*63.24 = 114.76`, `* 1.05 seasonal = 120.5` —
matches the observed `fwd=120.49` exactly. The intraday-volatility sigma is
**4.3x** the day-to-day sigma, and because `risk_factor=1.2` multiplies it
before adding to base, the "volatility premium" term alone is often *larger
than the base price itself*. That single term is the dominant driver of the
overpricing — not the seasonal multiplier (which is genuinely small, ~1.05
for any 12-month contract since it always spans 6 winter + 6 summer months),
and not the weather-sensitivity multiplier (capped at 1.10, applied to <half
the contracts).

## Decomposition across all 18 points

Re-deriving `base_90d` and `sigma_90d` from **daily-mean** SSP (not
half-hourly) for the same 18 dates:

```
date        base90d  sigma90d(daily)  1.2*sigma  base+1.2sigma  realized_12m  base/realized
2016-01-01    38.65       14.81          17.77        56.41          39.37        0.98
2016-07-01    34.69        9.84          11.81        46.49          43.23        0.80
2017-01-01    51.58       29.26          35.11        86.69          44.27        1.17
2017-07-01    40.58       18.79          22.54        63.12          49.52        0.82
2018-01-01    49.70       10.17          12.20        61.90          57.35        0.87
2018-07-01    50.38        9.36          11.23        61.61          53.35        0.94
2019-01-01    62.21        7.67           9.20        71.42          42.00        1.48
2019-07-01    41.24       10.20          12.23        53.47          33.36        1.24
2020-01-01    39.93        9.54          11.45        51.38          34.96        1.14
2020-07-01    24.63        9.81          11.77        36.40          54.87        0.45
2021-01-01    47.69       16.61          19.94        67.63         113.29        0.42
2021-07-01    75.01       27.87          33.44       108.45         166.05        0.45
2022-01-01   188.76       66.58          79.89       268.65         200.06        0.94
2022-07-01   151.02       45.26          54.31       205.33         167.88        0.90
2023-01-01   174.49      111.51         133.81       308.30          94.57        1.85
2023-07-01    87.26       23.29          27.95       115.21          71.96        1.21
2024-01-01    83.42       29.40          35.28       118.69          71.28        1.17
2024-07-01    63.55       22.27          26.72        90.27          82.64        0.77
```

## What a fix would change, and by how much

**Phase A (mechanical, low-risk): compute `volatility_premium` from
daily-mean SSP, not half-hourly records.** Re-running the premium calculation
with `(base_90d + 1.2*sigma_90d_daily) * 1.05` against realised:

```
2016-01-01: +50.4%   2016-07-01: +12.9%   2017-01-01: +105.6%  2017-07-01: +33.8%
2018-01-01: +13.3%   2018-07-01: +21.3%   2019-01-01: +78.5%   2019-07-01: +68.3%
2020-01-01: +54.3%   2020-07-01: -30.4%   2021-01-01: -37.3%   2021-07-01: -31.4%
2022-01-01: +41.0%   2022-07-01: +28.4%   2023-01-01: +242.3%  2023-07-01: +68.1%
2024-01-01: +74.9%   2024-07-01: +14.7%
```

Average premium drops from **~116% to ~45%** — a big improvement from one
mechanical change (use the right sigma for "year-ahead uncertainty"), and the
sign-changing/backwardation behaviour Rich asked about **emerges naturally**:
2020-07 to 2021-07 already go negative because the trailing-90-day base sits
below where the market was about to move (the genuine run-up-to-crisis
mean-reversion mismatch) — no special-casing needed.

**Phase B (recalibration, needs sign-off): reduce `risk_factor` from 1.2.**
Even with daily-mean sigma, the volatility-premium term alone contributes an
average of ~42% to the premium (ranging 18.5% to 149% across the 18 points).
To land the *average* premium in the 5-15% literature range, `risk_factor`
would need to drop to roughly **0.25-0.3** (from 1.2) — a ~4-5x reduction.
This is the part that directly re-prices the whole book and is what the Phase
5c mandate tuning assumed an (over-priced) environment for.

## Recommendation

1. **Build Phase A now** (fix the half-hourly→daily-mean sigma bug). This is
   a correctness fix — "volatility premium" should reflect year-ahead price
   uncertainty, not intraday peak/off-peak spread, regardless of what
   `risk_factor` ends up being. Low risk, ~45% average premium is still high
   but roughly half the current distortion.
2. **Re-run the full simulation** (equivalent to the current Phase 6c
   re-run) with Phase A only, and report the new headline figures (revenue,
   gross/net margin, capital cost ratio) alongside the Phase 6a baseline and
   the naked_kwh fix already in flight.
3. **Hold Phase B (risk_factor recalibration) for explicit sign-off** — rather
   than guess a number now, use Phase A's re-run output to see where the
   average premium actually lands across the realised mix of contract starts
   (not just the 18 Jan/Jul sample points), then propose a specific
   `risk_factor` value targeted at the 5-15% literature range, with a
   before/after on margins. This avoids a second large re-run if the first
   guess is off.
4. **No special-case for crisis premium compression is needed** — the
   trailing-90-day-base-vs-realised mismatch already produces negative
   premiums exactly in 2020-07 to 2021-07 (the run-up to the crisis), which
   is the behaviour the literature describes. Don't add an explicit
   crisis-detection branch; it would be redundant with what the existing
   trailing-average structure already does once the volatility term is fixed.

## Open question for Rich

Phase A and B together would roughly halve-then-quarter the capital cost /
margin contribution from the forward curve — on top of the naked_kwh fix
already being validated in the current Phase 6c re-run. Given both fixes
target the same "12.6% net margin vs 2-5% benchmark" gap, should Phase A be
built and re-run **after** Phase 6c's naked_kwh results are in (sequential,
so each fix's effect is isolated and attributable), or bundled into the next
re-run together? Default plan, absent redirection: sequential — finish
reviewing Phase 6c's naked_kwh-only results first, then build and re-run
Phase A on top.
