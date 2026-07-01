# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,714,934.33
  (£1,248,298.11 net change)
- Solvency signal (final year): £448,986/customer (8 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £19,926,863.00
  VAT remitted to HMRC: (£958,974.77) | Revenue (ex-VAT): £18,967,888.23
  Non-commodity pass-through: (£4,821,431.04)
- Gross margin: £6,482,518.46
- Capital costs: £238,331.17
- Net margin: £6,244,187.30
- Capital cost ratio: 3.7% of gross
- Net margin as % of revenue: 32.9%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1531, average clarity 0.816,
  service quality score 0.905
- Enterprise value (CLV sum across 14 billing accounts): £6,043,702.85
- Cost to serve (whole portfolio): £91,287.17, net margin after cost to serve: £6,152,900.13
- Hedge effectiveness (whole window): hedging cost £4,032,948.62 vs. a fully unhedged book (commodity-only: actual net £1,248,298.11 vs. naked net £5,281,246.73)

- **2021** (crisis year): net margin £58,825.01, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £257,281.79, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2250, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | -0.7x (net £-134,790.07 on £187,116.34 capital) | **RED** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 4/6 departures (67%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 3.3%, max 15.6% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +33.1% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 32.9% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Gas segment ROC, Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,482,518.46, capital £238,331.17, net £6,244,187.30. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 3.7% (commodity basis, comparable to old model) / 3.7% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £58,825.01 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 32.9%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,244,187.30
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,281,246.73
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,032,948.62 vs. a fully unhedged book (commodity-only: actual net £1,248,298.11 vs. naked net £5,281,246.73)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £103,725.49 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £617,054.66 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £254.88 | £626.84 | £296.53 | £1,178.25 |
| 2017 | £29,456.72 | £0.00 | £223.37 | £835.24 | £463.34 | £30,978.68 |
| 2018 | £99,267.12 | £0.00 | £-252.55 | £505.90 | £374.66 | £99,895.13 |
| 2019 | £217,417.60 | £34.62 | £208.82 | £720.62 | £431.59 | £218,813.25 |
| 2020 | £111,629.74 | £4,005.30 | £334.61 | £875.54 | £426.32 | £117,271.50 |
| 2021 | £60,362.57 | £-1,789.15 | £190.04 | £274.67 | £-213.12 | £58,825.01 |
| 2022 | £308,367.06 | £-48,236.35 | £820.78 | £-2,367.85 | £-1,301.85 | £257,281.79 |
| 2023 | £82,967.23 | £-31,147.16 | £1,268.84 | £300.20 | £-1,164.32 | £52,224.79 |
| 2024 | £353,834.37 | £-37,642.96 | £493.11 | £2,022.73 | £396.91 | £319,104.16 |
| 2025 | £112,088.84 | £-19,724.42 | £0.00 | £361.13 | £0.00 | £92,725.55 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **50** renewals.  Lost (churned): **6** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8255 |
| C_IC1 | 2018-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3902 |
| C1 | 2018-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6312 |
| C_IC2 | 2019-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3710 |
| C1 | 2019-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.5838 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.2600 | 0.5500 | 0.8830 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8723 |
| C2_2 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.7019 |
| C2_2 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.3751 |
| C2_2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 197.5%
- **Average signed error:** +51.7% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -82.1% | 82.1% |
| 2017 | 3 | -93.7% | 93.7% |
| 2018 | 4 | +402.7% | 497.3% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | +26.1% | 190.1% |
| 2021 | 9 | -6.7% | 120.3% |
| 2022 | 7 | -23.1% | 112.6% |
| 2023 | 7 | -13.3% | 122.7% |
| 2024 | 7 | +78.9% | 231.8% |
| 2025 | 2 | -94.4% | 94.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 34.9%, abs error 313.7%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.9%, abs error 146.8%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.2% | 0.0% | 82.1% |
| 2017 | 0 | 3 | 0.0% | 2.2% | 0.0% | 93.7% |
| 2018 | 2 | 2 | 19.1% | 49.9% | 51.5% | 943.1% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 16.7% | 0.5% | 281.7% | 98.4% |
| 2021 | 3 | 6 | 66.0% | 4.1% | 184.3% | 88.3% |
| 2022 | 0 | 7 | 0.0% | 19.5% | 0.0% | 112.6% |
| 2023 | 2 | 5 | 29.1% | 19.0% | 72.9% | 142.6% |
| 2024 | 3 | 4 | 39.9% | 0.0% | 407.5% | 100.0% |
| 2025 | 0 | 2 | 0.0% | 2.1% | 0.0% | 94.4% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 9 (23%)
- **Below/at SVT (protected):** 30 (77%)
- **Mean rate vs SVT premium:** -10.3%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.1 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 120.0 | 140.0 |
| 2018 | 2 | 1 (50%) | +0.1% | 152.7 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -25.9% | 130.9 | 176.9 |
| 2021 | 6 | 3 (50%) | +0.9% | 184.2 | 183.8 |
| 2022 | 7 | 4 (57%) | +11.5% | 294.5 | 318.4 |
| 2023 | 5 | 0 (0%) | -32.5% | 225.2 | 364.0 |
| 2024 | 4 | 0 (0%) | -16.3% | 205.6 | 246.9 |
| 2025 | 2 | 1 (50%) | -4.8% | 236.7 | 248.6 |

**Interpretation:** Premium > 0% means the company is charging passive renewers above the SVT rate — a regulatory and reputational risk. Premium < 0% means passive renewers are getting a better-than-SVT deal — the company is leaving margin on the table but building loyalty.

## Company Model Divergence

Year-by-year gap between company observable-data models and SIM ground truth.
A well-calibrated company model narrows divergence over time as the company
accumulates experience. Divergence in crisis years reveals epistemic risk.

### Tariff Pricing Error

Company forward price (120-day rolling mean + 15% risk premium + Phase 13d seasonal
adjustment: winter Oct-Mar +8%, summer Apr-Sep -4%) vs SIM forward curve.
Seasonal adjustment reduces structural under-pricing of winter contracts.
Crisis years (2021-22) remain negative — genuine market adversity, not model error.

| Year | Terms | Mean Abs Error | Max Abs Error |
|------|-------|---------------|--------------|
| 2016 | 17 | 15.1% | 29.1% |
| 2017 | 14 | 16.6% | 46.6% |
| 2018 | 16 | 12.1% | 27.7% |
| 2019 | 19 | 11.0% | 37.2% |
| 2020 | 22 | 12.5% | 33.8% |
| 2021 | 17 | 14.5% | 44.5% |
| 2022 | 15 | 10.2% | 23.2% |
| 2023 | 14 | 20.0% | 40.0% |
| 2024 | 13 | 9.7% | 22.6% |
| 2025 | 2 | 33.1% | 33.1% |

### Churn Estimate Error

Company observable-data churn estimate vs SIM bill-shock model.
Phase 13c adds a bill burden signal (prev_annual_bill / £3,000 threshold)
that captures high-spend SME customers under financial stress even when
their renewal rate is falling — the failure mode that caused company_p=0%
for C6 in 2024 despite SIM showing 38% churn risk.

**Structural limitation**: the company model uses rate-change % as a churn proxy.
The SIM uses bill-shock history (whether the customer experienced billing spikes
during their contract). In crisis years (2021-22), rate increases were extreme
but hedged customers had few bill shocks — the company systematically over-estimates
churn (company_p→0.95) for customers the SIM correctly sees as low-risk (sim_p=5-14%).
The 2021 max error reflects this: the company cannot observe that a customer was
well-hedged and therefore not experiencing bill shocks during their last contract.

| Year | Renewals | Mean Abs Error (×SIM) | Max Abs Error (×SIM) |
|------|----------|-----------------------|---------------------|
| 2016 | 3 | 0.82× | 0.82× |
| 2017 | 3 | 0.94× | 0.94× |
| 2018 | 4 | 4.97× ⚠ | 18.00× |
| 2019 | 4 | 5.25× ⚠ | 18.00× |
| 2020 | 10 | 1.90× | 10.81× |
| 2021 | 9 | 1.20× | 3.75× |
| 2022 | 7 | 1.13× | 3.13× |
| 2023 | 7 | 1.23× | 3.13× |
| 2024 | 7 | 2.32× ⚠ | 10.88× |
| 2025 | 2 | 0.94× | 1.00× |

### Demand Estimation Error (Phase AO)

Company EAC estimate error vs SIM settled consumption — year-by-year trend.
Error grows as customers acquire EVs, solar, and heat pumps that the company
cannot directly observe. The first contract term after asset acquisition has
the highest error; subsequent terms self-correct from billing history.

| Year | Customers | Mean Abs Error | Max Abs Error | Signal |
|------|-----------|----------------|---------------|--------|
| 2016 | 3 | 0.07% | 0.07% | Low — stable portfolio |
| 2017 | 9 | 0.38% | 1.69% | Low — stable portfolio |
| 2018 | 10 | 0.63% | 3.21% | Low — stable portfolio |
| 2019 | 11 | 1.00% | 5.05% | Low — stable portfolio |
| 2020 | 13 | 0.76% | 3.50% | Low — stable portfolio |
| 2021 | 11 | 1.06% | 4.24% | MODERATE — asset adoption visible |
| 2022 | 9 | 1.87% | 7.47% | MODERATE — asset adoption visible |
| 2023 | 9 | 2.46% | 8.47% | MODERATE — asset adoption visible |
| 2024 | 9 | 3.26% | 15.56% | HIGH drift — EV/asset cohort growing |
| 2025 | 2 | 1.42% | 2.07% | MODERATE — asset adoption visible |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **3.26%** mean / **15.56%** max in 2024. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
Portfolio action: prioritise smart meter installation for high-EAC-drift accounts — interval data eliminates estimation error at renewal.

## Demand Estimation Accuracy (Phase 23a/25a)

Company EAC estimate (from prior-year billing records) vs actual settled kWh.
Phase 25a: true_eac_kwh uses mean annual settled consumption (not declared EAC),
fixing the misleading ~100% error for EV customers (C2/C4: declared 3500/5500 kWh,
actual ~6820 kWh/year with EV charging). Near-zero error after first term confirms
company billing estimation correctly tracks actual consumption.

| Year | Renewals | Mean Abs Error | Max Abs Error |
|------|----------|----------------|--------------|
| 2016 | 3 | 0.1% | 0.1% |
| 2017 | 9 | 0.4% | 1.7% |
| 2018 | 10 | 0.6% | 3.2% |
| 2019 | 11 | 1.0% | 5.0% |
| 2020 | 13 | 0.8% | 3.5% |
| 2021 | 11 | 1.1% | 4.2% |
| 2022 | 9 | 1.9% | 7.5% |
| 2023 | 9 | 2.5% | 8.5% |
| 2024 | 9 | 3.3% | 15.6% |
| 2025 | 2 | 1.4% | 2.1% |

**86** of **86** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## EAC Drift Snapshot (Phase AI)

Per-customer consumption drift from company billing history (first renewal → latest renewal).
Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.

**1 significant** (≥15%) | **1 moderate** (5–15%) | **11 stable** (<5%)

| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |
|----------|-------------|-------------|-------|--------------|
| C4 | 4,131 | 3,365 | -19% | likely solar installation or significant efficiency upgrade |
| C7 | 13,179 | 12,155 | -8% | efficiency improvement or reduced occupancy |

**Portfolio demand trend:** 6 customers increasing / 6 decreasing (mean drift: -2.3%)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **7** (6 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.32, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.32, company est=0.04 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.83 |
| 2022-03-31 | CHURN | C2 | SIM p=0.26, company est=0.07 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.25 |
| 2024-09-29 | CHURN | C4 | SIM p=0.32, company est=0.00 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 1 accounts | 0 active | yes |
| 2021-12-31 | 3 accounts | 0 active | yes |
| 2022-12-31 | 4 accounts | 1 active | yes |
| 2023-12-31 | 4 accounts | 1 active | yes |
| 2024-12-31 | 6 accounts | 1 active | yes |
| 2025-12-31 | 6 accounts | 1 active | yes |

## Policy Costs — RO + CfD + CCL + CM + FiT + Mutualization (Phase 21a/27b/30a/31a/54)

Electricity policy costs deducted from net_margin_gbp each year. 
CfD levy was NEGATIVE in 2022 (crisis rebate from LCCC). 
CCL applies to business (SME/I&C) only — resi exempt. 
CM (Capacity Market) and FiT (Feed-in Tariff) levies apply to ALL demand including domestic.

| Year | RO levy £ | CfD levy £ | CCL £ | CM levy £ | FiT levy £ | Mutualization £ | Total policy cost £ | Note |
|------|-----------|------------|-------|-----------|-----------------|---------------------|------|---------------------|
| 2016 | 1,162 | 7 | 189 | 37 | 305 | 0 | 1,701 |  |
| 2017 | 37,352 | 2,722 | 11,227 | 1,985 | 9,991 | 0 | 63,278 |  |
| 2018 | 65,913 | 9,938 | 17,545 | 9,401 | 17,391 | 0 | 120,187 |  |
| 2019 | 165,083 | 28,434 | 42,580 | 32,051 | 44,423 | 0 | 312,571 |  |
| 2020 | 239,156 | 35,468 | 69,608 | 56,674 | 70,177 | 0 | 471,083 |  |
| 2021 | 249,026 | 15,152 | 72,054 | 50,148 | 63,433 | 41,818 | 491,631 |  |
| 2022 | 259,289 | -50,342 | 71,853 | 37,170 | 69,907 | 100,685 | 488,561 | ⬇ CfD REBATE |
| 2023 | 274,578 | 65,429 | 72,499 | 51,399 | 75,854 | 13,891 | 553,649 |  |
| 2024 | 310,631 | 111,030 | 73,612 | 69,368 | 83,373 | 2,019 | 650,033 |  |
| 2025 | 137,698 | 47,631 | 31,649 | 31,480 | 36,676 | 866 | 286,000 |  |
| **Total** | **1,739,886** | **265,468** | **462,816** | **339,713** | **471,531** | **159,279** | **3,438,694** | |

Total policy cost: £3,438,694 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

## Network Charges — DUoS + TNUoS (Phase 29a)

Electricity network charges deducted from net_margin_gbp each year. 
Resi/SME: combined DUoS + TNUoS unit rate (largest single non-commodity cost). 
I&C HV: DUoS only (Triad TNUoS is an annual lump tracked in the Triad section).

| Year | Network cost £ | Note |
|------|----------------|------|
| 2016 | 3,202 |  |
| 2017 | 26,301 |  |
| 2018 | 38,779 |  |
| 2019 | 88,630 |  |
| 2020 | 124,849 |  |
| 2021 | 124,693 |  |
| 2022 | 134,603 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 140,330 | RIIO-ED2 from Apr 2023 |
| 2024 | 144,360 |  |
| 2025 | 61,948 |  |
| **Total** | **887,696** | |

Total network cost: £887,696 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

## Gas Policy Costs and Network Charges (Phase 30b)

Gas CCL: non-domestic only (domestic gas exempt). Gas network (GDN + NTS): all on unit rate.
GGL (Green Gas Levy): per-meter, from Nov 2021; tiny in £/MWh terms.

| Year | Gas Policy (CCL + GGL) £ | Gas Network £ | Total Gas Non-Commodity £ |
|------|--------------------------|---------------|--------------------------|
| 2016 | 0 | 479 | 479 |
| 2017 | 0 | 898 | 898 |
| 2018 | 0 | 905 | 905 |
| 2019 | 15,155 | 50,388 | 65,543 |
| 2020 | 19,468 | 47,215 | 66,683 |
| 2021 | 22,472 | 50,441 | 72,913 |
| 2022 | 27,045 | 54,433 | 81,478 |
| 2023 | 32,229 | 79,700 | 111,929 |
| 2024 | 37,494 | 76,429 | 113,923 |
| 2025 | 17,243 | 31,816 | 49,059 |
| **Total** | **171,106** | **392,704** | **563,810** |

Gas policy pass-through in tariff unit rate (CCL + GGL at term start); gas network pass-through likewise. Net basis risk near-zero for annual contracts.


## Gas Book P&L — Year by Year (Phase 32a)

Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.
Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.

| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |
|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|
| 2016 | 1,388 | 578 | 811 | 0 | 479 | 7 | 297 | +21.4% |
| 2017 | 2,660 | 1,231 | 1,430 | 0 | 898 | 15 | 463 | +17.4% |
| 2018 | 3,114 | 1,751 | 1,363 | 0 | 905 | 21 | 375 | +12.0% |
| 2019 | 137,770 | 61,712 | 76,058 | 15,155 | 50,388 | 9,313 | 466 | +0.3% |
| 2020 | 121,134 | 43,943 | 77,191 | 19,468 | 47,215 | 5,440 | 4,432 | +3.7% |
| 2021 | 297,852 | 215,060 | 82,792 | 22,472 | 50,441 | 10,325 | -2,002 | -0.7% |
| 2022 | 588,330 | 497,974 | 90,356 | 27,045 | 54,433 | 52,405 | -49,538 | -8.4% |
| 2023 | 297,198 | 176,258 | 120,940 | 32,229 | 79,700 | 39,726 | -32,311 | -10.9% |
| 2024 | 270,491 | 146,077 | 124,414 | 37,494 | 76,429 | 46,351 | -37,246 | -13.8% |
| 2025 | 132,454 | 78,945 | 53,509 | 17,243 | 31,816 | 23,512 | -19,724 | -14.9% |
| **Total** | **1,852,390** | **1,223,528** | **628,862** | **171,106** | **392,704** | **187,116** | **-134,790** | **-7.3%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,424 | 9 | 274,158 | 2108.91× | OK |
| 2017 | 2,498,127 | 10 | 249,813 | 1921.64× | OK |
| 2018 | 2,486,792 | 11 | 226,072 | 1739.02× | OK |
| 2019 | 2,607,298 | 12 | 217,275 | 1671.35× | OK |
| 2020 | 2,901,196 | 13 | 223,169 | 1716.68× | OK |
| 2021 | 2,923,134 | 12 | 243,594 | 1873.80× | OK |
| 2022 | 3,071,857 | 11 | 279,260 | 2148.15× | OK |
| 2023 | 3,177,752 | 10 | 317,775 | 2444.43× | OK |
| 2024 | 3,539,953 | 10 | 353,995 | 2723.04× | OK |
| 2025 | 3,591,886 | 8 | 448,986 | 3453.74× | OK |

End-state (2025): **£448,986/account** across 8 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,424 | 81947.0× | OK |
| 2017 | 466 | 559 | 2,498,127 | 4468.4× | OK |
| 2018 | 849 | 1,019 | 2,486,792 | 2441.1× | OK |
| 2019 | 1,543 | 1,851 | 2,607,298 | 1408.5× | OK |
| 2020 | 1,979 | 2,375 | 2,901,196 | 1221.7× | OK |
| 2021 | 4,407 | 5,288 | 2,923,134 | 552.8× | OK |
| 2022 | 8,500 | 10,199 | 3,071,857 | 301.2× | OK |
| 2023 | 5,605 | 6,726 | 3,177,752 | 472.4× | OK |
| 2024 | 2,731 | 3,278 | 3,539,953 | 1080.0× | OK |
| 2025 | 4,173 | 5,008 | 3,591,886 | 717.3× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,487.72 | £12,221.26 | £261.74/MWh | £144.48/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,978.01 | £9,696.78 | £272.55/MWh | £154.47/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,929.70 | £9,307.86 | £250.17/MWh | £141.68/MWh | +10.9% |

Total HH revenue: £63,621.33 vs flat equivalent £58,720.50 (+8.3% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 31 | 100% | C8 (2016-10-31) |
| 2017 | 50 | 81% | C8 (2017-11-30) |
| 2018 | 60 | 85% | C4g (2018-10-31) |
| 2019 | 66 | 126% | C_IC1 (2019-03-31) |
| 2020 | 53 | 117% | C_IC2 (2020-03-31) |
| 2021 | 51 | 113% | C4g (2021-10-31) |
| 2022 | 61 | 1735% | C2_2 (2022-04-30) |
| 2023 | 42 | 100% | C_IC2 (2023-06-30) |
| 2024 | 33 | 107% | C_IC2 (2024-07-31) |
| 2025 | 20 | 80% | C7 (2025-06-07) |

Total: **467** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1735% | no |
| 2022-10-31 | C4g | +134% | no |
| 2019-03-31 | C_IC1 | +126% | no |
| 2020-03-31 | C_IC2 | +117% | no |
| 2021-10-31 | C4g | +113% | no |
| 2022-01-31 | C_IC3 | +109% | no |
| 2024-07-31 | C_IC2 | +107% | no |
| 2016-10-31 | C8 | +100% | no |
| 2023-06-30 | C_IC2 | +100% | no |
| 2023-10-31 | C8 | +92% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 11% | 11% | 0 |
| 2017 | 4 | 16% | 23% | 2 ⚠ |
| 2018 | 4 | 17% | 23% | 2 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 5 | 5% | 24% | 1 ⚠ |
| 2021 | 3 | 69% | 95% | 3 ⚠ |
| 2022 | 2 | 49% | 95% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 1 | 4% | 4% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £20.2 | £124.1 (+515%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £16.1 | £35.0 (+118%) | 74% |
| 2021-03-31 | C2g | £21.7 | £35.0 (+62%) | 40% |
| 2020-12-31 | C_IC3g | £15.4 | £20.2 (+31%) | 24% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 18 |
| Retained | 17 (94%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £422,380.48 |
| Margin saved (retained customers' terms) | £2,222,968.45 |
| Wasted offer cost (churned anyway) | £509.55 |
| **Net ROI of retention strategy** | **£1,800,587.97** |
| Acquisition cost avoided (retained customers) | £2,800.00 |
| **Full economic ROI (margin + acq savings)** | **£1,803,387.97** |

Missed opportunities (churns with no offer): **5** (£3,964.62 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 5 (£3,964.62 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24327.21 | £164116.51 | £139789.30 | £0.00 |
| 2019 | 2 | 2 | £43005.30 | £297820.20 | £254814.90 | £0.00 |
| 2020 | 3 | 3 | £26920.04 | £164754.75 | £137834.72 | £585.36 |
| 2021 | 4 | 3 | £120875.58 | £416122.26 | £295246.68 | £-178.13 |
| 2022 | 2 | 2 | £74522.99 | £330071.97 | £255548.98 | £236.63 |
| 2023 | 4 | 4 | £88246.56 | £442730.44 | £354483.88 | £0.00 |
| 2024 | 2 | 2 | £44482.80 | £407352.32 | £362869.52 | £3320.76 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24327.21 | £164116.51 | £150 | £139789.30 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14931.27 | £102253.79 | £150 | £87322.53 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £28074.03 | £195566.41 | £150 | £167492.37 | retained |
| 2020-01-01 | C_IC3 | 0.36 | 3% | £5730.88 | £10737.83 | £150 | £5006.95 | retained |
| 2020-03-31 | C_IC1 | 0.50 | 5% | £10390.59 | £131076.00 | £150 | £120685.41 | retained |
| 2020-12-31 | C_IC3 | 0.59 | 5% | £10798.57 | £22940.92 | £150 | £12142.35 | retained |
| 2021-03-31 | C_IC2 | 0.84 | 8% | £14247.34 | £91866.21 | £150 | £77618.88 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £22654.00 | £159133.51 | £150 | £136479.51 | retained |
| 2021-12-30 | C5 | 0.83 | 8% | £509.55 | £2237.23 | £400 | £-509.55 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £83464.68 | £165122.53 | £150 | £81657.85 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25472.71 | £96757.81 | £150 | £71285.10 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £49050.28 | £233314.16 | £150 | £184263.88 | retained |
| 2023-03-31 | C6 | 0.49 | 3% | £230.69 | £3262.34 | £400 | £3031.65 | retained |
| 2023-05-30 | C_IC2 | 0.58 | 5% | £11866.64 | £132206.10 | £150 | £120339.45 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £35189.99 | £246672.45 | £150 | £211482.46 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £40959.24 | £60589.55 | £150 | £19630.31 | retained |
| 2024-06-28 | C_IC2 | 0.54 | 5% | £10346.45 | £134846.74 | £150 | £124500.29 | retained |
| 2024-07-28 | C_IC1 | 0.95 | 8% | £34136.35 | £272505.58 | £150 | £238369.23 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C_IC1 | 2018-01-31 | (window end) | 95 | active |
| C_IC2 | 2019-01-31 | (window end) | 83 | active |
| C_IC3 | 2020-01-01 | (window end) | 72 | active |
| C5 | 2021-12-30 | 2021-12-30 | 0 | churned |
| C6 | 2023-03-31 | 2024-03-30 | 12 | churned |

**Eventually churned (2/5)**: C5, C6 — avg 6 months post-retention before final churn.
**Still active (3/5)**: C_IC1, C_IC2, C_IC3 — survived to simulation end.

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £6,043,702.85 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £444,665.32 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,178.25 |
| 2017 | £30,978.68 |
| 2018 | £99,895.13 |
| 2019 | £218,813.25 |
| 2020 | £117,271.50 |
| 2021 | £58,825.01 |
| 2022 | £257,281.79 |
| 2023 | £52,224.79 | ← trailing
| 2024 | £319,104.16 | ← trailing
| 2025 | £92,725.55 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £3,758.26 | — |
| C2 | £5,015.15 | — |
| C2_2 | — | £971.57 |
| C3 | £4,931.93 | — |
| C4 | £2,923.81 | £-862.74 |
| C5 | £8,448.42 | — |
| C6 | £15,097.81 | £2,529.33 |
| C7 | £6,647.70 | £114.97 |
| C8 | £7,256.17 | £383.04 |
| C9 | £7,557.39 | £939.85 |
| C_IC1 | £1,460,474.61 | £338,153.49 |
| C_IC2 | £788,502.26 | £179,004.86 |
| C_IC3 | £2,474,541.14 | £-84,882.37 |
| C_IC4 | £1,255,073.05 | £8,313.31 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £2,259.66 | — | — | — | — | £5,096.01 | — | £4,189.02 | — | — | — | — | — | — |
| 2017 | £1,925.07 | £3,735.37 | — | £3,578.06 | £3,313.17 | £4,557.02 | £8,375.76 | £3,198.78 | £4,612.76 | £3,979.18 | — | — | — | — |
| 2018 | £2,044.67 | £3,366.35 | — | £3,280.84 | £2,553.10 | £4,135.17 | £7,012.94 | £3,117.98 | £3,913.08 | £3,746.99 | £977,611.09 | — | — | — |
| 2019 | £2,031.88 | £2,976.43 | — | £3,306.15 | £2,818.73 | £4,447.02 | £7,484.38 | £3,271.22 | £3,889.36 | £3,802.39 | £877,158.92 | £533,063.30 | — | — |
| 2020 | £2,354.48 | £3,147.13 | — | £2,903.62 | £2,915.29 | £4,922.61 | £7,822.03 | £3,947.19 | £4,123.78 | £3,750.33 | £650,913.62 | £322,130.01 | £1,042,436.48 | £679,253.11 |
| 2021 | £2,149.90 | £3,535.21 | — | £2,898.44 | £2,579.50 | £4,780.06 | £8,976.90 | £3,182.04 | £4,275.15 | £3,525.30 | £583,927.76 | £357,340.56 | £1,047,971.26 | £635,185.70 |
| 2022 | £2,387.33 | £2,709.58 | £479.63 | £2,892.22 | £1,671.17 | £4,936.72 | £8,297.07 | £2,807.06 | £4,074.08 | £3,924.03 | £653,261.87 | £380,850.79 | £1,178,445.19 | £604,872.42 |
| 2023 | £2,363.74 | £2,754.30 | £1,362.38 | £2,939.89 | £1,284.79 | £4,887.44 | £9,034.18 | £3,049.76 | £4,076.05 | £4,133.22 | £706,196.69 | £397,846.07 | £1,091,525.35 | £633,772.08 |
| 2024 | £2,185.27 | £2,826.48 | £1,961.04 | £3,148.22 | £1,626.06 | £4,679.73 | £9,107.37 | £3,081.06 | £4,230.43 | £4,697.20 | £726,697.20 | £425,328.81 | £1,357,073.29 | £764,248.77 |
| 2025 | £2,182.92 | £2,873.24 | £2,072.10 | £2,946.11 | £1,671.27 | £4,762.46 | £8,825.69 | £3,543.96 | £4,133.91 | £4,527.83 | £773,391.74 | £449,632.77 | £1,408,672.45 | £795,670.40 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,804.59, range £58.35–£26,469.25.

- C1: cost to serve £414.45, net margin after CTS £2,320.29
- C1g: cost to serve £64.80, net margin after CTS £1,478.25
- C2: cost to serve £432.18, net margin after CTS £2,976.00
- C2_2: cost to serve £381.10, net margin after CTS £5,091.34
- C2g: cost to serve £83.87, net margin after CTS £1,935.34
- C3: cost to serve £292.46, net margin after CTS £2,093.32
- C3g: cost to serve £58.35, net margin after CTS £1,245.05
- C4: cost to serve £565.40, net margin after CTS £2,750.30
- C4g: cost to serve £216.69, net margin after CTS £1,132.91
- C5: cost to serve £871.77, net margin after CTS £8,504.73
- C6: cost to serve £1,349.13, net margin after CTS £21,100.16
- C7: cost to serve £953.31, net margin after CTS £9,778.66
- C8: cost to serve £938.93, net margin after CTS £11,516.08
- C9: cost to serve £896.47, net margin after CTS £11,805.69
- C_IC1: cost to serve £20,025.69, net margin after CTS £1,876,860.68
- C_IC2: cost to serve £11,447.46, net margin after CTS £910,849.13
- C_IC3: cost to serve £26,469.25, net margin after CTS £1,791,927.68
- C_IC3g: cost to serve £9,229.97, net margin after CTS £613,417.06
- C_IC4: cost to serve £16,595.90, net margin after CTS £1,100,681.25


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 29 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 13.8%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,749.07 | £10,901.23 | +20.0% | £112.24/MWh | £152.03/MWh |
| C5 | electricity | 2018-12-31 | £-203.29 | £2,323.55 | +3.8% | £148.68/MWh | £153.31/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,332.71 | £6,376.41 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,269.51 | £10,243.03 | +20.0% | £128.22/MWh | £175.50/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,922.12 | £3,444.18 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £177.17/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.59/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £59.42/MWh |
| C5 | electricity | 2021-12-30 | £-339.47 | £2,699.28 | +7.6% | £311.83/MWh | £340.54/MWh |
| C7 | electricity | 2021-12-30 | £-122.66 | £1,986.26 | +1.2% | £311.83/MWh | £320.27/MWh |
| C_IC3 | electricity | 2021-12-31 | £-27,449.78 | £447,310.03 | +1.1% | £224.03/MWh | £260.56/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £316.71/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £307.44/MWh |
| C4 | electricity | 2022-09-30 | £-220.41 | £906.59 | +19.3% | £404.86/MWh | £484.85/MWh |
| C4g | gas | 2022-09-30 | £-901.21 | £1,040.11 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £318.56/MWh |
| C_IC3g | gas | 2022-12-31 | £-49,329.98 | £586,562.16 | +3.4% | £101.23/MWh | £120.39/MWh |
| C8 | electricity | 2023-03-31 | £-348.38 | £3,898.74 | +3.9% | £319.17/MWh | £335.54/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.09/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £219.94/MWh |
| C4 | electricity | 2023-09-30 | £-277.33 | £1,324.46 | +15.9% | £216.77/MWh | £249.30/MWh |
| C4g | gas | 2023-09-30 | £-1,950.48 | £2,732.11 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-345.82 | £3,990.91 | +3.7% | £242.22/MWh | £238.54/MWh |
| C_IC3 | electricity | 2023-12-31 | £-170,519.48 | £937,174.33 | +13.2% | £118.95/MWh | £127.91/MWh |
| C_IC3g | gas | 2023-12-31 | £-30,637.15 | £295,562.62 | +5.4% | £51.89/MWh | £61.13/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |
| C_IC3g | gas | 2024-12-30 | £-37,283.07 | £268,211.20 | +8.9% | £50.47/MWh | £61.82/MWh |



## Portfolio Intelligence Pack (Phase AH)

Board-level synthesis of CRM and flexibility intelligence derived from observable operational data.

### 1. Retention Intelligence

- **Retention offers made:** 18
- **Offer acceptance rate:** 94% (17 retained / 1 churned despite offer)
- **Estimated margin protected:** £2,222,968.45
- **No-offer churns:** 5 total (0 blind miss / 0 deliberate pass)
- **Retention coverage rate:** 78% of at-risk renewals received an offer

### 2. Flexibility Revenue Intelligence

- No flexibility revenue data available.

### 3. Churn Pattern Analysis

- **Total lifetime churn events:** 6
- **Peak churn year:** 2021 (2 events)
- **Net book movement:** 1 acquisitions − 6 churns = -5
- **Portfolio trend:** shrinking

### 4. Board Recommendations

1. **Crisis-year churn:** 3 churn events in 2021–2022. Maintain minimum hedge floor pre-crisis to preserve pricing stability and limit bill-shock churn.

## CRM Intelligence: Risk Triage (Final Year)

Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.

| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |
|---------|-----|-----------|-----------|----------|-------------|-----------------|
| C6 | SME | HIGH | 38% | 25% | -24.9% [competitive] | £21,100.16 |
| C8 | resi | HIGH | 38% | 0% | -23.6% [competitive] | £11,516.08 |
| C9 | resi | HIGH | 38% | 0% | -14.3% | £11,805.69 |
| C2_2 | resi | HIGH | 38% | 4% | +14.0% [overpriced] | £5,091.34 |
| C5 | SME | HIGH | 35% | 83% | +63.7% [overpriced] | £8,504.73 |
| C7 | resi | HIGH | 35% | 0% | -14.3% | £9,778.66 |
| C1 | resi | HIGH | 32% | 4% | -12.0% | £2,320.29 |
| C3 | resi | HIGH | 32% | 0% | -39.0% [competitive] | £2,093.32 |
| C4 | resi | HIGH | 32% | 0% | -9.1% | £2,750.30 |
| C2 | resi | MEDIUM | 26% | 7% | +46.6% [overpriced] | £2,976.00 |
| C_IC3 | I&C | LOW | 8% | 95% | -54.9% [competitive] | £1,791,927.68 |
| C_IC1 | I&C | LOW | 5% | 95% | -0.3% | £1,876,860.68 |
| C_IC2 | I&C | LOW | 5% | 95% | +12.4% [overpriced] | £910,849.13 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 9 accounts
- MEDIUM (>=15%): 1 accounts
- LOW (<15%): 3 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £74,960.55
- Overpriced vs SVT within HIGH/CRITICAL band: 2 account(s) -- rate shock risk compounds churn probability

**Company blind spot:** 7 HIGH/CRITICAL account(s) where company churn estimate was <10%.
  - C8: sim 38%, company est 0%
  - C9: sim 38%, company est 0%
  - C2_2: sim 38%, company est 4%
  - C7: sim 35%, company est 0%
  - C1: sim 32%, company est 4%

## Churn Root Cause Attribution

Per-churned-account analysis: pricing journey, rate-vs-SVT positioning, and company vs SIM churn estimate at the point of departure.

| Account | Seg | Churn Date | Tenure | Last Rate Shock | Rate vs SVT | Sim Risk | Co. Est. | Margin Lost |
|---------|-----|------------|--------|-----------------|-------------|----------|----------|-------------|
| C3 | resi | 2020-06-30 | 4.0yr | -4.3% | -39.0% | 32% | 0% | £2,093.32 |
| C1 | resi | 2021-12-30 | 6.0yr | +1.5% | -12.0% | 32% | 4% | £2,320.29 |
| C5 | SME | 2021-12-30 | 6.0yr | +1.5% | +63.7% | 35% | 83% | £8,504.73 |
| C2 | resi | 2022-03-31 | 6.0yr | +15.0% | +46.6% | 26% | 7% | £2,976.00 |
| C6 | SME | 2024-03-30 | 8.0yr | -0.9% | -24.9% | 38% | 25% | £21,100.16 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.7% | -9.1% | 32% | 0% | £2,750.30 |

**Root Cause Summary:**
- Total churned accounts: 6
- Lifetime margin lost: £39,744.78
- Average tenure at departure: 6.3 years
- Company blind misses (sim >=30%, co. est. <10%): 3 -- C3, C1, C4
- Company-warned churns (co. est. >=20%): 2 -- C5, C6
- Crisis-era churns (2021-22): 3 -- absolute crisis price level, not rate-change delta, was the driver
- Overpriced vs SVT at departure: 2 account(s) -- rate shock risk was observable but unactioned

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 5 accounts that churned without an offer? Calibrated from 18 actual offers (observed retention rate 94%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C3 | resi | 2020-06-30 | 0% | £585.36 | 5% | £29.27 | £523.57 | MISSED OPP. |
| C1 | resi | 2021-12-30 | 4% | £-178.13 | 5% | £0.00 | n/a | CORRECT PASS |
| C2 | resi | 2022-03-31 | 7% | £236.63 | 5% | £11.83 | £211.65 | MISSED OPP. |
| C6 | SME | 2024-03-30 | 25% | £2,852.27 | 8% | £228.18 | £2,465.63 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 0% | £468.49 | 5% | £23.42 | £419.04 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 5
- Correct no-offer (net-neg ETM): 1 (C1)
- Missed opportunities (positive ETM, below detection): 4
- Total term margin foregone: £4,142.75
- Total retention cost (counterfactual): £292.71
- Net counterfactual benefit: £3,619.89 (at 94% retention probability)
- Root cause: company churn detection below threshold for all missed cases -- churn model underestimated bill-shock risk

## Pricing Basis Risk Attribution

Forward curve accuracy at each contract term. tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd: positive = company over-estimated costs (higher than market); negative = company under-estimated (margin-at-risk).
Portfolio-wide mean error: +6.2%

| Year | Contracts | Mean Error | Max Abs | Over-priced | Under-priced | Assessment |
|------|-----------|------------|---------|-------------|--------------|------------|
| 2016 | 17 | +8.9% | 29.1% | 9 | 4 | moderate over |
| 2017 | 14 | +5.4% | 46.6% | 8 | 5 | moderate over |
| 2018 | 16 | -2.9% | 27.7% | 6 | 8 | on target |
| 2019 | 19 | +8.3% | 37.2% | 9 | 3 | moderate over |
| 2020 | 22 | +0.7% | 33.8% | 10 | 7 | on target |
| 2021 | 17 | +8.5% | 44.5% | 6 | 3 | moderate over |
| 2022 | 15 | +0.7% | 23.2% | 7 | 3 | on target |
| 2023 | 14 | +18.4% | 40.0% | 9 | 1 | HIGH OVER-PRICE |
| 2024 | 13 | +7.2% | 22.6% | 7 | 1 | moderate over |
| 2025 | 2 | +33.1% | 33.1% | 2 | 0 | HIGH OVER-PRICE |

**Basis Risk Summary:**
- Portfolio mean tariff error: +6.2%
- Worst over-pricing year: 2025 (+33.1%) -- company forward curve above settled market
- Post-crisis over-pricing years (2023, 2025): company locked in expensive crisis-era forwards after prices normalised -- mechanism that eroded real suppliers' margins 2022-24

## BSC Settlement Exposure

Elexon's Balancing and Settlement Code (BSC) requires suppliers to post credit cover to fund potential imbalance charges. Credit requirements track portfolio size and wholesale price levels. Peak daily settlement is the largest single-day settlement amount seen in that year.

| Year | BSC Credit Required | Peak Daily | % of Revenue |
|------|---------------------|------------|--------------|
| 2016 | £30 | £25 | 0.29% |
| 2017 | £559 | £466 | 0.24% |
| 2018 | £1,019 | £849 | 0.23% |
| 2019 | £1,851 | £1,543 | 0.15% |
| 2020 | £2,375 | £1,979 | 0.19% |
| 2021 | £5,288 | £4,407 | 0.30% |
| 2022 | £10,199 | £8,500 | 0.29% |
| 2023 | £6,726 | £5,605 | 0.26% |
| 2024 | £3,278 | £2,731 | 0.15% |
| 2025 | £5,008 | £4,173 | 0.51% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,199 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £524 | £91 | 11.3% |
| 2017 | 14 | £16,841 | £8,864 | £2,213 | 13.1% |
| 2018 | 15 | £29,186 | £17,579 | £6,660 | 22.8% |
| 2019 | 17 | £70,649 | £41,376 | £12,871 | 18.2% |
| 2020 | 18 | £68,123 | £44,089 | £6,515 | 9.6% |
| 2021 | 16 | £109,720 | £48,327 | £3,677 | 3.4% << |
| 2022 | 14 | £248,072 | £75,965 | £18,377 | 7.4% |
| 2023 | 12 | £214,725 | £76,793 | £4,352 | 2.0% << |
| 2024 | 12 | £186,182 | £107,920 | £26,592 | 14.3% |
| 2025 | 9 | £109,116 | £58,209 | £10,303 | 9.4% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £26,592 net/customer
**Worst year per customer:** 2016 at £91 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £423 | — | £423 |
| C1g | — | £645 | £645 |
| C2 | £718 | — | £718 |
| C2_2 | £1,044 | — | £1,044 |
| C2g | — | £802 | £802 |
| C3 | £203 | — | £203 |
| C3g | — | £288 | £288 |
| C4 | £139 | — | £139 |
| C4g | — | £-2,024 | £-2,024 * |
| C5 | £-36 | — | £-36 * |
| C6 | £3,578 | — | £3,578 |
| C7 | £-1,362 | — | £-1,362 * |
| C8 | £1,502 | — | £1,502 |
| C9 | £1,487 | — | £1,487 |
| C_IC1 | £839,325 | — | £839,325 |
| C_IC2 | £433,679 | — | £433,679 |
| C_IC3 | £87,702 | — | £87,702 |
| C_IC3g | — | £-134,500 | £-134,500 * |
| C_IC4 | £14,686 | — | £14,686 |
| **Total** | **£1,383,088** | **£-134,790** | **£1,248,298** |

Loss-making accounts: C_IC3g (£-134,500), C4g (£-2,024), C7 (£-1,362), C5 (£-36)
Gas loss-making: C_IC3g (£-134,500), C4g (£-2,024)
Gas portfolio net: £-134,790 (-10.8% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,034 | £10,920 | £-8,885 |
| 2017 | £30,490 | £112,879 | £-82,388 |
| 2018 | £109,967 | £247,157 | £-137,189 |
| 2019 | £243,419 | £825,875 | £-582,456 |
| 2020 | £74,561 | £934,123 | £-859,561 |
| 2021 | £144,721 | £347,679 | £-202,958 |
| 2022 | £105,417 | £1,091,127 | £-985,709 |
| 2023 | £362,616 | £1,158,632 | £-796,016 |
| 2024 | £175,015 | £552,517 | £-377,502 |
| 2025 | £57 | £337 | £-279 |
| **Total** | **£1,248,298** | **£5,281,247** | **£-4,032,948** |

Largest hedging cost: **2022** (£985,709 vs naked)
Smallest hedging cost: **2025** (£279 vs naked)
Conclusion: systematic forward hedging cost £4,032,948 over 10 years vs spot purchasing.

## Customer Service Quality

Ofgem benchmarks: bill clarity >0.82 (GREEN) / >0.80 (AMBER) / ≤0.80 (RED); complaint probability <5% (GREEN) / <6% (RED); bill shock <0.20% (GREEN) / <0.30% (AMBER) / ≥0.30% (RED).

| Year | Clarity | Complaint% | Shock% | Shock events | Bills | RAG |
|------|---------|------------|--------|--------------|-------|-----|
| 2016 | 0.829 G | 4.7% | 0.20% | 31 | 108 | GREEN |
| 2017 | 0.818 A | 4.7% | 0.17% | 50 | 168 | AMBER |
| 2018 | 0.810 A | 4.7% | 0.16% | 60 | 180 | AMBER |
| 2019 | 0.824 G | 4.7% | 0.17% | 66 | 204 | GREEN |
| 2020 | 0.830 G | 4.3% | 0.14% | 53 | 204 | GREEN |
| 2021 | 0.829 G | 4.5% | 0.16% | 51 | 192 | GREEN |
| 2022 | 0.791 R | 5.6% | 0.34% | 61 | 148 | RED ! |
| 2023 | 0.808 A | 4.8% | 0.17% | 42 | 144 | AMBER |
| 2024 | 0.813 A | 4.6% | 0.16% | 33 | 129 | AMBER |
| 2025 | 0.777 R | 5.9% | 0.24% | 20 | 54 | RED ! |

Worst clarity year: **2025** (0.777)
Highest complaint probability: **2025** (5.9%)
Worst bill shock: **2022** (0.34%)
RED years: 2022, 2025
AMBER years: 2017, 2018, 2023, 2024
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,424 | £1,178 |
| 2017 | 2.69 | WATCH | £2,498,127 | £30,979 |
| 2018 | — | — | £2,486,792 | £99,895 |
| 2019 | — | — | £2,607,298 | £218,813 |
| 2020 | — | — | £2,901,196 | £117,272 |
| 2021 | — | — | £2,923,134 | £58,825 |
| 2022 | 2.70 | WATCH | £3,071,857 | £257,282 |
| 2023 | 2.73 | WATCH | £3,177,752 | £52,225 |
| 2024 | — | — | £3,539,953 | £319,104 |
| 2025 | — | — | £3,591,886 | £92,726 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,591,886)**
**Treasury growth: £2,467,424 → £3,591,886 (+£1,124,461)**

> VaR ratio = portfolio stressed VaR ÷ treasury; ≥ 3.0 triggers committee review.
> Treasury funded from net margin accumulation, never falling to zero across run.

## UK Grid Fuel Mix Disclosure (Ofgem FMD)

Company's disclosed fuel mix per year (UK national grid average — Ofgem FMD requirement).

| Year | Renewable % | Nuclear % | Gas % | Coal % | Other % | Low-Carbon % |
|------|------------|----------|-------|--------|---------|-------------|
| 2016 | 24.6% | 20.9% | 42.6% | 9.0% | 2.9% | **45.5%** |
| 2017 | 29.3% | 20.4% | 40.7% | 7.0% | 2.6% | **49.7%** |
| 2018 | 33.0% | 19.3% | 39.4% | 5.1% | 3.2% | **52.3%** |
| 2019 | 36.9% | 17.4% | 38.3% | 2.1% | 5.3% | **54.3%** |
| 2020 | 42.2% | 16.7% | 35.8% | 1.8% | 3.5% | **58.9%** |
| 2021 | 39.8% | 14.5% | 38.3% | 2.5% | 4.9% | **54.3%** |
| 2022 | 40.5% | 14.5% | 37.8% | 1.7% | 5.5% | **55.0%** |
| 2023 | 47.8% | 14.6% | 31.5% | 1.3% | 4.8% | **62.4%** |
| 2024 | 51.4% | 14.1% | 28.6% | 0.4% | 5.5% | **65.5%** |
| 2025 | 55.0% | 13.5% | 26.0% | 0.1% | 5.4% | **68.5%** |

**Peak renewable share: 2025 (55.0%)**
**Renewable majority first achieved: 2024**

> UK grid fuel mix disclosed per Ofgem FMD regulations; published annually.
> Suppliers with 100% renewable tariffs must hold REGOs matching total supply.

## Missed Retention Opportunity Analysis

Customers who reached a renewal/churn trigger but received no retention offer.

### Electricity Customers — No Offer Made

| Customer | Date | Churn Estimate | Margin at Risk £ | Reason |
|----------|------|---------------|-----------------|--------|
| C3 | 2020-06 | 0.0% | £585 | below threshold |
| C1 | 2021-12 | 3.8% | -£178 | below threshold |
| C2 | 2022-03 | 6.7% | £237 | below threshold |
| C6 | 2024-03 | 24.7% | £2,852 | below threshold ⚑ |
| C4 | 2024-09 | 0.0% | £468 | below threshold |

**High-risk no-offer events (≥10% churn): 1** — £2,852 margin at risk.

### Gas Renewal Risk — High-Churn Reprice Events (≥15% estimate)

| Customer | Term Start | Old Rate p/therm | New Rate p/therm | Churn Est |
|----------|-----------|-----------------|-----------------|----------|
| C2g | 2017-04 | 26.92 | 32.81 | 20.1% |
| C1g | 2017-12 | 26.25 | 33.49 | 22.6% |
| C3g | 2018-07 | 23.11 | 28.80 | 20.8% |
| C4g | 2018-10 | 26.10 | 33.61 | 23.3% |
| C_IC3g | 2020-12 | 15.44 | 20.18 | 24.4% |
| C2g | 2021-03 | 21.66 | 35.00 | 39.9% |
| C4g | 2021-09 | 16.09 | 35.00 | 73.5% |
| C_IC3g | 2021-12 | 20.18 | 124.11 | 95.0% |

**High-risk gas reprices: 9**

> ⚑ = customers with ≥15% churn estimate who received no retention offer.

## Retention Decision Economics

Per-offer cost, expected margin protected, and ROI for each retention intervention.

| Customer | Period | Retention Cost £ | Margin Protected £ | ROI | Discount % | Outcome |
|----------|--------|-----------------|-------------------|-----|------------|---------|
| C_IC1 | 2018-01 | £24,327 | £164,117 | 6.7× | 8% | retained |
| C_IC2 | 2019-01 | £14,931 | £102,254 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £28,074 | £195,566 | 7.0× | 8% | retained |
| C_IC3 | 2020-01 | £5,731 | £10,738 | 1.9× | 3% | retained |
| C_IC1 | 2020-03 | £10,391 | £131,076 | 12.6× | 5% | retained |
| C_IC3 | 2020-12 | £10,799 | £22,941 | 2.1× | 5% | retained |
| C_IC2 | 2021-03 | £14,247 | £91,866 | 6.4× | 8% | retained |
| C_IC1 | 2021-04 | £22,654 | £159,134 | 7.0× | 8% | retained |
| C5 | 2021-12 | £510 | £2,237 | 4.4× | 8% | churned_despite_offer |
| C_IC3 | 2021-12 | £83,465 | £165,123 | 2.0× | 8% | retained |
| C_IC2 | 2022-04 | £25,473 | £96,758 | 3.8× | 8% | retained |
| C_IC1 | 2022-05 | £49,050 | £233,314 | 4.8× | 8% | retained |
| C6 | 2023-03 | £231 | £3,262 | 14.1× | 3% | retained |
| C_IC2 | 2023-05 | £11,867 | £132,206 | 11.1× | 5% | retained |
| C_IC1 | 2023-06 | £35,190 | £246,672 | 7.0× | 8% | retained |
| C_IC3 | 2023-12 | £40,959 | £60,590 | 1.5× | 8% | retained |
| C_IC2 | 2024-06 | £10,346 | £134,847 | 13.0× | 5% | retained |
| C_IC1 | 2024-07 | £34,136 | £272,506 | 8.0× | 8% | retained |

**Total retention spend: £422,380** | **Total margin protected: £2,225,206**
**Portfolio retention ROI: 5.3×** | **Retained: 17/18**
**Best ROI intervention: C6 2023-03 (14.1×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | -£45,604 | — |
| Exit Gas (with churn risk) | £53,808 | +£99,412 |
| Reprice to Breakeven | £90,920 | +£136,524 |

**Loss-making gas accounts: C4, C_IC3**
**Board recommendation: REPRICE GAS**

> Gas drag reduces dual-fuel net margin. Repricing to breakeven is preferable to exit
> because exiting gas risks losing the electricity contract (cross-product churn).

## Portfolio Hedge Fraction Evolution

Average hedge fraction (0=fully naked, 1=fully hedged) per year.

| Year | Portfolio Avg | Min HF | Max HF | Naked Accounts | Covered Accts |
|------|--------------|--------|--------|---------------|--------------|
| 2016 | 88.9% | 85.0% | 92.2% | — | 13 |
| 2017 | 89.6% | 85.0% | 94.3% | — | 14 |
| 2018 | 89.5% | 85.0% | 93.1% | — | 15 |
| 2019 | 83.5% | 0.0% | 96.2% | 1 | 16 |
| 2020 | 81.8% | 0.0% | 96.0% | 1 | 15 |
| 2021 | 83.6% | 0.0% | 97.0% | 1 | 12 |
| 2022 | 85.7% | 0.0% | 97.4% | 1 | 11 |
| 2023 | 83.1% | 0.0% | 95.9% | 1 | 11 |
| 2024 | 79.3% | 0.0% | 94.5% | 1 | 8 |
| 2025 | 87.2% | 85.0% | 89.4% | — | 2 |

**Lowest portfolio hedge fraction: 2024 (79.3%)** — risk erosion from regime-change blindness.
**Naked positions first appear in 2019** — unhedged accounts expose portfolio to spot price swings.

> Regime-change blindness: the sim converged toward lower hedging during calm 2016-2020,
> mirroring the strategy that destroyed real UK suppliers entering the 2021-22 crisis.

## Risk Committee Intervention Pattern

Annual risk committee wake-ups (triggered when portfolio VaR exceeds threshold).

| Year | Wake-ups | Customer Adjustments | Avg Customers/Event | Max VaR Stressed £ |
|------|----------|---------------------|--------------------|--------------------|
| 2016 | 13 | 13 | 1.0 | £9 |
| 2017 | 12 | 33 | 2.8 | £401 |
| 2022 | 9 | 62 | 6.9 | £20,657 |
| 2023 | 4 | 32 | 8.0 | £49,307 |

**Peak intervention year: 2016 (13 wake-ups)**
**Total committee events (all years): 38**

> Each wake-up adjusts hedge fractions upward for flagged customers. 2016-17 (early book).
> 2022-23 crisis years trigger most interventions on I&C anchor accounts.

## Worst Half-Hourly Settlement Period by Year

Most loss-making single 30-minute period per settlement year.

| Year | Date | SP | Customer | Net Margin £ |
|------|------|----|----------|-------------|
| 2016 | 2016-11-08 | 40 | C6 | -£0 |
| 2017 | 2017-05-17 | 32 | C_IC1 | -£20 |
| 2018 | 2018-03-01 | 27 | C_IC1 | -£15 |
| 2019 | 2019-02-04 | 35 | C_IC1 | -£15 |
| 2020 | 2020-12-31 | 1 | C_IC3g | -£489 |
| 2021 | 2021-12-31 | 1 | C_IC3g | -£4,092 |
| 2022 | 2022-12-31 | 1 | C_IC3g | -£2,999 |
| 2023 | 2023-12-31 | 1 | C_IC3g | -£3,509 |
| 2024 | 2024-12-30 | 1 | C_IC3g | -£1,934 |
| 2025 | 2025-06-01 | 1 | C_IC3g | -£538 |

**Single worst period: 2021 2021-12-31 SP1 (C_IC3g, -£4,092)** — exposure from gas supply anchor at year-end pricing.

> SP = settlement period (1-48; SP1 = 00:00-00:30). Year-end gas exposure dominates from 2020 onward as C_IC3g position grows.

## BSC Credit Obligation and Regulatory Levy Breakdown

Elexon BSC credit posting requirement and annual levy costs.

| Year | BSC Credit £ | CM Levy £ | Mutualization £ | CCL £ | Gas Network £ |
|------|-------------|----------|----------------|-------|--------------|
| 2016 | £30 | £37 | — | £189 | £479 |
| 2017 | £559 | £1,985 | — | £11,227 | £898 |
| 2018 | £1,019 | £9,401 | — | £17,545 | £905 |
| 2019 | £1,851 | £32,051 | — | £42,580 | £50,388 |
| 2020 | £2,375 | £56,674 | — | £69,608 | £47,215 |
| 2021 | £5,288 | £50,148 | £41,818 | £72,054 | £50,441 |
| 2022 | £10,199 | £37,170 | £100,685 | £71,853 | £54,433 |
| 2023 | £6,726 | £51,399 | £13,891 | £72,499 | £79,700 |
| 2024 | £3,278 | £69,368 | £2,019 | £73,612 | £76,429 |
| 2025 | £5,008 | £31,480 | £866 | £31,649 | £31,816 |

**Peak BSC credit obligation: 2022 (£10,199)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 14 | £167,078 | £91,247 | £7,407 | £11,934 |
| 2017 | 1 | £3,161,514 | £1,896,886 | £839,325 | £3,161,514 |
| 2018 | 1 | £1,545,857 | £922,297 | £433,679 | £1,545,857 |
| 2019 | 2 | £6,482,765 | £2,441,044 | -£46,798 | £3,241,383 |
| 2020 | 1 | £2,775,476 | £1,117,277 | £14,686 | £2,775,476 |

**Best revenue/customer cohort: 2019 (£3,241,383/customer)**
**Best net margin cohort: 2017 (£839,325)**
**Loss cohort: 2019 (net -£46,798)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £167 | — | 108 |
| 2017 | +£2,722 | £37,352 | £1,361 | — | 168 |
| 2018 | +£9,938 | £65,913 | £2,388 | — | 180 |
| 2019 | +£28,434 | £165,083 | £6,221 | — | 204 |
| 2020 | +£35,468 | £239,156 | £6,309 | — | 204 |
| 2021 | +£15,152 | £249,026 | £9,215 | — | 192 |
| 2022 | -£50,342 CREDIT | £259,289 | £35,881 | 1 | 148 |
| 2023 | +£65,429 | £274,578 | £13,841 | 1 | 144 |
| 2024 | +£111,030 | £310,631 | £11,543 | 1 | 129 |
| 2025 | +£47,631 | £137,698 | £4,995 | — | 54 |

**CfD turned CREDIT in 2022: -£50,342 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2022 (£35,881)**

> CfD (Contracts for Difference): when wholesale > strike price, generators repay;
> the net credit is passed through as a negative levy on supplier bills.

## Segment Gross Margin Attribution

Gross margin (£) by customer segment and year.

| Year | resi electricity | resi gas | SME electricity | I&C electricity | I&C gas | Total |
|------|----------|----------|----------|----------|----------|-------|
| 2016 | £3,270 | £811 | £2,733 | £0 | £0 | £6,814 |
| 2017 | £4,985 | £1,430 | £3,384 | £114,290 | £0 | £124,089 |
| 2018 | £5,056 | £1,363 | £3,198 | £254,070 | £0 | £263,686 |
| 2019 | £5,779 | £1,432 | £4,045 | £617,503 | £74,626 | £703,386 |
| 2020 | £5,681 | £1,218 | £4,235 | £706,489 | £75,972 | £793,595 |
| 2021 | £5,363 | £537 | £4,488 | £680,595 | £82,255 | £773,238 |
| 2022 | £3,756 | -£762 | £3,742 | £965,650 | £91,118 | £1,063,504 |
| 2023 | £7,213 | -£575 | £4,478 | £788,885 | £121,515 | £921,516 |
| 2024 | £8,488 | £762 | £1,521 | £1,160,619 | £123,652 | £1,295,042 |
| 2025 | £3,616 | £0 | £0 | £466,756 | £53,509 | £523,881 |

**Best gross margin year: 2024 (£1,295,042)** | **Worst: 2016 (£6,814)**
**Loss-making: resi gas in 2022 (£-762)**
**Loss-making: resi gas in 2023 (£-575)**


## Price Cap Headroom (Tariff vs SVT)

Percentage difference between contracted unit rate and SVT (price cap) at term start.
Negative = below cap (headroom). Positive = above cap (I&C terms; SVT applies to resi only).

| Year | Terms | Avg vs SVT% | Above Cap | Min% | Max% |
|------|-------|-------------|-----------|------|------|
| 2016 | 3 | -6.3% | 0/3 | -6.7% | +-5.8% |
| 2017 | 3 | -14.3% | 0/3 | -15.9% | +-12.4% |
| 2018 | 4 | -1.2% | 1/4 | -3.3% | +0.5% |
| 2019 | 4 | -18.8% | 1/4 | -29.5% | +12.4% |
| 2020 | 10 | -30.0% | 0/10 | -68.7% | +-18.0% |
| 2021 | 9 | +9.1% | 5/9 | -12.0% | +63.7% |
| 2022 | 7 | +11.5% | 4/7 | -66.3% | +95.6% |
| 2023 | 7 | -37.2% | 0/7 | -60.5% | +-12.9% |
| 2024 | 7 | -24.2% | 0/7 | -54.9% | +-9.1% |
| 2025 | 2 | -4.8% | 1/2 | -23.6% | +14.0% |

**Best headroom year: 2023 (avg 37.2% below SVT)**
**Largest above-SVT year: 2022** (4/7 terms above — note: I&C customers exempt from SVT cap)

> SVT (Standard Variable Tariff) = Ofgem price cap. Residential tariffs must not exceed SVT.
> I&C/SME terms above SVT are expected during crisis years when wholesale >cap.

## Portfolio Stress Test History

Retrospective RAG status: would year-end treasury have survived each scenario?
Credit facility: £2M. Weekly burn estimated at 1% of year-end treasury.

| Year | Treasury £ | Mkt Spike | Credit | Demand | Liquidity | Combined |
|------|-----------|----------|----------|----------|----------|----------|
| 2016 | £2,467,424 | AMBER | RED | GREEN | AMBER | RED |
| 2017 | £2,498,127 | AMBER | RED | GREEN | AMBER | RED |
| 2018 | £2,486,792 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,607,298 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,901,196 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,923,134 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,071,857 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,177,752 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,539,953 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,591,886 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 45.2% | £1,181 | £605 | 1.53% |
| 2017 | 14 | 33.5% | £25,052 | £8,975 | 1.79% |
| 2018 | 15 | 41.6% | £40,297 | £17,689 | 1.96% |
| 2019 | 17 | 40.1% | £97,020 | £41,484 | 1.87% |
| 2020 | 18 | 40.2% | £103,400 | £44,189 | 2.06% |
| 2021 | 16 | 29.1% | £152,735 | £48,427 | 1.94% |
| 2022 | 14 | 21.3% | £306,031 | £76,053 | 1.98% |
| 2023 | 12 | 23.0% | £288,606 | £76,879 | 2.21% |
| 2024 | 12 | 38.4% | £254,378 | £107,944 | 2.13% |
| 2025 | 9 | 36.8% | £138,093 | £58,252 | 3.01% |

**Best EBIT%: 2016 (45.2%)** | **Worst EBIT%: 2022 (21.3%)**
**Peak revenue/customer: 2022 (£306,031)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Churn Prediction Calibration

How well the company estimated churn probability versus actual simulation outcomes.

| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |
|----------|------|----------------|-----------------|-------|---------|
| C3 | 2020-06 | 32.0% | 0.0% | -32.0pp | UNDERESTIMATED |
| C1 | 2021-12 | 32.0% | 3.8% | -28.2pp | UNDERESTIMATED |
| C5 | 2021-12 | 35.0% | 82.7% | +47.7pp | OVERESTIMATED |
| C2 | 2022-03 | 26.0% | 6.7% | -19.3pp | UNDERESTIMATED |
| C6 | 2024-03 | 38.0% | 24.7% | -13.3pp | UNDERESTIMATED |
| C4 | 2024-09 | 32.0% | 0.0% | -32.0pp | UNDERESTIMATED |

**Outcomes: 5 underestimated / 0 accurate / 1 overestimated**
**Mean absolute error: 28.7pp**
**Systematic bias: company consistently UNDER-predicted churn risk.**

> Company churn estimates derived from company-observable signals (bill shock,
> margin feedback, renewal history) without access to the simulation's internal
> churn parameters — epistemic gap is expected and realistic for a small supplier.

## Tariff Estimation Accuracy

Mean and maximum absolute error between company tariff estimates and actual outturn.

| Year | Observations | Mean Abs Error | Max Abs Error | Accuracy |
|------|-------------|---------------|--------------|----------|
| 2016 | 17 | 15.1% | 29.1% | POOR |
| 2017 | 14 | 16.6% | 46.6% | POOR |
| 2018 | 16 | 12.1% | 27.7% | MODERATE |
| 2019 | 19 | 11.0% | 37.2% | MODERATE |
| 2020 | 22 | 12.5% | 33.8% | MODERATE |
| 2021 | 17 | 14.5% | 44.5% | MODERATE |
| 2022 | 15 | 10.2% | 23.2% | MODERATE |
| 2023 | 14 | 20.0% | 40.0% | POOR |
| 2024 | 13 | 9.7% | 22.6% | GOOD |
| 2025 | 2 | 33.1% | 33.1% | POOR |

**Best accuracy year (n≥5): 2024 (9.7% mean error)**
**Worst accuracy year (n≥5): 2023 (20.0% mean error)**

> Errors reflect the company's information gap: forward curves are approximations;
> the company cannot observe simulation wholesale cost internals (epistemic blindfold).

## Dynamic Pricing Activity

Rate adjustments driven by the margin feedback loop and emergency reprice events.

| Year | Adjustments | Avg Delta £/MWh | Up | Down | Emergency |
|------|------------|-----------------|-----|------|-----------|
| 2016 | 4 | -0.6 | 1 | 3 | 0 |
| 2017 | 13 | -1.3 | 1 | 12 | 0 |
| 2018 | 14 | +2.4 | 6 | 8 | 2 |
| 2019 | 15 | +1.4 | 5 | 10 | 2 |
| 2020 | 18 | +3.3 | 9 | 9 | 2 |
| 2021 | 14 | +11.3 | 14 | 0 | 6 |
| 2022 | 11 | +18.1 | 10 | 1 | 6 |
| 2023 | 11 | +9.9 | 8 | 3 | 8 |
| 2024 | 10 | +8.0 | 6 | 4 | 3 |
| 2025 | 2 | +0.6 | 1 | 1 | 0 |

**Total adjustments 2016-2025: 112** | **Peak avg adjustment: 2022 (+18.1 £/MWh)**
**Emergency reprices: 29 total** (8 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £11,545 | £3,848 | — |
| 2017 | 9 | £37,275 | £4,142 | +£25,730 |
| 2018 | 10 | £1,010,782 | £101,078 | +£973,507 |
| 2019 | 11 | £1,444,250 | £131,295 | +£433,468 |
| 2020 | 13 | £2,730,620 | £210,048 | +£1,286,370 |
| 2021 | 13 | £2,660,328 | £204,641 | £-70,292 |
| 2022 | 14 | £2,851,609 | £203,686 | +£191,281 |
| 2023 | 14 | £2,865,226 | £204,659 | +£13,617 |
| 2024 | 14 | £3,310,891 | £236,492 | +£445,665 |
| 2025 | 14 | £3,464,907 | £247,493 | +£154,016 |

**Peak portfolio CLV: 2025 (£3,464,907)** | **Earliest/lowest: 2016 (£11,545)**
**Largest YoY gain: 2020 (+£1,286,370)**
**Largest YoY fall: 2021 (£-70,292)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | 51.2% | — | — | — | — |
| 2017 | £350,729.34 | £111,689.79 | £113,395.24 | £125,644.31 | 35.8% | +£335,374.73 | +£108,093.26 | +£109,503.00 | +£117,778.47 |
| 2018 | £604,451.47 | £174,111.82 | £165,010.73 | £265,328.92 | 43.9% | +£253,722.13 | +£62,422.03 | +£51,615.49 | +£139,684.61 |
| 2019 | £1,649,332.87 | £497,647.48 | £446,452.22 | £705,233.17 | 42.8% | +£1,044,881.40 | +£323,535.66 | +£281,441.49 | +£439,904.24 |
| 2020 | £1,861,191.07 | £432,681.10 | £633,114.40 | £795,395.57 | 42.7% | +£211,858.20 | £-64,966.38 | +£186,662.18 | +£90,162.40 |
| 2021 | £2,443,753.01 | £982,445.98 | £686,468.74 | £774,838.29 | 31.7% | +£582,561.94 | +£549,764.88 | +£53,354.34 | £-20,557.28 |
| 2022 | £4,284,429.70 | £2,409,566.66 | £810,117.20 | £1,064,745.84 | 24.9% | +£1,840,676.69 | +£1,427,120.68 | +£123,648.46 | +£289,907.55 |
| 2023 | £3,463,272.90 | £1,655,423.63 | £885,296.40 | £922,552.86 | 26.6% | £-821,156.80 | £-754,143.03 | +£75,179.20 | £-142,192.98 |
| 2024 | £3,052,539.42 | £939,927.56 | £817,278.82 | £1,295,333.04 | 42.4% | £-410,733.47 | £-715,496.07 | £-68,017.58 | +£372,780.18 |
| 2025 | £1,242,833.84 | £458,164.16 | £260,405.04 | £524,264.63 | 42.2% | £-1,809,705.59 | £-481,763.40 | £-556,873.78 | £-771,068.41 |

**Best GM year: 2016 (51.2%)** | **Worst GM year: 2022 (24.9%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Risk Committee Activity (2016-2025)

Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.

| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |
|------|----------|----------------------|----------------------|-----------------|
| 2016 | 13 | £28 | £9 | 1 |
| 2017 | 12 | £1,005 | £401 | 3 |
| 2022 | 9 | £55,845 | £20,657 | 8 |
| 2023 | 4 | £129,341 | £49,307 | 9 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £129,341 | Unique accounts ever adjusted: 11

**Most frequently adjusted accounts:**
- C1: 22 sessions
- C7: 19 sessions
- C2: 13 sessions
- C5: 12 sessions
- C6: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £7,557.39 | Median churn: 32% | Total portfolio CLV: £6,040,227.71

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £2,474,541.14 | 8% | 10.1 periods |
| C_IC1 | £1,460,474.61 | 8% | 10.2 periods |
| C_IC4 | £1,255,073.05 | 14% | 8.9 periods |
| C_IC2 | £788,502.26 | 8% | 9.8 periods |

Quadrant CLV: £5,978,591.07 (99% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C6 | £15,097.81 | 38% | 8.9 periods |
| C5 | £8,448.42 | 35% | 9.5 periods |
| C9 | £7,557.39 | 38% | 9.0 periods |

Quadrant CLV: £31,103.63 (1% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C2 | £5,015.15 | 26% | 10.0 periods |

Quadrant CLV: £5,015.15 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £7,256.17 | 38% | 8.8 periods |
| C7 | £6,647.70 | 35% | 9.9 periods |
| C3 | £4,931.93 | 32% | 9.4 periods |
| C1 | £3,758.26 | 32% | 9.5 periods |
| C4 | £2,923.81 | 32% | 9.7 periods |

Quadrant CLV: £25,517.87 (0% of portfolio)

**Board action: CRITICAL quadrant has 3 account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**

## Customer Experience & Service Quality

| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |
|------|----------------|---------------|-------------|---------|------|
| 2016 | 0.829 | 0.047 | 0 | 0 |  |
| 2017 | 0.818 | 0.047 | 0 | 0 |  |
| 2018 | 0.810 | 0.047 | 0 | 0 |  |
| 2019 | 0.824 | 0.047 | 0 | 0 |  |
| 2020 | 0.830 | 0.043 | 1 | 0 |  |
| 2021 | 0.829 | 0.045 | 2 | 0 |  |
| 2022 | 0.791 | 0.056 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.808 | 0.048 | 0 | 0 |  |
| 2024 | 0.813 | 0.046 | 2 | 0 |  |
| 2025 | 0.777 | 0.059 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.5% | **Average billing clarity:** 0.816 | **Average complaint probability:** 0.047

**Acquisition performance:** 5 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2025** (0.777) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

## Bill Shock Analysis

Bill shock events occur when a customer's bill increases >20% vs the prior bill.
Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.

| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |
|------|------------|--------|-------|------------|------|
| 2016 | 19.7% | 31 | 108 | 29% |  |
| 2017 | 16.5% | 50 | 168 | 30% |  |
| 2018 | 15.9% | 60 | 180 | 33% |  |
| 2019 | 17.0% | 66 | 204 | 32% |  |
| 2020 | 14.5% | 53 | 204 | 26% |  |
| 2021 | 15.9% | 51 | 192 | 27% |  |
| 2022 | 33.8% | 61 | 148 | 41% | **HIGH** |
| 2023 | 17.2% | 42 | 144 | 29% |  |
| 2024 | 15.9% | 33 | 129 | 26% |  |
| 2025 | 23.6% | 20 | 54 | 37% | ELEVATED |

**Crisis peak: 2022** — 33.8% average shock. Energy crisis drove wholesale costs above locked tariff rates,
causing step-change increases at every renewal. SLC 21: suppliers must issue
renewal notice 42 days before contract end, giving customers time to switch.

## Policy Cost & Levy Breakdown

UK energy levies collected through supplier bills. Policy costs are non-commodity costs
passed through to customers. CfD levy went negative in 2022 (crisis: spot exceeded strike prices;
renewable generators repaid back via levy mechanism).

| Year | RO | CfD | CCL | CM | FiT | Total Policy | Network |
|------|----|-----|-----|----|-----|-------------|---------|
| 2016 | £1,161.79 | £7.45 | £189.19 | £37.24 | £305.34 | £1,701.01 | £3,202.38 |
| 2017 | £37,352.08 | £2,721.53 | £11,227.21 | £1,985.49 | £9,991.40 | £63,277.71 | £26,300.83 |
| 2018 | £65,913.01 | £9,937.67 | £17,545.09 | £9,400.73 | £17,390.54 | £120,187.04 | £38,779.00 |
| 2019 | £165,082.60 | £28,433.77 | £42,580.25 | £32,050.88 | £44,423.38 | £312,570.88 | £88,630.41 |
| 2020 | £239,155.88 | £35,468.03 | £69,608.00 | £56,674.42 | £70,177.06 | £471,083.40 | £124,849.03 |
| 2021 | £249,025.89 | £15,151.61 | £72,053.98 | £50,147.85 | £63,433.22 | £491,631.00 | £124,693.38 |
| 2022 | £259,288.78 | **£-50,342.40** | £71,853.14 | £37,169.98 | £69,906.78 | £488,561.07 | £134,602.75 |
| 2023 | £274,577.82 | £65,429.09 | £72,498.67 | £51,398.91 | £75,853.52 | £553,649.11 | £140,330.40 |
| 2024 | £310,630.69 | £111,030.29 | £73,611.67 | £69,368.01 | £83,373.29 | £650,032.69 | £144,360.33 |
| 2025 | £137,697.53 | £47,631.22 | £31,649.06 | £31,479.91 | £36,676.04 | £285,999.79 | £61,947.94 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.01 (2016) → £285,999.79 (2025). CAGR: 76.7%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £881.72 | £296.53 | £9,021.95 | £1,388.28 | 13.3% | YES |
| 2017 | £30,515.34 | £463.34 | £233,118.78 | £2,660.42 | 1.1% | YES |
| 2018 | £99,520.47 | £374.66 | £434,673.35 | £3,113.94 | 0.7% | YES |
| 2019 | £218,347.04 | £466.22 | £1,063,259.85 | £137,770.25 | 11.5% | YES |
| 2020 | £112,839.89 | £4,431.62 | £1,105,084.69 | £121,133.74 | 9.9% | YES |
| 2021 | £60,827.28 | £-2,002.27 | £1,457,675.52 | £297,851.59 | 17.0% | **NO** |
| 2022 | £306,819.99 | £-49,538.20 | £2,884,682.97 | £588,329.77 | 16.9% | **NO** |
| 2023 | £84,536.28 | £-32,311.49 | £2,279,501.21 | £297,197.78 | 11.5% | **NO** |
| 2024 | £356,350.21 | £-37,246.05 | £1,963,690.21 | £270,490.62 | 12.1% | **NO** |
| 2025 | £112,449.98 | £-19,724.42 | £849,591.15 | £132,453.71 | 13.5% | **NO** |

**Gas has been loss-making since 2021** (5 consecutive years). Electricity cross-subsidises gas supply.

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £-45,603.97 | — | Current strategy |
| EXIT_GAS | £53,808.39 | £99,412.36 | Remove gas; model elec churn risk |
| REPRICE_GAS | £90,920.50 | £136,524.47 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-2,024.35 | -13.99x | +19.5% |
| C_IC3g | £-134,500.12 | -0.72x | +7.3% |

**Accretive gas accounts:** C1g (£645.06), C2g (£801.77), C3g (£287.57) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £134790 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,754,857.05 | £50,303.67 | £1,375,391.26 | 27.3x | Strong |
| I&C gas | £622,647.03 | £186,915.65 | £-134,500.12 | -0.7x | CAPITAL DESTROYER |
| SME electricity | £31,825.77 | £341.67 | £3,541.89 | 10.4x | Moderate |
| resi electricity | £53,205.96 | £569.49 | £4,155.03 | 7.3x | Moderate |
| resi gas | £6,215.25 | £200.69 | £-289.95 | -1.4x | CAPITAL DESTROYER |

**Gas Segment Finding:**
- Gas supply legs are net-negative over the simulation period (£-134,790.07 net on £187,116.34 capital)
- Electricity segments (£1,383,088.18 net) cross-subsidise gas retention
- Board decision required: is dual-fuel gas justified by CLV, or does it need pricing reform?

## Portfolio Concentration Risk

Revenue concentration analysis across 19 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2250** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,293,735.81 (98.7% of total positive margin)
- resi: £54,123.21 (0.8% of total positive margin)
- SME: £29,604.88 (0.5% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,876,860.68 | 29.4% | 5% | £93,843.03 |
| C_IC3 | I&C | £1,791,927.68 | 28.1% | 8% | £143,354.21 |
| C_IC4 | I&C | £1,100,681.25 | 17.3% | 0% | £0.00 |
| C_IC2 | I&C | £910,849.13 | 14.3% | 5% | £45,542.46 |
| C_IC3g | I&C | £613,417.06 | 9.6% | 0% | £0.00 |

**Concentration Risk Warning:**
- I&C segment accounts for 98.7% of total portfolio margin
- Resi and SME segments are effectively margin-neutral at portfolio scale
- A single large I&C departure would remove 14-29% of all margin
- Board action: diversify acquisition pipeline toward profitable resi/SME to reduce I&C dependency

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 112 renewal(s) (26 gas) based on recent portfolio-wide margin rates: 61 surcharge(s), 51 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | 7.4% | +0.3% | £131.49/MWh | £131.86/MWh |
| C1g | gas | 2016-12-31 | 19.6% | -5.0% | £27.63/MWh | £26.25/MWh |
| C5 | electricity | 2016-12-31 | 8.7% | -0.4% | £131.49/MWh | £131.01/MWh |
| C7 | electricity | 2016-12-31 | 9.4% | -0.7% | £131.49/MWh | £130.56/MWh |
| C2 | electricity | 2017-04-01 | 11.5% | -1.8% | £127.97/MWh | £125.73/MWh |
| C2g | gas | 2017-04-01 | 19.8% | -5.0% | £34.54/MWh | £32.81/MWh |
| C6 | electricity | 2017-04-01 | 10.7% | -1.4% | £127.97/MWh | £126.23/MWh |
| C8 | electricity | 2017-04-01 | 9.9% | -0.9% | £127.97/MWh | £126.77/MWh |
| C3 | electricity | 2017-07-01 | 11.2% | -1.6% | £122.23/MWh | £120.28/MWh |
| C3g | gas | 2017-07-01 | 20.5% | -5.0% | £24.33/MWh | £23.11/MWh |
| C9 | electricity | 2017-07-01 | 10.8% | -1.4% | £122.23/MWh | £120.50/MWh |
| C4 | electricity | 2017-10-01 | 10.8% | -1.4% | £111.62/MWh | £110.07/MWh |
| C4g | gas | 2017-10-01 | 18.4% | -5.0% | £27.48/MWh | £26.10/MWh |
| C1 | electricity | 2017-12-31 | 11.9% | -1.9% | £120.10/MWh | £117.78/MWh |
| C1g | gas | 2017-12-31 | 15.4% | -3.7% | £34.79/MWh | £33.49/MWh |
| C5 | electricity | 2017-12-31 | 8.9% | -0.4% | £120.10/MWh | £119.57/MWh |
| C7 | electricity | 2017-12-31 | 3.7% | +2.1% | £120.10/MWh | £122.67/MWh |
| C_IC1 | electricity | 2018-01-31 | -17.8% | +12.9% | £112.24/MWh | £126.69/MWh |
| C2 | electricity | 2018-04-01 | -6.6% | +7.3% | £133.89/MWh | £143.63/MWh |
| C2g | gas | 2018-04-01 | 15.4% | -3.7% | £38.21/MWh | £36.79/MWh |
| C6 | electricity | 2018-04-01 | -4.0% | +6.0% | £133.89/MWh | £141.94/MWh |
| C8 | electricity | 2018-04-01 | 8.1% | -0.0% | £133.89/MWh | £133.83/MWh |
| C3 | electricity | 2018-07-01 | 10.1% | -1.0% | £128.29/MWh | £126.95/MWh |
| C3g | gas | 2018-07-01 | 13.6% | -2.8% | £29.63/MWh | £28.80/MWh |
| C9 | electricity | 2018-07-01 | 1.8% | +3.1% | £128.29/MWh | £132.29/MWh |
| C4 | electricity | 2018-10-01 | 1.9% | +3.0% | £145.00/MWh | £149.38/MWh |
| C4g | gas | 2018-10-01 | 13.7% | -2.8% | £34.60/MWh | £33.61/MWh |
| C1 | electricity | 2018-12-31 | 6.7% | +0.7% | £148.68/MWh | £149.67/MWh |
| C1g | gas | 2018-12-31 | 13.9% | -3.0% | £37.15/MWh | £36.05/MWh |
| C5 | electricity | 2018-12-31 | 9.2% | -0.6% | £148.68/MWh | £147.77/MWh |
| C7 | electricity | 2018-12-31 | 9.6% | -0.8% | £148.68/MWh | £147.52/MWh |
| C_IC2 | electricity | 2019-01-31 | -29.8% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -20.1% | +14.1% | £128.22/MWh | £146.25/MWh |
| C2 | electricity | 2019-04-01 | 3.4% | +2.3% | £148.35/MWh | £151.78/MWh |
| C2g | gas | 2019-04-01 | 8.7% | -0.3% | £32.94/MWh | £32.82/MWh |
| C6 | electricity | 2019-04-01 | 7.6% | +0.2% | £148.35/MWh | £148.61/MWh |
| C8 | electricity | 2019-04-01 | 27.0% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 19.5% | -5.0% | £127.03/MWh | £120.68/MWh |
| C3g | gas | 2019-07-01 | 11.5% | -1.8% | £23.62/MWh | £23.21/MWh |
| C9 | electricity | 2019-07-01 | 10.0% | -1.0% | £127.03/MWh | £125.77/MWh |
| C4 | electricity | 2019-10-01 | 7.9% | +0.1% | £126.72/MWh | £126.77/MWh |
| C4g | gas | 2019-10-01 | 15.6% | -3.8% | £20.41/MWh | £19.63/MWh |
| C1 | electricity | 2019-12-31 | 10.5% | -1.3% | £127.44/MWh | £125.83/MWh |
| C1g | gas | 2019-12-31 | 13.0% | -2.5% | £26.17/MWh | £25.52/MWh |
| C5 | electricity | 2019-12-31 | 10.1% | -1.1% | £127.44/MWh | £126.10/MWh |
| C7 | electricity | 2019-12-31 | 8.9% | -0.4% | £127.44/MWh | £126.88/MWh |
| C_IC3 | electricity | 2020-01-01 | 7.5% | +0.3% | £47.59/MWh | £47.71/MWh |
| C_IC3g | gas | 2020-01-01 | 21.2% | -5.0% | £16.25/MWh | £15.44/MWh |
| C_IC2 | electricity | 2020-03-01 | -59.3% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -51.9% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 18.1% | -5.0% | £22.80/MWh | £21.66/MWh |
| C6 | electricity | 2020-03-31 | -47.2% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -16.3% | +12.1% | £125.12/MWh | £140.30/MWh |
| C_IC1 | electricity | 2020-03-31 | 20.1% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 16.5% | -4.3% | £113.43/MWh | £108.59/MWh |
| C9 | electricity | 2020-06-30 | 16.5% | -4.3% | £113.43/MWh | £108.59/MWh |
| C4 | electricity | 2020-09-30 | 11.2% | -1.6% | £124.42/MWh | £122.46/MWh |
| C4g | gas | 2020-09-30 | 19.9% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 9.7% | -0.8% | £133.55/MWh | £132.43/MWh |
| C1g | gas | 2020-12-30 | 13.7% | -2.9% | £28.99/MWh | £28.16/MWh |
| C5 | electricity | 2020-12-30 | 4.6% | +1.7% | £133.55/MWh | £135.83/MWh |
| C7 | electricity | 2020-12-30 | -3.1% | +5.5% | £133.55/MWh | £140.94/MWh |
| C_IC3 | electricity | 2020-12-31 | -4.3% | +6.2% | £50.65/MWh | £53.77/MWh |
| C_IC3g | gas | 2020-12-31 | 6.7% | +0.7% | £20.05/MWh | £20.18/MWh |
| C2 | electricity | 2021-03-31 | -20.8% | +14.4% | £175.90/MWh | £201.23/MWh |
| C2g | gas | 2021-03-31 | 5.9% | +1.1% | £36.20/MWh | £36.58/MWh |
| C6 | electricity | 2021-03-31 | -16.1% | +12.1% | £175.90/MWh | £197.10/MWh |
| C8 | electricity | 2021-03-31 | -11.9% | +9.9% | £175.90/MWh | £193.40/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.6% | +6.3% | £138.90/MWh | £147.64/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.9% | +3.5% | £113.97/MWh | £117.99/MWh |
| C9 | electricity | 2021-06-30 | 1.2% | +3.4% | £170.38/MWh | £176.20/MWh |
| C4 | electricity | 2021-09-30 | -2.3% | +5.2% | £205.15/MWh | £215.76/MWh |
| C4g | gas | 2021-09-30 | 0.2% | +3.9% | £53.99/MWh | £56.09/MWh |
| C1 | electricity | 2021-12-30 | 5.0% | +1.5% | £311.83/MWh | £316.55/MWh |
| C5 | electricity | 2021-12-30 | 5.0% | +1.5% | £311.83/MWh | £316.55/MWh |
| C7 | electricity | 2021-12-30 | 5.0% | +1.5% | £311.83/MWh | £316.55/MWh |
| C_IC3 | electricity | 2021-12-31 | -22.7% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -18.7% | +13.4% | £109.48/MWh | £124.11/MWh |
| C2 | electricity | 2022-03-31 | -23.1% | +15.0% | £361.95/MWh | £416.24/MWh |
| C6 | electricity | 2022-03-31 | -16.8% | +12.4% | £361.95/MWh | £406.81/MWh |
| C8 | electricity | 2022-03-31 | 5.1% | +1.4% | £361.95/MWh | £367.10/MWh |
| C_IC2 | electricity | 2022-04-30 | -9.5% | +8.7% | £269.81/MWh | £293.39/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.0% | +7.0% | £239.42/MWh | £256.20/MWh |
| C9 | electricity | 2022-06-30 | 4.4% | +1.8% | £255.09/MWh | £259.72/MWh |
| C4 | electricity | 2022-09-30 | 7.2% | +0.4% | £404.86/MWh | £406.38/MWh |
| C4g | gas | 2022-09-30 | -22.1% | +15.0% | £183.79/MWh | £211.36/MWh |
| C7 | electricity | 2022-12-30 | 8.9% | -0.5% | £266.73/MWh | £265.47/MWh |
| C_IC3 | electricity | 2022-12-31 | 0.4% | +3.8% | £168.36/MWh | £174.76/MWh |
| C_IC3g | gas | 2022-12-31 | -40.1% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -11.8% | +9.9% | £319.17/MWh | £350.73/MWh |
| C6 | electricity | 2023-03-31 | -0.9% | +4.5% | £319.17/MWh | £333.40/MWh |
| C8 | electricity | 2023-03-31 | 5.7% | +1.1% | £319.17/MWh | £322.83/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.5% | +14.8% | £171.46/MWh | £196.75/MWh |
| C_IC1 | electricity | 2023-06-29 | -16.6% | +12.3% | £163.19/MWh | £183.28/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.10/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.03/MWh |
| C4g | gas | 2023-09-30 | -44.2% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 23.7% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -15.6% | +11.8% | £51.89/MWh | £58.02/MWh |
| C2_2 | electricity | 2024-03-30 | 16.3% | -4.2% | £207.71/MWh | £199.09/MWh |
| C6 | electricity | 2024-03-30 | 9.9% | -0.9% | £207.71/MWh | £205.78/MWh |
| C8 | electricity | 2024-03-30 | 9.9% | -0.9% | £207.71/MWh | £205.78/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.0% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.1% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.5% | +3.7% | £195.97/MWh | £203.27/MWh |
| C7 | electricity | 2024-12-29 | 0.5% | +3.7% | £243.79/MWh | £252.87/MWh |
| C_IC3 | electricity | 2024-12-30 | 18.9% | -5.0% | £116.37/MWh | £110.55/MWh |
| C_IC3g | gas | 2024-12-30 | -17.0% | +12.5% | £50.47/MWh | £56.77/MWh |
| C2_2 | electricity | 2025-03-30 | 9.1% | -0.5% | £284.89/MWh | £283.36/MWh |
| C8 | electricity | 2025-03-30 | 6.1% | +0.9% | £284.89/MWh | £287.56/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **5** | Blind misses: **5** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 4 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £3,964.62 | deliberate: £0.00 | total: £3,964.62

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.32 | Yes | £585.36 |
| C1 | 2021-12-30 | Blind miss | 0.04 | 0.32 | Yes | £-178.13 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.26 | No | £236.63 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.38 | Yes | £2,852.27 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.32 | Yes | £468.49 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C2+C2g | £717.96 | £801.77 | £1,519.73 | Yes |
| C1+C1g | £423.16 | £645.06 | £1,068.22 | Yes |
| C3+C3g | £203.02 | £287.57 | £490.59 | Yes |
| C4+C4g | £139.48 | £-2,024.35 | £-1,884.86 | No |
| C_IC3+C_IC3g | £87,702.48 | £-134,500.12 | £-46,797.64 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-134,790.07.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,248,298.11 across 19 billing accounts. Revenue: £14,132,689.79.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,161,514.11 | £1,896,886.37 | £18,589.52 | £839,324.69 | 26.5% |
| 2 | C_IC2 | fixed | £1,545,856.91 | £922,296.59 | £8,618.53 | £433,678.54 | 28.1% |
| 3 | C_IC3 | pass_through | £4,650,185.41 | £1,818,396.93 | £23,095.62 | £87,702.48 | 1.9% |
| 4 | C_IC4 | flex | £2,775,475.73 | £1,117,277.15 | £0.00 | £14,685.55 | 0.5% |
| 5 | C6 | fixed | £38,935.47 | £22,449.28 | £264.35 | £3,577.56 | 9.2% |
| 6 | C8 | fixed | £21,674.80 | £12,455.01 | £134.82 | £1,502.47 | 6.9% |
| 7 | C9 | fixed | £20,237.56 | £12,702.16 | £131.40 | £1,486.70 | 7.3% |
| 8 | C2_2 | fixed | £10,280.06 | £5,472.43 | £67.80 | £1,043.96 | 10.2% |
| 9 | C2g | fixed | £3,849.77 | £2,019.21 | £21.85 | £801.77 | 20.8% |
| 10 | C2 | fixed | £5,112.28 | £3,408.18 | £24.73 | £717.96 | 14.0% |
| 11 | C1g | fixed | £2,896.32 | £1,543.05 | £18.80 | £645.06 | 22.3% |
| 12 | C1 | fixed | £4,225.80 | £2,734.73 | £19.17 | £423.16 | 10.0% |
| 13 | C3g | fixed | £2,688.18 | £1,303.40 | £15.29 | £287.57 | 10.7% |
| 14 | C3 | fixed | £3,625.65 | £2,385.79 | £14.76 | £203.02 | 5.6% |
| 15 | C4 | fixed | £6,275.34 | £3,315.69 | £37.48 | £139.48 | 2.2% |
| 16 | C5 | fixed | £15,191.61 | £9,376.49 | £77.32 | £-35.67 | -0.2% |
| 17 | C7 | fixed | £21,708.98 | £10,731.97 | £139.32 | £-1,361.73 | -6.3% |
| 18 | C4g | fixed | £10,375.92 | £1,349.59 | £144.75 | £-2,024.35 | -19.5% |
| 19 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £186,915.65 | £-134,500.12 | -7.3% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,132,690 | 100.0% |
| Wholesale cost | -£7,663,939 | 54.2% |
| **Gross supply margin** | **£6,468,751** | **45.8%** |
| Policy + Network costs | -£4,982,122 | 35.3% |
| Capital cost | -£238,331 | 1.7% |
| **Net supply margin** | **£1,248,298** | **8.8%** |

> *The ledger's `net_margin_gbp` (£6,244,187) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,133,032 | 47.4% | 11.3% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | -7.3% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £54,127 | 58.8% | 6.5% | CMA 3-8% | ✓ |
| resi/elec | £82,860 | 57.6% | 3.8% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £19,810 | 31.4% | -1.5% | Ofgem CMA 2-4% | ✓ |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: PASS** — all segments within benchmarks.
## Transaction Log

Total events: 3,297,294

| Event type | Count |
|------------|-------|
| acquisition_gate_event | 1 |
| acquisition_spend_event | 4 |
| bad_debt_event | 1,531 |
| billing_event | 1,531 |
| capital_charge_event | 1,587,774 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,531 |
| payment_received_event | 1,531 |
| settlement_event | 1,701,746 |
| vat_remittance_event | 1,531 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £19,926,863.00 |
|   Less: VAT remitted to HMRC | (£958,974.77) |
| = Revenue (ex-VAT) | £18,967,888.23 |
| Less: non-commodity pass-through | (£4,821,431.04) |
| Wholesale cost (settlement events) | (£7,663,938.73) |
| Gross margin | £6,482,518.46 |
| Capital charges | (£238,331.17) |
| Net margin | £6,244,187.30 |

_Cash reconciliation: of £19,926,863.00 billed, bad debt of £398,642.62 was written off, leaving £19,528,220.39 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £6,804,519.45._

| Acquisition spend | (£1,100.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £6,237,387.30 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | £234.62 | £834.62 | £6,944.88 (45.2%) |
| 2017 | £350,729.34 | £111,689.79 | £113,395.24 | £125,644.31 | £6,284.18 | £6,884.18 | £117,487.04 (33.5%) |
| 2018 | £604,451.47 | £174,111.82 | £165,010.73 | £265,328.92 | £11,865.24 | £12,465.24 | £251,331.62 (41.6%) |
| 2019 | £1,649,332.87 | £497,647.48 | £446,452.22 | £705,233.17 | £30,847.09 | £31,447.09 | £662,178.97 (40.1%) |
| 2020 | £1,861,191.07 | £432,681.10 | £633,114.40 | £795,395.57 | £38,318.75 | £39,068.75 | £748,927.69 (40.2%) |
| 2021 | £2,443,753.01 | £982,445.98 | £686,468.74 | £774,838.29 | £47,321.24 | £48,321.24 | £710,556.14 (29.1%) |
| 2022 | £4,284,429.70 | £2,409,566.66 | £810,117.20 | £1,064,745.84 | £84,909.37 | £85,509.37 | £913,537.92 (21.3%) |
| 2023 | £3,463,272.90 | £1,655,423.63 | £885,296.40 | £922,552.86 | £76,609.17 | £77,209.17 | £795,801.58 (23.0%) |
| 2024 | £3,052,539.42 | £939,927.56 | £817,278.82 | £1,295,333.04 | £64,892.08 | £66,042.08 | £1,173,212.11 (38.4%) |
| 2025 | £1,242,833.84 | £458,164.16 | £260,405.04 | £524,264.63 | £37,360.87 | £37,660.87 | £457,450.74 (36.8%) |
| **Total** | **£18,967,888.23** | | | | | | **£5,837,428.69 (30.8%)** |

**Best year:** 2024 — net £1,173,212.11 (38.4% margin)
**Worst year:** 2016 — net £6,944.88 (45.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,304,064.91 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,304,064.91** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,837,428.69 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,354.61 | +4.7% | £6,592.99 | £6,944.88 | +5.3% | AMBER |
| 2017 | £16,138.86 | £350,729.34 | +2073.2% | £7,252.29 | £117,487.04 | +1520.0% | RED |
| 2018 | £386,623.75 | £604,451.47 | +56.3% | £128,424.00 | £251,331.62 | +95.7% | RED |
| 2019 | £675,851.95 | £1,649,332.87 | +144.0% | £281,335.50 | £662,178.97 | +135.4% | RED |
| 2020 | £1,816,630.04 | £1,861,191.07 | +2.5% | £736,963.94 | £748,927.69 | +1.6% | GREEN |
| 2021 | £2,028,952.42 | £2,443,753.01 | +20.4% | £833,649.22 | £710,556.14 | -14.8% | AMBER |
| 2022 | £2,607,611.88 | £4,284,429.70 | +64.3% | £790,935.58 | £913,537.92 | +15.5% | RED |
| 2023 | £4,508,414.67 | £3,463,272.90 | -23.2% | £1,029,561.00 | £795,801.58 | -22.7% | RED |
| 2024 | £3,512,844.39 | £3,052,539.42 | -13.1% | £893,105.75 | £1,173,212.11 | +31.4% | RED |
| 2025 | £3,145,356.42 | £1,242,833.84 | -60.5% | £1,315,150.33 | £457,450.74 | -65.2% | RED |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 1 | 0 | 0% | £150.00 |
| 2021 | 2 | 0 | 0% | £400.00 |
| 2024 | 2 | 0 | 0% | £550.00 |

**Total:** 5 attempts, 0 wins (0% win rate), £1,100.00 total spend

**Operating overhead**

| Year | Fixed Cost |
|------|-----------|
| 2016 | (£600.00) |
| 2017 | (£600.00) |
| 2018 | (£600.00) |
| 2019 | (£600.00) |
| 2020 | (£600.00) |
| 2021 | (£600.00) |
| 2022 | (£600.00) |
| 2023 | (£600.00) |
| 2024 | (£600.00) |
| 2025 | (£300.00) |

**Total fixed cost:** £5,700.00 over simulation window
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,237,387.30

## 2016

**Trading & Risk**

- Net margin: £1,178.25 (gross £6,813.70, capital £86.34)
  - Electricity: gross £6,002.97, capital £78.97, net £881.72
  - Gas: gross £810.73, capital £7.36, net £296.53
- Treasury at year end: £2,467,424.50
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.23, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-01-31: treasury £2,466,648.39, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-03-01: treasury £2,466,660.65, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-03-31: treasury £2,466,672.63, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-04-30: treasury £2,466,683.74, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-05-30: treasury £2,466,694.75, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-06-29: treasury £2,466,705.34, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-07-29: treasury £2,466,716.06, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-08-28: treasury £2,466,726.80, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-09-27: treasury £2,466,737.73, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-10-27: treasury £2,466,748.64, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-11-26: treasury £2,466,759.45, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-12-26: treasury £2,466,771.39, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.25
- Worst single period: C6 on 2016-11-08 period 40, net margin £-0.36

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £3,848.23
  - By billing account: C1 £2,259.66, C5 £5,096.01, C7 £4,189.02
- Bill shock events (>=20%): 31 -- C1g 2016-05-31 (37%); C1g 2016-06-30 (29%); C1g 2016-10-31 (79%); C1g 2016-11-30 (46%); C5 2016-05-31 (27%); C5 2016-10-31 (40%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (77%); C7 2016-11-30 (52%); C2g 2016-05-31 (36%); C2g 2016-06-30 (34%); C2g 2016-10-31 (82%); C2g 2016-11-30 (53%); C6 2016-05-31 (25%); C6 2016-06-30 (23%); C6 2016-10-31 (40%); C6 2016-11-30 (46%); C8 2016-05-31 (40%); C8 2016-06-30 (40%); C8 2016-09-30 (22%); C8 2016-10-31 (100%); C8 2016-11-30 (68%); C3g 2016-10-31 (70%); C3g 2016-11-30 (48%); C9 2016-10-31 (74%); C9 2016-11-30 (58%); C4 2016-11-30 (28%); C4g 2016-11-30 (47%)
- Churn risk (accounts renewing in 2016): 3 at risk (≥20% churn prob): C1 29%, C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.30-£131.86/MWh, net margin £137.18
- C1g (gas): tariff £24.46-£26.25/MWh, net margin £101.24
- C2 (electricity): tariff £107.62/MWh, net margin £65.40
- C2g (gas): tariff £26.92/MWh, net margin £108.55
- C3 (electricity): tariff £98.21/MWh, net margin £21.61
- C3g (gas): tariff £21.93/MWh, net margin £40.58
- C4 (electricity): tariff £98.43/MWh, net margin £11.43
- C4g (gas): tariff £24.40/MWh, net margin £46.16
- C5 (electricity): tariff £117.30-£131.01/MWh, net margin £248.76
- C6 (electricity): tariff £107.62/MWh, net margin £6.12
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £234.27
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £120.80
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £36.15

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.829, average bill shock 19.7%, bad debt provision £166.66, avg complaint probability 4.7%
- Solvency signal: £274,158/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £2,034.44 vs. naked (unhedged) net margin: £10,920.39
- hedging cost £8,885.95 vs. a fully unhedged book (commodity-only: actual net £2,034.44 vs. naked net £10,920.39)
  - C1: actual £257.43 vs. naked £827.86 -- hedging cost £570.43
  - C1g: actual £207.55 vs. naked £516.14 -- hedging cost £308.59
  - C2: actual £83.88 vs. naked £370.88 -- hedging cost £287.00
  - C2g: actual £152.39 vs. naked £385.71 -- hedging cost £233.32
  - C3: actual £29.93 vs. naked £414.50 -- hedging cost £384.57
  - C3g: actual £77.50 vs. naked £396.79 -- hedging cost £319.29
  - C4: actual £48.51 vs. naked £261.09 -- hedging cost £212.58
  - C4g: actual £153.10 vs. naked £606.05 -- hedging cost £452.95
  - C5: actual £414.43 vs. naked £2,694.63 -- hedging cost £2,280.21
  - C6: actual £-19.99 vs. naked £1,068.86 -- hedging cost £1,088.85
  - C7: actual £395.13 vs. naked £1,939.88 -- hedging cost £1,544.75
  - C8: actual £175.42 vs. naked £784.40 -- hedging cost £608.98
  - C9: actual £59.16 vs. naked £653.59 -- hedging cost £594.44

**Year narrative:** 2016 produced a net gain of £1,178.25 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 31 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £30,978.68 (gross £124,089.41, capital £1,273.09)
  - Electricity: gross £122,659.84, capital £1,258.24, net £30,515.34
  - Gas: gross £1,429.57, capital £14.85, net £463.34
- Treasury at year end: £2,498,127.39
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.92 (avg 0.92), C7 0.91 (avg 0.91), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,467,429.20, C1->1.00, C5->1.00, C7->1.00, VaR (current £307.55 / stressed £98.11) ratio 3.13
  - 2017-02-24: treasury £2,467,435.20, C1->1.00, C5->1.00, C7->1.00, VaR (current £307.55 / stressed £98.11) ratio 3.13
  - 2017-03-26: treasury £2,467,441.63, C1->1.00, C5->1.00, C7->1.00, VaR (current £307.55 / stressed £98.11) ratio 3.13
  - 2017-04-25: treasury £2,467,778.39, C1->1.00, C5->1.00, C7->1.00, VaR (current £859.42 / stressed £329.85) ratio 2.61
  - 2017-05-25: treasury £2,467,778.80, C1->1.00, C5->1.00, C7->1.00, VaR (current £859.42 / stressed £329.85) ratio 2.61
  - 2017-06-24: treasury £2,467,780.28, C1->1.00, C5->1.00, C7->1.00, VaR (current £859.42 / stressed £329.85) ratio 2.61
  - 2017-07-24: treasury £2,467,956.57, C1->1.00, C5->1.00, C7->1.00, VaR (current £996.73 / stressed £394.58) ratio 2.53
  - 2017-08-23: treasury £2,467,961.22, C1->1.00, C5->1.00, C7->1.00, VaR (current £996.73 / stressed £394.58) ratio 2.53
  - 2017-09-22: treasury £2,467,964.95, C1->1.00, C5->1.00, C7->1.00, VaR (current £996.73 / stressed £394.58) ratio 2.53
  - 2017-10-22: treasury £2,468,217.02, C5->1.00, C7->1.00, VaR (current £1,005.08 / stressed £401.28) ratio 2.50
  - 2017-11-21: treasury £2,468,226.78, C5->1.00, C7->1.00, VaR (current £1,005.08 / stressed £401.28) ratio 2.50
  - 2017-12-21: treasury £2,468,236.21, C5->1.00, C7->1.00, VaR (current £1,005.08 / stressed £401.28) ratio 2.50
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.69
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-20.43

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £4,141.69
  - By billing account: C1 £1,925.07, C2 £3,735.37, C3 £3,578.06, C4 £3,313.17, C5 £4,557.02, C6 £8,375.76, C7 £3,198.78, C8 £4,612.76, C9 £3,979.18
- Bill shock events (>=20%): 50 -- C1g 2017-01-31 (31%); C1g 2017-02-28 (28%); C1g 2017-05-31 (30%); C1g 2017-06-30 (30%); C1g 2017-09-30 (21%); C1g 2017-11-30 (70%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-05-31 (34%); C2g 2017-06-30 (29%); C2g 2017-09-30 (27%); C2g 2017-11-30 (66%); C2g 2017-12-31 (22%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-05-31 (30%); C3g 2017-06-30 (23%); C3g 2017-09-30 (21%); C3g 2017-11-30 (59%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (28%); C4 2017-09-30 (21%); C4 2017-10-31 (26%); C4 2017-11-30 (26%); C4g 2017-01-31 (23%); C4g 2017-02-28 (22%); C4g 2017-05-31 (33%); C4g 2017-06-30 (35%); C4g 2017-09-30 (36%); C4g 2017-10-31 (22%); C4g 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): 9 at risk (≥20% churn prob): C1 32%, C2 29%, C3 23%, C4 29%, C5 32%, C6 35%, C7 38%, C8 35%, C9 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.78-£131.86/MWh, net margin £120.11
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £106.38
- C2 (electricity): tariff £107.62-£125.74/MWh, net margin £96.75
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £181.68
- C3 (electricity): tariff £98.21-£120.28/MWh, net margin £69.46
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £57.45
- C4 (electricity): tariff £98.43-£110.07/MWh, net margin £46.40
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £117.83
- C5 (electricity): tariff £119.57-£131.01/MWh, net margin £164.75
- C6 (electricity): tariff £107.62-£126.23/MWh, net margin £58.63
- C7 (electricity): tariff £96.38-£195.85/MWh, net margin £159.34
- C8 (electricity): tariff £84.56-£190.15/MWh, net margin £210.03
- C9 (electricity): tariff £77.16-£180.75/MWh, net margin £133.15
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £29,456.72

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.818, average bill shock 16.5%, bad debt provision £1,360.92, avg complaint probability 4.7%
- Solvency signal: £249,813/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,490.15 vs. naked (unhedged) net margin: £112,878.90
- hedging cost £82,388.75 vs. a fully unhedged book (commodity-only: actual net £30,490.15 vs. naked net £112,878.90)
  - C1: actual £15.31 vs. naked £330.30 -- hedging cost £314.99
  - C1g: actual £131.41 vs. naked £272.27 -- hedging cost £140.86
  - C2: actual £104.20 vs. naked £438.06 -- hedging cost £333.86
  - C2g: actual £207.48 vs. naked £448.25 -- hedging cost £240.78
  - C3: actual £110.78 vs. naked £513.19 -- hedging cost £402.41
  - C3g: actual £30.62 vs. naked £394.35 -- hedging cost £363.73
  - C4: actual £41.36 vs. naked £275.27 -- hedging cost £233.90
  - C4g: actual £44.94 vs. naked £544.66 -- hedging cost £499.72
  - C5: actual £-203.29 vs. naked £1,068.66 -- hedging cost £1,271.96
  - C6: actual £103.83 vs. naked £1,674.99 -- hedging cost £1,571.17
  - C7: actual £-49.33 vs. naked £820.06 -- hedging cost £869.39
  - C8: actual £254.22 vs. naked £989.89 -- hedging cost £735.67
  - C9: actual £241.90 vs. naked £951.62 -- hedging cost £709.73
  - C_IC1: actual £29,456.72 vs. naked £104,157.32 -- hedging cost £74,700.60

**Year narrative:** 2017 produced a net gain of £30,978.68 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 50 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £99,895.13 (gross £263,686.43, capital £1,532.06)
  - Electricity: gross £262,323.62, capital £1,510.99, net £99,520.47
  - Gas: gross £1,362.80, capital £21.07, net £374.66
- Treasury at year end: £2,486,792.26
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.92 (avg 0.92), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2018-03-01 period 27, net margin £-15.09

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £101,078.22
  - By billing account: C1 £2,044.67, C2 £3,366.35, C3 £3,280.84, C4 £2,553.10, C5 £4,135.17, C6 £7,012.94, C7 £3,117.98, C8 £3,913.08, C9 £3,746.99, C_IC1 £977,611.09
- Bill shock events (>=20%): 60 -- C1g 2018-04-30 (37%); C1g 2018-05-31 (29%); C1g 2018-06-30 (30%); C1g 2018-09-30 (25%); C1g 2018-10-31 (46%); C1g 2018-11-30 (27%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (28%); C2g 2018-05-31 (34%); C2g 2018-06-30 (34%); C2g 2018-09-30 (33%); C2g 2018-10-31 (45%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (28%); C3g 2018-05-31 (32%); C3g 2018-06-30 (29%); C3g 2018-08-31 (34%); C3g 2018-09-30 (34%); C3g 2018-10-31 (35%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (28%); C4 2018-09-30 (23%); C4 2018-10-31 (41%); C4 2018-11-30 (28%); C4g 2018-04-30 (36%); C4g 2018-05-31 (33%); C4g 2018-06-30 (36%); C4g 2018-09-30 (39%); C4g 2018-10-31 (85%); C4g 2018-11-30 (24%); C_IC1 2018-01-31 (21%); C_IC1 2018-02-28 (59%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 9 at risk (≥20% churn prob): C1 38%, C2 32%, C3 32%, C4 38%, C5 35%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £117.78-£149.67/MWh, net margin £15.61
- C1g (gas): tariff £33.49-£36.05/MWh, net margin £131.41
- C2 (electricity): tariff £125.74-£143.63/MWh, net margin £76.05
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £174.16
- C3 (electricity): tariff £120.28-£126.95/MWh, net margin £69.63
- C3g (gas): tariff £23.11-£28.80/MWh, net margin £26.42
- C4 (electricity): tariff £110.07-£149.38/MWh, net margin £62.33
- C4g (gas): tariff £26.10-£33.61/MWh, net margin £42.67
- C5 (electricity): tariff £119.57-£153.31/MWh, net margin £-202.30 -- **net-negative**
- C6 (electricity): tariff £126.23-£141.94/MWh, net margin £-50.25 -- **net-negative**
- C7 (electricity): tariff £96.38-£221.29/MWh, net margin £-46.99 -- **net-negative**
- C8 (electricity): tariff £99.60-£200.74/MWh, net margin £125.78
- C9 (electricity): tariff £94.68-£198.44/MWh, net margin £203.49
- C_IC1 (electricity): tariff £-82.12-£228.05/MWh, net margin £105,886.61
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,619.48 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.810, average bill shock 15.9%, bad debt provision £2,388.41, avg complaint probability 4.7%
- Solvency signal: £226,072/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £109,966.87 vs. naked (unhedged) net margin: £247,156.56
- hedging cost £137,189.69 vs. a fully unhedged book (commodity-only: actual net £109,966.87 vs. naked net £247,156.56)
  - C1: actual £93.93 vs. naked £560.87 -- hedging cost £466.94
  - C1g: actual £144.33 vs. naked £420.62 -- hedging cost £276.29
  - C2: actual £61.24 vs. naked £497.85 -- hedging cost £436.61
  - C2g: actual £158.01 vs. naked £399.99 -- hedging cost £241.98
  - C3: actual £27.05 vs. naked £558.30 -- hedging cost £531.25
  - C3g: actual £38.90 vs. naked £481.52 -- hedging cost £442.62
  - C4: actual £104.28 vs. naked £464.72 -- hedging cost £360.45
  - C4g: actual £68.19 vs. naked £870.63 -- hedging cost £802.44
  - C5: actual £120.32 vs. naked £1,980.45 -- hedging cost £1,860.13
  - C6: actual £-146.85 vs. naked £1,828.24 -- hedging cost £1,975.09
  - C7: actual £71.93 vs. naked £1,347.94 -- hedging cost £1,276.01
  - C8: actual £24.82 vs. naked £937.14 -- hedging cost £912.32
  - C9: actual £144.25 vs. naked £1,046.58 -- hedging cost £902.33
  - C_IC1: actual £115,675.95 vs. naked £202,172.07 -- hedging cost £86,496.13
  - C_IC2: actual £-6,619.48 vs. naked £33,589.64 -- hedging cost £40,209.12

**Year narrative:** 2018 produced a net gain of £99,895.13 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 60 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £218,813.25 (gross £703,385.66, capital £11,607.11)
  - Electricity: gross £627,327.70, capital £2,293.65, net £218,347.04
  - Gas: gross £76,057.95, capital £9,313.46, net £466.22
- Treasury at year end: £2,607,297.74
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2019-02-04 period 35, net margin £-14.60

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £131,295.43
  - By billing account: C1 £2,031.88, C2 £2,976.43, C3 £3,306.15, C4 £2,818.73, C5 £4,447.02, C6 £7,484.38, C7 £3,271.22, C8 £3,889.36, C9 £3,802.39, C_IC1 £877,158.92, C_IC2 £533,063.30
- Bill shock events (>=20%): 66 -- C1 2019-04-30 (21%); C1g 2019-01-31 (36%); C1g 2019-02-28 (26%); C1g 2019-05-31 (23%); C1g 2019-06-30 (35%); C1g 2019-10-31 (74%); C1g 2019-11-30 (43%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-01-31 (25%); C2g 2019-02-28 (26%); C2g 2019-04-30 (35%); C2g 2019-06-30 (32%); C2g 2019-07-31 (25%); C2g 2019-09-30 (30%); C2g 2019-10-31 (64%); C2g 2019-11-30 (28%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-02-28 (26%); C3g 2019-06-30 (33%); C3g 2019-07-31 (35%); C3g 2019-09-30 (35%); C3g 2019-10-31 (64%); C3g 2019-11-30 (31%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (31%); C4 2019-09-30 (25%); C4 2019-11-30 (26%); C4g 2019-01-31 (30%); C4g 2019-02-28 (25%); C4g 2019-05-31 (21%); C4g 2019-06-30 (33%); C4g 2019-07-31 (37%); C4g 2019-09-30 (31%); C4g 2019-10-31 (34%); C4g 2019-11-30 (35%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (126%); C_IC2 2019-02-28 (67%)
- Churn risk (accounts renewing in 2019): 10 at risk (≥20% churn prob): C1 35%, C2 29%, C3 32%, C4 38%, C5 38%, C6 29%, C7 35%, C8 38%, C9 32%, C_IC1 23%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£149.67/MWh, net margin £93.83
- C1g (gas): tariff £25.52-£36.05/MWh, net margin £144.52
- C2 (electricity): tariff £143.63-£151.78/MWh, net margin £126.62
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £121.37
- C3 (electricity): tariff £120.68-£126.95/MWh, net margin £25.87
- C3g (gas): tariff £23.21-£28.80/MWh, net margin £85.43
- C4 (electricity): tariff £126.77-£149.38/MWh, net margin £101.76
- C4g (gas): tariff £19.63-£33.61/MWh, net margin £80.27
- C5 (electricity): tariff £126.10-£153.31/MWh, net margin £119.52
- C6 (electricity): tariff £141.94-£148.61/MWh, net margin £89.30
- C7 (electricity): tariff £99.69-£221.29/MWh, net margin £71.74
- C8 (electricity): tariff £105.15-£211.40/MWh, net margin £155.04
- C9 (electricity): tariff £98.82-£198.44/MWh, net margin £145.74
- C_IC1 (electricity): tariff £0.00-£263.25/MWh, net margin £137,419.17
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £78,495.67
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £1,502.76
- C_IC3g (gas): tariff £27.53/MWh, net margin £34.62

**Portfolio Health**

- Capital cost ratio: 1.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.824, average bill shock 17.0%, bad debt provision £6,221.26, avg complaint probability 4.7%
- Solvency signal: £217,275/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £243,418.66 vs. naked (unhedged) net margin: £825,875.24
- hedging cost £582,456.58 vs. a fully unhedged book (commodity-only: actual net £243,418.66 vs. naked net £825,875.24)
  - C1: actual £75.36 vs. naked £487.41 -- hedging cost £412.06
  - C1g: actual £139.49 vs. naked £304.83 -- hedging cost £165.34
  - C2: actual £156.65 vs. naked £662.49 -- hedging cost £505.84
  - C2g: actual £93.46 vs. naked £403.54 -- hedging cost £310.08
  - C3: actual £35.26 vs. naked £668.43 -- hedging cost £633.17
  - C3g: actual £140.55 vs. naked £510.60 -- hedging cost £370.05
  - C4: actual £104.18 vs. naked £443.73 -- hedging cost £339.54
  - C4g: actual £106.85 vs. naked £579.54 -- hedging cost £472.69
  - C5: actual £-27.66 vs. naked £1,590.03 -- hedging cost £1,617.69
  - C6: actual £231.02 vs. naked £2,597.25 -- hedging cost £2,366.23
  - C7: actual £56.95 vs. naked £1,146.63 -- hedging cost £1,089.68
  - C8: actual £240.89 vs. naked £1,370.83 -- hedging cost £1,129.94
  - C9: actual £159.55 vs. naked £1,258.61 -- hedging cost £1,099.06
  - C_IC1: actual £154,554.23 vs. naked £295,481.65 -- hedging cost £140,927.42
  - C_IC2: actual £85,814.50 vs. naked £161,906.11 -- hedging cost £76,091.62
  - C_IC3: actual £1,502.76 vs. naked £290,362.92 -- hedging cost £288,860.16
  - C_IC3g: actual £34.62 vs. naked £66,100.62 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £218,813.25 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £117,271.50 (gross £793,594.97, capital £7,399.12)
  - Electricity: gross £716,404.32, capital £1,958.74, net £112,839.89
  - Gas: gross £77,190.65, capital £5,440.38, net £4,431.62
- Treasury at year end: £2,901,196.48
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.86 (avg 0.86), C7 0.89 (avg 0.89), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2020-12-31 period 1, net margin £-489.15

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2020): £210,047.67
  - By billing account: C1 £2,354.48, C2 £3,147.13, C3 £2,903.62, C4 £2,915.29, C5 £4,922.61, C6 £7,822.03, C7 £3,947.19, C8 £4,123.78, C9 £3,750.33, C_IC1 £650,913.62, C_IC2 £322,130.01, C_IC3 £1,042,436.48, C_IC4 £679,253.11
- Bill shock events (>=20%): 53 -- C1g 2020-01-31 (20%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-31 (35%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (22%); C4 2020-11-30 (24%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (48%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (117%)
- Churn risk (accounts renewing in 2020): 10 at risk (≥20% churn prob): C1 29%, C2 32%, C3 32%, C4 32%, C5 35%, C6 32%, C7 35%, C8 38%, C9 41%, C_IC2 20%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£132.43/MWh, net margin £75.00
- C1g (gas): tariff £25.00-£25.52/MWh, net margin £139.56
- C2 (electricity): tariff £143.89-£151.78/MWh, net margin £182.74
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £133.50
- C3 (electricity): tariff £120.68/MWh, net margin £16.44
- C3g (gas): tariff £23.21/MWh, net margin £77.69
- C4 (electricity): tariff £122.46-£126.77/MWh, net margin £87.28
- C4g (gas): tariff £16.09-£19.63/MWh, net margin £75.56
- C5 (electricity): tariff £126.10-£135.83/MWh, net margin £-30.69 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.61/MWh, net margin £365.30
- C7 (electricity): tariff £99.69-£211.41/MWh, net margin £58.16
- C8 (electricity): tariff £110.24-£211.40/MWh, net margin £338.58
- C9 (electricity): tariff £85.32-£188.66/MWh, net margin £117.34
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £52,214.76
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £43,740.58
- C_IC3 (electricity): tariff £37.49-£80.66/MWh, net margin £11,095.11
- C_IC3g (gas): tariff £15.44-£20.18/MWh, net margin £4,005.30
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £4,579.29

**Portfolio Health**

- Capital cost ratio: 0.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.830, average bill shock 14.5%, bad debt provision £6,309.15, avg complaint probability 4.3%
- Solvency signal: £223,169/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £74,561.09 vs. naked (unhedged) net margin: £934,122.76
- hedging cost £859,561.67 vs. a fully unhedged book (commodity-only: actual net £74,561.09 vs. naked net £934,122.76)
  - C1: actual £-18.86 vs. naked £97.57 -- hedging cost £116.44
  - C1g: actual £22.28 vs. naked £-68.18 -- hedging added £90.47
  - C2: actual £175.35 vs. naked £570.69 -- hedging cost £395.33
  - C2g: actual £144.84 vs. naked £324.27 -- hedging cost £179.43
  - C4: actual £25.00 vs. naked £235.45 -- hedging cost £210.45
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C5: actual £-339.47 vs. naked £173.51 -- hedging cost £512.98
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-122.66 vs. naked £315.77 -- hedging cost £438.43
  - C8: actual £341.68 vs. naked £1,170.25 -- hedging cost £828.57
  - C9: actual £-18.75 vs. naked £697.60 -- hedging cost £716.35
  - C_IC1: actual £33,397.82 vs. naked £127,374.87 -- hedging cost £93,977.05
  - C_IC2: actual £42,655.30 vs. naked £95,579.77 -- hedging cost £52,924.46
  - C_IC3: actual £-16,210.87 vs. naked £217,080.14 -- hedging cost £233,291.01
  - C_IC3g: actual £6,308.59 vs. naked £147,619.15 -- hedging cost £141,310.56
  - C_IC4: actual £7,920.21 vs. naked £340,659.18 -- hedging cost £332,738.97

**Year narrative:** 2020 produced a net gain of £117,271.50 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £58,825.01 (gross £773,238.12, capital £15,960.91)
  - Electricity: gross £690,446.24, capital £5,635.77, net £60,827.28
  - Gas: gross £82,791.88, capital £10,325.14, net £-2,002.27
- Treasury at year end: £2,923,133.67
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2021-12-31 period 1, net margin £-4,092.43

**Customer Book**

- Active accounts: 16 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £204,640.60
  - By billing account: C1 £2,149.90, C2 £3,535.21, C3 £2,898.44, C4 £2,579.50, C5 £4,780.06, C6 £8,976.90, C7 £3,182.04, C8 £4,275.15, C9 £3,525.30, C_IC1 £583,927.76, C_IC2 £357,340.56, C_IC3 £1,047,971.26, C_IC4 £635,185.70
- Bill shock events (>=20%): 51 -- C1g 2021-05-31 (28%); C1g 2021-06-30 (45%); C1g 2021-10-31 (55%); C1g 2021-11-30 (53%); C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (21%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (23%); C4 2021-10-31 (48%); C4 2021-11-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (24%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (22%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%)
- Churn risk (accounts renewing in 2021): 12 at risk (≥20% churn prob): C1 32%, C2 32%, C4 35%, C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC3 20%, C_IC4 29%

**Pricing & Margin**

- C1 (electricity): tariff £132.43/MWh, net margin £-18.58 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £21.95
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £157.33
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £99.84
- C4 (electricity): tariff £122.46-£183.00/MWh, net margin £-59.20 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-334.91 -- **net-negative**
- C5 (electricity): tariff £135.83/MWh, net margin £-335.69 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.10/MWh, net margin £525.74
- C7 (electricity): tariff £110.74-£274.50/MWh, net margin £-132.26 -- **net-negative**
- C8 (electricity): tariff £110.24-£274.50/MWh, net margin £341.35
- C9 (electricity): tariff £85.32-£264.30/MWh, net margin £-13.96 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £27,733.69
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £56,686.15
- C_IC3 (electricity): tariff £42.25-£390.84/MWh, net margin £-27,406.34 -- **net-negative**
- C_IC3g (gas): tariff £20.18-£124.11/MWh, net margin £-1,789.15 -- **net-negative**
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £3,349.06

**Portfolio Health**

- Capital cost ratio: 2.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.829, average bill shock 15.9%, bad debt provision £9,214.96, avg complaint probability 4.5%
- Solvency signal: £243,594/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £144,721.30 vs. naked (unhedged) net margin: £347,679.49
- hedging cost £202,958.18 vs. a fully unhedged book (commodity-only: actual net £144,721.30 vs. naked net £347,679.49)
  - C2: actual £136.64 vs. naked £124.72 -- hedging added £11.92
  - C2g: actual £45.59 vs. naked £-190.70 -- hedging added £236.29
  - C4: actual £-220.41 vs. naked £-170.34 -- hedging cost £50.07
  - C4g: actual £-901.21 vs. naked £-1,344.38 -- hedging added £443.17
  - C6: actual £512.47 vs. naked £267.77 -- hedging added £244.70
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-49.52 vs. naked £-185.20 -- hedging added £135.68
  - C_IC1: actual £28,828.53 vs. naked £-64,739.88 -- hedging added £93,568.41
  - C_IC2: actual £65,431.61 vs. naked £21,136.25 -- hedging added £44,295.36
  - C_IC3: actual £103,737.05 vs. naked £237,601.34 -- hedging cost £133,864.29
  - C_IC3g: actual £-49,329.98 vs. naked £31,726.54 -- hedging cost £81,056.52
  - C_IC4: actual £-1,924.70 vs. naked £124,214.85 -- hedging cost £126,139.55

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £58,825.01 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 51 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £257,281.79 (gross £1,063,503.87, capital £65,698.55)
  - Electricity: gross £973,147.95, capital £13,293.54, net £306,819.99
  - Gas: gross £90,355.92, capital £52,405.01, net £-49,538.20
- Treasury at year end: £3,071,857.50
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,022,183.65, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,612.27 / stressed £20,605.22) ratio 2.70
  - 2022-05-29: treasury £3,022,302.80, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,721.97 / stressed £20,634.38) ratio 2.70
  - 2022-06-28: treasury £3,022,297.51, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,721.97 / stressed £20,634.38) ratio 2.70
  - 2022-07-28: treasury £3,022,104.88, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,783.39 / stressed £20,646.62) ratio 2.70
  - 2022-08-27: treasury £3,022,095.28, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,783.39 / stressed £20,646.62) ratio 2.70
  - 2022-09-26: treasury £3,022,079.83, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,783.39 / stressed £20,646.62) ratio 2.70
  - 2022-10-26: treasury £3,019,793.89, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,845.49 / stressed £20,657.09) ratio 2.70
  - 2022-11-25: treasury £3,019,643.48, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,845.49 / stressed £20,657.09) ratio 2.70
  - 2022-12-25: treasury £3,019,377.29, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,845.49 / stressed £20,657.09) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC3g on 2022-12-31 period 1, net margin £-2,998.80

**Customer Book**

- Active accounts: 14 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £203,686.37
  - By billing account: C1 £2,387.33, C2 £2,709.58, C2_2 £479.63, C3 £2,892.22, C4 £1,671.17, C5 £4,936.72, C6 £8,297.07, C7 £2,807.06, C8 £4,074.08, C9 £3,924.03, C_IC1 £653,261.87, C_IC2 £380,850.79, C_IC3 £1,178,445.19, C_IC4 £604,872.42
- Bill shock events (>=20%): 61 -- C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-06-30 (77%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (109%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (35%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (69%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 9 at risk (≥20% churn prob): C2 26%, C4 38%, C6 32%, C7 35%, C8 35%, C9 38%, C_IC1 20%, C_IC3 23%, C_IC4 32%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £13.07
- C2_2 (electricity): tariff £361.95/MWh, net margin £28.76
- C2g (gas): tariff £35.00/MWh, net margin £-17.33 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-276.94 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,284.53 -- **net-negative**
- C6 (electricity): tariff £197.10-£406.81/MWh, net margin £820.78
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,826.12 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-189.35 -- **net-negative**
- C9 (electricity): tariff £138.44-£389.58/MWh, net margin £-117.27 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£461.16/MWh, net margin £133,273.98
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £74,331.76
- C_IC3 (electricity): tariff £137.31-£390.84/MWh, net margin £102,690.79
- C_IC3g (gas): tariff £120.39-£124.11/MWh, net margin £-48,236.35 -- **net-negative**
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £-1,929.46 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 6.2% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,377,518.07 -> £3,019,346.37 (10.6%)
- Bills issued: 148, average clarity 0.791, average bill shock 33.8%, bad debt provision £35,881.34, avg complaint probability 5.6%
- Solvency signal: £279,260/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £105,416.83 vs. naked (unhedged) net margin: £1,091,126.52
- hedging cost £985,709.70 vs. a fully unhedged book (commodity-only: actual net £105,416.83 vs. naked net £1,091,126.52)
  - C2_2: actual £30.18 vs. naked £1,645.15 -- hedging cost £1,614.97
  - C4: actual £-277.33 vs. naked £595.36 -- hedging cost £872.70
  - C4g: actual £-1,950.48 vs. naked £1,336.80 -- hedging cost £3,287.28
  - C6: actual £1,126.71 vs. naked £3,994.73 -- hedging cost £2,868.02
  - C7: actual £-345.82 vs. naked £2,281.71 -- hedging cost £2,627.53
  - C8: actual £-348.38 vs. naked £1,102.92 -- hedging cost £1,451.29
  - C9: actual £-49.13 vs. naked £1,012.47 -- hedging cost £1,061.60
  - C_IC1: actual £216,002.93 vs. naked £253,669.05 -- hedging cost £37,666.11
  - C_IC2: actual £88,877.93 vs. naked £128,323.38 -- hedging cost £39,445.45
  - C_IC3: actual £-170,519.48 vs. naked £446,535.18 -- hedging cost £617,054.66
  - C_IC3g: actual £-30,637.15 vs. naked £84,150.32 -- hedging cost £114,787.47
  - C_IC4: actual £3,506.84 vs. naked £166,479.45 -- hedging cost £162,972.61

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £257,281.79 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 61 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £52,224.79 (gross £921,515.81, capital £49,542.11)
  - Electricity: gross £800,575.70, capital £9,816.26, net £84,536.28
  - Gas: gross £120,940.11, capital £39,725.85, net £-32,311.49
- Treasury at year end: £3,177,752.43
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,071,857.16, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,122.64 / stressed £44,252.29) ratio 2.76
  - 2023-02-23: treasury £3,071,857.51, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,122.64 / stressed £44,252.29) ratio 2.76
  - 2023-03-25: treasury £3,071,857.81, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,122.64 / stressed £44,252.29) ratio 2.76
  - 2023-04-24: treasury £3,153,599.85, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £129,341.20 / stressed £49,307.19) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-12-31 period 1, net margin £-3,508.81

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £204,659.00
  - By billing account: C1 £2,363.74, C2 £2,754.30, C2_2 £1,362.38, C3 £2,939.89, C4 £1,284.79, C5 £4,887.44, C6 £9,034.18, C7 £3,049.76, C8 £4,076.05, C9 £4,133.22, C_IC1 £706,196.69, C_IC2 £397,846.07, C_IC3 £1,091,525.35, C_IC4 £633,772.08
- Bill shock events (>=20%): 42 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (31%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (25%); C4 2023-04-30 (29%); C4 2023-09-30 (24%); C4 2023-11-30 (27%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (46%); C4g 2023-11-30 (63%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (59%); C_IC2 2023-05-31 (52%); C_IC2 2023-06-30 (100%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (36%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%)
- Churn risk (accounts renewing in 2023): 8 at risk (≥20% churn prob): C2_2 38%, C4 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC3 23%, C_IC4 29%

**Pricing & Margin**

- C2_2 (electricity): tariff £350.73-£361.95/MWh, net margin £508.29
- C4 (electricity): tariff £249.30-£305.00/MWh, net margin £-68.71 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,164.32 -- **net-negative**
- C6 (electricity): tariff £333.40-£406.81/MWh, net margin £1,268.84
- C7 (electricity): tariff £187.43-£457.50/MWh, net margin £-344.44 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-21.10 -- **net-negative**
- C9 (electricity): tariff £192.58-£389.58/MWh, net margin £226.17
- C_IC1 (electricity): tariff £-60.00-£461.16/MWh, net margin £162,709.48
- C_IC2 (electricity): tariff £-186.24-£475.07/MWh, net margin £86,174.91
- C_IC3 (electricity): tariff £100.50-£262.14/MWh, net margin £-169,431.34 -- **net-negative**
- C_IC3g (gas): tariff £61.13-£120.39/MWh, net margin £-31,147.16 -- **net-negative**
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £3,514.18

**Portfolio Health**

- Capital cost ratio: 5.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,569,908.19 -> £3,177,749.07 (11.0%)
- Bills issued: 144, average clarity 0.808, average bill shock 17.2%, bad debt provision £13,840.67, avg complaint probability 4.8%
- Solvency signal: £317,775/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £362,616.46 vs. naked (unhedged) net margin: £1,158,632.46
- hedging cost £796,016.01 vs. a fully unhedged book (commodity-only: actual net £362,616.46 vs. naked net £1,158,632.46)
  - C2_2: actual £835.65 vs. naked £2,428.03 -- hedging cost £1,592.38
  - C4: actual £313.89 vs. naked £700.07 -- hedging cost £386.18
  - C4g: actual £529.39 vs. naked £1,048.79 -- hedging cost £519.40
  - C6: actual £1,414.61 vs. naked £5,082.92 -- hedging cost £3,668.31
  - C7: actual £474.16 vs. naked £1,920.00 -- hedging cost £1,445.85
  - C8: actual £212.54 vs. naked £1,972.23 -- hedging cost £1,759.69
  - C9: actual £626.08 vs. naked £2,129.72 -- hedging cost £1,503.64
  - C_IC1: actual £143,158.20 vs. naked £286,630.04 -- hedging cost £143,471.85
  - C_IC2: actual £95,214.41 vs. naked £163,560.49 -- hedging cost £68,346.08
  - C_IC3: actual £153,392.53 vs. naked £428,482.00 -- hedging cost £275,089.47
  - C_IC3g: actual £-37,283.07 vs. naked £77,163.92 -- hedging cost £114,446.99
  - C_IC4: actual £3,728.07 vs. naked £187,514.24 -- hedging cost £183,786.17

**Year narrative:** 2023 produced a net gain of £52,224.79 across 12 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 42 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £319,104.16 (gross £1,295,042.41, capital £56,078.86)
  - Electricity: gross £1,170,628.53, capital £9,727.57, net £356,350.21
  - Gas: gross £124,413.88, capital £46,351.29, net £-37,246.05
- Treasury at year end: £3,539,952.69
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.91 (avg 0.91), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2024-12-30 period 1, net margin £-1,934.36

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2024): £236,492.21
  - By billing account: C1 £2,185.27, C2 £2,826.48, C2_2 £1,961.04, C3 £3,148.22, C4 £1,626.06, C5 £4,679.73, C6 £9,107.37, C7 £3,081.06, C8 £4,230.43, C9 £4,697.20, C_IC1 £726,697.20, C_IC2 £425,328.81, C_IC3 £1,357,073.29, C_IC4 £764,248.77
- Bill shock events (>=20%): 33 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (30%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (58%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (54%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C4 32%, C6 38%, C7 35%, C8 41%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.09-£350.73/MWh, net margin £419.45
- C4 (electricity): tariff £249.30/MWh, net margin £235.13
- C4g (gas): tariff £66.00/MWh, net margin £396.91
- C6 (electricity): tariff £333.40/MWh, net margin £493.11
- C7 (electricity): tariff £165.00-£357.81/MWh, net margin £473.75
- C8 (electricity): tariff £161.68-£397.50/MWh, net margin £333.99
- C9 (electricity): tariff £165.00-£367.65/MWh, net margin £560.40
- C_IC1 (electricity): tariff £-98.58-£329.91/MWh, net margin £126,252.85
- C_IC2 (electricity): tariff £-106.92-£354.14/MWh, net margin £70,371.98
- C_IC3 (electricity): tariff £86.86-£191.87/MWh, net margin £153,473.47
- C_IC3g (gas): tariff £61.13-£61.82/MWh, net margin £-37,642.96 -- **net-negative**
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £3,736.07

**Portfolio Health**

- Capital cost ratio: 4.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,569,819.82 -> £3,177,752.47 (11.0%)
- Bills issued: 129, average clarity 0.813, average bill shock 15.9%, bad debt provision £11,543.25, avg complaint probability 4.6%
- Solvency signal: £353,995/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £175,014.97 vs. naked (unhedged) net margin: £552,517.23
- hedging cost £377,502.26 vs. a fully unhedged book (commodity-only: actual net £175,014.97 vs. naked net £552,517.23)
  - C2_2: actual £94.16 vs. naked £1,032.13 -- hedging cost £937.97
  - C7: actual £-12.31 vs. naked £653.82 -- hedging cost £666.14
  - C8: actual £342.87 vs. naked £1,419.87 -- hedging cost £1,077.00
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £118,250.31 vs. naked £213,069.51 -- hedging cost £94,819.20
  - C_IC2: actual £62,304.27 vs. naked £113,472.08 -- hedging cost £51,167.81
  - C_IC3: actual £15,800.49 vs. naked £116,372.70 -- hedging cost £100,572.21
  - C_IC3g: actual £-23,593.14 vs. naked £29,503.44 -- hedging cost £53,096.57
  - C_IC4: actual £1,455.13 vs. naked £75,565.97 -- hedging cost £74,110.84

**Year narrative:** 2024 produced a net gain of £319,104.16 across 12 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £92,725.55 (gross £523,880.69, capital £29,153.03)
  - Electricity: gross £470,371.91, capital £5,641.09, net £112,449.98
  - Gas: gross £53,508.78, capital £23,511.94, net £-19,724.42
- Treasury at year end: £3,591,885.54
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2025-06-01 period 1, net margin £-537.64

**Customer Book**

- Active accounts: 9 (C2_2, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 4, SME electricity: 0, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £247,493.35
  - By billing account: C1 £2,182.92, C2 £2,873.24, C2_2 £2,072.10, C3 £2,946.11, C4 £1,671.27, C5 £4,762.46, C6 £8,825.69, C7 £3,543.96, C8 £4,133.91, C9 £4,527.83, C_IC1 £773,391.74, C_IC2 £449,632.77, C_IC3 £1,408,672.45, C_IC4 £795,670.40
- Bill shock events (>=20%): 20 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (34%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.09-£283.36/MWh, net margin £87.46
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-9.17 -- **net-negative**
- C8 (electricity): tariff £149.29-£308.66/MWh, net margin £87.35
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £195.49
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £64,377.43
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £30,496.97
- C_IC3 (electricity): tariff £86.86-£165.83/MWh, net margin £15,778.03
- C_IC3g (gas): tariff £61.82/MWh, net margin £-19,724.42 -- **net-negative**
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £1,436.41

**Portfolio Health**

- Capital cost ratio: 5.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 54, average clarity 0.777, average bill shock 23.6%, bad debt provision £4,995.39, avg complaint probability 5.9%
- Solvency signal: £448,986/customer (8 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £57.34 vs. naked (unhedged) net margin: £337.17
- hedging cost £279.83 vs. a fully unhedged book (commodity-only: actual net £57.34 vs. naked net £337.17)
  - C2_2: actual £83.97 vs. naked £218.28 -- hedging cost £134.31
  - C8: actual £-26.63 vs. naked £118.90 -- hedging cost £145.52

**Year narrative:** 2025 produced a net gain of £92,725.55 across 9 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 20 customer(s) experienced a bill shock of >=20%.
