# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,903,142.73
  (£1,436,506.51 net change)
- Solvency signal (final year): £425,490/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £22,567,290.38
  VAT remitted to HMRC: (£3,739,961.91) | Revenue (ex-VAT): £18,827,328.47
  Non-commodity pass-through: (£4,782,814.97)
- Gross margin: £6,447,283.33
- Capital costs: £51,210.26
- Net margin: £6,396,073.07
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1550, average clarity 0.812,
  service quality score 0.903
- Enterprise value (CLV sum across 15 billing accounts): £8,220,970.68
- Cost to serve (whole portfolio): £18,726.90, net margin after cost to serve: £6,377,346.17
- Hedge effectiveness (whole window): hedging cost £4,223,726.70 vs. a fully unhedged book (commodity-only: actual net £1,436,506.51 vs. naked net £5,660,233.21)

- **2021** (crisis year): net margin £75,439.68, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £339,300.82, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2247, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 327.8x (net £64,798.54 on £197.67 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 4/6 departures (67%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 3.3%, max 15.6% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +33.1% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 34.0% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,447,283.33, capital £51,210.26, net £6,396,073.07. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £75,439.68 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,396,073.07
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,660,233.21
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,223,726.70 vs. a fully unhedged book (commodity-only: actual net £1,436,506.51 vs. naked net £5,660,233.21)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,383.31 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £612,920.70 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £-134.52 | £553.23 | £324.29 | £743.01 |
| 2017 | £30,139.92 | £0.00 | £361.26 | £622.10 | £516.54 | £31,639.82 |
| 2018 | £101,162.40 | £0.00 | £-187.39 | £346.75 | £436.94 | £101,758.70 |
| 2019 | £222,407.66 | £9,999.92 | £-218.60 | £812.55 | £489.73 | £233,491.26 |
| 2020 | £116,592.08 | £10,030.76 | £439.74 | £1,050.07 | £457.36 | £128,570.01 |
| 2021 | £64,766.65 | £9,999.92 | £592.73 | £257.10 | £-176.72 | £75,439.68 |
| 2022 | £330,715.51 | £9,999.92 | £1,061.61 | £-1,320.00 | £-1,156.22 | £339,300.82 |
| 2023 | £135,215.42 | £9,999.92 | £1,423.56 | £648.56 | £-1,040.96 | £146,246.51 |
| 2024 | £334,098.60 | £10,030.76 | £516.59 | £3,251.67 | £436.59 | £348,334.21 |
| 2025 | £115,818.30 | £4,449.79 | £0.00 | £724.65 | £0.00 | £120,992.73 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **52** renewals.  Lost (churned): **6** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9462 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.0500 | 0.3500 | 0.9223 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9462 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.1100 | 0.5500 | 0.9113 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.1100 | 0.3500 | 0.8718 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.1100 | 0.5500 | 0.9113 | 0.8255 |
| C_IC1 | 2018-01-31 | renewed | 0.0500 | 0.5500 | 0.9691 | 0.3902 |
| C1 | 2018-12-31 | renewed | 0.1100 | 0.5500 | 0.9113 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.1100 | 0.3500 | 0.9051 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.2000 | 0.5500 | 0.8387 | 0.6312 |
| C_IC2 | 2019-01-31 | renewed | 0.0500 | 0.5500 | 0.9715 | 0.3710 |
| C1 | 2019-12-31 | renewed | 0.2900 | 0.5500 | 0.7873 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3500 | 0.3500 | 0.8370 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.2900 | 0.5500 | 0.8370 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.0800 | 0.5500 | 0.9531 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.1100 | 0.3500 | 0.9068 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.2300 | 0.5500 | 0.8651 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9355 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.2300 | 0.5500 | 0.8651 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.4100 | 0.5500 | 0.8696 | 0.2845 |
| C1 | 2020-12-30 | churned **CHURNED** | 0.3800 | 0.5500 | 0.7771 | 0.8047 |
| C5 | 2020-12-30 | churned **CHURNED** | 0.3200 | 0.3500 | 0.7288 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.2000 | 0.5500 | 0.8827 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.2000 | 0.5500 | 0.8827 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.0800 | 0.5500 | 0.9707 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.0800 | 0.3500 | 0.9576 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.1100 | 0.5500 | 0.9597 | 0.4564 |
| C1_2 | 2021-12-30 | renewed | 0.0500 | 0.5500 | 0.9833 | 0.2977 |
| C7 | 2021-12-30 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.3200 | 0.5500 | 0.9402 | 0.5838 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.3800 | 0.5500 | 0.9511 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3500 | 0.3500 | 0.9511 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.2600 | 0.5500 | 0.9511 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3500 | 0.5500 | 0.9364 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.3800 | 0.5500 | 0.9364 | 0.8552 |
| C1_2 | 2022-12-30 | renewed | 0.4100 | 0.5500 | 0.9556 | 0.9433 |
| C7 | 2022-12-30 | renewed | 0.2900 | 0.5500 | 0.9364 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.4100 | 0.5500 | 0.9511 | 0.8723 |
| C2_2 | 2023-03-31 | renewed | 0.0500 | 0.5500 | 0.9802 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.4100 | 0.3500 | 0.8084 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.9251 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.7674 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.4100 | 0.5500 | 0.8739 | 0.6095 |
| C1_2 | 2023-12-30 | renewed | 0.1700 | 0.5500 | 0.9326 | 0.5453 |
| C7 | 2023-12-30 | renewed | 0.4100 | 0.5500 | 0.9026 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.4100 | 0.5500 | 0.9030 | 0.7019 |
| C2_2 | 2024-03-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.2600 | 0.3500 | 0.8141 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.1700 | 0.5500 | 0.9350 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.1700 | 0.5500 | 0.8906 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.3800 | 0.5500 | 0.8570 | 0.9018 |
| C1_2 | 2024-12-29 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.1722 |
| C7 | 2024-12-29 | renewed | 0.2900 | 0.5500 | 0.8895 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.4100 | 0.5500 | 0.7971 | 0.3751 |
| C2_2 | 2025-03-30 | renewed | 0.3200 | 0.5500 | 0.8889 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3200 | 0.5500 | 0.9056 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 140.6%
- **Average signed error:** +115.5% (over-estimates vs SIM)
- **Renewal events with estimates:** 58

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +113.9% | 113.9% |
| 2017 | 3 | -4.9% | 12.9% |
| 2018 | 4 | +646.2% | 646.2% |
| 2019 | 4 | +602.3% | 642.0% |
| 2020 | 10 | -11.1% | 56.6% |
| 2021 | 8 | +123.5% | 140.5% |
| 2022 | 8 | +2.0% | 11.1% |
| 2023 | 8 | +36.4% | 61.3% |
| 2024 | 8 | +20.2% | 38.4% |
| 2025 | 2 | +15.0% | 22.9% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 58
- **Active renewers:** 20 (34%) — mean company estimate 23.9%, abs error 307.0%
- **Passive SVT-rollers:** 38 (66%) — mean company estimate 9.9%, abs error 53.0%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 13.3% | 0.0% | 113.9% |
| 2017 | 0 | 3 | 0.0% | 9.4% | 0.0% | 12.9% |
| 2018 | 3 | 1 | 53.9% | 13.8% | 843.3% | 55.1% |
| 2019 | 2 | 2 | 53.2% | 13.6% | 1267.4% | 16.7% |
| 2020 | 6 | 4 | 11.5% | 6.9% | 65.9% | 42.7% |
| 2021 | 1 | 7 | 12.7% | 12.4% | 73.3% | 150.1% |
| 2022 | 0 | 8 | 0.0% | 5.5% | 0.0% | 11.1% |
| 2023 | 3 | 5 | 19.0% | 9.6% | 120.2% | 26.0% |
| 2024 | 5 | 3 | 14.2% | 13.0% | 49.4% | 20.2% |
| 2025 | 0 | 2 | 0.0% | 11.6% | 0.0% | 22.9% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 38
- **Above SVT (at-risk):** 11 (29%)
- **Below/at SVT (protected):** 27 (71%)
- **Mean rate vs SVT premium:** -7.0%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.1 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 119.9 | 140.0 |
| 2018 | 1 | 0 (0%) | -1.9% | 149.7 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 4 | 0 (0%) | -27.2% | 129.7 | 178.1 |
| 2021 | 7 | 5 (71%) | +14.6% | 216.6 | 187.2 |
| 2022 | 8 | 4 (50%) | +4.3% | 292.3 | 343.4 |
| 2023 | 5 | 0 (0%) | -29.2% | 229.8 | 358.6 |
| 2024 | 3 | 1 (33%) | -6.7% | 222.1 | 237.9 |
| 2025 | 2 | 1 (50%) | -3.6% | 239.8 | 248.6 |

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
| 2020 | 22 | 12.4% | 33.8% |
| 2021 | 16 | 15.4% | 44.5% |
| 2022 | 16 | 11.1% | 23.2% |
| 2023 | 15 | 21.3% | 40.0% |
| 2024 | 14 | 10.3% | 22.6% |
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
| 2016 | 3 | 1.14× | 1.23× |
| 2017 | 3 | 0.13× | 0.27× |
| 2018 | 4 | 6.46× ⚠ | 22.57× |
| 2019 | 4 | 6.42× ⚠ | 24.89× |
| 2020 | 10 | 0.57× | 1.47× |
| 2021 | 8 | 1.40× | 5.64× |
| 2022 | 8 | 0.11× | 0.28× |
| 2023 | 8 | 0.61× | 2.58× |
| 2024 | 8 | 0.38× | 1.15× |
| 2025 | 2 | 0.23× | 0.38× |

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
| 2021 | 10 | 0.96% | 4.24% | Low — stable portfolio |
| 2022 | 10 | 2.43% | 7.47% | MODERATE — asset adoption visible |
| 2023 | 10 | 2.58% | 8.47% | HIGH drift — EV/asset cohort growing |
| 2024 | 10 | 3.31% | 15.56% | HIGH drift — EV/asset cohort growing |
| 2025 | 2 | 1.42% | 2.07% | MODERATE — asset adoption visible |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **3.31%** mean / **15.56%** max in 2024. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
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
| 2021 | 10 | 1.0% | 4.2% |
| 2022 | 10 | 2.4% | 7.5% |
| 2023 | 10 | 2.6% | 8.5% |
| 2024 | 10 | 3.3% | 15.6% |
| 2025 | 2 | 1.4% | 2.1% |

**88** of **88** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## EAC Drift Snapshot (Phase AI)

Per-customer consumption drift from company billing history (first renewal → latest renewal).
Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.

**1 significant** (≥15%) | **2 moderate** (5–15%) | **11 stable** (<5%)

| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |
|----------|-------------|-------------|-------|--------------|
| C4 | 4,131 | 3,365 | -19% | likely solar installation or significant efficiency upgrade |
| C1_2 | 10,401 | 9,227 | -11% | efficiency improvement or reduced occupancy |
| C7 | 13,179 | 12,155 | -8% | efficiency improvement or reduced occupancy |

**Portfolio demand trend:** 3 customers increasing / 10 decreasing (mean drift: -3.3%)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **8** (6 churn, 2 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.06, company est=0.08 |
| 2020-12-30 | CHURN | C1 | SIM p=0.22, company est=0.07 |
| 2020-12-30 | CHURN | C5 | SIM p=0.27, company est=0.09 |
| 2020-12-30 | ACQUISITION | C1_2 | home-move-win (predecessor: C1) |
| 2022-03-31 | CHURN | C2 | SIM p=0.05, company est=0.06 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.19, company est=0.25 |
| 2024-09-29 | CHURN | C4 | SIM p=0.14, company est=0.14 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 3 accounts | 1 active | yes |
| 2021-12-31 | 3 accounts | 1 active | yes |
| 2022-12-31 | 4 accounts | 2 active | yes |
| 2023-12-31 | 4 accounts | 2 active | yes |
| 2024-12-31 | 6 accounts | 2 active | yes |
| 2025-12-31 | 6 accounts | 2 active | yes |

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
| 2020 | 238,634 | 35,391 | 69,453 | 56,549 | 70,023 | 0 | 470,050 |  |
| 2021 | 246,246 | 14,982 | 71,203 | 49,580 | 62,717 | 41,350 | 486,078 |  |
| 2022 | 256,213 | -49,739 | 70,920 | 36,681 | 69,110 | 99,478 | 482,663 | ⬇ CfD REBATE |
| 2023 | 271,884 | 64,773 | 71,702 | 50,966 | 75,106 | 13,752 | 548,182 |  |
| 2024 | 307,626 | 109,934 | 72,815 | 68,707 | 82,563 | 1,999 | 643,645 |  |
| 2025 | 135,727 | 46,950 | 31,156 | 31,029 | 36,151 | 854 | 281,867 |  |
| **Total** | **1,724,786** | **263,232** | **458,497** | **336,846** | **467,502** | **157,432** | **3,408,295** | |

Total policy cost: £3,408,295 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2020 | 124,580 |  |
| 2021 | 122,860 |  |
| 2022 | 133,531 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 139,555 | RIIO-ED2 from Apr 2023 |
| 2024 | 143,473 |  |
| 2025 | 61,363 |  |
| **Total** | **881,683** | |

Total network cost: £881,683 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

## Gas Policy Costs and Network Charges (Phase 30b)

Gas CCL: non-domestic only (domestic gas exempt). Gas network (GDN + NTS): all on unit rate.
GGL (Green Gas Levy): per-meter, from Nov 2021; tiny in £/MWh terms.

| Year | Gas Policy (CCL + GGL) £ | Gas Network £ | Total Gas Non-Commodity £ |
|------|--------------------------|---------------|--------------------------|
| 2016 | 0 | 479 | 479 |
| 2017 | 0 | 898 | 898 |
| 2018 | 0 | 905 | 905 |
| 2019 | 15,155 | 50,388 | 65,543 |
| 2020 | 19,468 | 47,213 | 66,681 |
| 2021 | 22,472 | 50,301 | 72,773 |
| 2022 | 27,045 | 54,433 | 81,478 |
| 2023 | 32,229 | 79,700 | 111,929 |
| 2024 | 37,494 | 76,429 | 113,923 |
| 2025 | 17,243 | 31,816 | 49,059 |
| **Total** | **171,106** | **392,562** | **563,668** |

Gas policy pass-through in tariff unit rate (CCL + GGL at term start); gas network pass-through likewise. Net basis risk near-zero for annual contracts.


## Gas Book P&L — Year by Year (Phase 32a)

Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.
Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.

| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |
|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|
| 2016 | 1,388 | 578 | 811 | 0 | 479 | 7 | 324 | +23.4% |
| 2017 | 2,660 | 1,231 | 1,430 | 0 | 898 | 15 | 517 | +19.4% |
| 2018 | 3,114 | 1,751 | 1,363 | 0 | 905 | 21 | 437 | +14.0% |
| 2019 | 137,766 | 61,712 | 76,054 | 15,155 | 50,388 | 21 | 10,490 | +7.6% |
| 2020 | 121,120 | 43,940 | 77,180 | 19,468 | 47,213 | 10 | 10,488 | +8.7% |
| 2021 | 297,399 | 214,790 | 82,609 | 22,472 | 50,301 | 13 | 9,823 | +3.3% |
| 2022 | 588,330 | 497,974 | 90,356 | 27,045 | 54,433 | 34 | 8,844 | +1.5% |
| 2023 | 297,198 | 176,258 | 120,940 | 32,229 | 79,700 | 52 | 8,959 | +3.0% |
| 2024 | 270,491 | 146,077 | 124,414 | 37,494 | 76,429 | 23 | 10,467 | +3.9% |
| 2025 | 132,454 | 78,945 | 53,509 | 17,243 | 31,816 | 0 | 4,450 | +3.4% |
| **Total** | **1,851,920** | **1,223,256** | **628,664** | **171,106** | **392,562** | **198** | **64,799** | **+3.5%** |

Gas book net margin positive over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,434 | 9 | 274,159 | 2108.92× | OK |
| 2017 | 2,498,375 | 10 | 249,838 | 1921.83× | OK |
| 2018 | 2,487,547 | 11 | 226,141 | 1739.54× | OK |
| 2019 | 2,611,522 | 12 | 217,627 | 1674.05× | OK |
| 2020 | 2,923,397 | 14 | 208,814 | 1606.26× | OK |
| 2021 | 2,956,667 | 11 | 268,788 | 2067.60× | OK |
| 2022 | 3,161,597 | 12 | 263,466 | 2026.66× | OK |
| 2023 | 3,382,344 | 11 | 307,486 | 2365.28× | OK |
| 2024 | 3,777,722 | 11 | 343,429 | 2641.76× | OK |
| 2025 | 3,829,410 | 9 | 425,490 | 3273.00× | OK |

End-state (2025): **£425,490/account** across 9 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,434 | 81947.3× | OK |
| 2017 | 466 | 559 | 2,498,375 | 4468.9× | OK |
| 2018 | 849 | 1,019 | 2,487,547 | 2440.9× | OK |
| 2019 | 1,543 | 1,851 | 2,611,522 | 1410.8× | OK |
| 2020 | 1,979 | 2,375 | 2,923,397 | 1231.0× | OK |
| 2021 | 4,332 | 5,198 | 2,956,667 | 568.8× | OK |
| 2022 | 8,502 | 10,203 | 3,161,597 | 309.9× | OK |
| 2023 | 5,613 | 6,736 | 3,382,344 | 502.1× | OK |
| 2024 | 2,659 | 3,191 | 3,777,722 | 1184.0× | OK |
| 2025 | 3,881 | 4,657 | 3,829,410 | 822.2× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,494.85 | £12,231.90 | £261.93/MWh | £144.60/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,984.93 | £9,701.94 | £272.71/MWh | £154.55/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,933.13 | £9,310.55 | £250.25/MWh | £141.72/MWh | +10.9% |

Total HH revenue: £63,657.30 vs flat equivalent £58,753.02 (+8.3% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 31 | 100% | C8 (2016-10-31) |
| 2017 | 50 | 81% | C8 (2017-11-30) |
| 2018 | 60 | 85% | C4g (2018-10-31) |
| 2019 | 66 | 130% | C_IC1 (2019-03-31) |
| 2020 | 52 | 118% | C_IC2 (2020-03-31) |
| 2021 | 47 | 1207% | C1_2 (2021-01-31) |
| 2022 | 71 | 1735% | C2_2 (2022-04-30) |
| 2023 | 48 | 101% | C_IC2 (2023-06-30) |
| 2024 | 40 | 107% | C_IC2 (2024-07-31) |
| 2025 | 23 | 80% | C1_2 (2025-06-07) |

Total: **488** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1735% | no |
| 2021-01-31 | C1_2 | +1207% | no |
| 2022-01-31 | C1_2 | +141% | no |
| 2022-10-31 | C4g | +134% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2020-03-31 | C_IC2 | +118% | no |
| 2021-10-31 | C4g | +113% | no |
| 2022-01-31 | C_IC3 | +109% | no |
| 2024-07-31 | C_IC2 | +107% | no |
| 2023-06-30 | C_IC2 | +101% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 11% | 11% | 0 |
| 2017 | 4 | 16% | 23% | 2 ⚠ |
| 2018 | 4 | 17% | 23% | 2 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 4 | 5% | 21% | 1 ⚠ |
| 2021 | 3 | 69% | 95% | 3 ⚠ |
| 2022 | 2 | 46% | 92% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 1 | 1% | 1% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £19.4 | £125.9 (+550%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 92% |
| 2021-09-30 | C4g | £16.1 | £35.0 (+118%) | 74% |
| 2021-03-31 | C2g | £21.7 | £35.0 (+62%) | 40% |
| 2018-10-01 | C4g | £26.1 | £33.6 (+29%) | 23% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 12 |
| Retained | 12 (100%) |
| Churned despite offer | 0 |
| Total offer cost (foregone margin) | £150,055.87 |
| Margin saved (retained customers' terms) | £1,209,365.23 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£1,059,309.35** |
| Acquisition cost avoided (retained customers) | £2,300.00 |
| **Full economic ROI (margin + acq savings)** | **£1,061,609.35** |

Missed opportunities (churns with no offer): **6** (£6,209.20 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 6 (£6,209.20 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 2 | 2 | £71.20 | £1362.45 | £1291.25 | £0.00 |
| 2018 | 2 | 2 | £24311.83 | £165243.09 | £140931.26 | £0.00 |
| 2019 | 2 | 2 | £32311.18 | £296612.44 | £264301.26 | £0.00 |
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £2642.54 |
| 2021 | 3 | 3 | £65571.90 | £415060.97 | £349489.07 | £0.00 |
| 2022 | 2 | 2 | £27559.81 | £327848.12 | £300288.31 | £236.63 |
| 2023 | 1 | 1 | £229.96 | £3238.16 | £3008.20 | £0.00 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £3330.03 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2017-04-01 | C8 | 0.34 | 3% | £46.02 | £867.92 | £150 | £821.90 | retained |
| 2017-07-01 | C3 | 0.39 | 3% | £25.18 | £494.53 | £150 | £469.35 | retained |
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24227.89 | £163704.65 | £150 | £139476.77 | retained |
| 2018-12-31 | C5 | 0.37 | 3% | £83.95 | £1538.44 | £400 | £1454.50 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.66 | 5% | £17469.37 | £194971.28 | £150 | £177501.91 | retained |
| 2021-03-31 | C_IC2 | 0.39 | 3% | £5310.36 | £91307.80 | £150 | £85997.43 | retained |
| 2021-04-30 | C_IC1 | 0.38 | 3% | £8446.20 | £158240.12 | £150 | £149793.92 | retained |
| 2021-12-31 | C_IC3 | 0.54 | 5% | £51815.33 | £165513.05 | £150 | £113697.72 | retained |
| 2022-04-30 | C_IC2 | 0.40 | 3% | £9417.90 | £96250.72 | £150 | £86832.82 | retained |
| 2022-05-30 | C_IC1 | 0.41 | 3% | £18141.91 | £231597.40 | £150 | £213455.49 | retained |
| 2023-03-31 | C6 | 0.39 | 3% | £229.96 | £3238.16 | £400 | £3008.20 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C8 | 2017-04-01 | (window end) | 105 | active |
| C3 | 2017-07-01 | 2020-06-30 | 36 | churned |
| C_IC1 | 2018-01-31 | (window end) | 95 | active |
| C5 | 2018-12-31 | 2020-12-30 | 24 | churned |
| C_IC2 | 2019-01-31 | (window end) | 83 | active |
| C_IC3 | 2021-12-31 | (window end) | 48 | active |
| C6 | 2023-03-31 | 2024-03-30 | 12 | churned |

**Eventually churned (3/7)**: C3, C5, C6 — avg 24 months post-retention before final churn.
**Still active (4/7)**: C8, C_IC1, C_IC2, C_IC3 — survived to simulation end.

## Retention as Deferral (H1 vs H2)

Every retention offer prices one renewal term margin (H1, assumed 12 months). This tracks what actually happened (H2): the realized months to that customer's next retention offer or churn.

| Customer | Offer Date | Assumed (H1) | Realized (H2) | Next Event | Underperformed |
|----------|-----------|---------------|----------------|-------------|-----------------|
| C8 | 2017-04-01 | 12 mo | still active | none yet | no |
| C3 | 2017-07-01 | 12 mo | 36.0 mo | churn | no |
| C_IC1 | 2018-01-31 | 12 mo | 13.0 mo | next_offer | no |
| C_IC1 | 2019-03-02 | 12 mo | 26.0 mo | next_offer | no |
| C_IC1 | 2021-04-30 | 12 mo | 13.0 mo | next_offer | no |
| C_IC1 | 2022-05-30 | 12 mo | still active | none yet | no |
| C5 | 2018-12-31 | 12 mo | 24.0 mo | churn | no |
| C_IC2 | 2019-01-31 | 12 mo | 26.0 mo | next_offer | no |
| C_IC2 | 2021-03-31 | 12 mo | 13.0 mo | next_offer | no |
| C_IC2 | 2022-04-30 | 12 mo | still active | none yet | no |
| C_IC3 | 2021-12-31 | 12 mo | still active | none yet | no |
| C6 | 2023-03-31 | 12 mo | 12.0 mo | churn | no |

0/8 resolved offers (0%) underperformed their assumed deferral window -- the next offer or churn arrived sooner than the term the discount was priced to buy.

Serial savers (2): C_IC1 (4 offers, £68,285), C_IC2 (3 offers, £29,570).

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £8,220,970.68 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £721,095.48 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £743.01 |
| 2017 | £31,639.82 |
| 2018 | £101,758.70 |
| 2019 | £233,491.26 |
| 2020 | £128,570.01 |
| 2021 | £75,439.68 |
| 2022 | £339,300.82 |
| 2023 | £146,246.51 | ← trailing
| 2024 | £348,334.21 | ← trailing
| 2025 | £120,992.73 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £5,355.55 | — |
| C1_2 | — | £647.40 |
| C2 | £6,438.04 | — |
| C2_2 | — | £1,557.92 |
| C3 | £7,335.78 | — |
| C4 | £4,510.24 | £-626.76 |
| C5 | £11,907.21 | — |
| C6 | £22,613.59 | £3,404.72 |
| C7 | £9,077.23 | £597.71 |
| C8 | £10,424.49 | £823.52 |
| C9 | £11,007.45 | £1,494.95 |
| C_IC1 | £1,923,108.93 | £411,521.91 |
| C_IC2 | £1,011,104.23 | £217,606.43 |
| C_IC3 | £3,353,951.54 | £67,264.55 |
| C_IC4 | £1,834,355.42 | £16,803.13 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C1_2 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £6,441.15 | — | — | — | — | — | £14,339.54 | — | £10,526.48 | — | — | — | — | — | — |
| 2017 | £5,601.50 | — | £11,116.43 | — | £9,546.99 | £8,808.37 | £12,098.33 | £24,176.00 | £8,777.12 | £13,810.06 | £11,265.80 | — | — | — | — |
| 2018 | £5,808.05 | — | £9,414.71 | — | £9,275.49 | £7,730.63 | £11,729.08 | £20,244.14 | £8,758.74 | £12,288.83 | £10,599.42 | £2,903,414.38 | — | — | — |
| 2019 | £5,712.93 | — | £9,836.41 | — | £9,414.65 | £7,275.29 | £14,161.51 | £20,277.71 | £8,950.16 | £10,190.96 | £10,617.54 | £2,675,978.51 | £1,664,017.56 | — | — |
| 2020 | £5,695.19 | £17.48 | £8,853.93 | — | £6,721.43 | £7,574.86 | £11,866.56 | £18,754.15 | £8,783.77 | £10,801.44 | £11,532.70 | £1,738,851.73 | £755,935.36 | £2,905,723.73 | £1,438,522.15 |
| 2021 | £4,932.48 | £1,192.45 | £7,259.30 | — | £6,992.28 | £7,515.68 | £11,321.46 | £19,567.16 | £7,818.11 | £10,835.01 | £9,625.86 | £1,519,664.14 | £963,457.48 | £2,434,316.76 | £1,706,943.89 |
| 2022 | £4,400.36 | £1,966.12 | £6,154.83 | £1,084.68 | £6,105.80 | £3,597.98 | £11,380.38 | £19,068.48 | £6,212.79 | £7,664.31 | £9,790.74 | £1,281,646.65 | £825,520.12 | £2,649,800.10 | £1,376,638.63 |
| 2023 | £4,136.75 | £2,369.24 | £4,927.44 | £2,855.02 | £5,569.43 | £2,746.79 | £7,937.00 | £17,967.24 | £5,555.70 | £8,439.10 | £7,646.80 | £1,408,505.47 | £666,004.29 | £2,005,078.93 | £1,259,915.93 |
| 2024 | £3,724.20 | £3,159.41 | £4,845.69 | £3,466.66 | £6,430.87 | £3,087.28 | £7,719.96 | £19,291.77 | £5,631.26 | £7,942.04 | £8,271.75 | £1,187,379.58 | £616,906.30 | £2,145,132.18 | £1,273,969.11 |
| 2025 | £4,034.93 | £3,485.86 | £5,336.79 | £3,265.17 | £4,837.31 | £2,821.14 | £9,061.44 | £15,051.72 | £6,720.99 | £6,930.49 | £7,180.75 | £1,333,397.41 | £742,181.66 | £2,318,770.74 | £1,126,827.37 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £936.35, range £4.58–£4,218.12.

- C1: cost to serve £274.94, net margin after CTS £2,018.79
- C1_2: cost to serve £244.19, net margin after CTS £5,412.07
- C1g: cost to serve £5.73, net margin after CTS £1,349.51
- C2: cost to serve £329.93, net margin after CTS £3,080.37
- C2_2: cost to serve £175.50, net margin after CTS £5,314.02
- C2g: cost to serve £6.87, net margin after CTS £2,012.33
- C3: cost to serve £219.95, net margin after CTS £2,168.89
- C3g: cost to serve £4.58, net margin after CTS £1,293.95
- C4: cost to serve £439.89, net margin after CTS £2,874.90
- C4g: cost to serve £9.17, net margin after CTS £1,334.80
- C5: cost to serve £599.87, net margin after CTS £7,228.41
- C6: cost to serve £959.77, net margin after CTS £21,491.11
- C7: cost to serve £519.13, net margin after CTS £10,233.41
- C8: cost to serve £505.43, net margin after CTS £11,961.56
- C9: cost to serve £491.72, net margin after CTS £12,216.44
- C_IC1: cost to serve £4,218.12, net margin after CTS £1,870,436.44
- C_IC2: cost to serve £3,718.18, net margin after CTS £906,113.37
- C_IC3: cost to serve £3,218.32, net margin after CTS £1,821,654.82
- C_IC3g: cost to serve £67.07, net margin after CTS £622,579.96
- C_IC4: cost to serve £2,718.52, net margin after CTS £1,103,966.75


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 27 recovery surcharge(s) at renewal based on prior-term losses (3 gas). Avg surcharge: 14.9%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.31/MWh |
| C5 | electricity | 2018-12-31 | £-204.31 | £2,322.51 | +3.8% | £148.68/MWh | £153.39/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,283.71 | £6,187.80 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,215.97 | £10,069.00 | +20.0% | £128.22/MWh | £175.80/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,915.21 | £3,421.95 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £177.16/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.62/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £57.53/MWh |
| C1_2 | electricity | 2021-12-30 | £-149.26 | £1,494.88 | +5.0% | £311.83/MWh | £332.49/MWh |
| C7 | electricity | 2021-12-30 | £-169.22 | £1,934.64 | +3.8% | £311.83/MWh | £343.53/MWh |
| C_IC3 | electricity | 2021-12-31 | £-27,935.26 | £442,665.25 | +1.3% | £224.03/MWh | £261.01/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £317.96/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.66/MWh |
| C4 | electricity | 2022-09-30 | £-220.41 | £906.59 | +19.3% | £404.86/MWh | £484.82/MWh |
| C4g | gas | 2022-09-30 | £-901.21 | £1,040.11 | +20.0% | £183.79/MWh | £250.54/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £337.40/MWh |
| C8 | electricity | 2023-03-31 | £-481.87 | £3,898.74 | +7.4% | £319.17/MWh | £344.50/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.61/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.46/MWh |
| C4 | electricity | 2023-09-30 | £-277.33 | £1,324.46 | +15.9% | £216.77/MWh | £249.30/MWh |
| C4g | gas | 2023-09-30 | £-1,950.48 | £2,732.11 | +20.0% | £47.83/MWh | £66.00/MWh |
| C1_2 | electricity | 2023-12-30 | £-589.08 | £2,728.18 | +16.6% | £242.22/MWh | £268.29/MWh |
| C7 | electricity | 2023-12-30 | £-445.92 | £3,990.91 | +6.2% | £242.22/MWh | £244.32/MWh |
| C_IC3 | electricity | 2023-12-31 | £-125,200.05 | £971,267.98 | +7.9% | £118.95/MWh | £121.92/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |


## Flexibility Revenue — DSR & Capacity Market (Phase AG/NX)

Two flexibility revenue streams: residential DSR (EV/ASHP/battery via FlexibilityRevenueBook) and I&C demand response (interruptible process load via ICFlexibilityRevenueBook).
- **Capacity Market (CM):** T-4 auction clearing prices (£6.44–£22.50/kW/yr by year, NESO); operational since 2014.
- **Demand Flexibility Service (DFS):** launched October 2022; £4.5/MWh × 20 events/yr.
- **I&C DSR aggregator fee:** 20% of gross CM/DFS revenue.

**Total 2016–2025:** £0.00  (Residential: £0.00 | I&C: £21,381.06)

### I&C Demand Response Revenue

| Year | Net Revenue | Enrolled | Flex kW |
|------|-------------|----------|---------|
| 2016 | £2,109.00 | 4 | 176 kW |
| 2017 | £1,406.00 | 4 | 176 kW |
| 2018 | £2,727.64 | 4 | 176 kW |
| 2019 | £2,530.80 | 4 | 176 kW |
| 2020 | £3,163.50 | 4 | 176 kW |
| 2021 | £1,181.04 | 4 | 176 kW |
| 2022 | £918.12 | 4 | 176 kW |
| 2023 | £2,258.04 | 4 | 176 kW |
| 2024 | £2,543.46 | 4 | 176 kW |
| 2025 | £2,543.46 | 4 | 176 kW |

## Portfolio Intelligence Pack (Phase AH)

Board-level synthesis of CRM and flexibility intelligence derived from observable operational data.

### 1. Retention Intelligence

- **Retention offers made:** 12
- **Offer acceptance rate:** 100% (12 retained / 0 churned despite offer)
- **Estimated margin protected:** £1,209,365.23
- **No-offer churns:** 6 total (0 blind miss / 0 deliberate pass)
- **Retention coverage rate:** 67% of at-risk renewals received an offer

### 2. Flexibility Revenue Intelligence

- No flexibility revenue data available.

### 3. Churn Pattern Analysis

- **Total lifetime churn events:** 6
- **Peak churn year:** 2020 (3 events)
- **Net book movement:** 2 acquisitions − 6 churns = -4
- **Portfolio trend:** shrinking

### 4. Board Recommendations

1. **Crisis-year churn:** 1 churn events in 2021–2022. Maintain minimum hedge floor pre-crisis to preserve pricing stability and limit bill-shock churn.

## CRM Intelligence: Risk Triage (Final Year)

Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.

| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |
|---------|-----|-----------|-----------|----------|-------------|-----------------|
| C5 | SME | MEDIUM | 27% | 9% | -20.3% [competitive] | £7,228.41 |
| C1 | resi | MEDIUM | 22% | 7% | -23.0% [competitive] | £2,018.79 |
| C_IC3 | I&C | MEDIUM | 20% | 10% | -54.0% [competitive] | £1,821,654.82 |
| C6 | SME | MEDIUM | 19% | 25% | -24.8% [competitive] | £21,491.11 |
| C4 | resi | LOW | 14% | 14% | -9.0% | £2,874.90 |
| C2_2 | resi | LOW | 11% | 10% | +16.5% [overpriced] | £5,314.02 |
| C7 | resi | LOW | 11% | 17% | -14.3% | £10,233.41 |
| C9 | resi | LOW | 11% | 14% | -14.3% | £12,216.44 |
| C8 | resi | LOW | 9% | 13% | -23.6% [competitive] | £11,961.56 |
| C1_2 | resi | LOW | 8% | 8% | +3.3% | £5,412.07 |
| C3 | resi | LOW | 6% | 8% | -39.0% [competitive] | £2,168.89 |
| C2 | resi | LOW | 5% | 6% | +46.6% [overpriced] | £3,080.37 |
| C_IC1 | I&C | LOW | 4% | 95% | -0.1% | £1,870,436.44 |
| C_IC2 | I&C | LOW | 4% | 95% | +12.4% [overpriced] | £906,113.37 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 0 accounts
- MEDIUM (>=15%): 4 accounts
- LOW (<15%): 10 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £0.00

## Churn Root Cause Attribution

Per-churned-account analysis: pricing journey, rate-vs-SVT positioning, and company vs SIM churn estimate at the point of departure.

| Account | Seg | Churn Date | Tenure | Last Rate Shock | Rate vs SVT | Sim Risk | Co. Est. | Margin Lost |
|---------|-----|------------|--------|-----------------|-------------|----------|----------|-------------|
| C3 | resi | 2020-06-30 | 4.0yr | -4.3% | -39.0% | 6% | 8% | £2,168.89 |
| C1 | resi | 2020-12-30 | 5.0yr | -0.8% | -23.0% | 22% | 7% | £2,018.79 |
| C5 | SME | 2020-12-30 | 5.0yr | +2.6% | -20.3% | 27% | 9% | £7,228.41 |
| C2 | resi | 2022-03-31 | 6.0yr | +12.8% | +46.6% | 5% | 6% | £3,080.37 |
| C6 | SME | 2024-03-30 | 8.0yr | -0.7% | -24.8% | 19% | 25% | £21,491.11 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 14% | 14% | £2,874.90 |

**Root Cause Summary:**
- Total churned accounts: 6
- Lifetime margin lost: £38,862.47
- Average tenure at departure: 6.0 years
- Company-warned churns (co. est. >=20%): 1 -- C6
- Crisis-era churns (2021-22): 1 -- absolute crisis price level, not rate-change delta, was the driver
- Overpriced vs SVT at departure: 1 account(s) -- rate shock risk was observable but unactioned

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 6 accounts that churned without an offer? Calibrated from 12 actual offers (observed retention rate 100%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C3 | resi | 2020-06-30 | 8% | £585.39 | 5% | £29.27 | £556.12 | MISSED OPP. |
| C1 | resi | 2020-12-30 | 7% | £415.17 | 5% | £20.76 | £394.42 | MISSED OPP. |
| C5 | SME | 2020-12-30 | 9% | £1,641.98 | 8% | £131.36 | £1,510.62 | MISSED OPP. |
| C2 | resi | 2022-03-31 | 6% | £236.63 | 5% | £11.83 | £224.80 | MISSED OPP. |
| C6 | SME | 2024-03-30 | 25% | £2,861.16 | 8% | £228.89 | £2,632.27 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 14% | £468.87 | 5% | £23.44 | £445.43 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 6
- Correct no-offer (net-neg ETM): 0
- Missed opportunities (positive ETM, below detection): 6
- Total term margin foregone: £6,209.20
- Total retention cost (counterfactual): £445.55
- Net counterfactual benefit: £5,763.65 (at 100% retention probability)
- Root cause: company churn detection below threshold for all missed cases -- churn model underestimated bill-shock risk

## Pricing Basis Risk Attribution

Forward curve accuracy at each contract term. tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd: positive = company over-estimated costs (higher than market); negative = company under-estimated (margin-at-risk).
Portfolio-wide mean error: +6.1%

| Year | Contracts | Mean Error | Max Abs | Over-priced | Under-priced | Assessment |
|------|-----------|------------|---------|-------------|--------------|------------|
| 2016 | 17 | +8.9% | 29.1% | 9 | 4 | moderate over |
| 2017 | 14 | +5.4% | 46.6% | 8 | 5 | moderate over |
| 2018 | 16 | -2.9% | 27.7% | 6 | 8 | on target |
| 2019 | 19 | +8.3% | 37.2% | 9 | 3 | moderate over |
| 2020 | 22 | -0.9% | 33.8% | 9 | 8 | on target |
| 2021 | 16 | +9.0% | 44.5% | 6 | 3 | moderate over |
| 2022 | 16 | -0.8% | 23.2% | 7 | 4 | on target |
| 2023 | 15 | +19.8% | 40.0% | 10 | 1 | HIGH OVER-PRICE |
| 2024 | 14 | +7.9% | 22.6% | 8 | 1 | moderate over |
| 2025 | 2 | +33.1% | 33.1% | 2 | 0 | HIGH OVER-PRICE |

**Basis Risk Summary:**
- Portfolio mean tariff error: +6.1%
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
| 2021 | £5,198 | £4,332 | 0.30% |
| 2022 | £10,203 | £8,502 | 0.30% |
| 2023 | £6,736 | £5,613 | 0.26% |
| 2024 | £3,191 | £2,659 | 0.15% |
| 2025 | £4,657 | £3,881 | 0.48% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,203 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £524 | £57 | 7.1% |
| 2017 | 14 | £16,735 | £8,803 | £2,260 | 13.5% |
| 2018 | 15 | £29,022 | £17,502 | £6,784 | 23.4% |
| 2019 | 17 | £70,486 | £41,296 | £13,735 | 19.5% |
| 2020 | 19 | £64,387 | £41,673 | £6,767 | 10.5% |
| 2021 | 14 | £123,908 | £54,498 | £5,389 | 4.3% << |
| 2022 | 15 | £229,260 | £70,024 | £22,620 | 9.9% |
| 2023 | 13 | £199,587 | £73,533 | £11,250 | 5.6% |
| 2024 | 13 | £168,447 | £96,838 | £26,795 | 15.9% |
| 2025 | 10 | £97,101 | £51,893 | £12,099 | 12.5% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £26,795 net/customer
**Worst year per customer:** 2016 at £57 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £368 | — | £368 |
| C1_2 | £641 | — | £641 |
| C1g | — | £669 | £669 |
| C2 | £180 | — | £180 |
| C2_2 | £1,551 | — | £1,551 |
| C2g | — | £907 | £907 |
| C3 | £16 | — | £16 |
| C3g | — | £336 | £336 |
| C4 | £193 | — | £193 |
| C4g | — | £-1,625 | £-1,625 * |
| C5 | £-386 | — | £-386 * |
| C6 | £4,241 | — | £4,241 |
| C7 | £-572 | — | £-572 * |
| C8 | £2,328 | — | £2,328 |
| C9 | £2,240 | — | £2,240 |
| C_IC1 | £846,421 | — | £846,421 |
| C_IC2 | £435,818 | — | £435,818 |
| C_IC3 | £136,457 | — | £136,457 |
| C_IC3g | — | £64,511 | £64,511 |
| C_IC4 | £32,221 | — | £32,221 |
| **Total** | **£1,461,718** | **£64,799** | **£1,526,517** |

Loss-making accounts: C4g (£-1,625), C7 (£-572), C5 (£-386)
Gas loss-making: C4g (£-1,625)
Gas portfolio net: £64,799 (4.2% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,034 | £10,920 | £-8,885 |
| 2017 | £30,081 | £112,495 | £-82,414 |
| 2018 | £109,583 | £246,455 | £-136,872 |
| 2019 | £252,590 | £836,842 | £-584,252 |
| 2020 | £85,012 | £962,664 | £-877,652 |
| 2021 | £191,989 | £457,510 | £-265,520 |
| 2022 | £184,435 | £1,207,217 | £-1,022,781 |
| 2023 | £381,547 | £1,221,202 | £-839,654 |
| 2024 | £199,174 | £604,582 | £-405,408 |
| 2025 | £62 | £345 | £-283 |
| **Total** | **£1,436,507** | **£5,660,233** | **£-4,223,726** |

Largest hedging cost: **2022** (£1,022,781 vs naked)
Smallest hedging cost: **2025** (£283 vs naked)
Conclusion: systematic forward hedging cost £4,223,726 over 10 years vs spot purchasing.

## Customer Service Quality

Ofgem benchmarks: bill clarity >0.82 (GREEN) / >0.80 (AMBER) / ≤0.80 (RED); complaint probability <5% (GREEN) / <6% (RED); bill shock <0.20% (GREEN) / <0.30% (AMBER) / ≥0.30% (RED).

| Year | Clarity | Complaint% | Shock% | Shock events | Bills | RAG |
|------|---------|------------|--------|--------------|-------|-----|
| 2016 | 0.829 G | 4.7% | 0.20% | 31 | 108 | GREEN |
| 2017 | 0.818 A | 4.7% | 0.17% | 50 | 168 | AMBER |
| 2018 | 0.810 A | 4.7% | 0.16% | 60 | 180 | AMBER |
| 2019 | 0.824 G | 4.7% | 0.17% | 66 | 204 | GREEN |
| 2020 | 0.832 G | 4.3% | 0.14% | 52 | 205 | GREEN |
| 2021 | 0.816 A | 4.8% | 0.24% | 47 | 168 | AMBER |
| 2022 | 0.783 R | 5.8% | 0.34% | 71 | 160 | RED ! |
| 2023 | 0.802 A | 5.0% | 0.18% | 48 | 156 | AMBER |
| 2024 | 0.805 A | 4.8% | 0.17% | 40 | 141 | AMBER |
| 2025 | 0.768 R | 6.1% | 0.25% | 23 | 60 | RED ! |

Worst clarity year: **2025** (0.768)
Highest complaint probability: **2025** (6.1%)
Worst bill shock: **2022** (0.34%)
RED years: 2022, 2025
AMBER years: 2017, 2018, 2021, 2023, 2024
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,434 | £743 |
| 2017 | 2.69 | WATCH | £2,498,375 | £31,640 |
| 2018 | — | — | £2,487,547 | £101,759 |
| 2019 | — | — | £2,611,522 | £233,491 |
| 2020 | — | — | £2,923,397 | £128,570 |
| 2021 | — | — | £2,956,667 | £75,440 |
| 2022 | 2.70 | WATCH | £3,161,597 | £339,301 |
| 2023 | 2.72 | WATCH | £3,382,344 | £146,247 |
| 2024 | — | — | £3,777,722 | £348,334 |
| 2025 | — | — | £3,829,410 | £120,993 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,829,410)**
**Treasury growth: £2,467,434 → £3,829,410 (+£1,361,977)**

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
| C3 | 2020-06 | 7.6% | £585 | below threshold |
| C1 | 2020-12 | 7.3% | £415 | below threshold |
| C5 | 2020-12 | 9.0% | £1,642 | below threshold |
| C2 | 2022-03 | 6.2% | £237 | below threshold |
| C6 | 2024-03 | 24.7% | £2,861 | below threshold ⚑ |
| C4 | 2024-09 | 14.0% | £469 | below threshold |

**High-risk no-offer events (≥10% churn): 2** — £3,330 margin at risk.

### Gas Renewal Risk — High-Churn Reprice Events (≥15% estimate)

| Customer | Term Start | Old Rate p/therm | New Rate p/therm | Churn Est |
|----------|-----------|-----------------|-----------------|----------|
| C2g | 2017-04 | 26.92 | 32.81 | 20.1% |
| C1g | 2017-12 | 26.25 | 33.49 | 22.6% |
| C3g | 2018-07 | 23.11 | 28.80 | 20.8% |
| C4g | 2018-10 | 26.10 | 33.61 | 23.3% |
| C_IC3g | 2020-12 | 15.44 | 19.38 | 21.3% |
| C2g | 2021-03 | 21.66 | 35.00 | 39.9% |
| C4g | 2021-09 | 16.09 | 35.00 | 73.5% |
| C_IC3g | 2021-12 | 19.38 | 125.90 | 95.0% |

**High-risk gas reprices: 9**

> ⚑ = customers with ≥15% churn estimate who received no retention offer.

## Retention Decision Economics

Per-offer cost, expected margin protected, and ROI for each retention intervention.

| Customer | Period | Retention Cost £ | Margin Protected £ | ROI | Discount % | Outcome |
|----------|--------|-----------------|-------------------|-----|------------|---------|
| C8 | 2017-04 | £46 | £868 | 18.9× | 3% | retained |
| C3 | 2017-07 | £25 | £495 | 19.6× | 3% | retained |
| C_IC1 | 2018-01 | £24,228 | £163,705 | 6.8× | 8% | retained |
| C5 | 2018-12 | £84 | £1,538 | 18.3× | 3% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £17,469 | £194,971 | 11.2× | 5% | retained |
| C_IC2 | 2021-03 | £5,310 | £91,308 | 17.2× | 3% | retained |
| C_IC1 | 2021-04 | £8,446 | £158,240 | 18.7× | 3% | retained |
| C_IC3 | 2021-12 | £51,815 | £165,513 | 3.2× | 5% | retained |
| C_IC2 | 2022-04 | £9,418 | £96,251 | 10.2× | 3% | retained |
| C_IC1 | 2022-05 | £18,142 | £231,597 | 12.8× | 3% | retained |
| C6 | 2023-03 | £230 | £3,238 | 14.1× | 3% | retained |

**Total retention spend: £150,056** | **Total margin protected: £1,209,365**
**Portfolio retention ROI: 8.1×** | **Retained: 12/12**
**Best ROI intervention: C3 2017-07 (19.6×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £202,013 | — |
| Exit Gas (with churn risk) | £82,480 | -£119,533 |
| Reprice to Breakeven | £203,638 | +£1,625 |

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
| 2020 | 81.1% | 0.0% | 96.0% | 1 | 13 |
| 2021 | 84.4% | 0.0% | 97.0% | 1 | 13 |
| 2022 | 86.4% | 0.0% | 97.4% | 1 | 12 |
| 2023 | 83.8% | 0.0% | 96.1% | 1 | 12 |
| 2024 | 80.1% | 0.0% | 94.4% | 1 | 9 |
| 2025 | 87.2% | 85.0% | 89.4% | — | 2 |

**Lowest portfolio hedge fraction: 2024 (80.1%)** — risk erosion from regime-change blindness.
**Naked positions first appear in 2019** — unhedged accounts expose portfolio to spot price swings.

> Regime-change blindness: the sim converged toward lower hedging during calm 2016-2020,
> mirroring the strategy that destroyed real UK suppliers entering the 2021-22 crisis.

## Risk Committee Intervention Pattern

Annual risk committee wake-ups (triggered when portfolio VaR exceeds threshold).

| Year | Wake-ups | Customer Adjustments | Avg Customers/Event | Max VaR Stressed £ |
|------|----------|---------------------|--------------------|--------------------|
| 2016 | 13 | 13 | 1.0 | £9 |
| 2017 | 12 | 33 | 2.8 | £401 |
| 2022 | 9 | 59 | 6.6 | £20,525 |
| 2023 | 4 | 32 | 8.0 | £48,907 |

**Peak intervention year: 2016 (13 wake-ups)**
**Total committee events (all years): 38**

> Each wake-up adjusts hedge fractions upward for flagged customers. 2016-17 (early book).
> 2022-23 crisis years trigger most interventions on I&C anchor accounts.

## Worst Half-Hourly Settlement Period by Year

Most loss-making single 30-minute period per settlement year.

| Year | Date | SP | Customer | Net Margin £ |
|------|------|----|----------|-------------|
| 2016 | 2016-12-31 | 48 | C5 | -£408 |
| 2017 | 2017-12-31 | 48 | C2 | -£287 |
| 2018 | 2018-12-31 | 48 | C2 | -£196 |
| 2019 | 2019-12-31 | 48 | C5 | -£469 |
| 2020 | 2020-03-16 | 20 | C_IC1 | -£19 |
| 2021 | 2021-12-31 | 48 | C4 | -£185 |
| 2022 | 2022-03-30 | 48 | C2 | -£112 |
| 2023 | 2023-06-16 | 22 | C_IC1 | -£22 |
| 2024 | 2024-06-28 | 31 | C_IC1 | -£26 |
| 2025 | 2025-01-08 | 31 | C_IC1 | -£81 |

**Single worst period: 2019 2019-12-31 SP48 (C5, -£469)** — exposure from gas supply anchor at year-end pricing.

> SP = settlement period (1-48; SP1 = 00:00-00:30). Year-end gas exposure dominates from 2020 onward as C_IC3g position grows.

## BSC Credit Obligation and Regulatory Levy Breakdown

Elexon BSC credit posting requirement and annual levy costs.

| Year | BSC Credit £ | CM Levy £ | Mutualization £ | CCL £ | Gas Network £ |
|------|-------------|----------|----------------|-------|--------------|
| 2016 | £30 | £37 | — | £189 | £479 |
| 2017 | £559 | £1,977 | — | £11,165 | £898 |
| 2018 | £1,019 | £9,350 | — | £17,434 | £905 |
| 2019 | £1,851 | £31,969 | — | £42,460 | £50,388 |
| 2020 | £2,375 | £56,549 | — | £69,453 | £47,213 |
| 2021 | £5,198 | £49,580 | £41,350 | £71,203 | £50,301 |
| 2022 | £10,203 | £36,681 | £99,478 | £70,920 | £54,433 |
| 2023 | £6,736 | £50,966 | £13,752 | £71,702 | £79,700 |
| 2024 | £3,191 | £68,707 | £1,999 | £72,815 | £76,429 |
| 2025 | £4,657 | £31,029 | £854 | £31,156 | £31,816 |

**Peak BSC credit obligation: 2022 (£10,203)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 15 | £174,863 | £94,777 | £11,089 | £11,658 |
| 2017 | 1 | £3,123,592 | £1,874,655 | £846,421 | £3,123,592 |
| 2018 | 1 | £1,525,272 | £909,832 | £435,818 | £1,525,272 |
| 2019 | 2 | £6,462,333 | £2,447,520 | £200,968 | £3,231,167 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £32,221 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,231,167/customer)**
**Best net margin cohort: 2017 (£846,421)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £602 | — | 108 |
| 2017 | +£2,707 | £37,159 | £302 | — | 168 |
| 2018 | +£9,875 | £65,510 | £332 | — | 180 |
| 2019 | +£28,353 | £164,625 | £589 | — | 204 |
| 2020 | +£35,391 | £238,634 | £-60 | — | 205 |
| 2021 | +£14,982 | £246,246 | £213 | — | 168 |
| 2022 | -£49,739 CREDIT | £256,213 | £119 | 2 | 160 |
| 2023 | +£64,773 | £271,884 | £-0 | 47 | 156 |
| 2024 | +£109,934 | £307,626 | £-0 | 4271 | 141 |
| 2025 | +£46,950 | £135,727 | £0 | — | 60 |

**CfD turned CREDIT in 2022: -£49,739 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2016 (£602)**

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
| 2020 | £5,687 | £1,207 | £4,220 | £704,697 | £75,972 | £791,784 |
| 2021 | £5,728 | £354 | £2,955 | £671,674 | £82,255 | £762,966 |
| 2022 | £4,971 | -£762 | £3,744 | £951,287 | £91,118 | £1,050,358 |
| 2023 | £7,946 | -£575 | £4,462 | £822,585 | £121,515 | £955,934 |
| 2024 | £10,508 | £762 | £1,513 | £1,122,456 | £123,652 | £1,258,891 |
| 2025 | £4,535 | £0 | £0 | £460,883 | £53,509 | £518,927 |

**Best gross margin year: 2024 (£1,258,891)** | **Worst: 2016 (£6,814)**
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
| 2020 | 10 | -30.1% | 0/10 | -68.8% | +-19.2% |
| 2021 | 8 | +11.3% | 5/8 | -12.0% | +59.9% |
| 2022 | 8 | +4.3% | 4/8 | -64.0% | +95.6% |
| 2023 | 8 | -32.8% | 0/8 | -60.5% | +-2.1% |
| 2024 | 8 | -20.6% | 1/8 | -54.0% | +3.3% |
| 2025 | 2 | -3.6% | 1/2 | -23.6% | +16.5% |

**Best headroom year: 2023 (avg 32.8% below SVT)**
**Largest above-SVT year: 2021** (5/8 terms above — note: I&C customers exempt from SVT cap)

> SVT (Standard Variable Tariff) = Ofgem price cap. Residential tariffs must not exceed SVT.
> I&C/SME terms above SVT are expected during crisis years when wholesale >cap.

## Portfolio Stress Test History

Retrospective RAG status: would year-end treasury have survived each scenario?
Credit facility: £2M. Weekly burn estimated at 1% of year-end treasury.

| Year | Treasury £ | Mkt Spike | Credit | Demand | Liquidity | Combined |
|------|-----------|----------|----------|----------|----------|----------|
| 2016 | £2,467,434 | AMBER | RED | GREEN | AMBER | RED |
| 2017 | £2,498,375 | AMBER | RED | GREEN | AMBER | RED |
| 2018 | £2,487,547 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,611,522 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,923,397 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,956,667 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,161,597 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,382,344 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,777,722 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,829,410 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 42.1% | £1,181 | £605 | 1.53% |
| 2017 | 14 | 32.9% | £24,902 | £8,914 | 2.03% |
| 2018 | 15 | 41.1% | £40,064 | £17,612 | 2.23% |
| 2019 | 17 | 40.3% | £96,791 | £41,404 | 2.13% |
| 2020 | 19 | 40.1% | £97,740 | £41,768 | 2.35% |
| 2021 | 14 | 29.1% | £172,552 | £54,591 | 2.22% |
| 2022 | 15 | 22.1% | £282,773 | £70,113 | 2.27% |
| 2023 | 13 | 24.7% | £267,171 | £73,621 | 2.51% |
| 2024 | 13 | 39.1% | £230,838 | £96,868 | 2.44% |
| 2025 | 10 | 38.3% | £122,843 | £51,935 | 3.40% |

**Best EBIT%: 2016 (42.1%)** | **Worst EBIT%: 2022 (22.1%)**
**Peak revenue/customer: 2022 (£282,773)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Population Anchoring -- Complaints & Arrears (Phase PS)

SIM aggregate complaint and arrears rates vs published UK benchmarks.
Complaints: Ofgem QoS survey, I&C adjusted (GREEN 2-6%, crisis 2-8%).
Arrears: DESNZ business energy debt (GREEN <8%, crisis <12%).

| Year | Complaint rate% | C.Bench hi | C.RAG | Arrears rate% | A.Bench hi | A.RAG |
|------|-----------------|-----------|-------|---------------|-----------|-------|
| 2016 | 4.70% | 6% | OK | 30.8% | 8% | ! |
| 2017 | 4.67% | 6% | OK | 28.6% | 8% | ! |
| 2018 | 4.66% | 6% | OK | 33.3% | 8% | ! |
| 2019 | 4.67% | 6% | OK | 23.5% | 8% | ! |
| 2020 | 4.28% | 6% | OK | 10.5% | 8% | ~ |
| 2021 | 4.81% | 8% | OK | 14.3% | 12% | ~ |
| 2022 | 5.82% | 8% | OK | 33.3% | 12% | ! |
| 2023 | 5.00% | 8% | OK | 15.4% | 12% | ~ |
| 2024 | 4.84% | 6% | OK | 23.1% | 8% | ! |
| 2025 | 6.09% | 6% | ~ | 10.0% | 8% | ~ |

**Complaints:** 9 of 10 years GREEN (I&C baseline 2-6% normal, 2-8% crisis).
**Arrears:** 0 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).

## Plausibility vs Industry

Key metrics vs UK retail energy norms (Ofgem/Cornwall Insight). OK = within range | ~ = amber | ! = outside expected range.

| Year | Net margin% | Gross margin% | Bad debt% | Churn% |
|------|-------------|---------------|-----------|--------|
| 2016 | !42.1% | !51.2% | OK1.53% | ~0% |
| 2017 | !32.9% | !35.8% | OK2.03% | ~0% |
| 2018 | !41.1% | !44.0% | OK2.23% | ~0% |
| 2019 | !40.3% | !42.8% | OK2.13% | ~0% |
| 2020 | !40.1% | !42.7% | OK2.35% | OK16% |
| 2021 | !29.1% | !31.6% | OK2.22% | ~0% |
| 2022 | !22.1% | ~24.8% | OK2.27% | OK7% |
| 2023 | !24.7% | ~27.6% | OK2.51% | ~0% |
| 2024 | !39.1% | !42.0% | OK2.44% | OK15% |
| 2025 | !38.3% | !42.3% | OK3.40% | ~0% |

**Benchmark ranges:** Net margin %: −5 to +8% green | Gross margin %: 0–20% green | Bad debt %: 0–5% green | Annual churn %: 3–35% green.
**RED — review required: 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025**

## Churn Prediction Calibration

How well the company estimated churn probability versus actual simulation outcomes.

| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |
|----------|------|----------------|-----------------|-------|---------|
| C3 | 2020-06 | 6.5% | 7.6% | +1.1pp | ACCURATE |
| C1 | 2020-12 | 22.3% | 7.3% | -15.0pp | UNDERESTIMATED |
| C5 | 2020-12 | 27.1% | 9.0% | -18.1pp | UNDERESTIMATED |
| C2 | 2022-03 | 4.9% | 6.2% | +1.3pp | ACCURATE |
| C6 | 2024-03 | 18.6% | 24.7% | +6.1pp | ACCURATE |
| C4 | 2024-09 | 14.3% | 14.0% | -0.3pp | ACCURATE |

**Outcomes: 2 underestimated / 4 accurate / 0 overestimated**
**Mean absolute error: 7.0pp**
**Systematic bias: company consistently UNDER-predicted churn risk.**

> Company churn estimates derived from company-observable signals (bill shock,
> margin feedback, renewal history) without access to the simulation's internal
> churn parameters — epistemic gap is expected and realistic for a small supplier.

## Counterfactual Retention & Threshold Optimisation

**Current threshold:** 30% | F1=0.000
**Optimal threshold:** 5% | F1=0.211

**RAG [!]:** RED — 3 unrecoverable high-value miss(es) — model underestimates churn: optimal threshold below current

**Missed retention opportunities:** 6 no-offer churns
  Value at stake: £6,209
  Counterfactually recoverable (with offer): 3/6
  Net value recoverable (after offer cost): £2,144

### Per-miss detail

| Year | Customer | Est | SIM p | Recoverable? | Margin | Net value |
|------|----------|-----|-------|-------------|--------|----------|
| 2020 | C3 | 8% | 6% | No | £585 | £-50 |
| 2020 | C1 | 7% | 22% | Yes | £415 | £365 |
| 2020 | C5 | 9% | 27% | Yes | £1,642 | £1,592 |
| 2022 | C2 | 6% | 5% | Yes | £237 | £187 |
| 2024 | C6 | 25% | 19% | No | £2,861 | £-50 |
| 2024 | C4 | 14% | 14% | No | £469 | £-50 |

### Threshold sensitivity curve

| Threshold | Recall | Precision | F1 |
|-----------|--------|-----------|----|
| 0% | 1.000 | 0.103 | 0.188 |
| 5% | 1.000 | 0.118 | 0.211 ← optimal |
| 10% | 0.333 | 0.074 | 0.121 |
| 15% | 0.167 | 0.091 | 0.118 |
| 20% | 0.167 | 0.125 | 0.143 |
| 25% | 0.000 | 0.000 | 0.000 |
| 30% | 0.000 | 0.000 | 0.000 |
| 35% | 0.000 | 0.000 | 0.000 |
| 40% | 0.000 | 0.000 | 0.000 |
| 45% | 0.000 | 0.000 | 0.000 |
| 50% | 0.000 | 0.000 | 0.000 |

### Lift-per-pound by intervention class (Part 4)

Every no-offer churn is one of two different management problems: the model never scored enough risk to consider an offer (detection gate), or a tier discount was priced but the cost/benefit guard blocked it (uneconomical). Each gets its own matched counterfactual under H3 (effectiveness scales with discount size) -- this is the fitness function Digital Darwinism compares policies on, not raw miss counts.

| Class | Misses | Assumed discount | Assumed effectiveness | Would retain | Net value | Lift/GBP |
|-------|--------|-------------------|------------------------|---------------|-----------|----------|
| Detection gate (never scored above offer threshold) | 6 | 3% | 12% | 2/6 | £1,579 | +5.26 |

## Churn Model Quality (Phase NK)

Company churn model performance: did the company predict churn before it happened?
Threshold: company_churn_estimate > 30% = predicted. Evaluated at each renewal event.

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total churn events | 6 | Customers who actually churned |
| True Positives (TP) | 0 | Churn predicted AND happened |
| False Positives (FP) | 5 | Churn predicted BUT customer renewed |
| False Negatives (FN) | 6 | Churn NOT predicted BUT happened (blind miss) |
| True Negatives (TN) | 47 | No churn predicted AND customer renewed |
| **Recall** | **0.0%** | % of churners detected before departure |
| **Precision** | **0.0%** | % of retention offers to genuine churners |
| **F1 Score** | **0.00** | Harmonic mean of recall and precision |

**Model quality: RED**

> **Board Action Required:** F1 < 0.30 — churn model is failing to detect departures.
> Company is missing churning customers; retention spend may be misdirected.

> **Known limitation:** passive SVT-rollers (69% of renewals) churn at ~10% effective rate
> after passive_churn_cap, but the 30% retention threshold is calibrated for active renewers.
> Passive blind misses are a structural feature — these customers's seasonal bill variability
> (8-11 monthly shocks/year) inflates the SIM's base churn_probability to 29-38%, but
> effective churn after the passive cap is ~11%. A separate passive loyalty programme
> would be needed to recover these departures.

### Episode-Level Recall (credits catches before departure)

The table above scores every renewal in isolation, so a customer correctly
flagged and saved by a retention offer, whose risk signal later decays before
they eventually churn at a subsequent renewal, is counted as both a false
positive (at the save) and a false negative (at the eventual departure) --
the same real catch penalised twice. Episode-level recall instead asks: did
the model ever flag this customer, at any renewal, before they left?

| Metric | Value |
|--------|-------|
| Churners | 6 |
| Caught before departure (any renewal) | 3 |
| Never flagged | 3 |
| **Episode recall** | **50.0%** |
| Decayed after a prior save | 3 |
| Prevented-churn saves (retention offers that worked) | 12 |

### Per-Year Model Performance

| Year | TP | FP | FN | TN | Recall | Precision |
|------|----|----|----|----|--------|-----------|
| 2016 | 0 | 0 | 0 | 3 | 0% | 0% |
| 2017 | 0 | 0 | 0 | 3 | 0% | 0% |
| 2018 | 0 | 2 | 0 | 2 | 0% | 0% |
| 2019 | 0 | 1 | 0 | 3 | 0% | 0% |
| 2020 | 0 | 0 | 3 | 7 | 0% | 0% |
| 2021 | 0 | 1 | 0 | 7 | 0% | 0% |
| 2022 | 0 | 0 | 1 | 7 | 0% | 0% |
| 2023 | 0 | 1 | 0 | 7 | 0% | 0% |
| 2024 | 0 | 0 | 2 | 6 | 0% | 0% |
| 2025 | 0 | 0 | 0 | 2 | 0% | 0% |

## Credit Risk & Capital Stress (Phase NR)

**Ofgem FRA stress multiplier:** 2.5x (empirical: 2021-22 crisis, industry bad debt 1% → 2.5% revenue)

| Year | Revenue £ | Bad Debt £ | Bad Debt % | Crisis Stress £ |
|------|-----------|------------|------------|-----------------|

**Total bad debt (all years):** £2,096
**Crisis stress incremental:** £3,144

**RAG [OK]:** GREEN — Incremental credit stress below 0.5% revenue — not material

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (10 active customers) under 12-month forward scenarios.
Generated: 2026-07-08T22:30:58Z

Closes CLAUDE.md known failure: regime-change blindness — board can now ask 'what if 2021-22 happened again?'

| Scenario | Elec Fwd (£/MWh) | Gas Fwd (£/MWh) | Hedge Rec | Renewing | Exposure Delta |
|----------|------------------|-----------------|-----------|----------|----------------|
| Base | 86.7 | 55.1 | INCREASE | 0 | — |
| Bull | 56.1 | 35.7 | INCREASE | 0 | £-397,725 |
| Bear | 147.9 | 93.8 | INCREASE | 0 | +£795,451 |
| Crisis | 217.3 | 110.2 | INCREASE | 0 | +£1,559,960 |

**Scenario labels:**
- **Base**: Base (normal OU, long-run mean start)
- **Bull**: Bull (prices below long-run mean — cheap energy)
- **Bear**: Bear (prices above long-run mean — expensive energy)
- **Crisis**: Crisis (high-vol regime forced — 2021-22 style shock)

**Exposure delta:** additional annual unhedged commodity cost vs base scenario.
Positive = more expensive under this scenario; negative = cheaper.

**Renewal flags under each scenario:**

## Tariff Estimation Accuracy

Mean and maximum absolute error between company tariff estimates and actual outturn.

| Year | Observations | Mean Abs Error | Max Abs Error | Accuracy |
|------|-------------|---------------|--------------|----------|
| 2016 | 17 | 15.1% | 29.1% | POOR |
| 2017 | 14 | 16.6% | 46.6% | POOR |
| 2018 | 16 | 12.1% | 27.7% | MODERATE |
| 2019 | 19 | 11.0% | 37.2% | MODERATE |
| 2020 | 22 | 12.4% | 33.8% | MODERATE |
| 2021 | 16 | 15.4% | 44.5% | POOR |
| 2022 | 16 | 11.1% | 23.2% | MODERATE |
| 2023 | 15 | 21.3% | 40.0% | POOR |
| 2024 | 14 | 10.3% | 22.6% | MODERATE |
| 2025 | 2 | 33.1% | 33.1% | POOR |

**Best accuracy year (n≥5): 2024 (10.3% mean error)**
**Worst accuracy year (n≥5): 2023 (21.3% mean error)**

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
| 2020 | 17 | +3.3 | 8 | 9 | 2 |
| 2021 | 13 | +13.0 | 13 | 0 | 6 |
| 2022 | 12 | +18.1 | 11 | 1 | 5 |
| 2023 | 12 | +7.7 | 8 | 4 | 8 |
| 2024 | 11 | +6.5 | 6 | 5 | 2 |
| 2025 | 2 | +3.4 | 2 | 0 | 0 |

**Total adjustments 2016-2025: 113** | **Peak avg adjustment: 2022 (+18.1 £/MWh)**
**Emergency reprices: 27 total** (8 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £31,307 | £10,436 | — |
| 2017 | 9 | £105,201 | £11,689 | +£73,893 |
| 2018 | 10 | £2,999,263 | £299,926 | +£2,894,063 |
| 2019 | 11 | £4,436,433 | £403,312 | +£1,437,170 |
| 2020 | 14 | £6,929,634 | £494,974 | +£2,493,201 |
| 2021 | 14 | £6,711,442 | £479,389 | £-218,192 |
| 2022 | 15 | £6,211,032 | £414,069 | £-500,410 |
| 2023 | 15 | £5,409,655 | £360,644 | £-801,377 |
| 2024 | 15 | £5,296,958 | £353,131 | £-112,697 |
| 2025 | 15 | £5,589,904 | £372,660 | +£292,946 |

**Peak portfolio CLV: 2020 (£6,929,634)** | **Earliest/lowest: 2016 (£31,307)**
**Largest YoY gain: 2018 (+£2,894,063)**
**Largest YoY fall: 2023 (£-801,377)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | 51.2% | — | — | — | — |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | 35.8% | +£333,275.90 | +£107,460.46 | +£108,889.99 | +£116,925.46 |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | 44.0% | +£252,322.49 | +£61,745.30 | +£51,194.57 | +£139,382.63 |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | 42.8% | +£1,044,499.09 | +£323,437.66 | +£281,360.24 | +£439,701.19 |
| 2020 | £1,857,054.07 | £431,617.21 | £631,853.59 | £793,583.26 | 42.7% | +£211,601.96 | £-64,622.74 | +£186,516.55 | +£89,708.15 |
| 2021 | £2,415,732.82 | £971,906.32 | £679,550.34 | £764,276.16 | 31.6% | +£558,678.76 | +£540,289.11 | +£47,696.75 | £-29,307.11 |
| 2022 | £4,241,597.52 | £2,388,594.70 | £801,304.69 | £1,051,698.13 | 24.8% | +£1,825,864.70 | +£1,416,688.38 | +£121,754.35 | +£287,421.98 |
| 2023 | £3,473,229.08 | £1,638,941.42 | £877,218.22 | £957,069.44 | 27.6% | £-768,368.45 | £-749,653.28 | +£75,913.53 | £-94,628.70 |
| 2024 | £3,000,893.30 | £931,709.77 | £809,903.10 | £1,259,280.43 | 42.0% | £-472,335.78 | £-707,231.65 | £-67,315.13 | +£302,210.99 |
| 2025 | £1,228,431.44 | £452,080.99 | £256,996.72 | £519,353.73 | 42.3% | £-1,772,461.85 | £-479,628.78 | £-552,906.38 | £-739,926.69 |

**Best GM year: 2016 (51.2%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Net Margin Bridge (Year-on-Year Attribution)

Decomposes each year's net margin change into: gross margin movement, bad debt, capital costs, policy levies, network costs.

| Transition | Net Δ | Gross Δ | Bad Debt Δ | Capital Δ | Policy Δ | Network Δ | Portfolio | Driver | RAG |
|-----------|-------|---------|-----------|---------|---------|---------|---------|--------|-----|
| 2016→2017 | +£30,897 | +£116,423 | +£300 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£70,119 | +£139,295 | -£31 | -£255 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£131,733 | +£439,496 | -£256 | -£781 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£104,921 | +£89,757 | +£648 | +£346 | -£162,654 | -£33,019 | +2 | policy levies | RED |
| 2020→2021 | -£53,130 | -£28,818 | -£272 | -£3,640 | -£19,033 | -£1,367 | -5 | gross margin | RED |
| 2021→2022 | +£263,861 | +£287,392 | +£94 | -£7,663 | -£1,158 | -£14,803 | +1 | gross margin | GREEN |
| 2022→2023 | -£193,054 | -£94,424 | +£119 | +£3,244 | -£70,703 | -£31,291 | -2 | gross margin | RED |
| 2023→2024 | +£202,088 | +£302,957 | -£0 | +£505 | -£100,728 | -£647 | +0 | gross margin | GREEN |
| 2024→2025 | -£227,341 | -£739,964 | -£0 | +£3,870 | +£382,030 | +£126,723 | -3 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£227,341)** | **Best transition: 2021→2022 (+£263,861)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Payment Portfolio Health (P2: Billing Infra)

Year-by-year bad debt rate and high-churn-risk customer concentration.

| Year | Bad Debt | Bad Debt Rate | At-Risk Customers | At-Risk % | Trend | RAG |
|------|----------|--------------|-----------------|----------|-------|-----|
| 2016 | £602 | 5.78% | 0/4 | 0% | — STABLE | RED |
| 2017 | £302 | 0.13% | 0/11 | 0% | ↓ IMPROVING | GREEN |
| 2018 | £332 | 0.08% | 1/12 | 8% | ↓ IMPROVING | GREEN |
| 2019 | £589 | 0.05% | 3/13 | 23% | ↓ IMPROVING | GREEN |
| 2020 | £-60 | -0.00% | 5/15 | 33% | ↓ IMPROVING | AMBER |
| 2021 | £213 | 0.01% | 4/12 | 33% | ↑ DETERIORATING | AMBER |
| 2022 | £119 | 0.00% | 9/12 | 75% | ↓ IMPROVING | RED |
| 2023 | £-0 | -0.00% | 9/11 | 82% | ↓ IMPROVING | RED |
| 2024 | £-0 | -0.00% | 3/11 | 27% | ↑ DETERIORATING | GREEN |
| 2025 | £0 | 0.00% | 2/3 | 67% | ↑ DETERIORATING | RED |

**Worst bad debt year: 2016 (5.78%)** | **Peak at-risk concentration: 2023 (82% of customers)**

> At-risk = churn risk score >30% at year-end. Bad debt rate = written-off bad debt as % of annual revenue. RAG: GREEN <0.75% bad debt and <30% at-risk; RED >1.5% bad debt or >60% at-risk.

## Portfolio Composition (P3: Population Anchoring)

Gross margin share by segment and fuel type. Concentration RAG: GREEN <70% dominant, AMBER 70-90%, RED >90% (single-segment dependency).
Benchmark: balanced UK small supplier targets resi 40-70%, I&C 20-50%, elec 70-90% of gross.

| Year | Resi% | SME% | I&C% | Elec% | Gas% | Dominant | Concentration |
|------|-------|------|------|-------|------|---------|--------------|
| 2016 | 60% | 40% | 0% | 88% | 12% | Residential | GREEN |
| 2017 | 5% | 3% | 92% | 99% | 1% | I&C | RED |
| 2018 | 2% | 1% | 96% | 99% | 1% | I&C | RED |
| 2019 | 1% | 1% | 98% | 89% | 11% | I&C | RED |
| 2020 | 1% | 1% | 99% | 90% | 10% | I&C | RED |
| 2021 | 1% | 0% | 99% | 89% | 11% | I&C | RED |
| 2022 | 0% | 0% | 99% | 91% | 9% | I&C | RED |
| 2023 | 1% | 0% | 99% | 87% | 13% | I&C | RED |
| 2024 | 1% | 0% | 99% | 90% | 10% | I&C | RED |
| 2025 | 1% | 0% | 99% | 90% | 10% | I&C | RED |

> **Concentration alert:** I&C dominated gross margin in 2017–2025. Loss of a single large I&C customer has outsized P&L impact. Benchmark: a resilient mixed-book supplier targets no segment >70% of gross margin.

## Shadow Retention Strategy (P4: Shadow Ops)

Counterfactual: what if the company had offered retention to ALL renewal customers (not just those above the 30% threshold)?
Shadow discount: 8% off next term. Assumes P(accept) = (1 - churn\_estimate) x 90%.

| Year | No-Offer Churns | Margin Lost | Shadow Retained | Offer Cost | Shadow Net Gain |
|------|----------------|------------|----------------|-----------|----------------|
| 2020 | 3 | £2,643 | £2,003 | £174 | +£1,829 |
| 2022 | 1 | £237 | £184 | £16 | +£168 |
| 2024 | 2 | £3,330 | £2,119 | £184 | +£1,934 |

**Total opportunity cost vs actual: +£3,932 net** (gross £6,209 margin lost; £374 offer cost if all retained).

> The shadow strategy net gain is small because all no-offer churns were residential customers with low margins. I&C customers (large margins) already received retention offers — the current threshold strategy is near-optimal for the existing portfolio composition.

## Ofgem FRA Regulatory Capital Ratio (Phase NZ)

Equity / (annual revenue ÷ 12). Ofgem FRA minimum: ≥ 1x monthly revenue.
Sector best practice: ≥ 6x (GREEN). Early warning: < 3x (AMBER). Non-compliant: < 1x (RED).
Real-world context: Bulb 2021 collapse at ~-0.01x; Igloo 2021 ~0.07x.

| Year | Equity | Monthly Rev | FRA Ratio | RAG | Compliant |
|------|--------|-------------|-----------|-----|-----------|
| 2016 | £2,473,105.03 | £1,279.55 | 1932.8x | ✓ GREEN | Yes |
| 2017 | £2,587,816.11 | £29,052.54 | 89.1x | ✓ GREEN | Yes |
| 2018 | £2,834,806.33 | £50,079.42 | 56.6x | ✓ GREEN | Yes |
| 2019 | £3,498,583.14 | £137,121.01 | 25.5x | ✓ GREEN | Yes |
| 2020 | £4,242,880.60 | £154,754.51 | 27.4x | ✓ GREEN | Yes |
| 2021 | £4,944,761.74 | £201,311.07 | 24.6x | ✓ GREEN | Yes |
| 2022 | £5,884,048.35 | £353,466.46 | 16.6x | ✓ GREEN | Yes |
| 2023 | £6,740,814.43 | £289,435.76 | 23.3x | ✓ GREEN | Yes |
| 2024 | £7,913,978.26 | £250,074.44 | 31.6x | ✓ GREEN | Yes |
| 2025 | £8,384,634.92 | £102,369.29 | 81.9x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.6x (equity £5,884,048.35 vs monthly revenue £353,466.46). RAG: GREEN.
**Strongest year:** 2016 — 1932.8x.

## I&C Broker / TPI Commission (Phase OA)

I&C customers procure electricity via energy brokers. Commission rate: £1.5/MWh (0.15p/kWh — standard for large I&C per Ofgem TPI register data).

| Year | Deals | Consumption (MWh) | Commission £ |
|------|-------|-------------------|--------------|
| 2016 | 0 | 0 | £0 |
| 2017 | 1 | 1,983 | £2,974 |
| 2018 | 2 | 2,986 | £4,478 |
| 2019 | 3 | 6,987 | £10,481 |
| 2020 | 4 | 10,016 | £15,024 |
| 2021 | 4 | 9,907 | £14,860 |
| 2022 | 4 | 9,868 | £14,802 |
| 2023 | 4 | 9,883 | £14,825 |
| 2024 | 4 | 9,929 | £14,894 |
| 2025 | 4 | 4,239 | £6,358 |
|------|-------|-------------------|--------------|
| **Total** | **30** | | **£98,698** |

**Total broker commission 2016–2025:** £98,698

_Note: This cost was previously unmodelled — I&C gross margin was overstated by this amount._
## Elexon Settlement Reconciliation Exposure (Phase OB)

UK electricity suppliers receive reconciliation adjustments via R1/R2/R3/RF runs (1, 3, 5, 28 months after delivery). 60% resolved at R1; 3% tail into RF.
HH meters (I&C): ±0.5% variance. Non-HH (resi/SME): ±4%. Portfolio: ~90% HH.
Zero-mean: adjustments go both ways. Crisis years bias toward supplier credit.

| Year | Revenue £ | Pool Outstanding £ | Max Adverse £ | RAG | Crisis |
|------|-----------|---------------------|---------------|-----|--------|
| 2016 | £15,354.61 | £5,706.80 | £48.51 | ✓ GREEN |  |
| 2017 | £348,630.52 | £129,574.34 | £1,101.38 | ✓ GREEN |  |
| 2018 | £600,953.01 | £223,354.20 | £1,898.51 | ✓ GREEN |  |
| 2019 | £1,645,452.10 | £611,559.70 | £5,198.26 | ✓ GREEN |  |
| 2020 | £1,857,054.07 | £690,205.09 | £5,866.74 | ✓ GREEN |  |
| 2021 | £2,415,732.82 | £897,847.36 | £7,631.70 | ✓ GREEN | CREDIT EXPECTED |
| 2022 | £4,241,597.52 | £1,576,460.41 | £13,399.91 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,473,229.08 | £1,290,883.47 | £10,972.51 | ✓ GREEN |  |
| 2024 | £3,000,893.30 | £1,115,332.01 | £9,480.32 | ✓ GREEN |  |
| 2025 | £1,228,431.44 | £456,567.02 | £3,880.82 | ✓ GREEN |  |

**Peak reconciliation exposure:** 2022 — max adverse £13,400 (4.5 months weighted tail).

_Note: Outstanding pool ≈ current-year revenue × (weighted outstanding months ÷ 12)._
_Max adverse = pool × blended variance rate (0.5% HH + 4% non-HH, portfolio-weighted)._
## Ofgem Supply Licence Health (Phase OC)

Annual licence health checks: customer base, net assets, liquidity, bad debt.
Breach triggers board escalation and Ofgem notification under SLC 0.
WATCH = within 20% of threshold. BREACH = threshold crossed.

| Year | Customers | Net Assets | Treasury | Cash Wks | Bad Debt % | Overall |
|------|-----------|------------|----------|----------|------------|---------|
| 2016 | 13 | £2,473,105.03 | £2,467,433.90 | 35675w | 5.78% | ✗ BREACH |
| 2017 | 14 | £2,587,816.11 | £2,498,375.34 | 1170w | 0.13% | ✗ BREACH |
| 2018 | 15 | £2,834,806.33 | £2,487,546.78 | 749w | 0.08% | ✗ BREACH |
| 2019 | 17 | £3,498,583.14 | £2,611,521.98 | 274w | 0.05% | ✗ BREACH |
| 2020 | 19 | £4,242,880.60 | £2,923,396.55 | 352w | -0.00% | ✗ BREACH |
| 2021 | 14 | £4,944,761.74 | £2,956,666.57 | 158w | 0.01% | ✗ BREACH |
| 2022 | 15 | £5,884,048.35 | £3,161,597.39 | 69w | 0.00% | ✗ BREACH |
| 2023 | 13 | £6,740,814.43 | £3,382,344.22 | 107w | -0.00% | ✗ BREACH |
| 2024 | 13 | £7,913,978.26 | £3,777,721.76 | 211w | -0.00% | ✗ BREACH |
| 2025 | 10 | £8,384,634.92 | £3,829,410.41 | 440w | 0.00% | ✗ BREACH |

**BREACH years:** 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 — board escalation required.

_Note: Complaints from contact model avg_complaint_probability. Customer count <50 triggers Ofgem viability review — small-portfolio years will show WATCH._
## Ofgem SLC Compliance Scorecard (Phase OD)

10 compliance domains per year, derived from simulation outputs.
G = GREEN (compliant), A = AMBER (watch), R = RED (breach).

| Domain | SLC Ref | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|--------|---------|------|------|------|------|------|------|------|------|------|------|
| Governance | SLC 0-9 | G | G | G | G | G | G | G | G | G | G |
| Billing/Metering | SLC 10-14 | G | G | G | G | G | G | A | G | G | A |
| Payment/Debt | SLC 15-19 | R | G | G | G | G | G | G | G | G | G |
| Information | SLC 20-24 | G | G | G | G | G | G | G | G | G | G |
| Complaints | SLC 25-29 / Ofgem Time to Fix rules | A | A | A | A | A | A | R | R | A | R |
| Vulnerable Cust | SLC 30-35 / PSR | G | G | G | G | G | G | G | G | G | G |
| Tariff/Cap | SLC 36-40 / Default Tariff Cap | G | G | G | G | G | G | G | G | G | G |
| Environmental | SLC 41-50 / RO, CfD, EE obligation | G | G | G | G | G | G | G | G | G | G |
| Network/BSC | SLC 51-60 / BSC obligations | G | G | G | G | G | G | G | G | G | G |
| Financial Res. | SLC 4C / SFR Decision 2023 | G | G | G | G | G | G | G | G | G | G |
| **Overall** |  | R | A | A | A | A | A | R | R | A | R |

**Breach years (RED):** 2016, 2022, 2023, 2025
**Watch years (AMBER):** 2017, 2018, 2019, 2020, 2021, 2024

_Note: Vulnerable customers, tariff/cap, and environmental domains defaulted to GREEN_
_(these are modelled as compliant; detailed SLC breach simulation not yet implemented)._
## Ofgem Annual Supply Return (Phase OE)

UK suppliers must file annual supply returns to Ofgem. Filed by 31 March of the following year.

| Year | Submitted | Customers (R/SME/I&C) | Elec GWh | Gas GWh | Bad Debt/Cust |
|------|-----------|----------------------|----------|---------|---------------|
| 2016 | Yes | 13/13/13 | 0.1 | 0.0 | £46 |
| 2017 | Yes | 14/14/14 | 1.5 | 0.1 | £22 |
| 2018 | Yes | 15/15/15 | 2.9 | 0.1 | £22 |
| 2019 | Yes | 17/17/17 | 7.1 | 2.8 | £35 |
| 2020 | Yes | 19/19/19 | 7.3 | 2.4 | £-3 |
| 2021 | Yes | 14/14/14 | 9.6 | 6.0 | £15 |
| 2022 | Yes | 15/15/15 | 19.0 | 11.8 | £8 |
| 2023 | Yes | 13/13/13 | 15.3 | 5.9 | £-0 |
| 2024 | Yes | 13/13/13 | 12.8 | 5.4 | £-0 |
| 2025 | Yes | 10/10/10 | 5.6 | 2.6 | £0 |

**All 10 annual returns filed** — full compliance 2016–2025.

_Note: WHD and GSOP metrics default to zero (not yet modelled in detail)._
_Volume GWh estimated from revenue at average unit rate proxies (£150/MWh elec, £50/MWh gas)._
## GSOP Obligations (Phase OF)

Guaranteed Standards of Performance — GBP 30 per breach (Ofgem-mandated).

No GSOP obligations triggered in 2016-2025 window.
_Small portfolio with low complaint and churn volumes falls below estimated trigger thresholds._
## Renewable Obligation (RO) Cost Observatory

UK suppliers must surrender ROCs (or pay buy-out price) by 1 September each year.
ROC buy-out cost is the maximum supplier exposure; ROC market purchases reduce actual cost.

| Year | Elec MWh | Obligation Level | ROCs Required | Buy-out Price | Buy-out Cost |
|------|----------|-----------------|--------------|--------------|-------------|
| 2016 | 74.5 | 0.317 ROC/MWh | 23.6 | £43.30 | £1,023 |
| 2017 | 2,082.1 | 0.334 ROC/MWh | 695.4 | £44.77 | £31,134 |
| 2018 | 3,086.0 | 0.342 ROC/MWh | 1,055.4 | £46.43 | £49,003 |
| 2019 | 7,088.2 | 0.351 ROC/MWh | 2,488.0 | £47.22 | £117,481 |
| 2020 | 10,111.6 | 0.358 ROC/MWh | 3,620.0 | £48.78 | £176,581 |
| 2021 | 9,988.0 | 0.364 ROC/MWh | 3,635.6 | £50.80 | £184,690 |
| 2022 | 9,947.8 | 0.370 ROC/MWh | 3,680.7 | £52.88 | £194,635 |
| 2023 | 9,965.0 | 0.376 ROC/MWh | 3,746.8 | £54.35 | £203,641 |
| 2024 | 9,994.0 | 0.382 ROC/MWh | 3,817.7 | £56.19 | £214,517 |
| 2025 | 4,268.1 | 0.389 ROC/MWh | 1,660.3 | £58.10 | £96,463 |
| **Total** | **66,605.3** | | | | **£1,269,168** |

RO cost as % of total revenue (2016-2025): **6.7%** (industry benchmark 5-10%)

> Note: actual RO cost depends on ROC market prices. Buy-out price is the regulatory ceiling.
## Feed-in Tariff (FiT) Levelisation Levy

Ofgem FiT levelisation redistributes FiT payment obligations across all licensed suppliers
(proportional to electricity supplied). FiT scheme closed to new applicants 2019-03-31.

| Year | Elec MWh | Levy Rate (GBP/MWh) | FiT Levy Cost |
|------|----------|---------------------|--------------|
| 2016 | 74.5 | GBP8.36 | GBP622.60 |
| 2017 | 2,082.1 | GBP9.19 | GBP19,134.80 |
| 2018 | 3,086.0 | GBP9.40 | GBP29,008.53 |
| 2019 | 7,088.2 | GBP9.45 | GBP66,983.17 |
| 2020 | 10,111.6 | GBP0.00 (scheme closed) | NIL |
| 2021 | 9,988.0 | GBP0.00 (scheme closed) | NIL |
| 2022 | 9,947.8 | GBP0.00 (scheme closed) | NIL |
| 2023 | 9,965.0 | GBP0.00 (scheme closed) | NIL |
| 2024 | 9,994.0 | GBP0.00 (scheme closed) | NIL |
| 2025 | 4,268.1 | GBP0.00 (scheme closed) | NIL |
| **Total** | | | **GBP115,749.10** |

FiT levy as % of total revenue (levy years 2016-2019): **0.6%** (industry benchmark ~1-2%)

> FiT levy ended 2019-20. Post-2019 cost is NIL as levelisation rates fell to zero.
## Climate Change Levy (CCL) Observatory

CCL is charged on business energy consumption and remitted to HMRC quarterly.
Residential customers are fully exempt. I&C customers pay at HMRC annual rates.
CCL is a pass-through: collected from customers, remitted to HMRC (no net P&L impact).

| Year | Elec kWh | Elec Rate (p/kWh) | CCL Elec | Gas kWh | Gas Rate | CCL Gas | Total CCL |
|------|----------|------------------|----------|---------|----------|---------|----------|
| 2016 | 0 | 0.554p | GBP0.00 | 0 | 0.195p | GBP0.00 | GBP0.00 |
| 2017 | 1,982,966 | 0.568p | GBP11,263.25 | 0 | 0.198p | GBP0.00 | GBP11,263.25 |
| 2018 | 2,985,506 | 0.583p | GBP17,405.50 | 0 | 0.203p | GBP0.00 | GBP17,405.50 |
| 2019 (*) | 6,987,285 | 0.847p | GBP59,182.30 | 4,999,959 | 0.339p | GBP16,949.86 | GBP76,132.16 |
| 2020 | 10,016,266 | 0.811p | GBP81,231.91 | 5,015,381 | 0.406p | GBP20,362.45 | GBP101,594.36 |
| 2021 | 9,906,804 | 0.775p | GBP76,777.73 | 4,999,959 | 0.465p | GBP23,249.81 | GBP100,027.54 |
| 2022 | 9,868,318 | 0.775p | GBP76,479.47 | 4,999,959 | 0.465p | GBP23,249.81 | GBP99,729.28 |
| 2023 | 9,883,290 | 0.775p | GBP76,595.50 | 4,999,959 | 0.465p | GBP23,249.81 | GBP99,845.31 |
| 2024 | 9,929,315 | 0.775p | GBP76,952.19 | 5,015,381 | 0.465p | GBP23,321.52 | GBP100,273.71 |
| 2025 | 4,238,894 | 0.775p | GBP32,851.43 | 2,224,893 | 0.465p | GBP10,345.75 | GBP43,197.18 |
| **Total** | | | | | | | **GBP649,468.29** |

(*) 2019: electricity CCL +45% (0.583->0.847p/kWh), gas +67% (0.203->0.339p/kWh) -- Budget 2018 carbon tax shift.

> Quarterly HMRC remittance obligation per CCLQuarterlyReturn. Pass-through: no net supplier P&L impact.
## Warm Home Discount (WHD) Liability Observatory

WHD is mandatory for suppliers with 150,000+ domestic customers.
Eligible customers receive a GBP 140-150 rebate applied to their electricity bill.

| Year | Domestic Customers | WHD Threshold | Status | Rebate/Customer | Liability |
|------|-------------------|--------------|--------|----------------|---------|
| 2016 | 13 | 150,000 | OK (exempt) | N/A | NIL |
| 2017 | 13 | 150,000 | OK (exempt) | N/A | NIL |
| 2018 | 13 | 150,000 | OK (exempt) | N/A | NIL |
| 2019 | 13 | 150,000 | OK (exempt) | N/A | NIL |
| 2020 | 14 | 150,000 | OK (exempt) | N/A | NIL |
| 2021 | 9 | 150,000 | OK (exempt) | N/A | NIL |
| 2022 | 10 | 150,000 | OK (exempt) | N/A | NIL |
| 2023 | 8 | 150,000 | OK (exempt) | N/A | NIL |
| 2024 | 8 | 150,000 | OK (exempt) | N/A | NIL |
| 2025 | 5 | 150,000 | OK (exempt) | N/A | NIL |

> Portfolio is primarily I&C. Domestic customer count is far below WHD threshold -- no obligation to participate.
> If domestic portfolio grows to 150,000+, WHD registration with Ofgem becomes mandatory.
## Energy Company Obligation (ECO) Observatory

ECO requires suppliers with 150,000+ domestic customers to fund home energy efficiency upgrades.
Phases: ECO2 (2015-2018, GBP3.20/MWh), ECO3 (2018-2022, GBP4.50/MWh), ECO4 (2022-2026, GBP6.80/MWh).

| Year | ECO Phase | Rate (GBP/MWh) | Domestic Cust | Status | Counterfactual Liability |
|------|----------|---------------|--------------|--------|------------------------|
| 2016 | ECO2 | GBP3.20 | 13 | OK (exempt) | GBP0 |
| 2017 | ECO2 | GBP3.20 | 13 | OK (exempt) | GBP7 |
| 2018 | ECO3 | GBP4.50 | 13 | OK (exempt) | GBP18 |
| 2019 | ECO3 | GBP4.50 | 13 | OK (exempt) | GBP49 |
| 2020 | ECO3 | GBP4.50 | 14 | OK (exempt) | GBP56 |
| 2021 | ECO3 | GBP4.50 | 9 | OK (exempt) | GBP72 |
| 2022 | ECO4 | GBP6.80 | 10 | OK (exempt) | GBP192 |
| 2023 | ECO4 | GBP6.80 | 8 | OK (exempt) | GBP157 |
| 2024 | ECO4 | GBP6.80 | 8 | OK (exempt) | GBP136 |
| 2025 | ECO4 | GBP6.80 | 5 | OK (exempt) | GBP56 |

Counterfactual total 2016-2025 (if 150k domestic): **GBP743**

> Actual ECO liability: NIL -- domestic customer count is far below threshold.
> Counterfactual shows obligation rate if portfolio scaled to 150,000 domestic customers.
## Carbon Emissions Reporting Observatory

Scope 2 emissions from customer electricity consumption (UK grid emission intensity).
Scope 1 emissions from gas supply (183g CO2/kWh). Source: DESNZ/National Grid annual fuel mix data.

| Year | Elec MWh | Grid Intensity | Elec CO2 (t) | Gas MWh | Gas CO2 (t) | Total CO2 (t) | Low Carbon % |
|------|----------|---------------|-------------|---------|------------|-------------|-------------|
| 2016 | 0 | 315g/kWh | 0.0 | 0 | 0.0 | 0.0 | 45% |
| 2017 | 2 | 290g/kWh | 0.7 | 0 | 0.0 | 0.7 | 49% |
| 2018 | 4 | 274g/kWh | 1.1 | 0 | 0.1 | 1.2 | 51% |
| 2019 | 11 | 244g/kWh | 2.7 | 1 | 0.2 | 2.9 | 57% |
| 2020 | 12 | 225g/kWh | 2.8 | 1 | 0.2 | 3.0 | 59% (decarbonising) |
| 2021 | 16 | 243g/kWh | 3.9 | 2 | 0.3 | 4.2 | 56% (decarbonising) |
| 2022 | 28 | 237g/kWh | 6.7 | 3 | 0.5 | 7.2 | 57% (decarbonising) |
| 2023 | 23 | 219g/kWh | 5.1 | 2 | 0.4 | 5.5 | 59% (decarbonising) |
| 2024 | 20 | 196g/kWh | 3.9 | 2 | 0.4 | 4.3 | 64% (decarbonising) |
| 2025 | 8 | 175g/kWh | 1.4 | 1 | 0.1 | 1.5 | 68% (decarbonising) |
| **Total** | | | | | | **30.5 t** | |

> Grid emission intensity declining: 2016 ~290g/kWh -> 2025 ~175g/kWh (40% reduction). Carbon disclosure per SECR/ESOS.
## Risk Committee Activity (2016-2025)

Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.

| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |
|------|----------|----------------------|----------------------|-----------------|
| 2016 | 13 | £28 | £9 | 1 |
| 2017 | 12 | £1,005 | £401 | 3 |
| 2022 | 9 | £55,367 | £20,525 | 7 |
| 2023 | 4 | £128,248 | £48,907 | 9 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £128,248 | Unique accounts ever adjusted: 11

**Most frequently adjusted accounts:**
- C1: 22 sessions
- C7: 16 sessions
- C2: 13 sessions
- C5: 12 sessions
- C6: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £11,007.45 | Median churn: 32% | Total portfolio CLV: £8,211,189.69

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC1 | £1,923,108.93 | 29% | 18.1 periods |
| C_IC4 | £1,834,355.42 | 20% | 18.7 periods |
| C6 | £22,613.59 | 26% | 19.4 periods |
| C9 | £11,007.45 | 26% | 17.5 periods |

Quadrant CLV: £3,791,085.39 (46% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £3,353,951.54 | 41% | 18.2 periods |
| C_IC2 | £1,011,104.23 | 32% | 15.9 periods |
| C5 | £11,907.21 | 32% | 18.2 periods |

Quadrant CLV: £4,376,962.98 (53% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C7 | £9,077.23 | 29% | 16.8 periods |
| C3 | £7,335.78 | 11% | 19.7 periods |

Quadrant CLV: £16,413.00 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £10,424.49 | 32% | 16.1 periods |
| C2 | £6,438.04 | 38% | 14.9 periods |
| C1 | £5,355.55 | 38% | 16.6 periods |
| C4 | £4,510.24 | 38% | 20.4 periods |

Quadrant CLV: £26,728.32 (0% of portfolio)

**Board action: CRITICAL quadrant has 3 account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**

## Customer Experience & Service Quality

| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |
|------|----------------|---------------|-------------|---------|------|
| 2016 | 0.829 | 0.047 | 0 | 0 |  |
| 2017 | 0.818 | 0.047 | 0 | 0 |  |
| 2018 | 0.810 | 0.047 | 0 | 0 |  |
| 2019 | 0.824 | 0.047 | 0 | 0 |  |
| 2020 | 0.832 | 0.043 | 2 | 0 |  |
| 2021 | 0.816 | 0.048 | 0 | 0 |  |
| 2022 | 0.783 | 0.058 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.802 | 0.050 | 0 | 0 |  |
| 2024 | 0.805 | 0.048 | 2 | 0 |  |
| 2025 | 0.768 | 0.061 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.3% | **Average billing clarity:** 0.812 | **Average complaint probability:** 0.049

**Acquisition performance:** 4 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2025** (0.768) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

## Bill Shock Analysis

Bill shock events occur when a customer's bill increases >20% vs the prior bill.
Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.

| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |
|------|------------|--------|-------|------------|------|
| 2016 | 19.7% | 31 | 108 | 29% |  |
| 2017 | 16.5% | 50 | 168 | 30% |  |
| 2018 | 16.0% | 60 | 180 | 33% |  |
| 2019 | 17.1% | 66 | 204 | 32% |  |
| 2020 | 14.4% | 52 | 205 | 25% |  |
| 2021 | 24.1% | 47 | 168 | 28% | ELEVATED |
| 2022 | 34.5% | 71 | 160 | 44% | **HIGH** |
| 2023 | 18.2% | 48 | 156 | 31% |  |
| 2024 | 17.1% | 40 | 141 | 28% |  |
| 2025 | 24.8% | 23 | 60 | 38% | ELEVATED |

**Crisis peak: 2022** — 34.5% average shock. Energy crisis drove wholesale costs above locked tariff rates,
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
| 2020 | £238,633.66 | £35,390.59 | £69,453.10 | £56,549.25 | £70,022.90 | £470,049.50 | £124,580.37 |
| 2021 | £246,245.51 | £14,982.00 | £71,202.78 | £49,580.31 | £62,717.48 | £486,078.41 | £122,860.33 |
| 2022 | £256,213.44 | **£-49,738.80** | £70,920.22 | £36,680.77 | £69,110.14 | £482,663.38 | £133,531.30 |
| 2023 | £271,884.09 | £64,772.74 | £71,701.96 | £50,965.78 | £75,106.16 | £548,182.48 | £139,555.43 |
| 2024 | £307,626.36 | £109,933.90 | £72,815.13 | £68,707.47 | £82,562.92 | £643,644.58 | £143,473.05 |
| 2025 | £135,726.90 | £46,949.56 | £31,155.87 | £31,029.39 | £36,151.16 | £281,866.51 | £61,362.58 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.01 (2016) → £281,866.51 (2025). CAGR: 76.4%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £418.71 | £324.29 | £9,021.95 | £1,388.28 | 13.3% | YES |
| 2017 | £31,123.28 | £516.54 | £231,632.96 | £2,660.42 | 1.1% | YES |
| 2018 | £101,321.76 | £436.94 | £432,208.83 | £3,113.94 | 0.7% | YES |
| 2019 | £223,001.61 | £10,489.65 | £1,060,498.38 | £137,766.14 | 11.5% | YES |
| 2020 | £118,081.89 | £10,488.12 | £1,102,223.95 | £121,119.88 | 9.9% | YES |
| 2021 | £65,616.48 | £9,823.20 | £1,437,316.01 | £297,399.17 | 17.1% | YES |
| 2022 | £330,457.12 | £8,843.70 | £2,850,564.76 | £588,329.77 | 17.1% | YES |
| 2023 | £137,287.54 | £8,958.96 | £2,297,437.03 | £297,197.78 | 11.5% | YES |
| 2024 | £337,866.86 | £10,467.35 | £1,919,320.99 | £270,490.62 | 12.4% | YES |
| 2025 | £116,542.95 | £4,449.79 | £838,554.42 | £132,453.71 | 13.6% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £202,013.08 | — | Current strategy |
| EXIT_GAS | £82,480.23 | £-119,532.85 | Remove gas; model elec churn risk |
| REPRICE_GAS | £203,638.21 | £1,625.13 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-1,625.13 | -11.23x | +15.7% |

**Accretive gas accounts:** C1g (£669.14), C2g (£907.09), C3g (£336.46), C_IC3g (£64,510.98) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £64799 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,716,044.53 | £50,044.16 | £1,450,916.53 | 29.0x | Strong |
| I&C gas | £622,647.03 | £0.00 | £64,510.98 | 0.0x | Low return |
| SME electricity | £30,279.16 | £322.08 | £3,854.99 | 12.0x | Moderate |
| resi electricity | £58,481.14 | £646.35 | £6,946.68 | 10.7x | Moderate |
| resi gas | £6,016.94 | £197.67 | £287.56 | 1.5x | Low return |

## Portfolio Concentration Risk

Revenue concentration analysis across 20 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2247** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,324,751.35 (98.6% of total positive margin)
- resi: £61,271.04 (1.0% of total positive margin)
- SME: £28,719.52 (0.4% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,870,436.44 | 29.2% | 4% | £75,378.59 |
| C_IC3 | I&C | £1,821,654.82 | 28.4% | 20% | £369,613.76 |
| C_IC4 | I&C | £1,103,966.75 | 17.2% | 0% | £0.00 |
| C_IC2 | I&C | £906,113.37 | 14.1% | 4% | £33,254.36 |
| C_IC3g | I&C | £622,579.96 | 9.7% | 0% | £0.00 |

**Concentration Risk Warning:**
- I&C segment accounts for 98.6% of total portfolio margin
- Resi and SME segments are effectively margin-neutral at portfolio scale
- A single large I&C departure would remove 14-29% of all margin
- Board action: diversify acquisition pipeline toward profitable resi/SME to reduce I&C dependency

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 113 renewal(s) (25 gas) based on recent portfolio-wide margin rates: 61 surcharge(s), 52 discount(s).

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
| C2g | gas | 2020-03-31 | 18.7% | -5.0% | £22.80/MWh | £21.66/MWh |
| C6 | electricity | 2020-03-31 | -47.4% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -16.3% | +12.1% | £125.12/MWh | £140.31/MWh |
| C_IC1 | electricity | 2020-03-31 | 20.1% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 16.5% | -4.3% | £113.43/MWh | £108.60/MWh |
| C9 | electricity | 2020-06-30 | 16.5% | -4.3% | £113.43/MWh | £108.60/MWh |
| C4 | electricity | 2020-09-30 | 11.1% | -1.6% | £124.42/MWh | £122.47/MWh |
| C4g | gas | 2020-09-30 | 20.7% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 9.7% | -0.8% | £133.55/MWh | £132.43/MWh |
| C5 | electricity | 2020-12-30 | 2.7% | +2.6% | £133.55/MWh | £137.07/MWh |
| C7 | electricity | 2020-12-30 | 2.7% | +2.6% | £133.55/MWh | £137.07/MWh |
| C_IC3 | electricity | 2020-12-31 | -4.0% | +6.0% | £50.65/MWh | £53.68/MWh |
| C_IC3g | gas | 2020-12-31 | 14.7% | -3.3% | £20.05/MWh | £19.38/MWh |
| C2 | electricity | 2021-03-31 | -21.5% | +14.8% | £175.90/MWh | £201.84/MWh |
| C2g | gas | 2021-03-31 | 7.2% | +0.4% | £36.20/MWh | £36.34/MWh |
| C6 | electricity | 2021-03-31 | -16.2% | +12.1% | £175.90/MWh | £197.14/MWh |
| C8 | electricity | 2021-03-31 | -11.9% | +9.9% | £175.90/MWh | £193.39/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.6% | +6.3% | £138.90/MWh | £147.64/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.9% | +3.5% | £113.97/MWh | £118.02/MWh |
| C9 | electricity | 2021-06-30 | 1.1% | +3.5% | £170.38/MWh | £176.29/MWh |
| C4 | electricity | 2021-09-30 | -2.4% | +5.2% | £205.15/MWh | £215.85/MWh |
| C4g | gas | 2021-09-30 | 6.8% | +0.6% | £53.99/MWh | £54.31/MWh |
| C1_2 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.70/MWh |
| C7 | electricity | 2021-12-30 | -4.4% | +6.2% | £311.83/MWh | £331.12/MWh |
| C_IC3 | electricity | 2021-12-31 | -26.2% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -22.1% | +15.0% | £109.48/MWh | £125.90/MWh |
| C2 | electricity | 2022-03-31 | -17.6% | +12.8% | £361.95/MWh | £408.34/MWh |
| C6 | electricity | 2022-03-31 | -16.8% | +12.4% | £361.95/MWh | £406.87/MWh |
| C8 | electricity | 2022-03-31 | 5.1% | +1.4% | £361.95/MWh | £367.15/MWh |
| C_IC2 | electricity | 2022-04-30 | -10.3% | +9.2% | £269.81/MWh | £294.54/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.9% | +7.4% | £239.42/MWh | £257.21/MWh |
| C9 | electricity | 2022-06-30 | 4.4% | +1.8% | £255.09/MWh | £259.70/MWh |
| C4 | electricity | 2022-09-30 | 7.3% | +0.4% | £404.86/MWh | £406.35/MWh |
| C4g | gas | 2022-09-30 | -19.2% | +13.6% | £183.79/MWh | £208.78/MWh |
| C1_2 | electricity | 2022-12-30 | 9.0% | -0.5% | £266.73/MWh | £265.45/MWh |
| C7 | electricity | 2022-12-30 | -2.8% | +5.4% | £266.73/MWh | £281.17/MWh |
| C_IC3 | electricity | 2022-12-31 | -13.8% | +10.9% | £168.36/MWh | £186.70/MWh |
| C_IC3g | gas | 2022-12-31 | -37.8% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -11.2% | +9.6% | £319.17/MWh | £349.87/MWh |
| C6 | electricity | 2023-03-31 | -0.2% | +4.1% | £319.17/MWh | £332.35/MWh |
| C8 | electricity | 2023-03-31 | 6.9% | +0.5% | £319.17/MWh | £320.88/MWh |
| C_IC2 | electricity | 2023-05-30 | -22.1% | +15.0% | £171.46/MWh | £197.18/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.2% | +12.6% | £163.19/MWh | £183.71/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.09/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.02/MWh |
| C4g | gas | 2023-09-30 | -38.6% | +15.0% | £47.83/MWh | £55.00/MWh |
| C1_2 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C7 | electricity | 2023-12-30 | 26.3% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 22.4% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -10.0% | +9.0% | £51.89/MWh | £56.57/MWh |
| C2_2 | electricity | 2024-03-30 | 14.7% | -3.3% | £207.71/MWh | £200.79/MWh |
| C6 | electricity | 2024-03-30 | 9.5% | -0.7% | £207.71/MWh | £206.16/MWh |
| C8 | electricity | 2024-03-30 | 9.5% | -0.7% | £207.71/MWh | £206.16/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.1% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.5% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C1_2 | electricity | 2024-12-29 | 0.4% | +3.8% | £243.79/MWh | £253.01/MWh |
| C7 | electricity | 2024-12-29 | 22.6% | -5.0% | £243.79/MWh | £231.60/MWh |
| C_IC3 | electricity | 2024-12-30 | 14.4% | -3.2% | £116.37/MWh | £112.67/MWh |
| C_IC3g | gas | 2024-12-30 | -9.4% | +8.7% | £50.47/MWh | £54.85/MWh |
| C2_2 | electricity | 2025-03-30 | 4.8% | +1.6% | £284.89/MWh | £289.53/MWh |
| C8 | electricity | 2025-03-30 | 6.5% | +0.8% | £284.89/MWh | £287.10/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **6** | Blind misses: **6** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 0 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £6,209.20 | deliberate: £0.00 | total: £6,209.20

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.08 | 0.06 | No | £585.39 |
| C1 | 2020-12-30 | Blind miss | 0.07 | 0.22 | No | £415.17 |
| C5 | 2020-12-30 | Blind miss | 0.09 | 0.27 | No | £1,641.98 |
| C2 | 2022-03-31 | Blind miss | 0.06 | 0.05 | No | £236.63 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.19 | No | £2,861.16 |
| C4 | 2024-09-29 | Blind miss | 0.14 | 0.14 | No | £468.87 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £136,457.01 | £64,510.98 | £200,967.99 | Yes |
| C2+C2g | £179.69 | £907.09 | £1,086.77 | Yes |
| C1+C1g | £368.25 | £669.14 | £1,037.38 | Yes |
| C3+C3g | £16.48 | £336.46 | £352.95 | Yes |
| C4+C4g | £193.11 | £-1,625.13 | £-1,432.02 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £64,798.54.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,526,516.74 across 20 billing accounts. Revenue: £14,030,698.98.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,123,591.82 | £1,874,654.56 | £18,414.15 | £846,420.81 | 27.1% |
| 2 | C_IC2 | fixed | £1,525,272.01 | £909,831.55 | £8,527.57 | £435,818.06 | 28.6% |
| 3 | C_IC3 | pass_through | £4,629,753.36 | £1,824,873.15 | £23,102.44 | £136,457.01 | 2.9% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £64,510.98 | 3.5% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £32,220.65 | 1.2% |
| 6 | C6 | fixed | £38,937.40 | £22,450.89 | £264.32 | £4,240.95 | 10.9% |
| 7 | C8 | fixed | £21,686.87 | £12,467.00 | £134.90 | £2,328.43 | 10.7% |
| 8 | C9 | fixed | £20,243.67 | £12,708.16 | £131.43 | £2,239.92 | 11.1% |
| 9 | C2_2 | fixed | £10,297.47 | £5,489.51 | £67.89 | £1,551.38 | 15.1% |
| 10 | C2g | fixed | £3,849.77 | £2,019.21 | £21.85 | £907.09 | 23.6% |
| 11 | C1g | fixed | £2,436.42 | £1,355.24 | £15.79 | £669.14 | 27.5% |
| 12 | C1_2 | fixed | £11,623.15 | £5,656.27 | £81.60 | £641.48 | 5.5% |
| 13 | C1 | fixed | £3,497.52 | £2,293.73 | £14.09 | £368.25 | 10.5% |
| 14 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £336.46 | 12.5% |
| 15 | C4 | fixed | £6,274.43 | £3,314.79 | £37.48 | £193.11 | 3.1% |
| 16 | C2 | fixed | £5,114.40 | £3,410.31 | £24.74 | £179.69 | 3.5% |
| 17 | C3 | fixed | £3,628.72 | £2,388.84 | £14.77 | £16.48 | 0.5% |
| 18 | C5 | fixed | £12,492.84 | £7,828.28 | £57.77 | £-385.96 | -3.1% |
| 19 | C7 | fixed | £21,726.75 | £10,752.54 | £139.44 | £-572.04 | -2.6% |
| 20 | C4g | fixed | £10,370.30 | £1,343.97 | £144.75 | £-1,625.13 | -15.7% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,030,699 | 100.0% |
| Wholesale cost | -£7,597,230 | 54.1% |
| **Gross supply margin** | **£6,433,469** | **45.9%** |
| Policy + Network costs | -£4,855,742 | 34.6% |
| Capital cost | -£51,210 | 0.4% |
| **Net supply margin** | **£1,526,517** | **10.9%** |

> *The ledger's `net_margin_gbp` (£6,396,073) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,023,256 | 47.5% | 12.1% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 3.5% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £51,430 | 58.9% | 7.5% | CMA 3-8% | ✓ |
| resi/elec | £82,172 | 57.6% | 5.8% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £19,340 | 31.1% | 1.5% | Ofgem CMA 2-4% | ✓ |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: PASS** — all segments within benchmarks.
## Transaction Log

Total events: 3,379,928

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 4 |
| bad_debt_event | 1,550 |
| billing_event | 1,550 |
| capital_charge_event | 1,627,812 |
| cost_to_serve_event | 114 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,550 |
| payment_received_event | 1,550 |
| settlement_event | 1,744,134 |
| vat_remittance_event | 1,550 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £22,567,290.38 |
|   Less: VAT remitted to HMRC | (£3,739,961.91) |
| = Revenue (ex-VAT) | £18,827,328.47 |
| Less: non-commodity pass-through | (£4,782,814.97) |
| Wholesale cost (settlement events) | (£7,597,230.17) |
| Gross margin | £6,447,283.33 |
| Capital charges | (£51,210.26) |
| Net margin | £6,396,073.07 |

_Cash reconciliation: of £22,567,290.38 billed, bad debt of £451,468.98 was written off, leaving £22,115,821.40 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £9,684,566.00._

| Acquisition spend | (£862.50) |
| Fixed overhead | (£5,700.00) |
| Cost to serve | (£18,726.90) |
| Operating net margin | £6,370,783.67 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | £234.62 | £1,310.70 | £6,468.81 (42.1%) |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | £7,077.55 | £8,807.01 | £114,711.08 (32.9%) |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | £13,426.53 | £15,655.65 | £246,990.22 (41.1%) |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | £35,049.84 | £37,788.99 | £663,776.82 (40.3%) |
| 2020 | £1,857,054.07 | £431,617.21 | £631,853.59 | £793,583.26 | £43,655.18 | £47,322.99 | £744,297.46 (40.1%) |
| 2021 | £2,415,732.82 | £971,906.32 | £679,550.34 | £764,276.16 | £53,730.40 | £56,792.69 | £701,881.14 (29.1%) |
| 2022 | £4,241,597.52 | £2,388,594.70 | £801,304.69 | £1,051,698.13 | £96,085.33 | £99,146.33 | £939,286.61 (22.1%) |
| 2023 | £3,473,229.08 | £1,638,941.42 | £877,218.22 | £957,069.44 | £87,222.22 | £90,282.66 | £856,766.08 (24.7%) |
| 2024 | £3,000,893.30 | £931,709.77 | £809,903.10 | £1,259,280.43 | £73,225.58 | £76,600.60 | £1,173,163.83 (39.1%) |
| 2025 | £1,228,431.44 | £452,080.99 | £256,996.72 | £519,353.73 | £41,761.72 | £43,050.76 | £470,656.66 (38.3%) |
| **Total** | **£18,827,328.47** | | | | | | **£5,917,998.70 (31.4%)** |

**Best year:** 2024 — net £1,173,163.83 (39.1% margin)
**Worst year:** 2016 — net £6,468.81 (42.1% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,384,634.92 |
| Trade Receivables | £-0.00 |
| **Total Assets** | **£8,384,634.92** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,917,998.70 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,354.61 | +4.7% | £6,592.99 | £6,468.81 | -1.9% | GREEN |
| 2017 | £16,138.86 | £348,630.52 | +2060.2% | £7,252.29 | £114,711.08 | +1481.7% | RED |
| 2018 | £386,623.75 | £600,953.01 | +55.4% | £128,424.00 | £246,990.22 | +92.3% | RED |
| 2019 | £675,851.95 | £1,645,452.10 | +143.5% | £281,335.50 | £663,776.82 | +135.9% | RED |
| 2020 | £1,816,630.04 | £1,857,054.07 | +2.2% | £736,963.94 | £744,297.46 | +1.0% | GREEN |
| 2021 | £2,028,952.42 | £2,415,732.82 | +19.1% | £833,649.22 | £701,881.14 | -15.8% | RED |
| 2022 | £2,607,611.88 | £4,241,597.52 | +62.7% | £790,935.58 | £939,286.61 | +18.8% | RED |
| 2023 | £4,508,414.67 | £3,473,229.08 | -23.0% | £1,029,561.00 | £856,766.08 | -16.8% | RED |
| 2024 | £3,512,844.39 | £3,000,893.30 | -14.6% | £893,105.75 | £1,173,163.83 | +31.4% | RED |
| 2025 | £3,145,356.42 | £1,228,431.44 | -60.9% | £1,315,150.33 | £470,656.66 | -64.2% | RED |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 2 | 0 | 0% | £450.00 |
| 2024 | 2 | 0 | 0% | £412.50 |

**Total:** 4 attempts, 0 wins (0% win rate), £862.50 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,389,510.57

## 2016

**Trading & Risk**

- Net margin: £743.01 (gross £6,813.70, capital £86.34)
  - Electricity: gross £6,002.97, capital £78.97, net £418.71
  - Gas: gross £810.73, capital £7.36, net £324.29
- Treasury at year end: £2,467,433.90
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
- Worst single period: C5 on 2016-12-31 period 48, net margin £-407.78

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £10,435.72
  - By billing account: C1 £6,441.15, C5 £14,339.54, C7 £10,526.48
- Bill shock events (>=20%): 31 -- C1g 2016-05-31 (37%); C1g 2016-06-30 (29%); C1g 2016-10-31 (79%); C1g 2016-11-30 (46%); C5 2016-05-31 (27%); C5 2016-10-31 (40%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (77%); C7 2016-11-30 (52%); C2g 2016-05-31 (36%); C2g 2016-06-30 (34%); C2g 2016-10-31 (82%); C2g 2016-11-30 (53%); C6 2016-05-31 (25%); C6 2016-06-30 (23%); C6 2016-10-31 (40%); C6 2016-11-30 (46%); C8 2016-05-31 (40%); C8 2016-06-30 (40%); C8 2016-09-30 (22%); C8 2016-10-31 (100%); C8 2016-11-30 (68%); C3g 2016-10-31 (70%); C3g 2016-11-30 (48%); C9 2016-10-31 (74%); C9 2016-11-30 (58%); C4 2016-11-30 (28%); C4g 2016-11-30 (47%)
- Churn risk (accounts renewing in 2016): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £117.30-£131.86/MWh, net margin £74.41
- C1g (gas): tariff £24.46-£26.25/MWh, net margin £109.88
- C2 (electricity): tariff £107.62/MWh, net margin £74.80
- C2g (gas): tariff £26.92/MWh, net margin £116.32
- C3 (electricity): tariff £98.21/MWh, net margin £-66.10 -- **net-negative**
- C3g (gas): tariff £21.93/MWh, net margin £45.98
- C4 (electricity): tariff £98.43/MWh, net margin £14.63
- C4g (gas): tariff £24.40/MWh, net margin £52.11
- C5 (electricity): tariff £117.30-£131.01/MWh, net margin £-159.01 -- **net-negative**
- C6 (electricity): tariff £107.62/MWh, net margin £24.49
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £267.20
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £139.89
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £48.41

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.829, average bill shock 19.7%, bad debt provision £601.90, avg complaint probability 4.7%
- Solvency signal: £274,159/customer (9 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2016 produced a net gain of £743.01 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 31 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £31,639.82 (gross £123,236.40, capital £1,273.22)
  - Electricity: gross £121,806.83, capital £1,258.37, net £31,123.28
  - Gas: gross £1,429.57, capital £14.85, net £516.54
- Treasury at year end: £2,498,375.34
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
- Worst single period: C2 on 2017-12-31 period 48, net margin £-287.18

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £11,688.96
  - By billing account: C1 £5,601.50, C2 £11,116.43, C3 £9,546.99, C4 £8,808.37, C5 £12,098.33, C6 £24,176.00, C7 £8,777.12, C8 £13,810.06, C9 £11,265.80
- Bill shock events (>=20%): 50 -- C1g 2017-01-31 (31%); C1g 2017-02-28 (28%); C1g 2017-05-31 (30%); C1g 2017-06-30 (30%); C1g 2017-09-30 (21%); C1g 2017-11-30 (70%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-05-31 (34%); C2g 2017-06-30 (29%); C2g 2017-09-30 (27%); C2g 2017-11-30 (66%); C2g 2017-12-31 (22%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-05-31 (30%); C3g 2017-06-30 (23%); C3g 2017-09-30 (21%); C3g 2017-11-30 (59%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (28%); C4 2017-09-30 (21%); C4 2017-10-31 (25%); C4 2017-11-30 (26%); C4g 2017-01-31 (23%); C4g 2017-02-28 (22%); C4g 2017-05-31 (33%); C4g 2017-06-30 (35%); C4g 2017-09-30 (36%); C4g 2017-10-31 (22%); C4g 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £117.65-£131.86/MWh, net margin £66.66
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £115.22
- C2 (electricity): tariff £107.62-£125.75/MWh, net margin £-212.03 -- **net-negative**
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £194.46
- C3 (electricity): tariff £98.21-£120.78/MWh, net margin £104.39
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £69.89
- C4 (electricity): tariff £98.43-£109.87/MWh, net margin £56.41
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £136.97
- C5 (electricity): tariff £119.51-£131.01/MWh, net margin £263.09
- C6 (electricity): tariff £107.62-£126.89/MWh, net margin £98.17
- C7 (electricity): tariff £96.38-£195.85/MWh, net margin £194.41
- C8 (electricity): tariff £84.56-£191.02/MWh, net margin £246.20
- C9 (electricity): tariff £77.16-£181.41/MWh, net margin £166.07
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £30,139.92

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.818, average bill shock 16.5%, bad debt provision £301.56, avg complaint probability 4.7%
- Solvency signal: £249,838/customer (10 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2017 produced a net gain of £31,639.82 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 50 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £101,758.70 (gross £262,531.43, capital £1,528.07)
  - Electricity: gross £261,168.63, capital £1,507.00, net £101,321.76
  - Gas: gross £1,362.80, capital £21.07, net £436.94
- Treasury at year end: £2,487,546.78
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.92 (avg 0.92), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C2 on 2018-12-31 period 48, net margin £-195.71

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £299,926.35
  - By billing account: C1 £5,808.05, C2 £9,414.71, C3 £9,275.49, C4 £7,730.63, C5 £11,729.08, C6 £20,244.14, C7 £8,758.74, C8 £12,288.83, C9 £10,599.42, C_IC1 £2,903,414.38
- Bill shock events (>=20%): 60 -- C1g 2018-04-30 (37%); C1g 2018-05-31 (29%); C1g 2018-06-30 (30%); C1g 2018-09-30 (25%); C1g 2018-10-31 (46%); C1g 2018-11-30 (27%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (28%); C2g 2018-05-31 (34%); C2g 2018-06-30 (34%); C2g 2018-09-30 (33%); C2g 2018-10-31 (45%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (28%); C3g 2018-05-31 (32%); C3g 2018-06-30 (29%); C3g 2018-08-31 (34%); C3g 2018-09-30 (34%); C3g 2018-10-31 (35%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (28%); C4 2018-09-30 (23%); C4 2018-10-31 (41%); C4 2018-11-30 (28%); C4g 2018-04-30 (36%); C4g 2018-05-31 (33%); C4g 2018-06-30 (36%); C4g 2018-09-30 (39%); C4g 2018-10-31 (85%); C4g 2018-11-30 (24%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C2 23%, C3 23%, C6 23%, C7 20%, C8 23%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £117.65-£149.68/MWh, net margin £28.02
- C1g (gas): tariff £33.49-£36.05/MWh, net margin £142.44
- C2 (electricity): tariff £125.75-£143.89/MWh, net margin £-127.19 -- **net-negative**
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £189.04
- C3 (electricity): tariff £120.78-£126.90/MWh, net margin £-21.25 -- **net-negative**
- C3g (gas): tariff £23.11-£28.80/MWh, net margin £40.74
- C4 (electricity): tariff £109.87-£149.37/MWh, net margin £73.83
- C4g (gas): tariff £26.10-£33.61/MWh, net margin £64.72
- C5 (electricity): tariff £119.51-£153.39/MWh, net margin £-180.03 -- **net-negative**
- C6 (electricity): tariff £126.89-£142.17/MWh, net margin £-7.36 -- **net-negative**
- C7 (electricity): tariff £96.38-£221.28/MWh, net margin £-13.48 -- **net-negative**
- C8 (electricity): tariff £100.06-£200.68/MWh, net margin £164.23
- C9 (electricity): tariff £95.02-£198.38/MWh, net margin £242.58
- C_IC1 (electricity): tariff £-82.12-£228.47/MWh, net margin £107,353.51
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,191.11 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.810, average bill shock 16.0%, bad debt provision £332.22, avg complaint probability 4.7%
- Solvency signal: £226,141/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2018 produced a net gain of £101,758.70 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 60 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £233,491.26 (gross £702,027.61, capital £2,309.31)
  - Electricity: gross £625,973.77, capital £2,287.85, net £223,001.61
  - Gas: gross £76,053.84, capital £21.46, net £10,489.65
- Treasury at year end: £2,611,521.98
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2019-12-31 period 48, net margin £-468.98

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £403,312.11
  - By billing account: C1 £5,712.93, C2 £9,836.41, C3 £9,414.65, C4 £7,275.29, C5 £14,161.51, C6 £20,277.71, C7 £8,950.16, C8 £10,190.96, C9 £10,617.54, C_IC1 £2,675,978.51, C_IC2 £1,664,017.56
- Bill shock events (>=20%): 66 -- C1 2019-04-30 (21%); C1g 2019-01-31 (36%); C1g 2019-02-28 (26%); C1g 2019-05-31 (23%); C1g 2019-06-30 (35%); C1g 2019-10-31 (74%); C1g 2019-11-30 (43%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-01-31 (25%); C2g 2019-02-28 (26%); C2g 2019-04-30 (35%); C2g 2019-06-30 (32%); C2g 2019-07-31 (25%); C2g 2019-09-30 (30%); C2g 2019-10-31 (64%); C2g 2019-11-30 (28%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-02-28 (26%); C3g 2019-06-30 (33%); C3g 2019-07-31 (35%); C3g 2019-09-30 (35%); C3g 2019-10-31 (64%); C3g 2019-11-30 (31%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (31%); C4 2019-09-30 (25%); C4 2019-11-30 (26%); C4g 2019-01-31 (30%); C4g 2019-02-28 (25%); C4g 2019-05-31 (21%); C4g 2019-06-30 (33%); C4g 2019-07-31 (37%); C4g 2019-09-30 (31%); C4g 2019-10-31 (34%); C4g 2019-11-30 (35%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C1 29%, C4 35%, C5 35%, C7 29%, C9 23%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£149.68/MWh, net margin £110.02
- C1g (gas): tariff £25.33-£36.05/MWh, net margin £156.37
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £145.29
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £134.46
- C3 (electricity): tariff £120.68-£126.90/MWh, net margin £-45.00 -- **net-negative**
- C3g (gas): tariff £23.00-£28.80/MWh, net margin £97.85
- C4 (electricity): tariff £126.76-£149.37/MWh, net margin £115.42
- C4g (gas): tariff £19.47-£33.61/MWh, net margin £101.05
- C5 (electricity): tariff £126.10-£153.39/MWh, net margin £-347.95 -- **net-negative**
- C6 (electricity): tariff £142.17-£148.72/MWh, net margin £129.35
- C7 (electricity): tariff £99.69-£221.28/MWh, net margin £112.02
- C8 (electricity): tariff £105.12-£211.40/MWh, net margin £192.83
- C9 (electricity): tariff £98.80-£198.38/MWh, net margin £181.99
- C_IC1 (electricity): tariff £0.00-£263.70/MWh, net margin £139,345.10
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £79,281.83
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £3,780.73
- C_IC3g (gas): tariff £27.53/MWh, net margin £9,999.92

**Portfolio Health**

- Capital cost ratio: 0.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.824, average bill shock 17.1%, bad debt provision £588.55, avg complaint probability 4.7%
- Solvency signal: £217,627/customer (12 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2019 produced a net gain of £233,491.26 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £128,570.01 (gross £791,784.27, capital £1,962.82)
  - Electricity: gross £714,604.72, capital £1,952.53, net £118,081.89
  - Gas: gross £77,179.55, capital £10.29, net £10,488.12
- Treasury at year end: £2,923,396.55
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.89 (avg 0.89), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C6 0.86 (avg 0.86), C7 0.89 (avg 0.89), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2020-03-16 period 20, net margin £-18.66

**Customer Book**

- Active accounts: 19 (C1, C1_2, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 8, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C1_2, C_IC4
- Losses (churn) during year: C3, C1, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2020): £494,973.89
  - By billing account: C1 £5,695.19, C1_2 £17.48, C2 £8,853.93, C3 £6,721.43, C4 £7,574.86, C5 £11,866.56, C6 £18,754.15, C7 £8,783.77, C8 £10,801.44, C9 £11,532.70, C_IC1 £1,738,851.73, C_IC2 £755,935.36, C_IC3 £2,905,723.73, C_IC4 £1,438,522.15
- Bill shock events (>=20%): 52 -- C1g 2020-01-31 (21%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-29 (23%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (22%); C4 2020-11-30 (24%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (49%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 38%, C4 41%, C5 32%, C7 20%, C8 23%, C9 23%, C_IC1 41%, C_IC2 41%, C_IC3 20%

**Pricing & Margin**

- C1 (electricity): tariff £125.83/MWh, net margin £89.13
- C1_2 (electricity): tariff £133.55/MWh, net margin £-1.02 -- **net-negative**
- C1g (gas): tariff £25.33/MWh, net margin £145.23
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £200.43
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £143.77
- C3 (electricity): tariff £120.68/MWh, net margin £44.45
- C3g (gas): tariff £23.00/MWh, net margin £82.00
- C4 (electricity): tariff £122.47-£126.76/MWh, net margin £99.65
- C4g (gas): tariff £16.09-£19.47/MWh, net margin £86.36
- C5 (electricity): tariff £126.10/MWh, net margin £37.94
- C6 (electricity): tariff £143.89-£148.72/MWh, net margin £401.80
- C7 (electricity): tariff £99.69-£205.61/MWh, net margin £91.13
- C8 (electricity): tariff £110.24-£211.40/MWh, net margin £376.05
- C9 (electricity): tariff £85.33-£188.63/MWh, net margin £150.25
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £53,249.44
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £44,258.51
- C_IC3 (electricity): tariff £37.49-£80.52/MWh, net margin £13,084.56
- C_IC3g (gas): tariff £15.44-£19.38/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £5,999.58

**Portfolio Health**

- Capital cost ratio: 0.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 205, average clarity 0.832, average bill shock 14.4%, bad debt provision £-59.57, avg complaint probability 4.3%
- Solvency signal: £208,814/customer (14 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £85,011.97 vs. naked (unhedged) net margin: £962,664.35
- hedging cost £877,652.37 vs. a fully unhedged book (commodity-only: actual net £85,011.97 vs. naked net £962,664.35)
  - C1_2: actual £-149.26 vs. naked £154.26 -- hedging cost £303.52
  - C2: actual £175.35 vs. naked £570.69 -- hedging cost £395.33
  - C2g: actual £144.84 vs. naked £324.27 -- hedging cost £179.43
  - C4: actual £25.02 vs. naked £235.46 -- hedging cost £210.45
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-169.22 vs. naked £264.15 -- hedging cost £433.37
  - C8: actual £341.71 vs. naked £1,170.27 -- hedging cost £828.57
  - C9: actual £-18.70 vs. naked £697.66 -- hedging cost £716.35
  - C_IC1: actual £33,034.60 vs. naked £128,260.98 -- hedging cost £95,226.38
  - C_IC2: actual £42,303.73 vs. naked £96,422.44 -- hedging cost £54,118.71
  - C_IC3: actual £-16,778.22 vs. naked £220,193.56 -- hedging cost £236,971.77
  - C_IC3g: actual £17,934.51 vs. naked £159,245.07 -- hedging cost £141,310.56
  - C_IC4: actual £7,886.99 vs. naked £352,832.81 -- hedging cost £344,945.82

**Year narrative:** 2020 produced a net gain of £128,570.01 across 19 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 52 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £75,439.68 (gross £762,965.84, capital £5,602.32)
  - Electricity: gross £680,357.05, capital £5,589.33, net £65,616.48
  - Gas: gross £82,608.79, capital £12.99, net £9,823.20
- Treasury at year end: £2,956,666.57
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.95 (avg 0.95), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C4 on 2021-12-31 period 48, net margin £-184.64

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2021): £479,388.72
  - By billing account: C1 £4,932.48, C1_2 £1,192.45, C2 £7,259.30, C3 £6,992.28, C4 £7,515.68, C5 £11,321.46, C6 £19,567.16, C7 £7,818.11, C8 £10,835.01, C9 £9,625.86, C_IC1 £1,519,664.14, C_IC2 £963,457.48, C_IC3 £2,434,316.76, C_IC4 £1,706,943.89
- Bill shock events (>=20%): 47 -- C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (62%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (23%); C4 2021-10-31 (48%); C4 2021-11-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%); C1_2 2021-01-31 (1207%); C1_2 2021-05-31 (33%); C1_2 2021-06-30 (55%); C1_2 2021-10-31 (76%); C1_2 2021-11-30 (75%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C7 20%, C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £133.55-£332.49/MWh, net margin £-89.38 -- **net-negative**
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £197.77
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £126.10
- C4 (electricity): tariff £122.47-£183.00/MWh, net margin £-243.82 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-302.82 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.14/MWh, net margin £592.73
- C7 (electricity): tariff £107.70-£274.50/MWh, net margin £-101.35 -- **net-negative**
- C8 (electricity): tariff £110.24-£274.50/MWh, net margin £431.61
- C9 (electricity): tariff £85.33-£264.43/MWh, net margin £62.27
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £28,122.58
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £56,390.32
- C_IC3 (electricity): tariff £42.18-£391.51/MWh, net margin £-25,685.27 -- **net-negative**
- C_IC3g (gas): tariff £19.38-£125.90/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £5,939.02

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.816, average bill shock 24.1%, bad debt provision £212.51, avg complaint probability 4.8%
- Solvency signal: £268,788/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £191,989.05 vs. naked (unhedged) net margin: £457,509.78
- hedging cost £265,520.73 vs. a fully unhedged book (commodity-only: actual net £191,989.05 vs. naked net £457,509.78)
  - C1_2: actual £-81.20 vs. naked £584.68 -- hedging cost £665.88
  - C2: actual £136.64 vs. naked £124.72 -- hedging added £11.92
  - C2g: actual £45.59 vs. naked £-190.70 -- hedging added £236.29
  - C4: actual £-220.41 vs. naked £-170.34 -- hedging cost £50.07
  - C4g: actual £-901.21 vs. naked £-1,344.38 -- hedging added £443.17
  - C6: actual £513.29 vs. naked £268.65 -- hedging added £244.64
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-48.54 vs. naked £-184.09 -- hedging added £135.55
  - C_IC1: actual £27,313.18 vs. naked £-61,913.05 -- hedging added £89,226.22
  - C_IC2: actual £63,557.08 vs. naked £22,118.29 -- hedging added £41,438.79
  - C_IC3: actual £100,979.79 vs. naked £235,473.85 -- hedging cost £134,494.06
  - C_IC3g: actual £4,142.87 vs. naked £85,199.40 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £178,304.23 -- hedging cost £180,207.49

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £75,439.68 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 47 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £339,300.82 (gross £1,050,357.61, capital £13,265.19)
  - Electricity: gross £960,001.69, capital £13,231.35, net £330,457.12
  - Gas: gross £90,355.92, capital £33.84, net £8,843.70
- Treasury at year end: £3,161,597.39
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,037,622.66, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,195.53 / stressed £20,483.42) ratio 2.69
  - 2022-05-29: treasury £3,037,743.01, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,305.32 / stressed £20,512.63) ratio 2.70
  - 2022-06-28: treasury £3,037,737.77, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,305.32 / stressed £20,512.63) ratio 2.70
  - 2022-07-28: treasury £3,037,545.14, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,366.74 / stressed £20,524.86) ratio 2.70
  - 2022-08-27: treasury £3,037,535.54, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,366.74 / stressed £20,524.86) ratio 2.70
  - 2022-09-26: treasury £3,037,520.09, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,366.74 / stressed £20,524.86) ratio 2.70
  - 2022-10-26: treasury £3,036,573.31, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,366.74 / stressed £20,524.86) ratio 2.70
  - 2022-11-25: treasury £3,036,570.32, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,366.74 / stressed £20,524.86) ratio 2.70
  - 2022-12-25: treasury £3,036,536.67, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,366.74 / stressed £20,524.86) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C2 on 2022-03-30 period 48, net margin £-112.45

**Customer Book**

- Active accounts: 15 (C1_2, C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2022): £414,068.80
  - By billing account: C1 £4,400.36, C1_2 £1,966.12, C2 £6,154.83, C2_2 £1,084.68, C3 £6,105.80, C4 £3,597.98, C5 £11,380.38, C6 £19,068.48, C7 £6,212.79, C8 £7,664.31, C9 £9,790.74, C_IC1 £1,281,646.65, C_IC2 £825,520.12, C_IC3 £2,649,800.10, C_IC4 £1,376,638.63
- Bill shock events (>=20%): 71 -- C7 2022-01-31 (52%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (57%); C_IC3 2022-01-31 (109%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C1_2 2022-01-31 (141%); C1_2 2022-02-28 (28%); C1_2 2022-04-30 (23%); C1_2 2022-05-31 (43%); C1_2 2022-06-30 (34%); C1_2 2022-09-30 (51%); C1_2 2022-11-30 (79%); C1_2 2022-12-31 (61%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 11 at risk (≥20% churn prob): C1_2 41%, C2 38%, C4 38%, C6 35%, C7 29%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.45-£332.49/MWh, net margin £178.51
- C2 (electricity): tariff £183.00/MWh, net margin £-99.38 -- **net-negative**
- C2_2 (electricity): tariff £361.95/MWh, net margin £219.72
- C2g (gas): tariff £35.00/MWh, net margin £2.93
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-170.22 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,159.15 -- **net-negative**
- C6 (electricity): tariff £197.14-£406.87/MWh, net margin £1,061.61
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,632.87 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £73.71
- C9 (electricity): tariff £138.51-£389.54/MWh, net margin £110.53
- C_IC1 (electricity): tariff £-83.39-£462.98/MWh, net margin £136,457.02
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £76,076.83
- C_IC3 (electricity): tariff £146.69-£391.51/MWh, net margin £112,262.29
- C_IC3g (gas): tariff £116.42-£125.90/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £5,919.38

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 2 -- £3,471,375.34 -> £3,052,384.88 (12.1%); £3,471,553.33 -> £3,051,839.08 (12.1%)
- Bills issued: 160, average clarity 0.783, average bill shock 34.5%, bad debt provision £118.54, avg complaint probability 5.8%
- Solvency signal: £263,466/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £184,435.00 vs. naked (unhedged) net margin: £1,207,216.93
- hedging cost £1,022,781.94 vs. a fully unhedged book (commodity-only: actual net £184,435.00 vs. naked net £1,207,216.93)
  - C1_2: actual £-589.08 vs. naked £1,295.37 -- hedging cost £1,884.46
  - C2_2: actual £30.18 vs. naked £1,645.15 -- hedging cost £1,614.97
  - C4: actual £-277.33 vs. naked £595.36 -- hedging cost £872.70
  - C4g: actual £-1,950.48 vs. naked £1,336.80 -- hedging cost £3,287.28
  - C6: actual £1,127.94 vs. naked £3,996.00 -- hedging cost £2,868.06
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-481.87 vs. naked £1,102.92 -- hedging cost £1,584.78
  - C9: actual £-49.37 vs. naked £1,012.21 -- hedging cost £1,061.58
  - C_IC1: actual £212,769.18 vs. naked £251,051.06 -- hedging cost £38,281.88
  - C_IC2: actual £87,515.21 vs. naked £126,821.77 -- hedging cost £39,306.57
  - C_IC3: actual £-125,200.05 vs. naked £487,720.66 -- hedging cost £612,920.70
  - C_IC3g: actual £8,513.79 vs. naked £123,301.26 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £205,056.67 -- hedging cost £201,583.86

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £339,300.82 across 15 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 71 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £146,246.51 (gross £955,933.83, capital £10,020.69)
  - Electricity: gross £834,993.72, capital £9,968.27, net £137,287.54
  - Gas: gross £120,940.11, capital £52.42, net £8,958.96
- Treasury at year end: £3,382,344.22
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.91 (avg 0.91), C2_2 0.93 (avg 0.93), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,137,953.26, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,214.46 / stressed £43,949.82) ratio 2.76
  - 2023-02-23: treasury £3,137,953.61, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,214.46 / stressed £43,949.82) ratio 2.76
  - 2023-03-25: treasury £3,137,953.91, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,214.46 / stressed £43,949.82) ratio 2.76
  - 2023-04-24: treasury £3,218,174.39, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,247.86 / stressed £48,906.85) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C_IC1 on 2023-06-16 period 22, net margin £-21.69

**Customer Book**

- Active accounts: 13 (C1_2, C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2023): £360,643.67
  - By billing account: C1 £4,136.75, C1_2 £2,369.24, C2 £4,927.44, C2_2 £2,855.02, C3 £5,569.43, C4 £2,746.79, C5 £7,937.00, C6 £17,967.24, C7 £5,555.70, C8 £8,439.10, C9 £7,646.80, C_IC1 £1,408,505.47, C_IC2 £666,004.29, C_IC3 £2,005,078.93, C_IC4 £1,259,915.93
- Bill shock events (>=20%): 48 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (32%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (25%); C4 2023-04-30 (29%); C4 2023-09-30 (24%); C4 2023-11-30 (27%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (46%); C4g 2023-11-30 (63%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (101%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%); C1_2 2023-05-31 (38%); C1_2 2023-06-30 (43%); C1_2 2023-10-31 (73%); C1_2 2023-11-30 (83%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%)
- Churn risk (accounts renewing in 2023): 9 at risk (≥20% churn prob): C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.45-£268.29/MWh, net margin £-444.73 -- **net-negative**
- C2_2 (electricity): tariff £349.87-£361.95/MWh, net margin £692.03
- C4 (electricity): tariff £249.30-£305.00/MWh, net margin £-9.42 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,040.96 -- **net-negative**
- C6 (electricity): tariff £332.35-£406.87/MWh, net margin £1,423.56
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-144.77 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £159.02
- C9 (electricity): tariff £192.57-£389.54/MWh, net margin £396.44
- C_IC1 (electricity): tariff £-60.00-£462.98/MWh, net margin £162,616.84
- C_IC2 (electricity): tariff £-186.24-£476.93/MWh, net margin £86,071.64
- C_IC3 (electricity): tariff £95.79-£280.04/MWh, net margin £-119,400.92 -- **net-negative**
- C_IC3g (gas): tariff £56.57-£116.42/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £5,927.85

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): 47 -- £3,771,396.96 -> £3,382,152.12 (10.3%); £3,771,397.11 -> £3,382,152.14 (10.3%); £3,771,397.26 -> £3,382,152.16 (10.3%); £3,771,397.41 -> £3,382,152.17 (10.3%); £3,771,397.57 -> £3,382,152.19 (10.3%); £3,771,397.72 -> £3,382,152.20 (10.3%); £3,771,397.87 -> £3,382,152.22 (10.3%); £3,771,398.03 -> £3,382,152.23 (10.3%); £3,771,398.18 -> £3,382,152.24 (10.3%); £3,771,398.34 -> £3,382,152.26 (10.3%); £3,771,398.49 -> £3,382,152.27 (10.3%); £3,771,398.65 -> £3,382,152.41 (10.3%); £3,771,398.81 -> £3,382,152.55 (10.3%); £3,771,398.98 -> £3,382,152.68 (10.3%); £3,771,399.17 -> £3,382,152.81 (10.3%); £3,771,399.38 -> £3,382,152.95 (10.3%); £3,771,399.60 -> £3,382,153.10 (10.3%); £3,771,399.84 -> £3,382,153.24 (10.3%); £3,771,400.11 -> £3,382,153.39 (10.3%); £3,771,400.36 -> £3,382,153.42 (10.3%); £3,771,400.62 -> £3,382,153.44 (10.3%); £3,771,400.87 -> £3,382,153.47 (10.3%); £3,771,401.14 -> £3,382,153.50 (10.3%); £3,771,401.40 -> £3,382,153.52 (10.3%); £3,771,401.66 -> £3,382,153.55 (10.3%); £3,771,401.93 -> £3,382,153.58 (10.3%); £3,771,402.19 -> £3,382,153.60 (10.3%); £3,771,402.45 -> £3,382,153.62 (10.3%); £3,771,402.71 -> £3,382,153.65 (10.3%); £3,771,402.96 -> £3,382,153.67 (10.3%); £3,771,403.22 -> £3,382,153.70 (10.3%); £3,771,403.47 -> £3,382,153.72 (10.3%); £3,771,403.73 -> £3,382,153.87 (10.3%); £3,771,403.99 -> £3,382,154.02 (10.3%); £3,771,404.25 -> £3,382,154.17 (10.3%); £3,771,404.51 -> £3,382,154.32 (10.3%); £3,771,404.77 -> £3,382,154.48 (10.3%); £3,771,405.03 -> £3,382,154.63 (10.3%); £3,771,405.30 -> £3,382,154.78 (10.3%); £3,771,405.56 -> £3,382,154.93 (10.3%); £3,771,405.82 -> £3,382,155.08 (10.3%); £3,771,406.08 -> £3,382,155.21 (10.3%); £3,771,406.34 -> £3,382,155.35 (10.3%); £3,771,406.60 -> £3,382,155.38 (10.3%); £3,771,406.86 -> £3,382,155.40 (10.3%); £3,771,407.10 -> £3,382,155.43 (10.3%); £3,771,407.32 -> £3,382,344.22 (10.3%)
- Bills issued: 156, average clarity 0.802, average bill shock 18.2%, bad debt provision £-0.00, avg complaint probability 5.0%
- Solvency signal: £307,486/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £381,547.29 vs. naked (unhedged) net margin: £1,221,201.87
- hedging cost £839,654.58 vs. a fully unhedged book (commodity-only: actual net £381,547.29 vs. naked net £1,221,201.87)
  - C1_2: actual £684.85 vs. naked £1,724.57 -- hedging cost £1,039.72
  - C2_2: actual £827.41 vs. naked £2,419.46 -- hedging cost £1,592.05
  - C4: actual £313.86 vs. naked £700.05 -- hedging cost £386.18
  - C4g: actual £529.39 vs. naked £1,048.79 -- hedging cost £519.40
  - C6: actual £1,390.89 vs. naked £5,058.90 -- hedging cost £3,668.01
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £140.61 vs. naked £1,972.23 -- hedging cost £1,831.62
  - C9: actual £626.00 vs. naked £2,129.64 -- hedging cost £1,503.64
  - C_IC1: actual £141,576.45 vs. naked £284,450.26 -- hedging cost £142,873.81
  - C_IC2: actual £94,108.05 vs. naked £162,159.80 -- hedging cost £68,051.75
  - C_IC3: actual £128,504.20 vs. naked £402,313.79 -- hedging cost £273,809.60
  - C_IC3g: actual £8,660.26 vs. naked £123,107.25 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £232,127.67 -- hedging cost £228,435.92

**Year narrative:** 2023 produced a net gain of £146,246.51 across 13 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 48 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £348,334.21 (gross £1,258,890.97, capital £9,516.00)
  - Electricity: gross £1,134,477.10, capital £9,492.60, net £337,866.86
  - Gas: gross £124,413.88, capital £23.40, net £10,467.35
- Treasury at year end: £3,777,721.76
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.87 (avg 0.87), C2_2 0.91 (avg 0.91), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2024-06-28 period 31, net margin £-26.25

**Customer Book**

- Active accounts: 13 (C1_2, C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £353,130.54
  - By billing account: C1 £3,724.20, C1_2 £3,159.41, C2 £4,845.69, C2_2 £3,466.66, C3 £6,430.87, C4 £3,087.28, C5 £7,719.96, C6 £19,291.77, C7 £5,631.26, C8 £7,942.04, C9 £8,271.75, C_IC1 £1,187,379.58, C_IC2 £616,906.30, C_IC3 £2,145,132.18, C_IC4 £1,273,969.11
- Bill shock events (>=20%): 40 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (30%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C1_2 2024-01-31 (21%); C1_2 2024-02-29 (28%); C1_2 2024-04-30 (23%); C1_2 2024-05-31 (44%); C1_2 2024-09-30 (51%); C1_2 2024-10-31 (45%); C1_2 2024-11-30 (57%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (59%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (55%)
- Churn risk (accounts renewing in 2024): 8 at risk (≥20% churn prob): C2_2 23%, C4 38%, C6 26%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC3 41%, C_IC4 20%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01-£268.29/MWh, net margin £765.10
- C2_2 (electricity): tariff £200.79-£349.87/MWh, net margin £511.18
- C4 (electricity): tariff £249.30/MWh, net margin £256.64
- C4g (gas): tariff £66.00/MWh, net margin £436.59
- C6 (electricity): tariff £332.35/MWh, net margin £516.59
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £635.74
- C8 (electricity): tariff £161.98-£397.50/MWh, net margin £427.05
- C9 (electricity): tariff £165.00-£367.64/MWh, net margin £655.96
- C_IC1 (electricity): tariff £-98.58-£330.68/MWh, net margin £125,732.10
- C_IC2 (electricity): tariff £-106.92-£354.92/MWh, net margin £69,935.13
- C_IC3 (electricity): tariff £88.52-£182.88/MWh, net margin £132,480.07
- C_IC3g (gas): tariff £54.85-£56.57/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £5,951.30

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): 4271 -- £3,773,855.30 -> £3,382,344.26 (10.4%); £3,773,855.48 -> £3,382,344.28 (10.4%); £3,773,855.65 -> £3,382,344.30 (10.4%); £3,773,855.83 -> £3,382,344.31 (10.4%); £3,773,856.00 -> £3,382,344.33 (10.4%); £3,773,856.17 -> £3,382,344.35 (10.4%); £3,773,856.34 -> £3,382,344.36 (10.4%); £3,773,856.52 -> £3,382,344.38 (10.4%); £3,773,856.69 -> £3,382,344.40 (10.4%); £3,773,856.86 -> £3,382,344.41 (10.4%); £3,773,857.04 -> £3,382,344.43 (10.4%); £3,773,857.21 -> £3,382,344.58 (10.4%); £3,773,857.38 -> £3,382,344.72 (10.4%); £3,773,857.57 -> £3,382,344.88 (10.4%); £3,773,857.78 -> £3,382,345.03 (10.4%); £3,773,858.01 -> £3,382,345.20 (10.4%); £3,773,858.25 -> £3,382,345.36 (10.4%); £3,773,858.51 -> £3,382,345.51 (10.4%); £3,773,858.80 -> £3,382,345.66 (10.4%); £3,773,859.07 -> £3,382,345.69 (10.4%); £3,773,859.37 -> £3,382,345.71 (10.4%); £3,773,859.66 -> £3,382,345.73 (10.4%); £3,773,859.95 -> £3,382,345.76 (10.4%); £3,773,860.24 -> £3,382,345.78 (10.4%); £3,773,860.53 -> £3,382,345.81 (10.4%); £3,773,860.82 -> £3,382,345.83 (10.4%); £3,773,861.10 -> £3,382,345.85 (10.4%); £3,773,861.37 -> £3,382,345.88 (10.4%); £3,773,861.64 -> £3,382,345.90 (10.4%); £3,773,861.93 -> £3,382,345.92 (10.4%); £3,773,862.22 -> £3,382,345.95 (10.4%); £3,773,862.50 -> £3,382,345.98 (10.4%); £3,773,862.79 -> £3,382,346.14 (10.4%); £3,773,863.07 -> £3,382,346.31 (10.4%); £3,773,863.29 -> £3,382,346.47 (10.4%); £3,773,863.51 -> £3,382,346.64 (10.4%); £3,773,863.72 -> £3,382,346.81 (10.4%); £3,773,864.02 -> £3,382,346.98 (10.4%); £3,773,864.32 -> £3,382,347.16 (10.4%); £3,773,864.59 -> £3,382,347.33 (10.4%); £3,773,864.89 -> £3,382,347.50 (10.4%); £3,773,865.17 -> £3,382,347.67 (10.4%); £3,773,865.46 -> £3,382,347.83 (10.4%); £3,773,865.75 -> £3,382,347.87 (10.4%); £3,773,866.05 -> £3,382,347.89 (10.4%); £3,773,866.30 -> £3,382,347.92 (10.4%); £3,773,866.55 -> £3,382,347.94 (10.4%); £3,773,866.77 -> £3,382,347.96 (10.4%); £3,773,866.94 -> £3,382,347.98 (10.4%); £3,773,867.12 -> £3,382,348.00 (10.4%); £3,773,867.29 -> £3,382,348.02 (10.4%); £3,773,867.45 -> £3,382,348.04 (10.4%); £3,773,867.62 -> £3,382,348.05 (10.4%); £3,773,867.79 -> £3,382,348.07 (10.4%); £3,773,867.97 -> £3,382,348.09 (10.4%); £3,773,868.13 -> £3,382,348.10 (10.4%); £3,773,868.30 -> £3,382,348.12 (10.4%); £3,773,868.48 -> £3,382,348.14 (10.4%); £3,773,868.64 -> £3,382,348.16 (10.4%); £3,773,868.81 -> £3,382,348.28 (10.4%); £3,773,868.98 -> £3,382,348.41 (10.4%); £3,773,869.17 -> £3,382,348.54 (10.4%); £3,773,869.37 -> £3,382,348.67 (10.4%); £3,773,869.60 -> £3,382,348.81 (10.4%); £3,773,869.83 -> £3,382,348.94 (10.4%); £3,773,870.09 -> £3,382,349.07 (10.4%); £3,773,870.37 -> £3,382,349.21 (10.4%); £3,773,870.65 -> £3,382,349.23 (10.4%); £3,773,870.92 -> £3,382,349.26 (10.4%); £3,773,871.21 -> £3,382,349.28 (10.4%); £3,773,871.49 -> £3,382,349.30 (10.4%); £3,773,871.77 -> £3,382,349.33 (10.4%); £3,773,872.05 -> £3,382,349.35 (10.4%); £3,773,872.33 -> £3,382,349.38 (10.4%); £3,773,872.61 -> £3,382,349.40 (10.4%); £3,773,872.88 -> £3,382,349.42 (10.4%); £3,773,873.16 -> £3,382,349.45 (10.4%); £3,773,873.43 -> £3,382,349.47 (10.4%); £3,773,873.71 -> £3,382,349.49 (10.4%); £3,773,873.99 -> £3,382,349.52 (10.4%); £3,773,874.20 -> £3,382,349.65 (10.4%); £3,773,874.41 -> £3,382,349.79 (10.4%); £3,773,874.63 -> £3,382,349.93 (10.4%); £3,773,874.84 -> £3,382,350.06 (10.4%); £3,773,875.05 -> £3,382,350.20 (10.4%); £3,773,875.27 -> £3,382,350.33 (10.4%); £3,773,875.48 -> £3,382,350.47 (10.4%); £3,773,875.76 -> £3,382,350.60 (10.4%); £3,773,876.04 -> £3,382,350.74 (10.4%); £3,773,876.32 -> £3,382,350.88 (10.4%); £3,773,876.60 -> £3,382,351.01 (10.4%); £3,773,876.89 -> £3,382,351.04 (10.4%); £3,773,877.17 -> £3,382,351.07 (10.4%); £3,773,877.44 -> £3,382,351.09 (10.4%); £3,773,877.67 -> £3,382,351.12 (10.4%); £3,773,877.88 -> £3,382,351.14 (10.4%); £3,773,878.06 -> £3,382,351.15 (10.4%); £3,773,878.23 -> £3,382,351.17 (10.4%); £3,773,878.40 -> £3,382,351.19 (10.4%); £3,773,878.57 -> £3,382,351.21 (10.4%); £3,773,878.74 -> £3,382,351.22 (10.4%); £3,773,878.90 -> £3,382,351.24 (10.4%); £3,773,879.07 -> £3,382,351.25 (10.4%); £3,773,879.24 -> £3,382,351.27 (10.4%); £3,773,879.41 -> £3,382,351.29 (10.4%); £3,773,879.58 -> £3,382,351.30 (10.4%); £3,773,879.75 -> £3,382,351.32 (10.4%); £3,773,879.92 -> £3,382,351.47 (10.4%); £3,773,880.09 -> £3,382,351.62 (10.4%); £3,773,880.28 -> £3,382,351.77 (10.4%); £3,773,880.49 -> £3,382,351.94 (10.4%); £3,773,880.71 -> £3,382,352.10 (10.4%); £3,773,880.96 -> £3,382,352.24 (10.4%); £3,773,881.23 -> £3,382,352.39 (10.4%); £3,773,881.51 -> £3,382,352.53 (10.4%); £3,773,881.79 -> £3,382,352.56 (10.4%); £3,773,882.07 -> £3,382,352.58 (10.4%); £3,773,882.35 -> £3,382,352.60 (10.4%); £3,773,882.64 -> £3,382,352.63 (10.4%); £3,773,882.93 -> £3,382,352.65 (10.4%); £3,773,883.22 -> £3,382,352.67 (10.4%); £3,773,883.51 -> £3,382,352.70 (10.4%); £3,773,883.79 -> £3,382,352.72 (10.4%); £3,773,884.07 -> £3,382,352.74 (10.4%); £3,773,884.35 -> £3,382,352.77 (10.4%); £3,773,884.63 -> £3,382,352.79 (10.4%); £3,773,884.91 -> £3,382,352.82 (10.4%); £3,773,885.19 -> £3,382,352.85 (10.4%); £3,773,885.47 -> £3,382,353.00 (10.4%); £3,773,885.69 -> £3,382,353.16 (10.4%); £3,773,885.97 -> £3,382,353.32 (10.4%); £3,773,886.17 -> £3,382,353.48 (10.4%); £3,773,886.38 -> £3,382,353.63 (10.4%); £3,773,886.60 -> £3,382,353.79 (10.4%); £3,773,886.81 -> £3,382,353.95 (10.4%); £3,773,887.09 -> £3,382,354.11 (10.4%); £3,773,887.37 -> £3,382,354.27 (10.4%); £3,773,887.65 -> £3,382,354.43 (10.4%); £3,773,887.93 -> £3,382,354.57 (10.4%); £3,773,888.21 -> £3,382,354.60 (10.4%); £3,773,888.51 -> £3,382,354.63 (10.4%); £3,773,888.76 -> £3,382,354.65 (10.4%); £3,773,889.00 -> £3,382,354.67 (10.4%); £3,773,889.22 -> £3,382,354.69 (10.4%); £3,773,889.38 -> £3,382,354.71 (10.4%); £3,773,889.55 -> £3,382,354.73 (10.4%); £3,773,889.71 -> £3,382,354.75 (10.4%); £3,773,889.88 -> £3,382,354.77 (10.4%); £3,773,890.05 -> £3,382,354.78 (10.4%); £3,773,890.21 -> £3,382,354.80 (10.4%); £3,773,890.38 -> £3,382,354.82 (10.4%); £3,773,890.55 -> £3,382,354.83 (10.4%); £3,773,890.72 -> £3,382,354.85 (10.4%); £3,773,890.89 -> £3,382,354.87 (10.4%); £3,773,891.06 -> £3,382,354.88 (10.4%); £3,773,891.23 -> £3,382,355.05 (10.4%); £3,773,891.40 -> £3,382,355.22 (10.4%); £3,773,891.59 -> £3,382,355.40 (10.4%); £3,773,891.79 -> £3,382,355.57 (10.4%); £3,773,892.01 -> £3,382,355.74 (10.4%); £3,773,892.25 -> £3,382,355.91 (10.4%); £3,773,892.51 -> £3,382,356.09 (10.4%); £3,773,892.79 -> £3,382,356.26 (10.4%); £3,773,893.06 -> £3,382,356.28 (10.4%); £3,773,893.35 -> £3,382,356.31 (10.4%); £3,773,893.62 -> £3,382,356.33 (10.4%); £3,773,893.90 -> £3,382,356.36 (10.4%); £3,773,894.18 -> £3,382,356.38 (10.4%); £3,773,894.45 -> £3,382,356.40 (10.4%); £3,773,894.72 -> £3,382,356.43 (10.4%); £3,773,895.01 -> £3,382,356.45 (10.4%); £3,773,895.29 -> £3,382,356.47 (10.4%); £3,773,895.56 -> £3,382,356.50 (10.4%); £3,773,895.84 -> £3,382,356.52 (10.4%); £3,773,896.12 -> £3,382,356.54 (10.4%); £3,773,896.40 -> £3,382,356.57 (10.4%); £3,773,896.60 -> £3,382,356.75 (10.4%); £3,773,896.88 -> £3,382,356.93 (10.4%); £3,773,897.16 -> £3,382,357.10 (10.4%); £3,773,897.36 -> £3,382,357.28 (10.4%); £3,773,897.63 -> £3,382,357.46 (10.4%); £3,773,897.91 -> £3,382,357.63 (10.4%); £3,773,898.12 -> £3,382,357.80 (10.4%); £3,773,898.41 -> £3,382,357.97 (10.4%); £3,773,898.68 -> £3,382,358.14 (10.4%); £3,773,898.96 -> £3,382,358.31 (10.4%); £3,773,899.24 -> £3,382,358.48 (10.4%); £3,773,899.53 -> £3,382,358.51 (10.4%); £3,773,899.80 -> £3,382,358.54 (10.4%); £3,773,900.05 -> £3,382,358.56 (10.4%); £3,773,900.29 -> £3,382,358.58 (10.4%); £3,773,900.51 -> £3,382,358.60 (10.4%); £3,773,900.67 -> £3,382,358.62 (10.4%); £3,773,900.83 -> £3,382,358.64 (10.4%); £3,773,900.99 -> £3,382,358.66 (10.4%); £3,773,901.15 -> £3,382,358.67 (10.4%); £3,773,901.31 -> £3,382,358.69 (10.4%); £3,773,901.47 -> £3,382,358.71 (10.4%); £3,773,901.64 -> £3,382,358.72 (10.4%); £3,773,901.79 -> £3,382,358.74 (10.4%); £3,773,901.96 -> £3,382,358.76 (10.4%); £3,773,902.13 -> £3,382,358.77 (10.4%); £3,773,902.29 -> £3,382,358.79 (10.4%); £3,773,902.45 -> £3,382,358.97 (10.4%); £3,773,902.61 -> £3,382,359.15 (10.4%); £3,773,902.79 -> £3,382,359.35 (10.4%); £3,773,902.98 -> £3,382,359.54 (10.4%); £3,773,903.19 -> £3,382,359.73 (10.4%); £3,773,903.43 -> £3,382,359.92 (10.4%); £3,773,903.69 -> £3,382,360.10 (10.4%); £3,773,903.96 -> £3,382,360.29 (10.4%); £3,773,904.24 -> £3,382,360.31 (10.4%); £3,773,904.50 -> £3,382,360.33 (10.4%); £3,773,904.77 -> £3,382,360.36 (10.4%); £3,773,905.04 -> £3,382,360.38 (10.4%); £3,773,905.31 -> £3,382,360.41 (10.4%); £3,773,905.58 -> £3,382,360.43 (10.4%); £3,773,905.85 -> £3,382,360.45 (10.4%); £3,773,906.12 -> £3,382,360.48 (10.4%); £3,773,906.38 -> £3,382,360.50 (10.4%); £3,773,906.65 -> £3,382,360.52 (10.4%); £3,773,906.92 -> £3,382,360.55 (10.4%); £3,773,907.18 -> £3,382,360.57 (10.4%); £3,773,907.46 -> £3,382,360.60 (10.4%); £3,773,907.65 -> £3,382,360.78 (10.4%); £3,773,907.86 -> £3,382,360.97 (10.4%); £3,773,908.06 -> £3,382,361.16 (10.4%); £3,773,908.27 -> £3,382,361.36 (10.4%); £3,773,908.53 -> £3,382,361.54 (10.4%); £3,773,908.73 -> £3,382,361.73 (10.4%); £3,773,908.94 -> £3,382,361.92 (10.4%); £3,773,909.20 -> £3,382,362.10 (10.4%); £3,773,909.47 -> £3,382,362.29 (10.4%); £3,773,909.74 -> £3,382,362.48 (10.4%); £3,773,910.01 -> £3,382,362.67 (10.4%); £3,773,910.27 -> £3,382,362.70 (10.4%); £3,773,910.54 -> £3,382,362.72 (10.4%); £3,773,910.80 -> £3,382,362.75 (10.4%); £3,773,911.02 -> £3,382,362.77 (10.4%); £3,773,911.23 -> £3,382,362.79 (10.4%); £3,773,911.38 -> £3,382,362.81 (10.4%); £3,773,911.52 -> £3,382,362.83 (10.4%); £3,773,911.67 -> £3,382,362.85 (10.4%); £3,773,911.81 -> £3,382,362.86 (10.4%); £3,773,911.96 -> £3,382,362.88 (10.4%); £3,773,912.10 -> £3,382,362.90 (10.4%); £3,773,912.24 -> £3,382,362.92 (10.4%); £3,773,912.38 -> £3,382,362.93 (10.4%); £3,773,912.52 -> £3,382,362.95 (10.4%); £3,773,912.66 -> £3,382,362.97 (10.4%); £3,773,912.79 -> £3,382,362.98 (10.4%); £3,773,912.94 -> £3,382,363.21 (10.4%); £3,773,913.08 -> £3,382,363.43 (10.4%); £3,773,913.23 -> £3,382,363.66 (10.4%); £3,773,913.40 -> £3,382,363.89 (10.4%); £3,773,913.60 -> £3,382,364.12 (10.4%); £3,773,913.80 -> £3,382,364.35 (10.4%); £3,773,914.02 -> £3,382,364.59 (10.4%); £3,773,914.26 -> £3,382,364.82 (10.4%); £3,773,914.49 -> £3,382,364.85 (10.4%); £3,773,914.72 -> £3,382,364.87 (10.4%); £3,773,914.96 -> £3,382,364.90 (10.4%); £3,773,915.20 -> £3,382,364.93 (10.4%); £3,773,915.43 -> £3,382,364.95 (10.4%); £3,773,915.67 -> £3,382,364.98 (10.4%); £3,773,915.90 -> £3,382,365.01 (10.4%); £3,773,916.14 -> £3,382,365.03 (10.4%); £3,773,916.39 -> £3,382,365.06 (10.4%); £3,773,916.62 -> £3,382,365.08 (10.4%); £3,773,916.87 -> £3,382,365.11 (10.4%); £3,773,917.10 -> £3,382,365.13 (10.4%); £3,773,917.34 -> £3,382,365.16 (10.4%); £3,773,917.57 -> £3,382,365.38 (10.4%); £3,773,917.74 -> £3,382,365.60 (10.4%); £3,773,917.91 -> £3,382,365.82 (10.4%); £3,773,918.09 -> £3,382,366.04 (10.4%); £3,773,918.27 -> £3,382,366.27 (10.4%); £3,773,918.44 -> £3,382,366.49 (10.4%); £3,773,918.63 -> £3,382,366.72 (10.4%); £3,773,918.86 -> £3,382,366.95 (10.4%); £3,773,919.09 -> £3,382,367.18 (10.4%); £3,773,919.32 -> £3,382,367.40 (10.4%); £3,773,919.56 -> £3,382,367.62 (10.4%); £3,773,919.79 -> £3,382,367.65 (10.4%); £3,773,920.02 -> £3,382,367.68 (10.4%); £3,773,920.24 -> £3,382,367.71 (10.4%); £3,773,920.44 -> £3,382,367.73 (10.4%); £3,773,920.62 -> £3,382,367.75 (10.4%); £3,773,920.76 -> £3,382,367.77 (10.4%); £3,773,920.90 -> £3,382,367.79 (10.4%); £3,773,921.04 -> £3,382,367.81 (10.4%); £3,773,921.18 -> £3,382,367.83 (10.4%); £3,773,921.32 -> £3,382,367.84 (10.4%); £3,773,921.46 -> £3,382,367.86 (10.4%); £3,773,921.60 -> £3,382,367.88 (10.4%); £3,773,921.74 -> £3,382,367.89 (10.4%); £3,773,921.88 -> £3,382,367.91 (10.4%); £3,773,922.02 -> £3,382,367.93 (10.4%); £3,773,922.16 -> £3,382,367.94 (10.4%); £3,773,922.30 -> £3,382,368.16 (10.4%); £3,773,922.43 -> £3,382,368.38 (10.4%); £3,773,922.59 -> £3,382,368.60 (10.4%); £3,773,922.76 -> £3,382,368.81 (10.4%); £3,773,922.95 -> £3,382,369.03 (10.4%); £3,773,923.16 -> £3,382,369.25 (10.4%); £3,773,923.37 -> £3,382,369.47 (10.4%); £3,773,923.61 -> £3,382,369.70 (10.4%); £3,773,923.85 -> £3,382,369.73 (10.4%); £3,773,924.08 -> £3,382,369.76 (10.4%); £3,773,924.31 -> £3,382,369.79 (10.4%); £3,773,924.54 -> £3,382,369.82 (10.4%); £3,773,924.77 -> £3,382,369.85 (10.4%); £3,773,925.00 -> £3,382,369.88 (10.4%); £3,773,925.22 -> £3,382,369.91 (10.4%); £3,773,925.46 -> £3,382,369.94 (10.4%); £3,773,925.69 -> £3,382,369.97 (10.4%); £3,773,925.92 -> £3,382,369.99 (10.4%); £3,773,926.16 -> £3,382,370.02 (10.4%); £3,773,926.39 -> £3,382,370.05 (10.4%); £3,773,926.62 -> £3,382,370.08 (10.4%); £3,773,926.79 -> £3,382,370.29 (10.4%); £3,773,926.97 -> £3,382,370.51 (10.4%); £3,773,927.14 -> £3,382,370.73 (10.4%); £3,773,927.31 -> £3,382,370.96 (10.4%); £3,773,927.54 -> £3,382,371.18 (10.4%); £3,773,927.72 -> £3,382,371.40 (10.4%); £3,773,927.90 -> £3,382,371.63 (10.4%); £3,773,928.14 -> £3,382,371.85 (10.4%); £3,773,928.37 -> £3,382,372.08 (10.4%); £3,773,928.61 -> £3,382,372.29 (10.4%); £3,773,928.83 -> £3,382,372.51 (10.4%); £3,773,929.06 -> £3,382,372.54 (10.4%); £3,773,929.30 -> £3,382,372.57 (10.4%); £3,773,929.51 -> £3,382,372.60 (10.4%); £3,773,929.71 -> £3,382,372.62 (10.4%); £3,773,929.89 -> £3,382,372.64 (10.4%); £3,773,930.05 -> £3,382,372.66 (10.4%); £3,773,930.21 -> £3,382,372.67 (10.4%); £3,773,930.35 -> £3,382,372.69 (10.4%); £3,773,930.51 -> £3,382,372.71 (10.4%); £3,773,930.66 -> £3,382,372.73 (10.4%); £3,773,930.82 -> £3,382,372.74 (10.4%); £3,773,930.97 -> £3,382,372.76 (10.4%); £3,773,931.12 -> £3,382,372.78 (10.4%); £3,773,931.28 -> £3,382,372.79 (10.4%); £3,773,931.43 -> £3,382,372.81 (10.4%); £3,773,931.59 -> £3,382,372.83 (10.4%); £3,773,931.74 -> £3,382,373.03 (10.4%); £3,773,931.90 -> £3,382,373.25 (10.4%); £3,773,932.07 -> £3,382,373.46 (10.4%); £3,773,932.25 -> £3,382,373.67 (10.4%); £3,773,932.45 -> £3,382,373.89 (10.4%); £3,773,932.68 -> £3,382,374.11 (10.4%); £3,773,932.91 -> £3,382,374.33 (10.4%); £3,773,933.16 -> £3,382,374.55 (10.4%); £3,773,933.40 -> £3,382,374.57 (10.4%); £3,773,933.66 -> £3,382,374.60 (10.4%); £3,773,933.92 -> £3,382,374.62 (10.4%); £3,773,934.17 -> £3,382,374.64 (10.4%); £3,773,934.43 -> £3,382,374.67 (10.4%); £3,773,934.69 -> £3,382,374.69 (10.4%); £3,773,934.95 -> £3,382,374.71 (10.4%); £3,773,935.21 -> £3,382,374.74 (10.4%); £3,773,935.47 -> £3,382,374.76 (10.4%); £3,773,935.72 -> £3,382,374.78 (10.4%); £3,773,935.98 -> £3,382,374.81 (10.4%); £3,773,936.24 -> £3,382,374.83 (10.4%); £3,773,936.50 -> £3,382,374.86 (10.4%); £3,773,936.76 -> £3,382,375.08 (10.4%); £3,773,937.02 -> £3,382,375.30 (10.4%); £3,773,937.28 -> £3,382,375.53 (10.4%); £3,773,937.52 -> £3,382,375.75 (10.4%); £3,773,937.77 -> £3,382,375.98 (10.4%); £3,773,938.03 -> £3,382,376.20 (10.4%); £3,773,938.22 -> £3,382,376.41 (10.4%); £3,773,938.47 -> £3,382,376.63 (10.4%); £3,773,938.72 -> £3,382,376.85 (10.4%); £3,773,938.97 -> £3,382,377.07 (10.4%); £3,773,939.23 -> £3,382,377.28 (10.4%); £3,773,939.48 -> £3,382,377.31 (10.4%); £3,773,939.73 -> £3,382,377.34 (10.4%); £3,773,939.97 -> £3,382,377.37 (10.4%); £3,773,940.19 -> £3,382,377.39 (10.4%); £3,773,940.39 -> £3,382,377.41 (10.4%); £3,773,940.54 -> £3,382,377.43 (10.4%); £3,773,940.69 -> £3,382,377.44 (10.4%); £3,773,940.85 -> £3,382,377.46 (10.4%); £3,773,941.00 -> £3,382,377.48 (10.4%); £3,773,941.15 -> £3,382,377.50 (10.4%); £3,773,941.31 -> £3,382,377.51 (10.4%); £3,773,941.46 -> £3,382,377.53 (10.4%); £3,773,941.61 -> £3,382,377.55 (10.4%); £3,773,941.77 -> £3,382,377.56 (10.4%); £3,773,941.91 -> £3,382,377.58 (10.4%); £3,773,942.07 -> £3,382,377.60 (10.4%); £3,773,942.23 -> £3,382,377.80 (10.4%); £3,773,942.38 -> £3,382,378.01 (10.4%); £3,773,942.54 -> £3,382,378.22 (10.4%); £3,773,942.72 -> £3,382,378.43 (10.4%); £3,773,942.92 -> £3,382,378.65 (10.4%); £3,773,943.15 -> £3,382,378.86 (10.4%); £3,773,943.38 -> £3,382,379.07 (10.4%); £3,773,943.62 -> £3,382,379.29 (10.4%); £3,773,943.88 -> £3,382,379.31 (10.4%); £3,773,944.13 -> £3,382,379.33 (10.4%); £3,773,944.39 -> £3,382,379.36 (10.4%); £3,773,944.64 -> £3,382,379.38 (10.4%); £3,773,944.90 -> £3,382,379.41 (10.4%); £3,773,945.16 -> £3,382,379.43 (10.4%); £3,773,945.41 -> £3,382,379.45 (10.4%); £3,773,945.68 -> £3,382,379.48 (10.4%); £3,773,945.93 -> £3,382,379.50 (10.4%); £3,773,946.19 -> £3,382,379.52 (10.4%); £3,773,946.44 -> £3,382,379.55 (10.4%); £3,773,946.69 -> £3,382,379.57 (10.4%); £3,773,946.94 -> £3,382,379.60 (10.4%); £3,773,947.13 -> £3,382,379.81 (10.4%); £3,773,947.32 -> £3,382,380.02 (10.4%); £3,773,947.56 -> £3,382,380.23 (10.4%); £3,773,947.75 -> £3,382,380.44 (10.4%); £3,773,947.95 -> £3,382,380.66 (10.4%); £3,773,948.21 -> £3,382,380.87 (10.4%); £3,773,948.46 -> £3,382,381.09 (10.4%); £3,773,948.71 -> £3,382,381.30 (10.4%); £3,773,948.97 -> £3,382,381.51 (10.4%); £3,773,949.23 -> £3,382,381.72 (10.4%); £3,773,949.49 -> £3,382,381.93 (10.4%); £3,773,949.74 -> £3,382,381.96 (10.4%); £3,773,949.99 -> £3,382,381.99 (10.4%); £3,773,950.22 -> £3,382,382.01 (10.4%); £3,773,950.43 -> £3,382,382.04 (10.4%); £3,773,950.63 -> £3,382,382.06 (10.4%); £3,773,950.78 -> £3,382,382.08 (10.4%); £3,773,950.94 -> £3,382,382.09 (10.4%); £3,773,951.09 -> £3,382,382.11 (10.4%); £3,773,951.24 -> £3,382,382.13 (10.4%); £3,773,951.39 -> £3,382,382.14 (10.4%); £3,773,951.55 -> £3,382,382.16 (10.4%); £3,773,951.69 -> £3,382,382.18 (10.4%); £3,773,951.85 -> £3,382,382.19 (10.4%); £3,773,952.00 -> £3,382,382.21 (10.4%); £3,773,952.15 -> £3,382,382.23 (10.4%); £3,773,952.30 -> £3,382,382.24 (10.4%); £3,773,952.45 -> £3,382,382.43 (10.4%); £3,773,952.60 -> £3,382,382.60 (10.4%); £3,773,952.77 -> £3,382,382.78 (10.4%); £3,773,952.95 -> £3,382,382.95 (10.4%); £3,773,953.15 -> £3,382,383.13 (10.4%); £3,773,953.37 -> £3,382,383.31 (10.4%); £3,773,953.62 -> £3,382,383.49 (10.4%); £3,773,953.86 -> £3,382,383.67 (10.4%); £3,773,954.11 -> £3,382,383.69 (10.4%); £3,773,954.36 -> £3,382,383.72 (10.4%); £3,773,954.62 -> £3,382,383.74 (10.4%); £3,773,954.87 -> £3,382,383.76 (10.4%); £3,773,955.12 -> £3,382,383.79 (10.4%); £3,773,955.37 -> £3,382,383.81 (10.4%); £3,773,955.64 -> £3,382,383.84 (10.4%); £3,773,955.89 -> £3,382,383.86 (10.4%); £3,773,956.14 -> £3,382,383.88 (10.4%); £3,773,956.40 -> £3,382,383.90 (10.4%); £3,773,956.64 -> £3,382,383.93 (10.4%); £3,773,956.90 -> £3,382,383.95 (10.4%); £3,773,957.14 -> £3,382,383.98 (10.4%); £3,773,957.39 -> £3,382,384.16 (10.4%); £3,773,957.58 -> £3,382,384.36 (10.4%); £3,773,957.83 -> £3,382,384.55 (10.4%); £3,773,958.09 -> £3,382,384.74 (10.4%); £3,773,958.28 -> £3,382,384.93 (10.4%); £3,773,958.53 -> £3,382,385.12 (10.4%); £3,773,958.71 -> £3,382,385.31 (10.4%); £3,773,958.96 -> £3,382,385.50 (10.4%); £3,773,959.21 -> £3,382,385.69 (10.4%); £3,773,959.47 -> £3,382,385.88 (10.4%); £3,773,959.71 -> £3,382,386.06 (10.4%); £3,773,959.96 -> £3,382,386.09 (10.4%); £3,773,960.21 -> £3,382,386.12 (10.4%); £3,773,960.45 -> £3,382,386.15 (10.4%); £3,773,960.66 -> £3,382,386.17 (10.4%); £3,773,960.85 -> £3,382,386.19 (10.4%); £3,773,961.01 -> £3,382,386.21 (10.4%); £3,773,961.16 -> £3,382,386.22 (10.4%); £3,773,961.30 -> £3,382,386.24 (10.4%); £3,773,961.45 -> £3,382,386.26 (10.4%); £3,773,961.60 -> £3,382,386.28 (10.4%); £3,773,961.76 -> £3,382,386.29 (10.4%); £3,773,961.91 -> £3,382,386.31 (10.4%); £3,773,962.06 -> £3,382,386.32 (10.4%); £3,773,962.20 -> £3,382,386.34 (10.4%); £3,773,962.35 -> £3,382,386.36 (10.4%); £3,773,962.50 -> £3,382,386.38 (10.4%); £3,773,962.65 -> £3,382,386.54 (10.4%); £3,773,962.80 -> £3,382,386.70 (10.4%); £3,773,962.97 -> £3,382,386.86 (10.4%); £3,773,963.15 -> £3,382,387.02 (10.4%); £3,773,963.35 -> £3,382,387.19 (10.4%); £3,773,963.56 -> £3,382,387.36 (10.4%); £3,773,963.78 -> £3,382,387.52 (10.4%); £3,773,964.04 -> £3,382,387.68 (10.4%); £3,773,964.29 -> £3,382,387.71 (10.4%); £3,773,964.54 -> £3,382,387.73 (10.4%); £3,773,964.79 -> £3,382,387.75 (10.4%); £3,773,965.05 -> £3,382,387.78 (10.4%); £3,773,965.29 -> £3,382,387.80 (10.4%); £3,773,965.54 -> £3,382,387.82 (10.4%); £3,773,965.78 -> £3,382,387.85 (10.4%); £3,773,966.02 -> £3,382,387.87 (10.4%); £3,773,966.27 -> £3,382,387.89 (10.4%); £3,773,966.52 -> £3,382,387.92 (10.4%); £3,773,966.77 -> £3,382,387.94 (10.4%); £3,773,967.02 -> £3,382,387.97 (10.4%); £3,773,967.27 -> £3,382,387.99 (10.4%); £3,773,967.46 -> £3,382,388.16 (10.4%); £3,773,967.64 -> £3,382,388.33 (10.4%); £3,773,967.82 -> £3,382,388.51 (10.4%); £3,773,968.01 -> £3,382,388.68 (10.4%); £3,773,968.19 -> £3,382,388.85 (10.4%); £3,773,968.38 -> £3,382,389.03 (10.4%); £3,773,968.56 -> £3,382,389.20 (10.4%); £3,773,968.81 -> £3,382,389.37 (10.4%); £3,773,969.06 -> £3,382,389.54 (10.4%); £3,773,969.31 -> £3,382,389.71 (10.4%); £3,773,969.56 -> £3,382,389.88 (10.4%); £3,773,969.81 -> £3,382,389.91 (10.4%); £3,773,970.06 -> £3,382,389.94 (10.4%); £3,773,970.29 -> £3,382,389.96 (10.4%); £3,773,970.50 -> £3,382,389.98 (10.4%); £3,773,970.69 -> £3,382,390.00 (10.4%); £3,773,970.84 -> £3,382,390.02 (10.4%); £3,773,970.99 -> £3,382,390.04 (10.4%); £3,773,971.14 -> £3,382,390.06 (10.4%); £3,773,971.28 -> £3,382,390.07 (10.4%); £3,773,971.43 -> £3,382,390.09 (10.4%); £3,773,971.57 -> £3,382,390.11 (10.4%); £3,773,971.72 -> £3,382,390.12 (10.4%); £3,773,971.87 -> £3,382,390.14 (10.4%); £3,773,972.02 -> £3,382,390.16 (10.4%); £3,773,972.17 -> £3,382,390.17 (10.4%); £3,773,972.32 -> £3,382,390.19 (10.4%); £3,773,972.46 -> £3,382,390.37 (10.4%); £3,773,972.61 -> £3,382,390.55 (10.4%); £3,773,972.78 -> £3,382,390.74 (10.4%); £3,773,972.96 -> £3,382,390.92 (10.4%); £3,773,973.16 -> £3,382,391.11 (10.4%); £3,773,973.37 -> £3,382,391.30 (10.4%); £3,773,973.60 -> £3,382,391.48 (10.4%); £3,773,973.84 -> £3,382,391.66 (10.4%); £3,773,974.08 -> £3,382,391.68 (10.4%); £3,773,974.32 -> £3,382,391.70 (10.4%); £3,773,974.57 -> £3,382,391.73 (10.4%); £3,773,974.81 -> £3,382,391.75 (10.4%); £3,773,975.06 -> £3,382,391.77 (10.4%); £3,773,975.31 -> £3,382,391.80 (10.4%); £3,773,975.55 -> £3,382,391.82 (10.4%); £3,773,975.80 -> £3,382,391.84 (10.4%); £3,773,976.04 -> £3,382,391.87 (10.4%); £3,773,976.27 -> £3,382,391.89 (10.4%); £3,773,976.52 -> £3,382,391.91 (10.4%); £3,773,976.77 -> £3,382,391.94 (10.4%); £3,773,977.01 -> £3,382,391.97 (10.4%); £3,773,977.20 -> £3,382,392.15 (10.4%); £3,773,977.38 -> £3,382,392.34 (10.4%); £3,773,977.56 -> £3,382,392.52 (10.4%); £3,773,977.75 -> £3,382,392.72 (10.4%); £3,773,977.93 -> £3,382,392.91 (10.4%); £3,773,978.11 -> £3,382,393.10 (10.4%); £3,773,978.30 -> £3,382,393.29 (10.4%); £3,773,978.54 -> £3,382,393.48 (10.4%); £3,773,978.78 -> £3,382,393.66 (10.4%); £3,773,979.03 -> £3,382,393.85 (10.4%); £3,773,979.27 -> £3,382,394.04 (10.4%); £3,773,979.53 -> £3,382,394.07 (10.4%); £3,773,979.78 -> £3,382,394.10 (10.4%); £3,773,980.01 -> £3,382,394.12 (10.4%); £3,773,980.22 -> £3,382,394.14 (10.4%); £3,773,980.41 -> £3,382,394.16 (10.4%); £3,773,980.54 -> £3,382,394.18 (10.4%); £3,773,980.67 -> £3,382,394.20 (10.4%); £3,773,980.80 -> £3,382,394.22 (10.4%); £3,773,980.93 -> £3,382,394.24 (10.4%); £3,773,981.06 -> £3,382,394.25 (10.4%); £3,773,981.19 -> £3,382,394.27 (10.4%); £3,773,981.32 -> £3,382,394.29 (10.4%); £3,773,981.45 -> £3,382,394.30 (10.4%); £3,773,981.57 -> £3,382,394.32 (10.4%); £3,773,981.70 -> £3,382,394.34 (10.4%); £3,773,981.83 -> £3,382,394.35 (10.4%); £3,773,981.96 -> £3,382,394.53 (10.4%); £3,773,982.08 -> £3,382,394.70 (10.4%); £3,773,982.22 -> £3,382,394.88 (10.4%); £3,773,982.38 -> £3,382,395.05 (10.4%); £3,773,982.56 -> £3,382,395.23 (10.4%); £3,773,982.74 -> £3,382,395.40 (10.4%); £3,773,982.94 -> £3,382,395.59 (10.4%); £3,773,983.15 -> £3,382,395.76 (10.4%); £3,773,983.36 -> £3,382,395.79 (10.4%); £3,773,983.56 -> £3,382,395.82 (10.4%); £3,773,983.78 -> £3,382,395.84 (10.4%); £3,773,983.99 -> £3,382,395.87 (10.4%); £3,773,984.20 -> £3,382,395.90 (10.4%); £3,773,984.42 -> £3,382,395.92 (10.4%); £3,773,984.63 -> £3,382,395.95 (10.4%); £3,773,984.84 -> £3,382,395.97 (10.4%); £3,773,985.05 -> £3,382,396.00 (10.4%); £3,773,985.26 -> £3,382,396.02 (10.4%); £3,773,985.48 -> £3,382,396.05 (10.4%); £3,773,985.69 -> £3,382,396.08 (10.4%); £3,773,985.91 -> £3,382,396.10 (10.4%); £3,773,986.06 -> £3,382,396.28 (10.4%); £3,773,986.23 -> £3,382,396.45 (10.4%); £3,773,986.39 -> £3,382,396.64 (10.4%); £3,773,986.55 -> £3,382,396.82 (10.4%); £3,773,986.71 -> £3,382,397.00 (10.4%); £3,773,986.86 -> £3,382,397.19 (10.4%); £3,773,987.07 -> £3,382,397.38 (10.4%); £3,773,987.29 -> £3,382,397.55 (10.4%); £3,773,987.50 -> £3,382,397.74 (10.4%); £3,773,987.72 -> £3,382,397.92 (10.4%); £3,773,987.92 -> £3,382,398.10 (10.4%); £3,773,988.14 -> £3,382,398.12 (10.4%); £3,773,988.35 -> £3,382,398.15 (10.4%); £3,773,988.55 -> £3,382,398.18 (10.4%); £3,773,988.73 -> £3,382,398.20 (10.4%); £3,773,988.89 -> £3,382,398.22 (10.4%); £3,773,989.01 -> £3,382,398.24 (10.4%); £3,773,989.14 -> £3,382,398.26 (10.4%); £3,773,989.27 -> £3,382,398.28 (10.4%); £3,773,989.39 -> £3,382,398.30 (10.4%); £3,773,989.52 -> £3,382,398.32 (10.4%); £3,773,989.65 -> £3,382,398.33 (10.4%); £3,773,989.77 -> £3,382,398.35 (10.4%); £3,773,989.90 -> £3,382,398.37 (10.4%); £3,773,990.03 -> £3,382,398.38 (10.4%); £3,773,990.15 -> £3,382,398.40 (10.4%); £3,773,990.28 -> £3,382,398.42 (10.4%); £3,773,990.40 -> £3,382,398.63 (10.4%); £3,773,990.53 -> £3,382,398.84 (10.4%); £3,773,990.67 -> £3,382,399.06 (10.4%); £3,773,990.83 -> £3,382,399.28 (10.4%); £3,773,991.00 -> £3,382,399.49 (10.4%); £3,773,991.19 -> £3,382,399.72 (10.4%); £3,773,991.38 -> £3,382,399.93 (10.4%); £3,773,991.59 -> £3,382,400.15 (10.4%); £3,773,991.80 -> £3,382,400.18 (10.4%); £3,773,992.01 -> £3,382,400.21 (10.4%); £3,773,992.22 -> £3,382,400.25 (10.4%); £3,773,992.43 -> £3,382,400.28 (10.4%); £3,773,992.65 -> £3,382,400.31 (10.4%); £3,773,992.86 -> £3,382,400.34 (10.4%); £3,773,993.07 -> £3,382,400.37 (10.4%); £3,773,993.28 -> £3,382,400.40 (10.4%); £3,773,993.49 -> £3,382,400.43 (10.4%); £3,773,993.70 -> £3,382,400.45 (10.4%); £3,773,993.91 -> £3,382,400.48 (10.4%); £3,773,994.12 -> £3,382,400.51 (10.4%); £3,773,994.33 -> £3,382,400.54 (10.4%); £3,773,994.49 -> £3,382,400.75 (10.4%); £3,773,994.65 -> £3,382,400.97 (10.4%); £3,773,994.81 -> £3,382,401.19 (10.4%); £3,773,994.97 -> £3,382,401.41 (10.4%); £3,773,995.13 -> £3,382,401.63 (10.4%); £3,773,995.29 -> £3,382,401.85 (10.4%); £3,773,995.45 -> £3,382,402.07 (10.4%); £3,773,995.67 -> £3,382,402.28 (10.4%); £3,773,995.89 -> £3,382,402.51 (10.4%); £3,773,996.09 -> £3,382,402.73 (10.4%); £3,773,996.30 -> £3,382,402.95 (10.4%); £3,773,996.51 -> £3,382,402.98 (10.4%); £3,773,996.72 -> £3,382,403.01 (10.4%); £3,773,996.92 -> £3,382,403.03 (10.4%); £3,773,997.10 -> £3,382,403.05 (10.4%); £3,773,997.26 -> £3,382,403.07 (10.4%); £3,773,997.41 -> £3,382,403.09 (10.4%); £3,773,997.56 -> £3,382,403.11 (10.4%); £3,773,997.71 -> £3,382,403.13 (10.4%); £3,773,997.86 -> £3,382,403.14 (10.4%); £3,773,998.00 -> £3,382,403.16 (10.4%); £3,773,998.14 -> £3,382,403.18 (10.4%); £3,773,998.29 -> £3,382,403.19 (10.4%); £3,773,998.44 -> £3,382,403.21 (10.4%); £3,773,998.58 -> £3,382,403.23 (10.4%); £3,773,998.73 -> £3,382,403.24 (10.4%); £3,773,998.87 -> £3,382,403.26 (10.4%); £3,773,999.01 -> £3,382,403.51 (10.4%); £3,773,999.16 -> £3,382,403.76 (10.4%); £3,773,999.32 -> £3,382,404.01 (10.4%); £3,773,999.49 -> £3,382,404.27 (10.4%); £3,773,999.68 -> £3,382,404.53 (10.4%); £3,773,999.89 -> £3,382,404.79 (10.4%); £3,774,000.11 -> £3,382,405.04 (10.4%); £3,774,000.35 -> £3,382,405.29 (10.4%); £3,774,000.59 -> £3,382,405.32 (10.4%); £3,774,000.83 -> £3,382,405.34 (10.4%); £3,774,001.08 -> £3,382,405.36 (10.4%); £3,774,001.32 -> £3,382,405.39 (10.4%); £3,774,001.57 -> £3,382,405.41 (10.4%); £3,774,001.81 -> £3,382,405.44 (10.4%); £3,774,002.05 -> £3,382,405.46 (10.4%); £3,774,002.29 -> £3,382,405.48 (10.4%); £3,774,002.53 -> £3,382,405.51 (10.4%); £3,774,002.78 -> £3,382,405.53 (10.4%); £3,774,003.02 -> £3,382,405.55 (10.4%); £3,774,003.26 -> £3,382,405.58 (10.4%); £3,774,003.50 -> £3,382,405.61 (10.4%); £3,774,003.69 -> £3,382,405.85 (10.4%); £3,774,003.87 -> £3,382,406.10 (10.4%); £3,774,004.06 -> £3,382,406.35 (10.4%); £3,774,004.24 -> £3,382,406.60 (10.4%); £3,774,004.42 -> £3,382,406.86 (10.4%); £3,774,004.60 -> £3,382,407.11 (10.4%); £3,774,004.77 -> £3,382,407.37 (10.4%); £3,774,005.01 -> £3,382,407.62 (10.4%); £3,774,005.25 -> £3,382,407.88 (10.4%); £3,774,005.49 -> £3,382,408.13 (10.4%); £3,774,005.73 -> £3,382,408.39 (10.4%); £3,774,005.98 -> £3,382,408.42 (10.4%); £3,774,006.22 -> £3,382,408.45 (10.4%); £3,774,006.44 -> £3,382,408.47 (10.4%); £3,774,006.65 -> £3,382,408.49 (10.4%); £3,774,006.84 -> £3,382,408.51 (10.4%); £3,774,006.98 -> £3,382,408.53 (10.4%); £3,774,007.12 -> £3,382,408.55 (10.4%); £3,774,007.27 -> £3,382,408.57 (10.4%); £3,774,007.41 -> £3,382,408.58 (10.4%); £3,774,007.55 -> £3,382,408.60 (10.4%); £3,774,007.69 -> £3,382,408.62 (10.4%); £3,774,007.83 -> £3,382,408.63 (10.4%); £3,774,007.97 -> £3,382,408.65 (10.4%); £3,774,008.11 -> £3,382,408.67 (10.4%); £3,774,008.26 -> £3,382,408.68 (10.4%); £3,774,008.40 -> £3,382,408.70 (10.4%); £3,774,008.55 -> £3,382,408.93 (10.4%); £3,774,008.70 -> £3,382,409.15 (10.4%); £3,774,008.86 -> £3,382,409.37 (10.4%); £3,774,009.03 -> £3,382,409.60 (10.4%); £3,774,009.22 -> £3,382,409.82 (10.4%); £3,774,009.44 -> £3,382,410.05 (10.4%); £3,774,009.66 -> £3,382,410.27 (10.4%); £3,774,009.90 -> £3,382,410.49 (10.4%); £3,774,010.15 -> £3,382,410.52 (10.4%); £3,774,010.38 -> £3,382,410.54 (10.4%); £3,774,010.62 -> £3,382,410.56 (10.4%); £3,774,010.85 -> £3,382,410.59 (10.4%); £3,774,011.09 -> £3,382,410.61 (10.4%); £3,774,011.33 -> £3,382,410.64 (10.4%); £3,774,011.57 -> £3,382,410.66 (10.4%); £3,774,011.80 -> £3,382,410.68 (10.4%); £3,774,012.04 -> £3,382,410.71 (10.4%); £3,774,012.27 -> £3,382,410.73 (10.4%); £3,774,012.51 -> £3,382,410.75 (10.4%); £3,774,012.74 -> £3,382,410.78 (10.4%); £3,774,012.98 -> £3,382,410.81 (10.4%); £3,774,013.17 -> £3,382,411.03 (10.4%); £3,774,013.35 -> £3,382,411.27 (10.4%); £3,774,013.54 -> £3,382,411.50 (10.4%); £3,774,013.79 -> £3,382,411.75 (10.4%); £3,774,014.03 -> £3,382,411.98 (10.4%); £3,774,014.28 -> £3,382,412.22 (10.4%); £3,774,014.46 -> £3,382,412.45 (10.4%); £3,774,014.70 -> £3,382,412.68 (10.4%); £3,774,014.94 -> £3,382,412.91 (10.4%); £3,774,015.18 -> £3,382,413.13 (10.4%); £3,774,015.42 -> £3,382,413.35 (10.4%); £3,774,015.67 -> £3,382,413.38 (10.4%); £3,774,015.91 -> £3,382,413.41 (10.4%); £3,774,016.13 -> £3,382,413.43 (10.4%); £3,774,016.33 -> £3,382,413.46 (10.4%); £3,774,016.51 -> £3,382,413.48 (10.4%); £3,774,016.65 -> £3,382,413.49 (10.4%); £3,774,016.79 -> £3,382,413.51 (10.4%); £3,774,016.93 -> £3,382,413.53 (10.4%); £3,774,017.07 -> £3,382,413.55 (10.4%); £3,774,017.21 -> £3,382,413.56 (10.4%); £3,774,017.36 -> £3,382,413.58 (10.4%); £3,774,017.50 -> £3,382,413.60 (10.4%); £3,774,017.64 -> £3,382,413.61 (10.4%); £3,774,017.78 -> £3,382,413.63 (10.4%); £3,774,017.92 -> £3,382,413.65 (10.4%); £3,774,018.06 -> £3,382,413.66 (10.4%); £3,774,018.20 -> £3,382,413.91 (10.4%); £3,774,018.35 -> £3,382,414.15 (10.4%); £3,774,018.50 -> £3,382,414.40 (10.4%); £3,774,018.68 -> £3,382,414.66 (10.4%); £3,774,018.87 -> £3,382,414.90 (10.4%); £3,774,019.07 -> £3,382,415.15 (10.4%); £3,774,019.29 -> £3,382,415.40 (10.4%); £3,774,019.53 -> £3,382,415.65 (10.4%); £3,774,019.76 -> £3,382,415.67 (10.4%); £3,774,020.00 -> £3,382,415.70 (10.4%); £3,774,020.24 -> £3,382,415.72 (10.4%); £3,774,020.47 -> £3,382,415.74 (10.4%); £3,774,020.71 -> £3,382,415.77 (10.4%); £3,774,020.95 -> £3,382,415.79 (10.4%); £3,774,021.18 -> £3,382,415.82 (10.4%); £3,774,021.42 -> £3,382,415.84 (10.4%); £3,774,021.66 -> £3,382,415.86 (10.4%); £3,774,021.90 -> £3,382,415.88 (10.4%); £3,774,022.14 -> £3,382,415.91 (10.4%); £3,774,022.38 -> £3,382,415.93 (10.4%); £3,774,022.61 -> £3,382,415.96 (10.4%); £3,774,022.79 -> £3,382,416.20 (10.4%); £3,774,022.97 -> £3,382,416.45 (10.4%); £3,774,023.20 -> £3,382,416.70 (10.4%); £3,774,023.44 -> £3,382,416.95 (10.4%); £3,774,023.68 -> £3,382,417.21 (10.4%); £3,774,023.92 -> £3,382,417.46 (10.4%); £3,774,024.16 -> £3,382,417.71 (10.4%); £3,774,024.40 -> £3,382,417.96 (10.4%); £3,774,024.64 -> £3,382,418.20 (10.4%); £3,774,024.88 -> £3,382,418.44 (10.4%); £3,774,025.12 -> £3,382,418.68 (10.4%); £3,774,025.34 -> £3,382,418.70 (10.4%); £3,774,025.58 -> £3,382,418.73 (10.4%); £3,774,025.79 -> £3,382,418.76 (10.4%); £3,774,025.99 -> £3,382,418.78 (10.4%); £3,774,026.17 -> £3,382,418.80 (10.4%); £3,774,026.31 -> £3,382,418.82 (10.4%); £3,774,026.45 -> £3,382,418.84 (10.4%); £3,774,026.59 -> £3,382,418.85 (10.4%); £3,774,026.73 -> £3,382,418.87 (10.4%); £3,774,026.87 -> £3,382,418.89 (10.4%); £3,774,027.01 -> £3,382,418.90 (10.4%); £3,774,027.15 -> £3,382,418.92 (10.4%); £3,774,027.30 -> £3,382,418.93 (10.4%); £3,774,027.45 -> £3,382,418.95 (10.4%); £3,774,027.59 -> £3,382,418.97 (10.4%); £3,774,027.73 -> £3,382,418.99 (10.4%); £3,774,027.88 -> £3,382,419.25 (10.4%); £3,774,028.02 -> £3,382,419.52 (10.4%); £3,774,028.18 -> £3,382,419.79 (10.4%); £3,774,028.35 -> £3,382,420.06 (10.4%); £3,774,028.54 -> £3,382,420.34 (10.4%); £3,774,028.74 -> £3,382,420.61 (10.4%); £3,774,028.96 -> £3,382,420.88 (10.4%); £3,774,029.20 -> £3,382,421.15 (10.4%); £3,774,029.43 -> £3,382,421.17 (10.4%); £3,774,029.67 -> £3,382,421.20 (10.4%); £3,774,029.89 -> £3,382,421.22 (10.4%); £3,774,030.13 -> £3,382,421.24 (10.4%); £3,774,030.35 -> £3,382,421.27 (10.4%); £3,774,030.60 -> £3,382,421.29 (10.4%); £3,774,030.84 -> £3,382,421.32 (10.4%); £3,774,031.08 -> £3,382,421.34 (10.4%); £3,774,031.31 -> £3,382,421.36 (10.4%); £3,774,031.55 -> £3,382,421.38 (10.4%); £3,774,031.78 -> £3,382,421.41 (10.4%); £3,774,032.02 -> £3,382,421.43 (10.4%); £3,774,032.25 -> £3,382,421.46 (10.4%); £3,774,032.44 -> £3,382,421.73 (10.4%); £3,774,032.61 -> £3,382,422.00 (10.4%); £3,774,032.79 -> £3,382,422.28 (10.4%); £3,774,032.96 -> £3,382,422.55 (10.4%); £3,774,033.14 -> £3,382,422.83 (10.4%); £3,774,033.32 -> £3,382,423.10 (10.4%); £3,774,033.50 -> £3,382,423.38 (10.4%); £3,774,033.72 -> £3,382,423.64 (10.4%); £3,774,033.96 -> £3,382,423.91 (10.4%); £3,774,034.20 -> £3,382,424.19 (10.4%); £3,774,034.42 -> £3,382,424.46 (10.4%); £3,774,034.66 -> £3,382,424.49 (10.4%); £3,774,034.90 -> £3,382,424.52 (10.4%); £3,774,035.12 -> £3,382,424.54 (10.4%); £3,774,035.33 -> £3,382,424.57 (10.4%); £3,774,035.51 -> £3,382,424.59 (10.4%); £3,774,035.66 -> £3,382,424.60 (10.4%); £3,774,035.80 -> £3,382,424.62 (10.4%); £3,774,035.94 -> £3,382,424.64 (10.4%); £3,774,036.09 -> £3,382,424.66 (10.4%); £3,774,036.23 -> £3,382,424.67 (10.4%); £3,774,036.37 -> £3,382,424.69 (10.4%); £3,774,036.52 -> £3,382,424.71 (10.4%); £3,774,036.66 -> £3,382,424.72 (10.4%); £3,774,036.80 -> £3,382,424.74 (10.4%); £3,774,036.95 -> £3,382,424.76 (10.4%); £3,774,037.09 -> £3,382,424.77 (10.4%); £3,774,037.23 -> £3,382,425.00 (10.4%); £3,774,037.38 -> £3,382,425.23 (10.4%); £3,774,037.54 -> £3,382,425.46 (10.4%); £3,774,037.72 -> £3,382,425.69 (10.4%); £3,774,037.90 -> £3,382,425.93 (10.4%); £3,774,038.11 -> £3,382,426.16 (10.4%); £3,774,038.33 -> £3,382,426.39 (10.4%); £3,774,038.57 -> £3,382,426.62 (10.4%); £3,774,038.80 -> £3,382,426.64 (10.4%); £3,774,039.03 -> £3,382,426.67 (10.4%); £3,774,039.27 -> £3,382,426.69 (10.4%); £3,774,039.51 -> £3,382,426.71 (10.4%); £3,774,039.76 -> £3,382,426.74 (10.4%); £3,774,039.99 -> £3,382,426.76 (10.4%); £3,774,040.24 -> £3,382,426.79 (10.4%); £3,774,040.47 -> £3,382,426.81 (10.4%); £3,774,040.70 -> £3,382,426.83 (10.4%); £3,774,040.94 -> £3,382,426.86 (10.4%); £3,774,041.18 -> £3,382,426.88 (10.4%); £3,774,041.42 -> £3,382,426.91 (10.4%); £3,774,041.66 -> £3,382,426.93 (10.4%); £3,774,041.89 -> £3,382,427.16 (10.4%); £3,774,042.07 -> £3,382,427.40 (10.4%); £3,774,042.24 -> £3,382,427.63 (10.4%); £3,774,042.42 -> £3,382,427.87 (10.4%); £3,774,042.60 -> £3,382,428.11 (10.4%); £3,774,042.85 -> £3,382,428.35 (10.4%); £3,774,043.09 -> £3,382,428.58 (10.4%); £3,774,043.33 -> £3,382,428.82 (10.4%); £3,774,043.58 -> £3,382,429.06 (10.4%); £3,774,043.82 -> £3,382,429.29 (10.4%); £3,774,044.06 -> £3,382,429.52 (10.4%); £3,774,044.30 -> £3,382,429.55 (10.4%); £3,774,044.54 -> £3,382,429.57 (10.4%); £3,774,044.76 -> £3,382,429.60 (10.4%); £3,774,044.97 -> £3,382,429.62 (10.4%); £3,774,045.16 -> £3,382,429.64 (10.4%); £3,774,045.29 -> £3,382,429.66 (10.4%); £3,774,045.41 -> £3,382,429.68 (10.4%); £3,774,045.54 -> £3,382,429.70 (10.4%); £3,774,045.67 -> £3,382,429.71 (10.4%); £3,774,045.80 -> £3,382,429.73 (10.4%); £3,774,045.93 -> £3,382,429.75 (10.4%); £3,774,046.06 -> £3,382,429.77 (10.4%); £3,774,046.18 -> £3,382,429.78 (10.4%); £3,774,046.31 -> £3,382,429.80 (10.4%); £3,774,046.44 -> £3,382,429.82 (10.4%); £3,774,046.56 -> £3,382,429.83 (10.4%); £3,774,046.70 -> £3,382,430.01 (10.4%); £3,774,046.83 -> £3,382,430.18 (10.4%); £3,774,046.97 -> £3,382,430.36 (10.4%); £3,774,047.13 -> £3,382,430.55 (10.4%); £3,774,047.30 -> £3,382,430.73 (10.4%); £3,774,047.49 -> £3,382,430.92 (10.4%); £3,774,047.69 -> £3,382,431.10 (10.4%); £3,774,047.90 -> £3,382,431.28 (10.4%); £3,774,048.12 -> £3,382,431.31 (10.4%); £3,774,048.34 -> £3,382,431.34 (10.4%); £3,774,048.55 -> £3,382,431.36 (10.4%); £3,774,048.76 -> £3,382,431.39 (10.4%); £3,774,048.97 -> £3,382,431.42 (10.4%); £3,774,049.19 -> £3,382,431.44 (10.4%); £3,774,049.40 -> £3,382,431.47 (10.4%); £3,774,049.62 -> £3,382,431.50 (10.4%); £3,774,049.83 -> £3,382,431.52 (10.4%); £3,774,050.05 -> £3,382,431.55 (10.4%); £3,774,050.26 -> £3,382,431.57 (10.4%); £3,774,050.47 -> £3,382,431.60 (10.4%); £3,774,050.69 -> £3,382,431.63 (10.4%); £3,774,050.85 -> £3,382,431.81 (10.4%); £3,774,051.01 -> £3,382,431.99 (10.4%); £3,774,051.18 -> £3,382,432.18 (10.4%); £3,774,051.34 -> £3,382,432.37 (10.4%); £3,774,051.50 -> £3,382,432.56 (10.4%); £3,774,051.67 -> £3,382,432.75 (10.4%); £3,774,051.83 -> £3,382,432.94 (10.4%); £3,774,052.04 -> £3,382,433.12 (10.4%); £3,774,052.25 -> £3,382,433.31 (10.4%); £3,774,052.47 -> £3,382,433.49 (10.4%); £3,774,052.68 -> £3,382,433.67 (10.4%); £3,774,052.90 -> £3,382,433.70 (10.4%); £3,774,053.11 -> £3,382,433.73 (10.4%); £3,774,053.31 -> £3,382,433.75 (10.4%); £3,774,053.50 -> £3,382,433.78 (10.4%); £3,774,053.66 -> £3,382,433.80 (10.4%); £3,774,053.79 -> £3,382,433.82 (10.4%); £3,774,053.92 -> £3,382,433.84 (10.4%); £3,774,054.05 -> £3,382,433.86 (10.4%); £3,774,054.18 -> £3,382,433.87 (10.4%); £3,774,054.31 -> £3,382,433.89 (10.4%); £3,774,054.44 -> £3,382,433.91 (10.4%); £3,774,054.56 -> £3,382,433.92 (10.4%); £3,774,054.69 -> £3,382,433.94 (10.4%); £3,774,054.82 -> £3,382,433.96 (10.4%); £3,774,054.94 -> £3,382,433.97 (10.4%); £3,774,055.08 -> £3,382,433.99 (10.4%); £3,774,055.21 -> £3,382,434.11 (10.4%); £3,774,055.33 -> £3,382,434.22 (10.4%); £3,774,055.48 -> £3,382,434.33 (10.4%); £3,774,055.64 -> £3,382,434.44 (10.4%); £3,774,055.81 -> £3,382,434.57 (10.4%); £3,774,055.99 -> £3,382,434.69 (10.4%); £3,774,056.20 -> £3,382,434.81 (10.4%); £3,774,056.42 -> £3,382,434.94 (10.4%); £3,774,056.63 -> £3,382,434.97 (10.4%); £3,774,056.85 -> £3,382,435.00 (10.4%); £3,774,057.07 -> £3,382,435.03 (10.4%); £3,774,057.28 -> £3,382,435.06 (10.4%); £3,774,057.49 -> £3,382,435.09 (10.4%); £3,774,057.71 -> £3,382,435.12 (10.4%); £3,774,057.92 -> £3,382,435.15 (10.4%); £3,774,058.13 -> £3,382,435.18 (10.4%); £3,774,058.35 -> £3,382,435.21 (10.4%); £3,774,058.56 -> £3,382,435.24 (10.4%); £3,774,058.78 -> £3,382,435.27 (10.4%); £3,774,059.00 -> £3,382,435.30 (10.4%); £3,774,059.22 -> £3,382,435.33 (10.4%); £3,774,059.38 -> £3,382,435.45 (10.4%); £3,774,059.54 -> £3,382,435.59 (10.4%); £3,774,059.69 -> £3,382,435.72 (10.4%); £3,774,059.85 -> £3,382,435.85 (10.4%); £3,774,060.01 -> £3,382,435.98 (10.4%); £3,774,060.18 -> £3,382,436.11 (10.4%); £3,774,060.33 -> £3,382,436.24 (10.4%); £3,774,060.55 -> £3,382,436.37 (10.4%); £3,774,060.76 -> £3,382,436.50 (10.4%); £3,774,060.98 -> £3,382,436.63 (10.4%); £3,774,061.19 -> £3,382,436.75 (10.4%); £3,774,061.40 -> £3,382,436.78 (10.4%); £3,774,061.63 -> £3,382,436.81 (10.4%); £3,774,061.82 -> £3,382,436.83 (10.4%); £3,774,061.99 -> £3,382,436.85 (10.4%); £3,774,062.16 -> £3,382,436.87 (10.4%); £3,774,062.31 -> £3,382,436.89 (10.4%); £3,774,062.45 -> £3,382,436.91 (10.4%); £3,774,062.60 -> £3,382,436.93 (10.4%); £3,774,062.75 -> £3,382,436.94 (10.4%); £3,774,062.89 -> £3,382,436.96 (10.4%); £3,774,063.04 -> £3,382,436.98 (10.4%); £3,774,063.18 -> £3,382,436.99 (10.4%); £3,774,063.34 -> £3,382,437.01 (10.4%); £3,774,063.48 -> £3,382,437.03 (10.4%); £3,774,063.62 -> £3,382,437.04 (10.4%); £3,774,063.77 -> £3,382,437.06 (10.4%); £3,774,063.91 -> £3,382,437.19 (10.4%); £3,774,064.06 -> £3,382,437.32 (10.4%); £3,774,064.22 -> £3,382,437.46 (10.4%); £3,774,064.40 -> £3,382,437.60 (10.4%); £3,774,064.60 -> £3,382,437.74 (10.4%); £3,774,064.81 -> £3,382,437.87 (10.4%); £3,774,065.04 -> £3,382,438.01 (10.4%); £3,774,065.30 -> £3,382,438.14 (10.4%); £3,774,065.54 -> £3,382,438.17 (10.4%); £3,774,065.79 -> £3,382,438.19 (10.4%); £3,774,066.04 -> £3,382,438.22 (10.4%); £3,774,066.28 -> £3,382,438.24 (10.4%); £3,774,066.53 -> £3,382,438.26 (10.4%); £3,774,066.79 -> £3,382,438.29 (10.4%); £3,774,067.03 -> £3,382,438.31 (10.4%); £3,774,067.28 -> £3,382,438.33 (10.4%); £3,774,067.53 -> £3,382,438.36 (10.4%); £3,774,067.78 -> £3,382,438.38 (10.4%); £3,774,068.03 -> £3,382,438.41 (10.4%); £3,774,068.28 -> £3,382,438.43 (10.4%); £3,774,068.53 -> £3,382,438.46 (10.4%); £3,774,068.77 -> £3,382,438.60 (10.4%); £3,774,068.96 -> £3,382,438.75 (10.4%); £3,774,069.13 -> £3,382,438.90 (10.4%); £3,774,069.33 -> £3,382,439.05 (10.4%); £3,774,069.50 -> £3,382,439.20 (10.4%); £3,774,069.68 -> £3,382,439.35 (10.4%); £3,774,069.87 -> £3,382,439.50 (10.4%); £3,774,070.11 -> £3,382,439.64 (10.4%); £3,774,070.35 -> £3,382,439.78 (10.4%); £3,774,070.60 -> £3,382,439.93 (10.4%); £3,774,070.85 -> £3,382,440.07 (10.4%); £3,774,071.09 -> £3,382,440.10 (10.4%); £3,774,071.33 -> £3,382,440.13 (10.4%); £3,774,071.56 -> £3,382,440.15 (10.4%); £3,774,071.77 -> £3,382,440.18 (10.4%); £3,774,071.97 -> £3,382,440.20 (10.4%); £3,774,072.11 -> £3,382,440.22 (10.4%); £3,774,072.26 -> £3,382,440.23 (10.4%); £3,774,072.41 -> £3,382,440.25 (10.4%); £3,774,072.55 -> £3,382,440.27 (10.4%); £3,774,072.70 -> £3,382,440.29 (10.4%); £3,774,072.85 -> £3,382,440.30 (10.4%); £3,774,073.00 -> £3,382,440.32 (10.4%); £3,774,073.15 -> £3,382,440.34 (10.4%); £3,774,073.29 -> £3,382,440.35 (10.4%); £3,774,073.44 -> £3,382,440.37 (10.4%); £3,774,073.59 -> £3,382,440.39 (10.4%); £3,774,073.74 -> £3,382,440.51 (10.4%); £3,774,073.89 -> £3,382,440.63 (10.4%); £3,774,074.05 -> £3,382,440.76 (10.4%); £3,774,074.24 -> £3,382,440.89 (10.4%); £3,774,074.43 -> £3,382,441.01 (10.4%); £3,774,074.65 -> £3,382,441.14 (10.4%); £3,774,074.88 -> £3,382,441.27 (10.4%); £3,774,075.13 -> £3,382,441.39 (10.4%); £3,774,075.37 -> £3,382,441.42 (10.4%); £3,774,075.62 -> £3,382,441.44 (10.4%); £3,774,075.87 -> £3,382,441.47 (10.4%); £3,774,076.11 -> £3,382,441.49 (10.4%); £3,774,076.36 -> £3,382,441.51 (10.4%); £3,774,076.60 -> £3,382,441.54 (10.4%); £3,774,076.85 -> £3,382,441.56 (10.4%); £3,774,077.10 -> £3,382,441.59 (10.4%); £3,774,077.35 -> £3,382,441.61 (10.4%); £3,774,077.59 -> £3,382,441.63 (10.4%); £3,774,077.83 -> £3,382,441.66 (10.4%); £3,774,078.08 -> £3,382,441.68 (10.4%); £3,774,078.33 -> £3,382,441.71 (10.4%); £3,774,078.51 -> £3,382,441.84 (10.4%); £3,774,078.70 -> £3,382,441.98 (10.4%); £3,774,078.96 -> £3,382,442.13 (10.4%); £3,774,079.20 -> £3,382,442.27 (10.4%); £3,774,079.44 -> £3,382,442.41 (10.4%); £3,774,079.69 -> £3,382,442.55 (10.4%); £3,774,079.87 -> £3,382,442.69 (10.4%); £3,774,080.13 -> £3,382,442.82 (10.4%); £3,774,080.38 -> £3,382,442.96 (10.4%); £3,774,080.62 -> £3,382,443.09 (10.4%); £3,774,080.88 -> £3,382,443.22 (10.4%); £3,774,081.12 -> £3,382,443.25 (10.4%); £3,774,081.37 -> £3,382,443.28 (10.4%); £3,774,081.61 -> £3,382,443.30 (10.4%); £3,774,081.81 -> £3,382,443.32 (10.4%); £3,774,082.01 -> £3,382,443.34 (10.4%); £3,774,082.15 -> £3,382,443.36 (10.4%); £3,774,082.30 -> £3,382,443.38 (10.4%); £3,774,082.45 -> £3,382,443.40 (10.4%); £3,774,082.60 -> £3,382,443.42 (10.4%); £3,774,082.74 -> £3,382,443.43 (10.4%); £3,774,082.89 -> £3,382,443.45 (10.4%); £3,774,083.04 -> £3,382,443.47 (10.4%); £3,774,083.19 -> £3,382,443.48 (10.4%); £3,774,083.34 -> £3,382,443.50 (10.4%); £3,774,083.49 -> £3,382,443.52 (10.4%); £3,774,083.64 -> £3,382,443.54 (10.4%); £3,774,083.79 -> £3,382,443.66 (10.4%); £3,774,083.94 -> £3,382,443.79 (10.4%); £3,774,084.12 -> £3,382,443.92 (10.4%); £3,774,084.30 -> £3,382,444.05 (10.4%); £3,774,084.50 -> £3,382,444.19 (10.4%); £3,774,084.71 -> £3,382,444.32 (10.4%); £3,774,084.95 -> £3,382,444.45 (10.4%); £3,774,085.19 -> £3,382,444.58 (10.4%); £3,774,085.45 -> £3,382,444.61 (10.4%); £3,774,085.70 -> £3,382,444.63 (10.4%); £3,774,085.95 -> £3,382,444.66 (10.4%); £3,774,086.20 -> £3,382,444.68 (10.4%); £3,774,086.45 -> £3,382,444.70 (10.4%); £3,774,086.70 -> £3,382,444.73 (10.4%); £3,774,086.95 -> £3,382,444.75 (10.4%); £3,774,087.20 -> £3,382,444.78 (10.4%); £3,774,087.47 -> £3,382,444.80 (10.4%); £3,774,087.72 -> £3,382,444.82 (10.4%); £3,774,087.97 -> £3,382,444.85 (10.4%); £3,774,088.22 -> £3,382,444.88 (10.4%); £3,774,088.48 -> £3,382,444.90 (10.4%); £3,774,088.72 -> £3,382,445.04 (10.4%); £3,774,088.91 -> £3,382,445.19 (10.4%); £3,774,089.10 -> £3,382,445.34 (10.4%); £3,774,089.34 -> £3,382,445.49 (10.4%); £3,774,089.60 -> £3,382,445.64 (10.4%); £3,774,089.85 -> £3,382,445.78 (10.4%); £3,774,090.05 -> £3,382,445.93 (10.4%); £3,774,090.30 -> £3,382,446.08 (10.4%); £3,774,090.56 -> £3,382,446.22 (10.4%); £3,774,090.80 -> £3,382,446.36 (10.4%); £3,774,091.06 -> £3,382,446.51 (10.4%); £3,774,091.31 -> £3,382,446.53 (10.4%); £3,774,091.56 -> £3,382,446.56 (10.4%); £3,774,091.80 -> £3,382,446.58 (10.4%); £3,774,092.01 -> £3,382,446.61 (10.4%); £3,774,092.20 -> £3,382,446.63 (10.4%); £3,774,092.36 -> £3,382,446.65 (10.4%); £3,774,092.51 -> £3,382,446.66 (10.4%); £3,774,092.67 -> £3,382,446.68 (10.4%); £3,774,092.83 -> £3,382,446.70 (10.4%); £3,774,092.98 -> £3,382,446.72 (10.4%); £3,774,093.13 -> £3,382,446.73 (10.4%); £3,774,093.29 -> £3,382,446.75 (10.4%); £3,774,093.45 -> £3,382,446.76 (10.4%); £3,774,093.60 -> £3,382,446.78 (10.4%); £3,774,093.75 -> £3,382,446.80 (10.4%); £3,774,093.90 -> £3,382,446.82 (10.4%); £3,774,094.05 -> £3,382,446.93 (10.4%); £3,774,094.21 -> £3,382,447.05 (10.4%); £3,774,094.38 -> £3,382,447.17 (10.4%); £3,774,094.57 -> £3,382,447.30 (10.4%); £3,774,094.77 -> £3,382,447.42 (10.4%); £3,774,094.99 -> £3,382,447.55 (10.4%); £3,774,095.23 -> £3,382,447.67 (10.4%); £3,774,095.48 -> £3,382,447.79 (10.4%); £3,774,095.74 -> £3,382,447.82 (10.4%); £3,774,095.99 -> £3,382,447.84 (10.4%); £3,774,096.24 -> £3,382,447.87 (10.4%); £3,774,096.49 -> £3,382,447.89 (10.4%); £3,774,096.74 -> £3,382,447.91 (10.4%); £3,774,097.00 -> £3,382,447.94 (10.4%); £3,774,097.27 -> £3,382,447.96 (10.4%); £3,774,097.52 -> £3,382,447.99 (10.4%); £3,774,097.78 -> £3,382,448.01 (10.4%); £3,774,098.04 -> £3,382,448.03 (10.4%); £3,774,098.29 -> £3,382,448.06 (10.4%); £3,774,098.54 -> £3,382,448.08 (10.4%); £3,774,098.80 -> £3,382,448.11 (10.4%); £3,774,098.99 -> £3,382,448.24 (10.4%); £3,774,099.18 -> £3,382,448.38 (10.4%); £3,774,099.37 -> £3,382,448.52 (10.4%); £3,774,099.56 -> £3,382,448.65 (10.4%); £3,774,099.82 -> £3,382,448.79 (10.4%); £3,774,100.07 -> £3,382,448.93 (10.4%); £3,774,100.26 -> £3,382,449.06 (10.4%); £3,774,100.53 -> £3,382,449.19 (10.4%); £3,774,100.78 -> £3,382,449.32 (10.4%); £3,774,101.04 -> £3,382,449.45 (10.4%); £3,774,101.29 -> £3,382,449.58 (10.4%); £3,774,101.55 -> £3,382,449.61 (10.4%); £3,774,101.80 -> £3,382,449.64 (10.4%); £3,774,102.04 -> £3,382,449.66 (10.4%); £3,774,102.26 -> £3,382,449.69 (10.4%); £3,774,102.46 -> £3,382,449.71 (10.4%); £3,774,102.61 -> £3,382,449.72 (10.4%); £3,774,102.76 -> £3,382,449.74 (10.4%); £3,774,102.91 -> £3,382,449.76 (10.4%); £3,774,103.07 -> £3,382,449.78 (10.4%); £3,774,103.21 -> £3,382,449.79 (10.4%); £3,774,103.37 -> £3,382,449.81 (10.4%); £3,774,103.52 -> £3,382,449.83 (10.4%); £3,774,103.68 -> £3,382,449.84 (10.4%); £3,774,103.83 -> £3,382,449.86 (10.4%); £3,774,103.98 -> £3,382,449.88 (10.4%); £3,774,104.14 -> £3,382,449.89 (10.4%); £3,774,104.29 -> £3,382,450.03 (10.4%); £3,774,104.45 -> £3,382,450.16 (10.4%); £3,774,104.62 -> £3,382,450.30 (10.4%); £3,774,104.81 -> £3,382,450.44 (10.4%); £3,774,105.01 -> £3,382,450.59 (10.4%); £3,774,105.23 -> £3,382,450.73 (10.4%); £3,774,105.47 -> £3,382,450.87 (10.4%); £3,774,105.74 -> £3,382,451.01 (10.4%); £3,774,106.00 -> £3,382,451.03 (10.4%); £3,774,106.27 -> £3,382,451.06 (10.4%); £3,774,106.52 -> £3,382,451.08 (10.4%); £3,774,106.78 -> £3,382,451.11 (10.4%); £3,774,107.04 -> £3,382,451.13 (10.4%); £3,774,107.28 -> £3,382,451.16 (10.4%); £3,774,107.54 -> £3,382,451.18 (10.4%); £3,774,107.79 -> £3,382,451.21 (10.4%); £3,774,108.05 -> £3,382,451.23 (10.4%); £3,774,108.31 -> £3,382,451.26 (10.4%); £3,774,108.56 -> £3,382,451.28 (10.4%); £3,774,108.81 -> £3,382,451.30 (10.4%); £3,774,109.07 -> £3,382,451.33 (10.4%); £3,774,109.26 -> £3,382,451.48 (10.4%); £3,774,109.46 -> £3,382,451.63 (10.4%); £3,774,109.65 -> £3,382,451.78 (10.4%); £3,774,109.85 -> £3,382,451.93 (10.4%); £3,774,110.04 -> £3,382,452.09 (10.4%); £3,774,110.23 -> £3,382,452.24 (10.4%); £3,774,110.43 -> £3,382,452.39 (10.4%); £3,774,110.69 -> £3,382,452.54 (10.4%); £3,774,110.94 -> £3,382,452.70 (10.4%); £3,774,111.20 -> £3,382,452.85 (10.4%); £3,774,111.46 -> £3,382,452.99 (10.4%); £3,774,111.71 -> £3,382,453.02 (10.4%); £3,774,111.96 -> £3,382,453.05 (10.4%); £3,774,112.20 -> £3,382,453.08 (10.4%); £3,774,112.41 -> £3,382,453.10 (10.4%); £3,774,112.62 -> £3,382,453.12 (10.4%); £3,774,112.76 -> £3,382,453.14 (10.4%); £3,774,112.90 -> £3,382,453.16 (10.4%); £3,774,113.04 -> £3,382,453.18 (10.4%); £3,774,113.18 -> £3,382,453.19 (10.4%); £3,774,113.32 -> £3,382,453.21 (10.4%); £3,774,113.46 -> £3,382,453.23 (10.4%); £3,774,113.60 -> £3,382,453.25 (10.4%); £3,774,113.74 -> £3,382,453.26 (10.4%); £3,774,113.88 -> £3,382,453.28 (10.4%); £3,774,114.02 -> £3,382,453.30 (10.4%); £3,774,114.15 -> £3,382,453.31 (10.4%); £3,774,114.29 -> £3,382,453.47 (10.4%); £3,774,114.43 -> £3,382,453.63 (10.4%); £3,774,114.59 -> £3,382,453.79 (10.4%); £3,774,114.76 -> £3,382,453.95 (10.4%); £3,774,114.95 -> £3,382,454.11 (10.4%); £3,774,115.15 -> £3,382,454.28 (10.4%); £3,774,115.36 -> £3,382,454.44 (10.4%); £3,774,115.59 -> £3,382,454.61 (10.4%); £3,774,115.83 -> £3,382,454.64 (10.4%); £3,774,116.07 -> £3,382,454.66 (10.4%); £3,774,116.30 -> £3,382,454.69 (10.4%); £3,774,116.53 -> £3,382,454.72 (10.4%); £3,774,116.75 -> £3,382,454.74 (10.4%); £3,774,116.98 -> £3,382,454.77 (10.4%); £3,774,117.21 -> £3,382,454.80 (10.4%); £3,774,117.45 -> £3,382,454.83 (10.4%); £3,774,117.68 -> £3,382,454.85 (10.4%); £3,774,117.92 -> £3,382,454.88 (10.4%); £3,774,118.15 -> £3,382,454.90 (10.4%); £3,774,118.38 -> £3,382,454.93 (10.4%); £3,774,118.60 -> £3,382,454.96 (10.4%); £3,774,118.77 -> £3,382,455.12 (10.4%); £3,774,118.95 -> £3,382,455.29 (10.4%); £3,774,119.13 -> £3,382,455.46 (10.4%); £3,774,119.30 -> £3,382,455.63 (10.4%); £3,774,119.47 -> £3,382,455.80 (10.4%); £3,774,119.71 -> £3,382,455.98 (10.4%); £3,774,119.93 -> £3,382,456.15 (10.4%); £3,774,120.16 -> £3,382,456.32 (10.4%); £3,774,120.40 -> £3,382,456.48 (10.4%); £3,774,120.63 -> £3,382,456.65 (10.4%); £3,774,120.86 -> £3,382,456.82 (10.4%); £3,774,121.09 -> £3,382,456.85 (10.4%); £3,774,121.32 -> £3,382,456.88 (10.4%); £3,774,121.53 -> £3,382,456.91 (10.4%); £3,774,121.72 -> £3,382,456.93 (10.4%); £3,774,121.89 -> £3,382,456.95 (10.4%); £3,774,122.03 -> £3,382,456.97 (10.4%); £3,774,122.17 -> £3,382,456.99 (10.4%); £3,774,122.31 -> £3,382,457.01 (10.4%); £3,774,122.46 -> £3,382,457.03 (10.4%); £3,774,122.60 -> £3,382,457.05 (10.4%); £3,774,122.74 -> £3,382,457.06 (10.4%); £3,774,122.88 -> £3,382,457.08 (10.4%); £3,774,123.02 -> £3,382,457.10 (10.4%); £3,774,123.16 -> £3,382,457.11 (10.4%); £3,774,123.30 -> £3,382,457.13 (10.4%); £3,774,123.43 -> £3,382,457.15 (10.4%); £3,774,123.57 -> £3,382,457.28 (10.4%); £3,774,123.71 -> £3,382,457.41 (10.4%); £3,774,123.87 -> £3,382,457.54 (10.4%); £3,774,124.04 -> £3,382,457.67 (10.4%); £3,774,124.23 -> £3,382,457.80 (10.4%); £3,774,124.43 -> £3,382,457.94 (10.4%); £3,774,124.65 -> £3,382,458.08 (10.4%); £3,774,124.88 -> £3,382,458.22 (10.4%); £3,774,125.12 -> £3,382,458.25 (10.4%); £3,774,125.36 -> £3,382,458.28 (10.4%); £3,774,125.59 -> £3,382,458.31 (10.4%); £3,774,125.82 -> £3,382,458.34 (10.4%); £3,774,126.05 -> £3,382,458.37 (10.4%); £3,774,126.28 -> £3,382,458.40 (10.4%); £3,774,126.51 -> £3,382,458.44 (10.4%); £3,774,126.74 -> £3,382,458.46 (10.4%); £3,774,126.98 -> £3,382,458.49 (10.4%); £3,774,127.21 -> £3,382,458.52 (10.4%); £3,774,127.45 -> £3,382,458.55 (10.4%); £3,774,127.68 -> £3,382,458.58 (10.4%); £3,774,127.90 -> £3,382,458.61 (10.4%); £3,774,128.07 -> £3,382,458.75 (10.4%); £3,774,128.24 -> £3,382,458.89 (10.4%); £3,774,128.42 -> £3,382,459.04 (10.4%); £3,774,128.60 -> £3,382,459.19 (10.4%); £3,774,128.83 -> £3,382,459.34 (10.4%); £3,774,129.06 -> £3,382,459.49 (10.4%); £3,774,129.24 -> £3,382,459.63 (10.4%); £3,774,129.47 -> £3,382,459.77 (10.4%); £3,774,129.70 -> £3,382,459.91 (10.4%); £3,774,129.94 -> £3,382,460.05 (10.4%); £3,774,130.18 -> £3,382,460.19 (10.4%); £3,774,130.41 -> £3,382,460.22 (10.4%); £3,774,130.65 -> £3,382,460.25 (10.4%); £3,774,130.86 -> £3,382,460.27 (10.4%); £3,774,131.05 -> £3,382,460.29 (10.4%); £3,774,131.23 -> £3,382,460.31 (10.4%); £3,774,131.39 -> £3,382,460.33 (10.4%); £3,774,131.54 -> £3,382,460.35 (10.4%); £3,774,131.71 -> £3,382,460.37 (10.4%); £3,774,131.87 -> £3,382,460.38 (10.4%); £3,774,132.03 -> £3,382,460.40 (10.4%); £3,774,132.18 -> £3,382,460.42 (10.4%); £3,774,132.35 -> £3,382,460.43 (10.4%); £3,774,132.51 -> £3,382,460.45 (10.4%); £3,774,132.67 -> £3,382,460.47 (10.4%); £3,774,132.83 -> £3,382,460.48 (10.4%); £3,774,132.99 -> £3,382,460.50 (10.4%); £3,774,133.16 -> £3,382,460.59 (10.4%); £3,774,133.32 -> £3,382,460.68 (10.4%); £3,774,133.50 -> £3,382,460.78 (10.4%); £3,774,133.70 -> £3,382,460.88 (10.4%); £3,774,133.91 -> £3,382,460.98 (10.4%); £3,774,134.15 -> £3,382,461.08 (10.4%); £3,774,134.40 -> £3,382,461.18 (10.4%); £3,774,134.67 -> £3,382,461.28 (10.4%); £3,774,134.94 -> £3,382,461.30 (10.4%); £3,774,135.21 -> £3,382,461.33 (10.4%); £3,774,135.49 -> £3,382,461.35 (10.4%); £3,774,135.74 -> £3,382,461.37 (10.4%); £3,774,136.01 -> £3,382,461.40 (10.4%); £3,774,136.28 -> £3,382,461.42 (10.4%); £3,774,136.53 -> £3,382,461.45 (10.4%); £3,774,136.79 -> £3,382,461.47 (10.4%); £3,774,137.05 -> £3,382,461.49 (10.4%); £3,774,137.32 -> £3,382,461.52 (10.4%); £3,774,137.59 -> £3,382,461.54 (10.4%); £3,774,137.86 -> £3,382,461.56 (10.4%); £3,774,138.13 -> £3,382,461.59 (10.4%); £3,774,138.39 -> £3,382,461.70 (10.4%); £3,774,138.67 -> £3,382,461.82 (10.4%); £3,774,138.94 -> £3,382,461.94 (10.4%); £3,774,139.21 -> £3,382,462.06 (10.4%); £3,774,139.49 -> £3,382,462.18 (10.4%); £3,774,139.75 -> £3,382,462.29 (10.4%); £3,774,139.96 -> £3,382,462.40 (10.4%); £3,774,140.23 -> £3,382,462.51 (10.4%); £3,774,140.50 -> £3,382,462.62 (10.4%); £3,774,140.76 -> £3,382,462.73 (10.4%); £3,774,141.02 -> £3,382,462.84 (10.4%); £3,774,141.29 -> £3,382,462.86 (10.4%); £3,774,141.57 -> £3,382,462.89 (10.4%); £3,774,141.81 -> £3,382,462.92 (10.4%); £3,774,142.04 -> £3,382,462.94 (10.4%); £3,774,142.25 -> £3,382,462.96 (10.4%); £3,774,142.41 -> £3,382,462.98 (10.4%); £3,774,142.57 -> £3,382,462.99 (10.4%); £3,774,142.73 -> £3,382,463.01 (10.4%); £3,774,142.89 -> £3,382,463.03 (10.4%); £3,774,143.04 -> £3,382,463.05 (10.4%); £3,774,143.20 -> £3,382,463.06 (10.4%); £3,774,143.36 -> £3,382,463.08 (10.4%); £3,774,143.51 -> £3,382,463.10 (10.4%); £3,774,143.68 -> £3,382,463.11 (10.4%); £3,774,143.84 -> £3,382,463.13 (10.4%); £3,774,143.99 -> £3,382,463.15 (10.4%); £3,774,144.15 -> £3,382,463.30 (10.4%); £3,774,144.31 -> £3,382,463.46 (10.4%); £3,774,144.48 -> £3,382,463.62 (10.4%); £3,774,144.68 -> £3,382,463.78 (10.4%); £3,774,144.89 -> £3,382,463.94 (10.4%); £3,774,145.12 -> £3,382,464.10 (10.4%); £3,774,145.37 -> £3,382,464.27 (10.4%); £3,774,145.64 -> £3,382,464.43 (10.4%); £3,774,145.91 -> £3,382,464.45 (10.4%); £3,774,146.18 -> £3,382,464.47 (10.4%); £3,774,146.43 -> £3,382,464.50 (10.4%); £3,774,146.70 -> £3,382,464.52 (10.4%); £3,774,146.97 -> £3,382,464.55 (10.4%); £3,774,147.23 -> £3,382,464.57 (10.4%); £3,774,147.49 -> £3,382,464.60 (10.4%); £3,774,147.76 -> £3,382,464.62 (10.4%); £3,774,148.03 -> £3,382,464.64 (10.4%); £3,774,148.30 -> £3,382,464.66 (10.4%); £3,774,148.56 -> £3,382,464.69 (10.4%); £3,774,148.82 -> £3,382,464.71 (10.4%); £3,774,149.09 -> £3,382,464.74 (10.4%); £3,774,149.29 -> £3,382,464.90 (10.4%); £3,774,149.49 -> £3,382,465.07 (10.4%); £3,774,149.76 -> £3,382,465.25 (10.4%); £3,774,150.03 -> £3,382,465.41 (10.4%); £3,774,150.23 -> £3,382,465.58 (10.4%); £3,774,150.42 -> £3,382,465.74 (10.4%); £3,774,150.62 -> £3,382,465.91 (10.4%); £3,774,150.88 -> £3,382,466.07 (10.4%); £3,774,151.14 -> £3,382,466.24 (10.4%); £3,774,151.40 -> £3,382,466.40 (10.4%); £3,774,151.66 -> £3,382,466.56 (10.4%); £3,774,151.92 -> £3,382,466.59 (10.4%); £3,774,152.19 -> £3,382,466.62 (10.4%); £3,774,152.43 -> £3,382,466.65 (10.4%); £3,774,152.65 -> £3,382,466.67 (10.4%); £3,774,152.86 -> £3,382,466.69 (10.4%); £3,774,153.02 -> £3,382,466.71 (10.4%); £3,774,153.18 -> £3,382,466.73 (10.4%); £3,774,153.34 -> £3,382,466.74 (10.4%); £3,774,153.50 -> £3,382,466.76 (10.4%); £3,774,153.66 -> £3,382,466.78 (10.4%); £3,774,153.81 -> £3,382,466.79 (10.4%); £3,774,153.97 -> £3,382,466.81 (10.4%); £3,774,154.13 -> £3,382,466.83 (10.4%); £3,774,154.29 -> £3,382,466.84 (10.4%); £3,774,154.45 -> £3,382,466.86 (10.4%); £3,774,154.61 -> £3,382,466.88 (10.4%); £3,774,154.76 -> £3,382,467.04 (10.4%); £3,774,154.92 -> £3,382,467.21 (10.4%); £3,774,155.10 -> £3,382,467.39 (10.4%); £3,774,155.29 -> £3,382,467.57 (10.4%); £3,774,155.50 -> £3,382,467.76 (10.4%); £3,774,155.73 -> £3,382,467.93 (10.4%); £3,774,155.99 -> £3,382,468.10 (10.4%); £3,774,156.25 -> £3,382,468.27 (10.4%); £3,774,156.52 -> £3,382,468.30 (10.4%); £3,774,156.79 -> £3,382,468.32 (10.4%); £3,774,157.06 -> £3,382,468.35 (10.4%); £3,774,157.32 -> £3,382,468.37 (10.4%); £3,774,157.59 -> £3,382,468.39 (10.4%); £3,774,157.85 -> £3,382,468.42 (10.4%); £3,774,158.11 -> £3,382,468.44 (10.4%); £3,774,158.36 -> £3,382,468.47 (10.4%); £3,774,158.64 -> £3,382,468.49 (10.4%); £3,774,158.90 -> £3,382,468.51 (10.4%); £3,774,159.17 -> £3,382,468.54 (10.4%); £3,774,159.43 -> £3,382,468.56 (10.4%); £3,774,159.69 -> £3,382,468.59 (10.4%); £3,774,159.96 -> £3,382,468.77 (10.4%); £3,774,160.22 -> £3,382,468.95 (10.4%); £3,774,160.42 -> £3,382,469.13 (10.4%); £3,774,160.62 -> £3,382,469.31 (10.4%); £3,774,160.83 -> £3,382,469.49 (10.4%); £3,774,161.10 -> £3,382,469.68 (10.4%); £3,774,161.36 -> £3,382,469.85 (10.4%); £3,774,161.62 -> £3,382,470.03 (10.4%); £3,774,161.89 -> £3,382,470.21 (10.4%); £3,774,162.16 -> £3,382,470.38 (10.4%); £3,774,162.42 -> £3,382,470.56 (10.4%); £3,774,162.69 -> £3,382,470.59 (10.4%); £3,774,162.96 -> £3,382,470.62 (10.4%); £3,774,163.20 -> £3,382,470.64 (10.4%); £3,774,163.42 -> £3,382,470.66 (10.4%); £3,774,163.62 -> £3,382,470.68 (10.4%); £3,774,163.79 -> £3,382,470.70 (10.4%); £3,774,163.95 -> £3,382,470.72 (10.4%); £3,774,164.11 -> £3,382,470.74 (10.4%); £3,774,164.27 -> £3,382,470.76 (10.4%); £3,774,164.42 -> £3,382,470.77 (10.4%); £3,774,164.58 -> £3,382,470.79 (10.4%); £3,774,164.74 -> £3,382,470.81 (10.4%); £3,774,164.90 -> £3,382,470.82 (10.4%); £3,774,165.06 -> £3,382,470.84 (10.4%); £3,774,165.22 -> £3,382,470.86 (10.4%); £3,774,165.38 -> £3,382,470.87 (10.4%); £3,774,165.55 -> £3,382,471.05 (10.4%); £3,774,165.71 -> £3,382,471.21 (10.4%); £3,774,165.87 -> £3,382,471.38 (10.4%); £3,774,166.06 -> £3,382,471.55 (10.4%); £3,774,166.28 -> £3,382,471.72 (10.4%); £3,774,166.50 -> £3,382,471.89 (10.4%); £3,774,166.74 -> £3,382,472.06 (10.4%); £3,774,167.01 -> £3,382,472.23 (10.4%); £3,774,167.27 -> £3,382,472.25 (10.4%); £3,774,167.53 -> £3,382,472.28 (10.4%); £3,774,167.79 -> £3,382,472.30 (10.4%); £3,774,168.05 -> £3,382,472.33 (10.4%); £3,774,168.31 -> £3,382,472.35 (10.4%); £3,774,168.58 -> £3,382,472.38 (10.4%); £3,774,168.85 -> £3,382,472.40 (10.4%); £3,774,169.12 -> £3,382,472.42 (10.4%); £3,774,169.38 -> £3,382,472.45 (10.4%); £3,774,169.65 -> £3,382,472.47 (10.4%); £3,774,169.92 -> £3,382,472.49 (10.4%); £3,774,170.19 -> £3,382,472.52 (10.4%); £3,774,170.46 -> £3,382,472.55 (10.4%); £3,774,170.72 -> £3,382,472.72 (10.4%); £3,774,170.92 -> £3,382,472.89 (10.4%); £3,774,171.11 -> £3,382,473.07 (10.4%); £3,774,171.31 -> £3,382,473.24 (10.4%); £3,774,171.51 -> £3,382,473.42 (10.4%); £3,774,171.70 -> £3,382,473.60 (10.4%); £3,774,171.97 -> £3,382,473.77 (10.4%); £3,774,172.23 -> £3,382,473.95 (10.4%); £3,774,172.50 -> £3,382,474.12 (10.4%); £3,774,172.76 -> £3,382,474.30 (10.4%); £3,774,173.03 -> £3,382,474.47 (10.4%); £3,774,173.29 -> £3,382,474.50 (10.4%); £3,774,173.56 -> £3,382,474.52 (10.4%); £3,774,173.81 -> £3,382,474.55 (10.4%); £3,774,174.03 -> £3,382,474.57 (10.4%); £3,774,174.23 -> £3,382,474.59 (10.4%); £3,774,174.39 -> £3,382,474.61 (10.4%); £3,774,174.55 -> £3,382,474.63 (10.4%); £3,774,174.71 -> £3,382,474.65 (10.4%); £3,774,174.86 -> £3,382,474.66 (10.4%); £3,774,175.02 -> £3,382,474.68 (10.4%); £3,774,175.18 -> £3,382,474.70 (10.4%); £3,774,175.34 -> £3,382,474.71 (10.4%); £3,774,175.50 -> £3,382,474.73 (10.4%); £3,774,175.66 -> £3,382,474.74 (10.4%); £3,774,175.82 -> £3,382,474.76 (10.4%); £3,774,175.97 -> £3,382,474.78 (10.4%); £3,774,176.14 -> £3,382,474.88 (10.4%); £3,774,176.29 -> £3,382,474.99 (10.4%); £3,774,176.47 -> £3,382,475.11 (10.4%); £3,774,176.66 -> £3,382,475.22 (10.4%); £3,774,176.87 -> £3,382,475.34 (10.4%); £3,774,177.10 -> £3,382,475.46 (10.4%); £3,774,177.35 -> £3,382,475.57 (10.4%); £3,774,177.63 -> £3,382,475.68 (10.4%); £3,774,177.90 -> £3,382,475.71 (10.4%); £3,774,178.17 -> £3,382,475.73 (10.4%); £3,774,178.44 -> £3,382,475.76 (10.4%); £3,774,178.70 -> £3,382,475.78 (10.4%); £3,774,178.97 -> £3,382,475.80 (10.4%); £3,774,179.24 -> £3,382,475.83 (10.4%); £3,774,179.50 -> £3,382,475.85 (10.4%); £3,774,179.77 -> £3,382,475.88 (10.4%); £3,774,180.04 -> £3,382,475.90 (10.4%); £3,774,180.29 -> £3,382,475.92 (10.4%); £3,774,180.56 -> £3,382,475.95 (10.4%); £3,774,180.82 -> £3,382,475.97 (10.4%); £3,774,181.09 -> £3,382,476.00 (10.4%); £3,774,181.37 -> £3,382,476.13 (10.4%); £3,774,181.63 -> £3,382,476.25 (10.4%); £3,774,181.89 -> £3,382,476.38 (10.4%); £3,774,182.15 -> £3,382,476.51 (10.4%); £3,774,182.42 -> £3,382,476.64 (10.4%); £3,774,182.68 -> £3,382,476.77 (10.4%); £3,774,182.95 -> £3,382,476.90 (10.4%); £3,774,183.22 -> £3,382,477.03 (10.4%); £3,774,183.48 -> £3,382,477.15 (10.4%); £3,774,183.75 -> £3,382,477.28 (10.4%); £3,774,184.01 -> £3,382,477.40 (10.4%); £3,774,184.28 -> £3,382,477.43 (10.4%); £3,774,184.55 -> £3,382,477.46 (10.4%); £3,774,184.80 -> £3,382,477.48 (10.4%); £3,774,185.03 -> £3,382,477.50 (10.4%); £3,774,185.23 -> £3,382,477.53 (10.4%); £3,774,185.37 -> £3,382,477.55 (10.4%); £3,774,185.51 -> £3,382,477.57 (10.4%); £3,774,185.65 -> £3,382,477.58 (10.4%); £3,774,185.79 -> £3,382,477.60 (10.4%); £3,774,185.93 -> £3,382,477.62 (10.4%); £3,774,186.07 -> £3,382,477.63 (10.4%); £3,774,186.21 -> £3,382,477.65 (10.4%); £3,774,186.35 -> £3,382,477.67 (10.4%); £3,774,186.49 -> £3,382,477.69 (10.4%); £3,774,186.63 -> £3,382,477.70 (10.4%); £3,774,186.77 -> £3,382,477.72 (10.4%); £3,774,186.91 -> £3,382,477.83 (10.4%); £3,774,187.05 -> £3,382,477.94 (10.4%); £3,774,187.20 -> £3,382,478.05 (10.4%); £3,774,187.38 -> £3,382,478.16 (10.4%); £3,774,187.56 -> £3,382,478.27 (10.4%); £3,774,187.76 -> £3,382,478.38 (10.4%); £3,774,187.98 -> £3,382,478.50 (10.4%); £3,774,188.20 -> £3,382,478.61 (10.4%); £3,774,188.44 -> £3,382,478.64 (10.4%); £3,774,188.68 -> £3,382,478.67 (10.4%); £3,774,188.91 -> £3,382,478.69 (10.4%); £3,774,189.14 -> £3,382,478.72 (10.4%); £3,774,189.37 -> £3,382,478.75 (10.4%); £3,774,189.60 -> £3,382,478.77 (10.4%); £3,774,189.84 -> £3,382,478.80 (10.4%); £3,774,190.07 -> £3,382,478.83 (10.4%); £3,774,190.30 -> £3,382,478.85 (10.4%); £3,774,190.53 -> £3,382,478.88 (10.4%); £3,774,190.76 -> £3,382,478.90 (10.4%); £3,774,190.99 -> £3,382,478.93 (10.4%); £3,774,191.23 -> £3,382,478.96 (10.4%); £3,774,191.46 -> £3,382,479.07 (10.4%); £3,774,191.64 -> £3,382,479.20 (10.4%); £3,774,191.88 -> £3,382,479.32 (10.4%); £3,774,192.05 -> £3,382,479.44 (10.4%); £3,774,192.22 -> £3,382,479.56 (10.4%); £3,774,192.40 -> £3,382,479.69 (10.4%); £3,774,192.57 -> £3,382,479.81 (10.4%); £3,774,192.80 -> £3,382,479.94 (10.4%); £3,774,193.03 -> £3,382,480.06 (10.4%); £3,774,193.27 -> £3,382,480.18 (10.4%); £3,774,193.49 -> £3,382,480.30 (10.4%); £3,774,193.72 -> £3,382,480.33 (10.4%); £3,774,193.95 -> £3,382,480.36 (10.4%); £3,774,194.17 -> £3,382,480.38 (10.4%); £3,774,194.36 -> £3,382,480.41 (10.4%); £3,774,194.54 -> £3,382,480.43 (10.4%); £3,774,194.68 -> £3,382,480.45 (10.4%); £3,774,194.82 -> £3,382,480.47 (10.4%); £3,774,194.96 -> £3,382,480.49 (10.4%); £3,774,195.10 -> £3,382,480.51 (10.4%); £3,774,195.24 -> £3,382,480.52 (10.4%); £3,774,195.38 -> £3,382,480.54 (10.4%); £3,774,195.52 -> £3,382,480.56 (10.4%); £3,774,195.66 -> £3,382,480.58 (10.4%); £3,774,195.80 -> £3,382,480.59 (10.4%); £3,774,195.94 -> £3,382,480.61 (10.4%); £3,774,196.08 -> £3,382,480.63 (10.4%); £3,774,196.22 -> £3,382,480.73 (10.4%); £3,774,196.36 -> £3,382,480.83 (10.4%); £3,774,196.52 -> £3,382,480.93 (10.4%); £3,774,196.68 -> £3,382,481.04 (10.4%); £3,774,196.87 -> £3,382,481.14 (10.4%); £3,774,197.07 -> £3,382,481.25 (10.4%); £3,774,197.30 -> £3,382,481.37 (10.4%); £3,774,197.53 -> £3,382,481.48 (10.4%); £3,774,197.76 -> £3,382,481.51 (10.4%); £3,774,197.99 -> £3,382,481.54 (10.4%); £3,774,198.23 -> £3,382,481.57 (10.4%); £3,774,198.47 -> £3,382,481.60 (10.4%); £3,774,198.70 -> £3,382,481.64 (10.4%); £3,774,198.94 -> £3,382,481.67 (10.4%); £3,774,199.18 -> £3,382,481.70 (10.4%); £3,774,199.42 -> £3,382,481.73 (10.4%); £3,774,199.65 -> £3,382,481.76 (10.4%); £3,774,199.89 -> £3,382,481.79 (10.4%); £3,774,200.13 -> £3,382,481.82 (10.4%); £3,774,200.36 -> £3,382,481.85 (10.4%); £3,774,200.60 -> £3,382,481.88 (10.4%); £3,774,200.83 -> £3,382,481.99 (10.4%); £3,774,201.06 -> £3,382,482.11 (10.4%); £3,774,201.23 -> £3,382,482.23 (10.4%); £3,774,201.40 -> £3,382,482.35 (10.4%); £3,774,201.58 -> £3,382,482.47 (10.4%); £3,774,201.76 -> £3,382,482.58 (10.4%); £3,774,201.94 -> £3,382,482.70 (10.4%); £3,774,202.18 -> £3,382,482.81 (10.4%); £3,774,202.41 -> £3,382,482.93 (10.4%); £3,774,202.64 -> £3,382,483.05 (10.4%); £3,774,202.87 -> £3,382,483.17 (10.4%); £3,774,203.11 -> £3,382,483.20 (10.4%); £3,774,203.35 -> £3,382,483.22 (10.4%); £3,774,203.57 -> £3,382,483.25 (10.4%); £3,774,203.77 -> £3,382,483.27 (10.4%); £3,774,203.95 -> £3,382,483.29 (10.4%); £3,774,204.11 -> £3,382,483.31 (10.4%); £3,774,204.27 -> £3,382,483.33 (10.4%); £3,774,204.44 -> £3,382,483.35 (10.4%); £3,774,204.60 -> £3,382,483.36 (10.4%); £3,774,204.75 -> £3,382,483.38 (10.4%); £3,774,204.92 -> £3,382,483.40 (10.4%); £3,774,205.08 -> £3,382,483.42 (10.4%); £3,774,205.25 -> £3,382,483.43 (10.4%); £3,774,205.42 -> £3,382,483.45 (10.4%); £3,774,205.58 -> £3,382,483.47 (10.4%); £3,774,205.74 -> £3,382,483.48 (10.4%); £3,774,205.91 -> £3,382,483.59 (10.4%); £3,774,206.07 -> £3,382,483.70 (10.4%); £3,774,206.25 -> £3,382,483.81 (10.4%); £3,774,206.46 -> £3,382,483.93 (10.4%); £3,774,206.68 -> £3,382,484.04 (10.4%); £3,774,206.92 -> £3,382,484.15 (10.4%); £3,774,207.16 -> £3,382,484.27 (10.4%); £3,774,207.43 -> £3,382,484.38 (10.4%); £3,774,207.70 -> £3,382,484.41 (10.4%); £3,774,207.98 -> £3,382,484.43 (10.4%); £3,774,208.26 -> £3,382,484.46 (10.4%); £3,774,208.53 -> £3,382,484.48 (10.4%); £3,774,208.80 -> £3,382,484.50 (10.4%); £3,774,209.06 -> £3,382,484.53 (10.4%); £3,774,209.33 -> £3,382,484.55 (10.4%); £3,774,209.60 -> £3,382,484.57 (10.4%); £3,774,209.87 -> £3,382,484.60 (10.4%); £3,774,210.13 -> £3,382,484.62 (10.4%); £3,774,210.41 -> £3,382,484.64 (10.4%); £3,774,210.69 -> £3,382,484.67 (10.4%); £3,774,210.95 -> £3,382,484.70 (10.4%); £3,774,211.15 -> £3,382,484.82 (10.4%); £3,774,211.36 -> £3,382,484.94 (10.4%); £3,774,211.56 -> £3,382,485.07 (10.4%); £3,774,211.76 -> £3,382,485.19 (10.4%); £3,774,211.97 -> £3,382,485.32 (10.4%); £3,774,212.25 -> £3,382,485.45 (10.4%); £3,774,212.52 -> £3,382,485.58 (10.4%); £3,774,212.80 -> £3,382,485.70 (10.4%); £3,774,213.07 -> £3,382,485.83 (10.4%); £3,774,213.34 -> £3,382,485.95 (10.4%); £3,774,213.61 -> £3,382,486.07 (10.4%); £3,774,213.89 -> £3,382,486.10 (10.4%); £3,774,214.15 -> £3,382,486.12 (10.4%); £3,774,214.41 -> £3,382,486.15 (10.4%); £3,774,214.64 -> £3,382,486.17 (10.4%); £3,774,214.86 -> £3,382,486.19 (10.4%); £3,774,215.02 -> £3,382,486.21 (10.4%); £3,774,215.19 -> £3,382,486.23 (10.4%); £3,774,215.36 -> £3,382,486.25 (10.4%); £3,774,215.52 -> £3,382,486.26 (10.4%); £3,774,215.70 -> £3,382,486.28 (10.4%); £3,774,215.86 -> £3,382,486.30 (10.4%); £3,774,216.02 -> £3,382,486.31 (10.4%); £3,774,216.19 -> £3,382,486.33 (10.4%); £3,774,216.35 -> £3,382,486.35 (10.4%); £3,774,216.52 -> £3,382,486.37 (10.4%); £3,774,216.69 -> £3,382,486.38 (10.4%); £3,774,216.85 -> £3,382,486.51 (10.4%); £3,774,217.02 -> £3,382,486.64 (10.4%); £3,774,217.20 -> £3,382,486.77 (10.4%); £3,774,217.41 -> £3,382,486.91 (10.4%); £3,774,217.62 -> £3,382,487.04 (10.4%); £3,774,217.86 -> £3,382,487.17 (10.4%); £3,774,218.12 -> £3,382,487.30 (10.4%); £3,774,218.39 -> £3,382,487.43 (10.4%); £3,774,218.66 -> £3,382,487.46 (10.4%); £3,774,218.94 -> £3,382,487.48 (10.4%); £3,774,219.22 -> £3,382,487.50 (10.4%); £3,774,219.49 -> £3,382,487.53 (10.4%); £3,774,219.77 -> £3,382,487.55 (10.4%); £3,774,220.04 -> £3,382,487.58 (10.4%); £3,774,220.31 -> £3,382,487.60 (10.4%); £3,774,220.59 -> £3,382,487.62 (10.4%); £3,774,220.86 -> £3,382,487.65 (10.4%); £3,774,221.13 -> £3,382,487.67 (10.4%); £3,774,221.40 -> £3,382,487.69 (10.4%); £3,774,221.66 -> £3,382,487.72 (10.4%); £3,774,221.94 -> £3,382,487.75 (10.4%); £3,774,222.15 -> £3,382,487.88 (10.4%); £3,774,222.36 -> £3,382,488.01 (10.4%); £3,774,222.56 -> £3,382,488.15 (10.4%); £3,774,222.77 -> £3,382,488.29 (10.4%); £3,774,222.97 -> £3,382,488.42 (10.4%); £3,774,223.17 -> £3,382,488.56 (10.4%); £3,774,223.38 -> £3,382,488.69 (10.4%); £3,774,223.66 -> £3,382,488.83 (10.4%); £3,774,223.93 -> £3,382,488.96 (10.4%); £3,774,224.20 -> £3,382,489.09 (10.4%); £3,774,224.48 -> £3,382,489.22 (10.4%); £3,774,224.75 -> £3,382,489.25 (10.4%); £3,774,225.02 -> £3,382,489.28 (10.4%); £3,774,225.27 -> £3,382,489.30 (10.4%); £3,774,225.50 -> £3,382,489.32 (10.4%); £3,774,225.71 -> £3,382,489.34 (10.4%); £3,774,225.88 -> £3,382,489.36 (10.4%); £3,774,226.05 -> £3,382,489.38 (10.4%); £3,774,226.21 -> £3,382,489.40 (10.4%); £3,774,226.36 -> £3,382,489.41 (10.4%); £3,774,226.53 -> £3,382,489.43 (10.4%); £3,774,226.70 -> £3,382,489.45 (10.4%); £3,774,226.87 -> £3,382,489.46 (10.4%); £3,774,227.03 -> £3,382,489.48 (10.4%); £3,774,227.20 -> £3,382,489.50 (10.4%); £3,774,227.36 -> £3,382,489.51 (10.4%); £3,774,227.53 -> £3,382,489.53 (10.4%); £3,774,227.70 -> £3,382,489.72 (10.4%); £3,774,227.86 -> £3,382,489.92 (10.4%); £3,774,228.04 -> £3,382,490.12 (10.4%); £3,774,228.25 -> £3,382,490.32 (10.4%); £3,774,228.47 -> £3,382,490.52 (10.4%); £3,774,228.72 -> £3,382,490.72 (10.4%); £3,774,228.97 -> £3,382,490.92 (10.4%); £3,774,229.25 -> £3,382,491.11 (10.4%); £3,774,229.54 -> £3,382,491.13 (10.4%); £3,774,229.82 -> £3,382,491.16 (10.4%); £3,774,230.09 -> £3,382,491.18 (10.4%); £3,774,230.37 -> £3,382,491.21 (10.4%); £3,774,230.65 -> £3,382,491.23 (10.4%); £3,774,230.93 -> £3,382,491.26 (10.4%); £3,774,231.19 -> £3,382,491.28 (10.4%); £3,774,231.47 -> £3,382,491.30 (10.4%); £3,774,231.74 -> £3,382,491.32 (10.4%); £3,774,232.02 -> £3,382,491.35 (10.4%); £3,774,232.29 -> £3,382,491.37 (10.4%); £3,774,232.57 -> £3,382,491.40 (10.4%); £3,774,232.84 -> £3,382,491.43 (10.4%); £3,774,233.05 -> £3,382,491.62 (10.4%); £3,774,233.26 -> £3,382,491.83 (10.4%); £3,774,233.54 -> £3,382,492.02 (10.4%); £3,774,233.74 -> £3,382,492.22 (10.4%); £3,774,233.94 -> £3,382,492.42 (10.4%); £3,774,234.15 -> £3,382,492.63 (10.4%); £3,774,234.42 -> £3,382,492.84 (10.4%); £3,774,234.70 -> £3,382,493.04 (10.4%); £3,774,234.96 -> £3,382,493.24 (10.4%); £3,774,235.23 -> £3,382,493.45 (10.4%); £3,774,235.50 -> £3,382,493.63 (10.4%); £3,774,235.79 -> £3,382,493.66 (10.4%); £3,774,236.07 -> £3,382,493.69 (10.4%); £3,774,236.33 -> £3,382,493.71 (10.4%); £3,774,236.56 -> £3,382,493.74 (10.4%); £3,774,236.78 -> £3,382,493.76 (10.4%); £3,774,236.95 -> £3,382,493.78 (10.4%); £3,774,237.11 -> £3,382,493.79 (10.4%); £3,774,237.27 -> £3,382,493.81 (10.4%); £3,774,237.44 -> £3,382,493.83 (10.4%); £3,774,237.61 -> £3,382,493.84 (10.4%); £3,774,237.78 -> £3,382,493.86 (10.4%); £3,774,237.94 -> £3,382,493.88 (10.4%); £3,774,238.10 -> £3,382,493.89 (10.4%); £3,774,238.27 -> £3,382,493.91 (10.4%); £3,774,238.43 -> £3,382,493.93 (10.4%); £3,774,238.59 -> £3,382,493.94 (10.4%); £3,774,238.76 -> £3,382,494.15 (10.4%); £3,774,238.92 -> £3,382,494.35 (10.4%); £3,774,239.11 -> £3,382,494.55 (10.4%); £3,774,239.31 -> £3,382,494.77 (10.4%); £3,774,239.53 -> £3,382,494.99 (10.4%); £3,774,239.77 -> £3,382,495.21 (10.4%); £3,774,240.02 -> £3,382,495.42 (10.4%); £3,774,240.30 -> £3,382,495.63 (10.4%); £3,774,240.58 -> £3,382,495.65 (10.4%); £3,774,240.86 -> £3,382,495.68 (10.4%); £3,774,241.13 -> £3,382,495.70 (10.4%); £3,774,241.41 -> £3,382,495.72 (10.4%); £3,774,241.68 -> £3,382,495.75 (10.4%); £3,774,241.95 -> £3,382,495.77 (10.4%); £3,774,242.23 -> £3,382,495.80 (10.4%); £3,774,242.51 -> £3,382,495.82 (10.4%); £3,774,242.77 -> £3,382,495.84 (10.4%); £3,774,243.05 -> £3,382,495.86 (10.4%); £3,774,243.32 -> £3,382,495.89 (10.4%); £3,774,243.59 -> £3,382,495.91 (10.4%); £3,774,243.86 -> £3,382,495.94 (10.4%); £3,774,244.07 -> £3,382,496.16 (10.4%); £3,774,244.35 -> £3,382,496.37 (10.4%); £3,774,244.56 -> £3,382,496.59 (10.4%); £3,774,244.83 -> £3,382,496.81 (10.4%); £3,774,245.09 -> £3,382,497.03 (10.4%); £3,774,245.37 -> £3,382,497.25 (10.4%); £3,774,245.64 -> £3,382,497.47 (10.4%); £3,774,245.92 -> £3,382,497.68 (10.4%); £3,774,246.20 -> £3,382,497.89 (10.4%); £3,774,246.47 -> £3,382,498.10 (10.4%); £3,774,246.75 -> £3,382,498.31 (10.4%); £3,774,247.03 -> £3,382,498.34 (10.4%); £3,774,247.31 -> £3,382,498.37 (10.4%); £3,774,247.56 -> £3,382,498.39 (10.4%); £3,774,247.80 -> £3,382,498.42 (10.4%); £3,774,248.01 -> £3,382,498.44 (10.4%); £3,774,248.18 -> £3,382,498.45 (10.4%); £3,774,248.34 -> £3,382,498.47 (10.4%); £3,774,248.50 -> £3,382,498.49 (10.4%); £3,774,248.66 -> £3,382,498.51 (10.4%); £3,774,248.83 -> £3,382,498.52 (10.4%); £3,774,248.99 -> £3,382,498.54 (10.4%); £3,774,249.16 -> £3,382,498.55 (10.4%); £3,774,249.32 -> £3,382,498.57 (10.4%); £3,774,249.48 -> £3,382,498.59 (10.4%); £3,774,249.65 -> £3,382,498.60 (10.4%); £3,774,249.81 -> £3,382,498.62 (10.4%); £3,774,249.98 -> £3,382,498.78 (10.4%); £3,774,250.15 -> £3,382,498.94 (10.4%); £3,774,250.33 -> £3,382,499.10 (10.4%); £3,774,250.53 -> £3,382,499.26 (10.4%); £3,774,250.75 -> £3,382,499.43 (10.4%); £3,774,250.97 -> £3,382,499.59 (10.4%); £3,774,251.23 -> £3,382,499.76 (10.4%); £3,774,251.49 -> £3,382,499.92 (10.4%); £3,774,251.77 -> £3,382,499.95 (10.4%); £3,774,252.04 -> £3,382,499.97 (10.4%); £3,774,252.31 -> £3,382,500.00 (10.4%); £3,774,252.58 -> £3,382,500.02 (10.4%); £3,774,252.85 -> £3,382,500.05 (10.4%); £3,774,253.11 -> £3,382,500.07 (10.4%); £3,774,253.38 -> £3,382,500.10 (10.4%); £3,774,253.64 -> £3,382,500.12 (10.4%); £3,774,253.92 -> £3,382,500.14 (10.4%); £3,774,254.20 -> £3,382,500.17 (10.4%); £3,774,254.47 -> £3,382,500.19 (10.4%); £3,774,254.74 -> £3,382,500.22 (10.4%); £3,774,255.01 -> £3,382,500.25 (10.4%); £3,774,255.28 -> £3,382,500.42 (10.4%); £3,774,255.55 -> £3,382,500.59 (10.4%); £3,774,255.83 -> £3,382,500.77 (10.4%); £3,774,256.11 -> £3,382,500.94 (10.4%); £3,774,256.38 -> £3,382,501.11 (10.4%); £3,774,256.58 -> £3,382,501.28 (10.4%); £3,774,256.79 -> £3,382,501.45 (10.4%); £3,774,257.06 -> £3,382,501.62 (10.4%); £3,774,257.32 -> £3,382,501.79 (10.4%); £3,774,257.59 -> £3,382,501.96 (10.4%); £3,774,257.86 -> £3,382,502.12 (10.4%); £3,774,258.14 -> £3,382,502.15 (10.4%); £3,774,258.40 -> £3,382,502.18 (10.4%); £3,774,258.65 -> £3,382,502.20 (10.4%); £3,774,258.89 -> £3,382,502.22 (10.4%); £3,774,259.10 -> £3,382,502.25 (10.4%); £3,774,259.25 -> £3,382,502.27 (10.4%); £3,774,259.39 -> £3,382,502.28 (10.4%); £3,774,259.53 -> £3,382,502.30 (10.4%); £3,774,259.67 -> £3,382,502.32 (10.4%); £3,774,259.82 -> £3,382,502.34 (10.4%); £3,774,259.96 -> £3,382,502.35 (10.4%); £3,774,260.10 -> £3,382,502.37 (10.4%); £3,774,260.24 -> £3,382,502.38 (10.4%); £3,774,260.38 -> £3,382,502.40 (10.4%); £3,774,260.52 -> £3,382,502.42 (10.4%); £3,774,260.67 -> £3,382,502.44 (10.4%); £3,774,260.81 -> £3,382,502.58 (10.4%); £3,774,260.96 -> £3,382,502.73 (10.4%); £3,774,261.11 -> £3,382,502.88 (10.4%); £3,774,261.30 -> £3,382,503.04 (10.4%); £3,774,261.49 -> £3,382,503.20 (10.4%); £3,774,261.70 -> £3,382,503.36 (10.4%); £3,774,261.91 -> £3,382,503.53 (10.4%); £3,774,262.15 -> £3,382,503.69 (10.4%); £3,774,262.39 -> £3,382,503.72 (10.4%); £3,774,262.63 -> £3,382,503.74 (10.4%); £3,774,262.87 -> £3,382,503.77 (10.4%); £3,774,263.11 -> £3,382,503.80 (10.4%); £3,774,263.35 -> £3,382,503.82 (10.4%); £3,774,263.58 -> £3,382,503.85 (10.4%); £3,774,263.82 -> £3,382,503.88 (10.4%); £3,774,264.06 -> £3,382,503.90 (10.4%); £3,774,264.29 -> £3,382,503.93 (10.4%); £3,774,264.54 -> £3,382,503.95 (10.4%); £3,774,264.78 -> £3,382,503.98 (10.4%); £3,774,265.01 -> £3,382,504.01 (10.4%); £3,774,265.26 -> £3,382,504.03 (10.4%); £3,774,265.50 -> £3,382,504.20 (10.4%); £3,774,265.73 -> £3,382,504.37 (10.4%); £3,774,265.96 -> £3,382,504.53 (10.4%); £3,774,266.14 -> £3,382,504.70 (10.4%); £3,774,266.38 -> £3,382,504.87 (10.4%); £3,774,266.56 -> £3,382,505.03 (10.4%); £3,774,266.74 -> £3,382,505.20 (10.4%); £3,774,266.99 -> £3,382,505.37 (10.4%); £3,774,267.23 -> £3,382,505.53 (10.4%); £3,774,267.47 -> £3,382,505.70 (10.4%); £3,774,267.71 -> £3,382,505.86 (10.4%); £3,774,267.95 -> £3,382,505.89 (10.4%); £3,774,268.19 -> £3,382,505.92 (10.4%); £3,774,268.41 -> £3,382,505.94 (10.4%); £3,774,268.61 -> £3,382,505.96 (10.4%); £3,774,268.80 -> £3,382,505.99 (10.4%); £3,774,268.95 -> £3,382,506.01 (10.4%); £3,774,269.09 -> £3,382,506.03 (10.4%); £3,774,269.22 -> £3,382,506.04 (10.4%); £3,774,269.36 -> £3,382,506.06 (10.4%); £3,774,269.50 -> £3,382,506.08 (10.4%); £3,774,269.65 -> £3,382,506.10 (10.4%); £3,774,269.79 -> £3,382,506.11 (10.4%); £3,774,269.93 -> £3,382,506.13 (10.4%); £3,774,270.07 -> £3,382,506.15 (10.4%); £3,774,270.21 -> £3,382,506.16 (10.4%); £3,774,270.35 -> £3,382,506.18 (10.4%); £3,774,270.49 -> £3,382,506.34 (10.4%); £3,774,270.62 -> £3,382,506.50 (10.4%); £3,774,270.77 -> £3,382,506.66 (10.4%); £3,774,270.94 -> £3,382,506.81 (10.4%); £3,774,271.13 -> £3,382,506.98 (10.4%); £3,774,271.33 -> £3,382,507.15 (10.4%); £3,774,271.55 -> £3,382,507.32 (10.4%); £3,774,271.79 -> £3,382,507.49 (10.4%); £3,774,272.03 -> £3,382,507.52 (10.4%); £3,774,272.27 -> £3,382,507.55 (10.4%); £3,774,272.50 -> £3,382,507.58 (10.4%); £3,774,272.73 -> £3,382,507.62 (10.4%); £3,774,272.97 -> £3,382,507.65 (10.4%); £3,774,273.21 -> £3,382,507.68 (10.4%); £3,774,273.44 -> £3,382,507.71 (10.4%); £3,774,273.68 -> £3,382,507.74 (10.4%); £3,774,273.91 -> £3,382,507.77 (10.4%); £3,774,274.14 -> £3,382,507.80 (10.4%); £3,774,274.37 -> £3,382,507.83 (10.4%); £3,774,274.60 -> £3,382,507.86 (10.4%); £3,774,274.84 -> £3,382,507.89 (10.4%); £3,774,275.08 -> £3,382,508.06 (10.4%); £3,774,275.31 -> £3,382,508.23 (10.4%); £3,774,275.49 -> £3,382,508.40 (10.4%); £3,774,275.66 -> £3,382,508.58 (10.4%); £3,774,275.84 -> £3,382,508.75 (10.4%); £3,774,276.01 -> £3,382,508.92 (10.4%); £3,774,276.19 -> £3,382,509.09 (10.4%); £3,774,276.43 -> £3,382,509.27 (10.4%); £3,774,276.66 -> £3,382,509.44 (10.4%); £3,774,276.89 -> £3,382,509.62 (10.4%); £3,774,277.13 -> £3,382,509.78 (10.4%); £3,774,277.36 -> £3,382,509.81 (10.4%); £3,774,277.59 -> £3,382,509.83 (10.4%); £3,774,277.81 -> £3,382,509.86 (10.4%); £3,774,278.02 -> £3,382,509.88 (10.4%); £3,774,278.20 -> £3,382,509.90 (10.4%); £3,774,278.35 -> £3,382,509.92 (10.4%); £3,774,278.51 -> £3,382,509.94 (10.4%); £3,774,278.66 -> £3,382,509.96 (10.4%); £3,774,278.82 -> £3,382,509.97 (10.4%); £3,774,278.98 -> £3,382,509.99 (10.4%); £3,774,279.13 -> £3,382,510.01 (10.4%); £3,774,279.28 -> £3,382,510.02 (10.4%); £3,774,279.44 -> £3,382,510.04 (10.4%); £3,774,279.59 -> £3,382,510.06 (10.4%); £3,774,279.75 -> £3,382,510.07 (10.4%); £3,774,279.91 -> £3,382,510.09 (10.4%); £3,774,280.06 -> £3,382,510.26 (10.4%); £3,774,280.21 -> £3,382,510.44 (10.4%); £3,774,280.39 -> £3,382,510.63 (10.4%); £3,774,280.58 -> £3,382,510.81 (10.4%); £3,774,280.80 -> £3,382,510.99 (10.4%); £3,774,281.02 -> £3,382,511.17 (10.4%); £3,774,281.26 -> £3,382,511.35 (10.4%); £3,774,281.52 -> £3,382,511.53 (10.4%); £3,774,281.77 -> £3,382,511.56 (10.4%); £3,774,282.03 -> £3,382,511.58 (10.4%); £3,774,282.29 -> £3,382,511.61 (10.4%); £3,774,282.55 -> £3,382,511.63 (10.4%); £3,774,282.81 -> £3,382,511.66 (10.4%); £3,774,283.07 -> £3,382,511.68 (10.4%); £3,774,283.33 -> £3,382,511.70 (10.4%); £3,774,283.58 -> £3,382,511.73 (10.4%); £3,774,283.85 -> £3,382,511.75 (10.4%); £3,774,284.10 -> £3,382,511.77 (10.4%); £3,774,284.36 -> £3,382,511.80 (10.4%); £3,774,284.62 -> £3,382,511.82 (10.4%); £3,774,284.89 -> £3,382,511.85 (10.4%); £3,774,285.08 -> £3,382,512.03 (10.4%); £3,774,285.27 -> £3,382,512.22 (10.4%); £3,774,285.46 -> £3,382,512.40 (10.4%); £3,774,285.66 -> £3,382,512.59 (10.4%); £3,774,285.85 -> £3,382,512.77 (10.4%); £3,774,286.04 -> £3,382,512.96 (10.4%); £3,774,286.24 -> £3,382,513.14 (10.4%); £3,774,286.51 -> £3,382,513.32 (10.4%); £3,774,286.76 -> £3,382,513.51 (10.4%); £3,774,287.02 -> £3,382,513.69 (10.4%); £3,774,287.28 -> £3,382,513.87 (10.4%); £3,774,287.54 -> £3,382,513.90 (10.4%); £3,774,287.80 -> £3,382,513.93 (10.4%); £3,774,288.04 -> £3,382,513.95 (10.4%); £3,774,288.26 -> £3,382,513.97 (10.4%); £3,774,288.46 -> £3,382,513.99 (10.4%); £3,774,288.62 -> £3,382,514.01 (10.4%); £3,774,288.78 -> £3,382,514.03 (10.4%); £3,774,288.94 -> £3,382,514.05 (10.4%); £3,774,289.10 -> £3,382,514.06 (10.4%); £3,774,289.25 -> £3,382,514.08 (10.4%); £3,774,289.40 -> £3,382,514.10 (10.4%); £3,774,289.56 -> £3,382,514.11 (10.4%); £3,774,289.71 -> £3,382,514.13 (10.4%); £3,774,289.87 -> £3,382,514.15 (10.4%); £3,774,290.02 -> £3,382,514.16 (10.4%); £3,774,290.18 -> £3,382,514.18 (10.4%); £3,774,290.33 -> £3,382,514.33 (10.4%); £3,774,290.49 -> £3,382,514.48 (10.4%); £3,774,290.67 -> £3,382,514.63 (10.4%); £3,774,290.86 -> £3,382,514.78 (10.4%); £3,774,291.08 -> £3,382,514.94 (10.4%); £3,774,291.30 -> £3,382,515.10 (10.4%); £3,774,291.54 -> £3,382,515.25 (10.4%); £3,774,291.79 -> £3,382,515.40 (10.4%); £3,774,292.05 -> £3,382,515.43 (10.4%); £3,774,292.31 -> £3,382,515.45 (10.4%); £3,774,292.57 -> £3,382,515.48 (10.4%); £3,774,292.82 -> £3,382,515.50 (10.4%); £3,774,293.08 -> £3,382,515.52 (10.4%); £3,774,293.35 -> £3,382,515.55 (10.4%); £3,774,293.61 -> £3,382,515.57 (10.4%); £3,774,293.88 -> £3,382,515.60 (10.4%); £3,774,294.13 -> £3,382,515.62 (10.4%); £3,774,294.39 -> £3,382,515.64 (10.4%); £3,774,294.65 -> £3,382,515.67 (10.4%); £3,774,294.91 -> £3,382,515.69 (10.4%); £3,774,295.17 -> £3,382,515.72 (10.4%); £3,774,295.42 -> £3,382,515.88 (10.4%); £3,774,295.68 -> £3,382,516.05 (10.4%); £3,774,295.94 -> £3,382,516.22 (10.4%); £3,774,296.20 -> £3,382,516.39 (10.4%); £3,774,296.46 -> £3,382,516.55 (10.4%); £3,774,296.71 -> £3,382,516.72 (10.4%); £3,774,296.96 -> £3,382,516.88 (10.4%); £3,774,297.23 -> £3,382,517.05 (10.4%); £3,774,297.49 -> £3,382,517.21 (10.4%); £3,774,297.75 -> £3,382,517.37 (10.4%); £3,774,298.01 -> £3,382,517.52 (10.4%); £3,774,298.28 -> £3,382,517.55 (10.4%); £3,774,298.54 -> £3,382,517.58 (10.4%); £3,774,298.78 -> £3,382,517.60 (10.4%); £3,774,299.00 -> £3,382,517.63 (10.4%); £3,774,299.20 -> £3,382,517.65 (10.4%); £3,774,299.35 -> £3,382,517.66 (10.4%); £3,774,299.51 -> £3,382,517.68 (10.4%); £3,774,299.66 -> £3,382,517.70 (10.4%); £3,774,299.82 -> £3,382,517.72 (10.4%); £3,774,299.97 -> £3,382,517.73 (10.4%); £3,774,300.12 -> £3,382,517.75 (10.4%); £3,774,300.27 -> £3,382,517.77 (10.4%); £3,774,300.43 -> £3,382,517.78 (10.4%); £3,774,300.58 -> £3,382,517.80 (10.4%); £3,774,300.74 -> £3,382,517.82 (10.4%); £3,774,300.90 -> £3,382,517.83 (10.4%); £3,774,301.06 -> £3,382,517.92 (10.4%); £3,774,301.22 -> £3,382,518.01 (10.4%); £3,774,301.39 -> £3,382,518.11 (10.4%); £3,774,301.59 -> £3,382,518.21 (10.4%); £3,774,301.80 -> £3,382,518.31 (10.4%); £3,774,302.02 -> £3,382,518.40 (10.4%); £3,774,302.26 -> £3,382,518.50 (10.4%); £3,774,302.52 -> £3,382,518.59 (10.4%); £3,774,302.78 -> £3,382,518.62 (10.4%); £3,774,303.03 -> £3,382,518.64 (10.4%); £3,774,303.30 -> £3,382,518.67 (10.4%); £3,774,303.55 -> £3,382,518.69 (10.4%); £3,774,303.82 -> £3,382,518.71 (10.4%); £3,774,304.06 -> £3,382,518.74 (10.4%); £3,774,304.31 -> £3,382,518.76 (10.4%); £3,774,304.58 -> £3,382,518.79 (10.4%); £3,774,304.83 -> £3,382,518.81 (10.4%); £3,774,305.09 -> £3,382,518.83 (10.4%); £3,774,305.36 -> £3,382,518.86 (10.4%); £3,774,305.61 -> £3,382,518.88 (10.4%); £3,774,305.88 -> £3,382,518.91 (10.4%); £3,774,306.13 -> £3,382,519.01 (10.4%); £3,774,306.33 -> £3,382,519.12 (10.4%); £3,774,306.52 -> £3,382,519.23 (10.4%); £3,774,306.71 -> £3,382,519.34 (10.4%); £3,774,306.97 -> £3,382,519.46 (10.4%); £3,774,307.23 -> £3,382,519.57 (10.4%); £3,774,307.48 -> £3,382,519.68 (10.4%); £3,774,307.75 -> £3,382,519.79 (10.4%); £3,774,308.01 -> £3,382,519.90 (10.4%); £3,774,308.28 -> £3,382,520.00 (10.4%); £3,774,308.54 -> £3,382,520.11 (10.4%); £3,774,308.78 -> £3,382,520.14 (10.4%); £3,774,309.05 -> £3,382,520.16 (10.4%); £3,774,309.29 -> £3,382,520.19 (10.4%); £3,774,309.51 -> £3,382,520.21 (10.4%); £3,774,309.71 -> £3,382,520.23 (10.4%); £3,774,309.87 -> £3,382,520.25 (10.4%); £3,774,310.02 -> £3,382,520.27 (10.4%); £3,774,310.17 -> £3,382,520.28 (10.4%); £3,774,310.33 -> £3,382,520.30 (10.4%); £3,774,310.49 -> £3,382,520.32 (10.4%); £3,774,310.64 -> £3,382,520.34 (10.4%); £3,774,310.80 -> £3,382,520.35 (10.4%); £3,774,310.96 -> £3,382,520.37 (10.4%); £3,774,311.12 -> £3,382,520.38 (10.4%); £3,774,311.28 -> £3,382,520.40 (10.4%); £3,774,311.44 -> £3,382,520.42 (10.4%); £3,774,311.59 -> £3,382,520.48 (10.4%); £3,774,311.75 -> £3,382,520.55 (10.4%); £3,774,311.92 -> £3,382,520.62 (10.4%); £3,774,312.11 -> £3,382,520.69 (10.4%); £3,774,312.32 -> £3,382,520.77 (10.4%); £3,774,312.55 -> £3,382,520.84 (10.4%); £3,774,312.79 -> £3,382,520.91 (10.4%); £3,774,313.05 -> £3,382,520.98 (10.4%); £3,774,313.33 -> £3,382,521.01 (10.4%); £3,774,313.59 -> £3,382,521.03 (10.4%); £3,774,313.85 -> £3,382,521.06 (10.4%); £3,774,314.12 -> £3,382,521.08 (10.4%); £3,774,314.38 -> £3,382,521.10 (10.4%); £3,774,314.64 -> £3,382,521.13 (10.4%); £3,774,314.90 -> £3,382,521.15 (10.4%); £3,774,315.16 -> £3,382,521.18 (10.4%); £3,774,315.43 -> £3,382,521.20 (10.4%); £3,774,315.68 -> £3,382,521.22 (10.4%); £3,774,315.93 -> £3,382,521.25 (10.4%); £3,774,316.19 -> £3,382,521.27 (10.4%); £3,774,316.46 -> £3,382,521.30 (10.4%); £3,774,316.71 -> £3,382,521.38 (10.4%); £3,774,316.98 -> £3,382,521.47 (10.4%); £3,774,317.24 -> £3,382,521.56 (10.4%); £3,774,317.49 -> £3,382,521.65 (10.4%); £3,774,317.76 -> £3,382,521.74 (10.4%); £3,774,318.02 -> £3,382,521.83 (10.4%); £3,774,318.28 -> £3,382,521.92 (10.4%); £3,774,318.54 -> £3,382,522.01 (10.4%); £3,774,318.80 -> £3,382,522.09 (10.4%); £3,774,319.05 -> £3,382,522.17 (10.4%); £3,774,319.30 -> £3,382,522.25 (10.4%); £3,774,319.56 -> £3,382,522.28 (10.4%); £3,774,319.82 -> £3,382,522.31 (10.4%); £3,774,320.06 -> £3,382,522.33 (10.4%); £3,774,320.28 -> £3,382,522.36 (10.4%); £3,774,320.48 -> £3,382,522.37 (10.4%); £3,774,320.64 -> £3,382,522.39 (10.4%); £3,774,320.80 -> £3,382,522.41 (10.4%); £3,774,320.95 -> £3,382,522.43 (10.4%); £3,774,321.11 -> £3,382,522.45 (10.4%); £3,774,321.27 -> £3,382,522.46 (10.4%); £3,774,321.43 -> £3,382,522.48 (10.4%); £3,774,321.58 -> £3,382,522.50 (10.4%); £3,774,321.74 -> £3,382,522.51 (10.4%); £3,774,321.90 -> £3,382,522.53 (10.4%); £3,774,322.06 -> £3,382,522.55 (10.4%); £3,774,322.22 -> £3,382,522.56 (10.4%); £3,774,322.38 -> £3,382,522.67 (10.4%); £3,774,322.54 -> £3,382,522.77 (10.4%); £3,774,322.72 -> £3,382,522.88 (10.4%); £3,774,322.91 -> £3,382,523.00 (10.4%); £3,774,323.12 -> £3,382,523.11 (10.4%); £3,774,323.35 -> £3,382,523.22 (10.4%); £3,774,323.60 -> £3,382,523.32 (10.4%); £3,774,323.86 -> £3,382,523.43 (10.4%); £3,774,324.12 -> £3,382,523.46 (10.4%); £3,774,324.39 -> £3,382,523.48 (10.4%); £3,774,324.65 -> £3,382,523.50 (10.4%); £3,774,324.90 -> £3,382,523.53 (10.4%); £3,774,325.16 -> £3,382,523.55 (10.4%); £3,774,325.43 -> £3,382,523.58 (10.4%); £3,774,325.68 -> £3,382,523.60 (10.4%); £3,774,325.94 -> £3,382,523.62 (10.4%); £3,774,326.20 -> £3,382,523.65 (10.4%); £3,774,326.46 -> £3,382,523.67 (10.4%); £3,774,326.72 -> £3,382,523.69 (10.4%); £3,774,326.99 -> £3,382,523.72 (10.4%); £3,774,327.24 -> £3,382,523.75 (10.4%); £3,774,327.44 -> £3,382,523.86 (10.4%); £3,774,327.71 -> £3,382,523.99 (10.4%); £3,774,327.91 -> £3,382,524.11 (10.4%); £3,774,328.10 -> £3,382,524.23 (10.4%); £3,774,328.30 -> £3,382,524.35 (10.4%); £3,774,328.49 -> £3,382,524.47 (10.4%); £3,774,328.68 -> £3,382,524.59 (10.4%); £3,774,328.94 -> £3,382,524.70 (10.4%); £3,774,329.20 -> £3,382,524.82 (10.4%); £3,774,329.46 -> £3,382,524.94 (10.4%); £3,774,329.73 -> £3,382,525.06 (10.4%); £3,774,329.99 -> £3,382,525.09 (10.4%); £3,774,330.27 -> £3,382,525.11 (10.4%); £3,774,330.50 -> £3,382,525.14 (10.4%); £3,774,330.72 -> £3,382,525.16 (10.4%); £3,774,330.92 -> £3,382,525.18 (10.4%); £3,774,331.06 -> £3,382,525.20 (10.4%); £3,774,331.20 -> £3,382,525.22 (10.4%); £3,774,331.34 -> £3,382,525.24 (10.4%); £3,774,331.48 -> £3,382,525.26 (10.4%); £3,774,331.62 -> £3,382,525.27 (10.4%); £3,774,331.75 -> £3,382,525.29 (10.4%); £3,774,331.89 -> £3,382,525.31 (10.4%); £3,774,332.04 -> £3,382,525.32 (10.4%); £3,774,332.17 -> £3,382,525.34 (10.4%); £3,774,332.30 -> £3,382,525.36 (10.4%); £3,774,332.44 -> £3,382,525.37 (10.4%); £3,774,332.58 -> £3,382,525.46 (10.4%); £3,774,332.72 -> £3,382,525.55 (10.4%); £3,774,332.88 -> £3,382,525.65 (10.4%); £3,774,333.04 -> £3,382,525.74 (10.4%); £3,774,333.23 -> £3,382,525.83 (10.4%); £3,774,333.43 -> £3,382,525.93 (10.4%); £3,774,333.64 -> £3,382,526.03 (10.4%); £3,774,333.86 -> £3,382,526.13 (10.4%); £3,774,334.09 -> £3,382,526.16 (10.4%); £3,774,334.31 -> £3,382,526.18 (10.4%); £3,774,334.53 -> £3,382,526.21 (10.4%); £3,774,334.76 -> £3,382,526.24 (10.4%); £3,774,335.00 -> £3,382,526.26 (10.4%); £3,774,335.23 -> £3,382,526.29 (10.4%); £3,774,335.45 -> £3,382,526.32 (10.4%); £3,774,335.68 -> £3,382,526.34 (10.4%); £3,774,335.90 -> £3,382,526.37 (10.4%); £3,774,336.13 -> £3,382,526.39 (10.4%); £3,774,336.36 -> £3,382,526.42 (10.4%); £3,774,336.59 -> £3,382,526.45 (10.4%); £3,774,336.81 -> £3,382,526.47 (10.4%); £3,774,336.98 -> £3,382,526.58 (10.4%); £3,774,337.15 -> £3,382,526.68 (10.4%); £3,774,337.32 -> £3,382,526.79 (10.4%); £3,774,337.50 -> £3,382,526.91 (10.4%); £3,774,337.67 -> £3,382,527.02 (10.4%); £3,774,337.84 -> £3,382,527.13 (10.4%); £3,774,338.01 -> £3,382,527.24 (10.4%); £3,774,338.24 -> £3,382,527.34 (10.4%); £3,774,338.47 -> £3,382,527.45 (10.4%); £3,774,338.70 -> £3,382,527.56 (10.4%); £3,774,338.93 -> £3,382,527.66 (10.4%); £3,774,339.15 -> £3,382,527.69 (10.4%); £3,774,339.38 -> £3,382,527.71 (10.4%); £3,774,339.59 -> £3,382,527.74 (10.4%); £3,774,339.79 -> £3,382,527.76 (10.4%); £3,774,339.96 -> £3,382,527.78 (10.4%); £3,774,340.10 -> £3,382,527.80 (10.4%); £3,774,340.24 -> £3,382,527.82 (10.4%); £3,774,340.37 -> £3,382,527.84 (10.4%); £3,774,340.51 -> £3,382,527.86 (10.4%); £3,774,340.65 -> £3,382,527.88 (10.4%); £3,774,340.79 -> £3,382,527.89 (10.4%); £3,774,340.93 -> £3,382,527.91 (10.4%); £3,774,341.07 -> £3,382,527.93 (10.4%); £3,774,341.21 -> £3,382,527.94 (10.4%); £3,774,341.35 -> £3,382,527.96 (10.4%); £3,774,341.48 -> £3,382,527.98 (10.4%); £3,774,341.61 -> £3,382,528.07 (10.4%); £3,774,341.75 -> £3,382,528.16 (10.4%); £3,774,341.91 -> £3,382,528.25 (10.4%); £3,774,342.08 -> £3,382,528.34 (10.4%); £3,774,342.27 -> £3,382,528.43 (10.4%); £3,774,342.46 -> £3,382,528.53 (10.4%); £3,774,342.68 -> £3,382,528.63 (10.4%); £3,774,342.90 -> £3,382,528.74 (10.4%); £3,774,343.13 -> £3,382,528.77 (10.4%); £3,774,343.36 -> £3,382,528.80 (10.4%); £3,774,343.59 -> £3,382,528.83 (10.4%); £3,774,343.83 -> £3,382,528.86 (10.4%); £3,774,344.05 -> £3,382,528.89 (10.4%); £3,774,344.28 -> £3,382,528.92 (10.4%); £3,774,344.51 -> £3,382,528.96 (10.4%); £3,774,344.74 -> £3,382,528.99 (10.4%); £3,774,344.97 -> £3,382,529.02 (10.4%); £3,774,345.20 -> £3,382,529.05 (10.4%); £3,774,345.44 -> £3,382,529.07 (10.4%); £3,774,345.67 -> £3,382,529.10 (10.4%); £3,774,345.89 -> £3,382,529.13 (10.4%); £3,774,346.13 -> £3,382,529.25 (10.4%); £3,774,346.36 -> £3,382,529.36 (10.4%); £3,774,346.59 -> £3,382,529.47 (10.4%); £3,774,346.76 -> £3,382,529.59 (10.4%); £3,774,346.99 -> £3,382,529.70 (10.4%); £3,774,347.16 -> £3,382,529.81 (10.4%); £3,774,347.33 -> £3,382,529.93 (10.4%); £3,774,347.56 -> £3,382,530.04 (10.4%); £3,774,347.79 -> £3,382,530.15 (10.4%); £3,774,348.02 -> £3,382,530.26 (10.4%); £3,774,348.25 -> £3,382,530.37 (10.4%); £3,774,348.47 -> £3,382,530.40 (10.4%); £3,774,348.70 -> £3,382,530.43 (10.4%); £3,774,348.90 -> £3,382,530.46 (10.4%); £3,774,349.10 -> £3,382,530.48 (10.4%); £3,774,349.27 -> £3,382,530.50 (10.4%); £3,774,349.43 -> £3,382,530.52 (10.4%); £3,774,349.60 -> £3,382,530.54 (10.4%); £3,774,349.76 -> £3,382,530.55 (10.4%); £3,774,349.92 -> £3,382,530.57 (10.4%); £3,774,350.08 -> £3,382,530.59 (10.4%); £3,774,350.24 -> £3,382,530.60 (10.4%); £3,774,350.39 -> £3,382,530.62 (10.4%); £3,774,350.56 -> £3,382,530.64 (10.4%); £3,774,350.71 -> £3,382,530.65 (10.4%); £3,774,350.87 -> £3,382,530.67 (10.4%); £3,774,351.03 -> £3,382,530.69 (10.4%); £3,774,351.20 -> £3,382,530.81 (10.4%); £3,774,351.36 -> £3,382,530.94 (10.4%); £3,774,351.53 -> £3,382,531.07 (10.4%); £3,774,351.72 -> £3,382,531.20 (10.4%); £3,774,351.93 -> £3,382,531.33 (10.4%); £3,774,352.16 -> £3,382,531.46 (10.4%); £3,774,352.41 -> £3,382,531.58 (10.4%); £3,774,352.66 -> £3,382,531.71 (10.4%); £3,774,352.92 -> £3,382,531.73 (10.4%); £3,774,353.18 -> £3,382,531.76 (10.4%); £3,774,353.45 -> £3,382,531.78 (10.4%); £3,774,353.71 -> £3,382,531.81 (10.4%); £3,774,353.98 -> £3,382,531.83 (10.4%); £3,774,354.25 -> £3,382,531.85 (10.4%); £3,774,354.51 -> £3,382,531.88 (10.4%); £3,774,354.77 -> £3,382,531.90 (10.4%); £3,774,355.05 -> £3,382,531.92 (10.4%); £3,774,355.32 -> £3,382,531.95 (10.4%); £3,774,355.58 -> £3,382,531.97 (10.4%); £3,774,355.84 -> £3,382,532.00 (10.4%); £3,774,356.10 -> £3,382,532.03 (10.4%); £3,774,356.36 -> £3,382,532.16 (10.4%); £3,774,356.55 -> £3,382,532.30 (10.4%); £3,774,356.75 -> £3,382,532.44 (10.4%); £3,774,356.94 -> £3,382,532.59 (10.4%); £3,774,357.21 -> £3,382,532.73 (10.4%); £3,774,357.46 -> £3,382,532.87 (10.4%); £3,774,357.73 -> £3,382,533.01 (10.4%); £3,774,358.00 -> £3,382,533.15 (10.4%); £3,774,358.26 -> £3,382,533.29 (10.4%); £3,774,358.53 -> £3,382,533.43 (10.4%); £3,774,358.79 -> £3,382,533.56 (10.4%); £3,774,359.06 -> £3,382,533.59 (10.4%); £3,774,359.32 -> £3,382,533.62 (10.4%); £3,774,359.58 -> £3,382,533.65 (10.4%); £3,774,359.80 -> £3,382,533.67 (10.4%); £3,774,360.00 -> £3,382,533.69 (10.4%); £3,774,360.16 -> £3,382,533.71 (10.4%); £3,774,360.32 -> £3,382,533.72 (10.4%); £3,774,360.48 -> £3,382,533.74 (10.4%); £3,774,360.64 -> £3,382,533.76 (10.4%); £3,774,360.79 -> £3,382,533.78 (10.4%); £3,774,360.95 -> £3,382,533.79 (10.4%); £3,774,361.11 -> £3,382,533.81 (10.4%); £3,774,361.27 -> £3,382,533.83 (10.4%); £3,774,361.43 -> £3,382,533.84 (10.4%); £3,774,361.59 -> £3,382,533.86 (10.4%); £3,774,361.75 -> £3,382,533.88 (10.4%); £3,774,361.90 -> £3,382,533.99 (10.4%); £3,774,362.06 -> £3,382,534.11 (10.4%); £3,774,362.23 -> £3,382,534.23 (10.4%); £3,774,362.43 -> £3,382,534.35 (10.4%); £3,774,362.64 -> £3,382,534.48 (10.4%); £3,774,362.87 -> £3,382,534.60 (10.4%); £3,774,363.12 -> £3,382,534.72 (10.4%); £3,774,363.38 -> £3,382,534.84 (10.4%); £3,774,363.65 -> £3,382,534.87 (10.4%); £3,774,363.91 -> £3,382,534.89 (10.4%); £3,774,364.19 -> £3,382,534.91 (10.4%); £3,774,364.45 -> £3,382,534.94 (10.4%); £3,774,364.71 -> £3,382,534.96 (10.4%); £3,774,364.97 -> £3,382,534.99 (10.4%); £3,774,365.23 -> £3,382,535.01 (10.4%); £3,774,365.50 -> £3,382,535.04 (10.4%); £3,774,365.76 -> £3,382,535.06 (10.4%); £3,774,366.02 -> £3,382,535.08 (10.4%); £3,774,366.29 -> £3,382,535.11 (10.4%); £3,774,366.56 -> £3,382,535.13 (10.4%); £3,774,366.82 -> £3,382,535.16 (10.4%); £3,774,367.09 -> £3,382,535.29 (10.4%); £3,774,367.35 -> £3,382,535.43 (10.4%); £3,774,367.61 -> £3,382,535.57 (10.4%); £3,774,367.88 -> £3,382,535.71 (10.4%); £3,774,368.14 -> £3,382,535.84 (10.4%); £3,774,368.41 -> £3,382,535.98 (10.4%); £3,774,368.61 -> £3,382,536.11 (10.4%); £3,774,368.86 -> £3,382,536.24 (10.4%); £3,774,369.12 -> £3,382,536.37 (10.4%); £3,774,369.38 -> £3,382,536.50 (10.4%); £3,774,369.66 -> £3,382,536.63 (10.4%); £3,774,369.92 -> £3,382,536.66 (10.4%); £3,774,370.18 -> £3,382,536.69 (10.4%); £3,774,370.43 -> £3,382,536.71 (10.4%); £3,774,370.65 -> £3,382,536.74 (10.4%); £3,774,370.85 -> £3,382,536.76 (10.4%); £3,774,371.02 -> £3,382,536.78 (10.4%); £3,774,371.18 -> £3,382,536.79 (10.4%); £3,774,371.34 -> £3,382,536.81 (10.4%); £3,774,371.50 -> £3,382,536.83 (10.4%); £3,774,371.67 -> £3,382,536.84 (10.4%); £3,774,371.82 -> £3,382,536.86 (10.4%); £3,774,371.99 -> £3,382,536.88 (10.4%); £3,774,372.15 -> £3,382,536.89 (10.4%); £3,774,372.30 -> £3,382,536.91 (10.4%); £3,774,372.47 -> £3,382,536.93 (10.4%); £3,774,372.63 -> £3,382,536.95 (10.4%); £3,774,372.79 -> £3,382,537.06 (10.4%); £3,774,372.95 -> £3,382,537.17 (10.4%); £3,774,373.13 -> £3,382,537.28 (10.4%); £3,774,373.33 -> £3,382,537.40 (10.4%); £3,774,373.54 -> £3,382,537.52 (10.4%); £3,774,373.76 -> £3,382,537.63 (10.4%); £3,774,374.01 -> £3,382,537.75 (10.4%); £3,774,374.28 -> £3,382,537.86 (10.4%); £3,774,374.55 -> £3,382,537.88 (10.4%); £3,774,374.81 -> £3,382,537.91 (10.4%); £3,774,375.08 -> £3,382,537.93 (10.4%); £3,774,375.35 -> £3,382,537.95 (10.4%); £3,774,375.61 -> £3,382,537.98 (10.4%); £3,774,375.87 -> £3,382,538.00 (10.4%); £3,774,376.15 -> £3,382,538.03 (10.4%); £3,774,376.42 -> £3,382,538.05 (10.4%); £3,774,376.69 -> £3,382,538.07 (10.4%); £3,774,376.95 -> £3,382,538.10 (10.4%); £3,774,377.22 -> £3,382,538.12 (10.4%); £3,774,377.49 -> £3,382,538.15 (10.4%); £3,774,377.76 -> £3,382,538.18 (10.4%); £3,774,378.02 -> £3,382,538.30 (10.4%); £3,774,378.29 -> £3,382,538.43 (10.4%); £3,774,378.55 -> £3,382,538.55 (10.4%); £3,774,378.82 -> £3,382,538.68 (10.4%); £3,774,379.02 -> £3,382,538.81 (10.4%); £3,774,379.22 -> £3,382,538.94 (10.4%); £3,774,379.49 -> £3,382,539.06 (10.4%); £3,774,379.75 -> £3,382,539.19 (10.4%); £3,774,380.01 -> £3,382,539.31 (10.4%); £3,774,380.28 -> £3,382,539.44 (10.4%); £3,774,380.55 -> £3,382,539.57 (10.4%); £3,774,380.82 -> £3,382,539.60 (10.4%); £3,774,381.08 -> £3,382,539.62 (10.4%); £3,774,381.33 -> £3,382,539.65 (10.4%); £3,774,381.56 -> £3,382,539.67 (10.4%); £3,774,381.76 -> £3,382,539.69 (10.4%); £3,774,381.92 -> £3,382,539.71 (10.4%); £3,774,382.07 -> £3,382,539.73 (10.4%); £3,774,382.23 -> £3,382,539.75 (10.4%); £3,774,382.39 -> £3,382,539.76 (10.4%); £3,774,382.56 -> £3,382,539.78 (10.4%); £3,774,382.72 -> £3,382,539.80 (10.4%); £3,774,382.88 -> £3,382,539.81 (10.4%); £3,774,383.05 -> £3,382,539.83 (10.4%); £3,774,383.21 -> £3,382,539.85 (10.4%); £3,774,383.37 -> £3,382,539.86 (10.4%); £3,774,383.53 -> £3,382,539.88 (10.4%); £3,774,383.69 -> £3,382,540.03 (10.4%); £3,774,383.84 -> £3,382,540.18 (10.4%); £3,774,384.03 -> £3,382,540.33 (10.4%); £3,774,384.22 -> £3,382,540.48 (10.4%); £3,774,384.44 -> £3,382,540.63 (10.4%); £3,774,384.67 -> £3,382,540.79 (10.4%); £3,774,384.93 -> £3,382,540.94 (10.4%); £3,774,385.19 -> £3,382,541.09 (10.4%); £3,774,385.46 -> £3,382,541.11 (10.4%); £3,774,385.73 -> £3,382,541.13 (10.4%); £3,774,385.99 -> £3,382,541.16 (10.4%); £3,774,386.26 -> £3,382,541.18 (10.4%); £3,774,386.51 -> £3,382,541.20 (10.4%); £3,774,386.79 -> £3,382,541.23 (10.4%); £3,774,387.07 -> £3,382,541.25 (10.4%); £3,774,387.34 -> £3,382,541.27 (10.4%); £3,774,387.60 -> £3,382,541.30 (10.4%); £3,774,387.86 -> £3,382,541.32 (10.4%); £3,774,388.13 -> £3,382,541.34 (10.4%); £3,774,388.39 -> £3,382,541.37 (10.4%); £3,774,388.67 -> £3,382,541.40 (10.4%); £3,774,388.94 -> £3,382,541.56 (10.4%); £3,774,389.21 -> £3,382,541.73 (10.4%); £3,774,389.48 -> £3,382,541.90 (10.4%); £3,774,389.75 -> £3,382,542.06 (10.4%); £3,774,389.95 -> £3,382,542.23 (10.4%); £3,774,390.22 -> £3,382,542.39 (10.4%); £3,774,390.49 -> £3,382,542.56 (10.4%); £3,774,390.76 -> £3,382,542.72 (10.4%); £3,774,391.03 -> £3,382,542.88 (10.4%); £3,774,391.31 -> £3,382,543.04 (10.4%); £3,774,391.57 -> £3,382,543.19 (10.4%); £3,774,391.83 -> £3,382,543.22 (10.4%); £3,774,392.10 -> £3,382,543.25 (10.4%); £3,774,392.34 -> £3,382,543.27 (10.4%); £3,774,392.57 -> £3,382,543.30 (10.4%); £3,774,392.78 -> £3,382,543.32 (10.4%); £3,774,392.94 -> £3,382,543.33 (10.4%); £3,774,393.10 -> £3,382,543.35 (10.4%); £3,774,393.26 -> £3,382,543.37 (10.4%); £3,774,393.42 -> £3,382,543.39 (10.4%); £3,774,393.58 -> £3,382,543.40 (10.4%); £3,774,393.74 -> £3,382,543.42 (10.4%); £3,774,393.90 -> £3,382,543.44 (10.4%); £3,774,394.06 -> £3,382,543.45 (10.4%); £3,774,394.23 -> £3,382,543.47 (10.4%); £3,774,394.39 -> £3,382,543.49 (10.4%); £3,774,394.55 -> £3,382,543.50 (10.4%); £3,774,394.71 -> £3,382,543.69 (10.4%); £3,774,394.86 -> £3,382,543.88 (10.4%); £3,774,395.04 -> £3,382,544.08 (10.4%); £3,774,395.24 -> £3,382,544.28 (10.4%); £3,774,395.45 -> £3,382,544.48 (10.4%); £3,774,395.68 -> £3,382,544.68 (10.4%); £3,774,395.93 -> £3,382,544.88 (10.4%); £3,774,396.21 -> £3,382,545.07 (10.4%); £3,774,396.46 -> £3,382,545.10 (10.4%); £3,774,396.73 -> £3,382,545.12 (10.4%); £3,774,396.98 -> £3,382,545.14 (10.4%); £3,774,397.24 -> £3,382,545.17 (10.4%); £3,774,397.50 -> £3,382,545.19 (10.4%); £3,774,397.77 -> £3,382,545.22 (10.4%); £3,774,398.02 -> £3,382,545.24 (10.4%); £3,774,398.30 -> £3,382,545.26 (10.4%); £3,774,398.57 -> £3,382,545.29 (10.4%); £3,774,398.83 -> £3,382,545.31 (10.4%); £3,774,399.10 -> £3,382,545.33 (10.4%); £3,774,399.37 -> £3,382,545.36 (10.4%); £3,774,399.63 -> £3,382,545.39 (10.4%); £3,774,399.89 -> £3,382,545.59 (10.4%); £3,774,400.15 -> £3,382,545.79 (10.4%); £3,774,400.35 -> £3,382,545.99 (10.4%); £3,774,400.55 -> £3,382,546.18 (10.4%); £3,774,400.75 -> £3,382,546.38 (10.4%); £3,774,400.95 -> £3,382,546.58 (10.4%); £3,774,401.15 -> £3,382,546.78 (10.4%); £3,774,401.42 -> £3,382,546.97 (10.4%); £3,774,401.68 -> £3,382,547.16 (10.4%); £3,774,401.95 -> £3,382,547.36 (10.4%); £3,774,402.21 -> £3,382,547.55 (10.4%); £3,774,402.49 -> £3,382,547.58 (10.4%); £3,774,402.75 -> £3,382,547.60 (10.4%); £3,774,402.99 -> £3,382,547.63 (10.4%); £3,774,403.21 -> £3,382,547.65 (10.4%); £3,774,403.41 -> £3,382,547.67 (10.4%); £3,774,403.55 -> £3,382,547.69 (10.4%); £3,774,403.69 -> £3,382,547.71 (10.4%); £3,774,403.83 -> £3,382,547.73 (10.4%); £3,774,403.97 -> £3,382,547.75 (10.4%); £3,774,404.12 -> £3,382,547.76 (10.4%); £3,774,404.25 -> £3,382,547.78 (10.4%); £3,774,404.40 -> £3,382,547.80 (10.4%); £3,774,404.54 -> £3,382,547.81 (10.4%); £3,774,404.67 -> £3,382,547.83 (10.4%); £3,774,404.81 -> £3,382,547.85 (10.4%); £3,774,404.96 -> £3,382,547.86 (10.4%); £3,774,405.10 -> £3,382,548.06 (10.4%); £3,774,405.24 -> £3,382,548.27 (10.4%); £3,774,405.39 -> £3,382,548.47 (10.4%); £3,774,405.57 -> £3,382,548.68 (10.4%); £3,774,405.76 -> £3,382,548.88 (10.4%); £3,774,405.96 -> £3,382,549.09 (10.4%); £3,774,406.19 -> £3,382,549.30 (10.4%); £3,774,406.42 -> £3,382,549.51 (10.4%); £3,774,406.66 -> £3,382,549.53 (10.4%); £3,774,406.89 -> £3,382,549.56 (10.4%); £3,774,407.12 -> £3,382,549.59 (10.4%); £3,774,407.36 -> £3,382,549.61 (10.4%); £3,774,407.59 -> £3,382,549.64 (10.4%); £3,774,407.82 -> £3,382,549.67 (10.4%); £3,774,408.05 -> £3,382,549.69 (10.4%); £3,774,408.28 -> £3,382,549.72 (10.4%); £3,774,408.53 -> £3,382,549.75 (10.4%); £3,774,408.76 -> £3,382,549.77 (10.4%); £3,774,409.00 -> £3,382,549.80 (10.4%); £3,774,409.25 -> £3,382,549.82 (10.4%); £3,774,409.48 -> £3,382,549.85 (10.4%); £3,774,409.66 -> £3,382,550.05 (10.4%); £3,774,409.83 -> £3,382,550.26 (10.4%); £3,774,410.00 -> £3,382,550.47 (10.4%); £3,774,410.18 -> £3,382,550.67 (10.4%); £3,774,410.35 -> £3,382,550.88 (10.4%); £3,774,410.53 -> £3,382,551.09 (10.4%); £3,774,410.71 -> £3,382,551.30 (10.4%); £3,774,410.95 -> £3,382,551.50 (10.4%); £3,774,411.19 -> £3,382,551.70 (10.4%); £3,774,411.42 -> £3,382,551.91 (10.4%); £3,774,411.66 -> £3,382,552.11 (10.4%); £3,774,411.89 -> £3,382,552.13 (10.4%); £3,774,412.13 -> £3,382,552.16 (10.4%); £3,774,412.34 -> £3,382,552.19 (10.4%); £3,774,412.54 -> £3,382,552.21 (10.4%); £3,774,412.73 -> £3,382,552.23 (10.4%); £3,774,412.87 -> £3,382,552.25 (10.4%); £3,774,413.01 -> £3,382,552.27 (10.4%); £3,774,413.15 -> £3,382,552.29 (10.4%); £3,774,413.29 -> £3,382,552.31 (10.4%); £3,774,413.43 -> £3,382,552.32 (10.4%); £3,774,413.57 -> £3,382,552.34 (10.4%); £3,774,413.71 -> £3,382,552.36 (10.4%); £3,774,413.85 -> £3,382,552.37 (10.4%); £3,774,413.99 -> £3,382,552.39 (10.4%); £3,774,414.13 -> £3,382,552.41 (10.4%); £3,774,414.27 -> £3,382,552.42 (10.4%); £3,774,414.41 -> £3,382,552.60 (10.4%); £3,774,414.55 -> £3,382,552.79 (10.4%); £3,774,414.70 -> £3,382,552.97 (10.4%); £3,774,414.88 -> £3,382,553.16 (10.4%); £3,774,415.07 -> £3,382,553.35 (10.4%); £3,774,415.26 -> £3,382,553.55 (10.4%); £3,774,415.48 -> £3,382,553.75 (10.4%); £3,774,415.71 -> £3,382,553.94 (10.4%); £3,774,415.95 -> £3,382,553.97 (10.4%); £3,774,416.19 -> £3,382,554.00 (10.4%); £3,774,416.43 -> £3,382,554.03 (10.4%); £3,774,416.66 -> £3,382,554.07 (10.4%); £3,774,416.90 -> £3,382,554.10 (10.4%); £3,774,417.13 -> £3,382,554.13 (10.4%); £3,774,417.36 -> £3,382,554.16 (10.4%); £3,774,417.61 -> £3,382,554.19 (10.4%); £3,774,417.83 -> £3,382,554.22 (10.4%); £3,774,418.06 -> £3,382,554.25 (10.4%); £3,774,418.30 -> £3,382,554.28 (10.4%); £3,774,418.53 -> £3,382,554.30 (10.4%); £3,774,418.77 -> £3,382,554.34 (10.4%); £3,774,418.95 -> £3,382,554.53 (10.4%); £3,774,419.12 -> £3,382,554.72 (10.4%); £3,774,419.30 -> £3,382,554.91 (10.4%); £3,774,419.48 -> £3,382,555.11 (10.4%); £3,774,419.71 -> £3,382,555.31 (10.4%); £3,774,419.94 -> £3,382,555.51 (10.4%); £3,774,420.12 -> £3,382,555.71 (10.4%); £3,774,420.35 -> £3,382,555.91 (10.4%); £3,774,420.59 -> £3,382,556.10 (10.4%); £3,774,420.81 -> £3,382,556.30 (10.4%); £3,774,421.05 -> £3,382,556.49 (10.4%); £3,774,421.28 -> £3,382,556.52 (10.4%); £3,774,421.52 -> £3,382,556.55 (10.4%); £3,774,421.73 -> £3,382,556.58 (10.4%); £3,774,421.93 -> £3,382,556.60 (10.4%); £3,774,422.10 -> £3,382,556.62 (10.4%); £3,774,422.27 -> £3,382,556.64 (10.4%); £3,774,422.42 -> £3,382,556.66 (10.4%); £3,774,422.58 -> £3,382,556.67 (10.4%); £3,774,422.74 -> £3,382,556.69 (10.4%); £3,774,422.91 -> £3,382,556.71 (10.4%); £3,774,423.06 -> £3,382,556.72 (10.4%); £3,774,423.22 -> £3,382,556.74 (10.4%); £3,774,423.38 -> £3,382,556.76 (10.4%); £3,774,423.55 -> £3,382,556.77 (10.4%); £3,774,423.71 -> £3,382,556.79 (10.4%); £3,774,423.87 -> £3,382,556.81 (10.4%); £3,774,424.03 -> £3,382,556.98 (10.4%); £3,774,424.18 -> £3,382,557.14 (10.4%); £3,774,424.36 -> £3,382,557.31 (10.4%); £3,774,424.55 -> £3,382,557.49 (10.4%); £3,774,424.77 -> £3,382,557.67 (10.4%); £3,774,425.00 -> £3,382,557.85 (10.4%); £3,774,425.24 -> £3,382,558.02 (10.4%); £3,774,425.50 -> £3,382,558.19 (10.4%); £3,774,425.77 -> £3,382,558.21 (10.4%); £3,774,426.03 -> £3,382,558.24 (10.4%); £3,774,426.30 -> £3,382,558.26 (10.4%); £3,774,426.57 -> £3,382,558.28 (10.4%); £3,774,426.83 -> £3,382,558.31 (10.4%); £3,774,427.08 -> £3,382,558.33 (10.4%); £3,774,427.35 -> £3,382,558.36 (10.4%); £3,774,427.62 -> £3,382,558.38 (10.4%); £3,774,427.89 -> £3,382,558.40 (10.4%); £3,774,428.15 -> £3,382,558.43 (10.4%); £3,774,428.41 -> £3,382,558.45 (10.4%); £3,774,428.67 -> £3,382,558.48 (10.4%); £3,774,428.94 -> £3,382,558.51 (10.4%); £3,774,429.20 -> £3,382,558.69 (10.4%); £3,774,429.47 -> £3,382,558.87 (10.4%); £3,774,429.74 -> £3,382,559.06 (10.4%); £3,774,430.00 -> £3,382,559.24 (10.4%); £3,774,430.26 -> £3,382,559.42 (10.4%); £3,774,430.51 -> £3,382,559.60 (10.4%); £3,774,430.71 -> £3,382,559.78 (10.4%); £3,774,430.97 -> £3,382,559.96 (10.4%); £3,774,431.24 -> £3,382,560.15 (10.4%); £3,774,431.49 -> £3,382,560.32 (10.4%); £3,774,431.75 -> £3,382,560.50 (10.4%); £3,774,432.01 -> £3,382,560.53 (10.4%); £3,774,432.27 -> £3,382,560.56 (10.4%); £3,774,432.52 -> £3,382,560.58 (10.4%); £3,774,432.74 -> £3,382,560.60 (10.4%); £3,774,432.95 -> £3,382,560.62 (10.4%); £3,774,433.11 -> £3,382,560.64 (10.4%); £3,774,433.26 -> £3,382,560.66 (10.4%); £3,774,433.42 -> £3,382,560.68 (10.4%); £3,774,433.57 -> £3,382,560.69 (10.4%); £3,774,433.73 -> £3,382,560.71 (10.4%); £3,774,433.89 -> £3,382,560.73 (10.4%); £3,774,434.05 -> £3,382,560.74 (10.4%); £3,774,434.20 -> £3,382,560.76 (10.4%); £3,774,434.36 -> £3,382,560.78 (10.4%); £3,774,434.52 -> £3,382,560.79 (10.4%); £3,774,434.67 -> £3,382,560.81 (10.4%); £3,774,434.83 -> £3,382,561.00 (10.4%); £3,774,434.99 -> £3,382,561.20 (10.4%); £3,774,435.16 -> £3,382,561.40 (10.4%); £3,774,435.35 -> £3,382,561.60 (10.4%); £3,774,435.56 -> £3,382,561.80 (10.4%); £3,774,435.79 -> £3,382,562.00 (10.4%); £3,774,436.04 -> £3,382,562.19 (10.4%); £3,774,436.30 -> £3,382,562.39 (10.4%); £3,774,436.56 -> £3,382,562.41 (10.4%); £3,774,436.82 -> £3,382,562.44 (10.4%); £3,774,437.07 -> £3,382,562.46 (10.4%); £3,774,437.32 -> £3,382,562.48 (10.4%); £3,774,437.59 -> £3,382,562.51 (10.4%); £3,774,437.85 -> £3,382,562.53 (10.4%); £3,774,438.11 -> £3,382,562.56 (10.4%); £3,774,438.38 -> £3,382,562.58 (10.4%); £3,774,438.63 -> £3,382,562.60 (10.4%); £3,774,438.90 -> £3,382,562.63 (10.4%); £3,774,439.15 -> £3,382,562.65 (10.4%); £3,774,439.41 -> £3,382,562.68 (10.4%); £3,774,439.67 -> £3,382,562.71 (10.4%); £3,774,439.95 -> £3,382,562.90 (10.4%); £3,774,440.20 -> £3,382,563.10 (10.4%); £3,774,440.39 -> £3,382,563.30 (10.4%); £3,774,440.59 -> £3,382,563.50 (10.4%); £3,774,440.79 -> £3,382,563.70 (10.4%); £3,774,440.99 -> £3,382,563.90 (10.4%); £3,774,441.25 -> £3,382,564.10 (10.4%); £3,774,441.51 -> £3,382,564.30 (10.4%); £3,774,441.78 -> £3,382,564.50 (10.4%); £3,774,442.04 -> £3,382,564.70 (10.4%); £3,774,442.30 -> £3,382,564.90 (10.4%); £3,774,442.56 -> £3,382,564.93 (10.4%); £3,774,442.82 -> £3,382,564.96 (10.4%); £3,774,443.07 -> £3,382,564.98 (10.4%); £3,774,443.29 -> £3,382,565.00 (10.4%); £3,774,443.50 -> £3,382,565.02 (10.4%); £3,774,443.66 -> £3,382,565.04 (10.4%); £3,774,443.81 -> £3,382,565.06 (10.4%); £3,774,443.97 -> £3,382,565.08 (10.4%); £3,774,444.13 -> £3,382,565.09 (10.4%); £3,774,444.28 -> £3,382,565.11 (10.4%); £3,774,444.44 -> £3,382,565.13 (10.4%); £3,774,444.60 -> £3,382,565.14 (10.4%); £3,774,444.76 -> £3,382,565.16 (10.4%); £3,774,444.91 -> £3,382,565.18 (10.4%); £3,774,445.07 -> £3,382,565.19 (10.4%); £3,774,445.23 -> £3,382,565.21 (10.4%); £3,774,445.38 -> £3,382,565.36 (10.4%); £3,774,445.54 -> £3,382,565.51 (10.4%); £3,774,445.72 -> £3,382,565.66 (10.4%); £3,774,445.91 -> £3,382,565.82 (10.4%); £3,774,446.11 -> £3,382,565.98 (10.4%); £3,774,446.34 -> £3,382,566.13 (10.4%); £3,774,446.58 -> £3,382,566.29 (10.4%); £3,774,446.84 -> £3,382,566.44 (10.4%); £3,774,447.09 -> £3,382,566.47 (10.4%); £3,774,447.36 -> £3,382,566.49 (10.4%); £3,774,447.61 -> £3,382,566.52 (10.4%); £3,774,447.87 -> £3,382,566.54 (10.4%); £3,774,448.14 -> £3,382,566.57 (10.4%); £3,774,448.40 -> £3,382,566.59 (10.4%); £3,774,448.67 -> £3,382,566.62 (10.4%); £3,774,448.93 -> £3,382,566.64 (10.4%); £3,774,449.19 -> £3,382,566.66 (10.4%); £3,774,449.45 -> £3,382,566.69 (10.4%); £3,774,449.72 -> £3,382,566.71 (10.4%); £3,774,449.98 -> £3,382,566.73 (10.4%); £3,774,450.24 -> £3,382,566.76 (10.4%); £3,774,450.43 -> £3,382,566.93 (10.4%); £3,774,450.69 -> £3,382,567.09 (10.4%); £3,774,450.90 -> £3,382,567.26 (10.4%); £3,774,451.10 -> £3,382,567.43 (10.4%); £3,774,451.36 -> £3,382,567.59 (10.4%); £3,774,451.62 -> £3,382,567.76 (10.4%); £3,774,451.82 -> £3,382,567.92 (10.4%); £3,774,452.08 -> £3,382,568.08 (10.4%); £3,774,452.34 -> £3,382,568.24 (10.4%); £3,774,452.60 -> £3,382,568.40 (10.4%); £3,774,452.87 -> £3,382,568.56 (10.4%); £3,774,453.14 -> £3,382,568.59 (10.4%); £3,774,453.40 -> £3,382,568.61 (10.4%); £3,774,453.65 -> £3,382,568.64 (10.4%); £3,774,453.87 -> £3,382,568.66 (10.4%); £3,774,454.07 -> £3,382,568.68 (10.4%); £3,774,454.23 -> £3,382,568.70 (10.4%); £3,774,454.39 -> £3,382,568.72 (10.4%); £3,774,454.54 -> £3,382,568.73 (10.4%); £3,774,454.69 -> £3,382,568.75 (10.4%); £3,774,454.85 -> £3,382,568.77 (10.4%); £3,774,455.01 -> £3,382,568.78 (10.4%); £3,774,455.16 -> £3,382,568.80 (10.4%); £3,774,455.31 -> £3,382,568.82 (10.4%); £3,774,455.47 -> £3,382,568.83 (10.4%); £3,774,455.62 -> £3,382,568.85 (10.4%); £3,774,455.78 -> £3,382,568.87 (10.4%); £3,774,455.94 -> £3,382,569.00 (10.4%); £3,774,456.09 -> £3,382,569.14 (10.4%); £3,774,456.26 -> £3,382,569.27 (10.4%); £3,774,456.45 -> £3,382,569.41 (10.4%); £3,774,456.65 -> £3,382,569.55 (10.4%); £3,774,456.88 -> £3,382,569.68 (10.4%); £3,774,457.12 -> £3,382,569.82 (10.4%); £3,774,457.38 -> £3,382,569.95 (10.4%); £3,774,457.64 -> £3,382,569.97 (10.4%); £3,774,457.90 -> £3,382,569.99 (10.4%); £3,774,458.16 -> £3,382,570.02 (10.4%); £3,774,458.41 -> £3,382,570.04 (10.4%); £3,774,458.67 -> £3,382,570.07 (10.4%); £3,774,458.92 -> £3,382,570.09 (10.4%); £3,774,459.18 -> £3,382,570.11 (10.4%); £3,774,459.44 -> £3,382,570.14 (10.4%); £3,774,459.70 -> £3,382,570.16 (10.4%); £3,774,459.95 -> £3,382,570.18 (10.4%); £3,774,460.21 -> £3,382,570.21 (10.4%); £3,774,460.45 -> £3,382,570.23 (10.4%); £3,774,460.71 -> £3,382,570.26 (10.4%); £3,774,460.97 -> £3,382,570.41 (10.4%); £3,774,461.22 -> £3,382,570.55 (10.4%); £3,774,461.48 -> £3,382,570.70 (10.4%); £3,774,461.67 -> £3,382,570.84 (10.4%); £3,774,461.87 -> £3,382,570.99 (10.4%); £3,774,462.13 -> £3,382,571.13 (10.4%); £3,774,462.32 -> £3,382,571.27 (10.4%); £3,774,462.58 -> £3,382,571.41 (10.4%); £3,774,462.83 -> £3,382,571.55 (10.4%); £3,774,463.09 -> £3,382,571.69 (10.4%); £3,774,463.35 -> £3,382,571.83 (10.4%); £3,774,463.62 -> £3,382,571.86 (10.4%); £3,774,463.88 -> £3,382,571.88 (10.4%); £3,774,464.11 -> £3,382,571.91 (10.4%); £3,774,464.34 -> £3,382,571.93 (10.4%); £3,774,464.54 -> £3,382,571.95 (10.4%); £3,774,464.70 -> £3,382,571.97 (10.4%); £3,774,464.85 -> £3,382,571.99 (10.4%); £3,774,465.01 -> £3,382,572.00 (10.4%); £3,774,465.16 -> £3,382,572.02 (10.4%); £3,774,465.32 -> £3,382,572.04 (10.4%); £3,774,465.48 -> £3,382,572.06 (10.4%); £3,774,465.64 -> £3,382,572.07 (10.4%); £3,774,465.79 -> £3,382,572.09 (10.4%); £3,774,465.95 -> £3,382,572.10 (10.4%); £3,774,466.10 -> £3,382,572.12 (10.4%); £3,774,466.25 -> £3,382,572.14 (10.4%); £3,774,466.41 -> £3,382,572.33 (10.4%); £3,774,466.56 -> £3,382,572.51 (10.4%); £3,774,466.74 -> £3,382,572.71 (10.4%); £3,774,466.92 -> £3,382,572.91 (10.4%); £3,774,467.12 -> £3,382,573.11 (10.4%); £3,774,467.34 -> £3,382,573.30 (10.4%); £3,774,467.58 -> £3,382,573.50 (10.4%); £3,774,467.83 -> £3,382,573.70 (10.4%); £3,774,468.09 -> £3,382,573.72 (10.4%); £3,774,468.36 -> £3,382,573.74 (10.4%); £3,774,468.62 -> £3,382,573.77 (10.4%); £3,774,468.88 -> £3,382,573.79 (10.4%); £3,774,469.15 -> £3,382,573.82 (10.4%); £3,774,469.41 -> £3,382,573.84 (10.4%); £3,774,469.67 -> £3,382,573.86 (10.4%); £3,774,469.92 -> £3,382,573.89 (10.4%); £3,774,470.19 -> £3,382,573.91 (10.4%); £3,774,470.45 -> £3,382,573.93 (10.4%); £3,774,470.71 -> £3,382,573.96 (10.4%); £3,774,470.98 -> £3,382,573.98 (10.4%); £3,774,471.23 -> £3,382,574.01 (10.4%); £3,774,471.48 -> £3,382,574.21 (10.4%); £3,774,471.75 -> £3,382,574.41 (10.4%); £3,774,472.01 -> £3,382,574.61 (10.4%); £3,774,472.28 -> £3,382,574.81 (10.4%); £3,774,472.54 -> £3,382,575.01 (10.4%); £3,774,472.81 -> £3,382,575.21 (10.4%); £3,774,473.07 -> £3,382,575.42 (10.4%); £3,774,473.33 -> £3,382,575.61 (10.4%); £3,774,473.60 -> £3,382,575.81 (10.4%); £3,774,473.86 -> £3,382,576.02 (10.4%); £3,774,474.12 -> £3,382,576.21 (10.4%); £3,774,474.39 -> £3,382,576.24 (10.4%); £3,774,474.65 -> £3,382,576.26 (10.4%); £3,774,474.89 -> £3,382,576.29 (10.4%); £3,774,475.11 -> £3,382,576.31 (10.4%); £3,774,475.31 -> £3,382,576.33 (10.4%); £3,774,475.44 -> £3,382,576.35 (10.4%); £3,774,475.58 -> £3,382,576.37 (10.4%); £3,774,475.71 -> £3,382,576.39 (10.4%); £3,774,475.85 -> £3,382,576.40 (10.4%); £3,774,475.98 -> £3,382,576.42 (10.4%); £3,774,476.12 -> £3,382,576.44 (10.4%); £3,774,476.26 -> £3,382,576.45 (10.4%); £3,774,476.39 -> £3,382,576.47 (10.4%); £3,774,476.53 -> £3,382,576.49 (10.4%); £3,774,476.67 -> £3,382,576.50 (10.4%); £3,774,476.80 -> £3,382,576.52 (10.4%); £3,774,476.94 -> £3,382,576.72 (10.4%); £3,774,477.08 -> £3,382,576.92 (10.4%); £3,774,477.23 -> £3,382,577.12 (10.4%); £3,774,477.40 -> £3,382,577.33 (10.4%); £3,774,477.58 -> £3,382,577.53 (10.4%); £3,774,477.78 -> £3,382,577.73 (10.4%); £3,774,477.99 -> £3,382,577.93 (10.4%); £3,774,478.21 -> £3,382,578.13 (10.4%); £3,774,478.44 -> £3,382,578.16 (10.4%); £3,774,478.66 -> £3,382,578.18 (10.4%); £3,774,478.89 -> £3,382,578.21 (10.4%); £3,774,479.11 -> £3,382,578.24 (10.4%); £3,774,479.34 -> £3,382,578.26 (10.4%); £3,774,479.56 -> £3,382,578.29 (10.4%); £3,774,479.79 -> £3,382,578.32 (10.4%); £3,774,480.02 -> £3,382,578.34 (10.4%); £3,774,480.26 -> £3,382,578.37 (10.4%); £3,774,480.48 -> £3,382,578.39 (10.4%); £3,774,480.71 -> £3,382,578.42 (10.4%); £3,774,480.94 -> £3,382,578.45 (10.4%); £3,774,481.16 -> £3,382,578.48 (10.4%); £3,774,481.39 -> £3,382,578.68 (10.4%); £3,774,481.61 -> £3,382,578.89 (10.4%); £3,774,481.84 -> £3,382,579.09 (10.4%); £3,774,482.06 -> £3,382,579.30 (10.4%); £3,774,482.29 -> £3,382,579.51 (10.4%); £3,774,482.51 -> £3,382,579.72 (10.4%); £3,774,482.74 -> £3,382,579.93 (10.4%); £3,774,482.97 -> £3,382,580.14 (10.4%); £3,774,483.20 -> £3,382,580.35 (10.4%); £3,774,483.43 -> £3,382,580.55 (10.4%); £3,774,483.66 -> £3,382,580.75 (10.4%); £3,774,483.88 -> £3,382,580.78 (10.4%); £3,774,484.10 -> £3,382,580.81 (10.4%); £3,774,484.32 -> £3,382,580.84 (10.4%); £3,774,484.51 -> £3,382,580.86 (10.4%); £3,774,484.69 -> £3,382,580.88 (10.4%); £3,774,484.82 -> £3,382,580.90 (10.4%); £3,774,484.95 -> £3,382,580.92 (10.4%); £3,774,485.08 -> £3,382,580.94 (10.4%); £3,774,485.22 -> £3,382,580.96 (10.4%); £3,774,485.35 -> £3,382,580.97 (10.4%); £3,774,485.49 -> £3,382,580.99 (10.4%); £3,774,485.62 -> £3,382,581.01 (10.4%); £3,774,485.76 -> £3,382,581.02 (10.4%); £3,774,485.90 -> £3,382,581.04 (10.4%); £3,774,486.04 -> £3,382,581.06 (10.4%); £3,774,486.17 -> £3,382,581.07 (10.4%); £3,774,486.31 -> £3,382,581.26 (10.4%); £3,774,486.44 -> £3,382,581.44 (10.4%); £3,774,486.60 -> £3,382,581.63 (10.4%); £3,774,486.76 -> £3,382,581.83 (10.4%); £3,774,486.94 -> £3,382,582.02 (10.4%); £3,774,487.14 -> £3,382,582.22 (10.4%); £3,774,487.35 -> £3,382,582.42 (10.4%); £3,774,487.57 -> £3,382,582.63 (10.4%); £3,774,487.80 -> £3,382,582.66 (10.4%); £3,774,488.03 -> £3,382,582.69 (10.4%); £3,774,488.26 -> £3,382,582.72 (10.4%); £3,774,488.47 -> £3,382,582.75 (10.4%); £3,774,488.69 -> £3,382,582.78 (10.4%); £3,774,488.92 -> £3,382,582.82 (10.4%); £3,774,489.14 -> £3,382,582.85 (10.4%); £3,774,489.38 -> £3,382,582.88 (10.4%); £3,774,489.60 -> £3,382,582.91 (10.4%); £3,774,489.83 -> £3,382,582.93 (10.4%); £3,774,490.05 -> £3,382,582.96 (10.4%); £3,774,490.28 -> £3,382,582.99 (10.4%); £3,774,490.51 -> £3,382,583.02 (10.4%); £3,774,490.75 -> £3,382,583.22 (10.4%); £3,774,490.97 -> £3,382,583.42 (10.4%); £3,774,491.20 -> £3,382,583.62 (10.4%); £3,774,491.43 -> £3,382,583.82 (10.4%); £3,774,491.65 -> £3,382,584.02 (10.4%); £3,774,491.87 -> £3,382,584.23 (10.4%); £3,774,492.09 -> £3,382,584.43 (10.4%); £3,774,492.31 -> £3,382,584.64 (10.4%); £3,774,492.54 -> £3,382,584.84 (10.4%); £3,774,492.77 -> £3,382,585.04 (10.4%); £3,774,493.01 -> £3,382,585.23 (10.4%); £3,774,493.23 -> £3,382,585.26 (10.4%); £3,774,493.46 -> £3,382,585.29 (10.4%); £3,774,493.67 -> £3,382,585.32 (10.4%); £3,774,493.86 -> £3,382,585.34 (10.4%); £3,774,494.04 -> £3,382,585.36 (10.4%); £3,774,494.19 -> £3,382,585.38 (10.4%); £3,774,494.34 -> £3,382,585.40 (10.4%); £3,774,494.50 -> £3,382,585.41 (10.4%); £3,774,494.65 -> £3,382,585.43 (10.4%); £3,774,494.81 -> £3,382,585.45 (10.4%); £3,774,494.97 -> £3,382,585.46 (10.4%); £3,774,495.12 -> £3,382,585.48 (10.4%); £3,774,495.27 -> £3,382,585.50 (10.4%); £3,774,495.43 -> £3,382,585.51 (10.4%); £3,774,495.58 -> £3,382,585.53 (10.4%); £3,774,495.74 -> £3,382,585.55 (10.4%); £3,774,495.89 -> £3,382,585.71 (10.4%); £3,774,496.05 -> £3,382,585.88 (10.4%); £3,774,496.21 -> £3,382,586.06 (10.4%); £3,774,496.40 -> £3,382,586.24 (10.4%); £3,774,496.61 -> £3,382,586.42 (10.4%); £3,774,496.84 -> £3,382,586.60 (10.4%); £3,774,497.08 -> £3,382,586.78 (10.4%); £3,774,497.34 -> £3,382,586.96 (10.4%); £3,774,497.60 -> £3,382,586.98 (10.4%); £3,774,497.86 -> £3,382,587.01 (10.4%); £3,774,498.12 -> £3,382,587.03 (10.4%); £3,774,498.37 -> £3,382,587.06 (10.4%); £3,774,498.64 -> £3,382,587.08 (10.4%); £3,774,498.89 -> £3,382,587.10 (10.4%); £3,774,499.16 -> £3,382,587.13 (10.4%); £3,774,499.42 -> £3,382,587.15 (10.4%); £3,774,499.68 -> £3,382,587.17 (10.4%); £3,774,499.93 -> £3,382,587.20 (10.4%); £3,774,500.19 -> £3,382,587.22 (10.4%); £3,774,500.45 -> £3,382,587.25 (10.4%); £3,774,500.71 -> £3,382,587.28 (10.4%); £3,774,500.96 -> £3,382,587.46 (10.4%); £3,774,501.22 -> £3,382,587.64 (10.4%); £3,774,501.46 -> £3,382,587.83 (10.4%); £3,774,501.72 -> £3,382,588.01 (10.4%); £3,774,501.98 -> £3,382,588.20 (10.4%); £3,774,502.23 -> £3,382,588.38 (10.4%); £3,774,502.49 -> £3,382,588.57 (10.4%); £3,774,502.75 -> £3,382,588.75 (10.4%); £3,774,503.01 -> £3,382,588.94 (10.4%); £3,774,503.26 -> £3,382,589.12 (10.4%); £3,774,503.52 -> £3,382,589.30 (10.4%); £3,774,503.78 -> £3,382,589.32 (10.4%); £3,774,504.04 -> £3,382,589.35 (10.4%); £3,774,504.28 -> £3,382,589.38 (10.4%); £3,774,504.50 -> £3,382,589.40 (10.4%); £3,774,504.69 -> £3,382,589.42 (10.4%); £3,774,504.85 -> £3,382,589.44 (10.4%); £3,774,505.00 -> £3,382,589.45 (10.4%); £3,774,505.16 -> £3,382,589.47 (10.4%); £3,774,505.32 -> £3,382,589.49 (10.4%); £3,774,505.47 -> £3,382,589.51 (10.4%); £3,774,505.62 -> £3,382,589.52 (10.4%); £3,774,505.77 -> £3,382,589.54 (10.4%); £3,774,505.92 -> £3,382,589.56 (10.4%); £3,774,506.07 -> £3,382,589.57 (10.4%); £3,774,506.22 -> £3,382,589.59 (10.4%); £3,774,506.37 -> £3,382,589.61 (10.4%); £3,774,506.53 -> £3,382,589.75 (10.4%); £3,774,506.68 -> £3,382,589.89 (10.4%); £3,774,506.86 -> £3,382,590.04 (10.4%); £3,774,507.04 -> £3,382,590.19 (10.4%); £3,774,507.25 -> £3,382,590.34 (10.4%); £3,774,507.47 -> £3,382,590.49 (10.4%); £3,774,507.71 -> £3,382,590.64 (10.4%); £3,774,507.97 -> £3,382,590.79 (10.4%); £3,774,508.22 -> £3,382,590.81 (10.4%); £3,774,508.48 -> £3,382,590.83 (10.4%); £3,774,508.74 -> £3,382,590.86 (10.4%); £3,774,508.99 -> £3,382,590.88 (10.4%); £3,774,509.24 -> £3,382,590.91 (10.4%); £3,774,509.50 -> £3,382,590.93 (10.4%); £3,774,509.76 -> £3,382,590.96 (10.4%); £3,774,510.01 -> £3,382,590.98 (10.4%); £3,774,510.26 -> £3,382,591.00 (10.4%); £3,774,510.53 -> £3,382,591.03 (10.4%); £3,774,510.78 -> £3,382,591.05 (10.4%); £3,774,511.05 -> £3,382,591.08 (10.4%); £3,774,511.30 -> £3,382,591.10 (10.4%); £3,774,511.56 -> £3,382,591.26 (10.4%); £3,774,511.82 -> £3,382,591.42 (10.4%); £3,774,512.07 -> £3,382,591.58 (10.4%); £3,774,512.33 -> £3,382,591.74 (10.4%); £3,774,512.59 -> £3,382,591.89 (10.4%); £3,774,512.84 -> £3,382,592.05 (10.4%); £3,774,513.10 -> £3,382,592.21 (10.4%); £3,774,513.36 -> £3,382,592.36 (10.4%); £3,774,513.62 -> £3,382,592.52 (10.4%); £3,774,513.87 -> £3,382,592.67 (10.4%); £3,774,514.13 -> £3,382,592.82 (10.4%); £3,774,514.38 -> £3,382,592.85 (10.4%); £3,774,514.65 -> £3,382,592.88 (10.4%); £3,774,514.88 -> £3,382,592.90 (10.4%); £3,774,515.10 -> £3,382,592.93 (10.4%); £3,774,515.29 -> £3,382,592.95 (10.4%); £3,774,515.44 -> £3,382,592.97 (10.4%); £3,774,515.59 -> £3,382,592.98 (10.4%); £3,774,515.75 -> £3,382,593.00 (10.4%); £3,774,515.89 -> £3,382,593.02 (10.4%); £3,774,516.04 -> £3,382,593.03 (10.4%); £3,774,516.20 -> £3,382,593.05 (10.4%); £3,774,516.35 -> £3,382,593.07 (10.4%); £3,774,516.50 -> £3,382,593.08 (10.4%); £3,774,516.65 -> £3,382,593.10 (10.4%); £3,774,516.81 -> £3,382,593.12 (10.4%); £3,774,516.95 -> £3,382,593.13 (10.4%); £3,774,517.11 -> £3,382,593.30 (10.4%); £3,774,517.26 -> £3,382,593.46 (10.4%); £3,774,517.44 -> £3,382,593.64 (10.4%); £3,774,517.63 -> £3,382,593.81 (10.4%); £3,774,517.83 -> £3,382,593.99 (10.4%); £3,774,518.05 -> £3,382,594.16 (10.4%); £3,774,518.29 -> £3,382,594.34 (10.4%); £3,774,518.54 -> £3,382,594.51 (10.4%); £3,774,518.79 -> £3,382,594.54 (10.4%); £3,774,519.04 -> £3,382,594.56 (10.4%); £3,774,519.30 -> £3,382,594.59 (10.4%); £3,774,519.56 -> £3,382,594.61 (10.4%); £3,774,519.82 -> £3,382,594.64 (10.4%); £3,774,520.08 -> £3,382,594.66 (10.4%); £3,774,520.34 -> £3,382,594.68 (10.4%); £3,774,520.60 -> £3,382,594.71 (10.4%); £3,774,520.86 -> £3,382,594.73 (10.4%); £3,774,521.11 -> £3,382,594.75 (10.4%); £3,774,521.37 -> £3,382,594.78 (10.4%); £3,774,521.62 -> £3,382,594.80 (10.4%); £3,774,521.88 -> £3,382,594.83 (10.4%); £3,774,522.13 -> £3,382,595.02 (10.4%); £3,774,522.40 -> £3,382,595.20 (10.4%); £3,774,522.66 -> £3,382,595.38 (10.4%); £3,774,522.92 -> £3,382,595.56 (10.4%); £3,774,523.17 -> £3,382,595.74 (10.4%); £3,774,523.43 -> £3,382,595.92 (10.4%); £3,774,523.68 -> £3,382,596.10 (10.4%); £3,774,523.93 -> £3,382,596.28 (10.4%); £3,774,524.19 -> £3,382,596.46 (10.4%); £3,774,524.45 -> £3,382,596.64 (10.4%); £3,774,524.70 -> £3,382,596.82 (10.4%); £3,774,524.95 -> £3,382,596.85 (10.4%); £3,774,525.21 -> £3,382,596.88 (10.4%); £3,774,525.45 -> £3,382,596.90 (10.4%); £3,774,525.66 -> £3,382,596.93 (10.4%); £3,774,525.86 -> £3,382,596.95 (10.4%); £3,774,526.02 -> £3,382,596.96 (10.4%); £3,774,526.17 -> £3,382,596.98 (10.4%); £3,774,526.32 -> £3,382,597.00 (10.4%); £3,774,526.47 -> £3,382,597.02 (10.4%); £3,774,526.62 -> £3,382,597.03 (10.4%); £3,774,526.77 -> £3,382,597.05 (10.4%); £3,774,526.93 -> £3,382,597.07 (10.4%); £3,774,527.08 -> £3,382,597.08 (10.4%); £3,774,527.23 -> £3,382,597.10 (10.4%); £3,774,527.39 -> £3,382,597.12 (10.4%); £3,774,527.54 -> £3,382,597.13 (10.4%); £3,774,527.69 -> £3,382,597.29 (10.4%); £3,774,527.84 -> £3,382,597.44 (10.4%); £3,774,528.01 -> £3,382,597.59 (10.4%); £3,774,528.20 -> £3,382,597.75 (10.4%); £3,774,528.40 -> £3,382,597.91 (10.4%); £3,774,528.61 -> £3,382,598.07 (10.4%); £3,774,528.85 -> £3,382,598.22 (10.4%); £3,774,529.12 -> £3,382,598.38 (10.4%); £3,774,529.37 -> £3,382,598.40 (10.4%); £3,774,529.64 -> £3,382,598.43 (10.4%); £3,774,529.89 -> £3,382,598.45 (10.4%); £3,774,530.14 -> £3,382,598.47 (10.4%); £3,774,530.39 -> £3,382,598.50 (10.4%); £3,774,530.64 -> £3,382,598.52 (10.4%); £3,774,530.90 -> £3,382,598.54 (10.4%); £3,774,531.15 -> £3,382,598.57 (10.4%); £3,774,531.41 -> £3,382,598.59 (10.4%); £3,774,531.66 -> £3,382,598.61 (10.4%); £3,774,531.92 -> £3,382,598.64 (10.4%); £3,774,532.18 -> £3,382,598.66 (10.4%); £3,774,532.43 -> £3,382,598.69 (10.4%); £3,774,532.68 -> £3,382,598.85 (10.4%); £3,774,532.94 -> £3,382,599.02 (10.4%); £3,774,533.20 -> £3,382,599.19 (10.4%); £3,774,533.46 -> £3,382,599.36 (10.4%); £3,774,533.71 -> £3,382,599.53 (10.4%); £3,774,533.97 -> £3,382,599.70 (10.4%); £3,774,534.22 -> £3,382,599.87 (10.4%); £3,774,534.47 -> £3,382,600.04 (10.4%); £3,774,534.73 -> £3,382,600.20 (10.4%); £3,774,534.99 -> £3,382,600.37 (10.4%); £3,774,535.25 -> £3,382,600.53 (10.4%); £3,774,535.50 -> £3,382,600.56 (10.4%); £3,774,535.75 -> £3,382,600.59 (10.4%); £3,774,535.99 -> £3,382,600.61 (10.4%); £3,774,536.20 -> £3,382,600.64 (10.4%); £3,774,536.40 -> £3,382,600.66 (10.4%); £3,774,536.55 -> £3,382,600.68 (10.4%); £3,774,536.71 -> £3,382,600.69 (10.4%); £3,774,536.86 -> £3,382,600.71 (10.4%); £3,774,537.01 -> £3,382,600.73 (10.4%); £3,774,537.16 -> £3,382,600.74 (10.4%); £3,774,537.32 -> £3,382,600.76 (10.4%); £3,774,537.47 -> £3,382,600.78 (10.4%); £3,774,537.62 -> £3,382,600.79 (10.4%); £3,774,537.77 -> £3,382,600.81 (10.4%); £3,774,537.93 -> £3,382,600.83 (10.4%); £3,774,538.08 -> £3,382,600.84 (10.4%); £3,774,538.23 -> £3,382,601.00 (10.4%); £3,774,538.39 -> £3,382,601.16 (10.4%); £3,774,538.56 -> £3,382,601.32 (10.4%); £3,774,538.75 -> £3,382,601.48 (10.4%); £3,774,538.95 -> £3,382,601.64 (10.4%); £3,774,539.16 -> £3,382,601.80 (10.4%); £3,774,539.40 -> £3,382,601.96 (10.4%); £3,774,539.67 -> £3,382,602.12 (10.4%); £3,774,539.93 -> £3,382,602.15 (10.4%); £3,774,540.18 -> £3,382,602.17 (10.4%); £3,774,540.44 -> £3,382,602.19 (10.4%); £3,774,540.70 -> £3,382,602.22 (10.4%); £3,774,540.95 -> £3,382,602.24 (10.4%); £3,774,541.21 -> £3,382,602.26 (10.4%); £3,774,541.47 -> £3,382,602.29 (10.4%); £3,774,541.72 -> £3,382,602.31 (10.4%); £3,774,541.97 -> £3,382,602.34 (10.4%); £3,774,542.23 -> £3,382,602.36 (10.4%); £3,774,542.49 -> £3,382,602.38 (10.4%); £3,774,542.74 -> £3,382,602.41 (10.4%); £3,774,542.99 -> £3,382,602.44 (10.4%); £3,774,543.25 -> £3,382,602.60 (10.4%); £3,774,543.50 -> £3,382,602.77 (10.4%); £3,774,543.75 -> £3,382,602.94 (10.4%); £3,774,544.01 -> £3,382,603.11 (10.4%); £3,774,544.27 -> £3,382,603.27 (10.4%); £3,774,544.52 -> £3,382,603.44 (10.4%); £3,774,544.76 -> £3,382,603.61 (10.4%); £3,774,545.03 -> £3,382,603.77 (10.4%); £3,774,545.28 -> £3,382,603.93 (10.4%); £3,774,545.54 -> £3,382,604.10 (10.4%); £3,774,545.78 -> £3,382,604.26 (10.4%); £3,774,546.04 -> £3,382,604.29 (10.4%); £3,774,546.30 -> £3,382,604.32 (10.4%); £3,774,546.54 -> £3,382,604.34 (10.4%); £3,774,546.75 -> £3,382,604.36 (10.4%); £3,774,546.94 -> £3,382,604.38 (10.4%); £3,774,547.08 -> £3,382,604.40 (10.4%); £3,774,547.21 -> £3,382,604.42 (10.4%); £3,774,547.34 -> £3,382,604.44 (10.4%); £3,774,547.48 -> £3,382,604.46 (10.4%); £3,774,547.61 -> £3,382,604.47 (10.4%); £3,774,547.74 -> £3,382,604.49 (10.4%); £3,774,547.88 -> £3,382,604.51 (10.4%); £3,774,548.01 -> £3,382,604.52 (10.4%); £3,774,548.15 -> £3,382,604.54 (10.4%); £3,774,548.28 -> £3,382,604.56 (10.4%); £3,774,548.41 -> £3,382,604.58 (10.4%); £3,774,548.55 -> £3,382,604.71 (10.4%); £3,774,548.69 -> £3,382,604.86 (10.4%); £3,774,548.84 -> £3,382,605.01 (10.4%); £3,774,549.00 -> £3,382,605.15 (10.4%); £3,774,549.18 -> £3,382,605.31 (10.4%); £3,774,549.38 -> £3,382,605.46 (10.4%); £3,774,549.59 -> £3,382,605.61 (10.4%); £3,774,549.81 -> £3,382,605.76 (10.4%); £3,774,550.03 -> £3,382,605.79 (10.4%); £3,774,550.26 -> £3,382,605.81 (10.4%); £3,774,550.48 -> £3,382,605.84 (10.4%); £3,774,550.70 -> £3,382,605.87 (10.4%); £3,774,550.93 -> £3,382,605.89 (10.4%); £3,774,551.16 -> £3,382,605.92 (10.4%); £3,774,551.38 -> £3,382,605.95 (10.4%); £3,774,551.60 -> £3,382,605.97 (10.4%); £3,774,551.83 -> £3,382,606.00 (10.4%); £3,774,552.05 -> £3,382,606.02 (10.4%); £3,774,552.28 -> £3,382,606.05 (10.4%); £3,774,552.51 -> £3,382,606.07 (10.4%); £3,774,552.74 -> £3,382,606.10 (10.4%); £3,774,552.96 -> £3,382,606.26 (10.4%); £3,774,553.19 -> £3,382,606.42 (10.4%); £3,774,553.41 -> £3,382,606.58 (10.4%); £3,774,553.64 -> £3,382,606.74 (10.4%); £3,774,553.86 -> £3,382,606.90 (10.4%); £3,774,554.09 -> £3,382,607.06 (10.4%); £3,774,554.31 -> £3,382,607.23 (10.4%); £3,774,554.53 -> £3,382,607.39 (10.4%); £3,774,554.75 -> £3,382,607.55 (10.4%); £3,774,554.97 -> £3,382,607.71 (10.4%); £3,774,555.19 -> £3,382,607.86 (10.4%); £3,774,555.42 -> £3,382,607.89 (10.4%); £3,774,555.64 -> £3,382,607.92 (10.4%); £3,774,555.85 -> £3,382,607.94 (10.4%); £3,774,556.04 -> £3,382,607.96 (10.4%); £3,774,556.21 -> £3,382,607.99 (10.4%); £3,774,556.34 -> £3,382,608.01 (10.4%); £3,774,556.48 -> £3,382,608.02 (10.4%); £3,774,556.62 -> £3,382,608.04 (10.4%); £3,774,556.75 -> £3,382,608.06 (10.4%); £3,774,556.89 -> £3,382,608.08 (10.4%); £3,774,557.02 -> £3,382,608.10 (10.4%); £3,774,557.16 -> £3,382,608.11 (10.4%); £3,774,557.30 -> £3,382,608.13 (10.4%); £3,774,557.43 -> £3,382,608.15 (10.4%); £3,774,557.57 -> £3,382,608.16 (10.4%); £3,774,557.70 -> £3,382,608.18 (10.4%); £3,774,557.84 -> £3,382,608.32 (10.4%); £3,774,557.97 -> £3,382,608.45 (10.4%); £3,774,558.12 -> £3,382,608.59 (10.4%); £3,774,558.29 -> £3,382,608.73 (10.4%); £3,774,558.47 -> £3,382,608.87 (10.4%); £3,774,558.66 -> £3,382,609.01 (10.4%); £3,774,558.87 -> £3,382,609.16 (10.4%); £3,774,559.09 -> £3,382,609.31 (10.4%); £3,774,559.33 -> £3,382,609.34 (10.4%); £3,774,559.55 -> £3,382,609.37 (10.4%); £3,774,559.77 -> £3,382,609.40 (10.4%); £3,774,559.99 -> £3,382,609.43 (10.4%); £3,774,560.22 -> £3,382,609.46 (10.4%); £3,774,560.45 -> £3,382,609.49 (10.4%); £3,774,560.67 -> £3,382,609.52 (10.4%); £3,774,560.89 -> £3,382,609.55 (10.4%); £3,774,561.11 -> £3,382,609.58 (10.4%); £3,774,561.34 -> £3,382,609.61 (10.4%); £3,774,561.56 -> £3,382,609.64 (10.4%); £3,774,561.79 -> £3,382,609.66 (10.4%); £3,774,562.01 -> £3,382,609.70 (10.4%); £3,774,562.23 -> £3,382,609.85 (10.4%); £3,774,562.46 -> £3,382,610.01 (10.4%); £3,774,562.69 -> £3,382,610.17 (10.4%); £3,774,562.92 -> £3,382,610.32 (10.4%); £3,774,563.13 -> £3,382,610.47 (10.4%); £3,774,563.34 -> £3,382,610.63 (10.4%); £3,774,563.57 -> £3,382,610.78 (10.4%); £3,774,563.78 -> £3,382,610.93 (10.4%); £3,774,564.01 -> £3,382,611.08 (10.4%); £3,774,564.23 -> £3,382,611.23 (10.4%); £3,774,564.46 -> £3,382,611.38 (10.4%); £3,774,564.68 -> £3,382,611.41 (10.4%); £3,774,564.90 -> £3,382,611.44 (10.4%); £3,774,565.12 -> £3,382,611.46 (10.4%); £3,774,565.31 -> £3,382,611.48 (10.4%); £3,774,565.48 -> £3,382,611.50 (10.4%); £3,774,565.63 -> £3,382,611.52 (10.4%); £3,774,565.79 -> £3,382,611.54 (10.4%); £3,774,565.94 -> £3,382,611.56 (10.4%); £3,774,566.09 -> £3,382,611.57 (10.4%); £3,774,566.25 -> £3,382,611.59 (10.4%); £3,774,566.40 -> £3,382,611.61 (10.4%); £3,774,566.55 -> £3,382,611.62 (10.4%); £3,774,566.70 -> £3,382,611.64 (10.4%); £3,774,566.86 -> £3,382,611.66 (10.4%); £3,774,567.01 -> £3,382,611.67 (10.4%); £3,774,567.15 -> £3,382,611.69 (10.4%); £3,774,567.30 -> £3,382,611.83 (10.4%); £3,774,567.45 -> £3,382,611.98 (10.4%); £3,774,567.62 -> £3,382,612.13 (10.4%); £3,774,567.81 -> £3,382,612.27 (10.4%); £3,774,568.02 -> £3,382,612.42 (10.4%); £3,774,568.24 -> £3,382,612.57 (10.4%); £3,774,568.48 -> £3,382,612.71 (10.4%); £3,774,568.72 -> £3,382,612.85 (10.4%); £3,774,568.98 -> £3,382,612.88 (10.4%); £3,774,569.23 -> £3,382,612.90 (10.4%); £3,774,569.49 -> £3,382,612.92 (10.4%); £3,774,569.74 -> £3,382,612.95 (10.4%); £3,774,569.99 -> £3,382,612.97 (10.4%); £3,774,570.25 -> £3,382,613.00 (10.4%); £3,774,570.50 -> £3,382,613.02 (10.4%); £3,774,570.74 -> £3,382,613.04 (10.4%); £3,774,570.99 -> £3,382,613.07 (10.4%); £3,774,571.26 -> £3,382,613.09 (10.4%); £3,774,571.51 -> £3,382,613.11 (10.4%); £3,774,571.76 -> £3,382,613.14 (10.4%); £3,774,572.01 -> £3,382,613.16 (10.4%); £3,774,572.27 -> £3,382,613.31 (10.4%); £3,774,572.52 -> £3,382,613.46 (10.4%); £3,774,572.78 -> £3,382,613.61 (10.4%); £3,774,573.04 -> £3,382,613.76 (10.4%); £3,774,573.29 -> £3,382,613.91 (10.4%); £3,774,573.54 -> £3,382,614.07 (10.4%); £3,774,573.79 -> £3,382,614.23 (10.4%); £3,774,574.04 -> £3,382,614.39 (10.4%); £3,774,574.29 -> £3,382,614.55 (10.4%); £3,774,574.54 -> £3,382,614.70 (10.4%); £3,774,574.81 -> £3,382,614.85 (10.4%); £3,774,575.06 -> £3,382,614.88 (10.4%); £3,774,575.31 -> £3,382,614.91 (10.4%); £3,774,575.54 -> £3,382,614.93 (10.4%); £3,774,575.76 -> £3,382,614.95 (10.4%); £3,774,575.95 -> £3,382,614.97 (10.4%); £3,774,576.10 -> £3,382,614.99 (10.4%); £3,774,576.25 -> £3,382,615.01 (10.4%); £3,774,576.39 -> £3,382,615.03 (10.4%); £3,774,576.54 -> £3,382,615.04 (10.4%); £3,774,576.70 -> £3,382,615.06 (10.4%); £3,774,576.85 -> £3,382,615.08 (10.4%); £3,774,577.00 -> £3,382,615.09 (10.4%); £3,774,577.15 -> £3,382,615.11 (10.4%); £3,774,577.30 -> £3,382,615.13 (10.4%); £3,774,577.45 -> £3,382,615.14 (10.4%); £3,774,577.59 -> £3,382,615.16 (10.4%); £3,774,577.74 -> £3,382,615.27 (10.4%); £3,774,577.90 -> £3,382,615.38 (10.4%); £3,774,578.07 -> £3,382,615.49 (10.4%); £3,774,578.25 -> £3,382,615.61 (10.4%); £3,774,578.46 -> £3,382,615.73 (10.4%); £3,774,578.67 -> £3,382,615.85 (10.4%); £3,774,578.90 -> £3,382,615.96 (10.4%); £3,774,579.16 -> £3,382,616.07 (10.4%); £3,774,579.41 -> £3,382,616.10 (10.4%); £3,774,579.66 -> £3,382,616.12 (10.4%); £3,774,579.91 -> £3,382,616.15 (10.4%); £3,774,580.17 -> £3,382,616.17 (10.4%); £3,774,580.42 -> £3,382,616.19 (10.4%); £3,774,580.67 -> £3,382,616.22 (10.4%); £3,774,580.91 -> £3,382,616.24 (10.4%); £3,774,581.17 -> £3,382,616.27 (10.4%); £3,774,581.42 -> £3,382,616.29 (10.4%); £3,774,581.67 -> £3,382,616.31 (10.4%); £3,774,581.92 -> £3,382,616.34 (10.4%); £3,774,582.18 -> £3,382,616.36 (10.4%); £3,774,582.44 -> £3,382,616.39 (10.4%); £3,774,582.69 -> £3,382,616.51 (10.4%); £3,774,582.95 -> £3,382,616.64 (10.4%); £3,774,583.20 -> £3,382,616.76 (10.4%); £3,774,583.46 -> £3,382,616.89 (10.4%); £3,774,583.72 -> £3,382,617.02 (10.4%); £3,774,583.97 -> £3,382,617.15 (10.4%); £3,774,584.23 -> £3,382,617.27 (10.4%); £3,774,584.48 -> £3,382,617.40 (10.4%); £3,774,584.72 -> £3,382,617.52 (10.4%); £3,774,584.96 -> £3,382,617.64 (10.4%); £3,774,585.21 -> £3,382,617.76 (10.4%); £3,774,585.46 -> £3,382,617.79 (10.4%); £3,774,585.71 -> £3,382,617.81 (10.4%); £3,774,585.95 -> £3,382,617.84 (10.4%); £3,774,586.16 -> £3,382,617.86 (10.4%); £3,774,586.35 -> £3,382,617.88 (10.4%); £3,774,586.51 -> £3,382,617.90 (10.4%); £3,774,586.66 -> £3,382,617.92 (10.4%); £3,774,586.81 -> £3,382,617.93 (10.4%); £3,774,586.96 -> £3,382,617.95 (10.4%); £3,774,587.11 -> £3,382,617.97 (10.4%); £3,774,587.27 -> £3,382,617.99 (10.4%); £3,774,587.42 -> £3,382,618.00 (10.4%); £3,774,587.57 -> £3,382,618.02 (10.4%); £3,774,587.72 -> £3,382,618.03 (10.4%); £3,774,587.87 -> £3,382,618.05 (10.4%); £3,774,588.02 -> £3,382,618.07 (10.4%); £3,774,588.18 -> £3,382,618.14 (10.4%); £3,774,588.32 -> £3,382,618.22 (10.4%); £3,774,588.49 -> £3,382,618.31 (10.4%); £3,774,588.67 -> £3,382,618.39 (10.4%); £3,774,588.87 -> £3,382,618.48 (10.4%); £3,774,589.09 -> £3,382,618.57 (10.4%); £3,774,589.33 -> £3,382,618.65 (10.4%); £3,774,589.58 -> £3,382,618.74 (10.4%); £3,774,589.82 -> £3,382,618.76 (10.4%); £3,774,590.08 -> £3,382,618.79 (10.4%); £3,774,590.33 -> £3,382,618.81 (10.4%); £3,774,590.59 -> £3,382,618.83 (10.4%); £3,774,590.84 -> £3,382,618.86 (10.4%); £3,774,591.08 -> £3,382,618.88 (10.4%); £3,774,591.34 -> £3,382,618.91 (10.4%); £3,774,591.60 -> £3,382,618.93 (10.4%); £3,774,591.85 -> £3,382,618.95 (10.4%); £3,774,592.09 -> £3,382,618.98 (10.4%); £3,774,592.34 -> £3,382,619.00 (10.4%); £3,774,592.58 -> £3,382,619.03 (10.4%); £3,774,592.83 -> £3,382,619.06 (10.4%); £3,774,593.08 -> £3,382,619.15 (10.4%); £3,774,593.33 -> £3,382,619.25 (10.4%); £3,774,593.58 -> £3,382,619.35 (10.4%); £3,774,593.83 -> £3,382,619.45 (10.4%); £3,774,594.07 -> £3,382,619.55 (10.4%); £3,774,594.32 -> £3,382,619.65 (10.4%); £3,774,594.57 -> £3,382,619.74 (10.4%); £3,774,594.83 -> £3,382,619.84 (10.4%); £3,774,595.07 -> £3,382,619.94 (10.4%); £3,774,595.31 -> £3,382,620.03 (10.4%); £3,774,595.56 -> £3,382,620.12 (10.4%); £3,774,595.81 -> £3,382,620.15 (10.4%); £3,774,596.07 -> £3,382,620.18 (10.4%); £3,774,596.31 -> £3,382,620.21 (10.4%); £3,774,596.51 -> £3,382,620.23 (10.4%); £3,774,596.71 -> £3,382,620.25 (10.4%); £3,774,596.86 -> £3,382,620.27 (10.4%); £3,774,597.01 -> £3,382,620.28 (10.4%); £3,774,597.16 -> £3,382,620.30 (10.4%); £3,774,597.32 -> £3,382,620.32 (10.4%); £3,774,597.47 -> £3,382,620.34 (10.4%); £3,774,597.62 -> £3,382,620.35 (10.4%); £3,774,597.77 -> £3,382,620.37 (10.4%); £3,774,597.92 -> £3,382,620.39 (10.4%); £3,774,598.07 -> £3,382,620.40 (10.4%); £3,774,598.22 -> £3,382,620.42 (10.4%); £3,774,598.38 -> £3,382,620.44 (10.4%); £3,774,598.52 -> £3,382,620.51 (10.4%); £3,774,598.67 -> £3,382,620.59 (10.4%); £3,774,598.84 -> £3,382,620.67 (10.4%); £3,774,599.02 -> £3,382,620.75 (10.4%); £3,774,599.22 -> £3,382,620.84 (10.4%); £3,774,599.44 -> £3,382,620.92 (10.4%); £3,774,599.67 -> £3,382,621.00 (10.4%); £3,774,599.92 -> £3,382,621.09 (10.4%); £3,774,600.17 -> £3,382,621.11 (10.4%); £3,774,600.42 -> £3,382,621.13 (10.4%); £3,774,600.68 -> £3,382,621.16 (10.4%); £3,774,600.93 -> £3,382,621.18 (10.4%); £3,774,601.18 -> £3,382,621.20 (10.4%); £3,774,601.44 -> £3,382,621.23 (10.4%); £3,774,601.69 -> £3,382,621.25 (10.4%); £3,774,601.94 -> £3,382,621.28 (10.4%); £3,774,602.19 -> £3,382,621.30 (10.4%); £3,774,602.44 -> £3,382,621.32 (10.4%); £3,774,602.69 -> £3,382,621.35 (10.4%); £3,774,602.95 -> £3,382,621.37 (10.4%); £3,774,603.20 -> £3,382,621.40 (10.4%); £3,774,603.46 -> £3,382,621.49 (10.4%); £3,774,603.72 -> £3,382,621.58 (10.4%); £3,774,603.97 -> £3,382,621.68 (10.4%); £3,774,604.23 -> £3,382,621.78 (10.4%); £3,774,604.49 -> £3,382,621.88 (10.4%); £3,774,604.73 -> £3,382,621.97 (10.4%); £3,774,604.98 -> £3,382,622.07 (10.4%); £3,774,605.24 -> £3,382,622.16 (10.4%); £3,774,605.49 -> £3,382,622.26 (10.4%); £3,774,605.74 -> £3,382,622.35 (10.4%); £3,774,605.98 -> £3,382,622.44 (10.4%); £3,774,606.24 -> £3,382,622.47 (10.4%); £3,774,606.50 -> £3,382,622.50 (10.4%); £3,774,606.72 -> £3,382,622.52 (10.4%); £3,774,606.94 -> £3,382,622.55 (10.4%); £3,774,607.14 -> £3,382,622.57 (10.4%); £3,774,607.28 -> £3,382,622.58 (10.4%); £3,774,607.44 -> £3,382,622.60 (10.4%); £3,774,607.59 -> £3,382,622.62 (10.4%); £3,774,607.74 -> £3,382,622.64 (10.4%); £3,774,607.89 -> £3,382,622.65 (10.4%); £3,774,608.04 -> £3,382,622.67 (10.4%); £3,774,608.20 -> £3,382,622.69 (10.4%); £3,774,608.35 -> £3,382,622.70 (10.4%); £3,774,608.50 -> £3,382,622.72 (10.4%); £3,774,608.65 -> £3,382,622.74 (10.4%); £3,774,608.80 -> £3,382,622.76 (10.4%); £3,774,608.95 -> £3,382,622.86 (10.4%); £3,774,609.10 -> £3,382,622.97 (10.4%); £3,774,609.27 -> £3,382,623.09 (10.4%); £3,774,609.45 -> £3,382,623.21 (10.4%); £3,774,609.66 -> £3,382,623.33 (10.4%); £3,774,609.87 -> £3,382,623.44 (10.4%); £3,774,610.11 -> £3,382,623.55 (10.4%); £3,774,610.36 -> £3,382,623.66 (10.4%); £3,774,610.62 -> £3,382,623.68 (10.4%); £3,774,610.87 -> £3,382,623.71 (10.4%); £3,774,611.11 -> £3,382,623.73 (10.4%); £3,774,611.37 -> £3,382,623.76 (10.4%); £3,774,611.61 -> £3,382,623.78 (10.4%); £3,774,611.87 -> £3,382,623.81 (10.4%); £3,774,612.12 -> £3,382,623.83 (10.4%); £3,774,612.37 -> £3,382,623.86 (10.4%); £3,774,612.63 -> £3,382,623.88 (10.4%); £3,774,612.88 -> £3,382,623.90 (10.4%); £3,774,613.13 -> £3,382,623.93 (10.4%); £3,774,613.38 -> £3,382,623.95 (10.4%); £3,774,613.63 -> £3,382,623.98 (10.4%); £3,774,613.88 -> £3,382,624.10 (10.4%); £3,774,614.14 -> £3,382,624.22 (10.4%); £3,774,614.39 -> £3,382,624.34 (10.4%); £3,774,614.64 -> £3,382,624.47 (10.4%); £3,774,614.89 -> £3,382,624.59 (10.4%); £3,774,615.14 -> £3,382,624.71 (10.4%); £3,774,615.39 -> £3,382,624.83 (10.4%); £3,774,615.64 -> £3,382,624.95 (10.4%); £3,774,615.90 -> £3,382,625.06 (10.4%); £3,774,616.15 -> £3,382,625.18 (10.4%); £3,774,616.40 -> £3,382,625.30 (10.4%); £3,774,616.66 -> £3,382,625.33 (10.4%); £3,774,616.91 -> £3,382,625.35 (10.4%); £3,774,617.14 -> £3,382,625.38 (10.4%); £3,774,617.35 -> £3,382,625.40 (10.4%); £3,774,617.54 -> £3,382,625.42 (10.4%); £3,774,617.67 -> £3,382,625.44 (10.4%); £3,774,617.81 -> £3,382,625.46 (10.4%); £3,774,617.94 -> £3,382,625.48 (10.4%); £3,774,618.08 -> £3,382,625.50 (10.4%); £3,774,618.22 -> £3,382,625.51 (10.4%); £3,774,618.35 -> £3,382,625.53 (10.4%); £3,774,618.49 -> £3,382,625.55 (10.4%); £3,774,618.62 -> £3,382,625.56 (10.4%); £3,774,618.76 -> £3,382,625.58 (10.4%); £3,774,618.89 -> £3,382,625.60 (10.4%); £3,774,619.03 -> £3,382,625.61 (10.4%); £3,774,619.16 -> £3,382,625.75 (10.4%); £3,774,619.30 -> £3,382,625.90 (10.4%); £3,774,619.45 -> £3,382,626.04 (10.4%); £3,774,619.62 -> £3,382,626.19 (10.4%); £3,774,619.80 -> £3,382,626.34 (10.4%); £3,774,620.00 -> £3,382,626.49 (10.4%); £3,774,620.21 -> £3,382,626.65 (10.4%); £3,774,620.43 -> £3,382,626.80 (10.4%); £3,774,620.65 -> £3,382,626.83 (10.4%); £3,774,620.87 -> £3,382,626.85 (10.4%); £3,774,621.10 -> £3,382,626.88 (10.4%); £3,774,621.33 -> £3,382,626.90 (10.4%); £3,774,621.55 -> £3,382,626.93 (10.4%); £3,774,621.77 -> £3,382,626.96 (10.4%); £3,774,622.00 -> £3,382,626.99 (10.4%); £3,774,622.23 -> £3,382,627.01 (10.4%); £3,774,622.44 -> £3,382,627.04 (10.4%); £3,774,622.65 -> £3,382,627.06 (10.4%); £3,774,622.88 -> £3,382,627.09 (10.4%); £3,774,623.09 -> £3,382,627.11 (10.4%); £3,774,623.31 -> £3,382,627.14 (10.4%); £3,774,623.54 -> £3,382,627.29 (10.4%); £3,774,623.76 -> £3,382,627.44 (10.4%); £3,774,623.99 -> £3,382,627.60 (10.4%); £3,774,624.22 -> £3,382,627.76 (10.4%); £3,774,624.44 -> £3,382,627.91 (10.4%); £3,774,624.67 -> £3,382,628.07 (10.4%); £3,774,624.89 -> £3,382,628.22 (10.4%); £3,774,625.11 -> £3,382,628.38 (10.4%); £3,774,625.34 -> £3,382,628.53 (10.4%); £3,774,625.56 -> £3,382,628.69 (10.4%); £3,774,625.78 -> £3,382,628.85 (10.4%); £3,774,626.00 -> £3,382,628.88 (10.4%); £3,774,626.23 -> £3,382,628.90 (10.4%); £3,774,626.43 -> £3,382,628.93 (10.4%); £3,774,626.62 -> £3,382,628.95 (10.4%); £3,774,626.80 -> £3,382,628.97 (10.4%); £3,774,626.93 -> £3,382,628.99 (10.4%); £3,774,627.06 -> £3,382,629.01 (10.4%); £3,774,627.20 -> £3,382,629.03 (10.4%); £3,774,627.33 -> £3,382,629.05 (10.4%); £3,774,627.47 -> £3,382,629.07 (10.4%); £3,774,627.60 -> £3,382,629.08 (10.4%); £3,774,627.73 -> £3,382,629.10 (10.4%); £3,774,627.87 -> £3,382,629.12 (10.4%); £3,774,628.01 -> £3,382,629.13 (10.4%); £3,774,628.15 -> £3,382,629.15 (10.4%); £3,774,628.29 -> £3,382,629.17 (10.4%); £3,774,628.42 -> £3,382,629.24 (10.4%); £3,774,628.56 -> £3,382,629.32 (10.4%); £3,774,628.70 -> £3,382,629.39 (10.4%); £3,774,628.87 -> £3,382,629.47 (10.4%); £3,774,629.05 -> £3,382,629.55 (10.4%); £3,774,629.25 -> £3,382,629.64 (10.4%); £3,774,629.46 -> £3,382,629.72 (10.4%); £3,774,629.69 -> £3,382,629.81 (10.4%); £3,774,629.92 -> £3,382,629.84 (10.4%); £3,774,630.15 -> £3,382,629.87 (10.4%); £3,774,630.37 -> £3,382,629.90 (10.4%); £3,774,630.59 -> £3,382,629.93 (10.4%); £3,774,630.82 -> £3,382,629.96 (10.4%); £3,774,631.05 -> £3,382,629.99 (10.4%); £3,774,631.28 -> £3,382,630.02 (10.4%); £3,774,631.50 -> £3,382,630.05 (10.4%); £3,774,631.73 -> £3,382,630.08 (10.4%); £3,774,631.96 -> £3,382,630.11 (10.4%); £3,774,632.19 -> £3,382,630.14 (10.4%); £3,774,632.42 -> £3,382,630.17 (10.4%); £3,774,632.64 -> £3,382,630.20 (10.4%); £3,774,632.87 -> £3,382,630.29 (10.4%); £3,774,633.09 -> £3,382,630.39 (10.4%); £3,774,633.32 -> £3,382,630.49 (10.4%); £3,774,633.55 -> £3,382,630.59 (10.4%); £3,774,633.77 -> £3,382,630.69 (10.4%); £3,774,634.00 -> £3,382,630.79 (10.4%); £3,774,634.22 -> £3,382,630.89 (10.4%); £3,774,634.45 -> £3,382,630.99 (10.4%); £3,774,634.67 -> £3,382,631.08 (10.4%); £3,774,634.89 -> £3,382,631.17 (10.4%); £3,774,635.12 -> £3,382,631.27 (10.4%); £3,774,635.35 -> £3,382,631.30 (10.4%); £3,774,635.57 -> £3,382,631.33 (10.4%); £3,774,635.79 -> £3,382,631.35 (10.4%); £3,774,635.98 -> £3,382,631.37 (10.4%); £3,774,636.16 -> £3,382,631.39 (10.4%); £3,774,636.32 -> £3,382,631.41 (10.4%); £3,774,636.47 -> £3,382,631.43 (10.4%); £3,774,636.62 -> £3,382,631.45 (10.4%); £3,774,636.78 -> £3,382,631.46 (10.4%); £3,774,636.93 -> £3,382,631.48 (10.4%); £3,774,637.08 -> £3,382,631.50 (10.4%); £3,774,637.23 -> £3,382,631.51 (10.4%); £3,774,637.39 -> £3,382,631.53 (10.4%); £3,774,637.54 -> £3,382,631.55 (10.4%); £3,774,637.69 -> £3,382,631.56 (10.4%); £3,774,637.85 -> £3,382,631.58 (10.4%); £3,774,638.00 -> £3,382,631.68 (10.4%); £3,774,638.16 -> £3,382,631.78 (10.4%); £3,774,638.33 -> £3,382,631.88 (10.4%); £3,774,638.52 -> £3,382,631.98 (10.4%); £3,774,638.72 -> £3,382,632.10 (10.4%); £3,774,638.94 -> £3,382,632.20 (10.4%); £3,774,639.19 -> £3,382,632.31 (10.4%); £3,774,639.45 -> £3,382,632.42 (10.4%); £3,774,639.70 -> £3,382,632.44 (10.4%); £3,774,639.95 -> £3,382,632.47 (10.4%); £3,774,640.21 -> £3,382,632.49 (10.4%); £3,774,640.46 -> £3,382,632.51 (10.4%); £3,774,640.70 -> £3,382,632.54 (10.4%); £3,774,640.96 -> £3,382,632.56 (10.4%); £3,774,641.21 -> £3,382,632.59 (10.4%); £3,774,641.47 -> £3,382,632.61 (10.4%); £3,774,641.74 -> £3,382,632.63 (10.4%); £3,774,641.99 -> £3,382,632.66 (10.4%); £3,774,642.25 -> £3,382,632.68 (10.4%); £3,774,642.51 -> £3,382,632.71 (10.4%); £3,774,642.77 -> £3,382,632.74 (10.4%); £3,774,643.03 -> £3,382,632.85 (10.4%); £3,774,643.28 -> £3,382,632.97 (10.4%); £3,774,643.54 -> £3,382,633.10 (10.4%); £3,774,643.79 -> £3,382,633.22 (10.4%); £3,774,644.05 -> £3,382,633.34 (10.4%); £3,774,644.32 -> £3,382,633.46 (10.4%); £3,774,644.57 -> £3,382,633.57 (10.4%); £3,774,644.82 -> £3,382,633.69 (10.4%); £3,774,645.08 -> £3,382,633.81 (10.4%); £3,774,645.33 -> £3,382,633.93 (10.4%); £3,774,645.59 -> £3,382,634.04 (10.4%); £3,774,645.85 -> £3,382,634.07 (10.4%); £3,774,646.11 -> £3,382,634.10 (10.4%); £3,774,646.34 -> £3,382,634.12 (10.4%); £3,774,646.56 -> £3,382,634.15 (10.4%); £3,774,646.75 -> £3,382,634.17 (10.4%); £3,774,646.91 -> £3,382,634.18 (10.4%); £3,774,647.07 -> £3,382,634.20 (10.4%); £3,774,647.22 -> £3,382,634.22 (10.4%); £3,774,647.37 -> £3,382,634.24 (10.4%); £3,774,647.53 -> £3,382,634.25 (10.4%); £3,774,647.68 -> £3,382,634.27 (10.4%); £3,774,647.84 -> £3,382,634.29 (10.4%); £3,774,647.99 -> £3,382,634.30 (10.4%); £3,774,648.15 -> £3,382,634.32 (10.4%); £3,774,648.30 -> £3,382,634.34 (10.4%); £3,774,648.46 -> £3,382,634.35 (10.4%); £3,774,648.61 -> £3,382,634.43 (10.4%); £3,774,648.77 -> £3,382,634.52 (10.4%); £3,774,648.94 -> £3,382,634.61 (10.4%); £3,774,649.14 -> £3,382,634.70 (10.4%); £3,774,649.34 -> £3,382,634.79 (10.4%); £3,774,649.57 -> £3,382,634.89 (10.4%); £3,774,649.81 -> £3,382,634.98 (10.4%); £3,774,650.07 -> £3,382,635.07 (10.4%); £3,774,650.32 -> £3,382,635.09 (10.4%); £3,774,650.57 -> £3,382,635.12 (10.4%); £3,774,650.83 -> £3,382,635.14 (10.4%); £3,774,651.09 -> £3,382,635.17 (10.4%); £3,774,651.34 -> £3,382,635.19 (10.4%); £3,774,651.60 -> £3,382,635.21 (10.4%); £3,774,651.87 -> £3,382,635.24 (10.4%); £3,774,652.13 -> £3,382,635.26 (10.4%); £3,774,652.40 -> £3,382,635.28 (10.4%); £3,774,652.65 -> £3,382,635.31 (10.4%); £3,774,652.91 -> £3,382,635.33 (10.4%); £3,774,653.18 -> £3,382,635.36 (10.4%); £3,774,653.43 -> £3,382,635.38 (10.4%); £3,774,653.68 -> £3,382,635.48 (10.4%); £3,774,653.94 -> £3,382,635.58 (10.4%); £3,774,654.20 -> £3,382,635.68 (10.4%); £3,774,654.45 -> £3,382,635.78 (10.4%); £3,774,654.71 -> £3,382,635.88 (10.4%); £3,774,654.97 -> £3,382,635.98 (10.4%); £3,774,655.23 -> £3,382,636.08 (10.4%); £3,774,655.49 -> £3,382,636.19 (10.4%); £3,774,655.74 -> £3,382,636.29 (10.4%); £3,774,656.00 -> £3,382,636.38 (10.4%); £3,774,656.25 -> £3,382,636.48 (10.4%); £3,774,656.51 -> £3,382,636.51 (10.4%); £3,774,656.77 -> £3,382,636.53 (10.4%); £3,774,657.01 -> £3,382,636.56 (10.4%); £3,774,657.23 -> £3,382,636.58 (10.4%); £3,774,657.42 -> £3,382,636.60 (10.4%); £3,774,657.57 -> £3,382,636.62 (10.4%); £3,774,657.73 -> £3,382,636.64 (10.4%); £3,774,657.88 -> £3,382,636.65 (10.4%); £3,774,658.04 -> £3,382,636.67 (10.4%); £3,774,658.19 -> £3,382,636.69 (10.4%); £3,774,658.34 -> £3,382,636.70 (10.4%); £3,774,658.50 -> £3,382,636.72 (10.4%); £3,774,658.65 -> £3,382,636.74 (10.4%); £3,774,658.81 -> £3,382,636.75 (10.4%); £3,774,658.96 -> £3,382,636.77 (10.4%); £3,774,659.13 -> £3,382,636.79 (10.4%); £3,774,659.28 -> £3,382,636.89 (10.4%); £3,774,659.44 -> £3,382,636.99 (10.4%); £3,774,659.61 -> £3,382,637.10 (10.4%); £3,774,659.79 -> £3,382,637.21 (10.4%); £3,774,660.00 -> £3,382,637.32 (10.4%); £3,774,660.23 -> £3,382,637.42 (10.4%); £3,774,660.48 -> £3,382,637.53 (10.4%); £3,774,660.74 -> £3,382,637.64 (10.4%); £3,774,660.99 -> £3,382,637.66 (10.4%); £3,774,661.25 -> £3,382,637.68 (10.4%); £3,774,661.50 -> £3,382,637.71 (10.4%); £3,774,661.76 -> £3,382,637.73 (10.4%); £3,774,662.02 -> £3,382,637.76 (10.4%); £3,774,662.27 -> £3,382,637.78 (10.4%); £3,774,662.53 -> £3,382,637.80 (10.4%); £3,774,662.78 -> £3,382,637.83 (10.4%); £3,774,663.03 -> £3,382,637.85 (10.4%); £3,774,663.29 -> £3,382,637.87 (10.4%); £3,774,663.55 -> £3,382,637.90 (10.4%); £3,774,663.80 -> £3,382,637.92 (10.4%); £3,774,664.06 -> £3,382,637.95 (10.4%); £3,774,664.32 -> £3,382,638.07 (10.4%); £3,774,664.58 -> £3,382,638.19 (10.4%); £3,774,664.84 -> £3,382,638.31 (10.4%); £3,774,665.09 -> £3,382,638.42 (10.4%); £3,774,665.35 -> £3,382,638.53 (10.4%); £3,774,665.61 -> £3,382,638.65 (10.4%); £3,774,665.87 -> £3,382,638.77 (10.4%); £3,774,666.13 -> £3,382,638.88 (10.4%); £3,774,666.38 -> £3,382,639.00 (10.4%); £3,774,666.64 -> £3,382,639.12 (10.4%); £3,774,666.89 -> £3,382,639.24 (10.4%); £3,774,667.14 -> £3,382,639.27 (10.4%); £3,774,667.40 -> £3,382,639.29 (10.4%); £3,774,667.64 -> £3,382,639.32 (10.4%); £3,774,667.87 -> £3,382,639.34 (10.4%); £3,774,668.07 -> £3,382,639.36 (10.4%); £3,774,668.23 -> £3,382,639.38 (10.4%); £3,774,668.38 -> £3,382,639.40 (10.4%); £3,774,668.53 -> £3,382,639.41 (10.4%); £3,774,668.68 -> £3,382,639.43 (10.4%); £3,774,668.84 -> £3,382,639.45 (10.4%); £3,774,668.99 -> £3,382,639.46 (10.4%); £3,774,669.14 -> £3,382,639.48 (10.4%); £3,774,669.29 -> £3,382,639.50 (10.4%); £3,774,669.44 -> £3,382,639.51 (10.4%); £3,774,669.59 -> £3,382,639.53 (10.4%); £3,774,669.74 -> £3,382,639.55 (10.4%); £3,774,669.90 -> £3,382,639.66 (10.4%); £3,774,670.05 -> £3,382,639.78 (10.4%); £3,774,670.23 -> £3,382,639.90 (10.4%); £3,774,670.41 -> £3,382,640.02 (10.4%); £3,774,670.61 -> £3,382,640.15 (10.4%); £3,774,670.84 -> £3,382,640.27 (10.4%); £3,774,671.08 -> £3,382,640.39 (10.4%); £3,774,671.33 -> £3,382,640.51 (10.4%); £3,774,671.59 -> £3,382,640.53 (10.4%); £3,774,671.85 -> £3,382,640.56 (10.4%); £3,774,672.10 -> £3,382,640.58 (10.4%); £3,774,672.35 -> £3,382,640.61 (10.4%); £3,774,672.62 -> £3,382,640.63 (10.4%); £3,774,672.87 -> £3,382,640.66 (10.4%); £3,774,673.13 -> £3,382,640.68 (10.4%); £3,774,673.38 -> £3,382,640.70 (10.4%); £3,774,673.63 -> £3,382,640.73 (10.4%); £3,774,673.89 -> £3,382,640.75 (10.4%); £3,774,674.15 -> £3,382,640.77 (10.4%); £3,774,674.40 -> £3,382,640.80 (10.4%); £3,774,674.66 -> £3,382,640.83 (10.4%); £3,774,674.91 -> £3,382,640.96 (10.4%); £3,774,675.16 -> £3,382,641.09 (10.4%); £3,774,675.42 -> £3,382,641.23 (10.4%); £3,774,675.68 -> £3,382,641.36 (10.4%); £3,774,675.94 -> £3,382,641.50 (10.4%); £3,774,676.19 -> £3,382,641.64 (10.4%); £3,774,676.45 -> £3,382,641.77 (10.4%); £3,774,676.71 -> £3,382,641.90 (10.4%); £3,774,676.96 -> £3,382,642.03 (10.4%); £3,774,677.21 -> £3,382,642.17 (10.4%); £3,774,677.46 -> £3,382,642.30 (10.4%); £3,774,677.72 -> £3,382,642.32 (10.4%); £3,774,677.97 -> £3,382,642.35 (10.4%); £3,774,678.21 -> £3,382,642.38 (10.4%); £3,774,678.43 -> £3,382,642.40 (10.4%); £3,774,678.63 -> £3,382,642.42 (10.4%); £3,774,678.79 -> £3,382,642.44 (10.4%); £3,774,678.94 -> £3,382,642.46 (10.4%); £3,774,679.09 -> £3,382,642.48 (10.4%); £3,774,679.24 -> £3,382,642.49 (10.4%); £3,774,679.39 -> £3,382,642.51 (10.4%); £3,774,679.55 -> £3,382,642.53 (10.4%); £3,774,679.70 -> £3,382,642.54 (10.4%); £3,774,679.85 -> £3,382,642.56 (10.4%); £3,774,680.00 -> £3,382,642.58 (10.4%); £3,774,680.15 -> £3,382,642.59 (10.4%); £3,774,680.30 -> £3,382,642.61 (10.4%); £3,774,680.46 -> £3,382,642.73 (10.4%); £3,774,680.61 -> £3,382,642.85 (10.4%); £3,774,680.78 -> £3,382,642.98 (10.4%); £3,774,680.97 -> £3,382,643.11 (10.4%); £3,774,681.19 -> £3,382,643.24 (10.4%); £3,774,681.40 -> £3,382,643.37 (10.4%); £3,774,681.65 -> £3,382,643.50 (10.4%); £3,774,681.91 -> £3,382,643.62 (10.4%); £3,774,682.17 -> £3,382,643.65 (10.4%); £3,774,682.43 -> £3,382,643.67 (10.4%); £3,774,682.69 -> £3,382,643.70 (10.4%); £3,774,682.95 -> £3,382,643.72 (10.4%); £3,774,683.21 -> £3,382,643.74 (10.4%); £3,774,683.46 -> £3,382,643.77 (10.4%); £3,774,683.72 -> £3,382,643.79 (10.4%); £3,774,683.98 -> £3,382,643.82 (10.4%); £3,774,684.23 -> £3,382,643.84 (10.4%); £3,774,684.49 -> £3,382,643.86 (10.4%); £3,774,684.75 -> £3,382,643.89 (10.4%); £3,774,685.01 -> £3,382,643.92 (10.4%); £3,774,685.26 -> £3,382,643.94 (10.4%); £3,774,685.52 -> £3,382,644.08 (10.4%); £3,774,685.78 -> £3,382,644.22 (10.4%); £3,774,686.04 -> £3,382,644.35 (10.4%); £3,774,686.30 -> £3,382,644.49 (10.4%); £3,774,686.55 -> £3,382,644.63 (10.4%); £3,774,686.81 -> £3,382,644.76 (10.4%); £3,774,687.07 -> £3,382,644.90 (10.4%); £3,774,687.33 -> £3,382,645.03 (10.4%); £3,774,687.59 -> £3,382,645.17 (10.4%); £3,774,687.84 -> £3,382,645.30 (10.4%); £3,774,688.10 -> £3,382,645.44 (10.4%); £3,774,688.36 -> £3,382,645.47 (10.4%); £3,774,688.62 -> £3,382,645.49 (10.4%); £3,774,688.86 -> £3,382,645.52 (10.4%); £3,774,689.08 -> £3,382,645.54 (10.4%); £3,774,689.28 -> £3,382,645.56 (10.4%); £3,774,689.42 -> £3,382,645.58 (10.4%); £3,774,689.55 -> £3,382,645.60 (10.4%); £3,774,689.69 -> £3,382,645.62 (10.4%); £3,774,689.83 -> £3,382,645.64 (10.4%); £3,774,689.96 -> £3,382,645.66 (10.4%); £3,774,690.10 -> £3,382,645.67 (10.4%); £3,774,690.23 -> £3,382,645.69 (10.4%); £3,774,690.37 -> £3,382,645.71 (10.4%); £3,774,690.51 -> £3,382,645.72 (10.4%); £3,774,690.64 -> £3,382,645.74 (10.4%); £3,774,690.78 -> £3,382,645.76 (10.4%); £3,774,690.91 -> £3,382,645.92 (10.4%); £3,774,691.04 -> £3,382,646.09 (10.4%); £3,774,691.20 -> £3,382,646.27 (10.4%); £3,774,691.36 -> £3,382,646.44 (10.4%); £3,774,691.55 -> £3,382,646.63 (10.4%); £3,774,691.74 -> £3,382,646.81 (10.4%); £3,774,691.96 -> £3,382,646.99 (10.4%); £3,774,692.18 -> £3,382,647.17 (10.4%); £3,774,692.41 -> £3,382,647.20 (10.4%); £3,774,692.64 -> £3,382,647.23 (10.4%); £3,774,692.86 -> £3,382,647.26 (10.4%); £3,774,693.09 -> £3,382,647.28 (10.4%); £3,774,693.31 -> £3,382,647.31 (10.4%); £3,774,693.54 -> £3,382,647.34 (10.4%); £3,774,693.77 -> £3,382,647.37 (10.4%); £3,774,694.00 -> £3,382,647.39 (10.4%); £3,774,694.23 -> £3,382,647.42 (10.4%); £3,774,694.45 -> £3,382,647.45 (10.4%); £3,774,694.67 -> £3,382,647.47 (10.4%); £3,774,694.89 -> £3,382,647.50 (10.4%); £3,774,695.12 -> £3,382,647.53 (10.4%); £3,774,695.35 -> £3,382,647.70 (10.4%); £3,774,695.58 -> £3,382,647.88 (10.4%); £3,774,695.81 -> £3,382,648.05 (10.4%); £3,774,696.05 -> £3,382,648.22 (10.4%); £3,774,696.28 -> £3,382,648.40 (10.4%); £3,774,696.50 -> £3,382,648.57 (10.4%); £3,774,696.73 -> £3,382,648.74 (10.4%); £3,774,696.95 -> £3,382,648.93 (10.4%); £3,774,697.18 -> £3,382,649.11 (10.4%); £3,774,697.40 -> £3,382,649.28 (10.4%); £3,774,697.63 -> £3,382,649.45 (10.4%); £3,774,697.86 -> £3,382,649.48 (10.4%); £3,774,698.08 -> £3,382,649.51 (10.4%); £3,774,698.29 -> £3,382,649.54 (10.4%); £3,774,698.48 -> £3,382,649.56 (10.4%); £3,774,698.65 -> £3,382,649.58 (10.4%); £3,774,698.80 -> £3,382,649.61 (10.4%); £3,774,698.93 -> £3,382,649.62 (10.4%); £3,774,699.08 -> £3,382,649.64 (10.4%); £3,774,699.22 -> £3,382,649.66 (10.4%); £3,774,699.36 -> £3,382,649.68 (10.4%); £3,774,699.50 -> £3,382,649.70 (10.4%); £3,774,699.64 -> £3,382,649.71 (10.4%); £3,774,699.78 -> £3,382,649.73 (10.4%); £3,774,699.92 -> £3,382,649.75 (10.4%); £3,774,700.06 -> £3,382,649.76 (10.4%); £3,774,700.20 -> £3,382,649.78 (10.4%); £3,774,700.35 -> £3,382,649.93 (10.4%); £3,774,700.50 -> £3,382,650.07 (10.4%); £3,774,700.65 -> £3,382,650.22 (10.4%); £3,774,700.82 -> £3,382,650.37 (10.4%); £3,774,701.00 -> £3,382,650.53 (10.4%); £3,774,701.21 -> £3,382,650.69 (10.4%); £3,774,701.42 -> £3,382,650.85 (10.4%); £3,774,701.65 -> £3,382,651.00 (10.4%); £3,774,701.89 -> £3,382,651.04 (10.4%); £3,774,702.13 -> £3,382,651.07 (10.4%); £3,774,702.35 -> £3,382,651.10 (10.4%); £3,774,702.58 -> £3,382,651.13 (10.4%); £3,774,702.81 -> £3,382,651.16 (10.4%); £3,774,703.05 -> £3,382,651.19 (10.4%); £3,774,703.28 -> £3,382,651.22 (10.4%); £3,774,703.51 -> £3,382,651.25 (10.4%); £3,774,703.74 -> £3,382,651.28 (10.4%); £3,774,703.97 -> £3,382,651.31 (10.4%); £3,774,704.21 -> £3,382,651.34 (10.4%); £3,774,704.43 -> £3,382,651.37 (10.4%); £3,774,704.67 -> £3,382,651.40 (10.4%); £3,774,704.90 -> £3,382,651.55 (10.4%); £3,774,705.14 -> £3,382,651.70 (10.4%); £3,774,705.37 -> £3,382,651.85 (10.4%); £3,774,705.60 -> £3,382,652.01 (10.4%); £3,774,705.83 -> £3,382,652.16 (10.4%); £3,774,706.07 -> £3,382,652.31 (10.4%); £3,774,706.30 -> £3,382,652.47 (10.4%); £3,774,706.54 -> £3,382,652.62 (10.4%); £3,774,706.78 -> £3,382,652.77 (10.4%); £3,774,707.01 -> £3,382,652.92 (10.4%); £3,774,707.25 -> £3,382,653.07 (10.4%); £3,774,707.48 -> £3,382,653.10 (10.4%); £3,774,707.72 -> £3,382,653.13 (10.4%); £3,774,707.95 -> £3,382,653.16 (10.4%); £3,774,708.14 -> £3,382,653.18 (10.4%); £3,774,708.32 -> £3,382,653.20 (10.4%); £3,774,708.48 -> £3,382,653.22 (10.4%); £3,774,708.64 -> £3,382,653.23 (10.4%); £3,774,708.80 -> £3,382,653.25 (10.4%); £3,774,708.96 -> £3,382,653.27 (10.4%); £3,774,709.13 -> £3,382,653.28 (10.4%); £3,774,709.29 -> £3,382,653.30 (10.4%); £3,774,709.45 -> £3,382,653.32 (10.4%); £3,774,709.62 -> £3,382,653.33 (10.4%); £3,774,709.78 -> £3,382,653.35 (10.4%); £3,774,709.94 -> £3,382,653.37 (10.4%); £3,774,710.10 -> £3,382,653.39 (10.4%); £3,774,710.26 -> £3,382,653.53 (10.4%); £3,774,710.42 -> £3,382,653.66 (10.4%); £3,774,710.60 -> £3,382,653.81 (10.4%); £3,774,710.80 -> £3,382,653.96 (10.4%); £3,774,711.01 -> £3,382,654.11 (10.4%); £3,774,711.24 -> £3,382,654.26 (10.4%); £3,774,711.50 -> £3,382,654.41 (10.4%); £3,774,711.77 -> £3,382,654.56 (10.4%); £3,774,712.04 -> £3,382,654.58 (10.4%); £3,774,712.32 -> £3,382,654.61 (10.4%); £3,774,712.59 -> £3,382,654.63 (10.4%); £3,774,712.86 -> £3,382,654.65 (10.4%); £3,774,713.13 -> £3,382,654.68 (10.4%); £3,774,713.40 -> £3,382,654.70 (10.4%); £3,774,713.67 -> £3,382,654.73 (10.4%); £3,774,713.94 -> £3,382,654.75 (10.4%); £3,774,714.22 -> £3,382,654.77 (10.4%); £3,774,714.49 -> £3,382,654.80 (10.4%); £3,774,714.76 -> £3,382,654.82 (10.4%); £3,774,715.03 -> £3,382,654.85 (10.4%); £3,774,715.30 -> £3,382,654.87 (10.4%); £3,774,715.57 -> £3,382,655.02 (10.4%); £3,774,715.84 -> £3,382,655.17 (10.4%); £3,774,716.11 -> £3,382,655.32 (10.4%); £3,774,716.37 -> £3,382,655.47 (10.4%); £3,774,716.63 -> £3,382,655.62 (10.4%); £3,774,716.89 -> £3,382,655.77 (10.4%); £3,774,717.16 -> £3,382,655.92 (10.4%); £3,774,717.43 -> £3,382,656.07 (10.4%); £3,774,717.70 -> £3,382,656.22 (10.4%); £3,774,717.97 -> £3,382,656.37 (10.4%); £3,774,718.23 -> £3,382,656.51 (10.4%); £3,774,718.49 -> £3,382,656.54 (10.4%); £3,774,718.77 -> £3,382,656.57 (10.4%); £3,774,719.01 -> £3,382,656.59 (10.4%); £3,774,719.23 -> £3,382,656.62 (10.4%); £3,774,719.44 -> £3,382,656.64 (10.4%); £3,774,719.61 -> £3,382,656.65 (10.4%); £3,774,719.77 -> £3,382,656.67 (10.4%); £3,774,719.93 -> £3,382,656.69 (10.4%); £3,774,720.10 -> £3,382,656.71 (10.4%); £3,774,720.26 -> £3,382,656.72 (10.4%); £3,774,720.42 -> £3,382,656.74 (10.4%); £3,774,720.59 -> £3,382,656.76 (10.4%); £3,774,720.75 -> £3,382,656.77 (10.4%); £3,774,720.91 -> £3,382,656.79 (10.4%); £3,774,721.07 -> £3,382,656.81 (10.4%); £3,774,721.23 -> £3,382,656.82 (10.4%); £3,774,721.39 -> £3,382,656.93 (10.4%); £3,774,721.56 -> £3,382,657.05 (10.4%); £3,774,721.74 -> £3,382,657.17 (10.4%); £3,774,721.94 -> £3,382,657.30 (10.4%); £3,774,722.16 -> £3,382,657.43 (10.4%); £3,774,722.39 -> £3,382,657.55 (10.4%); £3,774,722.64 -> £3,382,657.68 (10.4%); £3,774,722.91 -> £3,382,657.80 (10.4%); £3,774,723.18 -> £3,382,657.82 (10.4%); £3,774,723.46 -> £3,382,657.85 (10.4%); £3,774,723.73 -> £3,382,657.87 (10.4%); £3,774,723.98 -> £3,382,657.90 (10.4%); £3,774,724.25 -> £3,382,657.92 (10.4%); £3,774,724.52 -> £3,382,657.95 (10.4%); £3,774,724.79 -> £3,382,657.97 (10.4%); £3,774,725.05 -> £3,382,657.99 (10.4%); £3,774,725.31 -> £3,382,658.02 (10.4%); £3,774,725.58 -> £3,382,658.04 (10.4%); £3,774,725.86 -> £3,382,658.06 (10.4%); £3,774,726.13 -> £3,382,658.09 (10.4%); £3,774,726.40 -> £3,382,658.12 (10.4%); £3,774,726.67 -> £3,382,658.24 (10.4%); £3,774,726.94 -> £3,382,658.38 (10.4%); £3,774,727.21 -> £3,382,658.51 (10.4%); £3,774,727.48 -> £3,382,658.64 (10.4%); £3,774,727.74 -> £3,382,658.77 (10.4%); £3,774,728.01 -> £3,382,658.90 (10.4%); £3,774,728.27 -> £3,382,659.03 (10.4%); £3,774,728.54 -> £3,382,659.16 (10.4%); £3,774,728.80 -> £3,382,659.29 (10.4%); £3,774,729.07 -> £3,382,659.43 (10.4%); £3,774,729.35 -> £3,382,659.55 (10.4%); £3,774,729.62 -> £3,382,659.58 (10.4%); £3,774,729.89 -> £3,382,659.61 (10.4%); £3,774,730.14 -> £3,382,659.64 (10.4%); £3,774,730.37 -> £3,382,659.66 (10.4%); £3,774,730.58 -> £3,382,659.68 (10.4%); £3,774,730.74 -> £3,382,659.70 (10.4%); £3,774,730.90 -> £3,382,659.71 (10.4%); £3,774,731.06 -> £3,382,659.73 (10.4%); £3,774,731.22 -> £3,382,659.75 (10.4%); £3,774,731.38 -> £3,382,659.77 (10.4%); £3,774,731.54 -> £3,382,659.78 (10.4%); £3,774,731.70 -> £3,382,659.80 (10.4%); £3,774,731.86 -> £3,382,659.81 (10.4%); £3,774,732.01 -> £3,382,659.83 (10.4%); £3,774,732.17 -> £3,382,659.85 (10.4%); £3,774,732.33 -> £3,382,659.87 (10.4%); £3,774,732.49 -> £3,382,660.01 (10.4%); £3,774,732.65 -> £3,382,660.15 (10.4%); £3,774,732.82 -> £3,382,660.30 (10.4%); £3,774,733.02 -> £3,382,660.45 (10.4%); £3,774,733.24 -> £3,382,660.60 (10.4%); £3,774,733.48 -> £3,382,660.74 (10.4%); £3,774,733.73 -> £3,382,660.89 (10.4%); £3,774,734.00 -> £3,382,661.04 (10.4%); £3,774,734.27 -> £3,382,661.06 (10.4%); £3,774,734.53 -> £3,382,661.08 (10.4%); £3,774,734.81 -> £3,382,661.11 (10.4%); £3,774,735.07 -> £3,382,661.13 (10.4%); £3,774,735.33 -> £3,382,661.15 (10.4%); £3,774,735.61 -> £3,382,661.18 (10.4%); £3,774,735.88 -> £3,382,661.20 (10.4%); £3,774,736.15 -> £3,382,661.23 (10.4%); £3,774,736.44 -> £3,382,661.25 (10.4%); £3,774,736.70 -> £3,382,661.27 (10.4%); £3,774,736.96 -> £3,382,661.30 (10.4%); £3,774,737.24 -> £3,382,661.32 (10.4%); £3,774,737.51 -> £3,382,661.35 (10.4%); £3,774,737.77 -> £3,382,661.51 (10.4%); £3,774,738.05 -> £3,382,661.67 (10.4%); £3,774,738.32 -> £3,382,661.83 (10.4%); £3,774,738.58 -> £3,382,662.00 (10.4%); £3,774,738.86 -> £3,382,662.16 (10.4%); £3,774,739.12 -> £3,382,662.31 (10.4%); £3,774,739.39 -> £3,382,662.46 (10.4%); £3,774,739.66 -> £3,382,662.62 (10.4%); £3,774,739.93 -> £3,382,662.77 (10.4%); £3,774,740.20 -> £3,382,662.92 (10.4%); £3,774,740.47 -> £3,382,663.07 (10.4%); £3,774,740.73 -> £3,382,663.10 (10.4%); £3,774,741.02 -> £3,382,663.12 (10.4%); £3,774,741.26 -> £3,382,663.15 (10.4%); £3,774,741.49 -> £3,382,663.17 (10.4%); £3,774,741.70 -> £3,382,663.19 (10.4%); £3,774,741.86 -> £3,382,663.21 (10.4%); £3,774,742.02 -> £3,382,663.23 (10.4%); £3,774,742.18 -> £3,382,663.24 (10.4%); £3,774,742.34 -> £3,382,663.26 (10.4%); £3,774,742.50 -> £3,382,663.28 (10.4%); £3,774,742.66 -> £3,382,663.29 (10.4%); £3,774,742.82 -> £3,382,663.31 (10.4%); £3,774,742.98 -> £3,382,663.33 (10.4%); £3,774,743.14 -> £3,382,663.34 (10.4%); £3,774,743.30 -> £3,382,663.36 (10.4%); £3,774,743.46 -> £3,382,663.38 (10.4%); £3,774,743.62 -> £3,382,663.52 (10.4%); £3,774,743.79 -> £3,382,663.66 (10.4%); £3,774,743.97 -> £3,382,663.82 (10.4%); £3,774,744.18 -> £3,382,663.96 (10.4%); £3,774,744.39 -> £3,382,664.11 (10.4%); £3,774,744.62 -> £3,382,664.26 (10.4%); £3,774,744.88 -> £3,382,664.40 (10.4%); £3,774,745.15 -> £3,382,664.54 (10.4%); £3,774,745.42 -> £3,382,664.56 (10.4%); £3,774,745.69 -> £3,382,664.59 (10.4%); £3,774,745.95 -> £3,382,664.61 (10.4%); £3,774,746.23 -> £3,382,664.63 (10.4%); £3,774,746.51 -> £3,382,664.66 (10.4%); £3,774,746.77 -> £3,382,664.68 (10.4%); £3,774,747.04 -> £3,382,664.71 (10.4%); £3,774,747.32 -> £3,382,664.73 (10.4%); £3,774,747.60 -> £3,382,664.75 (10.4%); £3,774,747.87 -> £3,382,664.78 (10.4%); £3,774,748.14 -> £3,382,664.80 (10.4%); £3,774,748.41 -> £3,382,664.82 (10.4%); £3,774,748.68 -> £3,382,664.85 (10.4%); £3,774,748.97 -> £3,382,665.00 (10.4%); £3,774,749.24 -> £3,382,665.15 (10.4%); £3,774,749.51 -> £3,382,665.31 (10.4%); £3,774,749.77 -> £3,382,665.46 (10.4%); £3,774,750.04 -> £3,382,665.61 (10.4%); £3,774,750.31 -> £3,382,665.76 (10.4%); £3,774,750.59 -> £3,382,665.91 (10.4%); £3,774,750.87 -> £3,382,666.06 (10.4%); £3,774,751.14 -> £3,382,666.20 (10.4%); £3,774,751.42 -> £3,382,666.35 (10.4%); £3,774,751.68 -> £3,382,666.49 (10.4%); £3,774,751.96 -> £3,382,666.52 (10.4%); £3,774,752.24 -> £3,382,666.55 (10.4%); £3,774,752.49 -> £3,382,666.57 (10.4%); £3,774,752.73 -> £3,382,666.60 (10.4%); £3,774,752.94 -> £3,382,666.61 (10.4%); £3,774,753.10 -> £3,382,666.63 (10.4%); £3,774,753.27 -> £3,382,666.65 (10.4%); £3,774,753.43 -> £3,382,666.67 (10.4%); £3,774,753.59 -> £3,382,666.68 (10.4%); £3,774,753.75 -> £3,382,666.70 (10.4%); £3,774,753.91 -> £3,382,666.72 (10.4%); £3,774,754.08 -> £3,382,666.73 (10.4%); £3,774,754.24 -> £3,382,666.75 (10.4%); £3,774,754.40 -> £3,382,666.77 (10.4%); £3,774,754.56 -> £3,382,666.78 (10.4%); £3,774,754.73 -> £3,382,666.80 (10.4%); £3,774,754.89 -> £3,382,666.92 (10.4%); £3,774,755.05 -> £3,382,667.05 (10.4%); £3,774,755.23 -> £3,382,667.18 (10.4%); £3,774,755.43 -> £3,382,667.31 (10.4%); £3,774,755.64 -> £3,382,667.45 (10.4%); £3,774,755.88 -> £3,382,667.58 (10.4%); £3,774,756.13 -> £3,382,667.71 (10.4%); £3,774,756.39 -> £3,382,667.84 (10.4%); £3,774,756.67 -> £3,382,667.86 (10.4%); £3,774,756.93 -> £3,382,667.88 (10.4%); £3,774,757.19 -> £3,382,667.91 (10.4%); £3,774,757.47 -> £3,382,667.93 (10.4%); £3,774,757.74 -> £3,382,667.96 (10.4%); £3,774,758.01 -> £3,382,667.98 (10.4%); £3,774,758.29 -> £3,382,668.00 (10.4%); £3,774,758.56 -> £3,382,668.03 (10.4%); £3,774,758.83 -> £3,382,668.05 (10.4%); £3,774,759.10 -> £3,382,668.07 (10.4%); £3,774,759.37 -> £3,382,668.10 (10.4%); £3,774,759.64 -> £3,382,668.12 (10.4%); £3,774,759.91 -> £3,382,668.15 (10.4%); £3,774,760.17 -> £3,382,668.29 (10.4%); £3,774,760.44 -> £3,382,668.43 (10.4%); £3,774,760.71 -> £3,382,668.57 (10.4%); £3,774,760.99 -> £3,382,668.71 (10.4%); £3,774,761.26 -> £3,382,668.85 (10.4%); £3,774,761.53 -> £3,382,668.99 (10.4%); £3,774,761.80 -> £3,382,669.13 (10.4%); £3,774,762.06 -> £3,382,669.28 (10.4%); £3,774,762.34 -> £3,382,669.42 (10.4%); £3,774,762.62 -> £3,382,669.56 (10.4%); £3,774,762.89 -> £3,382,669.70 (10.4%); £3,774,763.16 -> £3,382,669.73 (10.4%); £3,774,763.43 -> £3,382,669.75 (10.4%); £3,774,763.68 -> £3,382,669.78 (10.4%); £3,774,763.92 -> £3,382,669.80 (10.4%)
- Bills issued: 141, average clarity 0.805, average bill shock 17.1%, bad debt provision £-0.00, avg complaint probability 4.8%
- Solvency signal: £343,429/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £199,173.62 vs. naked (unhedged) net margin: £604,581.76
- hedging cost £405,408.14 vs. a fully unhedged book (commodity-only: actual net £199,173.62 vs. naked net £604,581.76)
  - C1_2: actual £207.67 vs. naked £705.98 -- hedging cost £498.32
  - C2_2: actual £111.04 vs. naked £1,049.84 -- hedging cost £938.81
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £310.82 vs. naked £1,424.72 -- hedging cost £1,113.90
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £18,349.13 vs. naked £119,157.58 -- hedging cost £100,808.45
  - C_IC3g: actual £3,837.46 vs. naked £56,934.03 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £102,722.50 -- hedging cost £101,286.98

**Year narrative:** 2024 produced a net gain of £348,334.21 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 40 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £120,992.73 (gross £518,927.13, capital £5,646.31)
  - Electricity: gross £465,418.35, capital £5,646.31, net £116,542.95
  - Gas: gross £53,508.78, capital £0.00, net £4,449.79
- Treasury at year end: £3,829,410.41
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2025-01-08 period 31, net margin £-81.23

**Customer Book**

- Active accounts: 10 (C1_2, C2_2, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 0, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £372,660.25
  - By billing account: C1 £4,034.93, C1_2 £3,485.86, C2 £5,336.79, C2_2 £3,265.17, C3 £4,837.31, C4 £2,821.14, C5 £9,061.44, C6 £15,051.72, C7 £6,720.99, C8 £6,930.49, C9 £7,180.75, C_IC1 £1,333,397.41, C_IC2 £742,181.66, C_IC3 £2,318,770.74, C_IC4 £1,126,827.37
- Bill shock events (>=20%): 23 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C1_2 2025-04-30 (42%); C1_2 2025-05-31 (28%); C1_2 2025-06-07 (80%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (34%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 32%, C8 32%, C9 26%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01/MWh, net margin £233.00
- C2_2 (electricity): tariff £200.79-£289.53/MWh, net margin £128.44
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £19.93
- C8 (electricity): tariff £149.29-£309.24/MWh, net margin £117.84
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £225.43
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £63,404.31
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,994.92
- C_IC3 (electricity): tariff £88.52-£169.00/MWh, net margin £19,935.55
- C_IC3g (gas): tariff £54.85/MWh, net margin £4,449.79
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £2,483.52

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 60, average clarity 0.768, average bill shock 24.8%, bad debt provision £0.00, avg complaint probability 6.1%
- Solvency signal: £425,490/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £61.99 vs. naked (unhedged) net margin: £345.44
- hedging cost £283.45 vs. a fully unhedged book (commodity-only: actual net £61.99 vs. naked net £345.44)
  - C2_2: actual £92.07 vs. naked £226.54 -- hedging cost £134.47
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £120,992.73 across 10 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 23 customer(s) experienced a bill shock of >=20%.
