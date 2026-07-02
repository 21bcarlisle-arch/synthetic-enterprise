# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,690,733.50
  (£1,224,097.28 net change)
- Solvency signal (final year): £446,576/customer (8 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £19,743,837.48
  VAT remitted to HMRC: (£950,266.07) | Revenue (ex-VAT): £18,793,571.42
  Non-commodity pass-through: (£4,781,108.63)
- Gross margin: £6,418,373.49
- Capital costs: £237,898.41
- Net margin: £6,180,475.08
- Capital cost ratio: 3.7% of gross
- Net margin as % of revenue: 32.9%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1531, average clarity 0.816,
  service quality score 0.905
- Enterprise value (CLV sum across 14 billing accounts): £5,987,457.53
- Cost to serve (whole portfolio): £90,618.88, net margin after cost to serve: £6,089,856.20
- Hedge effectiveness (whole window): hedging cost £4,039,001.95 vs. a fully unhedged book (commodity-only: actual net £1,224,097.28 vs. naked net £5,263,099.24)

- **2021** (crisis year): net margin £56,437.94, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £250,445.09, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2247, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | -0.7x (net £-134,790.07 on £187,116.34 capital) | **RED** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 4/6 departures (67%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 3.2%, max 15.6% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +33.1% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 32.9% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Gas segment ROC, Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,418,373.49, capital £237,898.41, net £6,180,475.08. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 3.7% (commodity basis, comparable to old model) / 3.7% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £56,437.94 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 32.9%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,180,475.08
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,263,099.24
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,039,001.95 vs. a fully unhedged book (commodity-only: actual net £1,224,097.28 vs. naked net £5,263,099.24)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,383.14 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £613,595.97 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £254.88 | £626.84 | £296.53 | £1,178.25 |
| 2017 | £29,047.38 | £0.00 | £233.41 | £821.92 | £463.34 | £30,566.05 |
| 2018 | £99,071.38 | £0.00 | £-244.55 | £504.67 | £374.66 | £99,706.17 |
| 2019 | £217,183.69 | £34.62 | £213.88 | £720.65 | £431.59 | £218,584.43 |
| 2020 | £111,150.85 | £4,005.30 | £335.48 | £875.65 | £426.32 | £116,793.60 |
| 2021 | £57,974.67 | £-1,789.15 | £190.40 | £275.14 | £-213.12 | £56,437.94 |
| 2022 | £301,625.53 | £-48,236.35 | £822.10 | £-2,464.34 | £-1,301.85 | £250,445.09 |
| 2023 | £80,509.48 | £-31,147.16 | £1,283.10 | £116.48 | £-1,164.32 | £49,597.58 |
| 2024 | £346,662.89 | £-37,642.96 | £500.05 | £1,999.89 | £396.91 | £311,916.78 |
| 2025 | £108,263.17 | £-19,724.42 | £0.00 | £332.66 | £0.00 | £88,871.41 |

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

- **Average absolute error:** 198.5%
- **Average signed error:** +52.8% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -82.1% | 82.1% |
| 2017 | 3 | -93.7% | 93.7% |
| 2018 | 4 | +402.8% | 497.2% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | +26.0% | 189.9% |
| 2021 | 9 | -6.7% | 120.3% |
| 2022 | 7 | -23.1% | 112.6% |
| 2023 | 7 | -4.4% | 131.5% |
| 2024 | 7 | +79.0% | 231.8% |
| 2025 | 2 | -94.4% | 94.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 34.9%, abs error 313.6%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.9%, abs error 148.4%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.2% | 0.0% | 82.1% |
| 2017 | 0 | 3 | 0.0% | 2.1% | 0.0% | 93.7% |
| 2018 | 2 | 2 | 19.1% | 49.9% | 51.4% | 943.1% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 16.6% | 0.5% | 281.5% | 98.4% |
| 2021 | 3 | 6 | 66.0% | 4.1% | 184.3% | 88.3% |
| 2022 | 0 | 7 | 0.0% | 19.5% | 0.0% | 112.6% |
| 2023 | 2 | 5 | 29.3% | 19.0% | 72.9% | 155.0% |
| 2024 | 3 | 4 | 39.9% | 0.0% | 407.4% | 100.0% |
| 2025 | 0 | 2 | 0.0% | 2.1% | 0.0% | 94.4% |

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
| 2017 | 3 | 0 (0%) | -14.3% | 119.9 | 140.0 |
| 2018 | 2 | 1 (50%) | +0.2% | 152.9 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -25.9% | 130.9 | 176.9 |
| 2021 | 6 | 3 (50%) | +0.9% | 184.2 | 183.8 |
| 2022 | 7 | 4 (57%) | +11.5% | 294.6 | 318.4 |
| 2023 | 5 | 0 (0%) | -32.1% | 226.3 | 364.0 |
| 2024 | 4 | 0 (0%) | -16.2% | 205.6 | 246.9 |
| 2025 | 2 | 1 (50%) | -4.7% | 236.9 | 248.6 |

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
| 2020 | 10 | 1.90× | 10.80× |
| 2021 | 9 | 1.20× | 3.75× |
| 2022 | 7 | 1.13× | 3.13× |
| 2023 | 7 | 1.32× | 3.75× |
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
| 2021 | 11 | 1.10% | 4.24% | MODERATE — asset adoption visible |
| 2022 | 9 | 2.12% | 7.47% | MODERATE — asset adoption visible |
| 2023 | 9 | 2.60% | 8.47% | HIGH drift — EV/asset cohort growing |
| 2024 | 9 | 3.21% | 15.56% | HIGH drift — EV/asset cohort growing |
| 2025 | 2 | 1.42% | 2.07% | MODERATE — asset adoption visible |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **3.21%** mean / **15.56%** max in 2024. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
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
| 2022 | 9 | 2.1% | 7.5% |
| 2023 | 9 | 2.6% | 8.5% |
| 2024 | 9 | 3.2% | 15.6% |
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

**Portfolio demand trend:** 3 customers increasing / 9 decreasing (mean drift: -2.4%)

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
| 2017 | 37,159 | 2,707 | 11,165 | 1,977 | 9,940 | 0 | 62,948 |  |
| 2018 | 65,510 | 9,875 | 17,434 | 9,350 | 17,284 | 0 | 119,453 |  |
| 2019 | 164,625 | 28,353 | 42,460 | 31,969 | 44,302 | 0 | 311,709 |  |
| 2020 | 238,636 | 35,391 | 69,454 | 56,550 | 70,024 | 0 | 470,055 |  |
| 2021 | 246,562 | 15,001 | 71,336 | 49,645 | 62,799 | 41,404 | 486,746 |  |
| 2022 | 255,973 | -49,692 | 70,920 | 36,644 | 69,047 | 99,384 | 482,276 | ⬇ CfD REBATE |
| 2023 | 271,626 | 64,711 | 71,702 | 50,920 | 75,035 | 13,739 | 547,732 |  |
| 2024 | 307,347 | 109,832 | 72,815 | 68,646 | 82,488 | 1,997 | 643,126 |  |
| 2025 | 135,564 | 46,893 | 31,156 | 30,992 | 36,108 | 853 | 281,565 |  |
| **Total** | **1,724,164** | **263,078** | **458,631** | **336,730** | **467,330** | **157,375** | **3,407,310** | |

Total policy cost: £3,407,310 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2020 | 124,585 |  |
| 2021 | 123,491 |  |
| 2022 | 132,911 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 138,838 | RIIO-ED2 from Apr 2023 |
| 2024 | 142,836 |  |
| 2025 | 61,009 |  |
| **Total** | **879,989** | |

Total network cost: £879,989 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

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
| 2017 | 2,497,718 | 10 | 249,772 | 1921.32× | OK |
| 2018 | 2,486,407 | 11 | 226,037 | 1738.75× | OK |
| 2019 | 2,606,406 | 12 | 217,201 | 1670.77× | OK |
| 2020 | 2,900,060 | 13 | 223,082 | 1716.01× | OK |
| 2021 | 2,921,243 | 12 | 243,437 | 1872.59× | OK |
| 2022 | 3,063,100 | 11 | 278,464 | 2142.03× | OK |
| 2023 | 3,166,003 | 10 | 316,600 | 2435.39× | OK |
| 2024 | 3,522,694 | 10 | 352,269 | 2709.76× | OK |
| 2025 | 3,572,608 | 8 | 446,576 | 3435.20× | OK |

End-state (2025): **£446,576/account** across 8 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,424 | 81947.0× | OK |
| 2017 | 466 | 559 | 2,497,718 | 4467.7× | OK |
| 2018 | 849 | 1,019 | 2,486,407 | 2439.7× | OK |
| 2019 | 1,543 | 1,851 | 2,606,406 | 1408.0× | OK |
| 2020 | 1,979 | 2,375 | 2,900,060 | 1221.2× | OK |
| 2021 | 4,340 | 5,208 | 2,921,243 | 560.9× | OK |
| 2022 | 8,500 | 10,200 | 3,063,100 | 300.3× | OK |
| 2023 | 5,605 | 6,726 | 3,166,003 | 470.7× | OK |
| 2024 | 2,654 | 3,184 | 3,522,694 | 1106.3× | OK |
| 2025 | 3,863 | 4,636 | 3,572,608 | 770.6× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,518.21 | £12,260.14 | £262.58/MWh | £144.94/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,981.92 | £9,699.69 | £272.64/MWh | £154.52/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,933.14 | £9,310.56 | £250.25/MWh | £141.72/MWh | +10.9% |

Total HH revenue: £63,703.66 vs flat equivalent £58,800.41 (+8.3% ToU premium)

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
| 2021 | 51 | 113% | C4g (2021-10-31) |
| 2022 | 63 | 1735% | C2_2 (2022-04-30) |
| 2023 | 44 | 101% | C_IC2 (2023-06-30) |
| 2024 | 33 | 107% | C_IC2 (2024-07-31) |
| 2025 | 20 | 80% | C7 (2025-06-07) |

Total: **471** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1735% | no |
| 2022-10-31 | C4g | +134% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2020-03-31 | C_IC2 | +118% | no |
| 2021-10-31 | C4g | +113% | no |
| 2022-01-31 | C_IC3 | +109% | no |
| 2024-07-31 | C_IC2 | +107% | no |
| 2023-06-30 | C_IC2 | +101% | no |
| 2016-10-31 | C8 | +100% | no |
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
| Total offer cost (foregone margin) | £418,601.16 |
| Margin saved (retained customers' terms) | £2,207,124.11 |
| Wasted offer cost (churned anyway) | £509.78 |
| **Net ROI of retention strategy** | **£1,788,522.94** |
| Acquisition cost avoided (retained customers) | £2,800.00 |
| **Full economic ROI (margin + acq savings)** | **£1,791,322.94** |

Missed opportunities (churns with no offer): **5** (£3,964.27 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 5 (£3,964.27 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24227.89 | £163704.65 | £139476.77 | £0.00 |
| 2019 | 2 | 2 | £42792.80 | £296612.44 | £253819.64 | £0.00 |
| 2020 | 3 | 3 | £26868.85 | £164454.03 | £137585.18 | £585.39 |
| 2021 | 4 | 3 | £120034.52 | £414261.42 | £294226.91 | £-178.13 |
| 2022 | 2 | 2 | £73492.71 | £327846.57 | £254353.86 | £236.63 |
| 2023 | 4 | 4 | £87194.87 | £437413.74 | £350218.88 | £0.00 |
| 2024 | 2 | 2 | £43989.54 | £402831.26 | £358841.72 | £3320.39 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24227.89 | £163704.65 | £150 | £139476.77 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £27950.99 | £194971.28 | £150 | £167020.29 | retained |
| 2020-01-01 | C_IC3 | 0.36 | 3% | £5716.80 | £10711.28 | £150 | £4994.49 | retained |
| 2020-03-31 | C_IC1 | 0.50 | 5% | £10372.10 | £130842.70 | £150 | £120470.60 | retained |
| 2020-12-31 | C_IC3 | 0.59 | 5% | £10779.96 | £22900.05 | £150 | £12120.09 | retained |
| 2021-03-31 | C_IC2 | 0.84 | 8% | £14161.08 | £91309.23 | £150 | £77148.15 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £22523.37 | £158242.30 | £150 | £135718.92 | retained |
| 2021-12-30 | C5 | 0.83 | 8% | £509.78 | £2240.09 | £400 | £-509.78 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £82840.28 | £164709.89 | £150 | £81869.61 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25114.25 | £96248.86 | £150 | £71134.61 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £48378.45 | £231597.71 | £150 | £183219.25 | retained |
| 2023-03-31 | C6 | 0.49 | 3% | £231.31 | £3283.32 | £400 | £3052.01 | retained |
| 2023-05-30 | C_IC2 | 0.57 | 5% | £11695.77 | £130517.32 | £150 | £118821.56 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £34706.84 | £243734.66 | £150 | £209027.82 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £40560.94 | £59878.43 | £150 | £19317.49 | retained |
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

**Full-history EV:** £5,987,457.53 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £431,985.54 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,178.25 |
| 2017 | £30,566.05 |
| 2018 | £99,706.17 |
| 2019 | £218,584.43 |
| 2020 | £116,793.60 |
| 2021 | £56,437.94 |
| 2022 | £250,445.09 |
| 2023 | £49,597.58 | ← trailing
| 2024 | £311,916.78 | ← trailing
| 2025 | £88,871.41 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £3,759.27 | — |
| C2 | £5,019.18 | — |
| C2_2 | — | £981.87 |
| C3 | £4,940.21 | — |
| C4 | £2,924.28 | £-863.54 |
| C5 | £8,453.38 | — |
| C6 | £15,138.01 | £2,562.09 |
| C7 | £6,696.56 | £24.25 |
| C8 | £7,260.36 | £239.86 |
| C9 | £7,562.19 | £940.52 |
| C_IC1 | £1,444,140.21 | £331,276.75 |
| C_IC2 | £778,267.90 | £175,255.41 |
| C_IC3 | £2,456,086.95 | £-86,666.44 |
| C_IC4 | £1,243,726.11 | £8,234.77 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £2,259.66 | — | — | — | — | £5,096.01 | — | £4,189.02 | — | — | — | — | — | — |
| 2017 | £1,925.07 | £3,735.54 | — | £3,583.27 | £3,312.27 | £4,557.02 | £8,406.57 | £3,198.78 | £4,626.02 | £3,986.99 | — | — | — | — |
| 2018 | £2,044.04 | £3,368.07 | — | £3,286.16 | £2,551.89 | £4,134.11 | £7,042.85 | £3,117.95 | £3,924.42 | £3,755.90 | £972,627.22 | — | — | — |
| 2019 | £2,031.50 | £2,978.41 | — | £3,309.63 | £2,817.78 | £4,447.40 | £7,510.18 | £3,271.14 | £3,896.97 | £3,808.08 | £874,243.40 | £530,697.39 | — | — |
| 2020 | £2,354.14 | £3,148.88 | — | £2,906.22 | £2,914.53 | £4,922.97 | £7,842.46 | £3,947.14 | £4,129.73 | £3,754.50 | £648,789.43 | £320,804.92 | £1,040,421.13 | £677,852.11 |
| 2021 | £2,149.64 | £3,536.80 | — | £2,901.03 | £2,578.89 | £4,780.39 | £8,995.04 | £3,181.99 | £4,279.93 | £3,528.75 | £580,671.90 | £354,532.18 | £1,044,066.96 | £631,507.87 |
| 2022 | £2,387.04 | £2,710.73 | £479.63 | £2,894.81 | £1,670.68 | £4,937.07 | £8,310.71 | £2,807.02 | £4,077.92 | £3,927.44 | £648,109.54 | £376,947.92 | £1,170,113.34 | £600,067.18 |
| 2023 | £2,389.40 | £2,712.76 | £1,340.70 | £2,893.77 | £1,294.30 | £4,935.31 | £9,125.78 | £3,004.37 | £4,160.02 | £4,209.14 | £701,311.66 | £405,486.51 | £1,091,531.75 | £620,865.00 |
| 2024 | £2,192.88 | £2,891.75 | £1,974.13 | £3,172.25 | £1,666.07 | £4,609.64 | £9,337.65 | £3,240.54 | £4,289.43 | £4,765.37 | £718,367.20 | £413,874.68 | £1,294,401.76 | £737,975.73 |
| 2025 | £2,181.08 | £2,877.51 | £2,075.52 | £2,949.79 | £1,670.89 | £4,766.31 | £8,845.25 | £3,571.38 | £4,141.06 | £4,530.09 | £765,463.26 | £443,514.58 | £1,398,678.85 | £787,854.32 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,769.41, range £58.35–£26,245.40.

- C1: cost to serve £414.44, net margin after CTS £2,319.83
- C1g: cost to serve £64.80, net margin after CTS £1,478.25
- C2: cost to serve £432.22, net margin after CTS £2,978.09
- C2_2: cost to serve £381.30, net margin after CTS £5,101.46
- C2g: cost to serve £83.87, net margin after CTS £1,935.34
- C3: cost to serve £292.52, net margin after CTS £2,096.31
- C3g: cost to serve £58.35, net margin after CTS £1,245.05
- C4: cost to serve £565.38, net margin after CTS £2,749.42
- C4g: cost to serve £216.69, net margin after CTS £1,132.91
- C5: cost to serve £871.77, net margin after CTS £8,505.31
- C6: cost to serve £1,349.60, net margin after CTS £21,146.93
- C7: cost to serve £954.70, net margin after CTS £9,846.82
- C8: cost to serve £939.06, net margin after CTS £11,522.73
- C9: cost to serve £896.59, net margin after CTS £11,811.59
- C_IC1: cost to serve £19,836.11, net margin after CTS £1,854,824.98
- C_IC2: cost to serve £11,344.38, net margin after CTS £898,455.14
- C_IC3: cost to serve £26,245.40, net margin after CTS £1,773,176.43
- C_IC3g: cost to serve £9,229.97, net margin after CTS £613,417.06
- C_IC4: cost to serve £16,441.72, net margin after CTS £1,090,243.56


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 29 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 14.0%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.31/MWh |
| C5 | electricity | 2018-12-31 | £-204.31 | £2,322.51 | +3.8% | £148.68/MWh | £153.39/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,283.71 | £6,187.80 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,215.97 | £10,069.00 | +20.0% | £128.22/MWh | £175.80/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,915.21 | £3,421.95 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £177.17/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.62/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £59.42/MWh |
| C5 | electricity | 2021-12-30 | £-339.41 | £2,699.34 | +7.6% | £311.83/MWh | £340.69/MWh |
| C7 | electricity | 2021-12-30 | £-122.68 | £1,986.24 | +1.2% | £311.83/MWh | £320.43/MWh |
| C_IC3 | electricity | 2021-12-31 | £-27,609.28 | £443,011.72 | +1.2% | £224.03/MWh | £260.80/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £317.95/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.66/MWh |
| C4 | electricity | 2022-09-30 | £-220.41 | £906.59 | +19.3% | £404.86/MWh | £484.82/MWh |
| C4g | gas | 2022-09-30 | £-901.21 | £1,040.11 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £318.54/MWh |
| C_IC3g | gas | 2022-12-31 | £-49,329.98 | £586,562.16 | +3.4% | £101.23/MWh | £120.39/MWh |
| C8 | electricity | 2023-03-31 | £-481.87 | £3,898.74 | +7.4% | £319.17/MWh | £346.40/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.59/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.46/MWh |
| C4 | electricity | 2023-09-30 | £-277.33 | £1,324.46 | +15.9% | £216.77/MWh | £249.30/MWh |
| C4g | gas | 2023-09-30 | £-1,950.48 | £2,732.11 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-445.92 | £3,990.91 | +6.2% | £242.22/MWh | £244.32/MWh |
| C_IC3 | electricity | 2023-12-31 | £-168,652.86 | £928,490.44 | +13.2% | £118.95/MWh | £127.88/MWh |
| C_IC3g | gas | 2023-12-31 | £-30,637.15 | £295,562.62 | +5.4% | £51.89/MWh | £61.13/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |
| C_IC3g | gas | 2024-12-30 | £-37,283.07 | £268,211.20 | +8.9% | £50.47/MWh | £61.82/MWh |



## Portfolio Intelligence Pack (Phase AH)

Board-level synthesis of CRM and flexibility intelligence derived from observable operational data.

### 1. Retention Intelligence

- **Retention offers made:** 18
- **Offer acceptance rate:** 94% (17 retained / 1 churned despite offer)
- **Estimated margin protected:** £2,207,124.11
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
| C6 | SME | HIGH | 38% | 25% | -24.9% [competitive] | £21,146.93 |
| C8 | resi | HIGH | 38% | 0% | -23.6% [competitive] | £11,522.73 |
| C9 | resi | HIGH | 38% | 0% | -14.3% | £11,811.59 |
| C2_2 | resi | HIGH | 38% | 4% | +14.2% [overpriced] | £5,101.46 |
| C5 | SME | HIGH | 35% | 83% | +63.8% [overpriced] | £8,505.31 |
| C7 | resi | HIGH | 35% | 0% | -14.3% | £9,846.82 |
| C1 | resi | HIGH | 32% | 4% | -12.0% | £2,319.83 |
| C3 | resi | HIGH | 32% | 0% | -39.0% [competitive] | £2,096.31 |
| C4 | resi | HIGH | 32% | 0% | -9.0% | £2,749.42 |
| C2 | resi | MEDIUM | 26% | 7% | +46.6% [overpriced] | £2,978.09 |
| C_IC3 | I&C | LOW | 8% | 95% | -54.9% [competitive] | £1,773,176.43 |
| C_IC1 | I&C | LOW | 5% | 95% | -0.1% | £1,854,824.98 |
| C_IC2 | I&C | LOW | 5% | 95% | +12.4% [overpriced] | £898,455.14 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 9 accounts
- MEDIUM (>=15%): 1 accounts
- LOW (<15%): 3 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £75,100.41
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
| C3 | resi | 2020-06-30 | 4.0yr | -4.3% | -39.0% | 32% | 0% | £2,096.31 |
| C1 | resi | 2021-12-30 | 6.0yr | +1.6% | -12.0% | 32% | 4% | £2,319.83 |
| C5 | SME | 2021-12-30 | 6.0yr | +1.6% | +63.8% | 35% | 83% | £8,505.31 |
| C2 | resi | 2022-03-31 | 6.0yr | +15.0% | +46.6% | 26% | 7% | £2,978.09 |
| C6 | SME | 2024-03-30 | 8.0yr | -0.9% | -24.9% | 38% | 25% | £21,146.93 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 32% | 0% | £2,749.42 |

**Root Cause Summary:**
- Total churned accounts: 6
- Lifetime margin lost: £39,795.90
- Average tenure at departure: 6.3 years
- Company blind misses (sim >=30%, co. est. <10%): 3 -- C3, C1, C4
- Company-warned churns (co. est. >=20%): 2 -- C5, C6
- Crisis-era churns (2021-22): 3 -- absolute crisis price level, not rate-change delta, was the driver
- Overpriced vs SVT at departure: 2 account(s) -- rate shock risk was observable but unactioned

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 5 accounts that churned without an offer? Calibrated from 18 actual offers (observed retention rate 94%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C3 | resi | 2020-06-30 | 0% | £585.39 | 5% | £29.27 | £523.60 | MISSED OPP. |
| C1 | resi | 2021-12-30 | 4% | £-178.13 | 5% | £0.00 | n/a | CORRECT PASS |
| C2 | resi | 2022-03-31 | 7% | £236.63 | 5% | £11.83 | £211.65 | MISSED OPP. |
| C6 | SME | 2024-03-30 | 25% | £2,851.51 | 8% | £228.12 | £2,464.98 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 0% | £468.87 | 5% | £23.44 | £419.38 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 5
- Correct no-offer (net-neg ETM): 1 (C1)
- Missed opportunities (positive ETM, below detection): 4
- Total term margin foregone: £4,142.40
- Total retention cost (counterfactual): £292.67
- Net counterfactual benefit: £3,619.61 (at 94% retention probability)
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
| 2021 | £5,208 | £4,340 | 0.30% |
| 2022 | £10,200 | £8,500 | 0.30% |
| 2023 | £6,726 | £5,605 | 0.26% |
| 2024 | £3,184 | £2,654 | 0.14% |
| 2025 | £4,636 | £3,863 | 0.48% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,200 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £524 | £91 | 11.3% |
| 2017 | 14 | £16,735 | £8,803 | £2,183 | 13.0% |
| 2018 | 15 | £29,022 | £17,502 | £6,647 | 22.9% |
| 2019 | 17 | £70,486 | £41,296 | £12,858 | 18.2% |
| 2020 | 18 | £67,965 | £43,989 | £6,489 | 9.5% |
| 2021 | 16 | £108,592 | £47,790 | £3,527 | 3.2% << |
| 2022 | 14 | £245,340 | £74,878 | £17,889 | 7.3% |
| 2023 | 12 | £212,441 | £75,952 | £4,133 | 1.9% << |
| 2024 | 12 | £184,114 | £106,607 | £25,993 | 14.1% |
| 2025 | 9 | £107,349 | £57,172 | £9,875 | 9.2% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £25,993 net/customer
**Worst year per customer:** 2016 at £91 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £423 | — | £423 |
| C1g | — | £645 | £645 |
| C2 | £690 | — | £690 |
| C2_2 | £1,054 | — | £1,054 |
| C2g | — | £802 | £802 |
| C3 | £206 | — | £206 |
| C3g | — | £288 | £288 |
| C4 | £139 | — | £139 |
| C4g | — | £-2,024 | £-2,024 * |
| C5 | £-35 | — | £-35 * |
| C6 | £3,624 | — | £3,624 |
| C7 | £-1,458 | — | £-1,458 * |
| C8 | £1,264 | — | £1,264 |
| C9 | £1,493 | — | £1,493 |
| C_IC1 | £828,205 | — | £828,205 |
| C_IC2 | £426,641 | — | £426,641 |
| C_IC3 | £82,059 | — | £82,059 |
| C_IC3g | — | £-134,500 | £-134,500 * |
| C_IC4 | £14,584 | — | £14,584 |
| **Total** | **£1,358,887** | **£-134,790** | **£1,224,097** |

Loss-making accounts: C_IC3g (£-134,500), C4g (£-2,024), C7 (£-1,458), C5 (£-35)
Gas loss-making: C_IC3g (£-134,500), C4g (£-2,024)
Gas portfolio net: £-134,790 (-11.0% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,034 | £10,920 | £-8,885 |
| 2017 | £30,081 | £112,495 | £-82,414 |
| 2018 | £109,583 | £246,455 | £-136,872 |
| 2019 | £243,311 | £825,240 | £-581,929 |
| 2020 | £73,572 | £938,631 | £-865,059 |
| 2021 | £137,855 | £348,709 | £-210,854 |
| 2022 | £102,419 | £1,084,841 | £-982,421 |
| 2023 | £357,113 | £1,149,979 | £-792,866 |
| 2024 | £168,075 | £545,490 | £-377,414 |
| 2025 | £55 | £338 | £-283 |
| **Total** | **£1,224,097** | **£5,263,099** | **£-4,039,001** |

Largest hedging cost: **2022** (£982,421 vs naked)
Smallest hedging cost: **2025** (£283 vs naked)
Conclusion: systematic forward hedging cost £4,039,001 over 10 years vs spot purchasing.

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
| 2022 | 0.790 R | 5.6% | 0.34% | 63 | 148 | RED ! |
| 2023 | 0.807 A | 4.9% | 0.17% | 44 | 144 | AMBER |
| 2024 | 0.812 A | 4.7% | 0.16% | 33 | 129 | AMBER |
| 2025 | 0.776 R | 5.9% | 0.24% | 20 | 54 | RED ! |

Worst clarity year: **2025** (0.776)
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
| 2017 | 2.69 | WATCH | £2,497,718 | £30,566 |
| 2018 | — | — | £2,486,407 | £99,706 |
| 2019 | — | — | £2,606,406 | £218,584 |
| 2020 | — | — | £2,900,060 | £116,794 |
| 2021 | — | — | £2,921,243 | £56,438 |
| 2022 | 2.70 | WATCH | £3,063,100 | £250,445 |
| 2023 | 2.73 | WATCH | £3,166,003 | £49,598 |
| 2024 | — | — | £3,522,694 | £311,917 |
| 2025 | — | — | £3,572,608 | £88,871 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,572,608)**
**Treasury growth: £2,467,424 → £3,572,608 (+£1,105,184)**

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
| C6 | 2024-03 | 24.8% | £2,852 | below threshold ⚑ |
| C4 | 2024-09 | 0.0% | £469 | below threshold |

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
| C_IC1 | 2018-01 | £24,228 | £163,705 | 6.8× | 8% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £27,951 | £194,971 | 7.0× | 8% | retained |
| C_IC3 | 2020-01 | £5,717 | £10,711 | 1.9× | 3% | retained |
| C_IC1 | 2020-03 | £10,372 | £130,843 | 12.6× | 5% | retained |
| C_IC3 | 2020-12 | £10,780 | £22,900 | 2.1× | 5% | retained |
| C_IC2 | 2021-03 | £14,161 | £91,309 | 6.4× | 8% | retained |
| C_IC1 | 2021-04 | £22,523 | £158,242 | 7.0× | 8% | retained |
| C5 | 2021-12 | £510 | £2,240 | 4.4× | 8% | churned_despite_offer |
| C_IC3 | 2021-12 | £82,840 | £164,710 | 2.0× | 8% | retained |
| C_IC2 | 2022-04 | £25,114 | £96,249 | 3.8× | 8% | retained |
| C_IC1 | 2022-05 | £48,378 | £231,598 | 4.8× | 8% | retained |
| C6 | 2023-03 | £231 | £3,283 | 14.2× | 3% | retained |
| C_IC2 | 2023-05 | £11,696 | £130,517 | 11.2× | 5% | retained |
| C_IC1 | 2023-06 | £34,707 | £243,735 | 7.0× | 8% | retained |
| C_IC3 | 2023-12 | £40,561 | £59,878 | 1.5× | 8% | retained |
| C_IC2 | 2024-06 | £10,231 | £133,341 | 13.0× | 5% | retained |
| C_IC1 | 2024-07 | £33,759 | £269,490 | 8.0× | 8% | retained |

**Total retention spend: £418,601** | **Total margin protected: £2,209,364**
**Portfolio retention ROI: 5.3×** | **Retained: 17/18**
**Best ROI intervention: C6 2023-03 (14.2×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | -£51,273 | — |
| Exit Gas (with churn risk) | £50,401 | +£101,675 |
| Reprice to Breakeven | £85,251 | +£136,524 |

**Loss-making gas accounts: C4, C_IC3**
**Board recommendation: REPRICE GAS**

> Gas drag reduces dual-fuel net margin. Repricing to breakeven is preferable to exit
> because exiting gas risks losing the electricity contract (cross-product churn).

## Portfolio Hedge Fraction Evolution

Average hedge fraction (0=fully naked, 1=fully hedged) per year.

| Year | Portfolio Avg | Min HF | Max HF | Naked Accounts | Covered Accts |
|------|--------------|--------|--------|---------------|--------------|
| 2016 | 88.9% | 85.0% | 92.2% | — | 13 |
| 2017 | 89.5% | 85.0% | 94.3% | — | 14 |
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
| 2022 | 9 | 62 | 6.9 | £20,569 |
| 2023 | 4 | 32 | 8.0 | £48,903 |

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
| 2020 | £2,375 | £56,550 | — | £69,454 | £47,215 |
| 2021 | £5,208 | £49,645 | £41,404 | £71,336 | £50,441 |
| 2022 | £10,200 | £36,644 | £99,384 | £70,920 | £54,433 |
| 2023 | £6,726 | £50,920 | £13,739 | £71,702 | £79,700 |
| 2024 | £3,184 | £68,646 | £1,997 | £72,815 | £76,429 |
| 2025 | £4,636 | £30,992 | £853 | £31,156 | £31,816 |

**Peak BSC credit obligation: 2022 (£10,200)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 14 | £167,222 | £91,391 | £7,108 | £11,944 |
| 2017 | 1 | £3,123,598 | £1,874,661 | £828,205 | £3,123,598 |
| 2018 | 1 | £1,525,240 | £909,800 | £426,641 | £1,525,240 |
| 2019 | 2 | £6,437,996 | £2,422,069 | -£52,441 | £3,218,998 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £14,584 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,218,998/customer)**
**Best net margin cohort: 2017 (£828,205)**
**Loss cohort: 2019 (net -£52,441)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £167 | — | 108 |
| 2017 | +£2,707 | £37,159 | £1,375 | — | 168 |
| 2018 | +£9,875 | £65,510 | £2,385 | — | 180 |
| 2019 | +£28,353 | £164,625 | £6,207 | — | 204 |
| 2020 | +£35,391 | £238,636 | £6,295 | — | 204 |
| 2021 | +£15,001 | £246,562 | £9,125 | — | 192 |
| 2022 | -£49,692 CREDIT | £255,973 | £35,596 | 1 | 148 |
| 2023 | +£64,711 | £271,626 | £13,894 | 1 | 144 |
| 2024 | +£109,832 | £307,347 | £11,514 | 1 | 129 |
| 2025 | +£46,893 | £135,564 | £4,945 | — | 54 |

**CfD turned CREDIT in 2022: -£49,692 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2022 (£35,596)**

> CfD (Contracts for Difference): when wholesale > strike price, generators repay;
> the net credit is passed through as a negative levy on supplier bills.

## Segment Gross Margin Attribution

Gross margin (£) by customer segment and year.

| Year | resi electricity | resi gas | SME electricity | I&C electricity | I&C gas | Total |
|------|----------|----------|----------|----------|----------|-------|
| 2016 | £3,270 | £811 | £2,733 | £0 | £0 | £6,814 |
| 2017 | £4,994 | £1,430 | £3,395 | £113,418 | £0 | £123,236 |
| 2018 | £5,063 | £1,363 | £3,206 | £252,900 | £0 | £262,531 |
| 2019 | £5,779 | £1,432 | £4,051 | £616,144 | £74,626 | £702,032 |
| 2020 | £5,681 | £1,218 | £4,236 | £704,698 | £75,972 | £791,805 |
| 2021 | £5,364 | £537 | £4,488 | £672,004 | £82,255 | £764,647 |
| 2022 | £3,756 | -£762 | £3,744 | £950,431 | £91,118 | £1,048,287 |
| 2023 | £7,219 | -£575 | £4,493 | £778,771 | £121,515 | £911,423 |
| 2024 | £8,561 | £762 | £1,528 | £1,144,783 | £123,652 | £1,279,285 |
| 2025 | £3,617 | £0 | £0 | £457,420 | £53,509 | £514,545 |

**Best gross margin year: 2024 (£1,279,285)** | **Worst: 2016 (£6,814)**
**Loss-making: resi gas in 2022 (£-762)**
**Loss-making: resi gas in 2023 (£-575)**


## Price Cap Headroom (Tariff vs SVT)

Percentage difference between contracted unit rate and SVT (price cap) at term start.
Negative = below cap (headroom). Positive = above cap (I&C terms; SVT applies to resi only).

| Year | Terms | Avg vs SVT% | Above Cap | Min% | Max% |
|------|-------|-------------|-----------|------|------|
| 2016 | 3 | -6.3% | 0/3 | -6.7% | +-5.8% |
| 2017 | 3 | -14.3% | 0/3 | -16.0% | +-12.4% |
| 2018 | 4 | -1.2% | 1/4 | -3.3% | +0.6% |
| 2019 | 4 | -18.8% | 1/4 | -29.5% | +12.4% |
| 2020 | 10 | -30.0% | 0/10 | -68.7% | +-18.0% |
| 2021 | 9 | +9.1% | 5/9 | -12.0% | +63.8% |
| 2022 | 7 | +11.5% | 4/7 | -66.2% | +95.6% |
| 2023 | 7 | -36.9% | 0/7 | -60.5% | +-10.8% |
| 2024 | 7 | -24.2% | 0/7 | -54.9% | +-9.0% |
| 2025 | 2 | -4.7% | 1/2 | -23.6% | +14.2% |

**Best headroom year: 2023 (avg 36.9% below SVT)**
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
| 2019 | £2,606,406 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,900,060 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,921,243 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,063,100 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,166,003 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,522,694 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,572,608 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 45.2% | £1,181 | £605 | 1.53% |
| 2017 | 14 | 33.5% | £24,902 | £8,914 | 1.80% |
| 2018 | 15 | 41.6% | £40,064 | £17,612 | 1.97% |
| 2019 | 17 | 40.2% | £96,792 | £41,405 | 1.87% |
| 2020 | 18 | 40.2% | £103,172 | £44,089 | 2.06% |
| 2021 | 16 | 29.0% | £151,218 | £47,890 | 1.95% |
| 2022 | 14 | 21.2% | £302,620 | £74,966 | 1.98% |
| 2023 | 12 | 23.0% | £285,586 | £76,038 | 2.21% |
| 2024 | 12 | 38.4% | £251,639 | £106,631 | 2.13% |
| 2025 | 9 | 36.7% | £135,916 | £57,214 | 2.99% |

**Best EBIT%: 2016 (45.2%)** | **Worst EBIT%: 2022 (21.2%)**
**Peak revenue/customer: 2022 (£302,620)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Churn Prediction Calibration

How well the company estimated churn probability versus actual simulation outcomes.

| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |
|----------|------|----------------|-----------------|-------|---------|
| C3 | 2020-06 | 32.0% | 0.0% | -32.0pp | UNDERESTIMATED |
| C1 | 2021-12 | 32.0% | 3.8% | -28.2pp | UNDERESTIMATED |
| C5 | 2021-12 | 35.0% | 82.7% | +47.7pp | OVERESTIMATED |
| C2 | 2022-03 | 26.0% | 6.7% | -19.3pp | UNDERESTIMATED |
| C6 | 2024-03 | 38.0% | 24.8% | -13.2pp | UNDERESTIMATED |
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
| 2017 | 13 | -1.1 | 1 | 12 | 0 |
| 2018 | 14 | +2.5 | 6 | 8 | 2 |
| 2019 | 15 | +1.5 | 5 | 10 | 2 |
| 2020 | 18 | +3.3 | 9 | 9 | 2 |
| 2021 | 14 | +11.3 | 14 | 0 | 6 |
| 2022 | 11 | +18.3 | 10 | 1 | 6 |
| 2023 | 11 | +10.1 | 8 | 3 | 8 |
| 2024 | 10 | +8.1 | 6 | 4 | 3 |
| 2025 | 2 | +1.0 | 1 | 1 | 0 |

**Total adjustments 2016-2025: 112** | **Peak avg adjustment: 2022 (+18.3 £/MWh)**
**Emergency reprices: 29 total** (8 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £11,545 | £3,848 | — |
| 2017 | 9 | £37,332 | £4,148 | +£25,787 |
| 2018 | 10 | £1,005,853 | £100,585 | +£968,521 |
| 2019 | 11 | £1,439,012 | £130,819 | +£433,159 |
| 2020 | 13 | £2,723,788 | £209,522 | +£1,284,776 |
| 2021 | 13 | £2,646,711 | £203,593 | £-77,077 |
| 2022 | 14 | £2,829,441 | £202,103 | +£182,730 |
| 2023 | 14 | £2,855,260 | £203,947 | +£25,819 |
| 2024 | 14 | £3,202,759 | £228,769 | +£347,499 |
| 2025 | 14 | £3,433,120 | £245,223 | +£230,361 |

**Peak portfolio CLV: 2025 (£3,433,120)** | **Earliest/lowest: 2016 (£11,545)**
**Largest YoY gain: 2020 (+£1,284,776)**
**Largest YoY fall: 2021 (£-77,077)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | 51.2% | — | — | — | — |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | 35.8% | +£333,275.90 | +£107,460.46 | +£108,889.99 | +£116,925.46 |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | 44.0% | +£252,322.49 | +£61,745.30 | +£51,194.57 | +£139,382.63 |
| 2019 | £1,645,456.22 | £496,239.95 | £445,337.04 | £703,879.23 | 42.8% | +£1,044,503.20 | +£323,437.66 | +£281,360.24 | +£439,705.30 |
| 2020 | £1,857,089.38 | £431,625.18 | £631,858.33 | £793,605.87 | 42.7% | +£211,633.16 | £-64,614.77 | +£186,521.29 | +£89,726.64 |
| 2021 | £2,419,482.99 | £972,979.22 | £680,256.12 | £766,247.65 | 31.7% | +£562,393.61 | +£541,354.04 | +£48,397.79 | £-27,358.21 |
| 2022 | £4,236,673.18 | £2,386,525.78 | £800,618.90 | £1,049,528.50 | 24.8% | +£1,817,190.19 | +£1,413,546.57 | +£120,362.78 | +£283,280.85 |
| 2023 | £3,427,027.52 | £1,638,114.16 | £876,453.05 | £912,460.31 | 26.6% | £-809,645.66 | £-748,411.62 | +£75,834.16 | £-137,068.20 |
| 2024 | £3,019,663.02 | £930,867.67 | £809,219.42 | £1,279,575.92 | 42.4% | £-407,364.50 | £-707,246.49 | £-67,233.63 | +£367,115.62 |
| 2025 | £1,223,240.97 | £451,597.53 | £256,714.50 | £514,928.94 | 42.1% | £-1,796,422.05 | £-479,270.14 | £-552,504.92 | £-764,646.98 |

**Best GM year: 2016 (51.2%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Risk Committee Activity (2016-2025)

Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.

| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |
|------|----------|----------------------|----------------------|-----------------|
| 2016 | 13 | £28 | £9 | 1 |
| 2017 | 12 | £1,005 | £401 | 3 |
| 2022 | 9 | £55,590 | £20,569 | 8 |
| 2023 | 4 | £128,316 | £48,903 | 9 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £128,316 | Unique accounts ever adjusted: 11

**Most frequently adjusted accounts:**
- C1: 22 sessions
- C7: 19 sessions
- C2: 13 sessions
- C5: 12 sessions
- C6: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £7,562.19 | Median churn: 32% | Total portfolio CLV: £5,983,974.61

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £2,456,086.95 | 8% | 10.1 periods |
| C_IC1 | £1,444,140.21 | 8% | 10.2 periods |
| C_IC4 | £1,243,726.11 | 14% | 8.9 periods |
| C_IC2 | £778,267.90 | 11% | 9.8 periods |

Quadrant CLV: £5,922,221.18 (99% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C6 | £15,138.01 | 38% | 8.9 periods |
| C5 | £8,453.38 | 35% | 9.5 periods |
| C9 | £7,562.19 | 38% | 9.0 periods |

Quadrant CLV: £31,153.58 (1% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C2 | £5,019.18 | 26% | 10.0 periods |

Quadrant CLV: £5,019.18 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £7,260.36 | 38% | 8.8 periods |
| C7 | £6,696.56 | 35% | 9.9 periods |
| C3 | £4,940.21 | 32% | 9.4 periods |
| C1 | £3,759.27 | 32% | 9.5 periods |
| C4 | £2,924.28 | 32% | 9.7 periods |

Quadrant CLV: £25,580.68 (0% of portfolio)

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
| 2024 | 0.812 | 0.047 | 2 | 0 |  |
| 2025 | 0.776 | 0.059 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.5% | **Average billing clarity:** 0.816 | **Average complaint probability:** 0.048

**Acquisition performance:** 5 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2025** (0.776) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

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
| 2021 | 15.9% | 51 | 192 | 27% |  |
| 2022 | 34.0% | 63 | 148 | 43% | **HIGH** |
| 2023 | 17.5% | 44 | 144 | 31% |  |
| 2024 | 16.2% | 33 | 129 | 26% |  |
| 2025 | 24.0% | 20 | 54 | 37% | ELEVATED |

**Crisis peak: 2022** — 34.0% average shock. Energy crisis drove wholesale costs above locked tariff rates,
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
| 2020 | £238,635.82 | £35,390.91 | £69,454.47 | £56,549.79 | £70,023.55 | £470,054.54 | £124,584.59 |
| 2021 | £246,562.17 | £15,001.31 | £71,335.52 | £49,644.73 | £62,798.79 | £486,746.12 | £123,490.94 |
| 2022 | £255,972.99 | **£-49,691.83** | £70,920.22 | £36,644.17 | £69,046.74 | £482,275.95 | £132,911.27 |
| 2023 | £271,625.80 | £64,710.57 | £71,701.96 | £50,920.49 | £75,034.67 | £547,732.04 | £138,838.08 |
| 2024 | £307,347.45 | £109,832.27 | £72,815.13 | £68,646.08 | £82,487.72 | £643,125.60 | £142,835.58 |
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
| 2017 | £30,102.71 | £463.34 | £231,632.96 | £2,660.42 | 1.1% | YES |
| 2018 | £99,331.51 | £374.66 | £432,208.83 | £3,113.94 | 0.7% | YES |
| 2019 | £218,118.22 | £466.22 | £1,060,498.38 | £137,770.25 | 11.5% | YES |
| 2020 | £112,361.98 | £4,431.62 | £1,102,239.07 | £121,133.74 | 9.9% | YES |
| 2021 | £58,440.21 | £-2,002.27 | £1,439,618.12 | £297,851.59 | 17.1% | **NO** |
| 2022 | £299,983.29 | £-49,538.20 | £2,846,424.77 | £588,329.77 | 17.1% | **NO** |
| 2023 | £81,909.06 | £-32,311.49 | £2,252,099.19 | £297,197.78 | 11.7% | **NO** |
| 2024 | £349,162.83 | £-37,246.05 | £1,938,873.21 | £270,490.62 | 12.2% | **NO** |
| 2025 | £108,595.83 | £-19,724.42 | £833,688.82 | £132,453.71 | 13.7% | **NO** |

**Gas has been loss-making since 2021** (5 consecutive years). Electricity cross-subsidises gas supply.

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £-51,273.40 | — | Current strategy |
| EXIT_GAS | £50,401.44 | £101,674.84 | Remove gas; model elec churn risk |
| REPRICE_GAS | £85,251.07 | £136,524.47 | Raise gas tariff to break-even |

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
| I&C electricity | £5,690,567.73 | £49,869.92 | £1,351,489.04 | 27.1x | Strong |
| I&C gas | £622,647.03 | £186,915.65 | £-134,500.12 | -0.7x | CAPITAL DESTROYER |
| SME electricity | £31,873.62 | £341.98 | £3,588.76 | 10.5x | Moderate |
| resi electricity | £53,302.47 | £570.16 | £3,809.56 | 6.7x | Moderate |
| resi gas | £6,215.25 | £200.69 | £-289.95 | -1.4x | CAPITAL DESTROYER |

**Gas Segment Finding:**
- Gas supply legs are net-negative over the simulation period (£-134,790.07 net on £187,116.34 capital)
- Electricity segments (£1,358,887.35 net) cross-subsidise gas retention
- Board decision required: is dual-fuel gas justified by CLV, or does it need pricing reform?

## Portfolio Concentration Risk

Revenue concentration analysis across 19 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2247** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,230,117.17 (98.7% of total positive margin)
- resi: £54,217.79 (0.9% of total positive margin)
- SME: £29,652.25 (0.5% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,854,824.98 | 29.4% | 5% | £92,741.25 |
| C_IC3 | I&C | £1,773,176.43 | 28.1% | 8% | £141,854.11 |
| C_IC4 | I&C | £1,090,243.56 | 17.3% | 0% | £0.00 |
| C_IC2 | I&C | £898,455.14 | 14.2% | 5% | £44,922.76 |
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
| C6 | electricity | 2017-04-01 | 9.7% | -0.8% | £127.97/MWh | £126.89/MWh |
| C8 | electricity | 2017-04-01 | 9.0% | -0.5% | £127.97/MWh | £127.35/MWh |
| C3 | electricity | 2017-07-01 | 10.4% | -1.2% | £122.23/MWh | £120.78/MWh |
| C3g | gas | 2017-07-01 | 20.5% | -5.0% | £24.33/MWh | £23.11/MWh |
| C9 | electricity | 2017-07-01 | 10.1% | -1.1% | £122.23/MWh | £120.94/MWh |
| C4 | electricity | 2017-10-01 | 11.1% | -1.6% | £111.62/MWh | £109.87/MWh |
| C4g | gas | 2017-10-01 | 18.4% | -5.0% | £27.48/MWh | £26.10/MWh |
| C1 | electricity | 2017-12-31 | 12.1% | -2.0% | £120.10/MWh | £117.65/MWh |
| C1g | gas | 2017-12-31 | 15.4% | -3.7% | £34.79/MWh | £33.49/MWh |
| C5 | electricity | 2017-12-31 | 9.0% | -0.5% | £120.10/MWh | £119.51/MWh |
| C7 | electricity | 2017-12-31 | 3.7% | +2.1% | £120.10/MWh | £122.67/MWh |
| C_IC1 | electricity | 2018-01-31 | -18.2% | +13.1% | £112.24/MWh | £126.93/MWh |
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
| C7 | electricity | 2018-12-31 | 9.6% | -0.8% | £148.68/MWh | £147.52/MWh |
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
| C6 | electricity | 2020-03-31 | -47.4% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -16.3% | +12.1% | £125.12/MWh | £140.31/MWh |
| C_IC1 | electricity | 2020-03-31 | 20.1% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 16.5% | -4.3% | £113.43/MWh | £108.60/MWh |
| C9 | electricity | 2020-06-30 | 16.5% | -4.3% | £113.43/MWh | £108.60/MWh |
| C4 | electricity | 2020-09-30 | 11.1% | -1.6% | £124.42/MWh | £122.47/MWh |
| C4g | gas | 2020-09-30 | 19.9% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 9.7% | -0.8% | £133.55/MWh | £132.43/MWh |
| C1g | gas | 2020-12-30 | 13.7% | -2.9% | £28.99/MWh | £28.16/MWh |
| C5 | electricity | 2020-12-30 | 4.6% | +1.7% | £133.55/MWh | £135.84/MWh |
| C7 | electricity | 2020-12-30 | -3.1% | +5.5% | £133.55/MWh | £140.94/MWh |
| C_IC3 | electricity | 2020-12-31 | -4.3% | +6.2% | £50.65/MWh | £53.77/MWh |
| C_IC3g | gas | 2020-12-31 | 6.7% | +0.7% | £20.05/MWh | £20.18/MWh |
| C2 | electricity | 2021-03-31 | -20.8% | +14.4% | £175.90/MWh | £201.25/MWh |
| C2g | gas | 2021-03-31 | 5.9% | +1.1% | £36.20/MWh | £36.58/MWh |
| C6 | electricity | 2021-03-31 | -16.1% | +12.1% | £175.90/MWh | £197.12/MWh |
| C8 | electricity | 2021-03-31 | -11.9% | +9.9% | £175.90/MWh | £193.39/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.6% | +6.3% | £138.90/MWh | £147.64/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.9% | +3.5% | £113.97/MWh | £118.02/MWh |
| C9 | electricity | 2021-06-30 | 1.1% | +3.5% | £170.38/MWh | £176.29/MWh |
| C4 | electricity | 2021-09-30 | -2.4% | +5.2% | £205.15/MWh | £215.85/MWh |
| C4g | gas | 2021-09-30 | 0.2% | +3.9% | £53.99/MWh | £56.09/MWh |
| C1 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.70/MWh |
| C5 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.70/MWh |
| C7 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.70/MWh |
| C_IC3 | electricity | 2021-12-31 | -22.8% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -18.7% | +13.4% | £109.48/MWh | £124.11/MWh |
| C2 | electricity | 2022-03-31 | -23.1% | +15.0% | £361.95/MWh | £416.24/MWh |
| C6 | electricity | 2022-03-31 | -16.8% | +12.4% | £361.95/MWh | £406.89/MWh |
| C8 | electricity | 2022-03-31 | 5.1% | +1.4% | £361.95/MWh | £367.17/MWh |
| C_IC2 | electricity | 2022-04-30 | -10.3% | +9.2% | £269.81/MWh | £294.54/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.9% | +7.4% | £239.42/MWh | £257.21/MWh |
| C9 | electricity | 2022-06-30 | 4.4% | +1.8% | £255.09/MWh | £259.70/MWh |
| C4 | electricity | 2022-09-30 | 7.3% | +0.4% | £404.86/MWh | £406.35/MWh |
| C4g | gas | 2022-09-30 | -22.1% | +15.0% | £183.79/MWh | £211.36/MWh |
| C7 | electricity | 2022-12-30 | 9.0% | -0.5% | £266.73/MWh | £265.45/MWh |
| C_IC3 | electricity | 2022-12-31 | -0.2% | +4.1% | £168.36/MWh | £175.28/MWh |
| C_IC3g | gas | 2022-12-31 | -40.1% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -12.4% | +10.2% | £319.17/MWh | £351.72/MWh |
| C6 | electricity | 2023-03-31 | -1.5% | +4.7% | £319.17/MWh | £334.31/MWh |
| C8 | electricity | 2023-03-31 | 5.8% | +1.1% | £319.17/MWh | £322.66/MWh |
| C_IC2 | electricity | 2023-05-30 | -22.0% | +15.0% | £171.46/MWh | £197.15/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.2% | +12.6% | £163.19/MWh | £183.72/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.09/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.03/MWh |
| C4g | gas | 2023-09-30 | -44.2% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 23.8% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -15.6% | +11.8% | £51.89/MWh | £58.02/MWh |
| C2_2 | electricity | 2024-03-30 | 16.3% | -4.2% | £207.71/MWh | £199.06/MWh |
| C6 | electricity | 2024-03-30 | 9.9% | -0.9% | £207.71/MWh | £205.74/MWh |
| C8 | electricity | 2024-03-30 | 9.9% | -0.9% | £207.71/MWh | £205.74/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.3% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.5% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C7 | electricity | 2024-12-29 | 0.4% | +3.8% | £243.79/MWh | £253.01/MWh |
| C_IC3 | electricity | 2024-12-30 | 18.5% | -5.0% | £116.37/MWh | £110.55/MWh |
| C_IC3g | gas | 2024-12-30 | -17.0% | +12.5% | £50.47/MWh | £56.77/MWh |
| C2_2 | electricity | 2025-03-30 | 8.7% | -0.4% | £284.89/MWh | £283.87/MWh |
| C8 | electricity | 2025-03-30 | 5.9% | +1.1% | £284.89/MWh | £287.94/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **5** | Blind misses: **5** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 4 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £3,964.27 | deliberate: £0.00 | total: £3,964.27

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.32 | Yes | £585.39 |
| C1 | 2021-12-30 | Blind miss | 0.04 | 0.32 | Yes | £-178.13 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.26 | No | £236.63 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.38 | Yes | £2,851.51 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.32 | Yes | £468.87 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C2+C2g | £689.87 | £801.77 | £1,491.64 | Yes |
| C1+C1g | £422.71 | £645.06 | £1,067.77 | Yes |
| C3+C3g | £205.99 | £287.57 | £493.56 | Yes |
| C4+C4g | £138.61 | £-2,024.35 | £-1,885.73 | No |
| C_IC3+C_IC3g | £82,059.49 | £-134,500.12 | £-52,440.63 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-134,790.07.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,224,097.28 across 19 billing accounts. Revenue: £13,998,695.39.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,123,598.47 | £1,874,661.09 | £18,414.21 | £828,204.75 | 26.5% |
| 2 | C_IC2 | fixed | £1,525,240.17 | £909,799.52 | £8,527.33 | £426,640.99 | 28.0% |
| 3 | C_IC3 | pass_through | £4,605,416.35 | £1,799,421.84 | £22,928.39 | £82,059.49 | 1.8% |
| 4 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £14,583.80 | 0.5% |
| 5 | C6 | fixed | £38,982.46 | £22,496.53 | £264.66 | £3,623.84 | 9.3% |
| 6 | C9 | fixed | £20,243.70 | £12,708.19 | £131.43 | £1,492.53 | 7.4% |
| 7 | C8 | fixed | £21,681.60 | £12,461.79 | £134.86 | £1,263.58 | 5.8% |
| 8 | C2_2 | fixed | £10,290.26 | £5,482.76 | £67.88 | £1,053.79 | 10.2% |
| 9 | C2g | fixed | £3,849.77 | £2,019.21 | £21.85 | £801.77 | 20.8% |
| 10 | C2 | fixed | £5,114.40 | £3,410.31 | £24.74 | £689.87 | 13.5% |
| 11 | C1g | fixed | £2,896.32 | £1,543.05 | £18.80 | £645.06 | 22.3% |
| 12 | C1 | fixed | £4,225.33 | £2,734.27 | £19.17 | £422.71 | 10.0% |
| 13 | C3g | fixed | £2,688.18 | £1,303.40 | £15.29 | £287.57 | 10.7% |
| 14 | C3 | fixed | £3,628.72 | £2,388.84 | £14.77 | £205.99 | 5.7% |
| 15 | C4 | fixed | £6,274.44 | £3,314.80 | £37.48 | £138.61 | 2.2% |
| 16 | C5 | fixed | £15,192.19 | £9,377.09 | £77.32 | £-35.08 | -0.2% |
| 17 | C7 | fixed | £21,778.35 | £10,801.52 | £139.83 | £-1,457.52 | -6.7% |
| 18 | C4g | fixed | £10,375.92 | £1,349.59 | £144.75 | £-2,024.35 | -19.5% |
| 19 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £186,915.65 | £-134,500.12 | -7.3% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £13,998,695 | 100.0% |
| Wholesale cost | -£7,594,089 | 54.2% |
| **Gross supply margin** | **£6,404,606** | **45.8%** |
| Policy + Network costs | -£4,942,610 | 35.3% |
| Capital cost | -£237,898 | 1.7% |
| **Net supply margin** | **£1,224,097** | **8.7%** |

> *The ledger's `net_margin_gbp` (£6,180,475) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £11,998,894 | 47.4% | 11.3% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | -7.3% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £54,175 | 58.8% | 6.6% | CMA 3-8% | ✓ |
| resi/elec | £82,947 | 57.7% | 3.3% | Ofgem CMA 2-5% | ✓ |
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
| Customer bills (all-in) | £19,743,837.48 |
|   Less: VAT remitted to HMRC | (£950,266.07) |
| = Revenue (ex-VAT) | £18,793,571.42 |
| Less: non-commodity pass-through | (£4,781,108.63) |
| Wholesale cost (settlement events) | (£7,594,089.30) |
| Gross margin | £6,418,373.49 |
| Capital charges | (£237,898.41) |
| Net margin | £6,180,475.08 |

_Cash reconciliation: of £19,743,837.48 billed, bad debt of £394,982.32 was written off, leaving £19,348,855.16 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £6,735,758.83._

| Acquisition spend | (£1,100.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £6,173,675.08 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | £234.62 | £834.62 | £6,944.88 (45.2%) |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | £6,260.72 | £6,860.72 | £116,657.37 (33.5%) |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | £11,823.00 | £12,423.00 | £250,222.87 (41.6%) |
| 2019 | £1,645,456.22 | £496,239.95 | £445,337.04 | £703,879.23 | £30,746.64 | £31,346.64 | £660,931.28 (40.2%) |
| 2020 | £1,857,089.38 | £431,625.18 | £631,858.33 | £793,605.87 | £38,269.79 | £39,019.79 | £747,191.23 (40.2%) |
| 2021 | £2,419,482.99 | £972,979.22 | £680,256.12 | £766,247.65 | £47,128.94 | £48,128.94 | £702,183.79 (29.0%) |
| 2022 | £4,236,673.18 | £2,386,525.78 | £800,618.90 | £1,049,528.50 | £84,086.07 | £84,686.07 | £899,262.36 (21.2%) |
| 2023 | £3,427,027.52 | £1,638,114.16 | £876,453.05 | £912,460.31 | £75,589.86 | £76,189.86 | £786,837.50 (23.0%) |
| 2024 | £3,019,663.02 | £930,867.67 | £809,219.42 | £1,279,575.92 | £64,318.62 | £65,468.62 | £1,158,136.85 (38.4%) |
| 2025 | £1,223,240.97 | £451,597.53 | £256,714.50 | £514,928.94 | £36,524.07 | £36,824.07 | £449,008.64 (36.7%) |
| **Total** | **£18,793,571.42** | | | | | | **£5,777,376.77 (30.7%)** |

**Best year:** 2024 — net £1,158,136.85 (38.4% margin)
**Worst year:** 2016 — net £6,944.88 (45.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,244,012.99 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,244,012.99** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,777,376.77 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,354.61 | +4.7% | £6,592.99 | £6,944.88 | +5.3% | AMBER |
| 2017 | £16,138.86 | £348,630.52 | +2060.2% | £7,252.29 | £116,657.37 | +1508.6% | RED |
| 2018 | £386,623.75 | £600,953.01 | +55.4% | £128,424.00 | £250,222.87 | +94.8% | RED |
| 2019 | £675,851.95 | £1,645,456.22 | +143.5% | £281,335.50 | £660,931.28 | +134.9% | RED |
| 2020 | £1,816,630.04 | £1,857,089.38 | +2.2% | £736,963.94 | £747,191.23 | +1.4% | GREEN |
| 2021 | £2,028,952.42 | £2,419,482.99 | +19.2% | £833,649.22 | £702,183.79 | -15.8% | RED |
| 2022 | £2,607,611.88 | £4,236,673.18 | +62.5% | £790,935.58 | £899,262.36 | +13.7% | AMBER |
| 2023 | £4,508,414.67 | £3,427,027.52 | -24.0% | £1,029,561.00 | £786,837.50 | -23.6% | RED |
| 2024 | £3,512,844.39 | £3,019,663.02 | -14.0% | £893,105.75 | £1,158,136.85 | +29.7% | RED |
| 2025 | £3,145,356.42 | £1,223,240.97 | -61.1% | £1,315,150.33 | £449,008.64 | -65.9% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,173,675.08

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

- Net margin: £30,566.05 (gross £123,236.40, capital £1,273.22)
  - Electricity: gross £121,806.83, capital £1,258.37, net £30,102.71
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
- Average CLV (Point-in-Time, year-end 2017): £4,147.95
  - By billing account: C1 £1,925.07, C2 £3,735.54, C3 £3,583.27, C4 £3,312.27, C5 £4,557.02, C6 £8,406.57, C7 £3,198.78, C8 £4,626.02, C9 £3,986.99
- Bill shock events (>=20%): 50 -- C1g 2017-01-31 (31%); C1g 2017-02-28 (28%); C1g 2017-05-31 (30%); C1g 2017-06-30 (30%); C1g 2017-09-30 (21%); C1g 2017-11-30 (70%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-05-31 (34%); C2g 2017-06-30 (29%); C2g 2017-09-30 (27%); C2g 2017-11-30 (66%); C2g 2017-12-31 (22%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-05-31 (30%); C3g 2017-06-30 (23%); C3g 2017-09-30 (21%); C3g 2017-11-30 (59%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (28%); C4 2017-09-30 (21%); C4 2017-10-31 (25%); C4 2017-11-30 (26%); C4g 2017-01-31 (23%); C4g 2017-02-28 (22%); C4g 2017-05-31 (33%); C4g 2017-06-30 (35%); C4g 2017-09-30 (36%); C4g 2017-10-31 (22%); C4g 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): 9 at risk (≥20% churn prob): C1 32%, C2 29%, C3 23%, C4 29%, C5 32%, C6 35%, C7 38%, C8 35%, C9 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.65-£131.86/MWh, net margin £120.11
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £106.38
- C2 (electricity): tariff £107.62-£125.75/MWh, net margin £75.15
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £181.68
- C3 (electricity): tariff £98.21-£120.78/MWh, net margin £71.13
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £57.45
- C4 (electricity): tariff £98.43-£109.87/MWh, net margin £46.13
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £117.83
- C5 (electricity): tariff £119.51-£131.01/MWh, net margin £164.74
- C6 (electricity): tariff £107.62-£126.89/MWh, net margin £68.67
- C7 (electricity): tariff £96.38-£195.85/MWh, net margin £159.34
- C8 (electricity): tariff £84.56-£191.02/MWh, net margin £214.39
- C9 (electricity): tariff £77.16-£181.41/MWh, net margin £135.66
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £29,047.38

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.818, average bill shock 16.5%, bad debt provision £1,375.34, avg complaint probability 4.7%
- Solvency signal: £249,772/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,080.50 vs. naked (unhedged) net margin: £112,495.31
- hedging cost £82,414.80 vs. a fully unhedged book (commodity-only: actual net £30,080.50 vs. naked net £112,495.31)
  - C1: actual £14.74 vs. naked £329.72 -- hedging cost £314.97
  - C1g: actual £131.41 vs. naked £272.27 -- hedging cost £140.86
  - C2: actual £74.11 vs. naked £438.14 -- hedging cost £364.04
  - C2g: actual £207.48 vs. naked £448.25 -- hedging cost £240.78
  - C3: actual £114.13 vs. naked £516.65 -- hedging cost £402.52
  - C3g: actual £30.62 vs. naked £394.35 -- hedging cost £363.73
  - C4: actual £40.58 vs. naked £274.45 -- hedging cost £233.87
  - C4g: actual £44.94 vs. naked £544.66 -- hedging cost £499.72
  - C5: actual £-204.31 vs. naked £1,067.62 -- hedging cost £1,271.94
  - C6: actual £119.34 vs. naked £1,690.80 -- hedging cost £1,571.46
  - C7: actual £-49.36 vs. naked £820.03 -- hedging cost £869.39
  - C8: actual £261.70 vs. naked £997.59 -- hedging cost £735.89
  - C9: actual £247.74 vs. naked £957.68 -- hedging cost £709.94
  - C_IC1: actual £29,047.38 vs. naked £103,743.08 -- hedging cost £74,695.71

**Year narrative:** 2017 produced a net gain of £30,566.05 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 50 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £99,706.17 (gross £262,531.43, capital £1,528.07)
  - Electricity: gross £261,168.63, capital £1,507.00, net £99,331.51
  - Gas: gross £1,362.80, capital £21.07, net £374.66
- Treasury at year end: £2,486,406.51
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
- Average CLV (Point-in-Time, year-end 2018): £100,585.26
  - By billing account: C1 £2,044.04, C2 £3,368.07, C3 £3,286.16, C4 £2,551.89, C5 £4,134.11, C6 £7,042.85, C7 £3,117.95, C8 £3,924.42, C9 £3,755.90, C_IC1 £972,627.22
- Bill shock events (>=20%): 60 -- C1g 2018-04-30 (37%); C1g 2018-05-31 (29%); C1g 2018-06-30 (30%); C1g 2018-09-30 (25%); C1g 2018-10-31 (46%); C1g 2018-11-30 (27%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (28%); C2g 2018-05-31 (34%); C2g 2018-06-30 (34%); C2g 2018-09-30 (33%); C2g 2018-10-31 (45%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (28%); C3g 2018-05-31 (32%); C3g 2018-06-30 (29%); C3g 2018-08-31 (34%); C3g 2018-09-30 (34%); C3g 2018-10-31 (35%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (28%); C4 2018-09-30 (23%); C4 2018-10-31 (41%); C4 2018-11-30 (28%); C4g 2018-04-30 (36%); C4g 2018-05-31 (33%); C4g 2018-06-30 (36%); C4g 2018-09-30 (39%); C4g 2018-10-31 (85%); C4g 2018-11-30 (24%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 9 at risk (≥20% churn prob): C1 38%, C2 32%, C3 32%, C4 38%, C5 35%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £117.65-£149.68/MWh, net margin £15.05
- C1g (gas): tariff £33.49-£36.05/MWh, net margin £131.41
- C2 (electricity): tariff £125.75-£143.89/MWh, net margin £68.53
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £174.16
- C3 (electricity): tariff £120.78-£126.90/MWh, net margin £71.12
- C3g (gas): tariff £23.11-£28.80/MWh, net margin £26.42
- C4 (electricity): tariff £109.87-£149.37/MWh, net margin £61.80
- C4g (gas): tariff £26.10-£33.61/MWh, net margin £42.67
- C5 (electricity): tariff £119.51-£153.39/MWh, net margin £-203.32 -- **net-negative**
- C6 (electricity): tariff £126.89-£142.17/MWh, net margin £-41.23 -- **net-negative**
- C7 (electricity): tariff £96.38-£221.28/MWh, net margin £-47.02 -- **net-negative**
- C8 (electricity): tariff £100.06-£200.68/MWh, net margin £128.59
- C9 (electricity): tariff £95.02-£198.38/MWh, net margin £206.61
- C_IC1 (electricity): tariff £-82.12-£228.47/MWh, net margin £105,764.22
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,692.84 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.810, average bill shock 16.0%, bad debt provision £2,384.75, avg complaint probability 4.7%
- Solvency signal: £226,037/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £109,582.74 vs. naked (unhedged) net margin: £246,455.41
- hedging cost £136,872.67 vs. a fully unhedged book (commodity-only: actual net £109,582.74 vs. naked net £246,455.41)
  - C1: actual £94.01 vs. naked £560.96 -- hedging cost £466.94
  - C1g: actual £144.33 vs. naked £420.62 -- hedging cost £276.29
  - C2: actual £62.60 vs. naked £499.23 -- hedging cost £436.64
  - C2g: actual £158.01 vs. naked £399.99 -- hedging cost £241.98
  - C3: actual £26.68 vs. naked £557.91 -- hedging cost £531.24
  - C3g: actual £38.90 vs. naked £481.52 -- hedging cost £442.62
  - C4: actual £104.22 vs. naked £464.67 -- hedging cost £360.45
  - C4g: actual £68.19 vs. naked £870.63 -- hedging cost £802.44
  - C5: actual £121.83 vs. naked £1,981.96 -- hedging cost £1,860.13
  - C6: actual £-141.45 vs. naked £1,833.69 -- hedging cost £1,975.14
  - C7: actual £71.87 vs. naked £1,347.87 -- hedging cost £1,276.01
  - C8: actual £24.32 vs. naked £936.62 -- hedging cost £912.30
  - C9: actual £143.75 vs. naked £1,046.07 -- hedging cost £902.32
  - C_IC1: actual £115,358.32 vs. naked £201,607.35 -- hedging cost £86,249.03
  - C_IC2: actual £-6,692.84 vs. naked £33,446.32 -- hedging cost £40,139.15

**Year narrative:** 2018 produced a net gain of £99,706.17 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 60 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £218,584.43 (gross £702,031.72, capital £11,601.31)
  - Electricity: gross £625,973.77, capital £2,287.85, net £218,118.22
  - Gas: gross £76,057.95, capital £9,313.46, net £466.22
- Treasury at year end: £2,606,406.14
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
- Average CLV (Point-in-Time, year-end 2019): £130,819.26
  - By billing account: C1 £2,031.50, C2 £2,978.41, C3 £3,309.63, C4 £2,817.78, C5 £4,447.40, C6 £7,510.18, C7 £3,271.14, C8 £3,896.97, C9 £3,808.08, C_IC1 £874,243.40, C_IC2 £530,697.39
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
- C5 (electricity): tariff £126.10-£153.39/MWh, net margin £121.02
- C6 (electricity): tariff £142.17-£148.72/MWh, net margin £92.86
- C7 (electricity): tariff £99.69-£221.28/MWh, net margin £71.68
- C8 (electricity): tariff £105.12-£211.40/MWh, net margin £154.84
- C9 (electricity): tariff £98.80-£198.38/MWh, net margin £145.35
- C_IC1 (electricity): tariff £0.00-£263.70/MWh, net margin £137,538.19
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £78,289.55
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £1,355.95
- C_IC3g (gas): tariff £27.53/MWh, net margin £34.62

**Portfolio Health**

- Capital cost ratio: 1.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.824, average bill shock 17.1%, bad debt provision £6,207.48, avg complaint probability 4.7%
- Solvency signal: £217,201/customer (12 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2019 produced a net gain of £218,584.43 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £116,793.60 (gross £791,805.27, capital £7,394.84)
  - Electricity: gross £714,614.63, capital £1,954.47, net £112,361.98
  - Gas: gross £77,190.65, capital £5,440.38, net £4,431.62
- Treasury at year end: £2,900,060.12
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
- Average CLV (Point-in-Time, year-end 2020): £209,522.17
  - By billing account: C1 £2,354.14, C2 £3,148.88, C3 £2,906.22, C4 £2,914.53, C5 £4,922.97, C6 £7,842.46, C7 £3,947.14, C8 £4,129.73, C9 £3,754.50, C_IC1 £648,789.43, C_IC2 £320,804.92, C_IC3 £1,040,421.13, C_IC4 £677,852.11
- Bill shock events (>=20%): 53 -- C1g 2020-01-31 (20%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-31 (35%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (22%); C4 2020-11-30 (24%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (48%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 10 at risk (≥20% churn prob): C1 29%, C2 32%, C3 32%, C4 32%, C5 35%, C6 32%, C7 35%, C8 38%, C9 41%, C_IC2 20%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£132.43/MWh, net margin £75.01
- C1g (gas): tariff £25.00-£25.52/MWh, net margin £139.56
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £182.92
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £133.50
- C3 (electricity): tariff £120.68/MWh, net margin £16.44
- C3g (gas): tariff £23.21/MWh, net margin £77.69
- C4 (electricity): tariff £122.47-£126.76/MWh, net margin £87.27
- C4g (gas): tariff £16.09-£19.63/MWh, net margin £75.56
- C5 (electricity): tariff £126.10-£135.84/MWh, net margin £-30.65 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.72/MWh, net margin £366.13
- C7 (electricity): tariff £99.69-£211.41/MWh, net margin £58.18
- C8 (electricity): tariff £110.24-£211.40/MWh, net margin £338.60
- C9 (electricity): tariff £85.33-£188.63/MWh, net margin £117.22
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £52,028.29
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £43,546.80
- C_IC3 (electricity): tariff £37.49-£80.66/MWh, net margin £11,005.48
- C_IC3g (gas): tariff £15.44-£20.18/MWh, net margin £4,005.30
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £4,570.28

**Portfolio Health**

- Capital cost ratio: 0.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.830, average bill shock 14.5%, bad debt provision £6,294.92, avg complaint probability 4.3%
- Solvency signal: £223,082/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £73,571.85 vs. naked (unhedged) net margin: £938,630.90
- hedging cost £865,059.05 vs. a fully unhedged book (commodity-only: actual net £73,571.85 vs. naked net £938,630.90)
  - C1: actual £-18.85 vs. naked £97.59 -- hedging cost £116.44
  - C1g: actual £22.28 vs. naked £-68.18 -- hedging added £90.47
  - C2: actual £175.35 vs. naked £570.69 -- hedging cost £395.33
  - C2g: actual £144.84 vs. naked £324.27 -- hedging cost £179.43
  - C4: actual £25.02 vs. naked £235.46 -- hedging cost £210.45
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C5: actual £-339.41 vs. naked £173.58 -- hedging cost £512.99
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-122.68 vs. naked £315.75 -- hedging cost £438.43
  - C8: actual £341.71 vs. naked £1,170.27 -- hedging cost £828.57
  - C9: actual £-18.70 vs. naked £697.66 -- hedging cost £716.35
  - C_IC1: actual £33,034.60 vs. naked £127,851.52 -- hedging cost £94,816.92
  - C_IC2: actual £42,303.73 vs. naked £95,603.52 -- hedging cost £53,299.79
  - C_IC3: actual £-16,452.24 vs. naked £220,540.02 -- hedging cost £236,992.27
  - C_IC3g: actual £6,308.59 vs. naked £147,619.15 -- hedging cost £141,310.56
  - C_IC4: actual £7,886.99 vs. naked £341,206.88 -- hedging cost £333,319.89

**Year narrative:** 2020 produced a net gain of £116,793.60 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £56,437.94 (gross £764,647.48, capital £15,934.92)
  - Electricity: gross £681,855.60, capital £5,609.79, net £58,440.21
  - Gas: gross £82,791.88, capital £10,325.14, net £-2,002.27
- Treasury at year end: £2,921,242.55
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
- Average CLV (Point-in-Time, year-end 2021): £203,593.18
  - By billing account: C1 £2,149.64, C2 £3,536.80, C3 £2,901.03, C4 £2,578.89, C5 £4,780.39, C6 £8,995.04, C7 £3,181.99, C8 £4,279.93, C9 £3,528.75, C_IC1 £580,671.90, C_IC2 £354,532.18, C_IC3 £1,044,066.96, C_IC4 £631,507.87
- Bill shock events (>=20%): 51 -- C1g 2021-05-31 (28%); C1g 2021-06-30 (45%); C1g 2021-10-31 (55%); C1g 2021-11-30 (53%); C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (21%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (23%); C4 2021-10-31 (48%); C4 2021-11-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%)
- Churn risk (accounts renewing in 2021): 12 at risk (≥20% churn prob): C1 32%, C2 32%, C4 35%, C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC3 20%, C_IC4 29%

**Pricing & Margin**

- C1 (electricity): tariff £132.43/MWh, net margin £-18.56 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £21.95
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £157.33
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £99.84
- C4 (electricity): tariff £122.47-£183.00/MWh, net margin £-59.19 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-334.91 -- **net-negative**
- C5 (electricity): tariff £135.84/MWh, net margin £-335.64 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.12/MWh, net margin £526.04
- C7 (electricity): tariff £110.74-£274.50/MWh, net margin £-132.28 -- **net-negative**
- C8 (electricity): tariff £110.24-£274.50/MWh, net margin £341.36
- C9 (electricity): tariff £85.33-£264.43/MWh, net margin £-13.51 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £26,737.23
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £55,499.76
- C_IC3 (electricity): tariff £42.25-£391.21/MWh, net margin £-27,586.98 -- **net-negative**
- C_IC3g (gas): tariff £20.18-£124.11/MWh, net margin £-1,789.15 -- **net-negative**
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £3,324.66

**Portfolio Health**

- Capital cost ratio: 2.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.829, average bill shock 15.9%, bad debt provision £9,124.70, avg complaint probability 4.5%
- Solvency signal: £243,437/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £137,855.31 vs. naked (unhedged) net margin: £348,709.35
- hedging cost £210,854.04 vs. a fully unhedged book (commodity-only: actual net £137,855.31 vs. naked net £348,709.35)
  - C2: actual £136.64 vs. naked £124.72 -- hedging added £11.92
  - C2g: actual £45.59 vs. naked £-190.70 -- hedging added £236.29
  - C4: actual £-220.41 vs. naked £-170.34 -- hedging cost £50.07
  - C4g: actual £-901.21 vs. naked £-1,344.38 -- hedging added £443.17
  - C6: actual £512.91 vs. naked £268.24 -- hedging added £244.67
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-48.55 vs. naked £-184.09 -- hedging added £135.55
  - C_IC1: actual £27,315.38 vs. naked £-61,910.67 -- hedging added £89,226.05
  - C_IC2: actual £63,558.59 vs. naked £21,603.54 -- hedging added £41,955.05
  - C_IC3: actual £100,234.37 vs. naked £234,716.59 -- hedging cost £134,482.23
  - C_IC3g: actual £-49,329.98 vs. naked £31,726.54 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £124,831.37 -- hedging cost £126,734.63

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £56,437.94 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 51 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £250,445.09 (gross £1,048,286.53, capital £65,580.08)
  - Electricity: gross £957,930.62, capital £13,175.07, net £299,983.29
  - Gas: gross £90,355.92, capital £52,405.01, net £-49,538.20
- Treasury at year end: £3,063,100.38
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,016,906.53, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,356.45 / stressed £20,517.58) ratio 2.70
  - 2022-05-29: treasury £3,017,026.88, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,466.25 / stressed £20,546.78) ratio 2.70
  - 2022-06-28: treasury £3,017,021.63, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,466.25 / stressed £20,546.78) ratio 2.70
  - 2022-07-28: treasury £3,016,829.01, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,527.66 / stressed £20,559.02) ratio 2.70
  - 2022-08-27: treasury £3,016,819.40, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,527.66 / stressed £20,559.02) ratio 2.70
  - 2022-09-26: treasury £3,016,803.96, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,527.66 / stressed £20,559.02) ratio 2.70
  - 2022-10-26: treasury £3,014,518.02, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,589.77 / stressed £20,569.49) ratio 2.70
  - 2022-11-25: treasury £3,014,367.61, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,589.77 / stressed £20,569.49) ratio 2.70
  - 2022-12-25: treasury £3,014,101.41, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,589.77 / stressed £20,569.49) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC3g on 2022-12-31 period 1, net margin £-2,998.80

**Customer Book**

- Active accounts: 14 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £202,102.93
  - By billing account: C1 £2,387.04, C2 £2,710.73, C2_2 £479.63, C3 £2,894.81, C4 £1,670.68, C5 £4,937.07, C6 £8,310.71, C7 £2,807.02, C8 £4,077.92, C9 £3,927.44, C_IC1 £648,109.54, C_IC2 £376,947.92, C_IC3 £1,170,113.34, C_IC4 £600,067.18
- Bill shock events (>=20%): 63 -- C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (57%); C_IC3 2022-01-31 (109%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 9 at risk (≥20% churn prob): C2 26%, C4 38%, C6 32%, C7 35%, C8 35%, C9 38%, C_IC1 20%, C_IC3 23%, C_IC4 32%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £13.07
- C2_2 (electricity): tariff £361.95/MWh, net margin £28.76
- C2g (gas): tariff £35.00/MWh, net margin £-17.33 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-276.94 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,284.53 -- **net-negative**
- C6 (electricity): tariff £197.12-£406.89/MWh, net margin £822.10
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,827.01 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-285.40 -- **net-negative**
- C9 (electricity): tariff £138.51-£389.54/MWh, net margin £-116.82 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£462.98/MWh, net margin £131,248.84
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £73,037.60
- C_IC3 (electricity): tariff £137.72-£391.21/MWh, net margin £99,247.02
- C_IC3g (gas): tariff £120.39-£124.11/MWh, net margin £-48,236.35 -- **net-negative**
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £-1,907.93 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 6.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,364,031.06 -> £3,014,070.49 (10.4%)
- Bills issued: 148, average clarity 0.790, average bill shock 34.0%, bad debt provision £35,595.76, avg complaint probability 5.6%
- Solvency signal: £278,464/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £102,419.18 vs. naked (unhedged) net margin: £1,084,840.98
- hedging cost £982,421.80 vs. a fully unhedged book (commodity-only: actual net £102,419.18 vs. naked net £1,084,840.98)
  - C2_2: actual £30.18 vs. naked £1,645.15 -- hedging cost £1,614.97
  - C4: actual £-277.33 vs. naked £595.36 -- hedging cost £872.70
  - C4g: actual £-1,950.48 vs. naked £1,336.80 -- hedging cost £3,287.28
  - C6: actual £1,128.51 vs. naked £3,996.58 -- hedging cost £2,868.07
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-481.87 vs. naked £1,102.92 -- hedging cost £1,584.78
  - C9: actual £-49.37 vs. naked £1,012.21 -- hedging cost £1,061.58
  - C_IC1: actual £212,769.51 vs. naked £251,051.40 -- hedging cost £38,281.89
  - C_IC2: actual £87,513.15 vs. naked £126,819.69 -- hedging cost £39,306.54
  - C_IC3: actual £-168,652.86 vs. naked £444,943.12 -- hedging cost £613,595.97
  - C_IC3g: actual £-30,637.15 vs. naked £84,150.32 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £165,905.73 -- hedging cost £162,432.92

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £250,445.09 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 63 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £49,597.58 (gross £911,423.25, capital £49,432.94)
  - Electricity: gross £790,483.14, capital £9,707.09, net £81,909.06
  - Gas: gross £120,940.11, capital £39,725.85, net £-32,311.49
- Treasury at year end: £3,166,003.48
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,063,100.04, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,282.66 / stressed £43,945.85) ratio 2.76
  - 2023-02-23: treasury £3,063,100.39, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,282.66 / stressed £43,945.85) ratio 2.76
  - 2023-03-25: treasury £3,063,100.69, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,282.66 / stressed £43,945.85) ratio 2.76
  - 2023-04-24: treasury £3,143,319.73, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,315.93 / stressed £48,902.82) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-12-31 period 1, net margin £-3,508.81

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £203,947.18
  - By billing account: C1 £2,389.40, C2 £2,712.76, C2_2 £1,340.70, C3 £2,893.77, C4 £1,294.30, C5 £4,935.31, C6 £9,125.78, C7 £3,004.37, C8 £4,160.02, C9 £4,209.14, C_IC1 £701,311.66, C_IC2 £405,486.51, C_IC3 £1,091,531.75, C_IC4 £620,865.00
- Bill shock events (>=20%): 44 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (31%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (25%); C4 2023-04-30 (29%); C4 2023-09-30 (24%); C4 2023-11-30 (27%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (46%); C4g 2023-11-30 (63%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (101%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%)
- Churn risk (accounts renewing in 2023): 8 at risk (≥20% churn prob): C2_2 38%, C4 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC3 20%, C_IC4 26%

**Pricing & Margin**

- C2_2 (electricity): tariff £351.72-£361.95/MWh, net margin £514.11
- C4 (electricity): tariff £249.30-£305.00/MWh, net margin £-68.72 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,164.32 -- **net-negative**
- C6 (electricity): tariff £334.31-£406.89/MWh, net margin £1,283.10
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-443.76 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-111.16 -- **net-negative**
- C9 (electricity): tariff £192.57-£389.54/MWh, net margin £226.01
- C_IC1 (electricity): tariff £-60.00-£462.98/MWh, net margin £159,951.77
- C_IC2 (electricity): tariff £-186.24-£476.93/MWh, net margin £84,669.81
- C_IC3 (electricity): tariff £100.47-£262.92/MWh, net margin £-167,592.34 -- **net-negative**
- C_IC3g (gas): tariff £61.13-£120.39/MWh, net margin £-31,147.16 -- **net-negative**
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £3,480.25

**Portfolio Health**

- Capital cost ratio: 5.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,552,686.03 -> £3,166,000.08 (10.9%)
- Bills issued: 144, average clarity 0.807, average bill shock 17.5%, bad debt provision £13,893.89, avg complaint probability 4.9%
- Solvency signal: £316,600/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £357,112.73 vs. naked (unhedged) net margin: £1,149,979.30
- hedging cost £792,866.57 vs. a fully unhedged book (commodity-only: actual net £357,112.73 vs. naked net £1,149,979.30)
  - C2_2: actual £845.16 vs. naked £2,437.92 -- hedging cost £1,592.76
  - C4: actual £313.87 vs. naked £700.05 -- hedging cost £386.18
  - C4g: actual £529.39 vs. naked £1,048.79 -- hedging cost £519.40
  - C6: actual £1,435.20 vs. naked £5,103.78 -- hedging cost £3,668.57
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £140.61 vs. naked £1,972.23 -- hedging cost £1,831.62
  - C9: actual £626.02 vs. naked £2,129.66 -- hedging cost £1,503.64
  - C_IC1: actual £141,580.35 vs. naked £284,454.19 -- hedging cost £142,873.84
  - C_IC2: actual £94,076.97 vs. naked £162,128.45 -- hedging cost £68,051.48
  - C_IC3: actual £150,662.88 vs. naked £424,666.48 -- hedging cost £274,003.60
  - C_IC3g: actual £-37,283.07 vs. naked £77,163.92 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £186,184.34 -- hedging cost £182,492.59

**Year narrative:** 2023 produced a net gain of £49,597.58 across 12 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 44 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £311,916.78 (gross £1,279,285.29, capital £55,970.45)
  - Electricity: gross £1,154,871.41, capital £9,619.17, net £349,162.83
  - Gas: gross £124,413.88, capital £46,351.29, net £-37,246.05
- Treasury at year end: £3,522,693.98
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
- Average CLV (Point-in-Time, year-end 2024): £228,768.50
  - By billing account: C1 £2,192.88, C2 £2,891.75, C2_2 £1,974.13, C3 £3,172.25, C4 £1,666.07, C5 £4,609.64, C6 £9,337.65, C7 £3,240.54, C8 £4,289.43, C9 £4,765.37, C_IC1 £718,367.20, C_IC2 £413,874.68, C_IC3 £1,294,401.76, C_IC4 £737,975.73
- Bill shock events (>=20%): 33 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (30%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (58%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (54%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C4 32%, C6 38%, C7 35%, C8 41%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.06-£351.72/MWh, net margin £422.93
- C4 (electricity): tariff £249.30/MWh, net margin £235.12
- C4g (gas): tariff £66.00/MWh, net margin £396.91
- C6 (electricity): tariff £334.31/MWh, net margin £500.05
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £492.80
- C8 (electricity): tariff £161.65-£397.50/MWh, net margin £288.67
- C9 (electricity): tariff £165.00-£367.64/MWh, net margin £560.37
- C_IC1 (electricity): tariff £-98.58-£330.69/MWh, net margin £123,483.01
- C_IC2 (electricity): tariff £-106.92-£354.88/MWh, net margin £68,774.23
- C_IC3 (electricity): tariff £86.86-£191.81/MWh, net margin £150,706.52
- C_IC3g (gas): tariff £61.13-£61.82/MWh, net margin £-37,642.96 -- **net-negative**
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £3,699.12

**Portfolio Health**

- Capital cost ratio: 4.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,552,597.66 -> £3,166,003.52 (10.9%)
- Bills issued: 129, average clarity 0.812, average bill shock 16.2%, bad debt provision £11,513.76, avg complaint probability 4.7%
- Solvency signal: £352,269/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £168,075.41 vs. naked (unhedged) net margin: £545,489.85
- hedging cost £377,414.44 vs. a fully unhedged book (commodity-only: actual net £168,075.41 vs. naked net £545,489.85)
  - C2_2: actual £93.80 vs. naked £1,031.75 -- hedging cost £937.95
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £305.86 vs. naked £1,419.45 -- hedging cost £1,113.59
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £14,911.38 vs. naked £115,656.21 -- hedging cost £100,744.82
  - C_IC3g: actual £-23,593.14 vs. naked £29,503.44 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £75,291.91 -- hedging cost £73,856.39

**Year narrative:** 2024 produced a net gain of £311,916.78 across 12 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £88,871.41 (gross £514,545.00, capital £29,096.24)
  - Electricity: gross £461,036.22, capital £5,584.29, net £108,595.83
  - Gas: gross £53,508.78, capital £23,511.94, net £-19,724.42
- Treasury at year end: £3,572,608.11
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
- Average CLV (Point-in-Time, year-end 2025): £245,222.85
  - By billing account: C1 £2,181.08, C2 £2,877.51, C2_2 £2,075.52, C3 £2,949.79, C4 £1,670.89, C5 £4,766.31, C6 £8,845.25, C7 £3,571.38, C8 £4,141.06, C9 £4,530.09, C_IC1 £765,463.26, C_IC2 £443,514.58, C_IC3 £1,398,678.85, C_IC4 £787,854.32
- Bill shock events (>=20%): 20 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (34%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.06-£283.87/MWh, net margin £88.00
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-23.72 -- **net-negative**
- C8 (electricity): tariff £149.29-£308.61/MWh, net margin £72.90
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £195.49
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £62,405.83
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,516.09
- C_IC3 (electricity): tariff £86.86-£165.83/MWh, net margin £14,923.83
- C_IC3g (gas): tariff £61.82/MWh, net margin £-19,724.42 -- **net-negative**
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £1,417.43

**Portfolio Health**

- Capital cost ratio: 5.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 54, average clarity 0.776, average bill shock 24.0%, bad debt provision £4,944.73, avg complaint probability 5.9%
- Solvency signal: £446,576/customer (8 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £54.56 vs. naked (unhedged) net margin: £337.86
- hedging cost £283.30 vs. a fully unhedged book (commodity-only: actual net £54.56 vs. naked net £337.86)
  - C2_2: actual £84.65 vs. naked £218.97 -- hedging cost £134.32
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £88,871.41 across 9 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 20 customer(s) experienced a bill shock of >=20%.
