# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,927,889.71
  (£1,461,253.49 net change)
- Solvency signal (final year): £540,345/customer (7 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £19,781,497.50
  VAT remitted to HMRC: (£952,156.45) | Revenue (ex-VAT): £18,829,341.04
  Non-commodity pass-through: (£4,777,693.84)
- Gross margin: £6,462,528.09
- Capital costs: £51,123.12
- Net margin: £6,411,404.97
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.1%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1443, average clarity 0.818,
  service quality score 0.906
- Enterprise value (CLV sum across 13 billing accounts): £5,637,800.63
- Cost to serve (whole portfolio): £90,330.75, net margin after cost to serve: £6,321,074.21
- Hedge effectiveness (whole window): hedging cost £4,217,631.99 vs. a fully unhedged book (commodity-only: actual net £1,461,253.49 vs. naked net £5,678,885.48)

- **2021** (crisis year): net margin £87,129.50, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £303,662.24, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2256, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 267.4x (net £51,922.50 on £194.14 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 4/6 departures (67%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 3.5%, max 15.6% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +33.1% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 34.1% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,462,528.09, capital £51,123.12, net £6,411,404.97. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £87,129.50 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.1%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,411,404.97
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,678,885.48
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,217,631.99 vs. a fully unhedged book (commodity-only: actual net £1,461,253.49 vs. naked net £5,678,885.48)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,546.73 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £613,596.32 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £254.88 | £626.84 | £296.53 | £1,178.25 |
| 2017 | £29,047.38 | £0.00 | £233.41 | £821.92 | £463.34 | £30,566.05 |
| 2018 | £99,071.38 | £0.00 | £-244.55 | £504.67 | £374.66 | £99,706.17 |
| 2019 | £217,183.69 | £9,326.63 | £213.88 | £720.65 | £427.56 | £227,872.41 |
| 2020 | £142,198.64 | £9,435.16 | £335.22 | £753.59 | £309.78 | £153,032.39 |
| 2021 | £78,579.41 | £8,520.22 | £223.65 | £119.18 | £-312.96 | £87,129.50 |
| 2022 | £302,335.33 | £4,134.82 | £987.68 | £-2,511.06 | £-1,284.53 | £303,662.24 |
| 2023 | £79,711.08 | £8,526.27 | £1,615.51 | £-396.88 | £-1,164.32 | £88,291.65 |
| 2024 | £346,306.18 | £8,684.92 | £632.92 | £1,530.23 | £396.91 | £357,551.17 |
| 2025 | £108,263.17 | £3,787.52 | £0.00 | £212.98 | £0.00 | £112,263.68 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **45** renewals.  Lost (churned): **6** accounts.

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
| C2 | 2020-03-31 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.5941 |
| C6 | 2021-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.5838 |
| C6 | 2022-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8723 |
| C6 | 2023-03-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.7019 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.3751 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 232.0%
- **Average signed error:** +107.7% (over-estimates vs SIM)
- **Renewal events with estimates:** 51

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -82.1% | 82.1% |
| 2017 | 3 | -93.7% | 93.7% |
| 2018 | 4 | +450.1% | 515.7% |
| 2019 | 4 | +380.7% | 519.3% |
| 2020 | 10 | +168.8% | 281.8% |
| 2021 | 8 | +31.5% | 140.7% |
| 2022 | 6 | -14.6% | 118.9% |
| 2023 | 6 | +9.2% | 142.5% |
| 2024 | 6 | +147.8% | 258.6% |
| 2025 | 1 | -100.0% | 100.0% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 51
- **Active renewers:** 16 (31%) — mean company estimate 71.9%, abs error 400.0%
- **Passive SVT-rollers:** 35 (69%) — mean company estimate 10.6%, abs error 155.2%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.2% | 0.0% | 82.1% |
| 2017 | 0 | 3 | 0.0% | 2.1% | 0.0% | 93.7% |
| 2018 | 2 | 2 | 57.9% | 49.9% | 88.4% | 943.1% |
| 2019 | 2 | 2 | 51.5% | 0.0% | 938.6% | 100.0% |
| 2020 | 5 | 5 | 77.6% | 0.5% | 465.1% | 98.6% |
| 2021 | 3 | 5 | 91.6% | 4.4% | 229.6% | 87.3% |
| 2022 | 0 | 6 | 0.0% | 21.6% | 0.0% | 118.9% |
| 2023 | 1 | 5 | 52.3% | 19.0% | 80.2% | 155.0% |
| 2024 | 3 | 3 | 71.9% | 0.0% | 417.3% | 100.0% |
| 2025 | 0 | 1 | 0.0% | 0.0% | 0.0% | 100.0% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 35
- **Above SVT (at-risk):** 6 (17%)
- **Below/at SVT (protected):** 29 (83%)
- **Mean rate vs SVT premium:** -12.4%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.1 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 119.9 | 140.0 |
| 2018 | 2 | 1 (50%) | +0.2% | 152.9 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -26.4% | 130.0 | 176.9 |
| 2021 | 5 | 2 (40%) | +0.1% | 185.1 | 186.2 |
| 2022 | 6 | 3 (50%) | +6.4% | 294.4 | 336.8 |
| 2023 | 5 | 0 (0%) | -32.1% | 226.3 | 364.0 |
| 2024 | 3 | 0 (0%) | -12.5% | 207.8 | 237.9 |
| 2025 | 1 | 0 (0%) | -23.6% | 190.0 | 248.6 |

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
| 2020 | 21 | 11.8% | 33.8% |
| 2021 | 15 | 11.8% | 44.5% |
| 2022 | 13 | 10.5% | 23.2% |
| 2023 | 13 | 19.4% | 40.0% |
| 2024 | 12 | 9.7% | 22.6% |
| 2025 | 1 | 33.1% | 33.1% |

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
| 2018 | 4 | 5.16× ⚠ | 18.00× |
| 2019 | 4 | 5.19× ⚠ | 18.00× |
| 2020 | 10 | 2.82× ⚠ | 18.00× |
| 2021 | 8 | 1.41× | 3.75× |
| 2022 | 6 | 1.19× | 3.13× |
| 2023 | 6 | 1.43× | 3.75× |
| 2024 | 6 | 2.59× ⚠ | 10.88× |
| 2025 | 1 | 1.00× | 1.00× |

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
| 2021 | 10 | 1.19% | 4.24% | MODERATE — asset adoption visible |
| 2022 | 8 | 2.34% | 7.47% | MODERATE — asset adoption visible |
| 2023 | 8 | 2.92% | 8.47% | HIGH drift — EV/asset cohort growing |
| 2024 | 8 | 3.54% | 15.56% | HIGH drift — EV/asset cohort growing |
| 2025 | 1 | 0.77% | 0.77% | Low — stable portfolio |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **3.54%** mean / **15.56%** max in 2024. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
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
| 2021 | 10 | 1.2% | 4.2% |
| 2022 | 8 | 2.3% | 7.5% |
| 2023 | 8 | 2.9% | 8.5% |
| 2024 | 8 | 3.5% | 15.6% |
| 2025 | 1 | 0.8% | 0.8% |

**81** of **81** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## EAC Drift Snapshot (Phase AI)

Per-customer consumption drift from company billing history (first renewal → latest renewal).
Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.

**1 significant** (≥15%) | **1 moderate** (5–15%) | **10 stable** (<5%)

| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |
|----------|-------------|-------------|-------|--------------|
| C4 | 4,131 | 3,365 | -19% | likely solar installation or significant efficiency upgrade |
| C7 | 13,179 | 12,155 | -8% | efficiency improvement or reduced occupancy |

**Portfolio demand trend:** 3 customers increasing / 9 decreasing (mean drift: -2.7%)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **6** (6 churn, 0 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-03-31 | CHURN | C2 | SIM p=0.32, company est=0.00 |
| 2020-06-30 | CHURN | C3 | SIM p=0.32, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.32, company est=0.04 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.85 |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.26 |
| 2024-09-29 | CHURN | C4 | SIM p=0.32, company est=0.00 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 2 accounts | 0 active | yes |
| 2021-12-31 | 4 accounts | 0 active | yes |
| 2022-12-31 | 4 accounts | 0 active | yes |
| 2023-12-31 | 4 accounts | 0 active | yes |
| 2024-12-31 | 6 accounts | 0 active | yes |
| 2025-12-31 | 6 accounts | 0 active | yes |

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
| 2020 | 238,546 | 35,378 | 69,454 | 56,528 | 69,997 | 0 | 469,903 |  |
| 2021 | 246,433 | 14,993 | 71,336 | 49,618 | 62,765 | 41,382 | 486,527 |  |
| 2022 | 255,773 | -49,653 | 70,920 | 36,616 | 68,993 | 99,306 | 481,955 | ⬇ CfD REBATE |
| 2023 | 271,353 | 64,645 | 71,702 | 50,872 | 74,959 | 13,725 | 547,255 |  |
| 2024 | 307,042 | 109,721 | 72,815 | 68,579 | 82,405 | 1,995 | 642,557 |  |
| 2025 | 135,390 | 46,833 | 31,156 | 30,952 | 36,061 | 852 | 281,245 |  |
| **Total** | **1,722,993** | **262,859** | **458,631** | **336,498** | **467,012** | **157,259** | **3,405,252** | |

Total policy cost: £3,405,252 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2020 | 124,410 |  |
| 2021 | 123,233 |  |
| 2022 | 132,400 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 138,080 | RIIO-ED2 from Apr 2023 |
| 2024 | 142,137 |  |
| 2025 | 60,632 |  |
| **Total** | **877,213** | |

Total network cost: £877,213 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

## Gas Policy Costs and Network Charges (Phase 30b)

Gas CCL: non-domestic only (domestic gas exempt). Gas network (GDN + NTS): all on unit rate.
GGL (Green Gas Levy): per-meter, from Nov 2021; tiny in £/MWh terms.

| Year | Gas Policy (CCL + GGL) £ | Gas Network £ | Total Gas Non-Commodity £ |
|------|--------------------------|---------------|--------------------------|
| 2016 | 0 | 479 | 479 |
| 2017 | 0 | 898 | 898 |
| 2018 | 0 | 905 | 905 |
| 2019 | 15,155 | 50,388 | 65,543 |
| 2020 | 19,468 | 47,112 | 66,580 |
| 2021 | 22,472 | 50,256 | 72,728 |
| 2022 | 27,044 | 54,366 | 81,410 |
| 2023 | 32,229 | 79,700 | 111,929 |
| 2024 | 37,494 | 76,429 | 113,923 |
| 2025 | 17,243 | 31,816 | 49,059 |
| **Total** | **171,105** | **392,349** | **563,454** |

Gas policy pass-through in tariff unit rate (CCL + GGL at term start); gas network pass-through likewise. Net basis risk near-zero for annual contracts.


## Gas Book P&L — Year by Year (Phase 32a)

Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.
Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.

| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |
|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|
| 2016 | 1,388 | 578 | 811 | 0 | 479 | 7 | 297 | +21.4% |
| 2017 | 2,660 | 1,231 | 1,430 | 0 | 898 | 15 | 463 | +17.4% |
| 2018 | 3,114 | 1,751 | 1,363 | 0 | 905 | 21 | 375 | +12.0% |
| 2019 | 137,766 | 61,712 | 76,054 | 15,155 | 50,388 | 21 | 9,754 | +7.1% |
| 2020 | 120,808 | 43,845 | 76,963 | 19,468 | 47,112 | 9 | 9,745 | +8.1% |
| 2021 | 297,195 | 214,718 | 82,477 | 22,472 | 50,256 | 12 | 8,207 | +2.8% |
| 2022 | 588,077 | 497,793 | 90,284 | 27,044 | 54,366 | 33 | 2,850 | +0.5% |
| 2023 | 297,198 | 176,258 | 120,940 | 32,229 | 79,700 | 52 | 7,362 | +2.5% |
| 2024 | 270,491 | 146,077 | 124,414 | 37,494 | 76,429 | 23 | 9,082 | +3.4% |
| 2025 | 132,454 | 78,945 | 53,509 | 17,243 | 31,816 | 0 | 3,788 | +2.9% |
| **Total** | **1,851,150** | **1,222,906** | **628,244** | **171,105** | **392,349** | **194** | **51,923** | **+2.8%** |

Gas book net margin positive over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,424 | 9 | 274,158 | 2108.91× | OK |
| 2017 | 2,497,718 | 10 | 249,772 | 1921.32× | OK |
| 2018 | 2,486,407 | 11 | 226,037 | 1738.75× | OK |
| 2019 | 2,606,406 | 12 | 217,201 | 1670.77× | OK |
| 2020 | 2,914,253 | 13 | 224,173 | 1724.41× | OK |
| 2021 | 2,983,493 | 11 | 271,227 | 2086.36× | OK |
| 2022 | 3,190,740 | 9 | 354,527 | 2727.13× | OK |
| 2023 | 3,332,123 | 9 | 370,236 | 2847.97× | OK |
| 2024 | 3,732,742 | 9 | 414,749 | 3190.38× | OK |
| 2025 | 3,782,418 | 7 | 540,345 | 4156.50× | OK |

End-state (2025): **£540,345/account** across 7 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,424 | 81947.0× | OK |
| 2017 | 466 | 559 | 2,497,718 | 4467.7× | OK |
| 2018 | 849 | 1,019 | 2,486,407 | 2439.7× | OK |
| 2019 | 1,543 | 1,851 | 2,606,406 | 1408.0× | OK |
| 2020 | 1,979 | 2,375 | 2,914,253 | 1227.2× | OK |
| 2021 | 4,362 | 5,235 | 2,983,493 | 569.9× | OK |
| 2022 | 8,498 | 10,197 | 3,190,740 | 312.9× | OK |
| 2023 | 5,592 | 6,710 | 3,332,123 | 496.6× | OK |
| 2024 | 2,644 | 3,173 | 3,732,742 | 1176.5× | OK |
| 2025 | 3,853 | 4,623 | 3,782,418 | 818.1× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,522.54 | £12,265.37 | £262.70/MWh | £145.00/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,960.48 | £9,683.66 | £272.15/MWh | £154.26/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,921.68 | £9,301.42 | £249.99/MWh | £141.58/MWh | +10.9% |

Total HH revenue: £63,655.15 vs flat equivalent £58,756.25 (+8.3% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 31 | 100% | C8 (2016-10-31) |
| 2017 | 50 | 81% | C8 (2017-11-30) |
| 2018 | 60 | 85% | C4g (2018-10-31) |
| 2019 | 66 | 130% | C_IC1 (2019-03-31) |
| 2020 | 47 | 118% | C_IC2 (2020-03-31) |
| 2021 | 47 | 113% | C4g (2021-10-31) |
| 2022 | 56 | 134% | C4g (2022-10-31) |
| 2023 | 39 | 100% | C_IC2 (2023-06-30) |
| 2024 | 26 | 107% | C_IC2 (2024-07-31) |
| 2025 | 16 | 80% | C7 (2025-06-07) |

Total: **438** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-10-31 | C4g | +134% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2020-03-31 | C_IC2 | +118% | no |
| 2021-10-31 | C4g | +113% | no |
| 2022-01-31 | C_IC3 | +108% | no |
| 2024-07-31 | C_IC2 | +107% | no |
| 2016-10-31 | C8 | +100% | no |
| 2023-06-30 | C_IC2 | +100% | no |
| 2021-04-30 | C_IC2 | +93% | no |
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
| 2020 | 4 | 6% | 24% | 1 ⚠ |
| 2021 | 2 | 84% | 95% | 2 ⚠ |
| 2022 | 2 | 48% | 95% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 1 | 1% | 1% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £20.0 | £125.9 (+530%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £16.1 | £35.0 (+118%) | 74% |
| 2020-12-31 | C_IC3g | £15.4 | £20.0 (+29%) | 24% |
| 2018-10-01 | C4g | £26.1 | £33.6 (+29%) | 23% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 27 |
| Retained | 26 (96%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £454,243.14 |
| Margin saved (retained customers' terms) | £2,342,541.34 |
| Wasted offer cost (churned anyway) | £512.78 |
| **Net ROI of retention strategy** | **£1,888,298.21** |
| Acquisition cost avoided (retained customers) | £4,150.00 |
| **Full economic ROI (margin + acq savings)** | **£1,892,448.21** |

Missed opportunities (churns with no offer): **5** (£4,127.84 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 5 (£4,127.84 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 1 | 1 | £122.71 | £867.92 | £745.20 | £0.00 |
| 2018 | 3 | 3 | £24511.82 | £165693.15 | £141181.34 | £0.00 |
| 2019 | 4 | 4 | £43042.88 | £298543.40 | £255500.52 | £0.00 |
| 2020 | 6 | 6 | £47598.87 | £284072.45 | £236473.57 | £1139.33 |
| 2021 | 4 | 3 | £120893.47 | £424960.89 | £304067.42 | £-178.13 |
| 2022 | 2 | 2 | £73447.76 | £327284.70 | £253836.94 | £0.00 |
| 2023 | 4 | 4 | £94319.28 | £436973.65 | £342654.37 | £0.00 |
| 2024 | 3 | 3 | £50306.35 | £404145.19 | £353838.84 | £3166.65 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2017-04-01 | C8 | 0.95 | 8% | £122.71 | £867.92 | £150 | £745.20 | retained |
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24227.89 | £163704.65 | £150 | £139476.77 | retained |
| 2018-04-01 | C8 | 0.95 | 8% | £131.88 | £977.60 | £150 | £845.72 | retained |
| 2018-12-31 | C7 | 0.95 | 8% | £152.05 | £1010.90 | £150 | £858.85 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £27950.99 | £194971.28 | £150 | £167020.29 | retained |
| 2019-04-01 | C8 | 0.95 | 8% | £127.34 | £893.79 | £150 | £766.44 | retained |
| 2019-07-01 | C9 | 0.95 | 8% | £122.74 | £1037.18 | £150 | £914.44 | retained |
| 2020-03-01 | C_IC2 | 0.95 | 8% | £10298.77 | £88443.61 | £150 | £78144.84 | retained |
| 2020-03-31 | C8 | 0.95 | 8% | £137.77 | £1263.03 | £150 | £1125.26 | retained |
| 2020-03-31 | C_IC1 | 0.95 | 8% | £19604.63 | £168458.66 | £150 | £148854.03 | retained |
| 2020-06-30 | C9 | 0.95 | 8% | £106.17 | £1018.47 | £150 | £912.30 | retained |
| 2020-12-30 | C7 | 0.95 | 8% | £140.30 | £1197.37 | £150 | £1057.07 | retained |
| 2020-12-31 | C_IC3 | 0.95 | 8% | £17311.23 | £23691.31 | £150 | £6380.08 | retained |
| 2021-03-31 | C_IC2 | 0.95 | 8% | £15320.99 | £105808.01 | £150 | £90487.02 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £22356.55 | £156157.03 | £150 | £133800.48 | retained |
| 2021-12-30 | C5 | 0.85 | 8% | £512.78 | £2277.57 | £400 | £-512.78 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £82703.16 | £162995.85 | £150 | £80292.69 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25060.47 | £95576.59 | £150 | £70516.12 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £48387.28 | £231708.10 | £150 | £183320.82 | retained |
| 2023-03-31 | C6 | 0.52 | 5% | £405.60 | £3684.94 | £400 | £3279.33 | retained |
| 2023-05-30 | C_IC2 | 0.95 | 8% | £18634.85 | £129537.59 | £150 | £110902.74 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £34716.87 | £243860.00 | £150 | £209143.13 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £40561.96 | £59891.12 | £150 | £19329.17 | retained |
| 2024-03-30 | C8 | 0.95 | 8% | £178.26 | £1313.93 | £150 | £1135.67 | retained |
| 2024-06-28 | C_IC2 | 0.95 | 8% | £16369.46 | £133340.97 | £150 | £116971.50 | retained |
| 2024-07-28 | C_IC1 | 0.95 | 8% | £33758.63 | £269490.30 | £150 | £235731.67 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C8 | 2017-04-01 | (window end) | 105 | active |
| C_IC1 | 2018-01-31 | (window end) | 95 | active |
| C7 | 2018-12-31 | (window end) | 84 | active |
| C_IC2 | 2019-01-31 | (window end) | 83 | active |
| C9 | 2019-07-01 | (window end) | 78 | active |
| C_IC3 | 2020-12-31 | (window end) | 60 | active |
| C5 | 2021-12-30 | 2021-12-30 | 0 | churned |
| C6 | 2023-03-31 | 2024-03-30 | 12 | churned |

**Eventually churned (2/8)**: C5, C6 — avg 6 months post-retention before final churn.
**Still active (6/8)**: C8, C_IC1, C7, C_IC2, C9, C_IC3 — survived to simulation end.

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £5,637,800.63 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £518,339.09 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,178.25 |
| 2017 | £30,566.05 |
| 2018 | £99,706.17 |
| 2019 | £227,872.41 |
| 2020 | £153,032.39 |
| 2021 | £87,129.50 |
| 2022 | £303,662.24 |
| 2023 | £88,291.65 | ← trailing
| 2024 | £357,551.17 | ← trailing
| 2025 | £112,263.68 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £3,701.04 | — |
| C2 | £4,356.28 | — |
| C3 | £4,675.82 | — |
| C4 | £2,727.75 | £-835.73 |
| C5 | £7,565.43 | — |
| C6 | £15,520.49 | £3,127.71 |
| C7 | £6,201.62 | £23.48 |
| C8 | £7,042.38 | £158.93 |
| C9 | £7,296.60 | £911.62 |
| C_IC1 | £1,333,099.08 | £320,898.56 |
| C_IC2 | £735,365.89 | £168,437.45 |
| C_IC3 | £2,278,728.69 | £17,644.60 |
| C_IC4 | £1,231,519.55 | £7,972.47 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £2,259.66 | — | — | — | £5,096.01 | — | £4,189.02 | — | — | — | — | — | — |
| 2017 | £1,866.40 | £3,448.52 | £3,029.81 | £2,742.22 | £3,908.13 | £7,630.18 | £2,786.39 | £4,112.60 | £3,653.20 | — | — | — | — |
| 2018 | £1,719.42 | £3,117.96 | £2,735.70 | £2,244.33 | £3,848.31 | £5,861.07 | £2,579.63 | £3,446.77 | £3,434.55 | £909,624.79 | — | — | — |
| 2019 | £1,697.80 | £2,636.08 | £2,692.56 | £2,508.16 | £4,077.50 | £6,421.57 | £2,893.06 | £3,508.69 | £3,243.91 | £815,715.03 | £542,363.74 | — | — |
| 2020 | £2,034.59 | £2,294.14 | £2,586.03 | £2,582.20 | £4,517.94 | £7,623.25 | £3,145.02 | £4,073.66 | £3,787.92 | £576,736.84 | £293,544.83 | £1,010,362.98 | £538,445.61 |
| 2021 | £2,042.23 | £2,356.99 | £2,458.40 | £2,267.90 | £4,261.36 | £7,289.32 | £3,423.59 | £4,066.88 | £3,661.53 | £532,150.82 | £314,544.40 | £970,054.62 | £561,837.14 |
| 2022 | £2,033.60 | £2,343.14 | £2,442.45 | £1,528.55 | £4,247.85 | £7,927.26 | £2,724.09 | £3,997.66 | £3,698.51 | £564,101.48 | £335,668.74 | £1,074,307.83 | £559,776.91 |
| 2023 | £2,075.14 | £2,410.26 | £2,566.65 | £1,156.74 | £4,593.57 | £8,819.29 | £2,833.45 | £4,309.68 | £3,969.74 | £645,854.05 | £364,977.40 | £1,027,755.56 | £568,794.19 |
| 2024 | £2,081.42 | £2,634.75 | £2,590.58 | £1,546.23 | £4,242.06 | £9,206.96 | £3,203.73 | £4,815.58 | £4,262.49 | £736,756.68 | £388,212.19 | £1,154,175.83 | £660,062.52 |
| 2025 | £2,037.52 | £2,528.22 | £2,673.14 | £1,573.85 | £4,332.79 | £9,325.67 | £3,498.45 | £4,422.66 | £4,052.96 | £774,735.50 | £417,984.43 | £1,241,910.05 | £730,448.49 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £5,018.38, range £57.03–£26,240.98.

- C1: cost to serve £414.25, net margin after CTS £2,311.07
- C1g: cost to serve £64.75, net margin after CTS £1,475.88
- C2: cost to serve £283.32, net margin after CTS £1,762.99
- C2g: cost to serve £57.03, net margin after CTS £1,356.44
- C3: cost to serve £292.52, net margin after CTS £2,096.31
- C3g: cost to serve £58.25, net margin after CTS £1,240.28
- C4: cost to serve £565.21, net margin after CTS £2,741.57
- C4g: cost to serve £216.57, net margin after CTS £1,127.40
- C5: cost to serve £871.49, net margin after CTS £8,478.91
- C6: cost to serve £1,356.68, net margin after CTS £21,849.51
- C7: cost to serve £954.89, net margin after CTS £9,855.71
- C8: cost to serve £938.31, net margin after CTS £11,486.03
- C9: cost to serve £896.18, net margin after CTS £11,791.90
- C_IC1: cost to serve £20,033.25, net margin after CTS £1,893,675.74
- C_IC2: cost to serve £11,415.37, net margin after CTS £911,957.71
- C_IC3: cost to serve £26,240.98, net margin after CTS £1,772,256.03
- C_IC3g: cost to serve £9,229.97, net margin after CTS £613,417.06
- C_IC4: cost to serve £16,441.72, net margin after CTS £1,090,243.56


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 26 recovery surcharge(s) at renewal based on prior-term losses (3 gas). Avg surcharge: 15.0%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.31/MWh |
| C5 | electricity | 2018-12-31 | £-204.31 | £2,322.51 | +3.8% | £148.68/MWh | £153.39/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,283.71 | £6,187.80 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,215.97 | £10,069.00 | +20.0% | £128.22/MWh | £175.80/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,915.21 | £3,421.95 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £122.71/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £191.68/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £140.57/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £59.13/MWh |
| C5 | electricity | 2021-12-30 | £-365.46 | £2,671.00 | +8.7% | £311.83/MWh | £342.69/MWh |
| C7 | electricity | 2021-12-30 | £-114.05 | £1,995.80 | +0.7% | £311.83/MWh | £317.57/MWh |
| C_IC3 | electricity | 2021-12-31 | £-26,911.89 | £443,752.95 | +1.1% | £224.03/MWh | £260.37/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £317.27/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.71/MWh |
| C4 | electricity | 2022-09-30 | £-220.41 | £906.59 | +19.3% | £404.86/MWh | £484.90/MWh |
| C4g | gas | 2022-09-30 | £-901.21 | £1,040.11 | +20.0% | £183.79/MWh | £250.92/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £318.59/MWh |
| C8 | electricity | 2023-03-31 | £-481.87 | £3,898.74 | +7.4% | £319.17/MWh | £359.26/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £235.59/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.52/MWh |
| C4 | electricity | 2023-09-30 | £-277.33 | £1,324.46 | +15.9% | £216.77/MWh | £249.37/MWh |
| C4g | gas | 2023-09-30 | £-1,950.48 | £2,732.11 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-445.92 | £3,990.91 | +6.2% | £242.22/MWh | £244.32/MWh |
| C_IC3 | electricity | 2023-12-31 | £-168,675.16 | £928,468.48 | +13.2% | £118.95/MWh | £127.88/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |



## Portfolio Intelligence Pack (Phase AH)

Board-level synthesis of CRM and flexibility intelligence derived from observable operational data.

### 1. Retention Intelligence

- **Retention offers made:** 27
- **Offer acceptance rate:** 96% (26 retained / 1 churned despite offer)
- **Estimated margin protected:** £2,342,541.34
- **No-offer churns:** 5 total (0 blind miss / 0 deliberate pass)
- **Retention coverage rate:** 84% of at-risk renewals received an offer

### 2. Flexibility Revenue Intelligence

- No flexibility revenue data available.

### 3. Churn Pattern Analysis

- **Total lifetime churn events:** 6
- **Peak churn year:** 2020 (2 events)

### 4. Board Recommendations

1. **Crisis-year churn:** 2 churn events in 2021–2022. Maintain minimum hedge floor pre-crisis to preserve pricing stability and limit bill-shock churn.

## CRM Intelligence: Risk Triage (Final Year)

Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.

| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |
|---------|-----|-----------|-----------|----------|-------------|-----------------|
| C6 | SME | HIGH | 38% | 26% | -27.4% [competitive] | £21,849.51 |
| C8 | resi | HIGH | 38% | 0% | -23.6% [competitive] | £11,486.03 |
| C9 | resi | HIGH | 38% | 0% | -14.3% | £11,791.90 |
| C5 | SME | HIGH | 35% | 85% | +64.8% [overpriced] | £8,478.91 |
| C7 | resi | HIGH | 35% | 0% | -14.3% | £9,855.71 |
| C1 | resi | HIGH | 32% | 4% | -12.0% | £2,311.07 |
| C2 | resi | HIGH | 32% | 0% | -19.2% | £1,762.99 |
| C3 | resi | HIGH | 32% | 0% | -39.5% [competitive] | £2,096.31 |
| C4 | resi | HIGH | 32% | 0% | -9.0% | £2,741.57 |
| C_IC3 | I&C | LOW | 8% | 95% | -54.9% [competitive] | £1,772,256.03 |
| C_IC1 | I&C | LOW | 5% | 95% | -0.1% | £1,893,675.74 |
| C_IC2 | I&C | LOW | 5% | 95% | +12.4% [overpriced] | £911,957.71 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 9 accounts
- MEDIUM (>=15%): 0 accounts
- LOW (<15%): 3 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £72,373.99
- Overpriced vs SVT within HIGH/CRITICAL band: 1 account(s) -- rate shock risk compounds churn probability

**Company blind spot:** 7 HIGH/CRITICAL account(s) where company churn estimate was <10%.
  - C8: sim 38%, company est 0%
  - C9: sim 38%, company est 0%
  - C7: sim 35%, company est 0%
  - C1: sim 32%, company est 4%
  - C2: sim 32%, company est 0%

## Churn Root Cause Attribution

Per-churned-account analysis: pricing journey, rate-vs-SVT positioning, and company vs SIM churn estimate at the point of departure.

| Account | Seg | Churn Date | Tenure | Last Rate Shock | Rate vs SVT | Sim Risk | Co. Est. | Margin Lost |
|---------|-----|------------|--------|-----------------|-------------|----------|----------|-------------|
| C2 | resi | 2020-03-31 | 4.0yr | +15.0% | -19.2% | 32% | 0% | £1,762.99 |
| C3 | resi | 2020-06-30 | 4.0yr | -5.0% | -39.5% | 32% | 0% | £2,096.31 |
| C1 | resi | 2021-12-30 | 6.0yr | +1.1% | -12.0% | 32% | 4% | £2,311.07 |
| C5 | SME | 2021-12-30 | 6.0yr | +1.1% | +64.8% | 35% | 85% | £8,478.91 |
| C6 | SME | 2024-03-30 | 8.0yr | -4.2% | -27.4% | 38% | 26% | £21,849.51 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 32% | 0% | £2,741.57 |

**Root Cause Summary:**
- Total churned accounts: 6
- Lifetime margin lost: £39,240.35
- Average tenure at departure: 6.0 years
- Company blind misses (sim >=30%, co. est. <10%): 4 -- C2, C3, C1, C4
- Company-warned churns (co. est. >=20%): 2 -- C5, C6
- Crisis-era churns (2021-22): 2 -- absolute crisis price level, not rate-change delta, was the driver
- Overpriced vs SVT at departure: 1 account(s) -- rate shock risk was observable but unactioned

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 5 accounts that churned without an offer? Calibrated from 27 actual offers (observed retention rate 96%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C2 | resi | 2020-03-31 | 0% | £559.82 | 5% | £27.99 | £511.09 | MISSED OPP. |
| C3 | resi | 2020-06-30 | 0% | £579.51 | 5% | £28.98 | £529.08 | MISSED OPP. |
| C1 | resi | 2021-12-30 | 4% | £-178.13 | 5% | £0.00 | n/a | CORRECT PASS |
| C6 | SME | 2024-03-30 | 26% | £2,697.78 | 8% | £215.82 | £2,382.04 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 0% | £468.87 | 5% | £23.44 | £428.06 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 5
- Correct no-offer (net-neg ETM): 1 (C1)
- Missed opportunities (positive ETM, below detection): 4
- Total term margin foregone: £4,305.98
- Total retention cost (counterfactual): £296.23
- Net counterfactual benefit: £3,850.26 (at 96% retention probability)
- Root cause: company churn detection below threshold for all missed cases -- churn model underestimated bill-shock risk

## Pricing Basis Risk Attribution

Forward curve accuracy at each contract term. tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd: positive = company over-estimated costs (higher than market); negative = company under-estimated (margin-at-risk).
Portfolio-wide mean error: +5.2%

| Year | Contracts | Mean Error | Max Abs | Over-priced | Under-priced | Assessment |
|------|-----------|------------|---------|-------------|--------------|------------|
| 2016 | 17 | +8.9% | 29.1% | 9 | 4 | moderate over |
| 2017 | 14 | +5.4% | 46.6% | 8 | 5 | moderate over |
| 2018 | 16 | -2.9% | 27.7% | 6 | 8 | on target |
| 2019 | 19 | +8.3% | 37.2% | 9 | 3 | moderate over |
| 2020 | 21 | -0.6% | 33.8% | 9 | 7 | on target |
| 2021 | 15 | +4.8% | 44.5% | 4 | 3 | on target |
| 2022 | 13 | -0.6% | 23.2% | 5 | 3 | on target |
| 2023 | 13 | +17.7% | 40.0% | 8 | 1 | HIGH OVER-PRICE |
| 2024 | 12 | +6.9% | 22.6% | 6 | 1 | moderate over |
| 2025 | 1 | +33.1% | 33.1% | 1 | 0 | HIGH OVER-PRICE |

**Basis Risk Summary:**
- Portfolio mean tariff error: +5.2%
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
| 2021 | £5,235 | £4,362 | 0.30% |
| 2022 | £10,197 | £8,498 | 0.30% |
| 2023 | £6,710 | £5,592 | 0.26% |
| 2024 | £3,173 | £2,644 | 0.14% |
| 2025 | £4,623 | £3,853 | 0.48% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,197 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £524 | £91 | 11.3% |
| 2017 | 14 | £16,735 | £8,803 | £2,183 | 13.0% |
| 2018 | 15 | £29,022 | £17,502 | £6,647 | 22.9% |
| 2019 | 17 | £70,486 | £41,296 | £13,404 | 19.0% |
| 2020 | 18 | £69,666 | £45,692 | £8,502 | 12.2% |
| 2021 | 14 | £125,522 | £56,036 | £6,224 | 5.0% << |
| 2022 | 11 | £312,079 | £95,273 | £27,606 | 8.8% |
| 2023 | 11 | £231,368 | £82,636 | £8,027 | 3.5% << |
| 2024 | 11 | £200,570 | £116,111 | £32,505 | 16.2% |
| 2025 | 8 | £120,602 | £64,210 | £14,033 | 11.6% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £32,505 net/customer
**Worst year per customer:** 2016 at £91 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £414 | — | £414 |
| C1g | — | £643 | £643 |
| C2 | £378 | — | £378 |
| C2g | — | £611 | £611 |
| C3 | £206 | — | £206 |
| C3g | — | £283 | £283 |
| C4 | £131 | — | £131 |
| C4g | — | £-2,030 | £-2,030 * |
| C5 | £-61 | — | £-61 * |
| C6 | £4,314 | — | £4,314 |
| C7 | £-1,449 | — | £-1,449 * |
| C8 | £1,229 | — | £1,229 |
| C9 | £1,473 | — | £1,473 |
| C_IC1 | £866,914 | — | £866,914 |
| C_IC2 | £440,043 | — | £440,043 |
| C_IC3 | £81,156 | — | £81,156 |
| C_IC3g | — | £52,416 | £52,416 |
| C_IC4 | £14,584 | — | £14,584 |
| **Total** | **£1,409,331** | **£51,923** | **£1,461,253** |

Loss-making accounts: C4g (£-2,030), C7 (£-1,449), C5 (£-61)
Gas loss-making: C4g (£-2,030)
Gas portfolio net: £51,923 (3.6% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,034 | £10,920 | £-8,885 |
| 2017 | £30,081 | £112,495 | £-82,414 |
| 2018 | £109,583 | £246,455 | £-136,872 |
| 2019 | £252,590 | £836,842 | £-584,252 |
| 2020 | £126,136 | £1,004,397 | £-878,260 |
| 2021 | £202,761 | £468,486 | £-265,724 |
| 2022 | £141,106 | £1,161,062 | £-1,019,956 |
| 2023 | £401,660 | £1,238,874 | £-837,213 |
| 2024 | £195,333 | £599,235 | £-403,902 |
| 2025 | £-30 | £119 | £-148 |
| **Total** | **£1,461,253** | **£5,678,885** | **£-4,217,631** |

Largest hedging cost: **2022** (£1,019,956 vs naked)
Smallest hedging cost: **2025** (£148 vs naked)
Conclusion: systematic forward hedging cost £4,217,631 over 10 years vs spot purchasing.

## Customer Service Quality

Ofgem benchmarks: bill clarity >0.82 (GREEN) / >0.80 (AMBER) / ≤0.80 (RED); complaint probability <5% (GREEN) / <6% (RED); bill shock <0.20% (GREEN) / <0.30% (AMBER) / ≥0.30% (RED).

| Year | Clarity | Complaint% | Shock% | Shock events | Bills | RAG |
|------|---------|------------|--------|--------------|-------|-----|
| 2016 | 0.829 G | 4.7% | 0.20% | 31 | 108 | GREEN |
| 2017 | 0.818 A | 4.7% | 0.17% | 50 | 168 | AMBER |
| 2018 | 0.810 A | 4.7% | 0.16% | 60 | 180 | AMBER |
| 2019 | 0.824 G | 4.7% | 0.17% | 66 | 204 | GREEN |
| 2020 | 0.830 G | 4.3% | 0.14% | 47 | 186 | GREEN |
| 2021 | 0.826 G | 4.6% | 0.16% | 47 | 168 | GREEN |
| 2022 | 0.794 R | 5.5% | 0.22% | 56 | 132 | RED ! |
| 2023 | 0.813 A | 4.7% | 0.17% | 39 | 132 | AMBER |
| 2024 | 0.821 G | 4.5% | 0.15% | 26 | 117 | GREEN |
| 2025 | 0.782 R | 5.8% | 0.23% | 16 | 48 | RED ! |

Worst clarity year: **2025** (0.782)
Highest complaint probability: **2025** (5.8%)
Worst bill shock: **2025** (0.23%)
RED years: 2022, 2025
AMBER years: 2017, 2018, 2023
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,424 | £1,178 |
| 2017 | 2.69 | WATCH | £2,497,718 | £30,566 |
| 2018 | — | — | £2,486,407 | £99,706 |
| 2019 | — | — | £2,606,406 | £227,872 |
| 2020 | — | — | £2,914,253 | £153,032 |
| 2021 | — | — | £2,983,493 | £87,129 |
| 2022 | 2.70 | WATCH | £3,190,740 | £303,662 |
| 2023 | 2.72 | WATCH | £3,332,123 | £88,292 |
| 2024 | — | — | £3,732,742 | £357,551 |
| 2025 | — | — | £3,782,418 | £112,264 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,782,418)**
**Treasury growth: £2,467,424 → £3,782,418 (+£1,314,994)**

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
| C2 | 2020-03 | 0.5% | £560 | below threshold |
| C3 | 2020-06 | 0.0% | £580 | below threshold |
| C1 | 2021-12 | 4.0% | -£178 | below threshold |
| C6 | 2024-03 | 25.6% | £2,698 | below threshold ⚑ |
| C4 | 2024-09 | 0.0% | £469 | below threshold |

**High-risk no-offer events (≥10% churn): 1** — £2,698 margin at risk.

### Gas Renewal Risk — High-Churn Reprice Events (≥15% estimate)

| Customer | Term Start | Old Rate p/therm | New Rate p/therm | Churn Est |
|----------|-----------|-----------------|-----------------|----------|
| C2g | 2017-04 | 26.92 | 32.81 | 20.1% |
| C1g | 2017-12 | 26.25 | 33.49 | 22.6% |
| C3g | 2018-07 | 23.11 | 28.80 | 20.8% |
| C4g | 2018-10 | 26.10 | 33.61 | 23.3% |
| C_IC3g | 2020-12 | 15.44 | 19.98 | 23.7% |
| C4g | 2021-09 | 16.09 | 35.00 | 73.5% |
| C_IC3g | 2021-12 | 19.98 | 125.90 | 95.0% |
| C4g | 2022-09 | 35.00 | 95.00 | 95.0% |

**High-risk gas reprices: 8**

> ⚑ = customers with ≥15% churn estimate who received no retention offer.

## Retention Decision Economics

Per-offer cost, expected margin protected, and ROI for each retention intervention.

| Customer | Period | Retention Cost £ | Margin Protected £ | ROI | Discount % | Outcome |
|----------|--------|-----------------|-------------------|-----|------------|---------|
| C8 | 2017-04 | £123 | £868 | 7.1× | 8% | retained |
| C_IC1 | 2018-01 | £24,228 | £163,705 | 6.8× | 8% | retained |
| C8 | 2018-04 | £132 | £978 | 7.4× | 8% | retained |
| C7 | 2018-12 | £152 | £1,011 | 6.6× | 8% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £27,951 | £194,971 | 7.0× | 8% | retained |
| C8 | 2019-04 | £127 | £894 | 7.0× | 8% | retained |
| C9 | 2019-07 | £123 | £1,037 | 8.5× | 8% | retained |
| C_IC2 | 2020-03 | £10,299 | £88,444 | 8.6× | 8% | retained |
| C8 | 2020-03 | £138 | £1,263 | 9.2× | 8% | retained |
| C_IC1 | 2020-03 | £19,605 | £168,459 | 8.6× | 8% | retained |
| C9 | 2020-06 | £106 | £1,018 | 9.6× | 8% | retained |
| C7 | 2020-12 | £140 | £1,197 | 8.5× | 8% | retained |
| C_IC3 | 2020-12 | £17,311 | £23,691 | 1.4× | 8% | retained |
| C_IC2 | 2021-03 | £15,321 | £105,808 | 6.9× | 8% | retained |
| C_IC1 | 2021-04 | £22,357 | £156,157 | 7.0× | 8% | retained |
| C5 | 2021-12 | £513 | £2,278 | 4.4× | 8% | churned_despite_offer |
| C_IC3 | 2021-12 | £82,703 | £162,996 | 2.0× | 8% | retained |
| C_IC2 | 2022-04 | £25,060 | £95,577 | 3.8× | 8% | retained |
| C_IC1 | 2022-05 | £48,387 | £231,708 | 4.8× | 8% | retained |
| C6 | 2023-03 | £406 | £3,685 | 9.1× | 5% | retained |
| C_IC2 | 2023-05 | £18,635 | £129,538 | 7.0× | 8% | retained |
| C_IC1 | 2023-06 | £34,717 | £243,860 | 7.0× | 8% | retained |
| C_IC3 | 2023-12 | £40,562 | £59,891 | 1.5× | 8% | retained |
| C8 | 2024-03 | £178 | £1,314 | 7.4× | 8% | retained |
| C_IC2 | 2024-06 | £16,369 | £133,341 | 8.1× | 8% | retained |
| C_IC1 | 2024-07 | £33,759 | £269,490 | 8.0× | 8% | retained |

**Total retention spend: £454,243** | **Total margin protected: £2,344,819**
**Portfolio retention ROI: 5.2×** | **Retained: 26/27**
**Best ROI intervention: C9 2020-06 (9.6×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £134,207 | — |
| Exit Gas (with churn risk) | £49,597 | -£84,611 |
| Reprice to Breakeven | £136,237 | +£2,030 |

**Loss-making gas accounts: C4**
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
| 2020 | 81.2% | 0.0% | 96.0% | 1 | 13 |
| 2021 | 82.7% | 0.0% | 97.0% | 1 | 10 |
| 2022 | 84.9% | 0.0% | 97.4% | 1 | 10 |
| 2023 | 82.1% | 0.0% | 95.9% | 1 | 10 |
| 2024 | 77.9% | 0.0% | 94.5% | 1 | 7 |
| 2025 | 89.4% | 89.4% | 89.4% | — | 1 |

**Lowest portfolio hedge fraction: 2024 (77.9%)** — risk erosion from regime-change blindness.
**Naked positions first appear in 2019** — unhedged accounts expose portfolio to spot price swings.

> Regime-change blindness: the sim converged toward lower hedging during calm 2016-2020,
> mirroring the strategy that destroyed real UK suppliers entering the 2021-22 crisis.

## Risk Committee Intervention Pattern

Annual risk committee wake-ups (triggered when portfolio VaR exceeds threshold).

| Year | Wake-ups | Customer Adjustments | Avg Customers/Event | Max VaR Stressed £ |
|------|----------|---------------------|--------------------|--------------------|
| 2016 | 13 | 12 | 0.9 | £9 |
| 2017 | 12 | 33 | 2.8 | £401 |
| 2022 | 9 | 51 | 5.7 | £20,830 |
| 2023 | 4 | 25 | 6.2 | £48,770 |

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
| 2020 | 2020-03-16 | 20 | C_IC1 | -£19 |
| 2021 | 2021-11-24 | 30 | C_IC1 | -£75 |
| 2022 | 2022-01-24 | 26 | C_IC1 | -£89 |
| 2023 | 2023-06-16 | 22 | C_IC1 | -£22 |
| 2024 | 2024-06-28 | 31 | C_IC1 | -£26 |
| 2025 | 2025-01-08 | 31 | C_IC1 | -£81 |

**Single worst period: 2022 2022-01-24 SP26 (C_IC1, -£89)** — exposure from gas supply anchor at year-end pricing.

> SP = settlement period (1-48; SP1 = 00:00-00:30). Year-end gas exposure dominates from 2020 onward as C_IC3g position grows.

## BSC Credit Obligation and Regulatory Levy Breakdown

Elexon BSC credit posting requirement and annual levy costs.

| Year | BSC Credit £ | CM Levy £ | Mutualization £ | CCL £ | Gas Network £ |
|------|-------------|----------|----------------|-------|--------------|
| 2016 | £30 | £37 | — | £189 | £479 |
| 2017 | £559 | £1,977 | — | £11,165 | £898 |
| 2018 | £1,019 | £9,350 | — | £17,434 | £905 |
| 2019 | £1,851 | £31,969 | — | £42,460 | £50,388 |
| 2020 | £2,375 | £56,528 | — | £69,454 | £47,112 |
| 2021 | £5,235 | £49,618 | £41,382 | £71,336 | £50,256 |
| 2022 | £10,197 | £36,616 | £99,306 | £70,920 | £54,366 |
| 2023 | £6,710 | £50,872 | £13,725 | £71,702 | £79,700 |
| 2024 | £3,173 | £68,579 | £1,995 | £72,815 | £76,429 |
| 2025 | £4,623 | £30,952 | £852 | £31,156 | £31,816 |

**Peak BSC credit obligation: 2022 (£10,197)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 13 | £154,358 | £84,543 | £6,142 | £11,874 |
| 2017 | 1 | £3,163,027 | £1,913,709 | £866,914 | £3,163,027 |
| 2018 | 1 | £1,539,439 | £923,373 | £440,043 | £1,539,439 |
| 2019 | 2 | £6,437,111 | £2,421,144 | £133,571 | £3,218,556 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £14,584 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,218,556/customer)**
**Best net margin cohort: 2017 (£866,914)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £167 | — | 108 |
| 2017 | +£2,707 | £37,159 | £1,375 | — | 168 |
| 2018 | +£9,875 | £65,510 | £2,385 | — | 180 |
| 2019 | +£28,353 | £164,625 | £6,207 | — | 204 |
| 2020 | +£35,378 | £238,546 | £6,434 | — | 186 |
| 2021 | +£14,993 | £246,433 | £9,166 | — | 168 |
| 2022 | -£49,653 CREDIT | £255,773 | £35,373 | 1 | 132 |
| 2023 | +£64,645 | £271,353 | £13,707 | 47 | 132 |
| 2024 | +£109,721 | £307,042 | £11,427 | 4271 | 117 |
| 2025 | +£46,833 | £135,390 | £4,918 | — | 48 |

**CfD turned CREDIT in 2022: -£49,653 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2022 (£35,373)**

> CfD (Contracts for Difference): when wholesale > strike price, generators repay;
> the net credit is passed through as a negative levy on supplier bills.

## Segment Gross Margin Attribution

Gross margin (£) by customer segment and year.

| Year | resi electricity | resi gas | SME electricity | I&C electricity | I&C gas | Total |
|------|----------|----------|----------|----------|----------|-------|
| 2016 | £3,270 | £811 | £2,733 | £0 | £0 | £6,814 |
| 2017 | £4,994 | £1,430 | £3,395 | £113,418 | £0 | £123,236 |
| 2018 | £5,063 | £1,363 | £3,206 | £252,900 | £0 | £262,531 |
| 2019 | £5,779 | £1,428 | £4,051 | £616,144 | £74,626 | £702,028 |
| 2020 | £5,218 | £990 | £4,236 | £736,031 | £75,972 | £822,448 |
| 2021 | £4,684 | £222 | £4,522 | £692,818 | £82,255 | £784,501 |
| 2022 | £2,652 | -£834 | £3,916 | £951,149 | £91,118 | £1,048,001 |
| 2023 | £5,259 | -£575 | £4,835 | £777,963 | £121,515 | £908,997 |
| 2024 | £6,717 | £762 | £1,663 | £1,144,422 | £123,652 | £1,277,216 |
| 2025 | £2,755 | £0 | £0 | £457,420 | £53,509 | £513,683 |

**Best gross margin year: 2024 (£1,277,216)** | **Worst: 2016 (£6,814)**
**Loss-making: resi gas in 2022 (£-834)**
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
| 2020 | 10 | -30.1% | 0/10 | -68.6% | +-17.6% |
| 2021 | 8 | +9.8% | 4/8 | -12.0% | +64.8% |
| 2022 | 6 | +6.4% | 3/6 | -66.2% | +100.1% |
| 2023 | 6 | -34.6% | 0/6 | -60.5% | +-10.8% |
| 2024 | 6 | -24.5% | 0/6 | -54.9% | +-9.0% |
| 2025 | 1 | -23.6% | 0/1 | -23.6% | +-23.6% |

**Best headroom year: 2023 (avg 34.6% below SVT)**
**Largest above-SVT year: 2021** (4/8 terms above — note: I&C customers exempt from SVT cap)

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
| 2020 | £2,914,253 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,983,493 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,190,740 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,332,123 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,732,742 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,782,418 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 45.2% | £1,181 | £605 | 1.53% |
| 2017 | 14 | 33.5% | £24,902 | £8,914 | 1.80% |
| 2018 | 15 | 41.6% | £40,064 | £17,612 | 1.97% |
| 2019 | 17 | 40.7% | £96,791 | £41,404 | 1.87% |
| 2020 | 18 | 41.5% | £104,845 | £45,784 | 2.05% |
| 2021 | 14 | 30.0% | £174,184 | £56,137 | 1.95% |
| 2022 | 11 | 22.5% | £384,909 | £95,375 | 1.99% |
| 2023 | 11 | 24.1% | £311,079 | £82,721 | 2.21% |
| 2024 | 11 | 39.9% | £274,156 | £116,128 | 2.13% |
| 2025 | 8 | 38.6% | £152,696 | £64,253 | 2.99% |

**Best EBIT%: 2016 (45.2%)** | **Worst EBIT%: 2022 (22.5%)**
**Peak revenue/customer: 2022 (£384,909)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Churn Prediction Calibration

How well the company estimated churn probability versus actual simulation outcomes.

| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |
|----------|------|----------------|-----------------|-------|---------|
| C2 | 2020-03 | 32.0% | 0.5% | -31.5pp | UNDERESTIMATED |
| C3 | 2020-06 | 32.0% | 0.0% | -32.0pp | UNDERESTIMATED |
| C1 | 2021-12 | 32.0% | 4.0% | -28.0pp | UNDERESTIMATED |
| C5 | 2021-12 | 35.0% | 84.9% | +49.9pp | OVERESTIMATED |
| C6 | 2024-03 | 38.0% | 25.6% | -12.4pp | UNDERESTIMATED |
| C4 | 2024-09 | 32.0% | 0.0% | -32.0pp | UNDERESTIMATED |

**Outcomes: 5 underestimated / 0 accurate / 1 overestimated**
**Mean absolute error: 31.0pp**
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
| 2020 | 21 | 11.8% | 33.8% | MODERATE |
| 2021 | 15 | 11.8% | 44.5% | MODERATE |
| 2022 | 13 | 10.5% | 23.2% | MODERATE |
| 2023 | 13 | 19.4% | 40.0% | POOR |
| 2024 | 12 | 9.7% | 22.6% | GOOD |
| 2025 | 1 | 33.1% | 33.1% | POOR |

**Best accuracy year (n≥5): 2024 (9.7% mean error)**
**Worst accuracy year (n≥5): 2023 (19.4% mean error)**

> Errors reflect the company's information gap: forward curves are approximations;
> the company cannot observe simulation wholesale cost internals (epistemic blindfold).

## Dynamic Pricing Activity

Rate adjustments driven by the margin feedback loop and emergency reprice events.

| Year | Adjustments | Avg Delta £/MWh | Up | Down | Emergency |
|------|------------|-----------------|-----|------|-----------|
| 2016 | 4 | -0.6 | 1 | 3 | 0 |
| 2017 | 13 | -1.1 | 1 | 12 | 0 |
| 2018 | 14 | +2.5 | 6 | 8 | 2 |
| 2019 | 15 | +1.4 | 5 | 10 | 2 |
| 2020 | 17 | +4.3 | 9 | 8 | 2 |
| 2021 | 12 | +12.3 | 12 | 0 | 6 |
| 2022 | 10 | +18.8 | 9 | 1 | 5 |
| 2023 | 10 | +10.6 | 7 | 3 | 7 |
| 2024 | 9 | +8.2 | 6 | 3 | 2 |
| 2025 | 1 | -1.0 | 0 | 1 | 0 |

**Total adjustments 2016-2025: 105** | **Peak avg adjustment: 2022 (+18.8 £/MWh)**
**Emergency reprices: 26 total** (7 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £11,545 | £3,848 | — |
| 2017 | 9 | £33,177 | £3,686 | +£21,633 |
| 2018 | 10 | £938,613 | £93,861 | +£905,435 |
| 2019 | 11 | £1,387,758 | £126,160 | +£449,146 |
| 2020 | 13 | £2,451,735 | £188,595 | +£1,063,977 |
| 2021 | 13 | £2,410,415 | £185,417 | £-41,320 |
| 2022 | 13 | £2,564,798 | £197,292 | +£154,383 |
| 2023 | 13 | £2,640,116 | £203,086 | +£75,318 |
| 2024 | 13 | £2,973,791 | £228,753 | +£333,675 |
| 2025 | 13 | £3,199,524 | £246,117 | +£225,733 |

**Peak portfolio CLV: 2025 (£3,199,524)** | **Earliest/lowest: 2016 (£11,545)**
**Largest YoY gain: 2020 (+£1,063,977)**
**Largest YoY fall: 2021 (£-41,320)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | 51.2% | — | — | — | — |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | 35.8% | +£333,275.90 | +£107,460.46 | +£108,889.99 | +£116,925.46 |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | 44.0% | +£252,322.49 | +£61,745.30 | +£51,194.57 | +£139,382.63 |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | 42.8% | +£1,044,499.09 | +£323,437.66 | +£281,360.24 | +£439,701.19 |
| 2020 | £1,887,212.43 | £431,591.09 | £631,516.48 | £824,104.87 | 43.7% | +£241,760.32 | £-64,648.86 | +£186,179.44 | +£120,229.75 |
| 2021 | £2,438,581.89 | £972,966.99 | £679,703.43 | £785,911.46 | 32.2% | +£551,369.46 | +£541,375.91 | +£48,186.96 | £-38,193.41 |
| 2022 | £4,233,999.48 | £2,384,921.21 | £799,955.65 | £1,049,122.61 | 24.8% | +£1,795,417.59 | +£1,411,954.22 | +£120,252.22 | +£263,211.15 |
| 2023 | £3,421,867.92 | £1,636,287.73 | £875,644.76 | £909,935.43 | 26.6% | £-812,131.56 | £-748,633.49 | +£75,689.11 | £-139,187.18 |
| 2024 | £3,015,720.24 | £929,842.11 | £808,470.76 | £1,277,407.37 | 42.4% | £-406,147.68 | £-706,445.61 | £-67,174.00 | +£367,471.94 |
| 2025 | £1,221,568.85 | £451,130.22 | £256,414.46 | £514,024.17 | 42.1% | £-1,794,151.38 | £-478,711.89 | £-552,056.29 | £-763,383.20 |

**Best GM year: 2016 (51.2%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Risk Committee Activity (2016-2025)

Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.

| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |
|------|----------|----------------------|----------------------|-----------------|
| 2016 | 13 | £28 | £9 | 1 |
| 2017 | 12 | £1,005 | £401 | 3 |
| 2022 | 9 | £56,293 | £20,830 | 7 |
| 2023 | 4 | £127,898 | £48,770 | 7 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £127,898 | Unique accounts ever adjusted: 10

**Most frequently adjusted accounts:**
- C1: 21 sessions
- C7: 19 sessions
- C5: 12 sessions
- C8: 12 sessions
- C_IC1: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £7,296.60 | Median churn: 32% | Total portfolio CLV: £5,637,800.63

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £2,278,728.69 | 8% | 8.9 periods |
| C_IC1 | £1,333,099.08 | 8% | 8.7 periods |
| C_IC4 | £1,231,519.55 | 14% | 8.7 periods |
| C_IC2 | £735,365.89 | 11% | 8.7 periods |

Quadrant CLV: £5,578,713.21 (99% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C6 | £15,520.49 | 38% | 8.8 periods |
| C5 | £7,565.43 | 35% | 8.0 periods |
| C9 | £7,296.60 | 38% | 8.6 periods |

Quadrant CLV: £30,382.52 (1% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £7,042.38 | 38% | 8.4 periods |
| C7 | £6,201.62 | 35% | 8.8 periods |
| C3 | £4,675.82 | 32% | 8.6 periods |
| C2 | £4,356.28 | 32% | 8.6 periods |
| C1 | £3,701.04 | 32% | 9.3 periods |
| C4 | £2,727.75 | 32% | 8.7 periods |

Quadrant CLV: £28,704.90 (1% of portfolio)

**Board action: CRITICAL quadrant has 3 account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**

## Customer Experience & Service Quality

| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |
|------|----------------|---------------|-------------|---------|------|
| 2016 | 0.829 | 0.047 | 0 | 0 |  |
| 2017 | 0.818 | 0.047 | 0 | 0 |  |
| 2018 | 0.810 | 0.047 | 0 | 0 |  |
| 2019 | 0.824 | 0.047 | 0 | 0 |  |
| 2020 | 0.830 | 0.043 | 2 | 0 |  |
| 2021 | 0.826 | 0.046 | 2 | 0 |  |
| 2022 | 0.794 | 0.055 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.813 | 0.047 | 0 | 0 |  |
| 2024 | 0.821 | 0.045 | 2 | 0 |  |
| 2025 | 0.782 | 0.058 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.6% | **Average billing clarity:** 0.818 | **Average complaint probability:** 0.047

**Acquisition performance:** 6 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2025** (0.782) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

## Bill Shock Analysis

Bill shock events occur when a customer's bill increases >20% vs the prior bill.
Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.

| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |
|------|------------|--------|-------|------------|------|
| 2016 | 19.7% | 31 | 108 | 29% |  |
| 2017 | 16.5% | 50 | 168 | 30% |  |
| 2018 | 16.0% | 60 | 180 | 33% |  |
| 2019 | 17.1% | 66 | 204 | 32% |  |
| 2020 | 14.4% | 47 | 186 | 25% |  |
| 2021 | 16.1% | 47 | 168 | 28% |  |
| 2022 | 22.0% | 56 | 132 | 42% | ELEVATED |
| 2023 | 16.8% | 39 | 132 | 30% |  |
| 2024 | 15.1% | 26 | 117 | 22% |  |
| 2025 | 23.1% | 16 | 48 | 33% | ELEVATED |

**Crisis peak: 2025** — 23.1% average shock. Energy crisis drove wholesale costs above locked tariff rates,
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
| 2020 | £238,546.49 | £35,377.66 | £69,454.47 | £56,527.62 | £69,996.68 | £469,902.92 | £124,410.46 |
| 2021 | £246,432.58 | £14,993.40 | £71,335.52 | £49,618.32 | £62,765.47 | £486,527.09 | £123,232.78 |
| 2022 | £255,773.16 | **£-49,653.10** | £70,920.22 | £36,616.05 | £68,992.51 | £481,955.05 | £132,400.08 |
| 2023 | £271,352.62 | £64,644.90 | £71,701.96 | £50,872.20 | £74,959.07 | £547,255.36 | £138,080.31 |
| 2024 | £307,041.67 | £109,720.99 | £72,815.13 | £68,578.71 | £82,405.29 | £642,556.72 | £142,137.49 |
| 2025 | £135,390.25 | £46,833.11 | £31,155.87 | £30,952.43 | £36,061.49 | £281,244.66 | £60,632.12 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.01 (2016) → £281,244.66 (2025). CAGR: 76.4%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £881.72 | £296.53 | £9,021.95 | £1,388.28 | 13.3% | YES |
| 2017 | £30,102.71 | £463.34 | £231,632.96 | £2,660.42 | 1.1% | YES |
| 2018 | £99,331.51 | £374.66 | £432,208.83 | £3,113.94 | 0.7% | YES |
| 2019 | £218,118.22 | £9,754.19 | £1,060,498.38 | £137,766.14 | 11.5% | YES |
| 2020 | £143,287.45 | £9,744.94 | £1,133,173.61 | £120,807.62 | 9.6% | YES |
| 2021 | £78,922.24 | £8,207.26 | £1,460,116.20 | £297,194.89 | 16.9% | YES |
| 2022 | £300,811.94 | £2,850.30 | £2,844,788.31 | £588,076.57 | 17.1% | YES |
| 2023 | £80,929.70 | £7,361.94 | £2,247,846.43 | £297,197.78 | 11.7% | YES |
| 2024 | £348,469.34 | £9,081.83 | £1,935,777.91 | £270,490.62 | 12.3% | YES |
| 2025 | £108,476.16 | £3,787.52 | £832,359.40 | £132,453.71 | 13.7% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £134,207.14 | — | Current strategy |
| EXIT_GAS | £49,596.58 | £-84,610.56 | Remove gas; model elec churn risk |
| REPRICE_GAS | £136,237.00 | £2,029.86 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-2,029.86 | -14.02x | +19.6% |

**Accretive gas accounts:** C1g (£642.69), C2g (£611.34), C3g (£282.80), C_IC3g (£52,415.53) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £51923 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,742,264.36 | £50,091.14 | £1,402,696.26 | 28.0x | Strong |
| I&C gas | £622,647.03 | £0.00 | £52,415.53 | 0.0x | Low return |
| SME electricity | £32,556.58 | £347.01 | £4,252.60 | 12.3x | Moderate |
| resi electricity | £46,390.26 | £490.83 | £2,382.12 | 4.9x | Low return |
| resi gas | £5,596.61 | £194.14 | £-493.03 | -2.5x | CAPITAL DESTROYER |

## Portfolio Concentration Risk

Revenue concentration analysis across 18 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2256** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,281,550.10 (98.8% of total positive margin)
- resi: £47,245.57 (0.7% of total positive margin)
- SME: £30,328.42 (0.5% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,893,675.74 | 29.8% | 5% | £94,683.79 |
| C_IC3 | I&C | £1,772,256.03 | 27.9% | 8% | £141,780.48 |
| C_IC4 | I&C | £1,090,243.56 | 17.1% | 0% | £0.00 |
| C_IC2 | I&C | £911,957.71 | 14.3% | 5% | £45,597.89 |
| C_IC3g | I&C | £613,417.06 | 9.6% | 0% | £0.00 |

**Concentration Risk Warning:**
- I&C segment accounts for 98.8% of total portfolio margin
- Resi and SME segments are effectively margin-neutral at portfolio scale
- A single large I&C departure would remove 14-29% of all margin
- Board action: diversify acquisition pipeline toward profitable resi/SME to reduce I&C dependency

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 105 renewal(s) (24 gas) based on recent portfolio-wide margin rates: 56 surcharge(s), 49 discount(s).

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
| C2g | gas | 2019-04-01 | 10.4% | -1.2% | £32.94/MWh | £32.54/MWh |
| C6 | electricity | 2019-04-01 | 7.5% | +0.2% | £148.35/MWh | £148.72/MWh |
| C8 | electricity | 2019-04-01 | 27.0% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 19.5% | -5.0% | £127.03/MWh | £120.68/MWh |
| C3g | gas | 2019-07-01 | 13.2% | -2.6% | £23.62/MWh | £23.00/MWh |
| C9 | electricity | 2019-07-01 | 10.0% | -1.0% | £127.03/MWh | £125.75/MWh |
| C4 | electricity | 2019-10-01 | 7.9% | +0.0% | £126.72/MWh | £126.76/MWh |
| C4g | gas | 2019-10-01 | 17.2% | -4.6% | £20.41/MWh | £19.47/MWh |
| C1 | electricity | 2019-12-31 | 10.5% | -1.3% | £127.44/MWh | £125.83/MWh |
| C1g | gas | 2019-12-31 | 14.4% | -3.2% | £26.17/MWh | £25.33/MWh |
| C5 | electricity | 2019-12-31 | 10.1% | -1.1% | £127.44/MWh | £126.10/MWh |
| C7 | electricity | 2019-12-31 | 8.9% | -0.4% | £127.44/MWh | £126.88/MWh |
| C_IC3 | electricity | 2020-01-01 | 7.5% | +0.3% | £47.59/MWh | £47.71/MWh |
| C_IC3g | gas | 2020-01-01 | 20.8% | -5.0% | £16.25/MWh | £15.44/MWh |
| C_IC2 | electricity | 2020-03-01 | -59.4% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -52.0% | +15.0% | £125.12/MWh | £143.89/MWh |
| C6 | electricity | 2020-03-31 | -52.0% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -50.0% | +15.0% | £125.12/MWh | £143.89/MWh |
| C_IC1 | electricity | 2020-03-31 | -16.4% | +12.2% | £91.12/MWh | £102.26/MWh |
| C3 | electricity | 2020-06-30 | 23.0% | -5.0% | £113.43/MWh | £107.76/MWh |
| C9 | electricity | 2020-06-30 | 23.0% | -5.0% | £113.43/MWh | £107.76/MWh |
| C4 | electricity | 2020-09-30 | 14.5% | -3.2% | £124.42/MWh | £120.39/MWh |
| C4g | gas | 2020-09-30 | 18.7% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 12.7% | -2.4% | £133.55/MWh | £130.41/MWh |
| C1g | gas | 2020-12-30 | 10.7% | -1.4% | £28.99/MWh | £28.60/MWh |
| C5 | electricity | 2020-12-30 | 6.9% | +0.6% | £133.55/MWh | £134.32/MWh |
| C7 | electricity | 2020-12-30 | -4.1% | +6.1% | £133.55/MWh | £141.65/MWh |
| C_IC3 | electricity | 2020-12-31 | -5.1% | +6.5% | £50.65/MWh | £53.97/MWh |
| C_IC3g | gas | 2020-12-31 | 8.6% | -0.3% | £20.05/MWh | £19.98/MWh |
| C6 | electricity | 2021-03-31 | -20.7% | +14.3% | £175.90/MWh | £201.11/MWh |
| C8 | electricity | 2021-03-31 | -16.2% | +12.1% | £175.90/MWh | £197.15/MWh |
| C_IC2 | electricity | 2021-03-31 | -25.2% | +15.0% | £138.90/MWh | £159.73/MWh |
| C_IC1 | electricity | 2021-04-30 | 2.4% | +2.8% | £113.97/MWh | £117.15/MWh |
| C9 | electricity | 2021-06-30 | 2.1% | +3.0% | £170.38/MWh | £175.44/MWh |
| C4 | electricity | 2021-09-30 | -1.5% | +4.8% | £205.15/MWh | £214.94/MWh |
| C4g | gas | 2021-09-30 | 1.2% | +3.4% | £53.99/MWh | £55.83/MWh |
| C1 | electricity | 2021-12-30 | 5.8% | +1.1% | £311.83/MWh | £315.32/MWh |
| C5 | electricity | 2021-12-30 | 5.8% | +1.1% | £311.83/MWh | £315.32/MWh |
| C7 | electricity | 2021-12-30 | 5.8% | +1.1% | £311.83/MWh | £315.32/MWh |
| C_IC3 | electricity | 2021-12-31 | -23.0% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -22.4% | +15.0% | £109.48/MWh | £125.90/MWh |
| C6 | electricity | 2022-03-31 | -23.1% | +15.0% | £361.95/MWh | £416.24/MWh |
| C8 | electricity | 2022-03-31 | -13.7% | +10.8% | £361.95/MWh | £401.16/MWh |
| C_IC2 | electricity | 2022-04-30 | -9.9% | +8.9% | £269.81/MWh | £293.91/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.9% | +7.5% | £239.42/MWh | £257.26/MWh |
| C9 | electricity | 2022-06-30 | 4.3% | +1.8% | £255.09/MWh | £259.74/MWh |
| C4 | electricity | 2022-09-30 | 7.2% | +0.4% | £404.86/MWh | £406.41/MWh |
| C4g | gas | 2022-09-30 | -19.5% | +13.8% | £183.79/MWh | £209.10/MWh |
| C7 | electricity | 2022-12-30 | 8.9% | -0.5% | £266.73/MWh | £265.49/MWh |
| C_IC3 | electricity | 2022-12-31 | -0.2% | +4.1% | £168.36/MWh | £175.27/MWh |
| C_IC3g | gas | 2022-12-31 | -38.6% | +15.0% | £101.23/MWh | £116.42/MWh |
| C6 | electricity | 2023-03-31 | -12.4% | +10.2% | £319.17/MWh | £351.72/MWh |
| C8 | electricity | 2023-03-31 | -1.7% | +4.8% | £319.17/MWh | £334.64/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.0% | +14.5% | £171.46/MWh | £196.33/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.2% | +12.6% | £163.19/MWh | £183.77/MWh |
| C9 | electricity | 2023-06-30 | -10.5% | +9.2% | £224.44/MWh | £245.16/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.09/MWh |
| C4g | gas | 2023-09-30 | -38.6% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 23.8% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -10.0% | +9.0% | £51.89/MWh | £56.57/MWh |
| C6 | electricity | 2024-03-30 | 16.3% | -4.2% | £207.71/MWh | £199.05/MWh |
| C8 | electricity | 2024-03-30 | 16.3% | -4.2% | £207.71/MWh | £199.05/MWh |
| C_IC2 | electricity | 2024-06-28 | -35.7% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -28.2% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C7 | electricity | 2024-12-29 | 0.4% | +3.8% | £243.79/MWh | £253.01/MWh |
| C_IC3 | electricity | 2024-12-30 | 18.5% | -5.0% | £116.37/MWh | £110.55/MWh |
| C_IC3g | gas | 2024-12-30 | -9.4% | +8.7% | £50.47/MWh | £54.85/MWh |
| C8 | electricity | 2025-03-30 | 8.7% | -0.4% | £284.89/MWh | £283.87/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **5** | Blind misses: **5** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 5 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £4,127.84 | deliberate: £0.00 | total: £4,127.84

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C2 | 2020-03-31 | Blind miss | 0.00 | 0.32 | Yes | £559.82 |
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.32 | Yes | £579.51 |
| C1 | 2021-12-30 | Blind miss | 0.04 | 0.32 | Yes | £-178.13 |
| C6 | 2024-03-30 | Blind miss | 0.26 | 0.38 | Yes | £2,697.78 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.32 | Yes | £468.87 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £81,155.64 | £52,415.53 | £133,571.17 | Yes |
| C1+C1g | £414.20 | £642.69 | £1,056.90 | Yes |
| C2+C2g | £377.87 | £611.34 | £989.21 | Yes |
| C3+C3g | £205.99 | £282.80 | £488.79 | Yes |
| C4+C4g | £130.92 | £-2,029.86 | £-1,898.93 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £51,922.50.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,461,253.49 across 18 billing accounts. Revenue: £14,038,573.95.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,163,026.55 | £1,913,708.99 | £18,558.96 | £866,914.06 | 27.4% |
| 2 | C_IC2 | fixed | £1,539,438.82 | £923,373.08 | £8,612.28 | £440,042.76 | 28.6% |
| 3 | C_IC3 | pass_through | £4,604,531.53 | £1,798,497.01 | £22,919.90 | £81,155.64 | 1.8% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £52,415.53 | 2.9% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £14,583.80 | 0.5% |
| 6 | C6 | fixed | £39,690.19 | £23,206.19 | £269.91 | £4,313.74 | 10.9% |
| 7 | C9 | fixed | £20,223.10 | £12,688.08 | £131.35 | £1,473.46 | 7.3% |
| 8 | C8 | fixed | £21,644.13 | £12,424.34 | £134.40 | £1,228.56 | 5.7% |
| 9 | C1g | fixed | £2,893.90 | £1,540.63 | £18.80 | £642.69 | 22.2% |
| 10 | C2g | fixed | £2,622.54 | £1,413.47 | £15.30 | £611.34 | 23.3% |
| 11 | C1 | fixed | £4,215.83 | £2,725.31 | £19.09 | £414.20 | 9.8% |
| 12 | C2 | fixed | £3,168.45 | £2,046.31 | £13.89 | £377.87 | 11.9% |
| 13 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £282.80 | 10.5% |
| 14 | C3 | fixed | £3,628.72 | £2,388.84 | £14.77 | £205.99 | 5.7% |
| 15 | C4 | fixed | £6,266.04 | £3,306.78 | £37.42 | £130.92 | 2.1% |
| 16 | C5 | fixed | £15,163.84 | £9,350.39 | £77.10 | £-61.13 | -0.4% |
| 17 | C7 | fixed | £21,787.91 | £10,810.60 | £139.90 | £-1,448.90 | -6.7% |
| 18 | C4g | fixed | £10,370.30 | £1,343.97 | £144.75 | £-2,029.86 | -19.6% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,038,574 | 100.0% |
| Wholesale cost | -£7,589,119 | 54.1% |
| **Gross supply margin** | **£6,449,455** | **45.9%** |
| Policy + Network costs | -£4,937,078 | 35.2% |
| Capital cost | -£51,123 | 0.4% |
| **Net supply margin** | **£1,461,253** | **10.4%** |

> *The ledger's `net_margin_gbp` (£6,411,405) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,051,636 | 47.6% | 11.6% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 2.9% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £54,854 | 59.4% | 7.8% | CMA 3-8% | ✓ |
| resi/elec | £80,934 | 57.3% | 2.9% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £18,570 | 30.1% | -2.7% | Ofgem CMA 2-4% | ⚠ ANOMALY |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: ANOMALIES DETECTED**
- Segment resi/gas net -2.7% (benchmark Ofgem CMA 2-4%)
## Transaction Log

Total events: 3,111,167

| Event type | Count |
|------------|-------|
| acquisition_gate_event | 1 |
| acquisition_spend_event | 5 |
| bad_debt_event | 1,443 |
| billing_event | 1,443 |
| capital_charge_event | 1,493,755 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,443 |
| payment_received_event | 1,443 |
| settlement_event | 1,610,077 |
| vat_remittance_event | 1,443 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £19,781,497.50 |
|   Less: VAT remitted to HMRC | (£952,156.45) |
| = Revenue (ex-VAT) | £18,829,341.04 |
| Less: non-commodity pass-through | (£4,777,693.84) |
| Wholesale cost (settlement events) | (£7,589,119.11) |
| Gross margin | £6,462,528.09 |
| Capital charges | (£51,123.12) |
| Net margin | £6,411,404.97 |

_Cash reconciliation: of £19,781,497.50 billed, bad debt of £395,735.80 was written off, leaving £19,385,761.69 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £6,967,825.62._

| Acquisition spend | (£1,250.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £6,404,454.97 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | £234.62 | £834.62 | £6,944.88 (45.2%) |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | £6,260.72 | £6,860.72 | £116,657.37 (33.5%) |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | £11,823.00 | £12,423.00 | £250,222.87 (41.6%) |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | £30,746.61 | £31,346.61 | £670,219.20 (40.7%) |
| 2020 | £1,887,212.43 | £431,591.09 | £631,516.48 | £824,104.87 | £38,766.02 | £39,666.02 | £782,350.45 (41.5%) |
| 2021 | £2,438,581.89 | £972,966.99 | £679,703.43 | £785,911.46 | £47,629.10 | £48,629.10 | £731,564.68 (30.0%) |
| 2022 | £4,233,999.48 | £2,384,921.21 | £799,955.65 | £1,049,122.61 | £84,099.64 | £84,699.64 | £951,222.40 (22.5%) |
| 2023 | £3,421,867.92 | £1,636,287.73 | £875,644.76 | £909,935.43 | £75,475.97 | £76,075.97 | £824,125.88 (24.1%) |
| 2024 | £3,015,720.24 | £929,842.11 | £808,470.76 | £1,277,407.37 | £64,226.63 | £65,376.63 | £1,202,410.40 (39.9%) |
| 2025 | £1,221,568.85 | £451,130.22 | £256,414.46 | £514,024.17 | £36,473.51 | £36,773.51 | £471,685.03 (38.6%) |
| **Total** | **£18,829,341.04** | | | | | | **£6,007,403.18 (31.9%)** |

**Best year:** 2024 — net £1,202,410.40 (39.9% margin)
**Worst year:** 2016 — net £6,944.88 (45.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,474,039.40 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,474,039.40** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £6,007,403.18 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,354.61 | +4.7% | £6,592.99 | £6,944.88 | +5.3% | AMBER |
| 2017 | £16,138.86 | £348,630.52 | +2060.2% | £7,252.29 | £116,657.37 | +1508.6% | RED |
| 2018 | £386,623.75 | £600,953.01 | +55.4% | £128,424.00 | £250,222.87 | +94.8% | RED |
| 2019 | £675,851.95 | £1,645,452.10 | +143.5% | £281,335.50 | £670,219.20 | +138.2% | RED |
| 2020 | £1,816,630.04 | £1,887,212.43 | +3.9% | £736,963.94 | £782,350.45 | +6.2% | AMBER |
| 2021 | £2,028,952.42 | £2,438,581.89 | +20.2% | £833,649.22 | £731,564.68 | -12.2% | AMBER |
| 2022 | £2,607,611.88 | £4,233,999.48 | +62.4% | £790,935.58 | £951,222.40 | +20.3% | RED |
| 2023 | £4,508,414.67 | £3,421,867.92 | -24.1% | £1,029,561.00 | £824,125.88 | -20.0% | RED |
| 2024 | £3,512,844.39 | £3,015,720.24 | -14.2% | £893,105.75 | £1,202,410.40 | +34.6% | RED |
| 2025 | £3,145,356.42 | £1,221,568.85 | -61.2% | £1,315,150.33 | £471,685.03 | -64.1% | RED |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 2 | 0 | 0% | £300.00 |
| 2021 | 2 | 0 | 0% | £400.00 |
| 2024 | 2 | 0 | 0% | £550.00 |

**Total:** 6 attempts, 0 wins (0% win rate), £1,250.00 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,404,454.97

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
- Average CLV (Point-in-Time, year-end 2017): £3,686.38
  - By billing account: C1 £1,866.40, C2 £3,448.52, C3 £3,029.81, C4 £2,742.22, C5 £3,908.13, C6 £7,630.18, C7 £2,786.39, C8 £4,112.60, C9 £3,653.20
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
- Average CLV (Point-in-Time, year-end 2018): £93,861.25
  - By billing account: C1 £1,719.42, C2 £3,117.96, C3 £2,735.70, C4 £2,244.33, C5 £3,848.31, C6 £5,861.07, C7 £2,579.63, C8 £3,446.77, C9 £3,434.55, C_IC1 £909,624.79
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

- Net margin: £227,872.41 (gross £702,027.61, capital £2,309.31)
  - Electricity: gross £625,973.77, capital £2,287.85, net £218,118.22
  - Gas: gross £76,053.84, capital £21.46, net £9,754.19
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
- Average CLV (Point-in-Time, year-end 2019): £126,159.83
  - By billing account: C1 £1,697.80, C2 £2,636.08, C3 £2,692.56, C4 £2,508.16, C5 £4,077.50, C6 £6,421.57, C7 £2,893.06, C8 £3,508.69, C9 £3,243.91, C_IC1 £815,715.03, C_IC2 £542,363.74
- Bill shock events (>=20%): 66 -- C1 2019-04-30 (21%); C1g 2019-01-31 (36%); C1g 2019-02-28 (26%); C1g 2019-05-31 (23%); C1g 2019-06-30 (35%); C1g 2019-10-31 (74%); C1g 2019-11-30 (43%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-01-31 (25%); C2g 2019-02-28 (26%); C2g 2019-04-30 (35%); C2g 2019-06-30 (32%); C2g 2019-07-31 (25%); C2g 2019-09-30 (30%); C2g 2019-10-31 (64%); C2g 2019-11-30 (28%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-02-28 (26%); C3g 2019-06-30 (33%); C3g 2019-07-31 (35%); C3g 2019-09-30 (35%); C3g 2019-10-31 (64%); C3g 2019-11-30 (31%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (31%); C4 2019-09-30 (25%); C4 2019-11-30 (26%); C4g 2019-01-31 (30%); C4g 2019-02-28 (25%); C4g 2019-05-31 (21%); C4g 2019-06-30 (33%); C4g 2019-07-31 (37%); C4g 2019-09-30 (31%); C4g 2019-10-31 (34%); C4g 2019-11-30 (35%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 10 at risk (≥20% churn prob): C1 35%, C2 29%, C3 32%, C4 38%, C5 38%, C6 29%, C7 35%, C8 38%, C9 32%, C_IC1 23%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£149.68/MWh, net margin £93.91
- C1g (gas): tariff £25.33-£36.05/MWh, net margin £144.51
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £127.48
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £121.37
- C3 (electricity): tariff £120.68-£126.90/MWh, net margin £25.68
- C3g (gas): tariff £23.00-£28.80/MWh, net margin £83.28
- C4 (electricity): tariff £126.76-£149.37/MWh, net margin £101.72
- C4g (gas): tariff £19.47-£33.61/MWh, net margin £78.41
- C5 (electricity): tariff £126.10-£153.39/MWh, net margin £121.02
- C6 (electricity): tariff £142.17-£148.72/MWh, net margin £92.86
- C7 (electricity): tariff £99.69-£221.28/MWh, net margin £71.68
- C8 (electricity): tariff £105.12-£211.40/MWh, net margin £154.84
- C9 (electricity): tariff £98.80-£198.38/MWh, net margin £145.35
- C_IC1 (electricity): tariff £0.00-£263.70/MWh, net margin £137,538.19
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £78,289.55
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £1,355.95
- C_IC3g (gas): tariff £27.53/MWh, net margin £9,326.63

**Portfolio Health**

- Capital cost ratio: 0.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.824, average bill shock 17.1%, bad debt provision £6,207.40, avg complaint probability 4.7%
- Solvency signal: £217,201/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £252,589.91 vs. naked (unhedged) net margin: £836,841.98
- hedging cost £584,252.07 vs. a fully unhedged book (commodity-only: actual net £252,589.91 vs. naked net £836,841.98)
  - C1: actual £75.37 vs. naked £487.42 -- hedging cost £412.06
  - C1g: actual £137.12 vs. naked £302.41 -- hedging cost £165.30
  - C2: actual £157.29 vs. naked £663.14 -- hedging cost £505.85
  - C2g: actual £93.46 vs. naked £403.54 -- hedging cost £310.08
  - C3: actual £35.26 vs. naked £668.43 -- hedging cost £633.17
  - C3g: actual £135.78 vs. naked £505.74 -- hedging cost £369.96
  - C4: actual £104.15 vs. naked £443.69 -- hedging cost £339.54
  - C4g: actual £101.34 vs. naked £573.92 -- hedging cost £472.58
  - C5: actual £-27.61 vs. naked £1,590.08 -- hedging cost £1,617.69
  - C6: actual £233.55 vs. naked £2,599.80 -- hedging cost £2,366.24
  - C7: actual £56.98 vs. naked £1,146.66 -- hedging cost £1,089.68
  - C8: actual £240.89 vs. naked £1,370.83 -- hedging cost £1,129.94
  - C9: actual £159.29 vs. naked £1,258.35 -- hedging cost £1,099.06
  - C_IC1: actual £154,845.76 vs. naked £297,973.82 -- hedging cost £143,128.05
  - C_IC2: actual £85,558.69 vs. naked £161,523.27 -- hedging cost £75,964.58
  - C_IC3: actual £1,355.95 vs. naked £289,938.26 -- hedging cost £288,582.30
  - C_IC3g: actual £9,326.63 vs. naked £75,392.62 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £227,872.41 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £153,032.39 (gross £822,447.79, capital £2,088.40)
  - Electricity: gross £745,485.04, capital £2,079.49, net £143,287.45
  - Gas: gross £76,962.75, capital £8.92, net £9,744.94
- Treasury at year end: £2,914,252.99
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.86 (avg 0.86), C7 0.88 (avg 0.88), C8 0.86 (avg 0.86), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2020-03-16 period 20, net margin £-18.66

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C2, C3
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £188,595.00
  - By billing account: C1 £2,034.59, C2 £2,294.14, C3 £2,586.03, C4 £2,582.20, C5 £4,517.94, C6 £7,623.25, C7 £3,145.02, C8 £4,073.66, C9 £3,787.92, C_IC1 £576,736.84, C_IC2 £293,544.83, C_IC3 £1,010,362.98, C_IC4 £538,445.61
- Bill shock events (>=20%): 47 -- C1g 2020-01-31 (21%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-31 (35%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (35%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (48%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (21%); C4 2020-11-30 (24%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (49%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (91%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 10 at risk (≥20% churn prob): C1 29%, C2 32%, C3 32%, C4 32%, C5 35%, C6 32%, C7 35%, C8 38%, C9 41%, C_IC2 20%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£130.41/MWh, net margin £74.96
- C1g (gas): tariff £25.00-£25.33/MWh, net margin £137.20
- C2 (electricity): tariff £151.90/MWh, net margin £41.32
- C2g (gas): tariff £26.00/MWh, net margin £25.58
- C3 (electricity): tariff £120.68/MWh, net margin £16.44
- C3g (gas): tariff £23.00/MWh, net margin £75.08
- C4 (electricity): tariff £120.39-£126.76/MWh, net margin £84.40
- C4g (gas): tariff £16.09-£19.47/MWh, net margin £71.92
- C5 (electricity): tariff £126.10-£134.32/MWh, net margin £-30.91 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.72/MWh, net margin £366.13
- C7 (electricity): tariff £99.69-£212.48/MWh, net margin £58.29
- C8 (electricity): tariff £110.73-£215.83/MWh, net margin £365.81
- C9 (electricity): tariff £84.67-£188.63/MWh, net margin £112.35
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £83,074.42
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £43,546.80
- C_IC3 (electricity): tariff £37.49-£80.95/MWh, net margin £11,007.15
- C_IC3g (gas): tariff £15.44-£19.98/MWh, net margin £9,435.16
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £4,570.28

**Portfolio Health**

- Capital cost ratio: 0.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 186, average clarity 0.830, average bill shock 14.4%, bad debt provision £6,434.09, avg complaint probability 4.3%
- Solvency signal: £224,173/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £126,136.42 vs. naked (unhedged) net margin: £1,004,396.90
- hedging cost £878,260.48 vs. a fully unhedged book (commodity-only: actual net £126,136.42 vs. naked net £1,004,396.90)
  - C1: actual £-27.35 vs. naked £88.09 -- hedging cost £115.44
  - C1g: actual £22.28 vs. naked £-68.18 -- hedging added £90.47
  - C4: actual £17.11 vs. naked £226.84 -- hedging cost £209.73
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C5: actual £-365.46 vs. naked £145.23 -- hedging cost £510.69
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-114.05 vs. naked £325.31 -- hedging cost £439.36
  - C8: actual £385.72 vs. naked £1,216.68 -- hedging cost £830.96
  - C9: actual £-30.07 vs. naked £685.91 -- hedging cost £715.98
  - C_IC1: actual £73,597.25 vs. naked £169,702.73 -- hedging cost £96,105.47
  - C_IC2: actual £42,303.73 vs. naked £96,422.44 -- hedging cost £54,118.71
  - C_IC3: actual £-15,754.85 vs. naked £221,281.26 -- hedging cost £237,036.11
  - C_IC3g: actual £17,934.51 vs. naked £159,245.07 -- hedging cost £141,310.56
  - C_IC4: actual £7,886.99 vs. naked £352,832.81 -- hedging cost £344,945.82

**Year narrative:** 2020 produced a net gain of £153,032.39 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 47 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £87,129.50 (gross £784,501.09, capital £5,717.68)
  - Electricity: gross £702,023.97, capital £5,705.82, net £78,922.24
  - Gas: gross £82,477.12, capital £11.86, net £8,207.26
- Treasury at year end: £2,983,493.32
- Hedge fraction at first renewal this year (avg across year's terms): C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.91 (avg 0.91), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2021-11-24 period 30, net margin £-74.55

**Customer Book**

- Active accounts: 14 (C1, C1g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2021): £185,416.55
  - By billing account: C1 £2,042.23, C2 £2,356.99, C3 £2,458.40, C4 £2,267.90, C5 £4,261.36, C6 £7,289.32, C7 £3,423.59, C8 £4,066.88, C9 £3,661.53, C_IC1 £532,150.82, C_IC2 £314,544.40, C_IC3 £970,054.62, C_IC4 £561,837.14
- Bill shock events (>=20%): 47 -- C1g 2021-05-31 (28%); C1g 2021-06-30 (45%); C1g 2021-10-31 (55%); C1g 2021-11-30 (53%); C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (21%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (22%); C4 2021-10-31 (49%); C4 2021-11-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-04-30 (25%); C_IC1 2021-05-31 (39%); C_IC2 2021-03-31 (22%); C_IC2 2021-04-30 (93%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%)
- Churn risk (accounts renewing in 2021): 10 at risk (≥20% churn prob): C1 32%, C4 35%, C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC2 23%, C_IC3 20%, C_IC4 29%

**Pricing & Margin**

- C1 (electricity): tariff £130.41/MWh, net margin £-27.01 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £21.95
- C4 (electricity): tariff £120.39-£183.00/MWh, net margin £-64.23 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-334.91 -- **net-negative**
- C5 (electricity): tariff £134.32/MWh, net margin £-361.42 -- **net-negative**
- C6 (electricity): tariff £143.89-£201.11/MWh, net margin £585.08
- C7 (electricity): tariff £111.30-£274.50/MWh, net margin £-123.77 -- **net-negative**
- C8 (electricity): tariff £113.06-£274.50/MWh, net margin £358.15
- C9 (electricity): tariff £84.67-£263.17/MWh, net margin £-23.96 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £34,804.69
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £67,345.13
- C_IC3 (electricity): tariff £42.40-£390.56/MWh, net margin £-26,895.06 -- **net-negative**
- C_IC3g (gas): tariff £19.98-£125.90/MWh, net margin £8,520.22
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £3,324.66

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.826, average bill shock 16.1%, bad debt provision £9,165.93, avg complaint probability 4.6%
- Solvency signal: £271,227/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £202,760.86 vs. naked (unhedged) net margin: £468,485.56
- hedging cost £265,724.70 vs. a fully unhedged book (commodity-only: actual net £202,760.86 vs. naked net £468,485.56)
  - C4: actual £-220.41 vs. naked £-170.34 -- hedging cost £50.07
  - C4g: actual £-901.21 vs. naked £-1,344.38 -- hedging added £443.17
  - C6: actual £599.03 vs. naked £361.28 -- hedging added £237.75
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-57.61 vs. naked £-194.40 -- hedging added £136.78
  - C_IC1: actual £25,203.57 vs. naked £-64,186.08 -- hedging added £89,389.65
  - C_IC2: actual £78,799.11 vs. naked £38,176.83 -- hedging added £40,622.29
  - C_IC3: actual £98,643.53 vs. naked £233,100.50 -- hedging cost £134,456.97
  - C_IC3g: actual £4,142.87 vs. naked £85,199.40 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £178,304.23 -- hedging cost £180,207.49

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £87,129.50 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 47 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £303,662.24 (gross £1,048,001.44, capital £13,200.57)
  - Electricity: gross £957,717.40, capital £13,167.76, net £300,811.94
  - Gas: gross £90,284.04, capital £32.81, net £2,850.30
- Treasury at year end: £3,190,740.16
- Hedge fraction at first renewal this year (avg across year's terms): C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,091,790.81, C6->1.00, C8->1.00, C_IC1->1.00, VaR (current £56,060.50 / stressed £20,778.40) ratio 2.70
  - 2022-05-29: treasury £3,091,894.79, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,169.42 / stressed £20,807.27) ratio 2.70
  - 2022-06-28: treasury £3,091,889.12, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,169.42 / stressed £20,807.27) ratio 2.70
  - 2022-07-28: treasury £3,091,696.47, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,231.40 / stressed £20,819.81) ratio 2.70
  - 2022-08-27: treasury £3,091,686.87, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, VaR (current £56,231.40 / stressed £20,819.81) ratio 2.70
  - 2022-09-26: treasury £3,091,671.42, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,231.40 / stressed £20,819.81) ratio 2.70
  - 2022-10-26: treasury £3,089,385.48, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,292.84 / stressed £20,829.96) ratio 2.70
  - 2022-11-25: treasury £3,089,235.07, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,292.84 / stressed £20,829.96) ratio 2.70
  - 2022-12-25: treasury £3,088,968.88, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,292.84 / stressed £20,829.96) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC1 on 2022-01-24 period 26, net margin £-88.66

**Customer Book**

- Active accounts: 11 (C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 4, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £197,292.16
  - By billing account: C1 £2,033.60, C2 £2,343.14, C3 £2,442.45, C4 £1,528.55, C5 £4,247.85, C6 £7,927.26, C7 £2,724.09, C8 £3,997.66, C9 £3,698.51, C_IC1 £564,101.48, C_IC2 £335,668.74, C_IC3 £1,074,307.83, C_IC4 £559,776.91
- Bill shock events (>=20%): 56 -- C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (108%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%)
- Churn risk (accounts renewing in 2022): 8 at risk (≥20% churn prob): C4 38%, C6 32%, C7 35%, C8 35%, C9 38%, C_IC1 20%, C_IC3 23%, C_IC4 32%

**Pricing & Margin**

- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-276.94 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,284.53 -- **net-negative**
- C6 (electricity): tariff £201.11-£416.24/MWh, net margin £987.68
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,827.01 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-285.40 -- **net-negative**
- C9 (electricity): tariff £137.85-£389.61/MWh, net margin £-121.71 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£463.07/MWh, net margin £130,656.99
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £75,926.31
- C_IC3 (electricity): tariff £137.72-£390.56/MWh, net margin £97,659.96
- C_IC3g (gas): tariff £116.42-£125.90/MWh, net margin £4,134.82
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £-1,907.93 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,490,337.78 -> £3,088,937.96 (11.5%)
- Bills issued: 132, average clarity 0.794, average bill shock 22.0%, bad debt provision £35,373.03, avg complaint probability 5.5%
- Solvency signal: £354,527/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £141,105.59 vs. naked (unhedged) net margin: £1,161,061.78
- hedging cost £1,019,956.19 vs. a fully unhedged book (commodity-only: actual net £141,105.59 vs. naked net £1,161,061.78)
  - C4: actual £-277.33 vs. naked £595.36 -- hedging cost £872.70
  - C4g: actual £-1,950.48 vs. naked £1,336.80 -- hedging cost £3,287.28
  - C6: actual £1,338.15 vs. naked £4,212.15 -- hedging cost £2,874.00
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-481.87 vs. naked £1,102.92 -- hedging cost £1,584.78
  - C9: actual £-48.83 vs. naked £1,012.79 -- hedging cost £1,061.62
  - C_IC1: actual £212,889.80 vs. naked £251,173.84 -- hedging cost £38,284.04
  - C_IC2: actual £86,770.64 vs. naked £126,067.12 -- hedging cost £39,296.49
  - C_IC3: actual £-168,675.16 vs. naked £444,921.16 -- hedging cost £613,596.32
  - C_IC3g: actual £8,513.79 vs. naked £123,301.26 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £205,056.67 -- hedging cost £201,583.86

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £303,662.24 across 11 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 56 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £88,291.65 (gross £908,996.93, capital £9,733.58)
  - Electricity: gross £788,056.82, capital £9,681.15, net £80,929.70
  - Gas: gross £120,940.11, capital £52.42, net £7,361.94
- Treasury at year end: £3,332,123.10
- Hedge fraction at first renewal this year (avg across year's terms): C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.93 (avg 0.93), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,190,852.51, C4->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,074.63 / stressed £44,286.67) ratio 2.76
  - 2023-02-23: treasury £3,190,992.42, C4->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,074.63 / stressed £44,286.67) ratio 2.76
  - 2023-03-25: treasury £3,191,134.86, C4->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,074.63 / stressed £44,286.67) ratio 2.76
  - 2023-04-24: treasury £3,269,520.42, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £127,898.24 / stressed £48,770.20) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C_IC1 on 2023-06-16 period 22, net margin £-21.69

**Customer Book**

- Active accounts: 11 (C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 4, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2023): £203,085.82
  - By billing account: C1 £2,075.14, C2 £2,410.26, C3 £2,566.65, C4 £1,156.74, C5 £4,593.57, C6 £8,819.29, C7 £2,833.45, C8 £4,309.68, C9 £3,969.74, C_IC1 £645,854.05, C_IC2 £364,977.40, C_IC3 £1,027,755.56, C_IC4 £568,794.19
- Bill shock events (>=20%): 39 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (30%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (25%); C4 2023-04-30 (29%); C4 2023-09-30 (24%); C4 2023-11-30 (27%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (46%); C4g 2023-11-30 (63%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (52%); C_IC2 2023-06-30 (100%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%)
- Churn risk (accounts renewing in 2023): 7 at risk (≥20% churn prob): C4 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC3 20%, C_IC4 26%

**Pricing & Margin**

- C4 (electricity): tariff £249.37-£305.00/MWh, net margin £-68.64 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,164.32 -- **net-negative**
- C6 (electricity): tariff £351.72-£416.24/MWh, net margin £1,615.51
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-443.76 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-111.16 -- **net-negative**
- C9 (electricity): tariff £192.63-£389.61/MWh, net margin £226.68
- C_IC1 (electricity): tariff £-60.00-£463.07/MWh, net margin £160,070.92
- C_IC2 (electricity): tariff £-186.24-£475.91/MWh, net margin £83,774.51
- C_IC3 (electricity): tariff £100.48-£262.91/MWh, net margin £-167,614.59 -- **net-negative**
- C_IC3g (gas): tariff £56.57-£116.42/MWh, net margin £8,526.27
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £3,480.25

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): 47 -- £3,728,895.02 -> £3,332,117.97 (10.6%); £3,728,895.17 -> £3,332,118.01 (10.6%); £3,728,895.32 -> £3,332,118.05 (10.6%); £3,728,895.47 -> £3,332,118.08 (10.6%); £3,728,895.63 -> £3,332,118.12 (10.6%); £3,728,895.78 -> £3,332,118.16 (10.6%); £3,728,895.93 -> £3,332,118.20 (10.6%); £3,728,896.09 -> £3,332,118.24 (10.6%); £3,728,896.24 -> £3,332,118.28 (10.6%); £3,728,896.40 -> £3,332,118.31 (10.6%); £3,728,896.56 -> £3,332,118.35 (10.6%); £3,728,896.71 -> £3,332,118.56 (10.6%); £3,728,896.87 -> £3,332,118.77 (10.6%); £3,728,897.04 -> £3,332,118.97 (10.6%); £3,728,897.23 -> £3,332,119.16 (10.6%); £3,728,897.44 -> £3,332,119.37 (10.6%); £3,728,897.66 -> £3,332,119.58 (10.6%); £3,728,897.90 -> £3,332,119.80 (10.6%); £3,728,898.17 -> £3,332,120.02 (10.6%); £3,728,898.42 -> £3,332,120.07 (10.6%); £3,728,898.69 -> £3,332,120.12 (10.6%); £3,728,898.94 -> £3,332,120.17 (10.6%); £3,728,899.20 -> £3,332,120.22 (10.6%); £3,728,899.46 -> £3,332,120.27 (10.6%); £3,728,899.72 -> £3,332,120.32 (10.6%); £3,728,899.99 -> £3,332,120.36 (10.6%); £3,728,900.26 -> £3,332,120.41 (10.6%); £3,728,900.51 -> £3,332,120.46 (10.6%); £3,728,900.77 -> £3,332,120.51 (10.6%); £3,728,901.02 -> £3,332,120.55 (10.6%); £3,728,901.28 -> £3,332,120.60 (10.6%); £3,728,901.53 -> £3,332,120.65 (10.6%); £3,728,901.80 -> £3,332,120.86 (10.6%); £3,728,902.05 -> £3,332,121.07 (10.6%); £3,728,902.31 -> £3,332,121.28 (10.6%); £3,728,902.57 -> £3,332,121.49 (10.6%); £3,728,902.83 -> £3,332,121.71 (10.6%); £3,728,903.09 -> £3,332,121.93 (10.6%); £3,728,903.36 -> £3,332,122.14 (10.6%); £3,728,903.62 -> £3,332,122.35 (10.6%); £3,728,903.88 -> £3,332,122.56 (10.6%); £3,728,904.14 -> £3,332,122.75 (10.6%); £3,728,904.40 -> £3,332,122.95 (10.6%); £3,728,904.66 -> £3,332,122.99 (10.6%); £3,728,904.92 -> £3,332,123.03 (10.6%); £3,728,905.17 -> £3,332,123.07 (10.6%); £3,728,905.38 -> £3,332,123.10 (10.6%)
- Bills issued: 132, average clarity 0.813, average bill shock 16.8%, bad debt provision £13,707.32, avg complaint probability 4.7%
- Solvency signal: £370,236/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £401,659.92 vs. naked (unhedged) net margin: £1,238,873.84
- hedging cost £837,213.91 vs. a fully unhedged book (commodity-only: actual net £401,659.92 vs. naked net £1,238,873.84)
  - C4: actual £314.09 vs. naked £700.29 -- hedging cost £386.20
  - C4g: actual £529.39 vs. naked £1,048.79 -- hedging cost £519.40
  - C6: actual £1,829.34 vs. naked £5,502.90 -- hedging cost £3,673.56
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £140.61 vs. naked £1,972.23 -- hedging cost £1,831.62
  - C9: actual £626.86 vs. naked £2,130.53 -- hedging cost £1,503.68
  - C_IC1: actual £141,718.53 vs. naked £284,593.49 -- hedging cost £142,874.95
  - C_IC2: actual £92,980.73 vs. naked £161,022.73 -- hedging cost £68,042.00
  - C_IC3: actual £150,674.78 vs. naked £424,678.49 -- hedging cost £274,003.71
  - C_IC3g: actual £8,660.26 vs. naked £123,107.25 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £232,127.67 -- hedging cost £228,435.92

**Year narrative:** 2023 produced a net gain of £88,291.65 across 11 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 39 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £357,551.17 (gross £1,277,215.55, capital £9,620.34)
  - Electricity: gross £1,152,801.68, capital £9,596.94, net £348,469.34
  - Gas: gross £124,413.88, capital £23.40, net £9,081.83
- Treasury at year end: £3,732,742.14
- Hedge fraction at first renewal this year (avg across year's terms): C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2024-06-28 period 31, net margin £-26.25

**Customer Book**

- Active accounts: 11 (C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 4, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2024): £228,753.15
  - By billing account: C1 £2,081.42, C2 £2,634.75, C3 £2,590.58, C4 £1,546.23, C5 £4,242.06, C6 £9,206.96, C7 £3,203.73, C8 £4,815.58, C9 £4,262.49, C_IC1 £736,756.68, C_IC2 £388,212.19, C_IC3 £1,154,175.83, C_IC4 £660,062.52
- Bill shock events (>=20%): 26 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (35%); C8 2024-05-31 (47%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (30%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%)
- Churn risk (accounts renewing in 2024): 5 at risk (≥20% churn prob): C4 32%, C6 38%, C7 35%, C8 41%, C9 38%

**Pricing & Margin**

- C4 (electricity): tariff £249.37/MWh, net margin £235.27
- C4g (gas): tariff £66.00/MWh, net margin £396.91
- C6 (electricity): tariff £351.72/MWh, net margin £632.92
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £492.80
- C8 (electricity): tariff £156.40-£397.50/MWh, net margin £241.32
- C9 (electricity): tariff £165.00-£367.74/MWh, net margin £560.84
- C_IC1 (electricity): tariff £-98.58-£330.78/MWh, net margin £123,551.44
- C_IC2 (electricity): tariff £-106.92-£353.39/MWh, net margin £68,337.22
- C_IC3 (electricity): tariff £86.86-£191.82/MWh, net margin £150,718.40
- C_IC3g (gas): tariff £54.85-£56.57/MWh, net margin £8,684.92
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £3,699.12

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): 4271 -- £3,728,905.76 -> £3,332,123.18 (10.6%); £3,728,905.94 -> £3,332,123.23 (10.6%); £3,728,906.11 -> £3,332,123.27 (10.6%); £3,728,906.29 -> £3,332,123.31 (10.6%); £3,728,906.45 -> £3,332,123.35 (10.6%); £3,728,906.63 -> £3,332,123.39 (10.6%); £3,728,906.80 -> £3,332,123.43 (10.6%); £3,728,906.97 -> £3,332,123.47 (10.6%); £3,728,907.15 -> £3,332,123.52 (10.6%); £3,728,907.32 -> £3,332,123.56 (10.6%); £3,728,907.50 -> £3,332,123.60 (10.6%); £3,728,907.67 -> £3,332,123.82 (10.6%); £3,728,907.84 -> £3,332,124.04 (10.6%); £3,728,908.03 -> £3,332,124.28 (10.6%); £3,728,908.23 -> £3,332,124.53 (10.6%); £3,728,908.46 -> £3,332,124.83 (10.6%); £3,728,908.71 -> £3,332,125.13 (10.6%); £3,728,908.97 -> £3,332,125.46 (10.6%); £3,728,909.25 -> £3,332,125.81 (10.6%); £3,728,909.53 -> £3,332,125.96 (10.6%); £3,728,909.82 -> £3,332,126.11 (10.6%); £3,728,910.11 -> £3,332,126.25 (10.6%); £3,728,910.41 -> £3,332,126.40 (10.6%); £3,728,910.69 -> £3,332,126.55 (10.6%); £3,728,910.98 -> £3,332,126.71 (10.6%); £3,728,911.27 -> £3,332,126.84 (10.6%); £3,728,911.55 -> £3,332,126.98 (10.6%); £3,728,911.83 -> £3,332,127.11 (10.6%); £3,728,912.10 -> £3,332,127.25 (10.6%); £3,728,912.39 -> £3,332,127.39 (10.6%); £3,728,912.67 -> £3,332,127.52 (10.6%); £3,728,912.96 -> £3,332,127.66 (10.6%); £3,728,913.24 -> £3,332,128.01 (10.6%); £3,728,913.53 -> £3,332,128.32 (10.6%); £3,728,913.75 -> £3,332,128.60 (10.6%); £3,728,913.96 -> £3,332,128.85 (10.6%); £3,728,914.18 -> £3,332,129.11 (10.6%); £3,728,914.48 -> £3,332,129.36 (10.6%); £3,728,914.77 -> £3,332,129.60 (10.6%); £3,728,915.05 -> £3,332,129.85 (10.6%); £3,728,915.34 -> £3,332,130.09 (10.6%); £3,728,915.63 -> £3,332,130.32 (10.6%); £3,728,915.92 -> £3,332,130.55 (10.6%); £3,728,916.21 -> £3,332,130.60 (10.6%); £3,728,916.50 -> £3,332,130.65 (10.6%); £3,728,916.76 -> £3,332,130.70 (10.6%); £3,728,917.00 -> £3,332,130.74 (10.6%); £3,728,917.22 -> £3,332,130.79 (10.6%); £3,728,917.40 -> £3,332,130.83 (10.6%); £3,728,917.57 -> £3,332,130.88 (10.6%); £3,728,917.74 -> £3,332,130.92 (10.6%); £3,728,917.91 -> £3,332,130.97 (10.6%); £3,728,918.08 -> £3,332,131.01 (10.6%); £3,728,918.25 -> £3,332,131.05 (10.6%); £3,728,918.42 -> £3,332,131.10 (10.6%); £3,728,918.59 -> £3,332,131.14 (10.6%); £3,728,918.76 -> £3,332,131.19 (10.6%); £3,728,918.93 -> £3,332,131.23 (10.6%); £3,728,919.10 -> £3,332,131.28 (10.6%); £3,728,919.27 -> £3,332,131.47 (10.6%); £3,728,919.44 -> £3,332,131.67 (10.6%); £3,728,919.62 -> £3,332,131.88 (10.6%); £3,728,919.83 -> £3,332,132.11 (10.6%); £3,728,920.06 -> £3,332,132.36 (10.6%); £3,728,920.29 -> £3,332,132.65 (10.6%); £3,728,920.54 -> £3,332,132.97 (10.6%); £3,728,920.82 -> £3,332,133.30 (10.6%); £3,728,921.10 -> £3,332,133.45 (10.6%); £3,728,921.38 -> £3,332,133.60 (10.6%); £3,728,921.67 -> £3,332,133.75 (10.6%); £3,728,921.95 -> £3,332,133.91 (10.6%); £3,728,922.23 -> £3,332,134.06 (10.6%); £3,728,922.50 -> £3,332,134.21 (10.6%); £3,728,922.78 -> £3,332,134.34 (10.6%); £3,728,923.07 -> £3,332,134.48 (10.6%); £3,728,923.34 -> £3,332,134.62 (10.6%); £3,728,923.62 -> £3,332,134.75 (10.6%); £3,728,923.89 -> £3,332,134.89 (10.6%); £3,728,924.17 -> £3,332,135.02 (10.6%); £3,728,924.45 -> £3,332,135.14 (10.6%); £3,728,924.66 -> £3,332,135.44 (10.6%); £3,728,924.87 -> £3,332,135.72 (10.6%); £3,728,925.08 -> £3,332,135.96 (10.6%); £3,728,925.30 -> £3,332,136.18 (10.6%); £3,728,925.51 -> £3,332,136.38 (10.6%); £3,728,925.72 -> £3,332,136.58 (10.6%); £3,728,925.93 -> £3,332,136.78 (10.6%); £3,728,926.21 -> £3,332,136.98 (10.6%); £3,728,926.50 -> £3,332,137.18 (10.6%); £3,728,926.78 -> £3,332,137.37 (10.6%); £3,728,927.06 -> £3,332,137.56 (10.6%); £3,728,927.35 -> £3,332,137.61 (10.6%); £3,728,927.63 -> £3,332,137.65 (10.6%); £3,728,927.89 -> £3,332,137.70 (10.6%); £3,728,928.12 -> £3,332,137.74 (10.6%); £3,728,928.34 -> £3,332,137.78 (10.6%); £3,728,928.51 -> £3,332,137.82 (10.6%); £3,728,928.69 -> £3,332,137.86 (10.6%); £3,728,928.85 -> £3,332,137.90 (10.6%); £3,728,929.02 -> £3,332,137.94 (10.6%); £3,728,929.19 -> £3,332,137.99 (10.6%); £3,728,929.36 -> £3,332,138.03 (10.6%); £3,728,929.53 -> £3,332,138.07 (10.6%); £3,728,929.70 -> £3,332,138.11 (10.6%); £3,728,929.87 -> £3,332,138.15 (10.6%); £3,728,930.04 -> £3,332,138.20 (10.6%); £3,728,930.21 -> £3,332,138.24 (10.6%); £3,728,930.38 -> £3,332,138.46 (10.6%); £3,728,930.55 -> £3,332,138.69 (10.6%); £3,728,930.74 -> £3,332,138.93 (10.6%); £3,728,930.94 -> £3,332,139.20 (10.6%); £3,728,931.17 -> £3,332,139.49 (10.6%); £3,728,931.42 -> £3,332,139.78 (10.6%); £3,728,931.68 -> £3,332,140.10 (10.6%); £3,728,931.96 -> £3,332,140.42 (10.6%); £3,728,932.24 -> £3,332,140.57 (10.6%); £3,728,932.53 -> £3,332,140.72 (10.6%); £3,728,932.81 -> £3,332,140.86 (10.6%); £3,728,933.09 -> £3,332,141.01 (10.6%); £3,728,933.39 -> £3,332,141.16 (10.6%); £3,728,933.68 -> £3,332,141.30 (10.6%); £3,728,933.97 -> £3,332,141.44 (10.6%); £3,728,934.25 -> £3,332,141.57 (10.6%); £3,728,934.52 -> £3,332,141.71 (10.6%); £3,728,934.80 -> £3,332,141.85 (10.6%); £3,728,935.09 -> £3,332,141.99 (10.6%); £3,728,935.36 -> £3,332,142.13 (10.6%); £3,728,935.64 -> £3,332,142.26 (10.6%); £3,728,935.93 -> £3,332,142.59 (10.6%); £3,728,936.14 -> £3,332,142.90 (10.6%); £3,728,936.42 -> £3,332,143.17 (10.6%); £3,728,936.63 -> £3,332,143.41 (10.6%); £3,728,936.84 -> £3,332,143.64 (10.6%); £3,728,937.06 -> £3,332,143.87 (10.6%); £3,728,937.27 -> £3,332,144.10 (10.6%); £3,728,937.55 -> £3,332,144.33 (10.6%); £3,728,937.83 -> £3,332,144.56 (10.6%); £3,728,938.11 -> £3,332,144.78 (10.6%); £3,728,938.38 -> £3,332,144.98 (10.6%); £3,728,938.67 -> £3,332,145.03 (10.6%); £3,728,938.97 -> £3,332,145.07 (10.6%); £3,728,939.22 -> £3,332,145.12 (10.6%); £3,728,939.45 -> £3,332,145.16 (10.6%); £3,728,939.67 -> £3,332,145.20 (10.6%); £3,728,939.84 -> £3,332,145.24 (10.6%); £3,728,940.00 -> £3,332,145.29 (10.6%); £3,728,940.16 -> £3,332,145.33 (10.6%); £3,728,940.34 -> £3,332,145.37 (10.6%); £3,728,940.50 -> £3,332,145.41 (10.6%); £3,728,940.67 -> £3,332,145.46 (10.6%); £3,728,940.84 -> £3,332,145.50 (10.6%); £3,728,941.01 -> £3,332,145.54 (10.6%); £3,728,941.17 -> £3,332,145.59 (10.6%); £3,728,941.35 -> £3,332,145.63 (10.6%); £3,728,941.51 -> £3,332,145.68 (10.6%); £3,728,941.69 -> £3,332,145.92 (10.6%); £3,728,941.86 -> £3,332,146.17 (10.6%); £3,728,942.04 -> £3,332,146.44 (10.6%); £3,728,942.24 -> £3,332,146.72 (10.6%); £3,728,942.46 -> £3,332,147.01 (10.6%); £3,728,942.70 -> £3,332,147.34 (10.6%); £3,728,942.97 -> £3,332,147.71 (10.6%); £3,728,943.25 -> £3,332,148.08 (10.6%); £3,728,943.52 -> £3,332,148.24 (10.6%); £3,728,943.80 -> £3,332,148.39 (10.6%); £3,728,944.08 -> £3,332,148.54 (10.6%); £3,728,944.36 -> £3,332,148.69 (10.6%); £3,728,944.63 -> £3,332,148.84 (10.6%); £3,728,944.91 -> £3,332,148.98 (10.6%); £3,728,945.18 -> £3,332,149.11 (10.6%); £3,728,945.46 -> £3,332,149.25 (10.6%); £3,728,945.74 -> £3,332,149.38 (10.6%); £3,728,946.02 -> £3,332,149.52 (10.6%); £3,728,946.30 -> £3,332,149.65 (10.6%); £3,728,946.57 -> £3,332,149.78 (10.6%); £3,728,946.85 -> £3,332,149.90 (10.6%); £3,728,947.06 -> £3,332,150.26 (10.6%); £3,728,947.34 -> £3,332,150.60 (10.6%); £3,728,947.61 -> £3,332,150.88 (10.6%); £3,728,947.81 -> £3,332,151.16 (10.6%); £3,728,948.08 -> £3,332,151.42 (10.6%); £3,728,948.36 -> £3,332,151.66 (10.6%); £3,728,948.58 -> £3,332,151.90 (10.6%); £3,728,948.87 -> £3,332,152.14 (10.6%); £3,728,949.14 -> £3,332,152.39 (10.6%); £3,728,949.42 -> £3,332,152.62 (10.6%); £3,728,949.70 -> £3,332,152.85 (10.6%); £3,728,949.98 -> £3,332,152.90 (10.6%); £3,728,950.25 -> £3,332,152.95 (10.6%); £3,728,950.51 -> £3,332,152.99 (10.6%); £3,728,950.75 -> £3,332,153.03 (10.6%); £3,728,950.96 -> £3,332,153.07 (10.6%); £3,728,951.13 -> £3,332,153.11 (10.6%); £3,728,951.29 -> £3,332,153.16 (10.6%); £3,728,951.45 -> £3,332,153.20 (10.6%); £3,728,951.61 -> £3,332,153.24 (10.6%); £3,728,951.76 -> £3,332,153.28 (10.6%); £3,728,951.93 -> £3,332,153.33 (10.6%); £3,728,952.09 -> £3,332,153.37 (10.6%); £3,728,952.25 -> £3,332,153.41 (10.6%); £3,728,952.41 -> £3,332,153.45 (10.6%); £3,728,952.58 -> £3,332,153.50 (10.6%); £3,728,952.75 -> £3,332,153.54 (10.6%); £3,728,952.91 -> £3,332,153.81 (10.6%); £3,728,953.06 -> £3,332,154.07 (10.6%); £3,728,953.24 -> £3,332,154.36 (10.6%); £3,728,953.44 -> £3,332,154.66 (10.6%); £3,728,953.65 -> £3,332,154.99 (10.6%); £3,728,953.89 -> £3,332,155.33 (10.6%); £3,728,954.14 -> £3,332,155.70 (10.6%); £3,728,954.42 -> £3,332,156.08 (10.6%); £3,728,954.69 -> £3,332,156.23 (10.6%); £3,728,954.96 -> £3,332,156.37 (10.6%); £3,728,955.22 -> £3,332,156.53 (10.6%); £3,728,955.49 -> £3,332,156.68 (10.6%); £3,728,955.77 -> £3,332,156.84 (10.6%); £3,728,956.04 -> £3,332,156.98 (10.6%); £3,728,956.31 -> £3,332,157.12 (10.6%); £3,728,956.58 -> £3,332,157.26 (10.6%); £3,728,956.84 -> £3,332,157.40 (10.6%); £3,728,957.11 -> £3,332,157.54 (10.6%); £3,728,957.38 -> £3,332,157.67 (10.6%); £3,728,957.64 -> £3,332,157.80 (10.6%); £3,728,957.91 -> £3,332,157.93 (10.6%); £3,728,958.11 -> £3,332,158.29 (10.6%); £3,728,958.31 -> £3,332,158.62 (10.6%); £3,728,958.52 -> £3,332,158.93 (10.6%); £3,728,958.72 -> £3,332,159.23 (10.6%); £3,728,958.99 -> £3,332,159.50 (10.6%); £3,728,959.19 -> £3,332,159.76 (10.6%); £3,728,959.39 -> £3,332,160.03 (10.6%); £3,728,959.66 -> £3,332,160.29 (10.6%); £3,728,959.93 -> £3,332,160.54 (10.6%); £3,728,960.19 -> £3,332,160.80 (10.6%); £3,728,960.46 -> £3,332,161.06 (10.6%); £3,728,960.73 -> £3,332,161.11 (10.6%); £3,728,961.00 -> £3,332,161.15 (10.6%); £3,728,961.25 -> £3,332,161.20 (10.6%); £3,728,961.48 -> £3,332,161.24 (10.6%); £3,728,961.69 -> £3,332,161.28 (10.6%); £3,728,961.83 -> £3,332,161.32 (10.6%); £3,728,961.98 -> £3,332,161.37 (10.6%); £3,728,962.12 -> £3,332,161.41 (10.6%); £3,728,962.27 -> £3,332,161.45 (10.6%); £3,728,962.42 -> £3,332,161.49 (10.6%); £3,728,962.56 -> £3,332,161.53 (10.6%); £3,728,962.70 -> £3,332,161.58 (10.6%); £3,728,962.83 -> £3,332,161.62 (10.6%); £3,728,962.97 -> £3,332,161.66 (10.6%); £3,728,963.11 -> £3,332,161.70 (10.6%); £3,728,963.25 -> £3,332,161.75 (10.6%); £3,728,963.39 -> £3,332,162.05 (10.6%); £3,728,963.53 -> £3,332,162.37 (10.6%); £3,728,963.69 -> £3,332,162.68 (10.6%); £3,728,963.86 -> £3,332,163.01 (10.6%); £3,728,964.05 -> £3,332,163.34 (10.6%); £3,728,964.26 -> £3,332,163.70 (10.6%); £3,728,964.48 -> £3,332,164.08 (10.6%); £3,728,964.72 -> £3,332,164.46 (10.6%); £3,728,964.95 -> £3,332,164.57 (10.6%); £3,728,965.18 -> £3,332,164.67 (10.6%); £3,728,965.42 -> £3,332,164.78 (10.6%); £3,728,965.65 -> £3,332,164.88 (10.6%); £3,728,965.89 -> £3,332,164.97 (10.6%); £3,728,966.13 -> £3,332,165.07 (10.6%); £3,728,966.36 -> £3,332,165.16 (10.6%); £3,728,966.60 -> £3,332,165.24 (10.6%); £3,728,966.85 -> £3,332,165.32 (10.6%); £3,728,967.08 -> £3,332,165.40 (10.6%); £3,728,967.32 -> £3,332,165.48 (10.6%); £3,728,967.56 -> £3,332,165.56 (10.6%); £3,728,967.80 -> £3,332,165.64 (10.6%); £3,728,968.02 -> £3,332,165.97 (10.6%); £3,728,968.20 -> £3,332,166.29 (10.6%); £3,728,968.37 -> £3,332,166.60 (10.6%); £3,728,968.55 -> £3,332,166.90 (10.6%); £3,728,968.72 -> £3,332,167.20 (10.6%); £3,728,968.90 -> £3,332,167.49 (10.6%); £3,728,969.08 -> £3,332,167.80 (10.6%); £3,728,969.32 -> £3,332,168.11 (10.6%); £3,728,969.55 -> £3,332,168.41 (10.6%); £3,728,969.78 -> £3,332,168.70 (10.6%); £3,728,970.01 -> £3,332,169.00 (10.6%); £3,728,970.25 -> £3,332,169.05 (10.6%); £3,728,970.48 -> £3,332,169.10 (10.6%); £3,728,970.70 -> £3,332,169.14 (10.6%); £3,728,970.89 -> £3,332,169.18 (10.6%); £3,728,971.08 -> £3,332,169.23 (10.6%); £3,728,971.22 -> £3,332,169.27 (10.6%); £3,728,971.36 -> £3,332,169.31 (10.6%); £3,728,971.50 -> £3,332,169.35 (10.6%); £3,728,971.64 -> £3,332,169.39 (10.6%); £3,728,971.78 -> £3,332,169.44 (10.6%); £3,728,971.92 -> £3,332,169.48 (10.6%); £3,728,972.06 -> £3,332,169.52 (10.6%); £3,728,972.20 -> £3,332,169.56 (10.6%); £3,728,972.34 -> £3,332,169.60 (10.6%); £3,728,972.47 -> £3,332,169.64 (10.6%); £3,728,972.62 -> £3,332,169.68 (10.6%); £3,728,972.75 -> £3,332,169.98 (10.6%); £3,728,972.89 -> £3,332,170.28 (10.6%); £3,728,973.05 -> £3,332,170.58 (10.6%); £3,728,973.22 -> £3,332,170.87 (10.6%); £3,728,973.41 -> £3,332,171.17 (10.6%); £3,728,973.61 -> £3,332,171.47 (10.6%); £3,728,973.83 -> £3,332,171.77 (10.6%); £3,728,974.07 -> £3,332,172.07 (10.6%); £3,728,974.31 -> £3,332,172.12 (10.6%); £3,728,974.53 -> £3,332,172.18 (10.6%); £3,728,974.77 -> £3,332,172.23 (10.6%); £3,728,975.00 -> £3,332,172.29 (10.6%); £3,728,975.23 -> £3,332,172.34 (10.6%); £3,728,975.46 -> £3,332,172.40 (10.6%); £3,728,975.68 -> £3,332,172.45 (10.6%); £3,728,975.91 -> £3,332,172.50 (10.6%); £3,728,976.15 -> £3,332,172.55 (10.6%); £3,728,976.38 -> £3,332,172.60 (10.6%); £3,728,976.61 -> £3,332,172.66 (10.6%); £3,728,976.84 -> £3,332,172.71 (10.6%); £3,728,977.07 -> £3,332,172.76 (10.6%); £3,728,977.25 -> £3,332,173.04 (10.6%); £3,728,977.43 -> £3,332,173.33 (10.6%); £3,728,977.59 -> £3,332,173.61 (10.6%); £3,728,977.77 -> £3,332,173.91 (10.6%); £3,728,978.00 -> £3,332,174.20 (10.6%); £3,728,978.18 -> £3,332,174.49 (10.6%); £3,728,978.35 -> £3,332,174.79 (10.6%); £3,728,978.59 -> £3,332,175.09 (10.6%); £3,728,978.83 -> £3,332,175.38 (10.6%); £3,728,979.06 -> £3,332,175.66 (10.6%); £3,728,979.29 -> £3,332,175.96 (10.6%); £3,728,979.52 -> £3,332,176.00 (10.6%); £3,728,979.75 -> £3,332,176.04 (10.6%); £3,728,979.97 -> £3,332,176.09 (10.6%); £3,728,980.17 -> £3,332,176.13 (10.6%); £3,728,980.35 -> £3,332,176.17 (10.6%); £3,728,980.51 -> £3,332,176.21 (10.6%); £3,728,980.66 -> £3,332,176.25 (10.6%); £3,728,980.81 -> £3,332,176.29 (10.6%); £3,728,980.97 -> £3,332,176.34 (10.6%); £3,728,981.12 -> £3,332,176.38 (10.6%); £3,728,981.28 -> £3,332,176.42 (10.6%); £3,728,981.43 -> £3,332,176.46 (10.6%); £3,728,981.58 -> £3,332,176.50 (10.6%); £3,728,981.74 -> £3,332,176.55 (10.6%); £3,728,981.89 -> £3,332,176.59 (10.6%); £3,728,982.04 -> £3,332,176.64 (10.6%); £3,728,982.20 -> £3,332,176.93 (10.6%); £3,728,982.35 -> £3,332,177.24 (10.6%); £3,728,982.52 -> £3,332,177.55 (10.6%); £3,728,982.71 -> £3,332,177.87 (10.6%); £3,728,982.91 -> £3,332,178.23 (10.6%); £3,728,983.13 -> £3,332,178.62 (10.6%); £3,728,983.37 -> £3,332,179.04 (10.6%); £3,728,983.62 -> £3,332,179.47 (10.6%); £3,728,983.86 -> £3,332,179.61 (10.6%); £3,728,984.12 -> £3,332,179.75 (10.6%); £3,728,984.38 -> £3,332,179.90 (10.6%); £3,728,984.63 -> £3,332,180.05 (10.6%); £3,728,984.89 -> £3,332,180.19 (10.6%); £3,728,985.15 -> £3,332,180.33 (10.6%); £3,728,985.41 -> £3,332,180.47 (10.6%); £3,728,985.67 -> £3,332,180.61 (10.6%); £3,728,985.92 -> £3,332,180.75 (10.6%); £3,728,986.18 -> £3,332,180.88 (10.6%); £3,728,986.44 -> £3,332,181.01 (10.6%); £3,728,986.70 -> £3,332,181.14 (10.6%); £3,728,986.96 -> £3,332,181.27 (10.6%); £3,728,987.22 -> £3,332,181.68 (10.6%); £3,728,987.48 -> £3,332,182.07 (10.6%); £3,728,987.73 -> £3,332,182.43 (10.6%); £3,728,987.98 -> £3,332,182.75 (10.6%); £3,728,988.23 -> £3,332,183.07 (10.6%); £3,728,988.48 -> £3,332,183.38 (10.6%); £3,728,988.67 -> £3,332,183.69 (10.6%); £3,728,988.92 -> £3,332,183.99 (10.6%); £3,728,989.18 -> £3,332,184.29 (10.6%); £3,728,989.43 -> £3,332,184.58 (10.6%); £3,728,989.68 -> £3,332,184.87 (10.6%); £3,728,989.93 -> £3,332,184.92 (10.6%); £3,728,990.19 -> £3,332,184.97 (10.6%); £3,728,990.43 -> £3,332,185.01 (10.6%); £3,728,990.65 -> £3,332,185.06 (10.6%); £3,728,990.85 -> £3,332,185.10 (10.6%); £3,728,991.00 -> £3,332,185.14 (10.6%); £3,728,991.15 -> £3,332,185.18 (10.6%); £3,728,991.31 -> £3,332,185.22 (10.6%); £3,728,991.46 -> £3,332,185.27 (10.6%); £3,728,991.61 -> £3,332,185.31 (10.6%); £3,728,991.76 -> £3,332,185.35 (10.6%); £3,728,991.92 -> £3,332,185.39 (10.6%); £3,728,992.06 -> £3,332,185.44 (10.6%); £3,728,992.22 -> £3,332,185.48 (10.6%); £3,728,992.37 -> £3,332,185.53 (10.6%); £3,728,992.53 -> £3,332,185.57 (10.6%); £3,728,992.68 -> £3,332,185.86 (10.6%); £3,728,992.83 -> £3,332,186.16 (10.6%); £3,728,992.99 -> £3,332,186.47 (10.6%); £3,728,993.18 -> £3,332,186.80 (10.6%); £3,728,993.38 -> £3,332,187.15 (10.6%); £3,728,993.60 -> £3,332,187.53 (10.6%); £3,728,993.83 -> £3,332,187.94 (10.6%); £3,728,994.08 -> £3,332,188.37 (10.6%); £3,728,994.34 -> £3,332,188.52 (10.6%); £3,728,994.59 -> £3,332,188.67 (10.6%); £3,728,994.84 -> £3,332,188.82 (10.6%); £3,728,995.10 -> £3,332,188.98 (10.6%); £3,728,995.36 -> £3,332,189.13 (10.6%); £3,728,995.62 -> £3,332,189.27 (10.6%); £3,728,995.87 -> £3,332,189.42 (10.6%); £3,728,996.13 -> £3,332,189.55 (10.6%); £3,728,996.38 -> £3,332,189.69 (10.6%); £3,728,996.64 -> £3,332,189.83 (10.6%); £3,728,996.90 -> £3,332,189.97 (10.6%); £3,728,997.15 -> £3,332,190.10 (10.6%); £3,728,997.40 -> £3,332,190.23 (10.6%); £3,728,997.59 -> £3,332,190.61 (10.6%); £3,728,997.77 -> £3,332,191.00 (10.6%); £3,728,998.02 -> £3,332,191.33 (10.6%); £3,728,998.21 -> £3,332,191.63 (10.6%); £3,728,998.40 -> £3,332,191.94 (10.6%); £3,728,998.66 -> £3,332,192.25 (10.6%); £3,728,998.91 -> £3,332,192.55 (10.6%); £3,728,999.17 -> £3,332,192.85 (10.6%); £3,728,999.43 -> £3,332,193.14 (10.6%); £3,728,999.68 -> £3,332,193.43 (10.6%); £3,728,999.94 -> £3,332,193.71 (10.6%); £3,729,000.20 -> £3,332,193.75 (10.6%); £3,729,000.45 -> £3,332,193.80 (10.6%); £3,729,000.68 -> £3,332,193.85 (10.6%); £3,729,000.89 -> £3,332,193.89 (10.6%); £3,729,001.09 -> £3,332,193.93 (10.6%); £3,729,001.24 -> £3,332,193.97 (10.6%); £3,729,001.40 -> £3,332,194.01 (10.6%); £3,729,001.55 -> £3,332,194.06 (10.6%); £3,729,001.70 -> £3,332,194.10 (10.6%); £3,729,001.85 -> £3,332,194.14 (10.6%); £3,729,002.00 -> £3,332,194.18 (10.6%); £3,729,002.15 -> £3,332,194.22 (10.6%); £3,729,002.30 -> £3,332,194.27 (10.6%); £3,729,002.45 -> £3,332,194.31 (10.6%); £3,729,002.60 -> £3,332,194.35 (10.6%); £3,729,002.75 -> £3,332,194.40 (10.6%); £3,729,002.91 -> £3,332,194.66 (10.6%); £3,729,003.06 -> £3,332,194.92 (10.6%); £3,729,003.22 -> £3,332,195.18 (10.6%); £3,729,003.41 -> £3,332,195.46 (10.6%); £3,729,003.60 -> £3,332,195.76 (10.6%); £3,729,003.83 -> £3,332,196.09 (10.6%); £3,729,004.07 -> £3,332,196.45 (10.6%); £3,729,004.32 -> £3,332,196.83 (10.6%); £3,729,004.57 -> £3,332,196.97 (10.6%); £3,729,004.82 -> £3,332,197.12 (10.6%); £3,729,005.07 -> £3,332,197.27 (10.6%); £3,729,005.32 -> £3,332,197.42 (10.6%); £3,729,005.57 -> £3,332,197.56 (10.6%); £3,729,005.83 -> £3,332,197.70 (10.6%); £3,729,006.09 -> £3,332,197.85 (10.6%); £3,729,006.34 -> £3,332,197.98 (10.6%); £3,729,006.59 -> £3,332,198.11 (10.6%); £3,729,006.85 -> £3,332,198.24 (10.6%); £3,729,007.10 -> £3,332,198.38 (10.6%); £3,729,007.35 -> £3,332,198.50 (10.6%); £3,729,007.60 -> £3,332,198.63 (10.6%); £3,729,007.85 -> £3,332,198.99 (10.6%); £3,729,008.04 -> £3,332,199.35 (10.6%); £3,729,008.29 -> £3,332,199.67 (10.6%); £3,729,008.54 -> £3,332,199.94 (10.6%); £3,729,008.74 -> £3,332,200.22 (10.6%); £3,729,008.98 -> £3,332,200.49 (10.6%); £3,729,009.16 -> £3,332,200.75 (10.6%); £3,729,009.42 -> £3,332,201.02 (10.6%); £3,729,009.67 -> £3,332,201.29 (10.6%); £3,729,009.92 -> £3,332,201.54 (10.6%); £3,729,010.17 -> £3,332,201.80 (10.6%); £3,729,010.42 -> £3,332,201.85 (10.6%); £3,729,010.67 -> £3,332,201.89 (10.6%); £3,729,010.90 -> £3,332,201.94 (10.6%); £3,729,011.12 -> £3,332,201.98 (10.6%); £3,729,011.31 -> £3,332,202.02 (10.6%); £3,729,011.46 -> £3,332,202.06 (10.6%); £3,729,011.61 -> £3,332,202.11 (10.6%); £3,729,011.76 -> £3,332,202.15 (10.6%); £3,729,011.91 -> £3,332,202.19 (10.6%); £3,729,012.06 -> £3,332,202.23 (10.6%); £3,729,012.21 -> £3,332,202.27 (10.6%); £3,729,012.36 -> £3,332,202.32 (10.6%); £3,729,012.51 -> £3,332,202.36 (10.6%); £3,729,012.66 -> £3,332,202.40 (10.6%); £3,729,012.81 -> £3,332,202.45 (10.6%); £3,729,012.96 -> £3,332,202.49 (10.6%); £3,729,013.11 -> £3,332,202.73 (10.6%); £3,729,013.26 -> £3,332,202.97 (10.6%); £3,729,013.42 -> £3,332,203.21 (10.6%); £3,729,013.60 -> £3,332,203.47 (10.6%); £3,729,013.80 -> £3,332,203.76 (10.6%); £3,729,014.02 -> £3,332,204.07 (10.6%); £3,729,014.24 -> £3,332,204.42 (10.6%); £3,729,014.50 -> £3,332,204.77 (10.6%); £3,729,014.75 -> £3,332,204.91 (10.6%); £3,729,015.00 -> £3,332,205.06 (10.6%); £3,729,015.25 -> £3,332,205.20 (10.6%); £3,729,015.50 -> £3,332,205.35 (10.6%); £3,729,015.75 -> £3,332,205.49 (10.6%); £3,729,015.99 -> £3,332,205.64 (10.6%); £3,729,016.23 -> £3,332,205.78 (10.6%); £3,729,016.48 -> £3,332,205.92 (10.6%); £3,729,016.72 -> £3,332,206.05 (10.6%); £3,729,016.97 -> £3,332,206.19 (10.6%); £3,729,017.23 -> £3,332,206.32 (10.6%); £3,729,017.48 -> £3,332,206.45 (10.6%); £3,729,017.73 -> £3,332,206.58 (10.6%); £3,729,017.92 -> £3,332,206.92 (10.6%); £3,729,018.10 -> £3,332,207.24 (10.6%); £3,729,018.28 -> £3,332,207.53 (10.6%); £3,729,018.47 -> £3,332,207.79 (10.6%); £3,729,018.65 -> £3,332,208.04 (10.6%); £3,729,018.83 -> £3,332,208.29 (10.6%); £3,729,019.02 -> £3,332,208.54 (10.6%); £3,729,019.27 -> £3,332,208.78 (10.6%); £3,729,019.52 -> £3,332,209.02 (10.6%); £3,729,019.77 -> £3,332,209.26 (10.6%); £3,729,020.02 -> £3,332,209.49 (10.6%); £3,729,020.27 -> £3,332,209.53 (10.6%); £3,729,020.52 -> £3,332,209.58 (10.6%); £3,729,020.75 -> £3,332,209.63 (10.6%); £3,729,020.96 -> £3,332,209.67 (10.6%); £3,729,021.15 -> £3,332,209.71 (10.6%); £3,729,021.30 -> £3,332,209.75 (10.6%); £3,729,021.45 -> £3,332,209.79 (10.6%); £3,729,021.60 -> £3,332,209.83 (10.6%); £3,729,021.74 -> £3,332,209.88 (10.6%); £3,729,021.89 -> £3,332,209.92 (10.6%); £3,729,022.03 -> £3,332,209.96 (10.6%); £3,729,022.18 -> £3,332,210.00 (10.6%); £3,729,022.33 -> £3,332,210.04 (10.6%); £3,729,022.47 -> £3,332,210.08 (10.6%); £3,729,022.63 -> £3,332,210.13 (10.6%); £3,729,022.77 -> £3,332,210.17 (10.6%); £3,729,022.92 -> £3,332,210.43 (10.6%); £3,729,023.07 -> £3,332,210.69 (10.6%); £3,729,023.23 -> £3,332,210.97 (10.6%); £3,729,023.42 -> £3,332,211.26 (10.6%); £3,729,023.61 -> £3,332,211.58 (10.6%); £3,729,023.82 -> £3,332,211.92 (10.6%); £3,729,024.06 -> £3,332,212.28 (10.6%); £3,729,024.30 -> £3,332,212.65 (10.6%); £3,729,024.54 -> £3,332,212.80 (10.6%); £3,729,024.77 -> £3,332,212.94 (10.6%); £3,729,025.02 -> £3,332,213.09 (10.6%); £3,729,025.27 -> £3,332,213.23 (10.6%); £3,729,025.52 -> £3,332,213.38 (10.6%); £3,729,025.77 -> £3,332,213.52 (10.6%); £3,729,026.01 -> £3,332,213.66 (10.6%); £3,729,026.25 -> £3,332,213.79 (10.6%); £3,729,026.49 -> £3,332,213.92 (10.6%); £3,729,026.73 -> £3,332,214.06 (10.6%); £3,729,026.98 -> £3,332,214.19 (10.6%); £3,729,027.22 -> £3,332,214.31 (10.6%); £3,729,027.46 -> £3,332,214.44 (10.6%); £3,729,027.65 -> £3,332,214.80 (10.6%); £3,729,027.84 -> £3,332,215.14 (10.6%); £3,729,028.02 -> £3,332,215.44 (10.6%); £3,729,028.21 -> £3,332,215.73 (10.6%); £3,729,028.39 -> £3,332,216.00 (10.6%); £3,729,028.57 -> £3,332,216.28 (10.6%); £3,729,028.75 -> £3,332,216.54 (10.6%); £3,729,029.00 -> £3,332,216.81 (10.6%); £3,729,029.24 -> £3,332,217.07 (10.6%); £3,729,029.49 -> £3,332,217.33 (10.6%); £3,729,029.73 -> £3,332,217.58 (10.6%); £3,729,029.99 -> £3,332,217.63 (10.6%); £3,729,030.23 -> £3,332,217.67 (10.6%); £3,729,030.47 -> £3,332,217.72 (10.6%); £3,729,030.68 -> £3,332,217.76 (10.6%); £3,729,030.87 -> £3,332,217.80 (10.6%); £3,729,031.00 -> £3,332,217.84 (10.6%); £3,729,031.13 -> £3,332,217.88 (10.6%); £3,729,031.26 -> £3,332,217.93 (10.6%); £3,729,031.39 -> £3,332,217.97 (10.6%); £3,729,031.51 -> £3,332,218.01 (10.6%); £3,729,031.64 -> £3,332,218.05 (10.6%); £3,729,031.77 -> £3,332,218.09 (10.6%); £3,729,031.90 -> £3,332,218.13 (10.6%); £3,729,032.03 -> £3,332,218.18 (10.6%); £3,729,032.15 -> £3,332,218.22 (10.6%); £3,729,032.28 -> £3,332,218.26 (10.6%); £3,729,032.41 -> £3,332,218.50 (10.6%); £3,729,032.54 -> £3,332,218.75 (10.6%); £3,729,032.68 -> £3,332,219.00 (10.6%); £3,729,032.84 -> £3,332,219.25 (10.6%); £3,729,033.01 -> £3,332,219.52 (10.6%); £3,729,033.20 -> £3,332,219.80 (10.6%); £3,729,033.40 -> £3,332,220.11 (10.6%); £3,729,033.61 -> £3,332,220.42 (10.6%); £3,729,033.81 -> £3,332,220.53 (10.6%); £3,729,034.02 -> £3,332,220.63 (10.6%); £3,729,034.23 -> £3,332,220.74 (10.6%); £3,729,034.44 -> £3,332,220.85 (10.6%); £3,729,034.65 -> £3,332,220.94 (10.6%); £3,729,034.87 -> £3,332,221.04 (10.6%); £3,729,035.08 -> £3,332,221.12 (10.6%); £3,729,035.29 -> £3,332,221.21 (10.6%); £3,729,035.51 -> £3,332,221.29 (10.6%); £3,729,035.72 -> £3,332,221.37 (10.6%); £3,729,035.93 -> £3,332,221.45 (10.6%); £3,729,036.15 -> £3,332,221.53 (10.6%); £3,729,036.36 -> £3,332,221.61 (10.6%); £3,729,036.52 -> £3,332,221.88 (10.6%); £3,729,036.68 -> £3,332,222.15 (10.6%); £3,729,036.84 -> £3,332,222.41 (10.6%); £3,729,037.00 -> £3,332,222.65 (10.6%); £3,729,037.16 -> £3,332,222.90 (10.6%); £3,729,037.32 -> £3,332,223.16 (10.6%); £3,729,037.52 -> £3,332,223.41 (10.6%); £3,729,037.74 -> £3,332,223.64 (10.6%); £3,729,037.96 -> £3,332,223.89 (10.6%); £3,729,038.17 -> £3,332,224.14 (10.6%); £3,729,038.38 -> £3,332,224.38 (10.6%); £3,729,038.60 -> £3,332,224.42 (10.6%); £3,729,038.81 -> £3,332,224.47 (10.6%); £3,729,039.00 -> £3,332,224.52 (10.6%); £3,729,039.18 -> £3,332,224.56 (10.6%); £3,729,039.34 -> £3,332,224.60 (10.6%); £3,729,039.47 -> £3,332,224.64 (10.6%); £3,729,039.60 -> £3,332,224.69 (10.6%); £3,729,039.73 -> £3,332,224.73 (10.6%); £3,729,039.85 -> £3,332,224.77 (10.6%); £3,729,039.98 -> £3,332,224.81 (10.6%); £3,729,040.10 -> £3,332,224.85 (10.6%); £3,729,040.23 -> £3,332,224.89 (10.6%); £3,729,040.35 -> £3,332,224.93 (10.6%); £3,729,040.48 -> £3,332,224.97 (10.6%); £3,729,040.61 -> £3,332,225.01 (10.6%); £3,729,040.74 -> £3,332,225.05 (10.6%); £3,729,040.86 -> £3,332,225.34 (10.6%); £3,729,040.98 -> £3,332,225.64 (10.6%); £3,729,041.13 -> £3,332,225.94 (10.6%); £3,729,041.28 -> £3,332,226.24 (10.6%); £3,729,041.46 -> £3,332,226.53 (10.6%); £3,729,041.64 -> £3,332,226.83 (10.6%); £3,729,041.84 -> £3,332,227.12 (10.6%); £3,729,042.04 -> £3,332,227.42 (10.6%); £3,729,042.26 -> £3,332,227.48 (10.6%); £3,729,042.47 -> £3,332,227.54 (10.6%); £3,729,042.67 -> £3,332,227.59 (10.6%); £3,729,042.89 -> £3,332,227.65 (10.6%); £3,729,043.11 -> £3,332,227.70 (10.6%); £3,729,043.32 -> £3,332,227.76 (10.6%); £3,729,043.52 -> £3,332,227.81 (10.6%); £3,729,043.73 -> £3,332,227.86 (10.6%); £3,729,043.95 -> £3,332,227.91 (10.6%); £3,729,044.15 -> £3,332,227.97 (10.6%); £3,729,044.37 -> £3,332,228.02 (10.6%); £3,729,044.58 -> £3,332,228.07 (10.6%); £3,729,044.79 -> £3,332,228.12 (10.6%); £3,729,044.94 -> £3,332,228.40 (10.6%); £3,729,045.11 -> £3,332,228.69 (10.6%); £3,729,045.27 -> £3,332,228.97 (10.6%); £3,729,045.42 -> £3,332,229.27 (10.6%); £3,729,045.59 -> £3,332,229.56 (10.6%); £3,729,045.75 -> £3,332,229.84 (10.6%); £3,729,045.91 -> £3,332,230.13 (10.6%); £3,729,046.12 -> £3,332,230.41 (10.6%); £3,729,046.34 -> £3,332,230.70 (10.6%); £3,729,046.55 -> £3,332,231.00 (10.6%); £3,729,046.76 -> £3,332,231.29 (10.6%); £3,729,046.97 -> £3,332,231.33 (10.6%); £3,729,047.18 -> £3,332,231.37 (10.6%); £3,729,047.37 -> £3,332,231.41 (10.6%); £3,729,047.56 -> £3,332,231.45 (10.6%); £3,729,047.72 -> £3,332,231.49 (10.6%); £3,729,047.87 -> £3,332,231.53 (10.6%); £3,729,048.02 -> £3,332,231.58 (10.6%); £3,729,048.16 -> £3,332,231.62 (10.6%); £3,729,048.31 -> £3,332,231.66 (10.6%); £3,729,048.46 -> £3,332,231.70 (10.6%); £3,729,048.60 -> £3,332,231.74 (10.6%); £3,729,048.74 -> £3,332,231.79 (10.6%); £3,729,048.89 -> £3,332,231.83 (10.6%); £3,729,049.04 -> £3,332,231.87 (10.6%); £3,729,049.19 -> £3,332,231.92 (10.6%); £3,729,049.33 -> £3,332,231.96 (10.6%); £3,729,049.47 -> £3,332,232.31 (10.6%); £3,729,049.61 -> £3,332,232.66 (10.6%); £3,729,049.77 -> £3,332,233.03 (10.6%); £3,729,049.95 -> £3,332,233.41 (10.6%); £3,729,050.13 -> £3,332,233.81 (10.6%); £3,729,050.34 -> £3,332,234.24 (10.6%); £3,729,050.57 -> £3,332,234.70 (10.6%); £3,729,050.80 -> £3,332,235.17 (10.6%); £3,729,051.04 -> £3,332,235.32 (10.6%); £3,729,051.29 -> £3,332,235.47 (10.6%); £3,729,051.53 -> £3,332,235.62 (10.6%); £3,729,051.78 -> £3,332,235.78 (10.6%); £3,729,052.03 -> £3,332,235.93 (10.6%); £3,729,052.26 -> £3,332,236.08 (10.6%); £3,729,052.51 -> £3,332,236.22 (10.6%); £3,729,052.75 -> £3,332,236.36 (10.6%); £3,729,052.99 -> £3,332,236.49 (10.6%); £3,729,053.23 -> £3,332,236.63 (10.6%); £3,729,053.48 -> £3,332,236.77 (10.6%); £3,729,053.72 -> £3,332,236.90 (10.6%); £3,729,053.96 -> £3,332,237.02 (10.6%); £3,729,054.14 -> £3,332,237.46 (10.6%); £3,729,054.33 -> £3,332,237.88 (10.6%); £3,729,054.51 -> £3,332,238.26 (10.6%); £3,729,054.69 -> £3,332,238.62 (10.6%); £3,729,054.88 -> £3,332,238.98 (10.6%); £3,729,055.05 -> £3,332,239.33 (10.6%); £3,729,055.23 -> £3,332,239.69 (10.6%); £3,729,055.47 -> £3,332,240.02 (10.6%); £3,729,055.71 -> £3,332,240.38 (10.6%); £3,729,055.94 -> £3,332,240.72 (10.6%); £3,729,056.19 -> £3,332,241.06 (10.6%); £3,729,056.43 -> £3,332,241.11 (10.6%); £3,729,056.67 -> £3,332,241.16 (10.6%); £3,729,056.90 -> £3,332,241.20 (10.6%); £3,729,057.10 -> £3,332,241.24 (10.6%); £3,729,057.29 -> £3,332,241.28 (10.6%); £3,729,057.44 -> £3,332,241.32 (10.6%); £3,729,057.58 -> £3,332,241.37 (10.6%); £3,729,057.72 -> £3,332,241.41 (10.6%); £3,729,057.87 -> £3,332,241.45 (10.6%); £3,729,058.01 -> £3,332,241.49 (10.6%); £3,729,058.15 -> £3,332,241.53 (10.6%); £3,729,058.28 -> £3,332,241.57 (10.6%); £3,729,058.43 -> £3,332,241.62 (10.6%); £3,729,058.57 -> £3,332,241.66 (10.6%); £3,729,058.72 -> £3,332,241.70 (10.6%); £3,729,058.86 -> £3,332,241.75 (10.6%); £3,729,059.01 -> £3,332,242.07 (10.6%); £3,729,059.15 -> £3,332,242.39 (10.6%); £3,729,059.31 -> £3,332,242.71 (10.6%); £3,729,059.49 -> £3,332,243.05 (10.6%); £3,729,059.68 -> £3,332,243.41 (10.6%); £3,729,059.89 -> £3,332,243.80 (10.6%); £3,729,060.12 -> £3,332,244.22 (10.6%); £3,729,060.36 -> £3,332,244.64 (10.6%); £3,729,060.60 -> £3,332,244.79 (10.6%); £3,729,060.84 -> £3,332,244.93 (10.6%); £3,729,061.07 -> £3,332,245.08 (10.6%); £3,729,061.31 -> £3,332,245.23 (10.6%); £3,729,061.55 -> £3,332,245.38 (10.6%); £3,729,061.79 -> £3,332,245.53 (10.6%); £3,729,062.03 -> £3,332,245.67 (10.6%); £3,729,062.26 -> £3,332,245.81 (10.6%); £3,729,062.50 -> £3,332,245.95 (10.6%); £3,729,062.73 -> £3,332,246.08 (10.6%); £3,729,062.96 -> £3,332,246.21 (10.6%); £3,729,063.20 -> £3,332,246.35 (10.6%); £3,729,063.44 -> £3,332,246.47 (10.6%); £3,729,063.63 -> £3,332,246.89 (10.6%); £3,729,063.81 -> £3,332,247.29 (10.6%); £3,729,064.00 -> £3,332,247.67 (10.6%); £3,729,064.25 -> £3,332,248.01 (10.6%); £3,729,064.49 -> £3,332,248.35 (10.6%); £3,729,064.73 -> £3,332,248.68 (10.6%); £3,729,064.92 -> £3,332,249.00 (10.6%); £3,729,065.16 -> £3,332,249.32 (10.6%); £3,729,065.39 -> £3,332,249.63 (10.6%); £3,729,065.64 -> £3,332,249.93 (10.6%); £3,729,065.87 -> £3,332,250.23 (10.6%); £3,729,066.12 -> £3,332,250.27 (10.6%); £3,729,066.36 -> £3,332,250.32 (10.6%); £3,729,066.58 -> £3,332,250.37 (10.6%); £3,729,066.78 -> £3,332,250.41 (10.6%); £3,729,066.97 -> £3,332,250.45 (10.6%); £3,729,067.11 -> £3,332,250.49 (10.6%); £3,729,067.25 -> £3,332,250.53 (10.6%); £3,729,067.39 -> £3,332,250.58 (10.6%); £3,729,067.53 -> £3,332,250.62 (10.6%); £3,729,067.67 -> £3,332,250.66 (10.6%); £3,729,067.81 -> £3,332,250.70 (10.6%); £3,729,067.95 -> £3,332,250.74 (10.6%); £3,729,068.10 -> £3,332,250.79 (10.6%); £3,729,068.24 -> £3,332,250.83 (10.6%); £3,729,068.38 -> £3,332,250.87 (10.6%); £3,729,068.52 -> £3,332,250.92 (10.6%); £3,729,068.66 -> £3,332,251.26 (10.6%); £3,729,068.80 -> £3,332,251.61 (10.6%); £3,729,068.96 -> £3,332,251.97 (10.6%); £3,729,069.13 -> £3,332,252.35 (10.6%); £3,729,069.32 -> £3,332,252.73 (10.6%); £3,729,069.53 -> £3,332,253.16 (10.6%); £3,729,069.74 -> £3,332,253.62 (10.6%); £3,729,069.98 -> £3,332,254.09 (10.6%); £3,729,070.22 -> £3,332,254.24 (10.6%); £3,729,070.45 -> £3,332,254.39 (10.6%); £3,729,070.70 -> £3,332,254.54 (10.6%); £3,729,070.93 -> £3,332,254.69 (10.6%); £3,729,071.16 -> £3,332,254.84 (10.6%); £3,729,071.40 -> £3,332,254.98 (10.6%); £3,729,071.64 -> £3,332,255.11 (10.6%); £3,729,071.88 -> £3,332,255.25 (10.6%); £3,729,072.12 -> £3,332,255.38 (10.6%); £3,729,072.36 -> £3,332,255.52 (10.6%); £3,729,072.60 -> £3,332,255.66 (10.6%); £3,729,072.83 -> £3,332,255.78 (10.6%); £3,729,073.07 -> £3,332,255.91 (10.6%); £3,729,073.24 -> £3,332,256.34 (10.6%); £3,729,073.42 -> £3,332,256.77 (10.6%); £3,729,073.66 -> £3,332,257.16 (10.6%); £3,729,073.90 -> £3,332,257.52 (10.6%); £3,729,074.14 -> £3,332,257.88 (10.6%); £3,729,074.38 -> £3,332,258.23 (10.6%); £3,729,074.62 -> £3,332,258.57 (10.6%); £3,729,074.86 -> £3,332,258.91 (10.6%); £3,729,075.10 -> £3,332,259.25 (10.6%); £3,729,075.33 -> £3,332,259.57 (10.6%); £3,729,075.57 -> £3,332,259.88 (10.6%); £3,729,075.80 -> £3,332,259.93 (10.6%); £3,729,076.03 -> £3,332,259.97 (10.6%); £3,729,076.25 -> £3,332,260.02 (10.6%); £3,729,076.44 -> £3,332,260.06 (10.6%); £3,729,076.62 -> £3,332,260.10 (10.6%); £3,729,076.76 -> £3,332,260.14 (10.6%); £3,729,076.91 -> £3,332,260.19 (10.6%); £3,729,077.05 -> £3,332,260.23 (10.6%); £3,729,077.19 -> £3,332,260.27 (10.6%); £3,729,077.33 -> £3,332,260.31 (10.6%); £3,729,077.47 -> £3,332,260.35 (10.6%); £3,729,077.61 -> £3,332,260.39 (10.6%); £3,729,077.75 -> £3,332,260.44 (10.6%); £3,729,077.90 -> £3,332,260.48 (10.6%); £3,729,078.05 -> £3,332,260.52 (10.6%); £3,729,078.19 -> £3,332,260.56 (10.6%); £3,729,078.34 -> £3,332,260.93 (10.6%); £3,729,078.48 -> £3,332,261.31 (10.6%); £3,729,078.63 -> £3,332,261.69 (10.6%); £3,729,078.80 -> £3,332,262.09 (10.6%); £3,729,079.00 -> £3,332,262.52 (10.6%); £3,729,079.20 -> £3,332,262.96 (10.6%); £3,729,079.42 -> £3,332,263.44 (10.6%); £3,729,079.65 -> £3,332,263.93 (10.6%); £3,729,079.89 -> £3,332,264.08 (10.6%); £3,729,080.12 -> £3,332,264.23 (10.6%); £3,729,080.35 -> £3,332,264.38 (10.6%); £3,729,080.58 -> £3,332,264.53 (10.6%); £3,729,080.81 -> £3,332,264.68 (10.6%); £3,729,081.05 -> £3,332,264.82 (10.6%); £3,729,081.30 -> £3,332,264.96 (10.6%); £3,729,081.53 -> £3,332,265.09 (10.6%); £3,729,081.77 -> £3,332,265.23 (10.6%); £3,729,082.00 -> £3,332,265.37 (10.6%); £3,729,082.24 -> £3,332,265.51 (10.6%); £3,729,082.47 -> £3,332,265.64 (10.6%); £3,729,082.71 -> £3,332,265.77 (10.6%); £3,729,082.89 -> £3,332,266.24 (10.6%); £3,729,083.07 -> £3,332,266.69 (10.6%); £3,729,083.25 -> £3,332,267.11 (10.6%); £3,729,083.42 -> £3,332,267.50 (10.6%); £3,729,083.60 -> £3,332,267.88 (10.6%); £3,729,083.77 -> £3,332,268.26 (10.6%); £3,729,083.95 -> £3,332,268.64 (10.6%); £3,729,084.18 -> £3,332,269.00 (10.6%); £3,729,084.41 -> £3,332,269.36 (10.6%); £3,729,084.65 -> £3,332,269.73 (10.6%); £3,729,084.87 -> £3,332,270.09 (10.6%); £3,729,085.11 -> £3,332,270.14 (10.6%); £3,729,085.35 -> £3,332,270.19 (10.6%); £3,729,085.58 -> £3,332,270.23 (10.6%); £3,729,085.78 -> £3,332,270.28 (10.6%); £3,729,085.97 -> £3,332,270.32 (10.6%); £3,729,086.11 -> £3,332,270.36 (10.6%); £3,729,086.26 -> £3,332,270.40 (10.6%); £3,729,086.40 -> £3,332,270.44 (10.6%); £3,729,086.54 -> £3,332,270.49 (10.6%); £3,729,086.69 -> £3,332,270.53 (10.6%); £3,729,086.83 -> £3,332,270.57 (10.6%); £3,729,086.97 -> £3,332,270.61 (10.6%); £3,729,087.12 -> £3,332,270.66 (10.6%); £3,729,087.26 -> £3,332,270.70 (10.6%); £3,729,087.40 -> £3,332,270.74 (10.6%); £3,729,087.55 -> £3,332,270.79 (10.6%); £3,729,087.69 -> £3,332,271.10 (10.6%); £3,729,087.83 -> £3,332,271.43 (10.6%); £3,729,088.00 -> £3,332,271.76 (10.6%); £3,729,088.17 -> £3,332,272.12 (10.6%); £3,729,088.36 -> £3,332,272.49 (10.6%); £3,729,088.57 -> £3,332,272.89 (10.6%); £3,729,088.79 -> £3,332,273.32 (10.6%); £3,729,089.02 -> £3,332,273.76 (10.6%); £3,729,089.25 -> £3,332,273.91 (10.6%); £3,729,089.49 -> £3,332,274.06 (10.6%); £3,729,089.72 -> £3,332,274.21 (10.6%); £3,729,089.97 -> £3,332,274.36 (10.6%); £3,729,090.21 -> £3,332,274.51 (10.6%); £3,729,090.45 -> £3,332,274.66 (10.6%); £3,729,090.69 -> £3,332,274.80 (10.6%); £3,729,090.93 -> £3,332,274.94 (10.6%); £3,729,091.16 -> £3,332,275.08 (10.6%); £3,729,091.39 -> £3,332,275.22 (10.6%); £3,729,091.63 -> £3,332,275.36 (10.6%); £3,729,091.88 -> £3,332,275.49 (10.6%); £3,729,092.11 -> £3,332,275.62 (10.6%); £3,729,092.35 -> £3,332,276.04 (10.6%); £3,729,092.52 -> £3,332,276.44 (10.6%); £3,729,092.70 -> £3,332,276.81 (10.6%); £3,729,092.88 -> £3,332,277.16 (10.6%); £3,729,093.06 -> £3,332,277.49 (10.6%); £3,729,093.30 -> £3,332,277.83 (10.6%); £3,729,093.55 -> £3,332,278.15 (10.6%); £3,729,093.79 -> £3,332,278.48 (10.6%); £3,729,094.03 -> £3,332,278.81 (10.6%); £3,729,094.28 -> £3,332,279.11 (10.6%); £3,729,094.52 -> £3,332,279.42 (10.6%); £3,729,094.76 -> £3,332,279.47 (10.6%); £3,729,095.00 -> £3,332,279.51 (10.6%); £3,729,095.22 -> £3,332,279.56 (10.6%); £3,729,095.42 -> £3,332,279.60 (10.6%); £3,729,095.61 -> £3,332,279.64 (10.6%); £3,729,095.74 -> £3,332,279.68 (10.6%); £3,729,095.87 -> £3,332,279.72 (10.6%); £3,729,096.00 -> £3,332,279.76 (10.6%); £3,729,096.12 -> £3,332,279.81 (10.6%); £3,729,096.26 -> £3,332,279.85 (10.6%); £3,729,096.38 -> £3,332,279.89 (10.6%); £3,729,096.51 -> £3,332,279.93 (10.6%); £3,729,096.64 -> £3,332,279.98 (10.6%); £3,729,096.76 -> £3,332,280.02 (10.6%); £3,729,096.89 -> £3,332,280.06 (10.6%); £3,729,097.02 -> £3,332,280.10 (10.6%); £3,729,097.15 -> £3,332,280.35 (10.6%); £3,729,097.28 -> £3,332,280.60 (10.6%); £3,729,097.43 -> £3,332,280.86 (10.6%); £3,729,097.59 -> £3,332,281.12 (10.6%); £3,729,097.76 -> £3,332,281.40 (10.6%); £3,729,097.95 -> £3,332,281.69 (10.6%); £3,729,098.15 -> £3,332,282.00 (10.6%); £3,729,098.36 -> £3,332,282.32 (10.6%); £3,729,098.58 -> £3,332,282.43 (10.6%); £3,729,098.79 -> £3,332,282.53 (10.6%); £3,729,099.00 -> £3,332,282.64 (10.6%); £3,729,099.21 -> £3,332,282.74 (10.6%); £3,729,099.43 -> £3,332,282.84 (10.6%); £3,729,099.64 -> £3,332,282.94 (10.6%); £3,729,099.85 -> £3,332,283.03 (10.6%); £3,729,100.07 -> £3,332,283.11 (10.6%); £3,729,100.29 -> £3,332,283.19 (10.6%); £3,729,100.50 -> £3,332,283.27 (10.6%); £3,729,100.72 -> £3,332,283.35 (10.6%); £3,729,100.92 -> £3,332,283.43 (10.6%); £3,729,101.14 -> £3,332,283.51 (10.6%); £3,729,101.31 -> £3,332,283.80 (10.6%); £3,729,101.47 -> £3,332,284.08 (10.6%); £3,729,101.63 -> £3,332,284.34 (10.6%); £3,729,101.79 -> £3,332,284.60 (10.6%); £3,729,101.96 -> £3,332,284.86 (10.6%); £3,729,102.12 -> £3,332,285.11 (10.6%); £3,729,102.28 -> £3,332,285.36 (10.6%); £3,729,102.50 -> £3,332,285.61 (10.6%); £3,729,102.71 -> £3,332,285.86 (10.6%); £3,729,102.92 -> £3,332,286.10 (10.6%); £3,729,103.14 -> £3,332,286.35 (10.6%); £3,729,103.35 -> £3,332,286.40 (10.6%); £3,729,103.57 -> £3,332,286.44 (10.6%); £3,729,103.77 -> £3,332,286.49 (10.6%); £3,729,103.95 -> £3,332,286.53 (10.6%); £3,729,104.12 -> £3,332,286.57 (10.6%); £3,729,104.24 -> £3,332,286.61 (10.6%); £3,729,104.37 -> £3,332,286.66 (10.6%); £3,729,104.50 -> £3,332,286.70 (10.6%); £3,729,104.64 -> £3,332,286.74 (10.6%); £3,729,104.77 -> £3,332,286.78 (10.6%); £3,729,104.89 -> £3,332,286.82 (10.6%); £3,729,105.02 -> £3,332,286.86 (10.6%); £3,729,105.14 -> £3,332,286.90 (10.6%); £3,729,105.27 -> £3,332,286.94 (10.6%); £3,729,105.40 -> £3,332,286.98 (10.6%); £3,729,105.53 -> £3,332,287.02 (10.6%); £3,729,105.66 -> £3,332,287.19 (10.6%); £3,729,105.79 -> £3,332,287.36 (10.6%); £3,729,105.94 -> £3,332,287.53 (10.6%); £3,729,106.09 -> £3,332,287.69 (10.6%); £3,729,106.26 -> £3,332,287.87 (10.6%); £3,729,106.45 -> £3,332,288.04 (10.6%); £3,729,106.65 -> £3,332,288.22 (10.6%); £3,729,106.87 -> £3,332,288.40 (10.6%); £3,729,107.09 -> £3,332,288.45 (10.6%); £3,729,107.31 -> £3,332,288.51 (10.6%); £3,729,107.52 -> £3,332,288.56 (10.6%); £3,729,107.73 -> £3,332,288.62 (10.6%); £3,729,107.94 -> £3,332,288.68 (10.6%); £3,729,108.16 -> £3,332,288.73 (10.6%); £3,729,108.38 -> £3,332,288.78 (10.6%); £3,729,108.59 -> £3,332,288.84 (10.6%); £3,729,108.80 -> £3,332,288.89 (10.6%); £3,729,109.02 -> £3,332,288.94 (10.6%); £3,729,109.23 -> £3,332,288.99 (10.6%); £3,729,109.46 -> £3,332,289.05 (10.6%); £3,729,109.68 -> £3,332,289.10 (10.6%); £3,729,109.83 -> £3,332,289.27 (10.6%); £3,729,109.99 -> £3,332,289.45 (10.6%); £3,729,110.15 -> £3,332,289.63 (10.6%); £3,729,110.31 -> £3,332,289.81 (10.6%); £3,729,110.47 -> £3,332,289.98 (10.6%); £3,729,110.63 -> £3,332,290.16 (10.6%); £3,729,110.79 -> £3,332,290.34 (10.6%); £3,729,111.01 -> £3,332,290.51 (10.6%); £3,729,111.22 -> £3,332,290.68 (10.6%); £3,729,111.44 -> £3,332,290.85 (10.6%); £3,729,111.65 -> £3,332,291.02 (10.6%); £3,729,111.86 -> £3,332,291.06 (10.6%); £3,729,112.08 -> £3,332,291.10 (10.6%); £3,729,112.27 -> £3,332,291.15 (10.6%); £3,729,112.45 -> £3,332,291.19 (10.6%); £3,729,112.61 -> £3,332,291.23 (10.6%); £3,729,112.76 -> £3,332,291.27 (10.6%); £3,729,112.91 -> £3,332,291.31 (10.6%); £3,729,113.06 -> £3,332,291.35 (10.6%); £3,729,113.20 -> £3,332,291.39 (10.6%); £3,729,113.35 -> £3,332,291.44 (10.6%); £3,729,113.50 -> £3,332,291.48 (10.6%); £3,729,113.64 -> £3,332,291.52 (10.6%); £3,729,113.79 -> £3,332,291.56 (10.6%); £3,729,113.93 -> £3,332,291.60 (10.6%); £3,729,114.08 -> £3,332,291.65 (10.6%); £3,729,114.22 -> £3,332,291.69 (10.6%); £3,729,114.37 -> £3,332,291.89 (10.6%); £3,729,114.51 -> £3,332,292.10 (10.6%); £3,729,114.68 -> £3,332,292.31 (10.6%); £3,729,114.86 -> £3,332,292.54 (10.6%); £3,729,115.05 -> £3,332,292.80 (10.6%); £3,729,115.27 -> £3,332,293.08 (10.6%); £3,729,115.50 -> £3,332,293.39 (10.6%); £3,729,115.75 -> £3,332,293.71 (10.6%); £3,729,116.00 -> £3,332,293.86 (10.6%); £3,729,116.25 -> £3,332,294.01 (10.6%); £3,729,116.50 -> £3,332,294.16 (10.6%); £3,729,116.74 -> £3,332,294.31 (10.6%); £3,729,116.99 -> £3,332,294.46 (10.6%); £3,729,117.24 -> £3,332,294.61 (10.6%); £3,729,117.49 -> £3,332,294.74 (10.6%); £3,729,117.74 -> £3,332,294.88 (10.6%); £3,729,117.99 -> £3,332,295.02 (10.6%); £3,729,118.24 -> £3,332,295.16 (10.6%); £3,729,118.49 -> £3,332,295.31 (10.6%); £3,729,118.73 -> £3,332,295.44 (10.6%); £3,729,118.98 -> £3,332,295.58 (10.6%); £3,729,119.23 -> £3,332,295.89 (10.6%); £3,729,119.41 -> £3,332,296.18 (10.6%); £3,729,119.59 -> £3,332,296.44 (10.6%); £3,729,119.78 -> £3,332,296.67 (10.6%); £3,729,119.96 -> £3,332,296.89 (10.6%); £3,729,120.14 -> £3,332,297.11 (10.6%); £3,729,120.32 -> £3,332,297.33 (10.6%); £3,729,120.56 -> £3,332,297.54 (10.6%); £3,729,120.81 -> £3,332,297.75 (10.6%); £3,729,121.06 -> £3,332,297.95 (10.6%); £3,729,121.30 -> £3,332,298.15 (10.6%); £3,729,121.55 -> £3,332,298.20 (10.6%); £3,729,121.79 -> £3,332,298.24 (10.6%); £3,729,122.02 -> £3,332,298.29 (10.6%); £3,729,122.23 -> £3,332,298.33 (10.6%); £3,729,122.42 -> £3,332,298.38 (10.6%); £3,729,122.57 -> £3,332,298.42 (10.6%); £3,729,122.72 -> £3,332,298.46 (10.6%); £3,729,122.86 -> £3,332,298.51 (10.6%); £3,729,123.01 -> £3,332,298.55 (10.6%); £3,729,123.16 -> £3,332,298.59 (10.6%); £3,729,123.31 -> £3,332,298.64 (10.6%); £3,729,123.46 -> £3,332,298.68 (10.6%); £3,729,123.60 -> £3,332,298.72 (10.6%); £3,729,123.75 -> £3,332,298.76 (10.6%); £3,729,123.90 -> £3,332,298.81 (10.6%); £3,729,124.05 -> £3,332,298.86 (10.6%); £3,729,124.20 -> £3,332,299.04 (10.6%); £3,729,124.34 -> £3,332,299.23 (10.6%); £3,729,124.51 -> £3,332,299.44 (10.6%); £3,729,124.69 -> £3,332,299.65 (10.6%); £3,729,124.89 -> £3,332,299.90 (10.6%); £3,729,125.11 -> £3,332,300.17 (10.6%); £3,729,125.34 -> £3,332,300.47 (10.6%); £3,729,125.58 -> £3,332,300.78 (10.6%); £3,729,125.83 -> £3,332,300.93 (10.6%); £3,729,126.08 -> £3,332,301.08 (10.6%); £3,729,126.32 -> £3,332,301.24 (10.6%); £3,729,126.57 -> £3,332,301.39 (10.6%); £3,729,126.82 -> £3,332,301.55 (10.6%); £3,729,127.06 -> £3,332,301.69 (10.6%); £3,729,127.31 -> £3,332,301.83 (10.6%); £3,729,127.56 -> £3,332,301.98 (10.6%); £3,729,127.80 -> £3,332,302.11 (10.6%); £3,729,128.04 -> £3,332,302.25 (10.6%); £3,729,128.29 -> £3,332,302.39 (10.6%); £3,729,128.54 -> £3,332,302.52 (10.6%); £3,729,128.78 -> £3,332,302.65 (10.6%); £3,729,128.97 -> £3,332,302.95 (10.6%); £3,729,129.15 -> £3,332,303.24 (10.6%); £3,729,129.41 -> £3,332,303.49 (10.6%); £3,729,129.66 -> £3,332,303.72 (10.6%); £3,729,129.90 -> £3,332,303.94 (10.6%); £3,729,130.15 -> £3,332,304.14 (10.6%); £3,729,130.33 -> £3,332,304.34 (10.6%); £3,729,130.59 -> £3,332,304.54 (10.6%); £3,729,130.83 -> £3,332,304.73 (10.6%); £3,729,131.08 -> £3,332,304.92 (10.6%); £3,729,131.33 -> £3,332,305.10 (10.6%); £3,729,131.58 -> £3,332,305.15 (10.6%); £3,729,131.83 -> £3,332,305.20 (10.6%); £3,729,132.06 -> £3,332,305.24 (10.6%); £3,729,132.27 -> £3,332,305.29 (10.6%); £3,729,132.46 -> £3,332,305.33 (10.6%); £3,729,132.61 -> £3,332,305.37 (10.6%); £3,729,132.75 -> £3,332,305.42 (10.6%); £3,729,132.90 -> £3,332,305.46 (10.6%); £3,729,133.06 -> £3,332,305.50 (10.6%); £3,729,133.20 -> £3,332,305.55 (10.6%); £3,729,133.35 -> £3,332,305.59 (10.6%); £3,729,133.50 -> £3,332,305.63 (10.6%); £3,729,133.64 -> £3,332,305.68 (10.6%); £3,729,133.79 -> £3,332,305.72 (10.6%); £3,729,133.94 -> £3,332,305.77 (10.6%); £3,729,134.10 -> £3,332,305.81 (10.6%); £3,729,134.25 -> £3,332,306.00 (10.6%); £3,729,134.40 -> £3,332,306.20 (10.6%); £3,729,134.57 -> £3,332,306.41 (10.6%); £3,729,134.76 -> £3,332,306.63 (10.6%); £3,729,134.95 -> £3,332,306.88 (10.6%); £3,729,135.17 -> £3,332,307.16 (10.6%); £3,729,135.40 -> £3,332,307.46 (10.6%); £3,729,135.65 -> £3,332,307.78 (10.6%); £3,729,135.90 -> £3,332,307.93 (10.6%); £3,729,136.15 -> £3,332,308.09 (10.6%); £3,729,136.40 -> £3,332,308.25 (10.6%); £3,729,136.66 -> £3,332,308.40 (10.6%); £3,729,136.90 -> £3,332,308.55 (10.6%); £3,729,137.16 -> £3,332,308.70 (10.6%); £3,729,137.40 -> £3,332,308.85 (10.6%); £3,729,137.66 -> £3,332,308.99 (10.6%); £3,729,137.92 -> £3,332,309.13 (10.6%); £3,729,138.18 -> £3,332,309.28 (10.6%); £3,729,138.43 -> £3,332,309.42 (10.6%); £3,729,138.68 -> £3,332,309.56 (10.6%); £3,729,138.93 -> £3,332,309.69 (10.6%); £3,729,139.18 -> £3,332,310.00 (10.6%); £3,729,139.36 -> £3,332,310.29 (10.6%); £3,729,139.55 -> £3,332,310.55 (10.6%); £3,729,139.80 -> £3,332,310.79 (10.6%); £3,729,140.05 -> £3,332,311.02 (10.6%); £3,729,140.31 -> £3,332,311.23 (10.6%); £3,729,140.50 -> £3,332,311.44 (10.6%); £3,729,140.76 -> £3,332,311.66 (10.6%); £3,729,141.01 -> £3,332,311.86 (10.6%); £3,729,141.26 -> £3,332,312.06 (10.6%); £3,729,141.51 -> £3,332,312.26 (10.6%); £3,729,141.77 -> £3,332,312.31 (10.6%); £3,729,142.02 -> £3,332,312.35 (10.6%); £3,729,142.25 -> £3,332,312.40 (10.6%); £3,729,142.47 -> £3,332,312.44 (10.6%); £3,729,142.66 -> £3,332,312.48 (10.6%); £3,729,142.81 -> £3,332,312.52 (10.6%); £3,729,142.97 -> £3,332,312.56 (10.6%); £3,729,143.13 -> £3,332,312.61 (10.6%); £3,729,143.28 -> £3,332,312.65 (10.6%); £3,729,143.44 -> £3,332,312.69 (10.6%); £3,729,143.59 -> £3,332,312.73 (10.6%); £3,729,143.75 -> £3,332,312.78 (10.6%); £3,729,143.90 -> £3,332,312.82 (10.6%); £3,729,144.06 -> £3,332,312.86 (10.6%); £3,729,144.20 -> £3,332,312.90 (10.6%); £3,729,144.36 -> £3,332,312.95 (10.6%); £3,729,144.51 -> £3,332,313.13 (10.6%); £3,729,144.67 -> £3,332,313.31 (10.6%); £3,729,144.84 -> £3,332,313.51 (10.6%); £3,729,145.03 -> £3,332,313.72 (10.6%); £3,729,145.23 -> £3,332,313.96 (10.6%); £3,729,145.45 -> £3,332,314.22 (10.6%); £3,729,145.68 -> £3,332,314.52 (10.6%); £3,729,145.93 -> £3,332,314.83 (10.6%); £3,729,146.19 -> £3,332,314.98 (10.6%); £3,729,146.45 -> £3,332,315.13 (10.6%); £3,729,146.69 -> £3,332,315.29 (10.6%); £3,729,146.95 -> £3,332,315.45 (10.6%); £3,729,147.20 -> £3,332,315.59 (10.6%); £3,729,147.46 -> £3,332,315.74 (10.6%); £3,729,147.72 -> £3,332,315.89 (10.6%); £3,729,147.97 -> £3,332,316.03 (10.6%); £3,729,148.24 -> £3,332,316.17 (10.6%); £3,729,148.49 -> £3,332,316.31 (10.6%); £3,729,148.74 -> £3,332,316.45 (10.6%); £3,729,149.00 -> £3,332,316.58 (10.6%); £3,729,149.26 -> £3,332,316.71 (10.6%); £3,729,149.45 -> £3,332,317.01 (10.6%); £3,729,149.64 -> £3,332,317.28 (10.6%); £3,729,149.83 -> £3,332,317.53 (10.6%); £3,729,150.01 -> £3,332,317.75 (10.6%); £3,729,150.27 -> £3,332,317.95 (10.6%); £3,729,150.52 -> £3,332,318.15 (10.6%); £3,729,150.72 -> £3,332,318.35 (10.6%); £3,729,150.98 -> £3,332,318.54 (10.6%); £3,729,151.24 -> £3,332,318.73 (10.6%); £3,729,151.50 -> £3,332,318.92 (10.6%); £3,729,151.75 -> £3,332,319.10 (10.6%); £3,729,152.00 -> £3,332,319.14 (10.6%); £3,729,152.26 -> £3,332,319.19 (10.6%); £3,729,152.50 -> £3,332,319.24 (10.6%); £3,729,152.71 -> £3,332,319.28 (10.6%); £3,729,152.92 -> £3,332,319.32 (10.6%); £3,729,153.07 -> £3,332,319.36 (10.6%); £3,729,153.22 -> £3,332,319.41 (10.6%); £3,729,153.37 -> £3,332,319.45 (10.6%); £3,729,153.52 -> £3,332,319.49 (10.6%); £3,729,153.67 -> £3,332,319.53 (10.6%); £3,729,153.82 -> £3,332,319.57 (10.6%); £3,729,153.98 -> £3,332,319.62 (10.6%); £3,729,154.14 -> £3,332,319.66 (10.6%); £3,729,154.29 -> £3,332,319.70 (10.6%); £3,729,154.44 -> £3,332,319.75 (10.6%); £3,729,154.59 -> £3,332,319.80 (10.6%); £3,729,154.75 -> £3,332,319.99 (10.6%); £3,729,154.91 -> £3,332,320.20 (10.6%); £3,729,155.07 -> £3,332,320.42 (10.6%); £3,729,155.26 -> £3,332,320.66 (10.6%); £3,729,155.47 -> £3,332,320.92 (10.6%); £3,729,155.69 -> £3,332,321.20 (10.6%); £3,729,155.93 -> £3,332,321.52 (10.6%); £3,729,156.19 -> £3,332,321.85 (10.6%); £3,729,156.46 -> £3,332,322.00 (10.6%); £3,729,156.72 -> £3,332,322.16 (10.6%); £3,729,156.98 -> £3,332,322.32 (10.6%); £3,729,157.24 -> £3,332,322.49 (10.6%); £3,729,157.49 -> £3,332,322.66 (10.6%); £3,729,157.73 -> £3,332,322.82 (10.6%); £3,729,157.99 -> £3,332,322.97 (10.6%); £3,729,158.24 -> £3,332,323.12 (10.6%); £3,729,158.51 -> £3,332,323.27 (10.6%); £3,729,158.77 -> £3,332,323.41 (10.6%); £3,729,159.01 -> £3,332,323.54 (10.6%); £3,729,159.27 -> £3,332,323.68 (10.6%); £3,729,159.52 -> £3,332,323.80 (10.6%); £3,729,159.72 -> £3,332,324.12 (10.6%); £3,729,159.91 -> £3,332,324.42 (10.6%); £3,729,160.11 -> £3,332,324.68 (10.6%); £3,729,160.30 -> £3,332,324.91 (10.6%); £3,729,160.50 -> £3,332,325.14 (10.6%); £3,729,160.69 -> £3,332,325.36 (10.6%); £3,729,160.89 -> £3,332,325.59 (10.6%); £3,729,161.14 -> £3,332,325.81 (10.6%); £3,729,161.40 -> £3,332,326.03 (10.6%); £3,729,161.66 -> £3,332,326.24 (10.6%); £3,729,161.92 -> £3,332,326.44 (10.6%); £3,729,162.17 -> £3,332,326.49 (10.6%); £3,729,162.42 -> £3,332,326.53 (10.6%); £3,729,162.66 -> £3,332,326.58 (10.6%); £3,729,162.87 -> £3,332,326.62 (10.6%); £3,729,163.07 -> £3,332,326.67 (10.6%); £3,729,163.22 -> £3,332,326.71 (10.6%); £3,729,163.35 -> £3,332,326.75 (10.6%); £3,729,163.49 -> £3,332,326.79 (10.6%); £3,729,163.63 -> £3,332,326.84 (10.6%); £3,729,163.78 -> £3,332,326.88 (10.6%); £3,729,163.92 -> £3,332,326.92 (10.6%); £3,729,164.06 -> £3,332,326.96 (10.6%); £3,729,164.20 -> £3,332,327.01 (10.6%); £3,729,164.34 -> £3,332,327.05 (10.6%); £3,729,164.47 -> £3,332,327.09 (10.6%); £3,729,164.61 -> £3,332,327.14 (10.6%); £3,729,164.75 -> £3,332,327.37 (10.6%); £3,729,164.89 -> £3,332,327.59 (10.6%); £3,729,165.04 -> £3,332,327.82 (10.6%); £3,729,165.22 -> £3,332,328.06 (10.6%); £3,729,165.41 -> £3,332,328.31 (10.6%); £3,729,165.60 -> £3,332,328.57 (10.6%); £3,729,165.82 -> £3,332,328.86 (10.6%); £3,729,166.05 -> £3,332,329.17 (10.6%); £3,729,166.29 -> £3,332,329.27 (10.6%); £3,729,166.52 -> £3,332,329.38 (10.6%); £3,729,166.75 -> £3,332,329.48 (10.6%); £3,729,166.99 -> £3,332,329.59 (10.6%); £3,729,167.21 -> £3,332,329.69 (10.6%); £3,729,167.44 -> £3,332,329.80 (10.6%); £3,729,167.67 -> £3,332,329.89 (10.6%); £3,729,167.91 -> £3,332,329.98 (10.6%); £3,729,168.14 -> £3,332,330.07 (10.6%); £3,729,168.37 -> £3,332,330.15 (10.6%); £3,729,168.60 -> £3,332,330.23 (10.6%); £3,729,168.83 -> £3,332,330.32 (10.6%); £3,729,169.06 -> £3,332,330.39 (10.6%); £3,729,169.23 -> £3,332,330.66 (10.6%); £3,729,169.41 -> £3,332,330.91 (10.6%); £3,729,169.58 -> £3,332,331.15 (10.6%); £3,729,169.76 -> £3,332,331.39 (10.6%); £3,729,169.93 -> £3,332,331.63 (10.6%); £3,729,170.16 -> £3,332,331.86 (10.6%); £3,729,170.39 -> £3,332,332.09 (10.6%); £3,729,170.62 -> £3,332,332.32 (10.6%); £3,729,170.85 -> £3,332,332.55 (10.6%); £3,729,171.08 -> £3,332,332.77 (10.6%); £3,729,171.32 -> £3,332,333.01 (10.6%); £3,729,171.55 -> £3,332,333.05 (10.6%); £3,729,171.78 -> £3,332,333.10 (10.6%); £3,729,171.98 -> £3,332,333.15 (10.6%); £3,729,172.18 -> £3,332,333.19 (10.6%); £3,729,172.35 -> £3,332,333.23 (10.6%); £3,729,172.49 -> £3,332,333.27 (10.6%); £3,729,172.63 -> £3,332,333.32 (10.6%); £3,729,172.77 -> £3,332,333.36 (10.6%); £3,729,172.91 -> £3,332,333.40 (10.6%); £3,729,173.05 -> £3,332,333.45 (10.6%); £3,729,173.20 -> £3,332,333.49 (10.6%); £3,729,173.34 -> £3,332,333.53 (10.6%); £3,729,173.48 -> £3,332,333.57 (10.6%); £3,729,173.62 -> £3,332,333.61 (10.6%); £3,729,173.75 -> £3,332,333.65 (10.6%); £3,729,173.89 -> £3,332,333.69 (10.6%); £3,729,174.03 -> £3,332,333.89 (10.6%); £3,729,174.17 -> £3,332,334.08 (10.6%); £3,729,174.32 -> £3,332,334.26 (10.6%); £3,729,174.50 -> £3,332,334.45 (10.6%); £3,729,174.68 -> £3,332,334.64 (10.6%); £3,729,174.89 -> £3,332,334.83 (10.6%); £3,729,175.11 -> £3,332,335.02 (10.6%); £3,729,175.34 -> £3,332,335.22 (10.6%); £3,729,175.58 -> £3,332,335.28 (10.6%); £3,729,175.81 -> £3,332,335.34 (10.6%); £3,729,176.04 -> £3,332,335.40 (10.6%); £3,729,176.28 -> £3,332,335.45 (10.6%); £3,729,176.51 -> £3,332,335.51 (10.6%); £3,729,176.74 -> £3,332,335.56 (10.6%); £3,729,176.97 -> £3,332,335.62 (10.6%); £3,729,177.20 -> £3,332,335.67 (10.6%); £3,729,177.43 -> £3,332,335.72 (10.6%); £3,729,177.67 -> £3,332,335.77 (10.6%); £3,729,177.90 -> £3,332,335.82 (10.6%); £3,729,178.13 -> £3,332,335.88 (10.6%); £3,729,178.36 -> £3,332,335.93 (10.6%); £3,729,178.53 -> £3,332,336.12 (10.6%); £3,729,178.70 -> £3,332,336.31 (10.6%); £3,729,178.88 -> £3,332,336.51 (10.6%); £3,729,179.05 -> £3,332,336.71 (10.6%); £3,729,179.28 -> £3,332,336.91 (10.6%); £3,729,179.52 -> £3,332,337.11 (10.6%); £3,729,179.70 -> £3,332,337.30 (10.6%); £3,729,179.93 -> £3,332,337.49 (10.6%); £3,729,180.16 -> £3,332,337.68 (10.6%); £3,729,180.40 -> £3,332,337.86 (10.6%); £3,729,180.64 -> £3,332,338.05 (10.6%); £3,729,180.87 -> £3,332,338.09 (10.6%); £3,729,181.11 -> £3,332,338.14 (10.6%); £3,729,181.31 -> £3,332,338.18 (10.6%); £3,729,181.51 -> £3,332,338.22 (10.6%); £3,729,181.69 -> £3,332,338.26 (10.6%); £3,729,181.84 -> £3,332,338.30 (10.6%); £3,729,182.00 -> £3,332,338.34 (10.6%); £3,729,182.16 -> £3,332,338.38 (10.6%); £3,729,182.32 -> £3,332,338.43 (10.6%); £3,729,182.48 -> £3,332,338.47 (10.6%); £3,729,182.64 -> £3,332,338.51 (10.6%); £3,729,182.80 -> £3,332,338.55 (10.6%); £3,729,182.96 -> £3,332,338.60 (10.6%); £3,729,183.12 -> £3,332,338.64 (10.6%); £3,729,183.29 -> £3,332,338.68 (10.6%); £3,729,183.45 -> £3,332,338.73 (10.6%); £3,729,183.61 -> £3,332,338.87 (10.6%); £3,729,183.77 -> £3,332,339.02 (10.6%); £3,729,183.96 -> £3,332,339.19 (10.6%); £3,729,184.15 -> £3,332,339.38 (10.6%); £3,729,184.37 -> £3,332,339.58 (10.6%); £3,729,184.60 -> £3,332,339.82 (10.6%); £3,729,184.86 -> £3,332,340.08 (10.6%); £3,729,185.13 -> £3,332,340.35 (10.6%); £3,729,185.40 -> £3,332,340.50 (10.6%); £3,729,185.66 -> £3,332,340.64 (10.6%); £3,729,185.94 -> £3,332,340.79 (10.6%); £3,729,186.20 -> £3,332,340.94 (10.6%); £3,729,186.47 -> £3,332,341.09 (10.6%); £3,729,186.73 -> £3,332,341.23 (10.6%); £3,729,186.99 -> £3,332,341.36 (10.6%); £3,729,187.25 -> £3,332,341.50 (10.6%); £3,729,187.51 -> £3,332,341.64 (10.6%); £3,729,187.77 -> £3,332,341.78 (10.6%); £3,729,188.04 -> £3,332,341.91 (10.6%); £3,729,188.31 -> £3,332,342.04 (10.6%); £3,729,188.59 -> £3,332,342.17 (10.6%); £3,729,188.85 -> £3,332,342.45 (10.6%); £3,729,189.13 -> £3,332,342.71 (10.6%); £3,729,189.40 -> £3,332,342.93 (10.6%); £3,729,189.67 -> £3,332,343.13 (10.6%); £3,729,189.95 -> £3,332,343.31 (10.6%); £3,729,190.21 -> £3,332,343.48 (10.6%); £3,729,190.41 -> £3,332,343.66 (10.6%); £3,729,190.68 -> £3,332,343.82 (10.6%); £3,729,190.95 -> £3,332,343.98 (10.6%); £3,729,191.22 -> £3,332,344.14 (10.6%); £3,729,191.48 -> £3,332,344.29 (10.6%); £3,729,191.75 -> £3,332,344.34 (10.6%); £3,729,192.02 -> £3,332,344.38 (10.6%); £3,729,192.26 -> £3,332,344.43 (10.6%); £3,729,192.50 -> £3,332,344.47 (10.6%); £3,729,192.71 -> £3,332,344.51 (10.6%); £3,729,192.86 -> £3,332,344.55 (10.6%); £3,729,193.02 -> £3,332,344.60 (10.6%); £3,729,193.18 -> £3,332,344.64 (10.6%); £3,729,193.34 -> £3,332,344.68 (10.6%); £3,729,193.50 -> £3,332,344.72 (10.6%); £3,729,193.66 -> £3,332,344.77 (10.6%); £3,729,193.82 -> £3,332,344.81 (10.6%); £3,729,193.97 -> £3,332,344.85 (10.6%); £3,729,194.13 -> £3,332,344.89 (10.6%); £3,729,194.29 -> £3,332,344.94 (10.6%); £3,729,194.45 -> £3,332,344.99 (10.6%); £3,729,194.61 -> £3,332,345.21 (10.6%); £3,729,194.76 -> £3,332,345.45 (10.6%); £3,729,194.94 -> £3,332,345.70 (10.6%); £3,729,195.13 -> £3,332,345.95 (10.6%); £3,729,195.34 -> £3,332,346.24 (10.6%); £3,729,195.57 -> £3,332,346.56 (10.6%); £3,729,195.83 -> £3,332,346.91 (10.6%); £3,729,196.09 -> £3,332,347.27 (10.6%); £3,729,196.36 -> £3,332,347.42 (10.6%); £3,729,196.63 -> £3,332,347.57 (10.6%); £3,729,196.89 -> £3,332,347.73 (10.6%); £3,729,197.16 -> £3,332,347.88 (10.6%); £3,729,197.43 -> £3,332,348.03 (10.6%); £3,729,197.69 -> £3,332,348.18 (10.6%); £3,729,197.95 -> £3,332,348.32 (10.6%); £3,729,198.21 -> £3,332,348.45 (10.6%); £3,729,198.48 -> £3,332,348.59 (10.6%); £3,729,198.76 -> £3,332,348.73 (10.6%); £3,729,199.02 -> £3,332,348.87 (10.6%); £3,729,199.28 -> £3,332,349.00 (10.6%); £3,729,199.55 -> £3,332,349.13 (10.6%); £3,729,199.75 -> £3,332,349.47 (10.6%); £3,729,199.94 -> £3,332,349.79 (10.6%); £3,729,200.22 -> £3,332,350.08 (10.6%); £3,729,200.48 -> £3,332,350.34 (10.6%); £3,729,200.68 -> £3,332,350.58 (10.6%); £3,729,200.88 -> £3,332,350.82 (10.6%); £3,729,201.08 -> £3,332,351.06 (10.6%); £3,729,201.34 -> £3,332,351.29 (10.6%); £3,729,201.60 -> £3,332,351.52 (10.6%); £3,729,201.86 -> £3,332,351.75 (10.6%); £3,729,202.12 -> £3,332,351.97 (10.6%); £3,729,202.38 -> £3,332,352.02 (10.6%); £3,729,202.65 -> £3,332,352.07 (10.6%); £3,729,202.89 -> £3,332,352.11 (10.6%); £3,729,203.11 -> £3,332,352.16 (10.6%); £3,729,203.31 -> £3,332,352.20 (10.6%); £3,729,203.47 -> £3,332,352.24 (10.6%); £3,729,203.63 -> £3,332,352.28 (10.6%); £3,729,203.79 -> £3,332,352.33 (10.6%); £3,729,203.95 -> £3,332,352.37 (10.6%); £3,729,204.11 -> £3,332,352.41 (10.6%); £3,729,204.27 -> £3,332,352.45 (10.6%); £3,729,204.43 -> £3,332,352.50 (10.6%); £3,729,204.59 -> £3,332,352.54 (10.6%); £3,729,204.75 -> £3,332,352.58 (10.6%); £3,729,204.91 -> £3,332,352.63 (10.6%); £3,729,205.07 -> £3,332,352.67 (10.6%); £3,729,205.22 -> £3,332,352.91 (10.6%); £3,729,205.38 -> £3,332,353.17 (10.6%); £3,729,205.56 -> £3,332,353.44 (10.6%); £3,729,205.75 -> £3,332,353.73 (10.6%); £3,729,205.96 -> £3,332,354.04 (10.6%); £3,729,206.19 -> £3,332,354.36 (10.6%); £3,729,206.44 -> £3,332,354.73 (10.6%); £3,729,206.71 -> £3,332,355.10 (10.6%); £3,729,206.98 -> £3,332,355.24 (10.6%); £3,729,207.25 -> £3,332,355.39 (10.6%); £3,729,207.51 -> £3,332,355.54 (10.6%); £3,729,207.78 -> £3,332,355.69 (10.6%); £3,729,208.04 -> £3,332,355.84 (10.6%); £3,729,208.30 -> £3,332,355.99 (10.6%); £3,729,208.56 -> £3,332,356.14 (10.6%); £3,729,208.82 -> £3,332,356.28 (10.6%); £3,729,209.09 -> £3,332,356.42 (10.6%); £3,729,209.36 -> £3,332,356.56 (10.6%); £3,729,209.62 -> £3,332,356.70 (10.6%); £3,729,209.88 -> £3,332,356.83 (10.6%); £3,729,210.15 -> £3,332,356.96 (10.6%); £3,729,210.41 -> £3,332,357.32 (10.6%); £3,729,210.68 -> £3,332,357.65 (10.6%); £3,729,210.88 -> £3,332,357.95 (10.6%); £3,729,211.08 -> £3,332,358.22 (10.6%); £3,729,211.28 -> £3,332,358.49 (10.6%); £3,729,211.55 -> £3,332,358.76 (10.6%); £3,729,211.82 -> £3,332,359.01 (10.6%); £3,729,212.08 -> £3,332,359.27 (10.6%); £3,729,212.34 -> £3,332,359.51 (10.6%); £3,729,212.61 -> £3,332,359.75 (10.6%); £3,729,212.88 -> £3,332,359.99 (10.6%); £3,729,213.15 -> £3,332,360.04 (10.6%); £3,729,213.41 -> £3,332,360.09 (10.6%); £3,729,213.65 -> £3,332,360.13 (10.6%); £3,729,213.88 -> £3,332,360.17 (10.6%); £3,729,214.08 -> £3,332,360.21 (10.6%); £3,729,214.24 -> £3,332,360.26 (10.6%); £3,729,214.40 -> £3,332,360.30 (10.6%); £3,729,214.56 -> £3,332,360.34 (10.6%); £3,729,214.72 -> £3,332,360.39 (10.6%); £3,729,214.88 -> £3,332,360.43 (10.6%); £3,729,215.04 -> £3,332,360.47 (10.6%); £3,729,215.19 -> £3,332,360.52 (10.6%); £3,729,215.35 -> £3,332,360.56 (10.6%); £3,729,215.51 -> £3,332,360.60 (10.6%); £3,729,215.67 -> £3,332,360.65 (10.6%); £3,729,215.84 -> £3,332,360.69 (10.6%); £3,729,216.00 -> £3,332,360.95 (10.6%); £3,729,216.17 -> £3,332,361.20 (10.6%); £3,729,216.33 -> £3,332,361.45 (10.6%); £3,729,216.52 -> £3,332,361.72 (10.6%); £3,729,216.74 -> £3,332,362.01 (10.6%); £3,729,216.96 -> £3,332,362.33 (10.6%); £3,729,217.20 -> £3,332,362.69 (10.6%); £3,729,217.47 -> £3,332,363.07 (10.6%); £3,729,217.73 -> £3,332,363.22 (10.6%); £3,729,217.99 -> £3,332,363.37 (10.6%); £3,729,218.25 -> £3,332,363.53 (10.6%); £3,729,218.51 -> £3,332,363.68 (10.6%); £3,729,218.77 -> £3,332,363.84 (10.6%); £3,729,219.04 -> £3,332,363.98 (10.6%); £3,729,219.30 -> £3,332,364.13 (10.6%); £3,729,219.58 -> £3,332,364.27 (10.6%); £3,729,219.84 -> £3,332,364.41 (10.6%); £3,729,220.10 -> £3,332,364.55 (10.6%); £3,729,220.37 -> £3,332,364.68 (10.6%); £3,729,220.64 -> £3,332,364.82 (10.6%); £3,729,220.91 -> £3,332,364.95 (10.6%); £3,729,221.18 -> £3,332,365.30 (10.6%); £3,729,221.38 -> £3,332,365.62 (10.6%); £3,729,221.57 -> £3,332,365.91 (10.6%); £3,729,221.77 -> £3,332,366.18 (10.6%); £3,729,221.97 -> £3,332,366.44 (10.6%); £3,729,222.16 -> £3,332,366.69 (10.6%); £3,729,222.43 -> £3,332,366.95 (10.6%); £3,729,222.69 -> £3,332,367.20 (10.6%); £3,729,222.96 -> £3,332,367.44 (10.6%); £3,729,223.22 -> £3,332,367.68 (10.6%); £3,729,223.48 -> £3,332,367.91 (10.6%); £3,729,223.75 -> £3,332,367.96 (10.6%); £3,729,224.02 -> £3,332,368.00 (10.6%); £3,729,224.26 -> £3,332,368.05 (10.6%); £3,729,224.48 -> £3,332,368.09 (10.6%); £3,729,224.69 -> £3,332,368.13 (10.6%); £3,729,224.85 -> £3,332,368.17 (10.6%); £3,729,225.00 -> £3,332,368.22 (10.6%); £3,729,225.16 -> £3,332,368.26 (10.6%); £3,729,225.32 -> £3,332,368.30 (10.6%); £3,729,225.48 -> £3,332,368.34 (10.6%); £3,729,225.64 -> £3,332,368.39 (10.6%); £3,729,225.79 -> £3,332,368.43 (10.6%); £3,729,225.96 -> £3,332,368.47 (10.6%); £3,729,226.12 -> £3,332,368.51 (10.6%); £3,729,226.28 -> £3,332,368.56 (10.6%); £3,729,226.43 -> £3,332,368.60 (10.6%); £3,729,226.59 -> £3,332,368.77 (10.6%); £3,729,226.75 -> £3,332,368.94 (10.6%); £3,729,226.93 -> £3,332,369.13 (10.6%); £3,729,227.12 -> £3,332,369.33 (10.6%); £3,729,227.33 -> £3,332,369.56 (10.6%); £3,729,227.56 -> £3,332,369.82 (10.6%); £3,729,227.81 -> £3,332,370.10 (10.6%); £3,729,228.08 -> £3,332,370.40 (10.6%); £3,729,228.35 -> £3,332,370.55 (10.6%); £3,729,228.63 -> £3,332,370.70 (10.6%); £3,729,228.89 -> £3,332,370.86 (10.6%); £3,729,229.16 -> £3,332,371.01 (10.6%); £3,729,229.42 -> £3,332,371.17 (10.6%); £3,729,229.70 -> £3,332,371.32 (10.6%); £3,729,229.95 -> £3,332,371.46 (10.6%); £3,729,230.23 -> £3,332,371.61 (10.6%); £3,729,230.49 -> £3,332,371.75 (10.6%); £3,729,230.75 -> £3,332,371.89 (10.6%); £3,729,231.02 -> £3,332,372.03 (10.6%); £3,729,231.28 -> £3,332,372.17 (10.6%); £3,729,231.55 -> £3,332,372.30 (10.6%); £3,729,231.82 -> £3,332,372.59 (10.6%); £3,729,232.09 -> £3,332,372.86 (10.6%); £3,729,232.35 -> £3,332,373.09 (10.6%); £3,729,232.61 -> £3,332,373.30 (10.6%); £3,729,232.88 -> £3,332,373.50 (10.6%); £3,729,233.14 -> £3,332,373.70 (10.6%); £3,729,233.41 -> £3,332,373.89 (10.6%); £3,729,233.67 -> £3,332,374.08 (10.6%); £3,729,233.94 -> £3,332,374.26 (10.6%); £3,729,234.21 -> £3,332,374.43 (10.6%); £3,729,234.47 -> £3,332,374.61 (10.6%); £3,729,234.74 -> £3,332,374.65 (10.6%); £3,729,235.00 -> £3,332,374.70 (10.6%); £3,729,235.26 -> £3,332,374.75 (10.6%); £3,729,235.48 -> £3,332,374.79 (10.6%); £3,729,235.69 -> £3,332,374.83 (10.6%); £3,729,235.83 -> £3,332,374.88 (10.6%); £3,729,235.96 -> £3,332,374.92 (10.6%); £3,729,236.11 -> £3,332,374.96 (10.6%); £3,729,236.25 -> £3,332,375.01 (10.6%); £3,729,236.38 -> £3,332,375.05 (10.6%); £3,729,236.52 -> £3,332,375.09 (10.6%); £3,729,236.66 -> £3,332,375.14 (10.6%); £3,729,236.80 -> £3,332,375.18 (10.6%); £3,729,236.95 -> £3,332,375.22 (10.6%); £3,729,237.09 -> £3,332,375.27 (10.6%); £3,729,237.22 -> £3,332,375.31 (10.6%); £3,729,237.36 -> £3,332,375.48 (10.6%); £3,729,237.51 -> £3,332,375.65 (10.6%); £3,729,237.66 -> £3,332,375.82 (10.6%); £3,729,237.83 -> £3,332,375.99 (10.6%); £3,729,238.02 -> £3,332,376.17 (10.6%); £3,729,238.22 -> £3,332,376.37 (10.6%); £3,729,238.43 -> £3,332,376.60 (10.6%); £3,729,238.66 -> £3,332,376.84 (10.6%); £3,729,238.90 -> £3,332,376.94 (10.6%); £3,729,239.13 -> £3,332,377.05 (10.6%); £3,729,239.37 -> £3,332,377.16 (10.6%); £3,729,239.60 -> £3,332,377.27 (10.6%); £3,729,239.82 -> £3,332,377.37 (10.6%); £3,729,240.06 -> £3,332,377.46 (10.6%); £3,729,240.29 -> £3,332,377.55 (10.6%); £3,729,240.53 -> £3,332,377.64 (10.6%); £3,729,240.76 -> £3,332,377.73 (10.6%); £3,729,240.98 -> £3,332,377.81 (10.6%); £3,729,241.21 -> £3,332,377.89 (10.6%); £3,729,241.45 -> £3,332,377.97 (10.6%); £3,729,241.69 -> £3,332,378.05 (10.6%); £3,729,241.92 -> £3,332,378.26 (10.6%); £3,729,242.10 -> £3,332,378.45 (10.6%); £3,729,242.33 -> £3,332,378.63 (10.6%); £3,729,242.51 -> £3,332,378.81 (10.6%); £3,729,242.68 -> £3,332,378.98 (10.6%); £3,729,242.85 -> £3,332,379.15 (10.6%); £3,729,243.03 -> £3,332,379.33 (10.6%); £3,729,243.26 -> £3,332,379.50 (10.6%); £3,729,243.49 -> £3,332,379.68 (10.6%); £3,729,243.72 -> £3,332,379.84 (10.6%); £3,729,243.95 -> £3,332,380.01 (10.6%); £3,729,244.18 -> £3,332,380.05 (10.6%); £3,729,244.41 -> £3,332,380.10 (10.6%); £3,729,244.62 -> £3,332,380.15 (10.6%); £3,729,244.81 -> £3,332,380.19 (10.6%); £3,729,244.99 -> £3,332,380.23 (10.6%); £3,729,245.13 -> £3,332,380.28 (10.6%); £3,729,245.28 -> £3,332,380.32 (10.6%); £3,729,245.42 -> £3,332,380.36 (10.6%); £3,729,245.55 -> £3,332,380.41 (10.6%); £3,729,245.70 -> £3,332,380.45 (10.6%); £3,729,245.83 -> £3,332,380.49 (10.6%); £3,729,245.98 -> £3,332,380.54 (10.6%); £3,729,246.11 -> £3,332,380.58 (10.6%); £3,729,246.26 -> £3,332,380.62 (10.6%); £3,729,246.40 -> £3,332,380.66 (10.6%); £3,729,246.54 -> £3,332,380.70 (10.6%); £3,729,246.68 -> £3,332,380.86 (10.6%); £3,729,246.82 -> £3,332,381.01 (10.6%); £3,729,246.98 -> £3,332,381.16 (10.6%); £3,729,247.14 -> £3,332,381.32 (10.6%); £3,729,247.32 -> £3,332,381.48 (10.6%); £3,729,247.52 -> £3,332,381.64 (10.6%); £3,729,247.75 -> £3,332,381.80 (10.6%); £3,729,247.99 -> £3,332,381.96 (10.6%); £3,729,248.22 -> £3,332,382.02 (10.6%); £3,729,248.45 -> £3,332,382.08 (10.6%); £3,729,248.69 -> £3,332,382.14 (10.6%); £3,729,248.92 -> £3,332,382.20 (10.6%); £3,729,249.16 -> £3,332,382.25 (10.6%); £3,729,249.39 -> £3,332,382.31 (10.6%); £3,729,249.63 -> £3,332,382.36 (10.6%); £3,729,249.87 -> £3,332,382.41 (10.6%); £3,729,250.11 -> £3,332,382.47 (10.6%); £3,729,250.34 -> £3,332,382.52 (10.6%); £3,729,250.58 -> £3,332,382.57 (10.6%); £3,729,250.82 -> £3,332,382.63 (10.6%); £3,729,251.06 -> £3,332,382.68 (10.6%); £3,729,251.29 -> £3,332,382.84 (10.6%); £3,729,251.52 -> £3,332,383.00 (10.6%); £3,729,251.68 -> £3,332,383.16 (10.6%); £3,729,251.86 -> £3,332,383.32 (10.6%); £3,729,252.04 -> £3,332,383.48 (10.6%); £3,729,252.22 -> £3,332,383.64 (10.6%); £3,729,252.39 -> £3,332,383.80 (10.6%); £3,729,252.63 -> £3,332,383.95 (10.6%); £3,729,252.86 -> £3,332,384.11 (10.6%); £3,729,253.10 -> £3,332,384.27 (10.6%); £3,729,253.33 -> £3,332,384.43 (10.6%); £3,729,253.56 -> £3,332,384.47 (10.6%); £3,729,253.80 -> £3,332,384.52 (10.6%); £3,729,254.02 -> £3,332,384.56 (10.6%); £3,729,254.23 -> £3,332,384.61 (10.6%); £3,729,254.41 -> £3,332,384.65 (10.6%); £3,729,254.57 -> £3,332,384.69 (10.6%); £3,729,254.73 -> £3,332,384.73 (10.6%); £3,729,254.89 -> £3,332,384.78 (10.6%); £3,729,255.05 -> £3,332,384.82 (10.6%); £3,729,255.21 -> £3,332,384.86 (10.6%); £3,729,255.38 -> £3,332,384.91 (10.6%); £3,729,255.54 -> £3,332,384.95 (10.6%); £3,729,255.70 -> £3,332,385.00 (10.6%); £3,729,255.87 -> £3,332,385.04 (10.6%); £3,729,256.04 -> £3,332,385.08 (10.6%); £3,729,256.19 -> £3,332,385.13 (10.6%); £3,729,256.37 -> £3,332,385.30 (10.6%); £3,729,256.53 -> £3,332,385.48 (10.6%); £3,729,256.71 -> £3,332,385.66 (10.6%); £3,729,256.91 -> £3,332,385.86 (10.6%); £3,729,257.14 -> £3,332,386.08 (10.6%); £3,729,257.37 -> £3,332,386.33 (10.6%); £3,729,257.62 -> £3,332,386.63 (10.6%); £3,729,257.88 -> £3,332,386.93 (10.6%); £3,729,258.16 -> £3,332,387.09 (10.6%); £3,729,258.44 -> £3,332,387.24 (10.6%); £3,729,258.72 -> £3,332,387.39 (10.6%); £3,729,258.99 -> £3,332,387.54 (10.6%); £3,729,259.25 -> £3,332,387.68 (10.6%); £3,729,259.52 -> £3,332,387.83 (10.6%); £3,729,259.79 -> £3,332,387.96 (10.6%); £3,729,260.05 -> £3,332,388.10 (10.6%); £3,729,260.33 -> £3,332,388.24 (10.6%); £3,729,260.59 -> £3,332,388.37 (10.6%); £3,729,260.86 -> £3,332,388.51 (10.6%); £3,729,261.14 -> £3,332,388.64 (10.6%); £3,729,261.40 -> £3,332,388.76 (10.6%); £3,729,261.61 -> £3,332,389.05 (10.6%); £3,729,261.81 -> £3,332,389.31 (10.6%); £3,729,262.01 -> £3,332,389.54 (10.6%); £3,729,262.22 -> £3,332,389.74 (10.6%); £3,729,262.43 -> £3,332,389.94 (10.6%); £3,729,262.70 -> £3,332,390.14 (10.6%); £3,729,262.98 -> £3,332,390.33 (10.6%); £3,729,263.26 -> £3,332,390.51 (10.6%); £3,729,263.53 -> £3,332,390.69 (10.6%); £3,729,263.80 -> £3,332,390.86 (10.6%); £3,729,264.07 -> £3,332,391.03 (10.6%); £3,729,264.34 -> £3,332,391.08 (10.6%); £3,729,264.61 -> £3,332,391.13 (10.6%); £3,729,264.86 -> £3,332,391.17 (10.6%); £3,729,265.10 -> £3,332,391.21 (10.6%); £3,729,265.31 -> £3,332,391.26 (10.6%); £3,729,265.48 -> £3,332,391.30 (10.6%); £3,729,265.65 -> £3,332,391.34 (10.6%); £3,729,265.81 -> £3,332,391.39 (10.6%); £3,729,265.98 -> £3,332,391.43 (10.6%); £3,729,266.15 -> £3,332,391.47 (10.6%); £3,729,266.31 -> £3,332,391.52 (10.6%); £3,729,266.48 -> £3,332,391.56 (10.6%); £3,729,266.64 -> £3,332,391.60 (10.6%); £3,729,266.81 -> £3,332,391.65 (10.6%); £3,729,266.97 -> £3,332,391.69 (10.6%); £3,729,267.14 -> £3,332,391.74 (10.6%); £3,729,267.31 -> £3,332,391.94 (10.6%); £3,729,267.48 -> £3,332,392.14 (10.6%); £3,729,267.66 -> £3,332,392.35 (10.6%); £3,729,267.86 -> £3,332,392.58 (10.6%); £3,729,268.08 -> £3,332,392.82 (10.6%); £3,729,268.32 -> £3,332,393.10 (10.6%); £3,729,268.57 -> £3,332,393.42 (10.6%); £3,729,268.85 -> £3,332,393.74 (10.6%); £3,729,269.12 -> £3,332,393.89 (10.6%); £3,729,269.40 -> £3,332,394.04 (10.6%); £3,729,269.68 -> £3,332,394.19 (10.6%); £3,729,269.95 -> £3,332,394.35 (10.6%); £3,729,270.23 -> £3,332,394.50 (10.6%); £3,729,270.50 -> £3,332,394.65 (10.6%); £3,729,270.77 -> £3,332,394.79 (10.6%); £3,729,271.05 -> £3,332,394.93 (10.6%); £3,729,271.32 -> £3,332,395.07 (10.6%); £3,729,271.59 -> £3,332,395.20 (10.6%); £3,729,271.85 -> £3,332,395.34 (10.6%); £3,729,272.12 -> £3,332,395.47 (10.6%); £3,729,272.40 -> £3,332,395.60 (10.6%); £3,729,272.60 -> £3,332,395.90 (10.6%); £3,729,272.81 -> £3,332,396.17 (10.6%); £3,729,273.02 -> £3,332,396.41 (10.6%); £3,729,273.23 -> £3,332,396.63 (10.6%); £3,729,273.43 -> £3,332,396.84 (10.6%); £3,729,273.63 -> £3,332,397.04 (10.6%); £3,729,273.84 -> £3,332,397.23 (10.6%); £3,729,274.12 -> £3,332,397.43 (10.6%); £3,729,274.39 -> £3,332,397.62 (10.6%); £3,729,274.66 -> £3,332,397.80 (10.6%); £3,729,274.93 -> £3,332,397.98 (10.6%); £3,729,275.21 -> £3,332,398.03 (10.6%); £3,729,275.48 -> £3,332,398.08 (10.6%); £3,729,275.73 -> £3,332,398.12 (10.6%); £3,729,275.96 -> £3,332,398.17 (10.6%); £3,729,276.17 -> £3,332,398.21 (10.6%); £3,729,276.34 -> £3,332,398.25 (10.6%); £3,729,276.50 -> £3,332,398.29 (10.6%); £3,729,276.66 -> £3,332,398.33 (10.6%); £3,729,276.82 -> £3,332,398.38 (10.6%); £3,729,276.99 -> £3,332,398.42 (10.6%); £3,729,277.16 -> £3,332,398.46 (10.6%); £3,729,277.32 -> £3,332,398.50 (10.6%); £3,729,277.49 -> £3,332,398.54 (10.6%); £3,729,277.65 -> £3,332,398.59 (10.6%); £3,729,277.82 -> £3,332,398.63 (10.6%); £3,729,277.99 -> £3,332,398.68 (10.6%); £3,729,278.16 -> £3,332,398.95 (10.6%); £3,729,278.32 -> £3,332,399.23 (10.6%); £3,729,278.50 -> £3,332,399.54 (10.6%); £3,729,278.71 -> £3,332,399.84 (10.6%); £3,729,278.93 -> £3,332,400.18 (10.6%); £3,729,279.17 -> £3,332,400.54 (10.6%); £3,729,279.43 -> £3,332,400.93 (10.6%); £3,729,279.71 -> £3,332,401.32 (10.6%); £3,729,279.99 -> £3,332,401.47 (10.6%); £3,729,280.28 -> £3,332,401.62 (10.6%); £3,729,280.55 -> £3,332,401.76 (10.6%); £3,729,280.83 -> £3,332,401.92 (10.6%); £3,729,281.10 -> £3,332,402.07 (10.6%); £3,729,281.39 -> £3,332,402.22 (10.6%); £3,729,281.65 -> £3,332,402.36 (10.6%); £3,729,281.92 -> £3,332,402.50 (10.6%); £3,729,282.20 -> £3,332,402.64 (10.6%); £3,729,282.48 -> £3,332,402.78 (10.6%); £3,729,282.75 -> £3,332,402.91 (10.6%); £3,729,283.02 -> £3,332,403.05 (10.6%); £3,729,283.30 -> £3,332,403.17 (10.6%); £3,729,283.51 -> £3,332,403.55 (10.6%); £3,729,283.72 -> £3,332,403.92 (10.6%); £3,729,283.99 -> £3,332,404.24 (10.6%); £3,729,284.20 -> £3,332,404.53 (10.6%); £3,729,284.40 -> £3,332,404.82 (10.6%); £3,729,284.61 -> £3,332,405.11 (10.6%); £3,729,284.87 -> £3,332,405.40 (10.6%); £3,729,285.16 -> £3,332,405.69 (10.6%); £3,729,285.42 -> £3,332,405.97 (10.6%); £3,729,285.69 -> £3,332,406.24 (10.6%); £3,729,285.96 -> £3,332,406.50 (10.6%); £3,729,286.24 -> £3,332,406.54 (10.6%); £3,729,286.52 -> £3,332,406.59 (10.6%); £3,729,286.78 -> £3,332,406.64 (10.6%); £3,729,287.02 -> £3,332,406.68 (10.6%); £3,729,287.24 -> £3,332,406.72 (10.6%); £3,729,287.41 -> £3,332,406.76 (10.6%); £3,729,287.56 -> £3,332,406.80 (10.6%); £3,729,287.73 -> £3,332,406.85 (10.6%); £3,729,287.89 -> £3,332,406.89 (10.6%); £3,729,288.06 -> £3,332,406.93 (10.6%); £3,729,288.23 -> £3,332,406.97 (10.6%); £3,729,288.39 -> £3,332,407.01 (10.6%); £3,729,288.56 -> £3,332,407.06 (10.6%); £3,729,288.72 -> £3,332,407.10 (10.6%); £3,729,288.88 -> £3,332,407.14 (10.6%); £3,729,289.05 -> £3,332,407.19 (10.6%); £3,729,289.21 -> £3,332,407.47 (10.6%); £3,729,289.38 -> £3,332,407.77 (10.6%); £3,729,289.57 -> £3,332,408.07 (10.6%); £3,729,289.77 -> £3,332,408.41 (10.6%); £3,729,289.99 -> £3,332,408.76 (10.6%); £3,729,290.23 -> £3,332,409.15 (10.6%); £3,729,290.48 -> £3,332,409.56 (10.6%); £3,729,290.76 -> £3,332,409.97 (10.6%); £3,729,291.03 -> £3,332,410.12 (10.6%); £3,729,291.31 -> £3,332,410.26 (10.6%); £3,729,291.59 -> £3,332,410.42 (10.6%); £3,729,291.87 -> £3,332,410.57 (10.6%); £3,729,292.14 -> £3,332,410.73 (10.6%); £3,729,292.41 -> £3,332,410.87 (10.6%); £3,729,292.68 -> £3,332,411.01 (10.6%); £3,729,292.96 -> £3,332,411.14 (10.6%); £3,729,293.23 -> £3,332,411.28 (10.6%); £3,729,293.51 -> £3,332,411.41 (10.6%); £3,729,293.78 -> £3,332,411.55 (10.6%); £3,729,294.05 -> £3,332,411.68 (10.6%); £3,729,294.32 -> £3,332,411.80 (10.6%); £3,729,294.53 -> £3,332,412.21 (10.6%); £3,729,294.81 -> £3,332,412.59 (10.6%); £3,729,295.02 -> £3,332,412.94 (10.6%); £3,729,295.28 -> £3,332,413.26 (10.6%); £3,729,295.55 -> £3,332,413.57 (10.6%); £3,729,295.83 -> £3,332,413.88 (10.6%); £3,729,296.10 -> £3,332,414.19 (10.6%); £3,729,296.37 -> £3,332,414.49 (10.6%); £3,729,296.66 -> £3,332,414.78 (10.6%); £3,729,296.93 -> £3,332,415.06 (10.6%); £3,729,297.20 -> £3,332,415.34 (10.6%); £3,729,297.49 -> £3,332,415.39 (10.6%); £3,729,297.76 -> £3,332,415.44 (10.6%); £3,729,298.02 -> £3,332,415.48 (10.6%); £3,729,298.25 -> £3,332,415.53 (10.6%); £3,729,298.47 -> £3,332,415.57 (10.6%); £3,729,298.63 -> £3,332,415.61 (10.6%); £3,729,298.80 -> £3,332,415.65 (10.6%); £3,729,298.96 -> £3,332,415.69 (10.6%); £3,729,299.12 -> £3,332,415.73 (10.6%); £3,729,299.28 -> £3,332,415.77 (10.6%); £3,729,299.45 -> £3,332,415.81 (10.6%); £3,729,299.62 -> £3,332,415.86 (10.6%); £3,729,299.78 -> £3,332,415.90 (10.6%); £3,729,299.94 -> £3,332,415.94 (10.6%); £3,729,300.10 -> £3,332,415.99 (10.6%); £3,729,300.27 -> £3,332,416.03 (10.6%); £3,729,300.44 -> £3,332,416.26 (10.6%); £3,729,300.60 -> £3,332,416.50 (10.6%); £3,729,300.78 -> £3,332,416.75 (10.6%); £3,729,300.98 -> £3,332,417.01 (10.6%); £3,729,301.20 -> £3,332,417.30 (10.6%); £3,729,301.43 -> £3,332,417.61 (10.6%); £3,729,301.69 -> £3,332,417.97 (10.6%); £3,729,301.95 -> £3,332,418.33 (10.6%); £3,729,302.22 -> £3,332,418.48 (10.6%); £3,729,302.50 -> £3,332,418.65 (10.6%); £3,729,302.77 -> £3,332,418.81 (10.6%); £3,729,303.04 -> £3,332,418.97 (10.6%); £3,729,303.30 -> £3,332,419.14 (10.6%); £3,729,303.56 -> £3,332,419.30 (10.6%); £3,729,303.83 -> £3,332,419.45 (10.6%); £3,729,304.10 -> £3,332,419.60 (10.6%); £3,729,304.38 -> £3,332,419.73 (10.6%); £3,729,304.66 -> £3,332,419.88 (10.6%); £3,729,304.92 -> £3,332,420.01 (10.6%); £3,729,305.20 -> £3,332,420.15 (10.6%); £3,729,305.47 -> £3,332,420.28 (10.6%); £3,729,305.74 -> £3,332,420.63 (10.6%); £3,729,306.00 -> £3,332,420.96 (10.6%); £3,729,306.28 -> £3,332,421.25 (10.6%); £3,729,306.56 -> £3,332,421.52 (10.6%); £3,729,306.83 -> £3,332,421.77 (10.6%); £3,729,307.04 -> £3,332,422.01 (10.6%); £3,729,307.24 -> £3,332,422.26 (10.6%); £3,729,307.52 -> £3,332,422.49 (10.6%); £3,729,307.78 -> £3,332,422.73 (10.6%); £3,729,308.05 -> £3,332,422.97 (10.6%); £3,729,308.32 -> £3,332,423.19 (10.6%); £3,729,308.59 -> £3,332,423.24 (10.6%); £3,729,308.86 -> £3,332,423.28 (10.6%); £3,729,309.11 -> £3,332,423.33 (10.6%); £3,729,309.35 -> £3,332,423.37 (10.6%); £3,729,309.56 -> £3,332,423.41 (10.6%); £3,729,309.70 -> £3,332,423.45 (10.6%); £3,729,309.85 -> £3,332,423.49 (10.6%); £3,729,309.99 -> £3,332,423.54 (10.6%); £3,729,310.13 -> £3,332,423.58 (10.6%); £3,729,310.27 -> £3,332,423.62 (10.6%); £3,729,310.41 -> £3,332,423.66 (10.6%); £3,729,310.56 -> £3,332,423.70 (10.6%); £3,729,310.70 -> £3,332,423.74 (10.6%); £3,729,310.84 -> £3,332,423.78 (10.6%); £3,729,310.98 -> £3,332,423.83 (10.6%); £3,729,311.13 -> £3,332,423.87 (10.6%); £3,729,311.27 -> £3,332,424.08 (10.6%); £3,729,311.41 -> £3,332,424.30 (10.6%); £3,729,311.57 -> £3,332,424.52 (10.6%); £3,729,311.75 -> £3,332,424.75 (10.6%); £3,729,311.94 -> £3,332,424.99 (10.6%); £3,729,312.15 -> £3,332,425.25 (10.6%); £3,729,312.37 -> £3,332,425.54 (10.6%); £3,729,312.61 -> £3,332,425.84 (10.6%); £3,729,312.84 -> £3,332,425.95 (10.6%); £3,729,313.08 -> £3,332,426.06 (10.6%); £3,729,313.32 -> £3,332,426.17 (10.6%); £3,729,313.57 -> £3,332,426.27 (10.6%); £3,729,313.80 -> £3,332,426.37 (10.6%); £3,729,314.04 -> £3,332,426.47 (10.6%); £3,729,314.28 -> £3,332,426.55 (10.6%); £3,729,314.51 -> £3,332,426.64 (10.6%); £3,729,314.75 -> £3,332,426.73 (10.6%); £3,729,315.00 -> £3,332,426.81 (10.6%); £3,729,315.23 -> £3,332,426.89 (10.6%); £3,729,315.47 -> £3,332,426.97 (10.6%); £3,729,315.72 -> £3,332,427.05 (10.6%); £3,729,315.95 -> £3,332,427.31 (10.6%); £3,729,316.19 -> £3,332,427.57 (10.6%); £3,729,316.42 -> £3,332,427.81 (10.6%); £3,729,316.60 -> £3,332,428.04 (10.6%); £3,729,316.84 -> £3,332,428.26 (10.6%); £3,729,317.02 -> £3,332,428.49 (10.6%); £3,729,317.20 -> £3,332,428.72 (10.6%); £3,729,317.44 -> £3,332,428.94 (10.6%); £3,729,317.68 -> £3,332,429.17 (10.6%); £3,729,317.92 -> £3,332,429.39 (10.6%); £3,729,318.16 -> £3,332,429.62 (10.6%); £3,729,318.41 -> £3,332,429.66 (10.6%); £3,729,318.64 -> £3,332,429.71 (10.6%); £3,729,318.86 -> £3,332,429.75 (10.6%); £3,729,319.07 -> £3,332,429.79 (10.6%); £3,729,319.26 -> £3,332,429.84 (10.6%); £3,729,319.40 -> £3,332,429.88 (10.6%); £3,729,319.54 -> £3,332,429.92 (10.6%); £3,729,319.68 -> £3,332,429.96 (10.6%); £3,729,319.82 -> £3,332,430.00 (10.6%); £3,729,319.96 -> £3,332,430.05 (10.6%); £3,729,320.10 -> £3,332,430.09 (10.6%); £3,729,320.24 -> £3,332,430.13 (10.6%); £3,729,320.38 -> £3,332,430.17 (10.6%); £3,729,320.53 -> £3,332,430.21 (10.6%); £3,729,320.67 -> £3,332,430.25 (10.6%); £3,729,320.80 -> £3,332,430.29 (10.6%); £3,729,320.94 -> £3,332,430.52 (10.6%); £3,729,321.08 -> £3,332,430.74 (10.6%); £3,729,321.23 -> £3,332,430.97 (10.6%); £3,729,321.40 -> £3,332,431.19 (10.6%); £3,729,321.59 -> £3,332,431.42 (10.6%); £3,729,321.79 -> £3,332,431.65 (10.6%); £3,729,322.01 -> £3,332,431.89 (10.6%); £3,729,322.25 -> £3,332,432.13 (10.6%); £3,729,322.48 -> £3,332,432.18 (10.6%); £3,729,322.72 -> £3,332,432.24 (10.6%); £3,729,322.95 -> £3,332,432.30 (10.6%); £3,729,323.19 -> £3,332,432.35 (10.6%); £3,729,323.43 -> £3,332,432.41 (10.6%); £3,729,323.67 -> £3,332,432.46 (10.6%); £3,729,323.89 -> £3,332,432.52 (10.6%); £3,729,324.13 -> £3,332,432.57 (10.6%); £3,729,324.36 -> £3,332,432.63 (10.6%); £3,729,324.60 -> £3,332,432.68 (10.6%); £3,729,324.83 -> £3,332,432.73 (10.6%); £3,729,325.06 -> £3,332,432.78 (10.6%); £3,729,325.30 -> £3,332,432.84 (10.6%); £3,729,325.53 -> £3,332,433.07 (10.6%); £3,729,325.76 -> £3,332,433.30 (10.6%); £3,729,325.94 -> £3,332,433.53 (10.6%); £3,729,326.12 -> £3,332,433.76 (10.6%); £3,729,326.30 -> £3,332,433.98 (10.6%); £3,729,326.47 -> £3,332,434.21 (10.6%); £3,729,326.65 -> £3,332,434.44 (10.6%); £3,729,326.89 -> £3,332,434.68 (10.6%); £3,729,327.12 -> £3,332,434.91 (10.6%); £3,729,327.35 -> £3,332,435.13 (10.6%); £3,729,327.58 -> £3,332,435.35 (10.6%); £3,729,327.81 -> £3,332,435.39 (10.6%); £3,729,328.05 -> £3,332,435.44 (10.6%); £3,729,328.27 -> £3,332,435.48 (10.6%); £3,729,328.47 -> £3,332,435.52 (10.6%); £3,729,328.65 -> £3,332,435.56 (10.6%); £3,729,328.81 -> £3,332,435.60 (10.6%); £3,729,328.97 -> £3,332,435.64 (10.6%); £3,729,329.12 -> £3,332,435.69 (10.6%); £3,729,329.28 -> £3,332,435.73 (10.6%); £3,729,329.43 -> £3,332,435.77 (10.6%); £3,729,329.59 -> £3,332,435.81 (10.6%); £3,729,329.74 -> £3,332,435.85 (10.6%); £3,729,329.90 -> £3,332,435.90 (10.6%); £3,729,330.05 -> £3,332,435.94 (10.6%); £3,729,330.21 -> £3,332,435.98 (10.6%); £3,729,330.36 -> £3,332,436.03 (10.6%); £3,729,330.51 -> £3,332,436.28 (10.6%); £3,729,330.67 -> £3,332,436.55 (10.6%); £3,729,330.84 -> £3,332,436.82 (10.6%); £3,729,331.04 -> £3,332,437.10 (10.6%); £3,729,331.25 -> £3,332,437.41 (10.6%); £3,729,331.47 -> £3,332,437.75 (10.6%); £3,729,331.71 -> £3,332,438.13 (10.6%); £3,729,331.98 -> £3,332,438.52 (10.6%); £3,729,332.23 -> £3,332,438.67 (10.6%); £3,729,332.48 -> £3,332,438.82 (10.6%); £3,729,332.74 -> £3,332,438.98 (10.6%); £3,729,333.00 -> £3,332,439.13 (10.6%); £3,729,333.26 -> £3,332,439.29 (10.6%); £3,729,333.52 -> £3,332,439.43 (10.6%); £3,729,333.78 -> £3,332,439.58 (10.6%); £3,729,334.04 -> £3,332,439.72 (10.6%); £3,729,334.30 -> £3,332,439.86 (10.6%); £3,729,334.56 -> £3,332,440.00 (10.6%); £3,729,334.82 -> £3,332,440.13 (10.6%); £3,729,335.08 -> £3,332,440.27 (10.6%); £3,729,335.34 -> £3,332,440.40 (10.6%); £3,729,335.54 -> £3,332,440.76 (10.6%); £3,729,335.73 -> £3,332,441.10 (10.6%); £3,729,335.92 -> £3,332,441.40 (10.6%); £3,729,336.12 -> £3,332,441.68 (10.6%); £3,729,336.31 -> £3,332,441.95 (10.6%); £3,729,336.50 -> £3,332,442.21 (10.6%); £3,729,336.70 -> £3,332,442.47 (10.6%); £3,729,336.96 -> £3,332,442.73 (10.6%); £3,729,337.22 -> £3,332,442.99 (10.6%); £3,729,337.47 -> £3,332,443.23 (10.6%); £3,729,337.74 -> £3,332,443.48 (10.6%); £3,729,337.99 -> £3,332,443.53 (10.6%); £3,729,338.26 -> £3,332,443.57 (10.6%); £3,729,338.49 -> £3,332,443.62 (10.6%); £3,729,338.71 -> £3,332,443.66 (10.6%); £3,729,338.92 -> £3,332,443.70 (10.6%); £3,729,339.07 -> £3,332,443.74 (10.6%); £3,729,339.24 -> £3,332,443.79 (10.6%); £3,729,339.39 -> £3,332,443.83 (10.6%); £3,729,339.55 -> £3,332,443.87 (10.6%); £3,729,339.71 -> £3,332,443.91 (10.6%); £3,729,339.86 -> £3,332,443.95 (10.6%); £3,729,340.02 -> £3,332,443.99 (10.6%); £3,729,340.17 -> £3,332,444.04 (10.6%); £3,729,340.32 -> £3,332,444.08 (10.6%); £3,729,340.48 -> £3,332,444.12 (10.6%); £3,729,340.63 -> £3,332,444.17 (10.6%); £3,729,340.79 -> £3,332,444.39 (10.6%); £3,729,340.95 -> £3,332,444.61 (10.6%); £3,729,341.13 -> £3,332,444.85 (10.6%); £3,729,341.32 -> £3,332,445.10 (10.6%); £3,729,341.53 -> £3,332,445.38 (10.6%); £3,729,341.76 -> £3,332,445.68 (10.6%); £3,729,342.00 -> £3,332,446.02 (10.6%); £3,729,342.25 -> £3,332,446.37 (10.6%); £3,729,342.51 -> £3,332,446.52 (10.6%); £3,729,342.76 -> £3,332,446.67 (10.6%); £3,729,343.03 -> £3,332,446.82 (10.6%); £3,729,343.28 -> £3,332,446.98 (10.6%); £3,729,343.54 -> £3,332,447.13 (10.6%); £3,729,343.81 -> £3,332,447.28 (10.6%); £3,729,344.07 -> £3,332,447.42 (10.6%); £3,729,344.33 -> £3,332,447.56 (10.6%); £3,729,344.59 -> £3,332,447.70 (10.6%); £3,729,344.85 -> £3,332,447.84 (10.6%); £3,729,345.11 -> £3,332,447.98 (10.6%); £3,729,345.36 -> £3,332,448.12 (10.6%); £3,729,345.62 -> £3,332,448.25 (10.6%); £3,729,345.88 -> £3,332,448.59 (10.6%); £3,729,346.14 -> £3,332,448.91 (10.6%); £3,729,346.40 -> £3,332,449.20 (10.6%); £3,729,346.66 -> £3,332,449.45 (10.6%); £3,729,346.91 -> £3,332,449.70 (10.6%); £3,729,347.17 -> £3,332,449.94 (10.6%); £3,729,347.42 -> £3,332,450.18 (10.6%); £3,729,347.69 -> £3,332,450.41 (10.6%); £3,729,347.94 -> £3,332,450.64 (10.6%); £3,729,348.20 -> £3,332,450.86 (10.6%); £3,729,348.47 -> £3,332,451.08 (10.6%); £3,729,348.73 -> £3,332,451.12 (10.6%); £3,729,348.99 -> £3,332,451.17 (10.6%); £3,729,349.23 -> £3,332,451.21 (10.6%); £3,729,349.46 -> £3,332,451.25 (10.6%); £3,729,349.66 -> £3,332,451.29 (10.6%); £3,729,349.81 -> £3,332,451.34 (10.6%); £3,729,349.96 -> £3,332,451.38 (10.6%); £3,729,350.12 -> £3,332,451.42 (10.6%); £3,729,350.27 -> £3,332,451.46 (10.6%); £3,729,350.42 -> £3,332,451.51 (10.6%); £3,729,350.58 -> £3,332,451.55 (10.6%); £3,729,350.73 -> £3,332,451.59 (10.6%); £3,729,350.89 -> £3,332,451.63 (10.6%); £3,729,351.04 -> £3,332,451.68 (10.6%); £3,729,351.20 -> £3,332,451.72 (10.6%); £3,729,351.36 -> £3,332,451.77 (10.6%); £3,729,351.52 -> £3,332,451.91 (10.6%); £3,729,351.67 -> £3,332,452.06 (10.6%); £3,729,351.85 -> £3,332,452.23 (10.6%); £3,729,352.04 -> £3,332,452.41 (10.6%); £3,729,352.25 -> £3,332,452.62 (10.6%); £3,729,352.47 -> £3,332,452.85 (10.6%); £3,729,352.71 -> £3,332,453.11 (10.6%); £3,729,352.97 -> £3,332,453.39 (10.6%); £3,729,353.23 -> £3,332,453.54 (10.6%); £3,729,353.49 -> £3,332,453.69 (10.6%); £3,729,353.75 -> £3,332,453.85 (10.6%); £3,729,354.01 -> £3,332,454.00 (10.6%); £3,729,354.27 -> £3,332,454.16 (10.6%); £3,729,354.52 -> £3,332,454.30 (10.6%); £3,729,354.77 -> £3,332,454.44 (10.6%); £3,729,355.03 -> £3,332,454.58 (10.6%); £3,729,355.29 -> £3,332,454.72 (10.6%); £3,729,355.55 -> £3,332,454.86 (10.6%); £3,729,355.81 -> £3,332,455.00 (10.6%); £3,729,356.07 -> £3,332,455.13 (10.6%); £3,729,356.34 -> £3,332,455.26 (10.6%); £3,729,356.59 -> £3,332,455.53 (10.6%); £3,729,356.79 -> £3,332,455.77 (10.6%); £3,729,356.98 -> £3,332,455.97 (10.6%); £3,729,357.17 -> £3,332,456.16 (10.6%); £3,729,357.43 -> £3,332,456.34 (10.6%); £3,729,357.69 -> £3,332,456.51 (10.6%); £3,729,357.94 -> £3,332,456.68 (10.6%); £3,729,358.20 -> £3,332,456.85 (10.6%); £3,729,358.47 -> £3,332,457.01 (10.6%); £3,729,358.74 -> £3,332,457.16 (10.6%); £3,729,358.99 -> £3,332,457.31 (10.6%); £3,729,359.24 -> £3,332,457.36 (10.6%); £3,729,359.51 -> £3,332,457.41 (10.6%); £3,729,359.75 -> £3,332,457.45 (10.6%); £3,729,359.96 -> £3,332,457.49 (10.6%); £3,729,360.17 -> £3,332,457.53 (10.6%); £3,729,360.32 -> £3,332,457.58 (10.6%); £3,729,360.48 -> £3,332,457.62 (10.6%); £3,729,360.63 -> £3,332,457.66 (10.6%); £3,729,360.78 -> £3,332,457.70 (10.6%); £3,729,360.94 -> £3,332,457.75 (10.6%); £3,729,361.10 -> £3,332,457.79 (10.6%); £3,729,361.26 -> £3,332,457.83 (10.6%); £3,729,361.42 -> £3,332,457.87 (10.6%); £3,729,361.58 -> £3,332,457.92 (10.6%); £3,729,361.74 -> £3,332,457.96 (10.6%); £3,729,361.89 -> £3,332,458.00 (10.6%); £3,729,362.05 -> £3,332,458.12 (10.6%); £3,729,362.20 -> £3,332,458.24 (10.6%); £3,729,362.37 -> £3,332,458.37 (10.6%); £3,729,362.57 -> £3,332,458.52 (10.6%); £3,729,362.78 -> £3,332,458.70 (10.6%); £3,729,363.01 -> £3,332,458.90 (10.6%); £3,729,363.25 -> £3,332,459.14 (10.6%); £3,729,363.51 -> £3,332,459.38 (10.6%); £3,729,363.78 -> £3,332,459.54 (10.6%); £3,729,364.05 -> £3,332,459.69 (10.6%); £3,729,364.31 -> £3,332,459.84 (10.6%); £3,729,364.57 -> £3,332,460.00 (10.6%); £3,729,364.84 -> £3,332,460.15 (10.6%); £3,729,365.09 -> £3,332,460.30 (10.6%); £3,729,365.36 -> £3,332,460.44 (10.6%); £3,729,365.62 -> £3,332,460.58 (10.6%); £3,729,365.88 -> £3,332,460.73 (10.6%); £3,729,366.13 -> £3,332,460.87 (10.6%); £3,729,366.39 -> £3,332,461.00 (10.6%); £3,729,366.65 -> £3,332,461.13 (10.6%); £3,729,366.91 -> £3,332,461.26 (10.6%); £3,729,367.17 -> £3,332,461.51 (10.6%); £3,729,367.43 -> £3,332,461.73 (10.6%); £3,729,367.69 -> £3,332,461.91 (10.6%); £3,729,367.95 -> £3,332,462.07 (10.6%); £3,729,368.21 -> £3,332,462.22 (10.6%); £3,729,368.48 -> £3,332,462.37 (10.6%); £3,729,368.74 -> £3,332,462.51 (10.6%); £3,729,369.00 -> £3,332,462.64 (10.6%); £3,729,369.26 -> £3,332,462.77 (10.6%); £3,729,369.51 -> £3,332,462.90 (10.6%); £3,729,369.76 -> £3,332,463.01 (10.6%); £3,729,370.02 -> £3,332,463.06 (10.6%); £3,729,370.28 -> £3,332,463.11 (10.6%); £3,729,370.51 -> £3,332,463.15 (10.6%); £3,729,370.74 -> £3,332,463.19 (10.6%); £3,729,370.94 -> £3,332,463.23 (10.6%); £3,729,371.10 -> £3,332,463.27 (10.6%); £3,729,371.25 -> £3,332,463.32 (10.6%); £3,729,371.41 -> £3,332,463.36 (10.6%); £3,729,371.57 -> £3,332,463.40 (10.6%); £3,729,371.73 -> £3,332,463.44 (10.6%); £3,729,371.88 -> £3,332,463.48 (10.6%); £3,729,372.04 -> £3,332,463.53 (10.6%); £3,729,372.20 -> £3,332,463.57 (10.6%); £3,729,372.36 -> £3,332,463.61 (10.6%); £3,729,372.52 -> £3,332,463.66 (10.6%); £3,729,372.68 -> £3,332,463.70 (10.6%); £3,729,372.84 -> £3,332,463.87 (10.6%); £3,729,372.99 -> £3,332,464.04 (10.6%); £3,729,373.17 -> £3,332,464.22 (10.6%); £3,729,373.37 -> £3,332,464.43 (10.6%); £3,729,373.58 -> £3,332,464.65 (10.6%); £3,729,373.80 -> £3,332,464.89 (10.6%); £3,729,374.05 -> £3,332,465.17 (10.6%); £3,729,374.32 -> £3,332,465.46 (10.6%); £3,729,374.58 -> £3,332,465.60 (10.6%); £3,729,374.85 -> £3,332,465.76 (10.6%); £3,729,375.10 -> £3,332,465.91 (10.6%); £3,729,375.35 -> £3,332,466.07 (10.6%); £3,729,375.62 -> £3,332,466.22 (10.6%); £3,729,375.88 -> £3,332,466.36 (10.6%); £3,729,376.14 -> £3,332,466.50 (10.6%); £3,729,376.39 -> £3,332,466.63 (10.6%); £3,729,376.66 -> £3,332,466.77 (10.6%); £3,729,376.92 -> £3,332,466.91 (10.6%); £3,729,377.17 -> £3,332,467.04 (10.6%); £3,729,377.44 -> £3,332,467.17 (10.6%); £3,729,377.70 -> £3,332,467.30 (10.6%); £3,729,377.90 -> £3,332,467.59 (10.6%); £3,729,378.17 -> £3,332,467.84 (10.6%); £3,729,378.36 -> £3,332,468.07 (10.6%); £3,729,378.55 -> £3,332,468.26 (10.6%); £3,729,378.75 -> £3,332,468.45 (10.6%); £3,729,378.95 -> £3,332,468.63 (10.6%); £3,729,379.14 -> £3,332,468.81 (10.6%); £3,729,379.40 -> £3,332,468.98 (10.6%); £3,729,379.66 -> £3,332,469.15 (10.6%); £3,729,379.92 -> £3,332,469.32 (10.6%); £3,729,380.18 -> £3,332,469.49 (10.6%); £3,729,380.45 -> £3,332,469.54 (10.6%); £3,729,380.72 -> £3,332,469.58 (10.6%); £3,729,380.96 -> £3,332,469.63 (10.6%); £3,729,381.18 -> £3,332,469.67 (10.6%); £3,729,381.38 -> £3,332,469.71 (10.6%); £3,729,381.52 -> £3,332,469.76 (10.6%); £3,729,381.66 -> £3,332,469.80 (10.6%); £3,729,381.80 -> £3,332,469.84 (10.6%); £3,729,381.93 -> £3,332,469.88 (10.6%); £3,729,382.08 -> £3,332,469.93 (10.6%); £3,729,382.21 -> £3,332,469.97 (10.6%); £3,729,382.35 -> £3,332,470.01 (10.6%); £3,729,382.49 -> £3,332,470.05 (10.6%); £3,729,382.63 -> £3,332,470.09 (10.6%); £3,729,382.76 -> £3,332,470.14 (10.6%); £3,729,382.90 -> £3,332,470.18 (10.6%); £3,729,383.04 -> £3,332,470.32 (10.6%); £3,729,383.18 -> £3,332,470.46 (10.6%); £3,729,383.33 -> £3,332,470.61 (10.6%); £3,729,383.50 -> £3,332,470.76 (10.6%); £3,729,383.68 -> £3,332,470.92 (10.6%); £3,729,383.89 -> £3,332,471.10 (10.6%); £3,729,384.10 -> £3,332,471.31 (10.6%); £3,729,384.32 -> £3,332,471.53 (10.6%); £3,729,384.54 -> £3,332,471.63 (10.6%); £3,729,384.76 -> £3,332,471.74 (10.6%); £3,729,384.99 -> £3,332,471.85 (10.6%); £3,729,385.22 -> £3,332,471.96 (10.6%); £3,729,385.46 -> £3,332,472.06 (10.6%); £3,729,385.68 -> £3,332,472.15 (10.6%); £3,729,385.91 -> £3,332,472.24 (10.6%); £3,729,386.13 -> £3,332,472.33 (10.6%); £3,729,386.35 -> £3,332,472.41 (10.6%); £3,729,386.59 -> £3,332,472.49 (10.6%); £3,729,386.81 -> £3,332,472.57 (10.6%); £3,729,387.04 -> £3,332,472.65 (10.6%); £3,729,387.27 -> £3,332,472.73 (10.6%); £3,729,387.44 -> £3,332,472.92 (10.6%); £3,729,387.61 -> £3,332,473.10 (10.6%); £3,729,387.78 -> £3,332,473.27 (10.6%); £3,729,387.95 -> £3,332,473.42 (10.6%); £3,729,388.13 -> £3,332,473.58 (10.6%); £3,729,388.30 -> £3,332,473.73 (10.6%); £3,729,388.47 -> £3,332,473.89 (10.6%); £3,729,388.70 -> £3,332,474.04 (10.6%); £3,729,388.92 -> £3,332,474.19 (10.6%); £3,729,389.16 -> £3,332,474.34 (10.6%); £3,729,389.38 -> £3,332,474.49 (10.6%); £3,729,389.60 -> £3,332,474.53 (10.6%); £3,729,389.84 -> £3,332,474.58 (10.6%); £3,729,390.05 -> £3,332,474.62 (10.6%); £3,729,390.24 -> £3,332,474.66 (10.6%); £3,729,390.42 -> £3,332,474.70 (10.6%); £3,729,390.56 -> £3,332,474.75 (10.6%); £3,729,390.70 -> £3,332,474.79 (10.6%); £3,729,390.83 -> £3,332,474.83 (10.6%); £3,729,390.97 -> £3,332,474.88 (10.6%); £3,729,391.11 -> £3,332,474.92 (10.6%); £3,729,391.25 -> £3,332,474.96 (10.6%); £3,729,391.39 -> £3,332,475.00 (10.6%); £3,729,391.53 -> £3,332,475.04 (10.6%); £3,729,391.67 -> £3,332,475.08 (10.6%); £3,729,391.80 -> £3,332,475.12 (10.6%); £3,729,391.94 -> £3,332,475.16 (10.6%); £3,729,392.07 -> £3,332,475.30 (10.6%); £3,729,392.21 -> £3,332,475.44 (10.6%); £3,729,392.37 -> £3,332,475.58 (10.6%); £3,729,392.54 -> £3,332,475.71 (10.6%); £3,729,392.72 -> £3,332,475.85 (10.6%); £3,729,392.92 -> £3,332,476.00 (10.6%); £3,729,393.13 -> £3,332,476.14 (10.6%); £3,729,393.36 -> £3,332,476.30 (10.6%); £3,729,393.59 -> £3,332,476.35 (10.6%); £3,729,393.82 -> £3,332,476.41 (10.6%); £3,729,394.05 -> £3,332,476.46 (10.6%); £3,729,394.28 -> £3,332,476.52 (10.6%); £3,729,394.51 -> £3,332,476.58 (10.6%); £3,729,394.74 -> £3,332,476.63 (10.6%); £3,729,394.97 -> £3,332,476.69 (10.6%); £3,729,395.20 -> £3,332,476.74 (10.6%); £3,729,395.43 -> £3,332,476.80 (10.6%); £3,729,395.66 -> £3,332,476.85 (10.6%); £3,729,395.89 -> £3,332,476.90 (10.6%); £3,729,396.12 -> £3,332,476.96 (10.6%); £3,729,396.35 -> £3,332,477.01 (10.6%); £3,729,396.59 -> £3,332,477.17 (10.6%); £3,729,396.82 -> £3,332,477.33 (10.6%); £3,729,397.05 -> £3,332,477.48 (10.6%); £3,729,397.22 -> £3,332,477.63 (10.6%); £3,729,397.44 -> £3,332,477.79 (10.6%); £3,729,397.62 -> £3,332,477.94 (10.6%); £3,729,397.78 -> £3,332,478.09 (10.6%); £3,729,398.02 -> £3,332,478.25 (10.6%); £3,729,398.25 -> £3,332,478.40 (10.6%); £3,729,398.48 -> £3,332,478.55 (10.6%); £3,729,398.70 -> £3,332,478.70 (10.6%); £3,729,398.93 -> £3,332,478.74 (10.6%); £3,729,399.16 -> £3,332,478.79 (10.6%); £3,729,399.36 -> £3,332,478.83 (10.6%); £3,729,399.56 -> £3,332,478.87 (10.6%); £3,729,399.73 -> £3,332,478.91 (10.6%); £3,729,399.89 -> £3,332,478.96 (10.6%); £3,729,400.05 -> £3,332,479.00 (10.6%); £3,729,400.21 -> £3,332,479.04 (10.6%); £3,729,400.38 -> £3,332,479.09 (10.6%); £3,729,400.54 -> £3,332,479.13 (10.6%); £3,729,400.70 -> £3,332,479.17 (10.6%); £3,729,400.85 -> £3,332,479.22 (10.6%); £3,729,401.01 -> £3,332,479.26 (10.6%); £3,729,401.17 -> £3,332,479.30 (10.6%); £3,729,401.32 -> £3,332,479.35 (10.6%); £3,729,401.49 -> £3,332,479.39 (10.6%); £3,729,401.65 -> £3,332,479.58 (10.6%); £3,729,401.81 -> £3,332,479.78 (10.6%); £3,729,401.98 -> £3,332,479.99 (10.6%); £3,729,402.18 -> £3,332,480.21 (10.6%); £3,729,402.39 -> £3,332,480.45 (10.6%); £3,729,402.62 -> £3,332,480.72 (10.6%); £3,729,402.86 -> £3,332,481.02 (10.6%); £3,729,403.12 -> £3,332,481.34 (10.6%); £3,729,403.38 -> £3,332,481.49 (10.6%); £3,729,403.64 -> £3,332,481.64 (10.6%); £3,729,403.90 -> £3,332,481.79 (10.6%); £3,729,404.17 -> £3,332,481.95 (10.6%); £3,729,404.44 -> £3,332,482.10 (10.6%); £3,729,404.70 -> £3,332,482.25 (10.6%); £3,729,404.97 -> £3,332,482.39 (10.6%); £3,729,405.23 -> £3,332,482.53 (10.6%); £3,729,405.51 -> £3,332,482.67 (10.6%); £3,729,405.77 -> £3,332,482.81 (10.6%); £3,729,406.04 -> £3,332,482.95 (10.6%); £3,729,406.29 -> £3,332,483.09 (10.6%); £3,729,406.56 -> £3,332,483.22 (10.6%); £3,729,406.81 -> £3,332,483.52 (10.6%); £3,729,407.01 -> £3,332,483.81 (10.6%); £3,729,407.21 -> £3,332,484.05 (10.6%); £3,729,407.40 -> £3,332,484.28 (10.6%); £3,729,407.66 -> £3,332,484.50 (10.6%); £3,729,407.92 -> £3,332,484.71 (10.6%); £3,729,408.19 -> £3,332,484.92 (10.6%); £3,729,408.46 -> £3,332,485.12 (10.6%); £3,729,408.71 -> £3,332,485.32 (10.6%); £3,729,408.99 -> £3,332,485.52 (10.6%); £3,729,409.25 -> £3,332,485.70 (10.6%); £3,729,409.51 -> £3,332,485.75 (10.6%); £3,729,409.78 -> £3,332,485.80 (10.6%); £3,729,410.03 -> £3,332,485.84 (10.6%); £3,729,410.25 -> £3,332,485.89 (10.6%); £3,729,410.46 -> £3,332,485.93 (10.6%); £3,729,410.61 -> £3,332,485.97 (10.6%); £3,729,410.77 -> £3,332,486.01 (10.6%); £3,729,410.93 -> £3,332,486.05 (10.6%); £3,729,411.09 -> £3,332,486.10 (10.6%); £3,729,411.25 -> £3,332,486.14 (10.6%); £3,729,411.41 -> £3,332,486.18 (10.6%); £3,729,411.57 -> £3,332,486.22 (10.6%); £3,729,411.73 -> £3,332,486.27 (10.6%); £3,729,411.88 -> £3,332,486.31 (10.6%); £3,729,412.04 -> £3,332,486.35 (10.6%); £3,729,412.20 -> £3,332,486.40 (10.6%); £3,729,412.36 -> £3,332,486.57 (10.6%); £3,729,412.51 -> £3,332,486.76 (10.6%); £3,729,412.69 -> £3,332,486.96 (10.6%); £3,729,412.88 -> £3,332,487.17 (10.6%); £3,729,413.09 -> £3,332,487.41 (10.6%); £3,729,413.33 -> £3,332,487.67 (10.6%); £3,729,413.58 -> £3,332,487.96 (10.6%); £3,729,413.84 -> £3,332,488.27 (10.6%); £3,729,414.10 -> £3,332,488.42 (10.6%); £3,729,414.37 -> £3,332,488.58 (10.6%); £3,729,414.64 -> £3,332,488.73 (10.6%); £3,729,414.90 -> £3,332,488.89 (10.6%); £3,729,415.16 -> £3,332,489.04 (10.6%); £3,729,415.43 -> £3,332,489.19 (10.6%); £3,729,415.69 -> £3,332,489.34 (10.6%); £3,729,415.95 -> £3,332,489.49 (10.6%); £3,729,416.21 -> £3,332,489.63 (10.6%); £3,729,416.48 -> £3,332,489.78 (10.6%); £3,729,416.75 -> £3,332,489.92 (10.6%); £3,729,417.01 -> £3,332,490.05 (10.6%); £3,729,417.28 -> £3,332,490.19 (10.6%); £3,729,417.55 -> £3,332,490.49 (10.6%); £3,729,417.80 -> £3,332,490.78 (10.6%); £3,729,418.07 -> £3,332,491.02 (10.6%); £3,729,418.34 -> £3,332,491.24 (10.6%); £3,729,418.59 -> £3,332,491.45 (10.6%); £3,729,418.87 -> £3,332,491.65 (10.6%); £3,729,419.06 -> £3,332,491.85 (10.6%); £3,729,419.32 -> £3,332,492.04 (10.6%); £3,729,419.57 -> £3,332,492.23 (10.6%); £3,729,419.84 -> £3,332,492.41 (10.6%); £3,729,420.11 -> £3,332,492.59 (10.6%); £3,729,420.38 -> £3,332,492.64 (10.6%); £3,729,420.64 -> £3,332,492.69 (10.6%); £3,729,420.88 -> £3,332,492.73 (10.6%); £3,729,421.11 -> £3,332,492.78 (10.6%); £3,729,421.31 -> £3,332,492.82 (10.6%); £3,729,421.48 -> £3,332,492.86 (10.6%); £3,729,421.63 -> £3,332,492.90 (10.6%); £3,729,421.80 -> £3,332,492.95 (10.6%); £3,729,421.96 -> £3,332,492.99 (10.6%); £3,729,422.12 -> £3,332,493.03 (10.6%); £3,729,422.28 -> £3,332,493.07 (10.6%); £3,729,422.44 -> £3,332,493.12 (10.6%); £3,729,422.60 -> £3,332,493.16 (10.6%); £3,729,422.76 -> £3,332,493.20 (10.6%); £3,729,422.92 -> £3,332,493.25 (10.6%); £3,729,423.08 -> £3,332,493.29 (10.6%); £3,729,423.25 -> £3,332,493.47 (10.6%); £3,729,423.41 -> £3,332,493.65 (10.6%); £3,729,423.59 -> £3,332,493.83 (10.6%); £3,729,423.78 -> £3,332,494.04 (10.6%); £3,729,423.99 -> £3,332,494.27 (10.6%); £3,729,424.22 -> £3,332,494.52 (10.6%); £3,729,424.47 -> £3,332,494.81 (10.6%); £3,729,424.74 -> £3,332,495.10 (10.6%); £3,729,425.01 -> £3,332,495.26 (10.6%); £3,729,425.27 -> £3,332,495.41 (10.6%); £3,729,425.54 -> £3,332,495.56 (10.6%); £3,729,425.81 -> £3,332,495.71 (10.6%); £3,729,426.07 -> £3,332,495.86 (10.6%); £3,729,426.33 -> £3,332,496.01 (10.6%); £3,729,426.60 -> £3,332,496.15 (10.6%); £3,729,426.87 -> £3,332,496.29 (10.6%); £3,729,427.14 -> £3,332,496.43 (10.6%); £3,729,427.41 -> £3,332,496.57 (10.6%); £3,729,427.67 -> £3,332,496.71 (10.6%); £3,729,427.95 -> £3,332,496.84 (10.6%); £3,729,428.21 -> £3,332,496.97 (10.6%); £3,729,428.48 -> £3,332,497.26 (10.6%); £3,729,428.74 -> £3,332,497.53 (10.6%); £3,729,429.01 -> £3,332,497.76 (10.6%); £3,729,429.27 -> £3,332,497.97 (10.6%); £3,729,429.47 -> £3,332,498.16 (10.6%); £3,729,429.67 -> £3,332,498.36 (10.6%); £3,729,429.94 -> £3,332,498.55 (10.6%); £3,729,430.20 -> £3,332,498.74 (10.6%); £3,729,430.46 -> £3,332,498.91 (10.6%); £3,729,430.74 -> £3,332,499.09 (10.6%); £3,729,431.01 -> £3,332,499.27 (10.6%); £3,729,431.27 -> £3,332,499.32 (10.6%); £3,729,431.54 -> £3,332,499.37 (10.6%); £3,729,431.79 -> £3,332,499.41 (10.6%); £3,729,432.01 -> £3,332,499.46 (10.6%); £3,729,432.22 -> £3,332,499.50 (10.6%); £3,729,432.37 -> £3,332,499.54 (10.6%); £3,729,432.53 -> £3,332,499.58 (10.6%); £3,729,432.69 -> £3,332,499.63 (10.6%); £3,729,432.85 -> £3,332,499.67 (10.6%); £3,729,433.01 -> £3,332,499.71 (10.6%); £3,729,433.18 -> £3,332,499.75 (10.6%); £3,729,433.34 -> £3,332,499.79 (10.6%); £3,729,433.50 -> £3,332,499.84 (10.6%); £3,729,433.66 -> £3,332,499.88 (10.6%); £3,729,433.82 -> £3,332,499.92 (10.6%); £3,729,433.98 -> £3,332,499.97 (10.6%); £3,729,434.14 -> £3,332,500.19 (10.6%); £3,729,434.30 -> £3,332,500.41 (10.6%); £3,729,434.48 -> £3,332,500.65 (10.6%); £3,729,434.68 -> £3,332,500.89 (10.6%); £3,729,434.89 -> £3,332,501.17 (10.6%); £3,729,435.13 -> £3,332,501.47 (10.6%); £3,729,435.38 -> £3,332,501.79 (10.6%); £3,729,435.65 -> £3,332,502.13 (10.6%); £3,729,435.91 -> £3,332,502.28 (10.6%); £3,729,436.18 -> £3,332,502.43 (10.6%); £3,729,436.45 -> £3,332,502.58 (10.6%); £3,729,436.71 -> £3,332,502.72 (10.6%); £3,729,436.97 -> £3,332,502.87 (10.6%); £3,729,437.24 -> £3,332,503.01 (10.6%); £3,729,437.52 -> £3,332,503.15 (10.6%); £3,729,437.80 -> £3,332,503.28 (10.6%); £3,729,438.06 -> £3,332,503.42 (10.6%); £3,729,438.32 -> £3,332,503.55 (10.6%); £3,729,438.58 -> £3,332,503.69 (10.6%); £3,729,438.85 -> £3,332,503.82 (10.6%); £3,729,439.12 -> £3,332,503.95 (10.6%); £3,729,439.39 -> £3,332,504.29 (10.6%); £3,729,439.67 -> £3,332,504.62 (10.6%); £3,729,439.94 -> £3,332,504.90 (10.6%); £3,729,440.20 -> £3,332,505.15 (10.6%); £3,729,440.40 -> £3,332,505.40 (10.6%); £3,729,440.67 -> £3,332,505.64 (10.6%); £3,729,440.95 -> £3,332,505.88 (10.6%); £3,729,441.21 -> £3,332,506.11 (10.6%); £3,729,441.49 -> £3,332,506.34 (10.6%); £3,729,441.76 -> £3,332,506.56 (10.6%); £3,729,442.03 -> £3,332,506.77 (10.6%); £3,729,442.29 -> £3,332,506.81 (10.6%); £3,729,442.56 -> £3,332,506.86 (10.6%); £3,729,442.80 -> £3,332,506.91 (10.6%); £3,729,443.03 -> £3,332,506.95 (10.6%); £3,729,443.23 -> £3,332,506.99 (10.6%); £3,729,443.40 -> £3,332,507.03 (10.6%); £3,729,443.56 -> £3,332,507.07 (10.6%); £3,729,443.72 -> £3,332,507.12 (10.6%); £3,729,443.88 -> £3,332,507.16 (10.6%); £3,729,444.03 -> £3,332,507.20 (10.6%); £3,729,444.20 -> £3,332,507.24 (10.6%); £3,729,444.36 -> £3,332,507.29 (10.6%); £3,729,444.52 -> £3,332,507.33 (10.6%); £3,729,444.68 -> £3,332,507.37 (10.6%); £3,729,444.84 -> £3,332,507.42 (10.6%); £3,729,445.00 -> £3,332,507.46 (10.6%); £3,729,445.16 -> £3,332,507.73 (10.6%); £3,729,445.32 -> £3,332,508.01 (10.6%); £3,729,445.49 -> £3,332,508.31 (10.6%); £3,729,445.69 -> £3,332,508.62 (10.6%); £3,729,445.91 -> £3,332,508.95 (10.6%); £3,729,446.13 -> £3,332,509.31 (10.6%); £3,729,446.39 -> £3,332,509.71 (10.6%); £3,729,446.66 -> £3,332,510.11 (10.6%); £3,729,446.92 -> £3,332,510.26 (10.6%); £3,729,447.18 -> £3,332,510.41 (10.6%); £3,729,447.43 -> £3,332,510.57 (10.6%); £3,729,447.69 -> £3,332,510.72 (10.6%); £3,729,447.96 -> £3,332,510.87 (10.6%); £3,729,448.22 -> £3,332,511.02 (10.6%); £3,729,448.48 -> £3,332,511.15 (10.6%); £3,729,448.76 -> £3,332,511.29 (10.6%); £3,729,449.03 -> £3,332,511.43 (10.6%); £3,729,449.29 -> £3,332,511.57 (10.6%); £3,729,449.56 -> £3,332,511.71 (10.6%); £3,729,449.82 -> £3,332,511.85 (10.6%); £3,729,450.08 -> £3,332,511.98 (10.6%); £3,729,450.35 -> £3,332,512.37 (10.6%); £3,729,450.60 -> £3,332,512.72 (10.6%); £3,729,450.81 -> £3,332,513.04 (10.6%); £3,729,451.01 -> £3,332,513.34 (10.6%); £3,729,451.20 -> £3,332,513.63 (10.6%); £3,729,451.41 -> £3,332,513.91 (10.6%); £3,729,451.61 -> £3,332,514.18 (10.6%); £3,729,451.87 -> £3,332,514.45 (10.6%); £3,729,452.14 -> £3,332,514.72 (10.6%); £3,729,452.41 -> £3,332,514.99 (10.6%); £3,729,452.67 -> £3,332,515.24 (10.6%); £3,729,452.94 -> £3,332,515.29 (10.6%); £3,729,453.20 -> £3,332,515.34 (10.6%); £3,729,453.45 -> £3,332,515.38 (10.6%); £3,729,453.66 -> £3,332,515.43 (10.6%); £3,729,453.87 -> £3,332,515.47 (10.6%); £3,729,454.01 -> £3,332,515.51 (10.6%); £3,729,454.15 -> £3,332,515.55 (10.6%); £3,729,454.29 -> £3,332,515.59 (10.6%); £3,729,454.43 -> £3,332,515.63 (10.6%); £3,729,454.57 -> £3,332,515.68 (10.6%); £3,729,454.71 -> £3,332,515.72 (10.6%); £3,729,454.85 -> £3,332,515.76 (10.6%); £3,729,454.99 -> £3,332,515.80 (10.6%); £3,729,455.13 -> £3,332,515.84 (10.6%); £3,729,455.27 -> £3,332,515.88 (10.6%); £3,729,455.41 -> £3,332,515.93 (10.6%); £3,729,455.56 -> £3,332,516.21 (10.6%); £3,729,455.70 -> £3,332,516.49 (10.6%); £3,729,455.85 -> £3,332,516.79 (10.6%); £3,729,456.02 -> £3,332,517.08 (10.6%); £3,729,456.21 -> £3,332,517.38 (10.6%); £3,729,456.42 -> £3,332,517.69 (10.6%); £3,729,456.64 -> £3,332,518.04 (10.6%); £3,729,456.88 -> £3,332,518.39 (10.6%); £3,729,457.11 -> £3,332,518.50 (10.6%); £3,729,457.35 -> £3,332,518.60 (10.6%); £3,729,457.58 -> £3,332,518.71 (10.6%); £3,729,457.81 -> £3,332,518.82 (10.6%); £3,729,458.05 -> £3,332,518.92 (10.6%); £3,729,458.28 -> £3,332,519.01 (10.6%); £3,729,458.51 -> £3,332,519.10 (10.6%); £3,729,458.74 -> £3,332,519.19 (10.6%); £3,729,458.98 -> £3,332,519.27 (10.6%); £3,729,459.21 -> £3,332,519.36 (10.6%); £3,729,459.46 -> £3,332,519.44 (10.6%); £3,729,459.70 -> £3,332,519.52 (10.6%); £3,729,459.94 -> £3,332,519.59 (10.6%); £3,729,460.11 -> £3,332,519.91 (10.6%); £3,729,460.28 -> £3,332,520.21 (10.6%); £3,729,460.46 -> £3,332,520.50 (10.6%); £3,729,460.64 -> £3,332,520.78 (10.6%); £3,729,460.81 -> £3,332,521.06 (10.6%); £3,729,460.99 -> £3,332,521.34 (10.6%); £3,729,461.17 -> £3,332,521.61 (10.6%); £3,729,461.41 -> £3,332,521.88 (10.6%); £3,729,461.65 -> £3,332,522.16 (10.6%); £3,729,461.88 -> £3,332,522.43 (10.6%); £3,729,462.11 -> £3,332,522.70 (10.6%); £3,729,462.35 -> £3,332,522.74 (10.6%); £3,729,462.58 -> £3,332,522.79 (10.6%); £3,729,462.80 -> £3,332,522.83 (10.6%); £3,729,463.00 -> £3,332,522.88 (10.6%); £3,729,463.18 -> £3,332,522.92 (10.6%); £3,729,463.33 -> £3,332,522.96 (10.6%); £3,729,463.47 -> £3,332,523.00 (10.6%); £3,729,463.61 -> £3,332,523.05 (10.6%); £3,729,463.75 -> £3,332,523.09 (10.6%); £3,729,463.89 -> £3,332,523.13 (10.6%); £3,729,464.03 -> £3,332,523.17 (10.6%); £3,729,464.16 -> £3,332,523.21 (10.6%); £3,729,464.30 -> £3,332,523.25 (10.6%); £3,729,464.45 -> £3,332,523.29 (10.6%); £3,729,464.58 -> £3,332,523.33 (10.6%); £3,729,464.72 -> £3,332,523.37 (10.6%); £3,729,464.86 -> £3,332,523.62 (10.6%); £3,729,465.01 -> £3,332,523.88 (10.6%); £3,729,465.16 -> £3,332,524.14 (10.6%); £3,729,465.33 -> £3,332,524.40 (10.6%); £3,729,465.52 -> £3,332,524.66 (10.6%); £3,729,465.72 -> £3,332,524.93 (10.6%); £3,729,465.94 -> £3,332,525.20 (10.6%); £3,729,466.17 -> £3,332,525.47 (10.6%); £3,729,466.41 -> £3,332,525.53 (10.6%); £3,729,466.65 -> £3,332,525.58 (10.6%); £3,729,466.89 -> £3,332,525.64 (10.6%); £3,729,467.12 -> £3,332,525.70 (10.6%); £3,729,467.35 -> £3,332,525.75 (10.6%); £3,729,467.58 -> £3,332,525.81 (10.6%); £3,729,467.82 -> £3,332,525.86 (10.6%); £3,729,468.06 -> £3,332,525.91 (10.6%); £3,729,468.29 -> £3,332,525.97 (10.6%); £3,729,468.52 -> £3,332,526.02 (10.6%); £3,729,468.75 -> £3,332,526.07 (10.6%); £3,729,468.99 -> £3,332,526.12 (10.6%); £3,729,469.22 -> £3,332,526.17 (10.6%); £3,729,469.40 -> £3,332,526.43 (10.6%); £3,729,469.57 -> £3,332,526.69 (10.6%); £3,729,469.76 -> £3,332,526.94 (10.6%); £3,729,469.93 -> £3,332,527.20 (10.6%); £3,729,470.16 -> £3,332,527.47 (10.6%); £3,729,470.40 -> £3,332,527.73 (10.6%); £3,729,470.57 -> £3,332,527.99 (10.6%); £3,729,470.81 -> £3,332,528.25 (10.6%); £3,729,471.04 -> £3,332,528.51 (10.6%); £3,729,471.27 -> £3,332,528.77 (10.6%); £3,729,471.50 -> £3,332,529.03 (10.6%); £3,729,471.74 -> £3,332,529.07 (10.6%); £3,729,471.97 -> £3,332,529.12 (10.6%); £3,729,472.19 -> £3,332,529.16 (10.6%); £3,729,472.39 -> £3,332,529.20 (10.6%); £3,729,472.56 -> £3,332,529.24 (10.6%); £3,729,472.72 -> £3,332,529.28 (10.6%); £3,729,472.88 -> £3,332,529.33 (10.6%); £3,729,473.04 -> £3,332,529.37 (10.6%); £3,729,473.20 -> £3,332,529.41 (10.6%); £3,729,473.36 -> £3,332,529.45 (10.6%); £3,729,473.52 -> £3,332,529.49 (10.6%); £3,729,473.68 -> £3,332,529.54 (10.6%); £3,729,473.84 -> £3,332,529.58 (10.6%); £3,729,474.00 -> £3,332,529.62 (10.6%); £3,729,474.16 -> £3,332,529.67 (10.6%); £3,729,474.32 -> £3,332,529.71 (10.6%); £3,729,474.48 -> £3,332,529.96 (10.6%); £3,729,474.64 -> £3,332,530.21 (10.6%); £3,729,474.81 -> £3,332,530.47 (10.6%); £3,729,475.01 -> £3,332,530.75 (10.6%); £3,729,475.23 -> £3,332,531.06 (10.6%); £3,729,475.46 -> £3,332,531.39 (10.6%); £3,729,475.70 -> £3,332,531.74 (10.6%); £3,729,475.96 -> £3,332,532.11 (10.6%); £3,729,476.22 -> £3,332,532.26 (10.6%); £3,729,476.49 -> £3,332,532.41 (10.6%); £3,729,476.76 -> £3,332,532.56 (10.6%); £3,729,477.02 -> £3,332,532.71 (10.6%); £3,729,477.29 -> £3,332,532.87 (10.6%); £3,729,477.54 -> £3,332,533.02 (10.6%); £3,729,477.80 -> £3,332,533.16 (10.6%); £3,729,478.08 -> £3,332,533.30 (10.6%); £3,729,478.34 -> £3,332,533.44 (10.6%); £3,729,478.60 -> £3,332,533.58 (10.6%); £3,729,478.87 -> £3,332,533.72 (10.6%); £3,729,479.13 -> £3,332,533.85 (10.6%); £3,729,479.39 -> £3,332,533.99 (10.6%); £3,729,479.66 -> £3,332,534.35 (10.6%); £3,729,479.93 -> £3,332,534.70 (10.6%); £3,729,480.19 -> £3,332,535.00 (10.6%); £3,729,480.45 -> £3,332,535.28 (10.6%); £3,729,480.71 -> £3,332,535.54 (10.6%); £3,729,480.97 -> £3,332,535.80 (10.6%); £3,729,481.17 -> £3,332,536.06 (10.6%); £3,729,481.43 -> £3,332,536.32 (10.6%); £3,729,481.69 -> £3,332,536.57 (10.6%); £3,729,481.95 -> £3,332,536.81 (10.6%); £3,729,482.20 -> £3,332,537.05 (10.6%); £3,729,482.46 -> £3,332,537.10 (10.6%); £3,729,482.72 -> £3,332,537.15 (10.6%); £3,729,482.98 -> £3,332,537.19 (10.6%); £3,729,483.20 -> £3,332,537.24 (10.6%); £3,729,483.41 -> £3,332,537.28 (10.6%); £3,729,483.56 -> £3,332,537.32 (10.6%); £3,729,483.72 -> £3,332,537.36 (10.6%); £3,729,483.88 -> £3,332,537.40 (10.6%); £3,729,484.03 -> £3,332,537.45 (10.6%); £3,729,484.19 -> £3,332,537.49 (10.6%); £3,729,484.35 -> £3,332,537.53 (10.6%); £3,729,484.50 -> £3,332,537.57 (10.6%); £3,729,484.66 -> £3,332,537.62 (10.6%); £3,729,484.82 -> £3,332,537.66 (10.6%); £3,729,484.97 -> £3,332,537.70 (10.6%); £3,729,485.12 -> £3,332,537.75 (10.6%); £3,729,485.28 -> £3,332,538.02 (10.6%); £3,729,485.44 -> £3,332,538.31 (10.6%); £3,729,485.62 -> £3,332,538.61 (10.6%); £3,729,485.81 -> £3,332,538.91 (10.6%); £3,729,486.02 -> £3,332,539.25 (10.6%); £3,729,486.25 -> £3,332,539.61 (10.6%); £3,729,486.50 -> £3,332,540.00 (10.6%); £3,729,486.76 -> £3,332,540.40 (10.6%); £3,729,487.01 -> £3,332,540.55 (10.6%); £3,729,487.27 -> £3,332,540.71 (10.6%); £3,729,487.53 -> £3,332,540.86 (10.6%); £3,729,487.78 -> £3,332,541.02 (10.6%); £3,729,488.04 -> £3,332,541.17 (10.6%); £3,729,488.30 -> £3,332,541.32 (10.6%); £3,729,488.57 -> £3,332,541.46 (10.6%); £3,729,488.83 -> £3,332,541.60 (10.6%); £3,729,489.08 -> £3,332,541.75 (10.6%); £3,729,489.35 -> £3,332,541.89 (10.6%); £3,729,489.61 -> £3,332,542.02 (10.6%); £3,729,489.86 -> £3,332,542.16 (10.6%); £3,729,490.13 -> £3,332,542.29 (10.6%); £3,729,490.40 -> £3,332,542.68 (10.6%); £3,729,490.66 -> £3,332,543.03 (10.6%); £3,729,490.85 -> £3,332,543.35 (10.6%); £3,729,491.05 -> £3,332,543.65 (10.6%); £3,729,491.25 -> £3,332,543.93 (10.6%); £3,729,491.45 -> £3,332,544.22 (10.6%); £3,729,491.71 -> £3,332,544.50 (10.6%); £3,729,491.96 -> £3,332,544.78 (10.6%); £3,729,492.23 -> £3,332,545.06 (10.6%); £3,729,492.50 -> £3,332,545.33 (10.6%); £3,729,492.76 -> £3,332,545.60 (10.6%); £3,729,493.02 -> £3,332,545.64 (10.6%); £3,729,493.28 -> £3,332,545.69 (10.6%); £3,729,493.52 -> £3,332,545.74 (10.6%); £3,729,493.75 -> £3,332,545.78 (10.6%); £3,729,493.95 -> £3,332,545.82 (10.6%); £3,729,494.11 -> £3,332,545.86 (10.6%); £3,729,494.27 -> £3,332,545.90 (10.6%); £3,729,494.42 -> £3,332,545.95 (10.6%); £3,729,494.58 -> £3,332,545.99 (10.6%); £3,729,494.74 -> £3,332,546.03 (10.6%); £3,729,494.89 -> £3,332,546.07 (10.6%); £3,729,495.05 -> £3,332,546.11 (10.6%); £3,729,495.21 -> £3,332,546.16 (10.6%); £3,729,495.37 -> £3,332,546.20 (10.6%); £3,729,495.52 -> £3,332,546.24 (10.6%); £3,729,495.68 -> £3,332,546.29 (10.6%); £3,729,495.84 -> £3,332,546.51 (10.6%); £3,729,495.99 -> £3,332,546.73 (10.6%); £3,729,496.18 -> £3,332,546.97 (10.6%); £3,729,496.37 -> £3,332,547.22 (10.6%); £3,729,496.57 -> £3,332,547.50 (10.6%); £3,729,496.80 -> £3,332,547.81 (10.6%); £3,729,497.04 -> £3,332,548.15 (10.6%); £3,729,497.29 -> £3,332,548.50 (10.6%); £3,729,497.55 -> £3,332,548.65 (10.6%); £3,729,497.81 -> £3,332,548.80 (10.6%); £3,729,498.06 -> £3,332,548.96 (10.6%); £3,729,498.33 -> £3,332,549.12 (10.6%); £3,729,498.60 -> £3,332,549.27 (10.6%); £3,729,498.86 -> £3,332,549.42 (10.6%); £3,729,499.12 -> £3,332,549.56 (10.6%); £3,729,499.39 -> £3,332,549.70 (10.6%); £3,729,499.65 -> £3,332,549.84 (10.6%); £3,729,499.91 -> £3,332,549.98 (10.6%); £3,729,500.17 -> £3,332,550.11 (10.6%); £3,729,500.44 -> £3,332,550.25 (10.6%); £3,729,500.70 -> £3,332,550.38 (10.6%); £3,729,500.89 -> £3,332,550.72 (10.6%); £3,729,501.15 -> £3,332,551.04 (10.6%); £3,729,501.35 -> £3,332,551.32 (10.6%); £3,729,501.55 -> £3,332,551.57 (10.6%); £3,729,501.82 -> £3,332,551.82 (10.6%); £3,729,502.08 -> £3,332,552.05 (10.6%); £3,729,502.28 -> £3,332,552.29 (10.6%); £3,729,502.54 -> £3,332,552.52 (10.6%); £3,729,502.79 -> £3,332,552.75 (10.6%); £3,729,503.06 -> £3,332,552.97 (10.6%); £3,729,503.33 -> £3,332,553.18 (10.6%); £3,729,503.60 -> £3,332,553.23 (10.6%); £3,729,503.86 -> £3,332,553.28 (10.6%); £3,729,504.10 -> £3,332,553.32 (10.6%); £3,729,504.33 -> £3,332,553.36 (10.6%); £3,729,504.53 -> £3,332,553.40 (10.6%); £3,729,504.69 -> £3,332,553.45 (10.6%); £3,729,504.84 -> £3,332,553.49 (10.6%); £3,729,505.00 -> £3,332,553.53 (10.6%); £3,729,505.15 -> £3,332,553.57 (10.6%); £3,729,505.31 -> £3,332,553.61 (10.6%); £3,729,505.46 -> £3,332,553.66 (10.6%); £3,729,505.62 -> £3,332,553.70 (10.6%); £3,729,505.77 -> £3,332,553.74 (10.6%); £3,729,505.93 -> £3,332,553.78 (10.6%); £3,729,506.08 -> £3,332,553.83 (10.6%); £3,729,506.24 -> £3,332,553.87 (10.6%); £3,729,506.39 -> £3,332,554.08 (10.6%); £3,729,506.54 -> £3,332,554.29 (10.6%); £3,729,506.72 -> £3,332,554.51 (10.6%); £3,729,506.90 -> £3,332,554.73 (10.6%); £3,729,507.11 -> £3,332,554.99 (10.6%); £3,729,507.34 -> £3,332,555.27 (10.6%); £3,729,507.58 -> £3,332,555.58 (10.6%); £3,729,507.83 -> £3,332,555.90 (10.6%); £3,729,508.10 -> £3,332,556.04 (10.6%); £3,729,508.36 -> £3,332,556.19 (10.6%); £3,729,508.62 -> £3,332,556.34 (10.6%); £3,729,508.87 -> £3,332,556.50 (10.6%); £3,729,509.13 -> £3,332,556.65 (10.6%); £3,729,509.38 -> £3,332,556.79 (10.6%); £3,729,509.63 -> £3,332,556.93 (10.6%); £3,729,509.89 -> £3,332,557.07 (10.6%); £3,729,510.16 -> £3,332,557.21 (10.6%); £3,729,510.41 -> £3,332,557.35 (10.6%); £3,729,510.66 -> £3,332,557.49 (10.6%); £3,729,510.91 -> £3,332,557.62 (10.6%); £3,729,511.17 -> £3,332,557.75 (10.6%); £3,729,511.42 -> £3,332,558.07 (10.6%); £3,729,511.68 -> £3,332,558.37 (10.6%); £3,729,511.94 -> £3,332,558.62 (10.6%); £3,729,512.13 -> £3,332,558.85 (10.6%); £3,729,512.33 -> £3,332,559.07 (10.6%); £3,729,512.59 -> £3,332,559.28 (10.6%); £3,729,512.78 -> £3,332,559.49 (10.6%); £3,729,513.04 -> £3,332,559.69 (10.6%); £3,729,513.29 -> £3,332,559.89 (10.6%); £3,729,513.55 -> £3,332,560.08 (10.6%); £3,729,513.81 -> £3,332,560.27 (10.6%); £3,729,514.07 -> £3,332,560.32 (10.6%); £3,729,514.33 -> £3,332,560.37 (10.6%); £3,729,514.57 -> £3,332,560.41 (10.6%); £3,729,514.80 -> £3,332,560.45 (10.6%); £3,729,514.99 -> £3,332,560.49 (10.6%); £3,729,515.15 -> £3,332,560.54 (10.6%); £3,729,515.30 -> £3,332,560.58 (10.6%); £3,729,515.46 -> £3,332,560.62 (10.6%); £3,729,515.62 -> £3,332,560.66 (10.6%); £3,729,515.78 -> £3,332,560.71 (10.6%); £3,729,515.94 -> £3,332,560.75 (10.6%); £3,729,516.09 -> £3,332,560.79 (10.6%); £3,729,516.24 -> £3,332,560.83 (10.6%); £3,729,516.40 -> £3,332,560.88 (10.6%); £3,729,516.56 -> £3,332,560.92 (10.6%); £3,729,516.71 -> £3,332,560.97 (10.6%); £3,729,516.86 -> £3,332,561.23 (10.6%); £3,729,517.02 -> £3,332,561.51 (10.6%); £3,729,517.19 -> £3,332,561.80 (10.6%); £3,729,517.38 -> £3,332,562.10 (10.6%); £3,729,517.58 -> £3,332,562.43 (10.6%); £3,729,517.80 -> £3,332,562.79 (10.6%); £3,729,518.03 -> £3,332,563.18 (10.6%); £3,729,518.29 -> £3,332,563.58 (10.6%); £3,729,518.55 -> £3,332,563.72 (10.6%); £3,729,518.82 -> £3,332,563.87 (10.6%); £3,729,519.08 -> £3,332,564.02 (10.6%); £3,729,519.34 -> £3,332,564.18 (10.6%); £3,729,519.60 -> £3,332,564.33 (10.6%); £3,729,519.87 -> £3,332,564.47 (10.6%); £3,729,520.12 -> £3,332,564.61 (10.6%); £3,729,520.38 -> £3,332,564.74 (10.6%); £3,729,520.65 -> £3,332,564.88 (10.6%); £3,729,520.91 -> £3,332,565.02 (10.6%); £3,729,521.17 -> £3,332,565.16 (10.6%); £3,729,521.43 -> £3,332,565.29 (10.6%); £3,729,521.69 -> £3,332,565.42 (10.6%); £3,729,521.94 -> £3,332,565.80 (10.6%); £3,729,522.20 -> £3,332,566.16 (10.6%); £3,729,522.47 -> £3,332,566.48 (10.6%); £3,729,522.73 -> £3,332,566.78 (10.6%); £3,729,523.00 -> £3,332,567.06 (10.6%); £3,729,523.26 -> £3,332,567.35 (10.6%); £3,729,523.53 -> £3,332,567.64 (10.6%); £3,729,523.79 -> £3,332,567.91 (10.6%); £3,729,524.05 -> £3,332,568.19 (10.6%); £3,729,524.31 -> £3,332,568.47 (10.6%); £3,729,524.58 -> £3,332,568.73 (10.6%); £3,729,524.84 -> £3,332,568.77 (10.6%); £3,729,525.10 -> £3,332,568.82 (10.6%); £3,729,525.34 -> £3,332,568.86 (10.6%); £3,729,525.56 -> £3,332,568.90 (10.6%); £3,729,525.76 -> £3,332,568.94 (10.6%); £3,729,525.90 -> £3,332,568.98 (10.6%); £3,729,526.04 -> £3,332,569.03 (10.6%); £3,729,526.17 -> £3,332,569.07 (10.6%); £3,729,526.30 -> £3,332,569.11 (10.6%); £3,729,526.44 -> £3,332,569.15 (10.6%); £3,729,526.58 -> £3,332,569.19 (10.6%); £3,729,526.71 -> £3,332,569.24 (10.6%); £3,729,526.84 -> £3,332,569.28 (10.6%); £3,729,526.98 -> £3,332,569.32 (10.6%); £3,729,527.12 -> £3,332,569.36 (10.6%); £3,729,527.26 -> £3,332,569.41 (10.6%); £3,729,527.40 -> £3,332,569.68 (10.6%); £3,729,527.53 -> £3,332,569.96 (10.6%); £3,729,527.69 -> £3,332,570.25 (10.6%); £3,729,527.86 -> £3,332,570.54 (10.6%); £3,729,528.04 -> £3,332,570.84 (10.6%); £3,729,528.23 -> £3,332,571.15 (10.6%); £3,729,528.45 -> £3,332,571.48 (10.6%); £3,729,528.67 -> £3,332,571.82 (10.6%); £3,729,528.90 -> £3,332,571.93 (10.6%); £3,729,529.12 -> £3,332,572.03 (10.6%); £3,729,529.35 -> £3,332,572.14 (10.6%); £3,729,529.57 -> £3,332,572.24 (10.6%); £3,729,529.79 -> £3,332,572.34 (10.6%); £3,729,530.01 -> £3,332,572.44 (10.6%); £3,729,530.24 -> £3,332,572.53 (10.6%); £3,729,530.48 -> £3,332,572.62 (10.6%); £3,729,530.71 -> £3,332,572.70 (10.6%); £3,729,530.94 -> £3,332,572.78 (10.6%); £3,729,531.16 -> £3,332,572.87 (10.6%); £3,729,531.39 -> £3,332,572.95 (10.6%); £3,729,531.62 -> £3,332,573.03 (10.6%); £3,729,531.84 -> £3,332,573.35 (10.6%); £3,729,532.07 -> £3,332,573.65 (10.6%); £3,729,532.30 -> £3,332,573.94 (10.6%); £3,729,532.52 -> £3,332,574.22 (10.6%); £3,729,532.74 -> £3,332,574.50 (10.6%); £3,729,532.97 -> £3,332,574.78 (10.6%); £3,729,533.20 -> £3,332,575.06 (10.6%); £3,729,533.43 -> £3,332,575.34 (10.6%); £3,729,533.66 -> £3,332,575.62 (10.6%); £3,729,533.89 -> £3,332,575.90 (10.6%); £3,729,534.12 -> £3,332,576.17 (10.6%); £3,729,534.34 -> £3,332,576.22 (10.6%); £3,729,534.56 -> £3,332,576.26 (10.6%); £3,729,534.77 -> £3,332,576.31 (10.6%); £3,729,534.97 -> £3,332,576.35 (10.6%); £3,729,535.14 -> £3,332,576.39 (10.6%); £3,729,535.27 -> £3,332,576.43 (10.6%); £3,729,535.41 -> £3,332,576.48 (10.6%); £3,729,535.54 -> £3,332,576.52 (10.6%); £3,729,535.68 -> £3,332,576.56 (10.6%); £3,729,535.81 -> £3,332,576.60 (10.6%); £3,729,535.95 -> £3,332,576.64 (10.6%); £3,729,536.08 -> £3,332,576.68 (10.6%); £3,729,536.21 -> £3,332,576.72 (10.6%); £3,729,536.35 -> £3,332,576.76 (10.6%); £3,729,536.49 -> £3,332,576.80 (10.6%); £3,729,536.63 -> £3,332,576.84 (10.6%); £3,729,536.76 -> £3,332,577.10 (10.6%); £3,729,536.90 -> £3,332,577.36 (10.6%); £3,729,537.06 -> £3,332,577.62 (10.6%); £3,729,537.22 -> £3,332,577.89 (10.6%); £3,729,537.40 -> £3,332,578.16 (10.6%); £3,729,537.59 -> £3,332,578.43 (10.6%); £3,729,537.81 -> £3,332,578.70 (10.6%); £3,729,538.03 -> £3,332,578.98 (10.6%); £3,729,538.25 -> £3,332,579.04 (10.6%); £3,729,538.48 -> £3,332,579.09 (10.6%); £3,729,538.71 -> £3,332,579.15 (10.6%); £3,729,538.93 -> £3,332,579.21 (10.6%); £3,729,539.15 -> £3,332,579.27 (10.6%); £3,729,539.37 -> £3,332,579.32 (10.6%); £3,729,539.60 -> £3,332,579.38 (10.6%); £3,729,539.83 -> £3,332,579.43 (10.6%); £3,729,540.06 -> £3,332,579.48 (10.6%); £3,729,540.28 -> £3,332,579.54 (10.6%); £3,729,540.50 -> £3,332,579.59 (10.6%); £3,729,540.74 -> £3,332,579.64 (10.6%); £3,729,540.97 -> £3,332,579.69 (10.6%); £3,729,541.21 -> £3,332,579.96 (10.6%); £3,729,541.43 -> £3,332,580.23 (10.6%); £3,729,541.66 -> £3,332,580.49 (10.6%); £3,729,541.88 -> £3,332,580.75 (10.6%); £3,729,542.10 -> £3,332,581.02 (10.6%); £3,729,542.33 -> £3,332,581.29 (10.6%); £3,729,542.55 -> £3,332,581.56 (10.6%); £3,729,542.77 -> £3,332,581.83 (10.6%); £3,729,542.99 -> £3,332,582.09 (10.6%); £3,729,543.22 -> £3,332,582.35 (10.6%); £3,729,543.46 -> £3,332,582.61 (10.6%); £3,729,543.69 -> £3,332,582.66 (10.6%); £3,729,543.91 -> £3,332,582.70 (10.6%); £3,729,544.12 -> £3,332,582.74 (10.6%); £3,729,544.32 -> £3,332,582.78 (10.6%); £3,729,544.49 -> £3,332,582.83 (10.6%); £3,729,544.64 -> £3,332,582.87 (10.6%); £3,729,544.80 -> £3,332,582.91 (10.6%); £3,729,544.95 -> £3,332,582.95 (10.6%); £3,729,545.11 -> £3,332,582.99 (10.6%); £3,729,545.26 -> £3,332,583.04 (10.6%); £3,729,545.42 -> £3,332,583.08 (10.6%); £3,729,545.58 -> £3,332,583.12 (10.6%); £3,729,545.73 -> £3,332,583.16 (10.6%); £3,729,545.88 -> £3,332,583.21 (10.6%); £3,729,546.03 -> £3,332,583.25 (10.6%); £3,729,546.19 -> £3,332,583.29 (10.6%); £3,729,546.35 -> £3,332,583.54 (10.6%); £3,729,546.50 -> £3,332,583.79 (10.6%); £3,729,546.67 -> £3,332,584.05 (10.6%); £3,729,546.86 -> £3,332,584.33 (10.6%); £3,729,547.07 -> £3,332,584.64 (10.6%); £3,729,547.29 -> £3,332,584.98 (10.6%); £3,729,547.54 -> £3,332,585.35 (10.6%); £3,729,547.80 -> £3,332,585.73 (10.6%); £3,729,548.05 -> £3,332,585.89 (10.6%); £3,729,548.32 -> £3,332,586.04 (10.6%); £3,729,548.58 -> £3,332,586.19 (10.6%); £3,729,548.83 -> £3,332,586.35 (10.6%); £3,729,549.09 -> £3,332,586.50 (10.6%); £3,729,549.35 -> £3,332,586.65 (10.6%); £3,729,549.61 -> £3,332,586.79 (10.6%); £3,729,549.87 -> £3,332,586.93 (10.6%); £3,729,550.14 -> £3,332,587.07 (10.6%); £3,729,550.39 -> £3,332,587.21 (10.6%); £3,729,550.64 -> £3,332,587.35 (10.6%); £3,729,550.91 -> £3,332,587.48 (10.6%); £3,729,551.17 -> £3,332,587.61 (10.6%); £3,729,551.42 -> £3,332,587.98 (10.6%); £3,729,551.67 -> £3,332,588.32 (10.6%); £3,729,551.92 -> £3,332,588.62 (10.6%); £3,729,552.18 -> £3,332,588.90 (10.6%); £3,729,552.43 -> £3,332,589.16 (10.6%); £3,729,552.68 -> £3,332,589.43 (10.6%); £3,729,552.95 -> £3,332,589.69 (10.6%); £3,729,553.21 -> £3,332,589.96 (10.6%); £3,729,553.46 -> £3,332,590.21 (10.6%); £3,729,553.72 -> £3,332,590.46 (10.6%); £3,729,553.98 -> £3,332,590.70 (10.6%); £3,729,554.24 -> £3,332,590.75 (10.6%); £3,729,554.50 -> £3,332,590.80 (10.6%); £3,729,554.74 -> £3,332,590.84 (10.6%); £3,729,554.95 -> £3,332,590.88 (10.6%); £3,729,555.15 -> £3,332,590.92 (10.6%); £3,729,555.30 -> £3,332,590.97 (10.6%); £3,729,555.46 -> £3,332,591.01 (10.6%); £3,729,555.61 -> £3,332,591.05 (10.6%); £3,729,555.77 -> £3,332,591.09 (10.6%); £3,729,555.92 -> £3,332,591.13 (10.6%); £3,729,556.08 -> £3,332,591.18 (10.6%); £3,729,556.23 -> £3,332,591.22 (10.6%); £3,729,556.38 -> £3,332,591.26 (10.6%); £3,729,556.53 -> £3,332,591.30 (10.6%); £3,729,556.68 -> £3,332,591.35 (10.6%); £3,729,556.83 -> £3,332,591.39 (10.6%); £3,729,556.99 -> £3,332,591.61 (10.6%); £3,729,557.14 -> £3,332,591.83 (10.6%); £3,729,557.31 -> £3,332,592.06 (10.6%); £3,729,557.50 -> £3,332,592.30 (10.6%); £3,729,557.70 -> £3,332,592.57 (10.6%); £3,729,557.93 -> £3,332,592.87 (10.6%); £3,729,558.16 -> £3,332,593.20 (10.6%); £3,729,558.43 -> £3,332,593.53 (10.6%); £3,729,558.68 -> £3,332,593.68 (10.6%); £3,729,558.94 -> £3,332,593.83 (10.6%); £3,729,559.20 -> £3,332,593.99 (10.6%); £3,729,559.45 -> £3,332,594.14 (10.6%); £3,729,559.70 -> £3,332,594.30 (10.6%); £3,729,559.96 -> £3,332,594.45 (10.6%); £3,729,560.22 -> £3,332,594.59 (10.6%); £3,729,560.47 -> £3,332,594.73 (10.6%); £3,729,560.72 -> £3,332,594.87 (10.6%); £3,729,560.98 -> £3,332,595.01 (10.6%); £3,729,561.23 -> £3,332,595.15 (10.6%); £3,729,561.50 -> £3,332,595.28 (10.6%); £3,729,561.76 -> £3,332,595.41 (10.6%); £3,729,562.02 -> £3,332,595.75 (10.6%); £3,729,562.28 -> £3,332,596.06 (10.6%); £3,729,562.53 -> £3,332,596.33 (10.6%); £3,729,562.78 -> £3,332,596.57 (10.6%); £3,729,563.05 -> £3,332,596.80 (10.6%); £3,729,563.30 -> £3,332,597.03 (10.6%); £3,729,563.56 -> £3,332,597.26 (10.6%); £3,729,563.82 -> £3,332,597.47 (10.6%); £3,729,564.08 -> £3,332,597.70 (10.6%); £3,729,564.32 -> £3,332,597.91 (10.6%); £3,729,564.58 -> £3,332,598.12 (10.6%); £3,729,564.84 -> £3,332,598.17 (10.6%); £3,729,565.10 -> £3,332,598.22 (10.6%); £3,729,565.34 -> £3,332,598.26 (10.6%); £3,729,565.55 -> £3,332,598.30 (10.6%); £3,729,565.75 -> £3,332,598.34 (10.6%); £3,729,565.90 -> £3,332,598.39 (10.6%); £3,729,566.05 -> £3,332,598.43 (10.6%); £3,729,566.20 -> £3,332,598.47 (10.6%); £3,729,566.35 -> £3,332,598.51 (10.6%); £3,729,566.50 -> £3,332,598.55 (10.6%); £3,729,566.65 -> £3,332,598.59 (10.6%); £3,729,566.80 -> £3,332,598.64 (10.6%); £3,729,566.96 -> £3,332,598.68 (10.6%); £3,729,567.11 -> £3,332,598.72 (10.6%); £3,729,567.26 -> £3,332,598.76 (10.6%); £3,729,567.41 -> £3,332,598.81 (10.6%); £3,729,567.56 -> £3,332,599.05 (10.6%); £3,729,567.72 -> £3,332,599.30 (10.6%); £3,729,567.89 -> £3,332,599.56 (10.6%); £3,729,568.08 -> £3,332,599.83 (10.6%); £3,729,568.29 -> £3,332,600.13 (10.6%); £3,729,568.51 -> £3,332,600.46 (10.6%); £3,729,568.75 -> £3,332,600.82 (10.6%); £3,729,569.00 -> £3,332,601.20 (10.6%); £3,729,569.25 -> £3,332,601.36 (10.6%); £3,729,569.50 -> £3,332,601.51 (10.6%); £3,729,569.75 -> £3,332,601.67 (10.6%); £3,729,570.01 -> £3,332,601.82 (10.6%); £3,729,570.28 -> £3,332,601.97 (10.6%); £3,729,570.54 -> £3,332,602.12 (10.6%); £3,729,570.80 -> £3,332,602.26 (10.6%); £3,729,571.06 -> £3,332,602.40 (10.6%); £3,729,571.32 -> £3,332,602.54 (10.6%); £3,729,571.57 -> £3,332,602.68 (10.6%); £3,729,571.82 -> £3,332,602.81 (10.6%); £3,729,572.07 -> £3,332,602.95 (10.6%); £3,729,572.33 -> £3,332,603.08 (10.6%); £3,729,572.59 -> £3,332,603.46 (10.6%); £3,729,572.85 -> £3,332,603.79 (10.6%); £3,729,573.11 -> £3,332,604.08 (10.6%); £3,729,573.38 -> £3,332,604.35 (10.6%); £3,729,573.63 -> £3,332,604.62 (10.6%); £3,729,573.89 -> £3,332,604.87 (10.6%); £3,729,574.14 -> £3,332,605.14 (10.6%); £3,729,574.39 -> £3,332,605.38 (10.6%); £3,729,574.65 -> £3,332,605.64 (10.6%); £3,729,574.90 -> £3,332,605.89 (10.6%); £3,729,575.16 -> £3,332,606.13 (10.6%); £3,729,575.41 -> £3,332,606.18 (10.6%); £3,729,575.67 -> £3,332,606.23 (10.6%); £3,729,575.90 -> £3,332,606.27 (10.6%); £3,729,576.12 -> £3,332,606.32 (10.6%); £3,729,576.32 -> £3,332,606.36 (10.6%); £3,729,576.47 -> £3,332,606.40 (10.6%); £3,729,576.62 -> £3,332,606.45 (10.6%); £3,729,576.78 -> £3,332,606.49 (10.6%); £3,729,576.93 -> £3,332,606.53 (10.6%); £3,729,577.08 -> £3,332,606.57 (10.6%); £3,729,577.23 -> £3,332,606.61 (10.6%); £3,729,577.38 -> £3,332,606.65 (10.6%); £3,729,577.53 -> £3,332,606.70 (10.6%); £3,729,577.69 -> £3,332,606.74 (10.6%); £3,729,577.84 -> £3,332,606.78 (10.6%); £3,729,578.00 -> £3,332,606.83 (10.6%); £3,729,578.15 -> £3,332,607.05 (10.6%); £3,729,578.30 -> £3,332,607.28 (10.6%); £3,729,578.47 -> £3,332,607.52 (10.6%); £3,729,578.65 -> £3,332,607.77 (10.6%); £3,729,578.85 -> £3,332,608.06 (10.6%); £3,729,579.06 -> £3,332,608.37 (10.6%); £3,729,579.31 -> £3,332,608.70 (10.6%); £3,729,579.57 -> £3,332,609.04 (10.6%); £3,729,579.83 -> £3,332,609.19 (10.6%); £3,729,580.09 -> £3,332,609.34 (10.6%); £3,729,580.35 -> £3,332,609.49 (10.6%); £3,729,580.59 -> £3,332,609.64 (10.6%); £3,729,580.85 -> £3,332,609.79 (10.6%); £3,729,581.09 -> £3,332,609.93 (10.6%); £3,729,581.35 -> £3,332,610.07 (10.6%); £3,729,581.60 -> £3,332,610.21 (10.6%); £3,729,581.86 -> £3,332,610.35 (10.6%); £3,729,582.12 -> £3,332,610.48 (10.6%); £3,729,582.37 -> £3,332,610.62 (10.6%); £3,729,582.63 -> £3,332,610.75 (10.6%); £3,729,582.89 -> £3,332,610.88 (10.6%); £3,729,583.14 -> £3,332,611.21 (10.6%); £3,729,583.40 -> £3,332,611.53 (10.6%); £3,729,583.66 -> £3,332,611.82 (10.6%); £3,729,583.91 -> £3,332,612.08 (10.6%); £3,729,584.17 -> £3,332,612.33 (10.6%); £3,729,584.43 -> £3,332,612.58 (10.6%); £3,729,584.68 -> £3,332,612.82 (10.6%); £3,729,584.93 -> £3,332,613.06 (10.6%); £3,729,585.19 -> £3,332,613.30 (10.6%); £3,729,585.45 -> £3,332,613.53 (10.6%); £3,729,585.70 -> £3,332,613.75 (10.6%); £3,729,585.96 -> £3,332,613.80 (10.6%); £3,729,586.20 -> £3,332,613.84 (10.6%); £3,729,586.45 -> £3,332,613.89 (10.6%); £3,729,586.66 -> £3,332,613.93 (10.6%); £3,729,586.86 -> £3,332,613.97 (10.6%); £3,729,587.01 -> £3,332,614.01 (10.6%); £3,729,587.16 -> £3,332,614.06 (10.6%); £3,729,587.32 -> £3,332,614.10 (10.6%); £3,729,587.46 -> £3,332,614.14 (10.6%); £3,729,587.62 -> £3,332,614.18 (10.6%); £3,729,587.77 -> £3,332,614.22 (10.6%); £3,729,587.93 -> £3,332,614.26 (10.6%); £3,729,588.07 -> £3,332,614.31 (10.6%); £3,729,588.23 -> £3,332,614.35 (10.6%); £3,729,588.38 -> £3,332,614.39 (10.6%); £3,729,588.54 -> £3,332,614.44 (10.6%); £3,729,588.69 -> £3,332,614.67 (10.6%); £3,729,588.85 -> £3,332,614.90 (10.6%); £3,729,589.02 -> £3,332,615.15 (10.6%); £3,729,589.20 -> £3,332,615.41 (10.6%); £3,729,589.40 -> £3,332,615.70 (10.6%); £3,729,589.62 -> £3,332,616.01 (10.6%); £3,729,589.86 -> £3,332,616.35 (10.6%); £3,729,590.12 -> £3,332,616.70 (10.6%); £3,729,590.39 -> £3,332,616.85 (10.6%); £3,729,590.64 -> £3,332,617.00 (10.6%); £3,729,590.90 -> £3,332,617.15 (10.6%); £3,729,591.16 -> £3,332,617.30 (10.6%); £3,729,591.41 -> £3,332,617.45 (10.6%); £3,729,591.66 -> £3,332,617.59 (10.6%); £3,729,591.92 -> £3,332,617.73 (10.6%); £3,729,592.17 -> £3,332,617.87 (10.6%); £3,729,592.43 -> £3,332,618.02 (10.6%); £3,729,592.69 -> £3,332,618.16 (10.6%); £3,729,592.94 -> £3,332,618.29 (10.6%); £3,729,593.19 -> £3,332,618.42 (10.6%); £3,729,593.45 -> £3,332,618.55 (10.6%); £3,729,593.71 -> £3,332,618.89 (10.6%); £3,729,593.96 -> £3,332,619.21 (10.6%); £3,729,594.21 -> £3,332,619.49 (10.6%); £3,729,594.46 -> £3,332,619.75 (10.6%); £3,729,594.73 -> £3,332,619.99 (10.6%); £3,729,594.97 -> £3,332,620.24 (10.6%); £3,729,595.22 -> £3,332,620.47 (10.6%); £3,729,595.48 -> £3,332,620.71 (10.6%); £3,729,595.74 -> £3,332,620.94 (10.6%); £3,729,595.99 -> £3,332,621.16 (10.6%); £3,729,596.24 -> £3,332,621.38 (10.6%); £3,729,596.50 -> £3,332,621.43 (10.6%); £3,729,596.76 -> £3,332,621.48 (10.6%); £3,729,596.99 -> £3,332,621.52 (10.6%); £3,729,597.21 -> £3,332,621.57 (10.6%); £3,729,597.40 -> £3,332,621.61 (10.6%); £3,729,597.53 -> £3,332,621.65 (10.6%); £3,729,597.66 -> £3,332,621.69 (10.6%); £3,729,597.80 -> £3,332,621.73 (10.6%); £3,729,597.93 -> £3,332,621.77 (10.6%); £3,729,598.06 -> £3,332,621.82 (10.6%); £3,729,598.20 -> £3,332,621.86 (10.6%); £3,729,598.34 -> £3,332,621.90 (10.6%); £3,729,598.47 -> £3,332,621.94 (10.6%); £3,729,598.60 -> £3,332,621.98 (10.6%); £3,729,598.74 -> £3,332,622.03 (10.6%); £3,729,598.87 -> £3,332,622.07 (10.6%); £3,729,599.00 -> £3,332,622.27 (10.6%); £3,729,599.14 -> £3,332,622.48 (10.6%); £3,729,599.29 -> £3,332,622.69 (10.6%); £3,729,599.45 -> £3,332,622.91 (10.6%); £3,729,599.64 -> £3,332,623.16 (10.6%); £3,729,599.83 -> £3,332,623.40 (10.6%); £3,729,600.04 -> £3,332,623.67 (10.6%); £3,729,600.27 -> £3,332,623.95 (10.6%); £3,729,600.49 -> £3,332,624.06 (10.6%); £3,729,600.71 -> £3,332,624.16 (10.6%); £3,729,600.94 -> £3,332,624.27 (10.6%); £3,729,601.16 -> £3,332,624.37 (10.6%); £3,729,601.38 -> £3,332,624.47 (10.6%); £3,729,601.61 -> £3,332,624.56 (10.6%); £3,729,601.83 -> £3,332,624.65 (10.6%); £3,729,602.05 -> £3,332,624.74 (10.6%); £3,729,602.28 -> £3,332,624.82 (10.6%); £3,729,602.51 -> £3,332,624.90 (10.6%); £3,729,602.74 -> £3,332,624.98 (10.6%); £3,729,602.97 -> £3,332,625.06 (10.6%); £3,729,603.19 -> £3,332,625.14 (10.6%); £3,729,603.42 -> £3,332,625.40 (10.6%); £3,729,603.65 -> £3,332,625.65 (10.6%); £3,729,603.87 -> £3,332,625.88 (10.6%); £3,729,604.10 -> £3,332,626.10 (10.6%); £3,729,604.32 -> £3,332,626.31 (10.6%); £3,729,604.55 -> £3,332,626.54 (10.6%); £3,729,604.77 -> £3,332,626.76 (10.6%); £3,729,604.99 -> £3,332,626.98 (10.6%); £3,729,605.20 -> £3,332,627.20 (10.6%); £3,729,605.43 -> £3,332,627.41 (10.6%); £3,729,605.65 -> £3,332,627.62 (10.6%); £3,729,605.87 -> £3,332,627.67 (10.6%); £3,729,606.09 -> £3,332,627.71 (10.6%); £3,729,606.31 -> £3,332,627.76 (10.6%); £3,729,606.49 -> £3,332,627.80 (10.6%); £3,729,606.67 -> £3,332,627.84 (10.6%); £3,729,606.80 -> £3,332,627.88 (10.6%); £3,729,606.94 -> £3,332,627.93 (10.6%); £3,729,607.07 -> £3,332,627.97 (10.6%); £3,729,607.21 -> £3,332,628.01 (10.6%); £3,729,607.34 -> £3,332,628.06 (10.6%); £3,729,607.48 -> £3,332,628.10 (10.6%); £3,729,607.61 -> £3,332,628.14 (10.6%); £3,729,607.75 -> £3,332,628.18 (10.6%); £3,729,607.89 -> £3,332,628.23 (10.6%); £3,729,608.02 -> £3,332,628.27 (10.6%); £3,729,608.16 -> £3,332,628.31 (10.6%); £3,729,608.29 -> £3,332,628.50 (10.6%); £3,729,608.43 -> £3,332,628.70 (10.6%); £3,729,608.58 -> £3,332,628.89 (10.6%); £3,729,608.74 -> £3,332,629.09 (10.6%); £3,729,608.92 -> £3,332,629.29 (10.6%); £3,729,609.12 -> £3,332,629.49 (10.6%); £3,729,609.32 -> £3,332,629.69 (10.6%); £3,729,609.55 -> £3,332,629.90 (10.6%); £3,729,609.78 -> £3,332,629.96 (10.6%); £3,729,610.00 -> £3,332,630.01 (10.6%); £3,729,610.23 -> £3,332,630.07 (10.6%); £3,729,610.45 -> £3,332,630.12 (10.6%); £3,729,610.68 -> £3,332,630.18 (10.6%); £3,729,610.90 -> £3,332,630.23 (10.6%); £3,729,611.12 -> £3,332,630.29 (10.6%); £3,729,611.34 -> £3,332,630.34 (10.6%); £3,729,611.57 -> £3,332,630.39 (10.6%); £3,729,611.80 -> £3,332,630.44 (10.6%); £3,729,612.02 -> £3,332,630.50 (10.6%); £3,729,612.24 -> £3,332,630.55 (10.6%); £3,729,612.46 -> £3,332,630.60 (10.6%); £3,729,612.69 -> £3,332,630.82 (10.6%); £3,729,612.92 -> £3,332,631.03 (10.6%); £3,729,613.15 -> £3,332,631.23 (10.6%); £3,729,613.37 -> £3,332,631.44 (10.6%); £3,729,613.59 -> £3,332,631.64 (10.6%); £3,729,613.80 -> £3,332,631.85 (10.6%); £3,729,614.02 -> £3,332,632.05 (10.6%); £3,729,614.24 -> £3,332,632.25 (10.6%); £3,729,614.46 -> £3,332,632.45 (10.6%); £3,729,614.69 -> £3,332,632.65 (10.6%); £3,729,614.92 -> £3,332,632.85 (10.6%); £3,729,615.14 -> £3,332,632.89 (10.6%); £3,729,615.36 -> £3,332,632.94 (10.6%); £3,729,615.57 -> £3,332,632.98 (10.6%); £3,729,615.76 -> £3,332,633.02 (10.6%); £3,729,615.94 -> £3,332,633.06 (10.6%); £3,729,616.09 -> £3,332,633.10 (10.6%); £3,729,616.24 -> £3,332,633.15 (10.6%); £3,729,616.40 -> £3,332,633.19 (10.6%); £3,729,616.55 -> £3,332,633.23 (10.6%); £3,729,616.70 -> £3,332,633.27 (10.6%); £3,729,616.86 -> £3,332,633.31 (10.6%); £3,729,617.00 -> £3,332,633.36 (10.6%); £3,729,617.16 -> £3,332,633.40 (10.6%); £3,729,617.31 -> £3,332,633.44 (10.6%); £3,729,617.46 -> £3,332,633.48 (10.6%); £3,729,617.61 -> £3,332,633.53 (10.6%); £3,729,617.76 -> £3,332,633.75 (10.6%); £3,729,617.90 -> £3,332,633.97 (10.6%); £3,729,618.08 -> £3,332,634.20 (10.6%); £3,729,618.27 -> £3,332,634.44 (10.6%); £3,729,618.48 -> £3,332,634.70 (10.6%); £3,729,618.69 -> £3,332,634.99 (10.6%); £3,729,618.93 -> £3,332,635.31 (10.6%); £3,729,619.18 -> £3,332,635.64 (10.6%); £3,729,619.43 -> £3,332,635.79 (10.6%); £3,729,619.68 -> £3,332,635.93 (10.6%); £3,729,619.94 -> £3,332,636.08 (10.6%); £3,729,620.20 -> £3,332,636.23 (10.6%); £3,729,620.45 -> £3,332,636.38 (10.6%); £3,729,620.71 -> £3,332,636.52 (10.6%); £3,729,620.96 -> £3,332,636.66 (10.6%); £3,729,621.20 -> £3,332,636.79 (10.6%); £3,729,621.45 -> £3,332,636.93 (10.6%); £3,729,621.71 -> £3,332,637.06 (10.6%); £3,729,621.97 -> £3,332,637.19 (10.6%); £3,729,622.22 -> £3,332,637.32 (10.6%); £3,729,622.47 -> £3,332,637.45 (10.6%); £3,729,622.73 -> £3,332,637.76 (10.6%); £3,729,622.97 -> £3,332,638.05 (10.6%); £3,729,623.23 -> £3,332,638.30 (10.6%); £3,729,623.49 -> £3,332,638.53 (10.6%); £3,729,623.74 -> £3,332,638.76 (10.6%); £3,729,624.00 -> £3,332,639.00 (10.6%); £3,729,624.24 -> £3,332,639.23 (10.6%); £3,729,624.49 -> £3,332,639.45 (10.6%); £3,729,624.75 -> £3,332,639.68 (10.6%); £3,729,625.00 -> £3,332,639.89 (10.6%); £3,729,625.26 -> £3,332,640.09 (10.6%); £3,729,625.51 -> £3,332,640.14 (10.6%); £3,729,625.77 -> £3,332,640.19 (10.6%); £3,729,626.00 -> £3,332,640.23 (10.6%); £3,729,626.21 -> £3,332,640.28 (10.6%); £3,729,626.41 -> £3,332,640.32 (10.6%); £3,729,626.56 -> £3,332,640.36 (10.6%); £3,729,626.70 -> £3,332,640.40 (10.6%); £3,729,626.85 -> £3,332,640.44 (10.6%); £3,729,627.00 -> £3,332,640.49 (10.6%); £3,729,627.15 -> £3,332,640.53 (10.6%); £3,729,627.30 -> £3,332,640.57 (10.6%); £3,729,627.45 -> £3,332,640.61 (10.6%); £3,729,627.61 -> £3,332,640.66 (10.6%); £3,729,627.75 -> £3,332,640.70 (10.6%); £3,729,627.90 -> £3,332,640.74 (10.6%); £3,729,628.05 -> £3,332,640.79 (10.6%); £3,729,628.20 -> £3,332,640.95 (10.6%); £3,729,628.35 -> £3,332,641.13 (10.6%); £3,729,628.52 -> £3,332,641.32 (10.6%); £3,729,628.71 -> £3,332,641.53 (10.6%); £3,729,628.91 -> £3,332,641.76 (10.6%); £3,729,629.13 -> £3,332,642.02 (10.6%); £3,729,629.36 -> £3,332,642.31 (10.6%); £3,729,629.62 -> £3,332,642.60 (10.6%); £3,729,629.87 -> £3,332,642.75 (10.6%); £3,729,630.11 -> £3,332,642.89 (10.6%); £3,729,630.37 -> £3,332,643.05 (10.6%); £3,729,630.63 -> £3,332,643.20 (10.6%); £3,729,630.88 -> £3,332,643.36 (10.6%); £3,729,631.12 -> £3,332,643.50 (10.6%); £3,729,631.37 -> £3,332,643.65 (10.6%); £3,729,631.62 -> £3,332,643.79 (10.6%); £3,729,631.88 -> £3,332,643.92 (10.6%); £3,729,632.13 -> £3,332,644.06 (10.6%); £3,729,632.38 -> £3,332,644.19 (10.6%); £3,729,632.64 -> £3,332,644.32 (10.6%); £3,729,632.89 -> £3,332,644.45 (10.6%); £3,729,633.15 -> £3,332,644.75 (10.6%); £3,729,633.40 -> £3,332,645.01 (10.6%); £3,729,633.65 -> £3,332,645.23 (10.6%); £3,729,633.92 -> £3,332,645.44 (10.6%); £3,729,634.17 -> £3,332,645.63 (10.6%); £3,729,634.43 -> £3,332,645.83 (10.6%); £3,729,634.68 -> £3,332,646.02 (10.6%); £3,729,634.93 -> £3,332,646.20 (10.6%); £3,729,635.17 -> £3,332,646.38 (10.6%); £3,729,635.42 -> £3,332,646.55 (10.6%); £3,729,635.67 -> £3,332,646.72 (10.6%); £3,729,635.92 -> £3,332,646.76 (10.6%); £3,729,636.16 -> £3,332,646.81 (10.6%); £3,729,636.40 -> £3,332,646.85 (10.6%); £3,729,636.62 -> £3,332,646.90 (10.6%); £3,729,636.81 -> £3,332,646.94 (10.6%); £3,729,636.96 -> £3,332,646.98 (10.6%); £3,729,637.12 -> £3,332,647.02 (10.6%); £3,729,637.27 -> £3,332,647.06 (10.6%); £3,729,637.42 -> £3,332,647.11 (10.6%); £3,729,637.57 -> £3,332,647.15 (10.6%); £3,729,637.72 -> £3,332,647.19 (10.6%); £3,729,637.88 -> £3,332,647.23 (10.6%); £3,729,638.02 -> £3,332,647.28 (10.6%); £3,729,638.18 -> £3,332,647.32 (10.6%); £3,729,638.33 -> £3,332,647.36 (10.6%); £3,729,638.48 -> £3,332,647.41 (10.6%); £3,729,638.63 -> £3,332,647.54 (10.6%); £3,729,638.78 -> £3,332,647.67 (10.6%); £3,729,638.95 -> £3,332,647.82 (10.6%); £3,729,639.13 -> £3,332,647.98 (10.6%); £3,729,639.33 -> £3,332,648.18 (10.6%); £3,729,639.55 -> £3,332,648.41 (10.6%); £3,729,639.79 -> £3,332,648.66 (10.6%); £3,729,640.03 -> £3,332,648.91 (10.6%); £3,729,640.28 -> £3,332,649.07 (10.6%); £3,729,640.53 -> £3,332,649.23 (10.6%); £3,729,640.79 -> £3,332,649.38 (10.6%); £3,729,641.04 -> £3,332,649.53 (10.6%); £3,729,641.29 -> £3,332,649.68 (10.6%); £3,729,641.54 -> £3,332,649.83 (10.6%); £3,729,641.80 -> £3,332,649.97 (10.6%); £3,729,642.05 -> £3,332,650.11 (10.6%); £3,729,642.30 -> £3,332,650.25 (10.6%); £3,729,642.54 -> £3,332,650.39 (10.6%); £3,729,642.79 -> £3,332,650.53 (10.6%); £3,729,643.04 -> £3,332,650.66 (10.6%); £3,729,643.29 -> £3,332,650.79 (10.6%); £3,729,643.53 -> £3,332,651.05 (10.6%); £3,729,643.79 -> £3,332,651.28 (10.6%); £3,729,644.04 -> £3,332,651.47 (10.6%); £3,729,644.29 -> £3,332,651.64 (10.6%); £3,729,644.53 -> £3,332,651.80 (10.6%); £3,729,644.78 -> £3,332,651.96 (10.6%); £3,729,645.03 -> £3,332,652.11 (10.6%); £3,729,645.28 -> £3,332,652.26 (10.6%); £3,729,645.53 -> £3,332,652.41 (10.6%); £3,729,645.77 -> £3,332,652.55 (10.6%); £3,729,646.02 -> £3,332,652.68 (10.6%); £3,729,646.27 -> £3,332,652.73 (10.6%); £3,729,646.52 -> £3,332,652.77 (10.6%); £3,729,646.76 -> £3,332,652.82 (10.6%); £3,729,646.97 -> £3,332,652.86 (10.6%); £3,729,647.16 -> £3,332,652.90 (10.6%); £3,729,647.31 -> £3,332,652.94 (10.6%); £3,729,647.46 -> £3,332,652.98 (10.6%); £3,729,647.62 -> £3,332,653.03 (10.6%); £3,729,647.78 -> £3,332,653.07 (10.6%); £3,729,647.92 -> £3,332,653.11 (10.6%); £3,729,648.07 -> £3,332,653.15 (10.6%); £3,729,648.23 -> £3,332,653.20 (10.6%); £3,729,648.38 -> £3,332,653.24 (10.6%); £3,729,648.53 -> £3,332,653.28 (10.6%); £3,729,648.68 -> £3,332,653.33 (10.6%); £3,729,648.83 -> £3,332,653.37 (10.6%); £3,729,648.98 -> £3,332,653.50 (10.6%); £3,729,649.13 -> £3,332,653.63 (10.6%); £3,729,649.29 -> £3,332,653.78 (10.6%); £3,729,649.47 -> £3,332,653.94 (10.6%); £3,729,649.67 -> £3,332,654.13 (10.6%); £3,729,649.89 -> £3,332,654.34 (10.6%); £3,729,650.12 -> £3,332,654.58 (10.6%); £3,729,650.38 -> £3,332,654.84 (10.6%); £3,729,650.63 -> £3,332,654.99 (10.6%); £3,729,650.88 -> £3,332,655.14 (10.6%); £3,729,651.14 -> £3,332,655.29 (10.6%); £3,729,651.38 -> £3,332,655.44 (10.6%); £3,729,651.64 -> £3,332,655.59 (10.6%); £3,729,651.89 -> £3,332,655.73 (10.6%); £3,729,652.14 -> £3,332,655.87 (10.6%); £3,729,652.39 -> £3,332,656.01 (10.6%); £3,729,652.64 -> £3,332,656.14 (10.6%); £3,729,652.89 -> £3,332,656.28 (10.6%); £3,729,653.15 -> £3,332,656.42 (10.6%); £3,729,653.41 -> £3,332,656.55 (10.6%); £3,729,653.66 -> £3,332,656.68 (10.6%); £3,729,653.91 -> £3,332,656.92 (10.6%); £3,729,654.17 -> £3,332,657.14 (10.6%); £3,729,654.43 -> £3,332,657.33 (10.6%); £3,729,654.68 -> £3,332,657.50 (10.6%); £3,729,654.94 -> £3,332,657.66 (10.6%); £3,729,655.19 -> £3,332,657.81 (10.6%); £3,729,655.44 -> £3,332,657.96 (10.6%); £3,729,655.69 -> £3,332,658.11 (10.6%); £3,729,655.94 -> £3,332,658.25 (10.6%); £3,729,656.19 -> £3,332,658.39 (10.6%); £3,729,656.44 -> £3,332,658.52 (10.6%); £3,729,656.69 -> £3,332,658.57 (10.6%); £3,729,656.95 -> £3,332,658.61 (10.6%); £3,729,657.18 -> £3,332,658.66 (10.6%); £3,729,657.39 -> £3,332,658.70 (10.6%); £3,729,657.59 -> £3,332,658.74 (10.6%); £3,729,657.74 -> £3,332,658.78 (10.6%); £3,729,657.89 -> £3,332,658.83 (10.6%); £3,729,658.04 -> £3,332,658.87 (10.6%); £3,729,658.19 -> £3,332,658.91 (10.6%); £3,729,658.35 -> £3,332,658.96 (10.6%); £3,729,658.50 -> £3,332,659.00 (10.6%); £3,729,658.65 -> £3,332,659.04 (10.6%); £3,729,658.80 -> £3,332,659.08 (10.6%); £3,729,658.96 -> £3,332,659.13 (10.6%); £3,729,659.11 -> £3,332,659.17 (10.6%); £3,729,659.25 -> £3,332,659.22 (10.6%); £3,729,659.41 -> £3,332,659.39 (10.6%); £3,729,659.55 -> £3,332,659.57 (10.6%); £3,729,659.72 -> £3,332,659.76 (10.6%); £3,729,659.91 -> £3,332,659.98 (10.6%); £3,729,660.11 -> £3,332,660.21 (10.6%); £3,729,660.33 -> £3,332,660.47 (10.6%); £3,729,660.57 -> £3,332,660.74 (10.6%); £3,729,660.82 -> £3,332,661.04 (10.6%); £3,729,661.08 -> £3,332,661.19 (10.6%); £3,729,661.32 -> £3,332,661.35 (10.6%); £3,729,661.57 -> £3,332,661.50 (10.6%); £3,729,661.83 -> £3,332,661.67 (10.6%); £3,729,662.07 -> £3,332,661.83 (10.6%); £3,729,662.32 -> £3,332,661.98 (10.6%); £3,729,662.58 -> £3,332,662.12 (10.6%); £3,729,662.82 -> £3,332,662.27 (10.6%); £3,729,663.08 -> £3,332,662.41 (10.6%); £3,729,663.33 -> £3,332,662.56 (10.6%); £3,729,663.59 -> £3,332,662.70 (10.6%); £3,729,663.84 -> £3,332,662.83 (10.6%); £3,729,664.09 -> £3,332,662.96 (10.6%); £3,729,664.34 -> £3,332,663.24 (10.6%); £3,729,664.59 -> £3,332,663.50 (10.6%); £3,729,664.84 -> £3,332,663.72 (10.6%); £3,729,665.10 -> £3,332,663.93 (10.6%); £3,729,665.34 -> £3,332,664.12 (10.6%); £3,729,665.60 -> £3,332,664.31 (10.6%); £3,729,665.84 -> £3,332,664.48 (10.6%); £3,729,666.10 -> £3,332,664.66 (10.6%); £3,729,666.35 -> £3,332,664.83 (10.6%); £3,729,666.61 -> £3,332,664.99 (10.6%); £3,729,666.86 -> £3,332,665.16 (10.6%); £3,729,667.12 -> £3,332,665.21 (10.6%); £3,729,667.36 -> £3,332,665.25 (10.6%); £3,729,667.60 -> £3,332,665.30 (10.6%); £3,729,667.81 -> £3,332,665.34 (10.6%); £3,729,668.00 -> £3,332,665.38 (10.6%); £3,729,668.13 -> £3,332,665.42 (10.6%); £3,729,668.27 -> £3,332,665.46 (10.6%); £3,729,668.40 -> £3,332,665.51 (10.6%); £3,729,668.53 -> £3,332,665.55 (10.6%); £3,729,668.67 -> £3,332,665.59 (10.6%); £3,729,668.81 -> £3,332,665.63 (10.6%); £3,729,668.94 -> £3,332,665.67 (10.6%); £3,729,669.08 -> £3,332,665.71 (10.6%); £3,729,669.21 -> £3,332,665.76 (10.6%); £3,729,669.35 -> £3,332,665.80 (10.6%); £3,729,669.49 -> £3,332,665.84 (10.6%); £3,729,669.62 -> £3,332,666.05 (10.6%); £3,729,669.76 -> £3,332,666.25 (10.6%); £3,729,669.91 -> £3,332,666.47 (10.6%); £3,729,670.08 -> £3,332,666.69 (10.6%); £3,729,670.25 -> £3,332,666.92 (10.6%); £3,729,670.45 -> £3,332,667.17 (10.6%); £3,729,670.67 -> £3,332,667.45 (10.6%); £3,729,670.89 -> £3,332,667.73 (10.6%); £3,729,671.11 -> £3,332,667.84 (10.6%); £3,729,671.33 -> £3,332,667.95 (10.6%); £3,729,671.55 -> £3,332,668.06 (10.6%); £3,729,671.78 -> £3,332,668.16 (10.6%); £3,729,672.01 -> £3,332,668.26 (10.6%); £3,729,672.23 -> £3,332,668.36 (10.6%); £3,729,672.45 -> £3,332,668.44 (10.6%); £3,729,672.68 -> £3,332,668.53 (10.6%); £3,729,672.89 -> £3,332,668.61 (10.6%); £3,729,673.11 -> £3,332,668.69 (10.6%); £3,729,673.33 -> £3,332,668.77 (10.6%); £3,729,673.55 -> £3,332,668.85 (10.6%); £3,729,673.77 -> £3,332,668.93 (10.6%); £3,729,673.99 -> £3,332,669.18 (10.6%); £3,729,674.22 -> £3,332,669.42 (10.6%); £3,729,674.44 -> £3,332,669.64 (10.6%); £3,729,674.67 -> £3,332,669.85 (10.6%); £3,729,674.90 -> £3,332,670.07 (10.6%); £3,729,675.13 -> £3,332,670.28 (10.6%); £3,729,675.35 -> £3,332,670.49 (10.6%); £3,729,675.57 -> £3,332,670.71 (10.6%); £3,729,675.80 -> £3,332,670.91 (10.6%); £3,729,676.02 -> £3,332,671.12 (10.6%); £3,729,676.24 -> £3,332,671.34 (10.6%); £3,729,676.46 -> £3,332,671.39 (10.6%); £3,729,676.68 -> £3,332,671.43 (10.6%); £3,729,676.88 -> £3,332,671.48 (10.6%); £3,729,677.07 -> £3,332,671.52 (10.6%); £3,729,677.25 -> £3,332,671.56 (10.6%); £3,729,677.39 -> £3,332,671.61 (10.6%); £3,729,677.52 -> £3,332,671.65 (10.6%); £3,729,677.65 -> £3,332,671.69 (10.6%); £3,729,677.79 -> £3,332,671.73 (10.6%); £3,729,677.93 -> £3,332,671.78 (10.6%); £3,729,678.06 -> £3,332,671.82 (10.6%); £3,729,678.19 -> £3,332,671.86 (10.6%); £3,729,678.33 -> £3,332,671.90 (10.6%); £3,729,678.46 -> £3,332,671.94 (10.6%); £3,729,678.61 -> £3,332,671.98 (10.6%); £3,729,678.74 -> £3,332,672.02 (10.6%); £3,729,678.88 -> £3,332,672.14 (10.6%); £3,729,679.01 -> £3,332,672.26 (10.6%); £3,729,679.16 -> £3,332,672.38 (10.6%); £3,729,679.33 -> £3,332,672.50 (10.6%); £3,729,679.51 -> £3,332,672.62 (10.6%); £3,729,679.71 -> £3,332,672.75 (10.6%); £3,729,679.92 -> £3,332,672.87 (10.6%); £3,729,680.15 -> £3,332,673.00 (10.6%); £3,729,680.38 -> £3,332,673.06 (10.6%); £3,729,680.60 -> £3,332,673.11 (10.6%); £3,729,680.82 -> £3,332,673.17 (10.6%); £3,729,681.05 -> £3,332,673.22 (10.6%); £3,729,681.27 -> £3,332,673.28 (10.6%); £3,729,681.50 -> £3,332,673.33 (10.6%); £3,729,681.73 -> £3,332,673.39 (10.6%); £3,729,681.96 -> £3,332,673.44 (10.6%); £3,729,682.19 -> £3,332,673.49 (10.6%); £3,729,682.42 -> £3,332,673.55 (10.6%); £3,729,682.64 -> £3,332,673.60 (10.6%); £3,729,682.87 -> £3,332,673.65 (10.6%); £3,729,683.10 -> £3,332,673.70 (10.6%); £3,729,683.32 -> £3,332,673.84 (10.6%); £3,729,683.55 -> £3,332,673.97 (10.6%); £3,729,683.77 -> £3,332,674.11 (10.6%); £3,729,684.00 -> £3,332,674.25 (10.6%); £3,729,684.23 -> £3,332,674.38 (10.6%); £3,729,684.45 -> £3,332,674.52 (10.6%); £3,729,684.68 -> £3,332,674.66 (10.6%); £3,729,684.90 -> £3,332,674.79 (10.6%); £3,729,685.12 -> £3,332,674.92 (10.6%); £3,729,685.34 -> £3,332,675.05 (10.6%); £3,729,685.58 -> £3,332,675.18 (10.6%); £3,729,685.80 -> £3,332,675.22 (10.6%); £3,729,686.03 -> £3,332,675.27 (10.6%); £3,729,686.24 -> £3,332,675.31 (10.6%); £3,729,686.44 -> £3,332,675.35 (10.6%); £3,729,686.62 -> £3,332,675.39 (10.6%); £3,729,686.77 -> £3,332,675.43 (10.6%); £3,729,686.93 -> £3,332,675.47 (10.6%); £3,729,687.08 -> £3,332,675.51 (10.6%); £3,729,687.23 -> £3,332,675.56 (10.6%); £3,729,687.39 -> £3,332,675.60 (10.6%); £3,729,687.54 -> £3,332,675.64 (10.6%); £3,729,687.69 -> £3,332,675.68 (10.6%); £3,729,687.85 -> £3,332,675.73 (10.6%); £3,729,688.00 -> £3,332,675.77 (10.6%); £3,729,688.15 -> £3,332,675.81 (10.6%); £3,729,688.30 -> £3,332,675.86 (10.6%); £3,729,688.46 -> £3,332,676.02 (10.6%); £3,729,688.61 -> £3,332,676.18 (10.6%); £3,729,688.78 -> £3,332,676.35 (10.6%); £3,729,688.97 -> £3,332,676.53 (10.6%); £3,729,689.18 -> £3,332,676.75 (10.6%); £3,729,689.40 -> £3,332,677.00 (10.6%); £3,729,689.64 -> £3,332,677.28 (10.6%); £3,729,689.91 -> £3,332,677.57 (10.6%); £3,729,690.16 -> £3,332,677.73 (10.6%); £3,729,690.41 -> £3,332,677.87 (10.6%); £3,729,690.67 -> £3,332,678.02 (10.6%); £3,729,690.92 -> £3,332,678.18 (10.6%); £3,729,691.16 -> £3,332,678.33 (10.6%); £3,729,691.42 -> £3,332,678.48 (10.6%); £3,729,691.67 -> £3,332,678.62 (10.6%); £3,729,691.92 -> £3,332,678.76 (10.6%); £3,729,692.19 -> £3,332,678.90 (10.6%); £3,729,692.45 -> £3,332,679.04 (10.6%); £3,729,692.71 -> £3,332,679.17 (10.6%); £3,729,692.96 -> £3,332,679.31 (10.6%); £3,729,693.23 -> £3,332,679.44 (10.6%); £3,729,693.48 -> £3,332,679.73 (10.6%); £3,729,693.74 -> £3,332,679.99 (10.6%); £3,729,694.00 -> £3,332,680.22 (10.6%); £3,729,694.25 -> £3,332,680.41 (10.6%); £3,729,694.51 -> £3,332,680.60 (10.6%); £3,729,694.77 -> £3,332,680.78 (10.6%); £3,729,695.02 -> £3,332,680.96 (10.6%); £3,729,695.28 -> £3,332,681.13 (10.6%); £3,729,695.53 -> £3,332,681.31 (10.6%); £3,729,695.79 -> £3,332,681.47 (10.6%); £3,729,696.05 -> £3,332,681.64 (10.6%); £3,729,696.30 -> £3,332,681.68 (10.6%); £3,729,696.56 -> £3,332,681.73 (10.6%); £3,729,696.80 -> £3,332,681.78 (10.6%); £3,729,697.01 -> £3,332,681.82 (10.6%); £3,729,697.21 -> £3,332,681.86 (10.6%); £3,729,697.37 -> £3,332,681.90 (10.6%); £3,729,697.52 -> £3,332,681.95 (10.6%); £3,729,697.68 -> £3,332,681.99 (10.6%); £3,729,697.83 -> £3,332,682.03 (10.6%); £3,729,697.99 -> £3,332,682.07 (10.6%); £3,729,698.14 -> £3,332,682.12 (10.6%); £3,729,698.30 -> £3,332,682.16 (10.6%); £3,729,698.45 -> £3,332,682.20 (10.6%); £3,729,698.60 -> £3,332,682.24 (10.6%); £3,729,698.76 -> £3,332,682.29 (10.6%); £3,729,698.91 -> £3,332,682.33 (10.6%); £3,729,699.07 -> £3,332,682.47 (10.6%); £3,729,699.23 -> £3,332,682.61 (10.6%); £3,729,699.40 -> £3,332,682.77 (10.6%); £3,729,699.59 -> £3,332,682.94 (10.6%); £3,729,699.80 -> £3,332,683.14 (10.6%); £3,729,700.02 -> £3,332,683.38 (10.6%); £3,729,700.26 -> £3,332,683.65 (10.6%); £3,729,700.52 -> £3,332,683.92 (10.6%); £3,729,700.78 -> £3,332,684.07 (10.6%); £3,729,701.03 -> £3,332,684.21 (10.6%); £3,729,701.28 -> £3,332,684.38 (10.6%); £3,729,701.54 -> £3,332,684.53 (10.6%); £3,729,701.80 -> £3,332,684.68 (10.6%); £3,729,702.06 -> £3,332,684.82 (10.6%); £3,729,702.32 -> £3,332,684.96 (10.6%); £3,729,702.58 -> £3,332,685.10 (10.6%); £3,729,702.86 -> £3,332,685.23 (10.6%); £3,729,703.11 -> £3,332,685.37 (10.6%); £3,729,703.37 -> £3,332,685.51 (10.6%); £3,729,703.63 -> £3,332,685.64 (10.6%); £3,729,703.88 -> £3,332,685.77 (10.6%); £3,729,704.13 -> £3,332,686.03 (10.6%); £3,729,704.39 -> £3,332,686.25 (10.6%); £3,729,704.65 -> £3,332,686.45 (10.6%); £3,729,704.91 -> £3,332,686.61 (10.6%); £3,729,705.17 -> £3,332,686.77 (10.6%); £3,729,705.43 -> £3,332,686.94 (10.6%); £3,729,705.69 -> £3,332,687.09 (10.6%); £3,729,705.95 -> £3,332,687.25 (10.6%); £3,729,706.20 -> £3,332,687.40 (10.6%); £3,729,706.46 -> £3,332,687.54 (10.6%); £3,729,706.71 -> £3,332,687.68 (10.6%); £3,729,706.97 -> £3,332,687.72 (10.6%); £3,729,707.22 -> £3,332,687.77 (10.6%); £3,729,707.47 -> £3,332,687.81 (10.6%); £3,729,707.69 -> £3,332,687.86 (10.6%); £3,729,707.88 -> £3,332,687.90 (10.6%); £3,729,708.03 -> £3,332,687.94 (10.6%); £3,729,708.19 -> £3,332,687.98 (10.6%); £3,729,708.34 -> £3,332,688.02 (10.6%); £3,729,708.49 -> £3,332,688.06 (10.6%); £3,729,708.64 -> £3,332,688.11 (10.6%); £3,729,708.80 -> £3,332,688.15 (10.6%); £3,729,708.96 -> £3,332,688.19 (10.6%); £3,729,709.11 -> £3,332,688.23 (10.6%); £3,729,709.26 -> £3,332,688.27 (10.6%); £3,729,709.42 -> £3,332,688.32 (10.6%); £3,729,709.59 -> £3,332,688.36 (10.6%); £3,729,709.74 -> £3,332,688.52 (10.6%); £3,729,709.90 -> £3,332,688.69 (10.6%); £3,729,710.07 -> £3,332,688.87 (10.6%); £3,729,710.25 -> £3,332,689.06 (10.6%); £3,729,710.46 -> £3,332,689.28 (10.6%); £3,729,710.69 -> £3,332,689.52 (10.6%); £3,729,710.93 -> £3,332,689.80 (10.6%); £3,729,711.19 -> £3,332,690.08 (10.6%); £3,729,711.45 -> £3,332,690.23 (10.6%); £3,729,711.71 -> £3,332,690.38 (10.6%); £3,729,711.96 -> £3,332,690.53 (10.6%); £3,729,712.21 -> £3,332,690.69 (10.6%); £3,729,712.47 -> £3,332,690.84 (10.6%); £3,729,712.73 -> £3,332,690.98 (10.6%); £3,729,712.98 -> £3,332,691.12 (10.6%); £3,729,713.24 -> £3,332,691.25 (10.6%); £3,729,713.49 -> £3,332,691.39 (10.6%); £3,729,713.74 -> £3,332,691.53 (10.6%); £3,729,714.01 -> £3,332,691.66 (10.6%); £3,729,714.26 -> £3,332,691.80 (10.6%); £3,729,714.52 -> £3,332,691.93 (10.6%); £3,729,714.77 -> £3,332,692.22 (10.6%); £3,729,715.03 -> £3,332,692.48 (10.6%); £3,729,715.30 -> £3,332,692.69 (10.6%); £3,729,715.55 -> £3,332,692.87 (10.6%); £3,729,715.81 -> £3,332,693.05 (10.6%); £3,729,716.07 -> £3,332,693.22 (10.6%); £3,729,716.33 -> £3,332,693.40 (10.6%); £3,729,716.58 -> £3,332,693.57 (10.6%); £3,729,716.84 -> £3,332,693.75 (10.6%); £3,729,717.10 -> £3,332,693.91 (10.6%); £3,729,717.35 -> £3,332,694.08 (10.6%); £3,729,717.60 -> £3,332,694.13 (10.6%); £3,729,717.86 -> £3,332,694.17 (10.6%); £3,729,718.10 -> £3,332,694.22 (10.6%); £3,729,718.32 -> £3,332,694.26 (10.6%); £3,729,718.53 -> £3,332,694.30 (10.6%); £3,729,718.69 -> £3,332,694.34 (10.6%); £3,729,718.84 -> £3,332,694.38 (10.6%); £3,729,718.99 -> £3,332,694.43 (10.6%); £3,729,719.14 -> £3,332,694.47 (10.6%); £3,729,719.29 -> £3,332,694.51 (10.6%); £3,729,719.44 -> £3,332,694.55 (10.6%); £3,729,719.59 -> £3,332,694.60 (10.6%); £3,729,719.75 -> £3,332,694.64 (10.6%); £3,729,719.90 -> £3,332,694.68 (10.6%); £3,729,720.05 -> £3,332,694.72 (10.6%); £3,729,720.20 -> £3,332,694.77 (10.6%); £3,729,720.35 -> £3,332,694.95 (10.6%); £3,729,720.51 -> £3,332,695.13 (10.6%); £3,729,720.68 -> £3,332,695.33 (10.6%); £3,729,720.86 -> £3,332,695.54 (10.6%); £3,729,721.07 -> £3,332,695.78 (10.6%); £3,729,721.29 -> £3,332,696.04 (10.6%); £3,729,721.53 -> £3,332,696.33 (10.6%); £3,729,721.79 -> £3,332,696.63 (10.6%); £3,729,722.05 -> £3,332,696.78 (10.6%); £3,729,722.30 -> £3,332,696.93 (10.6%); £3,729,722.56 -> £3,332,697.09 (10.6%); £3,729,722.81 -> £3,332,697.24 (10.6%); £3,729,723.08 -> £3,332,697.40 (10.6%); £3,729,723.33 -> £3,332,697.55 (10.6%); £3,729,723.58 -> £3,332,697.69 (10.6%); £3,729,723.83 -> £3,332,697.83 (10.6%); £3,729,724.09 -> £3,332,697.96 (10.6%); £3,729,724.34 -> £3,332,698.10 (10.6%); £3,729,724.60 -> £3,332,698.24 (10.6%); £3,729,724.85 -> £3,332,698.37 (10.6%); £3,729,725.11 -> £3,332,698.50 (10.6%); £3,729,725.37 -> £3,332,698.80 (10.6%); £3,729,725.61 -> £3,332,699.08 (10.6%); £3,729,725.87 -> £3,332,699.32 (10.6%); £3,729,726.13 -> £3,332,699.54 (10.6%); £3,729,726.39 -> £3,332,699.74 (10.6%); £3,729,726.65 -> £3,332,699.95 (10.6%); £3,729,726.90 -> £3,332,700.15 (10.6%); £3,729,727.16 -> £3,332,700.34 (10.6%); £3,729,727.41 -> £3,332,700.53 (10.6%); £3,729,727.66 -> £3,332,700.72 (10.6%); £3,729,727.92 -> £3,332,700.90 (10.6%); £3,729,728.18 -> £3,332,700.94 (10.6%); £3,729,728.43 -> £3,332,700.99 (10.6%); £3,729,728.66 -> £3,332,701.04 (10.6%); £3,729,728.89 -> £3,332,701.08 (10.6%); £3,729,729.08 -> £3,332,701.12 (10.6%); £3,729,729.24 -> £3,332,701.17 (10.6%); £3,729,729.40 -> £3,332,701.21 (10.6%); £3,729,729.54 -> £3,332,701.26 (10.6%); £3,729,729.70 -> £3,332,701.30 (10.6%); £3,729,729.85 -> £3,332,701.34 (10.6%); £3,729,730.00 -> £3,332,701.39 (10.6%); £3,729,730.16 -> £3,332,701.43 (10.6%); £3,729,730.31 -> £3,332,701.47 (10.6%); £3,729,730.46 -> £3,332,701.52 (10.6%); £3,729,730.61 -> £3,332,701.56 (10.6%); £3,729,730.76 -> £3,332,701.60 (10.6%); £3,729,730.92 -> £3,332,701.78 (10.6%); £3,729,731.07 -> £3,332,701.97 (10.6%); £3,729,731.24 -> £3,332,702.19 (10.6%); £3,729,731.43 -> £3,332,702.41 (10.6%); £3,729,731.64 -> £3,332,702.65 (10.6%); £3,729,731.86 -> £3,332,702.93 (10.6%); £3,729,732.10 -> £3,332,703.23 (10.6%); £3,729,732.37 -> £3,332,703.55 (10.6%); £3,729,732.63 -> £3,332,703.70 (10.6%); £3,729,732.89 -> £3,332,703.85 (10.6%); £3,729,733.15 -> £3,332,704.01 (10.6%); £3,729,733.41 -> £3,332,704.17 (10.6%); £3,729,733.66 -> £3,332,704.32 (10.6%); £3,729,733.92 -> £3,332,704.47 (10.6%); £3,729,734.18 -> £3,332,704.60 (10.6%); £3,729,734.43 -> £3,332,704.75 (10.6%); £3,729,734.69 -> £3,332,704.90 (10.6%); £3,729,734.95 -> £3,332,705.04 (10.6%); £3,729,735.20 -> £3,332,705.19 (10.6%); £3,729,735.46 -> £3,332,705.33 (10.6%); £3,729,735.72 -> £3,332,705.46 (10.6%); £3,729,735.98 -> £3,332,705.77 (10.6%); £3,729,736.24 -> £3,332,706.05 (10.6%); £3,729,736.49 -> £3,332,706.29 (10.6%); £3,729,736.76 -> £3,332,706.51 (10.6%); £3,729,737.00 -> £3,332,706.72 (10.6%); £3,729,737.26 -> £3,332,706.92 (10.6%); £3,729,737.52 -> £3,332,707.12 (10.6%); £3,729,737.79 -> £3,332,707.31 (10.6%); £3,729,738.04 -> £3,332,707.51 (10.6%); £3,729,738.30 -> £3,332,707.70 (10.6%); £3,729,738.56 -> £3,332,707.89 (10.6%); £3,729,738.81 -> £3,332,707.94 (10.6%); £3,729,739.07 -> £3,332,707.98 (10.6%); £3,729,739.31 -> £3,332,708.03 (10.6%); £3,729,739.53 -> £3,332,708.07 (10.6%); £3,729,739.73 -> £3,332,708.11 (10.6%); £3,729,739.87 -> £3,332,708.16 (10.6%); £3,729,740.01 -> £3,332,708.20 (10.6%); £3,729,740.15 -> £3,332,708.24 (10.6%); £3,729,740.28 -> £3,332,708.29 (10.6%); £3,729,740.42 -> £3,332,708.33 (10.6%); £3,729,740.55 -> £3,332,708.37 (10.6%); £3,729,740.69 -> £3,332,708.42 (10.6%); £3,729,740.83 -> £3,332,708.46 (10.6%); £3,729,740.96 -> £3,332,708.50 (10.6%); £3,729,741.10 -> £3,332,708.55 (10.6%); £3,729,741.24 -> £3,332,708.59 (10.6%); £3,729,741.37 -> £3,332,708.83 (10.6%); £3,729,741.50 -> £3,332,709.07 (10.6%); £3,729,741.65 -> £3,332,709.32 (10.6%); £3,729,741.82 -> £3,332,709.58 (10.6%); £3,729,742.00 -> £3,332,709.86 (10.6%); £3,729,742.20 -> £3,332,710.15 (10.6%); £3,729,742.41 -> £3,332,710.47 (10.6%); £3,729,742.64 -> £3,332,710.80 (10.6%); £3,729,742.87 -> £3,332,710.91 (10.6%); £3,729,743.09 -> £3,332,711.03 (10.6%); £3,729,743.32 -> £3,332,711.14 (10.6%); £3,729,743.55 -> £3,332,711.26 (10.6%); £3,729,743.77 -> £3,332,711.36 (10.6%); £3,729,744.00 -> £3,332,711.46 (10.6%); £3,729,744.23 -> £3,332,711.55 (10.6%); £3,729,744.46 -> £3,332,711.64 (10.6%); £3,729,744.68 -> £3,332,711.73 (10.6%); £3,729,744.91 -> £3,332,711.81 (10.6%); £3,729,745.13 -> £3,332,711.90 (10.6%); £3,729,745.35 -> £3,332,711.98 (10.6%); £3,729,745.58 -> £3,332,712.06 (10.6%); £3,729,745.81 -> £3,332,712.34 (10.6%); £3,729,746.04 -> £3,332,712.61 (10.6%); £3,729,746.27 -> £3,332,712.85 (10.6%); £3,729,746.50 -> £3,332,713.09 (10.6%); £3,729,746.73 -> £3,332,713.33 (10.6%); £3,729,746.96 -> £3,332,713.56 (10.6%); £3,729,747.18 -> £3,332,713.80 (10.6%); £3,729,747.41 -> £3,332,714.04 (10.6%); £3,729,747.64 -> £3,332,714.29 (10.6%); £3,729,747.86 -> £3,332,714.52 (10.6%); £3,729,748.08 -> £3,332,714.76 (10.6%); £3,729,748.31 -> £3,332,714.81 (10.6%); £3,729,748.54 -> £3,332,714.85 (10.6%); £3,729,748.75 -> £3,332,714.90 (10.6%); £3,729,748.94 -> £3,332,714.95 (10.6%); £3,729,749.11 -> £3,332,714.99 (10.6%); £3,729,749.25 -> £3,332,715.03 (10.6%); £3,729,749.39 -> £3,332,715.08 (10.6%); £3,729,749.53 -> £3,332,715.12 (10.6%); £3,729,749.67 -> £3,332,715.16 (10.6%); £3,729,749.82 -> £3,332,715.21 (10.6%); £3,729,749.95 -> £3,332,715.25 (10.6%); £3,729,750.09 -> £3,332,715.29 (10.6%); £3,729,750.24 -> £3,332,715.33 (10.6%); £3,729,750.38 -> £3,332,715.38 (10.6%); £3,729,750.52 -> £3,332,715.42 (10.6%); £3,729,750.66 -> £3,332,715.46 (10.6%); £3,729,750.81 -> £3,332,715.67 (10.6%); £3,729,750.95 -> £3,332,715.88 (10.6%); £3,729,751.10 -> £3,332,716.09 (10.6%); £3,729,751.27 -> £3,332,716.31 (10.6%); £3,729,751.46 -> £3,332,716.53 (10.6%); £3,729,751.66 -> £3,332,716.74 (10.6%); £3,729,751.88 -> £3,332,716.97 (10.6%); £3,729,752.10 -> £3,332,717.19 (10.6%); £3,729,752.34 -> £3,332,717.25 (10.6%); £3,729,752.58 -> £3,332,717.30 (10.6%); £3,729,752.81 -> £3,332,717.36 (10.6%); £3,729,753.04 -> £3,332,717.42 (10.6%); £3,729,753.27 -> £3,332,717.47 (10.6%); £3,729,753.50 -> £3,332,717.53 (10.6%); £3,729,753.74 -> £3,332,717.58 (10.6%); £3,729,753.97 -> £3,332,717.63 (10.6%); £3,729,754.20 -> £3,332,717.69 (10.6%); £3,729,754.43 -> £3,332,717.74 (10.6%); £3,729,754.67 -> £3,332,717.79 (10.6%); £3,729,754.89 -> £3,332,717.85 (10.6%); £3,729,755.12 -> £3,332,717.90 (10.6%); £3,729,755.36 -> £3,332,718.11 (10.6%); £3,729,755.59 -> £3,332,718.31 (10.6%); £3,729,755.83 -> £3,332,718.51 (10.6%); £3,729,756.06 -> £3,332,718.72 (10.6%); £3,729,756.29 -> £3,332,718.92 (10.6%); £3,729,756.52 -> £3,332,719.13 (10.6%); £3,729,756.75 -> £3,332,719.33 (10.6%); £3,729,757.00 -> £3,332,719.53 (10.6%); £3,729,757.24 -> £3,332,719.73 (10.6%); £3,729,757.47 -> £3,332,719.93 (10.6%); £3,729,757.71 -> £3,332,720.14 (10.6%); £3,729,757.94 -> £3,332,720.18 (10.6%); £3,729,758.17 -> £3,332,720.23 (10.6%); £3,729,758.40 -> £3,332,720.27 (10.6%); £3,729,758.60 -> £3,332,720.31 (10.6%); £3,729,758.78 -> £3,332,720.35 (10.6%); £3,729,758.94 -> £3,332,720.39 (10.6%); £3,729,759.10 -> £3,332,720.43 (10.6%); £3,729,759.26 -> £3,332,720.48 (10.6%); £3,729,759.42 -> £3,332,720.52 (10.6%); £3,729,759.59 -> £3,332,720.56 (10.6%); £3,729,759.74 -> £3,332,720.60 (10.6%); £3,729,759.91 -> £3,332,720.64 (10.6%); £3,729,760.07 -> £3,332,720.69 (10.6%); £3,729,760.23 -> £3,332,720.73 (10.6%); £3,729,760.40 -> £3,332,720.77 (10.6%); £3,729,760.55 -> £3,332,720.82 (10.6%); £3,729,760.72 -> £3,332,721.03 (10.6%); £3,729,760.88 -> £3,332,721.24 (10.6%); £3,729,761.05 -> £3,332,721.47 (10.6%); £3,729,761.26 -> £3,332,721.72 (10.6%); £3,729,761.47 -> £3,332,721.99 (10.6%); £3,729,761.70 -> £3,332,722.29 (10.6%); £3,729,761.95 -> £3,332,722.62 (10.6%); £3,729,762.23 -> £3,332,722.97 (10.6%); £3,729,762.50 -> £3,332,723.12 (10.6%); £3,729,762.78 -> £3,332,723.27 (10.6%); £3,729,763.05 -> £3,332,723.42 (10.6%); £3,729,763.32 -> £3,332,723.58 (10.6%); £3,729,763.59 -> £3,332,723.73 (10.6%); £3,729,763.86 -> £3,332,723.88 (10.6%); £3,729,764.13 -> £3,332,724.02 (10.6%); £3,729,764.39 -> £3,332,724.16 (10.6%); £3,729,764.67 -> £3,332,724.30 (10.6%); £3,729,764.94 -> £3,332,724.44 (10.6%); £3,729,765.21 -> £3,332,724.58 (10.6%); £3,729,765.49 -> £3,332,724.72 (10.6%); £3,729,765.76 -> £3,332,724.84 (10.6%); £3,729,766.03 -> £3,332,725.15 (10.6%); £3,729,766.29 -> £3,332,725.44 (10.6%); £3,729,766.57 -> £3,332,725.70 (10.6%); £3,729,766.83 -> £3,332,725.93 (10.6%); £3,729,767.09 -> £3,332,726.15 (10.6%); £3,729,767.35 -> £3,332,726.38 (10.6%); £3,729,767.62 -> £3,332,726.60 (10.6%); £3,729,767.89 -> £3,332,726.81 (10.6%); £3,729,768.16 -> £3,332,727.02 (10.6%); £3,729,768.42 -> £3,332,727.23 (10.6%); £3,729,768.69 -> £3,332,727.43 (10.6%); £3,729,768.95 -> £3,332,727.48 (10.6%); £3,729,769.23 -> £3,332,727.52 (10.6%); £3,729,769.46 -> £3,332,727.57 (10.6%); £3,729,769.69 -> £3,332,727.61 (10.6%); £3,729,769.90 -> £3,332,727.65 (10.6%); £3,729,770.06 -> £3,332,727.69 (10.6%); £3,729,770.22 -> £3,332,727.73 (10.6%); £3,729,770.39 -> £3,332,727.78 (10.6%); £3,729,770.56 -> £3,332,727.82 (10.6%); £3,729,770.72 -> £3,332,727.86 (10.6%); £3,729,770.88 -> £3,332,727.90 (10.6%); £3,729,771.04 -> £3,332,727.94 (10.6%); £3,729,771.21 -> £3,332,727.98 (10.6%); £3,729,771.37 -> £3,332,728.03 (10.6%); £3,729,771.53 -> £3,332,728.07 (10.6%); £3,729,771.69 -> £3,332,728.12 (10.6%); £3,729,771.85 -> £3,332,728.29 (10.6%); £3,729,772.02 -> £3,332,728.47 (10.6%); £3,729,772.19 -> £3,332,728.67 (10.6%); £3,729,772.40 -> £3,332,728.89 (10.6%); £3,729,772.61 -> £3,332,729.13 (10.6%); £3,729,772.85 -> £3,332,729.40 (10.6%); £3,729,773.10 -> £3,332,729.70 (10.6%); £3,729,773.37 -> £3,332,730.01 (10.6%); £3,729,773.64 -> £3,332,730.16 (10.6%); £3,729,773.92 -> £3,332,730.32 (10.6%); £3,729,774.19 -> £3,332,730.48 (10.6%); £3,729,774.44 -> £3,332,730.63 (10.6%); £3,729,774.71 -> £3,332,730.78 (10.6%); £3,729,774.98 -> £3,332,730.93 (10.6%); £3,729,775.24 -> £3,332,731.07 (10.6%); £3,729,775.51 -> £3,332,731.21 (10.6%); £3,729,775.77 -> £3,332,731.35 (10.6%); £3,729,776.04 -> £3,332,731.49 (10.6%); £3,729,776.31 -> £3,332,731.62 (10.6%); £3,729,776.59 -> £3,332,731.75 (10.6%); £3,729,776.86 -> £3,332,731.88 (10.6%); £3,729,777.13 -> £3,332,732.18 (10.6%); £3,729,777.39 -> £3,332,732.45 (10.6%); £3,729,777.67 -> £3,332,732.68 (10.6%); £3,729,777.93 -> £3,332,732.89 (10.6%); £3,729,778.20 -> £3,332,733.09 (10.6%); £3,729,778.47 -> £3,332,733.29 (10.6%); £3,729,778.73 -> £3,332,733.48 (10.6%); £3,729,778.99 -> £3,332,733.67 (10.6%); £3,729,779.26 -> £3,332,733.86 (10.6%); £3,729,779.53 -> £3,332,734.05 (10.6%); £3,729,779.81 -> £3,332,734.23 (10.6%); £3,729,780.08 -> £3,332,734.27 (10.6%); £3,729,780.35 -> £3,332,734.32 (10.6%); £3,729,780.59 -> £3,332,734.37 (10.6%); £3,729,780.82 -> £3,332,734.41 (10.6%); £3,729,781.04 -> £3,332,734.45 (10.6%); £3,729,781.20 -> £3,332,734.49 (10.6%); £3,729,781.36 -> £3,332,734.53 (10.6%); £3,729,781.52 -> £3,332,734.58 (10.6%); £3,729,781.68 -> £3,332,734.62 (10.6%); £3,729,781.83 -> £3,332,734.66 (10.6%); £3,729,782.00 -> £3,332,734.70 (10.6%); £3,729,782.15 -> £3,332,734.75 (10.6%); £3,729,782.31 -> £3,332,734.79 (10.6%); £3,729,782.47 -> £3,332,734.84 (10.6%); £3,729,782.63 -> £3,332,734.88 (10.6%); £3,729,782.79 -> £3,332,734.92 (10.6%); £3,729,782.94 -> £3,332,735.13 (10.6%); £3,729,783.10 -> £3,332,735.35 (10.6%); £3,729,783.28 -> £3,332,735.58 (10.6%); £3,729,783.48 -> £3,332,735.83 (10.6%); £3,729,783.70 -> £3,332,736.10 (10.6%); £3,729,783.93 -> £3,332,736.39 (10.6%); £3,729,784.18 -> £3,332,736.71 (10.6%); £3,729,784.45 -> £3,332,737.05 (10.6%); £3,729,784.72 -> £3,332,737.20 (10.6%); £3,729,784.99 -> £3,332,737.35 (10.6%); £3,729,785.26 -> £3,332,737.50 (10.6%); £3,729,785.52 -> £3,332,737.65 (10.6%); £3,729,785.79 -> £3,332,737.80 (10.6%); £3,729,786.07 -> £3,332,737.94 (10.6%); £3,729,786.34 -> £3,332,738.08 (10.6%); £3,729,786.61 -> £3,332,738.22 (10.6%); £3,729,786.89 -> £3,332,738.36 (10.6%); £3,729,787.16 -> £3,332,738.51 (10.6%); £3,729,787.42 -> £3,332,738.66 (10.6%); £3,729,787.69 -> £3,332,738.80 (10.6%); £3,729,787.96 -> £3,332,738.93 (10.6%); £3,729,788.23 -> £3,332,739.26 (10.6%); £3,729,788.50 -> £3,332,739.58 (10.6%); £3,729,788.77 -> £3,332,739.86 (10.6%); £3,729,789.04 -> £3,332,740.11 (10.6%); £3,729,789.31 -> £3,332,740.34 (10.6%); £3,729,789.58 -> £3,332,740.57 (10.6%); £3,729,789.85 -> £3,332,740.79 (10.6%); £3,729,790.12 -> £3,332,741.01 (10.6%); £3,729,790.38 -> £3,332,741.22 (10.6%); £3,729,790.65 -> £3,332,741.43 (10.6%); £3,729,790.92 -> £3,332,741.64 (10.6%); £3,729,791.19 -> £3,332,741.68 (10.6%); £3,729,791.47 -> £3,332,741.73 (10.6%); £3,729,791.72 -> £3,332,741.77 (10.6%); £3,729,791.94 -> £3,332,741.82 (10.6%); £3,729,792.15 -> £3,332,741.86 (10.6%); £3,729,792.31 -> £3,332,741.90 (10.6%); £3,729,792.48 -> £3,332,741.94 (10.6%); £3,729,792.64 -> £3,332,741.98 (10.6%); £3,729,792.80 -> £3,332,742.02 (10.6%); £3,729,792.96 -> £3,332,742.07 (10.6%); £3,729,793.12 -> £3,332,742.11 (10.6%); £3,729,793.28 -> £3,332,742.15 (10.6%); £3,729,793.44 -> £3,332,742.20 (10.6%); £3,729,793.60 -> £3,332,742.24 (10.6%); £3,729,793.76 -> £3,332,742.28 (10.6%); £3,729,793.92 -> £3,332,742.33 (10.6%); £3,729,794.08 -> £3,332,742.55 (10.6%); £3,729,794.24 -> £3,332,742.77 (10.6%); £3,729,794.43 -> £3,332,743.01 (10.6%); £3,729,794.63 -> £3,332,743.24 (10.6%); £3,729,794.85 -> £3,332,743.51 (10.6%); £3,729,795.08 -> £3,332,743.81 (10.6%); £3,729,795.33 -> £3,332,744.13 (10.6%); £3,729,795.61 -> £3,332,744.46 (10.6%); £3,729,795.88 -> £3,332,744.60 (10.6%); £3,729,796.15 -> £3,332,744.75 (10.6%); £3,729,796.41 -> £3,332,744.90 (10.6%); £3,729,796.69 -> £3,332,745.05 (10.6%); £3,729,796.96 -> £3,332,745.20 (10.6%); £3,729,797.23 -> £3,332,745.34 (10.6%); £3,729,797.50 -> £3,332,745.48 (10.6%); £3,729,797.78 -> £3,332,745.62 (10.6%); £3,729,798.06 -> £3,332,745.75 (10.6%); £3,729,798.32 -> £3,332,745.90 (10.6%); £3,729,798.59 -> £3,332,746.03 (10.6%); £3,729,798.87 -> £3,332,746.16 (10.6%); £3,729,799.14 -> £3,332,746.29 (10.6%); £3,729,799.42 -> £3,332,746.61 (10.6%); £3,729,799.69 -> £3,332,746.91 (10.6%); £3,729,799.96 -> £3,332,747.17 (10.6%); £3,729,800.23 -> £3,332,747.40 (10.6%); £3,729,800.49 -> £3,332,747.63 (10.6%); £3,729,800.77 -> £3,332,747.85 (10.6%); £3,729,801.05 -> £3,332,748.07 (10.6%); £3,729,801.33 -> £3,332,748.28 (10.6%); £3,729,801.60 -> £3,332,748.49 (10.6%); £3,729,801.88 -> £3,332,748.69 (10.6%); £3,729,802.14 -> £3,332,748.89 (10.6%); £3,729,802.42 -> £3,332,748.94 (10.6%); £3,729,802.69 -> £3,332,748.98 (10.6%); £3,729,802.95 -> £3,332,749.03 (10.6%); £3,729,803.19 -> £3,332,749.07 (10.6%); £3,729,803.40 -> £3,332,749.11 (10.6%); £3,729,803.56 -> £3,332,749.15 (10.6%); £3,729,803.72 -> £3,332,749.19 (10.6%); £3,729,803.88 -> £3,332,749.23 (10.6%); £3,729,804.05 -> £3,332,749.28 (10.6%); £3,729,804.21 -> £3,332,749.32 (10.6%); £3,729,804.37 -> £3,332,749.36 (10.6%); £3,729,804.54 -> £3,332,749.40 (10.6%); £3,729,804.70 -> £3,332,749.44 (10.6%); £3,729,804.86 -> £3,332,749.49 (10.6%); £3,729,805.02 -> £3,332,749.53 (10.6%); £3,729,805.19 -> £3,332,749.57 (10.6%); £3,729,805.35 -> £3,332,749.76 (10.6%); £3,729,805.51 -> £3,332,749.95 (10.6%); £3,729,805.69 -> £3,332,750.16 (10.6%); £3,729,805.88 -> £3,332,750.38 (10.6%); £3,729,806.10 -> £3,332,750.63 (10.6%); £3,729,806.33 -> £3,332,750.90 (10.6%); £3,729,806.58 -> £3,332,751.20 (10.6%); £3,729,806.84 -> £3,332,751.52 (10.6%); £3,729,807.12 -> £3,332,751.67 (10.6%); £3,729,807.38 -> £3,332,751.82 (10.6%); £3,729,807.65 -> £3,332,751.97 (10.6%); £3,729,807.93 -> £3,332,752.13 (10.6%); £3,729,808.19 -> £3,332,752.28 (10.6%); £3,729,808.47 -> £3,332,752.43 (10.6%); £3,729,808.75 -> £3,332,752.56 (10.6%); £3,729,809.02 -> £3,332,752.70 (10.6%); £3,729,809.29 -> £3,332,752.84 (10.6%); £3,729,809.56 -> £3,332,752.98 (10.6%); £3,729,809.83 -> £3,332,753.11 (10.6%); £3,729,810.09 -> £3,332,753.24 (10.6%); £3,729,810.36 -> £3,332,753.36 (10.6%); £3,729,810.63 -> £3,332,753.67 (10.6%); £3,729,810.90 -> £3,332,753.95 (10.6%); £3,729,811.17 -> £3,332,754.20 (10.6%); £3,729,811.44 -> £3,332,754.42 (10.6%); £3,729,811.72 -> £3,332,754.63 (10.6%); £3,729,811.98 -> £3,332,754.84 (10.6%); £3,729,812.26 -> £3,332,755.05 (10.6%); £3,729,812.52 -> £3,332,755.26 (10.6%); £3,729,812.79 -> £3,332,755.46 (10.6%); £3,729,813.08 -> £3,332,755.66 (10.6%); £3,729,813.35 -> £3,332,755.85 (10.6%); £3,729,813.62 -> £3,332,755.89 (10.6%); £3,729,813.88 -> £3,332,755.94 (10.6%); £3,729,814.14 -> £3,332,755.98 (10.6%); £3,729,814.37 -> £3,332,756.03 (10.6%)
- Bills issued: 117, average clarity 0.821, average bill shock 15.1%, bad debt provision £11,426.70, avg complaint probability 4.5%
- Solvency signal: £414,749/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £195,333.18 vs. naked (unhedged) net margin: £599,235.42
- hedging cost £403,902.24 vs. a fully unhedged book (commodity-only: actual net £195,333.18 vs. naked net £599,235.42)
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £226.83 vs. naked £1,335.58 -- hedging cost £1,108.75
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £14,911.38 vs. naked £115,656.21 -- hedging cost £100,744.82
  - C_IC3g: actual £3,837.46 vs. naked £56,934.03 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £102,722.50 -- hedging cost £101,286.98

**Year narrative:** 2024 produced a net gain of £357,551.17 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 26 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £112,263.68 (gross £513,682.89, capital £5,565.63)
  - Electricity: gross £460,174.11, capital £5,565.63, net £108,476.16
  - Gas: gross £53,508.78, capital £0.00, net £3,787.52
- Treasury at year end: £3,782,418.37
- Hedge fraction at first renewal this year (avg across year's terms): C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2025-01-08 period 31, net margin £-81.23

**Customer Book**

- Active accounts: 8 (C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 3, SME electricity: 0, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 1 accounts
- Average CLV (Point-in-Time, year-end 2025): £246,117.21
  - By billing account: C1 £2,037.52, C2 £2,528.22, C3 £2,673.14, C4 £1,573.85, C5 £4,332.79, C6 £9,325.67, C7 £3,498.45, C8 £4,422.66, C9 £4,052.96, C_IC1 £774,735.50, C_IC2 £417,984.43, C_IC3 £1,241,910.05, C_IC4 £730,448.49
- Bill shock events (>=20%): 16 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (29%); C8 2025-02-28 (24%); C8 2025-04-30 (38%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%)
- Churn risk (accounts renewing in 2025): 2 at risk (≥20% churn prob): C8 38%, C9 38%

**Pricing & Margin**

- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-23.72 -- **net-negative**
- C8 (electricity): tariff £149.29-£298.58/MWh, net margin £41.22
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £195.49
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £62,405.83
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,516.09
- C_IC3 (electricity): tariff £86.86-£165.83/MWh, net margin £14,923.83
- C_IC3g (gas): tariff £54.85/MWh, net margin £3,787.52
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £1,417.43

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 48, average clarity 0.782, average bill shock 23.1%, bad debt provision £4,917.81, avg complaint probability 5.8%
- Solvency signal: £540,345/customer (7 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-30.08 vs. naked (unhedged) net margin: £118.90
- hedging cost £148.98 vs. a fully unhedged book (commodity-only: actual net £-30.08 vs. naked net £118.90)
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £112,263.68 across 8 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 16 customer(s) experienced a bill shock of >=20%.
