# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,684,422.91
  (£1,217,786.69 net change)
- Solvency signal (final year): £445,785/customer (8 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £19,738,965.63
  VAT remitted to HMRC: (£950,027.19) | Revenue (ex-VAT): £18,788,938.44
  Non-commodity pass-through: (£4,781,366.43)
- Gross margin: £6,411,862.49
- Capital costs: £237,889.15
- Net margin: £6,173,973.33
- Capital cost ratio: 3.7% of gross
- Net margin as % of revenue: 32.9%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1531, average clarity 0.816,
  service quality score 0.905
- Enterprise value (CLV sum across 14 billing accounts): £5,967,084.36
- Cost to serve (whole portfolio): £90,612.16, net margin after cost to serve: £6,083,361.18
- Hedge effectiveness (whole window): hedging cost £4,040,363.84 vs. a fully unhedged book (commodity-only: actual net £1,217,786.69 vs. naked net £5,258,150.53)

- **2021** (crisis year): net margin £56,065.55, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £247,853.47, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2247, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | -0.7x (net £-135,418.44 on £187,143.92 capital) | **RED** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 4/6 departures (67%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 3.8%, max 15.1% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +33.1% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 32.9% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Gas segment ROC, Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,411,862.49, capital £237,889.15, net £6,173,973.33. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 3.7% (commodity basis, comparable to old model) / 3.7% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £56,065.55 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 32.9%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,173,973.33
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,258,150.53
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,040,363.84 vs. a fully unhedged book (commodity-only: actual net £1,217,786.69 vs. naked net £5,258,150.53)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,374.20 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £613,605.49 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £254.88 | £626.84 | £296.53 | £1,178.25 |
| 2017 | £29,047.38 | £0.00 | £223.58 | £835.39 | £463.34 | £30,569.69 |
| 2018 | £99,054.39 | £0.00 | £-248.88 | £506.23 | £374.66 | £99,686.40 |
| 2019 | £217,182.16 | £34.62 | £212.59 | £720.76 | £431.59 | £218,581.72 |
| 2020 | £111,150.80 | £4,005.30 | £335.49 | £862.26 | £426.32 | £116,780.16 |
| 2021 | £57,693.34 | £-1,789.15 | £183.66 | £261.22 | £-283.52 | £56,065.55 |
| 2022 | £299,264.79 | £-48,236.35 | £818.81 | £-2,361.57 | £-1,632.21 | £247,853.47 |
| 2023 | £77,619.89 | £-31,147.16 | £1,268.95 | £270.31 | £-1,467.63 | £46,544.35 |
| 2024 | £346,249.71 | £-37,642.96 | £492.86 | £2,053.12 | £472.61 | £311,625.34 |
| 2025 | £108,263.17 | £-19,724.42 | £0.00 | £363.01 | £0.00 | £88,901.76 |

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
| C2 | 2021-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.5838 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.2900 | 0.5500 | 0.8695 | 0.9547 |
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
| C4 | 2023-09-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.7019 |
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

- **Average absolute error:** 198.6%
- **Average signed error:** +52.7% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -82.1% | 82.1% |
| 2017 | 3 | -93.7% | 93.7% |
| 2018 | 4 | +402.7% | 497.3% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | +26.0% | 189.9% |
| 2021 | 9 | -6.7% | 120.4% |
| 2022 | 7 | -23.5% | 112.9% |
| 2023 | 7 | -4.5% | 131.5% |
| 2024 | 7 | +78.9% | 231.8% |
| 2025 | 2 | -94.5% | 94.5% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 34.8%, abs error 313.6%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.9%, abs error 148.5%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.2% | 0.0% | 82.1% |
| 2017 | 0 | 3 | 0.0% | 2.2% | 0.0% | 93.7% |
| 2018 | 2 | 2 | 19.1% | 49.9% | 51.5% | 943.1% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 16.6% | 0.5% | 281.4% | 98.4% |
| 2021 | 3 | 6 | 66.0% | 4.1% | 184.3% | 88.4% |
| 2022 | 0 | 7 | 0.0% | 19.5% | 0.0% | 112.9% |
| 2023 | 2 | 5 | 29.2% | 19.0% | 72.8% | 155.0% |
| 2024 | 3 | 4 | 39.9% | 0.0% | 407.5% | 100.0% |
| 2025 | 0 | 2 | 0.0% | 2.1% | 0.0% | 94.5% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 9 (23%)
- **Below/at SVT (protected):** 30 (77%)
- **Mean rate vs SVT premium:** -10.2%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.1 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 120.0 | 140.0 |
| 2018 | 2 | 1 (50%) | +0.2% | 152.8 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -25.9% | 130.9 | 176.9 |
| 2021 | 6 | 3 (50%) | +0.8% | 184.2 | 183.8 |
| 2022 | 7 | 4 (57%) | +11.5% | 294.6 | 318.4 |
| 2023 | 5 | 0 (0%) | -32.3% | 225.9 | 364.0 |
| 2024 | 4 | 0 (0%) | -16.2% | 205.7 | 246.9 |
| 2025 | 2 | 1 (50%) | -4.8% | 236.8 | 248.6 |

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
| 2020 | 10 | 1.90× | 10.79× |
| 2021 | 9 | 1.20× | 3.75× |
| 2022 | 7 | 1.13× | 3.13× |
| 2023 | 7 | 1.31× | 3.75× |
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
| 2018 | 10 | 0.64% | 3.21% | Low — stable portfolio |
| 2019 | 11 | 1.00% | 5.05% | MODERATE — asset adoption visible |
| 2020 | 13 | 0.81% | 3.50% | Low — stable portfolio |
| 2021 | 11 | 2.29% | 13.24% | MODERATE — asset adoption visible |
| 2022 | 9 | 3.76% | 15.13% | HIGH drift — EV/asset cohort growing |
| 2023 | 9 | 1.68% | 4.56% | MODERATE — asset adoption visible |
| 2024 | 9 | 1.57% | 4.41% | MODERATE — asset adoption visible |
| 2025 | 2 | 1.42% | 2.07% | MODERATE — asset adoption visible |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **3.76%** mean / **15.13%** max in 2022. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
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
| 2021 | 11 | 2.3% | 13.2% |
| 2022 | 9 | 3.8% | 15.1% |
| 2023 | 9 | 1.7% | 4.6% |
| 2024 | 9 | 1.6% | 4.4% |
| 2025 | 2 | 1.4% | 2.1% |

**86** of **86** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## EAC Drift Snapshot (Phase AI)

Per-customer consumption drift from company billing history (first renewal → latest renewal).
Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.

**1 significant** (≥15%) | **1 moderate** (5–15%) | **11 stable** (<5%)

| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |
|----------|-------------|-------------|-------|--------------|
| C2 | 5,265 | 4,212 | -20% | likely solar installation or significant efficiency upgrade |
| C7 | 13,179 | 12,155 | -8% | efficiency improvement or reduced occupancy |

**Portfolio demand trend:** 3 customers increasing / 10 decreasing (mean drift: -2.6%)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **7** (6 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.32, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.32, company est=0.04 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.83 |
| 2022-03-31 | CHURN | C2 | SIM p=0.29, company est=0.07 |
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
| 2017 | 37,159 | 2,707 | 11,165 | 1,977 | 9,940 | 0 | 62,948 |  |
| 2018 | 65,510 | 9,875 | 17,434 | 9,350 | 17,284 | 0 | 119,453 |  |
| 2019 | 164,625 | 28,353 | 42,460 | 31,969 | 44,302 | 0 | 311,709 |  |
| 2020 | 238,623 | 35,389 | 69,454 | 56,547 | 70,020 | 0 | 470,032 |  |
| 2021 | 246,536 | 15,000 | 71,336 | 49,639 | 62,792 | 41,399 | 486,702 |  |
| 2022 | 255,965 | -49,690 | 70,920 | 36,643 | 69,045 | 99,381 | 482,264 | ⬇ CfD REBATE |
| 2023 | 271,644 | 64,715 | 71,702 | 50,924 | 75,040 | 13,739 | 547,764 |  |
| 2024 | 307,361 | 109,837 | 72,815 | 68,649 | 82,491 | 1,997 | 643,150 |  |
| 2025 | 135,564 | 46,893 | 31,156 | 30,992 | 36,108 | 853 | 281,565 |  |
| **Total** | **1,724,149** | **263,086** | **458,631** | **336,727** | **467,327** | **157,369** | **3,407,288** | |

Total policy cost: £3,407,288 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

## Network Charges — DUoS + TNUoS (Phase 29a)

Electricity network charges deducted from net_margin_gbp each year. 
Resi/SME: combined DUoS + TNUoS unit rate (largest single non-commodity cost). 
I&C HV: DUoS only (Triad TNUoS is an annual lump tracked in the Triad section).

| Year | Network cost £ | Note |
|------|----------------|------|
| 2016 | 3,202 |  |
| 2017 | 26,176 |  |
| 2018 | 38,555 |  |
| 2019 | 88,387 |  |
| 2020 | 124,559 |  |
| 2021 | 123,439 |  |
| 2022 | 132,891 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 138,888 | RIIO-ED2 from Apr 2023 |
| 2024 | 142,866 |  |
| 2025 | 61,009 |  |
| **Total** | **879,973** | |

Total network cost: £879,973 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

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
| 2021 | 22,472 | 50,462 | 72,934 |
| 2022 | 27,045 | 54,503 | 81,548 |
| 2023 | 32,229 | 79,799 | 112,028 |
| 2024 | 37,494 | 76,501 | 113,996 |
| 2025 | 17,243 | 31,816 | 49,059 |
| **Total** | **171,106** | **392,966** | **564,072** |

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
| 2021 | 297,922 | 215,176 | 82,747 | 22,472 | 50,462 | 10,327 | -2,073 | -0.7% |
| 2022 | 588,681 | 498,550 | 90,131 | 27,045 | 54,503 | 52,413 | -49,869 | -8.5% |
| 2023 | 297,765 | 176,988 | 120,777 | 32,229 | 79,799 | 39,738 | -32,615 | -11.0% |
| 2024 | 270,788 | 146,211 | 124,577 | 37,494 | 76,501 | 46,357 | -37,170 | -13.7% |
| 2025 | 132,454 | 78,945 | 53,509 | 17,243 | 31,816 | 23,512 | -19,724 | -14.9% |
| **Total** | **1,853,676** | **1,225,085** | **628,592** | **171,106** | **392,966** | **187,144** | **-135,418** | **-7.3%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,424 | 9 | 274,158 | 2108.91× | OK |
| 2017 | 2,497,718 | 10 | 249,772 | 1921.32× | OK |
| 2018 | 2,486,407 | 11 | 226,037 | 1738.75× | OK |
| 2019 | 2,606,387 | 12 | 217,199 | 1670.76× | OK |
| 2020 | 2,900,041 | 13 | 223,080 | 1716.00× | OK |
| 2021 | 2,921,176 | 12 | 243,431 | 1872.55× | OK |
| 2022 | 3,062,514 | 11 | 278,410 | 2141.62× | OK |
| 2023 | 3,160,736 | 10 | 316,074 | 2431.34× | OK |
| 2024 | 3,516,327 | 10 | 351,633 | 2704.87× | OK |
| 2025 | 3,566,280 | 8 | 445,785 | 3429.11× | OK |

End-state (2025): **£445,785/account** across 8 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,424 | 81947.0× | OK |
| 2017 | 466 | 559 | 2,497,718 | 4467.7× | OK |
| 2018 | 849 | 1,019 | 2,486,407 | 2439.9× | OK |
| 2019 | 1,543 | 1,851 | 2,606,387 | 1408.0× | OK |
| 2020 | 1,979 | 2,375 | 2,900,041 | 1221.2× | OK |
| 2021 | 4,339 | 5,207 | 2,921,176 | 561.0× | OK |
| 2022 | 8,500 | 10,200 | 3,062,514 | 300.3× | OK |
| 2023 | 5,606 | 6,727 | 3,160,736 | 469.8× | OK |
| 2024 | 2,654 | 3,185 | 3,516,327 | 1104.2× | OK |
| 2025 | 3,863 | 4,636 | 3,566,280 | 769.3× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,487.86 | £12,221.43 | £261.74/MWh | £144.48/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,975.64 | £9,695.00 | £272.50/MWh | £154.44/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,929.80 | £9,307.96 | £250.17/MWh | £141.68/MWh | +10.9% |

Total HH revenue: £63,617.69 vs flat equivalent £58,716.94 (+8.3% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 31 | 100% | C8 (2016-10-31) |
| 2017 | 50 | 81% | C8 (2017-11-30) |
| 2018 | 60 | 85% | C4g (2018-10-31) |
| 2019 | 66 | 130% | C_IC1 (2019-03-31) |
| 2020 | 53 | 118% | C_IC2 (2020-03-31) |
| 2021 | 51 | 153% | C4g (2021-10-31) |
| 2022 | 63 | 1735% | C2_2 (2022-04-30) |
| 2023 | 43 | 100% | C_IC2 (2023-06-30) |
| 2024 | 33 | 107% | C_IC2 (2024-07-31) |
| 2025 | 20 | 80% | C7 (2025-06-07) |

Total: **470** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1735% | no |
| 2021-10-31 | C4g | +153% | no |
| 2022-10-31 | C4g | +138% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2020-03-31 | C_IC2 | +118% | no |
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
| 2022 | 2 | 48% | 95% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 1 | 4% | 4% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £20.2 | £124.6 (+517%) | 95% |
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
| Total offer cost (foregone margin) | £418,229.71 |
| Margin saved (retained customers' terms) | £2,202,277.65 |
| Wasted offer cost (churned anyway) | £509.77 |
| **Net ROI of retention strategy** | **£1,784,047.94** |
| Acquisition cost avoided (retained customers) | £2,800.00 |
| **Full economic ROI (margin + acq savings)** | **£1,786,847.94** |

Missed opportunities (churns with no offer): **5** (£4,016.60 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 5 (£4,016.60 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24226.53 | £163687.72 | £139461.19 | £0.00 |
| 2019 | 2 | 2 | £42792.80 | £296612.44 | £253819.64 | £0.00 |
| 2020 | 3 | 3 | £26867.71 | £164431.12 | £137563.42 | £583.78 |
| 2021 | 4 | 3 | £120014.25 | £414008.32 | £293994.06 | £-178.13 |
| 2022 | 2 | 2 | £73217.72 | £324409.26 | £251191.54 | £189.30 |
| 2023 | 4 | 4 | £87121.16 | £436297.53 | £349176.37 | £0.00 |
| 2024 | 2 | 2 | £43989.54 | £402831.26 | £358841.72 | £3421.64 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24226.53 | £163687.72 | £150 | £139461.19 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £27950.99 | £194971.28 | £150 | £167020.29 | retained |
| 2020-01-01 | C_IC3 | 0.36 | 3% | £5716.80 | £10711.28 | £150 | £4994.49 | retained |
| 2020-03-31 | C_IC1 | 0.50 | 5% | £10372.10 | £130842.70 | £150 | £120470.60 | retained |
| 2020-12-31 | C_IC3 | 0.59 | 5% | £10778.81 | £22877.14 | £150 | £12098.33 | retained |
| 2021-03-31 | C_IC2 | 0.83 | 8% | £14127.74 | £90892.48 | £150 | £76764.73 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £22532.49 | £158356.24 | £150 | £135823.76 | retained |
| 2021-12-30 | C5 | 0.83 | 8% | £509.77 | £2239.91 | £400 | £-509.77 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £82844.26 | £164759.60 | £150 | £81915.34 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25015.80 | £95018.20 | £150 | £70002.40 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £48201.92 | £229391.06 | £150 | £181189.14 | retained |
| 2023-03-31 | C6 | 0.49 | 3% | £230.66 | £3261.59 | £400 | £3030.93 | retained |
| 2023-05-30 | C_IC2 | 0.57 | 5% | £11671.60 | £130033.94 | £150 | £118362.34 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £34630.07 | £242774.93 | £150 | £208144.86 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £40588.83 | £60227.07 | £150 | £19638.24 | retained |
| 2024-06-28 | C_IC2 | 0.54 | 5% | £10230.92 | £133340.97 | £150 | £123110.05 | retained |
| 2024-07-28 | C_IC1 | 0.95 | 8% | £33758.63 | £269490.30 | £150 | £235731.67 | retained |

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

**Full-history EV:** £5,967,084.36 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £427,524.12 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,178.25 |
| 2017 | £30,569.69 |
| 2018 | £99,686.40 |
| 2019 | £218,581.72 |
| 2020 | £116,780.16 |
| 2021 | £56,065.55 |
| 2022 | £247,853.47 |
| 2023 | £46,544.35 | ← trailing
| 2024 | £311,625.34 | ← trailing
| 2025 | £88,901.76 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £3,752.23 | — |
| C2 | £4,802.90 | — |
| C2_2 | — | £980.20 |
| C3 | £4,917.97 | — |
| C4 | £2,796.67 | £-1,201.86 |
| C5 | £8,437.09 | — |
| C6 | £15,057.00 | £2,524.56 |
| C7 | £6,636.17 | £114.76 |
| C8 | £7,234.11 | £382.10 |
| C9 | £7,544.43 | £939.97 |
| C_IC1 | £1,438,740.77 | £328,424.51 |
| C_IC2 | £774,349.92 | £173,850.60 |
| C_IC3 | £2,449,685.16 | £-86,703.16 |
| C_IC4 | £1,239,657.26 | £8,212.44 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £2,259.66 | — | — | — | — | £5,096.01 | — | £4,189.02 | — | — | — | — | — | — |
| 2017 | £1,925.07 | £3,735.54 | — | £3,578.17 | £3,313.16 | £4,557.02 | £8,376.41 | £3,198.78 | £4,613.04 | £3,979.09 | — | — | — | — |
| 2018 | £2,044.66 | £3,368.07 | — | £3,280.65 | £2,553.05 | £4,135.17 | £7,019.05 | £3,118.00 | £3,912.85 | £3,746.54 | £972,575.09 | — | — | — |
| 2019 | £2,031.94 | £2,978.41 | — | £3,305.80 | £2,818.64 | £4,447.19 | £7,492.87 | £3,271.26 | £3,888.99 | £3,801.64 | £874,214.78 | £530,697.39 | — | — |
| 2020 | £2,354.55 | £3,100.60 | — | £2,903.35 | £2,915.27 | £4,922.79 | £7,829.24 | £3,947.26 | £4,121.72 | £3,748.60 | £648,773.07 | £320,804.92 | £1,040,421.02 | £677,852.11 |
| 2021 | £2,149.30 | £3,409.73 | — | £2,888.84 | £2,546.44 | £4,778.70 | £8,975.29 | £3,176.63 | £4,269.49 | £3,520.10 | £580,052.44 | £353,610.90 | £1,044,043.93 | £630,832.11 |
| 2022 | £2,383.60 | £2,596.56 | £478.63 | £2,885.74 | £1,509.67 | £4,930.09 | £8,258.58 | £2,802.14 | £4,056.56 | £3,912.84 | £645,935.71 | £375,708.71 | £1,165,061.18 | £599,840.96 |
| 2023 | £2,367.09 | £2,644.37 | £1,364.88 | £2,943.77 | £1,092.91 | £4,889.60 | £9,023.49 | £3,049.89 | £4,080.67 | £4,137.70 | £699,406.81 | £391,898.12 | £1,087,180.28 | £629,044.89 |
| 2024 | £2,194.11 | £2,781.92 | £1,961.85 | £3,166.30 | £1,589.95 | £4,597.37 | £9,162.72 | £3,182.77 | £4,300.01 | £4,759.47 | £715,884.83 | £411,819.60 | £1,287,486.15 | £739,204.65 |
| 2025 | £2,176.03 | £2,750.71 | £2,071.00 | £2,941.70 | £1,598.61 | £4,752.29 | £8,812.27 | £3,535.97 | £4,122.94 | £4,524.62 | £760,326.93 | £440,601.91 | £1,393,587.02 | £787,041.97 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,769.06, range £58.35–£26,244.16.

- C1: cost to serve £414.45, net margin after CTS £2,320.62
- C1g: cost to serve £64.80, net margin after CTS £1,478.25
- C2: cost to serve £425.91, net margin after CTS £2,778.22
- C2_2: cost to serve £381.33, net margin after CTS £5,102.47
- C2g: cost to serve £83.87, net margin after CTS £1,935.34
- C3: cost to serve £292.46, net margin after CTS £2,093.02
- C3g: cost to serve £58.35, net margin after CTS £1,245.05
- C4: cost to serve £571.68, net margin after CTS £2,885.91
- C4g: cost to serve £242.41, net margin after CTS £836.54
- C5: cost to serve £871.77, net margin after CTS £8,505.43
- C6: cost to serve £1,349.12, net margin after CTS £21,099.39
- C7: cost to serve £953.32, net margin after CTS £9,778.96
- C8: cost to serve £938.84, net margin after CTS £11,512.07
- C9: cost to serve £896.47, net margin after CTS £11,805.82
- C_IC1: cost to serve £19,819.07, net margin after CTS £1,851,432.22
- C_IC2: cost to serve £11,332.46, net margin after CTS £896,097.22
- C_IC3: cost to serve £26,244.16, net margin after CTS £1,772,915.80
- C_IC3g: cost to serve £9,229.97, net margin after CTS £613,417.06
- C_IC4: cost to serve £16,441.72, net margin after CTS £1,090,243.56


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 29 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 13.9%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.30/MWh |
| C5 | electricity | 2018-12-31 | £-203.29 | £2,323.55 | +3.8% | £148.68/MWh | £153.32/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,283.71 | £6,187.80 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,215.97 | £10,069.00 | +20.0% | £128.22/MWh | £175.80/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,915.21 | £3,421.95 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £176.75/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.68/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £59.42/MWh |
| C5 | electricity | 2021-12-30 | £-339.03 | £2,699.76 | +7.6% | £311.83/MWh | £340.68/MWh |
| C7 | electricity | 2021-12-30 | £-122.44 | £1,986.50 | +1.2% | £311.83/MWh | £320.43/MWh |
| C_IC3 | electricity | 2021-12-31 | £-27,629.47 | £442,990.26 | +1.2% | £224.03/MWh | £260.82/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £316.71/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £307.53/MWh |
| C4 | electricity | 2022-09-30 | £-220.41 | £906.59 | +19.3% | £404.86/MWh | £485.10/MWh |
| C4g | gas | 2022-09-30 | £-1,139.49 | £1,265.65 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £319.35/MWh |
| C_IC3g | gas | 2022-12-31 | £-49,329.98 | £586,562.16 | +3.4% | £101.23/MWh | £120.39/MWh |
| C8 | electricity | 2023-03-31 | £-348.38 | £3,898.74 | +3.9% | £319.17/MWh | £335.51/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.10/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £219.97/MWh |
| C4 | electricity | 2023-09-30 | £-324.97 | £1,444.27 | +17.5% | £216.77/MWh | £252.74/MWh |
| C4g | gas | 2023-09-30 | £-2,441.94 | £3,362.64 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-345.82 | £3,990.91 | +3.7% | £242.22/MWh | £238.54/MWh |
| C_IC3 | electricity | 2023-12-31 | £-169,265.37 | £927,887.44 | +13.2% | £118.95/MWh | £127.96/MWh |
| C_IC3g | gas | 2023-12-31 | £-30,637.15 | £295,562.62 | +5.4% | £51.89/MWh | £61.27/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |
| C_IC3g | gas | 2024-12-30 | £-37,283.07 | £268,211.20 | +8.9% | £50.47/MWh | £61.96/MWh |


## Flexibility Revenue — DSR & Capacity Market (Phase AG)

Customers with EVs, ASHPs, and batteries earn ancillary revenue through two channels:
- **Capacity Market (CM):** ~£75/kW/yr; T-4 auctions; operational since 2014.
- **Demand Flexibility Service (DFS):** launched October 2022 by NESO; ~£4.5/MWh × 20 winter dispatch events/yr.

**Portfolio total (2016–2025):** £1,650.00 (CM: £750.00 | DFS: £900.00 | Peak year: £825.00 | Enrolled customer-years: 2)

| Year | CM Revenue | DFS Revenue | Total | Enrolled |
|------|------------|-------------|-------|----------|
| 2024 | £375.00 | £450.00 | £825.00 | 1 |
| 2025 | £375.00 | £450.00 | £825.00 | 1 |

DFS launched October 2022 (NESO Winter Demand Flexibility Service). Pre-2022 years show CM-only revenue. EV+battery customers earn ~£2,046/yr; EV-only ~£930/yr.

## Portfolio Intelligence Pack (Phase AH)

Board-level synthesis of CRM and flexibility intelligence derived from observable operational data.

### 1. Retention Intelligence

- **Retention offers made:** 18
- **Offer acceptance rate:** 94% (17 retained / 1 churned despite offer)
- **Estimated margin protected:** £2,202,277.65
- **No-offer churns:** 5 total (0 blind miss / 0 deliberate pass)
- **Retention coverage rate:** 78% of at-risk renewals received an offer

### 2. Flexibility Revenue Intelligence

- **Total flexibility revenue (full run):** £1,650.00
- **Revenue per enrolled customer-year:** £825.00
- **Enrollment trajectory:** 1 (2024) → 1 (2025)
- **DFS revenue since 2024:** £900.00 (CAGR 0%/yr)

### 3. Churn Pattern Analysis

- **Total lifetime churn events:** 6
- **Peak churn year:** 2021 (2 events)
- **Net book movement:** 1 acquisitions − 6 churns = -5
- **Portfolio trend:** shrinking

### 4. Board Recommendations

1. **Flexibility revenue:** 1 customers enrolled in CM/DFS as of 2025. Prioritise EV+battery acquisition — combined enrollment earns ~£2,046/yr vs EV-only ~£930/yr.
2. **Crisis-year churn:** 3 churn events in 2021–2022. Maintain minimum hedge floor pre-crisis to preserve pricing stability and limit bill-shock churn.

## CRM Intelligence: Risk Triage (Final Year)

Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.

| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |
|---------|-----|-----------|-----------|----------|-------------|-----------------|
| C6 | SME | HIGH | 38% | 25% | -24.9% [competitive] | £21,099.39 |
| C8 | resi | HIGH | 38% | 0% | -23.6% [competitive] | £11,512.07 |
| C9 | resi | HIGH | 38% | 0% | -14.3% | £11,805.82 |
| C2_2 | resi | HIGH | 38% | 4% | +14.0% [overpriced] | £5,102.47 |
| C5 | SME | HIGH | 35% | 83% | +63.8% [overpriced] | £8,505.43 |
| C7 | resi | HIGH | 35% | 0% | -14.3% | £9,778.96 |
| C1 | resi | HIGH | 32% | 4% | -12.0% | £2,320.62 |
| C3 | resi | HIGH | 32% | 0% | -39.1% [competitive] | £2,093.02 |
| C4 | resi | HIGH | 32% | 0% | -9.0% | £2,885.91 |
| C2 | resi | MEDIUM | 29% | 7% | +46.6% [overpriced] | £2,778.22 |
| C_IC3 | I&C | LOW | 8% | 95% | -54.9% [competitive] | £1,772,915.80 |
| C_IC1 | I&C | LOW | 5% | 95% | -0.1% | £1,851,432.22 |
| C_IC2 | I&C | LOW | 5% | 95% | +12.4% [overpriced] | £896,097.22 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 9 accounts
- MEDIUM (>=15%): 1 accounts
- LOW (<15%): 3 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £75,103.67
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
| C3 | resi | 2020-06-30 | 4.0yr | -4.5% | -39.1% | 32% | 0% | £2,093.02 |
| C1 | resi | 2021-12-30 | 6.0yr | +1.6% | -12.0% | 32% | 4% | £2,320.62 |
| C5 | SME | 2021-12-30 | 6.0yr | +1.6% | +63.8% | 35% | 83% | £8,505.43 |
| C2 | resi | 2022-03-31 | 6.0yr | +15.0% | +46.6% | 29% | 7% | £2,778.22 |
| C6 | SME | 2024-03-30 | 8.0yr | -0.9% | -24.9% | 38% | 25% | £21,099.39 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 32% | 0% | £2,885.91 |

**Root Cause Summary:**
- Total churned accounts: 6
- Lifetime margin lost: £39,682.58
- Average tenure at departure: 6.3 years
- Company blind misses (sim >=30%, co. est. <10%): 3 -- C3, C1, C4
- Company-warned churns (co. est. >=20%): 2 -- C5, C6
- Crisis-era churns (2021-22): 3 -- absolute crisis price level, not rate-change delta, was the driver
- Overpriced vs SVT at departure: 2 account(s) -- rate shock risk was observable but unactioned

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 5 accounts that churned without an offer? Calibrated from 18 actual offers (observed retention rate 94%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C3 | resi | 2020-06-30 | 0% | £583.78 | 5% | £29.19 | £522.16 | MISSED OPP. |
| C1 | resi | 2021-12-30 | 4% | £-178.13 | 5% | £0.00 | n/a | CORRECT PASS |
| C2 | resi | 2022-03-31 | 7% | £189.30 | 5% | £9.47 | £169.32 | MISSED OPP. |
| C6 | SME | 2024-03-30 | 25% | £2,851.77 | 8% | £228.14 | £2,465.19 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 0% | £569.88 | 5% | £28.49 | £509.72 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 5
- Correct no-offer (net-neg ETM): 1 (C1)
- Missed opportunities (positive ETM, below detection): 4
- Total term margin foregone: £4,194.73
- Total retention cost (counterfactual): £295.29
- Net counterfactual benefit: £3,666.40 (at 94% retention probability)
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
| 2021 | £5,207 | £4,339 | 0.30% |
| 2022 | £10,200 | £8,500 | 0.30% |
| 2023 | £6,727 | £5,606 | 0.26% |
| 2024 | £3,185 | £2,654 | 0.14% |
| 2025 | £4,636 | £3,863 | 0.48% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,200 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £524 | £91 | 11.3% |
| 2017 | 14 | £16,734 | £8,801 | £2,184 | 13.0% |
| 2018 | 15 | £29,020 | £17,500 | £6,646 | 22.9% |
| 2019 | 17 | £70,486 | £41,296 | £12,858 | 18.2% |
| 2020 | 18 | £67,961 | £43,986 | £6,488 | 9.5% |
| 2021 | 16 | £108,566 | £47,762 | £3,504 | 3.2% << |
| 2022 | 14 | £245,187 | £74,688 | £17,704 | 7.2% |
| 2023 | 12 | £212,262 | £75,698 | £3,879 | 1.8% << |
| 2024 | 12 | £184,108 | £106,587 | £25,969 | 14.1% |
| 2025 | 9 | £107,349 | £57,172 | £9,878 | 9.2% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £25,969 net/customer
**Worst year per customer:** 2016 at £91 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £423 | — | £423 |
| C1g | — | £645 | £645 |
| C2 | £703 | — | £703 |
| C2_2 | £1,055 | — | £1,055 |
| C2g | — | £802 | £802 |
| C3 | £203 | — | £203 |
| C3g | — | £288 | £288 |
| C4 | £129 | — | £129 |
| C4g | — | £-2,653 | £-2,653 * |
| C5 | £-35 | — | £-35 * |
| C6 | £3,577 | — | £3,577 |
| C7 | £-1,361 | — | £-1,361 * |
| C8 | £1,499 | — | £1,499 |
| C9 | £1,487 | — | £1,487 |
| C_IC1 | £824,839 | — | £824,839 |
| C_IC2 | £424,303 | — | £424,303 |
| C_IC3 | £81,800 | — | £81,800 |
| C_IC3g | — | £-134,500 | £-134,500 * |
| C_IC4 | £14,584 | — | £14,584 |
| **Total** | **£1,353,205** | **£-135,418** | **£1,217,787** |

Loss-making accounts: C_IC3g (£-134,500), C4g (£-2,653), C7 (£-1,361), C5 (£-35)
Gas loss-making: C_IC3g (£-134,500), C4g (£-2,653)
Gas portfolio net: £-135,418 (-11.1% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,034 | £10,920 | £-8,885 |
| 2017 | £30,081 | £112,465 | £-82,383 |
| 2018 | £109,563 | £246,436 | £-136,872 |
| 2019 | £243,311 | £825,240 | £-581,929 |
| 2020 | £73,534 | £938,528 | £-864,993 |
| 2021 | £137,326 | £348,597 | £-211,271 |
| 2022 | £97,739 | £1,081,023 | £-983,283 |
| 2023 | £356,008 | £1,149,109 | £-793,100 |
| 2024 | £168,132 | £545,495 | £-377,363 |
| 2025 | £58 | £337 | £-279 |
| **Total** | **£1,217,787** | **£5,258,151** | **£-4,040,363** |

Largest hedging cost: **2022** (£983,283 vs naked)
Smallest hedging cost: **2025** (£279 vs naked)
Conclusion: systematic forward hedging cost £4,040,363 over 10 years vs spot purchasing.

## Customer Service Quality

Ofgem benchmarks: bill clarity >0.82 (GREEN) / >0.80 (AMBER) / ≤0.80 (RED); complaint probability <5% (GREEN) / <6% (RED); bill shock <0.20% (GREEN) / <0.30% (AMBER) / ≥0.30% (RED).

| Year | Clarity | Complaint% | Shock% | Shock events | Bills | RAG |
|------|---------|------------|--------|--------------|-------|-----|
| 2016 | 0.829 G | 4.7% | 0.20% | 31 | 108 | GREEN |
| 2017 | 0.818 A | 4.7% | 0.17% | 50 | 168 | AMBER |
| 2018 | 0.810 A | 4.7% | 0.16% | 60 | 180 | AMBER |
| 2019 | 0.824 G | 4.7% | 0.17% | 66 | 204 | GREEN |
| 2020 | 0.830 G | 4.3% | 0.15% | 53 | 204 | GREEN |
| 2021 | 0.829 G | 4.5% | 0.16% | 51 | 192 | GREEN |
| 2022 | 0.790 R | 5.6% | 0.34% | 63 | 148 | RED ! |
| 2023 | 0.807 A | 4.9% | 0.17% | 43 | 144 | AMBER |
| 2024 | 0.811 A | 4.7% | 0.16% | 33 | 129 | AMBER |
| 2025 | 0.775 R | 5.9% | 0.24% | 20 | 54 | RED ! |

Worst clarity year: **2025** (0.775)
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
| 2017 | 2.69 | WATCH | £2,497,718 | £30,570 |
| 2018 | — | — | £2,486,407 | £99,686 |
| 2019 | — | — | £2,606,387 | £218,582 |
| 2020 | — | — | £2,900,041 | £116,780 |
| 2021 | — | — | £2,921,176 | £56,066 |
| 2022 | 2.70 | WATCH | £3,062,514 | £247,853 |
| 2023 | 2.73 | WATCH | £3,160,736 | £46,544 |
| 2024 | — | — | £3,516,327 | £311,625 |
| 2025 | — | — | £3,566,280 | £88,902 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,566,280)**
**Treasury growth: £2,467,424 → £3,566,280 (+£1,098,855)**

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
| C3 | 2020-06 | 0.0% | £584 | below threshold |
| C1 | 2021-12 | 3.8% | -£178 | below threshold |
| C2 | 2022-03 | 6.7% | £189 | below threshold |
| C6 | 2024-03 | 24.7% | £2,852 | below threshold ⚑ |
| C4 | 2024-09 | 0.0% | £570 | below threshold |

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
| C_IC3g | 2021-12 | 20.18 | 124.57 | 95.0% |

**High-risk gas reprices: 9**

> ⚑ = customers with ≥15% churn estimate who received no retention offer.

## Retention Decision Economics

Per-offer cost, expected margin protected, and ROI for each retention intervention.

| Customer | Period | Retention Cost £ | Margin Protected £ | ROI | Discount % | Outcome |
|----------|--------|-----------------|-------------------|-----|------------|---------|
| C_IC1 | 2018-01 | £24,227 | £163,688 | 6.8× | 8% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £27,951 | £194,971 | 7.0× | 8% | retained |
| C_IC3 | 2020-01 | £5,717 | £10,711 | 1.9× | 3% | retained |
| C_IC1 | 2020-03 | £10,372 | £130,843 | 12.6× | 5% | retained |
| C_IC3 | 2020-12 | £10,779 | £22,877 | 2.1× | 5% | retained |
| C_IC2 | 2021-03 | £14,128 | £90,892 | 6.4× | 8% | retained |
| C_IC1 | 2021-04 | £22,532 | £158,356 | 7.0× | 8% | retained |
| C5 | 2021-12 | £510 | £2,240 | 4.4× | 8% | churned_despite_offer |
| C_IC3 | 2021-12 | £82,844 | £164,760 | 2.0× | 8% | retained |
| C_IC2 | 2022-04 | £25,016 | £95,018 | 3.8× | 8% | retained |
| C_IC1 | 2022-05 | £48,202 | £229,391 | 4.8× | 8% | retained |
| C6 | 2023-03 | £231 | £3,262 | 14.1× | 3% | retained |
| C_IC2 | 2023-05 | £11,672 | £130,034 | 11.1× | 5% | retained |
| C_IC1 | 2023-06 | £34,630 | £242,775 | 7.0× | 8% | retained |
| C_IC3 | 2023-12 | £40,589 | £60,227 | 1.5× | 8% | retained |
| C_IC2 | 2024-06 | £10,231 | £133,341 | 13.0× | 5% | retained |
| C_IC1 | 2024-07 | £33,759 | £269,490 | 8.0× | 8% | retained |

**Total retention spend: £418,230** | **Total margin protected: £2,204,518**
**Portfolio retention ROI: 5.3×** | **Retained: 17/18**
**Best ROI intervention: C6 2023-03 (14.1×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | -£52,160 | — |
| Exit Gas (with churn risk) | £50,247 | +£102,407 |
| Reprice to Breakeven | £84,993 | +£137,153 |

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
| 2016 | 13 | 11 | 0.8 | £9 |
| 2017 | 12 | 33 | 2.8 | £401 |
| 2022 | 9 | 62 | 6.9 | £20,560 |
| 2023 | 4 | 32 | 8.0 | £48,871 |

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
| 2017 | £559 | £1,977 | — | £11,165 | £898 |
| 2018 | £1,019 | £9,350 | — | £17,434 | £905 |
| 2019 | £1,851 | £31,969 | — | £42,460 | £50,388 |
| 2020 | £2,375 | £56,547 | — | £69,454 | £47,215 |
| 2021 | £5,207 | £49,639 | £41,399 | £71,336 | £50,462 |
| 2022 | £10,200 | £36,643 | £99,381 | £70,920 | £54,503 |
| 2023 | £6,727 | £50,924 | £13,739 | £71,702 | £79,799 |
| 2024 | £3,185 | £68,649 | £1,997 | £72,815 | £76,501 |
| 2025 | £4,636 | £30,992 | £853 | £31,156 | £31,816 |

**Peak BSC credit obligation: 2022 (£10,200)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 14 | £168,372 | £90,922 | £6,761 | £12,027 |
| 2017 | 1 | £3,120,190 | £1,871,251 | £824,839 | £3,120,190 |
| 2018 | 1 | £1,522,855 | £907,430 | £424,303 | £1,522,855 |
| 2019 | 2 | £6,437,748 | £2,421,807 | -£52,700 | £3,218,874 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £14,584 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,218,874/customer)**
**Best net margin cohort: 2017 (£824,839)**
**Loss cohort: 2019 (net -£52,700)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £167 | — | 108 |
| 2017 | +£2,707 | £37,159 | £1,353 | — | 168 |
| 2018 | +£9,875 | £65,510 | £2,376 | — | 180 |
| 2019 | +£28,353 | £164,625 | £6,207 | — | 204 |
| 2020 | +£35,389 | £238,623 | £6,293 | — | 204 |
| 2021 | +£15,000 | £246,536 | £9,119 | — | 192 |
| 2022 | -£49,690 CREDIT | £255,965 | £35,498 | 1 | 148 |
| 2023 | +£64,715 | £271,644 | £13,727 | 1 | 144 |
| 2024 | +£109,837 | £307,361 | £11,429 | 1 | 129 |
| 2025 | +£46,893 | £135,564 | £4,916 | — | 54 |

**CfD turned CREDIT in 2022: -£49,690 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2022 (£35,498)**

> CfD (Contracts for Difference): when wholesale > strike price, generators repay;
> the net credit is passed through as a negative levy on supplier bills.

## Segment Gross Margin Attribution

Gross margin (£) by customer segment and year.

| Year | resi electricity | resi gas | SME electricity | I&C electricity | I&C gas | Total |
|------|----------|----------|----------|----------|----------|-------|
| 2016 | £3,270 | £811 | £2,733 | £0 | £0 | £6,814 |
| 2017 | £4,985 | £1,430 | £3,385 | £113,418 | £0 | £123,218 |
| 2018 | £5,056 | £1,363 | £3,202 | £252,882 | £0 | £262,503 |
| 2019 | £5,779 | £1,432 | £4,049 | £616,143 | £74,626 | £702,029 |
| 2020 | £5,618 | £1,218 | £4,236 | £704,698 | £75,972 | £791,743 |
| 2021 | £5,246 | £492 | £4,481 | £671,720 | £82,255 | £764,194 |
| 2022 | £3,726 | -£987 | £3,740 | £948,033 | £91,118 | £1,045,630 |
| 2023 | £7,275 | -£739 | £4,478 | £775,849 | £121,515 | £908,379 |
| 2024 | £8,578 | £925 | £1,521 | £1,144,364 | £123,652 | £1,279,040 |
| 2025 | £3,618 | £0 | £0 | £457,420 | £53,509 | £514,547 |

**Best gross margin year: 2024 (£1,279,040)** | **Worst: 2016 (£6,814)**
**Loss-making: resi gas in 2022 (£-987)**
**Loss-making: resi gas in 2023 (£-739)**


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
| 2021 | 9 | +9.1% | 5/9 | -12.0% | +63.8% |
| 2022 | 7 | +11.5% | 4/7 | -66.2% | +95.6% |
| 2023 | 7 | -37.0% | 0/7 | -60.5% | +-12.9% |
| 2024 | 7 | -24.2% | 0/7 | -54.9% | +-9.0% |
| 2025 | 2 | -4.8% | 1/2 | -23.6% | +14.0% |

**Best headroom year: 2023 (avg 37.0% below SVT)**
**Largest above-SVT year: 2022** (4/7 terms above — note: I&C customers exempt from SVT cap)

> SVT (Standard Variable Tariff) = Ofgem price cap. Residential tariffs must not exceed SVT.
> I&C/SME terms above SVT are expected during crisis years when wholesale >cap.

## Portfolio Stress Test History

Retrospective RAG status: would year-end treasury have survived each scenario?
Credit facility: £2M. Weekly burn estimated at 1% of year-end treasury.

| Year | Treasury £ | Mkt Spike | Credit | Demand | Liquidity | Combined |
|------|-----------|----------|----------|----------|----------|----------|
| 2016 | £2,467,424 | AMBER | RED | GREEN | AMBER | RED |
| 2017 | £2,497,718 | AMBER | RED | GREEN | AMBER | RED |
| 2018 | £2,486,407 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,606,387 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,900,041 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,921,176 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,062,514 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,160,736 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,516,327 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,566,280 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 45.2% | £1,181 | £605 | 1.53% |
| 2017 | 14 | 33.5% | £24,901 | £8,912 | 1.80% |
| 2018 | 15 | 41.6% | £40,062 | £17,610 | 1.97% |
| 2019 | 17 | 40.2% | £96,791 | £41,404 | 1.87% |
| 2020 | 18 | 40.2% | £103,165 | £44,086 | 2.06% |
| 2021 | 16 | 29.0% | £151,189 | £47,862 | 1.95% |
| 2022 | 14 | 21.2% | £302,473 | £74,777 | 1.98% |
| 2023 | 12 | 22.9% | £285,420 | £75,785 | 2.21% |
| 2024 | 12 | 38.3% | £251,641 | £106,611 | 2.13% |
| 2025 | 9 | 36.7% | £135,916 | £57,214 | 2.99% |

**Best EBIT%: 2016 (45.2%)** | **Worst EBIT%: 2022 (21.2%)**
**Peak revenue/customer: 2022 (£302,473)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Churn Prediction Calibration

How well the company estimated churn probability versus actual simulation outcomes.

| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |
|----------|------|----------------|-----------------|-------|---------|
| C3 | 2020-06 | 32.0% | 0.0% | -32.0pp | UNDERESTIMATED |
| C1 | 2021-12 | 32.0% | 3.8% | -28.2pp | UNDERESTIMATED |
| C5 | 2021-12 | 35.0% | 82.7% | +47.7pp | OVERESTIMATED |
| C2 | 2022-03 | 29.0% | 6.7% | -22.3pp | UNDERESTIMATED |
| C6 | 2024-03 | 38.0% | 24.7% | -13.3pp | UNDERESTIMATED |
| C4 | 2024-09 | 32.0% | 0.0% | -32.0pp | UNDERESTIMATED |

**Outcomes: 5 underestimated / 0 accurate / 1 overestimated**
**Mean absolute error: 29.3pp**
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
| 2018 | 14 | +2.5 | 6 | 8 | 2 |
| 2019 | 15 | +1.5 | 5 | 10 | 2 |
| 2020 | 18 | +3.2 | 9 | 9 | 2 |
| 2021 | 14 | +11.3 | 14 | 0 | 6 |
| 2022 | 11 | +18.2 | 10 | 1 | 6 |
| 2023 | 11 | +10.0 | 8 | 3 | 8 |
| 2024 | 10 | +8.1 | 6 | 4 | 3 |
| 2025 | 2 | +0.7 | 1 | 1 | 0 |

**Total adjustments 2016-2025: 112** | **Peak avg adjustment: 2022 (+18.2 £/MWh)**
**Emergency reprices: 29 total** (8 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £11,545 | £3,848 | — |
| 2017 | 9 | £37,276 | £4,142 | +£25,732 |
| 2018 | 10 | £1,005,753 | £100,575 | +£968,477 |
| 2019 | 11 | £1,438,949 | £130,814 | +£433,196 |
| 2020 | 13 | £2,723,695 | £209,515 | +£1,284,746 |
| 2021 | 13 | £2,644,254 | £203,404 | £-79,441 |
| 2022 | 14 | £2,820,361 | £201,454 | +£176,107 |
| 2023 | 14 | £2,843,124 | £203,080 | +£22,763 |
| 2024 | 14 | £3,192,092 | £228,007 | +£348,967 |
| 2025 | 14 | £3,418,844 | £244,203 | +£226,752 |

**Peak portfolio CLV: 2025 (£3,418,844)** | **Earliest/lowest: 2016 (£11,545)**
**Largest YoY gain: 2020 (+£1,284,746)**
**Largest YoY fall: 2021 (£-79,441)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | 51.2% | — | — | — | — |
| 2017 | £348,612.09 | £111,056.97 | £112,782.23 | £124,772.89 | 35.8% | +£333,257.48 | +£107,460.44 | +£108,889.99 | +£116,907.05 |
| 2018 | £600,924.19 | £172,802.12 | £163,976.80 | £264,145.28 | 44.0% | +£252,312.10 | +£61,745.15 | +£51,194.57 | +£139,372.38 |
| 2019 | £1,645,453.49 | £496,239.95 | £445,337.04 | £703,876.49 | 42.8% | +£1,044,529.29 | +£323,437.83 | +£281,360.24 | +£439,731.22 |
| 2020 | £1,856,974.75 | £431,604.81 | £631,826.80 | £793,543.14 | 42.7% | +£211,521.26 | £-64,635.14 | +£186,489.76 | +£89,666.65 |
| 2021 | £2,419,029.36 | £973,020.63 | £680,215.05 | £765,793.68 | 31.7% | +£562,054.61 | +£541,415.82 | +£48,388.24 | £-27,749.45 |
| 2022 | £4,234,619.06 | £2,387,052.89 | £800,694.40 | £1,046,871.77 | 24.7% | +£1,815,589.70 | +£1,414,032.26 | +£120,479.35 | +£281,078.08 |
| 2023 | £3,425,038.86 | £1,639,010.64 | £876,611.76 | £909,416.46 | 26.6% | £-809,580.19 | £-748,042.25 | +£75,917.36 | £-137,455.31 |
| 2024 | £3,019,689.47 | £931,043.39 | £809,315.61 | £1,279,330.46 | 42.4% | £-405,349.39 | £-707,967.25 | £-67,296.15 | +£369,914.01 |
| 2025 | £1,223,242.55 | £451,597.58 | £256,714.50 | £514,930.48 | 42.1% | £-1,796,446.92 | £-479,445.82 | £-552,601.12 | £-764,399.99 |

**Best GM year: 2016 (51.2%)** | **Worst GM year: 2022 (24.7%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Risk Committee Activity (2016-2025)

Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.

| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |
|------|----------|----------------------|----------------------|-----------------|
| 2016 | 13 | £28 | £9 | 1 |
| 2017 | 12 | £1,005 | £401 | 3 |
| 2022 | 9 | £55,562 | £20,560 | 8 |
| 2023 | 4 | £128,251 | £48,871 | 9 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £128,251 | Unique accounts ever adjusted: 11

**Most frequently adjusted accounts:**
- C1: 20 sessions
- C7: 19 sessions
- C2: 13 sessions
- C5: 12 sessions
- C6: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £7,544.43 | Median churn: 32% | Total portfolio CLV: £5,963,611.69

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £2,449,685.16 | 8% | 10.0 periods |
| C_IC1 | £1,438,740.77 | 8% | 10.2 periods |
| C_IC4 | £1,239,657.26 | 14% | 8.8 periods |
| C_IC2 | £774,349.92 | 11% | 9.8 periods |

Quadrant CLV: £5,902,433.11 (99% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C6 | £15,057.00 | 38% | 8.9 periods |
| C5 | £8,437.09 | 35% | 9.5 periods |
| C9 | £7,544.43 | 38% | 9.0 periods |

Quadrant CLV: £31,038.52 (1% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C2 | £4,802.90 | 29% | 9.9 periods |

Quadrant CLV: £4,802.90 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £7,234.11 | 38% | 8.8 periods |
| C7 | £6,636.17 | 35% | 9.9 periods |
| C3 | £4,917.97 | 32% | 9.3 periods |
| C1 | £3,752.23 | 32% | 9.4 periods |
| C4 | £2,796.67 | 32% | 9.7 periods |

Quadrant CLV: £25,337.15 (0% of portfolio)

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
| 2022 | 0.790 | 0.056 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.807 | 0.049 | 0 | 0 |  |
| 2024 | 0.811 | 0.047 | 2 | 0 |  |
| 2025 | 0.775 | 0.059 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.5% | **Average billing clarity:** 0.816 | **Average complaint probability:** 0.048

**Acquisition performance:** 5 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2025** (0.775) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

## Bill Shock Analysis

Bill shock events occur when a customer's bill increases >20% vs the prior bill.
Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.

| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |
|------|------------|--------|-------|------------|------|
| 2016 | 19.7% | 31 | 108 | 29% |  |
| 2017 | 16.5% | 50 | 168 | 30% |  |
| 2018 | 16.0% | 60 | 180 | 33% |  |
| 2019 | 17.1% | 66 | 204 | 32% |  |
| 2020 | 14.5% | 53 | 204 | 26% |  |
| 2021 | 16.1% | 51 | 192 | 27% |  |
| 2022 | 34.1% | 63 | 148 | 43% | **HIGH** |
| 2023 | 17.4% | 43 | 144 | 30% |  |
| 2024 | 16.2% | 33 | 129 | 26% |  |
| 2025 | 24.0% | 20 | 54 | 37% | ELEVATED |

**Crisis peak: 2022** — 34.1% average shock. Energy crisis drove wholesale costs above locked tariff rates,
causing step-change increases at every renewal. SLC 21: suppliers must issue
renewal notice 42 days before contract end, giving customers time to switch.

## Policy Cost & Levy Breakdown

UK energy levies collected through supplier bills. Policy costs are non-commodity costs
passed through to customers. CfD levy went negative in 2022 (crisis: spot exceeded strike prices;
renewable generators repaid back via levy mechanism).

| Year | RO | CfD | CCL | CM | FiT | Total Policy | Network |
|------|----|-----|-----|----|-----|-------------|---------|
| 2016 | £1,161.79 | £7.45 | £189.19 | £37.24 | £305.34 | £1,701.01 | £3,202.38 |
| 2017 | £37,159.19 | £2,706.77 | £11,164.93 | £1,976.65 | £9,940.12 | £62,947.66 | £26,175.96 |
| 2018 | £65,510.23 | £9,875.24 | £17,433.71 | £9,349.95 | £17,283.87 | £119,453.00 | £38,554.65 |
| 2019 | £164,624.73 | £28,352.67 | £42,460.21 | £31,969.18 | £44,301.87 | £311,708.66 | £88,387.10 |
| 2020 | £238,622.77 | £35,388.97 | £69,454.47 | £56,546.55 | £70,019.62 | £470,032.38 | £124,559.14 |
| 2021 | £246,536.25 | £14,999.73 | £71,335.52 | £49,639.45 | £62,792.12 | £486,702.31 | £123,439.31 |
| 2022 | £255,965.48 | **£-49,690.33** | £70,920.22 | £36,642.77 | £69,044.94 | £482,263.74 | £132,891.46 |
| 2023 | £271,644.07 | £64,714.91 | £71,701.96 | £50,923.98 | £75,039.71 | £547,764.11 | £138,888.15 |
| 2024 | £307,360.60 | £109,837.20 | £72,815.13 | £68,648.91 | £82,491.29 | £643,150.16 | £142,866.50 |
| 2025 | £135,563.73 | £46,893.11 | £31,155.87 | £30,992.09 | £36,107.70 | £281,565.10 | £61,008.53 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.01 (2016) → £281,565.10 (2025). CAGR: 76.4%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £881.72 | £296.53 | £9,021.95 | £1,388.28 | 13.3% | YES |
| 2017 | £30,106.36 | £463.34 | £231,614.54 | £2,660.42 | 1.1% | YES |
| 2018 | £99,311.74 | £374.66 | £432,180.01 | £3,113.94 | 0.7% | YES |
| 2019 | £218,115.51 | £466.22 | £1,060,495.65 | £137,770.25 | 11.5% | YES |
| 2020 | £112,348.54 | £4,431.62 | £1,102,155.97 | £121,133.74 | 9.9% | YES |
| 2021 | £58,138.21 | £-2,072.67 | £1,439,134.81 | £297,922.34 | 17.2% | **NO** |
| 2022 | £297,722.03 | £-49,868.55 | £2,843,943.53 | £588,681.38 | 17.1% | **NO** |
| 2023 | £79,159.15 | £-32,614.80 | £2,249,385.06 | £297,764.54 | 11.7% | **NO** |
| 2024 | £348,795.69 | £-37,170.35 | £1,938,506.33 | £270,787.76 | 12.3% | **NO** |
| 2025 | £108,626.18 | £-19,724.42 | £833,690.41 | £132,453.71 | 13.7% | **NO** |

**Gas has been loss-making since 2021** (5 consecutive years). Electricity cross-subsidises gas supply.

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £-52,159.59 | — | Current strategy |
| EXIT_GAS | £50,247.10 | £102,406.69 | Remove gas; model elec churn risk |
| REPRICE_GAS | £84,993.24 | £137,152.83 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-2,652.71 | -15.39x | +22.7% |
| C_IC3g | £-134,500.12 | -0.72x | +7.3% |

**Accretive gas accounts:** C1g (£645.06), C2g (£801.77), C3g (£287.57) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £135418 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,684,526.21 | £49,834.13 | £1,345,525.63 | 27.0x | Strong |
| I&C gas | £622,647.03 | £186,915.65 | £-134,500.12 | -0.7x | CAPITAL DESTROYER |
| SME electricity | £31,825.71 | £341.64 | £3,541.94 | 10.4x | Moderate |
| resi electricity | £53,151.54 | £569.45 | £4,137.56 | 7.3x | Moderate |
| resi gas | £5,944.60 | £228.27 | £-918.32 | -4.0x | CAPITAL DESTROYER |

**Gas Segment Finding:**
- Gas supply legs are net-negative over the simulation period (£-135,418.44 net on £187,143.92 capital)
- Electricity segments (£1,353,205.12 net) cross-subsidise gas retention
- Board decision required: is dual-fuel gas justified by CLV, or does it need pricing reform?

## Portfolio Concentration Risk

Revenue concentration analysis across 19 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2247** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,224,105.86 (98.7% of total positive margin)
- resi: £53,772.24 (0.9% of total positive margin)
- SME: £29,604.82 (0.5% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,851,432.22 | 29.4% | 5% | £92,571.61 |
| C_IC3 | I&C | £1,772,915.80 | 28.1% | 8% | £141,833.26 |
| C_IC4 | I&C | £1,090,243.56 | 17.3% | 0% | £0.00 |
| C_IC2 | I&C | £896,097.22 | 14.2% | 5% | £44,804.86 |
| C_IC3g | I&C | £613,417.06 | 9.7% | 0% | £0.00 |

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
| C2 | electricity | 2017-04-01 | 11.5% | -1.7% | £127.97/MWh | £125.75/MWh |
| C2g | gas | 2017-04-01 | 19.8% | -5.0% | £34.54/MWh | £32.81/MWh |
| C6 | electricity | 2017-04-01 | 10.7% | -1.4% | £127.97/MWh | £126.25/MWh |
| C8 | electricity | 2017-04-01 | 9.9% | -0.9% | £127.97/MWh | £126.78/MWh |
| C3 | electricity | 2017-07-01 | 11.2% | -1.6% | £122.23/MWh | £120.29/MWh |
| C3g | gas | 2017-07-01 | 20.5% | -5.0% | £24.33/MWh | £23.11/MWh |
| C9 | electricity | 2017-07-01 | 10.8% | -1.4% | £122.23/MWh | £120.50/MWh |
| C4 | electricity | 2017-10-01 | 10.8% | -1.4% | £111.62/MWh | £110.06/MWh |
| C4g | gas | 2017-10-01 | 18.4% | -5.0% | £27.48/MWh | £26.10/MWh |
| C1 | electricity | 2017-12-31 | 11.9% | -1.9% | £120.10/MWh | £117.78/MWh |
| C1g | gas | 2017-12-31 | 15.4% | -3.7% | £34.79/MWh | £33.49/MWh |
| C5 | electricity | 2017-12-31 | 8.9% | -0.4% | £120.10/MWh | £119.57/MWh |
| C7 | electricity | 2017-12-31 | 3.7% | +2.1% | £120.10/MWh | £122.67/MWh |
| C_IC1 | electricity | 2018-01-31 | -18.1% | +13.1% | £112.24/MWh | £126.92/MWh |
| C2 | electricity | 2018-04-01 | -6.9% | +7.5% | £133.89/MWh | £143.89/MWh |
| C2g | gas | 2018-04-01 | 15.4% | -3.7% | £38.21/MWh | £36.79/MWh |
| C6 | electricity | 2018-04-01 | -4.4% | +6.2% | £133.89/MWh | £142.17/MWh |
| C8 | electricity | 2018-04-01 | 8.2% | -0.1% | £133.89/MWh | £133.79/MWh |
| C3 | electricity | 2018-07-01 | 10.2% | -1.1% | £128.29/MWh | £126.90/MWh |
| C3g | gas | 2018-07-01 | 13.6% | -2.8% | £29.63/MWh | £28.80/MWh |
| C9 | electricity | 2018-07-01 | 1.8% | +3.1% | £128.29/MWh | £132.25/MWh |
| C4 | electricity | 2018-10-01 | 2.0% | +3.0% | £145.00/MWh | £149.37/MWh |
| C4g | gas | 2018-10-01 | 13.7% | -2.8% | £34.60/MWh | £33.61/MWh |
| C1 | electricity | 2018-12-31 | 6.7% | +0.7% | £148.68/MWh | £149.68/MWh |
| C1g | gas | 2018-12-31 | 13.9% | -3.0% | £37.15/MWh | £36.05/MWh |
| C5 | electricity | 2018-12-31 | 9.2% | -0.6% | £148.68/MWh | £147.78/MWh |
| C7 | electricity | 2018-12-31 | 9.6% | -0.8% | £148.68/MWh | £147.53/MWh |
| C_IC2 | electricity | 2019-01-31 | -30.2% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -20.5% | +14.2% | £128.22/MWh | £146.50/MWh |
| C2 | electricity | 2019-04-01 | 3.2% | +2.4% | £148.35/MWh | £151.90/MWh |
| C2g | gas | 2019-04-01 | 8.7% | -0.3% | £32.94/MWh | £32.82/MWh |
| C6 | electricity | 2019-04-01 | 7.5% | +0.2% | £148.35/MWh | £148.72/MWh |
| C8 | electricity | 2019-04-01 | 27.0% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 19.5% | -5.0% | £127.03/MWh | £120.68/MWh |
| C3g | gas | 2019-07-01 | 11.5% | -1.8% | £23.62/MWh | £23.21/MWh |
| C9 | electricity | 2019-07-01 | 10.0% | -1.0% | £127.03/MWh | £125.75/MWh |
| C4 | electricity | 2019-10-01 | 7.9% | +0.0% | £126.72/MWh | £126.76/MWh |
| C4g | gas | 2019-10-01 | 15.6% | -3.8% | £20.41/MWh | £19.63/MWh |
| C1 | electricity | 2019-12-31 | 10.5% | -1.3% | £127.44/MWh | £125.83/MWh |
| C1g | gas | 2019-12-31 | 13.0% | -2.5% | £26.17/MWh | £25.52/MWh |
| C5 | electricity | 2019-12-31 | 10.1% | -1.1% | £127.44/MWh | £126.10/MWh |
| C7 | electricity | 2019-12-31 | 8.9% | -0.4% | £127.44/MWh | £126.88/MWh |
| C_IC3 | electricity | 2020-01-01 | 7.5% | +0.3% | £47.59/MWh | £47.71/MWh |
| C_IC3g | gas | 2020-01-01 | 21.2% | -5.0% | £16.25/MWh | £15.44/MWh |
| C_IC2 | electricity | 2020-03-01 | -59.4% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -52.0% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 18.1% | -5.0% | £22.80/MWh | £21.66/MWh |
| C6 | electricity | 2020-03-31 | -46.9% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -15.8% | +11.9% | £125.12/MWh | £140.03/MWh |
| C_IC1 | electricity | 2020-03-31 | 20.5% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 16.9% | -4.5% | £113.43/MWh | £108.37/MWh |
| C9 | electricity | 2020-06-30 | 16.9% | -4.5% | £113.43/MWh | £108.37/MWh |
| C4 | electricity | 2020-09-30 | 11.1% | -1.5% | £124.42/MWh | £122.52/MWh |
| C4g | gas | 2020-09-30 | 19.9% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 9.6% | -0.8% | £133.55/MWh | £132.48/MWh |
| C1g | gas | 2020-12-30 | 13.7% | -2.9% | £28.99/MWh | £28.16/MWh |
| C5 | electricity | 2020-12-30 | 4.5% | +1.7% | £133.55/MWh | £135.86/MWh |
| C7 | electricity | 2020-12-30 | -3.1% | +5.5% | £133.55/MWh | £140.96/MWh |
| C_IC3 | electricity | 2020-12-31 | -4.3% | +6.2% | £50.65/MWh | £53.77/MWh |
| C_IC3g | gas | 2020-12-31 | 6.7% | +0.7% | £20.05/MWh | £20.18/MWh |
| C2 | electricity | 2021-03-31 | -20.8% | +14.4% | £175.90/MWh | £201.25/MWh |
| C2g | gas | 2021-03-31 | 5.9% | +1.1% | £36.20/MWh | £36.58/MWh |
| C6 | electricity | 2021-03-31 | -15.6% | +11.8% | £175.90/MWh | £196.64/MWh |
| C8 | electricity | 2021-03-31 | -11.4% | +9.7% | £175.90/MWh | £192.95/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.1% | +6.0% | £138.90/MWh | £147.29/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.8% | +3.6% | £113.97/MWh | £118.07/MWh |
| C9 | electricity | 2021-06-30 | 1.0% | +3.5% | £170.38/MWh | £176.31/MWh |
| C4 | electricity | 2021-09-30 | -2.5% | +5.2% | £205.15/MWh | £215.88/MWh |
| C4g | gas | 2021-09-30 | 0.2% | +3.9% | £53.99/MWh | £56.09/MWh |
| C1 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.74/MWh |
| C5 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.74/MWh |
| C7 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.74/MWh |
| C_IC3 | electricity | 2021-12-31 | -22.8% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -19.6% | +13.8% | £109.48/MWh | £124.57/MWh |
| C2 | electricity | 2022-03-31 | -23.1% | +15.0% | £361.95/MWh | £416.24/MWh |
| C6 | electricity | 2022-03-31 | -16.8% | +12.4% | £361.95/MWh | £406.89/MWh |
| C8 | electricity | 2022-03-31 | 5.1% | +1.4% | £361.95/MWh | £367.17/MWh |
| C_IC2 | electricity | 2022-04-30 | -9.5% | +8.7% | £269.81/MWh | £293.38/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.1% | +7.0% | £239.42/MWh | £256.28/MWh |
| C9 | electricity | 2022-06-30 | 4.2% | +1.9% | £255.09/MWh | £259.86/MWh |
| C4 | electricity | 2022-09-30 | 7.1% | +0.4% | £404.86/MWh | £406.58/MWh |
| C4g | gas | 2022-09-30 | -22.9% | +15.0% | £183.79/MWh | £211.36/MWh |
| C7 | electricity | 2022-12-30 | 8.5% | -0.2% | £266.73/MWh | £266.13/MWh |
| C_IC3 | electricity | 2022-12-31 | -0.0% | +4.0% | £168.36/MWh | £175.12/MWh |
| C_IC3g | gas | 2022-12-31 | -41.2% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -12.2% | +10.1% | £319.17/MWh | £351.37/MWh |
| C6 | electricity | 2023-03-31 | -0.9% | +4.5% | £319.17/MWh | £333.36/MWh |
| C8 | electricity | 2023-03-31 | 5.7% | +1.1% | £319.17/MWh | £322.80/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.5% | +14.8% | £171.46/MWh | £196.75/MWh |
| C_IC1 | electricity | 2023-06-29 | -16.7% | +12.3% | £163.19/MWh | £183.31/MWh |
| C9 | electricity | 2023-06-30 | -10.5% | +9.2% | £224.44/MWh | £245.17/MWh |
| C4 | electricity | 2023-09-30 | 9.5% | -0.8% | £216.77/MWh | £215.09/MWh |
| C4g | gas | 2023-09-30 | -45.4% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 28.7% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 23.3% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -16.1% | +12.1% | £51.89/MWh | £58.15/MWh |
| C2_2 | electricity | 2024-03-30 | 15.9% | -3.9% | £207.71/MWh | £199.55/MWh |
| C6 | electricity | 2024-03-30 | 9.9% | -0.9% | £207.71/MWh | £205.75/MWh |
| C8 | electricity | 2024-03-30 | 9.9% | -0.9% | £207.71/MWh | £205.75/MWh |
| C_IC2 | electricity | 2024-06-28 | -33.9% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.2% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C7 | electricity | 2024-12-29 | 0.4% | +3.8% | £243.79/MWh | £253.01/MWh |
| C_IC3 | electricity | 2024-12-30 | 18.8% | -5.0% | £116.37/MWh | £110.55/MWh |
| C_IC3g | gas | 2024-12-30 | -17.5% | +12.7% | £50.47/MWh | £56.89/MWh |
| C2_2 | electricity | 2025-03-30 | 9.0% | -0.5% | £284.89/MWh | £283.51/MWh |
| C8 | electricity | 2025-03-30 | 6.1% | +0.9% | £284.89/MWh | £287.61/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **5** | Blind misses: **5** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 4 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £4,016.60 | deliberate: £0.00 | total: £4,016.60

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.32 | Yes | £583.78 |
| C1 | 2021-12-30 | Blind miss | 0.04 | 0.32 | Yes | £-178.13 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.29 | No | £189.30 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.38 | Yes | £2,851.77 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.32 | Yes | £569.88 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C2+C2g | £703.32 | £801.77 | £1,505.08 | Yes |
| C1+C1g | £423.48 | £645.06 | £1,068.54 | Yes |
| C3+C3g | £202.72 | £287.57 | £490.28 | Yes |
| C4+C4g | £129.46 | £-2,652.71 | £-2,523.25 | No |
| C_IC3+C_IC3g | £81,799.88 | £-134,500.12 | £-52,700.24 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-135,418.44.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,217,786.69 across 19 billing accounts. Revenue: £13,993,804.61.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,120,190.02 | £1,871,251.30 | £18,394.12 | £824,839.17 | 26.4% |
| 2 | C_IC2 | fixed | £1,522,855.42 | £907,429.68 | £8,512.87 | £424,302.79 | 27.9% |
| 3 | C_IC3 | pass_through | £4,605,168.57 | £1,799,159.96 | £22,927.14 | £81,799.88 | 1.8% |
| 4 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £14,583.80 | 0.5% |
| 5 | C6 | fixed | £38,934.13 | £22,448.51 | £264.32 | £3,576.91 | 9.2% |
| 6 | C8 | fixed | £21,670.64 | £12,450.92 | £134.80 | £1,498.51 | 6.9% |
| 7 | C9 | fixed | £20,237.76 | £12,702.29 | £131.42 | £1,486.68 | 7.3% |
| 8 | C2_2 | fixed | £10,291.40 | £5,483.79 | £67.89 | £1,054.83 | 10.2% |
| 9 | C2g | fixed | £3,849.77 | £2,019.21 | £21.85 | £801.77 | 20.8% |
| 10 | C2 | fixed | £4,798.81 | £3,204.13 | £23.59 | £703.32 | 14.7% |
| 11 | C1g | fixed | £2,896.32 | £1,543.05 | £18.80 | £645.06 | 22.3% |
| 12 | C1 | fixed | £4,226.15 | £2,735.07 | £19.17 | £423.48 | 10.0% |
| 13 | C3g | fixed | £2,688.18 | £1,303.40 | £15.29 | £287.57 | 10.7% |
| 14 | C3 | fixed | £3,625.34 | £2,385.47 | £14.75 | £202.72 | 5.6% |
| 15 | C4 | fixed | £6,589.52 | £3,457.59 | £38.49 | £129.46 | 2.0% |
| 16 | C5 | fixed | £15,192.34 | £9,377.20 | £77.33 | £-34.97 | -0.2% |
| 17 | C7 | fixed | £21,709.29 | £10,732.28 | £139.33 | £-1,361.44 | -6.3% |
| 18 | C4g | fixed | £11,662.16 | £1,078.95 | £172.33 | £-2,652.71 | -22.7% |
| 19 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £186,915.65 | £-134,500.12 | -7.3% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £13,993,805 | 100.0% |
| Wholesale cost | -£7,595,710 | 54.3% |
| **Gross supply margin** | **£6,398,095** | **45.7%** |
| Policy + Network costs | -£4,942,419 | 35.3% |
| Capital cost | -£237,889 | 1.7% |
| **Net supply margin** | **£1,217,787** | **8.7%** |

> *The ledger's `net_margin_gbp` (£6,173,973) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £11,992,853 | 47.4% | 11.2% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | -7.3% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £54,126 | 58.8% | 6.5% | CMA 3-8% | ✓ |
| resi/elec | £82,858 | 57.5% | 3.7% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £21,096 | 28.2% | -4.4% | Ofgem CMA 2-4% | ⚠ ANOMALY |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: ANOMALIES DETECTED**
- Segment resi/gas net -4.4% (benchmark Ofgem CMA 2-4%)
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
| Customer bills (all-in) | £19,738,965.63 |
|   Less: VAT remitted to HMRC | (£950,027.19) |
| = Revenue (ex-VAT) | £18,788,938.44 |
| Less: non-commodity pass-through | (£4,781,366.43) |
| Wholesale cost (settlement events) | (£7,595,709.52) |
| Gross margin | £6,411,862.49 |
| Capital charges | (£237,889.15) |
| Net margin | £6,173,973.33 |

_Cash reconciliation: of £19,738,965.63 billed, bad debt of £394,878.33 was written off, leaving £19,344,087.29 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £6,729,122.19._

| Acquisition spend | (£1,100.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £6,167,173.33 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | £234.62 | £834.62 | £6,944.88 (45.2%) |
| 2017 | £348,612.09 | £111,056.97 | £112,782.23 | £124,772.89 | £6,260.42 | £6,860.42 | £116,639.38 (33.5%) |
| 2018 | £600,924.19 | £172,802.12 | £163,976.80 | £264,145.28 | £11,822.08 | £12,422.08 | £250,195.23 (41.6%) |
| 2019 | £1,645,453.49 | £496,239.95 | £445,337.04 | £703,876.49 | £30,746.52 | £31,346.52 | £660,928.66 (40.2%) |
| 2020 | £1,856,974.75 | £431,604.81 | £631,826.80 | £793,543.14 | £38,268.28 | £39,018.28 | £747,130.03 (40.2%) |
| 2021 | £2,419,029.36 | £973,020.63 | £680,215.05 | £765,793.68 | £47,119.25 | £48,119.25 | £701,740.39 (29.0%) |
| 2022 | £4,234,619.06 | £2,387,052.89 | £800,694.40 | £1,046,871.77 | £84,051.06 | £84,651.06 | £896,645.97 (21.2%) |
| 2023 | £3,425,038.86 | £1,639,010.64 | £876,611.76 | £909,416.46 | £75,539.83 | £76,139.83 | £783,848.84 (22.9%) |
| 2024 | £3,019,689.47 | £931,043.39 | £809,315.61 | £1,279,330.46 | £64,311.35 | £65,461.35 | £1,157,896.30 (38.3%) |
| 2025 | £1,223,242.55 | £451,597.58 | £256,714.50 | £514,930.48 | £36,524.91 | £36,824.91 | £449,009.32 (36.7%) |
| **Total** | **£18,788,938.44** | | | | | | **£5,770,979.01 (30.7%)** |

**Best year:** 2024 — net £1,157,896.30 (38.3% margin)
**Worst year:** 2016 — net £6,944.88 (45.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,237,615.23 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,237,615.23** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,770,979.01 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,354.61 | +4.7% | £6,592.99 | £6,944.88 | +5.3% | AMBER |
| 2017 | £16,138.86 | £348,612.09 | +2060.1% | £7,252.29 | £116,639.38 | +1508.3% | RED |
| 2018 | £386,623.75 | £600,924.19 | +55.4% | £128,424.00 | £250,195.23 | +94.8% | RED |
| 2019 | £675,851.95 | £1,645,453.49 | +143.5% | £281,335.50 | £660,928.66 | +134.9% | RED |
| 2020 | £1,816,630.04 | £1,856,974.75 | +2.2% | £736,963.94 | £747,130.03 | +1.4% | GREEN |
| 2021 | £2,028,952.42 | £2,419,029.36 | +19.2% | £833,649.22 | £701,740.39 | -15.8% | RED |
| 2022 | £2,607,611.88 | £4,234,619.06 | +62.4% | £790,935.58 | £896,645.97 | +13.4% | AMBER |
| 2023 | £4,508,414.67 | £3,425,038.86 | -24.0% | £1,029,561.00 | £783,848.84 | -23.9% | RED |
| 2024 | £3,512,844.39 | £3,019,689.47 | -14.0% | £893,105.75 | £1,157,896.30 | +29.6% | RED |
| 2025 | £3,145,356.42 | £1,223,242.55 | -61.1% | £1,315,150.33 | £449,009.32 | -65.9% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,167,173.33

## 2016

**Trading & Risk**

- Net margin: £1,178.25 (gross £6,813.70, capital £86.34)
  - Electricity: gross £6,002.97, capital £78.97, net £881.72
  - Gas: gross £810.73, capital £7.36, net £296.53
- Treasury at year end: £2,467,424.50
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.23, (none), VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-01-31: treasury £2,466,648.39, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-03-01: treasury £2,466,660.65, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-03-31: treasury £2,466,672.63, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-04-30: treasury £2,466,683.74, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-05-30: treasury £2,466,694.75, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-06-29: treasury £2,466,705.34, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-07-29: treasury £2,466,716.06, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-08-28: treasury £2,466,726.80, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-09-27: treasury £2,466,737.73, (none), VaR (current £27.73 / stressed £8.52) ratio 3.25
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

- Net margin: £30,569.69 (gross £123,217.99, capital £1,273.09)
  - Electricity: gross £121,788.42, capital £1,258.25, net £30,106.36
  - Gas: gross £1,429.57, capital £14.85, net £463.34
- Treasury at year end: £2,497,718.04
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
- Average CLV (Point-in-Time, year-end 2017): £4,141.81
  - By billing account: C1 £1,925.07, C2 £3,735.54, C3 £3,578.17, C4 £3,313.16, C5 £4,557.02, C6 £8,376.41, C7 £3,198.78, C8 £4,613.04, C9 £3,979.09
- Bill shock events (>=20%): 50 -- C1g 2017-01-31 (31%); C1g 2017-02-28 (28%); C1g 2017-05-31 (30%); C1g 2017-06-30 (30%); C1g 2017-09-30 (21%); C1g 2017-11-30 (70%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-05-31 (34%); C2g 2017-06-30 (29%); C2g 2017-09-30 (27%); C2g 2017-11-30 (66%); C2g 2017-12-31 (22%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-05-31 (30%); C3g 2017-06-30 (23%); C3g 2017-09-30 (21%); C3g 2017-11-30 (59%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (28%); C4 2017-09-30 (21%); C4 2017-10-31 (26%); C4 2017-11-30 (26%); C4g 2017-01-31 (23%); C4g 2017-02-28 (22%); C4g 2017-05-31 (33%); C4g 2017-06-30 (35%); C4g 2017-09-30 (36%); C4g 2017-10-31 (22%); C4g 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): 9 at risk (≥20% churn prob): C1 32%, C2 29%, C3 23%, C4 29%, C5 32%, C6 35%, C7 38%, C8 35%, C9 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.78-£131.86/MWh, net margin £120.11
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £106.38
- C2 (electricity): tariff £107.62-£125.75/MWh, net margin £96.81
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £181.68
- C3 (electricity): tariff £98.21-£120.29/MWh, net margin £69.50
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £57.45
- C4 (electricity): tariff £98.43-£110.06/MWh, net margin £46.39
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £117.83
- C5 (electricity): tariff £119.57-£131.01/MWh, net margin £164.75
- C6 (electricity): tariff £107.62-£126.25/MWh, net margin £58.84
- C7 (electricity): tariff £96.38-£195.85/MWh, net margin £159.34
- C8 (electricity): tariff £84.56-£190.17/MWh, net margin £210.12
- C9 (electricity): tariff £77.16-£180.75/MWh, net margin £133.12
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £29,047.38

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.818, average bill shock 16.5%, bad debt provision £1,353.41, avg complaint probability 4.7%
- Solvency signal: £249,772/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,081.36 vs. naked (unhedged) net margin: £112,465.24
- hedging cost £82,383.88 vs. a fully unhedged book (commodity-only: actual net £30,081.36 vs. naked net £112,465.24)
  - C1: actual £15.30 vs. naked £330.29 -- hedging cost £314.99
  - C1g: actual £131.41 vs. naked £272.27 -- hedging cost £140.86
  - C2: actual £104.28 vs. naked £438.14 -- hedging cost £333.87
  - C2g: actual £207.48 vs. naked £448.25 -- hedging cost £240.78
  - C3: actual £110.85 vs. naked £513.26 -- hedging cost £402.41
  - C3g: actual £30.62 vs. naked £394.35 -- hedging cost £363.73
  - C4: actual £41.35 vs. naked £275.26 -- hedging cost £233.90
  - C4g: actual £44.94 vs. naked £544.66 -- hedging cost £499.72
  - C5: actual £-203.29 vs. naked £1,068.66 -- hedging cost £1,271.96
  - C6: actual £104.15 vs. naked £1,675.33 -- hedging cost £1,571.17
  - C7: actual £-49.31 vs. naked £820.07 -- hedging cost £869.39
  - C8: actual £254.38 vs. naked £990.05 -- hedging cost £735.67
  - C9: actual £241.83 vs. naked £951.55 -- hedging cost £709.73
  - C_IC1: actual £29,047.38 vs. naked £103,743.08 -- hedging cost £74,695.71

**Year narrative:** 2017 produced a net gain of £30,569.69 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 50 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £99,686.40 (gross £262,502.78, capital £1,527.97)
  - Electricity: gross £261,139.98, capital £1,506.90, net £99,311.74
  - Gas: gross £1,362.80, capital £21.07, net £374.66
- Treasury at year end: £2,486,407.37
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.92 (avg 0.92), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2018-03-01 period 27, net margin £-15.07

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £100,575.31
  - By billing account: C1 £2,044.66, C2 £3,368.07, C3 £3,280.65, C4 £2,553.05, C5 £4,135.17, C6 £7,019.05, C7 £3,118.00, C8 £3,912.85, C9 £3,746.54, C_IC1 £972,575.09
- Bill shock events (>=20%): 60 -- C1g 2018-04-30 (37%); C1g 2018-05-31 (29%); C1g 2018-06-30 (30%); C1g 2018-09-30 (25%); C1g 2018-10-31 (46%); C1g 2018-11-30 (27%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (28%); C2g 2018-05-31 (34%); C2g 2018-06-30 (34%); C2g 2018-09-30 (33%); C2g 2018-10-31 (45%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (28%); C3g 2018-05-31 (32%); C3g 2018-06-30 (29%); C3g 2018-08-31 (34%); C3g 2018-09-30 (34%); C3g 2018-10-31 (35%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (28%); C4 2018-09-30 (23%); C4 2018-10-31 (41%); C4 2018-11-30 (28%); C4g 2018-04-30 (36%); C4g 2018-05-31 (33%); C4g 2018-06-30 (36%); C4g 2018-09-30 (39%); C4g 2018-10-31 (85%); C4g 2018-11-30 (24%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 9 at risk (≥20% churn prob): C1 38%, C2 32%, C3 32%, C4 38%, C5 35%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £117.78-£149.68/MWh, net margin £15.60
- C1g (gas): tariff £33.49-£36.05/MWh, net margin £131.41
- C2 (electricity): tariff £125.75-£143.89/MWh, net margin £77.04
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £174.16
- C3 (electricity): tariff £120.29-£126.90/MWh, net margin £69.48
- C3g (gas): tariff £23.11-£28.80/MWh, net margin £26.42
- C4 (electricity): tariff £110.06-£149.37/MWh, net margin £62.31
- C4g (gas): tariff £26.10-£33.61/MWh, net margin £42.67
- C5 (electricity): tariff £119.57-£153.32/MWh, net margin £-202.30 -- **net-negative**
- C6 (electricity): tariff £126.25-£142.17/MWh, net margin £-46.57 -- **net-negative**
- C7 (electricity): tariff £96.38-£221.29/MWh, net margin £-46.98 -- **net-negative**
- C8 (electricity): tariff £99.61-£200.68/MWh, net margin £125.55
- C9 (electricity): tariff £94.68-£198.38/MWh, net margin £203.24
- C_IC1 (electricity): tariff £-82.12-£228.46/MWh, net margin £105,747.23
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,692.84 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.810, average bill shock 16.0%, bad debt provision £2,375.96, avg complaint probability 4.7%
- Solvency signal: £226,037/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £109,563.04 vs. naked (unhedged) net margin: £246,435.50
- hedging cost £136,872.46 vs. a fully unhedged book (commodity-only: actual net £109,563.04 vs. naked net £246,435.50)
  - C1: actual £94.01 vs. naked £560.96 -- hedging cost £466.94
  - C1g: actual £144.33 vs. naked £420.62 -- hedging cost £276.29
  - C2: actual £62.60 vs. naked £499.23 -- hedging cost £436.64
  - C2g: actual £158.01 vs. naked £399.99 -- hedging cost £241.98
  - C3: actual £26.68 vs. naked £557.91 -- hedging cost £531.24
  - C3g: actual £38.90 vs. naked £481.52 -- hedging cost £442.62
  - C4: actual £104.22 vs. naked £464.67 -- hedging cost £360.45
  - C4g: actual £68.19 vs. naked £870.63 -- hedging cost £802.44
  - C5: actual £120.54 vs. naked £1,980.66 -- hedging cost £1,860.13
  - C6: actual £-141.43 vs. naked £1,833.71 -- hedging cost £1,975.14
  - C7: actual £71.97 vs. naked £1,347.98 -- hedging cost £1,276.01
  - C8: actual £24.33 vs. naked £936.63 -- hedging cost £912.30
  - C9: actual £143.75 vs. naked £1,046.06 -- hedging cost £902.32
  - C_IC1: actual £115,339.80 vs. naked £201,588.62 -- hedging cost £86,248.82
  - C_IC2: actual £-6,692.84 vs. naked £33,446.32 -- hedging cost £40,139.15

**Year narrative:** 2018 produced a net gain of £99,686.40 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 60 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £218,581.72 (gross £702,028.98, capital £11,601.30)
  - Electricity: gross £625,971.03, capital £2,287.85, net £218,115.51
  - Gas: gross £76,057.95, capital £9,313.46, net £466.22
- Treasury at year end: £2,606,387.31
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
- Average CLV (Point-in-Time, year-end 2019): £130,813.54
  - By billing account: C1 £2,031.94, C2 £2,978.41, C3 £3,305.80, C4 £2,818.64, C5 £4,447.19, C6 £7,492.87, C7 £3,271.26, C8 £3,888.99, C9 £3,801.64, C_IC1 £874,214.78, C_IC2 £530,697.39
- Bill shock events (>=20%): 66 -- C1 2019-04-30 (21%); C1g 2019-01-31 (36%); C1g 2019-02-28 (26%); C1g 2019-05-31 (23%); C1g 2019-06-30 (35%); C1g 2019-10-31 (74%); C1g 2019-11-30 (43%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-01-31 (25%); C2g 2019-02-28 (26%); C2g 2019-04-30 (35%); C2g 2019-06-30 (32%); C2g 2019-07-31 (25%); C2g 2019-09-30 (30%); C2g 2019-10-31 (64%); C2g 2019-11-30 (28%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-02-28 (26%); C3g 2019-06-30 (33%); C3g 2019-07-31 (35%); C3g 2019-09-30 (35%); C3g 2019-10-31 (64%); C3g 2019-11-30 (31%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (31%); C4 2019-09-30 (25%); C4 2019-11-30 (26%); C4g 2019-01-31 (30%); C4g 2019-02-28 (25%); C4g 2019-05-31 (21%); C4g 2019-06-30 (33%); C4g 2019-07-31 (37%); C4g 2019-09-30 (31%); C4g 2019-10-31 (34%); C4g 2019-11-30 (35%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 10 at risk (≥20% churn prob): C1 35%, C2 29%, C3 32%, C4 38%, C5 38%, C6 29%, C7 35%, C8 38%, C9 32%, C_IC1 23%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£149.68/MWh, net margin £93.91
- C1g (gas): tariff £25.52-£36.05/MWh, net margin £144.52
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £127.48
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £121.37
- C3 (electricity): tariff £120.68-£126.90/MWh, net margin £25.68
- C3g (gas): tariff £23.21-£28.80/MWh, net margin £85.43
- C4 (electricity): tariff £126.76-£149.37/MWh, net margin £101.72
- C4g (gas): tariff £19.63-£33.61/MWh, net margin £80.27
- C5 (electricity): tariff £126.10-£153.32/MWh, net margin £119.73
- C6 (electricity): tariff £142.17-£148.72/MWh, net margin £92.86
- C7 (electricity): tariff £99.69-£221.29/MWh, net margin £71.78
- C8 (electricity): tariff £105.12-£211.40/MWh, net margin £154.84
- C9 (electricity): tariff £98.80-£198.38/MWh, net margin £145.34
- C_IC1 (electricity): tariff £0.00-£263.70/MWh, net margin £137,536.66
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £78,289.55
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £1,355.95
- C_IC3g (gas): tariff £27.53/MWh, net margin £34.62

**Portfolio Health**

- Capital cost ratio: 1.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.824, average bill shock 17.1%, bad debt provision £6,207.46, avg complaint probability 4.7%
- Solvency signal: £217,199/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £243,310.56 vs. naked (unhedged) net margin: £825,239.88
- hedging cost £581,929.32 vs. a fully unhedged book (commodity-only: actual net £243,310.56 vs. naked net £825,239.88)
  - C1: actual £75.37 vs. naked £487.42 -- hedging cost £412.06
  - C1g: actual £139.49 vs. naked £304.83 -- hedging cost £165.34
  - C2: actual £157.29 vs. naked £663.14 -- hedging cost £505.85
  - C2g: actual £93.46 vs. naked £403.54 -- hedging cost £310.08
  - C3: actual £35.26 vs. naked £668.43 -- hedging cost £633.17
  - C3g: actual £140.55 vs. naked £510.60 -- hedging cost £370.05
  - C4: actual £104.15 vs. naked £443.69 -- hedging cost £339.54
  - C4g: actual £106.85 vs. naked £579.54 -- hedging cost £472.69
  - C5: actual £-27.61 vs. naked £1,590.08 -- hedging cost £1,617.69
  - C6: actual £233.55 vs. naked £2,599.80 -- hedging cost £2,366.24
  - C7: actual £56.98 vs. naked £1,146.66 -- hedging cost £1,089.68
  - C8: actual £240.89 vs. naked £1,370.83 -- hedging cost £1,129.94
  - C9: actual £159.29 vs. naked £1,258.35 -- hedging cost £1,099.06
  - C_IC1: actual £154,845.76 vs. naked £295,650.82 -- hedging cost £140,805.05
  - C_IC2: actual £85,558.69 vs. naked £161,523.27 -- hedging cost £75,964.58
  - C_IC3: actual £1,355.95 vs. naked £289,938.26 -- hedging cost £288,582.30
  - C_IC3g: actual £34.62 vs. naked £66,100.62 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £218,581.72 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £116,780.16 (gross £791,742.55, capital £7,394.82)
  - Electricity: gross £714,551.90, capital £1,954.44, net £112,348.54
  - Gas: gross £77,190.65, capital £5,440.38, net £4,431.62
- Treasury at year end: £2,900,041.29
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
- Average CLV (Point-in-Time, year-end 2020): £209,514.96
  - By billing account: C1 £2,354.55, C2 £3,100.60, C3 £2,903.35, C4 £2,915.27, C5 £4,922.79, C6 £7,829.24, C7 £3,947.26, C8 £4,121.72, C9 £3,748.60, C_IC1 £648,773.07, C_IC2 £320,804.92, C_IC3 £1,040,421.02, C_IC4 £677,852.11
- Bill shock events (>=20%): 53 -- C1g 2020-01-31 (20%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-31 (35%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (22%); C4 2020-11-30 (24%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (48%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 10 at risk (≥20% churn prob): C1 29%, C2 32%, C3 32%, C4 32%, C5 35%, C6 32%, C7 35%, C8 38%, C9 41%, C_IC2 20%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£132.48/MWh, net margin £75.01
- C1g (gas): tariff £25.00-£25.52/MWh, net margin £139.56
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £172.88
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £133.50
- C3 (electricity): tariff £120.68/MWh, net margin £16.44
- C3g (gas): tariff £23.21/MWh, net margin £77.69
- C4 (electricity): tariff £122.52-£126.76/MWh, net margin £87.34
- C4g (gas): tariff £16.09-£19.63/MWh, net margin £75.56
- C5 (electricity): tariff £126.10-£135.86/MWh, net margin £-30.64 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.72/MWh, net margin £366.13
- C7 (electricity): tariff £99.69-£211.44/MWh, net margin £58.19
- C8 (electricity): tariff £110.02-£211.40/MWh, net margin £336.50
- C9 (electricity): tariff £85.15-£188.63/MWh, net margin £115.89
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £52,028.29
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £43,546.80
- C_IC3 (electricity): tariff £37.49-£80.65/MWh, net margin £11,005.43
- C_IC3g (gas): tariff £15.44-£20.18/MWh, net margin £4,005.30
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £4,570.28

**Portfolio Health**

- Capital cost ratio: 0.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.830, average bill shock 14.5%, bad debt provision £6,293.26, avg complaint probability 4.3%
- Solvency signal: £223,080/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £73,534.19 vs. naked (unhedged) net margin: £938,528.15
- hedging cost £864,993.96 vs. a fully unhedged book (commodity-only: actual net £73,534.19 vs. naked net £938,528.15)
  - C1: actual £-18.63 vs. naked £97.83 -- hedging cost £116.46
  - C1g: actual £22.28 vs. naked £-68.18 -- hedging added £90.47
  - C2: actual £163.34 vs. naked £495.04 -- hedging cost £331.69
  - C2g: actual £144.84 vs. naked £324.27 -- hedging cost £179.43
  - C4: actual £25.22 vs. naked £235.68 -- hedging cost £210.47
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C5: actual £-339.03 vs. naked £173.99 -- hedging cost £513.02
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-122.44 vs. naked £316.01 -- hedging cost £438.45
  - C8: actual £338.33 vs. naked £1,166.71 -- hedging cost £828.38
  - C9: actual £-21.81 vs. naked £694.44 -- hedging cost £716.25
  - C_IC1: actual £33,034.60 vs. naked £127,851.52 -- hedging cost £94,816.92
  - C_IC2: actual £42,303.73 vs. naked £95,603.52 -- hedging cost £53,299.79
  - C_IC3: actual £-16,472.43 vs. naked £220,518.57 -- hedging cost £236,991.00
  - C_IC3g: actual £6,308.59 vs. naked £147,619.15 -- hedging cost £141,310.56
  - C_IC4: actual £7,886.99 vs. naked £341,206.88 -- hedging cost £333,319.89

**Year narrative:** 2020 produced a net gain of £116,780.16 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £56,065.55 (gross £764,193.51, capital £15,934.05)
  - Electricity: gross £681,446.87, capital £5,607.40, net £58,138.21
  - Gas: gross £82,746.64, capital £10,326.64, net £-2,072.67
- Treasury at year end: £2,921,176.49
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
- Average CLV (Point-in-Time, year-end 2021): £203,404.15
  - By billing account: C1 £2,149.30, C2 £3,409.73, C3 £2,888.84, C4 £2,546.44, C5 £4,778.70, C6 £8,975.29, C7 £3,176.63, C8 £4,269.49, C9 £3,520.10, C_IC1 £580,052.44, C_IC2 £353,610.90, C_IC3 £1,044,043.93, C_IC4 £630,832.11
- Bill shock events (>=20%): 51 -- C1g 2021-05-31 (28%); C1g 2021-06-30 (45%); C1g 2021-10-31 (55%); C1g 2021-11-30 (53%); C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (21%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (23%); C4 2021-10-31 (48%); C4 2021-11-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (153%); C4g 2021-11-30 (58%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (82%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%)
- Churn risk (accounts renewing in 2021): 12 at risk (≥20% churn prob): C1 32%, C2 35%, C4 35%, C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC3 20%, C_IC4 29%

**Pricing & Margin**

- C1 (electricity): tariff £132.48/MWh, net margin £-18.35 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £21.95
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £145.80
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £99.84
- C4 (electricity): tariff £122.52-£183.00/MWh, net margin £-59.06 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-405.31 -- **net-negative**
- C5 (electricity): tariff £135.86/MWh, net margin £-335.26 -- **net-negative**
- C6 (electricity): tariff £143.89-£196.64/MWh, net margin £518.91
- C7 (electricity): tariff £110.75-£274.50/MWh, net margin £-132.05 -- **net-negative**
- C8 (electricity): tariff £110.02-£274.50/MWh, net margin £340.07
- C9 (electricity): tariff £85.15-£264.47/MWh, net margin £-15.18 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £26,816.41
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £55,159.28
- C_IC3 (electricity): tariff £42.24-£391.23/MWh, net margin £-27,607.01 -- **net-negative**
- C_IC3g (gas): tariff £20.18-£124.57/MWh, net margin £-1,789.15 -- **net-negative**
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £3,324.66

**Portfolio Health**

- Capital cost ratio: 2.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.829, average bill shock 16.1%, bad debt provision £9,118.62, avg complaint probability 4.5%
- Solvency signal: £243,431/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £137,325.63 vs. naked (unhedged) net margin: £348,596.65
- hedging cost £211,271.02 vs. a fully unhedged book (commodity-only: actual net £137,325.63 vs. naked net £348,596.65)
  - C2: actual £131.93 vs. naked £120.43 -- hedging added £11.51
  - C2g: actual £45.59 vs. naked £-190.70 -- hedging added £236.29
  - C4: actual £-220.41 vs. naked £-170.34 -- hedging cost £50.07
  - C4g: actual £-1,139.49 vs. naked £-1,151.50 -- hedging added £12.02
  - C6: actual £502.52 vs. naked £257.02 -- hedging added £245.50
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-48.30 vs. naked £-183.81 -- hedging added £135.51
  - C_IC1: actual £27,430.78 vs. naked £-61,786.33 -- hedging added £89,217.11
  - C_IC2: actual £63,120.51 vs. naked £21,141.99 -- hedging added £41,978.51
  - C_IC3: actual £100,280.50 vs. naked £234,763.46 -- hedging cost £134,482.96
  - C_IC3g: actual £-49,329.98 vs. naked £31,726.54 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £124,831.37 -- hedging cost £126,734.63

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £56,065.55 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 51 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £247,853.47 (gross £1,045,629.80, capital £65,574.74)
  - Electricity: gross £955,498.52, capital £13,161.85, net £297,722.03
  - Gas: gross £90,131.28, capital £52,412.89, net £-49,868.55
- Treasury at year end: £3,062,514.20
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,016,511.82, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,328.93 / stressed £20,508.02) ratio 2.70
  - 2022-05-29: treasury £3,016,632.84, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,438.75 / stressed £20,537.23) ratio 2.70
  - 2022-06-28: treasury £3,016,627.61, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,438.75 / stressed £20,537.23) ratio 2.70
  - 2022-07-28: treasury £3,016,434.98, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,500.15 / stressed £20,549.46) ratio 2.70
  - 2022-08-27: treasury £3,016,425.38, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,500.15 / stressed £20,549.46) ratio 2.70
  - 2022-09-26: treasury £3,016,409.93, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,500.15 / stressed £20,549.46) ratio 2.70
  - 2022-10-26: treasury £3,013,885.72, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,562.24 / stressed £20,559.92) ratio 2.70
  - 2022-11-25: treasury £3,013,735.30, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,562.24 / stressed £20,559.92) ratio 2.70
  - 2022-12-25: treasury £3,013,469.11, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,562.24 / stressed £20,559.92) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC3g on 2022-12-31 period 1, net margin £-2,998.80

**Customer Book**

- Active accounts: 14 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £201,454.36
  - By billing account: C1 £2,383.60, C2 £2,596.56, C2_2 £478.63, C3 £2,885.74, C4 £1,509.67, C5 £4,930.09, C6 £8,258.58, C7 £2,802.14, C8 £4,056.56, C9 £3,912.84, C_IC1 £645,935.71, C_IC2 £375,708.71, C_IC3 £1,165,061.18, C_IC4 £599,840.96
- Bill shock events (>=20%): 63 -- C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (35%); C4g 2022-06-30 (29%); C4g 2022-07-31 (24%); C4g 2022-09-30 (68%); C4g 2022-10-31 (138%); C4g 2022-11-30 (58%); C4g 2022-12-31 (57%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (109%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 9 at risk (≥20% churn prob): C2 29%, C4 38%, C6 32%, C7 35%, C8 35%, C9 38%, C_IC1 20%, C_IC3 23%, C_IC4 32%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £17.92
- C2_2 (electricity): tariff £361.95/MWh, net margin £28.76
- C2g (gas): tariff £35.00/MWh, net margin £-17.33 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-276.94 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,614.88 -- **net-negative**
- C6 (electricity): tariff £196.64-£406.89/MWh, net margin £818.81
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,826.12 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-189.35 -- **net-negative**
- C9 (electricity): tariff £138.53-£389.80/MWh, net margin £-115.85 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£461.30/MWh, net margin £129,867.86
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £72,012.90
- C_IC3 (electricity): tariff £137.59-£391.23/MWh, net margin £99,291.96
- C_IC3g (gas): tariff £120.39-£124.57/MWh, net margin £-48,236.35 -- **net-negative**
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £-1,907.93 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 6.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,359,814.69 -> £3,013,438.19 (10.3%)
- Bills issued: 148, average clarity 0.790, average bill shock 34.1%, bad debt provision £35,498.29, avg complaint probability 5.6%
- Solvency signal: £278,410/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £97,739.43 vs. naked (unhedged) net margin: £1,081,023.36
- hedging cost £983,283.93 vs. a fully unhedged book (commodity-only: actual net £97,739.43 vs. naked net £1,081,023.36)
  - C2_2: actual £30.18 vs. naked £1,645.15 -- hedging cost £1,614.97
  - C4: actual £-324.97 vs. naked £670.37 -- hedging cost £995.34
  - C4g: actual £-2,441.94 vs. naked £1,870.20 -- hedging cost £4,312.14
  - C6: actual £1,128.48 vs. naked £3,996.55 -- hedging cost £2,868.07
  - C7: actual £-345.82 vs. naked £2,281.71 -- hedging cost £2,627.53
  - C8: actual £-348.38 vs. naked £1,102.92 -- hedging cost £1,451.29
  - C9: actual £-47.42 vs. naked £1,014.32 -- hedging cost £1,061.73
  - C_IC1: actual £210,365.12 vs. naked £248,603.94 -- hedging cost £38,238.82
  - C_IC2: actual £86,153.89 vs. naked £125,442.04 -- hedging cost £39,288.14
  - C_IC3: actual £-169,265.37 vs. naked £444,340.12 -- hedging cost £613,605.49
  - C_IC3g: actual £-30,637.15 vs. naked £84,150.32 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £165,905.73 -- hedging cost £162,432.92

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £247,853.47 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 63 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £46,544.35 (gross £908,379.40, capital £49,427.78)
  - Electricity: gross £787,602.78, capital £9,689.35, net £79,159.15
  - Gas: gross £120,776.62, capital £39,738.44, net £-32,614.80
- Treasury at year end: £3,160,735.52
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,062,513.87, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,260.65 / stressed £43,938.54) ratio 2.76
  - 2023-02-23: treasury £3,062,514.22, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,260.65 / stressed £43,938.54) ratio 2.76
  - 2023-03-25: treasury £3,062,514.52, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,260.65 / stressed £43,938.54) ratio 2.76
  - 2023-04-24: treasury £3,141,533.86, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,251.28 / stressed £48,871.37) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-12-31 period 1, net margin £-3,508.81

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £203,080.32
  - By billing account: C1 £2,367.09, C2 £2,644.37, C2_2 £1,364.88, C3 £2,943.77, C4 £1,092.91, C5 £4,889.60, C6 £9,023.49, C7 £3,049.89, C8 £4,080.67, C9 £4,137.70, C_IC1 £699,406.81, C_IC2 £391,898.12, C_IC3 £1,087,180.28, C_IC4 £629,044.89
- Bill shock events (>=20%): 43 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (31%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-04-30 (30%); C4 2023-09-30 (25%); C4 2023-11-30 (28%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (47%); C4g 2023-11-30 (65%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (59%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (52%); C_IC2 2023-06-30 (100%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%)
- Churn risk (accounts renewing in 2023): 8 at risk (≥20% churn prob): C2_2 38%, C4 38%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC3 20%, C_IC4 26%

**Pricing & Margin**

- C2_2 (electricity): tariff £351.37-£361.95/MWh, net margin £512.06
- C4 (electricity): tariff £252.74-£305.00/MWh, net margin £-103.77 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,467.63 -- **net-negative**
- C6 (electricity): tariff £333.36-£406.89/MWh, net margin £1,268.95
- C7 (electricity): tariff £187.43-£457.50/MWh, net margin £-344.44 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-21.10 -- **net-negative**
- C9 (electricity): tariff £192.64-£389.80/MWh, net margin £227.55
- C_IC1 (electricity): tariff £-60.00-£461.30/MWh, net margin £158,430.45
- C_IC2 (electricity): tariff £-186.24-£475.06/MWh, net margin £83,912.41
- C_IC3 (electricity): tariff £100.54-£262.68/MWh, net margin £-168,203.21 -- **net-negative**
- C_IC3g (gas): tariff £61.27-£120.39/MWh, net margin £-31,147.16 -- **net-negative**
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £3,480.25

**Portfolio Health**

- Capital cost ratio: 5.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,546,315.82 -> £3,160,732.13 (10.9%)
- Bills issued: 144, average clarity 0.807, average bill shock 17.4%, bad debt provision £13,727.37, avg complaint probability 4.9%
- Solvency signal: £316,074/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £356,008.45 vs. naked (unhedged) net margin: £1,149,108.89
- hedging cost £793,100.44 vs. a fully unhedged book (commodity-only: actual net £356,008.45 vs. naked net £1,149,108.89)
  - C2_2: actual £841.82 vs. naked £2,434.45 -- hedging cost £1,592.62
  - C4: actual £351.38 vs. naked £829.41 -- hedging cost £478.03
  - C4g: actual £630.76 vs. naked £1,424.88 -- hedging cost £794.12
  - C6: actual £1,413.88 vs. naked £5,082.18 -- hedging cost £3,668.30
  - C7: actual £474.16 vs. naked £1,920.00 -- hedging cost £1,445.85
  - C8: actual £212.54 vs. naked £1,972.23 -- hedging cost £1,759.69
  - C9: actual £626.99 vs. naked £2,130.67 -- hedging cost £1,503.68
  - C_IC1: actual £140,522.29 vs. naked £283,387.59 -- hedging cost £142,865.30
  - C_IC2: actual £93,536.10 vs. naked £161,582.91 -- hedging cost £68,046.80
  - C_IC3: actual £150,989.84 vs. naked £424,996.30 -- hedging cost £274,006.46
  - C_IC3g: actual £-37,283.07 vs. naked £77,163.92 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £186,184.34 -- hedging cost £182,492.59

**Year narrative:** 2023 produced a net gain of £46,544.35 across 12 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 43 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £311,625.34 (gross £1,279,039.83, capital £55,972.82)
  - Electricity: gross £1,154,463.24, capital £9,615.92, net £348,795.69
  - Gas: gross £124,576.59, capital £46,356.90, net £-37,170.35
- Treasury at year end: £3,516,326.71
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
- Average CLV (Point-in-Time, year-end 2024): £228,006.55
  - By billing account: C1 £2,194.11, C2 £2,781.92, C2_2 £1,961.85, C3 £3,166.30, C4 £1,589.95, C5 £4,597.37, C6 £9,162.72, C7 £3,182.77, C8 £4,300.01, C9 £4,759.47, C_IC1 £715,884.83, C_IC2 £411,819.60, C_IC3 £1,287,486.15, C_IC4 £739,204.65
- Bill shock events (>=20%): 33 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (31%); C4g 2024-02-29 (27%); C4g 2024-05-31 (40%); C4g 2024-07-31 (25%); C4g 2024-09-28 (48%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (58%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (54%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C4 32%, C6 38%, C7 35%, C8 41%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.55-£351.37/MWh, net margin £424.57
- C4 (electricity): tariff £252.74/MWh, net margin £260.05
- C4g (gas): tariff £66.00/MWh, net margin £472.61
- C6 (electricity): tariff £333.36/MWh, net margin £492.86
- C7 (electricity): tariff £165.00-£357.81/MWh, net margin £473.75
- C8 (electricity): tariff £161.66-£397.50/MWh, net margin £333.84
- C9 (electricity): tariff £165.00-£367.76/MWh, net margin £560.92
- C_IC1 (electricity): tariff £-98.58-£329.96/MWh, net margin £122,959.07
- C_IC2 (electricity): tariff £-106.92-£354.14/MWh, net margin £68,558.62
- C_IC3 (electricity): tariff £86.86-£191.95/MWh, net margin £151,032.91
- C_IC3g (gas): tariff £61.27-£61.96/MWh, net margin £-37,642.96 -- **net-negative**
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £3,699.12

**Portfolio Health**

- Capital cost ratio: 4.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,546,227.45 -> £3,160,735.55 (10.9%)
- Bills issued: 129, average clarity 0.811, average bill shock 16.2%, bad debt provision £11,429.40, avg complaint probability 4.7%
- Solvency signal: £351,633/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £168,132.04 vs. naked (unhedged) net margin: £545,495.08
- hedging cost £377,363.04 vs. a fully unhedged book (commodity-only: actual net £168,132.04 vs. naked net £545,495.08)
  - C2_2: actual £98.66 vs. naked £1,036.85 -- hedging cost £938.19
  - C7: actual £-12.31 vs. naked £653.82 -- hedging cost £666.14
  - C8: actual £342.61 vs. naked £1,419.59 -- hedging cost £1,076.98
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £14,911.38 vs. naked £115,656.21 -- hedging cost £100,744.82
  - C_IC3g: actual £-23,593.14 vs. naked £29,503.44 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £75,291.91 -- hedging cost £73,856.39

**Year narrative:** 2024 produced a net gain of £311,625.34 across 12 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £88,901.76 (gross £514,546.54, capital £29,096.25)
  - Electricity: gross £461,037.76, capital £5,584.31, net £108,626.18
  - Gas: gross £53,508.78, capital £23,511.94, net £-19,724.42
- Treasury at year end: £3,566,279.51
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
- Average CLV (Point-in-Time, year-end 2025): £244,203.14
  - By billing account: C1 £2,176.03, C2 £2,750.71, C2_2 £2,071.00, C3 £2,941.70, C4 £1,598.61, C5 £4,752.29, C6 £8,812.27, C7 £3,535.97, C8 £4,122.94, C9 £4,524.62, C_IC1 £760,326.93, C_IC2 £440,601.91, C_IC3 £1,393,587.02, C_IC4 £787,041.97
- Bill shock events (>=20%): 20 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (34%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.55-£283.51/MWh, net margin £89.44
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-9.17 -- **net-negative**
- C8 (electricity): tariff £149.29-£308.63/MWh, net margin £87.25
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £195.49
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £62,405.83
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,516.09
- C_IC3 (electricity): tariff £86.86-£165.83/MWh, net margin £14,923.83
- C_IC3g (gas): tariff £61.96/MWh, net margin £-19,724.42 -- **net-negative**
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £1,417.43

**Portfolio Health**

- Capital cost ratio: 5.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 54, average clarity 0.775, average bill shock 24.0%, bad debt provision £4,915.91, avg complaint probability 5.9%
- Solvency signal: £445,785/customer (8 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £57.55 vs. naked (unhedged) net margin: £337.38
- hedging cost £279.83 vs. a fully unhedged book (commodity-only: actual net £57.55 vs. naked net £337.38)
  - C2_2: actual £84.17 vs. naked £218.49 -- hedging cost £134.31
  - C8: actual £-26.63 vs. naked £118.90 -- hedging cost £145.52

**Year narrative:** 2025 produced a net gain of £88,901.76 across 9 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 20 customer(s) experienced a bill shock of >=20%.
