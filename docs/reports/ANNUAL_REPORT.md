# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,902,095.14
  (£1,435,458.92 net change)
- Solvency signal (final year): £425,201/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £22,565,291.81
  VAT remitted to HMRC: (£3,739,867.99) | Revenue (ex-VAT): £18,825,423.81
  Non-commodity pass-through: (£4,782,360.86)
- Gross margin: £6,445,318.38
- Capital costs: £51,377.37
- Net margin: £6,393,941.01
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1588, average clarity 0.814,
  service quality score 0.904
- Enterprise value (CLV sum across 14 billing accounts): £7,735,815.99
- Cost to serve (whole portfolio): £18,730.56, net margin after cost to serve: £6,375,210.45
- Hedge effectiveness (whole window): hedging cost £4,222,848.02 vs. a fully unhedged book (commodity-only: actual net £1,435,458.92 vs. naked net £5,658,306.93)

- **2021** (crisis year): net margin £75,231.55, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £338,347.87, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2249, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 243.0x (net £65,099.25 on £267.86 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 3/5 departures (60%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 4.7%, max 16.5% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +34.0% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 34.0% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,445,318.38, capital £51,377.37, net £6,393,941.01. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £75,231.55 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,393,941.01
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,658,306.93
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,222,848.02 vs. a fully unhedged book (commodity-only: actual net £1,435,458.92 vs. naked net £5,658,306.93)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,382.63 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £612,905.20 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £296.42 | £657.33 | £324.29 | £1,278.04 |
| 2017 | £30,139.92 | £0.00 | £45.06 | £929.53 | £516.54 | £31,631.05 |
| 2018 | £101,124.28 | £0.00 | £-655.88 | £625.30 | £436.94 | £101,530.64 |
| 2019 | £222,457.58 | £9,999.92 | £363.18 | £797.62 | £489.73 | £234,108.02 |
| 2020 | £116,572.09 | £10,030.76 | £398.12 | £1,053.89 | £457.36 | £128,512.22 |
| 2021 | £64,952.49 | £9,999.92 | £-17.67 | £466.40 | £-169.59 | £75,231.55 |
| 2022 | £330,000.66 | £9,999.92 | £1,141.20 | £-1,534.82 | £-1,259.09 | £338,347.87 |
| 2023 | £135,957.41 | £9,999.92 | £-652.18 | £48.08 | £-976.37 | £144,376.85 |
| 2024 | £333,515.99 | £10,030.76 | £817.61 | £2,772.90 | £678.12 | £347,815.39 |
| 2025 | £115,818.30 | £4,449.79 | £0.00 | £634.54 | £90.34 | £120,992.97 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **53** renewals.  Lost (churned): **5** accounts.

Accounts lost before end of window: C1, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9462 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.0500 | 0.3500 | 0.9223 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9462 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.1100 | 0.5500 | 0.9113 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.1100 | 0.3500 | 0.8718 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.1400 | 0.5500 | 0.8871 | 0.8255 |
| C_IC1 | 2018-01-31 | renewed | 0.0500 | 0.5500 | 0.9753 | 0.3902 |
| C1 | 2018-12-31 | renewed | 0.1100 | 0.5500 | 0.9113 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.1100 | 0.3500 | 0.9051 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.2000 | 0.5500 | 0.8387 | 0.6312 |
| C_IC2 | 2019-01-31 | renewed | 0.0500 | 0.5500 | 0.9715 | 0.3710 |
| C1 | 2019-12-31 | renewed | 0.2900 | 0.5500 | 0.7873 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3500 | 0.3500 | 0.8370 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.2900 | 0.5500 | 0.8370 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.0800 | 0.5500 | 0.9648 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.1100 | 0.3500 | 0.9254 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.2300 | 0.5500 | 0.8921 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9355 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.2300 | 0.5500 | 0.8651 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.4100 | 0.5500 | 0.8696 | 0.2845 |
| C1 | 2020-12-30 | churned **CHURNED** | 0.3500 | 0.5500 | 0.7947 | 0.8047 |
| C5 | 2020-12-30 | churned **CHURNED** | 0.3200 | 0.3500 | 0.7288 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.2000 | 0.5500 | 0.8827 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.2000 | 0.5500 | 0.8827 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.0800 | 0.5500 | 0.9780 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.0800 | 0.3500 | 0.9661 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9413 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.1100 | 0.5500 | 0.9597 | 0.4564 |
| C1_2 | 2021-12-30 | renewed | 0.0500 | 0.5500 | 0.9833 | 0.2977 |
| C7 | 2021-12-30 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.3200 | 0.5500 | 0.9402 | 0.5838 |
| C2 | 2022-03-31 | renewed | 0.3800 | 0.5500 | 0.9633 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3500 | 0.3500 | 0.9609 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.2600 | 0.5500 | 0.9609 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3500 | 0.5500 | 0.9364 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.3800 | 0.5500 | 0.9364 | 0.8552 |
| C1_2 | 2022-12-30 | renewed | 0.4100 | 0.5500 | 0.9556 | 0.9433 |
| C7 | 2022-12-30 | renewed | 0.2900 | 0.5500 | 0.9364 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.4100 | 0.5500 | 0.9511 | 0.8723 |
| C2 | 2023-03-31 | renewed | 0.4100 | 0.5500 | 0.9273 | 0.6357 |
| C6 | 2023-03-31 | renewed | 0.4100 | 0.3500 | 0.8467 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.9221 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.7674 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.4100 | 0.5500 | 0.8739 | 0.6095 |
| C1_2 | 2023-12-30 | renewed | 0.1700 | 0.5500 | 0.9326 | 0.5453 |
| C7 | 2023-12-30 | renewed | 0.4100 | 0.5500 | 0.9026 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.4100 | 0.5500 | 0.9030 | 0.7019 |
| C2 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.9175 | 0.8119 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.2600 | 0.3500 | 0.8513 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.1700 | 0.5500 | 0.9324 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.1700 | 0.5500 | 0.8906 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.3800 | 0.5500 | 0.8570 | 0.9018 |
| C1_2 | 2024-12-29 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.1722 |
| C7 | 2024-12-29 | renewed | 0.2900 | 0.5500 | 0.8895 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.4100 | 0.5500 | 0.7971 | 0.3751 |
| C2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.9083 | 0.1514 |
| C8 | 2025-03-30 | renewed | 0.3200 | 0.5500 | 0.9018 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 154.0%
- **Average signed error:** +130.7% (over-estimates vs SIM)
- **Renewal events with estimates:** 58

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +114.2% | 114.2% |
| 2017 | 3 | -12.5% | 16.5% |
| 2018 | 4 | +793.2% | 793.2% |
| 2019 | 4 | +602.3% | 642.0% |
| 2020 | 10 | -3.0% | 59.5% |
| 2021 | 8 | +137.2% | 151.2% |
| 2022 | 8 | +13.5% | 22.0% |
| 2023 | 8 | +15.4% | 40.3% |
| 2024 | 8 | +39.9% | 52.4% |
| 2025 | 2 | +37.3% | 37.3% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 58
- **Active renewers:** 18 (31%) — mean company estimate 25.8%, abs error 361.2%
- **Passive SVT-rollers:** 40 (69%) — mean company estimate 10.2%, abs error 60.7%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 13.3% | 0.0% | 114.2% |
| 2017 | 0 | 3 | 0.0% | 9.4% | 0.0% | 16.5% |
| 2018 | 3 | 1 | 54.1% | 13.8% | 1039.3% | 55.1% |
| 2019 | 2 | 2 | 53.2% | 13.6% | 1267.4% | 16.7% |
| 2020 | 6 | 4 | 11.5% | 6.9% | 63.8% | 52.9% |
| 2021 | 1 | 7 | 12.7% | 12.4% | 72.6% | 162.4% |
| 2022 | 0 | 8 | 0.0% | 5.5% | 0.0% | 22.0% |
| 2023 | 2 | 6 | 25.4% | 9.9% | 72.3% | 29.6% |
| 2024 | 4 | 4 | 15.8% | 14.0% | 62.4% | 42.4% |
| 2025 | 0 | 2 | 0.0% | 13.0% | 0.0% | 37.3% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 40
- **Above SVT (at-risk):** 10 (25%)
- **Below/at SVT (protected):** 30 (75%)
- **Mean rate vs SVT premium:** -9.8%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.2 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 120.0 | 140.0 |
| 2018 | 1 | 0 (0%) | -1.7% | 149.9 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 4 | 0 (0%) | -27.2% | 129.7 | 178.1 |
| 2021 | 7 | 5 (71%) | +14.7% | 216.6 | 187.2 |
| 2022 | 8 | 4 (50%) | +4.6% | 293.1 | 343.4 |
| 2023 | 6 | 0 (0%) | -34.3% | 236.1 | 410.5 |
| 2024 | 4 | 1 (25%) | -11.7% | 216.8 | 246.9 |
| 2025 | 2 | 0 (0%) | -23.6% | 190.0 | 248.6 |

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
| 2022 | 16 | 11.4% | 23.2% |
| 2023 | 16 | 23.4% | 55.4% |
| 2024 | 15 | 10.9% | 22.6% |
| 2025 | 3 | 34.0% | 35.7% |

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
| 2018 | 4 | 7.93× ⚠ | 28.41× |
| 2019 | 4 | 6.42× ⚠ | 24.89× |
| 2020 | 10 | 0.59× | 1.48× |
| 2021 | 8 | 1.51× | 5.64× |
| 2022 | 8 | 0.22× | 0.68× |
| 2023 | 8 | 0.40× | 0.92× |
| 2024 | 8 | 0.52× | 1.07× |
| 2025 | 2 | 0.37× | 0.42× |

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
| 2023 | 10 | 2.59% | 8.48% | HIGH drift — EV/asset cohort growing |
| 2024 | 10 | 4.66% | 15.56% | HIGH drift — EV/asset cohort growing |
| 2025 | 2 | 8.62% | 16.47% | HIGH drift — EV/asset cohort growing |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **4.66%** mean / **15.56%** max in 2024. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
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
| 2024 | 10 | 4.7% | 15.6% |
| 2025 | 2 | 8.6% | 16.5% |

**88** of **88** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## EAC Drift Snapshot (Phase AI)

Per-customer consumption drift from company billing history (first renewal → latest renewal).
Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.

**2 significant** (≥15%) | **2 moderate** (5–15%) | **9 stable** (<5%)

| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |
|----------|-------------|-------------|-------|--------------|
| C2 | 5,265 | 4,236 | -20% | likely solar installation or significant efficiency upgrade |
| C4 | 4,131 | 3,365 | -19% | likely solar installation or significant efficiency upgrade |
| C1_2 | 10,401 | 9,227 | -11% | efficiency improvement or reduced occupancy |
| C7 | 13,179 | 12,155 | -8% | efficiency improvement or reduced occupancy |

**Portfolio demand trend:** 2 customers increasing / 11 decreasing (mean drift: -5.2%)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **6** (5 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.06, company est=0.08 |
| 2020-12-30 | CHURN | C1 | SIM p=0.21, company est=0.07 |
| 2020-12-30 | CHURN | C5 | SIM p=0.27, company est=0.09 |
| 2020-12-30 | ACQUISITION | C1_2 | home-move-win (predecessor: C1) |
| 2024-03-30 | CHURN | C6 | SIM p=0.15, company est=0.25 |
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
| 2022-12-31 | 3 accounts | 1 active | yes |
| 2023-12-31 | 3 accounts | 1 active | yes |
| 2024-12-31 | 5 accounts | 1 active | yes |
| 2025-12-31 | 5 accounts | 1 active | yes |

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
| 2022 | 256,149 | -49,726 | 70,920 | 36,672 | 69,092 | 99,453 | 482,561 | ⬇ CfD REBATE |
| 2023 | 271,739 | 64,738 | 71,702 | 50,941 | 75,066 | 13,744 | 547,930 |  |
| 2024 | 307,451 | 109,869 | 72,815 | 68,669 | 82,515 | 1,998 | 643,317 |  |
| 2025 | 135,614 | 46,911 | 31,156 | 31,004 | 36,121 | 853 | 281,658 |  |
| **Total** | **1,724,288** | **263,106** | **458,497** | **336,748** | **467,366** | **157,398** | **3,407,404** | |

Total policy cost: £3,407,404 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2022 | 133,368 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 139,152 | RIIO-ED2 from Apr 2023 |
| 2024 | 143,068 |  |
| 2025 | 61,118 |  |
| **Total** | **880,467** | |

Total network cost: £880,467 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

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
| 2022 | 27,046 | 54,554 | 81,600 |
| 2023 | 32,230 | 79,964 | 112,194 |
| 2024 | 37,495 | 76,702 | 114,196 |
| 2025 | 17,243 | 31,952 | 49,195 |
| **Total** | **171,109** | **393,356** | **564,464** |

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
| 2021 | 297,399 | 214,784 | 82,615 | 22,472 | 50,301 | 12 | 9,830 | +3.3% |
| 2022 | 589,447 | 499,059 | 90,388 | 27,046 | 54,554 | 47 | 8,741 | +1.5% |
| 2023 | 298,692 | 177,398 | 121,293 | 32,230 | 79,964 | 75 | 9,024 | +3.0% |
| 2024 | 271,570 | 146,620 | 124,950 | 37,495 | 76,702 | 45 | 10,709 | +3.9% |
| 2025 | 132,970 | 79,222 | 53,748 | 17,243 | 31,952 | 13 | 4,540 | +3.4% |
| **Total** | **1,856,126** | **1,226,295** | **629,831** | **171,109** | **393,356** | **268** | **65,099** | **+3.5%** |

Gas book net margin positive over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,441 | 9 | 274,160 | 2108.92× | OK |
| 2017 | 2,498,914 | 10 | 249,891 | 1922.24× | OK |
| 2018 | 2,487,878 | 11 | 226,171 | 1739.78× | OK |
| 2019 | 2,611,839 | 12 | 217,653 | 1674.26× | OK |
| 2020 | 2,924,252 | 14 | 208,875 | 1606.73× | OK |
| 2021 | 2,957,719 | 11 | 268,884 | 2068.34× | OK |
| 2022 | 3,161,656 | 11 | 287,423 | 2210.95× | OK |
| 2023 | 3,382,229 | 11 | 307,475 | 2365.20× | OK |
| 2024 | 3,774,871 | 11 | 343,170 | 2639.77× | OK |
| 2025 | 3,826,810 | 9 | 425,201 | 3270.78× | OK |

End-state (2025): **£425,201/account** across 9 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,441 | 81974.8× | OK |
| 2017 | 466 | 559 | 2,498,914 | 4470.2× | OK |
| 2018 | 868 | 1,041 | 2,487,878 | 2389.1× | OK |
| 2019 | 1,543 | 1,851 | 2,611,839 | 1410.9× | OK |
| 2020 | 1,979 | 2,374 | 2,924,252 | 1231.6× | OK |
| 2021 | 4,332 | 5,198 | 2,957,719 | 569.0× | OK |
| 2022 | 8,503 | 10,204 | 3,161,656 | 309.9× | OK |
| 2023 | 5,604 | 6,725 | 3,382,229 | 502.9× | OK |
| 2024 | 2,651 | 3,182 | 3,774,871 | 1186.5× | OK |
| 2025 | 3,872 | 4,647 | 3,826,810 | 823.5× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,495.87 | £12,233.14 | £261.96/MWh | £144.62/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,963.41 | £9,685.86 | £272.22/MWh | £154.30/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,933.34 | £9,310.71 | £250.25/MWh | £141.72/MWh | +10.9% |

Total HH revenue: £63,622.33 vs flat equivalent £58,720.58 (+8.3% ToU premium)

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
| 2022 | 71 | 141% | C1_2 (2022-01-31) |
| 2023 | 49 | 100% | C_IC2 (2023-06-30) |
| 2024 | 41 | 107% | C_IC2 (2024-07-31) |
| 2025 | 26 | 80% | C1_2 (2025-06-07) |

Total: **494** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2021-01-31 | C1_2 | +1207% | no |
| 2022-01-31 | C1_2 | +141% | no |
| 2022-10-31 | C4g | +134% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2020-03-31 | C_IC2 | +118% | no |
| 2021-10-31 | C4g | +113% | no |
| 2022-01-31 | C_IC3 | +109% | no |
| 2024-07-31 | C_IC2 | +107% | no |
| 2023-06-30 | C_IC2 | +100% | no |
| 2016-10-31 | C8 | +100% | no |

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
| 2022 | 3 | 61% | 92% | 2 ⚠ |
| 2023 | 3 | 0% | 0% | 0 |
| 2024 | 2 | 0% | 0% | 0 |
| 2025 | 1 | 8% | 8% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £19.4 | £125.6 (+548%) | 95% |
| 2022-03-31 | C2g | £35.0 | £95.0 (+171%) | 92% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 92% |
| 2021-09-30 | C4g | £16.1 | £35.0 (+118%) | 74% |
| 2021-03-31 | C2g | £21.7 | £35.0 (+62%) | 40% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 12 |
| Retained | 12 (100%) |
| Churned despite offer | 0 |
| Total offer cost (foregone margin) | £150,037.26 |
| Margin saved (retained customers' terms) | £1,208,823.06 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£1,058,785.81** |
| Acquisition cost avoided (retained customers) | £2,300.00 |
| **Full economic ROI (margin + acq savings)** | **£1,061,085.81** |

Missed opportunities (churns with no offer): **5** (£5,906.90 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 5 (£5,906.90 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 2 | 2 | £71.21 | £1362.79 | £1291.58 | £0.00 |
| 2018 | 2 | 2 | £24324.09 | £165398.74 | £141074.66 | £0.00 |
| 2019 | 2 | 2 | £32311.18 | £296612.44 | £264301.26 | £0.00 |
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £2646.25 |
| 2021 | 3 | 3 | £65546.54 | £414546.89 | £349000.35 | £0.00 |
| 2022 | 2 | 2 | £27550.29 | £327530.64 | £299980.36 | £0.00 |
| 2023 | 1 | 1 | £233.96 | £3371.56 | £3137.60 | £0.00 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £3260.66 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2017-04-01 | C8 | 0.35 | 3% | £46.02 | £868.15 | £150 | £822.12 | retained |
| 2017-07-01 | C3 | 0.39 | 3% | £25.18 | £494.64 | £150 | £469.46 | retained |
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24240.02 | £163856.32 | £150 | £139616.30 | retained |
| 2018-12-31 | C5 | 0.37 | 3% | £84.07 | £1542.42 | £400 | £1458.35 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.66 | 5% | £17469.37 | £194971.28 | £150 | £177501.91 | retained |
| 2021-03-31 | C_IC2 | 0.39 | 3% | £5309.59 | £91281.89 | £150 | £85972.31 | retained |
| 2021-04-30 | C_IC1 | 0.38 | 3% | £8446.46 | £158248.78 | £150 | £149802.32 | retained |
| 2021-12-31 | C_IC3 | 0.54 | 5% | £51790.49 | £165016.21 | £150 | £113225.72 | retained |
| 2022-04-30 | C_IC2 | 0.40 | 3% | £9406.51 | £95870.93 | £150 | £86464.43 | retained |
| 2022-05-30 | C_IC1 | 0.41 | 3% | £18143.78 | £231659.71 | £150 | £213515.93 | retained |
| 2023-03-31 | C6 | 0.40 | 3% | £233.96 | £3371.56 | £400 | £3137.60 | retained |

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

Serial savers (2): C_IC1 (4 offers, £68,300), C_IC2 (3 offers, £29,558).

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £7,735,815.99 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £677,911.60 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,278.04 |
| 2017 | £31,631.05 |
| 2018 | £101,530.64 |
| 2019 | £234,108.02 |
| 2020 | £128,512.22 |
| 2021 | £75,231.55 |
| 2022 | £338,347.87 |
| 2023 | £144,376.85 | ← trailing
| 2024 | £347,815.39 | ← trailing
| 2025 | £120,992.97 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £5,452.61 | — |
| C1_2 | — | £612.56 |
| C2 | £6,620.17 | £933.32 |
| C3 | £6,491.05 | — |
| C4 | £3,807.08 | £-1,005.44 |
| C5 | £10,919.84 | — |
| C6 | £19,260.39 | £274.43 |
| C7 | £8,738.68 | £565.03 |
| C8 | £9,622.89 | £737.43 |
| C9 | £9,949.67 | £1,413.67 |
| C_IC1 | £1,762,208.13 | £389,093.54 |
| C_IC2 | £957,420.63 | £205,248.66 |
| C_IC3 | £3,218,402.68 | £64,153.93 |
| C_IC4 | £1,712,238.71 | £15,884.48 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C1_2 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £6,522.54 | — | — | — | — | £14,339.54 | — | £10,526.48 | — | — | — | — | — | — |
| 2017 | £5,740.27 | — | £11,364.56 | £9,644.02 | £8,744.86 | £12,167.53 | £24,200.80 | £8,895.16 | £13,842.89 | £11,262.19 | — | — | — | — |
| 2018 | £5,706.06 | — | £8,726.77 | £9,643.83 | £7,300.25 | £12,344.35 | £20,424.84 | £8,038.55 | £10,898.61 | £10,640.88 | £2,792,331.69 | — | — | — |
| 2019 | £5,661.65 | — | £8,873.94 | £8,256.51 | £6,507.79 | £11,192.06 | £19,074.59 | £8,373.08 | £9,472.90 | £9,974.34 | £2,348,957.18 | £1,778,067.01 | — | — |
| 2020 | £4,622.02 | £16.03 | £6,623.51 | £5,895.98 | £7,053.95 | £12,943.29 | £19,510.54 | £7,742.53 | £9,552.17 | £9,057.96 | £1,391,889.73 | £887,578.71 | £2,197,517.58 | £1,462,114.75 |
| 2021 | £4,744.82 | £986.91 | £6,791.99 | £5,831.99 | £5,409.21 | £12,050.99 | £17,951.57 | £6,973.39 | £9,219.23 | £8,492.59 | £1,502,450.85 | £765,170.10 | £2,019,710.36 | £1,364,017.02 |
| 2022 | £4,582.39 | £2,003.94 | £5,036.95 | £5,087.16 | £3,176.70 | £9,425.03 | £15,793.20 | £5,021.24 | £7,914.07 | £7,134.34 | £1,299,467.84 | £764,895.23 | £2,828,439.92 | £1,074,640.43 |
| 2023 | £3,680.74 | £1,944.13 | £4,982.25 | £4,440.04 | £2,107.60 | £7,623.31 | £17,306.38 | £5,356.78 | £7,277.99 | £6,952.69 | £1,320,738.65 | £640,507.44 | £1,892,395.24 | £1,169,282.75 |
| 2024 | £3,291.89 | £2,675.04 | £4,369.83 | £4,033.43 | £2,598.16 | £7,834.04 | £15,341.31 | £4,975.97 | £7,062.48 | £7,097.09 | £1,156,263.05 | £680,833.29 | £2,019,730.99 | £963,733.92 |
| 2025 | £3,675.53 | £3,572.27 | £4,381.71 | £4,035.20 | £2,503.98 | £6,507.60 | £13,097.23 | £5,846.15 | £6,249.07 | £6,617.37 | £1,073,429.56 | £766,140.36 | £2,041,976.89 | £1,121,677.29 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £985.82, range £4.58–£4,218.12.

- C1: cost to serve £274.94, net margin after CTS £2,068.10
- C1_2: cost to serve £244.19, net margin after CTS £5,418.65
- C1g: cost to serve £5.73, net margin after CTS £1,349.51
- C2: cost to serve £505.43, net margin after CTS £5,017.38
- C2g: cost to serve £10.53, net margin after CTS £3,276.95
- C3: cost to serve £219.95, net margin after CTS £2,168.93
- C3g: cost to serve £4.58, net margin after CTS £1,293.95
- C4: cost to serve £439.89, net margin after CTS £2,803.41
- C4g: cost to serve £9.17, net margin after CTS £1,233.88
- C5: cost to serve £599.87, net margin after CTS £7,230.71
- C6: cost to serve £959.77, net margin after CTS £21,746.58
- C7: cost to serve £519.13, net margin after CTS £10,234.75
- C8: cost to serve £505.43, net margin after CTS £11,924.39
- C9: cost to serve £491.72, net margin after CTS £12,216.81
- C_IC1: cost to serve £4,218.12, net margin after CTS £1,870,784.18
- C_IC2: cost to serve £3,718.18, net margin after CTS £905,291.97
- C_IC3: cost to serve £3,218.32, net margin after CTS £1,821,875.22
- C_IC3g: cost to serve £67.07, net margin after CTS £622,579.96
- C_IC4: cost to serve £2,718.52, net margin after CTS £1,103,966.75


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 29 recovery surcharge(s) at renewal based on prior-term losses (4 gas). Avg surcharge: 14.4%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.39/MWh |
| C5 | electricity | 2018-12-31 | £-208.04 | £2,323.11 | +4.0% | £148.68/MWh | £153.61/MWh |
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
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £317.57/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.69/MWh |
| C4 | electricity | 2022-09-30 | £-231.16 | £893.04 | +20.0% | £404.86/MWh | £487.66/MWh |
| C4g | gas | 2022-09-30 | £-874.54 | £1,040.11 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £337.90/MWh |
| C2 | electricity | 2023-03-31 | £-191.17 | £1,780.28 | +5.7% | £319.17/MWh | £369.81/MWh |
| C2g | gas | 2023-03-31 | £-258.54 | £1,782.04 | +9.5% | £83.68/MWh | £105.06/MWh |
| C8 | electricity | 2023-03-31 | £-481.87 | £3,898.74 | +7.4% | £319.17/MWh | £350.13/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.36/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.47/MWh |
| C4 | electricity | 2023-09-30 | £-292.88 | £1,307.19 | +17.4% | £216.77/MWh | £252.47/MWh |
| C4g | gas | 2023-09-30 | £-2,028.81 | £2,732.11 | +20.0% | £47.83/MWh | £64.73/MWh |
| C1_2 | electricity | 2023-12-30 | £-584.36 | £2,733.08 | +16.4% | £242.22/MWh | £267.80/MWh |
| C7 | electricity | 2023-12-30 | £-445.92 | £3,990.91 | +6.2% | £242.22/MWh | £244.32/MWh |
| C_IC3 | electricity | 2023-12-31 | £-124,202.28 | £972,250.24 | +7.8% | £118.95/MWh | £121.79/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |


## Flexibility Revenue — DSR & Capacity Market (Phase AG/NX)

Two flexibility revenue streams: residential DSR (EV/ASHP/battery via FlexibilityRevenueBook) and I&C demand response (interruptible process load via ICFlexibilityRevenueBook).
- **Capacity Market (CM):** T-4 auction clearing prices (£6.44–£22.50/kW/yr by year, NESO); operational since 2014.
- **Demand Flexibility Service (DFS):** launched October 2022; £4.5/MWh × 20 events/yr.
- **I&C DSR aggregator fee:** 20% of gross CM/DFS revenue.

**Total 2016–2025:** £21,381.06  (Residential: £0.00 | I&C: £21,381.06)

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
- **Estimated margin protected:** £1,208,823.06
- **No-offer churns:** 5 total (0 blind miss / 0 deliberate pass)
- **Retention coverage rate:** 71% of at-risk renewals received an offer

### 2. Flexibility Revenue Intelligence

- No flexibility revenue data available.

### 3. Churn Pattern Analysis

- **Total lifetime churn events:** 5
- **Peak churn year:** 2020 (3 events)
- **Net book movement:** 1 acquisitions − 5 churns = -4
- **Portfolio trend:** shrinking

### 4. Board Recommendations

1. Portfolio operating within normal parameters. Monitor retention coverage and flexibility enrollment growth.

## CRM Intelligence: Risk Triage (Final Year)

Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.

| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |
|---------|-----|-----------|-----------|----------|-------------|-----------------|
| C5 | SME | MEDIUM | 27% | 9% | -20.2% [competitive] | £7,230.71 |
| C1 | resi | MEDIUM | 21% | 7% | -22.9% [competitive] | £2,068.10 |
| C_IC3 | I&C | MEDIUM | 20% | 11% | -54.0% [competitive] | £1,821,875.22 |
| C6 | SME | LOW | 15% | 25% | -25.9% [competitive] | £21,746.58 |
| C4 | resi | LOW | 14% | 14% | -9.0% | £2,803.41 |
| C7 | resi | LOW | 11% | 17% | -14.3% | £10,234.75 |
| C9 | resi | LOW | 11% | 14% | -14.3% | £12,216.81 |
| C8 | resi | LOW | 10% | 13% | -23.6% [competitive] | £11,924.39 |
| C2 | resi | LOW | 9% | 13% | -23.6% [competitive] | £5,017.38 |
| C1_2 | resi | LOW | 8% | 11% | +3.3% | £5,418.65 |
| C3 | resi | LOW | 6% | 8% | -39.0% [competitive] | £2,168.93 |
| C_IC2 | I&C | LOW | 4% | 95% | +12.4% [overpriced] | £905,291.97 |
| C_IC1 | I&C | LOW | 3% | 95% | -0.1% | £1,870,784.18 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 0 accounts
- MEDIUM (>=15%): 3 accounts
- LOW (<15%): 10 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £0.00

## Churn Root Cause Attribution

Per-churned-account analysis: pricing journey, rate-vs-SVT positioning, and company vs SIM churn estimate at the point of departure.

| Account | Seg | Churn Date | Tenure | Last Rate Shock | Rate vs SVT | Sim Risk | Co. Est. | Margin Lost |
|---------|-----|------------|--------|-----------------|-------------|----------|----------|-------------|
| C3 | resi | 2020-06-30 | 4.0yr | -4.3% | -39.0% | 6% | 8% | £2,168.93 |
| C1 | resi | 2020-12-30 | 5.0yr | -0.7% | -22.9% | 21% | 7% | £2,068.10 |
| C5 | SME | 2020-12-30 | 5.0yr | +2.8% | -20.2% | 27% | 9% | £7,230.71 |
| C6 | SME | 2024-03-30 | 8.0yr | -2.2% | -25.9% | 15% | 25% | £21,746.58 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 14% | 14% | £2,803.41 |

**Root Cause Summary:**
- Total churned accounts: 5
- Lifetime margin lost: £36,017.72
- Average tenure at departure: 6.0 years
- Company-warned churns (co. est. >=20%): 1 -- C6

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 5 accounts that churned without an offer? Calibrated from 12 actual offers (observed retention rate 100%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C3 | resi | 2020-06-30 | 8% | £585.26 | 5% | £29.26 | £556.00 | MISSED OPP. |
| C1 | resi | 2020-12-30 | 7% | £415.98 | 5% | £20.80 | £395.19 | MISSED OPP. |
| C5 | SME | 2020-12-30 | 9% | £1,645.00 | 8% | £131.60 | £1,513.40 | MISSED OPP. |
| C6 | SME | 2024-03-30 | 25% | £2,791.79 | 8% | £223.34 | £2,568.45 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 14% | £468.86 | 5% | £23.44 | £445.42 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 5
- Correct no-offer (net-neg ETM): 0
- Missed opportunities (positive ETM, below detection): 5
- Total term margin foregone: £5,906.90
- Total retention cost (counterfactual): £428.45
- Net counterfactual benefit: £5,478.46 (at 100% retention probability)
- Root cause: company churn detection below threshold for all missed cases -- churn model underestimated bill-shock risk

## Pricing Basis Risk Attribution

Forward curve accuracy at each contract term. tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd: positive = company over-estimated costs (higher than market); negative = company under-estimated (margin-at-risk).
Portfolio-wide mean error: +6.6%

| Year | Contracts | Mean Error | Max Abs | Over-priced | Under-priced | Assessment |
|------|-----------|------------|---------|-------------|--------------|------------|
| 2016 | 17 | +8.9% | 29.1% | 9 | 4 | moderate over |
| 2017 | 14 | +5.4% | 46.6% | 8 | 5 | moderate over |
| 2018 | 16 | -2.9% | 27.7% | 6 | 8 | on target |
| 2019 | 19 | +8.3% | 37.2% | 9 | 3 | moderate over |
| 2020 | 22 | -0.9% | 33.8% | 9 | 8 | on target |
| 2021 | 16 | +9.0% | 44.5% | 6 | 3 | moderate over |
| 2022 | 16 | -2.2% | 23.2% | 6 | 5 | on target |
| 2023 | 16 | +22.0% | 55.4% | 11 | 1 | HIGH OVER-PRICE |
| 2024 | 15 | +8.7% | 22.6% | 9 | 1 | moderate over |
| 2025 | 3 | +34.0% | 35.7% | 3 | 0 | HIGH OVER-PRICE |

**Basis Risk Summary:**
- Portfolio mean tariff error: +6.6%
- Worst over-pricing year: 2025 (+34.0%) -- company forward curve above settled market
- Post-crisis over-pricing years (2023, 2025): company locked in expensive crisis-era forwards after prices normalised -- mechanism that eroded real suppliers' margins 2022-24

## BSC Settlement Exposure

Elexon's Balancing and Settlement Code (BSC) requires suppliers to post credit cover to fund potential imbalance charges. Credit requirements track portfolio size and wholesale price levels. Peak daily settlement is the largest single-day settlement amount seen in that year.

| Year | BSC Credit Required | Peak Daily | % of Revenue |
|------|---------------------|------------|--------------|
| 2016 | £30 | £25 | 0.29% |
| 2017 | £559 | £466 | 0.24% |
| 2018 | £1,041 | £868 | 0.24% |
| 2019 | £1,851 | £1,543 | 0.15% |
| 2020 | £2,374 | £1,979 | 0.19% |
| 2021 | £5,198 | £4,332 | 0.30% |
| 2022 | £10,204 | £8,503 | 0.30% |
| 2023 | £6,725 | £5,604 | 0.26% |
| 2024 | £3,182 | £2,651 | 0.15% |
| 2025 | £4,647 | £3,872 | 0.48% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,204 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £525 | £98 | 12.3% |
| 2017 | 14 | £16,735 | £8,803 | £2,259 | 13.5% |
| 2018 | 15 | £29,032 | £17,507 | £6,769 | 23.3% |
| 2019 | 17 | £70,487 | £41,300 | £13,771 | 19.5% |
| 2020 | 19 | £64,385 | £41,672 | £6,764 | 10.5% |
| 2021 | 14 | £123,922 | £54,511 | £5,374 | 4.3% << |
| 2022 | 14 | £245,590 | £74,945 | £24,168 | 9.8% |
| 2023 | 14 | £185,335 | £68,277 | £10,313 | 5.6% |
| 2024 | 14 | £156,332 | £89,843 | £24,844 | 15.9% |
| 2025 | 11 | £88,243 | £47,146 | £10,999 | 12.5% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £24,844 net/customer
**Worst year per customer:** 2016 at £98 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £416 | — | £416 |
| C1_2 | £648 | — | £648 |
| C1g | — | £669 | £669 |
| C2 | £1,177 | — | £1,177 |
| C2g | — | £1,294 | £1,294 |
| C3 | £182 | — | £182 |
| C3g | — | £336 | £336 |
| C4 | £68 | — | £68 |
| C4g | — | £-1,711 | £-1,711 * |
| C5 | £-200 | — | £-200 * |
| C6 | £1,936 | — | £1,936 |
| C7 | £-572 | — | £-572 * |
| C8 | £2,292 | — | £2,292 |
| C9 | £2,240 | — | £2,240 |
| C_IC1 | £846,747 | — | £846,747 |
| C_IC2 | £434,894 | — | £434,894 |
| C_IC3 | £136,677 | — | £136,677 |
| C_IC3g | — | £64,511 | £64,511 |
| C_IC4 | £32,221 | — | £32,221 |
| **Total** | **£1,458,725** | **£65,099** | **£1,523,825** |

Loss-making accounts: C4g (£-1,711), C7 (£-572), C5 (£-200)
Gas loss-making: C4g (£-1,711)
Gas portfolio net: £65,099 (4.3% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,047 | £10,957 | £-8,909 |
| 2017 | £30,074 | £112,510 | £-82,435 |
| 2018 | £109,564 | £246,641 | £-137,077 |
| 2019 | £252,638 | £836,859 | £-584,221 |
| 2020 | £85,179 | £962,868 | £-877,689 |
| 2021 | £191,531 | £457,067 | £-265,535 |
| 2022 | £184,630 | £1,207,112 | £-1,022,482 |
| 2023 | £380,391 | £1,219,610 | £-839,219 |
| 2024 | £199,426 | £604,483 | £-405,057 |
| 2025 | £-21 | £200 | £-220 |
| **Total** | **£1,435,459** | **£5,658,307** | **£-4,222,848** |

Largest hedging cost: **2022** (£1,022,482 vs naked)
Smallest hedging cost: **2025** (£220 vs naked)
Conclusion: systematic forward hedging cost £4,222,848 over 10 years vs spot purchasing.

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
| 2022 | 0.791 R | 5.6% | 0.23% | 71 | 168 | RED ! |
| 2023 | 0.811 A | 4.9% | 0.17% | 49 | 168 | AMBER |
| 2024 | 0.816 A | 4.6% | 0.16% | 41 | 153 | AMBER |
| 2025 | 0.776 R | 6.0% | 0.25% | 26 | 66 | RED ! |

Worst clarity year: **2025** (0.776)
Highest complaint probability: **2025** (6.0%)
Worst bill shock: **2025** (0.25%)
RED years: 2022, 2025
AMBER years: 2017, 2018, 2021, 2023, 2024
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,441 | £1,278 |
| 2017 | 2.69 | WATCH | £2,498,914 | £31,631 |
| 2018 | — | — | £2,487,878 | £101,531 |
| 2019 | — | — | £2,611,839 | £234,108 |
| 2020 | — | — | £2,924,252 | £128,512 |
| 2021 | — | — | £2,957,719 | £75,232 |
| 2022 | 2.70 | WATCH | £3,161,656 | £338,348 |
| 2023 | 2.72 | WATCH | £3,382,229 | £144,377 |
| 2024 | — | — | £3,774,871 | £347,815 |
| 2025 | — | — | £3,826,810 | £120,993 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,826,810)**
**Treasury growth: £2,467,441 → £3,826,810 (+£1,359,369)**

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
| C6 | 2024-03 | 24.8% | £2,792 | below threshold ⚑ |
| C4 | 2024-09 | 14.0% | £469 | below threshold |

**High-risk no-offer events (≥10% churn): 2** — £3,261 margin at risk.

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
| C_IC3g | 2021-12 | 19.38 | 125.61 | 95.0% |

**High-risk gas reprices: 10**

> ⚑ = customers with ≥15% churn estimate who received no retention offer.

## Retention Decision Economics

Per-offer cost, expected margin protected, and ROI for each retention intervention.

| Customer | Period | Retention Cost £ | Margin Protected £ | ROI | Discount % | Outcome |
|----------|--------|-----------------|-------------------|-----|------------|---------|
| C8 | 2017-04 | £46 | £868 | 18.9× | 3% | retained |
| C3 | 2017-07 | £25 | £495 | 19.6× | 3% | retained |
| C_IC1 | 2018-01 | £24,240 | £163,856 | 6.8× | 8% | retained |
| C5 | 2018-12 | £84 | £1,542 | 18.3× | 3% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £17,469 | £194,971 | 11.2× | 5% | retained |
| C_IC2 | 2021-03 | £5,310 | £91,282 | 17.2× | 3% | retained |
| C_IC1 | 2021-04 | £8,446 | £158,249 | 18.7× | 3% | retained |
| C_IC3 | 2021-12 | £51,790 | £165,016 | 3.2× | 5% | retained |
| C_IC2 | 2022-04 | £9,407 | £95,871 | 10.2× | 3% | retained |
| C_IC1 | 2022-05 | £18,144 | £231,660 | 12.8× | 3% | retained |
| C6 | 2023-03 | £234 | £3,372 | 14.4× | 3% | retained |

**Total retention spend: £150,037** | **Total margin protected: £1,208,823**
**Portfolio retention ROI: 8.1×** | **Retained: 12/12**
**Best ROI intervention: C3 2017-07 (19.6×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £203,620 | — |
| Exit Gas (with churn risk) | £83,481 | -£120,139 |
| Reprice to Breakeven | £205,331 | +£1,711 |

**Loss-making gas accounts: C4**
**Board recommendation: REPRICE GAS**

> Gas drag reduces dual-fuel net margin. Repricing to breakeven is preferable to exit
> because exiting gas risks losing the electricity contract (cross-product churn).

## Portfolio Hedge Fraction Evolution

Average hedge fraction (0=fully naked, 1=fully hedged) per year.

| Year | Portfolio Avg | Min HF | Max HF | Naked Accounts | Covered Accts |
|------|--------------|--------|--------|---------------|--------------|
| 2016 | 88.9% | 85.0% | 92.2% | — | 13 |
| 2017 | 89.1% | 85.0% | 94.3% | — | 14 |
| 2018 | 89.3% | 85.0% | 92.2% | — | 15 |
| 2019 | 83.5% | 0.0% | 96.2% | 1 | 16 |
| 2020 | 81.1% | 0.0% | 96.0% | 1 | 13 |
| 2021 | 84.6% | 0.0% | 97.0% | 1 | 13 |
| 2022 | 86.5% | 0.0% | 97.4% | 1 | 13 |
| 2023 | 83.9% | 0.0% | 96.1% | 1 | 13 |
| 2024 | 80.6% | 0.0% | 94.4% | 1 | 10 |
| 2025 | 88.0% | 85.0% | 89.4% | — | 3 |

**Lowest portfolio hedge fraction: 2024 (80.6%)** — risk erosion from regime-change blindness.
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
| 2023 | 4 | 28 | 7.0 | £48,908 |

**Peak intervention year: 2016 (13 wake-ups)**
**Total committee events (all years): 38**

> Each wake-up adjusts hedge fractions upward for flagged customers. 2016-17 (early book).
> 2022-23 crisis years trigger most interventions on I&C anchor accounts.

## Worst Half-Hourly Settlement Period by Year

Most loss-making single 30-minute period per settlement year.

| Year | Date | SP | Customer | Net Margin £ |
|------|------|----|----------|-------------|
| 2016 | 2016-12-31 | 48 | C1 | -£62 |
| 2017 | 2017-12-31 | 48 | C5 | -£218 |
| 2018 | 2018-12-31 | 48 | C5 | -£442 |
| 2019 | 2019-12-31 | 48 | C3 | -£97 |
| 2020 | 2020-03-16 | 20 | C_IC1 | -£19 |
| 2021 | 2021-12-31 | 48 | C6 | -£543 |
| 2022 | 2022-01-24 | 26 | C_IC1 | -£89 |
| 2023 | 2023-12-31 | 48 | C6 | -£2,032 |
| 2024 | 2024-09-28 | 48 | C4 | -£122 |
| 2025 | 2025-01-08 | 31 | C_IC1 | -£81 |

**Single worst period: 2023 2023-12-31 SP48 (C6, -£2,032)** — exposure from gas supply anchor at year-end pricing.

> SP = settlement period (1-48; SP1 = 00:00-00:30). Year-end gas exposure dominates from 2020 onward as C_IC3g position grows.

## BSC Credit Obligation and Regulatory Levy Breakdown

Elexon BSC credit posting requirement and annual levy costs.

| Year | BSC Credit £ | CM Levy £ | Mutualization £ | CCL £ | Gas Network £ |
|------|-------------|----------|----------------|-------|--------------|
| 2016 | £30 | £37 | — | £189 | £479 |
| 2017 | £559 | £1,977 | — | £11,165 | £898 |
| 2018 | £1,041 | £9,350 | — | £17,434 | £905 |
| 2019 | £1,851 | £31,969 | — | £42,460 | £50,388 |
| 2020 | £2,374 | £56,549 | — | £69,453 | £47,213 |
| 2021 | £5,198 | £49,580 | £41,350 | £71,203 | £50,301 |
| 2022 | £10,204 | £36,672 | £99,453 | £70,920 | £54,554 |
| 2023 | £6,725 | £50,941 | £13,744 | £71,702 | £79,964 |
| 2024 | £3,182 | £68,669 | £1,998 | £72,815 | £76,702 |
| 2025 | £4,647 | £31,004 | £853 | £31,156 | £31,952 |

**Peak BSC credit obligation: 2022 (£10,204)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 14 | £173,370 | £92,774 | £8,775 | £12,384 |
| 2017 | 1 | £3,123,874 | £1,875,002 | £846,747 | £3,123,874 |
| 2018 | 1 | £1,524,534 | £909,010 | £434,894 | £1,524,534 |
| 2019 | 2 | £6,462,540 | £2,447,741 | £201,188 | £3,231,270 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £32,221 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,231,270/customer)**
**Best net margin cohort: 2017 (£846,747)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £75 | — | 108 |
| 2017 | +£2,707 | £37,159 | £312 | — | 168 |
| 2018 | +£9,875 | £65,510 | £519 | — | 180 |
| 2019 | +£28,353 | £164,625 | £28 | — | 204 |
| 2020 | +£35,391 | £238,634 | £-20 | — | 205 |
| 2021 | +£14,982 | £246,246 | £610 | — | 168 |
| 2022 | -£49,726 CREDIT | £256,149 | £72 | 2 | 168 |
| 2023 | +£64,738 | £271,739 | £2,193 | 47 | 168 |
| 2024 | +£109,869 | £307,451 | £-114 | 4271 | 153 |
| 2025 | +£46,911 | £135,614 | £0 | — | 66 |

**CfD turned CREDIT in 2022: -£49,726 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2023 (£2,193)**

> CfD (Contracts for Difference): when wholesale > strike price, generators repay;
> the net credit is passed through as a negative levy on supplier bills.

## Segment Gross Margin Attribution

Gross margin (£) by customer segment and year.

| Year | resi electricity | resi gas | SME electricity | I&C electricity | I&C gas | Total |
|------|----------|----------|----------|----------|----------|-------|
| 2016 | £3,278 | £811 | £2,733 | £0 | £0 | £6,822 |
| 2017 | £4,996 | £1,430 | £3,395 | £113,418 | £0 | £123,239 |
| 2018 | £5,065 | £1,363 | £3,205 | £252,969 | £0 | £262,602 |
| 2019 | £5,781 | £1,428 | £4,055 | £616,211 | £74,626 | £702,101 |
| 2020 | £5,690 | £1,207 | £4,220 | £704,680 | £75,972 | £791,770 |
| 2021 | £5,725 | £360 | £2,955 | £671,861 | £82,255 | £763,155 |
| 2022 | £4,445 | -£730 | £3,824 | £950,568 | £91,118 | £1,049,225 |
| 2023 | £6,665 | -£222 | £4,592 | £823,331 | £121,515 | £955,882 |
| 2024 | £9,428 | £1,299 | £1,558 | £1,121,870 | £123,652 | £1,257,806 |
| 2025 | £3,980 | £239 | £0 | £460,883 | £53,509 | £518,611 |

**Best gross margin year: 2024 (£1,257,806)** | **Worst: 2016 (£6,822)**
**Loss-making: resi gas in 2022 (£-730)**
**Loss-making: resi gas in 2023 (£-222)**


## Price Cap Headroom (Tariff vs SVT)

Percentage difference between contracted unit rate and SVT (price cap) at term start.
Negative = below cap (headroom). Positive = above cap (I&C terms; SVT applies to resi only).

| Year | Terms | Avg vs SVT% | Above Cap | Min% | Max% |
|------|-------|-------------|-----------|------|------|
| 2016 | 3 | -6.3% | 0/3 | -6.7% | +-5.7% |
| 2017 | 3 | -14.3% | 0/3 | -15.8% | +-12.3% |
| 2018 | 4 | -1.1% | 1/4 | -3.3% | +0.7% |
| 2019 | 4 | -18.8% | 1/4 | -29.4% | +12.4% |
| 2020 | 10 | -30.1% | 0/10 | -68.7% | +-19.2% |
| 2021 | 8 | +11.3% | 5/8 | -12.0% | +60.2% |
| 2022 | 8 | +4.6% | 4/8 | -64.0% | +98.1% |
| 2023 | 8 | -34.2% | 0/8 | -60.5% | +-2.3% |
| 2024 | 8 | -20.8% | 1/8 | -54.0% | +3.3% |
| 2025 | 2 | -23.6% | 0/2 | -23.6% | +-23.6% |

**Best headroom year: 2023 (avg 34.2% below SVT)**
**Largest above-SVT year: 2021** (5/8 terms above — note: I&C customers exempt from SVT cap)

> SVT (Standard Variable Tariff) = Ofgem price cap. Residential tariffs must not exceed SVT.
> I&C/SME terms above SVT are expected during crisis years when wholesale >cap.

## Portfolio Stress Test History

Retrospective RAG status: would year-end treasury have survived each scenario?
Credit facility: £2M. Weekly burn estimated at 1% of year-end treasury.

| Year | Treasury £ | Mkt Spike | Credit | Demand | Liquidity | Combined |
|------|-----------|----------|----------|----------|----------|----------|
| 2016 | £2,467,441 | AMBER | RED | GREEN | AMBER | RED |
| 2017 | £2,498,914 | AMBER | RED | GREEN | AMBER | RED |
| 2018 | £2,487,878 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,611,839 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,924,252 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,957,719 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,161,656 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,382,229 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,774,871 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,826,810 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 42.2% | £1,182 | £606 | 1.53% |
| 2017 | 14 | 32.9% | £24,902 | £8,914 | 2.03% |
| 2018 | 15 | 41.1% | £40,074 | £17,616 | 2.23% |
| 2019 | 17 | 40.3% | £96,792 | £41,409 | 2.13% |
| 2020 | 19 | 40.1% | £97,738 | £41,767 | 2.35% |
| 2021 | 14 | 29.1% | £172,566 | £54,605 | 2.22% |
| 2022 | 14 | 22.1% | £302,929 | £75,045 | 2.27% |
| 2023 | 14 | 24.7% | £248,088 | £68,365 | 2.51% |
| 2024 | 14 | 39.1% | £214,259 | £89,878 | 2.44% |
| 2025 | 11 | 38.3% | £111,640 | £47,189 | 3.40% |

**Best EBIT%: 2016 (42.2%)** | **Worst EBIT%: 2022 (22.1%)**
**Peak revenue/customer: 2022 (£302,929)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Population Anchoring -- Complaints & Arrears (Phase PS)

SIM aggregate complaint and arrears rates vs published UK benchmarks.
Complaints: Ofgem QoS survey, I&C adjusted (GREEN 2-6%, crisis 2-8%).
Arrears: DESNZ business energy debt (GREEN <8%, crisis <12%).

| Year | Complaint rate% | C.Bench hi | C.RAG | Arrears rate% | A.Bench hi | A.RAG |
|------|-----------------|-----------|-------|---------------|-----------|-------|
| 2016 | 4.70% | 6% | OK | 15.4% | 8% | ! |
| 2017 | 4.68% | 6% | OK | 21.4% | 8% | ! |
| 2018 | 4.67% | 6% | OK | 26.7% | 8% | ! |
| 2019 | 4.69% | 6% | OK | 29.4% | 8% | ! |
| 2020 | 4.29% | 6% | OK | 5.3% | 8% | OK |
| 2021 | 4.82% | 8% | OK | 21.4% | 12% | ! |
| 2022 | 5.63% | 8% | OK | 50.0% | 12% | ! |
| 2023 | 4.85% | 8% | OK | 21.4% | 12% | ! |
| 2024 | 4.64% | 6% | OK | 35.7% | 8% | ! |
| 2025 | 6.01% | 6% | ~ | 27.3% | 8% | ! |

**Complaints:** 9 of 10 years GREEN (I&C baseline 2-6% normal, 2-8% crisis).
**Arrears:** 1 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).

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
| 2022 | !22.1% | ~24.8% | OK2.27% | ~0% |
| 2023 | !24.7% | ~27.6% | OK2.51% | ~0% |
| 2024 | !39.1% | !41.9% | OK2.44% | OK14% |
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
| C6 | 2024-03 | 14.9% | 24.8% | +9.9pp | ACCURATE |
| C4 | 2024-09 | 14.3% | 14.0% | -0.3pp | ACCURATE |

**Outcomes: 2 underestimated / 3 accurate / 0 overestimated**
**Mean absolute error: 8.5pp**
**Systematic bias: company consistently UNDER-predicted churn risk.**

> Company churn estimates derived from company-observable signals (bill shock,
> margin feedback, renewal history) without access to the simulation's internal
> churn parameters — epistemic gap is expected and realistic for a small supplier.

## Counterfactual Retention & Threshold Optimisation

**Current threshold:** 30% | F1=0.000
**Optimal threshold:** 5% | F1=0.179

**RAG [!]:** RED — 3 unrecoverable high-value miss(es) — model underestimates churn: optimal threshold below current

**Missed retention opportunities:** 5 no-offer churns
  Value at stake: £5,907
  Counterfactually recoverable (with offer): 2/5
  Net value recoverable (after offer cost): £1,961

### Per-miss detail

| Year | Customer | Est | SIM p | Recoverable? | Margin | Net value |
|------|----------|-----|-------|-------------|--------|----------|
| 2020 | C3 | 8% | 6% | No | £585 | £-50 |
| 2020 | C1 | 7% | 21% | Yes | £416 | £366 |
| 2020 | C5 | 9% | 27% | Yes | £1,645 | £1,595 |
| 2024 | C6 | 25% | 15% | No | £2,792 | £-50 |
| 2024 | C4 | 14% | 14% | No | £469 | £-50 |

### Threshold sensitivity curve

| Threshold | Recall | Precision | F1 |
|-----------|--------|-----------|----|
| 0% | 1.000 | 0.086 | 0.159 |
| 5% | 1.000 | 0.098 | 0.179 ← optimal |
| 10% | 0.400 | 0.067 | 0.114 |
| 15% | 0.200 | 0.091 | 0.125 |
| 20% | 0.200 | 0.125 | 0.154 |
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
| Detection gate (never scored above offer threshold) | 5 | 3% | 12% | 2/5 | £1,811 | +7.24 |

## Churn Model Quality (Phase NK)

Company churn model performance: did the company predict churn before it happened?
Threshold: company_churn_estimate > 30% = predicted. Evaluated at each renewal event.

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total churn events | 5 | Customers who actually churned |
| True Positives (TP) | 0 | Churn predicted AND happened |
| False Positives (FP) | 5 | Churn predicted BUT customer renewed |
| False Negatives (FN) | 5 | Churn NOT predicted BUT happened (blind miss) |
| True Negatives (TN) | 48 | No churn predicted AND customer renewed |
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
| Churners | 5 |
| Caught before departure (any renewal) | 3 |
| Never flagged | 2 |
| **Episode recall** | **60.0%** |
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
| 2022 | 0 | 0 | 0 | 8 | 0% | 0% |
| 2023 | 0 | 1 | 0 | 7 | 0% | 0% |
| 2024 | 0 | 0 | 2 | 6 | 0% | 0% |
| 2025 | 0 | 0 | 0 | 2 | 0% | 0% |

## Credit Risk & Capital Stress (Phase NR)

**Ofgem FRA stress multiplier:** 2.5x (empirical: 2021-22 crisis, industry bad debt 1% → 2.5% revenue)

| Year | Revenue £ | Bad Debt £ | Bad Debt % | Crisis Stress £ |
|------|-----------|------------|------------|-----------------|

**Total bad debt (all years):** £3,675
**Crisis stress incremental:** £5,513

**RAG [OK]:** GREEN — Incremental credit stress below 0.5% revenue — not material

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (11 active customers) under 12-month forward scenarios.
Generated: 2026-07-11T17:24:55Z

Closes CLAUDE.md known failure: regime-change blindness — board can now ask 'what if 2021-22 happened again?'

| Scenario | Elec Fwd (£/MWh) | Gas Fwd (£/MWh) | Hedge Rec | Renewing | Exposure Delta |
|----------|------------------|-----------------|-----------|----------|----------------|
| Base | 86.7 | 55.1 | INCREASE | 0 | — |
| Bull | 56.1 | 35.7 | INCREASE | 0 | £-397,750 |
| Bear | 147.9 | 93.8 | INCREASE | 0 | +£795,500 |
| Crisis | 217.3 | 110.2 | INCREASE | 0 | +£1,559,990 |

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
| 2022 | 16 | 11.4% | 23.2% | MODERATE |
| 2023 | 16 | 23.4% | 55.4% | POOR |
| 2024 | 15 | 10.9% | 22.6% | MODERATE |
| 2025 | 3 | 34.0% | 35.7% | POOR |

**Best accuracy year (n≥5): 2024 (10.9% mean error)**
**Worst accuracy year (n≥5): 2023 (23.4% mean error)**

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
| 2022 | 13 | +18.7 | 12 | 1 | 5 |
| 2023 | 13 | +8.7 | 9 | 4 | 10 |
| 2024 | 12 | +4.8 | 5 | 7 | 2 |
| 2025 | 3 | +4.1 | 2 | 1 | 0 |

**Total adjustments 2016-2025: 117** | **Peak avg adjustment: 2022 (+18.7 £/MWh)**
**Emergency reprices: 29 total** (10 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £31,389 | £10,463 | — |
| 2017 | 9 | £105,862 | £11,762 | +£74,474 |
| 2018 | 10 | £2,886,056 | £288,606 | +£2,780,194 |
| 2019 | 11 | £4,214,411 | £383,128 | +£1,328,355 |
| 2020 | 14 | £6,022,119 | £430,151 | +£1,807,708 |
| 2021 | 14 | £5,729,801 | £409,272 | £-292,318 |
| 2022 | 14 | £6,032,618 | £430,901 | +£302,817 |
| 2023 | 14 | £5,084,596 | £363,185 | £-948,022 |
| 2024 | 14 | £4,879,840 | £348,560 | £-204,756 |
| 2025 | 14 | £5,059,710 | £361,408 | +£179,870 |

**Peak portfolio CLV: 2022 (£6,032,618)** | **Earliest/lowest: 2016 (£31,389)**
**Largest YoY gain: 2018 (+£2,780,194)**
**Largest YoY fall: 2023 (£-948,022)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,361.53 | £3,594.97 | £3,892.24 | £7,874.33 | 51.3% | — | — | — | — |
| 2017 | £348,631.32 | £111,055.46 | £112,782.22 | £124,793.64 | 35.8% | +£333,269.79 | +£107,460.50 | +£108,889.98 | +£116,919.31 |
| 2018 | £601,109.91 | £172,888.20 | £163,976.85 | £264,244.87 | 44.0% | +£252,478.59 | +£61,832.74 | +£51,194.63 | +£139,451.22 |
| 2019 | £1,645,470.37 | £496,185.23 | £445,337.03 | £703,948.11 | 42.8% | +£1,044,360.46 | +£323,297.03 | +£281,360.18 | +£439,703.25 |
| 2020 | £1,857,023.18 | £431,600.88 | £631,853.58 | £793,568.73 | 42.7% | +£211,552.81 | £-64,584.35 | +£186,516.55 | +£89,620.61 |
| 2021 | £2,415,921.71 | £971,905.80 | £679,550.33 | £764,465.58 | 31.6% | +£558,898.53 | +£540,304.92 | +£47,696.75 | £-29,103.15 |
| 2022 | £4,241,008.90 | £2,389,086.10 | £801,288.51 | £1,050,634.29 | 24.8% | +£1,825,087.19 | +£1,417,180.30 | +£121,738.18 | +£286,168.71 |
| 2023 | £3,473,230.38 | £1,639,053.05 | £877,068.66 | £957,108.68 | 27.6% | £-767,778.52 | £-750,033.06 | +£75,780.15 | £-93,525.61 |
| 2024 | £2,999,631.38 | £931,630.07 | £809,714.61 | £1,258,286.69 | 41.9% | £-473,599.00 | £-707,422.97 | £-67,354.04 | +£301,178.01 |
| 2025 | £1,228,035.13 | £452,060.81 | £256,896.84 | £519,077.48 | 42.3% | £-1,771,596.25 | £-479,569.26 | £-552,817.78 | £-739,209.21 |

**Best GM year: 2016 (51.3%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Net Margin Bridge (Year-on-Year Attribution)

Decomposes each year's net margin change into: gross margin movement, bad debt, capital costs, policy levies, network costs.

| Transition | Net Δ | Gross Δ | Bad Debt Δ | Capital Δ | Policy Δ | Network Δ | Portfolio | Driver | RAG |
|-----------|-------|---------|-----------|---------|---------|---------|---------|--------|-----|
| 2016→2017 | +£30,353 | +£116,417 | -£237 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£69,900 | +£139,364 | -£206 | -£367 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£132,577 | +£439,498 | +£491 | -£686 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£105,596 | +£89,669 | +£47 | +£360 | -£162,654 | -£33,019 | +2 | policy levies | RED |
| 2020→2021 | -£53,281 | -£28,614 | -£629 | -£3,636 | -£19,033 | -£1,367 | -5 | gross margin | RED |
| 2021→2022 | +£263,116 | +£286,070 | +£538 | -£7,674 | -£1,057 | -£14,761 | +0 | gross margin | GREEN |
| 2022→2023 | -£193,971 | -£93,343 | -£2,121 | +£3,240 | -£70,553 | -£31,194 | +0 | gross margin | RED |
| 2023→2024 | +£203,439 | +£301,924 | +£2,306 | +£514 | -£100,652 | -£654 | +0 | gross margin | GREEN |
| 2024→2025 | -£226,822 | -£739,194 | -£114 | +£3,875 | +£381,910 | +£126,700 | -3 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£226,822)** | **Best transition: 2021→2022 (+£263,116)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Payment Portfolio Health (P2: Billing Infra)

Year-by-year bad debt rate and high-churn-risk customer concentration.

| Year | Bad Debt | Bad Debt Rate | At-Risk Customers | At-Risk % | Trend | RAG |
|------|----------|--------------|-----------------|----------|-------|-----|
| 2016 | £75 | 0.72% | 0/4 | 0% | — STABLE | GREEN |
| 2017 | £312 | 0.13% | 0/10 | 0% | ↓ IMPROVING | GREEN |
| 2018 | £519 | 0.12% | 1/11 | 9% | — STABLE | GREEN |
| 2019 | £28 | 0.00% | 3/12 | 25% | ↓ IMPROVING | GREEN |
| 2020 | £-20 | -0.00% | 5/14 | 36% | ↓ IMPROVING | AMBER |
| 2021 | £610 | 0.04% | 4/11 | 36% | ↑ DETERIORATING | AMBER |
| 2022 | £72 | 0.00% | 9/11 | 82% | ↓ IMPROVING | RED |
| 2023 | £2,193 | 0.08% | 10/11 | 91% | ↑ DETERIORATING | RED |
| 2024 | £-114 | -0.01% | 4/11 | 36% | ↓ IMPROVING | AMBER |
| 2025 | £0 | 0.00% | 2/3 | 67% | ↑ DETERIORATING | RED |

**Worst bad debt year: 2016 (0.72%)** | **Peak at-risk concentration: 2023 (91% of customers)**

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
| 2024 | 2 | £3,261 | £2,073 | £180 | +£1,892 |

**Total opportunity cost vs actual: +£3,723 net** (gross £5,907 margin lost; £355 offer cost if all retained).

> The shadow strategy net gain is small because all no-offer churns were residential customers with low margins. I&C customers (large margins) already received retention offers — the current threshold strategy is near-optimal for the existing portfolio composition.

## Ofgem FRA Regulatory Capital Ratio (Phase NZ)

Equity / (annual revenue ÷ 12). Ofgem FRA minimum: ≥ 1x monthly revenue.
Sector best practice: ≥ 6x (GREEN). Early warning: < 3x (AMBER). Non-compliant: < 1x (RED).
Real-world context: Bulb 2021 collapse at ~-0.01x; Igloo 2021 ~0.07x.

| Year | Equity | Monthly Rev | FRA Ratio | RAG | Compliant |
|------|--------|-------------|-----------|-----|-----------|
| 2016 | £2,473,113.55 | £1,280.13 | 1931.9x | ✓ GREEN | Yes |
| 2017 | £2,587,826.60 | £29,052.61 | 89.1x | ✓ GREEN | Yes |
| 2018 | £2,834,772.25 | £50,092.49 | 56.6x | ✓ GREEN | Yes |
| 2019 | £3,498,603.92 | £137,122.53 | 25.5x | ✓ GREEN | Yes |
| 2020 | £4,242,884.07 | £154,751.93 | 27.4x | ✓ GREEN | Yes |
| 2021 | £4,944,950.54 | £201,326.81 | 24.6x | ✓ GREEN | Yes |
| 2022 | £5,883,167.41 | £353,417.41 | 16.6x | ✓ GREEN | Yes |
| 2023 | £6,739,955.36 | £289,435.87 | 23.3x | ✓ GREEN | Yes |
| 2024 | £7,912,145.79 | £249,969.28 | 31.6x | ✓ GREEN | Yes |
| 2025 | £8,382,538.66 | £102,336.26 | 81.9x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.6x (equity £5,883,167.41 vs monthly revenue £353,417.41). RAG: GREEN.
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
| 2018 | £601,109.91 | £223,412.52 | £1,899.01 | ✓ GREEN |  |
| 2019 | £1,645,470.37 | £611,566.49 | £5,198.32 | ✓ GREEN |  |
| 2020 | £1,857,023.18 | £690,193.62 | £5,866.65 | ✓ GREEN |  |
| 2021 | £2,415,921.71 | £897,917.57 | £7,632.30 | ✓ GREEN | CREDIT EXPECTED |
| 2022 | £4,241,008.90 | £1,576,241.64 | £13,398.05 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,473,230.38 | £1,290,883.96 | £10,972.51 | ✓ GREEN |  |
| 2024 | £2,999,631.38 | £1,114,863.00 | £9,476.34 | ✓ GREEN |  |
| 2025 | £1,228,035.13 | £456,419.72 | £3,879.57 | ✓ GREEN |  |

**Peak reconciliation exposure:** 2022 — max adverse £13,398 (4.5 months weighted tail).

_Note: Outstanding pool ≈ current-year revenue × (weighted outstanding months ÷ 12)._
_Max adverse = pool × blended variance rate (0.5% HH + 4% non-HH, portfolio-weighted)._
## Ofgem Supply Licence Health (Phase OC)

Annual licence health checks: customer base, net assets, liquidity, bad debt.
Breach triggers board escalation and Ofgem notification under SLC 0.
WATCH = within 20% of threshold. BREACH = threshold crossed.

| Year | Customers | Net Assets | Treasury | Cash Wks | Bad Debt % | Overall |
|------|-----------|------------|----------|----------|------------|---------|
| 2016 | 13 | £2,473,113.55 | £2,467,441.30 | 35691w | 0.72% | ✗ BREACH |
| 2017 | 14 | £2,587,826.60 | £2,498,914.43 | 1170w | 0.13% | ✗ BREACH |
| 2018 | 15 | £2,834,772.25 | £2,487,877.83 | 748w | 0.12% | ✗ BREACH |
| 2019 | 17 | £3,498,603.92 | £2,611,839.47 | 274w | 0.00% | ✗ BREACH |
| 2020 | 19 | £4,242,884.07 | £2,924,252.19 | 352w | -0.00% | ✗ BREACH |
| 2021 | 14 | £4,944,950.54 | £2,957,719.05 | 158w | 0.04% | ✗ BREACH |
| 2022 | 14 | £5,883,167.41 | £3,161,655.98 | 69w | 0.00% | ✗ BREACH |
| 2023 | 14 | £6,739,955.36 | £3,382,228.73 | 107w | 0.08% | ✗ BREACH |
| 2024 | 14 | £7,912,145.79 | £3,774,871.00 | 211w | -0.01% | ✗ BREACH |
| 2025 | 11 | £8,382,538.66 | £3,826,810.30 | 440w | 0.00% | ✗ BREACH |

**BREACH years:** 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 — board escalation required.

_Note: Complaints from contact model avg_complaint_probability. Customer count <50 triggers Ofgem viability review — small-portfolio years will show WATCH._
## Ofgem SLC Compliance Scorecard (Phase OD)

10 compliance domains per year, derived from simulation outputs.
G = GREEN (compliant), A = AMBER (watch), R = RED (breach).

| Domain | SLC Ref | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|--------|---------|------|------|------|------|------|------|------|------|------|------|
| Governance | SLC 0-9 | G | G | G | G | G | G | G | G | G | G |
| Billing/Metering | SLC 10-14 | G | G | G | G | G | G | A | G | G | A |
| Payment/Debt | SLC 15-19 | G | G | G | G | G | G | G | G | G | G |
| Information | SLC 20-24 | G | G | G | G | G | G | G | G | G | G |
| Complaints | SLC 25-29 / Ofgem Time to Fix rules | G | G | G | G | G | G | G | G | G | G |
| Vulnerable Cust | SLC 30-35 / PSR | G | G | G | G | G | G | G | G | G | G |
| Tariff/Cap | SLC 36-40 / Default Tariff Cap | G | G | G | G | G | G | G | G | G | G |
| Environmental | SLC 41-50 / RO, CfD, EE obligation | G | G | G | G | G | G | G | G | G | G |
| Network/BSC | SLC 51-60 / BSC obligations | G | G | G | G | G | G | G | G | G | G |
| Financial Res. | SLC 4C / SFR Decision 2023 | G | G | G | G | G | G | G | G | G | G |
| **Overall** |  | G | G | G | G | G | G | A | G | G | A |

**Watch years (AMBER):** 2022, 2025

_Note: Vulnerable customers, tariff/cap, and environmental domains defaulted to GREEN_
_(these are modelled as compliant; detailed SLC breach simulation not yet implemented)._
## Ofgem Annual Supply Return (Phase OE)

UK suppliers must file annual supply returns to Ofgem. Filed by 31 March of the following year.

| Year | Submitted | Customers (R/SME/I&C) | Elec GWh | Gas GWh | Bad Debt/Cust |
|------|-----------|----------------------|----------|---------|---------------|
| 2016 | Yes | 13/13/13 | 0.1 | 0.0 | £6 |
| 2017 | Yes | 14/14/14 | 1.5 | 0.1 | £22 |
| 2018 | Yes | 15/15/15 | 2.9 | 0.1 | £35 |
| 2019 | Yes | 17/17/17 | 7.1 | 2.8 | £2 |
| 2020 | Yes | 19/19/19 | 7.3 | 2.4 | £-1 |
| 2021 | Yes | 14/14/14 | 9.6 | 6.0 | £44 |
| 2022 | Yes | 14/14/14 | 19.0 | 11.8 | £5 |
| 2023 | Yes | 14/14/14 | 15.3 | 6.0 | £157 |
| 2024 | Yes | 14/14/14 | 12.8 | 5.4 | £-8 |
| 2025 | Yes | 11/11/11 | 5.6 | 2.7 | £0 |

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
| 2022 | 9,945.3 | 0.370 ROC/MWh | 3,679.8 | £52.88 | £194,586 |
| 2023 | 9,959.7 | 0.376 ROC/MWh | 3,744.8 | £54.35 | £203,532 |
| 2024 | 9,988.1 | 0.382 ROC/MWh | 3,815.5 | £56.19 | £214,390 |
| 2025 | 4,264.6 | 0.389 ROC/MWh | 1,658.9 | £58.10 | £96,384 |
| **Total** | **66,588.1** | | | | **£1,268,804** |

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
| 2022 | 9,945.3 | GBP0.00 (scheme closed) | NIL |
| 2023 | 9,959.7 | GBP0.00 (scheme closed) | NIL |
| 2024 | 9,988.1 | GBP0.00 (scheme closed) | NIL |
| 2025 | 4,264.6 | GBP0.00 (scheme closed) | NIL |
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
| 2022 | 9 | 150,000 | OK (exempt) | N/A | NIL |
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
| 2021 | ECO3 | GBP4.50 | 9 | OK (exempt) | GBP72 |
| 2022 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP192 |
| 2023 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP157 |
| 2024 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP136 |
| 2025 | ECO4 | GBP6.80 | 6 | OK (exempt) | GBP56 |

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
| 2023 | 4 | £128,230 | £48,908 | 8 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £128,230 | Unique accounts ever adjusted: 11

**Most frequently adjusted accounts:**
- C1: 22 sessions
- C7: 16 sessions
- C5: 12 sessions
- C6: 12 sessions
- C8: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £9,949.67 | Median churn: 32% | Total portfolio CLV: £7,731,132.54

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC1 | £1,762,208.13 | 29% | 14.7 periods |
| C_IC4 | £1,712,238.71 | 20% | 15.7 periods |
| C6 | £19,260.39 | 26% | 12.9 periods |
| C9 | £9,949.67 | 26% | 13.9 periods |

Quadrant CLV: £3,503,656.90 (45% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £3,218,402.68 | 41% | 16.4 periods |
| C_IC2 | £957,420.63 | 32% | 14.2 periods |
| C5 | £10,919.84 | 32% | 14.8 periods |

Quadrant CLV: £4,186,743.15 (54% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C7 | £8,738.68 | 29% | 15.4 periods |
| C3 | £6,491.05 | 11% | 14.5 periods |

Quadrant CLV: £15,229.73 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £9,622.89 | 32% | 13.6 periods |
| C2 | £6,620.17 | 38% | 13.3 periods |
| C1 | £5,452.61 | 35% | 16.8 periods |
| C4 | £3,807.08 | 38% | 14.7 periods |

Quadrant CLV: £25,502.76 (0% of portfolio)

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
| 2022 | 0.791 | 0.056 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.811 | 0.049 | 0 | 0 |  |
| 2024 | 0.816 | 0.046 | 2 | 0 |  |
| 2025 | 0.776 | 0.060 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.4% | **Average billing clarity:** 0.814 | **Average complaint probability:** 0.048

**Acquisition performance:** 4 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2025** (0.776) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

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
| 2022 | 23.0% | 71 | 168 | 42% | ELEVATED |
| 2023 | 17.5% | 49 | 168 | 29% |  |
| 2024 | 16.1% | 41 | 153 | 27% |  |
| 2025 | 24.6% | 26 | 66 | 39% | ELEVATED |

**Crisis peak: 2025** — 24.6% average shock. Energy crisis drove wholesale costs above locked tariff rates,
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
| 2022 | £256,149.25 | **£-49,726.45** | £70,920.22 | £36,672.40 | £69,092.28 | £482,560.59 | £133,368.24 |
| 2023 | £271,739.05 | £64,737.74 | £71,701.96 | £50,940.81 | £75,065.99 | £547,929.87 | £139,151.55 |
| 2024 | £307,450.63 | £109,869.35 | £72,815.13 | £68,669.03 | £82,515.45 | £643,317.21 | £143,068.15 |
| 2025 | £135,614.27 | £46,910.60 | £31,155.87 | £31,003.64 | £36,121.16 | £281,658.45 | £61,118.19 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.00 (2016) → £281,658.45 (2025). CAGR: 76.4%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £953.75 | £324.29 | £9,028.87 | £1,388.28 | 13.3% | YES |
| 2017 | £31,114.51 | £516.54 | £231,633.78 | £2,660.42 | 1.1% | YES |
| 2018 | £101,093.70 | £436.94 | £432,365.68 | £3,113.94 | 0.7% | YES |
| 2019 | £223,618.38 | £10,489.65 | £1,060,516.66 | £137,766.14 | 11.5% | YES |
| 2020 | £118,024.10 | £10,488.12 | £1,102,193.08 | £121,119.88 | 9.9% | YES |
| 2021 | £65,401.22 | £9,830.33 | £1,437,504.91 | £297,399.17 | 17.1% | YES |
| 2022 | £329,607.04 | £8,740.82 | £2,848,806.28 | £589,446.82 | 17.1% | YES |
| 2023 | £135,353.30 | £9,023.55 | £2,296,002.86 | £298,691.57 | 11.5% | YES |
| 2024 | £337,106.50 | £10,708.88 | £1,917,076.86 | £271,569.81 | 12.4% | YES |
| 2025 | £116,452.84 | £4,540.12 | £837,702.08 | £132,970.11 | 13.7% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £203,619.80 | — | Current strategy |
| EXIT_GAS | £83,481.00 | £-120,138.80 | Remove gas; model elec churn risk |
| REPRICE_GAS | £205,331.12 | £1,711.32 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-1,711.32 | -13.16x | +16.6% |

**Accretive gas accounts:** C1g (£669.14), C2g (£1,293.99), C3g (£336.46), C_IC3g (£64,510.98) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £65099 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,715,791.26 | £50,168.70 | £1,450,538.71 | 28.9x | Strong |
| I&C gas | £622,647.03 | £0.00 | £64,510.98 | 0.0x | Low return |
| SME electricity | £30,536.93 | £326.30 | £1,735.86 | 5.3x | Moderate |
| resi electricity | £55,053.10 | £614.51 | £6,450.77 | 10.5x | Moderate |
| resi gas | £7,184.29 | £267.86 | £588.27 | 2.2x | Low return |

## Portfolio Concentration Risk

Revenue concentration analysis across 19 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2249** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,324,498.07 (98.6% of total positive margin)
- resi: £59,006.69 (0.9% of total positive margin)
- SME: £28,977.28 (0.5% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,870,784.18 | 29.2% | 3% | £60,426.33 |
| C_IC3 | I&C | £1,821,875.22 | 28.4% | 20% | £369,658.48 |
| C_IC4 | I&C | £1,103,966.75 | 17.2% | 0% | £0.00 |
| C_IC2 | I&C | £905,291.97 | 14.1% | 4% | £33,224.22 |
| C_IC3g | I&C | £622,579.96 | 9.7% | 0% | £0.00 |

**Concentration Risk Warning:**
- I&C segment accounts for 98.6% of total portfolio margin
- Resi and SME segments are effectively margin-neutral at portfolio scale
- A single large I&C departure would remove 14-29% of all margin
- Board action: diversify acquisition pipeline toward profitable resi/SME to reduce I&C dependency

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 117 renewal(s) (29 gas) based on recent portfolio-wide margin rates: 62 surcharge(s), 55 discount(s).

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
| C5 | electricity | 2017-12-31 | 8.9% | -0.5% | £120.10/MWh | £119.54/MWh |
| C7 | electricity | 2017-12-31 | 3.6% | +2.2% | £120.10/MWh | £122.73/MWh |
| C_IC1 | electricity | 2018-01-31 | -18.3% | +13.1% | £112.24/MWh | £126.99/MWh |
| C2 | electricity | 2018-04-01 | -7.0% | +7.5% | £133.89/MWh | £143.93/MWh |
| C2g | gas | 2018-04-01 | 15.4% | -3.7% | £38.21/MWh | £36.79/MWh |
| C6 | electricity | 2018-04-01 | -4.4% | +6.2% | £133.89/MWh | £142.20/MWh |
| C8 | electricity | 2018-04-01 | 8.1% | -0.1% | £133.89/MWh | £133.81/MWh |
| C3 | electricity | 2018-07-01 | 10.2% | -1.1% | £128.29/MWh | £126.89/MWh |
| C3g | gas | 2018-07-01 | 13.6% | -2.8% | £29.63/MWh | £28.80/MWh |
| C9 | electricity | 2018-07-01 | 1.8% | +3.1% | £128.29/MWh | £132.25/MWh |
| C4 | electricity | 2018-10-01 | 2.0% | +3.0% | £145.00/MWh | £149.37/MWh |
| C4g | gas | 2018-10-01 | 13.7% | -2.8% | £34.60/MWh | £33.61/MWh |
| C1 | electricity | 2018-12-31 | 6.3% | +0.8% | £148.68/MWh | £149.91/MWh |
| C1g | gas | 2018-12-31 | 13.9% | -3.0% | £37.15/MWh | £36.05/MWh |
| C5 | electricity | 2018-12-31 | 9.2% | -0.6% | £148.68/MWh | £147.76/MWh |
| C7 | electricity | 2018-12-31 | 9.6% | -0.8% | £148.68/MWh | £147.48/MWh |
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
| C_IC3g | gas | 2021-12-31 | -21.5% | +14.7% | £109.48/MWh | £125.61/MWh |
| C2 | electricity | 2022-03-31 | -17.6% | +12.8% | £361.95/MWh | £408.28/MWh |
| C2g | gas | 2022-03-31 | -18.6% | +13.3% | £99.49/MWh | £112.70/MWh |
| C6 | electricity | 2022-03-31 | -19.7% | +13.9% | £361.95/MWh | £412.09/MWh |
| C8 | electricity | 2022-03-31 | 2.5% | +2.8% | £361.95/MWh | £371.90/MWh |
| C_IC2 | electricity | 2022-04-30 | -10.1% | +9.0% | £269.81/MWh | £294.18/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.9% | +7.4% | £239.42/MWh | £257.24/MWh |
| C9 | electricity | 2022-06-30 | 4.4% | +1.8% | £255.09/MWh | £259.72/MWh |
| C4 | electricity | 2022-09-30 | 7.2% | +0.4% | £404.86/MWh | £406.38/MWh |
| C4g | gas | 2022-09-30 | -22.9% | +15.0% | £183.79/MWh | £211.36/MWh |
| C1_2 | electricity | 2022-12-30 | 8.6% | -0.3% | £266.73/MWh | £265.96/MWh |
| C7 | electricity | 2022-12-30 | -3.1% | +5.6% | £266.73/MWh | £281.58/MWh |
| C_IC3 | electricity | 2022-12-31 | -14.1% | +11.1% | £168.36/MWh | £186.96/MWh |
| C_IC3g | gas | 2022-12-31 | -43.0% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2 | electricity | 2023-03-31 | -11.2% | +9.6% | £319.17/MWh | £349.74/MWh |
| C2g | gas | 2023-03-31 | -21.3% | +14.7% | £83.68/MWh | £95.94/MWh |
| C6 | electricity | 2023-03-31 | -3.9% | +5.9% | £319.17/MWh | £338.13/MWh |
| C8 | electricity | 2023-03-31 | 3.6% | +2.2% | £319.17/MWh | £326.13/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.8% | +14.9% | £171.46/MWh | £196.97/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.2% | +12.6% | £163.19/MWh | £183.73/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.11/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.04/MWh |
| C4g | gas | 2023-09-30 | -17.6% | +12.8% | £47.83/MWh | £53.94/MWh |
| C1_2 | electricity | 2023-12-30 | 29.1% | -5.0% | £242.22/MWh | £230.11/MWh |
| C7 | electricity | 2023-12-30 | 26.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 22.3% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -7.3% | +7.7% | £51.89/MWh | £55.87/MWh |
| C2 | electricity | 2024-03-30 | 14.6% | -3.3% | £207.71/MWh | £200.84/MWh |
| C2g | gas | 2024-03-30 | 12.1% | -2.0% | £49.31/MWh | £48.30/MWh |
| C6 | electricity | 2024-03-30 | 12.4% | -2.2% | £207.71/MWh | £203.14/MWh |
| C8 | electricity | 2024-03-30 | 12.4% | -2.2% | £207.71/MWh | £203.14/MWh |
| C_IC2 | electricity | 2024-06-28 | -31.4% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.8% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C1_2 | electricity | 2024-12-29 | 0.4% | +3.8% | £243.79/MWh | £253.01/MWh |
| C7 | electricity | 2024-12-29 | 22.6% | -5.0% | £243.79/MWh | £231.60/MWh |
| C_IC3 | electricity | 2024-12-30 | 14.4% | -3.2% | £116.37/MWh | £112.67/MWh |
| C_IC3g | gas | 2024-12-30 | 17.0% | -4.5% | £50.47/MWh | £48.21/MWh |
| C2 | electricity | 2025-03-30 | 4.8% | +1.6% | £284.89/MWh | £289.53/MWh |
| C2g | gas | 2025-03-30 | 13.8% | -2.9% | £71.57/MWh | £69.51/MWh |
| C8 | electricity | 2025-03-30 | 1.2% | +3.4% | £284.89/MWh | £294.60/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **5** | Blind misses: **5** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 0 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £5,906.90 | deliberate: £0.00 | total: £5,906.90

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.08 | 0.06 | No | £585.26 |
| C1 | 2020-12-30 | Blind miss | 0.07 | 0.21 | No | £415.98 |
| C5 | 2020-12-30 | Blind miss | 0.09 | 0.27 | No | £1,645.00 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.15 | No | £2,791.79 |
| C4 | 2024-09-29 | Blind miss | 0.14 | 0.14 | No | £468.86 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £136,677.18 | £64,510.98 | £201,188.16 | Yes |
| C2+C2g | £1,177.20 | £1,293.99 | £2,471.19 | Yes |
| C1+C1g | £415.73 | £669.14 | £1,084.87 | Yes |
| C3+C3g | £182.41 | £336.46 | £518.88 | Yes |
| C4+C4g | £68.03 | £-1,711.32 | £-1,643.29 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £65,099.25.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,523,824.60 across 19 billing accounts. Revenue: £14,028,957.18.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,123,873.83 | £1,875,002.30 | £18,435.60 | £846,747.11 | 27.1% |
| 2 | C_IC2 | fixed | £1,524,534.49 | £909,010.15 | £8,630.44 | £434,893.78 | 28.5% |
| 3 | C_IC3 | pass_through | £4,629,960.35 | £1,825,093.54 | £23,102.67 | £136,677.18 | 3.0% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £64,510.98 | 3.5% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £32,220.65 | 1.2% |
| 6 | C8 | fixed | £21,649.27 | £12,429.82 | £134.60 | £2,291.54 | 10.6% |
| 7 | C9 | fixed | £20,244.05 | £12,708.53 | £131.44 | £2,240.28 | 11.1% |
| 8 | C6 | fixed | £39,190.43 | £22,706.35 | £266.16 | £1,936.26 | 4.9% |
| 9 | C2g | fixed | £8,090.72 | £3,287.48 | £106.78 | £1,293.99 | 16.0% |
| 10 | C2 | fixed | £9,515.76 | £5,522.81 | £58.28 | £1,177.20 | 12.4% |
| 11 | C1g | fixed | £2,436.42 | £1,355.24 | £15.79 | £669.14 | 27.5% |
| 12 | C1_2 | fixed | £11,629.63 | £5,662.84 | £81.65 | £648.00 | 5.6% |
| 13 | C1 | fixed | £3,545.67 | £2,343.04 | £14.71 | £415.73 | 11.7% |
| 14 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £336.46 | 12.5% |
| 15 | C3 | fixed | £3,628.76 | £2,388.88 | £14.77 | £182.41 | 5.0% |
| 16 | C4 | fixed | £6,193.87 | £3,243.30 | £37.88 | £68.03 | 1.1% |
| 17 | C5 | fixed | £12,497.06 | £7,830.58 | £60.14 | £-200.40 | -1.6% |
| 18 | C7 | fixed | £21,729.00 | £10,753.88 | £141.17 | £-572.42 | -2.6% |
| 19 | C4g | fixed | £10,335.76 | £1,243.04 | £130.00 | £-1,711.32 | -16.6% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,028,957 | 100.0% |
| Wholesale cost | -£7,597,745 | 54.2% |
| **Gross supply margin** | **£6,431,213** | **45.8%** |
| Policy + Network costs | -£4,856,011 | 34.6% |
| Capital cost | -£51,377 | 0.4% |
| **Net supply margin** | **£1,523,825** | **10.9%** |

> *The ledger's `net_margin_gbp` (£6,393,941) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,023,008 | 47.5% | 12.1% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 3.5% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £51,687 | 59.1% | 3.4% | CMA 3-8% | ✓ |
| resi/elec | £86,506 | 57.1% | 6.7% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £23,546 | 30.5% | 2.5% | Ofgem CMA 2-4% | ✓ |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: PASS** — all segments within benchmarks.
## Transaction Log

Total events: 3,382,448

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 4 |
| bad_debt_event | 1,588 |
| billing_event | 1,588 |
| capital_charge_event | 1,628,977 |
| cost_to_serve_event | 114 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,588 |
| payment_received_event | 1,588 |
| settlement_event | 1,745,299 |
| vat_remittance_event | 1,588 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £22,565,291.81 |
|   Less: VAT remitted to HMRC | (£3,739,867.99) |
| = Revenue (ex-VAT) | £18,825,423.81 |
| Less: non-commodity pass-through | (£4,782,360.86) |
| Wholesale cost (settlement events) | (£7,597,744.58) |
| Gross margin | £6,445,318.38 |
| Capital charges | (£51,377.37) |
| Net margin | £6,393,941.01 |

_Cash reconciliation: of £22,565,291.81 billed, bad debt of £451,429.52 was written off, leaving £22,113,862.28 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £9,682,379.47._

| Acquisition spend | (£862.50) |
| Fixed overhead | (£5,700.00) |
| Cost to serve | (£18,730.56) |
| Operating net margin | £6,368,647.95 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,361.53 | £3,594.97 | £3,892.24 | £7,874.33 | £234.59 | £1,310.66 | £6,477.33 (42.2%) |
| 2017 | £348,631.32 | £111,055.46 | £112,782.22 | £124,793.64 | £7,077.55 | £8,807.01 | £114,713.05 (32.9%) |
| 2018 | £601,109.91 | £172,888.20 | £163,976.85 | £264,244.87 | £13,429.61 | £15,658.73 | £246,945.65 (41.1%) |
| 2019 | £1,645,470.37 | £496,185.23 | £445,337.03 | £703,948.11 | £35,050.90 | £37,790.05 | £663,831.67 (40.3%) |
| 2020 | £1,857,023.18 | £431,600.88 | £631,853.58 | £793,568.73 | £43,654.54 | £47,322.36 | £744,280.15 (40.1%) |
| 2021 | £2,415,921.71 | £971,905.80 | £679,550.33 | £764,465.58 | £53,734.20 | £56,796.49 | £702,066.47 (29.1%) |
| 2022 | £4,241,008.90 | £2,389,086.10 | £801,288.51 | £1,050,634.29 | £96,079.23 | £99,141.10 | £938,216.87 (22.1%) |
| 2023 | £3,473,230.38 | £1,639,053.05 | £877,068.66 | £957,108.68 | £87,222.64 | £90,284.23 | £856,787.95 (24.7%) |
| 2024 | £2,999,631.38 | £931,630.07 | £809,714.61 | £1,258,286.69 | £73,198.08 | £76,574.24 | £1,172,190.42 (39.1%) |
| 2025 | £1,228,035.13 | £452,060.81 | £256,896.84 | £519,077.48 | £41,748.18 | £43,037.72 | £470,392.87 (38.3%) |
| **Total** | **£18,825,423.81** | | | | | | **£5,915,902.44 (31.4%)** |

**Best year:** 2024 — net £1,172,190.42 (39.1% margin)
**Worst year:** 2016 — net £6,477.33 (42.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,382,538.66 |
| Trade Receivables | £-0.00 |
| **Total Assets** | **£8,382,538.66** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,915,902.44 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,361.53 | +4.7% | £6,592.99 | £6,477.33 | -1.8% | GREEN |
| 2017 | £16,138.86 | £348,631.32 | +2060.2% | £7,252.29 | £114,713.05 | +1481.7% | RED |
| 2018 | £386,623.75 | £601,109.91 | +55.5% | £128,424.00 | £246,945.65 | +92.3% | RED |
| 2019 | £675,851.95 | £1,645,470.37 | +143.5% | £281,335.50 | £663,831.67 | +136.0% | RED |
| 2020 | £1,816,630.04 | £1,857,023.18 | +2.2% | £736,963.94 | £744,280.15 | +1.0% | GREEN |
| 2021 | £2,028,952.42 | £2,415,921.71 | +19.1% | £833,649.22 | £702,066.47 | -15.8% | RED |
| 2022 | £2,607,611.88 | £4,241,008.90 | +62.6% | £790,935.58 | £938,216.87 | +18.6% | RED |
| 2023 | £4,508,414.67 | £3,473,230.38 | -23.0% | £1,029,561.00 | £856,787.95 | -16.8% | RED |
| 2024 | £3,512,844.39 | £2,999,631.38 | -14.6% | £893,105.75 | £1,172,190.42 | +31.2% | RED |
| 2025 | £3,145,356.42 | £1,228,035.13 | -61.0% | £1,315,150.33 | £470,392.87 | -64.2% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,387,378.51

## 2016

**Trading & Risk**

- Net margin: £1,278.04 (gross £6,822.19, capital £86.34)
  - Electricity: gross £6,011.45, capital £78.97, net £953.75
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
- Worst single period: C1 on 2016-12-31 period 48, net margin £-62.38

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
- C3 (electricity): tariff £98.21/MWh, net margin £29.26
- C3g (gas): tariff £21.93/MWh, net margin £45.98
- C4 (electricity): tariff £77.34-£147.65/MWh, net margin £15.96
- C4g (gas): tariff £24.40/MWh, net margin £52.11
- C5 (electricity): tariff £117.30-£131.01/MWh, net margin £271.93
- C6 (electricity): tariff £107.62/MWh, net margin £24.49
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £267.20
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £139.89
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £48.41

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.829, average bill shock 19.7%, bad debt provision £75.35, avg complaint probability 4.7%
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

**Year narrative:** 2016 produced a net gain of £1,278.04 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 31 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £31,631.05 (gross £123,238.74, capital £1,273.58)
  - Electricity: gross £121,809.17, capital £1,258.73, net £31,114.51
  - Gas: gross £1,429.57, capital £14.85, net £516.54
- Treasury at year end: £2,498,914.43
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.92 (avg 0.92), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.94 (avg 0.94)
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
- Worst single period: C5 on 2017-12-31 period 48, net margin £-218.13

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £11,762.47
  - By billing account: C1 £5,740.27, C2 £11,364.56, C3 £9,644.02, C4 £8,744.86, C5 £12,167.53, C6 £24,200.80, C7 £8,895.16, C8 £13,842.89, C9 £11,262.19
- Bill shock events (>=20%): 50 -- C1g 2017-01-31 (31%); C1g 2017-02-28 (28%); C1g 2017-05-31 (30%); C1g 2017-06-30 (30%); C1g 2017-09-30 (21%); C1g 2017-11-30 (70%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-05-31 (34%); C2g 2017-06-30 (29%); C2g 2017-09-30 (27%); C2g 2017-11-30 (66%); C2g 2017-12-31 (22%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-05-31 (30%); C3g 2017-06-30 (23%); C3g 2017-09-30 (21%); C3g 2017-11-30 (59%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (30%); C4 2017-09-30 (23%); C4 2017-10-31 (27%); C4 2017-11-30 (29%); C4g 2017-01-31 (23%); C4g 2017-02-28 (22%); C4g 2017-05-31 (33%); C4g 2017-06-30 (35%); C4g 2017-09-30 (36%); C4g 2017-10-31 (22%); C4g 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £92.60-£198.06/MWh, net margin £74.90
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £115.22
- C2 (electricity): tariff £84.56-£188.36/MWh, net margin £110.01
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £194.46
- C3 (electricity): tariff £98.21-£120.79/MWh, net margin £88.24
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £69.89
- C4 (electricity): tariff £77.34-£164.79/MWh, net margin £49.52
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £136.97
- C5 (electricity): tariff £119.54-£131.01/MWh, net margin £-53.44 -- **net-negative**
- C6 (electricity): tariff £107.62-£126.91/MWh, net margin £98.49
- C7 (electricity): tariff £96.43-£195.85/MWh, net margin £194.36
- C8 (electricity): tariff £84.56-£191.05/MWh, net margin £246.35
- C9 (electricity): tariff £77.16-£181.43/MWh, net margin £166.16
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £30,139.92

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.818, average bill shock 16.6%, bad debt provision £312.32, avg complaint probability 4.7%
- Solvency signal: £249,891/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,074.48 vs. naked (unhedged) net margin: £112,510.11
- hedging cost £82,435.62 vs. a fully unhedged book (commodity-only: actual net £30,074.48 vs. naked net £112,510.11)
  - C1: actual £22.41 vs. naked £341.15 -- hedging cost £318.75
  - C1g: actual £131.41 vs. naked £272.27 -- hedging cost £140.86
  - C2: actual £72.90 vs. naked £442.11 -- hedging cost £369.21
  - C2g: actual £207.48 vs. naked £448.25 -- hedging cost £240.78
  - C3: actual £114.24 vs. naked £516.77 -- hedging cost £402.53
  - C3g: actual £30.62 vs. naked £394.35 -- hedging cost £363.73
  - C4: actual £32.54 vs. naked £271.42 -- hedging cost £238.88
  - C4g: actual £44.94 vs. naked £544.66 -- hedging cost £499.72
  - C5: actual £-208.04 vs. naked £1,068.22 -- hedging cost £1,276.26
  - C6: actual £119.83 vs. naked £1,691.30 -- hedging cost £1,571.47
  - C7: actual £-51.13 vs. naked £820.77 -- hedging cost £871.90
  - C8: actual £261.95 vs. naked £997.85 -- hedging cost £735.90
  - C9: actual £247.95 vs. naked £957.89 -- hedging cost £709.94
  - C_IC1: actual £29,047.38 vs. naked £103,743.08 -- hedging cost £74,695.71

**Year narrative:** 2017 produced a net gain of £31,631.05 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 50 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £101,530.64 (gross £262,602.37, capital £1,640.49)
  - Electricity: gross £261,239.56, capital £1,619.42, net £101,093.70
  - Gas: gross £1,362.80, capital £21.07, net £436.94
- Treasury at year end: £2,487,877.83
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.91 (avg 0.91)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2018-12-31 period 48, net margin £-442.23

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £288,605.58
  - By billing account: C1 £5,706.06, C2 £8,726.77, C3 £9,643.83, C4 £7,300.25, C5 £12,344.35, C6 £20,424.84, C7 £8,038.55, C8 £10,898.61, C9 £10,640.88, C_IC1 £2,792,331.69
- Bill shock events (>=20%): 60 -- C1g 2018-04-30 (37%); C1g 2018-05-31 (29%); C1g 2018-06-30 (30%); C1g 2018-09-30 (25%); C1g 2018-10-31 (46%); C1g 2018-11-30 (27%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (28%); C2g 2018-05-31 (34%); C2g 2018-06-30 (34%); C2g 2018-09-30 (33%); C2g 2018-10-31 (45%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (28%); C3g 2018-05-31 (32%); C3g 2018-06-30 (29%); C3g 2018-08-31 (34%); C3g 2018-09-30 (34%); C3g 2018-10-31 (35%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (29%); C4 2018-09-30 (24%); C4 2018-10-31 (44%); C4 2018-11-30 (30%); C4g 2018-04-30 (36%); C4g 2018-05-31 (33%); C4g 2018-06-30 (36%); C4g 2018-09-30 (39%); C4g 2018-10-31 (85%); C4g 2018-11-30 (24%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C2 23%, C3 23%, C6 23%, C7 20%, C8 23%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £92.60-£224.86/MWh, net margin £36.58
- C1g (gas): tariff £33.49-£36.05/MWh, net margin £142.44
- C2 (electricity): tariff £98.66-£215.90/MWh, net margin £93.32
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £189.04
- C3 (electricity): tariff £120.79-£126.89/MWh, net margin £90.26
- C3g (gas): tariff £23.11-£28.80/MWh, net margin £40.74
- C4 (electricity): tariff £86.32-£224.05/MWh, net margin £13.09
- C4g (gas): tariff £26.10-£33.61/MWh, net margin £64.72
- C5 (electricity): tariff £119.54-£153.61/MWh, net margin £-649.10 -- **net-negative**
- C6 (electricity): tariff £126.91-£142.20/MWh, net margin £-6.78 -- **net-negative**
- C7 (electricity): tariff £96.43-£221.22/MWh, net margin £-15.12 -- **net-negative**
- C8 (electricity): tariff £100.07-£200.72/MWh, net margin £164.50
- C9 (electricity): tariff £95.03-£198.37/MWh, net margin £242.67
- C_IC1 (electricity): tariff £-82.12-£228.58/MWh, net margin £107,506.53
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,382.25 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.809, average bill shock 16.0%, bad debt provision £518.72, avg complaint probability 4.7%
- Solvency signal: £226,171/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £109,563.65 vs. naked (unhedged) net margin: £246,641.26
- hedging cost £137,077.61 vs. a fully unhedged book (commodity-only: actual net £109,563.65 vs. naked net £246,641.26)
  - C1: actual £105.97 vs. naked £575.46 -- hedging cost £469.49
  - C1g: actual £144.33 vs. naked £420.62 -- hedging cost £276.29
  - C2: actual £62.57 vs. naked £503.97 -- hedging cost £441.40
  - C2g: actual £158.01 vs. naked £399.99 -- hedging cost £241.98
  - C3: actual £26.60 vs. naked £557.84 -- hedging cost £531.23
  - C3g: actual £38.90 vs. naked £481.52 -- hedging cost £442.62
  - C4: actual £94.19 vs. naked £459.22 -- hedging cost £365.03
  - C4g: actual £68.19 vs. naked £870.63 -- hedging cost £802.44
  - C5: actual £125.82 vs. naked £1,985.96 -- hedging cost £1,860.14
  - C6: actual £-140.85 vs. naked £1,834.30 -- hedging cost £1,975.15
  - C7: actual £71.35 vs. naked £1,347.35 -- hedging cost £1,276.00
  - C8: actual £24.60 vs. naked £936.91 -- hedging cost £912.31
  - C9: actual £143.69 vs. naked £1,046.01 -- hedging cost £902.32
  - C_IC1: actual £115,524.26 vs. naked £201,775.17 -- hedging cost £86,250.91
  - C_IC2: actual £-6,883.98 vs. naked £33,446.32 -- hedging cost £40,330.30

**Year narrative:** 2018 produced a net gain of £101,530.64 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 60 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £234,108.02 (gross £702,100.60, capital £2,326.39)
  - Electricity: gross £626,046.76, capital £2,304.94, net £223,618.38
  - Gas: gross £76,053.84, capital £21.46, net £10,489.65
- Treasury at year end: £2,611,839.47
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C3 on 2019-12-31 period 48, net margin £-96.62

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £383,128.28
  - By billing account: C1 £5,661.65, C2 £8,873.94, C3 £8,256.51, C4 £6,507.79, C5 £11,192.06, C6 £19,074.59, C7 £8,373.08, C8 £9,472.90, C9 £9,974.34, C_IC1 £2,348,957.18, C_IC2 £1,778,067.01
- Bill shock events (>=20%): 66 -- C1 2019-04-30 (21%); C1g 2019-01-31 (36%); C1g 2019-02-28 (26%); C1g 2019-05-31 (23%); C1g 2019-06-30 (35%); C1g 2019-10-31 (74%); C1g 2019-11-30 (43%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-01-31 (25%); C2g 2019-02-28 (26%); C2g 2019-04-30 (35%); C2g 2019-06-30 (32%); C2g 2019-07-31 (25%); C2g 2019-09-30 (30%); C2g 2019-10-31 (64%); C2g 2019-11-30 (28%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-02-28 (26%); C3g 2019-06-30 (33%); C3g 2019-07-31 (35%); C3g 2019-09-30 (35%); C3g 2019-10-31 (64%); C3g 2019-11-30 (31%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (32%); C4 2019-09-30 (27%); C4 2019-11-30 (27%); C4g 2019-01-31 (30%); C4g 2019-02-28 (25%); C4g 2019-05-31 (21%); C4g 2019-06-30 (33%); C4g 2019-07-31 (37%); C4g 2019-09-30 (31%); C4g 2019-10-31 (34%); C4g 2019-11-30 (35%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C1 29%, C4 35%, C5 35%, C7 29%, C9 23%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £99.01-£224.86/MWh, net margin £122.17
- C1g (gas): tariff £25.33-£36.05/MWh, net margin £156.37
- C2 (electricity): tariff £113.09-£227.85/MWh, net margin £145.70
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £134.46
- C3 (electricity): tariff £120.68-£126.89/MWh, net margin £-70.98 -- **net-negative**
- C3g (gas): tariff £23.00-£28.80/MWh, net margin £97.85
- C4 (electricity): tariff £99.60-£224.05/MWh, net margin £114.38
- C4g (gas): tariff £19.47-£33.61/MWh, net margin £101.05
- C5 (electricity): tariff £126.07-£153.61/MWh, net margin £233.80
- C6 (electricity): tariff £142.20-£148.71/MWh, net margin £129.38
- C7 (electricity): tariff £99.67-£221.22/MWh, net margin £111.49
- C8 (electricity): tariff £105.14-£211.40/MWh, net margin £192.94
- C9 (electricity): tariff £98.80-£198.37/MWh, net margin £181.91
- C_IC1 (electricity): tariff £0.00-£263.70/MWh, net margin £139,395.02
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £79,281.83
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £3,780.73
- C_IC3g (gas): tariff £27.53/MWh, net margin £9,999.92

**Portfolio Health**

- Capital cost ratio: 0.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.823, average bill shock 17.2%, bad debt provision £27.71, avg complaint probability 4.7%
- Solvency signal: £217,653/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £252,637.66 vs. naked (unhedged) net margin: £836,858.75
- hedging cost £584,221.09 vs. a fully unhedged book (commodity-only: actual net £252,637.66 vs. naked net £836,858.75)
  - C1: actual £85.49 vs. naked £501.36 -- hedging cost £415.87
  - C1g: actual £137.12 vs. naked £302.41 -- hedging cost £165.30
  - C2: actual £157.70 vs. naked £669.23 -- hedging cost £511.53
  - C2g: actual £93.46 vs. naked £403.54 -- hedging cost £310.08
  - C3: actual £35.26 vs. naked £668.43 -- hedging cost £633.17
  - C3g: actual £135.78 vs. naked £505.74 -- hedging cost £369.96
  - C4: actual £95.76 vs. naked £441.56 -- hedging cost £345.80
  - C4g: actual £101.34 vs. naked £573.92 -- hedging cost £472.58
  - C5: actual £-28.09 vs. naked £1,589.60 -- hedging cost £1,617.68
  - C6: actual £233.29 vs. naked £2,599.53 -- hedging cost £2,366.24
  - C7: actual £56.69 vs. naked £1,146.37 -- hedging cost £1,089.68
  - C8: actual £240.89 vs. naked £1,370.83 -- hedging cost £1,129.94
  - C9: actual £159.21 vs. naked £1,258.26 -- hedging cost £1,099.06
  - C_IC1: actual £154,892.48 vs. naked £297,973.82 -- hedging cost £143,081.33
  - C_IC2: actual £85,558.69 vs. naked £161,523.27 -- hedging cost £75,964.58
  - C_IC3: actual £1,355.95 vs. naked £289,938.26 -- hedging cost £288,582.30
  - C_IC3g: actual £9,326.63 vs. naked £75,392.62 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £234,108.02 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £128,512.22 (gross £791,769.73, capital £1,966.22)
  - Electricity: gross £714,590.18, capital £1,955.93, net £118,024.10
  - Gas: gross £77,179.55, capital £10.29, net £10,488.12
- Treasury at year end: £2,924,252.19
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
- Average CLV (Point-in-Time, year-end 2020): £430,151.34
  - By billing account: C1 £4,622.02, C1_2 £16.03, C2 £6,623.51, C3 £5,895.98, C4 £7,053.95, C5 £12,943.29, C6 £19,510.54, C7 £7,742.53, C8 £9,552.17, C9 £9,057.96, C_IC1 £1,391,889.73, C_IC2 £887,578.71, C_IC3 £2,197,517.58, C_IC4 £1,462,114.75
- Bill shock events (>=20%): 53 -- C1 2020-04-30 (20%); C1g 2020-01-31 (21%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-29 (23%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (32%); C4 2020-09-30 (23%); C4 2020-10-31 (24%); C4 2020-11-30 (25%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (49%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 35%, C4 41%, C5 32%, C7 20%, C8 23%, C9 23%, C_IC1 41%, C_IC2 41%, C_IC3 20%

**Pricing & Margin**

- C1 (electricity): tariff £99.01-£189.01/MWh, net margin £99.21
- C1_2 (electricity): tariff £133.55/MWh, net margin £-1.02 -- **net-negative**
- C1g (gas): tariff £25.33/MWh, net margin £145.23
- C2 (electricity): tariff £113.06-£227.85/MWh, net margin £201.59
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £143.77
- C3 (electricity): tariff £120.68/MWh, net margin £45.64
- C3g (gas): tariff £23.00/MWh, net margin £82.00
- C4 (electricity): tariff £96.23-£190.15/MWh, net margin £91.63
- C4g (gas): tariff £16.09-£19.47/MWh, net margin £86.36
- C5 (electricity): tariff £126.07/MWh, net margin £-3.59 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.71/MWh, net margin £401.71
- C7 (electricity): tariff £99.67-£205.86/MWh, net margin £90.87
- C8 (electricity): tariff £110.22-£211.40/MWh, net margin £375.88
- C9 (electricity): tariff £85.31-£188.62/MWh, net margin £150.09
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £53,259.99
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £44,258.51
- C_IC3 (electricity): tariff £37.48-£80.61/MWh, net margin £13,054.01
- C_IC3g (gas): tariff £15.44-£19.38/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £5,999.58

**Portfolio Health**

- Capital cost ratio: 0.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 205, average clarity 0.831, average bill shock 14.4%, bad debt provision £-19.70, avg complaint probability 4.3%
- Solvency signal: £208,875/customer (14 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2020 produced a net gain of £128,512.22 across 19 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £75,231.55 (gross £763,155.26, capital £5,602.62)
  - Electricity: gross £680,540.29, capital £5,590.58, net £65,401.22
  - Gas: gross £82,614.97, capital £12.04, net £9,830.33
- Treasury at year end: £2,957,719.05
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.87 (avg 0.87), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2021-12-31 period 48, net margin £-543.33

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2021): £409,271.50
  - By billing account: C1 £4,744.82, C1_2 £986.91, C2 £6,791.99, C3 £5,831.99, C4 £5,409.21, C5 £12,050.99, C6 £17,951.57, C7 £6,973.39, C8 £9,219.23, C9 £8,492.59, C_IC1 £1,502,450.85, C_IC2 £765,170.10, C_IC3 £2,019,710.36, C_IC4 £1,364,017.02
- Bill shock events (>=20%): 47 -- C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (62%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (32%); C4 2021-09-30 (25%); C4 2021-10-31 (47%); C4 2021-11-30 (35%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%); C1_2 2021-01-31 (1207%); C1_2 2021-05-31 (33%); C1_2 2021-06-30 (55%); C1_2 2021-10-31 (76%); C1_2 2021-11-30 (75%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C7 20%, C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £133.55-£333.14/MWh, net margin £-89.36 -- **net-negative**
- C2 (electricity): tariff £113.06-£274.50/MWh, net margin £198.84
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £126.10
- C4 (electricity): tariff £96.23-£274.50/MWh, net margin £-37.46 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-295.69 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.10/MWh, net margin £-17.67 -- **net-negative**
- C7 (electricity): tariff £107.83-£274.50/MWh, net margin £-99.25 -- **net-negative**
- C8 (electricity): tariff £110.22-£274.50/MWh, net margin £431.50
- C9 (electricity): tariff £85.31-£264.44/MWh, net margin £62.13
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £28,128.63
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £56,369.05
- C_IC3 (electricity): tariff £42.22-£391.32/MWh, net margin £-25,484.20 -- **net-negative**
- C_IC3g (gas): tariff £19.38-£125.61/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £5,939.02

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.816, average bill shock 24.2%, bad debt provision £609.77, avg complaint probability 4.8%
- Solvency signal: £268,884/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £191,531.47 vs. naked (unhedged) net margin: £457,066.87
- hedging cost £265,535.40 vs. a fully unhedged book (commodity-only: actual net £191,531.47 vs. naked net £457,066.87)
  - C1_2: actual £-75.69 vs. naked £590.74 -- hedging cost £666.43
  - C2: actual £138.10 vs. naked £150.31 -- hedging cost £12.22
  - C2g: actual £45.59 vs. naked £-190.70 -- hedging added £236.29
  - C4: actual £-231.16 vs. naked £-156.26 -- hedging cost £74.90
  - C4g: actual £-874.54 vs. naked £-1,344.38 -- hedging added £469.85
  - C6: actual £512.38 vs. naked £267.67 -- hedging added £244.71
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-48.53 vs. naked £-184.07 -- hedging added £135.54
  - C_IC1: actual £27,321.95 vs. naked £-61,903.59 -- hedging added £89,225.54
  - C_IC2: actual £63,529.85 vs. naked £22,089.60 -- hedging added £41,440.25
  - C_IC3: actual £100,518.67 vs. naked £235,005.41 -- hedging cost £134,486.74
  - C_IC3g: actual £4,142.87 vs. naked £85,199.40 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £178,304.23 -- hedging cost £180,207.49

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £75,231.55 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 47 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £338,347.87 (gross £1,049,224.77, capital £13,276.32)
  - Electricity: gross £958,836.70, capital £13,229.01, net £329,607.04
  - Gas: gross £90,388.06, capital £47.31, net £8,740.82
- Treasury at year end: £3,161,655.98
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2 0.96 (avg 0.96), C2g 0.85 (avg 0.85), C4 0.96 (avg 0.96), C4g 0.88 (avg 0.88), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,037,806.78, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,211.15 / stressed £20,491.01) ratio 2.69
  - 2022-05-29: treasury £3,037,927.17, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,320.95 / stressed £20,520.22) ratio 2.70
  - 2022-06-28: treasury £3,037,921.93, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,320.95 / stressed £20,520.22) ratio 2.70
  - 2022-07-28: treasury £3,037,722.83, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
  - 2022-08-27: treasury £3,037,710.74, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
  - 2022-09-26: treasury £3,037,693.15, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
  - 2022-10-26: treasury £3,036,777.42, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
  - 2022-11-25: treasury £3,036,774.91, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
  - 2022-12-25: treasury £3,036,742.14, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,382.36 / stressed £20,532.45) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC1 on 2022-01-24 period 26, net margin £-89.07

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2022): £430,901.32
  - By billing account: C1 £4,582.39, C1_2 £2,003.94, C2 £5,036.95, C3 £5,087.16, C4 £3,176.70, C5 £9,425.03, C6 £15,793.20, C7 £5,021.24, C8 £7,914.07, C9 £7,134.34, C_IC1 £1,299,467.84, C_IC2 £764,895.23, C_IC3 £2,828,439.92, C_IC4 £1,074,640.43
- Bill shock events (>=20%): 71 -- C7 2022-01-31 (52%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C2g 2022-04-30 (64%); C2g 2022-05-31 (36%); C2g 2022-06-30 (30%); C2g 2022-09-30 (58%); C2g 2022-11-30 (54%); C2g 2022-12-31 (61%); C6 2022-04-30 (43%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (31%); C4 2022-09-30 (28%); C4 2022-10-31 (61%); C4 2022-11-30 (35%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (109%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C1_2 2022-01-31 (141%); C1_2 2022-02-28 (28%); C1_2 2022-04-30 (23%); C1_2 2022-05-31 (43%); C1_2 2022-06-30 (34%); C1_2 2022-09-30 (51%); C1_2 2022-11-30 (79%); C1_2 2022-12-31 (61%)
- Churn risk (accounts renewing in 2022): 11 at risk (≥20% churn prob): C1_2 41%, C2 38%, C4 38%, C6 35%, C7 29%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.96-£333.14/MWh, net margin £184.51
- C2 (electricity): tariff £143.79-£457.50/MWh, net margin £2.28
- C2g (gas): tariff £35.00-£95.00/MWh, net margin £-102.36 -- **net-negative**
- C4 (electricity): tariff £143.79-£457.50/MWh, net margin £-273.13 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,156.74 -- **net-negative**
- C6 (electricity): tariff £197.10-£412.09/MWh, net margin £1,141.20
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,632.87 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £73.71
- C9 (electricity): tariff £138.51-£389.58/MWh, net margin £110.68
- C_IC1 (electricity): tariff £-83.39-£463.03/MWh, net margin £136,500.23
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £75,781.66
- C_IC3 (electricity): tariff £146.89-£391.32/MWh, net margin £111,799.38
- C_IC3g (gas): tariff £116.42-£125.61/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £5,919.38

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 2 -- £3,470,998.09 -> £3,053,136.14 (12.0%); £3,471,176.38 -> £3,052,590.34 (12.1%)
- Bills issued: 168, average clarity 0.791, average bill shock 23.0%, bad debt provision £71.82, avg complaint probability 5.6%
- Solvency signal: £287,423/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £184,629.73 vs. naked (unhedged) net margin: £1,207,112.18
- hedging cost £1,022,482.44 vs. a fully unhedged book (commodity-only: actual net £184,629.73 vs. naked net £1,207,112.18)
  - C1_2: actual £-584.36 vs. naked £1,300.27 -- hedging cost £1,884.63
  - C2: actual £-191.17 vs. naked £524.01 -- hedging cost £715.18
  - C2g: actual £-258.54 vs. naked £262.02 -- hedging cost £520.56
  - C4: actual £-292.88 vs. naked £597.69 -- hedging cost £890.57
  - C4g: actual £-2,028.81 vs. naked £1,336.80 -- hedging cost £3,365.60
  - C6: actual £1,245.22 vs. naked £4,116.60 -- hedging cost £2,871.37
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-481.87 vs. naked £1,102.92 -- hedging cost £1,584.78
  - C9: actual £-49.07 vs. naked £1,012.53 -- hedging cost £1,061.60
  - C_IC1: actual £212,837.07 vs. naked £251,120.17 -- hedging cost £38,283.10
  - C_IC2: actual £87,095.73 vs. naked £126,396.62 -- hedging cost £39,300.89
  - C_IC3: actual £-124,202.28 vs. naked £488,702.92 -- hedging cost £612,905.20
  - C_IC3g: actual £8,513.79 vs. naked £123,301.26 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £205,056.67 -- hedging cost £201,583.86

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £338,347.87 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 71 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £144,376.85 (gross £955,881.82, capital £10,036.50)
  - Electricity: gross £834,588.49, capital £9,961.08, net £135,353.30
  - Gas: gross £121,293.34, capital £75.41, net £9,023.55
- Treasury at year end: £3,382,228.73
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.91 (avg 0.91), C2 0.95 (avg 0.95), C2g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,137,514.98, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-02-23: treasury £3,137,498.06, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-03-25: treasury £3,137,481.31, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-04-24: treasury £3,217,144.83, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,230.41 / stressed £48,907.75) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C6 on 2023-12-31 period 48, net margin £-2,032.26

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2023): £363,185.43
  - By billing account: C1 £3,680.74, C1_2 £1,944.13, C2 £4,982.25, C3 £4,440.04, C4 £2,107.60, C5 £7,623.31, C6 £17,306.38, C7 £5,356.78, C8 £7,277.99, C9 £6,952.69, C_IC1 £1,320,738.65, C_IC2 £640,507.44, C_IC3 £1,892,395.24, C_IC4 £1,169,282.75
- Bill shock events (>=20%): 49 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C2 2023-04-30 (28%); C2g 2023-04-30 (34%); C2g 2023-05-31 (38%); C2g 2023-06-30 (37%); C2g 2023-10-31 (85%); C2g 2023-11-30 (56%); C6 2023-04-30 (31%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (26%); C4 2023-04-30 (32%); C4 2023-09-30 (26%); C4 2023-11-30 (29%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (44%); C4g 2023-11-30 (63%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (100%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%); C1_2 2023-05-31 (38%); C1_2 2023-06-30 (43%); C1_2 2023-10-31 (73%); C1_2 2023-11-30 (83%)
- Churn risk (accounts renewing in 2023): 10 at risk (≥20% churn prob): C2 41%, C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.96-£267.80/MWh, net margin £-439.82 -- **net-negative**
- C2 (electricity): tariff £208.21-£457.50/MWh, net margin £88.59
- C2g (gas): tariff £70.00-£95.00/MWh, net margin £136.46
- C4 (electricity): tariff £198.37-£457.50/MWh, net margin £-11.67 -- **net-negative**
- C4g (gas): tariff £64.73-£95.00/MWh, net margin £-1,112.83 -- **net-negative**
- C6 (electricity): tariff £338.13-£412.09/MWh, net margin £-652.18 -- **net-negative**
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-144.77 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £159.02
- C9 (electricity): tariff £192.59-£389.58/MWh, net margin £396.72
- C_IC1 (electricity): tariff £-60.00-£463.03/MWh, net margin £162,662.79
- C_IC2 (electricity): tariff £-186.24-£476.36/MWh, net margin £85,767.63
- C_IC3 (electricity): tariff £95.69-£280.44/MWh, net margin £-118,400.86 -- **net-negative**
- C_IC3g (gas): tariff £55.87-£116.42/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £5,927.85

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): 47 -- £3,768,563.48 -> £3,382,154.13 (10.3%); £3,768,563.63 -> £3,382,154.13 (10.3%); £3,768,563.78 -> £3,382,154.12 (10.3%); £3,768,563.93 -> £3,382,154.12 (10.3%); £3,768,564.09 -> £3,382,154.12 (10.3%); £3,768,564.24 -> £3,382,154.12 (10.3%); £3,768,564.39 -> £3,382,154.12 (10.3%); £3,768,564.55 -> £3,382,154.12 (10.3%); £3,768,564.70 -> £3,382,154.12 (10.3%); £3,768,564.86 -> £3,382,154.12 (10.3%); £3,768,565.02 -> £3,382,154.12 (10.3%); £3,768,565.17 -> £3,382,154.12 (10.3%); £3,768,565.33 -> £3,382,154.11 (10.3%); £3,768,565.50 -> £3,382,154.11 (10.3%); £3,768,565.69 -> £3,382,154.10 (10.3%); £3,768,565.90 -> £3,382,154.10 (10.3%); £3,768,566.12 -> £3,382,154.09 (10.3%); £3,768,566.36 -> £3,382,154.08 (10.3%); £3,768,566.63 -> £3,382,154.06 (10.3%); £3,768,566.88 -> £3,382,154.05 (10.3%); £3,768,567.14 -> £3,382,154.04 (10.3%); £3,768,567.39 -> £3,382,154.03 (10.3%); £3,768,567.66 -> £3,382,154.01 (10.3%); £3,768,567.92 -> £3,382,154.00 (10.3%); £3,768,568.18 -> £3,382,153.99 (10.3%); £3,768,568.45 -> £3,382,153.97 (10.3%); £3,768,568.72 -> £3,382,153.96 (10.3%); £3,768,568.97 -> £3,382,153.95 (10.3%); £3,768,569.23 -> £3,382,153.94 (10.3%); £3,768,569.48 -> £3,382,153.93 (10.3%); £3,768,569.74 -> £3,382,153.93 (10.3%); £3,768,569.99 -> £3,382,153.92 (10.3%); £3,768,570.26 -> £3,382,153.90 (10.3%); £3,768,570.51 -> £3,382,153.88 (10.3%); £3,768,570.77 -> £3,382,153.86 (10.3%); £3,768,571.03 -> £3,382,153.84 (10.3%); £3,768,571.29 -> £3,382,153.81 (10.3%); £3,768,571.55 -> £3,382,153.78 (10.3%); £3,768,571.82 -> £3,382,153.75 (10.3%); £3,768,572.08 -> £3,382,153.72 (10.3%); £3,768,572.34 -> £3,382,153.69 (10.3%); £3,768,572.60 -> £3,382,153.66 (10.3%); £3,768,572.86 -> £3,382,153.64 (10.3%); £3,768,573.12 -> £3,382,153.63 (10.3%); £3,768,573.38 -> £3,382,153.62 (10.3%); £3,768,573.62 -> £3,382,153.61 (10.3%); £3,768,573.84 -> £3,381,512.62 (10.3%)
- Bills issued: 168, average clarity 0.811, average bill shock 17.5%, bad debt provision £2,192.68, avg complaint probability 4.9%
- Solvency signal: £307,475/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £380,391.26 vs. naked (unhedged) net margin: £1,219,610.31
- hedging cost £839,219.05 vs. a fully unhedged book (commodity-only: actual net £380,391.26 vs. naked net £1,219,610.31)
  - C1_2: actual £680.54 vs. naked £1,720.09 -- hedging cost £1,039.55
  - C2: actual £106.23 vs. naked £797.97 -- hedging cost £691.74
  - C2g: actual £206.68 vs. naked £669.84 -- hedging cost £463.16
  - C4: actual £310.61 vs. naked £704.57 -- hedging cost £393.96
  - C4g: actual £496.10 vs. naked £1,014.26 -- hedging cost £518.15
  - C6: actual £1,521.80 vs. naked £5,191.47 -- hedging cost £3,669.67
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £140.61 vs. naked £1,972.23 -- hedging cost £1,831.62
  - C9: actual £626.21 vs. naked £2,129.86 -- hedging cost £1,503.65
  - C_IC1: actual £141,611.78 vs. naked £284,485.88 -- hedging cost £142,874.09
  - C_IC2: actual £93,826.81 vs. naked £161,876.12 -- hedging cost £68,049.31
  - C_IC3: actual £128,018.29 vs. naked £401,823.63 -- hedging cost £273,805.34
  - C_IC3g: actual £8,660.26 vs. naked £123,107.25 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £232,127.67 -- hedging cost £228,435.92

**Year narrative:** 2023 produced a net gain of £144,376.85 across 14 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 49 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £347,815.39 (gross £1,257,805.74, capital £9,522.03)
  - Electricity: gross £1,132,855.54, capital £9,477.19, net £337,106.50
  - Gas: gross £124,950.20, capital £44.84, net £10,708.88
- Treasury at year end: £3,774,871.00
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.87 (avg 0.87), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C4 on 2024-09-28 period 48, net margin £-121.57

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £348,560.03
  - By billing account: C1 £3,291.89, C1_2 £2,675.04, C2 £4,369.83, C3 £4,033.43, C4 £2,598.16, C5 £7,834.04, C6 £15,341.31, C7 £4,975.97, C8 £7,062.48, C9 £7,097.09, C_IC1 £1,156,263.05, C_IC2 £680,833.29, C_IC3 £2,019,730.99, C_IC4 £963,733.92
- Bill shock events (>=20%): 41 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C2 2024-04-30 (32%); C2g 2024-02-29 (23%); C2g 2024-04-30 (35%); C2g 2024-05-31 (44%); C2g 2024-07-31 (22%); C2g 2024-09-30 (45%); C2g 2024-10-31 (31%); C2g 2024-11-30 (48%); C8 2024-02-29 (23%); C8 2024-04-30 (34%); C8 2024-05-31 (47%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (31%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C1_2 2024-01-31 (21%); C1_2 2024-02-29 (28%); C1_2 2024-04-30 (23%); C1_2 2024-05-31 (44%); C1_2 2024-09-30 (51%); C1_2 2024-10-31 (45%); C1_2 2024-11-30 (57%)
- Churn risk (accounts renewing in 2024): 8 at risk (≥20% churn prob): C2 41%, C4 38%, C6 26%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC3 41%, C_IC4 20%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01-£267.80/MWh, net margin £760.69
- C2 (electricity): tariff £157.80-£397.50/MWh, net margin £210.04
- C2g (gas): tariff £48.30-£70.00/MWh, net margin £265.39
- C4 (electricity): tariff £198.37-£378.70/MWh, net margin £105.69
- C4g (gas): tariff £64.73/MWh, net margin £412.73
- C6 (electricity): tariff £338.13/MWh, net margin £817.61
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £635.74
- C8 (electricity): tariff £159.61-£397.50/MWh, net margin £404.66
- C9 (electricity): tariff £165.00-£367.66/MWh, net margin £656.09
- C_IC1 (electricity): tariff £-98.58-£330.71/MWh, net margin £125,749.68
- C_IC2 (electricity): tariff £-106.92-£354.54/MWh, net margin £69,822.45
- C_IC3 (electricity): tariff £88.52-£182.68/MWh, net margin £131,992.56
- C_IC3g (gas): tariff £48.21-£55.87/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £5,951.30

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): 4271 -- £3,771,021.83 -> £3,381,512.69 (10.3%); £3,771,022.00 -> £3,381,512.73 (10.3%); £3,771,022.17 -> £3,381,512.76 (10.3%); £3,771,022.35 -> £3,381,512.80 (10.3%); £3,771,022.52 -> £3,381,512.84 (10.3%); £3,771,022.69 -> £3,381,512.87 (10.3%); £3,771,022.87 -> £3,381,512.91 (10.3%); £3,771,023.04 -> £3,381,512.95 (10.3%); £3,771,023.21 -> £3,381,512.98 (10.3%); £3,771,023.39 -> £3,381,513.02 (10.3%); £3,771,023.56 -> £3,381,513.06 (10.3%); £3,771,023.74 -> £3,381,513.24 (10.3%); £3,771,023.90 -> £3,381,513.42 (10.3%); £3,771,024.10 -> £3,381,513.62 (10.3%); £3,771,024.30 -> £3,381,513.83 (10.3%); £3,771,024.53 -> £3,381,514.07 (10.3%); £3,771,024.77 -> £3,381,514.32 (10.3%); £3,771,025.03 -> £3,381,514.60 (10.3%); £3,771,025.32 -> £3,381,514.88 (10.3%); £3,771,025.59 -> £3,381,515.00 (10.3%); £3,771,025.89 -> £3,381,515.13 (10.3%); £3,771,026.18 -> £3,381,515.25 (10.3%); £3,771,026.48 -> £3,381,515.38 (10.3%); £3,771,026.76 -> £3,381,515.50 (10.3%); £3,771,027.05 -> £3,381,515.63 (10.3%); £3,771,027.34 -> £3,381,515.75 (10.3%); £3,771,027.62 -> £3,381,515.86 (10.3%); £3,771,027.90 -> £3,381,515.97 (10.3%); £3,771,028.17 -> £3,381,516.08 (10.3%); £3,771,028.45 -> £3,381,516.20 (10.3%); £3,771,028.74 -> £3,381,516.32 (10.3%); £3,771,029.03 -> £3,381,516.43 (10.3%); £3,771,029.31 -> £3,381,516.72 (10.3%); £3,771,029.59 -> £3,381,516.97 (10.3%); £3,771,029.81 -> £3,381,517.20 (10.3%); £3,771,030.03 -> £3,381,517.41 (10.3%); £3,771,030.25 -> £3,381,517.63 (10.3%); £3,771,030.55 -> £3,381,517.83 (10.3%); £3,771,030.84 -> £3,381,518.04 (10.3%); £3,771,031.12 -> £3,381,518.25 (10.3%); £3,771,031.41 -> £3,381,518.45 (10.3%); £3,771,031.69 -> £3,381,518.64 (10.3%); £3,771,031.99 -> £3,381,518.83 (10.3%); £3,771,032.28 -> £3,381,518.88 (10.3%); £3,771,032.57 -> £3,381,518.92 (10.3%); £3,771,032.83 -> £3,381,518.96 (10.3%); £3,771,033.07 -> £3,381,519.00 (10.3%); £3,771,033.29 -> £3,381,519.04 (10.3%); £3,771,033.47 -> £3,381,519.08 (10.3%); £3,771,033.64 -> £3,381,519.12 (10.3%); £3,771,033.81 -> £3,381,519.16 (10.3%); £3,771,033.97 -> £3,381,519.20 (10.3%); £3,771,034.14 -> £3,381,519.24 (10.3%); £3,771,034.31 -> £3,381,519.28 (10.3%); £3,771,034.49 -> £3,381,519.32 (10.3%); £3,771,034.66 -> £3,381,519.36 (10.3%); £3,771,034.83 -> £3,381,519.40 (10.3%); £3,771,035.00 -> £3,381,519.44 (10.3%); £3,771,035.17 -> £3,381,519.48 (10.3%); £3,771,035.34 -> £3,381,519.64 (10.3%); £3,771,035.51 -> £3,381,519.81 (10.3%); £3,771,035.69 -> £3,381,519.98 (10.3%); £3,771,035.90 -> £3,381,520.17 (10.3%); £3,771,036.12 -> £3,381,520.39 (10.3%); £3,771,036.36 -> £3,381,520.62 (10.3%); £3,771,036.61 -> £3,381,520.89 (10.3%); £3,771,036.89 -> £3,381,521.16 (10.3%); £3,771,037.17 -> £3,381,521.30 (10.3%); £3,771,037.45 -> £3,381,521.42 (10.3%); £3,771,037.73 -> £3,381,521.54 (10.3%); £3,771,038.02 -> £3,381,521.68 (10.3%); £3,771,038.29 -> £3,381,521.81 (10.3%); £3,771,038.57 -> £3,381,521.92 (10.3%); £3,771,038.85 -> £3,381,522.04 (10.3%); £3,771,039.13 -> £3,381,522.16 (10.3%); £3,771,039.41 -> £3,381,522.27 (10.3%); £3,771,039.68 -> £3,381,522.38 (10.3%); £3,771,039.96 -> £3,381,522.49 (10.3%); £3,771,040.23 -> £3,381,522.60 (10.3%); £3,771,040.51 -> £3,381,522.71 (10.3%); £3,771,040.72 -> £3,381,522.95 (10.3%); £3,771,040.94 -> £3,381,523.18 (10.3%); £3,771,041.15 -> £3,381,523.38 (10.3%); £3,771,041.36 -> £3,381,523.56 (10.3%); £3,771,041.58 -> £3,381,523.73 (10.3%); £3,771,041.79 -> £3,381,523.90 (10.3%); £3,771,042.00 -> £3,381,524.06 (10.3%); £3,771,042.28 -> £3,381,524.22 (10.3%); £3,771,042.57 -> £3,381,524.39 (10.3%); £3,771,042.84 -> £3,381,524.55 (10.3%); £3,771,043.13 -> £3,381,524.71 (10.3%); £3,771,043.41 -> £3,381,524.75 (10.3%); £3,771,043.69 -> £3,381,524.79 (10.3%); £3,771,043.96 -> £3,381,524.83 (10.3%); £3,771,044.19 -> £3,381,524.87 (10.3%); £3,771,044.41 -> £3,381,524.90 (10.3%); £3,771,044.58 -> £3,381,524.94 (10.3%); £3,771,044.75 -> £3,381,524.98 (10.3%); £3,771,044.92 -> £3,381,525.01 (10.3%); £3,771,045.09 -> £3,381,525.05 (10.3%); £3,771,045.26 -> £3,381,525.09 (10.3%); £3,771,045.43 -> £3,381,525.12 (10.3%); £3,771,045.60 -> £3,381,525.16 (10.3%); £3,771,045.76 -> £3,381,525.20 (10.3%); £3,771,045.93 -> £3,381,525.24 (10.3%); £3,771,046.10 -> £3,381,525.27 (10.3%); £3,771,046.27 -> £3,381,525.32 (10.3%); £3,771,046.45 -> £3,381,525.50 (10.3%); £3,771,046.62 -> £3,381,525.69 (10.3%); £3,771,046.80 -> £3,381,525.89 (10.3%); £3,771,047.01 -> £3,381,526.11 (10.3%); £3,771,047.24 -> £3,381,526.35 (10.3%); £3,771,047.48 -> £3,381,526.59 (10.3%); £3,771,047.75 -> £3,381,526.85 (10.3%); £3,771,048.03 -> £3,381,527.12 (10.3%); £3,771,048.31 -> £3,381,527.24 (10.3%); £3,771,048.59 -> £3,381,527.36 (10.3%); £3,771,048.87 -> £3,381,527.49 (10.3%); £3,771,049.16 -> £3,381,527.61 (10.3%); £3,771,049.45 -> £3,381,527.73 (10.3%); £3,771,049.74 -> £3,381,527.85 (10.3%); £3,771,050.03 -> £3,381,527.96 (10.3%); £3,771,050.31 -> £3,381,528.08 (10.3%); £3,771,050.59 -> £3,381,528.20 (10.3%); £3,771,050.87 -> £3,381,528.32 (10.3%); £3,771,051.16 -> £3,381,528.43 (10.3%); £3,771,051.43 -> £3,381,528.55 (10.3%); £3,771,051.71 -> £3,381,528.66 (10.3%); £3,771,051.99 -> £3,381,528.92 (10.3%); £3,771,052.21 -> £3,381,529.19 (10.3%); £3,771,052.49 -> £3,381,529.41 (10.3%); £3,771,052.70 -> £3,381,529.61 (10.3%); £3,771,052.91 -> £3,381,529.80 (10.3%); £3,771,053.12 -> £3,381,529.98 (10.3%); £3,771,053.34 -> £3,381,530.18 (10.3%); £3,771,053.61 -> £3,381,530.37 (10.3%); £3,771,053.89 -> £3,381,530.56 (10.3%); £3,771,054.18 -> £3,381,530.74 (10.3%); £3,771,054.45 -> £3,381,530.91 (10.3%); £3,771,054.74 -> £3,381,530.95 (10.3%); £3,771,055.03 -> £3,381,530.99 (10.3%); £3,771,055.28 -> £3,381,531.03 (10.3%); £3,771,055.52 -> £3,381,531.06 (10.3%); £3,771,055.74 -> £3,381,531.10 (10.3%); £3,771,055.90 -> £3,381,531.14 (10.3%); £3,771,056.07 -> £3,381,531.18 (10.3%); £3,771,056.23 -> £3,381,531.22 (10.3%); £3,771,056.40 -> £3,381,531.25 (10.3%); £3,771,056.57 -> £3,381,531.29 (10.3%); £3,771,056.74 -> £3,381,531.33 (10.3%); £3,771,056.91 -> £3,381,531.37 (10.3%); £3,771,057.07 -> £3,381,531.41 (10.3%); £3,771,057.24 -> £3,381,531.45 (10.3%); £3,771,057.41 -> £3,381,531.48 (10.3%); £3,771,057.58 -> £3,381,531.52 (10.3%); £3,771,057.75 -> £3,381,531.73 (10.3%); £3,771,057.92 -> £3,381,531.94 (10.3%); £3,771,058.11 -> £3,381,532.16 (10.3%); £3,771,058.31 -> £3,381,532.39 (10.3%); £3,771,058.53 -> £3,381,532.63 (10.3%); £3,771,058.77 -> £3,381,532.91 (10.3%); £3,771,059.03 -> £3,381,533.21 (10.3%); £3,771,059.31 -> £3,381,533.52 (10.3%); £3,771,059.58 -> £3,381,533.65 (10.3%); £3,771,059.87 -> £3,381,533.77 (10.3%); £3,771,060.14 -> £3,381,533.90 (10.3%); £3,771,060.42 -> £3,381,534.03 (10.3%); £3,771,060.70 -> £3,381,534.15 (10.3%); £3,771,060.97 -> £3,381,534.27 (10.3%); £3,771,061.25 -> £3,381,534.38 (10.3%); £3,771,061.53 -> £3,381,534.49 (10.3%); £3,771,061.81 -> £3,381,534.60 (10.3%); £3,771,062.08 -> £3,381,534.72 (10.3%); £3,771,062.36 -> £3,381,534.83 (10.3%); £3,771,062.64 -> £3,381,534.94 (10.3%); £3,771,062.92 -> £3,381,535.04 (10.3%); £3,771,063.13 -> £3,381,535.34 (10.3%); £3,771,063.40 -> £3,381,535.62 (10.3%); £3,771,063.68 -> £3,381,535.85 (10.3%); £3,771,063.88 -> £3,381,536.07 (10.3%); £3,771,064.15 -> £3,381,536.29 (10.3%); £3,771,064.43 -> £3,381,536.49 (10.3%); £3,771,064.65 -> £3,381,536.69 (10.3%); £3,771,064.93 -> £3,381,536.89 (10.3%); £3,771,065.20 -> £3,381,537.09 (10.3%); £3,771,065.49 -> £3,381,537.28 (10.3%); £3,771,065.76 -> £3,381,537.48 (10.3%); £3,771,066.05 -> £3,381,537.52 (10.3%); £3,771,066.32 -> £3,381,537.56 (10.3%); £3,771,066.57 -> £3,381,537.60 (10.3%); £3,771,066.81 -> £3,381,537.63 (10.3%); £3,771,067.03 -> £3,381,537.67 (10.3%); £3,771,067.19 -> £3,381,537.71 (10.3%); £3,771,067.35 -> £3,381,537.74 (10.3%); £3,771,067.51 -> £3,381,537.78 (10.3%); £3,771,067.67 -> £3,381,537.82 (10.3%); £3,771,067.83 -> £3,381,537.86 (10.3%); £3,771,067.99 -> £3,381,537.89 (10.3%); £3,771,068.16 -> £3,381,537.93 (10.3%); £3,771,068.31 -> £3,381,537.97 (10.3%); £3,771,068.48 -> £3,381,538.01 (10.3%); £3,771,068.65 -> £3,381,538.05 (10.3%); £3,771,068.81 -> £3,381,538.09 (10.3%); £3,771,068.97 -> £3,381,538.31 (10.3%); £3,771,069.13 -> £3,381,538.52 (10.3%); £3,771,069.31 -> £3,381,538.77 (10.3%); £3,771,069.51 -> £3,381,539.02 (10.3%); £3,771,069.72 -> £3,381,539.29 (10.3%); £3,771,069.95 -> £3,381,539.57 (10.3%); £3,771,070.21 -> £3,381,539.87 (10.3%); £3,771,070.48 -> £3,381,540.18 (10.3%); £3,771,070.76 -> £3,381,540.30 (10.3%); £3,771,071.02 -> £3,381,540.43 (10.3%); £3,771,071.29 -> £3,381,540.55 (10.3%); £3,771,071.56 -> £3,381,540.68 (10.3%); £3,771,071.83 -> £3,381,540.81 (10.3%); £3,771,072.10 -> £3,381,540.93 (10.3%); £3,771,072.38 -> £3,381,541.05 (10.3%); £3,771,072.65 -> £3,381,541.17 (10.3%); £3,771,072.91 -> £3,381,541.28 (10.3%); £3,771,073.17 -> £3,381,541.40 (10.3%); £3,771,073.44 -> £3,381,541.51 (10.3%); £3,771,073.70 -> £3,381,541.62 (10.3%); £3,771,073.98 -> £3,381,541.72 (10.3%); £3,771,074.18 -> £3,381,542.02 (10.3%); £3,771,074.38 -> £3,381,542.29 (10.3%); £3,771,074.59 -> £3,381,542.55 (10.3%); £3,771,074.79 -> £3,381,542.79 (10.3%); £3,771,075.06 -> £3,381,543.01 (10.3%); £3,771,075.26 -> £3,381,543.23 (10.3%); £3,771,075.46 -> £3,381,543.45 (10.3%); £3,771,075.73 -> £3,381,543.66 (10.3%); £3,771,076.00 -> £3,381,543.87 (10.3%); £3,771,076.26 -> £3,381,544.09 (10.3%); £3,771,076.53 -> £3,381,544.30 (10.3%); £3,771,076.79 -> £3,381,544.34 (10.3%); £3,771,077.06 -> £3,381,544.38 (10.3%); £3,771,077.32 -> £3,381,544.42 (10.3%); £3,771,077.55 -> £3,381,544.46 (10.3%); £3,771,077.76 -> £3,381,544.50 (10.3%); £3,771,077.90 -> £3,381,544.53 (10.3%); £3,771,078.05 -> £3,381,544.57 (10.3%); £3,771,078.19 -> £3,381,544.61 (10.3%); £3,771,078.34 -> £3,381,544.65 (10.3%); £3,771,078.48 -> £3,381,544.69 (10.3%); £3,771,078.63 -> £3,381,544.72 (10.3%); £3,771,078.76 -> £3,381,544.76 (10.3%); £3,771,078.90 -> £3,381,544.80 (10.3%); £3,771,079.04 -> £3,381,544.83 (10.3%); £3,771,079.18 -> £3,381,544.87 (10.3%); £3,771,079.32 -> £3,381,544.91 (10.3%); £3,771,079.46 -> £3,381,545.17 (10.3%); £3,771,079.60 -> £3,381,545.42 (10.3%); £3,771,079.76 -> £3,381,545.69 (10.3%); £3,771,079.93 -> £3,381,545.96 (10.3%); £3,771,080.12 -> £3,381,546.23 (10.3%); £3,771,080.33 -> £3,381,546.52 (10.3%); £3,771,080.54 -> £3,381,546.84 (10.3%); £3,771,080.78 -> £3,381,547.16 (10.3%); £3,771,081.01 -> £3,381,547.25 (10.3%); £3,771,081.25 -> £3,381,547.33 (10.3%); £3,771,081.48 -> £3,381,547.42 (10.3%); £3,771,081.72 -> £3,381,547.51 (10.3%); £3,771,081.95 -> £3,381,547.59 (10.3%); £3,771,082.19 -> £3,381,547.67 (10.3%); £3,771,082.42 -> £3,381,547.74 (10.3%); £3,771,082.67 -> £3,381,547.82 (10.3%); £3,771,082.91 -> £3,381,547.88 (10.3%); £3,771,083.15 -> £3,381,547.95 (10.3%); £3,771,083.39 -> £3,381,548.02 (10.3%); £3,771,083.62 -> £3,381,548.08 (10.3%); £3,771,083.87 -> £3,381,548.15 (10.3%); £3,771,084.09 -> £3,381,548.42 (10.3%); £3,771,084.26 -> £3,381,548.68 (10.3%); £3,771,084.44 -> £3,381,548.94 (10.3%); £3,771,084.61 -> £3,381,549.18 (10.3%); £3,771,084.79 -> £3,381,549.43 (10.3%); £3,771,084.97 -> £3,381,549.67 (10.3%); £3,771,085.15 -> £3,381,549.93 (10.3%); £3,771,085.38 -> £3,381,550.18 (10.3%); £3,771,085.61 -> £3,381,550.43 (10.3%); £3,771,085.84 -> £3,381,550.67 (10.3%); £3,771,086.08 -> £3,381,550.92 (10.3%); £3,771,086.31 -> £3,381,550.96 (10.3%); £3,771,086.54 -> £3,381,551.00 (10.3%); £3,771,086.76 -> £3,381,551.04 (10.3%); £3,771,086.96 -> £3,381,551.08 (10.3%); £3,771,087.14 -> £3,381,551.12 (10.3%); £3,771,087.28 -> £3,381,551.15 (10.3%); £3,771,087.42 -> £3,381,551.19 (10.3%); £3,771,087.57 -> £3,381,551.23 (10.3%); £3,771,087.71 -> £3,381,551.27 (10.3%); £3,771,087.84 -> £3,381,551.30 (10.3%); £3,771,087.98 -> £3,381,551.34 (10.3%); £3,771,088.12 -> £3,381,551.37 (10.3%); £3,771,088.27 -> £3,381,551.41 (10.3%); £3,771,088.40 -> £3,381,551.45 (10.3%); £3,771,088.54 -> £3,381,551.48 (10.3%); £3,771,088.68 -> £3,381,551.52 (10.3%); £3,771,088.82 -> £3,381,551.77 (10.3%); £3,771,088.96 -> £3,381,552.01 (10.3%); £3,771,089.11 -> £3,381,552.26 (10.3%); £3,771,089.29 -> £3,381,552.50 (10.3%); £3,771,089.48 -> £3,381,552.75 (10.3%); £3,771,089.68 -> £3,381,553.00 (10.3%); £3,771,089.90 -> £3,381,553.24 (10.3%); £3,771,090.13 -> £3,381,553.49 (10.3%); £3,771,090.38 -> £3,381,553.54 (10.3%); £3,771,090.60 -> £3,381,553.58 (10.3%); £3,771,090.83 -> £3,381,553.63 (10.3%); £3,771,091.06 -> £3,381,553.68 (10.3%); £3,771,091.29 -> £3,381,553.73 (10.3%); £3,771,091.52 -> £3,381,553.78 (10.3%); £3,771,091.75 -> £3,381,553.82 (10.3%); £3,771,091.98 -> £3,381,553.86 (10.3%); £3,771,092.21 -> £3,381,553.91 (10.3%); £3,771,092.45 -> £3,381,553.96 (10.3%); £3,771,092.68 -> £3,381,554.00 (10.3%); £3,771,092.91 -> £3,381,554.04 (10.3%); £3,771,093.14 -> £3,381,554.09 (10.3%); £3,771,093.32 -> £3,381,554.32 (10.3%); £3,771,093.49 -> £3,381,554.55 (10.3%); £3,771,093.66 -> £3,381,554.79 (10.3%); £3,771,093.83 -> £3,381,555.04 (10.3%); £3,771,094.07 -> £3,381,555.28 (10.3%); £3,771,094.25 -> £3,381,555.51 (10.3%); £3,771,094.42 -> £3,381,555.76 (10.3%); £3,771,094.66 -> £3,381,556.01 (10.3%); £3,771,094.89 -> £3,381,556.25 (10.3%); £3,771,095.13 -> £3,381,556.48 (10.3%); £3,771,095.36 -> £3,381,556.72 (10.3%); £3,771,095.58 -> £3,381,556.76 (10.3%); £3,771,095.82 -> £3,381,556.80 (10.3%); £3,771,096.03 -> £3,381,556.84 (10.3%); £3,771,096.23 -> £3,381,556.87 (10.3%); £3,771,096.42 -> £3,381,556.91 (10.3%); £3,771,096.58 -> £3,381,556.95 (10.3%); £3,771,096.73 -> £3,381,556.98 (10.3%); £3,771,096.88 -> £3,381,557.02 (10.3%); £3,771,097.03 -> £3,381,557.06 (10.3%); £3,771,097.18 -> £3,381,557.10 (10.3%); £3,771,097.34 -> £3,381,557.13 (10.3%); £3,771,097.49 -> £3,381,557.17 (10.3%); £3,771,097.65 -> £3,381,557.21 (10.3%); £3,771,097.80 -> £3,381,557.25 (10.3%); £3,771,097.96 -> £3,381,557.28 (10.3%); £3,771,098.11 -> £3,381,557.33 (10.3%); £3,771,098.26 -> £3,381,557.56 (10.3%); £3,771,098.42 -> £3,381,557.82 (10.3%); £3,771,098.59 -> £3,381,558.08 (10.3%); £3,771,098.77 -> £3,381,558.34 (10.3%); £3,771,098.98 -> £3,381,558.64 (10.3%); £3,771,099.20 -> £3,381,558.96 (10.3%); £3,771,099.43 -> £3,381,559.30 (10.3%); £3,771,099.68 -> £3,381,559.66 (10.3%); £3,771,099.93 -> £3,381,559.77 (10.3%); £3,771,100.18 -> £3,381,559.89 (10.3%); £3,771,100.45 -> £3,381,560.01 (10.3%); £3,771,100.69 -> £3,381,560.14 (10.3%); £3,771,100.95 -> £3,381,560.26 (10.3%); £3,771,101.21 -> £3,381,560.37 (10.3%); £3,771,101.47 -> £3,381,560.49 (10.3%); £3,771,101.74 -> £3,381,560.61 (10.3%); £3,771,101.99 -> £3,381,560.72 (10.3%); £3,771,102.24 -> £3,381,560.83 (10.3%); £3,771,102.51 -> £3,381,560.94 (10.3%); £3,771,102.76 -> £3,381,561.05 (10.3%); £3,771,103.02 -> £3,381,561.16 (10.3%); £3,771,103.29 -> £3,381,561.50 (10.3%); £3,771,103.55 -> £3,381,561.82 (10.3%); £3,771,103.80 -> £3,381,562.11 (10.3%); £3,771,104.05 -> £3,381,562.38 (10.3%); £3,771,104.30 -> £3,381,562.65 (10.3%); £3,771,104.55 -> £3,381,562.90 (10.3%); £3,771,104.74 -> £3,381,563.15 (10.3%); £3,771,104.99 -> £3,381,563.40 (10.3%); £3,771,105.24 -> £3,381,563.65 (10.3%); £3,771,105.49 -> £3,381,563.89 (10.3%); £3,771,105.75 -> £3,381,564.13 (10.3%); £3,771,106.00 -> £3,381,564.17 (10.3%); £3,771,106.26 -> £3,381,564.22 (10.3%); £3,771,106.49 -> £3,381,564.26 (10.3%); £3,771,106.71 -> £3,381,564.29 (10.3%); £3,771,106.91 -> £3,381,564.33 (10.3%); £3,771,107.06 -> £3,381,564.37 (10.3%); £3,771,107.22 -> £3,381,564.41 (10.3%); £3,771,107.37 -> £3,381,564.44 (10.3%); £3,771,107.52 -> £3,381,564.48 (10.3%); £3,771,107.68 -> £3,381,564.52 (10.3%); £3,771,107.83 -> £3,381,564.56 (10.3%); £3,771,107.98 -> £3,381,564.59 (10.3%); £3,771,108.13 -> £3,381,564.63 (10.3%); £3,771,108.29 -> £3,381,564.67 (10.3%); £3,771,108.44 -> £3,381,564.71 (10.3%); £3,771,108.59 -> £3,381,564.75 (10.3%); £3,771,108.75 -> £3,381,564.99 (10.3%); £3,771,108.90 -> £3,381,565.24 (10.3%); £3,771,109.06 -> £3,381,565.50 (10.3%); £3,771,109.24 -> £3,381,565.77 (10.3%); £3,771,109.45 -> £3,381,566.06 (10.3%); £3,771,109.67 -> £3,381,566.37 (10.3%); £3,771,109.90 -> £3,381,566.71 (10.3%); £3,771,110.15 -> £3,381,567.06 (10.3%); £3,771,110.40 -> £3,381,567.18 (10.3%); £3,771,110.65 -> £3,381,567.31 (10.3%); £3,771,110.91 -> £3,381,567.44 (10.3%); £3,771,111.16 -> £3,381,567.57 (10.3%); £3,771,111.43 -> £3,381,567.70 (10.3%); £3,771,111.69 -> £3,381,567.82 (10.3%); £3,771,111.94 -> £3,381,567.94 (10.3%); £3,771,112.20 -> £3,381,568.05 (10.3%); £3,771,112.45 -> £3,381,568.17 (10.3%); £3,771,112.71 -> £3,381,568.29 (10.3%); £3,771,112.97 -> £3,381,568.40 (10.3%); £3,771,113.22 -> £3,381,568.51 (10.3%); £3,771,113.46 -> £3,381,568.62 (10.3%); £3,771,113.65 -> £3,381,568.93 (10.3%); £3,771,113.84 -> £3,381,569.25 (10.3%); £3,771,114.09 -> £3,381,569.52 (10.3%); £3,771,114.28 -> £3,381,569.77 (10.3%); £3,771,114.47 -> £3,381,570.03 (10.3%); £3,771,114.73 -> £3,381,570.28 (10.3%); £3,771,114.98 -> £3,381,570.53 (10.3%); £3,771,115.24 -> £3,381,570.78 (10.3%); £3,771,115.49 -> £3,381,571.02 (10.3%); £3,771,115.75 -> £3,381,571.25 (10.3%); £3,771,116.01 -> £3,381,571.49 (10.3%); £3,771,116.26 -> £3,381,571.53 (10.3%); £3,771,116.51 -> £3,381,571.57 (10.3%); £3,771,116.75 -> £3,381,571.61 (10.3%); £3,771,116.96 -> £3,381,571.65 (10.3%); £3,771,117.16 -> £3,381,571.68 (10.3%); £3,771,117.31 -> £3,381,571.72 (10.3%); £3,771,117.46 -> £3,381,571.76 (10.3%); £3,771,117.61 -> £3,381,571.80 (10.3%); £3,771,117.77 -> £3,381,571.83 (10.3%); £3,771,117.91 -> £3,381,571.87 (10.3%); £3,771,118.07 -> £3,381,571.91 (10.3%); £3,771,118.22 -> £3,381,571.95 (10.3%); £3,771,118.37 -> £3,381,571.98 (10.3%); £3,771,118.52 -> £3,381,572.02 (10.3%); £3,771,118.67 -> £3,381,572.06 (10.3%); £3,771,118.82 -> £3,381,572.10 (10.3%); £3,771,118.97 -> £3,381,572.32 (10.3%); £3,771,119.13 -> £3,381,572.53 (10.3%); £3,771,119.29 -> £3,381,572.74 (10.3%); £3,771,119.48 -> £3,381,572.97 (10.3%); £3,771,119.67 -> £3,381,573.22 (10.3%); £3,771,119.89 -> £3,381,573.49 (10.3%); £3,771,120.14 -> £3,381,573.79 (10.3%); £3,771,120.38 -> £3,381,574.09 (10.3%); £3,771,120.64 -> £3,381,574.21 (10.3%); £3,771,120.88 -> £3,381,574.33 (10.3%); £3,771,121.14 -> £3,381,574.46 (10.3%); £3,771,121.39 -> £3,381,574.58 (10.3%); £3,771,121.64 -> £3,381,574.70 (10.3%); £3,771,121.89 -> £3,381,574.82 (10.3%); £3,771,122.16 -> £3,381,574.94 (10.3%); £3,771,122.41 -> £3,381,575.05 (10.3%); £3,771,122.66 -> £3,381,575.16 (10.3%); £3,771,122.92 -> £3,381,575.27 (10.3%); £3,771,123.17 -> £3,381,575.38 (10.3%); £3,771,123.42 -> £3,381,575.49 (10.3%); £3,771,123.66 -> £3,381,575.60 (10.3%); £3,771,123.92 -> £3,381,575.89 (10.3%); £3,771,124.10 -> £3,381,576.18 (10.3%); £3,771,124.36 -> £3,381,576.45 (10.3%); £3,771,124.61 -> £3,381,576.67 (10.3%); £3,771,124.81 -> £3,381,576.91 (10.3%); £3,771,125.05 -> £3,381,577.12 (10.3%); £3,771,125.23 -> £3,381,577.34 (10.3%); £3,771,125.49 -> £3,381,577.56 (10.3%); £3,771,125.74 -> £3,381,577.78 (10.3%); £3,771,125.99 -> £3,381,578.00 (10.3%); £3,771,126.24 -> £3,381,578.21 (10.3%); £3,771,126.49 -> £3,381,578.25 (10.3%); £3,771,126.73 -> £3,381,578.29 (10.3%); £3,771,126.97 -> £3,381,578.33 (10.3%); £3,771,127.18 -> £3,381,578.37 (10.3%); £3,771,127.37 -> £3,381,578.40 (10.3%); £3,771,127.53 -> £3,381,578.44 (10.3%); £3,771,127.68 -> £3,381,578.48 (10.3%); £3,771,127.82 -> £3,381,578.52 (10.3%); £3,771,127.98 -> £3,381,578.55 (10.3%); £3,771,128.12 -> £3,381,578.59 (10.3%); £3,771,128.28 -> £3,381,578.63 (10.3%); £3,771,128.43 -> £3,381,578.67 (10.3%); £3,771,128.58 -> £3,381,578.70 (10.3%); £3,771,128.73 -> £3,381,578.74 (10.3%); £3,771,128.87 -> £3,381,578.78 (10.3%); £3,771,129.03 -> £3,381,578.82 (10.3%); £3,771,129.18 -> £3,381,579.02 (10.3%); £3,771,129.32 -> £3,381,579.22 (10.3%); £3,771,129.49 -> £3,381,579.42 (10.3%); £3,771,129.67 -> £3,381,579.63 (10.3%); £3,771,129.87 -> £3,381,579.87 (10.3%); £3,771,130.08 -> £3,381,580.12 (10.3%); £3,771,130.31 -> £3,381,580.41 (10.3%); £3,771,130.56 -> £3,381,580.69 (10.3%); £3,771,130.82 -> £3,381,580.81 (10.3%); £3,771,131.06 -> £3,381,580.93 (10.3%); £3,771,131.31 -> £3,381,581.05 (10.3%); £3,771,131.57 -> £3,381,581.17 (10.3%); £3,771,131.81 -> £3,381,581.29 (10.3%); £3,771,132.06 -> £3,381,581.41 (10.3%); £3,771,132.30 -> £3,381,581.53 (10.3%); £3,771,132.54 -> £3,381,581.65 (10.3%); £3,771,132.79 -> £3,381,581.76 (10.3%); £3,771,133.04 -> £3,381,581.87 (10.3%); £3,771,133.29 -> £3,381,581.99 (10.3%); £3,771,133.54 -> £3,381,582.10 (10.3%); £3,771,133.79 -> £3,381,582.20 (10.3%); £3,771,133.98 -> £3,381,582.48 (10.3%); £3,771,134.16 -> £3,381,582.74 (10.3%); £3,771,134.35 -> £3,381,582.98 (10.3%); £3,771,134.53 -> £3,381,583.19 (10.3%); £3,771,134.72 -> £3,381,583.40 (10.3%); £3,771,134.90 -> £3,381,583.61 (10.3%); £3,771,135.08 -> £3,381,583.81 (10.3%); £3,771,135.33 -> £3,381,584.01 (10.3%); £3,771,135.58 -> £3,381,584.21 (10.3%); £3,771,135.84 -> £3,381,584.40 (10.3%); £3,771,136.08 -> £3,381,584.59 (10.3%); £3,771,136.33 -> £3,381,584.63 (10.3%); £3,771,136.58 -> £3,381,584.68 (10.3%); £3,771,136.81 -> £3,381,584.72 (10.3%); £3,771,137.02 -> £3,381,584.75 (10.3%); £3,771,137.21 -> £3,381,584.79 (10.3%); £3,771,137.36 -> £3,381,584.83 (10.3%); £3,771,137.51 -> £3,381,584.86 (10.3%); £3,771,137.66 -> £3,381,584.90 (10.3%); £3,771,137.80 -> £3,381,584.94 (10.3%); £3,771,137.95 -> £3,381,584.97 (10.3%); £3,771,138.10 -> £3,381,585.01 (10.3%); £3,771,138.25 -> £3,381,585.05 (10.3%); £3,771,138.39 -> £3,381,585.08 (10.3%); £3,771,138.54 -> £3,381,585.12 (10.3%); £3,771,138.69 -> £3,381,585.16 (10.3%); £3,771,138.84 -> £3,381,585.20 (10.3%); £3,771,138.98 -> £3,381,585.41 (10.3%); £3,771,139.14 -> £3,381,585.63 (10.3%); £3,771,139.30 -> £3,381,585.86 (10.3%); £3,771,139.48 -> £3,381,586.10 (10.3%); £3,771,139.68 -> £3,381,586.35 (10.3%); £3,771,139.89 -> £3,381,586.63 (10.3%); £3,771,140.12 -> £3,381,586.93 (10.3%); £3,771,140.37 -> £3,381,587.23 (10.3%); £3,771,140.60 -> £3,381,587.36 (10.3%); £3,771,140.84 -> £3,381,587.48 (10.3%); £3,771,141.09 -> £3,381,587.60 (10.3%); £3,771,141.34 -> £3,381,587.72 (10.3%); £3,771,141.58 -> £3,381,587.84 (10.3%); £3,771,141.84 -> £3,381,587.96 (10.3%); £3,771,142.08 -> £3,381,588.07 (10.3%); £3,771,142.32 -> £3,381,588.18 (10.3%); £3,771,142.56 -> £3,381,588.29 (10.3%); £3,771,142.80 -> £3,381,588.40 (10.3%); £3,771,143.05 -> £3,381,588.51 (10.3%); £3,771,143.29 -> £3,381,588.62 (10.3%); £3,771,143.53 -> £3,381,588.72 (10.3%); £3,771,143.72 -> £3,381,589.01 (10.3%); £3,771,143.90 -> £3,381,589.29 (10.3%); £3,771,144.09 -> £3,381,589.54 (10.3%); £3,771,144.27 -> £3,381,589.77 (10.3%); £3,771,144.45 -> £3,381,590.00 (10.3%); £3,771,144.63 -> £3,381,590.23 (10.3%); £3,771,144.82 -> £3,381,590.45 (10.3%); £3,771,145.06 -> £3,381,590.66 (10.3%); £3,771,145.31 -> £3,381,590.88 (10.3%); £3,771,145.56 -> £3,381,591.09 (10.3%); £3,771,145.80 -> £3,381,591.30 (10.3%); £3,771,146.05 -> £3,381,591.34 (10.3%); £3,771,146.30 -> £3,381,591.38 (10.3%); £3,771,146.53 -> £3,381,591.42 (10.3%); £3,771,146.74 -> £3,381,591.46 (10.3%); £3,771,146.94 -> £3,381,591.49 (10.3%); £3,771,147.06 -> £3,381,591.53 (10.3%); £3,771,147.19 -> £3,381,591.57 (10.3%); £3,771,147.32 -> £3,381,591.61 (10.3%); £3,771,147.45 -> £3,381,591.64 (10.3%); £3,771,147.58 -> £3,381,591.68 (10.3%); £3,771,147.71 -> £3,381,591.72 (10.3%); £3,771,147.84 -> £3,381,591.75 (10.3%); £3,771,147.97 -> £3,381,591.79 (10.3%); £3,771,148.09 -> £3,381,591.83 (10.3%); £3,771,148.22 -> £3,381,591.86 (10.3%); £3,771,148.35 -> £3,381,591.90 (10.3%); £3,771,148.48 -> £3,381,592.10 (10.3%); £3,771,148.61 -> £3,381,592.31 (10.3%); £3,771,148.75 -> £3,381,592.52 (10.3%); £3,771,148.91 -> £3,381,592.72 (10.3%); £3,771,149.08 -> £3,381,592.95 (10.3%); £3,771,149.26 -> £3,381,593.18 (10.3%); £3,771,149.46 -> £3,381,593.43 (10.3%); £3,771,149.67 -> £3,381,593.69 (10.3%); £3,771,149.88 -> £3,381,593.78 (10.3%); £3,771,150.09 -> £3,381,593.87 (10.3%); £3,771,150.30 -> £3,381,593.96 (10.3%); £3,771,150.51 -> £3,381,594.05 (10.3%); £3,771,150.72 -> £3,381,594.13 (10.3%); £3,771,150.94 -> £3,381,594.21 (10.3%); £3,771,151.15 -> £3,381,594.28 (10.3%); £3,771,151.36 -> £3,381,594.35 (10.3%); £3,771,151.58 -> £3,381,594.42 (10.3%); £3,771,151.79 -> £3,381,594.49 (10.3%); £3,771,152.00 -> £3,381,594.56 (10.3%); £3,771,152.21 -> £3,381,594.63 (10.3%); £3,771,152.43 -> £3,381,594.69 (10.3%); £3,771,152.59 -> £3,381,594.92 (10.3%); £3,771,152.75 -> £3,381,595.14 (10.3%); £3,771,152.91 -> £3,381,595.35 (10.3%); £3,771,153.07 -> £3,381,595.55 (10.3%); £3,771,153.23 -> £3,381,595.76 (10.3%); £3,771,153.38 -> £3,381,595.97 (10.3%); £3,771,153.59 -> £3,381,596.18 (10.3%); £3,771,153.81 -> £3,381,596.37 (10.3%); £3,771,154.03 -> £3,381,596.58 (10.3%); £3,771,154.24 -> £3,381,596.78 (10.3%); £3,771,154.45 -> £3,381,596.98 (10.3%); £3,771,154.66 -> £3,381,597.02 (10.3%); £3,771,154.88 -> £3,381,597.06 (10.3%); £3,771,155.07 -> £3,381,597.10 (10.3%); £3,771,155.25 -> £3,381,597.14 (10.3%); £3,771,155.41 -> £3,381,597.18 (10.3%); £3,771,155.54 -> £3,381,597.22 (10.3%); £3,771,155.67 -> £3,381,597.25 (10.3%); £3,771,155.79 -> £3,381,597.29 (10.3%); £3,771,155.91 -> £3,381,597.33 (10.3%); £3,771,156.04 -> £3,381,597.36 (10.3%); £3,771,156.17 -> £3,381,597.40 (10.3%); £3,771,156.29 -> £3,381,597.44 (10.3%); £3,771,156.42 -> £3,381,597.47 (10.3%); £3,771,156.55 -> £3,381,597.51 (10.3%); £3,771,156.68 -> £3,381,597.54 (10.3%); £3,771,156.80 -> £3,381,597.58 (10.3%); £3,771,156.93 -> £3,381,597.82 (10.3%); £3,771,157.05 -> £3,381,598.07 (10.3%); £3,771,157.20 -> £3,381,598.31 (10.3%); £3,771,157.35 -> £3,381,598.56 (10.3%); £3,771,157.52 -> £3,381,598.80 (10.3%); £3,771,157.71 -> £3,381,599.05 (10.3%); £3,771,157.91 -> £3,381,599.29 (10.3%); £3,771,158.11 -> £3,381,599.54 (10.3%); £3,771,158.33 -> £3,381,599.58 (10.3%); £3,771,158.53 -> £3,381,599.63 (10.3%); £3,771,158.74 -> £3,381,599.68 (10.3%); £3,771,158.96 -> £3,381,599.73 (10.3%); £3,771,159.17 -> £3,381,599.78 (10.3%); £3,771,159.38 -> £3,381,599.82 (10.3%); £3,771,159.59 -> £3,381,599.87 (10.3%); £3,771,159.80 -> £3,381,599.92 (10.3%); £3,771,160.02 -> £3,381,599.96 (10.3%); £3,771,160.22 -> £3,381,600.01 (10.3%); £3,771,160.43 -> £3,381,600.05 (10.3%); £3,771,160.64 -> £3,381,600.10 (10.3%); £3,771,160.85 -> £3,381,600.14 (10.3%); £3,771,161.01 -> £3,381,600.38 (10.3%); £3,771,161.17 -> £3,381,600.61 (10.3%); £3,771,161.34 -> £3,381,600.84 (10.3%); £3,771,161.49 -> £3,381,601.08 (10.3%); £3,771,161.65 -> £3,381,601.32 (10.3%); £3,771,161.82 -> £3,381,601.56 (10.3%); £3,771,161.97 -> £3,381,601.79 (10.3%); £3,771,162.19 -> £3,381,602.02 (10.3%); £3,771,162.41 -> £3,381,602.27 (10.3%); £3,771,162.61 -> £3,381,602.51 (10.3%); £3,771,162.82 -> £3,381,602.75 (10.3%); £3,771,163.03 -> £3,381,602.79 (10.3%); £3,771,163.24 -> £3,381,602.83 (10.3%); £3,771,163.44 -> £3,381,602.86 (10.3%); £3,771,163.62 -> £3,381,602.90 (10.3%); £3,771,163.79 -> £3,381,602.93 (10.3%); £3,771,163.94 -> £3,381,602.97 (10.3%); £3,771,164.08 -> £3,381,603.01 (10.3%); £3,771,164.23 -> £3,381,603.05 (10.3%); £3,771,164.38 -> £3,381,603.08 (10.3%); £3,771,164.52 -> £3,381,603.12 (10.3%); £3,771,164.67 -> £3,381,603.16 (10.3%); £3,771,164.81 -> £3,381,603.19 (10.3%); £3,771,164.96 -> £3,381,603.23 (10.3%); £3,771,165.11 -> £3,381,603.27 (10.3%); £3,771,165.25 -> £3,381,603.31 (10.3%); £3,771,165.39 -> £3,381,603.35 (10.3%); £3,771,165.53 -> £3,381,603.63 (10.3%); £3,771,165.68 -> £3,381,603.92 (10.3%); £3,771,165.84 -> £3,381,604.22 (10.3%); £3,771,166.02 -> £3,381,604.54 (10.3%); £3,771,166.20 -> £3,381,604.87 (10.3%); £3,771,166.41 -> £3,381,605.22 (10.3%); £3,771,166.63 -> £3,381,605.59 (10.3%); £3,771,166.87 -> £3,381,605.98 (10.3%); £3,771,167.11 -> £3,381,606.10 (10.3%); £3,771,167.36 -> £3,381,606.23 (10.3%); £3,771,167.60 -> £3,381,606.36 (10.3%); £3,771,167.85 -> £3,381,606.49 (10.3%); £3,771,168.09 -> £3,381,606.61 (10.3%); £3,771,168.33 -> £3,381,606.74 (10.3%); £3,771,168.57 -> £3,381,606.86 (10.3%); £3,771,168.81 -> £3,381,606.97 (10.3%); £3,771,169.05 -> £3,381,607.09 (10.3%); £3,771,169.30 -> £3,381,607.20 (10.3%); £3,771,169.54 -> £3,381,607.31 (10.3%); £3,771,169.78 -> £3,381,607.42 (10.3%); £3,771,170.02 -> £3,381,607.53 (10.3%); £3,771,170.21 -> £3,381,607.89 (10.3%); £3,771,170.39 -> £3,381,608.23 (10.3%); £3,771,170.58 -> £3,381,608.54 (10.3%); £3,771,170.76 -> £3,381,608.84 (10.3%); £3,771,170.94 -> £3,381,609.13 (10.3%); £3,771,171.12 -> £3,381,609.41 (10.3%); £3,771,171.29 -> £3,381,609.71 (10.3%); £3,771,171.54 -> £3,381,609.99 (10.3%); £3,771,171.77 -> £3,381,610.28 (10.3%); £3,771,172.01 -> £3,381,610.56 (10.3%); £3,771,172.25 -> £3,381,610.84 (10.3%); £3,771,172.50 -> £3,381,610.89 (10.3%); £3,771,172.74 -> £3,381,610.93 (10.3%); £3,771,172.96 -> £3,381,610.97 (10.3%); £3,771,173.17 -> £3,381,611.00 (10.3%); £3,771,173.36 -> £3,381,611.04 (10.3%); £3,771,173.50 -> £3,381,611.08 (10.3%); £3,771,173.65 -> £3,381,611.11 (10.3%); £3,771,173.79 -> £3,381,611.15 (10.3%); £3,771,173.93 -> £3,381,611.19 (10.3%); £3,771,174.07 -> £3,381,611.22 (10.3%); £3,771,174.21 -> £3,381,611.26 (10.3%); £3,771,174.35 -> £3,381,611.30 (10.3%); £3,771,174.49 -> £3,381,611.34 (10.3%); £3,771,174.64 -> £3,381,611.37 (10.3%); £3,771,174.78 -> £3,381,611.41 (10.3%); £3,771,174.93 -> £3,381,611.45 (10.3%); £3,771,175.07 -> £3,381,611.72 (10.3%); £3,771,175.22 -> £3,381,611.98 (10.3%); £3,771,175.38 -> £3,381,612.25 (10.3%); £3,771,175.56 -> £3,381,612.52 (10.3%); £3,771,175.74 -> £3,381,612.81 (10.3%); £3,771,175.96 -> £3,381,613.13 (10.3%); £3,771,176.18 -> £3,381,613.47 (10.3%); £3,771,176.43 -> £3,381,613.82 (10.3%); £3,771,176.67 -> £3,381,613.94 (10.3%); £3,771,176.90 -> £3,381,614.06 (10.3%); £3,771,177.14 -> £3,381,614.18 (10.3%); £3,771,177.38 -> £3,381,614.31 (10.3%); £3,771,177.61 -> £3,381,614.44 (10.3%); £3,771,177.86 -> £3,381,614.56 (10.3%); £3,771,178.09 -> £3,381,614.68 (10.3%); £3,771,178.32 -> £3,381,614.80 (10.3%); £3,771,178.56 -> £3,381,614.91 (10.3%); £3,771,178.80 -> £3,381,615.02 (10.3%); £3,771,179.03 -> £3,381,615.13 (10.3%); £3,771,179.27 -> £3,381,615.24 (10.3%); £3,771,179.51 -> £3,381,615.35 (10.3%); £3,771,179.69 -> £3,381,615.69 (10.3%); £3,771,179.87 -> £3,381,616.02 (10.3%); £3,771,180.06 -> £3,381,616.33 (10.3%); £3,771,180.31 -> £3,381,616.62 (10.3%); £3,771,180.55 -> £3,381,616.90 (10.3%); £3,771,180.80 -> £3,381,617.17 (10.3%); £3,771,180.98 -> £3,381,617.43 (10.3%); £3,771,181.22 -> £3,381,617.69 (10.3%); £3,771,181.46 -> £3,381,617.95 (10.3%); £3,771,181.70 -> £3,381,618.20 (10.3%); £3,771,181.94 -> £3,381,618.44 (10.3%); £3,771,182.19 -> £3,381,618.48 (10.3%); £3,771,182.43 -> £3,381,618.52 (10.3%); £3,771,182.65 -> £3,381,618.56 (10.3%); £3,771,182.85 -> £3,381,618.60 (10.3%); £3,771,183.03 -> £3,381,618.64 (10.3%); £3,771,183.18 -> £3,381,618.67 (10.3%); £3,771,183.32 -> £3,381,618.71 (10.3%); £3,771,183.45 -> £3,381,618.75 (10.3%); £3,771,183.59 -> £3,381,618.79 (10.3%); £3,771,183.73 -> £3,381,618.83 (10.3%); £3,771,183.88 -> £3,381,618.86 (10.3%); £3,771,184.02 -> £3,381,618.90 (10.3%); £3,771,184.16 -> £3,381,618.94 (10.3%); £3,771,184.31 -> £3,381,618.98 (10.3%); £3,771,184.45 -> £3,381,619.02 (10.3%); £3,771,184.59 -> £3,381,619.06 (10.3%); £3,771,184.73 -> £3,381,619.34 (10.3%); £3,771,184.87 -> £3,381,619.62 (10.3%); £3,771,185.02 -> £3,381,619.92 (10.3%); £3,771,185.20 -> £3,381,620.23 (10.3%); £3,771,185.39 -> £3,381,620.55 (10.3%); £3,771,185.59 -> £3,381,620.90 (10.3%); £3,771,185.81 -> £3,381,621.28 (10.3%); £3,771,186.05 -> £3,381,621.67 (10.3%); £3,771,186.29 -> £3,381,621.79 (10.3%); £3,771,186.52 -> £3,381,621.92 (10.3%); £3,771,186.76 -> £3,381,622.04 (10.3%); £3,771,187.00 -> £3,381,622.17 (10.3%); £3,771,187.23 -> £3,381,622.29 (10.3%); £3,771,187.47 -> £3,381,622.41 (10.3%); £3,771,187.71 -> £3,381,622.52 (10.3%); £3,771,187.94 -> £3,381,622.64 (10.3%); £3,771,188.18 -> £3,381,622.75 (10.3%); £3,771,188.42 -> £3,381,622.87 (10.3%); £3,771,188.67 -> £3,381,622.98 (10.3%); £3,771,188.90 -> £3,381,623.08 (10.3%); £3,771,189.14 -> £3,381,623.19 (10.3%); £3,771,189.31 -> £3,381,623.54 (10.3%); £3,771,189.49 -> £3,381,623.89 (10.3%); £3,771,189.73 -> £3,381,624.21 (10.3%); £3,771,189.97 -> £3,381,624.52 (10.3%); £3,771,190.21 -> £3,381,624.81 (10.3%); £3,771,190.44 -> £3,381,625.10 (10.3%); £3,771,190.69 -> £3,381,625.38 (10.3%); £3,771,190.93 -> £3,381,625.67 (10.3%); £3,771,191.17 -> £3,381,625.94 (10.3%); £3,771,191.40 -> £3,381,626.21 (10.3%); £3,771,191.64 -> £3,381,626.46 (10.3%); £3,771,191.87 -> £3,381,626.50 (10.3%); £3,771,192.10 -> £3,381,626.54 (10.3%); £3,771,192.31 -> £3,381,626.58 (10.3%); £3,771,192.51 -> £3,381,626.62 (10.3%); £3,771,192.69 -> £3,381,626.66 (10.3%); £3,771,192.83 -> £3,381,626.70 (10.3%); £3,771,192.97 -> £3,381,626.73 (10.3%); £3,771,193.12 -> £3,381,626.77 (10.3%); £3,771,193.26 -> £3,381,626.81 (10.3%); £3,771,193.40 -> £3,381,626.85 (10.3%); £3,771,193.54 -> £3,381,626.88 (10.3%); £3,771,193.68 -> £3,381,626.92 (10.3%); £3,771,193.82 -> £3,381,626.95 (10.3%); £3,771,193.97 -> £3,381,626.99 (10.3%); £3,771,194.11 -> £3,381,627.03 (10.3%); £3,771,194.26 -> £3,381,627.07 (10.3%); £3,771,194.40 -> £3,381,627.37 (10.3%); £3,771,194.54 -> £3,381,627.68 (10.3%); £3,771,194.70 -> £3,381,627.99 (10.3%); £3,771,194.87 -> £3,381,628.32 (10.3%); £3,771,195.06 -> £3,381,628.67 (10.3%); £3,771,195.27 -> £3,381,629.03 (10.3%); £3,771,195.49 -> £3,381,629.42 (10.3%); £3,771,195.72 -> £3,381,629.82 (10.3%); £3,771,195.95 -> £3,381,629.95 (10.3%); £3,771,196.19 -> £3,381,630.07 (10.3%); £3,771,196.42 -> £3,381,630.20 (10.3%); £3,771,196.65 -> £3,381,630.32 (10.3%); £3,771,196.87 -> £3,381,630.45 (10.3%); £3,771,197.12 -> £3,381,630.57 (10.3%); £3,771,197.36 -> £3,381,630.68 (10.3%); £3,771,197.60 -> £3,381,630.79 (10.3%); £3,771,197.83 -> £3,381,630.91 (10.3%); £3,771,198.07 -> £3,381,631.03 (10.3%); £3,771,198.30 -> £3,381,631.14 (10.3%); £3,771,198.54 -> £3,381,631.25 (10.3%); £3,771,198.78 -> £3,381,631.36 (10.3%); £3,771,198.96 -> £3,381,631.75 (10.3%); £3,771,199.14 -> £3,381,632.12 (10.3%); £3,771,199.31 -> £3,381,632.46 (10.3%); £3,771,199.48 -> £3,381,632.78 (10.3%); £3,771,199.67 -> £3,381,633.10 (10.3%); £3,771,199.84 -> £3,381,633.41 (10.3%); £3,771,200.02 -> £3,381,633.71 (10.3%); £3,771,200.25 -> £3,381,634.01 (10.3%); £3,771,200.48 -> £3,381,634.31 (10.3%); £3,771,200.72 -> £3,381,634.61 (10.3%); £3,771,200.94 -> £3,381,634.91 (10.3%); £3,771,201.18 -> £3,381,634.95 (10.3%); £3,771,201.42 -> £3,381,635.00 (10.3%); £3,771,201.64 -> £3,381,635.04 (10.3%); £3,771,201.85 -> £3,381,635.07 (10.3%); £3,771,202.04 -> £3,381,635.11 (10.3%); £3,771,202.18 -> £3,381,635.15 (10.3%); £3,771,202.32 -> £3,381,635.19 (10.3%); £3,771,202.47 -> £3,381,635.22 (10.3%); £3,771,202.61 -> £3,381,635.26 (10.3%); £3,771,202.75 -> £3,381,635.30 (10.3%); £3,771,202.90 -> £3,381,635.34 (10.3%); £3,771,203.04 -> £3,381,635.37 (10.3%); £3,771,203.19 -> £3,381,635.41 (10.3%); £3,771,203.32 -> £3,381,635.45 (10.3%); £3,771,203.47 -> £3,381,635.49 (10.3%); £3,771,203.62 -> £3,381,635.53 (10.3%); £3,771,203.76 -> £3,381,635.79 (10.3%); £3,771,203.90 -> £3,381,636.06 (10.3%); £3,771,204.06 -> £3,381,636.33 (10.3%); £3,771,204.24 -> £3,381,636.62 (10.3%); £3,771,204.43 -> £3,381,636.93 (10.3%); £3,771,204.63 -> £3,381,637.26 (10.3%); £3,771,204.85 -> £3,381,637.61 (10.3%); £3,771,205.09 -> £3,381,637.97 (10.3%); £3,771,205.32 -> £3,381,638.09 (10.3%); £3,771,205.56 -> £3,381,638.22 (10.3%); £3,771,205.79 -> £3,381,638.34 (10.3%); £3,771,206.03 -> £3,381,638.47 (10.3%); £3,771,206.28 -> £3,381,638.60 (10.3%); £3,771,206.52 -> £3,381,638.72 (10.3%); £3,771,206.76 -> £3,381,638.84 (10.3%); £3,771,206.99 -> £3,381,638.96 (10.3%); £3,771,207.22 -> £3,381,639.08 (10.3%); £3,771,207.46 -> £3,381,639.19 (10.3%); £3,771,207.70 -> £3,381,639.31 (10.3%); £3,771,207.94 -> £3,381,639.42 (10.3%); £3,771,208.18 -> £3,381,639.53 (10.3%); £3,771,208.41 -> £3,381,639.87 (10.3%); £3,771,208.59 -> £3,381,640.20 (10.3%); £3,771,208.76 -> £3,381,640.50 (10.3%); £3,771,208.95 -> £3,381,640.79 (10.3%); £3,771,209.12 -> £3,381,641.07 (10.3%); £3,771,209.37 -> £3,381,641.34 (10.3%); £3,771,209.61 -> £3,381,641.61 (10.3%); £3,771,209.86 -> £3,381,641.88 (10.3%); £3,771,210.10 -> £3,381,642.15 (10.3%); £3,771,210.34 -> £3,381,642.40 (10.3%); £3,771,210.58 -> £3,381,642.65 (10.3%); £3,771,210.83 -> £3,381,642.70 (10.3%); £3,771,211.07 -> £3,381,642.74 (10.3%); £3,771,211.29 -> £3,381,642.78 (10.3%); £3,771,211.49 -> £3,381,642.81 (10.3%); £3,771,211.68 -> £3,381,642.85 (10.3%); £3,771,211.81 -> £3,381,642.89 (10.3%); £3,771,211.94 -> £3,381,642.92 (10.3%); £3,771,212.06 -> £3,381,642.96 (10.3%); £3,771,212.19 -> £3,381,643.00 (10.3%); £3,771,212.32 -> £3,381,643.04 (10.3%); £3,771,212.45 -> £3,381,643.07 (10.3%); £3,771,212.58 -> £3,381,643.11 (10.3%); £3,771,212.71 -> £3,381,643.15 (10.3%); £3,771,212.83 -> £3,381,643.19 (10.3%); £3,771,212.96 -> £3,381,643.22 (10.3%); £3,771,213.09 -> £3,381,643.26 (10.3%); £3,771,213.22 -> £3,381,643.47 (10.3%); £3,771,213.35 -> £3,381,643.67 (10.3%); £3,771,213.49 -> £3,381,643.89 (10.3%); £3,771,213.65 -> £3,381,644.10 (10.3%); £3,771,213.82 -> £3,381,644.33 (10.3%); £3,771,214.01 -> £3,381,644.57 (10.3%); £3,771,214.22 -> £3,381,644.83 (10.3%); £3,771,214.43 -> £3,381,645.10 (10.3%); £3,771,214.64 -> £3,381,645.18 (10.3%); £3,771,214.86 -> £3,381,645.27 (10.3%); £3,771,215.07 -> £3,381,645.36 (10.3%); £3,771,215.28 -> £3,381,645.45 (10.3%); £3,771,215.50 -> £3,381,645.53 (10.3%); £3,771,215.71 -> £3,381,645.61 (10.3%); £3,771,215.92 -> £3,381,645.69 (10.3%); £3,771,216.14 -> £3,381,645.76 (10.3%); £3,771,216.36 -> £3,381,645.83 (10.3%); £3,771,216.57 -> £3,381,645.90 (10.3%); £3,771,216.78 -> £3,381,645.97 (10.3%); £3,771,216.99 -> £3,381,646.03 (10.3%); £3,771,217.21 -> £3,381,646.10 (10.3%); £3,771,217.37 -> £3,381,646.34 (10.3%); £3,771,217.54 -> £3,381,646.57 (10.3%); £3,771,217.70 -> £3,381,646.79 (10.3%); £3,771,217.86 -> £3,381,647.00 (10.3%); £3,771,218.02 -> £3,381,647.21 (10.3%); £3,771,218.19 -> £3,381,647.42 (10.3%); £3,771,218.35 -> £3,381,647.63 (10.3%); £3,771,218.56 -> £3,381,647.83 (10.3%); £3,771,218.78 -> £3,381,648.04 (10.3%); £3,771,218.99 -> £3,381,648.24 (10.3%); £3,771,219.21 -> £3,381,648.45 (10.3%); £3,771,219.42 -> £3,381,648.49 (10.3%); £3,771,219.63 -> £3,381,648.53 (10.3%); £3,771,219.84 -> £3,381,648.56 (10.3%); £3,771,220.02 -> £3,381,648.60 (10.3%); £3,771,220.18 -> £3,381,648.64 (10.3%); £3,771,220.31 -> £3,381,648.68 (10.3%); £3,771,220.44 -> £3,381,648.72 (10.3%); £3,771,220.57 -> £3,381,648.75 (10.3%); £3,771,220.70 -> £3,381,648.79 (10.3%); £3,771,220.83 -> £3,381,648.83 (10.3%); £3,771,220.96 -> £3,381,648.86 (10.3%); £3,771,221.09 -> £3,381,648.90 (10.3%); £3,771,221.21 -> £3,381,648.93 (10.3%); £3,771,221.34 -> £3,381,648.97 (10.3%); £3,771,221.47 -> £3,381,649.00 (10.3%); £3,771,221.60 -> £3,381,649.04 (10.3%); £3,771,221.73 -> £3,381,649.18 (10.3%); £3,771,221.86 -> £3,381,649.32 (10.3%); £3,771,222.00 -> £3,381,649.46 (10.3%); £3,771,222.16 -> £3,381,649.60 (10.3%); £3,771,222.33 -> £3,381,649.75 (10.3%); £3,771,222.52 -> £3,381,649.89 (10.3%); £3,771,222.72 -> £3,381,650.04 (10.3%); £3,771,222.94 -> £3,381,650.19 (10.3%); £3,771,223.16 -> £3,381,650.24 (10.3%); £3,771,223.37 -> £3,381,650.29 (10.3%); £3,771,223.59 -> £3,381,650.34 (10.3%); £3,771,223.80 -> £3,381,650.38 (10.3%); £3,771,224.01 -> £3,381,650.43 (10.3%); £3,771,224.23 -> £3,381,650.48 (10.3%); £3,771,224.44 -> £3,381,650.53 (10.3%); £3,771,224.66 -> £3,381,650.57 (10.3%); £3,771,224.87 -> £3,381,650.62 (10.3%); £3,771,225.08 -> £3,381,650.66 (10.3%); £3,771,225.30 -> £3,381,650.71 (10.3%); £3,771,225.52 -> £3,381,650.75 (10.3%); £3,771,225.74 -> £3,381,650.80 (10.3%); £3,771,225.90 -> £3,381,650.95 (10.3%); £3,771,226.06 -> £3,381,651.09 (10.3%); £3,771,226.22 -> £3,381,651.24 (10.3%); £3,771,226.37 -> £3,381,651.39 (10.3%); £3,771,226.53 -> £3,381,651.54 (10.3%); £3,771,226.70 -> £3,381,651.68 (10.3%); £3,771,226.85 -> £3,381,651.83 (10.3%); £3,771,227.07 -> £3,381,651.97 (10.3%); £3,771,227.28 -> £3,381,652.12 (10.3%); £3,771,227.51 -> £3,381,652.26 (10.3%); £3,771,227.72 -> £3,381,652.39 (10.3%); £3,771,227.93 -> £3,381,652.43 (10.3%); £3,771,228.15 -> £3,381,652.47 (10.3%); £3,771,228.34 -> £3,381,652.51 (10.3%); £3,771,228.52 -> £3,381,652.54 (10.3%); £3,771,228.68 -> £3,381,652.58 (10.3%); £3,771,228.83 -> £3,381,652.62 (10.3%); £3,771,228.98 -> £3,381,652.66 (10.3%); £3,771,229.12 -> £3,381,652.69 (10.3%); £3,771,229.27 -> £3,381,652.73 (10.3%); £3,771,229.41 -> £3,381,652.77 (10.3%); £3,771,229.56 -> £3,381,652.80 (10.3%); £3,771,229.71 -> £3,381,652.84 (10.3%); £3,771,229.86 -> £3,381,652.88 (10.3%); £3,771,230.00 -> £3,381,652.91 (10.3%); £3,771,230.14 -> £3,381,652.95 (10.3%); £3,771,230.29 -> £3,381,652.99 (10.3%); £3,771,230.44 -> £3,381,653.16 (10.3%); £3,771,230.58 -> £3,381,653.33 (10.3%); £3,771,230.74 -> £3,381,653.51 (10.3%); £3,771,230.92 -> £3,381,653.70 (10.3%); £3,771,231.12 -> £3,381,653.91 (10.3%); £3,771,231.34 -> £3,381,654.14 (10.3%); £3,771,231.57 -> £3,381,654.39 (10.3%); £3,771,231.82 -> £3,381,654.66 (10.3%); £3,771,232.07 -> £3,381,654.78 (10.3%); £3,771,232.31 -> £3,381,654.91 (10.3%); £3,771,232.57 -> £3,381,655.04 (10.3%); £3,771,232.80 -> £3,381,655.16 (10.3%); £3,771,233.05 -> £3,381,655.29 (10.3%); £3,771,233.31 -> £3,381,655.41 (10.3%); £3,771,233.55 -> £3,381,655.52 (10.3%); £3,771,233.80 -> £3,381,655.64 (10.3%); £3,771,234.06 -> £3,381,655.76 (10.3%); £3,771,234.30 -> £3,381,655.88 (10.3%); £3,771,234.55 -> £3,381,656.00 (10.3%); £3,771,234.80 -> £3,381,656.11 (10.3%); £3,771,235.05 -> £3,381,656.22 (10.3%); £3,771,235.29 -> £3,381,656.49 (10.3%); £3,771,235.48 -> £3,381,656.72 (10.3%); £3,771,235.66 -> £3,381,656.94 (10.3%); £3,771,235.85 -> £3,381,657.13 (10.3%); £3,771,236.02 -> £3,381,657.31 (10.3%); £3,771,236.21 -> £3,381,657.49 (10.3%); £3,771,236.39 -> £3,381,657.68 (10.3%); £3,771,236.63 -> £3,381,657.85 (10.3%); £3,771,236.87 -> £3,381,658.02 (10.3%); £3,771,237.12 -> £3,381,658.19 (10.3%); £3,771,237.37 -> £3,381,658.36 (10.3%); £3,771,237.61 -> £3,381,658.40 (10.3%); £3,771,237.86 -> £3,381,658.44 (10.3%); £3,771,238.09 -> £3,381,658.48 (10.3%); £3,771,238.30 -> £3,381,658.52 (10.3%); £3,771,238.49 -> £3,381,658.56 (10.3%); £3,771,238.64 -> £3,381,658.59 (10.3%); £3,771,238.79 -> £3,381,658.63 (10.3%); £3,771,238.93 -> £3,381,658.67 (10.3%); £3,771,239.07 -> £3,381,658.71 (10.3%); £3,771,239.23 -> £3,381,658.75 (10.3%); £3,771,239.37 -> £3,381,658.79 (10.3%); £3,771,239.52 -> £3,381,658.83 (10.3%); £3,771,239.67 -> £3,381,658.87 (10.3%); £3,771,239.82 -> £3,381,658.90 (10.3%); £3,771,239.96 -> £3,381,658.94 (10.3%); £3,771,240.11 -> £3,381,658.98 (10.3%); £3,771,240.26 -> £3,381,659.14 (10.3%); £3,771,240.41 -> £3,381,659.29 (10.3%); £3,771,240.58 -> £3,381,659.47 (10.3%); £3,771,240.76 -> £3,381,659.65 (10.3%); £3,771,240.96 -> £3,381,659.85 (10.3%); £3,771,241.17 -> £3,381,660.08 (10.3%); £3,771,241.40 -> £3,381,660.32 (10.3%); £3,771,241.65 -> £3,381,660.57 (10.3%); £3,771,241.90 -> £3,381,660.70 (10.3%); £3,771,242.14 -> £3,381,660.83 (10.3%); £3,771,242.39 -> £3,381,660.96 (10.3%); £3,771,242.63 -> £3,381,661.09 (10.3%); £3,771,242.89 -> £3,381,661.22 (10.3%); £3,771,243.13 -> £3,381,661.34 (10.3%); £3,771,243.38 -> £3,381,661.46 (10.3%); £3,771,243.62 -> £3,381,661.58 (10.3%); £3,771,243.87 -> £3,381,661.69 (10.3%); £3,771,244.11 -> £3,381,661.81 (10.3%); £3,771,244.35 -> £3,381,661.93 (10.3%); £3,771,244.60 -> £3,381,662.04 (10.3%); £3,771,244.85 -> £3,381,662.15 (10.3%); £3,771,245.03 -> £3,381,662.40 (10.3%); £3,771,245.22 -> £3,381,662.64 (10.3%); £3,771,245.48 -> £3,381,662.84 (10.3%); £3,771,245.72 -> £3,381,663.03 (10.3%); £3,771,245.96 -> £3,381,663.21 (10.3%); £3,771,246.21 -> £3,381,663.38 (10.3%); £3,771,246.40 -> £3,381,663.55 (10.3%); £3,771,246.65 -> £3,381,663.71 (10.3%); £3,771,246.90 -> £3,381,663.88 (10.3%); £3,771,247.15 -> £3,381,664.03 (10.3%); £3,771,247.40 -> £3,381,664.18 (10.3%); £3,771,247.65 -> £3,381,664.22 (10.3%); £3,771,247.90 -> £3,381,664.27 (10.3%); £3,771,248.13 -> £3,381,664.31 (10.3%); £3,771,248.33 -> £3,381,664.34 (10.3%); £3,771,248.53 -> £3,381,664.38 (10.3%); £3,771,248.67 -> £3,381,664.42 (10.3%); £3,771,248.82 -> £3,381,664.46 (10.3%); £3,771,248.97 -> £3,381,664.50 (10.3%); £3,771,249.12 -> £3,381,664.54 (10.3%); £3,771,249.27 -> £3,381,664.58 (10.3%); £3,771,249.41 -> £3,381,664.61 (10.3%); £3,771,249.56 -> £3,381,664.65 (10.3%); £3,771,249.71 -> £3,381,664.69 (10.3%); £3,771,249.86 -> £3,381,664.73 (10.3%); £3,771,250.01 -> £3,381,664.77 (10.3%); £3,771,250.16 -> £3,381,664.81 (10.3%); £3,771,250.32 -> £3,381,664.97 (10.3%); £3,771,250.47 -> £3,381,665.13 (10.3%); £3,771,250.64 -> £3,381,665.30 (10.3%); £3,771,250.82 -> £3,381,665.49 (10.3%); £3,771,251.02 -> £3,381,665.70 (10.3%); £3,771,251.23 -> £3,381,665.92 (10.3%); £3,771,251.47 -> £3,381,666.18 (10.3%); £3,771,251.71 -> £3,381,666.44 (10.3%); £3,771,251.97 -> £3,381,666.57 (10.3%); £3,771,252.22 -> £3,381,666.70 (10.3%); £3,771,252.47 -> £3,381,666.83 (10.3%); £3,771,252.72 -> £3,381,666.96 (10.3%); £3,771,252.97 -> £3,381,667.09 (10.3%); £3,771,253.22 -> £3,381,667.21 (10.3%); £3,771,253.47 -> £3,381,667.33 (10.3%); £3,771,253.73 -> £3,381,667.45 (10.3%); £3,771,253.99 -> £3,381,667.57 (10.3%); £3,771,254.24 -> £3,381,667.69 (10.3%); £3,771,254.50 -> £3,381,667.81 (10.3%); £3,771,254.75 -> £3,381,667.93 (10.3%); £3,771,255.00 -> £3,381,668.05 (10.3%); £3,771,255.25 -> £3,381,668.30 (10.3%); £3,771,255.43 -> £3,381,668.54 (10.3%); £3,771,255.62 -> £3,381,668.76 (10.3%); £3,771,255.87 -> £3,381,668.95 (10.3%); £3,771,256.12 -> £3,381,669.14 (10.3%); £3,771,256.38 -> £3,381,669.32 (10.3%); £3,771,256.57 -> £3,381,669.50 (10.3%); £3,771,256.82 -> £3,381,669.68 (10.3%); £3,771,257.08 -> £3,381,669.85 (10.3%); £3,771,257.33 -> £3,381,670.02 (10.3%); £3,771,257.58 -> £3,381,670.18 (10.3%); £3,771,257.83 -> £3,381,670.22 (10.3%); £3,771,258.08 -> £3,381,670.26 (10.3%); £3,771,258.32 -> £3,381,670.30 (10.3%); £3,771,258.53 -> £3,381,670.34 (10.3%); £3,771,258.73 -> £3,381,670.37 (10.3%); £3,771,258.88 -> £3,381,670.41 (10.3%); £3,771,259.03 -> £3,381,670.45 (10.3%); £3,771,259.19 -> £3,381,670.49 (10.3%); £3,771,259.35 -> £3,381,670.53 (10.3%); £3,771,259.50 -> £3,381,670.56 (10.3%); £3,771,259.66 -> £3,381,670.60 (10.3%); £3,771,259.81 -> £3,381,670.64 (10.3%); £3,771,259.97 -> £3,381,670.68 (10.3%); £3,771,260.12 -> £3,381,670.71 (10.3%); £3,771,260.27 -> £3,381,670.75 (10.3%); £3,771,260.43 -> £3,381,670.79 (10.3%); £3,771,260.58 -> £3,381,670.94 (10.3%); £3,771,260.74 -> £3,381,671.09 (10.3%); £3,771,260.90 -> £3,381,671.25 (10.3%); £3,771,261.09 -> £3,381,671.43 (10.3%); £3,771,261.30 -> £3,381,671.63 (10.3%); £3,771,261.51 -> £3,381,671.84 (10.3%); £3,771,261.75 -> £3,381,672.09 (10.3%); £3,771,262.00 -> £3,381,672.35 (10.3%); £3,771,262.26 -> £3,381,672.47 (10.3%); £3,771,262.51 -> £3,381,672.60 (10.3%); £3,771,262.76 -> £3,381,672.73 (10.3%); £3,771,263.02 -> £3,381,672.86 (10.3%); £3,771,263.27 -> £3,381,672.99 (10.3%); £3,771,263.53 -> £3,381,673.11 (10.3%); £3,771,263.79 -> £3,381,673.23 (10.3%); £3,771,264.04 -> £3,381,673.35 (10.3%); £3,771,264.30 -> £3,381,673.47 (10.3%); £3,771,264.56 -> £3,381,673.59 (10.3%); £3,771,264.81 -> £3,381,673.70 (10.3%); £3,771,265.06 -> £3,381,673.81 (10.3%); £3,771,265.32 -> £3,381,673.92 (10.3%); £3,771,265.52 -> £3,381,674.17 (10.3%); £3,771,265.71 -> £3,381,674.39 (10.3%); £3,771,265.89 -> £3,381,674.59 (10.3%); £3,771,266.08 -> £3,381,674.78 (10.3%); £3,771,266.34 -> £3,381,674.95 (10.3%); £3,771,266.59 -> £3,381,675.12 (10.3%); £3,771,266.79 -> £3,381,675.28 (10.3%); £3,771,267.05 -> £3,381,675.44 (10.3%); £3,771,267.31 -> £3,381,675.60 (10.3%); £3,771,267.57 -> £3,381,675.75 (10.3%); £3,771,267.81 -> £3,381,675.90 (10.3%); £3,771,268.07 -> £3,381,675.94 (10.3%); £3,771,268.33 -> £3,381,675.98 (10.3%); £3,771,268.56 -> £3,381,676.02 (10.3%); £3,771,268.78 -> £3,381,676.06 (10.3%); £3,771,268.98 -> £3,381,676.10 (10.3%); £3,771,269.14 -> £3,381,676.13 (10.3%); £3,771,269.29 -> £3,381,676.17 (10.3%); £3,771,269.44 -> £3,381,676.21 (10.3%); £3,771,269.59 -> £3,381,676.25 (10.3%); £3,771,269.74 -> £3,381,676.28 (10.3%); £3,771,269.89 -> £3,381,676.32 (10.3%); £3,771,270.05 -> £3,381,676.36 (10.3%); £3,771,270.20 -> £3,381,676.40 (10.3%); £3,771,270.36 -> £3,381,676.44 (10.3%); £3,771,270.51 -> £3,381,676.48 (10.3%); £3,771,270.66 -> £3,381,676.52 (10.3%); £3,771,270.81 -> £3,381,676.68 (10.3%); £3,771,270.97 -> £3,381,676.85 (10.3%); £3,771,271.14 -> £3,381,677.04 (10.3%); £3,771,271.33 -> £3,381,677.23 (10.3%); £3,771,271.53 -> £3,381,677.45 (10.3%); £3,771,271.75 -> £3,381,677.68 (10.3%); £3,771,272.00 -> £3,381,677.94 (10.3%); £3,771,272.26 -> £3,381,678.21 (10.3%); £3,771,272.53 -> £3,381,678.34 (10.3%); £3,771,272.79 -> £3,381,678.47 (10.3%); £3,771,273.05 -> £3,381,678.61 (10.3%); £3,771,273.30 -> £3,381,678.76 (10.3%); £3,771,273.56 -> £3,381,678.90 (10.3%); £3,771,273.80 -> £3,381,679.04 (10.3%); £3,771,274.06 -> £3,381,679.16 (10.3%); £3,771,274.31 -> £3,381,679.29 (10.3%); £3,771,274.58 -> £3,381,679.42 (10.3%); £3,771,274.84 -> £3,381,679.53 (10.3%); £3,771,275.08 -> £3,381,679.65 (10.3%); £3,771,275.33 -> £3,381,679.76 (10.3%); £3,771,275.59 -> £3,381,679.86 (10.3%); £3,771,275.79 -> £3,381,680.12 (10.3%); £3,771,275.98 -> £3,381,680.37 (10.3%); £3,771,276.17 -> £3,381,680.58 (10.3%); £3,771,276.37 -> £3,381,680.78 (10.3%); £3,771,276.57 -> £3,381,680.97 (10.3%); £3,771,276.76 -> £3,381,681.15 (10.3%); £3,771,276.95 -> £3,381,681.34 (10.3%); £3,771,277.21 -> £3,381,681.52 (10.3%); £3,771,277.47 -> £3,381,681.70 (10.3%); £3,771,277.72 -> £3,381,681.88 (10.3%); £3,771,277.98 -> £3,381,682.05 (10.3%); £3,771,278.23 -> £3,381,682.09 (10.3%); £3,771,278.49 -> £3,381,682.13 (10.3%); £3,771,278.72 -> £3,381,682.17 (10.3%); £3,771,278.93 -> £3,381,682.21 (10.3%); £3,771,279.14 -> £3,381,682.25 (10.3%); £3,771,279.28 -> £3,381,682.29 (10.3%); £3,771,279.42 -> £3,381,682.32 (10.3%); £3,771,279.56 -> £3,381,682.36 (10.3%); £3,771,279.70 -> £3,381,682.40 (10.3%); £3,771,279.84 -> £3,381,682.44 (10.3%); £3,771,279.99 -> £3,381,682.47 (10.3%); £3,771,280.13 -> £3,381,682.51 (10.3%); £3,771,280.27 -> £3,381,682.55 (10.3%); £3,771,280.40 -> £3,381,682.59 (10.3%); £3,771,280.54 -> £3,381,682.63 (10.3%); £3,771,280.67 -> £3,381,682.67 (10.3%); £3,771,280.81 -> £3,381,682.86 (10.3%); £3,771,280.96 -> £3,381,683.04 (10.3%); £3,771,281.11 -> £3,381,683.23 (10.3%); £3,771,281.28 -> £3,381,683.43 (10.3%); £3,771,281.47 -> £3,381,683.64 (10.3%); £3,771,281.67 -> £3,381,683.86 (10.3%); £3,771,281.89 -> £3,381,684.10 (10.3%); £3,771,282.12 -> £3,381,684.35 (10.3%); £3,771,282.35 -> £3,381,684.44 (10.3%); £3,771,282.59 -> £3,381,684.53 (10.3%); £3,771,282.82 -> £3,381,684.62 (10.3%); £3,771,283.05 -> £3,381,684.71 (10.3%); £3,771,283.28 -> £3,381,684.80 (10.3%); £3,771,283.50 -> £3,381,684.88 (10.3%); £3,771,283.74 -> £3,381,684.96 (10.3%); £3,771,283.97 -> £3,381,685.04 (10.3%); £3,771,284.20 -> £3,381,685.12 (10.3%); £3,771,284.44 -> £3,381,685.19 (10.3%); £3,771,284.67 -> £3,381,685.26 (10.3%); £3,771,284.90 -> £3,381,685.33 (10.3%); £3,771,285.12 -> £3,381,685.39 (10.3%); £3,771,285.30 -> £3,381,685.61 (10.3%); £3,771,285.48 -> £3,381,685.82 (10.3%); £3,771,285.65 -> £3,381,686.02 (10.3%); £3,771,285.82 -> £3,381,686.21 (10.3%); £3,771,285.99 -> £3,381,686.41 (10.3%); £3,771,286.23 -> £3,381,686.61 (10.3%); £3,771,286.46 -> £3,381,686.80 (10.3%); £3,771,286.69 -> £3,381,686.99 (10.3%); £3,771,286.92 -> £3,381,687.18 (10.3%); £3,771,287.15 -> £3,381,687.36 (10.3%); £3,771,287.38 -> £3,381,687.56 (10.3%); £3,771,287.61 -> £3,381,687.60 (10.3%); £3,771,287.84 -> £3,381,687.64 (10.3%); £3,771,288.05 -> £3,381,687.68 (10.3%); £3,771,288.24 -> £3,381,687.72 (10.3%); £3,771,288.42 -> £3,381,687.76 (10.3%); £3,771,288.55 -> £3,381,687.80 (10.3%); £3,771,288.70 -> £3,381,687.84 (10.3%); £3,771,288.84 -> £3,381,687.88 (10.3%); £3,771,288.98 -> £3,381,687.91 (10.3%); £3,771,289.12 -> £3,381,687.95 (10.3%); £3,771,289.26 -> £3,381,687.99 (10.3%); £3,771,289.40 -> £3,381,688.02 (10.3%); £3,771,289.55 -> £3,381,688.06 (10.3%); £3,771,289.68 -> £3,381,688.10 (10.3%); £3,771,289.82 -> £3,381,688.13 (10.3%); £3,771,289.95 -> £3,381,688.17 (10.3%); £3,771,290.09 -> £3,381,688.33 (10.3%); £3,771,290.23 -> £3,381,688.49 (10.3%); £3,771,290.39 -> £3,381,688.65 (10.3%); £3,771,290.56 -> £3,381,688.80 (10.3%); £3,771,290.75 -> £3,381,688.96 (10.3%); £3,771,290.96 -> £3,381,689.12 (10.3%); £3,771,291.18 -> £3,381,689.28 (10.3%); £3,771,291.41 -> £3,381,689.45 (10.3%); £3,771,291.64 -> £3,381,689.50 (10.3%); £3,771,291.88 -> £3,381,689.54 (10.3%); £3,771,292.11 -> £3,381,689.60 (10.3%); £3,771,292.35 -> £3,381,689.65 (10.3%); £3,771,292.58 -> £3,381,689.69 (10.3%); £3,771,292.81 -> £3,381,689.74 (10.3%); £3,771,293.03 -> £3,381,689.79 (10.3%); £3,771,293.26 -> £3,381,689.83 (10.3%); £3,771,293.50 -> £3,381,689.88 (10.3%); £3,771,293.73 -> £3,381,689.92 (10.3%); £3,771,293.97 -> £3,381,689.97 (10.3%); £3,771,294.20 -> £3,381,690.01 (10.3%); £3,771,294.42 -> £3,381,690.06 (10.3%); £3,771,294.60 -> £3,381,690.22 (10.3%); £3,771,294.76 -> £3,381,690.38 (10.3%); £3,771,294.94 -> £3,381,690.54 (10.3%); £3,771,295.12 -> £3,381,690.71 (10.3%); £3,771,295.35 -> £3,381,690.88 (10.3%); £3,771,295.58 -> £3,381,691.04 (10.3%); £3,771,295.76 -> £3,381,691.20 (10.3%); £3,771,295.99 -> £3,381,691.36 (10.3%); £3,771,296.23 -> £3,381,691.51 (10.3%); £3,771,296.46 -> £3,381,691.67 (10.3%); £3,771,296.70 -> £3,381,691.82 (10.3%); £3,771,296.94 -> £3,381,691.86 (10.3%); £3,771,297.17 -> £3,381,691.90 (10.3%); £3,771,297.38 -> £3,381,691.94 (10.3%); £3,771,297.58 -> £3,381,691.97 (10.3%); £3,771,297.75 -> £3,381,692.01 (10.3%); £3,771,297.91 -> £3,381,692.04 (10.3%); £3,771,298.07 -> £3,381,692.08 (10.3%); £3,771,298.23 -> £3,381,692.12 (10.3%); £3,771,298.39 -> £3,381,692.15 (10.3%); £3,771,298.55 -> £3,381,692.19 (10.3%); £3,771,298.71 -> £3,381,692.23 (10.3%); £3,771,298.87 -> £3,381,692.27 (10.3%); £3,771,299.03 -> £3,381,692.31 (10.3%); £3,771,299.19 -> £3,381,692.34 (10.3%); £3,771,299.35 -> £3,381,692.38 (10.3%); £3,771,299.52 -> £3,381,692.42 (10.3%); £3,771,299.68 -> £3,381,692.54 (10.3%); £3,771,299.84 -> £3,381,692.67 (10.3%); £3,771,300.02 -> £3,381,692.81 (10.3%); £3,771,300.22 -> £3,381,692.96 (10.3%); £3,771,300.43 -> £3,381,693.13 (10.3%); £3,771,300.67 -> £3,381,693.33 (10.3%); £3,771,300.92 -> £3,381,693.54 (10.3%); £3,771,301.20 -> £3,381,693.77 (10.3%); £3,771,301.46 -> £3,381,693.89 (10.3%); £3,771,301.73 -> £3,381,694.01 (10.3%); £3,771,302.01 -> £3,381,694.14 (10.3%); £3,771,302.27 -> £3,381,694.26 (10.3%); £3,771,302.53 -> £3,381,694.38 (10.3%); £3,771,302.80 -> £3,381,694.50 (10.3%); £3,771,303.05 -> £3,381,694.61 (10.3%); £3,771,303.31 -> £3,381,694.72 (10.3%); £3,771,303.58 -> £3,381,694.84 (10.3%); £3,771,303.84 -> £3,381,694.95 (10.3%); £3,771,304.11 -> £3,381,695.07 (10.3%); £3,771,304.38 -> £3,381,695.18 (10.3%); £3,771,304.65 -> £3,381,695.29 (10.3%); £3,771,304.92 -> £3,381,695.52 (10.3%); £3,771,305.19 -> £3,381,695.73 (10.3%); £3,771,305.46 -> £3,381,695.92 (10.3%); £3,771,305.73 -> £3,381,696.08 (10.3%); £3,771,306.01 -> £3,381,696.23 (10.3%); £3,771,306.27 -> £3,381,696.37 (10.3%); £3,771,306.48 -> £3,381,696.52 (10.3%); £3,771,306.75 -> £3,381,696.66 (10.3%); £3,771,307.02 -> £3,381,696.79 (10.3%); £3,771,307.28 -> £3,381,696.92 (10.3%); £3,771,307.55 -> £3,381,697.05 (10.3%); £3,771,307.81 -> £3,381,697.09 (10.3%); £3,771,308.09 -> £3,381,697.13 (10.3%); £3,771,308.33 -> £3,381,697.17 (10.3%); £3,771,308.56 -> £3,381,697.21 (10.3%); £3,771,308.77 -> £3,381,697.24 (10.3%); £3,771,308.93 -> £3,381,697.28 (10.3%); £3,771,309.09 -> £3,381,697.32 (10.3%); £3,771,309.25 -> £3,381,697.36 (10.3%); £3,771,309.41 -> £3,381,697.39 (10.3%); £3,771,309.56 -> £3,381,697.43 (10.3%); £3,771,309.73 -> £3,381,697.47 (10.3%); £3,771,309.88 -> £3,381,697.51 (10.3%); £3,771,310.04 -> £3,381,697.55 (10.3%); £3,771,310.20 -> £3,381,697.58 (10.3%); £3,771,310.36 -> £3,381,697.62 (10.3%); £3,771,310.52 -> £3,381,697.67 (10.3%); £3,771,310.67 -> £3,381,697.85 (10.3%); £3,771,310.83 -> £3,381,698.05 (10.3%); £3,771,311.01 -> £3,381,698.26 (10.3%); £3,771,311.20 -> £3,381,698.47 (10.3%); £3,771,311.41 -> £3,381,698.71 (10.3%); £3,771,311.64 -> £3,381,698.97 (10.3%); £3,771,311.89 -> £3,381,699.26 (10.3%); £3,771,312.16 -> £3,381,699.56 (10.3%); £3,771,312.43 -> £3,381,699.69 (10.3%); £3,771,312.70 -> £3,381,699.81 (10.3%); £3,771,312.96 -> £3,381,699.94 (10.3%); £3,771,313.23 -> £3,381,700.07 (10.3%); £3,771,313.49 -> £3,381,700.20 (10.3%); £3,771,313.75 -> £3,381,700.32 (10.3%); £3,771,314.02 -> £3,381,700.43 (10.3%); £3,771,314.28 -> £3,381,700.55 (10.3%); £3,771,314.55 -> £3,381,700.67 (10.3%); £3,771,314.83 -> £3,381,700.78 (10.3%); £3,771,315.08 -> £3,381,700.90 (10.3%); £3,771,315.35 -> £3,381,701.01 (10.3%); £3,771,315.62 -> £3,381,701.12 (10.3%); £3,771,315.82 -> £3,381,701.39 (10.3%); £3,771,316.01 -> £3,381,701.66 (10.3%); £3,771,316.28 -> £3,381,701.90 (10.3%); £3,771,316.55 -> £3,381,702.11 (10.3%); £3,771,316.75 -> £3,381,702.32 (10.3%); £3,771,316.95 -> £3,381,702.51 (10.3%); £3,771,317.14 -> £3,381,702.71 (10.3%); £3,771,317.41 -> £3,381,702.90 (10.3%); £3,771,317.67 -> £3,381,703.10 (10.3%); £3,771,317.93 -> £3,381,703.29 (10.3%); £3,771,318.18 -> £3,381,703.47 (10.3%); £3,771,318.44 -> £3,381,703.51 (10.3%); £3,771,318.71 -> £3,381,703.56 (10.3%); £3,771,318.96 -> £3,381,703.60 (10.3%); £3,771,319.17 -> £3,381,703.63 (10.3%); £3,771,319.38 -> £3,381,703.67 (10.3%); £3,771,319.54 -> £3,381,703.71 (10.3%); £3,771,319.70 -> £3,381,703.75 (10.3%); £3,771,319.86 -> £3,381,703.78 (10.3%); £3,771,320.02 -> £3,381,703.82 (10.3%); £3,771,320.18 -> £3,381,703.86 (10.3%); £3,771,320.34 -> £3,381,703.90 (10.3%); £3,771,320.49 -> £3,381,703.94 (10.3%); £3,771,320.66 -> £3,381,703.97 (10.3%); £3,771,320.81 -> £3,381,704.01 (10.3%); £3,771,320.98 -> £3,381,704.05 (10.3%); £3,771,321.13 -> £3,381,704.09 (10.3%); £3,771,321.29 -> £3,381,704.29 (10.3%); £3,771,321.45 -> £3,381,704.50 (10.3%); £3,771,321.62 -> £3,381,704.73 (10.3%); £3,771,321.82 -> £3,381,704.97 (10.3%); £3,771,322.02 -> £3,381,705.23 (10.3%); £3,771,322.25 -> £3,381,705.49 (10.3%); £3,771,322.51 -> £3,381,705.80 (10.3%); £3,771,322.78 -> £3,381,706.10 (10.3%); £3,771,323.04 -> £3,381,706.22 (10.3%); £3,771,323.31 -> £3,381,706.34 (10.3%); £3,771,323.58 -> £3,381,706.47 (10.3%); £3,771,323.84 -> £3,381,706.59 (10.3%); £3,771,324.11 -> £3,381,706.72 (10.3%); £3,771,324.37 -> £3,381,706.85 (10.3%); £3,771,324.63 -> £3,381,706.97 (10.3%); £3,771,324.88 -> £3,381,707.09 (10.3%); £3,771,325.16 -> £3,381,707.21 (10.3%); £3,771,325.42 -> £3,381,707.32 (10.3%); £3,771,325.69 -> £3,381,707.44 (10.3%); £3,771,325.95 -> £3,381,707.55 (10.3%); £3,771,326.22 -> £3,381,707.66 (10.3%); £3,771,326.48 -> £3,381,707.96 (10.3%); £3,771,326.74 -> £3,381,708.23 (10.3%); £3,771,326.95 -> £3,381,708.48 (10.3%); £3,771,327.14 -> £3,381,708.70 (10.3%); £3,771,327.35 -> £3,381,708.92 (10.3%); £3,771,327.62 -> £3,381,709.14 (10.3%); £3,771,327.88 -> £3,381,709.35 (10.3%); £3,771,328.15 -> £3,381,709.56 (10.3%); £3,771,328.41 -> £3,381,709.76 (10.3%); £3,771,328.68 -> £3,381,709.96 (10.3%); £3,771,328.94 -> £3,381,710.16 (10.3%); £3,771,329.21 -> £3,381,710.21 (10.3%); £3,771,329.48 -> £3,381,710.25 (10.3%); £3,771,329.72 -> £3,381,710.29 (10.3%); £3,771,329.94 -> £3,381,710.33 (10.3%); £3,771,330.15 -> £3,381,710.36 (10.3%); £3,771,330.31 -> £3,381,710.40 (10.3%); £3,771,330.47 -> £3,381,710.44 (10.3%); £3,771,330.63 -> £3,381,710.48 (10.3%); £3,771,330.79 -> £3,381,710.52 (10.3%); £3,771,330.94 -> £3,381,710.55 (10.3%); £3,771,331.10 -> £3,381,710.59 (10.3%); £3,771,331.26 -> £3,381,710.63 (10.3%); £3,771,331.42 -> £3,381,710.67 (10.3%); £3,771,331.58 -> £3,381,710.71 (10.3%); £3,771,331.74 -> £3,381,710.75 (10.3%); £3,771,331.90 -> £3,381,710.79 (10.3%); £3,771,332.07 -> £3,381,711.00 (10.3%); £3,771,332.23 -> £3,381,711.21 (10.3%); £3,771,332.40 -> £3,381,711.42 (10.3%); £3,771,332.59 -> £3,381,711.64 (10.3%); £3,771,332.80 -> £3,381,711.88 (10.3%); £3,771,333.02 -> £3,381,712.15 (10.3%); £3,771,333.26 -> £3,381,712.44 (10.3%); £3,771,333.53 -> £3,381,712.75 (10.3%); £3,771,333.79 -> £3,381,712.88 (10.3%); £3,771,334.05 -> £3,381,713.01 (10.3%); £3,771,334.31 -> £3,381,713.14 (10.3%); £3,771,334.58 -> £3,381,713.27 (10.3%); £3,771,334.84 -> £3,381,713.40 (10.3%); £3,771,335.11 -> £3,381,713.52 (10.3%); £3,771,335.37 -> £3,381,713.64 (10.3%); £3,771,335.65 -> £3,381,713.76 (10.3%); £3,771,335.90 -> £3,381,713.88 (10.3%); £3,771,336.17 -> £3,381,713.99 (10.3%); £3,771,336.44 -> £3,381,714.11 (10.3%); £3,771,336.71 -> £3,381,714.22 (10.3%); £3,771,336.98 -> £3,381,714.33 (10.3%); £3,771,337.24 -> £3,381,714.62 (10.3%); £3,771,337.44 -> £3,381,714.88 (10.3%); £3,771,337.64 -> £3,381,715.12 (10.3%); £3,771,337.83 -> £3,381,715.34 (10.3%); £3,771,338.03 -> £3,381,715.56 (10.3%); £3,771,338.23 -> £3,381,715.77 (10.3%); £3,771,338.50 -> £3,381,715.98 (10.3%); £3,771,338.76 -> £3,381,716.18 (10.3%); £3,771,339.02 -> £3,381,716.39 (10.3%); £3,771,339.29 -> £3,381,716.59 (10.3%); £3,771,339.55 -> £3,381,716.78 (10.3%); £3,771,339.81 -> £3,381,716.82 (10.3%); £3,771,340.08 -> £3,381,716.86 (10.3%); £3,771,340.33 -> £3,381,716.90 (10.3%); £3,771,340.55 -> £3,381,716.94 (10.3%); £3,771,340.75 -> £3,381,716.97 (10.3%); £3,771,340.91 -> £3,381,717.01 (10.3%); £3,771,341.07 -> £3,381,717.05 (10.3%); £3,771,341.23 -> £3,381,717.09 (10.3%); £3,771,341.39 -> £3,381,717.13 (10.3%); £3,771,341.54 -> £3,381,717.16 (10.3%); £3,771,341.70 -> £3,381,717.20 (10.3%); £3,771,341.86 -> £3,381,717.24 (10.3%); £3,771,342.02 -> £3,381,717.27 (10.3%); £3,771,342.19 -> £3,381,717.31 (10.3%); £3,771,342.34 -> £3,381,717.35 (10.3%); £3,771,342.50 -> £3,381,717.39 (10.3%); £3,771,342.66 -> £3,381,717.53 (10.3%); £3,771,342.81 -> £3,381,717.67 (10.3%); £3,771,342.99 -> £3,381,717.83 (10.3%); £3,771,343.19 -> £3,381,718.00 (10.3%); £3,771,343.40 -> £3,381,718.19 (10.3%); £3,771,343.63 -> £3,381,718.40 (10.3%); £3,771,343.87 -> £3,381,718.64 (10.3%); £3,771,344.15 -> £3,381,718.88 (10.3%); £3,771,344.42 -> £3,381,719.01 (10.3%); £3,771,344.70 -> £3,381,719.13 (10.3%); £3,771,344.96 -> £3,381,719.26 (10.3%); £3,771,345.23 -> £3,381,719.40 (10.3%); £3,771,345.49 -> £3,381,719.53 (10.3%); £3,771,345.76 -> £3,381,719.65 (10.3%); £3,771,346.02 -> £3,381,719.77 (10.3%); £3,771,346.29 -> £3,381,719.89 (10.3%); £3,771,346.56 -> £3,381,720.01 (10.3%); £3,771,346.81 -> £3,381,720.13 (10.3%); £3,771,347.08 -> £3,381,720.25 (10.3%); £3,771,347.34 -> £3,381,720.36 (10.3%); £3,771,347.62 -> £3,381,720.48 (10.3%); £3,771,347.89 -> £3,381,720.72 (10.3%); £3,771,348.15 -> £3,381,720.94 (10.3%); £3,771,348.42 -> £3,381,721.13 (10.3%); £3,771,348.68 -> £3,381,721.31 (10.3%); £3,771,348.94 -> £3,381,721.47 (10.3%); £3,771,349.21 -> £3,381,721.64 (10.3%); £3,771,349.47 -> £3,381,721.80 (10.3%); £3,771,349.74 -> £3,381,721.95 (10.3%); £3,771,350.01 -> £3,381,722.11 (10.3%); £3,771,350.27 -> £3,381,722.25 (10.3%); £3,771,350.53 -> £3,381,722.40 (10.3%); £3,771,350.80 -> £3,381,722.44 (10.3%); £3,771,351.07 -> £3,381,722.48 (10.3%); £3,771,351.32 -> £3,381,722.52 (10.3%); £3,771,351.55 -> £3,381,722.56 (10.3%); £3,771,351.76 -> £3,381,722.60 (10.3%); £3,771,351.89 -> £3,381,722.64 (10.3%); £3,771,352.03 -> £3,381,722.67 (10.3%); £3,771,352.17 -> £3,381,722.71 (10.3%); £3,771,352.31 -> £3,381,722.75 (10.3%); £3,771,352.45 -> £3,381,722.79 (10.3%); £3,771,352.59 -> £3,381,722.83 (10.3%); £3,771,352.73 -> £3,381,722.87 (10.3%); £3,771,352.87 -> £3,381,722.90 (10.3%); £3,771,353.01 -> £3,381,722.94 (10.3%); £3,771,353.15 -> £3,381,722.98 (10.3%); £3,771,353.29 -> £3,381,723.02 (10.3%); £3,771,353.43 -> £3,381,723.16 (10.3%); £3,771,353.57 -> £3,381,723.31 (10.3%); £3,771,353.73 -> £3,381,723.45 (10.3%); £3,771,353.90 -> £3,381,723.59 (10.3%); £3,771,354.08 -> £3,381,723.75 (10.3%); £3,771,354.28 -> £3,381,723.91 (10.3%); £3,771,354.50 -> £3,381,724.10 (10.3%); £3,771,354.73 -> £3,381,724.30 (10.3%); £3,771,354.96 -> £3,381,724.39 (10.3%); £3,771,355.20 -> £3,381,724.48 (10.3%); £3,771,355.43 -> £3,381,724.57 (10.3%); £3,771,355.66 -> £3,381,724.66 (10.3%); £3,771,355.89 -> £3,381,724.75 (10.3%); £3,771,356.12 -> £3,381,724.83 (10.3%); £3,771,356.36 -> £3,381,724.91 (10.3%); £3,771,356.59 -> £3,381,724.98 (10.3%); £3,771,356.82 -> £3,381,725.05 (10.3%); £3,771,357.05 -> £3,381,725.12 (10.3%); £3,771,357.28 -> £3,381,725.20 (10.3%); £3,771,357.52 -> £3,381,725.26 (10.3%); £3,771,357.75 -> £3,381,725.33 (10.3%); £3,771,357.98 -> £3,381,725.50 (10.3%); £3,771,358.16 -> £3,381,725.67 (10.3%); £3,771,358.40 -> £3,381,725.82 (10.3%); £3,771,358.57 -> £3,381,725.96 (10.3%); £3,771,358.74 -> £3,381,726.10 (10.3%); £3,771,358.92 -> £3,381,726.24 (10.3%); £3,771,359.09 -> £3,381,726.39 (10.3%); £3,771,359.33 -> £3,381,726.54 (10.3%); £3,771,359.56 -> £3,381,726.69 (10.3%); £3,771,359.79 -> £3,381,726.82 (10.3%); £3,771,360.01 -> £3,381,726.96 (10.3%); £3,771,360.24 -> £3,381,727.01 (10.3%); £3,771,360.48 -> £3,381,727.05 (10.3%); £3,771,360.69 -> £3,381,727.09 (10.3%); £3,771,360.88 -> £3,381,727.13 (10.3%); £3,771,361.06 -> £3,381,727.16 (10.3%); £3,771,361.20 -> £3,381,727.20 (10.3%); £3,771,361.34 -> £3,381,727.24 (10.3%); £3,771,361.48 -> £3,381,727.28 (10.3%); £3,771,361.62 -> £3,381,727.32 (10.3%); £3,771,361.76 -> £3,381,727.36 (10.3%); £3,771,361.90 -> £3,381,727.40 (10.3%); £3,771,362.04 -> £3,381,727.43 (10.3%); £3,771,362.18 -> £3,381,727.47 (10.3%); £3,771,362.32 -> £3,381,727.51 (10.3%); £3,771,362.46 -> £3,381,727.55 (10.3%); £3,771,362.60 -> £3,381,727.58 (10.3%); £3,771,362.74 -> £3,381,727.71 (10.3%); £3,771,362.89 -> £3,381,727.84 (10.3%); £3,771,363.05 -> £3,381,727.97 (10.3%); £3,771,363.21 -> £3,381,728.10 (10.3%); £3,771,363.39 -> £3,381,728.24 (10.3%); £3,771,363.59 -> £3,381,728.37 (10.3%); £3,771,363.82 -> £3,381,728.50 (10.3%); £3,771,364.05 -> £3,381,728.64 (10.3%); £3,771,364.28 -> £3,381,728.69 (10.3%); £3,771,364.52 -> £3,381,728.74 (10.3%); £3,771,364.75 -> £3,381,728.79 (10.3%); £3,771,364.99 -> £3,381,728.85 (10.3%); £3,771,365.22 -> £3,381,728.90 (10.3%); £3,771,365.46 -> £3,381,728.95 (10.3%); £3,771,365.70 -> £3,381,728.99 (10.3%); £3,771,365.94 -> £3,381,729.04 (10.3%); £3,771,366.17 -> £3,381,729.08 (10.3%); £3,771,366.41 -> £3,381,729.13 (10.3%); £3,771,366.65 -> £3,381,729.18 (10.3%); £3,771,366.88 -> £3,381,729.22 (10.3%); £3,771,367.12 -> £3,381,729.27 (10.3%); £3,771,367.35 -> £3,381,729.41 (10.3%); £3,771,367.58 -> £3,381,729.54 (10.3%); £3,771,367.75 -> £3,381,729.67 (10.3%); £3,771,367.93 -> £3,381,729.80 (10.3%); £3,771,368.11 -> £3,381,729.94 (10.3%); £3,771,368.28 -> £3,381,730.07 (10.3%); £3,771,368.46 -> £3,381,730.20 (10.3%); £3,771,368.70 -> £3,381,730.33 (10.3%); £3,771,368.93 -> £3,381,730.46 (10.3%); £3,771,369.17 -> £3,381,730.59 (10.3%); £3,771,369.40 -> £3,381,730.73 (10.3%); £3,771,369.63 -> £3,381,730.77 (10.3%); £3,771,369.87 -> £3,381,730.81 (10.3%); £3,771,370.09 -> £3,381,730.85 (10.3%); £3,771,370.29 -> £3,381,730.89 (10.3%); £3,771,370.47 -> £3,381,730.92 (10.3%); £3,771,370.63 -> £3,381,730.96 (10.3%); £3,771,370.79 -> £3,381,731.00 (10.3%); £3,771,370.96 -> £3,381,731.04 (10.3%); £3,771,371.12 -> £3,381,731.08 (10.3%); £3,771,371.28 -> £3,381,731.12 (10.3%); £3,771,371.44 -> £3,381,731.15 (10.3%); £3,771,371.61 -> £3,381,731.19 (10.3%); £3,771,371.77 -> £3,381,731.23 (10.3%); £3,771,371.94 -> £3,381,731.27 (10.3%); £3,771,372.10 -> £3,381,731.31 (10.3%); £3,771,372.26 -> £3,381,731.35 (10.3%); £3,771,372.43 -> £3,381,731.50 (10.3%); £3,771,372.59 -> £3,381,731.64 (10.3%); £3,771,372.77 -> £3,381,731.79 (10.3%); £3,771,372.98 -> £3,381,731.96 (10.3%); £3,771,373.20 -> £3,381,732.14 (10.3%); £3,771,373.44 -> £3,381,732.35 (10.3%); £3,771,373.69 -> £3,381,732.59 (10.3%); £3,771,373.95 -> £3,381,732.85 (10.3%); £3,771,374.23 -> £3,381,732.98 (10.3%); £3,771,374.50 -> £3,381,733.10 (10.3%); £3,771,374.78 -> £3,381,733.23 (10.3%); £3,771,375.05 -> £3,381,733.35 (10.3%); £3,771,375.32 -> £3,381,733.48 (10.3%); £3,771,375.59 -> £3,381,733.60 (10.3%); £3,771,375.86 -> £3,381,733.71 (10.3%); £3,771,376.12 -> £3,381,733.82 (10.3%); £3,771,376.39 -> £3,381,733.94 (10.3%); £3,771,376.65 -> £3,381,734.05 (10.3%); £3,771,376.93 -> £3,381,734.16 (10.3%); £3,771,377.21 -> £3,381,734.27 (10.3%); £3,771,377.47 -> £3,381,734.38 (10.3%); £3,771,377.68 -> £3,381,734.61 (10.3%); £3,771,377.88 -> £3,381,734.83 (10.3%); £3,771,378.08 -> £3,381,735.02 (10.3%); £3,771,378.28 -> £3,381,735.18 (10.3%); £3,771,378.49 -> £3,381,735.35 (10.3%); £3,771,378.77 -> £3,381,735.52 (10.3%); £3,771,379.04 -> £3,381,735.68 (10.3%); £3,771,379.33 -> £3,381,735.83 (10.3%); £3,771,379.60 -> £3,381,735.98 (10.3%); £3,771,379.87 -> £3,381,736.12 (10.3%); £3,771,380.14 -> £3,381,736.26 (10.3%); £3,771,380.41 -> £3,381,736.30 (10.3%); £3,771,380.68 -> £3,381,736.35 (10.3%); £3,771,380.93 -> £3,381,736.39 (10.3%); £3,771,381.16 -> £3,381,736.43 (10.3%); £3,771,381.38 -> £3,381,736.46 (10.3%); £3,771,381.55 -> £3,381,736.50 (10.3%); £3,771,381.71 -> £3,381,736.54 (10.3%); £3,771,381.88 -> £3,381,736.58 (10.3%); £3,771,382.05 -> £3,381,736.62 (10.3%); £3,771,382.22 -> £3,381,736.66 (10.3%); £3,771,382.38 -> £3,381,736.69 (10.3%); £3,771,382.55 -> £3,381,736.73 (10.3%); £3,771,382.71 -> £3,381,736.77 (10.3%); £3,771,382.87 -> £3,381,736.81 (10.3%); £3,771,383.04 -> £3,381,736.85 (10.3%); £3,771,383.21 -> £3,381,736.89 (10.3%); £3,771,383.37 -> £3,381,737.06 (10.3%); £3,771,383.54 -> £3,381,737.22 (10.3%); £3,771,383.73 -> £3,381,737.40 (10.3%); £3,771,383.93 -> £3,381,737.59 (10.3%); £3,771,384.15 -> £3,381,737.80 (10.3%); £3,771,384.38 -> £3,381,738.03 (10.3%); £3,771,384.64 -> £3,381,738.29 (10.3%); £3,771,384.91 -> £3,381,738.55 (10.3%); £3,771,385.18 -> £3,381,738.68 (10.3%); £3,771,385.46 -> £3,381,738.81 (10.3%); £3,771,385.74 -> £3,381,738.93 (10.3%); £3,771,386.02 -> £3,381,739.07 (10.3%); £3,771,386.29 -> £3,381,739.19 (10.3%); £3,771,386.56 -> £3,381,739.32 (10.3%); £3,771,386.83 -> £3,381,739.44 (10.3%); £3,771,387.11 -> £3,381,739.55 (10.3%); £3,771,387.38 -> £3,381,739.67 (10.3%); £3,771,387.66 -> £3,381,739.78 (10.3%); £3,771,387.92 -> £3,381,739.90 (10.3%); £3,771,388.19 -> £3,381,740.01 (10.3%); £3,771,388.46 -> £3,381,740.11 (10.3%); £3,771,388.67 -> £3,381,740.36 (10.3%); £3,771,388.88 -> £3,381,740.59 (10.3%); £3,771,389.08 -> £3,381,740.78 (10.3%); £3,771,389.29 -> £3,381,740.96 (10.3%); £3,771,389.49 -> £3,381,741.13 (10.3%); £3,771,389.70 -> £3,381,741.30 (10.3%); £3,771,389.91 -> £3,381,741.46 (10.3%); £3,771,390.18 -> £3,381,741.62 (10.3%); £3,771,390.45 -> £3,381,741.78 (10.3%); £3,771,390.72 -> £3,381,741.93 (10.3%); £3,771,391.00 -> £3,381,742.08 (10.3%); £3,771,391.28 -> £3,381,742.12 (10.3%); £3,771,391.54 -> £3,381,742.17 (10.3%); £3,771,391.79 -> £3,381,742.21 (10.3%); £3,771,392.03 -> £3,381,742.24 (10.3%); £3,771,392.23 -> £3,381,742.28 (10.3%); £3,771,392.40 -> £3,381,742.32 (10.3%); £3,771,392.57 -> £3,381,742.35 (10.3%); £3,771,392.73 -> £3,381,742.39 (10.3%); £3,771,392.89 -> £3,381,742.43 (10.3%); £3,771,393.06 -> £3,381,742.47 (10.3%); £3,771,393.23 -> £3,381,742.50 (10.3%); £3,771,393.39 -> £3,381,742.54 (10.3%); £3,771,393.56 -> £3,381,742.58 (10.3%); £3,771,393.72 -> £3,381,742.62 (10.3%); £3,771,393.89 -> £3,381,742.66 (10.3%); £3,771,394.05 -> £3,381,742.70 (10.3%); £3,771,394.22 -> £3,381,742.92 (10.3%); £3,771,394.38 -> £3,381,743.16 (10.3%); £3,771,394.57 -> £3,381,743.41 (10.3%); £3,771,394.77 -> £3,381,743.66 (10.3%); £3,771,395.00 -> £3,381,743.94 (10.3%); £3,771,395.24 -> £3,381,744.24 (10.3%); £3,771,395.49 -> £3,381,744.55 (10.3%); £3,771,395.77 -> £3,381,744.88 (10.3%); £3,771,396.06 -> £3,381,745.00 (10.3%); £3,771,396.34 -> £3,381,745.12 (10.3%); £3,771,396.62 -> £3,381,745.25 (10.3%); £3,771,396.90 -> £3,381,745.38 (10.3%); £3,771,397.17 -> £3,381,745.50 (10.3%); £3,771,397.45 -> £3,381,745.63 (10.3%); £3,771,397.72 -> £3,381,745.75 (10.3%); £3,771,397.99 -> £3,381,745.86 (10.3%); £3,771,398.26 -> £3,381,745.98 (10.3%); £3,771,398.55 -> £3,381,746.09 (10.3%); £3,771,398.81 -> £3,381,746.21 (10.3%); £3,771,399.09 -> £3,381,746.32 (10.3%); £3,771,399.37 -> £3,381,746.43 (10.3%); £3,771,399.58 -> £3,381,746.74 (10.3%); £3,771,399.78 -> £3,381,747.04 (10.3%); £3,771,400.06 -> £3,381,747.30 (10.3%); £3,771,400.26 -> £3,381,747.54 (10.3%); £3,771,400.46 -> £3,381,747.78 (10.3%); £3,771,400.67 -> £3,381,748.02 (10.3%); £3,771,400.94 -> £3,381,748.26 (10.3%); £3,771,401.22 -> £3,381,748.50 (10.3%); £3,771,401.48 -> £3,381,748.73 (10.3%); £3,771,401.76 -> £3,381,748.96 (10.3%); £3,771,402.03 -> £3,381,749.17 (10.3%); £3,771,402.31 -> £3,381,749.21 (10.3%); £3,771,402.59 -> £3,381,749.25 (10.3%); £3,771,402.85 -> £3,381,749.29 (10.3%); £3,771,403.09 -> £3,381,749.33 (10.3%); £3,771,403.30 -> £3,381,749.36 (10.3%); £3,771,403.47 -> £3,381,749.40 (10.3%); £3,771,403.63 -> £3,381,749.44 (10.3%); £3,771,403.80 -> £3,381,749.48 (10.3%); £3,771,403.96 -> £3,381,749.51 (10.3%); £3,771,404.13 -> £3,381,749.55 (10.3%); £3,771,404.30 -> £3,381,749.59 (10.3%); £3,771,404.46 -> £3,381,749.62 (10.3%); £3,771,404.63 -> £3,381,749.66 (10.3%); £3,771,404.79 -> £3,381,749.70 (10.3%); £3,771,404.95 -> £3,381,749.74 (10.3%); £3,771,405.11 -> £3,381,749.78 (10.3%); £3,771,405.28 -> £3,381,750.02 (10.3%); £3,771,405.44 -> £3,381,750.26 (10.3%); £3,771,405.63 -> £3,381,750.51 (10.3%); £3,771,405.83 -> £3,381,750.78 (10.3%); £3,771,406.05 -> £3,381,751.08 (10.3%); £3,771,406.29 -> £3,381,751.40 (10.3%); £3,771,406.55 -> £3,381,751.74 (10.3%); £3,771,406.83 -> £3,381,752.08 (10.3%); £3,771,407.10 -> £3,381,752.20 (10.3%); £3,771,407.38 -> £3,381,752.32 (10.3%); £3,771,407.65 -> £3,381,752.45 (10.3%); £3,771,407.93 -> £3,381,752.58 (10.3%); £3,771,408.21 -> £3,381,752.70 (10.3%); £3,771,408.47 -> £3,381,752.83 (10.3%); £3,771,408.75 -> £3,381,752.94 (10.3%); £3,771,409.03 -> £3,381,753.05 (10.3%); £3,771,409.30 -> £3,381,753.16 (10.3%); £3,771,409.57 -> £3,381,753.28 (10.3%); £3,771,409.85 -> £3,381,753.39 (10.3%); £3,771,410.12 -> £3,381,753.50 (10.3%); £3,771,410.39 -> £3,381,753.61 (10.3%); £3,771,410.59 -> £3,381,753.94 (10.3%); £3,771,410.88 -> £3,381,754.25 (10.3%); £3,771,411.08 -> £3,381,754.54 (10.3%); £3,771,411.35 -> £3,381,754.81 (10.3%); £3,771,411.62 -> £3,381,755.07 (10.3%); £3,771,411.89 -> £3,381,755.32 (10.3%); £3,771,412.16 -> £3,381,755.58 (10.3%); £3,771,412.44 -> £3,381,755.82 (10.3%); £3,771,412.72 -> £3,381,756.06 (10.3%); £3,771,413.00 -> £3,381,756.29 (10.3%); £3,771,413.27 -> £3,381,756.53 (10.3%); £3,771,413.56 -> £3,381,756.57 (10.3%); £3,771,413.83 -> £3,381,756.61 (10.3%); £3,771,414.08 -> £3,381,756.65 (10.3%); £3,771,414.32 -> £3,381,756.69 (10.3%); £3,771,414.53 -> £3,381,756.73 (10.3%); £3,771,414.70 -> £3,381,756.76 (10.3%); £3,771,414.86 -> £3,381,756.80 (10.3%); £3,771,415.03 -> £3,381,756.84 (10.3%); £3,771,415.19 -> £3,381,756.87 (10.3%); £3,771,415.35 -> £3,381,756.91 (10.3%); £3,771,415.52 -> £3,381,756.95 (10.3%); £3,771,415.68 -> £3,381,756.98 (10.3%); £3,771,415.84 -> £3,381,757.02 (10.3%); £3,771,416.01 -> £3,381,757.06 (10.3%); £3,771,416.17 -> £3,381,757.10 (10.3%); £3,771,416.33 -> £3,381,757.14 (10.3%); £3,771,416.51 -> £3,381,757.33 (10.3%); £3,771,416.67 -> £3,381,757.53 (10.3%); £3,771,416.85 -> £3,381,757.73 (10.3%); £3,771,417.05 -> £3,381,757.95 (10.3%); £3,771,417.27 -> £3,381,758.19 (10.3%); £3,771,417.49 -> £3,381,758.45 (10.3%); £3,771,417.75 -> £3,381,758.74 (10.3%); £3,771,418.02 -> £3,381,759.04 (10.3%); £3,771,418.29 -> £3,381,759.17 (10.3%); £3,771,418.57 -> £3,381,759.31 (10.3%); £3,771,418.83 -> £3,381,759.44 (10.3%); £3,771,419.11 -> £3,381,759.58 (10.3%); £3,771,419.37 -> £3,381,759.72 (10.3%); £3,771,419.63 -> £3,381,759.85 (10.3%); £3,771,419.90 -> £3,381,759.98 (10.3%); £3,771,420.16 -> £3,381,760.11 (10.3%); £3,771,420.44 -> £3,381,760.22 (10.3%); £3,771,420.73 -> £3,381,760.34 (10.3%); £3,771,420.99 -> £3,381,760.46 (10.3%); £3,771,421.27 -> £3,381,760.57 (10.3%); £3,771,421.53 -> £3,381,760.68 (10.3%); £3,771,421.80 -> £3,381,760.97 (10.3%); £3,771,422.07 -> £3,381,761.25 (10.3%); £3,771,422.35 -> £3,381,761.49 (10.3%); £3,771,422.63 -> £3,381,761.71 (10.3%); £3,771,422.90 -> £3,381,761.91 (10.3%); £3,771,423.10 -> £3,381,762.12 (10.3%); £3,771,423.31 -> £3,381,762.32 (10.3%); £3,771,423.58 -> £3,381,762.51 (10.3%); £3,771,423.85 -> £3,381,762.71 (10.3%); £3,771,424.11 -> £3,381,762.91 (10.3%); £3,771,424.38 -> £3,381,763.09 (10.3%); £3,771,424.66 -> £3,381,763.13 (10.3%); £3,771,424.92 -> £3,381,763.17 (10.3%); £3,771,425.17 -> £3,381,763.21 (10.3%); £3,771,425.41 -> £3,381,763.25 (10.3%); £3,771,425.62 -> £3,381,763.29 (10.3%); £3,771,425.77 -> £3,381,763.32 (10.3%); £3,771,425.91 -> £3,381,763.36 (10.3%); £3,771,426.06 -> £3,381,763.40 (10.3%); £3,771,426.20 -> £3,381,763.44 (10.3%); £3,771,426.34 -> £3,381,763.47 (10.3%); £3,771,426.48 -> £3,381,763.51 (10.3%); £3,771,426.62 -> £3,381,763.54 (10.3%); £3,771,426.76 -> £3,381,763.58 (10.3%); £3,771,426.90 -> £3,381,763.62 (10.3%); £3,771,427.05 -> £3,381,763.65 (10.3%); £3,771,427.19 -> £3,381,763.69 (10.3%); £3,771,427.33 -> £3,381,763.87 (10.3%); £3,771,427.48 -> £3,381,764.05 (10.3%); £3,771,427.64 -> £3,381,764.23 (10.3%); £3,771,427.82 -> £3,381,764.42 (10.3%); £3,771,428.01 -> £3,381,764.62 (10.3%); £3,771,428.22 -> £3,381,764.84 (10.3%); £3,771,428.44 -> £3,381,765.08 (10.3%); £3,771,428.67 -> £3,381,765.33 (10.3%); £3,771,428.91 -> £3,381,765.42 (10.3%); £3,771,429.15 -> £3,381,765.51 (10.3%); £3,771,429.39 -> £3,381,765.60 (10.3%); £3,771,429.64 -> £3,381,765.69 (10.3%); £3,771,429.87 -> £3,381,765.78 (10.3%); £3,771,430.10 -> £3,381,765.86 (10.3%); £3,771,430.34 -> £3,381,765.93 (10.3%); £3,771,430.58 -> £3,381,766.00 (10.3%); £3,771,430.82 -> £3,381,766.08 (10.3%); £3,771,431.06 -> £3,381,766.14 (10.3%); £3,771,431.30 -> £3,381,766.21 (10.3%); £3,771,431.53 -> £3,381,766.28 (10.3%); £3,771,431.78 -> £3,381,766.35 (10.3%); £3,771,432.02 -> £3,381,766.57 (10.3%); £3,771,432.25 -> £3,381,766.79 (10.3%); £3,771,432.49 -> £3,381,766.98 (10.3%); £3,771,432.67 -> £3,381,767.17 (10.3%); £3,771,432.90 -> £3,381,767.36 (10.3%); £3,771,433.08 -> £3,381,767.54 (10.3%); £3,771,433.26 -> £3,381,767.73 (10.3%); £3,771,433.51 -> £3,381,767.92 (10.3%); £3,771,433.75 -> £3,381,768.11 (10.3%); £3,771,433.99 -> £3,381,768.30 (10.3%); £3,771,434.23 -> £3,381,768.48 (10.3%); £3,771,434.47 -> £3,381,768.52 (10.3%); £3,771,434.71 -> £3,381,768.56 (10.3%); £3,771,434.93 -> £3,381,768.60 (10.3%); £3,771,435.14 -> £3,381,768.64 (10.3%); £3,771,435.33 -> £3,381,768.68 (10.3%); £3,771,435.47 -> £3,381,768.71 (10.3%); £3,771,435.61 -> £3,381,768.75 (10.3%); £3,771,435.74 -> £3,381,768.79 (10.3%); £3,771,435.88 -> £3,381,768.83 (10.3%); £3,771,436.02 -> £3,381,768.86 (10.3%); £3,771,436.17 -> £3,381,768.90 (10.3%); £3,771,436.31 -> £3,381,768.94 (10.3%); £3,771,436.45 -> £3,381,768.97 (10.3%); £3,771,436.59 -> £3,381,769.01 (10.3%); £3,771,436.73 -> £3,381,769.04 (10.3%); £3,771,436.87 -> £3,381,769.08 (10.3%); £3,771,437.01 -> £3,381,769.27 (10.3%); £3,771,437.14 -> £3,381,769.46 (10.3%); £3,771,437.30 -> £3,381,769.64 (10.3%); £3,771,437.46 -> £3,381,769.83 (10.3%); £3,771,437.65 -> £3,381,770.02 (10.3%); £3,771,437.86 -> £3,381,770.21 (10.3%); £3,771,438.08 -> £3,381,770.41 (10.3%); £3,771,438.32 -> £3,381,770.61 (10.3%); £3,771,438.55 -> £3,381,770.66 (10.3%); £3,771,438.79 -> £3,381,770.70 (10.3%); £3,771,439.02 -> £3,381,770.75 (10.3%); £3,771,439.25 -> £3,381,770.80 (10.3%); £3,771,439.49 -> £3,381,770.85 (10.3%); £3,771,439.73 -> £3,381,770.90 (10.3%); £3,771,439.96 -> £3,381,770.95 (10.3%); £3,771,440.20 -> £3,381,770.99 (10.3%); £3,771,440.43 -> £3,381,771.04 (10.3%); £3,771,440.67 -> £3,381,771.09 (10.3%); £3,771,440.90 -> £3,381,771.13 (10.3%); £3,771,441.13 -> £3,381,771.18 (10.3%); £3,771,441.36 -> £3,381,771.23 (10.3%); £3,771,441.60 -> £3,381,771.42 (10.3%); £3,771,441.83 -> £3,381,771.61 (10.3%); £3,771,442.01 -> £3,381,771.80 (10.3%); £3,771,442.18 -> £3,381,771.99 (10.3%); £3,771,442.36 -> £3,381,772.17 (10.3%); £3,771,442.54 -> £3,381,772.36 (10.3%); £3,771,442.72 -> £3,381,772.56 (10.3%); £3,771,442.95 -> £3,381,772.75 (10.3%); £3,771,443.18 -> £3,381,772.94 (10.3%); £3,771,443.41 -> £3,381,773.13 (10.3%); £3,771,443.65 -> £3,381,773.31 (10.3%); £3,771,443.88 -> £3,381,773.35 (10.3%); £3,771,444.12 -> £3,381,773.38 (10.3%); £3,771,444.34 -> £3,381,773.42 (10.3%); £3,771,444.54 -> £3,381,773.46 (10.3%); £3,771,444.72 -> £3,381,773.49 (10.3%); £3,771,444.88 -> £3,381,773.53 (10.3%); £3,771,445.03 -> £3,381,773.57 (10.3%); £3,771,445.19 -> £3,381,773.61 (10.3%); £3,771,445.34 -> £3,381,773.64 (10.3%); £3,771,445.50 -> £3,381,773.68 (10.3%); £3,771,445.65 -> £3,381,773.72 (10.3%); £3,771,445.81 -> £3,381,773.75 (10.3%); £3,771,445.97 -> £3,381,773.79 (10.3%); £3,771,446.12 -> £3,381,773.83 (10.3%); £3,771,446.27 -> £3,381,773.87 (10.3%); £3,771,446.43 -> £3,381,773.91 (10.3%); £3,771,446.58 -> £3,381,774.12 (10.3%); £3,771,446.74 -> £3,381,774.34 (10.3%); £3,771,446.91 -> £3,381,774.57 (10.3%); £3,771,447.10 -> £3,381,774.80 (10.3%); £3,771,447.32 -> £3,381,775.05 (10.3%); £3,771,447.54 -> £3,381,775.34 (10.3%); £3,771,447.78 -> £3,381,775.65 (10.3%); £3,771,448.04 -> £3,381,775.97 (10.3%); £3,771,448.30 -> £3,381,776.10 (10.3%); £3,771,448.55 -> £3,381,776.22 (10.3%); £3,771,448.81 -> £3,381,776.35 (10.3%); £3,771,449.07 -> £3,381,776.48 (10.3%); £3,771,449.33 -> £3,381,776.61 (10.3%); £3,771,449.59 -> £3,381,776.74 (10.3%); £3,771,449.85 -> £3,381,776.85 (10.3%); £3,771,450.11 -> £3,381,776.97 (10.3%); £3,771,450.37 -> £3,381,777.09 (10.3%); £3,771,450.63 -> £3,381,777.21 (10.3%); £3,771,450.88 -> £3,381,777.32 (10.3%); £3,771,451.15 -> £3,381,777.44 (10.3%); £3,771,451.41 -> £3,381,777.54 (10.3%); £3,771,451.61 -> £3,381,777.84 (10.3%); £3,771,451.80 -> £3,381,778.12 (10.3%); £3,771,451.99 -> £3,381,778.37 (10.3%); £3,771,452.18 -> £3,381,778.60 (10.3%); £3,771,452.38 -> £3,381,778.82 (10.3%); £3,771,452.57 -> £3,381,779.04 (10.3%); £3,771,452.76 -> £3,381,779.25 (10.3%); £3,771,453.03 -> £3,381,779.46 (10.3%); £3,771,453.28 -> £3,381,779.68 (10.3%); £3,771,453.54 -> £3,381,779.88 (10.3%); £3,771,453.80 -> £3,381,780.09 (10.3%); £3,771,454.06 -> £3,381,780.13 (10.3%); £3,771,454.32 -> £3,381,780.17 (10.3%); £3,771,454.56 -> £3,381,780.21 (10.3%); £3,771,454.78 -> £3,381,780.25 (10.3%); £3,771,454.98 -> £3,381,780.28 (10.3%); £3,771,455.14 -> £3,381,780.32 (10.3%); £3,771,455.30 -> £3,381,780.36 (10.3%); £3,771,455.46 -> £3,381,780.40 (10.3%); £3,771,455.62 -> £3,381,780.43 (10.3%); £3,771,455.77 -> £3,381,780.47 (10.3%); £3,771,455.93 -> £3,381,780.50 (10.3%); £3,771,456.08 -> £3,381,780.54 (10.3%); £3,771,456.23 -> £3,381,780.58 (10.3%); £3,771,456.39 -> £3,381,780.62 (10.3%); £3,771,456.55 -> £3,381,780.66 (10.3%); £3,771,456.70 -> £3,381,780.70 (10.3%); £3,771,456.86 -> £3,381,780.88 (10.3%); £3,771,457.02 -> £3,381,781.06 (10.3%); £3,771,457.19 -> £3,381,781.26 (10.3%); £3,771,457.38 -> £3,381,781.47 (10.3%); £3,771,457.60 -> £3,381,781.70 (10.3%); £3,771,457.83 -> £3,381,781.95 (10.3%); £3,771,458.06 -> £3,381,782.23 (10.3%); £3,771,458.32 -> £3,381,782.52 (10.3%); £3,771,458.58 -> £3,381,782.64 (10.3%); £3,771,458.83 -> £3,381,782.77 (10.3%); £3,771,459.09 -> £3,381,782.90 (10.3%); £3,771,459.35 -> £3,381,783.03 (10.3%); £3,771,459.61 -> £3,381,783.15 (10.3%); £3,771,459.87 -> £3,381,783.28 (10.3%); £3,771,460.13 -> £3,381,783.40 (10.3%); £3,771,460.40 -> £3,381,783.52 (10.3%); £3,771,460.66 -> £3,381,783.63 (10.3%); £3,771,460.92 -> £3,381,783.75 (10.3%); £3,771,461.18 -> £3,381,783.87 (10.3%); £3,771,461.43 -> £3,381,783.98 (10.3%); £3,771,461.69 -> £3,381,784.09 (10.3%); £3,771,461.94 -> £3,381,784.38 (10.3%); £3,771,462.21 -> £3,381,784.64 (10.3%); £3,771,462.46 -> £3,381,784.88 (10.3%); £3,771,462.73 -> £3,381,785.09 (10.3%); £3,771,462.98 -> £3,381,785.30 (10.3%); £3,771,463.23 -> £3,381,785.50 (10.3%); £3,771,463.49 -> £3,381,785.70 (10.3%); £3,771,463.75 -> £3,381,785.89 (10.3%); £3,771,464.01 -> £3,381,786.08 (10.3%); £3,771,464.27 -> £3,381,786.27 (10.3%); £3,771,464.53 -> £3,381,786.44 (10.3%); £3,771,464.80 -> £3,381,786.48 (10.3%); £3,771,465.06 -> £3,381,786.52 (10.3%); £3,771,465.30 -> £3,381,786.56 (10.3%); £3,771,465.52 -> £3,381,786.60 (10.3%); £3,771,465.72 -> £3,381,786.63 (10.3%); £3,771,465.88 -> £3,381,786.67 (10.3%); £3,771,466.03 -> £3,381,786.71 (10.3%); £3,771,466.19 -> £3,381,786.75 (10.3%); £3,771,466.34 -> £3,381,786.78 (10.3%); £3,771,466.49 -> £3,381,786.82 (10.3%); £3,771,466.64 -> £3,381,786.86 (10.3%); £3,771,466.80 -> £3,381,786.90 (10.3%); £3,771,466.95 -> £3,381,786.93 (10.3%); £3,771,467.11 -> £3,381,786.97 (10.3%); £3,771,467.27 -> £3,381,787.01 (10.3%); £3,771,467.42 -> £3,381,787.05 (10.3%); £3,771,467.58 -> £3,381,787.17 (10.3%); £3,771,467.74 -> £3,381,787.30 (10.3%); £3,771,467.92 -> £3,381,787.44 (10.3%); £3,771,468.11 -> £3,381,787.59 (10.3%); £3,771,468.32 -> £3,381,787.76 (10.3%); £3,771,468.54 -> £3,381,787.96 (10.3%); £3,771,468.78 -> £3,381,788.17 (10.3%); £3,771,469.04 -> £3,381,788.40 (10.3%); £3,771,469.30 -> £3,381,788.53 (10.3%); £3,771,469.56 -> £3,381,788.66 (10.3%); £3,771,469.82 -> £3,381,788.79 (10.3%); £3,771,470.08 -> £3,381,788.92 (10.3%); £3,771,470.34 -> £3,381,789.05 (10.3%); £3,771,470.58 -> £3,381,789.17 (10.3%); £3,771,470.83 -> £3,381,789.28 (10.3%); £3,771,471.10 -> £3,381,789.40 (10.3%); £3,771,471.36 -> £3,381,789.52 (10.3%); £3,771,471.62 -> £3,381,789.63 (10.3%); £3,771,471.88 -> £3,381,789.75 (10.3%); £3,771,472.14 -> £3,381,789.86 (10.3%); £3,771,472.41 -> £3,381,789.97 (10.3%); £3,771,472.66 -> £3,381,790.19 (10.3%); £3,771,472.85 -> £3,381,790.39 (10.3%); £3,771,473.05 -> £3,381,790.56 (10.3%); £3,771,473.24 -> £3,381,790.72 (10.3%); £3,771,473.50 -> £3,381,790.86 (10.3%); £3,771,473.75 -> £3,381,791.01 (10.3%); £3,771,474.00 -> £3,381,791.15 (10.3%); £3,771,474.27 -> £3,381,791.29 (10.3%); £3,771,474.54 -> £3,381,791.43 (10.3%); £3,771,474.80 -> £3,381,791.55 (10.3%); £3,771,475.06 -> £3,381,791.68 (10.3%); £3,771,475.31 -> £3,381,791.72 (10.3%); £3,771,475.57 -> £3,381,791.76 (10.3%); £3,771,475.81 -> £3,381,791.80 (10.3%); £3,771,476.03 -> £3,381,791.84 (10.3%); £3,771,476.23 -> £3,381,791.88 (10.3%); £3,771,476.39 -> £3,381,791.91 (10.3%); £3,771,476.54 -> £3,381,791.95 (10.3%); £3,771,476.70 -> £3,381,791.99 (10.3%); £3,771,476.85 -> £3,381,792.03 (10.3%); £3,771,477.01 -> £3,381,792.06 (10.3%); £3,771,477.16 -> £3,381,792.10 (10.3%); £3,771,477.32 -> £3,381,792.14 (10.3%); £3,771,477.49 -> £3,381,792.18 (10.3%); £3,771,477.65 -> £3,381,792.22 (10.3%); £3,771,477.81 -> £3,381,792.25 (10.3%); £3,771,477.96 -> £3,381,792.29 (10.3%); £3,771,478.12 -> £3,381,792.39 (10.3%); £3,771,478.27 -> £3,381,792.49 (10.3%); £3,771,478.44 -> £3,381,792.60 (10.3%); £3,771,478.63 -> £3,381,792.73 (10.3%); £3,771,478.85 -> £3,381,792.88 (10.3%); £3,771,479.07 -> £3,381,793.05 (10.3%); £3,771,479.32 -> £3,381,793.24 (10.3%); £3,771,479.58 -> £3,381,793.45 (10.3%); £3,771,479.85 -> £3,381,793.57 (10.3%); £3,771,480.11 -> £3,381,793.70 (10.3%); £3,771,480.38 -> £3,381,793.83 (10.3%); £3,771,480.64 -> £3,381,793.96 (10.3%); £3,771,480.90 -> £3,381,794.09 (10.3%); £3,771,481.16 -> £3,381,794.22 (10.3%); £3,771,481.42 -> £3,381,794.34 (10.3%); £3,771,481.69 -> £3,381,794.45 (10.3%); £3,771,481.95 -> £3,381,794.57 (10.3%); £3,771,482.20 -> £3,381,794.69 (10.3%); £3,771,482.45 -> £3,381,794.80 (10.3%); £3,771,482.72 -> £3,381,794.91 (10.3%); £3,771,482.98 -> £3,381,795.02 (10.3%); £3,771,483.23 -> £3,381,795.22 (10.3%); £3,771,483.50 -> £3,381,795.41 (10.3%); £3,771,483.76 -> £3,381,795.56 (10.3%); £3,771,484.01 -> £3,381,795.70 (10.3%); £3,771,484.28 -> £3,381,795.82 (10.3%); £3,771,484.54 -> £3,381,795.94 (10.3%); £3,771,484.81 -> £3,381,796.06 (10.3%); £3,771,485.06 -> £3,381,796.18 (10.3%); £3,771,485.32 -> £3,381,796.29 (10.3%); £3,771,485.57 -> £3,381,796.39 (10.3%); £3,771,485.83 -> £3,381,796.49 (10.3%); £3,771,486.08 -> £3,381,796.53 (10.3%); £3,771,486.34 -> £3,381,796.57 (10.3%); £3,771,486.58 -> £3,381,796.61 (10.3%); £3,771,486.80 -> £3,381,796.65 (10.3%); £3,771,487.01 -> £3,381,796.68 (10.3%); £3,771,487.16 -> £3,381,796.72 (10.3%); £3,771,487.32 -> £3,381,796.76 (10.3%); £3,771,487.47 -> £3,381,796.79 (10.3%); £3,771,487.63 -> £3,381,796.83 (10.3%); £3,771,487.79 -> £3,381,796.87 (10.3%); £3,771,487.95 -> £3,381,796.91 (10.3%); £3,771,488.11 -> £3,381,796.94 (10.3%); £3,771,488.26 -> £3,381,796.98 (10.3%); £3,771,488.42 -> £3,381,797.02 (10.3%); £3,771,488.59 -> £3,381,797.06 (10.3%); £3,771,488.74 -> £3,381,797.10 (10.3%); £3,771,488.90 -> £3,381,797.24 (10.3%); £3,771,489.06 -> £3,381,797.38 (10.3%); £3,771,489.24 -> £3,381,797.53 (10.3%); £3,771,489.43 -> £3,381,797.70 (10.3%); £3,771,489.65 -> £3,381,797.89 (10.3%); £3,771,489.87 -> £3,381,798.09 (10.3%); £3,771,490.12 -> £3,381,798.32 (10.3%); £3,771,490.39 -> £3,381,798.55 (10.3%); £3,771,490.65 -> £3,381,798.68 (10.3%); £3,771,490.92 -> £3,381,798.81 (10.3%); £3,771,491.17 -> £3,381,798.94 (10.3%); £3,771,491.42 -> £3,381,799.07 (10.3%); £3,771,491.69 -> £3,381,799.19 (10.3%); £3,771,491.95 -> £3,381,799.31 (10.3%); £3,771,492.20 -> £3,381,799.43 (10.3%); £3,771,492.46 -> £3,381,799.54 (10.3%); £3,771,492.72 -> £3,381,799.65 (10.3%); £3,771,492.98 -> £3,381,799.77 (10.3%); £3,771,493.24 -> £3,381,799.88 (10.3%); £3,771,493.51 -> £3,381,799.99 (10.3%); £3,771,493.76 -> £3,381,800.09 (10.3%); £3,771,493.96 -> £3,381,800.33 (10.3%); £3,771,494.24 -> £3,381,800.55 (10.3%); £3,771,494.43 -> £3,381,800.73 (10.3%); £3,771,494.62 -> £3,381,800.89 (10.3%); £3,771,494.82 -> £3,381,801.05 (10.3%); £3,771,495.01 -> £3,381,801.20 (10.3%); £3,771,495.20 -> £3,381,801.35 (10.3%); £3,771,495.46 -> £3,381,801.49 (10.3%); £3,771,495.72 -> £3,381,801.63 (10.3%); £3,771,495.98 -> £3,381,801.78 (10.3%); £3,771,496.25 -> £3,381,801.91 (10.3%); £3,771,496.52 -> £3,381,801.96 (10.3%); £3,771,496.79 -> £3,381,802.00 (10.3%); £3,771,497.03 -> £3,381,802.04 (10.3%); £3,771,497.25 -> £3,381,802.07 (10.3%); £3,771,497.45 -> £3,381,802.11 (10.3%); £3,771,497.58 -> £3,381,802.15 (10.3%); £3,771,497.73 -> £3,381,802.19 (10.3%); £3,771,497.86 -> £3,381,802.22 (10.3%); £3,771,498.00 -> £3,381,802.26 (10.3%); £3,771,498.14 -> £3,381,802.30 (10.3%); £3,771,498.28 -> £3,381,802.34 (10.3%); £3,771,498.41 -> £3,381,802.37 (10.3%); £3,771,498.56 -> £3,381,802.41 (10.3%); £3,771,498.69 -> £3,381,802.45 (10.3%); £3,771,498.83 -> £3,381,802.49 (10.3%); £3,771,498.96 -> £3,381,802.53 (10.3%); £3,771,499.10 -> £3,381,802.64 (10.3%); £3,771,499.24 -> £3,381,802.76 (10.3%); £3,771,499.40 -> £3,381,802.89 (10.3%); £3,771,499.57 -> £3,381,803.01 (10.3%); £3,771,499.75 -> £3,381,803.15 (10.3%); £3,771,499.95 -> £3,381,803.29 (10.3%); £3,771,500.16 -> £3,381,803.47 (10.3%); £3,771,500.38 -> £3,381,803.65 (10.3%); £3,771,500.61 -> £3,381,803.74 (10.3%); £3,771,500.83 -> £3,381,803.83 (10.3%); £3,771,501.05 -> £3,381,803.93 (10.3%); £3,771,501.28 -> £3,381,804.02 (10.3%); £3,771,501.52 -> £3,381,804.10 (10.3%); £3,771,501.75 -> £3,381,804.18 (10.3%); £3,771,501.98 -> £3,381,804.26 (10.3%); £3,771,502.20 -> £3,381,804.33 (10.3%); £3,771,502.42 -> £3,381,804.40 (10.3%); £3,771,502.65 -> £3,381,804.47 (10.3%); £3,771,502.88 -> £3,381,804.54 (10.3%); £3,771,503.11 -> £3,381,804.61 (10.3%); £3,771,503.33 -> £3,381,804.67 (10.3%); £3,771,503.50 -> £3,381,804.83 (10.3%); £3,771,503.68 -> £3,381,804.98 (10.3%); £3,771,503.85 -> £3,381,805.12 (10.3%); £3,771,504.02 -> £3,381,805.25 (10.3%); £3,771,504.19 -> £3,381,805.38 (10.3%); £3,771,504.37 -> £3,381,805.51 (10.3%); £3,771,504.53 -> £3,381,805.64 (10.3%); £3,771,504.76 -> £3,381,805.76 (10.3%); £3,771,504.99 -> £3,381,805.89 (10.3%); £3,771,505.22 -> £3,381,806.02 (10.3%); £3,771,505.45 -> £3,381,806.14 (10.3%); £3,771,505.67 -> £3,381,806.18 (10.3%); £3,771,505.91 -> £3,381,806.22 (10.3%); £3,771,506.12 -> £3,381,806.26 (10.3%); £3,771,506.31 -> £3,381,806.29 (10.3%); £3,771,506.48 -> £3,381,806.33 (10.3%); £3,771,506.62 -> £3,381,806.37 (10.3%); £3,771,506.76 -> £3,381,806.41 (10.3%); £3,771,506.90 -> £3,381,806.45 (10.3%); £3,771,507.04 -> £3,381,806.48 (10.3%); £3,771,507.18 -> £3,381,806.52 (10.3%); £3,771,507.31 -> £3,381,806.56 (10.3%); £3,771,507.45 -> £3,381,806.59 (10.3%); £3,771,507.59 -> £3,381,806.63 (10.3%); £3,771,507.73 -> £3,381,806.66 (10.3%); £3,771,507.87 -> £3,381,806.70 (10.3%); £3,771,508.00 -> £3,381,806.74 (10.3%); £3,771,508.14 -> £3,381,806.85 (10.3%); £3,771,508.28 -> £3,381,806.97 (10.3%); £3,771,508.44 -> £3,381,807.08 (10.3%); £3,771,508.60 -> £3,381,807.20 (10.3%); £3,771,508.79 -> £3,381,807.32 (10.3%); £3,771,508.98 -> £3,381,807.44 (10.3%); £3,771,509.20 -> £3,381,807.56 (10.3%); £3,771,509.43 -> £3,381,807.69 (10.3%); £3,771,509.66 -> £3,381,807.74 (10.3%); £3,771,509.89 -> £3,381,807.78 (10.3%); £3,771,510.12 -> £3,381,807.83 (10.3%); £3,771,510.35 -> £3,381,807.88 (10.3%); £3,771,510.58 -> £3,381,807.93 (10.3%); £3,771,510.80 -> £3,381,807.98 (10.3%); £3,771,511.04 -> £3,381,808.03 (10.3%); £3,771,511.26 -> £3,381,808.08 (10.3%); £3,771,511.49 -> £3,381,808.12 (10.3%); £3,771,511.72 -> £3,381,808.17 (10.3%); £3,771,511.96 -> £3,381,808.22 (10.3%); £3,771,512.19 -> £3,381,808.26 (10.3%); £3,771,512.41 -> £3,381,808.31 (10.3%); £3,771,512.65 -> £3,381,808.44 (10.3%); £3,771,512.89 -> £3,381,808.57 (10.3%); £3,771,513.12 -> £3,381,808.70 (10.3%); £3,771,513.28 -> £3,381,808.83 (10.3%); £3,771,513.51 -> £3,381,808.96 (10.3%); £3,771,513.68 -> £3,381,809.09 (10.3%); £3,771,513.85 -> £3,381,809.22 (10.3%); £3,771,514.08 -> £3,381,809.35 (10.3%); £3,771,514.32 -> £3,381,809.47 (10.3%); £3,771,514.54 -> £3,381,809.60 (10.3%); £3,771,514.77 -> £3,381,809.72 (10.3%); £3,771,514.99 -> £3,381,809.76 (10.3%); £3,771,515.22 -> £3,381,809.80 (10.3%); £3,771,515.43 -> £3,381,809.84 (10.3%); £3,771,515.62 -> £3,381,809.88 (10.3%); £3,771,515.80 -> £3,381,809.91 (10.3%); £3,771,515.96 -> £3,381,809.95 (10.3%); £3,771,516.12 -> £3,381,809.99 (10.3%); £3,771,516.28 -> £3,381,810.03 (10.3%); £3,771,516.44 -> £3,381,810.07 (10.3%); £3,771,516.60 -> £3,381,810.11 (10.3%); £3,771,516.76 -> £3,381,810.15 (10.3%); £3,771,516.92 -> £3,381,810.18 (10.3%); £3,771,517.08 -> £3,381,810.22 (10.3%); £3,771,517.24 -> £3,381,810.26 (10.3%); £3,771,517.39 -> £3,381,810.30 (10.3%); £3,771,517.56 -> £3,381,810.34 (10.3%); £3,771,517.72 -> £3,381,810.50 (10.3%); £3,771,517.88 -> £3,381,810.66 (10.3%); £3,771,518.05 -> £3,381,810.83 (10.3%); £3,771,518.24 -> £3,381,811.02 (10.3%); £3,771,518.45 -> £3,381,811.22 (10.3%); £3,771,518.68 -> £3,381,811.45 (10.3%); £3,771,518.93 -> £3,381,811.69 (10.3%); £3,771,519.19 -> £3,381,811.95 (10.3%); £3,771,519.44 -> £3,381,812.08 (10.3%); £3,771,519.71 -> £3,381,812.21 (10.3%); £3,771,519.97 -> £3,381,812.33 (10.3%); £3,771,520.24 -> £3,381,812.47 (10.3%); £3,771,520.51 -> £3,381,812.60 (10.3%); £3,771,520.77 -> £3,381,812.72 (10.3%); £3,771,521.04 -> £3,381,812.83 (10.3%); £3,771,521.30 -> £3,381,812.95 (10.3%); £3,771,521.58 -> £3,381,813.07 (10.3%); £3,771,521.84 -> £3,381,813.19 (10.3%); £3,771,522.10 -> £3,381,813.31 (10.3%); £3,771,522.36 -> £3,381,813.42 (10.3%); £3,771,522.62 -> £3,381,813.53 (10.3%); £3,771,522.88 -> £3,381,813.78 (10.3%); £3,771,523.08 -> £3,381,814.02 (10.3%); £3,771,523.27 -> £3,381,814.22 (10.3%); £3,771,523.47 -> £3,381,814.41 (10.3%); £3,771,523.73 -> £3,381,814.59 (10.3%); £3,771,523.98 -> £3,381,814.77 (10.3%); £3,771,524.25 -> £3,381,814.94 (10.3%); £3,771,524.52 -> £3,381,815.11 (10.3%); £3,771,524.78 -> £3,381,815.28 (10.3%); £3,771,525.05 -> £3,381,815.44 (10.3%); £3,771,525.31 -> £3,381,815.60 (10.3%); £3,771,525.58 -> £3,381,815.64 (10.3%); £3,771,525.85 -> £3,381,815.68 (10.3%); £3,771,526.10 -> £3,381,815.72 (10.3%); £3,771,526.32 -> £3,381,815.76 (10.3%); £3,771,526.52 -> £3,381,815.79 (10.3%); £3,771,526.68 -> £3,381,815.83 (10.3%); £3,771,526.84 -> £3,381,815.87 (10.3%); £3,771,527.00 -> £3,381,815.91 (10.3%); £3,771,527.16 -> £3,381,815.94 (10.3%); £3,771,527.32 -> £3,381,815.98 (10.3%); £3,771,527.48 -> £3,381,816.02 (10.3%); £3,771,527.64 -> £3,381,816.06 (10.3%); £3,771,527.79 -> £3,381,816.10 (10.3%); £3,771,527.95 -> £3,381,816.13 (10.3%); £3,771,528.11 -> £3,381,816.17 (10.3%); £3,771,528.27 -> £3,381,816.21 (10.3%); £3,771,528.42 -> £3,381,816.36 (10.3%); £3,771,528.58 -> £3,381,816.51 (10.3%); £3,771,528.76 -> £3,381,816.67 (10.3%); £3,771,528.95 -> £3,381,816.85 (10.3%); £3,771,529.16 -> £3,381,817.05 (10.3%); £3,771,529.39 -> £3,381,817.27 (10.3%); £3,771,529.64 -> £3,381,817.51 (10.3%); £3,771,529.90 -> £3,381,817.77 (10.3%); £3,771,530.17 -> £3,381,817.89 (10.3%); £3,771,530.43 -> £3,381,818.02 (10.3%); £3,771,530.71 -> £3,381,818.15 (10.3%); £3,771,530.97 -> £3,381,818.28 (10.3%); £3,771,531.23 -> £3,381,818.41 (10.3%); £3,771,531.49 -> £3,381,818.54 (10.3%); £3,771,531.76 -> £3,381,818.66 (10.3%); £3,771,532.02 -> £3,381,818.79 (10.3%); £3,771,532.28 -> £3,381,818.91 (10.3%); £3,771,532.54 -> £3,381,819.03 (10.3%); £3,771,532.81 -> £3,381,819.15 (10.3%); £3,771,533.08 -> £3,381,819.26 (10.3%); £3,771,533.34 -> £3,381,819.37 (10.3%); £3,771,533.61 -> £3,381,819.63 (10.3%); £3,771,533.87 -> £3,381,819.86 (10.3%); £3,771,534.14 -> £3,381,820.07 (10.3%); £3,771,534.40 -> £3,381,820.25 (10.3%); £3,771,534.66 -> £3,381,820.43 (10.3%); £3,771,534.94 -> £3,381,820.59 (10.3%); £3,771,535.13 -> £3,381,820.75 (10.3%); £3,771,535.39 -> £3,381,820.92 (10.3%); £3,771,535.64 -> £3,381,821.07 (10.3%); £3,771,535.91 -> £3,381,821.23 (10.3%); £3,771,536.18 -> £3,381,821.38 (10.3%); £3,771,536.44 -> £3,381,821.42 (10.3%); £3,771,536.70 -> £3,381,821.46 (10.3%); £3,771,536.95 -> £3,381,821.50 (10.3%); £3,771,537.17 -> £3,381,821.54 (10.3%); £3,771,537.37 -> £3,381,821.58 (10.3%); £3,771,537.54 -> £3,381,821.61 (10.3%); £3,771,537.70 -> £3,381,821.65 (10.3%); £3,771,537.86 -> £3,381,821.69 (10.3%); £3,771,538.03 -> £3,381,821.73 (10.3%); £3,771,538.19 -> £3,381,821.77 (10.3%); £3,771,538.35 -> £3,381,821.80 (10.3%); £3,771,538.51 -> £3,381,821.84 (10.3%); £3,771,538.67 -> £3,381,821.88 (10.3%); £3,771,538.82 -> £3,381,821.92 (10.3%); £3,771,538.99 -> £3,381,821.96 (10.3%); £3,771,539.15 -> £3,381,822.00 (10.3%); £3,771,539.31 -> £3,381,822.15 (10.3%); £3,771,539.47 -> £3,381,822.29 (10.3%); £3,771,539.65 -> £3,381,822.45 (10.3%); £3,771,539.85 -> £3,381,822.62 (10.3%); £3,771,540.06 -> £3,381,822.81 (10.3%); £3,771,540.28 -> £3,381,823.02 (10.3%); £3,771,540.53 -> £3,381,823.26 (10.3%); £3,771,540.81 -> £3,381,823.50 (10.3%); £3,771,541.08 -> £3,381,823.63 (10.3%); £3,771,541.34 -> £3,381,823.76 (10.3%); £3,771,541.61 -> £3,381,823.88 (10.3%); £3,771,541.87 -> £3,381,824.01 (10.3%); £3,771,542.14 -> £3,381,824.14 (10.3%); £3,771,542.40 -> £3,381,824.26 (10.3%); £3,771,542.67 -> £3,381,824.38 (10.3%); £3,771,542.94 -> £3,381,824.49 (10.3%); £3,771,543.21 -> £3,381,824.61 (10.3%); £3,771,543.47 -> £3,381,824.73 (10.3%); £3,771,543.74 -> £3,381,824.85 (10.3%); £3,771,544.01 -> £3,381,824.96 (10.3%); £3,771,544.28 -> £3,381,825.07 (10.3%); £3,771,544.54 -> £3,381,825.31 (10.3%); £3,771,544.81 -> £3,381,825.53 (10.3%); £3,771,545.07 -> £3,381,825.72 (10.3%); £3,771,545.34 -> £3,381,825.89 (10.3%); £3,771,545.54 -> £3,381,826.05 (10.3%); £3,771,545.74 -> £3,381,826.21 (10.3%); £3,771,546.01 -> £3,381,826.37 (10.3%); £3,771,546.27 -> £3,381,826.53 (10.3%); £3,771,546.53 -> £3,381,826.68 (10.3%); £3,771,546.80 -> £3,381,826.82 (10.3%); £3,771,547.08 -> £3,381,826.98 (10.3%); £3,771,547.34 -> £3,381,827.02 (10.3%); £3,771,547.61 -> £3,381,827.06 (10.3%); £3,771,547.86 -> £3,381,827.10 (10.3%); £3,771,548.08 -> £3,381,827.14 (10.3%); £3,771,548.29 -> £3,381,827.18 (10.3%); £3,771,548.44 -> £3,381,827.22 (10.3%); £3,771,548.60 -> £3,381,827.25 (10.3%); £3,771,548.76 -> £3,381,827.29 (10.3%); £3,771,548.92 -> £3,381,827.33 (10.3%); £3,771,549.08 -> £3,381,827.37 (10.3%); £3,771,549.24 -> £3,381,827.41 (10.3%); £3,771,549.41 -> £3,381,827.44 (10.3%); £3,771,549.57 -> £3,381,827.48 (10.3%); £3,771,549.73 -> £3,381,827.52 (10.3%); £3,771,549.89 -> £3,381,827.56 (10.3%); £3,771,550.05 -> £3,381,827.60 (10.3%); £3,771,550.21 -> £3,381,827.78 (10.3%); £3,771,550.37 -> £3,381,827.97 (10.3%); £3,771,550.55 -> £3,381,828.16 (10.3%); £3,771,550.75 -> £3,381,828.36 (10.3%); £3,771,550.96 -> £3,381,828.59 (10.3%); £3,771,551.20 -> £3,381,828.84 (10.3%); £3,771,551.45 -> £3,381,829.10 (10.3%); £3,771,551.72 -> £3,381,829.38 (10.3%); £3,771,551.98 -> £3,381,829.50 (10.3%); £3,771,552.25 -> £3,381,829.63 (10.3%); £3,771,552.52 -> £3,381,829.75 (10.3%); £3,771,552.78 -> £3,381,829.87 (10.3%); £3,771,553.04 -> £3,381,830.00 (10.3%); £3,771,553.31 -> £3,381,830.12 (10.3%); £3,771,553.59 -> £3,381,830.23 (10.3%); £3,771,553.86 -> £3,381,830.34 (10.3%); £3,771,554.12 -> £3,381,830.45 (10.3%); £3,771,554.39 -> £3,381,830.57 (10.3%); £3,771,554.65 -> £3,381,830.68 (10.3%); £3,771,554.92 -> £3,381,830.79 (10.3%); £3,771,555.19 -> £3,381,830.90 (10.3%); £3,771,555.46 -> £3,381,831.18 (10.3%); £3,771,555.73 -> £3,381,831.45 (10.3%); £3,771,556.00 -> £3,381,831.69 (10.3%); £3,771,556.27 -> £3,381,831.89 (10.3%); £3,771,556.47 -> £3,381,832.10 (10.3%); £3,771,556.74 -> £3,381,832.30 (10.3%); £3,771,557.02 -> £3,381,832.50 (10.3%); £3,771,557.28 -> £3,381,832.69 (10.3%); £3,771,557.56 -> £3,381,832.88 (10.3%); £3,771,557.83 -> £3,381,833.06 (10.3%); £3,771,558.09 -> £3,381,833.23 (10.3%); £3,771,558.36 -> £3,381,833.28 (10.3%); £3,771,558.63 -> £3,381,833.32 (10.3%); £3,771,558.87 -> £3,381,833.36 (10.3%); £3,771,559.09 -> £3,381,833.40 (10.3%); £3,771,559.30 -> £3,381,833.43 (10.3%); £3,771,559.46 -> £3,381,833.47 (10.3%); £3,771,559.62 -> £3,381,833.51 (10.3%); £3,771,559.79 -> £3,381,833.54 (10.3%); £3,771,559.94 -> £3,381,833.58 (10.3%); £3,771,560.10 -> £3,381,833.62 (10.3%); £3,771,560.26 -> £3,381,833.66 (10.3%); £3,771,560.42 -> £3,381,833.69 (10.3%); £3,771,560.58 -> £3,381,833.73 (10.3%); £3,771,560.75 -> £3,381,833.77 (10.3%); £3,771,560.91 -> £3,381,833.81 (10.3%); £3,771,561.07 -> £3,381,833.85 (10.3%); £3,771,561.23 -> £3,381,834.07 (10.3%); £3,771,561.38 -> £3,381,834.30 (10.3%); £3,771,561.56 -> £3,381,834.55 (10.3%); £3,771,561.76 -> £3,381,834.81 (10.3%); £3,771,561.97 -> £3,381,835.08 (10.3%); £3,771,562.20 -> £3,381,835.38 (10.3%); £3,771,562.45 -> £3,381,835.71 (10.3%); £3,771,562.73 -> £3,381,836.04 (10.3%); £3,771,562.99 -> £3,381,836.17 (10.3%); £3,771,563.25 -> £3,381,836.30 (10.3%); £3,771,563.50 -> £3,381,836.42 (10.3%); £3,771,563.76 -> £3,381,836.55 (10.3%); £3,771,564.02 -> £3,381,836.68 (10.3%); £3,771,564.29 -> £3,381,836.80 (10.3%); £3,771,564.55 -> £3,381,836.91 (10.3%); £3,771,564.83 -> £3,381,837.03 (10.3%); £3,771,565.10 -> £3,381,837.15 (10.3%); £3,771,565.36 -> £3,381,837.27 (10.3%); £3,771,565.62 -> £3,381,837.38 (10.3%); £3,771,565.89 -> £3,381,837.50 (10.3%); £3,771,566.15 -> £3,381,837.61 (10.3%); £3,771,566.42 -> £3,381,837.93 (10.3%); £3,771,566.67 -> £3,381,838.22 (10.3%); £3,771,566.87 -> £3,381,838.49 (10.3%); £3,771,567.08 -> £3,381,838.73 (10.3%); £3,771,567.27 -> £3,381,838.97 (10.3%); £3,771,567.47 -> £3,381,839.20 (10.3%); £3,771,567.68 -> £3,381,839.43 (10.3%); £3,771,567.94 -> £3,381,839.65 (10.3%); £3,771,568.20 -> £3,381,839.87 (10.3%); £3,771,568.48 -> £3,381,840.09 (10.3%); £3,771,568.74 -> £3,381,840.30 (10.3%); £3,771,569.01 -> £3,381,840.34 (10.3%); £3,771,569.27 -> £3,381,840.39 (10.3%); £3,771,569.51 -> £3,381,840.43 (10.3%); £3,771,569.73 -> £3,381,840.46 (10.3%); £3,771,569.93 -> £3,381,840.50 (10.3%); £3,771,570.07 -> £3,381,840.54 (10.3%); £3,771,570.21 -> £3,381,840.57 (10.3%); £3,771,570.36 -> £3,381,840.61 (10.3%); £3,771,570.50 -> £3,381,840.65 (10.3%); £3,771,570.64 -> £3,381,840.68 (10.3%); £3,771,570.78 -> £3,381,840.72 (10.3%); £3,771,570.92 -> £3,381,840.76 (10.3%); £3,771,571.06 -> £3,381,840.79 (10.3%); £3,771,571.20 -> £3,381,840.83 (10.3%); £3,771,571.34 -> £3,381,840.87 (10.3%); £3,771,571.48 -> £3,381,840.91 (10.3%); £3,771,571.62 -> £3,381,841.14 (10.3%); £3,771,571.76 -> £3,381,841.38 (10.3%); £3,771,571.92 -> £3,381,841.62 (10.3%); £3,771,572.09 -> £3,381,841.86 (10.3%); £3,771,572.28 -> £3,381,842.11 (10.3%); £3,771,572.48 -> £3,381,842.37 (10.3%); £3,771,572.71 -> £3,381,842.65 (10.3%); £3,771,572.94 -> £3,381,842.94 (10.3%); £3,771,573.18 -> £3,381,843.03 (10.3%); £3,771,573.41 -> £3,381,843.12 (10.3%); £3,771,573.65 -> £3,381,843.21 (10.3%); £3,771,573.88 -> £3,381,843.31 (10.3%); £3,771,574.11 -> £3,381,843.39 (10.3%); £3,771,574.35 -> £3,381,843.47 (10.3%); £3,771,574.58 -> £3,381,843.54 (10.3%); £3,771,574.81 -> £3,381,843.62 (10.3%); £3,771,575.05 -> £3,381,843.69 (10.3%); £3,771,575.28 -> £3,381,843.76 (10.3%); £3,771,575.52 -> £3,381,843.83 (10.3%); £3,771,575.77 -> £3,381,843.90 (10.3%); £3,771,576.00 -> £3,381,843.96 (10.3%); £3,771,576.18 -> £3,381,844.22 (10.3%); £3,771,576.35 -> £3,381,844.47 (10.3%); £3,771,576.53 -> £3,381,844.71 (10.3%); £3,771,576.70 -> £3,381,844.94 (10.3%); £3,771,576.88 -> £3,381,845.17 (10.3%); £3,771,577.05 -> £3,381,845.40 (10.3%); £3,771,577.23 -> £3,381,845.63 (10.3%); £3,771,577.47 -> £3,381,845.85 (10.3%); £3,771,577.71 -> £3,381,846.08 (10.3%); £3,771,577.94 -> £3,381,846.30 (10.3%); £3,771,578.18 -> £3,381,846.52 (10.3%); £3,771,578.42 -> £3,381,846.56 (10.3%); £3,771,578.65 -> £3,381,846.60 (10.3%); £3,771,578.86 -> £3,381,846.64 (10.3%); £3,771,579.06 -> £3,381,846.68 (10.3%); £3,771,579.25 -> £3,381,846.72 (10.3%); £3,771,579.39 -> £3,381,846.75 (10.3%); £3,771,579.54 -> £3,381,846.79 (10.3%); £3,771,579.67 -> £3,381,846.83 (10.3%); £3,771,579.82 -> £3,381,846.87 (10.3%); £3,771,579.95 -> £3,381,846.90 (10.3%); £3,771,580.09 -> £3,381,846.94 (10.3%); £3,771,580.23 -> £3,381,846.98 (10.3%); £3,771,580.37 -> £3,381,847.01 (10.3%); £3,771,580.51 -> £3,381,847.05 (10.3%); £3,771,580.65 -> £3,381,847.08 (10.3%); £3,771,580.79 -> £3,381,847.12 (10.3%); £3,771,580.93 -> £3,381,847.33 (10.3%); £3,771,581.07 -> £3,381,847.54 (10.3%); £3,771,581.22 -> £3,381,847.76 (10.3%); £3,771,581.40 -> £3,381,847.97 (10.3%); £3,771,581.59 -> £3,381,848.19 (10.3%); £3,771,581.79 -> £3,381,848.41 (10.3%); £3,771,582.00 -> £3,381,848.63 (10.3%); £3,771,582.24 -> £3,381,848.86 (10.3%); £3,771,582.48 -> £3,381,848.91 (10.3%); £3,771,582.72 -> £3,381,848.96 (10.3%); £3,771,582.96 -> £3,381,849.01 (10.3%); £3,771,583.18 -> £3,381,849.06 (10.3%); £3,771,583.42 -> £3,381,849.11 (10.3%); £3,771,583.65 -> £3,381,849.15 (10.3%); £3,771,583.88 -> £3,381,849.20 (10.3%); £3,771,584.13 -> £3,381,849.25 (10.3%); £3,771,584.36 -> £3,381,849.29 (10.3%); £3,771,584.59 -> £3,381,849.34 (10.3%); £3,771,584.82 -> £3,381,849.38 (10.3%); £3,771,585.06 -> £3,381,849.43 (10.3%); £3,771,585.29 -> £3,381,849.47 (10.3%); £3,771,585.47 -> £3,381,849.69 (10.3%); £3,771,585.64 -> £3,381,849.90 (10.3%); £3,771,585.82 -> £3,381,850.11 (10.3%); £3,771,586.00 -> £3,381,850.32 (10.3%); £3,771,586.23 -> £3,381,850.55 (10.3%); £3,771,586.46 -> £3,381,850.76 (10.3%); £3,771,586.64 -> £3,381,850.98 (10.3%); £3,771,586.88 -> £3,381,851.19 (10.3%); £3,771,587.11 -> £3,381,851.41 (10.3%); £3,771,587.34 -> £3,381,851.62 (10.3%); £3,771,587.57 -> £3,381,851.84 (10.3%); £3,771,587.80 -> £3,381,851.88 (10.3%); £3,771,588.04 -> £3,381,851.92 (10.3%); £3,771,588.25 -> £3,381,851.95 (10.3%); £3,771,588.45 -> £3,381,851.99 (10.3%); £3,771,588.63 -> £3,381,852.03 (10.3%); £3,771,588.79 -> £3,381,852.06 (10.3%); £3,771,588.95 -> £3,381,852.10 (10.3%); £3,771,589.11 -> £3,381,852.14 (10.3%); £3,771,589.26 -> £3,381,852.18 (10.3%); £3,771,589.43 -> £3,381,852.22 (10.3%); £3,771,589.59 -> £3,381,852.25 (10.3%); £3,771,589.74 -> £3,381,852.29 (10.3%); £3,771,589.91 -> £3,381,852.33 (10.3%); £3,771,590.07 -> £3,381,852.37 (10.3%); £3,771,590.23 -> £3,381,852.41 (10.3%); £3,771,590.39 -> £3,381,852.45 (10.3%); £3,771,590.55 -> £3,381,852.65 (10.3%); £3,771,590.71 -> £3,381,852.86 (10.3%); £3,771,590.88 -> £3,381,853.07 (10.3%); £3,771,591.07 -> £3,381,853.30 (10.3%); £3,771,591.30 -> £3,381,853.56 (10.3%); £3,771,591.52 -> £3,381,853.83 (10.3%); £3,771,591.76 -> £3,381,854.13 (10.3%); £3,771,592.03 -> £3,381,854.43 (10.3%); £3,771,592.29 -> £3,381,854.55 (10.3%); £3,771,592.55 -> £3,381,854.68 (10.3%); £3,771,592.82 -> £3,381,854.80 (10.3%); £3,771,593.09 -> £3,381,854.93 (10.3%); £3,771,593.36 -> £3,381,855.06 (10.3%); £3,771,593.61 -> £3,381,855.18 (10.3%); £3,771,593.87 -> £3,381,855.30 (10.3%); £3,771,594.14 -> £3,381,855.42 (10.3%); £3,771,594.41 -> £3,381,855.54 (10.3%); £3,771,594.67 -> £3,381,855.66 (10.3%); £3,771,594.94 -> £3,381,855.77 (10.3%); £3,771,595.20 -> £3,381,855.89 (10.3%); £3,771,595.46 -> £3,381,856.00 (10.3%); £3,771,595.72 -> £3,381,856.30 (10.3%); £3,771,596.00 -> £3,381,856.59 (10.3%); £3,771,596.26 -> £3,381,856.84 (10.3%); £3,771,596.52 -> £3,381,857.07 (10.3%); £3,771,596.78 -> £3,381,857.29 (10.3%); £3,771,597.03 -> £3,381,857.50 (10.3%); £3,771,597.24 -> £3,381,857.72 (10.3%); £3,771,597.50 -> £3,381,857.93 (10.3%); £3,771,597.76 -> £3,381,858.14 (10.3%); £3,771,598.01 -> £3,381,858.34 (10.3%); £3,771,598.27 -> £3,381,858.54 (10.3%); £3,771,598.53 -> £3,381,858.58 (10.3%); £3,771,598.79 -> £3,381,858.62 (10.3%); £3,771,599.04 -> £3,381,858.66 (10.3%); £3,771,599.26 -> £3,381,858.70 (10.3%); £3,771,599.47 -> £3,381,858.74 (10.3%); £3,771,599.63 -> £3,381,858.78 (10.3%); £3,771,599.78 -> £3,381,858.81 (10.3%); £3,771,599.94 -> £3,381,858.85 (10.3%); £3,771,600.10 -> £3,381,858.89 (10.3%); £3,771,600.26 -> £3,381,858.93 (10.3%); £3,771,600.41 -> £3,381,858.96 (10.3%); £3,771,600.57 -> £3,381,859.00 (10.3%); £3,771,600.73 -> £3,381,859.04 (10.3%); £3,771,600.89 -> £3,381,859.08 (10.3%); £3,771,601.04 -> £3,381,859.12 (10.3%); £3,771,601.19 -> £3,381,859.16 (10.3%); £3,771,601.35 -> £3,381,859.39 (10.3%); £3,771,601.51 -> £3,381,859.62 (10.3%); £3,771,601.69 -> £3,381,859.87 (10.3%); £3,771,601.87 -> £3,381,860.12 (10.3%); £3,771,602.08 -> £3,381,860.40 (10.3%); £3,771,602.32 -> £3,381,860.70 (10.3%); £3,771,602.57 -> £3,381,861.02 (10.3%); £3,771,602.82 -> £3,381,861.35 (10.3%); £3,771,603.08 -> £3,381,861.47 (10.3%); £3,771,603.34 -> £3,381,861.60 (10.3%); £3,771,603.59 -> £3,381,861.73 (10.3%); £3,771,603.85 -> £3,381,861.86 (10.3%); £3,771,604.11 -> £3,381,861.99 (10.3%); £3,771,604.37 -> £3,381,862.12 (10.3%); £3,771,604.63 -> £3,381,862.24 (10.3%); £3,771,604.90 -> £3,381,862.36 (10.3%); £3,771,605.15 -> £3,381,862.48 (10.3%); £3,771,605.42 -> £3,381,862.60 (10.3%); £3,771,605.67 -> £3,381,862.71 (10.3%); £3,771,605.93 -> £3,381,862.82 (10.3%); £3,771,606.20 -> £3,381,862.93 (10.3%); £3,771,606.47 -> £3,381,863.25 (10.3%); £3,771,606.73 -> £3,381,863.54 (10.3%); £3,771,606.91 -> £3,381,863.81 (10.3%); £3,771,607.12 -> £3,381,864.05 (10.3%); £3,771,607.32 -> £3,381,864.29 (10.3%); £3,771,607.51 -> £3,381,864.53 (10.3%); £3,771,607.77 -> £3,381,864.76 (10.3%); £3,771,608.03 -> £3,381,864.99 (10.3%); £3,771,608.30 -> £3,381,865.21 (10.3%); £3,771,608.56 -> £3,381,865.44 (10.3%); £3,771,608.82 -> £3,381,865.66 (10.3%); £3,771,609.08 -> £3,381,865.71 (10.3%); £3,771,609.35 -> £3,381,865.75 (10.3%); £3,771,609.59 -> £3,381,865.79 (10.3%); £3,771,609.82 -> £3,381,865.82 (10.3%); £3,771,610.02 -> £3,381,865.86 (10.3%); £3,771,610.18 -> £3,381,865.90 (10.3%); £3,771,610.34 -> £3,381,865.94 (10.3%); £3,771,610.49 -> £3,381,865.97 (10.3%); £3,771,610.65 -> £3,381,866.01 (10.3%); £3,771,610.80 -> £3,381,866.05 (10.3%); £3,771,610.96 -> £3,381,866.08 (10.3%); £3,771,611.12 -> £3,381,866.12 (10.3%); £3,771,611.28 -> £3,381,866.16 (10.3%); £3,771,611.44 -> £3,381,866.20 (10.3%); £3,771,611.59 -> £3,381,866.24 (10.3%); £3,771,611.75 -> £3,381,866.28 (10.3%); £3,771,611.91 -> £3,381,866.46 (10.3%); £3,771,612.06 -> £3,381,866.64 (10.3%); £3,771,612.24 -> £3,381,866.84 (10.3%); £3,771,612.44 -> £3,381,867.05 (10.3%); £3,771,612.64 -> £3,381,867.28 (10.3%); £3,771,612.87 -> £3,381,867.53 (10.3%); £3,771,613.11 -> £3,381,867.81 (10.3%); £3,771,613.36 -> £3,381,868.10 (10.3%); £3,771,613.62 -> £3,381,868.23 (10.3%); £3,771,613.88 -> £3,381,868.36 (10.3%); £3,771,614.13 -> £3,381,868.49 (10.3%); £3,771,614.40 -> £3,381,868.62 (10.3%); £3,771,614.66 -> £3,381,868.75 (10.3%); £3,771,614.92 -> £3,381,868.87 (10.3%); £3,771,615.19 -> £3,381,868.99 (10.3%); £3,771,615.45 -> £3,381,869.11 (10.3%); £3,771,615.71 -> £3,381,869.23 (10.3%); £3,771,615.98 -> £3,381,869.34 (10.3%); £3,771,616.24 -> £3,381,869.45 (10.3%); £3,771,616.50 -> £3,381,869.57 (10.3%); £3,771,616.76 -> £3,381,869.67 (10.3%); £3,771,616.96 -> £3,381,869.96 (10.3%); £3,771,617.22 -> £3,381,870.22 (10.3%); £3,771,617.42 -> £3,381,870.45 (10.3%); £3,771,617.62 -> £3,381,870.66 (10.3%); £3,771,617.89 -> £3,381,870.86 (10.3%); £3,771,618.15 -> £3,381,871.06 (10.3%); £3,771,618.34 -> £3,381,871.26 (10.3%); £3,771,618.60 -> £3,381,871.45 (10.3%); £3,771,618.86 -> £3,381,871.63 (10.3%); £3,771,619.13 -> £3,381,871.82 (10.3%); £3,771,619.39 -> £3,381,872.00 (10.3%); £3,771,619.66 -> £3,381,872.04 (10.3%); £3,771,619.93 -> £3,381,872.08 (10.3%); £3,771,620.17 -> £3,381,872.12 (10.3%); £3,771,620.40 -> £3,381,872.16 (10.3%); £3,771,620.60 -> £3,381,872.19 (10.3%); £3,771,620.76 -> £3,381,872.23 (10.3%); £3,771,620.91 -> £3,381,872.27 (10.3%); £3,771,621.06 -> £3,381,872.31 (10.3%); £3,771,621.22 -> £3,381,872.34 (10.3%); £3,771,621.37 -> £3,381,872.38 (10.3%); £3,771,621.53 -> £3,381,872.42 (10.3%); £3,771,621.68 -> £3,381,872.45 (10.3%); £3,771,621.84 -> £3,381,872.49 (10.3%); £3,771,621.99 -> £3,381,872.53 (10.3%); £3,771,622.15 -> £3,381,872.57 (10.3%); £3,771,622.30 -> £3,381,872.61 (10.3%); £3,771,622.46 -> £3,381,872.78 (10.3%); £3,771,622.61 -> £3,381,872.96 (10.3%); £3,771,622.78 -> £3,381,873.14 (10.3%); £3,771,622.97 -> £3,381,873.33 (10.3%); £3,771,623.17 -> £3,381,873.54 (10.3%); £3,771,623.40 -> £3,381,873.77 (10.3%); £3,771,623.64 -> £3,381,874.02 (10.3%); £3,771,623.90 -> £3,381,874.29 (10.3%); £3,771,624.16 -> £3,381,874.41 (10.3%); £3,771,624.42 -> £3,381,874.54 (10.3%); £3,771,624.68 -> £3,381,874.66 (10.3%); £3,771,624.93 -> £3,381,874.79 (10.3%); £3,771,625.19 -> £3,381,874.91 (10.3%); £3,771,625.44 -> £3,381,875.04 (10.3%); £3,771,625.70 -> £3,381,875.15 (10.3%); £3,771,625.96 -> £3,381,875.27 (10.3%); £3,771,626.22 -> £3,381,875.38 (10.3%); £3,771,626.48 -> £3,381,875.50 (10.3%); £3,771,626.73 -> £3,381,875.62 (10.3%); £3,771,626.97 -> £3,381,875.73 (10.3%); £3,771,627.24 -> £3,381,875.84 (10.3%); £3,771,627.49 -> £3,381,876.11 (10.3%); £3,771,627.75 -> £3,381,876.35 (10.3%); £3,771,628.00 -> £3,381,876.56 (10.3%); £3,771,628.20 -> £3,381,876.75 (10.3%); £3,771,628.39 -> £3,381,876.93 (10.3%); £3,771,628.65 -> £3,381,877.11 (10.3%); £3,771,628.85 -> £3,381,877.28 (10.3%); £3,771,629.10 -> £3,381,877.45 (10.3%); £3,771,629.35 -> £3,381,877.61 (10.3%); £3,771,629.62 -> £3,381,877.77 (10.3%); £3,771,629.87 -> £3,381,877.93 (10.3%); £3,771,630.14 -> £3,381,877.97 (10.3%); £3,771,630.40 -> £3,381,878.01 (10.3%); £3,771,630.64 -> £3,381,878.05 (10.3%); £3,771,630.86 -> £3,381,878.09 (10.3%); £3,771,631.06 -> £3,381,878.13 (10.3%); £3,771,631.22 -> £3,381,878.17 (10.3%); £3,771,631.37 -> £3,381,878.20 (10.3%); £3,771,631.53 -> £3,381,878.24 (10.3%); £3,771,631.68 -> £3,381,878.28 (10.3%); £3,771,631.84 -> £3,381,878.31 (10.3%); £3,771,632.00 -> £3,381,878.35 (10.3%); £3,771,632.16 -> £3,381,878.39 (10.3%); £3,771,632.31 -> £3,381,878.43 (10.3%); £3,771,632.47 -> £3,381,878.47 (10.3%); £3,771,632.62 -> £3,381,878.50 (10.3%); £3,771,632.77 -> £3,381,878.55 (10.3%); £3,771,632.93 -> £3,381,878.77 (10.3%); £3,771,633.08 -> £3,381,878.99 (10.3%); £3,771,633.26 -> £3,381,879.23 (10.3%); £3,771,633.44 -> £3,381,879.48 (10.3%); £3,771,633.64 -> £3,381,879.75 (10.3%); £3,771,633.87 -> £3,381,880.04 (10.3%); £3,771,634.10 -> £3,381,880.36 (10.3%); £3,771,634.36 -> £3,381,880.69 (10.3%); £3,771,634.62 -> £3,381,880.81 (10.3%); £3,771,634.88 -> £3,381,880.94 (10.3%); £3,771,635.14 -> £3,381,881.06 (10.3%); £3,771,635.40 -> £3,381,881.19 (10.3%); £3,771,635.67 -> £3,381,881.32 (10.3%); £3,771,635.93 -> £3,381,881.44 (10.3%); £3,771,636.19 -> £3,381,881.55 (10.3%); £3,771,636.45 -> £3,381,881.66 (10.3%); £3,771,636.71 -> £3,381,881.78 (10.3%); £3,771,636.98 -> £3,381,881.90 (10.3%); £3,771,637.24 -> £3,381,882.02 (10.3%); £3,771,637.50 -> £3,381,882.13 (10.3%); £3,771,637.76 -> £3,381,882.23 (10.3%); £3,771,638.01 -> £3,381,882.54 (10.3%); £3,771,638.27 -> £3,381,882.84 (10.3%); £3,771,638.53 -> £3,381,883.10 (10.3%); £3,771,638.80 -> £3,381,883.34 (10.3%); £3,771,639.07 -> £3,381,883.58 (10.3%); £3,771,639.33 -> £3,381,883.81 (10.3%); £3,771,639.59 -> £3,381,884.06 (10.3%); £3,771,639.85 -> £3,381,884.28 (10.3%); £3,771,640.12 -> £3,381,884.51 (10.3%); £3,771,640.38 -> £3,381,884.74 (10.3%); £3,771,640.64 -> £3,381,884.95 (10.3%); £3,771,640.91 -> £3,381,884.99 (10.3%); £3,771,641.17 -> £3,381,885.03 (10.3%); £3,771,641.41 -> £3,381,885.07 (10.3%); £3,771,641.63 -> £3,381,885.11 (10.3%); £3,771,641.83 -> £3,381,885.14 (10.3%); £3,771,641.97 -> £3,381,885.18 (10.3%); £3,771,642.10 -> £3,381,885.22 (10.3%); £3,771,642.23 -> £3,381,885.26 (10.3%); £3,771,642.37 -> £3,381,885.29 (10.3%); £3,771,642.51 -> £3,381,885.33 (10.3%); £3,771,642.64 -> £3,381,885.37 (10.3%); £3,771,642.78 -> £3,381,885.40 (10.3%); £3,771,642.91 -> £3,381,885.44 (10.3%); £3,771,643.05 -> £3,381,885.48 (10.3%); £3,771,643.19 -> £3,381,885.52 (10.3%); £3,771,643.33 -> £3,381,885.55 (10.3%); £3,771,643.46 -> £3,381,885.79 (10.3%); £3,771,643.60 -> £3,381,886.02 (10.3%); £3,771,643.76 -> £3,381,886.26 (10.3%); £3,771,643.92 -> £3,381,886.50 (10.3%); £3,771,644.10 -> £3,381,886.74 (10.3%); £3,771,644.30 -> £3,381,887.00 (10.3%); £3,771,644.51 -> £3,381,887.27 (10.3%); £3,771,644.74 -> £3,381,887.55 (10.3%); £3,771,644.97 -> £3,381,887.64 (10.3%); £3,771,645.19 -> £3,381,887.73 (10.3%); £3,771,645.41 -> £3,381,887.82 (10.3%); £3,771,645.63 -> £3,381,887.91 (10.3%); £3,771,645.86 -> £3,381,887.99 (10.3%); £3,771,646.08 -> £3,381,888.07 (10.3%); £3,771,646.31 -> £3,381,888.15 (10.3%); £3,771,646.54 -> £3,381,888.22 (10.3%); £3,771,646.78 -> £3,381,888.30 (10.3%); £3,771,647.01 -> £3,381,888.37 (10.3%); £3,771,647.23 -> £3,381,888.44 (10.3%); £3,771,647.46 -> £3,381,888.51 (10.3%); £3,771,647.69 -> £3,381,888.58 (10.3%); £3,771,647.91 -> £3,381,888.84 (10.3%); £3,771,648.14 -> £3,381,889.09 (10.3%); £3,771,648.36 -> £3,381,889.33 (10.3%); £3,771,648.59 -> £3,381,889.56 (10.3%); £3,771,648.81 -> £3,381,889.79 (10.3%); £3,771,649.04 -> £3,381,890.03 (10.3%); £3,771,649.27 -> £3,381,890.26 (10.3%); £3,771,649.50 -> £3,381,890.49 (10.3%); £3,771,649.73 -> £3,381,890.72 (10.3%); £3,771,649.95 -> £3,381,890.95 (10.3%); £3,771,650.18 -> £3,381,891.18 (10.3%); £3,771,650.41 -> £3,381,891.22 (10.3%); £3,771,650.62 -> £3,381,891.26 (10.3%); £3,771,650.84 -> £3,381,891.30 (10.3%); £3,771,651.03 -> £3,381,891.34 (10.3%); £3,771,651.21 -> £3,381,891.37 (10.3%); £3,771,651.34 -> £3,381,891.41 (10.3%); £3,771,651.48 -> £3,381,891.45 (10.3%); £3,771,651.61 -> £3,381,891.49 (10.3%); £3,771,651.74 -> £3,381,891.52 (10.3%); £3,771,651.88 -> £3,381,891.56 (10.3%); £3,771,652.02 -> £3,381,891.59 (10.3%); £3,771,652.15 -> £3,381,891.63 (10.3%); £3,771,652.28 -> £3,381,891.67 (10.3%); £3,771,652.42 -> £3,381,891.70 (10.3%); £3,771,652.56 -> £3,381,891.74 (10.3%); £3,771,652.69 -> £3,381,891.77 (10.3%); £3,771,652.83 -> £3,381,891.99 (10.3%); £3,771,652.97 -> £3,381,892.20 (10.3%); £3,771,653.12 -> £3,381,892.42 (10.3%); £3,771,653.28 -> £3,381,892.64 (10.3%); £3,771,653.46 -> £3,381,892.86 (10.3%); £3,771,653.66 -> £3,381,893.09 (10.3%); £3,771,653.87 -> £3,381,893.32 (10.3%); £3,771,654.09 -> £3,381,893.54 (10.3%); £3,771,654.32 -> £3,381,893.59 (10.3%); £3,771,654.55 -> £3,381,893.64 (10.3%); £3,771,654.78 -> £3,381,893.69 (10.3%); £3,771,655.00 -> £3,381,893.74 (10.3%); £3,771,655.21 -> £3,381,893.79 (10.3%); £3,771,655.44 -> £3,381,893.84 (10.3%); £3,771,655.67 -> £3,381,893.89 (10.3%); £3,771,655.90 -> £3,381,893.94 (10.3%); £3,771,656.12 -> £3,381,893.98 (10.3%); £3,771,656.35 -> £3,381,894.03 (10.3%); £3,771,656.57 -> £3,381,894.07 (10.3%); £3,771,656.80 -> £3,381,894.12 (10.3%); £3,771,657.04 -> £3,381,894.17 (10.3%); £3,771,657.27 -> £3,381,894.38 (10.3%); £3,771,657.49 -> £3,381,894.61 (10.3%); £3,771,657.72 -> £3,381,894.82 (10.3%); £3,771,657.95 -> £3,381,895.04 (10.3%); £3,771,658.17 -> £3,381,895.26 (10.3%); £3,771,658.39 -> £3,381,895.49 (10.3%); £3,771,658.62 -> £3,381,895.71 (10.3%); £3,771,658.83 -> £3,381,895.93 (10.3%); £3,771,659.06 -> £3,381,896.15 (10.3%); £3,771,659.29 -> £3,381,896.37 (10.3%); £3,771,659.53 -> £3,381,896.58 (10.3%); £3,771,659.75 -> £3,381,896.62 (10.3%); £3,771,659.98 -> £3,381,896.66 (10.3%); £3,771,660.19 -> £3,381,896.70 (10.3%); £3,771,660.38 -> £3,381,896.74 (10.3%); £3,771,660.56 -> £3,381,896.77 (10.3%); £3,771,660.71 -> £3,381,896.81 (10.3%); £3,771,660.87 -> £3,381,896.85 (10.3%); £3,771,661.02 -> £3,381,896.89 (10.3%); £3,771,661.18 -> £3,381,896.92 (10.3%); £3,771,661.33 -> £3,381,896.96 (10.3%); £3,771,661.49 -> £3,381,897.00 (10.3%); £3,771,661.64 -> £3,381,897.03 (10.3%); £3,771,661.80 -> £3,381,897.07 (10.3%); £3,771,661.95 -> £3,381,897.11 (10.3%); £3,771,662.10 -> £3,381,897.15 (10.3%); £3,771,662.26 -> £3,381,897.19 (10.3%); £3,771,662.42 -> £3,381,897.39 (10.3%); £3,771,662.57 -> £3,381,897.60 (10.3%); £3,771,662.74 -> £3,381,897.81 (10.3%); £3,771,662.93 -> £3,381,898.05 (10.3%); £3,771,663.13 -> £3,381,898.30 (10.3%); £3,771,663.36 -> £3,381,898.58 (10.3%); £3,771,663.60 -> £3,381,898.88 (10.3%); £3,771,663.86 -> £3,381,899.20 (10.3%); £3,771,664.12 -> £3,381,899.33 (10.3%); £3,771,664.38 -> £3,381,899.46 (10.3%); £3,771,664.65 -> £3,381,899.59 (10.3%); £3,771,664.90 -> £3,381,899.72 (10.3%); £3,771,665.16 -> £3,381,899.85 (10.3%); £3,771,665.42 -> £3,381,899.97 (10.3%); £3,771,665.68 -> £3,381,900.09 (10.3%); £3,771,665.94 -> £3,381,900.20 (10.3%); £3,771,666.20 -> £3,381,900.32 (10.3%); £3,771,666.46 -> £3,381,900.44 (10.3%); £3,771,666.71 -> £3,381,900.55 (10.3%); £3,771,666.98 -> £3,381,900.67 (10.3%); £3,771,667.24 -> £3,381,900.78 (10.3%); £3,771,667.48 -> £3,381,901.08 (10.3%); £3,771,667.74 -> £3,381,901.36 (10.3%); £3,771,667.99 -> £3,381,901.61 (10.3%); £3,771,668.24 -> £3,381,901.84 (10.3%); £3,771,668.50 -> £3,381,902.06 (10.3%); £3,771,668.75 -> £3,381,902.27 (10.3%); £3,771,669.01 -> £3,381,902.49 (10.3%); £3,771,669.27 -> £3,381,902.71 (10.3%); £3,771,669.53 -> £3,381,902.93 (10.3%); £3,771,669.78 -> £3,381,903.13 (10.3%); £3,771,670.05 -> £3,381,903.33 (10.3%); £3,771,670.30 -> £3,381,903.37 (10.3%); £3,771,670.56 -> £3,381,903.41 (10.3%); £3,771,670.80 -> £3,381,903.45 (10.3%); £3,771,671.02 -> £3,381,903.49 (10.3%); £3,771,671.22 -> £3,381,903.52 (10.3%); £3,771,671.37 -> £3,381,903.56 (10.3%); £3,771,671.52 -> £3,381,903.60 (10.3%); £3,771,671.68 -> £3,381,903.64 (10.3%); £3,771,671.84 -> £3,381,903.68 (10.3%); £3,771,671.99 -> £3,381,903.71 (10.3%); £3,771,672.15 -> £3,381,903.75 (10.3%); £3,771,672.29 -> £3,381,903.79 (10.3%); £3,771,672.44 -> £3,381,903.83 (10.3%); £3,771,672.59 -> £3,381,903.86 (10.3%); £3,771,672.74 -> £3,381,903.90 (10.3%); £3,771,672.90 -> £3,381,903.94 (10.3%); £3,771,673.05 -> £3,381,904.12 (10.3%); £3,771,673.21 -> £3,381,904.30 (10.3%); £3,771,673.38 -> £3,381,904.49 (10.3%); £3,771,673.57 -> £3,381,904.69 (10.3%); £3,771,673.77 -> £3,381,904.92 (10.3%); £3,771,673.99 -> £3,381,905.16 (10.3%); £3,771,674.23 -> £3,381,905.43 (10.3%); £3,771,674.49 -> £3,381,905.71 (10.3%); £3,771,674.74 -> £3,381,905.83 (10.3%); £3,771,675.00 -> £3,381,905.96 (10.3%); £3,771,675.26 -> £3,381,906.09 (10.3%); £3,771,675.52 -> £3,381,906.22 (10.3%); £3,771,675.77 -> £3,381,906.35 (10.3%); £3,771,676.02 -> £3,381,906.48 (10.3%); £3,771,676.29 -> £3,381,906.60 (10.3%); £3,771,676.54 -> £3,381,906.72 (10.3%); £3,771,676.79 -> £3,381,906.83 (10.3%); £3,771,677.05 -> £3,381,906.95 (10.3%); £3,771,677.30 -> £3,381,907.06 (10.3%); £3,771,677.57 -> £3,381,907.18 (10.3%); £3,771,677.82 -> £3,381,907.29 (10.3%); £3,771,678.09 -> £3,381,907.56 (10.3%); £3,771,678.35 -> £3,381,907.82 (10.3%); £3,771,678.60 -> £3,381,908.04 (10.3%); £3,771,678.85 -> £3,381,908.24 (10.3%); £3,771,679.11 -> £3,381,908.43 (10.3%); £3,771,679.37 -> £3,381,908.62 (10.3%); £3,771,679.62 -> £3,381,908.81 (10.3%); £3,771,679.88 -> £3,381,908.99 (10.3%); £3,771,680.14 -> £3,381,909.17 (10.3%); £3,771,680.39 -> £3,381,909.35 (10.3%); £3,771,680.65 -> £3,381,909.53 (10.3%); £3,771,680.91 -> £3,381,909.57 (10.3%); £3,771,681.17 -> £3,381,909.61 (10.3%); £3,771,681.41 -> £3,381,909.65 (10.3%); £3,771,681.62 -> £3,381,909.69 (10.3%); £3,771,681.82 -> £3,381,909.72 (10.3%); £3,771,681.97 -> £3,381,909.76 (10.3%); £3,771,682.12 -> £3,381,909.80 (10.3%); £3,771,682.27 -> £3,381,909.83 (10.3%); £3,771,682.41 -> £3,381,909.87 (10.3%); £3,771,682.56 -> £3,381,909.91 (10.3%); £3,771,682.72 -> £3,381,909.94 (10.3%); £3,771,682.87 -> £3,381,909.98 (10.3%); £3,771,683.03 -> £3,381,910.02 (10.3%); £3,771,683.17 -> £3,381,910.06 (10.3%); £3,771,683.33 -> £3,381,910.09 (10.3%); £3,771,683.48 -> £3,381,910.13 (10.3%); £3,771,683.63 -> £3,381,910.33 (10.3%); £3,771,683.79 -> £3,381,910.54 (10.3%); £3,771,683.96 -> £3,381,910.75 (10.3%); £3,771,684.15 -> £3,381,910.98 (10.3%); £3,771,684.36 -> £3,381,911.23 (10.3%); £3,771,684.57 -> £3,381,911.49 (10.3%); £3,771,684.81 -> £3,381,911.79 (10.3%); £3,771,685.06 -> £3,381,912.11 (10.3%); £3,771,685.31 -> £3,381,912.24 (10.3%); £3,771,685.57 -> £3,381,912.36 (10.3%); £3,771,685.82 -> £3,381,912.50 (10.3%); £3,771,686.08 -> £3,381,912.63 (10.3%); £3,771,686.35 -> £3,381,912.75 (10.3%); £3,771,686.61 -> £3,381,912.88 (10.3%); £3,771,686.86 -> £3,381,912.99 (10.3%); £3,771,687.12 -> £3,381,913.11 (10.3%); £3,771,687.39 -> £3,381,913.23 (10.3%); £3,771,687.63 -> £3,381,913.34 (10.3%); £3,771,687.89 -> £3,381,913.46 (10.3%); £3,771,688.14 -> £3,381,913.57 (10.3%); £3,771,688.40 -> £3,381,913.68 (10.3%); £3,771,688.66 -> £3,381,913.99 (10.3%); £3,771,688.92 -> £3,381,914.27 (10.3%); £3,771,689.18 -> £3,381,914.51 (10.3%); £3,771,689.44 -> £3,381,914.73 (10.3%); £3,771,689.69 -> £3,381,914.95 (10.3%); £3,771,689.95 -> £3,381,915.16 (10.3%); £3,771,690.20 -> £3,381,915.38 (10.3%); £3,771,690.46 -> £3,381,915.58 (10.3%); £3,771,690.71 -> £3,381,915.79 (10.3%); £3,771,690.97 -> £3,381,916.00 (10.3%); £3,771,691.22 -> £3,381,916.21 (10.3%); £3,771,691.48 -> £3,381,916.25 (10.3%); £3,771,691.73 -> £3,381,916.29 (10.3%); £3,771,691.97 -> £3,381,916.33 (10.3%); £3,771,692.19 -> £3,381,916.37 (10.3%); £3,771,692.38 -> £3,381,916.40 (10.3%); £3,771,692.54 -> £3,381,916.44 (10.3%); £3,771,692.69 -> £3,381,916.48 (10.3%); £3,771,692.85 -> £3,381,916.52 (10.3%); £3,771,692.99 -> £3,381,916.56 (10.3%); £3,771,693.14 -> £3,381,916.59 (10.3%); £3,771,693.30 -> £3,381,916.63 (10.3%); £3,771,693.45 -> £3,381,916.67 (10.3%); £3,771,693.60 -> £3,381,916.70 (10.3%); £3,771,693.75 -> £3,381,916.74 (10.3%); £3,771,693.91 -> £3,381,916.78 (10.3%); £3,771,694.06 -> £3,381,916.82 (10.3%); £3,771,694.21 -> £3,381,917.01 (10.3%); £3,771,694.36 -> £3,381,917.19 (10.3%); £3,771,694.53 -> £3,381,917.39 (10.3%); £3,771,694.72 -> £3,381,917.60 (10.3%); £3,771,694.92 -> £3,381,917.84 (10.3%); £3,771,695.13 -> £3,381,918.09 (10.3%); £3,771,695.37 -> £3,381,918.37 (10.3%); £3,771,695.64 -> £3,381,918.65 (10.3%); £3,771,695.89 -> £3,381,918.77 (10.3%); £3,771,696.16 -> £3,381,918.89 (10.3%); £3,771,696.41 -> £3,381,919.02 (10.3%); £3,771,696.66 -> £3,381,919.14 (10.3%); £3,771,696.91 -> £3,381,919.27 (10.3%); £3,771,697.16 -> £3,381,919.39 (10.3%); £3,771,697.42 -> £3,381,919.51 (10.3%); £3,771,697.67 -> £3,381,919.62 (10.3%); £3,771,697.93 -> £3,381,919.74 (10.3%); £3,771,698.18 -> £3,381,919.85 (10.3%); £3,771,698.44 -> £3,381,919.96 (10.3%); £3,771,698.70 -> £3,381,920.07 (10.3%); £3,771,698.95 -> £3,381,920.18 (10.3%); £3,771,699.21 -> £3,381,920.46 (10.3%); £3,771,699.47 -> £3,381,920.72 (10.3%); £3,771,699.72 -> £3,381,920.96 (10.3%); £3,771,699.98 -> £3,381,921.18 (10.3%); £3,771,700.23 -> £3,381,921.38 (10.3%); £3,771,700.49 -> £3,381,921.59 (10.3%); £3,771,700.74 -> £3,381,921.79 (10.3%); £3,771,700.99 -> £3,381,921.99 (10.3%); £3,771,701.26 -> £3,381,922.19 (10.3%); £3,771,701.52 -> £3,381,922.38 (10.3%); £3,771,701.77 -> £3,381,922.56 (10.3%); £3,771,702.02 -> £3,381,922.60 (10.3%); £3,771,702.27 -> £3,381,922.64 (10.3%); £3,771,702.51 -> £3,381,922.68 (10.3%); £3,771,702.72 -> £3,381,922.72 (10.3%); £3,771,702.93 -> £3,381,922.76 (10.3%); £3,771,703.07 -> £3,381,922.79 (10.3%); £3,771,703.23 -> £3,381,922.83 (10.3%); £3,771,703.38 -> £3,381,922.87 (10.3%); £3,771,703.53 -> £3,381,922.91 (10.3%); £3,771,703.68 -> £3,381,922.95 (10.3%); £3,771,703.84 -> £3,381,922.98 (10.3%); £3,771,703.99 -> £3,381,923.02 (10.3%); £3,771,704.14 -> £3,381,923.06 (10.3%); £3,771,704.30 -> £3,381,923.10 (10.3%); £3,771,704.45 -> £3,381,923.13 (10.3%); £3,771,704.60 -> £3,381,923.17 (10.3%); £3,771,704.75 -> £3,381,923.37 (10.3%); £3,771,704.91 -> £3,381,923.56 (10.3%); £3,771,705.08 -> £3,381,923.76 (10.3%); £3,771,705.27 -> £3,381,923.98 (10.3%); £3,771,705.47 -> £3,381,924.21 (10.3%); £3,771,705.68 -> £3,381,924.47 (10.3%); £3,771,705.92 -> £3,381,924.75 (10.3%); £3,771,706.19 -> £3,381,925.04 (10.3%); £3,771,706.45 -> £3,381,925.16 (10.3%); £3,771,706.71 -> £3,381,925.29 (10.3%); £3,771,706.96 -> £3,381,925.41 (10.3%); £3,771,707.22 -> £3,381,925.54 (10.3%); £3,771,707.48 -> £3,381,925.66 (10.3%); £3,771,707.73 -> £3,381,925.78 (10.3%); £3,771,707.99 -> £3,381,925.90 (10.3%); £3,771,708.24 -> £3,381,926.02 (10.3%); £3,771,708.49 -> £3,381,926.14 (10.3%); £3,771,708.75 -> £3,381,926.26 (10.3%); £3,771,709.01 -> £3,381,926.37 (10.3%); £3,771,709.26 -> £3,381,926.48 (10.3%); £3,771,709.52 -> £3,381,926.59 (10.3%); £3,771,709.78 -> £3,381,926.87 (10.3%); £3,771,710.02 -> £3,381,927.13 (10.3%); £3,771,710.28 -> £3,381,927.36 (10.3%); £3,771,710.53 -> £3,381,927.57 (10.3%); £3,771,710.79 -> £3,381,927.78 (10.3%); £3,771,711.04 -> £3,381,927.98 (10.3%); £3,771,711.29 -> £3,381,928.17 (10.3%); £3,771,711.55 -> £3,381,928.37 (10.3%); £3,771,711.81 -> £3,381,928.56 (10.3%); £3,771,712.06 -> £3,381,928.74 (10.3%); £3,771,712.30 -> £3,381,928.92 (10.3%); £3,771,712.57 -> £3,381,928.97 (10.3%); £3,771,712.82 -> £3,381,929.01 (10.3%); £3,771,713.06 -> £3,381,929.05 (10.3%); £3,771,713.27 -> £3,381,929.08 (10.3%); £3,771,713.47 -> £3,381,929.12 (10.3%); £3,771,713.60 -> £3,381,929.16 (10.3%); £3,771,713.73 -> £3,381,929.20 (10.3%); £3,771,713.86 -> £3,381,929.23 (10.3%); £3,771,714.00 -> £3,381,929.27 (10.3%); £3,771,714.13 -> £3,381,929.31 (10.3%); £3,771,714.26 -> £3,381,929.34 (10.3%); £3,771,714.40 -> £3,381,929.38 (10.3%); £3,771,714.54 -> £3,381,929.42 (10.3%); £3,771,714.67 -> £3,381,929.46 (10.3%); £3,771,714.80 -> £3,381,929.49 (10.3%); £3,771,714.93 -> £3,381,929.53 (10.3%); £3,771,715.07 -> £3,381,929.70 (10.3%); £3,771,715.21 -> £3,381,929.87 (10.3%); £3,771,715.36 -> £3,381,930.05 (10.3%); £3,771,715.52 -> £3,381,930.23 (10.3%); £3,771,715.70 -> £3,381,930.43 (10.3%); £3,771,715.90 -> £3,381,930.64 (10.3%); £3,771,716.11 -> £3,381,930.86 (10.3%); £3,771,716.33 -> £3,381,931.09 (10.3%); £3,771,716.56 -> £3,381,931.18 (10.3%); £3,771,716.78 -> £3,381,931.27 (10.3%); £3,771,717.00 -> £3,381,931.36 (10.3%); £3,771,717.22 -> £3,381,931.45 (10.3%); £3,771,717.45 -> £3,381,931.53 (10.3%); £3,771,717.68 -> £3,381,931.61 (10.3%); £3,771,717.90 -> £3,381,931.68 (10.3%); £3,771,718.12 -> £3,381,931.75 (10.3%); £3,771,718.35 -> £3,381,931.82 (10.3%); £3,771,718.58 -> £3,381,931.89 (10.3%); £3,771,718.81 -> £3,381,931.96 (10.3%); £3,771,719.04 -> £3,381,932.03 (10.3%); £3,771,719.26 -> £3,381,932.10 (10.3%); £3,771,719.48 -> £3,381,932.31 (10.3%); £3,771,719.71 -> £3,381,932.52 (10.3%); £3,771,719.93 -> £3,381,932.71 (10.3%); £3,771,720.17 -> £3,381,932.89 (10.3%); £3,771,720.39 -> £3,381,933.07 (10.3%); £3,771,720.61 -> £3,381,933.26 (10.3%); £3,771,720.83 -> £3,381,933.44 (10.3%); £3,771,721.06 -> £3,381,933.63 (10.3%); £3,771,721.27 -> £3,381,933.81 (10.3%); £3,771,721.50 -> £3,381,933.99 (10.3%); £3,771,721.72 -> £3,381,934.16 (10.3%); £3,771,721.94 -> £3,381,934.20 (10.3%); £3,771,722.16 -> £3,381,934.24 (10.3%); £3,771,722.37 -> £3,381,934.28 (10.3%); £3,771,722.56 -> £3,381,934.32 (10.3%); £3,771,722.74 -> £3,381,934.35 (10.3%); £3,771,722.87 -> £3,381,934.39 (10.3%); £3,771,723.00 -> £3,381,934.43 (10.3%); £3,771,723.14 -> £3,381,934.47 (10.3%); £3,771,723.27 -> £3,381,934.51 (10.3%); £3,771,723.41 -> £3,381,934.55 (10.3%); £3,771,723.54 -> £3,381,934.58 (10.3%); £3,771,723.68 -> £3,381,934.62 (10.3%); £3,771,723.82 -> £3,381,934.66 (10.3%); £3,771,723.95 -> £3,381,934.70 (10.3%); £3,771,724.09 -> £3,381,934.73 (10.3%); £3,771,724.22 -> £3,381,934.77 (10.3%); £3,771,724.36 -> £3,381,934.93 (10.3%); £3,771,724.49 -> £3,381,935.09 (10.3%); £3,771,724.64 -> £3,381,935.26 (10.3%); £3,771,724.81 -> £3,381,935.42 (10.3%); £3,771,724.99 -> £3,381,935.59 (10.3%); £3,771,725.19 -> £3,381,935.75 (10.3%); £3,771,725.39 -> £3,381,935.92 (10.3%); £3,771,725.61 -> £3,381,936.09 (10.3%); £3,771,725.85 -> £3,381,936.14 (10.3%); £3,771,726.07 -> £3,381,936.19 (10.3%); £3,771,726.30 -> £3,381,936.24 (10.3%); £3,771,726.52 -> £3,381,936.29 (10.3%); £3,771,726.74 -> £3,381,936.33 (10.3%); £3,771,726.97 -> £3,381,936.38 (10.3%); £3,771,727.19 -> £3,381,936.43 (10.3%); £3,771,727.41 -> £3,381,936.47 (10.3%); £3,771,727.63 -> £3,381,936.52 (10.3%); £3,771,727.86 -> £3,381,936.56 (10.3%); £3,771,728.09 -> £3,381,936.61 (10.3%); £3,771,728.31 -> £3,381,936.66 (10.3%); £3,771,728.53 -> £3,381,936.70 (10.3%); £3,771,728.76 -> £3,381,936.88 (10.3%); £3,771,728.98 -> £3,381,937.06 (10.3%); £3,771,729.21 -> £3,381,937.23 (10.3%); £3,771,729.44 -> £3,381,937.40 (10.3%); £3,771,729.66 -> £3,381,937.57 (10.3%); £3,771,729.87 -> £3,381,937.74 (10.3%); £3,771,730.09 -> £3,381,937.91 (10.3%); £3,771,730.30 -> £3,381,938.07 (10.3%); £3,771,730.53 -> £3,381,938.24 (10.3%); £3,771,730.76 -> £3,381,938.40 (10.3%); £3,771,730.98 -> £3,381,938.57 (10.3%); £3,771,731.21 -> £3,381,938.61 (10.3%); £3,771,731.43 -> £3,381,938.65 (10.3%); £3,771,731.64 -> £3,381,938.68 (10.3%); £3,771,731.83 -> £3,381,938.72 (10.3%); £3,771,732.01 -> £3,381,938.75 (10.3%); £3,771,732.16 -> £3,381,938.79 (10.3%); £3,771,732.31 -> £3,381,938.83 (10.3%); £3,771,732.46 -> £3,381,938.87 (10.3%); £3,771,732.62 -> £3,381,938.91 (10.3%); £3,771,732.77 -> £3,381,938.94 (10.3%); £3,771,732.92 -> £3,381,938.98 (10.3%); £3,771,733.07 -> £3,381,939.02 (10.3%); £3,771,733.22 -> £3,381,939.06 (10.3%); £3,771,733.38 -> £3,381,939.09 (10.3%); £3,771,733.53 -> £3,381,939.13 (10.3%); £3,771,733.68 -> £3,381,939.17 (10.3%); £3,771,733.82 -> £3,381,939.35 (10.3%); £3,771,733.97 -> £3,381,939.54 (10.3%); £3,771,734.14 -> £3,381,939.73 (10.3%); £3,771,734.33 -> £3,381,939.92 (10.3%); £3,771,734.54 -> £3,381,940.14 (10.3%); £3,771,734.76 -> £3,381,940.38 (10.3%); £3,771,735.00 -> £3,381,940.64 (10.3%); £3,771,735.25 -> £3,381,940.91 (10.3%); £3,771,735.50 -> £3,381,941.03 (10.3%); £3,771,735.75 -> £3,381,941.16 (10.3%); £3,771,736.01 -> £3,381,941.28 (10.3%); £3,771,736.27 -> £3,381,941.40 (10.3%); £3,771,736.51 -> £3,381,941.53 (10.3%); £3,771,736.78 -> £3,381,941.65 (10.3%); £3,771,737.02 -> £3,381,941.76 (10.3%); £3,771,737.27 -> £3,381,941.87 (10.3%); £3,771,737.52 -> £3,381,941.99 (10.3%); £3,771,737.78 -> £3,381,942.10 (10.3%); £3,771,738.03 -> £3,381,942.21 (10.3%); £3,771,738.29 -> £3,381,942.31 (10.3%); £3,771,738.54 -> £3,381,942.42 (10.3%); £3,771,738.79 -> £3,381,942.67 (10.3%); £3,771,739.04 -> £3,381,942.91 (10.3%); £3,771,739.30 -> £3,381,943.12 (10.3%); £3,771,739.56 -> £3,381,943.31 (10.3%); £3,771,739.81 -> £3,381,943.49 (10.3%); £3,771,740.07 -> £3,381,943.69 (10.3%); £3,771,740.31 -> £3,381,943.88 (10.3%); £3,771,740.56 -> £3,381,944.07 (10.3%); £3,771,740.81 -> £3,381,944.26 (10.3%); £3,771,741.07 -> £3,381,944.43 (10.3%); £3,771,741.33 -> £3,381,944.60 (10.3%); £3,771,741.58 -> £3,381,944.64 (10.3%); £3,771,741.84 -> £3,381,944.69 (10.3%); £3,771,742.06 -> £3,381,944.73 (10.3%); £3,771,742.28 -> £3,381,944.76 (10.3%); £3,771,742.47 -> £3,381,944.80 (10.3%); £3,771,742.62 -> £3,381,944.84 (10.3%); £3,771,742.77 -> £3,381,944.88 (10.3%); £3,771,742.92 -> £3,381,944.91 (10.3%); £3,771,743.07 -> £3,381,944.95 (10.3%); £3,771,743.22 -> £3,381,944.99 (10.3%); £3,771,743.37 -> £3,381,945.02 (10.3%); £3,771,743.52 -> £3,381,945.06 (10.3%); £3,771,743.67 -> £3,381,945.10 (10.3%); £3,771,743.82 -> £3,381,945.14 (10.3%); £3,771,743.97 -> £3,381,945.18 (10.3%); £3,771,744.12 -> £3,381,945.22 (10.3%); £3,771,744.26 -> £3,381,945.35 (10.3%); £3,771,744.42 -> £3,381,945.50 (10.3%); £3,771,744.59 -> £3,381,945.66 (10.3%); £3,771,744.78 -> £3,381,945.83 (10.3%); £3,771,744.98 -> £3,381,946.03 (10.3%); £3,771,745.19 -> £3,381,946.24 (10.3%); £3,771,745.43 -> £3,381,946.48 (10.3%); £3,771,745.68 -> £3,381,946.72 (10.3%); £3,771,745.93 -> £3,381,946.84 (10.3%); £3,771,746.18 -> £3,381,946.97 (10.3%); £3,771,746.43 -> £3,381,947.10 (10.3%); £3,771,746.69 -> £3,381,947.23 (10.3%); £3,771,746.94 -> £3,381,947.35 (10.3%); £3,771,747.19 -> £3,381,947.48 (10.3%); £3,771,747.44 -> £3,381,947.60 (10.3%); £3,771,747.69 -> £3,381,947.72 (10.3%); £3,771,747.94 -> £3,381,947.83 (10.3%); £3,771,748.19 -> £3,381,947.94 (10.3%); £3,771,748.45 -> £3,381,948.05 (10.3%); £3,771,748.70 -> £3,381,948.16 (10.3%); £3,771,748.96 -> £3,381,948.27 (10.3%); £3,771,749.21 -> £3,381,948.51 (10.3%); £3,771,749.47 -> £3,381,948.73 (10.3%); £3,771,749.72 -> £3,381,948.92 (10.3%); £3,771,749.98 -> £3,381,949.08 (10.3%); £3,771,750.24 -> £3,381,949.25 (10.3%); £3,771,750.50 -> £3,381,949.41 (10.3%); £3,771,750.75 -> £3,381,949.57 (10.3%); £3,771,751.00 -> £3,381,949.72 (10.3%); £3,771,751.24 -> £3,381,949.87 (10.3%); £3,771,751.48 -> £3,381,950.01 (10.3%); £3,771,751.73 -> £3,381,950.15 (10.3%); £3,771,751.98 -> £3,381,950.19 (10.3%); £3,771,752.23 -> £3,381,950.23 (10.3%); £3,771,752.47 -> £3,381,950.27 (10.3%); £3,771,752.69 -> £3,381,950.31 (10.3%); £3,771,752.88 -> £3,381,950.34 (10.3%); £3,771,753.03 -> £3,381,950.38 (10.3%); £3,771,753.18 -> £3,381,950.42 (10.3%); £3,771,753.34 -> £3,381,950.46 (10.3%); £3,771,753.49 -> £3,381,950.50 (10.3%); £3,771,753.64 -> £3,381,950.53 (10.3%); £3,771,753.79 -> £3,381,950.57 (10.3%); £3,771,753.94 -> £3,381,950.61 (10.3%); £3,771,754.09 -> £3,381,950.65 (10.3%); £3,771,754.24 -> £3,381,950.68 (10.3%); £3,771,754.39 -> £3,381,950.72 (10.3%); £3,771,754.55 -> £3,381,950.76 (10.3%); £3,771,754.70 -> £3,381,950.87 (10.3%); £3,771,754.85 -> £3,381,950.98 (10.3%); £3,771,755.02 -> £3,381,951.11 (10.3%); £3,771,755.20 -> £3,381,951.24 (10.3%); £3,771,755.39 -> £3,381,951.41 (10.3%); £3,771,755.61 -> £3,381,951.60 (10.3%); £3,771,755.85 -> £3,381,951.80 (10.3%); £3,771,756.10 -> £3,381,952.02 (10.3%); £3,771,756.35 -> £3,381,952.15 (10.3%); £3,771,756.60 -> £3,381,952.28 (10.3%); £3,771,756.86 -> £3,381,952.41 (10.3%); £3,771,757.11 -> £3,381,952.53 (10.3%); £3,771,757.36 -> £3,381,952.66 (10.3%); £3,771,757.61 -> £3,381,952.78 (10.3%); £3,771,757.86 -> £3,381,952.90 (10.3%); £3,771,758.12 -> £3,381,953.02 (10.3%); £3,771,758.37 -> £3,381,953.14 (10.3%); £3,771,758.61 -> £3,381,953.25 (10.3%); £3,771,758.86 -> £3,381,953.37 (10.3%); £3,771,759.11 -> £3,381,953.49 (10.3%); £3,771,759.35 -> £3,381,953.59 (10.3%); £3,771,759.60 -> £3,381,953.80 (10.3%); £3,771,759.86 -> £3,381,953.99 (10.3%); £3,771,760.10 -> £3,381,954.15 (10.3%); £3,771,760.35 -> £3,381,954.30 (10.3%); £3,771,760.60 -> £3,381,954.43 (10.3%); £3,771,760.84 -> £3,381,954.56 (10.3%); £3,771,761.09 -> £3,381,954.69 (10.3%); £3,771,761.35 -> £3,381,954.81 (10.3%); £3,771,761.59 -> £3,381,954.94 (10.3%); £3,771,761.84 -> £3,381,955.05 (10.3%); £3,771,762.08 -> £3,381,955.16 (10.3%); £3,771,762.33 -> £3,381,955.20 (10.3%); £3,771,762.59 -> £3,381,955.25 (10.3%); £3,771,762.83 -> £3,381,955.29 (10.3%); £3,771,763.04 -> £3,381,955.32 (10.3%); £3,771,763.23 -> £3,381,955.36 (10.3%); £3,771,763.38 -> £3,381,955.40 (10.3%); £3,771,763.53 -> £3,381,955.43 (10.3%); £3,771,763.69 -> £3,381,955.47 (10.3%); £3,771,763.84 -> £3,381,955.51 (10.3%); £3,771,763.99 -> £3,381,955.55 (10.3%); £3,771,764.14 -> £3,381,955.58 (10.3%); £3,771,764.29 -> £3,381,955.62 (10.3%); £3,771,764.44 -> £3,381,955.66 (10.3%); £3,771,764.59 -> £3,381,955.70 (10.3%); £3,771,764.75 -> £3,381,955.74 (10.3%); £3,771,764.90 -> £3,381,955.78 (10.3%); £3,771,765.05 -> £3,381,955.88 (10.3%); £3,771,765.19 -> £3,381,955.99 (10.3%); £3,771,765.36 -> £3,381,956.12 (10.3%); £3,771,765.54 -> £3,381,956.25 (10.3%); £3,771,765.74 -> £3,381,956.41 (10.3%); £3,771,765.96 -> £3,381,956.59 (10.3%); £3,771,766.19 -> £3,381,956.78 (10.3%); £3,771,766.44 -> £3,381,957.00 (10.3%); £3,771,766.70 -> £3,381,957.13 (10.3%); £3,771,766.95 -> £3,381,957.25 (10.3%); £3,771,767.20 -> £3,381,957.37 (10.3%); £3,771,767.45 -> £3,381,957.50 (10.3%); £3,771,767.70 -> £3,381,957.62 (10.3%); £3,771,767.96 -> £3,381,957.74 (10.3%); £3,771,768.21 -> £3,381,957.86 (10.3%); £3,771,768.46 -> £3,381,957.97 (10.3%); £3,771,768.71 -> £3,381,958.09 (10.3%); £3,771,768.96 -> £3,381,958.20 (10.3%); £3,771,769.21 -> £3,381,958.32 (10.3%); £3,771,769.47 -> £3,381,958.43 (10.3%); £3,771,769.73 -> £3,381,958.53 (10.3%); £3,771,769.98 -> £3,381,958.73 (10.3%); £3,771,770.24 -> £3,381,958.91 (10.3%); £3,771,770.49 -> £3,381,959.07 (10.3%); £3,771,770.75 -> £3,381,959.21 (10.3%); £3,771,771.01 -> £3,381,959.35 (10.3%); £3,771,771.26 -> £3,381,959.47 (10.3%); £3,771,771.50 -> £3,381,959.60 (10.3%); £3,771,771.76 -> £3,381,959.72 (10.3%); £3,771,772.01 -> £3,381,959.84 (10.3%); £3,771,772.26 -> £3,381,959.95 (10.3%); £3,771,772.51 -> £3,381,960.06 (10.3%); £3,771,772.76 -> £3,381,960.10 (10.3%); £3,771,773.02 -> £3,381,960.15 (10.3%); £3,771,773.24 -> £3,381,960.18 (10.3%); £3,771,773.46 -> £3,381,960.22 (10.3%); £3,771,773.66 -> £3,381,960.26 (10.3%); £3,771,773.81 -> £3,381,960.30 (10.3%); £3,771,773.96 -> £3,381,960.34 (10.3%); £3,771,774.11 -> £3,381,960.37 (10.3%); £3,771,774.26 -> £3,381,960.41 (10.3%); £3,771,774.41 -> £3,381,960.45 (10.3%); £3,771,774.56 -> £3,381,960.49 (10.3%); £3,771,774.72 -> £3,381,960.53 (10.3%); £3,771,774.87 -> £3,381,960.56 (10.3%); £3,771,775.02 -> £3,381,960.60 (10.3%); £3,771,775.17 -> £3,381,960.64 (10.3%); £3,771,775.32 -> £3,381,960.68 (10.3%); £3,771,775.47 -> £3,381,960.83 (10.3%); £3,771,775.62 -> £3,381,960.98 (10.3%); £3,771,775.79 -> £3,381,961.14 (10.3%); £3,771,775.97 -> £3,381,961.32 (10.3%); £3,771,776.18 -> £3,381,961.52 (10.3%); £3,771,776.40 -> £3,381,961.73 (10.3%); £3,771,776.63 -> £3,381,961.96 (10.3%); £3,771,776.89 -> £3,381,962.20 (10.3%); £3,771,777.15 -> £3,381,962.33 (10.3%); £3,771,777.39 -> £3,381,962.46 (10.3%); £3,771,777.64 -> £3,381,962.59 (10.3%); £3,771,777.89 -> £3,381,962.73 (10.3%); £3,771,778.14 -> £3,381,962.87 (10.3%); £3,771,778.39 -> £3,381,962.99 (10.3%); £3,771,778.64 -> £3,381,963.12 (10.3%); £3,771,778.89 -> £3,381,963.24 (10.3%); £3,771,779.15 -> £3,381,963.36 (10.3%); £3,771,779.40 -> £3,381,963.48 (10.3%); £3,771,779.65 -> £3,381,963.60 (10.3%); £3,771,779.90 -> £3,381,963.71 (10.3%); £3,771,780.15 -> £3,381,963.82 (10.3%); £3,771,780.40 -> £3,381,964.05 (10.3%); £3,771,780.66 -> £3,381,964.27 (10.3%); £3,771,780.91 -> £3,381,964.45 (10.3%); £3,771,781.16 -> £3,381,964.62 (10.3%); £3,771,781.41 -> £3,381,964.78 (10.3%); £3,771,781.66 -> £3,381,964.94 (10.3%); £3,771,781.91 -> £3,381,965.08 (10.3%); £3,771,782.16 -> £3,381,965.23 (10.3%); £3,771,782.42 -> £3,381,965.37 (10.3%); £3,771,782.67 -> £3,381,965.51 (10.3%); £3,771,782.93 -> £3,381,965.65 (10.3%); £3,771,783.18 -> £3,381,965.69 (10.3%); £3,771,783.43 -> £3,381,965.73 (10.3%); £3,771,783.66 -> £3,381,965.77 (10.3%); £3,771,783.87 -> £3,381,965.80 (10.3%); £3,771,784.06 -> £3,381,965.84 (10.3%); £3,771,784.20 -> £3,381,965.88 (10.3%); £3,771,784.33 -> £3,381,965.92 (10.3%); £3,771,784.46 -> £3,381,965.95 (10.3%); £3,771,784.60 -> £3,381,965.99 (10.3%); £3,771,784.74 -> £3,381,966.03 (10.3%); £3,771,784.87 -> £3,381,966.06 (10.3%); £3,771,785.01 -> £3,381,966.10 (10.3%); £3,771,785.15 -> £3,381,966.14 (10.3%); £3,771,785.28 -> £3,381,966.18 (10.3%); £3,771,785.41 -> £3,381,966.21 (10.3%); £3,771,785.55 -> £3,381,966.25 (10.3%); £3,771,785.69 -> £3,381,966.42 (10.3%); £3,771,785.83 -> £3,381,966.59 (10.3%); £3,771,785.97 -> £3,381,966.77 (10.3%); £3,771,786.14 -> £3,381,966.96 (10.3%); £3,771,786.32 -> £3,381,967.15 (10.3%); £3,771,786.52 -> £3,381,967.36 (10.3%); £3,771,786.73 -> £3,381,967.59 (10.3%); £3,771,786.95 -> £3,381,967.82 (10.3%); £3,771,787.18 -> £3,381,967.91 (10.3%); £3,771,787.40 -> £3,381,968.01 (10.3%); £3,771,787.62 -> £3,381,968.10 (10.3%); £3,771,787.85 -> £3,381,968.19 (10.3%); £3,771,788.08 -> £3,381,968.27 (10.3%); £3,771,788.30 -> £3,381,968.35 (10.3%); £3,771,788.52 -> £3,381,968.42 (10.3%); £3,771,788.75 -> £3,381,968.50 (10.3%); £3,771,788.96 -> £3,381,968.57 (10.3%); £3,771,789.18 -> £3,381,968.64 (10.3%); £3,771,789.40 -> £3,381,968.70 (10.3%); £3,771,789.62 -> £3,381,968.77 (10.3%); £3,771,789.83 -> £3,381,968.84 (10.3%); £3,771,790.06 -> £3,381,969.04 (10.3%); £3,771,790.29 -> £3,381,969.24 (10.3%); £3,771,790.51 -> £3,381,969.42 (10.3%); £3,771,790.74 -> £3,381,969.60 (10.3%); £3,771,790.96 -> £3,381,969.78 (10.3%); £3,771,791.20 -> £3,381,969.96 (10.3%); £3,771,791.41 -> £3,381,970.13 (10.3%); £3,771,791.64 -> £3,381,970.31 (10.3%); £3,771,791.86 -> £3,381,970.48 (10.3%); £3,771,792.08 -> £3,381,970.65 (10.3%); £3,771,792.31 -> £3,381,970.84 (10.3%); £3,771,792.53 -> £3,381,970.88 (10.3%); £3,771,792.75 -> £3,381,970.92 (10.3%); £3,771,792.95 -> £3,381,970.96 (10.3%); £3,771,793.14 -> £3,381,971.00 (10.3%); £3,771,793.32 -> £3,381,971.03 (10.3%); £3,771,793.45 -> £3,381,971.07 (10.3%); £3,771,793.59 -> £3,381,971.11 (10.3%); £3,771,793.72 -> £3,381,971.15 (10.3%); £3,771,793.85 -> £3,381,971.19 (10.3%); £3,771,793.99 -> £3,381,971.22 (10.3%); £3,771,794.13 -> £3,381,971.26 (10.3%); £3,771,794.26 -> £3,381,971.30 (10.3%); £3,771,794.39 -> £3,381,971.33 (10.3%); £3,771,794.53 -> £3,381,971.37 (10.3%); £3,771,794.67 -> £3,381,971.41 (10.3%); £3,771,794.81 -> £3,381,971.44 (10.3%); £3,771,794.94 -> £3,381,971.54 (10.3%); £3,771,795.08 -> £3,381,971.64 (10.3%); £3,771,795.23 -> £3,381,971.74 (10.3%); £3,771,795.40 -> £3,381,971.85 (10.3%); £3,771,795.58 -> £3,381,971.95 (10.3%); £3,771,795.78 -> £3,381,972.05 (10.3%); £3,771,795.99 -> £3,381,972.16 (10.3%); £3,771,796.22 -> £3,381,972.27 (10.3%); £3,771,796.45 -> £3,381,972.31 (10.3%); £3,771,796.67 -> £3,381,972.36 (10.3%); £3,771,796.89 -> £3,381,972.41 (10.3%); £3,771,797.12 -> £3,381,972.46 (10.3%); £3,771,797.34 -> £3,381,972.50 (10.3%); £3,771,797.57 -> £3,381,972.55 (10.3%); £3,771,797.80 -> £3,381,972.60 (10.3%); £3,771,798.03 -> £3,381,972.64 (10.3%); £3,771,798.25 -> £3,381,972.69 (10.3%); £3,771,798.48 -> £3,381,972.74 (10.3%); £3,771,798.71 -> £3,381,972.78 (10.3%); £3,771,798.94 -> £3,381,972.83 (10.3%); £3,771,799.17 -> £3,381,972.87 (10.3%); £3,771,799.39 -> £3,381,972.99 (10.3%); £3,771,799.61 -> £3,381,973.10 (10.3%); £3,771,799.84 -> £3,381,973.21 (10.3%); £3,771,800.07 -> £3,381,973.33 (10.3%); £3,771,800.30 -> £3,381,973.44 (10.3%); £3,771,800.52 -> £3,381,973.56 (10.3%); £3,771,800.74 -> £3,381,973.67 (10.3%); £3,771,800.97 -> £3,381,973.78 (10.3%); £3,771,801.19 -> £3,381,973.89 (10.3%); £3,771,801.41 -> £3,381,974.00 (10.3%); £3,771,801.64 -> £3,381,974.11 (10.3%); £3,771,801.87 -> £3,381,974.15 (10.3%); £3,771,802.09 -> £3,381,974.19 (10.3%); £3,771,802.31 -> £3,381,974.22 (10.3%); £3,771,802.51 -> £3,381,974.26 (10.3%); £3,771,802.68 -> £3,381,974.30 (10.3%); £3,771,802.84 -> £3,381,974.33 (10.3%); £3,771,802.99 -> £3,381,974.37 (10.3%); £3,771,803.15 -> £3,381,974.41 (10.3%); £3,771,803.30 -> £3,381,974.44 (10.3%); £3,771,803.45 -> £3,381,974.48 (10.3%); £3,771,803.60 -> £3,381,974.52 (10.3%); £3,771,803.76 -> £3,381,974.56 (10.3%); £3,771,803.91 -> £3,381,974.59 (10.3%); £3,771,804.06 -> £3,381,974.63 (10.3%); £3,771,804.21 -> £3,381,974.67 (10.3%); £3,771,804.37 -> £3,381,974.71 (10.3%); £3,771,804.52 -> £3,381,974.85 (10.3%); £3,771,804.68 -> £3,381,974.98 (10.3%); £3,771,804.85 -> £3,381,975.12 (10.3%); £3,771,805.04 -> £3,381,975.27 (10.3%); £3,771,805.24 -> £3,381,975.46 (10.3%); £3,771,805.47 -> £3,381,975.66 (10.3%); £3,771,805.71 -> £3,381,975.89 (10.3%); £3,771,805.97 -> £3,381,976.14 (10.3%); £3,771,806.22 -> £3,381,976.26 (10.3%); £3,771,806.48 -> £3,381,976.39 (10.3%); £3,771,806.73 -> £3,381,976.51 (10.3%); £3,771,806.98 -> £3,381,976.64 (10.3%); £3,771,807.23 -> £3,381,976.77 (10.3%); £3,771,807.48 -> £3,381,976.89 (10.3%); £3,771,807.73 -> £3,381,977.01 (10.3%); £3,771,807.99 -> £3,381,977.13 (10.3%); £3,771,808.26 -> £3,381,977.25 (10.3%); £3,771,808.52 -> £3,381,977.36 (10.3%); £3,771,808.77 -> £3,381,977.47 (10.3%); £3,771,809.03 -> £3,381,977.59 (10.3%); £3,771,809.29 -> £3,381,977.70 (10.3%); £3,771,809.55 -> £3,381,977.94 (10.3%); £3,771,809.81 -> £3,381,978.16 (10.3%); £3,771,810.07 -> £3,381,978.35 (10.3%); £3,771,810.31 -> £3,381,978.51 (10.3%); £3,771,810.58 -> £3,381,978.66 (10.3%); £3,771,810.84 -> £3,381,978.81 (10.3%); £3,771,811.09 -> £3,381,978.96 (10.3%); £3,771,811.34 -> £3,381,979.10 (10.3%); £3,771,811.60 -> £3,381,979.25 (10.3%); £3,771,811.85 -> £3,381,979.39 (10.3%); £3,771,812.11 -> £3,381,979.53 (10.3%); £3,771,812.37 -> £3,381,979.57 (10.3%); £3,771,812.63 -> £3,381,979.61 (10.3%); £3,771,812.86 -> £3,381,979.65 (10.3%); £3,771,813.08 -> £3,381,979.69 (10.3%); £3,771,813.27 -> £3,381,979.73 (10.3%); £3,771,813.43 -> £3,381,979.76 (10.3%); £3,771,813.59 -> £3,381,979.80 (10.3%); £3,771,813.75 -> £3,381,979.84 (10.3%); £3,771,813.90 -> £3,381,979.88 (10.3%); £3,771,814.05 -> £3,381,979.91 (10.3%); £3,771,814.20 -> £3,381,979.95 (10.3%); £3,771,814.36 -> £3,381,979.99 (10.3%); £3,771,814.51 -> £3,381,980.03 (10.3%); £3,771,814.67 -> £3,381,980.07 (10.3%); £3,771,814.82 -> £3,381,980.10 (10.3%); £3,771,814.98 -> £3,381,980.14 (10.3%); £3,771,815.14 -> £3,381,980.26 (10.3%); £3,771,815.29 -> £3,381,980.38 (10.3%); £3,771,815.46 -> £3,381,980.51 (10.3%); £3,771,815.66 -> £3,381,980.65 (10.3%); £3,771,815.87 -> £3,381,980.82 (10.3%); £3,771,816.09 -> £3,381,981.02 (10.3%); £3,771,816.33 -> £3,381,981.25 (10.3%); £3,771,816.59 -> £3,381,981.47 (10.3%); £3,771,816.84 -> £3,381,981.59 (10.3%); £3,771,817.10 -> £3,381,981.72 (10.3%); £3,771,817.35 -> £3,381,981.86 (10.3%); £3,771,817.61 -> £3,381,981.98 (10.3%); £3,771,817.86 -> £3,381,982.11 (10.3%); £3,771,818.12 -> £3,381,982.23 (10.3%); £3,771,818.39 -> £3,381,982.34 (10.3%); £3,771,818.65 -> £3,381,982.46 (10.3%); £3,771,818.92 -> £3,381,982.57 (10.3%); £3,771,819.18 -> £3,381,982.68 (10.3%); £3,771,819.44 -> £3,381,982.80 (10.3%); £3,771,819.70 -> £3,381,982.91 (10.3%); £3,771,819.95 -> £3,381,983.02 (10.3%); £3,771,820.20 -> £3,381,983.23 (10.3%); £3,771,820.46 -> £3,381,983.42 (10.3%); £3,771,820.72 -> £3,381,983.58 (10.3%); £3,771,820.98 -> £3,381,983.71 (10.3%); £3,771,821.23 -> £3,381,983.84 (10.3%); £3,771,821.49 -> £3,381,983.98 (10.3%); £3,771,821.75 -> £3,381,984.11 (10.3%); £3,771,822.02 -> £3,381,984.24 (10.3%); £3,771,822.27 -> £3,381,984.37 (10.3%); £3,771,822.52 -> £3,381,984.49 (10.3%); £3,771,822.78 -> £3,381,984.60 (10.3%); £3,771,823.04 -> £3,381,984.64 (10.3%); £3,771,823.29 -> £3,381,984.68 (10.3%); £3,771,823.53 -> £3,381,984.72 (10.3%); £3,771,823.75 -> £3,381,984.76 (10.3%); £3,771,823.94 -> £3,381,984.80 (10.3%); £3,771,824.10 -> £3,381,984.83 (10.3%); £3,771,824.26 -> £3,381,984.87 (10.3%); £3,771,824.40 -> £3,381,984.91 (10.3%); £3,771,824.56 -> £3,381,984.94 (10.3%); £3,771,824.71 -> £3,381,984.98 (10.3%); £3,771,824.86 -> £3,381,985.02 (10.3%); £3,771,825.02 -> £3,381,985.05 (10.3%); £3,771,825.18 -> £3,381,985.09 (10.3%); £3,771,825.33 -> £3,381,985.13 (10.3%); £3,771,825.49 -> £3,381,985.17 (10.3%); £3,771,825.65 -> £3,381,985.21 (10.3%); £3,771,825.81 -> £3,381,985.34 (10.3%); £3,771,825.96 -> £3,381,985.48 (10.3%); £3,771,826.13 -> £3,381,985.63 (10.3%); £3,771,826.32 -> £3,381,985.79 (10.3%); £3,771,826.53 -> £3,381,985.97 (10.3%); £3,771,826.76 -> £3,381,986.17 (10.3%); £3,771,827.00 -> £3,381,986.40 (10.3%); £3,771,827.26 -> £3,381,986.63 (10.3%); £3,771,827.52 -> £3,381,986.75 (10.3%); £3,771,827.77 -> £3,381,986.88 (10.3%); £3,771,828.02 -> £3,381,987.01 (10.3%); £3,771,828.28 -> £3,381,987.14 (10.3%); £3,771,828.54 -> £3,381,987.26 (10.3%); £3,771,828.80 -> £3,381,987.38 (10.3%); £3,771,829.05 -> £3,381,987.50 (10.3%); £3,771,829.30 -> £3,381,987.61 (10.3%); £3,771,829.55 -> £3,381,987.72 (10.3%); £3,771,829.81 -> £3,381,987.84 (10.3%); £3,771,830.07 -> £3,381,987.95 (10.3%); £3,771,830.32 -> £3,381,988.07 (10.3%); £3,771,830.59 -> £3,381,988.18 (10.3%); £3,771,830.84 -> £3,381,988.42 (10.3%); £3,771,831.10 -> £3,381,988.64 (10.3%); £3,771,831.36 -> £3,381,988.80 (10.3%); £3,771,831.62 -> £3,381,988.95 (10.3%); £3,771,831.87 -> £3,381,989.10 (10.3%); £3,771,832.14 -> £3,381,989.24 (10.3%); £3,771,832.39 -> £3,381,989.39 (10.3%); £3,771,832.65 -> £3,381,989.53 (10.3%); £3,771,832.90 -> £3,381,989.68 (10.3%); £3,771,833.16 -> £3,381,989.82 (10.3%); £3,771,833.41 -> £3,381,989.96 (10.3%); £3,771,833.66 -> £3,381,990.00 (10.3%); £3,771,833.92 -> £3,381,990.04 (10.3%); £3,771,834.17 -> £3,381,990.08 (10.3%); £3,771,834.39 -> £3,381,990.11 (10.3%); £3,771,834.59 -> £3,381,990.15 (10.3%); £3,771,834.75 -> £3,381,990.19 (10.3%); £3,771,834.90 -> £3,381,990.23 (10.3%); £3,771,835.05 -> £3,381,990.26 (10.3%); £3,771,835.20 -> £3,381,990.30 (10.3%); £3,771,835.36 -> £3,381,990.34 (10.3%); £3,771,835.51 -> £3,381,990.38 (10.3%); £3,771,835.66 -> £3,381,990.41 (10.3%); £3,771,835.81 -> £3,381,990.45 (10.3%); £3,771,835.96 -> £3,381,990.49 (10.3%); £3,771,836.12 -> £3,381,990.53 (10.3%); £3,771,836.27 -> £3,381,990.57 (10.3%); £3,771,836.42 -> £3,381,990.72 (10.3%); £3,771,836.58 -> £3,381,990.87 (10.3%); £3,771,836.75 -> £3,381,991.03 (10.3%); £3,771,836.93 -> £3,381,991.21 (10.3%); £3,771,837.14 -> £3,381,991.40 (10.3%); £3,771,837.36 -> £3,381,991.62 (10.3%); £3,771,837.60 -> £3,381,991.86 (10.3%); £3,771,837.85 -> £3,381,992.11 (10.3%); £3,771,838.11 -> £3,381,992.23 (10.3%); £3,771,838.37 -> £3,381,992.36 (10.3%); £3,771,838.62 -> £3,381,992.49 (10.3%); £3,771,838.88 -> £3,381,992.62 (10.3%); £3,771,839.14 -> £3,381,992.75 (10.3%); £3,771,839.39 -> £3,381,992.88 (10.3%); £3,771,839.65 -> £3,381,992.99 (10.3%); £3,771,839.90 -> £3,381,993.11 (10.3%); £3,771,840.15 -> £3,381,993.22 (10.3%); £3,771,840.41 -> £3,381,993.34 (10.3%); £3,771,840.67 -> £3,381,993.45 (10.3%); £3,771,840.92 -> £3,381,993.56 (10.3%); £3,771,841.18 -> £3,381,993.67 (10.3%); £3,771,841.44 -> £3,381,993.92 (10.3%); £3,771,841.68 -> £3,381,994.15 (10.3%); £3,771,841.94 -> £3,381,994.35 (10.3%); £3,771,842.20 -> £3,381,994.53 (10.3%); £3,771,842.46 -> £3,381,994.70 (10.3%); £3,771,842.72 -> £3,381,994.87 (10.3%); £3,771,842.97 -> £3,381,995.04 (10.3%); £3,771,843.23 -> £3,381,995.20 (10.3%); £3,771,843.48 -> £3,381,995.36 (10.3%); £3,771,843.73 -> £3,381,995.51 (10.3%); £3,771,843.99 -> £3,381,995.67 (10.3%); £3,771,844.24 -> £3,381,995.71 (10.3%); £3,771,844.49 -> £3,381,995.75 (10.3%); £3,771,844.73 -> £3,381,995.79 (10.3%); £3,771,844.95 -> £3,381,995.83 (10.3%); £3,771,845.15 -> £3,381,995.86 (10.3%); £3,771,845.31 -> £3,381,995.90 (10.3%); £3,771,845.46 -> £3,381,995.94 (10.3%); £3,771,845.61 -> £3,381,995.98 (10.3%); £3,771,845.77 -> £3,381,996.02 (10.3%); £3,771,845.92 -> £3,381,996.06 (10.3%); £3,771,846.07 -> £3,381,996.10 (10.3%); £3,771,846.22 -> £3,381,996.14 (10.3%); £3,771,846.37 -> £3,381,996.17 (10.3%); £3,771,846.52 -> £3,381,996.21 (10.3%); £3,771,846.67 -> £3,381,996.25 (10.3%); £3,771,846.83 -> £3,381,996.29 (10.3%); £3,771,846.98 -> £3,381,996.44 (10.3%); £3,771,847.14 -> £3,381,996.60 (10.3%); £3,771,847.31 -> £3,381,996.78 (10.3%); £3,771,847.50 -> £3,381,996.96 (10.3%); £3,771,847.71 -> £3,381,997.16 (10.3%); £3,771,847.93 -> £3,381,997.39 (10.3%); £3,771,848.17 -> £3,381,997.65 (10.3%); £3,771,848.43 -> £3,381,997.91 (10.3%); £3,771,848.69 -> £3,381,998.04 (10.3%); £3,771,848.96 -> £3,381,998.16 (10.3%); £3,771,849.21 -> £3,381,998.29 (10.3%); £3,771,849.47 -> £3,381,998.43 (10.3%); £3,771,849.73 -> £3,381,998.55 (10.3%); £3,771,849.99 -> £3,381,998.68 (10.3%); £3,771,850.25 -> £3,381,998.79 (10.3%); £3,771,850.50 -> £3,381,998.92 (10.3%); £3,771,850.76 -> £3,381,999.04 (10.3%); £3,771,851.01 -> £3,381,999.16 (10.3%); £3,771,851.27 -> £3,381,999.29 (10.3%); £3,771,851.53 -> £3,381,999.40 (10.3%); £3,771,851.79 -> £3,381,999.51 (10.3%); £3,771,852.04 -> £3,381,999.77 (10.3%); £3,771,852.30 -> £3,382,000.00 (10.3%); £3,771,852.56 -> £3,382,000.20 (10.3%); £3,771,852.82 -> £3,382,000.38 (10.3%); £3,771,853.07 -> £3,382,000.56 (10.3%); £3,771,853.33 -> £3,382,000.72 (10.3%); £3,771,853.59 -> £3,382,000.89 (10.3%); £3,771,853.85 -> £3,382,001.05 (10.3%); £3,771,854.11 -> £3,382,001.21 (10.3%); £3,771,854.37 -> £3,382,001.37 (10.3%); £3,771,854.62 -> £3,382,001.53 (10.3%); £3,771,854.88 -> £3,382,001.57 (10.3%); £3,771,855.14 -> £3,382,001.61 (10.3%); £3,771,855.38 -> £3,382,001.65 (10.3%); £3,771,855.60 -> £3,382,001.69 (10.3%); £3,771,855.80 -> £3,382,001.73 (10.3%); £3,771,855.94 -> £3,382,001.77 (10.3%); £3,771,856.07 -> £3,382,001.81 (10.3%); £3,771,856.21 -> £3,382,001.85 (10.3%); £3,771,856.35 -> £3,382,001.89 (10.3%); £3,771,856.48 -> £3,382,001.92 (10.3%); £3,771,856.62 -> £3,382,001.96 (10.3%); £3,771,856.76 -> £3,382,002.00 (10.3%); £3,771,856.90 -> £3,382,002.04 (10.3%); £3,771,857.03 -> £3,382,002.08 (10.3%); £3,771,857.17 -> £3,382,002.12 (10.3%); £3,771,857.30 -> £3,382,002.16 (10.3%); £3,771,857.44 -> £3,382,002.36 (10.3%); £3,771,857.57 -> £3,382,002.56 (10.3%); £3,771,857.72 -> £3,382,002.77 (10.3%); £3,771,857.88 -> £3,382,002.99 (10.3%); £3,771,858.07 -> £3,382,003.22 (10.3%); £3,771,858.27 -> £3,382,003.47 (10.3%); £3,771,858.48 -> £3,382,003.73 (10.3%); £3,771,858.70 -> £3,382,004.01 (10.3%); £3,771,858.93 -> £3,382,004.10 (10.3%); £3,771,859.16 -> £3,382,004.20 (10.3%); £3,771,859.39 -> £3,382,004.30 (10.3%); £3,771,859.61 -> £3,382,004.40 (10.3%); £3,771,859.84 -> £3,382,004.48 (10.3%); £3,771,860.07 -> £3,382,004.57 (10.3%); £3,771,860.29 -> £3,382,004.65 (10.3%); £3,771,860.53 -> £3,382,004.73 (10.3%); £3,771,860.75 -> £3,382,004.80 (10.3%); £3,771,860.97 -> £3,382,004.87 (10.3%); £3,771,861.19 -> £3,382,004.94 (10.3%); £3,771,861.42 -> £3,382,005.02 (10.3%); £3,771,861.64 -> £3,382,005.09 (10.3%); £3,771,861.87 -> £3,382,005.32 (10.3%); £3,771,862.11 -> £3,382,005.54 (10.3%); £3,771,862.33 -> £3,382,005.74 (10.3%); £3,771,862.57 -> £3,382,005.94 (10.3%); £3,771,862.80 -> £3,382,006.13 (10.3%); £3,771,863.02 -> £3,382,006.33 (10.3%); £3,771,863.25 -> £3,382,006.52 (10.3%); £3,771,863.47 -> £3,382,006.73 (10.3%); £3,771,863.70 -> £3,382,006.94 (10.3%); £3,771,863.93 -> £3,382,007.12 (10.3%); £3,771,864.15 -> £3,382,007.32 (10.3%); £3,771,864.38 -> £3,382,007.37 (10.3%); £3,771,864.60 -> £3,382,007.41 (10.3%); £3,771,864.81 -> £3,382,007.45 (10.3%); £3,771,865.00 -> £3,382,007.49 (10.3%); £3,771,865.17 -> £3,382,007.53 (10.3%); £3,771,865.32 -> £3,382,007.57 (10.3%); £3,771,865.46 -> £3,382,007.61 (10.3%); £3,771,865.60 -> £3,382,007.65 (10.3%); £3,771,865.74 -> £3,382,007.69 (10.3%); £3,771,865.88 -> £3,382,007.72 (10.3%); £3,771,866.02 -> £3,382,007.76 (10.3%); £3,771,866.16 -> £3,382,007.80 (10.3%); £3,771,866.30 -> £3,382,007.84 (10.3%); £3,771,866.45 -> £3,382,007.87 (10.3%); £3,771,866.58 -> £3,382,007.91 (10.3%); £3,771,866.73 -> £3,382,007.95 (10.3%); £3,771,866.87 -> £3,382,008.12 (10.3%); £3,771,867.02 -> £3,382,008.30 (10.3%); £3,771,867.17 -> £3,382,008.48 (10.3%); £3,771,867.34 -> £3,382,008.66 (10.3%); £3,771,867.53 -> £3,382,008.84 (10.3%); £3,771,867.73 -> £3,382,009.03 (10.3%); £3,771,867.94 -> £3,382,009.21 (10.3%); £3,771,868.17 -> £3,382,009.40 (10.3%); £3,771,868.41 -> £3,382,009.45 (10.3%); £3,771,868.65 -> £3,382,009.50 (10.3%); £3,771,868.88 -> £3,382,009.55 (10.3%); £3,771,869.11 -> £3,382,009.60 (10.3%); £3,771,869.33 -> £3,382,009.65 (10.3%); £3,771,869.57 -> £3,382,009.69 (10.3%); £3,771,869.80 -> £3,382,009.74 (10.3%); £3,771,870.03 -> £3,382,009.79 (10.3%); £3,771,870.26 -> £3,382,009.83 (10.3%); £3,771,870.49 -> £3,382,009.88 (10.3%); £3,771,870.73 -> £3,382,009.93 (10.3%); £3,771,870.96 -> £3,382,009.97 (10.3%); £3,771,871.19 -> £3,382,010.02 (10.3%); £3,771,871.43 -> £3,382,010.19 (10.3%); £3,771,871.66 -> £3,382,010.36 (10.3%); £3,771,871.89 -> £3,382,010.53 (10.3%); £3,771,872.12 -> £3,382,010.70 (10.3%); £3,771,872.36 -> £3,382,010.87 (10.3%); £3,771,872.59 -> £3,382,011.04 (10.3%); £3,771,872.82 -> £3,382,011.20 (10.3%); £3,771,873.06 -> £3,382,011.37 (10.3%); £3,771,873.30 -> £3,382,011.53 (10.3%); £3,771,873.53 -> £3,382,011.70 (10.3%); £3,771,873.77 -> £3,382,011.87 (10.3%); £3,771,874.01 -> £3,382,011.91 (10.3%); £3,771,874.24 -> £3,382,011.95 (10.3%); £3,771,874.47 -> £3,382,011.99 (10.3%); £3,771,874.67 -> £3,382,012.02 (10.3%); £3,771,874.84 -> £3,382,012.06 (10.3%); £3,771,875.00 -> £3,382,012.10 (10.3%); £3,771,875.16 -> £3,382,012.14 (10.3%); £3,771,875.32 -> £3,382,012.17 (10.3%); £3,771,875.49 -> £3,382,012.21 (10.3%); £3,771,875.65 -> £3,382,012.25 (10.3%); £3,771,875.81 -> £3,382,012.29 (10.3%); £3,771,875.97 -> £3,382,012.32 (10.3%); £3,771,876.14 -> £3,382,012.36 (10.3%); £3,771,876.30 -> £3,382,012.40 (10.3%); £3,771,876.46 -> £3,382,012.44 (10.3%); £3,771,876.62 -> £3,382,012.48 (10.3%); £3,771,876.78 -> £3,382,012.65 (10.3%); £3,771,876.94 -> £3,382,012.83 (10.3%); £3,771,877.12 -> £3,382,013.02 (10.3%); £3,771,877.32 -> £3,382,013.22 (10.3%); £3,771,877.54 -> £3,382,013.45 (10.3%); £3,771,877.77 -> £3,382,013.70 (10.3%); £3,771,878.02 -> £3,382,013.97 (10.3%); £3,771,878.30 -> £3,382,014.26 (10.3%); £3,771,878.56 -> £3,382,014.38 (10.3%); £3,771,878.85 -> £3,382,014.51 (10.3%); £3,771,879.12 -> £3,382,014.64 (10.3%); £3,771,879.39 -> £3,382,014.77 (10.3%); £3,771,879.65 -> £3,382,014.90 (10.3%); £3,771,879.93 -> £3,382,015.02 (10.3%); £3,771,880.19 -> £3,382,015.14 (10.3%); £3,771,880.46 -> £3,382,015.26 (10.3%); £3,771,880.74 -> £3,382,015.38 (10.3%); £3,771,881.01 -> £3,382,015.50 (10.3%); £3,771,881.28 -> £3,382,015.61 (10.3%); £3,771,881.56 -> £3,382,015.73 (10.3%); £3,771,881.83 -> £3,382,015.83 (10.3%); £3,771,882.10 -> £3,382,016.08 (10.3%); £3,771,882.36 -> £3,382,016.32 (10.3%); £3,771,882.63 -> £3,382,016.53 (10.3%); £3,771,882.89 -> £3,382,016.72 (10.3%); £3,771,883.15 -> £3,382,016.91 (10.3%); £3,771,883.42 -> £3,382,017.09 (10.3%); £3,771,883.68 -> £3,382,017.27 (10.3%); £3,771,883.95 -> £3,382,017.45 (10.3%); £3,771,884.22 -> £3,382,017.62 (10.3%); £3,771,884.49 -> £3,382,017.79 (10.3%); £3,771,884.75 -> £3,382,017.96 (10.3%); £3,771,885.02 -> £3,382,018.00 (10.3%); £3,771,885.29 -> £3,382,018.04 (10.3%); £3,771,885.53 -> £3,382,018.08 (10.3%); £3,771,885.75 -> £3,382,018.12 (10.3%); £3,771,885.97 -> £3,382,018.15 (10.3%); £3,771,886.13 -> £3,382,018.19 (10.3%); £3,771,886.29 -> £3,382,018.23 (10.3%); £3,771,886.46 -> £3,382,018.27 (10.3%); £3,771,886.62 -> £3,382,018.31 (10.3%); £3,771,886.79 -> £3,382,018.34 (10.3%); £3,771,886.95 -> £3,382,018.38 (10.3%); £3,771,887.11 -> £3,382,018.42 (10.3%); £3,771,887.27 -> £3,382,018.45 (10.3%); £3,771,887.43 -> £3,382,018.49 (10.3%); £3,771,887.60 -> £3,382,018.53 (10.3%); £3,771,887.76 -> £3,382,018.57 (10.3%); £3,771,887.92 -> £3,382,018.71 (10.3%); £3,771,888.08 -> £3,382,018.86 (10.3%); £3,771,888.26 -> £3,382,019.03 (10.3%); £3,771,888.46 -> £3,382,019.21 (10.3%); £3,771,888.68 -> £3,382,019.41 (10.3%); £3,771,888.91 -> £3,382,019.64 (10.3%); £3,771,889.16 -> £3,382,019.88 (10.3%); £3,771,889.43 -> £3,382,020.14 (10.3%); £3,771,889.70 -> £3,382,020.27 (10.3%); £3,771,889.99 -> £3,382,020.40 (10.3%); £3,771,890.25 -> £3,382,020.53 (10.3%); £3,771,890.51 -> £3,382,020.66 (10.3%); £3,771,890.77 -> £3,382,020.79 (10.3%); £3,771,891.04 -> £3,382,020.91 (10.3%); £3,771,891.31 -> £3,382,021.03 (10.3%); £3,771,891.58 -> £3,382,021.15 (10.3%); £3,771,891.84 -> £3,382,021.27 (10.3%); £3,771,892.10 -> £3,382,021.38 (10.3%); £3,771,892.38 -> £3,382,021.49 (10.3%); £3,771,892.65 -> £3,382,021.60 (10.3%); £3,771,892.92 -> £3,382,021.71 (10.3%); £3,771,893.20 -> £3,382,021.96 (10.3%); £3,771,893.46 -> £3,382,022.18 (10.3%); £3,771,893.73 -> £3,382,022.37 (10.3%); £3,771,894.00 -> £3,382,022.54 (10.3%); £3,771,894.27 -> £3,382,022.71 (10.3%); £3,771,894.53 -> £3,382,022.87 (10.3%); £3,771,894.80 -> £3,382,023.03 (10.3%); £3,771,895.06 -> £3,382,023.19 (10.3%); £3,771,895.32 -> £3,382,023.35 (10.3%); £3,771,895.60 -> £3,382,023.50 (10.3%); £3,771,895.87 -> £3,382,023.65 (10.3%); £3,771,896.14 -> £3,382,023.69 (10.3%); £3,771,896.41 -> £3,382,023.73 (10.3%); £3,771,896.66 -> £3,382,023.77 (10.3%); £3,771,896.89 -> £3,382,023.81 (10.3%); £3,771,897.10 -> £3,382,023.85 (10.3%); £3,771,897.27 -> £3,382,023.88 (10.3%); £3,771,897.43 -> £3,382,023.92 (10.3%); £3,771,897.58 -> £3,382,023.96 (10.3%); £3,771,897.74 -> £3,382,024.00 (10.3%); £3,771,897.90 -> £3,382,024.04 (10.3%); £3,771,898.06 -> £3,382,024.07 (10.3%); £3,771,898.22 -> £3,382,024.11 (10.3%); £3,771,898.38 -> £3,382,024.15 (10.3%); £3,771,898.53 -> £3,382,024.19 (10.3%); £3,771,898.69 -> £3,382,024.23 (10.3%); £3,771,898.85 -> £3,382,024.27 (10.3%); £3,771,899.01 -> £3,382,024.44 (10.3%); £3,771,899.17 -> £3,382,024.62 (10.3%); £3,771,899.35 -> £3,382,024.81 (10.3%); £3,771,899.55 -> £3,382,025.02 (10.3%); £3,771,899.77 -> £3,382,025.24 (10.3%); £3,771,900.00 -> £3,382,025.48 (10.3%); £3,771,900.25 -> £3,382,025.75 (10.3%); £3,771,900.52 -> £3,382,026.02 (10.3%); £3,771,900.79 -> £3,382,026.15 (10.3%); £3,771,901.05 -> £3,382,026.27 (10.3%); £3,771,901.33 -> £3,382,026.40 (10.3%); £3,771,901.59 -> £3,382,026.53 (10.3%); £3,771,901.86 -> £3,382,026.65 (10.3%); £3,771,902.13 -> £3,382,026.77 (10.3%); £3,771,902.40 -> £3,382,026.89 (10.3%); £3,771,902.68 -> £3,382,027.00 (10.3%); £3,771,902.96 -> £3,382,027.12 (10.3%); £3,771,903.22 -> £3,382,027.25 (10.3%); £3,771,903.49 -> £3,382,027.37 (10.3%); £3,771,903.76 -> £3,382,027.49 (10.3%); £3,771,904.03 -> £3,382,027.60 (10.3%); £3,771,904.30 -> £3,382,027.88 (10.3%); £3,771,904.57 -> £3,382,028.14 (10.3%); £3,771,904.84 -> £3,382,028.37 (10.3%); £3,771,905.11 -> £3,382,028.58 (10.3%); £3,771,905.38 -> £3,382,028.77 (10.3%); £3,771,905.65 -> £3,382,028.96 (10.3%); £3,771,905.92 -> £3,382,029.14 (10.3%); £3,771,906.18 -> £3,382,029.32 (10.3%); £3,771,906.45 -> £3,382,029.50 (10.3%); £3,771,906.72 -> £3,382,029.67 (10.3%); £3,771,906.99 -> £3,382,029.84 (10.3%); £3,771,907.26 -> £3,382,029.88 (10.3%); £3,771,907.54 -> £3,382,029.92 (10.3%); £3,771,907.78 -> £3,382,029.96 (10.3%); £3,771,908.01 -> £3,382,030.00 (10.3%); £3,771,908.22 -> £3,382,030.04 (10.3%); £3,771,908.38 -> £3,382,030.07 (10.3%); £3,771,908.54 -> £3,382,030.11 (10.3%); £3,771,908.70 -> £3,382,030.15 (10.3%); £3,771,908.86 -> £3,382,030.18 (10.3%); £3,771,909.02 -> £3,382,030.22 (10.3%); £3,771,909.18 -> £3,382,030.26 (10.3%); £3,771,909.34 -> £3,382,030.30 (10.3%); £3,771,909.50 -> £3,382,030.34 (10.3%); £3,771,909.66 -> £3,382,030.38 (10.3%); £3,771,909.82 -> £3,382,030.42 (10.3%); £3,771,909.99 -> £3,382,030.46 (10.3%); £3,771,910.15 -> £3,382,030.64 (10.3%); £3,771,910.31 -> £3,382,030.82 (10.3%); £3,771,910.50 -> £3,382,031.02 (10.3%); £3,771,910.70 -> £3,382,031.22 (10.3%); £3,771,910.92 -> £3,382,031.44 (10.3%); £3,771,911.15 -> £3,382,031.69 (10.3%); £3,771,911.40 -> £3,382,031.95 (10.3%); £3,771,911.67 -> £3,382,032.22 (10.3%); £3,771,911.94 -> £3,382,032.34 (10.3%); £3,771,912.21 -> £3,382,032.47 (10.3%); £3,771,912.48 -> £3,382,032.59 (10.3%); £3,771,912.75 -> £3,382,032.71 (10.3%); £3,771,913.03 -> £3,382,032.84 (10.3%); £3,771,913.30 -> £3,382,032.96 (10.3%); £3,771,913.57 -> £3,382,033.07 (10.3%); £3,771,913.84 -> £3,382,033.19 (10.3%); £3,771,914.12 -> £3,382,033.30 (10.3%); £3,771,914.39 -> £3,382,033.42 (10.3%); £3,771,914.66 -> £3,382,033.53 (10.3%); £3,771,914.93 -> £3,382,033.64 (10.3%); £3,771,915.20 -> £3,382,033.75 (10.3%); £3,771,915.49 -> £3,382,034.02 (10.3%); £3,771,915.76 -> £3,382,034.26 (10.3%); £3,771,916.03 -> £3,382,034.47 (10.3%); £3,771,916.29 -> £3,382,034.67 (10.3%); £3,771,916.56 -> £3,382,034.86 (10.3%); £3,771,916.83 -> £3,382,035.04 (10.3%); £3,771,917.12 -> £3,382,035.22 (10.3%); £3,771,917.39 -> £3,382,035.39 (10.3%); £3,771,917.67 -> £3,382,035.57 (10.3%); £3,771,917.94 -> £3,382,035.73 (10.3%); £3,771,918.20 -> £3,382,035.90 (10.3%); £3,771,918.49 -> £3,382,035.94 (10.3%); £3,771,918.76 -> £3,382,035.98 (10.3%); £3,771,919.01 -> £3,382,036.02 (10.3%); £3,771,919.25 -> £3,382,036.05 (10.3%); £3,771,919.47 -> £3,382,036.09 (10.3%); £3,771,919.62 -> £3,382,036.13 (10.3%); £3,771,919.79 -> £3,382,036.16 (10.3%); £3,771,919.95 -> £3,382,036.20 (10.3%); £3,771,920.12 -> £3,382,036.24 (10.3%); £3,771,920.27 -> £3,382,036.28 (10.3%); £3,771,920.44 -> £3,382,036.31 (10.3%); £3,771,920.60 -> £3,382,036.35 (10.3%); £3,771,920.77 -> £3,382,036.39 (10.3%); £3,771,920.93 -> £3,382,036.42 (10.3%); £3,771,921.09 -> £3,382,036.46 (10.3%); £3,771,921.25 -> £3,382,036.50 (10.3%); £3,771,921.41 -> £3,382,036.65 (10.3%); £3,771,921.57 -> £3,382,036.82 (10.3%); £3,771,921.75 -> £3,382,036.99 (10.3%); £3,771,921.95 -> £3,382,037.17 (10.3%); £3,771,922.16 -> £3,382,037.38 (10.3%); £3,771,922.40 -> £3,382,037.60 (10.3%); £3,771,922.65 -> £3,382,037.85 (10.3%); £3,771,922.91 -> £3,382,038.11 (10.3%); £3,771,923.19 -> £3,382,038.23 (10.3%); £3,771,923.45 -> £3,382,038.36 (10.3%); £3,771,923.72 -> £3,382,038.49 (10.3%); £3,771,923.99 -> £3,382,038.62 (10.3%); £3,771,924.26 -> £3,382,038.75 (10.3%); £3,771,924.53 -> £3,382,038.87 (10.3%); £3,771,924.81 -> £3,382,038.98 (10.3%); £3,771,925.09 -> £3,382,039.09 (10.3%); £3,771,925.35 -> £3,382,039.21 (10.3%); £3,771,925.62 -> £3,382,039.33 (10.3%); £3,771,925.89 -> £3,382,039.44 (10.3%); £3,771,926.16 -> £3,382,039.54 (10.3%); £3,771,926.43 -> £3,382,039.65 (10.3%); £3,771,926.69 -> £3,382,039.90 (10.3%); £3,771,926.97 -> £3,382,040.13 (10.3%); £3,771,927.24 -> £3,382,040.34 (10.3%); £3,771,927.51 -> £3,382,040.52 (10.3%); £3,771,927.78 -> £3,382,040.70 (10.3%); £3,771,928.05 -> £3,382,040.87 (10.3%); £3,771,928.33 -> £3,382,041.04 (10.3%); £3,771,928.59 -> £3,382,041.21 (10.3%); £3,771,928.86 -> £3,382,041.38 (10.3%); £3,771,929.14 -> £3,382,041.55 (10.3%); £3,771,929.41 -> £3,382,041.70 (10.3%); £3,771,929.68 -> £3,382,041.74 (10.3%); £3,771,929.95 -> £3,382,041.78 (10.3%); £3,771,930.20 -> £3,382,041.82 (10.3%); £3,771,930.44 -> £3,382,270.44 (10.3%)
- Bills issued: 153, average clarity 0.816, average bill shock 16.1%, bad debt provision £-113.51, avg complaint probability 4.6%
- Solvency signal: £343,170/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £199,425.54 vs. naked (unhedged) net margin: £604,482.82
- hedging cost £405,057.29 vs. a fully unhedged book (commodity-only: actual net £199,425.54 vs. naked net £604,482.82)
  - C1_2: actual £207.67 vs. naked £705.98 -- hedging cost £498.32
  - C2: actual £176.70 vs. naked £611.57 -- hedging cost £434.86
  - C2g: actual £221.91 vs. naked £377.19 -- hedging cost £155.28
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £275.16 vs. naked £1,386.87 -- hedging cost £1,111.71
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £18,349.13 vs. naked £119,157.58 -- hedging cost £100,808.45
  - C_IC3g: actual £3,837.46 vs. naked £56,934.03 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £102,722.50 -- hedging cost £101,286.98

**Year narrative:** 2024 produced a net gain of £347,815.39 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 41 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £120,992.97 (gross £518,611.38, capital £5,646.89)
  - Electricity: gross £464,863.13, capital £5,633.65, net £116,452.84
  - Gas: gross £53,748.25, capital £13.23, net £4,540.12
- Treasury at year end: £3,826,810.30
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.89 (avg 0.89), C2g 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2025-01-08 period 31, net margin £-81.23

**Customer Book**

- Active accounts: 11 (C1_2, C2, C2g, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 0, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £361,407.87
  - By billing account: C1 £3,675.53, C1_2 £3,572.27, C2 £4,381.71, C3 £4,035.20, C4 £2,503.98, C5 £6,507.60, C6 £13,097.23, C7 £5,846.15, C8 £6,249.07, C9 £6,617.37, C_IC1 £1,073,429.56, C_IC2 £766,140.36, C_IC3 £2,041,976.89, C_IC4 £1,121,677.29
- Bill shock events (>=20%): 26 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C2 2025-04-30 (22%); C2 2025-06-07 (78%); C2g 2025-01-31 (31%); C2g 2025-02-28 (24%); C2g 2025-04-30 (28%); C2g 2025-05-31 (31%); C2g 2025-06-07 (73%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C1_2 2025-04-30 (42%); C1_2 2025-05-31 (28%); C1_2 2025-06-07 (80%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2 38%, C8 32%, C9 26%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01/MWh, net margin £233.00
- C2 (electricity): tariff £149.29-£301.26/MWh, net margin £53.08
- C2g (gas): tariff £48.30-£52.00/MWh, net margin £90.34
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £19.93
- C8 (electricity): tariff £149.29-£304.72/MWh, net margin £103.10
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £225.43
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £63,404.31
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,994.92
- C_IC3 (electricity): tariff £88.52-£169.00/MWh, net margin £19,935.55
- C_IC3g (gas): tariff £48.21/MWh, net margin £4,449.79
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £2,483.52

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 66, average clarity 0.776, average bill shock 24.6%, bad debt provision £0.00, avg complaint probability 6.0%
- Solvency signal: £425,201/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-20.68 vs. naked (unhedged) net margin: £199.65
- hedging cost £220.33 vs. a fully unhedged book (commodity-only: actual net £-20.68 vs. naked net £199.65)
  - C2: actual £0.57 vs. naked £84.47 -- hedging cost £83.90
  - C2g: actual £8.83 vs. naked £-3.72 -- hedging added £12.55
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £120,992.97 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 26 customer(s) experienced a bill shock of >=20%.
