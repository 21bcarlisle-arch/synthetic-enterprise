# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,911,893.89
  (£1,445,257.67 net change)
- Solvency signal (final year): £383,606/customer (10 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £19,819,620.93
  VAT remitted to HMRC: (£957,157.22) | Revenue (ex-VAT): £18,862,463.71
  Non-commodity pass-through: (£4,787,181.64)
- Gross margin: £6,467,308.57
- Capital costs: £51,432.98
- Net margin: £6,415,875.59
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1605, average clarity 0.811,
  service quality score 0.903
- Enterprise value (CLV sum across 16 billing accounts): £8,930,210.95
- Cost to serve (whole portfolio): £19,259.69, net margin after cost to serve: £6,396,615.90
- Hedge effectiveness (whole window): hedging cost £4,232,037.05 vs. a fully unhedged book (commodity-only: actual net £1,445,257.67 vs. naked net £5,677,294.72)

- **2021** (crisis year): net margin £76,456.70, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £336,112.17, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2241, I&C 98% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 327.8x (net £64,798.54 on £197.67 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 4/6 departures (67%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 3.1%, max 15.6% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +33.1% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 34.0% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,467,308.57, capital £51,432.98, net £6,415,875.59. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £76,456.70 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,415,875.59
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,677,294.72
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,232,037.05 vs. a fully unhedged book (commodity-only: actual net £1,445,257.67 vs. naked net £5,677,294.72)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,382.46 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £612,664.13 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £-134.52 | £553.23 | £324.29 | £743.01 |
| 2017 | £30,139.92 | £0.00 | £361.26 | £622.10 | £516.54 | £31,639.82 |
| 2018 | £101,162.40 | £0.00 | £-187.39 | £346.75 | £436.94 | £101,758.70 |
| 2019 | £222,407.66 | £9,999.92 | £-218.60 | £812.55 | £489.73 | £233,491.26 |
| 2020 | £116,595.99 | £10,030.76 | £436.45 | £1,050.84 | £457.36 | £128,571.40 |
| 2021 | £66,401.97 | £9,999.92 | £-87.04 | £318.57 | £-176.72 | £76,456.70 |
| 2022 | £327,008.57 | £9,999.92 | £1,579.92 | £-1,320.02 | £-1,156.22 | £336,112.17 |
| 2023 | £151,761.38 | £9,999.92 | £412.46 | £645.03 | £-1,040.96 | £161,777.83 |
| 2024 | £326,179.35 | £10,030.76 | £1,763.52 | £3,254.83 | £436.59 | £341,665.05 |
| 2025 | £117,774.12 | £4,449.79 | £135.46 | £732.43 | £0.00 | £123,091.80 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **56** renewals.  Lost (churned): **6** accounts.

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
| C1 | 2018-12-31 | renewed | 0.1100 | 0.5500 | 0.9317 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.1100 | 0.3500 | 0.8718 | 0.3096 |
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
| C5 | 2020-12-30 | renewed | 0.3200 | 0.3500 | 0.8696 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.2000 | 0.5500 | 0.8827 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.2000 | 0.5500 | 0.8827 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.0800 | 0.5500 | 0.9707 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.0800 | 0.3500 | 0.9576 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.1100 | 0.5500 | 0.9597 | 0.4564 |
| C1_2 | 2021-12-30 | renewed | 0.0500 | 0.5500 | 0.9833 | 0.2977 |
| C5 | 2021-12-30 | renewed | 0.1700 | 0.3500 | 0.9280 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.3200 | 0.5500 | 0.9138 | 0.5838 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.3800 | 0.5500 | 0.9511 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3500 | 0.3500 | 0.9511 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.2600 | 0.5500 | 0.9511 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3500 | 0.5500 | 0.9364 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.3800 | 0.5500 | 0.9364 | 0.8552 |
| C1_2 | 2022-12-30 | renewed | 0.4100 | 0.5500 | 0.9556 | 0.9433 |
| C5 | 2022-12-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.9511 | 0.9650 |
| C7 | 2022-12-30 | renewed | 0.2300 | 0.5500 | 0.9364 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.4100 | 0.5500 | 0.9511 | 0.8723 |
| C2_2 | 2023-03-31 | renewed | 0.0500 | 0.5500 | 0.9802 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.4100 | 0.3500 | 0.8084 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.9251 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.8739 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.4100 | 0.5500 | 0.8739 | 0.6095 |
| C1_2 | 2023-12-30 | renewed | 0.1700 | 0.5500 | 0.9326 | 0.5453 |
| C5_2 | 2023-12-30 | renewed | 0.0500 | 0.3500 | 0.9714 | 0.6875 |
| C7 | 2023-12-30 | renewed | 0.4100 | 0.5500 | 0.9026 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.4100 | 0.5500 | 0.9030 | 0.7019 |
| C2_2 | 2024-03-30 | renewed | 0.2300 | 0.5500 | 0.9000 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.2900 | 0.3500 | 0.7926 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.1700 | 0.5500 | 0.9350 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.1700 | 0.5500 | 0.8906 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.3800 | 0.5500 | 0.8570 | 0.9018 |
| C1_2 | 2024-12-29 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.1722 |
| C5_2 | 2024-12-29 | renewed | 0.0800 | 0.3500 | 0.9480 | 0.4422 |
| C7 | 2024-12-29 | renewed | 0.2900 | 0.5500 | 0.8895 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.4100 | 0.5500 | 0.7971 | 0.3751 |
| C2_2 | 2025-03-30 | renewed | 0.3200 | 0.5500 | 0.8889 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3200 | 0.5500 | 0.9056 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 150.4%
- **Average signed error:** +127.1% (over-estimates vs SIM)
- **Renewal events with estimates:** 62

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +113.9% | 113.9% |
| 2017 | 3 | -4.9% | 12.9% |
| 2018 | 4 | +663.5% | 663.5% |
| 2019 | 4 | +602.3% | 642.0% |
| 2020 | 10 | -7.8% | 54.7% |
| 2021 | 9 | +134.9% | 149.9% |
| 2022 | 9 | -3.6% | 13.3% |
| 2023 | 9 | +132.6% | 145.8% |
| 2024 | 9 | +18.0% | 38.5% |
| 2025 | 2 | +15.0% | 22.9% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 62
- **Active renewers:** 20 (32%) — mean company estimate 24.8%, abs error 276.5%
- **Passive SVT-rollers:** 42 (68%) — mean company estimate 10.6%, abs error 90.3%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 13.3% | 0.0% | 113.9% |
| 2017 | 0 | 3 | 0.0% | 9.4% | 0.0% | 12.9% |
| 2018 | 2 | 2 | 32.8% | 54.4% | 194.6% | 1132.3% |
| 2019 | 2 | 2 | 53.2% | 13.6% | 1267.4% | 16.7% |
| 2020 | 5 | 5 | 12.2% | 7.0% | 66.9% | 42.5% |
| 2021 | 3 | 6 | 38.2% | 5.4% | 287.8% | 81.0% |
| 2022 | 0 | 9 | 0.0% | 5.2% | 0.0% | 13.3% |
| 2023 | 4 | 5 | 21.2% | 10.1% | 299.7% | 22.7% |
| 2024 | 4 | 5 | 15.7% | 11.0% | 52.2% | 27.6% |
| 2025 | 0 | 2 | 0.0% | 11.6% | 0.0% | 22.9% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 42
- **Above SVT (at-risk):** 10 (24%)
- **Below/at SVT (protected):** 32 (76%)
- **Mean rate vs SVT premium:** -10.0%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.1 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 119.9 | 140.0 |
| 2018 | 2 | 1 (50%) | +0.2% | 152.9 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -25.8% | 131.2 | 176.9 |
| 2021 | 6 | 4 (67%) | +12.8% | 209.1 | 183.8 |
| 2022 | 9 | 4 (44%) | -1.2% | 291.6 | 362.9 |
| 2023 | 5 | 0 (0%) | -32.7% | 224.7 | 364.0 |
| 2024 | 5 | 0 (0%) | -13.9% | 211.3 | 246.5 |
| 2025 | 2 | 1 (50%) | -2.9% | 241.4 | 248.6 |

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
| 2021 | 17 | 14.5% | 44.5% |
| 2022 | 18 | 12.4% | 23.2% |
| 2023 | 16 | 22.3% | 40.0% |
| 2024 | 15 | 10.8% | 22.6% |
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
| 2018 | 4 | 6.63× ⚠ | 22.57× |
| 2019 | 4 | 6.42× ⚠ | 24.89× |
| 2020 | 10 | 0.55× | 1.55× |
| 2021 | 9 | 1.50× | 4.47× |
| 2022 | 9 | 0.13× | 0.28× |
| 2023 | 9 | 1.46× | 7.88× |
| 2024 | 9 | 0.38× | 0.84× |
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
| 2021 | 11 | 1.07% | 4.24% | MODERATE — asset adoption visible |
| 2022 | 11 | 2.47% | 7.47% | MODERATE — asset adoption visible |
| 2023 | 11 | 2.35% | 8.47% | MODERATE — asset adoption visible |
| 2024 | 11 | 3.07% | 15.56% | HIGH drift — EV/asset cohort growing |
| 2025 | 2 | 1.42% | 2.07% | MODERATE — asset adoption visible |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **3.07%** mean / **15.56%** max in 2024. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
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
| 2022 | 11 | 2.5% | 7.5% |
| 2023 | 11 | 2.4% | 8.5% |
| 2024 | 11 | 3.1% | 15.6% |
| 2025 | 2 | 1.4% | 2.1% |

**92** of **92** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## EAC Drift Snapshot (Phase AI)

Per-customer consumption drift from company billing history (first renewal → latest renewal).
Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.

**1 significant** (≥15%) | **2 moderate** (5–15%) | **12 stable** (<5%)

| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |
|----------|-------------|-------------|-------|--------------|
| C4 | 4,131 | 3,365 | -19% | likely solar installation or significant efficiency upgrade |
| C1_2 | 10,401 | 9,227 | -11% | efficiency improvement or reduced occupancy |
| C7 | 13,179 | 12,155 | -8% | efficiency improvement or reduced occupancy |

**Portfolio demand trend:** 3 customers increasing / 11 decreasing (mean drift: -3.2%)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **9** (6 churn, 3 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.06, company est=0.08 |
| 2020-12-30 | CHURN | C1 | SIM p=0.22, company est=0.07 |
| 2020-12-30 | ACQUISITION | C1_2 | home-move-win (predecessor: C1) |
| 2022-03-31 | CHURN | C2 | SIM p=0.05, company est=0.06 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2022-12-30 | CHURN | C5 | SIM p=0.05, company est=0.05 |
| 2022-12-30 | ACQUISITION | C5_2 | home-move-win (predecessor: C5) |
| 2024-03-30 | CHURN | C6 | SIM p=0.21, company est=0.25 |
| 2024-09-29 | CHURN | C4 | SIM p=0.14, company est=0.14 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 2 accounts | 1 active | yes |
| 2021-12-31 | 2 accounts | 1 active | yes |
| 2022-12-31 | 4 accounts | 3 active | yes |
| 2023-12-31 | 4 accounts | 3 active | yes |
| 2024-12-31 | 6 accounts | 3 active | yes |
| 2025-12-31 | 6 accounts | 3 active | yes |

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
| 2020 | 238,638 | 35,391 | 69,454 | 56,550 | 70,024 | 0 | 470,058 |  |
| 2021 | 246,702 | 15,010 | 71,336 | 49,675 | 62,836 | 41,427 | 486,987 |  |
| 2022 | 256,667 | -49,827 | 71,047 | 36,748 | 69,231 | 99,654 | 483,520 | ⬇ CfD REBATE |
| 2023 | 272,368 | 64,889 | 71,831 | 51,053 | 75,240 | 13,776 | 549,157 |  |
| 2024 | 308,162 | 110,127 | 72,944 | 68,826 | 82,707 | 2,002 | 644,768 |  |
| 2025 | 136,010 | 47,047 | 31,221 | 31,094 | 36,227 | 855 | 282,455 |  |
| **Total** | **1,727,002** | **263,580** | **459,082** | **337,279** | **468,096** | **157,716** | **3,412,755** | |

Total policy cost: £3,412,755 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2020 | 124,589 |  |
| 2021 | 123,772 |  |
| 2022 | 134,698 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 140,894 | RIIO-ED2 from Apr 2023 |
| 2024 | 144,687 |  |
| 2025 | 61,977 |  |
| **Total** | **886,938** | |

Total network cost: £886,938 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

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
| 2020 | 2,923,332 | 14 | 208,809 | 1606.23× | OK |
| 2021 | 2,958,034 | 12 | 246,503 | 1896.18× | OK |
| 2022 | 3,159,446 | 14 | 225,675 | 1735.96× | OK |
| 2023 | 3,395,544 | 12 | 282,962 | 2176.63× | OK |
| 2024 | 3,784,369 | 12 | 315,364 | 2425.88× | OK |
| 2025 | 3,836,063 | 10 | 383,606 | 2950.82× | OK |

End-state (2025): **£383,606/account** across 10 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,434 | 81947.3× | OK |
| 2017 | 466 | 559 | 2,498,375 | 4468.9× | OK |
| 2018 | 849 | 1,019 | 2,487,547 | 2440.9× | OK |
| 2019 | 1,543 | 1,851 | 2,611,522 | 1410.8× | OK |
| 2020 | 1,979 | 2,375 | 2,923,332 | 1231.0× | OK |
| 2021 | 4,342 | 5,211 | 2,958,034 | 567.7× | OK |
| 2022 | 8,509 | 10,211 | 3,159,446 | 309.4× | OK |
| 2023 | 5,630 | 6,755 | 3,395,544 | 502.6× | OK |
| 2024 | 2,667 | 3,200 | 3,784,369 | 1182.7× | OK |
| 2025 | 3,902 | 4,682 | 3,836,063 | 819.2× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,524.77 | £12,268.08 | £262.76/MWh | £145.03/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,986.02 | £9,702.76 | £272.73/MWh | £154.57/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,933.12 | £9,310.54 | £250.25/MWh | £141.72/MWh | +10.9% |

Total HH revenue: £63,725.29 vs flat equivalent £58,821.31 (+8.3% ToU premium)

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
| 2021 | 52 | 1207% | C1_2 (2021-01-31) |
| 2022 | 76 | 1735% | C2_2 (2022-04-30) |
| 2023 | 53 | 2059% | C5_2 (2023-01-31) |
| 2024 | 45 | 107% | C_IC2 (2024-07-31) |
| 2025 | 25 | 80% | C1_2 (2025-06-07) |

Total: **511** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2023-01-31 | C5_2 | +2059% | no |
| 2022-04-30 | C2_2 | +1735% | no |
| 2021-01-31 | C1_2 | +1207% | no |
| 2022-01-31 | C1_2 | +141% | no |
| 2022-10-31 | C4g | +134% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2022-01-31 | C5 | +128% | yes |
| 2020-03-31 | C_IC2 | +118% | no |
| 2021-10-31 | C4g | +113% | no |
| 2022-01-31 | C_IC3 | +108% | no |

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
| Offers made | 14 |
| Retained | 14 (100%) |
| Churned despite offer | 0 |
| Total offer cost (foregone margin) | £150,009.81 |
| Margin saved (retained customers' terms) | £1,207,026.38 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£1,057,016.57** |
| Acquisition cost avoided (retained customers) | £2,600.00 |
| **Full economic ROI (margin + acq savings)** | **£1,059,616.57** |

Missed opportunities (churns with no offer): **6** (£6,623.39 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 6 (£6,623.39 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 2 | 2 | £71.20 | £1362.45 | £1291.25 | £0.00 |
| 2018 | 3 | 3 | £24267.43 | £164429.07 | £140161.64 | £0.00 |
| 2019 | 2 | 2 | £32311.18 | £296612.44 | £264301.26 | £0.00 |
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £1000.56 |
| 2021 | 4 | 4 | £65570.96 | £413560.19 | £347989.23 | £0.00 |
| 2022 | 2 | 2 | £27559.58 | £327840.37 | £300280.79 | £2289.28 |
| 2023 | 1 | 1 | £229.47 | £3221.88 | £2992.40 | £0.00 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £3333.54 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2017-04-01 | C8 | 0.34 | 3% | £46.02 | £867.92 | £150 | £821.90 | retained |
| 2017-07-01 | C3 | 0.39 | 3% | £25.18 | £494.53 | £150 | £469.35 | retained |
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24227.89 | £163704.65 | £150 | £139476.77 | retained |
| 2018-10-01 | C4 | 0.45 | 3% | £18.42 | £345.06 | £150 | £326.64 | retained |
| 2018-12-31 | C1 | 0.36 | 3% | £21.13 | £379.36 | £150 | £358.23 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.66 | 5% | £17469.37 | £194971.28 | £150 | £177501.91 | retained |
| 2021-03-31 | C_IC2 | 0.39 | 3% | £5310.58 | £91314.94 | £150 | £86004.36 | retained |
| 2021-04-30 | C_IC1 | 0.38 | 3% | £8446.52 | £158250.95 | £150 | £149804.43 | retained |
| 2021-12-30 | C5 | 0.49 | 3% | £198.22 | £2475.25 | £400 | £2277.03 | retained |
| 2021-12-31 | C_IC3 | 0.54 | 5% | £51615.63 | £161519.05 | £150 | £109903.42 | retained |
| 2022-04-30 | C_IC2 | 0.40 | 3% | £9417.62 | £96241.44 | £150 | £86823.82 | retained |
| 2022-05-30 | C_IC1 | 0.41 | 3% | £18141.96 | £231598.92 | £150 | £213456.97 | retained |
| 2023-03-31 | C6 | 0.39 | 3% | £229.47 | £3221.88 | £400 | £2992.40 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C8 | 2017-04-01 | (window end) | 105 | active |
| C3 | 2017-07-01 | 2020-06-30 | 36 | churned |
| C_IC1 | 2018-01-31 | (window end) | 95 | active |
| C4 | 2018-10-01 | 2024-09-29 | 72 | churned |
| C1 | 2018-12-31 | 2020-12-30 | 24 | churned |
| C_IC2 | 2019-01-31 | (window end) | 83 | active |
| C5 | 2021-12-30 | 2022-12-30 | 12 | churned |
| C_IC3 | 2021-12-31 | (window end) | 48 | active |
| C6 | 2023-03-31 | 2024-03-30 | 12 | churned |

**Eventually churned (5/9)**: C3, C4, C1, C5, C6 — avg 31 months post-retention before final churn.
**Still active (4/9)**: C8, C_IC1, C_IC2, C_IC3 — survived to simulation end.

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
| C4 | 2018-10-01 | 12 mo | 71.9 mo | churn | no |
| C1 | 2018-12-31 | 12 mo | 24.0 mo | churn | no |
| C_IC2 | 2019-01-31 | 12 mo | 26.0 mo | next_offer | no |
| C_IC2 | 2021-03-31 | 12 mo | 13.0 mo | next_offer | no |
| C_IC2 | 2022-04-30 | 12 mo | still active | none yet | no |
| C5 | 2021-12-30 | 12 mo | 12.0 mo | churn | no |
| C_IC3 | 2021-12-31 | 12 mo | still active | none yet | no |
| C6 | 2023-03-31 | 12 mo | 12.0 mo | churn | no |

0/10 resolved offers (0%) underperformed their assumed deferral window -- the next offer or churn arrived sooner than the term the discount was priced to buy.

Serial savers (2): C_IC1 (4 offers, £68,286), C_IC2 (3 offers, £29,570).

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £8,930,210.95 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £768,064.27 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

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
| 2020 | £128,571.40 |
| 2021 | £76,456.70 |
| 2022 | £336,112.17 |
| 2023 | £161,777.83 | ← trailing
| 2024 | £341,665.05 | ← trailing
| 2025 | £123,091.80 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £5,684.57 | — |
| C1_2 | — | £677.53 |
| C2 | £7,607.67 | — |
| C2_2 | — | £1,637.20 |
| C3 | £7,081.97 | — |
| C4 | £4,258.34 | £-655.92 |
| C5 | £14,695.51 | — |
| C5_2 | — | £473.30 |
| C6 | £22,762.61 | £3,535.10 |
| C7 | £9,626.07 | £625.53 |
| C8 | £11,195.14 | £864.14 |
| C9 | £12,429.21 | £1,564.53 |
| C_IC1 | £1,996,084.25 | £430,673.75 |
| C_IC2 | £1,150,855.11 | £227,729.17 |
| C_IC3 | £3,815,089.31 | £83,354.85 |
| C_IC4 | £1,857,486.62 | £17,585.10 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C1_2 | C2 | C2_2 | C3 | C4 | C5 | C5_2 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £6,441.15 | — | — | — | — | — | £14,339.54 | — | — | £10,526.48 | — | — | — | — | — | — |
| 2017 | £5,663.48 | — | £11,201.34 | — | £9,822.81 | £8,697.48 | £11,936.33 | — | £24,335.45 | £8,960.39 | £13,765.67 | £11,233.24 | — | — | — | — |
| 2018 | £5,908.44 | — | £9,760.41 | — | £9,235.37 | £8,131.44 | £12,553.69 | — | £20,472.90 | £8,866.14 | £11,804.74 | £11,153.98 | £2,833,451.59 | — | — | — |
| 2019 | £6,273.48 | — | £9,836.41 | — | £9,678.42 | £8,087.41 | £14,161.51 | — | £21,122.67 | £10,193.81 | £11,402.42 | £10,995.80 | £2,669,956.93 | £1,778,896.14 | — | — |
| 2020 | £6,522.99 | £16.55 | £9,653.27 | — | £8,572.79 | £8,572.96 | £13,146.03 | — | £19,251.42 | £10,043.04 | £12,191.78 | £10,844.02 | £1,840,925.66 | £823,091.66 | £2,921,176.76 | £1,488,348.49 |
| 2021 | £5,488.85 | £1,262.68 | £7,441.32 | — | £7,226.86 | £6,160.98 | £12,625.55 | — | £21,620.22 | £8,801.34 | £11,447.33 | £11,547.29 | £1,626,788.13 | £954,231.19 | £2,621,748.66 | £1,697,384.49 |
| 2022 | £5,971.32 | £2,337.47 | £6,887.65 | £1,131.75 | £7,886.40 | £4,436.54 | £11,761.71 | £7.48 | £20,105.15 | £6,371.39 | £11,785.07 | £10,370.97 | £1,693,345.62 | £1,065,669.85 | £2,473,547.06 | £1,488,123.58 |
| 2023 | £6,367.23 | £2,113.03 | £6,360.83 | £3,891.56 | £6,449.53 | £3,232.16 | £10,840.28 | £951.63 | £19,356.17 | £7,009.62 | £9,274.92 | £9,990.44 | £1,556,560.50 | £831,541.06 | £2,426,056.82 | £1,427,566.29 |
| 2024 | £4,802.98 | £3,245.92 | £5,274.31 | £4,317.22 | £5,898.12 | £3,712.88 | £11,553.29 | £3,503.81 | £16,545.70 | £9,084.64 | £9,500.16 | £9,190.96 | £1,507,259.29 | £615,557.54 | £2,358,214.99 | £1,320,453.23 |
| 2025 | £4,496.52 | £4,029.13 | £6,127.56 | £3,634.31 | £5,965.37 | £3,010.84 | £9,867.03 | £4,365.25 | £15,480.62 | £7,930.18 | £8,246.08 | £9,103.46 | £1,367,228.00 | £856,669.63 | £2,187,505.37 | £1,366,739.83 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £917.13, range £4.58–£4,218.12.

- C1: cost to serve £274.94, net margin after CTS £2,018.79
- C1_2: cost to serve £244.19, net margin after CTS £5,412.05
- C1g: cost to serve £5.73, net margin after CTS £1,349.51
- C2: cost to serve £329.93, net margin after CTS £3,080.37
- C2_2: cost to serve £175.50, net margin after CTS £5,319.57
- C2g: cost to serve £6.87, net margin after CTS £2,012.33
- C3: cost to serve £219.95, net margin after CTS £2,168.89
- C3g: cost to serve £4.58, net margin after CTS £1,293.95
- C4: cost to serve £439.89, net margin after CTS £2,874.90
- C4g: cost to serve £9.17, net margin after CTS £1,334.80
- C5: cost to serve £839.81, net margin after CTS £11,161.75
- C5_2: cost to serve £292.85, net margin after CTS £6,038.12
- C6: cost to serve £959.77, net margin after CTS £21,475.75
- C7: cost to serve £519.13, net margin after CTS £10,296.15
- C8: cost to serve £505.43, net margin after CTS £11,963.46
- C9: cost to serve £491.72, net margin after CTS £12,216.44
- C_IC1: cost to serve £4,218.12, net margin after CTS £1,870,449.28
- C_IC2: cost to serve £3,718.18, net margin after CTS £906,110.58
- C_IC3: cost to serve £3,218.32, net margin after CTS £1,830,219.41
- C_IC3g: cost to serve £67.07, net margin after CTS £622,579.96
- C_IC4: cost to serve £2,718.52, net margin after CTS £1,103,966.75


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 29 recovery surcharge(s) at renewal based on prior-term losses (3 gas). Avg surcharge: 14.5%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.31/MWh |
| C5 | electricity | 2018-12-31 | £-204.31 | £2,322.51 | +3.8% | £148.68/MWh | £153.39/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,283.71 | £6,187.80 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,215.97 | £10,069.00 | +20.0% | £128.22/MWh | £175.80/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,915.21 | £3,421.95 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £177.17/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.63/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £57.53/MWh |
| C1_2 | electricity | 2021-12-30 | £-149.26 | £1,494.88 | +5.0% | £311.83/MWh | £332.49/MWh |
| C5 | electricity | 2021-12-30 | £-318.19 | £2,722.44 | +6.7% | £311.83/MWh | £353.26/MWh |
| C7 | electricity | 2021-12-30 | £-109.60 | £2,000.74 | +0.5% | £311.83/MWh | £335.19/MWh |
| C_IC3 | electricity | 2021-12-31 | £-26,309.16 | £444,393.58 | +0.9% | £224.03/MWh | £260.00/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £317.95/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.66/MWh |
| C4 | electricity | 2022-09-30 | £-220.41 | £906.59 | +19.3% | £404.86/MWh | £484.82/MWh |
| C4g | gas | 2022-09-30 | £-901.21 | £1,040.11 | +20.0% | £183.79/MWh | £250.54/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £359.29/MWh |
| C8 | electricity | 2023-03-31 | £-481.87 | £3,898.74 | +7.4% | £319.17/MWh | £343.81/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.61/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.46/MWh |
| C4 | electricity | 2023-09-30 | £-277.33 | £1,324.46 | +15.9% | £216.77/MWh | £249.30/MWh |
| C4g | gas | 2023-09-30 | £-1,950.48 | £2,732.11 | +20.0% | £47.83/MWh | £66.00/MWh |
| C1_2 | electricity | 2023-12-30 | £-589.08 | £2,728.19 | +16.6% | £242.22/MWh | £268.29/MWh |
| C5_2 | electricity | 2023-12-30 | £-1,113.67 | £5,051.61 | +17.1% | £242.22/MWh | £269.33/MWh |
| C7 | electricity | 2023-12-30 | £-445.92 | £3,990.91 | +6.2% | £242.22/MWh | £244.32/MWh |
| C_IC3 | electricity | 2023-12-31 | £-108,689.56 | £987,521.89 | +6.0% | £118.95/MWh | £119.79/MWh |
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

- **Retention offers made:** 14
- **Offer acceptance rate:** 100% (14 retained / 0 churned despite offer)
- **Estimated margin protected:** £1,207,026.38
- **No-offer churns:** 6 total (0 blind miss / 0 deliberate pass)
- **Retention coverage rate:** 70% of at-risk renewals received an offer

### 2. Flexibility Revenue Intelligence

- No flexibility revenue data available.

### 3. Churn Pattern Analysis

- **Total lifetime churn events:** 6
- **Peak churn year:** 2020 (2 events)
- **Net book movement:** 3 acquisitions − 6 churns = -3
- **Portfolio trend:** shrinking

### 4. Board Recommendations

1. **Crisis-year churn:** 2 churn events in 2021–2022. Maintain minimum hedge floor pre-crisis to preserve pricing stability and limit bill-shock churn.

## CRM Intelligence: Risk Triage (Final Year)

Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.

| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |
|---------|-----|-----------|-----------|----------|-------------|-----------------|
| C1 | resi | MEDIUM | 22% | 7% | -23.0% [competitive] | £2,018.79 |
| C6 | SME | MEDIUM | 21% | 25% | -24.7% [competitive] | £21,475.75 |
| C_IC3 | I&C | MEDIUM | 20% | 13% | -53.5% [competitive] | £1,830,219.41 |
| C4 | resi | LOW | 14% | 14% | -9.0% | £2,874.90 |
| C2_2 | resi | LOW | 11% | 10% | +17.8% [overpriced] | £5,319.57 |
| C7 | resi | LOW | 11% | 17% | -14.3% | £10,296.15 |
| C9 | resi | LOW | 11% | 14% | -14.3% | £12,216.44 |
| C8 | resi | LOW | 9% | 13% | -23.6% [competitive] | £11,963.46 |
| C1_2 | resi | LOW | 8% | 14% | +3.3% | £5,412.05 |
| C3 | resi | LOW | 6% | 8% | -39.0% [competitive] | £2,168.89 |
| C5_2 | SME | LOW | 5% | 5% | -5.5% | £6,038.12 |
| C5 | SME | LOW | 5% | 5% | -45.8% [competitive] | £11,161.75 |
| C2 | resi | LOW | 5% | 6% | +46.6% [overpriced] | £3,080.37 |
| C_IC1 | I&C | LOW | 4% | 95% | -0.1% | £1,870,449.28 |
| C_IC2 | I&C | LOW | 4% | 95% | +12.4% [overpriced] | £906,110.58 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 0 accounts
- MEDIUM (>=15%): 3 accounts
- LOW (<15%): 12 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £0.00

## Churn Root Cause Attribution

Per-churned-account analysis: pricing journey, rate-vs-SVT positioning, and company vs SIM churn estimate at the point of departure.

| Account | Seg | Churn Date | Tenure | Last Rate Shock | Rate vs SVT | Sim Risk | Co. Est. | Margin Lost |
|---------|-----|------------|--------|-----------------|-------------|----------|----------|-------------|
| C3 | resi | 2020-06-30 | 4.0yr | -4.3% | -39.0% | 6% | 8% | £2,168.89 |
| C1 | resi | 2020-12-30 | 5.0yr | -0.8% | -23.0% | 22% | 7% | £2,018.79 |
| C2 | resi | 2022-03-31 | 6.0yr | +11.9% | +46.6% | 5% | 6% | £3,080.37 |
| C5 | SME | 2022-12-30 | 7.0yr | +5.4% | -45.8% | 5% | 5% | £11,161.75 |
| C6 | SME | 2024-03-30 | 8.0yr | -0.7% | -24.7% | 21% | 25% | £21,475.75 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 14% | 14% | £2,874.90 |

**Root Cause Summary:**
- Total churned accounts: 6
- Lifetime margin lost: £42,780.44
- Average tenure at departure: 6.3 years
- Company-warned churns (co. est. >=20%): 1 -- C6
- Crisis-era churns (2021-22): 2 -- absolute crisis price level, not rate-change delta, was the driver
- Overpriced vs SVT at departure: 1 account(s) -- rate shock risk was observable but unactioned

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 6 accounts that churned without an offer? Calibrated from 14 actual offers (observed retention rate 100%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C3 | resi | 2020-06-30 | 8% | £585.39 | 5% | £29.27 | £556.12 | MISSED OPP. |
| C1 | resi | 2020-12-30 | 7% | £415.17 | 5% | £20.76 | £394.42 | MISSED OPP. |
| C2 | resi | 2022-03-31 | 6% | £236.63 | 5% | £11.83 | £224.80 | MISSED OPP. |
| C5 | SME | 2022-12-30 | 5% | £2,052.65 | 8% | £164.21 | £1,888.44 | MISSED OPP. |
| C6 | SME | 2024-03-30 | 25% | £2,864.67 | 8% | £229.17 | £2,635.50 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 14% | £468.87 | 5% | £23.44 | £445.43 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 6
- Correct no-offer (net-neg ETM): 0
- Missed opportunities (positive ETM, below detection): 6
- Total term margin foregone: £6,623.39
- Total retention cost (counterfactual): £478.69
- Net counterfactual benefit: £6,144.70 (at 100% retention probability)
- Root cause: company churn detection below threshold for all missed cases -- churn model underestimated bill-shock risk

## Pricing Basis Risk Attribution

Forward curve accuracy at each contract term. tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd: positive = company over-estimated costs (higher than market); negative = company under-estimated (margin-at-risk).
Portfolio-wide mean error: +6.0%

| Year | Contracts | Mean Error | Max Abs | Over-priced | Under-priced | Assessment |
|------|-----------|------------|---------|-------------|--------------|------------|
| 2016 | 17 | +8.9% | 29.1% | 9 | 4 | moderate over |
| 2017 | 14 | +5.4% | 46.6% | 8 | 5 | moderate over |
| 2018 | 16 | -2.9% | 27.7% | 6 | 8 | on target |
| 2019 | 19 | +8.3% | 37.2% | 9 | 3 | moderate over |
| 2020 | 22 | -0.9% | 33.8% | 9 | 8 | on target |
| 2021 | 17 | +8.5% | 44.5% | 6 | 3 | moderate over |
| 2022 | 18 | -3.3% | 23.2% | 7 | 6 | on target |
| 2023 | 16 | +20.9% | 40.0% | 11 | 1 | HIGH OVER-PRICE |
| 2024 | 15 | +8.6% | 22.6% | 9 | 1 | moderate over |
| 2025 | 2 | +33.1% | 33.1% | 2 | 0 | HIGH OVER-PRICE |

**Basis Risk Summary:**
- Portfolio mean tariff error: +6.0%
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
| 2021 | £5,211 | £4,342 | 0.30% |
| 2022 | £10,211 | £8,509 | 0.30% |
| 2023 | £6,755 | £5,630 | 0.26% |
| 2024 | £3,200 | £2,667 | 0.15% |
| 2025 | £4,682 | £3,902 | 0.48% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,211 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £524 | £57 | 7.1% |
| 2017 | 14 | £16,735 | £8,803 | £2,260 | 13.5% |
| 2018 | 15 | £29,022 | £17,502 | £6,784 | 23.4% |
| 2019 | 17 | £70,486 | £41,296 | £13,735 | 19.5% |
| 2020 | 19 | £64,388 | £41,674 | £6,767 | 10.5% |
| 2021 | 15 | £115,949 | £51,083 | £5,097 | 4.4% << |
| 2022 | 17 | £202,451 | £61,719 | £19,771 | 9.8% |
| 2023 | 14 | £186,848 | £69,564 | £11,556 | 6.2% |
| 2024 | 14 | £156,210 | £89,610 | £24,405 | 15.6% |
| 2025 | 11 | £88,655 | £47,480 | £11,190 | 12.6% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £24,405 net/customer
**Worst year per customer:** 2016 at £57 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £368 | — | £368 |
| C1_2 | £641 | — | £641 |
| C1g | — | £669 | £669 |
| C2 | £180 | — | £180 |
| C2_2 | £1,557 | — | £1,557 |
| C2g | — | £907 | £907 |
| C3 | £16 | — | £16 |
| C3g | — | £336 | £336 |
| C4 | £193 | — | £193 |
| C4g | — | £-1,625 | £-1,625 * |
| C5 | £-544 | — | £-544 * |
| C5_2 | £380 | — | £380 |
| C6 | £4,226 | — | £4,226 |
| C7 | £-510 | — | £-510 * |
| C8 | £2,330 | — | £2,330 |
| C9 | £2,240 | — | £2,240 |
| C_IC1 | £846,434 | — | £846,434 |
| C_IC2 | £435,815 | — | £435,815 |
| C_IC3 | £144,962 | — | £144,962 |
| C_IC3g | — | £64,511 | £64,511 |
| C_IC4 | £32,221 | — | £32,221 |
| **Total** | **£1,470,509** | **£64,799** | **£1,535,308** |

Loss-making accounts: C4g (£-1,625), C5 (£-544), C7 (£-510)
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
| 2020 | £86,380 | £964,655 | £-878,275 |
| 2021 | £188,629 | £455,365 | £-266,736 |
| 2022 | £199,826 | £1,226,097 | £-1,026,271 |
| 2023 | £374,806 | £1,216,465 | £-841,659 |
| 2024 | £201,264 | £607,649 | £-406,385 |
| 2025 | £66 | £350 | £-283 |
| **Total** | **£1,445,258** | **£5,677,295** | **£-4,232,037** |

Largest hedging cost: **2022** (£1,026,271 vs naked)
Smallest hedging cost: **2025** (£283 vs naked)
Conclusion: systematic forward hedging cost £4,232,037 over 10 years vs spot purchasing.

## Customer Service Quality

Ofgem benchmarks: bill clarity >0.82 (GREEN) / >0.80 (AMBER) / ≤0.80 (RED); complaint probability <5% (GREEN) / <6% (RED); bill shock <0.20% (GREEN) / <0.30% (AMBER) / ≥0.30% (RED).

| Year | Clarity | Complaint% | Shock% | Shock events | Bills | RAG |
|------|---------|------------|--------|--------------|-------|-----|
| 2016 | 0.829 G | 4.7% | 0.20% | 31 | 108 | GREEN |
| 2017 | 0.818 A | 4.7% | 0.17% | 50 | 168 | AMBER |
| 2018 | 0.810 A | 4.7% | 0.16% | 60 | 180 | AMBER |
| 2019 | 0.824 G | 4.7% | 0.17% | 66 | 204 | GREEN |
| 2020 | 0.831 G | 4.3% | 0.14% | 53 | 205 | GREEN |
| 2021 | 0.817 A | 4.8% | 0.24% | 52 | 180 | AMBER |
| 2022 | 0.783 R | 5.8% | 0.34% | 76 | 173 | RED ! |
| 2023 | 0.801 A | 5.0% | 0.30% | 53 | 168 | RED ! |
| 2024 | 0.806 A | 4.8% | 0.17% | 45 | 153 | AMBER |
| 2025 | 0.768 R | 6.1% | 0.25% | 25 | 66 | RED ! |

Worst clarity year: **2025** (0.768)
Highest complaint probability: **2025** (6.1%)
Worst bill shock: **2022** (0.34%)
RED years: 2022, 2023, 2025
AMBER years: 2017, 2018, 2021, 2024
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,434 | £743 |
| 2017 | 2.69 | WATCH | £2,498,375 | £31,640 |
| 2018 | — | — | £2,487,547 | £101,759 |
| 2019 | — | — | £2,611,522 | £233,491 |
| 2020 | — | — | £2,923,332 | £128,571 |
| 2021 | — | — | £2,958,034 | £76,457 |
| 2022 | 2.70 | WATCH | £3,159,446 | £336,112 |
| 2023 | 2.73 | WATCH | £3,395,544 | £161,778 |
| 2024 | — | — | £3,784,369 | £341,665 |
| 2025 | — | — | £3,836,063 | £123,092 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,836,063)**
**Treasury growth: £2,467,434 → £3,836,063 (+£1,368,629)**

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
| C2 | 2022-03 | 6.2% | £237 | below threshold |
| C5 | 2022-12 | 4.8% | £2,053 | below threshold |
| C6 | 2024-03 | 24.6% | £2,865 | below threshold ⚑ |
| C4 | 2024-09 | 14.0% | £469 | below threshold |

**High-risk no-offer events (≥10% churn): 2** — £3,334 margin at risk.

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
| C4 | 2018-10 | £18 | £345 | 18.7× | 3% | retained |
| C1 | 2018-12 | £21 | £379 | 18.0× | 3% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £17,469 | £194,971 | 11.2× | 5% | retained |
| C_IC2 | 2021-03 | £5,311 | £91,315 | 17.2× | 3% | retained |
| C_IC1 | 2021-04 | £8,447 | £158,251 | 18.7× | 3% | retained |
| C5 | 2021-12 | £198 | £2,475 | 12.5× | 3% | retained |
| C_IC3 | 2021-12 | £51,616 | £161,519 | 3.1× | 5% | retained |
| C_IC2 | 2022-04 | £9,418 | £96,241 | 10.2× | 3% | retained |
| C_IC1 | 2022-05 | £18,142 | £231,599 | 12.8× | 3% | retained |
| C6 | 2023-03 | £229 | £3,222 | 14.0× | 3% | retained |

**Total retention spend: £150,010** | **Total margin protected: £1,207,026**
**Portfolio retention ROI: 8.0×** | **Retained: 14/14**
**Best ROI intervention: C3 2017-07 (19.6×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £210,518 | — |
| Exit Gas (with churn risk) | £87,583 | -£122,935 |
| Reprice to Breakeven | £212,143 | +£1,625 |

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
| 2020 | 81.6% | 0.0% | 96.0% | 1 | 14 |
| 2021 | 85.0% | 0.0% | 97.0% | 1 | 14 |
| 2022 | 86.9% | 0.0% | 97.4% | 1 | 13 |
| 2023 | 84.3% | 0.0% | 96.1% | 1 | 13 |
| 2024 | 80.9% | 0.0% | 94.3% | 1 | 10 |
| 2025 | 87.2% | 85.0% | 89.4% | — | 2 |

**Lowest portfolio hedge fraction: 2024 (80.9%)** — risk erosion from regime-change blindness.
**Naked positions first appear in 2019** — unhedged accounts expose portfolio to spot price swings.

> Regime-change blindness: the sim converged toward lower hedging during calm 2016-2020,
> mirroring the strategy that destroyed real UK suppliers entering the 2021-22 crisis.

## Risk Committee Intervention Pattern

Annual risk committee wake-ups (triggered when portfolio VaR exceeds threshold).

| Year | Wake-ups | Customer Adjustments | Avg Customers/Event | Max VaR Stressed £ |
|------|----------|---------------------|--------------------|--------------------|
| 2016 | 13 | 13 | 1.0 | £9 |
| 2017 | 12 | 33 | 2.8 | £401 |
| 2022 | 9 | 59 | 6.6 | £20,607 |
| 2023 | 4 | 36 | 9.0 | £48,915 |

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
| 2021 | 2021-12-31 | 48 | C5 | -£364 |
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
| 2020 | £2,375 | £56,550 | — | £69,454 | £47,213 |
| 2021 | £5,211 | £49,675 | £41,427 | £71,336 | £50,301 |
| 2022 | £10,211 | £36,748 | £99,654 | £71,047 | £54,433 |
| 2023 | £6,755 | £51,053 | £13,776 | £71,831 | £79,700 |
| 2024 | £3,200 | £68,826 | £2,002 | £72,944 | £76,429 |
| 2025 | £4,682 | £31,094 | £855 | £31,221 | £31,816 |

**Peak BSC credit obligation: 2022 (£10,211)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 16 | £196,493 | £105,336 | £11,365 | £12,281 |
| 2017 | 1 | £3,123,605 | £1,874,667 | £846,434 | £3,123,605 |
| 2018 | 1 | £1,525,270 | £909,829 | £435,815 | £1,525,270 |
| 2019 | 2 | £6,470,569 | £2,456,085 | £209,473 | £3,235,285 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £32,221 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,235,285/customer)**
**Best net margin cohort: 2017 (£846,434)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £602 | — | 108 |
| 2017 | +£2,707 | £37,159 | £302 | — | 168 |
| 2018 | +£9,875 | £65,510 | £332 | — | 180 |
| 2019 | +£28,353 | £164,625 | £589 | — | 204 |
| 2020 | +£35,391 | £238,638 | £-60 | — | 205 |
| 2021 | +£15,010 | £246,702 | £618 | — | 180 |
| 2022 | -£49,827 CREDIT | £256,667 | £119 | 2 | 173 |
| 2023 | +£64,889 | £272,368 | £0 | 47 | 168 |
| 2024 | +£110,127 | £308,162 | £0 | 4271 | 153 |
| 2025 | +£47,047 | £136,010 | £0 | — | 66 |

**CfD turned CREDIT in 2022: -£49,827 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2021 (£618)**

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
| 2020 | £5,688 | £1,207 | £4,236 | £704,702 | £75,972 | £791,806 |
| 2021 | £5,790 | £354 | £4,524 | £673,320 | £82,255 | £766,242 |
| 2022 | £4,971 | -£762 | £6,340 | £947,557 | £91,118 | £1,049,224 |
| 2023 | £7,943 | -£575 | £5,789 | £839,225 | £121,515 | £973,897 |
| 2024 | £10,511 | £762 | £5,133 | £1,114,487 | £123,652 | £1,254,545 |
| 2025 | £4,543 | £0 | £1,361 | £462,867 | £53,509 | £522,280 |

**Best gross margin year: 2024 (£1,254,545)** | **Worst: 2016 (£6,814)**
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
| 2020 | 10 | -29.8% | 0/10 | -68.5% | +-17.4% |
| 2021 | 9 | +17.8% | 6/9 | -12.0% | +69.8% |
| 2022 | 9 | -1.2% | 4/9 | -63.2% | +95.7% |
| 2023 | 9 | -29.5% | 0/9 | -60.5% | +-1.7% |
| 2024 | 9 | -18.8% | 1/9 | -53.5% | +3.3% |
| 2025 | 2 | -2.9% | 1/2 | -23.6% | +17.8% |

**Best headroom year: 2020 (avg 29.8% below SVT)**
**Largest above-SVT year: 2021** (6/9 terms above — note: I&C customers exempt from SVT cap)

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
| 2020 | £2,923,332 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,958,034 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,159,446 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,395,544 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,784,369 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,836,063 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 42.1% | £1,181 | £605 | 1.53% |
| 2017 | 14 | 33.1% | £24,902 | £8,914 | 1.80% |
| 2018 | 15 | 41.4% | £40,064 | £17,612 | 1.97% |
| 2019 | 17 | 40.6% | £96,791 | £41,404 | 1.87% |
| 2020 | 19 | 40.4% | £97,742 | £41,769 | 2.06% |
| 2021 | 15 | 29.4% | £161,423 | £51,184 | 1.95% |
| 2022 | 17 | 22.4% | £249,739 | £61,810 | 1.98% |
| 2023 | 14 | 25.3% | £249,697 | £69,660 | 2.20% |
| 2024 | 14 | 39.3% | £214,230 | £89,653 | 2.14% |
| 2025 | 11 | 38.9% | £112,099 | £47,527 | 2.98% |

**Best EBIT%: 2016 (42.1%)** | **Worst EBIT%: 2022 (22.4%)**
**Peak revenue/customer: 2022 (£249,739)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Population Anchoring -- Complaints & Arrears (Phase PS)

SIM aggregate complaint and arrears rates vs published UK benchmarks.
Complaints: Ofgem QoS survey, I&C adjusted (GREEN 2-6%, crisis 2-8%).
Arrears: DESNZ business energy debt (GREEN <8%, crisis <12%).

| Year | Complaint rate% | C.Bench hi | C.RAG | Arrears rate% | A.Bench hi | A.RAG |
|------|-----------------|-----------|-------|---------------|-----------|-------|
| 2016 | 4.70% | 6% | OK | 30.8% | 8% | ! |
| 2017 | 4.67% | 6% | OK | 21.4% | 8% | ! |
| 2018 | 4.66% | 6% | OK | 33.3% | 8% | ! |
| 2019 | 4.67% | 6% | OK | 23.5% | 8% | ! |
| 2020 | 4.29% | 6% | OK | 5.3% | 8% | OK |
| 2021 | 4.80% | 8% | OK | 20.0% | 12% | ! |
| 2022 | 5.81% | 8% | OK | 35.3% | 12% | ! |
| 2023 | 5.05% | 8% | OK | 21.4% | 12% | ! |
| 2024 | 4.82% | 6% | OK | 28.6% | 8% | ! |
| 2025 | 6.07% | 6% | ~ | 9.1% | 8% | ~ |

**Complaints:** 9 of 10 years GREEN (I&C baseline 2-6% normal, 2-8% crisis).
**Arrears:** 1 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).

## Plausibility vs Industry

Key metrics vs UK retail energy norms (Ofgem/Cornwall Insight). OK = within range | ~ = amber | ! = outside expected range.

| Year | Net margin% | Gross margin% | Bad debt% | Churn% |
|------|-------------|---------------|-----------|--------|
| 2016 | !42.1% | !51.2% | OK1.53% | ~0% |
| 2017 | !33.1% | !35.8% | OK1.80% | ~0% |
| 2018 | !41.4% | !44.0% | OK1.97% | ~0% |
| 2019 | !40.6% | !42.8% | OK1.87% | ~0% |
| 2020 | !40.4% | !42.7% | OK2.06% | OK11% |
| 2021 | !29.4% | !31.7% | OK1.95% | ~0% |
| 2022 | !22.4% | ~24.7% | OK1.98% | OK12% |
| 2023 | !25.3% | ~27.9% | OK2.20% | ~0% |
| 2024 | !39.3% | !41.8% | OK2.14% | OK14% |
| 2025 | !38.9% | !42.4% | OK2.98% | ~0% |

**Benchmark ranges:** Net margin %: −5 to +8% green | Gross margin %: 0–20% green | Bad debt %: 0–5% green | Annual churn %: 3–35% green.
**RED — review required: 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025**

## Churn Prediction Calibration

How well the company estimated churn probability versus actual simulation outcomes.

| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |
|----------|------|----------------|-----------------|-------|---------|
| C3 | 2020-06 | 6.5% | 7.6% | +1.1pp | ACCURATE |
| C1 | 2020-12 | 22.3% | 7.3% | -15.0pp | UNDERESTIMATED |
| C2 | 2022-03 | 4.9% | 6.2% | +1.3pp | ACCURATE |
| C5 | 2022-12 | 4.9% | 4.8% | -0.1pp | ACCURATE |
| C6 | 2024-03 | 20.7% | 24.6% | +3.9pp | ACCURATE |
| C4 | 2024-09 | 14.3% | 14.0% | -0.3pp | ACCURATE |

**Outcomes: 1 underestimated / 5 accurate / 0 overestimated**
**Mean absolute error: 3.6pp**
**Systematic bias: company consistently UNDER-predicted churn risk.**

> Company churn estimates derived from company-observable signals (bill shock,
> margin feedback, renewal history) without access to the simulation's internal
> churn parameters — epistemic gap is expected and realistic for a small supplier.

## Counterfactual Retention & Threshold Optimisation

**Current threshold:** 30% | F1=0.000
**Optimal threshold:** 0% | F1=0.176

**RAG [!]:** RED — 4 unrecoverable high-value miss(es) — model underestimates churn: optimal threshold below current

**Missed retention opportunities:** 6 no-offer churns
  Value at stake: £6,623
  Counterfactually recoverable (with offer): 2/6
  Net value recoverable (after offer cost): £552

### Per-miss detail

| Year | Customer | Est | SIM p | Recoverable? | Margin | Net value |
|------|----------|-----|-------|-------------|--------|----------|
| 2020 | C3 | 8% | 6% | No | £585 | £-50 |
| 2020 | C1 | 7% | 22% | Yes | £415 | £365 |
| 2022 | C2 | 6% | 5% | Yes | £237 | £187 |
| 2022 | C5 | 5% | 5% | No | £2,053 | £-50 |
| 2024 | C6 | 25% | 21% | No | £2,865 | £-50 |
| 2024 | C4 | 14% | 14% | No | £469 | £-50 |

### Threshold sensitivity curve

| Threshold | Recall | Precision | F1 |
|-----------|--------|-----------|----|
| 0% | 1.000 | 0.097 | 0.176 ← optimal |
| 5% | 0.833 | 0.093 | 0.167 |
| 10% | 0.333 | 0.065 | 0.108 |
| 15% | 0.167 | 0.077 | 0.105 |
| 20% | 0.167 | 0.100 | 0.125 |
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
| Detection gate (never scored above offer threshold) | 6 | 3% | 12% | 1/6 | £-63 | -0.21 |

## Churn Model Quality (Phase NK)

Company churn model performance: did the company predict churn before it happened?
Threshold: company_churn_estimate > 30% = predicted. Evaluated at each renewal event.

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total churn events | 6 | Customers who actually churned |
| True Positives (TP) | 0 | Churn predicted AND happened |
| False Positives (FP) | 6 | Churn predicted BUT customer renewed |
| False Negatives (FN) | 6 | Churn NOT predicted BUT happened (blind miss) |
| True Negatives (TN) | 50 | No churn predicted AND customer renewed |
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
| Caught before departure (any renewal) | 5 |
| Never flagged | 1 |
| **Episode recall** | **83.3%** |
| Decayed after a prior save | 5 |
| Prevented-churn saves (retention offers that worked) | 14 |

### Per-Year Model Performance

| Year | TP | FP | FN | TN | Recall | Precision |
|------|----|----|----|----|--------|-----------|
| 2016 | 0 | 0 | 0 | 3 | 0% | 0% |
| 2017 | 0 | 0 | 0 | 3 | 0% | 0% |
| 2018 | 0 | 2 | 0 | 2 | 0% | 0% |
| 2019 | 0 | 1 | 0 | 3 | 0% | 0% |
| 2020 | 0 | 0 | 2 | 8 | 0% | 0% |
| 2021 | 0 | 2 | 0 | 7 | 0% | 0% |
| 2022 | 0 | 0 | 2 | 7 | 0% | 0% |
| 2023 | 0 | 1 | 0 | 8 | 0% | 0% |
| 2024 | 0 | 0 | 2 | 7 | 0% | 0% |
| 2025 | 0 | 0 | 0 | 2 | 0% | 0% |

## Credit Risk & Capital Stress (Phase NR)

**Ofgem FRA stress multiplier:** 2.5x (empirical: 2021-22 crisis, industry bad debt 1% → 2.5% revenue)

| Year | Revenue £ | Bad Debt £ | Bad Debt % | Crisis Stress £ |
|------|-----------|------------|------------|-----------------|

**Total bad debt (all years):** £2,501
**Crisis stress incremental:** £3,751

**RAG [OK]:** GREEN — Incremental credit stress below 0.5% revenue — not material

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (11 active customers) under 12-month forward scenarios.
Generated: 2026-07-08T02:04:09Z

Closes CLAUDE.md known failure: regime-change blindness — board can now ask 'what if 2021-22 happened again?'

| Scenario | Elec Fwd (£/MWh) | Gas Fwd (£/MWh) | Hedge Rec | Renewing | Exposure Delta |
|----------|------------------|-----------------|-----------|----------|----------------|
| Base | 86.7 | 55.1 | INCREASE | 0 | — |
| Bull | 56.1 | 35.7 | INCREASE | 0 | £-398,252 |
| Bear | 147.9 | 93.8 | INCREASE | 0 | +£796,504 |
| Crisis | 217.3 | 110.2 | INCREASE | 0 | +£1,562,206 |

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
| 2021 | 17 | 14.5% | 44.5% | MODERATE |
| 2022 | 18 | 12.4% | 23.2% | MODERATE |
| 2023 | 16 | 22.3% | 40.0% | POOR |
| 2024 | 15 | 10.8% | 22.6% | MODERATE |
| 2025 | 2 | 33.1% | 33.1% | POOR |

**Best accuracy year (n≥5): 2024 (10.8% mean error)**
**Worst accuracy year (n≥5): 2023 (22.3% mean error)**

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
| 2020 | 17 | +3.6 | 8 | 9 | 2 |
| 2021 | 14 | +13.5 | 14 | 0 | 7 |
| 2022 | 13 | +19.3 | 12 | 1 | 5 |
| 2023 | 13 | +6.0 | 8 | 5 | 9 |
| 2024 | 12 | +5.3 | 6 | 6 | 2 |
| 2025 | 2 | +4.8 | 2 | 0 | 0 |

**Total adjustments 2016-2025: 117** | **Peak avg adjustment: 2022 (+19.3 £/MWh)**
**Emergency reprices: 29 total** (9 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £31,307 | £10,436 | — |
| 2017 | 9 | £105,616 | £11,735 | +£74,309 |
| 2018 | 10 | £2,931,339 | £293,134 | +£2,825,722 |
| 2019 | 11 | £4,550,605 | £413,691 | +£1,619,266 |
| 2020 | 14 | £7,172,357 | £512,311 | +£2,621,752 |
| 2021 | 14 | £6,993,775 | £499,555 | £-178,582 |
| 2022 | 16 | £6,809,739 | £425,609 | £-184,036 |
| 2023 | 16 | £6,327,562 | £395,473 | £-482,177 |
| 2024 | 16 | £5,888,115 | £368,007 | £-439,447 |
| 2025 | 16 | £5,860,399 | £366,275 | £-27,716 |

**Peak portfolio CLV: 2020 (£7,172,357)** | **Earliest/lowest: 2016 (£31,307)**
**Largest YoY gain: 2018 (+£2,825,722)**
**Largest YoY fall: 2023 (£-482,177)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | 51.2% | — | — | — | — |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | 35.8% | +£333,275.90 | +£107,460.46 | +£108,889.99 | +£116,925.46 |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | 44.0% | +£252,322.49 | +£61,745.30 | +£51,194.57 | +£139,382.63 |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | 42.8% | +£1,044,499.09 | +£323,437.66 | +£281,360.24 | +£439,701.19 |
| 2020 | £1,857,096.31 | £431,628.21 | £631,861.95 | £793,606.15 | 42.7% | +£211,644.21 | £-64,611.74 | +£186,524.91 | +£89,731.04 |
| 2021 | £2,421,344.01 | £973,152.05 | £680,438.97 | £767,752.99 | 31.7% | +£564,247.70 | +£541,523.84 | +£48,577.02 | £-25,853.16 |
| 2022 | £4,245,565.53 | £2,392,501.35 | £802,298.72 | £1,050,765.46 | 24.7% | +£1,824,221.52 | +£1,419,349.30 | +£121,859.75 | +£283,012.47 |
| 2023 | £3,495,761.69 | £1,642,210.96 | £878,317.42 | £975,233.31 | 27.9% | £-749,803.83 | £-750,290.38 | +£76,018.70 | £-75,532.15 |
| 2024 | £2,999,221.95 | £933,180.92 | £810,905.76 | £1,255,135.26 | 41.8% | £-496,539.75 | £-709,030.04 | £-67,411.66 | +£279,901.95 |
| 2025 | £1,233,083.98 | £452,920.26 | £257,370.51 | £522,793.21 | 42.4% | £-1,766,137.97 | £-480,260.67 | £-553,535.25 | £-732,342.05 |

**Best GM year: 2016 (51.2%)** | **Worst GM year: 2022 (24.7%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Net Margin Bridge (Year-on-Year Attribution)

Decomposes each year's net margin change into: gross margin movement, bad debt, capital costs, policy levies, network costs.

| Transition | Net Δ | Gross Δ | Bad Debt Δ | Capital Δ | Policy Δ | Network Δ | Portfolio | Driver | RAG |
|-----------|-------|---------|-----------|---------|---------|---------|---------|--------|-----|
| 2016→2017 | +£30,897 | +£116,423 | +£300 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£70,119 | +£139,295 | -£31 | -£255 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£131,733 | +£439,496 | -£256 | -£781 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£104,920 | +£89,778 | +£648 | +£344 | -£162,663 | -£33,027 | +2 | policy levies | RED |
| 2020→2021 | -£52,115 | -£25,564 | -£677 | -£3,670 | -£19,932 | -£2,271 | -4 | gross margin | RED |
| 2021→2022 | +£259,655 | +£282,982 | +£499 | -£7,660 | -£1,107 | -£15,058 | +2 | gross margin | GREEN |
| 2022→2023 | -£174,334 | -£75,327 | +£119 | +£3,156 | -£70,820 | -£31,462 | -3 | gross margin | RED |
| 2023→2024 | +£179,887 | +£280,648 | +£0 | +£639 | -£100,877 | -£522 | +0 | gross margin | GREEN |
| 2024→2025 | -£218,573 | -£732,265 | +£0 | +£3,803 | +£382,565 | +£127,323 | -3 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£218,573)** | **Best transition: 2021→2022 (+£259,655)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Payment Portfolio Health (P2: Billing Infra)

Year-by-year bad debt rate and high-churn-risk customer concentration.

| Year | Bad Debt | Bad Debt Rate | At-Risk Customers | At-Risk % | Trend | RAG |
|------|----------|--------------|-----------------|----------|-------|-----|
| 2016 | £602 | 5.78% | 0/5 | 0% | — STABLE | RED |
| 2017 | £302 | 0.13% | 0/12 | 0% | ↓ IMPROVING | GREEN |
| 2018 | £332 | 0.08% | 1/13 | 8% | ↓ IMPROVING | GREEN |
| 2019 | £589 | 0.05% | 3/14 | 21% | ↓ IMPROVING | GREEN |
| 2020 | £-60 | -0.00% | 5/16 | 31% | ↓ IMPROVING | AMBER |
| 2021 | £618 | 0.04% | 4/14 | 29% | ↑ DETERIORATING | GREEN |
| 2022 | £119 | 0.00% | 10/14 | 71% | ↓ IMPROVING | RED |
| 2023 | £0 | 0.00% | 9/12 | 75% | ↓ IMPROVING | RED |
| 2024 | £0 | 0.00% | 3/12 | 25% | — STABLE | GREEN |
| 2025 | £0 | 0.00% | 2/3 | 67% | ↓ IMPROVING | RED |

**Worst bad debt year: 2016 (5.78%)** | **Peak at-risk concentration: 2023 (75% of customers)**

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
| 2021 | 1% | 1% | 99% | 89% | 11% | I&C | RED |
| 2022 | 0% | 1% | 99% | 91% | 9% | I&C | RED |
| 2023 | 1% | 1% | 99% | 88% | 12% | I&C | RED |
| 2024 | 1% | 0% | 99% | 90% | 10% | I&C | RED |
| 2025 | 1% | 0% | 99% | 90% | 10% | I&C | RED |

> **Concentration alert:** I&C dominated gross margin in 2017–2025. Loss of a single large I&C customer has outsized P&L impact. Benchmark: a resilient mixed-book supplier targets no segment >70% of gross margin.

## Shadow Retention Strategy (P4: Shadow Ops)

Counterfactual: what if the company had offered retention to ALL renewal customers (not just those above the 30% threshold)?
Shadow discount: 8% off next term. Assumes P(accept) = (1 - churn\_estimate) x 90%.

| Year | No-Offer Churns | Margin Lost | Shadow Retained | Offer Cost | Shadow Net Gain |
|------|----------------|------------|----------------|-----------|----------------|
| 2020 | 2 | £1,001 | £766 | £67 | +£700 |
| 2022 | 2 | £2,289 | £1,801 | £157 | +£1,645 |
| 2024 | 2 | £3,334 | £2,122 | £185 | +£1,937 |

**Total opportunity cost vs actual: +£4,282 net** (gross £6,623 margin lost; £408 offer cost if all retained).

> The shadow strategy net gain is small because all no-offer churns were residential customers with low margins. I&C customers (large margins) already received retention offers — the current threshold strategy is near-optimal for the existing portfolio composition.

## Ofgem FRA Regulatory Capital Ratio (Phase NZ)

Equity / (annual revenue ÷ 12). Ofgem FRA minimum: ≥ 1x monthly revenue.
Sector best practice: ≥ 6x (GREEN). Early warning: < 3x (AMBER). Non-compliant: < 1x (RED).
Real-world context: Bulb 2021 collapse at ~-0.01x; Igloo 2021 ~0.07x.

| Year | Equity | Monthly Rev | FRA Ratio | RAG | Compliant |
|------|--------|-------------|-----------|-----|-----------|
| 2016 | £2,473,105.03 | £1,279.55 | 1932.8x | ✓ GREEN | Yes |
| 2017 | £2,588,632.95 | £29,052.54 | 89.1x | ✓ GREEN | Yes |
| 2018 | £2,837,226.69 | £50,079.42 | 56.6x | ✓ GREEN | Yes |
| 2019 | £3,505,306.75 | £137,121.01 | 25.6x | ✓ GREEN | Yes |
| 2020 | £4,255,309.40 | £154,758.03 | 27.5x | ✓ GREEN | Yes |
| 2021 | £4,967,070.44 | £201,778.67 | 24.6x | ✓ GREEN | Yes |
| 2022 | £5,917,106.46 | £353,797.13 | 16.7x | ✓ GREEN | Yes |
| 2023 | £6,802,167.58 | £291,313.47 | 23.4x | ✓ GREEN | Yes |
| 2024 | £7,980,090.83 | £249,935.16 | 31.9x | ✓ GREEN | Yes |
| 2025 | £8,459,158.04 | £102,757.00 | 82.3x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.7x (equity £5,917,106.46 vs monthly revenue £353,797.13). RAG: GREEN.
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
| 2020 | £1,857,096.31 | £690,220.80 | £5,866.88 | ✓ GREEN |  |
| 2021 | £2,421,344.01 | £899,932.86 | £7,649.43 | ✓ GREEN | CREDIT EXPECTED |
| 2022 | £4,245,565.53 | £1,577,935.19 | £13,412.45 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,495,761.69 | £1,299,258.10 | £11,043.69 | ✓ GREEN |  |
| 2024 | £2,999,221.95 | £1,114,710.82 | £9,475.04 | ✓ GREEN |  |
| 2025 | £1,233,083.98 | £458,296.21 | £3,895.52 | ✓ GREEN |  |

**Peak reconciliation exposure:** 2022 — max adverse £13,412 (4.5 months weighted tail).

_Note: Outstanding pool ≈ current-year revenue × (weighted outstanding months ÷ 12)._
_Max adverse = pool × blended variance rate (0.5% HH + 4% non-HH, portfolio-weighted)._
## Ofgem Supply Licence Health (Phase OC)

Annual licence health checks: customer base, net assets, liquidity, bad debt.
Breach triggers board escalation and Ofgem notification under SLC 0.
WATCH = within 20% of threshold. BREACH = threshold crossed.

| Year | Customers | Net Assets | Treasury | Cash Wks | Bad Debt % | Overall |
|------|-----------|------------|----------|----------|------------|---------|
| 2016 | 13 | £2,473,105.03 | £2,467,433.90 | 35675w | 5.78% | ✗ BREACH |
| 2017 | 14 | £2,588,632.95 | £2,498,375.34 | 1170w | 0.13% | ✗ BREACH |
| 2018 | 15 | £2,837,226.69 | £2,487,546.78 | 749w | 0.08% | ✗ BREACH |
| 2019 | 17 | £3,505,306.75 | £2,611,521.98 | 274w | 0.05% | ✗ BREACH |
| 2020 | 19 | £4,255,309.40 | £2,923,331.74 | 352w | -0.00% | ✗ BREACH |
| 2021 | 15 | £4,967,070.44 | £2,958,034.42 | 158w | 0.04% | ✗ BREACH |
| 2022 | 17 | £5,917,106.46 | £3,159,445.73 | 69w | 0.00% | ✗ BREACH |
| 2023 | 14 | £6,802,167.58 | £3,395,543.83 | 108w | 0.00% | ✗ BREACH |
| 2024 | 14 | £7,980,090.83 | £3,784,369.41 | 211w | 0.00% | ✗ BREACH |
| 2025 | 11 | £8,459,158.04 | £3,836,062.59 | 440w | 0.00% | ✗ BREACH |

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
| 2021 | Yes | 15/15/15 | 9.6 | 6.0 | £41 |
| 2022 | Yes | 17/17/17 | 19.0 | 11.8 | £7 |
| 2023 | Yes | 14/14/14 | 15.5 | 5.9 | £0 |
| 2024 | Yes | 14/14/14 | 12.8 | 5.4 | £0 |
| 2025 | Yes | 11/11/11 | 5.6 | 2.6 | £0 |

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
| 2020 | 10,111.8 | 0.358 ROC/MWh | 3,620.0 | £48.78 | £176,585 |
| 2021 | 10,006.6 | 0.364 ROC/MWh | 3,642.4 | £50.80 | £185,034 |
| 2022 | 9,965.4 | 0.370 ROC/MWh | 3,687.2 | £52.88 | £194,979 |
| 2023 | 9,982.9 | 0.376 ROC/MWh | 3,753.6 | £54.35 | £204,007 |
| 2024 | 10,011.6 | 0.382 ROC/MWh | 3,824.4 | £56.19 | £214,895 |
| 2025 | 4,277.0 | 0.389 ROC/MWh | 1,663.8 | £58.10 | £96,664 |
| **Total** | **66,686.1** | | | | **£1,270,805** |

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
| 2020 | 10,111.8 | GBP0.00 (scheme closed) | NIL |
| 2021 | 10,006.6 | GBP0.00 (scheme closed) | NIL |
| 2022 | 9,965.4 | GBP0.00 (scheme closed) | NIL |
| 2023 | 9,982.9 | GBP0.00 (scheme closed) | NIL |
| 2024 | 10,011.6 | GBP0.00 (scheme closed) | NIL |
| 2025 | 4,277.0 | GBP0.00 (scheme closed) | NIL |
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
| 2021 | 10 | 150,000 | OK (exempt) | N/A | NIL |
| 2022 | 12 | 150,000 | OK (exempt) | N/A | NIL |
| 2023 | 9 | 150,000 | OK (exempt) | N/A | NIL |
| 2024 | 9 | 150,000 | OK (exempt) | N/A | NIL |
| 2025 | 6 | 150,000 | OK (exempt) | N/A | NIL |

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
| 2021 | ECO3 | GBP4.50 | 10 | OK (exempt) | GBP73 |
| 2022 | ECO4 | GBP6.80 | 12 | OK (exempt) | GBP192 |
| 2023 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP158 |
| 2024 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP136 |
| 2025 | ECO4 | GBP6.80 | 6 | OK (exempt) | GBP56 |

Counterfactual total 2016-2025 (if 150k domestic): **GBP745**

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
| 2025 | 8 | 175g/kWh | 1.4 | 1 | 0.2 | 1.6 | 68% (decarbonising) |
| **Total** | | | | | | **30.6 t** | |

> Grid emission intensity declining: 2016 ~290g/kWh -> 2025 ~175g/kWh (40% reduction). Carbon disclosure per SECR/ESOS.
## Risk Committee Activity (2016-2025)

Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.

| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |
|------|----------|----------------------|----------------------|-----------------|
| 2016 | 13 | £28 | £9 | 1 |
| 2017 | 12 | £1,005 | £401 | 3 |
| 2022 | 9 | £55,609 | £20,607 | 7 |
| 2023 | 4 | £128,380 | £48,915 | 10 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £128,380 | Unique accounts ever adjusted: 11

**Most frequently adjusted accounts:**
- C1: 22 sessions
- C5: 16 sessions
- C7: 16 sessions
- C2: 13 sessions
- C6: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £12,429.21 | Median churn: 32% | Total portfolio CLV: £8,914,856.36

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC1 | £1,996,084.25 | 29% | 20.2 periods |
| C_IC4 | £1,857,486.62 | 20% | 19.3 periods |
| C6 | £22,762.61 | 29% | 19.8 periods |
| C9 | £12,429.21 | 26% | 25.9 periods |

Quadrant CLV: £3,888,762.69 (44% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £3,815,089.31 | 41% | 28.4 periods |
| C_IC2 | £1,150,855.11 | 32% | 23.1 periods |
| C5 | £14,695.51 | 38% | 26.7 periods |

Quadrant CLV: £4,980,639.93 (56% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C7 | £9,626.07 | 29% | 19.3 periods |
| C3 | £7,081.97 | 11% | 17.9 periods |

Quadrant CLV: £16,708.04 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £11,195.14 | 32% | 19.4 periods |
| C2 | £7,607.67 | 38% | 23.8 periods |
| C1 | £5,684.57 | 38% | 19.5 periods |
| C4 | £4,258.34 | 38% | 17.4 periods |

Quadrant CLV: £28,745.71 (0% of portfolio)

**Board action: CRITICAL quadrant has 3 account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**

## Customer Experience & Service Quality

| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |
|------|----------------|---------------|-------------|---------|------|
| 2016 | 0.829 | 0.047 | 0 | 0 |  |
| 2017 | 0.818 | 0.047 | 0 | 0 |  |
| 2018 | 0.810 | 0.047 | 0 | 0 |  |
| 2019 | 0.824 | 0.047 | 0 | 0 |  |
| 2020 | 0.831 | 0.043 | 1 | 0 |  |
| 2021 | 0.817 | 0.048 | 0 | 0 |  |
| 2022 | 0.783 | 0.058 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.801 | 0.050 | 0 | 0 |  |
| 2024 | 0.806 | 0.048 | 2 | 0 |  |
| 2025 | 0.768 | 0.061 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.3% | **Average billing clarity:** 0.811 | **Average complaint probability:** 0.049

**Acquisition performance:** 3 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

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
| 2020 | 14.4% | 53 | 205 | 26% |  |
| 2021 | 23.6% | 52 | 180 | 29% | ELEVATED |
| 2022 | 33.9% | 76 | 173 | 44% | **HIGH** |
| 2023 | 30.1% | 53 | 168 | 32% | **HIGH** |
| 2024 | 17.0% | 45 | 153 | 29% |  |
| 2025 | 24.7% | 25 | 66 | 38% | ELEVATED |

**Crisis peak: 2022** — 33.9% average shock. Energy crisis drove wholesale costs above locked tariff rates,
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
| 2020 | £238,638.15 | £35,391.25 | £69,454.47 | £56,550.37 | £70,024.25 | £470,058.49 | £124,589.13 |
| 2021 | £246,701.82 | £15,009.92 | £71,336.24 | £49,674.92 | £62,836.38 | £486,986.67 | £123,772.40 |
| 2022 | £256,667.15 | **£-49,827.22** | £71,047.02 | £36,748.27 | £69,230.82 | £483,520.48 | £134,698.46 |
| 2023 | £272,367.84 | £64,888.73 | £71,830.95 | £51,052.83 | £75,239.96 | £549,156.68 | £140,893.74 |
| 2024 | £308,161.53 | £110,127.47 | £72,943.93 | £68,825.93 | £82,706.97 | £644,768.14 | £144,687.24 |
| 2025 | £136,009.92 | £47,047.46 | £31,221.29 | £31,094.09 | £36,226.54 | £282,454.70 | £61,976.68 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.01 (2016) → £282,454.70 (2025). CAGR: 76.5%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £418.71 | £324.29 | £9,021.95 | £1,388.28 | 13.3% | YES |
| 2017 | £31,123.28 | £516.54 | £231,632.96 | £2,660.42 | 1.1% | YES |
| 2018 | £101,321.76 | £436.94 | £432,208.83 | £3,113.94 | 0.7% | YES |
| 2019 | £223,001.61 | £10,489.65 | £1,060,498.38 | £137,766.14 | 11.5% | YES |
| 2020 | £118,083.28 | £10,488.12 | £1,102,256.74 | £121,119.88 | 9.9% | YES |
| 2021 | £66,633.50 | £9,823.20 | £1,441,837.83 | £297,399.17 | 17.1% | YES |
| 2022 | £327,268.47 | £8,843.70 | £2,853,337.99 | £588,329.77 | 17.1% | YES |
| 2023 | £152,818.87 | £8,958.96 | £2,318,669.69 | £297,197.78 | 11.4% | YES |
| 2024 | £331,197.71 | £10,467.35 | £1,916,445.67 | £270,490.62 | 12.4% | YES |
| 2025 | £118,642.02 | £4,449.79 | £842,746.26 | £132,453.71 | 13.6% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £210,517.97 | — | Current strategy |
| EXIT_GAS | £87,583.16 | £-122,934.81 | Remove gas; model elec churn risk |
| REPRICE_GAS | £212,143.10 | £1,625.13 | Raise gas tariff to break-even |

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
| I&C electricity | £5,724,619.17 | £50,103.96 | £1,459,431.37 | 29.1x | Strong |
| I&C gas | £622,647.03 | £0.00 | £64,510.98 | 0.0x | Low return |
| SME electricity | £40,768.05 | £484.47 | £4,061.52 | 8.4x | Moderate |
| resi electricity | £58,551.31 | £646.88 | £7,016.32 | 10.8x | Moderate |
| resi gas | £6,016.94 | £197.67 | £287.56 | 1.5x | Low return |

## Portfolio Concentration Risk

Revenue concentration analysis across 21 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2241** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,333,325.99 (98.4% of total positive margin)
- resi: £61,341.21 (1.0% of total positive margin)
- SME: £38,675.61 (0.6% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,870,449.28 | 29.1% | 4% | £75,379.11 |
| C_IC3 | I&C | £1,830,219.41 | 28.4% | 20% | £371,351.52 |
| C_IC4 | I&C | £1,103,966.75 | 17.2% | 0% | £0.00 |
| C_IC2 | I&C | £906,110.58 | 14.1% | 4% | £33,254.26 |
| C_IC3g | I&C | £622,579.96 | 9.7% | 0% | £0.00 |

**Concentration Risk Warning:**
- I&C segment accounts for 98.4% of total portfolio margin
- Resi and SME segments are effectively margin-neutral at portfolio scale
- A single large I&C departure would remove 14-29% of all margin
- Board action: diversify acquisition pipeline toward profitable resi/SME to reduce I&C dependency

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 117 renewal(s) (25 gas) based on recent portfolio-wide margin rates: 63 surcharge(s), 54 discount(s).

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
| C7 | electricity | 2020-12-30 | -4.7% | +6.3% | £133.55/MWh | £142.02/MWh |
| C_IC3 | electricity | 2020-12-31 | -5.8% | +6.9% | £50.65/MWh | £54.14/MWh |
| C_IC3g | gas | 2020-12-31 | 14.7% | -3.3% | £20.05/MWh | £19.38/MWh |
| C2 | electricity | 2021-03-31 | -20.6% | +14.3% | £175.90/MWh | £201.03/MWh |
| C2g | gas | 2021-03-31 | 7.2% | +0.4% | £36.20/MWh | £36.34/MWh |
| C6 | electricity | 2021-03-31 | -16.1% | +12.0% | £175.90/MWh | £197.06/MWh |
| C8 | electricity | 2021-03-31 | -11.9% | +9.9% | £175.90/MWh | £193.40/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.6% | +6.3% | £138.90/MWh | £147.64/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.9% | +3.6% | £113.97/MWh | £118.02/MWh |
| C9 | electricity | 2021-06-30 | 1.1% | +3.5% | £170.38/MWh | £176.29/MWh |
| C4 | electricity | 2021-09-30 | -2.4% | +5.2% | £205.15/MWh | £215.85/MWh |
| C4g | gas | 2021-09-30 | 6.8% | +0.6% | £53.99/MWh | £54.31/MWh |
| C1_2 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.70/MWh |
| C5 | electricity | 2021-12-30 | -4.4% | +6.2% | £311.83/MWh | £331.12/MWh |
| C7 | electricity | 2021-12-30 | -6.0% | +7.0% | £311.83/MWh | £333.59/MWh |
| C_IC3 | electricity | 2021-12-31 | -24.4% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -22.1% | +15.0% | £109.48/MWh | £125.90/MWh |
| C2 | electricity | 2022-03-31 | -15.8% | +11.9% | £361.95/MWh | £405.05/MWh |
| C6 | electricity | 2022-03-31 | -16.9% | +12.4% | £361.95/MWh | £406.99/MWh |
| C8 | electricity | 2022-03-31 | 5.1% | +1.5% | £361.95/MWh | £367.26/MWh |
| C_IC2 | electricity | 2022-04-30 | -10.3% | +9.2% | £269.81/MWh | £294.53/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.9% | +7.4% | £239.42/MWh | £257.21/MWh |
| C9 | electricity | 2022-06-30 | 4.4% | +1.8% | £255.09/MWh | £259.70/MWh |
| C4 | electricity | 2022-09-30 | 7.3% | +0.4% | £404.86/MWh | £406.35/MWh |
| C4g | gas | 2022-09-30 | -19.2% | +13.6% | £183.79/MWh | £208.78/MWh |
| C1_2 | electricity | 2022-12-30 | 9.0% | -0.5% | £266.73/MWh | £265.45/MWh |
| C5 | electricity | 2022-12-30 | -2.8% | +5.4% | £266.73/MWh | £281.17/MWh |
| C7 | electricity | 2022-12-30 | -16.5% | +12.2% | £266.73/MWh | £299.40/MWh |
| C_IC3 | electricity | 2022-12-31 | -18.9% | +13.5% | £168.36/MWh | £191.03/MWh |
| C_IC3g | gas | 2022-12-31 | -37.8% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -10.9% | +9.4% | £319.17/MWh | £349.30/MWh |
| C6 | electricity | 2023-03-31 | 0.2% | +3.9% | £319.17/MWh | £331.64/MWh |
| C8 | electricity | 2023-03-31 | 7.3% | +0.3% | £319.17/MWh | £320.24/MWh |
| C_IC2 | electricity | 2023-05-30 | -22.1% | +15.0% | £171.46/MWh | £197.18/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.2% | +12.6% | £163.19/MWh | £183.71/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.09/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.02/MWh |
| C4g | gas | 2023-09-30 | -38.6% | +15.0% | £47.83/MWh | £55.00/MWh |
| C1_2 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C5_2 | electricity | 2023-12-30 | 26.3% | -5.0% | £242.22/MWh | £230.11/MWh |
| C7 | electricity | 2023-12-30 | 24.4% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 23.6% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -10.0% | +9.0% | £51.89/MWh | £56.57/MWh |
| C2_2 | electricity | 2024-03-30 | 14.0% | -3.0% | £207.71/MWh | £201.48/MWh |
| C6 | electricity | 2024-03-30 | 9.3% | -0.7% | £207.71/MWh | £206.31/MWh |
| C8 | electricity | 2024-03-30 | 9.3% | -0.7% | £207.71/MWh | £206.31/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.0% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.5% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C1_2 | electricity | 2024-12-29 | 0.4% | +3.8% | £243.79/MWh | £253.01/MWh |
| C5_2 | electricity | 2024-12-29 | 22.6% | -5.0% | £243.79/MWh | £231.60/MWh |
| C7 | electricity | 2024-12-29 | 16.1% | -4.0% | £243.79/MWh | £233.94/MWh |
| C_IC3 | electricity | 2024-12-30 | 12.3% | -2.1% | £116.37/MWh | £113.88/MWh |
| C_IC3g | gas | 2024-12-30 | -9.4% | +8.7% | £50.47/MWh | £54.85/MWh |
| C2_2 | electricity | 2025-03-30 | 2.5% | +2.8% | £284.89/MWh | £292.73/MWh |
| C8 | electricity | 2025-03-30 | 6.8% | +0.6% | £284.89/MWh | £286.63/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **6** | Blind misses: **6** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 0 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £6,623.39 | deliberate: £0.00 | total: £6,623.39

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.08 | 0.06 | No | £585.39 |
| C1 | 2020-12-30 | Blind miss | 0.07 | 0.22 | No | £415.17 |
| C2 | 2022-03-31 | Blind miss | 0.06 | 0.05 | No | £236.63 |
| C5 | 2022-12-30 | Blind miss | 0.05 | 0.05 | No | £2,052.65 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.21 | No | £2,864.67 |
| C4 | 2024-09-29 | Blind miss | 0.14 | 0.14 | No | £468.87 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £144,961.91 | £64,510.98 | £209,472.89 | Yes |
| C2+C2g | £179.69 | £907.09 | £1,086.77 | Yes |
| C1+C1g | £368.25 | £669.14 | £1,037.38 | Yes |
| C3+C3g | £16.48 | £336.46 | £352.95 | Yes |
| C4+C4g | £193.11 | £-1,625.13 | £-1,432.02 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £64,798.54.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,535,307.74 across 21 billing accounts. Revenue: £14,060,576.00.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,123,605.33 | £1,874,667.40 | £18,414.27 | £846,433.53 | 27.1% |
| 2 | C_IC2 | fixed | £1,525,269.53 | £909,828.76 | £8,527.56 | £435,815.28 | 28.6% |
| 3 | C_IC3 | pass_through | £4,637,989.59 | £1,833,437.73 | £23,162.13 | £144,961.91 | 3.1% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £64,510.98 | 3.5% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £32,220.65 | 1.2% |
| 6 | C6 | fixed | £38,922.12 | £22,435.52 | £264.20 | £4,225.70 | 10.9% |
| 7 | C8 | fixed | £21,688.78 | £12,468.89 | £134.91 | £2,330.30 | 10.7% |
| 8 | C9 | fixed | £20,243.67 | £12,708.16 | £131.43 | £2,239.91 | 11.1% |
| 9 | C2_2 | fixed | £10,303.18 | £5,495.07 | £67.91 | £1,556.91 | 15.1% |
| 10 | C2g | fixed | £3,849.77 | £2,019.21 | £21.85 | £907.09 | 23.6% |
| 11 | C1g | fixed | £2,436.42 | £1,355.24 | £15.79 | £669.14 | 27.5% |
| 12 | C1_2 | fixed | £11,623.13 | £5,656.25 | £81.60 | £641.46 | 5.5% |
| 13 | C5_2 | fixed | £12,351.94 | £6,330.97 | £86.34 | £380.12 | 3.1% |
| 14 | C1 | fixed | £3,497.52 | £2,293.73 | £14.09 | £368.25 | 10.5% |
| 15 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £336.46 | 12.5% |
| 16 | C4 | fixed | £6,274.43 | £3,314.79 | £37.48 | £193.11 | 3.1% |
| 17 | C2 | fixed | £5,114.40 | £3,410.31 | £24.74 | £179.69 | 3.5% |
| 18 | C3 | fixed | £3,628.72 | £2,388.84 | £14.77 | £16.48 | 0.5% |
| 19 | C7 | fixed | £21,792.85 | £10,815.29 | £139.94 | £-509.79 | -2.3% |
| 20 | C5 | fixed | £21,712.25 | £12,001.55 | £133.94 | £-544.30 | -2.5% |
| 21 | C4g | fixed | £10,370.30 | £1,343.97 | £144.75 | £-1,625.13 | -15.7% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,060,576 | 100.0% |
| Wholesale cost | -£7,607,974 | 54.1% |
| **Gross supply margin** | **£6,452,602** | **45.9%** |
| Policy + Network costs | -£4,865,862 | 34.6% |
| Capital cost | -£51,433 | 0.4% |
| **Net supply margin** | **£1,535,308** | **10.9%** |

> *The ledger's `net_margin_gbp` (£6,415,876) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,031,503 | 47.6% | 12.1% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 3.5% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £60,634 | 56.8% | 6.1% | CMA 3-8% | ✓ |
| resi/elec | £82,240 | 57.6% | 5.9% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £19,340 | 31.1% | 1.5% | Ofgem CMA 2-4% | ✓ |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: PASS** — all segments within benchmarks.
## Transaction Log

Total events: 3,535,776

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 3 |
| bad_debt_event | 1,605 |
| billing_event | 1,605 |
| capital_charge_event | 1,705,599 |
| cost_to_serve_event | 114 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,605 |
| payment_received_event | 1,605 |
| settlement_event | 1,821,921 |
| vat_remittance_event | 1,605 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £19,819,620.93 |
|   Less: VAT remitted to HMRC | (£957,157.22) |
| = Revenue (ex-VAT) | £18,862,463.71 |
| Less: non-commodity pass-through | (£4,787,181.64) |
| Wholesale cost (settlement events) | (£7,607,973.51) |
| Gross margin | £6,467,308.57 |
| Capital charges | (£51,432.98) |
| Net margin | £6,415,875.59 |

_Cash reconciliation: of £19,819,620.93 billed, bad debt of £396,515.59 was written off, leaving £19,423,105.34 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £6,976,517.22._

| Acquisition spend | (£562.50) |
| Fixed overhead | (£5,700.00) |
| Cost to serve | (£19,259.69) |
| Operating net margin | £6,390,353.40 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | £234.62 | £1,310.70 | £6,468.81 (42.1%) |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | £6,260.72 | £7,990.17 | £115,527.91 (33.1%) |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | £11,823.00 | £14,052.12 | £248,593.75 (41.4%) |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | £30,746.61 | £33,485.76 | £668,080.05 (40.6%) |
| 2020 | £1,857,096.31 | £431,628.21 | £631,861.95 | £793,606.15 | £38,269.56 | £41,638.03 | £750,002.65 (40.4%) |
| 2021 | £2,421,344.01 | £973,152.05 | £680,438.97 | £767,752.99 | £47,173.73 | £50,356.00 | £711,761.04 (29.4%) |
| 2022 | £4,245,565.53 | £2,392,501.35 | £802,298.72 | £1,050,765.46 | £84,252.31 | £87,433.27 | £950,036.02 (22.4%) |
| 2023 | £3,495,761.69 | £1,642,210.96 | £878,317.42 | £975,233.31 | £76,851.81 | £80,032.20 | £885,061.13 (25.3%) |
| 2024 | £2,999,221.95 | £933,180.92 | £810,905.76 | £1,255,135.26 | £64,215.74 | £67,711.06 | £1,177,923.25 (39.3%) |
| 2025 | £1,233,083.98 | £452,920.26 | £257,370.51 | £522,793.21 | £36,687.50 | £38,028.48 | £479,067.20 (38.9%) |
| **Total** | **£18,862,463.71** | | | | | | **£5,992,521.82 (31.8%)** |

**Best year:** 2024 — net £1,177,923.25 (39.3% margin)
**Worst year:** 2016 — net £6,468.81 (42.1% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,459,158.04 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,459,158.04** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,992,521.82 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,354.61 | +4.7% | £6,592.99 | £6,468.81 | -1.9% | GREEN |
| 2017 | £16,138.86 | £348,630.52 | +2060.2% | £7,252.29 | £115,527.91 | +1493.0% | RED |
| 2018 | £386,623.75 | £600,953.01 | +55.4% | £128,424.00 | £248,593.75 | +93.6% | RED |
| 2019 | £675,851.95 | £1,645,452.10 | +143.5% | £281,335.50 | £668,080.05 | +137.5% | RED |
| 2020 | £1,816,630.04 | £1,857,096.31 | +2.2% | £736,963.94 | £750,002.65 | +1.8% | GREEN |
| 2021 | £2,028,952.42 | £2,421,344.01 | +19.3% | £833,649.22 | £711,761.04 | -14.6% | AMBER |
| 2022 | £2,607,611.88 | £4,245,565.53 | +62.8% | £790,935.58 | £950,036.02 | +20.1% | RED |
| 2023 | £4,508,414.67 | £3,495,761.69 | -22.5% | £1,029,561.00 | £885,061.13 | -14.0% | AMBER |
| 2024 | £3,512,844.39 | £2,999,221.95 | -14.6% | £893,105.75 | £1,177,923.25 | +31.9% | RED |
| 2025 | £3,145,356.42 | £1,233,083.98 | -60.8% | £1,315,150.33 | £479,067.20 | -63.6% | RED |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 1 | 0 | 0% | £150.00 |
| 2024 | 2 | 0 | 0% | £412.50 |

**Total:** 3 attempts, 0 wins (0% win rate), £562.50 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,409,613.09

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
- Average CLV (Point-in-Time, year-end 2017): £11,735.13
  - By billing account: C1 £5,663.48, C2 £11,201.34, C3 £9,822.81, C4 £8,697.48, C5 £11,936.33, C6 £24,335.45, C7 £8,960.39, C8 £13,765.67, C9 £11,233.24
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
- Average CLV (Point-in-Time, year-end 2018): £293,133.87
  - By billing account: C1 £5,908.44, C2 £9,760.41, C3 £9,235.37, C4 £8,131.44, C5 £12,553.69, C6 £20,472.90, C7 £8,866.14, C8 £11,804.74, C9 £11,153.98, C_IC1 £2,833,451.59
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
- Average CLV (Point-in-Time, year-end 2019): £413,691.36
  - By billing account: C1 £6,273.48, C2 £9,836.41, C3 £9,678.42, C4 £8,087.41, C5 £14,161.51, C6 £21,122.67, C7 £10,193.81, C8 £11,402.42, C9 £10,995.80, C_IC1 £2,669,956.93, C_IC2 £1,778,896.14
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

- Net margin: £128,571.40 (gross £791,806.06, capital £1,965.47)
  - Electricity: gross £714,626.51, capital £1,955.18, net £118,083.28
  - Gas: gross £77,179.55, capital £10.29, net £10,488.12
- Treasury at year end: £2,923,331.74
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.89 (avg 0.89), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.86 (avg 0.86), C7 0.88 (avg 0.88), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2020-03-16 period 20, net margin £-18.66

**Customer Book**

- Active accounts: 19 (C1, C1_2, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 8, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C1_2, C_IC4
- Losses (churn) during year: C3, C1
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £512,311.24
  - By billing account: C1 £6,522.99, C1_2 £16.55, C2 £9,653.27, C3 £8,572.79, C4 £8,572.96, C5 £13,146.03, C6 £19,251.42, C7 £10,043.04, C8 £12,191.78, C9 £10,844.02, C_IC1 £1,840,925.66, C_IC2 £823,091.66, C_IC3 £2,921,176.76, C_IC4 £1,488,348.49
- Bill shock events (>=20%): 53 -- C1g 2020-01-31 (21%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-29 (23%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (22%); C4 2020-11-30 (24%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (49%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
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
- C5 (electricity): tariff £126.10-£137.07/MWh, net margin £34.65
- C6 (electricity): tariff £143.89-£148.72/MWh, net margin £401.80
- C7 (electricity): tariff £99.69-£213.04/MWh, net margin £91.91
- C8 (electricity): tariff £110.24-£211.40/MWh, net margin £376.05
- C9 (electricity): tariff £85.33-£188.63/MWh, net margin £150.25
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £53,249.44
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £44,258.51
- C_IC3 (electricity): tariff £37.49-£81.21/MWh, net margin £13,088.47
- C_IC3g (gas): tariff £15.44-£19.38/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £5,999.58

**Portfolio Health**

- Capital cost ratio: 0.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 205, average clarity 0.831, average bill shock 14.4%, bad debt provision £-59.57, avg complaint probability 4.3%
- Solvency signal: £208,809/customer (14 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £86,379.50 vs. naked (unhedged) net margin: £964,655.44
- hedging cost £878,275.93 vs. a fully unhedged book (commodity-only: actual net £86,379.50 vs. naked net £964,655.44)
  - C1_2: actual £-149.26 vs. naked £154.26 -- hedging cost £303.52
  - C2: actual £175.35 vs. naked £570.69 -- hedging cost £395.33
  - C2g: actual £144.84 vs. naked £324.27 -- hedging cost £179.43
  - C4: actual £25.02 vs. naked £235.46 -- hedging cost £210.45
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C5: actual £-318.19 vs. naked £196.67 -- hedging cost £514.86
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-109.60 vs. naked £330.25 -- hedging cost £439.85
  - C8: actual £341.71 vs. naked £1,170.27 -- hedging cost £828.57
  - C9: actual £-18.70 vs. naked £697.66 -- hedging cost £716.35
  - C_IC1: actual £33,034.60 vs. naked £128,260.98 -- hedging cost £95,226.38
  - C_IC2: actual £42,303.73 vs. naked £96,422.44 -- hedging cost £54,118.71
  - C_IC3: actual £-15,152.11 vs. naked £221,921.88 -- hedging cost £237,074.00
  - C_IC3g: actual £17,934.51 vs. naked £159,245.07 -- hedging cost £141,310.56
  - C_IC4: actual £7,886.99 vs. naked £352,832.81 -- hedging cost £344,945.82

**Year narrative:** 2020 produced a net gain of £128,571.40 across 19 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £76,456.70 (gross £766,241.93, capital £5,635.95)
  - Electricity: gross £683,633.14, capital £5,622.97, net £66,633.50
  - Gas: gross £82,608.79, capital £12.99, net £9,823.20
- Treasury at year end: £2,958,034.42
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.95 (avg 0.95), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C5 0.94 (avg 0.94), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2021-12-31 period 48, net margin £-364.14

**Customer Book**

- Active accounts: 15 (C1_2, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2021): £499,555.35
  - By billing account: C1 £5,488.85, C1_2 £1,262.68, C2 £7,441.32, C3 £7,226.86, C4 £6,160.98, C5 £12,625.55, C6 £21,620.22, C7 £8,801.34, C8 £11,447.33, C9 £11,547.29, C_IC1 £1,626,788.13, C_IC2 £954,231.19, C_IC3 £2,621,748.66, C_IC4 £1,697,384.49
- Bill shock events (>=20%): 52 -- C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (22%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (23%); C4 2021-10-31 (48%); C4 2021-11-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%); C1_2 2021-01-31 (1207%); C1_2 2021-05-31 (33%); C1_2 2021-06-30 (55%); C1_2 2021-10-31 (76%); C1_2 2021-11-30 (75%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C7 20%, C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £133.55-£332.49/MWh, net margin £-89.38 -- **net-negative**
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £197.77
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £126.10
- C4 (electricity): tariff £122.47-£183.00/MWh, net margin £-243.82 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-302.82 -- **net-negative**
- C5 (electricity): tariff £137.07-£353.26/MWh, net margin £-678.48 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.06/MWh, net margin £591.44
- C7 (electricity): tariff £111.59-£274.50/MWh, net margin £-39.88 -- **net-negative**
- C8 (electricity): tariff £110.24-£274.50/MWh, net margin £431.61
- C9 (electricity): tariff £85.33-£264.43/MWh, net margin £62.27
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £28,130.14
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £56,396.19
- C_IC3 (electricity): tariff £42.54-£390.00/MWh, net margin £-24,063.37 -- **net-negative**
- C_IC3g (gas): tariff £19.38-£125.90/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £5,939.02

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.817, average bill shock 23.6%, bad debt provision £617.60, avg complaint probability 4.8%
- Solvency signal: £246,503/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £188,628.62 vs. naked (unhedged) net margin: £455,364.94
- hedging cost £266,736.32 vs. a fully unhedged book (commodity-only: actual net £188,628.62 vs. naked net £455,364.94)
  - C1_2: actual £-81.21 vs. naked £584.66 -- hedging cost £665.87
  - C2: actual £136.64 vs. naked £124.72 -- hedging added £11.92
  - C2g: actual £45.59 vs. naked £-190.70 -- hedging added £236.29
  - C4: actual £-220.41 vs. naked £-170.34 -- hedging cost £50.07
  - C4g: actual £-901.21 vs. naked £-1,344.38 -- hedging added £443.17
  - C5: actual £329.88 vs. naked £1,603.22 -- hedging cost £1,273.34
  - C6: actual £511.43 vs. naked £266.64 -- hedging added £244.79
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-48.56 vs. naked £-184.11 -- hedging added £135.55
  - C_IC1: actual £27,324.15 vs. naked £-61,901.23 -- hedging added £89,225.37
  - C_IC2: actual £63,564.59 vs. naked £22,126.20 -- hedging added £41,438.39
  - C_IC3: actual £97,272.89 vs. naked £231,708.10 -- hedging cost £134,435.21
  - C_IC3g: actual £4,142.87 vs. naked £85,199.40 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £178,304.23 -- hedging cost £180,207.49

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £76,456.70 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 52 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £336,112.17 (gross £1,049,224.19, capital £13,296.17)
  - Electricity: gross £958,868.27, capital £13,262.33, net £327,268.47
  - Gas: gross £90,355.92, capital £33.84, net £8,843.70
- Treasury at year end: £3,159,445.73
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C5_2 0.94 (avg 0.94), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,039,006.78, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,437.98 / stressed £20,565.19) ratio 2.70
  - 2022-05-29: treasury £3,039,127.16, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,547.78 / stressed £20,594.39) ratio 2.70
  - 2022-06-28: treasury £3,039,121.91, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,547.78 / stressed £20,594.39) ratio 2.70
  - 2022-07-28: treasury £3,038,929.29, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
  - 2022-08-27: treasury £3,038,919.68, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
  - 2022-09-26: treasury £3,038,904.24, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
  - 2022-10-26: treasury £3,037,957.44, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
  - 2022-11-25: treasury £3,037,954.46, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
  - 2022-12-25: treasury £3,037,920.80, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C2 on 2022-03-30 period 48, net margin £-112.45

**Customer Book**

- Active accounts: 17 (C1_2, C2, C2_2, C2g, C4, C4g, C5, C5_2, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 3, gas (dual-fuel): 3
- New acquisitions this year: C2_2, C5_2
- Losses (churn) during year: C2, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2022): £425,608.69
  - By billing account: C1 £5,971.32, C1_2 £2,337.47, C2 £6,887.65, C2_2 £1,131.75, C3 £7,886.40, C4 £4,436.54, C5 £11,761.71, C5_2 £7.48, C6 £20,105.15, C7 £6,371.39, C8 £11,785.07, C9 £10,370.97, C_IC1 £1,693,345.62, C_IC2 £1,065,669.85, C_IC3 £2,473,547.06, C_IC4 £1,488,123.58
- Bill shock events (>=20%): 76 -- C5 2022-01-31 (128%); C5 2022-02-28 (21%); C5 2022-05-31 (25%); C5 2022-11-30 (48%); C5 2022-12-29 (29%); C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (57%); C_IC3 2022-01-31 (108%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C1_2 2022-01-31 (141%); C1_2 2022-02-28 (28%); C1_2 2022-04-30 (23%); C1_2 2022-05-31 (43%); C1_2 2022-06-30 (34%); C1_2 2022-09-30 (51%); C1_2 2022-11-30 (79%); C1_2 2022-12-31 (61%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 12 at risk (≥20% churn prob): C1_2 41%, C2 38%, C4 38%, C5 38%, C6 35%, C7 23%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.45-£332.49/MWh, net margin £178.50
- C2 (electricity): tariff £183.00/MWh, net margin £-99.38 -- **net-negative**
- C2_2 (electricity): tariff £361.95/MWh, net margin £219.72
- C2g (gas): tariff £35.00/MWh, net margin £2.93
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-170.22 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,159.15 -- **net-negative**
- C5 (electricity): tariff £353.26/MWh, net margin £523.43
- C5_2 (electricity): tariff £266.73/MWh, net margin £-6.45 -- **net-negative**
- C6 (electricity): tariff £197.06-£406.99/MWh, net margin £1,062.94
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,632.87 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £73.71
- C9 (electricity): tariff £138.51-£389.55/MWh, net margin £110.53
- C_IC1 (electricity): tariff £-83.39-£462.99/MWh, net margin £136,461.49
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £76,071.45
- C_IC3 (electricity): tariff £150.10-£390.00/MWh, net margin £108,556.25
- C_IC3g (gas): tariff £116.42-£125.90/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £5,919.38

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 2 -- £3,469,217.95 -> £3,053,931.56 (12.0%); £3,469,395.95 -> £3,053,385.77 (12.0%)
- Bills issued: 173, average clarity 0.783, average bill shock 33.9%, bad debt provision £118.54, avg complaint probability 5.8%
- Solvency signal: £225,675/customer (14 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £199,826.07 vs. naked (unhedged) net margin: £1,226,097.34
- hedging cost £1,026,271.27 vs. a fully unhedged book (commodity-only: actual net £199,826.07 vs. naked net £1,226,097.34)
  - C1_2: actual £-589.08 vs. naked £1,295.38 -- hedging cost £1,884.46
  - C2_2: actual £30.18 vs. naked £1,645.15 -- hedging cost £1,614.97
  - C4: actual £-277.33 vs. naked £595.36 -- hedging cost £872.70
  - C4g: actual £-1,950.48 vs. naked £1,336.80 -- hedging cost £3,287.28
  - C5_2: actual £-1,113.67 vs. naked £2,632.27 -- hedging cost £3,745.94
  - C6: actual £1,130.77 vs. naked £3,998.91 -- hedging cost £2,868.14
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-481.87 vs. naked £1,102.92 -- hedging cost £1,584.78
  - C9: actual £-49.37 vs. naked £1,012.21 -- hedging cost £1,061.58
  - C_IC1: actual £212,770.84 vs. naked £251,052.75 -- hedging cost £38,281.91
  - C_IC2: actual £87,504.96 vs. naked £126,811.39 -- hedging cost £39,306.43
  - C_IC3: actual £-108,689.56 vs. naked £503,974.57 -- hedging cost £612,664.13
  - C_IC3g: actual £8,513.79 vs. naked £123,301.26 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £205,056.67 -- hedging cost £201,583.86

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £336,112.17 across 17 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 76 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £161,777.83 (gross £973,896.95, capital £10,139.98)
  - Electricity: gross £852,956.85, capital £10,087.56, net £152,818.87
  - Gas: gross £120,940.11, capital £52.42, net £8,958.96
- Treasury at year end: £3,395,543.83
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.91 (avg 0.91), C2_2 0.93 (avg 0.93), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5_2 0.91 (avg 0.91), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,135,960.36, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,347.43 / stressed £43,958.32) ratio 2.76
  - 2023-02-23: treasury £3,135,960.71, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,347.43 / stressed £43,958.32) ratio 2.76
  - 2023-03-25: treasury £3,135,961.01, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,347.43 / stressed £43,958.32) ratio 2.76
  - 2023-04-24: treasury £3,216,174.27, C2->1.00, C4->1.00, C5->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,380.19 / stressed £48,915.08) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC1 on 2023-06-16 period 22, net margin £-21.69

**Customer Book**

- Active accounts: 14 (C1_2, C2_2, C4, C4g, C5_2, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2023): £395,472.63
  - By billing account: C1 £6,367.23, C1_2 £2,113.03, C2 £6,360.83, C2_2 £3,891.56, C3 £6,449.53, C4 £3,232.16, C5 £10,840.28, C5_2 £951.63, C6 £19,356.17, C7 £7,009.62, C8 £9,274.92, C9 £9,990.44, C_IC1 £1,556,560.50, C_IC2 £831,541.06, C_IC3 £2,426,056.82, C_IC4 £1,427,566.29
- Bill shock events (>=20%): 53 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (32%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (25%); C4 2023-04-30 (29%); C4 2023-09-30 (24%); C4 2023-11-30 (27%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (46%); C4g 2023-11-30 (63%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (101%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%); C1_2 2023-05-31 (38%); C1_2 2023-06-30 (43%); C1_2 2023-10-31 (73%); C1_2 2023-11-30 (83%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%); C5_2 2023-01-31 (2059%); C5_2 2023-05-31 (21%); C5_2 2023-06-30 (24%); C5_2 2023-10-31 (30%); C5_2 2023-11-30 (50%)
- Churn risk (accounts renewing in 2023): 9 at risk (≥20% churn prob): C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.45-£268.29/MWh, net margin £-444.72 -- **net-negative**
- C2_2 (electricity): tariff £349.30-£361.95/MWh, net margin £688.49
- C4 (electricity): tariff £249.30-£305.00/MWh, net margin £-9.42 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,040.96 -- **net-negative**
- C5_2 (electricity): tariff £266.73-£269.33/MWh, net margin £-1,001.27 -- **net-negative**
- C6 (electricity): tariff £331.64-£406.99/MWh, net margin £1,413.73
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-144.77 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £159.02
- C9 (electricity): tariff £192.57-£389.55/MWh, net margin £396.44
- C_IC1 (electricity): tariff £-60.00-£462.99/MWh, net margin £162,617.53
- C_IC2 (electricity): tariff £-186.24-£476.92/MWh, net margin £86,068.37
- C_IC3 (electricity): tariff £94.12-£286.55/MWh, net margin £-102,852.37 -- **net-negative**
- C_IC3g (gas): tariff £56.57-£116.42/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £5,927.85

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): 47 -- £3,778,040.43 -> £3,395,351.94 (10.1%); £3,778,040.58 -> £3,395,351.95 (10.1%); £3,778,040.73 -> £3,395,351.97 (10.1%); £3,778,040.88 -> £3,395,351.98 (10.1%); £3,778,041.04 -> £3,395,352.00 (10.1%); £3,778,041.19 -> £3,395,352.01 (10.1%); £3,778,041.34 -> £3,395,352.03 (10.1%); £3,778,041.50 -> £3,395,352.04 (10.1%); £3,778,041.65 -> £3,395,352.06 (10.1%); £3,778,041.81 -> £3,395,352.07 (10.1%); £3,778,041.97 -> £3,395,352.09 (10.1%); £3,778,042.12 -> £3,395,352.22 (10.1%); £3,778,042.28 -> £3,395,352.36 (10.1%); £3,778,042.45 -> £3,395,352.49 (10.1%); £3,778,042.64 -> £3,395,352.62 (10.1%); £3,778,042.85 -> £3,395,352.76 (10.1%); £3,778,043.07 -> £3,395,352.90 (10.1%); £3,778,043.31 -> £3,395,353.05 (10.1%); £3,778,043.58 -> £3,395,353.20 (10.1%); £3,778,043.83 -> £3,395,353.22 (10.1%); £3,778,044.09 -> £3,395,353.25 (10.1%); £3,778,044.34 -> £3,395,353.27 (10.1%); £3,778,044.61 -> £3,395,353.30 (10.1%); £3,778,044.87 -> £3,395,353.33 (10.1%); £3,778,045.13 -> £3,395,353.35 (10.1%); £3,778,045.40 -> £3,395,353.38 (10.1%); £3,778,045.66 -> £3,395,353.40 (10.1%); £3,778,045.92 -> £3,395,353.43 (10.1%); £3,778,046.18 -> £3,395,353.45 (10.1%); £3,778,046.43 -> £3,395,353.48 (10.1%); £3,778,046.69 -> £3,395,353.50 (10.1%); £3,778,046.94 -> £3,395,353.53 (10.1%); £3,778,047.20 -> £3,395,353.67 (10.1%); £3,778,047.46 -> £3,395,353.82 (10.1%); £3,778,047.72 -> £3,395,353.97 (10.1%); £3,778,047.98 -> £3,395,354.12 (10.1%); £3,778,048.24 -> £3,395,354.27 (10.1%); £3,778,048.50 -> £3,395,354.42 (10.1%); £3,778,048.77 -> £3,395,354.57 (10.1%); £3,778,049.03 -> £3,395,354.72 (10.1%); £3,778,049.29 -> £3,395,354.87 (10.1%); £3,778,049.55 -> £3,395,355.00 (10.1%); £3,778,049.81 -> £3,395,355.14 (10.1%); £3,778,050.07 -> £3,395,355.17 (10.1%); £3,778,050.33 -> £3,395,355.19 (10.1%); £3,778,050.57 -> £3,395,355.22 (10.1%); £3,778,050.79 -> £3,395,543.83 (10.1%)
- Bills issued: 168, average clarity 0.801, average bill shock 30.1%, bad debt provision £0.00, avg complaint probability 5.0%
- Solvency signal: £282,962/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £374,806.08 vs. naked (unhedged) net margin: £1,216,465.11
- hedging cost £841,659.04 vs. a fully unhedged book (commodity-only: actual net £374,806.08 vs. naked net £1,216,465.11)
  - C1_2: actual £684.84 vs. naked £1,724.56 -- hedging cost £1,039.72
  - C2_2: actual £821.91 vs. naked £2,413.74 -- hedging cost £1,591.83
  - C4: actual £313.86 vs. naked £700.05 -- hedging cost £386.18
  - C4g: actual £529.39 vs. naked £1,048.79 -- hedging cost £519.40
  - C5_2: actual £1,196.47 vs. naked £3,270.66 -- hedging cost £2,074.19
  - C6: actual £1,374.90 vs. naked £5,042.71 -- hedging cost £3,667.81
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £140.61 vs. naked £1,972.23 -- hedging cost £1,831.62
  - C9: actual £626.00 vs. naked £2,129.64 -- hedging cost £1,503.64
  - C_IC1: actual £141,576.45 vs. naked £284,450.26 -- hedging cost £142,873.81
  - C_IC2: actual £94,108.05 vs. naked £162,159.80 -- hedging cost £68,051.75
  - C_IC3: actual £120,587.99 vs. naked £394,328.28 -- hedging cost £273,740.29
  - C_IC3g: actual £8,660.26 vs. naked £123,107.25 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £232,127.67 -- hedging cost £228,435.92

**Year narrative:** 2023 produced a net gain of £161,777.83 across 14 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 53 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £341,665.05 (gross £1,254,544.51, capital £9,500.95)
  - Electricity: gross £1,130,130.63, capital £9,477.55, net £331,197.71
  - Gas: gross £124,413.88, capital £23.40, net £10,467.35
- Treasury at year end: £3,784,369.41
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.87 (avg 0.87), C2_2 0.91 (avg 0.91), C5_2 0.88 (avg 0.88), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2024-06-28 period 31, net margin £-26.25

**Customer Book**

- Active accounts: 14 (C1_2, C2_2, C4, C4g, C5_2, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2024): £368,007.19
  - By billing account: C1 £4,802.98, C1_2 £3,245.92, C2 £5,274.31, C2_2 £4,317.22, C3 £5,898.12, C4 £3,712.88, C5 £11,553.29, C5_2 £3,503.81, C6 £16,545.70, C7 £9,084.64, C8 £9,500.16, C9 £9,190.96, C_IC1 £1,507,259.29, C_IC2 £615,557.54, C_IC3 £2,358,214.99, C_IC4 £1,320,453.23
- Bill shock events (>=20%): 45 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (30%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C_IC3 2024-01-31 (20%); C1_2 2024-01-31 (21%); C1_2 2024-02-29 (28%); C1_2 2024-04-30 (23%); C1_2 2024-05-31 (44%); C1_2 2024-09-30 (51%); C1_2 2024-10-31 (45%); C1_2 2024-11-30 (57%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (59%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (55%); C5_2 2024-02-29 (21%); C5_2 2024-05-31 (24%); C5_2 2024-10-31 (25%); C5_2 2024-11-30 (34%)
- Churn risk (accounts renewing in 2024): 8 at risk (≥20% churn prob): C2_2 23%, C4 38%, C6 29%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC3 41%, C_IC4 20%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01-£268.29/MWh, net margin £765.09
- C2_2 (electricity): tariff £201.48-£349.30/MWh, net margin £513.22
- C4 (electricity): tariff £249.30/MWh, net margin £256.64
- C4g (gas): tariff £66.00/MWh, net margin £436.59
- C5_2 (electricity): tariff £231.60-£269.33/MWh, net margin £1,252.38
- C6 (electricity): tariff £331.64/MWh, net margin £511.14
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £635.74
- C8 (electricity): tariff £162.10-£397.50/MWh, net margin £428.18
- C9 (electricity): tariff £165.00-£367.64/MWh, net margin £655.96
- C_IC1 (electricity): tariff £-98.58-£330.68/MWh, net margin £125,732.10
- C_IC2 (electricity): tariff £-106.92-£354.92/MWh, net margin £69,935.13
- C_IC3 (electricity): tariff £89.47-£179.68/MWh, net margin £124,560.82
- C_IC3g (gas): tariff £54.85-£56.57/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £5,951.30

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): 4271 -- £3,780,498.77 -> £3,395,543.87 (10.2%); £3,780,498.95 -> £3,395,543.89 (10.2%); £3,780,499.12 -> £3,395,543.91 (10.2%); £3,780,499.30 -> £3,395,543.92 (10.2%); £3,780,499.47 -> £3,395,543.94 (10.2%); £3,780,499.64 -> £3,395,543.96 (10.2%); £3,780,499.81 -> £3,395,543.97 (10.2%); £3,780,499.99 -> £3,395,543.99 (10.2%); £3,780,500.16 -> £3,395,544.01 (10.2%); £3,780,500.34 -> £3,395,544.02 (10.2%); £3,780,500.51 -> £3,395,544.04 (10.2%); £3,780,500.68 -> £3,395,544.18 (10.2%); £3,780,500.85 -> £3,395,544.33 (10.2%); £3,780,501.04 -> £3,395,544.48 (10.2%); £3,780,501.25 -> £3,395,544.64 (10.2%); £3,780,501.48 -> £3,395,544.80 (10.2%); £3,780,501.72 -> £3,395,544.96 (10.2%); £3,780,501.98 -> £3,395,545.11 (10.2%); £3,780,502.27 -> £3,395,545.26 (10.2%); £3,780,502.54 -> £3,395,545.29 (10.2%); £3,780,502.84 -> £3,395,545.31 (10.2%); £3,780,503.13 -> £3,395,545.33 (10.2%); £3,780,503.42 -> £3,395,545.36 (10.2%); £3,780,503.71 -> £3,395,545.38 (10.2%); £3,780,504.00 -> £3,395,545.41 (10.2%); £3,780,504.29 -> £3,395,545.43 (10.2%); £3,780,504.57 -> £3,395,545.45 (10.2%); £3,780,504.84 -> £3,395,545.48 (10.2%); £3,780,505.11 -> £3,395,545.50 (10.2%); £3,780,505.40 -> £3,395,545.52 (10.2%); £3,780,505.69 -> £3,395,545.55 (10.2%); £3,780,505.97 -> £3,395,545.58 (10.2%); £3,780,506.26 -> £3,395,545.74 (10.2%); £3,780,506.54 -> £3,395,545.91 (10.2%); £3,780,506.76 -> £3,395,546.07 (10.2%); £3,780,506.98 -> £3,395,546.23 (10.2%); £3,780,507.19 -> £3,395,546.41 (10.2%); £3,780,507.49 -> £3,395,546.58 (10.2%); £3,780,507.79 -> £3,395,546.75 (10.2%); £3,780,508.06 -> £3,395,546.92 (10.2%); £3,780,508.36 -> £3,395,547.09 (10.2%); £3,780,508.64 -> £3,395,547.25 (10.2%); £3,780,508.93 -> £3,395,547.42 (10.2%); £3,780,509.22 -> £3,395,547.45 (10.2%); £3,780,509.52 -> £3,395,547.48 (10.2%); £3,780,509.77 -> £3,395,547.51 (10.2%); £3,780,510.02 -> £3,395,547.53 (10.2%); £3,780,510.24 -> £3,395,547.55 (10.2%); £3,780,510.41 -> £3,395,547.57 (10.2%); £3,780,510.59 -> £3,395,547.59 (10.2%); £3,780,510.76 -> £3,395,547.61 (10.2%); £3,780,510.92 -> £3,395,547.62 (10.2%); £3,780,511.09 -> £3,395,547.64 (10.2%); £3,780,511.26 -> £3,395,547.66 (10.2%); £3,780,511.44 -> £3,395,547.67 (10.2%); £3,780,511.60 -> £3,395,547.69 (10.2%); £3,780,511.77 -> £3,395,547.71 (10.2%); £3,780,511.95 -> £3,395,547.73 (10.2%); £3,780,512.11 -> £3,395,547.74 (10.2%); £3,780,512.28 -> £3,395,547.87 (10.2%); £3,780,512.45 -> £3,395,547.99 (10.2%); £3,780,512.64 -> £3,395,548.12 (10.2%); £3,780,512.84 -> £3,395,548.25 (10.2%); £3,780,513.07 -> £3,395,548.39 (10.2%); £3,780,513.30 -> £3,395,548.52 (10.2%); £3,780,513.56 -> £3,395,548.65 (10.2%); £3,780,513.84 -> £3,395,548.79 (10.2%); £3,780,514.12 -> £3,395,548.81 (10.2%); £3,780,514.40 -> £3,395,548.83 (10.2%); £3,780,514.68 -> £3,395,548.86 (10.2%); £3,780,514.96 -> £3,395,548.88 (10.2%); £3,780,515.24 -> £3,395,548.91 (10.2%); £3,780,515.52 -> £3,395,548.93 (10.2%); £3,780,515.80 -> £3,395,548.95 (10.2%); £3,780,516.08 -> £3,395,548.98 (10.2%); £3,780,516.35 -> £3,395,549.00 (10.2%); £3,780,516.63 -> £3,395,549.02 (10.2%); £3,780,516.90 -> £3,395,549.05 (10.2%); £3,780,517.18 -> £3,395,549.07 (10.2%); £3,780,517.46 -> £3,395,549.10 (10.2%); £3,780,517.67 -> £3,395,549.23 (10.2%); £3,780,517.88 -> £3,395,549.36 (10.2%); £3,780,518.10 -> £3,395,549.50 (10.2%); £3,780,518.31 -> £3,395,549.64 (10.2%); £3,780,518.52 -> £3,395,549.77 (10.2%); £3,780,518.74 -> £3,395,549.91 (10.2%); £3,780,518.95 -> £3,395,550.04 (10.2%); £3,780,519.23 -> £3,395,550.17 (10.2%); £3,780,519.51 -> £3,395,550.31 (10.2%); £3,780,519.79 -> £3,395,550.44 (10.2%); £3,780,520.07 -> £3,395,550.58 (10.2%); £3,780,520.36 -> £3,395,550.61 (10.2%); £3,780,520.64 -> £3,395,550.64 (10.2%); £3,780,520.91 -> £3,395,550.66 (10.2%); £3,780,521.14 -> £3,395,550.68 (10.2%); £3,780,521.35 -> £3,395,550.70 (10.2%); £3,780,521.53 -> £3,395,550.72 (10.2%); £3,780,521.70 -> £3,395,550.74 (10.2%); £3,780,521.87 -> £3,395,550.75 (10.2%); £3,780,522.04 -> £3,395,550.77 (10.2%); £3,780,522.21 -> £3,395,550.79 (10.2%); £3,780,522.37 -> £3,395,550.80 (10.2%); £3,780,522.54 -> £3,395,550.82 (10.2%); £3,780,522.71 -> £3,395,550.84 (10.2%); £3,780,522.88 -> £3,395,550.85 (10.2%); £3,780,523.05 -> £3,395,550.87 (10.2%); £3,780,523.22 -> £3,395,550.89 (10.2%); £3,780,523.39 -> £3,395,551.03 (10.2%); £3,780,523.57 -> £3,395,551.18 (10.2%); £3,780,523.75 -> £3,395,551.34 (10.2%); £3,780,523.96 -> £3,395,551.50 (10.2%); £3,780,524.18 -> £3,395,551.66 (10.2%); £3,780,524.43 -> £3,395,551.80 (10.2%); £3,780,524.70 -> £3,395,551.95 (10.2%); £3,780,524.98 -> £3,395,552.09 (10.2%); £3,780,525.26 -> £3,395,552.11 (10.2%); £3,780,525.54 -> £3,395,552.14 (10.2%); £3,780,525.82 -> £3,395,552.16 (10.2%); £3,780,526.11 -> £3,395,552.18 (10.2%); £3,780,526.40 -> £3,395,552.21 (10.2%); £3,780,526.69 -> £3,395,552.23 (10.2%); £3,780,526.98 -> £3,395,552.25 (10.2%); £3,780,527.26 -> £3,395,552.28 (10.2%); £3,780,527.54 -> £3,395,552.30 (10.2%); £3,780,527.82 -> £3,395,552.32 (10.2%); £3,780,528.10 -> £3,395,552.35 (10.2%); £3,780,528.38 -> £3,395,552.37 (10.2%); £3,780,528.66 -> £3,395,552.40 (10.2%); £3,780,528.94 -> £3,395,552.55 (10.2%); £3,780,529.16 -> £3,395,552.71 (10.2%); £3,780,529.44 -> £3,395,552.87 (10.2%); £3,780,529.64 -> £3,395,553.03 (10.2%); £3,780,529.85 -> £3,395,553.18 (10.2%); £3,780,530.07 -> £3,395,553.34 (10.2%); £3,780,530.29 -> £3,395,553.50 (10.2%); £3,780,530.56 -> £3,395,553.66 (10.2%); £3,780,530.84 -> £3,395,553.81 (10.2%); £3,780,531.12 -> £3,395,553.97 (10.2%); £3,780,531.40 -> £3,395,554.12 (10.2%); £3,780,531.69 -> £3,395,554.15 (10.2%); £3,780,531.98 -> £3,395,554.17 (10.2%); £3,780,532.23 -> £3,395,554.20 (10.2%); £3,780,532.47 -> £3,395,554.22 (10.2%); £3,780,532.69 -> £3,395,554.24 (10.2%); £3,780,532.85 -> £3,395,554.26 (10.2%); £3,780,533.02 -> £3,395,554.27 (10.2%); £3,780,533.18 -> £3,395,554.29 (10.2%); £3,780,533.35 -> £3,395,554.31 (10.2%); £3,780,533.52 -> £3,395,554.33 (10.2%); £3,780,533.68 -> £3,395,554.34 (10.2%); £3,780,533.85 -> £3,395,554.36 (10.2%); £3,780,534.02 -> £3,395,554.38 (10.2%); £3,780,534.19 -> £3,395,554.39 (10.2%); £3,780,534.36 -> £3,395,554.41 (10.2%); £3,780,534.53 -> £3,395,554.43 (10.2%); £3,780,534.70 -> £3,395,554.59 (10.2%); £3,780,534.87 -> £3,395,554.76 (10.2%); £3,780,535.06 -> £3,395,554.93 (10.2%); £3,780,535.26 -> £3,395,555.11 (10.2%); £3,780,535.48 -> £3,395,555.28 (10.2%); £3,780,535.72 -> £3,395,555.45 (10.2%); £3,780,535.98 -> £3,395,555.62 (10.2%); £3,780,536.26 -> £3,395,555.79 (10.2%); £3,780,536.53 -> £3,395,555.82 (10.2%); £3,780,536.82 -> £3,395,555.84 (10.2%); £3,780,537.09 -> £3,395,555.87 (10.2%); £3,780,537.37 -> £3,395,555.89 (10.2%); £3,780,537.65 -> £3,395,555.91 (10.2%); £3,780,537.92 -> £3,395,555.94 (10.2%); £3,780,538.20 -> £3,395,555.96 (10.2%); £3,780,538.48 -> £3,395,555.98 (10.2%); £3,780,538.76 -> £3,395,556.00 (10.2%); £3,780,539.03 -> £3,395,556.03 (10.2%); £3,780,539.31 -> £3,395,556.05 (10.2%); £3,780,539.59 -> £3,395,556.08 (10.2%); £3,780,539.87 -> £3,395,556.10 (10.2%); £3,780,540.07 -> £3,395,556.28 (10.2%); £3,780,540.35 -> £3,395,556.46 (10.2%); £3,780,540.63 -> £3,395,556.63 (10.2%); £3,780,540.83 -> £3,395,556.81 (10.2%); £3,780,541.10 -> £3,395,556.99 (10.2%); £3,780,541.38 -> £3,395,557.15 (10.2%); £3,780,541.59 -> £3,395,557.32 (10.2%); £3,780,541.88 -> £3,395,557.49 (10.2%); £3,780,542.15 -> £3,395,557.66 (10.2%); £3,780,542.43 -> £3,395,557.83 (10.2%); £3,780,542.71 -> £3,395,558.00 (10.2%); £3,780,543.00 -> £3,395,558.03 (10.2%); £3,780,543.27 -> £3,395,558.05 (10.2%); £3,780,543.52 -> £3,395,558.08 (10.2%); £3,780,543.76 -> £3,395,558.10 (10.2%); £3,780,543.98 -> £3,395,558.12 (10.2%); £3,780,544.14 -> £3,395,558.14 (10.2%); £3,780,544.30 -> £3,395,558.16 (10.2%); £3,780,544.46 -> £3,395,558.17 (10.2%); £3,780,544.62 -> £3,395,558.19 (10.2%); £3,780,544.78 -> £3,395,558.21 (10.2%); £3,780,544.94 -> £3,395,558.22 (10.2%); £3,780,545.11 -> £3,395,558.24 (10.2%); £3,780,545.26 -> £3,395,558.26 (10.2%); £3,780,545.43 -> £3,395,558.27 (10.2%); £3,780,545.60 -> £3,395,558.29 (10.2%); £3,780,545.76 -> £3,395,558.31 (10.2%); £3,780,545.92 -> £3,395,558.49 (10.2%); £3,780,546.08 -> £3,395,558.67 (10.2%); £3,780,546.26 -> £3,395,558.86 (10.2%); £3,780,546.45 -> £3,395,559.05 (10.2%); £3,780,546.66 -> £3,395,559.24 (10.2%); £3,780,546.90 -> £3,395,559.43 (10.2%); £3,780,547.16 -> £3,395,559.61 (10.2%); £3,780,547.43 -> £3,395,559.79 (10.2%); £3,780,547.71 -> £3,395,559.82 (10.2%); £3,780,547.97 -> £3,395,559.84 (10.2%); £3,780,548.24 -> £3,395,559.86 (10.2%); £3,780,548.51 -> £3,395,559.89 (10.2%); £3,780,548.78 -> £3,395,559.91 (10.2%); £3,780,549.05 -> £3,395,559.94 (10.2%); £3,780,549.32 -> £3,395,559.96 (10.2%); £3,780,549.59 -> £3,395,559.98 (10.2%); £3,780,549.85 -> £3,395,560.01 (10.2%); £3,780,550.12 -> £3,395,560.03 (10.2%); £3,780,550.39 -> £3,395,560.05 (10.2%); £3,780,550.65 -> £3,395,560.08 (10.2%); £3,780,550.93 -> £3,395,560.11 (10.2%); £3,780,551.12 -> £3,395,560.29 (10.2%); £3,780,551.33 -> £3,395,560.47 (10.2%); £3,780,551.53 -> £3,395,560.66 (10.2%); £3,780,551.74 -> £3,395,560.86 (10.2%); £3,780,552.00 -> £3,395,561.04 (10.2%); £3,780,552.20 -> £3,395,561.23 (10.2%); £3,780,552.41 -> £3,395,561.41 (10.2%); £3,780,552.67 -> £3,395,561.60 (10.2%); £3,780,552.94 -> £3,395,561.78 (10.2%); £3,780,553.21 -> £3,395,561.97 (10.2%); £3,780,553.48 -> £3,395,562.16 (10.2%); £3,780,553.74 -> £3,395,562.19 (10.2%); £3,780,554.01 -> £3,395,562.21 (10.2%); £3,780,554.27 -> £3,395,562.24 (10.2%); £3,780,554.49 -> £3,395,562.26 (10.2%); £3,780,554.70 -> £3,395,562.28 (10.2%); £3,780,554.85 -> £3,395,562.30 (10.2%); £3,780,554.99 -> £3,395,562.32 (10.2%); £3,780,555.14 -> £3,395,562.34 (10.2%); £3,780,555.29 -> £3,395,562.35 (10.2%); £3,780,555.43 -> £3,395,562.37 (10.2%); £3,780,555.57 -> £3,395,562.39 (10.2%); £3,780,555.71 -> £3,395,562.40 (10.2%); £3,780,555.85 -> £3,395,562.42 (10.2%); £3,780,555.99 -> £3,395,562.44 (10.2%); £3,780,556.13 -> £3,395,562.45 (10.2%); £3,780,556.26 -> £3,395,562.47 (10.2%); £3,780,556.41 -> £3,395,562.69 (10.2%); £3,780,556.55 -> £3,395,562.91 (10.2%); £3,780,556.70 -> £3,395,563.14 (10.2%); £3,780,556.88 -> £3,395,563.37 (10.2%); £3,780,557.07 -> £3,395,563.60 (10.2%); £3,780,557.27 -> £3,395,563.83 (10.2%); £3,780,557.49 -> £3,395,564.06 (10.2%); £3,780,557.73 -> £3,395,564.30 (10.2%); £3,780,557.96 -> £3,395,564.32 (10.2%); £3,780,558.19 -> £3,395,564.35 (10.2%); £3,780,558.43 -> £3,395,564.37 (10.2%); £3,780,558.67 -> £3,395,564.40 (10.2%); £3,780,558.90 -> £3,395,564.43 (10.2%); £3,780,559.14 -> £3,395,564.45 (10.2%); £3,780,559.37 -> £3,395,564.48 (10.2%); £3,780,559.61 -> £3,395,564.51 (10.2%); £3,780,559.86 -> £3,395,564.53 (10.2%); £3,780,560.09 -> £3,395,564.55 (10.2%); £3,780,560.34 -> £3,395,564.58 (10.2%); £3,780,560.57 -> £3,395,564.60 (10.2%); £3,780,560.81 -> £3,395,564.63 (10.2%); £3,780,561.04 -> £3,395,564.85 (10.2%); £3,780,561.21 -> £3,395,565.07 (10.2%); £3,780,561.39 -> £3,395,565.29 (10.2%); £3,780,561.56 -> £3,395,565.51 (10.2%); £3,780,561.74 -> £3,395,565.73 (10.2%); £3,780,561.91 -> £3,395,565.95 (10.2%); £3,780,562.10 -> £3,395,566.18 (10.2%); £3,780,562.33 -> £3,395,566.41 (10.2%); £3,780,562.56 -> £3,395,566.64 (10.2%); £3,780,562.79 -> £3,395,566.86 (10.2%); £3,780,563.03 -> £3,395,567.08 (10.2%); £3,780,563.26 -> £3,395,567.11 (10.2%); £3,780,563.49 -> £3,395,567.13 (10.2%); £3,780,563.71 -> £3,395,567.16 (10.2%); £3,780,563.91 -> £3,395,567.18 (10.2%); £3,780,564.09 -> £3,395,567.21 (10.2%); £3,780,564.23 -> £3,395,567.23 (10.2%); £3,780,564.37 -> £3,395,567.24 (10.2%); £3,780,564.51 -> £3,395,567.26 (10.2%); £3,780,564.65 -> £3,395,567.28 (10.2%); £3,780,564.79 -> £3,395,567.30 (10.2%); £3,780,564.93 -> £3,395,567.31 (10.2%); £3,780,565.07 -> £3,395,567.33 (10.2%); £3,780,565.21 -> £3,395,567.35 (10.2%); £3,780,565.35 -> £3,395,567.36 (10.2%); £3,780,565.49 -> £3,395,567.38 (10.2%); £3,780,565.63 -> £3,395,567.40 (10.2%); £3,780,565.77 -> £3,395,567.61 (10.2%); £3,780,565.90 -> £3,395,567.83 (10.2%); £3,780,566.06 -> £3,395,568.05 (10.2%); £3,780,566.23 -> £3,395,568.26 (10.2%); £3,780,566.42 -> £3,395,568.48 (10.2%); £3,780,566.63 -> £3,395,568.70 (10.2%); £3,780,566.85 -> £3,395,568.92 (10.2%); £3,780,567.08 -> £3,395,569.14 (10.2%); £3,780,567.32 -> £3,395,569.17 (10.2%); £3,780,567.55 -> £3,395,569.20 (10.2%); £3,780,567.78 -> £3,395,569.23 (10.2%); £3,780,568.01 -> £3,395,569.26 (10.2%); £3,780,568.24 -> £3,395,569.29 (10.2%); £3,780,568.47 -> £3,395,569.32 (10.2%); £3,780,568.69 -> £3,395,569.35 (10.2%); £3,780,568.93 -> £3,395,569.38 (10.2%); £3,780,569.16 -> £3,395,569.41 (10.2%); £3,780,569.40 -> £3,395,569.43 (10.2%); £3,780,569.63 -> £3,395,569.46 (10.2%); £3,780,569.86 -> £3,395,569.49 (10.2%); £3,780,570.09 -> £3,395,569.52 (10.2%); £3,780,570.26 -> £3,395,569.73 (10.2%); £3,780,570.44 -> £3,395,569.95 (10.2%); £3,780,570.61 -> £3,395,570.16 (10.2%); £3,780,570.78 -> £3,395,570.39 (10.2%); £3,780,571.01 -> £3,395,570.61 (10.2%); £3,780,571.19 -> £3,395,570.83 (10.2%); £3,780,571.37 -> £3,395,571.05 (10.2%); £3,780,571.61 -> £3,395,571.28 (10.2%); £3,780,571.84 -> £3,395,571.50 (10.2%); £3,780,572.08 -> £3,395,571.72 (10.2%); £3,780,572.31 -> £3,395,571.94 (10.2%); £3,780,572.53 -> £3,395,571.96 (10.2%); £3,780,572.77 -> £3,395,571.99 (10.2%); £3,780,572.98 -> £3,395,572.02 (10.2%); £3,780,573.18 -> £3,395,572.04 (10.2%); £3,780,573.36 -> £3,395,572.06 (10.2%); £3,780,573.52 -> £3,395,572.08 (10.2%); £3,780,573.68 -> £3,395,572.10 (10.2%); £3,780,573.82 -> £3,395,572.11 (10.2%); £3,780,573.98 -> £3,395,572.13 (10.2%); £3,780,574.13 -> £3,395,572.15 (10.2%); £3,780,574.29 -> £3,395,572.16 (10.2%); £3,780,574.44 -> £3,395,572.18 (10.2%); £3,780,574.59 -> £3,395,572.20 (10.2%); £3,780,574.75 -> £3,395,572.21 (10.2%); £3,780,574.90 -> £3,395,572.23 (10.2%); £3,780,575.06 -> £3,395,572.25 (10.2%); £3,780,575.21 -> £3,395,572.45 (10.2%); £3,780,575.37 -> £3,395,572.66 (10.2%); £3,780,575.54 -> £3,395,572.87 (10.2%); £3,780,575.72 -> £3,395,573.08 (10.2%); £3,780,575.93 -> £3,395,573.30 (10.2%); £3,780,576.15 -> £3,395,573.52 (10.2%); £3,780,576.38 -> £3,395,573.74 (10.2%); £3,780,576.63 -> £3,395,573.96 (10.2%); £3,780,576.88 -> £3,395,573.98 (10.2%); £3,780,577.13 -> £3,395,574.00 (10.2%); £3,780,577.40 -> £3,395,574.03 (10.2%); £3,780,577.64 -> £3,395,574.05 (10.2%); £3,780,577.90 -> £3,395,574.07 (10.2%); £3,780,578.16 -> £3,395,574.10 (10.2%); £3,780,578.42 -> £3,395,574.12 (10.2%); £3,780,578.68 -> £3,395,574.14 (10.2%); £3,780,578.94 -> £3,395,574.17 (10.2%); £3,780,579.19 -> £3,395,574.19 (10.2%); £3,780,579.45 -> £3,395,574.21 (10.2%); £3,780,579.71 -> £3,395,574.24 (10.2%); £3,780,579.97 -> £3,395,574.27 (10.2%); £3,780,580.23 -> £3,395,574.48 (10.2%); £3,780,580.49 -> £3,395,574.70 (10.2%); £3,780,580.75 -> £3,395,574.93 (10.2%); £3,780,580.99 -> £3,395,575.15 (10.2%); £3,780,581.24 -> £3,395,575.37 (10.2%); £3,780,581.50 -> £3,395,575.59 (10.2%); £3,780,581.69 -> £3,395,575.81 (10.2%); £3,780,581.94 -> £3,395,576.03 (10.2%); £3,780,582.19 -> £3,395,576.24 (10.2%); £3,780,582.44 -> £3,395,576.46 (10.2%); £3,780,582.70 -> £3,395,576.67 (10.2%); £3,780,582.95 -> £3,395,576.70 (10.2%); £3,780,583.21 -> £3,395,576.73 (10.2%); £3,780,583.44 -> £3,395,576.75 (10.2%); £3,780,583.66 -> £3,395,576.78 (10.2%); £3,780,583.86 -> £3,395,576.80 (10.2%); £3,780,584.01 -> £3,395,576.81 (10.2%); £3,780,584.16 -> £3,395,576.83 (10.2%); £3,780,584.32 -> £3,395,576.85 (10.2%); £3,780,584.47 -> £3,395,576.87 (10.2%); £3,780,584.62 -> £3,395,576.88 (10.2%); £3,780,584.78 -> £3,395,576.90 (10.2%); £3,780,584.93 -> £3,395,576.92 (10.2%); £3,780,585.08 -> £3,395,576.93 (10.2%); £3,780,585.24 -> £3,395,576.95 (10.2%); £3,780,585.39 -> £3,395,576.97 (10.2%); £3,780,585.54 -> £3,395,576.98 (10.2%); £3,780,585.70 -> £3,395,577.19 (10.2%); £3,780,585.85 -> £3,395,577.39 (10.2%); £3,780,586.01 -> £3,395,577.60 (10.2%); £3,780,586.19 -> £3,395,577.82 (10.2%); £3,780,586.39 -> £3,395,578.03 (10.2%); £3,780,586.62 -> £3,395,578.24 (10.2%); £3,780,586.85 -> £3,395,578.45 (10.2%); £3,780,587.10 -> £3,395,578.66 (10.2%); £3,780,587.35 -> £3,395,578.69 (10.2%); £3,780,587.60 -> £3,395,578.71 (10.2%); £3,780,587.86 -> £3,395,578.73 (10.2%); £3,780,588.11 -> £3,395,578.76 (10.2%); £3,780,588.37 -> £3,395,578.78 (10.2%); £3,780,588.63 -> £3,395,578.81 (10.2%); £3,780,588.88 -> £3,395,578.83 (10.2%); £3,780,589.15 -> £3,395,578.85 (10.2%); £3,780,589.40 -> £3,395,578.88 (10.2%); £3,780,589.66 -> £3,395,578.90 (10.2%); £3,780,589.91 -> £3,395,578.92 (10.2%); £3,780,590.16 -> £3,395,578.95 (10.2%); £3,780,590.41 -> £3,395,578.98 (10.2%); £3,780,590.60 -> £3,395,579.18 (10.2%); £3,780,590.79 -> £3,395,579.39 (10.2%); £3,780,591.03 -> £3,395,579.60 (10.2%); £3,780,591.22 -> £3,395,579.81 (10.2%); £3,780,591.42 -> £3,395,580.02 (10.2%); £3,780,591.68 -> £3,395,580.24 (10.2%); £3,780,591.93 -> £3,395,580.45 (10.2%); £3,780,592.18 -> £3,395,580.66 (10.2%); £3,780,592.44 -> £3,395,580.87 (10.2%); £3,780,592.70 -> £3,395,581.08 (10.2%); £3,780,592.96 -> £3,395,581.29 (10.2%); £3,780,593.21 -> £3,395,581.32 (10.2%); £3,780,593.46 -> £3,395,581.35 (10.2%); £3,780,593.69 -> £3,395,581.37 (10.2%); £3,780,593.90 -> £3,395,581.39 (10.2%); £3,780,594.10 -> £3,395,581.41 (10.2%); £3,780,594.26 -> £3,395,581.43 (10.2%); £3,780,594.41 -> £3,395,581.45 (10.2%); £3,780,594.56 -> £3,395,581.47 (10.2%); £3,780,594.71 -> £3,395,581.48 (10.2%); £3,780,594.86 -> £3,395,581.50 (10.2%); £3,780,595.02 -> £3,395,581.52 (10.2%); £3,780,595.16 -> £3,395,581.53 (10.2%); £3,780,595.32 -> £3,395,581.55 (10.2%); £3,780,595.47 -> £3,395,581.57 (10.2%); £3,780,595.62 -> £3,395,581.58 (10.2%); £3,780,595.77 -> £3,395,581.60 (10.2%); £3,780,595.92 -> £3,395,581.78 (10.2%); £3,780,596.07 -> £3,395,581.95 (10.2%); £3,780,596.24 -> £3,395,582.13 (10.2%); £3,780,596.42 -> £3,395,582.31 (10.2%); £3,780,596.62 -> £3,395,582.48 (10.2%); £3,780,596.84 -> £3,395,582.66 (10.2%); £3,780,597.09 -> £3,395,582.84 (10.2%); £3,780,597.33 -> £3,395,583.02 (10.2%); £3,780,597.58 -> £3,395,583.04 (10.2%); £3,780,597.83 -> £3,395,583.06 (10.2%); £3,780,598.09 -> £3,395,583.09 (10.2%); £3,780,598.34 -> £3,395,583.11 (10.2%); £3,780,598.59 -> £3,395,583.13 (10.2%); £3,780,598.84 -> £3,395,583.16 (10.2%); £3,780,599.11 -> £3,395,583.18 (10.2%); £3,780,599.36 -> £3,395,583.20 (10.2%); £3,780,599.61 -> £3,395,583.23 (10.2%); £3,780,599.87 -> £3,395,583.25 (10.2%); £3,780,600.12 -> £3,395,583.27 (10.2%); £3,780,600.37 -> £3,395,583.30 (10.2%); £3,780,600.61 -> £3,395,583.33 (10.2%); £3,780,600.86 -> £3,395,583.50 (10.2%); £3,780,601.05 -> £3,395,583.70 (10.2%); £3,780,601.30 -> £3,395,583.89 (10.2%); £3,780,601.56 -> £3,395,584.08 (10.2%); £3,780,601.75 -> £3,395,584.27 (10.2%); £3,780,602.00 -> £3,395,584.46 (10.2%); £3,780,602.18 -> £3,395,584.64 (10.2%); £3,780,602.43 -> £3,395,584.83 (10.2%); £3,780,602.68 -> £3,395,585.02 (10.2%); £3,780,602.94 -> £3,395,585.21 (10.2%); £3,780,603.18 -> £3,395,585.39 (10.2%); £3,780,603.43 -> £3,395,585.42 (10.2%); £3,780,603.68 -> £3,395,585.45 (10.2%); £3,780,603.92 -> £3,395,585.47 (10.2%); £3,780,604.13 -> £3,395,585.50 (10.2%); £3,780,604.32 -> £3,395,585.52 (10.2%); £3,780,604.48 -> £3,395,585.53 (10.2%); £3,780,604.63 -> £3,395,585.55 (10.2%); £3,780,604.77 -> £3,395,585.57 (10.2%); £3,780,604.92 -> £3,395,585.59 (10.2%); £3,780,605.07 -> £3,395,585.60 (10.2%); £3,780,605.23 -> £3,395,585.62 (10.2%); £3,780,605.38 -> £3,395,585.64 (10.2%); £3,780,605.53 -> £3,395,585.65 (10.2%); £3,780,605.68 -> £3,395,585.67 (10.2%); £3,780,605.82 -> £3,395,585.69 (10.2%); £3,780,605.97 -> £3,395,585.70 (10.2%); £3,780,606.12 -> £3,395,585.87 (10.2%); £3,780,606.27 -> £3,395,586.03 (10.2%); £3,780,606.44 -> £3,395,586.18 (10.2%); £3,780,606.62 -> £3,395,586.35 (10.2%); £3,780,606.82 -> £3,395,586.51 (10.2%); £3,780,607.03 -> £3,395,586.68 (10.2%); £3,780,607.25 -> £3,395,586.84 (10.2%); £3,780,607.51 -> £3,395,587.00 (10.2%); £3,780,607.76 -> £3,395,587.02 (10.2%); £3,780,608.01 -> £3,395,587.05 (10.2%); £3,780,608.26 -> £3,395,587.07 (10.2%); £3,780,608.52 -> £3,395,587.09 (10.2%); £3,780,608.76 -> £3,395,587.12 (10.2%); £3,780,609.01 -> £3,395,587.14 (10.2%); £3,780,609.25 -> £3,395,587.17 (10.2%); £3,780,609.49 -> £3,395,587.19 (10.2%); £3,780,609.74 -> £3,395,587.21 (10.2%); £3,780,609.99 -> £3,395,587.23 (10.2%); £3,780,610.24 -> £3,395,587.26 (10.2%); £3,780,610.49 -> £3,395,587.28 (10.2%); £3,780,610.74 -> £3,395,587.31 (10.2%); £3,780,610.93 -> £3,395,587.48 (10.2%); £3,780,611.11 -> £3,395,587.65 (10.2%); £3,780,611.30 -> £3,395,587.82 (10.2%); £3,780,611.48 -> £3,395,587.99 (10.2%); £3,780,611.67 -> £3,395,588.16 (10.2%); £3,780,611.85 -> £3,395,588.34 (10.2%); £3,780,612.03 -> £3,395,588.51 (10.2%); £3,780,612.28 -> £3,395,588.68 (10.2%); £3,780,612.53 -> £3,395,588.85 (10.2%); £3,780,612.78 -> £3,395,589.02 (10.2%); £3,780,613.03 -> £3,395,589.18 (10.2%); £3,780,613.28 -> £3,395,589.21 (10.2%); £3,780,613.53 -> £3,395,589.24 (10.2%); £3,780,613.76 -> £3,395,589.26 (10.2%); £3,780,613.97 -> £3,395,589.29 (10.2%); £3,780,614.16 -> £3,395,589.31 (10.2%); £3,780,614.31 -> £3,395,589.32 (10.2%); £3,780,614.46 -> £3,395,589.34 (10.2%); £3,780,614.61 -> £3,395,589.36 (10.2%); £3,780,614.75 -> £3,395,589.38 (10.2%); £3,780,614.90 -> £3,395,589.39 (10.2%); £3,780,615.04 -> £3,395,589.41 (10.2%); £3,780,615.19 -> £3,395,589.43 (10.2%); £3,780,615.34 -> £3,395,589.44 (10.2%); £3,780,615.49 -> £3,395,589.46 (10.2%); £3,780,615.64 -> £3,395,589.48 (10.2%); £3,780,615.79 -> £3,395,589.49 (10.2%); £3,780,615.93 -> £3,395,589.67 (10.2%); £3,780,616.09 -> £3,395,589.85 (10.2%); £3,780,616.25 -> £3,395,590.04 (10.2%); £3,780,616.43 -> £3,395,590.22 (10.2%); £3,780,616.63 -> £3,395,590.41 (10.2%); £3,780,616.84 -> £3,395,590.59 (10.2%); £3,780,617.07 -> £3,395,590.77 (10.2%); £3,780,617.31 -> £3,395,590.95 (10.2%); £3,780,617.55 -> £3,395,590.97 (10.2%); £3,780,617.79 -> £3,395,590.99 (10.2%); £3,780,618.04 -> £3,395,591.02 (10.2%); £3,780,618.28 -> £3,395,591.04 (10.2%); £3,780,618.53 -> £3,395,591.06 (10.2%); £3,780,618.78 -> £3,395,591.09 (10.2%); £3,780,619.02 -> £3,395,591.11 (10.2%); £3,780,619.27 -> £3,395,591.13 (10.2%); £3,780,619.51 -> £3,395,591.16 (10.2%); £3,780,619.74 -> £3,395,591.18 (10.2%); £3,780,620.00 -> £3,395,591.20 (10.2%); £3,780,620.24 -> £3,395,591.23 (10.2%); £3,780,620.48 -> £3,395,591.26 (10.2%); £3,780,620.67 -> £3,395,591.44 (10.2%); £3,780,620.85 -> £3,395,591.62 (10.2%); £3,780,621.03 -> £3,395,591.81 (10.2%); £3,780,621.22 -> £3,395,592.00 (10.2%); £3,780,621.40 -> £3,395,592.19 (10.2%); £3,780,621.58 -> £3,395,592.38 (10.2%); £3,780,621.77 -> £3,395,592.57 (10.2%); £3,780,622.01 -> £3,395,592.75 (10.2%); £3,780,622.25 -> £3,395,592.94 (10.2%); £3,780,622.50 -> £3,395,593.13 (10.2%); £3,780,622.74 -> £3,395,593.32 (10.2%); £3,780,623.00 -> £3,395,593.34 (10.2%); £3,780,623.25 -> £3,395,593.37 (10.2%); £3,780,623.48 -> £3,395,593.40 (10.2%); £3,780,623.69 -> £3,395,593.42 (10.2%); £3,780,623.88 -> £3,395,593.44 (10.2%); £3,780,624.01 -> £3,395,593.46 (10.2%); £3,780,624.14 -> £3,395,593.48 (10.2%); £3,780,624.27 -> £3,395,593.49 (10.2%); £3,780,624.40 -> £3,395,593.51 (10.2%); £3,780,624.53 -> £3,395,593.53 (10.2%); £3,780,624.66 -> £3,395,593.54 (10.2%); £3,780,624.79 -> £3,395,593.56 (10.2%); £3,780,624.92 -> £3,395,593.58 (10.2%); £3,780,625.04 -> £3,395,593.59 (10.2%); £3,780,625.17 -> £3,395,593.61 (10.2%); £3,780,625.30 -> £3,395,593.63 (10.2%); £3,780,625.43 -> £3,395,593.80 (10.2%); £3,780,625.55 -> £3,395,593.97 (10.2%); £3,780,625.69 -> £3,395,594.15 (10.2%); £3,780,625.85 -> £3,395,594.32 (10.2%); £3,780,626.03 -> £3,395,594.50 (10.2%); £3,780,626.21 -> £3,395,594.67 (10.2%); £3,780,626.41 -> £3,395,594.85 (10.2%); £3,780,626.62 -> £3,395,595.03 (10.2%); £3,780,626.83 -> £3,395,595.05 (10.2%); £3,780,627.03 -> £3,395,595.08 (10.2%); £3,780,627.25 -> £3,395,595.11 (10.2%); £3,780,627.46 -> £3,395,595.13 (10.2%); £3,780,627.67 -> £3,395,595.16 (10.2%); £3,780,627.89 -> £3,395,595.19 (10.2%); £3,780,628.10 -> £3,395,595.21 (10.2%); £3,780,628.31 -> £3,395,595.24 (10.2%); £3,780,628.52 -> £3,395,595.26 (10.2%); £3,780,628.73 -> £3,395,595.29 (10.2%); £3,780,628.95 -> £3,395,595.31 (10.2%); £3,780,629.16 -> £3,395,595.34 (10.2%); £3,780,629.38 -> £3,395,595.37 (10.2%); £3,780,629.53 -> £3,395,595.54 (10.2%); £3,780,629.70 -> £3,395,595.71 (10.2%); £3,780,629.86 -> £3,395,595.89 (10.2%); £3,780,630.02 -> £3,395,596.07 (10.2%); £3,780,630.18 -> £3,395,596.26 (10.2%); £3,780,630.33 -> £3,395,596.44 (10.2%); £3,780,630.54 -> £3,395,596.63 (10.2%); £3,780,630.76 -> £3,395,596.80 (10.2%); £3,780,630.97 -> £3,395,596.99 (10.2%); £3,780,631.19 -> £3,395,597.17 (10.2%); £3,780,631.39 -> £3,395,597.34 (10.2%); £3,780,631.61 -> £3,395,597.37 (10.2%); £3,780,631.82 -> £3,395,597.40 (10.2%); £3,780,632.02 -> £3,395,597.42 (10.2%); £3,780,632.20 -> £3,395,597.45 (10.2%); £3,780,632.36 -> £3,395,597.47 (10.2%); £3,780,632.48 -> £3,395,597.49 (10.2%); £3,780,632.61 -> £3,395,597.51 (10.2%); £3,780,632.74 -> £3,395,597.53 (10.2%); £3,780,632.86 -> £3,395,597.55 (10.2%); £3,780,632.99 -> £3,395,597.56 (10.2%); £3,780,633.12 -> £3,395,597.58 (10.2%); £3,780,633.24 -> £3,395,597.60 (10.2%); £3,780,633.37 -> £3,395,597.61 (10.2%); £3,780,633.50 -> £3,395,597.63 (10.2%); £3,780,633.62 -> £3,395,597.65 (10.2%); £3,780,633.75 -> £3,395,597.66 (10.2%); £3,780,633.87 -> £3,395,597.87 (10.2%); £3,780,634.00 -> £3,395,598.09 (10.2%); £3,780,634.14 -> £3,395,598.30 (10.2%); £3,780,634.30 -> £3,395,598.52 (10.2%); £3,780,634.47 -> £3,395,598.73 (10.2%); £3,780,634.66 -> £3,395,598.95 (10.2%); £3,780,634.85 -> £3,395,599.17 (10.2%); £3,780,635.06 -> £3,395,599.39 (10.2%); £3,780,635.27 -> £3,395,599.42 (10.2%); £3,780,635.48 -> £3,395,599.45 (10.2%); £3,780,635.69 -> £3,395,599.48 (10.2%); £3,780,635.90 -> £3,395,599.51 (10.2%); £3,780,636.12 -> £3,395,599.54 (10.2%); £3,780,636.33 -> £3,395,599.57 (10.2%); £3,780,636.54 -> £3,395,599.60 (10.2%); £3,780,636.75 -> £3,395,599.63 (10.2%); £3,780,636.96 -> £3,395,599.66 (10.2%); £3,780,637.17 -> £3,395,599.69 (10.2%); £3,780,637.38 -> £3,395,599.72 (10.2%); £3,780,637.59 -> £3,395,599.74 (10.2%); £3,780,637.80 -> £3,395,599.77 (10.2%); £3,780,637.96 -> £3,395,599.98 (10.2%); £3,780,638.12 -> £3,395,600.20 (10.2%); £3,780,638.28 -> £3,395,600.42 (10.2%); £3,780,638.44 -> £3,395,600.64 (10.2%); £3,780,638.60 -> £3,395,600.86 (10.2%); £3,780,638.76 -> £3,395,601.07 (10.2%); £3,780,638.92 -> £3,395,601.29 (10.2%); £3,780,639.14 -> £3,395,601.50 (10.2%); £3,780,639.36 -> £3,395,601.72 (10.2%); £3,780,639.56 -> £3,395,601.94 (10.2%); £3,780,639.77 -> £3,395,602.16 (10.2%); £3,780,639.98 -> £3,395,602.19 (10.2%); £3,780,640.19 -> £3,395,602.22 (10.2%); £3,780,640.39 -> £3,395,602.24 (10.2%); £3,780,640.57 -> £3,395,602.27 (10.2%); £3,780,640.74 -> £3,395,602.28 (10.2%); £3,780,640.88 -> £3,395,602.30 (10.2%); £3,780,641.03 -> £3,395,602.32 (10.2%); £3,780,641.18 -> £3,395,602.34 (10.2%); £3,780,641.33 -> £3,395,602.36 (10.2%); £3,780,641.47 -> £3,395,602.37 (10.2%); £3,780,641.62 -> £3,395,602.39 (10.2%); £3,780,641.76 -> £3,395,602.41 (10.2%); £3,780,641.91 -> £3,395,602.42 (10.2%); £3,780,642.05 -> £3,395,602.44 (10.2%); £3,780,642.20 -> £3,395,602.46 (10.2%); £3,780,642.34 -> £3,395,602.47 (10.2%); £3,780,642.48 -> £3,395,602.72 (10.2%); £3,780,642.63 -> £3,395,602.97 (10.2%); £3,780,642.79 -> £3,395,603.22 (10.2%); £3,780,642.96 -> £3,395,603.48 (10.2%); £3,780,643.15 -> £3,395,603.73 (10.2%); £3,780,643.36 -> £3,395,603.99 (10.2%); £3,780,643.58 -> £3,395,604.24 (10.2%); £3,780,643.82 -> £3,395,604.49 (10.2%); £3,780,644.06 -> £3,395,604.51 (10.2%); £3,780,644.30 -> £3,395,604.54 (10.2%); £3,780,644.55 -> £3,395,604.56 (10.2%); £3,780,644.79 -> £3,395,604.58 (10.2%); £3,780,645.04 -> £3,395,604.61 (10.2%); £3,780,645.28 -> £3,395,604.63 (10.2%); £3,780,645.52 -> £3,395,604.66 (10.2%); £3,780,645.76 -> £3,395,604.68 (10.2%); £3,780,646.00 -> £3,395,604.70 (10.2%); £3,780,646.25 -> £3,395,604.73 (10.2%); £3,780,646.49 -> £3,395,604.75 (10.2%); £3,780,646.73 -> £3,395,604.78 (10.2%); £3,780,646.97 -> £3,395,604.80 (10.2%); £3,780,647.16 -> £3,395,605.05 (10.2%); £3,780,647.34 -> £3,395,605.30 (10.2%); £3,780,647.53 -> £3,395,605.54 (10.2%); £3,780,647.71 -> £3,395,605.79 (10.2%); £3,780,647.89 -> £3,395,606.04 (10.2%); £3,780,648.07 -> £3,395,606.29 (10.2%); £3,780,648.24 -> £3,395,606.55 (10.2%); £3,780,648.48 -> £3,395,606.80 (10.2%); £3,780,648.72 -> £3,395,607.05 (10.2%); £3,780,648.96 -> £3,395,607.31 (10.2%); £3,780,649.20 -> £3,395,607.57 (10.2%); £3,780,649.45 -> £3,395,607.59 (10.2%); £3,780,649.69 -> £3,395,607.62 (10.2%); £3,780,649.91 -> £3,395,607.65 (10.2%); £3,780,650.12 -> £3,395,607.67 (10.2%); £3,780,650.31 -> £3,395,607.69 (10.2%); £3,780,650.45 -> £3,395,607.71 (10.2%); £3,780,650.59 -> £3,395,607.72 (10.2%); £3,780,650.74 -> £3,395,607.74 (10.2%); £3,780,650.88 -> £3,395,607.76 (10.2%); £3,780,651.02 -> £3,395,607.77 (10.2%); £3,780,651.16 -> £3,395,607.79 (10.2%); £3,780,651.30 -> £3,395,607.81 (10.2%); £3,780,651.44 -> £3,395,607.82 (10.2%); £3,780,651.59 -> £3,395,607.84 (10.2%); £3,780,651.73 -> £3,395,607.86 (10.2%); £3,780,651.87 -> £3,395,607.88 (10.2%); £3,780,652.02 -> £3,395,608.10 (10.2%); £3,780,652.17 -> £3,395,608.32 (10.2%); £3,780,652.33 -> £3,395,608.54 (10.2%); £3,780,652.50 -> £3,395,608.77 (10.2%); £3,780,652.69 -> £3,395,608.99 (10.2%); £3,780,652.91 -> £3,395,609.21 (10.2%); £3,780,653.13 -> £3,395,609.43 (10.2%); £3,780,653.38 -> £3,395,609.65 (10.2%); £3,780,653.62 -> £3,395,609.68 (10.2%); £3,780,653.85 -> £3,395,609.70 (10.2%); £3,780,654.09 -> £3,395,609.72 (10.2%); £3,780,654.32 -> £3,395,609.75 (10.2%); £3,780,654.56 -> £3,395,609.77 (10.2%); £3,780,654.80 -> £3,395,609.80 (10.2%); £3,780,655.04 -> £3,395,609.82 (10.2%); £3,780,655.27 -> £3,395,609.84 (10.2%); £3,780,655.51 -> £3,395,609.87 (10.2%); £3,780,655.74 -> £3,395,609.89 (10.2%); £3,780,655.98 -> £3,395,609.91 (10.2%); £3,780,656.21 -> £3,395,609.94 (10.2%); £3,780,656.45 -> £3,395,609.97 (10.2%); £3,780,656.64 -> £3,395,610.19 (10.2%); £3,780,656.82 -> £3,395,610.42 (10.2%); £3,780,657.01 -> £3,395,610.66 (10.2%); £3,780,657.26 -> £3,395,610.90 (10.2%); £3,780,657.50 -> £3,395,611.13 (10.2%); £3,780,657.75 -> £3,395,611.37 (10.2%); £3,780,657.93 -> £3,395,611.60 (10.2%); £3,780,658.17 -> £3,395,611.83 (10.2%); £3,780,658.41 -> £3,395,612.05 (10.2%); £3,780,658.65 -> £3,395,612.27 (10.2%); £3,780,658.89 -> £3,395,612.49 (10.2%); £3,780,659.14 -> £3,395,612.52 (10.2%); £3,780,659.38 -> £3,395,612.55 (10.2%); £3,780,659.60 -> £3,395,612.57 (10.2%); £3,780,659.80 -> £3,395,612.60 (10.2%); £3,780,659.98 -> £3,395,612.62 (10.2%); £3,780,660.12 -> £3,395,612.63 (10.2%); £3,780,660.26 -> £3,395,612.65 (10.2%); £3,780,660.40 -> £3,395,612.67 (10.2%); £3,780,660.54 -> £3,395,612.69 (10.2%); £3,780,660.68 -> £3,395,612.70 (10.2%); £3,780,660.83 -> £3,395,612.72 (10.2%); £3,780,660.97 -> £3,395,612.74 (10.2%); £3,780,661.11 -> £3,395,612.75 (10.2%); £3,780,661.25 -> £3,395,612.77 (10.2%); £3,780,661.39 -> £3,395,612.79 (10.2%); £3,780,661.53 -> £3,395,612.80 (10.2%); £3,780,661.67 -> £3,395,613.04 (10.2%); £3,780,661.82 -> £3,395,613.29 (10.2%); £3,780,661.97 -> £3,395,613.54 (10.2%); £3,780,662.15 -> £3,395,613.79 (10.2%); £3,780,662.34 -> £3,395,614.03 (10.2%); £3,780,662.54 -> £3,395,614.28 (10.2%); £3,780,662.76 -> £3,395,614.53 (10.2%); £3,780,663.00 -> £3,395,614.77 (10.2%); £3,780,663.23 -> £3,395,614.80 (10.2%); £3,780,663.47 -> £3,395,614.82 (10.2%); £3,780,663.71 -> £3,395,614.85 (10.2%); £3,780,663.94 -> £3,395,614.87 (10.2%); £3,780,664.18 -> £3,395,614.89 (10.2%); £3,780,664.42 -> £3,395,614.92 (10.2%); £3,780,664.65 -> £3,395,614.94 (10.2%); £3,780,664.89 -> £3,395,614.96 (10.2%); £3,780,665.13 -> £3,395,614.99 (10.2%); £3,780,665.37 -> £3,395,615.01 (10.2%); £3,780,665.61 -> £3,395,615.03 (10.2%); £3,780,665.85 -> £3,395,615.06 (10.2%); £3,780,666.08 -> £3,395,615.08 (10.2%); £3,780,666.26 -> £3,395,615.32 (10.2%); £3,780,666.44 -> £3,395,615.57 (10.2%); £3,780,666.67 -> £3,395,615.82 (10.2%); £3,780,666.91 -> £3,395,616.07 (10.2%); £3,780,667.15 -> £3,395,616.32 (10.2%); £3,780,667.39 -> £3,395,616.57 (10.2%); £3,780,667.63 -> £3,395,616.82 (10.2%); £3,780,667.88 -> £3,395,617.07 (10.2%); £3,780,668.11 -> £3,395,617.31 (10.2%); £3,780,668.35 -> £3,395,617.55 (10.2%); £3,780,668.59 -> £3,395,617.78 (10.2%); £3,780,668.82 -> £3,395,617.81 (10.2%); £3,780,669.05 -> £3,395,617.84 (10.2%); £3,780,669.26 -> £3,395,617.86 (10.2%); £3,780,669.46 -> £3,395,617.88 (10.2%); £3,780,669.64 -> £3,395,617.90 (10.2%); £3,780,669.78 -> £3,395,617.92 (10.2%); £3,780,669.92 -> £3,395,617.94 (10.2%); £3,780,670.06 -> £3,395,617.96 (10.2%); £3,780,670.21 -> £3,395,617.97 (10.2%); £3,780,670.34 -> £3,395,617.99 (10.2%); £3,780,670.48 -> £3,395,618.01 (10.2%); £3,780,670.62 -> £3,395,618.02 (10.2%); £3,780,670.77 -> £3,395,618.04 (10.2%); £3,780,670.92 -> £3,395,618.05 (10.2%); £3,780,671.06 -> £3,395,618.07 (10.2%); £3,780,671.20 -> £3,395,618.09 (10.2%); £3,780,671.35 -> £3,395,618.35 (10.2%); £3,780,671.49 -> £3,395,618.62 (10.2%); £3,780,671.65 -> £3,395,618.89 (10.2%); £3,780,671.82 -> £3,395,619.16 (10.2%); £3,780,672.01 -> £3,395,619.43 (10.2%); £3,780,672.21 -> £3,395,619.70 (10.2%); £3,780,672.43 -> £3,395,619.97 (10.2%); £3,780,672.67 -> £3,395,620.23 (10.2%); £3,780,672.90 -> £3,395,620.26 (10.2%); £3,780,673.14 -> £3,395,620.28 (10.2%); £3,780,673.36 -> £3,395,620.31 (10.2%); £3,780,673.60 -> £3,395,620.33 (10.2%); £3,780,673.82 -> £3,395,620.35 (10.2%); £3,780,674.07 -> £3,395,620.38 (10.2%); £3,780,674.31 -> £3,395,620.40 (10.2%); £3,780,674.55 -> £3,395,620.42 (10.2%); £3,780,674.78 -> £3,395,620.45 (10.2%); £3,780,675.02 -> £3,395,620.47 (10.2%); £3,780,675.25 -> £3,395,620.49 (10.2%); £3,780,675.49 -> £3,395,620.52 (10.2%); £3,780,675.72 -> £3,395,620.55 (10.2%); £3,780,675.91 -> £3,395,620.81 (10.2%); £3,780,676.08 -> £3,395,621.09 (10.2%); £3,780,676.26 -> £3,395,621.36 (10.2%); £3,780,676.43 -> £3,395,621.63 (10.2%); £3,780,676.61 -> £3,395,621.91 (10.2%); £3,780,676.79 -> £3,395,622.18 (10.2%); £3,780,676.97 -> £3,395,622.45 (10.2%); £3,780,677.19 -> £3,395,622.71 (10.2%); £3,780,677.43 -> £3,395,622.98 (10.2%); £3,780,677.67 -> £3,395,623.25 (10.2%); £3,780,677.89 -> £3,395,623.52 (10.2%); £3,780,678.13 -> £3,395,623.55 (10.2%); £3,780,678.37 -> £3,395,623.58 (10.2%); £3,780,678.59 -> £3,395,623.61 (10.2%); £3,780,678.80 -> £3,395,623.63 (10.2%); £3,780,678.98 -> £3,395,623.65 (10.2%); £3,780,679.13 -> £3,395,623.67 (10.2%); £3,780,679.27 -> £3,395,623.68 (10.2%); £3,780,679.42 -> £3,395,623.70 (10.2%); £3,780,679.56 -> £3,395,623.72 (10.2%); £3,780,679.70 -> £3,395,623.74 (10.2%); £3,780,679.84 -> £3,395,623.75 (10.2%); £3,780,679.99 -> £3,395,623.77 (10.2%); £3,780,680.13 -> £3,395,623.79 (10.2%); £3,780,680.27 -> £3,395,623.80 (10.2%); £3,780,680.42 -> £3,395,623.82 (10.2%); £3,780,680.56 -> £3,395,623.84 (10.2%); £3,780,680.70 -> £3,395,624.06 (10.2%); £3,780,680.85 -> £3,395,624.29 (10.2%); £3,780,681.01 -> £3,395,624.51 (10.2%); £3,780,681.19 -> £3,395,624.75 (10.2%); £3,780,681.37 -> £3,395,624.98 (10.2%); £3,780,681.58 -> £3,395,625.21 (10.2%); £3,780,681.80 -> £3,395,625.44 (10.2%); £3,780,682.04 -> £3,395,625.67 (10.2%); £3,780,682.27 -> £3,395,625.69 (10.2%); £3,780,682.50 -> £3,395,625.71 (10.2%); £3,780,682.74 -> £3,395,625.74 (10.2%); £3,780,682.98 -> £3,395,625.76 (10.2%); £3,780,683.23 -> £3,395,625.79 (10.2%); £3,780,683.46 -> £3,395,625.81 (10.2%); £3,780,683.71 -> £3,395,625.83 (10.2%); £3,780,683.94 -> £3,395,625.86 (10.2%); £3,780,684.17 -> £3,395,625.88 (10.2%); £3,780,684.41 -> £3,395,625.90 (10.2%); £3,780,684.65 -> £3,395,625.93 (10.2%); £3,780,684.89 -> £3,395,625.95 (10.2%); £3,780,685.13 -> £3,395,625.98 (10.2%); £3,780,685.36 -> £3,395,626.21 (10.2%); £3,780,685.54 -> £3,395,626.44 (10.2%); £3,780,685.71 -> £3,395,626.68 (10.2%); £3,780,685.89 -> £3,395,626.91 (10.2%); £3,780,686.07 -> £3,395,627.15 (10.2%); £3,780,686.32 -> £3,395,627.39 (10.2%); £3,780,686.56 -> £3,395,627.62 (10.2%); £3,780,686.80 -> £3,395,627.86 (10.2%); £3,780,687.05 -> £3,395,628.09 (10.2%); £3,780,687.29 -> £3,395,628.32 (10.2%); £3,780,687.53 -> £3,395,628.54 (10.2%); £3,780,687.77 -> £3,395,628.57 (10.2%); £3,780,688.01 -> £3,395,628.60 (10.2%); £3,780,688.23 -> £3,395,628.63 (10.2%); £3,780,688.44 -> £3,395,628.65 (10.2%); £3,780,688.63 -> £3,395,628.67 (10.2%); £3,780,688.76 -> £3,395,628.69 (10.2%); £3,780,688.88 -> £3,395,628.71 (10.2%); £3,780,689.01 -> £3,395,628.72 (10.2%); £3,780,689.14 -> £3,395,628.74 (10.2%); £3,780,689.27 -> £3,395,628.76 (10.2%); £3,780,689.40 -> £3,395,628.78 (10.2%); £3,780,689.53 -> £3,395,628.79 (10.2%); £3,780,689.65 -> £3,395,628.81 (10.2%); £3,780,689.78 -> £3,395,628.83 (10.2%); £3,780,689.91 -> £3,395,628.84 (10.2%); £3,780,690.03 -> £3,395,628.86 (10.2%); £3,780,690.17 -> £3,395,629.03 (10.2%); £3,780,690.30 -> £3,395,629.21 (10.2%); £3,780,690.44 -> £3,395,629.39 (10.2%); £3,780,690.60 -> £3,395,629.57 (10.2%); £3,780,690.77 -> £3,395,629.75 (10.2%); £3,780,690.96 -> £3,395,629.93 (10.2%); £3,780,691.16 -> £3,395,630.12 (10.2%); £3,780,691.37 -> £3,395,630.30 (10.2%); £3,780,691.59 -> £3,395,630.33 (10.2%); £3,780,691.81 -> £3,395,630.35 (10.2%); £3,780,692.02 -> £3,395,630.38 (10.2%); £3,780,692.23 -> £3,395,630.41 (10.2%); £3,780,692.44 -> £3,395,630.43 (10.2%); £3,780,692.66 -> £3,395,630.46 (10.2%); £3,780,692.87 -> £3,395,630.49 (10.2%); £3,780,693.09 -> £3,395,630.51 (10.2%); £3,780,693.30 -> £3,395,630.54 (10.2%); £3,780,693.52 -> £3,395,630.56 (10.2%); £3,780,693.73 -> £3,395,630.59 (10.2%); £3,780,693.94 -> £3,395,630.61 (10.2%); £3,780,694.16 -> £3,395,630.64 (10.2%); £3,780,694.32 -> £3,395,630.82 (10.2%); £3,780,694.48 -> £3,395,631.01 (10.2%); £3,780,694.65 -> £3,395,631.19 (10.2%); £3,780,694.81 -> £3,395,631.38 (10.2%); £3,780,694.97 -> £3,395,631.57 (10.2%); £3,780,695.14 -> £3,395,631.76 (10.2%); £3,780,695.30 -> £3,395,631.94 (10.2%); £3,780,695.51 -> £3,395,632.13 (10.2%); £3,780,695.72 -> £3,395,632.31 (10.2%); £3,780,695.94 -> £3,395,632.49 (10.2%); £3,780,696.15 -> £3,395,632.67 (10.2%); £3,780,696.37 -> £3,395,632.70 (10.2%); £3,780,696.58 -> £3,395,632.73 (10.2%); £3,780,696.78 -> £3,395,632.75 (10.2%); £3,780,696.97 -> £3,395,632.78 (10.2%); £3,780,697.13 -> £3,395,632.80 (10.2%); £3,780,697.26 -> £3,395,632.82 (10.2%); £3,780,697.39 -> £3,395,632.84 (10.2%); £3,780,697.52 -> £3,395,632.86 (10.2%); £3,780,697.65 -> £3,395,632.87 (10.2%); £3,780,697.78 -> £3,395,632.89 (10.2%); £3,780,697.91 -> £3,395,632.91 (10.2%); £3,780,698.03 -> £3,395,632.92 (10.2%); £3,780,698.16 -> £3,395,632.94 (10.2%); £3,780,698.29 -> £3,395,632.96 (10.2%); £3,780,698.41 -> £3,395,632.97 (10.2%); £3,780,698.55 -> £3,395,632.99 (10.2%); £3,780,698.68 -> £3,395,633.10 (10.2%); £3,780,698.80 -> £3,395,633.22 (10.2%); £3,780,698.95 -> £3,395,633.33 (10.2%); £3,780,699.11 -> £3,395,633.44 (10.2%); £3,780,699.28 -> £3,395,633.56 (10.2%); £3,780,699.46 -> £3,395,633.68 (10.2%); £3,780,699.67 -> £3,395,633.81 (10.2%); £3,780,699.89 -> £3,395,633.93 (10.2%); £3,780,700.10 -> £3,395,633.96 (10.2%); £3,780,700.32 -> £3,395,633.99 (10.2%); £3,780,700.54 -> £3,395,634.02 (10.2%); £3,780,700.75 -> £3,395,634.05 (10.2%); £3,780,700.96 -> £3,395,634.08 (10.2%); £3,780,701.18 -> £3,395,634.11 (10.2%); £3,780,701.39 -> £3,395,634.15 (10.2%); £3,780,701.60 -> £3,395,634.17 (10.2%); £3,780,701.82 -> £3,395,634.20 (10.2%); £3,780,702.03 -> £3,395,634.23 (10.2%); £3,780,702.25 -> £3,395,634.26 (10.2%); £3,780,702.47 -> £3,395,634.29 (10.2%); £3,780,702.69 -> £3,395,634.32 (10.2%); £3,780,702.85 -> £3,395,634.44 (10.2%); £3,780,703.01 -> £3,395,634.57 (10.2%); £3,780,703.16 -> £3,395,634.71 (10.2%); £3,780,703.32 -> £3,395,634.84 (10.2%); £3,780,703.48 -> £3,395,634.97 (10.2%); £3,780,703.65 -> £3,395,635.10 (10.2%); £3,780,703.80 -> £3,395,635.23 (10.2%); £3,780,704.02 -> £3,395,635.36 (10.2%); £3,780,704.23 -> £3,395,635.48 (10.2%); £3,780,704.45 -> £3,395,635.61 (10.2%); £3,780,704.66 -> £3,395,635.73 (10.2%); £3,780,704.87 -> £3,395,635.76 (10.2%); £3,780,705.10 -> £3,395,635.79 (10.2%); £3,780,705.29 -> £3,395,635.81 (10.2%); £3,780,705.47 -> £3,395,635.83 (10.2%); £3,780,705.63 -> £3,395,635.85 (10.2%); £3,780,705.78 -> £3,395,635.87 (10.2%); £3,780,705.92 -> £3,395,635.89 (10.2%); £3,780,706.07 -> £3,395,635.91 (10.2%); £3,780,706.22 -> £3,395,635.92 (10.2%); £3,780,706.36 -> £3,395,635.94 (10.2%); £3,780,706.51 -> £3,395,635.96 (10.2%); £3,780,706.65 -> £3,395,635.97 (10.2%); £3,780,706.81 -> £3,395,635.99 (10.2%); £3,780,706.95 -> £3,395,636.01 (10.2%); £3,780,707.09 -> £3,395,636.02 (10.2%); £3,780,707.24 -> £3,395,636.04 (10.2%); £3,780,707.38 -> £3,395,636.17 (10.2%); £3,780,707.53 -> £3,395,636.30 (10.2%); £3,780,707.69 -> £3,395,636.44 (10.2%); £3,780,707.87 -> £3,395,636.57 (10.2%); £3,780,708.07 -> £3,395,636.71 (10.2%); £3,780,708.28 -> £3,395,636.85 (10.2%); £3,780,708.51 -> £3,395,636.98 (10.2%); £3,780,708.77 -> £3,395,637.12 (10.2%); £3,780,709.01 -> £3,395,637.14 (10.2%); £3,780,709.26 -> £3,395,637.16 (10.2%); £3,780,709.51 -> £3,395,637.19 (10.2%); £3,780,709.75 -> £3,395,637.21 (10.2%); £3,780,710.00 -> £3,395,637.24 (10.2%); £3,780,710.26 -> £3,395,637.26 (10.2%); £3,780,710.50 -> £3,395,637.28 (10.2%); £3,780,710.75 -> £3,395,637.31 (10.2%); £3,780,711.00 -> £3,395,637.33 (10.2%); £3,780,711.25 -> £3,395,637.35 (10.2%); £3,780,711.50 -> £3,395,637.38 (10.2%); £3,780,711.75 -> £3,395,637.40 (10.2%); £3,780,712.00 -> £3,395,637.43 (10.2%); £3,780,712.24 -> £3,395,637.57 (10.2%); £3,780,712.43 -> £3,395,637.72 (10.2%); £3,780,712.60 -> £3,395,637.87 (10.2%); £3,780,712.80 -> £3,395,638.02 (10.2%); £3,780,712.97 -> £3,395,638.16 (10.2%); £3,780,713.15 -> £3,395,638.31 (10.2%); £3,780,713.34 -> £3,395,638.46 (10.2%); £3,780,713.58 -> £3,395,638.60 (10.2%); £3,780,713.82 -> £3,395,638.74 (10.2%); £3,780,714.07 -> £3,395,638.89 (10.2%); £3,780,714.32 -> £3,395,639.03 (10.2%); £3,780,714.56 -> £3,395,639.06 (10.2%); £3,780,714.80 -> £3,395,639.09 (10.2%); £3,780,715.03 -> £3,395,639.11 (10.2%); £3,780,715.24 -> £3,395,639.14 (10.2%); £3,780,715.44 -> £3,395,639.16 (10.2%); £3,780,715.58 -> £3,395,639.18 (10.2%); £3,780,715.73 -> £3,395,639.19 (10.2%); £3,780,715.88 -> £3,395,639.21 (10.2%); £3,780,716.02 -> £3,395,639.23 (10.2%); £3,780,716.17 -> £3,395,639.25 (10.2%); £3,780,716.32 -> £3,395,639.26 (10.2%); £3,780,716.47 -> £3,395,639.28 (10.2%); £3,780,716.62 -> £3,395,639.30 (10.2%); £3,780,716.76 -> £3,395,639.31 (10.2%); £3,780,716.91 -> £3,395,639.33 (10.2%); £3,780,717.06 -> £3,395,639.35 (10.2%); £3,780,717.21 -> £3,395,639.46 (10.2%); £3,780,717.36 -> £3,395,639.59 (10.2%); £3,780,717.52 -> £3,395,639.71 (10.2%); £3,780,717.71 -> £3,395,639.84 (10.2%); £3,780,717.90 -> £3,395,639.97 (10.2%); £3,780,718.12 -> £3,395,640.10 (10.2%); £3,780,718.35 -> £3,395,640.22 (10.2%); £3,780,718.60 -> £3,395,640.34 (10.2%); £3,780,718.85 -> £3,395,640.37 (10.2%); £3,780,719.09 -> £3,395,640.39 (10.2%); £3,780,719.34 -> £3,395,640.42 (10.2%); £3,780,719.58 -> £3,395,640.44 (10.2%); £3,780,719.84 -> £3,395,640.47 (10.2%); £3,780,720.07 -> £3,395,640.49 (10.2%); £3,780,720.32 -> £3,395,640.51 (10.2%); £3,780,720.57 -> £3,395,640.54 (10.2%); £3,780,720.82 -> £3,395,640.56 (10.2%); £3,780,721.06 -> £3,395,640.58 (10.2%); £3,780,721.30 -> £3,395,640.61 (10.2%); £3,780,721.55 -> £3,395,640.63 (10.2%); £3,780,721.80 -> £3,395,640.66 (10.2%); £3,780,721.98 -> £3,395,640.79 (10.2%); £3,780,722.17 -> £3,395,640.93 (10.2%); £3,780,722.43 -> £3,395,641.08 (10.2%); £3,780,722.67 -> £3,395,641.22 (10.2%); £3,780,722.91 -> £3,395,641.36 (10.2%); £3,780,723.16 -> £3,395,641.50 (10.2%); £3,780,723.34 -> £3,395,641.63 (10.2%); £3,780,723.60 -> £3,395,641.76 (10.2%); £3,780,723.85 -> £3,395,641.90 (10.2%); £3,780,724.09 -> £3,395,642.03 (10.2%); £3,780,724.35 -> £3,395,642.16 (10.2%); £3,780,724.59 -> £3,395,642.19 (10.2%); £3,780,724.84 -> £3,395,642.22 (10.2%); £3,780,725.08 -> £3,395,642.24 (10.2%); £3,780,725.28 -> £3,395,642.26 (10.2%); £3,780,725.48 -> £3,395,642.28 (10.2%); £3,780,725.62 -> £3,395,642.30 (10.2%); £3,780,725.77 -> £3,395,642.32 (10.2%); £3,780,725.92 -> £3,395,642.34 (10.2%); £3,780,726.07 -> £3,395,642.36 (10.2%); £3,780,726.21 -> £3,395,642.37 (10.2%); £3,780,726.36 -> £3,395,642.39 (10.2%); £3,780,726.51 -> £3,395,642.41 (10.2%); £3,780,726.66 -> £3,395,642.42 (10.2%); £3,780,726.81 -> £3,395,642.44 (10.2%); £3,780,726.96 -> £3,395,642.46 (10.2%); £3,780,727.11 -> £3,395,642.47 (10.2%); £3,780,727.26 -> £3,395,642.60 (10.2%); £3,780,727.41 -> £3,395,642.72 (10.2%); £3,780,727.59 -> £3,395,642.85 (10.2%); £3,780,727.77 -> £3,395,642.99 (10.2%); £3,780,727.97 -> £3,395,643.12 (10.2%); £3,780,728.18 -> £3,395,643.25 (10.2%); £3,780,728.42 -> £3,395,643.38 (10.2%); £3,780,728.66 -> £3,395,643.51 (10.2%); £3,780,728.92 -> £3,395,643.54 (10.2%); £3,780,729.17 -> £3,395,643.56 (10.2%); £3,780,729.42 -> £3,395,643.59 (10.2%); £3,780,729.67 -> £3,395,643.61 (10.2%); £3,780,729.92 -> £3,395,643.63 (10.2%); £3,780,730.17 -> £3,395,643.66 (10.2%); £3,780,730.42 -> £3,395,643.68 (10.2%); £3,780,730.67 -> £3,395,643.71 (10.2%); £3,780,730.94 -> £3,395,643.73 (10.2%); £3,780,731.19 -> £3,395,643.75 (10.2%); £3,780,731.44 -> £3,395,643.78 (10.2%); £3,780,731.69 -> £3,395,643.80 (10.2%); £3,780,731.95 -> £3,395,643.83 (10.2%); £3,780,732.19 -> £3,395,643.97 (10.2%); £3,780,732.38 -> £3,395,644.11 (10.2%); £3,780,732.57 -> £3,395,644.26 (10.2%); £3,780,732.81 -> £3,395,644.41 (10.2%); £3,780,733.07 -> £3,395,644.56 (10.2%); £3,780,733.32 -> £3,395,644.71 (10.2%); £3,780,733.52 -> £3,395,644.85 (10.2%); £3,780,733.77 -> £3,395,645.00 (10.2%); £3,780,734.03 -> £3,395,645.14 (10.2%); £3,780,734.27 -> £3,395,645.28 (10.2%); £3,780,734.53 -> £3,395,645.42 (10.2%); £3,780,734.78 -> £3,395,645.45 (10.2%); £3,780,735.03 -> £3,395,645.48 (10.2%); £3,780,735.27 -> £3,395,645.50 (10.2%); £3,780,735.48 -> £3,395,645.52 (10.2%); £3,780,735.67 -> £3,395,645.54 (10.2%); £3,780,735.83 -> £3,395,645.56 (10.2%); £3,780,735.98 -> £3,395,645.58 (10.2%); £3,780,736.14 -> £3,395,645.60 (10.2%); £3,780,736.30 -> £3,395,645.62 (10.2%); £3,780,736.45 -> £3,395,645.63 (10.2%); £3,780,736.60 -> £3,395,645.65 (10.2%); £3,780,736.76 -> £3,395,645.67 (10.2%); £3,780,736.92 -> £3,395,645.68 (10.2%); £3,780,737.07 -> £3,395,645.70 (10.2%); £3,780,737.22 -> £3,395,645.72 (10.2%); £3,780,737.37 -> £3,395,645.73 (10.2%); £3,780,737.52 -> £3,395,645.85 (10.2%); £3,780,737.68 -> £3,395,645.96 (10.2%); £3,780,737.85 -> £3,395,646.08 (10.2%); £3,780,738.04 -> £3,395,646.21 (10.2%); £3,780,738.24 -> £3,395,646.33 (10.2%); £3,780,738.46 -> £3,395,646.46 (10.2%); £3,780,738.70 -> £3,395,646.58 (10.2%); £3,780,738.95 -> £3,395,646.70 (10.2%); £3,780,739.21 -> £3,395,646.73 (10.2%); £3,780,739.46 -> £3,395,646.75 (10.2%); £3,780,739.71 -> £3,395,646.78 (10.2%); £3,780,739.96 -> £3,395,646.80 (10.2%); £3,780,740.21 -> £3,395,646.82 (10.2%); £3,780,740.47 -> £3,395,646.85 (10.2%); £3,780,740.74 -> £3,395,646.87 (10.2%); £3,780,740.99 -> £3,395,646.90 (10.2%); £3,780,741.25 -> £3,395,646.92 (10.2%); £3,780,741.51 -> £3,395,646.94 (10.2%); £3,780,741.76 -> £3,395,646.97 (10.2%); £3,780,742.01 -> £3,395,646.99 (10.2%); £3,780,742.27 -> £3,395,647.02 (10.2%); £3,780,742.46 -> £3,395,647.15 (10.2%); £3,780,742.65 -> £3,395,647.29 (10.2%); £3,780,742.84 -> £3,395,647.42 (10.2%); £3,780,743.03 -> £3,395,647.56 (10.2%); £3,780,743.29 -> £3,395,647.70 (10.2%); £3,780,743.54 -> £3,395,647.83 (10.2%); £3,780,743.73 -> £3,395,647.96 (10.2%); £3,780,744.00 -> £3,395,648.09 (10.2%); £3,780,744.25 -> £3,395,648.22 (10.2%); £3,780,744.51 -> £3,395,648.35 (10.2%); £3,780,744.76 -> £3,395,648.48 (10.2%); £3,780,745.02 -> £3,395,648.51 (10.2%); £3,780,745.27 -> £3,395,648.54 (10.2%); £3,780,745.51 -> £3,395,648.56 (10.2%); £3,780,745.73 -> £3,395,648.58 (10.2%); £3,780,745.93 -> £3,395,648.60 (10.2%); £3,780,746.08 -> £3,395,648.62 (10.2%); £3,780,746.23 -> £3,395,648.64 (10.2%); £3,780,746.38 -> £3,395,648.66 (10.2%); £3,780,746.54 -> £3,395,648.67 (10.2%); £3,780,746.68 -> £3,395,648.69 (10.2%); £3,780,746.84 -> £3,395,648.71 (10.2%); £3,780,746.99 -> £3,395,648.72 (10.2%); £3,780,747.15 -> £3,395,648.74 (10.2%); £3,780,747.30 -> £3,395,648.76 (10.2%); £3,780,747.46 -> £3,395,648.77 (10.2%); £3,780,747.61 -> £3,395,648.79 (10.2%); £3,780,747.76 -> £3,395,648.92 (10.2%); £3,780,747.92 -> £3,395,649.06 (10.2%); £3,780,748.09 -> £3,395,649.20 (10.2%); £3,780,748.28 -> £3,395,649.34 (10.2%); £3,780,748.48 -> £3,395,649.48 (10.2%); £3,780,748.70 -> £3,395,649.62 (10.2%); £3,780,748.94 -> £3,395,649.76 (10.2%); £3,780,749.21 -> £3,395,649.90 (10.2%); £3,780,749.47 -> £3,395,649.92 (10.2%); £3,780,749.74 -> £3,395,649.95 (10.2%); £3,780,749.99 -> £3,395,649.97 (10.2%); £3,780,750.25 -> £3,395,650.00 (10.2%); £3,780,750.51 -> £3,395,650.02 (10.2%); £3,780,750.75 -> £3,395,650.05 (10.2%); £3,780,751.01 -> £3,395,650.07 (10.2%); £3,780,751.26 -> £3,395,650.10 (10.2%); £3,780,751.52 -> £3,395,650.12 (10.2%); £3,780,751.78 -> £3,395,650.14 (10.2%); £3,780,752.03 -> £3,395,650.17 (10.2%); £3,780,752.28 -> £3,395,650.19 (10.2%); £3,780,752.54 -> £3,395,650.22 (10.2%); £3,780,752.73 -> £3,395,650.37 (10.2%); £3,780,752.93 -> £3,395,650.52 (10.2%); £3,780,753.12 -> £3,395,650.67 (10.2%); £3,780,753.32 -> £3,395,650.82 (10.2%); £3,780,753.51 -> £3,395,650.97 (10.2%); £3,780,753.70 -> £3,395,651.12 (10.2%); £3,780,753.90 -> £3,395,651.27 (10.2%); £3,780,754.16 -> £3,395,651.42 (10.2%); £3,780,754.41 -> £3,395,651.57 (10.2%); £3,780,754.67 -> £3,395,651.73 (10.2%); £3,780,754.93 -> £3,395,651.87 (10.2%); £3,780,755.18 -> £3,395,651.90 (10.2%); £3,780,755.43 -> £3,395,651.93 (10.2%); £3,780,755.67 -> £3,395,651.95 (10.2%); £3,780,755.88 -> £3,395,651.97 (10.2%); £3,780,756.09 -> £3,395,652.00 (10.2%); £3,780,756.23 -> £3,395,652.02 (10.2%); £3,780,756.37 -> £3,395,652.04 (10.2%); £3,780,756.51 -> £3,395,652.05 (10.2%); £3,780,756.65 -> £3,395,652.07 (10.2%); £3,780,756.79 -> £3,395,652.09 (10.2%); £3,780,756.93 -> £3,395,652.10 (10.2%); £3,780,757.07 -> £3,395,652.12 (10.2%); £3,780,757.21 -> £3,395,652.14 (10.2%); £3,780,757.35 -> £3,395,652.16 (10.2%); £3,780,757.49 -> £3,395,652.17 (10.2%); £3,780,757.62 -> £3,395,652.19 (10.2%); £3,780,757.76 -> £3,395,652.35 (10.2%); £3,780,757.90 -> £3,395,652.50 (10.2%); £3,780,758.06 -> £3,395,652.66 (10.2%); £3,780,758.23 -> £3,395,652.82 (10.2%); £3,780,758.42 -> £3,395,652.98 (10.2%); £3,780,758.62 -> £3,395,653.15 (10.2%); £3,780,758.83 -> £3,395,653.31 (10.2%); £3,780,759.07 -> £3,395,653.48 (10.2%); £3,780,759.30 -> £3,395,653.50 (10.2%); £3,780,759.54 -> £3,395,653.53 (10.2%); £3,780,759.77 -> £3,395,653.55 (10.2%); £3,780,760.00 -> £3,395,653.58 (10.2%); £3,780,760.22 -> £3,395,653.61 (10.2%); £3,780,760.45 -> £3,395,653.64 (10.2%); £3,780,760.68 -> £3,395,653.67 (10.2%); £3,780,760.92 -> £3,395,653.69 (10.2%); £3,780,761.15 -> £3,395,653.72 (10.2%); £3,780,761.39 -> £3,395,653.74 (10.2%); £3,780,761.62 -> £3,395,653.77 (10.2%); £3,780,761.85 -> £3,395,653.80 (10.2%); £3,780,762.07 -> £3,395,653.82 (10.2%); £3,780,762.24 -> £3,395,653.99 (10.2%); £3,780,762.42 -> £3,395,654.15 (10.2%); £3,780,762.60 -> £3,395,654.32 (10.2%); £3,780,762.77 -> £3,395,654.49 (10.2%); £3,780,762.94 -> £3,395,654.66 (10.2%); £3,780,763.18 -> £3,395,654.84 (10.2%); £3,780,763.40 -> £3,395,655.01 (10.2%); £3,780,763.63 -> £3,395,655.17 (10.2%); £3,780,763.87 -> £3,395,655.34 (10.2%); £3,780,764.10 -> £3,395,655.50 (10.2%); £3,780,764.33 -> £3,395,655.67 (10.2%); £3,780,764.56 -> £3,395,655.70 (10.2%); £3,780,764.79 -> £3,395,655.73 (10.2%); £3,780,765.00 -> £3,395,655.76 (10.2%); £3,780,765.19 -> £3,395,655.78 (10.2%); £3,780,765.36 -> £3,395,655.80 (10.2%); £3,780,765.50 -> £3,395,655.82 (10.2%); £3,780,765.64 -> £3,395,655.84 (10.2%); £3,780,765.78 -> £3,395,655.86 (10.2%); £3,780,765.93 -> £3,395,655.88 (10.2%); £3,780,766.07 -> £3,395,655.90 (10.2%); £3,780,766.21 -> £3,395,655.91 (10.2%); £3,780,766.35 -> £3,395,655.93 (10.2%); £3,780,766.49 -> £3,395,655.95 (10.2%); £3,780,766.63 -> £3,395,655.96 (10.2%); £3,780,766.77 -> £3,395,655.98 (10.2%); £3,780,766.90 -> £3,395,656.00 (10.2%); £3,780,767.04 -> £3,395,656.13 (10.2%); £3,780,767.18 -> £3,395,656.26 (10.2%); £3,780,767.34 -> £3,395,656.39 (10.2%); £3,780,767.51 -> £3,395,656.52 (10.2%); £3,780,767.70 -> £3,395,656.65 (10.2%); £3,780,767.90 -> £3,395,656.78 (10.2%); £3,780,768.12 -> £3,395,656.92 (10.2%); £3,780,768.35 -> £3,395,657.06 (10.2%); £3,780,768.59 -> £3,395,657.09 (10.2%); £3,780,768.83 -> £3,395,657.12 (10.2%); £3,780,769.06 -> £3,395,657.15 (10.2%); £3,780,769.29 -> £3,395,657.18 (10.2%); £3,780,769.52 -> £3,395,657.21 (10.2%); £3,780,769.75 -> £3,395,657.25 (10.2%); £3,780,769.98 -> £3,395,657.28 (10.2%); £3,780,770.21 -> £3,395,657.31 (10.2%); £3,780,770.45 -> £3,395,657.33 (10.2%); £3,780,770.68 -> £3,395,657.36 (10.2%); £3,780,770.92 -> £3,395,657.39 (10.2%); £3,780,771.15 -> £3,395,657.42 (10.2%); £3,780,771.37 -> £3,395,657.45 (10.2%); £3,780,771.54 -> £3,395,657.59 (10.2%); £3,780,771.71 -> £3,395,657.73 (10.2%); £3,780,771.89 -> £3,395,657.87 (10.2%); £3,780,772.07 -> £3,395,658.03 (10.2%); £3,780,772.30 -> £3,395,658.18 (10.2%); £3,780,772.53 -> £3,395,658.32 (10.2%); £3,780,772.71 -> £3,395,658.46 (10.2%); £3,780,772.94 -> £3,395,658.60 (10.2%); £3,780,773.18 -> £3,395,658.74 (10.2%); £3,780,773.41 -> £3,395,658.88 (10.2%); £3,780,773.65 -> £3,395,659.02 (10.2%); £3,780,773.88 -> £3,395,659.05 (10.2%); £3,780,774.12 -> £3,395,659.08 (10.2%); £3,780,774.33 -> £3,395,659.10 (10.2%); £3,780,774.53 -> £3,395,659.12 (10.2%); £3,780,774.70 -> £3,395,659.14 (10.2%); £3,780,774.86 -> £3,395,659.16 (10.2%); £3,780,775.01 -> £3,395,659.18 (10.2%); £3,780,775.18 -> £3,395,659.20 (10.2%); £3,780,775.34 -> £3,395,659.21 (10.2%); £3,780,775.50 -> £3,395,659.23 (10.2%); £3,780,775.65 -> £3,395,659.25 (10.2%); £3,780,775.82 -> £3,395,659.26 (10.2%); £3,780,775.98 -> £3,395,659.28 (10.2%); £3,780,776.14 -> £3,395,659.30 (10.2%); £3,780,776.30 -> £3,395,659.31 (10.2%); £3,780,776.46 -> £3,395,659.33 (10.2%); £3,780,776.63 -> £3,395,659.42 (10.2%); £3,780,776.79 -> £3,395,659.51 (10.2%); £3,780,776.97 -> £3,395,659.61 (10.2%); £3,780,777.17 -> £3,395,659.71 (10.2%); £3,780,777.38 -> £3,395,659.81 (10.2%); £3,780,777.62 -> £3,395,659.91 (10.2%); £3,780,777.87 -> £3,395,660.01 (10.2%); £3,780,778.14 -> £3,395,660.10 (10.2%); £3,780,778.41 -> £3,395,660.13 (10.2%); £3,780,778.68 -> £3,395,660.15 (10.2%); £3,780,778.96 -> £3,395,660.17 (10.2%); £3,780,779.21 -> £3,395,660.20 (10.2%); £3,780,779.48 -> £3,395,660.22 (10.2%); £3,780,779.75 -> £3,395,660.24 (10.2%); £3,780,780.00 -> £3,395,660.27 (10.2%); £3,780,780.26 -> £3,395,660.29 (10.2%); £3,780,780.53 -> £3,395,660.31 (10.2%); £3,780,780.79 -> £3,395,660.34 (10.2%); £3,780,781.06 -> £3,395,660.36 (10.2%); £3,780,781.33 -> £3,395,660.39 (10.2%); £3,780,781.60 -> £3,395,660.41 (10.2%); £3,780,781.86 -> £3,395,660.53 (10.2%); £3,780,782.14 -> £3,395,660.64 (10.2%); £3,780,782.41 -> £3,395,660.76 (10.2%); £3,780,782.68 -> £3,395,660.88 (10.2%); £3,780,782.96 -> £3,395,660.99 (10.2%); £3,780,783.22 -> £3,395,661.10 (10.2%); £3,780,783.43 -> £3,395,661.22 (10.2%); £3,780,783.70 -> £3,395,661.33 (10.2%); £3,780,783.97 -> £3,395,661.44 (10.2%); £3,780,784.23 -> £3,395,661.54 (10.2%); £3,780,784.50 -> £3,395,661.65 (10.2%); £3,780,784.76 -> £3,395,661.68 (10.2%); £3,780,785.04 -> £3,395,661.71 (10.2%); £3,780,785.28 -> £3,395,661.73 (10.2%); £3,780,785.51 -> £3,395,661.75 (10.2%); £3,780,785.72 -> £3,395,661.77 (10.2%); £3,780,785.88 -> £3,395,661.79 (10.2%); £3,780,786.04 -> £3,395,661.81 (10.2%); £3,780,786.20 -> £3,395,661.82 (10.2%); £3,780,786.36 -> £3,395,661.84 (10.2%); £3,780,786.51 -> £3,395,661.86 (10.2%); £3,780,786.67 -> £3,395,661.88 (10.2%); £3,780,786.83 -> £3,395,661.89 (10.2%); £3,780,786.98 -> £3,395,661.91 (10.2%); £3,780,787.15 -> £3,395,661.93 (10.2%); £3,780,787.31 -> £3,395,661.94 (10.2%); £3,780,787.46 -> £3,395,661.96 (10.2%); £3,780,787.62 -> £3,395,662.11 (10.2%); £3,780,787.78 -> £3,395,662.27 (10.2%); £3,780,787.95 -> £3,395,662.43 (10.2%); £3,780,788.15 -> £3,395,662.59 (10.2%); £3,780,788.36 -> £3,395,662.75 (10.2%); £3,780,788.59 -> £3,395,662.91 (10.2%); £3,780,788.84 -> £3,395,663.07 (10.2%); £3,780,789.11 -> £3,395,663.23 (10.2%); £3,780,789.38 -> £3,395,663.25 (10.2%); £3,780,789.65 -> £3,395,663.28 (10.2%); £3,780,789.90 -> £3,395,663.30 (10.2%); £3,780,790.17 -> £3,395,663.33 (10.2%); £3,780,790.44 -> £3,395,663.35 (10.2%); £3,780,790.70 -> £3,395,663.37 (10.2%); £3,780,790.96 -> £3,395,663.40 (10.2%); £3,780,791.23 -> £3,395,663.42 (10.2%); £3,780,791.50 -> £3,395,663.44 (10.2%); £3,780,791.77 -> £3,395,663.47 (10.2%); £3,780,792.03 -> £3,395,663.49 (10.2%); £3,780,792.29 -> £3,395,663.52 (10.2%); £3,780,792.56 -> £3,395,663.55 (10.2%); £3,780,792.76 -> £3,395,663.70 (10.2%); £3,780,792.96 -> £3,395,663.87 (10.2%); £3,780,793.23 -> £3,395,664.04 (10.2%); £3,780,793.50 -> £3,395,664.21 (10.2%); £3,780,793.70 -> £3,395,664.38 (10.2%); £3,780,793.89 -> £3,395,664.54 (10.2%); £3,780,794.09 -> £3,395,664.70 (10.2%); £3,780,794.35 -> £3,395,664.86 (10.2%); £3,780,794.61 -> £3,395,665.03 (10.2%); £3,780,794.87 -> £3,395,665.19 (10.2%); £3,780,795.13 -> £3,395,665.35 (10.2%); £3,780,795.39 -> £3,395,665.38 (10.2%); £3,780,795.66 -> £3,395,665.41 (10.2%); £3,780,795.90 -> £3,395,665.44 (10.2%); £3,780,796.12 -> £3,395,665.46 (10.2%); £3,780,796.33 -> £3,395,665.48 (10.2%); £3,780,796.49 -> £3,395,665.50 (10.2%); £3,780,796.65 -> £3,395,665.51 (10.2%); £3,780,796.81 -> £3,395,665.53 (10.2%); £3,780,796.97 -> £3,395,665.55 (10.2%); £3,780,797.13 -> £3,395,665.57 (10.2%); £3,780,797.28 -> £3,395,665.58 (10.2%); £3,780,797.44 -> £3,395,665.60 (10.2%); £3,780,797.60 -> £3,395,665.62 (10.2%); £3,780,797.76 -> £3,395,665.63 (10.2%); £3,780,797.92 -> £3,395,665.65 (10.2%); £3,780,798.08 -> £3,395,665.67 (10.2%); £3,780,798.24 -> £3,395,665.83 (10.2%); £3,780,798.39 -> £3,395,666.00 (10.2%); £3,780,798.57 -> £3,395,666.18 (10.2%); £3,780,798.76 -> £3,395,666.36 (10.2%); £3,780,798.97 -> £3,395,666.54 (10.2%); £3,780,799.20 -> £3,395,666.71 (10.2%); £3,780,799.46 -> £3,395,666.88 (10.2%); £3,780,799.72 -> £3,395,667.05 (10.2%); £3,780,799.99 -> £3,395,667.08 (10.2%); £3,780,800.26 -> £3,395,667.10 (10.2%); £3,780,800.53 -> £3,395,667.12 (10.2%); £3,780,800.79 -> £3,395,667.15 (10.2%); £3,780,801.06 -> £3,395,667.17 (10.2%); £3,780,801.32 -> £3,395,667.20 (10.2%); £3,780,801.58 -> £3,395,667.22 (10.2%); £3,780,801.83 -> £3,395,667.24 (10.2%); £3,780,802.11 -> £3,395,667.27 (10.2%); £3,780,802.37 -> £3,395,667.29 (10.2%); £3,780,802.64 -> £3,395,667.31 (10.2%); £3,780,802.90 -> £3,395,667.34 (10.2%); £3,780,803.16 -> £3,395,667.37 (10.2%); £3,780,803.43 -> £3,395,667.54 (10.2%); £3,780,803.69 -> £3,395,667.72 (10.2%); £3,780,803.89 -> £3,395,667.90 (10.2%); £3,780,804.09 -> £3,395,668.08 (10.2%); £3,780,804.30 -> £3,395,668.26 (10.2%); £3,780,804.57 -> £3,395,668.45 (10.2%); £3,780,804.83 -> £3,395,668.62 (10.2%); £3,780,805.10 -> £3,395,668.80 (10.2%); £3,780,805.36 -> £3,395,668.97 (10.2%); £3,780,805.63 -> £3,395,669.15 (10.2%); £3,780,805.89 -> £3,395,669.32 (10.2%); £3,780,806.16 -> £3,395,669.35 (10.2%); £3,780,806.43 -> £3,395,669.38 (10.2%); £3,780,806.67 -> £3,395,669.40 (10.2%); £3,780,806.89 -> £3,395,669.43 (10.2%); £3,780,807.10 -> £3,395,669.45 (10.2%); £3,780,807.26 -> £3,395,669.47 (10.2%); £3,780,807.42 -> £3,395,669.48 (10.2%); £3,780,807.58 -> £3,395,669.50 (10.2%); £3,780,807.74 -> £3,395,669.52 (10.2%); £3,780,807.89 -> £3,395,669.53 (10.2%); £3,780,808.05 -> £3,395,669.55 (10.2%); £3,780,808.21 -> £3,395,669.57 (10.2%); £3,780,808.37 -> £3,395,669.58 (10.2%); £3,780,808.53 -> £3,395,669.60 (10.2%); £3,780,808.69 -> £3,395,669.62 (10.2%); £3,780,808.85 -> £3,395,669.64 (10.2%); £3,780,809.02 -> £3,395,669.81 (10.2%); £3,780,809.18 -> £3,395,669.97 (10.2%); £3,780,809.35 -> £3,395,670.14 (10.2%); £3,780,809.53 -> £3,395,670.30 (10.2%); £3,780,809.75 -> £3,395,670.47 (10.2%); £3,780,809.97 -> £3,395,670.64 (10.2%); £3,780,810.21 -> £3,395,670.81 (10.2%); £3,780,810.48 -> £3,395,670.98 (10.2%); £3,780,810.74 -> £3,395,671.01 (10.2%); £3,780,811.00 -> £3,395,671.03 (10.2%); £3,780,811.26 -> £3,395,671.05 (10.2%); £3,780,811.52 -> £3,395,671.08 (10.2%); £3,780,811.78 -> £3,395,671.10 (10.2%); £3,780,812.05 -> £3,395,671.13 (10.2%); £3,780,812.32 -> £3,395,671.15 (10.2%); £3,780,812.59 -> £3,395,671.17 (10.2%); £3,780,812.85 -> £3,395,671.20 (10.2%); £3,780,813.12 -> £3,395,671.22 (10.2%); £3,780,813.39 -> £3,395,671.24 (10.2%); £3,780,813.66 -> £3,395,671.27 (10.2%); £3,780,813.93 -> £3,395,671.30 (10.2%); £3,780,814.19 -> £3,395,671.47 (10.2%); £3,780,814.39 -> £3,395,671.64 (10.2%); £3,780,814.58 -> £3,395,671.81 (10.2%); £3,780,814.78 -> £3,395,671.99 (10.2%); £3,780,814.98 -> £3,395,672.16 (10.2%); £3,780,815.17 -> £3,395,672.34 (10.2%); £3,780,815.44 -> £3,395,672.52 (10.2%); £3,780,815.70 -> £3,395,672.69 (10.2%); £3,780,815.97 -> £3,395,672.86 (10.2%); £3,780,816.23 -> £3,395,673.04 (10.2%); £3,780,816.50 -> £3,395,673.21 (10.2%); £3,780,816.76 -> £3,395,673.23 (10.2%); £3,780,817.03 -> £3,395,673.26 (10.2%); £3,780,817.28 -> £3,395,673.29 (10.2%); £3,780,817.50 -> £3,395,673.31 (10.2%); £3,780,817.70 -> £3,395,673.33 (10.2%); £3,780,817.86 -> £3,395,673.35 (10.2%); £3,780,818.02 -> £3,395,673.36 (10.2%); £3,780,818.18 -> £3,395,673.38 (10.2%); £3,780,818.33 -> £3,395,673.40 (10.2%); £3,780,818.49 -> £3,395,673.41 (10.2%); £3,780,818.65 -> £3,395,673.43 (10.2%); £3,780,818.81 -> £3,395,673.45 (10.2%); £3,780,818.97 -> £3,395,673.46 (10.2%); £3,780,819.13 -> £3,395,673.48 (10.2%); £3,780,819.29 -> £3,395,673.50 (10.2%); £3,780,819.44 -> £3,395,673.51 (10.2%); £3,780,819.61 -> £3,395,673.62 (10.2%); £3,780,819.76 -> £3,395,673.73 (10.2%); £3,780,819.94 -> £3,395,673.84 (10.2%); £3,780,820.13 -> £3,395,673.96 (10.2%); £3,780,820.34 -> £3,395,674.07 (10.2%); £3,780,820.57 -> £3,395,674.19 (10.2%); £3,780,820.82 -> £3,395,674.30 (10.2%); £3,780,821.10 -> £3,395,674.41 (10.2%); £3,780,821.37 -> £3,395,674.44 (10.2%); £3,780,821.64 -> £3,395,674.46 (10.2%); £3,780,821.91 -> £3,395,674.48 (10.2%); £3,780,822.17 -> £3,395,674.51 (10.2%); £3,780,822.44 -> £3,395,674.53 (10.2%); £3,780,822.71 -> £3,395,674.56 (10.2%); £3,780,822.97 -> £3,395,674.58 (10.2%); £3,780,823.24 -> £3,395,674.61 (10.2%); £3,780,823.51 -> £3,395,674.63 (10.2%); £3,780,823.76 -> £3,395,674.65 (10.2%); £3,780,824.03 -> £3,395,674.68 (10.2%); £3,780,824.29 -> £3,395,674.70 (10.2%); £3,780,824.57 -> £3,395,674.73 (10.2%); £3,780,824.84 -> £3,395,674.85 (10.2%); £3,780,825.10 -> £3,395,674.98 (10.2%); £3,780,825.36 -> £3,395,675.11 (10.2%); £3,780,825.62 -> £3,395,675.24 (10.2%); £3,780,825.89 -> £3,395,675.37 (10.2%); £3,780,826.15 -> £3,395,675.50 (10.2%); £3,780,826.42 -> £3,395,675.62 (10.2%); £3,780,826.69 -> £3,395,675.75 (10.2%); £3,780,826.95 -> £3,395,675.87 (10.2%); £3,780,827.22 -> £3,395,675.99 (10.2%); £3,780,827.48 -> £3,395,676.12 (10.2%); £3,780,827.75 -> £3,395,676.15 (10.2%); £3,780,828.02 -> £3,395,676.17 (10.2%); £3,780,828.27 -> £3,395,676.20 (10.2%); £3,780,828.50 -> £3,395,676.22 (10.2%); £3,780,828.71 -> £3,395,676.24 (10.2%); £3,780,828.84 -> £3,395,676.26 (10.2%); £3,780,828.98 -> £3,395,676.28 (10.2%); £3,780,829.12 -> £3,395,676.30 (10.2%); £3,780,829.26 -> £3,395,676.32 (10.2%); £3,780,829.40 -> £3,395,676.34 (10.2%); £3,780,829.54 -> £3,395,676.35 (10.2%); £3,780,829.68 -> £3,395,676.37 (10.2%); £3,780,829.82 -> £3,395,676.39 (10.2%); £3,780,829.96 -> £3,395,676.40 (10.2%); £3,780,830.10 -> £3,395,676.42 (10.2%); £3,780,830.24 -> £3,395,676.44 (10.2%); £3,780,830.38 -> £3,395,676.55 (10.2%); £3,780,830.52 -> £3,395,676.66 (10.2%); £3,780,830.67 -> £3,395,676.77 (10.2%); £3,780,830.85 -> £3,395,676.88 (10.2%); £3,780,831.03 -> £3,395,676.99 (10.2%); £3,780,831.23 -> £3,395,677.10 (10.2%); £3,780,831.45 -> £3,395,677.21 (10.2%); £3,780,831.67 -> £3,395,677.32 (10.2%); £3,780,831.91 -> £3,395,677.35 (10.2%); £3,780,832.15 -> £3,395,677.38 (10.2%); £3,780,832.38 -> £3,395,677.40 (10.2%); £3,780,832.61 -> £3,395,677.43 (10.2%); £3,780,832.84 -> £3,395,677.46 (10.2%); £3,780,833.07 -> £3,395,677.48 (10.2%); £3,780,833.31 -> £3,395,677.51 (10.2%); £3,780,833.54 -> £3,395,677.54 (10.2%); £3,780,833.77 -> £3,395,677.56 (10.2%); £3,780,834.00 -> £3,395,677.59 (10.2%); £3,780,834.23 -> £3,395,677.61 (10.2%); £3,780,834.46 -> £3,395,677.64 (10.2%); £3,780,834.70 -> £3,395,677.67 (10.2%); £3,780,834.93 -> £3,395,677.78 (10.2%); £3,780,835.11 -> £3,395,677.90 (10.2%); £3,780,835.35 -> £3,395,678.03 (10.2%); £3,780,835.52 -> £3,395,678.15 (10.2%); £3,780,835.69 -> £3,395,678.27 (10.2%); £3,780,835.87 -> £3,395,678.39 (10.2%); £3,780,836.04 -> £3,395,678.52 (10.2%); £3,780,836.27 -> £3,395,678.64 (10.2%); £3,780,836.50 -> £3,395,678.77 (10.2%); £3,780,836.74 -> £3,395,678.88 (10.2%); £3,780,836.96 -> £3,395,679.00 (10.2%); £3,780,837.19 -> £3,395,679.03 (10.2%); £3,780,837.42 -> £3,395,679.06 (10.2%); £3,780,837.64 -> £3,395,679.08 (10.2%); £3,780,837.83 -> £3,395,679.11 (10.2%); £3,780,838.01 -> £3,395,679.13 (10.2%); £3,780,838.15 -> £3,395,679.15 (10.2%); £3,780,838.29 -> £3,395,679.17 (10.2%); £3,780,838.43 -> £3,395,679.19 (10.2%); £3,780,838.57 -> £3,395,679.21 (10.2%); £3,780,838.71 -> £3,395,679.22 (10.2%); £3,780,838.85 -> £3,395,679.24 (10.2%); £3,780,838.99 -> £3,395,679.26 (10.2%); £3,780,839.13 -> £3,395,679.28 (10.2%); £3,780,839.27 -> £3,395,679.29 (10.2%); £3,780,839.41 -> £3,395,679.31 (10.2%); £3,780,839.55 -> £3,395,679.33 (10.2%); £3,780,839.69 -> £3,395,679.43 (10.2%); £3,780,839.83 -> £3,395,679.53 (10.2%); £3,780,839.99 -> £3,395,679.63 (10.2%); £3,780,840.15 -> £3,395,679.73 (10.2%); £3,780,840.34 -> £3,395,679.84 (10.2%); £3,780,840.54 -> £3,395,679.95 (10.2%); £3,780,840.77 -> £3,395,680.06 (10.2%); £3,780,841.00 -> £3,395,680.17 (10.2%); £3,780,841.23 -> £3,395,680.20 (10.2%); £3,780,841.46 -> £3,395,680.23 (10.2%); £3,780,841.70 -> £3,395,680.27 (10.2%); £3,780,841.94 -> £3,395,680.30 (10.2%); £3,780,842.17 -> £3,395,680.33 (10.2%); £3,780,842.41 -> £3,395,680.36 (10.2%); £3,780,842.65 -> £3,395,680.39 (10.2%); £3,780,842.89 -> £3,395,680.42 (10.2%); £3,780,843.12 -> £3,395,680.45 (10.2%); £3,780,843.36 -> £3,395,680.48 (10.2%); £3,780,843.60 -> £3,395,680.51 (10.2%); £3,780,843.83 -> £3,395,680.54 (10.2%); £3,780,844.07 -> £3,395,680.57 (10.2%); £3,780,844.30 -> £3,395,680.68 (10.2%); £3,780,844.53 -> £3,395,680.80 (10.2%); £3,780,844.70 -> £3,395,680.92 (10.2%); £3,780,844.87 -> £3,395,681.04 (10.2%); £3,780,845.05 -> £3,395,681.15 (10.2%); £3,780,845.23 -> £3,395,681.27 (10.2%); £3,780,845.41 -> £3,395,681.39 (10.2%); £3,780,845.65 -> £3,395,681.50 (10.2%); £3,780,845.88 -> £3,395,681.61 (10.2%); £3,780,846.11 -> £3,395,681.73 (10.2%); £3,780,846.34 -> £3,395,681.85 (10.2%); £3,780,846.58 -> £3,395,681.88 (10.2%); £3,780,846.82 -> £3,395,681.91 (10.2%); £3,780,847.04 -> £3,395,681.93 (10.2%); £3,780,847.24 -> £3,395,681.96 (10.2%); £3,780,847.42 -> £3,395,681.98 (10.2%); £3,780,847.58 -> £3,395,681.99 (10.2%); £3,780,847.74 -> £3,395,682.01 (10.2%); £3,780,847.91 -> £3,395,682.03 (10.2%); £3,780,848.07 -> £3,395,682.05 (10.2%); £3,780,848.22 -> £3,395,682.06 (10.2%); £3,780,848.39 -> £3,395,682.08 (10.2%); £3,780,848.55 -> £3,395,682.10 (10.2%); £3,780,848.72 -> £3,395,682.11 (10.2%); £3,780,848.89 -> £3,395,682.13 (10.2%); £3,780,849.05 -> £3,395,682.15 (10.2%); £3,780,849.21 -> £3,395,682.17 (10.2%); £3,780,849.38 -> £3,395,682.28 (10.2%); £3,780,849.54 -> £3,395,682.38 (10.2%); £3,780,849.72 -> £3,395,682.49 (10.2%); £3,780,849.93 -> £3,395,682.60 (10.2%); £3,780,850.15 -> £3,395,682.72 (10.2%); £3,780,850.39 -> £3,395,682.83 (10.2%); £3,780,850.63 -> £3,395,682.95 (10.2%); £3,780,850.90 -> £3,395,683.06 (10.2%); £3,780,851.17 -> £3,395,683.09 (10.2%); £3,780,851.45 -> £3,395,683.11 (10.2%); £3,780,851.73 -> £3,395,683.13 (10.2%); £3,780,852.00 -> £3,395,683.16 (10.2%); £3,780,852.27 -> £3,395,683.18 (10.2%); £3,780,852.53 -> £3,395,683.20 (10.2%); £3,780,852.80 -> £3,395,683.23 (10.2%); £3,780,853.07 -> £3,395,683.25 (10.2%); £3,780,853.34 -> £3,395,683.27 (10.2%); £3,780,853.60 -> £3,395,683.30 (10.2%); £3,780,853.88 -> £3,395,683.32 (10.2%); £3,780,854.16 -> £3,395,683.34 (10.2%); £3,780,854.42 -> £3,395,683.37 (10.2%); £3,780,854.63 -> £3,395,683.49 (10.2%); £3,780,854.83 -> £3,395,683.61 (10.2%); £3,780,855.03 -> £3,395,683.74 (10.2%); £3,780,855.23 -> £3,395,683.86 (10.2%); £3,780,855.44 -> £3,395,683.99 (10.2%); £3,780,855.72 -> £3,395,684.12 (10.2%); £3,780,855.99 -> £3,395,684.25 (10.2%); £3,780,856.27 -> £3,395,684.37 (10.2%); £3,780,856.54 -> £3,395,684.49 (10.2%); £3,780,856.81 -> £3,395,684.61 (10.2%); £3,780,857.08 -> £3,395,684.73 (10.2%); £3,780,857.36 -> £3,395,684.76 (10.2%); £3,780,857.62 -> £3,395,684.79 (10.2%); £3,780,857.88 -> £3,395,684.81 (10.2%); £3,780,858.11 -> £3,395,684.84 (10.2%); £3,780,858.33 -> £3,395,684.86 (10.2%); £3,780,858.49 -> £3,395,684.88 (10.2%); £3,780,858.66 -> £3,395,684.89 (10.2%); £3,780,858.83 -> £3,395,684.91 (10.2%); £3,780,858.99 -> £3,395,684.93 (10.2%); £3,780,859.17 -> £3,395,684.95 (10.2%); £3,780,859.33 -> £3,395,684.96 (10.2%); £3,780,859.49 -> £3,395,684.98 (10.2%); £3,780,859.66 -> £3,395,685.00 (10.2%); £3,780,859.82 -> £3,395,685.01 (10.2%); £3,780,859.99 -> £3,395,685.03 (10.2%); £3,780,860.16 -> £3,395,685.05 (10.2%); £3,780,860.32 -> £3,395,685.18 (10.2%); £3,780,860.49 -> £3,395,685.30 (10.2%); £3,780,860.67 -> £3,395,685.43 (10.2%); £3,780,860.88 -> £3,395,685.57 (10.2%); £3,780,861.09 -> £3,395,685.70 (10.2%); £3,780,861.33 -> £3,395,685.83 (10.2%); £3,780,861.59 -> £3,395,685.96 (10.2%); £3,780,861.86 -> £3,395,686.09 (10.2%); £3,780,862.13 -> £3,395,686.11 (10.2%); £3,780,862.41 -> £3,395,686.14 (10.2%); £3,780,862.69 -> £3,395,686.16 (10.2%); £3,780,862.96 -> £3,395,686.18 (10.2%); £3,780,863.24 -> £3,395,686.21 (10.2%); £3,780,863.51 -> £3,395,686.23 (10.2%); £3,780,863.78 -> £3,395,686.26 (10.2%); £3,780,864.06 -> £3,395,686.28 (10.2%); £3,780,864.33 -> £3,395,686.30 (10.2%); £3,780,864.60 -> £3,395,686.33 (10.2%); £3,780,864.87 -> £3,395,686.35 (10.2%); £3,780,865.13 -> £3,395,686.37 (10.2%); £3,780,865.41 -> £3,395,686.40 (10.2%); £3,780,865.62 -> £3,395,686.53 (10.2%); £3,780,865.83 -> £3,395,686.67 (10.2%); £3,780,866.03 -> £3,395,686.80 (10.2%); £3,780,866.24 -> £3,395,686.94 (10.2%); £3,780,866.44 -> £3,395,687.08 (10.2%); £3,780,866.64 -> £3,395,687.21 (10.2%); £3,780,866.85 -> £3,395,687.34 (10.2%); £3,780,867.13 -> £3,395,687.47 (10.2%); £3,780,867.40 -> £3,395,687.61 (10.2%); £3,780,867.67 -> £3,395,687.73 (10.2%); £3,780,867.95 -> £3,395,687.87 (10.2%); £3,780,868.22 -> £3,395,687.89 (10.2%); £3,780,868.49 -> £3,395,687.92 (10.2%); £3,780,868.74 -> £3,395,687.95 (10.2%); £3,780,868.97 -> £3,395,687.97 (10.2%); £3,780,869.18 -> £3,395,687.99 (10.2%); £3,780,869.35 -> £3,395,688.01 (10.2%); £3,780,869.52 -> £3,395,688.02 (10.2%); £3,780,869.68 -> £3,395,688.04 (10.2%); £3,780,869.83 -> £3,395,688.06 (10.2%); £3,780,870.00 -> £3,395,688.08 (10.2%); £3,780,870.17 -> £3,395,688.09 (10.2%); £3,780,870.34 -> £3,395,688.11 (10.2%); £3,780,870.50 -> £3,395,688.12 (10.2%); £3,780,870.67 -> £3,395,688.14 (10.2%); £3,780,870.84 -> £3,395,688.16 (10.2%); £3,780,871.00 -> £3,395,688.18 (10.2%); £3,780,871.17 -> £3,395,688.36 (10.2%); £3,780,871.33 -> £3,395,688.56 (10.2%); £3,780,871.51 -> £3,395,688.76 (10.2%); £3,780,871.72 -> £3,395,688.96 (10.2%); £3,780,871.94 -> £3,395,689.16 (10.2%); £3,780,872.19 -> £3,395,689.36 (10.2%); £3,780,872.44 -> £3,395,689.55 (10.2%); £3,780,872.72 -> £3,395,689.74 (10.2%); £3,780,873.01 -> £3,395,689.77 (10.2%); £3,780,873.29 -> £3,395,689.79 (10.2%); £3,780,873.56 -> £3,395,689.81 (10.2%); £3,780,873.84 -> £3,395,689.84 (10.2%); £3,780,874.12 -> £3,395,689.86 (10.2%); £3,780,874.40 -> £3,395,689.89 (10.2%); £3,780,874.66 -> £3,395,689.91 (10.2%); £3,780,874.94 -> £3,395,689.93 (10.2%); £3,780,875.21 -> £3,395,689.96 (10.2%); £3,780,875.49 -> £3,395,689.98 (10.2%); £3,780,875.76 -> £3,395,690.00 (10.2%); £3,780,876.04 -> £3,395,690.03 (10.2%); £3,780,876.31 -> £3,395,690.06 (10.2%); £3,780,876.52 -> £3,395,690.25 (10.2%); £3,780,876.73 -> £3,395,690.45 (10.2%); £3,780,877.01 -> £3,395,690.65 (10.2%); £3,780,877.21 -> £3,395,690.85 (10.2%); £3,780,877.41 -> £3,395,691.05 (10.2%); £3,780,877.62 -> £3,395,691.25 (10.2%); £3,780,877.89 -> £3,395,691.46 (10.2%); £3,780,878.17 -> £3,395,691.66 (10.2%); £3,780,878.43 -> £3,395,691.86 (10.2%); £3,780,878.70 -> £3,395,692.06 (10.2%); £3,780,878.97 -> £3,395,692.25 (10.2%); £3,780,879.26 -> £3,395,692.28 (10.2%); £3,780,879.54 -> £3,395,692.30 (10.2%); £3,780,879.80 -> £3,395,692.33 (10.2%); £3,780,880.03 -> £3,395,692.35 (10.2%); £3,780,880.25 -> £3,395,692.37 (10.2%); £3,780,880.42 -> £3,395,692.39 (10.2%); £3,780,880.58 -> £3,395,692.41 (10.2%); £3,780,880.74 -> £3,395,692.43 (10.2%); £3,780,880.91 -> £3,395,692.44 (10.2%); £3,780,881.08 -> £3,395,692.46 (10.2%); £3,780,881.25 -> £3,395,692.48 (10.2%); £3,780,881.41 -> £3,395,692.49 (10.2%); £3,780,881.57 -> £3,395,692.51 (10.2%); £3,780,881.74 -> £3,395,692.52 (10.2%); £3,780,881.90 -> £3,395,692.54 (10.2%); £3,780,882.06 -> £3,395,692.56 (10.2%); £3,780,882.23 -> £3,395,692.76 (10.2%); £3,780,882.39 -> £3,395,692.96 (10.2%); £3,780,882.58 -> £3,395,693.16 (10.2%); £3,780,882.78 -> £3,395,693.38 (10.2%); £3,780,883.00 -> £3,395,693.60 (10.2%); £3,780,883.24 -> £3,395,693.81 (10.2%); £3,780,883.50 -> £3,395,694.03 (10.2%); £3,780,883.78 -> £3,395,694.23 (10.2%); £3,780,884.05 -> £3,395,694.25 (10.2%); £3,780,884.33 -> £3,395,694.28 (10.2%); £3,780,884.60 -> £3,395,694.30 (10.2%); £3,780,884.88 -> £3,395,694.33 (10.2%); £3,780,885.15 -> £3,395,694.35 (10.2%); £3,780,885.42 -> £3,395,694.37 (10.2%); £3,780,885.70 -> £3,395,694.40 (10.2%); £3,780,885.98 -> £3,395,694.42 (10.2%); £3,780,886.24 -> £3,395,694.44 (10.2%); £3,780,886.52 -> £3,395,694.47 (10.2%); £3,780,886.79 -> £3,395,694.49 (10.2%); £3,780,887.06 -> £3,395,694.51 (10.2%); £3,780,887.34 -> £3,395,694.54 (10.2%); £3,780,887.54 -> £3,395,694.76 (10.2%); £3,780,887.82 -> £3,395,694.97 (10.2%); £3,780,888.03 -> £3,395,695.18 (10.2%); £3,780,888.30 -> £3,395,695.40 (10.2%); £3,780,888.57 -> £3,395,695.62 (10.2%); £3,780,888.84 -> £3,395,695.84 (10.2%); £3,780,889.11 -> £3,395,696.06 (10.2%); £3,780,889.39 -> £3,395,696.27 (10.2%); £3,780,889.67 -> £3,395,696.48 (10.2%); £3,780,889.94 -> £3,395,696.68 (10.2%); £3,780,890.22 -> £3,395,696.90 (10.2%); £3,780,890.50 -> £3,395,696.92 (10.2%); £3,780,890.78 -> £3,395,696.95 (10.2%); £3,780,891.03 -> £3,395,696.98 (10.2%); £3,780,891.27 -> £3,395,697.00 (10.2%); £3,780,891.48 -> £3,395,697.02 (10.2%); £3,780,891.65 -> £3,395,697.04 (10.2%); £3,780,891.81 -> £3,395,697.05 (10.2%); £3,780,891.97 -> £3,395,697.07 (10.2%); £3,780,892.14 -> £3,395,697.09 (10.2%); £3,780,892.30 -> £3,395,697.10 (10.2%); £3,780,892.46 -> £3,395,697.12 (10.2%); £3,780,892.63 -> £3,395,697.14 (10.2%); £3,780,892.79 -> £3,395,697.15 (10.2%); £3,780,892.95 -> £3,395,697.17 (10.2%); £3,780,893.12 -> £3,395,697.19 (10.2%); £3,780,893.28 -> £3,395,697.20 (10.2%); £3,780,893.46 -> £3,395,697.36 (10.2%); £3,780,893.62 -> £3,395,697.52 (10.2%); £3,780,893.80 -> £3,395,697.68 (10.2%); £3,780,894.00 -> £3,395,697.84 (10.2%); £3,780,894.22 -> £3,395,698.01 (10.2%); £3,780,894.44 -> £3,395,698.17 (10.2%); £3,780,894.70 -> £3,395,698.33 (10.2%); £3,780,894.97 -> £3,395,698.50 (10.2%); £3,780,895.24 -> £3,395,698.52 (10.2%); £3,780,895.51 -> £3,395,698.54 (10.2%); £3,780,895.78 -> £3,395,698.57 (10.2%); £3,780,896.05 -> £3,395,698.59 (10.2%); £3,780,896.32 -> £3,395,698.62 (10.2%); £3,780,896.58 -> £3,395,698.65 (10.2%); £3,780,896.85 -> £3,395,698.67 (10.2%); £3,780,897.11 -> £3,395,698.69 (10.2%); £3,780,897.39 -> £3,395,698.72 (10.2%); £3,780,897.67 -> £3,395,698.74 (10.2%); £3,780,897.94 -> £3,395,698.76 (10.2%); £3,780,898.21 -> £3,395,698.79 (10.2%); £3,780,898.48 -> £3,395,698.82 (10.2%); £3,780,898.75 -> £3,395,698.99 (10.2%); £3,780,899.02 -> £3,395,699.16 (10.2%); £3,780,899.30 -> £3,395,699.33 (10.2%); £3,780,899.58 -> £3,395,699.51 (10.2%); £3,780,899.85 -> £3,395,699.68 (10.2%); £3,780,900.05 -> £3,395,699.85 (10.2%); £3,780,900.26 -> £3,395,700.01 (10.2%); £3,780,900.53 -> £3,395,700.18 (10.2%); £3,780,900.79 -> £3,395,700.35 (10.2%); £3,780,901.06 -> £3,395,700.52 (10.2%); £3,780,901.33 -> £3,395,700.68 (10.2%); £3,780,901.61 -> £3,395,700.71 (10.2%); £3,780,901.87 -> £3,395,700.74 (10.2%); £3,780,902.12 -> £3,395,700.76 (10.2%); £3,780,902.36 -> £3,395,700.78 (10.2%); £3,780,902.57 -> £3,395,700.80 (10.2%); £3,780,902.72 -> £3,395,700.82 (10.2%); £3,780,902.86 -> £3,395,700.84 (10.2%); £3,780,903.00 -> £3,395,700.86 (10.2%); £3,780,903.15 -> £3,395,700.88 (10.2%); £3,780,903.29 -> £3,395,700.89 (10.2%); £3,780,903.43 -> £3,395,700.91 (10.2%); £3,780,903.57 -> £3,395,700.93 (10.2%); £3,780,903.71 -> £3,395,700.94 (10.2%); £3,780,903.85 -> £3,395,700.96 (10.2%); £3,780,903.99 -> £3,395,700.98 (10.2%); £3,780,904.14 -> £3,395,700.99 (10.2%); £3,780,904.28 -> £3,395,701.14 (10.2%); £3,780,904.43 -> £3,395,701.29 (10.2%); £3,780,904.59 -> £3,395,701.44 (10.2%); £3,780,904.77 -> £3,395,701.59 (10.2%); £3,780,904.96 -> £3,395,701.75 (10.2%); £3,780,905.17 -> £3,395,701.91 (10.2%); £3,780,905.38 -> £3,395,702.08 (10.2%); £3,780,905.62 -> £3,395,702.24 (10.2%); £3,780,905.86 -> £3,395,702.27 (10.2%); £3,780,906.10 -> £3,395,702.29 (10.2%); £3,780,906.34 -> £3,395,702.32 (10.2%); £3,780,906.58 -> £3,395,702.34 (10.2%); £3,780,906.82 -> £3,395,702.37 (10.2%); £3,780,907.05 -> £3,395,702.40 (10.2%); £3,780,907.29 -> £3,395,702.42 (10.2%); £3,780,907.53 -> £3,395,702.45 (10.2%); £3,780,907.76 -> £3,395,702.48 (10.2%); £3,780,908.01 -> £3,395,702.50 (10.2%); £3,780,908.25 -> £3,395,702.53 (10.2%); £3,780,908.48 -> £3,395,702.55 (10.2%); £3,780,908.73 -> £3,395,702.58 (10.2%); £3,780,908.97 -> £3,395,702.74 (10.2%); £3,780,909.20 -> £3,395,702.91 (10.2%); £3,780,909.43 -> £3,395,703.07 (10.2%); £3,780,909.61 -> £3,395,703.24 (10.2%); £3,780,909.85 -> £3,395,703.41 (10.2%); £3,780,910.03 -> £3,395,703.57 (10.2%); £3,780,910.21 -> £3,395,703.74 (10.2%); £3,780,910.46 -> £3,395,703.91 (10.2%); £3,780,910.70 -> £3,395,704.07 (10.2%); £3,780,910.94 -> £3,395,704.23 (10.2%); £3,780,911.18 -> £3,395,704.39 (10.2%); £3,780,911.42 -> £3,395,704.42 (10.2%); £3,780,911.66 -> £3,395,704.45 (10.2%); £3,780,911.88 -> £3,395,704.47 (10.2%); £3,780,912.08 -> £3,395,704.50 (10.2%); £3,780,912.27 -> £3,395,704.52 (10.2%); £3,780,912.42 -> £3,395,704.54 (10.2%); £3,780,912.56 -> £3,395,704.56 (10.2%); £3,780,912.69 -> £3,395,704.58 (10.2%); £3,780,912.83 -> £3,395,704.60 (10.2%); £3,780,912.97 -> £3,395,704.61 (10.2%); £3,780,913.12 -> £3,395,704.63 (10.2%); £3,780,913.26 -> £3,395,704.65 (10.2%); £3,780,913.40 -> £3,395,704.66 (10.2%); £3,780,913.54 -> £3,395,704.68 (10.2%); £3,780,913.68 -> £3,395,704.70 (10.2%); £3,780,913.82 -> £3,395,704.71 (10.2%); £3,780,913.96 -> £3,395,704.87 (10.2%); £3,780,914.09 -> £3,395,705.03 (10.2%); £3,780,914.24 -> £3,395,705.18 (10.2%); £3,780,914.41 -> £3,395,705.34 (10.2%); £3,780,914.60 -> £3,395,705.51 (10.2%); £3,780,914.80 -> £3,395,705.68 (10.2%); £3,780,915.02 -> £3,395,705.85 (10.2%); £3,780,915.26 -> £3,395,706.02 (10.2%); £3,780,915.50 -> £3,395,706.05 (10.2%); £3,780,915.74 -> £3,395,706.08 (10.2%); £3,780,915.97 -> £3,395,706.11 (10.2%); £3,780,916.20 -> £3,395,706.14 (10.2%); £3,780,916.44 -> £3,395,706.17 (10.2%); £3,780,916.68 -> £3,395,706.20 (10.2%); £3,780,916.91 -> £3,395,706.23 (10.2%); £3,780,917.15 -> £3,395,706.26 (10.2%); £3,780,917.38 -> £3,395,706.29 (10.2%); £3,780,917.61 -> £3,395,706.32 (10.2%); £3,780,917.84 -> £3,395,706.35 (10.2%); £3,780,918.07 -> £3,395,706.38 (10.2%); £3,780,918.31 -> £3,395,706.41 (10.2%); £3,780,918.55 -> £3,395,706.58 (10.2%); £3,780,918.78 -> £3,395,706.75 (10.2%); £3,780,918.96 -> £3,395,706.92 (10.2%); £3,780,919.13 -> £3,395,707.09 (10.2%); £3,780,919.31 -> £3,395,707.26 (10.2%); £3,780,919.48 -> £3,395,707.43 (10.2%); £3,780,919.66 -> £3,395,707.61 (10.2%); £3,780,919.90 -> £3,395,707.78 (10.2%); £3,780,920.13 -> £3,395,707.95 (10.2%); £3,780,920.36 -> £3,395,708.12 (10.2%); £3,780,920.60 -> £3,395,708.29 (10.2%); £3,780,920.83 -> £3,395,708.32 (10.2%); £3,780,921.06 -> £3,395,708.34 (10.2%); £3,780,921.28 -> £3,395,708.37 (10.2%); £3,780,921.49 -> £3,395,708.39 (10.2%); £3,780,921.67 -> £3,395,708.41 (10.2%); £3,780,921.82 -> £3,395,708.43 (10.2%); £3,780,921.98 -> £3,395,708.45 (10.2%); £3,780,922.13 -> £3,395,708.46 (10.2%); £3,780,922.29 -> £3,395,708.48 (10.2%); £3,780,922.45 -> £3,395,708.50 (10.2%); £3,780,922.60 -> £3,395,708.51 (10.2%); £3,780,922.76 -> £3,395,708.53 (10.2%); £3,780,922.91 -> £3,395,708.55 (10.2%); £3,780,923.06 -> £3,395,708.56 (10.2%); £3,780,923.22 -> £3,395,708.58 (10.2%); £3,780,923.38 -> £3,395,708.60 (10.2%); £3,780,923.53 -> £3,395,708.77 (10.2%); £3,780,923.68 -> £3,395,708.95 (10.2%); £3,780,923.86 -> £3,395,709.13 (10.2%); £3,780,924.05 -> £3,395,709.31 (10.2%); £3,780,924.27 -> £3,395,709.49 (10.2%); £3,780,924.49 -> £3,395,709.67 (10.2%); £3,780,924.73 -> £3,395,709.85 (10.2%); £3,780,924.99 -> £3,395,710.03 (10.2%); £3,780,925.24 -> £3,395,710.06 (10.2%); £3,780,925.50 -> £3,395,710.08 (10.2%); £3,780,925.76 -> £3,395,710.10 (10.2%); £3,780,926.02 -> £3,395,710.13 (10.2%); £3,780,926.28 -> £3,395,710.15 (10.2%); £3,780,926.54 -> £3,395,710.18 (10.2%); £3,780,926.80 -> £3,395,710.20 (10.2%); £3,780,927.05 -> £3,395,710.22 (10.2%); £3,780,927.32 -> £3,395,710.25 (10.2%); £3,780,927.57 -> £3,395,710.27 (10.2%); £3,780,927.83 -> £3,395,710.29 (10.2%); £3,780,928.09 -> £3,395,710.32 (10.2%); £3,780,928.36 -> £3,395,710.35 (10.2%); £3,780,928.55 -> £3,395,710.53 (10.2%); £3,780,928.74 -> £3,395,710.71 (10.2%); £3,780,928.94 -> £3,395,710.89 (10.2%); £3,780,929.13 -> £3,395,711.08 (10.2%); £3,780,929.33 -> £3,395,711.26 (10.2%); £3,780,929.51 -> £3,395,711.45 (10.2%); £3,780,929.71 -> £3,395,711.63 (10.2%); £3,780,929.98 -> £3,395,711.81 (10.2%); £3,780,930.23 -> £3,395,711.99 (10.2%); £3,780,930.49 -> £3,395,712.17 (10.2%); £3,780,930.75 -> £3,395,712.35 (10.2%); £3,780,931.01 -> £3,395,712.38 (10.2%); £3,780,931.27 -> £3,395,712.41 (10.2%); £3,780,931.51 -> £3,395,712.43 (10.2%); £3,780,931.73 -> £3,395,712.45 (10.2%); £3,780,931.93 -> £3,395,712.47 (10.2%); £3,780,932.09 -> £3,395,712.49 (10.2%); £3,780,932.25 -> £3,395,712.51 (10.2%); £3,780,932.41 -> £3,395,712.53 (10.2%); £3,780,932.57 -> £3,395,712.54 (10.2%); £3,780,932.72 -> £3,395,712.56 (10.2%); £3,780,932.87 -> £3,395,712.58 (10.2%); £3,780,933.03 -> £3,395,712.59 (10.2%); £3,780,933.18 -> £3,395,712.61 (10.2%); £3,780,933.34 -> £3,395,712.63 (10.2%); £3,780,933.49 -> £3,395,712.64 (10.2%); £3,780,933.65 -> £3,395,712.66 (10.2%); £3,780,933.81 -> £3,395,712.81 (10.2%); £3,780,933.97 -> £3,395,712.95 (10.2%); £3,780,934.14 -> £3,395,713.10 (10.2%); £3,780,934.33 -> £3,395,713.26 (10.2%); £3,780,934.55 -> £3,395,713.42 (10.2%); £3,780,934.77 -> £3,395,713.57 (10.2%); £3,780,935.01 -> £3,395,713.72 (10.2%); £3,780,935.26 -> £3,395,713.87 (10.2%); £3,780,935.52 -> £3,395,713.90 (10.2%); £3,780,935.78 -> £3,395,713.92 (10.2%); £3,780,936.04 -> £3,395,713.95 (10.2%); £3,780,936.29 -> £3,395,713.97 (10.2%); £3,780,936.56 -> £3,395,713.99 (10.2%); £3,780,936.82 -> £3,395,714.02 (10.2%); £3,780,937.08 -> £3,395,714.04 (10.2%); £3,780,937.35 -> £3,395,714.07 (10.2%); £3,780,937.60 -> £3,395,714.09 (10.2%); £3,780,937.86 -> £3,395,714.11 (10.2%); £3,780,938.12 -> £3,395,714.14 (10.2%); £3,780,938.38 -> £3,395,714.16 (10.2%); £3,780,938.64 -> £3,395,714.19 (10.2%); £3,780,938.89 -> £3,395,714.35 (10.2%); £3,780,939.15 -> £3,395,714.52 (10.2%); £3,780,939.41 -> £3,395,714.68 (10.2%); £3,780,939.67 -> £3,395,714.85 (10.2%); £3,780,939.93 -> £3,395,715.02 (10.2%); £3,780,940.18 -> £3,395,715.18 (10.2%); £3,780,940.44 -> £3,395,715.35 (10.2%); £3,780,940.70 -> £3,395,715.51 (10.2%); £3,780,940.96 -> £3,395,715.67 (10.2%); £3,780,941.22 -> £3,395,715.83 (10.2%); £3,780,941.48 -> £3,395,715.98 (10.2%); £3,780,941.75 -> £3,395,716.01 (10.2%); £3,780,942.01 -> £3,395,716.04 (10.2%); £3,780,942.25 -> £3,395,716.06 (10.2%); £3,780,942.47 -> £3,395,716.08 (10.2%); £3,780,942.67 -> £3,395,716.10 (10.2%); £3,780,942.82 -> £3,395,716.12 (10.2%); £3,780,942.98 -> £3,395,716.14 (10.2%); £3,780,943.13 -> £3,395,716.16 (10.2%); £3,780,943.29 -> £3,395,716.17 (10.2%); £3,780,943.44 -> £3,395,716.19 (10.2%); £3,780,943.59 -> £3,395,716.21 (10.2%); £3,780,943.74 -> £3,395,716.22 (10.2%); £3,780,943.90 -> £3,395,716.24 (10.2%); £3,780,944.05 -> £3,395,716.25 (10.2%); £3,780,944.21 -> £3,395,716.27 (10.2%); £3,780,944.37 -> £3,395,716.29 (10.2%); £3,780,944.53 -> £3,395,716.37 (10.2%); £3,780,944.69 -> £3,395,716.47 (10.2%); £3,780,944.86 -> £3,395,716.56 (10.2%); £3,780,945.06 -> £3,395,716.66 (10.2%); £3,780,945.27 -> £3,395,716.76 (10.2%); £3,780,945.49 -> £3,395,716.86 (10.2%); £3,780,945.73 -> £3,395,716.95 (10.2%); £3,780,945.99 -> £3,395,717.04 (10.2%); £3,780,946.25 -> £3,395,717.07 (10.2%); £3,780,946.51 -> £3,395,717.09 (10.2%); £3,780,946.77 -> £3,395,717.12 (10.2%); £3,780,947.02 -> £3,395,717.14 (10.2%); £3,780,947.29 -> £3,395,717.16 (10.2%); £3,780,947.53 -> £3,395,717.19 (10.2%); £3,780,947.78 -> £3,395,717.21 (10.2%); £3,780,948.05 -> £3,395,717.24 (10.2%); £3,780,948.30 -> £3,395,717.26 (10.2%); £3,780,948.56 -> £3,395,717.28 (10.2%); £3,780,948.83 -> £3,395,717.31 (10.2%); £3,780,949.08 -> £3,395,717.33 (10.2%); £3,780,949.35 -> £3,395,717.36 (10.2%); £3,780,949.61 -> £3,395,717.46 (10.2%); £3,780,949.80 -> £3,395,717.57 (10.2%); £3,780,949.99 -> £3,395,717.68 (10.2%); £3,780,950.18 -> £3,395,717.79 (10.2%); £3,780,950.44 -> £3,395,717.90 (10.2%); £3,780,950.70 -> £3,395,718.01 (10.2%); £3,780,950.95 -> £3,395,718.12 (10.2%); £3,780,951.22 -> £3,395,718.23 (10.2%); £3,780,951.48 -> £3,395,718.34 (10.2%); £3,780,951.75 -> £3,395,718.44 (10.2%); £3,780,952.01 -> £3,395,718.55 (10.2%); £3,780,952.25 -> £3,395,718.58 (10.2%); £3,780,952.52 -> £3,395,718.61 (10.2%); £3,780,952.76 -> £3,395,718.63 (10.2%); £3,780,952.98 -> £3,395,718.65 (10.2%); £3,780,953.18 -> £3,395,718.67 (10.2%); £3,780,953.34 -> £3,395,718.69 (10.2%); £3,780,953.49 -> £3,395,718.71 (10.2%); £3,780,953.64 -> £3,395,718.73 (10.2%); £3,780,953.80 -> £3,395,718.74 (10.2%); £3,780,953.96 -> £3,395,718.76 (10.2%); £3,780,954.11 -> £3,395,718.78 (10.2%); £3,780,954.27 -> £3,395,718.79 (10.2%); £3,780,954.43 -> £3,395,718.81 (10.2%); £3,780,954.59 -> £3,395,718.83 (10.2%); £3,780,954.75 -> £3,395,718.84 (10.2%); £3,780,954.91 -> £3,395,718.86 (10.2%); £3,780,955.06 -> £3,395,718.92 (10.2%); £3,780,955.22 -> £3,395,718.99 (10.2%); £3,780,955.39 -> £3,395,719.06 (10.2%); £3,780,955.58 -> £3,395,719.13 (10.2%); £3,780,955.79 -> £3,395,719.21 (10.2%); £3,780,956.02 -> £3,395,719.28 (10.2%); £3,780,956.26 -> £3,395,719.35 (10.2%); £3,780,956.52 -> £3,395,719.42 (10.2%); £3,780,956.80 -> £3,395,719.44 (10.2%); £3,780,957.06 -> £3,395,719.47 (10.2%); £3,780,957.32 -> £3,395,719.49 (10.2%); £3,780,957.59 -> £3,395,719.52 (10.2%); £3,780,957.85 -> £3,395,719.54 (10.2%); £3,780,958.11 -> £3,395,719.56 (10.2%); £3,780,958.37 -> £3,395,719.59 (10.2%); £3,780,958.63 -> £3,395,719.61 (10.2%); £3,780,958.90 -> £3,395,719.63 (10.2%); £3,780,959.15 -> £3,395,719.66 (10.2%); £3,780,959.40 -> £3,395,719.68 (10.2%); £3,780,959.66 -> £3,395,719.71 (10.2%); £3,780,959.93 -> £3,395,719.74 (10.2%); £3,780,960.18 -> £3,395,719.82 (10.2%); £3,780,960.45 -> £3,395,719.91 (10.2%); £3,780,960.71 -> £3,395,720.00 (10.2%); £3,780,960.96 -> £3,395,720.09 (10.2%); £3,780,961.23 -> £3,395,720.18 (10.2%); £3,780,961.49 -> £3,395,720.27 (10.2%); £3,780,961.75 -> £3,395,720.35 (10.2%); £3,780,962.01 -> £3,395,720.44 (10.2%); £3,780,962.27 -> £3,395,720.52 (10.2%); £3,780,962.52 -> £3,395,720.60 (10.2%); £3,780,962.77 -> £3,395,720.68 (10.2%); £3,780,963.03 -> £3,395,720.71 (10.2%); £3,780,963.29 -> £3,395,720.74 (10.2%); £3,780,963.53 -> £3,395,720.76 (10.2%); £3,780,963.75 -> £3,395,720.78 (10.2%); £3,780,963.95 -> £3,395,720.80 (10.2%); £3,780,964.11 -> £3,395,720.82 (10.2%); £3,780,964.27 -> £3,395,720.84 (10.2%); £3,780,964.42 -> £3,395,720.86 (10.2%); £3,780,964.58 -> £3,395,720.87 (10.2%); £3,780,964.74 -> £3,395,720.89 (10.2%); £3,780,964.90 -> £3,395,720.91 (10.2%); £3,780,965.05 -> £3,395,720.92 (10.2%); £3,780,965.21 -> £3,395,720.94 (10.2%); £3,780,965.37 -> £3,395,720.96 (10.2%); £3,780,965.53 -> £3,395,720.97 (10.2%); £3,780,965.69 -> £3,395,720.99 (10.2%); £3,780,965.85 -> £3,395,721.09 (10.2%); £3,780,966.01 -> £3,395,721.20 (10.2%); £3,780,966.19 -> £3,395,721.31 (10.2%); £3,780,966.38 -> £3,395,721.42 (10.2%); £3,780,966.59 -> £3,395,721.53 (10.2%); £3,780,966.82 -> £3,395,721.64 (10.2%); £3,780,967.07 -> £3,395,721.75 (10.2%); £3,780,967.33 -> £3,395,721.85 (10.2%); £3,780,967.59 -> £3,395,721.88 (10.2%); £3,780,967.86 -> £3,395,721.90 (10.2%); £3,780,968.12 -> £3,395,721.93 (10.2%); £3,780,968.37 -> £3,395,721.95 (10.2%); £3,780,968.63 -> £3,395,721.97 (10.2%); £3,780,968.90 -> £3,395,722.00 (10.2%); £3,780,969.15 -> £3,395,722.02 (10.2%); £3,780,969.41 -> £3,395,722.04 (10.2%); £3,780,969.67 -> £3,395,722.07 (10.2%); £3,780,969.93 -> £3,395,722.09 (10.2%); £3,780,970.19 -> £3,395,722.11 (10.2%); £3,780,970.46 -> £3,395,722.14 (10.2%); £3,780,970.71 -> £3,395,722.17 (10.2%); £3,780,970.91 -> £3,395,722.28 (10.2%); £3,780,971.19 -> £3,395,722.40 (10.2%); £3,780,971.38 -> £3,395,722.53 (10.2%); £3,780,971.57 -> £3,395,722.65 (10.2%); £3,780,971.77 -> £3,395,722.77 (10.2%); £3,780,971.96 -> £3,395,722.88 (10.2%); £3,780,972.15 -> £3,395,723.00 (10.2%); £3,780,972.41 -> £3,395,723.12 (10.2%); £3,780,972.67 -> £3,395,723.23 (10.2%); £3,780,972.93 -> £3,395,723.35 (10.2%); £3,780,973.20 -> £3,395,723.47 (10.2%); £3,780,973.46 -> £3,395,723.50 (10.2%); £3,780,973.74 -> £3,395,723.53 (10.2%); £3,780,973.98 -> £3,395,723.55 (10.2%); £3,780,974.19 -> £3,395,723.57 (10.2%); £3,780,974.39 -> £3,395,723.59 (10.2%); £3,780,974.53 -> £3,395,723.61 (10.2%); £3,780,974.67 -> £3,395,723.63 (10.2%); £3,780,974.81 -> £3,395,723.65 (10.2%); £3,780,974.95 -> £3,395,723.67 (10.2%); £3,780,975.09 -> £3,395,723.68 (10.2%); £3,780,975.22 -> £3,395,723.70 (10.2%); £3,780,975.36 -> £3,395,723.72 (10.2%); £3,780,975.51 -> £3,395,723.73 (10.2%); £3,780,975.64 -> £3,395,723.75 (10.2%); £3,780,975.77 -> £3,395,723.77 (10.2%); £3,780,975.91 -> £3,395,723.79 (10.2%); £3,780,976.05 -> £3,395,723.87 (10.2%); £3,780,976.19 -> £3,395,723.96 (10.2%); £3,780,976.35 -> £3,395,724.05 (10.2%); £3,780,976.51 -> £3,395,724.15 (10.2%); £3,780,976.70 -> £3,395,724.24 (10.2%); £3,780,976.90 -> £3,395,724.34 (10.2%); £3,780,977.11 -> £3,395,724.44 (10.2%); £3,780,977.33 -> £3,395,724.54 (10.2%); £3,780,977.56 -> £3,395,724.56 (10.2%); £3,780,977.78 -> £3,395,724.59 (10.2%); £3,780,978.00 -> £3,395,724.62 (10.2%); £3,780,978.23 -> £3,395,724.64 (10.2%); £3,780,978.47 -> £3,395,724.67 (10.2%); £3,780,978.70 -> £3,395,724.70 (10.2%); £3,780,978.92 -> £3,395,724.72 (10.2%); £3,780,979.15 -> £3,395,724.75 (10.2%); £3,780,979.37 -> £3,395,724.77 (10.2%); £3,780,979.60 -> £3,395,724.80 (10.2%); £3,780,979.83 -> £3,395,724.82 (10.2%); £3,780,980.06 -> £3,395,724.85 (10.2%); £3,780,980.28 -> £3,395,724.88 (10.2%); £3,780,980.45 -> £3,395,724.98 (10.2%); £3,780,980.62 -> £3,395,725.09 (10.2%); £3,780,980.79 -> £3,395,725.20 (10.2%); £3,780,980.97 -> £3,395,725.31 (10.2%); £3,780,981.14 -> £3,395,725.42 (10.2%); £3,780,981.31 -> £3,395,725.53 (10.2%); £3,780,981.48 -> £3,395,725.64 (10.2%); £3,780,981.71 -> £3,395,725.74 (10.2%); £3,780,981.94 -> £3,395,725.85 (10.2%); £3,780,982.17 -> £3,395,725.95 (10.2%); £3,780,982.40 -> £3,395,726.05 (10.2%); £3,780,982.62 -> £3,395,726.08 (10.2%); £3,780,982.85 -> £3,395,726.11 (10.2%); £3,780,983.06 -> £3,395,726.13 (10.2%); £3,780,983.26 -> £3,395,726.16 (10.2%); £3,780,983.43 -> £3,395,726.18 (10.2%); £3,780,983.57 -> £3,395,726.20 (10.2%); £3,780,983.71 -> £3,395,726.22 (10.2%); £3,780,983.85 -> £3,395,726.24 (10.2%); £3,780,983.98 -> £3,395,726.25 (10.2%); £3,780,984.12 -> £3,395,726.27 (10.2%); £3,780,984.26 -> £3,395,726.29 (10.2%); £3,780,984.40 -> £3,395,726.31 (10.2%); £3,780,984.54 -> £3,395,726.32 (10.2%); £3,780,984.68 -> £3,395,726.34 (10.2%); £3,780,984.82 -> £3,395,726.36 (10.2%); £3,780,984.95 -> £3,395,726.37 (10.2%); £3,780,985.08 -> £3,395,726.46 (10.2%); £3,780,985.22 -> £3,395,726.55 (10.2%); £3,780,985.38 -> £3,395,726.64 (10.2%); £3,780,985.55 -> £3,395,726.73 (10.2%); £3,780,985.74 -> £3,395,726.83 (10.2%); £3,780,985.93 -> £3,395,726.92 (10.2%); £3,780,986.15 -> £3,395,727.02 (10.2%); £3,780,986.37 -> £3,395,727.13 (10.2%); £3,780,986.60 -> £3,395,727.16 (10.2%); £3,780,986.83 -> £3,395,727.19 (10.2%); £3,780,987.06 -> £3,395,727.22 (10.2%); £3,780,987.30 -> £3,395,727.25 (10.2%); £3,780,987.52 -> £3,395,727.28 (10.2%); £3,780,987.75 -> £3,395,727.31 (10.2%); £3,780,987.98 -> £3,395,727.34 (10.2%); £3,780,988.21 -> £3,395,727.38 (10.2%); £3,780,988.44 -> £3,395,727.40 (10.2%); £3,780,988.67 -> £3,395,727.43 (10.2%); £3,780,988.91 -> £3,395,727.46 (10.2%); £3,780,989.14 -> £3,395,727.49 (10.2%); £3,780,989.36 -> £3,395,727.52 (10.2%); £3,780,989.60 -> £3,395,727.63 (10.2%); £3,780,989.84 -> £3,395,727.75 (10.2%); £3,780,990.06 -> £3,395,727.86 (10.2%); £3,780,990.23 -> £3,395,727.97 (10.2%); £3,780,990.46 -> £3,395,728.09 (10.2%); £3,780,990.63 -> £3,395,728.20 (10.2%); £3,780,990.80 -> £3,395,728.31 (10.2%); £3,780,991.03 -> £3,395,728.42 (10.2%); £3,780,991.26 -> £3,395,728.53 (10.2%); £3,780,991.49 -> £3,395,728.64 (10.2%); £3,780,991.72 -> £3,395,728.75 (10.2%); £3,780,991.94 -> £3,395,728.78 (10.2%); £3,780,992.17 -> £3,395,728.81 (10.2%); £3,780,992.37 -> £3,395,728.83 (10.2%); £3,780,992.57 -> £3,395,728.86 (10.2%); £3,780,992.74 -> £3,395,728.88 (10.2%); £3,780,992.90 -> £3,395,728.90 (10.2%); £3,780,993.07 -> £3,395,728.91 (10.2%); £3,780,993.23 -> £3,395,728.93 (10.2%); £3,780,993.39 -> £3,395,728.95 (10.2%); £3,780,993.55 -> £3,395,728.97 (10.2%); £3,780,993.71 -> £3,395,728.98 (10.2%); £3,780,993.86 -> £3,395,729.00 (10.2%); £3,780,994.03 -> £3,395,729.02 (10.2%); £3,780,994.18 -> £3,395,729.03 (10.2%); £3,780,994.34 -> £3,395,729.05 (10.2%); £3,780,994.50 -> £3,395,729.07 (10.2%); £3,780,994.67 -> £3,395,729.19 (10.2%); £3,780,994.83 -> £3,395,729.31 (10.2%); £3,780,995.00 -> £3,395,729.44 (10.2%); £3,780,995.19 -> £3,395,729.57 (10.2%); £3,780,995.40 -> £3,395,729.70 (10.2%); £3,780,995.63 -> £3,395,729.83 (10.2%); £3,780,995.88 -> £3,395,729.95 (10.2%); £3,780,996.13 -> £3,395,730.08 (10.2%); £3,780,996.39 -> £3,395,730.10 (10.2%); £3,780,996.65 -> £3,395,730.13 (10.2%); £3,780,996.92 -> £3,395,730.15 (10.2%); £3,780,997.18 -> £3,395,730.18 (10.2%); £3,780,997.45 -> £3,395,730.20 (10.2%); £3,780,997.72 -> £3,395,730.23 (10.2%); £3,780,997.98 -> £3,395,730.25 (10.2%); £3,780,998.25 -> £3,395,730.27 (10.2%); £3,780,998.52 -> £3,395,730.29 (10.2%); £3,780,998.79 -> £3,395,730.32 (10.2%); £3,780,999.05 -> £3,395,730.34 (10.2%); £3,780,999.31 -> £3,395,730.37 (10.2%); £3,780,999.57 -> £3,395,730.40 (10.2%); £3,780,999.83 -> £3,395,730.53 (10.2%); £3,781,000.02 -> £3,395,730.67 (10.2%); £3,781,000.22 -> £3,395,730.81 (10.2%); £3,781,000.42 -> £3,395,730.95 (10.2%); £3,781,000.68 -> £3,395,731.10 (10.2%); £3,781,000.93 -> £3,395,731.24 (10.2%); £3,781,001.20 -> £3,395,731.38 (10.2%); £3,781,001.47 -> £3,395,731.51 (10.2%); £3,781,001.73 -> £3,395,731.65 (10.2%); £3,781,002.00 -> £3,395,731.79 (10.2%); £3,781,002.26 -> £3,395,731.92 (10.2%); £3,781,002.53 -> £3,395,731.95 (10.2%); £3,781,002.79 -> £3,395,731.98 (10.2%); £3,781,003.05 -> £3,395,732.01 (10.2%); £3,781,003.27 -> £3,395,732.03 (10.2%); £3,781,003.47 -> £3,395,732.05 (10.2%); £3,781,003.63 -> £3,395,732.07 (10.2%); £3,781,003.79 -> £3,395,732.08 (10.2%); £3,781,003.95 -> £3,395,732.10 (10.2%); £3,781,004.11 -> £3,395,732.12 (10.2%); £3,781,004.26 -> £3,395,732.13 (10.2%); £3,781,004.42 -> £3,395,732.15 (10.2%); £3,781,004.58 -> £3,395,732.17 (10.2%); £3,781,004.74 -> £3,395,732.18 (10.2%); £3,781,004.90 -> £3,395,732.20 (10.2%); £3,781,005.06 -> £3,395,732.22 (10.2%); £3,781,005.22 -> £3,395,732.23 (10.2%); £3,781,005.37 -> £3,395,732.35 (10.2%); £3,781,005.53 -> £3,395,732.46 (10.2%); £3,781,005.70 -> £3,395,732.58 (10.2%); £3,781,005.90 -> £3,395,732.71 (10.2%); £3,781,006.11 -> £3,395,732.83 (10.2%); £3,781,006.34 -> £3,395,732.95 (10.2%); £3,781,006.59 -> £3,395,733.07 (10.2%); £3,781,006.85 -> £3,395,733.19 (10.2%); £3,781,007.12 -> £3,395,733.22 (10.2%); £3,781,007.38 -> £3,395,733.24 (10.2%); £3,781,007.66 -> £3,395,733.26 (10.2%); £3,781,007.92 -> £3,395,733.29 (10.2%); £3,781,008.18 -> £3,395,733.31 (10.2%); £3,781,008.44 -> £3,395,733.34 (10.2%); £3,781,008.70 -> £3,395,733.36 (10.2%); £3,781,008.97 -> £3,395,733.39 (10.2%); £3,781,009.23 -> £3,395,733.41 (10.2%); £3,781,009.49 -> £3,395,733.43 (10.2%); £3,781,009.76 -> £3,395,733.46 (10.2%); £3,781,010.03 -> £3,395,733.48 (10.2%); £3,781,010.29 -> £3,395,733.51 (10.2%); £3,781,010.56 -> £3,395,733.64 (10.2%); £3,781,010.82 -> £3,395,733.78 (10.2%); £3,781,011.08 -> £3,395,733.92 (10.2%); £3,781,011.35 -> £3,395,734.05 (10.2%); £3,781,011.61 -> £3,395,734.19 (10.2%); £3,781,011.88 -> £3,395,734.32 (10.2%); £3,781,012.08 -> £3,395,734.45 (10.2%); £3,781,012.33 -> £3,395,734.58 (10.2%); £3,781,012.59 -> £3,395,734.71 (10.2%); £3,781,012.85 -> £3,395,734.84 (10.2%); £3,781,013.13 -> £3,395,734.97 (10.2%); £3,781,013.39 -> £3,395,735.00 (10.2%); £3,781,013.65 -> £3,395,735.03 (10.2%); £3,781,013.90 -> £3,395,735.05 (10.2%); £3,781,014.12 -> £3,395,735.08 (10.2%); £3,781,014.32 -> £3,395,735.10 (10.2%); £3,781,014.49 -> £3,395,735.11 (10.2%); £3,781,014.65 -> £3,395,735.13 (10.2%); £3,781,014.81 -> £3,395,735.15 (10.2%); £3,781,014.97 -> £3,395,735.17 (10.2%); £3,781,015.14 -> £3,395,735.18 (10.2%); £3,781,015.29 -> £3,395,735.20 (10.2%); £3,781,015.46 -> £3,395,735.22 (10.2%); £3,781,015.62 -> £3,395,735.23 (10.2%); £3,781,015.77 -> £3,395,735.25 (10.2%); £3,781,015.94 -> £3,395,735.27 (10.2%); £3,781,016.10 -> £3,395,735.28 (10.2%); £3,781,016.26 -> £3,395,735.40 (10.2%); £3,781,016.42 -> £3,395,735.50 (10.2%); £3,781,016.60 -> £3,395,735.62 (10.2%); £3,781,016.80 -> £3,395,735.73 (10.2%); £3,781,017.01 -> £3,395,735.85 (10.2%); £3,781,017.23 -> £3,395,735.97 (10.2%); £3,781,017.48 -> £3,395,736.08 (10.2%); £3,781,017.75 -> £3,395,736.19 (10.2%); £3,781,018.02 -> £3,395,736.22 (10.2%); £3,781,018.28 -> £3,395,736.24 (10.2%); £3,781,018.55 -> £3,395,736.26 (10.2%); £3,781,018.82 -> £3,395,736.29 (10.2%); £3,781,019.08 -> £3,395,736.31 (10.2%); £3,781,019.34 -> £3,395,736.34 (10.2%); £3,781,019.62 -> £3,395,736.36 (10.2%); £3,781,019.89 -> £3,395,736.38 (10.2%); £3,781,020.16 -> £3,395,736.41 (10.2%); £3,781,020.42 -> £3,395,736.43 (10.2%); £3,781,020.69 -> £3,395,736.45 (10.2%); £3,781,020.96 -> £3,395,736.48 (10.2%); £3,781,021.23 -> £3,395,736.51 (10.2%); £3,781,021.49 -> £3,395,736.63 (10.2%); £3,781,021.76 -> £3,395,736.75 (10.2%); £3,781,022.02 -> £3,395,736.88 (10.2%); £3,781,022.29 -> £3,395,737.01 (10.2%); £3,781,022.49 -> £3,395,737.14 (10.2%); £3,781,022.69 -> £3,395,737.26 (10.2%); £3,781,022.96 -> £3,395,737.39 (10.2%); £3,781,023.22 -> £3,395,737.51 (10.2%); £3,781,023.48 -> £3,395,737.64 (10.2%); £3,781,023.75 -> £3,395,737.76 (10.2%); £3,781,024.02 -> £3,395,737.89 (10.2%); £3,781,024.29 -> £3,395,737.92 (10.2%); £3,781,024.55 -> £3,395,737.95 (10.2%); £3,781,024.80 -> £3,395,737.97 (10.2%); £3,781,025.03 -> £3,395,737.99 (10.2%); £3,781,025.23 -> £3,395,738.01 (10.2%); £3,781,025.39 -> £3,395,738.03 (10.2%); £3,781,025.54 -> £3,395,738.05 (10.2%); £3,781,025.70 -> £3,395,738.07 (10.2%); £3,781,025.86 -> £3,395,738.08 (10.2%); £3,781,026.03 -> £3,395,738.10 (10.2%); £3,781,026.19 -> £3,395,738.12 (10.2%); £3,781,026.35 -> £3,395,738.13 (10.2%); £3,781,026.52 -> £3,395,738.15 (10.2%); £3,781,026.68 -> £3,395,738.17 (10.2%); £3,781,026.84 -> £3,395,738.18 (10.2%); £3,781,027.00 -> £3,395,738.20 (10.2%); £3,781,027.16 -> £3,395,738.35 (10.2%); £3,781,027.31 -> £3,395,738.49 (10.2%); £3,781,027.50 -> £3,395,738.64 (10.2%); £3,781,027.69 -> £3,395,738.80 (10.2%); £3,781,027.91 -> £3,395,738.95 (10.2%); £3,781,028.14 -> £3,395,739.10 (10.2%); £3,781,028.40 -> £3,395,739.25 (10.2%); £3,781,028.66 -> £3,395,739.40 (10.2%); £3,781,028.93 -> £3,395,739.42 (10.2%); £3,781,029.20 -> £3,395,739.44 (10.2%); £3,781,029.46 -> £3,395,739.47 (10.2%); £3,781,029.73 -> £3,395,739.49 (10.2%); £3,781,029.98 -> £3,395,739.52 (10.2%); £3,781,030.26 -> £3,395,739.54 (10.2%); £3,781,030.54 -> £3,395,739.56 (10.2%); £3,781,030.81 -> £3,395,739.58 (10.2%); £3,781,031.07 -> £3,395,739.61 (10.2%); £3,781,031.33 -> £3,395,739.63 (10.2%); £3,781,031.60 -> £3,395,739.65 (10.2%); £3,781,031.86 -> £3,395,739.68 (10.2%); £3,781,032.14 -> £3,395,739.71 (10.2%); £3,781,032.41 -> £3,395,739.87 (10.2%); £3,781,032.68 -> £3,395,740.04 (10.2%); £3,781,032.95 -> £3,395,740.20 (10.2%); £3,781,033.22 -> £3,395,740.36 (10.2%); £3,781,033.42 -> £3,395,740.53 (10.2%); £3,781,033.69 -> £3,395,740.70 (10.2%); £3,781,033.96 -> £3,395,740.86 (10.2%); £3,781,034.23 -> £3,395,741.02 (10.2%); £3,781,034.50 -> £3,395,741.18 (10.2%); £3,781,034.78 -> £3,395,741.34 (10.2%); £3,781,035.04 -> £3,395,741.49 (10.2%); £3,781,035.30 -> £3,395,741.52 (10.2%); £3,781,035.57 -> £3,395,741.55 (10.2%); £3,781,035.81 -> £3,395,741.57 (10.2%); £3,781,036.04 -> £3,395,741.59 (10.2%); £3,781,036.25 -> £3,395,741.61 (10.2%); £3,781,036.41 -> £3,395,741.63 (10.2%); £3,781,036.57 -> £3,395,741.65 (10.2%); £3,781,036.73 -> £3,395,741.67 (10.2%); £3,781,036.89 -> £3,395,741.68 (10.2%); £3,781,037.05 -> £3,395,741.70 (10.2%); £3,781,037.21 -> £3,395,741.72 (10.2%); £3,781,037.37 -> £3,395,741.73 (10.2%); £3,781,037.53 -> £3,395,741.75 (10.2%); £3,781,037.70 -> £3,395,741.77 (10.2%); £3,781,037.86 -> £3,395,741.78 (10.2%); £3,781,038.02 -> £3,395,741.80 (10.2%); £3,781,038.18 -> £3,395,741.98 (10.2%); £3,781,038.33 -> £3,395,742.17 (10.2%); £3,781,038.51 -> £3,395,742.37 (10.2%); £3,781,038.71 -> £3,395,742.57 (10.2%); £3,781,038.92 -> £3,395,742.77 (10.2%); £3,781,039.15 -> £3,395,742.97 (10.2%); £3,781,039.40 -> £3,395,743.16 (10.2%); £3,781,039.68 -> £3,395,743.36 (10.2%); £3,781,039.93 -> £3,395,743.38 (10.2%); £3,781,040.20 -> £3,395,743.41 (10.2%); £3,781,040.45 -> £3,395,743.43 (10.2%); £3,781,040.71 -> £3,395,743.45 (10.2%); £3,781,040.97 -> £3,395,743.48 (10.2%); £3,781,041.24 -> £3,395,743.50 (10.2%); £3,781,041.49 -> £3,395,743.53 (10.2%); £3,781,041.77 -> £3,395,743.55 (10.2%); £3,781,042.04 -> £3,395,743.57 (10.2%); £3,781,042.30 -> £3,395,743.60 (10.2%); £3,781,042.57 -> £3,395,743.62 (10.2%); £3,781,042.84 -> £3,395,743.64 (10.2%); £3,781,043.10 -> £3,395,743.67 (10.2%); £3,781,043.36 -> £3,395,743.87 (10.2%); £3,781,043.62 -> £3,395,744.07 (10.2%); £3,781,043.82 -> £3,395,744.27 (10.2%); £3,781,044.02 -> £3,395,744.46 (10.2%); £3,781,044.22 -> £3,395,744.66 (10.2%); £3,781,044.42 -> £3,395,744.86 (10.2%); £3,781,044.62 -> £3,395,745.05 (10.2%); £3,781,044.89 -> £3,395,745.24 (10.2%); £3,781,045.15 -> £3,395,745.43 (10.2%); £3,781,045.43 -> £3,395,745.63 (10.2%); £3,781,045.68 -> £3,395,745.82 (10.2%); £3,781,045.96 -> £3,395,745.85 (10.2%); £3,781,046.22 -> £3,395,745.87 (10.2%); £3,781,046.46 -> £3,395,745.90 (10.2%); £3,781,046.68 -> £3,395,745.92 (10.2%); £3,781,046.88 -> £3,395,745.94 (10.2%); £3,781,047.02 -> £3,395,745.96 (10.2%); £3,781,047.16 -> £3,395,745.98 (10.2%); £3,781,047.30 -> £3,395,746.00 (10.2%); £3,781,047.44 -> £3,395,746.01 (10.2%); £3,781,047.59 -> £3,395,746.03 (10.2%); £3,781,047.72 -> £3,395,746.05 (10.2%); £3,781,047.87 -> £3,395,746.06 (10.2%); £3,781,048.01 -> £3,395,746.08 (10.2%); £3,781,048.14 -> £3,395,746.10 (10.2%); £3,781,048.28 -> £3,395,746.11 (10.2%); £3,781,048.43 -> £3,395,746.13 (10.2%); £3,781,048.57 -> £3,395,746.33 (10.2%); £3,781,048.71 -> £3,395,746.53 (10.2%); £3,781,048.86 -> £3,395,746.74 (10.2%); £3,781,049.04 -> £3,395,746.94 (10.2%); £3,781,049.23 -> £3,395,747.14 (10.2%); £3,781,049.43 -> £3,395,747.35 (10.2%); £3,781,049.66 -> £3,395,747.56 (10.2%); £3,781,049.89 -> £3,395,747.76 (10.2%); £3,781,050.13 -> £3,395,747.79 (10.2%); £3,781,050.36 -> £3,395,747.82 (10.2%); £3,781,050.59 -> £3,395,747.84 (10.2%); £3,781,050.83 -> £3,395,747.87 (10.2%); £3,781,051.06 -> £3,395,747.90 (10.2%); £3,781,051.29 -> £3,395,747.92 (10.2%); £3,781,051.52 -> £3,395,747.95 (10.2%); £3,781,051.75 -> £3,395,747.97 (10.2%); £3,781,052.00 -> £3,395,748.00 (10.2%); £3,781,052.23 -> £3,395,748.03 (10.2%); £3,781,052.47 -> £3,395,748.05 (10.2%); £3,781,052.72 -> £3,395,748.08 (10.2%); £3,781,052.95 -> £3,395,748.10 (10.2%); £3,781,053.13 -> £3,395,748.30 (10.2%); £3,781,053.30 -> £3,395,748.51 (10.2%); £3,781,053.47 -> £3,395,748.72 (10.2%); £3,781,053.65 -> £3,395,748.92 (10.2%); £3,781,053.82 -> £3,395,749.13 (10.2%); £3,781,054.00 -> £3,395,749.33 (10.2%); £3,781,054.18 -> £3,395,749.54 (10.2%); £3,781,054.42 -> £3,395,749.74 (10.2%); £3,781,054.66 -> £3,395,749.94 (10.2%); £3,781,054.89 -> £3,395,750.14 (10.2%); £3,781,055.13 -> £3,395,750.34 (10.2%); £3,781,055.36 -> £3,395,750.37 (10.2%); £3,781,055.60 -> £3,395,750.40 (10.2%); £3,781,055.81 -> £3,395,750.42 (10.2%); £3,781,056.01 -> £3,395,750.45 (10.2%); £3,781,056.20 -> £3,395,750.47 (10.2%); £3,781,056.34 -> £3,395,750.49 (10.2%); £3,781,056.49 -> £3,395,750.51 (10.2%); £3,781,056.62 -> £3,395,750.53 (10.2%); £3,781,056.76 -> £3,395,750.54 (10.2%); £3,781,056.90 -> £3,395,750.56 (10.2%); £3,781,057.04 -> £3,395,750.58 (10.2%); £3,781,057.18 -> £3,395,750.59 (10.2%); £3,781,057.32 -> £3,395,750.61 (10.2%); £3,781,057.46 -> £3,395,750.63 (10.2%); £3,781,057.60 -> £3,395,750.64 (10.2%); £3,781,057.74 -> £3,395,750.66 (10.2%); £3,781,057.88 -> £3,395,750.84 (10.2%); £3,781,058.02 -> £3,395,751.02 (10.2%); £3,781,058.17 -> £3,395,751.21 (10.2%); £3,781,058.35 -> £3,395,751.39 (10.2%); £3,781,058.54 -> £3,395,751.58 (10.2%); £3,781,058.73 -> £3,395,751.78 (10.2%); £3,781,058.95 -> £3,395,751.97 (10.2%); £3,781,059.18 -> £3,395,752.17 (10.2%); £3,781,059.43 -> £3,395,752.20 (10.2%); £3,781,059.66 -> £3,395,752.23 (10.2%); £3,781,059.91 -> £3,395,752.26 (10.2%); £3,781,060.13 -> £3,395,752.29 (10.2%); £3,781,060.37 -> £3,395,752.32 (10.2%); £3,781,060.60 -> £3,395,752.36 (10.2%); £3,781,060.83 -> £3,395,752.39 (10.2%); £3,781,061.08 -> £3,395,752.42 (10.2%); £3,781,061.30 -> £3,395,752.44 (10.2%); £3,781,061.54 -> £3,395,752.47 (10.2%); £3,781,061.77 -> £3,395,752.50 (10.2%); £3,781,062.00 -> £3,395,752.53 (10.2%); £3,781,062.24 -> £3,395,752.56 (10.2%); £3,781,062.42 -> £3,395,752.75 (10.2%); £3,781,062.59 -> £3,395,752.94 (10.2%); £3,781,062.77 -> £3,395,753.13 (10.2%); £3,781,062.95 -> £3,395,753.33 (10.2%); £3,781,063.18 -> £3,395,753.53 (10.2%); £3,781,063.41 -> £3,395,753.72 (10.2%); £3,781,063.59 -> £3,395,753.92 (10.2%); £3,781,063.82 -> £3,395,754.12 (10.2%); £3,781,064.06 -> £3,395,754.31 (10.2%); £3,781,064.28 -> £3,395,754.51 (10.2%); £3,781,064.52 -> £3,395,754.70 (10.2%); £3,781,064.75 -> £3,395,754.73 (10.2%); £3,781,064.99 -> £3,395,754.76 (10.2%); £3,781,065.20 -> £3,395,754.78 (10.2%); £3,781,065.40 -> £3,395,754.81 (10.2%); £3,781,065.57 -> £3,395,754.83 (10.2%); £3,781,065.74 -> £3,395,754.85 (10.2%); £3,781,065.90 -> £3,395,754.86 (10.2%); £3,781,066.05 -> £3,395,754.88 (10.2%); £3,781,066.21 -> £3,395,754.90 (10.2%); £3,781,066.38 -> £3,395,754.91 (10.2%); £3,781,066.53 -> £3,395,754.93 (10.2%); £3,781,066.69 -> £3,395,754.95 (10.2%); £3,781,066.85 -> £3,395,754.96 (10.2%); £3,781,067.02 -> £3,395,754.98 (10.2%); £3,781,067.18 -> £3,395,755.00 (10.2%); £3,781,067.34 -> £3,395,755.02 (10.2%); £3,781,067.50 -> £3,395,755.18 (10.2%); £3,781,067.65 -> £3,395,755.35 (10.2%); £3,781,067.83 -> £3,395,755.52 (10.2%); £3,781,068.02 -> £3,395,755.69 (10.2%); £3,781,068.24 -> £3,395,755.87 (10.2%); £3,781,068.47 -> £3,395,756.05 (10.2%); £3,781,068.71 -> £3,395,756.22 (10.2%); £3,781,068.97 -> £3,395,756.39 (10.2%); £3,781,069.24 -> £3,395,756.41 (10.2%); £3,781,069.50 -> £3,395,756.43 (10.2%); £3,781,069.77 -> £3,395,756.46 (10.2%); £3,781,070.04 -> £3,395,756.48 (10.2%); £3,781,070.30 -> £3,395,756.51 (10.2%); £3,781,070.55 -> £3,395,756.53 (10.2%); £3,781,070.82 -> £3,395,756.55 (10.2%); £3,781,071.09 -> £3,395,756.58 (10.2%); £3,781,071.36 -> £3,395,756.60 (10.2%); £3,781,071.62 -> £3,395,756.62 (10.2%); £3,781,071.88 -> £3,395,756.65 (10.2%); £3,781,072.14 -> £3,395,756.67 (10.2%); £3,781,072.41 -> £3,395,756.70 (10.2%); £3,781,072.67 -> £3,395,756.88 (10.2%); £3,781,072.94 -> £3,395,757.06 (10.2%); £3,781,073.21 -> £3,395,757.25 (10.2%); £3,781,073.47 -> £3,395,757.43 (10.2%); £3,781,073.73 -> £3,395,757.61 (10.2%); £3,781,073.98 -> £3,395,757.79 (10.2%); £3,781,074.18 -> £3,395,757.97 (10.2%); £3,781,074.44 -> £3,395,758.15 (10.2%); £3,781,074.71 -> £3,395,758.33 (10.2%); £3,781,074.96 -> £3,395,758.51 (10.2%); £3,781,075.22 -> £3,395,758.68 (10.2%); £3,781,075.48 -> £3,395,758.71 (10.2%); £3,781,075.74 -> £3,395,758.74 (10.2%); £3,781,075.99 -> £3,395,758.76 (10.2%); £3,781,076.21 -> £3,395,758.78 (10.2%); £3,781,076.42 -> £3,395,758.80 (10.2%); £3,781,076.58 -> £3,395,758.82 (10.2%); £3,781,076.73 -> £3,395,758.84 (10.2%); £3,781,076.89 -> £3,395,758.86 (10.2%); £3,781,077.04 -> £3,395,758.87 (10.2%); £3,781,077.20 -> £3,395,758.89 (10.2%); £3,781,077.36 -> £3,395,758.91 (10.2%); £3,781,077.52 -> £3,395,758.92 (10.2%); £3,781,077.67 -> £3,395,758.94 (10.2%); £3,781,077.83 -> £3,395,758.96 (10.2%); £3,781,077.99 -> £3,395,758.97 (10.2%); £3,781,078.14 -> £3,395,758.99 (10.2%); £3,781,078.30 -> £3,395,759.18 (10.2%); £3,781,078.46 -> £3,395,759.38 (10.2%); £3,781,078.63 -> £3,395,759.57 (10.2%); £3,781,078.82 -> £3,395,759.77 (10.2%); £3,781,079.03 -> £3,395,759.97 (10.2%); £3,781,079.26 -> £3,395,760.17 (10.2%); £3,781,079.51 -> £3,395,760.36 (10.2%); £3,781,079.77 -> £3,395,760.56 (10.2%); £3,781,080.03 -> £3,395,760.58 (10.2%); £3,781,080.29 -> £3,395,760.61 (10.2%); £3,781,080.54 -> £3,395,760.63 (10.2%); £3,781,080.79 -> £3,395,760.65 (10.2%); £3,781,081.06 -> £3,395,760.68 (10.2%); £3,781,081.32 -> £3,395,760.70 (10.2%); £3,781,081.58 -> £3,395,760.73 (10.2%); £3,781,081.85 -> £3,395,760.75 (10.2%); £3,781,082.10 -> £3,395,760.77 (10.2%); £3,781,082.37 -> £3,395,760.80 (10.2%); £3,781,082.62 -> £3,395,760.82 (10.2%); £3,781,082.88 -> £3,395,760.85 (10.2%); £3,781,083.14 -> £3,395,760.87 (10.2%); £3,781,083.42 -> £3,395,761.07 (10.2%); £3,781,083.68 -> £3,395,761.27 (10.2%); £3,781,083.86 -> £3,395,761.47 (10.2%); £3,781,084.06 -> £3,395,761.66 (10.2%); £3,781,084.26 -> £3,395,761.86 (10.2%); £3,781,084.46 -> £3,395,762.06 (10.2%); £3,781,084.72 -> £3,395,762.26 (10.2%); £3,781,084.98 -> £3,395,762.46 (10.2%); £3,781,085.25 -> £3,395,762.66 (10.2%); £3,781,085.51 -> £3,395,762.85 (10.2%); £3,781,085.77 -> £3,395,763.05 (10.2%); £3,781,086.03 -> £3,395,763.08 (10.2%); £3,781,086.29 -> £3,395,763.11 (10.2%); £3,781,086.54 -> £3,395,763.13 (10.2%); £3,781,086.76 -> £3,395,763.15 (10.2%); £3,781,086.97 -> £3,395,763.17 (10.2%); £3,781,087.13 -> £3,395,763.19 (10.2%); £3,781,087.28 -> £3,395,763.21 (10.2%); £3,781,087.44 -> £3,395,763.23 (10.2%); £3,781,087.60 -> £3,395,763.25 (10.2%); £3,781,087.75 -> £3,395,763.26 (10.2%); £3,781,087.91 -> £3,395,763.28 (10.2%); £3,781,088.07 -> £3,395,763.29 (10.2%); £3,781,088.23 -> £3,395,763.31 (10.2%); £3,781,088.38 -> £3,395,763.33 (10.2%); £3,781,088.54 -> £3,395,763.34 (10.2%); £3,781,088.70 -> £3,395,763.36 (10.2%); £3,781,088.85 -> £3,395,763.51 (10.2%); £3,781,089.01 -> £3,395,763.66 (10.2%); £3,781,089.19 -> £3,395,763.81 (10.2%); £3,781,089.38 -> £3,395,763.97 (10.2%); £3,781,089.58 -> £3,395,764.12 (10.2%); £3,781,089.81 -> £3,395,764.28 (10.2%); £3,781,090.05 -> £3,395,764.43 (10.2%); £3,781,090.31 -> £3,395,764.59 (10.2%); £3,781,090.56 -> £3,395,764.61 (10.2%); £3,781,090.83 -> £3,395,764.64 (10.2%); £3,781,091.08 -> £3,395,764.66 (10.2%); £3,781,091.35 -> £3,395,764.68 (10.2%); £3,781,091.61 -> £3,395,764.71 (10.2%); £3,781,091.87 -> £3,395,764.73 (10.2%); £3,781,092.14 -> £3,395,764.76 (10.2%); £3,781,092.40 -> £3,395,764.78 (10.2%); £3,781,092.66 -> £3,395,764.80 (10.2%); £3,781,092.92 -> £3,395,764.83 (10.2%); £3,781,093.19 -> £3,395,764.85 (10.2%); £3,781,093.45 -> £3,395,764.88 (10.2%); £3,781,093.71 -> £3,395,764.90 (10.2%); £3,781,093.90 -> £3,395,765.07 (10.2%); £3,781,094.16 -> £3,395,765.23 (10.2%); £3,781,094.37 -> £3,395,765.40 (10.2%); £3,781,094.57 -> £3,395,765.56 (10.2%); £3,781,094.83 -> £3,395,765.73 (10.2%); £3,781,095.09 -> £3,395,765.89 (10.2%); £3,781,095.29 -> £3,395,766.05 (10.2%); £3,781,095.55 -> £3,395,766.21 (10.2%); £3,781,095.81 -> £3,395,766.37 (10.2%); £3,781,096.07 -> £3,395,766.53 (10.2%); £3,781,096.34 -> £3,395,766.69 (10.2%); £3,781,096.61 -> £3,395,766.72 (10.2%); £3,781,096.87 -> £3,395,766.74 (10.2%); £3,781,097.12 -> £3,395,766.77 (10.2%); £3,781,097.34 -> £3,395,766.79 (10.2%); £3,781,097.54 -> £3,395,766.81 (10.2%); £3,781,097.70 -> £3,395,766.83 (10.2%); £3,781,097.86 -> £3,395,766.84 (10.2%); £3,781,098.01 -> £3,395,766.86 (10.2%); £3,781,098.16 -> £3,395,766.88 (10.2%); £3,781,098.32 -> £3,395,766.90 (10.2%); £3,781,098.48 -> £3,395,766.91 (10.2%); £3,781,098.63 -> £3,395,766.93 (10.2%); £3,781,098.78 -> £3,395,766.94 (10.2%); £3,781,098.94 -> £3,395,766.96 (10.2%); £3,781,099.10 -> £3,395,766.98 (10.2%); £3,781,099.25 -> £3,395,767.00 (10.2%); £3,781,099.41 -> £3,395,767.13 (10.2%); £3,781,099.56 -> £3,395,767.26 (10.2%); £3,781,099.73 -> £3,395,767.40 (10.2%); £3,781,099.92 -> £3,395,767.53 (10.2%); £3,781,100.12 -> £3,395,767.67 (10.2%); £3,781,100.35 -> £3,395,767.80 (10.2%); £3,781,100.59 -> £3,395,767.94 (10.2%); £3,781,100.85 -> £3,395,768.07 (10.2%); £3,781,101.11 -> £3,395,768.09 (10.2%); £3,781,101.37 -> £3,395,768.11 (10.2%); £3,781,101.63 -> £3,395,768.14 (10.2%); £3,781,101.88 -> £3,395,768.16 (10.2%); £3,781,102.14 -> £3,395,768.19 (10.2%); £3,781,102.39 -> £3,395,768.21 (10.2%); £3,781,102.65 -> £3,395,768.23 (10.2%); £3,781,102.91 -> £3,395,768.26 (10.2%); £3,781,103.17 -> £3,395,768.28 (10.2%); £3,781,103.42 -> £3,395,768.30 (10.2%); £3,781,103.68 -> £3,395,768.33 (10.2%); £3,781,103.92 -> £3,395,768.35 (10.2%); £3,781,104.18 -> £3,395,768.38 (10.2%); £3,781,104.44 -> £3,395,768.52 (10.2%); £3,781,104.69 -> £3,395,768.67 (10.2%); £3,781,104.95 -> £3,395,768.81 (10.2%); £3,781,105.14 -> £3,395,768.96 (10.2%); £3,781,105.34 -> £3,395,769.10 (10.2%); £3,781,105.60 -> £3,395,769.25 (10.2%); £3,781,105.79 -> £3,395,769.39 (10.2%); £3,781,106.05 -> £3,395,769.52 (10.2%); £3,781,106.30 -> £3,395,769.66 (10.2%); £3,781,106.56 -> £3,395,769.80 (10.2%); £3,781,106.82 -> £3,395,769.94 (10.2%); £3,781,107.09 -> £3,395,769.96 (10.2%); £3,781,107.35 -> £3,395,769.99 (10.2%); £3,781,107.58 -> £3,395,770.02 (10.2%); £3,781,107.81 -> £3,395,770.04 (10.2%); £3,781,108.01 -> £3,395,770.06 (10.2%); £3,781,108.17 -> £3,395,770.08 (10.2%); £3,781,108.32 -> £3,395,770.09 (10.2%); £3,781,108.48 -> £3,395,770.11 (10.2%); £3,781,108.63 -> £3,395,770.13 (10.2%); £3,781,108.79 -> £3,395,770.14 (10.2%); £3,781,108.95 -> £3,395,770.16 (10.2%); £3,781,109.11 -> £3,395,770.18 (10.2%); £3,781,109.26 -> £3,395,770.19 (10.2%); £3,781,109.42 -> £3,395,770.21 (10.2%); £3,781,109.57 -> £3,395,770.23 (10.2%); £3,781,109.72 -> £3,395,770.25 (10.2%); £3,781,109.88 -> £3,395,770.43 (10.2%); £3,781,110.03 -> £3,395,770.62 (10.2%); £3,781,110.21 -> £3,395,770.81 (10.2%); £3,781,110.39 -> £3,395,771.01 (10.2%); £3,781,110.59 -> £3,395,771.21 (10.2%); £3,781,110.81 -> £3,395,771.40 (10.2%); £3,781,111.05 -> £3,395,771.60 (10.2%); £3,781,111.30 -> £3,395,771.79 (10.2%); £3,781,111.56 -> £3,395,771.82 (10.2%); £3,781,111.83 -> £3,395,771.84 (10.2%); £3,781,112.09 -> £3,395,771.86 (10.2%); £3,781,112.35 -> £3,395,771.89 (10.2%); £3,781,112.62 -> £3,395,771.91 (10.2%); £3,781,112.88 -> £3,395,771.93 (10.2%); £3,781,113.14 -> £3,395,771.96 (10.2%); £3,781,113.39 -> £3,395,771.98 (10.2%); £3,781,113.66 -> £3,395,772.00 (10.2%); £3,781,113.92 -> £3,395,772.03 (10.2%); £3,781,114.19 -> £3,395,772.05 (10.2%); £3,781,114.45 -> £3,395,772.08 (10.2%); £3,781,114.70 -> £3,395,772.10 (10.2%); £3,781,114.95 -> £3,395,772.30 (10.2%); £3,781,115.22 -> £3,395,772.50 (10.2%); £3,781,115.48 -> £3,395,772.70 (10.2%); £3,781,115.75 -> £3,395,772.90 (10.2%); £3,781,116.01 -> £3,395,773.09 (10.2%); £3,781,116.28 -> £3,395,773.29 (10.2%); £3,781,116.54 -> £3,395,773.50 (10.2%); £3,781,116.80 -> £3,395,773.69 (10.2%); £3,781,117.07 -> £3,395,773.89 (10.2%); £3,781,117.33 -> £3,395,774.09 (10.2%); £3,781,117.59 -> £3,395,774.29 (10.2%); £3,781,117.86 -> £3,395,774.31 (10.2%); £3,781,118.12 -> £3,395,774.34 (10.2%); £3,781,118.36 -> £3,395,774.36 (10.2%); £3,781,118.58 -> £3,395,774.39 (10.2%); £3,781,118.78 -> £3,395,774.41 (10.2%); £3,781,118.91 -> £3,395,774.43 (10.2%); £3,781,119.05 -> £3,395,774.45 (10.2%); £3,781,119.18 -> £3,395,774.46 (10.2%); £3,781,119.32 -> £3,395,774.48 (10.2%); £3,781,119.45 -> £3,395,774.50 (10.2%); £3,781,119.59 -> £3,395,774.51 (10.2%); £3,781,119.73 -> £3,395,774.53 (10.2%); £3,781,119.86 -> £3,395,774.55 (10.2%); £3,781,120.00 -> £3,395,774.56 (10.2%); £3,781,120.14 -> £3,395,774.58 (10.2%); £3,781,120.27 -> £3,395,774.60 (10.2%); £3,781,120.41 -> £3,395,774.79 (10.2%); £3,781,120.55 -> £3,395,774.99 (10.2%); £3,781,120.70 -> £3,395,775.19 (10.2%); £3,781,120.87 -> £3,395,775.40 (10.2%); £3,781,121.05 -> £3,395,775.60 (10.2%); £3,781,121.25 -> £3,395,775.80 (10.2%); £3,781,121.46 -> £3,395,776.00 (10.2%); £3,781,121.68 -> £3,395,776.20 (10.2%); £3,781,121.91 -> £3,395,776.22 (10.2%); £3,781,122.13 -> £3,395,776.25 (10.2%); £3,781,122.36 -> £3,395,776.27 (10.2%); £3,781,122.58 -> £3,395,776.30 (10.2%); £3,781,122.81 -> £3,395,776.33 (10.2%); £3,781,123.03 -> £3,395,776.35 (10.2%); £3,781,123.26 -> £3,395,776.38 (10.2%); £3,781,123.49 -> £3,395,776.41 (10.2%); £3,781,123.73 -> £3,395,776.43 (10.2%); £3,781,123.95 -> £3,395,776.46 (10.2%); £3,781,124.18 -> £3,395,776.48 (10.2%); £3,781,124.41 -> £3,395,776.51 (10.2%); £3,781,124.63 -> £3,395,776.54 (10.2%); £3,781,124.86 -> £3,395,776.74 (10.2%); £3,781,125.08 -> £3,395,776.95 (10.2%); £3,781,125.31 -> £3,395,777.15 (10.2%); £3,781,125.53 -> £3,395,777.36 (10.2%); £3,781,125.76 -> £3,395,777.56 (10.2%); £3,781,125.98 -> £3,395,777.77 (10.2%); £3,781,126.21 -> £3,395,777.98 (10.2%); £3,781,126.44 -> £3,395,778.19 (10.2%); £3,781,126.67 -> £3,395,778.39 (10.2%); £3,781,126.90 -> £3,395,778.60 (10.2%); £3,781,127.13 -> £3,395,778.80 (10.2%); £3,781,127.35 -> £3,395,778.83 (10.2%); £3,781,127.57 -> £3,395,778.86 (10.2%); £3,781,127.79 -> £3,395,778.88 (10.2%); £3,781,127.98 -> £3,395,778.91 (10.2%); £3,781,128.16 -> £3,395,778.93 (10.2%); £3,781,128.29 -> £3,395,778.95 (10.2%); £3,781,128.42 -> £3,395,778.97 (10.2%); £3,781,128.56 -> £3,395,778.99 (10.2%); £3,781,128.69 -> £3,395,779.00 (10.2%); £3,781,128.82 -> £3,395,779.02 (10.2%); £3,781,128.96 -> £3,395,779.04 (10.2%); £3,781,129.09 -> £3,395,779.05 (10.2%); £3,781,129.23 -> £3,395,779.07 (10.2%); £3,781,129.37 -> £3,395,779.09 (10.2%); £3,781,129.51 -> £3,395,779.10 (10.2%); £3,781,129.64 -> £3,395,779.12 (10.2%); £3,781,129.78 -> £3,395,779.30 (10.2%); £3,781,129.91 -> £3,395,779.49 (10.2%); £3,781,130.07 -> £3,395,779.67 (10.2%); £3,781,130.23 -> £3,395,779.87 (10.2%); £3,781,130.41 -> £3,395,780.06 (10.2%); £3,781,130.61 -> £3,395,780.26 (10.2%); £3,781,130.82 -> £3,395,780.46 (10.2%); £3,781,131.04 -> £3,395,780.66 (10.2%); £3,781,131.27 -> £3,395,780.69 (10.2%); £3,781,131.50 -> £3,395,780.72 (10.2%); £3,781,131.73 -> £3,395,780.75 (10.2%); £3,781,131.94 -> £3,395,780.78 (10.2%); £3,781,132.16 -> £3,395,780.82 (10.2%); £3,781,132.39 -> £3,395,780.85 (10.2%); £3,781,132.61 -> £3,395,780.88 (10.2%); £3,781,132.85 -> £3,395,780.91 (10.2%); £3,781,133.07 -> £3,395,780.94 (10.2%); £3,781,133.30 -> £3,395,780.97 (10.2%); £3,781,133.52 -> £3,395,780.99 (10.2%); £3,781,133.75 -> £3,395,781.02 (10.2%); £3,781,133.98 -> £3,395,781.05 (10.2%); £3,781,134.22 -> £3,395,781.25 (10.2%); £3,781,134.44 -> £3,395,781.45 (10.2%); £3,781,134.67 -> £3,395,781.65 (10.2%); £3,781,134.90 -> £3,395,781.85 (10.2%); £3,781,135.12 -> £3,395,782.05 (10.2%); £3,781,135.34 -> £3,395,782.25 (10.2%); £3,781,135.56 -> £3,395,782.46 (10.2%); £3,781,135.78 -> £3,395,782.66 (10.2%); £3,781,136.01 -> £3,395,782.86 (10.2%); £3,781,136.24 -> £3,395,783.05 (10.2%); £3,781,136.48 -> £3,395,783.25 (10.2%); £3,781,136.70 -> £3,395,783.28 (10.2%); £3,781,136.93 -> £3,395,783.31 (10.2%); £3,781,137.14 -> £3,395,783.33 (10.2%); £3,781,137.33 -> £3,395,783.35 (10.2%); £3,781,137.51 -> £3,395,783.37 (10.2%); £3,781,137.66 -> £3,395,783.39 (10.2%); £3,781,137.81 -> £3,395,783.41 (10.2%); £3,781,137.97 -> £3,395,783.43 (10.2%); £3,781,138.12 -> £3,395,783.45 (10.2%); £3,781,138.28 -> £3,395,783.46 (10.2%); £3,781,138.44 -> £3,395,783.48 (10.2%); £3,781,138.59 -> £3,395,783.50 (10.2%); £3,781,138.74 -> £3,395,783.51 (10.2%); £3,781,138.90 -> £3,395,783.53 (10.2%); £3,781,139.05 -> £3,395,783.54 (10.2%); £3,781,139.21 -> £3,395,783.56 (10.2%); £3,781,139.36 -> £3,395,783.73 (10.2%); £3,781,139.52 -> £3,395,783.90 (10.2%); £3,781,139.68 -> £3,395,784.07 (10.2%); £3,781,139.87 -> £3,395,784.25 (10.2%); £3,781,140.08 -> £3,395,784.43 (10.2%); £3,781,140.31 -> £3,395,784.61 (10.2%); £3,781,140.55 -> £3,395,784.78 (10.2%); £3,781,140.81 -> £3,395,784.96 (10.2%); £3,781,141.07 -> £3,395,784.99 (10.2%); £3,781,141.33 -> £3,395,785.01 (10.2%); £3,781,141.59 -> £3,395,785.04 (10.2%); £3,781,141.85 -> £3,395,785.06 (10.2%); £3,781,142.11 -> £3,395,785.08 (10.2%); £3,781,142.37 -> £3,395,785.11 (10.2%); £3,781,142.63 -> £3,395,785.13 (10.2%); £3,781,142.89 -> £3,395,785.16 (10.2%); £3,781,143.15 -> £3,395,785.18 (10.2%); £3,781,143.41 -> £3,395,785.20 (10.2%); £3,781,143.66 -> £3,395,785.23 (10.2%); £3,781,143.92 -> £3,395,785.25 (10.2%); £3,781,144.18 -> £3,395,785.28 (10.2%); £3,781,144.43 -> £3,395,785.46 (10.2%); £3,781,144.69 -> £3,395,785.64 (10.2%); £3,781,144.93 -> £3,395,785.83 (10.2%); £3,781,145.19 -> £3,395,786.01 (10.2%); £3,781,145.45 -> £3,395,786.19 (10.2%); £3,781,145.70 -> £3,395,786.37 (10.2%); £3,781,145.96 -> £3,395,786.56 (10.2%); £3,781,146.22 -> £3,395,786.74 (10.2%); £3,781,146.48 -> £3,395,786.93 (10.2%); £3,781,146.73 -> £3,395,787.11 (10.2%); £3,781,146.99 -> £3,395,787.28 (10.2%); £3,781,147.25 -> £3,395,787.31 (10.2%); £3,781,147.51 -> £3,395,787.34 (10.2%); £3,781,147.75 -> £3,395,787.37 (10.2%); £3,781,147.97 -> £3,395,787.39 (10.2%); £3,781,148.17 -> £3,395,787.41 (10.2%); £3,781,148.32 -> £3,395,787.43 (10.2%); £3,781,148.47 -> £3,395,787.44 (10.2%); £3,781,148.63 -> £3,395,787.46 (10.2%); £3,781,148.79 -> £3,395,787.48 (10.2%); £3,781,148.94 -> £3,395,787.49 (10.2%); £3,781,149.09 -> £3,395,787.51 (10.2%); £3,781,149.24 -> £3,395,787.53 (10.2%); £3,781,149.39 -> £3,395,787.54 (10.2%); £3,781,149.54 -> £3,395,787.56 (10.2%); £3,781,149.69 -> £3,395,787.58 (10.2%); £3,781,149.84 -> £3,395,787.59 (10.2%); £3,781,150.00 -> £3,395,787.74 (10.2%); £3,781,150.15 -> £3,395,787.88 (10.2%); £3,781,150.33 -> £3,395,788.03 (10.2%); £3,781,150.51 -> £3,395,788.18 (10.2%); £3,781,150.72 -> £3,395,788.33 (10.2%); £3,781,150.94 -> £3,395,788.47 (10.2%); £3,781,151.18 -> £3,395,788.62 (10.2%); £3,781,151.44 -> £3,395,788.77 (10.2%); £3,781,151.69 -> £3,395,788.79 (10.2%); £3,781,151.95 -> £3,395,788.81 (10.2%); £3,781,152.21 -> £3,395,788.84 (10.2%); £3,781,152.46 -> £3,395,788.86 (10.2%); £3,781,152.71 -> £3,395,788.89 (10.2%); £3,781,152.97 -> £3,395,788.91 (10.2%); £3,781,153.23 -> £3,395,788.94 (10.2%); £3,781,153.48 -> £3,395,788.96 (10.2%); £3,781,153.73 -> £3,395,788.98 (10.2%); £3,781,154.00 -> £3,395,789.01 (10.2%); £3,781,154.25 -> £3,395,789.03 (10.2%); £3,781,154.52 -> £3,395,789.05 (10.2%); £3,781,154.77 -> £3,395,789.08 (10.2%); £3,781,155.03 -> £3,395,789.24 (10.2%); £3,781,155.29 -> £3,395,789.40 (10.2%); £3,781,155.54 -> £3,395,789.55 (10.2%); £3,781,155.80 -> £3,395,789.71 (10.2%); £3,781,156.06 -> £3,395,789.87 (10.2%); £3,781,156.31 -> £3,395,790.02 (10.2%); £3,781,156.57 -> £3,395,790.18 (10.2%); £3,781,156.83 -> £3,395,790.33 (10.2%); £3,781,157.09 -> £3,395,790.48 (10.2%); £3,781,157.34 -> £3,395,790.64 (10.2%); £3,781,157.60 -> £3,395,790.79 (10.2%); £3,781,157.85 -> £3,395,790.82 (10.2%); £3,781,158.12 -> £3,395,790.85 (10.2%); £3,781,158.35 -> £3,395,790.87 (10.2%); £3,781,158.57 -> £3,395,790.89 (10.2%); £3,781,158.76 -> £3,395,790.91 (10.2%); £3,781,158.91 -> £3,395,790.93 (10.2%); £3,781,159.06 -> £3,395,790.95 (10.2%); £3,781,159.22 -> £3,395,790.97 (10.2%); £3,781,159.36 -> £3,395,790.98 (10.2%); £3,781,159.51 -> £3,395,791.00 (10.2%); £3,781,159.67 -> £3,395,791.02 (10.2%); £3,781,159.82 -> £3,395,791.03 (10.2%); £3,781,159.97 -> £3,395,791.05 (10.2%); £3,781,160.12 -> £3,395,791.06 (10.2%); £3,781,160.28 -> £3,395,791.08 (10.2%); £3,781,160.43 -> £3,395,791.10 (10.2%); £3,781,160.58 -> £3,395,791.26 (10.2%); £3,781,160.73 -> £3,395,791.43 (10.2%); £3,781,160.91 -> £3,395,791.60 (10.2%); £3,781,161.10 -> £3,395,791.77 (10.2%); £3,781,161.30 -> £3,395,791.95 (10.2%); £3,781,161.52 -> £3,395,792.12 (10.2%); £3,781,161.76 -> £3,395,792.29 (10.2%); £3,781,162.01 -> £3,395,792.47 (10.2%); £3,781,162.26 -> £3,395,792.49 (10.2%); £3,781,162.51 -> £3,395,792.52 (10.2%); £3,781,162.77 -> £3,395,792.54 (10.2%); £3,781,163.03 -> £3,395,792.57 (10.2%); £3,781,163.29 -> £3,395,792.59 (10.2%); £3,781,163.55 -> £3,395,792.61 (10.2%); £3,781,163.81 -> £3,395,792.64 (10.2%); £3,781,164.07 -> £3,395,792.66 (10.2%); £3,781,164.33 -> £3,395,792.68 (10.2%); £3,781,164.58 -> £3,395,792.71 (10.2%); £3,781,164.84 -> £3,395,792.73 (10.2%); £3,781,165.09 -> £3,395,792.76 (10.2%); £3,781,165.35 -> £3,395,792.79 (10.2%); £3,781,165.60 -> £3,395,792.97 (10.2%); £3,781,165.87 -> £3,395,793.15 (10.2%); £3,781,166.13 -> £3,395,793.33 (10.2%); £3,781,166.39 -> £3,395,793.51 (10.2%); £3,781,166.64 -> £3,395,793.68 (10.2%); £3,781,166.90 -> £3,395,793.86 (10.2%); £3,781,167.15 -> £3,395,794.04 (10.2%); £3,781,167.40 -> £3,395,794.22 (10.2%); £3,781,167.66 -> £3,395,794.40 (10.2%); £3,781,167.92 -> £3,395,794.58 (10.2%); £3,781,168.17 -> £3,395,794.76 (10.2%); £3,781,168.42 -> £3,395,794.79 (10.2%); £3,781,168.68 -> £3,395,794.82 (10.2%); £3,781,168.92 -> £3,395,794.84 (10.2%); £3,781,169.13 -> £3,395,794.86 (10.2%); £3,781,169.33 -> £3,395,794.88 (10.2%); £3,781,169.49 -> £3,395,794.90 (10.2%); £3,781,169.64 -> £3,395,794.92 (10.2%); £3,781,169.79 -> £3,395,794.94 (10.2%); £3,781,169.94 -> £3,395,794.96 (10.2%); £3,781,170.09 -> £3,395,794.97 (10.2%); £3,781,170.24 -> £3,395,794.99 (10.2%); £3,781,170.40 -> £3,395,795.00 (10.2%); £3,781,170.55 -> £3,395,795.02 (10.2%); £3,781,170.70 -> £3,395,795.04 (10.2%); £3,781,170.86 -> £3,395,795.05 (10.2%); £3,781,171.01 -> £3,395,795.07 (10.2%); £3,781,171.16 -> £3,395,795.22 (10.2%); £3,781,171.31 -> £3,395,795.37 (10.2%); £3,781,171.48 -> £3,395,795.53 (10.2%); £3,781,171.67 -> £3,395,795.68 (10.2%); £3,781,171.87 -> £3,395,795.85 (10.2%); £3,781,172.08 -> £3,395,796.00 (10.2%); £3,781,172.32 -> £3,395,796.15 (10.2%); £3,781,172.59 -> £3,395,796.31 (10.2%); £3,781,172.84 -> £3,395,796.33 (10.2%); £3,781,173.11 -> £3,395,796.35 (10.2%); £3,781,173.36 -> £3,395,796.38 (10.2%); £3,781,173.61 -> £3,395,796.40 (10.2%); £3,781,173.86 -> £3,395,796.43 (10.2%); £3,781,174.11 -> £3,395,796.45 (10.2%); £3,781,174.37 -> £3,395,796.47 (10.2%); £3,781,174.62 -> £3,395,796.50 (10.2%); £3,781,174.88 -> £3,395,796.52 (10.2%); £3,781,175.13 -> £3,395,796.54 (10.2%); £3,781,175.39 -> £3,395,796.57 (10.2%); £3,781,175.65 -> £3,395,796.59 (10.2%); £3,781,175.90 -> £3,395,796.62 (10.2%); £3,781,176.15 -> £3,395,796.78 (10.2%); £3,781,176.41 -> £3,395,796.95 (10.2%); £3,781,176.67 -> £3,395,797.12 (10.2%); £3,781,176.93 -> £3,395,797.29 (10.2%); £3,781,177.18 -> £3,395,797.45 (10.2%); £3,781,177.44 -> £3,395,797.62 (10.2%); £3,781,177.69 -> £3,395,797.79 (10.2%); £3,781,177.94 -> £3,395,797.96 (10.2%); £3,781,178.20 -> £3,395,798.12 (10.2%); £3,781,178.46 -> £3,395,798.29 (10.2%); £3,781,178.72 -> £3,395,798.45 (10.2%); £3,781,178.97 -> £3,395,798.48 (10.2%); £3,781,179.22 -> £3,395,798.50 (10.2%); £3,781,179.46 -> £3,395,798.53 (10.2%); £3,781,179.67 -> £3,395,798.55 (10.2%); £3,781,179.87 -> £3,395,798.57 (10.2%); £3,781,180.02 -> £3,395,798.59 (10.2%); £3,781,180.18 -> £3,395,798.61 (10.2%); £3,781,180.33 -> £3,395,798.62 (10.2%); £3,781,180.48 -> £3,395,798.64 (10.2%); £3,781,180.63 -> £3,395,798.66 (10.2%); £3,781,180.79 -> £3,395,798.67 (10.2%); £3,781,180.94 -> £3,395,798.69 (10.2%); £3,781,181.09 -> £3,395,798.71 (10.2%); £3,781,181.24 -> £3,395,798.72 (10.2%); £3,781,181.40 -> £3,395,798.74 (10.2%); £3,781,181.55 -> £3,395,798.76 (10.2%); £3,781,181.70 -> £3,395,798.91 (10.2%); £3,781,181.86 -> £3,395,799.07 (10.2%); £3,781,182.03 -> £3,395,799.23 (10.2%); £3,781,182.22 -> £3,395,799.39 (10.2%); £3,781,182.42 -> £3,395,799.55 (10.2%); £3,781,182.63 -> £3,395,799.71 (10.2%); £3,781,182.87 -> £3,395,799.87 (10.2%); £3,781,183.14 -> £3,395,800.03 (10.2%); £3,781,183.40 -> £3,395,800.05 (10.2%); £3,781,183.65 -> £3,395,800.07 (10.2%); £3,781,183.91 -> £3,395,800.10 (10.2%); £3,781,184.17 -> £3,395,800.12 (10.2%); £3,781,184.42 -> £3,395,800.14 (10.2%); £3,781,184.68 -> £3,395,800.17 (10.2%); £3,781,184.94 -> £3,395,800.19 (10.2%); £3,781,185.19 -> £3,395,800.22 (10.2%); £3,781,185.44 -> £3,395,800.24 (10.2%); £3,781,185.70 -> £3,395,800.26 (10.2%); £3,781,185.96 -> £3,395,800.29 (10.2%); £3,781,186.21 -> £3,395,800.31 (10.2%); £3,781,186.46 -> £3,395,800.34 (10.2%); £3,781,186.72 -> £3,395,800.50 (10.2%); £3,781,186.97 -> £3,395,800.67 (10.2%); £3,781,187.22 -> £3,395,800.84 (10.2%); £3,781,187.48 -> £3,395,801.00 (10.2%); £3,781,187.74 -> £3,395,801.17 (10.2%); £3,781,187.99 -> £3,395,801.34 (10.2%); £3,781,188.23 -> £3,395,801.50 (10.2%); £3,781,188.50 -> £3,395,801.66 (10.2%); £3,781,188.75 -> £3,395,801.83 (10.2%); £3,781,189.01 -> £3,395,801.99 (10.2%); £3,781,189.25 -> £3,395,802.15 (10.2%); £3,781,189.51 -> £3,395,802.18 (10.2%); £3,781,189.77 -> £3,395,802.21 (10.2%); £3,781,190.01 -> £3,395,802.23 (10.2%); £3,781,190.22 -> £3,395,802.25 (10.2%); £3,781,190.42 -> £3,395,802.27 (10.2%); £3,781,190.55 -> £3,395,802.29 (10.2%); £3,781,190.68 -> £3,395,802.31 (10.2%); £3,781,190.81 -> £3,395,802.33 (10.2%); £3,781,190.95 -> £3,395,802.35 (10.2%); £3,781,191.08 -> £3,395,802.36 (10.2%); £3,781,191.21 -> £3,395,802.38 (10.2%); £3,781,191.35 -> £3,395,802.40 (10.2%); £3,781,191.48 -> £3,395,802.41 (10.2%); £3,781,191.62 -> £3,395,802.43 (10.2%); £3,781,191.75 -> £3,395,802.45 (10.2%); £3,781,191.88 -> £3,395,802.46 (10.2%); £3,781,192.02 -> £3,395,802.60 (10.2%); £3,781,192.16 -> £3,395,802.74 (10.2%); £3,781,192.31 -> £3,395,802.89 (10.2%); £3,781,192.47 -> £3,395,803.04 (10.2%); £3,781,192.65 -> £3,395,803.19 (10.2%); £3,781,192.85 -> £3,395,803.34 (10.2%); £3,781,193.06 -> £3,395,803.49 (10.2%); £3,781,193.28 -> £3,395,803.64 (10.2%); £3,781,193.51 -> £3,395,803.67 (10.2%); £3,781,193.73 -> £3,395,803.69 (10.2%); £3,781,193.95 -> £3,395,803.72 (10.2%); £3,781,194.17 -> £3,395,803.75 (10.2%); £3,781,194.40 -> £3,395,803.77 (10.2%); £3,781,194.63 -> £3,395,803.80 (10.2%); £3,781,194.85 -> £3,395,803.83 (10.2%); £3,781,195.07 -> £3,395,803.85 (10.2%); £3,781,195.30 -> £3,395,803.88 (10.2%); £3,781,195.52 -> £3,395,803.90 (10.2%); £3,781,195.75 -> £3,395,803.93 (10.2%); £3,781,195.98 -> £3,395,803.95 (10.2%); £3,781,196.21 -> £3,395,803.98 (10.2%); £3,781,196.43 -> £3,395,804.14 (10.2%); £3,781,196.66 -> £3,395,804.30 (10.2%); £3,781,196.88 -> £3,395,804.46 (10.2%); £3,781,197.11 -> £3,395,804.61 (10.2%); £3,781,197.33 -> £3,395,804.77 (10.2%); £3,781,197.56 -> £3,395,804.94 (10.2%); £3,781,197.78 -> £3,395,805.10 (10.2%); £3,781,198.00 -> £3,395,805.26 (10.2%); £3,781,198.22 -> £3,395,805.42 (10.2%); £3,781,198.44 -> £3,395,805.58 (10.2%); £3,781,198.67 -> £3,395,805.73 (10.2%); £3,781,198.89 -> £3,395,805.75 (10.2%); £3,781,199.11 -> £3,395,805.78 (10.2%); £3,781,199.32 -> £3,395,805.81 (10.2%); £3,781,199.51 -> £3,395,805.83 (10.2%); £3,781,199.68 -> £3,395,805.85 (10.2%); £3,781,199.82 -> £3,395,805.87 (10.2%); £3,781,199.95 -> £3,395,805.89 (10.2%); £3,781,200.09 -> £3,395,805.91 (10.2%); £3,781,200.22 -> £3,395,805.93 (10.2%); £3,781,200.36 -> £3,395,805.95 (10.2%); £3,781,200.49 -> £3,395,805.96 (10.2%); £3,781,200.63 -> £3,395,805.98 (10.2%); £3,781,200.77 -> £3,395,806.00 (10.2%); £3,781,200.90 -> £3,395,806.01 (10.2%); £3,781,201.04 -> £3,395,806.03 (10.2%); £3,781,201.17 -> £3,395,806.05 (10.2%); £3,781,201.31 -> £3,395,806.18 (10.2%); £3,781,201.44 -> £3,395,806.32 (10.2%); £3,781,201.59 -> £3,395,806.45 (10.2%); £3,781,201.76 -> £3,395,806.59 (10.2%); £3,781,201.94 -> £3,395,806.73 (10.2%); £3,781,202.13 -> £3,395,806.87 (10.2%); £3,781,202.34 -> £3,395,807.02 (10.2%); £3,781,202.56 -> £3,395,807.16 (10.2%); £3,781,202.80 -> £3,395,807.19 (10.2%); £3,781,203.02 -> £3,395,807.22 (10.2%); £3,781,203.24 -> £3,395,807.25 (10.2%); £3,781,203.46 -> £3,395,807.28 (10.2%); £3,781,203.69 -> £3,395,807.32 (10.2%); £3,781,203.92 -> £3,395,807.35 (10.2%); £3,781,204.14 -> £3,395,807.38 (10.2%); £3,781,204.36 -> £3,395,807.41 (10.2%); £3,781,204.58 -> £3,395,807.44 (10.2%); £3,781,204.81 -> £3,395,807.46 (10.2%); £3,781,205.03 -> £3,395,807.49 (10.2%); £3,781,205.26 -> £3,395,807.52 (10.2%); £3,781,205.48 -> £3,395,807.55 (10.2%); £3,781,205.70 -> £3,395,807.71 (10.2%); £3,781,205.93 -> £3,395,807.86 (10.2%); £3,781,206.16 -> £3,395,808.02 (10.2%); £3,781,206.39 -> £3,395,808.17 (10.2%); £3,781,206.60 -> £3,395,808.32 (10.2%); £3,781,206.81 -> £3,395,808.48 (10.2%); £3,781,207.04 -> £3,395,808.63 (10.2%); £3,781,207.25 -> £3,395,808.78 (10.2%); £3,781,207.48 -> £3,395,808.92 (10.2%); £3,781,207.71 -> £3,395,809.07 (10.2%); £3,781,207.93 -> £3,395,809.22 (10.2%); £3,781,208.15 -> £3,395,809.25 (10.2%); £3,781,208.37 -> £3,395,809.28 (10.2%); £3,781,208.59 -> £3,395,809.30 (10.2%); £3,781,208.78 -> £3,395,809.33 (10.2%); £3,781,208.95 -> £3,395,809.35 (10.2%); £3,781,209.11 -> £3,395,809.36 (10.2%); £3,781,209.26 -> £3,395,809.38 (10.2%); £3,781,209.41 -> £3,395,809.40 (10.2%); £3,781,209.56 -> £3,395,809.42 (10.2%); £3,781,209.72 -> £3,395,809.43 (10.2%); £3,781,209.87 -> £3,395,809.45 (10.2%); £3,781,210.02 -> £3,395,809.47 (10.2%); £3,781,210.17 -> £3,395,809.48 (10.2%); £3,781,210.33 -> £3,395,809.50 (10.2%); £3,781,210.48 -> £3,395,809.52 (10.2%); £3,781,210.62 -> £3,395,809.53 (10.2%); £3,781,210.77 -> £3,395,809.68 (10.2%); £3,781,210.92 -> £3,395,809.82 (10.2%); £3,781,211.09 -> £3,395,809.97 (10.2%); £3,781,211.28 -> £3,395,810.11 (10.2%); £3,781,211.49 -> £3,395,810.26 (10.2%); £3,781,211.71 -> £3,395,810.40 (10.2%); £3,781,211.95 -> £3,395,810.55 (10.2%); £3,781,212.19 -> £3,395,810.69 (10.2%); £3,781,212.45 -> £3,395,810.71 (10.2%); £3,781,212.70 -> £3,395,810.74 (10.2%); £3,781,212.96 -> £3,395,810.76 (10.2%); £3,781,213.21 -> £3,395,810.78 (10.2%); £3,781,213.46 -> £3,395,810.81 (10.2%); £3,781,213.72 -> £3,395,810.83 (10.2%); £3,781,213.97 -> £3,395,810.85 (10.2%); £3,781,214.21 -> £3,395,810.88 (10.2%); £3,781,214.46 -> £3,395,810.90 (10.2%); £3,781,214.73 -> £3,395,810.92 (10.2%); £3,781,214.98 -> £3,395,810.95 (10.2%); £3,781,215.23 -> £3,395,810.97 (10.2%); £3,781,215.49 -> £3,395,811.00 (10.2%); £3,781,215.74 -> £3,395,811.14 (10.2%); £3,781,215.99 -> £3,395,811.29 (10.2%); £3,781,216.25 -> £3,395,811.44 (10.2%); £3,781,216.51 -> £3,395,811.59 (10.2%); £3,781,216.76 -> £3,395,811.74 (10.2%); £3,781,217.01 -> £3,395,811.90 (10.2%); £3,781,217.26 -> £3,395,812.06 (10.2%); £3,781,217.51 -> £3,395,812.21 (10.2%); £3,781,217.76 -> £3,395,812.37 (10.2%); £3,781,218.01 -> £3,395,812.52 (10.2%); £3,781,218.28 -> £3,395,812.67 (10.2%); £3,781,218.53 -> £3,395,812.70 (10.2%); £3,781,218.78 -> £3,395,812.73 (10.2%); £3,781,219.01 -> £3,395,812.75 (10.2%); £3,781,219.23 -> £3,395,812.77 (10.2%); £3,781,219.42 -> £3,395,812.79 (10.2%); £3,781,219.57 -> £3,395,812.81 (10.2%); £3,781,219.72 -> £3,395,812.83 (10.2%); £3,781,219.87 -> £3,395,812.85 (10.2%); £3,781,220.01 -> £3,395,812.86 (10.2%); £3,781,220.17 -> £3,395,812.88 (10.2%); £3,781,220.32 -> £3,395,812.90 (10.2%); £3,781,220.47 -> £3,395,812.91 (10.2%); £3,781,220.62 -> £3,395,812.93 (10.2%); £3,781,220.77 -> £3,395,812.95 (10.2%); £3,781,220.92 -> £3,395,812.96 (10.2%); £3,781,221.06 -> £3,395,812.98 (10.2%); £3,781,221.21 -> £3,395,813.08 (10.2%); £3,781,221.37 -> £3,395,813.19 (10.2%); £3,781,221.54 -> £3,395,813.31 (10.2%); £3,781,221.72 -> £3,395,813.43 (10.2%); £3,781,221.93 -> £3,395,813.55 (10.2%); £3,781,222.14 -> £3,395,813.66 (10.2%); £3,781,222.37 -> £3,395,813.78 (10.2%); £3,781,222.63 -> £3,395,813.89 (10.2%); £3,781,222.88 -> £3,395,813.91 (10.2%); £3,781,223.13 -> £3,395,813.94 (10.2%); £3,781,223.38 -> £3,395,813.96 (10.2%); £3,781,223.64 -> £3,395,813.98 (10.2%); £3,781,223.89 -> £3,395,814.01 (10.2%); £3,781,224.14 -> £3,395,814.03 (10.2%); £3,781,224.39 -> £3,395,814.06 (10.2%); £3,781,224.64 -> £3,395,814.08 (10.2%); £3,781,224.89 -> £3,395,814.10 (10.2%); £3,781,225.14 -> £3,395,814.13 (10.2%); £3,781,225.39 -> £3,395,814.15 (10.2%); £3,781,225.65 -> £3,395,814.17 (10.2%); £3,781,225.91 -> £3,395,814.20 (10.2%); £3,781,226.16 -> £3,395,814.32 (10.2%); £3,781,226.42 -> £3,395,814.45 (10.2%); £3,781,226.67 -> £3,395,814.57 (10.2%); £3,781,226.93 -> £3,395,814.70 (10.2%); £3,781,227.19 -> £3,395,814.82 (10.2%); £3,781,227.44 -> £3,395,814.95 (10.2%); £3,781,227.70 -> £3,395,815.08 (10.2%); £3,781,227.95 -> £3,395,815.20 (10.2%); £3,781,228.19 -> £3,395,815.32 (10.2%); £3,781,228.43 -> £3,395,815.44 (10.2%); £3,781,228.68 -> £3,395,815.56 (10.2%); £3,781,228.93 -> £3,395,815.59 (10.2%); £3,781,229.18 -> £3,395,815.62 (10.2%); £3,781,229.42 -> £3,395,815.64 (10.2%); £3,781,229.63 -> £3,395,815.66 (10.2%); £3,781,229.82 -> £3,395,815.68 (10.2%); £3,781,229.98 -> £3,395,815.70 (10.2%); £3,781,230.13 -> £3,395,815.72 (10.2%); £3,781,230.28 -> £3,395,815.74 (10.2%); £3,781,230.43 -> £3,395,815.75 (10.2%); £3,781,230.58 -> £3,395,815.77 (10.2%); £3,781,230.74 -> £3,395,815.79 (10.2%); £3,781,230.89 -> £3,395,815.80 (10.2%); £3,781,231.04 -> £3,395,815.82 (10.2%); £3,781,231.19 -> £3,395,815.84 (10.2%); £3,781,231.34 -> £3,395,815.85 (10.2%); £3,781,231.49 -> £3,395,815.87 (10.2%); £3,781,231.65 -> £3,395,815.95 (10.2%); £3,781,231.79 -> £3,395,816.02 (10.2%); £3,781,231.96 -> £3,395,816.11 (10.2%); £3,781,232.14 -> £3,395,816.19 (10.2%); £3,781,232.34 -> £3,395,816.28 (10.2%); £3,781,232.56 -> £3,395,816.37 (10.2%); £3,781,232.80 -> £3,395,816.45 (10.2%); £3,781,233.05 -> £3,395,816.53 (10.2%); £3,781,233.30 -> £3,395,816.56 (10.2%); £3,781,233.55 -> £3,395,816.58 (10.2%); £3,781,233.80 -> £3,395,816.61 (10.2%); £3,781,234.06 -> £3,395,816.63 (10.2%); £3,781,234.31 -> £3,395,816.66 (10.2%); £3,781,234.55 -> £3,395,816.68 (10.2%); £3,781,234.81 -> £3,395,816.70 (10.2%); £3,781,235.07 -> £3,395,816.73 (10.2%); £3,781,235.32 -> £3,395,816.75 (10.2%); £3,781,235.56 -> £3,395,816.77 (10.2%); £3,781,235.81 -> £3,395,816.80 (10.2%); £3,781,236.05 -> £3,395,816.82 (10.2%); £3,781,236.30 -> £3,395,816.85 (10.2%); £3,781,236.55 -> £3,395,816.94 (10.2%); £3,781,236.80 -> £3,395,817.04 (10.2%); £3,781,237.05 -> £3,395,817.14 (10.2%); £3,781,237.30 -> £3,395,817.24 (10.2%); £3,781,237.54 -> £3,395,817.34 (10.2%); £3,781,237.79 -> £3,395,817.44 (10.2%); £3,781,238.04 -> £3,395,817.54 (10.2%); £3,781,238.30 -> £3,395,817.63 (10.2%); £3,781,238.54 -> £3,395,817.73 (10.2%); £3,781,238.78 -> £3,395,817.82 (10.2%); £3,781,239.03 -> £3,395,817.91 (10.2%); £3,781,239.28 -> £3,395,817.94 (10.2%); £3,781,239.54 -> £3,395,817.97 (10.2%); £3,781,239.78 -> £3,395,817.99 (10.2%); £3,781,239.98 -> £3,395,818.02 (10.2%); £3,781,240.18 -> £3,395,818.04 (10.2%); £3,781,240.33 -> £3,395,818.06 (10.2%); £3,781,240.48 -> £3,395,818.07 (10.2%); £3,781,240.63 -> £3,395,818.09 (10.2%); £3,781,240.79 -> £3,395,818.11 (10.2%); £3,781,240.94 -> £3,395,818.12 (10.2%); £3,781,241.09 -> £3,395,818.14 (10.2%); £3,781,241.24 -> £3,395,818.16 (10.2%); £3,781,241.39 -> £3,395,818.17 (10.2%); £3,781,241.54 -> £3,395,818.19 (10.2%); £3,781,241.69 -> £3,395,818.21 (10.2%); £3,781,241.85 -> £3,395,818.22 (10.2%); £3,781,241.99 -> £3,395,818.30 (10.2%); £3,781,242.14 -> £3,395,818.37 (10.2%); £3,781,242.31 -> £3,395,818.46 (10.2%); £3,781,242.49 -> £3,395,818.54 (10.2%); £3,781,242.69 -> £3,395,818.62 (10.2%); £3,781,242.91 -> £3,395,818.71 (10.2%); £3,781,243.14 -> £3,395,818.79 (10.2%); £3,781,243.39 -> £3,395,818.87 (10.2%); £3,781,243.64 -> £3,395,818.89 (10.2%); £3,781,243.89 -> £3,395,818.92 (10.2%); £3,781,244.15 -> £3,395,818.94 (10.2%); £3,781,244.40 -> £3,395,818.96 (10.2%); £3,781,244.65 -> £3,395,818.99 (10.2%); £3,781,244.91 -> £3,395,819.01 (10.2%); £3,781,245.16 -> £3,395,819.04 (10.2%); £3,781,245.41 -> £3,395,819.06 (10.2%); £3,781,245.66 -> £3,395,819.08 (10.2%); £3,781,245.91 -> £3,395,819.10 (10.2%); £3,781,246.16 -> £3,395,819.13 (10.2%); £3,781,246.42 -> £3,395,819.15 (10.2%); £3,781,246.67 -> £3,395,819.18 (10.2%); £3,781,246.93 -> £3,395,819.27 (10.2%); £3,781,247.19 -> £3,395,819.36 (10.2%); £3,781,247.44 -> £3,395,819.46 (10.2%); £3,781,247.70 -> £3,395,819.56 (10.2%); £3,781,247.96 -> £3,395,819.66 (10.2%); £3,781,248.20 -> £3,395,819.75 (10.2%); £3,781,248.45 -> £3,395,819.85 (10.2%); £3,781,248.71 -> £3,395,819.94 (10.2%); £3,781,248.96 -> £3,395,820.03 (10.2%); £3,781,249.21 -> £3,395,820.13 (10.2%); £3,781,249.45 -> £3,395,820.22 (10.2%); £3,781,249.71 -> £3,395,820.25 (10.2%); £3,781,249.97 -> £3,395,820.27 (10.2%); £3,781,250.19 -> £3,395,820.30 (10.2%); £3,781,250.41 -> £3,395,820.32 (10.2%); £3,781,250.61 -> £3,395,820.34 (10.2%); £3,781,250.75 -> £3,395,820.36 (10.2%); £3,781,250.91 -> £3,395,820.38 (10.2%); £3,781,251.06 -> £3,395,820.39 (10.2%); £3,781,251.21 -> £3,395,820.41 (10.2%); £3,781,251.36 -> £3,395,820.43 (10.2%); £3,781,251.51 -> £3,395,820.44 (10.2%); £3,781,251.67 -> £3,395,820.46 (10.2%); £3,781,251.82 -> £3,395,820.48 (10.2%); £3,781,251.97 -> £3,395,820.49 (10.2%); £3,781,252.12 -> £3,395,820.51 (10.2%); £3,781,252.27 -> £3,395,820.53 (10.2%); £3,781,252.42 -> £3,395,820.63 (10.2%); £3,781,252.57 -> £3,395,820.74 (10.2%); £3,781,252.74 -> £3,395,820.86 (10.2%); £3,781,252.92 -> £3,395,820.98 (10.2%); £3,781,253.13 -> £3,395,821.10 (10.2%); £3,781,253.34 -> £3,395,821.21 (10.2%); £3,781,253.58 -> £3,395,821.32 (10.2%); £3,781,253.83 -> £3,395,821.43 (10.2%); £3,781,254.09 -> £3,395,821.45 (10.2%); £3,781,254.34 -> £3,395,821.48 (10.2%); £3,781,254.58 -> £3,395,821.50 (10.2%); £3,781,254.84 -> £3,395,821.52 (10.2%); £3,781,255.08 -> £3,395,821.55 (10.2%); £3,781,255.34 -> £3,395,821.57 (10.2%); £3,781,255.59 -> £3,395,821.60 (10.2%); £3,781,255.84 -> £3,395,821.62 (10.2%); £3,781,256.10 -> £3,395,821.65 (10.2%); £3,781,256.35 -> £3,395,821.67 (10.2%); £3,781,256.60 -> £3,395,821.69 (10.2%); £3,781,256.85 -> £3,395,821.72 (10.2%); £3,781,257.10 -> £3,395,821.75 (10.2%); £3,781,257.35 -> £3,395,821.86 (10.2%); £3,781,257.61 -> £3,395,821.98 (10.2%); £3,781,257.86 -> £3,395,822.10 (10.2%); £3,781,258.11 -> £3,395,822.23 (10.2%); £3,781,258.36 -> £3,395,822.36 (10.2%); £3,781,258.61 -> £3,395,822.48 (10.2%); £3,781,258.86 -> £3,395,822.59 (10.2%); £3,781,259.11 -> £3,395,822.71 (10.2%); £3,781,259.37 -> £3,395,822.82 (10.2%); £3,781,259.62 -> £3,395,822.94 (10.2%); £3,781,259.88 -> £3,395,823.06 (10.2%); £3,781,260.13 -> £3,395,823.08 (10.2%); £3,781,260.38 -> £3,395,823.11 (10.2%); £3,781,260.61 -> £3,395,823.14 (10.2%); £3,781,260.82 -> £3,395,823.16 (10.2%); £3,781,261.01 -> £3,395,823.18 (10.2%); £3,781,261.14 -> £3,395,823.20 (10.2%); £3,781,261.28 -> £3,395,823.22 (10.2%); £3,781,261.41 -> £3,395,823.24 (10.2%); £3,781,261.55 -> £3,395,823.25 (10.2%); £3,781,261.69 -> £3,395,823.27 (10.2%); £3,781,261.82 -> £3,395,823.29 (10.2%); £3,781,261.96 -> £3,395,823.30 (10.2%); £3,781,262.09 -> £3,395,823.32 (10.2%); £3,781,262.23 -> £3,395,823.34 (10.2%); £3,781,262.36 -> £3,395,823.35 (10.2%); £3,781,262.50 -> £3,395,823.37 (10.2%); £3,781,262.63 -> £3,395,823.51 (10.2%); £3,781,262.77 -> £3,395,823.65 (10.2%); £3,781,262.92 -> £3,395,823.80 (10.2%); £3,781,263.09 -> £3,395,823.94 (10.2%); £3,781,263.27 -> £3,395,824.09 (10.2%); £3,781,263.47 -> £3,395,824.24 (10.2%); £3,781,263.68 -> £3,395,824.39 (10.2%); £3,781,263.90 -> £3,395,824.55 (10.2%); £3,781,264.12 -> £3,395,824.57 (10.2%); £3,781,264.35 -> £3,395,824.60 (10.2%); £3,781,264.57 -> £3,395,824.63 (10.2%); £3,781,264.80 -> £3,395,824.65 (10.2%); £3,781,265.02 -> £3,395,824.68 (10.2%); £3,781,265.24 -> £3,395,824.71 (10.2%); £3,781,265.47 -> £3,395,824.73 (10.2%); £3,781,265.70 -> £3,395,824.76 (10.2%); £3,781,265.91 -> £3,395,824.78 (10.2%); £3,781,266.12 -> £3,395,824.81 (10.2%); £3,781,266.35 -> £3,395,824.83 (10.2%); £3,781,266.56 -> £3,395,824.86 (10.2%); £3,781,266.78 -> £3,395,824.89 (10.2%); £3,781,267.01 -> £3,395,825.04 (10.2%); £3,781,267.23 -> £3,395,825.19 (10.2%); £3,781,267.46 -> £3,395,825.34 (10.2%); £3,781,267.69 -> £3,395,825.50 (10.2%); £3,781,267.91 -> £3,395,825.65 (10.2%); £3,781,268.14 -> £3,395,825.81 (10.2%); £3,781,268.36 -> £3,395,825.96 (10.2%); £3,781,268.58 -> £3,395,826.12 (10.2%); £3,781,268.81 -> £3,395,826.27 (10.2%); £3,781,269.03 -> £3,395,826.42 (10.2%); £3,781,269.25 -> £3,395,826.58 (10.2%); £3,781,269.47 -> £3,395,826.61 (10.2%); £3,781,269.70 -> £3,395,826.64 (10.2%); £3,781,269.90 -> £3,395,826.66 (10.2%); £3,781,270.09 -> £3,395,826.68 (10.2%); £3,781,270.27 -> £3,395,826.71 (10.2%); £3,781,270.40 -> £3,395,826.73 (10.2%); £3,781,270.53 -> £3,395,826.75 (10.2%); £3,781,270.67 -> £3,395,826.76 (10.2%); £3,781,270.80 -> £3,395,826.78 (10.2%); £3,781,270.94 -> £3,395,826.80 (10.2%); £3,781,271.07 -> £3,395,826.82 (10.2%); £3,781,271.20 -> £3,395,826.83 (10.2%); £3,781,271.34 -> £3,395,826.85 (10.2%); £3,781,271.48 -> £3,395,826.87 (10.2%); £3,781,271.62 -> £3,395,826.88 (10.2%); £3,781,271.76 -> £3,395,826.90 (10.2%); £3,781,271.89 -> £3,395,826.97 (10.2%); £3,781,272.03 -> £3,395,827.05 (10.2%); £3,781,272.17 -> £3,395,827.13 (10.2%); £3,781,272.34 -> £3,395,827.20 (10.2%); £3,781,272.52 -> £3,395,827.28 (10.2%); £3,781,272.72 -> £3,395,827.37 (10.2%); £3,781,272.93 -> £3,395,827.45 (10.2%); £3,781,273.16 -> £3,395,827.54 (10.2%); £3,781,273.39 -> £3,395,827.57 (10.2%); £3,781,273.62 -> £3,395,827.59 (10.2%); £3,781,273.84 -> £3,395,827.63 (10.2%); £3,781,274.06 -> £3,395,827.66 (10.2%); £3,781,274.29 -> £3,395,827.69 (10.2%); £3,781,274.52 -> £3,395,827.72 (10.2%); £3,781,274.75 -> £3,395,827.75 (10.2%); £3,781,274.98 -> £3,395,827.78 (10.2%); £3,781,275.20 -> £3,395,827.81 (10.2%); £3,781,275.43 -> £3,395,827.84 (10.2%); £3,781,275.66 -> £3,395,827.86 (10.2%); £3,781,275.89 -> £3,395,827.89 (10.2%); £3,781,276.11 -> £3,395,827.92 (10.2%); £3,781,276.34 -> £3,395,828.02 (10.2%); £3,781,276.56 -> £3,395,828.12 (10.2%); £3,781,276.79 -> £3,395,828.22 (10.2%); £3,781,277.02 -> £3,395,828.32 (10.2%); £3,781,277.24 -> £3,395,828.42 (10.2%); £3,781,277.47 -> £3,395,828.51 (10.2%); £3,781,277.69 -> £3,395,828.61 (10.2%); £3,781,277.92 -> £3,395,828.71 (10.2%); £3,781,278.14 -> £3,395,828.80 (10.2%); £3,781,278.36 -> £3,395,828.89 (10.2%); £3,781,278.59 -> £3,395,828.99 (10.2%); £3,781,278.82 -> £3,395,829.02 (10.2%); £3,781,279.04 -> £3,395,829.05 (10.2%); £3,781,279.26 -> £3,395,829.07 (10.2%); £3,781,279.45 -> £3,395,829.09 (10.2%); £3,781,279.63 -> £3,395,829.11 (10.2%); £3,781,279.79 -> £3,395,829.13 (10.2%); £3,781,279.94 -> £3,395,829.15 (10.2%); £3,781,280.09 -> £3,395,829.17 (10.2%); £3,781,280.25 -> £3,395,829.18 (10.2%); £3,781,280.40 -> £3,395,829.20 (10.2%); £3,781,280.55 -> £3,395,829.22 (10.2%); £3,781,280.71 -> £3,395,829.23 (10.2%); £3,781,280.86 -> £3,395,829.25 (10.2%); £3,781,281.01 -> £3,395,829.27 (10.2%); £3,781,281.16 -> £3,395,829.28 (10.2%); £3,781,281.32 -> £3,395,829.30 (10.2%); £3,781,281.47 -> £3,395,829.40 (10.2%); £3,781,281.63 -> £3,395,829.50 (10.2%); £3,781,281.80 -> £3,395,829.60 (10.2%); £3,781,281.99 -> £3,395,829.70 (10.2%); £3,781,282.19 -> £3,395,829.81 (10.2%); £3,781,282.41 -> £3,395,829.92 (10.2%); £3,781,282.66 -> £3,395,830.03 (10.2%); £3,781,282.92 -> £3,395,830.13 (10.2%); £3,781,283.17 -> £3,395,830.16 (10.2%); £3,781,283.42 -> £3,395,830.18 (10.2%); £3,781,283.68 -> £3,395,830.20 (10.2%); £3,781,283.93 -> £3,395,830.23 (10.2%); £3,781,284.17 -> £3,395,830.25 (10.2%); £3,781,284.43 -> £3,395,830.28 (10.2%); £3,781,284.68 -> £3,395,830.30 (10.2%); £3,781,284.94 -> £3,395,830.32 (10.2%); £3,781,285.21 -> £3,395,830.35 (10.2%); £3,781,285.46 -> £3,395,830.37 (10.2%); £3,781,285.72 -> £3,395,830.39 (10.2%); £3,781,285.98 -> £3,395,830.42 (10.2%); £3,781,286.24 -> £3,395,830.45 (10.2%); £3,781,286.50 -> £3,395,830.56 (10.2%); £3,781,286.75 -> £3,395,830.68 (10.2%); £3,781,287.01 -> £3,395,830.81 (10.2%); £3,781,287.26 -> £3,395,830.92 (10.2%); £3,781,287.53 -> £3,395,831.04 (10.2%); £3,781,287.79 -> £3,395,831.16 (10.2%); £3,781,288.04 -> £3,395,831.28 (10.2%); £3,781,288.29 -> £3,395,831.39 (10.2%); £3,781,288.55 -> £3,395,831.51 (10.2%); £3,781,288.80 -> £3,395,831.63 (10.2%); £3,781,289.06 -> £3,395,831.74 (10.2%); £3,781,289.32 -> £3,395,831.77 (10.2%); £3,781,289.58 -> £3,395,831.80 (10.2%); £3,781,289.81 -> £3,395,831.82 (10.2%); £3,781,290.03 -> £3,395,831.85 (10.2%); £3,781,290.22 -> £3,395,831.87 (10.2%); £3,781,290.38 -> £3,395,831.89 (10.2%); £3,781,290.54 -> £3,395,831.90 (10.2%); £3,781,290.69 -> £3,395,831.92 (10.2%); £3,781,290.84 -> £3,395,831.94 (10.2%); £3,781,291.00 -> £3,395,831.95 (10.2%); £3,781,291.15 -> £3,395,831.97 (10.2%); £3,781,291.31 -> £3,395,831.99 (10.2%); £3,781,291.46 -> £3,395,832.00 (10.2%); £3,781,291.62 -> £3,395,832.02 (10.2%); £3,781,291.77 -> £3,395,832.04 (10.2%); £3,781,291.93 -> £3,395,832.06 (10.2%); £3,781,292.08 -> £3,395,832.14 (10.2%); £3,781,292.24 -> £3,395,832.22 (10.2%); £3,781,292.41 -> £3,395,832.31 (10.2%); £3,781,292.61 -> £3,395,832.40 (10.2%); £3,781,292.82 -> £3,395,832.49 (10.2%); £3,781,293.04 -> £3,395,832.58 (10.2%); £3,781,293.28 -> £3,395,832.68 (10.2%); £3,781,293.54 -> £3,395,832.77 (10.2%); £3,781,293.79 -> £3,395,832.79 (10.2%); £3,781,294.04 -> £3,395,832.81 (10.2%); £3,781,294.30 -> £3,395,832.84 (10.2%); £3,781,294.56 -> £3,395,832.86 (10.2%); £3,781,294.81 -> £3,395,832.89 (10.2%); £3,781,295.07 -> £3,395,832.91 (10.2%); £3,781,295.34 -> £3,395,832.93 (10.2%); £3,781,295.60 -> £3,395,832.96 (10.2%); £3,781,295.87 -> £3,395,832.98 (10.2%); £3,781,296.12 -> £3,395,833.00 (10.2%); £3,781,296.38 -> £3,395,833.03 (10.2%); £3,781,296.65 -> £3,395,833.05 (10.2%); £3,781,296.90 -> £3,395,833.08 (10.2%); £3,781,297.15 -> £3,395,833.18 (10.2%); £3,781,297.41 -> £3,395,833.27 (10.2%); £3,781,297.67 -> £3,395,833.37 (10.2%); £3,781,297.92 -> £3,395,833.47 (10.2%); £3,781,298.18 -> £3,395,833.57 (10.2%); £3,781,298.44 -> £3,395,833.67 (10.2%); £3,781,298.70 -> £3,395,833.78 (10.2%); £3,781,298.96 -> £3,395,833.88 (10.2%); £3,781,299.22 -> £3,395,833.97 (10.2%); £3,781,299.47 -> £3,395,834.07 (10.2%); £3,781,299.72 -> £3,395,834.17 (10.2%); £3,781,299.98 -> £3,395,834.19 (10.2%); £3,781,300.24 -> £3,395,834.22 (10.2%); £3,781,300.48 -> £3,395,834.25 (10.2%); £3,781,300.70 -> £3,395,834.27 (10.2%); £3,781,300.89 -> £3,395,834.29 (10.2%); £3,781,301.04 -> £3,395,834.31 (10.2%); £3,781,301.20 -> £3,395,834.32 (10.2%); £3,781,301.35 -> £3,395,834.34 (10.2%); £3,781,301.51 -> £3,395,834.36 (10.2%); £3,781,301.66 -> £3,395,834.37 (10.2%); £3,781,301.81 -> £3,395,834.39 (10.2%); £3,781,301.97 -> £3,395,834.41 (10.2%); £3,781,302.12 -> £3,395,834.42 (10.2%); £3,781,302.28 -> £3,395,834.44 (10.2%); £3,781,302.44 -> £3,395,834.46 (10.2%); £3,781,302.60 -> £3,395,834.47 (10.2%); £3,781,302.75 -> £3,395,834.57 (10.2%); £3,781,302.91 -> £3,395,834.67 (10.2%); £3,781,303.08 -> £3,395,834.78 (10.2%); £3,781,303.26 -> £3,395,834.89 (10.2%); £3,781,303.47 -> £3,395,835.00 (10.2%); £3,781,303.70 -> £3,395,835.11 (10.2%); £3,781,303.95 -> £3,395,835.21 (10.2%); £3,781,304.21 -> £3,395,835.32 (10.2%); £3,781,304.46 -> £3,395,835.34 (10.2%); £3,781,304.72 -> £3,395,835.37 (10.2%); £3,781,304.97 -> £3,395,835.39 (10.2%); £3,781,305.23 -> £3,395,835.41 (10.2%); £3,781,305.49 -> £3,395,835.44 (10.2%); £3,781,305.74 -> £3,395,835.46 (10.2%); £3,781,306.00 -> £3,395,835.48 (10.2%); £3,781,306.25 -> £3,395,835.51 (10.2%); £3,781,306.50 -> £3,395,835.53 (10.2%); £3,781,306.76 -> £3,395,835.55 (10.2%); £3,781,307.02 -> £3,395,835.58 (10.2%); £3,781,307.27 -> £3,395,835.60 (10.2%); £3,781,307.53 -> £3,395,835.63 (10.2%); £3,781,307.79 -> £3,395,835.75 (10.2%); £3,781,308.05 -> £3,395,835.87 (10.2%); £3,781,308.31 -> £3,395,835.99 (10.2%); £3,781,308.57 -> £3,395,836.10 (10.2%); £3,781,308.82 -> £3,395,836.21 (10.2%); £3,781,309.08 -> £3,395,836.33 (10.2%); £3,781,309.34 -> £3,395,836.44 (10.2%); £3,781,309.60 -> £3,395,836.56 (10.2%); £3,781,309.85 -> £3,395,836.67 (10.2%); £3,781,310.11 -> £3,395,836.79 (10.2%); £3,781,310.36 -> £3,395,836.91 (10.2%); £3,781,310.61 -> £3,395,836.94 (10.2%); £3,781,310.87 -> £3,395,836.96 (10.2%); £3,781,311.11 -> £3,395,836.99 (10.2%); £3,781,311.34 -> £3,395,837.01 (10.2%); £3,781,311.54 -> £3,395,837.03 (10.2%); £3,781,311.70 -> £3,395,837.05 (10.2%); £3,781,311.85 -> £3,395,837.07 (10.2%); £3,781,312.00 -> £3,395,837.08 (10.2%); £3,781,312.15 -> £3,395,837.10 (10.2%); £3,781,312.31 -> £3,395,837.12 (10.2%); £3,781,312.46 -> £3,395,837.13 (10.2%); £3,781,312.61 -> £3,395,837.15 (10.2%); £3,781,312.76 -> £3,395,837.17 (10.2%); £3,781,312.91 -> £3,395,837.18 (10.2%); £3,781,313.06 -> £3,395,837.20 (10.2%); £3,781,313.21 -> £3,395,837.22 (10.2%); £3,781,313.37 -> £3,395,837.33 (10.2%); £3,781,313.52 -> £3,395,837.45 (10.2%); £3,781,313.70 -> £3,395,837.57 (10.2%); £3,781,313.88 -> £3,395,837.69 (10.2%); £3,781,314.08 -> £3,395,837.81 (10.2%); £3,781,314.31 -> £3,395,837.93 (10.2%); £3,781,314.55 -> £3,395,838.05 (10.2%); £3,781,314.80 -> £3,395,838.17 (10.2%); £3,781,315.06 -> £3,395,838.20 (10.2%); £3,781,315.32 -> £3,395,838.22 (10.2%); £3,781,315.57 -> £3,395,838.24 (10.2%); £3,781,315.82 -> £3,395,838.27 (10.2%); £3,781,316.09 -> £3,395,838.29 (10.2%); £3,781,316.34 -> £3,395,838.32 (10.2%); £3,781,316.60 -> £3,395,838.34 (10.2%); £3,781,316.85 -> £3,395,838.36 (10.2%); £3,781,317.10 -> £3,395,838.39 (10.2%); £3,781,317.36 -> £3,395,838.41 (10.2%); £3,781,317.62 -> £3,395,838.43 (10.2%); £3,781,317.87 -> £3,395,838.46 (10.2%); £3,781,318.13 -> £3,395,838.49 (10.2%); £3,781,318.38 -> £3,395,838.62 (10.2%); £3,781,318.63 -> £3,395,838.75 (10.2%); £3,781,318.89 -> £3,395,838.89 (10.2%); £3,781,319.15 -> £3,395,839.02 (10.2%); £3,781,319.41 -> £3,395,839.16 (10.2%); £3,781,319.66 -> £3,395,839.29 (10.2%); £3,781,319.92 -> £3,395,839.43 (10.2%); £3,781,320.18 -> £3,395,839.56 (10.2%); £3,781,320.43 -> £3,395,839.69 (10.2%); £3,781,320.68 -> £3,395,839.82 (10.2%); £3,781,320.93 -> £3,395,839.95 (10.2%); £3,781,321.19 -> £3,395,839.98 (10.2%); £3,781,321.44 -> £3,395,840.00 (10.2%); £3,781,321.68 -> £3,395,840.03 (10.2%); £3,781,321.90 -> £3,395,840.05 (10.2%); £3,781,322.10 -> £3,395,840.07 (10.2%); £3,781,322.26 -> £3,395,840.09 (10.2%); £3,781,322.41 -> £3,395,840.11 (10.2%); £3,781,322.56 -> £3,395,840.13 (10.2%); £3,781,322.71 -> £3,395,840.14 (10.2%); £3,781,322.87 -> £3,395,840.16 (10.2%); £3,781,323.02 -> £3,395,840.18 (10.2%); £3,781,323.17 -> £3,395,840.19 (10.2%); £3,781,323.32 -> £3,395,840.21 (10.2%); £3,781,323.47 -> £3,395,840.23 (10.2%); £3,781,323.62 -> £3,395,840.24 (10.2%); £3,781,323.77 -> £3,395,840.26 (10.2%); £3,781,323.93 -> £3,395,840.38 (10.2%); £3,781,324.08 -> £3,395,840.49 (10.2%); £3,781,324.25 -> £3,395,840.63 (10.2%); £3,781,324.44 -> £3,395,840.76 (10.2%); £3,781,324.66 -> £3,395,840.88 (10.2%); £3,781,324.87 -> £3,395,841.01 (10.2%); £3,781,325.12 -> £3,395,841.14 (10.2%); £3,781,325.38 -> £3,395,841.27 (10.2%); £3,781,325.64 -> £3,395,841.29 (10.2%); £3,781,325.91 -> £3,395,841.31 (10.2%); £3,781,326.16 -> £3,395,841.34 (10.2%); £3,781,326.42 -> £3,395,841.36 (10.2%); £3,781,326.68 -> £3,395,841.39 (10.2%); £3,781,326.94 -> £3,395,841.41 (10.2%); £3,781,327.19 -> £3,395,841.43 (10.2%); £3,781,327.45 -> £3,395,841.46 (10.2%); £3,781,327.70 -> £3,395,841.48 (10.2%); £3,781,327.96 -> £3,395,841.51 (10.2%); £3,781,328.22 -> £3,395,841.53 (10.2%); £3,781,328.48 -> £3,395,841.56 (10.2%); £3,781,328.74 -> £3,395,841.59 (10.2%); £3,781,328.99 -> £3,395,841.72 (10.2%); £3,781,329.25 -> £3,395,841.86 (10.2%); £3,781,329.51 -> £3,395,841.99 (10.2%); £3,781,329.77 -> £3,395,842.13 (10.2%); £3,781,330.02 -> £3,395,842.27 (10.2%); £3,781,330.28 -> £3,395,842.40 (10.2%); £3,781,330.54 -> £3,395,842.53 (10.2%); £3,781,330.80 -> £3,395,842.67 (10.2%); £3,781,331.06 -> £3,395,842.80 (10.2%); £3,781,331.31 -> £3,395,842.93 (10.2%); £3,781,331.57 -> £3,395,843.07 (10.2%); £3,781,331.83 -> £3,395,843.10 (10.2%); £3,781,332.09 -> £3,395,843.13 (10.2%); £3,781,332.33 -> £3,395,843.15 (10.2%); £3,781,332.55 -> £3,395,843.17 (10.2%); £3,781,332.75 -> £3,395,843.19 (10.2%); £3,781,332.89 -> £3,395,843.21 (10.2%); £3,781,333.02 -> £3,395,843.23 (10.2%); £3,781,333.16 -> £3,395,843.25 (10.2%); £3,781,333.30 -> £3,395,843.27 (10.2%); £3,781,333.43 -> £3,395,843.29 (10.2%); £3,781,333.57 -> £3,395,843.30 (10.2%); £3,781,333.70 -> £3,395,843.32 (10.2%); £3,781,333.84 -> £3,395,843.34 (10.2%); £3,781,333.98 -> £3,395,843.35 (10.2%); £3,781,334.11 -> £3,395,843.37 (10.2%); £3,781,334.25 -> £3,395,843.39 (10.2%); £3,781,334.38 -> £3,395,843.55 (10.2%); £3,781,334.51 -> £3,395,843.72 (10.2%); £3,781,334.67 -> £3,395,843.89 (10.2%); £3,781,334.83 -> £3,395,844.07 (10.2%); £3,781,335.02 -> £3,395,844.25 (10.2%); £3,781,335.21 -> £3,395,844.43 (10.2%); £3,781,335.43 -> £3,395,844.61 (10.2%); £3,781,335.65 -> £3,395,844.79 (10.2%); £3,781,335.88 -> £3,395,844.82 (10.2%); £3,781,336.11 -> £3,395,844.85 (10.2%); £3,781,336.33 -> £3,395,844.88 (10.2%); £3,781,336.56 -> £3,395,844.90 (10.2%); £3,781,336.78 -> £3,395,844.93 (10.2%); £3,781,337.01 -> £3,395,844.96 (10.2%); £3,781,337.24 -> £3,395,844.99 (10.2%); £3,781,337.47 -> £3,395,845.01 (10.2%); £3,781,337.70 -> £3,395,845.04 (10.2%); £3,781,337.92 -> £3,395,845.07 (10.2%); £3,781,338.14 -> £3,395,845.09 (10.2%); £3,781,338.36 -> £3,395,845.12 (10.2%); £3,781,338.59 -> £3,395,845.15 (10.2%); £3,781,338.82 -> £3,395,845.32 (10.2%); £3,781,339.05 -> £3,395,845.49 (10.2%); £3,781,339.28 -> £3,395,845.67 (10.2%); £3,781,339.52 -> £3,395,845.84 (10.2%); £3,781,339.75 -> £3,395,846.01 (10.2%); £3,781,339.97 -> £3,395,846.18 (10.2%); £3,781,340.20 -> £3,395,846.35 (10.2%); £3,781,340.42 -> £3,395,846.54 (10.2%); £3,781,340.65 -> £3,395,846.72 (10.2%); £3,781,340.87 -> £3,395,846.88 (10.2%); £3,781,341.10 -> £3,395,847.06 (10.2%); £3,781,341.33 -> £3,395,847.09 (10.2%); £3,781,341.55 -> £3,395,847.12 (10.2%); £3,781,341.76 -> £3,395,847.14 (10.2%); £3,781,341.95 -> £3,395,847.17 (10.2%); £3,781,342.12 -> £3,395,847.19 (10.2%); £3,781,342.27 -> £3,395,847.21 (10.2%); £3,781,342.40 -> £3,395,847.23 (10.2%); £3,781,342.55 -> £3,395,847.25 (10.2%); £3,781,342.69 -> £3,395,847.27 (10.2%); £3,781,342.83 -> £3,395,847.28 (10.2%); £3,781,342.97 -> £3,395,847.30 (10.2%); £3,781,343.11 -> £3,395,847.32 (10.2%); £3,781,343.25 -> £3,395,847.34 (10.2%); £3,781,343.39 -> £3,395,847.35 (10.2%); £3,781,343.53 -> £3,395,847.37 (10.2%); £3,781,343.68 -> £3,395,847.39 (10.2%); £3,781,343.82 -> £3,395,847.53 (10.2%); £3,781,343.97 -> £3,395,847.68 (10.2%); £3,781,344.12 -> £3,395,847.82 (10.2%); £3,781,344.29 -> £3,395,847.97 (10.2%); £3,781,344.47 -> £3,395,848.13 (10.2%); £3,781,344.68 -> £3,395,848.28 (10.2%); £3,781,344.89 -> £3,395,848.44 (10.2%); £3,781,345.12 -> £3,395,848.60 (10.2%); £3,781,345.36 -> £3,395,848.63 (10.2%); £3,781,345.60 -> £3,395,848.66 (10.2%); £3,781,345.82 -> £3,395,848.69 (10.2%); £3,781,346.05 -> £3,395,848.72 (10.2%); £3,781,346.28 -> £3,395,848.75 (10.2%); £3,781,346.52 -> £3,395,848.79 (10.2%); £3,781,346.75 -> £3,395,848.82 (10.2%); £3,781,346.98 -> £3,395,848.85 (10.2%); £3,781,347.21 -> £3,395,848.88 (10.2%); £3,781,347.44 -> £3,395,848.90 (10.2%); £3,781,347.68 -> £3,395,848.93 (10.2%); £3,781,347.90 -> £3,395,848.96 (10.2%); £3,781,348.14 -> £3,395,848.99 (10.2%); £3,781,348.37 -> £3,395,849.14 (10.2%); £3,781,348.61 -> £3,395,849.29 (10.2%); £3,781,348.84 -> £3,395,849.44 (10.2%); £3,781,349.07 -> £3,395,849.60 (10.2%); £3,781,349.30 -> £3,395,849.75 (10.2%); £3,781,349.54 -> £3,395,849.90 (10.2%); £3,781,349.77 -> £3,395,850.05 (10.2%); £3,781,350.01 -> £3,395,850.20 (10.2%); £3,781,350.25 -> £3,395,850.35 (10.2%); £3,781,350.48 -> £3,395,850.50 (10.2%); £3,781,350.72 -> £3,395,850.66 (10.2%); £3,781,350.95 -> £3,395,850.69 (10.2%); £3,781,351.19 -> £3,395,850.71 (10.2%); £3,781,351.42 -> £3,395,850.74 (10.2%); £3,781,351.61 -> £3,395,850.76 (10.2%); £3,781,351.79 -> £3,395,850.78 (10.2%); £3,781,351.95 -> £3,395,850.80 (10.2%); £3,781,352.11 -> £3,395,850.82 (10.2%); £3,781,352.27 -> £3,395,850.83 (10.2%); £3,781,352.43 -> £3,395,850.85 (10.2%); £3,781,352.60 -> £3,395,850.87 (10.2%); £3,781,352.76 -> £3,395,850.88 (10.2%); £3,781,352.92 -> £3,395,850.90 (10.2%); £3,781,353.09 -> £3,395,850.92 (10.2%); £3,781,353.25 -> £3,395,850.93 (10.2%); £3,781,353.41 -> £3,395,850.95 (10.2%); £3,781,353.57 -> £3,395,850.97 (10.2%); £3,781,353.73 -> £3,395,851.11 (10.2%); £3,781,353.89 -> £3,395,851.24 (10.2%); £3,781,354.07 -> £3,395,851.39 (10.2%); £3,781,354.27 -> £3,395,851.54 (10.2%); £3,781,354.48 -> £3,395,851.69 (10.2%); £3,781,354.71 -> £3,395,851.84 (10.2%); £3,781,354.97 -> £3,395,851.98 (10.2%); £3,781,355.24 -> £3,395,852.13 (10.2%); £3,781,355.51 -> £3,395,852.16 (10.2%); £3,781,355.79 -> £3,395,852.18 (10.2%); £3,781,356.07 -> £3,395,852.20 (10.2%); £3,781,356.33 -> £3,395,852.23 (10.2%); £3,781,356.60 -> £3,395,852.25 (10.2%); £3,781,356.87 -> £3,395,852.28 (10.2%); £3,781,357.14 -> £3,395,852.30 (10.2%); £3,781,357.41 -> £3,395,852.32 (10.2%); £3,781,357.69 -> £3,395,852.35 (10.2%); £3,781,357.96 -> £3,395,852.37 (10.2%); £3,781,358.23 -> £3,395,852.39 (10.2%); £3,781,358.50 -> £3,395,852.42 (10.2%); £3,781,358.78 -> £3,395,852.45 (10.2%); £3,781,359.04 -> £3,395,852.59 (10.2%); £3,781,359.31 -> £3,395,852.74 (10.2%); £3,781,359.58 -> £3,395,852.89 (10.2%); £3,781,359.84 -> £3,395,853.04 (10.2%); £3,781,360.10 -> £3,395,853.19 (10.2%); £3,781,360.37 -> £3,395,853.34 (10.2%); £3,781,360.63 -> £3,395,853.49 (10.2%); £3,781,360.90 -> £3,395,853.63 (10.2%); £3,781,361.17 -> £3,395,853.78 (10.2%); £3,781,361.44 -> £3,395,853.93 (10.2%); £3,781,361.70 -> £3,395,854.07 (10.2%); £3,781,361.96 -> £3,395,854.10 (10.2%); £3,781,362.24 -> £3,395,854.13 (10.2%); £3,781,362.48 -> £3,395,854.15 (10.2%); £3,781,362.70 -> £3,395,854.18 (10.2%); £3,781,362.91 -> £3,395,854.20 (10.2%); £3,781,363.08 -> £3,395,854.21 (10.2%); £3,781,363.24 -> £3,395,854.23 (10.2%); £3,781,363.41 -> £3,395,854.25 (10.2%); £3,781,363.57 -> £3,395,854.27 (10.2%); £3,781,363.73 -> £3,395,854.28 (10.2%); £3,781,363.89 -> £3,395,854.30 (10.2%); £3,781,364.06 -> £3,395,854.32 (10.2%); £3,781,364.22 -> £3,395,854.33 (10.2%); £3,781,364.38 -> £3,395,854.35 (10.2%); £3,781,364.54 -> £3,395,854.36 (10.2%); £3,781,364.70 -> £3,395,854.38 (10.2%); £3,781,364.86 -> £3,395,854.49 (10.2%); £3,781,365.03 -> £3,395,854.61 (10.2%); £3,781,365.21 -> £3,395,854.73 (10.2%); £3,781,365.41 -> £3,395,854.86 (10.2%); £3,781,365.63 -> £3,395,854.98 (10.2%); £3,781,365.86 -> £3,395,855.11 (10.2%); £3,781,366.11 -> £3,395,855.23 (10.2%); £3,781,366.38 -> £3,395,855.35 (10.2%); £3,781,366.65 -> £3,395,855.38 (10.2%); £3,781,366.93 -> £3,395,855.40 (10.2%); £3,781,367.20 -> £3,395,855.43 (10.2%); £3,781,367.45 -> £3,395,855.45 (10.2%); £3,781,367.72 -> £3,395,855.47 (10.2%); £3,781,367.99 -> £3,395,855.50 (10.2%); £3,781,368.26 -> £3,395,855.52 (10.2%); £3,781,368.52 -> £3,395,855.54 (10.2%); £3,781,368.78 -> £3,395,855.57 (10.2%); £3,781,369.05 -> £3,395,855.59 (10.2%); £3,781,369.33 -> £3,395,855.61 (10.2%); £3,781,369.60 -> £3,395,855.64 (10.2%); £3,781,369.87 -> £3,395,855.67 (10.2%); £3,781,370.14 -> £3,395,855.79 (10.2%); £3,781,370.41 -> £3,395,855.93 (10.2%); £3,781,370.68 -> £3,395,856.06 (10.2%); £3,781,370.95 -> £3,395,856.19 (10.2%); £3,781,371.21 -> £3,395,856.32 (10.2%); £3,781,371.48 -> £3,395,856.45 (10.2%); £3,781,371.74 -> £3,395,856.58 (10.2%); £3,781,372.01 -> £3,395,856.71 (10.2%); £3,781,372.27 -> £3,395,856.84 (10.2%); £3,781,372.54 -> £3,395,856.97 (10.2%); £3,781,372.82 -> £3,395,857.09 (10.2%); £3,781,373.09 -> £3,395,857.12 (10.2%); £3,781,373.36 -> £3,395,857.15 (10.2%); £3,781,373.61 -> £3,395,857.18 (10.2%); £3,781,373.84 -> £3,395,857.20 (10.2%); £3,781,374.05 -> £3,395,857.22 (10.2%); £3,781,374.21 -> £3,395,857.24 (10.2%); £3,781,374.37 -> £3,395,857.25 (10.2%); £3,781,374.53 -> £3,395,857.27 (10.2%); £3,781,374.69 -> £3,395,857.29 (10.2%); £3,781,374.85 -> £3,395,857.30 (10.2%); £3,781,375.01 -> £3,395,857.32 (10.2%); £3,781,375.17 -> £3,395,857.34 (10.2%); £3,781,375.33 -> £3,395,857.35 (10.2%); £3,781,375.48 -> £3,395,857.37 (10.2%); £3,781,375.64 -> £3,395,857.39 (10.2%); £3,781,375.80 -> £3,395,857.41 (10.2%); £3,781,375.96 -> £3,395,857.54 (10.2%); £3,781,376.12 -> £3,395,857.68 (10.2%); £3,781,376.29 -> £3,395,857.83 (10.2%); £3,781,376.49 -> £3,395,857.98 (10.2%); £3,781,376.71 -> £3,395,858.13 (10.2%); £3,781,376.95 -> £3,395,858.28 (10.2%); £3,781,377.20 -> £3,395,858.42 (10.2%); £3,781,377.47 -> £3,395,858.57 (10.2%); £3,781,377.74 -> £3,395,858.59 (10.2%); £3,781,378.00 -> £3,395,858.61 (10.2%); £3,781,378.28 -> £3,395,858.64 (10.2%); £3,781,378.54 -> £3,395,858.66 (10.2%); £3,781,378.80 -> £3,395,858.69 (10.2%); £3,781,379.08 -> £3,395,858.71 (10.2%); £3,781,379.35 -> £3,395,858.73 (10.2%); £3,781,379.62 -> £3,395,858.76 (10.2%); £3,781,379.91 -> £3,395,858.78 (10.2%); £3,781,380.17 -> £3,395,858.80 (10.2%); £3,781,380.43 -> £3,395,858.83 (10.2%); £3,781,380.71 -> £3,395,858.85 (10.2%); £3,781,380.98 -> £3,395,858.88 (10.2%); £3,781,381.24 -> £3,395,859.04 (10.2%); £3,781,381.52 -> £3,395,859.20 (10.2%); £3,781,381.79 -> £3,395,859.36 (10.2%); £3,781,382.05 -> £3,395,859.52 (10.2%); £3,781,382.33 -> £3,395,859.68 (10.2%); £3,781,382.59 -> £3,395,859.83 (10.2%); £3,781,382.86 -> £3,395,859.99 (10.2%); £3,781,383.13 -> £3,395,860.14 (10.2%); £3,781,383.40 -> £3,395,860.29 (10.2%); £3,781,383.67 -> £3,395,860.44 (10.2%); £3,781,383.94 -> £3,395,860.58 (10.2%); £3,781,384.21 -> £3,395,860.61 (10.2%); £3,781,384.49 -> £3,395,860.64 (10.2%); £3,781,384.73 -> £3,395,860.66 (10.2%); £3,781,384.96 -> £3,395,860.69 (10.2%); £3,781,385.17 -> £3,395,860.71 (10.2%); £3,781,385.33 -> £3,395,860.72 (10.2%); £3,781,385.49 -> £3,395,860.74 (10.2%); £3,781,385.65 -> £3,395,860.76 (10.2%); £3,781,385.81 -> £3,395,860.78 (10.2%); £3,781,385.97 -> £3,395,860.79 (10.2%); £3,781,386.13 -> £3,395,860.81 (10.2%); £3,781,386.29 -> £3,395,860.83 (10.2%); £3,781,386.45 -> £3,395,860.84 (10.2%); £3,781,386.61 -> £3,395,860.86 (10.2%); £3,781,386.77 -> £3,395,860.88 (10.2%); £3,781,386.93 -> £3,395,860.89 (10.2%); £3,781,387.09 -> £3,395,861.04 (10.2%); £3,781,387.26 -> £3,395,861.18 (10.2%); £3,781,387.44 -> £3,395,861.33 (10.2%); £3,781,387.65 -> £3,395,861.47 (10.2%); £3,781,387.86 -> £3,395,861.62 (10.2%); £3,781,388.10 -> £3,395,861.77 (10.2%); £3,781,388.35 -> £3,395,861.91 (10.2%); £3,781,388.62 -> £3,395,862.05 (10.2%); £3,781,388.89 -> £3,395,862.07 (10.2%); £3,781,389.16 -> £3,395,862.10 (10.2%); £3,781,389.42 -> £3,395,862.12 (10.2%); £3,781,389.70 -> £3,395,862.14 (10.2%); £3,781,389.98 -> £3,395,862.17 (10.2%); £3,781,390.24 -> £3,395,862.19 (10.2%); £3,781,390.51 -> £3,395,862.21 (10.2%); £3,781,390.79 -> £3,395,862.24 (10.2%); £3,781,391.07 -> £3,395,862.26 (10.2%); £3,781,391.34 -> £3,395,862.28 (10.2%); £3,781,391.61 -> £3,395,862.31 (10.2%); £3,781,391.88 -> £3,395,862.33 (10.2%); £3,781,392.15 -> £3,395,862.36 (10.2%); £3,781,392.44 -> £3,395,862.51 (10.2%); £3,781,392.71 -> £3,395,862.66 (10.2%); £3,781,392.98 -> £3,395,862.81 (10.2%); £3,781,393.24 -> £3,395,862.96 (10.2%); £3,781,393.51 -> £3,395,863.11 (10.2%); £3,781,393.78 -> £3,395,863.26 (10.2%); £3,781,394.06 -> £3,395,863.41 (10.2%); £3,781,394.34 -> £3,395,863.56 (10.2%); £3,781,394.61 -> £3,395,863.70 (10.2%); £3,781,394.89 -> £3,395,863.85 (10.2%); £3,781,395.15 -> £3,395,863.99 (10.2%); £3,781,395.43 -> £3,395,864.02 (10.2%); £3,781,395.71 -> £3,395,864.04 (10.2%); £3,781,395.96 -> £3,395,864.07 (10.2%); £3,781,396.20 -> £3,395,864.09 (10.2%); £3,781,396.41 -> £3,395,864.11 (10.2%); £3,781,396.57 -> £3,395,864.13 (10.2%); £3,781,396.74 -> £3,395,864.15 (10.2%); £3,781,396.90 -> £3,395,864.16 (10.2%); £3,781,397.06 -> £3,395,864.18 (10.2%); £3,781,397.22 -> £3,395,864.20 (10.2%); £3,781,397.38 -> £3,395,864.21 (10.2%); £3,781,397.55 -> £3,395,864.23 (10.2%); £3,781,397.71 -> £3,395,864.25 (10.2%); £3,781,397.87 -> £3,395,864.26 (10.2%); £3,781,398.03 -> £3,395,864.28 (10.2%); £3,781,398.20 -> £3,395,864.30 (10.2%); £3,781,398.36 -> £3,395,864.42 (10.2%); £3,781,398.52 -> £3,395,864.54 (10.2%); £3,781,398.70 -> £3,395,864.67 (10.2%); £3,781,398.90 -> £3,395,864.80 (10.2%); £3,781,399.11 -> £3,395,864.94 (10.2%); £3,781,399.35 -> £3,395,865.07 (10.2%); £3,781,399.60 -> £3,395,865.19 (10.2%); £3,781,399.86 -> £3,395,865.32 (10.2%); £3,781,400.14 -> £3,395,865.35 (10.2%); £3,781,400.40 -> £3,395,865.37 (10.2%); £3,781,400.66 -> £3,395,865.39 (10.2%); £3,781,400.94 -> £3,395,865.42 (10.2%); £3,781,401.21 -> £3,395,865.44 (10.2%); £3,781,401.48 -> £3,395,865.47 (10.2%); £3,781,401.76 -> £3,395,865.49 (10.2%); £3,781,402.03 -> £3,395,865.51 (10.2%); £3,781,402.30 -> £3,395,865.54 (10.2%); £3,781,402.57 -> £3,395,865.56 (10.2%); £3,781,402.84 -> £3,395,865.58 (10.2%); £3,781,403.11 -> £3,395,865.61 (10.2%); £3,781,403.38 -> £3,395,865.64 (10.2%); £3,781,403.64 -> £3,395,865.77 (10.2%); £3,781,403.91 -> £3,395,865.91 (10.2%); £3,781,404.18 -> £3,395,866.05 (10.2%); £3,781,404.46 -> £3,395,866.19 (10.2%); £3,781,404.73 -> £3,395,866.33 (10.2%); £3,781,405.00 -> £3,395,866.47 (10.2%); £3,781,405.27 -> £3,395,866.61 (10.2%); £3,781,405.53 -> £3,395,866.75 (10.2%); £3,781,405.81 -> £3,395,866.90 (10.2%); £3,781,406.09 -> £3,395,867.04 (10.2%); £3,781,406.36 -> £3,395,867.17 (10.2%); £3,781,406.63 -> £3,395,867.20 (10.2%); £3,781,406.90 -> £3,395,867.23 (10.2%); £3,781,407.15 -> £3,395,867.25 (10.2%); £3,781,407.39 -> £3,395,867.27 (10.2%)
- Bills issued: 153, average clarity 0.806, average bill shock 17.0%, bad debt provision £0.00, avg complaint probability 4.8%
- Solvency signal: £315,364/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £201,263.61 vs. naked (unhedged) net margin: £607,649.06
- hedging cost £406,385.45 vs. a fully unhedged book (commodity-only: actual net £201,263.61 vs. naked net £607,649.06)
  - C1_2: actual £207.67 vs. naked £705.98 -- hedging cost £498.32
  - C2_2: actual £117.83 vs. naked £1,056.98 -- hedging cost £939.14
  - C5_2: actual £112.58 vs. naked £1,053.00 -- hedging cost £940.42
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £312.62 vs. naked £1,426.63 -- hedging cost £1,114.01
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £20,317.94 vs. naked £121,162.83 -- hedging cost £100,844.89
  - C_IC3g: actual £3,837.46 vs. naked £56,934.03 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £102,722.50 -- hedging cost £101,286.98

**Year narrative:** 2024 produced a net gain of £341,665.05 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 45 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £123,091.80 (gross £522,279.71, capital £5,697.53)
  - Electricity: gross £468,770.93, capital £5,697.53, net £118,642.02
  - Gas: gross £53,508.78, capital £0.00, net £4,449.79
- Treasury at year end: £3,836,062.59
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2025-01-08 period 31, net margin £-81.23

**Customer Book**

- Active accounts: 11 (C1_2, C2_2, C5_2, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £366,274.95
  - By billing account: C1 £4,496.52, C1_2 £4,029.13, C2 £6,127.56, C2_2 £3,634.31, C3 £5,965.37, C4 £3,010.84, C5 £9,867.03, C5_2 £4,365.25, C6 £15,480.62, C7 £7,930.18, C8 £8,246.08, C9 £9,103.46, C_IC1 £1,367,228.00, C_IC2 £856,669.63, C_IC3 £2,187,505.37, C_IC4 £1,366,739.83
- Bill shock events (>=20%): 25 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (40%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C1_2 2025-04-30 (42%); C1_2 2025-05-31 (28%); C1_2 2025-06-07 (80%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (35%); C2_2 2025-06-07 (73%); C5_2 2025-04-30 (29%); C5_2 2025-06-07 (79%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 32%, C8 32%, C9 26%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01/MWh, net margin £233.00
- C2_2 (electricity): tariff £201.48-£292.73/MWh, net margin £135.47
- C5_2 (electricity): tariff £231.60/MWh, net margin £135.46
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £19.93
- C8 (electricity): tariff £149.29-£309.47/MWh, net margin £118.59
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £225.43
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £63,404.31
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,994.92
- C_IC3 (electricity): tariff £89.47-£170.81/MWh, net margin £21,891.38
- C_IC3g (gas): tariff £54.85/MWh, net margin £4,449.79
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £2,483.52

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 66, average clarity 0.768, average bill shock 24.7%, bad debt provision £0.00, avg complaint probability 6.1%
- Solvency signal: £383,606/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £66.19 vs. naked (unhedged) net margin: £349.73
- hedging cost £283.54 vs. a fully unhedged book (commodity-only: actual net £66.19 vs. naked net £349.73)
  - C2_2: actual £96.28 vs. naked £230.84 -- hedging cost £134.56
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £123,091.80 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 25 customer(s) experienced a bill shock of >=20%.
