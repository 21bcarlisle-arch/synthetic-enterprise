# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,902,095.14
  (£1,435,458.92 net change)
- Solvency signal (final year): £425,223/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £22,610,139.59
  VAT remitted to HMRC: (£3,748,469.75) | Revenue (ex-VAT): £18,861,669.84
  Non-commodity pass-through: (£4,793,045.39)
- Gross margin: £6,470,879.87
- Capital costs: £51,377.37
- Net margin: £6,419,502.50
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1588, average clarity 0.798,
  service quality score 0.893
- Enterprise value (CLV sum across 14 billing accounts): £7,735,815.99
- Cost to serve (whole portfolio): £18,730.56, net margin after cost to serve: £6,400,771.94
- Hedge effectiveness (whole window): hedging cost £4,222,848.02 vs. a fully unhedged book (commodity-only: actual net £1,435,458.92 vs. naked net £5,658,306.93)

- **2021** (crisis year): net margin £75,467.55, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £338,356.66, 9 risk committee wake-up(s).

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

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,470,879.87, capital £51,377.37, net £6,419,502.50. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £75,467.55 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,419,502.50
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
| 2016 | £0.00 | £0.00 | £296.42 | £666.12 | £324.29 | £1,286.83 |
| 2017 | £30,139.92 | £0.00 | £-64.53 | £935.10 | £516.54 | £31,527.03 |
| 2018 | £101,124.28 | £0.00 | £-500.02 | £634.09 | £436.94 | £101,695.29 |
| 2019 | £222,457.58 | £9,999.92 | £336.68 | £804.63 | £489.73 | £234,088.53 |
| 2020 | £116,572.09 | £10,030.76 | £398.12 | £1,052.45 | £457.36 | £128,510.78 |
| 2021 | £64,952.49 | £9,999.92 | £218.33 | £466.40 | £-169.59 | £75,467.55 |
| 2022 | £330,000.66 | £9,999.92 | £1,141.20 | £-1,526.03 | £-1,259.09 | £338,356.66 |
| 2023 | £135,957.41 | £9,999.92 | £-708.90 | £46.59 | £-976.37 | £144,318.64 |
| 2024 | £333,515.99 | £10,030.76 | £772.41 | £2,781.69 | £678.12 | £347,778.98 |
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
| 2017 | 2,498,923 | 10 | 249,892 | 1922.25× | OK |
| 2018 | 2,487,783 | 11 | 226,162 | 1739.71× | OK |
| 2019 | 2,611,909 | 12 | 217,659 | 1674.30× | OK |
| 2020 | 2,924,301 | 14 | 208,879 | 1606.76× | OK |
| 2021 | 2,957,768 | 11 | 268,888 | 2068.37× | OK |
| 2022 | 3,161,940 | 11 | 287,449 | 2211.15× | OK |
| 2023 | 3,382,522 | 11 | 307,502 | 2365.40× | OK |
| 2024 | 3,775,070 | 11 | 343,188 | 2639.91× | OK |
| 2025 | 3,827,009 | 9 | 425,223 | 3270.95× | OK |

End-state (2025): **£425,223/account** across 9 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,441 | 81974.8× | OK |
| 2017 | 466 | 559 | 2,498,923 | 4470.2× | OK |
| 2018 | 868 | 1,041 | 2,487,783 | 2389.0× | OK |
| 2019 | 1,543 | 1,851 | 2,611,909 | 1411.0× | OK |
| 2020 | 1,979 | 2,374 | 2,924,301 | 1231.6× | OK |
| 2021 | 4,332 | 5,198 | 2,957,768 | 569.0× | OK |
| 2022 | 8,503 | 10,204 | 3,161,940 | 309.9× | OK |
| 2023 | 5,604 | 6,725 | 3,382,522 | 503.0× | OK |
| 2024 | 2,651 | 3,182 | 3,775,070 | 1186.5× | OK |
| 2025 | 3,872 | 4,647 | 3,827,009 | 823.6× | OK |




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
| 2016 | 38 | 135% | C5 (2016-09-30) |
| 2017 | 63 | 87% | C1g (2017-11-30) |
| 2018 | 78 | 93% | C4g (2018-10-31) |
| 2019 | 71 | 130% | C_IC1 (2019-03-31) |
| 2020 | 66 | 118% | C_IC2 (2020-03-31) |
| 2021 | 52 | 1202% | C1_2 (2021-01-31) |
| 2022 | 71 | 172% | C1_2 (2022-08-31) |
| 2023 | 60 | 120% | C1_2 (2023-08-31) |
| 2024 | 44 | 174% | C1_2 (2024-09-30) |
| 2025 | 26 | 80% | C7 (2025-06-07) |

Total: **569** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2021-01-31 | C1_2 | +1202% | no |
| 2024-09-30 | C1_2 | +174% | no |
| 2022-08-31 | C1_2 | +172% | no |
| 2024-08-31 | C1_2 | +161% | no |
| 2022-07-31 | C1_2 | +157% | no |
| 2016-09-30 | C5 | +135% | yes |
| 2016-08-31 | C5 | +133% | yes |
| 2021-10-31 | C4g | +132% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2019-08-31 | C3g | +129% | no |

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
**3yr-trailing EV:** £677,754.63 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,286.83 |
| 2017 | £31,527.03 |
| 2018 | £101,695.29 |
| 2019 | £234,088.53 |
| 2020 | £128,510.78 |
| 2021 | £75,467.55 |
| 2022 | £338,356.66 |
| 2023 | £144,318.64 | ← trailing
| 2024 | £347,778.98 | ← trailing
| 2025 | £120,992.97 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £5,452.61 | — |
| C1_2 | — | £612.56 |
| C2 | £6,620.17 | £933.32 |
| C3 | £6,491.05 | — |
| C4 | £3,807.08 | £-993.33 |
| C5 | £10,919.84 | — |
| C6 | £19,260.39 | £105.36 |
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
| 2016 | 13 | £801 | £525 | £99 | 12.4% |
| 2017 | 14 | £16,735 | £8,803 | £2,252 | 13.5% |
| 2018 | 15 | £29,032 | £17,507 | £6,780 | 23.4% |
| 2019 | 17 | £70,487 | £41,300 | £13,770 | 19.5% |
| 2020 | 19 | £64,385 | £41,672 | £6,764 | 10.5% |
| 2021 | 14 | £123,922 | £54,511 | £5,391 | 4.3% << |
| 2022 | 14 | £245,590 | £74,945 | £24,168 | 9.8% |
| 2023 | 14 | £185,335 | £68,277 | £10,308 | 5.6% |
| 2024 | 14 | £156,332 | £89,843 | £24,841 | 15.9% |
| 2025 | 11 | £88,243 | £47,146 | £10,999 | 12.5% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £24,841 net/customer
**Worst year per customer:** 2016 at £99 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £430 | — | £430 |
| C1_2 | £648 | — | £648 |
| C1g | — | £669 | £669 |
| C2 | £1,177 | — | £1,177 |
| C2g | — | £1,294 | £1,294 |
| C3 | £189 | — | £189 |
| C3g | — | £336 | £336 |
| C4 | £91 | — | £91 |
| C4g | — | £-1,711 | £-1,711 * |
| C5 | £-181 | — | £-181 * |
| C6 | £2,070 | — | £2,070 |
| C7 | £-572 | — | £-572 * |
| C8 | £2,292 | — | £2,292 |
| C9 | £2,240 | — | £2,240 |
| C_IC1 | £846,747 | — | £846,747 |
| C_IC2 | £434,894 | — | £434,894 |
| C_IC3 | £136,677 | — | £136,677 |
| C_IC3g | — | £64,511 | £64,511 |
| C_IC4 | £32,221 | — | £32,221 |
| **Total** | **£1,458,924** | **£65,099** | **£1,524,023** |

Loss-making accounts: C4g (£-1,711), C7 (£-572), C5 (£-181)
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
| 2016 | 0.794 R | 5.8% | 0.29% | 38 | 108 | RED ! |
| 2017 | 0.804 A | 5.1% | 0.19% | 63 | 168 | AMBER |
| 2018 | 0.774 R | 5.8% | 0.23% | 78 | 180 | RED ! |
| 2019 | 0.809 A | 5.2% | 0.20% | 71 | 204 | AMBER |
| 2020 | 0.812 A | 4.9% | 0.18% | 66 | 205 | AMBER |
| 2021 | 0.809 A | 5.1% | 0.26% | 52 | 168 | AMBER |
| 2022 | 0.785 R | 5.8% | 0.24% | 71 | 168 | RED ! |
| 2023 | 0.786 R | 5.7% | 0.23% | 60 | 168 | RED ! |
| 2024 | 0.804 A | 5.0% | 0.19% | 44 | 153 | AMBER |
| 2025 | 0.785 R | 5.7% | 0.23% | 26 | 66 | RED ! |

Worst clarity year: **2018** (0.774)
Highest complaint probability: **2016** (5.8%)
Worst bill shock: **2016** (0.29%)
RED years: 2016, 2018, 2022, 2023, 2025
AMBER years: 2017, 2019, 2020, 2021, 2024
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,441 | £1,287 |
| 2017 | 2.69 | WATCH | £2,498,923 | £31,527 |
| 2018 | — | — | £2,487,783 | £101,695 |
| 2019 | — | — | £2,611,909 | £234,089 |
| 2020 | — | — | £2,924,301 | £128,511 |
| 2021 | — | — | £2,957,768 | £75,468 |
| 2022 | 2.70 | WATCH | £3,161,940 | £338,357 |
| 2023 | 2.72 | WATCH | £3,382,522 | £144,319 |
| 2024 | — | — | £3,775,070 | £347,779 |
| 2025 | — | — | £3,827,009 | £120,993 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,827,009)**
**Treasury growth: £2,467,441 → £3,827,009 (+£1,359,568)**

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
| Status Quo (hold gas) | £203,665 | — |
| Exit Gas (with churn risk) | £83,517 | -£120,148 |
| Reprice to Breakeven | £205,376 | +£1,711 |

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
| 2016 | 2016-12-31 | 48 | C1 | -£54 |
| 2017 | 2017-12-31 | 48 | C5 | -£328 |
| 2018 | 2018-12-31 | 48 | C5 | -£286 |
| 2019 | 2019-12-31 | 48 | C3 | -£88 |
| 2020 | 2020-03-16 | 20 | C_IC1 | -£19 |
| 2021 | 2021-12-31 | 48 | C6 | -£307 |
| 2022 | 2022-01-24 | 26 | C_IC1 | -£89 |
| 2023 | 2023-12-31 | 48 | C6 | -£2,089 |
| 2024 | 2024-09-28 | 48 | C4 | -£113 |
| 2025 | 2025-01-08 | 31 | C_IC1 | -£81 |

**Single worst period: 2023 2023-12-31 SP48 (C6, -£2,089)** — exposure from gas supply anchor at year-end pricing.

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
| 2016 | 14 | £173,370 | £92,774 | £8,974 | £12,384 |
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
| 2016 | +£7 | £1,162 | £67 | — | 108 |
| 2017 | +£2,707 | £37,159 | £416 | — | 168 |
| 2018 | +£9,875 | £65,510 | £354 | — | 180 |
| 2019 | +£28,353 | £164,625 | £47 | — | 204 |
| 2020 | +£35,391 | £238,634 | £-18 | — | 205 |
| 2021 | +£14,982 | £246,246 | £374 | — | 168 |
| 2022 | -£49,726 CREDIT | £256,149 | £63 | 2 | 168 |
| 2023 | +£64,738 | £271,739 | £2,251 | 47 | 168 |
| 2024 | +£109,869 | £307,451 | £-77 | 4271 | 153 |
| 2025 | +£46,911 | £135,614 | £0 | — | 66 |

**CfD turned CREDIT in 2022: -£49,726 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2023 (£2,251)**

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
| 2017 | £2,498,923 | AMBER | RED | GREEN | AMBER | RED |
| 2018 | £2,487,783 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,611,909 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,924,301 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,957,768 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,161,940 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,382,522 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,775,070 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,827,009 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 41.8% | £1,241 | £629 | 1.63% |
| 2017 | 14 | 32.5% | £24,715 | £8,752 | 2.03% |
| 2018 | 15 | 41.0% | £40,016 | £17,552 | 2.23% |
| 2019 | 17 | 40.1% | £96,196 | £40,938 | 2.13% |
| 2020 | 19 | 39.9% | £97,253 | £41,410 | 2.35% |
| 2021 | 14 | 29.0% | £172,595 | £54,535 | 2.22% |
| 2022 | 14 | 22.1% | £302,830 | £75,008 | 2.27% |
| 2023 | 14 | 24.6% | £247,839 | £68,197 | 2.51% |
| 2024 | 14 | 39.1% | £214,729 | £90,196 | 2.44% |
| 2025 | 11 | 39.8% | £116,753 | £51,069 | 3.36% |

**Best EBIT%: 2016 (41.8%)** | **Worst EBIT%: 2022 (22.1%)**
**Peak revenue/customer: 2022 (£302,830)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Population Anchoring -- Complaints & Arrears (Phase PS)

SIM aggregate complaint and arrears rates vs published UK benchmarks.
Complaints: Ofgem QoS survey, I&C adjusted (GREEN 2-6%, crisis 2-8%).
Arrears: DESNZ business energy debt (GREEN <8%, crisis <12%).

| Year | Complaint rate% | C.Bench hi | C.RAG | Arrears rate% | A.Bench hi | A.RAG |
|------|-----------------|-----------|-------|---------------|-----------|-------|
| 2016 | 5.84% | 6% | OK | 15.4% | 8% | ! |
| 2017 | 5.11% | 6% | OK | 21.4% | 8% | ! |
| 2018 | 5.81% | 6% | OK | 26.7% | 8% | ! |
| 2019 | 5.16% | 6% | OK | 29.4% | 8% | ! |
| 2020 | 4.91% | 6% | OK | 5.3% | 8% | OK |
| 2021 | 5.07% | 8% | OK | 21.4% | 12% | ! |
| 2022 | 5.81% | 8% | OK | 50.0% | 12% | ! |
| 2023 | 5.68% | 8% | OK | 21.4% | 12% | ! |
| 2024 | 5.04% | 6% | OK | 35.7% | 8% | ! |
| 2025 | 5.72% | 6% | OK | 27.3% | 8% | ! |

**Complaints:** 10 of 10 years GREEN (I&C baseline 2-6% normal, 2-8% crisis).
**Arrears:** 1 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).

## Plausibility vs Industry

Key metrics vs UK retail energy norms (Ofgem/Cornwall Insight). OK = within range | ~ = amber | ! = outside expected range.

| Year | Net margin% | Gross margin% | Bad debt% | Churn% |
|------|-------------|---------------|-----------|--------|
| 2016 | !41.8% | !50.7% | OK1.63% | ~0% |
| 2017 | !32.5% | !35.4% | OK2.03% | ~0% |
| 2018 | !41.0% | !43.9% | OK2.23% | ~0% |
| 2019 | !40.1% | !42.6% | OK2.13% | ~0% |
| 2020 | !39.9% | !42.6% | OK2.35% | OK16% |
| 2021 | !29.0% | !31.6% | OK2.22% | ~0% |
| 2022 | !22.1% | ~24.8% | OK2.27% | ~0% |
| 2023 | !24.6% | ~27.5% | OK2.51% | ~0% |
| 2024 | !39.1% | !42.0% | OK2.44% | OK14% |
| 2025 | !39.8% | !43.7% | OK3.36% | ~0% |

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

**Total bad debt (all years):** £3,476
**Crisis stress incremental:** £5,215

**RAG [OK]:** GREEN — Incremental credit stress below 0.5% revenue — not material

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (11 active customers) under 12-month forward scenarios.
Generated: 2026-07-12T00:10:40Z

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
| 2016 | £16,131.40 | £3,594.97 | £4,363.77 | £8,172.66 | 50.7% | — | — | — | — |
| 2017 | £346,003.86 | £111,055.46 | £112,416.49 | £122,531.90 | 35.4% | +£329,872.46 | +£107,460.50 | +£108,052.72 | +£114,359.24 |
| 2018 | £600,234.49 | £172,888.20 | £164,071.67 | £263,274.62 | 43.9% | +£254,230.63 | +£61,832.74 | +£51,655.17 | +£140,742.72 |
| 2019 | £1,635,331.12 | £496,185.23 | £443,205.99 | £695,939.90 | 42.6% | +£1,035,096.63 | +£323,297.03 | +£279,134.32 | +£432,665.27 |
| 2020 | £1,847,806.25 | £431,600.88 | £629,416.29 | £786,789.09 | 42.6% | +£212,475.14 | £-64,584.35 | +£186,210.30 | +£90,849.19 |
| 2021 | £2,416,323.84 | £971,905.80 | £680,933.21 | £763,484.82 | 31.6% | +£568,517.58 | +£540,304.92 | +£51,516.93 | £-23,304.27 |
| 2022 | £4,239,614.45 | £2,389,086.10 | £800,420.93 | £1,050,107.41 | 24.8% | +£1,823,290.61 | +£1,417,180.30 | +£119,487.72 | +£286,622.59 |
| 2023 | £3,469,744.20 | £1,639,053.05 | £875,932.70 | £954,758.46 | 27.5% | £-769,870.24 | £-750,033.06 | +£75,511.77 | £-95,348.96 |
| 2024 | £3,006,202.48 | £931,630.07 | £811,823.30 | £1,262,749.11 | 42.0% | £-463,541.72 | £-707,422.97 | £-64,109.40 | +£307,990.65 |
| 2025 | £1,284,277.76 | £452,060.81 | £270,461.05 | £561,755.90 | 43.7% | £-1,721,924.72 | £-479,569.26 | £-541,362.25 | £-700,993.21 |

**Best GM year: 2016 (50.7%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Net Margin Bridge (Year-on-Year Attribution)

Decomposes each year's net margin change into: gross margin movement, bad debt, capital costs, policy levies, network costs.

| Transition | Net Δ | Gross Δ | Bad Debt Δ | Capital Δ | Policy Δ | Network Δ | Portfolio | Driver | RAG |
|-----------|-------|---------|-----------|---------|---------|---------|---------|--------|-----|
| 2016→2017 | +£30,240 | +£116,417 | -£350 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£70,168 | +£139,364 | +£62 | -£367 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£132,393 | +£439,498 | +£307 | -£686 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£105,578 | +£89,669 | +£65 | +£360 | -£162,654 | -£33,019 | +2 | policy levies | RED |
| 2020→2021 | -£53,043 | -£28,614 | -£392 | -£3,636 | -£19,033 | -£1,367 | -5 | gross margin | RED |
| 2021→2022 | +£262,889 | +£286,070 | +£311 | -£7,674 | -£1,057 | -£14,761 | +0 | gross margin | GREEN |
| 2022→2023 | -£194,038 | -£93,343 | -£2,188 | +£3,240 | -£70,553 | -£31,194 | +0 | gross margin | RED |
| 2023→2024 | +£203,460 | +£301,924 | +£2,328 | +£514 | -£100,652 | -£654 | +0 | gross margin | GREEN |
| 2024→2025 | -£226,786 | -£739,194 | -£77 | +£3,875 | +£381,910 | +£126,700 | -3 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£226,786)** | **Best transition: 2021→2022 (+£262,889)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Payment Portfolio Health (P2: Billing Infra)

Year-by-year bad debt rate and high-churn-risk customer concentration.

| Year | Bad Debt | Bad Debt Rate | At-Risk Customers | At-Risk % | Trend | RAG |
|------|----------|--------------|-----------------|----------|-------|-----|
| 2016 | £67 | 0.64% | 0/4 | 0% | — STABLE | GREEN |
| 2017 | £416 | 0.18% | 0/10 | 0% | ↓ IMPROVING | GREEN |
| 2018 | £354 | 0.08% | 1/11 | 9% | ↓ IMPROVING | GREEN |
| 2019 | £47 | 0.00% | 3/12 | 25% | ↓ IMPROVING | GREEN |
| 2020 | £-18 | -0.00% | 5/14 | 36% | ↓ IMPROVING | AMBER |
| 2021 | £374 | 0.02% | 4/11 | 36% | ↑ DETERIORATING | AMBER |
| 2022 | £63 | 0.00% | 9/11 | 82% | ↓ IMPROVING | RED |
| 2023 | £2,251 | 0.09% | 10/11 | 91% | ↑ DETERIORATING | RED |
| 2024 | £-77 | -0.00% | 4/11 | 36% | ↓ IMPROVING | AMBER |
| 2025 | £0 | 0.00% | 2/3 | 67% | ↑ DETERIORATING | RED |

**Worst bad debt year: 2016 (0.64%)** | **Peak at-risk concentration: 2023 (91% of customers)**

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
| 2016 | £2,473,383.65 | £1,344.28 | 1839.9x | ✓ GREEN | Yes |
| 2017 | £2,585,875.84 | £28,833.65 | 89.7x | ✓ GREEN | Yes |
| 2018 | £2,831,913.62 | £50,019.54 | 56.6x | ✓ GREEN | Yes |
| 2019 | £3,487,888.13 | £136,277.59 | 25.6x | ✓ GREEN | Yes |
| 2020 | £4,225,626.53 | £153,983.85 | 27.4x | ✓ GREEN | Yes |
| 2021 | £4,926,748.54 | £201,360.32 | 24.5x | ✓ GREEN | Yes |
| 2022 | £5,864,358.74 | £353,301.20 | 16.6x | ✓ GREEN | Yes |
| 2023 | £6,718,989.60 | £289,145.35 | 23.2x | ✓ GREEN | Yes |
| 2024 | £7,895,509.35 | £250,516.87 | 31.5x | ✓ GREEN | Yes |
| 2025 | £8,407,231.20 | £107,023.15 | 78.6x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.6x (equity £5,864,358.74 vs monthly revenue £353,301.20). RAG: GREEN.
**Strongest year:** 2016 — 1839.9x.

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
| 2016 | £16,131.40 | £5,995.50 | £50.96 | ✓ GREEN |  |
| 2017 | £346,003.86 | £128,598.10 | £1,093.08 | ✓ GREEN |  |
| 2018 | £600,234.49 | £223,087.15 | £1,896.24 | ✓ GREEN |  |
| 2019 | £1,635,331.12 | £607,798.07 | £5,166.28 | ✓ GREEN |  |
| 2020 | £1,847,806.25 | £686,767.99 | £5,837.53 | ✓ GREEN |  |
| 2021 | £2,416,323.84 | £898,067.03 | £7,633.57 | ✓ GREEN | CREDIT EXPECTED |
| 2022 | £4,239,614.45 | £1,575,723.37 | £13,393.65 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,469,744.20 | £1,289,588.26 | £10,961.50 | ✓ GREEN |  |
| 2024 | £3,006,202.48 | £1,117,305.26 | £9,497.09 | ✓ GREEN |  |
| 2025 | £1,284,277.76 | £477,323.23 | £4,057.25 | ✓ GREEN |  |

**Peak reconciliation exposure:** 2022 — max adverse £13,394 (4.5 months weighted tail).

_Note: Outstanding pool ≈ current-year revenue × (weighted outstanding months ÷ 12)._
_Max adverse = pool × blended variance rate (0.5% HH + 4% non-HH, portfolio-weighted)._
## Ofgem Supply Licence Health (Phase OC)

Annual licence health checks: customer base, net assets, liquidity, bad debt.
Breach triggers board escalation and Ofgem notification under SLC 0.
WATCH = within 20% of threshold. BREACH = threshold crossed.

| Year | Customers | Net Assets | Treasury | Cash Wks | Bad Debt % | Overall |
|------|-----------|------------|----------|----------|------------|---------|
| 2016 | 13 | £2,473,383.65 | £2,467,441.30 | 35691w | 0.64% | ✗ BREACH |
| 2017 | 14 | £2,585,875.84 | £2,498,923.22 | 1170w | 0.18% | ✗ BREACH |
| 2018 | 15 | £2,831,913.62 | £2,487,782.60 | 748w | 0.08% | ✗ BREACH |
| 2019 | 17 | £3,487,888.13 | £2,611,908.89 | 274w | 0.00% | ✗ BREACH |
| 2020 | 19 | £4,225,626.53 | £2,924,300.68 | 352w | -0.00% | ✗ BREACH |
| 2021 | 14 | £4,926,748.54 | £2,957,767.54 | 158w | 0.02% | ✗ BREACH |
| 2022 | 14 | £5,864,358.74 | £3,161,940.47 | 69w | 0.00% | ✗ BREACH |
| 2023 | 14 | £6,718,989.60 | £3,382,522.01 | 107w | 0.09% | ✗ BREACH |
| 2024 | 14 | £7,895,509.35 | £3,775,069.66 | 211w | -0.00% | ✗ BREACH |
| 2025 | 11 | £8,407,231.20 | £3,827,008.96 | 440w | 0.00% | ✗ BREACH |

**BREACH years:** 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 — board escalation required.

_Note: Complaints from contact model avg_complaint_probability. Customer count <50 triggers Ofgem viability review — small-portfolio years will show WATCH._
## Ofgem SLC Compliance Scorecard (Phase OD)

10 compliance domains per year, derived from simulation outputs.
G = GREEN (compliant), A = AMBER (watch), R = RED (breach).

| Domain | SLC Ref | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|--------|---------|------|------|------|------|------|------|------|------|------|------|
| Governance | SLC 0-9 | G | G | G | G | G | G | G | G | G | G |
| Billing/Metering | SLC 10-14 | A | G | A | G | G | G | A | A | G | A |
| Payment/Debt | SLC 15-19 | G | G | G | G | G | G | G | G | G | G |
| Information | SLC 20-24 | G | G | G | G | G | G | G | G | G | G |
| Complaints | SLC 25-29 / Ofgem Time to Fix rules | G | G | G | G | G | G | G | G | G | G |
| Vulnerable Cust | SLC 30-35 / PSR | G | G | G | G | G | G | G | G | G | G |
| Tariff/Cap | SLC 36-40 / Default Tariff Cap | G | G | G | G | G | G | G | G | G | G |
| Environmental | SLC 41-50 / RO, CfD, EE obligation | G | G | G | G | G | G | G | G | G | G |
| Network/BSC | SLC 51-60 / BSC obligations | G | G | G | G | G | G | G | G | G | G |
| Financial Res. | SLC 4C / SFR Decision 2023 | G | G | G | G | G | G | G | G | G | G |
| **Overall** |  | A | G | A | G | G | G | A | A | G | A |

**Watch years (AMBER):** 2016, 2018, 2022, 2023, 2025

_Note: Vulnerable customers, tariff/cap, and environmental domains defaulted to GREEN_
_(these are modelled as compliant; detailed SLC breach simulation not yet implemented)._
## Ofgem Annual Supply Return (Phase OE)

UK suppliers must file annual supply returns to Ofgem. Filed by 31 March of the following year.

| Year | Submitted | Customers (R/SME/I&C) | Elec GWh | Gas GWh | Bad Debt/Cust |
|------|-----------|----------------------|----------|---------|---------------|
| 2016 | Yes | 13/13/13 | 0.1 | 0.0 | £5 |
| 2017 | Yes | 14/14/14 | 1.5 | 0.1 | £30 |
| 2018 | Yes | 15/15/15 | 2.9 | 0.1 | £24 |
| 2019 | Yes | 17/17/17 | 7.1 | 2.8 | £3 |
| 2020 | Yes | 19/19/19 | 7.3 | 2.4 | £-1 |
| 2021 | Yes | 14/14/14 | 9.6 | 6.0 | £27 |
| 2022 | Yes | 14/14/14 | 19.0 | 11.8 | £4 |
| 2023 | Yes | 14/14/14 | 15.3 | 6.0 | £161 |
| 2024 | Yes | 14/14/14 | 12.8 | 5.4 | £-6 |
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
| 2020 | ECO3 | GBP4.50 | 14 | OK (exempt) | GBP55 |
| 2021 | ECO3 | GBP4.50 | 9 | OK (exempt) | GBP72 |
| 2022 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP192 |
| 2023 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP157 |
| 2024 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP136 |
| 2025 | ECO4 | GBP6.80 | 6 | OK (exempt) | GBP58 |

Counterfactual total 2016-2025 (if 150k domestic): **GBP744**

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
| 2025 | 9 | 175g/kWh | 1.5 | 1 | 0.2 | 1.7 | 68% (decarbonising) |
| **Total** | | | | | | **30.7 t** | |

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
| 2016 | 0.794 | 0.058 | 0 | 0 | **LOW CLARITY** |
| 2017 | 0.804 | 0.051 | 0 | 0 |  |
| 2018 | 0.774 | 0.058 | 0 | 0 | **LOW CLARITY** |
| 2019 | 0.809 | 0.052 | 0 | 0 |  |
| 2020 | 0.812 | 0.049 | 2 | 0 |  |
| 2021 | 0.809 | 0.051 | 0 | 0 |  |
| 2022 | 0.785 | 0.058 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.786 | 0.057 | 0 | 0 | **LOW CLARITY** |
| 2024 | 0.804 | 0.050 | 2 | 0 |  |
| 2025 | 0.785 | 0.057 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 89.3% | **Average billing clarity:** 0.798 | **Average complaint probability:** 0.054

**Acquisition performance:** 4 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2018** (0.774) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

## Bill Shock Analysis

Bill shock events occur when a customer's bill increases >20% vs the prior bill.
Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.

| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |
|------|------------|--------|-------|------------|------|
| 2016 | 29.1% | 38 | 108 | 35% | ELEVATED |
| 2017 | 19.3% | 63 | 168 | 38% |  |
| 2018 | 23.0% | 78 | 180 | 43% | ELEVATED |
| 2019 | 20.3% | 71 | 204 | 35% | ELEVATED |
| 2020 | 18.3% | 66 | 205 | 32% |  |
| 2021 | 25.8% | 52 | 168 | 31% | ELEVATED |
| 2022 | 24.5% | 71 | 168 | 42% | ELEVATED |
| 2023 | 22.7% | 60 | 168 | 36% | ELEVATED |
| 2024 | 19.5% | 44 | 153 | 29% |  |
| 2025 | 22.9% | 26 | 66 | 39% | ELEVATED |

**Crisis peak: 2016** — 29.1% average shock. Energy crisis drove wholesale costs above locked tariff rates,
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
| 2016 | £962.54 | £324.29 | £9,028.87 | £1,388.28 | 13.3% | YES |
| 2017 | £31,010.49 | £516.54 | £231,633.78 | £2,660.42 | 1.1% | YES |
| 2018 | £101,258.35 | £436.94 | £432,365.68 | £3,113.94 | 0.7% | YES |
| 2019 | £223,598.89 | £10,489.65 | £1,060,516.66 | £137,766.14 | 11.5% | YES |
| 2020 | £118,022.66 | £10,488.12 | £1,102,193.08 | £121,119.88 | 9.9% | YES |
| 2021 | £65,637.22 | £9,830.33 | £1,437,504.91 | £297,399.17 | 17.1% | YES |
| 2022 | £329,615.83 | £8,740.82 | £2,848,806.28 | £589,446.82 | 17.1% | YES |
| 2023 | £135,295.09 | £9,023.55 | £2,296,002.86 | £298,691.57 | 11.5% | YES |
| 2024 | £337,070.09 | £10,708.88 | £1,917,076.86 | £271,569.81 | 12.4% | YES |
| 2025 | £116,452.84 | £4,540.12 | £837,702.08 | £132,970.11 | 13.7% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £203,664.61 | — | Current strategy |
| EXIT_GAS | £83,516.85 | £-120,147.76 | Remove gas; model elec churn risk |
| REPRICE_GAS | £205,375.93 | £1,711.32 | Raise gas tariff to break-even |

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
| SME electricity | £30,536.93 | £326.30 | £1,889.71 | 5.8x | Moderate |
| resi electricity | £55,053.10 | £614.51 | £6,495.58 | 10.6x | Moderate |
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
| C1+C1g | £430.09 | £669.14 | £1,099.23 | Yes |
| C3+C3g | £189.47 | £336.46 | £525.94 | Yes |
| C4+C4g | £91.42 | £-1,711.32 | £-1,619.90 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £65,099.25.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,524,023.26 across 19 billing accounts. Revenue: £14,028,957.18.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,123,873.83 | £1,875,002.30 | £18,435.60 | £846,747.11 | 27.1% |
| 2 | C_IC2 | fixed | £1,524,534.49 | £909,010.15 | £8,630.44 | £434,893.78 | 28.5% |
| 3 | C_IC3 | pass_through | £4,629,960.35 | £1,825,093.54 | £23,102.67 | £136,677.18 | 3.0% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £64,510.98 | 3.5% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £32,220.65 | 1.2% |
| 6 | C8 | fixed | £21,649.27 | £12,429.82 | £134.60 | £2,291.54 | 10.6% |
| 7 | C9 | fixed | £20,244.05 | £12,708.53 | £131.44 | £2,240.28 | 11.1% |
| 8 | C6 | fixed | £39,190.43 | £22,706.35 | £266.16 | £2,070.34 | 5.3% |
| 9 | C2g | fixed | £8,090.72 | £3,287.48 | £106.78 | £1,293.99 | 16.0% |
| 10 | C2 | fixed | £9,515.76 | £5,522.81 | £58.28 | £1,177.20 | 12.4% |
| 11 | C1g | fixed | £2,436.42 | £1,355.24 | £15.79 | £669.14 | 27.5% |
| 12 | C1_2 | fixed | £11,629.63 | £5,662.84 | £81.65 | £648.00 | 5.6% |
| 13 | C1 | fixed | £3,545.67 | £2,343.04 | £14.71 | £430.09 | 12.1% |
| 14 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £336.46 | 12.5% |
| 15 | C3 | fixed | £3,628.76 | £2,388.88 | £14.77 | £189.47 | 5.2% |
| 16 | C4 | fixed | £6,193.87 | £3,243.30 | £37.88 | £91.42 | 1.5% |
| 17 | C5 | fixed | £12,497.06 | £7,830.58 | £60.14 | £-180.63 | -1.4% |
| 18 | C7 | fixed | £21,729.00 | £10,753.88 | £141.17 | £-572.42 | -2.6% |
| 19 | C4g | fixed | £10,335.76 | £1,243.04 | £130.00 | £-1,711.32 | -16.6% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,028,957 | 100.0% |
| Wholesale cost | -£7,597,745 | 54.2% |
| **Gross supply margin** | **£6,431,213** | **45.8%** |
| Policy + Network costs | -£4,855,812 | 34.6% |
| Capital cost | -£51,377 | 0.4% |
| **Net supply margin** | **£1,524,023** | **10.9%** |

> *The ledger's `net_margin_gbp` (£6,419,502) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,023,008 | 47.5% | 12.1% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 3.5% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £51,687 | 59.1% | 3.7% | CMA 3-8% | ✓ |
| resi/elec | £86,506 | 57.1% | 6.8% | Ofgem CMA 2-5% | ✓ |
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
| Customer bills (all-in) | £22,610,139.59 |
|   Less: VAT remitted to HMRC | (£3,748,469.75) |
| = Revenue (ex-VAT) | £18,861,669.84 |
| Less: non-commodity pass-through | (£4,793,045.39) |
| Wholesale cost (settlement events) | (£7,597,744.58) |
| Gross margin | £6,470,879.87 |
| Capital charges | (£51,377.37) |
| Net margin | £6,419,502.50 |

_Cash reconciliation: of £22,610,139.59 billed, bad debt of £452,298.47 was written off, leaving £22,157,841.12 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £9,715,673.77._

| Acquisition spend | (£862.50) |
| Fixed overhead | (£5,700.00) |
| Cost to serve | (£18,730.56) |
| Operating net margin | £6,394,209.44 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £16,131.40 | £3,594.97 | £4,363.77 | £8,172.66 | £262.82 | £1,338.89 | £6,747.43 (41.8%) |
| 2017 | £346,003.86 | £111,055.46 | £112,416.49 | £122,531.90 | £7,036.68 | £8,766.14 | £112,492.18 (32.5%) |
| 2018 | £600,234.49 | £172,888.20 | £164,071.67 | £263,274.62 | £13,367.24 | £15,596.36 | £246,037.78 (41.0%) |
| 2019 | £1,635,331.12 | £496,185.23 | £443,205.99 | £695,939.90 | £34,899.85 | £37,639.00 | £655,974.51 (40.1%) |
| 2020 | £1,847,806.25 | £431,600.88 | £629,416.29 | £786,789.09 | £43,416.65 | £47,084.47 | £737,738.41 (39.9%) |
| 2021 | £2,416,323.84 | £971,905.80 | £680,933.21 | £763,484.82 | £53,697.91 | £56,760.20 | £701,122.00 (29.0%) |
| 2022 | £4,239,614.45 | £2,389,086.10 | £800,420.93 | £1,050,107.41 | £96,159.03 | £99,220.90 | £937,610.20 (22.1%) |
| 2023 | £3,469,744.20 | £1,639,053.05 | £875,932.70 | £954,758.46 | £87,029.51 | £90,091.10 | £854,630.86 (24.6%) |
| 2024 | £3,006,202.48 | £931,630.07 | £811,823.30 | £1,262,749.11 | £73,331.16 | £76,707.33 | £1,176,519.75 (39.1%) |
| 2025 | £1,284,277.76 | £452,060.81 | £270,461.05 | £561,755.90 | £43,097.63 | £44,387.17 | £511,721.85 (39.8%) |
| **Total** | **£18,861,669.84** | | | | | | **£5,940,594.98 (31.5%)** |

**Best year:** 2024 — net £1,176,519.75 (39.1% margin)
**Worst year:** 2016 — net £6,747.43 (41.8% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,407,231.20 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,407,231.20** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,940,594.98 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £16,131.40 | +9.9% | £6,592.99 | £6,747.43 | +2.3% | GREEN |
| 2017 | £16,138.86 | £346,003.86 | +2043.9% | £7,252.29 | £112,492.18 | +1451.1% | RED |
| 2018 | £386,623.75 | £600,234.49 | +55.3% | £128,424.00 | £246,037.78 | +91.6% | RED |
| 2019 | £675,851.95 | £1,635,331.12 | +142.0% | £281,335.50 | £655,974.51 | +133.2% | RED |
| 2020 | £1,816,630.04 | £1,847,806.25 | +1.7% | £736,963.94 | £737,738.41 | +0.1% | GREEN |
| 2021 | £2,028,952.42 | £2,416,323.84 | +19.1% | £833,649.22 | £701,122.00 | -15.9% | RED |
| 2022 | £2,607,611.88 | £4,239,614.45 | +62.6% | £790,935.58 | £937,610.20 | +18.5% | RED |
| 2023 | £4,508,414.67 | £3,469,744.20 | -23.0% | £1,029,561.00 | £854,630.86 | -17.0% | RED |
| 2024 | £3,512,844.39 | £3,006,202.48 | -14.4% | £893,105.75 | £1,176,519.75 | +31.7% | RED |
| 2025 | £3,145,356.42 | £1,284,277.76 | -59.2% | £1,315,150.33 | £511,721.85 | -61.1% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,412,940.00

## 2016

**Trading & Risk**

- Net margin: £1,286.83 (gross £6,822.19, capital £86.34)
  - Electricity: gross £6,011.45, capital £78.97, net £962.54
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
- Worst single period: C1 on 2016-12-31 period 48, net margin £-53.59

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £10,462.85
  - By billing account: C1 £6,522.54, C5 £14,339.54, C7 £10,526.48
- Bill shock events (>=20%): 38 -- C1 2016-04-30 (21%); C1g 2016-05-31 (42%); C1g 2016-06-30 (35%); C1g 2016-10-31 (107%); C1g 2016-11-30 (55%); C5 2016-05-31 (25%); C5 2016-06-30 (75%); C5 2016-07-31 (122%); C5 2016-08-31 (133%); C5 2016-09-30 (135%); C5 2016-10-31 (125%); C5 2016-11-30 (56%); C7 2016-04-30 (22%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-11-30 (54%); C2g 2016-05-31 (39%); C2g 2016-06-30 (39%); C2g 2016-10-31 (102%); C2g 2016-11-30 (60%); C6 2016-06-30 (37%); C6 2016-07-31 (80%); C6 2016-08-31 (87%); C6 2016-09-30 (97%); C6 2016-10-31 (80%); C6 2016-11-30 (26%); C8 2016-05-31 (41%); C8 2016-06-30 (43%); C8 2016-09-30 (25%); C8 2016-10-31 (111%); C8 2016-11-30 (72%); C3g 2016-10-31 (84%); C3g 2016-11-30 (53%); C9 2016-09-30 (20%); C9 2016-10-31 (80%); C9 2016-11-30 (61%); C4 2016-11-30 (36%); C4g 2016-11-30 (50%)
- Churn risk (accounts renewing in 2016): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £92.16-£175.95/MWh, net margin £91.66
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
- Bills issued: 108, average clarity 0.794, average bill shock 29.1%, bad debt provision £66.56, avg complaint probability 5.8%
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

**Year narrative:** 2016 produced a net gain of £1,286.83 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 38 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £31,527.03 (gross £123,238.74, capital £1,273.58)
  - Electricity: gross £121,809.17, capital £1,258.73, net £31,010.49
  - Gas: gross £1,429.57, capital £14.85, net £516.54
- Treasury at year end: £2,498,923.22
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
- Worst single period: C5 on 2017-12-31 period 48, net margin £-327.72

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £11,762.47
  - By billing account: C1 £5,740.27, C2 £11,364.56, C3 £9,644.02, C4 £8,744.86, C5 £12,167.53, C6 £24,200.80, C7 £8,895.16, C8 £13,842.89, C9 £11,262.19
- Bill shock events (>=20%): 63 -- C1 2017-04-30 (21%); C1g 2017-02-28 (30%); C1g 2017-05-31 (34%); C1g 2017-06-30 (36%); C1g 2017-10-31 (23%); C1g 2017-11-30 (87%); C1g 2017-12-31 (21%); C5 2017-02-28 (23%); C5 2017-05-31 (21%); C5 2017-06-30 (27%); C5 2017-07-31 (64%); C5 2017-08-31 (69%); C5 2017-09-30 (65%); C5 2017-10-31 (43%); C5 2017-11-30 (25%); C5 2017-12-31 (21%); C7 2017-01-31 (34%); C7 2017-02-28 (28%); C7 2017-05-31 (31%); C7 2017-06-30 (33%); C7 2017-09-30 (28%); C7 2017-10-31 (22%); C7 2017-11-30 (78%); C2g 2017-04-30 (29%); C2g 2017-05-31 (38%); C2g 2017-06-30 (54%); C2g 2017-09-30 (34%); C2g 2017-10-31 (20%); C2g 2017-11-30 (75%); C2g 2017-12-31 (23%); C6 2017-05-31 (23%); C6 2017-06-30 (23%); C6 2017-07-31 (56%); C6 2017-08-31 (67%); C6 2017-10-31 (23%); C6 2017-12-31 (28%); C8 2017-05-31 (40%); C8 2017-06-30 (37%); C8 2017-09-30 (48%); C8 2017-10-31 (23%); C8 2017-11-30 (85%); C8 2017-12-31 (22%); C3 2017-12-31 (23%); C3g 2017-05-31 (33%); C3g 2017-06-30 (25%); C3g 2017-10-31 (24%); C3g 2017-11-30 (37%); C3g 2017-12-31 (62%); C9 2017-05-31 (33%); C9 2017-06-30 (27%); C9 2017-10-31 (23%); C9 2017-11-30 (73%); C9 2017-12-31 (42%); C4 2017-04-30 (33%); C4 2017-09-30 (28%); C4 2017-10-31 (30%); C4g 2017-01-31 (24%); C4g 2017-02-28 (22%); C4g 2017-05-31 (35%); C4g 2017-06-30 (50%); C4g 2017-09-30 (42%); C4g 2017-10-31 (24%); C4g 2017-12-31 (21%)
- Churn risk (accounts renewing in 2017): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £92.60-£198.06/MWh, net margin £80.47
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £115.22
- C2 (electricity): tariff £84.56-£188.36/MWh, net margin £110.01
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £194.46
- C3 (electricity): tariff £98.21-£120.79/MWh, net margin £88.24
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £69.89
- C4 (electricity): tariff £77.34-£164.79/MWh, net margin £49.52
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £136.97
- C5 (electricity): tariff £119.54-£131.01/MWh, net margin £-163.03 -- **net-negative**
- C6 (electricity): tariff £107.62-£126.91/MWh, net margin £98.49
- C7 (electricity): tariff £96.43-£195.85/MWh, net margin £194.36
- C8 (electricity): tariff £84.56-£191.05/MWh, net margin £246.35
- C9 (electricity): tariff £77.16-£181.43/MWh, net margin £166.16
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £30,139.92

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.804, average bill shock 19.3%, bad debt provision £416.34, avg complaint probability 5.1%
- Solvency signal: £249,892/customer (10 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2017 produced a net gain of £31,527.03 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 63 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £101,695.29 (gross £262,602.37, capital £1,640.49)
  - Electricity: gross £261,239.56, capital £1,619.42, net £101,258.35
  - Gas: gross £1,362.80, capital £21.07, net £436.94
- Treasury at year end: £2,487,782.60
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.91 (avg 0.91)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2018-12-31 period 48, net margin £-286.37

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £288,605.58
  - By billing account: C1 £5,706.06, C2 £8,726.77, C3 £9,643.83, C4 £7,300.25, C5 £12,344.35, C6 £20,424.84, C7 £8,038.55, C8 £10,898.61, C9 £10,640.88, C_IC1 £2,792,331.69
- Bill shock events (>=20%): 78 -- C1g 2018-04-30 (40%); C1g 2018-05-31 (33%); C1g 2018-06-30 (35%); C1g 2018-09-30 (34%); C1g 2018-10-31 (56%); C1g 2018-11-30 (31%); C5 2018-01-31 (35%); C5 2018-02-28 (29%); C5 2018-04-30 (24%); C5 2018-06-30 (39%); C5 2018-07-31 (77%); C5 2018-08-31 (76%); C5 2018-09-30 (74%); C5 2018-10-31 (51%); C7 2018-04-30 (39%); C7 2018-05-31 (40%); C7 2018-06-30 (88%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C2g 2018-04-30 (29%); C2g 2018-05-31 (37%); C2g 2018-06-30 (38%); C2g 2018-07-31 (73%); C2g 2018-08-31 (92%); C2g 2018-09-30 (41%); C2g 2018-10-31 (51%); C2g 2018-11-30 (21%); C6 2018-01-31 (37%); C6 2018-02-28 (38%); C6 2018-03-31 (36%); C6 2018-04-30 (31%); C6 2018-07-31 (51%); C6 2018-08-31 (56%); C6 2018-09-30 (46%); C6 2018-10-31 (31%); C6 2018-12-31 (29%); C8 2018-05-31 (38%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (56%); C8 2018-11-30 (30%); C3 2018-01-31 (26%); C3 2018-02-28 (26%); C3 2018-12-31 (21%); C3g 2018-01-31 (66%); C3g 2018-02-28 (68%); C3g 2018-03-31 (66%); C3g 2018-04-30 (68%); C3g 2018-05-31 (54%); C3g 2018-06-30 (30%); C3g 2018-08-31 (43%); C3g 2018-09-30 (41%); C3g 2018-11-30 (42%); C3g 2018-12-31 (49%); C9 2018-04-30 (32%); C9 2018-05-31 (30%); C9 2018-06-30 (35%); C9 2018-07-31 (23%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-04-30 (32%); C4 2018-09-30 (29%); C4 2018-10-31 (50%); C4 2018-11-30 (33%); C4g 2018-04-30 (37%); C4g 2018-05-31 (36%); C4g 2018-06-30 (40%); C4g 2018-08-31 (23%); C4g 2018-09-30 (45%); C4g 2018-10-31 (93%); C4g 2018-11-30 (26%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C2 23%, C3 23%, C6 23%, C7 20%, C8 23%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £92.60-£224.86/MWh, net margin £36.58
- C1g (gas): tariff £33.49-£36.05/MWh, net margin £142.44
- C2 (electricity): tariff £98.66-£215.90/MWh, net margin £93.32
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £189.04
- C3 (electricity): tariff £120.79-£126.89/MWh, net margin £90.26
- C3g (gas): tariff £23.11-£28.80/MWh, net margin £40.74
- C4 (electricity): tariff £86.32-£224.05/MWh, net margin £21.88
- C4g (gas): tariff £26.10-£33.61/MWh, net margin £64.72
- C5 (electricity): tariff £119.54-£153.61/MWh, net margin £-493.24 -- **net-negative**
- C6 (electricity): tariff £126.91-£142.20/MWh, net margin £-6.78 -- **net-negative**
- C7 (electricity): tariff £96.43-£221.22/MWh, net margin £-15.12 -- **net-negative**
- C8 (electricity): tariff £100.07-£200.72/MWh, net margin £164.50
- C9 (electricity): tariff £95.03-£198.37/MWh, net margin £242.67
- C_IC1 (electricity): tariff £-82.12-£228.58/MWh, net margin £107,506.53
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,382.25 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.774, average bill shock 23.0%, bad debt provision £354.07, avg complaint probability 5.8%
- Solvency signal: £226,162/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2018 produced a net gain of £101,695.29 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 78 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £234,088.53 (gross £702,100.60, capital £2,326.39)
  - Electricity: gross £626,046.76, capital £2,304.94, net £223,598.89
  - Gas: gross £76,053.84, capital £21.46, net £10,489.65
- Treasury at year end: £2,611,908.89
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C3 on 2019-12-31 period 48, net margin £-88.12

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £383,128.28
  - By billing account: C1 £5,661.65, C2 £8,873.94, C3 £8,256.51, C4 £6,507.79, C5 £11,192.06, C6 £19,074.59, C7 £8,373.08, C8 £9,472.90, C9 £9,974.34, C_IC1 £2,348,957.18, C_IC2 £1,778,067.01
- Bill shock events (>=20%): 71 -- C1 2019-04-30 (22%); C1g 2019-01-31 (40%); C1g 2019-02-28 (27%); C1g 2019-05-31 (26%); C1g 2019-06-30 (40%); C1g 2019-10-31 (91%); C1g 2019-11-30 (50%); C5 2019-02-28 (32%); C5 2019-06-30 (25%); C5 2019-07-31 (70%); C5 2019-08-31 (77%); C5 2019-09-30 (83%); C5 2019-10-31 (66%); C7 2019-01-31 (46%); C7 2019-02-28 (26%); C7 2019-05-31 (24%); C7 2019-06-30 (35%); C7 2019-10-31 (72%); C7 2019-11-30 (46%); C2g 2019-01-31 (27%); C2g 2019-02-28 (27%); C2g 2019-04-30 (37%); C2g 2019-06-30 (35%); C2g 2019-07-31 (30%); C2g 2019-09-30 (40%); C2g 2019-10-31 (76%); C2g 2019-11-30 (31%); C6 2019-01-31 (35%); C6 2019-02-28 (21%); C6 2019-04-30 (21%); C6 2019-07-31 (43%); C6 2019-08-31 (62%); C6 2019-09-30 (64%); C6 2019-10-31 (36%); C6 2019-12-31 (26%); C8 2019-01-31 (28%); C8 2019-02-28 (28%); C8 2019-04-30 (22%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-10-31 (88%); C8 2019-11-30 (38%); C3 2019-01-31 (23%); C3 2019-02-28 (24%); C3 2019-04-30 (23%); C3g 2019-02-28 (41%); C3g 2019-04-30 (28%); C3g 2019-07-31 (37%); C3g 2019-08-31 (129%); C3g 2019-09-30 (44%); C3g 2019-10-31 (56%); C3g 2019-11-30 (34%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (37%); C9 2019-07-31 (59%); C9 2019-09-30 (53%); C9 2019-11-30 (38%); C4 2019-04-30 (35%); C4 2019-09-30 (33%); C4g 2019-01-31 (31%); C4g 2019-02-28 (25%); C4g 2019-05-31 (22%); C4g 2019-06-30 (35%); C4g 2019-07-31 (40%); C4g 2019-09-30 (36%); C4g 2019-10-31 (37%); C4g 2019-11-30 (38%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C1 29%, C4 35%, C5 35%, C7 29%, C9 23%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £99.01-£224.86/MWh, net margin £122.17
- C1g (gas): tariff £25.33-£36.05/MWh, net margin £156.37
- C2 (electricity): tariff £113.09-£227.85/MWh, net margin £145.70
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £134.46
- C3 (electricity): tariff £120.68-£126.89/MWh, net margin £-62.48 -- **net-negative**
- C3g (gas): tariff £23.00-£28.80/MWh, net margin £97.85
- C4 (electricity): tariff £99.60-£224.05/MWh, net margin £112.89
- C4g (gas): tariff £19.47-£33.61/MWh, net margin £101.05
- C5 (electricity): tariff £126.07-£153.61/MWh, net margin £207.30
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
- Bills issued: 204, average clarity 0.809, average bill shock 20.3%, bad debt provision £47.20, avg complaint probability 5.2%
- Solvency signal: £217,659/customer (12 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2019 produced a net gain of £234,088.53 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 71 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £128,510.78 (gross £791,769.73, capital £1,966.22)
  - Electricity: gross £714,590.18, capital £1,955.93, net £118,022.66
  - Gas: gross £77,179.55, capital £10.29, net £10,488.12
- Treasury at year end: £2,924,300.68
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
- Bill shock events (>=20%): 66 -- C1 2020-04-30 (22%); C1g 2020-01-31 (22%); C1g 2020-04-30 (35%); C1g 2020-05-31 (22%); C1g 2020-06-30 (30%); C1g 2020-08-31 (27%); C1g 2020-10-31 (71%); C1g 2020-11-30 (20%); C1g 2020-12-29 (27%); C5 2020-05-31 (36%); C5 2020-06-30 (61%); C5 2020-07-31 (97%); C5 2020-08-31 (106%); C5 2020-09-30 (110%); C5 2020-10-31 (87%); C5 2020-11-30 (34%); C7 2020-05-31 (21%); C7 2020-06-30 (28%); C7 2020-10-31 (62%); C7 2020-11-30 (24%); C7 2020-12-31 (35%); C2 2020-04-30 (25%); C2g 2020-04-30 (39%); C2g 2020-05-31 (20%); C2g 2020-06-30 (29%); C2g 2020-09-30 (35%); C2g 2020-10-31 (56%); C2g 2020-12-31 (42%); C6 2020-01-31 (30%); C6 2020-02-29 (28%); C6 2020-04-30 (30%); C6 2020-05-31 (21%); C6 2020-06-30 (42%); C6 2020-07-31 (74%); C6 2020-09-30 (59%); C6 2020-10-31 (31%); C8 2020-04-30 (36%); C8 2020-05-31 (26%); C8 2020-06-30 (46%); C8 2020-09-30 (34%); C8 2020-10-31 (68%); C8 2020-12-31 (44%); C3 2020-01-31 (22%); C3 2020-02-29 (23%); C3 2020-04-30 (21%); C3g 2020-06-29 (44%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-09-30 (46%); C9 2020-10-31 (51%); C9 2020-12-31 (37%); C4 2020-04-30 (35%); C4 2020-05-31 (34%); C4 2020-09-30 (27%); C4 2020-10-31 (26%); C4 2020-11-30 (29%); C4g 2020-04-30 (36%); C4g 2020-05-31 (22%); C4g 2020-06-30 (29%); C4g 2020-10-31 (55%); C4g 2020-12-31 (38%); C_IC1 2020-03-31 (58%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 35%, C4 41%, C5 32%, C7 20%, C8 23%, C9 23%, C_IC1 41%, C_IC2 41%, C_IC3 20%

**Pricing & Margin**

- C1 (electricity): tariff £99.01-£189.01/MWh, net margin £99.21
- C1_2 (electricity): tariff £133.55/MWh, net margin £-1.02 -- **net-negative**
- C1g (gas): tariff £25.33/MWh, net margin £145.23
- C2 (electricity): tariff £113.06-£227.85/MWh, net margin £201.59
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £143.77
- C3 (electricity): tariff £120.68/MWh, net margin £44.20
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
- Bills issued: 205, average clarity 0.812, average bill shock 18.3%, bad debt provision £-18.26, avg complaint probability 4.9%
- Solvency signal: £208,879/customer (14 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2020 produced a net gain of £128,510.78 across 19 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £75,467.55 (gross £763,155.26, capital £5,602.62)
  - Electricity: gross £680,540.29, capital £5,590.58, net £65,637.22
  - Gas: gross £82,614.97, capital £12.04, net £9,830.33
- Treasury at year end: £2,957,767.54
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.87 (avg 0.87), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2021-12-31 period 48, net margin £-307.33

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2021): £409,271.50
  - By billing account: C1 £4,744.82, C1_2 £986.91, C2 £6,791.99, C3 £5,831.99, C4 £5,409.21, C5 £12,050.99, C6 £17,951.57, C7 £6,973.39, C8 £9,219.23, C9 £8,492.59, C_IC1 £1,502,450.85, C_IC2 £765,170.10, C_IC3 £2,019,710.36, C_IC4 £1,364,017.02
- Bill shock events (>=20%): 52 -- C7 2021-05-31 (30%); C7 2021-06-30 (47%); C7 2021-10-31 (55%); C7 2021-11-30 (65%); C2 2021-11-30 (21%); C2g 2021-02-28 (20%); C2g 2021-04-30 (50%); C2g 2021-05-31 (26%); C2g 2021-06-30 (58%); C2g 2021-10-31 (67%); C2g 2021-11-30 (66%); C6 2021-01-31 (32%); C6 2021-02-28 (37%); C6 2021-03-31 (24%); C6 2021-07-31 (58%); C6 2021-08-31 (62%); C6 2021-10-31 (28%); C6 2021-12-31 (45%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (25%); C8 2021-10-31 (69%); C8 2021-11-30 (84%); C9 2021-02-28 (22%); C9 2021-05-31 (25%); C9 2021-06-30 (51%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-11-30 (50%); C9 2021-12-31 (24%); C4 2021-04-30 (35%); C4 2021-09-30 (30%); C4 2021-10-31 (53%); C4 2021-11-30 (38%); C4g 2021-05-31 (24%); C4g 2021-06-30 (57%); C4g 2021-10-31 (132%); C4g 2021-11-30 (61%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (76%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (21%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (27%); C1_2 2021-01-31 (1202%); C1_2 2021-05-31 (34%); C1_2 2021-06-30 (58%); C1_2 2021-10-31 (85%); C1_2 2021-11-30 (80%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C7 20%, C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £133.55-£333.14/MWh, net margin £-89.36 -- **net-negative**
- C2 (electricity): tariff £113.06-£274.50/MWh, net margin £198.84
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £126.10
- C4 (electricity): tariff £96.23-£274.50/MWh, net margin £-37.46 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-295.69 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.10/MWh, net margin £218.33
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
- Bills issued: 168, average clarity 0.809, average bill shock 25.8%, bad debt provision £373.77, avg complaint probability 5.1%
- Solvency signal: £268,888/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £75,467.55 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 52 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £338,356.66 (gross £1,049,224.77, capital £13,276.32)
  - Electricity: gross £958,836.70, capital £13,229.01, net £329,615.83
  - Gas: gross £90,388.06, capital £47.31, net £8,740.82
- Treasury at year end: £3,161,940.47
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
- Bill shock events (>=20%): 71 -- C7 2022-02-28 (26%); C7 2022-05-31 (35%); C7 2022-06-30 (26%); C7 2022-09-30 (32%); C7 2022-11-30 (61%); C7 2022-12-31 (55%); C2g 2022-02-28 (22%); C2g 2022-04-30 (69%); C2g 2022-05-31 (38%); C2g 2022-06-30 (31%); C2g 2022-07-31 (20%); C2g 2022-09-30 (65%); C2g 2022-11-30 (22%); C2g 2022-12-31 (63%); C6 2022-01-31 (47%); C6 2022-04-30 (54%); C6 2022-06-30 (39%); C6 2022-07-31 (69%); C6 2022-08-31 (85%); C6 2022-09-30 (88%); C6 2022-10-31 (50%); C6 2022-11-30 (37%); C8 2022-05-31 (39%); C8 2022-06-30 (34%); C8 2022-07-31 (21%); C8 2022-09-30 (81%); C8 2022-12-31 (57%); C9 2022-04-30 (21%); C9 2022-05-31 (29%); C9 2022-06-30 (37%); C9 2022-09-30 (48%); C9 2022-10-31 (30%); C9 2022-11-30 (44%); C9 2022-12-31 (52%); C4 2022-06-30 (59%); C4 2022-11-30 (36%); C4g 2022-01-31 (26%); C4g 2022-02-28 (24%); C4g 2022-05-31 (36%); C4g 2022-06-30 (30%); C4g 2022-07-31 (25%); C4g 2022-09-30 (75%); C4g 2022-10-31 (43%); C4g 2022-11-30 (42%); C4g 2022-12-31 (57%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (109%); C_IC3g 2022-01-31 (25%); C_IC3g 2022-03-31 (33%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (50%); C_IC3g 2022-08-31 (39%); C_IC3g 2022-10-31 (50%); C_IC3g 2022-11-30 (31%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C1_2 2022-01-31 (100%); C1_2 2022-04-30 (24%); C1_2 2022-05-31 (21%); C1_2 2022-06-30 (36%); C1_2 2022-07-31 (157%); C1_2 2022-08-31 (172%); C1_2 2022-09-30 (54%); C1_2 2022-10-31 (21%); C1_2 2022-12-31 (42%)
- Churn risk (accounts renewing in 2022): 11 at risk (≥20% churn prob): C1_2 41%, C2 38%, C4 38%, C6 35%, C7 29%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.96-£333.14/MWh, net margin £184.51
- C2 (electricity): tariff £143.79-£457.50/MWh, net margin £2.28
- C2g (gas): tariff £35.00-£95.00/MWh, net margin £-102.36 -- **net-negative**
- C4 (electricity): tariff £143.79-£457.50/MWh, net margin £-264.34 -- **net-negative**
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
- Treasury drawdown events (>=10% threshold): 2 -- £3,471,282.58 -> £3,053,420.63 (12.0%); £3,471,460.87 -> £3,052,874.83 (12.1%)
- Bills issued: 168, average clarity 0.785, average bill shock 24.5%, bad debt provision £63.03, avg complaint probability 5.8%
- Solvency signal: £287,449/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £338,356.66 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 71 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £144,318.64 (gross £955,881.82, capital £10,036.50)
  - Electricity: gross £834,588.49, capital £9,961.08, net £135,295.09
  - Gas: gross £121,293.34, capital £75.41, net £9,023.55
- Treasury at year end: £3,382,522.01
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.91 (avg 0.91), C2 0.95 (avg 0.95), C2g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,137,514.98, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-02-23: treasury £3,137,498.06, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-03-25: treasury £3,137,481.31, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-04-24: treasury £3,217,144.83, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,230.41 / stressed £48,907.75) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C6 on 2023-12-31 period 48, net margin £-2,088.98

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2023): £363,185.43
  - By billing account: C1 £3,680.74, C1_2 £1,944.13, C2 £4,982.25, C3 £4,440.04, C4 £2,107.60, C5 £7,623.31, C6 £17,306.38, C7 £5,356.78, C8 £7,277.99, C9 £6,952.69, C_IC1 £1,320,738.65, C_IC2 £640,507.44, C_IC3 £1,892,395.24, C_IC4 £1,169,282.75
- Bill shock events (>=20%): 60 -- C7 2023-01-31 (40%); C7 2023-06-30 (36%); C7 2023-07-31 (86%); C7 2023-10-31 (55%); C7 2023-11-30 (70%); C7 2023-12-31 (33%); C2 2023-04-30 (28%); C2g 2023-01-31 (42%); C2g 2023-04-30 (35%); C2g 2023-05-31 (40%); C2g 2023-06-30 (40%); C2g 2023-08-31 (21%); C2g 2023-10-31 (96%); C2g 2023-11-30 (60%); C6 2023-01-31 (28%); C6 2023-02-28 (24%); C6 2023-04-30 (32%); C6 2023-06-30 (45%); C6 2023-07-31 (89%); C6 2023-08-31 (90%); C6 2023-09-30 (88%); C6 2023-10-31 (83%); C6 2023-11-30 (44%); C8 2023-04-30 (30%); C8 2023-05-31 (40%); C8 2023-06-30 (43%); C8 2023-11-30 (50%); C9 2023-02-28 (21%); C9 2023-03-31 (24%); C9 2023-04-30 (26%); C9 2023-05-31 (33%); C9 2023-06-30 (45%); C9 2023-09-30 (21%); C9 2023-10-31 (74%); C9 2023-11-30 (53%); C4 2023-02-28 (26%); C4 2023-06-30 (50%); C4 2023-09-30 (29%); C4 2023-11-30 (32%); C4g 2023-05-31 (37%); C4g 2023-06-30 (46%); C4g 2023-10-31 (47%); C4g 2023-11-30 (67%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (101%); C_IC3g 2023-01-31 (36%); C_IC4 2023-01-31 (35%); C1_2 2023-01-31 (69%); C1_2 2023-02-28 (62%); C1_2 2023-04-30 (45%); C1_2 2023-05-31 (32%); C1_2 2023-07-31 (100%); C1_2 2023-08-31 (120%); C1_2 2023-09-30 (114%); C1_2 2023-10-31 (90%); C1_2 2023-12-31 (43%)
- Churn risk (accounts renewing in 2023): 10 at risk (≥20% churn prob): C2 41%, C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.96-£267.80/MWh, net margin £-439.82 -- **net-negative**
- C2 (electricity): tariff £208.21-£457.50/MWh, net margin £88.59
- C2g (gas): tariff £70.00-£95.00/MWh, net margin £136.46
- C4 (electricity): tariff £198.37-£457.50/MWh, net margin £-13.16 -- **net-negative**
- C4g (gas): tariff £64.73-£95.00/MWh, net margin £-1,112.83 -- **net-negative**
- C6 (electricity): tariff £338.13-£412.09/MWh, net margin £-708.90 -- **net-negative**
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
- Treasury drawdown events (>=10% threshold): 47 -- £3,768,762.14 -> £3,382,447.41 (10.3%); £3,768,762.29 -> £3,382,447.41 (10.3%); £3,768,762.44 -> £3,382,447.40 (10.3%); £3,768,762.59 -> £3,382,447.40 (10.3%); £3,768,762.75 -> £3,382,447.40 (10.3%); £3,768,762.90 -> £3,382,447.40 (10.3%); £3,768,763.05 -> £3,382,447.40 (10.3%); £3,768,763.21 -> £3,382,447.40 (10.3%); £3,768,763.36 -> £3,382,447.40 (10.3%); £3,768,763.52 -> £3,382,447.40 (10.3%); £3,768,763.68 -> £3,382,447.40 (10.3%); £3,768,763.83 -> £3,382,447.40 (10.3%); £3,768,763.99 -> £3,382,447.39 (10.3%); £3,768,764.16 -> £3,382,447.39 (10.3%); £3,768,764.35 -> £3,382,447.38 (10.3%); £3,768,764.56 -> £3,382,447.38 (10.3%); £3,768,764.78 -> £3,382,447.37 (10.3%); £3,768,765.02 -> £3,382,447.36 (10.3%); £3,768,765.29 -> £3,382,447.34 (10.3%); £3,768,765.54 -> £3,382,447.33 (10.3%); £3,768,765.80 -> £3,382,447.32 (10.3%); £3,768,766.05 -> £3,382,447.31 (10.3%); £3,768,766.32 -> £3,382,447.29 (10.3%); £3,768,766.58 -> £3,382,447.28 (10.3%); £3,768,766.84 -> £3,382,447.27 (10.3%); £3,768,767.11 -> £3,382,447.25 (10.3%); £3,768,767.38 -> £3,382,447.24 (10.3%); £3,768,767.63 -> £3,382,447.23 (10.3%); £3,768,767.89 -> £3,382,447.22 (10.3%); £3,768,768.14 -> £3,382,447.21 (10.3%); £3,768,768.40 -> £3,382,447.21 (10.3%); £3,768,768.65 -> £3,382,447.20 (10.3%); £3,768,768.92 -> £3,382,447.18 (10.3%); £3,768,769.17 -> £3,382,447.16 (10.3%); £3,768,769.43 -> £3,382,447.14 (10.3%); £3,768,769.69 -> £3,382,447.12 (10.3%); £3,768,769.95 -> £3,382,447.09 (10.3%); £3,768,770.21 -> £3,382,447.06 (10.3%); £3,768,770.48 -> £3,382,447.03 (10.3%); £3,768,770.74 -> £3,382,447.00 (10.3%); £3,768,771.00 -> £3,382,446.97 (10.3%); £3,768,771.26 -> £3,382,446.94 (10.3%); £3,768,771.52 -> £3,382,446.92 (10.3%); £3,768,771.78 -> £3,382,446.91 (10.3%); £3,768,772.04 -> £3,382,446.90 (10.3%); £3,768,772.28 -> £3,382,446.89 (10.3%); £3,768,772.50 -> £3,381,749.18 (10.3%)
- Bills issued: 168, average clarity 0.786, average bill shock 22.7%, bad debt provision £2,250.89, avg complaint probability 5.7%
- Solvency signal: £307,502/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2023 produced a net gain of £144,318.64 across 14 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 60 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £347,778.98 (gross £1,257,805.74, capital £9,522.03)
  - Electricity: gross £1,132,855.54, capital £9,477.19, net £337,070.09
  - Gas: gross £124,950.20, capital £44.84, net £10,708.88
- Treasury at year end: £3,775,069.66
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.87 (avg 0.87), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C4 on 2024-09-28 period 48, net margin £-112.78

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £348,560.03
  - By billing account: C1 £3,291.89, C1_2 £2,675.04, C2 £4,369.83, C3 £4,033.43, C4 £2,598.16, C5 £7,834.04, C6 £15,341.31, C7 £4,975.97, C8 £7,062.48, C9 £7,097.09, C_IC1 £1,156,263.05, C_IC2 £680,833.29, C_IC3 £2,019,730.99, C_IC4 £963,733.92
- Bill shock events (>=20%): 44 -- C7 2024-02-29 (27%); C7 2024-05-31 (37%); C7 2024-09-30 (34%); C7 2024-11-30 (48%); C2 2024-04-30 (34%); C2g 2024-02-29 (24%); C2g 2024-04-30 (37%); C2g 2024-05-31 (47%); C2g 2024-07-31 (25%); C2g 2024-09-30 (53%); C2g 2024-10-31 (34%); C2g 2024-11-30 (52%); C8 2024-02-29 (23%); C8 2024-04-30 (34%); C8 2024-05-31 (27%); C8 2024-07-31 (65%); C8 2024-09-30 (72%); C8 2024-10-31 (35%); C8 2024-11-30 (61%); C9 2024-05-31 (49%); C9 2024-07-31 (30%); C9 2024-09-30 (55%); C9 2024-10-31 (23%); C9 2024-11-30 (47%); C4 2024-04-30 (33%); C4g 2024-02-29 (27%); C4g 2024-05-31 (41%); C4g 2024-07-31 (26%); C4g 2024-09-28 (51%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (63%); C_IC2 2024-06-30 (50%); C_IC2 2024-07-31 (79%); C1_2 2024-01-31 (45%); C1_2 2024-02-29 (55%); C1_2 2024-03-31 (36%); C1_2 2024-04-30 (24%); C1_2 2024-06-30 (79%); C1_2 2024-07-31 (109%); C1_2 2024-08-31 (161%); C1_2 2024-09-30 (174%); C1_2 2024-10-31 (77%); C1_2 2024-11-30 (21%); C1_2 2024-12-31 (24%)
- Churn risk (accounts renewing in 2024): 8 at risk (≥20% churn prob): C2 41%, C4 38%, C6 26%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC3 41%, C_IC4 20%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01-£267.80/MWh, net margin £760.69
- C2 (electricity): tariff £157.80-£397.50/MWh, net margin £210.04
- C2g (gas): tariff £48.30-£70.00/MWh, net margin £265.39
- C4 (electricity): tariff £198.37-£378.70/MWh, net margin £114.48
- C4g (gas): tariff £64.73/MWh, net margin £412.73
- C6 (electricity): tariff £338.13/MWh, net margin £772.41
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
- Treasury drawdown events (>=10% threshold): 4271 -- £3,771,220.49 -> £3,381,749.25 (10.3%); £3,771,220.66 -> £3,381,749.29 (10.3%); £3,771,220.83 -> £3,381,749.32 (10.3%); £3,771,221.01 -> £3,381,749.36 (10.3%); £3,771,221.18 -> £3,381,749.40 (10.3%); £3,771,221.35 -> £3,381,749.43 (10.3%); £3,771,221.53 -> £3,381,749.47 (10.3%); £3,771,221.70 -> £3,381,749.51 (10.3%); £3,771,221.87 -> £3,381,749.54 (10.3%); £3,771,222.05 -> £3,381,749.58 (10.3%); £3,771,222.22 -> £3,381,749.62 (10.3%); £3,771,222.40 -> £3,381,749.80 (10.3%); £3,771,222.56 -> £3,381,749.98 (10.3%); £3,771,222.76 -> £3,381,750.18 (10.3%); £3,771,222.96 -> £3,381,750.39 (10.3%); £3,771,223.19 -> £3,381,750.63 (10.3%); £3,771,223.43 -> £3,381,750.88 (10.3%); £3,771,223.69 -> £3,381,751.16 (10.3%); £3,771,223.98 -> £3,381,751.44 (10.3%); £3,771,224.25 -> £3,381,751.56 (10.3%); £3,771,224.55 -> £3,381,751.69 (10.3%); £3,771,224.84 -> £3,381,751.81 (10.3%); £3,771,225.14 -> £3,381,751.94 (10.3%); £3,771,225.42 -> £3,381,752.06 (10.3%); £3,771,225.71 -> £3,381,752.19 (10.3%); £3,771,226.00 -> £3,381,752.31 (10.3%); £3,771,226.28 -> £3,381,752.42 (10.3%); £3,771,226.56 -> £3,381,752.53 (10.3%); £3,771,226.83 -> £3,381,752.64 (10.3%); £3,771,227.11 -> £3,381,752.76 (10.3%); £3,771,227.40 -> £3,381,752.88 (10.3%); £3,771,227.69 -> £3,381,752.99 (10.3%); £3,771,227.97 -> £3,381,753.28 (10.3%); £3,771,228.25 -> £3,381,753.53 (10.3%); £3,771,228.47 -> £3,381,753.76 (10.3%); £3,771,228.69 -> £3,381,753.97 (10.3%); £3,771,228.91 -> £3,381,754.19 (10.3%); £3,771,229.21 -> £3,381,754.39 (10.3%); £3,771,229.50 -> £3,381,754.60 (10.3%); £3,771,229.78 -> £3,381,754.81 (10.3%); £3,771,230.07 -> £3,381,755.01 (10.3%); £3,771,230.35 -> £3,381,755.20 (10.3%); £3,771,230.65 -> £3,381,755.39 (10.3%); £3,771,230.94 -> £3,381,755.44 (10.3%); £3,771,231.23 -> £3,381,755.48 (10.3%); £3,771,231.49 -> £3,381,755.52 (10.3%); £3,771,231.73 -> £3,381,755.56 (10.3%); £3,771,231.95 -> £3,381,755.60 (10.3%); £3,771,232.13 -> £3,381,755.64 (10.3%); £3,771,232.30 -> £3,381,755.68 (10.3%); £3,771,232.47 -> £3,381,755.72 (10.3%); £3,771,232.63 -> £3,381,755.76 (10.3%); £3,771,232.80 -> £3,381,755.80 (10.3%); £3,771,232.97 -> £3,381,755.84 (10.3%); £3,771,233.15 -> £3,381,755.88 (10.3%); £3,771,233.32 -> £3,381,755.92 (10.3%); £3,771,233.49 -> £3,381,755.96 (10.3%); £3,771,233.66 -> £3,381,756.00 (10.3%); £3,771,233.83 -> £3,381,756.04 (10.3%); £3,771,234.00 -> £3,381,756.20 (10.3%); £3,771,234.17 -> £3,381,756.37 (10.3%); £3,771,234.35 -> £3,381,756.54 (10.3%); £3,771,234.56 -> £3,381,756.73 (10.3%); £3,771,234.78 -> £3,381,756.95 (10.3%); £3,771,235.02 -> £3,381,757.18 (10.3%); £3,771,235.27 -> £3,381,757.45 (10.3%); £3,771,235.55 -> £3,381,757.72 (10.3%); £3,771,235.83 -> £3,381,757.86 (10.3%); £3,771,236.11 -> £3,381,757.98 (10.3%); £3,771,236.39 -> £3,381,758.10 (10.3%); £3,771,236.68 -> £3,381,758.24 (10.3%); £3,771,236.95 -> £3,381,758.37 (10.3%); £3,771,237.23 -> £3,381,758.48 (10.3%); £3,771,237.51 -> £3,381,758.60 (10.3%); £3,771,237.79 -> £3,381,758.72 (10.3%); £3,771,238.07 -> £3,381,758.83 (10.3%); £3,771,238.34 -> £3,381,758.94 (10.3%); £3,771,238.62 -> £3,381,759.05 (10.3%); £3,771,238.89 -> £3,381,759.16 (10.3%); £3,771,239.17 -> £3,381,759.27 (10.3%); £3,771,239.38 -> £3,381,759.51 (10.3%); £3,771,239.60 -> £3,381,759.74 (10.3%); £3,771,239.81 -> £3,381,759.94 (10.3%); £3,771,240.02 -> £3,381,760.12 (10.3%); £3,771,240.24 -> £3,381,760.29 (10.3%); £3,771,240.45 -> £3,381,760.46 (10.3%); £3,771,240.66 -> £3,381,760.62 (10.3%); £3,771,240.94 -> £3,381,760.78 (10.3%); £3,771,241.23 -> £3,381,760.95 (10.3%); £3,771,241.50 -> £3,381,761.11 (10.3%); £3,771,241.79 -> £3,381,761.27 (10.3%); £3,771,242.07 -> £3,381,761.31 (10.3%); £3,771,242.35 -> £3,381,761.35 (10.3%); £3,771,242.62 -> £3,381,761.39 (10.3%); £3,771,242.85 -> £3,381,761.43 (10.3%); £3,771,243.07 -> £3,381,761.46 (10.3%); £3,771,243.24 -> £3,381,761.50 (10.3%); £3,771,243.41 -> £3,381,761.54 (10.3%); £3,771,243.58 -> £3,381,761.57 (10.3%); £3,771,243.75 -> £3,381,761.61 (10.3%); £3,771,243.92 -> £3,381,761.65 (10.3%); £3,771,244.09 -> £3,381,761.68 (10.3%); £3,771,244.26 -> £3,381,761.72 (10.3%); £3,771,244.42 -> £3,381,761.76 (10.3%); £3,771,244.59 -> £3,381,761.80 (10.3%); £3,771,244.76 -> £3,381,761.83 (10.3%); £3,771,244.93 -> £3,381,761.88 (10.3%); £3,771,245.11 -> £3,381,762.06 (10.3%); £3,771,245.28 -> £3,381,762.25 (10.3%); £3,771,245.46 -> £3,381,762.45 (10.3%); £3,771,245.67 -> £3,381,762.67 (10.3%); £3,771,245.90 -> £3,381,762.91 (10.3%); £3,771,246.14 -> £3,381,763.15 (10.3%); £3,771,246.41 -> £3,381,763.41 (10.3%); £3,771,246.69 -> £3,381,763.68 (10.3%); £3,771,246.97 -> £3,381,763.80 (10.3%); £3,771,247.25 -> £3,381,763.92 (10.3%); £3,771,247.53 -> £3,381,764.05 (10.3%); £3,771,247.82 -> £3,381,764.17 (10.3%); £3,771,248.11 -> £3,381,764.29 (10.3%); £3,771,248.40 -> £3,381,764.41 (10.3%); £3,771,248.69 -> £3,381,764.52 (10.3%); £3,771,248.97 -> £3,381,764.64 (10.3%); £3,771,249.25 -> £3,381,764.76 (10.3%); £3,771,249.53 -> £3,381,764.88 (10.3%); £3,771,249.82 -> £3,381,764.99 (10.3%); £3,771,250.09 -> £3,381,765.11 (10.3%); £3,771,250.37 -> £3,381,765.22 (10.3%); £3,771,250.65 -> £3,381,765.48 (10.3%); £3,771,250.87 -> £3,381,765.75 (10.3%); £3,771,251.15 -> £3,381,765.97 (10.3%); £3,771,251.36 -> £3,381,766.17 (10.3%); £3,771,251.57 -> £3,381,766.36 (10.3%); £3,771,251.78 -> £3,381,766.54 (10.3%); £3,771,252.00 -> £3,381,766.74 (10.3%); £3,771,252.27 -> £3,381,766.93 (10.3%); £3,771,252.55 -> £3,381,767.12 (10.3%); £3,771,252.84 -> £3,381,767.30 (10.3%); £3,771,253.11 -> £3,381,767.47 (10.3%); £3,771,253.40 -> £3,381,767.51 (10.3%); £3,771,253.69 -> £3,381,767.55 (10.3%); £3,771,253.94 -> £3,381,767.59 (10.3%); £3,771,254.18 -> £3,381,767.62 (10.3%); £3,771,254.40 -> £3,381,767.66 (10.3%); £3,771,254.56 -> £3,381,767.70 (10.3%); £3,771,254.73 -> £3,381,767.74 (10.3%); £3,771,254.89 -> £3,381,767.78 (10.3%); £3,771,255.06 -> £3,381,767.81 (10.3%); £3,771,255.23 -> £3,381,767.85 (10.3%); £3,771,255.40 -> £3,381,767.89 (10.3%); £3,771,255.57 -> £3,381,767.93 (10.3%); £3,771,255.73 -> £3,381,767.97 (10.3%); £3,771,255.90 -> £3,381,768.01 (10.3%); £3,771,256.07 -> £3,381,768.04 (10.3%); £3,771,256.24 -> £3,381,768.08 (10.3%); £3,771,256.41 -> £3,381,768.29 (10.3%); £3,771,256.58 -> £3,381,768.50 (10.3%); £3,771,256.77 -> £3,381,768.72 (10.3%); £3,771,256.97 -> £3,381,768.95 (10.3%); £3,771,257.19 -> £3,381,769.19 (10.3%); £3,771,257.43 -> £3,381,769.47 (10.3%); £3,771,257.69 -> £3,381,769.77 (10.3%); £3,771,257.97 -> £3,381,770.08 (10.3%); £3,771,258.24 -> £3,381,770.21 (10.3%); £3,771,258.53 -> £3,381,770.33 (10.3%); £3,771,258.80 -> £3,381,770.46 (10.3%); £3,771,259.08 -> £3,381,770.59 (10.3%); £3,771,259.36 -> £3,381,770.71 (10.3%); £3,771,259.63 -> £3,381,770.83 (10.3%); £3,771,259.91 -> £3,381,770.94 (10.3%); £3,771,260.19 -> £3,381,771.05 (10.3%); £3,771,260.47 -> £3,381,771.16 (10.3%); £3,771,260.74 -> £3,381,771.28 (10.3%); £3,771,261.02 -> £3,381,771.39 (10.3%); £3,771,261.30 -> £3,381,771.50 (10.3%); £3,771,261.58 -> £3,381,771.60 (10.3%); £3,771,261.79 -> £3,381,771.90 (10.3%); £3,771,262.06 -> £3,381,772.18 (10.3%); £3,771,262.34 -> £3,381,772.41 (10.3%); £3,771,262.54 -> £3,381,772.63 (10.3%); £3,771,262.81 -> £3,381,772.85 (10.3%); £3,771,263.09 -> £3,381,773.05 (10.3%); £3,771,263.31 -> £3,381,773.25 (10.3%); £3,771,263.59 -> £3,381,773.45 (10.3%); £3,771,263.86 -> £3,381,773.65 (10.3%); £3,771,264.15 -> £3,381,773.84 (10.3%); £3,771,264.42 -> £3,381,774.04 (10.3%); £3,771,264.71 -> £3,381,774.08 (10.3%); £3,771,264.98 -> £3,381,774.12 (10.3%); £3,771,265.23 -> £3,381,774.16 (10.3%); £3,771,265.47 -> £3,381,774.19 (10.3%); £3,771,265.69 -> £3,381,774.23 (10.3%); £3,771,265.85 -> £3,381,774.27 (10.3%); £3,771,266.01 -> £3,381,774.30 (10.3%); £3,771,266.17 -> £3,381,774.34 (10.3%); £3,771,266.33 -> £3,381,774.38 (10.3%); £3,771,266.49 -> £3,381,774.42 (10.3%); £3,771,266.65 -> £3,381,774.45 (10.3%); £3,771,266.82 -> £3,381,774.49 (10.3%); £3,771,266.97 -> £3,381,774.53 (10.3%); £3,771,267.14 -> £3,381,774.57 (10.3%); £3,771,267.31 -> £3,381,774.61 (10.3%); £3,771,267.47 -> £3,381,774.65 (10.3%); £3,771,267.63 -> £3,381,774.87 (10.3%); £3,771,267.79 -> £3,381,775.08 (10.3%); £3,771,267.97 -> £3,381,775.33 (10.3%); £3,771,268.17 -> £3,381,775.58 (10.3%); £3,771,268.38 -> £3,381,775.85 (10.3%); £3,771,268.61 -> £3,381,776.13 (10.3%); £3,771,268.87 -> £3,381,776.43 (10.3%); £3,771,269.14 -> £3,381,776.74 (10.3%); £3,771,269.42 -> £3,381,776.86 (10.3%); £3,771,269.68 -> £3,381,776.99 (10.3%); £3,771,269.95 -> £3,381,777.11 (10.3%); £3,771,270.22 -> £3,381,777.24 (10.3%); £3,771,270.49 -> £3,381,777.37 (10.3%); £3,771,270.76 -> £3,381,777.49 (10.3%); £3,771,271.04 -> £3,381,777.61 (10.3%); £3,771,271.31 -> £3,381,777.73 (10.3%); £3,771,271.57 -> £3,381,777.84 (10.3%); £3,771,271.83 -> £3,381,777.96 (10.3%); £3,771,272.10 -> £3,381,778.07 (10.3%); £3,771,272.36 -> £3,381,778.18 (10.3%); £3,771,272.64 -> £3,381,778.28 (10.3%); £3,771,272.84 -> £3,381,778.58 (10.3%); £3,771,273.04 -> £3,381,778.85 (10.3%); £3,771,273.25 -> £3,381,779.11 (10.3%); £3,771,273.45 -> £3,381,779.35 (10.3%); £3,771,273.72 -> £3,381,779.57 (10.3%); £3,771,273.92 -> £3,381,779.79 (10.3%); £3,771,274.12 -> £3,381,780.01 (10.3%); £3,771,274.39 -> £3,381,780.22 (10.3%); £3,771,274.66 -> £3,381,780.43 (10.3%); £3,771,274.92 -> £3,381,780.65 (10.3%); £3,771,275.19 -> £3,381,780.86 (10.3%); £3,771,275.45 -> £3,381,780.90 (10.3%); £3,771,275.72 -> £3,381,780.94 (10.3%); £3,771,275.98 -> £3,381,780.98 (10.3%); £3,771,276.21 -> £3,381,781.02 (10.3%); £3,771,276.42 -> £3,381,781.06 (10.3%); £3,771,276.56 -> £3,381,781.09 (10.3%); £3,771,276.71 -> £3,381,781.13 (10.3%); £3,771,276.85 -> £3,381,781.17 (10.3%); £3,771,277.00 -> £3,381,781.21 (10.3%); £3,771,277.14 -> £3,381,781.25 (10.3%); £3,771,277.29 -> £3,381,781.28 (10.3%); £3,771,277.42 -> £3,381,781.32 (10.3%); £3,771,277.56 -> £3,381,781.36 (10.3%); £3,771,277.70 -> £3,381,781.39 (10.3%); £3,771,277.84 -> £3,381,781.43 (10.3%); £3,771,277.98 -> £3,381,781.47 (10.3%); £3,771,278.12 -> £3,381,781.73 (10.3%); £3,771,278.26 -> £3,381,781.98 (10.3%); £3,771,278.42 -> £3,381,782.25 (10.3%); £3,771,278.59 -> £3,381,782.52 (10.3%); £3,771,278.78 -> £3,381,782.79 (10.3%); £3,771,278.99 -> £3,381,783.08 (10.3%); £3,771,279.20 -> £3,381,783.40 (10.3%); £3,771,279.44 -> £3,381,783.72 (10.3%); £3,771,279.67 -> £3,381,783.81 (10.3%); £3,771,279.91 -> £3,381,783.89 (10.3%); £3,771,280.14 -> £3,381,783.98 (10.3%); £3,771,280.38 -> £3,381,784.07 (10.3%); £3,771,280.61 -> £3,381,784.15 (10.3%); £3,771,280.85 -> £3,381,784.23 (10.3%); £3,771,281.08 -> £3,381,784.30 (10.3%); £3,771,281.33 -> £3,381,784.38 (10.3%); £3,771,281.57 -> £3,381,784.44 (10.3%); £3,771,281.81 -> £3,381,784.51 (10.3%); £3,771,282.05 -> £3,381,784.58 (10.3%); £3,771,282.28 -> £3,381,784.64 (10.3%); £3,771,282.53 -> £3,381,784.71 (10.3%); £3,771,282.75 -> £3,381,784.98 (10.3%); £3,771,282.92 -> £3,381,785.24 (10.3%); £3,771,283.10 -> £3,381,785.50 (10.3%); £3,771,283.27 -> £3,381,785.74 (10.3%); £3,771,283.45 -> £3,381,785.99 (10.3%); £3,771,283.63 -> £3,381,786.23 (10.3%); £3,771,283.81 -> £3,381,786.49 (10.3%); £3,771,284.04 -> £3,381,786.74 (10.3%); £3,771,284.27 -> £3,381,786.99 (10.3%); £3,771,284.50 -> £3,381,787.23 (10.3%); £3,771,284.74 -> £3,381,787.48 (10.3%); £3,771,284.97 -> £3,381,787.52 (10.3%); £3,771,285.20 -> £3,381,787.56 (10.3%); £3,771,285.42 -> £3,381,787.60 (10.3%); £3,771,285.62 -> £3,381,787.64 (10.3%); £3,771,285.80 -> £3,381,787.68 (10.3%); £3,771,285.94 -> £3,381,787.71 (10.3%); £3,771,286.08 -> £3,381,787.75 (10.3%); £3,771,286.23 -> £3,381,787.79 (10.3%); £3,771,286.37 -> £3,381,787.83 (10.3%); £3,771,286.50 -> £3,381,787.86 (10.3%); £3,771,286.64 -> £3,381,787.90 (10.3%); £3,771,286.78 -> £3,381,787.93 (10.3%); £3,771,286.93 -> £3,381,787.97 (10.3%); £3,771,287.06 -> £3,381,788.01 (10.3%); £3,771,287.20 -> £3,381,788.04 (10.3%); £3,771,287.34 -> £3,381,788.08 (10.3%); £3,771,287.48 -> £3,381,788.33 (10.3%); £3,771,287.62 -> £3,381,788.57 (10.3%); £3,771,287.77 -> £3,381,788.82 (10.3%); £3,771,287.95 -> £3,381,789.06 (10.3%); £3,771,288.14 -> £3,381,789.31 (10.3%); £3,771,288.34 -> £3,381,789.56 (10.3%); £3,771,288.56 -> £3,381,789.80 (10.3%); £3,771,288.79 -> £3,381,790.05 (10.3%); £3,771,289.04 -> £3,381,790.10 (10.3%); £3,771,289.26 -> £3,381,790.14 (10.3%); £3,771,289.49 -> £3,381,790.19 (10.3%); £3,771,289.72 -> £3,381,790.24 (10.3%); £3,771,289.95 -> £3,381,790.29 (10.3%); £3,771,290.18 -> £3,381,790.34 (10.3%); £3,771,290.41 -> £3,381,790.38 (10.3%); £3,771,290.64 -> £3,381,790.42 (10.3%); £3,771,290.87 -> £3,381,790.47 (10.3%); £3,771,291.11 -> £3,381,790.52 (10.3%); £3,771,291.34 -> £3,381,790.56 (10.3%); £3,771,291.57 -> £3,381,790.60 (10.3%); £3,771,291.80 -> £3,381,790.65 (10.3%); £3,771,291.98 -> £3,381,790.88 (10.3%); £3,771,292.15 -> £3,381,791.11 (10.3%); £3,771,292.32 -> £3,381,791.35 (10.3%); £3,771,292.49 -> £3,381,791.60 (10.3%); £3,771,292.73 -> £3,381,791.84 (10.3%); £3,771,292.91 -> £3,381,792.07 (10.3%); £3,771,293.08 -> £3,381,792.32 (10.3%); £3,771,293.32 -> £3,381,792.57 (10.3%); £3,771,293.55 -> £3,381,792.81 (10.3%); £3,771,293.79 -> £3,381,793.04 (10.3%); £3,771,294.02 -> £3,381,793.28 (10.3%); £3,771,294.24 -> £3,381,793.32 (10.3%); £3,771,294.48 -> £3,381,793.36 (10.3%); £3,771,294.69 -> £3,381,793.40 (10.3%); £3,771,294.89 -> £3,381,793.43 (10.3%); £3,771,295.08 -> £3,381,793.47 (10.3%); £3,771,295.24 -> £3,381,793.51 (10.3%); £3,771,295.39 -> £3,381,793.54 (10.3%); £3,771,295.54 -> £3,381,793.58 (10.3%); £3,771,295.69 -> £3,381,793.62 (10.3%); £3,771,295.84 -> £3,381,793.66 (10.3%); £3,771,296.00 -> £3,381,793.69 (10.3%); £3,771,296.15 -> £3,381,793.73 (10.3%); £3,771,296.31 -> £3,381,793.77 (10.3%); £3,771,296.46 -> £3,381,793.81 (10.3%); £3,771,296.62 -> £3,381,793.84 (10.3%); £3,771,296.77 -> £3,381,793.89 (10.3%); £3,771,296.92 -> £3,381,794.12 (10.3%); £3,771,297.08 -> £3,381,794.38 (10.3%); £3,771,297.25 -> £3,381,794.64 (10.3%); £3,771,297.43 -> £3,381,794.90 (10.3%); £3,771,297.64 -> £3,381,795.20 (10.3%); £3,771,297.86 -> £3,381,795.52 (10.3%); £3,771,298.09 -> £3,381,795.86 (10.3%); £3,771,298.34 -> £3,381,796.22 (10.3%); £3,771,298.59 -> £3,381,796.33 (10.3%); £3,771,298.84 -> £3,381,796.45 (10.3%); £3,771,299.11 -> £3,381,796.57 (10.3%); £3,771,299.35 -> £3,381,796.70 (10.3%); £3,771,299.61 -> £3,381,796.82 (10.3%); £3,771,299.87 -> £3,381,796.93 (10.3%); £3,771,300.13 -> £3,381,797.05 (10.3%); £3,771,300.40 -> £3,381,797.17 (10.3%); £3,771,300.65 -> £3,381,797.28 (10.3%); £3,771,300.90 -> £3,381,797.39 (10.3%); £3,771,301.17 -> £3,381,797.50 (10.3%); £3,771,301.42 -> £3,381,797.61 (10.3%); £3,771,301.68 -> £3,381,797.72 (10.3%); £3,771,301.95 -> £3,381,798.06 (10.3%); £3,771,302.21 -> £3,381,798.38 (10.3%); £3,771,302.46 -> £3,381,798.67 (10.3%); £3,771,302.71 -> £3,381,798.94 (10.3%); £3,771,302.96 -> £3,381,799.21 (10.3%); £3,771,303.21 -> £3,381,799.46 (10.3%); £3,771,303.40 -> £3,381,799.71 (10.3%); £3,771,303.65 -> £3,381,799.96 (10.3%); £3,771,303.90 -> £3,381,800.21 (10.3%); £3,771,304.15 -> £3,381,800.45 (10.3%); £3,771,304.41 -> £3,381,800.69 (10.3%); £3,771,304.66 -> £3,381,800.73 (10.3%); £3,771,304.92 -> £3,381,800.78 (10.3%); £3,771,305.15 -> £3,381,800.82 (10.3%); £3,771,305.37 -> £3,381,800.85 (10.3%); £3,771,305.57 -> £3,381,800.89 (10.3%); £3,771,305.72 -> £3,381,800.93 (10.3%); £3,771,305.88 -> £3,381,800.97 (10.3%); £3,771,306.03 -> £3,381,801.00 (10.3%); £3,771,306.18 -> £3,381,801.04 (10.3%); £3,771,306.34 -> £3,381,801.08 (10.3%); £3,771,306.49 -> £3,381,801.12 (10.3%); £3,771,306.64 -> £3,381,801.15 (10.3%); £3,771,306.79 -> £3,381,801.19 (10.3%); £3,771,306.95 -> £3,381,801.23 (10.3%); £3,771,307.10 -> £3,381,801.27 (10.3%); £3,771,307.25 -> £3,381,801.31 (10.3%); £3,771,307.41 -> £3,381,801.55 (10.3%); £3,771,307.56 -> £3,381,801.80 (10.3%); £3,771,307.72 -> £3,381,802.06 (10.3%); £3,771,307.90 -> £3,381,802.33 (10.3%); £3,771,308.11 -> £3,381,802.62 (10.3%); £3,771,308.33 -> £3,381,802.93 (10.3%); £3,771,308.56 -> £3,381,803.27 (10.3%); £3,771,308.81 -> £3,381,803.62 (10.3%); £3,771,309.06 -> £3,381,803.74 (10.3%); £3,771,309.31 -> £3,381,803.87 (10.3%); £3,771,309.57 -> £3,381,804.00 (10.3%); £3,771,309.82 -> £3,381,804.13 (10.3%); £3,771,310.09 -> £3,381,804.26 (10.3%); £3,771,310.35 -> £3,381,804.38 (10.3%); £3,771,310.60 -> £3,381,804.50 (10.3%); £3,771,310.86 -> £3,381,804.61 (10.3%); £3,771,311.11 -> £3,381,804.73 (10.3%); £3,771,311.37 -> £3,381,804.85 (10.3%); £3,771,311.63 -> £3,381,804.96 (10.3%); £3,771,311.88 -> £3,381,805.07 (10.3%); £3,771,312.12 -> £3,381,805.18 (10.3%); £3,771,312.31 -> £3,381,805.49 (10.3%); £3,771,312.50 -> £3,381,805.81 (10.3%); £3,771,312.75 -> £3,381,806.08 (10.3%); £3,771,312.94 -> £3,381,806.33 (10.3%); £3,771,313.13 -> £3,381,806.59 (10.3%); £3,771,313.39 -> £3,381,806.84 (10.3%); £3,771,313.64 -> £3,381,807.09 (10.3%); £3,771,313.90 -> £3,381,807.34 (10.3%); £3,771,314.15 -> £3,381,807.58 (10.3%); £3,771,314.41 -> £3,381,807.81 (10.3%); £3,771,314.67 -> £3,381,808.05 (10.3%); £3,771,314.92 -> £3,381,808.09 (10.3%); £3,771,315.17 -> £3,381,808.13 (10.3%); £3,771,315.41 -> £3,381,808.17 (10.3%); £3,771,315.62 -> £3,381,808.21 (10.3%); £3,771,315.82 -> £3,381,808.24 (10.3%); £3,771,315.97 -> £3,381,808.28 (10.3%); £3,771,316.12 -> £3,381,808.32 (10.3%); £3,771,316.27 -> £3,381,808.36 (10.3%); £3,771,316.43 -> £3,381,808.39 (10.3%); £3,771,316.57 -> £3,381,808.43 (10.3%); £3,771,316.73 -> £3,381,808.47 (10.3%); £3,771,316.88 -> £3,381,808.51 (10.3%); £3,771,317.03 -> £3,381,808.54 (10.3%); £3,771,317.18 -> £3,381,808.58 (10.3%); £3,771,317.33 -> £3,381,808.62 (10.3%); £3,771,317.48 -> £3,381,808.66 (10.3%); £3,771,317.63 -> £3,381,808.88 (10.3%); £3,771,317.79 -> £3,381,809.09 (10.3%); £3,771,317.95 -> £3,381,809.30 (10.3%); £3,771,318.14 -> £3,381,809.53 (10.3%); £3,771,318.33 -> £3,381,809.78 (10.3%); £3,771,318.55 -> £3,381,810.05 (10.3%); £3,771,318.80 -> £3,381,810.35 (10.3%); £3,771,319.04 -> £3,381,810.65 (10.3%); £3,771,319.30 -> £3,381,810.77 (10.3%); £3,771,319.54 -> £3,381,810.89 (10.3%); £3,771,319.80 -> £3,381,811.02 (10.3%); £3,771,320.05 -> £3,381,811.14 (10.3%); £3,771,320.30 -> £3,381,811.26 (10.3%); £3,771,320.55 -> £3,381,811.38 (10.3%); £3,771,320.82 -> £3,381,811.50 (10.3%); £3,771,321.07 -> £3,381,811.61 (10.3%); £3,771,321.32 -> £3,381,811.72 (10.3%); £3,771,321.58 -> £3,381,811.83 (10.3%); £3,771,321.83 -> £3,381,811.94 (10.3%); £3,771,322.08 -> £3,381,812.05 (10.3%); £3,771,322.32 -> £3,381,812.16 (10.3%); £3,771,322.58 -> £3,381,812.45 (10.3%); £3,771,322.76 -> £3,381,812.74 (10.3%); £3,771,323.02 -> £3,381,813.01 (10.3%); £3,771,323.27 -> £3,381,813.23 (10.3%); £3,771,323.47 -> £3,381,813.47 (10.3%); £3,771,323.71 -> £3,381,813.68 (10.3%); £3,771,323.89 -> £3,381,813.90 (10.3%); £3,771,324.15 -> £3,381,814.12 (10.3%); £3,771,324.40 -> £3,381,814.34 (10.3%); £3,771,324.65 -> £3,381,814.56 (10.3%); £3,771,324.90 -> £3,381,814.77 (10.3%); £3,771,325.15 -> £3,381,814.81 (10.3%); £3,771,325.39 -> £3,381,814.85 (10.3%); £3,771,325.63 -> £3,381,814.89 (10.3%); £3,771,325.84 -> £3,381,814.93 (10.3%); £3,771,326.03 -> £3,381,814.96 (10.3%); £3,771,326.19 -> £3,381,815.00 (10.3%); £3,771,326.34 -> £3,381,815.04 (10.3%); £3,771,326.48 -> £3,381,815.08 (10.3%); £3,771,326.64 -> £3,381,815.11 (10.3%); £3,771,326.78 -> £3,381,815.15 (10.3%); £3,771,326.94 -> £3,381,815.19 (10.3%); £3,771,327.09 -> £3,381,815.23 (10.3%); £3,771,327.24 -> £3,381,815.26 (10.3%); £3,771,327.39 -> £3,381,815.30 (10.3%); £3,771,327.53 -> £3,381,815.34 (10.3%); £3,771,327.69 -> £3,381,815.38 (10.3%); £3,771,327.84 -> £3,381,815.58 (10.3%); £3,771,327.98 -> £3,381,815.78 (10.3%); £3,771,328.15 -> £3,381,815.98 (10.3%); £3,771,328.33 -> £3,381,816.19 (10.3%); £3,771,328.53 -> £3,381,816.43 (10.3%); £3,771,328.74 -> £3,381,816.68 (10.3%); £3,771,328.97 -> £3,381,816.97 (10.3%); £3,771,329.22 -> £3,381,817.25 (10.3%); £3,771,329.48 -> £3,381,817.37 (10.3%); £3,771,329.72 -> £3,381,817.49 (10.3%); £3,771,329.97 -> £3,381,817.61 (10.3%); £3,771,330.23 -> £3,381,817.73 (10.3%); £3,771,330.47 -> £3,381,817.85 (10.3%); £3,771,330.72 -> £3,381,817.97 (10.3%); £3,771,330.96 -> £3,381,818.09 (10.3%); £3,771,331.20 -> £3,381,818.21 (10.3%); £3,771,331.45 -> £3,381,818.32 (10.3%); £3,771,331.70 -> £3,381,818.43 (10.3%); £3,771,331.95 -> £3,381,818.55 (10.3%); £3,771,332.20 -> £3,381,818.66 (10.3%); £3,771,332.45 -> £3,381,818.76 (10.3%); £3,771,332.64 -> £3,381,819.04 (10.3%); £3,771,332.82 -> £3,381,819.30 (10.3%); £3,771,333.01 -> £3,381,819.54 (10.3%); £3,771,333.19 -> £3,381,819.75 (10.3%); £3,771,333.38 -> £3,381,819.96 (10.3%); £3,771,333.56 -> £3,381,820.17 (10.3%); £3,771,333.74 -> £3,381,820.37 (10.3%); £3,771,333.99 -> £3,381,820.57 (10.3%); £3,771,334.24 -> £3,381,820.77 (10.3%); £3,771,334.50 -> £3,381,820.96 (10.3%); £3,771,334.74 -> £3,381,821.15 (10.3%); £3,771,334.99 -> £3,381,821.19 (10.3%); £3,771,335.24 -> £3,381,821.24 (10.3%); £3,771,335.47 -> £3,381,821.28 (10.3%); £3,771,335.68 -> £3,381,821.31 (10.3%); £3,771,335.87 -> £3,381,821.35 (10.3%); £3,771,336.02 -> £3,381,821.39 (10.3%); £3,771,336.17 -> £3,381,821.42 (10.3%); £3,771,336.32 -> £3,381,821.46 (10.3%); £3,771,336.46 -> £3,381,821.50 (10.3%); £3,771,336.61 -> £3,381,821.53 (10.3%); £3,771,336.76 -> £3,381,821.57 (10.3%); £3,771,336.91 -> £3,381,821.61 (10.3%); £3,771,337.05 -> £3,381,821.64 (10.3%); £3,771,337.20 -> £3,381,821.68 (10.3%); £3,771,337.35 -> £3,381,821.72 (10.3%); £3,771,337.50 -> £3,381,821.76 (10.3%); £3,771,337.64 -> £3,381,821.97 (10.3%); £3,771,337.80 -> £3,381,822.19 (10.3%); £3,771,337.96 -> £3,381,822.42 (10.3%); £3,771,338.14 -> £3,381,822.66 (10.3%); £3,771,338.34 -> £3,381,822.91 (10.3%); £3,771,338.55 -> £3,381,823.19 (10.3%); £3,771,338.78 -> £3,381,823.49 (10.3%); £3,771,339.03 -> £3,381,823.79 (10.3%); £3,771,339.26 -> £3,381,823.92 (10.3%); £3,771,339.50 -> £3,381,824.04 (10.3%); £3,771,339.75 -> £3,381,824.16 (10.3%); £3,771,340.00 -> £3,381,824.28 (10.3%); £3,771,340.24 -> £3,381,824.40 (10.3%); £3,771,340.50 -> £3,381,824.52 (10.3%); £3,771,340.74 -> £3,381,824.63 (10.3%); £3,771,340.98 -> £3,381,824.74 (10.3%); £3,771,341.22 -> £3,381,824.85 (10.3%); £3,771,341.46 -> £3,381,824.96 (10.3%); £3,771,341.71 -> £3,381,825.07 (10.3%); £3,771,341.95 -> £3,381,825.18 (10.3%); £3,771,342.19 -> £3,381,825.28 (10.3%); £3,771,342.38 -> £3,381,825.57 (10.3%); £3,771,342.56 -> £3,381,825.85 (10.3%); £3,771,342.75 -> £3,381,826.10 (10.3%); £3,771,342.93 -> £3,381,826.33 (10.3%); £3,771,343.11 -> £3,381,826.56 (10.3%); £3,771,343.29 -> £3,381,826.79 (10.3%); £3,771,343.48 -> £3,381,827.01 (10.3%); £3,771,343.72 -> £3,381,827.22 (10.3%); £3,771,343.97 -> £3,381,827.44 (10.3%); £3,771,344.22 -> £3,381,827.65 (10.3%); £3,771,344.46 -> £3,381,827.86 (10.3%); £3,771,344.71 -> £3,381,827.90 (10.3%); £3,771,344.96 -> £3,381,827.94 (10.3%); £3,771,345.19 -> £3,381,827.98 (10.3%); £3,771,345.40 -> £3,381,828.02 (10.3%); £3,771,345.60 -> £3,381,828.05 (10.3%); £3,771,345.72 -> £3,381,828.09 (10.3%); £3,771,345.85 -> £3,381,828.13 (10.3%); £3,771,345.98 -> £3,381,828.17 (10.3%); £3,771,346.11 -> £3,381,828.20 (10.3%); £3,771,346.24 -> £3,381,828.24 (10.3%); £3,771,346.37 -> £3,381,828.28 (10.3%); £3,771,346.50 -> £3,381,828.31 (10.3%); £3,771,346.63 -> £3,381,828.35 (10.3%); £3,771,346.75 -> £3,381,828.39 (10.3%); £3,771,346.88 -> £3,381,828.42 (10.3%); £3,771,347.01 -> £3,381,828.46 (10.3%); £3,771,347.14 -> £3,381,828.66 (10.3%); £3,771,347.27 -> £3,381,828.87 (10.3%); £3,771,347.41 -> £3,381,829.08 (10.3%); £3,771,347.57 -> £3,381,829.28 (10.3%); £3,771,347.74 -> £3,381,829.51 (10.3%); £3,771,347.92 -> £3,381,829.74 (10.3%); £3,771,348.12 -> £3,381,829.99 (10.3%); £3,771,348.33 -> £3,381,830.25 (10.3%); £3,771,348.54 -> £3,381,830.34 (10.3%); £3,771,348.75 -> £3,381,830.43 (10.3%); £3,771,348.96 -> £3,381,830.52 (10.3%); £3,771,349.17 -> £3,381,830.61 (10.3%); £3,771,349.38 -> £3,381,830.69 (10.3%); £3,771,349.60 -> £3,381,830.77 (10.3%); £3,771,349.81 -> £3,381,830.84 (10.3%); £3,771,350.02 -> £3,381,830.91 (10.3%); £3,771,350.24 -> £3,381,830.98 (10.3%); £3,771,350.45 -> £3,381,831.05 (10.3%); £3,771,350.66 -> £3,381,831.12 (10.3%); £3,771,350.87 -> £3,381,831.19 (10.3%); £3,771,351.09 -> £3,381,831.25 (10.3%); £3,771,351.25 -> £3,381,831.48 (10.3%); £3,771,351.41 -> £3,381,831.70 (10.3%); £3,771,351.57 -> £3,381,831.91 (10.3%); £3,771,351.73 -> £3,381,832.11 (10.3%); £3,771,351.89 -> £3,381,832.32 (10.3%); £3,771,352.04 -> £3,381,832.53 (10.3%); £3,771,352.25 -> £3,381,832.74 (10.3%); £3,771,352.47 -> £3,381,832.93 (10.3%); £3,771,352.69 -> £3,381,833.14 (10.3%); £3,771,352.90 -> £3,381,833.34 (10.3%); £3,771,353.11 -> £3,381,833.54 (10.3%); £3,771,353.32 -> £3,381,833.58 (10.3%); £3,771,353.54 -> £3,381,833.62 (10.3%); £3,771,353.73 -> £3,381,833.66 (10.3%); £3,771,353.91 -> £3,381,833.70 (10.3%); £3,771,354.07 -> £3,381,833.74 (10.3%); £3,771,354.20 -> £3,381,833.78 (10.3%); £3,771,354.33 -> £3,381,833.81 (10.3%); £3,771,354.45 -> £3,381,833.85 (10.3%); £3,771,354.57 -> £3,381,833.89 (10.3%); £3,771,354.70 -> £3,381,833.92 (10.3%); £3,771,354.83 -> £3,381,833.96 (10.3%); £3,771,354.95 -> £3,381,834.00 (10.3%); £3,771,355.08 -> £3,381,834.03 (10.3%); £3,771,355.21 -> £3,381,834.07 (10.3%); £3,771,355.34 -> £3,381,834.10 (10.3%); £3,771,355.46 -> £3,381,834.14 (10.3%); £3,771,355.59 -> £3,381,834.38 (10.3%); £3,771,355.71 -> £3,381,834.63 (10.3%); £3,771,355.86 -> £3,381,834.87 (10.3%); £3,771,356.01 -> £3,381,835.12 (10.3%); £3,771,356.18 -> £3,381,835.36 (10.3%); £3,771,356.37 -> £3,381,835.61 (10.3%); £3,771,356.57 -> £3,381,835.85 (10.3%); £3,771,356.77 -> £3,381,836.10 (10.3%); £3,771,356.99 -> £3,381,836.14 (10.3%); £3,771,357.19 -> £3,381,836.19 (10.3%); £3,771,357.40 -> £3,381,836.24 (10.3%); £3,771,357.62 -> £3,381,836.29 (10.3%); £3,771,357.83 -> £3,381,836.34 (10.3%); £3,771,358.04 -> £3,381,836.38 (10.3%); £3,771,358.25 -> £3,381,836.43 (10.3%); £3,771,358.46 -> £3,381,836.48 (10.3%); £3,771,358.68 -> £3,381,836.52 (10.3%); £3,771,358.88 -> £3,381,836.57 (10.3%); £3,771,359.09 -> £3,381,836.61 (10.3%); £3,771,359.30 -> £3,381,836.66 (10.3%); £3,771,359.51 -> £3,381,836.70 (10.3%); £3,771,359.67 -> £3,381,836.94 (10.3%); £3,771,359.83 -> £3,381,837.17 (10.3%); £3,771,360.00 -> £3,381,837.40 (10.3%); £3,771,360.15 -> £3,381,837.64 (10.3%); £3,771,360.31 -> £3,381,837.88 (10.3%); £3,771,360.48 -> £3,381,838.12 (10.3%); £3,771,360.63 -> £3,381,838.35 (10.3%); £3,771,360.85 -> £3,381,838.58 (10.3%); £3,771,361.07 -> £3,381,838.83 (10.3%); £3,771,361.27 -> £3,381,839.07 (10.3%); £3,771,361.48 -> £3,381,839.31 (10.3%); £3,771,361.69 -> £3,381,839.35 (10.3%); £3,771,361.90 -> £3,381,839.39 (10.3%); £3,771,362.10 -> £3,381,839.42 (10.3%); £3,771,362.28 -> £3,381,839.46 (10.3%); £3,771,362.45 -> £3,381,839.49 (10.3%); £3,771,362.60 -> £3,381,839.53 (10.3%); £3,771,362.74 -> £3,381,839.57 (10.3%); £3,771,362.89 -> £3,381,839.61 (10.3%); £3,771,363.04 -> £3,381,839.64 (10.3%); £3,771,363.18 -> £3,381,839.68 (10.3%); £3,771,363.33 -> £3,381,839.72 (10.3%); £3,771,363.47 -> £3,381,839.75 (10.3%); £3,771,363.62 -> £3,381,839.79 (10.3%); £3,771,363.77 -> £3,381,839.83 (10.3%); £3,771,363.91 -> £3,381,839.87 (10.3%); £3,771,364.05 -> £3,381,839.91 (10.3%); £3,771,364.19 -> £3,381,840.19 (10.3%); £3,771,364.34 -> £3,381,840.48 (10.3%); £3,771,364.50 -> £3,381,840.78 (10.3%); £3,771,364.68 -> £3,381,841.10 (10.3%); £3,771,364.86 -> £3,381,841.43 (10.3%); £3,771,365.07 -> £3,381,841.78 (10.3%); £3,771,365.29 -> £3,381,842.15 (10.3%); £3,771,365.53 -> £3,381,842.54 (10.3%); £3,771,365.77 -> £3,381,842.66 (10.3%); £3,771,366.02 -> £3,381,842.79 (10.3%); £3,771,366.26 -> £3,381,842.92 (10.3%); £3,771,366.51 -> £3,381,843.05 (10.3%); £3,771,366.75 -> £3,381,843.17 (10.3%); £3,771,366.99 -> £3,381,843.30 (10.3%); £3,771,367.23 -> £3,381,843.42 (10.3%); £3,771,367.47 -> £3,381,843.53 (10.3%); £3,771,367.71 -> £3,381,843.65 (10.3%); £3,771,367.96 -> £3,381,843.76 (10.3%); £3,771,368.20 -> £3,381,843.87 (10.3%); £3,771,368.44 -> £3,381,843.98 (10.3%); £3,771,368.68 -> £3,381,844.09 (10.3%); £3,771,368.87 -> £3,381,844.45 (10.3%); £3,771,369.05 -> £3,381,844.79 (10.3%); £3,771,369.24 -> £3,381,845.10 (10.3%); £3,771,369.42 -> £3,381,845.40 (10.3%); £3,771,369.60 -> £3,381,845.69 (10.3%); £3,771,369.78 -> £3,381,845.97 (10.3%); £3,771,369.95 -> £3,381,846.27 (10.3%); £3,771,370.20 -> £3,381,846.55 (10.3%); £3,771,370.43 -> £3,381,846.84 (10.3%); £3,771,370.67 -> £3,381,847.12 (10.3%); £3,771,370.91 -> £3,381,847.40 (10.3%); £3,771,371.16 -> £3,381,847.45 (10.3%); £3,771,371.40 -> £3,381,847.49 (10.3%); £3,771,371.62 -> £3,381,847.53 (10.3%); £3,771,371.83 -> £3,381,847.56 (10.3%); £3,771,372.02 -> £3,381,847.60 (10.3%); £3,771,372.16 -> £3,381,847.64 (10.3%); £3,771,372.31 -> £3,381,847.67 (10.3%); £3,771,372.45 -> £3,381,847.71 (10.3%); £3,771,372.59 -> £3,381,847.75 (10.3%); £3,771,372.73 -> £3,381,847.78 (10.3%); £3,771,372.87 -> £3,381,847.82 (10.3%); £3,771,373.01 -> £3,381,847.86 (10.3%); £3,771,373.15 -> £3,381,847.90 (10.3%); £3,771,373.30 -> £3,381,847.93 (10.3%); £3,771,373.44 -> £3,381,847.97 (10.3%); £3,771,373.59 -> £3,381,848.01 (10.3%); £3,771,373.73 -> £3,381,848.28 (10.3%); £3,771,373.88 -> £3,381,848.54 (10.3%); £3,771,374.04 -> £3,381,848.81 (10.3%); £3,771,374.22 -> £3,381,849.08 (10.3%); £3,771,374.40 -> £3,381,849.37 (10.3%); £3,771,374.62 -> £3,381,849.69 (10.3%); £3,771,374.84 -> £3,381,850.03 (10.3%); £3,771,375.09 -> £3,381,850.38 (10.3%); £3,771,375.33 -> £3,381,850.50 (10.3%); £3,771,375.56 -> £3,381,850.62 (10.3%); £3,771,375.80 -> £3,381,850.74 (10.3%); £3,771,376.04 -> £3,381,850.87 (10.3%); £3,771,376.27 -> £3,381,851.00 (10.3%); £3,771,376.52 -> £3,381,851.12 (10.3%); £3,771,376.75 -> £3,381,851.24 (10.3%); £3,771,376.98 -> £3,381,851.36 (10.3%); £3,771,377.22 -> £3,381,851.47 (10.3%); £3,771,377.46 -> £3,381,851.58 (10.3%); £3,771,377.69 -> £3,381,851.69 (10.3%); £3,771,377.93 -> £3,381,851.80 (10.3%); £3,771,378.17 -> £3,381,851.91 (10.3%); £3,771,378.35 -> £3,381,852.25 (10.3%); £3,771,378.53 -> £3,381,852.58 (10.3%); £3,771,378.72 -> £3,381,852.89 (10.3%); £3,771,378.97 -> £3,381,853.18 (10.3%); £3,771,379.21 -> £3,381,853.46 (10.3%); £3,771,379.46 -> £3,381,853.73 (10.3%); £3,771,379.64 -> £3,381,853.99 (10.3%); £3,771,379.88 -> £3,381,854.25 (10.3%); £3,771,380.12 -> £3,381,854.51 (10.3%); £3,771,380.36 -> £3,381,854.76 (10.3%); £3,771,380.60 -> £3,381,855.00 (10.3%); £3,771,380.85 -> £3,381,855.04 (10.3%); £3,771,381.09 -> £3,381,855.08 (10.3%); £3,771,381.31 -> £3,381,855.12 (10.3%); £3,771,381.51 -> £3,381,855.16 (10.3%); £3,771,381.69 -> £3,381,855.20 (10.3%); £3,771,381.84 -> £3,381,855.23 (10.3%); £3,771,381.98 -> £3,381,855.27 (10.3%); £3,771,382.11 -> £3,381,855.31 (10.3%); £3,771,382.25 -> £3,381,855.35 (10.3%); £3,771,382.39 -> £3,381,855.39 (10.3%); £3,771,382.54 -> £3,381,855.42 (10.3%); £3,771,382.68 -> £3,381,855.46 (10.3%); £3,771,382.82 -> £3,381,855.50 (10.3%); £3,771,382.97 -> £3,381,855.54 (10.3%); £3,771,383.11 -> £3,381,855.58 (10.3%); £3,771,383.25 -> £3,381,855.62 (10.3%); £3,771,383.39 -> £3,381,855.90 (10.3%); £3,771,383.53 -> £3,381,856.18 (10.3%); £3,771,383.68 -> £3,381,856.48 (10.3%); £3,771,383.86 -> £3,381,856.79 (10.3%); £3,771,384.05 -> £3,381,857.11 (10.3%); £3,771,384.25 -> £3,381,857.46 (10.3%); £3,771,384.47 -> £3,381,857.84 (10.3%); £3,771,384.71 -> £3,381,858.23 (10.3%); £3,771,384.95 -> £3,381,858.35 (10.3%); £3,771,385.18 -> £3,381,858.48 (10.3%); £3,771,385.42 -> £3,381,858.60 (10.3%); £3,771,385.66 -> £3,381,858.73 (10.3%); £3,771,385.89 -> £3,381,858.85 (10.3%); £3,771,386.13 -> £3,381,858.97 (10.3%); £3,771,386.37 -> £3,381,859.08 (10.3%); £3,771,386.60 -> £3,381,859.20 (10.3%); £3,771,386.84 -> £3,381,859.31 (10.3%); £3,771,387.08 -> £3,381,859.43 (10.3%); £3,771,387.33 -> £3,381,859.54 (10.3%); £3,771,387.56 -> £3,381,859.64 (10.3%); £3,771,387.80 -> £3,381,859.75 (10.3%); £3,771,387.97 -> £3,381,860.10 (10.3%); £3,771,388.15 -> £3,381,860.45 (10.3%); £3,771,388.39 -> £3,381,860.77 (10.3%); £3,771,388.63 -> £3,381,861.08 (10.3%); £3,771,388.87 -> £3,381,861.37 (10.3%); £3,771,389.10 -> £3,381,861.66 (10.3%); £3,771,389.35 -> £3,381,861.94 (10.3%); £3,771,389.59 -> £3,381,862.23 (10.3%); £3,771,389.83 -> £3,381,862.50 (10.3%); £3,771,390.06 -> £3,381,862.77 (10.3%); £3,771,390.30 -> £3,381,863.02 (10.3%); £3,771,390.53 -> £3,381,863.06 (10.3%); £3,771,390.76 -> £3,381,863.10 (10.3%); £3,771,390.97 -> £3,381,863.14 (10.3%); £3,771,391.17 -> £3,381,863.18 (10.3%); £3,771,391.35 -> £3,381,863.22 (10.3%); £3,771,391.49 -> £3,381,863.26 (10.3%); £3,771,391.63 -> £3,381,863.29 (10.3%); £3,771,391.78 -> £3,381,863.33 (10.3%); £3,771,391.92 -> £3,381,863.37 (10.3%); £3,771,392.06 -> £3,381,863.41 (10.3%); £3,771,392.20 -> £3,381,863.44 (10.3%); £3,771,392.34 -> £3,381,863.48 (10.3%); £3,771,392.48 -> £3,381,863.51 (10.3%); £3,771,392.63 -> £3,381,863.55 (10.3%); £3,771,392.77 -> £3,381,863.59 (10.3%); £3,771,392.92 -> £3,381,863.63 (10.3%); £3,771,393.06 -> £3,381,863.93 (10.3%); £3,771,393.20 -> £3,381,864.24 (10.3%); £3,771,393.36 -> £3,381,864.55 (10.3%); £3,771,393.53 -> £3,381,864.88 (10.3%); £3,771,393.72 -> £3,381,865.23 (10.3%); £3,771,393.93 -> £3,381,865.59 (10.3%); £3,771,394.15 -> £3,381,865.98 (10.3%); £3,771,394.38 -> £3,381,866.38 (10.3%); £3,771,394.61 -> £3,381,866.51 (10.3%); £3,771,394.85 -> £3,381,866.63 (10.3%); £3,771,395.08 -> £3,381,866.76 (10.3%); £3,771,395.31 -> £3,381,866.88 (10.3%); £3,771,395.53 -> £3,381,867.01 (10.3%); £3,771,395.78 -> £3,381,867.13 (10.3%); £3,771,396.02 -> £3,381,867.24 (10.3%); £3,771,396.26 -> £3,381,867.35 (10.3%); £3,771,396.49 -> £3,381,867.47 (10.3%); £3,771,396.73 -> £3,381,867.59 (10.3%); £3,771,396.96 -> £3,381,867.70 (10.3%); £3,771,397.20 -> £3,381,867.81 (10.3%); £3,771,397.44 -> £3,381,867.92 (10.3%); £3,771,397.62 -> £3,381,868.31 (10.3%); £3,771,397.80 -> £3,381,868.68 (10.3%); £3,771,397.97 -> £3,381,869.02 (10.3%); £3,771,398.14 -> £3,381,869.34 (10.3%); £3,771,398.33 -> £3,381,869.66 (10.3%); £3,771,398.50 -> £3,381,869.97 (10.3%); £3,771,398.68 -> £3,381,870.27 (10.3%); £3,771,398.91 -> £3,381,870.57 (10.3%); £3,771,399.14 -> £3,381,870.87 (10.3%); £3,771,399.38 -> £3,381,871.17 (10.3%); £3,771,399.60 -> £3,381,871.47 (10.3%); £3,771,399.84 -> £3,381,871.51 (10.3%); £3,771,400.08 -> £3,381,871.56 (10.3%); £3,771,400.30 -> £3,381,871.60 (10.3%); £3,771,400.51 -> £3,381,871.63 (10.3%); £3,771,400.70 -> £3,381,871.67 (10.3%); £3,771,400.84 -> £3,381,871.71 (10.3%); £3,771,400.98 -> £3,381,871.75 (10.3%); £3,771,401.13 -> £3,381,871.78 (10.3%); £3,771,401.27 -> £3,381,871.82 (10.3%); £3,771,401.41 -> £3,381,871.86 (10.3%); £3,771,401.56 -> £3,381,871.90 (10.3%); £3,771,401.70 -> £3,381,871.93 (10.3%); £3,771,401.85 -> £3,381,871.97 (10.3%); £3,771,401.98 -> £3,381,872.01 (10.3%); £3,771,402.13 -> £3,381,872.05 (10.3%); £3,771,402.28 -> £3,381,872.09 (10.3%); £3,771,402.42 -> £3,381,872.35 (10.3%); £3,771,402.56 -> £3,381,872.62 (10.3%); £3,771,402.72 -> £3,381,872.89 (10.3%); £3,771,402.90 -> £3,381,873.18 (10.3%); £3,771,403.09 -> £3,381,873.49 (10.3%); £3,771,403.29 -> £3,381,873.82 (10.3%); £3,771,403.51 -> £3,381,874.17 (10.3%); £3,771,403.75 -> £3,381,874.53 (10.3%); £3,771,403.98 -> £3,381,874.65 (10.3%); £3,771,404.22 -> £3,381,874.78 (10.3%); £3,771,404.45 -> £3,381,874.90 (10.3%); £3,771,404.69 -> £3,381,875.03 (10.3%); £3,771,404.94 -> £3,381,875.16 (10.3%); £3,771,405.18 -> £3,381,875.28 (10.3%); £3,771,405.42 -> £3,381,875.40 (10.3%); £3,771,405.65 -> £3,381,875.52 (10.3%); £3,771,405.88 -> £3,381,875.64 (10.3%); £3,771,406.12 -> £3,381,875.75 (10.3%); £3,771,406.36 -> £3,381,875.87 (10.3%); £3,771,406.60 -> £3,381,875.98 (10.3%); £3,771,406.84 -> £3,381,876.09 (10.3%); £3,771,407.07 -> £3,381,876.43 (10.3%); £3,771,407.25 -> £3,381,876.76 (10.3%); £3,771,407.42 -> £3,381,877.06 (10.3%); £3,771,407.61 -> £3,381,877.35 (10.3%); £3,771,407.78 -> £3,381,877.63 (10.3%); £3,771,408.03 -> £3,381,877.90 (10.3%); £3,771,408.27 -> £3,381,878.17 (10.3%); £3,771,408.52 -> £3,381,878.44 (10.3%); £3,771,408.76 -> £3,381,878.71 (10.3%); £3,771,409.00 -> £3,381,878.96 (10.3%); £3,771,409.24 -> £3,381,879.21 (10.3%); £3,771,409.49 -> £3,381,879.26 (10.3%); £3,771,409.73 -> £3,381,879.30 (10.3%); £3,771,409.95 -> £3,381,879.34 (10.3%); £3,771,410.15 -> £3,381,879.37 (10.3%); £3,771,410.34 -> £3,381,879.41 (10.3%); £3,771,410.47 -> £3,381,879.45 (10.3%); £3,771,410.60 -> £3,381,879.48 (10.3%); £3,771,410.72 -> £3,381,879.52 (10.3%); £3,771,410.85 -> £3,381,879.56 (10.3%); £3,771,410.98 -> £3,381,879.60 (10.3%); £3,771,411.11 -> £3,381,879.63 (10.3%); £3,771,411.24 -> £3,381,879.67 (10.3%); £3,771,411.37 -> £3,381,879.71 (10.3%); £3,771,411.49 -> £3,381,879.75 (10.3%); £3,771,411.62 -> £3,381,879.78 (10.3%); £3,771,411.75 -> £3,381,879.82 (10.3%); £3,771,411.88 -> £3,381,880.03 (10.3%); £3,771,412.01 -> £3,381,880.23 (10.3%); £3,771,412.15 -> £3,381,880.45 (10.3%); £3,771,412.31 -> £3,381,880.66 (10.3%); £3,771,412.48 -> £3,381,880.89 (10.3%); £3,771,412.67 -> £3,381,881.13 (10.3%); £3,771,412.88 -> £3,381,881.39 (10.3%); £3,771,413.09 -> £3,381,881.66 (10.3%); £3,771,413.30 -> £3,381,881.74 (10.3%); £3,771,413.52 -> £3,381,881.83 (10.3%); £3,771,413.73 -> £3,381,881.92 (10.3%); £3,771,413.94 -> £3,381,882.01 (10.3%); £3,771,414.16 -> £3,381,882.09 (10.3%); £3,771,414.37 -> £3,381,882.17 (10.3%); £3,771,414.58 -> £3,381,882.25 (10.3%); £3,771,414.80 -> £3,381,882.32 (10.3%); £3,771,415.02 -> £3,381,882.39 (10.3%); £3,771,415.23 -> £3,381,882.46 (10.3%); £3,771,415.44 -> £3,381,882.53 (10.3%); £3,771,415.65 -> £3,381,882.59 (10.3%); £3,771,415.87 -> £3,381,882.66 (10.3%); £3,771,416.03 -> £3,381,882.90 (10.3%); £3,771,416.20 -> £3,381,883.13 (10.3%); £3,771,416.36 -> £3,381,883.35 (10.3%); £3,771,416.52 -> £3,381,883.56 (10.3%); £3,771,416.68 -> £3,381,883.77 (10.3%); £3,771,416.85 -> £3,381,883.98 (10.3%); £3,771,417.01 -> £3,381,884.19 (10.3%); £3,771,417.22 -> £3,381,884.39 (10.3%); £3,771,417.44 -> £3,381,884.60 (10.3%); £3,771,417.65 -> £3,381,884.80 (10.3%); £3,771,417.87 -> £3,381,885.01 (10.3%); £3,771,418.08 -> £3,381,885.05 (10.3%); £3,771,418.29 -> £3,381,885.09 (10.3%); £3,771,418.50 -> £3,381,885.12 (10.3%); £3,771,418.68 -> £3,381,885.16 (10.3%); £3,771,418.84 -> £3,381,885.20 (10.3%); £3,771,418.97 -> £3,381,885.24 (10.3%); £3,771,419.10 -> £3,381,885.28 (10.3%); £3,771,419.23 -> £3,381,885.31 (10.3%); £3,771,419.36 -> £3,381,885.35 (10.3%); £3,771,419.49 -> £3,381,885.39 (10.3%); £3,771,419.62 -> £3,381,885.42 (10.3%); £3,771,419.75 -> £3,381,885.46 (10.3%); £3,771,419.87 -> £3,381,885.49 (10.3%); £3,771,420.00 -> £3,381,885.53 (10.3%); £3,771,420.13 -> £3,381,885.56 (10.3%); £3,771,420.26 -> £3,381,885.60 (10.3%); £3,771,420.39 -> £3,381,885.74 (10.3%); £3,771,420.52 -> £3,381,885.88 (10.3%); £3,771,420.66 -> £3,381,886.02 (10.3%); £3,771,420.82 -> £3,381,886.16 (10.3%); £3,771,420.99 -> £3,381,886.31 (10.3%); £3,771,421.18 -> £3,381,886.45 (10.3%); £3,771,421.38 -> £3,381,886.60 (10.3%); £3,771,421.60 -> £3,381,886.75 (10.3%); £3,771,421.82 -> £3,381,886.80 (10.3%); £3,771,422.03 -> £3,381,886.85 (10.3%); £3,771,422.25 -> £3,381,886.90 (10.3%); £3,771,422.46 -> £3,381,886.94 (10.3%); £3,771,422.67 -> £3,381,886.99 (10.3%); £3,771,422.89 -> £3,381,887.04 (10.3%); £3,771,423.10 -> £3,381,887.09 (10.3%); £3,771,423.32 -> £3,381,887.13 (10.3%); £3,771,423.53 -> £3,381,887.18 (10.3%); £3,771,423.74 -> £3,381,887.22 (10.3%); £3,771,423.96 -> £3,381,887.27 (10.3%); £3,771,424.18 -> £3,381,887.31 (10.3%); £3,771,424.40 -> £3,381,887.36 (10.3%); £3,771,424.56 -> £3,381,887.51 (10.3%); £3,771,424.72 -> £3,381,887.65 (10.3%); £3,771,424.88 -> £3,381,887.80 (10.3%); £3,771,425.03 -> £3,381,887.95 (10.3%); £3,771,425.19 -> £3,381,888.10 (10.3%); £3,771,425.36 -> £3,381,888.24 (10.3%); £3,771,425.51 -> £3,381,888.39 (10.3%); £3,771,425.73 -> £3,381,888.53 (10.3%); £3,771,425.94 -> £3,381,888.68 (10.3%); £3,771,426.17 -> £3,381,888.82 (10.3%); £3,771,426.38 -> £3,381,888.95 (10.3%); £3,771,426.59 -> £3,381,888.99 (10.3%); £3,771,426.81 -> £3,381,889.03 (10.3%); £3,771,427.00 -> £3,381,889.07 (10.3%); £3,771,427.18 -> £3,381,889.10 (10.3%); £3,771,427.34 -> £3,381,889.14 (10.3%); £3,771,427.49 -> £3,381,889.18 (10.3%); £3,771,427.64 -> £3,381,889.22 (10.3%); £3,771,427.78 -> £3,381,889.25 (10.3%); £3,771,427.93 -> £3,381,889.29 (10.3%); £3,771,428.07 -> £3,381,889.33 (10.3%); £3,771,428.22 -> £3,381,889.36 (10.3%); £3,771,428.37 -> £3,381,889.40 (10.3%); £3,771,428.52 -> £3,381,889.44 (10.3%); £3,771,428.66 -> £3,381,889.47 (10.3%); £3,771,428.80 -> £3,381,889.51 (10.3%); £3,771,428.95 -> £3,381,889.55 (10.3%); £3,771,429.10 -> £3,381,889.72 (10.3%); £3,771,429.24 -> £3,381,889.89 (10.3%); £3,771,429.40 -> £3,381,890.07 (10.3%); £3,771,429.58 -> £3,381,890.26 (10.3%); £3,771,429.78 -> £3,381,890.47 (10.3%); £3,771,430.00 -> £3,381,890.70 (10.3%); £3,771,430.23 -> £3,381,890.95 (10.3%); £3,771,430.48 -> £3,381,891.22 (10.3%); £3,771,430.73 -> £3,381,891.34 (10.3%); £3,771,430.97 -> £3,381,891.47 (10.3%); £3,771,431.23 -> £3,381,891.60 (10.3%); £3,771,431.46 -> £3,381,891.72 (10.3%); £3,771,431.71 -> £3,381,891.85 (10.3%); £3,771,431.97 -> £3,381,891.97 (10.3%); £3,771,432.21 -> £3,381,892.08 (10.3%); £3,771,432.46 -> £3,381,892.20 (10.3%); £3,771,432.72 -> £3,381,892.32 (10.3%); £3,771,432.96 -> £3,381,892.44 (10.3%); £3,771,433.21 -> £3,381,892.56 (10.3%); £3,771,433.46 -> £3,381,892.67 (10.3%); £3,771,433.71 -> £3,381,892.78 (10.3%); £3,771,433.95 -> £3,381,893.05 (10.3%); £3,771,434.14 -> £3,381,893.28 (10.3%); £3,771,434.32 -> £3,381,893.50 (10.3%); £3,771,434.51 -> £3,381,893.69 (10.3%); £3,771,434.68 -> £3,381,893.87 (10.3%); £3,771,434.87 -> £3,381,894.05 (10.3%); £3,771,435.05 -> £3,381,894.24 (10.3%); £3,771,435.29 -> £3,381,894.41 (10.3%); £3,771,435.53 -> £3,381,894.58 (10.3%); £3,771,435.78 -> £3,381,894.75 (10.3%); £3,771,436.03 -> £3,381,894.92 (10.3%); £3,771,436.27 -> £3,381,894.96 (10.3%); £3,771,436.52 -> £3,381,895.00 (10.3%); £3,771,436.75 -> £3,381,895.04 (10.3%); £3,771,436.96 -> £3,381,895.08 (10.3%); £3,771,437.15 -> £3,381,895.12 (10.3%); £3,771,437.30 -> £3,381,895.15 (10.3%); £3,771,437.45 -> £3,381,895.19 (10.3%); £3,771,437.59 -> £3,381,895.23 (10.3%); £3,771,437.73 -> £3,381,895.27 (10.3%); £3,771,437.89 -> £3,381,895.31 (10.3%); £3,771,438.03 -> £3,381,895.35 (10.3%); £3,771,438.18 -> £3,381,895.39 (10.3%); £3,771,438.33 -> £3,381,895.43 (10.3%); £3,771,438.48 -> £3,381,895.46 (10.3%); £3,771,438.62 -> £3,381,895.50 (10.3%); £3,771,438.77 -> £3,381,895.54 (10.3%); £3,771,438.92 -> £3,381,895.70 (10.3%); £3,771,439.07 -> £3,381,895.85 (10.3%); £3,771,439.24 -> £3,381,896.03 (10.3%); £3,771,439.42 -> £3,381,896.21 (10.3%); £3,771,439.62 -> £3,381,896.41 (10.3%); £3,771,439.83 -> £3,381,896.64 (10.3%); £3,771,440.06 -> £3,381,896.88 (10.3%); £3,771,440.31 -> £3,381,897.13 (10.3%); £3,771,440.56 -> £3,381,897.26 (10.3%); £3,771,440.80 -> £3,381,897.39 (10.3%); £3,771,441.05 -> £3,381,897.52 (10.3%); £3,771,441.29 -> £3,381,897.65 (10.3%); £3,771,441.55 -> £3,381,897.78 (10.3%); £3,771,441.79 -> £3,381,897.90 (10.3%); £3,771,442.04 -> £3,381,898.02 (10.3%); £3,771,442.28 -> £3,381,898.14 (10.3%); £3,771,442.53 -> £3,381,898.25 (10.3%); £3,771,442.77 -> £3,381,898.37 (10.3%); £3,771,443.01 -> £3,381,898.49 (10.3%); £3,771,443.26 -> £3,381,898.60 (10.3%); £3,771,443.51 -> £3,381,898.71 (10.3%); £3,771,443.69 -> £3,381,898.96 (10.3%); £3,771,443.88 -> £3,381,899.20 (10.3%); £3,771,444.14 -> £3,381,899.40 (10.3%); £3,771,444.38 -> £3,381,899.59 (10.3%); £3,771,444.62 -> £3,381,899.77 (10.3%); £3,771,444.87 -> £3,381,899.94 (10.3%); £3,771,445.06 -> £3,381,900.11 (10.3%); £3,771,445.31 -> £3,381,900.27 (10.3%); £3,771,445.56 -> £3,381,900.44 (10.3%); £3,771,445.81 -> £3,381,900.59 (10.3%); £3,771,446.06 -> £3,381,900.74 (10.3%); £3,771,446.31 -> £3,381,900.78 (10.3%); £3,771,446.56 -> £3,381,900.83 (10.3%); £3,771,446.79 -> £3,381,900.87 (10.3%); £3,771,446.99 -> £3,381,900.90 (10.3%); £3,771,447.19 -> £3,381,900.94 (10.3%); £3,771,447.33 -> £3,381,900.98 (10.3%); £3,771,447.48 -> £3,381,901.02 (10.3%); £3,771,447.63 -> £3,381,901.06 (10.3%); £3,771,447.78 -> £3,381,901.10 (10.3%); £3,771,447.93 -> £3,381,901.14 (10.3%); £3,771,448.07 -> £3,381,901.17 (10.3%); £3,771,448.22 -> £3,381,901.21 (10.3%); £3,771,448.37 -> £3,381,901.25 (10.3%); £3,771,448.52 -> £3,381,901.29 (10.3%); £3,771,448.67 -> £3,381,901.33 (10.3%); £3,771,448.82 -> £3,381,901.37 (10.3%); £3,771,448.98 -> £3,381,901.53 (10.3%); £3,771,449.13 -> £3,381,901.69 (10.3%); £3,771,449.30 -> £3,381,901.86 (10.3%); £3,771,449.48 -> £3,381,902.05 (10.3%); £3,771,449.68 -> £3,381,902.26 (10.3%); £3,771,449.89 -> £3,381,902.48 (10.3%); £3,771,450.13 -> £3,381,902.74 (10.3%); £3,771,450.37 -> £3,381,903.00 (10.3%); £3,771,450.63 -> £3,381,903.13 (10.3%); £3,771,450.88 -> £3,381,903.26 (10.3%); £3,771,451.13 -> £3,381,903.39 (10.3%); £3,771,451.38 -> £3,381,903.52 (10.3%); £3,771,451.63 -> £3,381,903.65 (10.3%); £3,771,451.88 -> £3,381,903.77 (10.3%); £3,771,452.13 -> £3,381,903.89 (10.3%); £3,771,452.39 -> £3,381,904.01 (10.3%); £3,771,452.65 -> £3,381,904.13 (10.3%); £3,771,452.90 -> £3,381,904.25 (10.3%); £3,771,453.16 -> £3,381,904.37 (10.3%); £3,771,453.41 -> £3,381,904.49 (10.3%); £3,771,453.66 -> £3,381,904.61 (10.3%); £3,771,453.91 -> £3,381,904.86 (10.3%); £3,771,454.09 -> £3,381,905.10 (10.3%); £3,771,454.28 -> £3,381,905.32 (10.3%); £3,771,454.53 -> £3,381,905.51 (10.3%); £3,771,454.78 -> £3,381,905.70 (10.3%); £3,771,455.04 -> £3,381,905.88 (10.3%); £3,771,455.23 -> £3,381,906.06 (10.3%); £3,771,455.48 -> £3,381,906.24 (10.3%); £3,771,455.74 -> £3,381,906.41 (10.3%); £3,771,455.99 -> £3,381,906.58 (10.3%); £3,771,456.24 -> £3,381,906.74 (10.3%); £3,771,456.49 -> £3,381,906.78 (10.3%); £3,771,456.74 -> £3,381,906.82 (10.3%); £3,771,456.98 -> £3,381,906.86 (10.3%); £3,771,457.19 -> £3,381,906.90 (10.3%); £3,771,457.39 -> £3,381,906.93 (10.3%); £3,771,457.54 -> £3,381,906.97 (10.3%); £3,771,457.69 -> £3,381,907.01 (10.3%); £3,771,457.85 -> £3,381,907.05 (10.3%); £3,771,458.01 -> £3,381,907.09 (10.3%); £3,771,458.16 -> £3,381,907.12 (10.3%); £3,771,458.32 -> £3,381,907.16 (10.3%); £3,771,458.47 -> £3,381,907.20 (10.3%); £3,771,458.63 -> £3,381,907.24 (10.3%); £3,771,458.78 -> £3,381,907.27 (10.3%); £3,771,458.93 -> £3,381,907.31 (10.3%); £3,771,459.09 -> £3,381,907.35 (10.3%); £3,771,459.24 -> £3,381,907.50 (10.3%); £3,771,459.40 -> £3,381,907.65 (10.3%); £3,771,459.56 -> £3,381,907.81 (10.3%); £3,771,459.75 -> £3,381,907.99 (10.3%); £3,771,459.96 -> £3,381,908.19 (10.3%); £3,771,460.17 -> £3,381,908.40 (10.3%); £3,771,460.41 -> £3,381,908.65 (10.3%); £3,771,460.66 -> £3,381,908.91 (10.3%); £3,771,460.92 -> £3,381,909.03 (10.3%); £3,771,461.17 -> £3,381,909.16 (10.3%); £3,771,461.42 -> £3,381,909.29 (10.3%); £3,771,461.68 -> £3,381,909.42 (10.3%); £3,771,461.93 -> £3,381,909.55 (10.3%); £3,771,462.19 -> £3,381,909.67 (10.3%); £3,771,462.45 -> £3,381,909.79 (10.3%); £3,771,462.70 -> £3,381,909.91 (10.3%); £3,771,462.96 -> £3,381,910.03 (10.3%); £3,771,463.22 -> £3,381,910.15 (10.3%); £3,771,463.47 -> £3,381,910.26 (10.3%); £3,771,463.72 -> £3,381,910.37 (10.3%); £3,771,463.98 -> £3,381,910.48 (10.3%); £3,771,464.18 -> £3,381,910.73 (10.3%); £3,771,464.37 -> £3,381,910.95 (10.3%); £3,771,464.55 -> £3,381,911.15 (10.3%); £3,771,464.74 -> £3,381,911.34 (10.3%); £3,771,465.00 -> £3,381,911.51 (10.3%); £3,771,465.25 -> £3,381,911.68 (10.3%); £3,771,465.45 -> £3,381,911.84 (10.3%); £3,771,465.71 -> £3,381,912.00 (10.3%); £3,771,465.97 -> £3,381,912.16 (10.3%); £3,771,466.23 -> £3,381,912.31 (10.3%); £3,771,466.47 -> £3,381,912.46 (10.3%); £3,771,466.73 -> £3,381,912.50 (10.3%); £3,771,466.99 -> £3,381,912.54 (10.3%); £3,771,467.22 -> £3,381,912.58 (10.3%); £3,771,467.44 -> £3,381,912.62 (10.3%); £3,771,467.64 -> £3,381,912.66 (10.3%); £3,771,467.80 -> £3,381,912.69 (10.3%); £3,771,467.95 -> £3,381,912.73 (10.3%); £3,771,468.10 -> £3,381,912.77 (10.3%); £3,771,468.25 -> £3,381,912.81 (10.3%); £3,771,468.40 -> £3,381,912.84 (10.3%); £3,771,468.55 -> £3,381,912.88 (10.3%); £3,771,468.71 -> £3,381,912.92 (10.3%); £3,771,468.86 -> £3,381,912.96 (10.3%); £3,771,469.02 -> £3,381,913.00 (10.3%); £3,771,469.17 -> £3,381,913.04 (10.3%); £3,771,469.32 -> £3,381,913.08 (10.3%); £3,771,469.47 -> £3,381,913.24 (10.3%); £3,771,469.63 -> £3,381,913.41 (10.3%); £3,771,469.80 -> £3,381,913.60 (10.3%); £3,771,469.99 -> £3,381,913.79 (10.3%); £3,771,470.19 -> £3,381,914.01 (10.3%); £3,771,470.41 -> £3,381,914.24 (10.3%); £3,771,470.66 -> £3,381,914.50 (10.3%); £3,771,470.92 -> £3,381,914.77 (10.3%); £3,771,471.19 -> £3,381,914.90 (10.3%); £3,771,471.45 -> £3,381,915.03 (10.3%); £3,771,471.71 -> £3,381,915.17 (10.3%); £3,771,471.96 -> £3,381,915.32 (10.3%); £3,771,472.22 -> £3,381,915.46 (10.3%); £3,771,472.46 -> £3,381,915.60 (10.3%); £3,771,472.72 -> £3,381,915.72 (10.3%); £3,771,472.97 -> £3,381,915.85 (10.3%); £3,771,473.24 -> £3,381,915.98 (10.3%); £3,771,473.50 -> £3,381,916.09 (10.3%); £3,771,473.74 -> £3,381,916.21 (10.3%); £3,771,473.99 -> £3,381,916.32 (10.3%); £3,771,474.25 -> £3,381,916.42 (10.3%); £3,771,474.45 -> £3,381,916.68 (10.3%); £3,771,474.64 -> £3,381,916.93 (10.3%); £3,771,474.83 -> £3,381,917.14 (10.3%); £3,771,475.03 -> £3,381,917.34 (10.3%); £3,771,475.23 -> £3,381,917.53 (10.3%); £3,771,475.42 -> £3,381,917.71 (10.3%); £3,771,475.61 -> £3,381,917.90 (10.3%); £3,771,475.87 -> £3,381,918.08 (10.3%); £3,771,476.13 -> £3,381,918.26 (10.3%); £3,771,476.38 -> £3,381,918.44 (10.3%); £3,771,476.64 -> £3,381,918.61 (10.3%); £3,771,476.89 -> £3,381,918.65 (10.3%); £3,771,477.15 -> £3,381,918.69 (10.3%); £3,771,477.38 -> £3,381,918.73 (10.3%); £3,771,477.59 -> £3,381,918.77 (10.3%); £3,771,477.80 -> £3,381,918.81 (10.3%); £3,771,477.94 -> £3,381,918.85 (10.3%); £3,771,478.08 -> £3,381,918.88 (10.3%); £3,771,478.22 -> £3,381,918.92 (10.3%); £3,771,478.36 -> £3,381,918.96 (10.3%); £3,771,478.50 -> £3,381,919.00 (10.3%); £3,771,478.65 -> £3,381,919.03 (10.3%); £3,771,478.79 -> £3,381,919.07 (10.3%); £3,771,478.93 -> £3,381,919.11 (10.3%); £3,771,479.06 -> £3,381,919.15 (10.3%); £3,771,479.20 -> £3,381,919.19 (10.3%); £3,771,479.33 -> £3,381,919.23 (10.3%); £3,771,479.47 -> £3,381,919.42 (10.3%); £3,771,479.62 -> £3,381,919.60 (10.3%); £3,771,479.77 -> £3,381,919.79 (10.3%); £3,771,479.94 -> £3,381,919.99 (10.3%); £3,771,480.13 -> £3,381,920.20 (10.3%); £3,771,480.33 -> £3,381,920.42 (10.3%); £3,771,480.55 -> £3,381,920.66 (10.3%); £3,771,480.78 -> £3,381,920.91 (10.3%); £3,771,481.01 -> £3,381,921.00 (10.3%); £3,771,481.25 -> £3,381,921.09 (10.3%); £3,771,481.48 -> £3,381,921.18 (10.3%); £3,771,481.71 -> £3,381,921.27 (10.3%); £3,771,481.94 -> £3,381,921.36 (10.3%); £3,771,482.16 -> £3,381,921.44 (10.3%); £3,771,482.40 -> £3,381,921.52 (10.3%); £3,771,482.63 -> £3,381,921.60 (10.3%); £3,771,482.86 -> £3,381,921.68 (10.3%); £3,771,483.10 -> £3,381,921.75 (10.3%); £3,771,483.33 -> £3,381,921.82 (10.3%); £3,771,483.56 -> £3,381,921.89 (10.3%); £3,771,483.78 -> £3,381,921.95 (10.3%); £3,771,483.96 -> £3,381,922.17 (10.3%); £3,771,484.14 -> £3,381,922.38 (10.3%); £3,771,484.31 -> £3,381,922.58 (10.3%); £3,771,484.48 -> £3,381,922.77 (10.3%); £3,771,484.65 -> £3,381,922.97 (10.3%); £3,771,484.89 -> £3,381,923.17 (10.3%); £3,771,485.12 -> £3,381,923.36 (10.3%); £3,771,485.35 -> £3,381,923.55 (10.3%); £3,771,485.58 -> £3,381,923.74 (10.3%); £3,771,485.81 -> £3,381,923.92 (10.3%); £3,771,486.04 -> £3,381,924.12 (10.3%); £3,771,486.27 -> £3,381,924.16 (10.3%); £3,771,486.50 -> £3,381,924.20 (10.3%); £3,771,486.71 -> £3,381,924.24 (10.3%); £3,771,486.90 -> £3,381,924.28 (10.3%); £3,771,487.08 -> £3,381,924.32 (10.3%); £3,771,487.21 -> £3,381,924.36 (10.3%); £3,771,487.36 -> £3,381,924.40 (10.3%); £3,771,487.50 -> £3,381,924.44 (10.3%); £3,771,487.64 -> £3,381,924.47 (10.3%); £3,771,487.78 -> £3,381,924.51 (10.3%); £3,771,487.92 -> £3,381,924.55 (10.3%); £3,771,488.06 -> £3,381,924.58 (10.3%); £3,771,488.21 -> £3,381,924.62 (10.3%); £3,771,488.34 -> £3,381,924.66 (10.3%); £3,771,488.48 -> £3,381,924.69 (10.3%); £3,771,488.61 -> £3,381,924.73 (10.3%); £3,771,488.75 -> £3,381,924.89 (10.3%); £3,771,488.89 -> £3,381,925.05 (10.3%); £3,771,489.05 -> £3,381,925.21 (10.3%); £3,771,489.22 -> £3,381,925.36 (10.3%); £3,771,489.41 -> £3,381,925.52 (10.3%); £3,771,489.62 -> £3,381,925.68 (10.3%); £3,771,489.84 -> £3,381,925.84 (10.3%); £3,771,490.07 -> £3,381,926.01 (10.3%); £3,771,490.30 -> £3,381,926.06 (10.3%); £3,771,490.54 -> £3,381,926.10 (10.3%); £3,771,490.77 -> £3,381,926.16 (10.3%); £3,771,491.01 -> £3,381,926.21 (10.3%); £3,771,491.24 -> £3,381,926.25 (10.3%); £3,771,491.47 -> £3,381,926.30 (10.3%); £3,771,491.69 -> £3,381,926.35 (10.3%); £3,771,491.92 -> £3,381,926.39 (10.3%); £3,771,492.16 -> £3,381,926.44 (10.3%); £3,771,492.39 -> £3,381,926.48 (10.3%); £3,771,492.63 -> £3,381,926.53 (10.3%); £3,771,492.86 -> £3,381,926.57 (10.3%); £3,771,493.08 -> £3,381,926.62 (10.3%); £3,771,493.26 -> £3,381,926.78 (10.3%); £3,771,493.42 -> £3,381,926.94 (10.3%); £3,771,493.60 -> £3,381,927.10 (10.3%); £3,771,493.78 -> £3,381,927.27 (10.3%); £3,771,494.01 -> £3,381,927.44 (10.3%); £3,771,494.24 -> £3,381,927.60 (10.3%); £3,771,494.42 -> £3,381,927.76 (10.3%); £3,771,494.65 -> £3,381,927.92 (10.3%); £3,771,494.89 -> £3,381,928.07 (10.3%); £3,771,495.12 -> £3,381,928.23 (10.3%); £3,771,495.36 -> £3,381,928.38 (10.3%); £3,771,495.60 -> £3,381,928.42 (10.3%); £3,771,495.83 -> £3,381,928.46 (10.3%); £3,771,496.04 -> £3,381,928.50 (10.3%); £3,771,496.24 -> £3,381,928.53 (10.3%); £3,771,496.41 -> £3,381,928.57 (10.3%); £3,771,496.57 -> £3,381,928.60 (10.3%); £3,771,496.73 -> £3,381,928.64 (10.3%); £3,771,496.89 -> £3,381,928.68 (10.3%); £3,771,497.05 -> £3,381,928.71 (10.3%); £3,771,497.21 -> £3,381,928.75 (10.3%); £3,771,497.37 -> £3,381,928.79 (10.3%); £3,771,497.53 -> £3,381,928.83 (10.3%); £3,771,497.69 -> £3,381,928.87 (10.3%); £3,771,497.85 -> £3,381,928.90 (10.3%); £3,771,498.01 -> £3,381,928.94 (10.3%); £3,771,498.18 -> £3,381,928.98 (10.3%); £3,771,498.34 -> £3,381,929.10 (10.3%); £3,771,498.50 -> £3,381,929.23 (10.3%); £3,771,498.68 -> £3,381,929.37 (10.3%); £3,771,498.88 -> £3,381,929.52 (10.3%); £3,771,499.09 -> £3,381,929.69 (10.3%); £3,771,499.33 -> £3,381,929.89 (10.3%); £3,771,499.58 -> £3,381,930.10 (10.3%); £3,771,499.86 -> £3,381,930.33 (10.3%); £3,771,500.12 -> £3,381,930.45 (10.3%); £3,771,500.39 -> £3,381,930.57 (10.3%); £3,771,500.67 -> £3,381,930.70 (10.3%); £3,771,500.93 -> £3,381,930.82 (10.3%); £3,771,501.19 -> £3,381,930.94 (10.3%); £3,771,501.46 -> £3,381,931.06 (10.3%); £3,771,501.71 -> £3,381,931.17 (10.3%); £3,771,501.97 -> £3,381,931.28 (10.3%); £3,771,502.24 -> £3,381,931.40 (10.3%); £3,771,502.50 -> £3,381,931.51 (10.3%); £3,771,502.77 -> £3,381,931.63 (10.3%); £3,771,503.04 -> £3,381,931.74 (10.3%); £3,771,503.31 -> £3,381,931.85 (10.3%); £3,771,503.58 -> £3,381,932.08 (10.3%); £3,771,503.85 -> £3,381,932.29 (10.3%); £3,771,504.12 -> £3,381,932.48 (10.3%); £3,771,504.39 -> £3,381,932.64 (10.3%); £3,771,504.67 -> £3,381,932.79 (10.3%); £3,771,504.93 -> £3,381,932.93 (10.3%); £3,771,505.14 -> £3,381,933.08 (10.3%); £3,771,505.41 -> £3,381,933.22 (10.3%); £3,771,505.68 -> £3,381,933.35 (10.3%); £3,771,505.94 -> £3,381,933.48 (10.3%); £3,771,506.21 -> £3,381,933.61 (10.3%); £3,771,506.47 -> £3,381,933.65 (10.3%); £3,771,506.75 -> £3,381,933.69 (10.3%); £3,771,506.99 -> £3,381,933.73 (10.3%); £3,771,507.22 -> £3,381,933.77 (10.3%); £3,771,507.43 -> £3,381,933.80 (10.3%); £3,771,507.59 -> £3,381,933.84 (10.3%); £3,771,507.75 -> £3,381,933.88 (10.3%); £3,771,507.91 -> £3,381,933.92 (10.3%); £3,771,508.07 -> £3,381,933.95 (10.3%); £3,771,508.22 -> £3,381,933.99 (10.3%); £3,771,508.39 -> £3,381,934.03 (10.3%); £3,771,508.54 -> £3,381,934.07 (10.3%); £3,771,508.70 -> £3,381,934.11 (10.3%); £3,771,508.86 -> £3,381,934.14 (10.3%); £3,771,509.02 -> £3,381,934.18 (10.3%); £3,771,509.18 -> £3,381,934.23 (10.3%); £3,771,509.33 -> £3,381,934.41 (10.3%); £3,771,509.49 -> £3,381,934.61 (10.3%); £3,771,509.67 -> £3,381,934.82 (10.3%); £3,771,509.86 -> £3,381,935.03 (10.3%); £3,771,510.07 -> £3,381,935.27 (10.3%); £3,771,510.30 -> £3,381,935.53 (10.3%); £3,771,510.55 -> £3,381,935.82 (10.3%); £3,771,510.82 -> £3,381,936.12 (10.3%); £3,771,511.09 -> £3,381,936.25 (10.3%); £3,771,511.36 -> £3,381,936.37 (10.3%); £3,771,511.62 -> £3,381,936.50 (10.3%); £3,771,511.89 -> £3,381,936.63 (10.3%); £3,771,512.15 -> £3,381,936.76 (10.3%); £3,771,512.41 -> £3,381,936.88 (10.3%); £3,771,512.68 -> £3,381,936.99 (10.3%); £3,771,512.94 -> £3,381,937.11 (10.3%); £3,771,513.21 -> £3,381,937.23 (10.3%); £3,771,513.49 -> £3,381,937.34 (10.3%); £3,771,513.74 -> £3,381,937.46 (10.3%); £3,771,514.01 -> £3,381,937.57 (10.3%); £3,771,514.28 -> £3,381,937.68 (10.3%); £3,771,514.48 -> £3,381,937.95 (10.3%); £3,771,514.67 -> £3,381,938.22 (10.3%); £3,771,514.94 -> £3,381,938.46 (10.3%); £3,771,515.21 -> £3,381,938.67 (10.3%); £3,771,515.41 -> £3,381,938.88 (10.3%); £3,771,515.61 -> £3,381,939.07 (10.3%); £3,771,515.80 -> £3,381,939.27 (10.3%); £3,771,516.07 -> £3,381,939.46 (10.3%); £3,771,516.33 -> £3,381,939.66 (10.3%); £3,771,516.59 -> £3,381,939.85 (10.3%); £3,771,516.84 -> £3,381,940.03 (10.3%); £3,771,517.10 -> £3,381,940.07 (10.3%); £3,771,517.37 -> £3,381,940.12 (10.3%); £3,771,517.62 -> £3,381,940.16 (10.3%); £3,771,517.83 -> £3,381,940.19 (10.3%); £3,771,518.04 -> £3,381,940.23 (10.3%); £3,771,518.20 -> £3,381,940.27 (10.3%); £3,771,518.36 -> £3,381,940.31 (10.3%); £3,771,518.52 -> £3,381,940.34 (10.3%); £3,771,518.68 -> £3,381,940.38 (10.3%); £3,771,518.84 -> £3,381,940.42 (10.3%); £3,771,519.00 -> £3,381,940.46 (10.3%); £3,771,519.15 -> £3,381,940.50 (10.3%); £3,771,519.32 -> £3,381,940.53 (10.3%); £3,771,519.47 -> £3,381,940.57 (10.3%); £3,771,519.64 -> £3,381,940.61 (10.3%); £3,771,519.79 -> £3,381,940.65 (10.3%); £3,771,519.95 -> £3,381,940.85 (10.3%); £3,771,520.11 -> £3,381,941.06 (10.3%); £3,771,520.28 -> £3,381,941.29 (10.3%); £3,771,520.48 -> £3,381,941.53 (10.3%); £3,771,520.68 -> £3,381,941.79 (10.3%); £3,771,520.91 -> £3,381,942.05 (10.3%); £3,771,521.17 -> £3,381,942.36 (10.3%); £3,771,521.44 -> £3,381,942.66 (10.3%); £3,771,521.70 -> £3,381,942.78 (10.3%); £3,771,521.97 -> £3,381,942.90 (10.3%); £3,771,522.24 -> £3,381,943.03 (10.3%); £3,771,522.50 -> £3,381,943.15 (10.3%); £3,771,522.77 -> £3,381,943.28 (10.3%); £3,771,523.03 -> £3,381,943.41 (10.3%); £3,771,523.29 -> £3,381,943.53 (10.3%); £3,771,523.54 -> £3,381,943.65 (10.3%); £3,771,523.82 -> £3,381,943.77 (10.3%); £3,771,524.08 -> £3,381,943.88 (10.3%); £3,771,524.35 -> £3,381,944.00 (10.3%); £3,771,524.61 -> £3,381,944.11 (10.3%); £3,771,524.88 -> £3,381,944.22 (10.3%); £3,771,525.14 -> £3,381,944.52 (10.3%); £3,771,525.40 -> £3,381,944.79 (10.3%); £3,771,525.61 -> £3,381,945.04 (10.3%); £3,771,525.80 -> £3,381,945.26 (10.3%); £3,771,526.01 -> £3,381,945.48 (10.3%); £3,771,526.28 -> £3,381,945.70 (10.3%); £3,771,526.54 -> £3,381,945.91 (10.3%); £3,771,526.81 -> £3,381,946.12 (10.3%); £3,771,527.07 -> £3,381,946.32 (10.3%); £3,771,527.34 -> £3,381,946.52 (10.3%); £3,771,527.60 -> £3,381,946.72 (10.3%); £3,771,527.87 -> £3,381,946.77 (10.3%); £3,771,528.14 -> £3,381,946.81 (10.3%); £3,771,528.38 -> £3,381,946.85 (10.3%); £3,771,528.60 -> £3,381,946.89 (10.3%); £3,771,528.81 -> £3,381,946.92 (10.3%); £3,771,528.97 -> £3,381,946.96 (10.3%); £3,771,529.13 -> £3,381,947.00 (10.3%); £3,771,529.29 -> £3,381,947.04 (10.3%); £3,771,529.45 -> £3,381,947.08 (10.3%); £3,771,529.60 -> £3,381,947.11 (10.3%); £3,771,529.76 -> £3,381,947.15 (10.3%); £3,771,529.92 -> £3,381,947.19 (10.3%); £3,771,530.08 -> £3,381,947.23 (10.3%); £3,771,530.24 -> £3,381,947.27 (10.3%); £3,771,530.40 -> £3,381,947.31 (10.3%); £3,771,530.56 -> £3,381,947.35 (10.3%); £3,771,530.73 -> £3,381,947.56 (10.3%); £3,771,530.89 -> £3,381,947.77 (10.3%); £3,771,531.06 -> £3,381,947.98 (10.3%); £3,771,531.25 -> £3,381,948.20 (10.3%); £3,771,531.46 -> £3,381,948.44 (10.3%); £3,771,531.68 -> £3,381,948.71 (10.3%); £3,771,531.92 -> £3,381,949.00 (10.3%); £3,771,532.19 -> £3,381,949.31 (10.3%); £3,771,532.45 -> £3,381,949.44 (10.3%); £3,771,532.71 -> £3,381,949.57 (10.3%); £3,771,532.97 -> £3,381,949.70 (10.3%); £3,771,533.24 -> £3,381,949.83 (10.3%); £3,771,533.50 -> £3,381,949.96 (10.3%); £3,771,533.77 -> £3,381,950.08 (10.3%); £3,771,534.03 -> £3,381,950.20 (10.3%); £3,771,534.31 -> £3,381,950.32 (10.3%); £3,771,534.56 -> £3,381,950.44 (10.3%); £3,771,534.83 -> £3,381,950.55 (10.3%); £3,771,535.10 -> £3,381,950.67 (10.3%); £3,771,535.37 -> £3,381,950.78 (10.3%); £3,771,535.64 -> £3,381,950.89 (10.3%); £3,771,535.90 -> £3,381,951.18 (10.3%); £3,771,536.10 -> £3,381,951.44 (10.3%); £3,771,536.30 -> £3,381,951.68 (10.3%); £3,771,536.49 -> £3,381,951.90 (10.3%); £3,771,536.69 -> £3,381,952.12 (10.3%); £3,771,536.89 -> £3,381,952.33 (10.3%); £3,771,537.16 -> £3,381,952.54 (10.3%); £3,771,537.42 -> £3,381,952.74 (10.3%); £3,771,537.68 -> £3,381,952.95 (10.3%); £3,771,537.95 -> £3,381,953.15 (10.3%); £3,771,538.21 -> £3,381,953.34 (10.3%); £3,771,538.47 -> £3,381,953.38 (10.3%); £3,771,538.74 -> £3,381,953.42 (10.3%); £3,771,538.99 -> £3,381,953.46 (10.3%); £3,771,539.21 -> £3,381,953.50 (10.3%); £3,771,539.41 -> £3,381,953.53 (10.3%); £3,771,539.57 -> £3,381,953.57 (10.3%); £3,771,539.73 -> £3,381,953.61 (10.3%); £3,771,539.89 -> £3,381,953.65 (10.3%); £3,771,540.05 -> £3,381,953.69 (10.3%); £3,771,540.20 -> £3,381,953.72 (10.3%); £3,771,540.36 -> £3,381,953.76 (10.3%); £3,771,540.52 -> £3,381,953.80 (10.3%); £3,771,540.68 -> £3,381,953.83 (10.3%); £3,771,540.85 -> £3,381,953.87 (10.3%); £3,771,541.00 -> £3,381,953.91 (10.3%); £3,771,541.16 -> £3,381,953.95 (10.3%); £3,771,541.32 -> £3,381,954.09 (10.3%); £3,771,541.47 -> £3,381,954.23 (10.3%); £3,771,541.65 -> £3,381,954.39 (10.3%); £3,771,541.85 -> £3,381,954.56 (10.3%); £3,771,542.06 -> £3,381,954.75 (10.3%); £3,771,542.29 -> £3,381,954.96 (10.3%); £3,771,542.53 -> £3,381,955.20 (10.3%); £3,771,542.81 -> £3,381,955.44 (10.3%); £3,771,543.08 -> £3,381,955.57 (10.3%); £3,771,543.36 -> £3,381,955.69 (10.3%); £3,771,543.62 -> £3,381,955.82 (10.3%); £3,771,543.89 -> £3,381,955.96 (10.3%); £3,771,544.15 -> £3,381,956.09 (10.3%); £3,771,544.42 -> £3,381,956.21 (10.3%); £3,771,544.68 -> £3,381,956.33 (10.3%); £3,771,544.95 -> £3,381,956.45 (10.3%); £3,771,545.22 -> £3,381,956.57 (10.3%); £3,771,545.47 -> £3,381,956.69 (10.3%); £3,771,545.74 -> £3,381,956.81 (10.3%); £3,771,546.00 -> £3,381,956.92 (10.3%); £3,771,546.28 -> £3,381,957.04 (10.3%); £3,771,546.55 -> £3,381,957.28 (10.3%); £3,771,546.81 -> £3,381,957.50 (10.3%); £3,771,547.08 -> £3,381,957.69 (10.3%); £3,771,547.34 -> £3,381,957.87 (10.3%); £3,771,547.60 -> £3,381,958.03 (10.3%); £3,771,547.87 -> £3,381,958.20 (10.3%); £3,771,548.13 -> £3,381,958.36 (10.3%); £3,771,548.40 -> £3,381,958.51 (10.3%); £3,771,548.67 -> £3,381,958.67 (10.3%); £3,771,548.93 -> £3,381,958.81 (10.3%); £3,771,549.19 -> £3,381,958.96 (10.3%); £3,771,549.46 -> £3,381,959.00 (10.3%); £3,771,549.73 -> £3,381,959.04 (10.3%); £3,771,549.98 -> £3,381,959.08 (10.3%); £3,771,550.21 -> £3,381,959.12 (10.3%); £3,771,550.42 -> £3,381,959.16 (10.3%); £3,771,550.55 -> £3,381,959.20 (10.3%); £3,771,550.69 -> £3,381,959.23 (10.3%); £3,771,550.83 -> £3,381,959.27 (10.3%); £3,771,550.97 -> £3,381,959.31 (10.3%); £3,771,551.11 -> £3,381,959.35 (10.3%); £3,771,551.25 -> £3,381,959.39 (10.3%); £3,771,551.39 -> £3,381,959.43 (10.3%); £3,771,551.53 -> £3,381,959.46 (10.3%); £3,771,551.67 -> £3,381,959.50 (10.3%); £3,771,551.81 -> £3,381,959.54 (10.3%); £3,771,551.95 -> £3,381,959.58 (10.3%); £3,771,552.09 -> £3,381,959.72 (10.3%); £3,771,552.23 -> £3,381,959.87 (10.3%); £3,771,552.39 -> £3,381,960.01 (10.3%); £3,771,552.56 -> £3,381,960.15 (10.3%); £3,771,552.74 -> £3,381,960.31 (10.3%); £3,771,552.94 -> £3,381,960.47 (10.3%); £3,771,553.16 -> £3,381,960.66 (10.3%); £3,771,553.39 -> £3,381,960.86 (10.3%); £3,771,553.62 -> £3,381,960.95 (10.3%); £3,771,553.86 -> £3,381,961.04 (10.3%); £3,771,554.09 -> £3,381,961.13 (10.3%); £3,771,554.32 -> £3,381,961.22 (10.3%); £3,771,554.55 -> £3,381,961.31 (10.3%); £3,771,554.78 -> £3,381,961.39 (10.3%); £3,771,555.02 -> £3,381,961.47 (10.3%); £3,771,555.25 -> £3,381,961.54 (10.3%); £3,771,555.48 -> £3,381,961.61 (10.3%); £3,771,555.71 -> £3,381,961.68 (10.3%); £3,771,555.94 -> £3,381,961.76 (10.3%); £3,771,556.18 -> £3,381,961.82 (10.3%); £3,771,556.41 -> £3,381,961.89 (10.3%); £3,771,556.64 -> £3,381,962.06 (10.3%); £3,771,556.82 -> £3,381,962.23 (10.3%); £3,771,557.06 -> £3,381,962.38 (10.3%); £3,771,557.23 -> £3,381,962.52 (10.3%); £3,771,557.40 -> £3,381,962.66 (10.3%); £3,771,557.58 -> £3,381,962.80 (10.3%); £3,771,557.75 -> £3,381,962.95 (10.3%); £3,771,557.99 -> £3,381,963.10 (10.3%); £3,771,558.22 -> £3,381,963.25 (10.3%); £3,771,558.45 -> £3,381,963.38 (10.3%); £3,771,558.67 -> £3,381,963.52 (10.3%); £3,771,558.90 -> £3,381,963.57 (10.3%); £3,771,559.14 -> £3,381,963.61 (10.3%); £3,771,559.35 -> £3,381,963.65 (10.3%); £3,771,559.54 -> £3,381,963.69 (10.3%); £3,771,559.72 -> £3,381,963.72 (10.3%); £3,771,559.86 -> £3,381,963.76 (10.3%); £3,771,560.00 -> £3,381,963.80 (10.3%); £3,771,560.14 -> £3,381,963.84 (10.3%); £3,771,560.28 -> £3,381,963.88 (10.3%); £3,771,560.42 -> £3,381,963.92 (10.3%); £3,771,560.56 -> £3,381,963.96 (10.3%); £3,771,560.70 -> £3,381,963.99 (10.3%); £3,771,560.84 -> £3,381,964.03 (10.3%); £3,771,560.98 -> £3,381,964.07 (10.3%); £3,771,561.12 -> £3,381,964.11 (10.3%); £3,771,561.26 -> £3,381,964.14 (10.3%); £3,771,561.40 -> £3,381,964.27 (10.3%); £3,771,561.55 -> £3,381,964.40 (10.3%); £3,771,561.71 -> £3,381,964.53 (10.3%); £3,771,561.87 -> £3,381,964.66 (10.3%); £3,771,562.05 -> £3,381,964.80 (10.3%); £3,771,562.25 -> £3,381,964.93 (10.3%); £3,771,562.48 -> £3,381,965.06 (10.3%); £3,771,562.71 -> £3,381,965.20 (10.3%); £3,771,562.94 -> £3,381,965.25 (10.3%); £3,771,563.18 -> £3,381,965.30 (10.3%); £3,771,563.41 -> £3,381,965.35 (10.3%); £3,771,563.65 -> £3,381,965.41 (10.3%); £3,771,563.88 -> £3,381,965.46 (10.3%); £3,771,564.12 -> £3,381,965.51 (10.3%); £3,771,564.36 -> £3,381,965.55 (10.3%); £3,771,564.60 -> £3,381,965.60 (10.3%); £3,771,564.83 -> £3,381,965.64 (10.3%); £3,771,565.07 -> £3,381,965.69 (10.3%); £3,771,565.31 -> £3,381,965.74 (10.3%); £3,771,565.54 -> £3,381,965.78 (10.3%); £3,771,565.78 -> £3,381,965.83 (10.3%); £3,771,566.01 -> £3,381,965.97 (10.3%); £3,771,566.24 -> £3,381,966.10 (10.3%); £3,771,566.41 -> £3,381,966.23 (10.3%); £3,771,566.59 -> £3,381,966.36 (10.3%); £3,771,566.77 -> £3,381,966.50 (10.3%); £3,771,566.94 -> £3,381,966.63 (10.3%); £3,771,567.12 -> £3,381,966.76 (10.3%); £3,771,567.36 -> £3,381,966.89 (10.3%); £3,771,567.59 -> £3,381,967.02 (10.3%); £3,771,567.83 -> £3,381,967.15 (10.3%); £3,771,568.06 -> £3,381,967.29 (10.3%); £3,771,568.29 -> £3,381,967.33 (10.3%); £3,771,568.53 -> £3,381,967.37 (10.3%); £3,771,568.75 -> £3,381,967.41 (10.3%); £3,771,568.95 -> £3,381,967.45 (10.3%); £3,771,569.13 -> £3,381,967.48 (10.3%); £3,771,569.29 -> £3,381,967.52 (10.3%); £3,771,569.45 -> £3,381,967.56 (10.3%); £3,771,569.62 -> £3,381,967.60 (10.3%); £3,771,569.78 -> £3,381,967.64 (10.3%); £3,771,569.94 -> £3,381,967.68 (10.3%); £3,771,570.10 -> £3,381,967.71 (10.3%); £3,771,570.27 -> £3,381,967.75 (10.3%); £3,771,570.43 -> £3,381,967.79 (10.3%); £3,771,570.60 -> £3,381,967.83 (10.3%); £3,771,570.76 -> £3,381,967.87 (10.3%); £3,771,570.92 -> £3,381,967.91 (10.3%); £3,771,571.09 -> £3,381,968.06 (10.3%); £3,771,571.25 -> £3,381,968.20 (10.3%); £3,771,571.43 -> £3,381,968.35 (10.3%); £3,771,571.64 -> £3,381,968.52 (10.3%); £3,771,571.86 -> £3,381,968.70 (10.3%); £3,771,572.10 -> £3,381,968.91 (10.3%); £3,771,572.35 -> £3,381,969.15 (10.3%); £3,771,572.61 -> £3,381,969.41 (10.3%); £3,771,572.89 -> £3,381,969.54 (10.3%); £3,771,573.16 -> £3,381,969.66 (10.3%); £3,771,573.44 -> £3,381,969.79 (10.3%); £3,771,573.71 -> £3,381,969.91 (10.3%); £3,771,573.98 -> £3,381,970.04 (10.3%); £3,771,574.25 -> £3,381,970.16 (10.3%); £3,771,574.52 -> £3,381,970.27 (10.3%); £3,771,574.78 -> £3,381,970.38 (10.3%); £3,771,575.05 -> £3,381,970.50 (10.3%); £3,771,575.31 -> £3,381,970.61 (10.3%); £3,771,575.59 -> £3,381,970.72 (10.3%); £3,771,575.87 -> £3,381,970.83 (10.3%); £3,771,576.13 -> £3,381,970.94 (10.3%); £3,771,576.34 -> £3,381,971.17 (10.3%); £3,771,576.54 -> £3,381,971.39 (10.3%); £3,771,576.74 -> £3,381,971.58 (10.3%); £3,771,576.94 -> £3,381,971.74 (10.3%); £3,771,577.15 -> £3,381,971.91 (10.3%); £3,771,577.43 -> £3,381,972.08 (10.3%); £3,771,577.70 -> £3,381,972.24 (10.3%); £3,771,577.99 -> £3,381,972.39 (10.3%); £3,771,578.26 -> £3,381,972.54 (10.3%); £3,771,578.53 -> £3,381,972.68 (10.3%); £3,771,578.80 -> £3,381,972.82 (10.3%); £3,771,579.07 -> £3,381,972.86 (10.3%); £3,771,579.34 -> £3,381,972.91 (10.3%); £3,771,579.59 -> £3,381,972.95 (10.3%); £3,771,579.82 -> £3,381,972.99 (10.3%); £3,771,580.04 -> £3,381,973.02 (10.3%); £3,771,580.21 -> £3,381,973.06 (10.3%); £3,771,580.37 -> £3,381,973.10 (10.3%); £3,771,580.54 -> £3,381,973.14 (10.3%); £3,771,580.71 -> £3,381,973.18 (10.3%); £3,771,580.88 -> £3,381,973.22 (10.3%); £3,771,581.04 -> £3,381,973.25 (10.3%); £3,771,581.21 -> £3,381,973.29 (10.3%); £3,771,581.37 -> £3,381,973.33 (10.3%); £3,771,581.53 -> £3,381,973.37 (10.3%); £3,771,581.70 -> £3,381,973.41 (10.3%); £3,771,581.87 -> £3,381,973.45 (10.3%); £3,771,582.03 -> £3,381,973.62 (10.3%); £3,771,582.20 -> £3,381,973.78 (10.3%); £3,771,582.39 -> £3,381,973.96 (10.3%); £3,771,582.59 -> £3,381,974.15 (10.3%); £3,771,582.81 -> £3,381,974.36 (10.3%); £3,771,583.04 -> £3,381,974.59 (10.3%); £3,771,583.30 -> £3,381,974.85 (10.3%); £3,771,583.57 -> £3,381,975.11 (10.3%); £3,771,583.84 -> £3,381,975.24 (10.3%); £3,771,584.12 -> £3,381,975.37 (10.3%); £3,771,584.40 -> £3,381,975.49 (10.3%); £3,771,584.68 -> £3,381,975.63 (10.3%); £3,771,584.95 -> £3,381,975.75 (10.3%); £3,771,585.22 -> £3,381,975.88 (10.3%); £3,771,585.49 -> £3,381,976.00 (10.3%); £3,771,585.77 -> £3,381,976.11 (10.3%); £3,771,586.04 -> £3,381,976.23 (10.3%); £3,771,586.32 -> £3,381,976.34 (10.3%); £3,771,586.58 -> £3,381,976.46 (10.3%); £3,771,586.85 -> £3,381,976.57 (10.3%); £3,771,587.12 -> £3,381,976.67 (10.3%); £3,771,587.33 -> £3,381,976.92 (10.3%); £3,771,587.54 -> £3,381,977.15 (10.3%); £3,771,587.74 -> £3,381,977.34 (10.3%); £3,771,587.95 -> £3,381,977.52 (10.3%); £3,771,588.15 -> £3,381,977.69 (10.3%); £3,771,588.36 -> £3,381,977.86 (10.3%); £3,771,588.57 -> £3,381,978.02 (10.3%); £3,771,588.84 -> £3,381,978.18 (10.3%); £3,771,589.11 -> £3,381,978.34 (10.3%); £3,771,589.38 -> £3,381,978.49 (10.3%); £3,771,589.66 -> £3,381,978.64 (10.3%); £3,771,589.94 -> £3,381,978.68 (10.3%); £3,771,590.20 -> £3,381,978.73 (10.3%); £3,771,590.45 -> £3,381,978.77 (10.3%); £3,771,590.69 -> £3,381,978.80 (10.3%); £3,771,590.89 -> £3,381,978.84 (10.3%); £3,771,591.06 -> £3,381,978.88 (10.3%); £3,771,591.23 -> £3,381,978.91 (10.3%); £3,771,591.39 -> £3,381,978.95 (10.3%); £3,771,591.55 -> £3,381,978.99 (10.3%); £3,771,591.72 -> £3,381,979.03 (10.3%); £3,771,591.89 -> £3,381,979.06 (10.3%); £3,771,592.05 -> £3,381,979.10 (10.3%); £3,771,592.22 -> £3,381,979.14 (10.3%); £3,771,592.38 -> £3,381,979.18 (10.3%); £3,771,592.55 -> £3,381,979.22 (10.3%); £3,771,592.71 -> £3,381,979.26 (10.3%); £3,771,592.88 -> £3,381,979.48 (10.3%); £3,771,593.04 -> £3,381,979.72 (10.3%); £3,771,593.23 -> £3,381,979.97 (10.3%); £3,771,593.43 -> £3,381,980.22 (10.3%); £3,771,593.66 -> £3,381,980.50 (10.3%); £3,771,593.90 -> £3,381,980.80 (10.3%); £3,771,594.15 -> £3,381,981.11 (10.3%); £3,771,594.43 -> £3,381,981.44 (10.3%); £3,771,594.72 -> £3,381,981.56 (10.3%); £3,771,595.00 -> £3,381,981.68 (10.3%); £3,771,595.28 -> £3,381,981.81 (10.3%); £3,771,595.56 -> £3,381,981.94 (10.3%); £3,771,595.83 -> £3,381,982.06 (10.3%); £3,771,596.11 -> £3,381,982.19 (10.3%); £3,771,596.38 -> £3,381,982.31 (10.3%); £3,771,596.65 -> £3,381,982.42 (10.3%); £3,771,596.92 -> £3,381,982.54 (10.3%); £3,771,597.21 -> £3,381,982.65 (10.3%); £3,771,597.47 -> £3,381,982.77 (10.3%); £3,771,597.75 -> £3,381,982.88 (10.3%); £3,771,598.03 -> £3,381,982.99 (10.3%); £3,771,598.24 -> £3,381,983.30 (10.3%); £3,771,598.44 -> £3,381,983.60 (10.3%); £3,771,598.72 -> £3,381,983.86 (10.3%); £3,771,598.92 -> £3,381,984.10 (10.3%); £3,771,599.12 -> £3,381,984.34 (10.3%); £3,771,599.33 -> £3,381,984.58 (10.3%); £3,771,599.60 -> £3,381,984.82 (10.3%); £3,771,599.88 -> £3,381,985.06 (10.3%); £3,771,600.14 -> £3,381,985.29 (10.3%); £3,771,600.42 -> £3,381,985.52 (10.3%); £3,771,600.69 -> £3,381,985.73 (10.3%); £3,771,600.97 -> £3,381,985.77 (10.3%); £3,771,601.25 -> £3,381,985.81 (10.3%); £3,771,601.51 -> £3,381,985.85 (10.3%); £3,771,601.75 -> £3,381,985.89 (10.3%); £3,771,601.96 -> £3,381,985.92 (10.3%); £3,771,602.13 -> £3,381,985.96 (10.3%); £3,771,602.29 -> £3,381,986.00 (10.3%); £3,771,602.46 -> £3,381,986.04 (10.3%); £3,771,602.62 -> £3,381,986.07 (10.3%); £3,771,602.79 -> £3,381,986.11 (10.3%); £3,771,602.96 -> £3,381,986.15 (10.3%); £3,771,603.12 -> £3,381,986.18 (10.3%); £3,771,603.29 -> £3,381,986.22 (10.3%); £3,771,603.45 -> £3,381,986.26 (10.3%); £3,771,603.61 -> £3,381,986.30 (10.3%); £3,771,603.77 -> £3,381,986.34 (10.3%); £3,771,603.94 -> £3,381,986.58 (10.3%); £3,771,604.10 -> £3,381,986.82 (10.3%); £3,771,604.29 -> £3,381,987.07 (10.3%); £3,771,604.49 -> £3,381,987.34 (10.3%); £3,771,604.71 -> £3,381,987.64 (10.3%); £3,771,604.95 -> £3,381,987.96 (10.3%); £3,771,605.21 -> £3,381,988.30 (10.3%); £3,771,605.49 -> £3,381,988.64 (10.3%); £3,771,605.76 -> £3,381,988.76 (10.3%); £3,771,606.04 -> £3,381,988.88 (10.3%); £3,771,606.31 -> £3,381,989.01 (10.3%); £3,771,606.59 -> £3,381,989.14 (10.3%); £3,771,606.87 -> £3,381,989.26 (10.3%); £3,771,607.13 -> £3,381,989.39 (10.3%); £3,771,607.41 -> £3,381,989.50 (10.3%); £3,771,607.69 -> £3,381,989.61 (10.3%); £3,771,607.96 -> £3,381,989.72 (10.3%); £3,771,608.23 -> £3,381,989.84 (10.3%); £3,771,608.51 -> £3,381,989.95 (10.3%); £3,771,608.78 -> £3,381,990.06 (10.3%); £3,771,609.05 -> £3,381,990.17 (10.3%); £3,771,609.25 -> £3,381,990.50 (10.3%); £3,771,609.54 -> £3,381,990.81 (10.3%); £3,771,609.74 -> £3,381,991.10 (10.3%); £3,771,610.01 -> £3,381,991.37 (10.3%); £3,771,610.28 -> £3,381,991.63 (10.3%); £3,771,610.55 -> £3,381,991.88 (10.3%); £3,771,610.82 -> £3,381,992.14 (10.3%); £3,771,611.10 -> £3,381,992.38 (10.3%); £3,771,611.38 -> £3,381,992.62 (10.3%); £3,771,611.66 -> £3,381,992.85 (10.3%); £3,771,611.93 -> £3,381,993.09 (10.3%); £3,771,612.22 -> £3,381,993.13 (10.3%); £3,771,612.49 -> £3,381,993.17 (10.3%); £3,771,612.74 -> £3,381,993.21 (10.3%); £3,771,612.98 -> £3,381,993.25 (10.3%); £3,771,613.19 -> £3,381,993.29 (10.3%); £3,771,613.36 -> £3,381,993.32 (10.3%); £3,771,613.52 -> £3,381,993.36 (10.3%); £3,771,613.69 -> £3,381,993.40 (10.3%); £3,771,613.85 -> £3,381,993.43 (10.3%); £3,771,614.01 -> £3,381,993.47 (10.3%); £3,771,614.18 -> £3,381,993.51 (10.3%); £3,771,614.34 -> £3,381,993.54 (10.3%); £3,771,614.50 -> £3,381,993.58 (10.3%); £3,771,614.67 -> £3,381,993.62 (10.3%); £3,771,614.83 -> £3,381,993.66 (10.3%); £3,771,614.99 -> £3,381,993.70 (10.3%); £3,771,615.17 -> £3,381,993.89 (10.3%); £3,771,615.33 -> £3,381,994.09 (10.3%); £3,771,615.51 -> £3,381,994.29 (10.3%); £3,771,615.71 -> £3,381,994.51 (10.3%); £3,771,615.93 -> £3,381,994.75 (10.3%); £3,771,616.15 -> £3,381,995.01 (10.3%); £3,771,616.41 -> £3,381,995.30 (10.3%); £3,771,616.68 -> £3,381,995.60 (10.3%); £3,771,616.95 -> £3,381,995.73 (10.3%); £3,771,617.23 -> £3,381,995.87 (10.3%); £3,771,617.49 -> £3,381,996.00 (10.3%); £3,771,617.77 -> £3,381,996.14 (10.3%); £3,771,618.03 -> £3,381,996.28 (10.3%); £3,771,618.29 -> £3,381,996.41 (10.3%); £3,771,618.56 -> £3,381,996.54 (10.3%); £3,771,618.82 -> £3,381,996.67 (10.3%); £3,771,619.10 -> £3,381,996.78 (10.3%); £3,771,619.39 -> £3,381,996.90 (10.3%); £3,771,619.65 -> £3,381,997.02 (10.3%); £3,771,619.93 -> £3,381,997.13 (10.3%); £3,771,620.19 -> £3,381,997.24 (10.3%); £3,771,620.46 -> £3,381,997.53 (10.3%); £3,771,620.73 -> £3,381,997.81 (10.3%); £3,771,621.01 -> £3,381,998.05 (10.3%); £3,771,621.29 -> £3,381,998.27 (10.3%); £3,771,621.56 -> £3,381,998.47 (10.3%); £3,771,621.76 -> £3,381,998.68 (10.3%); £3,771,621.97 -> £3,381,998.88 (10.3%); £3,771,622.24 -> £3,381,999.07 (10.3%); £3,771,622.51 -> £3,381,999.27 (10.3%); £3,771,622.77 -> £3,381,999.47 (10.3%); £3,771,623.04 -> £3,381,999.65 (10.3%); £3,771,623.32 -> £3,381,999.69 (10.3%); £3,771,623.58 -> £3,381,999.73 (10.3%); £3,771,623.83 -> £3,381,999.77 (10.3%); £3,771,624.07 -> £3,381,999.81 (10.3%); £3,771,624.28 -> £3,381,999.85 (10.3%); £3,771,624.43 -> £3,381,999.88 (10.3%); £3,771,624.57 -> £3,381,999.92 (10.3%); £3,771,624.72 -> £3,381,999.96 (10.3%); £3,771,624.86 -> £3,382,000.00 (10.3%); £3,771,625.00 -> £3,382,000.03 (10.3%); £3,771,625.14 -> £3,382,000.07 (10.3%); £3,771,625.28 -> £3,382,000.10 (10.3%); £3,771,625.42 -> £3,382,000.14 (10.3%); £3,771,625.56 -> £3,382,000.18 (10.3%); £3,771,625.71 -> £3,382,000.21 (10.3%); £3,771,625.85 -> £3,382,000.25 (10.3%); £3,771,625.99 -> £3,382,000.43 (10.3%); £3,771,626.14 -> £3,382,000.61 (10.3%); £3,771,626.30 -> £3,382,000.79 (10.3%); £3,771,626.48 -> £3,382,000.98 (10.3%); £3,771,626.67 -> £3,382,001.18 (10.3%); £3,771,626.88 -> £3,382,001.40 (10.3%); £3,771,627.10 -> £3,382,001.64 (10.3%); £3,771,627.33 -> £3,382,001.89 (10.3%); £3,771,627.57 -> £3,382,001.98 (10.3%); £3,771,627.81 -> £3,382,002.07 (10.3%); £3,771,628.05 -> £3,382,002.16 (10.3%); £3,771,628.30 -> £3,382,002.25 (10.3%); £3,771,628.53 -> £3,382,002.34 (10.3%); £3,771,628.76 -> £3,382,002.42 (10.3%); £3,771,629.00 -> £3,382,002.49 (10.3%); £3,771,629.24 -> £3,382,002.56 (10.3%); £3,771,629.48 -> £3,382,002.64 (10.3%); £3,771,629.72 -> £3,382,002.70 (10.3%); £3,771,629.96 -> £3,382,002.77 (10.3%); £3,771,630.19 -> £3,382,002.84 (10.3%); £3,771,630.44 -> £3,382,002.91 (10.3%); £3,771,630.68 -> £3,382,003.13 (10.3%); £3,771,630.91 -> £3,382,003.35 (10.3%); £3,771,631.15 -> £3,382,003.54 (10.3%); £3,771,631.33 -> £3,382,003.73 (10.3%); £3,771,631.56 -> £3,382,003.92 (10.3%); £3,771,631.74 -> £3,382,004.10 (10.3%); £3,771,631.92 -> £3,382,004.29 (10.3%); £3,771,632.17 -> £3,382,004.48 (10.3%); £3,771,632.41 -> £3,382,004.67 (10.3%); £3,771,632.65 -> £3,382,004.86 (10.3%); £3,771,632.89 -> £3,382,005.04 (10.3%); £3,771,633.13 -> £3,382,005.08 (10.3%); £3,771,633.37 -> £3,382,005.12 (10.3%); £3,771,633.59 -> £3,382,005.16 (10.3%); £3,771,633.80 -> £3,382,005.20 (10.3%); £3,771,633.99 -> £3,382,005.24 (10.3%); £3,771,634.13 -> £3,382,005.27 (10.3%); £3,771,634.27 -> £3,382,005.31 (10.3%); £3,771,634.40 -> £3,382,005.35 (10.3%); £3,771,634.54 -> £3,382,005.39 (10.3%); £3,771,634.68 -> £3,382,005.42 (10.3%); £3,771,634.83 -> £3,382,005.46 (10.3%); £3,771,634.97 -> £3,382,005.50 (10.3%); £3,771,635.11 -> £3,382,005.53 (10.3%); £3,771,635.25 -> £3,382,005.57 (10.3%); £3,771,635.39 -> £3,382,005.60 (10.3%); £3,771,635.53 -> £3,382,005.64 (10.3%); £3,771,635.67 -> £3,382,005.83 (10.3%); £3,771,635.80 -> £3,382,006.02 (10.3%); £3,771,635.96 -> £3,382,006.20 (10.3%); £3,771,636.12 -> £3,382,006.39 (10.3%); £3,771,636.31 -> £3,382,006.58 (10.3%); £3,771,636.52 -> £3,382,006.77 (10.3%); £3,771,636.74 -> £3,382,006.97 (10.3%); £3,771,636.98 -> £3,382,007.17 (10.3%); £3,771,637.21 -> £3,382,007.22 (10.3%); £3,771,637.45 -> £3,382,007.26 (10.3%); £3,771,637.68 -> £3,382,007.31 (10.3%); £3,771,637.91 -> £3,382,007.36 (10.3%); £3,771,638.15 -> £3,382,007.41 (10.3%); £3,771,638.39 -> £3,382,007.46 (10.3%); £3,771,638.62 -> £3,382,007.51 (10.3%); £3,771,638.86 -> £3,382,007.55 (10.3%); £3,771,639.09 -> £3,382,007.60 (10.3%); £3,771,639.33 -> £3,382,007.65 (10.3%); £3,771,639.56 -> £3,382,007.69 (10.3%); £3,771,639.79 -> £3,382,007.74 (10.3%); £3,771,640.02 -> £3,382,007.79 (10.3%); £3,771,640.26 -> £3,382,007.98 (10.3%); £3,771,640.49 -> £3,382,008.17 (10.3%); £3,771,640.67 -> £3,382,008.36 (10.3%); £3,771,640.84 -> £3,382,008.55 (10.3%); £3,771,641.02 -> £3,382,008.73 (10.3%); £3,771,641.20 -> £3,382,008.92 (10.3%); £3,771,641.38 -> £3,382,009.12 (10.3%); £3,771,641.61 -> £3,382,009.31 (10.3%); £3,771,641.84 -> £3,382,009.50 (10.3%); £3,771,642.07 -> £3,382,009.69 (10.3%); £3,771,642.31 -> £3,382,009.87 (10.3%); £3,771,642.54 -> £3,382,009.91 (10.3%); £3,771,642.78 -> £3,382,009.94 (10.3%); £3,771,643.00 -> £3,382,009.98 (10.3%); £3,771,643.20 -> £3,382,010.02 (10.3%); £3,771,643.38 -> £3,382,010.05 (10.3%); £3,771,643.54 -> £3,382,010.09 (10.3%); £3,771,643.69 -> £3,382,010.13 (10.3%); £3,771,643.85 -> £3,382,010.17 (10.3%); £3,771,644.00 -> £3,382,010.20 (10.3%); £3,771,644.16 -> £3,382,010.24 (10.3%); £3,771,644.31 -> £3,382,010.28 (10.3%); £3,771,644.47 -> £3,382,010.31 (10.3%); £3,771,644.63 -> £3,382,010.35 (10.3%); £3,771,644.78 -> £3,382,010.39 (10.3%); £3,771,644.93 -> £3,382,010.43 (10.3%); £3,771,645.09 -> £3,382,010.47 (10.3%); £3,771,645.24 -> £3,382,010.68 (10.3%); £3,771,645.40 -> £3,382,010.90 (10.3%); £3,771,645.57 -> £3,382,011.13 (10.3%); £3,771,645.76 -> £3,382,011.36 (10.3%); £3,771,645.98 -> £3,382,011.61 (10.3%); £3,771,646.20 -> £3,382,011.90 (10.3%); £3,771,646.44 -> £3,382,012.21 (10.3%); £3,771,646.70 -> £3,382,012.53 (10.3%); £3,771,646.96 -> £3,382,012.66 (10.3%); £3,771,647.21 -> £3,382,012.78 (10.3%); £3,771,647.47 -> £3,382,012.91 (10.3%); £3,771,647.73 -> £3,382,013.04 (10.3%); £3,771,647.99 -> £3,382,013.17 (10.3%); £3,771,648.25 -> £3,382,013.30 (10.3%); £3,771,648.51 -> £3,382,013.41 (10.3%); £3,771,648.77 -> £3,382,013.53 (10.3%); £3,771,649.03 -> £3,382,013.65 (10.3%); £3,771,649.29 -> £3,382,013.77 (10.3%); £3,771,649.54 -> £3,382,013.88 (10.3%); £3,771,649.81 -> £3,382,014.00 (10.3%); £3,771,650.07 -> £3,382,014.10 (10.3%); £3,771,650.27 -> £3,382,014.40 (10.3%); £3,771,650.46 -> £3,382,014.68 (10.3%); £3,771,650.65 -> £3,382,014.93 (10.3%); £3,771,650.84 -> £3,382,015.16 (10.3%); £3,771,651.04 -> £3,382,015.38 (10.3%); £3,771,651.23 -> £3,382,015.60 (10.3%); £3,771,651.42 -> £3,382,015.81 (10.3%); £3,771,651.69 -> £3,382,016.02 (10.3%); £3,771,651.94 -> £3,382,016.24 (10.3%); £3,771,652.20 -> £3,382,016.44 (10.3%); £3,771,652.46 -> £3,382,016.65 (10.3%); £3,771,652.72 -> £3,382,016.69 (10.3%); £3,771,652.98 -> £3,382,016.73 (10.3%); £3,771,653.22 -> £3,382,016.77 (10.3%); £3,771,653.44 -> £3,382,016.81 (10.3%); £3,771,653.64 -> £3,382,016.84 (10.3%); £3,771,653.80 -> £3,382,016.88 (10.3%); £3,771,653.96 -> £3,382,016.92 (10.3%); £3,771,654.12 -> £3,382,016.96 (10.3%); £3,771,654.28 -> £3,382,016.99 (10.3%); £3,771,654.43 -> £3,382,017.03 (10.3%); £3,771,654.59 -> £3,382,017.06 (10.3%); £3,771,654.74 -> £3,382,017.10 (10.3%); £3,771,654.89 -> £3,382,017.14 (10.3%); £3,771,655.05 -> £3,382,017.18 (10.3%); £3,771,655.21 -> £3,382,017.22 (10.3%); £3,771,655.36 -> £3,382,017.26 (10.3%); £3,771,655.52 -> £3,382,017.44 (10.3%); £3,771,655.68 -> £3,382,017.62 (10.3%); £3,771,655.85 -> £3,382,017.82 (10.3%); £3,771,656.04 -> £3,382,018.03 (10.3%); £3,771,656.26 -> £3,382,018.26 (10.3%); £3,771,656.49 -> £3,382,018.51 (10.3%); £3,771,656.72 -> £3,382,018.79 (10.3%); £3,771,656.98 -> £3,382,019.08 (10.3%); £3,771,657.24 -> £3,382,019.20 (10.3%); £3,771,657.49 -> £3,382,019.33 (10.3%); £3,771,657.75 -> £3,382,019.46 (10.3%); £3,771,658.01 -> £3,382,019.59 (10.3%); £3,771,658.27 -> £3,382,019.71 (10.3%); £3,771,658.53 -> £3,382,019.84 (10.3%); £3,771,658.79 -> £3,382,019.96 (10.3%); £3,771,659.06 -> £3,382,020.08 (10.3%); £3,771,659.32 -> £3,382,020.19 (10.3%); £3,771,659.58 -> £3,382,020.31 (10.3%); £3,771,659.84 -> £3,382,020.43 (10.3%); £3,771,660.09 -> £3,382,020.54 (10.3%); £3,771,660.35 -> £3,382,020.65 (10.3%); £3,771,660.60 -> £3,382,020.94 (10.3%); £3,771,660.87 -> £3,382,021.20 (10.3%); £3,771,661.12 -> £3,382,021.44 (10.3%); £3,771,661.39 -> £3,382,021.65 (10.3%); £3,771,661.64 -> £3,382,021.86 (10.3%); £3,771,661.89 -> £3,382,022.06 (10.3%); £3,771,662.15 -> £3,382,022.26 (10.3%); £3,771,662.41 -> £3,382,022.45 (10.3%); £3,771,662.67 -> £3,382,022.64 (10.3%); £3,771,662.93 -> £3,382,022.83 (10.3%); £3,771,663.19 -> £3,382,023.00 (10.3%); £3,771,663.46 -> £3,382,023.04 (10.3%); £3,771,663.72 -> £3,382,023.08 (10.3%); £3,771,663.96 -> £3,382,023.12 (10.3%); £3,771,664.18 -> £3,382,023.16 (10.3%); £3,771,664.38 -> £3,382,023.19 (10.3%); £3,771,664.54 -> £3,382,023.23 (10.3%); £3,771,664.69 -> £3,382,023.27 (10.3%); £3,771,664.85 -> £3,382,023.31 (10.3%); £3,771,665.00 -> £3,382,023.34 (10.3%); £3,771,665.15 -> £3,382,023.38 (10.3%); £3,771,665.30 -> £3,382,023.42 (10.3%); £3,771,665.46 -> £3,382,023.46 (10.3%); £3,771,665.61 -> £3,382,023.49 (10.3%); £3,771,665.77 -> £3,382,023.53 (10.3%); £3,771,665.93 -> £3,382,023.57 (10.3%); £3,771,666.08 -> £3,382,023.61 (10.3%); £3,771,666.24 -> £3,382,023.73 (10.3%); £3,771,666.40 -> £3,382,023.86 (10.3%); £3,771,666.58 -> £3,382,024.00 (10.3%); £3,771,666.77 -> £3,382,024.15 (10.3%); £3,771,666.98 -> £3,382,024.32 (10.3%); £3,771,667.20 -> £3,382,024.52 (10.3%); £3,771,667.44 -> £3,382,024.73 (10.3%); £3,771,667.70 -> £3,382,024.96 (10.3%); £3,771,667.96 -> £3,382,025.09 (10.3%); £3,771,668.22 -> £3,382,025.22 (10.3%); £3,771,668.48 -> £3,382,025.35 (10.3%); £3,771,668.74 -> £3,382,025.48 (10.3%); £3,771,669.00 -> £3,382,025.61 (10.3%); £3,771,669.24 -> £3,382,025.73 (10.3%); £3,771,669.49 -> £3,382,025.84 (10.3%); £3,771,669.76 -> £3,382,025.96 (10.3%); £3,771,670.02 -> £3,382,026.08 (10.3%); £3,771,670.28 -> £3,382,026.19 (10.3%); £3,771,670.54 -> £3,382,026.31 (10.3%); £3,771,670.80 -> £3,382,026.42 (10.3%); £3,771,671.07 -> £3,382,026.53 (10.3%); £3,771,671.32 -> £3,382,026.75 (10.3%); £3,771,671.51 -> £3,382,026.95 (10.3%); £3,771,671.71 -> £3,382,027.12 (10.3%); £3,771,671.90 -> £3,382,027.28 (10.3%); £3,771,672.16 -> £3,382,027.42 (10.3%); £3,771,672.41 -> £3,382,027.57 (10.3%); £3,771,672.66 -> £3,382,027.71 (10.3%); £3,771,672.93 -> £3,382,027.85 (10.3%); £3,771,673.20 -> £3,382,027.99 (10.3%); £3,771,673.46 -> £3,382,028.11 (10.3%); £3,771,673.72 -> £3,382,028.24 (10.3%); £3,771,673.97 -> £3,382,028.28 (10.3%); £3,771,674.23 -> £3,382,028.32 (10.3%); £3,771,674.47 -> £3,382,028.36 (10.3%); £3,771,674.69 -> £3,382,028.40 (10.3%); £3,771,674.89 -> £3,382,028.44 (10.3%); £3,771,675.05 -> £3,382,028.47 (10.3%); £3,771,675.20 -> £3,382,028.51 (10.3%); £3,771,675.36 -> £3,382,028.55 (10.3%); £3,771,675.51 -> £3,382,028.59 (10.3%); £3,771,675.67 -> £3,382,028.62 (10.3%); £3,771,675.82 -> £3,382,028.66 (10.3%); £3,771,675.98 -> £3,382,028.70 (10.3%); £3,771,676.15 -> £3,382,028.74 (10.3%); £3,771,676.31 -> £3,382,028.78 (10.3%); £3,771,676.47 -> £3,382,028.81 (10.3%); £3,771,676.62 -> £3,382,028.85 (10.3%); £3,771,676.78 -> £3,382,028.95 (10.3%); £3,771,676.93 -> £3,382,029.05 (10.3%); £3,771,677.10 -> £3,382,029.16 (10.3%); £3,771,677.29 -> £3,382,029.29 (10.3%); £3,771,677.51 -> £3,382,029.44 (10.3%); £3,771,677.73 -> £3,382,029.61 (10.3%); £3,771,677.98 -> £3,382,029.80 (10.3%); £3,771,678.24 -> £3,382,030.01 (10.3%); £3,771,678.51 -> £3,382,030.13 (10.3%); £3,771,678.77 -> £3,382,030.26 (10.3%); £3,771,679.04 -> £3,382,030.39 (10.3%); £3,771,679.30 -> £3,382,030.52 (10.3%); £3,771,679.56 -> £3,382,030.65 (10.3%); £3,771,679.82 -> £3,382,030.78 (10.3%); £3,771,680.08 -> £3,382,030.90 (10.3%); £3,771,680.35 -> £3,382,031.01 (10.3%); £3,771,680.61 -> £3,382,031.13 (10.3%); £3,771,680.86 -> £3,382,031.25 (10.3%); £3,771,681.11 -> £3,382,031.36 (10.3%); £3,771,681.38 -> £3,382,031.47 (10.3%); £3,771,681.64 -> £3,382,031.58 (10.3%); £3,771,681.89 -> £3,382,031.78 (10.3%); £3,771,682.16 -> £3,382,031.97 (10.3%); £3,771,682.42 -> £3,382,032.12 (10.3%); £3,771,682.67 -> £3,382,032.26 (10.3%); £3,771,682.94 -> £3,382,032.38 (10.3%); £3,771,683.20 -> £3,382,032.50 (10.3%); £3,771,683.47 -> £3,382,032.62 (10.3%); £3,771,683.72 -> £3,382,032.74 (10.3%); £3,771,683.98 -> £3,382,032.85 (10.3%); £3,771,684.23 -> £3,382,032.95 (10.3%); £3,771,684.49 -> £3,382,033.05 (10.3%); £3,771,684.74 -> £3,382,033.09 (10.3%); £3,771,685.00 -> £3,382,033.13 (10.3%); £3,771,685.24 -> £3,382,033.17 (10.3%); £3,771,685.46 -> £3,382,033.21 (10.3%); £3,771,685.67 -> £3,382,033.24 (10.3%); £3,771,685.82 -> £3,382,033.28 (10.3%); £3,771,685.98 -> £3,382,033.32 (10.3%); £3,771,686.13 -> £3,382,033.35 (10.3%); £3,771,686.29 -> £3,382,033.39 (10.3%); £3,771,686.45 -> £3,382,033.43 (10.3%); £3,771,686.61 -> £3,382,033.47 (10.3%); £3,771,686.77 -> £3,382,033.50 (10.3%); £3,771,686.92 -> £3,382,033.54 (10.3%); £3,771,687.08 -> £3,382,033.58 (10.3%); £3,771,687.25 -> £3,382,033.62 (10.3%); £3,771,687.40 -> £3,382,033.66 (10.3%); £3,771,687.56 -> £3,382,033.80 (10.3%); £3,771,687.72 -> £3,382,033.94 (10.3%); £3,771,687.90 -> £3,382,034.09 (10.3%); £3,771,688.09 -> £3,382,034.26 (10.3%); £3,771,688.31 -> £3,382,034.45 (10.3%); £3,771,688.53 -> £3,382,034.65 (10.3%); £3,771,688.78 -> £3,382,034.88 (10.3%); £3,771,689.05 -> £3,382,035.11 (10.3%); £3,771,689.31 -> £3,382,035.24 (10.3%); £3,771,689.58 -> £3,382,035.37 (10.3%); £3,771,689.83 -> £3,382,035.50 (10.3%); £3,771,690.08 -> £3,382,035.63 (10.3%); £3,771,690.35 -> £3,382,035.75 (10.3%); £3,771,690.61 -> £3,382,035.87 (10.3%); £3,771,690.86 -> £3,382,035.99 (10.3%); £3,771,691.12 -> £3,382,036.10 (10.3%); £3,771,691.38 -> £3,382,036.21 (10.3%); £3,771,691.64 -> £3,382,036.33 (10.3%); £3,771,691.90 -> £3,382,036.44 (10.3%); £3,771,692.17 -> £3,382,036.55 (10.3%); £3,771,692.42 -> £3,382,036.65 (10.3%); £3,771,692.62 -> £3,382,036.89 (10.3%); £3,771,692.90 -> £3,382,037.11 (10.3%); £3,771,693.09 -> £3,382,037.29 (10.3%); £3,771,693.28 -> £3,382,037.45 (10.3%); £3,771,693.48 -> £3,382,037.61 (10.3%); £3,771,693.67 -> £3,382,037.76 (10.3%); £3,771,693.86 -> £3,382,037.91 (10.3%); £3,771,694.12 -> £3,382,038.05 (10.3%); £3,771,694.38 -> £3,382,038.19 (10.3%); £3,771,694.64 -> £3,382,038.34 (10.3%); £3,771,694.91 -> £3,382,038.47 (10.3%); £3,771,695.18 -> £3,382,038.52 (10.3%); £3,771,695.45 -> £3,382,038.56 (10.3%); £3,771,695.69 -> £3,382,038.60 (10.3%); £3,771,695.91 -> £3,382,038.63 (10.3%); £3,771,696.11 -> £3,382,038.67 (10.3%); £3,771,696.24 -> £3,382,038.71 (10.3%); £3,771,696.39 -> £3,382,038.75 (10.3%); £3,771,696.52 -> £3,382,038.78 (10.3%); £3,771,696.66 -> £3,382,038.82 (10.3%); £3,771,696.80 -> £3,382,038.86 (10.3%); £3,771,696.94 -> £3,382,038.90 (10.3%); £3,771,697.07 -> £3,382,038.93 (10.3%); £3,771,697.22 -> £3,382,038.97 (10.3%); £3,771,697.35 -> £3,382,039.01 (10.3%); £3,771,697.49 -> £3,382,039.05 (10.3%); £3,771,697.62 -> £3,382,039.09 (10.3%); £3,771,697.76 -> £3,382,039.20 (10.3%); £3,771,697.90 -> £3,382,039.32 (10.3%); £3,771,698.06 -> £3,382,039.45 (10.3%); £3,771,698.23 -> £3,382,039.57 (10.3%); £3,771,698.41 -> £3,382,039.71 (10.3%); £3,771,698.61 -> £3,382,039.85 (10.3%); £3,771,698.82 -> £3,382,040.03 (10.3%); £3,771,699.04 -> £3,382,040.21 (10.3%); £3,771,699.27 -> £3,382,040.30 (10.3%); £3,771,699.49 -> £3,382,040.39 (10.3%); £3,771,699.71 -> £3,382,040.49 (10.3%); £3,771,699.94 -> £3,382,040.58 (10.3%); £3,771,700.18 -> £3,382,040.66 (10.3%); £3,771,700.41 -> £3,382,040.74 (10.3%); £3,771,700.64 -> £3,382,040.82 (10.3%); £3,771,700.86 -> £3,382,040.89 (10.3%); £3,771,701.08 -> £3,382,040.96 (10.3%); £3,771,701.31 -> £3,382,041.03 (10.3%); £3,771,701.54 -> £3,382,041.10 (10.3%); £3,771,701.77 -> £3,382,041.17 (10.3%); £3,771,701.99 -> £3,382,041.23 (10.3%); £3,771,702.16 -> £3,382,041.39 (10.3%); £3,771,702.34 -> £3,382,041.54 (10.3%); £3,771,702.51 -> £3,382,041.68 (10.3%); £3,771,702.68 -> £3,382,041.81 (10.3%); £3,771,702.85 -> £3,382,041.94 (10.3%); £3,771,703.03 -> £3,382,042.07 (10.3%); £3,771,703.19 -> £3,382,042.20 (10.3%); £3,771,703.42 -> £3,382,042.32 (10.3%); £3,771,703.65 -> £3,382,042.45 (10.3%); £3,771,703.88 -> £3,382,042.58 (10.3%); £3,771,704.11 -> £3,382,042.70 (10.3%); £3,771,704.33 -> £3,382,042.74 (10.3%); £3,771,704.57 -> £3,382,042.78 (10.3%); £3,771,704.78 -> £3,382,042.82 (10.3%); £3,771,704.97 -> £3,382,042.85 (10.3%); £3,771,705.14 -> £3,382,042.89 (10.3%); £3,771,705.28 -> £3,382,042.93 (10.3%); £3,771,705.42 -> £3,382,042.97 (10.3%); £3,771,705.56 -> £3,382,043.01 (10.3%); £3,771,705.70 -> £3,382,043.04 (10.3%); £3,771,705.84 -> £3,382,043.08 (10.3%); £3,771,705.97 -> £3,382,043.12 (10.3%); £3,771,706.11 -> £3,382,043.15 (10.3%); £3,771,706.25 -> £3,382,043.19 (10.3%); £3,771,706.39 -> £3,382,043.22 (10.3%); £3,771,706.53 -> £3,382,043.26 (10.3%); £3,771,706.66 -> £3,382,043.30 (10.3%); £3,771,706.80 -> £3,382,043.41 (10.3%); £3,771,706.94 -> £3,382,043.53 (10.3%); £3,771,707.10 -> £3,382,043.64 (10.3%); £3,771,707.26 -> £3,382,043.76 (10.3%); £3,771,707.45 -> £3,382,043.88 (10.3%); £3,771,707.64 -> £3,382,044.00 (10.3%); £3,771,707.86 -> £3,382,044.12 (10.3%); £3,771,708.09 -> £3,382,044.25 (10.3%); £3,771,708.32 -> £3,382,044.30 (10.3%); £3,771,708.55 -> £3,382,044.34 (10.3%); £3,771,708.78 -> £3,382,044.39 (10.3%); £3,771,709.01 -> £3,382,044.44 (10.3%); £3,771,709.24 -> £3,382,044.49 (10.3%); £3,771,709.46 -> £3,382,044.54 (10.3%); £3,771,709.70 -> £3,382,044.59 (10.3%); £3,771,709.92 -> £3,382,044.64 (10.3%); £3,771,710.15 -> £3,382,044.68 (10.3%); £3,771,710.38 -> £3,382,044.73 (10.3%); £3,771,710.62 -> £3,382,044.78 (10.3%); £3,771,710.85 -> £3,382,044.82 (10.3%); £3,771,711.07 -> £3,382,044.87 (10.3%); £3,771,711.31 -> £3,382,045.00 (10.3%); £3,771,711.55 -> £3,382,045.13 (10.3%); £3,771,711.78 -> £3,382,045.26 (10.3%); £3,771,711.94 -> £3,382,045.39 (10.3%); £3,771,712.17 -> £3,382,045.52 (10.3%); £3,771,712.34 -> £3,382,045.65 (10.3%); £3,771,712.51 -> £3,382,045.78 (10.3%); £3,771,712.74 -> £3,382,045.91 (10.3%); £3,771,712.98 -> £3,382,046.03 (10.3%); £3,771,713.20 -> £3,382,046.16 (10.3%); £3,771,713.43 -> £3,382,046.28 (10.3%); £3,771,713.65 -> £3,382,046.32 (10.3%); £3,771,713.88 -> £3,382,046.36 (10.3%); £3,771,714.09 -> £3,382,046.40 (10.3%); £3,771,714.28 -> £3,382,046.44 (10.3%); £3,771,714.46 -> £3,382,046.47 (10.3%); £3,771,714.62 -> £3,382,046.51 (10.3%); £3,771,714.78 -> £3,382,046.55 (10.3%); £3,771,714.94 -> £3,382,046.59 (10.3%); £3,771,715.10 -> £3,382,046.63 (10.3%); £3,771,715.26 -> £3,382,046.67 (10.3%); £3,771,715.42 -> £3,382,046.71 (10.3%); £3,771,715.58 -> £3,382,046.74 (10.3%); £3,771,715.74 -> £3,382,046.78 (10.3%); £3,771,715.90 -> £3,382,046.82 (10.3%); £3,771,716.05 -> £3,382,046.86 (10.3%); £3,771,716.22 -> £3,382,046.90 (10.3%); £3,771,716.38 -> £3,382,047.06 (10.3%); £3,771,716.54 -> £3,382,047.22 (10.3%); £3,771,716.71 -> £3,382,047.39 (10.3%); £3,771,716.90 -> £3,382,047.58 (10.3%); £3,771,717.11 -> £3,382,047.78 (10.3%); £3,771,717.34 -> £3,382,048.01 (10.3%); £3,771,717.59 -> £3,382,048.25 (10.3%); £3,771,717.85 -> £3,382,048.51 (10.3%); £3,771,718.10 -> £3,382,048.64 (10.3%); £3,771,718.37 -> £3,382,048.77 (10.3%); £3,771,718.63 -> £3,382,048.89 (10.3%); £3,771,718.90 -> £3,382,049.03 (10.3%); £3,771,719.17 -> £3,382,049.16 (10.3%); £3,771,719.43 -> £3,382,049.28 (10.3%); £3,771,719.70 -> £3,382,049.39 (10.3%); £3,771,719.96 -> £3,382,049.51 (10.3%); £3,771,720.24 -> £3,382,049.63 (10.3%); £3,771,720.50 -> £3,382,049.75 (10.3%); £3,771,720.76 -> £3,382,049.87 (10.3%); £3,771,721.02 -> £3,382,049.98 (10.3%); £3,771,721.28 -> £3,382,050.09 (10.3%); £3,771,721.54 -> £3,382,050.34 (10.3%); £3,771,721.74 -> £3,382,050.58 (10.3%); £3,771,721.93 -> £3,382,050.78 (10.3%); £3,771,722.13 -> £3,382,050.97 (10.3%); £3,771,722.39 -> £3,382,051.15 (10.3%); £3,771,722.64 -> £3,382,051.33 (10.3%); £3,771,722.91 -> £3,382,051.50 (10.3%); £3,771,723.18 -> £3,382,051.67 (10.3%); £3,771,723.44 -> £3,382,051.84 (10.3%); £3,771,723.71 -> £3,382,052.00 (10.3%); £3,771,723.97 -> £3,382,052.16 (10.3%); £3,771,724.24 -> £3,382,052.20 (10.3%); £3,771,724.51 -> £3,382,052.24 (10.3%); £3,771,724.76 -> £3,382,052.28 (10.3%); £3,771,724.98 -> £3,382,052.32 (10.3%); £3,771,725.18 -> £3,382,052.35 (10.3%); £3,771,725.34 -> £3,382,052.39 (10.3%); £3,771,725.50 -> £3,382,052.43 (10.3%); £3,771,725.66 -> £3,382,052.47 (10.3%); £3,771,725.82 -> £3,382,052.50 (10.3%); £3,771,725.98 -> £3,382,052.54 (10.3%); £3,771,726.14 -> £3,382,052.58 (10.3%); £3,771,726.30 -> £3,382,052.62 (10.3%); £3,771,726.45 -> £3,382,052.66 (10.3%); £3,771,726.61 -> £3,382,052.69 (10.3%); £3,771,726.77 -> £3,382,052.73 (10.3%); £3,771,726.93 -> £3,382,052.77 (10.3%); £3,771,727.08 -> £3,382,052.92 (10.3%); £3,771,727.24 -> £3,382,053.07 (10.3%); £3,771,727.42 -> £3,382,053.23 (10.3%); £3,771,727.61 -> £3,382,053.41 (10.3%); £3,771,727.82 -> £3,382,053.61 (10.3%); £3,771,728.05 -> £3,382,053.83 (10.3%); £3,771,728.30 -> £3,382,054.07 (10.3%); £3,771,728.56 -> £3,382,054.33 (10.3%); £3,771,728.83 -> £3,382,054.45 (10.3%); £3,771,729.09 -> £3,382,054.58 (10.3%); £3,771,729.37 -> £3,382,054.71 (10.3%); £3,771,729.63 -> £3,382,054.84 (10.3%); £3,771,729.89 -> £3,382,054.97 (10.3%); £3,771,730.15 -> £3,382,055.10 (10.3%); £3,771,730.42 -> £3,382,055.22 (10.3%); £3,771,730.68 -> £3,382,055.35 (10.3%); £3,771,730.94 -> £3,382,055.47 (10.3%); £3,771,731.20 -> £3,382,055.59 (10.3%); £3,771,731.47 -> £3,382,055.71 (10.3%); £3,771,731.74 -> £3,382,055.82 (10.3%); £3,771,732.00 -> £3,382,055.93 (10.3%); £3,771,732.27 -> £3,382,056.19 (10.3%); £3,771,732.53 -> £3,382,056.42 (10.3%); £3,771,732.80 -> £3,382,056.63 (10.3%); £3,771,733.06 -> £3,382,056.81 (10.3%); £3,771,733.32 -> £3,382,056.99 (10.3%); £3,771,733.60 -> £3,382,057.15 (10.3%); £3,771,733.79 -> £3,382,057.31 (10.3%); £3,771,734.05 -> £3,382,057.48 (10.3%); £3,771,734.30 -> £3,382,057.63 (10.3%); £3,771,734.57 -> £3,382,057.79 (10.3%); £3,771,734.84 -> £3,382,057.94 (10.3%); £3,771,735.10 -> £3,382,057.98 (10.3%); £3,771,735.36 -> £3,382,058.02 (10.3%); £3,771,735.61 -> £3,382,058.06 (10.3%); £3,771,735.83 -> £3,382,058.10 (10.3%); £3,771,736.03 -> £3,382,058.14 (10.3%); £3,771,736.20 -> £3,382,058.17 (10.3%); £3,771,736.36 -> £3,382,058.21 (10.3%); £3,771,736.52 -> £3,382,058.25 (10.3%); £3,771,736.69 -> £3,382,058.29 (10.3%); £3,771,736.85 -> £3,382,058.33 (10.3%); £3,771,737.01 -> £3,382,058.36 (10.3%); £3,771,737.17 -> £3,382,058.40 (10.3%); £3,771,737.33 -> £3,382,058.44 (10.3%); £3,771,737.48 -> £3,382,058.48 (10.3%); £3,771,737.65 -> £3,382,058.52 (10.3%); £3,771,737.81 -> £3,382,058.56 (10.3%); £3,771,737.97 -> £3,382,058.71 (10.3%); £3,771,738.13 -> £3,382,058.85 (10.3%); £3,771,738.31 -> £3,382,059.01 (10.3%); £3,771,738.51 -> £3,382,059.18 (10.3%); £3,771,738.72 -> £3,382,059.37 (10.3%); £3,771,738.94 -> £3,382,059.58 (10.3%); £3,771,739.19 -> £3,382,059.82 (10.3%); £3,771,739.47 -> £3,382,060.06 (10.3%); £3,771,739.74 -> £3,382,060.19 (10.3%); £3,771,740.00 -> £3,382,060.32 (10.3%); £3,771,740.27 -> £3,382,060.44 (10.3%); £3,771,740.53 -> £3,382,060.57 (10.3%); £3,771,740.80 -> £3,382,060.70 (10.3%); £3,771,741.06 -> £3,382,060.82 (10.3%); £3,771,741.33 -> £3,382,060.94 (10.3%); £3,771,741.60 -> £3,382,061.05 (10.3%); £3,771,741.87 -> £3,382,061.17 (10.3%); £3,771,742.13 -> £3,382,061.29 (10.3%); £3,771,742.40 -> £3,382,061.41 (10.3%); £3,771,742.67 -> £3,382,061.52 (10.3%); £3,771,742.94 -> £3,382,061.63 (10.3%); £3,771,743.20 -> £3,382,061.87 (10.3%); £3,771,743.47 -> £3,382,062.09 (10.3%); £3,771,743.73 -> £3,382,062.28 (10.3%); £3,771,744.00 -> £3,382,062.45 (10.3%); £3,771,744.20 -> £3,382,062.61 (10.3%); £3,771,744.40 -> £3,382,062.77 (10.3%); £3,771,744.67 -> £3,382,062.93 (10.3%); £3,771,744.93 -> £3,382,063.09 (10.3%); £3,771,745.19 -> £3,382,063.24 (10.3%); £3,771,745.46 -> £3,382,063.38 (10.3%); £3,771,745.74 -> £3,382,063.54 (10.3%); £3,771,746.00 -> £3,382,063.58 (10.3%); £3,771,746.27 -> £3,382,063.62 (10.3%); £3,771,746.52 -> £3,382,063.66 (10.3%); £3,771,746.74 -> £3,382,063.70 (10.3%); £3,771,746.95 -> £3,382,063.74 (10.3%); £3,771,747.10 -> £3,382,063.78 (10.3%); £3,771,747.26 -> £3,382,063.81 (10.3%); £3,771,747.42 -> £3,382,063.85 (10.3%); £3,771,747.58 -> £3,382,063.89 (10.3%); £3,771,747.74 -> £3,382,063.93 (10.3%); £3,771,747.90 -> £3,382,063.97 (10.3%); £3,771,748.07 -> £3,382,064.00 (10.3%); £3,771,748.23 -> £3,382,064.04 (10.3%); £3,771,748.39 -> £3,382,064.08 (10.3%); £3,771,748.55 -> £3,382,064.12 (10.3%); £3,771,748.71 -> £3,382,064.16 (10.3%); £3,771,748.87 -> £3,382,064.34 (10.3%); £3,771,749.03 -> £3,382,064.53 (10.3%); £3,771,749.21 -> £3,382,064.72 (10.3%); £3,771,749.41 -> £3,382,064.92 (10.3%); £3,771,749.62 -> £3,382,065.15 (10.3%); £3,771,749.86 -> £3,382,065.40 (10.3%); £3,771,750.11 -> £3,382,065.66 (10.3%); £3,771,750.38 -> £3,382,065.94 (10.3%); £3,771,750.64 -> £3,382,066.06 (10.3%); £3,771,750.91 -> £3,382,066.19 (10.3%); £3,771,751.18 -> £3,382,066.31 (10.3%); £3,771,751.44 -> £3,382,066.43 (10.3%); £3,771,751.70 -> £3,382,066.56 (10.3%); £3,771,751.97 -> £3,382,066.68 (10.3%); £3,771,752.25 -> £3,382,066.79 (10.3%); £3,771,752.52 -> £3,382,066.90 (10.3%); £3,771,752.78 -> £3,382,067.01 (10.3%); £3,771,753.05 -> £3,382,067.13 (10.3%); £3,771,753.31 -> £3,382,067.24 (10.3%); £3,771,753.58 -> £3,382,067.35 (10.3%); £3,771,753.85 -> £3,382,067.46 (10.3%); £3,771,754.12 -> £3,382,067.74 (10.3%); £3,771,754.39 -> £3,382,068.01 (10.3%); £3,771,754.66 -> £3,382,068.25 (10.3%); £3,771,754.93 -> £3,382,068.45 (10.3%); £3,771,755.13 -> £3,382,068.66 (10.3%); £3,771,755.40 -> £3,382,068.86 (10.3%); £3,771,755.68 -> £3,382,069.06 (10.3%); £3,771,755.94 -> £3,382,069.25 (10.3%); £3,771,756.22 -> £3,382,069.44 (10.3%); £3,771,756.49 -> £3,382,069.62 (10.3%); £3,771,756.75 -> £3,382,069.79 (10.3%); £3,771,757.02 -> £3,382,069.84 (10.3%); £3,771,757.29 -> £3,382,069.88 (10.3%); £3,771,757.53 -> £3,382,069.92 (10.3%); £3,771,757.75 -> £3,382,069.96 (10.3%); £3,771,757.96 -> £3,382,069.99 (10.3%); £3,771,758.12 -> £3,382,070.03 (10.3%); £3,771,758.28 -> £3,382,070.07 (10.3%); £3,771,758.45 -> £3,382,070.10 (10.3%); £3,771,758.60 -> £3,382,070.14 (10.3%); £3,771,758.76 -> £3,382,070.18 (10.3%); £3,771,758.92 -> £3,382,070.22 (10.3%); £3,771,759.08 -> £3,382,070.25 (10.3%); £3,771,759.24 -> £3,382,070.29 (10.3%); £3,771,759.41 -> £3,382,070.33 (10.3%); £3,771,759.57 -> £3,382,070.37 (10.3%); £3,771,759.73 -> £3,382,070.41 (10.3%); £3,771,759.89 -> £3,382,070.63 (10.3%); £3,771,760.04 -> £3,382,070.86 (10.3%); £3,771,760.22 -> £3,382,071.11 (10.3%); £3,771,760.42 -> £3,382,071.37 (10.3%); £3,771,760.63 -> £3,382,071.64 (10.3%); £3,771,760.86 -> £3,382,071.94 (10.3%); £3,771,761.11 -> £3,382,072.27 (10.3%); £3,771,761.39 -> £3,382,072.60 (10.3%); £3,771,761.65 -> £3,382,072.73 (10.3%); £3,771,761.91 -> £3,382,072.86 (10.3%); £3,771,762.16 -> £3,382,072.98 (10.3%); £3,771,762.42 -> £3,382,073.11 (10.3%); £3,771,762.68 -> £3,382,073.24 (10.3%); £3,771,762.95 -> £3,382,073.36 (10.3%); £3,771,763.21 -> £3,382,073.47 (10.3%); £3,771,763.49 -> £3,382,073.59 (10.3%); £3,771,763.76 -> £3,382,073.71 (10.3%); £3,771,764.02 -> £3,382,073.83 (10.3%); £3,771,764.28 -> £3,382,073.94 (10.3%); £3,771,764.55 -> £3,382,074.06 (10.3%); £3,771,764.81 -> £3,382,074.17 (10.3%); £3,771,765.08 -> £3,382,074.49 (10.3%); £3,771,765.33 -> £3,382,074.78 (10.3%); £3,771,765.53 -> £3,382,075.05 (10.3%); £3,771,765.74 -> £3,382,075.29 (10.3%); £3,771,765.93 -> £3,382,075.53 (10.3%); £3,771,766.13 -> £3,382,075.76 (10.3%); £3,771,766.34 -> £3,382,075.99 (10.3%); £3,771,766.60 -> £3,382,076.21 (10.3%); £3,771,766.86 -> £3,382,076.43 (10.3%); £3,771,767.14 -> £3,382,076.65 (10.3%); £3,771,767.40 -> £3,382,076.86 (10.3%); £3,771,767.67 -> £3,382,076.90 (10.3%); £3,771,767.93 -> £3,382,076.95 (10.3%); £3,771,768.17 -> £3,382,076.99 (10.3%); £3,771,768.39 -> £3,382,077.02 (10.3%); £3,771,768.59 -> £3,382,077.06 (10.3%); £3,771,768.73 -> £3,382,077.10 (10.3%); £3,771,768.87 -> £3,382,077.13 (10.3%); £3,771,769.02 -> £3,382,077.17 (10.3%); £3,771,769.16 -> £3,382,077.21 (10.3%); £3,771,769.30 -> £3,382,077.24 (10.3%); £3,771,769.44 -> £3,382,077.28 (10.3%); £3,771,769.58 -> £3,382,077.32 (10.3%); £3,771,769.72 -> £3,382,077.35 (10.3%); £3,771,769.86 -> £3,382,077.39 (10.3%); £3,771,770.00 -> £3,382,077.43 (10.3%); £3,771,770.14 -> £3,382,077.47 (10.3%); £3,771,770.28 -> £3,382,077.70 (10.3%); £3,771,770.42 -> £3,382,077.94 (10.3%); £3,771,770.58 -> £3,382,078.18 (10.3%); £3,771,770.75 -> £3,382,078.42 (10.3%); £3,771,770.94 -> £3,382,078.67 (10.3%); £3,771,771.14 -> £3,382,078.93 (10.3%); £3,771,771.37 -> £3,382,079.21 (10.3%); £3,771,771.60 -> £3,382,079.50 (10.3%); £3,771,771.84 -> £3,382,079.59 (10.3%); £3,771,772.07 -> £3,382,079.68 (10.3%); £3,771,772.31 -> £3,382,079.77 (10.3%); £3,771,772.54 -> £3,382,079.87 (10.3%); £3,771,772.77 -> £3,382,079.95 (10.3%); £3,771,773.01 -> £3,382,080.03 (10.3%); £3,771,773.24 -> £3,382,080.10 (10.3%); £3,771,773.47 -> £3,382,080.18 (10.3%); £3,771,773.71 -> £3,382,080.25 (10.3%); £3,771,773.94 -> £3,382,080.32 (10.3%); £3,771,774.18 -> £3,382,080.39 (10.3%); £3,771,774.43 -> £3,382,080.46 (10.3%); £3,771,774.66 -> £3,382,080.52 (10.3%); £3,771,774.84 -> £3,382,080.78 (10.3%); £3,771,775.01 -> £3,382,081.03 (10.3%); £3,771,775.19 -> £3,382,081.27 (10.3%); £3,771,775.36 -> £3,382,081.50 (10.3%); £3,771,775.54 -> £3,382,081.73 (10.3%); £3,771,775.71 -> £3,382,081.96 (10.3%); £3,771,775.89 -> £3,382,082.19 (10.3%); £3,771,776.13 -> £3,382,082.41 (10.3%); £3,771,776.37 -> £3,382,082.64 (10.3%); £3,771,776.60 -> £3,382,082.86 (10.3%); £3,771,776.84 -> £3,382,083.08 (10.3%); £3,771,777.08 -> £3,382,083.12 (10.3%); £3,771,777.31 -> £3,382,083.16 (10.3%); £3,771,777.52 -> £3,382,083.20 (10.3%); £3,771,777.72 -> £3,382,083.24 (10.3%); £3,771,777.91 -> £3,382,083.28 (10.3%); £3,771,778.05 -> £3,382,083.31 (10.3%); £3,771,778.20 -> £3,382,083.35 (10.3%); £3,771,778.33 -> £3,382,083.39 (10.3%); £3,771,778.48 -> £3,382,083.43 (10.3%); £3,771,778.61 -> £3,382,083.46 (10.3%); £3,771,778.75 -> £3,382,083.50 (10.3%); £3,771,778.89 -> £3,382,083.54 (10.3%); £3,771,779.03 -> £3,382,083.57 (10.3%); £3,771,779.17 -> £3,382,083.61 (10.3%); £3,771,779.31 -> £3,382,083.64 (10.3%); £3,771,779.45 -> £3,382,083.68 (10.3%); £3,771,779.59 -> £3,382,083.89 (10.3%); £3,771,779.73 -> £3,382,084.10 (10.3%); £3,771,779.88 -> £3,382,084.32 (10.3%); £3,771,780.06 -> £3,382,084.53 (10.3%); £3,771,780.25 -> £3,382,084.75 (10.3%); £3,771,780.45 -> £3,382,084.97 (10.3%); £3,771,780.66 -> £3,382,085.19 (10.3%); £3,771,780.90 -> £3,382,085.42 (10.3%); £3,771,781.14 -> £3,382,085.47 (10.3%); £3,771,781.38 -> £3,382,085.52 (10.3%); £3,771,781.62 -> £3,382,085.57 (10.3%); £3,771,781.84 -> £3,382,085.62 (10.3%); £3,771,782.08 -> £3,382,085.67 (10.3%); £3,771,782.31 -> £3,382,085.71 (10.3%); £3,771,782.54 -> £3,382,085.76 (10.3%); £3,771,782.79 -> £3,382,085.81 (10.3%); £3,771,783.02 -> £3,382,085.85 (10.3%); £3,771,783.25 -> £3,382,085.90 (10.3%); £3,771,783.48 -> £3,382,085.94 (10.3%); £3,771,783.72 -> £3,382,085.99 (10.3%); £3,771,783.95 -> £3,382,086.03 (10.3%); £3,771,784.13 -> £3,382,086.25 (10.3%); £3,771,784.30 -> £3,382,086.46 (10.3%); £3,771,784.48 -> £3,382,086.67 (10.3%); £3,771,784.66 -> £3,382,086.88 (10.3%); £3,771,784.89 -> £3,382,087.11 (10.3%); £3,771,785.12 -> £3,382,087.32 (10.3%); £3,771,785.30 -> £3,382,087.54 (10.3%); £3,771,785.54 -> £3,382,087.75 (10.3%); £3,771,785.77 -> £3,382,087.97 (10.3%); £3,771,786.00 -> £3,382,088.18 (10.3%); £3,771,786.23 -> £3,382,088.40 (10.3%); £3,771,786.46 -> £3,382,088.44 (10.3%); £3,771,786.70 -> £3,382,088.48 (10.3%); £3,771,786.91 -> £3,382,088.51 (10.3%); £3,771,787.11 -> £3,382,088.55 (10.3%); £3,771,787.29 -> £3,382,088.59 (10.3%); £3,771,787.45 -> £3,382,088.62 (10.3%); £3,771,787.61 -> £3,382,088.66 (10.3%); £3,771,787.77 -> £3,382,088.70 (10.3%); £3,771,787.92 -> £3,382,088.74 (10.3%); £3,771,788.09 -> £3,382,088.78 (10.3%); £3,771,788.25 -> £3,382,088.81 (10.3%); £3,771,788.40 -> £3,382,088.85 (10.3%); £3,771,788.57 -> £3,382,088.89 (10.3%); £3,771,788.73 -> £3,382,088.93 (10.3%); £3,771,788.89 -> £3,382,088.97 (10.3%); £3,771,789.05 -> £3,382,089.01 (10.3%); £3,771,789.21 -> £3,382,089.21 (10.3%); £3,771,789.37 -> £3,382,089.42 (10.3%); £3,771,789.54 -> £3,382,089.63 (10.3%); £3,771,789.73 -> £3,382,089.86 (10.3%); £3,771,789.96 -> £3,382,090.12 (10.3%); £3,771,790.18 -> £3,382,090.39 (10.3%); £3,771,790.42 -> £3,382,090.69 (10.3%); £3,771,790.69 -> £3,382,090.99 (10.3%); £3,771,790.95 -> £3,382,091.11 (10.3%); £3,771,791.21 -> £3,382,091.24 (10.3%); £3,771,791.48 -> £3,382,091.36 (10.3%); £3,771,791.75 -> £3,382,091.49 (10.3%); £3,771,792.02 -> £3,382,091.62 (10.3%); £3,771,792.27 -> £3,382,091.74 (10.3%); £3,771,792.53 -> £3,382,091.86 (10.3%); £3,771,792.80 -> £3,382,091.98 (10.3%); £3,771,793.07 -> £3,382,092.10 (10.3%); £3,771,793.33 -> £3,382,092.22 (10.3%); £3,771,793.60 -> £3,382,092.33 (10.3%); £3,771,793.86 -> £3,382,092.45 (10.3%); £3,771,794.12 -> £3,382,092.56 (10.3%); £3,771,794.38 -> £3,382,092.86 (10.3%); £3,771,794.66 -> £3,382,093.15 (10.3%); £3,771,794.92 -> £3,382,093.40 (10.3%); £3,771,795.18 -> £3,382,093.63 (10.3%); £3,771,795.44 -> £3,382,093.85 (10.3%); £3,771,795.69 -> £3,382,094.06 (10.3%); £3,771,795.90 -> £3,382,094.28 (10.3%); £3,771,796.16 -> £3,382,094.49 (10.3%); £3,771,796.42 -> £3,382,094.70 (10.3%); £3,771,796.67 -> £3,382,094.90 (10.3%); £3,771,796.93 -> £3,382,095.10 (10.3%); £3,771,797.19 -> £3,382,095.14 (10.3%); £3,771,797.45 -> £3,382,095.18 (10.3%); £3,771,797.70 -> £3,382,095.22 (10.3%); £3,771,797.92 -> £3,382,095.26 (10.3%); £3,771,798.13 -> £3,382,095.30 (10.3%); £3,771,798.29 -> £3,382,095.34 (10.3%); £3,771,798.44 -> £3,382,095.37 (10.3%); £3,771,798.60 -> £3,382,095.41 (10.3%); £3,771,798.76 -> £3,382,095.45 (10.3%); £3,771,798.92 -> £3,382,095.49 (10.3%); £3,771,799.07 -> £3,382,095.52 (10.3%); £3,771,799.23 -> £3,382,095.56 (10.3%); £3,771,799.39 -> £3,382,095.60 (10.3%); £3,771,799.55 -> £3,382,095.64 (10.3%); £3,771,799.70 -> £3,382,095.68 (10.3%); £3,771,799.85 -> £3,382,095.72 (10.3%); £3,771,800.01 -> £3,382,095.95 (10.3%); £3,771,800.17 -> £3,382,096.18 (10.3%); £3,771,800.35 -> £3,382,096.43 (10.3%); £3,771,800.53 -> £3,382,096.68 (10.3%); £3,771,800.74 -> £3,382,096.96 (10.3%); £3,771,800.98 -> £3,382,097.26 (10.3%); £3,771,801.23 -> £3,382,097.58 (10.3%); £3,771,801.48 -> £3,382,097.91 (10.3%); £3,771,801.74 -> £3,382,098.03 (10.3%); £3,771,802.00 -> £3,382,098.16 (10.3%); £3,771,802.25 -> £3,382,098.29 (10.3%); £3,771,802.51 -> £3,382,098.42 (10.3%); £3,771,802.77 -> £3,382,098.55 (10.3%); £3,771,803.03 -> £3,382,098.68 (10.3%); £3,771,803.29 -> £3,382,098.80 (10.3%); £3,771,803.56 -> £3,382,098.92 (10.3%); £3,771,803.81 -> £3,382,099.04 (10.3%); £3,771,804.08 -> £3,382,099.16 (10.3%); £3,771,804.33 -> £3,382,099.27 (10.3%); £3,771,804.59 -> £3,382,099.38 (10.3%); £3,771,804.86 -> £3,382,099.49 (10.3%); £3,771,805.13 -> £3,382,099.81 (10.3%); £3,771,805.39 -> £3,382,100.10 (10.3%); £3,771,805.57 -> £3,382,100.37 (10.3%); £3,771,805.78 -> £3,382,100.61 (10.3%); £3,771,805.98 -> £3,382,100.85 (10.3%); £3,771,806.17 -> £3,382,101.09 (10.3%); £3,771,806.43 -> £3,382,101.32 (10.3%); £3,771,806.69 -> £3,382,101.55 (10.3%); £3,771,806.96 -> £3,382,101.77 (10.3%); £3,771,807.22 -> £3,382,102.00 (10.3%); £3,771,807.48 -> £3,382,102.22 (10.3%); £3,771,807.74 -> £3,382,102.27 (10.3%); £3,771,808.01 -> £3,382,102.31 (10.3%); £3,771,808.25 -> £3,382,102.35 (10.3%); £3,771,808.48 -> £3,382,102.38 (10.3%); £3,771,808.68 -> £3,382,102.42 (10.3%); £3,771,808.84 -> £3,382,102.46 (10.3%); £3,771,809.00 -> £3,382,102.50 (10.3%); £3,771,809.15 -> £3,382,102.53 (10.3%); £3,771,809.31 -> £3,382,102.57 (10.3%); £3,771,809.46 -> £3,382,102.61 (10.3%); £3,771,809.62 -> £3,382,102.64 (10.3%); £3,771,809.78 -> £3,382,102.68 (10.3%); £3,771,809.94 -> £3,382,102.72 (10.3%); £3,771,810.10 -> £3,382,102.76 (10.3%); £3,771,810.25 -> £3,382,102.80 (10.3%); £3,771,810.41 -> £3,382,102.84 (10.3%); £3,771,810.57 -> £3,382,103.02 (10.3%); £3,771,810.72 -> £3,382,103.20 (10.3%); £3,771,810.90 -> £3,382,103.40 (10.3%); £3,771,811.10 -> £3,382,103.61 (10.3%); £3,771,811.30 -> £3,382,103.84 (10.3%); £3,771,811.53 -> £3,382,104.09 (10.3%); £3,771,811.77 -> £3,382,104.37 (10.3%); £3,771,812.02 -> £3,382,104.66 (10.3%); £3,771,812.28 -> £3,382,104.79 (10.3%); £3,771,812.54 -> £3,382,104.92 (10.3%); £3,771,812.79 -> £3,382,105.05 (10.3%); £3,771,813.06 -> £3,382,105.18 (10.3%); £3,771,813.32 -> £3,382,105.31 (10.3%); £3,771,813.58 -> £3,382,105.43 (10.3%); £3,771,813.85 -> £3,382,105.55 (10.3%); £3,771,814.11 -> £3,382,105.67 (10.3%); £3,771,814.37 -> £3,382,105.79 (10.3%); £3,771,814.64 -> £3,382,105.90 (10.3%); £3,771,814.90 -> £3,382,106.01 (10.3%); £3,771,815.16 -> £3,382,106.13 (10.3%); £3,771,815.42 -> £3,382,106.23 (10.3%); £3,771,815.62 -> £3,382,106.52 (10.3%); £3,771,815.88 -> £3,382,106.78 (10.3%); £3,771,816.08 -> £3,382,107.01 (10.3%); £3,771,816.28 -> £3,382,107.22 (10.3%); £3,771,816.55 -> £3,382,107.42 (10.3%); £3,771,816.81 -> £3,382,107.62 (10.3%); £3,771,817.00 -> £3,382,107.82 (10.3%); £3,771,817.26 -> £3,382,108.01 (10.3%); £3,771,817.52 -> £3,382,108.19 (10.3%); £3,771,817.79 -> £3,382,108.38 (10.3%); £3,771,818.05 -> £3,382,108.56 (10.3%); £3,771,818.32 -> £3,382,108.60 (10.3%); £3,771,818.59 -> £3,382,108.64 (10.3%); £3,771,818.83 -> £3,382,108.68 (10.3%); £3,771,819.06 -> £3,382,108.72 (10.3%); £3,771,819.26 -> £3,382,108.75 (10.3%); £3,771,819.42 -> £3,382,108.79 (10.3%); £3,771,819.57 -> £3,382,108.83 (10.3%); £3,771,819.72 -> £3,382,108.87 (10.3%); £3,771,819.88 -> £3,382,108.90 (10.3%); £3,771,820.03 -> £3,382,108.94 (10.3%); £3,771,820.19 -> £3,382,108.98 (10.3%); £3,771,820.34 -> £3,382,109.01 (10.3%); £3,771,820.50 -> £3,382,109.05 (10.3%); £3,771,820.65 -> £3,382,109.09 (10.3%); £3,771,820.81 -> £3,382,109.13 (10.3%); £3,771,820.96 -> £3,382,109.17 (10.3%); £3,771,821.12 -> £3,382,109.34 (10.3%); £3,771,821.27 -> £3,382,109.52 (10.3%); £3,771,821.44 -> £3,382,109.70 (10.3%); £3,771,821.63 -> £3,382,109.89 (10.3%); £3,771,821.83 -> £3,382,110.10 (10.3%); £3,771,822.06 -> £3,382,110.33 (10.3%); £3,771,822.30 -> £3,382,110.58 (10.3%); £3,771,822.56 -> £3,382,110.85 (10.3%); £3,771,822.82 -> £3,382,110.97 (10.3%); £3,771,823.08 -> £3,382,111.10 (10.3%); £3,771,823.34 -> £3,382,111.22 (10.3%); £3,771,823.59 -> £3,382,111.35 (10.3%); £3,771,823.85 -> £3,382,111.47 (10.3%); £3,771,824.10 -> £3,382,111.60 (10.3%); £3,771,824.36 -> £3,382,111.71 (10.3%); £3,771,824.62 -> £3,382,111.83 (10.3%); £3,771,824.88 -> £3,382,111.94 (10.3%); £3,771,825.14 -> £3,382,112.06 (10.3%); £3,771,825.39 -> £3,382,112.18 (10.3%); £3,771,825.63 -> £3,382,112.29 (10.3%); £3,771,825.90 -> £3,382,112.40 (10.3%); £3,771,826.15 -> £3,382,112.67 (10.3%); £3,771,826.41 -> £3,382,112.91 (10.3%); £3,771,826.66 -> £3,382,113.12 (10.3%); £3,771,826.86 -> £3,382,113.31 (10.3%); £3,771,827.05 -> £3,382,113.49 (10.3%); £3,771,827.31 -> £3,382,113.67 (10.3%); £3,771,827.51 -> £3,382,113.84 (10.3%); £3,771,827.76 -> £3,382,114.01 (10.3%); £3,771,828.01 -> £3,382,114.17 (10.3%); £3,771,828.28 -> £3,382,114.33 (10.3%); £3,771,828.53 -> £3,382,114.49 (10.3%); £3,771,828.80 -> £3,382,114.53 (10.3%); £3,771,829.06 -> £3,382,114.57 (10.3%); £3,771,829.30 -> £3,382,114.61 (10.3%); £3,771,829.52 -> £3,382,114.65 (10.3%); £3,771,829.72 -> £3,382,114.69 (10.3%); £3,771,829.88 -> £3,382,114.73 (10.3%); £3,771,830.03 -> £3,382,114.76 (10.3%); £3,771,830.19 -> £3,382,114.80 (10.3%); £3,771,830.34 -> £3,382,114.84 (10.3%); £3,771,830.50 -> £3,382,114.87 (10.3%); £3,771,830.66 -> £3,382,114.91 (10.3%); £3,771,830.82 -> £3,382,114.95 (10.3%); £3,771,830.97 -> £3,382,114.99 (10.3%); £3,771,831.13 -> £3,382,115.03 (10.3%); £3,771,831.28 -> £3,382,115.06 (10.3%); £3,771,831.43 -> £3,382,115.11 (10.3%); £3,771,831.59 -> £3,382,115.33 (10.3%); £3,771,831.74 -> £3,382,115.55 (10.3%); £3,771,831.92 -> £3,382,115.79 (10.3%); £3,771,832.10 -> £3,382,116.04 (10.3%); £3,771,832.30 -> £3,382,116.31 (10.3%); £3,771,832.53 -> £3,382,116.60 (10.3%); £3,771,832.76 -> £3,382,116.92 (10.3%); £3,771,833.02 -> £3,382,117.25 (10.3%); £3,771,833.28 -> £3,382,117.37 (10.3%); £3,771,833.54 -> £3,382,117.50 (10.3%); £3,771,833.80 -> £3,382,117.62 (10.3%); £3,771,834.06 -> £3,382,117.75 (10.3%); £3,771,834.33 -> £3,382,117.88 (10.3%); £3,771,834.59 -> £3,382,118.00 (10.3%); £3,771,834.85 -> £3,382,118.11 (10.3%); £3,771,835.11 -> £3,382,118.22 (10.3%); £3,771,835.37 -> £3,382,118.34 (10.3%); £3,771,835.64 -> £3,382,118.46 (10.3%); £3,771,835.90 -> £3,382,118.58 (10.3%); £3,771,836.16 -> £3,382,118.69 (10.3%); £3,771,836.42 -> £3,382,118.79 (10.3%); £3,771,836.67 -> £3,382,119.10 (10.3%); £3,771,836.93 -> £3,382,119.40 (10.3%); £3,771,837.19 -> £3,382,119.66 (10.3%); £3,771,837.46 -> £3,382,119.90 (10.3%); £3,771,837.73 -> £3,382,120.14 (10.3%); £3,771,837.99 -> £3,382,120.37 (10.3%); £3,771,838.25 -> £3,382,120.62 (10.3%); £3,771,838.51 -> £3,382,120.84 (10.3%); £3,771,838.78 -> £3,382,121.07 (10.3%); £3,771,839.04 -> £3,382,121.30 (10.3%); £3,771,839.30 -> £3,382,121.51 (10.3%); £3,771,839.57 -> £3,382,121.55 (10.3%); £3,771,839.83 -> £3,382,121.59 (10.3%); £3,771,840.07 -> £3,382,121.63 (10.3%); £3,771,840.29 -> £3,382,121.67 (10.3%); £3,771,840.49 -> £3,382,121.70 (10.3%); £3,771,840.63 -> £3,382,121.74 (10.3%); £3,771,840.76 -> £3,382,121.78 (10.3%); £3,771,840.89 -> £3,382,121.82 (10.3%); £3,771,841.03 -> £3,382,121.85 (10.3%); £3,771,841.17 -> £3,382,121.89 (10.3%); £3,771,841.30 -> £3,382,121.93 (10.3%); £3,771,841.44 -> £3,382,121.96 (10.3%); £3,771,841.57 -> £3,382,122.00 (10.3%); £3,771,841.71 -> £3,382,122.04 (10.3%); £3,771,841.85 -> £3,382,122.08 (10.3%); £3,771,841.99 -> £3,382,122.11 (10.3%); £3,771,842.12 -> £3,382,122.35 (10.3%); £3,771,842.26 -> £3,382,122.58 (10.3%); £3,771,842.42 -> £3,382,122.82 (10.3%); £3,771,842.58 -> £3,382,123.06 (10.3%); £3,771,842.76 -> £3,382,123.30 (10.3%); £3,771,842.96 -> £3,382,123.56 (10.3%); £3,771,843.17 -> £3,382,123.83 (10.3%); £3,771,843.40 -> £3,382,124.11 (10.3%); £3,771,843.63 -> £3,382,124.20 (10.3%); £3,771,843.85 -> £3,382,124.29 (10.3%); £3,771,844.07 -> £3,382,124.38 (10.3%); £3,771,844.29 -> £3,382,124.47 (10.3%); £3,771,844.52 -> £3,382,124.55 (10.3%); £3,771,844.74 -> £3,382,124.63 (10.3%); £3,771,844.97 -> £3,382,124.71 (10.3%); £3,771,845.20 -> £3,382,124.78 (10.3%); £3,771,845.44 -> £3,382,124.86 (10.3%); £3,771,845.67 -> £3,382,124.93 (10.3%); £3,771,845.89 -> £3,382,125.00 (10.3%); £3,771,846.12 -> £3,382,125.07 (10.3%); £3,771,846.35 -> £3,382,125.14 (10.3%); £3,771,846.57 -> £3,382,125.40 (10.3%); £3,771,846.80 -> £3,382,125.65 (10.3%); £3,771,847.02 -> £3,382,125.89 (10.3%); £3,771,847.25 -> £3,382,126.12 (10.3%); £3,771,847.47 -> £3,382,126.35 (10.3%); £3,771,847.70 -> £3,382,126.59 (10.3%); £3,771,847.93 -> £3,382,126.82 (10.3%); £3,771,848.16 -> £3,382,127.05 (10.3%); £3,771,848.39 -> £3,382,127.28 (10.3%); £3,771,848.61 -> £3,382,127.51 (10.3%); £3,771,848.84 -> £3,382,127.74 (10.3%); £3,771,849.07 -> £3,382,127.78 (10.3%); £3,771,849.28 -> £3,382,127.82 (10.3%); £3,771,849.50 -> £3,382,127.86 (10.3%); £3,771,849.69 -> £3,382,127.90 (10.3%); £3,771,849.87 -> £3,382,127.93 (10.3%); £3,771,850.00 -> £3,382,127.97 (10.3%); £3,771,850.14 -> £3,382,128.01 (10.3%); £3,771,850.27 -> £3,382,128.05 (10.3%); £3,771,850.40 -> £3,382,128.08 (10.3%); £3,771,850.54 -> £3,382,128.12 (10.3%); £3,771,850.68 -> £3,382,128.15 (10.3%); £3,771,850.81 -> £3,382,128.19 (10.3%); £3,771,850.94 -> £3,382,128.23 (10.3%); £3,771,851.08 -> £3,382,128.26 (10.3%); £3,771,851.22 -> £3,382,128.30 (10.3%); £3,771,851.35 -> £3,382,128.33 (10.3%); £3,771,851.49 -> £3,382,128.55 (10.3%); £3,771,851.63 -> £3,382,128.76 (10.3%); £3,771,851.78 -> £3,382,128.98 (10.3%); £3,771,851.94 -> £3,382,129.20 (10.3%); £3,771,852.12 -> £3,382,129.42 (10.3%); £3,771,852.32 -> £3,382,129.65 (10.3%); £3,771,852.53 -> £3,382,129.88 (10.3%); £3,771,852.75 -> £3,382,130.10 (10.3%); £3,771,852.98 -> £3,382,130.15 (10.3%); £3,771,853.21 -> £3,382,130.20 (10.3%); £3,771,853.44 -> £3,382,130.25 (10.3%); £3,771,853.66 -> £3,382,130.30 (10.3%); £3,771,853.87 -> £3,382,130.35 (10.3%); £3,771,854.10 -> £3,382,130.40 (10.3%); £3,771,854.33 -> £3,382,130.45 (10.3%); £3,771,854.56 -> £3,382,130.50 (10.3%); £3,771,854.78 -> £3,382,130.54 (10.3%); £3,771,855.01 -> £3,382,130.59 (10.3%); £3,771,855.23 -> £3,382,130.63 (10.3%); £3,771,855.46 -> £3,382,130.68 (10.3%); £3,771,855.70 -> £3,382,130.73 (10.3%); £3,771,855.93 -> £3,382,130.94 (10.3%); £3,771,856.15 -> £3,382,131.17 (10.3%); £3,771,856.38 -> £3,382,131.38 (10.3%); £3,771,856.61 -> £3,382,131.60 (10.3%); £3,771,856.83 -> £3,382,131.82 (10.3%); £3,771,857.05 -> £3,382,132.05 (10.3%); £3,771,857.28 -> £3,382,132.27 (10.3%); £3,771,857.49 -> £3,382,132.49 (10.3%); £3,771,857.72 -> £3,382,132.71 (10.3%); £3,771,857.95 -> £3,382,132.93 (10.3%); £3,771,858.19 -> £3,382,133.14 (10.3%); £3,771,858.41 -> £3,382,133.18 (10.3%); £3,771,858.64 -> £3,382,133.22 (10.3%); £3,771,858.85 -> £3,382,133.26 (10.3%); £3,771,859.04 -> £3,382,133.30 (10.3%); £3,771,859.22 -> £3,382,133.33 (10.3%); £3,771,859.37 -> £3,382,133.37 (10.3%); £3,771,859.53 -> £3,382,133.41 (10.3%); £3,771,859.68 -> £3,382,133.45 (10.3%); £3,771,859.84 -> £3,382,133.48 (10.3%); £3,771,859.99 -> £3,382,133.52 (10.3%); £3,771,860.15 -> £3,382,133.56 (10.3%); £3,771,860.30 -> £3,382,133.59 (10.3%); £3,771,860.46 -> £3,382,133.63 (10.3%); £3,771,860.61 -> £3,382,133.67 (10.3%); £3,771,860.76 -> £3,382,133.71 (10.3%); £3,771,860.92 -> £3,382,133.75 (10.3%); £3,771,861.08 -> £3,382,133.95 (10.3%); £3,771,861.23 -> £3,382,134.16 (10.3%); £3,771,861.40 -> £3,382,134.37 (10.3%); £3,771,861.59 -> £3,382,134.61 (10.3%); £3,771,861.79 -> £3,382,134.86 (10.3%); £3,771,862.02 -> £3,382,135.14 (10.3%); £3,771,862.26 -> £3,382,135.44 (10.3%); £3,771,862.52 -> £3,382,135.76 (10.3%); £3,771,862.78 -> £3,382,135.89 (10.3%); £3,771,863.04 -> £3,382,136.02 (10.3%); £3,771,863.31 -> £3,382,136.15 (10.3%); £3,771,863.56 -> £3,382,136.28 (10.3%); £3,771,863.82 -> £3,382,136.41 (10.3%); £3,771,864.08 -> £3,382,136.53 (10.3%); £3,771,864.34 -> £3,382,136.65 (10.3%); £3,771,864.60 -> £3,382,136.76 (10.3%); £3,771,864.86 -> £3,382,136.88 (10.3%); £3,771,865.12 -> £3,382,137.00 (10.3%); £3,771,865.37 -> £3,382,137.11 (10.3%); £3,771,865.64 -> £3,382,137.23 (10.3%); £3,771,865.90 -> £3,382,137.34 (10.3%); £3,771,866.14 -> £3,382,137.64 (10.3%); £3,771,866.40 -> £3,382,137.92 (10.3%); £3,771,866.65 -> £3,382,138.17 (10.3%); £3,771,866.90 -> £3,382,138.40 (10.3%); £3,771,867.16 -> £3,382,138.62 (10.3%); £3,771,867.41 -> £3,382,138.83 (10.3%); £3,771,867.67 -> £3,382,139.05 (10.3%); £3,771,867.93 -> £3,382,139.27 (10.3%); £3,771,868.19 -> £3,382,139.49 (10.3%); £3,771,868.44 -> £3,382,139.69 (10.3%); £3,771,868.71 -> £3,382,139.89 (10.3%); £3,771,868.96 -> £3,382,139.93 (10.3%); £3,771,869.22 -> £3,382,139.97 (10.3%); £3,771,869.46 -> £3,382,140.01 (10.3%); £3,771,869.68 -> £3,382,140.05 (10.3%); £3,771,869.88 -> £3,382,140.08 (10.3%); £3,771,870.03 -> £3,382,140.12 (10.3%); £3,771,870.18 -> £3,382,140.16 (10.3%); £3,771,870.34 -> £3,382,140.20 (10.3%); £3,771,870.50 -> £3,382,140.24 (10.3%); £3,771,870.65 -> £3,382,140.27 (10.3%); £3,771,870.81 -> £3,382,140.31 (10.3%); £3,771,870.95 -> £3,382,140.35 (10.3%); £3,771,871.10 -> £3,382,140.39 (10.3%); £3,771,871.25 -> £3,382,140.42 (10.3%); £3,771,871.40 -> £3,382,140.46 (10.3%); £3,771,871.56 -> £3,382,140.50 (10.3%); £3,771,871.71 -> £3,382,140.68 (10.3%); £3,771,871.87 -> £3,382,140.86 (10.3%); £3,771,872.04 -> £3,382,141.05 (10.3%); £3,771,872.23 -> £3,382,141.25 (10.3%); £3,771,872.43 -> £3,382,141.48 (10.3%); £3,771,872.65 -> £3,382,141.72 (10.3%); £3,771,872.89 -> £3,382,141.99 (10.3%); £3,771,873.15 -> £3,382,142.27 (10.3%); £3,771,873.40 -> £3,382,142.39 (10.3%); £3,771,873.66 -> £3,382,142.52 (10.3%); £3,771,873.92 -> £3,382,142.65 (10.3%); £3,771,874.18 -> £3,382,142.78 (10.3%); £3,771,874.43 -> £3,382,142.91 (10.3%); £3,771,874.68 -> £3,382,143.04 (10.3%); £3,771,874.95 -> £3,382,143.16 (10.3%); £3,771,875.20 -> £3,382,143.28 (10.3%); £3,771,875.45 -> £3,382,143.39 (10.3%); £3,771,875.71 -> £3,382,143.51 (10.3%); £3,771,875.96 -> £3,382,143.62 (10.3%); £3,771,876.23 -> £3,382,143.74 (10.3%); £3,771,876.48 -> £3,382,143.85 (10.3%); £3,771,876.75 -> £3,382,144.12 (10.3%); £3,771,877.01 -> £3,382,144.38 (10.3%); £3,771,877.26 -> £3,382,144.60 (10.3%); £3,771,877.51 -> £3,382,144.80 (10.3%); £3,771,877.77 -> £3,382,144.99 (10.3%); £3,771,878.03 -> £3,382,145.18 (10.3%); £3,771,878.28 -> £3,382,145.37 (10.3%); £3,771,878.54 -> £3,382,145.55 (10.3%); £3,771,878.80 -> £3,382,145.73 (10.3%); £3,771,879.05 -> £3,382,145.91 (10.3%); £3,771,879.31 -> £3,382,146.09 (10.3%); £3,771,879.57 -> £3,382,146.13 (10.3%); £3,771,879.83 -> £3,382,146.17 (10.3%); £3,771,880.07 -> £3,382,146.21 (10.3%); £3,771,880.28 -> £3,382,146.25 (10.3%); £3,771,880.48 -> £3,382,146.28 (10.3%); £3,771,880.63 -> £3,382,146.32 (10.3%); £3,771,880.78 -> £3,382,146.36 (10.3%); £3,771,880.93 -> £3,382,146.39 (10.3%); £3,771,881.07 -> £3,382,146.43 (10.3%); £3,771,881.22 -> £3,382,146.47 (10.3%); £3,771,881.38 -> £3,382,146.50 (10.3%); £3,771,881.53 -> £3,382,146.54 (10.3%); £3,771,881.69 -> £3,382,146.58 (10.3%); £3,771,881.83 -> £3,382,146.62 (10.3%); £3,771,881.99 -> £3,382,146.65 (10.3%); £3,771,882.14 -> £3,382,146.69 (10.3%); £3,771,882.29 -> £3,382,146.89 (10.3%); £3,771,882.45 -> £3,382,147.10 (10.3%); £3,771,882.62 -> £3,382,147.31 (10.3%); £3,771,882.81 -> £3,382,147.54 (10.3%); £3,771,883.02 -> £3,382,147.79 (10.3%); £3,771,883.23 -> £3,382,148.05 (10.3%); £3,771,883.47 -> £3,382,148.35 (10.3%); £3,771,883.72 -> £3,382,148.67 (10.3%); £3,771,883.97 -> £3,382,148.80 (10.3%); £3,771,884.23 -> £3,382,148.92 (10.3%); £3,771,884.48 -> £3,382,149.06 (10.3%); £3,771,884.74 -> £3,382,149.19 (10.3%); £3,771,885.01 -> £3,382,149.31 (10.3%); £3,771,885.27 -> £3,382,149.44 (10.3%); £3,771,885.52 -> £3,382,149.55 (10.3%); £3,771,885.78 -> £3,382,149.67 (10.3%); £3,771,886.05 -> £3,382,149.79 (10.3%); £3,771,886.29 -> £3,382,149.90 (10.3%); £3,771,886.55 -> £3,382,150.02 (10.3%); £3,771,886.80 -> £3,382,150.13 (10.3%); £3,771,887.06 -> £3,382,150.24 (10.3%); £3,771,887.32 -> £3,382,150.55 (10.3%); £3,771,887.58 -> £3,382,150.83 (10.3%); £3,771,887.84 -> £3,382,151.07 (10.3%); £3,771,888.10 -> £3,382,151.29 (10.3%); £3,771,888.35 -> £3,382,151.51 (10.3%); £3,771,888.61 -> £3,382,151.72 (10.3%); £3,771,888.86 -> £3,382,151.94 (10.3%); £3,771,889.12 -> £3,382,152.14 (10.3%); £3,771,889.37 -> £3,382,152.35 (10.3%); £3,771,889.63 -> £3,382,152.56 (10.3%); £3,771,889.88 -> £3,382,152.77 (10.3%); £3,771,890.14 -> £3,382,152.81 (10.3%); £3,771,890.39 -> £3,382,152.85 (10.3%); £3,771,890.63 -> £3,382,152.89 (10.3%); £3,771,890.85 -> £3,382,152.93 (10.3%); £3,771,891.04 -> £3,382,152.96 (10.3%); £3,771,891.20 -> £3,382,153.00 (10.3%); £3,771,891.35 -> £3,382,153.04 (10.3%); £3,771,891.51 -> £3,382,153.08 (10.3%); £3,771,891.65 -> £3,382,153.12 (10.3%); £3,771,891.80 -> £3,382,153.15 (10.3%); £3,771,891.96 -> £3,382,153.19 (10.3%); £3,771,892.11 -> £3,382,153.23 (10.3%); £3,771,892.26 -> £3,382,153.26 (10.3%); £3,771,892.41 -> £3,382,153.30 (10.3%); £3,771,892.57 -> £3,382,153.34 (10.3%); £3,771,892.72 -> £3,382,153.38 (10.3%); £3,771,892.87 -> £3,382,153.57 (10.3%); £3,771,893.02 -> £3,382,153.75 (10.3%); £3,771,893.19 -> £3,382,153.95 (10.3%); £3,771,893.38 -> £3,382,154.16 (10.3%); £3,771,893.58 -> £3,382,154.40 (10.3%); £3,771,893.79 -> £3,382,154.65 (10.3%); £3,771,894.03 -> £3,382,154.93 (10.3%); £3,771,894.30 -> £3,382,155.21 (10.3%); £3,771,894.55 -> £3,382,155.33 (10.3%); £3,771,894.82 -> £3,382,155.45 (10.3%); £3,771,895.07 -> £3,382,155.58 (10.3%); £3,771,895.32 -> £3,382,155.70 (10.3%); £3,771,895.57 -> £3,382,155.83 (10.3%); £3,771,895.82 -> £3,382,155.95 (10.3%); £3,771,896.08 -> £3,382,156.07 (10.3%); £3,771,896.33 -> £3,382,156.18 (10.3%); £3,771,896.59 -> £3,382,156.30 (10.3%); £3,771,896.84 -> £3,382,156.41 (10.3%); £3,771,897.10 -> £3,382,156.52 (10.3%); £3,771,897.36 -> £3,382,156.63 (10.3%); £3,771,897.61 -> £3,382,156.74 (10.3%); £3,771,897.87 -> £3,382,157.02 (10.3%); £3,771,898.13 -> £3,382,157.28 (10.3%); £3,771,898.38 -> £3,382,157.52 (10.3%); £3,771,898.64 -> £3,382,157.74 (10.3%); £3,771,898.89 -> £3,382,157.94 (10.3%); £3,771,899.15 -> £3,382,158.15 (10.3%); £3,771,899.40 -> £3,382,158.35 (10.3%); £3,771,899.65 -> £3,382,158.55 (10.3%); £3,771,899.92 -> £3,382,158.75 (10.3%); £3,771,900.18 -> £3,382,158.94 (10.3%); £3,771,900.43 -> £3,382,159.12 (10.3%); £3,771,900.68 -> £3,382,159.16 (10.3%); £3,771,900.93 -> £3,382,159.20 (10.3%); £3,771,901.17 -> £3,382,159.24 (10.3%); £3,771,901.38 -> £3,382,159.28 (10.3%); £3,771,901.59 -> £3,382,159.32 (10.3%); £3,771,901.73 -> £3,382,159.35 (10.3%); £3,771,901.89 -> £3,382,159.39 (10.3%); £3,771,902.04 -> £3,382,159.43 (10.3%); £3,771,902.19 -> £3,382,159.47 (10.3%); £3,771,902.34 -> £3,382,159.51 (10.3%); £3,771,902.50 -> £3,382,159.54 (10.3%); £3,771,902.65 -> £3,382,159.58 (10.3%); £3,771,902.80 -> £3,382,159.62 (10.3%); £3,771,902.96 -> £3,382,159.66 (10.3%); £3,771,903.11 -> £3,382,159.69 (10.3%); £3,771,903.26 -> £3,382,159.73 (10.3%); £3,771,903.41 -> £3,382,159.93 (10.3%); £3,771,903.57 -> £3,382,160.12 (10.3%); £3,771,903.74 -> £3,382,160.32 (10.3%); £3,771,903.93 -> £3,382,160.54 (10.3%); £3,771,904.13 -> £3,382,160.77 (10.3%); £3,771,904.34 -> £3,382,161.03 (10.3%); £3,771,904.58 -> £3,382,161.31 (10.3%); £3,771,904.85 -> £3,382,161.60 (10.3%); £3,771,905.11 -> £3,382,161.72 (10.3%); £3,771,905.37 -> £3,382,161.85 (10.3%); £3,771,905.62 -> £3,382,161.97 (10.3%); £3,771,905.88 -> £3,382,162.10 (10.3%); £3,771,906.14 -> £3,382,162.22 (10.3%); £3,771,906.39 -> £3,382,162.34 (10.3%); £3,771,906.65 -> £3,382,162.46 (10.3%); £3,771,906.90 -> £3,382,162.58 (10.3%); £3,771,907.15 -> £3,382,162.70 (10.3%); £3,771,907.41 -> £3,382,162.82 (10.3%); £3,771,907.67 -> £3,382,162.93 (10.3%); £3,771,907.92 -> £3,382,163.04 (10.3%); £3,771,908.18 -> £3,382,163.15 (10.3%); £3,771,908.44 -> £3,382,163.43 (10.3%); £3,771,908.68 -> £3,382,163.69 (10.3%); £3,771,908.94 -> £3,382,163.92 (10.3%); £3,771,909.19 -> £3,382,164.13 (10.3%); £3,771,909.45 -> £3,382,164.34 (10.3%); £3,771,909.70 -> £3,382,164.54 (10.3%); £3,771,909.95 -> £3,382,164.73 (10.3%); £3,771,910.21 -> £3,382,164.93 (10.3%); £3,771,910.47 -> £3,382,165.12 (10.3%); £3,771,910.72 -> £3,382,165.30 (10.3%); £3,771,910.96 -> £3,382,165.48 (10.3%); £3,771,911.23 -> £3,382,165.53 (10.3%); £3,771,911.48 -> £3,382,165.57 (10.3%); £3,771,911.72 -> £3,382,165.61 (10.3%); £3,771,911.93 -> £3,382,165.64 (10.3%); £3,771,912.13 -> £3,382,165.68 (10.3%); £3,771,912.26 -> £3,382,165.72 (10.3%); £3,771,912.39 -> £3,382,165.76 (10.3%); £3,771,912.52 -> £3,382,165.79 (10.3%); £3,771,912.66 -> £3,382,165.83 (10.3%); £3,771,912.79 -> £3,382,165.87 (10.3%); £3,771,912.92 -> £3,382,165.90 (10.3%); £3,771,913.06 -> £3,382,165.94 (10.3%); £3,771,913.20 -> £3,382,165.98 (10.3%); £3,771,913.33 -> £3,382,166.02 (10.3%); £3,771,913.46 -> £3,382,166.05 (10.3%); £3,771,913.59 -> £3,382,166.09 (10.3%); £3,771,913.73 -> £3,382,166.26 (10.3%); £3,771,913.87 -> £3,382,166.43 (10.3%); £3,771,914.02 -> £3,382,166.61 (10.3%); £3,771,914.18 -> £3,382,166.79 (10.3%); £3,771,914.36 -> £3,382,166.99 (10.3%); £3,771,914.56 -> £3,382,167.20 (10.3%); £3,771,914.77 -> £3,382,167.42 (10.3%); £3,771,914.99 -> £3,382,167.65 (10.3%); £3,771,915.22 -> £3,382,167.74 (10.3%); £3,771,915.44 -> £3,382,167.83 (10.3%); £3,771,915.66 -> £3,382,167.92 (10.3%); £3,771,915.88 -> £3,382,168.01 (10.3%); £3,771,916.11 -> £3,382,168.09 (10.3%); £3,771,916.34 -> £3,382,168.17 (10.3%); £3,771,916.56 -> £3,382,168.24 (10.3%); £3,771,916.78 -> £3,382,168.31 (10.3%); £3,771,917.01 -> £3,382,168.38 (10.3%); £3,771,917.24 -> £3,382,168.45 (10.3%); £3,771,917.47 -> £3,382,168.52 (10.3%); £3,771,917.70 -> £3,382,168.59 (10.3%); £3,771,917.92 -> £3,382,168.66 (10.3%); £3,771,918.14 -> £3,382,168.87 (10.3%); £3,771,918.37 -> £3,382,169.08 (10.3%); £3,771,918.59 -> £3,382,169.27 (10.3%); £3,771,918.83 -> £3,382,169.45 (10.3%); £3,771,919.05 -> £3,382,169.63 (10.3%); £3,771,919.27 -> £3,382,169.82 (10.3%); £3,771,919.49 -> £3,382,170.00 (10.3%); £3,771,919.72 -> £3,382,170.19 (10.3%); £3,771,919.93 -> £3,382,170.37 (10.3%); £3,771,920.16 -> £3,382,170.55 (10.3%); £3,771,920.38 -> £3,382,170.72 (10.3%); £3,771,920.60 -> £3,382,170.76 (10.3%); £3,771,920.82 -> £3,382,170.80 (10.3%); £3,771,921.03 -> £3,382,170.84 (10.3%); £3,771,921.22 -> £3,382,170.88 (10.3%); £3,771,921.40 -> £3,382,170.91 (10.3%); £3,771,921.53 -> £3,382,170.95 (10.3%); £3,771,921.66 -> £3,382,170.99 (10.3%); £3,771,921.80 -> £3,382,171.03 (10.3%); £3,771,921.93 -> £3,382,171.07 (10.3%); £3,771,922.07 -> £3,382,171.11 (10.3%); £3,771,922.20 -> £3,382,171.14 (10.3%); £3,771,922.34 -> £3,382,171.18 (10.3%); £3,771,922.48 -> £3,382,171.22 (10.3%); £3,771,922.61 -> £3,382,171.26 (10.3%); £3,771,922.75 -> £3,382,171.29 (10.3%); £3,771,922.88 -> £3,382,171.33 (10.3%); £3,771,923.02 -> £3,382,171.49 (10.3%); £3,771,923.15 -> £3,382,171.65 (10.3%); £3,771,923.30 -> £3,382,171.82 (10.3%); £3,771,923.47 -> £3,382,171.98 (10.3%); £3,771,923.65 -> £3,382,172.15 (10.3%); £3,771,923.85 -> £3,382,172.31 (10.3%); £3,771,924.05 -> £3,382,172.48 (10.3%); £3,771,924.27 -> £3,382,172.65 (10.3%); £3,771,924.51 -> £3,382,172.70 (10.3%); £3,771,924.73 -> £3,382,172.75 (10.3%); £3,771,924.96 -> £3,382,172.80 (10.3%); £3,771,925.18 -> £3,382,172.85 (10.3%); £3,771,925.40 -> £3,382,172.89 (10.3%); £3,771,925.63 -> £3,382,172.94 (10.3%); £3,771,925.85 -> £3,382,172.99 (10.3%); £3,771,926.07 -> £3,382,173.03 (10.3%); £3,771,926.29 -> £3,382,173.08 (10.3%); £3,771,926.52 -> £3,382,173.12 (10.3%); £3,771,926.75 -> £3,382,173.17 (10.3%); £3,771,926.97 -> £3,382,173.22 (10.3%); £3,771,927.19 -> £3,382,173.26 (10.3%); £3,771,927.42 -> £3,382,173.44 (10.3%); £3,771,927.64 -> £3,382,173.62 (10.3%); £3,771,927.87 -> £3,382,173.79 (10.3%); £3,771,928.10 -> £3,382,173.96 (10.3%); £3,771,928.32 -> £3,382,174.13 (10.3%); £3,771,928.53 -> £3,382,174.30 (10.3%); £3,771,928.75 -> £3,382,174.47 (10.3%); £3,771,928.96 -> £3,382,174.63 (10.3%); £3,771,929.19 -> £3,382,174.80 (10.3%); £3,771,929.42 -> £3,382,174.96 (10.3%); £3,771,929.64 -> £3,382,175.13 (10.3%); £3,771,929.87 -> £3,382,175.17 (10.3%); £3,771,930.09 -> £3,382,175.21 (10.3%); £3,771,930.30 -> £3,382,175.24 (10.3%); £3,771,930.49 -> £3,382,175.28 (10.3%); £3,771,930.67 -> £3,382,175.31 (10.3%); £3,771,930.82 -> £3,382,175.35 (10.3%); £3,771,930.97 -> £3,382,175.39 (10.3%); £3,771,931.12 -> £3,382,175.43 (10.3%); £3,771,931.28 -> £3,382,175.47 (10.3%); £3,771,931.43 -> £3,382,175.50 (10.3%); £3,771,931.58 -> £3,382,175.54 (10.3%); £3,771,931.73 -> £3,382,175.58 (10.3%); £3,771,931.88 -> £3,382,175.62 (10.3%); £3,771,932.04 -> £3,382,175.65 (10.3%); £3,771,932.19 -> £3,382,175.69 (10.3%); £3,771,932.34 -> £3,382,175.73 (10.3%); £3,771,932.48 -> £3,382,175.91 (10.3%); £3,771,932.63 -> £3,382,176.10 (10.3%); £3,771,932.80 -> £3,382,176.29 (10.3%); £3,771,932.99 -> £3,382,176.48 (10.3%); £3,771,933.20 -> £3,382,176.70 (10.3%); £3,771,933.42 -> £3,382,176.94 (10.3%); £3,771,933.66 -> £3,382,177.20 (10.3%); £3,771,933.91 -> £3,382,177.47 (10.3%); £3,771,934.16 -> £3,382,177.59 (10.3%); £3,771,934.41 -> £3,382,177.72 (10.3%); £3,771,934.67 -> £3,382,177.84 (10.3%); £3,771,934.93 -> £3,382,177.96 (10.3%); £3,771,935.17 -> £3,382,178.09 (10.3%); £3,771,935.44 -> £3,382,178.21 (10.3%); £3,771,935.68 -> £3,382,178.32 (10.3%); £3,771,935.93 -> £3,382,178.43 (10.3%); £3,771,936.18 -> £3,382,178.55 (10.3%); £3,771,936.44 -> £3,382,178.66 (10.3%); £3,771,936.69 -> £3,382,178.77 (10.3%); £3,771,936.95 -> £3,382,178.87 (10.3%); £3,771,937.20 -> £3,382,178.98 (10.3%); £3,771,937.45 -> £3,382,179.23 (10.3%); £3,771,937.70 -> £3,382,179.47 (10.3%); £3,771,937.96 -> £3,382,179.68 (10.3%); £3,771,938.22 -> £3,382,179.87 (10.3%); £3,771,938.47 -> £3,382,180.05 (10.3%); £3,771,938.73 -> £3,382,180.25 (10.3%); £3,771,938.97 -> £3,382,180.44 (10.3%); £3,771,939.22 -> £3,382,180.63 (10.3%); £3,771,939.47 -> £3,382,180.82 (10.3%); £3,771,939.73 -> £3,382,180.99 (10.3%); £3,771,939.99 -> £3,382,181.16 (10.3%); £3,771,940.24 -> £3,382,181.20 (10.3%); £3,771,940.50 -> £3,382,181.25 (10.3%); £3,771,940.72 -> £3,382,181.29 (10.3%); £3,771,940.94 -> £3,382,181.32 (10.3%); £3,771,941.13 -> £3,382,181.36 (10.3%); £3,771,941.28 -> £3,382,181.40 (10.3%); £3,771,941.43 -> £3,382,181.44 (10.3%); £3,771,941.58 -> £3,382,181.47 (10.3%); £3,771,941.73 -> £3,382,181.51 (10.3%); £3,771,941.88 -> £3,382,181.55 (10.3%); £3,771,942.03 -> £3,382,181.58 (10.3%); £3,771,942.18 -> £3,382,181.62 (10.3%); £3,771,942.33 -> £3,382,181.66 (10.3%); £3,771,942.48 -> £3,382,181.70 (10.3%); £3,771,942.63 -> £3,382,181.74 (10.3%); £3,771,942.78 -> £3,382,181.78 (10.3%); £3,771,942.92 -> £3,382,181.91 (10.3%); £3,771,943.08 -> £3,382,182.06 (10.3%); £3,771,943.25 -> £3,382,182.22 (10.3%); £3,771,943.44 -> £3,382,182.39 (10.3%); £3,771,943.64 -> £3,382,182.59 (10.3%); £3,771,943.85 -> £3,382,182.80 (10.3%); £3,771,944.09 -> £3,382,183.04 (10.3%); £3,771,944.34 -> £3,382,183.28 (10.3%); £3,771,944.59 -> £3,382,183.40 (10.3%); £3,771,944.84 -> £3,382,183.53 (10.3%); £3,771,945.09 -> £3,382,183.66 (10.3%); £3,771,945.35 -> £3,382,183.79 (10.3%); £3,771,945.60 -> £3,382,183.91 (10.3%); £3,771,945.85 -> £3,382,184.04 (10.3%); £3,771,946.10 -> £3,382,184.16 (10.3%); £3,771,946.35 -> £3,382,184.28 (10.3%); £3,771,946.60 -> £3,382,184.39 (10.3%); £3,771,946.85 -> £3,382,184.50 (10.3%); £3,771,947.11 -> £3,382,184.61 (10.3%); £3,771,947.36 -> £3,382,184.72 (10.3%); £3,771,947.62 -> £3,382,184.83 (10.3%); £3,771,947.87 -> £3,382,185.07 (10.3%); £3,771,948.13 -> £3,382,185.29 (10.3%); £3,771,948.38 -> £3,382,185.48 (10.3%); £3,771,948.64 -> £3,382,185.64 (10.3%); £3,771,948.90 -> £3,382,185.81 (10.3%); £3,771,949.16 -> £3,382,185.97 (10.3%); £3,771,949.41 -> £3,382,186.13 (10.3%); £3,771,949.66 -> £3,382,186.28 (10.3%); £3,771,949.90 -> £3,382,186.43 (10.3%); £3,771,950.14 -> £3,382,186.57 (10.3%); £3,771,950.39 -> £3,382,186.71 (10.3%); £3,771,950.64 -> £3,382,186.75 (10.3%); £3,771,950.89 -> £3,382,186.79 (10.3%); £3,771,951.13 -> £3,382,186.83 (10.3%); £3,771,951.35 -> £3,382,186.87 (10.3%); £3,771,951.54 -> £3,382,186.90 (10.3%); £3,771,951.69 -> £3,382,186.94 (10.3%); £3,771,951.84 -> £3,382,186.98 (10.3%); £3,771,952.00 -> £3,382,187.02 (10.3%); £3,771,952.15 -> £3,382,187.06 (10.3%); £3,771,952.30 -> £3,382,187.09 (10.3%); £3,771,952.45 -> £3,382,187.13 (10.3%); £3,771,952.60 -> £3,382,187.17 (10.3%); £3,771,952.75 -> £3,382,187.21 (10.3%); £3,771,952.90 -> £3,382,187.24 (10.3%); £3,771,953.05 -> £3,382,187.28 (10.3%); £3,771,953.21 -> £3,382,187.32 (10.3%); £3,771,953.36 -> £3,382,187.43 (10.3%); £3,771,953.51 -> £3,382,187.54 (10.3%); £3,771,953.68 -> £3,382,187.67 (10.3%); £3,771,953.86 -> £3,382,187.80 (10.3%); £3,771,954.05 -> £3,382,187.97 (10.3%); £3,771,954.27 -> £3,382,188.16 (10.3%); £3,771,954.51 -> £3,382,188.36 (10.3%); £3,771,954.76 -> £3,382,188.58 (10.3%); £3,771,955.01 -> £3,382,188.71 (10.3%); £3,771,955.26 -> £3,382,188.84 (10.3%); £3,771,955.52 -> £3,382,188.97 (10.3%); £3,771,955.77 -> £3,382,189.09 (10.3%); £3,771,956.02 -> £3,382,189.22 (10.3%); £3,771,956.27 -> £3,382,189.34 (10.3%); £3,771,956.52 -> £3,382,189.46 (10.3%); £3,771,956.78 -> £3,382,189.58 (10.3%); £3,771,957.03 -> £3,382,189.70 (10.3%); £3,771,957.27 -> £3,382,189.81 (10.3%); £3,771,957.52 -> £3,382,189.93 (10.3%); £3,771,957.77 -> £3,382,190.05 (10.3%); £3,771,958.01 -> £3,382,190.15 (10.3%); £3,771,958.26 -> £3,382,190.36 (10.3%); £3,771,958.52 -> £3,382,190.55 (10.3%); £3,771,958.76 -> £3,382,190.71 (10.3%); £3,771,959.01 -> £3,382,190.86 (10.3%); £3,771,959.26 -> £3,382,190.99 (10.3%); £3,771,959.50 -> £3,382,191.12 (10.3%); £3,771,959.75 -> £3,382,191.25 (10.3%); £3,771,960.01 -> £3,382,191.37 (10.3%); £3,771,960.25 -> £3,382,191.50 (10.3%); £3,771,960.50 -> £3,382,191.61 (10.3%); £3,771,960.74 -> £3,382,191.72 (10.3%); £3,771,960.99 -> £3,382,191.76 (10.3%); £3,771,961.25 -> £3,382,191.81 (10.3%); £3,771,961.49 -> £3,382,191.85 (10.3%); £3,771,961.70 -> £3,382,191.88 (10.3%); £3,771,961.89 -> £3,382,191.92 (10.3%); £3,771,962.04 -> £3,382,191.96 (10.3%); £3,771,962.19 -> £3,382,191.99 (10.3%); £3,771,962.35 -> £3,382,192.03 (10.3%); £3,771,962.50 -> £3,382,192.07 (10.3%); £3,771,962.65 -> £3,382,192.11 (10.3%); £3,771,962.80 -> £3,382,192.14 (10.3%); £3,771,962.95 -> £3,382,192.18 (10.3%); £3,771,963.10 -> £3,382,192.22 (10.3%); £3,771,963.25 -> £3,382,192.26 (10.3%); £3,771,963.41 -> £3,382,192.30 (10.3%); £3,771,963.56 -> £3,382,192.34 (10.3%); £3,771,963.71 -> £3,382,192.44 (10.3%); £3,771,963.85 -> £3,382,192.55 (10.3%); £3,771,964.02 -> £3,382,192.68 (10.3%); £3,771,964.20 -> £3,382,192.81 (10.3%); £3,771,964.40 -> £3,382,192.97 (10.3%); £3,771,964.62 -> £3,382,193.15 (10.3%); £3,771,964.85 -> £3,382,193.34 (10.3%); £3,771,965.10 -> £3,382,193.56 (10.3%); £3,771,965.36 -> £3,382,193.69 (10.3%); £3,771,965.61 -> £3,382,193.81 (10.3%); £3,771,965.86 -> £3,382,193.93 (10.3%); £3,771,966.11 -> £3,382,194.06 (10.3%); £3,771,966.36 -> £3,382,194.18 (10.3%); £3,771,966.62 -> £3,382,194.30 (10.3%); £3,771,966.87 -> £3,382,194.42 (10.3%); £3,771,967.12 -> £3,382,194.53 (10.3%); £3,771,967.37 -> £3,382,194.65 (10.3%); £3,771,967.62 -> £3,382,194.76 (10.3%); £3,771,967.87 -> £3,382,194.88 (10.3%); £3,771,968.13 -> £3,382,194.99 (10.3%); £3,771,968.39 -> £3,382,195.09 (10.3%); £3,771,968.64 -> £3,382,195.29 (10.3%); £3,771,968.90 -> £3,382,195.47 (10.3%); £3,771,969.15 -> £3,382,195.63 (10.3%); £3,771,969.41 -> £3,382,195.77 (10.3%); £3,771,969.67 -> £3,382,195.91 (10.3%); £3,771,969.92 -> £3,382,196.03 (10.3%); £3,771,970.16 -> £3,382,196.16 (10.3%); £3,771,970.42 -> £3,382,196.28 (10.3%); £3,771,970.67 -> £3,382,196.40 (10.3%); £3,771,970.92 -> £3,382,196.51 (10.3%); £3,771,971.17 -> £3,382,196.62 (10.3%); £3,771,971.42 -> £3,382,196.66 (10.3%); £3,771,971.68 -> £3,382,196.71 (10.3%); £3,771,971.90 -> £3,382,196.74 (10.3%); £3,771,972.12 -> £3,382,196.78 (10.3%); £3,771,972.32 -> £3,382,196.82 (10.3%); £3,771,972.47 -> £3,382,196.86 (10.3%); £3,771,972.62 -> £3,382,196.90 (10.3%); £3,771,972.77 -> £3,382,196.93 (10.3%); £3,771,972.92 -> £3,382,196.97 (10.3%); £3,771,973.07 -> £3,382,197.01 (10.3%); £3,771,973.22 -> £3,382,197.05 (10.3%); £3,771,973.38 -> £3,382,197.09 (10.3%); £3,771,973.53 -> £3,382,197.12 (10.3%); £3,771,973.68 -> £3,382,197.16 (10.3%); £3,771,973.83 -> £3,382,197.20 (10.3%); £3,771,973.98 -> £3,382,197.24 (10.3%); £3,771,974.13 -> £3,382,197.39 (10.3%); £3,771,974.28 -> £3,382,197.54 (10.3%); £3,771,974.45 -> £3,382,197.70 (10.3%); £3,771,974.63 -> £3,382,197.88 (10.3%); £3,771,974.84 -> £3,382,198.08 (10.3%); £3,771,975.06 -> £3,382,198.29 (10.3%); £3,771,975.29 -> £3,382,198.52 (10.3%); £3,771,975.55 -> £3,382,198.76 (10.3%); £3,771,975.81 -> £3,382,198.89 (10.3%); £3,771,976.05 -> £3,382,199.02 (10.3%); £3,771,976.30 -> £3,382,199.15 (10.3%); £3,771,976.55 -> £3,382,199.29 (10.3%); £3,771,976.80 -> £3,382,199.43 (10.3%); £3,771,977.05 -> £3,382,199.55 (10.3%); £3,771,977.30 -> £3,382,199.68 (10.3%); £3,771,977.55 -> £3,382,199.80 (10.3%); £3,771,977.81 -> £3,382,199.92 (10.3%); £3,771,978.06 -> £3,382,200.04 (10.3%); £3,771,978.31 -> £3,382,200.16 (10.3%); £3,771,978.56 -> £3,382,200.27 (10.3%); £3,771,978.81 -> £3,382,200.38 (10.3%); £3,771,979.06 -> £3,382,200.61 (10.3%); £3,771,979.32 -> £3,382,200.83 (10.3%); £3,771,979.57 -> £3,382,201.01 (10.3%); £3,771,979.82 -> £3,382,201.18 (10.3%); £3,771,980.07 -> £3,382,201.34 (10.3%); £3,771,980.32 -> £3,382,201.50 (10.3%); £3,771,980.57 -> £3,382,201.64 (10.3%); £3,771,980.82 -> £3,382,201.79 (10.3%); £3,771,981.08 -> £3,382,201.93 (10.3%); £3,771,981.33 -> £3,382,202.07 (10.3%); £3,771,981.59 -> £3,382,202.21 (10.3%); £3,771,981.84 -> £3,382,202.25 (10.3%); £3,771,982.09 -> £3,382,202.29 (10.3%); £3,771,982.32 -> £3,382,202.33 (10.3%); £3,771,982.53 -> £3,382,202.36 (10.3%); £3,771,982.72 -> £3,382,202.40 (10.3%); £3,771,982.86 -> £3,382,202.44 (10.3%); £3,771,982.99 -> £3,382,202.48 (10.3%); £3,771,983.12 -> £3,382,202.51 (10.3%); £3,771,983.26 -> £3,382,202.55 (10.3%); £3,771,983.40 -> £3,382,202.59 (10.3%); £3,771,983.53 -> £3,382,202.62 (10.3%); £3,771,983.67 -> £3,382,202.66 (10.3%); £3,771,983.81 -> £3,382,202.70 (10.3%); £3,771,983.94 -> £3,382,202.74 (10.3%); £3,771,984.07 -> £3,382,202.77 (10.3%); £3,771,984.21 -> £3,382,202.81 (10.3%); £3,771,984.35 -> £3,382,202.98 (10.3%); £3,771,984.49 -> £3,382,203.15 (10.3%); £3,771,984.63 -> £3,382,203.33 (10.3%); £3,771,984.80 -> £3,382,203.52 (10.3%); £3,771,984.98 -> £3,382,203.71 (10.3%); £3,771,985.18 -> £3,382,203.92 (10.3%); £3,771,985.39 -> £3,382,204.15 (10.3%); £3,771,985.61 -> £3,382,204.38 (10.3%); £3,771,985.84 -> £3,382,204.47 (10.3%); £3,771,986.06 -> £3,382,204.57 (10.3%); £3,771,986.28 -> £3,382,204.66 (10.3%); £3,771,986.51 -> £3,382,204.75 (10.3%); £3,771,986.74 -> £3,382,204.83 (10.3%); £3,771,986.96 -> £3,382,204.91 (10.3%); £3,771,987.18 -> £3,382,204.98 (10.3%); £3,771,987.41 -> £3,382,205.06 (10.3%); £3,771,987.62 -> £3,382,205.13 (10.3%); £3,771,987.84 -> £3,382,205.20 (10.3%); £3,771,988.06 -> £3,382,205.26 (10.3%); £3,771,988.28 -> £3,382,205.33 (10.3%); £3,771,988.49 -> £3,382,205.40 (10.3%); £3,771,988.72 -> £3,382,205.60 (10.3%); £3,771,988.95 -> £3,382,205.80 (10.3%); £3,771,989.17 -> £3,382,205.98 (10.3%); £3,771,989.40 -> £3,382,206.16 (10.3%); £3,771,989.62 -> £3,382,206.34 (10.3%); £3,771,989.86 -> £3,382,206.52 (10.3%); £3,771,990.07 -> £3,382,206.69 (10.3%); £3,771,990.30 -> £3,382,206.87 (10.3%); £3,771,990.52 -> £3,382,207.04 (10.3%); £3,771,990.74 -> £3,382,207.21 (10.3%); £3,771,990.97 -> £3,382,207.40 (10.3%); £3,771,991.19 -> £3,382,207.44 (10.3%); £3,771,991.41 -> £3,382,207.48 (10.3%); £3,771,991.61 -> £3,382,207.52 (10.3%); £3,771,991.80 -> £3,382,207.56 (10.3%); £3,771,991.98 -> £3,382,207.59 (10.3%); £3,771,992.11 -> £3,382,207.63 (10.3%); £3,771,992.25 -> £3,382,207.67 (10.3%); £3,771,992.38 -> £3,382,207.71 (10.3%); £3,771,992.51 -> £3,382,207.75 (10.3%); £3,771,992.65 -> £3,382,207.78 (10.3%); £3,771,992.79 -> £3,382,207.82 (10.3%); £3,771,992.92 -> £3,382,207.86 (10.3%); £3,771,993.05 -> £3,382,207.89 (10.3%); £3,771,993.19 -> £3,382,207.93 (10.3%); £3,771,993.33 -> £3,382,207.97 (10.3%); £3,771,993.47 -> £3,382,208.00 (10.3%); £3,771,993.60 -> £3,382,208.10 (10.3%); £3,771,993.74 -> £3,382,208.20 (10.3%); £3,771,993.89 -> £3,382,208.30 (10.3%); £3,771,994.06 -> £3,382,208.41 (10.3%); £3,771,994.24 -> £3,382,208.51 (10.3%); £3,771,994.44 -> £3,382,208.61 (10.3%); £3,771,994.65 -> £3,382,208.72 (10.3%); £3,771,994.88 -> £3,382,208.83 (10.3%); £3,771,995.11 -> £3,382,208.87 (10.3%); £3,771,995.33 -> £3,382,208.92 (10.3%); £3,771,995.55 -> £3,382,208.97 (10.3%); £3,771,995.78 -> £3,382,209.02 (10.3%); £3,771,996.00 -> £3,382,209.06 (10.3%); £3,771,996.23 -> £3,382,209.11 (10.3%); £3,771,996.46 -> £3,382,209.16 (10.3%); £3,771,996.69 -> £3,382,209.20 (10.3%); £3,771,996.91 -> £3,382,209.25 (10.3%); £3,771,997.14 -> £3,382,209.30 (10.3%); £3,771,997.37 -> £3,382,209.34 (10.3%); £3,771,997.60 -> £3,382,209.39 (10.3%); £3,771,997.83 -> £3,382,209.43 (10.3%); £3,771,998.05 -> £3,382,209.55 (10.3%); £3,771,998.27 -> £3,382,209.66 (10.3%); £3,771,998.50 -> £3,382,209.77 (10.3%); £3,771,998.73 -> £3,382,209.89 (10.3%); £3,771,998.96 -> £3,382,210.00 (10.3%); £3,771,999.18 -> £3,382,210.12 (10.3%); £3,771,999.40 -> £3,382,210.23 (10.3%); £3,771,999.63 -> £3,382,210.34 (10.3%); £3,771,999.85 -> £3,382,210.45 (10.3%); £3,772,000.07 -> £3,382,210.56 (10.3%); £3,772,000.30 -> £3,382,210.67 (10.3%); £3,772,000.53 -> £3,382,210.71 (10.3%); £3,772,000.75 -> £3,382,210.75 (10.3%); £3,772,000.97 -> £3,382,210.78 (10.3%); £3,772,001.17 -> £3,382,210.82 (10.3%); £3,772,001.34 -> £3,382,210.86 (10.3%); £3,772,001.50 -> £3,382,210.89 (10.3%); £3,772,001.65 -> £3,382,210.93 (10.3%); £3,772,001.81 -> £3,382,210.97 (10.3%); £3,772,001.96 -> £3,382,211.00 (10.3%); £3,772,002.11 -> £3,382,211.04 (10.3%); £3,772,002.26 -> £3,382,211.08 (10.3%); £3,772,002.42 -> £3,382,211.12 (10.3%); £3,772,002.57 -> £3,382,211.15 (10.3%); £3,772,002.72 -> £3,382,211.19 (10.3%); £3,772,002.87 -> £3,382,211.23 (10.3%); £3,772,003.03 -> £3,382,211.27 (10.3%); £3,772,003.18 -> £3,382,211.41 (10.3%); £3,772,003.34 -> £3,382,211.54 (10.3%); £3,772,003.51 -> £3,382,211.68 (10.3%); £3,772,003.70 -> £3,382,211.83 (10.3%); £3,772,003.90 -> £3,382,212.02 (10.3%); £3,772,004.13 -> £3,382,212.22 (10.3%); £3,772,004.37 -> £3,382,212.45 (10.3%); £3,772,004.63 -> £3,382,212.70 (10.3%); £3,772,004.88 -> £3,382,212.82 (10.3%); £3,772,005.14 -> £3,382,212.95 (10.3%); £3,772,005.39 -> £3,382,213.07 (10.3%); £3,772,005.64 -> £3,382,213.20 (10.3%); £3,772,005.89 -> £3,382,213.33 (10.3%); £3,772,006.14 -> £3,382,213.45 (10.3%); £3,772,006.39 -> £3,382,213.57 (10.3%); £3,772,006.65 -> £3,382,213.69 (10.3%); £3,772,006.92 -> £3,382,213.81 (10.3%); £3,772,007.18 -> £3,382,213.92 (10.3%); £3,772,007.43 -> £3,382,214.03 (10.3%); £3,772,007.69 -> £3,382,214.15 (10.3%); £3,772,007.95 -> £3,382,214.26 (10.3%); £3,772,008.21 -> £3,382,214.50 (10.3%); £3,772,008.47 -> £3,382,214.72 (10.3%); £3,772,008.73 -> £3,382,214.91 (10.3%); £3,772,008.97 -> £3,382,215.07 (10.3%); £3,772,009.24 -> £3,382,215.22 (10.3%); £3,772,009.50 -> £3,382,215.37 (10.3%); £3,772,009.75 -> £3,382,215.52 (10.3%); £3,772,010.00 -> £3,382,215.66 (10.3%); £3,772,010.26 -> £3,382,215.81 (10.3%); £3,772,010.51 -> £3,382,215.95 (10.3%); £3,772,010.77 -> £3,382,216.09 (10.3%); £3,772,011.03 -> £3,382,216.13 (10.3%); £3,772,011.29 -> £3,382,216.17 (10.3%); £3,772,011.52 -> £3,382,216.21 (10.3%); £3,772,011.74 -> £3,382,216.25 (10.3%); £3,772,011.93 -> £3,382,216.29 (10.3%); £3,772,012.09 -> £3,382,216.32 (10.3%); £3,772,012.25 -> £3,382,216.36 (10.3%); £3,772,012.41 -> £3,382,216.40 (10.3%); £3,772,012.56 -> £3,382,216.44 (10.3%); £3,772,012.71 -> £3,382,216.47 (10.3%); £3,772,012.86 -> £3,382,216.51 (10.3%); £3,772,013.02 -> £3,382,216.55 (10.3%); £3,772,013.17 -> £3,382,216.59 (10.3%); £3,772,013.33 -> £3,382,216.63 (10.3%); £3,772,013.48 -> £3,382,216.66 (10.3%); £3,772,013.64 -> £3,382,216.70 (10.3%); £3,772,013.80 -> £3,382,216.82 (10.3%); £3,772,013.95 -> £3,382,216.94 (10.3%); £3,772,014.12 -> £3,382,217.07 (10.3%); £3,772,014.32 -> £3,382,217.21 (10.3%); £3,772,014.53 -> £3,382,217.38 (10.3%); £3,772,014.75 -> £3,382,217.58 (10.3%); £3,772,014.99 -> £3,382,217.81 (10.3%); £3,772,015.25 -> £3,382,218.03 (10.3%); £3,772,015.50 -> £3,382,218.15 (10.3%); £3,772,015.76 -> £3,382,218.28 (10.3%); £3,772,016.01 -> £3,382,218.42 (10.3%); £3,772,016.27 -> £3,382,218.54 (10.3%); £3,772,016.52 -> £3,382,218.67 (10.3%); £3,772,016.78 -> £3,382,218.79 (10.3%); £3,772,017.05 -> £3,382,218.90 (10.3%); £3,772,017.31 -> £3,382,219.02 (10.3%); £3,772,017.58 -> £3,382,219.13 (10.3%); £3,772,017.84 -> £3,382,219.24 (10.3%); £3,772,018.10 -> £3,382,219.36 (10.3%); £3,772,018.36 -> £3,382,219.47 (10.3%); £3,772,018.61 -> £3,382,219.58 (10.3%); £3,772,018.86 -> £3,382,219.79 (10.3%); £3,772,019.12 -> £3,382,219.98 (10.3%); £3,772,019.38 -> £3,382,220.14 (10.3%); £3,772,019.64 -> £3,382,220.27 (10.3%); £3,772,019.89 -> £3,382,220.40 (10.3%); £3,772,020.15 -> £3,382,220.54 (10.3%); £3,772,020.41 -> £3,382,220.67 (10.3%); £3,772,020.68 -> £3,382,220.80 (10.3%); £3,772,020.93 -> £3,382,220.93 (10.3%); £3,772,021.18 -> £3,382,221.05 (10.3%); £3,772,021.44 -> £3,382,221.16 (10.3%); £3,772,021.70 -> £3,382,221.20 (10.3%); £3,772,021.95 -> £3,382,221.24 (10.3%); £3,772,022.19 -> £3,382,221.28 (10.3%); £3,772,022.41 -> £3,382,221.32 (10.3%); £3,772,022.60 -> £3,382,221.36 (10.3%); £3,772,022.76 -> £3,382,221.39 (10.3%); £3,772,022.92 -> £3,382,221.43 (10.3%); £3,772,023.06 -> £3,382,221.47 (10.3%); £3,772,023.22 -> £3,382,221.50 (10.3%); £3,772,023.37 -> £3,382,221.54 (10.3%); £3,772,023.52 -> £3,382,221.58 (10.3%); £3,772,023.68 -> £3,382,221.61 (10.3%); £3,772,023.84 -> £3,382,221.65 (10.3%); £3,772,023.99 -> £3,382,221.69 (10.3%); £3,772,024.15 -> £3,382,221.73 (10.3%); £3,772,024.31 -> £3,382,221.77 (10.3%); £3,772,024.47 -> £3,382,221.90 (10.3%); £3,772,024.62 -> £3,382,222.04 (10.3%); £3,772,024.79 -> £3,382,222.19 (10.3%); £3,772,024.98 -> £3,382,222.35 (10.3%); £3,772,025.19 -> £3,382,222.53 (10.3%); £3,772,025.42 -> £3,382,222.73 (10.3%); £3,772,025.66 -> £3,382,222.96 (10.3%); £3,772,025.92 -> £3,382,223.19 (10.3%); £3,772,026.18 -> £3,382,223.31 (10.3%); £3,772,026.43 -> £3,382,223.44 (10.3%); £3,772,026.68 -> £3,382,223.57 (10.3%); £3,772,026.94 -> £3,382,223.70 (10.3%); £3,772,027.20 -> £3,382,223.82 (10.3%); £3,772,027.46 -> £3,382,223.94 (10.3%); £3,772,027.71 -> £3,382,224.06 (10.3%); £3,772,027.96 -> £3,382,224.17 (10.3%); £3,772,028.21 -> £3,382,224.28 (10.3%); £3,772,028.47 -> £3,382,224.40 (10.3%); £3,772,028.73 -> £3,382,224.51 (10.3%); £3,772,028.98 -> £3,382,224.63 (10.3%); £3,772,029.25 -> £3,382,224.74 (10.3%); £3,772,029.50 -> £3,382,224.98 (10.3%); £3,772,029.76 -> £3,382,225.20 (10.3%); £3,772,030.02 -> £3,382,225.36 (10.3%); £3,772,030.28 -> £3,382,225.51 (10.3%); £3,772,030.53 -> £3,382,225.66 (10.3%); £3,772,030.80 -> £3,382,225.80 (10.3%); £3,772,031.05 -> £3,382,225.95 (10.3%); £3,772,031.31 -> £3,382,226.09 (10.3%); £3,772,031.56 -> £3,382,226.24 (10.3%); £3,772,031.82 -> £3,382,226.38 (10.3%); £3,772,032.07 -> £3,382,226.52 (10.3%); £3,772,032.32 -> £3,382,226.56 (10.3%); £3,772,032.58 -> £3,382,226.60 (10.3%); £3,772,032.83 -> £3,382,226.64 (10.3%); £3,772,033.05 -> £3,382,226.67 (10.3%); £3,772,033.25 -> £3,382,226.71 (10.3%); £3,772,033.41 -> £3,382,226.75 (10.3%); £3,772,033.56 -> £3,382,226.79 (10.3%); £3,772,033.71 -> £3,382,226.82 (10.3%); £3,772,033.86 -> £3,382,226.86 (10.3%); £3,772,034.02 -> £3,382,226.90 (10.3%); £3,772,034.17 -> £3,382,226.94 (10.3%); £3,772,034.32 -> £3,382,226.97 (10.3%); £3,772,034.47 -> £3,382,227.01 (10.3%); £3,772,034.62 -> £3,382,227.05 (10.3%); £3,772,034.78 -> £3,382,227.09 (10.3%); £3,772,034.93 -> £3,382,227.13 (10.3%); £3,772,035.08 -> £3,382,227.28 (10.3%); £3,772,035.24 -> £3,382,227.43 (10.3%); £3,772,035.41 -> £3,382,227.59 (10.3%); £3,772,035.59 -> £3,382,227.77 (10.3%); £3,772,035.80 -> £3,382,227.96 (10.3%); £3,772,036.02 -> £3,382,228.18 (10.3%); £3,772,036.26 -> £3,382,228.42 (10.3%); £3,772,036.51 -> £3,382,228.67 (10.3%); £3,772,036.77 -> £3,382,228.79 (10.3%); £3,772,037.03 -> £3,382,228.92 (10.3%); £3,772,037.28 -> £3,382,229.05 (10.3%); £3,772,037.54 -> £3,382,229.18 (10.3%); £3,772,037.80 -> £3,382,229.31 (10.3%); £3,772,038.05 -> £3,382,229.44 (10.3%); £3,772,038.31 -> £3,382,229.55 (10.3%); £3,772,038.56 -> £3,382,229.67 (10.3%); £3,772,038.81 -> £3,382,229.78 (10.3%); £3,772,039.07 -> £3,382,229.90 (10.3%); £3,772,039.33 -> £3,382,230.01 (10.3%); £3,772,039.58 -> £3,382,230.12 (10.3%); £3,772,039.84 -> £3,382,230.23 (10.3%); £3,772,040.10 -> £3,382,230.48 (10.3%); £3,772,040.34 -> £3,382,230.71 (10.3%); £3,772,040.60 -> £3,382,230.91 (10.3%); £3,772,040.86 -> £3,382,231.09 (10.3%); £3,772,041.12 -> £3,382,231.26 (10.3%); £3,772,041.38 -> £3,382,231.43 (10.3%); £3,772,041.63 -> £3,382,231.60 (10.3%); £3,772,041.89 -> £3,382,231.76 (10.3%); £3,772,042.14 -> £3,382,231.92 (10.3%); £3,772,042.39 -> £3,382,232.07 (10.3%); £3,772,042.65 -> £3,382,232.23 (10.3%); £3,772,042.90 -> £3,382,232.27 (10.3%); £3,772,043.15 -> £3,382,232.31 (10.3%); £3,772,043.39 -> £3,382,232.35 (10.3%); £3,772,043.61 -> £3,382,232.39 (10.3%); £3,772,043.81 -> £3,382,232.42 (10.3%); £3,772,043.97 -> £3,382,232.46 (10.3%); £3,772,044.12 -> £3,382,232.50 (10.3%); £3,772,044.27 -> £3,382,232.54 (10.3%); £3,772,044.43 -> £3,382,232.58 (10.3%); £3,772,044.58 -> £3,382,232.62 (10.3%); £3,772,044.73 -> £3,382,232.66 (10.3%); £3,772,044.88 -> £3,382,232.70 (10.3%); £3,772,045.03 -> £3,382,232.73 (10.3%); £3,772,045.18 -> £3,382,232.77 (10.3%); £3,772,045.33 -> £3,382,232.81 (10.3%); £3,772,045.49 -> £3,382,232.85 (10.3%); £3,772,045.64 -> £3,382,233.00 (10.3%); £3,772,045.80 -> £3,382,233.16 (10.3%); £3,772,045.97 -> £3,382,233.34 (10.3%); £3,772,046.16 -> £3,382,233.52 (10.3%); £3,772,046.37 -> £3,382,233.72 (10.3%); £3,772,046.59 -> £3,382,233.95 (10.3%); £3,772,046.83 -> £3,382,234.21 (10.3%); £3,772,047.09 -> £3,382,234.47 (10.3%); £3,772,047.35 -> £3,382,234.60 (10.3%); £3,772,047.62 -> £3,382,234.72 (10.3%); £3,772,047.87 -> £3,382,234.85 (10.3%); £3,772,048.13 -> £3,382,234.99 (10.3%); £3,772,048.39 -> £3,382,235.11 (10.3%); £3,772,048.65 -> £3,382,235.24 (10.3%); £3,772,048.91 -> £3,382,235.35 (10.3%); £3,772,049.16 -> £3,382,235.48 (10.3%); £3,772,049.42 -> £3,382,235.60 (10.3%); £3,772,049.67 -> £3,382,235.72 (10.3%); £3,772,049.93 -> £3,382,235.85 (10.3%); £3,772,050.19 -> £3,382,235.96 (10.3%); £3,772,050.45 -> £3,382,236.07 (10.3%); £3,772,050.70 -> £3,382,236.33 (10.3%); £3,772,050.96 -> £3,382,236.56 (10.3%); £3,772,051.22 -> £3,382,236.76 (10.3%); £3,772,051.48 -> £3,382,236.94 (10.3%); £3,772,051.73 -> £3,382,237.12 (10.3%); £3,772,051.99 -> £3,382,237.28 (10.3%); £3,772,052.25 -> £3,382,237.45 (10.3%); £3,772,052.51 -> £3,382,237.61 (10.3%); £3,772,052.77 -> £3,382,237.77 (10.3%); £3,772,053.03 -> £3,382,237.93 (10.3%); £3,772,053.28 -> £3,382,238.09 (10.3%); £3,772,053.54 -> £3,382,238.13 (10.3%); £3,772,053.80 -> £3,382,238.17 (10.3%); £3,772,054.04 -> £3,382,238.21 (10.3%); £3,772,054.26 -> £3,382,238.25 (10.3%); £3,772,054.46 -> £3,382,238.29 (10.3%); £3,772,054.60 -> £3,382,238.33 (10.3%); £3,772,054.73 -> £3,382,238.37 (10.3%); £3,772,054.87 -> £3,382,238.41 (10.3%); £3,772,055.01 -> £3,382,238.45 (10.3%); £3,772,055.14 -> £3,382,238.48 (10.3%); £3,772,055.28 -> £3,382,238.52 (10.3%); £3,772,055.42 -> £3,382,238.56 (10.3%); £3,772,055.56 -> £3,382,238.60 (10.3%); £3,772,055.69 -> £3,382,238.64 (10.3%); £3,772,055.83 -> £3,382,238.68 (10.3%); £3,772,055.96 -> £3,382,238.72 (10.3%); £3,772,056.10 -> £3,382,238.92 (10.3%); £3,772,056.23 -> £3,382,239.12 (10.3%); £3,772,056.38 -> £3,382,239.33 (10.3%); £3,772,056.54 -> £3,382,239.55 (10.3%); £3,772,056.73 -> £3,382,239.78 (10.3%); £3,772,056.93 -> £3,382,240.03 (10.3%); £3,772,057.14 -> £3,382,240.29 (10.3%); £3,772,057.36 -> £3,382,240.57 (10.3%); £3,772,057.59 -> £3,382,240.66 (10.3%); £3,772,057.82 -> £3,382,240.76 (10.3%); £3,772,058.05 -> £3,382,240.86 (10.3%); £3,772,058.27 -> £3,382,240.96 (10.3%); £3,772,058.50 -> £3,382,241.04 (10.3%); £3,772,058.73 -> £3,382,241.13 (10.3%); £3,772,058.95 -> £3,382,241.21 (10.3%); £3,772,059.19 -> £3,382,241.29 (10.3%); £3,772,059.41 -> £3,382,241.36 (10.3%); £3,772,059.63 -> £3,382,241.43 (10.3%); £3,772,059.85 -> £3,382,241.50 (10.3%); £3,772,060.08 -> £3,382,241.58 (10.3%); £3,772,060.30 -> £3,382,241.65 (10.3%); £3,772,060.53 -> £3,382,241.88 (10.3%); £3,772,060.77 -> £3,382,242.10 (10.3%); £3,772,060.99 -> £3,382,242.30 (10.3%); £3,772,061.23 -> £3,382,242.50 (10.3%); £3,772,061.46 -> £3,382,242.69 (10.3%); £3,772,061.68 -> £3,382,242.89 (10.3%); £3,772,061.91 -> £3,382,243.08 (10.3%); £3,772,062.13 -> £3,382,243.29 (10.3%); £3,772,062.36 -> £3,382,243.50 (10.3%); £3,772,062.59 -> £3,382,243.68 (10.3%); £3,772,062.81 -> £3,382,243.88 (10.3%); £3,772,063.04 -> £3,382,243.93 (10.3%); £3,772,063.26 -> £3,382,243.97 (10.3%); £3,772,063.47 -> £3,382,244.01 (10.3%); £3,772,063.66 -> £3,382,244.05 (10.3%); £3,772,063.83 -> £3,382,244.09 (10.3%); £3,772,063.98 -> £3,382,244.13 (10.3%); £3,772,064.12 -> £3,382,244.17 (10.3%); £3,772,064.26 -> £3,382,244.21 (10.3%); £3,772,064.40 -> £3,382,244.25 (10.3%); £3,772,064.54 -> £3,382,244.28 (10.3%); £3,772,064.68 -> £3,382,244.32 (10.3%); £3,772,064.82 -> £3,382,244.36 (10.3%); £3,772,064.96 -> £3,382,244.40 (10.3%); £3,772,065.11 -> £3,382,244.43 (10.3%); £3,772,065.24 -> £3,382,244.47 (10.3%); £3,772,065.39 -> £3,382,244.51 (10.3%); £3,772,065.53 -> £3,382,244.68 (10.3%); £3,772,065.68 -> £3,382,244.86 (10.3%); £3,772,065.83 -> £3,382,245.04 (10.3%); £3,772,066.00 -> £3,382,245.22 (10.3%); £3,772,066.19 -> £3,382,245.40 (10.3%); £3,772,066.39 -> £3,382,245.59 (10.3%); £3,772,066.60 -> £3,382,245.77 (10.3%); £3,772,066.83 -> £3,382,245.96 (10.3%); £3,772,067.07 -> £3,382,246.01 (10.3%); £3,772,067.31 -> £3,382,246.06 (10.3%); £3,772,067.54 -> £3,382,246.11 (10.3%); £3,772,067.77 -> £3,382,246.16 (10.3%); £3,772,067.99 -> £3,382,246.21 (10.3%); £3,772,068.23 -> £3,382,246.25 (10.3%); £3,772,068.46 -> £3,382,246.30 (10.3%); £3,772,068.69 -> £3,382,246.35 (10.3%); £3,772,068.92 -> £3,382,246.39 (10.3%); £3,772,069.15 -> £3,382,246.44 (10.3%); £3,772,069.39 -> £3,382,246.49 (10.3%); £3,772,069.62 -> £3,382,246.53 (10.3%); £3,772,069.85 -> £3,382,246.58 (10.3%); £3,772,070.09 -> £3,382,246.75 (10.3%); £3,772,070.32 -> £3,382,246.92 (10.3%); £3,772,070.55 -> £3,382,247.09 (10.3%); £3,772,070.78 -> £3,382,247.26 (10.3%); £3,772,071.02 -> £3,382,247.43 (10.3%); £3,772,071.25 -> £3,382,247.60 (10.3%); £3,772,071.48 -> £3,382,247.76 (10.3%); £3,772,071.72 -> £3,382,247.93 (10.3%); £3,772,071.96 -> £3,382,248.09 (10.3%); £3,772,072.19 -> £3,382,248.26 (10.3%); £3,772,072.43 -> £3,382,248.43 (10.3%); £3,772,072.67 -> £3,382,248.47 (10.3%); £3,772,072.90 -> £3,382,248.51 (10.3%); £3,772,073.13 -> £3,382,248.55 (10.3%); £3,772,073.33 -> £3,382,248.58 (10.3%); £3,772,073.50 -> £3,382,248.62 (10.3%); £3,772,073.66 -> £3,382,248.66 (10.3%); £3,772,073.82 -> £3,382,248.70 (10.3%); £3,772,073.98 -> £3,382,248.73 (10.3%); £3,772,074.15 -> £3,382,248.77 (10.3%); £3,772,074.31 -> £3,382,248.81 (10.3%); £3,772,074.47 -> £3,382,248.85 (10.3%); £3,772,074.63 -> £3,382,248.88 (10.3%); £3,772,074.80 -> £3,382,248.92 (10.3%); £3,772,074.96 -> £3,382,248.96 (10.3%); £3,772,075.12 -> £3,382,249.00 (10.3%); £3,772,075.28 -> £3,382,249.04 (10.3%); £3,772,075.44 -> £3,382,249.21 (10.3%); £3,772,075.60 -> £3,382,249.39 (10.3%); £3,772,075.78 -> £3,382,249.58 (10.3%); £3,772,075.98 -> £3,382,249.78 (10.3%); £3,772,076.20 -> £3,382,250.01 (10.3%); £3,772,076.43 -> £3,382,250.26 (10.3%); £3,772,076.68 -> £3,382,250.53 (10.3%); £3,772,076.96 -> £3,382,250.82 (10.3%); £3,772,077.22 -> £3,382,250.94 (10.3%); £3,772,077.51 -> £3,382,251.07 (10.3%); £3,772,077.78 -> £3,382,251.20 (10.3%); £3,772,078.05 -> £3,382,251.33 (10.3%); £3,772,078.31 -> £3,382,251.46 (10.3%); £3,772,078.59 -> £3,382,251.58 (10.3%); £3,772,078.85 -> £3,382,251.70 (10.3%); £3,772,079.12 -> £3,382,251.82 (10.3%); £3,772,079.40 -> £3,382,251.94 (10.3%); £3,772,079.67 -> £3,382,252.06 (10.3%); £3,772,079.94 -> £3,382,252.17 (10.3%); £3,772,080.22 -> £3,382,252.29 (10.3%); £3,772,080.49 -> £3,382,252.39 (10.3%); £3,772,080.76 -> £3,382,252.64 (10.3%); £3,772,081.02 -> £3,382,252.88 (10.3%); £3,772,081.29 -> £3,382,253.09 (10.3%); £3,772,081.55 -> £3,382,253.28 (10.3%); £3,772,081.81 -> £3,382,253.47 (10.3%); £3,772,082.08 -> £3,382,253.65 (10.3%); £3,772,082.34 -> £3,382,253.83 (10.3%); £3,772,082.61 -> £3,382,254.01 (10.3%); £3,772,082.88 -> £3,382,254.18 (10.3%); £3,772,083.15 -> £3,382,254.35 (10.3%); £3,772,083.41 -> £3,382,254.52 (10.3%); £3,772,083.68 -> £3,382,254.56 (10.3%); £3,772,083.95 -> £3,382,254.60 (10.3%); £3,772,084.19 -> £3,382,254.64 (10.3%); £3,772,084.41 -> £3,382,254.68 (10.3%); £3,772,084.63 -> £3,382,254.71 (10.3%); £3,772,084.79 -> £3,382,254.75 (10.3%); £3,772,084.95 -> £3,382,254.79 (10.3%); £3,772,085.12 -> £3,382,254.83 (10.3%); £3,772,085.28 -> £3,382,254.87 (10.3%); £3,772,085.45 -> £3,382,254.90 (10.3%); £3,772,085.61 -> £3,382,254.94 (10.3%); £3,772,085.77 -> £3,382,254.98 (10.3%); £3,772,085.93 -> £3,382,255.01 (10.3%); £3,772,086.09 -> £3,382,255.05 (10.3%); £3,772,086.26 -> £3,382,255.09 (10.3%); £3,772,086.42 -> £3,382,255.13 (10.3%); £3,772,086.58 -> £3,382,255.27 (10.3%); £3,772,086.74 -> £3,382,255.42 (10.3%); £3,772,086.92 -> £3,382,255.59 (10.3%); £3,772,087.12 -> £3,382,255.77 (10.3%); £3,772,087.34 -> £3,382,255.97 (10.3%); £3,772,087.57 -> £3,382,256.20 (10.3%); £3,772,087.82 -> £3,382,256.44 (10.3%); £3,772,088.09 -> £3,382,256.70 (10.3%); £3,772,088.36 -> £3,382,256.83 (10.3%); £3,772,088.65 -> £3,382,256.96 (10.3%); £3,772,088.91 -> £3,382,257.09 (10.3%); £3,772,089.17 -> £3,382,257.22 (10.3%); £3,772,089.43 -> £3,382,257.35 (10.3%); £3,772,089.70 -> £3,382,257.47 (10.3%); £3,772,089.97 -> £3,382,257.59 (10.3%); £3,772,090.24 -> £3,382,257.71 (10.3%); £3,772,090.50 -> £3,382,257.83 (10.3%); £3,772,090.76 -> £3,382,257.94 (10.3%); £3,772,091.04 -> £3,382,258.05 (10.3%); £3,772,091.31 -> £3,382,258.16 (10.3%); £3,772,091.58 -> £3,382,258.27 (10.3%); £3,772,091.86 -> £3,382,258.52 (10.3%); £3,772,092.12 -> £3,382,258.74 (10.3%); £3,772,092.39 -> £3,382,258.93 (10.3%); £3,772,092.66 -> £3,382,259.10 (10.3%); £3,772,092.93 -> £3,382,259.27 (10.3%); £3,772,093.19 -> £3,382,259.43 (10.3%); £3,772,093.46 -> £3,382,259.59 (10.3%); £3,772,093.72 -> £3,382,259.75 (10.3%); £3,772,093.98 -> £3,382,259.91 (10.3%); £3,772,094.26 -> £3,382,260.06 (10.3%); £3,772,094.53 -> £3,382,260.21 (10.3%); £3,772,094.80 -> £3,382,260.25 (10.3%); £3,772,095.07 -> £3,382,260.29 (10.3%); £3,772,095.32 -> £3,382,260.33 (10.3%); £3,772,095.55 -> £3,382,260.37 (10.3%); £3,772,095.76 -> £3,382,260.41 (10.3%); £3,772,095.93 -> £3,382,260.44 (10.3%); £3,772,096.09 -> £3,382,260.48 (10.3%); £3,772,096.24 -> £3,382,260.52 (10.3%); £3,772,096.40 -> £3,382,260.56 (10.3%); £3,772,096.56 -> £3,382,260.60 (10.3%); £3,772,096.72 -> £3,382,260.63 (10.3%); £3,772,096.88 -> £3,382,260.67 (10.3%); £3,772,097.04 -> £3,382,260.71 (10.3%); £3,772,097.19 -> £3,382,260.75 (10.3%); £3,772,097.35 -> £3,382,260.79 (10.3%); £3,772,097.51 -> £3,382,260.83 (10.3%); £3,772,097.67 -> £3,382,261.00 (10.3%); £3,772,097.83 -> £3,382,261.18 (10.3%); £3,772,098.01 -> £3,382,261.37 (10.3%); £3,772,098.21 -> £3,382,261.58 (10.3%); £3,772,098.43 -> £3,382,261.80 (10.3%); £3,772,098.66 -> £3,382,262.04 (10.3%); £3,772,098.91 -> £3,382,262.31 (10.3%); £3,772,099.18 -> £3,382,262.58 (10.3%); £3,772,099.45 -> £3,382,262.71 (10.3%); £3,772,099.71 -> £3,382,262.83 (10.3%); £3,772,099.99 -> £3,382,262.96 (10.3%); £3,772,100.25 -> £3,382,263.09 (10.3%); £3,772,100.52 -> £3,382,263.21 (10.3%); £3,772,100.79 -> £3,382,263.33 (10.3%); £3,772,101.06 -> £3,382,263.45 (10.3%); £3,772,101.34 -> £3,382,263.56 (10.3%); £3,772,101.62 -> £3,382,263.68 (10.3%); £3,772,101.88 -> £3,382,263.81 (10.3%); £3,772,102.15 -> £3,382,263.93 (10.3%); £3,772,102.42 -> £3,382,264.05 (10.3%); £3,772,102.69 -> £3,382,264.16 (10.3%); £3,772,102.96 -> £3,382,264.44 (10.3%); £3,772,103.23 -> £3,382,264.70 (10.3%); £3,772,103.50 -> £3,382,264.93 (10.3%); £3,772,103.77 -> £3,382,265.14 (10.3%); £3,772,104.04 -> £3,382,265.33 (10.3%); £3,772,104.31 -> £3,382,265.52 (10.3%); £3,772,104.58 -> £3,382,265.70 (10.3%); £3,772,104.84 -> £3,382,265.88 (10.3%); £3,772,105.11 -> £3,382,266.06 (10.3%); £3,772,105.38 -> £3,382,266.23 (10.3%); £3,772,105.65 -> £3,382,266.40 (10.3%); £3,772,105.92 -> £3,382,266.44 (10.3%); £3,772,106.20 -> £3,382,266.48 (10.3%); £3,772,106.44 -> £3,382,266.52 (10.3%); £3,772,106.67 -> £3,382,266.56 (10.3%); £3,772,106.88 -> £3,382,266.60 (10.3%); £3,772,107.04 -> £3,382,266.63 (10.3%); £3,772,107.20 -> £3,382,266.67 (10.3%); £3,772,107.36 -> £3,382,266.71 (10.3%); £3,772,107.52 -> £3,382,266.74 (10.3%); £3,772,107.68 -> £3,382,266.78 (10.3%); £3,772,107.84 -> £3,382,266.82 (10.3%); £3,772,108.00 -> £3,382,266.86 (10.3%); £3,772,108.16 -> £3,382,266.90 (10.3%); £3,772,108.32 -> £3,382,266.94 (10.3%); £3,772,108.48 -> £3,382,266.98 (10.3%); £3,772,108.65 -> £3,382,267.02 (10.3%); £3,772,108.81 -> £3,382,267.20 (10.3%); £3,772,108.97 -> £3,382,267.38 (10.3%); £3,772,109.16 -> £3,382,267.58 (10.3%); £3,772,109.36 -> £3,382,267.78 (10.3%); £3,772,109.58 -> £3,382,268.00 (10.3%); £3,772,109.81 -> £3,382,268.25 (10.3%); £3,772,110.06 -> £3,382,268.51 (10.3%); £3,772,110.33 -> £3,382,268.78 (10.3%); £3,772,110.60 -> £3,382,268.90 (10.3%); £3,772,110.87 -> £3,382,269.03 (10.3%); £3,772,111.14 -> £3,382,269.15 (10.3%); £3,772,111.41 -> £3,382,269.27 (10.3%); £3,772,111.69 -> £3,382,269.40 (10.3%); £3,772,111.96 -> £3,382,269.52 (10.3%); £3,772,112.23 -> £3,382,269.63 (10.3%); £3,772,112.50 -> £3,382,269.75 (10.3%); £3,772,112.78 -> £3,382,269.86 (10.3%); £3,772,113.05 -> £3,382,269.98 (10.3%); £3,772,113.32 -> £3,382,270.09 (10.3%); £3,772,113.59 -> £3,382,270.20 (10.3%); £3,772,113.86 -> £3,382,270.31 (10.3%); £3,772,114.15 -> £3,382,270.58 (10.3%); £3,772,114.42 -> £3,382,270.82 (10.3%); £3,772,114.69 -> £3,382,271.03 (10.3%); £3,772,114.95 -> £3,382,271.23 (10.3%); £3,772,115.22 -> £3,382,271.42 (10.3%); £3,772,115.49 -> £3,382,271.60 (10.3%); £3,772,115.78 -> £3,382,271.78 (10.3%); £3,772,116.05 -> £3,382,271.95 (10.3%); £3,772,116.33 -> £3,382,272.13 (10.3%); £3,772,116.60 -> £3,382,272.29 (10.3%); £3,772,116.86 -> £3,382,272.46 (10.3%); £3,772,117.15 -> £3,382,272.50 (10.3%); £3,772,117.42 -> £3,382,272.54 (10.3%); £3,772,117.67 -> £3,382,272.58 (10.3%); £3,772,117.91 -> £3,382,272.61 (10.3%); £3,772,118.13 -> £3,382,272.65 (10.3%); £3,772,118.28 -> £3,382,272.69 (10.3%); £3,772,118.45 -> £3,382,272.72 (10.3%); £3,772,118.61 -> £3,382,272.76 (10.3%); £3,772,118.78 -> £3,382,272.80 (10.3%); £3,772,118.93 -> £3,382,272.84 (10.3%); £3,772,119.10 -> £3,382,272.87 (10.3%); £3,772,119.26 -> £3,382,272.91 (10.3%); £3,772,119.43 -> £3,382,272.95 (10.3%); £3,772,119.59 -> £3,382,272.98 (10.3%); £3,772,119.75 -> £3,382,273.02 (10.3%); £3,772,119.91 -> £3,382,273.06 (10.3%); £3,772,120.07 -> £3,382,273.21 (10.3%); £3,772,120.23 -> £3,382,273.38 (10.3%); £3,772,120.41 -> £3,382,273.55 (10.3%); £3,772,120.61 -> £3,382,273.73 (10.3%); £3,772,120.82 -> £3,382,273.94 (10.3%); £3,772,121.06 -> £3,382,274.16 (10.3%); £3,772,121.31 -> £3,382,274.41 (10.3%); £3,772,121.57 -> £3,382,274.67 (10.3%); £3,772,121.85 -> £3,382,274.79 (10.3%); £3,772,122.11 -> £3,382,274.92 (10.3%); £3,772,122.38 -> £3,382,275.05 (10.3%); £3,772,122.65 -> £3,382,275.18 (10.3%); £3,772,122.92 -> £3,382,275.31 (10.3%); £3,772,123.19 -> £3,382,275.43 (10.3%); £3,772,123.47 -> £3,382,275.54 (10.3%); £3,772,123.75 -> £3,382,275.65 (10.3%); £3,772,124.01 -> £3,382,275.77 (10.3%); £3,772,124.28 -> £3,382,275.89 (10.3%); £3,772,124.55 -> £3,382,276.00 (10.3%); £3,772,124.82 -> £3,382,276.10 (10.3%); £3,772,125.09 -> £3,382,276.21 (10.3%); £3,772,125.35 -> £3,382,276.46 (10.3%); £3,772,125.63 -> £3,382,276.69 (10.3%); £3,772,125.90 -> £3,382,276.90 (10.3%); £3,772,126.17 -> £3,382,277.08 (10.3%); £3,772,126.44 -> £3,382,277.26 (10.3%); £3,772,126.71 -> £3,382,277.43 (10.3%); £3,772,126.99 -> £3,382,277.60 (10.3%); £3,772,127.25 -> £3,382,277.77 (10.3%); £3,772,127.52 -> £3,382,277.94 (10.3%); £3,772,127.80 -> £3,382,278.11 (10.3%); £3,772,128.07 -> £3,382,278.26 (10.3%); £3,772,128.34 -> £3,382,278.30 (10.3%); £3,772,128.61 -> £3,382,278.34 (10.3%); £3,772,128.86 -> £3,382,278.38 (10.3%); £3,772,129.10 -> £3,382,521.59 (10.3%)
- Bills issued: 153, average clarity 0.804, average bill shock 19.5%, bad debt provision £-77.10, avg complaint probability 5.0%
- Solvency signal: £343,188/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2024 produced a net gain of £347,778.98 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 44 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £120,992.97 (gross £518,611.38, capital £5,646.89)
  - Electricity: gross £464,863.13, capital £5,633.65, net £116,452.84
  - Gas: gross £53,748.25, capital £13.23, net £4,540.12
- Treasury at year end: £3,827,008.96
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
- Bill shock events (>=20%): 26 -- C7 2025-04-30 (36%); C7 2025-05-31 (37%); C7 2025-06-07 (80%); C2 2025-04-30 (23%); C2g 2025-01-31 (32%); C2g 2025-02-28 (24%); C2g 2025-04-30 (30%); C2g 2025-05-31 (34%); C2g 2025-06-07 (73%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (40%); C8 2025-05-31 (42%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (33%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C1_2 2025-01-31 (36%); C1_2 2025-02-28 (46%); C1_2 2025-03-31 (34%); C1_2 2025-04-30 (26%); C1_2 2025-05-31 (29%); C1_2 2025-06-07 (71%)
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
- Bills issued: 66, average clarity 0.785, average bill shock 22.9%, bad debt provision £0.00, avg complaint probability 5.7%
- Solvency signal: £425,223/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-20.68 vs. naked (unhedged) net margin: £199.65
- hedging cost £220.33 vs. a fully unhedged book (commodity-only: actual net £-20.68 vs. naked net £199.65)
  - C2: actual £0.57 vs. naked £84.47 -- hedging cost £83.90
  - C2g: actual £8.83 vs. naked £-3.72 -- hedging added £12.55
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £120,992.97 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 26 customer(s) experienced a bill shock of >=20%.
