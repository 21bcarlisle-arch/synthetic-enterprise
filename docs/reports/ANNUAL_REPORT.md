# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,911,893.89
  (£1,445,257.67 net change)
- Solvency signal (final year): £383,551/customer (10 customers, OK; Ofgem floor £130/customer)
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
- Enterprise value (CLV sum across 16 billing accounts): £8,826,938.57
- Cost to serve (whole portfolio): £91,780.10, net margin after cost to serve: £6,324,095.49
- Hedge effectiveness (whole window): hedging cost £4,232,037.05 vs. a fully unhedged book (commodity-only: actual net £1,445,257.67 vs. naked net £5,677,294.72)

- **2021** (crisis year): net margin £76,353.28, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £336,064.81, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2244, I&C 98% | **AMBER** | Single I&C departure removes 14-29%% of margin |
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
- **2021 net margin**: £76,353.28 under the new mandate vs. £-1,096.43 under the old reactive model.
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
| 2017 | £30,139.92 | £0.00 | £288.00 | £528.14 | £516.54 | £31,472.60 |
| 2018 | £101,162.40 | £0.00 | £-187.39 | £245.65 | £436.94 | £101,657.60 |
| 2019 | £222,407.66 | £9,999.92 | £-271.25 | £793.60 | £489.73 | £233,419.66 |
| 2020 | £116,595.99 | £10,030.76 | £395.39 | £1,032.33 | £457.36 | £128,511.83 |
| 2021 | £66,401.97 | £9,999.92 | £-170.01 | £298.12 | £-176.72 | £76,353.28 |
| 2022 | £327,008.57 | £9,999.92 | £1,579.92 | £-1,367.38 | £-1,156.22 | £336,064.81 |
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
| C_IC1 | 2018-01-31 | renewed | 0.0500 | 0.5500 | 0.9677 | 0.3902 |
| C1 | 2018-12-31 | renewed | 0.1100 | 0.5500 | 0.9290 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.1100 | 0.3500 | 0.8718 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.2000 | 0.5500 | 0.8387 | 0.6312 |
| C_IC2 | 2019-01-31 | renewed | 0.0500 | 0.5500 | 0.9707 | 0.3710 |
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
| C_IC3 | 2021-12-31 | renewed | 0.3200 | 0.5500 | 0.9061 | 0.5838 |
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
| C6 | 2023-03-31 | renewed | 0.4100 | 0.3500 | 0.7933 | 0.5155 |
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
| 2018 | 2,487,380 | 11 | 226,125 | 1739.43× | OK |
| 2019 | 2,611,254 | 12 | 217,604 | 1673.88× | OK |
| 2020 | 2,922,973 | 14 | 208,784 | 1606.03× | OK |
| 2021 | 2,957,635 | 12 | 246,470 | 1895.92× | OK |
| 2022 | 3,158,915 | 14 | 225,637 | 1735.67× | OK |
| 2023 | 3,394,994 | 12 | 282,916 | 2176.28× | OK |
| 2024 | 3,783,819 | 12 | 315,318 | 2425.53× | OK |
| 2025 | 3,835,512 | 10 | 383,551 | 2950.39× | OK |

End-state (2025): **£383,551/account** across 10 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,434 | 81947.3× | OK |
| 2017 | 466 | 559 | 2,498,375 | 4468.9× | OK |
| 2018 | 849 | 1,019 | 2,487,380 | 2440.7× | OK |
| 2019 | 1,543 | 1,851 | 2,611,254 | 1410.6× | OK |
| 2020 | 1,979 | 2,375 | 2,922,973 | 1230.9× | OK |
| 2021 | 4,342 | 5,211 | 2,957,635 | 567.6× | OK |
| 2022 | 8,509 | 10,211 | 3,158,915 | 309.4× | OK |
| 2023 | 5,630 | 6,755 | 3,394,994 | 502.6× | OK |
| 2024 | 2,667 | 3,200 | 3,783,819 | 1182.5× | OK |
| 2025 | 3,902 | 4,682 | 3,835,512 | 819.1× | OK |




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

**Full-history EV:** £8,826,938.57 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £768,064.27 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £743.01 |
| 2017 | £31,472.60 |
| 2018 | £101,657.60 |
| 2019 | £233,419.66 |
| 2020 | £128,511.83 |
| 2021 | £76,353.28 |
| 2022 | £336,064.81 |
| 2023 | £161,777.83 | ← trailing
| 2024 | £341,665.05 | ← trailing
| 2025 | £123,091.80 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £5,484.28 | — |
| C1_2 | — | £677.53 |
| C2 | £7,339.85 | — |
| C2_2 | — | £1,637.20 |
| C3 | £6,823.79 | — |
| C4 | £3,921.60 | £-655.92 |
| C5 | £14,409.65 | — |
| C5_2 | — | £473.30 |
| C6 | £22,350.07 | £3,535.10 |
| C7 | £9,218.57 | £625.53 |
| C8 | £10,789.22 | £864.14 |
| C9 | £12,017.28 | £1,564.53 |
| C_IC1 | £1,979,417.19 | £430,673.75 |
| C_IC2 | £1,141,168.85 | £227,729.17 |
| C_IC3 | £3,764,767.63 | £83,354.85 |
| C_IC4 | £1,834,396.57 | £17,585.10 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C1_2 | C2 | C2_2 | C3 | C4 | C5 | C5_2 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £6,228.45 | — | — | — | — | — | £14,109.80 | — | — | £10,200.00 | — | — | — | — | — | — |
| 2017 | £5,470.70 | — | £10,821.00 | — | £9,473.64 | £8,371.99 | £11,735.66 | — | £23,920.37 | £8,667.92 | £13,323.56 | £10,874.42 | — | — | — | — |
| 2018 | £5,697.08 | — | £9,411.38 | — | £8,891.54 | £7,799.21 | £12,331.60 | — | £20,109.02 | £8,563.83 | £11,409.42 | £10,798.47 | £2,809,761.35 | — | — | — |
| 2019 | £6,046.01 | — | £9,483.53 | — | £9,318.53 | £7,754.22 | £13,910.73 | — | £20,752.15 | £9,842.14 | £11,020.84 | £10,646.87 | £2,649,003.90 | £1,764,083.33 | — | — |
| 2020 | £6,293.16 | £15.96 | £9,319.76 | — | £8,260.26 | £8,236.31 | £12,918.81 | — | £18,929.57 | £9,705.30 | £11,800.14 | £10,507.78 | £1,826,772.55 | £816,663.61 | £2,894,255.48 | £1,476,603.82 |
| 2021 | £5,295.46 | £1,215.38 | £7,182.87 | — | £6,963.40 | £5,891.46 | £12,404.05 | — | £21,264.35 | £8,502.43 | £11,083.85 | £11,184.62 | £1,613,852.65 | £946,833.37 | £2,594,930.48 | £1,678,673.09 |
| 2022 | £5,760.93 | £2,223.35 | £6,645.17 | £1,068.69 | £7,598.89 | £4,129.23 | £11,532.92 | £7.16 | £19,748.20 | £6,091.12 | £11,370.96 | £10,023.90 | £1,679,089.32 | £1,056,515.43 | £2,440,360.88 | £1,466,766.77 |
| 2023 | £6,142.89 | £1,992.91 | £6,136.90 | £3,717.08 | £6,214.40 | £2,912.30 | £10,629.41 | £912.14 | £19,004.78 | £6,681.84 | £8,929.80 | £9,648.06 | £1,543,308.03 | £824,338.30 | £2,389,942.94 | £1,408,103.70 |
| 2024 | £4,633.75 | £3,099.46 | £5,088.64 | £4,144.53 | £5,683.10 | £3,419.27 | £11,328.55 | £3,428.63 | £16,245.83 | £8,694.38 | £9,152.68 | £8,883.63 | £1,494,574.75 | £610,332.16 | £2,326,510.46 | £1,303,777.60 |
| 2025 | £4,338.09 | £3,856.07 | £5,911.85 | £3,493.53 | £5,747.90 | £2,772.74 | £9,675.09 | £4,275.95 | £15,200.05 | £7,594.48 | £7,947.09 | £8,801.76 | £1,355,811.81 | £849,459.41 | £2,158,651.79 | £1,349,750.16 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,370.48, range £54.46–£26,408.27.

- C1: cost to serve £344.89, net margin after CTS £1,948.84
- C1_2: cost to serve £476.66, net margin after CTS £5,179.59
- C1g: cost to serve £54.46, net margin after CTS £1,300.78
- C2: cost to serve £432.22, net margin after CTS £2,978.09
- C2_2: cost to serve £381.56, net margin after CTS £5,113.51
- C2g: cost to serve £83.87, net margin after CTS £1,935.34
- C3: cost to serve £292.52, net margin after CTS £2,096.31
- C3g: cost to serve £58.25, net margin after CTS £1,240.28
- C4: cost to serve £565.38, net margin after CTS £2,749.41
- C4g: cost to serve £216.57, net margin after CTS £1,127.40
- C5: cost to serve £1,056.93, net margin after CTS £10,944.62
- C5_2: cost to serve £416.37, net margin after CTS £5,914.60
- C6: cost to serve £1,349.00, net margin after CTS £21,086.52
- C7: cost to serve £954.99, net margin after CTS £9,860.29
- C8: cost to serve £939.21, net margin after CTS £11,529.68
- C9: cost to serve £896.59, net margin after CTS £11,811.56
- C_IC1: cost to serve £19,836.15, net margin after CTS £1,854,831.25
- C_IC2: cost to serve £11,344.53, net margin after CTS £898,484.24
- C_IC3: cost to serve £26,408.27, net margin after CTS £1,807,029.46
- C_IC3g: cost to serve £9,229.97, net margin after CTS £613,417.06
- C_IC4: cost to serve £16,441.72, net margin after CTS £1,090,243.56


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
| C1 | resi | MEDIUM | 22% | 7% | -23.0% [competitive] | £1,948.84 |
| C6 | SME | MEDIUM | 21% | 25% | -24.7% [competitive] | £21,086.52 |
| C_IC3 | I&C | MEDIUM | 20% | 13% | -53.5% [competitive] | £1,807,029.46 |
| C4 | resi | LOW | 14% | 14% | -9.0% | £2,749.41 |
| C2_2 | resi | LOW | 11% | 10% | +17.8% [overpriced] | £5,113.51 |
| C7 | resi | LOW | 11% | 17% | -14.3% | £9,860.29 |
| C9 | resi | LOW | 11% | 14% | -14.3% | £11,811.56 |
| C8 | resi | LOW | 9% | 13% | -23.6% [competitive] | £11,529.68 |
| C1_2 | resi | LOW | 8% | 14% | +3.3% | £5,179.59 |
| C3 | resi | LOW | 6% | 8% | -39.0% [competitive] | £2,096.31 |
| C5_2 | SME | LOW | 5% | 5% | -5.5% | £5,914.60 |
| C5 | SME | LOW | 5% | 5% | -45.8% [competitive] | £10,944.62 |
| C2 | resi | LOW | 5% | 6% | +46.6% [overpriced] | £2,978.09 |
| C_IC1 | I&C | LOW | 4% | 95% | -0.1% | £1,854,831.25 |
| C_IC2 | I&C | LOW | 4% | 95% | +12.4% [overpriced] | £898,484.24 |

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
| C3 | resi | 2020-06-30 | 4.0yr | -4.3% | -39.0% | 6% | 8% | £2,096.31 |
| C1 | resi | 2020-12-30 | 5.0yr | -0.8% | -23.0% | 22% | 7% | £1,948.84 |
| C2 | resi | 2022-03-31 | 6.0yr | +11.9% | +46.6% | 5% | 6% | £2,978.09 |
| C5 | SME | 2022-12-30 | 7.0yr | +5.4% | -45.8% | 5% | 5% | £10,944.62 |
| C6 | SME | 2024-03-30 | 8.0yr | -0.7% | -24.7% | 21% | 25% | £21,086.52 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 14% | 14% | £2,749.41 |

**Root Cause Summary:**
- Total churned accounts: 6
- Lifetime margin lost: £41,803.80
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
| 2017 | 14 | £16,735 | £8,803 | £2,248 | 13.4% |
| 2018 | 15 | £29,022 | £17,502 | £6,777 | 23.4% |
| 2019 | 17 | £70,486 | £41,296 | £13,731 | 19.5% |
| 2020 | 19 | £64,388 | £41,674 | £6,764 | 10.5% |
| 2021 | 15 | £115,949 | £51,083 | £5,090 | 4.4% << |
| 2022 | 17 | £202,451 | £61,719 | £19,769 | 9.8% |
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
| C1 | £339 | — | £339 |
| C1_2 | £641 | — | £641 |
| C1g | — | £669 | £669 |
| C2 | £2 | — | £2 |
| C2_2 | £1,557 | — | £1,557 |
| C2g | — | £907 | £907 |
| C3 | £-37 | — | £-37 * |
| C3g | — | £336 | £336 |
| C4 | £153 | — | £153 |
| C4g | — | £-1,625 | £-1,625 * |
| C5 | £-794 | — | £-794 * |
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
| **Total** | **£1,469,959** | **£64,799** | **£1,534,757** |

Loss-making accounts: C4g (£-1,625), C5 (£-794), C7 (£-510), C3 (£-37)
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
| 2017 | 2.69 | WATCH | £2,498,375 | £31,473 |
| 2018 | — | — | £2,487,380 | £101,658 |
| 2019 | — | — | £2,611,254 | £233,420 |
| 2020 | — | — | £2,922,973 | £128,512 |
| 2021 | — | — | £2,957,635 | £76,353 |
| 2022 | 2.70 | WATCH | £3,158,915 | £336,065 |
| 2023 | 2.73 | WATCH | £3,394,994 | £161,778 |
| 2024 | — | — | £3,783,819 | £341,665 |
| 2025 | — | — | £3,835,512 | £123,092 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,835,512)**
**Treasury growth: £2,467,434 → £3,835,512 (+£1,368,078)**

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
| Status Quo (hold gas) | £210,218 | — |
| Exit Gas (with churn risk) | £87,343 | -£122,875 |
| Reprice to Breakeven | £211,843 | +£1,625 |

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
| 2017 | 2017-12-31 | 48 | C2 | -£336 |
| 2018 | 2018-12-31 | 48 | C2 | -£297 |
| 2019 | 2019-12-31 | 48 | C5 | -£522 |
| 2020 | 2020-03-16 | 20 | C_IC1 | -£19 |
| 2021 | 2021-12-31 | 48 | C5 | -£447 |
| 2022 | 2022-03-30 | 48 | C2 | -£141 |
| 2023 | 2023-06-16 | 22 | C_IC1 | -£22 |
| 2024 | 2024-06-28 | 31 | C_IC1 | -£26 |
| 2025 | 2025-01-08 | 31 | C_IC1 | -£81 |

**Single worst period: 2019 2019-12-31 SP48 (C5, -£522)** — exposure from gas supply anchor at year-end pricing.

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
| 2016 | 16 | £196,493 | £105,336 | £10,815 | £12,281 |
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
| 2017 | +£2,707 | £37,159 | £469 | — | 168 |
| 2018 | +£9,875 | £65,510 | £433 | — | 180 |
| 2019 | +£28,353 | £164,625 | £660 | — | 204 |
| 2020 | +£35,391 | £238,638 | £0 | — | 205 |
| 2021 | +£15,010 | £246,702 | £721 | — | 180 |
| 2022 | -£49,827 CREDIT | £256,667 | £166 | 2 | 173 |
| 2023 | +£64,889 | £272,368 | £0 | 47 | 168 |
| 2024 | +£110,127 | £308,162 | £0 | 4271 | 153 |
| 2025 | +£47,047 | £136,010 | £0 | — | 66 |

**CfD turned CREDIT in 2022: -£49,827 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2021 (£721)**

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
| 2018 | £2,487,380 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,611,254 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,922,973 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,957,635 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,158,915 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,394,994 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,783,819 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,835,512 | AMBER | AMBER | GREEN | AMBER | RED |

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
| 2020 | 19 | 40.5% | £97,742 | £41,769 | 2.06% |
| 2021 | 15 | 29.5% | £161,423 | £51,184 | 1.95% |
| 2022 | 17 | 22.4% | £249,739 | £61,810 | 1.98% |
| 2023 | 14 | 25.4% | £249,697 | £69,660 | 2.20% |
| 2024 | 14 | 39.4% | £214,230 | £89,653 | 2.14% |
| 2025 | 11 | 38.9% | £112,099 | £47,527 | 2.98% |

**Best EBIT%: 2016 (45.2%)** | **Worst EBIT%: 2022 (22.4%)**
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
| 2016 | !45.2% | !51.2% | OK1.53% | ~0% |
| 2017 | !33.5% | !35.8% | OK1.80% | ~0% |
| 2018 | !41.6% | !44.0% | OK1.97% | ~0% |
| 2019 | !40.7% | !42.8% | OK1.87% | ~0% |
| 2020 | !40.5% | !42.7% | OK2.06% | OK11% |
| 2021 | !29.5% | !31.7% | OK1.95% | ~0% |
| 2022 | !22.4% | ~24.7% | OK1.98% | OK12% |
| 2023 | !25.4% | ~27.9% | OK2.20% | ~0% |
| 2024 | !39.4% | !41.8% | OK2.14% | OK14% |
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

**Total bad debt (all years):** £92,551
**Crisis stress incremental:** £138,826

**RAG [~]:** AMBER — Credit stress material but below 1% revenue

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (11 active customers) under 12-month forward scenarios.
Generated: 2026-07-05T05:43:14Z

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
| 2016 | 3 | £30,538 | £10,179 | — |
| 2017 | 9 | £102,659 | £11,407 | +£72,121 |
| 2018 | 10 | £2,904,773 | £290,477 | +£2,802,114 |
| 2019 | 11 | £4,511,862 | £410,169 | +£1,607,089 |
| 2020 | 14 | £7,110,282 | £507,877 | +£2,598,420 |
| 2021 | 14 | £6,925,277 | £494,663 | £-185,005 |
| 2022 | 16 | £6,728,933 | £420,558 | £-196,345 |
| 2023 | 16 | £6,248,615 | £390,538 | £-480,317 |
| 2024 | 16 | £5,818,997 | £363,687 | £-429,618 |
| 2025 | 16 | £5,793,288 | £362,080 | £-25,710 |

**Peak portfolio CLV: 2020 (£7,110,282)** | **Earliest/lowest: 2016 (£30,538)**
**Largest YoY gain: 2018 (+£2,802,114)**
**Largest YoY fall: 2023 (£-480,317)**

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
| 2016→2017 | +£30,730 | +£116,423 | +£133 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£70,185 | +£139,295 | +£35 | -£255 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£131,762 | +£439,496 | -£227 | -£781 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£104,908 | +£89,778 | +£660 | +£344 | -£162,663 | -£33,027 | +2 | policy levies | RED |
| 2020→2021 | -£52,159 | -£25,564 | -£721 | -£3,670 | -£19,932 | -£2,271 | -4 | gross margin | RED |
| 2021→2022 | +£259,712 | +£282,982 | +£555 | -£7,660 | -£1,107 | -£15,058 | +2 | gross margin | GREEN |
| 2022→2023 | -£174,287 | -£75,327 | +£166 | +£3,156 | -£70,820 | -£31,462 | -3 | gross margin | RED |
| 2023→2024 | +£179,887 | +£280,648 | +£0 | +£639 | -£100,877 | -£522 | +0 | gross margin | GREEN |
| 2024→2025 | -£218,573 | -£732,265 | +£0 | +£3,803 | +£382,565 | +£127,323 | -3 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£218,573)** | **Best transition: 2021→2022 (+£259,712)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Payment Portfolio Health (P2: Billing Infra)

Year-by-year bad debt rate and high-churn-risk customer concentration.

| Year | Bad Debt | Bad Debt Rate | At-Risk Customers | At-Risk % | Trend | RAG |
|------|----------|--------------|-----------------|----------|-------|-----|
| 2016 | £602 | 5.78% | 0/5 | 0% | — STABLE | RED |
| 2017 | £469 | 0.20% | 0/12 | 0% | ↓ IMPROVING | GREEN |
| 2018 | £433 | 0.10% | 1/13 | 8% | ↓ IMPROVING | GREEN |
| 2019 | £660 | 0.06% | 3/14 | 21% | ↓ IMPROVING | GREEN |
| 2020 | £0 | 0.00% | 5/16 | 31% | ↓ IMPROVING | AMBER |
| 2021 | £721 | 0.04% | 4/14 | 29% | ↑ DETERIORATING | GREEN |
| 2022 | £166 | 0.00% | 10/14 | 71% | ↓ IMPROVING | RED |
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
| 2016 | £2,473,581.11 | £1,279.55 | 1933.2x | ✓ GREEN | Yes |
| 2017 | £2,590,238.47 | £29,052.54 | 89.2x | ✓ GREEN | Yes |
| 2018 | £2,840,461.34 | £50,079.42 | 56.7x | ✓ GREEN | Yes |
| 2019 | £3,510,680.54 | £137,121.01 | 25.6x | ✓ GREEN | Yes |
| 2020 | £4,263,301.67 | £154,758.03 | 27.6x | ✓ GREEN | Yes |
| 2021 | £4,977,644.98 | £201,778.67 | 24.7x | ✓ GREEN | Yes |
| 2022 | £5,930,261.96 | £353,797.13 | 16.8x | ✓ GREEN | Yes |
| 2023 | £6,817,903.47 | £291,313.47 | 23.4x | ✓ GREEN | Yes |
| 2024 | £7,998,309.55 | £249,935.16 | 32.0x | ✓ GREEN | Yes |
| 2025 | £8,478,417.73 | £102,757.00 | 82.5x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.8x (equity £5,930,261.96 vs monthly revenue £353,797.13). RAG: GREEN.
**Strongest year:** 2016 — 1933.2x.

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
| 2016 | 13 | £2,473,581.11 | £2,467,433.90 | 35675w | 5.78% | ✗ BREACH |
| 2017 | 14 | £2,590,238.47 | £2,498,375.34 | 1170w | 0.20% | ✗ BREACH |
| 2018 | 15 | £2,840,461.34 | £2,487,379.56 | 749w | 0.10% | ✗ BREACH |
| 2019 | 17 | £3,510,680.54 | £2,611,253.66 | 274w | 0.06% | ✗ BREACH |
| 2020 | 19 | £4,263,301.67 | £2,922,973.31 | 352w | 0.00% | ✗ BREACH |
| 2021 | 15 | £4,977,644.98 | £2,957,634.93 | 158w | 0.04% | ✗ BREACH |
| 2022 | 17 | £5,930,261.96 | £3,158,914.62 | 69w | 0.00% | ✗ BREACH |
| 2023 | 14 | £6,817,903.47 | £3,394,993.56 | 108w | 0.00% | ✗ BREACH |
| 2024 | 14 | £7,998,309.55 | £3,783,819.14 | 211w | 0.00% | ✗ BREACH |
| 2025 | 11 | £8,478,417.73 | £3,835,512.32 | 440w | 0.00% | ✗ BREACH |

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
| 2017 | Yes | 14/14/14 | 1.5 | 0.1 | £33 |
| 2018 | Yes | 15/15/15 | 2.9 | 0.1 | £29 |
| 2019 | Yes | 17/17/17 | 7.1 | 2.8 | £39 |
| 2020 | Yes | 19/19/19 | 7.3 | 2.4 | £0 |
| 2021 | Yes | 15/15/15 | 9.6 | 6.0 | £48 |
| 2022 | Yes | 17/17/17 | 19.0 | 11.8 | £10 |
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
Median CLV: £12,017.28 | Median churn: 32% | Total portfolio CLV: £8,812,104.53

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC1 | £1,979,417.19 | 29% | 20.2 periods |
| C_IC4 | £1,834,396.57 | 20% | 19.3 periods |
| C6 | £22,350.07 | 29% | 19.8 periods |
| C9 | £12,017.28 | 26% | 25.9 periods |

Quadrant CLV: £3,848,181.10 (44% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £3,764,767.63 | 41% | 28.4 periods |
| C_IC2 | £1,141,168.85 | 32% | 23.1 periods |
| C5 | £14,409.65 | 38% | 26.7 periods |

Quadrant CLV: £4,920,346.12 (56% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C7 | £9,218.57 | 29% | 19.3 periods |
| C3 | £6,823.79 | 11% | 17.9 periods |

Quadrant CLV: £16,042.37 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £10,789.22 | 32% | 19.4 periods |
| C2 | £7,339.85 | 38% | 23.8 periods |
| C1 | £5,484.28 | 38% | 19.5 periods |
| C4 | £3,921.60 | 38% | 17.4 periods |

Quadrant CLV: £27,534.94 (0% of portfolio)

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
| 2017 | £30,956.06 | £516.54 | £231,632.96 | £2,660.42 | 1.1% | YES |
| 2018 | £101,220.66 | £436.94 | £432,208.83 | £3,113.94 | 0.7% | YES |
| 2019 | £222,930.01 | £10,489.65 | £1,060,498.38 | £137,766.14 | 11.5% | YES |
| 2020 | £118,023.71 | £10,488.12 | £1,102,256.74 | £121,119.88 | 9.9% | YES |
| 2021 | £66,530.08 | £9,823.20 | £1,441,837.83 | £297,399.17 | 17.1% | YES |
| 2022 | £327,221.11 | £8,843.70 | £2,853,337.99 | £588,329.77 | 17.1% | YES |
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
| STATUS_QUO | £210,217.64 | — | Current strategy |
| EXIT_GAS | £87,342.90 | £-122,874.74 | Remove gas; model elec churn risk |
| REPRICE_GAS | £211,842.77 | £1,625.13 | Raise gas tariff to break-even |

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
| SME electricity | £40,768.05 | £484.47 | £3,811.58 | 7.9x | Moderate |
| resi electricity | £58,551.31 | £646.88 | £6,715.99 | 10.4x | Moderate |
| resi gas | £6,016.94 | £197.67 | £287.56 | 1.5x | Low return |

## Portfolio Concentration Risk

Revenue concentration analysis across 21 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2244** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,264,005.57 (98.5% of total positive margin)
- resi: £58,871.08 (0.9% of total positive margin)
- SME: £37,945.75 (0.6% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,854,831.25 | 29.2% | 4% | £74,749.70 |
| C_IC3 | I&C | £1,807,029.46 | 28.4% | 20% | £366,646.28 |
| C_IC4 | I&C | £1,090,243.56 | 17.1% | 0% | £0.00 |
| C_IC2 | I&C | £898,484.24 | 14.1% | 4% | £32,974.37 |
| C_IC3g | I&C | £613,417.06 | 9.6% | 0% | £0.00 |

**Concentration Risk Warning:**
- I&C segment accounts for 98.5% of total portfolio margin
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
| C1+C1g | £338.91 | £669.14 | £1,008.04 | Yes |
| C2+C2g | £1.98 | £907.09 | £909.06 | Yes |
| C3+C3g | £-37.19 | £336.46 | £299.28 | Yes |
| C4+C4g | £153.50 | £-1,625.13 | £-1,471.63 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £64,798.54.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,534,757.47 across 21 billing accounts. Revenue: £14,060,576.00.

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
| 14 | C1 | fixed | £3,497.52 | £2,293.73 | £14.09 | £338.91 | 9.7% |
| 15 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £336.46 | 12.5% |
| 16 | C4 | fixed | £6,274.43 | £3,314.79 | £37.48 | £153.50 | 2.4% |
| 17 | C2 | fixed | £5,114.40 | £3,410.31 | £24.74 | £1.98 | 0.0% |
| 18 | C3 | fixed | £3,628.72 | £2,388.84 | £14.77 | £-37.19 | -1.0% |
| 19 | C7 | fixed | £21,792.85 | £10,815.29 | £139.94 | £-509.79 | -2.3% |
| 20 | C5 | fixed | £21,712.25 | £12,001.55 | £133.94 | £-794.24 | -3.7% |
| 21 | C4g | fixed | £10,370.30 | £1,343.97 | £144.75 | £-1,625.13 | -15.7% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,060,576 | 100.0% |
| Wholesale cost | -£7,607,974 | 54.1% |
| **Gross supply margin** | **£6,452,602** | **45.9%** |
| Policy + Network costs | -£4,955,912 | 35.2% |
| Capital cost | -£51,433 | 0.4% |
| **Net supply margin** | **£1,445,258** | **10.3%** |

> *The ledger's `net_margin_gbp` (£6,415,876) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,031,503 | 47.6% | 12.1% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 3.5% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £60,634 | 56.8% | 5.7% | CMA 3-8% | ✓ |
| resi/elec | £82,240 | 57.6% | 5.5% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £19,340 | 31.1% | 1.5% | Ofgem CMA 2-4% | ✓ |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: PASS** — all segments within benchmarks.
## Transaction Log

Total events: 3,535,662

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 3 |
| bad_debt_event | 1,605 |
| billing_event | 1,605 |
| capital_charge_event | 1,705,599 |
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
| Operating net margin | £6,409,613.09 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | £234.62 | £834.62 | £6,944.88 (45.2%) |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | £6,260.72 | £6,860.72 | £116,657.37 (33.5%) |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | £11,823.00 | £12,423.00 | £250,222.87 (41.6%) |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | £30,746.61 | £31,346.61 | £670,219.20 (40.7%) |
| 2020 | £1,857,096.31 | £431,628.21 | £631,861.95 | £793,606.15 | £38,269.56 | £39,019.56 | £752,621.12 (40.5%) |
| 2021 | £2,421,344.01 | £973,152.05 | £680,438.97 | £767,752.99 | £47,173.73 | £47,773.73 | £714,343.31 (29.5%) |
| 2022 | £4,245,565.53 | £2,392,501.35 | £802,298.72 | £1,050,765.46 | £84,252.31 | £84,852.31 | £952,616.98 (22.4%) |
| 2023 | £3,495,761.69 | £1,642,210.96 | £878,317.42 | £975,233.31 | £76,851.81 | £77,451.81 | £887,641.52 (25.4%) |
| 2024 | £2,999,221.95 | £933,180.92 | £810,905.76 | £1,255,135.26 | £64,215.74 | £65,228.24 | £1,180,406.08 (39.4%) |
| 2025 | £1,233,083.98 | £452,920.26 | £257,370.51 | £522,793.21 | £36,687.50 | £36,987.50 | £480,108.18 (38.9%) |
| **Total** | **£18,862,463.71** | | | | | | **£6,011,781.51 (31.9%)** |

**Best year:** 2024 — net £1,180,406.08 (39.4% margin)
**Worst year:** 2016 — net £6,944.88 (45.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,478,417.73 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,478,417.73** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £6,011,781.51 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,354.61 | +4.7% | £6,592.99 | £6,944.88 | +5.3% | AMBER |
| 2017 | £16,138.86 | £348,630.52 | +2060.2% | £7,252.29 | £116,657.37 | +1508.6% | RED |
| 2018 | £386,623.75 | £600,953.01 | +55.4% | £128,424.00 | £250,222.87 | +94.8% | RED |
| 2019 | £675,851.95 | £1,645,452.10 | +143.5% | £281,335.50 | £670,219.20 | +138.2% | RED |
| 2020 | £1,816,630.04 | £1,857,096.31 | +2.2% | £736,963.94 | £752,621.12 | +2.1% | GREEN |
| 2021 | £2,028,952.42 | £2,421,344.01 | +19.3% | £833,649.22 | £714,343.31 | -14.3% | AMBER |
| 2022 | £2,607,611.88 | £4,245,565.53 | +62.8% | £790,935.58 | £952,616.98 | +20.4% | RED |
| 2023 | £4,508,414.67 | £3,495,761.69 | -22.5% | £1,029,561.00 | £887,641.52 | -13.8% | AMBER |
| 2024 | £3,512,844.39 | £2,999,221.95 | -14.6% | £893,105.75 | £1,180,406.08 | +32.2% | RED |
| 2025 | £3,145,356.42 | £1,233,083.98 | -60.8% | £1,315,150.33 | £480,108.18 | -63.5% | RED |

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
- Average CLV (Point-in-Time, year-end 2016): £10,179.42
  - By billing account: C1 £6,228.45, C5 £14,109.80, C7 £10,200.00
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

- Net margin: £31,472.60 (gross £123,236.40, capital £1,273.22)
  - Electricity: gross £121,806.83, capital £1,258.37, net £30,956.06
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
- Worst single period: C2 on 2017-12-31 period 48, net margin £-335.59

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £11,406.58
  - By billing account: C1 £5,470.70, C2 £10,821.00, C3 £9,473.64, C4 £8,371.99, C5 £11,735.66, C6 £23,920.37, C7 £8,667.92, C8 £13,323.56, C9 £10,874.42
- Bill shock events (>=20%): 50 -- C1g 2017-01-31 (31%); C1g 2017-02-28 (28%); C1g 2017-05-31 (30%); C1g 2017-06-30 (30%); C1g 2017-09-30 (21%); C1g 2017-11-30 (70%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-05-31 (34%); C2g 2017-06-30 (29%); C2g 2017-09-30 (27%); C2g 2017-11-30 (66%); C2g 2017-12-31 (22%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-05-31 (30%); C3g 2017-06-30 (23%); C3g 2017-09-30 (21%); C3g 2017-11-30 (59%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (28%); C4 2017-09-30 (21%); C4 2017-10-31 (25%); C4 2017-11-30 (26%); C4g 2017-01-31 (23%); C4g 2017-02-28 (22%); C4g 2017-05-31 (33%); C4g 2017-06-30 (35%); C4g 2017-09-30 (36%); C4g 2017-10-31 (22%); C4g 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £117.65-£131.86/MWh, net margin £37.32
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £115.22
- C2 (electricity): tariff £107.62-£125.75/MWh, net margin £-260.44 -- **net-negative**
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £194.46
- C3 (electricity): tariff £98.21-£120.78/MWh, net margin £88.18
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £69.89
- C4 (electricity): tariff £98.43-£109.87/MWh, net margin £56.41
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £136.97
- C5 (electricity): tariff £119.51-£131.01/MWh, net margin £189.83
- C6 (electricity): tariff £107.62-£126.89/MWh, net margin £98.17
- C7 (electricity): tariff £96.38-£195.85/MWh, net margin £194.41
- C8 (electricity): tariff £84.56-£191.02/MWh, net margin £246.20
- C9 (electricity): tariff £77.16-£181.41/MWh, net margin £166.07
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £30,139.92

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.818, average bill shock 16.5%, bad debt provision £468.78, avg complaint probability 4.7%
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

**Year narrative:** 2017 produced a net gain of £31,472.60 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 50 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £101,657.60 (gross £262,531.43, capital £1,528.07)
  - Electricity: gross £261,168.63, capital £1,507.00, net £101,220.66
  - Gas: gross £1,362.80, capital £21.07, net £436.94
- Treasury at year end: £2,487,379.56
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.92 (avg 0.92), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C2 on 2018-12-31 period 48, net margin £-296.81

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £290,477.29
  - By billing account: C1 £5,697.08, C2 £9,411.38, C3 £8,891.54, C4 £7,799.21, C5 £12,331.60, C6 £20,109.02, C7 £8,563.83, C8 £11,409.42, C9 £10,798.47, C_IC1 £2,809,761.35
- Bill shock events (>=20%): 60 -- C1g 2018-04-30 (37%); C1g 2018-05-31 (29%); C1g 2018-06-30 (30%); C1g 2018-09-30 (25%); C1g 2018-10-31 (46%); C1g 2018-11-30 (27%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (28%); C2g 2018-05-31 (34%); C2g 2018-06-30 (34%); C2g 2018-09-30 (33%); C2g 2018-10-31 (45%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (28%); C3g 2018-05-31 (32%); C3g 2018-06-30 (29%); C3g 2018-08-31 (34%); C3g 2018-09-30 (34%); C3g 2018-10-31 (35%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (28%); C4 2018-09-30 (23%); C4 2018-10-31 (41%); C4 2018-11-30 (28%); C4g 2018-04-30 (36%); C4g 2018-05-31 (33%); C4g 2018-06-30 (36%); C4g 2018-09-30 (39%); C4g 2018-10-31 (85%); C4g 2018-11-30 (24%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C2 23%, C3 23%, C6 23%, C7 20%, C8 23%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £117.65-£149.68/MWh, net margin £28.02
- C1g (gas): tariff £33.49-£36.05/MWh, net margin £142.44
- C2 (electricity): tariff £125.75-£143.89/MWh, net margin £-228.29 -- **net-negative**
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
- Bills issued: 180, average clarity 0.810, average bill shock 16.0%, bad debt provision £433.32, avg complaint probability 4.7%
- Solvency signal: £226,125/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2018 produced a net gain of £101,657.60 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 60 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £233,419.66 (gross £702,027.61, capital £2,309.31)
  - Electricity: gross £625,973.77, capital £2,287.85, net £222,930.01
  - Gas: gross £76,053.84, capital £21.46, net £10,489.65
- Treasury at year end: £2,611,253.66
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2019-12-31 period 48, net margin £-521.63

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £410,169.30
  - By billing account: C1 £6,046.01, C2 £9,483.53, C3 £9,318.53, C4 £7,754.22, C5 £13,910.73, C6 £20,752.15, C7 £9,842.14, C8 £11,020.84, C9 £10,646.87, C_IC1 £2,649,003.90, C_IC2 £1,764,083.33
- Bill shock events (>=20%): 66 -- C1 2019-04-30 (21%); C1g 2019-01-31 (36%); C1g 2019-02-28 (26%); C1g 2019-05-31 (23%); C1g 2019-06-30 (35%); C1g 2019-10-31 (74%); C1g 2019-11-30 (43%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-01-31 (25%); C2g 2019-02-28 (26%); C2g 2019-04-30 (35%); C2g 2019-06-30 (32%); C2g 2019-07-31 (25%); C2g 2019-09-30 (30%); C2g 2019-10-31 (64%); C2g 2019-11-30 (28%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-02-28 (26%); C3g 2019-06-30 (33%); C3g 2019-07-31 (35%); C3g 2019-09-30 (35%); C3g 2019-10-31 (64%); C3g 2019-11-30 (31%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (31%); C4 2019-09-30 (25%); C4 2019-11-30 (26%); C4g 2019-01-31 (30%); C4g 2019-02-28 (25%); C4g 2019-05-31 (21%); C4g 2019-06-30 (33%); C4g 2019-07-31 (37%); C4g 2019-09-30 (31%); C4g 2019-10-31 (34%); C4g 2019-11-30 (35%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C1 29%, C4 35%, C5 35%, C7 29%, C9 23%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£149.68/MWh, net margin £110.02
- C1g (gas): tariff £25.33-£36.05/MWh, net margin £156.37
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £145.29
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £134.46
- C3 (electricity): tariff £120.68-£126.90/MWh, net margin £-63.95 -- **net-negative**
- C3g (gas): tariff £23.00-£28.80/MWh, net margin £97.85
- C4 (electricity): tariff £126.76-£149.37/MWh, net margin £115.42
- C4g (gas): tariff £19.47-£33.61/MWh, net margin £101.05
- C5 (electricity): tariff £126.10-£153.39/MWh, net margin £-400.60 -- **net-negative**
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
- Bills issued: 204, average clarity 0.824, average bill shock 17.1%, bad debt provision £660.15, avg complaint probability 4.7%
- Solvency signal: £217,604/customer (12 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2019 produced a net gain of £233,419.66 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £128,511.83 (gross £791,806.06, capital £1,965.47)
  - Electricity: gross £714,626.51, capital £1,955.18, net £118,023.71
  - Gas: gross £77,179.55, capital £10.29, net £10,488.12
- Treasury at year end: £2,922,973.31
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
- Average CLV (Point-in-Time, year-end 2020): £507,877.32
  - By billing account: C1 £6,293.16, C1_2 £15.96, C2 £9,319.76, C3 £8,260.26, C4 £8,236.31, C5 £12,918.81, C6 £18,929.57, C7 £9,705.30, C8 £11,800.14, C9 £10,507.78, C_IC1 £1,826,772.55, C_IC2 £816,663.61, C_IC3 £2,894,255.48, C_IC4 £1,476,603.82
- Bill shock events (>=20%): 53 -- C1g 2020-01-31 (21%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-29 (23%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (22%); C4 2020-11-30 (24%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (49%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 38%, C4 41%, C5 32%, C7 20%, C8 23%, C9 23%, C_IC1 41%, C_IC2 41%, C_IC3 20%

**Pricing & Margin**

- C1 (electricity): tariff £125.83/MWh, net margin £89.13
- C1_2 (electricity): tariff £133.55/MWh, net margin £-1.02 -- **net-negative**
- C1g (gas): tariff £25.33/MWh, net margin £145.23
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £200.43
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £143.77
- C3 (electricity): tariff £120.68/MWh, net margin £25.94
- C3g (gas): tariff £23.00/MWh, net margin £82.00
- C4 (electricity): tariff £122.47-£126.76/MWh, net margin £99.65
- C4g (gas): tariff £16.09-£19.47/MWh, net margin £86.36
- C5 (electricity): tariff £126.10-£137.07/MWh, net margin £-6.41 -- **net-negative**
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
- Bills issued: 205, average clarity 0.831, average bill shock 14.4%, bad debt provision £0.00, avg complaint probability 4.3%
- Solvency signal: £208,784/customer (14 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2020 produced a net gain of £128,511.83 across 19 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £76,353.28 (gross £766,241.93, capital £5,635.95)
  - Electricity: gross £683,633.14, capital £5,622.97, net £66,530.08
  - Gas: gross £82,608.79, capital £12.99, net £9,823.20
- Treasury at year end: £2,957,634.93
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.95 (avg 0.95), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C5 0.94 (avg 0.94), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2021-12-31 period 48, net margin £-447.11

**Customer Book**

- Active accounts: 15 (C1_2, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2021): £494,662.68
  - By billing account: C1 £5,295.46, C1_2 £1,215.38, C2 £7,182.87, C3 £6,963.40, C4 £5,891.46, C5 £12,404.05, C6 £21,264.35, C7 £8,502.43, C8 £11,083.85, C9 £11,184.62, C_IC1 £1,613,852.65, C_IC2 £946,833.37, C_IC3 £2,594,930.48, C_IC4 £1,678,673.09
- Bill shock events (>=20%): 52 -- C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (22%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (23%); C4 2021-10-31 (48%); C4 2021-11-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%); C1_2 2021-01-31 (1207%); C1_2 2021-05-31 (33%); C1_2 2021-06-30 (55%); C1_2 2021-10-31 (76%); C1_2 2021-11-30 (75%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C7 20%, C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £133.55-£332.49/MWh, net margin £-89.38 -- **net-negative**
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £197.77
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £126.10
- C4 (electricity): tariff £122.47-£183.00/MWh, net margin £-264.27 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-302.82 -- **net-negative**
- C5 (electricity): tariff £137.07-£353.26/MWh, net margin £-761.45 -- **net-negative**
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
- Bills issued: 180, average clarity 0.817, average bill shock 23.6%, bad debt provision £721.02, avg complaint probability 4.8%
- Solvency signal: £246,470/customer (12 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £76,353.28 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 52 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £336,064.81 (gross £1,049,224.19, capital £13,296.17)
  - Electricity: gross £958,868.27, capital £13,262.33, net £327,221.11
  - Gas: gross £90,355.92, capital £33.84, net £8,843.70
- Treasury at year end: £3,158,914.62
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
- Worst single period: C2 on 2022-03-30 period 48, net margin £-140.65

**Customer Book**

- Active accounts: 17 (C1_2, C2, C2_2, C2g, C4, C4g, C5, C5_2, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 3, gas (dual-fuel): 3
- New acquisitions this year: C2_2, C5_2
- Losses (churn) during year: C2, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2022): £420,558.31
  - By billing account: C1 £5,760.93, C1_2 £2,223.35, C2 £6,645.17, C2_2 £1,068.69, C3 £7,598.89, C4 £4,129.23, C5 £11,532.92, C5_2 £7.16, C6 £19,748.20, C7 £6,091.12, C8 £11,370.96, C9 £10,023.90, C_IC1 £1,679,089.32, C_IC2 £1,056,515.43, C_IC3 £2,440,360.88, C_IC4 £1,466,766.77
- Bill shock events (>=20%): 76 -- C5 2022-01-31 (128%); C5 2022-02-28 (21%); C5 2022-05-31 (25%); C5 2022-11-30 (48%); C5 2022-12-29 (29%); C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (57%); C_IC3 2022-01-31 (108%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C1_2 2022-01-31 (141%); C1_2 2022-02-28 (28%); C1_2 2022-04-30 (23%); C1_2 2022-05-31 (43%); C1_2 2022-06-30 (34%); C1_2 2022-09-30 (51%); C1_2 2022-11-30 (79%); C1_2 2022-12-31 (61%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 12 at risk (≥20% churn prob): C1_2 41%, C2 38%, C4 38%, C5 38%, C6 35%, C7 23%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.45-£332.49/MWh, net margin £178.50
- C2 (electricity): tariff £183.00/MWh, net margin £-127.58 -- **net-negative**
- C2_2 (electricity): tariff £361.95/MWh, net margin £219.72
- C2g (gas): tariff £35.00/MWh, net margin £2.93
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-189.38 -- **net-negative**
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
- Treasury drawdown events (>=10% threshold): 2 -- £3,468,686.84 -> £3,053,400.45 (12.0%); £3,468,864.84 -> £3,052,854.66 (12.0%)
- Bills issued: 173, average clarity 0.783, average bill shock 33.9%, bad debt provision £165.90, avg complaint probability 5.8%
- Solvency signal: £225,637/customer (14 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £336,064.81 across 17 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 76 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £161,777.83 (gross £973,896.95, capital £10,139.98)
  - Electricity: gross £852,956.85, capital £10,087.56, net £152,818.87
  - Gas: gross £120,940.11, capital £52.42, net £8,958.96
- Treasury at year end: £3,394,993.56
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
- Average CLV (Point-in-Time, year-end 2023): £390,538.47
  - By billing account: C1 £6,142.89, C1_2 £1,992.91, C2 £6,136.90, C2_2 £3,717.08, C3 £6,214.40, C4 £2,912.30, C5 £10,629.41, C5_2 £912.14, C6 £19,004.78, C7 £6,681.84, C8 £8,929.80, C9 £9,648.06, C_IC1 £1,543,308.03, C_IC2 £824,338.30, C_IC3 £2,389,942.94, C_IC4 £1,408,103.70
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
- Treasury drawdown events (>=10% threshold): 47 -- £3,777,490.16 -> £3,394,801.67 (10.1%); £3,777,490.31 -> £3,394,801.68 (10.1%); £3,777,490.46 -> £3,394,801.70 (10.1%); £3,777,490.61 -> £3,394,801.71 (10.1%); £3,777,490.77 -> £3,394,801.73 (10.1%); £3,777,490.92 -> £3,394,801.74 (10.1%); £3,777,491.07 -> £3,394,801.76 (10.1%); £3,777,491.23 -> £3,394,801.77 (10.1%); £3,777,491.38 -> £3,394,801.79 (10.1%); £3,777,491.54 -> £3,394,801.80 (10.1%); £3,777,491.70 -> £3,394,801.82 (10.1%); £3,777,491.85 -> £3,394,801.95 (10.1%); £3,777,492.01 -> £3,394,802.09 (10.1%); £3,777,492.18 -> £3,394,802.22 (10.1%); £3,777,492.37 -> £3,394,802.35 (10.1%); £3,777,492.58 -> £3,394,802.49 (10.1%); £3,777,492.80 -> £3,394,802.63 (10.1%); £3,777,493.04 -> £3,394,802.78 (10.1%); £3,777,493.31 -> £3,394,802.93 (10.1%); £3,777,493.56 -> £3,394,802.95 (10.1%); £3,777,493.82 -> £3,394,802.98 (10.1%); £3,777,494.07 -> £3,394,803.00 (10.1%); £3,777,494.34 -> £3,394,803.03 (10.1%); £3,777,494.60 -> £3,394,803.06 (10.1%); £3,777,494.86 -> £3,394,803.08 (10.1%); £3,777,495.13 -> £3,394,803.11 (10.1%); £3,777,495.39 -> £3,394,803.13 (10.1%); £3,777,495.65 -> £3,394,803.16 (10.1%); £3,777,495.91 -> £3,394,803.18 (10.1%); £3,777,496.16 -> £3,394,803.21 (10.1%); £3,777,496.42 -> £3,394,803.23 (10.1%); £3,777,496.67 -> £3,394,803.26 (10.1%); £3,777,496.93 -> £3,394,803.40 (10.1%); £3,777,497.19 -> £3,394,803.55 (10.1%); £3,777,497.45 -> £3,394,803.70 (10.1%); £3,777,497.71 -> £3,394,803.85 (10.1%); £3,777,497.97 -> £3,394,804.00 (10.1%); £3,777,498.23 -> £3,394,804.15 (10.1%); £3,777,498.50 -> £3,394,804.30 (10.1%); £3,777,498.76 -> £3,394,804.45 (10.1%); £3,777,499.02 -> £3,394,804.60 (10.1%); £3,777,499.28 -> £3,394,804.73 (10.1%); £3,777,499.54 -> £3,394,804.87 (10.1%); £3,777,499.80 -> £3,394,804.90 (10.1%); £3,777,500.06 -> £3,394,804.92 (10.1%); £3,777,500.30 -> £3,394,804.95 (10.1%); £3,777,500.52 -> £3,394,993.56 (10.1%)
- Bills issued: 168, average clarity 0.801, average bill shock 30.1%, bad debt provision £0.00, avg complaint probability 5.0%
- Solvency signal: £282,916/customer (12 customers) — OK (Ofgem floor £130/customer)

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
- Treasury at year end: £3,783,819.14
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
- Average CLV (Point-in-Time, year-end 2024): £363,687.34
  - By billing account: C1 £4,633.75, C1_2 £3,099.46, C2 £5,088.64, C2_2 £4,144.53, C3 £5,683.10, C4 £3,419.27, C5 £11,328.55, C5_2 £3,428.63, C6 £16,245.83, C7 £8,694.38, C8 £9,152.68, C9 £8,883.63, C_IC1 £1,494,574.75, C_IC2 £610,332.16, C_IC3 £2,326,510.46, C_IC4 £1,303,777.60
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
- Treasury drawdown events (>=10% threshold): 4271 -- £3,779,948.50 -> £3,394,993.60 (10.2%); £3,779,948.68 -> £3,394,993.62 (10.2%); £3,779,948.85 -> £3,394,993.64 (10.2%); £3,779,949.03 -> £3,394,993.65 (10.2%); £3,779,949.20 -> £3,394,993.67 (10.2%); £3,779,949.37 -> £3,394,993.69 (10.2%); £3,779,949.54 -> £3,394,993.70 (10.2%); £3,779,949.72 -> £3,394,993.72 (10.2%); £3,779,949.89 -> £3,394,993.74 (10.2%); £3,779,950.07 -> £3,394,993.75 (10.2%); £3,779,950.24 -> £3,394,993.77 (10.2%); £3,779,950.41 -> £3,394,993.91 (10.2%); £3,779,950.58 -> £3,394,994.06 (10.2%); £3,779,950.77 -> £3,394,994.21 (10.2%); £3,779,950.98 -> £3,394,994.37 (10.2%); £3,779,951.21 -> £3,394,994.53 (10.2%); £3,779,951.45 -> £3,394,994.69 (10.2%); £3,779,951.71 -> £3,394,994.84 (10.2%); £3,779,952.00 -> £3,394,994.99 (10.2%); £3,779,952.27 -> £3,394,995.02 (10.2%); £3,779,952.57 -> £3,394,995.04 (10.2%); £3,779,952.86 -> £3,394,995.06 (10.2%); £3,779,953.15 -> £3,394,995.09 (10.2%); £3,779,953.44 -> £3,394,995.11 (10.2%); £3,779,953.73 -> £3,394,995.14 (10.2%); £3,779,954.02 -> £3,394,995.16 (10.2%); £3,779,954.30 -> £3,394,995.18 (10.2%); £3,779,954.57 -> £3,394,995.21 (10.2%); £3,779,954.84 -> £3,394,995.23 (10.2%); £3,779,955.13 -> £3,394,995.25 (10.2%); £3,779,955.42 -> £3,394,995.28 (10.2%); £3,779,955.70 -> £3,394,995.31 (10.2%); £3,779,955.99 -> £3,394,995.47 (10.2%); £3,779,956.27 -> £3,394,995.64 (10.2%); £3,779,956.49 -> £3,394,995.80 (10.2%); £3,779,956.71 -> £3,394,995.96 (10.2%); £3,779,956.92 -> £3,394,996.14 (10.2%); £3,779,957.22 -> £3,394,996.31 (10.2%); £3,779,957.52 -> £3,394,996.48 (10.2%); £3,779,957.79 -> £3,394,996.65 (10.2%); £3,779,958.09 -> £3,394,996.82 (10.2%); £3,779,958.37 -> £3,394,996.98 (10.2%); £3,779,958.66 -> £3,394,997.15 (10.2%); £3,779,958.95 -> £3,394,997.18 (10.2%); £3,779,959.25 -> £3,394,997.21 (10.2%); £3,779,959.50 -> £3,394,997.24 (10.2%); £3,779,959.75 -> £3,394,997.26 (10.2%); £3,779,959.97 -> £3,394,997.28 (10.2%); £3,779,960.14 -> £3,394,997.30 (10.2%); £3,779,960.32 -> £3,394,997.32 (10.2%); £3,779,960.49 -> £3,394,997.34 (10.2%); £3,779,960.65 -> £3,394,997.35 (10.2%); £3,779,960.82 -> £3,394,997.37 (10.2%); £3,779,960.99 -> £3,394,997.39 (10.2%); £3,779,961.17 -> £3,394,997.40 (10.2%); £3,779,961.33 -> £3,394,997.42 (10.2%); £3,779,961.50 -> £3,394,997.44 (10.2%); £3,779,961.68 -> £3,394,997.46 (10.2%); £3,779,961.84 -> £3,394,997.47 (10.2%); £3,779,962.01 -> £3,394,997.60 (10.2%); £3,779,962.18 -> £3,394,997.72 (10.2%); £3,779,962.37 -> £3,394,997.85 (10.2%); £3,779,962.57 -> £3,394,997.98 (10.2%); £3,779,962.80 -> £3,394,998.12 (10.2%); £3,779,963.03 -> £3,394,998.25 (10.2%); £3,779,963.29 -> £3,394,998.38 (10.2%); £3,779,963.57 -> £3,394,998.52 (10.2%); £3,779,963.85 -> £3,394,998.54 (10.2%); £3,779,964.13 -> £3,394,998.56 (10.2%); £3,779,964.41 -> £3,394,998.59 (10.2%); £3,779,964.69 -> £3,394,998.61 (10.2%); £3,779,964.97 -> £3,394,998.64 (10.2%); £3,779,965.25 -> £3,394,998.66 (10.2%); £3,779,965.53 -> £3,394,998.68 (10.2%); £3,779,965.81 -> £3,394,998.71 (10.2%); £3,779,966.08 -> £3,394,998.73 (10.2%); £3,779,966.36 -> £3,394,998.75 (10.2%); £3,779,966.63 -> £3,394,998.78 (10.2%); £3,779,966.91 -> £3,394,998.80 (10.2%); £3,779,967.19 -> £3,394,998.83 (10.2%); £3,779,967.40 -> £3,394,998.96 (10.2%); £3,779,967.61 -> £3,394,999.09 (10.2%); £3,779,967.83 -> £3,394,999.23 (10.2%); £3,779,968.04 -> £3,394,999.37 (10.2%); £3,779,968.25 -> £3,394,999.50 (10.2%); £3,779,968.47 -> £3,394,999.64 (10.2%); £3,779,968.68 -> £3,394,999.77 (10.2%); £3,779,968.96 -> £3,394,999.90 (10.2%); £3,779,969.24 -> £3,395,000.04 (10.2%); £3,779,969.52 -> £3,395,000.17 (10.2%); £3,779,969.80 -> £3,395,000.31 (10.2%); £3,779,970.09 -> £3,395,000.34 (10.2%); £3,779,970.37 -> £3,395,000.37 (10.2%); £3,779,970.64 -> £3,395,000.39 (10.2%); £3,779,970.87 -> £3,395,000.41 (10.2%); £3,779,971.08 -> £3,395,000.43 (10.2%); £3,779,971.26 -> £3,395,000.45 (10.2%); £3,779,971.43 -> £3,395,000.47 (10.2%); £3,779,971.60 -> £3,395,000.48 (10.2%); £3,779,971.77 -> £3,395,000.50 (10.2%); £3,779,971.94 -> £3,395,000.52 (10.2%); £3,779,972.10 -> £3,395,000.53 (10.2%); £3,779,972.27 -> £3,395,000.55 (10.2%); £3,779,972.44 -> £3,395,000.57 (10.2%); £3,779,972.61 -> £3,395,000.58 (10.2%); £3,779,972.78 -> £3,395,000.60 (10.2%); £3,779,972.95 -> £3,395,000.62 (10.2%); £3,779,973.12 -> £3,395,000.76 (10.2%); £3,779,973.30 -> £3,395,000.91 (10.2%); £3,779,973.48 -> £3,395,001.07 (10.2%); £3,779,973.69 -> £3,395,001.23 (10.2%); £3,779,973.91 -> £3,395,001.39 (10.2%); £3,779,974.16 -> £3,395,001.53 (10.2%); £3,779,974.43 -> £3,395,001.68 (10.2%); £3,779,974.71 -> £3,395,001.82 (10.2%); £3,779,974.99 -> £3,395,001.84 (10.2%); £3,779,975.27 -> £3,395,001.87 (10.2%); £3,779,975.55 -> £3,395,001.89 (10.2%); £3,779,975.84 -> £3,395,001.91 (10.2%); £3,779,976.13 -> £3,395,001.94 (10.2%); £3,779,976.42 -> £3,395,001.96 (10.2%); £3,779,976.71 -> £3,395,001.98 (10.2%); £3,779,976.99 -> £3,395,002.01 (10.2%); £3,779,977.27 -> £3,395,002.03 (10.2%); £3,779,977.55 -> £3,395,002.05 (10.2%); £3,779,977.83 -> £3,395,002.08 (10.2%); £3,779,978.11 -> £3,395,002.10 (10.2%); £3,779,978.39 -> £3,395,002.13 (10.2%); £3,779,978.67 -> £3,395,002.28 (10.2%); £3,779,978.89 -> £3,395,002.44 (10.2%); £3,779,979.17 -> £3,395,002.60 (10.2%); £3,779,979.37 -> £3,395,002.76 (10.2%); £3,779,979.58 -> £3,395,002.91 (10.2%); £3,779,979.80 -> £3,395,003.07 (10.2%); £3,779,980.02 -> £3,395,003.23 (10.2%); £3,779,980.29 -> £3,395,003.39 (10.2%); £3,779,980.57 -> £3,395,003.54 (10.2%); £3,779,980.85 -> £3,395,003.70 (10.2%); £3,779,981.13 -> £3,395,003.85 (10.2%); £3,779,981.42 -> £3,395,003.88 (10.2%); £3,779,981.71 -> £3,395,003.90 (10.2%); £3,779,981.96 -> £3,395,003.93 (10.2%); £3,779,982.20 -> £3,395,003.95 (10.2%); £3,779,982.42 -> £3,395,003.97 (10.2%); £3,779,982.58 -> £3,395,003.99 (10.2%); £3,779,982.75 -> £3,395,004.00 (10.2%); £3,779,982.91 -> £3,395,004.02 (10.2%); £3,779,983.08 -> £3,395,004.04 (10.2%); £3,779,983.25 -> £3,395,004.06 (10.2%); £3,779,983.41 -> £3,395,004.07 (10.2%); £3,779,983.58 -> £3,395,004.09 (10.2%); £3,779,983.75 -> £3,395,004.11 (10.2%); £3,779,983.92 -> £3,395,004.12 (10.2%); £3,779,984.09 -> £3,395,004.14 (10.2%); £3,779,984.26 -> £3,395,004.16 (10.2%); £3,779,984.43 -> £3,395,004.32 (10.2%); £3,779,984.60 -> £3,395,004.49 (10.2%); £3,779,984.79 -> £3,395,004.66 (10.2%); £3,779,984.99 -> £3,395,004.84 (10.2%); £3,779,985.21 -> £3,395,005.01 (10.2%); £3,779,985.45 -> £3,395,005.18 (10.2%); £3,779,985.71 -> £3,395,005.35 (10.2%); £3,779,985.99 -> £3,395,005.52 (10.2%); £3,779,986.26 -> £3,395,005.55 (10.2%); £3,779,986.55 -> £3,395,005.57 (10.2%); £3,779,986.82 -> £3,395,005.60 (10.2%); £3,779,987.10 -> £3,395,005.62 (10.2%); £3,779,987.38 -> £3,395,005.64 (10.2%); £3,779,987.65 -> £3,395,005.67 (10.2%); £3,779,987.93 -> £3,395,005.69 (10.2%); £3,779,988.21 -> £3,395,005.71 (10.2%); £3,779,988.49 -> £3,395,005.73 (10.2%); £3,779,988.76 -> £3,395,005.76 (10.2%); £3,779,989.04 -> £3,395,005.78 (10.2%); £3,779,989.32 -> £3,395,005.81 (10.2%); £3,779,989.60 -> £3,395,005.83 (10.2%); £3,779,989.80 -> £3,395,006.01 (10.2%); £3,779,990.08 -> £3,395,006.19 (10.2%); £3,779,990.36 -> £3,395,006.36 (10.2%); £3,779,990.56 -> £3,395,006.54 (10.2%); £3,779,990.83 -> £3,395,006.72 (10.2%); £3,779,991.11 -> £3,395,006.88 (10.2%); £3,779,991.32 -> £3,395,007.05 (10.2%); £3,779,991.61 -> £3,395,007.22 (10.2%); £3,779,991.88 -> £3,395,007.39 (10.2%); £3,779,992.16 -> £3,395,007.56 (10.2%); £3,779,992.44 -> £3,395,007.73 (10.2%); £3,779,992.73 -> £3,395,007.76 (10.2%); £3,779,993.00 -> £3,395,007.78 (10.2%); £3,779,993.25 -> £3,395,007.81 (10.2%); £3,779,993.49 -> £3,395,007.83 (10.2%); £3,779,993.71 -> £3,395,007.85 (10.2%); £3,779,993.87 -> £3,395,007.87 (10.2%); £3,779,994.03 -> £3,395,007.89 (10.2%); £3,779,994.19 -> £3,395,007.90 (10.2%); £3,779,994.35 -> £3,395,007.92 (10.2%); £3,779,994.51 -> £3,395,007.94 (10.2%); £3,779,994.67 -> £3,395,007.95 (10.2%); £3,779,994.84 -> £3,395,007.97 (10.2%); £3,779,994.99 -> £3,395,007.99 (10.2%); £3,779,995.16 -> £3,395,008.00 (10.2%); £3,779,995.33 -> £3,395,008.02 (10.2%); £3,779,995.49 -> £3,395,008.04 (10.2%); £3,779,995.65 -> £3,395,008.22 (10.2%); £3,779,995.81 -> £3,395,008.40 (10.2%); £3,779,995.99 -> £3,395,008.59 (10.2%); £3,779,996.18 -> £3,395,008.78 (10.2%); £3,779,996.39 -> £3,395,008.97 (10.2%); £3,779,996.63 -> £3,395,009.16 (10.2%); £3,779,996.89 -> £3,395,009.34 (10.2%); £3,779,997.16 -> £3,395,009.52 (10.2%); £3,779,997.44 -> £3,395,009.55 (10.2%); £3,779,997.70 -> £3,395,009.57 (10.2%); £3,779,997.97 -> £3,395,009.59 (10.2%); £3,779,998.24 -> £3,395,009.62 (10.2%); £3,779,998.51 -> £3,395,009.64 (10.2%); £3,779,998.78 -> £3,395,009.67 (10.2%); £3,779,999.05 -> £3,395,009.69 (10.2%); £3,779,999.32 -> £3,395,009.71 (10.2%); £3,779,999.58 -> £3,395,009.74 (10.2%); £3,779,999.85 -> £3,395,009.76 (10.2%); £3,780,000.12 -> £3,395,009.78 (10.2%); £3,780,000.38 -> £3,395,009.81 (10.2%); £3,780,000.66 -> £3,395,009.84 (10.2%); £3,780,000.85 -> £3,395,010.02 (10.2%); £3,780,001.06 -> £3,395,010.20 (10.2%); £3,780,001.26 -> £3,395,010.39 (10.2%); £3,780,001.47 -> £3,395,010.59 (10.2%); £3,780,001.73 -> £3,395,010.77 (10.2%); £3,780,001.93 -> £3,395,010.96 (10.2%); £3,780,002.14 -> £3,395,011.14 (10.2%); £3,780,002.40 -> £3,395,011.33 (10.2%); £3,780,002.67 -> £3,395,011.51 (10.2%); £3,780,002.94 -> £3,395,011.70 (10.2%); £3,780,003.21 -> £3,395,011.89 (10.2%); £3,780,003.47 -> £3,395,011.92 (10.2%); £3,780,003.74 -> £3,395,011.94 (10.2%); £3,780,004.00 -> £3,395,011.97 (10.2%); £3,780,004.22 -> £3,395,011.99 (10.2%); £3,780,004.43 -> £3,395,012.01 (10.2%); £3,780,004.58 -> £3,395,012.03 (10.2%); £3,780,004.72 -> £3,395,012.05 (10.2%); £3,780,004.87 -> £3,395,012.07 (10.2%); £3,780,005.02 -> £3,395,012.08 (10.2%); £3,780,005.16 -> £3,395,012.10 (10.2%); £3,780,005.30 -> £3,395,012.12 (10.2%); £3,780,005.44 -> £3,395,012.13 (10.2%); £3,780,005.58 -> £3,395,012.15 (10.2%); £3,780,005.72 -> £3,395,012.17 (10.2%); £3,780,005.86 -> £3,395,012.18 (10.2%); £3,780,005.99 -> £3,395,012.20 (10.2%); £3,780,006.14 -> £3,395,012.42 (10.2%); £3,780,006.28 -> £3,395,012.64 (10.2%); £3,780,006.43 -> £3,395,012.87 (10.2%); £3,780,006.61 -> £3,395,013.10 (10.2%); £3,780,006.80 -> £3,395,013.33 (10.2%); £3,780,007.00 -> £3,395,013.56 (10.2%); £3,780,007.22 -> £3,395,013.79 (10.2%); £3,780,007.46 -> £3,395,014.03 (10.2%); £3,780,007.69 -> £3,395,014.05 (10.2%); £3,780,007.92 -> £3,395,014.08 (10.2%); £3,780,008.16 -> £3,395,014.10 (10.2%); £3,780,008.40 -> £3,395,014.13 (10.2%); £3,780,008.63 -> £3,395,014.16 (10.2%); £3,780,008.87 -> £3,395,014.18 (10.2%); £3,780,009.10 -> £3,395,014.21 (10.2%); £3,780,009.34 -> £3,395,014.24 (10.2%); £3,780,009.59 -> £3,395,014.26 (10.2%); £3,780,009.82 -> £3,395,014.28 (10.2%); £3,780,010.07 -> £3,395,014.31 (10.2%); £3,780,010.30 -> £3,395,014.33 (10.2%); £3,780,010.54 -> £3,395,014.36 (10.2%); £3,780,010.77 -> £3,395,014.58 (10.2%); £3,780,010.94 -> £3,395,014.80 (10.2%); £3,780,011.12 -> £3,395,015.02 (10.2%); £3,780,011.29 -> £3,395,015.24 (10.2%); £3,780,011.47 -> £3,395,015.46 (10.2%); £3,780,011.64 -> £3,395,015.68 (10.2%); £3,780,011.83 -> £3,395,015.91 (10.2%); £3,780,012.06 -> £3,395,016.14 (10.2%); £3,780,012.29 -> £3,395,016.37 (10.2%); £3,780,012.52 -> £3,395,016.59 (10.2%); £3,780,012.76 -> £3,395,016.81 (10.2%); £3,780,012.99 -> £3,395,016.84 (10.2%); £3,780,013.22 -> £3,395,016.86 (10.2%); £3,780,013.44 -> £3,395,016.89 (10.2%); £3,780,013.64 -> £3,395,016.91 (10.2%); £3,780,013.82 -> £3,395,016.94 (10.2%); £3,780,013.96 -> £3,395,016.96 (10.2%); £3,780,014.10 -> £3,395,016.97 (10.2%); £3,780,014.24 -> £3,395,016.99 (10.2%); £3,780,014.38 -> £3,395,017.01 (10.2%); £3,780,014.52 -> £3,395,017.03 (10.2%); £3,780,014.66 -> £3,395,017.04 (10.2%); £3,780,014.80 -> £3,395,017.06 (10.2%); £3,780,014.94 -> £3,395,017.08 (10.2%); £3,780,015.08 -> £3,395,017.09 (10.2%); £3,780,015.22 -> £3,395,017.11 (10.2%); £3,780,015.36 -> £3,395,017.13 (10.2%); £3,780,015.50 -> £3,395,017.34 (10.2%); £3,780,015.63 -> £3,395,017.56 (10.2%); £3,780,015.79 -> £3,395,017.78 (10.2%); £3,780,015.96 -> £3,395,017.99 (10.2%); £3,780,016.15 -> £3,395,018.21 (10.2%); £3,780,016.36 -> £3,395,018.43 (10.2%); £3,780,016.58 -> £3,395,018.65 (10.2%); £3,780,016.81 -> £3,395,018.87 (10.2%); £3,780,017.05 -> £3,395,018.90 (10.2%); £3,780,017.28 -> £3,395,018.93 (10.2%); £3,780,017.51 -> £3,395,018.96 (10.2%); £3,780,017.74 -> £3,395,018.99 (10.2%); £3,780,017.97 -> £3,395,019.02 (10.2%); £3,780,018.20 -> £3,395,019.05 (10.2%); £3,780,018.42 -> £3,395,019.08 (10.2%); £3,780,018.66 -> £3,395,019.11 (10.2%); £3,780,018.89 -> £3,395,019.14 (10.2%); £3,780,019.13 -> £3,395,019.16 (10.2%); £3,780,019.36 -> £3,395,019.19 (10.2%); £3,780,019.59 -> £3,395,019.22 (10.2%); £3,780,019.82 -> £3,395,019.25 (10.2%); £3,780,019.99 -> £3,395,019.46 (10.2%); £3,780,020.17 -> £3,395,019.68 (10.2%); £3,780,020.34 -> £3,395,019.89 (10.2%); £3,780,020.51 -> £3,395,020.12 (10.2%); £3,780,020.74 -> £3,395,020.34 (10.2%); £3,780,020.92 -> £3,395,020.56 (10.2%); £3,780,021.10 -> £3,395,020.78 (10.2%); £3,780,021.34 -> £3,395,021.01 (10.2%); £3,780,021.57 -> £3,395,021.23 (10.2%); £3,780,021.81 -> £3,395,021.45 (10.2%); £3,780,022.04 -> £3,395,021.67 (10.2%); £3,780,022.26 -> £3,395,021.69 (10.2%); £3,780,022.50 -> £3,395,021.72 (10.2%); £3,780,022.71 -> £3,395,021.75 (10.2%); £3,780,022.91 -> £3,395,021.77 (10.2%); £3,780,023.09 -> £3,395,021.79 (10.2%); £3,780,023.25 -> £3,395,021.81 (10.2%); £3,780,023.41 -> £3,395,021.83 (10.2%); £3,780,023.55 -> £3,395,021.84 (10.2%); £3,780,023.71 -> £3,395,021.86 (10.2%); £3,780,023.86 -> £3,395,021.88 (10.2%); £3,780,024.02 -> £3,395,021.89 (10.2%); £3,780,024.17 -> £3,395,021.91 (10.2%); £3,780,024.32 -> £3,395,021.93 (10.2%); £3,780,024.48 -> £3,395,021.94 (10.2%); £3,780,024.63 -> £3,395,021.96 (10.2%); £3,780,024.79 -> £3,395,021.98 (10.2%); £3,780,024.94 -> £3,395,022.18 (10.2%); £3,780,025.10 -> £3,395,022.39 (10.2%); £3,780,025.27 -> £3,395,022.60 (10.2%); £3,780,025.45 -> £3,395,022.81 (10.2%); £3,780,025.66 -> £3,395,023.03 (10.2%); £3,780,025.88 -> £3,395,023.25 (10.2%); £3,780,026.11 -> £3,395,023.47 (10.2%); £3,780,026.36 -> £3,395,023.69 (10.2%); £3,780,026.61 -> £3,395,023.71 (10.2%); £3,780,026.86 -> £3,395,023.73 (10.2%); £3,780,027.13 -> £3,395,023.76 (10.2%); £3,780,027.37 -> £3,395,023.78 (10.2%); £3,780,027.63 -> £3,395,023.80 (10.2%); £3,780,027.89 -> £3,395,023.83 (10.2%); £3,780,028.15 -> £3,395,023.85 (10.2%); £3,780,028.41 -> £3,395,023.87 (10.2%); £3,780,028.67 -> £3,395,023.90 (10.2%); £3,780,028.92 -> £3,395,023.92 (10.2%); £3,780,029.18 -> £3,395,023.94 (10.2%); £3,780,029.44 -> £3,395,023.97 (10.2%); £3,780,029.70 -> £3,395,024.00 (10.2%); £3,780,029.96 -> £3,395,024.21 (10.2%); £3,780,030.22 -> £3,395,024.43 (10.2%); £3,780,030.48 -> £3,395,024.66 (10.2%); £3,780,030.72 -> £3,395,024.88 (10.2%); £3,780,030.97 -> £3,395,025.10 (10.2%); £3,780,031.23 -> £3,395,025.32 (10.2%); £3,780,031.42 -> £3,395,025.54 (10.2%); £3,780,031.67 -> £3,395,025.76 (10.2%); £3,780,031.92 -> £3,395,025.97 (10.2%); £3,780,032.17 -> £3,395,026.19 (10.2%); £3,780,032.43 -> £3,395,026.40 (10.2%); £3,780,032.68 -> £3,395,026.43 (10.2%); £3,780,032.94 -> £3,395,026.46 (10.2%); £3,780,033.17 -> £3,395,026.48 (10.2%); £3,780,033.39 -> £3,395,026.51 (10.2%); £3,780,033.59 -> £3,395,026.53 (10.2%); £3,780,033.74 -> £3,395,026.54 (10.2%); £3,780,033.89 -> £3,395,026.56 (10.2%); £3,780,034.05 -> £3,395,026.58 (10.2%); £3,780,034.20 -> £3,395,026.60 (10.2%); £3,780,034.35 -> £3,395,026.61 (10.2%); £3,780,034.51 -> £3,395,026.63 (10.2%); £3,780,034.66 -> £3,395,026.65 (10.2%); £3,780,034.81 -> £3,395,026.66 (10.2%); £3,780,034.97 -> £3,395,026.68 (10.2%); £3,780,035.12 -> £3,395,026.70 (10.2%); £3,780,035.27 -> £3,395,026.71 (10.2%); £3,780,035.43 -> £3,395,026.92 (10.2%); £3,780,035.58 -> £3,395,027.12 (10.2%); £3,780,035.74 -> £3,395,027.33 (10.2%); £3,780,035.92 -> £3,395,027.55 (10.2%); £3,780,036.12 -> £3,395,027.76 (10.2%); £3,780,036.35 -> £3,395,027.97 (10.2%); £3,780,036.58 -> £3,395,028.18 (10.2%); £3,780,036.83 -> £3,395,028.39 (10.2%); £3,780,037.08 -> £3,395,028.42 (10.2%); £3,780,037.33 -> £3,395,028.44 (10.2%); £3,780,037.59 -> £3,395,028.46 (10.2%); £3,780,037.84 -> £3,395,028.49 (10.2%); £3,780,038.10 -> £3,395,028.51 (10.2%); £3,780,038.36 -> £3,395,028.54 (10.2%); £3,780,038.61 -> £3,395,028.56 (10.2%); £3,780,038.88 -> £3,395,028.58 (10.2%); £3,780,039.13 -> £3,395,028.61 (10.2%); £3,780,039.39 -> £3,395,028.63 (10.2%); £3,780,039.64 -> £3,395,028.65 (10.2%); £3,780,039.89 -> £3,395,028.68 (10.2%); £3,780,040.14 -> £3,395,028.71 (10.2%); £3,780,040.33 -> £3,395,028.91 (10.2%); £3,780,040.52 -> £3,395,029.12 (10.2%); £3,780,040.76 -> £3,395,029.33 (10.2%); £3,780,040.95 -> £3,395,029.54 (10.2%); £3,780,041.15 -> £3,395,029.75 (10.2%); £3,780,041.41 -> £3,395,029.97 (10.2%); £3,780,041.66 -> £3,395,030.18 (10.2%); £3,780,041.91 -> £3,395,030.39 (10.2%); £3,780,042.17 -> £3,395,030.60 (10.2%); £3,780,042.43 -> £3,395,030.81 (10.2%); £3,780,042.69 -> £3,395,031.02 (10.2%); £3,780,042.94 -> £3,395,031.05 (10.2%); £3,780,043.19 -> £3,395,031.08 (10.2%); £3,780,043.42 -> £3,395,031.10 (10.2%); £3,780,043.63 -> £3,395,031.12 (10.2%); £3,780,043.83 -> £3,395,031.14 (10.2%); £3,780,043.99 -> £3,395,031.16 (10.2%); £3,780,044.14 -> £3,395,031.18 (10.2%); £3,780,044.29 -> £3,395,031.20 (10.2%); £3,780,044.44 -> £3,395,031.21 (10.2%); £3,780,044.59 -> £3,395,031.23 (10.2%); £3,780,044.75 -> £3,395,031.25 (10.2%); £3,780,044.89 -> £3,395,031.26 (10.2%); £3,780,045.05 -> £3,395,031.28 (10.2%); £3,780,045.20 -> £3,395,031.30 (10.2%); £3,780,045.35 -> £3,395,031.31 (10.2%); £3,780,045.50 -> £3,395,031.33 (10.2%); £3,780,045.65 -> £3,395,031.51 (10.2%); £3,780,045.80 -> £3,395,031.68 (10.2%); £3,780,045.97 -> £3,395,031.86 (10.2%); £3,780,046.15 -> £3,395,032.04 (10.2%); £3,780,046.35 -> £3,395,032.21 (10.2%); £3,780,046.57 -> £3,395,032.39 (10.2%); £3,780,046.82 -> £3,395,032.57 (10.2%); £3,780,047.06 -> £3,395,032.75 (10.2%); £3,780,047.31 -> £3,395,032.77 (10.2%); £3,780,047.56 -> £3,395,032.79 (10.2%); £3,780,047.82 -> £3,395,032.82 (10.2%); £3,780,048.07 -> £3,395,032.84 (10.2%); £3,780,048.32 -> £3,395,032.86 (10.2%); £3,780,048.57 -> £3,395,032.89 (10.2%); £3,780,048.84 -> £3,395,032.91 (10.2%); £3,780,049.09 -> £3,395,032.93 (10.2%); £3,780,049.34 -> £3,395,032.96 (10.2%); £3,780,049.60 -> £3,395,032.98 (10.2%); £3,780,049.85 -> £3,395,033.00 (10.2%); £3,780,050.10 -> £3,395,033.03 (10.2%); £3,780,050.34 -> £3,395,033.06 (10.2%); £3,780,050.59 -> £3,395,033.23 (10.2%); £3,780,050.78 -> £3,395,033.43 (10.2%); £3,780,051.03 -> £3,395,033.62 (10.2%); £3,780,051.29 -> £3,395,033.81 (10.2%); £3,780,051.48 -> £3,395,034.00 (10.2%); £3,780,051.73 -> £3,395,034.19 (10.2%); £3,780,051.91 -> £3,395,034.37 (10.2%); £3,780,052.16 -> £3,395,034.56 (10.2%); £3,780,052.41 -> £3,395,034.75 (10.2%); £3,780,052.67 -> £3,395,034.94 (10.2%); £3,780,052.91 -> £3,395,035.12 (10.2%); £3,780,053.16 -> £3,395,035.15 (10.2%); £3,780,053.41 -> £3,395,035.18 (10.2%); £3,780,053.65 -> £3,395,035.20 (10.2%); £3,780,053.86 -> £3,395,035.23 (10.2%); £3,780,054.05 -> £3,395,035.25 (10.2%); £3,780,054.21 -> £3,395,035.26 (10.2%); £3,780,054.36 -> £3,395,035.28 (10.2%); £3,780,054.50 -> £3,395,035.30 (10.2%); £3,780,054.65 -> £3,395,035.32 (10.2%); £3,780,054.80 -> £3,395,035.33 (10.2%); £3,780,054.96 -> £3,395,035.35 (10.2%); £3,780,055.11 -> £3,395,035.37 (10.2%); £3,780,055.26 -> £3,395,035.38 (10.2%); £3,780,055.41 -> £3,395,035.40 (10.2%); £3,780,055.55 -> £3,395,035.42 (10.2%); £3,780,055.70 -> £3,395,035.43 (10.2%); £3,780,055.85 -> £3,395,035.60 (10.2%); £3,780,056.00 -> £3,395,035.76 (10.2%); £3,780,056.17 -> £3,395,035.91 (10.2%); £3,780,056.35 -> £3,395,036.08 (10.2%); £3,780,056.55 -> £3,395,036.24 (10.2%); £3,780,056.76 -> £3,395,036.41 (10.2%); £3,780,056.98 -> £3,395,036.57 (10.2%); £3,780,057.24 -> £3,395,036.73 (10.2%); £3,780,057.49 -> £3,395,036.75 (10.2%); £3,780,057.74 -> £3,395,036.78 (10.2%); £3,780,057.99 -> £3,395,036.80 (10.2%); £3,780,058.25 -> £3,395,036.82 (10.2%); £3,780,058.49 -> £3,395,036.85 (10.2%); £3,780,058.74 -> £3,395,036.87 (10.2%); £3,780,058.98 -> £3,395,036.90 (10.2%); £3,780,059.22 -> £3,395,036.92 (10.2%); £3,780,059.47 -> £3,395,036.94 (10.2%); £3,780,059.72 -> £3,395,036.96 (10.2%); £3,780,059.97 -> £3,395,036.99 (10.2%); £3,780,060.22 -> £3,395,037.01 (10.2%); £3,780,060.47 -> £3,395,037.04 (10.2%); £3,780,060.66 -> £3,395,037.21 (10.2%); £3,780,060.84 -> £3,395,037.38 (10.2%); £3,780,061.03 -> £3,395,037.55 (10.2%); £3,780,061.21 -> £3,395,037.72 (10.2%); £3,780,061.40 -> £3,395,037.89 (10.2%); £3,780,061.58 -> £3,395,038.07 (10.2%); £3,780,061.76 -> £3,395,038.24 (10.2%); £3,780,062.01 -> £3,395,038.41 (10.2%); £3,780,062.26 -> £3,395,038.58 (10.2%); £3,780,062.51 -> £3,395,038.75 (10.2%); £3,780,062.76 -> £3,395,038.91 (10.2%); £3,780,063.01 -> £3,395,038.94 (10.2%); £3,780,063.26 -> £3,395,038.97 (10.2%); £3,780,063.49 -> £3,395,038.99 (10.2%); £3,780,063.70 -> £3,395,039.02 (10.2%); £3,780,063.89 -> £3,395,039.04 (10.2%); £3,780,064.04 -> £3,395,039.05 (10.2%); £3,780,064.19 -> £3,395,039.07 (10.2%); £3,780,064.34 -> £3,395,039.09 (10.2%); £3,780,064.48 -> £3,395,039.11 (10.2%); £3,780,064.63 -> £3,395,039.12 (10.2%); £3,780,064.77 -> £3,395,039.14 (10.2%); £3,780,064.92 -> £3,395,039.16 (10.2%); £3,780,065.07 -> £3,395,039.17 (10.2%); £3,780,065.22 -> £3,395,039.19 (10.2%); £3,780,065.37 -> £3,395,039.21 (10.2%); £3,780,065.52 -> £3,395,039.22 (10.2%); £3,780,065.66 -> £3,395,039.40 (10.2%); £3,780,065.82 -> £3,395,039.58 (10.2%); £3,780,065.98 -> £3,395,039.77 (10.2%); £3,780,066.16 -> £3,395,039.95 (10.2%); £3,780,066.36 -> £3,395,040.14 (10.2%); £3,780,066.57 -> £3,395,040.32 (10.2%); £3,780,066.80 -> £3,395,040.50 (10.2%); £3,780,067.04 -> £3,395,040.68 (10.2%); £3,780,067.28 -> £3,395,040.70 (10.2%); £3,780,067.52 -> £3,395,040.72 (10.2%); £3,780,067.77 -> £3,395,040.75 (10.2%); £3,780,068.01 -> £3,395,040.77 (10.2%); £3,780,068.26 -> £3,395,040.79 (10.2%); £3,780,068.51 -> £3,395,040.82 (10.2%); £3,780,068.75 -> £3,395,040.84 (10.2%); £3,780,069.00 -> £3,395,040.86 (10.2%); £3,780,069.24 -> £3,395,040.89 (10.2%); £3,780,069.47 -> £3,395,040.91 (10.2%); £3,780,069.73 -> £3,395,040.93 (10.2%); £3,780,069.97 -> £3,395,040.96 (10.2%); £3,780,070.21 -> £3,395,040.99 (10.2%); £3,780,070.40 -> £3,395,041.17 (10.2%); £3,780,070.58 -> £3,395,041.35 (10.2%); £3,780,070.76 -> £3,395,041.54 (10.2%); £3,780,070.95 -> £3,395,041.73 (10.2%); £3,780,071.13 -> £3,395,041.92 (10.2%); £3,780,071.31 -> £3,395,042.11 (10.2%); £3,780,071.50 -> £3,395,042.30 (10.2%); £3,780,071.74 -> £3,395,042.48 (10.2%); £3,780,071.98 -> £3,395,042.67 (10.2%); £3,780,072.23 -> £3,395,042.86 (10.2%); £3,780,072.47 -> £3,395,043.05 (10.2%); £3,780,072.73 -> £3,395,043.07 (10.2%); £3,780,072.98 -> £3,395,043.10 (10.2%); £3,780,073.21 -> £3,395,043.13 (10.2%); £3,780,073.42 -> £3,395,043.15 (10.2%); £3,780,073.61 -> £3,395,043.17 (10.2%); £3,780,073.74 -> £3,395,043.19 (10.2%); £3,780,073.87 -> £3,395,043.21 (10.2%); £3,780,074.00 -> £3,395,043.22 (10.2%); £3,780,074.13 -> £3,395,043.24 (10.2%); £3,780,074.26 -> £3,395,043.26 (10.2%); £3,780,074.39 -> £3,395,043.27 (10.2%); £3,780,074.52 -> £3,395,043.29 (10.2%); £3,780,074.65 -> £3,395,043.31 (10.2%); £3,780,074.77 -> £3,395,043.32 (10.2%); £3,780,074.90 -> £3,395,043.34 (10.2%); £3,780,075.03 -> £3,395,043.36 (10.2%); £3,780,075.16 -> £3,395,043.53 (10.2%); £3,780,075.28 -> £3,395,043.70 (10.2%); £3,780,075.42 -> £3,395,043.88 (10.2%); £3,780,075.58 -> £3,395,044.05 (10.2%); £3,780,075.76 -> £3,395,044.23 (10.2%); £3,780,075.94 -> £3,395,044.40 (10.2%); £3,780,076.14 -> £3,395,044.58 (10.2%); £3,780,076.35 -> £3,395,044.76 (10.2%); £3,780,076.56 -> £3,395,044.78 (10.2%); £3,780,076.76 -> £3,395,044.81 (10.2%); £3,780,076.98 -> £3,395,044.84 (10.2%); £3,780,077.19 -> £3,395,044.86 (10.2%); £3,780,077.40 -> £3,395,044.89 (10.2%); £3,780,077.62 -> £3,395,044.92 (10.2%); £3,780,077.83 -> £3,395,044.94 (10.2%); £3,780,078.04 -> £3,395,044.97 (10.2%); £3,780,078.25 -> £3,395,044.99 (10.2%); £3,780,078.46 -> £3,395,045.02 (10.2%); £3,780,078.68 -> £3,395,045.04 (10.2%); £3,780,078.89 -> £3,395,045.07 (10.2%); £3,780,079.11 -> £3,395,045.10 (10.2%); £3,780,079.26 -> £3,395,045.27 (10.2%); £3,780,079.43 -> £3,395,045.44 (10.2%); £3,780,079.59 -> £3,395,045.62 (10.2%); £3,780,079.75 -> £3,395,045.80 (10.2%); £3,780,079.91 -> £3,395,045.99 (10.2%); £3,780,080.06 -> £3,395,046.17 (10.2%); £3,780,080.27 -> £3,395,046.36 (10.2%); £3,780,080.49 -> £3,395,046.53 (10.2%); £3,780,080.70 -> £3,395,046.72 (10.2%); £3,780,080.92 -> £3,395,046.90 (10.2%); £3,780,081.12 -> £3,395,047.07 (10.2%); £3,780,081.34 -> £3,395,047.10 (10.2%); £3,780,081.55 -> £3,395,047.13 (10.2%); £3,780,081.75 -> £3,395,047.15 (10.2%); £3,780,081.93 -> £3,395,047.18 (10.2%); £3,780,082.09 -> £3,395,047.20 (10.2%); £3,780,082.21 -> £3,395,047.22 (10.2%); £3,780,082.34 -> £3,395,047.24 (10.2%); £3,780,082.47 -> £3,395,047.26 (10.2%); £3,780,082.59 -> £3,395,047.28 (10.2%); £3,780,082.72 -> £3,395,047.29 (10.2%); £3,780,082.85 -> £3,395,047.31 (10.2%); £3,780,082.97 -> £3,395,047.33 (10.2%); £3,780,083.10 -> £3,395,047.34 (10.2%); £3,780,083.23 -> £3,395,047.36 (10.2%); £3,780,083.35 -> £3,395,047.38 (10.2%); £3,780,083.48 -> £3,395,047.39 (10.2%); £3,780,083.60 -> £3,395,047.60 (10.2%); £3,780,083.73 -> £3,395,047.82 (10.2%); £3,780,083.87 -> £3,395,048.03 (10.2%); £3,780,084.03 -> £3,395,048.25 (10.2%); £3,780,084.20 -> £3,395,048.46 (10.2%); £3,780,084.39 -> £3,395,048.68 (10.2%); £3,780,084.58 -> £3,395,048.90 (10.2%); £3,780,084.79 -> £3,395,049.12 (10.2%); £3,780,085.00 -> £3,395,049.15 (10.2%); £3,780,085.21 -> £3,395,049.18 (10.2%); £3,780,085.42 -> £3,395,049.21 (10.2%); £3,780,085.63 -> £3,395,049.24 (10.2%); £3,780,085.85 -> £3,395,049.27 (10.2%); £3,780,086.06 -> £3,395,049.30 (10.2%); £3,780,086.27 -> £3,395,049.33 (10.2%); £3,780,086.48 -> £3,395,049.36 (10.2%); £3,780,086.69 -> £3,395,049.39 (10.2%); £3,780,086.90 -> £3,395,049.42 (10.2%); £3,780,087.11 -> £3,395,049.45 (10.2%); £3,780,087.32 -> £3,395,049.47 (10.2%); £3,780,087.53 -> £3,395,049.50 (10.2%); £3,780,087.69 -> £3,395,049.71 (10.2%); £3,780,087.85 -> £3,395,049.93 (10.2%); £3,780,088.01 -> £3,395,050.15 (10.2%); £3,780,088.17 -> £3,395,050.37 (10.2%); £3,780,088.33 -> £3,395,050.59 (10.2%); £3,780,088.49 -> £3,395,050.80 (10.2%); £3,780,088.65 -> £3,395,051.02 (10.2%); £3,780,088.87 -> £3,395,051.23 (10.2%); £3,780,089.09 -> £3,395,051.45 (10.2%); £3,780,089.29 -> £3,395,051.67 (10.2%); £3,780,089.50 -> £3,395,051.89 (10.2%); £3,780,089.71 -> £3,395,051.92 (10.2%); £3,780,089.92 -> £3,395,051.95 (10.2%); £3,780,090.12 -> £3,395,051.97 (10.2%); £3,780,090.30 -> £3,395,052.00 (10.2%); £3,780,090.47 -> £3,395,052.01 (10.2%); £3,780,090.61 -> £3,395,052.03 (10.2%); £3,780,090.76 -> £3,395,052.05 (10.2%); £3,780,090.91 -> £3,395,052.07 (10.2%); £3,780,091.06 -> £3,395,052.09 (10.2%); £3,780,091.20 -> £3,395,052.10 (10.2%); £3,780,091.35 -> £3,395,052.12 (10.2%); £3,780,091.49 -> £3,395,052.14 (10.2%); £3,780,091.64 -> £3,395,052.15 (10.2%); £3,780,091.78 -> £3,395,052.17 (10.2%); £3,780,091.93 -> £3,395,052.19 (10.2%); £3,780,092.07 -> £3,395,052.20 (10.2%); £3,780,092.21 -> £3,395,052.45 (10.2%); £3,780,092.36 -> £3,395,052.70 (10.2%); £3,780,092.52 -> £3,395,052.95 (10.2%); £3,780,092.69 -> £3,395,053.21 (10.2%); £3,780,092.88 -> £3,395,053.46 (10.2%); £3,780,093.09 -> £3,395,053.72 (10.2%); £3,780,093.31 -> £3,395,053.97 (10.2%); £3,780,093.55 -> £3,395,054.22 (10.2%); £3,780,093.79 -> £3,395,054.24 (10.2%); £3,780,094.03 -> £3,395,054.27 (10.2%); £3,780,094.28 -> £3,395,054.29 (10.2%); £3,780,094.52 -> £3,395,054.31 (10.2%); £3,780,094.77 -> £3,395,054.34 (10.2%); £3,780,095.01 -> £3,395,054.36 (10.2%); £3,780,095.25 -> £3,395,054.39 (10.2%); £3,780,095.49 -> £3,395,054.41 (10.2%); £3,780,095.73 -> £3,395,054.43 (10.2%); £3,780,095.98 -> £3,395,054.46 (10.2%); £3,780,096.22 -> £3,395,054.48 (10.2%); £3,780,096.46 -> £3,395,054.51 (10.2%); £3,780,096.70 -> £3,395,054.53 (10.2%); £3,780,096.89 -> £3,395,054.78 (10.2%); £3,780,097.07 -> £3,395,055.03 (10.2%); £3,780,097.26 -> £3,395,055.27 (10.2%); £3,780,097.44 -> £3,395,055.52 (10.2%); £3,780,097.62 -> £3,395,055.77 (10.2%); £3,780,097.80 -> £3,395,056.02 (10.2%); £3,780,097.97 -> £3,395,056.28 (10.2%); £3,780,098.21 -> £3,395,056.53 (10.2%); £3,780,098.45 -> £3,395,056.78 (10.2%); £3,780,098.69 -> £3,395,057.04 (10.2%); £3,780,098.93 -> £3,395,057.30 (10.2%); £3,780,099.18 -> £3,395,057.32 (10.2%); £3,780,099.42 -> £3,395,057.35 (10.2%); £3,780,099.64 -> £3,395,057.38 (10.2%); £3,780,099.85 -> £3,395,057.40 (10.2%); £3,780,100.04 -> £3,395,057.42 (10.2%); £3,780,100.18 -> £3,395,057.44 (10.2%); £3,780,100.32 -> £3,395,057.45 (10.2%); £3,780,100.47 -> £3,395,057.47 (10.2%); £3,780,100.61 -> £3,395,057.49 (10.2%); £3,780,100.75 -> £3,395,057.50 (10.2%); £3,780,100.89 -> £3,395,057.52 (10.2%); £3,780,101.03 -> £3,395,057.54 (10.2%); £3,780,101.17 -> £3,395,057.55 (10.2%); £3,780,101.32 -> £3,395,057.57 (10.2%); £3,780,101.46 -> £3,395,057.59 (10.2%); £3,780,101.60 -> £3,395,057.61 (10.2%); £3,780,101.75 -> £3,395,057.83 (10.2%); £3,780,101.90 -> £3,395,058.05 (10.2%); £3,780,102.06 -> £3,395,058.27 (10.2%); £3,780,102.23 -> £3,395,058.50 (10.2%); £3,780,102.42 -> £3,395,058.72 (10.2%); £3,780,102.64 -> £3,395,058.94 (10.2%); £3,780,102.86 -> £3,395,059.16 (10.2%); £3,780,103.11 -> £3,395,059.38 (10.2%); £3,780,103.35 -> £3,395,059.41 (10.2%); £3,780,103.58 -> £3,395,059.43 (10.2%); £3,780,103.82 -> £3,395,059.45 (10.2%); £3,780,104.05 -> £3,395,059.48 (10.2%); £3,780,104.29 -> £3,395,059.50 (10.2%); £3,780,104.53 -> £3,395,059.53 (10.2%); £3,780,104.77 -> £3,395,059.55 (10.2%); £3,780,105.00 -> £3,395,059.57 (10.2%); £3,780,105.24 -> £3,395,059.60 (10.2%); £3,780,105.47 -> £3,395,059.62 (10.2%); £3,780,105.71 -> £3,395,059.64 (10.2%); £3,780,105.94 -> £3,395,059.67 (10.2%); £3,780,106.18 -> £3,395,059.70 (10.2%); £3,780,106.37 -> £3,395,059.92 (10.2%); £3,780,106.55 -> £3,395,060.15 (10.2%); £3,780,106.74 -> £3,395,060.39 (10.2%); £3,780,106.99 -> £3,395,060.63 (10.2%); £3,780,107.23 -> £3,395,060.86 (10.2%); £3,780,107.48 -> £3,395,061.10 (10.2%); £3,780,107.66 -> £3,395,061.33 (10.2%); £3,780,107.90 -> £3,395,061.56 (10.2%); £3,780,108.14 -> £3,395,061.78 (10.2%); £3,780,108.38 -> £3,395,062.00 (10.2%); £3,780,108.62 -> £3,395,062.22 (10.2%); £3,780,108.87 -> £3,395,062.25 (10.2%); £3,780,109.11 -> £3,395,062.28 (10.2%); £3,780,109.33 -> £3,395,062.30 (10.2%); £3,780,109.53 -> £3,395,062.33 (10.2%); £3,780,109.71 -> £3,395,062.35 (10.2%); £3,780,109.85 -> £3,395,062.36 (10.2%); £3,780,109.99 -> £3,395,062.38 (10.2%); £3,780,110.13 -> £3,395,062.40 (10.2%); £3,780,110.27 -> £3,395,062.42 (10.2%); £3,780,110.41 -> £3,395,062.43 (10.2%); £3,780,110.56 -> £3,395,062.45 (10.2%); £3,780,110.70 -> £3,395,062.47 (10.2%); £3,780,110.84 -> £3,395,062.48 (10.2%); £3,780,110.98 -> £3,395,062.50 (10.2%); £3,780,111.12 -> £3,395,062.52 (10.2%); £3,780,111.26 -> £3,395,062.53 (10.2%); £3,780,111.40 -> £3,395,062.77 (10.2%); £3,780,111.55 -> £3,395,063.02 (10.2%); £3,780,111.70 -> £3,395,063.27 (10.2%); £3,780,111.88 -> £3,395,063.52 (10.2%); £3,780,112.07 -> £3,395,063.76 (10.2%); £3,780,112.27 -> £3,395,064.01 (10.2%); £3,780,112.49 -> £3,395,064.26 (10.2%); £3,780,112.73 -> £3,395,064.50 (10.2%); £3,780,112.96 -> £3,395,064.53 (10.2%); £3,780,113.20 -> £3,395,064.55 (10.2%); £3,780,113.44 -> £3,395,064.58 (10.2%); £3,780,113.67 -> £3,395,064.60 (10.2%); £3,780,113.91 -> £3,395,064.62 (10.2%); £3,780,114.15 -> £3,395,064.65 (10.2%); £3,780,114.38 -> £3,395,064.67 (10.2%); £3,780,114.62 -> £3,395,064.69 (10.2%); £3,780,114.86 -> £3,395,064.72 (10.2%); £3,780,115.10 -> £3,395,064.74 (10.2%); £3,780,115.34 -> £3,395,064.76 (10.2%); £3,780,115.58 -> £3,395,064.79 (10.2%); £3,780,115.81 -> £3,395,064.81 (10.2%); £3,780,115.99 -> £3,395,065.05 (10.2%); £3,780,116.17 -> £3,395,065.30 (10.2%); £3,780,116.40 -> £3,395,065.55 (10.2%); £3,780,116.64 -> £3,395,065.80 (10.2%); £3,780,116.88 -> £3,395,066.05 (10.2%); £3,780,117.12 -> £3,395,066.30 (10.2%); £3,780,117.36 -> £3,395,066.55 (10.2%); £3,780,117.61 -> £3,395,066.80 (10.2%); £3,780,117.84 -> £3,395,067.04 (10.2%); £3,780,118.08 -> £3,395,067.28 (10.2%); £3,780,118.32 -> £3,395,067.51 (10.2%); £3,780,118.55 -> £3,395,067.54 (10.2%); £3,780,118.78 -> £3,395,067.57 (10.2%); £3,780,118.99 -> £3,395,067.59 (10.2%); £3,780,119.19 -> £3,395,067.61 (10.2%); £3,780,119.37 -> £3,395,067.63 (10.2%); £3,780,119.51 -> £3,395,067.65 (10.2%); £3,780,119.65 -> £3,395,067.67 (10.2%); £3,780,119.79 -> £3,395,067.69 (10.2%); £3,780,119.94 -> £3,395,067.70 (10.2%); £3,780,120.07 -> £3,395,067.72 (10.2%); £3,780,120.21 -> £3,395,067.74 (10.2%); £3,780,120.35 -> £3,395,067.75 (10.2%); £3,780,120.50 -> £3,395,067.77 (10.2%); £3,780,120.65 -> £3,395,067.78 (10.2%); £3,780,120.79 -> £3,395,067.80 (10.2%); £3,780,120.93 -> £3,395,067.82 (10.2%); £3,780,121.08 -> £3,395,068.08 (10.2%); £3,780,121.22 -> £3,395,068.35 (10.2%); £3,780,121.38 -> £3,395,068.62 (10.2%); £3,780,121.55 -> £3,395,068.89 (10.2%); £3,780,121.74 -> £3,395,069.16 (10.2%); £3,780,121.94 -> £3,395,069.43 (10.2%); £3,780,122.16 -> £3,395,069.70 (10.2%); £3,780,122.40 -> £3,395,069.96 (10.2%); £3,780,122.63 -> £3,395,069.99 (10.2%); £3,780,122.87 -> £3,395,070.01 (10.2%); £3,780,123.09 -> £3,395,070.04 (10.2%); £3,780,123.33 -> £3,395,070.06 (10.2%); £3,780,123.55 -> £3,395,070.08 (10.2%); £3,780,123.80 -> £3,395,070.11 (10.2%); £3,780,124.04 -> £3,395,070.13 (10.2%); £3,780,124.28 -> £3,395,070.15 (10.2%); £3,780,124.51 -> £3,395,070.18 (10.2%); £3,780,124.75 -> £3,395,070.20 (10.2%); £3,780,124.98 -> £3,395,070.22 (10.2%); £3,780,125.22 -> £3,395,070.25 (10.2%); £3,780,125.45 -> £3,395,070.28 (10.2%); £3,780,125.64 -> £3,395,070.54 (10.2%); £3,780,125.81 -> £3,395,070.82 (10.2%); £3,780,125.99 -> £3,395,071.09 (10.2%); £3,780,126.16 -> £3,395,071.36 (10.2%); £3,780,126.34 -> £3,395,071.64 (10.2%); £3,780,126.52 -> £3,395,071.91 (10.2%); £3,780,126.70 -> £3,395,072.18 (10.2%); £3,780,126.92 -> £3,395,072.44 (10.2%); £3,780,127.16 -> £3,395,072.71 (10.2%); £3,780,127.40 -> £3,395,072.98 (10.2%); £3,780,127.62 -> £3,395,073.25 (10.2%); £3,780,127.86 -> £3,395,073.28 (10.2%); £3,780,128.10 -> £3,395,073.31 (10.2%); £3,780,128.32 -> £3,395,073.34 (10.2%); £3,780,128.53 -> £3,395,073.36 (10.2%); £3,780,128.71 -> £3,395,073.38 (10.2%); £3,780,128.86 -> £3,395,073.40 (10.2%); £3,780,129.00 -> £3,395,073.41 (10.2%); £3,780,129.15 -> £3,395,073.43 (10.2%); £3,780,129.29 -> £3,395,073.45 (10.2%); £3,780,129.43 -> £3,395,073.47 (10.2%); £3,780,129.57 -> £3,395,073.48 (10.2%); £3,780,129.72 -> £3,395,073.50 (10.2%); £3,780,129.86 -> £3,395,073.52 (10.2%); £3,780,130.00 -> £3,395,073.53 (10.2%); £3,780,130.15 -> £3,395,073.55 (10.2%); £3,780,130.29 -> £3,395,073.57 (10.2%); £3,780,130.43 -> £3,395,073.79 (10.2%); £3,780,130.58 -> £3,395,074.02 (10.2%); £3,780,130.74 -> £3,395,074.24 (10.2%); £3,780,130.92 -> £3,395,074.48 (10.2%); £3,780,131.10 -> £3,395,074.71 (10.2%); £3,780,131.31 -> £3,395,074.94 (10.2%); £3,780,131.53 -> £3,395,075.17 (10.2%); £3,780,131.77 -> £3,395,075.40 (10.2%); £3,780,132.00 -> £3,395,075.42 (10.2%); £3,780,132.23 -> £3,395,075.44 (10.2%); £3,780,132.47 -> £3,395,075.47 (10.2%); £3,780,132.71 -> £3,395,075.49 (10.2%); £3,780,132.96 -> £3,395,075.52 (10.2%); £3,780,133.19 -> £3,395,075.54 (10.2%); £3,780,133.44 -> £3,395,075.56 (10.2%); £3,780,133.67 -> £3,395,075.59 (10.2%); £3,780,133.90 -> £3,395,075.61 (10.2%); £3,780,134.14 -> £3,395,075.63 (10.2%); £3,780,134.38 -> £3,395,075.66 (10.2%); £3,780,134.62 -> £3,395,075.68 (10.2%); £3,780,134.86 -> £3,395,075.71 (10.2%); £3,780,135.09 -> £3,395,075.94 (10.2%); £3,780,135.27 -> £3,395,076.17 (10.2%); £3,780,135.44 -> £3,395,076.41 (10.2%); £3,780,135.62 -> £3,395,076.64 (10.2%); £3,780,135.80 -> £3,395,076.88 (10.2%); £3,780,136.05 -> £3,395,077.12 (10.2%); £3,780,136.29 -> £3,395,077.35 (10.2%); £3,780,136.53 -> £3,395,077.59 (10.2%); £3,780,136.78 -> £3,395,077.82 (10.2%); £3,780,137.02 -> £3,395,078.05 (10.2%); £3,780,137.26 -> £3,395,078.27 (10.2%); £3,780,137.50 -> £3,395,078.30 (10.2%); £3,780,137.74 -> £3,395,078.33 (10.2%); £3,780,137.96 -> £3,395,078.36 (10.2%); £3,780,138.17 -> £3,395,078.38 (10.2%); £3,780,138.36 -> £3,395,078.40 (10.2%); £3,780,138.49 -> £3,395,078.42 (10.2%); £3,780,138.61 -> £3,395,078.44 (10.2%); £3,780,138.74 -> £3,395,078.45 (10.2%); £3,780,138.87 -> £3,395,078.47 (10.2%); £3,780,139.00 -> £3,395,078.49 (10.2%); £3,780,139.13 -> £3,395,078.51 (10.2%); £3,780,139.26 -> £3,395,078.52 (10.2%); £3,780,139.38 -> £3,395,078.54 (10.2%); £3,780,139.51 -> £3,395,078.56 (10.2%); £3,780,139.64 -> £3,395,078.57 (10.2%); £3,780,139.76 -> £3,395,078.59 (10.2%); £3,780,139.90 -> £3,395,078.76 (10.2%); £3,780,140.03 -> £3,395,078.94 (10.2%); £3,780,140.17 -> £3,395,079.12 (10.2%); £3,780,140.33 -> £3,395,079.30 (10.2%); £3,780,140.50 -> £3,395,079.48 (10.2%); £3,780,140.69 -> £3,395,079.66 (10.2%); £3,780,140.89 -> £3,395,079.85 (10.2%); £3,780,141.10 -> £3,395,080.03 (10.2%); £3,780,141.32 -> £3,395,080.06 (10.2%); £3,780,141.54 -> £3,395,080.08 (10.2%); £3,780,141.75 -> £3,395,080.11 (10.2%); £3,780,141.96 -> £3,395,080.14 (10.2%); £3,780,142.17 -> £3,395,080.16 (10.2%); £3,780,142.39 -> £3,395,080.19 (10.2%); £3,780,142.60 -> £3,395,080.22 (10.2%); £3,780,142.82 -> £3,395,080.24 (10.2%); £3,780,143.03 -> £3,395,080.27 (10.2%); £3,780,143.25 -> £3,395,080.29 (10.2%); £3,780,143.46 -> £3,395,080.32 (10.2%); £3,780,143.67 -> £3,395,080.34 (10.2%); £3,780,143.89 -> £3,395,080.37 (10.2%); £3,780,144.05 -> £3,395,080.55 (10.2%); £3,780,144.21 -> £3,395,080.74 (10.2%); £3,780,144.38 -> £3,395,080.92 (10.2%); £3,780,144.54 -> £3,395,081.11 (10.2%); £3,780,144.70 -> £3,395,081.30 (10.2%); £3,780,144.87 -> £3,395,081.49 (10.2%); £3,780,145.03 -> £3,395,081.67 (10.2%); £3,780,145.24 -> £3,395,081.86 (10.2%); £3,780,145.45 -> £3,395,082.04 (10.2%); £3,780,145.67 -> £3,395,082.22 (10.2%); £3,780,145.88 -> £3,395,082.40 (10.2%); £3,780,146.10 -> £3,395,082.43 (10.2%); £3,780,146.31 -> £3,395,082.46 (10.2%); £3,780,146.51 -> £3,395,082.48 (10.2%); £3,780,146.70 -> £3,395,082.51 (10.2%); £3,780,146.86 -> £3,395,082.53 (10.2%); £3,780,146.99 -> £3,395,082.55 (10.2%); £3,780,147.12 -> £3,395,082.57 (10.2%); £3,780,147.25 -> £3,395,082.59 (10.2%); £3,780,147.38 -> £3,395,082.60 (10.2%); £3,780,147.51 -> £3,395,082.62 (10.2%); £3,780,147.64 -> £3,395,082.64 (10.2%); £3,780,147.76 -> £3,395,082.65 (10.2%); £3,780,147.89 -> £3,395,082.67 (10.2%); £3,780,148.02 -> £3,395,082.69 (10.2%); £3,780,148.14 -> £3,395,082.70 (10.2%); £3,780,148.28 -> £3,395,082.72 (10.2%); £3,780,148.41 -> £3,395,082.83 (10.2%); £3,780,148.53 -> £3,395,082.95 (10.2%); £3,780,148.68 -> £3,395,083.06 (10.2%); £3,780,148.84 -> £3,395,083.17 (10.2%); £3,780,149.01 -> £3,395,083.29 (10.2%); £3,780,149.19 -> £3,395,083.41 (10.2%); £3,780,149.40 -> £3,395,083.54 (10.2%); £3,780,149.62 -> £3,395,083.66 (10.2%); £3,780,149.83 -> £3,395,083.69 (10.2%); £3,780,150.05 -> £3,395,083.72 (10.2%); £3,780,150.27 -> £3,395,083.75 (10.2%); £3,780,150.48 -> £3,395,083.78 (10.2%); £3,780,150.69 -> £3,395,083.81 (10.2%); £3,780,150.91 -> £3,395,083.84 (10.2%); £3,780,151.12 -> £3,395,083.88 (10.2%); £3,780,151.33 -> £3,395,083.90 (10.2%); £3,780,151.55 -> £3,395,083.93 (10.2%); £3,780,151.76 -> £3,395,083.96 (10.2%); £3,780,151.98 -> £3,395,083.99 (10.2%); £3,780,152.20 -> £3,395,084.02 (10.2%); £3,780,152.42 -> £3,395,084.05 (10.2%); £3,780,152.58 -> £3,395,084.17 (10.2%); £3,780,152.74 -> £3,395,084.30 (10.2%); £3,780,152.89 -> £3,395,084.44 (10.2%); £3,780,153.05 -> £3,395,084.57 (10.2%); £3,780,153.21 -> £3,395,084.70 (10.2%); £3,780,153.38 -> £3,395,084.83 (10.2%); £3,780,153.53 -> £3,395,084.96 (10.2%); £3,780,153.75 -> £3,395,085.09 (10.2%); £3,780,153.96 -> £3,395,085.21 (10.2%); £3,780,154.18 -> £3,395,085.34 (10.2%); £3,780,154.39 -> £3,395,085.46 (10.2%); £3,780,154.60 -> £3,395,085.49 (10.2%); £3,780,154.83 -> £3,395,085.52 (10.2%); £3,780,155.02 -> £3,395,085.54 (10.2%); £3,780,155.20 -> £3,395,085.56 (10.2%); £3,780,155.36 -> £3,395,085.58 (10.2%); £3,780,155.51 -> £3,395,085.60 (10.2%); £3,780,155.65 -> £3,395,085.62 (10.2%); £3,780,155.80 -> £3,395,085.64 (10.2%); £3,780,155.95 -> £3,395,085.65 (10.2%); £3,780,156.09 -> £3,395,085.67 (10.2%); £3,780,156.24 -> £3,395,085.69 (10.2%); £3,780,156.38 -> £3,395,085.70 (10.2%); £3,780,156.54 -> £3,395,085.72 (10.2%); £3,780,156.68 -> £3,395,085.74 (10.2%); £3,780,156.82 -> £3,395,085.75 (10.2%); £3,780,156.97 -> £3,395,085.77 (10.2%); £3,780,157.11 -> £3,395,085.90 (10.2%); £3,780,157.26 -> £3,395,086.03 (10.2%); £3,780,157.42 -> £3,395,086.17 (10.2%); £3,780,157.60 -> £3,395,086.30 (10.2%); £3,780,157.80 -> £3,395,086.44 (10.2%); £3,780,158.01 -> £3,395,086.58 (10.2%); £3,780,158.24 -> £3,395,086.71 (10.2%); £3,780,158.50 -> £3,395,086.85 (10.2%); £3,780,158.74 -> £3,395,086.87 (10.2%); £3,780,158.99 -> £3,395,086.89 (10.2%); £3,780,159.24 -> £3,395,086.92 (10.2%); £3,780,159.48 -> £3,395,086.94 (10.2%); £3,780,159.73 -> £3,395,086.97 (10.2%); £3,780,159.99 -> £3,395,086.99 (10.2%); £3,780,160.23 -> £3,395,087.01 (10.2%); £3,780,160.48 -> £3,395,087.04 (10.2%); £3,780,160.73 -> £3,395,087.06 (10.2%); £3,780,160.98 -> £3,395,087.08 (10.2%); £3,780,161.23 -> £3,395,087.11 (10.2%); £3,780,161.48 -> £3,395,087.13 (10.2%); £3,780,161.73 -> £3,395,087.16 (10.2%); £3,780,161.97 -> £3,395,087.30 (10.2%); £3,780,162.16 -> £3,395,087.45 (10.2%); £3,780,162.33 -> £3,395,087.60 (10.2%); £3,780,162.53 -> £3,395,087.75 (10.2%); £3,780,162.70 -> £3,395,087.89 (10.2%); £3,780,162.88 -> £3,395,088.04 (10.2%); £3,780,163.07 -> £3,395,088.19 (10.2%); £3,780,163.31 -> £3,395,088.33 (10.2%); £3,780,163.55 -> £3,395,088.47 (10.2%); £3,780,163.80 -> £3,395,088.62 (10.2%); £3,780,164.05 -> £3,395,088.76 (10.2%); £3,780,164.29 -> £3,395,088.79 (10.2%); £3,780,164.53 -> £3,395,088.82 (10.2%); £3,780,164.76 -> £3,395,088.84 (10.2%); £3,780,164.97 -> £3,395,088.87 (10.2%); £3,780,165.17 -> £3,395,088.89 (10.2%); £3,780,165.31 -> £3,395,088.91 (10.2%); £3,780,165.46 -> £3,395,088.92 (10.2%); £3,780,165.61 -> £3,395,088.94 (10.2%); £3,780,165.75 -> £3,395,088.96 (10.2%); £3,780,165.90 -> £3,395,088.98 (10.2%); £3,780,166.05 -> £3,395,088.99 (10.2%); £3,780,166.20 -> £3,395,089.01 (10.2%); £3,780,166.35 -> £3,395,089.03 (10.2%); £3,780,166.49 -> £3,395,089.04 (10.2%); £3,780,166.64 -> £3,395,089.06 (10.2%); £3,780,166.79 -> £3,395,089.08 (10.2%); £3,780,166.94 -> £3,395,089.19 (10.2%); £3,780,167.09 -> £3,395,089.32 (10.2%); £3,780,167.25 -> £3,395,089.44 (10.2%); £3,780,167.44 -> £3,395,089.57 (10.2%); £3,780,167.63 -> £3,395,089.70 (10.2%); £3,780,167.85 -> £3,395,089.83 (10.2%); £3,780,168.08 -> £3,395,089.95 (10.2%); £3,780,168.33 -> £3,395,090.07 (10.2%); £3,780,168.58 -> £3,395,090.10 (10.2%); £3,780,168.82 -> £3,395,090.12 (10.2%); £3,780,169.07 -> £3,395,090.15 (10.2%); £3,780,169.31 -> £3,395,090.17 (10.2%); £3,780,169.57 -> £3,395,090.20 (10.2%); £3,780,169.80 -> £3,395,090.22 (10.2%); £3,780,170.05 -> £3,395,090.24 (10.2%); £3,780,170.30 -> £3,395,090.27 (10.2%); £3,780,170.55 -> £3,395,090.29 (10.2%); £3,780,170.79 -> £3,395,090.31 (10.2%); £3,780,171.03 -> £3,395,090.34 (10.2%); £3,780,171.28 -> £3,395,090.36 (10.2%); £3,780,171.53 -> £3,395,090.39 (10.2%); £3,780,171.71 -> £3,395,090.52 (10.2%); £3,780,171.90 -> £3,395,090.66 (10.2%); £3,780,172.16 -> £3,395,090.81 (10.2%); £3,780,172.40 -> £3,395,090.95 (10.2%); £3,780,172.64 -> £3,395,091.09 (10.2%); £3,780,172.89 -> £3,395,091.23 (10.2%); £3,780,173.07 -> £3,395,091.36 (10.2%); £3,780,173.33 -> £3,395,091.49 (10.2%); £3,780,173.58 -> £3,395,091.63 (10.2%); £3,780,173.82 -> £3,395,091.76 (10.2%); £3,780,174.08 -> £3,395,091.89 (10.2%); £3,780,174.32 -> £3,395,091.92 (10.2%); £3,780,174.57 -> £3,395,091.95 (10.2%); £3,780,174.81 -> £3,395,091.97 (10.2%); £3,780,175.01 -> £3,395,091.99 (10.2%); £3,780,175.21 -> £3,395,092.01 (10.2%); £3,780,175.35 -> £3,395,092.03 (10.2%); £3,780,175.50 -> £3,395,092.05 (10.2%); £3,780,175.65 -> £3,395,092.07 (10.2%); £3,780,175.80 -> £3,395,092.09 (10.2%); £3,780,175.94 -> £3,395,092.10 (10.2%); £3,780,176.09 -> £3,395,092.12 (10.2%); £3,780,176.24 -> £3,395,092.14 (10.2%); £3,780,176.39 -> £3,395,092.15 (10.2%); £3,780,176.54 -> £3,395,092.17 (10.2%); £3,780,176.69 -> £3,395,092.19 (10.2%); £3,780,176.84 -> £3,395,092.20 (10.2%); £3,780,176.99 -> £3,395,092.33 (10.2%); £3,780,177.14 -> £3,395,092.45 (10.2%); £3,780,177.32 -> £3,395,092.58 (10.2%); £3,780,177.50 -> £3,395,092.72 (10.2%); £3,780,177.70 -> £3,395,092.85 (10.2%); £3,780,177.91 -> £3,395,092.98 (10.2%); £3,780,178.15 -> £3,395,093.11 (10.2%); £3,780,178.39 -> £3,395,093.24 (10.2%); £3,780,178.65 -> £3,395,093.27 (10.2%); £3,780,178.90 -> £3,395,093.29 (10.2%); £3,780,179.15 -> £3,395,093.32 (10.2%); £3,780,179.40 -> £3,395,093.34 (10.2%); £3,780,179.65 -> £3,395,093.36 (10.2%); £3,780,179.90 -> £3,395,093.39 (10.2%); £3,780,180.15 -> £3,395,093.41 (10.2%); £3,780,180.40 -> £3,395,093.44 (10.2%); £3,780,180.67 -> £3,395,093.46 (10.2%); £3,780,180.92 -> £3,395,093.48 (10.2%); £3,780,181.17 -> £3,395,093.51 (10.2%); £3,780,181.42 -> £3,395,093.53 (10.2%); £3,780,181.68 -> £3,395,093.56 (10.2%); £3,780,181.92 -> £3,395,093.70 (10.2%); £3,780,182.11 -> £3,395,093.84 (10.2%); £3,780,182.30 -> £3,395,093.99 (10.2%); £3,780,182.54 -> £3,395,094.14 (10.2%); £3,780,182.80 -> £3,395,094.29 (10.2%); £3,780,183.05 -> £3,395,094.44 (10.2%); £3,780,183.25 -> £3,395,094.58 (10.2%); £3,780,183.50 -> £3,395,094.73 (10.2%); £3,780,183.76 -> £3,395,094.87 (10.2%); £3,780,184.00 -> £3,395,095.01 (10.2%); £3,780,184.26 -> £3,395,095.15 (10.2%); £3,780,184.51 -> £3,395,095.18 (10.2%); £3,780,184.76 -> £3,395,095.21 (10.2%); £3,780,185.00 -> £3,395,095.23 (10.2%); £3,780,185.21 -> £3,395,095.25 (10.2%); £3,780,185.40 -> £3,395,095.27 (10.2%); £3,780,185.56 -> £3,395,095.29 (10.2%); £3,780,185.71 -> £3,395,095.31 (10.2%); £3,780,185.87 -> £3,395,095.33 (10.2%); £3,780,186.03 -> £3,395,095.35 (10.2%); £3,780,186.18 -> £3,395,095.36 (10.2%); £3,780,186.33 -> £3,395,095.38 (10.2%); £3,780,186.49 -> £3,395,095.40 (10.2%); £3,780,186.65 -> £3,395,095.41 (10.2%); £3,780,186.80 -> £3,395,095.43 (10.2%); £3,780,186.95 -> £3,395,095.45 (10.2%); £3,780,187.10 -> £3,395,095.46 (10.2%); £3,780,187.25 -> £3,395,095.58 (10.2%); £3,780,187.41 -> £3,395,095.69 (10.2%); £3,780,187.58 -> £3,395,095.81 (10.2%); £3,780,187.77 -> £3,395,095.94 (10.2%); £3,780,187.97 -> £3,395,096.06 (10.2%); £3,780,188.19 -> £3,395,096.19 (10.2%); £3,780,188.43 -> £3,395,096.31 (10.2%); £3,780,188.68 -> £3,395,096.43 (10.2%); £3,780,188.94 -> £3,395,096.46 (10.2%); £3,780,189.19 -> £3,395,096.48 (10.2%); £3,780,189.44 -> £3,395,096.51 (10.2%); £3,780,189.69 -> £3,395,096.53 (10.2%); £3,780,189.94 -> £3,395,096.55 (10.2%); £3,780,190.20 -> £3,395,096.58 (10.2%); £3,780,190.47 -> £3,395,096.60 (10.2%); £3,780,190.72 -> £3,395,096.63 (10.2%); £3,780,190.98 -> £3,395,096.65 (10.2%); £3,780,191.24 -> £3,395,096.67 (10.2%); £3,780,191.49 -> £3,395,096.70 (10.2%); £3,780,191.74 -> £3,395,096.72 (10.2%); £3,780,192.00 -> £3,395,096.75 (10.2%); £3,780,192.19 -> £3,395,096.88 (10.2%); £3,780,192.38 -> £3,395,097.02 (10.2%); £3,780,192.57 -> £3,395,097.15 (10.2%); £3,780,192.76 -> £3,395,097.29 (10.2%); £3,780,193.02 -> £3,395,097.43 (10.2%); £3,780,193.27 -> £3,395,097.56 (10.2%); £3,780,193.46 -> £3,395,097.69 (10.2%); £3,780,193.73 -> £3,395,097.82 (10.2%); £3,780,193.98 -> £3,395,097.95 (10.2%); £3,780,194.24 -> £3,395,098.08 (10.2%); £3,780,194.49 -> £3,395,098.21 (10.2%); £3,780,194.75 -> £3,395,098.24 (10.2%); £3,780,195.00 -> £3,395,098.27 (10.2%); £3,780,195.24 -> £3,395,098.29 (10.2%); £3,780,195.46 -> £3,395,098.31 (10.2%); £3,780,195.66 -> £3,395,098.33 (10.2%); £3,780,195.81 -> £3,395,098.35 (10.2%); £3,780,195.96 -> £3,395,098.37 (10.2%); £3,780,196.11 -> £3,395,098.39 (10.2%); £3,780,196.27 -> £3,395,098.40 (10.2%); £3,780,196.41 -> £3,395,098.42 (10.2%); £3,780,196.57 -> £3,395,098.44 (10.2%); £3,780,196.72 -> £3,395,098.45 (10.2%); £3,780,196.88 -> £3,395,098.47 (10.2%); £3,780,197.03 -> £3,395,098.49 (10.2%); £3,780,197.19 -> £3,395,098.50 (10.2%); £3,780,197.34 -> £3,395,098.52 (10.2%); £3,780,197.49 -> £3,395,098.65 (10.2%); £3,780,197.65 -> £3,395,098.79 (10.2%); £3,780,197.82 -> £3,395,098.93 (10.2%); £3,780,198.01 -> £3,395,099.07 (10.2%); £3,780,198.21 -> £3,395,099.21 (10.2%); £3,780,198.43 -> £3,395,099.35 (10.2%); £3,780,198.67 -> £3,395,099.49 (10.2%); £3,780,198.94 -> £3,395,099.63 (10.2%); £3,780,199.20 -> £3,395,099.65 (10.2%); £3,780,199.47 -> £3,395,099.68 (10.2%); £3,780,199.72 -> £3,395,099.70 (10.2%); £3,780,199.98 -> £3,395,099.73 (10.2%); £3,780,200.24 -> £3,395,099.75 (10.2%); £3,780,200.48 -> £3,395,099.78 (10.2%); £3,780,200.74 -> £3,395,099.80 (10.2%); £3,780,200.99 -> £3,395,099.83 (10.2%); £3,780,201.25 -> £3,395,099.85 (10.2%); £3,780,201.51 -> £3,395,099.87 (10.2%); £3,780,201.76 -> £3,395,099.90 (10.2%); £3,780,202.01 -> £3,395,099.92 (10.2%); £3,780,202.27 -> £3,395,099.95 (10.2%); £3,780,202.46 -> £3,395,100.10 (10.2%); £3,780,202.66 -> £3,395,100.25 (10.2%); £3,780,202.85 -> £3,395,100.40 (10.2%); £3,780,203.05 -> £3,395,100.55 (10.2%); £3,780,203.24 -> £3,395,100.70 (10.2%); £3,780,203.43 -> £3,395,100.85 (10.2%); £3,780,203.63 -> £3,395,101.00 (10.2%); £3,780,203.89 -> £3,395,101.15 (10.2%); £3,780,204.14 -> £3,395,101.30 (10.2%); £3,780,204.40 -> £3,395,101.46 (10.2%); £3,780,204.66 -> £3,395,101.60 (10.2%); £3,780,204.91 -> £3,395,101.63 (10.2%); £3,780,205.16 -> £3,395,101.66 (10.2%); £3,780,205.40 -> £3,395,101.68 (10.2%); £3,780,205.61 -> £3,395,101.70 (10.2%); £3,780,205.82 -> £3,395,101.73 (10.2%); £3,780,205.96 -> £3,395,101.75 (10.2%); £3,780,206.10 -> £3,395,101.77 (10.2%); £3,780,206.24 -> £3,395,101.78 (10.2%); £3,780,206.38 -> £3,395,101.80 (10.2%); £3,780,206.52 -> £3,395,101.82 (10.2%); £3,780,206.66 -> £3,395,101.83 (10.2%); £3,780,206.80 -> £3,395,101.85 (10.2%); £3,780,206.94 -> £3,395,101.87 (10.2%); £3,780,207.08 -> £3,395,101.89 (10.2%); £3,780,207.22 -> £3,395,101.90 (10.2%); £3,780,207.35 -> £3,395,101.92 (10.2%); £3,780,207.49 -> £3,395,102.08 (10.2%); £3,780,207.63 -> £3,395,102.23 (10.2%); £3,780,207.79 -> £3,395,102.39 (10.2%); £3,780,207.96 -> £3,395,102.55 (10.2%); £3,780,208.15 -> £3,395,102.71 (10.2%); £3,780,208.35 -> £3,395,102.88 (10.2%); £3,780,208.56 -> £3,395,103.04 (10.2%); £3,780,208.80 -> £3,395,103.21 (10.2%); £3,780,209.03 -> £3,395,103.23 (10.2%); £3,780,209.27 -> £3,395,103.26 (10.2%); £3,780,209.50 -> £3,395,103.28 (10.2%); £3,780,209.73 -> £3,395,103.31 (10.2%); £3,780,209.95 -> £3,395,103.34 (10.2%); £3,780,210.18 -> £3,395,103.37 (10.2%); £3,780,210.41 -> £3,395,103.40 (10.2%); £3,780,210.65 -> £3,395,103.42 (10.2%); £3,780,210.88 -> £3,395,103.45 (10.2%); £3,780,211.12 -> £3,395,103.47 (10.2%); £3,780,211.35 -> £3,395,103.50 (10.2%); £3,780,211.58 -> £3,395,103.53 (10.2%); £3,780,211.80 -> £3,395,103.55 (10.2%); £3,780,211.97 -> £3,395,103.72 (10.2%); £3,780,212.15 -> £3,395,103.88 (10.2%); £3,780,212.33 -> £3,395,104.05 (10.2%); £3,780,212.50 -> £3,395,104.22 (10.2%); £3,780,212.67 -> £3,395,104.39 (10.2%); £3,780,212.91 -> £3,395,104.57 (10.2%); £3,780,213.13 -> £3,395,104.74 (10.2%); £3,780,213.36 -> £3,395,104.90 (10.2%); £3,780,213.60 -> £3,395,105.07 (10.2%); £3,780,213.83 -> £3,395,105.23 (10.2%); £3,780,214.06 -> £3,395,105.40 (10.2%); £3,780,214.29 -> £3,395,105.43 (10.2%); £3,780,214.52 -> £3,395,105.46 (10.2%); £3,780,214.73 -> £3,395,105.49 (10.2%); £3,780,214.92 -> £3,395,105.51 (10.2%); £3,780,215.09 -> £3,395,105.53 (10.2%); £3,780,215.23 -> £3,395,105.55 (10.2%); £3,780,215.37 -> £3,395,105.57 (10.2%); £3,780,215.51 -> £3,395,105.59 (10.2%); £3,780,215.66 -> £3,395,105.61 (10.2%); £3,780,215.80 -> £3,395,105.63 (10.2%); £3,780,215.94 -> £3,395,105.64 (10.2%); £3,780,216.08 -> £3,395,105.66 (10.2%); £3,780,216.22 -> £3,395,105.68 (10.2%); £3,780,216.36 -> £3,395,105.69 (10.2%); £3,780,216.50 -> £3,395,105.71 (10.2%); £3,780,216.63 -> £3,395,105.73 (10.2%); £3,780,216.77 -> £3,395,105.86 (10.2%); £3,780,216.91 -> £3,395,105.99 (10.2%); £3,780,217.07 -> £3,395,106.12 (10.2%); £3,780,217.24 -> £3,395,106.25 (10.2%); £3,780,217.43 -> £3,395,106.38 (10.2%); £3,780,217.63 -> £3,395,106.51 (10.2%); £3,780,217.85 -> £3,395,106.65 (10.2%); £3,780,218.08 -> £3,395,106.79 (10.2%); £3,780,218.32 -> £3,395,106.82 (10.2%); £3,780,218.56 -> £3,395,106.85 (10.2%); £3,780,218.79 -> £3,395,106.88 (10.2%); £3,780,219.02 -> £3,395,106.91 (10.2%); £3,780,219.25 -> £3,395,106.94 (10.2%); £3,780,219.48 -> £3,395,106.98 (10.2%); £3,780,219.71 -> £3,395,107.01 (10.2%); £3,780,219.94 -> £3,395,107.04 (10.2%); £3,780,220.18 -> £3,395,107.06 (10.2%); £3,780,220.41 -> £3,395,107.09 (10.2%); £3,780,220.65 -> £3,395,107.12 (10.2%); £3,780,220.88 -> £3,395,107.15 (10.2%); £3,780,221.10 -> £3,395,107.18 (10.2%); £3,780,221.27 -> £3,395,107.32 (10.2%); £3,780,221.44 -> £3,395,107.46 (10.2%); £3,780,221.62 -> £3,395,107.60 (10.2%); £3,780,221.80 -> £3,395,107.76 (10.2%); £3,780,222.03 -> £3,395,107.91 (10.2%); £3,780,222.26 -> £3,395,108.05 (10.2%); £3,780,222.44 -> £3,395,108.19 (10.2%); £3,780,222.67 -> £3,395,108.33 (10.2%); £3,780,222.91 -> £3,395,108.47 (10.2%); £3,780,223.14 -> £3,395,108.61 (10.2%); £3,780,223.38 -> £3,395,108.75 (10.2%); £3,780,223.61 -> £3,395,108.78 (10.2%); £3,780,223.85 -> £3,395,108.81 (10.2%); £3,780,224.06 -> £3,395,108.83 (10.2%); £3,780,224.26 -> £3,395,108.85 (10.2%); £3,780,224.43 -> £3,395,108.87 (10.2%); £3,780,224.59 -> £3,395,108.89 (10.2%); £3,780,224.74 -> £3,395,108.91 (10.2%); £3,780,224.91 -> £3,395,108.93 (10.2%); £3,780,225.07 -> £3,395,108.94 (10.2%); £3,780,225.23 -> £3,395,108.96 (10.2%); £3,780,225.38 -> £3,395,108.98 (10.2%); £3,780,225.55 -> £3,395,108.99 (10.2%); £3,780,225.71 -> £3,395,109.01 (10.2%); £3,780,225.87 -> £3,395,109.03 (10.2%); £3,780,226.03 -> £3,395,109.04 (10.2%); £3,780,226.19 -> £3,395,109.06 (10.2%); £3,780,226.36 -> £3,395,109.15 (10.2%); £3,780,226.52 -> £3,395,109.24 (10.2%); £3,780,226.70 -> £3,395,109.34 (10.2%); £3,780,226.90 -> £3,395,109.44 (10.2%); £3,780,227.11 -> £3,395,109.54 (10.2%); £3,780,227.35 -> £3,395,109.64 (10.2%); £3,780,227.60 -> £3,395,109.74 (10.2%); £3,780,227.87 -> £3,395,109.83 (10.2%); £3,780,228.14 -> £3,395,109.86 (10.2%); £3,780,228.41 -> £3,395,109.88 (10.2%); £3,780,228.69 -> £3,395,109.90 (10.2%); £3,780,228.94 -> £3,395,109.93 (10.2%); £3,780,229.21 -> £3,395,109.95 (10.2%); £3,780,229.48 -> £3,395,109.97 (10.2%); £3,780,229.73 -> £3,395,110.00 (10.2%); £3,780,229.99 -> £3,395,110.02 (10.2%); £3,780,230.26 -> £3,395,110.04 (10.2%); £3,780,230.52 -> £3,395,110.07 (10.2%); £3,780,230.79 -> £3,395,110.09 (10.2%); £3,780,231.06 -> £3,395,110.12 (10.2%); £3,780,231.33 -> £3,395,110.14 (10.2%); £3,780,231.59 -> £3,395,110.26 (10.2%); £3,780,231.87 -> £3,395,110.37 (10.2%); £3,780,232.14 -> £3,395,110.49 (10.2%); £3,780,232.41 -> £3,395,110.61 (10.2%); £3,780,232.69 -> £3,395,110.72 (10.2%); £3,780,232.95 -> £3,395,110.83 (10.2%); £3,780,233.16 -> £3,395,110.95 (10.2%); £3,780,233.43 -> £3,395,111.06 (10.2%); £3,780,233.70 -> £3,395,111.17 (10.2%); £3,780,233.96 -> £3,395,111.27 (10.2%); £3,780,234.23 -> £3,395,111.38 (10.2%); £3,780,234.49 -> £3,395,111.41 (10.2%); £3,780,234.77 -> £3,395,111.44 (10.2%); £3,780,235.01 -> £3,395,111.46 (10.2%); £3,780,235.24 -> £3,395,111.48 (10.2%); £3,780,235.45 -> £3,395,111.50 (10.2%); £3,780,235.61 -> £3,395,111.52 (10.2%); £3,780,235.77 -> £3,395,111.54 (10.2%); £3,780,235.93 -> £3,395,111.55 (10.2%); £3,780,236.09 -> £3,395,111.57 (10.2%); £3,780,236.24 -> £3,395,111.59 (10.2%); £3,780,236.40 -> £3,395,111.61 (10.2%); £3,780,236.56 -> £3,395,111.62 (10.2%); £3,780,236.71 -> £3,395,111.64 (10.2%); £3,780,236.88 -> £3,395,111.66 (10.2%); £3,780,237.04 -> £3,395,111.67 (10.2%); £3,780,237.19 -> £3,395,111.69 (10.2%); £3,780,237.35 -> £3,395,111.84 (10.2%); £3,780,237.51 -> £3,395,112.00 (10.2%); £3,780,237.68 -> £3,395,112.16 (10.2%); £3,780,237.88 -> £3,395,112.32 (10.2%); £3,780,238.09 -> £3,395,112.48 (10.2%); £3,780,238.32 -> £3,395,112.64 (10.2%); £3,780,238.57 -> £3,395,112.80 (10.2%); £3,780,238.84 -> £3,395,112.96 (10.2%); £3,780,239.11 -> £3,395,112.98 (10.2%); £3,780,239.38 -> £3,395,113.01 (10.2%); £3,780,239.63 -> £3,395,113.03 (10.2%); £3,780,239.90 -> £3,395,113.06 (10.2%); £3,780,240.17 -> £3,395,113.08 (10.2%); £3,780,240.43 -> £3,395,113.10 (10.2%); £3,780,240.69 -> £3,395,113.13 (10.2%); £3,780,240.96 -> £3,395,113.15 (10.2%); £3,780,241.23 -> £3,395,113.17 (10.2%); £3,780,241.50 -> £3,395,113.20 (10.2%); £3,780,241.76 -> £3,395,113.22 (10.2%); £3,780,242.02 -> £3,395,113.25 (10.2%); £3,780,242.29 -> £3,395,113.28 (10.2%); £3,780,242.49 -> £3,395,113.43 (10.2%); £3,780,242.69 -> £3,395,113.60 (10.2%); £3,780,242.96 -> £3,395,113.77 (10.2%); £3,780,243.23 -> £3,395,113.94 (10.2%); £3,780,243.43 -> £3,395,114.11 (10.2%); £3,780,243.62 -> £3,395,114.27 (10.2%); £3,780,243.82 -> £3,395,114.43 (10.2%); £3,780,244.08 -> £3,395,114.59 (10.2%); £3,780,244.34 -> £3,395,114.76 (10.2%); £3,780,244.60 -> £3,395,114.92 (10.2%); £3,780,244.86 -> £3,395,115.08 (10.2%); £3,780,245.12 -> £3,395,115.11 (10.2%); £3,780,245.39 -> £3,395,115.14 (10.2%); £3,780,245.63 -> £3,395,115.17 (10.2%); £3,780,245.85 -> £3,395,115.19 (10.2%); £3,780,246.06 -> £3,395,115.21 (10.2%); £3,780,246.22 -> £3,395,115.23 (10.2%); £3,780,246.38 -> £3,395,115.24 (10.2%); £3,780,246.54 -> £3,395,115.26 (10.2%); £3,780,246.70 -> £3,395,115.28 (10.2%); £3,780,246.86 -> £3,395,115.30 (10.2%); £3,780,247.01 -> £3,395,115.31 (10.2%); £3,780,247.17 -> £3,395,115.33 (10.2%); £3,780,247.33 -> £3,395,115.35 (10.2%); £3,780,247.49 -> £3,395,115.36 (10.2%); £3,780,247.65 -> £3,395,115.38 (10.2%); £3,780,247.81 -> £3,395,115.40 (10.2%); £3,780,247.97 -> £3,395,115.56 (10.2%); £3,780,248.12 -> £3,395,115.73 (10.2%); £3,780,248.30 -> £3,395,115.91 (10.2%); £3,780,248.49 -> £3,395,116.09 (10.2%); £3,780,248.70 -> £3,395,116.27 (10.2%); £3,780,248.93 -> £3,395,116.44 (10.2%); £3,780,249.19 -> £3,395,116.61 (10.2%); £3,780,249.45 -> £3,395,116.78 (10.2%); £3,780,249.72 -> £3,395,116.81 (10.2%); £3,780,249.99 -> £3,395,116.83 (10.2%); £3,780,250.26 -> £3,395,116.85 (10.2%); £3,780,250.52 -> £3,395,116.88 (10.2%); £3,780,250.79 -> £3,395,116.90 (10.2%); £3,780,251.05 -> £3,395,116.93 (10.2%); £3,780,251.31 -> £3,395,116.95 (10.2%); £3,780,251.56 -> £3,395,116.97 (10.2%); £3,780,251.84 -> £3,395,117.00 (10.2%); £3,780,252.10 -> £3,395,117.02 (10.2%); £3,780,252.37 -> £3,395,117.04 (10.2%); £3,780,252.63 -> £3,395,117.07 (10.2%); £3,780,252.89 -> £3,395,117.10 (10.2%); £3,780,253.16 -> £3,395,117.27 (10.2%); £3,780,253.42 -> £3,395,117.45 (10.2%); £3,780,253.62 -> £3,395,117.63 (10.2%); £3,780,253.82 -> £3,395,117.81 (10.2%); £3,780,254.03 -> £3,395,117.99 (10.2%); £3,780,254.30 -> £3,395,118.18 (10.2%); £3,780,254.56 -> £3,395,118.35 (10.2%); £3,780,254.83 -> £3,395,118.53 (10.2%); £3,780,255.09 -> £3,395,118.70 (10.2%); £3,780,255.36 -> £3,395,118.88 (10.2%); £3,780,255.62 -> £3,395,119.05 (10.2%); £3,780,255.89 -> £3,395,119.08 (10.2%); £3,780,256.16 -> £3,395,119.11 (10.2%); £3,780,256.40 -> £3,395,119.13 (10.2%); £3,780,256.62 -> £3,395,119.16 (10.2%); £3,780,256.83 -> £3,395,119.18 (10.2%); £3,780,256.99 -> £3,395,119.20 (10.2%); £3,780,257.15 -> £3,395,119.21 (10.2%); £3,780,257.31 -> £3,395,119.23 (10.2%); £3,780,257.47 -> £3,395,119.25 (10.2%); £3,780,257.62 -> £3,395,119.26 (10.2%); £3,780,257.78 -> £3,395,119.28 (10.2%); £3,780,257.94 -> £3,395,119.30 (10.2%); £3,780,258.10 -> £3,395,119.31 (10.2%); £3,780,258.26 -> £3,395,119.33 (10.2%); £3,780,258.42 -> £3,395,119.35 (10.2%); £3,780,258.58 -> £3,395,119.37 (10.2%); £3,780,258.75 -> £3,395,119.54 (10.2%); £3,780,258.91 -> £3,395,119.70 (10.2%); £3,780,259.08 -> £3,395,119.87 (10.2%); £3,780,259.26 -> £3,395,120.03 (10.2%); £3,780,259.48 -> £3,395,120.20 (10.2%); £3,780,259.70 -> £3,395,120.37 (10.2%); £3,780,259.94 -> £3,395,120.54 (10.2%); £3,780,260.21 -> £3,395,120.71 (10.2%); £3,780,260.47 -> £3,395,120.74 (10.2%); £3,780,260.73 -> £3,395,120.76 (10.2%); £3,780,260.99 -> £3,395,120.78 (10.2%); £3,780,261.25 -> £3,395,120.81 (10.2%); £3,780,261.51 -> £3,395,120.83 (10.2%); £3,780,261.78 -> £3,395,120.86 (10.2%); £3,780,262.05 -> £3,395,120.88 (10.2%); £3,780,262.32 -> £3,395,120.90 (10.2%); £3,780,262.58 -> £3,395,120.93 (10.2%); £3,780,262.85 -> £3,395,120.95 (10.2%); £3,780,263.12 -> £3,395,120.97 (10.2%); £3,780,263.39 -> £3,395,121.00 (10.2%); £3,780,263.66 -> £3,395,121.03 (10.2%); £3,780,263.92 -> £3,395,121.20 (10.2%); £3,780,264.12 -> £3,395,121.37 (10.2%); £3,780,264.31 -> £3,395,121.54 (10.2%); £3,780,264.51 -> £3,395,121.72 (10.2%); £3,780,264.71 -> £3,395,121.89 (10.2%); £3,780,264.90 -> £3,395,122.07 (10.2%); £3,780,265.17 -> £3,395,122.25 (10.2%); £3,780,265.43 -> £3,395,122.42 (10.2%); £3,780,265.70 -> £3,395,122.59 (10.2%); £3,780,265.96 -> £3,395,122.77 (10.2%); £3,780,266.23 -> £3,395,122.94 (10.2%); £3,780,266.49 -> £3,395,122.96 (10.2%); £3,780,266.76 -> £3,395,122.99 (10.2%); £3,780,267.01 -> £3,395,123.02 (10.2%); £3,780,267.23 -> £3,395,123.04 (10.2%); £3,780,267.43 -> £3,395,123.06 (10.2%); £3,780,267.59 -> £3,395,123.08 (10.2%); £3,780,267.75 -> £3,395,123.09 (10.2%); £3,780,267.91 -> £3,395,123.11 (10.2%); £3,780,268.06 -> £3,395,123.13 (10.2%); £3,780,268.22 -> £3,395,123.14 (10.2%); £3,780,268.38 -> £3,395,123.16 (10.2%); £3,780,268.54 -> £3,395,123.18 (10.2%); £3,780,268.70 -> £3,395,123.19 (10.2%); £3,780,268.86 -> £3,395,123.21 (10.2%); £3,780,269.02 -> £3,395,123.23 (10.2%); £3,780,269.17 -> £3,395,123.24 (10.2%); £3,780,269.34 -> £3,395,123.35 (10.2%); £3,780,269.49 -> £3,395,123.46 (10.2%); £3,780,269.67 -> £3,395,123.57 (10.2%); £3,780,269.86 -> £3,395,123.69 (10.2%); £3,780,270.07 -> £3,395,123.80 (10.2%); £3,780,270.30 -> £3,395,123.92 (10.2%); £3,780,270.55 -> £3,395,124.03 (10.2%); £3,780,270.83 -> £3,395,124.14 (10.2%); £3,780,271.10 -> £3,395,124.17 (10.2%); £3,780,271.37 -> £3,395,124.19 (10.2%); £3,780,271.64 -> £3,395,124.21 (10.2%); £3,780,271.90 -> £3,395,124.24 (10.2%); £3,780,272.17 -> £3,395,124.26 (10.2%); £3,780,272.44 -> £3,395,124.29 (10.2%); £3,780,272.70 -> £3,395,124.31 (10.2%); £3,780,272.97 -> £3,395,124.34 (10.2%); £3,780,273.24 -> £3,395,124.36 (10.2%); £3,780,273.49 -> £3,395,124.38 (10.2%); £3,780,273.76 -> £3,395,124.41 (10.2%); £3,780,274.02 -> £3,395,124.43 (10.2%); £3,780,274.30 -> £3,395,124.46 (10.2%); £3,780,274.57 -> £3,395,124.58 (10.2%); £3,780,274.83 -> £3,395,124.71 (10.2%); £3,780,275.09 -> £3,395,124.84 (10.2%); £3,780,275.35 -> £3,395,124.97 (10.2%); £3,780,275.62 -> £3,395,125.10 (10.2%); £3,780,275.88 -> £3,395,125.23 (10.2%); £3,780,276.15 -> £3,395,125.35 (10.2%); £3,780,276.42 -> £3,395,125.48 (10.2%); £3,780,276.68 -> £3,395,125.60 (10.2%); £3,780,276.95 -> £3,395,125.72 (10.2%); £3,780,277.21 -> £3,395,125.85 (10.2%); £3,780,277.48 -> £3,395,125.88 (10.2%); £3,780,277.75 -> £3,395,125.90 (10.2%); £3,780,278.00 -> £3,395,125.93 (10.2%); £3,780,278.23 -> £3,395,125.95 (10.2%); £3,780,278.44 -> £3,395,125.97 (10.2%); £3,780,278.57 -> £3,395,125.99 (10.2%); £3,780,278.71 -> £3,395,126.01 (10.2%); £3,780,278.85 -> £3,395,126.03 (10.2%); £3,780,278.99 -> £3,395,126.05 (10.2%); £3,780,279.13 -> £3,395,126.07 (10.2%); £3,780,279.27 -> £3,395,126.08 (10.2%); £3,780,279.41 -> £3,395,126.10 (10.2%); £3,780,279.55 -> £3,395,126.12 (10.2%); £3,780,279.69 -> £3,395,126.13 (10.2%); £3,780,279.83 -> £3,395,126.15 (10.2%); £3,780,279.97 -> £3,395,126.17 (10.2%); £3,780,280.11 -> £3,395,126.28 (10.2%); £3,780,280.25 -> £3,395,126.39 (10.2%); £3,780,280.40 -> £3,395,126.50 (10.2%); £3,780,280.58 -> £3,395,126.61 (10.2%); £3,780,280.76 -> £3,395,126.72 (10.2%); £3,780,280.96 -> £3,395,126.83 (10.2%); £3,780,281.18 -> £3,395,126.94 (10.2%); £3,780,281.40 -> £3,395,127.05 (10.2%); £3,780,281.64 -> £3,395,127.08 (10.2%); £3,780,281.88 -> £3,395,127.11 (10.2%); £3,780,282.11 -> £3,395,127.13 (10.2%); £3,780,282.34 -> £3,395,127.16 (10.2%); £3,780,282.57 -> £3,395,127.19 (10.2%); £3,780,282.80 -> £3,395,127.21 (10.2%); £3,780,283.04 -> £3,395,127.24 (10.2%); £3,780,283.27 -> £3,395,127.27 (10.2%); £3,780,283.50 -> £3,395,127.29 (10.2%); £3,780,283.73 -> £3,395,127.32 (10.2%); £3,780,283.96 -> £3,395,127.34 (10.2%); £3,780,284.19 -> £3,395,127.37 (10.2%); £3,780,284.43 -> £3,395,127.40 (10.2%); £3,780,284.66 -> £3,395,127.51 (10.2%); £3,780,284.84 -> £3,395,127.63 (10.2%); £3,780,285.08 -> £3,395,127.76 (10.2%); £3,780,285.25 -> £3,395,127.88 (10.2%); £3,780,285.42 -> £3,395,128.00 (10.2%); £3,780,285.60 -> £3,395,128.12 (10.2%); £3,780,285.77 -> £3,395,128.25 (10.2%); £3,780,286.00 -> £3,395,128.37 (10.2%); £3,780,286.23 -> £3,395,128.50 (10.2%); £3,780,286.47 -> £3,395,128.61 (10.2%); £3,780,286.69 -> £3,395,128.73 (10.2%); £3,780,286.92 -> £3,395,128.76 (10.2%); £3,780,287.15 -> £3,395,128.79 (10.2%); £3,780,287.37 -> £3,395,128.81 (10.2%); £3,780,287.56 -> £3,395,128.84 (10.2%); £3,780,287.74 -> £3,395,128.86 (10.2%); £3,780,287.88 -> £3,395,128.88 (10.2%); £3,780,288.02 -> £3,395,128.90 (10.2%); £3,780,288.16 -> £3,395,128.92 (10.2%); £3,780,288.30 -> £3,395,128.94 (10.2%); £3,780,288.44 -> £3,395,128.95 (10.2%); £3,780,288.58 -> £3,395,128.97 (10.2%); £3,780,288.72 -> £3,395,128.99 (10.2%); £3,780,288.86 -> £3,395,129.01 (10.2%); £3,780,289.00 -> £3,395,129.02 (10.2%); £3,780,289.14 -> £3,395,129.04 (10.2%); £3,780,289.28 -> £3,395,129.06 (10.2%); £3,780,289.42 -> £3,395,129.16 (10.2%); £3,780,289.56 -> £3,395,129.26 (10.2%); £3,780,289.72 -> £3,395,129.36 (10.2%); £3,780,289.88 -> £3,395,129.46 (10.2%); £3,780,290.07 -> £3,395,129.57 (10.2%); £3,780,290.27 -> £3,395,129.68 (10.2%); £3,780,290.50 -> £3,395,129.79 (10.2%); £3,780,290.73 -> £3,395,129.90 (10.2%); £3,780,290.96 -> £3,395,129.93 (10.2%); £3,780,291.19 -> £3,395,129.96 (10.2%); £3,780,291.43 -> £3,395,130.00 (10.2%); £3,780,291.67 -> £3,395,130.03 (10.2%); £3,780,291.90 -> £3,395,130.06 (10.2%); £3,780,292.14 -> £3,395,130.09 (10.2%); £3,780,292.38 -> £3,395,130.12 (10.2%); £3,780,292.62 -> £3,395,130.15 (10.2%); £3,780,292.85 -> £3,395,130.18 (10.2%); £3,780,293.09 -> £3,395,130.21 (10.2%); £3,780,293.33 -> £3,395,130.24 (10.2%); £3,780,293.56 -> £3,395,130.27 (10.2%); £3,780,293.80 -> £3,395,130.30 (10.2%); £3,780,294.03 -> £3,395,130.41 (10.2%); £3,780,294.26 -> £3,395,130.53 (10.2%); £3,780,294.43 -> £3,395,130.65 (10.2%); £3,780,294.60 -> £3,395,130.77 (10.2%); £3,780,294.78 -> £3,395,130.88 (10.2%); £3,780,294.96 -> £3,395,131.00 (10.2%); £3,780,295.14 -> £3,395,131.12 (10.2%); £3,780,295.38 -> £3,395,131.23 (10.2%); £3,780,295.61 -> £3,395,131.34 (10.2%); £3,780,295.84 -> £3,395,131.46 (10.2%); £3,780,296.07 -> £3,395,131.58 (10.2%); £3,780,296.31 -> £3,395,131.61 (10.2%); £3,780,296.55 -> £3,395,131.64 (10.2%); £3,780,296.77 -> £3,395,131.66 (10.2%); £3,780,296.97 -> £3,395,131.69 (10.2%); £3,780,297.15 -> £3,395,131.71 (10.2%); £3,780,297.31 -> £3,395,131.72 (10.2%); £3,780,297.47 -> £3,395,131.74 (10.2%); £3,780,297.64 -> £3,395,131.76 (10.2%); £3,780,297.80 -> £3,395,131.78 (10.2%); £3,780,297.95 -> £3,395,131.79 (10.2%); £3,780,298.12 -> £3,395,131.81 (10.2%); £3,780,298.28 -> £3,395,131.83 (10.2%); £3,780,298.45 -> £3,395,131.84 (10.2%); £3,780,298.62 -> £3,395,131.86 (10.2%); £3,780,298.78 -> £3,395,131.88 (10.2%); £3,780,298.94 -> £3,395,131.90 (10.2%); £3,780,299.11 -> £3,395,132.01 (10.2%); £3,780,299.27 -> £3,395,132.11 (10.2%); £3,780,299.45 -> £3,395,132.22 (10.2%); £3,780,299.66 -> £3,395,132.33 (10.2%); £3,780,299.88 -> £3,395,132.45 (10.2%); £3,780,300.12 -> £3,395,132.56 (10.2%); £3,780,300.36 -> £3,395,132.68 (10.2%); £3,780,300.63 -> £3,395,132.79 (10.2%); £3,780,300.90 -> £3,395,132.82 (10.2%); £3,780,301.18 -> £3,395,132.84 (10.2%); £3,780,301.46 -> £3,395,132.86 (10.2%); £3,780,301.73 -> £3,395,132.89 (10.2%); £3,780,302.00 -> £3,395,132.91 (10.2%); £3,780,302.26 -> £3,395,132.93 (10.2%); £3,780,302.53 -> £3,395,132.96 (10.2%); £3,780,302.80 -> £3,395,132.98 (10.2%); £3,780,303.07 -> £3,395,133.00 (10.2%); £3,780,303.33 -> £3,395,133.03 (10.2%); £3,780,303.61 -> £3,395,133.05 (10.2%); £3,780,303.89 -> £3,395,133.07 (10.2%); £3,780,304.15 -> £3,395,133.10 (10.2%); £3,780,304.36 -> £3,395,133.22 (10.2%); £3,780,304.56 -> £3,395,133.34 (10.2%); £3,780,304.76 -> £3,395,133.47 (10.2%); £3,780,304.96 -> £3,395,133.59 (10.2%); £3,780,305.17 -> £3,395,133.72 (10.2%); £3,780,305.45 -> £3,395,133.85 (10.2%); £3,780,305.72 -> £3,395,133.98 (10.2%); £3,780,306.00 -> £3,395,134.10 (10.2%); £3,780,306.27 -> £3,395,134.22 (10.2%); £3,780,306.54 -> £3,395,134.34 (10.2%); £3,780,306.81 -> £3,395,134.46 (10.2%); £3,780,307.09 -> £3,395,134.49 (10.2%); £3,780,307.35 -> £3,395,134.52 (10.2%); £3,780,307.61 -> £3,395,134.54 (10.2%); £3,780,307.84 -> £3,395,134.57 (10.2%); £3,780,308.06 -> £3,395,134.59 (10.2%); £3,780,308.22 -> £3,395,134.61 (10.2%); £3,780,308.39 -> £3,395,134.62 (10.2%); £3,780,308.56 -> £3,395,134.64 (10.2%); £3,780,308.72 -> £3,395,134.66 (10.2%); £3,780,308.90 -> £3,395,134.68 (10.2%); £3,780,309.06 -> £3,395,134.69 (10.2%); £3,780,309.22 -> £3,395,134.71 (10.2%); £3,780,309.39 -> £3,395,134.73 (10.2%); £3,780,309.55 -> £3,395,134.74 (10.2%); £3,780,309.72 -> £3,395,134.76 (10.2%); £3,780,309.89 -> £3,395,134.78 (10.2%); £3,780,310.05 -> £3,395,134.91 (10.2%); £3,780,310.22 -> £3,395,135.03 (10.2%); £3,780,310.40 -> £3,395,135.16 (10.2%); £3,780,310.61 -> £3,395,135.30 (10.2%); £3,780,310.82 -> £3,395,135.43 (10.2%); £3,780,311.06 -> £3,395,135.56 (10.2%); £3,780,311.32 -> £3,395,135.69 (10.2%); £3,780,311.59 -> £3,395,135.82 (10.2%); £3,780,311.86 -> £3,395,135.84 (10.2%); £3,780,312.14 -> £3,395,135.87 (10.2%); £3,780,312.42 -> £3,395,135.89 (10.2%); £3,780,312.69 -> £3,395,135.91 (10.2%); £3,780,312.97 -> £3,395,135.94 (10.2%); £3,780,313.24 -> £3,395,135.96 (10.2%); £3,780,313.51 -> £3,395,135.99 (10.2%); £3,780,313.79 -> £3,395,136.01 (10.2%); £3,780,314.06 -> £3,395,136.03 (10.2%); £3,780,314.33 -> £3,395,136.06 (10.2%); £3,780,314.60 -> £3,395,136.08 (10.2%); £3,780,314.86 -> £3,395,136.10 (10.2%); £3,780,315.14 -> £3,395,136.13 (10.2%); £3,780,315.35 -> £3,395,136.26 (10.2%); £3,780,315.56 -> £3,395,136.40 (10.2%); £3,780,315.76 -> £3,395,136.53 (10.2%); £3,780,315.97 -> £3,395,136.67 (10.2%); £3,780,316.17 -> £3,395,136.81 (10.2%); £3,780,316.37 -> £3,395,136.94 (10.2%); £3,780,316.58 -> £3,395,137.07 (10.2%); £3,780,316.86 -> £3,395,137.20 (10.2%); £3,780,317.13 -> £3,395,137.34 (10.2%); £3,780,317.40 -> £3,395,137.46 (10.2%); £3,780,317.68 -> £3,395,137.60 (10.2%); £3,780,317.95 -> £3,395,137.62 (10.2%); £3,780,318.22 -> £3,395,137.65 (10.2%); £3,780,318.47 -> £3,395,137.68 (10.2%); £3,780,318.70 -> £3,395,137.70 (10.2%); £3,780,318.91 -> £3,395,137.72 (10.2%); £3,780,319.08 -> £3,395,137.74 (10.2%); £3,780,319.25 -> £3,395,137.75 (10.2%); £3,780,319.41 -> £3,395,137.77 (10.2%); £3,780,319.56 -> £3,395,137.79 (10.2%); £3,780,319.73 -> £3,395,137.81 (10.2%); £3,780,319.90 -> £3,395,137.82 (10.2%); £3,780,320.07 -> £3,395,137.84 (10.2%); £3,780,320.23 -> £3,395,137.85 (10.2%); £3,780,320.40 -> £3,395,137.87 (10.2%); £3,780,320.57 -> £3,395,137.89 (10.2%); £3,780,320.73 -> £3,395,137.91 (10.2%); £3,780,320.90 -> £3,395,138.09 (10.2%); £3,780,321.06 -> £3,395,138.29 (10.2%); £3,780,321.24 -> £3,395,138.49 (10.2%); £3,780,321.45 -> £3,395,138.69 (10.2%); £3,780,321.67 -> £3,395,138.89 (10.2%); £3,780,321.92 -> £3,395,139.09 (10.2%); £3,780,322.17 -> £3,395,139.28 (10.2%); £3,780,322.45 -> £3,395,139.47 (10.2%); £3,780,322.74 -> £3,395,139.50 (10.2%); £3,780,323.02 -> £3,395,139.52 (10.2%); £3,780,323.29 -> £3,395,139.54 (10.2%); £3,780,323.57 -> £3,395,139.57 (10.2%); £3,780,323.85 -> £3,395,139.59 (10.2%); £3,780,324.13 -> £3,395,139.62 (10.2%); £3,780,324.39 -> £3,395,139.64 (10.2%); £3,780,324.67 -> £3,395,139.66 (10.2%); £3,780,324.94 -> £3,395,139.69 (10.2%); £3,780,325.22 -> £3,395,139.71 (10.2%); £3,780,325.49 -> £3,395,139.73 (10.2%); £3,780,325.77 -> £3,395,139.76 (10.2%); £3,780,326.04 -> £3,395,139.79 (10.2%); £3,780,326.25 -> £3,395,139.98 (10.2%); £3,780,326.46 -> £3,395,140.18 (10.2%); £3,780,326.74 -> £3,395,140.38 (10.2%); £3,780,326.94 -> £3,395,140.58 (10.2%); £3,780,327.14 -> £3,395,140.78 (10.2%); £3,780,327.35 -> £3,395,140.98 (10.2%); £3,780,327.62 -> £3,395,141.19 (10.2%); £3,780,327.90 -> £3,395,141.39 (10.2%); £3,780,328.16 -> £3,395,141.59 (10.2%); £3,780,328.43 -> £3,395,141.79 (10.2%); £3,780,328.70 -> £3,395,141.98 (10.2%); £3,780,328.99 -> £3,395,142.01 (10.2%); £3,780,329.27 -> £3,395,142.03 (10.2%); £3,780,329.53 -> £3,395,142.06 (10.2%); £3,780,329.76 -> £3,395,142.08 (10.2%); £3,780,329.98 -> £3,395,142.10 (10.2%); £3,780,330.15 -> £3,395,142.12 (10.2%); £3,780,330.31 -> £3,395,142.14 (10.2%); £3,780,330.47 -> £3,395,142.16 (10.2%); £3,780,330.64 -> £3,395,142.17 (10.2%); £3,780,330.81 -> £3,395,142.19 (10.2%); £3,780,330.98 -> £3,395,142.21 (10.2%); £3,780,331.14 -> £3,395,142.22 (10.2%); £3,780,331.30 -> £3,395,142.24 (10.2%); £3,780,331.47 -> £3,395,142.25 (10.2%); £3,780,331.63 -> £3,395,142.27 (10.2%); £3,780,331.79 -> £3,395,142.29 (10.2%); £3,780,331.96 -> £3,395,142.49 (10.2%); £3,780,332.12 -> £3,395,142.69 (10.2%); £3,780,332.31 -> £3,395,142.89 (10.2%); £3,780,332.51 -> £3,395,143.11 (10.2%); £3,780,332.73 -> £3,395,143.33 (10.2%); £3,780,332.97 -> £3,395,143.54 (10.2%); £3,780,333.23 -> £3,395,143.76 (10.2%); £3,780,333.51 -> £3,395,143.96 (10.2%); £3,780,333.78 -> £3,395,143.98 (10.2%); £3,780,334.06 -> £3,395,144.01 (10.2%); £3,780,334.33 -> £3,395,144.03 (10.2%); £3,780,334.61 -> £3,395,144.06 (10.2%); £3,780,334.88 -> £3,395,144.08 (10.2%); £3,780,335.15 -> £3,395,144.10 (10.2%); £3,780,335.43 -> £3,395,144.13 (10.2%); £3,780,335.71 -> £3,395,144.15 (10.2%); £3,780,335.97 -> £3,395,144.17 (10.2%); £3,780,336.25 -> £3,395,144.20 (10.2%); £3,780,336.52 -> £3,395,144.22 (10.2%); £3,780,336.79 -> £3,395,144.24 (10.2%); £3,780,337.07 -> £3,395,144.27 (10.2%); £3,780,337.27 -> £3,395,144.49 (10.2%); £3,780,337.55 -> £3,395,144.70 (10.2%); £3,780,337.76 -> £3,395,144.91 (10.2%); £3,780,338.03 -> £3,395,145.13 (10.2%); £3,780,338.30 -> £3,395,145.35 (10.2%); £3,780,338.57 -> £3,395,145.57 (10.2%); £3,780,338.84 -> £3,395,145.79 (10.2%); £3,780,339.12 -> £3,395,146.00 (10.2%); £3,780,339.40 -> £3,395,146.21 (10.2%); £3,780,339.67 -> £3,395,146.41 (10.2%); £3,780,339.95 -> £3,395,146.63 (10.2%); £3,780,340.23 -> £3,395,146.65 (10.2%); £3,780,340.51 -> £3,395,146.68 (10.2%); £3,780,340.76 -> £3,395,146.71 (10.2%); £3,780,341.00 -> £3,395,146.73 (10.2%); £3,780,341.21 -> £3,395,146.75 (10.2%); £3,780,341.38 -> £3,395,146.77 (10.2%); £3,780,341.54 -> £3,395,146.78 (10.2%); £3,780,341.70 -> £3,395,146.80 (10.2%); £3,780,341.87 -> £3,395,146.82 (10.2%); £3,780,342.03 -> £3,395,146.83 (10.2%); £3,780,342.19 -> £3,395,146.85 (10.2%); £3,780,342.36 -> £3,395,146.87 (10.2%); £3,780,342.52 -> £3,395,146.88 (10.2%); £3,780,342.68 -> £3,395,146.90 (10.2%); £3,780,342.85 -> £3,395,146.92 (10.2%); £3,780,343.01 -> £3,395,146.93 (10.2%); £3,780,343.19 -> £3,395,147.09 (10.2%); £3,780,343.35 -> £3,395,147.25 (10.2%); £3,780,343.53 -> £3,395,147.41 (10.2%); £3,780,343.73 -> £3,395,147.57 (10.2%); £3,780,343.95 -> £3,395,147.74 (10.2%); £3,780,344.17 -> £3,395,147.90 (10.2%); £3,780,344.43 -> £3,395,148.06 (10.2%); £3,780,344.70 -> £3,395,148.23 (10.2%); £3,780,344.97 -> £3,395,148.25 (10.2%); £3,780,345.24 -> £3,395,148.27 (10.2%); £3,780,345.51 -> £3,395,148.30 (10.2%); £3,780,345.78 -> £3,395,148.32 (10.2%); £3,780,346.05 -> £3,395,148.35 (10.2%); £3,780,346.31 -> £3,395,148.38 (10.2%); £3,780,346.58 -> £3,395,148.40 (10.2%); £3,780,346.84 -> £3,395,148.42 (10.2%); £3,780,347.12 -> £3,395,148.45 (10.2%); £3,780,347.40 -> £3,395,148.47 (10.2%); £3,780,347.67 -> £3,395,148.49 (10.2%); £3,780,347.94 -> £3,395,148.52 (10.2%); £3,780,348.21 -> £3,395,148.55 (10.2%); £3,780,348.48 -> £3,395,148.72 (10.2%); £3,780,348.75 -> £3,395,148.89 (10.2%); £3,780,349.03 -> £3,395,149.06 (10.2%); £3,780,349.31 -> £3,395,149.24 (10.2%); £3,780,349.58 -> £3,395,149.41 (10.2%); £3,780,349.78 -> £3,395,149.58 (10.2%); £3,780,349.99 -> £3,395,149.74 (10.2%); £3,780,350.26 -> £3,395,149.91 (10.2%); £3,780,350.52 -> £3,395,150.08 (10.2%); £3,780,350.79 -> £3,395,150.25 (10.2%); £3,780,351.06 -> £3,395,150.41 (10.2%); £3,780,351.34 -> £3,395,150.44 (10.2%); £3,780,351.60 -> £3,395,150.47 (10.2%); £3,780,351.85 -> £3,395,150.49 (10.2%); £3,780,352.09 -> £3,395,150.51 (10.2%); £3,780,352.30 -> £3,395,150.53 (10.2%); £3,780,352.45 -> £3,395,150.55 (10.2%); £3,780,352.59 -> £3,395,150.57 (10.2%); £3,780,352.73 -> £3,395,150.59 (10.2%); £3,780,352.88 -> £3,395,150.61 (10.2%); £3,780,353.02 -> £3,395,150.62 (10.2%); £3,780,353.16 -> £3,395,150.64 (10.2%); £3,780,353.30 -> £3,395,150.66 (10.2%); £3,780,353.44 -> £3,395,150.67 (10.2%); £3,780,353.58 -> £3,395,150.69 (10.2%); £3,780,353.72 -> £3,395,150.71 (10.2%); £3,780,353.87 -> £3,395,150.72 (10.2%); £3,780,354.01 -> £3,395,150.87 (10.2%); £3,780,354.16 -> £3,395,151.02 (10.2%); £3,780,354.32 -> £3,395,151.17 (10.2%); £3,780,354.50 -> £3,395,151.32 (10.2%); £3,780,354.69 -> £3,395,151.48 (10.2%); £3,780,354.90 -> £3,395,151.64 (10.2%); £3,780,355.11 -> £3,395,151.81 (10.2%); £3,780,355.35 -> £3,395,151.97 (10.2%); £3,780,355.59 -> £3,395,152.00 (10.2%); £3,780,355.83 -> £3,395,152.02 (10.2%); £3,780,356.07 -> £3,395,152.05 (10.2%); £3,780,356.31 -> £3,395,152.07 (10.2%); £3,780,356.55 -> £3,395,152.10 (10.2%); £3,780,356.78 -> £3,395,152.13 (10.2%); £3,780,357.02 -> £3,395,152.15 (10.2%); £3,780,357.26 -> £3,395,152.18 (10.2%); £3,780,357.49 -> £3,395,152.21 (10.2%); £3,780,357.74 -> £3,395,152.23 (10.2%); £3,780,357.98 -> £3,395,152.26 (10.2%); £3,780,358.21 -> £3,395,152.28 (10.2%); £3,780,358.46 -> £3,395,152.31 (10.2%); £3,780,358.70 -> £3,395,152.47 (10.2%); £3,780,358.93 -> £3,395,152.64 (10.2%); £3,780,359.16 -> £3,395,152.80 (10.2%); £3,780,359.34 -> £3,395,152.97 (10.2%); £3,780,359.58 -> £3,395,153.14 (10.2%); £3,780,359.76 -> £3,395,153.30 (10.2%); £3,780,359.94 -> £3,395,153.47 (10.2%); £3,780,360.19 -> £3,395,153.64 (10.2%); £3,780,360.43 -> £3,395,153.80 (10.2%); £3,780,360.67 -> £3,395,153.96 (10.2%); £3,780,360.91 -> £3,395,154.12 (10.2%); £3,780,361.15 -> £3,395,154.15 (10.2%); £3,780,361.39 -> £3,395,154.18 (10.2%); £3,780,361.61 -> £3,395,154.20 (10.2%); £3,780,361.81 -> £3,395,154.23 (10.2%); £3,780,362.00 -> £3,395,154.25 (10.2%); £3,780,362.15 -> £3,395,154.27 (10.2%); £3,780,362.29 -> £3,395,154.29 (10.2%); £3,780,362.42 -> £3,395,154.31 (10.2%); £3,780,362.56 -> £3,395,154.33 (10.2%); £3,780,362.70 -> £3,395,154.34 (10.2%); £3,780,362.85 -> £3,395,154.36 (10.2%); £3,780,362.99 -> £3,395,154.38 (10.2%); £3,780,363.13 -> £3,395,154.39 (10.2%); £3,780,363.27 -> £3,395,154.41 (10.2%); £3,780,363.41 -> £3,395,154.43 (10.2%); £3,780,363.55 -> £3,395,154.44 (10.2%); £3,780,363.69 -> £3,395,154.60 (10.2%); £3,780,363.82 -> £3,395,154.76 (10.2%); £3,780,363.97 -> £3,395,154.91 (10.2%); £3,780,364.14 -> £3,395,155.07 (10.2%); £3,780,364.33 -> £3,395,155.24 (10.2%); £3,780,364.53 -> £3,395,155.41 (10.2%); £3,780,364.75 -> £3,395,155.58 (10.2%); £3,780,364.99 -> £3,395,155.75 (10.2%); £3,780,365.23 -> £3,395,155.78 (10.2%); £3,780,365.47 -> £3,395,155.81 (10.2%); £3,780,365.70 -> £3,395,155.84 (10.2%); £3,780,365.93 -> £3,395,155.87 (10.2%); £3,780,366.17 -> £3,395,155.90 (10.2%); £3,780,366.41 -> £3,395,155.93 (10.2%); £3,780,366.64 -> £3,395,155.96 (10.2%); £3,780,366.88 -> £3,395,155.99 (10.2%); £3,780,367.11 -> £3,395,156.02 (10.2%); £3,780,367.34 -> £3,395,156.05 (10.2%); £3,780,367.57 -> £3,395,156.08 (10.2%); £3,780,367.80 -> £3,395,156.11 (10.2%); £3,780,368.04 -> £3,395,156.14 (10.2%); £3,780,368.28 -> £3,395,156.31 (10.2%); £3,780,368.51 -> £3,395,156.48 (10.2%); £3,780,368.69 -> £3,395,156.65 (10.2%); £3,780,368.86 -> £3,395,156.82 (10.2%); £3,780,369.04 -> £3,395,156.99 (10.2%); £3,780,369.21 -> £3,395,157.16 (10.2%); £3,780,369.39 -> £3,395,157.34 (10.2%); £3,780,369.63 -> £3,395,157.51 (10.2%); £3,780,369.86 -> £3,395,157.68 (10.2%); £3,780,370.09 -> £3,395,157.85 (10.2%); £3,780,370.33 -> £3,395,158.02 (10.2%); £3,780,370.56 -> £3,395,158.05 (10.2%); £3,780,370.79 -> £3,395,158.07 (10.2%); £3,780,371.01 -> £3,395,158.10 (10.2%); £3,780,371.22 -> £3,395,158.12 (10.2%); £3,780,371.40 -> £3,395,158.14 (10.2%); £3,780,371.55 -> £3,395,158.16 (10.2%); £3,780,371.71 -> £3,395,158.18 (10.2%); £3,780,371.86 -> £3,395,158.19 (10.2%); £3,780,372.02 -> £3,395,158.21 (10.2%); £3,780,372.18 -> £3,395,158.23 (10.2%); £3,780,372.33 -> £3,395,158.24 (10.2%); £3,780,372.49 -> £3,395,158.26 (10.2%); £3,780,372.64 -> £3,395,158.28 (10.2%); £3,780,372.79 -> £3,395,158.29 (10.2%); £3,780,372.95 -> £3,395,158.31 (10.2%); £3,780,373.11 -> £3,395,158.33 (10.2%); £3,780,373.26 -> £3,395,158.50 (10.2%); £3,780,373.41 -> £3,395,158.68 (10.2%); £3,780,373.59 -> £3,395,158.86 (10.2%); £3,780,373.78 -> £3,395,159.04 (10.2%); £3,780,374.00 -> £3,395,159.22 (10.2%); £3,780,374.22 -> £3,395,159.40 (10.2%); £3,780,374.46 -> £3,395,159.58 (10.2%); £3,780,374.72 -> £3,395,159.76 (10.2%); £3,780,374.97 -> £3,395,159.79 (10.2%); £3,780,375.23 -> £3,395,159.81 (10.2%); £3,780,375.49 -> £3,395,159.83 (10.2%); £3,780,375.75 -> £3,395,159.86 (10.2%); £3,780,376.01 -> £3,395,159.88 (10.2%); £3,780,376.27 -> £3,395,159.91 (10.2%); £3,780,376.53 -> £3,395,159.93 (10.2%); £3,780,376.78 -> £3,395,159.95 (10.2%); £3,780,377.05 -> £3,395,159.98 (10.2%); £3,780,377.30 -> £3,395,160.00 (10.2%); £3,780,377.56 -> £3,395,160.02 (10.2%); £3,780,377.82 -> £3,395,160.05 (10.2%); £3,780,378.09 -> £3,395,160.08 (10.2%); £3,780,378.28 -> £3,395,160.26 (10.2%); £3,780,378.47 -> £3,395,160.44 (10.2%); £3,780,378.67 -> £3,395,160.62 (10.2%); £3,780,378.86 -> £3,395,160.81 (10.2%); £3,780,379.06 -> £3,395,160.99 (10.2%); £3,780,379.24 -> £3,395,161.18 (10.2%); £3,780,379.44 -> £3,395,161.36 (10.2%); £3,780,379.71 -> £3,395,161.54 (10.2%); £3,780,379.96 -> £3,395,161.72 (10.2%); £3,780,380.22 -> £3,395,161.90 (10.2%); £3,780,380.48 -> £3,395,162.08 (10.2%); £3,780,380.74 -> £3,395,162.11 (10.2%); £3,780,381.00 -> £3,395,162.14 (10.2%); £3,780,381.24 -> £3,395,162.16 (10.2%); £3,780,381.46 -> £3,395,162.18 (10.2%); £3,780,381.66 -> £3,395,162.20 (10.2%); £3,780,381.82 -> £3,395,162.22 (10.2%); £3,780,381.98 -> £3,395,162.24 (10.2%); £3,780,382.14 -> £3,395,162.26 (10.2%); £3,780,382.30 -> £3,395,162.27 (10.2%); £3,780,382.45 -> £3,395,162.29 (10.2%); £3,780,382.60 -> £3,395,162.31 (10.2%); £3,780,382.76 -> £3,395,162.32 (10.2%); £3,780,382.91 -> £3,395,162.34 (10.2%); £3,780,383.07 -> £3,395,162.36 (10.2%); £3,780,383.22 -> £3,395,162.37 (10.2%); £3,780,383.38 -> £3,395,162.39 (10.2%); £3,780,383.54 -> £3,395,162.54 (10.2%); £3,780,383.70 -> £3,395,162.68 (10.2%); £3,780,383.87 -> £3,395,162.83 (10.2%); £3,780,384.06 -> £3,395,162.99 (10.2%); £3,780,384.28 -> £3,395,163.15 (10.2%); £3,780,384.50 -> £3,395,163.30 (10.2%); £3,780,384.74 -> £3,395,163.45 (10.2%); £3,780,384.99 -> £3,395,163.60 (10.2%); £3,780,385.25 -> £3,395,163.63 (10.2%); £3,780,385.51 -> £3,395,163.65 (10.2%); £3,780,385.77 -> £3,395,163.68 (10.2%); £3,780,386.02 -> £3,395,163.70 (10.2%); £3,780,386.29 -> £3,395,163.72 (10.2%); £3,780,386.55 -> £3,395,163.75 (10.2%); £3,780,386.81 -> £3,395,163.77 (10.2%); £3,780,387.08 -> £3,395,163.80 (10.2%); £3,780,387.33 -> £3,395,163.82 (10.2%); £3,780,387.59 -> £3,395,163.84 (10.2%); £3,780,387.85 -> £3,395,163.87 (10.2%); £3,780,388.11 -> £3,395,163.89 (10.2%); £3,780,388.37 -> £3,395,163.92 (10.2%); £3,780,388.62 -> £3,395,164.08 (10.2%); £3,780,388.88 -> £3,395,164.25 (10.2%); £3,780,389.14 -> £3,395,164.41 (10.2%); £3,780,389.40 -> £3,395,164.58 (10.2%); £3,780,389.66 -> £3,395,164.75 (10.2%); £3,780,389.91 -> £3,395,164.91 (10.2%); £3,780,390.17 -> £3,395,165.08 (10.2%); £3,780,390.43 -> £3,395,165.24 (10.2%); £3,780,390.69 -> £3,395,165.40 (10.2%); £3,780,390.95 -> £3,395,165.56 (10.2%); £3,780,391.21 -> £3,395,165.71 (10.2%); £3,780,391.48 -> £3,395,165.74 (10.2%); £3,780,391.74 -> £3,395,165.77 (10.2%); £3,780,391.98 -> £3,395,165.79 (10.2%); £3,780,392.20 -> £3,395,165.81 (10.2%); £3,780,392.40 -> £3,395,165.83 (10.2%); £3,780,392.55 -> £3,395,165.85 (10.2%); £3,780,392.71 -> £3,395,165.87 (10.2%); £3,780,392.86 -> £3,395,165.89 (10.2%); £3,780,393.02 -> £3,395,165.90 (10.2%); £3,780,393.17 -> £3,395,165.92 (10.2%); £3,780,393.32 -> £3,395,165.94 (10.2%); £3,780,393.47 -> £3,395,165.95 (10.2%); £3,780,393.63 -> £3,395,165.97 (10.2%); £3,780,393.78 -> £3,395,165.98 (10.2%); £3,780,393.94 -> £3,395,166.00 (10.2%); £3,780,394.10 -> £3,395,166.02 (10.2%); £3,780,394.26 -> £3,395,166.10 (10.2%); £3,780,394.42 -> £3,395,166.20 (10.2%); £3,780,394.59 -> £3,395,166.29 (10.2%); £3,780,394.79 -> £3,395,166.39 (10.2%); £3,780,395.00 -> £3,395,166.49 (10.2%); £3,780,395.22 -> £3,395,166.59 (10.2%); £3,780,395.46 -> £3,395,166.68 (10.2%); £3,780,395.72 -> £3,395,166.77 (10.2%); £3,780,395.98 -> £3,395,166.80 (10.2%); £3,780,396.24 -> £3,395,166.82 (10.2%); £3,780,396.50 -> £3,395,166.85 (10.2%); £3,780,396.75 -> £3,395,166.87 (10.2%); £3,780,397.02 -> £3,395,166.89 (10.2%); £3,780,397.26 -> £3,395,166.92 (10.2%); £3,780,397.51 -> £3,395,166.94 (10.2%); £3,780,397.78 -> £3,395,166.97 (10.2%); £3,780,398.03 -> £3,395,166.99 (10.2%); £3,780,398.29 -> £3,395,167.01 (10.2%); £3,780,398.56 -> £3,395,167.04 (10.2%); £3,780,398.81 -> £3,395,167.06 (10.2%); £3,780,399.08 -> £3,395,167.09 (10.2%); £3,780,399.34 -> £3,395,167.19 (10.2%); £3,780,399.53 -> £3,395,167.30 (10.2%); £3,780,399.72 -> £3,395,167.41 (10.2%); £3,780,399.91 -> £3,395,167.52 (10.2%); £3,780,400.17 -> £3,395,167.63 (10.2%); £3,780,400.43 -> £3,395,167.74 (10.2%); £3,780,400.68 -> £3,395,167.85 (10.2%); £3,780,400.95 -> £3,395,167.96 (10.2%); £3,780,401.21 -> £3,395,168.07 (10.2%); £3,780,401.48 -> £3,395,168.17 (10.2%); £3,780,401.74 -> £3,395,168.28 (10.2%); £3,780,401.98 -> £3,395,168.31 (10.2%); £3,780,402.25 -> £3,395,168.34 (10.2%); £3,780,402.49 -> £3,395,168.36 (10.2%); £3,780,402.71 -> £3,395,168.38 (10.2%); £3,780,402.91 -> £3,395,168.40 (10.2%); £3,780,403.07 -> £3,395,168.42 (10.2%); £3,780,403.22 -> £3,395,168.44 (10.2%); £3,780,403.37 -> £3,395,168.46 (10.2%); £3,780,403.53 -> £3,395,168.47 (10.2%); £3,780,403.69 -> £3,395,168.49 (10.2%); £3,780,403.84 -> £3,395,168.51 (10.2%); £3,780,404.00 -> £3,395,168.52 (10.2%); £3,780,404.16 -> £3,395,168.54 (10.2%); £3,780,404.32 -> £3,395,168.56 (10.2%); £3,780,404.48 -> £3,395,168.57 (10.2%); £3,780,404.64 -> £3,395,168.59 (10.2%); £3,780,404.79 -> £3,395,168.65 (10.2%); £3,780,404.95 -> £3,395,168.72 (10.2%); £3,780,405.12 -> £3,395,168.79 (10.2%); £3,780,405.31 -> £3,395,168.86 (10.2%); £3,780,405.52 -> £3,395,168.94 (10.2%); £3,780,405.75 -> £3,395,169.01 (10.2%); £3,780,405.99 -> £3,395,169.08 (10.2%); £3,780,406.25 -> £3,395,169.15 (10.2%); £3,780,406.53 -> £3,395,169.17 (10.2%); £3,780,406.79 -> £3,395,169.20 (10.2%); £3,780,407.05 -> £3,395,169.22 (10.2%); £3,780,407.32 -> £3,395,169.25 (10.2%); £3,780,407.58 -> £3,395,169.27 (10.2%); £3,780,407.84 -> £3,395,169.29 (10.2%); £3,780,408.10 -> £3,395,169.32 (10.2%); £3,780,408.36 -> £3,395,169.34 (10.2%); £3,780,408.63 -> £3,395,169.36 (10.2%); £3,780,408.88 -> £3,395,169.39 (10.2%); £3,780,409.13 -> £3,395,169.41 (10.2%); £3,780,409.39 -> £3,395,169.44 (10.2%); £3,780,409.66 -> £3,395,169.47 (10.2%); £3,780,409.91 -> £3,395,169.55 (10.2%); £3,780,410.18 -> £3,395,169.64 (10.2%); £3,780,410.44 -> £3,395,169.73 (10.2%); £3,780,410.69 -> £3,395,169.82 (10.2%); £3,780,410.96 -> £3,395,169.91 (10.2%); £3,780,411.22 -> £3,395,170.00 (10.2%); £3,780,411.48 -> £3,395,170.08 (10.2%); £3,780,411.74 -> £3,395,170.17 (10.2%); £3,780,412.00 -> £3,395,170.25 (10.2%); £3,780,412.25 -> £3,395,170.33 (10.2%); £3,780,412.50 -> £3,395,170.41 (10.2%); £3,780,412.76 -> £3,395,170.44 (10.2%); £3,780,413.02 -> £3,395,170.47 (10.2%); £3,780,413.26 -> £3,395,170.49 (10.2%); £3,780,413.48 -> £3,395,170.51 (10.2%); £3,780,413.68 -> £3,395,170.53 (10.2%); £3,780,413.84 -> £3,395,170.55 (10.2%); £3,780,414.00 -> £3,395,170.57 (10.2%); £3,780,414.15 -> £3,395,170.59 (10.2%); £3,780,414.31 -> £3,395,170.60 (10.2%); £3,780,414.47 -> £3,395,170.62 (10.2%); £3,780,414.63 -> £3,395,170.64 (10.2%); £3,780,414.78 -> £3,395,170.65 (10.2%); £3,780,414.94 -> £3,395,170.67 (10.2%); £3,780,415.10 -> £3,395,170.69 (10.2%); £3,780,415.26 -> £3,395,170.70 (10.2%); £3,780,415.42 -> £3,395,170.72 (10.2%); £3,780,415.58 -> £3,395,170.82 (10.2%); £3,780,415.74 -> £3,395,170.93 (10.2%); £3,780,415.92 -> £3,395,171.04 (10.2%); £3,780,416.11 -> £3,395,171.15 (10.2%); £3,780,416.32 -> £3,395,171.26 (10.2%); £3,780,416.55 -> £3,395,171.37 (10.2%); £3,780,416.80 -> £3,395,171.48 (10.2%); £3,780,417.06 -> £3,395,171.58 (10.2%); £3,780,417.32 -> £3,395,171.61 (10.2%); £3,780,417.59 -> £3,395,171.63 (10.2%); £3,780,417.85 -> £3,395,171.66 (10.2%); £3,780,418.10 -> £3,395,171.68 (10.2%); £3,780,418.36 -> £3,395,171.70 (10.2%); £3,780,418.63 -> £3,395,171.73 (10.2%); £3,780,418.88 -> £3,395,171.75 (10.2%); £3,780,419.14 -> £3,395,171.77 (10.2%); £3,780,419.40 -> £3,395,171.80 (10.2%); £3,780,419.66 -> £3,395,171.82 (10.2%); £3,780,419.92 -> £3,395,171.84 (10.2%); £3,780,420.19 -> £3,395,171.87 (10.2%); £3,780,420.44 -> £3,395,171.90 (10.2%); £3,780,420.64 -> £3,395,172.01 (10.2%); £3,780,420.92 -> £3,395,172.13 (10.2%); £3,780,421.11 -> £3,395,172.26 (10.2%); £3,780,421.30 -> £3,395,172.38 (10.2%); £3,780,421.50 -> £3,395,172.50 (10.2%); £3,780,421.69 -> £3,395,172.61 (10.2%); £3,780,421.88 -> £3,395,172.73 (10.2%); £3,780,422.14 -> £3,395,172.85 (10.2%); £3,780,422.40 -> £3,395,172.96 (10.2%); £3,780,422.66 -> £3,395,173.08 (10.2%); £3,780,422.93 -> £3,395,173.20 (10.2%); £3,780,423.19 -> £3,395,173.23 (10.2%); £3,780,423.47 -> £3,395,173.26 (10.2%); £3,780,423.71 -> £3,395,173.28 (10.2%); £3,780,423.92 -> £3,395,173.30 (10.2%); £3,780,424.12 -> £3,395,173.32 (10.2%); £3,780,424.26 -> £3,395,173.34 (10.2%); £3,780,424.40 -> £3,395,173.36 (10.2%); £3,780,424.54 -> £3,395,173.38 (10.2%); £3,780,424.68 -> £3,395,173.40 (10.2%); £3,780,424.82 -> £3,395,173.41 (10.2%); £3,780,424.95 -> £3,395,173.43 (10.2%); £3,780,425.09 -> £3,395,173.45 (10.2%); £3,780,425.24 -> £3,395,173.46 (10.2%); £3,780,425.37 -> £3,395,173.48 (10.2%); £3,780,425.50 -> £3,395,173.50 (10.2%); £3,780,425.64 -> £3,395,173.52 (10.2%); £3,780,425.78 -> £3,395,173.60 (10.2%); £3,780,425.92 -> £3,395,173.69 (10.2%); £3,780,426.08 -> £3,395,173.78 (10.2%); £3,780,426.24 -> £3,395,173.88 (10.2%); £3,780,426.43 -> £3,395,173.97 (10.2%); £3,780,426.63 -> £3,395,174.07 (10.2%); £3,780,426.84 -> £3,395,174.17 (10.2%); £3,780,427.06 -> £3,395,174.27 (10.2%); £3,780,427.29 -> £3,395,174.29 (10.2%); £3,780,427.51 -> £3,395,174.32 (10.2%); £3,780,427.73 -> £3,395,174.35 (10.2%); £3,780,427.96 -> £3,395,174.37 (10.2%); £3,780,428.20 -> £3,395,174.40 (10.2%); £3,780,428.43 -> £3,395,174.43 (10.2%); £3,780,428.65 -> £3,395,174.45 (10.2%); £3,780,428.88 -> £3,395,174.48 (10.2%); £3,780,429.10 -> £3,395,174.50 (10.2%); £3,780,429.33 -> £3,395,174.53 (10.2%); £3,780,429.56 -> £3,395,174.55 (10.2%); £3,780,429.79 -> £3,395,174.58 (10.2%); £3,780,430.01 -> £3,395,174.61 (10.2%); £3,780,430.18 -> £3,395,174.71 (10.2%); £3,780,430.35 -> £3,395,174.82 (10.2%); £3,780,430.52 -> £3,395,174.93 (10.2%); £3,780,430.70 -> £3,395,175.04 (10.2%); £3,780,430.87 -> £3,395,175.15 (10.2%); £3,780,431.04 -> £3,395,175.26 (10.2%); £3,780,431.21 -> £3,395,175.37 (10.2%); £3,780,431.44 -> £3,395,175.47 (10.2%); £3,780,431.67 -> £3,395,175.58 (10.2%); £3,780,431.90 -> £3,395,175.68 (10.2%); £3,780,432.13 -> £3,395,175.78 (10.2%); £3,780,432.35 -> £3,395,175.81 (10.2%); £3,780,432.58 -> £3,395,175.84 (10.2%); £3,780,432.79 -> £3,395,175.86 (10.2%); £3,780,432.99 -> £3,395,175.89 (10.2%); £3,780,433.16 -> £3,395,175.91 (10.2%); £3,780,433.30 -> £3,395,175.93 (10.2%); £3,780,433.44 -> £3,395,175.95 (10.2%); £3,780,433.58 -> £3,395,175.97 (10.2%); £3,780,433.71 -> £3,395,175.98 (10.2%); £3,780,433.85 -> £3,395,176.00 (10.2%); £3,780,433.99 -> £3,395,176.02 (10.2%); £3,780,434.13 -> £3,395,176.04 (10.2%); £3,780,434.27 -> £3,395,176.05 (10.2%); £3,780,434.41 -> £3,395,176.07 (10.2%); £3,780,434.55 -> £3,395,176.09 (10.2%); £3,780,434.68 -> £3,395,176.10 (10.2%); £3,780,434.81 -> £3,395,176.19 (10.2%); £3,780,434.95 -> £3,395,176.28 (10.2%); £3,780,435.11 -> £3,395,176.37 (10.2%); £3,780,435.28 -> £3,395,176.46 (10.2%); £3,780,435.47 -> £3,395,176.56 (10.2%); £3,780,435.66 -> £3,395,176.65 (10.2%); £3,780,435.88 -> £3,395,176.75 (10.2%); £3,780,436.10 -> £3,395,176.86 (10.2%); £3,780,436.33 -> £3,395,176.89 (10.2%); £3,780,436.56 -> £3,395,176.92 (10.2%); £3,780,436.79 -> £3,395,176.95 (10.2%); £3,780,437.03 -> £3,395,176.98 (10.2%); £3,780,437.25 -> £3,395,177.01 (10.2%); £3,780,437.48 -> £3,395,177.04 (10.2%); £3,780,437.71 -> £3,395,177.07 (10.2%); £3,780,437.94 -> £3,395,177.11 (10.2%); £3,780,438.17 -> £3,395,177.13 (10.2%); £3,780,438.40 -> £3,395,177.16 (10.2%); £3,780,438.64 -> £3,395,177.19 (10.2%); £3,780,438.87 -> £3,395,177.22 (10.2%); £3,780,439.09 -> £3,395,177.25 (10.2%); £3,780,439.33 -> £3,395,177.36 (10.2%); £3,780,439.57 -> £3,395,177.48 (10.2%); £3,780,439.79 -> £3,395,177.59 (10.2%); £3,780,439.96 -> £3,395,177.70 (10.2%); £3,780,440.19 -> £3,395,177.82 (10.2%); £3,780,440.36 -> £3,395,177.93 (10.2%); £3,780,440.53 -> £3,395,178.04 (10.2%); £3,780,440.76 -> £3,395,178.15 (10.2%); £3,780,440.99 -> £3,395,178.26 (10.2%); £3,780,441.22 -> £3,395,178.37 (10.2%); £3,780,441.45 -> £3,395,178.48 (10.2%); £3,780,441.67 -> £3,395,178.51 (10.2%); £3,780,441.90 -> £3,395,178.54 (10.2%); £3,780,442.10 -> £3,395,178.56 (10.2%); £3,780,442.30 -> £3,395,178.59 (10.2%); £3,780,442.47 -> £3,395,178.61 (10.2%); £3,780,442.63 -> £3,395,178.63 (10.2%); £3,780,442.80 -> £3,395,178.64 (10.2%); £3,780,442.96 -> £3,395,178.66 (10.2%); £3,780,443.12 -> £3,395,178.68 (10.2%); £3,780,443.28 -> £3,395,178.70 (10.2%); £3,780,443.44 -> £3,395,178.71 (10.2%); £3,780,443.59 -> £3,395,178.73 (10.2%); £3,780,443.76 -> £3,395,178.75 (10.2%); £3,780,443.91 -> £3,395,178.76 (10.2%); £3,780,444.07 -> £3,395,178.78 (10.2%); £3,780,444.23 -> £3,395,178.80 (10.2%); £3,780,444.40 -> £3,395,178.92 (10.2%); £3,780,444.56 -> £3,395,179.04 (10.2%); £3,780,444.73 -> £3,395,179.17 (10.2%); £3,780,444.92 -> £3,395,179.30 (10.2%); £3,780,445.13 -> £3,395,179.43 (10.2%); £3,780,445.36 -> £3,395,179.56 (10.2%); £3,780,445.61 -> £3,395,179.68 (10.2%); £3,780,445.86 -> £3,395,179.81 (10.2%); £3,780,446.12 -> £3,395,179.83 (10.2%); £3,780,446.38 -> £3,395,179.86 (10.2%); £3,780,446.65 -> £3,395,179.88 (10.2%); £3,780,446.91 -> £3,395,179.91 (10.2%); £3,780,447.18 -> £3,395,179.93 (10.2%); £3,780,447.45 -> £3,395,179.96 (10.2%); £3,780,447.71 -> £3,395,179.98 (10.2%); £3,780,447.98 -> £3,395,180.00 (10.2%); £3,780,448.25 -> £3,395,180.02 (10.2%); £3,780,448.52 -> £3,395,180.05 (10.2%); £3,780,448.78 -> £3,395,180.07 (10.2%); £3,780,449.04 -> £3,395,180.10 (10.2%); £3,780,449.30 -> £3,395,180.13 (10.2%); £3,780,449.56 -> £3,395,180.26 (10.2%); £3,780,449.75 -> £3,395,180.40 (10.2%); £3,780,449.95 -> £3,395,180.54 (10.2%); £3,780,450.15 -> £3,395,180.68 (10.2%); £3,780,450.41 -> £3,395,180.83 (10.2%); £3,780,450.66 -> £3,395,180.97 (10.2%); £3,780,450.93 -> £3,395,181.11 (10.2%); £3,780,451.20 -> £3,395,181.24 (10.2%); £3,780,451.46 -> £3,395,181.38 (10.2%); £3,780,451.73 -> £3,395,181.52 (10.2%); £3,780,451.99 -> £3,395,181.65 (10.2%); £3,780,452.26 -> £3,395,181.68 (10.2%); £3,780,452.52 -> £3,395,181.71 (10.2%); £3,780,452.78 -> £3,395,181.74 (10.2%); £3,780,453.00 -> £3,395,181.76 (10.2%); £3,780,453.20 -> £3,395,181.78 (10.2%); £3,780,453.36 -> £3,395,181.80 (10.2%); £3,780,453.52 -> £3,395,181.81 (10.2%); £3,780,453.68 -> £3,395,181.83 (10.2%); £3,780,453.84 -> £3,395,181.85 (10.2%); £3,780,453.99 -> £3,395,181.86 (10.2%); £3,780,454.15 -> £3,395,181.88 (10.2%); £3,780,454.31 -> £3,395,181.90 (10.2%); £3,780,454.47 -> £3,395,181.91 (10.2%); £3,780,454.63 -> £3,395,181.93 (10.2%); £3,780,454.79 -> £3,395,181.95 (10.2%); £3,780,454.95 -> £3,395,181.96 (10.2%); £3,780,455.10 -> £3,395,182.08 (10.2%); £3,780,455.26 -> £3,395,182.19 (10.2%); £3,780,455.43 -> £3,395,182.31 (10.2%); £3,780,455.63 -> £3,395,182.44 (10.2%); £3,780,455.84 -> £3,395,182.56 (10.2%); £3,780,456.07 -> £3,395,182.68 (10.2%); £3,780,456.32 -> £3,395,182.80 (10.2%); £3,780,456.58 -> £3,395,182.92 (10.2%); £3,780,456.85 -> £3,395,182.95 (10.2%); £3,780,457.11 -> £3,395,182.97 (10.2%); £3,780,457.39 -> £3,395,182.99 (10.2%); £3,780,457.65 -> £3,395,183.02 (10.2%); £3,780,457.91 -> £3,395,183.04 (10.2%); £3,780,458.17 -> £3,395,183.07 (10.2%); £3,780,458.43 -> £3,395,183.09 (10.2%); £3,780,458.70 -> £3,395,183.12 (10.2%); £3,780,458.96 -> £3,395,183.14 (10.2%); £3,780,459.22 -> £3,395,183.16 (10.2%); £3,780,459.49 -> £3,395,183.19 (10.2%); £3,780,459.76 -> £3,395,183.21 (10.2%); £3,780,460.02 -> £3,395,183.24 (10.2%); £3,780,460.29 -> £3,395,183.37 (10.2%); £3,780,460.55 -> £3,395,183.51 (10.2%); £3,780,460.81 -> £3,395,183.65 (10.2%); £3,780,461.08 -> £3,395,183.78 (10.2%); £3,780,461.34 -> £3,395,183.92 (10.2%); £3,780,461.61 -> £3,395,184.05 (10.2%); £3,780,461.81 -> £3,395,184.18 (10.2%); £3,780,462.06 -> £3,395,184.31 (10.2%); £3,780,462.32 -> £3,395,184.44 (10.2%); £3,780,462.58 -> £3,395,184.57 (10.2%); £3,780,462.86 -> £3,395,184.70 (10.2%); £3,780,463.12 -> £3,395,184.73 (10.2%); £3,780,463.38 -> £3,395,184.76 (10.2%); £3,780,463.63 -> £3,395,184.78 (10.2%); £3,780,463.85 -> £3,395,184.81 (10.2%); £3,780,464.05 -> £3,395,184.83 (10.2%); £3,780,464.22 -> £3,395,184.84 (10.2%); £3,780,464.38 -> £3,395,184.86 (10.2%); £3,780,464.54 -> £3,395,184.88 (10.2%); £3,780,464.70 -> £3,395,184.90 (10.2%); £3,780,464.87 -> £3,395,184.91 (10.2%); £3,780,465.02 -> £3,395,184.93 (10.2%); £3,780,465.19 -> £3,395,184.95 (10.2%); £3,780,465.35 -> £3,395,184.96 (10.2%); £3,780,465.50 -> £3,395,184.98 (10.2%); £3,780,465.67 -> £3,395,185.00 (10.2%); £3,780,465.83 -> £3,395,185.01 (10.2%); £3,780,465.99 -> £3,395,185.13 (10.2%); £3,780,466.15 -> £3,395,185.23 (10.2%); £3,780,466.33 -> £3,395,185.35 (10.2%); £3,780,466.53 -> £3,395,185.46 (10.2%); £3,780,466.74 -> £3,395,185.58 (10.2%); £3,780,466.96 -> £3,395,185.70 (10.2%); £3,780,467.21 -> £3,395,185.81 (10.2%); £3,780,467.48 -> £3,395,185.92 (10.2%); £3,780,467.75 -> £3,395,185.95 (10.2%); £3,780,468.01 -> £3,395,185.97 (10.2%); £3,780,468.28 -> £3,395,185.99 (10.2%); £3,780,468.55 -> £3,395,186.02 (10.2%); £3,780,468.81 -> £3,395,186.04 (10.2%); £3,780,469.07 -> £3,395,186.07 (10.2%); £3,780,469.35 -> £3,395,186.09 (10.2%); £3,780,469.62 -> £3,395,186.11 (10.2%); £3,780,469.89 -> £3,395,186.14 (10.2%); £3,780,470.15 -> £3,395,186.16 (10.2%); £3,780,470.42 -> £3,395,186.18 (10.2%); £3,780,470.69 -> £3,395,186.21 (10.2%); £3,780,470.96 -> £3,395,186.24 (10.2%); £3,780,471.22 -> £3,395,186.36 (10.2%); £3,780,471.49 -> £3,395,186.48 (10.2%); £3,780,471.75 -> £3,395,186.61 (10.2%); £3,780,472.02 -> £3,395,186.74 (10.2%); £3,780,472.22 -> £3,395,186.87 (10.2%); £3,780,472.42 -> £3,395,186.99 (10.2%); £3,780,472.69 -> £3,395,187.12 (10.2%); £3,780,472.95 -> £3,395,187.24 (10.2%); £3,780,473.21 -> £3,395,187.37 (10.2%); £3,780,473.48 -> £3,395,187.49 (10.2%); £3,780,473.75 -> £3,395,187.62 (10.2%); £3,780,474.02 -> £3,395,187.65 (10.2%); £3,780,474.28 -> £3,395,187.68 (10.2%); £3,780,474.53 -> £3,395,187.70 (10.2%); £3,780,474.76 -> £3,395,187.72 (10.2%); £3,780,474.96 -> £3,395,187.74 (10.2%); £3,780,475.12 -> £3,395,187.76 (10.2%); £3,780,475.27 -> £3,395,187.78 (10.2%); £3,780,475.43 -> £3,395,187.80 (10.2%); £3,780,475.59 -> £3,395,187.81 (10.2%); £3,780,475.76 -> £3,395,187.83 (10.2%); £3,780,475.92 -> £3,395,187.85 (10.2%); £3,780,476.08 -> £3,395,187.86 (10.2%); £3,780,476.25 -> £3,395,187.88 (10.2%); £3,780,476.41 -> £3,395,187.90 (10.2%); £3,780,476.57 -> £3,395,187.91 (10.2%); £3,780,476.73 -> £3,395,187.93 (10.2%); £3,780,476.89 -> £3,395,188.08 (10.2%); £3,780,477.04 -> £3,395,188.22 (10.2%); £3,780,477.23 -> £3,395,188.37 (10.2%); £3,780,477.42 -> £3,395,188.53 (10.2%); £3,780,477.64 -> £3,395,188.68 (10.2%); £3,780,477.87 -> £3,395,188.83 (10.2%); £3,780,478.13 -> £3,395,188.98 (10.2%); £3,780,478.39 -> £3,395,189.13 (10.2%); £3,780,478.66 -> £3,395,189.15 (10.2%); £3,780,478.93 -> £3,395,189.17 (10.2%); £3,780,479.19 -> £3,395,189.20 (10.2%); £3,780,479.46 -> £3,395,189.22 (10.2%); £3,780,479.71 -> £3,395,189.25 (10.2%); £3,780,479.99 -> £3,395,189.27 (10.2%); £3,780,480.27 -> £3,395,189.29 (10.2%); £3,780,480.54 -> £3,395,189.31 (10.2%); £3,780,480.80 -> £3,395,189.34 (10.2%); £3,780,481.06 -> £3,395,189.36 (10.2%); £3,780,481.33 -> £3,395,189.38 (10.2%); £3,780,481.59 -> £3,395,189.41 (10.2%); £3,780,481.87 -> £3,395,189.44 (10.2%); £3,780,482.14 -> £3,395,189.60 (10.2%); £3,780,482.41 -> £3,395,189.77 (10.2%); £3,780,482.68 -> £3,395,189.93 (10.2%); £3,780,482.95 -> £3,395,190.09 (10.2%); £3,780,483.15 -> £3,395,190.26 (10.2%); £3,780,483.42 -> £3,395,190.43 (10.2%); £3,780,483.69 -> £3,395,190.59 (10.2%); £3,780,483.96 -> £3,395,190.75 (10.2%); £3,780,484.23 -> £3,395,190.91 (10.2%); £3,780,484.51 -> £3,395,191.07 (10.2%); £3,780,484.77 -> £3,395,191.22 (10.2%); £3,780,485.03 -> £3,395,191.25 (10.2%); £3,780,485.30 -> £3,395,191.28 (10.2%); £3,780,485.54 -> £3,395,191.30 (10.2%); £3,780,485.77 -> £3,395,191.32 (10.2%); £3,780,485.98 -> £3,395,191.34 (10.2%); £3,780,486.14 -> £3,395,191.36 (10.2%); £3,780,486.30 -> £3,395,191.38 (10.2%); £3,780,486.46 -> £3,395,191.40 (10.2%); £3,780,486.62 -> £3,395,191.41 (10.2%); £3,780,486.78 -> £3,395,191.43 (10.2%); £3,780,486.94 -> £3,395,191.45 (10.2%); £3,780,487.10 -> £3,395,191.46 (10.2%); £3,780,487.26 -> £3,395,191.48 (10.2%); £3,780,487.43 -> £3,395,191.50 (10.2%); £3,780,487.59 -> £3,395,191.51 (10.2%); £3,780,487.75 -> £3,395,191.53 (10.2%); £3,780,487.91 -> £3,395,191.71 (10.2%); £3,780,488.06 -> £3,395,191.90 (10.2%); £3,780,488.24 -> £3,395,192.10 (10.2%); £3,780,488.44 -> £3,395,192.30 (10.2%); £3,780,488.65 -> £3,395,192.50 (10.2%); £3,780,488.88 -> £3,395,192.70 (10.2%); £3,780,489.13 -> £3,395,192.89 (10.2%); £3,780,489.41 -> £3,395,193.09 (10.2%); £3,780,489.66 -> £3,395,193.11 (10.2%); £3,780,489.93 -> £3,395,193.14 (10.2%); £3,780,490.18 -> £3,395,193.16 (10.2%); £3,780,490.44 -> £3,395,193.18 (10.2%); £3,780,490.70 -> £3,395,193.21 (10.2%); £3,780,490.97 -> £3,395,193.23 (10.2%); £3,780,491.22 -> £3,395,193.26 (10.2%); £3,780,491.50 -> £3,395,193.28 (10.2%); £3,780,491.77 -> £3,395,193.30 (10.2%); £3,780,492.03 -> £3,395,193.33 (10.2%); £3,780,492.30 -> £3,395,193.35 (10.2%); £3,780,492.57 -> £3,395,193.37 (10.2%); £3,780,492.83 -> £3,395,193.40 (10.2%); £3,780,493.09 -> £3,395,193.60 (10.2%); £3,780,493.35 -> £3,395,193.80 (10.2%); £3,780,493.55 -> £3,395,194.00 (10.2%); £3,780,493.75 -> £3,395,194.19 (10.2%); £3,780,493.95 -> £3,395,194.39 (10.2%); £3,780,494.15 -> £3,395,194.59 (10.2%); £3,780,494.35 -> £3,395,194.78 (10.2%); £3,780,494.62 -> £3,395,194.97 (10.2%); £3,780,494.88 -> £3,395,195.16 (10.2%); £3,780,495.16 -> £3,395,195.36 (10.2%); £3,780,495.41 -> £3,395,195.55 (10.2%); £3,780,495.69 -> £3,395,195.58 (10.2%); £3,780,495.95 -> £3,395,195.60 (10.2%); £3,780,496.19 -> £3,395,195.63 (10.2%); £3,780,496.41 -> £3,395,195.65 (10.2%); £3,780,496.61 -> £3,395,195.67 (10.2%); £3,780,496.75 -> £3,395,195.69 (10.2%); £3,780,496.89 -> £3,395,195.71 (10.2%); £3,780,497.03 -> £3,395,195.73 (10.2%); £3,780,497.17 -> £3,395,195.74 (10.2%); £3,780,497.32 -> £3,395,195.76 (10.2%); £3,780,497.45 -> £3,395,195.78 (10.2%); £3,780,497.60 -> £3,395,195.79 (10.2%); £3,780,497.74 -> £3,395,195.81 (10.2%); £3,780,497.87 -> £3,395,195.83 (10.2%); £3,780,498.01 -> £3,395,195.84 (10.2%); £3,780,498.16 -> £3,395,195.86 (10.2%); £3,780,498.30 -> £3,395,196.06 (10.2%); £3,780,498.44 -> £3,395,196.26 (10.2%); £3,780,498.59 -> £3,395,196.47 (10.2%); £3,780,498.77 -> £3,395,196.67 (10.2%); £3,780,498.96 -> £3,395,196.87 (10.2%); £3,780,499.16 -> £3,395,197.08 (10.2%); £3,780,499.39 -> £3,395,197.29 (10.2%); £3,780,499.62 -> £3,395,197.49 (10.2%); £3,780,499.86 -> £3,395,197.52 (10.2%); £3,780,500.09 -> £3,395,197.55 (10.2%); £3,780,500.32 -> £3,395,197.57 (10.2%); £3,780,500.56 -> £3,395,197.60 (10.2%); £3,780,500.79 -> £3,395,197.63 (10.2%); £3,780,501.02 -> £3,395,197.65 (10.2%); £3,780,501.25 -> £3,395,197.68 (10.2%); £3,780,501.48 -> £3,395,197.70 (10.2%); £3,780,501.73 -> £3,395,197.73 (10.2%); £3,780,501.96 -> £3,395,197.76 (10.2%); £3,780,502.20 -> £3,395,197.78 (10.2%); £3,780,502.45 -> £3,395,197.81 (10.2%); £3,780,502.68 -> £3,395,197.83 (10.2%); £3,780,502.86 -> £3,395,198.03 (10.2%); £3,780,503.03 -> £3,395,198.24 (10.2%); £3,780,503.20 -> £3,395,198.45 (10.2%); £3,780,503.38 -> £3,395,198.65 (10.2%); £3,780,503.55 -> £3,395,198.86 (10.2%); £3,780,503.73 -> £3,395,199.06 (10.2%); £3,780,503.91 -> £3,395,199.27 (10.2%); £3,780,504.15 -> £3,395,199.47 (10.2%); £3,780,504.39 -> £3,395,199.67 (10.2%); £3,780,504.62 -> £3,395,199.87 (10.2%); £3,780,504.86 -> £3,395,200.07 (10.2%); £3,780,505.09 -> £3,395,200.10 (10.2%); £3,780,505.33 -> £3,395,200.13 (10.2%); £3,780,505.54 -> £3,395,200.15 (10.2%); £3,780,505.74 -> £3,395,200.18 (10.2%); £3,780,505.93 -> £3,395,200.20 (10.2%); £3,780,506.07 -> £3,395,200.22 (10.2%); £3,780,506.22 -> £3,395,200.24 (10.2%); £3,780,506.35 -> £3,395,200.26 (10.2%); £3,780,506.49 -> £3,395,200.27 (10.2%); £3,780,506.63 -> £3,395,200.29 (10.2%); £3,780,506.77 -> £3,395,200.31 (10.2%); £3,780,506.91 -> £3,395,200.32 (10.2%); £3,780,507.05 -> £3,395,200.34 (10.2%); £3,780,507.19 -> £3,395,200.36 (10.2%); £3,780,507.33 -> £3,395,200.37 (10.2%); £3,780,507.47 -> £3,395,200.39 (10.2%); £3,780,507.61 -> £3,395,200.57 (10.2%); £3,780,507.75 -> £3,395,200.75 (10.2%); £3,780,507.90 -> £3,395,200.94 (10.2%); £3,780,508.08 -> £3,395,201.12 (10.2%); £3,780,508.27 -> £3,395,201.31 (10.2%); £3,780,508.46 -> £3,395,201.51 (10.2%); £3,780,508.68 -> £3,395,201.70 (10.2%); £3,780,508.91 -> £3,395,201.90 (10.2%); £3,780,509.16 -> £3,395,201.93 (10.2%); £3,780,509.39 -> £3,395,201.96 (10.2%); £3,780,509.64 -> £3,395,201.99 (10.2%); £3,780,509.86 -> £3,395,202.02 (10.2%); £3,780,510.10 -> £3,395,202.05 (10.2%); £3,780,510.33 -> £3,395,202.09 (10.2%); £3,780,510.56 -> £3,395,202.12 (10.2%); £3,780,510.81 -> £3,395,202.15 (10.2%); £3,780,511.03 -> £3,395,202.17 (10.2%); £3,780,511.27 -> £3,395,202.20 (10.2%); £3,780,511.50 -> £3,395,202.23 (10.2%); £3,780,511.73 -> £3,395,202.26 (10.2%); £3,780,511.97 -> £3,395,202.29 (10.2%); £3,780,512.15 -> £3,395,202.48 (10.2%); £3,780,512.32 -> £3,395,202.67 (10.2%); £3,780,512.50 -> £3,395,202.86 (10.2%); £3,780,512.68 -> £3,395,203.06 (10.2%); £3,780,512.91 -> £3,395,203.26 (10.2%); £3,780,513.14 -> £3,395,203.45 (10.2%); £3,780,513.32 -> £3,395,203.65 (10.2%); £3,780,513.55 -> £3,395,203.85 (10.2%); £3,780,513.79 -> £3,395,204.04 (10.2%); £3,780,514.01 -> £3,395,204.24 (10.2%); £3,780,514.25 -> £3,395,204.43 (10.2%); £3,780,514.48 -> £3,395,204.46 (10.2%); £3,780,514.72 -> £3,395,204.49 (10.2%); £3,780,514.93 -> £3,395,204.51 (10.2%); £3,780,515.13 -> £3,395,204.54 (10.2%); £3,780,515.30 -> £3,395,204.56 (10.2%); £3,780,515.47 -> £3,395,204.58 (10.2%); £3,780,515.63 -> £3,395,204.59 (10.2%); £3,780,515.78 -> £3,395,204.61 (10.2%); £3,780,515.94 -> £3,395,204.63 (10.2%); £3,780,516.11 -> £3,395,204.64 (10.2%); £3,780,516.26 -> £3,395,204.66 (10.2%); £3,780,516.42 -> £3,395,204.68 (10.2%); £3,780,516.58 -> £3,395,204.69 (10.2%); £3,780,516.75 -> £3,395,204.71 (10.2%); £3,780,516.91 -> £3,395,204.73 (10.2%); £3,780,517.07 -> £3,395,204.75 (10.2%); £3,780,517.23 -> £3,395,204.91 (10.2%); £3,780,517.38 -> £3,395,205.08 (10.2%); £3,780,517.56 -> £3,395,205.25 (10.2%); £3,780,517.75 -> £3,395,205.42 (10.2%); £3,780,517.97 -> £3,395,205.60 (10.2%); £3,780,518.20 -> £3,395,205.78 (10.2%); £3,780,518.44 -> £3,395,205.95 (10.2%); £3,780,518.70 -> £3,395,206.12 (10.2%); £3,780,518.97 -> £3,395,206.14 (10.2%); £3,780,519.23 -> £3,395,206.16 (10.2%); £3,780,519.50 -> £3,395,206.19 (10.2%); £3,780,519.77 -> £3,395,206.21 (10.2%); £3,780,520.03 -> £3,395,206.24 (10.2%); £3,780,520.28 -> £3,395,206.26 (10.2%); £3,780,520.55 -> £3,395,206.28 (10.2%); £3,780,520.82 -> £3,395,206.31 (10.2%); £3,780,521.09 -> £3,395,206.33 (10.2%); £3,780,521.35 -> £3,395,206.35 (10.2%); £3,780,521.61 -> £3,395,206.38 (10.2%); £3,780,521.87 -> £3,395,206.40 (10.2%); £3,780,522.14 -> £3,395,206.43 (10.2%); £3,780,522.40 -> £3,395,206.61 (10.2%); £3,780,522.67 -> £3,395,206.79 (10.2%); £3,780,522.94 -> £3,395,206.98 (10.2%); £3,780,523.20 -> £3,395,207.16 (10.2%); £3,780,523.46 -> £3,395,207.34 (10.2%); £3,780,523.71 -> £3,395,207.52 (10.2%); £3,780,523.91 -> £3,395,207.70 (10.2%); £3,780,524.17 -> £3,395,207.88 (10.2%); £3,780,524.44 -> £3,395,208.06 (10.2%); £3,780,524.69 -> £3,395,208.24 (10.2%); £3,780,524.95 -> £3,395,208.41 (10.2%); £3,780,525.21 -> £3,395,208.44 (10.2%); £3,780,525.47 -> £3,395,208.47 (10.2%); £3,780,525.72 -> £3,395,208.49 (10.2%); £3,780,525.94 -> £3,395,208.51 (10.2%); £3,780,526.15 -> £3,395,208.53 (10.2%); £3,780,526.31 -> £3,395,208.55 (10.2%); £3,780,526.46 -> £3,395,208.57 (10.2%); £3,780,526.62 -> £3,395,208.59 (10.2%); £3,780,526.77 -> £3,395,208.60 (10.2%); £3,780,526.93 -> £3,395,208.62 (10.2%); £3,780,527.09 -> £3,395,208.64 (10.2%); £3,780,527.25 -> £3,395,208.65 (10.2%); £3,780,527.40 -> £3,395,208.67 (10.2%); £3,780,527.56 -> £3,395,208.69 (10.2%); £3,780,527.72 -> £3,395,208.70 (10.2%); £3,780,527.87 -> £3,395,208.72 (10.2%); £3,780,528.03 -> £3,395,208.91 (10.2%); £3,780,528.19 -> £3,395,209.11 (10.2%); £3,780,528.36 -> £3,395,209.30 (10.2%); £3,780,528.55 -> £3,395,209.50 (10.2%); £3,780,528.76 -> £3,395,209.70 (10.2%); £3,780,528.99 -> £3,395,209.90 (10.2%); £3,780,529.24 -> £3,395,210.09 (10.2%); £3,780,529.50 -> £3,395,210.29 (10.2%); £3,780,529.76 -> £3,395,210.31 (10.2%); £3,780,530.02 -> £3,395,210.34 (10.2%); £3,780,530.27 -> £3,395,210.36 (10.2%); £3,780,530.52 -> £3,395,210.38 (10.2%); £3,780,530.79 -> £3,395,210.41 (10.2%); £3,780,531.05 -> £3,395,210.43 (10.2%); £3,780,531.31 -> £3,395,210.46 (10.2%); £3,780,531.58 -> £3,395,210.48 (10.2%); £3,780,531.83 -> £3,395,210.50 (10.2%); £3,780,532.10 -> £3,395,210.53 (10.2%); £3,780,532.35 -> £3,395,210.55 (10.2%); £3,780,532.61 -> £3,395,210.58 (10.2%); £3,780,532.87 -> £3,395,210.60 (10.2%); £3,780,533.15 -> £3,395,210.80 (10.2%); £3,780,533.41 -> £3,395,211.00 (10.2%); £3,780,533.59 -> £3,395,211.20 (10.2%); £3,780,533.79 -> £3,395,211.39 (10.2%); £3,780,533.99 -> £3,395,211.59 (10.2%); £3,780,534.19 -> £3,395,211.79 (10.2%); £3,780,534.45 -> £3,395,211.99 (10.2%); £3,780,534.71 -> £3,395,212.19 (10.2%); £3,780,534.98 -> £3,395,212.39 (10.2%); £3,780,535.24 -> £3,395,212.58 (10.2%); £3,780,535.50 -> £3,395,212.78 (10.2%); £3,780,535.76 -> £3,395,212.81 (10.2%); £3,780,536.02 -> £3,395,212.84 (10.2%); £3,780,536.27 -> £3,395,212.86 (10.2%); £3,780,536.49 -> £3,395,212.88 (10.2%); £3,780,536.70 -> £3,395,212.90 (10.2%); £3,780,536.86 -> £3,395,212.92 (10.2%); £3,780,537.01 -> £3,395,212.94 (10.2%); £3,780,537.17 -> £3,395,212.96 (10.2%); £3,780,537.33 -> £3,395,212.98 (10.2%); £3,780,537.48 -> £3,395,212.99 (10.2%); £3,780,537.64 -> £3,395,213.01 (10.2%); £3,780,537.80 -> £3,395,213.02 (10.2%); £3,780,537.96 -> £3,395,213.04 (10.2%); £3,780,538.11 -> £3,395,213.06 (10.2%); £3,780,538.27 -> £3,395,213.07 (10.2%); £3,780,538.43 -> £3,395,213.09 (10.2%); £3,780,538.58 -> £3,395,213.24 (10.2%); £3,780,538.74 -> £3,395,213.39 (10.2%); £3,780,538.92 -> £3,395,213.54 (10.2%); £3,780,539.11 -> £3,395,213.70 (10.2%); £3,780,539.31 -> £3,395,213.85 (10.2%); £3,780,539.54 -> £3,395,214.01 (10.2%); £3,780,539.78 -> £3,395,214.16 (10.2%); £3,780,540.04 -> £3,395,214.32 (10.2%); £3,780,540.29 -> £3,395,214.34 (10.2%); £3,780,540.56 -> £3,395,214.37 (10.2%); £3,780,540.81 -> £3,395,214.39 (10.2%); £3,780,541.08 -> £3,395,214.41 (10.2%); £3,780,541.34 -> £3,395,214.44 (10.2%); £3,780,541.60 -> £3,395,214.46 (10.2%); £3,780,541.87 -> £3,395,214.49 (10.2%); £3,780,542.13 -> £3,395,214.51 (10.2%); £3,780,542.39 -> £3,395,214.53 (10.2%); £3,780,542.65 -> £3,395,214.56 (10.2%); £3,780,542.92 -> £3,395,214.58 (10.2%); £3,780,543.18 -> £3,395,214.61 (10.2%); £3,780,543.44 -> £3,395,214.63 (10.2%); £3,780,543.63 -> £3,395,214.80 (10.2%); £3,780,543.89 -> £3,395,214.96 (10.2%); £3,780,544.10 -> £3,395,215.13 (10.2%); £3,780,544.30 -> £3,395,215.29 (10.2%); £3,780,544.56 -> £3,395,215.46 (10.2%); £3,780,544.82 -> £3,395,215.62 (10.2%); £3,780,545.02 -> £3,395,215.78 (10.2%); £3,780,545.28 -> £3,395,215.94 (10.2%); £3,780,545.54 -> £3,395,216.10 (10.2%); £3,780,545.80 -> £3,395,216.26 (10.2%); £3,780,546.07 -> £3,395,216.42 (10.2%); £3,780,546.34 -> £3,395,216.45 (10.2%); £3,780,546.60 -> £3,395,216.47 (10.2%); £3,780,546.85 -> £3,395,216.50 (10.2%); £3,780,547.07 -> £3,395,216.52 (10.2%); £3,780,547.27 -> £3,395,216.54 (10.2%); £3,780,547.43 -> £3,395,216.56 (10.2%); £3,780,547.59 -> £3,395,216.57 (10.2%); £3,780,547.74 -> £3,395,216.59 (10.2%); £3,780,547.89 -> £3,395,216.61 (10.2%); £3,780,548.05 -> £3,395,216.63 (10.2%); £3,780,548.21 -> £3,395,216.64 (10.2%); £3,780,548.36 -> £3,395,216.66 (10.2%); £3,780,548.51 -> £3,395,216.67 (10.2%); £3,780,548.67 -> £3,395,216.69 (10.2%); £3,780,548.83 -> £3,395,216.71 (10.2%); £3,780,548.98 -> £3,395,216.73 (10.2%); £3,780,549.14 -> £3,395,216.86 (10.2%); £3,780,549.29 -> £3,395,216.99 (10.2%); £3,780,549.46 -> £3,395,217.13 (10.2%); £3,780,549.65 -> £3,395,217.26 (10.2%); £3,780,549.85 -> £3,395,217.40 (10.2%); £3,780,550.08 -> £3,395,217.53 (10.2%); £3,780,550.32 -> £3,395,217.67 (10.2%); £3,780,550.58 -> £3,395,217.80 (10.2%); £3,780,550.84 -> £3,395,217.82 (10.2%); £3,780,551.10 -> £3,395,217.84 (10.2%); £3,780,551.36 -> £3,395,217.87 (10.2%); £3,780,551.61 -> £3,395,217.89 (10.2%); £3,780,551.87 -> £3,395,217.92 (10.2%); £3,780,552.12 -> £3,395,217.94 (10.2%); £3,780,552.38 -> £3,395,217.96 (10.2%); £3,780,552.64 -> £3,395,217.99 (10.2%); £3,780,552.90 -> £3,395,218.01 (10.2%); £3,780,553.15 -> £3,395,218.03 (10.2%); £3,780,553.41 -> £3,395,218.06 (10.2%); £3,780,553.65 -> £3,395,218.08 (10.2%); £3,780,553.91 -> £3,395,218.11 (10.2%); £3,780,554.17 -> £3,395,218.25 (10.2%); £3,780,554.42 -> £3,395,218.40 (10.2%); £3,780,554.68 -> £3,395,218.54 (10.2%); £3,780,554.87 -> £3,395,218.69 (10.2%); £3,780,555.07 -> £3,395,218.83 (10.2%); £3,780,555.33 -> £3,395,218.98 (10.2%); £3,780,555.52 -> £3,395,219.12 (10.2%); £3,780,555.78 -> £3,395,219.25 (10.2%); £3,780,556.03 -> £3,395,219.39 (10.2%); £3,780,556.29 -> £3,395,219.53 (10.2%); £3,780,556.55 -> £3,395,219.67 (10.2%); £3,780,556.82 -> £3,395,219.69 (10.2%); £3,780,557.08 -> £3,395,219.72 (10.2%); £3,780,557.31 -> £3,395,219.75 (10.2%); £3,780,557.54 -> £3,395,219.77 (10.2%); £3,780,557.74 -> £3,395,219.79 (10.2%); £3,780,557.90 -> £3,395,219.81 (10.2%); £3,780,558.05 -> £3,395,219.82 (10.2%); £3,780,558.21 -> £3,395,219.84 (10.2%); £3,780,558.36 -> £3,395,219.86 (10.2%); £3,780,558.52 -> £3,395,219.87 (10.2%); £3,780,558.68 -> £3,395,219.89 (10.2%); £3,780,558.84 -> £3,395,219.91 (10.2%); £3,780,558.99 -> £3,395,219.92 (10.2%); £3,780,559.15 -> £3,395,219.94 (10.2%); £3,780,559.30 -> £3,395,219.96 (10.2%); £3,780,559.45 -> £3,395,219.98 (10.2%); £3,780,559.61 -> £3,395,220.16 (10.2%); £3,780,559.76 -> £3,395,220.35 (10.2%); £3,780,559.94 -> £3,395,220.54 (10.2%); £3,780,560.12 -> £3,395,220.74 (10.2%); £3,780,560.32 -> £3,395,220.94 (10.2%); £3,780,560.54 -> £3,395,221.13 (10.2%); £3,780,560.78 -> £3,395,221.33 (10.2%); £3,780,561.03 -> £3,395,221.52 (10.2%); £3,780,561.29 -> £3,395,221.55 (10.2%); £3,780,561.56 -> £3,395,221.57 (10.2%); £3,780,561.82 -> £3,395,221.59 (10.2%); £3,780,562.08 -> £3,395,221.62 (10.2%); £3,780,562.35 -> £3,395,221.64 (10.2%); £3,780,562.61 -> £3,395,221.66 (10.2%); £3,780,562.87 -> £3,395,221.69 (10.2%); £3,780,563.12 -> £3,395,221.71 (10.2%); £3,780,563.39 -> £3,395,221.73 (10.2%); £3,780,563.65 -> £3,395,221.76 (10.2%); £3,780,563.92 -> £3,395,221.78 (10.2%); £3,780,564.18 -> £3,395,221.81 (10.2%); £3,780,564.43 -> £3,395,221.83 (10.2%); £3,780,564.68 -> £3,395,222.03 (10.2%); £3,780,564.95 -> £3,395,222.23 (10.2%); £3,780,565.21 -> £3,395,222.43 (10.2%); £3,780,565.48 -> £3,395,222.63 (10.2%); £3,780,565.74 -> £3,395,222.82 (10.2%); £3,780,566.01 -> £3,395,223.02 (10.2%); £3,780,566.27 -> £3,395,223.23 (10.2%); £3,780,566.53 -> £3,395,223.42 (10.2%); £3,780,566.80 -> £3,395,223.62 (10.2%); £3,780,567.06 -> £3,395,223.82 (10.2%); £3,780,567.32 -> £3,395,224.02 (10.2%); £3,780,567.59 -> £3,395,224.04 (10.2%); £3,780,567.85 -> £3,395,224.07 (10.2%); £3,780,568.09 -> £3,395,224.09 (10.2%); £3,780,568.31 -> £3,395,224.12 (10.2%); £3,780,568.51 -> £3,395,224.14 (10.2%); £3,780,568.64 -> £3,395,224.16 (10.2%); £3,780,568.78 -> £3,395,224.18 (10.2%); £3,780,568.91 -> £3,395,224.19 (10.2%); £3,780,569.05 -> £3,395,224.21 (10.2%); £3,780,569.18 -> £3,395,224.23 (10.2%); £3,780,569.32 -> £3,395,224.24 (10.2%); £3,780,569.46 -> £3,395,224.26 (10.2%); £3,780,569.59 -> £3,395,224.28 (10.2%); £3,780,569.73 -> £3,395,224.29 (10.2%); £3,780,569.87 -> £3,395,224.31 (10.2%); £3,780,570.00 -> £3,395,224.33 (10.2%); £3,780,570.14 -> £3,395,224.52 (10.2%); £3,780,570.28 -> £3,395,224.72 (10.2%); £3,780,570.43 -> £3,395,224.92 (10.2%); £3,780,570.60 -> £3,395,225.13 (10.2%); £3,780,570.78 -> £3,395,225.33 (10.2%); £3,780,570.98 -> £3,395,225.53 (10.2%); £3,780,571.19 -> £3,395,225.73 (10.2%); £3,780,571.41 -> £3,395,225.93 (10.2%); £3,780,571.64 -> £3,395,225.95 (10.2%); £3,780,571.86 -> £3,395,225.98 (10.2%); £3,780,572.09 -> £3,395,226.00 (10.2%); £3,780,572.31 -> £3,395,226.03 (10.2%); £3,780,572.54 -> £3,395,226.06 (10.2%); £3,780,572.76 -> £3,395,226.08 (10.2%); £3,780,572.99 -> £3,395,226.11 (10.2%); £3,780,573.22 -> £3,395,226.14 (10.2%); £3,780,573.46 -> £3,395,226.16 (10.2%); £3,780,573.68 -> £3,395,226.19 (10.2%); £3,780,573.91 -> £3,395,226.21 (10.2%); £3,780,574.14 -> £3,395,226.24 (10.2%); £3,780,574.36 -> £3,395,226.27 (10.2%); £3,780,574.59 -> £3,395,226.47 (10.2%); £3,780,574.81 -> £3,395,226.68 (10.2%); £3,780,575.04 -> £3,395,226.88 (10.2%); £3,780,575.26 -> £3,395,227.09 (10.2%); £3,780,575.49 -> £3,395,227.29 (10.2%); £3,780,575.71 -> £3,395,227.50 (10.2%); £3,780,575.94 -> £3,395,227.71 (10.2%); £3,780,576.17 -> £3,395,227.92 (10.2%); £3,780,576.40 -> £3,395,228.12 (10.2%); £3,780,576.63 -> £3,395,228.33 (10.2%); £3,780,576.86 -> £3,395,228.53 (10.2%); £3,780,577.08 -> £3,395,228.56 (10.2%); £3,780,577.30 -> £3,395,228.59 (10.2%); £3,780,577.52 -> £3,395,228.61 (10.2%); £3,780,577.71 -> £3,395,228.64 (10.2%); £3,780,577.89 -> £3,395,228.66 (10.2%); £3,780,578.02 -> £3,395,228.68 (10.2%); £3,780,578.15 -> £3,395,228.70 (10.2%); £3,780,578.29 -> £3,395,228.72 (10.2%); £3,780,578.42 -> £3,395,228.73 (10.2%); £3,780,578.55 -> £3,395,228.75 (10.2%); £3,780,578.69 -> £3,395,228.77 (10.2%); £3,780,578.82 -> £3,395,228.78 (10.2%); £3,780,578.96 -> £3,395,228.80 (10.2%); £3,780,579.10 -> £3,395,228.82 (10.2%); £3,780,579.24 -> £3,395,228.83 (10.2%); £3,780,579.37 -> £3,395,228.85 (10.2%); £3,780,579.51 -> £3,395,229.03 (10.2%); £3,780,579.64 -> £3,395,229.22 (10.2%); £3,780,579.80 -> £3,395,229.40 (10.2%); £3,780,579.96 -> £3,395,229.60 (10.2%); £3,780,580.14 -> £3,395,229.79 (10.2%); £3,780,580.34 -> £3,395,229.99 (10.2%); £3,780,580.55 -> £3,395,230.19 (10.2%); £3,780,580.77 -> £3,395,230.39 (10.2%); £3,780,581.00 -> £3,395,230.42 (10.2%); £3,780,581.23 -> £3,395,230.45 (10.2%); £3,780,581.46 -> £3,395,230.48 (10.2%); £3,780,581.67 -> £3,395,230.51 (10.2%); £3,780,581.89 -> £3,395,230.55 (10.2%); £3,780,582.12 -> £3,395,230.58 (10.2%); £3,780,582.34 -> £3,395,230.61 (10.2%); £3,780,582.58 -> £3,395,230.64 (10.2%); £3,780,582.80 -> £3,395,230.67 (10.2%); £3,780,583.03 -> £3,395,230.70 (10.2%); £3,780,583.25 -> £3,395,230.72 (10.2%); £3,780,583.48 -> £3,395,230.75 (10.2%); £3,780,583.71 -> £3,395,230.78 (10.2%); £3,780,583.95 -> £3,395,230.98 (10.2%); £3,780,584.17 -> £3,395,231.18 (10.2%); £3,780,584.40 -> £3,395,231.38 (10.2%); £3,780,584.63 -> £3,395,231.58 (10.2%); £3,780,584.85 -> £3,395,231.78 (10.2%); £3,780,585.07 -> £3,395,231.98 (10.2%); £3,780,585.29 -> £3,395,232.19 (10.2%); £3,780,585.51 -> £3,395,232.39 (10.2%); £3,780,585.74 -> £3,395,232.59 (10.2%); £3,780,585.97 -> £3,395,232.78 (10.2%); £3,780,586.21 -> £3,395,232.98 (10.2%); £3,780,586.43 -> £3,395,233.01 (10.2%); £3,780,586.66 -> £3,395,233.04 (10.2%); £3,780,586.87 -> £3,395,233.06 (10.2%); £3,780,587.06 -> £3,395,233.08 (10.2%); £3,780,587.24 -> £3,395,233.10 (10.2%); £3,780,587.39 -> £3,395,233.12 (10.2%); £3,780,587.54 -> £3,395,233.14 (10.2%); £3,780,587.70 -> £3,395,233.16 (10.2%); £3,780,587.85 -> £3,395,233.18 (10.2%); £3,780,588.01 -> £3,395,233.19 (10.2%); £3,780,588.17 -> £3,395,233.21 (10.2%); £3,780,588.32 -> £3,395,233.23 (10.2%); £3,780,588.47 -> £3,395,233.24 (10.2%); £3,780,588.63 -> £3,395,233.26 (10.2%); £3,780,588.78 -> £3,395,233.27 (10.2%); £3,780,588.94 -> £3,395,233.29 (10.2%); £3,780,589.09 -> £3,395,233.46 (10.2%); £3,780,589.25 -> £3,395,233.63 (10.2%); £3,780,589.41 -> £3,395,233.80 (10.2%); £3,780,589.60 -> £3,395,233.98 (10.2%); £3,780,589.81 -> £3,395,234.16 (10.2%); £3,780,590.04 -> £3,395,234.34 (10.2%); £3,780,590.28 -> £3,395,234.51 (10.2%); £3,780,590.54 -> £3,395,234.69 (10.2%); £3,780,590.80 -> £3,395,234.72 (10.2%); £3,780,591.06 -> £3,395,234.74 (10.2%); £3,780,591.32 -> £3,395,234.77 (10.2%); £3,780,591.58 -> £3,395,234.79 (10.2%); £3,780,591.84 -> £3,395,234.81 (10.2%); £3,780,592.10 -> £3,395,234.84 (10.2%); £3,780,592.36 -> £3,395,234.86 (10.2%); £3,780,592.62 -> £3,395,234.89 (10.2%); £3,780,592.88 -> £3,395,234.91 (10.2%); £3,780,593.14 -> £3,395,234.93 (10.2%); £3,780,593.39 -> £3,395,234.96 (10.2%); £3,780,593.65 -> £3,395,234.98 (10.2%); £3,780,593.91 -> £3,395,235.01 (10.2%); £3,780,594.16 -> £3,395,235.19 (10.2%); £3,780,594.42 -> £3,395,235.37 (10.2%); £3,780,594.66 -> £3,395,235.56 (10.2%); £3,780,594.92 -> £3,395,235.74 (10.2%); £3,780,595.18 -> £3,395,235.92 (10.2%); £3,780,595.43 -> £3,395,236.10 (10.2%); £3,780,595.69 -> £3,395,236.29 (10.2%); £3,780,595.95 -> £3,395,236.47 (10.2%); £3,780,596.21 -> £3,395,236.66 (10.2%); £3,780,596.46 -> £3,395,236.84 (10.2%); £3,780,596.72 -> £3,395,237.01 (10.2%); £3,780,596.98 -> £3,395,237.04 (10.2%); £3,780,597.24 -> £3,395,237.07 (10.2%); £3,780,597.48 -> £3,395,237.10 (10.2%); £3,780,597.70 -> £3,395,237.12 (10.2%); £3,780,597.90 -> £3,395,237.14 (10.2%); £3,780,598.05 -> £3,395,237.16 (10.2%); £3,780,598.20 -> £3,395,237.17 (10.2%); £3,780,598.36 -> £3,395,237.19 (10.2%); £3,780,598.52 -> £3,395,237.21 (10.2%); £3,780,598.67 -> £3,395,237.22 (10.2%); £3,780,598.82 -> £3,395,237.24 (10.2%); £3,780,598.97 -> £3,395,237.26 (10.2%); £3,780,599.12 -> £3,395,237.27 (10.2%); £3,780,599.27 -> £3,395,237.29 (10.2%); £3,780,599.42 -> £3,395,237.31 (10.2%); £3,780,599.57 -> £3,395,237.32 (10.2%); £3,780,599.73 -> £3,395,237.47 (10.2%); £3,780,599.88 -> £3,395,237.61 (10.2%); £3,780,600.06 -> £3,395,237.76 (10.2%); £3,780,600.24 -> £3,395,237.91 (10.2%); £3,780,600.45 -> £3,395,238.06 (10.2%); £3,780,600.67 -> £3,395,238.20 (10.2%); £3,780,600.91 -> £3,395,238.35 (10.2%); £3,780,601.17 -> £3,395,238.50 (10.2%); £3,780,601.42 -> £3,395,238.52 (10.2%); £3,780,601.68 -> £3,395,238.54 (10.2%); £3,780,601.94 -> £3,395,238.57 (10.2%); £3,780,602.19 -> £3,395,238.59 (10.2%); £3,780,602.44 -> £3,395,238.62 (10.2%); £3,780,602.70 -> £3,395,238.64 (10.2%); £3,780,602.96 -> £3,395,238.67 (10.2%); £3,780,603.21 -> £3,395,238.69 (10.2%); £3,780,603.46 -> £3,395,238.71 (10.2%); £3,780,603.73 -> £3,395,238.74 (10.2%); £3,780,603.98 -> £3,395,238.76 (10.2%); £3,780,604.25 -> £3,395,238.78 (10.2%); £3,780,604.50 -> £3,395,238.81 (10.2%); £3,780,604.76 -> £3,395,238.97 (10.2%); £3,780,605.02 -> £3,395,239.13 (10.2%); £3,780,605.27 -> £3,395,239.28 (10.2%); £3,780,605.53 -> £3,395,239.44 (10.2%); £3,780,605.79 -> £3,395,239.60 (10.2%); £3,780,606.04 -> £3,395,239.75 (10.2%); £3,780,606.30 -> £3,395,239.91 (10.2%); £3,780,606.56 -> £3,395,240.06 (10.2%); £3,780,606.82 -> £3,395,240.21 (10.2%); £3,780,607.07 -> £3,395,240.37 (10.2%); £3,780,607.33 -> £3,395,240.52 (10.2%); £3,780,607.58 -> £3,395,240.55 (10.2%); £3,780,607.85 -> £3,395,240.58 (10.2%); £3,780,608.08 -> £3,395,240.60 (10.2%); £3,780,608.30 -> £3,395,240.62 (10.2%); £3,780,608.49 -> £3,395,240.64 (10.2%); £3,780,608.64 -> £3,395,240.66 (10.2%); £3,780,608.79 -> £3,395,240.68 (10.2%); £3,780,608.95 -> £3,395,240.70 (10.2%); £3,780,609.09 -> £3,395,240.71 (10.2%); £3,780,609.24 -> £3,395,240.73 (10.2%); £3,780,609.40 -> £3,395,240.75 (10.2%); £3,780,609.55 -> £3,395,240.76 (10.2%); £3,780,609.70 -> £3,395,240.78 (10.2%); £3,780,609.85 -> £3,395,240.79 (10.2%); £3,780,610.01 -> £3,395,240.81 (10.2%); £3,780,610.16 -> £3,395,240.83 (10.2%); £3,780,610.31 -> £3,395,240.99 (10.2%); £3,780,610.46 -> £3,395,241.16 (10.2%); £3,780,610.64 -> £3,395,241.33 (10.2%); £3,780,610.83 -> £3,395,241.50 (10.2%); £3,780,611.03 -> £3,395,241.68 (10.2%); £3,780,611.25 -> £3,395,241.85 (10.2%); £3,780,611.49 -> £3,395,242.02 (10.2%); £3,780,611.74 -> £3,395,242.20 (10.2%); £3,780,611.99 -> £3,395,242.22 (10.2%); £3,780,612.24 -> £3,395,242.25 (10.2%); £3,780,612.50 -> £3,395,242.27 (10.2%); £3,780,612.76 -> £3,395,242.30 (10.2%); £3,780,613.02 -> £3,395,242.32 (10.2%); £3,780,613.28 -> £3,395,242.34 (10.2%); £3,780,613.54 -> £3,395,242.37 (10.2%); £3,780,613.80 -> £3,395,242.39 (10.2%); £3,780,614.06 -> £3,395,242.41 (10.2%); £3,780,614.31 -> £3,395,242.44 (10.2%); £3,780,614.57 -> £3,395,242.46 (10.2%); £3,780,614.82 -> £3,395,242.49 (10.2%); £3,780,615.08 -> £3,395,242.52 (10.2%); £3,780,615.33 -> £3,395,242.70 (10.2%); £3,780,615.60 -> £3,395,242.88 (10.2%); £3,780,615.86 -> £3,395,243.06 (10.2%); £3,780,616.12 -> £3,395,243.24 (10.2%); £3,780,616.37 -> £3,395,243.41 (10.2%); £3,780,616.63 -> £3,395,243.59 (10.2%); £3,780,616.88 -> £3,395,243.77 (10.2%); £3,780,617.13 -> £3,395,243.95 (10.2%); £3,780,617.39 -> £3,395,244.13 (10.2%); £3,780,617.65 -> £3,395,244.31 (10.2%); £3,780,617.90 -> £3,395,244.49 (10.2%); £3,780,618.15 -> £3,395,244.52 (10.2%); £3,780,618.41 -> £3,395,244.55 (10.2%); £3,780,618.65 -> £3,395,244.57 (10.2%); £3,780,618.86 -> £3,395,244.59 (10.2%); £3,780,619.06 -> £3,395,244.61 (10.2%); £3,780,619.22 -> £3,395,244.63 (10.2%); £3,780,619.37 -> £3,395,244.65 (10.2%); £3,780,619.52 -> £3,395,244.67 (10.2%); £3,780,619.67 -> £3,395,244.69 (10.2%); £3,780,619.82 -> £3,395,244.70 (10.2%); £3,780,619.97 -> £3,395,244.72 (10.2%); £3,780,620.13 -> £3,395,244.73 (10.2%); £3,780,620.28 -> £3,395,244.75 (10.2%); £3,780,620.43 -> £3,395,244.77 (10.2%); £3,780,620.59 -> £3,395,244.78 (10.2%); £3,780,620.74 -> £3,395,244.80 (10.2%); £3,780,620.89 -> £3,395,244.95 (10.2%); £3,780,621.04 -> £3,395,245.10 (10.2%); £3,780,621.21 -> £3,395,245.26 (10.2%); £3,780,621.40 -> £3,395,245.41 (10.2%); £3,780,621.60 -> £3,395,245.58 (10.2%); £3,780,621.81 -> £3,395,245.73 (10.2%); £3,780,622.05 -> £3,395,245.88 (10.2%); £3,780,622.32 -> £3,395,246.04 (10.2%); £3,780,622.57 -> £3,395,246.06 (10.2%); £3,780,622.84 -> £3,395,246.08 (10.2%); £3,780,623.09 -> £3,395,246.11 (10.2%); £3,780,623.34 -> £3,395,246.13 (10.2%); £3,780,623.59 -> £3,395,246.16 (10.2%); £3,780,623.84 -> £3,395,246.18 (10.2%); £3,780,624.10 -> £3,395,246.20 (10.2%); £3,780,624.35 -> £3,395,246.23 (10.2%); £3,780,624.61 -> £3,395,246.25 (10.2%); £3,780,624.86 -> £3,395,246.27 (10.2%); £3,780,625.12 -> £3,395,246.30 (10.2%); £3,780,625.38 -> £3,395,246.32 (10.2%); £3,780,625.63 -> £3,395,246.35 (10.2%); £3,780,625.88 -> £3,395,246.51 (10.2%); £3,780,626.14 -> £3,395,246.68 (10.2%); £3,780,626.40 -> £3,395,246.85 (10.2%); £3,780,626.66 -> £3,395,247.02 (10.2%); £3,780,626.91 -> £3,395,247.18 (10.2%); £3,780,627.17 -> £3,395,247.35 (10.2%); £3,780,627.42 -> £3,395,247.52 (10.2%); £3,780,627.67 -> £3,395,247.69 (10.2%); £3,780,627.93 -> £3,395,247.85 (10.2%); £3,780,628.19 -> £3,395,248.02 (10.2%); £3,780,628.45 -> £3,395,248.18 (10.2%); £3,780,628.70 -> £3,395,248.21 (10.2%); £3,780,628.95 -> £3,395,248.23 (10.2%); £3,780,629.19 -> £3,395,248.26 (10.2%); £3,780,629.40 -> £3,395,248.28 (10.2%); £3,780,629.60 -> £3,395,248.30 (10.2%); £3,780,629.75 -> £3,395,248.32 (10.2%); £3,780,629.91 -> £3,395,248.34 (10.2%); £3,780,630.06 -> £3,395,248.35 (10.2%); £3,780,630.21 -> £3,395,248.37 (10.2%); £3,780,630.36 -> £3,395,248.39 (10.2%); £3,780,630.52 -> £3,395,248.40 (10.2%); £3,780,630.67 -> £3,395,248.42 (10.2%); £3,780,630.82 -> £3,395,248.44 (10.2%); £3,780,630.97 -> £3,395,248.45 (10.2%); £3,780,631.13 -> £3,395,248.47 (10.2%); £3,780,631.28 -> £3,395,248.49 (10.2%); £3,780,631.43 -> £3,395,248.64 (10.2%); £3,780,631.59 -> £3,395,248.80 (10.2%); £3,780,631.76 -> £3,395,248.96 (10.2%); £3,780,631.95 -> £3,395,249.12 (10.2%); £3,780,632.15 -> £3,395,249.28 (10.2%); £3,780,632.36 -> £3,395,249.44 (10.2%); £3,780,632.60 -> £3,395,249.60 (10.2%); £3,780,632.87 -> £3,395,249.76 (10.2%); £3,780,633.13 -> £3,395,249.78 (10.2%); £3,780,633.38 -> £3,395,249.80 (10.2%); £3,780,633.64 -> £3,395,249.83 (10.2%); £3,780,633.90 -> £3,395,249.85 (10.2%); £3,780,634.15 -> £3,395,249.87 (10.2%); £3,780,634.41 -> £3,395,249.90 (10.2%); £3,780,634.67 -> £3,395,249.92 (10.2%); £3,780,634.92 -> £3,395,249.95 (10.2%); £3,780,635.17 -> £3,395,249.97 (10.2%); £3,780,635.43 -> £3,395,249.99 (10.2%); £3,780,635.69 -> £3,395,250.02 (10.2%); £3,780,635.94 -> £3,395,250.04 (10.2%); £3,780,636.19 -> £3,395,250.07 (10.2%); £3,780,636.45 -> £3,395,250.23 (10.2%); £3,780,636.70 -> £3,395,250.40 (10.2%); £3,780,636.95 -> £3,395,250.57 (10.2%); £3,780,637.21 -> £3,395,250.73 (10.2%); £3,780,637.47 -> £3,395,250.90 (10.2%); £3,780,637.72 -> £3,395,251.07 (10.2%); £3,780,637.96 -> £3,395,251.23 (10.2%); £3,780,638.23 -> £3,395,251.39 (10.2%); £3,780,638.48 -> £3,395,251.56 (10.2%); £3,780,638.74 -> £3,395,251.72 (10.2%); £3,780,638.98 -> £3,395,251.88 (10.2%); £3,780,639.24 -> £3,395,251.91 (10.2%); £3,780,639.50 -> £3,395,251.94 (10.2%); £3,780,639.74 -> £3,395,251.96 (10.2%); £3,780,639.95 -> £3,395,251.98 (10.2%); £3,780,640.15 -> £3,395,252.00 (10.2%); £3,780,640.28 -> £3,395,252.02 (10.2%); £3,780,640.41 -> £3,395,252.04 (10.2%); £3,780,640.54 -> £3,395,252.06 (10.2%); £3,780,640.68 -> £3,395,252.08 (10.2%); £3,780,640.81 -> £3,395,252.09 (10.2%); £3,780,640.94 -> £3,395,252.11 (10.2%); £3,780,641.08 -> £3,395,252.13 (10.2%); £3,780,641.21 -> £3,395,252.14 (10.2%); £3,780,641.35 -> £3,395,252.16 (10.2%); £3,780,641.48 -> £3,395,252.18 (10.2%); £3,780,641.61 -> £3,395,252.19 (10.2%); £3,780,641.75 -> £3,395,252.33 (10.2%); £3,780,641.89 -> £3,395,252.47 (10.2%); £3,780,642.04 -> £3,395,252.62 (10.2%); £3,780,642.20 -> £3,395,252.77 (10.2%); £3,780,642.38 -> £3,395,252.92 (10.2%); £3,780,642.58 -> £3,395,253.07 (10.2%); £3,780,642.79 -> £3,395,253.22 (10.2%); £3,780,643.01 -> £3,395,253.37 (10.2%); £3,780,643.24 -> £3,395,253.40 (10.2%); £3,780,643.46 -> £3,395,253.42 (10.2%); £3,780,643.68 -> £3,395,253.45 (10.2%); £3,780,643.90 -> £3,395,253.48 (10.2%); £3,780,644.13 -> £3,395,253.50 (10.2%); £3,780,644.36 -> £3,395,253.53 (10.2%); £3,780,644.58 -> £3,395,253.56 (10.2%); £3,780,644.80 -> £3,395,253.58 (10.2%); £3,780,645.03 -> £3,395,253.61 (10.2%); £3,780,645.25 -> £3,395,253.63 (10.2%); £3,780,645.48 -> £3,395,253.66 (10.2%); £3,780,645.71 -> £3,395,253.68 (10.2%); £3,780,645.94 -> £3,395,253.71 (10.2%); £3,780,646.16 -> £3,395,253.87 (10.2%); £3,780,646.39 -> £3,395,254.03 (10.2%); £3,780,646.61 -> £3,395,254.19 (10.2%); £3,780,646.84 -> £3,395,254.34 (10.2%); £3,780,647.06 -> £3,395,254.50 (10.2%); £3,780,647.29 -> £3,395,254.67 (10.2%); £3,780,647.51 -> £3,395,254.83 (10.2%); £3,780,647.73 -> £3,395,254.99 (10.2%); £3,780,647.95 -> £3,395,255.15 (10.2%); £3,780,648.17 -> £3,395,255.31 (10.2%); £3,780,648.40 -> £3,395,255.46 (10.2%); £3,780,648.62 -> £3,395,255.48 (10.2%); £3,780,648.84 -> £3,395,255.51 (10.2%); £3,780,649.05 -> £3,395,255.54 (10.2%); £3,780,649.24 -> £3,395,255.56 (10.2%); £3,780,649.41 -> £3,395,255.58 (10.2%); £3,780,649.55 -> £3,395,255.60 (10.2%); £3,780,649.68 -> £3,395,255.62 (10.2%); £3,780,649.82 -> £3,395,255.64 (10.2%); £3,780,649.95 -> £3,395,255.66 (10.2%); £3,780,650.09 -> £3,395,255.68 (10.2%); £3,780,650.22 -> £3,395,255.69 (10.2%); £3,780,650.36 -> £3,395,255.71 (10.2%); £3,780,650.50 -> £3,395,255.73 (10.2%); £3,780,650.63 -> £3,395,255.74 (10.2%); £3,780,650.77 -> £3,395,255.76 (10.2%); £3,780,650.90 -> £3,395,255.78 (10.2%); £3,780,651.04 -> £3,395,255.91 (10.2%); £3,780,651.17 -> £3,395,256.05 (10.2%); £3,780,651.32 -> £3,395,256.18 (10.2%); £3,780,651.49 -> £3,395,256.32 (10.2%); £3,780,651.67 -> £3,395,256.46 (10.2%); £3,780,651.86 -> £3,395,256.60 (10.2%); £3,780,652.07 -> £3,395,256.75 (10.2%); £3,780,652.29 -> £3,395,256.89 (10.2%); £3,780,652.53 -> £3,395,256.92 (10.2%); £3,780,652.75 -> £3,395,256.95 (10.2%); £3,780,652.97 -> £3,395,256.98 (10.2%); £3,780,653.19 -> £3,395,257.01 (10.2%); £3,780,653.42 -> £3,395,257.05 (10.2%); £3,780,653.65 -> £3,395,257.08 (10.2%); £3,780,653.87 -> £3,395,257.11 (10.2%); £3,780,654.09 -> £3,395,257.14 (10.2%); £3,780,654.31 -> £3,395,257.17 (10.2%); £3,780,654.54 -> £3,395,257.19 (10.2%); £3,780,654.76 -> £3,395,257.22 (10.2%); £3,780,654.99 -> £3,395,257.25 (10.2%); £3,780,655.21 -> £3,395,257.28 (10.2%); £3,780,655.43 -> £3,395,257.44 (10.2%); £3,780,655.66 -> £3,395,257.59 (10.2%); £3,780,655.89 -> £3,395,257.75 (10.2%); £3,780,656.12 -> £3,395,257.90 (10.2%); £3,780,656.33 -> £3,395,258.05 (10.2%); £3,780,656.54 -> £3,395,258.21 (10.2%); £3,780,656.77 -> £3,395,258.36 (10.2%); £3,780,656.98 -> £3,395,258.51 (10.2%); £3,780,657.21 -> £3,395,258.65 (10.2%); £3,780,657.44 -> £3,395,258.80 (10.2%); £3,780,657.66 -> £3,395,258.95 (10.2%); £3,780,657.88 -> £3,395,258.98 (10.2%); £3,780,658.10 -> £3,395,259.01 (10.2%); £3,780,658.32 -> £3,395,259.03 (10.2%); £3,780,658.51 -> £3,395,259.06 (10.2%); £3,780,658.68 -> £3,395,259.08 (10.2%); £3,780,658.84 -> £3,395,259.09 (10.2%); £3,780,658.99 -> £3,395,259.11 (10.2%); £3,780,659.14 -> £3,395,259.13 (10.2%); £3,780,659.29 -> £3,395,259.15 (10.2%); £3,780,659.45 -> £3,395,259.16 (10.2%); £3,780,659.60 -> £3,395,259.18 (10.2%); £3,780,659.75 -> £3,395,259.20 (10.2%); £3,780,659.90 -> £3,395,259.21 (10.2%); £3,780,660.06 -> £3,395,259.23 (10.2%); £3,780,660.21 -> £3,395,259.25 (10.2%); £3,780,660.35 -> £3,395,259.26 (10.2%); £3,780,660.50 -> £3,395,259.41 (10.2%); £3,780,660.65 -> £3,395,259.55 (10.2%); £3,780,660.82 -> £3,395,259.70 (10.2%); £3,780,661.01 -> £3,395,259.84 (10.2%); £3,780,661.22 -> £3,395,259.99 (10.2%); £3,780,661.44 -> £3,395,260.13 (10.2%); £3,780,661.68 -> £3,395,260.28 (10.2%); £3,780,661.92 -> £3,395,260.42 (10.2%); £3,780,662.18 -> £3,395,260.44 (10.2%); £3,780,662.43 -> £3,395,260.47 (10.2%); £3,780,662.69 -> £3,395,260.49 (10.2%); £3,780,662.94 -> £3,395,260.51 (10.2%); £3,780,663.19 -> £3,395,260.54 (10.2%); £3,780,663.45 -> £3,395,260.56 (10.2%); £3,780,663.70 -> £3,395,260.58 (10.2%); £3,780,663.94 -> £3,395,260.61 (10.2%); £3,780,664.19 -> £3,395,260.63 (10.2%); £3,780,664.46 -> £3,395,260.65 (10.2%); £3,780,664.71 -> £3,395,260.68 (10.2%); £3,780,664.96 -> £3,395,260.70 (10.2%); £3,780,665.22 -> £3,395,260.73 (10.2%); £3,780,665.47 -> £3,395,260.87 (10.2%); £3,780,665.72 -> £3,395,261.02 (10.2%); £3,780,665.98 -> £3,395,261.17 (10.2%); £3,780,666.24 -> £3,395,261.32 (10.2%); £3,780,666.49 -> £3,395,261.47 (10.2%); £3,780,666.74 -> £3,395,261.63 (10.2%); £3,780,666.99 -> £3,395,261.79 (10.2%); £3,780,667.24 -> £3,395,261.94 (10.2%); £3,780,667.49 -> £3,395,262.10 (10.2%); £3,780,667.74 -> £3,395,262.25 (10.2%); £3,780,668.01 -> £3,395,262.40 (10.2%); £3,780,668.26 -> £3,395,262.43 (10.2%); £3,780,668.51 -> £3,395,262.46 (10.2%); £3,780,668.74 -> £3,395,262.48 (10.2%); £3,780,668.96 -> £3,395,262.50 (10.2%); £3,780,669.15 -> £3,395,262.52 (10.2%); £3,780,669.30 -> £3,395,262.54 (10.2%); £3,780,669.45 -> £3,395,262.56 (10.2%); £3,780,669.60 -> £3,395,262.58 (10.2%); £3,780,669.74 -> £3,395,262.59 (10.2%); £3,780,669.90 -> £3,395,262.61 (10.2%); £3,780,670.05 -> £3,395,262.63 (10.2%); £3,780,670.20 -> £3,395,262.64 (10.2%); £3,780,670.35 -> £3,395,262.66 (10.2%); £3,780,670.50 -> £3,395,262.68 (10.2%); £3,780,670.65 -> £3,395,262.69 (10.2%); £3,780,670.79 -> £3,395,262.71 (10.2%); £3,780,670.94 -> £3,395,262.81 (10.2%); £3,780,671.10 -> £3,395,262.92 (10.2%); £3,780,671.27 -> £3,395,263.04 (10.2%); £3,780,671.45 -> £3,395,263.16 (10.2%); £3,780,671.66 -> £3,395,263.28 (10.2%); £3,780,671.87 -> £3,395,263.39 (10.2%); £3,780,672.10 -> £3,395,263.51 (10.2%); £3,780,672.36 -> £3,395,263.62 (10.2%); £3,780,672.61 -> £3,395,263.64 (10.2%); £3,780,672.86 -> £3,395,263.67 (10.2%); £3,780,673.11 -> £3,395,263.69 (10.2%); £3,780,673.37 -> £3,395,263.71 (10.2%); £3,780,673.62 -> £3,395,263.74 (10.2%); £3,780,673.87 -> £3,395,263.76 (10.2%); £3,780,674.12 -> £3,395,263.79 (10.2%); £3,780,674.37 -> £3,395,263.81 (10.2%); £3,780,674.62 -> £3,395,263.83 (10.2%); £3,780,674.87 -> £3,395,263.86 (10.2%); £3,780,675.12 -> £3,395,263.88 (10.2%); £3,780,675.38 -> £3,395,263.90 (10.2%); £3,780,675.64 -> £3,395,263.93 (10.2%); £3,780,675.89 -> £3,395,264.05 (10.2%); £3,780,676.15 -> £3,395,264.18 (10.2%); £3,780,676.40 -> £3,395,264.30 (10.2%); £3,780,676.66 -> £3,395,264.43 (10.2%); £3,780,676.92 -> £3,395,264.55 (10.2%); £3,780,677.17 -> £3,395,264.68 (10.2%); £3,780,677.43 -> £3,395,264.81 (10.2%); £3,780,677.68 -> £3,395,264.93 (10.2%); £3,780,677.92 -> £3,395,265.05 (10.2%); £3,780,678.16 -> £3,395,265.17 (10.2%); £3,780,678.41 -> £3,395,265.29 (10.2%); £3,780,678.66 -> £3,395,265.32 (10.2%); £3,780,678.91 -> £3,395,265.35 (10.2%); £3,780,679.15 -> £3,395,265.37 (10.2%); £3,780,679.36 -> £3,395,265.39 (10.2%); £3,780,679.55 -> £3,395,265.41 (10.2%); £3,780,679.71 -> £3,395,265.43 (10.2%); £3,780,679.86 -> £3,395,265.45 (10.2%); £3,780,680.01 -> £3,395,265.47 (10.2%); £3,780,680.16 -> £3,395,265.48 (10.2%); £3,780,680.31 -> £3,395,265.50 (10.2%); £3,780,680.47 -> £3,395,265.52 (10.2%); £3,780,680.62 -> £3,395,265.53 (10.2%); £3,780,680.77 -> £3,395,265.55 (10.2%); £3,780,680.92 -> £3,395,265.57 (10.2%); £3,780,681.07 -> £3,395,265.58 (10.2%); £3,780,681.22 -> £3,395,265.60 (10.2%); £3,780,681.38 -> £3,395,265.68 (10.2%); £3,780,681.52 -> £3,395,265.75 (10.2%); £3,780,681.69 -> £3,395,265.84 (10.2%); £3,780,681.87 -> £3,395,265.92 (10.2%); £3,780,682.07 -> £3,395,266.01 (10.2%); £3,780,682.29 -> £3,395,266.10 (10.2%); £3,780,682.53 -> £3,395,266.18 (10.2%); £3,780,682.78 -> £3,395,266.26 (10.2%); £3,780,683.03 -> £3,395,266.29 (10.2%); £3,780,683.28 -> £3,395,266.31 (10.2%); £3,780,683.53 -> £3,395,266.34 (10.2%); £3,780,683.79 -> £3,395,266.36 (10.2%); £3,780,684.04 -> £3,395,266.39 (10.2%); £3,780,684.28 -> £3,395,266.41 (10.2%); £3,780,684.54 -> £3,395,266.43 (10.2%); £3,780,684.80 -> £3,395,266.46 (10.2%); £3,780,685.05 -> £3,395,266.48 (10.2%); £3,780,685.29 -> £3,395,266.50 (10.2%); £3,780,685.54 -> £3,395,266.53 (10.2%); £3,780,685.78 -> £3,395,266.55 (10.2%); £3,780,686.03 -> £3,395,266.58 (10.2%); £3,780,686.28 -> £3,395,266.67 (10.2%); £3,780,686.53 -> £3,395,266.77 (10.2%); £3,780,686.78 -> £3,395,266.87 (10.2%); £3,780,687.03 -> £3,395,266.97 (10.2%); £3,780,687.27 -> £3,395,267.07 (10.2%); £3,780,687.52 -> £3,395,267.17 (10.2%); £3,780,687.77 -> £3,395,267.27 (10.2%); £3,780,688.03 -> £3,395,267.36 (10.2%); £3,780,688.27 -> £3,395,267.46 (10.2%); £3,780,688.51 -> £3,395,267.55 (10.2%); £3,780,688.76 -> £3,395,267.64 (10.2%); £3,780,689.01 -> £3,395,267.67 (10.2%); £3,780,689.27 -> £3,395,267.70 (10.2%); £3,780,689.51 -> £3,395,267.72 (10.2%); £3,780,689.71 -> £3,395,267.75 (10.2%); £3,780,689.91 -> £3,395,267.77 (10.2%); £3,780,690.06 -> £3,395,267.79 (10.2%); £3,780,690.21 -> £3,395,267.80 (10.2%); £3,780,690.36 -> £3,395,267.82 (10.2%); £3,780,690.52 -> £3,395,267.84 (10.2%); £3,780,690.67 -> £3,395,267.85 (10.2%); £3,780,690.82 -> £3,395,267.87 (10.2%); £3,780,690.97 -> £3,395,267.89 (10.2%); £3,780,691.12 -> £3,395,267.90 (10.2%); £3,780,691.27 -> £3,395,267.92 (10.2%); £3,780,691.42 -> £3,395,267.94 (10.2%); £3,780,691.58 -> £3,395,267.95 (10.2%); £3,780,691.72 -> £3,395,268.03 (10.2%); £3,780,691.87 -> £3,395,268.10 (10.2%); £3,780,692.04 -> £3,395,268.19 (10.2%); £3,780,692.22 -> £3,395,268.27 (10.2%); £3,780,692.42 -> £3,395,268.35 (10.2%); £3,780,692.64 -> £3,395,268.44 (10.2%); £3,780,692.87 -> £3,395,268.52 (10.2%); £3,780,693.12 -> £3,395,268.60 (10.2%); £3,780,693.37 -> £3,395,268.62 (10.2%); £3,780,693.62 -> £3,395,268.65 (10.2%); £3,780,693.88 -> £3,395,268.67 (10.2%); £3,780,694.13 -> £3,395,268.69 (10.2%); £3,780,694.38 -> £3,395,268.72 (10.2%); £3,780,694.64 -> £3,395,268.74 (10.2%); £3,780,694.89 -> £3,395,268.77 (10.2%); £3,780,695.14 -> £3,395,268.79 (10.2%); £3,780,695.39 -> £3,395,268.81 (10.2%); £3,780,695.64 -> £3,395,268.83 (10.2%); £3,780,695.89 -> £3,395,268.86 (10.2%); £3,780,696.15 -> £3,395,268.88 (10.2%); £3,780,696.40 -> £3,395,268.91 (10.2%); £3,780,696.66 -> £3,395,269.00 (10.2%); £3,780,696.92 -> £3,395,269.09 (10.2%); £3,780,697.17 -> £3,395,269.19 (10.2%); £3,780,697.43 -> £3,395,269.29 (10.2%); £3,780,697.69 -> £3,395,269.39 (10.2%); £3,780,697.93 -> £3,395,269.48 (10.2%); £3,780,698.18 -> £3,395,269.58 (10.2%); £3,780,698.44 -> £3,395,269.67 (10.2%); £3,780,698.69 -> £3,395,269.76 (10.2%); £3,780,698.94 -> £3,395,269.86 (10.2%); £3,780,699.18 -> £3,395,269.95 (10.2%); £3,780,699.44 -> £3,395,269.98 (10.2%); £3,780,699.70 -> £3,395,270.00 (10.2%); £3,780,699.92 -> £3,395,270.03 (10.2%); £3,780,700.14 -> £3,395,270.05 (10.2%); £3,780,700.34 -> £3,395,270.07 (10.2%); £3,780,700.48 -> £3,395,270.09 (10.2%); £3,780,700.64 -> £3,395,270.11 (10.2%); £3,780,700.79 -> £3,395,270.12 (10.2%); £3,780,700.94 -> £3,395,270.14 (10.2%); £3,780,701.09 -> £3,395,270.16 (10.2%); £3,780,701.24 -> £3,395,270.17 (10.2%); £3,780,701.40 -> £3,395,270.19 (10.2%); £3,780,701.55 -> £3,395,270.21 (10.2%); £3,780,701.70 -> £3,395,270.22 (10.2%); £3,780,701.85 -> £3,395,270.24 (10.2%); £3,780,702.00 -> £3,395,270.26 (10.2%); £3,780,702.15 -> £3,395,270.36 (10.2%); £3,780,702.30 -> £3,395,270.47 (10.2%); £3,780,702.47 -> £3,395,270.59 (10.2%); £3,780,702.65 -> £3,395,270.71 (10.2%); £3,780,702.86 -> £3,395,270.83 (10.2%); £3,780,703.07 -> £3,395,270.94 (10.2%); £3,780,703.31 -> £3,395,271.05 (10.2%); £3,780,703.56 -> £3,395,271.16 (10.2%); £3,780,703.82 -> £3,395,271.18 (10.2%); £3,780,704.07 -> £3,395,271.21 (10.2%); £3,780,704.31 -> £3,395,271.23 (10.2%); £3,780,704.57 -> £3,395,271.25 (10.2%); £3,780,704.81 -> £3,395,271.28 (10.2%); £3,780,705.07 -> £3,395,271.30 (10.2%); £3,780,705.32 -> £3,395,271.33 (10.2%); £3,780,705.57 -> £3,395,271.35 (10.2%); £3,780,705.83 -> £3,395,271.38 (10.2%); £3,780,706.08 -> £3,395,271.40 (10.2%); £3,780,706.33 -> £3,395,271.42 (10.2%); £3,780,706.58 -> £3,395,271.45 (10.2%); £3,780,706.83 -> £3,395,271.48 (10.2%); £3,780,707.08 -> £3,395,271.59 (10.2%); £3,780,707.34 -> £3,395,271.71 (10.2%); £3,780,707.59 -> £3,395,271.83 (10.2%); £3,780,707.84 -> £3,395,271.96 (10.2%); £3,780,708.09 -> £3,395,272.09 (10.2%); £3,780,708.34 -> £3,395,272.21 (10.2%); £3,780,708.59 -> £3,395,272.32 (10.2%); £3,780,708.84 -> £3,395,272.44 (10.2%); £3,780,709.10 -> £3,395,272.55 (10.2%); £3,780,709.35 -> £3,395,272.67 (10.2%); £3,780,709.61 -> £3,395,272.79 (10.2%); £3,780,709.86 -> £3,395,272.81 (10.2%); £3,780,710.11 -> £3,395,272.84 (10.2%); £3,780,710.34 -> £3,395,272.87 (10.2%); £3,780,710.55 -> £3,395,272.89 (10.2%); £3,780,710.74 -> £3,395,272.91 (10.2%); £3,780,710.87 -> £3,395,272.93 (10.2%); £3,780,711.01 -> £3,395,272.95 (10.2%); £3,780,711.14 -> £3,395,272.97 (10.2%); £3,780,711.28 -> £3,395,272.98 (10.2%); £3,780,711.42 -> £3,395,273.00 (10.2%); £3,780,711.55 -> £3,395,273.02 (10.2%); £3,780,711.69 -> £3,395,273.03 (10.2%); £3,780,711.82 -> £3,395,273.05 (10.2%); £3,780,711.96 -> £3,395,273.07 (10.2%); £3,780,712.09 -> £3,395,273.08 (10.2%); £3,780,712.23 -> £3,395,273.10 (10.2%); £3,780,712.36 -> £3,395,273.24 (10.2%); £3,780,712.50 -> £3,395,273.38 (10.2%); £3,780,712.65 -> £3,395,273.53 (10.2%); £3,780,712.82 -> £3,395,273.67 (10.2%); £3,780,713.00 -> £3,395,273.82 (10.2%); £3,780,713.20 -> £3,395,273.97 (10.2%); £3,780,713.41 -> £3,395,274.12 (10.2%); £3,780,713.63 -> £3,395,274.28 (10.2%); £3,780,713.85 -> £3,395,274.30 (10.2%); £3,780,714.08 -> £3,395,274.33 (10.2%); £3,780,714.30 -> £3,395,274.36 (10.2%); £3,780,714.53 -> £3,395,274.38 (10.2%); £3,780,714.75 -> £3,395,274.41 (10.2%); £3,780,714.97 -> £3,395,274.44 (10.2%); £3,780,715.20 -> £3,395,274.46 (10.2%); £3,780,715.43 -> £3,395,274.49 (10.2%); £3,780,715.64 -> £3,395,274.51 (10.2%); £3,780,715.85 -> £3,395,274.54 (10.2%); £3,780,716.08 -> £3,395,274.56 (10.2%); £3,780,716.29 -> £3,395,274.59 (10.2%); £3,780,716.51 -> £3,395,274.62 (10.2%); £3,780,716.74 -> £3,395,274.77 (10.2%); £3,780,716.96 -> £3,395,274.92 (10.2%); £3,780,717.19 -> £3,395,275.07 (10.2%); £3,780,717.42 -> £3,395,275.23 (10.2%); £3,780,717.64 -> £3,395,275.38 (10.2%); £3,780,717.87 -> £3,395,275.54 (10.2%); £3,780,718.09 -> £3,395,275.69 (10.2%); £3,780,718.31 -> £3,395,275.85 (10.2%); £3,780,718.54 -> £3,395,276.00 (10.2%); £3,780,718.76 -> £3,395,276.15 (10.2%); £3,780,718.98 -> £3,395,276.31 (10.2%); £3,780,719.20 -> £3,395,276.34 (10.2%); £3,780,719.43 -> £3,395,276.37 (10.2%); £3,780,719.63 -> £3,395,276.39 (10.2%); £3,780,719.82 -> £3,395,276.41 (10.2%); £3,780,720.00 -> £3,395,276.44 (10.2%); £3,780,720.13 -> £3,395,276.46 (10.2%); £3,780,720.26 -> £3,395,276.48 (10.2%); £3,780,720.40 -> £3,395,276.49 (10.2%); £3,780,720.53 -> £3,395,276.51 (10.2%); £3,780,720.67 -> £3,395,276.53 (10.2%); £3,780,720.80 -> £3,395,276.55 (10.2%); £3,780,720.93 -> £3,395,276.56 (10.2%); £3,780,721.07 -> £3,395,276.58 (10.2%); £3,780,721.21 -> £3,395,276.60 (10.2%); £3,780,721.35 -> £3,395,276.61 (10.2%); £3,780,721.49 -> £3,395,276.63 (10.2%); £3,780,721.62 -> £3,395,276.70 (10.2%); £3,780,721.76 -> £3,395,276.78 (10.2%); £3,780,721.90 -> £3,395,276.86 (10.2%); £3,780,722.07 -> £3,395,276.93 (10.2%); £3,780,722.25 -> £3,395,277.01 (10.2%); £3,780,722.45 -> £3,395,277.10 (10.2%); £3,780,722.66 -> £3,395,277.18 (10.2%); £3,780,722.89 -> £3,395,277.27 (10.2%); £3,780,723.12 -> £3,395,277.30 (10.2%); £3,780,723.35 -> £3,395,277.32 (10.2%); £3,780,723.57 -> £3,395,277.36 (10.2%); £3,780,723.79 -> £3,395,277.39 (10.2%); £3,780,724.02 -> £3,395,277.42 (10.2%); £3,780,724.25 -> £3,395,277.45 (10.2%); £3,780,724.48 -> £3,395,277.48 (10.2%); £3,780,724.71 -> £3,395,277.51 (10.2%); £3,780,724.93 -> £3,395,277.54 (10.2%); £3,780,725.16 -> £3,395,277.57 (10.2%); £3,780,725.39 -> £3,395,277.59 (10.2%); £3,780,725.62 -> £3,395,277.62 (10.2%); £3,780,725.84 -> £3,395,277.65 (10.2%); £3,780,726.07 -> £3,395,277.75 (10.2%); £3,780,726.29 -> £3,395,277.85 (10.2%); £3,780,726.52 -> £3,395,277.95 (10.2%); £3,780,726.75 -> £3,395,278.05 (10.2%); £3,780,726.97 -> £3,395,278.15 (10.2%); £3,780,727.20 -> £3,395,278.24 (10.2%); £3,780,727.42 -> £3,395,278.34 (10.2%); £3,780,727.65 -> £3,395,278.44 (10.2%); £3,780,727.87 -> £3,395,278.53 (10.2%); £3,780,728.09 -> £3,395,278.62 (10.2%); £3,780,728.32 -> £3,395,278.72 (10.2%); £3,780,728.55 -> £3,395,278.75 (10.2%); £3,780,728.77 -> £3,395,278.78 (10.2%); £3,780,728.99 -> £3,395,278.80 (10.2%); £3,780,729.18 -> £3,395,278.82 (10.2%); £3,780,729.36 -> £3,395,278.84 (10.2%); £3,780,729.52 -> £3,395,278.86 (10.2%); £3,780,729.67 -> £3,395,278.88 (10.2%); £3,780,729.82 -> £3,395,278.90 (10.2%); £3,780,729.98 -> £3,395,278.91 (10.2%); £3,780,730.13 -> £3,395,278.93 (10.2%); £3,780,730.28 -> £3,395,278.95 (10.2%); £3,780,730.44 -> £3,395,278.96 (10.2%); £3,780,730.59 -> £3,395,278.98 (10.2%); £3,780,730.74 -> £3,395,279.00 (10.2%); £3,780,730.89 -> £3,395,279.01 (10.2%); £3,780,731.05 -> £3,395,279.03 (10.2%); £3,780,731.20 -> £3,395,279.13 (10.2%); £3,780,731.36 -> £3,395,279.23 (10.2%); £3,780,731.53 -> £3,395,279.33 (10.2%); £3,780,731.72 -> £3,395,279.43 (10.2%); £3,780,731.92 -> £3,395,279.54 (10.2%); £3,780,732.14 -> £3,395,279.65 (10.2%); £3,780,732.39 -> £3,395,279.76 (10.2%); £3,780,732.65 -> £3,395,279.86 (10.2%); £3,780,732.90 -> £3,395,279.89 (10.2%); £3,780,733.15 -> £3,395,279.91 (10.2%); £3,780,733.41 -> £3,395,279.93 (10.2%); £3,780,733.66 -> £3,395,279.96 (10.2%); £3,780,733.90 -> £3,395,279.98 (10.2%); £3,780,734.16 -> £3,395,280.01 (10.2%); £3,780,734.41 -> £3,395,280.03 (10.2%); £3,780,734.67 -> £3,395,280.05 (10.2%); £3,780,734.94 -> £3,395,280.08 (10.2%); £3,780,735.19 -> £3,395,280.10 (10.2%); £3,780,735.45 -> £3,395,280.12 (10.2%); £3,780,735.71 -> £3,395,280.15 (10.2%); £3,780,735.97 -> £3,395,280.18 (10.2%); £3,780,736.23 -> £3,395,280.29 (10.2%); £3,780,736.48 -> £3,395,280.41 (10.2%); £3,780,736.74 -> £3,395,280.54 (10.2%); £3,780,736.99 -> £3,395,280.65 (10.2%); £3,780,737.26 -> £3,395,280.77 (10.2%); £3,780,737.52 -> £3,395,280.89 (10.2%); £3,780,737.77 -> £3,395,281.01 (10.2%); £3,780,738.02 -> £3,395,281.12 (10.2%); £3,780,738.28 -> £3,395,281.24 (10.2%); £3,780,738.53 -> £3,395,281.36 (10.2%); £3,780,738.79 -> £3,395,281.47 (10.2%); £3,780,739.05 -> £3,395,281.50 (10.2%); £3,780,739.31 -> £3,395,281.53 (10.2%); £3,780,739.54 -> £3,395,281.55 (10.2%); £3,780,739.76 -> £3,395,281.58 (10.2%); £3,780,739.95 -> £3,395,281.60 (10.2%); £3,780,740.11 -> £3,395,281.62 (10.2%); £3,780,740.27 -> £3,395,281.63 (10.2%); £3,780,740.42 -> £3,395,281.65 (10.2%); £3,780,740.57 -> £3,395,281.67 (10.2%); £3,780,740.73 -> £3,395,281.68 (10.2%); £3,780,740.88 -> £3,395,281.70 (10.2%); £3,780,741.04 -> £3,395,281.72 (10.2%); £3,780,741.19 -> £3,395,281.73 (10.2%); £3,780,741.35 -> £3,395,281.75 (10.2%); £3,780,741.50 -> £3,395,281.77 (10.2%); £3,780,741.66 -> £3,395,281.79 (10.2%); £3,780,741.81 -> £3,395,281.87 (10.2%); £3,780,741.97 -> £3,395,281.95 (10.2%); £3,780,742.14 -> £3,395,282.04 (10.2%); £3,780,742.34 -> £3,395,282.13 (10.2%); £3,780,742.55 -> £3,395,282.22 (10.2%); £3,780,742.77 -> £3,395,282.31 (10.2%); £3,780,743.01 -> £3,395,282.41 (10.2%); £3,780,743.27 -> £3,395,282.50 (10.2%); £3,780,743.52 -> £3,395,282.52 (10.2%); £3,780,743.77 -> £3,395,282.54 (10.2%); £3,780,744.03 -> £3,395,282.57 (10.2%); £3,780,744.29 -> £3,395,282.59 (10.2%); £3,780,744.54 -> £3,395,282.62 (10.2%); £3,780,744.80 -> £3,395,282.64 (10.2%); £3,780,745.07 -> £3,395,282.66 (10.2%); £3,780,745.33 -> £3,395,282.69 (10.2%); £3,780,745.60 -> £3,395,282.71 (10.2%); £3,780,745.85 -> £3,395,282.73 (10.2%); £3,780,746.11 -> £3,395,282.76 (10.2%); £3,780,746.38 -> £3,395,282.78 (10.2%); £3,780,746.63 -> £3,395,282.81 (10.2%); £3,780,746.88 -> £3,395,282.91 (10.2%); £3,780,747.14 -> £3,395,283.00 (10.2%); £3,780,747.40 -> £3,395,283.10 (10.2%); £3,780,747.65 -> £3,395,283.20 (10.2%); £3,780,747.91 -> £3,395,283.30 (10.2%); £3,780,748.17 -> £3,395,283.40 (10.2%); £3,780,748.43 -> £3,395,283.51 (10.2%); £3,780,748.69 -> £3,395,283.61 (10.2%); £3,780,748.95 -> £3,395,283.70 (10.2%); £3,780,749.20 -> £3,395,283.80 (10.2%); £3,780,749.45 -> £3,395,283.90 (10.2%); £3,780,749.71 -> £3,395,283.92 (10.2%); £3,780,749.97 -> £3,395,283.95 (10.2%); £3,780,750.21 -> £3,395,283.98 (10.2%); £3,780,750.43 -> £3,395,284.00 (10.2%); £3,780,750.62 -> £3,395,284.02 (10.2%); £3,780,750.77 -> £3,395,284.04 (10.2%); £3,780,750.93 -> £3,395,284.05 (10.2%); £3,780,751.08 -> £3,395,284.07 (10.2%); £3,780,751.24 -> £3,395,284.09 (10.2%); £3,780,751.39 -> £3,395,284.10 (10.2%); £3,780,751.54 -> £3,395,284.12 (10.2%); £3,780,751.70 -> £3,395,284.14 (10.2%); £3,780,751.85 -> £3,395,284.15 (10.2%); £3,780,752.01 -> £3,395,284.17 (10.2%); £3,780,752.17 -> £3,395,284.19 (10.2%); £3,780,752.33 -> £3,395,284.20 (10.2%); £3,780,752.48 -> £3,395,284.30 (10.2%); £3,780,752.64 -> £3,395,284.40 (10.2%); £3,780,752.81 -> £3,395,284.51 (10.2%); £3,780,752.99 -> £3,395,284.62 (10.2%); £3,780,753.20 -> £3,395,284.73 (10.2%); £3,780,753.43 -> £3,395,284.84 (10.2%); £3,780,753.68 -> £3,395,284.94 (10.2%); £3,780,753.94 -> £3,395,285.05 (10.2%); £3,780,754.19 -> £3,395,285.07 (10.2%); £3,780,754.45 -> £3,395,285.10 (10.2%); £3,780,754.70 -> £3,395,285.12 (10.2%); £3,780,754.96 -> £3,395,285.14 (10.2%); £3,780,755.22 -> £3,395,285.17 (10.2%); £3,780,755.47 -> £3,395,285.19 (10.2%); £3,780,755.73 -> £3,395,285.21 (10.2%); £3,780,755.98 -> £3,395,285.24 (10.2%); £3,780,756.23 -> £3,395,285.26 (10.2%); £3,780,756.49 -> £3,395,285.28 (10.2%); £3,780,756.75 -> £3,395,285.31 (10.2%); £3,780,757.00 -> £3,395,285.33 (10.2%); £3,780,757.26 -> £3,395,285.36 (10.2%); £3,780,757.52 -> £3,395,285.48 (10.2%); £3,780,757.78 -> £3,395,285.60 (10.2%); £3,780,758.04 -> £3,395,285.72 (10.2%); £3,780,758.30 -> £3,395,285.83 (10.2%); £3,780,758.55 -> £3,395,285.94 (10.2%); £3,780,758.81 -> £3,395,286.06 (10.2%); £3,780,759.07 -> £3,395,286.17 (10.2%); £3,780,759.33 -> £3,395,286.29 (10.2%); £3,780,759.58 -> £3,395,286.40 (10.2%); £3,780,759.84 -> £3,395,286.52 (10.2%); £3,780,760.09 -> £3,395,286.64 (10.2%); £3,780,760.34 -> £3,395,286.67 (10.2%); £3,780,760.60 -> £3,395,286.69 (10.2%); £3,780,760.84 -> £3,395,286.72 (10.2%); £3,780,761.07 -> £3,395,286.74 (10.2%); £3,780,761.27 -> £3,395,286.76 (10.2%); £3,780,761.43 -> £3,395,286.78 (10.2%); £3,780,761.58 -> £3,395,286.80 (10.2%); £3,780,761.73 -> £3,395,286.81 (10.2%); £3,780,761.88 -> £3,395,286.83 (10.2%); £3,780,762.04 -> £3,395,286.85 (10.2%); £3,780,762.19 -> £3,395,286.86 (10.2%); £3,780,762.34 -> £3,395,286.88 (10.2%); £3,780,762.49 -> £3,395,286.90 (10.2%); £3,780,762.64 -> £3,395,286.91 (10.2%); £3,780,762.79 -> £3,395,286.93 (10.2%); £3,780,762.94 -> £3,395,286.95 (10.2%); £3,780,763.10 -> £3,395,287.06 (10.2%); £3,780,763.25 -> £3,395,287.18 (10.2%); £3,780,763.43 -> £3,395,287.30 (10.2%); £3,780,763.61 -> £3,395,287.42 (10.2%); £3,780,763.81 -> £3,395,287.54 (10.2%); £3,780,764.04 -> £3,395,287.66 (10.2%); £3,780,764.28 -> £3,395,287.78 (10.2%); £3,780,764.53 -> £3,395,287.90 (10.2%); £3,780,764.79 -> £3,395,287.93 (10.2%); £3,780,765.05 -> £3,395,287.95 (10.2%); £3,780,765.30 -> £3,395,287.97 (10.2%); £3,780,765.55 -> £3,395,288.00 (10.2%); £3,780,765.82 -> £3,395,288.02 (10.2%); £3,780,766.07 -> £3,395,288.05 (10.2%); £3,780,766.33 -> £3,395,288.07 (10.2%); £3,780,766.58 -> £3,395,288.09 (10.2%); £3,780,766.83 -> £3,395,288.12 (10.2%); £3,780,767.09 -> £3,395,288.14 (10.2%); £3,780,767.35 -> £3,395,288.16 (10.2%); £3,780,767.60 -> £3,395,288.19 (10.2%); £3,780,767.86 -> £3,395,288.22 (10.2%); £3,780,768.11 -> £3,395,288.35 (10.2%); £3,780,768.36 -> £3,395,288.48 (10.2%); £3,780,768.62 -> £3,395,288.62 (10.2%); £3,780,768.88 -> £3,395,288.75 (10.2%); £3,780,769.14 -> £3,395,288.89 (10.2%); £3,780,769.39 -> £3,395,289.02 (10.2%); £3,780,769.65 -> £3,395,289.16 (10.2%); £3,780,769.91 -> £3,395,289.29 (10.2%); £3,780,770.16 -> £3,395,289.42 (10.2%); £3,780,770.41 -> £3,395,289.55 (10.2%); £3,780,770.66 -> £3,395,289.68 (10.2%); £3,780,770.92 -> £3,395,289.71 (10.2%); £3,780,771.17 -> £3,395,289.73 (10.2%); £3,780,771.41 -> £3,395,289.76 (10.2%); £3,780,771.63 -> £3,395,289.78 (10.2%); £3,780,771.83 -> £3,395,289.80 (10.2%); £3,780,771.99 -> £3,395,289.82 (10.2%); £3,780,772.14 -> £3,395,289.84 (10.2%); £3,780,772.29 -> £3,395,289.86 (10.2%); £3,780,772.44 -> £3,395,289.87 (10.2%); £3,780,772.60 -> £3,395,289.89 (10.2%); £3,780,772.75 -> £3,395,289.91 (10.2%); £3,780,772.90 -> £3,395,289.92 (10.2%); £3,780,773.05 -> £3,395,289.94 (10.2%); £3,780,773.20 -> £3,395,289.96 (10.2%); £3,780,773.35 -> £3,395,289.97 (10.2%); £3,780,773.50 -> £3,395,289.99 (10.2%); £3,780,773.66 -> £3,395,290.11 (10.2%); £3,780,773.81 -> £3,395,290.22 (10.2%); £3,780,773.98 -> £3,395,290.36 (10.2%); £3,780,774.17 -> £3,395,290.49 (10.2%); £3,780,774.39 -> £3,395,290.61 (10.2%); £3,780,774.60 -> £3,395,290.74 (10.2%); £3,780,774.85 -> £3,395,290.87 (10.2%); £3,780,775.11 -> £3,395,291.00 (10.2%); £3,780,775.37 -> £3,395,291.02 (10.2%); £3,780,775.64 -> £3,395,291.04 (10.2%); £3,780,775.89 -> £3,395,291.07 (10.2%); £3,780,776.15 -> £3,395,291.09 (10.2%); £3,780,776.41 -> £3,395,291.12 (10.2%); £3,780,776.67 -> £3,395,291.14 (10.2%); £3,780,776.92 -> £3,395,291.16 (10.2%); £3,780,777.18 -> £3,395,291.19 (10.2%); £3,780,777.43 -> £3,395,291.21 (10.2%); £3,780,777.69 -> £3,395,291.24 (10.2%); £3,780,777.95 -> £3,395,291.26 (10.2%); £3,780,778.21 -> £3,395,291.29 (10.2%); £3,780,778.47 -> £3,395,291.32 (10.2%); £3,780,778.72 -> £3,395,291.45 (10.2%); £3,780,778.98 -> £3,395,291.59 (10.2%); £3,780,779.24 -> £3,395,291.72 (10.2%); £3,780,779.50 -> £3,395,291.86 (10.2%); £3,780,779.75 -> £3,395,292.00 (10.2%); £3,780,780.01 -> £3,395,292.13 (10.2%); £3,780,780.27 -> £3,395,292.26 (10.2%); £3,780,780.53 -> £3,395,292.40 (10.2%); £3,780,780.79 -> £3,395,292.53 (10.2%); £3,780,781.04 -> £3,395,292.66 (10.2%); £3,780,781.30 -> £3,395,292.80 (10.2%); £3,780,781.56 -> £3,395,292.83 (10.2%); £3,780,781.82 -> £3,395,292.86 (10.2%); £3,780,782.06 -> £3,395,292.88 (10.2%); £3,780,782.28 -> £3,395,292.90 (10.2%); £3,780,782.48 -> £3,395,292.92 (10.2%); £3,780,782.62 -> £3,395,292.94 (10.2%); £3,780,782.75 -> £3,395,292.96 (10.2%); £3,780,782.89 -> £3,395,292.98 (10.2%); £3,780,783.03 -> £3,395,293.00 (10.2%); £3,780,783.16 -> £3,395,293.02 (10.2%); £3,780,783.30 -> £3,395,293.03 (10.2%); £3,780,783.43 -> £3,395,293.05 (10.2%); £3,780,783.57 -> £3,395,293.07 (10.2%); £3,780,783.71 -> £3,395,293.08 (10.2%); £3,780,783.84 -> £3,395,293.10 (10.2%); £3,780,783.98 -> £3,395,293.12 (10.2%); £3,780,784.11 -> £3,395,293.28 (10.2%); £3,780,784.24 -> £3,395,293.45 (10.2%); £3,780,784.40 -> £3,395,293.62 (10.2%); £3,780,784.56 -> £3,395,293.80 (10.2%); £3,780,784.75 -> £3,395,293.98 (10.2%); £3,780,784.94 -> £3,395,294.16 (10.2%); £3,780,785.16 -> £3,395,294.34 (10.2%); £3,780,785.38 -> £3,395,294.52 (10.2%); £3,780,785.61 -> £3,395,294.55 (10.2%); £3,780,785.84 -> £3,395,294.58 (10.2%); £3,780,786.06 -> £3,395,294.61 (10.2%); £3,780,786.29 -> £3,395,294.63 (10.2%); £3,780,786.51 -> £3,395,294.66 (10.2%); £3,780,786.74 -> £3,395,294.69 (10.2%); £3,780,786.97 -> £3,395,294.72 (10.2%); £3,780,787.20 -> £3,395,294.74 (10.2%); £3,780,787.43 -> £3,395,294.77 (10.2%); £3,780,787.65 -> £3,395,294.80 (10.2%); £3,780,787.87 -> £3,395,294.82 (10.2%); £3,780,788.09 -> £3,395,294.85 (10.2%); £3,780,788.32 -> £3,395,294.88 (10.2%); £3,780,788.55 -> £3,395,295.05 (10.2%); £3,780,788.78 -> £3,395,295.22 (10.2%); £3,780,789.01 -> £3,395,295.40 (10.2%); £3,780,789.25 -> £3,395,295.57 (10.2%); £3,780,789.48 -> £3,395,295.74 (10.2%); £3,780,789.70 -> £3,395,295.91 (10.2%); £3,780,789.93 -> £3,395,296.08 (10.2%); £3,780,790.15 -> £3,395,296.27 (10.2%); £3,780,790.38 -> £3,395,296.45 (10.2%); £3,780,790.60 -> £3,395,296.61 (10.2%); £3,780,790.83 -> £3,395,296.79 (10.2%); £3,780,791.06 -> £3,395,296.82 (10.2%); £3,780,791.28 -> £3,395,296.85 (10.2%); £3,780,791.49 -> £3,395,296.87 (10.2%); £3,780,791.68 -> £3,395,296.90 (10.2%); £3,780,791.85 -> £3,395,296.92 (10.2%); £3,780,792.00 -> £3,395,296.94 (10.2%); £3,780,792.13 -> £3,395,296.96 (10.2%); £3,780,792.28 -> £3,395,296.98 (10.2%); £3,780,792.42 -> £3,395,297.00 (10.2%); £3,780,792.56 -> £3,395,297.01 (10.2%); £3,780,792.70 -> £3,395,297.03 (10.2%); £3,780,792.84 -> £3,395,297.05 (10.2%); £3,780,792.98 -> £3,395,297.07 (10.2%); £3,780,793.12 -> £3,395,297.08 (10.2%); £3,780,793.26 -> £3,395,297.10 (10.2%); £3,780,793.41 -> £3,395,297.12 (10.2%); £3,780,793.55 -> £3,395,297.26 (10.2%); £3,780,793.70 -> £3,395,297.41 (10.2%); £3,780,793.85 -> £3,395,297.55 (10.2%); £3,780,794.02 -> £3,395,297.70 (10.2%); £3,780,794.20 -> £3,395,297.86 (10.2%); £3,780,794.41 -> £3,395,298.01 (10.2%); £3,780,794.62 -> £3,395,298.17 (10.2%); £3,780,794.85 -> £3,395,298.33 (10.2%); £3,780,795.09 -> £3,395,298.36 (10.2%); £3,780,795.33 -> £3,395,298.39 (10.2%); £3,780,795.55 -> £3,395,298.42 (10.2%); £3,780,795.78 -> £3,395,298.45 (10.2%); £3,780,796.01 -> £3,395,298.48 (10.2%); £3,780,796.25 -> £3,395,298.52 (10.2%); £3,780,796.48 -> £3,395,298.55 (10.2%); £3,780,796.71 -> £3,395,298.58 (10.2%); £3,780,796.94 -> £3,395,298.61 (10.2%); £3,780,797.17 -> £3,395,298.63 (10.2%); £3,780,797.41 -> £3,395,298.66 (10.2%); £3,780,797.63 -> £3,395,298.69 (10.2%); £3,780,797.87 -> £3,395,298.72 (10.2%); £3,780,798.10 -> £3,395,298.87 (10.2%); £3,780,798.34 -> £3,395,299.02 (10.2%); £3,780,798.57 -> £3,395,299.17 (10.2%); £3,780,798.80 -> £3,395,299.33 (10.2%); £3,780,799.03 -> £3,395,299.48 (10.2%); £3,780,799.27 -> £3,395,299.63 (10.2%); £3,780,799.50 -> £3,395,299.78 (10.2%); £3,780,799.74 -> £3,395,299.93 (10.2%); £3,780,799.98 -> £3,395,300.08 (10.2%); £3,780,800.21 -> £3,395,300.23 (10.2%); £3,780,800.45 -> £3,395,300.39 (10.2%); £3,780,800.68 -> £3,395,300.42 (10.2%); £3,780,800.92 -> £3,395,300.44 (10.2%); £3,780,801.15 -> £3,395,300.47 (10.2%); £3,780,801.34 -> £3,395,300.49 (10.2%); £3,780,801.52 -> £3,395,300.51 (10.2%); £3,780,801.68 -> £3,395,300.53 (10.2%); £3,780,801.84 -> £3,395,300.55 (10.2%); £3,780,802.00 -> £3,395,300.56 (10.2%); £3,780,802.16 -> £3,395,300.58 (10.2%); £3,780,802.33 -> £3,395,300.60 (10.2%); £3,780,802.49 -> £3,395,300.61 (10.2%); £3,780,802.65 -> £3,395,300.63 (10.2%); £3,780,802.82 -> £3,395,300.65 (10.2%); £3,780,802.98 -> £3,395,300.66 (10.2%); £3,780,803.14 -> £3,395,300.68 (10.2%); £3,780,803.30 -> £3,395,300.70 (10.2%); £3,780,803.46 -> £3,395,300.84 (10.2%); £3,780,803.62 -> £3,395,300.97 (10.2%); £3,780,803.80 -> £3,395,301.12 (10.2%); £3,780,804.00 -> £3,395,301.27 (10.2%); £3,780,804.21 -> £3,395,301.42 (10.2%); £3,780,804.44 -> £3,395,301.57 (10.2%); £3,780,804.70 -> £3,395,301.71 (10.2%); £3,780,804.97 -> £3,395,301.86 (10.2%); £3,780,805.24 -> £3,395,301.89 (10.2%); £3,780,805.52 -> £3,395,301.91 (10.2%); £3,780,805.80 -> £3,395,301.93 (10.2%); £3,780,806.06 -> £3,395,301.96 (10.2%); £3,780,806.33 -> £3,395,301.98 (10.2%); £3,780,806.60 -> £3,395,302.01 (10.2%); £3,780,806.87 -> £3,395,302.03 (10.2%); £3,780,807.14 -> £3,395,302.05 (10.2%); £3,780,807.42 -> £3,395,302.08 (10.2%); £3,780,807.69 -> £3,395,302.10 (10.2%); £3,780,807.96 -> £3,395,302.12 (10.2%); £3,780,808.23 -> £3,395,302.15 (10.2%); £3,780,808.51 -> £3,395,302.18 (10.2%); £3,780,808.77 -> £3,395,302.32 (10.2%); £3,780,809.04 -> £3,395,302.47 (10.2%); £3,780,809.31 -> £3,395,302.62 (10.2%); £3,780,809.57 -> £3,395,302.77 (10.2%); £3,780,809.83 -> £3,395,302.92 (10.2%); £3,780,810.10 -> £3,395,303.07 (10.2%); £3,780,810.36 -> £3,395,303.22 (10.2%); £3,780,810.63 -> £3,395,303.36 (10.2%); £3,780,810.90 -> £3,395,303.51 (10.2%); £3,780,811.17 -> £3,395,303.66 (10.2%); £3,780,811.43 -> £3,395,303.80 (10.2%); £3,780,811.69 -> £3,395,303.83 (10.2%); £3,780,811.97 -> £3,395,303.86 (10.2%); £3,780,812.21 -> £3,395,303.88 (10.2%); £3,780,812.43 -> £3,395,303.91 (10.2%); £3,780,812.64 -> £3,395,303.93 (10.2%); £3,780,812.81 -> £3,395,303.94 (10.2%); £3,780,812.97 -> £3,395,303.96 (10.2%); £3,780,813.14 -> £3,395,303.98 (10.2%); £3,780,813.30 -> £3,395,304.00 (10.2%); £3,780,813.46 -> £3,395,304.01 (10.2%); £3,780,813.62 -> £3,395,304.03 (10.2%); £3,780,813.79 -> £3,395,304.05 (10.2%); £3,780,813.95 -> £3,395,304.06 (10.2%); £3,780,814.11 -> £3,395,304.08 (10.2%); £3,780,814.27 -> £3,395,304.09 (10.2%); £3,780,814.43 -> £3,395,304.11 (10.2%); £3,780,814.59 -> £3,395,304.22 (10.2%); £3,780,814.76 -> £3,395,304.34 (10.2%); £3,780,814.94 -> £3,395,304.46 (10.2%); £3,780,815.14 -> £3,395,304.59 (10.2%); £3,780,815.36 -> £3,395,304.71 (10.2%); £3,780,815.59 -> £3,395,304.84 (10.2%); £3,780,815.84 -> £3,395,304.96 (10.2%); £3,780,816.11 -> £3,395,305.08 (10.2%); £3,780,816.38 -> £3,395,305.11 (10.2%); £3,780,816.66 -> £3,395,305.13 (10.2%); £3,780,816.93 -> £3,395,305.16 (10.2%); £3,780,817.18 -> £3,395,305.18 (10.2%); £3,780,817.45 -> £3,395,305.20 (10.2%); £3,780,817.72 -> £3,395,305.23 (10.2%); £3,780,817.99 -> £3,395,305.25 (10.2%); £3,780,818.25 -> £3,395,305.27 (10.2%); £3,780,818.51 -> £3,395,305.30 (10.2%); £3,780,818.78 -> £3,395,305.32 (10.2%); £3,780,819.06 -> £3,395,305.34 (10.2%); £3,780,819.33 -> £3,395,305.37 (10.2%); £3,780,819.60 -> £3,395,305.40 (10.2%); £3,780,819.87 -> £3,395,305.52 (10.2%); £3,780,820.14 -> £3,395,305.66 (10.2%); £3,780,820.41 -> £3,395,305.79 (10.2%); £3,780,820.68 -> £3,395,305.92 (10.2%); £3,780,820.94 -> £3,395,306.05 (10.2%); £3,780,821.21 -> £3,395,306.18 (10.2%); £3,780,821.47 -> £3,395,306.31 (10.2%); £3,780,821.74 -> £3,395,306.44 (10.2%); £3,780,822.00 -> £3,395,306.57 (10.2%); £3,780,822.27 -> £3,395,306.70 (10.2%); £3,780,822.55 -> £3,395,306.82 (10.2%); £3,780,822.82 -> £3,395,306.85 (10.2%); £3,780,823.09 -> £3,395,306.88 (10.2%); £3,780,823.34 -> £3,395,306.91 (10.2%); £3,780,823.57 -> £3,395,306.93 (10.2%); £3,780,823.78 -> £3,395,306.95 (10.2%); £3,780,823.94 -> £3,395,306.97 (10.2%); £3,780,824.10 -> £3,395,306.98 (10.2%); £3,780,824.26 -> £3,395,307.00 (10.2%); £3,780,824.42 -> £3,395,307.02 (10.2%); £3,780,824.58 -> £3,395,307.03 (10.2%); £3,780,824.74 -> £3,395,307.05 (10.2%); £3,780,824.90 -> £3,395,307.07 (10.2%); £3,780,825.06 -> £3,395,307.08 (10.2%); £3,780,825.21 -> £3,395,307.10 (10.2%); £3,780,825.37 -> £3,395,307.12 (10.2%); £3,780,825.53 -> £3,395,307.14 (10.2%); £3,780,825.69 -> £3,395,307.27 (10.2%); £3,780,825.85 -> £3,395,307.41 (10.2%); £3,780,826.02 -> £3,395,307.56 (10.2%); £3,780,826.22 -> £3,395,307.71 (10.2%); £3,780,826.44 -> £3,395,307.86 (10.2%); £3,780,826.68 -> £3,395,308.01 (10.2%); £3,780,826.93 -> £3,395,308.15 (10.2%); £3,780,827.20 -> £3,395,308.30 (10.2%); £3,780,827.47 -> £3,395,308.32 (10.2%); £3,780,827.73 -> £3,395,308.34 (10.2%); £3,780,828.01 -> £3,395,308.37 (10.2%); £3,780,828.27 -> £3,395,308.39 (10.2%); £3,780,828.53 -> £3,395,308.42 (10.2%); £3,780,828.81 -> £3,395,308.44 (10.2%); £3,780,829.08 -> £3,395,308.46 (10.2%); £3,780,829.35 -> £3,395,308.49 (10.2%); £3,780,829.64 -> £3,395,308.51 (10.2%); £3,780,829.90 -> £3,395,308.53 (10.2%); £3,780,830.16 -> £3,395,308.56 (10.2%); £3,780,830.44 -> £3,395,308.58 (10.2%); £3,780,830.71 -> £3,395,308.61 (10.2%); £3,780,830.97 -> £3,395,308.77 (10.2%); £3,780,831.25 -> £3,395,308.93 (10.2%); £3,780,831.52 -> £3,395,309.09 (10.2%); £3,780,831.78 -> £3,395,309.25 (10.2%); £3,780,832.06 -> £3,395,309.41 (10.2%); £3,780,832.32 -> £3,395,309.56 (10.2%); £3,780,832.59 -> £3,395,309.72 (10.2%); £3,780,832.86 -> £3,395,309.87 (10.2%); £3,780,833.13 -> £3,395,310.02 (10.2%); £3,780,833.40 -> £3,395,310.17 (10.2%); £3,780,833.67 -> £3,395,310.31 (10.2%); £3,780,833.94 -> £3,395,310.34 (10.2%); £3,780,834.22 -> £3,395,310.37 (10.2%); £3,780,834.46 -> £3,395,310.39 (10.2%); £3,780,834.69 -> £3,395,310.42 (10.2%); £3,780,834.90 -> £3,395,310.44 (10.2%); £3,780,835.06 -> £3,395,310.45 (10.2%); £3,780,835.22 -> £3,395,310.47 (10.2%); £3,780,835.38 -> £3,395,310.49 (10.2%); £3,780,835.54 -> £3,395,310.51 (10.2%); £3,780,835.70 -> £3,395,310.52 (10.2%); £3,780,835.86 -> £3,395,310.54 (10.2%); £3,780,836.02 -> £3,395,310.56 (10.2%); £3,780,836.18 -> £3,395,310.57 (10.2%); £3,780,836.34 -> £3,395,310.59 (10.2%); £3,780,836.50 -> £3,395,310.61 (10.2%); £3,780,836.66 -> £3,395,310.62 (10.2%); £3,780,836.82 -> £3,395,310.77 (10.2%); £3,780,836.99 -> £3,395,310.91 (10.2%); £3,780,837.17 -> £3,395,311.06 (10.2%); £3,780,837.38 -> £3,395,311.20 (10.2%); £3,780,837.59 -> £3,395,311.35 (10.2%); £3,780,837.83 -> £3,395,311.50 (10.2%); £3,780,838.08 -> £3,395,311.64 (10.2%); £3,780,838.35 -> £3,395,311.78 (10.2%); £3,780,838.62 -> £3,395,311.80 (10.2%); £3,780,838.89 -> £3,395,311.83 (10.2%); £3,780,839.15 -> £3,395,311.85 (10.2%); £3,780,839.43 -> £3,395,311.87 (10.2%); £3,780,839.71 -> £3,395,311.90 (10.2%); £3,780,839.97 -> £3,395,311.92 (10.2%); £3,780,840.24 -> £3,395,311.94 (10.2%); £3,780,840.52 -> £3,395,311.97 (10.2%); £3,780,840.80 -> £3,395,311.99 (10.2%); £3,780,841.07 -> £3,395,312.01 (10.2%); £3,780,841.34 -> £3,395,312.04 (10.2%); £3,780,841.61 -> £3,395,312.06 (10.2%); £3,780,841.88 -> £3,395,312.09 (10.2%); £3,780,842.17 -> £3,395,312.24 (10.2%); £3,780,842.44 -> £3,395,312.39 (10.2%); £3,780,842.71 -> £3,395,312.54 (10.2%); £3,780,842.97 -> £3,395,312.69 (10.2%); £3,780,843.24 -> £3,395,312.84 (10.2%); £3,780,843.51 -> £3,395,312.99 (10.2%); £3,780,843.79 -> £3,395,313.14 (10.2%); £3,780,844.07 -> £3,395,313.29 (10.2%); £3,780,844.34 -> £3,395,313.43 (10.2%); £3,780,844.62 -> £3,395,313.58 (10.2%); £3,780,844.88 -> £3,395,313.72 (10.2%); £3,780,845.16 -> £3,395,313.75 (10.2%); £3,780,845.44 -> £3,395,313.77 (10.2%); £3,780,845.69 -> £3,395,313.80 (10.2%); £3,780,845.93 -> £3,395,313.82 (10.2%); £3,780,846.14 -> £3,395,313.84 (10.2%); £3,780,846.30 -> £3,395,313.86 (10.2%); £3,780,846.47 -> £3,395,313.88 (10.2%); £3,780,846.63 -> £3,395,313.89 (10.2%); £3,780,846.79 -> £3,395,313.91 (10.2%); £3,780,846.95 -> £3,395,313.93 (10.2%); £3,780,847.11 -> £3,395,313.94 (10.2%); £3,780,847.28 -> £3,395,313.96 (10.2%); £3,780,847.44 -> £3,395,313.98 (10.2%); £3,780,847.60 -> £3,395,313.99 (10.2%); £3,780,847.76 -> £3,395,314.01 (10.2%); £3,780,847.93 -> £3,395,314.03 (10.2%); £3,780,848.09 -> £3,395,314.15 (10.2%); £3,780,848.25 -> £3,395,314.27 (10.2%); £3,780,848.43 -> £3,395,314.40 (10.2%); £3,780,848.63 -> £3,395,314.53 (10.2%); £3,780,848.84 -> £3,395,314.67 (10.2%); £3,780,849.08 -> £3,395,314.80 (10.2%); £3,780,849.33 -> £3,395,314.92 (10.2%); £3,780,849.59 -> £3,395,315.05 (10.2%); £3,780,849.87 -> £3,395,315.08 (10.2%); £3,780,850.13 -> £3,395,315.10 (10.2%); £3,780,850.39 -> £3,395,315.12 (10.2%); £3,780,850.67 -> £3,395,315.15 (10.2%); £3,780,850.94 -> £3,395,315.17 (10.2%); £3,780,851.21 -> £3,395,315.20 (10.2%); £3,780,851.49 -> £3,395,315.22 (10.2%); £3,780,851.76 -> £3,395,315.24 (10.2%); £3,780,852.03 -> £3,395,315.27 (10.2%); £3,780,852.30 -> £3,395,315.29 (10.2%); £3,780,852.57 -> £3,395,315.31 (10.2%); £3,780,852.84 -> £3,395,315.34 (10.2%); £3,780,853.11 -> £3,395,315.37 (10.2%); £3,780,853.37 -> £3,395,315.50 (10.2%); £3,780,853.64 -> £3,395,315.64 (10.2%); £3,780,853.91 -> £3,395,315.78 (10.2%); £3,780,854.19 -> £3,395,315.92 (10.2%); £3,780,854.46 -> £3,395,316.06 (10.2%); £3,780,854.73 -> £3,395,316.20 (10.2%); £3,780,855.00 -> £3,395,316.34 (10.2%); £3,780,855.26 -> £3,395,316.48 (10.2%); £3,780,855.54 -> £3,395,316.63 (10.2%); £3,780,855.82 -> £3,395,316.77 (10.2%); £3,780,856.09 -> £3,395,316.90 (10.2%); £3,780,856.36 -> £3,395,316.93 (10.2%); £3,780,856.63 -> £3,395,316.96 (10.2%); £3,780,856.88 -> £3,395,316.98 (10.2%); £3,780,857.12 -> £3,395,317.00 (10.2%)
- Bills issued: 153, average clarity 0.806, average bill shock 17.0%, bad debt provision £0.00, avg complaint probability 4.8%
- Solvency signal: £315,318/customer (12 customers) — OK (Ofgem floor £130/customer)

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
- Treasury at year end: £3,835,512.32
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
- Average CLV (Point-in-Time, year-end 2025): £362,080.49
  - By billing account: C1 £4,338.09, C1_2 £3,856.07, C2 £5,911.85, C2_2 £3,493.53, C3 £5,747.90, C4 £2,772.74, C5 £9,675.09, C5_2 £4,275.95, C6 £15,200.05, C7 £7,594.48, C8 £7,947.09, C9 £8,801.76, C_IC1 £1,355,811.81, C_IC2 £849,459.41, C_IC3 £2,158,651.79, C_IC4 £1,349,750.16
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
- Solvency signal: £383,551/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £66.19 vs. naked (unhedged) net margin: £349.73
- hedging cost £283.54 vs. a fully unhedged book (commodity-only: actual net £66.19 vs. naked net £349.73)
  - C2_2: actual £96.28 vs. naked £230.84 -- hedging cost £134.56
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £123,091.80 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 25 customer(s) experienced a bill shock of >=20%.
