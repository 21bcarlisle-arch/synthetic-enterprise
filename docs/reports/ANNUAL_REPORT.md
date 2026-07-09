# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,903,333.21
  (£1,436,696.99 net change)
- Solvency signal (final year): £425,398/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £22,567,483.45
  VAT remitted to HMRC: (£3,739,997.66) | Revenue (ex-VAT): £18,827,485.80
  Non-commodity pass-through: (£4,782,814.91)
- Gross margin: £6,447,470.99
- Capital costs: £51,210.60
- Net margin: £6,396,260.40
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1550, average clarity 0.812,
  service quality score 0.903
- Enterprise value (CLV sum across 15 billing accounts): £8,160,654.31
- Cost to serve (whole portfolio): £18,726.90, net margin after cost to serve: £6,377,533.49
- Hedge effectiveness (whole window): hedging cost £4,223,875.31 vs. a fully unhedged book (commodity-only: actual net £1,436,696.99 vs. naked net £5,660,572.30)

- **2021** (crisis year): net margin £75,626.01, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £338,829.66, 9 risk committee wake-up(s).

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

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,447,470.99, capital £51,210.60, net £6,396,260.40. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £75,626.01 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,396,260.40
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,660,572.30
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,223,875.31 vs. a fully unhedged book (commodity-only: actual net £1,436,696.99 vs. naked net £5,660,572.30)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,382.63 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £612,904.96 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £-134.52 | £561.97 | £324.29 | £751.74 |
| 2017 | £30,139.92 | £0.00 | £361.68 | £623.68 | £516.54 | £31,641.82 |
| 2018 | £101,156.41 | £0.00 | £-186.95 | £348.42 | £436.94 | £101,754.82 |
| 2019 | £222,407.12 | £9,999.92 | £-219.18 | £814.59 | £489.73 | £233,492.18 |
| 2020 | £116,561.53 | £10,030.76 | £439.20 | £1,052.70 | £457.36 | £128,541.55 |
| 2021 | £64,952.49 | £9,999.92 | £592.10 | £258.22 | £-176.72 | £75,626.01 |
| 2022 | £330,248.53 | £9,999.92 | £1,061.56 | £-1,324.12 | £-1,156.22 | £338,829.66 |
| 2023 | £136,230.29 | £9,999.92 | £1,423.12 | £637.98 | £-1,040.96 | £147,250.35 |
| 2024 | £333,603.72 | £10,030.76 | £-509.00 | £3,239.16 | £436.59 | £346,801.23 |
| 2025 | £115,818.30 | £4,449.79 | £0.00 | £724.87 | £0.00 | £120,992.95 |

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
| C7 | 2017-12-31 | renewed | 0.1400 | 0.5500 | 0.8871 | 0.8255 |
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
| C8 | 2020-03-31 | renewed | 0.2600 | 0.5500 | 0.8475 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9355 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.2300 | 0.5500 | 0.8651 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.4100 | 0.5500 | 0.8696 | 0.2845 |
| C1 | 2020-12-30 | churned **CHURNED** | 0.3500 | 0.5500 | 0.7947 | 0.8047 |
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

- **Average absolute error:** 140.8%
- **Average signed error:** +115.0% (over-estimates vs SIM)
- **Renewal events with estimates:** 58

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +114.2% | 114.2% |
| 2017 | 3 | -12.5% | 16.5% |
| 2018 | 4 | +646.2% | 646.2% |
| 2019 | 4 | +602.3% | 642.0% |
| 2020 | 10 | -11.2% | 56.9% |
| 2021 | 8 | +123.5% | 140.4% |
| 2022 | 8 | +2.0% | 11.1% |
| 2023 | 8 | +36.3% | 61.2% |
| 2024 | 8 | +20.2% | 38.4% |
| 2025 | 2 | +15.0% | 22.9% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 58
- **Active renewers:** 20 (34%) — mean company estimate 23.9%, abs error 307.0%
- **Passive SVT-rollers:** 38 (66%) — mean company estimate 9.9%, abs error 53.3%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 13.3% | 0.0% | 114.2% |
| 2017 | 0 | 3 | 0.0% | 9.4% | 0.0% | 16.5% |
| 2018 | 3 | 1 | 53.9% | 13.8% | 843.2% | 55.1% |
| 2019 | 2 | 2 | 53.2% | 13.6% | 1267.4% | 16.7% |
| 2020 | 6 | 4 | 11.5% | 6.9% | 66.3% | 42.7% |
| 2021 | 1 | 7 | 12.7% | 12.4% | 72.6% | 150.1% |
| 2022 | 0 | 8 | 0.0% | 5.5% | 0.0% | 11.1% |
| 2023 | 3 | 5 | 19.0% | 9.6% | 119.9% | 26.0% |
| 2024 | 5 | 3 | 14.2% | 13.0% | 49.3% | 20.2% |
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
| 2016 | 3 | 0 (0%) | -6.3% | 131.2 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 120.0 | 140.0 |
| 2018 | 1 | 0 (0%) | -1.7% | 149.9 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 4 | 0 (0%) | -27.2% | 129.7 | 178.1 |
| 2021 | 7 | 5 (71%) | +14.7% | 216.6 | 187.2 |
| 2022 | 8 | 4 (50%) | +4.3% | 292.4 | 343.4 |
| 2023 | 5 | 0 (0%) | -29.0% | 230.3 | 358.6 |
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
| 2017 | 3 | 0.16× | 0.27× |
| 2018 | 4 | 6.46× ⚠ | 22.57× |
| 2019 | 4 | 6.42× ⚠ | 24.89× |
| 2020 | 10 | 0.57× | 1.48× |
| 2021 | 8 | 1.40× | 5.64× |
| 2022 | 8 | 0.11× | 0.28× |
| 2023 | 8 | 0.61× | 2.57× |
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
| 2023 | 10 | 2.58% | 8.48% | HIGH drift — EV/asset cohort growing |
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
| 2020-12-30 | CHURN | C1 | SIM p=0.21, company est=0.07 |
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
| 2020 | 238,634 | 35,391 | 69,453 | 56,549 | 70,023 | 0 | 470,049 |  |
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
| 2016 | 2,467,441 | 9 | 274,160 | 2108.92× | OK |
| 2017 | 2,498,388 | 10 | 249,839 | 1921.84× | OK |
| 2018 | 2,487,560 | 11 | 226,142 | 1739.55× | OK |
| 2019 | 2,611,529 | 12 | 217,627 | 1674.06× | OK |
| 2020 | 2,923,374 | 14 | 208,812 | 1606.25× | OK |
| 2021 | 2,956,841 | 11 | 268,804 | 2067.72× | OK |
| 2022 | 3,161,294 | 12 | 263,441 | 2026.47× | OK |
| 2023 | 3,383,035 | 11 | 307,549 | 2365.76× | OK |
| 2024 | 3,776,890 | 11 | 343,354 | 2641.18× | OK |
| 2025 | 3,828,579 | 9 | 425,398 | 3272.29× | OK |

End-state (2025): **£425,398/account** across 9 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,441 | 81974.8× | OK |
| 2017 | 466 | 559 | 2,498,388 | 4469.2× | OK |
| 2018 | 849 | 1,019 | 2,487,560 | 2441.2× | OK |
| 2019 | 1,543 | 1,851 | 2,611,529 | 1410.8× | OK |
| 2020 | 1,979 | 2,374 | 2,923,374 | 1231.2× | OK |
| 2021 | 4,332 | 5,198 | 2,956,841 | 568.8× | OK |
| 2022 | 8,502 | 10,203 | 3,161,294 | 309.9× | OK |
| 2023 | 5,613 | 6,736 | 3,383,035 | 502.2× | OK |
| 2024 | 2,659 | 3,191 | 3,776,890 | 1183.8× | OK |
| 2025 | 3,881 | 4,657 | 3,828,579 | 822.1× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,495.78 | £12,233.03 | £261.96/MWh | £144.62/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,985.00 | £9,701.99 | £272.71/MWh | £154.55/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,933.08 | £9,310.51 | £250.25/MWh | £141.72/MWh | +10.9% |

Total HH revenue: £63,659.39 vs flat equivalent £58,755.44 (+8.3% ToU premium)

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
| 2021 | 47 | 1207% | C1_2 (2021-01-31) |
| 2022 | 71 | 1735% | C2_2 (2022-04-30) |
| 2023 | 48 | 101% | C_IC2 (2023-06-30) |
| 2024 | 40 | 107% | C_IC2 (2024-07-31) |
| 2025 | 23 | 80% | C1_2 (2025-06-07) |

Total: **489** bill shock events across 10 years

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
| Total offer cost (foregone margin) | £150,029.98 |
| Margin saved (retained customers' terms) | £1,208,843.28 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£1,058,813.30** |
| Acquisition cost avoided (retained customers) | £2,300.00 |
| **Full economic ROI (margin + acq savings)** | **£1,061,113.30** |

Missed opportunities (churns with no offer): **6** (£6,213.11 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 6 (£6,213.11 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 2 | 2 | £71.21 | £1362.79 | £1291.58 | £0.00 |
| 2018 | 2 | 2 | £24311.34 | £165236.69 | £140925.35 | £0.00 |
| 2019 | 2 | 2 | £32311.18 | £296612.44 | £264301.26 | £0.00 |
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £2646.25 |
| 2021 | 3 | 3 | £65546.54 | £414546.89 | £349000.35 | £0.00 |
| 2022 | 2 | 2 | £27559.78 | £327847.16 | £300287.38 | £236.62 |
| 2023 | 1 | 1 | £229.93 | £3237.32 | £3007.38 | £0.00 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £3330.24 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2017-04-01 | C8 | 0.35 | 3% | £46.02 | £868.15 | £150 | £822.12 | retained |
| 2017-07-01 | C3 | 0.39 | 3% | £25.18 | £494.64 | £150 | £469.46 | retained |
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24227.41 | £163698.72 | £150 | £139471.31 | retained |
| 2018-12-31 | C5 | 0.37 | 3% | £83.93 | £1537.97 | £400 | £1454.04 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.66 | 5% | £17469.37 | £194971.28 | £150 | £177501.91 | retained |
| 2021-03-31 | C_IC2 | 0.39 | 3% | £5309.59 | £91281.89 | £150 | £85972.31 | retained |
| 2021-04-30 | C_IC1 | 0.38 | 3% | £8446.46 | £158248.78 | £150 | £149802.32 | retained |
| 2021-12-31 | C_IC3 | 0.54 | 5% | £51790.49 | £165016.21 | £150 | £113225.72 | retained |
| 2022-04-30 | C_IC2 | 0.40 | 3% | £9417.87 | £96249.57 | £150 | £86831.70 | retained |
| 2022-05-30 | C_IC1 | 0.41 | 3% | £18141.92 | £231597.59 | £150 | £213455.67 | retained |
| 2023-03-31 | C6 | 0.39 | 3% | £229.93 | £3237.32 | £400 | £3007.38 | retained |

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

Serial savers (2): C_IC1 (4 offers, £68,285), C_IC2 (3 offers, £29,569).

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £8,160,654.31 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £718,390.29 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £751.74 |
| 2017 | £31,641.82 |
| 2018 | £101,754.82 |
| 2019 | £233,492.18 |
| 2020 | £128,541.55 |
| 2021 | £75,626.01 |
| 2022 | £338,829.66 |
| 2023 | £147,250.35 | ← trailing
| 2024 | £346,801.23 | ← trailing
| 2025 | £120,992.95 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £5,408.86 | — |
| C1_2 | — | £646.63 |
| C2 | £6,450.72 | — |
| C2_2 | — | £1,553.75 |
| C3 | £7,199.40 | — |
| C4 | £4,319.75 | £-665.09 |
| C5 | £11,854.50 | — |
| C6 | £22,562.18 | £1,600.88 |
| C7 | £9,021.35 | £596.49 |
| C8 | £10,141.46 | £821.97 |
| C9 | £10,993.21 | £1,491.89 |
| C_IC1 | £1,946,507.72 | £410,679.95 |
| C_IC2 | £1,001,099.81 | £217,160.69 |
| C_IC3 | £3,288,435.88 | £67,734.39 |
| C_IC4 | £1,826,846.31 | £16,768.75 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C1_2 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £6,522.54 | — | — | — | — | — | £14,339.54 | — | £10,526.48 | — | — | — | — | — | — |
| 2017 | £5,770.04 | — | £11,350.74 | — | £9,696.98 | £8,759.54 | £12,168.29 | £24,527.24 | £8,959.81 | £13,809.78 | £11,347.95 | — | — | — | — |
| 2018 | £6,102.39 | — | £9,236.69 | — | £9,902.95 | £7,224.11 | £11,918.34 | £21,306.17 | £8,359.71 | £11,680.09 | £10,889.97 | £2,735,156.85 | — | — | — |
| 2019 | £6,008.71 | — | £9,828.42 | — | £8,673.34 | £7,865.79 | £12,510.60 | £18,751.84 | £8,851.13 | £10,967.18 | £9,904.90 | £2,260,228.03 | £1,539,851.41 | — | — |
| 2020 | £6,062.93 | £14.67 | £7,461.50 | — | £7,097.51 | £6,958.93 | £11,417.66 | £18,484.19 | £7,699.48 | £10,975.38 | £11,778.47 | £1,600,255.61 | £878,138.44 | £2,961,679.17 | £1,498,358.65 |
| 2021 | £4,592.48 | £1,143.77 | £7,717.34 | — | £6,727.73 | £5,865.90 | £10,706.35 | £18,791.34 | £8,138.18 | £10,014.31 | £8,673.79 | £1,494,085.84 | £990,270.34 | £2,665,830.06 | £1,653,492.90 |
| 2022 | £4,672.87 | £1,812.68 | £6,692.96 | £1,076.89 | £5,964.61 | £3,242.89 | £11,174.91 | £18,581.34 | £5,755.21 | £8,729.70 | £9,426.22 | £1,289,115.03 | £825,289.28 | £2,443,488.43 | £1,171,133.87 |
| 2023 | £4,144.01 | £2,304.56 | £4,847.58 | £2,801.64 | £5,479.83 | £2,651.00 | £7,823.47 | £17,720.14 | £5,475.09 | £8,314.73 | £7,531.69 | £1,371,874.04 | £657,583.63 | £1,975,760.54 | £1,241,920.86 |
| 2024 | £3,941.07 | £2,860.95 | £5,262.09 | £3,191.51 | £5,935.02 | £3,130.12 | £9,843.08 | £15,865.86 | £5,995.94 | £7,601.58 | £7,482.09 | £1,487,751.46 | £656,785.63 | £2,381,217.67 | £1,041,329.45 |
| 2025 | £3,791.32 | £3,674.38 | £4,828.14 | £3,197.06 | £4,696.51 | £2,775.46 | £9,340.29 | £14,672.77 | £6,699.47 | £6,827.64 | £7,476.35 | £1,318,327.54 | £779,985.99 | £2,205,296.81 | £1,141,453.62 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £936.35, range £4.58–£4,218.12.

- C1: cost to serve £274.94, net margin after CTS £2,068.48
- C1_2: cost to serve £244.19, net margin after CTS £5,418.62
- C1g: cost to serve £5.73, net margin after CTS £1,349.51
- C2: cost to serve £329.93, net margin after CTS £3,082.36
- C2_2: cost to serve £175.50, net margin after CTS £5,313.17
- C2g: cost to serve £6.87, net margin after CTS £2,012.33
- C3: cost to serve £219.95, net margin after CTS £2,169.02
- C3g: cost to serve £4.58, net margin after CTS £1,293.95
- C4: cost to serve £439.89, net margin after CTS £2,802.81
- C4g: cost to serve £9.17, net margin after CTS £1,334.80
- C5: cost to serve £599.87, net margin after CTS £7,227.74
- C6: cost to serve £959.77, net margin after CTS £21,490.08
- C7: cost to serve £519.13, net margin after CTS £10,235.35
- C8: cost to serve £505.43, net margin after CTS £11,961.70
- C9: cost to serve £491.72, net margin after CTS £12,216.35
- C_IC1: cost to serve £4,218.12, net margin after CTS £1,870,439.03
- C_IC2: cost to serve £3,718.18, net margin after CTS £906,084.50
- C_IC3: cost to serve £3,218.32, net margin after CTS £1,821,883.05
- C_IC3g: cost to serve £67.07, net margin after CTS £622,579.96
- C_IC4: cost to serve £2,718.52, net margin after CTS £1,103,966.75


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 27 recovery surcharge(s) at renewal based on prior-term losses (3 gas). Avg surcharge: 14.9%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.31/MWh |
| C5 | electricity | 2018-12-31 | £-204.12 | £2,322.71 | +3.8% | £148.68/MWh | £153.36/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,283.71 | £6,187.80 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,215.97 | £10,069.00 | +20.0% | £128.22/MWh | £175.80/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,915.21 | £3,421.95 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £177.14/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.63/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £57.53/MWh |
| C1_2 | electricity | 2021-12-30 | £-149.26 | £1,494.88 | +5.0% | £311.83/MWh | £333.14/MWh |
| C7 | electricity | 2021-12-30 | £-167.18 | £1,936.90 | +3.6% | £311.83/MWh | £343.71/MWh |
| C_IC3 | electricity | 2021-12-31 | £-27,733.67 | £442,879.51 | +1.3% | £224.03/MWh | £260.88/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £317.96/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.66/MWh |
| C4 | electricity | 2022-09-30 | £-231.16 | £893.04 | +20.0% | £404.86/MWh | £487.62/MWh |
| C4g | gas | 2022-09-30 | £-901.21 | £1,040.11 | +20.0% | £183.79/MWh | £250.54/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £337.91/MWh |
| C8 | electricity | 2023-03-31 | £-481.87 | £3,898.74 | +7.4% | £319.17/MWh | £344.46/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.61/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.46/MWh |
| C4 | electricity | 2023-09-30 | £-292.88 | £1,307.19 | +17.4% | £216.77/MWh | £252.45/MWh |
| C4g | gas | 2023-09-30 | £-1,950.48 | £2,732.11 | +20.0% | £47.83/MWh | £66.00/MWh |
| C1_2 | electricity | 2023-12-30 | £-584.58 | £2,732.85 | +16.4% | £242.22/MWh | £267.83/MWh |
| C7 | electricity | 2023-12-30 | £-445.92 | £3,990.91 | +6.2% | £242.22/MWh | £244.32/MWh |
| C_IC3 | electricity | 2023-12-31 | £-124,187.18 | £972,265.10 | +7.8% | £118.95/MWh | £121.78/MWh |
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
- **Estimated margin protected:** £1,208,843.28
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
| C5 | SME | MEDIUM | 27% | 9% | -20.2% [competitive] | £7,227.74 |
| C1 | resi | MEDIUM | 21% | 7% | -22.9% [competitive] | £2,068.48 |
| C_IC3 | I&C | MEDIUM | 20% | 11% | -54.0% [competitive] | £1,821,883.05 |
| C6 | SME | MEDIUM | 19% | 25% | -24.8% [competitive] | £21,490.08 |
| C4 | resi | LOW | 14% | 14% | -9.0% | £2,802.81 |
| C2_2 | resi | LOW | 11% | 10% | +16.5% [overpriced] | £5,313.17 |
| C7 | resi | LOW | 11% | 17% | -14.3% | £10,235.35 |
| C9 | resi | LOW | 11% | 14% | -14.3% | £12,216.35 |
| C8 | resi | LOW | 9% | 13% | -23.6% [competitive] | £11,961.70 |
| C1_2 | resi | LOW | 8% | 8% | +3.3% | £5,418.62 |
| C3 | resi | LOW | 6% | 8% | -39.0% [competitive] | £2,169.02 |
| C2 | resi | LOW | 5% | 6% | +46.6% [overpriced] | £3,082.36 |
| C_IC1 | I&C | LOW | 4% | 95% | -0.1% | £1,870,439.03 |
| C_IC2 | I&C | LOW | 4% | 95% | +12.4% [overpriced] | £906,084.50 |

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
| C3 | resi | 2020-06-30 | 4.0yr | -4.3% | -39.0% | 6% | 8% | £2,169.02 |
| C1 | resi | 2020-12-30 | 5.0yr | -0.7% | -22.9% | 21% | 7% | £2,068.48 |
| C5 | SME | 2020-12-30 | 5.0yr | +2.8% | -20.2% | 27% | 9% | £7,227.74 |
| C2 | resi | 2022-03-31 | 6.0yr | +12.8% | +46.6% | 5% | 6% | £3,082.36 |
| C6 | SME | 2024-03-30 | 8.0yr | -0.7% | -24.8% | 19% | 25% | £21,490.08 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 14% | 14% | £2,802.81 |

**Root Cause Summary:**
- Total churned accounts: 6
- Lifetime margin lost: £38,840.50
- Average tenure at departure: 6.0 years
- Company-warned churns (co. est. >=20%): 1 -- C6
- Crisis-era churns (2021-22): 1 -- absolute crisis price level, not rate-change delta, was the driver
- Overpriced vs SVT at departure: 1 account(s) -- rate shock risk was observable but unactioned

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 6 accounts that churned without an offer? Calibrated from 12 actual offers (observed retention rate 100%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C3 | resi | 2020-06-30 | 8% | £585.26 | 5% | £29.26 | £556.00 | MISSED OPP. |
| C1 | resi | 2020-12-30 | 7% | £415.98 | 5% | £20.80 | £395.19 | MISSED OPP. |
| C5 | SME | 2020-12-30 | 9% | £1,645.00 | 8% | £131.60 | £1,513.40 | MISSED OPP. |
| C2 | resi | 2022-03-31 | 6% | £236.62 | 5% | £11.83 | £224.79 | MISSED OPP. |
| C6 | SME | 2024-03-30 | 25% | £2,861.38 | 8% | £228.91 | £2,632.47 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 14% | £468.86 | 5% | £23.44 | £445.42 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 6
- Correct no-offer (net-neg ETM): 0
- Missed opportunities (positive ETM, below detection): 6
- Total term margin foregone: £6,213.11
- Total retention cost (counterfactual): £445.85
- Net counterfactual benefit: £5,767.26 (at 100% retention probability)
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
| 2020 | £2,374 | £1,979 | 0.19% |
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
| 2016 | 13 | £801 | £525 | £58 | 7.2% |
| 2017 | 14 | £16,735 | £8,803 | £2,260 | 13.5% |
| 2018 | 15 | £29,021 | £17,502 | £6,784 | 23.4% |
| 2019 | 17 | £70,486 | £41,296 | £13,735 | 19.5% |
| 2020 | 19 | £64,385 | £41,671 | £6,765 | 10.5% |
| 2021 | 14 | £123,922 | £54,511 | £5,402 | 4.4% << |
| 2022 | 15 | £229,228 | £69,992 | £22,589 | 9.9% |
| 2023 | 13 | £199,663 | £73,611 | £11,327 | 5.7% |
| 2024 | 13 | £168,408 | £96,798 | £26,677 | 15.8% |
| 2025 | 10 | £97,101 | £51,893 | £12,099 | 12.5% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £26,677 net/customer
**Worst year per customer:** 2016 at £58 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £417 | — | £417 |
| C1_2 | £648 | — | £648 |
| C1g | — | £669 | £669 |
| C2 | £183 | — | £183 |
| C2_2 | £1,551 | — | £1,551 |
| C2g | — | £907 | £907 |
| C3 | £17 | — | £17 |
| C3g | — | £336 | £336 |
| C4 | £125 | — | £125 |
| C4g | — | £-1,625 | £-1,625 * |
| C5 | £-387 | — | £-387 * |
| C6 | £3,215 | — | £3,215 |
| C7 | £-570 | — | £-570 * |
| C8 | £2,329 | — | £2,329 |
| C9 | £2,240 | — | £2,240 |
| C_IC1 | £846,423 | — | £846,423 |
| C_IC2 | £435,789 | — | £435,789 |
| C_IC3 | £136,685 | — | £136,685 |
| C_IC3g | — | £64,511 | £64,511 |
| C_IC4 | £32,221 | — | £32,221 |
| **Total** | **£1,460,884** | **£64,799** | **£1,525,682** |

Loss-making accounts: C4g (£-1,625), C7 (£-570), C5 (£-387)
Gas loss-making: C4g (£-1,625)
Gas portfolio net: £64,799 (4.2% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,047 | £10,957 | £-8,909 |
| 2017 | £30,081 | £112,509 | £-82,427 |
| 2018 | £109,577 | £246,462 | £-136,884 |
| 2019 | £252,591 | £836,859 | £-584,267 |
| 2020 | £85,179 | £962,868 | £-877,689 |
| 2021 | £191,505 | £457,067 | £-265,562 |
| 2022 | £185,436 | £1,208,220 | £-1,022,784 |
| 2023 | £381,045 | £1,220,702 | £-839,657 |
| 2024 | £199,174 | £604,582 | £-405,408 |
| 2025 | £62 | £345 | £-283 |
| **Total** | **£1,436,697** | **£5,660,572** | **£-4,223,875** |

Largest hedging cost: **2022** (£1,022,784 vs naked)
Smallest hedging cost: **2025** (£283 vs naked)
Conclusion: systematic forward hedging cost £4,223,875 over 10 years vs spot purchasing.

## Customer Service Quality

Ofgem benchmarks: bill clarity >0.82 (GREEN) / >0.80 (AMBER) / ≤0.80 (RED); complaint probability <5% (GREEN) / <6% (RED); bill shock <0.20% (GREEN) / <0.30% (AMBER) / ≥0.30% (RED).

| Year | Clarity | Complaint% | Shock% | Shock events | Bills | RAG |
|------|---------|------------|--------|--------------|-------|-----|
| 2016 | 0.829 G | 4.7% | 0.20% | 31 | 108 | GREEN |
| 2017 | 0.818 A | 4.7% | 0.17% | 50 | 168 | AMBER |
| 2018 | 0.809 A | 4.7% | 0.16% | 60 | 180 | AMBER |
| 2019 | 0.823 G | 4.7% | 0.17% | 66 | 204 | GREEN |
| 2020 | 0.831 G | 4.3% | 0.14% | 53 | 205 | GREEN |
| 2021 | 0.816 A | 4.8% | 0.24% | 47 | 168 | AMBER |
| 2022 | 0.782 R | 5.8% | 0.35% | 71 | 160 | RED ! |
| 2023 | 0.802 A | 5.0% | 0.18% | 48 | 156 | AMBER |
| 2024 | 0.805 A | 4.9% | 0.17% | 40 | 141 | AMBER |
| 2025 | 0.768 R | 6.1% | 0.25% | 23 | 60 | RED ! |

Worst clarity year: **2025** (0.768)
Highest complaint probability: **2025** (6.1%)
Worst bill shock: **2022** (0.35%)
RED years: 2022, 2025
AMBER years: 2017, 2018, 2021, 2023, 2024
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,441 | £752 |
| 2017 | 2.69 | WATCH | £2,498,388 | £31,642 |
| 2018 | — | — | £2,487,560 | £101,755 |
| 2019 | — | — | £2,611,529 | £233,492 |
| 2020 | — | — | £2,923,374 | £128,542 |
| 2021 | — | — | £2,956,841 | £75,626 |
| 2022 | 2.70 | WATCH | £3,161,294 | £338,830 |
| 2023 | 2.72 | WATCH | £3,383,035 | £147,250 |
| 2024 | — | — | £3,776,890 | £346,801 |
| 2025 | — | — | £3,828,579 | £120,993 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,828,579)**
**Treasury growth: £2,467,441 → £3,828,579 (+£1,361,137)**

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
| C1 | 2020-12 | 7.3% | £416 | below threshold |
| C5 | 2020-12 | 9.1% | £1,645 | below threshold |
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
| C_IC1 | 2018-01 | £24,227 | £163,699 | 6.8× | 8% | retained |
| C5 | 2018-12 | £84 | £1,538 | 18.3× | 3% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £17,469 | £194,971 | 11.2× | 5% | retained |
| C_IC2 | 2021-03 | £5,310 | £91,282 | 17.2× | 3% | retained |
| C_IC1 | 2021-04 | £8,446 | £158,249 | 18.7× | 3% | retained |
| C_IC3 | 2021-12 | £51,790 | £165,016 | 3.2× | 5% | retained |
| C_IC2 | 2022-04 | £9,418 | £96,250 | 10.2× | 3% | retained |
| C_IC1 | 2022-05 | £18,142 | £231,598 | 12.8× | 3% | retained |
| C6 | 2023-03 | £230 | £3,237 | 14.1× | 3% | retained |

**Total retention spend: £150,030** | **Total margin protected: £1,208,843**
**Portfolio retention ROI: 8.1×** | **Retained: 12/12**
**Best ROI intervention: C3 2017-07 (19.6×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £202,224 | — |
| Exit Gas (with churn risk) | £82,604 | -£119,621 |
| Reprice to Breakeven | £203,849 | +£1,625 |

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
| 2023 | 83.7% | 0.0% | 96.1% | 1 | 12 |
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
| 2022 | 9 | 59 | 6.6 | £20,532 |
| 2023 | 4 | 32 | 8.0 | £48,892 |

**Peak intervention year: 2016 (13 wake-ups)**
**Total committee events (all years): 38**

> Each wake-up adjusts hedge fractions upward for flagged customers. 2016-17 (early book).
> 2022-23 crisis years trigger most interventions on I&C anchor accounts.

## Worst Half-Hourly Settlement Period by Year

Most loss-making single 30-minute period per settlement year.

| Year | Date | SP | Customer | Net Margin £ |
|------|------|----|----------|-------------|
| 2016 | 2016-12-31 | 48 | C5 | -£408 |
| 2017 | 2017-12-31 | 48 | C2 | -£286 |
| 2018 | 2018-12-31 | 48 | C2 | -£196 |
| 2019 | 2019-12-31 | 48 | C5 | -£469 |
| 2020 | 2020-03-16 | 20 | C_IC1 | -£19 |
| 2021 | 2021-12-31 | 48 | C4 | -£181 |
| 2022 | 2022-03-30 | 48 | C2 | -£112 |
| 2023 | 2023-06-16 | 22 | C_IC1 | -£22 |
| 2024 | 2024-03-29 | 48 | C6 | -£994 |
| 2025 | 2025-01-08 | 31 | C_IC1 | -£81 |

**Single worst period: 2024 2024-03-29 SP48 (C6, -£994)** — exposure from gas supply anchor at year-end pricing.

> SP = settlement period (1-48; SP1 = 00:00-00:30). Year-end gas exposure dominates from 2020 onward as C_IC3g position grows.

## BSC Credit Obligation and Regulatory Levy Breakdown

Elexon BSC credit posting requirement and annual levy costs.

| Year | BSC Credit £ | CM Levy £ | Mutualization £ | CCL £ | Gas Network £ |
|------|-------------|----------|----------------|-------|--------------|
| 2016 | £30 | £37 | — | £189 | £479 |
| 2017 | £559 | £1,977 | — | £11,165 | £898 |
| 2018 | £1,019 | £9,350 | — | £17,434 | £905 |
| 2019 | £1,851 | £31,969 | — | £42,460 | £50,388 |
| 2020 | £2,374 | £56,549 | — | £69,453 | £47,213 |
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
| 2016 | 15 | £174,833 | £94,763 | £10,053 | £11,656 |
| 2017 | 1 | £3,123,595 | £1,874,657 | £846,423 | £3,123,595 |
| 2018 | 1 | £1,525,242 | £909,803 | £435,789 | £1,525,242 |
| 2019 | 2 | £6,462,548 | £2,447,748 | £201,196 | £3,231,274 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £32,221 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,231,274/customer)**
**Best net margin cohort: 2017 (£846,423)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £602 | — | 108 |
| 2017 | +£2,707 | £37,159 | £302 | — | 168 |
| 2018 | +£9,875 | £65,510 | £333 | — | 180 |
| 2019 | +£28,353 | £164,625 | £589 | — | 204 |
| 2020 | +£35,391 | £238,634 | £-60 | — | 205 |
| 2021 | +£14,982 | £246,246 | £208 | — | 168 |
| 2022 | -£49,739 CREDIT | £256,213 | £119 | 2 | 160 |
| 2023 | +£64,773 | £271,884 | £0 | 47 | 156 |
| 2024 | +£109,934 | £307,626 | £1,025 | 4271 | 141 |
| 2025 | +£46,950 | £135,727 | £0 | — | 60 |

**CfD turned CREDIT in 2022: -£49,739 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2024 (£1,025)**

> CfD (Contracts for Difference): when wholesale > strike price, generators repay;
> the net credit is passed through as a negative levy on supplier bills.

## Segment Gross Margin Attribution

Gross margin (£) by customer segment and year.

| Year | resi electricity | resi gas | SME electricity | I&C electricity | I&C gas | Total |
|------|----------|----------|----------|----------|----------|-------|
| 2016 | £3,278 | £811 | £2,733 | £0 | £0 | £6,822 |
| 2017 | £4,996 | £1,430 | £3,395 | £113,418 | £0 | £123,239 |
| 2018 | £5,065 | £1,363 | £3,206 | £252,894 | £0 | £262,528 |
| 2019 | £5,781 | £1,428 | £4,050 | £616,144 | £74,626 | £702,029 |
| 2020 | £5,690 | £1,207 | £4,220 | £704,666 | £75,972 | £791,756 |
| 2021 | £5,725 | £354 | £2,955 | £671,861 | £82,255 | £763,149 |
| 2022 | £4,967 | -£762 | £3,744 | £950,817 | £91,118 | £1,049,883 |
| 2023 | £7,936 | -£575 | £4,462 | £823,606 | £121,515 | £956,943 |
| 2024 | £10,495 | £762 | £1,513 | £1,121,958 | £123,652 | £1,258,380 |
| 2025 | £4,535 | £0 | £0 | £460,883 | £53,509 | £518,927 |

**Best gross margin year: 2024 (£1,258,380)** | **Worst: 2016 (£6,822)**
**Loss-making: resi gas in 2022 (£-762)**
**Loss-making: resi gas in 2023 (£-575)**


## Price Cap Headroom (Tariff vs SVT)

Percentage difference between contracted unit rate and SVT (price cap) at term start.
Negative = below cap (headroom). Positive = above cap (I&C terms; SVT applies to resi only).

| Year | Terms | Avg vs SVT% | Above Cap | Min% | Max% |
|------|-------|-------------|-----------|------|------|
| 2016 | 3 | -6.3% | 0/3 | -6.7% | +-5.7% |
| 2017 | 3 | -14.3% | 0/3 | -15.8% | +-12.4% |
| 2018 | 4 | -1.1% | 1/4 | -3.3% | +0.6% |
| 2019 | 4 | -18.8% | 1/4 | -29.4% | +12.4% |
| 2020 | 10 | -30.1% | 0/10 | -68.7% | +-19.2% |
| 2021 | 8 | +11.3% | 5/8 | -12.0% | +60.2% |
| 2022 | 8 | +4.3% | 4/8 | -64.0% | +95.6% |
| 2023 | 8 | -32.7% | 0/8 | -60.5% | +-2.2% |
| 2024 | 8 | -20.6% | 1/8 | -54.0% | +3.3% |
| 2025 | 2 | -3.6% | 1/2 | -23.6% | +16.5% |

**Best headroom year: 2023 (avg 32.7% below SVT)**
**Largest above-SVT year: 2021** (5/8 terms above — note: I&C customers exempt from SVT cap)

> SVT (Standard Variable Tariff) = Ofgem price cap. Residential tariffs must not exceed SVT.
> I&C/SME terms above SVT are expected during crisis years when wholesale >cap.

## Portfolio Stress Test History

Retrospective RAG status: would year-end treasury have survived each scenario?
Credit facility: £2M. Weekly burn estimated at 1% of year-end treasury.

| Year | Treasury £ | Mkt Spike | Credit | Demand | Liquidity | Combined |
|------|-----------|----------|----------|----------|----------|----------|
| 2016 | £2,467,441 | AMBER | RED | GREEN | AMBER | RED |
| 2017 | £2,498,388 | AMBER | RED | GREEN | AMBER | RED |
| 2018 | £2,487,560 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,611,529 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,923,374 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,956,841 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,161,294 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,383,035 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,776,890 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,828,579 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 42.2% | £1,182 | £606 | 1.53% |
| 2017 | 14 | 32.9% | £24,902 | £8,914 | 2.03% |
| 2018 | 15 | 41.1% | £40,063 | £17,611 | 2.23% |
| 2019 | 17 | 40.3% | £96,791 | £41,404 | 2.13% |
| 2020 | 19 | 40.1% | £97,738 | £41,766 | 2.35% |
| 2021 | 14 | 29.1% | £172,566 | £54,604 | 2.22% |
| 2022 | 15 | 22.1% | £282,741 | £70,082 | 2.27% |
| 2023 | 13 | 24.7% | £267,247 | £73,698 | 2.51% |
| 2024 | 13 | 39.1% | £230,799 | £96,828 | 2.44% |
| 2025 | 10 | 38.3% | £122,843 | £51,935 | 3.40% |

**Best EBIT%: 2016 (42.2%)** | **Worst EBIT%: 2022 (22.1%)**
**Peak revenue/customer: 2022 (£282,741)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Population Anchoring -- Complaints & Arrears (Phase PS)

SIM aggregate complaint and arrears rates vs published UK benchmarks.
Complaints: Ofgem QoS survey, I&C adjusted (GREEN 2-6%, crisis 2-8%).
Arrears: DESNZ business energy debt (GREEN <8%, crisis <12%).

| Year | Complaint rate% | C.Bench hi | C.RAG | Arrears rate% | A.Bench hi | A.RAG |
|------|-----------------|-----------|-------|---------------|-----------|-------|
| 2016 | 4.70% | 6% | OK | 30.8% | 8% | ! |
| 2017 | 4.68% | 6% | OK | 28.6% | 8% | ! |
| 2018 | 4.67% | 6% | OK | 33.3% | 8% | ! |
| 2019 | 4.69% | 6% | OK | 23.5% | 8% | ! |
| 2020 | 4.29% | 6% | OK | 10.5% | 8% | ~ |
| 2021 | 4.82% | 8% | OK | 21.4% | 12% | ! |
| 2022 | 5.83% | 8% | OK | 26.7% | 12% | ! |
| 2023 | 5.02% | 8% | OK | 23.1% | 12% | ! |
| 2024 | 4.85% | 6% | OK | 23.1% | 8% | ! |
| 2025 | 6.09% | 6% | ~ | 10.0% | 8% | ~ |

**Complaints:** 9 of 10 years GREEN (I&C baseline 2-6% normal, 2-8% crisis).
**Arrears:** 0 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).

## Plausibility vs Industry

Key metrics vs UK retail energy norms (Ofgem/Cornwall Insight). OK = within range | ~ = amber | ! = outside expected range.

| Year | Net margin% | Gross margin% | Bad debt% | Churn% |
|------|-------------|---------------|-----------|--------|
| 2016 | !42.2% | !51.3% | OK1.53% | ~0% |
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
| C1 | 2020-12 | 20.5% | 7.3% | -13.2pp | UNDERESTIMATED |
| C5 | 2020-12 | 27.1% | 9.1% | -18.0pp | UNDERESTIMATED |
| C2 | 2022-03 | 4.9% | 6.2% | +1.3pp | ACCURATE |
| C6 | 2024-03 | 18.6% | 24.7% | +6.1pp | ACCURATE |
| C4 | 2024-09 | 14.3% | 14.0% | -0.3pp | ACCURATE |

**Outcomes: 2 underestimated / 4 accurate / 0 overestimated**
**Mean absolute error: 6.7pp**
**Systematic bias: company consistently UNDER-predicted churn risk.**

> Company churn estimates derived from company-observable signals (bill shock,
> margin feedback, renewal history) without access to the simulation's internal
> churn parameters — epistemic gap is expected and realistic for a small supplier.

## Counterfactual Retention & Threshold Optimisation

**Current threshold:** 30% | F1=0.000
**Optimal threshold:** 5% | F1=0.211

**RAG [!]:** RED — 3 unrecoverable high-value miss(es) — model underestimates churn: optimal threshold below current

**Missed retention opportunities:** 6 no-offer churns
  Value at stake: £6,213
  Counterfactually recoverable (with offer): 3/6
  Net value recoverable (after offer cost): £2,148

### Per-miss detail

| Year | Customer | Est | SIM p | Recoverable? | Margin | Net value |
|------|----------|-----|-------|-------------|--------|----------|
| 2020 | C3 | 8% | 6% | No | £585 | £-50 |
| 2020 | C1 | 7% | 21% | Yes | £416 | £366 |
| 2020 | C5 | 9% | 27% | Yes | £1,645 | £1,595 |
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
| Detection gate (never scored above offer threshold) | 6 | 3% | 12% | 3/6 | £1,998 | +6.66 |

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

**Total bad debt (all years):** £3,118
**Crisis stress incremental:** £4,676

**RAG [OK]:** GREEN — Incremental credit stress below 0.5% revenue — not material

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (10 active customers) under 12-month forward scenarios.
Generated: 2026-07-09T22:05:59Z

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
| 2021 | 13 | +13.1 | 13 | 0 | 6 |
| 2022 | 12 | +18.2 | 11 | 1 | 5 |
| 2023 | 12 | +7.7 | 8 | 4 | 8 |
| 2024 | 11 | +6.5 | 6 | 5 | 2 |
| 2025 | 2 | +3.4 | 2 | 0 | 0 |

**Total adjustments 2016-2025: 113** | **Peak avg adjustment: 2022 (+18.2 £/MWh)**
**Emergency reprices: 27 total** (8 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £31,389 | £10,463 | — |
| 2017 | 9 | £106,390 | £11,821 | +£75,002 |
| 2018 | 10 | £2,831,777 | £283,178 | +£2,725,387 |
| 2019 | 11 | £3,893,441 | £353,949 | +£1,061,664 |
| 2020 | 14 | £7,026,383 | £501,884 | +£3,132,941 |
| 2021 | 14 | £6,886,050 | £491,861 | £-140,332 |
| 2022 | 15 | £5,806,157 | £387,077 | £-1,079,893 |
| 2023 | 15 | £5,316,233 | £354,416 | £-489,924 |
| 2024 | 15 | £5,638,194 | £375,880 | +£321,961 |
| 2025 | 15 | £5,513,043 | £367,536 | £-125,150 |

**Peak portfolio CLV: 2020 (£7,026,383)** | **Earliest/lowest: 2016 (£31,389)**
**Largest YoY gain: 2020 (+£3,132,941)**
**Largest YoY fall: 2022 (£-1,079,893)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,361.53 | £3,594.97 | £3,892.24 | £7,874.33 | 51.3% | — | — | — | — |
| 2017 | £348,631.32 | £111,055.51 | £112,782.22 | £124,793.59 | 35.8% | +£333,269.79 | +£107,460.54 | +£108,889.98 | +£116,919.27 |
| 2018 | £600,948.35 | £172,800.98 | £163,976.85 | £264,170.52 | 44.0% | +£252,317.03 | +£61,745.47 | +£51,194.63 | +£139,376.93 |
| 2019 | £1,645,451.76 | £496,238.73 | £445,337.03 | £703,876.01 | 42.8% | +£1,044,503.42 | +£323,437.75 | +£281,360.18 | +£439,705.49 |
| 2020 | £1,857,023.20 | £431,614.79 | £631,853.58 | £793,554.82 | 42.7% | +£211,571.44 | £-64,623.93 | +£186,516.55 | +£89,678.81 |
| 2021 | £2,415,921.71 | £971,911.98 | £679,550.33 | £764,459.39 | 31.6% | +£558,898.51 | +£540,297.19 | +£47,696.75 | £-29,095.43 |
| 2022 | £4,241,122.23 | £2,388,593.54 | £801,304.68 | £1,051,224.01 | 24.8% | +£1,825,200.52 | +£1,416,681.56 | +£121,754.34 | +£286,764.62 |
| 2023 | £3,474,210.42 | £1,638,913.23 | £877,218.18 | £958,079.00 | 27.6% | £-766,911.81 | £-749,680.31 | +£75,913.51 | £-93,145.01 |
| 2024 | £3,000,383.61 | £931,711.15 | £809,903.09 | £1,258,769.37 | 42.0% | £-473,826.81 | £-707,202.09 | £-67,315.09 | +£300,690.37 |
| 2025 | £1,228,431.67 | £452,081.00 | £256,996.72 | £519,353.95 | 42.3% | £-1,771,951.94 | £-479,630.15 | £-552,906.38 | £-739,415.42 |

**Best GM year: 2016 (51.3%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Net Margin Bridge (Year-on-Year Attribution)

Decomposes each year's net margin change into: gross margin movement, bad debt, capital costs, policy levies, network costs.

| Transition | Net Δ | Gross Δ | Bad Debt Δ | Capital Δ | Policy Δ | Network Δ | Portfolio | Driver | RAG |
|-----------|-------|---------|-----------|---------|---------|---------|---------|--------|-----|
| 2016→2017 | +£30,890 | +£116,417 | +£300 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£70,113 | +£139,289 | -£31 | -£255 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£131,737 | +£439,500 | -£256 | -£781 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£104,951 | +£89,727 | +£648 | +£346 | -£162,654 | -£33,019 | +2 | policy levies | RED |
| 2020→2021 | -£52,916 | -£28,607 | -£268 | -£3,641 | -£19,033 | -£1,367 | -5 | gross margin | RED |
| 2021→2022 | +£263,204 | +£286,734 | +£89 | -£7,658 | -£1,158 | -£14,803 | +1 | gross margin | GREEN |
| 2022→2023 | -£191,579 | -£92,940 | +£119 | +£3,235 | -£70,703 | -£31,291 | -2 | gross margin | RED |
| 2023→2024 | +£199,551 | +£301,437 | -£1,025 | +£514 | -£100,728 | -£647 | +0 | gross margin | GREEN |
| 2024→2025 | -£225,808 | -£739,453 | +£1,025 | +£3,866 | +£382,030 | +£126,723 | -3 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£225,808)** | **Best transition: 2021→2022 (+£263,204)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Payment Portfolio Health (P2: Billing Infra)

Year-by-year bad debt rate and high-churn-risk customer concentration.

| Year | Bad Debt | Bad Debt Rate | At-Risk Customers | At-Risk % | Trend | RAG |
|------|----------|--------------|-----------------|----------|-------|-----|
| 2016 | £602 | 5.78% | 0/4 | 0% | — STABLE | RED |
| 2017 | £302 | 0.13% | 0/11 | 0% | ↓ IMPROVING | GREEN |
| 2018 | £333 | 0.08% | 1/12 | 8% | ↓ IMPROVING | GREEN |
| 2019 | £589 | 0.05% | 3/13 | 23% | ↓ IMPROVING | GREEN |
| 2020 | £-60 | -0.00% | 5/15 | 33% | ↓ IMPROVING | AMBER |
| 2021 | £208 | 0.01% | 4/12 | 33% | ↑ DETERIORATING | AMBER |
| 2022 | £119 | 0.00% | 9/12 | 75% | ↓ IMPROVING | RED |
| 2023 | £0 | 0.00% | 9/11 | 82% | ↓ IMPROVING | RED |
| 2024 | £1,025 | 0.05% | 3/11 | 27% | ↑ DETERIORATING | GREEN |
| 2025 | £0 | 0.00% | 2/3 | 67% | ↓ IMPROVING | RED |

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
| 2020 | 3 | £2,646 | £2,005 | £174 | +£1,831 |
| 2022 | 1 | £237 | £184 | £16 | +£168 |
| 2024 | 2 | £3,330 | £2,119 | £184 | +£1,935 |

**Total opportunity cost vs actual: +£3,933 net** (gross £6,213 margin lost; £375 offer cost if all retained).

> The shadow strategy net gain is small because all no-offer churns were residential customers with low margins. I&C customers (large margins) already received retention offers — the current threshold strategy is near-optimal for the existing portfolio composition.

## Ofgem FRA Regulatory Capital Ratio (Phase NZ)

Equity / (annual revenue ÷ 12). Ofgem FRA minimum: ≥ 1x monthly revenue.
Sector best practice: ≥ 6x (GREEN). Early warning: < 3x (AMBER). Non-compliant: < 1x (RED).
Real-world context: Bulb 2021 collapse at ~-0.01x; Igloo 2021 ~0.07x.

| Year | Equity | Monthly Rev | FRA Ratio | RAG | Compliant |
|------|--------|-------------|-----------|-----|-----------|
| 2016 | £2,473,113.55 | £1,280.13 | 1931.9x | ✓ GREEN | Yes |
| 2017 | £2,587,826.91 | £29,052.61 | 89.1x | ✓ GREEN | Yes |
| 2018 | £2,834,813.84 | £50,079.03 | 56.6x | ✓ GREEN | Yes |
| 2019 | £3,498,591.59 | £137,120.98 | 25.5x | ✓ GREEN | Yes |
| 2020 | £4,242,861.23 | £154,751.93 | 27.4x | ✓ GREEN | Yes |
| 2021 | £4,944,920.57 | £201,326.81 | 24.6x | ✓ GREEN | Yes |
| 2022 | £5,883,744.99 | £353,426.85 | 16.6x | ✓ GREEN | Yes |
| 2023 | £6,741,496.80 | £289,517.54 | 23.3x | ✓ GREEN | Yes |
| 2024 | £7,914,159.05 | £250,031.97 | 31.6x | ✓ GREEN | Yes |
| 2025 | £8,384,817.87 | £102,369.31 | 81.9x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.6x (equity £5,883,744.99 vs monthly revenue £353,426.85). RAG: GREEN.
**Strongest year:** 2016 — 1931.9x.

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
| 2016 | £15,361.53 | £5,709.37 | £48.53 | ✓ GREEN |  |
| 2017 | £348,631.32 | £129,574.64 | £1,101.38 | ✓ GREEN |  |
| 2018 | £600,948.35 | £223,352.47 | £1,898.50 | ✓ GREEN |  |
| 2019 | £1,645,451.76 | £611,559.57 | £5,198.26 | ✓ GREEN |  |
| 2020 | £1,857,023.20 | £690,193.62 | £5,866.65 | ✓ GREEN |  |
| 2021 | £2,415,921.71 | £897,917.57 | £7,632.30 | ✓ GREEN | CREDIT EXPECTED |
| 2022 | £4,241,122.23 | £1,576,283.76 | £13,398.41 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,474,210.42 | £1,291,248.21 | £10,975.61 | ✓ GREEN |  |
| 2024 | £3,000,383.61 | £1,115,142.58 | £9,478.71 | ✓ GREEN |  |
| 2025 | £1,228,431.67 | £456,567.10 | £3,880.82 | ✓ GREEN |  |

**Peak reconciliation exposure:** 2022 — max adverse £13,398 (4.5 months weighted tail).

_Note: Outstanding pool ≈ current-year revenue × (weighted outstanding months ÷ 12)._
_Max adverse = pool × blended variance rate (0.5% HH + 4% non-HH, portfolio-weighted)._
## Ofgem Supply Licence Health (Phase OC)

Annual licence health checks: customer base, net assets, liquidity, bad debt.
Breach triggers board escalation and Ofgem notification under SLC 0.
WATCH = within 20% of threshold. BREACH = threshold crossed.

| Year | Customers | Net Assets | Treasury | Cash Wks | Bad Debt % | Overall |
|------|-----------|------------|----------|----------|------------|---------|
| 2016 | 13 | £2,473,113.55 | £2,467,441.30 | 35691w | 5.78% | ✗ BREACH |
| 2017 | 14 | £2,587,826.91 | £2,498,388.13 | 1170w | 0.13% | ✗ BREACH |
| 2018 | 15 | £2,834,813.84 | £2,487,559.92 | 749w | 0.08% | ✗ BREACH |
| 2019 | 17 | £3,498,591.59 | £2,611,529.35 | 274w | 0.05% | ✗ BREACH |
| 2020 | 19 | £4,242,861.23 | £2,923,374.33 | 352w | -0.00% | ✗ BREACH |
| 2021 | 14 | £4,944,920.57 | £2,956,841.19 | 158w | 0.01% | ✗ BREACH |
| 2022 | 15 | £5,883,744.99 | £3,161,293.93 | 69w | 0.00% | ✗ BREACH |
| 2023 | 13 | £6,741,496.80 | £3,383,035.01 | 107w | 0.00% | ✗ BREACH |
| 2024 | 13 | £7,914,159.05 | £3,776,889.67 | 211w | 0.05% | ✗ BREACH |
| 2025 | 10 | £8,384,817.87 | £3,828,578.60 | 440w | 0.00% | ✗ BREACH |

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
| 2023 | Yes | 13/13/13 | 15.3 | 5.9 | £0 |
| 2024 | Yes | 13/13/13 | 12.8 | 5.4 | £79 |
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
| 2018 | 3,086.0 | GBP9.40 | GBP29,008.54 |
| 2019 | 7,088.2 | GBP9.45 | GBP66,983.17 |
| 2020 | 10,111.6 | GBP0.00 (scheme closed) | NIL |
| 2021 | 9,988.0 | GBP0.00 (scheme closed) | NIL |
| 2022 | 9,947.8 | GBP0.00 (scheme closed) | NIL |
| 2023 | 9,965.0 | GBP0.00 (scheme closed) | NIL |
| 2024 | 9,994.0 | GBP0.00 (scheme closed) | NIL |
| 2025 | 4,268.1 | GBP0.00 (scheme closed) | NIL |
| **Total** | | | **GBP115,749.11** |

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
| 2022 | 9 | £55,382 | £20,532 | 7 |
| 2023 | 4 | £128,210 | £48,892 | 9 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £128,210 | Unique accounts ever adjusted: 11

**Most frequently adjusted accounts:**
- C1: 22 sessions
- C7: 16 sessions
- C2: 13 sessions
- C5: 12 sessions
- C6: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £10,993.21 | Median churn: 32% | Total portfolio CLV: £8,150,841.18

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC1 | £1,946,507.72 | 29% | 18.8 periods |
| C_IC4 | £1,826,846.31 | 20% | 18.4 periods |
| C6 | £22,562.18 | 26% | 19.2 periods |
| C9 | £10,993.21 | 26% | 17.4 periods |

Quadrant CLV: £3,806,909.43 (47% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £3,288,435.88 | 41% | 17.3 periods |
| C_IC2 | £1,001,099.81 | 32% | 15.6 periods |
| C5 | £11,854.50 | 32% | 18.0 periods |

Quadrant CLV: £4,301,390.20 (53% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C7 | £9,021.35 | 29% | 16.6 periods |
| C3 | £7,199.40 | 11% | 18.7 periods |

Quadrant CLV: £16,220.76 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £10,141.46 | 32% | 15.1 periods |
| C2 | £6,450.72 | 38% | 15.0 periods |
| C1 | £5,408.86 | 35% | 16.4 periods |
| C4 | £4,319.75 | 38% | 18.9 periods |

Quadrant CLV: £26,320.79 (0% of portfolio)

**Board action: CRITICAL quadrant has 3 account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**

## Customer Experience & Service Quality

| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |
|------|----------------|---------------|-------------|---------|------|
| 2016 | 0.829 | 0.047 | 0 | 0 |  |
| 2017 | 0.818 | 0.047 | 0 | 0 |  |
| 2018 | 0.809 | 0.047 | 0 | 0 |  |
| 2019 | 0.823 | 0.047 | 0 | 0 |  |
| 2020 | 0.831 | 0.043 | 2 | 0 |  |
| 2021 | 0.816 | 0.048 | 0 | 0 |  |
| 2022 | 0.782 | 0.058 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.802 | 0.050 | 0 | 0 |  |
| 2024 | 0.805 | 0.049 | 2 | 0 |  |
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
| 2017 | 16.6% | 50 | 168 | 30% |  |
| 2018 | 16.0% | 60 | 180 | 33% |  |
| 2019 | 17.2% | 66 | 204 | 32% |  |
| 2020 | 14.4% | 53 | 205 | 26% |  |
| 2021 | 24.2% | 47 | 168 | 28% | ELEVATED |
| 2022 | 34.5% | 71 | 160 | 44% | **HIGH** |
| 2023 | 18.2% | 48 | 156 | 31% |  |
| 2024 | 17.2% | 40 | 141 | 28% |  |
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
| 2016 | £1,161.79 | £7.45 | £189.19 | £37.24 | £305.34 | £1,701.00 | £3,202.38 |
| 2017 | £37,159.18 | £2,706.77 | £11,164.93 | £1,976.65 | £9,940.12 | £62,947.66 | £26,175.95 |
| 2018 | £65,510.25 | £9,875.25 | £17,433.71 | £9,349.95 | £17,283.87 | £119,453.03 | £38,554.69 |
| 2019 | £164,624.73 | £28,352.66 | £42,460.21 | £31,969.18 | £44,301.87 | £311,708.65 | £88,387.09 |
| 2020 | £238,633.65 | £35,390.58 | £69,453.10 | £56,549.25 | £70,022.90 | £470,049.49 | £124,580.36 |
| 2021 | £246,245.51 | £14,982.00 | £71,202.78 | £49,580.31 | £62,717.48 | £486,078.40 | £122,860.32 |
| 2022 | £256,213.44 | **£-49,738.80** | £70,920.22 | £36,680.77 | £69,110.14 | £482,663.37 | £133,531.29 |
| 2023 | £271,884.08 | £64,772.74 | £71,701.96 | £50,965.78 | £75,106.16 | £548,182.46 | £139,555.39 |
| 2024 | £307,626.36 | £109,933.90 | £72,815.13 | £68,707.47 | £82,562.92 | £643,644.58 | £143,473.05 |
| 2025 | £135,726.90 | £46,949.56 | £31,155.87 | £31,029.39 | £36,151.16 | £281,866.51 | £61,362.58 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.00 (2016) → £281,866.51 (2025). CAGR: 76.4%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £427.45 | £324.29 | £9,028.87 | £1,388.28 | 13.3% | YES |
| 2017 | £31,125.28 | £516.54 | £231,633.78 | £2,660.42 | 1.1% | YES |
| 2018 | £101,317.88 | £436.94 | £432,204.11 | £3,113.94 | 0.7% | YES |
| 2019 | £223,002.53 | £10,489.65 | £1,060,498.05 | £137,766.14 | 11.5% | YES |
| 2020 | £118,053.43 | £10,488.12 | £1,102,193.09 | £121,119.88 | 9.9% | YES |
| 2021 | £65,802.81 | £9,823.20 | £1,437,504.91 | £297,399.17 | 17.1% | YES |
| 2022 | £329,985.96 | £8,843.70 | £2,850,089.48 | £588,329.77 | 17.1% | YES |
| 2023 | £138,291.39 | £8,958.96 | £2,298,418.41 | £297,197.78 | 11.4% | YES |
| 2024 | £336,333.88 | £10,467.35 | £1,918,811.31 | £270,490.62 | 12.4% | YES |
| 2025 | £116,543.17 | £4,449.79 | £838,554.64 | £132,453.71 | 13.6% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £202,224.20 | — | Current strategy |
| EXIT_GAS | £82,603.53 | £-119,620.66 | Remove gas; model elec churn risk |
| REPRICE_GAS | £203,849.33 | £1,625.13 | Raise gas tariff to break-even |

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
| I&C electricity | £5,716,246.48 | £50,044.32 | £1,451,118.32 | 29.0x | Strong |
| I&C gas | £622,647.03 | £0.00 | £64,510.98 | 0.0x | Low return |
| SME electricity | £30,277.46 | £322.07 | £2,828.00 | 8.8x | Moderate |
| resi electricity | £58,468.56 | £646.53 | £6,937.47 | 10.7x | Moderate |
| resi gas | £6,016.94 | £197.67 | £287.56 | 1.5x | Low return |

## Portfolio Concentration Risk

Revenue concentration analysis across 20 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2247** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,324,953.29 (98.6% of total positive margin)
- resi: £61,258.46 (1.0% of total positive margin)
- SME: £28,717.82 (0.4% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,870,439.03 | 29.2% | 4% | £75,378.69 |
| C_IC3 | I&C | £1,821,883.05 | 28.4% | 20% | £369,660.07 |
| C_IC4 | I&C | £1,103,966.75 | 17.2% | 0% | £0.00 |
| C_IC2 | I&C | £906,084.50 | 14.1% | 4% | £33,253.30 |
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
| C1 | electricity | 2016-12-31 | 7.2% | +0.4% | £131.49/MWh | £132.04/MWh |
| C1g | gas | 2016-12-31 | 19.6% | -5.0% | £27.63/MWh | £26.25/MWh |
| C5 | electricity | 2016-12-31 | 8.7% | -0.4% | £131.49/MWh | £131.01/MWh |
| C7 | electricity | 2016-12-31 | 9.4% | -0.7% | £131.49/MWh | £130.57/MWh |
| C2 | electricity | 2017-04-01 | 11.8% | -1.9% | £127.97/MWh | £125.57/MWh |
| C2g | gas | 2017-04-01 | 19.8% | -5.0% | £34.54/MWh | £32.81/MWh |
| C6 | electricity | 2017-04-01 | 9.7% | -0.8% | £127.97/MWh | £126.91/MWh |
| C8 | electricity | 2017-04-01 | 8.9% | -0.5% | £127.97/MWh | £127.36/MWh |
| C3 | electricity | 2017-07-01 | 10.3% | -1.2% | £122.23/MWh | £120.79/MWh |
| C3g | gas | 2017-07-01 | 20.5% | -5.0% | £24.33/MWh | £23.11/MWh |
| C9 | electricity | 2017-07-01 | 10.1% | -1.0% | £122.23/MWh | £120.95/MWh |
| C4 | electricity | 2017-10-01 | 11.2% | -1.6% | £111.62/MWh | £109.86/MWh |
| C4g | gas | 2017-10-01 | 18.4% | -5.0% | £27.48/MWh | £26.10/MWh |
| C1 | electricity | 2017-12-31 | 11.7% | -1.9% | £120.10/MWh | £117.85/MWh |
| C1g | gas | 2017-12-31 | 15.4% | -3.7% | £34.79/MWh | £33.49/MWh |
| C5 | electricity | 2017-12-31 | 9.0% | -0.5% | £120.10/MWh | £119.52/MWh |
| C7 | electricity | 2017-12-31 | 3.7% | +2.1% | £120.10/MWh | £122.68/MWh |
| C_IC1 | electricity | 2018-01-31 | -18.2% | +13.1% | £112.24/MWh | £126.92/MWh |
| C2 | electricity | 2018-04-01 | -6.9% | +7.5% | £133.89/MWh | £143.89/MWh |
| C2g | gas | 2018-04-01 | 15.4% | -3.7% | £38.21/MWh | £36.79/MWh |
| C6 | electricity | 2018-04-01 | -4.4% | +6.2% | £133.89/MWh | £142.18/MWh |
| C8 | electricity | 2018-04-01 | 8.2% | -0.1% | £133.89/MWh | £133.79/MWh |
| C3 | electricity | 2018-07-01 | 10.2% | -1.1% | £128.29/MWh | £126.90/MWh |
| C3g | gas | 2018-07-01 | 13.6% | -2.8% | £29.63/MWh | £28.80/MWh |
| C9 | electricity | 2018-07-01 | 1.8% | +3.1% | £128.29/MWh | £132.25/MWh |
| C4 | electricity | 2018-10-01 | 2.0% | +3.0% | £145.00/MWh | £149.37/MWh |
| C4g | gas | 2018-10-01 | 13.7% | -2.8% | £34.60/MWh | £33.61/MWh |
| C1 | electricity | 2018-12-31 | 6.3% | +0.8% | £148.68/MWh | £149.91/MWh |
| C1g | gas | 2018-12-31 | 13.9% | -3.0% | £37.15/MWh | £36.05/MWh |
| C5 | electricity | 2018-12-31 | 9.2% | -0.6% | £148.68/MWh | £147.77/MWh |
| C7 | electricity | 2018-12-31 | 9.6% | -0.8% | £148.68/MWh | £147.51/MWh |
| C_IC2 | electricity | 2019-01-31 | -30.2% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -20.5% | +14.2% | £128.22/MWh | £146.50/MWh |
| C2 | electricity | 2019-04-01 | 3.2% | +2.4% | £148.35/MWh | £151.90/MWh |
| C2g | gas | 2019-04-01 | 10.4% | -1.2% | £32.94/MWh | £32.54/MWh |
| C6 | electricity | 2019-04-01 | 7.5% | +0.2% | £148.35/MWh | £148.71/MWh |
| C8 | electricity | 2019-04-01 | 27.0% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 19.5% | -5.0% | £127.03/MWh | £120.68/MWh |
| C3g | gas | 2019-07-01 | 13.2% | -2.6% | £23.62/MWh | £23.00/MWh |
| C9 | electricity | 2019-07-01 | 10.0% | -1.0% | £127.03/MWh | £125.74/MWh |
| C4 | electricity | 2019-10-01 | 7.9% | +0.0% | £126.72/MWh | £126.77/MWh |
| C4g | gas | 2019-10-01 | 17.2% | -4.6% | £20.41/MWh | £19.47/MWh |
| C1 | electricity | 2019-12-31 | 10.2% | -1.1% | £127.44/MWh | £126.01/MWh |
| C1g | gas | 2019-12-31 | 14.4% | -3.2% | £26.17/MWh | £25.33/MWh |
| C5 | electricity | 2019-12-31 | 10.1% | -1.1% | £127.44/MWh | £126.07/MWh |
| C7 | electricity | 2019-12-31 | 8.9% | -0.5% | £127.44/MWh | £126.85/MWh |
| C_IC3 | electricity | 2020-01-01 | 7.5% | +0.2% | £47.59/MWh | £47.70/MWh |
| C_IC3g | gas | 2020-01-01 | 20.8% | -5.0% | £16.25/MWh | £15.44/MWh |
| C_IC2 | electricity | 2020-03-01 | -59.4% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -52.0% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 18.7% | -5.0% | £22.80/MWh | £21.66/MWh |
| C6 | electricity | 2020-03-31 | -47.3% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -16.2% | +12.1% | £125.12/MWh | £140.28/MWh |
| C_IC1 | electricity | 2020-03-31 | 20.1% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 16.6% | -4.3% | £113.43/MWh | £108.58/MWh |
| C9 | electricity | 2020-06-30 | 16.6% | -4.3% | £113.43/MWh | £108.58/MWh |
| C4 | electricity | 2020-09-30 | 11.1% | -1.6% | £124.42/MWh | £122.47/MWh |
| C4g | gas | 2020-09-30 | 20.7% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 9.4% | -0.7% | £133.55/MWh | £132.60/MWh |
| C5 | electricity | 2020-12-30 | 2.5% | +2.8% | £133.55/MWh | £137.24/MWh |
| C7 | electricity | 2020-12-30 | 2.5% | +2.8% | £133.55/MWh | £137.24/MWh |
| C_IC3 | electricity | 2020-12-31 | -4.2% | +6.1% | £50.65/MWh | £53.74/MWh |
| C_IC3g | gas | 2020-12-31 | 14.7% | -3.3% | £20.05/MWh | £19.38/MWh |
| C2 | electricity | 2021-03-31 | -21.4% | +14.7% | £175.90/MWh | £201.80/MWh |
| C2g | gas | 2021-03-31 | 7.2% | +0.4% | £36.20/MWh | £36.34/MWh |
| C6 | electricity | 2021-03-31 | -16.1% | +12.1% | £175.90/MWh | £197.10/MWh |
| C8 | electricity | 2021-03-31 | -11.9% | +9.9% | £175.90/MWh | £193.37/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.5% | +6.3% | £138.90/MWh | £147.62/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.9% | +3.6% | £113.97/MWh | £118.02/MWh |
| C9 | electricity | 2021-06-30 | 1.1% | +3.5% | £170.38/MWh | £176.29/MWh |
| C4 | electricity | 2021-09-30 | -2.4% | +5.2% | £205.15/MWh | £215.86/MWh |
| C4g | gas | 2021-09-30 | 6.8% | +0.6% | £53.99/MWh | £54.31/MWh |
| C1_2 | electricity | 2021-12-30 | 4.5% | +1.8% | £311.83/MWh | £317.32/MWh |
| C7 | electricity | 2021-12-30 | -4.7% | +6.4% | £311.83/MWh | £331.66/MWh |
| C_IC3 | electricity | 2021-12-31 | -26.6% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -22.1% | +15.0% | £109.48/MWh | £125.90/MWh |
| C2 | electricity | 2022-03-31 | -17.6% | +12.8% | £361.95/MWh | £408.28/MWh |
| C6 | electricity | 2022-03-31 | -16.8% | +12.4% | £361.95/MWh | £406.88/MWh |
| C8 | electricity | 2022-03-31 | 5.1% | +1.4% | £361.95/MWh | £367.16/MWh |
| C_IC2 | electricity | 2022-04-30 | -10.3% | +9.2% | £269.81/MWh | £294.54/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.9% | +7.4% | £239.42/MWh | £257.21/MWh |
| C9 | electricity | 2022-06-30 | 4.4% | +1.8% | £255.09/MWh | £259.70/MWh |
| C4 | electricity | 2022-09-30 | 7.3% | +0.4% | £404.86/MWh | £406.35/MWh |
| C4g | gas | 2022-09-30 | -19.2% | +13.6% | £183.79/MWh | £208.78/MWh |
| C1_2 | electricity | 2022-12-30 | 8.6% | -0.3% | £266.73/MWh | £265.94/MWh |
| C7 | electricity | 2022-12-30 | -3.1% | +5.6% | £266.73/MWh | £281.59/MWh |
| C_IC3 | electricity | 2022-12-31 | -14.1% | +11.1% | £168.36/MWh | £186.96/MWh |
| C_IC3g | gas | 2022-12-31 | -37.8% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -11.2% | +9.6% | £319.17/MWh | £349.75/MWh |
| C6 | electricity | 2023-03-31 | -0.2% | +4.1% | £319.17/MWh | £332.31/MWh |
| C8 | electricity | 2023-03-31 | 7.0% | +0.5% | £319.17/MWh | £320.85/MWh |
| C_IC2 | electricity | 2023-05-30 | -22.1% | +15.0% | £171.46/MWh | £197.18/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.2% | +12.6% | £163.19/MWh | £183.71/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.09/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.02/MWh |
| C4g | gas | 2023-09-30 | -38.6% | +15.0% | £47.83/MWh | £55.00/MWh |
| C1_2 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C7 | electricity | 2023-12-30 | 26.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 22.3% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -10.0% | +9.0% | £51.89/MWh | £56.57/MWh |
| C2_2 | electricity | 2024-03-30 | 14.6% | -3.3% | £207.71/MWh | £200.84/MWh |
| C6 | electricity | 2024-03-30 | 9.5% | -0.7% | £207.71/MWh | £206.17/MWh |
| C8 | electricity | 2024-03-30 | 9.5% | -0.7% | £207.71/MWh | £206.17/MWh |
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

**Estimated margin at stake** — blind: £6,213.11 | deliberate: £0.00 | total: £6,213.11

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.08 | 0.06 | No | £585.26 |
| C1 | 2020-12-30 | Blind miss | 0.07 | 0.21 | No | £415.98 |
| C5 | 2020-12-30 | Blind miss | 0.09 | 0.27 | No | £1,645.00 |
| C2 | 2022-03-31 | Blind miss | 0.06 | 0.05 | No | £236.62 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.19 | No | £2,861.38 |
| C4 | 2024-09-29 | Blind miss | 0.14 | 0.14 | No | £468.86 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £136,684.97 | £64,510.98 | £201,195.95 | Yes |
| C2+C2g | £182.83 | £907.09 | £1,089.92 | Yes |
| C1+C1g | £416.71 | £669.14 | £1,085.85 | Yes |
| C3+C3g | £16.62 | £336.46 | £353.09 | Yes |
| C4+C4g | £124.53 | £-1,625.13 | £-1,500.60 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £64,798.54.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,525,682.33 across 20 billing accounts. Revenue: £14,030,856.37.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,123,594.92 | £1,874,657.16 | £18,414.22 | £846,423.33 | 27.1% |
| 2 | C_IC2 | fixed | £1,525,242.03 | £909,802.68 | £8,527.39 | £435,789.37 | 28.6% |
| 3 | C_IC3 | pass_through | £4,629,967.80 | £1,825,101.37 | £23,102.71 | £136,684.97 | 3.0% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £64,510.98 | 3.5% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £32,220.65 | 1.2% |
| 6 | C6 | fixed | £38,936.32 | £22,449.85 | £264.31 | £3,214.61 | 8.3% |
| 7 | C8 | fixed | £21,687.00 | £12,467.13 | £134.90 | £2,328.56 | 10.7% |
| 8 | C9 | fixed | £20,243.59 | £12,708.07 | £131.43 | £2,239.82 | 11.1% |
| 9 | C2_2 | fixed | £10,296.64 | £5,488.67 | £67.88 | £1,550.53 | 15.1% |
| 10 | C2g | fixed | £3,849.77 | £2,019.21 | £21.85 | £907.09 | 23.6% |
| 11 | C1g | fixed | £2,436.42 | £1,355.24 | £15.79 | £669.14 | 27.5% |
| 12 | C1_2 | fixed | £11,629.61 | £5,662.82 | £81.65 | £647.97 | 5.6% |
| 13 | C1 | fixed | £3,545.70 | £2,343.42 | £14.11 | £416.71 | 11.8% |
| 14 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £336.46 | 12.5% |
| 15 | C2 | fixed | £5,110.49 | £3,412.30 | £24.74 | £182.83 | 3.6% |
| 16 | C4 | fixed | £6,193.82 | £3,242.70 | £37.58 | £124.53 | 2.0% |
| 17 | C3 | fixed | £3,628.86 | £2,388.97 | £14.77 | £16.62 | 0.5% |
| 18 | C5 | fixed | £12,492.19 | £7,827.61 | £57.77 | £-386.61 | -3.1% |
| 19 | C7 | fixed | £21,728.81 | £10,754.49 | £139.46 | £-570.11 | -2.6% |
| 20 | C4g | fixed | £10,370.30 | £1,343.97 | £144.75 | £-1,625.13 | -15.7% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,030,856 | 100.0% |
| Wholesale cost | -£7,597,200 | 54.1% |
| **Gross supply margin** | **£6,433,656** | **45.9%** |
| Policy + Network costs | -£4,856,764 | 34.6% |
| Capital cost | -£51,211 | 0.4% |
| **Net supply margin** | **£1,525,682** | **10.9%** |

> *The ledger's `net_margin_gbp` (£6,396,260) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,023,444 | 47.5% | 12.1% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 3.5% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £51,429 | 58.9% | 5.5% | CMA 3-8% | ✓ |
| resi/elec | £82,138 | 57.6% | 5.8% | Ofgem CMA 2-5% | ✓ |
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
| Customer bills (all-in) | £22,567,483.45 |
|   Less: VAT remitted to HMRC | (£3,739,997.66) |
| = Revenue (ex-VAT) | £18,827,485.80 |
| Less: non-commodity pass-through | (£4,782,814.91) |
| Wholesale cost (settlement events) | (£7,597,199.90) |
| Gross margin | £6,447,470.99 |
| Capital charges | (£51,210.60) |
| Net margin | £6,396,260.40 |

_Cash reconciliation: of £22,567,483.45 billed, bad debt of £451,473.36 was written off, leaving £22,116,010.09 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £9,684,784.69._

| Acquisition spend | (£862.50) |
| Fixed overhead | (£5,700.00) |
| Cost to serve | (£18,726.90) |
| Operating net margin | £6,370,970.99 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,361.53 | £3,594.97 | £3,892.24 | £7,874.33 | £234.59 | £1,310.66 | £6,477.33 (42.2%) |
| 2017 | £348,631.32 | £111,055.51 | £112,782.22 | £124,793.59 | £7,077.55 | £8,807.01 | £114,713.36 (32.9%) |
| 2018 | £600,948.35 | £172,800.98 | £163,976.85 | £264,170.52 | £13,426.42 | £15,655.54 | £246,986.92 (41.1%) |
| 2019 | £1,645,451.76 | £496,238.73 | £445,337.03 | £703,876.01 | £35,049.79 | £37,788.94 | £663,777.76 (40.3%) |
| 2020 | £1,857,023.20 | £431,614.79 | £631,853.58 | £793,554.82 | £43,654.52 | £47,322.33 | £744,269.64 (40.1%) |
| 2021 | £2,415,921.71 | £971,911.98 | £679,550.33 | £764,459.39 | £53,734.20 | £56,796.49 | £702,059.34 (29.1%) |
| 2022 | £4,241,122.23 | £2,388,593.54 | £801,304.68 | £1,051,224.01 | £96,076.74 | £99,137.74 | £938,824.43 (22.1%) |
| 2023 | £3,474,210.42 | £1,638,913.23 | £877,218.18 | £958,079.00 | £87,240.28 | £90,300.73 | £857,751.80 (24.7%) |
| 2024 | £3,000,383.61 | £931,711.15 | £809,903.09 | £1,258,769.37 | £73,219.48 | £76,594.50 | £1,172,662.26 (39.1%) |
| 2025 | £1,228,431.67 | £452,081.00 | £256,996.72 | £519,353.95 | £41,759.78 | £43,048.82 | £470,658.81 (38.3%) |
| **Total** | **£18,827,485.80** | | | | | | **£5,918,181.65 (31.4%)** |

**Best year:** 2024 — net £1,172,662.26 (39.1% margin)
**Worst year:** 2016 — net £6,477.33 (42.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,384,817.87 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,384,817.87** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,918,181.65 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,361.53 | +4.7% | £6,592.99 | £6,477.33 | -1.8% | GREEN |
| 2017 | £16,138.86 | £348,631.32 | +2060.2% | £7,252.29 | £114,713.36 | +1481.8% | RED |
| 2018 | £386,623.75 | £600,948.35 | +55.4% | £128,424.00 | £246,986.92 | +92.3% | RED |
| 2019 | £675,851.95 | £1,645,451.76 | +143.5% | £281,335.50 | £663,777.76 | +135.9% | RED |
| 2020 | £1,816,630.04 | £1,857,023.20 | +2.2% | £736,963.94 | £744,269.64 | +1.0% | GREEN |
| 2021 | £2,028,952.42 | £2,415,921.71 | +19.1% | £833,649.22 | £702,059.34 | -15.8% | RED |
| 2022 | £2,607,611.88 | £4,241,122.23 | +62.6% | £790,935.58 | £938,824.43 | +18.7% | RED |
| 2023 | £4,508,414.67 | £3,474,210.42 | -22.9% | £1,029,561.00 | £857,751.80 | -16.7% | RED |
| 2024 | £3,512,844.39 | £3,000,383.61 | -14.6% | £893,105.75 | £1,172,662.26 | +31.3% | RED |
| 2025 | £3,145,356.42 | £1,228,431.67 | -60.9% | £1,315,150.33 | £470,658.81 | -64.2% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,389,697.90

## 2016

**Trading & Risk**

- Net margin: £751.74 (gross £6,822.19, capital £86.34)
  - Electricity: gross £6,011.45, capital £78.97, net £427.45
  - Gas: gross £810.73, capital £7.36, net £324.29
- Treasury at year end: £2,467,441.30
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.22, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-01-31: treasury £2,466,649.42, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-03-01: treasury £2,466,662.69, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-03-31: treasury £2,466,676.15, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-04-30: treasury £2,466,687.59, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-05-30: treasury £2,466,698.23, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-06-29: treasury £2,466,709.30, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-07-29: treasury £2,466,720.45, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-08-28: treasury £2,466,731.08, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-09-27: treasury £2,466,742.26, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-10-27: treasury £2,466,753.97, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-11-26: treasury £2,466,766.42, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-12-26: treasury £2,466,778.78, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.25
- Worst single period: C5 on 2016-12-31 period 48, net margin £-407.78

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £10,462.85
  - By billing account: C1 £6,522.54, C5 £14,339.54, C7 £10,526.48
- Bill shock events (>=20%): 31 -- C1g 2016-05-31 (37%); C1g 2016-06-30 (29%); C1g 2016-10-31 (79%); C1g 2016-11-30 (46%); C5 2016-05-31 (27%); C5 2016-10-31 (40%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (77%); C7 2016-11-30 (52%); C2g 2016-05-31 (36%); C2g 2016-06-30 (34%); C2g 2016-10-31 (82%); C2g 2016-11-30 (53%); C6 2016-05-31 (25%); C6 2016-06-30 (23%); C6 2016-10-31 (40%); C6 2016-11-30 (46%); C8 2016-05-31 (40%); C8 2016-06-30 (40%); C8 2016-09-30 (22%); C8 2016-10-31 (100%); C8 2016-11-30 (68%); C3g 2016-10-31 (70%); C3g 2016-11-30 (48%); C9 2016-10-31 (74%); C9 2016-11-30 (58%); C4 2016-11-30 (31%); C4g 2016-11-30 (47%)
- Churn risk (accounts renewing in 2016): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £92.16-£175.95/MWh, net margin £82.87
- C1g (gas): tariff £24.46-£26.25/MWh, net margin £109.88
- C2 (electricity): tariff £84.56-£161.43/MWh, net margin £73.74
- C2g (gas): tariff £26.92/MWh, net margin £116.32
- C3 (electricity): tariff £98.21/MWh, net margin £-66.10 -- **net-negative**
- C3g (gas): tariff £21.93/MWh, net margin £45.98
- C4 (electricity): tariff £77.34-£147.65/MWh, net margin £15.96
- C4g (gas): tariff £24.40/MWh, net margin £52.11
- C5 (electricity): tariff £117.30-£131.01/MWh, net margin £-159.01 -- **net-negative**
- C6 (electricity): tariff £107.62/MWh, net margin £24.49
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £267.20
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £139.89
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £48.41

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.829, average bill shock 19.7%, bad debt provision £601.65, avg complaint probability 4.7%
- Solvency signal: £274,160/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £2,046.85 vs. naked (unhedged) net margin: £10,956.59
- hedging cost £8,909.74 vs. a fully unhedged book (commodity-only: actual net £2,046.85 vs. naked net £10,956.59)
  - C1: actual £275.42 vs. naked £852.97 -- hedging cost £577.55
  - C1g: actual £207.55 vs. naked £516.14 -- hedging cost £308.59
  - C2: actual £84.41 vs. naked £379.56 -- hedging cost £295.15
  - C2g: actual £152.39 vs. naked £385.71 -- hedging cost £233.32
  - C3: actual £29.93 vs. naked £414.50 -- hedging cost £384.57
  - C3g: actual £77.50 vs. naked £396.79 -- hedging cost £319.29
  - C4: actual £42.24 vs. naked £263.33 -- hedging cost £221.09
  - C4g: actual £153.10 vs. naked £606.05 -- hedging cost £452.95
  - C5: actual £414.52 vs. naked £2,694.73 -- hedging cost £2,280.21
  - C6: actual £-19.99 vs. naked £1,068.86 -- hedging cost £1,088.85
  - C7: actual £395.19 vs. naked £1,939.94 -- hedging cost £1,544.76
  - C8: actual £175.42 vs. naked £784.40 -- hedging cost £608.98
  - C9: actual £59.16 vs. naked £653.59 -- hedging cost £594.44

**Year narrative:** 2016 produced a net gain of £751.74 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 31 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £31,641.82 (gross £123,238.69, capital £1,273.22)
  - Electricity: gross £121,809.12, capital £1,258.37, net £31,125.28
  - Gas: gross £1,429.57, capital £14.85, net £516.54
- Treasury at year end: £2,498,388.13
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.92 (avg 0.92), C7 0.91 (avg 0.91), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,467,436.93, C1->1.00, C5->1.00, C7->1.00, VaR (current £307.55 / stressed £98.11) ratio 3.13
  - 2017-02-24: treasury £2,467,443.75, C1->1.00, C5->1.00, C7->1.00, VaR (current £307.55 / stressed £98.11) ratio 3.13
  - 2017-03-26: treasury £2,467,450.43, C1->1.00, C5->1.00, C7->1.00, VaR (current £307.55 / stressed £98.11) ratio 3.13
  - 2017-04-25: treasury £2,467,787.39, C1->1.00, C5->1.00, C7->1.00, VaR (current £859.42 / stressed £329.85) ratio 2.61
  - 2017-05-25: treasury £2,467,787.80, C1->1.00, C5->1.00, C7->1.00, VaR (current £859.42 / stressed £329.85) ratio 2.61
  - 2017-06-24: treasury £2,467,789.28, C1->1.00, C5->1.00, C7->1.00, VaR (current £859.42 / stressed £329.85) ratio 2.61
  - 2017-07-24: treasury £2,467,961.97, C1->1.00, C5->1.00, C7->1.00, VaR (current £996.73 / stressed £394.58) ratio 2.53
  - 2017-08-23: treasury £2,467,965.19, C1->1.00, C5->1.00, C7->1.00, VaR (current £996.73 / stressed £394.58) ratio 2.53
  - 2017-09-22: treasury £2,467,968.02, C1->1.00, C5->1.00, C7->1.00, VaR (current £996.73 / stressed £394.58) ratio 2.53
  - 2017-10-22: treasury £2,468,225.94, C5->1.00, C7->1.00, VaR (current £1,005.13 / stressed £401.30) ratio 2.50
  - 2017-11-21: treasury £2,468,236.71, C5->1.00, C7->1.00, VaR (current £1,005.13 / stressed £401.30) ratio 2.50
  - 2017-12-21: treasury £2,468,248.03, C5->1.00, C7->1.00, VaR (current £1,005.13 / stressed £401.30) ratio 2.50
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.69
- Worst single period: C2 on 2017-12-31 period 48, net margin £-286.19

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £11,821.15
  - By billing account: C1 £5,770.04, C2 £11,350.74, C3 £9,696.98, C4 £8,759.54, C5 £12,168.29, C6 £24,527.24, C7 £8,959.81, C8 £13,809.78, C9 £11,347.95
- Bill shock events (>=20%): 50 -- C1g 2017-01-31 (31%); C1g 2017-02-28 (28%); C1g 2017-05-31 (30%); C1g 2017-06-30 (30%); C1g 2017-09-30 (21%); C1g 2017-11-30 (70%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-05-31 (34%); C2g 2017-06-30 (29%); C2g 2017-09-30 (27%); C2g 2017-11-30 (66%); C2g 2017-12-31 (22%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-05-31 (30%); C3g 2017-06-30 (23%); C3g 2017-09-30 (21%); C3g 2017-11-30 (59%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (30%); C4 2017-09-30 (23%); C4 2017-10-31 (27%); C4 2017-11-30 (29%); C4g 2017-01-31 (23%); C4g 2017-02-28 (22%); C4g 2017-05-31 (33%); C4g 2017-06-30 (35%); C4g 2017-09-30 (36%); C4g 2017-10-31 (22%); C4g 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £92.60-£198.06/MWh, net margin £74.94
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £115.22
- C2 (electricity): tariff £84.56-£188.36/MWh, net margin £-212.20 -- **net-negative**
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £194.46
- C3 (electricity): tariff £98.21-£120.79/MWh, net margin £104.45
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £69.89
- C4 (electricity): tariff £77.34-£164.79/MWh, net margin £49.52
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £136.97
- C5 (electricity): tariff £119.52-£131.01/MWh, net margin £263.18
- C6 (electricity): tariff £107.62-£126.91/MWh, net margin £98.49
- C7 (electricity): tariff £96.39-£195.85/MWh, net margin £194.47
- C8 (electricity): tariff £84.56-£191.05/MWh, net margin £246.35
- C9 (electricity): tariff £77.16-£181.43/MWh, net margin £166.16
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £30,139.92

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.818, average bill shock 16.6%, bad debt provision £301.86, avg complaint probability 4.7%
- Solvency signal: £249,839/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,081.27 vs. naked (unhedged) net margin: £112,509.10
- hedging cost £82,427.84 vs. a fully unhedged book (commodity-only: actual net £30,081.27 vs. naked net £112,509.10)
  - C1: actual £23.36 vs. naked £341.15 -- hedging cost £317.79
  - C1g: actual £131.41 vs. naked £272.27 -- hedging cost £140.86
  - C2: actual £72.90 vs. naked £442.11 -- hedging cost £369.21
  - C2g: actual £207.48 vs. naked £448.25 -- hedging cost £240.78
  - C3: actual £114.24 vs. naked £516.77 -- hedging cost £402.53
  - C3g: actual £30.62 vs. naked £394.35 -- hedging cost £363.73
  - C4: actual £32.54 vs. naked £271.42 -- hedging cost £238.88
  - C4g: actual £44.94 vs. naked £544.66 -- hedging cost £499.72
  - C5: actual £-204.12 vs. naked £1,067.82 -- hedging cost £1,271.94
  - C6: actual £119.83 vs. naked £1,691.30 -- hedging cost £1,571.47
  - C7: actual £-49.22 vs. naked £820.17 -- hedging cost £869.39
  - C8: actual £261.95 vs. naked £997.85 -- hedging cost £735.90
  - C9: actual £247.95 vs. naked £957.89 -- hedging cost £709.94
  - C_IC1: actual £29,047.38 vs. naked £103,743.08 -- hedging cost £74,695.71

**Year narrative:** 2017 produced a net gain of £31,641.82 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 50 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £101,754.82 (gross £262,528.02, capital £1,528.05)
  - Electricity: gross £261,165.22, capital £1,506.99, net £101,317.88
  - Gas: gross £1,362.80, capital £21.07, net £436.94
- Treasury at year end: £2,487,559.92
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.92 (avg 0.92), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C2 on 2018-12-31 period 48, net margin £-196.08

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £283,177.73
  - By billing account: C1 £6,102.39, C2 £9,236.69, C3 £9,902.95, C4 £7,224.11, C5 £11,918.34, C6 £21,306.17, C7 £8,359.71, C8 £11,680.09, C9 £10,889.97, C_IC1 £2,735,156.85
- Bill shock events (>=20%): 60 -- C1g 2018-04-30 (37%); C1g 2018-05-31 (29%); C1g 2018-06-30 (30%); C1g 2018-09-30 (25%); C1g 2018-10-31 (46%); C1g 2018-11-30 (27%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (28%); C2g 2018-05-31 (34%); C2g 2018-06-30 (34%); C2g 2018-09-30 (33%); C2g 2018-10-31 (45%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (28%); C3g 2018-05-31 (32%); C3g 2018-06-30 (29%); C3g 2018-08-31 (34%); C3g 2018-09-30 (34%); C3g 2018-10-31 (35%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (29%); C4 2018-09-30 (24%); C4 2018-10-31 (44%); C4 2018-11-30 (30%); C4g 2018-04-30 (36%); C4g 2018-05-31 (33%); C4g 2018-06-30 (36%); C4g 2018-09-30 (39%); C4g 2018-10-31 (85%); C4g 2018-11-30 (24%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C2 23%, C3 23%, C6 23%, C7 20%, C8 23%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £92.60-£224.87/MWh, net margin £37.49
- C1g (gas): tariff £33.49-£36.05/MWh, net margin £142.44
- C2 (electricity): tariff £98.66-£215.83/MWh, net margin £-127.97 -- **net-negative**
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £189.04
- C3 (electricity): tariff £120.79-£126.90/MWh, net margin £-21.18 -- **net-negative**
- C3g (gas): tariff £23.11-£28.80/MWh, net margin £40.74
- C4 (electricity): tariff £86.32-£224.05/MWh, net margin £66.36
- C4g (gas): tariff £26.10-£33.61/MWh, net margin £64.72
- C5 (electricity): tariff £119.52-£153.36/MWh, net margin £-179.83 -- **net-negative**
- C6 (electricity): tariff £126.91-£142.18/MWh, net margin £-7.12 -- **net-negative**
- C7 (electricity): tariff £96.39-£221.26/MWh, net margin £-13.33 -- **net-negative**
- C8 (electricity): tariff £100.07-£200.69/MWh, net margin £164.36
- C9 (electricity): tariff £95.03-£198.38/MWh, net margin £242.71
- C_IC1 (electricity): tariff £-82.12-£228.46/MWh, net margin £107,347.52
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,191.11 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.809, average bill shock 16.0%, bad debt provision £332.62, avg complaint probability 4.7%
- Solvency signal: £226,142/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £109,577.31 vs. naked (unhedged) net margin: £246,462.05
- hedging cost £136,884.74 vs. a fully unhedged book (commodity-only: actual net £109,577.31 vs. naked net £246,462.05)
  - C1: actual £106.00 vs. naked £575.49 -- hedging cost £469.49
  - C1g: actual £144.33 vs. naked £420.62 -- hedging cost £276.29
  - C2: actual £62.34 vs. naked £503.73 -- hedging cost £441.39
  - C2g: actual £158.01 vs. naked £399.99 -- hedging cost £241.98
  - C3: actual £26.70 vs. naked £557.93 -- hedging cost £531.24
  - C3g: actual £38.90 vs. naked £481.52 -- hedging cost £442.62
  - C4: actual £93.94 vs. naked £459.23 -- hedging cost £365.29
  - C4g: actual £68.19 vs. naked £870.63 -- hedging cost £802.44
  - C5: actual £121.36 vs. naked £1,981.49 -- hedging cost £1,860.13
  - C6: actual £-141.35 vs. naked £1,833.79 -- hedging cost £1,975.14
  - C7: actual £71.76 vs. naked £1,347.76 -- hedging cost £1,276.00
  - C8: actual £24.36 vs. naked £936.67 -- hedging cost £912.31
  - C9: actual £143.78 vs. naked £1,046.10 -- hedging cost £902.32
  - C_IC1: actual £115,351.83 vs. naked £201,600.78 -- hedging cost £86,248.95
  - C_IC2: actual £-6,692.84 vs. naked £33,446.32 -- hedging cost £40,139.15

**Year narrative:** 2018 produced a net gain of £101,754.82 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 60 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £233,492.18 (gross £702,028.50, capital £2,309.31)
  - Electricity: gross £625,974.66, capital £2,287.85, net £223,002.53
  - Gas: gross £76,053.84, capital £21.46, net £10,489.65
- Treasury at year end: £2,611,529.35
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2019-12-31 period 48, net margin £-468.97

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £353,949.21
  - By billing account: C1 £6,008.71, C2 £9,828.42, C3 £8,673.34, C4 £7,865.79, C5 £12,510.60, C6 £18,751.84, C7 £8,851.13, C8 £10,967.18, C9 £9,904.90, C_IC1 £2,260,228.03, C_IC2 £1,539,851.41
- Bill shock events (>=20%): 66 -- C1 2019-04-30 (21%); C1g 2019-01-31 (36%); C1g 2019-02-28 (26%); C1g 2019-05-31 (23%); C1g 2019-06-30 (35%); C1g 2019-10-31 (74%); C1g 2019-11-30 (43%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-01-31 (25%); C2g 2019-02-28 (26%); C2g 2019-04-30 (35%); C2g 2019-06-30 (32%); C2g 2019-07-31 (25%); C2g 2019-09-30 (30%); C2g 2019-10-31 (64%); C2g 2019-11-30 (28%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-02-28 (26%); C3g 2019-06-30 (33%); C3g 2019-07-31 (35%); C3g 2019-09-30 (35%); C3g 2019-10-31 (64%); C3g 2019-11-30 (31%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (32%); C4 2019-09-30 (27%); C4 2019-11-30 (27%); C4g 2019-01-31 (30%); C4g 2019-02-28 (25%); C4g 2019-05-31 (21%); C4g 2019-06-30 (33%); C4g 2019-07-31 (37%); C4g 2019-09-30 (31%); C4g 2019-10-31 (34%); C4g 2019-11-30 (35%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C1 29%, C4 35%, C5 35%, C7 29%, C9 23%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £99.01-£224.87/MWh, net margin £122.21
- C1g (gas): tariff £25.33-£36.05/MWh, net margin £156.37
- C2 (electricity): tariff £113.05-£227.85/MWh, net margin £145.64
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £134.46
- C3 (electricity): tariff £120.68-£126.90/MWh, net margin £-44.99 -- **net-negative**
- C3g (gas): tariff £23.00-£28.80/MWh, net margin £97.85
- C4 (electricity): tariff £99.60-£224.05/MWh, net margin £105.03
- C4g (gas): tariff £19.47-£33.61/MWh, net margin £101.05
- C5 (electricity): tariff £126.07-£153.36/MWh, net margin £-348.42 -- **net-negative**
- C6 (electricity): tariff £142.18-£148.71/MWh, net margin £129.23
- C7 (electricity): tariff £99.67-£221.26/MWh, net margin £111.90
- C8 (electricity): tariff £105.12-£211.40/MWh, net margin £192.85
- C9 (electricity): tariff £98.80-£198.38/MWh, net margin £181.96
- C_IC1 (electricity): tariff £0.00-£263.70/MWh, net margin £139,344.56
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £79,281.83
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £3,780.73
- C_IC3g (gas): tariff £27.53/MWh, net margin £9,999.92

**Portfolio Health**

- Capital cost ratio: 0.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.823, average bill shock 17.2%, bad debt provision £588.54, avg complaint probability 4.7%
- Solvency signal: £217,627/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £252,590.99 vs. naked (unhedged) net margin: £836,858.80
- hedging cost £584,267.81 vs. a fully unhedged book (commodity-only: actual net £252,590.99 vs. naked net £836,858.80)
  - C1: actual £85.49 vs. naked £501.36 -- hedging cost £415.87
  - C1g: actual £137.12 vs. naked £302.41 -- hedging cost £165.30
  - C2: actual £157.71 vs. naked £669.24 -- hedging cost £511.53
  - C2g: actual £93.46 vs. naked £403.54 -- hedging cost £310.08
  - C3: actual £35.26 vs. naked £668.43 -- hedging cost £633.17
  - C3g: actual £135.78 vs. naked £505.74 -- hedging cost £369.96
  - C4: actual £95.76 vs. naked £441.56 -- hedging cost £345.80
  - C4g: actual £101.34 vs. naked £573.92 -- hedging cost £472.58
  - C5: actual £-28.09 vs. naked £1,589.60 -- hedging cost £1,617.68
  - C6: actual £233.34 vs. naked £2,599.58 -- hedging cost £2,366.24
  - C7: actual £56.69 vs. naked £1,146.37 -- hedging cost £1,089.68
  - C8: actual £240.89 vs. naked £1,370.83 -- hedging cost £1,129.94
  - C9: actual £159.20 vs. naked £1,258.26 -- hedging cost £1,099.06
  - C_IC1: actual £154,845.76 vs. naked £297,973.82 -- hedging cost £143,128.05
  - C_IC2: actual £85,558.69 vs. naked £161,523.27 -- hedging cost £75,964.58
  - C_IC3: actual £1,355.95 vs. naked £289,938.26 -- hedging cost £288,582.30
  - C_IC3g: actual £9,326.63 vs. naked £75,392.62 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £233,492.18 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £128,541.55 (gross £791,755.83, capital £1,962.86)
  - Electricity: gross £714,576.28, capital £1,952.57, net £118,053.43
  - Gas: gross £77,179.55, capital £10.29, net £10,488.12
- Treasury at year end: £2,923,374.33
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
- Average CLV (Point-in-Time, year-end 2020): £501,884.47
  - By billing account: C1 £6,062.93, C1_2 £14.67, C2 £7,461.50, C3 £7,097.51, C4 £6,958.93, C5 £11,417.66, C6 £18,484.19, C7 £7,699.48, C8 £10,975.38, C9 £11,778.47, C_IC1 £1,600,255.61, C_IC2 £878,138.44, C_IC3 £2,961,679.17, C_IC4 £1,498,358.65
- Bill shock events (>=20%): 53 -- C1 2020-04-30 (20%); C1g 2020-01-31 (21%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-29 (23%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (32%); C4 2020-09-30 (23%); C4 2020-10-31 (24%); C4 2020-11-30 (25%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (49%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 35%, C4 41%, C5 32%, C7 20%, C8 26%, C9 23%, C_IC1 41%, C_IC2 41%, C_IC3 20%

**Pricing & Margin**

- C1 (electricity): tariff £99.01-£189.01/MWh, net margin £99.22
- C1_2 (electricity): tariff £133.55/MWh, net margin £-1.02 -- **net-negative**
- C1g (gas): tariff £25.33/MWh, net margin £145.23
- C2 (electricity): tariff £113.06-£227.85/MWh, net margin £201.59
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £143.77
- C3 (electricity): tariff £120.68/MWh, net margin £44.45
- C3g (gas): tariff £23.00/MWh, net margin £82.00
- C4 (electricity): tariff £96.23-£190.15/MWh, net margin £91.63
- C4g (gas): tariff £16.09-£19.47/MWh, net margin £86.36
- C5 (electricity): tariff £126.07/MWh, net margin £37.47
- C6 (electricity): tariff £143.89-£148.71/MWh, net margin £401.73
- C7 (electricity): tariff £99.67-£205.86/MWh, net margin £90.87
- C8 (electricity): tariff £110.22-£211.40/MWh, net margin £375.88
- C9 (electricity): tariff £85.31-£188.62/MWh, net margin £150.09
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £53,249.44
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £44,258.51
- C_IC3 (electricity): tariff £37.48-£80.61/MWh, net margin £13,054.01
- C_IC3g (gas): tariff £15.44-£19.38/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £5,999.58

**Portfolio Health**

- Capital cost ratio: 0.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 205, average clarity 0.831, average bill shock 14.4%, bad debt provision £-59.57, avg complaint probability 4.3%
- Solvency signal: £208,812/customer (14 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £85,178.96 vs. naked (unhedged) net margin: £962,868.41
- hedging cost £877,689.45 vs. a fully unhedged book (commodity-only: actual net £85,178.96 vs. naked net £962,868.41)
  - C1_2: actual £-149.26 vs. naked £154.26 -- hedging cost £303.52
  - C2: actual £176.51 vs. naked £581.07 -- hedging cost £404.56
  - C2g: actual £144.84 vs. naked £324.27 -- hedging cost £179.43
  - C4: actual £18.61 vs. naked £244.09 -- hedging cost £225.48
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-167.18 vs. naked £266.42 -- hedging cost £433.59
  - C8: actual £341.44 vs. naked £1,169.99 -- hedging cost £828.55
  - C9: actual £-18.95 vs. naked £697.40 -- hedging cost £716.34
  - C_IC1: actual £33,034.60 vs. naked £128,260.98 -- hedging cost £95,226.38
  - C_IC2: actual £42,303.73 vs. naked £96,422.44 -- hedging cost £54,118.71
  - C_IC3: actual £-16,607.50 vs. naked £220,376.89 -- hedging cost £236,984.39
  - C_IC3g: actual £17,934.51 vs. naked £159,245.07 -- hedging cost £141,310.56
  - C_IC4: actual £7,886.99 vs. naked £352,832.81 -- hedging cost £344,945.82

**Year narrative:** 2020 produced a net gain of £128,541.55 across 19 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £75,626.01 (gross £763,149.08, capital £5,603.57)
  - Electricity: gross £680,540.29, capital £5,590.58, net £65,802.81
  - Gas: gross £82,608.79, capital £12.99, net £9,823.20
- Treasury at year end: £2,956,841.19
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C4 on 2021-12-31 period 48, net margin £-180.66

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2021): £491,860.74
  - By billing account: C1 £4,592.48, C1_2 £1,143.77, C2 £7,717.34, C3 £6,727.73, C4 £5,865.90, C5 £10,706.35, C6 £18,791.34, C7 £8,138.18, C8 £10,014.31, C9 £8,673.79, C_IC1 £1,494,085.84, C_IC2 £990,270.34, C_IC3 £2,665,830.06, C_IC4 £1,653,492.90
- Bill shock events (>=20%): 47 -- C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (62%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (32%); C4 2021-09-30 (25%); C4 2021-10-31 (47%); C4 2021-11-30 (35%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%); C1_2 2021-01-31 (1207%); C1_2 2021-05-31 (33%); C1_2 2021-06-30 (55%); C1_2 2021-10-31 (76%); C1_2 2021-11-30 (75%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C7 20%, C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £133.55-£333.14/MWh, net margin £-89.36 -- **net-negative**
- C2 (electricity): tariff £113.06-£274.50/MWh, net margin £198.84
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £126.10
- C4 (electricity): tariff £96.23-£274.50/MWh, net margin £-245.64 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-302.82 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.10/MWh, net margin £592.10
- C7 (electricity): tariff £107.83-£274.50/MWh, net margin £-99.25 -- **net-negative**
- C8 (electricity): tariff £110.22-£274.50/MWh, net margin £431.50
- C9 (electricity): tariff £85.31-£264.44/MWh, net margin £62.13
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £28,128.63
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £56,369.05
- C_IC3 (electricity): tariff £42.22-£391.32/MWh, net margin £-25,484.20 -- **net-negative**
- C_IC3g (gas): tariff £19.38-£125.90/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £5,939.02

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.816, average bill shock 24.2%, bad debt provision £208.18, avg complaint probability 4.8%
- Solvency signal: £268,804/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £191,504.80 vs. naked (unhedged) net margin: £457,066.87
- hedging cost £265,562.07 vs. a fully unhedged book (commodity-only: actual net £191,504.80 vs. naked net £457,066.87)
  - C1_2: actual £-75.69 vs. naked £590.74 -- hedging cost £666.43
  - C2: actual £138.10 vs. naked £150.31 -- hedging cost £12.22
  - C2g: actual £45.59 vs. naked £-190.70 -- hedging added £236.29
  - C4: actual £-231.16 vs. naked £-156.26 -- hedging cost £74.90
  - C4g: actual £-901.21 vs. naked £-1,344.38 -- hedging added £443.17
  - C6: actual £512.38 vs. naked £267.67 -- hedging added £244.71
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-48.53 vs. naked £-184.07 -- hedging added £135.54
  - C_IC1: actual £27,321.95 vs. naked £-61,903.59 -- hedging added £89,225.54
  - C_IC2: actual £63,529.85 vs. naked £22,089.60 -- hedging added £41,440.25
  - C_IC3: actual £100,518.67 vs. naked £235,005.41 -- hedging cost £134,486.74
  - C_IC3g: actual £4,142.87 vs. naked £85,199.40 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £178,304.23 -- hedging cost £180,207.49

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £75,626.01 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 47 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £338,829.66 (gross £1,049,883.49, capital £13,261.84)
  - Electricity: gross £959,527.57, capital £13,228.00, net £329,985.96
  - Gas: gross £90,355.92, capital £33.84, net £8,843.70
- Treasury at year end: £3,161,293.93
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,037,780.55, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,211.15 / stressed £20,491.01) ratio 2.69
  - 2022-05-29: treasury £3,037,900.95, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,320.95 / stressed £20,520.22) ratio 2.70
  - 2022-06-28: treasury £3,037,895.70, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,320.95 / stressed £20,520.22) ratio 2.70
  - 2022-07-28: treasury £3,037,696.60, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
  - 2022-08-27: treasury £3,037,684.52, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
  - 2022-09-26: treasury £3,037,666.93, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
  - 2022-10-26: treasury £3,036,724.53, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
  - 2022-11-25: treasury £3,036,722.02, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
  - 2022-12-25: treasury £3,036,689.25, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C2 on 2022-03-30 period 48, net margin £-111.99

**Customer Book**

- Active accounts: 15 (C1_2, C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2022): £387,077.13
  - By billing account: C1 £4,672.87, C1_2 £1,812.68, C2 £6,692.96, C2_2 £1,076.89, C3 £5,964.61, C4 £3,242.89, C5 £11,174.91, C6 £18,581.34, C7 £5,755.21, C8 £8,729.70, C9 £9,426.22, C_IC1 £1,289,115.03, C_IC2 £825,289.28, C_IC3 £2,443,488.43, C_IC4 £1,171,133.87
- Bill shock events (>=20%): 71 -- C7 2022-01-31 (52%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (31%); C4 2022-09-30 (28%); C4 2022-10-31 (61%); C4 2022-11-30 (35%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (57%); C_IC3 2022-01-31 (109%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C1_2 2022-01-31 (141%); C1_2 2022-02-28 (28%); C1_2 2022-04-30 (23%); C1_2 2022-05-31 (43%); C1_2 2022-06-30 (34%); C1_2 2022-09-30 (51%); C1_2 2022-11-30 (79%); C1_2 2022-12-31 (61%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 11 at risk (≥20% churn prob): C1_2 41%, C2 38%, C4 38%, C6 35%, C7 29%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.94-£333.14/MWh, net margin £184.51
- C2 (electricity): tariff £143.79-£274.50/MWh, net margin £-96.81 -- **net-negative**
- C2_2 (electricity): tariff £361.95/MWh, net margin £219.72
- C2g (gas): tariff £35.00/MWh, net margin £2.93
- C4 (electricity): tariff £143.79-£457.50/MWh, net margin £-182.93 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,159.15 -- **net-negative**
- C6 (electricity): tariff £197.10-£406.88/MWh, net margin £1,061.56
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,632.87 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £73.71
- C9 (electricity): tariff £138.51-£389.54/MWh, net margin £110.54
- C_IC1 (electricity): tariff £-83.39-£462.98/MWh, net margin £136,459.93
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £76,069.82
- C_IC3 (electricity): tariff £146.90-£391.32/MWh, net margin £111,799.41
- C_IC3g (gas): tariff £116.42-£125.90/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £5,919.38

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 2 -- £3,471,071.11 -> £3,052,541.47 (12.1%); £3,471,249.08 -> £3,051,995.68 (12.1%)
- Bills issued: 160, average clarity 0.782, average bill shock 34.5%, bad debt provision £118.95, avg complaint probability 5.8%
- Solvency signal: £263,441/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £185,436.11 vs. naked (unhedged) net margin: £1,208,220.34
- hedging cost £1,022,784.23 vs. a fully unhedged book (commodity-only: actual net £185,436.11 vs. naked net £1,208,220.34)
  - C1_2: actual £-584.58 vs. naked £1,300.04 -- hedging cost £1,884.62
  - C2_2: actual £30.18 vs. naked £1,645.15 -- hedging cost £1,614.97
  - C4: actual £-292.88 vs. naked £597.69 -- hedging cost £890.57
  - C4g: actual £-1,950.48 vs. naked £1,336.80 -- hedging cost £3,287.28
  - C6: actual £1,128.29 vs. naked £3,996.36 -- hedging cost £2,868.07
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-481.87 vs. naked £1,102.92 -- hedging cost £1,584.78
  - C9: actual £-49.37 vs. naked £1,012.21 -- hedging cost £1,061.58
  - C_IC1: actual £212,769.39 vs. naked £251,051.27 -- hedging cost £38,281.88
  - C_IC2: actual £87,513.94 vs. naked £126,820.48 -- hedging cost £39,306.55
  - C_IC3: actual £-124,187.18 vs. naked £488,717.78 -- hedging cost £612,904.96
  - C_IC3g: actual £8,513.79 vs. naked £123,301.26 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £205,056.67 -- hedging cost £201,583.86

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £338,829.66 across 15 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 71 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £147,250.35 (gross £956,943.40, capital £10,026.47)
  - Electricity: gross £836,003.29, capital £9,974.05, net £138,291.39
  - Gas: gross £120,940.11, capital £52.42, net £8,958.96
- Treasury at year end: £3,383,035.01
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.91 (avg 0.91), C2_2 0.93 (avg 0.93), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,137,644.82, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,174.78 / stressed £43,934.81) ratio 2.76
  - 2023-02-23: treasury £3,137,645.17, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,174.78 / stressed £43,934.81) ratio 2.76
  - 2023-03-25: treasury £3,137,645.47, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,174.78 / stressed £43,934.81) ratio 2.76
  - 2023-04-24: treasury £3,217,865.06, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,209.81 / stressed £48,892.38) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C_IC1 on 2023-06-16 period 22, net margin £-21.69

**Customer Book**

- Active accounts: 13 (C1_2, C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2023): £354,415.52
  - By billing account: C1 £4,144.01, C1_2 £2,304.56, C2 £4,847.58, C2_2 £2,801.64, C3 £5,479.83, C4 £2,651.00, C5 £7,823.47, C6 £17,720.14, C7 £5,475.09, C8 £8,314.73, C9 £7,531.69, C_IC1 £1,371,874.04, C_IC2 £657,583.63, C_IC3 £1,975,760.54, C_IC4 £1,241,920.86
- Bill shock events (>=20%): 48 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (32%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (26%); C4 2023-04-30 (32%); C4 2023-09-30 (26%); C4 2023-11-30 (29%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (46%); C4g 2023-11-30 (63%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (101%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%); C1_2 2023-05-31 (38%); C1_2 2023-06-30 (43%); C1_2 2023-10-31 (73%); C1_2 2023-11-30 (83%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%)
- Churn risk (accounts renewing in 2023): 9 at risk (≥20% churn prob): C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.94-£267.83/MWh, net margin £-440.05 -- **net-negative**
- C2_2 (electricity): tariff £349.75-£361.95/MWh, net margin £691.24
- C4 (electricity): tariff £198.35-£457.50/MWh, net margin £-23.90 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,040.96 -- **net-negative**
- C6 (electricity): tariff £332.31-£406.88/MWh, net margin £1,423.12
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-144.77 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £159.02
- C9 (electricity): tariff £192.57-£389.54/MWh, net margin £396.44
- C_IC1 (electricity): tariff £-60.00-£462.98/MWh, net margin £162,616.93
- C_IC2 (electricity): tariff £-186.24-£476.93/MWh, net margin £86,071.23
- C_IC3 (electricity): tariff £95.69-£280.44/MWh, net margin £-118,385.72 -- **net-negative**
- C_IC3g (gas): tariff £56.57-£116.42/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £5,927.85

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): 47 -- £3,770,564.61 -> £3,382,842.96 (10.3%); £3,770,564.76 -> £3,382,842.98 (10.3%); £3,770,564.91 -> £3,382,842.99 (10.3%); £3,770,565.07 -> £3,382,843.01 (10.3%); £3,770,565.22 -> £3,382,843.02 (10.3%); £3,770,565.37 -> £3,382,843.04 (10.3%); £3,770,565.53 -> £3,382,843.05 (10.3%); £3,770,565.68 -> £3,382,843.07 (10.3%); £3,770,565.84 -> £3,382,843.08 (10.3%); £3,770,566.00 -> £3,382,843.10 (10.3%); £3,770,566.15 -> £3,382,843.11 (10.3%); £3,770,566.31 -> £3,382,843.25 (10.3%); £3,770,566.46 -> £3,382,843.39 (10.3%); £3,770,566.63 -> £3,382,843.52 (10.3%); £3,770,566.82 -> £3,382,843.64 (10.3%); £3,770,567.03 -> £3,382,843.79 (10.3%); £3,770,567.25 -> £3,382,843.93 (10.3%); £3,770,567.50 -> £3,382,844.08 (10.3%); £3,770,567.76 -> £3,382,844.23 (10.3%); £3,770,568.01 -> £3,382,844.25 (10.3%); £3,770,568.28 -> £3,382,844.28 (10.3%); £3,770,568.53 -> £3,382,844.30 (10.3%); £3,770,568.79 -> £3,382,844.33 (10.3%); £3,770,569.05 -> £3,382,844.36 (10.3%); £3,770,569.31 -> £3,382,844.38 (10.3%); £3,770,569.58 -> £3,382,844.41 (10.3%); £3,770,569.85 -> £3,382,844.44 (10.3%); £3,770,570.11 -> £3,382,844.46 (10.3%); £3,770,570.37 -> £3,382,844.48 (10.3%); £3,770,570.62 -> £3,382,844.51 (10.3%); £3,770,570.88 -> £3,382,844.53 (10.3%); £3,770,571.13 -> £3,382,844.56 (10.3%); £3,770,571.39 -> £3,382,844.71 (10.3%); £3,770,571.65 -> £3,382,844.85 (10.3%); £3,770,571.90 -> £3,382,845.00 (10.3%); £3,770,572.16 -> £3,382,845.16 (10.3%); £3,770,572.42 -> £3,382,845.31 (10.3%); £3,770,572.69 -> £3,382,845.46 (10.3%); £3,770,572.95 -> £3,382,845.61 (10.3%); £3,770,573.21 -> £3,382,845.76 (10.3%); £3,770,573.47 -> £3,382,845.91 (10.3%); £3,770,573.73 -> £3,382,846.04 (10.3%); £3,770,573.99 -> £3,382,846.19 (10.3%); £3,770,574.25 -> £3,382,846.21 (10.3%); £3,770,574.51 -> £3,382,846.24 (10.3%); £3,770,574.76 -> £3,382,846.26 (10.3%); £3,770,574.98 -> £3,383,035.01 (10.3%)
- Bills issued: 156, average clarity 0.802, average bill shock 18.2%, bad debt provision £0.00, avg complaint probability 5.0%
- Solvency signal: £307,549/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £381,044.56 vs. naked (unhedged) net margin: £1,220,702.38
- hedging cost £839,657.81 vs. a fully unhedged book (commodity-only: actual net £381,044.56 vs. naked net £1,220,702.38)
  - C1_2: actual £680.74 vs. naked £1,720.30 -- hedging cost £1,039.56
  - C2_2: actual £826.18 vs. naked £2,418.19 -- hedging cost £1,592.00
  - C4: actual £310.55 vs. naked £704.51 -- hedging cost £393.96
  - C4g: actual £529.39 vs. naked £1,048.79 -- hedging cost £519.40
  - C6: actual £1,390.06 vs. naked £5,058.06 -- hedging cost £3,668.00
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £140.61 vs. naked £1,972.23 -- hedging cost £1,831.62
  - C9: actual £626.00 vs. naked £2,129.64 -- hedging cost £1,503.64
  - C_IC1: actual £141,576.45 vs. naked £284,450.26 -- hedging cost £142,873.81
  - C_IC2: actual £94,108.05 vs. naked £162,159.80 -- hedging cost £68,051.75
  - C_IC3: actual £128,010.94 vs. naked £401,816.22 -- hedging cost £273,805.28
  - C_IC3g: actual £8,660.26 vs. naked £123,107.25 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £232,127.67 -- hedging cost £228,435.92

**Year narrative:** 2023 produced a net gain of £147,250.35 across 13 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 48 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £346,801.23 (gross £1,258,379.92, capital £9,512.62)
  - Electricity: gross £1,133,966.04, capital £9,489.22, net £336,333.88
  - Gas: gross £124,413.88, capital £23.40, net £10,467.35
- Treasury at year end: £3,776,889.67
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.87 (avg 0.87), C2_2 0.91 (avg 0.91), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2024-03-29 period 48, net margin £-993.79

**Customer Book**

- Active accounts: 13 (C1_2, C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £375,879.57
  - By billing account: C1 £3,941.07, C1_2 £2,860.95, C2 £5,262.09, C2_2 £3,191.51, C3 £5,935.02, C4 £3,130.12, C5 £9,843.08, C6 £15,865.86, C7 £5,995.94, C8 £7,601.58, C9 £7,482.09, C_IC1 £1,487,751.46, C_IC2 £656,785.63, C_IC3 £2,381,217.67, C_IC4 £1,041,329.45
- Bill shock events (>=20%): 40 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (31%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C1_2 2024-01-31 (21%); C1_2 2024-02-29 (28%); C1_2 2024-04-30 (23%); C1_2 2024-05-31 (44%); C1_2 2024-09-30 (51%); C1_2 2024-10-31 (45%); C1_2 2024-11-30 (57%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (59%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (55%)
- Churn risk (accounts renewing in 2024): 8 at risk (≥20% churn prob): C2_2 23%, C4 38%, C6 26%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC3 41%, C_IC4 20%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01-£267.83/MWh, net margin £760.89
- C2_2 (electricity): tariff £200.84-£349.75/MWh, net margin £510.96
- C4 (electricity): tariff £198.35-£378.67/MWh, net margin £248.49
- C4g (gas): tariff £66.00/MWh, net margin £436.59
- C6 (electricity): tariff £332.31/MWh, net margin £-509.00 -- **net-negative**
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £635.74
- C8 (electricity): tariff £161.99-£397.50/MWh, net margin £427.12
- C9 (electricity): tariff £165.00-£367.64/MWh, net margin £655.96
- C_IC1 (electricity): tariff £-98.58-£330.68/MWh, net margin £125,732.10
- C_IC2 (electricity): tariff £-106.92-£354.92/MWh, net margin £69,935.13
- C_IC3 (electricity): tariff £88.52-£182.68/MWh, net margin £131,985.19
- C_IC3g (gas): tariff £54.85-£56.57/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £5,951.30

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): 4271 -- £3,773,022.96 -> £3,383,035.05 (10.3%); £3,773,023.14 -> £3,383,035.07 (10.3%); £3,773,023.31 -> £3,383,035.09 (10.3%); £3,773,023.49 -> £3,383,035.10 (10.3%); £3,773,023.66 -> £3,383,035.12 (10.3%); £3,773,023.83 -> £3,383,035.14 (10.3%); £3,773,024.00 -> £3,383,035.15 (10.3%); £3,773,024.17 -> £3,383,035.17 (10.3%); £3,773,024.35 -> £3,383,035.19 (10.3%); £3,773,024.52 -> £3,383,035.20 (10.3%); £3,773,024.70 -> £3,383,035.22 (10.3%); £3,773,024.87 -> £3,383,035.37 (10.3%); £3,773,025.04 -> £3,383,035.51 (10.3%); £3,773,025.23 -> £3,383,035.67 (10.3%); £3,773,025.44 -> £3,383,035.82 (10.3%); £3,773,025.66 -> £3,383,035.99 (10.3%); £3,773,025.91 -> £3,383,036.14 (10.3%); £3,773,026.17 -> £3,383,036.30 (10.3%); £3,773,026.45 -> £3,383,036.45 (10.3%); £3,773,026.73 -> £3,383,036.47 (10.3%); £3,773,027.02 -> £3,383,036.50 (10.3%); £3,773,027.31 -> £3,383,036.52 (10.3%); £3,773,027.61 -> £3,383,036.55 (10.3%); £3,773,027.89 -> £3,383,036.57 (10.3%); £3,773,028.18 -> £3,383,036.59 (10.3%); £3,773,028.47 -> £3,383,036.62 (10.3%); £3,773,028.75 -> £3,383,036.64 (10.3%); £3,773,029.03 -> £3,383,036.66 (10.3%); £3,773,029.30 -> £3,383,036.69 (10.3%); £3,773,029.59 -> £3,383,036.71 (10.3%); £3,773,029.87 -> £3,383,036.74 (10.3%); £3,773,030.16 -> £3,383,036.77 (10.3%); £3,773,030.44 -> £3,383,036.93 (10.3%); £3,773,030.73 -> £3,383,037.10 (10.3%); £3,773,030.95 -> £3,383,037.26 (10.3%); £3,773,031.16 -> £3,383,037.42 (10.3%); £3,773,031.38 -> £3,383,037.60 (10.3%); £3,773,031.68 -> £3,383,037.77 (10.3%); £3,773,031.97 -> £3,383,037.94 (10.3%); £3,773,032.25 -> £3,383,038.11 (10.3%); £3,773,032.54 -> £3,383,038.28 (10.3%); £3,773,032.83 -> £3,383,038.45 (10.3%); £3,773,033.12 -> £3,383,038.62 (10.3%); £3,773,033.41 -> £3,383,038.65 (10.3%); £3,773,033.70 -> £3,383,038.68 (10.3%); £3,773,033.96 -> £3,383,038.70 (10.3%); £3,773,034.20 -> £3,383,038.73 (10.3%); £3,773,034.42 -> £3,383,038.75 (10.3%); £3,773,034.60 -> £3,383,038.77 (10.3%); £3,773,034.77 -> £3,383,038.79 (10.3%); £3,773,034.94 -> £3,383,038.80 (10.3%); £3,773,035.11 -> £3,383,038.82 (10.3%); £3,773,035.28 -> £3,383,038.84 (10.3%); £3,773,035.45 -> £3,383,038.86 (10.3%); £3,773,035.62 -> £3,383,038.87 (10.3%); £3,773,035.79 -> £3,383,038.89 (10.3%); £3,773,035.96 -> £3,383,038.91 (10.3%); £3,773,036.13 -> £3,383,038.92 (10.3%); £3,773,036.30 -> £3,383,038.94 (10.3%); £3,773,036.47 -> £3,383,039.07 (10.3%); £3,773,036.64 -> £3,383,039.19 (10.3%); £3,773,036.82 -> £3,383,039.32 (10.3%); £3,773,037.03 -> £3,383,039.45 (10.3%); £3,773,037.26 -> £3,383,039.59 (10.3%); £3,773,037.49 -> £3,383,039.73 (10.3%); £3,773,037.74 -> £3,383,039.86 (10.3%); £3,773,038.02 -> £3,383,039.99 (10.3%); £3,773,038.30 -> £3,383,040.02 (10.3%); £3,773,038.58 -> £3,383,040.04 (10.3%); £3,773,038.87 -> £3,383,040.06 (10.3%); £3,773,039.15 -> £3,383,040.09 (10.3%); £3,773,039.43 -> £3,383,040.11 (10.3%); £3,773,039.70 -> £3,383,040.14 (10.3%); £3,773,039.98 -> £3,383,040.16 (10.3%); £3,773,040.27 -> £3,383,040.18 (10.3%); £3,773,040.54 -> £3,383,040.21 (10.3%); £3,773,040.82 -> £3,383,040.23 (10.3%); £3,773,041.09 -> £3,383,040.25 (10.3%); £3,773,041.37 -> £3,383,040.28 (10.3%); £3,773,041.65 -> £3,383,040.31 (10.3%); £3,773,041.86 -> £3,383,040.44 (10.3%); £3,773,042.07 -> £3,383,040.57 (10.3%); £3,773,042.28 -> £3,383,040.71 (10.3%); £3,773,042.50 -> £3,383,040.85 (10.3%); £3,773,042.71 -> £3,383,040.98 (10.3%); £3,773,042.92 -> £3,383,041.12 (10.3%); £3,773,043.13 -> £3,383,041.25 (10.3%); £3,773,043.41 -> £3,383,041.38 (10.3%); £3,773,043.70 -> £3,383,041.52 (10.3%); £3,773,043.98 -> £3,383,041.66 (10.3%); £3,773,044.26 -> £3,383,041.79 (10.3%); £3,773,044.55 -> £3,383,041.82 (10.3%); £3,773,044.83 -> £3,383,041.85 (10.3%); £3,773,045.09 -> £3,383,041.87 (10.3%); £3,773,045.32 -> £3,383,041.90 (10.3%); £3,773,045.54 -> £3,383,041.92 (10.3%); £3,773,045.71 -> £3,383,041.93 (10.3%); £3,773,045.89 -> £3,383,041.95 (10.3%); £3,773,046.05 -> £3,383,041.97 (10.3%); £3,773,046.22 -> £3,383,041.99 (10.3%); £3,773,046.39 -> £3,383,042.00 (10.3%); £3,773,046.56 -> £3,383,042.02 (10.3%); £3,773,046.73 -> £3,383,042.04 (10.3%); £3,773,046.90 -> £3,383,042.05 (10.3%); £3,773,047.07 -> £3,383,042.07 (10.3%); £3,773,047.24 -> £3,383,042.09 (10.3%); £3,773,047.41 -> £3,383,042.10 (10.3%); £3,773,047.58 -> £3,383,042.25 (10.3%); £3,773,047.75 -> £3,383,042.40 (10.3%); £3,773,047.94 -> £3,383,042.55 (10.3%); £3,773,048.14 -> £3,383,042.72 (10.3%); £3,773,048.37 -> £3,383,042.88 (10.3%); £3,773,048.62 -> £3,383,043.02 (10.3%); £3,773,048.88 -> £3,383,043.17 (10.3%); £3,773,049.16 -> £3,383,043.31 (10.3%); £3,773,049.44 -> £3,383,043.33 (10.3%); £3,773,049.73 -> £3,383,043.36 (10.3%); £3,773,050.01 -> £3,383,043.38 (10.3%); £3,773,050.29 -> £3,383,043.40 (10.3%); £3,773,050.59 -> £3,383,043.43 (10.3%); £3,773,050.88 -> £3,383,043.45 (10.3%); £3,773,051.17 -> £3,383,043.48 (10.3%); £3,773,051.45 -> £3,383,043.50 (10.3%); £3,773,051.72 -> £3,383,043.52 (10.3%); £3,773,052.00 -> £3,383,043.55 (10.3%); £3,773,052.29 -> £3,383,043.57 (10.3%); £3,773,052.56 -> £3,383,043.60 (10.3%); £3,773,052.84 -> £3,383,043.62 (10.3%); £3,773,053.13 -> £3,383,043.78 (10.3%); £3,773,053.34 -> £3,383,043.94 (10.3%); £3,773,053.62 -> £3,383,044.10 (10.3%); £3,773,053.83 -> £3,383,044.25 (10.3%); £3,773,054.04 -> £3,383,044.41 (10.3%); £3,773,054.26 -> £3,383,044.56 (10.3%); £3,773,054.47 -> £3,383,044.73 (10.3%); £3,773,054.75 -> £3,383,044.88 (10.3%); £3,773,055.03 -> £3,383,045.04 (10.3%); £3,773,055.31 -> £3,383,045.20 (10.3%); £3,773,055.58 -> £3,383,045.35 (10.3%); £3,773,055.87 -> £3,383,045.38 (10.3%); £3,773,056.17 -> £3,383,045.40 (10.3%); £3,773,056.42 -> £3,383,045.43 (10.3%); £3,773,056.65 -> £3,383,045.45 (10.3%); £3,773,056.87 -> £3,383,045.47 (10.3%); £3,773,057.04 -> £3,383,045.49 (10.3%); £3,773,057.20 -> £3,383,045.51 (10.3%); £3,773,057.36 -> £3,383,045.52 (10.3%); £3,773,057.54 -> £3,383,045.54 (10.3%); £3,773,057.70 -> £3,383,045.56 (10.3%); £3,773,057.87 -> £3,383,045.58 (10.3%); £3,773,058.04 -> £3,383,045.59 (10.3%); £3,773,058.21 -> £3,383,045.61 (10.3%); £3,773,058.37 -> £3,383,045.63 (10.3%); £3,773,058.55 -> £3,383,045.64 (10.3%); £3,773,058.71 -> £3,383,045.66 (10.3%); £3,773,058.89 -> £3,383,045.83 (10.3%); £3,773,059.06 -> £3,383,046.00 (10.3%); £3,773,059.24 -> £3,383,046.17 (10.3%); £3,773,059.44 -> £3,383,046.35 (10.3%); £3,773,059.66 -> £3,383,046.51 (10.3%); £3,773,059.90 -> £3,383,046.69 (10.3%); £3,773,060.17 -> £3,383,046.86 (10.3%); £3,773,060.45 -> £3,383,047.03 (10.3%); £3,773,060.72 -> £3,383,047.06 (10.3%); £3,773,061.00 -> £3,383,047.08 (10.3%); £3,773,061.28 -> £3,383,047.11 (10.3%); £3,773,061.56 -> £3,383,047.13 (10.3%); £3,773,061.83 -> £3,383,047.15 (10.3%); £3,773,062.11 -> £3,383,047.18 (10.3%); £3,773,062.38 -> £3,383,047.20 (10.3%); £3,773,062.66 -> £3,383,047.22 (10.3%); £3,773,062.94 -> £3,383,047.25 (10.3%); £3,773,063.22 -> £3,383,047.27 (10.3%); £3,773,063.50 -> £3,383,047.29 (10.3%); £3,773,063.77 -> £3,383,047.32 (10.3%); £3,773,064.05 -> £3,383,047.35 (10.3%); £3,773,064.26 -> £3,383,047.52 (10.3%); £3,773,064.54 -> £3,383,047.70 (10.3%); £3,773,064.81 -> £3,383,047.87 (10.3%); £3,773,065.01 -> £3,383,048.05 (10.3%); £3,773,065.28 -> £3,383,048.23 (10.3%); £3,773,065.56 -> £3,383,048.40 (10.3%); £3,773,065.78 -> £3,383,048.57 (10.3%); £3,773,066.07 -> £3,383,048.74 (10.3%); £3,773,066.34 -> £3,383,048.91 (10.3%); £3,773,066.62 -> £3,383,049.08 (10.3%); £3,773,066.90 -> £3,383,049.25 (10.3%); £3,773,067.18 -> £3,383,049.28 (10.3%); £3,773,067.45 -> £3,383,049.31 (10.3%); £3,773,067.71 -> £3,383,049.33 (10.3%); £3,773,067.95 -> £3,383,049.35 (10.3%); £3,773,068.16 -> £3,383,049.37 (10.3%); £3,773,068.33 -> £3,383,049.39 (10.3%); £3,773,068.49 -> £3,383,049.41 (10.3%); £3,773,068.65 -> £3,383,049.43 (10.3%); £3,773,068.81 -> £3,383,049.44 (10.3%); £3,773,068.96 -> £3,383,049.46 (10.3%); £3,773,069.13 -> £3,383,049.48 (10.3%); £3,773,069.29 -> £3,383,049.49 (10.3%); £3,773,069.45 -> £3,383,049.51 (10.3%); £3,773,069.61 -> £3,383,049.53 (10.3%); £3,773,069.78 -> £3,383,049.54 (10.3%); £3,773,069.95 -> £3,383,049.56 (10.3%); £3,773,070.11 -> £3,383,049.74 (10.3%); £3,773,070.26 -> £3,383,049.92 (10.3%); £3,773,070.44 -> £3,383,050.12 (10.3%); £3,773,070.64 -> £3,383,050.31 (10.3%); £3,773,070.85 -> £3,383,050.50 (10.3%); £3,773,071.09 -> £3,383,050.69 (10.3%); £3,773,071.34 -> £3,383,050.87 (10.3%); £3,773,071.62 -> £3,383,051.05 (10.3%); £3,773,071.89 -> £3,383,051.08 (10.3%); £3,773,072.16 -> £3,383,051.10 (10.3%); £3,773,072.43 -> £3,383,051.12 (10.3%); £3,773,072.69 -> £3,383,051.15 (10.3%); £3,773,072.97 -> £3,383,051.17 (10.3%); £3,773,073.24 -> £3,383,051.20 (10.3%); £3,773,073.51 -> £3,383,051.22 (10.3%); £3,773,073.78 -> £3,383,051.25 (10.3%); £3,773,074.04 -> £3,383,051.27 (10.3%); £3,773,074.31 -> £3,383,051.29 (10.3%); £3,773,074.58 -> £3,383,051.32 (10.3%); £3,773,074.84 -> £3,383,051.34 (10.3%); £3,773,075.11 -> £3,383,051.37 (10.3%); £3,773,075.31 -> £3,383,051.55 (10.3%); £3,773,075.51 -> £3,383,051.74 (10.3%); £3,773,075.72 -> £3,383,051.92 (10.3%); £3,773,075.92 -> £3,383,052.12 (10.3%); £3,773,076.19 -> £3,383,052.31 (10.3%); £3,773,076.39 -> £3,383,052.50 (10.3%); £3,773,076.59 -> £3,383,052.68 (10.3%); £3,773,076.86 -> £3,383,052.87 (10.3%); £3,773,077.13 -> £3,383,053.05 (10.3%); £3,773,077.39 -> £3,383,053.24 (10.3%); £3,773,077.66 -> £3,383,053.43 (10.3%); £3,773,077.93 -> £3,383,053.46 (10.3%); £3,773,078.20 -> £3,383,053.49 (10.3%); £3,773,078.45 -> £3,383,053.51 (10.3%); £3,773,078.68 -> £3,383,053.53 (10.3%); £3,773,078.89 -> £3,383,053.55 (10.3%); £3,773,079.03 -> £3,383,053.57 (10.3%); £3,773,079.18 -> £3,383,053.59 (10.3%); £3,773,079.32 -> £3,383,053.61 (10.3%); £3,773,079.47 -> £3,383,053.63 (10.3%); £3,773,079.62 -> £3,383,053.65 (10.3%); £3,773,079.76 -> £3,383,053.66 (10.3%); £3,773,079.90 -> £3,383,053.68 (10.3%); £3,773,080.03 -> £3,383,053.70 (10.3%); £3,773,080.18 -> £3,383,053.71 (10.3%); £3,773,080.31 -> £3,383,053.73 (10.3%); £3,773,080.45 -> £3,383,053.75 (10.3%); £3,773,080.59 -> £3,383,053.97 (10.3%); £3,773,080.73 -> £3,383,054.19 (10.3%); £3,773,080.89 -> £3,383,054.42 (10.3%); £3,773,081.06 -> £3,383,054.65 (10.3%); £3,773,081.25 -> £3,383,054.88 (10.3%); £3,773,081.46 -> £3,383,055.12 (10.3%); £3,773,081.68 -> £3,383,055.35 (10.3%); £3,773,081.92 -> £3,383,055.58 (10.3%); £3,773,082.15 -> £3,383,055.61 (10.3%); £3,773,082.38 -> £3,383,055.63 (10.3%); £3,773,082.62 -> £3,383,055.66 (10.3%); £3,773,082.85 -> £3,383,055.69 (10.3%); £3,773,083.09 -> £3,383,055.71 (10.3%); £3,773,083.33 -> £3,383,055.74 (10.3%); £3,773,083.56 -> £3,383,055.77 (10.3%); £3,773,083.80 -> £3,383,055.79 (10.3%); £3,773,084.05 -> £3,383,055.82 (10.3%); £3,773,084.28 -> £3,383,055.84 (10.3%); £3,773,084.52 -> £3,383,055.87 (10.3%); £3,773,084.76 -> £3,383,055.89 (10.3%); £3,773,085.00 -> £3,383,055.92 (10.3%); £3,773,085.22 -> £3,383,056.14 (10.3%); £3,773,085.40 -> £3,383,056.36 (10.3%); £3,773,085.57 -> £3,383,056.58 (10.3%); £3,773,085.75 -> £3,383,056.80 (10.3%); £3,773,085.92 -> £3,383,057.03 (10.3%); £3,773,086.10 -> £3,383,057.25 (10.3%); £3,773,086.28 -> £3,383,057.48 (10.3%); £3,773,086.52 -> £3,383,057.71 (10.3%); £3,773,086.75 -> £3,383,057.94 (10.3%); £3,773,086.98 -> £3,383,058.16 (10.3%); £3,773,087.21 -> £3,383,058.38 (10.3%); £3,773,087.45 -> £3,383,058.41 (10.3%); £3,773,087.68 -> £3,383,058.44 (10.3%); £3,773,087.90 -> £3,383,058.46 (10.3%); £3,773,088.09 -> £3,383,058.48 (10.3%); £3,773,088.28 -> £3,383,058.51 (10.3%); £3,773,088.42 -> £3,383,058.53 (10.3%); £3,773,088.56 -> £3,383,058.55 (10.3%); £3,773,088.70 -> £3,383,058.56 (10.3%); £3,773,088.84 -> £3,383,058.58 (10.3%); £3,773,088.98 -> £3,383,058.60 (10.3%); £3,773,089.12 -> £3,383,058.62 (10.3%); £3,773,089.26 -> £3,383,058.63 (10.3%); £3,773,089.40 -> £3,383,058.65 (10.3%); £3,773,089.54 -> £3,383,058.67 (10.3%); £3,773,089.67 -> £3,383,058.68 (10.3%); £3,773,089.82 -> £3,383,058.70 (10.3%); £3,773,089.95 -> £3,383,058.92 (10.3%); £3,773,090.09 -> £3,383,059.13 (10.3%); £3,773,090.25 -> £3,383,059.35 (10.3%); £3,773,090.42 -> £3,383,059.56 (10.3%); £3,773,090.61 -> £3,383,059.79 (10.3%); £3,773,090.81 -> £3,383,060.01 (10.3%); £3,773,091.03 -> £3,383,060.23 (10.3%); £3,773,091.27 -> £3,383,060.45 (10.3%); £3,773,091.51 -> £3,383,060.48 (10.3%); £3,773,091.74 -> £3,383,060.51 (10.3%); £3,773,091.97 -> £3,383,060.54 (10.3%); £3,773,092.20 -> £3,383,060.57 (10.3%); £3,773,092.43 -> £3,383,060.60 (10.3%); £3,773,092.66 -> £3,383,060.63 (10.3%); £3,773,092.88 -> £3,383,060.66 (10.3%); £3,773,093.12 -> £3,383,060.69 (10.3%); £3,773,093.35 -> £3,383,060.72 (10.3%); £3,773,093.58 -> £3,383,060.75 (10.3%); £3,773,093.81 -> £3,383,060.77 (10.3%); £3,773,094.04 -> £3,383,060.80 (10.3%); £3,773,094.27 -> £3,383,060.83 (10.3%); £3,773,094.45 -> £3,383,061.05 (10.3%); £3,773,094.63 -> £3,383,061.26 (10.3%); £3,773,094.79 -> £3,383,061.48 (10.3%); £3,773,094.97 -> £3,383,061.71 (10.3%); £3,773,095.20 -> £3,383,061.93 (10.3%); £3,773,095.38 -> £3,383,062.15 (10.3%); £3,773,095.55 -> £3,383,062.38 (10.3%); £3,773,095.79 -> £3,383,062.60 (10.3%); £3,773,096.03 -> £3,383,062.83 (10.3%); £3,773,096.26 -> £3,383,063.04 (10.3%); £3,773,096.49 -> £3,383,063.26 (10.3%); £3,773,096.72 -> £3,383,063.29 (10.3%); £3,773,096.95 -> £3,383,063.32 (10.3%); £3,773,097.17 -> £3,383,063.34 (10.3%); £3,773,097.37 -> £3,383,063.37 (10.3%); £3,773,097.55 -> £3,383,063.39 (10.3%); £3,773,097.71 -> £3,383,063.41 (10.3%); £3,773,097.86 -> £3,383,063.42 (10.3%); £3,773,098.01 -> £3,383,063.44 (10.3%); £3,773,098.17 -> £3,383,063.46 (10.3%); £3,773,098.32 -> £3,383,063.47 (10.3%); £3,773,098.48 -> £3,383,063.49 (10.3%); £3,773,098.63 -> £3,383,063.51 (10.3%); £3,773,098.78 -> £3,383,063.52 (10.3%); £3,773,098.94 -> £3,383,063.54 (10.3%); £3,773,099.09 -> £3,383,063.56 (10.3%); £3,773,099.24 -> £3,383,063.57 (10.3%); £3,773,099.40 -> £3,383,063.78 (10.3%); £3,773,099.55 -> £3,383,063.99 (10.3%); £3,773,099.72 -> £3,383,064.21 (10.3%); £3,773,099.91 -> £3,383,064.42 (10.3%); £3,773,100.11 -> £3,383,064.64 (10.3%); £3,773,100.33 -> £3,383,064.86 (10.3%); £3,773,100.57 -> £3,383,065.08 (10.3%); £3,773,100.82 -> £3,383,065.29 (10.3%); £3,773,101.06 -> £3,383,065.32 (10.3%); £3,773,101.32 -> £3,383,065.34 (10.3%); £3,773,101.58 -> £3,383,065.36 (10.3%); £3,773,101.83 -> £3,383,065.39 (10.3%); £3,773,102.09 -> £3,383,065.41 (10.3%); £3,773,102.35 -> £3,383,065.44 (10.3%); £3,773,102.61 -> £3,383,065.46 (10.3%); £3,773,102.87 -> £3,383,065.48 (10.3%); £3,773,103.12 -> £3,383,065.51 (10.3%); £3,773,103.38 -> £3,383,065.53 (10.3%); £3,773,103.64 -> £3,383,065.55 (10.3%); £3,773,103.90 -> £3,383,065.58 (10.3%); £3,773,104.16 -> £3,383,065.60 (10.3%); £3,773,104.42 -> £3,383,065.82 (10.3%); £3,773,104.68 -> £3,383,066.05 (10.3%); £3,773,104.93 -> £3,383,066.27 (10.3%); £3,773,105.18 -> £3,383,066.50 (10.3%); £3,773,105.43 -> £3,383,066.72 (10.3%); £3,773,105.68 -> £3,383,066.94 (10.3%); £3,773,105.87 -> £3,383,067.15 (10.3%); £3,773,106.12 -> £3,383,067.37 (10.3%); £3,773,106.38 -> £3,383,067.59 (10.3%); £3,773,106.63 -> £3,383,067.81 (10.3%); £3,773,106.88 -> £3,383,068.03 (10.3%); £3,773,107.13 -> £3,383,068.05 (10.3%); £3,773,107.39 -> £3,383,068.08 (10.3%); £3,773,107.63 -> £3,383,068.11 (10.3%); £3,773,107.85 -> £3,383,068.13 (10.3%); £3,773,108.05 -> £3,383,068.15 (10.3%); £3,773,108.20 -> £3,383,068.17 (10.3%); £3,773,108.35 -> £3,383,068.19 (10.3%); £3,773,108.51 -> £3,383,068.20 (10.3%); £3,773,108.66 -> £3,383,068.22 (10.3%); £3,773,108.81 -> £3,383,068.24 (10.3%); £3,773,108.96 -> £3,383,068.25 (10.3%); £3,773,109.12 -> £3,383,068.27 (10.3%); £3,773,109.26 -> £3,383,068.29 (10.3%); £3,773,109.42 -> £3,383,068.30 (10.3%); £3,773,109.57 -> £3,383,068.32 (10.3%); £3,773,109.73 -> £3,383,068.34 (10.3%); £3,773,109.88 -> £3,383,068.54 (10.3%); £3,773,110.03 -> £3,383,068.75 (10.3%); £3,773,110.19 -> £3,383,068.96 (10.3%); £3,773,110.38 -> £3,383,069.17 (10.3%); £3,773,110.58 -> £3,383,069.39 (10.3%); £3,773,110.80 -> £3,383,069.60 (10.3%); £3,773,111.03 -> £3,383,069.81 (10.3%); £3,773,111.28 -> £3,383,070.02 (10.3%); £3,773,111.54 -> £3,383,070.05 (10.3%); £3,773,111.79 -> £3,383,070.07 (10.3%); £3,773,112.04 -> £3,383,070.10 (10.3%); £3,773,112.30 -> £3,383,070.12 (10.3%); £3,773,112.56 -> £3,383,070.14 (10.3%); £3,773,112.82 -> £3,383,070.17 (10.3%); £3,773,113.07 -> £3,383,070.19 (10.3%); £3,773,113.33 -> £3,383,070.22 (10.3%); £3,773,113.58 -> £3,383,070.24 (10.3%); £3,773,113.84 -> £3,383,070.26 (10.3%); £3,773,114.10 -> £3,383,070.29 (10.3%); £3,773,114.35 -> £3,383,070.31 (10.3%); £3,773,114.60 -> £3,383,070.34 (10.3%); £3,773,114.79 -> £3,383,070.54 (10.3%); £3,773,114.97 -> £3,383,070.76 (10.3%); £3,773,115.22 -> £3,383,070.97 (10.3%); £3,773,115.41 -> £3,383,071.18 (10.3%); £3,773,115.60 -> £3,383,071.39 (10.3%); £3,773,115.86 -> £3,383,071.61 (10.3%); £3,773,116.11 -> £3,383,071.82 (10.3%); £3,773,116.37 -> £3,383,072.04 (10.3%); £3,773,116.63 -> £3,383,072.25 (10.3%); £3,773,116.88 -> £3,383,072.46 (10.3%); £3,773,117.14 -> £3,383,072.67 (10.3%); £3,773,117.40 -> £3,383,072.70 (10.3%); £3,773,117.65 -> £3,383,072.72 (10.3%); £3,773,117.88 -> £3,383,072.75 (10.3%); £3,773,118.09 -> £3,383,072.77 (10.3%); £3,773,118.29 -> £3,383,072.79 (10.3%); £3,773,118.44 -> £3,383,072.81 (10.3%); £3,773,118.60 -> £3,383,072.83 (10.3%); £3,773,118.75 -> £3,383,072.84 (10.3%); £3,773,118.90 -> £3,383,072.86 (10.3%); £3,773,119.05 -> £3,383,072.88 (10.3%); £3,773,119.20 -> £3,383,072.89 (10.3%); £3,773,119.35 -> £3,383,072.91 (10.3%); £3,773,119.50 -> £3,383,072.93 (10.3%); £3,773,119.65 -> £3,383,072.94 (10.3%); £3,773,119.80 -> £3,383,072.96 (10.3%); £3,773,119.95 -> £3,383,072.98 (10.3%); £3,773,120.11 -> £3,383,073.16 (10.3%); £3,773,120.26 -> £3,383,073.33 (10.3%); £3,773,120.42 -> £3,383,073.51 (10.3%); £3,773,120.61 -> £3,383,073.69 (10.3%); £3,773,120.80 -> £3,383,073.87 (10.3%); £3,773,121.03 -> £3,383,074.05 (10.3%); £3,773,121.27 -> £3,383,074.22 (10.3%); £3,773,121.52 -> £3,383,074.40 (10.3%); £3,773,121.77 -> £3,383,074.43 (10.3%); £3,773,122.02 -> £3,383,074.45 (10.3%); £3,773,122.27 -> £3,383,074.47 (10.3%); £3,773,122.52 -> £3,383,074.50 (10.3%); £3,773,122.77 -> £3,383,074.52 (10.3%); £3,773,123.03 -> £3,383,074.54 (10.3%); £3,773,123.29 -> £3,383,074.57 (10.3%); £3,773,123.54 -> £3,383,074.59 (10.3%); £3,773,123.79 -> £3,383,074.61 (10.3%); £3,773,124.05 -> £3,383,074.64 (10.3%); £3,773,124.30 -> £3,383,074.66 (10.3%); £3,773,124.55 -> £3,383,074.68 (10.3%); £3,773,124.80 -> £3,383,074.71 (10.3%); £3,773,125.05 -> £3,383,074.89 (10.3%); £3,773,125.24 -> £3,383,075.09 (10.3%); £3,773,125.49 -> £3,383,075.28 (10.3%); £3,773,125.74 -> £3,383,075.47 (10.3%); £3,773,125.94 -> £3,383,075.66 (10.3%); £3,773,126.18 -> £3,383,075.85 (10.3%); £3,773,126.36 -> £3,383,076.03 (10.3%); £3,773,126.62 -> £3,383,076.23 (10.3%); £3,773,126.87 -> £3,383,076.42 (10.3%); £3,773,127.12 -> £3,383,076.60 (10.3%); £3,773,127.37 -> £3,383,076.79 (10.3%); £3,773,127.62 -> £3,383,076.82 (10.3%); £3,773,127.87 -> £3,383,076.85 (10.3%); £3,773,128.10 -> £3,383,076.87 (10.3%); £3,773,128.32 -> £3,383,076.90 (10.3%); £3,773,128.51 -> £3,383,076.92 (10.3%); £3,773,128.66 -> £3,383,076.93 (10.3%); £3,773,128.81 -> £3,383,076.95 (10.3%); £3,773,128.96 -> £3,383,076.97 (10.3%); £3,773,129.11 -> £3,383,076.99 (10.3%); £3,773,129.26 -> £3,383,077.00 (10.3%); £3,773,129.41 -> £3,383,077.02 (10.3%); £3,773,129.56 -> £3,383,077.04 (10.3%); £3,773,129.71 -> £3,383,077.05 (10.3%); £3,773,129.86 -> £3,383,077.07 (10.3%); £3,773,130.01 -> £3,383,077.09 (10.3%); £3,773,130.16 -> £3,383,077.10 (10.3%); £3,773,130.31 -> £3,383,077.27 (10.3%); £3,773,130.46 -> £3,383,077.43 (10.3%); £3,773,130.62 -> £3,383,077.59 (10.3%); £3,773,130.80 -> £3,383,077.75 (10.3%); £3,773,131.00 -> £3,383,077.92 (10.3%); £3,773,131.22 -> £3,383,078.08 (10.3%); £3,773,131.44 -> £3,383,078.25 (10.3%); £3,773,131.70 -> £3,383,078.41 (10.3%); £3,773,131.95 -> £3,383,078.43 (10.3%); £3,773,132.20 -> £3,383,078.45 (10.3%); £3,773,132.45 -> £3,383,078.48 (10.3%); £3,773,132.70 -> £3,383,078.50 (10.3%); £3,773,132.95 -> £3,383,078.52 (10.3%); £3,773,133.19 -> £3,383,078.55 (10.3%); £3,773,133.43 -> £3,383,078.57 (10.3%); £3,773,133.68 -> £3,383,078.60 (10.3%); £3,773,133.92 -> £3,383,078.62 (10.3%); £3,773,134.17 -> £3,383,078.64 (10.3%); £3,773,134.43 -> £3,383,078.67 (10.3%); £3,773,134.68 -> £3,383,078.69 (10.3%); £3,773,134.93 -> £3,383,078.72 (10.3%); £3,773,135.12 -> £3,383,078.89 (10.3%); £3,773,135.30 -> £3,383,079.06 (10.3%); £3,773,135.48 -> £3,383,079.23 (10.3%); £3,773,135.67 -> £3,383,079.40 (10.3%); £3,773,135.85 -> £3,383,079.58 (10.3%); £3,773,136.03 -> £3,383,079.75 (10.3%); £3,773,136.22 -> £3,383,079.92 (10.3%); £3,773,136.47 -> £3,383,080.09 (10.3%); £3,773,136.72 -> £3,383,080.26 (10.3%); £3,773,136.97 -> £3,383,080.43 (10.3%); £3,773,137.22 -> £3,383,080.60 (10.3%); £3,773,137.47 -> £3,383,080.63 (10.3%); £3,773,137.72 -> £3,383,080.66 (10.3%); £3,773,137.95 -> £3,383,080.68 (10.3%); £3,773,138.16 -> £3,383,080.71 (10.3%); £3,773,138.35 -> £3,383,080.73 (10.3%); £3,773,138.50 -> £3,383,080.74 (10.3%); £3,773,138.65 -> £3,383,080.76 (10.3%); £3,773,138.80 -> £3,383,080.78 (10.3%); £3,773,138.94 -> £3,383,080.80 (10.3%); £3,773,139.09 -> £3,383,080.81 (10.3%); £3,773,139.23 -> £3,383,080.83 (10.3%); £3,773,139.38 -> £3,383,080.85 (10.3%); £3,773,139.53 -> £3,383,080.86 (10.3%); £3,773,139.67 -> £3,383,080.88 (10.3%); £3,773,139.83 -> £3,383,080.90 (10.3%); £3,773,139.97 -> £3,383,080.91 (10.3%); £3,773,140.12 -> £3,383,081.09 (10.3%); £3,773,140.27 -> £3,383,081.27 (10.3%); £3,773,140.44 -> £3,383,081.46 (10.3%); £3,773,140.62 -> £3,383,081.64 (10.3%); £3,773,140.81 -> £3,383,081.83 (10.3%); £3,773,141.02 -> £3,383,082.02 (10.3%); £3,773,141.26 -> £3,383,082.20 (10.3%); £3,773,141.50 -> £3,383,082.38 (10.3%); £3,773,141.74 -> £3,383,082.40 (10.3%); £3,773,141.97 -> £3,383,082.42 (10.3%); £3,773,142.22 -> £3,383,082.45 (10.3%); £3,773,142.47 -> £3,383,082.47 (10.3%); £3,773,142.72 -> £3,383,082.49 (10.3%); £3,773,142.97 -> £3,383,082.52 (10.3%); £3,773,143.21 -> £3,383,082.54 (10.3%); £3,773,143.45 -> £3,383,082.56 (10.3%); £3,773,143.69 -> £3,383,082.59 (10.3%); £3,773,143.93 -> £3,383,082.61 (10.3%); £3,773,144.18 -> £3,383,082.63 (10.3%); £3,773,144.42 -> £3,383,082.66 (10.3%); £3,773,144.66 -> £3,383,082.68 (10.3%); £3,773,144.85 -> £3,383,082.87 (10.3%); £3,773,145.04 -> £3,383,083.05 (10.3%); £3,773,145.22 -> £3,383,083.24 (10.3%); £3,773,145.41 -> £3,383,083.43 (10.3%); £3,773,145.59 -> £3,383,083.62 (10.3%); £3,773,145.77 -> £3,383,083.82 (10.3%); £3,773,145.95 -> £3,383,084.01 (10.3%); £3,773,146.20 -> £3,383,084.19 (10.3%); £3,773,146.44 -> £3,383,084.38 (10.3%); £3,773,146.69 -> £3,383,084.57 (10.3%); £3,773,146.93 -> £3,383,084.76 (10.3%); £3,773,147.19 -> £3,383,084.79 (10.3%); £3,773,147.43 -> £3,383,084.81 (10.3%); £3,773,147.67 -> £3,383,084.84 (10.3%); £3,773,147.88 -> £3,383,084.86 (10.3%); £3,773,148.07 -> £3,383,084.88 (10.3%); £3,773,148.20 -> £3,383,084.90 (10.3%); £3,773,148.33 -> £3,383,084.92 (10.3%); £3,773,148.46 -> £3,383,084.94 (10.3%); £3,773,148.59 -> £3,383,084.95 (10.3%); £3,773,148.71 -> £3,383,084.97 (10.3%); £3,773,148.84 -> £3,383,084.99 (10.3%); £3,773,148.97 -> £3,383,085.00 (10.3%); £3,773,149.10 -> £3,383,085.02 (10.3%); £3,773,149.23 -> £3,383,085.04 (10.3%); £3,773,149.35 -> £3,383,085.05 (10.3%); £3,773,149.48 -> £3,383,085.07 (10.3%); £3,773,149.61 -> £3,383,085.24 (10.3%); £3,773,149.74 -> £3,383,085.41 (10.3%); £3,773,149.88 -> £3,383,085.59 (10.3%); £3,773,150.04 -> £3,383,085.76 (10.3%); £3,773,150.21 -> £3,383,085.94 (10.3%); £3,773,150.40 -> £3,383,086.12 (10.3%); £3,773,150.60 -> £3,383,086.30 (10.3%); £3,773,150.81 -> £3,383,086.48 (10.3%); £3,773,151.01 -> £3,383,086.50 (10.3%); £3,773,151.22 -> £3,383,086.53 (10.3%); £3,773,151.43 -> £3,383,086.56 (10.3%); £3,773,151.64 -> £3,383,086.58 (10.3%); £3,773,151.85 -> £3,383,086.61 (10.3%); £3,773,152.07 -> £3,383,086.64 (10.3%); £3,773,152.28 -> £3,383,086.66 (10.3%); £3,773,152.49 -> £3,383,086.69 (10.3%); £3,773,152.71 -> £3,383,086.71 (10.3%); £3,773,152.92 -> £3,383,086.74 (10.3%); £3,773,153.13 -> £3,383,086.76 (10.3%); £3,773,153.35 -> £3,383,086.79 (10.3%); £3,773,153.56 -> £3,383,086.82 (10.3%); £3,773,153.72 -> £3,383,086.99 (10.3%); £3,773,153.88 -> £3,383,087.17 (10.3%); £3,773,154.04 -> £3,383,087.35 (10.3%); £3,773,154.20 -> £3,383,087.53 (10.3%); £3,773,154.36 -> £3,383,087.71 (10.3%); £3,773,154.52 -> £3,383,087.90 (10.3%); £3,773,154.72 -> £3,383,088.09 (10.3%); £3,773,154.94 -> £3,383,088.26 (10.3%); £3,773,155.16 -> £3,383,088.45 (10.3%); £3,773,155.37 -> £3,383,088.63 (10.3%); £3,773,155.58 -> £3,383,088.81 (10.3%); £3,773,155.80 -> £3,383,088.83 (10.3%); £3,773,156.01 -> £3,383,088.86 (10.3%); £3,773,156.20 -> £3,383,088.89 (10.3%); £3,773,156.38 -> £3,383,088.91 (10.3%); £3,773,156.54 -> £3,383,088.93 (10.3%); £3,773,156.67 -> £3,383,088.95 (10.3%); £3,773,156.80 -> £3,383,088.97 (10.3%); £3,773,156.93 -> £3,383,088.99 (10.3%); £3,773,157.05 -> £3,383,089.01 (10.3%); £3,773,157.18 -> £3,383,089.03 (10.3%); £3,773,157.30 -> £3,383,089.04 (10.3%); £3,773,157.43 -> £3,383,089.06 (10.3%); £3,773,157.55 -> £3,383,089.08 (10.3%); £3,773,157.68 -> £3,383,089.09 (10.3%); £3,773,157.81 -> £3,383,089.11 (10.3%); £3,773,157.94 -> £3,383,089.13 (10.3%); £3,773,158.06 -> £3,383,089.34 (10.3%); £3,773,158.18 -> £3,383,089.55 (10.3%); £3,773,158.33 -> £3,383,089.77 (10.3%); £3,773,158.48 -> £3,383,089.99 (10.3%); £3,773,158.66 -> £3,383,090.20 (10.3%); £3,773,158.84 -> £3,383,090.42 (10.3%); £3,773,159.04 -> £3,383,090.64 (10.3%); £3,773,159.24 -> £3,383,090.86 (10.3%); £3,773,159.46 -> £3,383,090.89 (10.3%); £3,773,159.67 -> £3,383,090.92 (10.3%); £3,773,159.87 -> £3,383,090.95 (10.3%); £3,773,160.09 -> £3,383,090.98 (10.3%); £3,773,160.31 -> £3,383,091.01 (10.3%); £3,773,160.52 -> £3,383,091.05 (10.3%); £3,773,160.72 -> £3,383,091.08 (10.3%); £3,773,160.93 -> £3,383,091.10 (10.3%); £3,773,161.15 -> £3,383,091.13 (10.3%); £3,773,161.35 -> £3,383,091.16 (10.3%); £3,773,161.57 -> £3,383,091.19 (10.3%); £3,773,161.78 -> £3,383,091.22 (10.3%); £3,773,161.99 -> £3,383,091.25 (10.3%); £3,773,162.14 -> £3,383,091.46 (10.3%); £3,773,162.31 -> £3,383,091.67 (10.3%); £3,773,162.47 -> £3,383,091.89 (10.3%); £3,773,162.62 -> £3,383,092.12 (10.3%); £3,773,162.79 -> £3,383,092.34 (10.3%); £3,773,162.95 -> £3,383,092.55 (10.3%); £3,773,163.11 -> £3,383,092.77 (10.3%); £3,773,163.32 -> £3,383,092.98 (10.3%); £3,773,163.54 -> £3,383,093.21 (10.3%); £3,773,163.75 -> £3,383,093.43 (10.3%); £3,773,163.96 -> £3,383,093.65 (10.3%); £3,773,164.17 -> £3,383,093.68 (10.3%); £3,773,164.38 -> £3,383,093.71 (10.3%); £3,773,164.57 -> £3,383,093.73 (10.3%); £3,773,164.76 -> £3,383,093.75 (10.3%); £3,773,164.92 -> £3,383,093.77 (10.3%); £3,773,165.07 -> £3,383,093.79 (10.3%); £3,773,165.22 -> £3,383,093.81 (10.3%); £3,773,165.36 -> £3,383,093.83 (10.3%); £3,773,165.51 -> £3,383,093.84 (10.3%); £3,773,165.66 -> £3,383,093.86 (10.3%); £3,773,165.80 -> £3,383,093.88 (10.3%); £3,773,165.94 -> £3,383,093.89 (10.3%); £3,773,166.09 -> £3,383,093.91 (10.3%); £3,773,166.24 -> £3,383,093.93 (10.3%); £3,773,166.39 -> £3,383,093.94 (10.3%); £3,773,166.53 -> £3,383,093.96 (10.3%); £3,773,166.67 -> £3,383,094.21 (10.3%); £3,773,166.81 -> £3,383,094.46 (10.3%); £3,773,166.97 -> £3,383,094.71 (10.3%); £3,773,167.15 -> £3,383,094.97 (10.3%); £3,773,167.33 -> £3,383,095.23 (10.3%); £3,773,167.54 -> £3,383,095.49 (10.3%); £3,773,167.77 -> £3,383,095.74 (10.3%); £3,773,168.00 -> £3,383,095.99 (10.3%); £3,773,168.24 -> £3,383,096.01 (10.3%); £3,773,168.49 -> £3,383,096.04 (10.3%); £3,773,168.73 -> £3,383,096.06 (10.3%); £3,773,168.98 -> £3,383,096.09 (10.3%); £3,773,169.23 -> £3,383,096.11 (10.3%); £3,773,169.46 -> £3,383,096.14 (10.3%); £3,773,169.71 -> £3,383,096.16 (10.3%); £3,773,169.95 -> £3,383,096.18 (10.3%); £3,773,170.19 -> £3,383,096.21 (10.3%); £3,773,170.43 -> £3,383,096.23 (10.3%); £3,773,170.68 -> £3,383,096.25 (10.3%); £3,773,170.92 -> £3,383,096.28 (10.3%); £3,773,171.16 -> £3,383,096.31 (10.3%); £3,773,171.34 -> £3,383,096.55 (10.3%); £3,773,171.53 -> £3,383,096.80 (10.3%); £3,773,171.71 -> £3,383,097.05 (10.3%); £3,773,171.89 -> £3,383,097.30 (10.3%); £3,773,172.08 -> £3,383,097.55 (10.3%); £3,773,172.25 -> £3,383,097.81 (10.3%); £3,773,172.43 -> £3,383,098.07 (10.3%); £3,773,172.67 -> £3,383,098.31 (10.3%); £3,773,172.91 -> £3,383,098.57 (10.3%); £3,773,173.14 -> £3,383,098.83 (10.3%); £3,773,173.39 -> £3,383,099.08 (10.3%); £3,773,173.63 -> £3,383,099.11 (10.3%); £3,773,173.87 -> £3,383,099.14 (10.3%); £3,773,174.10 -> £3,383,099.16 (10.3%); £3,773,174.30 -> £3,383,099.19 (10.3%); £3,773,174.49 -> £3,383,099.21 (10.3%); £3,773,174.64 -> £3,383,099.22 (10.3%); £3,773,174.78 -> £3,383,099.24 (10.3%); £3,773,174.92 -> £3,383,099.26 (10.3%); £3,773,175.07 -> £3,383,099.28 (10.3%); £3,773,175.21 -> £3,383,099.29 (10.3%); £3,773,175.35 -> £3,383,099.31 (10.3%); £3,773,175.48 -> £3,383,099.33 (10.3%); £3,773,175.63 -> £3,383,099.34 (10.3%); £3,773,175.77 -> £3,383,099.36 (10.3%); £3,773,175.92 -> £3,383,099.38 (10.3%); £3,773,176.06 -> £3,383,099.39 (10.3%); £3,773,176.21 -> £3,383,099.62 (10.3%); £3,773,176.35 -> £3,383,099.84 (10.3%); £3,773,176.51 -> £3,383,100.07 (10.3%); £3,773,176.69 -> £3,383,100.29 (10.3%); £3,773,176.88 -> £3,383,100.51 (10.3%); £3,773,177.09 -> £3,383,100.74 (10.3%); £3,773,177.32 -> £3,383,100.96 (10.3%); £3,773,177.56 -> £3,383,101.18 (10.3%); £3,773,177.80 -> £3,383,101.21 (10.3%); £3,773,178.04 -> £3,383,101.23 (10.3%); £3,773,178.27 -> £3,383,101.25 (10.3%); £3,773,178.51 -> £3,383,101.28 (10.3%); £3,773,178.75 -> £3,383,101.30 (10.3%); £3,773,178.99 -> £3,383,101.33 (10.3%); £3,773,179.23 -> £3,383,101.35 (10.3%); £3,773,179.46 -> £3,383,101.37 (10.3%); £3,773,179.70 -> £3,383,101.40 (10.3%); £3,773,179.93 -> £3,383,101.42 (10.3%); £3,773,180.16 -> £3,383,101.44 (10.3%); £3,773,180.40 -> £3,383,101.47 (10.3%); £3,773,180.64 -> £3,383,101.50 (10.3%); £3,773,180.83 -> £3,383,101.72 (10.3%); £3,773,181.01 -> £3,383,101.96 (10.3%); £3,773,181.20 -> £3,383,102.19 (10.3%); £3,773,181.45 -> £3,383,102.43 (10.3%); £3,773,181.69 -> £3,383,102.67 (10.3%); £3,773,181.94 -> £3,383,102.91 (10.3%); £3,773,182.12 -> £3,383,103.14 (10.3%); £3,773,182.36 -> £3,383,103.37 (10.3%); £3,773,182.59 -> £3,383,103.60 (10.3%); £3,773,182.84 -> £3,383,103.82 (10.3%); £3,773,183.07 -> £3,383,104.04 (10.3%); £3,773,183.32 -> £3,383,104.07 (10.3%); £3,773,183.56 -> £3,383,104.09 (10.3%); £3,773,183.78 -> £3,383,104.12 (10.3%); £3,773,183.98 -> £3,383,104.14 (10.3%); £3,773,184.17 -> £3,383,104.16 (10.3%); £3,773,184.31 -> £3,383,104.18 (10.3%); £3,773,184.45 -> £3,383,104.20 (10.3%); £3,773,184.59 -> £3,383,104.22 (10.3%); £3,773,184.73 -> £3,383,104.23 (10.3%); £3,773,184.87 -> £3,383,104.25 (10.3%); £3,773,185.01 -> £3,383,104.27 (10.3%); £3,773,185.15 -> £3,383,104.28 (10.3%); £3,773,185.30 -> £3,383,104.30 (10.3%); £3,773,185.44 -> £3,383,104.32 (10.3%); £3,773,185.58 -> £3,383,104.33 (10.3%); £3,773,185.72 -> £3,383,104.35 (10.3%); £3,773,185.86 -> £3,383,104.59 (10.3%); £3,773,186.00 -> £3,383,104.84 (10.3%); £3,773,186.16 -> £3,383,105.09 (10.3%); £3,773,186.33 -> £3,383,105.34 (10.3%); £3,773,186.52 -> £3,383,105.58 (10.3%); £3,773,186.73 -> £3,383,105.83 (10.3%); £3,773,186.94 -> £3,383,106.08 (10.3%); £3,773,187.18 -> £3,383,106.33 (10.3%); £3,773,187.42 -> £3,383,106.36 (10.3%); £3,773,187.65 -> £3,383,106.38 (10.3%); £3,773,187.90 -> £3,383,106.40 (10.3%); £3,773,188.13 -> £3,383,106.43 (10.3%); £3,773,188.36 -> £3,383,106.45 (10.3%); £3,773,188.60 -> £3,383,106.47 (10.3%); £3,773,188.84 -> £3,383,106.50 (10.3%); £3,773,189.08 -> £3,383,106.52 (10.3%); £3,773,189.32 -> £3,383,106.54 (10.3%); £3,773,189.56 -> £3,383,106.57 (10.3%); £3,773,189.80 -> £3,383,106.59 (10.3%); £3,773,190.03 -> £3,383,106.62 (10.3%); £3,773,190.27 -> £3,383,106.64 (10.3%); £3,773,190.44 -> £3,383,106.88 (10.3%); £3,773,190.62 -> £3,383,107.13 (10.3%); £3,773,190.86 -> £3,383,107.38 (10.3%); £3,773,191.10 -> £3,383,107.64 (10.3%); £3,773,191.34 -> £3,383,107.89 (10.3%); £3,773,191.58 -> £3,383,108.14 (10.3%); £3,773,191.82 -> £3,383,108.39 (10.3%); £3,773,192.06 -> £3,383,108.64 (10.3%); £3,773,192.30 -> £3,383,108.88 (10.3%); £3,773,192.53 -> £3,383,109.12 (10.3%); £3,773,192.78 -> £3,383,109.35 (10.3%); £3,773,193.00 -> £3,383,109.38 (10.3%); £3,773,193.24 -> £3,383,109.41 (10.3%); £3,773,193.45 -> £3,383,109.43 (10.3%); £3,773,193.64 -> £3,383,109.46 (10.3%); £3,773,193.82 -> £3,383,109.48 (10.3%); £3,773,193.96 -> £3,383,109.49 (10.3%); £3,773,194.11 -> £3,383,109.51 (10.3%); £3,773,194.25 -> £3,383,109.53 (10.3%); £3,773,194.39 -> £3,383,109.55 (10.3%); £3,773,194.53 -> £3,383,109.56 (10.3%); £3,773,194.67 -> £3,383,109.58 (10.3%); £3,773,194.81 -> £3,383,109.60 (10.3%); £3,773,194.95 -> £3,383,109.61 (10.3%); £3,773,195.10 -> £3,383,109.63 (10.3%); £3,773,195.25 -> £3,383,109.65 (10.3%); £3,773,195.39 -> £3,383,109.66 (10.3%); £3,773,195.54 -> £3,383,109.93 (10.3%); £3,773,195.68 -> £3,383,110.20 (10.3%); £3,773,195.83 -> £3,383,110.47 (10.3%); £3,773,196.00 -> £3,383,110.74 (10.3%); £3,773,196.20 -> £3,383,111.01 (10.3%); £3,773,196.40 -> £3,383,111.28 (10.3%); £3,773,196.62 -> £3,383,111.55 (10.3%); £3,773,196.85 -> £3,383,111.82 (10.3%); £3,773,197.09 -> £3,383,111.85 (10.3%); £3,773,197.32 -> £3,383,111.87 (10.3%); £3,773,197.55 -> £3,383,111.89 (10.3%); £3,773,197.78 -> £3,383,111.92 (10.3%); £3,773,198.01 -> £3,383,111.94 (10.3%); £3,773,198.26 -> £3,383,111.97 (10.3%); £3,773,198.50 -> £3,383,111.99 (10.3%); £3,773,198.73 -> £3,383,112.01 (10.3%); £3,773,198.97 -> £3,383,112.03 (10.3%); £3,773,199.20 -> £3,383,112.06 (10.3%); £3,773,199.44 -> £3,383,112.08 (10.3%); £3,773,199.67 -> £3,383,112.11 (10.3%); £3,773,199.91 -> £3,383,112.14 (10.3%); £3,773,200.09 -> £3,383,112.40 (10.3%); £3,773,200.27 -> £3,383,112.68 (10.3%); £3,773,200.45 -> £3,383,112.95 (10.3%); £3,773,200.62 -> £3,383,113.23 (10.3%); £3,773,200.80 -> £3,383,113.50 (10.3%); £3,773,200.97 -> £3,383,113.77 (10.3%); £3,773,201.15 -> £3,383,114.05 (10.3%); £3,773,201.38 -> £3,383,114.31 (10.3%); £3,773,201.61 -> £3,383,114.58 (10.3%); £3,773,201.85 -> £3,383,114.86 (10.3%); £3,773,202.07 -> £3,383,115.13 (10.3%); £3,773,202.31 -> £3,383,115.16 (10.3%); £3,773,202.55 -> £3,383,115.19 (10.3%); £3,773,202.78 -> £3,383,115.21 (10.3%); £3,773,202.98 -> £3,383,115.23 (10.3%); £3,773,203.17 -> £3,383,115.25 (10.3%); £3,773,203.31 -> £3,383,115.27 (10.3%); £3,773,203.46 -> £3,383,115.29 (10.3%); £3,773,203.60 -> £3,383,115.31 (10.3%); £3,773,203.74 -> £3,383,115.32 (10.3%); £3,773,203.89 -> £3,383,115.34 (10.3%); £3,773,204.03 -> £3,383,115.36 (10.3%); £3,773,204.17 -> £3,383,115.37 (10.3%); £3,773,204.32 -> £3,383,115.39 (10.3%); £3,773,204.46 -> £3,383,115.41 (10.3%); £3,773,204.60 -> £3,383,115.42 (10.3%); £3,773,204.75 -> £3,383,115.44 (10.3%); £3,773,204.89 -> £3,383,115.67 (10.3%); £3,773,205.03 -> £3,383,115.89 (10.3%); £3,773,205.20 -> £3,383,116.12 (10.3%); £3,773,205.37 -> £3,383,116.36 (10.3%); £3,773,205.56 -> £3,383,116.59 (10.3%); £3,773,205.77 -> £3,383,116.82 (10.3%); £3,773,205.99 -> £3,383,117.05 (10.3%); £3,773,206.22 -> £3,383,117.28 (10.3%); £3,773,206.46 -> £3,383,117.31 (10.3%); £3,773,206.69 -> £3,383,117.33 (10.3%); £3,773,206.92 -> £3,383,117.35 (10.3%); £3,773,207.17 -> £3,383,117.38 (10.3%); £3,773,207.41 -> £3,383,117.40 (10.3%); £3,773,207.65 -> £3,383,117.43 (10.3%); £3,773,207.89 -> £3,383,117.45 (10.3%); £3,773,208.13 -> £3,383,117.48 (10.3%); £3,773,208.36 -> £3,383,117.50 (10.3%); £3,773,208.59 -> £3,383,117.52 (10.3%); £3,773,208.83 -> £3,383,117.55 (10.3%); £3,773,209.08 -> £3,383,117.57 (10.3%); £3,773,209.31 -> £3,383,117.60 (10.3%); £3,773,209.55 -> £3,383,117.83 (10.3%); £3,773,209.72 -> £3,383,118.06 (10.3%); £3,773,209.90 -> £3,383,118.30 (10.3%); £3,773,210.08 -> £3,383,118.53 (10.3%); £3,773,210.26 -> £3,383,118.77 (10.3%); £3,773,210.50 -> £3,383,119.01 (10.3%); £3,773,210.75 -> £3,383,119.25 (10.3%); £3,773,210.99 -> £3,383,119.48 (10.3%); £3,773,211.23 -> £3,383,119.72 (10.3%); £3,773,211.48 -> £3,383,119.95 (10.3%); £3,773,211.72 -> £3,383,120.18 (10.3%); £3,773,211.96 -> £3,383,120.21 (10.3%); £3,773,212.20 -> £3,383,120.23 (10.3%); £3,773,212.42 -> £3,383,120.26 (10.3%); £3,773,212.62 -> £3,383,120.28 (10.3%); £3,773,212.81 -> £3,383,120.30 (10.3%); £3,773,212.94 -> £3,383,120.32 (10.3%); £3,773,213.07 -> £3,383,120.34 (10.3%); £3,773,213.20 -> £3,383,120.36 (10.3%); £3,773,213.33 -> £3,383,120.38 (10.3%); £3,773,213.46 -> £3,383,120.39 (10.3%); £3,773,213.58 -> £3,383,120.41 (10.3%); £3,773,213.71 -> £3,383,120.43 (10.3%); £3,773,213.84 -> £3,383,120.44 (10.3%); £3,773,213.96 -> £3,383,120.46 (10.3%); £3,773,214.09 -> £3,383,120.48 (10.3%); £3,773,214.22 -> £3,383,120.49 (10.3%); £3,773,214.35 -> £3,383,120.67 (10.3%); £3,773,214.48 -> £3,383,120.84 (10.3%); £3,773,214.63 -> £3,383,121.02 (10.3%); £3,773,214.79 -> £3,383,121.21 (10.3%); £3,773,214.96 -> £3,383,121.39 (10.3%); £3,773,215.15 -> £3,383,121.57 (10.3%); £3,773,215.35 -> £3,383,121.76 (10.3%); £3,773,215.56 -> £3,383,121.94 (10.3%); £3,773,215.78 -> £3,383,121.97 (10.3%); £3,773,215.99 -> £3,383,122.00 (10.3%); £3,773,216.20 -> £3,383,122.02 (10.3%); £3,773,216.41 -> £3,383,122.05 (10.3%); £3,773,216.63 -> £3,383,122.08 (10.3%); £3,773,216.84 -> £3,383,122.10 (10.3%); £3,773,217.05 -> £3,383,122.13 (10.3%); £3,773,217.27 -> £3,383,122.15 (10.3%); £3,773,217.49 -> £3,383,122.18 (10.3%); £3,773,217.70 -> £3,383,122.20 (10.3%); £3,773,217.92 -> £3,383,122.23 (10.3%); £3,773,218.12 -> £3,383,122.26 (10.3%); £3,773,218.34 -> £3,383,122.28 (10.3%); £3,773,218.51 -> £3,383,122.46 (10.3%); £3,773,218.67 -> £3,383,122.65 (10.3%); £3,773,218.83 -> £3,383,122.84 (10.3%); £3,773,218.99 -> £3,383,123.03 (10.3%); £3,773,219.16 -> £3,383,123.22 (10.3%); £3,773,219.32 -> £3,383,123.41 (10.3%); £3,773,219.48 -> £3,383,123.59 (10.3%); £3,773,219.70 -> £3,383,123.78 (10.3%); £3,773,219.91 -> £3,383,123.96 (10.3%); £3,773,220.12 -> £3,383,124.14 (10.3%); £3,773,220.34 -> £3,383,124.33 (10.3%); £3,773,220.55 -> £3,383,124.35 (10.3%); £3,773,220.77 -> £3,383,124.38 (10.3%); £3,773,220.97 -> £3,383,124.41 (10.3%); £3,773,221.15 -> £3,383,124.43 (10.3%); £3,773,221.32 -> £3,383,124.45 (10.3%); £3,773,221.45 -> £3,383,124.47 (10.3%); £3,773,221.57 -> £3,383,124.49 (10.3%); £3,773,221.70 -> £3,383,124.51 (10.3%); £3,773,221.84 -> £3,383,124.53 (10.3%); £3,773,221.97 -> £3,383,124.55 (10.3%); £3,773,222.09 -> £3,383,124.56 (10.3%); £3,773,222.22 -> £3,383,124.58 (10.3%); £3,773,222.34 -> £3,383,124.60 (10.3%); £3,773,222.47 -> £3,383,124.61 (10.3%); £3,773,222.60 -> £3,383,124.63 (10.3%); £3,773,222.73 -> £3,383,124.65 (10.3%); £3,773,222.86 -> £3,383,124.76 (10.3%); £3,773,222.99 -> £3,383,124.87 (10.3%); £3,773,223.14 -> £3,383,124.98 (10.3%); £3,773,223.30 -> £3,383,125.10 (10.3%); £3,773,223.46 -> £3,383,125.22 (10.3%); £3,773,223.65 -> £3,383,125.34 (10.3%); £3,773,223.85 -> £3,383,125.47 (10.3%); £3,773,224.07 -> £3,383,125.59 (10.3%); £3,773,224.29 -> £3,383,125.62 (10.3%); £3,773,224.51 -> £3,383,125.65 (10.3%); £3,773,224.72 -> £3,383,125.68 (10.3%); £3,773,224.93 -> £3,383,125.71 (10.3%); £3,773,225.14 -> £3,383,125.74 (10.3%); £3,773,225.36 -> £3,383,125.78 (10.3%); £3,773,225.58 -> £3,383,125.81 (10.3%); £3,773,225.79 -> £3,383,125.84 (10.3%); £3,773,226.00 -> £3,383,125.86 (10.3%); £3,773,226.22 -> £3,383,125.89 (10.3%); £3,773,226.43 -> £3,383,125.92 (10.3%); £3,773,226.66 -> £3,383,125.95 (10.3%); £3,773,226.88 -> £3,383,125.98 (10.3%); £3,773,227.03 -> £3,383,126.11 (10.3%); £3,773,227.19 -> £3,383,126.24 (10.3%); £3,773,227.35 -> £3,383,126.37 (10.3%); £3,773,227.51 -> £3,383,126.50 (10.3%); £3,773,227.67 -> £3,383,126.63 (10.3%); £3,773,227.83 -> £3,383,126.77 (10.3%); £3,773,227.99 -> £3,383,126.90 (10.3%); £3,773,228.21 -> £3,383,127.02 (10.3%); £3,773,228.42 -> £3,383,127.15 (10.3%); £3,773,228.64 -> £3,383,127.28 (10.3%); £3,773,228.85 -> £3,383,127.40 (10.3%); £3,773,229.06 -> £3,383,127.43 (10.3%); £3,773,229.28 -> £3,383,127.46 (10.3%); £3,773,229.47 -> £3,383,127.48 (10.3%); £3,773,229.65 -> £3,383,127.50 (10.3%); £3,773,229.81 -> £3,383,127.52 (10.3%); £3,773,229.96 -> £3,383,127.54 (10.3%); £3,773,230.11 -> £3,383,127.56 (10.3%); £3,773,230.26 -> £3,383,127.58 (10.3%); £3,773,230.40 -> £3,383,127.59 (10.3%); £3,773,230.55 -> £3,383,127.61 (10.3%); £3,773,230.70 -> £3,383,127.63 (10.3%); £3,773,230.84 -> £3,383,127.64 (10.3%); £3,773,230.99 -> £3,383,127.66 (10.3%); £3,773,231.13 -> £3,383,127.68 (10.3%); £3,773,231.28 -> £3,383,127.69 (10.3%); £3,773,231.42 -> £3,383,127.71 (10.3%); £3,773,231.57 -> £3,383,127.84 (10.3%); £3,773,231.71 -> £3,383,127.97 (10.3%); £3,773,231.88 -> £3,383,128.11 (10.3%); £3,773,232.06 -> £3,383,128.25 (10.3%); £3,773,232.25 -> £3,383,128.39 (10.3%); £3,773,232.47 -> £3,383,128.52 (10.3%); £3,773,232.70 -> £3,383,128.66 (10.3%); £3,773,232.95 -> £3,383,128.79 (10.3%); £3,773,233.20 -> £3,383,128.82 (10.3%); £3,773,233.45 -> £3,383,128.84 (10.3%); £3,773,233.70 -> £3,383,128.86 (10.3%); £3,773,233.94 -> £3,383,128.89 (10.3%); £3,773,234.19 -> £3,383,128.91 (10.3%); £3,773,234.44 -> £3,383,128.94 (10.3%); £3,773,234.69 -> £3,383,128.96 (10.3%); £3,773,234.94 -> £3,383,128.98 (10.3%); £3,773,235.19 -> £3,383,129.01 (10.3%); £3,773,235.44 -> £3,383,129.03 (10.3%); £3,773,235.69 -> £3,383,129.05 (10.3%); £3,773,235.93 -> £3,383,129.08 (10.3%); £3,773,236.18 -> £3,383,129.11 (10.3%); £3,773,236.43 -> £3,383,129.25 (10.3%); £3,773,236.61 -> £3,383,129.40 (10.3%); £3,773,236.79 -> £3,383,129.55 (10.3%); £3,773,236.98 -> £3,383,129.70 (10.3%); £3,773,237.16 -> £3,383,129.84 (10.3%); £3,773,237.34 -> £3,383,129.99 (10.3%); £3,773,237.52 -> £3,383,130.14 (10.3%); £3,773,237.76 -> £3,383,130.29 (10.3%); £3,773,238.01 -> £3,383,130.43 (10.3%); £3,773,238.26 -> £3,383,130.57 (10.3%); £3,773,238.50 -> £3,383,130.72 (10.3%); £3,773,238.75 -> £3,383,130.75 (10.3%); £3,773,238.99 -> £3,383,130.78 (10.3%); £3,773,239.22 -> £3,383,130.80 (10.3%); £3,773,239.43 -> £3,383,130.82 (10.3%); £3,773,239.62 -> £3,383,130.84 (10.3%); £3,773,239.77 -> £3,383,130.86 (10.3%); £3,773,239.92 -> £3,383,130.88 (10.3%); £3,773,240.06 -> £3,383,130.90 (10.3%); £3,773,240.21 -> £3,383,130.92 (10.3%); £3,773,240.36 -> £3,383,130.93 (10.3%); £3,773,240.51 -> £3,383,130.95 (10.3%); £3,773,240.66 -> £3,383,130.97 (10.3%); £3,773,240.80 -> £3,383,130.98 (10.3%); £3,773,240.95 -> £3,383,131.00 (10.3%); £3,773,241.10 -> £3,383,131.02 (10.3%); £3,773,241.25 -> £3,383,131.03 (10.3%); £3,773,241.40 -> £3,383,131.15 (10.3%); £3,773,241.54 -> £3,383,131.27 (10.3%); £3,773,241.71 -> £3,383,131.40 (10.3%); £3,773,241.89 -> £3,383,131.53 (10.3%); £3,773,242.09 -> £3,383,131.66 (10.3%); £3,773,242.31 -> £3,383,131.79 (10.3%); £3,773,242.54 -> £3,383,131.91 (10.3%); £3,773,242.78 -> £3,383,132.04 (10.3%); £3,773,243.03 -> £3,383,132.06 (10.3%); £3,773,243.28 -> £3,383,132.09 (10.3%); £3,773,243.52 -> £3,383,132.11 (10.3%); £3,773,243.77 -> £3,383,132.13 (10.3%); £3,773,244.02 -> £3,383,132.16 (10.3%); £3,773,244.26 -> £3,383,132.18 (10.3%); £3,773,244.51 -> £3,383,132.21 (10.3%); £3,773,244.76 -> £3,383,132.23 (10.3%); £3,773,245.00 -> £3,383,132.25 (10.3%); £3,773,245.24 -> £3,383,132.28 (10.3%); £3,773,245.49 -> £3,383,132.30 (10.3%); £3,773,245.74 -> £3,383,132.33 (10.3%); £3,773,245.98 -> £3,383,132.35 (10.3%); £3,773,246.17 -> £3,383,132.49 (10.3%); £3,773,246.35 -> £3,383,132.63 (10.3%); £3,773,246.61 -> £3,383,132.77 (10.3%); £3,773,246.86 -> £3,383,132.91 (10.3%); £3,773,247.10 -> £3,383,133.06 (10.3%); £3,773,247.35 -> £3,383,133.19 (10.3%); £3,773,247.53 -> £3,383,133.33 (10.3%); £3,773,247.79 -> £3,383,133.46 (10.3%); £3,773,248.03 -> £3,383,133.60 (10.3%); £3,773,248.28 -> £3,383,133.73 (10.3%); £3,773,248.53 -> £3,383,133.86 (10.3%); £3,773,248.78 -> £3,383,133.89 (10.3%); £3,773,249.03 -> £3,383,133.92 (10.3%); £3,773,249.26 -> £3,383,133.94 (10.3%); £3,773,249.47 -> £3,383,133.97 (10.3%); £3,773,249.66 -> £3,383,133.99 (10.3%); £3,773,249.81 -> £3,383,134.00 (10.3%); £3,773,249.95 -> £3,383,134.02 (10.3%); £3,773,250.10 -> £3,383,134.04 (10.3%); £3,773,250.26 -> £3,383,134.06 (10.3%); £3,773,250.40 -> £3,383,134.07 (10.3%); £3,773,250.55 -> £3,383,134.09 (10.3%); £3,773,250.70 -> £3,383,134.11 (10.3%); £3,773,250.84 -> £3,383,134.13 (10.3%); £3,773,250.99 -> £3,383,134.14 (10.3%); £3,773,251.14 -> £3,383,134.16 (10.3%); £3,773,251.30 -> £3,383,134.18 (10.3%); £3,773,251.45 -> £3,383,134.30 (10.3%); £3,773,251.60 -> £3,383,134.43 (10.3%); £3,773,251.77 -> £3,383,134.56 (10.3%); £3,773,251.96 -> £3,383,134.69 (10.3%); £3,773,252.15 -> £3,383,134.83 (10.3%); £3,773,252.37 -> £3,383,134.96 (10.3%); £3,773,252.60 -> £3,383,135.09 (10.3%); £3,773,252.85 -> £3,383,135.22 (10.3%); £3,773,253.10 -> £3,383,135.25 (10.3%); £3,773,253.35 -> £3,383,135.27 (10.3%); £3,773,253.60 -> £3,383,135.29 (10.3%); £3,773,253.86 -> £3,383,135.32 (10.3%); £3,773,254.10 -> £3,383,135.34 (10.3%); £3,773,254.36 -> £3,383,135.37 (10.3%); £3,773,254.60 -> £3,383,135.39 (10.3%); £3,773,254.86 -> £3,383,135.42 (10.3%); £3,773,255.12 -> £3,383,135.44 (10.3%); £3,773,255.38 -> £3,383,135.46 (10.3%); £3,773,255.63 -> £3,383,135.49 (10.3%); £3,773,255.88 -> £3,383,135.51 (10.3%); £3,773,256.13 -> £3,383,135.54 (10.3%); £3,773,256.38 -> £3,383,135.68 (10.3%); £3,773,256.57 -> £3,383,135.83 (10.3%); £3,773,256.75 -> £3,383,135.98 (10.3%); £3,773,257.00 -> £3,383,136.13 (10.3%); £3,773,257.26 -> £3,383,136.28 (10.3%); £3,773,257.51 -> £3,383,136.42 (10.3%); £3,773,257.70 -> £3,383,136.57 (10.3%); £3,773,257.96 -> £3,383,136.71 (10.3%); £3,773,258.21 -> £3,383,136.86 (10.3%); £3,773,258.46 -> £3,383,137.00 (10.3%); £3,773,258.71 -> £3,383,137.14 (10.3%); £3,773,258.97 -> £3,383,137.17 (10.3%); £3,773,259.22 -> £3,383,137.20 (10.3%); £3,773,259.45 -> £3,383,137.22 (10.3%); £3,773,259.67 -> £3,383,137.24 (10.3%); £3,773,259.86 -> £3,383,137.26 (10.3%); £3,773,260.01 -> £3,383,137.28 (10.3%); £3,773,260.17 -> £3,383,137.30 (10.3%); £3,773,260.33 -> £3,383,137.32 (10.3%); £3,773,260.48 -> £3,383,137.33 (10.3%); £3,773,260.64 -> £3,383,137.35 (10.3%); £3,773,260.79 -> £3,383,137.37 (10.3%); £3,773,260.95 -> £3,383,137.38 (10.3%); £3,773,261.10 -> £3,383,137.40 (10.3%); £3,773,261.26 -> £3,383,137.42 (10.3%); £3,773,261.40 -> £3,383,137.43 (10.3%); £3,773,261.56 -> £3,383,137.45 (10.3%); £3,773,261.71 -> £3,383,137.57 (10.3%); £3,773,261.87 -> £3,383,137.68 (10.3%); £3,773,262.04 -> £3,383,137.81 (10.3%); £3,773,262.23 -> £3,383,137.93 (10.3%); £3,773,262.43 -> £3,383,138.06 (10.3%); £3,773,262.65 -> £3,383,138.18 (10.3%); £3,773,262.88 -> £3,383,138.30 (10.3%); £3,773,263.13 -> £3,383,138.43 (10.3%); £3,773,263.39 -> £3,383,138.45 (10.3%); £3,773,263.65 -> £3,383,138.48 (10.3%); £3,773,263.89 -> £3,383,138.50 (10.3%); £3,773,264.15 -> £3,383,138.52 (10.3%); £3,773,264.40 -> £3,383,138.55 (10.3%); £3,773,264.66 -> £3,383,138.57 (10.3%); £3,773,264.92 -> £3,383,138.60 (10.3%); £3,773,265.17 -> £3,383,138.62 (10.3%); £3,773,265.44 -> £3,383,138.65 (10.3%); £3,773,265.69 -> £3,383,138.67 (10.3%); £3,773,265.94 -> £3,383,138.69 (10.3%); £3,773,266.20 -> £3,383,138.72 (10.3%); £3,773,266.46 -> £3,383,138.75 (10.3%); £3,773,266.65 -> £3,383,138.88 (10.3%); £3,773,266.84 -> £3,383,139.01 (10.3%); £3,773,267.03 -> £3,383,139.15 (10.3%); £3,773,267.22 -> £3,383,139.29 (10.3%); £3,773,267.47 -> £3,383,139.43 (10.3%); £3,773,267.72 -> £3,383,139.56 (10.3%); £3,773,267.92 -> £3,383,139.69 (10.3%); £3,773,268.18 -> £3,383,139.82 (10.3%); £3,773,268.44 -> £3,383,139.95 (10.3%); £3,773,268.70 -> £3,383,140.08 (10.3%); £3,773,268.95 -> £3,383,140.21 (10.3%); £3,773,269.20 -> £3,383,140.24 (10.3%); £3,773,269.46 -> £3,383,140.27 (10.3%); £3,773,269.70 -> £3,383,140.29 (10.3%); £3,773,269.91 -> £3,383,140.32 (10.3%); £3,773,270.12 -> £3,383,140.34 (10.3%); £3,773,270.27 -> £3,383,140.36 (10.3%); £3,773,270.42 -> £3,383,140.37 (10.3%); £3,773,270.57 -> £3,383,140.39 (10.3%); £3,773,270.72 -> £3,383,140.41 (10.3%); £3,773,270.87 -> £3,383,140.42 (10.3%); £3,773,271.02 -> £3,383,140.44 (10.3%); £3,773,271.18 -> £3,383,140.46 (10.3%); £3,773,271.34 -> £3,383,140.47 (10.3%); £3,773,271.49 -> £3,383,140.49 (10.3%); £3,773,271.64 -> £3,383,140.51 (10.3%); £3,773,271.79 -> £3,383,140.53 (10.3%); £3,773,271.95 -> £3,383,140.66 (10.3%); £3,773,272.11 -> £3,383,140.79 (10.3%); £3,773,272.27 -> £3,383,140.93 (10.3%); £3,773,272.47 -> £3,383,141.07 (10.3%); £3,773,272.67 -> £3,383,141.22 (10.3%); £3,773,272.89 -> £3,383,141.36 (10.3%); £3,773,273.13 -> £3,383,141.50 (10.3%); £3,773,273.39 -> £3,383,141.64 (10.3%); £3,773,273.66 -> £3,383,141.66 (10.3%); £3,773,273.92 -> £3,383,141.69 (10.3%); £3,773,274.18 -> £3,383,141.71 (10.3%); £3,773,274.44 -> £3,383,141.74 (10.3%); £3,773,274.69 -> £3,383,141.76 (10.3%); £3,773,274.94 -> £3,383,141.79 (10.3%); £3,773,275.19 -> £3,383,141.81 (10.3%); £3,773,275.44 -> £3,383,141.84 (10.3%); £3,773,275.71 -> £3,383,141.86 (10.3%); £3,773,275.97 -> £3,383,141.89 (10.3%); £3,773,276.22 -> £3,383,141.91 (10.3%); £3,773,276.47 -> £3,383,141.93 (10.3%); £3,773,276.72 -> £3,383,141.96 (10.3%); £3,773,276.92 -> £3,383,142.11 (10.3%); £3,773,277.11 -> £3,383,142.26 (10.3%); £3,773,277.31 -> £3,383,142.41 (10.3%); £3,773,277.50 -> £3,383,142.56 (10.3%); £3,773,277.70 -> £3,383,142.71 (10.3%); £3,773,277.89 -> £3,383,142.86 (10.3%); £3,773,278.09 -> £3,383,143.02 (10.3%); £3,773,278.34 -> £3,383,143.17 (10.3%); £3,773,278.60 -> £3,383,143.32 (10.3%); £3,773,278.86 -> £3,383,143.48 (10.3%); £3,773,279.12 -> £3,383,143.62 (10.3%); £3,773,279.37 -> £3,383,143.65 (10.3%); £3,773,279.62 -> £3,383,143.68 (10.3%); £3,773,279.86 -> £3,383,143.70 (10.3%); £3,773,280.07 -> £3,383,143.73 (10.3%); £3,773,280.27 -> £3,383,143.75 (10.3%); £3,773,280.42 -> £3,383,143.77 (10.3%); £3,773,280.55 -> £3,383,143.79 (10.3%); £3,773,280.69 -> £3,383,143.80 (10.3%); £3,773,280.83 -> £3,383,143.82 (10.3%); £3,773,280.98 -> £3,383,143.84 (10.3%); £3,773,281.12 -> £3,383,143.86 (10.3%); £3,773,281.26 -> £3,383,143.87 (10.3%); £3,773,281.40 -> £3,383,143.89 (10.3%); £3,773,281.54 -> £3,383,143.91 (10.3%); £3,773,281.67 -> £3,383,143.92 (10.3%); £3,773,281.81 -> £3,383,143.94 (10.3%); £3,773,281.95 -> £3,383,144.10 (10.3%); £3,773,282.09 -> £3,383,144.25 (10.3%); £3,773,282.24 -> £3,383,144.41 (10.3%); £3,773,282.42 -> £3,383,144.58 (10.3%); £3,773,282.61 -> £3,383,144.74 (10.3%); £3,773,282.80 -> £3,383,144.90 (10.3%); £3,773,283.02 -> £3,383,145.07 (10.3%); £3,773,283.25 -> £3,383,145.23 (10.3%); £3,773,283.49 -> £3,383,145.26 (10.3%); £3,773,283.72 -> £3,383,145.29 (10.3%); £3,773,283.95 -> £3,383,145.31 (10.3%); £3,773,284.19 -> £3,383,145.34 (10.3%); £3,773,284.41 -> £3,383,145.37 (10.3%); £3,773,284.64 -> £3,383,145.40 (10.3%); £3,773,284.87 -> £3,383,145.42 (10.3%); £3,773,285.11 -> £3,383,145.45 (10.3%); £3,773,285.34 -> £3,383,145.48 (10.3%); £3,773,285.57 -> £3,383,145.50 (10.3%); £3,773,285.80 -> £3,383,145.53 (10.3%); £3,773,286.03 -> £3,383,145.56 (10.3%); £3,773,286.26 -> £3,383,145.58 (10.3%); £3,773,286.43 -> £3,383,145.75 (10.3%); £3,773,286.61 -> £3,383,145.91 (10.3%); £3,773,286.78 -> £3,383,146.08 (10.3%); £3,773,286.96 -> £3,383,146.25 (10.3%); £3,773,287.13 -> £3,383,146.43 (10.3%); £3,773,287.36 -> £3,383,146.60 (10.3%); £3,773,287.59 -> £3,383,146.77 (10.3%); £3,773,287.82 -> £3,383,146.94 (10.3%); £3,773,288.05 -> £3,383,147.11 (10.3%); £3,773,288.28 -> £3,383,147.27 (10.3%); £3,773,288.52 -> £3,383,147.44 (10.3%); £3,773,288.75 -> £3,383,147.47 (10.3%); £3,773,288.98 -> £3,383,147.50 (10.3%); £3,773,289.18 -> £3,383,147.53 (10.3%); £3,773,289.38 -> £3,383,147.55 (10.3%); £3,773,289.55 -> £3,383,147.57 (10.3%); £3,773,289.69 -> £3,383,147.59 (10.3%); £3,773,289.83 -> £3,383,147.61 (10.3%); £3,773,289.97 -> £3,383,147.63 (10.3%); £3,773,290.11 -> £3,383,147.65 (10.3%); £3,773,290.25 -> £3,383,147.67 (10.3%); £3,773,290.40 -> £3,383,147.68 (10.3%); £3,773,290.54 -> £3,383,147.70 (10.3%); £3,773,290.68 -> £3,383,147.72 (10.3%); £3,773,290.82 -> £3,383,147.73 (10.3%); £3,773,290.95 -> £3,383,147.75 (10.3%); £3,773,291.09 -> £3,383,147.77 (10.3%); £3,773,291.23 -> £3,383,147.90 (10.3%); £3,773,291.37 -> £3,383,148.03 (10.3%); £3,773,291.52 -> £3,383,148.16 (10.3%); £3,773,291.70 -> £3,383,148.29 (10.3%); £3,773,291.88 -> £3,383,148.42 (10.3%); £3,773,292.09 -> £3,383,148.56 (10.3%); £3,773,292.31 -> £3,383,148.70 (10.3%); £3,773,292.54 -> £3,383,148.84 (10.3%); £3,773,292.78 -> £3,383,148.87 (10.3%); £3,773,293.01 -> £3,383,148.90 (10.3%); £3,773,293.24 -> £3,383,148.93 (10.3%); £3,773,293.48 -> £3,383,148.96 (10.3%); £3,773,293.71 -> £3,383,148.99 (10.3%); £3,773,293.94 -> £3,383,149.02 (10.3%); £3,773,294.17 -> £3,383,149.05 (10.3%); £3,773,294.40 -> £3,383,149.08 (10.3%); £3,773,294.63 -> £3,383,149.11 (10.3%); £3,773,294.87 -> £3,383,149.14 (10.3%); £3,773,295.10 -> £3,383,149.17 (10.3%); £3,773,295.33 -> £3,383,149.20 (10.3%); £3,773,295.56 -> £3,383,149.23 (10.3%); £3,773,295.73 -> £3,383,149.37 (10.3%); £3,773,295.90 -> £3,383,149.51 (10.3%); £3,773,296.08 -> £3,383,149.66 (10.3%); £3,773,296.25 -> £3,383,149.81 (10.3%); £3,773,296.48 -> £3,383,149.96 (10.3%); £3,773,296.72 -> £3,383,150.10 (10.3%); £3,773,296.90 -> £3,383,150.25 (10.3%); £3,773,297.13 -> £3,383,150.39 (10.3%); £3,773,297.36 -> £3,383,150.53 (10.3%); £3,773,297.60 -> £3,383,150.67 (10.3%); £3,773,297.84 -> £3,383,150.81 (10.3%); £3,773,298.07 -> £3,383,150.84 (10.3%); £3,773,298.31 -> £3,383,150.86 (10.3%); £3,773,298.51 -> £3,383,150.89 (10.3%); £3,773,298.71 -> £3,383,150.91 (10.3%); £3,773,298.89 -> £3,383,150.93 (10.3%); £3,773,299.04 -> £3,383,150.95 (10.3%); £3,773,299.20 -> £3,383,150.97 (10.3%); £3,773,299.36 -> £3,383,150.98 (10.3%); £3,773,299.52 -> £3,383,151.00 (10.3%); £3,773,299.68 -> £3,383,151.02 (10.3%); £3,773,299.84 -> £3,383,151.03 (10.3%); £3,773,300.00 -> £3,383,151.05 (10.3%); £3,773,300.16 -> £3,383,151.07 (10.3%); £3,773,300.32 -> £3,383,151.08 (10.3%); £3,773,300.49 -> £3,383,151.10 (10.3%); £3,773,300.65 -> £3,383,151.12 (10.3%); £3,773,300.81 -> £3,383,151.20 (10.3%); £3,773,300.97 -> £3,383,151.30 (10.3%); £3,773,301.16 -> £3,383,151.40 (10.3%); £3,773,301.35 -> £3,383,151.50 (10.3%); £3,773,301.57 -> £3,383,151.60 (10.3%); £3,773,301.80 -> £3,383,151.70 (10.3%); £3,773,302.06 -> £3,383,151.80 (10.3%); £3,773,302.33 -> £3,383,151.90 (10.3%); £3,773,302.60 -> £3,383,151.92 (10.3%); £3,773,302.86 -> £3,383,151.94 (10.3%); £3,773,303.14 -> £3,383,151.97 (10.3%); £3,773,303.40 -> £3,383,151.99 (10.3%); £3,773,303.67 -> £3,383,152.01 (10.3%); £3,773,303.93 -> £3,383,152.04 (10.3%); £3,773,304.19 -> £3,383,152.06 (10.3%); £3,773,304.45 -> £3,383,152.08 (10.3%); £3,773,304.71 -> £3,383,152.11 (10.3%); £3,773,304.97 -> £3,383,152.13 (10.3%); £3,773,305.24 -> £3,383,152.15 (10.3%); £3,773,305.51 -> £3,383,152.18 (10.3%); £3,773,305.79 -> £3,383,152.21 (10.3%); £3,773,306.05 -> £3,383,152.32 (10.3%); £3,773,306.33 -> £3,383,152.44 (10.3%); £3,773,306.60 -> £3,383,152.55 (10.3%); £3,773,306.87 -> £3,383,152.67 (10.3%); £3,773,307.15 -> £3,383,152.79 (10.3%); £3,773,307.41 -> £3,383,152.90 (10.3%); £3,773,307.61 -> £3,383,153.02 (10.3%); £3,773,307.88 -> £3,383,153.13 (10.3%); £3,773,308.15 -> £3,383,153.23 (10.3%); £3,773,308.42 -> £3,383,153.34 (10.3%); £3,773,308.68 -> £3,383,153.45 (10.3%); £3,773,308.95 -> £3,383,153.48 (10.3%); £3,773,309.22 -> £3,383,153.51 (10.3%); £3,773,309.46 -> £3,383,153.53 (10.3%); £3,773,309.70 -> £3,383,153.55 (10.3%); £3,773,309.91 -> £3,383,153.57 (10.3%); £3,773,310.06 -> £3,383,153.59 (10.3%); £3,773,310.22 -> £3,383,153.61 (10.3%); £3,773,310.38 -> £3,383,153.62 (10.3%); £3,773,310.54 -> £3,383,153.64 (10.3%); £3,773,310.70 -> £3,383,153.66 (10.3%); £3,773,310.86 -> £3,383,153.68 (10.3%); £3,773,311.02 -> £3,383,153.69 (10.3%); £3,773,311.17 -> £3,383,153.71 (10.3%); £3,773,311.33 -> £3,383,153.73 (10.3%); £3,773,311.49 -> £3,383,153.74 (10.3%); £3,773,311.65 -> £3,383,153.76 (10.3%); £3,773,311.81 -> £3,383,153.91 (10.3%); £3,773,311.96 -> £3,383,154.07 (10.3%); £3,773,312.14 -> £3,383,154.23 (10.3%); £3,773,312.33 -> £3,383,154.39 (10.3%); £3,773,312.54 -> £3,383,154.55 (10.3%); £3,773,312.77 -> £3,383,154.72 (10.3%); £3,773,313.03 -> £3,383,154.88 (10.3%); £3,773,313.29 -> £3,383,155.04 (10.3%); £3,773,313.56 -> £3,383,155.06 (10.3%); £3,773,313.83 -> £3,383,155.09 (10.3%); £3,773,314.09 -> £3,383,155.11 (10.3%); £3,773,314.36 -> £3,383,155.13 (10.3%); £3,773,314.63 -> £3,383,155.16 (10.3%); £3,773,314.89 -> £3,383,155.18 (10.3%); £3,773,315.15 -> £3,383,155.21 (10.3%); £3,773,315.41 -> £3,383,155.23 (10.3%); £3,773,315.68 -> £3,383,155.25 (10.3%); £3,773,315.96 -> £3,383,155.28 (10.3%); £3,773,316.22 -> £3,383,155.30 (10.3%); £3,773,316.48 -> £3,383,155.33 (10.3%); £3,773,316.75 -> £3,383,155.35 (10.3%); £3,773,316.95 -> £3,383,155.51 (10.3%); £3,773,317.14 -> £3,383,155.68 (10.3%); £3,773,317.42 -> £3,383,155.86 (10.3%); £3,773,317.68 -> £3,383,156.02 (10.3%); £3,773,317.88 -> £3,383,156.19 (10.3%); £3,773,318.08 -> £3,383,156.35 (10.3%); £3,773,318.28 -> £3,383,156.52 (10.3%); £3,773,318.54 -> £3,383,156.68 (10.3%); £3,773,318.80 -> £3,383,156.84 (10.3%); £3,773,319.06 -> £3,383,157.01 (10.3%); £3,773,319.32 -> £3,383,157.17 (10.3%); £3,773,319.58 -> £3,383,157.20 (10.3%); £3,773,319.85 -> £3,383,157.23 (10.3%); £3,773,320.09 -> £3,383,157.25 (10.3%); £3,773,320.31 -> £3,383,157.28 (10.3%); £3,773,320.51 -> £3,383,157.30 (10.3%); £3,773,320.67 -> £3,383,157.32 (10.3%); £3,773,320.83 -> £3,383,157.33 (10.3%); £3,773,320.99 -> £3,383,157.35 (10.3%); £3,773,321.15 -> £3,383,157.37 (10.3%); £3,773,321.31 -> £3,383,157.38 (10.3%); £3,773,321.47 -> £3,383,157.40 (10.3%); £3,773,321.63 -> £3,383,157.42 (10.3%); £3,773,321.79 -> £3,383,157.43 (10.3%); £3,773,321.95 -> £3,383,157.45 (10.3%); £3,773,322.11 -> £3,383,157.47 (10.3%); £3,773,322.27 -> £3,383,157.49 (10.3%); £3,773,322.42 -> £3,383,157.65 (10.3%); £3,773,322.58 -> £3,383,157.82 (10.3%); £3,773,322.76 -> £3,383,158.00 (10.3%); £3,773,322.95 -> £3,383,158.18 (10.3%); £3,773,323.16 -> £3,383,158.36 (10.3%); £3,773,323.39 -> £3,383,158.53 (10.3%); £3,773,323.64 -> £3,383,158.71 (10.3%); £3,773,323.91 -> £3,383,158.88 (10.3%); £3,773,324.18 -> £3,383,158.90 (10.3%); £3,773,324.45 -> £3,383,158.93 (10.3%); £3,773,324.71 -> £3,383,158.95 (10.3%); £3,773,324.98 -> £3,383,158.97 (10.3%); £3,773,325.24 -> £3,383,159.00 (10.3%); £3,773,325.50 -> £3,383,159.02 (10.3%); £3,773,325.76 -> £3,383,159.05 (10.3%); £3,773,326.02 -> £3,383,159.07 (10.3%); £3,773,326.29 -> £3,383,159.09 (10.3%); £3,773,326.56 -> £3,383,159.12 (10.3%); £3,773,326.82 -> £3,383,159.14 (10.3%); £3,773,327.08 -> £3,383,159.17 (10.3%); £3,773,327.35 -> £3,383,159.20 (10.3%); £3,773,327.61 -> £3,383,159.37 (10.3%); £3,773,327.88 -> £3,383,159.55 (10.3%); £3,773,328.08 -> £3,383,159.73 (10.3%); £3,773,328.28 -> £3,383,159.91 (10.3%); £3,773,328.48 -> £3,383,160.10 (10.3%); £3,773,328.75 -> £3,383,160.28 (10.3%); £3,773,329.02 -> £3,383,160.46 (10.3%); £3,773,329.28 -> £3,383,160.64 (10.3%); £3,773,329.54 -> £3,383,160.81 (10.3%); £3,773,329.81 -> £3,383,160.98 (10.3%); £3,773,330.08 -> £3,383,161.16 (10.3%); £3,773,330.35 -> £3,383,161.19 (10.3%); £3,773,330.61 -> £3,383,161.22 (10.3%); £3,773,330.85 -> £3,383,161.24 (10.3%); £3,773,331.08 -> £3,383,161.27 (10.3%); £3,773,331.28 -> £3,383,161.29 (10.3%); £3,773,331.44 -> £3,383,161.30 (10.3%); £3,773,331.60 -> £3,383,161.32 (10.3%); £3,773,331.76 -> £3,383,161.34 (10.3%); £3,773,331.92 -> £3,383,161.36 (10.3%); £3,773,332.08 -> £3,383,161.37 (10.3%); £3,773,332.24 -> £3,383,161.39 (10.3%); £3,773,332.40 -> £3,383,161.41 (10.3%); £3,773,332.56 -> £3,383,161.42 (10.3%); £3,773,332.71 -> £3,383,161.44 (10.3%); £3,773,332.87 -> £3,383,161.46 (10.3%); £3,773,333.04 -> £3,383,161.48 (10.3%); £3,773,333.20 -> £3,383,161.65 (10.3%); £3,773,333.37 -> £3,383,161.81 (10.3%); £3,773,333.53 -> £3,383,161.98 (10.3%); £3,773,333.72 -> £3,383,162.15 (10.3%); £3,773,333.94 -> £3,383,162.32 (10.3%); £3,773,334.16 -> £3,383,162.49 (10.3%); £3,773,334.40 -> £3,383,162.66 (10.3%); £3,773,334.67 -> £3,383,162.83 (10.3%); £3,773,334.93 -> £3,383,162.85 (10.3%); £3,773,335.19 -> £3,383,162.88 (10.3%); £3,773,335.45 -> £3,383,162.90 (10.3%); £3,773,335.71 -> £3,383,162.93 (10.3%); £3,773,335.97 -> £3,383,162.95 (10.3%); £3,773,336.24 -> £3,383,162.97 (10.3%); £3,773,336.50 -> £3,383,163.00 (10.3%); £3,773,336.78 -> £3,383,163.02 (10.3%); £3,773,337.04 -> £3,383,163.05 (10.3%); £3,773,337.30 -> £3,383,163.07 (10.3%); £3,773,337.57 -> £3,383,163.09 (10.3%); £3,773,337.84 -> £3,383,163.12 (10.3%); £3,773,338.11 -> £3,383,163.15 (10.3%); £3,773,338.38 -> £3,383,163.32 (10.3%); £3,773,338.58 -> £3,383,163.49 (10.3%); £3,773,338.77 -> £3,383,163.66 (10.3%); £3,773,338.97 -> £3,383,163.84 (10.3%); £3,773,339.17 -> £3,383,164.02 (10.3%); £3,773,339.36 -> £3,383,164.19 (10.3%); £3,773,339.63 -> £3,383,164.37 (10.3%); £3,773,339.89 -> £3,383,164.55 (10.3%); £3,773,340.16 -> £3,383,164.72 (10.3%); £3,773,340.42 -> £3,383,164.90 (10.3%); £3,773,340.68 -> £3,383,165.06 (10.3%); £3,773,340.95 -> £3,383,165.09 (10.3%); £3,773,341.22 -> £3,383,165.12 (10.3%); £3,773,341.46 -> £3,383,165.14 (10.3%); £3,773,341.68 -> £3,383,165.17 (10.3%); £3,773,341.89 -> £3,383,165.19 (10.3%); £3,773,342.05 -> £3,383,165.21 (10.3%); £3,773,342.20 -> £3,383,165.22 (10.3%); £3,773,342.36 -> £3,383,165.24 (10.3%); £3,773,342.52 -> £3,383,165.26 (10.3%); £3,773,342.68 -> £3,383,165.27 (10.3%); £3,773,342.84 -> £3,383,165.29 (10.3%); £3,773,342.99 -> £3,383,165.31 (10.3%); £3,773,343.16 -> £3,383,165.32 (10.3%); £3,773,343.32 -> £3,383,165.34 (10.3%); £3,773,343.48 -> £3,383,165.36 (10.3%); £3,773,343.63 -> £3,383,165.37 (10.3%); £3,773,343.79 -> £3,383,165.48 (10.3%); £3,773,343.95 -> £3,383,165.59 (10.3%); £3,773,344.13 -> £3,383,165.70 (10.3%); £3,773,344.32 -> £3,383,165.82 (10.3%); £3,773,344.53 -> £3,383,165.94 (10.3%); £3,773,344.76 -> £3,383,166.05 (10.3%); £3,773,345.01 -> £3,383,166.17 (10.3%); £3,773,345.28 -> £3,383,166.28 (10.3%); £3,773,345.55 -> £3,383,166.30 (10.3%); £3,773,345.83 -> £3,383,166.33 (10.3%); £3,773,346.10 -> £3,383,166.35 (10.3%); £3,773,346.36 -> £3,383,166.37 (10.3%); £3,773,346.62 -> £3,383,166.40 (10.3%); £3,773,346.90 -> £3,383,166.42 (10.3%); £3,773,347.15 -> £3,383,166.45 (10.3%); £3,773,347.43 -> £3,383,166.47 (10.3%); £3,773,347.69 -> £3,383,166.49 (10.3%); £3,773,347.95 -> £3,383,166.52 (10.3%); £3,773,348.22 -> £3,383,166.54 (10.3%); £3,773,348.48 -> £3,383,166.57 (10.3%); £3,773,348.75 -> £3,383,166.60 (10.3%); £3,773,349.02 -> £3,383,166.72 (10.3%); £3,773,349.29 -> £3,383,166.85 (10.3%); £3,773,349.55 -> £3,383,166.98 (10.3%); £3,773,349.81 -> £3,383,167.11 (10.3%); £3,773,350.08 -> £3,383,167.24 (10.3%); £3,773,350.34 -> £3,383,167.37 (10.3%); £3,773,350.61 -> £3,383,167.50 (10.3%); £3,773,350.87 -> £3,383,167.62 (10.3%); £3,773,351.14 -> £3,383,167.74 (10.3%); £3,773,351.41 -> £3,383,167.87 (10.3%); £3,773,351.67 -> £3,383,167.99 (10.3%); £3,773,351.94 -> £3,383,168.02 (10.3%); £3,773,352.20 -> £3,383,168.05 (10.3%); £3,773,352.46 -> £3,383,168.07 (10.3%); £3,773,352.68 -> £3,383,168.10 (10.3%); £3,773,352.89 -> £3,383,168.12 (10.3%); £3,773,353.03 -> £3,383,168.14 (10.3%); £3,773,353.16 -> £3,383,168.16 (10.3%); £3,773,353.31 -> £3,383,168.17 (10.3%); £3,773,353.45 -> £3,383,168.19 (10.3%); £3,773,353.58 -> £3,383,168.21 (10.3%); £3,773,353.72 -> £3,383,168.23 (10.3%); £3,773,353.86 -> £3,383,168.24 (10.3%); £3,773,354.00 -> £3,383,168.26 (10.3%); £3,773,354.15 -> £3,383,168.28 (10.3%); £3,773,354.29 -> £3,383,168.29 (10.3%); £3,773,354.42 -> £3,383,168.31 (10.3%); £3,773,354.56 -> £3,383,168.42 (10.3%); £3,773,354.71 -> £3,383,168.53 (10.3%); £3,773,354.86 -> £3,383,168.64 (10.3%); £3,773,355.03 -> £3,383,168.75 (10.3%); £3,773,355.22 -> £3,383,168.86 (10.3%); £3,773,355.42 -> £3,383,168.97 (10.3%); £3,773,355.63 -> £3,383,169.09 (10.3%); £3,773,355.86 -> £3,383,169.20 (10.3%); £3,773,356.10 -> £3,383,169.23 (10.3%); £3,773,356.33 -> £3,383,169.26 (10.3%); £3,773,356.57 -> £3,383,169.28 (10.3%); £3,773,356.80 -> £3,383,169.31 (10.3%); £3,773,357.02 -> £3,383,169.34 (10.3%); £3,773,357.26 -> £3,383,169.36 (10.3%); £3,773,357.49 -> £3,383,169.39 (10.3%); £3,773,357.73 -> £3,383,169.42 (10.3%); £3,773,357.96 -> £3,383,169.44 (10.3%); £3,773,358.18 -> £3,383,169.47 (10.3%); £3,773,358.41 -> £3,383,169.49 (10.3%); £3,773,358.65 -> £3,383,169.52 (10.3%); £3,773,358.89 -> £3,383,169.55 (10.3%); £3,773,359.12 -> £3,383,169.66 (10.3%); £3,773,359.30 -> £3,383,169.78 (10.3%); £3,773,359.53 -> £3,383,169.91 (10.3%); £3,773,359.71 -> £3,383,170.03 (10.3%); £3,773,359.88 -> £3,383,170.15 (10.3%); £3,773,360.05 -> £3,383,170.27 (10.3%); £3,773,360.23 -> £3,383,170.40 (10.3%); £3,773,360.46 -> £3,383,170.53 (10.3%); £3,773,360.69 -> £3,383,170.65 (10.3%); £3,773,360.92 -> £3,383,170.77 (10.3%); £3,773,361.15 -> £3,383,170.89 (10.3%); £3,773,361.38 -> £3,383,170.92 (10.3%); £3,773,361.61 -> £3,383,170.95 (10.3%); £3,773,361.82 -> £3,383,170.97 (10.3%); £3,773,362.01 -> £3,383,170.99 (10.3%); £3,773,362.19 -> £3,383,171.02 (10.3%); £3,773,362.33 -> £3,383,171.04 (10.3%); £3,773,362.48 -> £3,383,171.06 (10.3%); £3,773,362.62 -> £3,383,171.08 (10.3%); £3,773,362.75 -> £3,383,171.09 (10.3%); £3,773,362.90 -> £3,383,171.11 (10.3%); £3,773,363.04 -> £3,383,171.13 (10.3%); £3,773,363.18 -> £3,383,171.15 (10.3%); £3,773,363.31 -> £3,383,171.16 (10.3%); £3,773,363.46 -> £3,383,171.18 (10.3%); £3,773,363.60 -> £3,383,171.20 (10.3%); £3,773,363.74 -> £3,383,171.21 (10.3%); £3,773,363.88 -> £3,383,171.31 (10.3%); £3,773,364.02 -> £3,383,171.42 (10.3%); £3,773,364.18 -> £3,383,171.52 (10.3%); £3,773,364.34 -> £3,383,171.62 (10.3%); £3,773,364.52 -> £3,383,171.73 (10.3%); £3,773,364.72 -> £3,383,171.84 (10.3%); £3,773,364.95 -> £3,383,171.95 (10.3%); £3,773,365.19 -> £3,383,172.06 (10.3%); £3,773,365.42 -> £3,383,172.10 (10.3%); £3,773,365.65 -> £3,383,172.13 (10.3%); £3,773,365.89 -> £3,383,172.16 (10.3%); £3,773,366.12 -> £3,383,172.19 (10.3%); £3,773,366.36 -> £3,383,172.22 (10.3%); £3,773,366.59 -> £3,383,172.26 (10.3%); £3,773,366.83 -> £3,383,172.29 (10.3%); £3,773,367.07 -> £3,383,172.32 (10.3%); £3,773,367.31 -> £3,383,172.34 (10.3%); £3,773,367.54 -> £3,383,172.37 (10.3%); £3,773,367.78 -> £3,383,172.40 (10.3%); £3,773,368.02 -> £3,383,172.43 (10.3%); £3,773,368.26 -> £3,383,172.46 (10.3%); £3,773,368.49 -> £3,383,172.58 (10.3%); £3,773,368.72 -> £3,383,172.69 (10.3%); £3,773,368.88 -> £3,383,172.81 (10.3%); £3,773,369.06 -> £3,383,172.93 (10.3%); £3,773,369.24 -> £3,383,173.05 (10.3%); £3,773,369.42 -> £3,383,173.17 (10.3%); £3,773,369.59 -> £3,383,173.28 (10.3%); £3,773,369.83 -> £3,383,173.40 (10.3%); £3,773,370.06 -> £3,383,173.51 (10.3%); £3,773,370.30 -> £3,383,173.63 (10.3%); £3,773,370.53 -> £3,383,173.75 (10.3%); £3,773,370.76 -> £3,383,173.78 (10.3%); £3,773,371.00 -> £3,383,173.81 (10.3%); £3,773,371.22 -> £3,383,173.83 (10.3%); £3,773,371.43 -> £3,383,173.86 (10.3%); £3,773,371.61 -> £3,383,173.88 (10.3%); £3,773,371.77 -> £3,383,173.90 (10.3%); £3,773,371.93 -> £3,383,173.91 (10.3%); £3,773,372.09 -> £3,383,173.93 (10.3%); £3,773,372.25 -> £3,383,173.95 (10.3%); £3,773,372.41 -> £3,383,173.97 (10.3%); £3,773,372.58 -> £3,383,173.98 (10.3%); £3,773,372.74 -> £3,383,174.00 (10.3%); £3,773,372.91 -> £3,383,174.02 (10.3%); £3,773,373.07 -> £3,383,174.03 (10.3%); £3,773,373.24 -> £3,383,174.05 (10.3%); £3,773,373.39 -> £3,383,174.07 (10.3%); £3,773,373.57 -> £3,383,174.18 (10.3%); £3,773,373.73 -> £3,383,174.28 (10.3%); £3,773,373.91 -> £3,383,174.39 (10.3%); £3,773,374.11 -> £3,383,174.51 (10.3%); £3,773,374.34 -> £3,383,174.62 (10.3%); £3,773,374.57 -> £3,383,174.74 (10.3%); £3,773,374.82 -> £3,383,174.85 (10.3%); £3,773,375.08 -> £3,383,174.97 (10.3%); £3,773,375.36 -> £3,383,174.99 (10.3%); £3,773,375.64 -> £3,383,175.02 (10.3%); £3,773,375.92 -> £3,383,175.04 (10.3%); £3,773,376.19 -> £3,383,175.06 (10.3%); £3,773,376.45 -> £3,383,175.09 (10.3%); £3,773,376.72 -> £3,383,175.11 (10.3%); £3,773,376.99 -> £3,383,175.13 (10.3%); £3,773,377.25 -> £3,383,175.16 (10.3%); £3,773,377.53 -> £3,383,175.18 (10.3%); £3,773,377.79 -> £3,383,175.20 (10.3%); £3,773,378.06 -> £3,383,175.23 (10.3%); £3,773,378.34 -> £3,383,175.25 (10.3%); £3,773,378.60 -> £3,383,175.28 (10.3%); £3,773,378.81 -> £3,383,175.40 (10.3%); £3,773,379.01 -> £3,383,175.52 (10.3%); £3,773,379.21 -> £3,383,175.65 (10.3%); £3,773,379.42 -> £3,383,175.77 (10.3%); £3,773,379.63 -> £3,383,175.90 (10.3%); £3,773,379.90 -> £3,383,176.03 (10.3%); £3,773,380.18 -> £3,383,176.16 (10.3%); £3,773,380.46 -> £3,383,176.28 (10.3%); £3,773,380.73 -> £3,383,176.41 (10.3%); £3,773,381.00 -> £3,383,176.53 (10.3%); £3,773,381.27 -> £3,383,176.65 (10.3%); £3,773,381.54 -> £3,383,176.68 (10.3%); £3,773,381.81 -> £3,383,176.70 (10.3%); £3,773,382.06 -> £3,383,176.73 (10.3%); £3,773,382.30 -> £3,383,176.75 (10.3%); £3,773,382.51 -> £3,383,176.77 (10.3%); £3,773,382.68 -> £3,383,176.79 (10.3%); £3,773,382.85 -> £3,383,176.81 (10.3%); £3,773,383.01 -> £3,383,176.83 (10.3%); £3,773,383.18 -> £3,383,176.84 (10.3%); £3,773,383.35 -> £3,383,176.86 (10.3%); £3,773,383.51 -> £3,383,176.88 (10.3%); £3,773,383.68 -> £3,383,176.89 (10.3%); £3,773,383.84 -> £3,383,176.91 (10.3%); £3,773,384.01 -> £3,383,176.93 (10.3%); £3,773,384.17 -> £3,383,176.94 (10.3%); £3,773,384.34 -> £3,383,176.96 (10.3%); £3,773,384.51 -> £3,383,177.09 (10.3%); £3,773,384.68 -> £3,383,177.22 (10.3%); £3,773,384.86 -> £3,383,177.35 (10.3%); £3,773,385.06 -> £3,383,177.49 (10.3%); £3,773,385.28 -> £3,383,177.62 (10.3%); £3,773,385.52 -> £3,383,177.75 (10.3%); £3,773,385.77 -> £3,383,177.88 (10.3%); £3,773,386.05 -> £3,383,178.01 (10.3%); £3,773,386.32 -> £3,383,178.03 (10.3%); £3,773,386.60 -> £3,383,178.06 (10.3%); £3,773,386.88 -> £3,383,178.08 (10.3%); £3,773,387.15 -> £3,383,178.11 (10.3%); £3,773,387.43 -> £3,383,178.13 (10.3%); £3,773,387.70 -> £3,383,178.15 (10.3%); £3,773,387.97 -> £3,383,178.18 (10.3%); £3,773,388.25 -> £3,383,178.20 (10.3%); £3,773,388.52 -> £3,383,178.22 (10.3%); £3,773,388.79 -> £3,383,178.25 (10.3%); £3,773,389.05 -> £3,383,178.27 (10.3%); £3,773,389.32 -> £3,383,178.30 (10.3%); £3,773,389.60 -> £3,383,178.32 (10.3%); £3,773,389.80 -> £3,383,178.46 (10.3%); £3,773,390.01 -> £3,383,178.59 (10.3%); £3,773,390.22 -> £3,383,178.73 (10.3%); £3,773,390.43 -> £3,383,178.87 (10.3%); £3,773,390.63 -> £3,383,179.00 (10.3%); £3,773,390.83 -> £3,383,179.14 (10.3%); £3,773,391.04 -> £3,383,179.27 (10.3%); £3,773,391.32 -> £3,383,179.40 (10.3%); £3,773,391.59 -> £3,383,179.53 (10.3%); £3,773,391.86 -> £3,383,179.66 (10.3%); £3,773,392.13 -> £3,383,179.80 (10.3%); £3,773,392.41 -> £3,383,179.82 (10.3%); £3,773,392.68 -> £3,383,179.85 (10.3%); £3,773,392.93 -> £3,383,179.88 (10.3%); £3,773,393.16 -> £3,383,179.90 (10.3%); £3,773,393.37 -> £3,383,179.92 (10.3%); £3,773,393.54 -> £3,383,179.94 (10.3%); £3,773,393.70 -> £3,383,179.96 (10.3%); £3,773,393.86 -> £3,383,179.97 (10.3%); £3,773,394.02 -> £3,383,179.99 (10.3%); £3,773,394.19 -> £3,383,180.01 (10.3%); £3,773,394.36 -> £3,383,180.02 (10.3%); £3,773,394.52 -> £3,383,180.04 (10.3%); £3,773,394.69 -> £3,383,180.06 (10.3%); £3,773,394.85 -> £3,383,180.07 (10.3%); £3,773,395.02 -> £3,383,180.09 (10.3%); £3,773,395.19 -> £3,383,180.11 (10.3%); £3,773,395.36 -> £3,383,180.29 (10.3%); £3,773,395.52 -> £3,383,180.49 (10.3%); £3,773,395.70 -> £3,383,180.69 (10.3%); £3,773,395.91 -> £3,383,180.89 (10.3%); £3,773,396.13 -> £3,383,181.10 (10.3%); £3,773,396.37 -> £3,383,181.30 (10.3%); £3,773,396.63 -> £3,383,181.49 (10.3%); £3,773,396.91 -> £3,383,181.68 (10.3%); £3,773,397.19 -> £3,383,181.71 (10.3%); £3,773,397.48 -> £3,383,181.73 (10.3%); £3,773,397.75 -> £3,383,181.75 (10.3%); £3,773,398.03 -> £3,383,181.78 (10.3%); £3,773,398.30 -> £3,383,181.80 (10.3%); £3,773,398.59 -> £3,383,181.83 (10.3%); £3,773,398.85 -> £3,383,181.85 (10.3%); £3,773,399.12 -> £3,383,181.87 (10.3%); £3,773,399.40 -> £3,383,181.90 (10.3%); £3,773,399.68 -> £3,383,181.92 (10.3%); £3,773,399.95 -> £3,383,181.94 (10.3%); £3,773,400.22 -> £3,383,181.97 (10.3%); £3,773,400.50 -> £3,383,182.00 (10.3%); £3,773,400.71 -> £3,383,182.19 (10.3%); £3,773,400.92 -> £3,383,182.40 (10.3%); £3,773,401.19 -> £3,383,182.59 (10.3%); £3,773,401.40 -> £3,383,182.80 (10.3%); £3,773,401.60 -> £3,383,182.99 (10.3%); £3,773,401.81 -> £3,383,183.20 (10.3%); £3,773,402.07 -> £3,383,183.40 (10.3%); £3,773,402.36 -> £3,383,183.61 (10.3%); £3,773,402.62 -> £3,383,183.81 (10.3%); £3,773,402.89 -> £3,383,184.01 (10.3%); £3,773,403.16 -> £3,383,184.20 (10.3%); £3,773,403.44 -> £3,383,184.23 (10.3%); £3,773,403.72 -> £3,383,184.26 (10.3%); £3,773,403.98 -> £3,383,184.28 (10.3%); £3,773,404.22 -> £3,383,184.31 (10.3%); £3,773,404.44 -> £3,383,184.33 (10.3%); £3,773,404.61 -> £3,383,184.34 (10.3%); £3,773,404.77 -> £3,383,184.36 (10.3%); £3,773,404.93 -> £3,383,184.38 (10.3%); £3,773,405.09 -> £3,383,184.40 (10.3%); £3,773,405.26 -> £3,383,184.41 (10.3%); £3,773,405.43 -> £3,383,184.43 (10.3%); £3,773,405.59 -> £3,383,184.45 (10.3%); £3,773,405.76 -> £3,383,184.46 (10.3%); £3,773,405.93 -> £3,383,184.48 (10.3%); £3,773,406.08 -> £3,383,184.50 (10.3%); £3,773,406.25 -> £3,383,184.51 (10.3%); £3,773,406.41 -> £3,383,184.71 (10.3%); £3,773,406.58 -> £3,383,184.92 (10.3%); £3,773,406.77 -> £3,383,185.12 (10.3%); £3,773,406.97 -> £3,383,185.34 (10.3%); £3,773,407.19 -> £3,383,185.56 (10.3%); £3,773,407.43 -> £3,383,185.77 (10.3%); £3,773,407.68 -> £3,383,185.99 (10.3%); £3,773,407.96 -> £3,383,186.19 (10.3%); £3,773,408.23 -> £3,383,186.22 (10.3%); £3,773,408.51 -> £3,383,186.24 (10.3%); £3,773,408.79 -> £3,383,186.27 (10.3%); £3,773,409.07 -> £3,383,186.29 (10.3%); £3,773,409.34 -> £3,383,186.31 (10.3%); £3,773,409.61 -> £3,383,186.34 (10.3%); £3,773,409.88 -> £3,383,186.36 (10.3%); £3,773,410.16 -> £3,383,186.38 (10.3%); £3,773,410.43 -> £3,383,186.41 (10.3%); £3,773,410.71 -> £3,383,186.43 (10.3%); £3,773,410.98 -> £3,383,186.45 (10.3%); £3,773,411.25 -> £3,383,186.48 (10.3%); £3,773,411.52 -> £3,383,186.51 (10.3%); £3,773,411.73 -> £3,383,186.72 (10.3%); £3,773,412.01 -> £3,383,186.93 (10.3%); £3,773,412.22 -> £3,383,187.15 (10.3%); £3,773,412.48 -> £3,383,187.37 (10.3%); £3,773,412.75 -> £3,383,187.59 (10.3%); £3,773,413.03 -> £3,383,187.81 (10.3%); £3,773,413.30 -> £3,383,188.03 (10.3%); £3,773,413.57 -> £3,383,188.24 (10.3%); £3,773,413.86 -> £3,383,188.45 (10.3%); £3,773,414.13 -> £3,383,188.66 (10.3%); £3,773,414.40 -> £3,383,188.87 (10.3%); £3,773,414.69 -> £3,383,188.90 (10.3%); £3,773,414.96 -> £3,383,188.93 (10.3%); £3,773,415.22 -> £3,383,188.96 (10.3%); £3,773,415.46 -> £3,383,188.98 (10.3%); £3,773,415.67 -> £3,383,189.00 (10.3%); £3,773,415.83 -> £3,383,189.02 (10.3%); £3,773,416.00 -> £3,383,189.03 (10.3%); £3,773,416.16 -> £3,383,189.05 (10.3%); £3,773,416.32 -> £3,383,189.07 (10.3%); £3,773,416.48 -> £3,383,189.08 (10.3%); £3,773,416.65 -> £3,383,189.10 (10.3%); £3,773,416.82 -> £3,383,189.12 (10.3%); £3,773,416.98 -> £3,383,189.13 (10.3%); £3,773,417.14 -> £3,383,189.15 (10.3%); £3,773,417.30 -> £3,383,189.17 (10.3%); £3,773,417.47 -> £3,383,189.18 (10.3%); £3,773,417.64 -> £3,383,189.34 (10.3%); £3,773,417.80 -> £3,383,189.50 (10.3%); £3,773,417.98 -> £3,383,189.66 (10.3%); £3,773,418.18 -> £3,383,189.82 (10.3%); £3,773,418.40 -> £3,383,189.99 (10.3%); £3,773,418.63 -> £3,383,190.15 (10.3%); £3,773,418.89 -> £3,383,190.32 (10.3%); £3,773,419.15 -> £3,383,190.48 (10.3%); £3,773,419.42 -> £3,383,190.51 (10.3%); £3,773,419.70 -> £3,383,190.53 (10.3%); £3,773,419.97 -> £3,383,190.56 (10.3%); £3,773,420.24 -> £3,383,190.58 (10.3%); £3,773,420.50 -> £3,383,190.61 (10.3%); £3,773,420.76 -> £3,383,190.63 (10.3%); £3,773,421.03 -> £3,383,190.66 (10.3%); £3,773,421.30 -> £3,383,190.68 (10.3%); £3,773,421.58 -> £3,383,190.70 (10.3%); £3,773,421.86 -> £3,383,190.73 (10.3%); £3,773,422.12 -> £3,383,190.75 (10.3%); £3,773,422.40 -> £3,383,190.78 (10.3%); £3,773,422.67 -> £3,383,190.81 (10.3%); £3,773,422.94 -> £3,383,190.98 (10.3%); £3,773,423.20 -> £3,383,191.15 (10.3%); £3,773,423.48 -> £3,383,191.32 (10.3%); £3,773,423.76 -> £3,383,191.50 (10.3%); £3,773,424.03 -> £3,383,191.67 (10.3%); £3,773,424.24 -> £3,383,191.84 (10.3%); £3,773,424.44 -> £3,383,192.01 (10.3%); £3,773,424.72 -> £3,383,192.17 (10.3%); £3,773,424.98 -> £3,383,192.34 (10.3%); £3,773,425.25 -> £3,383,192.51 (10.3%); £3,773,425.52 -> £3,383,192.68 (10.3%); £3,773,425.79 -> £3,383,192.71 (10.3%); £3,773,426.06 -> £3,383,192.73 (10.3%); £3,773,426.31 -> £3,383,192.76 (10.3%); £3,773,426.55 -> £3,383,192.78 (10.3%); £3,773,426.76 -> £3,383,192.80 (10.3%); £3,773,426.90 -> £3,383,192.82 (10.3%); £3,773,427.05 -> £3,383,192.84 (10.3%); £3,773,427.19 -> £3,383,192.86 (10.3%); £3,773,427.33 -> £3,383,192.87 (10.3%); £3,773,427.47 -> £3,383,192.89 (10.3%); £3,773,427.61 -> £3,383,192.91 (10.3%); £3,773,427.76 -> £3,383,192.92 (10.3%); £3,773,427.90 -> £3,383,192.94 (10.3%); £3,773,428.04 -> £3,383,192.96 (10.3%); £3,773,428.18 -> £3,383,192.97 (10.3%); £3,773,428.33 -> £3,383,192.99 (10.3%); £3,773,428.47 -> £3,383,193.14 (10.3%); £3,773,428.61 -> £3,383,193.29 (10.3%); £3,773,428.77 -> £3,383,193.44 (10.3%); £3,773,428.95 -> £3,383,193.59 (10.3%); £3,773,429.14 -> £3,383,193.75 (10.3%); £3,773,429.35 -> £3,383,193.92 (10.3%); £3,773,429.57 -> £3,383,194.08 (10.3%); £3,773,429.81 -> £3,383,194.24 (10.3%); £3,773,430.04 -> £3,383,194.27 (10.3%); £3,773,430.28 -> £3,383,194.30 (10.3%); £3,773,430.52 -> £3,383,194.32 (10.3%); £3,773,430.77 -> £3,383,194.35 (10.3%); £3,773,431.00 -> £3,383,194.38 (10.3%); £3,773,431.24 -> £3,383,194.40 (10.3%); £3,773,431.48 -> £3,383,194.43 (10.3%); £3,773,431.71 -> £3,383,194.46 (10.3%); £3,773,431.95 -> £3,383,194.48 (10.3%); £3,773,432.20 -> £3,383,194.51 (10.3%); £3,773,432.43 -> £3,383,194.53 (10.3%); £3,773,432.67 -> £3,383,194.56 (10.3%); £3,773,432.92 -> £3,383,194.59 (10.3%); £3,773,433.15 -> £3,383,194.75 (10.3%); £3,773,433.39 -> £3,383,194.92 (10.3%); £3,773,433.62 -> £3,383,195.08 (10.3%); £3,773,433.80 -> £3,383,195.25 (10.3%); £3,773,434.04 -> £3,383,195.42 (10.3%); £3,773,434.22 -> £3,383,195.58 (10.3%); £3,773,434.40 -> £3,383,195.75 (10.3%); £3,773,434.64 -> £3,383,195.92 (10.3%); £3,773,434.88 -> £3,383,196.08 (10.3%); £3,773,435.12 -> £3,383,196.25 (10.3%); £3,773,435.36 -> £3,383,196.41 (10.3%); £3,773,435.61 -> £3,383,196.44 (10.3%); £3,773,435.84 -> £3,383,196.47 (10.3%); £3,773,436.06 -> £3,383,196.49 (10.3%); £3,773,436.27 -> £3,383,196.51 (10.3%); £3,773,436.46 -> £3,383,196.54 (10.3%); £3,773,436.60 -> £3,383,196.56 (10.3%); £3,773,436.74 -> £3,383,196.58 (10.3%); £3,773,436.88 -> £3,383,196.59 (10.3%); £3,773,437.02 -> £3,383,196.61 (10.3%); £3,773,437.16 -> £3,383,196.63 (10.3%); £3,773,437.30 -> £3,383,196.65 (10.3%); £3,773,437.44 -> £3,383,196.66 (10.3%); £3,773,437.58 -> £3,383,196.68 (10.3%); £3,773,437.73 -> £3,383,196.70 (10.3%); £3,773,437.87 -> £3,383,196.71 (10.3%); £3,773,438.00 -> £3,383,196.73 (10.3%); £3,773,438.14 -> £3,383,196.89 (10.3%); £3,773,438.28 -> £3,383,197.05 (10.3%); £3,773,438.43 -> £3,383,197.20 (10.3%); £3,773,438.60 -> £3,383,197.36 (10.3%); £3,773,438.79 -> £3,383,197.53 (10.3%); £3,773,438.99 -> £3,383,197.70 (10.3%); £3,773,439.21 -> £3,383,197.87 (10.3%); £3,773,439.45 -> £3,383,198.04 (10.3%); £3,773,439.68 -> £3,383,198.07 (10.3%); £3,773,439.92 -> £3,383,198.10 (10.3%); £3,773,440.15 -> £3,383,198.13 (10.3%); £3,773,440.39 -> £3,383,198.16 (10.3%); £3,773,440.63 -> £3,383,198.20 (10.3%); £3,773,440.87 -> £3,383,198.23 (10.3%); £3,773,441.09 -> £3,383,198.26 (10.3%); £3,773,441.33 -> £3,383,198.29 (10.3%); £3,773,441.56 -> £3,383,198.32 (10.3%); £3,773,441.80 -> £3,383,198.35 (10.3%); £3,773,442.03 -> £3,383,198.37 (10.3%); £3,773,442.26 -> £3,383,198.40 (10.3%); £3,773,442.50 -> £3,383,198.43 (10.3%); £3,773,442.73 -> £3,383,198.61 (10.3%); £3,773,442.96 -> £3,383,198.78 (10.3%); £3,773,443.14 -> £3,383,198.95 (10.3%); £3,773,443.32 -> £3,383,199.13 (10.3%); £3,773,443.50 -> £3,383,199.29 (10.3%); £3,773,443.67 -> £3,383,199.46 (10.3%); £3,773,443.85 -> £3,383,199.64 (10.3%); £3,773,444.09 -> £3,383,199.82 (10.3%); £3,773,444.32 -> £3,383,199.99 (10.3%); £3,773,444.55 -> £3,383,200.16 (10.3%); £3,773,444.78 -> £3,383,200.33 (10.3%); £3,773,445.01 -> £3,383,200.35 (10.3%); £3,773,445.25 -> £3,383,200.38 (10.3%); £3,773,445.47 -> £3,383,200.40 (10.3%); £3,773,445.67 -> £3,383,200.43 (10.3%); £3,773,445.85 -> £3,383,200.45 (10.3%); £3,773,446.01 -> £3,383,200.46 (10.3%); £3,773,446.17 -> £3,383,200.48 (10.3%); £3,773,446.32 -> £3,383,200.50 (10.3%); £3,773,446.48 -> £3,383,200.52 (10.3%); £3,773,446.63 -> £3,383,200.53 (10.3%); £3,773,446.79 -> £3,383,200.55 (10.3%); £3,773,446.94 -> £3,383,200.57 (10.3%); £3,773,447.10 -> £3,383,200.58 (10.3%); £3,773,447.25 -> £3,383,200.60 (10.3%); £3,773,447.41 -> £3,383,200.62 (10.3%); £3,773,447.56 -> £3,383,200.63 (10.3%); £3,773,447.71 -> £3,383,200.81 (10.3%); £3,773,447.87 -> £3,383,200.99 (10.3%); £3,773,448.04 -> £3,383,201.17 (10.3%); £3,773,448.24 -> £3,383,201.35 (10.3%); £3,773,448.45 -> £3,383,201.53 (10.3%); £3,773,448.67 -> £3,383,201.71 (10.3%); £3,773,448.91 -> £3,383,201.89 (10.3%); £3,773,449.18 -> £3,383,202.08 (10.3%); £3,773,449.43 -> £3,383,202.10 (10.3%); £3,773,449.68 -> £3,383,202.13 (10.3%); £3,773,449.94 -> £3,383,202.15 (10.3%); £3,773,450.20 -> £3,383,202.17 (10.3%); £3,773,450.46 -> £3,383,202.20 (10.3%); £3,773,450.72 -> £3,383,202.22 (10.3%); £3,773,450.98 -> £3,383,202.25 (10.3%); £3,773,451.24 -> £3,383,202.27 (10.3%); £3,773,451.50 -> £3,383,202.29 (10.3%); £3,773,451.76 -> £3,383,202.32 (10.3%); £3,773,452.02 -> £3,383,202.34 (10.3%); £3,773,452.28 -> £3,383,202.37 (10.3%); £3,773,452.54 -> £3,383,202.39 (10.3%); £3,773,452.74 -> £3,383,202.57 (10.3%); £3,773,452.93 -> £3,383,202.76 (10.3%); £3,773,453.12 -> £3,383,202.94 (10.3%); £3,773,453.32 -> £3,383,203.13 (10.3%); £3,773,453.51 -> £3,383,203.31 (10.3%); £3,773,453.70 -> £3,383,203.50 (10.3%); £3,773,453.90 -> £3,383,203.68 (10.3%); £3,773,454.16 -> £3,383,203.86 (10.3%); £3,773,454.42 -> £3,383,204.05 (10.3%); £3,773,454.67 -> £3,383,204.23 (10.3%); £3,773,454.94 -> £3,383,204.41 (10.3%); £3,773,455.19 -> £3,383,204.44 (10.3%); £3,773,455.46 -> £3,383,204.47 (10.3%); £3,773,455.69 -> £3,383,204.49 (10.3%); £3,773,455.91 -> £3,383,204.51 (10.3%); £3,773,456.12 -> £3,383,204.53 (10.3%); £3,773,456.27 -> £3,383,204.55 (10.3%); £3,773,456.44 -> £3,383,204.57 (10.3%); £3,773,456.59 -> £3,383,204.59 (10.3%); £3,773,456.75 -> £3,383,204.60 (10.3%); £3,773,456.91 -> £3,383,204.62 (10.3%); £3,773,457.06 -> £3,383,204.64 (10.3%); £3,773,457.22 -> £3,383,204.65 (10.3%); £3,773,457.37 -> £3,383,204.67 (10.3%); £3,773,457.52 -> £3,383,204.68 (10.3%); £3,773,457.68 -> £3,383,204.70 (10.3%); £3,773,457.83 -> £3,383,204.72 (10.3%); £3,773,457.99 -> £3,383,204.87 (10.3%); £3,773,458.15 -> £3,383,205.01 (10.3%); £3,773,458.33 -> £3,383,205.16 (10.3%); £3,773,458.52 -> £3,383,205.32 (10.3%); £3,773,458.73 -> £3,383,205.48 (10.3%); £3,773,458.96 -> £3,383,205.63 (10.3%); £3,773,459.20 -> £3,383,205.79 (10.3%); £3,773,459.45 -> £3,383,205.94 (10.3%); £3,773,459.71 -> £3,383,205.96 (10.3%); £3,773,459.96 -> £3,383,205.99 (10.3%); £3,773,460.23 -> £3,383,206.01 (10.3%); £3,773,460.48 -> £3,383,206.04 (10.3%); £3,773,460.74 -> £3,383,206.06 (10.3%); £3,773,461.01 -> £3,383,206.08 (10.3%); £3,773,461.27 -> £3,383,206.11 (10.3%); £3,773,461.53 -> £3,383,206.13 (10.3%); £3,773,461.79 -> £3,383,206.16 (10.3%); £3,773,462.05 -> £3,383,206.18 (10.3%); £3,773,462.31 -> £3,383,206.20 (10.3%); £3,773,462.56 -> £3,383,206.23 (10.3%); £3,773,462.82 -> £3,383,206.26 (10.3%); £3,773,463.08 -> £3,383,206.42 (10.3%); £3,773,463.34 -> £3,383,206.59 (10.3%); £3,773,463.60 -> £3,383,206.75 (10.3%); £3,773,463.86 -> £3,383,206.92 (10.3%); £3,773,464.11 -> £3,383,207.09 (10.3%); £3,773,464.37 -> £3,383,207.25 (10.3%); £3,773,464.62 -> £3,383,207.42 (10.3%); £3,773,464.89 -> £3,383,207.58 (10.3%); £3,773,465.14 -> £3,383,207.74 (10.3%); £3,773,465.40 -> £3,383,207.90 (10.3%); £3,773,465.67 -> £3,383,208.06 (10.3%); £3,773,465.93 -> £3,383,208.09 (10.3%); £3,773,466.19 -> £3,383,208.11 (10.3%); £3,773,466.43 -> £3,383,208.14 (10.3%); £3,773,466.66 -> £3,383,208.16 (10.3%); £3,773,466.86 -> £3,383,208.18 (10.3%); £3,773,467.01 -> £3,383,208.20 (10.3%); £3,773,467.16 -> £3,383,208.21 (10.3%); £3,773,467.32 -> £3,383,208.23 (10.3%); £3,773,467.47 -> £3,383,208.25 (10.3%); £3,773,467.62 -> £3,383,208.27 (10.3%); £3,773,467.78 -> £3,383,208.28 (10.3%); £3,773,467.93 -> £3,383,208.30 (10.3%); £3,773,468.09 -> £3,383,208.32 (10.3%); £3,773,468.24 -> £3,383,208.33 (10.3%); £3,773,468.40 -> £3,383,208.35 (10.3%); £3,773,468.56 -> £3,383,208.37 (10.3%); £3,773,468.72 -> £3,383,208.45 (10.3%); £3,773,468.87 -> £3,383,208.54 (10.3%); £3,773,469.05 -> £3,383,208.64 (10.3%); £3,773,469.24 -> £3,383,208.74 (10.3%); £3,773,469.45 -> £3,383,208.84 (10.3%); £3,773,469.67 -> £3,383,208.94 (10.3%); £3,773,469.91 -> £3,383,209.03 (10.3%); £3,773,470.17 -> £3,383,209.13 (10.3%); £3,773,470.43 -> £3,383,209.15 (10.3%); £3,773,470.69 -> £3,383,209.17 (10.3%); £3,773,470.95 -> £3,383,209.20 (10.3%); £3,773,471.21 -> £3,383,209.22 (10.3%); £3,773,471.47 -> £3,383,209.25 (10.3%); £3,773,471.72 -> £3,383,209.27 (10.3%); £3,773,471.97 -> £3,383,209.29 (10.3%); £3,773,472.23 -> £3,383,209.32 (10.3%); £3,773,472.49 -> £3,383,209.34 (10.3%); £3,773,472.75 -> £3,383,209.36 (10.3%); £3,773,473.01 -> £3,383,209.39 (10.3%); £3,773,473.27 -> £3,383,209.41 (10.3%); £3,773,473.54 -> £3,383,209.44 (10.3%); £3,773,473.79 -> £3,383,209.55 (10.3%); £3,773,473.99 -> £3,383,209.65 (10.3%); £3,773,474.18 -> £3,383,209.76 (10.3%); £3,773,474.37 -> £3,383,209.87 (10.3%); £3,773,474.63 -> £3,383,209.99 (10.3%); £3,773,474.89 -> £3,383,210.10 (10.3%); £3,773,475.14 -> £3,383,210.21 (10.3%); £3,773,475.40 -> £3,383,210.32 (10.3%); £3,773,475.67 -> £3,383,210.43 (10.3%); £3,773,475.94 -> £3,383,210.53 (10.3%); £3,773,476.19 -> £3,383,210.64 (10.3%); £3,773,476.44 -> £3,383,210.67 (10.3%); £3,773,476.71 -> £3,383,210.69 (10.3%); £3,773,476.95 -> £3,383,210.72 (10.3%); £3,773,477.16 -> £3,383,210.74 (10.3%); £3,773,477.37 -> £3,383,210.76 (10.3%); £3,773,477.52 -> £3,383,210.78 (10.3%); £3,773,477.68 -> £3,383,210.80 (10.3%); £3,773,477.83 -> £3,383,210.81 (10.3%); £3,773,477.98 -> £3,383,210.83 (10.3%); £3,773,478.14 -> £3,383,210.85 (10.3%); £3,773,478.30 -> £3,383,210.86 (10.3%); £3,773,478.46 -> £3,383,210.88 (10.3%); £3,773,478.62 -> £3,383,210.90 (10.3%); £3,773,478.78 -> £3,383,210.91 (10.3%); £3,773,478.94 -> £3,383,210.93 (10.3%); £3,773,479.09 -> £3,383,210.95 (10.3%); £3,773,479.25 -> £3,383,211.01 (10.3%); £3,773,479.40 -> £3,383,211.08 (10.3%); £3,773,479.57 -> £3,383,211.15 (10.3%); £3,773,479.77 -> £3,383,211.22 (10.3%); £3,773,479.98 -> £3,383,211.30 (10.3%); £3,773,480.21 -> £3,383,211.37 (10.3%); £3,773,480.45 -> £3,383,211.44 (10.3%); £3,773,480.71 -> £3,383,211.51 (10.3%); £3,773,480.98 -> £3,383,211.54 (10.3%); £3,773,481.25 -> £3,383,211.56 (10.3%); £3,773,481.51 -> £3,383,211.58 (10.3%); £3,773,481.77 -> £3,383,211.61 (10.3%); £3,773,482.04 -> £3,383,211.63 (10.3%); £3,773,482.29 -> £3,383,211.66 (10.3%); £3,773,482.56 -> £3,383,211.68 (10.3%); £3,773,482.82 -> £3,383,211.70 (10.3%); £3,773,483.08 -> £3,383,211.73 (10.3%); £3,773,483.33 -> £3,383,211.75 (10.3%); £3,773,483.59 -> £3,383,211.77 (10.3%); £3,773,483.85 -> £3,383,211.80 (10.3%); £3,773,484.11 -> £3,383,211.83 (10.3%); £3,773,484.37 -> £3,383,211.91 (10.3%); £3,773,484.63 -> £3,383,212.00 (10.3%); £3,773,484.89 -> £3,383,212.09 (10.3%); £3,773,485.15 -> £3,383,212.18 (10.3%); £3,773,485.41 -> £3,383,212.27 (10.3%); £3,773,485.68 -> £3,383,212.36 (10.3%); £3,773,485.94 -> £3,383,212.45 (10.3%); £3,773,486.20 -> £3,383,212.53 (10.3%); £3,773,486.46 -> £3,383,212.62 (10.3%); £3,773,486.71 -> £3,383,212.70 (10.3%); £3,773,486.96 -> £3,383,212.78 (10.3%); £3,773,487.22 -> £3,383,212.81 (10.3%); £3,773,487.48 -> £3,383,212.84 (10.3%); £3,773,487.71 -> £3,383,212.86 (10.3%); £3,773,487.94 -> £3,383,212.88 (10.3%); £3,773,488.14 -> £3,383,212.90 (10.3%); £3,773,488.30 -> £3,383,212.92 (10.3%); £3,773,488.45 -> £3,383,212.94 (10.3%); £3,773,488.61 -> £3,383,212.96 (10.3%); £3,773,488.77 -> £3,383,212.97 (10.3%); £3,773,488.93 -> £3,383,212.99 (10.3%); £3,773,489.08 -> £3,383,213.01 (10.3%); £3,773,489.24 -> £3,383,213.02 (10.3%); £3,773,489.40 -> £3,383,213.04 (10.3%); £3,773,489.56 -> £3,383,213.06 (10.3%); £3,773,489.72 -> £3,383,213.07 (10.3%); £3,773,489.88 -> £3,383,213.09 (10.3%); £3,773,490.04 -> £3,383,213.19 (10.3%); £3,773,490.19 -> £3,383,213.30 (10.3%); £3,773,490.37 -> £3,383,213.41 (10.3%); £3,773,490.57 -> £3,383,213.52 (10.3%); £3,773,490.78 -> £3,383,213.63 (10.3%); £3,773,491.00 -> £3,383,213.74 (10.3%); £3,773,491.25 -> £3,383,213.85 (10.3%); £3,773,491.52 -> £3,383,213.96 (10.3%); £3,773,491.78 -> £3,383,213.98 (10.3%); £3,773,492.05 -> £3,383,214.01 (10.3%); £3,773,492.30 -> £3,383,214.03 (10.3%); £3,773,492.55 -> £3,383,214.05 (10.3%); £3,773,492.82 -> £3,383,214.08 (10.3%); £3,773,493.08 -> £3,383,214.10 (10.3%); £3,773,493.34 -> £3,383,214.13 (10.3%); £3,773,493.59 -> £3,383,214.15 (10.3%); £3,773,493.86 -> £3,383,214.17 (10.3%); £3,773,494.12 -> £3,383,214.19 (10.3%); £3,773,494.37 -> £3,383,214.22 (10.3%); £3,773,494.64 -> £3,383,214.24 (10.3%); £3,773,494.90 -> £3,383,214.27 (10.3%); £3,773,495.10 -> £3,383,214.39 (10.3%); £3,773,495.37 -> £3,383,214.51 (10.3%); £3,773,495.56 -> £3,383,214.63 (10.3%); £3,773,495.75 -> £3,383,214.75 (10.3%); £3,773,495.95 -> £3,383,214.87 (10.3%); £3,773,496.15 -> £3,383,214.99 (10.3%); £3,773,496.34 -> £3,383,215.11 (10.3%); £3,773,496.60 -> £3,383,215.23 (10.3%); £3,773,496.86 -> £3,383,215.34 (10.3%); £3,773,497.12 -> £3,383,215.46 (10.3%); £3,773,497.38 -> £3,383,215.58 (10.3%); £3,773,497.65 -> £3,383,215.61 (10.3%); £3,773,497.92 -> £3,383,215.64 (10.3%); £3,773,498.16 -> £3,383,215.66 (10.3%); £3,773,498.38 -> £3,383,215.68 (10.3%); £3,773,498.58 -> £3,383,215.71 (10.3%); £3,773,498.72 -> £3,383,215.73 (10.3%); £3,773,498.86 -> £3,383,215.74 (10.3%); £3,773,499.00 -> £3,383,215.76 (10.3%); £3,773,499.13 -> £3,383,215.78 (10.3%); £3,773,499.28 -> £3,383,215.80 (10.3%); £3,773,499.41 -> £3,383,215.81 (10.3%); £3,773,499.55 -> £3,383,215.83 (10.3%); £3,773,499.69 -> £3,383,215.85 (10.3%); £3,773,499.83 -> £3,383,215.86 (10.3%); £3,773,499.96 -> £3,383,215.88 (10.3%); £3,773,500.10 -> £3,383,215.90 (10.3%); £3,773,500.24 -> £3,383,215.99 (10.3%); £3,773,500.38 -> £3,383,216.08 (10.3%); £3,773,500.53 -> £3,383,216.17 (10.3%); £3,773,500.70 -> £3,383,216.26 (10.3%); £3,773,500.88 -> £3,383,216.36 (10.3%); £3,773,501.09 -> £3,383,216.45 (10.3%); £3,773,501.30 -> £3,383,216.55 (10.3%); £3,773,501.52 -> £3,383,216.65 (10.3%); £3,773,501.74 -> £3,383,216.68 (10.3%); £3,773,501.96 -> £3,383,216.71 (10.3%); £3,773,502.19 -> £3,383,216.73 (10.3%); £3,773,502.42 -> £3,383,216.76 (10.3%); £3,773,502.66 -> £3,383,216.79 (10.3%); £3,773,502.88 -> £3,383,216.81 (10.3%); £3,773,503.11 -> £3,383,216.84 (10.3%); £3,773,503.33 -> £3,383,216.87 (10.3%); £3,773,503.55 -> £3,383,216.89 (10.3%); £3,773,503.79 -> £3,383,216.92 (10.3%); £3,773,504.01 -> £3,383,216.94 (10.3%); £3,773,504.24 -> £3,383,216.97 (10.3%); £3,773,504.47 -> £3,383,217.00 (10.3%); £3,773,504.64 -> £3,383,217.10 (10.3%); £3,773,504.81 -> £3,383,217.21 (10.3%); £3,773,504.98 -> £3,383,217.32 (10.3%); £3,773,505.15 -> £3,383,217.43 (10.3%); £3,773,505.33 -> £3,383,217.54 (10.3%); £3,773,505.50 -> £3,383,217.65 (10.3%); £3,773,505.67 -> £3,383,217.76 (10.3%); £3,773,505.90 -> £3,383,217.86 (10.3%); £3,773,506.12 -> £3,383,217.97 (10.3%); £3,773,506.36 -> £3,383,218.08 (10.3%); £3,773,506.58 -> £3,383,218.18 (10.3%); £3,773,506.80 -> £3,383,218.21 (10.3%); £3,773,507.04 -> £3,383,218.23 (10.3%); £3,773,507.25 -> £3,383,218.26 (10.3%); £3,773,507.44 -> £3,383,218.28 (10.3%); £3,773,507.62 -> £3,383,218.30 (10.3%); £3,773,507.76 -> £3,383,218.32 (10.3%); £3,773,507.90 -> £3,383,218.34 (10.3%); £3,773,508.03 -> £3,383,218.36 (10.3%); £3,773,508.17 -> £3,383,218.38 (10.3%); £3,773,508.31 -> £3,383,218.40 (10.3%); £3,773,508.45 -> £3,383,218.41 (10.3%); £3,773,508.59 -> £3,383,218.43 (10.3%); £3,773,508.73 -> £3,383,218.45 (10.3%); £3,773,508.87 -> £3,383,218.46 (10.3%); £3,773,509.00 -> £3,383,218.48 (10.3%); £3,773,509.14 -> £3,383,218.50 (10.3%); £3,773,509.27 -> £3,383,218.59 (10.3%); £3,773,509.41 -> £3,383,218.68 (10.3%); £3,773,509.57 -> £3,383,218.77 (10.3%); £3,773,509.74 -> £3,383,218.86 (10.3%); £3,773,509.92 -> £3,383,218.95 (10.3%); £3,773,510.12 -> £3,383,219.05 (10.3%); £3,773,510.33 -> £3,383,219.15 (10.3%); £3,773,510.56 -> £3,383,219.26 (10.3%); £3,773,510.79 -> £3,383,219.29 (10.3%); £3,773,511.02 -> £3,383,219.32 (10.3%); £3,773,511.25 -> £3,383,219.35 (10.3%); £3,773,511.48 -> £3,383,219.38 (10.3%); £3,773,511.71 -> £3,383,219.41 (10.3%); £3,773,511.94 -> £3,383,219.44 (10.3%); £3,773,512.17 -> £3,383,219.47 (10.3%); £3,773,512.40 -> £3,383,219.50 (10.3%); £3,773,512.63 -> £3,383,219.53 (10.3%); £3,773,512.86 -> £3,383,219.56 (10.3%); £3,773,513.09 -> £3,383,219.59 (10.3%); £3,773,513.32 -> £3,383,219.62 (10.3%); £3,773,513.55 -> £3,383,219.65 (10.3%); £3,773,513.79 -> £3,383,219.76 (10.3%); £3,773,514.02 -> £3,383,219.88 (10.3%); £3,773,514.25 -> £3,383,219.99 (10.3%); £3,773,514.42 -> £3,383,220.11 (10.3%); £3,773,514.64 -> £3,383,220.22 (10.3%); £3,773,514.82 -> £3,383,220.33 (10.3%); £3,773,514.99 -> £3,383,220.44 (10.3%); £3,773,515.22 -> £3,383,220.56 (10.3%); £3,773,515.45 -> £3,383,220.67 (10.3%); £3,773,515.68 -> £3,383,220.78 (10.3%); £3,773,515.91 -> £3,383,220.89 (10.3%); £3,773,516.13 -> £3,383,220.92 (10.3%); £3,773,516.36 -> £3,383,220.95 (10.3%); £3,773,516.56 -> £3,383,220.97 (10.3%); £3,773,516.76 -> £3,383,220.99 (10.3%); £3,773,516.93 -> £3,383,221.01 (10.3%); £3,773,517.09 -> £3,383,221.03 (10.3%); £3,773,517.25 -> £3,383,221.05 (10.3%); £3,773,517.41 -> £3,383,221.07 (10.3%); £3,773,517.58 -> £3,383,221.09 (10.3%); £3,773,517.74 -> £3,383,221.10 (10.3%); £3,773,517.90 -> £3,383,221.12 (10.3%); £3,773,518.05 -> £3,383,221.14 (10.3%); £3,773,518.21 -> £3,383,221.15 (10.3%); £3,773,518.37 -> £3,383,221.17 (10.3%); £3,773,518.52 -> £3,383,221.19 (10.3%); £3,773,518.69 -> £3,383,221.20 (10.3%); £3,773,518.85 -> £3,383,221.33 (10.3%); £3,773,519.01 -> £3,383,221.45 (10.3%); £3,773,519.18 -> £3,383,221.58 (10.3%); £3,773,519.38 -> £3,383,221.71 (10.3%); £3,773,519.59 -> £3,383,221.84 (10.3%); £3,773,519.82 -> £3,383,221.97 (10.3%); £3,773,520.06 -> £3,383,222.10 (10.3%); £3,773,520.32 -> £3,383,222.22 (10.3%); £3,773,520.58 -> £3,383,222.25 (10.3%); £3,773,520.84 -> £3,383,222.27 (10.3%); £3,773,521.10 -> £3,383,222.30 (10.3%); £3,773,521.37 -> £3,383,222.32 (10.3%); £3,773,521.64 -> £3,383,222.34 (10.3%); £3,773,521.90 -> £3,383,222.37 (10.3%); £3,773,522.17 -> £3,383,222.39 (10.3%); £3,773,522.43 -> £3,383,222.42 (10.3%); £3,773,522.71 -> £3,383,222.44 (10.3%); £3,773,522.97 -> £3,383,222.46 (10.3%); £3,773,523.24 -> £3,383,222.49 (10.3%); £3,773,523.49 -> £3,383,222.51 (10.3%); £3,773,523.76 -> £3,383,222.54 (10.3%); £3,773,524.01 -> £3,383,222.68 (10.3%); £3,773,524.21 -> £3,383,222.81 (10.3%); £3,773,524.41 -> £3,383,222.95 (10.3%); £3,773,524.60 -> £3,383,223.10 (10.3%); £3,773,524.86 -> £3,383,223.24 (10.3%); £3,773,525.12 -> £3,383,223.39 (10.3%); £3,773,525.39 -> £3,383,223.53 (10.3%); £3,773,525.66 -> £3,383,223.66 (10.3%); £3,773,525.92 -> £3,383,223.80 (10.3%); £3,773,526.19 -> £3,383,223.94 (10.3%); £3,773,526.45 -> £3,383,224.08 (10.3%); £3,773,526.72 -> £3,383,224.11 (10.3%); £3,773,526.98 -> £3,383,224.13 (10.3%); £3,773,527.23 -> £3,383,224.16 (10.3%); £3,773,527.45 -> £3,383,224.18 (10.3%); £3,773,527.66 -> £3,383,224.20 (10.3%); £3,773,527.81 -> £3,383,224.22 (10.3%); £3,773,527.97 -> £3,383,224.24 (10.3%); £3,773,528.13 -> £3,383,224.25 (10.3%); £3,773,528.29 -> £3,383,224.27 (10.3%); £3,773,528.45 -> £3,383,224.29 (10.3%); £3,773,528.61 -> £3,383,224.30 (10.3%); £3,773,528.77 -> £3,383,224.32 (10.3%); £3,773,528.93 -> £3,383,224.34 (10.3%); £3,773,529.08 -> £3,383,224.35 (10.3%); £3,773,529.24 -> £3,383,224.37 (10.3%); £3,773,529.40 -> £3,383,224.39 (10.3%); £3,773,529.56 -> £3,383,224.50 (10.3%); £3,773,529.71 -> £3,383,224.62 (10.3%); £3,773,529.89 -> £3,383,224.74 (10.3%); £3,773,530.08 -> £3,383,224.86 (10.3%); £3,773,530.29 -> £3,383,224.99 (10.3%); £3,773,530.53 -> £3,383,225.11 (10.3%); £3,773,530.78 -> £3,383,225.23 (10.3%); £3,773,531.04 -> £3,383,225.35 (10.3%); £3,773,531.30 -> £3,383,225.37 (10.3%); £3,773,531.57 -> £3,383,225.40 (10.3%); £3,773,531.84 -> £3,383,225.42 (10.3%); £3,773,532.10 -> £3,383,225.45 (10.3%); £3,773,532.36 -> £3,383,225.47 (10.3%); £3,773,532.63 -> £3,383,225.50 (10.3%); £3,773,532.89 -> £3,383,225.52 (10.3%); £3,773,533.15 -> £3,383,225.55 (10.3%); £3,773,533.41 -> £3,383,225.57 (10.3%); £3,773,533.68 -> £3,383,225.59 (10.3%); £3,773,533.95 -> £3,383,225.62 (10.3%); £3,773,534.21 -> £3,383,225.64 (10.3%); £3,773,534.48 -> £3,383,225.67 (10.3%); £3,773,534.75 -> £3,383,225.80 (10.3%); £3,773,535.00 -> £3,383,225.94 (10.3%); £3,773,535.27 -> £3,383,226.08 (10.3%); £3,773,535.54 -> £3,383,226.22 (10.3%); £3,773,535.79 -> £3,383,226.35 (10.3%); £3,773,536.07 -> £3,383,226.49 (10.3%); £3,773,536.26 -> £3,383,226.62 (10.3%); £3,773,536.52 -> £3,383,226.75 (10.3%); £3,773,536.77 -> £3,383,226.88 (10.3%); £3,773,537.04 -> £3,383,227.01 (10.3%); £3,773,537.31 -> £3,383,227.14 (10.3%); £3,773,537.58 -> £3,383,227.17 (10.3%); £3,773,537.84 -> £3,383,227.20 (10.3%); £3,773,538.08 -> £3,383,227.22 (10.3%); £3,773,538.31 -> £3,383,227.24 (10.3%); £3,773,538.51 -> £3,383,227.26 (10.3%); £3,773,538.68 -> £3,383,227.28 (10.3%); £3,773,538.83 -> £3,383,227.30 (10.3%); £3,773,539.00 -> £3,383,227.32 (10.3%); £3,773,539.16 -> £3,383,227.33 (10.3%); £3,773,539.32 -> £3,383,227.35 (10.3%); £3,773,539.48 -> £3,383,227.37 (10.3%); £3,773,539.64 -> £3,383,227.38 (10.3%); £3,773,539.80 -> £3,383,227.40 (10.3%); £3,773,539.96 -> £3,383,227.42 (10.3%); £3,773,540.12 -> £3,383,227.44 (10.3%); £3,773,540.28 -> £3,383,227.45 (10.3%); £3,773,540.45 -> £3,383,227.56 (10.3%); £3,773,540.61 -> £3,383,227.67 (10.3%); £3,773,540.79 -> £3,383,227.79 (10.3%); £3,773,540.98 -> £3,383,227.90 (10.3%); £3,773,541.19 -> £3,383,228.02 (10.3%); £3,773,541.42 -> £3,383,228.14 (10.3%); £3,773,541.67 -> £3,383,228.25 (10.3%); £3,773,541.94 -> £3,383,228.36 (10.3%); £3,773,542.21 -> £3,383,228.39 (10.3%); £3,773,542.47 -> £3,383,228.41 (10.3%); £3,773,542.74 -> £3,383,228.44 (10.3%); £3,773,543.01 -> £3,383,228.46 (10.3%); £3,773,543.27 -> £3,383,228.48 (10.3%); £3,773,543.53 -> £3,383,228.51 (10.3%); £3,773,543.80 -> £3,383,228.53 (10.3%); £3,773,544.07 -> £3,383,228.56 (10.3%); £3,773,544.34 -> £3,383,228.58 (10.3%); £3,773,544.61 -> £3,383,228.60 (10.3%); £3,773,544.87 -> £3,383,228.63 (10.3%); £3,773,545.15 -> £3,383,228.65 (10.3%); £3,773,545.41 -> £3,383,228.68 (10.3%); £3,773,545.68 -> £3,383,228.80 (10.3%); £3,773,545.94 -> £3,383,228.93 (10.3%); £3,773,546.21 -> £3,383,229.06 (10.3%); £3,773,546.47 -> £3,383,229.19 (10.3%); £3,773,546.68 -> £3,383,229.31 (10.3%); £3,773,546.87 -> £3,383,229.44 (10.3%); £3,773,547.14 -> £3,383,229.57 (10.3%); £3,773,547.40 -> £3,383,229.69 (10.3%); £3,773,547.66 -> £3,383,229.82 (10.3%); £3,773,547.94 -> £3,383,229.94 (10.3%); £3,773,548.21 -> £3,383,230.07 (10.3%); £3,773,548.47 -> £3,383,230.10 (10.3%); £3,773,548.74 -> £3,383,230.13 (10.3%); £3,773,548.99 -> £3,383,230.15 (10.3%); £3,773,549.21 -> £3,383,230.17 (10.3%); £3,773,549.42 -> £3,383,230.19 (10.3%); £3,773,549.57 -> £3,383,230.21 (10.3%); £3,773,549.73 -> £3,383,230.23 (10.3%); £3,773,549.89 -> £3,383,230.25 (10.3%); £3,773,550.05 -> £3,383,230.27 (10.3%); £3,773,550.21 -> £3,383,230.28 (10.3%); £3,773,550.38 -> £3,383,230.30 (10.3%); £3,773,550.54 -> £3,383,230.32 (10.3%); £3,773,550.70 -> £3,383,230.33 (10.3%); £3,773,550.86 -> £3,383,230.35 (10.3%); £3,773,551.02 -> £3,383,230.37 (10.3%); £3,773,551.18 -> £3,383,230.38 (10.3%); £3,773,551.34 -> £3,383,230.53 (10.3%); £3,773,551.50 -> £3,383,230.68 (10.3%); £3,773,551.68 -> £3,383,230.83 (10.3%); £3,773,551.88 -> £3,383,230.98 (10.3%); £3,773,552.09 -> £3,383,231.14 (10.3%); £3,773,552.33 -> £3,383,231.29 (10.3%); £3,773,552.58 -> £3,383,231.44 (10.3%); £3,773,552.85 -> £3,383,231.59 (10.3%); £3,773,553.11 -> £3,383,231.61 (10.3%); £3,773,553.38 -> £3,383,231.63 (10.3%); £3,773,553.65 -> £3,383,231.66 (10.3%); £3,773,553.91 -> £3,383,231.68 (10.3%); £3,773,554.17 -> £3,383,231.70 (10.3%); £3,773,554.44 -> £3,383,231.73 (10.3%); £3,773,554.72 -> £3,383,231.75 (10.3%); £3,773,555.00 -> £3,383,231.77 (10.3%); £3,773,555.26 -> £3,383,231.80 (10.3%); £3,773,555.52 -> £3,383,231.82 (10.3%); £3,773,555.78 -> £3,383,231.84 (10.3%); £3,773,556.05 -> £3,383,231.87 (10.3%); £3,773,556.32 -> £3,383,231.90 (10.3%); £3,773,556.59 -> £3,383,232.06 (10.3%); £3,773,556.87 -> £3,383,232.23 (10.3%); £3,773,557.14 -> £3,383,232.40 (10.3%); £3,773,557.40 -> £3,383,232.56 (10.3%); £3,773,557.60 -> £3,383,232.73 (10.3%); £3,773,557.87 -> £3,383,232.89 (10.3%); £3,773,558.15 -> £3,383,233.06 (10.3%); £3,773,558.41 -> £3,383,233.22 (10.3%); £3,773,558.69 -> £3,383,233.38 (10.3%); £3,773,558.96 -> £3,383,233.54 (10.3%); £3,773,559.23 -> £3,383,233.69 (10.3%); £3,773,559.49 -> £3,383,233.72 (10.3%); £3,773,559.76 -> £3,383,233.75 (10.3%); £3,773,560.00 -> £3,383,233.77 (10.3%); £3,773,560.23 -> £3,383,233.79 (10.3%); £3,773,560.43 -> £3,383,233.81 (10.3%); £3,773,560.60 -> £3,383,233.83 (10.3%); £3,773,560.76 -> £3,383,233.85 (10.3%); £3,773,560.92 -> £3,383,233.87 (10.3%); £3,773,561.08 -> £3,383,233.88 (10.3%); £3,773,561.23 -> £3,383,233.90 (10.3%); £3,773,561.40 -> £3,383,233.92 (10.3%); £3,773,561.56 -> £3,383,233.93 (10.3%); £3,773,561.72 -> £3,383,233.95 (10.3%); £3,773,561.88 -> £3,383,233.97 (10.3%); £3,773,562.04 -> £3,383,233.98 (10.3%); £3,773,562.20 -> £3,383,234.00 (10.3%); £3,773,562.36 -> £3,383,234.19 (10.3%); £3,773,562.52 -> £3,383,234.38 (10.3%); £3,773,562.69 -> £3,383,234.58 (10.3%); £3,773,562.89 -> £3,383,234.78 (10.3%); £3,773,563.11 -> £3,383,234.97 (10.3%); £3,773,563.33 -> £3,383,235.17 (10.3%); £3,773,563.59 -> £3,383,235.37 (10.3%); £3,773,563.86 -> £3,383,235.57 (10.3%); £3,773,564.12 -> £3,383,235.59 (10.3%); £3,773,564.38 -> £3,383,235.62 (10.3%); £3,773,564.63 -> £3,383,235.64 (10.3%); £3,773,564.89 -> £3,383,235.66 (10.3%); £3,773,565.16 -> £3,383,235.69 (10.3%); £3,773,565.42 -> £3,383,235.71 (10.3%); £3,773,565.68 -> £3,383,235.74 (10.3%); £3,773,565.96 -> £3,383,235.76 (10.3%); £3,773,566.23 -> £3,383,235.78 (10.3%); £3,773,566.49 -> £3,383,235.81 (10.3%); £3,773,566.76 -> £3,383,235.83 (10.3%); £3,773,567.02 -> £3,383,235.86 (10.3%); £3,773,567.28 -> £3,383,235.88 (10.3%); £3,773,567.55 -> £3,383,236.08 (10.3%); £3,773,567.80 -> £3,383,236.28 (10.3%); £3,773,568.01 -> £3,383,236.48 (10.3%); £3,773,568.21 -> £3,383,236.68 (10.3%); £3,773,568.40 -> £3,383,236.88 (10.3%); £3,773,568.61 -> £3,383,237.07 (10.3%); £3,773,568.81 -> £3,383,237.27 (10.3%); £3,773,569.07 -> £3,383,237.46 (10.3%); £3,773,569.34 -> £3,383,237.65 (10.3%); £3,773,569.61 -> £3,383,237.85 (10.3%); £3,773,569.87 -> £3,383,238.04 (10.3%); £3,773,570.14 -> £3,383,238.07 (10.3%); £3,773,570.40 -> £3,383,238.10 (10.3%); £3,773,570.65 -> £3,383,238.12 (10.3%); £3,773,570.86 -> £3,383,238.14 (10.3%); £3,773,571.07 -> £3,383,238.16 (10.3%); £3,773,571.21 -> £3,383,238.18 (10.3%); £3,773,571.35 -> £3,383,238.20 (10.3%); £3,773,571.49 -> £3,383,238.22 (10.3%); £3,773,571.63 -> £3,383,238.24 (10.3%); £3,773,571.77 -> £3,383,238.25 (10.3%); £3,773,571.91 -> £3,383,238.27 (10.3%); £3,773,572.05 -> £3,383,238.29 (10.3%); £3,773,572.19 -> £3,383,238.30 (10.3%); £3,773,572.33 -> £3,383,238.32 (10.3%); £3,773,572.47 -> £3,383,238.34 (10.3%); £3,773,572.61 -> £3,383,238.35 (10.3%); £3,773,572.76 -> £3,383,238.56 (10.3%); £3,773,572.90 -> £3,383,238.76 (10.3%); £3,773,573.05 -> £3,383,238.96 (10.3%); £3,773,573.22 -> £3,383,239.17 (10.3%); £3,773,573.41 -> £3,383,239.37 (10.3%); £3,773,573.62 -> £3,383,239.58 (10.3%); £3,773,573.84 -> £3,383,239.79 (10.3%); £3,773,574.08 -> £3,383,240.00 (10.3%); £3,773,574.31 -> £3,383,240.02 (10.3%); £3,773,574.55 -> £3,383,240.05 (10.3%); £3,773,574.78 -> £3,383,240.07 (10.3%); £3,773,575.01 -> £3,383,240.10 (10.3%); £3,773,575.25 -> £3,383,240.13 (10.3%); £3,773,575.48 -> £3,383,240.16 (10.3%); £3,773,575.71 -> £3,383,240.18 (10.3%); £3,773,575.94 -> £3,383,240.21 (10.3%); £3,773,576.18 -> £3,383,240.23 (10.3%); £3,773,576.41 -> £3,383,240.26 (10.3%); £3,773,576.66 -> £3,383,240.28 (10.3%); £3,773,576.90 -> £3,383,240.31 (10.3%); £3,773,577.14 -> £3,383,240.34 (10.3%); £3,773,577.31 -> £3,383,240.54 (10.3%); £3,773,577.48 -> £3,383,240.75 (10.3%); £3,773,577.66 -> £3,383,240.95 (10.3%); £3,773,577.84 -> £3,383,241.16 (10.3%); £3,773,578.01 -> £3,383,241.37 (10.3%); £3,773,578.19 -> £3,383,241.58 (10.3%); £3,773,578.37 -> £3,383,241.78 (10.3%); £3,773,578.61 -> £3,383,241.99 (10.3%); £3,773,578.85 -> £3,383,242.19 (10.3%); £3,773,579.08 -> £3,383,242.39 (10.3%); £3,773,579.32 -> £3,383,242.59 (10.3%); £3,773,579.55 -> £3,383,242.62 (10.3%); £3,773,579.78 -> £3,383,242.65 (10.3%); £3,773,580.00 -> £3,383,242.67 (10.3%); £3,773,580.20 -> £3,383,242.69 (10.3%); £3,773,580.38 -> £3,383,242.72 (10.3%); £3,773,580.53 -> £3,383,242.74 (10.3%); £3,773,580.67 -> £3,383,242.76 (10.3%); £3,773,580.81 -> £3,383,242.77 (10.3%); £3,773,580.95 -> £3,383,242.79 (10.3%); £3,773,581.09 -> £3,383,242.81 (10.3%); £3,773,581.23 -> £3,383,242.83 (10.3%); £3,773,581.36 -> £3,383,242.84 (10.3%); £3,773,581.50 -> £3,383,242.86 (10.3%); £3,773,581.65 -> £3,383,242.88 (10.3%); £3,773,581.78 -> £3,383,242.89 (10.3%); £3,773,581.92 -> £3,383,242.91 (10.3%); £3,773,582.07 -> £3,383,243.09 (10.3%); £3,773,582.21 -> £3,383,243.27 (10.3%); £3,773,582.36 -> £3,383,243.46 (10.3%); £3,773,582.53 -> £3,383,243.65 (10.3%); £3,773,582.72 -> £3,383,243.84 (10.3%); £3,773,582.92 -> £3,383,244.03 (10.3%); £3,773,583.14 -> £3,383,244.23 (10.3%); £3,773,583.37 -> £3,383,244.42 (10.3%); £3,773,583.61 -> £3,383,244.45 (10.3%); £3,773,583.85 -> £3,383,244.49 (10.3%); £3,773,584.09 -> £3,383,244.52 (10.3%); £3,773,584.32 -> £3,383,244.55 (10.3%); £3,773,584.55 -> £3,383,244.58 (10.3%); £3,773,584.78 -> £3,383,244.61 (10.3%); £3,773,585.02 -> £3,383,244.64 (10.3%); £3,773,585.26 -> £3,383,244.67 (10.3%); £3,773,585.49 -> £3,383,244.70 (10.3%); £3,773,585.72 -> £3,383,244.73 (10.3%); £3,773,585.95 -> £3,383,244.76 (10.3%); £3,773,586.19 -> £3,383,244.79 (10.3%); £3,773,586.42 -> £3,383,244.82 (10.3%); £3,773,586.60 -> £3,383,245.01 (10.3%); £3,773,586.77 -> £3,383,245.20 (10.3%); £3,773,586.96 -> £3,383,245.39 (10.3%); £3,773,587.13 -> £3,383,245.59 (10.3%); £3,773,587.36 -> £3,383,245.79 (10.3%); £3,773,587.60 -> £3,383,245.99 (10.3%); £3,773,587.77 -> £3,383,246.19 (10.3%); £3,773,588.01 -> £3,383,246.39 (10.3%); £3,773,588.24 -> £3,383,246.58 (10.3%); £3,773,588.47 -> £3,383,246.78 (10.3%); £3,773,588.70 -> £3,383,246.97 (10.3%); £3,773,588.94 -> £3,383,247.00 (10.3%); £3,773,589.17 -> £3,383,247.03 (10.3%); £3,773,589.39 -> £3,383,247.05 (10.3%); £3,773,589.59 -> £3,383,247.08 (10.3%); £3,773,589.76 -> £3,383,247.10 (10.3%); £3,773,589.92 -> £3,383,247.12 (10.3%); £3,773,590.08 -> £3,383,247.13 (10.3%); £3,773,590.24 -> £3,383,247.15 (10.3%); £3,773,590.40 -> £3,383,247.17 (10.3%); £3,773,590.56 -> £3,383,247.18 (10.3%); £3,773,590.72 -> £3,383,247.20 (10.3%); £3,773,590.88 -> £3,383,247.22 (10.3%); £3,773,591.04 -> £3,383,247.23 (10.3%); £3,773,591.20 -> £3,383,247.25 (10.3%); £3,773,591.36 -> £3,383,247.27 (10.3%); £3,773,591.52 -> £3,383,247.29 (10.3%); £3,773,591.68 -> £3,383,247.45 (10.3%); £3,773,591.84 -> £3,383,247.62 (10.3%); £3,773,592.01 -> £3,383,247.79 (10.3%); £3,773,592.21 -> £3,383,247.97 (10.3%); £3,773,592.43 -> £3,383,248.15 (10.3%); £3,773,592.66 -> £3,383,248.32 (10.3%); £3,773,592.90 -> £3,383,248.49 (10.3%); £3,773,593.16 -> £3,383,248.66 (10.3%); £3,773,593.42 -> £3,383,248.69 (10.3%); £3,773,593.69 -> £3,383,248.71 (10.3%); £3,773,593.96 -> £3,383,248.74 (10.3%); £3,773,594.22 -> £3,383,248.76 (10.3%); £3,773,594.49 -> £3,383,248.78 (10.3%); £3,773,594.74 -> £3,383,248.81 (10.3%); £3,773,595.00 -> £3,383,248.83 (10.3%); £3,773,595.28 -> £3,383,248.86 (10.3%); £3,773,595.54 -> £3,383,248.88 (10.3%); £3,773,595.80 -> £3,383,248.90 (10.3%); £3,773,596.07 -> £3,383,248.93 (10.3%); £3,773,596.33 -> £3,383,248.95 (10.3%); £3,773,596.59 -> £3,383,248.98 (10.3%); £3,773,596.86 -> £3,383,249.16 (10.3%); £3,773,597.13 -> £3,383,249.35 (10.3%); £3,773,597.39 -> £3,383,249.53 (10.3%); £3,773,597.65 -> £3,383,249.71 (10.3%); £3,773,597.91 -> £3,383,249.90 (10.3%); £3,773,598.17 -> £3,383,250.08 (10.3%); £3,773,598.37 -> £3,383,250.26 (10.3%); £3,773,598.63 -> £3,383,250.44 (10.3%); £3,773,598.89 -> £3,383,250.62 (10.3%); £3,773,599.15 -> £3,383,250.80 (10.3%); £3,773,599.40 -> £3,383,250.97 (10.3%); £3,773,599.66 -> £3,383,251.00 (10.3%); £3,773,599.92 -> £3,383,251.03 (10.3%); £3,773,600.18 -> £3,383,251.05 (10.3%); £3,773,600.40 -> £3,383,251.07 (10.3%); £3,773,600.61 -> £3,383,251.09 (10.3%); £3,773,600.76 -> £3,383,251.11 (10.3%); £3,773,600.92 -> £3,383,251.13 (10.3%); £3,773,601.08 -> £3,383,251.15 (10.3%); £3,773,601.23 -> £3,383,251.17 (10.3%); £3,773,601.39 -> £3,383,251.18 (10.3%); £3,773,601.55 -> £3,383,251.20 (10.3%); £3,773,601.70 -> £3,383,251.22 (10.3%); £3,773,601.86 -> £3,383,251.23 (10.3%); £3,773,602.02 -> £3,383,251.25 (10.3%); £3,773,602.17 -> £3,383,251.27 (10.3%); £3,773,602.32 -> £3,383,251.28 (10.3%); £3,773,602.48 -> £3,383,251.47 (10.3%); £3,773,602.64 -> £3,383,251.67 (10.3%); £3,773,602.82 -> £3,383,251.87 (10.3%); £3,773,603.01 -> £3,383,252.07 (10.3%); £3,773,603.22 -> £3,383,252.27 (10.3%); £3,773,603.45 -> £3,383,252.47 (10.3%); £3,773,603.70 -> £3,383,252.66 (10.3%); £3,773,603.96 -> £3,383,252.86 (10.3%); £3,773,604.21 -> £3,383,252.88 (10.3%); £3,773,604.47 -> £3,383,252.91 (10.3%); £3,773,604.73 -> £3,383,252.93 (10.3%); £3,773,604.98 -> £3,383,252.95 (10.3%); £3,773,605.24 -> £3,383,252.98 (10.3%); £3,773,605.50 -> £3,383,253.00 (10.3%); £3,773,605.77 -> £3,383,253.03 (10.3%); £3,773,606.03 -> £3,383,253.05 (10.3%); £3,773,606.28 -> £3,383,253.07 (10.3%); £3,773,606.56 -> £3,383,253.10 (10.3%); £3,773,606.81 -> £3,383,253.12 (10.3%); £3,773,607.06 -> £3,383,253.15 (10.3%); £3,773,607.33 -> £3,383,253.18 (10.3%); £3,773,607.60 -> £3,383,253.37 (10.3%); £3,773,607.86 -> £3,383,253.57 (10.3%); £3,773,608.05 -> £3,383,253.77 (10.3%); £3,773,608.25 -> £3,383,253.97 (10.3%); £3,773,608.45 -> £3,383,254.17 (10.3%); £3,773,608.65 -> £3,383,254.37 (10.3%); £3,773,608.91 -> £3,383,254.57 (10.3%); £3,773,609.16 -> £3,383,254.77 (10.3%); £3,773,609.43 -> £3,383,254.97 (10.3%); £3,773,609.70 -> £3,383,255.17 (10.3%); £3,773,609.96 -> £3,383,255.36 (10.3%); £3,773,610.22 -> £3,383,255.39 (10.3%); £3,773,610.48 -> £3,383,255.42 (10.3%); £3,773,610.72 -> £3,383,255.45 (10.3%); £3,773,610.95 -> £3,383,255.47 (10.3%); £3,773,611.15 -> £3,383,255.49 (10.3%); £3,773,611.31 -> £3,383,255.51 (10.3%); £3,773,611.47 -> £3,383,255.52 (10.3%); £3,773,611.62 -> £3,383,255.54 (10.3%); £3,773,611.78 -> £3,383,255.56 (10.3%); £3,773,611.94 -> £3,383,255.58 (10.3%); £3,773,612.09 -> £3,383,255.59 (10.3%); £3,773,612.25 -> £3,383,255.61 (10.3%); £3,773,612.41 -> £3,383,255.63 (10.3%); £3,773,612.57 -> £3,383,255.64 (10.3%); £3,773,612.72 -> £3,383,255.66 (10.3%); £3,773,612.88 -> £3,383,255.68 (10.3%); £3,773,613.04 -> £3,383,255.82 (10.3%); £3,773,613.19 -> £3,383,255.97 (10.3%); £3,773,613.38 -> £3,383,256.13 (10.3%); £3,773,613.57 -> £3,383,256.28 (10.3%); £3,773,613.77 -> £3,383,256.44 (10.3%); £3,773,614.00 -> £3,383,256.60 (10.3%); £3,773,614.24 -> £3,383,256.75 (10.3%); £3,773,614.49 -> £3,383,256.91 (10.3%); £3,773,614.75 -> £3,383,256.93 (10.3%); £3,773,615.01 -> £3,383,256.96 (10.3%); £3,773,615.26 -> £3,383,256.98 (10.3%); £3,773,615.53 -> £3,383,257.01 (10.3%); £3,773,615.80 -> £3,383,257.03 (10.3%); £3,773,616.06 -> £3,383,257.05 (10.3%); £3,773,616.32 -> £3,383,257.08 (10.3%); £3,773,616.59 -> £3,383,257.10 (10.3%); £3,773,616.85 -> £3,383,257.12 (10.3%); £3,773,617.11 -> £3,383,257.15 (10.3%); £3,773,617.37 -> £3,383,257.17 (10.3%); £3,773,617.64 -> £3,383,257.20 (10.3%); £3,773,617.90 -> £3,383,257.23 (10.3%); £3,773,618.09 -> £3,383,257.39 (10.3%); £3,773,618.35 -> £3,383,257.55 (10.3%); £3,773,618.55 -> £3,383,257.72 (10.3%); £3,773,618.76 -> £3,383,257.89 (10.3%); £3,773,619.02 -> £3,383,258.05 (10.3%); £3,773,619.28 -> £3,383,258.22 (10.3%); £3,773,619.48 -> £3,383,258.38 (10.3%); £3,773,619.74 -> £3,383,258.54 (10.3%); £3,773,619.99 -> £3,383,258.70 (10.3%); £3,773,620.26 -> £3,383,258.86 (10.3%); £3,773,620.53 -> £3,383,259.02 (10.3%); £3,773,620.80 -> £3,383,259.05 (10.3%); £3,773,621.06 -> £3,383,259.07 (10.3%); £3,773,621.30 -> £3,383,259.10 (10.3%); £3,773,621.53 -> £3,383,259.12 (10.3%); £3,773,621.73 -> £3,383,259.14 (10.3%); £3,773,621.89 -> £3,383,259.16 (10.3%); £3,773,622.04 -> £3,383,259.18 (10.3%); £3,773,622.20 -> £3,383,259.19 (10.3%); £3,773,622.35 -> £3,383,259.21 (10.3%); £3,773,622.51 -> £3,383,259.23 (10.3%); £3,773,622.66 -> £3,383,259.24 (10.3%); £3,773,622.82 -> £3,383,259.26 (10.3%); £3,773,622.97 -> £3,383,259.28 (10.3%); £3,773,623.13 -> £3,383,259.29 (10.3%); £3,773,623.28 -> £3,383,259.31 (10.3%); £3,773,623.44 -> £3,383,259.33 (10.3%); £3,773,623.59 -> £3,383,259.46 (10.3%); £3,773,623.75 -> £3,383,259.60 (10.3%); £3,773,623.92 -> £3,383,259.73 (10.3%); £3,773,624.10 -> £3,383,259.87 (10.3%); £3,773,624.31 -> £3,383,260.01 (10.3%); £3,773,624.54 -> £3,383,260.14 (10.3%); £3,773,624.78 -> £3,383,260.27 (10.3%); £3,773,625.03 -> £3,383,260.40 (10.3%); £3,773,625.30 -> £3,383,260.43 (10.3%); £3,773,625.56 -> £3,383,260.45 (10.3%); £3,773,625.82 -> £3,383,260.48 (10.3%); £3,773,626.07 -> £3,383,260.50 (10.3%); £3,773,626.33 -> £3,383,260.52 (10.3%); £3,773,626.58 -> £3,383,260.55 (10.3%); £3,773,626.83 -> £3,383,260.57 (10.3%); £3,773,627.09 -> £3,383,260.60 (10.3%); £3,773,627.36 -> £3,383,260.62 (10.3%); £3,773,627.61 -> £3,383,260.64 (10.3%); £3,773,627.86 -> £3,383,260.67 (10.3%); £3,773,628.11 -> £3,383,260.69 (10.3%); £3,773,628.37 -> £3,383,260.72 (10.3%); £3,773,628.62 -> £3,383,260.86 (10.3%); £3,773,628.88 -> £3,383,261.01 (10.3%); £3,773,629.14 -> £3,383,261.15 (10.3%); £3,773,629.33 -> £3,383,261.30 (10.3%); £3,773,629.53 -> £3,383,261.45 (10.3%); £3,773,629.79 -> £3,383,261.59 (10.3%); £3,773,629.98 -> £3,383,261.73 (10.3%); £3,773,630.24 -> £3,383,261.87 (10.3%); £3,773,630.49 -> £3,383,262.01 (10.3%); £3,773,630.75 -> £3,383,262.15 (10.3%); £3,773,631.01 -> £3,383,262.28 (10.3%); £3,773,631.27 -> £3,383,262.31 (10.3%); £3,773,631.53 -> £3,383,262.34 (10.3%); £3,773,631.77 -> £3,383,262.36 (10.3%); £3,773,632.00 -> £3,383,262.39 (10.3%); £3,773,632.19 -> £3,383,262.41 (10.3%); £3,773,632.35 -> £3,383,262.42 (10.3%); £3,773,632.50 -> £3,383,262.44 (10.3%); £3,773,632.66 -> £3,383,262.46 (10.3%); £3,773,632.82 -> £3,383,262.48 (10.3%); £3,773,632.98 -> £3,383,262.49 (10.3%); £3,773,633.14 -> £3,383,262.51 (10.3%); £3,773,633.29 -> £3,383,262.53 (10.3%); £3,773,633.44 -> £3,383,262.54 (10.3%); £3,773,633.60 -> £3,383,262.56 (10.3%); £3,773,633.76 -> £3,383,262.58 (10.3%); £3,773,633.91 -> £3,383,262.59 (10.3%); £3,773,634.06 -> £3,383,262.78 (10.3%); £3,773,634.22 -> £3,383,262.97 (10.3%); £3,773,634.39 -> £3,383,263.16 (10.3%); £3,773,634.58 -> £3,383,263.36 (10.3%); £3,773,634.78 -> £3,383,263.56 (10.3%); £3,773,635.00 -> £3,383,263.76 (10.3%); £3,773,635.23 -> £3,383,263.95 (10.3%); £3,773,635.49 -> £3,383,264.15 (10.3%); £3,773,635.75 -> £3,383,264.17 (10.3%); £3,773,636.02 -> £3,383,264.20 (10.3%); £3,773,636.28 -> £3,383,264.22 (10.3%); £3,773,636.54 -> £3,383,264.24 (10.3%); £3,773,636.80 -> £3,383,264.27 (10.3%); £3,773,637.07 -> £3,383,264.29 (10.3%); £3,773,637.32 -> £3,383,264.32 (10.3%); £3,773,637.58 -> £3,383,264.34 (10.3%); £3,773,637.85 -> £3,383,264.36 (10.3%); £3,773,638.11 -> £3,383,264.39 (10.3%); £3,773,638.37 -> £3,383,264.41 (10.3%); £3,773,638.63 -> £3,383,264.43 (10.3%); £3,773,638.89 -> £3,383,264.46 (10.3%); £3,773,639.14 -> £3,383,264.66 (10.3%); £3,773,639.40 -> £3,383,264.86 (10.3%); £3,773,639.67 -> £3,383,265.06 (10.3%); £3,773,639.93 -> £3,383,265.26 (10.3%); £3,773,640.20 -> £3,383,265.46 (10.3%); £3,773,640.46 -> £3,383,265.66 (10.3%); £3,773,640.73 -> £3,383,265.87 (10.3%); £3,773,640.99 -> £3,383,266.06 (10.3%); £3,773,641.25 -> £3,383,266.26 (10.3%); £3,773,641.51 -> £3,383,266.46 (10.3%); £3,773,641.78 -> £3,383,266.66 (10.3%); £3,773,642.04 -> £3,383,266.69 (10.3%); £3,773,642.30 -> £3,383,266.71 (10.3%); £3,773,642.54 -> £3,383,266.74 (10.3%); £3,773,642.76 -> £3,383,266.76 (10.3%); £3,773,642.96 -> £3,383,266.78 (10.3%); £3,773,643.10 -> £3,383,266.80 (10.3%); £3,773,643.24 -> £3,383,266.82 (10.3%); £3,773,643.37 -> £3,383,266.84 (10.3%); £3,773,643.50 -> £3,383,266.85 (10.3%); £3,773,643.64 -> £3,383,266.87 (10.3%); £3,773,643.78 -> £3,383,266.89 (10.3%); £3,773,643.91 -> £3,383,266.90 (10.3%); £3,773,644.05 -> £3,383,266.92 (10.3%); £3,773,644.18 -> £3,383,266.94 (10.3%); £3,773,644.32 -> £3,383,266.95 (10.3%); £3,773,644.46 -> £3,383,266.97 (10.3%); £3,773,644.60 -> £3,383,267.17 (10.3%); £3,773,644.73 -> £3,383,267.37 (10.3%); £3,773,644.89 -> £3,383,267.57 (10.3%); £3,773,645.06 -> £3,383,267.77 (10.3%); £3,773,645.24 -> £3,383,267.98 (10.3%); £3,773,645.43 -> £3,383,268.18 (10.3%); £3,773,645.65 -> £3,383,268.38 (10.3%); £3,773,645.87 -> £3,383,268.58 (10.3%); £3,773,646.10 -> £3,383,268.60 (10.3%); £3,773,646.32 -> £3,383,268.63 (10.3%); £3,773,646.55 -> £3,383,268.66 (10.3%); £3,773,646.77 -> £3,383,268.68 (10.3%); £3,773,646.99 -> £3,383,268.71 (10.3%); £3,773,647.21 -> £3,383,268.74 (10.3%); £3,773,647.44 -> £3,383,268.76 (10.3%); £3,773,647.68 -> £3,383,268.79 (10.3%); £3,773,647.91 -> £3,383,268.81 (10.3%); £3,773,648.14 -> £3,383,268.84 (10.3%); £3,773,648.36 -> £3,383,268.87 (10.3%); £3,773,648.59 -> £3,383,268.89 (10.3%); £3,773,648.82 -> £3,383,268.92 (10.3%); £3,773,649.04 -> £3,383,269.12 (10.3%); £3,773,649.27 -> £3,383,269.33 (10.3%); £3,773,649.50 -> £3,383,269.54 (10.3%); £3,773,649.72 -> £3,383,269.75 (10.3%); £3,773,649.94 -> £3,383,269.95 (10.3%); £3,773,650.17 -> £3,383,270.16 (10.3%); £3,773,650.40 -> £3,383,270.37 (10.3%); £3,773,650.63 -> £3,383,270.58 (10.3%); £3,773,650.86 -> £3,383,270.79 (10.3%); £3,773,651.09 -> £3,383,270.99 (10.3%); £3,773,651.32 -> £3,383,271.20 (10.3%); £3,773,651.54 -> £3,383,271.23 (10.3%); £3,773,651.76 -> £3,383,271.25 (10.3%); £3,773,651.97 -> £3,383,271.28 (10.3%); £3,773,652.17 -> £3,383,271.30 (10.3%); £3,773,652.34 -> £3,383,271.32 (10.3%); £3,773,652.47 -> £3,383,271.34 (10.3%); £3,773,652.61 -> £3,383,271.36 (10.3%); £3,773,652.74 -> £3,383,271.38 (10.3%); £3,773,652.88 -> £3,383,271.40 (10.3%); £3,773,653.01 -> £3,383,271.42 (10.3%); £3,773,653.15 -> £3,383,271.43 (10.3%); £3,773,653.28 -> £3,383,271.45 (10.3%); £3,773,653.41 -> £3,383,271.47 (10.3%); £3,773,653.55 -> £3,383,271.48 (10.3%); £3,773,653.69 -> £3,383,271.50 (10.3%); £3,773,653.83 -> £3,383,271.52 (10.3%); £3,773,653.96 -> £3,383,271.70 (10.3%); £3,773,654.10 -> £3,383,271.89 (10.3%); £3,773,654.26 -> £3,383,272.07 (10.3%); £3,773,654.42 -> £3,383,272.27 (10.3%); £3,773,654.60 -> £3,383,272.46 (10.3%); £3,773,654.79 -> £3,383,272.66 (10.3%); £3,773,655.01 -> £3,383,272.86 (10.3%); £3,773,655.23 -> £3,383,273.07 (10.3%); £3,773,655.45 -> £3,383,273.10 (10.3%); £3,773,655.68 -> £3,383,273.13 (10.3%); £3,773,655.91 -> £3,383,273.16 (10.3%); £3,773,656.13 -> £3,383,273.19 (10.3%); £3,773,656.35 -> £3,383,273.22 (10.3%); £3,773,656.57 -> £3,383,273.26 (10.3%); £3,773,656.80 -> £3,383,273.29 (10.3%); £3,773,657.03 -> £3,383,273.32 (10.3%); £3,773,657.26 -> £3,383,273.34 (10.3%); £3,773,657.48 -> £3,383,273.37 (10.3%); £3,773,657.70 -> £3,383,273.40 (10.3%); £3,773,657.94 -> £3,383,273.43 (10.3%); £3,773,658.17 -> £3,383,273.46 (10.3%); £3,773,658.41 -> £3,383,273.66 (10.3%); £3,773,658.63 -> £3,383,273.86 (10.3%); £3,773,658.86 -> £3,383,274.06 (10.3%); £3,773,659.08 -> £3,383,274.26 (10.3%); £3,773,659.30 -> £3,383,274.46 (10.3%); £3,773,659.53 -> £3,383,274.67 (10.3%); £3,773,659.75 -> £3,383,274.87 (10.3%); £3,773,659.97 -> £3,383,275.07 (10.3%); £3,773,660.19 -> £3,383,275.28 (10.3%); £3,773,660.42 -> £3,383,275.47 (10.3%); £3,773,660.66 -> £3,383,275.67 (10.3%); £3,773,660.89 -> £3,383,275.70 (10.3%); £3,773,661.11 -> £3,383,275.73 (10.3%); £3,773,661.32 -> £3,383,275.75 (10.3%); £3,773,661.52 -> £3,383,275.77 (10.3%); £3,773,661.69 -> £3,383,275.79 (10.3%); £3,773,661.84 -> £3,383,275.81 (10.3%); £3,773,662.00 -> £3,383,275.83 (10.3%); £3,773,662.15 -> £3,383,275.85 (10.3%); £3,773,662.31 -> £3,383,275.86 (10.3%); £3,773,662.47 -> £3,383,275.88 (10.3%); £3,773,662.62 -> £3,383,275.90 (10.3%); £3,773,662.78 -> £3,383,275.91 (10.3%); £3,773,662.93 -> £3,383,275.93 (10.3%); £3,773,663.08 -> £3,383,275.95 (10.3%); £3,773,663.23 -> £3,383,275.96 (10.3%); £3,773,663.39 -> £3,383,275.98 (10.3%); £3,773,663.55 -> £3,383,276.15 (10.3%); £3,773,663.70 -> £3,383,276.32 (10.3%); £3,773,663.87 -> £3,383,276.49 (10.3%); £3,773,664.06 -> £3,383,276.67 (10.3%); £3,773,664.27 -> £3,383,276.85 (10.3%); £3,773,664.49 -> £3,383,277.03 (10.3%); £3,773,664.74 -> £3,383,277.21 (10.3%); £3,773,665.00 -> £3,383,277.39 (10.3%); £3,773,665.25 -> £3,383,277.42 (10.3%); £3,773,665.52 -> £3,383,277.44 (10.3%); £3,773,665.78 -> £3,383,277.46 (10.3%); £3,773,666.03 -> £3,383,277.49 (10.3%); £3,773,666.29 -> £3,383,277.51 (10.3%); £3,773,666.55 -> £3,383,277.54 (10.3%); £3,773,666.81 -> £3,383,277.56 (10.3%); £3,773,667.07 -> £3,383,277.58 (10.3%); £3,773,667.34 -> £3,383,277.61 (10.3%); £3,773,667.59 -> £3,383,277.63 (10.3%); £3,773,667.84 -> £3,383,277.65 (10.3%); £3,773,668.11 -> £3,383,277.68 (10.3%); £3,773,668.37 -> £3,383,277.71 (10.3%); £3,773,668.62 -> £3,383,277.89 (10.3%); £3,773,668.87 -> £3,383,278.08 (10.3%); £3,773,669.12 -> £3,383,278.26 (10.3%); £3,773,669.38 -> £3,383,278.44 (10.3%); £3,773,669.63 -> £3,383,278.63 (10.3%); £3,773,669.88 -> £3,383,278.81 (10.3%); £3,773,670.15 -> £3,383,279.00 (10.3%); £3,773,670.41 -> £3,383,279.18 (10.3%); £3,773,670.66 -> £3,383,279.37 (10.3%); £3,773,670.92 -> £3,383,279.55 (10.3%); £3,773,671.18 -> £3,383,279.72 (10.3%); £3,773,671.44 -> £3,383,279.75 (10.3%); £3,773,671.70 -> £3,383,279.78 (10.3%); £3,773,671.94 -> £3,383,279.81 (10.3%); £3,773,672.15 -> £3,383,279.83 (10.3%); £3,773,672.35 -> £3,383,279.85 (10.3%); £3,773,672.50 -> £3,383,279.87 (10.3%); £3,773,672.66 -> £3,383,279.88 (10.3%); £3,773,672.81 -> £3,383,279.90 (10.3%); £3,773,672.97 -> £3,383,279.92 (10.3%); £3,773,673.12 -> £3,383,279.93 (10.3%); £3,773,673.28 -> £3,383,279.95 (10.3%); £3,773,673.43 -> £3,383,279.97 (10.3%); £3,773,673.58 -> £3,383,279.98 (10.3%); £3,773,673.73 -> £3,383,280.00 (10.3%); £3,773,673.88 -> £3,383,280.02 (10.3%); £3,773,674.03 -> £3,383,280.04 (10.3%); £3,773,674.19 -> £3,383,280.18 (10.3%); £3,773,674.34 -> £3,383,280.32 (10.3%); £3,773,674.51 -> £3,383,280.47 (10.3%); £3,773,674.70 -> £3,383,280.62 (10.3%); £3,773,674.90 -> £3,383,280.77 (10.3%); £3,773,675.13 -> £3,383,280.92 (10.3%); £3,773,675.36 -> £3,383,281.07 (10.3%); £3,773,675.63 -> £3,383,281.21 (10.3%); £3,773,675.88 -> £3,383,281.24 (10.3%); £3,773,676.14 -> £3,383,281.26 (10.3%); £3,773,676.40 -> £3,383,281.29 (10.3%); £3,773,676.65 -> £3,383,281.31 (10.3%); £3,773,676.90 -> £3,383,281.33 (10.3%); £3,773,677.16 -> £3,383,281.36 (10.3%); £3,773,677.42 -> £3,383,281.38 (10.3%); £3,773,677.67 -> £3,383,281.41 (10.3%); £3,773,677.92 -> £3,383,281.43 (10.3%); £3,773,678.18 -> £3,383,281.45 (10.3%); £3,773,678.43 -> £3,383,281.48 (10.3%); £3,773,678.70 -> £3,383,281.50 (10.3%); £3,773,678.96 -> £3,383,281.53 (10.3%); £3,773,679.22 -> £3,383,281.69 (10.3%); £3,773,679.48 -> £3,383,281.85 (10.3%); £3,773,679.73 -> £3,383,282.00 (10.3%); £3,773,679.98 -> £3,383,282.16 (10.3%); £3,773,680.25 -> £3,383,282.32 (10.3%); £3,773,680.50 -> £3,383,282.47 (10.3%); £3,773,680.76 -> £3,383,282.63 (10.3%); £3,773,681.02 -> £3,383,282.78 (10.3%); £3,773,681.28 -> £3,383,282.94 (10.3%); £3,773,681.52 -> £3,383,283.09 (10.3%); £3,773,681.78 -> £3,383,283.25 (10.3%); £3,773,682.04 -> £3,383,283.28 (10.3%); £3,773,682.30 -> £3,383,283.30 (10.3%); £3,773,682.54 -> £3,383,283.33 (10.3%); £3,773,682.75 -> £3,383,283.35 (10.3%); £3,773,682.95 -> £3,383,283.37 (10.3%); £3,773,683.10 -> £3,383,283.39 (10.3%); £3,773,683.25 -> £3,383,283.41 (10.3%); £3,773,683.40 -> £3,383,283.42 (10.3%); £3,773,683.55 -> £3,383,283.44 (10.3%); £3,773,683.70 -> £3,383,283.46 (10.3%); £3,773,683.85 -> £3,383,283.47 (10.3%); £3,773,684.00 -> £3,383,283.49 (10.3%); £3,773,684.16 -> £3,383,283.51 (10.3%); £3,773,684.31 -> £3,383,283.52 (10.3%); £3,773,684.46 -> £3,383,283.54 (10.3%); £3,773,684.61 -> £3,383,283.56 (10.3%); £3,773,684.76 -> £3,383,283.72 (10.3%); £3,773,684.92 -> £3,383,283.89 (10.3%); £3,773,685.09 -> £3,383,284.06 (10.3%); £3,773,685.28 -> £3,383,284.23 (10.3%); £3,773,685.49 -> £3,383,284.41 (10.3%); £3,773,685.71 -> £3,383,284.58 (10.3%); £3,773,685.95 -> £3,383,284.76 (10.3%); £3,773,686.20 -> £3,383,284.94 (10.3%); £3,773,686.45 -> £3,383,284.96 (10.3%); £3,773,686.70 -> £3,383,284.98 (10.3%); £3,773,686.96 -> £3,383,285.01 (10.3%); £3,773,687.21 -> £3,383,285.03 (10.3%); £3,773,687.48 -> £3,383,285.06 (10.3%); £3,773,687.74 -> £3,383,285.08 (10.3%); £3,773,688.00 -> £3,383,285.11 (10.3%); £3,773,688.26 -> £3,383,285.13 (10.3%); £3,773,688.52 -> £3,383,285.15 (10.3%); £3,773,688.77 -> £3,383,285.17 (10.3%); £3,773,689.02 -> £3,383,285.20 (10.3%); £3,773,689.27 -> £3,383,285.22 (10.3%); £3,773,689.53 -> £3,383,285.25 (10.3%); £3,773,689.79 -> £3,383,285.44 (10.3%); £3,773,690.05 -> £3,383,285.62 (10.3%); £3,773,690.32 -> £3,383,285.80 (10.3%); £3,773,690.58 -> £3,383,285.98 (10.3%); £3,773,690.83 -> £3,383,286.16 (10.3%); £3,773,691.09 -> £3,383,286.34 (10.3%); £3,773,691.34 -> £3,383,286.52 (10.3%); £3,773,691.59 -> £3,383,286.69 (10.3%); £3,773,691.85 -> £3,383,286.88 (10.3%); £3,773,692.10 -> £3,383,287.06 (10.3%); £3,773,692.36 -> £3,383,287.24 (10.3%); £3,773,692.61 -> £3,383,287.27 (10.3%); £3,773,692.87 -> £3,383,287.30 (10.3%); £3,773,693.10 -> £3,383,287.32 (10.3%); £3,773,693.32 -> £3,383,287.34 (10.3%); £3,773,693.52 -> £3,383,287.36 (10.3%); £3,773,693.67 -> £3,383,287.38 (10.3%); £3,773,693.82 -> £3,383,287.40 (10.3%); £3,773,693.98 -> £3,383,287.42 (10.3%); £3,773,694.13 -> £3,383,287.43 (10.3%); £3,773,694.28 -> £3,383,287.45 (10.3%); £3,773,694.43 -> £3,383,287.47 (10.3%); £3,773,694.58 -> £3,383,287.48 (10.3%); £3,773,694.74 -> £3,383,287.50 (10.3%); £3,773,694.89 -> £3,383,287.52 (10.3%); £3,773,695.04 -> £3,383,287.53 (10.3%); £3,773,695.20 -> £3,383,287.55 (10.3%); £3,773,695.35 -> £3,383,287.70 (10.3%); £3,773,695.50 -> £3,383,287.85 (10.3%); £3,773,695.67 -> £3,383,288.01 (10.3%); £3,773,695.85 -> £3,383,288.17 (10.3%); £3,773,696.05 -> £3,383,288.33 (10.3%); £3,773,696.26 -> £3,383,288.49 (10.3%); £3,773,696.51 -> £3,383,288.64 (10.3%); £3,773,696.77 -> £3,383,288.79 (10.3%); £3,773,697.03 -> £3,383,288.82 (10.3%); £3,773,697.29 -> £3,383,288.84 (10.3%); £3,773,697.55 -> £3,383,288.86 (10.3%); £3,773,697.79 -> £3,383,288.89 (10.3%); £3,773,698.05 -> £3,383,288.91 (10.3%); £3,773,698.29 -> £3,383,288.94 (10.3%); £3,773,698.55 -> £3,383,288.96 (10.3%); £3,773,698.80 -> £3,383,288.98 (10.3%); £3,773,699.06 -> £3,383,289.01 (10.3%); £3,773,699.32 -> £3,383,289.03 (10.3%); £3,773,699.57 -> £3,383,289.05 (10.3%); £3,773,699.83 -> £3,383,289.08 (10.3%); £3,773,700.09 -> £3,383,289.11 (10.3%); £3,773,700.34 -> £3,383,289.27 (10.3%); £3,773,700.60 -> £3,383,289.43 (10.3%); £3,773,700.86 -> £3,383,289.61 (10.3%); £3,773,701.11 -> £3,383,289.78 (10.3%); £3,773,701.37 -> £3,383,289.95 (10.3%); £3,773,701.63 -> £3,383,290.12 (10.3%); £3,773,701.88 -> £3,383,290.29 (10.3%); £3,773,702.13 -> £3,383,290.45 (10.3%); £3,773,702.39 -> £3,383,290.62 (10.3%); £3,773,702.65 -> £3,383,290.78 (10.3%); £3,773,702.90 -> £3,383,290.95 (10.3%); £3,773,703.16 -> £3,383,290.97 (10.3%); £3,773,703.40 -> £3,383,291.00 (10.3%); £3,773,703.65 -> £3,383,291.03 (10.3%); £3,773,703.86 -> £3,383,291.05 (10.3%); £3,773,704.06 -> £3,383,291.07 (10.3%); £3,773,704.21 -> £3,383,291.09 (10.3%); £3,773,704.36 -> £3,383,291.11 (10.3%); £3,773,704.52 -> £3,383,291.12 (10.3%); £3,773,704.66 -> £3,383,291.14 (10.3%); £3,773,704.82 -> £3,383,291.16 (10.3%); £3,773,704.97 -> £3,383,291.17 (10.3%); £3,773,705.13 -> £3,383,291.19 (10.3%); £3,773,705.27 -> £3,383,291.21 (10.3%); £3,773,705.43 -> £3,383,291.22 (10.3%); £3,773,705.58 -> £3,383,291.24 (10.3%); £3,773,705.74 -> £3,383,291.26 (10.3%); £3,773,705.89 -> £3,383,291.41 (10.3%); £3,773,706.05 -> £3,383,291.57 (10.3%); £3,773,706.22 -> £3,383,291.73 (10.3%); £3,773,706.40 -> £3,383,291.89 (10.3%); £3,773,706.60 -> £3,383,292.05 (10.3%); £3,773,706.82 -> £3,383,292.21 (10.3%); £3,773,707.06 -> £3,383,292.37 (10.3%); £3,773,707.32 -> £3,383,292.53 (10.3%); £3,773,707.59 -> £3,383,292.56 (10.3%); £3,773,707.84 -> £3,383,292.58 (10.3%); £3,773,708.10 -> £3,383,292.60 (10.3%); £3,773,708.36 -> £3,383,292.63 (10.3%); £3,773,708.61 -> £3,383,292.65 (10.3%); £3,773,708.86 -> £3,383,292.67 (10.3%); £3,773,709.12 -> £3,383,292.70 (10.3%); £3,773,709.37 -> £3,383,292.72 (10.3%); £3,773,709.63 -> £3,383,292.75 (10.3%); £3,773,709.89 -> £3,383,292.77 (10.3%); £3,773,710.14 -> £3,383,292.79 (10.3%); £3,773,710.39 -> £3,383,292.82 (10.3%); £3,773,710.65 -> £3,383,292.85 (10.3%); £3,773,710.91 -> £3,383,293.01 (10.3%); £3,773,711.16 -> £3,383,293.18 (10.3%); £3,773,711.41 -> £3,383,293.35 (10.3%); £3,773,711.66 -> £3,383,293.51 (10.3%); £3,773,711.93 -> £3,383,293.68 (10.3%); £3,773,712.17 -> £3,383,293.85 (10.3%); £3,773,712.42 -> £3,383,294.01 (10.3%); £3,773,712.68 -> £3,383,294.18 (10.3%); £3,773,712.94 -> £3,383,294.34 (10.3%); £3,773,713.19 -> £3,383,294.50 (10.3%); £3,773,713.44 -> £3,383,294.67 (10.3%); £3,773,713.70 -> £3,383,294.70 (10.3%); £3,773,713.96 -> £3,383,294.72 (10.3%); £3,773,714.19 -> £3,383,294.75 (10.3%); £3,773,714.41 -> £3,383,294.77 (10.3%); £3,773,714.60 -> £3,383,294.79 (10.3%); £3,773,714.73 -> £3,383,294.81 (10.3%); £3,773,714.86 -> £3,383,294.83 (10.3%); £3,773,715.00 -> £3,383,294.85 (10.3%); £3,773,715.13 -> £3,383,294.86 (10.3%); £3,773,715.26 -> £3,383,294.88 (10.3%); £3,773,715.40 -> £3,383,294.90 (10.3%); £3,773,715.54 -> £3,383,294.91 (10.3%); £3,773,715.67 -> £3,383,294.93 (10.3%); £3,773,715.80 -> £3,383,294.95 (10.3%); £3,773,715.94 -> £3,383,294.96 (10.3%); £3,773,716.07 -> £3,383,294.98 (10.3%); £3,773,716.20 -> £3,383,295.12 (10.3%); £3,773,716.34 -> £3,383,295.26 (10.3%); £3,773,716.49 -> £3,383,295.41 (10.3%); £3,773,716.65 -> £3,383,295.56 (10.3%); £3,773,716.84 -> £3,383,295.71 (10.3%); £3,773,717.03 -> £3,383,295.87 (10.3%); £3,773,717.24 -> £3,383,296.02 (10.3%); £3,773,717.47 -> £3,383,296.17 (10.3%); £3,773,717.69 -> £3,383,296.19 (10.3%); £3,773,717.91 -> £3,383,296.22 (10.3%); £3,773,718.14 -> £3,383,296.24 (10.3%); £3,773,718.36 -> £3,383,296.27 (10.3%); £3,773,718.58 -> £3,383,296.30 (10.3%); £3,773,718.81 -> £3,383,296.32 (10.3%); £3,773,719.03 -> £3,383,296.35 (10.3%); £3,773,719.25 -> £3,383,296.38 (10.3%); £3,773,719.48 -> £3,383,296.40 (10.3%); £3,773,719.71 -> £3,383,296.43 (10.3%); £3,773,719.94 -> £3,383,296.45 (10.3%); £3,773,720.17 -> £3,383,296.48 (10.3%); £3,773,720.39 -> £3,383,296.51 (10.3%); £3,773,720.62 -> £3,383,296.66 (10.3%); £3,773,720.85 -> £3,383,296.83 (10.3%); £3,773,721.07 -> £3,383,296.98 (10.3%); £3,773,721.30 -> £3,383,297.14 (10.3%); £3,773,721.52 -> £3,383,297.30 (10.3%); £3,773,721.75 -> £3,383,297.47 (10.3%); £3,773,721.97 -> £3,383,297.63 (10.3%); £3,773,722.19 -> £3,383,297.79 (10.3%); £3,773,722.40 -> £3,383,297.95 (10.3%); £3,773,722.63 -> £3,383,298.11 (10.3%); £3,773,722.85 -> £3,383,298.26 (10.3%); £3,773,723.07 -> £3,383,298.29 (10.3%); £3,773,723.29 -> £3,383,298.32 (10.3%); £3,773,723.51 -> £3,383,298.34 (10.3%); £3,773,723.69 -> £3,383,298.37 (10.3%); £3,773,723.87 -> £3,383,298.39 (10.3%); £3,773,724.00 -> £3,383,298.41 (10.3%); £3,773,724.14 -> £3,383,298.43 (10.3%); £3,773,724.27 -> £3,383,298.44 (10.3%); £3,773,724.41 -> £3,383,298.46 (10.3%); £3,773,724.54 -> £3,383,298.48 (10.3%); £3,773,724.68 -> £3,383,298.50 (10.3%); £3,773,724.81 -> £3,383,298.52 (10.3%); £3,773,724.95 -> £3,383,298.53 (10.3%); £3,773,725.09 -> £3,383,298.55 (10.3%); £3,773,725.22 -> £3,383,298.57 (10.3%); £3,773,725.36 -> £3,383,298.58 (10.3%); £3,773,725.49 -> £3,383,298.72 (10.3%); £3,773,725.63 -> £3,383,298.85 (10.3%); £3,773,725.78 -> £3,383,298.99 (10.3%); £3,773,725.94 -> £3,383,299.13 (10.3%); £3,773,726.12 -> £3,383,299.27 (10.3%); £3,773,726.32 -> £3,383,299.41 (10.3%); £3,773,726.52 -> £3,383,299.56 (10.3%); £3,773,726.75 -> £3,383,299.71 (10.3%); £3,773,726.98 -> £3,383,299.74 (10.3%); £3,773,727.20 -> £3,383,299.76 (10.3%); £3,773,727.43 -> £3,383,299.80 (10.3%); £3,773,727.65 -> £3,383,299.83 (10.3%); £3,773,727.88 -> £3,383,299.86 (10.3%); £3,773,728.10 -> £3,383,299.89 (10.3%); £3,773,728.32 -> £3,383,299.92 (10.3%); £3,773,728.54 -> £3,383,299.95 (10.3%); £3,773,728.77 -> £3,383,299.98 (10.3%); £3,773,729.00 -> £3,383,300.01 (10.3%); £3,773,729.22 -> £3,383,300.03 (10.3%); £3,773,729.44 -> £3,383,300.06 (10.3%); £3,773,729.66 -> £3,383,300.10 (10.3%); £3,773,729.89 -> £3,383,300.25 (10.3%); £3,773,730.12 -> £3,383,300.41 (10.3%); £3,773,730.35 -> £3,383,300.56 (10.3%); £3,773,730.57 -> £3,383,300.72 (10.3%); £3,773,730.79 -> £3,383,300.87 (10.3%); £3,773,731.00 -> £3,383,301.02 (10.3%); £3,773,731.22 -> £3,383,301.18 (10.3%); £3,773,731.44 -> £3,383,301.33 (10.3%); £3,773,731.66 -> £3,383,301.47 (10.3%); £3,773,731.89 -> £3,383,301.62 (10.3%); £3,773,732.12 -> £3,383,301.77 (10.3%); £3,773,732.34 -> £3,383,301.80 (10.3%); £3,773,732.56 -> £3,383,301.83 (10.3%); £3,773,732.77 -> £3,383,301.86 (10.3%); £3,773,732.96 -> £3,383,301.88 (10.3%); £3,773,733.14 -> £3,383,301.90 (10.3%); £3,773,733.29 -> £3,383,301.92 (10.3%); £3,773,733.44 -> £3,383,301.93 (10.3%); £3,773,733.60 -> £3,383,301.95 (10.3%); £3,773,733.75 -> £3,383,301.97 (10.3%); £3,773,733.90 -> £3,383,301.99 (10.3%); £3,773,734.06 -> £3,383,302.00 (10.3%); £3,773,734.20 -> £3,383,302.02 (10.3%); £3,773,734.36 -> £3,383,302.04 (10.3%); £3,773,734.51 -> £3,383,302.05 (10.3%); £3,773,734.66 -> £3,383,302.07 (10.3%); £3,773,734.81 -> £3,383,302.09 (10.3%); £3,773,734.96 -> £3,383,302.23 (10.3%); £3,773,735.10 -> £3,383,302.38 (10.3%); £3,773,735.28 -> £3,383,302.52 (10.3%); £3,773,735.47 -> £3,383,302.67 (10.3%); £3,773,735.68 -> £3,383,302.82 (10.3%); £3,773,735.89 -> £3,383,302.96 (10.3%); £3,773,736.13 -> £3,383,303.11 (10.3%); £3,773,736.38 -> £3,383,303.25 (10.3%); £3,773,736.63 -> £3,383,303.27 (10.3%); £3,773,736.88 -> £3,383,303.30 (10.3%); £3,773,737.14 -> £3,383,303.32 (10.3%); £3,773,737.40 -> £3,383,303.34 (10.3%); £3,773,737.65 -> £3,383,303.37 (10.3%); £3,773,737.91 -> £3,383,303.39 (10.3%); £3,773,738.16 -> £3,383,303.41 (10.3%); £3,773,738.40 -> £3,383,303.44 (10.3%); £3,773,738.65 -> £3,383,303.46 (10.3%); £3,773,738.91 -> £3,383,303.48 (10.3%); £3,773,739.17 -> £3,383,303.51 (10.3%); £3,773,739.42 -> £3,383,303.53 (10.3%); £3,773,739.67 -> £3,383,303.56 (10.3%); £3,773,739.93 -> £3,383,303.70 (10.3%); £3,773,740.17 -> £3,383,303.85 (10.3%); £3,773,740.43 -> £3,383,304.00 (10.3%); £3,773,740.69 -> £3,383,304.15 (10.3%); £3,773,740.94 -> £3,383,304.30 (10.3%); £3,773,741.20 -> £3,383,304.46 (10.3%); £3,773,741.44 -> £3,383,304.62 (10.3%); £3,773,741.69 -> £3,383,304.78 (10.3%); £3,773,741.95 -> £3,383,304.94 (10.3%); £3,773,742.20 -> £3,383,305.09 (10.3%); £3,773,742.46 -> £3,383,305.24 (10.3%); £3,773,742.71 -> £3,383,305.27 (10.3%); £3,773,742.97 -> £3,383,305.30 (10.3%); £3,773,743.20 -> £3,383,305.32 (10.3%); £3,773,743.41 -> £3,383,305.34 (10.3%); £3,773,743.61 -> £3,383,305.36 (10.3%); £3,773,743.76 -> £3,383,305.38 (10.3%); £3,773,743.90 -> £3,383,305.40 (10.3%); £3,773,744.05 -> £3,383,305.42 (10.3%); £3,773,744.20 -> £3,383,305.44 (10.3%); £3,773,744.35 -> £3,383,305.45 (10.3%); £3,773,744.50 -> £3,383,305.47 (10.3%); £3,773,744.66 -> £3,383,305.49 (10.3%); £3,773,744.81 -> £3,383,305.50 (10.3%); £3,773,744.95 -> £3,383,305.52 (10.3%); £3,773,745.10 -> £3,383,305.54 (10.3%); £3,773,745.25 -> £3,383,305.55 (10.3%); £3,773,745.40 -> £3,383,305.66 (10.3%); £3,773,745.55 -> £3,383,305.77 (10.3%); £3,773,745.72 -> £3,383,305.88 (10.3%); £3,773,745.91 -> £3,383,306.00 (10.3%); £3,773,746.11 -> £3,383,306.12 (10.3%); £3,773,746.33 -> £3,383,306.24 (10.3%); £3,773,746.56 -> £3,383,306.35 (10.3%); £3,773,746.82 -> £3,383,306.46 (10.3%); £3,773,747.07 -> £3,383,306.49 (10.3%); £3,773,747.31 -> £3,383,306.51 (10.3%); £3,773,747.57 -> £3,383,306.54 (10.3%); £3,773,747.83 -> £3,383,306.56 (10.3%); £3,773,748.08 -> £3,383,306.58 (10.3%); £3,773,748.32 -> £3,383,306.61 (10.3%); £3,773,748.57 -> £3,383,306.63 (10.3%); £3,773,748.82 -> £3,383,306.66 (10.3%); £3,773,749.08 -> £3,383,306.68 (10.3%); £3,773,749.33 -> £3,383,306.70 (10.3%); £3,773,749.58 -> £3,383,306.73 (10.3%); £3,773,749.84 -> £3,383,306.75 (10.3%); £3,773,750.09 -> £3,383,306.78 (10.3%); £3,773,750.35 -> £3,383,306.90 (10.3%); £3,773,750.60 -> £3,383,307.03 (10.3%); £3,773,750.85 -> £3,383,307.15 (10.3%); £3,773,751.12 -> £3,383,307.28 (10.3%); £3,773,751.37 -> £3,383,307.41 (10.3%); £3,773,751.63 -> £3,383,307.53 (10.3%); £3,773,751.88 -> £3,383,307.66 (10.3%); £3,773,752.13 -> £3,383,307.79 (10.3%); £3,773,752.37 -> £3,383,307.91 (10.3%); £3,773,752.62 -> £3,383,308.03 (10.3%); £3,773,752.87 -> £3,383,308.15 (10.3%); £3,773,753.12 -> £3,383,308.17 (10.3%); £3,773,753.36 -> £3,383,308.20 (10.3%); £3,773,753.60 -> £3,383,308.23 (10.3%); £3,773,753.82 -> £3,383,308.25 (10.3%); £3,773,754.01 -> £3,383,308.27 (10.3%); £3,773,754.16 -> £3,383,308.29 (10.3%); £3,773,754.32 -> £3,383,308.30 (10.3%); £3,773,754.47 -> £3,383,308.32 (10.3%); £3,773,754.62 -> £3,383,308.34 (10.3%); £3,773,754.77 -> £3,383,308.36 (10.3%); £3,773,754.92 -> £3,383,308.37 (10.3%); £3,773,755.08 -> £3,383,308.39 (10.3%); £3,773,755.22 -> £3,383,308.40 (10.3%); £3,773,755.38 -> £3,383,308.42 (10.3%); £3,773,755.53 -> £3,383,308.44 (10.3%); £3,773,755.68 -> £3,383,308.46 (10.3%); £3,773,755.83 -> £3,383,308.53 (10.3%); £3,773,755.98 -> £3,383,308.61 (10.3%); £3,773,756.15 -> £3,383,308.69 (10.3%); £3,773,756.33 -> £3,383,308.78 (10.3%); £3,773,756.53 -> £3,383,308.87 (10.3%); £3,773,756.75 -> £3,383,308.96 (10.3%); £3,773,756.99 -> £3,383,309.04 (10.3%); £3,773,757.23 -> £3,383,309.12 (10.3%); £3,773,757.48 -> £3,383,309.15 (10.3%); £3,773,757.73 -> £3,383,309.17 (10.3%); £3,773,757.99 -> £3,383,309.20 (10.3%); £3,773,758.24 -> £3,383,309.22 (10.3%); £3,773,758.49 -> £3,383,309.24 (10.3%); £3,773,758.74 -> £3,383,309.27 (10.3%); £3,773,759.00 -> £3,383,309.29 (10.3%); £3,773,759.25 -> £3,383,309.32 (10.3%); £3,773,759.50 -> £3,383,309.34 (10.3%); £3,773,759.74 -> £3,383,309.36 (10.3%); £3,773,759.99 -> £3,383,309.39 (10.3%); £3,773,760.24 -> £3,383,309.41 (10.3%); £3,773,760.49 -> £3,383,309.44 (10.3%); £3,773,760.73 -> £3,383,309.53 (10.3%); £3,773,760.99 -> £3,383,309.63 (10.3%); £3,773,761.24 -> £3,383,309.73 (10.3%); £3,773,761.49 -> £3,383,309.83 (10.3%); £3,773,761.73 -> £3,383,309.93 (10.3%); £3,773,761.98 -> £3,383,310.03 (10.3%); £3,773,762.23 -> £3,383,310.13 (10.3%); £3,773,762.48 -> £3,383,310.23 (10.3%); £3,773,762.73 -> £3,383,310.32 (10.3%); £3,773,762.97 -> £3,383,310.42 (10.3%); £3,773,763.22 -> £3,383,310.51 (10.3%); £3,773,763.47 -> £3,383,310.54 (10.3%); £3,773,763.72 -> £3,383,310.57 (10.3%); £3,773,763.96 -> £3,383,310.59 (10.3%); £3,773,764.17 -> £3,383,310.61 (10.3%); £3,773,764.36 -> £3,383,310.63 (10.3%); £3,773,764.51 -> £3,383,310.65 (10.3%); £3,773,764.66 -> £3,383,310.67 (10.3%); £3,773,764.82 -> £3,383,310.69 (10.3%); £3,773,764.98 -> £3,383,310.70 (10.3%); £3,773,765.12 -> £3,383,310.72 (10.3%); £3,773,765.27 -> £3,383,310.74 (10.3%); £3,773,765.43 -> £3,383,310.75 (10.3%); £3,773,765.58 -> £3,383,310.77 (10.3%); £3,773,765.73 -> £3,383,310.79 (10.3%); £3,773,765.88 -> £3,383,310.80 (10.3%); £3,773,766.03 -> £3,383,310.82 (10.3%); £3,773,766.18 -> £3,383,310.89 (10.3%); £3,773,766.33 -> £3,383,310.97 (10.3%); £3,773,766.49 -> £3,383,311.05 (10.3%); £3,773,766.67 -> £3,383,311.14 (10.3%); £3,773,766.87 -> £3,383,311.22 (10.3%); £3,773,767.09 -> £3,383,311.31 (10.3%); £3,773,767.32 -> £3,383,311.39 (10.3%); £3,773,767.58 -> £3,383,311.47 (10.3%); £3,773,767.83 -> £3,383,311.49 (10.3%); £3,773,768.08 -> £3,383,311.52 (10.3%); £3,773,768.34 -> £3,383,311.54 (10.3%); £3,773,768.58 -> £3,383,311.56 (10.3%); £3,773,768.84 -> £3,383,311.59 (10.3%); £3,773,769.09 -> £3,383,311.61 (10.3%); £3,773,769.34 -> £3,383,311.64 (10.3%); £3,773,769.59 -> £3,383,311.66 (10.3%); £3,773,769.84 -> £3,383,311.68 (10.3%); £3,773,770.09 -> £3,383,311.70 (10.3%); £3,773,770.35 -> £3,383,311.73 (10.3%); £3,773,770.61 -> £3,383,311.75 (10.3%); £3,773,770.86 -> £3,383,311.78 (10.3%); £3,773,771.11 -> £3,383,311.87 (10.3%); £3,773,771.37 -> £3,383,311.97 (10.3%); £3,773,771.63 -> £3,383,312.06 (10.3%); £3,773,771.88 -> £3,383,312.16 (10.3%); £3,773,772.14 -> £3,383,312.26 (10.3%); £3,773,772.39 -> £3,383,312.36 (10.3%); £3,773,772.64 -> £3,383,312.45 (10.3%); £3,773,772.89 -> £3,383,312.55 (10.3%); £3,773,773.14 -> £3,383,312.64 (10.3%); £3,773,773.39 -> £3,383,312.73 (10.3%); £3,773,773.64 -> £3,383,312.82 (10.3%); £3,773,773.89 -> £3,383,312.85 (10.3%); £3,773,774.15 -> £3,383,312.88 (10.3%); £3,773,774.38 -> £3,383,312.90 (10.3%); £3,773,774.59 -> £3,383,312.93 (10.3%); £3,773,774.79 -> £3,383,312.95 (10.3%); £3,773,774.94 -> £3,383,312.97 (10.3%); £3,773,775.09 -> £3,383,312.98 (10.3%); £3,773,775.24 -> £3,383,313.00 (10.3%); £3,773,775.39 -> £3,383,313.02 (10.3%); £3,773,775.55 -> £3,383,313.03 (10.3%); £3,773,775.70 -> £3,383,313.05 (10.3%); £3,773,775.85 -> £3,383,313.07 (10.3%); £3,773,776.01 -> £3,383,313.08 (10.3%); £3,773,776.16 -> £3,383,313.10 (10.3%); £3,773,776.31 -> £3,383,313.12 (10.3%); £3,773,776.45 -> £3,383,313.14 (10.3%); £3,773,776.61 -> £3,383,313.24 (10.3%); £3,773,776.75 -> £3,383,313.35 (10.3%); £3,773,776.92 -> £3,383,313.47 (10.3%); £3,773,777.11 -> £3,383,313.59 (10.3%); £3,773,777.31 -> £3,383,313.71 (10.3%); £3,773,777.53 -> £3,383,313.82 (10.3%); £3,773,777.77 -> £3,383,313.93 (10.3%); £3,773,778.02 -> £3,383,314.04 (10.3%); £3,773,778.28 -> £3,383,314.06 (10.3%); £3,773,778.52 -> £3,383,314.09 (10.3%); £3,773,778.77 -> £3,383,314.11 (10.3%); £3,773,779.03 -> £3,383,314.14 (10.3%); £3,773,779.27 -> £3,383,314.16 (10.3%); £3,773,779.52 -> £3,383,314.19 (10.3%); £3,773,779.78 -> £3,383,314.21 (10.3%); £3,773,780.02 -> £3,383,314.23 (10.3%); £3,773,780.28 -> £3,383,314.26 (10.3%); £3,773,780.53 -> £3,383,314.28 (10.3%); £3,773,780.79 -> £3,383,314.31 (10.3%); £3,773,781.04 -> £3,383,314.33 (10.3%); £3,773,781.29 -> £3,383,314.36 (10.3%); £3,773,781.54 -> £3,383,314.48 (10.3%); £3,773,781.79 -> £3,383,314.60 (10.3%); £3,773,782.04 -> £3,383,314.72 (10.3%); £3,773,782.30 -> £3,383,314.85 (10.3%); £3,773,782.54 -> £3,383,314.97 (10.3%); £3,773,782.80 -> £3,383,315.09 (10.3%); £3,773,783.04 -> £3,383,315.21 (10.3%); £3,773,783.30 -> £3,383,315.33 (10.3%); £3,773,783.55 -> £3,383,315.44 (10.3%); £3,773,783.81 -> £3,383,315.56 (10.3%); £3,773,784.06 -> £3,383,315.67 (10.3%); £3,773,784.32 -> £3,383,315.70 (10.3%); £3,773,784.56 -> £3,383,315.73 (10.3%); £3,773,784.80 -> £3,383,315.76 (10.3%); £3,773,785.01 -> £3,383,315.78 (10.3%); £3,773,785.20 -> £3,383,315.80 (10.3%); £3,773,785.33 -> £3,383,315.82 (10.3%); £3,773,785.47 -> £3,383,315.84 (10.3%); £3,773,785.60 -> £3,383,315.86 (10.3%); £3,773,785.73 -> £3,383,315.87 (10.3%); £3,773,785.87 -> £3,383,315.89 (10.3%); £3,773,786.01 -> £3,383,315.91 (10.3%); £3,773,786.14 -> £3,383,315.92 (10.3%); £3,773,786.28 -> £3,383,315.94 (10.3%); £3,773,786.41 -> £3,383,315.96 (10.3%); £3,773,786.55 -> £3,383,315.97 (10.3%); £3,773,786.69 -> £3,383,315.99 (10.3%); £3,773,786.82 -> £3,383,316.13 (10.3%); £3,773,786.96 -> £3,383,316.27 (10.3%); £3,773,787.11 -> £3,383,316.42 (10.3%); £3,773,787.28 -> £3,383,316.57 (10.3%); £3,773,787.45 -> £3,383,316.72 (10.3%); £3,773,787.65 -> £3,383,316.87 (10.3%); £3,773,787.87 -> £3,383,317.02 (10.3%); £3,773,788.09 -> £3,383,317.17 (10.3%); £3,773,788.31 -> £3,383,317.20 (10.3%); £3,773,788.53 -> £3,383,317.23 (10.3%); £3,773,788.75 -> £3,383,317.25 (10.3%); £3,773,788.98 -> £3,383,317.28 (10.3%); £3,773,789.21 -> £3,383,317.31 (10.3%); £3,773,789.43 -> £3,383,317.33 (10.3%); £3,773,789.65 -> £3,383,317.36 (10.3%); £3,773,789.88 -> £3,383,317.39 (10.3%); £3,773,790.09 -> £3,383,317.41 (10.3%); £3,773,790.31 -> £3,383,317.44 (10.3%); £3,773,790.53 -> £3,383,317.46 (10.3%); £3,773,790.75 -> £3,383,317.49 (10.3%); £3,773,790.97 -> £3,383,317.52 (10.3%); £3,773,791.19 -> £3,383,317.66 (10.3%); £3,773,791.42 -> £3,383,317.82 (10.3%); £3,773,791.64 -> £3,383,317.97 (10.3%); £3,773,791.87 -> £3,383,318.13 (10.3%); £3,773,792.10 -> £3,383,318.29 (10.3%); £3,773,792.33 -> £3,383,318.44 (10.3%); £3,773,792.55 -> £3,383,318.60 (10.3%); £3,773,792.77 -> £3,383,318.75 (10.3%); £3,773,793.00 -> £3,383,318.90 (10.3%); £3,773,793.22 -> £3,383,319.06 (10.3%); £3,773,793.44 -> £3,383,319.22 (10.3%); £3,773,793.66 -> £3,383,319.25 (10.3%); £3,773,793.88 -> £3,383,319.27 (10.3%); £3,773,794.08 -> £3,383,319.30 (10.3%); £3,773,794.27 -> £3,383,319.32 (10.3%); £3,773,794.45 -> £3,383,319.35 (10.3%); £3,773,794.59 -> £3,383,319.37 (10.3%); £3,773,794.72 -> £3,383,319.38 (10.3%); £3,773,794.85 -> £3,383,319.40 (10.3%); £3,773,794.99 -> £3,383,319.42 (10.3%); £3,773,795.13 -> £3,383,319.44 (10.3%); £3,773,795.26 -> £3,383,319.46 (10.3%); £3,773,795.39 -> £3,383,319.47 (10.3%); £3,773,795.53 -> £3,383,319.49 (10.3%); £3,773,795.66 -> £3,383,319.51 (10.3%); £3,773,795.81 -> £3,383,319.52 (10.3%); £3,773,795.94 -> £3,383,319.54 (10.3%); £3,773,796.08 -> £3,383,319.61 (10.3%); £3,773,796.21 -> £3,383,319.69 (10.3%); £3,773,796.36 -> £3,383,319.77 (10.3%); £3,773,796.53 -> £3,383,319.84 (10.3%); £3,773,796.71 -> £3,383,319.93 (10.3%); £3,773,796.91 -> £3,383,320.01 (10.3%); £3,773,797.12 -> £3,383,320.09 (10.3%); £3,773,797.35 -> £3,383,320.18 (10.3%); £3,773,797.58 -> £3,383,320.21 (10.3%); £3,773,797.80 -> £3,383,320.24 (10.3%); £3,773,798.02 -> £3,383,320.27 (10.3%); £3,773,798.25 -> £3,383,320.30 (10.3%); £3,773,798.47 -> £3,383,320.33 (10.3%); £3,773,798.70 -> £3,383,320.36 (10.3%); £3,773,798.93 -> £3,383,320.39 (10.3%); £3,773,799.16 -> £3,383,320.42 (10.3%); £3,773,799.39 -> £3,383,320.45 (10.3%); £3,773,799.62 -> £3,383,320.48 (10.3%); £3,773,799.84 -> £3,383,320.51 (10.3%); £3,773,800.07 -> £3,383,320.54 (10.3%); £3,773,800.30 -> £3,383,320.57 (10.3%); £3,773,800.52 -> £3,383,320.66 (10.3%); £3,773,800.75 -> £3,383,320.76 (10.3%); £3,773,800.97 -> £3,383,320.86 (10.3%); £3,773,801.20 -> £3,383,320.96 (10.3%); £3,773,801.43 -> £3,383,321.06 (10.3%); £3,773,801.65 -> £3,383,321.16 (10.3%); £3,773,801.88 -> £3,383,321.26 (10.3%); £3,773,802.10 -> £3,383,321.35 (10.3%); £3,773,802.32 -> £3,383,321.45 (10.3%); £3,773,802.54 -> £3,383,321.54 (10.3%); £3,773,802.78 -> £3,383,321.64 (10.3%); £3,773,803.00 -> £3,383,321.67 (10.3%); £3,773,803.23 -> £3,383,321.70 (10.3%); £3,773,803.44 -> £3,383,321.72 (10.3%); £3,773,803.64 -> £3,383,321.74 (10.3%); £3,773,803.82 -> £3,383,321.76 (10.3%); £3,773,803.97 -> £3,383,321.78 (10.3%); £3,773,804.13 -> £3,383,321.80 (10.3%); £3,773,804.28 -> £3,383,321.82 (10.3%); £3,773,804.43 -> £3,383,321.83 (10.3%); £3,773,804.59 -> £3,383,321.85 (10.3%); £3,773,804.74 -> £3,383,321.87 (10.3%); £3,773,804.89 -> £3,383,321.88 (10.3%); £3,773,805.05 -> £3,383,321.90 (10.3%); £3,773,805.20 -> £3,383,321.92 (10.3%); £3,773,805.35 -> £3,383,321.93 (10.3%); £3,773,805.50 -> £3,383,321.95 (10.3%); £3,773,805.66 -> £3,383,322.05 (10.3%); £3,773,805.81 -> £3,383,322.15 (10.3%); £3,773,805.98 -> £3,383,322.25 (10.3%); £3,773,806.17 -> £3,383,322.35 (10.3%); £3,773,806.38 -> £3,383,322.46 (10.3%); £3,773,806.60 -> £3,383,322.57 (10.3%); £3,773,806.84 -> £3,383,322.68 (10.3%); £3,773,807.11 -> £3,383,322.79 (10.3%); £3,773,807.36 -> £3,383,322.81 (10.3%); £3,773,807.61 -> £3,383,322.83 (10.3%); £3,773,807.87 -> £3,383,322.86 (10.3%); £3,773,808.12 -> £3,383,322.88 (10.3%); £3,773,808.36 -> £3,383,322.91 (10.3%); £3,773,808.62 -> £3,383,322.93 (10.3%); £3,773,808.87 -> £3,383,322.95 (10.3%); £3,773,809.12 -> £3,383,322.98 (10.3%); £3,773,809.39 -> £3,383,323.00 (10.3%); £3,773,809.65 -> £3,383,323.02 (10.3%); £3,773,809.91 -> £3,383,323.05 (10.3%); £3,773,810.16 -> £3,383,323.07 (10.3%); £3,773,810.43 -> £3,383,323.10 (10.3%); £3,773,810.68 -> £3,383,323.22 (10.3%); £3,773,810.94 -> £3,383,323.34 (10.3%); £3,773,811.20 -> £3,383,323.46 (10.3%); £3,773,811.45 -> £3,383,323.58 (10.3%); £3,773,811.71 -> £3,383,323.70 (10.3%); £3,773,811.97 -> £3,383,323.82 (10.3%); £3,773,812.22 -> £3,383,323.94 (10.3%); £3,773,812.48 -> £3,383,324.05 (10.3%); £3,773,812.73 -> £3,383,324.17 (10.3%); £3,773,812.99 -> £3,383,324.29 (10.3%); £3,773,813.25 -> £3,383,324.41 (10.3%); £3,773,813.51 -> £3,383,324.44 (10.3%); £3,773,813.76 -> £3,383,324.46 (10.3%); £3,773,814.00 -> £3,383,324.49 (10.3%); £3,773,814.21 -> £3,383,324.51 (10.3%); £3,773,814.41 -> £3,383,324.53 (10.3%); £3,773,814.57 -> £3,383,324.55 (10.3%); £3,773,814.72 -> £3,383,324.57 (10.3%); £3,773,814.88 -> £3,383,324.58 (10.3%); £3,773,815.03 -> £3,383,324.60 (10.3%); £3,773,815.19 -> £3,383,324.62 (10.3%); £3,773,815.34 -> £3,383,324.63 (10.3%); £3,773,815.50 -> £3,383,324.65 (10.3%); £3,773,815.65 -> £3,383,324.67 (10.3%); £3,773,815.80 -> £3,383,324.68 (10.3%); £3,773,815.96 -> £3,383,324.70 (10.3%); £3,773,816.11 -> £3,383,324.72 (10.3%); £3,773,816.27 -> £3,383,324.80 (10.3%); £3,773,816.43 -> £3,383,324.88 (10.3%); £3,773,816.60 -> £3,383,324.97 (10.3%); £3,773,816.79 -> £3,383,325.06 (10.3%); £3,773,817.00 -> £3,383,325.15 (10.3%); £3,773,817.22 -> £3,383,325.25 (10.3%); £3,773,817.46 -> £3,383,325.34 (10.3%); £3,773,817.72 -> £3,383,325.43 (10.3%); £3,773,817.98 -> £3,383,325.46 (10.3%); £3,773,818.23 -> £3,383,325.48 (10.3%); £3,773,818.48 -> £3,383,325.51 (10.3%); £3,773,818.74 -> £3,383,325.53 (10.3%); £3,773,819.00 -> £3,383,325.55 (10.3%); £3,773,819.26 -> £3,383,325.58 (10.3%); £3,773,819.52 -> £3,383,325.60 (10.3%); £3,773,819.78 -> £3,383,325.62 (10.3%); £3,773,820.06 -> £3,383,325.65 (10.3%); £3,773,820.31 -> £3,383,325.67 (10.3%); £3,773,820.57 -> £3,383,325.69 (10.3%); £3,773,820.83 -> £3,383,325.72 (10.3%); £3,773,821.08 -> £3,383,325.75 (10.3%); £3,773,821.33 -> £3,383,325.84 (10.3%); £3,773,821.59 -> £3,383,325.94 (10.3%); £3,773,821.85 -> £3,383,326.04 (10.3%); £3,773,822.11 -> £3,383,326.14 (10.3%); £3,773,822.37 -> £3,383,326.24 (10.3%); £3,773,822.63 -> £3,383,326.35 (10.3%); £3,773,822.89 -> £3,383,326.45 (10.3%); £3,773,823.15 -> £3,383,326.55 (10.3%); £3,773,823.40 -> £3,383,326.65 (10.3%); £3,773,823.66 -> £3,383,326.74 (10.3%); £3,773,823.91 -> £3,383,326.84 (10.3%); £3,773,824.17 -> £3,383,326.87 (10.3%); £3,773,824.42 -> £3,383,326.90 (10.3%); £3,773,824.67 -> £3,383,326.92 (10.3%); £3,773,824.89 -> £3,383,326.94 (10.3%); £3,773,825.08 -> £3,383,326.96 (10.3%); £3,773,825.23 -> £3,383,326.98 (10.3%); £3,773,825.39 -> £3,383,327.00 (10.3%); £3,773,825.54 -> £3,383,327.01 (10.3%); £3,773,825.69 -> £3,383,327.03 (10.3%); £3,773,825.84 -> £3,383,327.05 (10.3%); £3,773,826.00 -> £3,383,327.06 (10.3%); £3,773,826.16 -> £3,383,327.08 (10.3%); £3,773,826.31 -> £3,383,327.10 (10.3%); £3,773,826.46 -> £3,383,327.11 (10.3%); £3,773,826.62 -> £3,383,327.13 (10.3%); £3,773,826.79 -> £3,383,327.15 (10.3%); £3,773,826.94 -> £3,383,327.25 (10.3%); £3,773,827.10 -> £3,383,327.35 (10.3%); £3,773,827.27 -> £3,383,327.46 (10.3%); £3,773,827.45 -> £3,383,327.57 (10.3%); £3,773,827.66 -> £3,383,327.68 (10.3%); £3,773,827.89 -> £3,383,327.79 (10.3%); £3,773,828.13 -> £3,383,327.89 (10.3%); £3,773,828.39 -> £3,383,328.00 (10.3%); £3,773,828.65 -> £3,383,328.02 (10.3%); £3,773,828.91 -> £3,383,328.04 (10.3%); £3,773,829.16 -> £3,383,328.07 (10.3%); £3,773,829.41 -> £3,383,328.09 (10.3%); £3,773,829.67 -> £3,383,328.12 (10.3%); £3,773,829.93 -> £3,383,328.14 (10.3%); £3,773,830.19 -> £3,383,328.16 (10.3%); £3,773,830.44 -> £3,383,328.19 (10.3%); £3,773,830.69 -> £3,383,328.21 (10.3%); £3,773,830.94 -> £3,383,328.23 (10.3%); £3,773,831.21 -> £3,383,328.26 (10.3%); £3,773,831.46 -> £3,383,328.28 (10.3%); £3,773,831.72 -> £3,383,328.31 (10.3%); £3,773,831.97 -> £3,383,328.43 (10.3%); £3,773,832.23 -> £3,383,328.55 (10.3%); £3,773,832.50 -> £3,383,328.67 (10.3%); £3,773,832.75 -> £3,383,328.78 (10.3%); £3,773,833.01 -> £3,383,328.89 (10.3%); £3,773,833.27 -> £3,383,329.01 (10.3%); £3,773,833.53 -> £3,383,329.12 (10.3%); £3,773,833.78 -> £3,383,329.24 (10.3%); £3,773,834.04 -> £3,383,329.36 (10.3%); £3,773,834.30 -> £3,383,329.48 (10.3%); £3,773,834.55 -> £3,383,329.59 (10.3%); £3,773,834.80 -> £3,383,329.62 (10.3%); £3,773,835.06 -> £3,383,329.65 (10.3%); £3,773,835.30 -> £3,383,329.67 (10.3%); £3,773,835.52 -> £3,383,329.70 (10.3%); £3,773,835.73 -> £3,383,329.72 (10.3%); £3,773,835.89 -> £3,383,329.74 (10.3%); £3,773,836.04 -> £3,383,329.75 (10.3%); £3,773,836.19 -> £3,383,329.77 (10.3%); £3,773,836.34 -> £3,383,329.79 (10.3%); £3,773,836.49 -> £3,383,329.80 (10.3%); £3,773,836.64 -> £3,383,329.82 (10.3%); £3,773,836.79 -> £3,383,329.84 (10.3%); £3,773,836.95 -> £3,383,329.85 (10.3%); £3,773,837.10 -> £3,383,329.87 (10.3%); £3,773,837.25 -> £3,383,329.89 (10.3%); £3,773,837.40 -> £3,383,329.90 (10.3%); £3,773,837.55 -> £3,383,330.02 (10.3%); £3,773,837.71 -> £3,383,330.14 (10.3%); £3,773,837.88 -> £3,383,330.26 (10.3%); £3,773,838.06 -> £3,383,330.38 (10.3%); £3,773,838.27 -> £3,383,330.50 (10.3%); £3,773,838.49 -> £3,383,330.63 (10.3%); £3,773,838.73 -> £3,383,330.75 (10.3%); £3,773,838.99 -> £3,383,330.87 (10.3%); £3,773,839.25 -> £3,383,330.89 (10.3%); £3,773,839.50 -> £3,383,330.91 (10.3%); £3,773,839.76 -> £3,383,330.94 (10.3%); £3,773,840.01 -> £3,383,330.96 (10.3%); £3,773,840.28 -> £3,383,330.99 (10.3%); £3,773,840.53 -> £3,383,331.01 (10.3%); £3,773,840.78 -> £3,383,331.04 (10.3%); £3,773,841.04 -> £3,383,331.06 (10.3%); £3,773,841.29 -> £3,383,331.08 (10.3%); £3,773,841.55 -> £3,383,331.10 (10.3%); £3,773,841.80 -> £3,383,331.13 (10.3%); £3,773,842.05 -> £3,383,331.15 (10.3%); £3,773,842.31 -> £3,383,331.18 (10.3%); £3,773,842.57 -> £3,383,331.31 (10.3%); £3,773,842.81 -> £3,383,331.45 (10.3%); £3,773,843.07 -> £3,383,331.58 (10.3%); £3,773,843.33 -> £3,383,331.72 (10.3%); £3,773,843.59 -> £3,383,331.85 (10.3%); £3,773,843.85 -> £3,383,331.99 (10.3%); £3,773,844.10 -> £3,383,332.12 (10.3%); £3,773,844.36 -> £3,383,332.26 (10.3%); £3,773,844.61 -> £3,383,332.39 (10.3%); £3,773,844.86 -> £3,383,332.52 (10.3%); £3,773,845.12 -> £3,383,332.65 (10.3%); £3,773,845.38 -> £3,383,332.68 (10.3%); £3,773,845.63 -> £3,383,332.71 (10.3%); £3,773,845.86 -> £3,383,332.73 (10.3%); £3,773,846.09 -> £3,383,332.75 (10.3%); £3,773,846.28 -> £3,383,332.77 (10.3%); £3,773,846.44 -> £3,383,332.79 (10.3%); £3,773,846.60 -> £3,383,332.81 (10.3%); £3,773,846.74 -> £3,383,332.83 (10.3%); £3,773,846.90 -> £3,383,332.85 (10.3%); £3,773,847.05 -> £3,383,332.86 (10.3%); £3,773,847.20 -> £3,383,332.88 (10.3%); £3,773,847.36 -> £3,383,332.90 (10.3%); £3,773,847.51 -> £3,383,332.91 (10.3%); £3,773,847.66 -> £3,383,332.93 (10.3%); £3,773,847.81 -> £3,383,332.95 (10.3%); £3,773,847.96 -> £3,383,332.96 (10.3%); £3,773,848.12 -> £3,383,333.08 (10.3%); £3,773,848.27 -> £3,383,333.20 (10.3%); £3,773,848.44 -> £3,383,333.33 (10.3%); £3,773,848.63 -> £3,383,333.46 (10.3%); £3,773,848.84 -> £3,383,333.59 (10.3%); £3,773,849.06 -> £3,383,333.72 (10.3%); £3,773,849.30 -> £3,383,333.85 (10.3%); £3,773,849.57 -> £3,383,333.97 (10.3%); £3,773,849.83 -> £3,383,334.00 (10.3%); £3,773,850.09 -> £3,383,334.02 (10.3%); £3,773,850.35 -> £3,383,334.05 (10.3%); £3,773,850.61 -> £3,383,334.07 (10.3%); £3,773,850.86 -> £3,383,334.10 (10.3%); £3,773,851.12 -> £3,383,334.12 (10.3%); £3,773,851.38 -> £3,383,334.14 (10.3%); £3,773,851.63 -> £3,383,334.17 (10.3%); £3,773,851.89 -> £3,383,334.19 (10.3%); £3,773,852.15 -> £3,383,334.22 (10.3%); £3,773,852.40 -> £3,383,334.24 (10.3%); £3,773,852.66 -> £3,383,334.27 (10.3%); £3,773,852.92 -> £3,383,334.30 (10.3%); £3,773,853.18 -> £3,383,334.43 (10.3%); £3,773,853.44 -> £3,383,334.57 (10.3%); £3,773,853.69 -> £3,383,334.71 (10.3%); £3,773,853.96 -> £3,383,334.84 (10.3%); £3,773,854.20 -> £3,383,334.98 (10.3%); £3,773,854.46 -> £3,383,335.11 (10.3%); £3,773,854.72 -> £3,383,335.25 (10.3%); £3,773,854.99 -> £3,383,335.38 (10.3%); £3,773,855.24 -> £3,383,335.52 (10.3%); £3,773,855.50 -> £3,383,335.65 (10.3%); £3,773,855.76 -> £3,383,335.79 (10.3%); £3,773,856.01 -> £3,383,335.82 (10.3%); £3,773,856.27 -> £3,383,335.84 (10.3%); £3,773,856.51 -> £3,383,335.87 (10.3%); £3,773,856.73 -> £3,383,335.89 (10.3%); £3,773,856.93 -> £3,383,335.91 (10.3%); £3,773,857.07 -> £3,383,335.93 (10.3%); £3,773,857.21 -> £3,383,335.95 (10.3%); £3,773,857.35 -> £3,383,335.97 (10.3%); £3,773,857.48 -> £3,383,335.99 (10.3%); £3,773,857.62 -> £3,383,336.00 (10.3%); £3,773,857.75 -> £3,383,336.02 (10.3%); £3,773,857.89 -> £3,383,336.04 (10.3%); £3,773,858.03 -> £3,383,336.06 (10.3%); £3,773,858.16 -> £3,383,336.07 (10.3%); £3,773,858.30 -> £3,383,336.09 (10.3%); £3,773,858.44 -> £3,383,336.11 (10.3%); £3,773,858.57 -> £3,383,336.27 (10.3%); £3,773,858.70 -> £3,383,336.44 (10.3%); £3,773,858.85 -> £3,383,336.61 (10.3%); £3,773,859.02 -> £3,383,336.79 (10.3%); £3,773,859.20 -> £3,383,336.97 (10.3%); £3,773,859.40 -> £3,383,337.16 (10.3%); £3,773,859.61 -> £3,383,337.34 (10.3%); £3,773,859.84 -> £3,383,337.52 (10.3%); £3,773,860.07 -> £3,383,337.55 (10.3%); £3,773,860.29 -> £3,383,337.58 (10.3%); £3,773,860.52 -> £3,383,337.60 (10.3%); £3,773,860.75 -> £3,383,337.63 (10.3%); £3,773,860.97 -> £3,383,337.66 (10.3%); £3,773,861.20 -> £3,383,337.69 (10.3%); £3,773,861.43 -> £3,383,337.71 (10.3%); £3,773,861.66 -> £3,383,337.74 (10.3%); £3,773,861.88 -> £3,383,337.77 (10.3%); £3,773,862.11 -> £3,383,337.79 (10.3%); £3,773,862.33 -> £3,383,337.82 (10.3%); £3,773,862.55 -> £3,383,337.85 (10.3%); £3,773,862.78 -> £3,383,337.88 (10.3%); £3,773,863.01 -> £3,383,338.05 (10.3%); £3,773,863.24 -> £3,383,338.22 (10.3%); £3,773,863.47 -> £3,383,338.40 (10.3%); £3,773,863.70 -> £3,383,338.57 (10.3%); £3,773,863.93 -> £3,383,338.74 (10.3%); £3,773,864.16 -> £3,383,338.92 (10.3%); £3,773,864.38 -> £3,383,339.09 (10.3%); £3,773,864.61 -> £3,383,339.27 (10.3%); £3,773,864.84 -> £3,383,339.45 (10.3%); £3,773,865.06 -> £3,383,339.62 (10.3%); £3,773,865.28 -> £3,383,339.80 (10.3%); £3,773,865.51 -> £3,383,339.83 (10.3%); £3,773,865.74 -> £3,383,339.85 (10.3%); £3,773,865.95 -> £3,383,339.88 (10.3%); £3,773,866.14 -> £3,383,339.90 (10.3%); £3,773,866.31 -> £3,383,339.93 (10.3%); £3,773,866.45 -> £3,383,339.95 (10.3%); £3,773,866.59 -> £3,383,339.97 (10.3%); £3,773,866.73 -> £3,383,339.99 (10.3%); £3,773,866.87 -> £3,383,340.00 (10.3%); £3,773,867.02 -> £3,383,340.02 (10.3%); £3,773,867.15 -> £3,383,340.04 (10.3%); £3,773,867.29 -> £3,383,340.06 (10.3%); £3,773,867.44 -> £3,383,340.07 (10.3%); £3,773,867.58 -> £3,383,340.09 (10.3%); £3,773,867.72 -> £3,383,340.11 (10.3%); £3,773,867.86 -> £3,383,340.12 (10.3%); £3,773,868.01 -> £3,383,340.27 (10.3%); £3,773,868.15 -> £3,383,340.42 (10.3%); £3,773,868.30 -> £3,383,340.56 (10.3%); £3,773,868.47 -> £3,383,340.72 (10.3%); £3,773,868.66 -> £3,383,340.87 (10.3%); £3,773,868.87 -> £3,383,341.03 (10.3%); £3,773,869.08 -> £3,383,341.19 (10.3%); £3,773,869.31 -> £3,383,341.35 (10.3%); £3,773,869.54 -> £3,383,341.38 (10.3%); £3,773,869.78 -> £3,383,341.41 (10.3%); £3,773,870.01 -> £3,383,341.44 (10.3%); £3,773,870.24 -> £3,383,341.47 (10.3%); £3,773,870.47 -> £3,383,341.50 (10.3%); £3,773,870.70 -> £3,383,341.53 (10.3%); £3,773,870.94 -> £3,383,341.56 (10.3%); £3,773,871.17 -> £3,383,341.59 (10.3%); £3,773,871.40 -> £3,383,341.62 (10.3%); £3,773,871.63 -> £3,383,341.65 (10.3%); £3,773,871.87 -> £3,383,341.68 (10.3%); £3,773,872.09 -> £3,383,341.71 (10.3%); £3,773,872.32 -> £3,383,341.74 (10.3%); £3,773,872.56 -> £3,383,341.89 (10.3%); £3,773,872.79 -> £3,383,342.04 (10.3%); £3,773,873.03 -> £3,383,342.19 (10.3%); £3,773,873.26 -> £3,383,342.35 (10.3%); £3,773,873.49 -> £3,383,342.50 (10.3%); £3,773,873.72 -> £3,383,342.65 (10.3%); £3,773,873.95 -> £3,383,342.81 (10.3%); £3,773,874.20 -> £3,383,342.96 (10.3%); £3,773,874.44 -> £3,383,343.11 (10.3%); £3,773,874.67 -> £3,383,343.26 (10.3%); £3,773,874.91 -> £3,383,343.41 (10.3%); £3,773,875.14 -> £3,383,343.44 (10.3%); £3,773,875.37 -> £3,383,343.47 (10.3%); £3,773,875.60 -> £3,383,343.49 (10.3%); £3,773,875.80 -> £3,383,343.52 (10.3%); £3,773,875.98 -> £3,383,343.54 (10.3%); £3,773,876.14 -> £3,383,343.55 (10.3%); £3,773,876.30 -> £3,383,343.57 (10.3%); £3,773,876.46 -> £3,383,343.59 (10.3%); £3,773,876.62 -> £3,383,343.61 (10.3%); £3,773,876.79 -> £3,383,343.62 (10.3%); £3,773,876.94 -> £3,383,343.64 (10.3%); £3,773,877.11 -> £3,383,343.66 (10.3%); £3,773,877.27 -> £3,383,343.67 (10.3%); £3,773,877.43 -> £3,383,343.69 (10.3%); £3,773,877.60 -> £3,383,343.71 (10.3%); £3,773,877.75 -> £3,383,343.72 (10.3%); £3,773,877.92 -> £3,383,343.86 (10.3%); £3,773,878.08 -> £3,383,344.00 (10.3%); £3,773,878.25 -> £3,383,344.15 (10.3%); £3,773,878.46 -> £3,383,344.30 (10.3%); £3,773,878.67 -> £3,383,344.45 (10.3%); £3,773,878.90 -> £3,383,344.60 (10.3%); £3,773,879.15 -> £3,383,344.75 (10.3%); £3,773,879.43 -> £3,383,344.89 (10.3%); £3,773,879.70 -> £3,383,344.92 (10.3%); £3,773,879.98 -> £3,383,344.94 (10.3%); £3,773,880.25 -> £3,383,344.97 (10.3%); £3,773,880.52 -> £3,383,344.99 (10.3%); £3,773,880.79 -> £3,383,345.02 (10.3%); £3,773,881.06 -> £3,383,345.04 (10.3%); £3,773,881.33 -> £3,383,345.06 (10.3%); £3,773,881.59 -> £3,383,345.09 (10.3%); £3,773,881.87 -> £3,383,345.11 (10.3%); £3,773,882.14 -> £3,383,345.13 (10.3%); £3,773,882.42 -> £3,383,345.16 (10.3%); £3,773,882.69 -> £3,383,345.18 (10.3%); £3,773,882.96 -> £3,383,345.21 (10.3%); £3,773,883.23 -> £3,383,345.35 (10.3%); £3,773,883.49 -> £3,383,345.50 (10.3%); £3,773,883.77 -> £3,383,345.65 (10.3%); £3,773,884.03 -> £3,383,345.80 (10.3%); £3,773,884.29 -> £3,383,345.95 (10.3%); £3,773,884.55 -> £3,383,346.10 (10.3%); £3,773,884.82 -> £3,383,346.26 (10.3%); £3,773,885.09 -> £3,383,346.41 (10.3%); £3,773,885.36 -> £3,383,346.55 (10.3%); £3,773,885.62 -> £3,383,346.70 (10.3%); £3,773,885.89 -> £3,383,346.85 (10.3%); £3,773,886.15 -> £3,383,346.88 (10.3%); £3,773,886.43 -> £3,383,346.90 (10.3%); £3,773,886.66 -> £3,383,346.93 (10.3%); £3,773,886.89 -> £3,383,346.95 (10.3%); £3,773,887.10 -> £3,383,346.97 (10.3%); £3,773,887.26 -> £3,383,346.99 (10.3%); £3,773,887.42 -> £3,383,347.01 (10.3%); £3,773,887.59 -> £3,383,347.02 (10.3%); £3,773,887.76 -> £3,383,347.04 (10.3%); £3,773,887.92 -> £3,383,347.06 (10.3%); £3,773,888.08 -> £3,383,347.07 (10.3%); £3,773,888.24 -> £3,383,347.09 (10.3%); £3,773,888.41 -> £3,383,347.11 (10.3%); £3,773,888.57 -> £3,383,347.12 (10.3%); £3,773,888.73 -> £3,383,347.14 (10.3%); £3,773,888.89 -> £3,383,347.16 (10.3%); £3,773,889.05 -> £3,383,347.27 (10.3%); £3,773,889.22 -> £3,383,347.38 (10.3%); £3,773,889.39 -> £3,383,347.50 (10.3%); £3,773,889.60 -> £3,383,347.63 (10.3%); £3,773,889.81 -> £3,383,347.76 (10.3%); £3,773,890.05 -> £3,383,347.89 (10.3%); £3,773,890.30 -> £3,383,348.01 (10.3%); £3,773,890.57 -> £3,383,348.13 (10.3%); £3,773,890.84 -> £3,383,348.16 (10.3%); £3,773,891.12 -> £3,383,348.18 (10.3%); £3,773,891.39 -> £3,383,348.20 (10.3%); £3,773,891.64 -> £3,383,348.23 (10.3%); £3,773,891.91 -> £3,383,348.25 (10.3%); £3,773,892.18 -> £3,383,348.28 (10.3%); £3,773,892.44 -> £3,383,348.30 (10.3%); £3,773,892.71 -> £3,383,348.32 (10.3%); £3,773,892.97 -> £3,383,348.35 (10.3%); £3,773,893.24 -> £3,383,348.37 (10.3%); £3,773,893.51 -> £3,383,348.39 (10.3%); £3,773,893.79 -> £3,383,348.42 (10.3%); £3,773,894.06 -> £3,383,348.45 (10.3%); £3,773,894.33 -> £3,383,348.58 (10.3%); £3,773,894.59 -> £3,383,348.71 (10.3%); £3,773,894.87 -> £3,383,348.84 (10.3%); £3,773,895.13 -> £3,383,348.97 (10.3%); £3,773,895.40 -> £3,383,349.10 (10.3%); £3,773,895.67 -> £3,383,349.23 (10.3%); £3,773,895.93 -> £3,383,349.36 (10.3%); £3,773,896.19 -> £3,383,349.49 (10.3%); £3,773,896.46 -> £3,383,349.62 (10.3%); £3,773,896.73 -> £3,383,349.75 (10.3%); £3,773,897.01 -> £3,383,349.88 (10.3%); £3,773,897.28 -> £3,383,349.91 (10.3%); £3,773,897.55 -> £3,383,349.94 (10.3%); £3,773,897.79 -> £3,383,349.96 (10.3%); £3,773,898.02 -> £3,383,349.99 (10.3%); £3,773,898.24 -> £3,383,350.01 (10.3%); £3,773,898.40 -> £3,383,350.02 (10.3%); £3,773,898.56 -> £3,383,350.04 (10.3%); £3,773,898.72 -> £3,383,350.06 (10.3%); £3,773,898.88 -> £3,383,350.08 (10.3%); £3,773,899.03 -> £3,383,350.09 (10.3%); £3,773,899.20 -> £3,383,350.11 (10.3%); £3,773,899.35 -> £3,383,350.13 (10.3%); £3,773,899.51 -> £3,383,350.14 (10.3%); £3,773,899.67 -> £3,383,350.16 (10.3%); £3,773,899.83 -> £3,383,350.18 (10.3%); £3,773,899.99 -> £3,383,350.19 (10.3%); £3,773,900.14 -> £3,383,350.33 (10.3%); £3,773,900.30 -> £3,383,350.47 (10.3%); £3,773,900.48 -> £3,383,350.63 (10.3%); £3,773,900.68 -> £3,383,350.78 (10.3%); £3,773,900.90 -> £3,383,350.92 (10.3%); £3,773,901.13 -> £3,383,351.07 (10.3%); £3,773,901.38 -> £3,383,351.22 (10.3%); £3,773,901.65 -> £3,383,351.36 (10.3%); £3,773,901.92 -> £3,383,351.39 (10.3%); £3,773,902.19 -> £3,383,351.41 (10.3%); £3,773,902.46 -> £3,383,351.43 (10.3%); £3,773,902.73 -> £3,383,351.46 (10.3%); £3,773,902.99 -> £3,383,351.48 (10.3%); £3,773,903.27 -> £3,383,351.51 (10.3%); £3,773,903.54 -> £3,383,351.53 (10.3%); £3,773,903.81 -> £3,383,351.55 (10.3%); £3,773,904.09 -> £3,383,351.58 (10.3%); £3,773,904.36 -> £3,383,351.60 (10.3%); £3,773,904.62 -> £3,383,351.62 (10.3%); £3,773,904.89 -> £3,383,351.65 (10.3%); £3,773,905.16 -> £3,383,351.68 (10.3%); £3,773,905.43 -> £3,383,351.84 (10.3%); £3,773,905.70 -> £3,383,352.00 (10.3%); £3,773,905.97 -> £3,383,352.16 (10.3%); £3,773,906.24 -> £3,383,352.32 (10.3%); £3,773,906.51 -> £3,383,352.48 (10.3%); £3,773,906.78 -> £3,383,352.64 (10.3%); £3,773,907.05 -> £3,383,352.79 (10.3%); £3,773,907.32 -> £3,383,352.94 (10.3%); £3,773,907.58 -> £3,383,353.09 (10.3%); £3,773,907.85 -> £3,383,353.24 (10.3%); £3,773,908.12 -> £3,383,353.39 (10.3%); £3,773,908.39 -> £3,383,353.42 (10.3%); £3,773,908.67 -> £3,383,353.45 (10.3%); £3,773,908.92 -> £3,383,353.47 (10.3%); £3,773,909.14 -> £3,383,353.49 (10.3%); £3,773,909.35 -> £3,383,353.51 (10.3%); £3,773,909.51 -> £3,383,353.53 (10.3%); £3,773,909.68 -> £3,383,353.55 (10.3%); £3,773,909.84 -> £3,383,353.57 (10.3%); £3,773,910.00 -> £3,383,353.58 (10.3%); £3,773,910.16 -> £3,383,353.60 (10.3%); £3,773,910.32 -> £3,383,353.62 (10.3%); £3,773,910.48 -> £3,383,353.63 (10.3%); £3,773,910.64 -> £3,383,353.65 (10.3%); £3,773,910.80 -> £3,383,353.67 (10.3%); £3,773,910.96 -> £3,383,353.68 (10.3%); £3,773,911.12 -> £3,383,353.70 (10.3%); £3,773,911.28 -> £3,383,353.85 (10.3%); £3,773,911.44 -> £3,383,353.99 (10.3%); £3,773,911.63 -> £3,383,354.14 (10.3%); £3,773,911.83 -> £3,383,354.28 (10.3%); £3,773,912.05 -> £3,383,354.43 (10.3%); £3,773,912.28 -> £3,383,354.58 (10.3%); £3,773,912.53 -> £3,383,354.72 (10.3%); £3,773,912.81 -> £3,383,354.86 (10.3%); £3,773,913.08 -> £3,383,354.89 (10.3%); £3,773,913.35 -> £3,383,354.91 (10.3%); £3,773,913.61 -> £3,383,354.93 (10.3%); £3,773,913.89 -> £3,383,354.96 (10.3%); £3,773,914.16 -> £3,383,354.98 (10.3%); £3,773,914.43 -> £3,383,355.00 (10.3%); £3,773,914.70 -> £3,383,355.03 (10.3%); £3,773,914.98 -> £3,383,355.05 (10.3%); £3,773,915.26 -> £3,383,355.07 (10.3%); £3,773,915.52 -> £3,383,355.10 (10.3%); £3,773,915.79 -> £3,383,355.12 (10.3%); £3,773,916.07 -> £3,383,355.15 (10.3%); £3,773,916.34 -> £3,383,355.17 (10.3%); £3,773,916.62 -> £3,383,355.32 (10.3%); £3,773,916.89 -> £3,383,355.47 (10.3%); £3,773,917.16 -> £3,383,355.63 (10.3%); £3,773,917.43 -> £3,383,355.78 (10.3%); £3,773,917.69 -> £3,383,355.93 (10.3%); £3,773,917.97 -> £3,383,356.08 (10.3%); £3,773,918.25 -> £3,383,356.23 (10.3%); £3,773,918.53 -> £3,383,356.38 (10.3%); £3,773,918.80 -> £3,383,356.52 (10.3%); £3,773,919.08 -> £3,383,356.67 (10.3%); £3,773,919.34 -> £3,383,356.81 (10.3%); £3,773,919.62 -> £3,383,356.84 (10.3%); £3,773,919.89 -> £3,383,356.87 (10.3%); £3,773,920.15 -> £3,383,356.89 (10.3%); £3,773,920.39 -> £3,383,356.91 (10.3%); £3,773,920.60 -> £3,383,356.93 (10.3%); £3,773,920.76 -> £3,383,356.95 (10.3%); £3,773,920.92 -> £3,383,356.97 (10.3%); £3,773,921.08 -> £3,383,356.99 (10.3%); £3,773,921.25 -> £3,383,357.00 (10.3%); £3,773,921.41 -> £3,383,357.02 (10.3%); £3,773,921.57 -> £3,383,357.04 (10.3%); £3,773,921.74 -> £3,383,357.05 (10.3%); £3,773,921.90 -> £3,383,357.07 (10.3%); £3,773,922.06 -> £3,383,357.09 (10.3%); £3,773,922.22 -> £3,383,357.10 (10.3%); £3,773,922.39 -> £3,383,357.12 (10.3%); £3,773,922.55 -> £3,383,357.24 (10.3%); £3,773,922.71 -> £3,383,357.37 (10.3%); £3,773,922.89 -> £3,383,357.50 (10.3%); £3,773,923.08 -> £3,383,357.63 (10.3%); £3,773,923.30 -> £3,383,357.76 (10.3%); £3,773,923.53 -> £3,383,357.89 (10.3%); £3,773,923.78 -> £3,383,358.02 (10.3%); £3,773,924.04 -> £3,383,358.15 (10.3%); £3,773,924.32 -> £3,383,358.18 (10.3%); £3,773,924.59 -> £3,383,358.20 (10.3%); £3,773,924.85 -> £3,383,358.22 (10.3%); £3,773,925.13 -> £3,383,358.25 (10.3%); £3,773,925.39 -> £3,383,358.27 (10.3%); £3,773,925.67 -> £3,383,358.30 (10.3%); £3,773,925.95 -> £3,383,358.32 (10.3%); £3,773,926.22 -> £3,383,358.34 (10.3%); £3,773,926.49 -> £3,383,358.37 (10.3%); £3,773,926.76 -> £3,383,358.39 (10.3%); £3,773,927.03 -> £3,383,358.41 (10.3%); £3,773,927.29 -> £3,383,358.44 (10.3%); £3,773,927.56 -> £3,383,358.47 (10.3%); £3,773,927.83 -> £3,383,358.60 (10.3%); £3,773,928.10 -> £3,383,358.74 (10.3%); £3,773,928.37 -> £3,383,358.89 (10.3%); £3,773,928.64 -> £3,383,359.03 (10.3%); £3,773,928.92 -> £3,383,359.17 (10.3%); £3,773,929.18 -> £3,383,359.31 (10.3%); £3,773,929.46 -> £3,383,359.45 (10.3%); £3,773,929.72 -> £3,383,359.59 (10.3%); £3,773,929.99 -> £3,383,359.73 (10.3%); £3,773,930.28 -> £3,383,359.88 (10.3%); £3,773,930.55 -> £3,383,360.01 (10.3%); £3,773,930.82 -> £3,383,360.04 (10.3%); £3,773,931.08 -> £3,383,360.07 (10.3%); £3,773,931.34 -> £3,383,360.09 (10.3%); £3,773,931.57 -> £3,383,360.11 (10.3%)
- Bills issued: 141, average clarity 0.805, average bill shock 17.2%, bad debt provision £1,025.31, avg complaint probability 4.9%
- Solvency signal: £343,354/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £199,174.16 vs. naked (unhedged) net margin: £604,582.32
- hedging cost £405,408.17 vs. a fully unhedged book (commodity-only: actual net £199,174.16 vs. naked net £604,582.32)
  - C1_2: actual £207.67 vs. naked £705.98 -- hedging cost £498.32
  - C2_2: actual £111.46 vs. naked £1,050.29 -- hedging cost £938.83
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £310.93 vs. naked £1,424.84 -- hedging cost £1,113.91
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £18,349.13 vs. naked £119,157.58 -- hedging cost £100,808.45
  - C_IC3g: actual £3,837.46 vs. naked £56,934.03 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £102,722.50 -- hedging cost £101,286.98

**Year narrative:** 2024 produced a net gain of £346,801.23 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 40 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £120,992.95 (gross £518,927.35, capital £5,646.32)
  - Electricity: gross £465,418.57, capital £5,646.32, net £116,543.17
  - Gas: gross £53,508.78, capital £0.00, net £4,449.79
- Treasury at year end: £3,828,578.60
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
- Average CLV (Point-in-Time, year-end 2025): £367,536.22
  - By billing account: C1 £3,791.32, C1_2 £3,674.38, C2 £4,828.14, C2_2 £3,197.06, C3 £4,696.51, C4 £2,775.46, C5 £9,340.29, C6 £14,672.77, C7 £6,699.47, C8 £6,827.64, C9 £7,476.35, C_IC1 £1,318,327.54, C_IC2 £779,985.99, C_IC3 £2,205,296.81, C_IC4 £1,141,453.62
- Bill shock events (>=20%): 23 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C1_2 2025-04-30 (42%); C1_2 2025-05-31 (28%); C1_2 2025-06-07 (80%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (34%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 32%, C8 32%, C9 26%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01/MWh, net margin £233.00
- C2_2 (electricity): tariff £200.84-£289.53/MWh, net margin £128.61
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £19.93
- C8 (electricity): tariff £149.29-£309.26/MWh, net margin £117.89
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
- Solvency signal: £425,398/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £61.99 vs. naked (unhedged) net margin: £345.44
- hedging cost £283.45 vs. a fully unhedged book (commodity-only: actual net £61.99 vs. naked net £345.44)
  - C2_2: actual £92.07 vs. naked £226.54 -- hedging cost £134.47
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £120,992.95 across 10 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 23 customer(s) experienced a bill shock of >=20%.
