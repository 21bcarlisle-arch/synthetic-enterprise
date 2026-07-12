# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,902,095.14
  (£1,435,458.92 net change)
- Solvency signal (final year): £425,215/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £22,549,583.84
  VAT remitted to HMRC: (£3,738,265.80) | Revenue (ex-VAT): £18,811,318.04
  Non-commodity pass-through: (£4,782,360.86)
- Gross margin: £6,431,212.61
- Capital costs: £51,377.37
- Net margin: £6,379,835.24
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 33.9%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1588, average clarity 0.809,
  service quality score 0.900
- Enterprise value (CLV sum across 14 billing accounts): £7,735,815.99
- Cost to serve (whole portfolio): £18,730.56, net margin after cost to serve: £6,361,104.68
- Hedge effectiveness (whole window): hedging cost £4,222,848.02 vs. a fully unhedged book (commodity-only: actual net £1,435,458.92 vs. naked net £5,658,306.93)

- **2021** (crisis year): net margin £75,248.53, 0 risk committee wake-up(s).
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
| Net margin % of revenue | 33.9% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,431,212.61, capital £51,377.37, net £6,379,835.24. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £75,248.53 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 33.9%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,379,835.24
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
| 2017 | £30,139.92 | £0.00 | £62.04 | £935.10 | £516.54 | £31,653.60 |
| 2018 | £101,124.28 | £0.00 | £-637.40 | £634.09 | £436.94 | £101,557.91 |
| 2019 | £222,457.58 | £9,999.92 | £360.04 | £804.92 | £489.73 | £234,112.18 |
| 2020 | £116,572.09 | £10,030.76 | £398.12 | £1,052.40 | £457.36 | £128,510.73 |
| 2021 | £64,952.49 | £9,999.92 | £-0.69 | £466.40 | £-169.59 | £75,248.53 |
| 2022 | £330,000.66 | £9,999.92 | £1,141.20 | £-1,526.03 | £-1,259.09 | £338,356.66 |
| 2023 | £135,957.41 | £9,999.92 | £-615.29 | £46.59 | £-976.37 | £144,412.25 |
| 2024 | £333,515.99 | £10,030.76 | £814.14 | £2,781.69 | £678.12 | £347,820.71 |
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
| 2018 | 2,487,909 | 11 | 226,174 | 1739.80× | OK |
| 2019 | 2,611,898 | 12 | 217,658 | 1674.29× | OK |
| 2020 | 2,924,313 | 14 | 208,880 | 1606.77× | OK |
| 2021 | 2,957,780 | 11 | 268,889 | 2068.38× | OK |
| 2022 | 3,161,734 | 11 | 287,430 | 2211.00× | OK |
| 2023 | 3,382,316 | 11 | 307,483 | 2365.26× | OK |
| 2024 | 3,774,999 | 11 | 343,182 | 2639.86× | OK |
| 2025 | 3,826,938 | 9 | 425,215 | 3270.89× | OK |

End-state (2025): **£425,215/account** across 9 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,441 | 81974.8× | OK |
| 2017 | 466 | 559 | 2,498,923 | 4470.2× | OK |
| 2018 | 868 | 1,041 | 2,487,909 | 2389.2× | OK |
| 2019 | 1,543 | 1,851 | 2,611,898 | 1411.0× | OK |
| 2020 | 1,979 | 2,374 | 2,924,313 | 1231.6× | OK |
| 2021 | 4,332 | 5,198 | 2,957,780 | 569.0× | OK |
| 2022 | 8,503 | 10,204 | 3,161,734 | 309.9× | OK |
| 2023 | 5,604 | 6,725 | 3,382,316 | 503.0× | OK |
| 2024 | 2,651 | 3,182 | 3,774,999 | 1186.5× | OK |
| 2025 | 3,872 | 4,647 | 3,826,938 | 823.6× | OK |




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
| 2016 | 35 | 111% | C8 (2016-10-31) |
| 2017 | 56 | 87% | C1g (2017-11-30) |
| 2018 | 64 | 93% | C4g (2018-10-31) |
| 2019 | 68 | 130% | C_IC1 (2019-03-31) |
| 2020 | 58 | 118% | C_IC2 (2020-03-31) |
| 2021 | 49 | 1202% | C1_2 (2021-01-31) |
| 2022 | 73 | 146% | C4g (2022-10-31) |
| 2023 | 49 | 101% | C_IC2 (2023-06-30) |
| 2024 | 41 | 107% | C_IC2 (2024-07-31) |
| 2025 | 26 | 81% | C1_2 (2025-06-07) |

Total: **519** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2021-01-31 | C1_2 | +1202% | no |
| 2022-10-31 | C4g | +146% | no |
| 2022-01-31 | C1_2 | +146% | no |
| 2021-10-31 | C4g | +132% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2020-03-31 | C_IC2 | +118% | no |
| 2016-10-31 | C8 | +111% | no |
| 2022-01-31 | C_IC3 | +109% | no |
| 2016-10-31 | C1g | +107% | no |
| 2024-07-31 | C_IC2 | +107% | no |

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
**3yr-trailing EV:** £677,979.15 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,286.83 |
| 2017 | £31,653.60 |
| 2018 | £101,557.91 |
| 2019 | £234,112.18 |
| 2020 | £128,510.73 |
| 2021 | £75,248.53 |
| 2022 | £338,356.66 |
| 2023 | £144,412.25 | ← trailing
| 2024 | £347,820.71 | ← trailing
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
| C6 | £19,260.39 | £329.88 |
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
| 2017 | 14 | £16,735 | £8,803 | £2,261 | 13.5% |
| 2018 | 15 | £29,032 | £17,507 | £6,771 | 23.3% |
| 2019 | 17 | £70,487 | £41,300 | £13,771 | 19.5% |
| 2020 | 19 | £64,385 | £41,672 | £6,764 | 10.5% |
| 2021 | 14 | £123,922 | £54,511 | £5,375 | 4.3% << |
| 2022 | 14 | £245,590 | £74,945 | £24,168 | 9.8% |
| 2023 | 14 | £185,335 | £68,277 | £10,315 | 5.6% |
| 2024 | 14 | £156,332 | £89,843 | £24,844 | 15.9% |
| 2025 | 11 | £88,243 | £47,146 | £10,999 | 12.5% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £24,844 net/customer
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
| C3 | £190 | — | £190 |
| C3g | — | £336 | £336 |
| C4 | £91 | — | £91 |
| C4g | — | £-1,711 | £-1,711 * |
| C5 | £-168 | — | £-168 * |
| C6 | £1,987 | — | £1,987 |
| C7 | £-572 | — | £-572 * |
| C8 | £2,292 | — | £2,292 |
| C9 | £2,240 | — | £2,240 |
| C_IC1 | £846,747 | — | £846,747 |
| C_IC2 | £434,894 | — | £434,894 |
| C_IC3 | £136,677 | — | £136,677 |
| C_IC3g | — | £64,511 | £64,511 |
| C_IC4 | £32,221 | — | £32,221 |
| **Total** | **£1,458,853** | **£65,099** | **£1,523,952** |

Loss-making accounts: C4g (£-1,711), C7 (£-572), C5 (£-168)
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
| 2016 | 0.820 A | 5.0% | 0.22% | 35 | 108 | AMBER |
| 2017 | 0.810 A | 4.9% | 0.18% | 56 | 168 | AMBER |
| 2018 | 0.802 A | 4.9% | 0.17% | 64 | 180 | AMBER |
| 2019 | 0.817 A | 4.9% | 0.18% | 68 | 204 | AMBER |
| 2020 | 0.826 G | 4.5% | 0.16% | 58 | 205 | GREEN |
| 2021 | 0.811 A | 5.0% | 0.25% | 49 | 168 | AMBER |
| 2022 | 0.787 R | 5.8% | 0.24% | 73 | 168 | RED ! |
| 2023 | 0.808 A | 4.9% | 0.18% | 49 | 168 | AMBER |
| 2024 | 0.813 A | 4.7% | 0.17% | 41 | 153 | AMBER |
| 2025 | 0.775 R | 6.1% | 0.25% | 26 | 66 | RED ! |

Worst clarity year: **2025** (0.775)
Highest complaint probability: **2025** (6.1%)
Worst bill shock: **2021** (0.25%)
RED years: 2022, 2025
AMBER years: 2016, 2017, 2018, 2019, 2021, 2023, 2024
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,441 | £1,287 |
| 2017 | 2.69 | WATCH | £2,498,923 | £31,654 |
| 2018 | — | — | £2,487,909 | £101,558 |
| 2019 | — | — | £2,611,898 | £234,112 |
| 2020 | — | — | £2,924,313 | £128,511 |
| 2021 | — | — | £2,957,780 | £75,249 |
| 2022 | 2.70 | WATCH | £3,161,734 | £338,357 |
| 2023 | 2.72 | WATCH | £3,382,316 | £144,412 |
| 2024 | — | — | £3,774,999 | £347,821 |
| 2025 | — | — | £3,826,938 | £120,993 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,826,938)**
**Treasury growth: £2,467,441 → £3,826,938 (+£1,359,497)**

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
| 2017 | 2017-12-31 | 48 | C5 | -£201 |
| 2018 | 2018-12-31 | 48 | C5 | -£424 |
| 2019 | 2019-12-31 | 48 | C3 | -£88 |
| 2020 | 2020-03-16 | 20 | C_IC1 | -£19 |
| 2021 | 2021-12-31 | 48 | C6 | -£526 |
| 2022 | 2022-01-24 | 26 | C_IC1 | -£89 |
| 2023 | 2023-12-31 | 48 | C6 | -£1,995 |
| 2024 | 2024-09-28 | 48 | C4 | -£113 |
| 2025 | 2025-01-08 | 31 | C_IC1 | -£81 |

**Single worst period: 2023 2023-12-31 SP48 (C6, -£1,995)** — exposure from gas supply anchor at year-end pricing.

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
| 2016 | 14 | £173,370 | £92,774 | £8,903 | £12,384 |
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
| 2017 | +£2,707 | £37,159 | £290 | — | 168 |
| 2018 | +£9,875 | £65,510 | £491 | — | 180 |
| 2019 | +£28,353 | £164,625 | £24 | — | 204 |
| 2020 | +£35,391 | £238,634 | £-18 | — | 205 |
| 2021 | +£14,982 | £246,246 | £593 | — | 168 |
| 2022 | -£49,726 CREDIT | £256,149 | £63 | 2 | 168 |
| 2023 | +£64,738 | £271,739 | £2,157 | 47 | 168 |
| 2024 | +£109,869 | £307,451 | £-119 | 4271 | 153 |
| 2025 | +£46,911 | £135,614 | £0 | — | 66 |

**CfD turned CREDIT in 2022: -£49,726 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2023 (£2,157)**

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
| 2018 | £2,487,909 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,611,898 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,924,313 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,957,780 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,161,734 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,382,316 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,774,999 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,826,938 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 38.0% | £1,101 | £525 | 1.51% |
| 2017 | 14 | 32.6% | £24,791 | £8,803 | 2.03% |
| 2018 | 15 | 40.9% | £39,964 | £17,506 | 2.23% |
| 2019 | 17 | 40.3% | £96,684 | £41,300 | 2.13% |
| 2020 | 19 | 40.0% | £97,640 | £41,669 | 2.35% |
| 2021 | 14 | 29.0% | £172,461 | £54,500 | 2.22% |
| 2022 | 14 | 22.1% | £302,824 | £74,940 | 2.27% |
| 2023 | 14 | 24.6% | £247,983 | £68,260 | 2.51% |
| 2024 | 14 | 39.1% | £214,169 | £89,787 | 2.44% |
| 2025 | 11 | 38.3% | £111,597 | £47,146 | 3.40% |

**Best EBIT%: 2018 (40.9%)** | **Worst EBIT%: 2022 (22.1%)**
**Peak revenue/customer: 2022 (£302,824)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Population Anchoring -- Complaints & Arrears (Phase PS)

SIM aggregate complaint and arrears rates vs published UK benchmarks.
Complaints: Ofgem QoS survey, I&C adjusted (GREEN 2-6%, crisis 2-8%).
Arrears: DESNZ business energy debt (GREEN <8%, crisis <12%).

| Year | Complaint rate% | C.Bench hi | C.RAG | Arrears rate% | A.Bench hi | A.RAG |
|------|-----------------|-----------|-------|---------------|-----------|-------|
| 2016 | 5.00% | 6% | OK | 15.4% | 8% | ! |
| 2017 | 4.93% | 6% | OK | 21.4% | 8% | ! |
| 2018 | 4.91% | 6% | OK | 26.7% | 8% | ! |
| 2019 | 4.89% | 6% | OK | 29.4% | 8% | ! |
| 2020 | 4.46% | 6% | OK | 5.3% | 8% | OK |
| 2021 | 4.97% | 8% | OK | 21.4% | 12% | ! |
| 2022 | 5.75% | 8% | OK | 50.0% | 12% | ! |
| 2023 | 4.94% | 8% | OK | 21.4% | 12% | ! |
| 2024 | 4.74% | 6% | OK | 35.7% | 8% | ! |
| 2025 | 6.05% | 6% | ~ | 27.3% | 8% | ! |

**Complaints:** 9 of 10 years GREEN (I&C baseline 2-6% normal, 2-8% crisis).
**Arrears:** 1 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).

## Plausibility vs Industry

Key metrics vs UK retail energy norms (Ofgem/Cornwall Insight). OK = within range | ~ = amber | ! = outside expected range.

| Year | Net margin% | Gross margin% | Bad debt% | Churn% |
|------|-------------|---------------|-----------|--------|
| 2016 | !38.0% | !47.7% | OK1.51% | ~0% |
| 2017 | !32.6% | !35.5% | OK2.03% | ~0% |
| 2018 | !40.9% | !43.8% | OK2.23% | ~0% |
| 2019 | !40.3% | !42.7% | OK2.13% | ~0% |
| 2020 | !40.0% | !42.7% | OK2.35% | OK16% |
| 2021 | !29.0% | !31.6% | OK2.22% | ~0% |
| 2022 | !22.1% | ~24.7% | OK2.27% | ~0% |
| 2023 | !24.6% | ~27.5% | OK2.51% | ~0% |
| 2024 | !39.1% | !41.9% | OK2.44% | OK14% |
| 2025 | !38.3% | !42.2% | OK3.40% | ~0% |

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

**Total bad debt (all years):** £3,547
**Crisis stress incremental:** £5,321

**RAG [OK]:** GREEN — Incremental credit stress below 0.5% revenue — not material

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (11 active customers) under 12-month forward scenarios.
Generated: 2026-07-11T19:28:32Z

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
| 2016 | £14,309.39 | £3,594.97 | £3,892.24 | £6,822.19 | 47.7% | — | — | — | — |
| 2017 | £347,076.42 | £111,055.46 | £112,782.22 | £123,238.74 | 35.5% | +£332,767.03 | +£107,460.50 | +£108,889.98 | +£116,416.55 |
| 2018 | £599,456.46 | £172,888.20 | £163,976.85 | £262,591.42 | 43.8% | +£252,380.04 | +£61,832.74 | +£51,194.63 | +£139,352.67 |
| 2019 | £1,643,619.82 | £496,185.23 | £445,337.03 | £702,097.56 | 42.7% | +£1,044,163.36 | +£323,297.03 | +£281,360.18 | +£439,506.15 |
| 2020 | £1,855,166.54 | £431,600.88 | £631,853.58 | £791,712.09 | 42.7% | +£211,546.72 | £-64,584.35 | +£186,516.55 | +£89,614.52 |
| 2021 | £2,414,454.41 | £971,905.80 | £679,550.33 | £762,998.28 | 31.6% | +£559,287.87 | +£540,304.92 | +£47,696.75 | £-28,713.81 |
| 2022 | £4,239,541.60 | £2,389,086.10 | £801,288.51 | £1,049,166.99 | 24.7% | +£1,825,087.19 | +£1,417,180.30 | +£121,738.18 | +£286,168.71 |
| 2023 | £3,471,763.08 | £1,639,053.05 | £877,068.66 | £955,641.38 | 27.5% | £-767,778.52 | £-750,033.06 | +£75,780.15 | £-93,525.61 |
| 2024 | £2,998,361.29 | £931,630.07 | £809,714.61 | £1,257,016.60 | 41.9% | £-473,401.79 | £-707,422.97 | £-67,354.04 | +£301,375.22 |
| 2025 | £1,227,569.03 | £452,060.81 | £256,896.84 | £518,611.38 | 42.2% | £-1,770,792.26 | £-479,569.26 | £-552,817.78 | £-738,405.22 |

**Best GM year: 2016 (47.7%)** | **Worst GM year: 2022 (24.7%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Net Margin Bridge (Year-on-Year Attribution)

Decomposes each year's net margin change into: gross margin movement, bad debt, capital costs, policy levies, network costs.

| Transition | Net Δ | Gross Δ | Bad Debt Δ | Capital Δ | Policy Δ | Network Δ | Portfolio | Driver | RAG |
|-----------|-------|---------|-----------|---------|---------|---------|---------|--------|-----|
| 2016→2017 | +£30,367 | +£116,417 | -£223 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£69,904 | +£139,364 | -£202 | -£367 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£132,554 | +£439,498 | +£468 | -£686 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£105,601 | +£89,669 | +£42 | +£360 | -£162,654 | -£33,019 | +2 | policy levies | RED |
| 2020→2021 | -£53,262 | -£28,614 | -£611 | -£3,636 | -£19,033 | -£1,367 | -5 | gross margin | RED |
| 2021→2022 | +£263,108 | +£286,070 | +£530 | -£7,674 | -£1,057 | -£14,761 | +0 | gross margin | GREEN |
| 2022→2023 | -£193,944 | -£93,343 | -£2,094 | +£3,240 | -£70,553 | -£31,194 | +0 | gross margin | RED |
| 2023→2024 | +£203,408 | +£301,924 | +£2,276 | +£514 | -£100,652 | -£654 | +0 | gross margin | GREEN |
| 2024→2025 | -£226,828 | -£739,194 | -£119 | +£3,875 | +£381,910 | +£126,700 | -3 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£226,828)** | **Best transition: 2021→2022 (+£263,108)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Payment Portfolio Health (P2: Billing Infra)

Year-by-year bad debt rate and high-churn-risk customer concentration.

| Year | Bad Debt | Bad Debt Rate | At-Risk Customers | At-Risk % | Trend | RAG |
|------|----------|--------------|-----------------|----------|-------|-----|
| 2016 | £67 | 0.64% | 0/4 | 0% | — STABLE | GREEN |
| 2017 | £290 | 0.12% | 0/10 | 0% | ↓ IMPROVING | GREEN |
| 2018 | £491 | 0.11% | 1/11 | 9% | — STABLE | GREEN |
| 2019 | £24 | 0.00% | 3/12 | 25% | ↓ IMPROVING | GREEN |
| 2020 | £-18 | -0.00% | 5/14 | 36% | ↓ IMPROVING | AMBER |
| 2021 | £593 | 0.03% | 4/11 | 36% | ↑ DETERIORATING | AMBER |
| 2022 | £63 | 0.00% | 9/11 | 82% | ↓ IMPROVING | RED |
| 2023 | £2,157 | 0.08% | 10/11 | 91% | ↑ DETERIORATING | RED |
| 2024 | £-119 | -0.01% | 4/11 | 36% | ↓ IMPROVING | AMBER |
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
| 2016 | £2,472,079.21 | £1,192.45 | 2073.1x | ✓ GREEN | Yes |
| 2017 | £2,585,274.22 | £28,923.04 | 89.4x | ✓ GREEN | Yes |
| 2018 | £2,830,605.65 | £49,954.71 | 56.7x | ✓ GREEN | Yes |
| 2019 | £3,492,630.33 | £136,968.32 | 25.5x | ✓ GREEN | Yes |
| 2020 | £4,235,097.53 | £154,597.21 | 27.4x | ✓ GREEN | Yes |
| 2021 | £4,935,728.88 | £201,204.53 | 24.5x | ✓ GREEN | Yes |
| 2022 | £5,872,509.80 | £353,295.13 | 16.6x | ✓ GREEN | Yes |
| 2023 | £6,727,861.79 | £289,313.59 | 23.2x | ✓ GREEN | Yes |
| 2024 | £7,898,810.48 | £249,863.44 | 31.6x | ✓ GREEN | Yes |
| 2025 | £8,368,751.70 | £102,297.42 | 81.8x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.6x (equity £5,872,509.80 vs monthly revenue £353,295.13). RAG: GREEN.
**Strongest year:** 2016 — 2073.1x.

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
| 2016 | £14,309.39 | £5,318.32 | £45.21 | ✓ GREEN |  |
| 2017 | £347,076.42 | £128,996.74 | £1,096.47 | ✓ GREEN |  |
| 2018 | £599,456.46 | £222,797.98 | £1,893.78 | ✓ GREEN |  |
| 2019 | £1,643,619.82 | £610,878.70 | £5,192.47 | ✓ GREEN |  |
| 2020 | £1,855,166.54 | £689,503.57 | £5,860.78 | ✓ GREEN |  |
| 2021 | £2,414,454.41 | £897,372.22 | £7,627.66 | ✓ GREEN | CREDIT EXPECTED |
| 2022 | £4,239,541.60 | £1,575,696.30 | £13,393.42 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,471,763.08 | £1,290,338.61 | £10,967.88 | ✓ GREEN |  |
| 2024 | £2,998,361.29 | £1,114,390.95 | £9,472.32 | ✓ GREEN |  |
| 2025 | £1,227,569.03 | £456,246.49 | £3,878.10 | ✓ GREEN |  |

**Peak reconciliation exposure:** 2022 — max adverse £13,393 (4.5 months weighted tail).

_Note: Outstanding pool ≈ current-year revenue × (weighted outstanding months ÷ 12)._
_Max adverse = pool × blended variance rate (0.5% HH + 4% non-HH, portfolio-weighted)._
## Ofgem Supply Licence Health (Phase OC)

Annual licence health checks: customer base, net assets, liquidity, bad debt.
Breach triggers board escalation and Ofgem notification under SLC 0.
WATCH = within 20% of threshold. BREACH = threshold crossed.

| Year | Customers | Net Assets | Treasury | Cash Wks | Bad Debt % | Overall |
|------|-----------|------------|----------|----------|------------|---------|
| 2016 | 13 | £2,472,079.21 | £2,467,441.30 | 35691w | 0.64% | ✗ BREACH |
| 2017 | 14 | £2,585,274.22 | £2,498,923.22 | 1170w | 0.12% | ✗ BREACH |
| 2018 | 15 | £2,830,605.65 | £2,487,909.17 | 748w | 0.11% | ✗ BREACH |
| 2019 | 17 | £3,492,630.33 | £2,611,898.08 | 274w | 0.00% | ✗ BREACH |
| 2020 | 19 | £4,235,097.53 | £2,924,313.47 | 352w | -0.00% | ✗ BREACH |
| 2021 | 14 | £4,935,728.88 | £2,957,780.33 | 158w | 0.03% | ✗ BREACH |
| 2022 | 14 | £5,872,509.80 | £3,161,734.24 | 69w | 0.00% | ✗ BREACH |
| 2023 | 14 | £6,727,861.79 | £3,382,315.78 | 107w | 0.08% | ✗ BREACH |
| 2024 | 14 | £7,898,810.48 | £3,774,998.77 | 211w | -0.01% | ✗ BREACH |
| 2025 | 11 | £8,368,751.70 | £3,826,938.07 | 440w | 0.00% | ✗ BREACH |

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
| 2016 | Yes | 13/13/13 | 0.1 | 0.0 | £5 |
| 2017 | Yes | 14/14/14 | 1.5 | 0.1 | £21 |
| 2018 | Yes | 15/15/15 | 2.9 | 0.1 | £33 |
| 2019 | Yes | 17/17/17 | 7.1 | 2.8 | £1 |
| 2020 | Yes | 19/19/19 | 7.3 | 2.4 | £-1 |
| 2021 | Yes | 14/14/14 | 9.6 | 6.0 | £42 |
| 2022 | Yes | 14/14/14 | 19.0 | 11.8 | £4 |
| 2023 | Yes | 14/14/14 | 15.3 | 6.0 | £154 |
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
| 2016 | 0.820 | 0.050 | 0 | 0 |  |
| 2017 | 0.810 | 0.049 | 0 | 0 |  |
| 2018 | 0.802 | 0.049 | 0 | 0 |  |
| 2019 | 0.817 | 0.049 | 0 | 0 |  |
| 2020 | 0.826 | 0.045 | 2 | 0 |  |
| 2021 | 0.811 | 0.050 | 0 | 0 |  |
| 2022 | 0.787 | 0.058 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.808 | 0.049 | 0 | 0 |  |
| 2024 | 0.813 | 0.047 | 2 | 0 |  |
| 2025 | 0.775 | 0.061 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.0% | **Average billing clarity:** 0.809 | **Average complaint probability:** 0.050

**Acquisition performance:** 4 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2025** (0.775) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

## Bill Shock Analysis

Bill shock events occur when a customer's bill increases >20% vs the prior bill.
Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.

| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |
|------|------------|--------|-------|------------|------|
| 2016 | 22.0% | 35 | 108 | 32% | ELEVATED |
| 2017 | 18.1% | 56 | 168 | 33% |  |
| 2018 | 17.5% | 64 | 180 | 36% |  |
| 2019 | 18.5% | 68 | 204 | 33% |  |
| 2020 | 15.5% | 58 | 205 | 28% |  |
| 2021 | 25.2% | 49 | 168 | 29% | ELEVATED |
| 2022 | 23.8% | 73 | 168 | 43% | ELEVATED |
| 2023 | 18.0% | 49 | 168 | 29% |  |
| 2024 | 16.8% | 41 | 153 | 27% |  |
| 2025 | 24.9% | 26 | 66 | 39% | ELEVATED |

**Crisis peak: 2021** — 25.2% average shock. Energy crisis drove wholesale costs above locked tariff rates,
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
| 2017 | £31,137.06 | £516.54 | £231,633.78 | £2,660.42 | 1.1% | YES |
| 2018 | £101,120.97 | £436.94 | £432,365.68 | £3,113.94 | 0.7% | YES |
| 2019 | £223,622.54 | £10,489.65 | £1,060,516.66 | £137,766.14 | 11.5% | YES |
| 2020 | £118,022.61 | £10,488.12 | £1,102,193.08 | £121,119.88 | 9.9% | YES |
| 2021 | £65,418.20 | £9,830.33 | £1,437,504.91 | £297,399.17 | 17.1% | YES |
| 2022 | £329,615.83 | £8,740.82 | £2,848,806.28 | £589,446.82 | 17.1% | YES |
| 2023 | £135,388.70 | £9,023.55 | £2,296,002.86 | £298,691.57 | 11.5% | YES |
| 2024 | £337,111.82 | £10,708.88 | £1,917,076.86 | £271,569.81 | 12.4% | YES |
| 2025 | £116,452.84 | £4,540.12 | £837,702.08 | £132,970.11 | 13.7% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £203,664.85 | — | Current strategy |
| EXIT_GAS | £83,517.04 | £-120,147.81 | Remove gas; model elec churn risk |
| REPRICE_GAS | £205,376.17 | £1,711.32 | Raise gas tariff to break-even |

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
| SME electricity | £30,536.93 | £326.30 | £1,818.58 | 5.6x | Moderate |
| resi electricity | £55,053.10 | £614.51 | £6,495.82 | 10.6x | Moderate |
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
| C3+C3g | £189.71 | £336.46 | £526.18 | Yes |
| C4+C4g | £91.42 | £-1,711.32 | £-1,619.90 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £65,099.25.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,523,952.37 across 19 billing accounts. Revenue: £14,028,957.18.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,123,873.83 | £1,875,002.30 | £18,435.60 | £846,747.11 | 27.1% |
| 2 | C_IC2 | fixed | £1,524,534.49 | £909,010.15 | £8,630.44 | £434,893.78 | 28.5% |
| 3 | C_IC3 | pass_through | £4,629,960.35 | £1,825,093.54 | £23,102.67 | £136,677.18 | 3.0% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £64,510.98 | 3.5% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £32,220.65 | 1.2% |
| 6 | C8 | fixed | £21,649.27 | £12,429.82 | £134.60 | £2,291.54 | 10.6% |
| 7 | C9 | fixed | £20,244.05 | £12,708.53 | £131.44 | £2,240.28 | 11.1% |
| 8 | C6 | fixed | £39,190.43 | £22,706.35 | £266.16 | £1,986.66 | 5.1% |
| 9 | C2g | fixed | £8,090.72 | £3,287.48 | £106.78 | £1,293.99 | 16.0% |
| 10 | C2 | fixed | £9,515.76 | £5,522.81 | £58.28 | £1,177.20 | 12.4% |
| 11 | C1g | fixed | £2,436.42 | £1,355.24 | £15.79 | £669.14 | 27.5% |
| 12 | C1_2 | fixed | £11,629.63 | £5,662.84 | £81.65 | £648.00 | 5.6% |
| 13 | C1 | fixed | £3,545.67 | £2,343.04 | £14.71 | £430.09 | 12.1% |
| 14 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £336.46 | 12.5% |
| 15 | C3 | fixed | £3,628.76 | £2,388.88 | £14.77 | £189.71 | 5.2% |
| 16 | C4 | fixed | £6,193.87 | £3,243.30 | £37.88 | £91.42 | 1.5% |
| 17 | C5 | fixed | £12,497.06 | £7,830.58 | £60.14 | £-168.08 | -1.3% |
| 18 | C7 | fixed | £21,729.00 | £10,753.88 | £141.17 | £-572.42 | -2.6% |
| 19 | C4g | fixed | £10,335.76 | £1,243.04 | £130.00 | £-1,711.32 | -16.6% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,028,957 | 100.0% |
| Wholesale cost | -£7,597,745 | 54.2% |
| **Gross supply margin** | **£6,431,213** | **45.8%** |
| Policy + Network costs | -£4,855,883 | 34.6% |
| Capital cost | -£51,377 | 0.4% |
| **Net supply margin** | **£1,523,952** | **10.9%** |

> *The ledger's `net_margin_gbp` (£6,379,835) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,023,008 | 47.5% | 12.1% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 3.5% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £51,687 | 59.1% | 3.5% | CMA 3-8% | ✓ |
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
| Customer bills (all-in) | £22,549,583.84 |
|   Less: VAT remitted to HMRC | (£3,738,265.80) |
| = Revenue (ex-VAT) | £18,811,318.04 |
| Less: non-commodity pass-through | (£4,782,360.86) |
| Wholesale cost (settlement events) | (£7,597,744.58) |
| Gross margin | £6,431,212.61 |
| Capital charges | (£51,377.37) |
| Net margin | £6,379,835.24 |

_Cash reconciliation: of £22,549,583.84 billed, bad debt of £451,110.71 was written off, leaving £22,098,473.14 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £9,666,990.33._

| Acquisition spend | (£862.50) |
| Fixed overhead | (£5,700.00) |
| Cost to serve | (£18,730.56) |
| Operating net margin | £6,354,542.18 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £14,309.39 | £3,594.97 | £3,892.24 | £6,822.19 | £216.79 | £1,292.86 | £5,442.99 (38.0%) |
| 2017 | £347,076.42 | £111,055.46 | £112,782.22 | £123,238.74 | £7,040.69 | £8,770.15 | £113,195.01 (32.6%) |
| 2018 | £599,456.46 | £172,888.20 | £163,976.85 | £262,591.42 | £13,390.38 | £15,619.50 | £245,331.43 (40.9%) |
| 2019 | £1,643,619.82 | £496,185.23 | £445,337.03 | £702,097.56 | £35,007.34 | £37,746.49 | £662,024.68 (40.3%) |
| 2020 | £1,855,166.54 | £431,600.88 | £631,853.58 | £791,712.09 | £43,610.85 | £47,278.66 | £742,467.20 (40.0%) |
| 2021 | £2,414,454.41 | £971,905.80 | £679,550.33 | £762,998.28 | £53,702.02 | £56,764.31 | £700,631.35 (29.0%) |
| 2022 | £4,239,541.60 | £2,389,086.10 | £801,288.51 | £1,049,166.99 | £96,047.89 | £99,109.75 | £936,780.91 (22.1%) |
| 2023 | £3,471,763.08 | £1,639,053.05 | £877,068.66 | £955,641.38 | £87,191.30 | £90,252.89 | £855,351.99 (24.6%) |
| 2024 | £2,998,361.29 | £931,630.07 | £809,714.61 | £1,257,016.60 | £73,169.72 | £76,545.88 | £1,170,948.69 (39.1%) |
| 2025 | £1,227,569.03 | £452,060.81 | £256,896.84 | £518,611.38 | £41,733.73 | £43,023.27 | £469,941.23 (38.3%) |
| **Total** | **£18,811,318.04** | | | | | | **£5,902,115.48 (31.4%)** |

**Best year:** 2024 — net £1,170,948.69 (39.1% margin)
**Worst year:** 2016 — net £5,442.99 (38.0% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,368,751.70 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,368,751.70** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,902,115.48 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £14,309.39 | -2.5% | £6,592.99 | £5,442.99 | -17.4% | RED |
| 2017 | £16,138.86 | £347,076.42 | +2050.6% | £7,252.29 | £113,195.01 | +1460.8% | RED |
| 2018 | £386,623.75 | £599,456.46 | +55.0% | £128,424.00 | £245,331.43 | +91.0% | RED |
| 2019 | £675,851.95 | £1,643,619.82 | +143.2% | £281,335.50 | £662,024.68 | +135.3% | RED |
| 2020 | £1,816,630.04 | £1,855,166.54 | +2.1% | £736,963.94 | £742,467.20 | +0.7% | GREEN |
| 2021 | £2,028,952.42 | £2,414,454.41 | +19.0% | £833,649.22 | £700,631.35 | -16.0% | RED |
| 2022 | £2,607,611.88 | £4,239,541.60 | +62.6% | £790,935.58 | £936,780.91 | +18.4% | RED |
| 2023 | £4,508,414.67 | £3,471,763.08 | -23.0% | £1,029,561.00 | £855,351.99 | -16.9% | RED |
| 2024 | £3,512,844.39 | £2,998,361.29 | -14.6% | £893,105.75 | £1,170,948.69 | +31.1% | RED |
| 2025 | £3,145,356.42 | £1,227,569.03 | -61.0% | £1,315,150.33 | £469,941.23 | -64.3% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,373,272.74

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
- Bill shock events (>=20%): 35 -- C1 2016-04-30 (21%); C1g 2016-05-31 (42%); C1g 2016-06-30 (35%); C1g 2016-10-31 (107%); C1g 2016-11-30 (55%); C5 2016-04-30 (20%); C5 2016-05-31 (28%); C5 2016-06-30 (21%); C5 2016-10-31 (44%); C5 2016-11-30 (46%); C7 2016-04-30 (22%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-10-31 (83%); C7 2016-11-30 (54%); C2g 2016-05-31 (39%); C2g 2016-06-30 (39%); C2g 2016-10-31 (102%); C2g 2016-11-30 (60%); C6 2016-05-31 (27%); C6 2016-06-30 (24%); C6 2016-10-31 (43%); C6 2016-11-30 (49%); C8 2016-05-31 (41%); C8 2016-06-30 (43%); C8 2016-09-30 (25%); C8 2016-10-31 (111%); C8 2016-11-30 (72%); C3g 2016-10-31 (84%); C3g 2016-11-30 (53%); C9 2016-09-30 (20%); C9 2016-10-31 (80%); C9 2016-11-30 (61%); C4 2016-11-30 (36%); C4g 2016-11-30 (50%)
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
- Bills issued: 108, average clarity 0.820, average bill shock 22.0%, bad debt provision £66.56, avg complaint probability 5.0%
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

**Year narrative:** 2016 produced a net gain of £1,286.83 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 35 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £31,653.60 (gross £123,238.74, capital £1,273.58)
  - Electricity: gross £121,809.17, capital £1,258.73, net £31,137.06
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
- Worst single period: C5 on 2017-12-31 period 48, net margin £-201.15

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £11,762.47
  - By billing account: C1 £5,740.27, C2 £11,364.56, C3 £9,644.02, C4 £8,744.86, C5 £12,167.53, C6 £24,200.80, C7 £8,895.16, C8 £13,842.89, C9 £11,262.19
- Bill shock events (>=20%): 56 -- C1 2017-04-30 (21%); C1g 2017-01-31 (35%); C1g 2017-02-28 (30%); C1g 2017-05-31 (34%); C1g 2017-06-30 (36%); C1g 2017-09-30 (29%); C1g 2017-10-31 (23%); C1g 2017-11-30 (87%); C1g 2017-12-31 (21%); C5 2017-01-31 (26%); C5 2017-02-28 (23%); C5 2017-05-31 (21%); C5 2017-06-30 (22%); C5 2017-11-30 (59%); C7 2017-01-31 (34%); C7 2017-02-28 (28%); C7 2017-05-31 (31%); C7 2017-06-30 (33%); C7 2017-09-30 (28%); C7 2017-10-31 (22%); C7 2017-11-30 (78%); C2g 2017-05-31 (38%); C2g 2017-06-30 (33%); C2g 2017-09-30 (34%); C2g 2017-11-30 (75%); C2g 2017-12-31 (23%); C6 2017-05-31 (23%); C6 2017-06-30 (21%); C6 2017-11-30 (53%); C8 2017-05-31 (40%); C8 2017-06-30 (37%); C8 2017-09-30 (48%); C8 2017-10-31 (23%); C8 2017-11-30 (85%); C8 2017-12-31 (22%); C3g 2017-05-31 (33%); C3g 2017-06-30 (25%); C3g 2017-09-30 (26%); C3g 2017-11-30 (67%); C9 2017-05-31 (33%); C9 2017-06-30 (27%); C9 2017-09-30 (31%); C9 2017-10-31 (22%); C9 2017-11-30 (73%); C4 2017-04-30 (33%); C4 2017-09-30 (28%); C4 2017-10-31 (30%); C4 2017-11-30 (33%); C4g 2017-01-31 (24%); C4g 2017-02-28 (22%); C4g 2017-05-31 (35%); C4g 2017-06-30 (38%); C4g 2017-09-30 (42%); C4g 2017-10-31 (24%); C4g 2017-11-30 (76%); C4g 2017-12-31 (21%)
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
- C5 (electricity): tariff £119.54-£131.01/MWh, net margin £-36.46 -- **net-negative**
- C6 (electricity): tariff £107.62-£126.91/MWh, net margin £98.49
- C7 (electricity): tariff £96.43-£195.85/MWh, net margin £194.36
- C8 (electricity): tariff £84.56-£191.05/MWh, net margin £246.35
- C9 (electricity): tariff £77.16-£181.43/MWh, net margin £166.16
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £30,139.92

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.810, average bill shock 18.1%, bad debt provision £289.77, avg complaint probability 4.9%
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

**Year narrative:** 2017 produced a net gain of £31,653.60 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 56 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £101,557.91 (gross £262,602.37, capital £1,640.49)
  - Electricity: gross £261,239.56, capital £1,619.42, net £101,120.97
  - Gas: gross £1,362.80, capital £21.07, net £436.94
- Treasury at year end: £2,487,909.17
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.91 (avg 0.91)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2018-12-31 period 48, net margin £-423.75

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £288,605.58
  - By billing account: C1 £5,706.06, C2 £8,726.77, C3 £9,643.83, C4 £7,300.25, C5 £12,344.35, C6 £20,424.84, C7 £8,038.55, C8 £10,898.61, C9 £10,640.88, C_IC1 £2,792,331.69
- Bill shock events (>=20%): 64 -- C1g 2018-04-30 (40%); C1g 2018-05-31 (33%); C1g 2018-06-30 (35%); C1g 2018-09-30 (34%); C1g 2018-10-31 (56%); C1g 2018-11-30 (31%); C5 2018-04-30 (33%); C5 2018-06-30 (21%); C5 2018-10-31 (33%); C5 2018-11-30 (28%); C7 2018-04-30 (39%); C7 2018-05-31 (29%); C7 2018-06-30 (31%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C2g 2018-04-30 (29%); C2g 2018-05-31 (37%); C2g 2018-06-30 (38%); C2g 2018-08-31 (22%); C2g 2018-09-30 (41%); C2g 2018-10-31 (51%); C2g 2018-11-30 (21%); C6 2018-04-30 (24%); C6 2018-05-31 (22%); C6 2018-06-30 (23%); C6 2018-10-31 (31%); C6 2018-11-30 (23%); C8 2018-04-30 (36%); C8 2018-05-31 (38%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (56%); C8 2018-11-30 (30%); C3g 2018-04-30 (30%); C3g 2018-05-31 (35%); C3g 2018-06-30 (32%); C3g 2018-08-31 (43%); C3g 2018-09-30 (41%); C3g 2018-10-31 (39%); C3g 2018-12-31 (24%); C9 2018-04-30 (32%); C9 2018-05-31 (35%); C9 2018-06-30 (35%); C9 2018-07-31 (23%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-04-30 (32%); C4 2018-09-30 (29%); C4 2018-10-31 (50%); C4 2018-11-30 (33%); C4g 2018-04-30 (37%); C4g 2018-05-31 (36%); C4g 2018-06-30 (40%); C4g 2018-08-31 (23%); C4g 2018-09-30 (45%); C4g 2018-10-31 (93%); C4g 2018-11-30 (26%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
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
- C5 (electricity): tariff £119.54-£153.61/MWh, net margin £-630.62 -- **net-negative**
- C6 (electricity): tariff £126.91-£142.20/MWh, net margin £-6.78 -- **net-negative**
- C7 (electricity): tariff £96.43-£221.22/MWh, net margin £-15.12 -- **net-negative**
- C8 (electricity): tariff £100.07-£200.72/MWh, net margin £164.50
- C9 (electricity): tariff £95.03-£198.37/MWh, net margin £242.67
- C_IC1 (electricity): tariff £-82.12-£228.58/MWh, net margin £107,506.53
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,382.25 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.802, average bill shock 17.5%, bad debt provision £491.45, avg complaint probability 4.9%
- Solvency signal: £226,174/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2018 produced a net gain of £101,557.91 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 64 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £234,112.18 (gross £702,100.60, capital £2,326.39)
  - Electricity: gross £626,046.76, capital £2,304.94, net £223,622.54
  - Gas: gross £76,053.84, capital £21.46, net £10,489.65
- Treasury at year end: £2,611,898.08
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C3 on 2019-12-31 period 48, net margin £-87.83

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £383,128.28
  - By billing account: C1 £5,661.65, C2 £8,873.94, C3 £8,256.51, C4 £6,507.79, C5 £11,192.06, C6 £19,074.59, C7 £8,373.08, C8 £9,472.90, C9 £9,974.34, C_IC1 £2,348,957.18, C_IC2 £1,778,067.01
- Bill shock events (>=20%): 68 -- C1 2019-04-30 (22%); C1g 2019-01-31 (40%); C1g 2019-02-28 (27%); C1g 2019-05-31 (26%); C1g 2019-06-30 (40%); C1g 2019-10-31 (91%); C1g 2019-11-30 (50%); C5 2019-01-31 (44%); C5 2019-02-28 (22%); C5 2019-06-30 (26%); C5 2019-10-31 (45%); C5 2019-11-30 (37%); C7 2019-01-31 (46%); C7 2019-02-28 (26%); C7 2019-05-31 (24%); C7 2019-06-30 (35%); C7 2019-10-31 (72%); C7 2019-11-30 (46%); C2g 2019-01-31 (27%); C2g 2019-02-28 (27%); C2g 2019-04-30 (37%); C2g 2019-06-30 (35%); C2g 2019-07-31 (30%); C2g 2019-09-30 (40%); C2g 2019-10-31 (76%); C2g 2019-11-30 (31%); C6 2019-02-28 (21%); C6 2019-06-30 (25%); C6 2019-09-30 (20%); C6 2019-10-31 (44%); C6 2019-11-30 (28%); C8 2019-01-31 (28%); C8 2019-02-28 (28%); C8 2019-04-30 (22%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-09-30 (61%); C8 2019-10-31 (88%); C8 2019-11-30 (38%); C3 2019-04-30 (21%); C3g 2019-02-28 (27%); C3g 2019-04-30 (20%); C3g 2019-06-30 (36%); C3g 2019-07-31 (40%); C3g 2019-09-30 (44%); C3g 2019-10-31 (73%); C3g 2019-11-30 (34%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (37%); C9 2019-07-31 (35%); C9 2019-09-30 (53%); C9 2019-10-31 (76%); C9 2019-11-30 (38%); C4 2019-04-30 (35%); C4 2019-09-30 (33%); C4 2019-11-30 (30%); C4g 2019-01-31 (31%); C4g 2019-02-28 (25%); C4g 2019-05-31 (22%); C4g 2019-06-30 (35%); C4g 2019-07-31 (40%); C4g 2019-09-30 (36%); C4g 2019-10-31 (37%); C4g 2019-11-30 (38%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C1 29%, C4 35%, C5 35%, C7 29%, C9 23%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £99.01-£224.86/MWh, net margin £122.17
- C1g (gas): tariff £25.33-£36.05/MWh, net margin £156.37
- C2 (electricity): tariff £113.09-£227.85/MWh, net margin £145.70
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £134.46
- C3 (electricity): tariff £120.68-£126.89/MWh, net margin £-62.19 -- **net-negative**
- C3g (gas): tariff £23.00-£28.80/MWh, net margin £97.85
- C4 (electricity): tariff £99.60-£224.05/MWh, net margin £112.89
- C4g (gas): tariff £19.47-£33.61/MWh, net margin £101.05
- C5 (electricity): tariff £126.07-£153.61/MWh, net margin £230.66
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
- Bills issued: 204, average clarity 0.817, average bill shock 18.5%, bad debt provision £23.55, avg complaint probability 4.9%
- Solvency signal: £217,658/customer (12 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2019 produced a net gain of £234,112.18 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 68 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £128,510.73 (gross £791,769.73, capital £1,966.22)
  - Electricity: gross £714,590.18, capital £1,955.93, net £118,022.61
  - Gas: gross £77,179.55, capital £10.29, net £10,488.12
- Treasury at year end: £2,924,313.47
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
- Bill shock events (>=20%): 58 -- C1 2020-04-30 (22%); C1g 2020-01-31 (22%); C1g 2020-04-30 (35%); C1g 2020-05-31 (22%); C1g 2020-06-30 (30%); C1g 2020-10-31 (71%); C1g 2020-11-30 (20%); C1g 2020-12-29 (27%); C5 2020-04-30 (30%); C5 2020-10-31 (39%); C5 2020-11-30 (20%); C7 2020-04-30 (35%); C7 2020-05-31 (21%); C7 2020-06-30 (28%); C7 2020-10-31 (62%); C7 2020-11-30 (24%); C7 2020-12-31 (35%); C2 2020-04-30 (25%); C2g 2020-04-30 (39%); C2g 2020-05-31 (20%); C2g 2020-06-30 (29%); C2g 2020-09-30 (35%); C2g 2020-10-31 (56%); C2g 2020-12-31 (42%); C6 2020-04-30 (30%); C6 2020-09-30 (22%); C6 2020-10-31 (35%); C6 2020-12-31 (27%); C8 2020-04-30 (36%); C8 2020-05-31 (26%); C8 2020-06-30 (33%); C8 2020-09-30 (57%); C8 2020-10-31 (68%); C8 2020-12-31 (44%); C3 2020-04-30 (20%); C3g 2020-04-30 (25%); C3g 2020-05-31 (23%); C3g 2020-06-29 (37%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-09-30 (46%); C9 2020-10-31 (51%); C9 2020-12-31 (37%); C4 2020-04-30 (35%); C4 2020-09-30 (27%); C4 2020-10-31 (26%); C4 2020-11-30 (29%); C4g 2020-04-30 (36%); C4g 2020-05-31 (22%); C4g 2020-06-30 (29%); C4g 2020-09-30 (36%); C4g 2020-10-31 (55%); C4g 2020-12-31 (38%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 35%, C4 41%, C5 32%, C7 20%, C8 23%, C9 23%, C_IC1 41%, C_IC2 41%, C_IC3 20%

**Pricing & Margin**

- C1 (electricity): tariff £99.01-£189.01/MWh, net margin £99.21
- C1_2 (electricity): tariff £133.55/MWh, net margin £-1.02 -- **net-negative**
- C1g (gas): tariff £25.33/MWh, net margin £145.23
- C2 (electricity): tariff £113.06-£227.85/MWh, net margin £201.59
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £143.77
- C3 (electricity): tariff £120.68/MWh, net margin £44.15
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
- Bills issued: 205, average clarity 0.826, average bill shock 15.5%, bad debt provision £-18.21, avg complaint probability 4.5%
- Solvency signal: £208,880/customer (14 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2020 produced a net gain of £128,510.73 across 19 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 58 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £75,248.53 (gross £763,155.26, capital £5,602.62)
  - Electricity: gross £680,540.29, capital £5,590.58, net £65,418.20
  - Gas: gross £82,614.97, capital £12.04, net £9,830.33
- Treasury at year end: £2,957,780.33
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.87 (avg 0.87), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2021-12-31 period 48, net margin £-526.35

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2021): £409,271.50
  - By billing account: C1 £4,744.82, C1_2 £986.91, C2 £6,791.99, C3 £5,831.99, C4 £5,409.21, C5 £12,050.99, C6 £17,951.57, C7 £6,973.39, C8 £9,219.23, C9 £8,492.59, C_IC1 £1,502,450.85, C_IC2 £765,170.10, C_IC3 £2,019,710.36, C_IC4 £1,364,017.02
- Bill shock events (>=20%): 49 -- C7 2021-05-31 (30%); C7 2021-06-30 (47%); C7 2021-10-31 (55%); C7 2021-11-30 (65%); C2 2021-11-30 (21%); C2g 2021-02-28 (20%); C2g 2021-04-30 (35%); C2g 2021-05-31 (26%); C2g 2021-06-30 (58%); C2g 2021-10-31 (67%); C2g 2021-11-30 (66%); C6 2021-06-30 (36%); C6 2021-10-31 (28%); C6 2021-11-30 (52%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (25%); C8 2021-10-31 (69%); C8 2021-11-30 (84%); C9 2021-02-28 (22%); C9 2021-05-31 (25%); C9 2021-06-30 (51%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-10-31 (63%); C9 2021-11-30 (50%); C9 2021-12-31 (24%); C4 2021-04-30 (35%); C4 2021-09-30 (30%); C4 2021-10-31 (53%); C4 2021-11-30 (38%); C4g 2021-05-31 (24%); C4g 2021-06-30 (57%); C4g 2021-10-31 (132%); C4g 2021-11-30 (61%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%); C1_2 2021-01-31 (1202%); C1_2 2021-05-31 (34%); C1_2 2021-06-30 (58%); C1_2 2021-10-31 (85%); C1_2 2021-11-30 (80%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C7 20%, C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £133.55-£333.14/MWh, net margin £-89.36 -- **net-negative**
- C2 (electricity): tariff £113.06-£274.50/MWh, net margin £198.84
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £126.10
- C4 (electricity): tariff £96.23-£274.50/MWh, net margin £-37.46 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-295.69 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.10/MWh, net margin £-0.69 -- **net-negative**
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
- Bills issued: 168, average clarity 0.811, average bill shock 25.2%, bad debt provision £592.79, avg complaint probability 5.0%
- Solvency signal: £268,889/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £75,248.53 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 49 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £338,356.66 (gross £1,049,224.77, capital £13,276.32)
  - Electricity: gross £958,836.70, capital £13,229.01, net £329,615.83
  - Gas: gross £90,388.06, capital £47.31, net £8,740.82
- Treasury at year end: £3,161,734.24
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
- Bill shock events (>=20%): 73 -- C7 2022-01-31 (53%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (35%); C7 2022-06-30 (26%); C7 2022-09-30 (32%); C7 2022-11-30 (61%); C7 2022-12-31 (55%); C2g 2022-02-28 (22%); C2g 2022-04-30 (69%); C2g 2022-05-31 (38%); C2g 2022-06-30 (31%); C2g 2022-07-31 (20%); C2g 2022-09-30 (65%); C2g 2022-11-30 (57%); C2g 2022-12-31 (63%); C6 2022-04-30 (44%); C6 2022-05-31 (24%); C6 2022-09-30 (26%); C6 2022-11-30 (44%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-05-31 (39%); C8 2022-06-30 (34%); C8 2022-07-31 (21%); C8 2022-09-30 (81%); C8 2022-11-30 (70%); C8 2022-12-31 (57%); C9 2022-04-30 (21%); C9 2022-05-31 (29%); C9 2022-06-30 (30%); C9 2022-09-30 (48%); C9 2022-10-31 (30%); C9 2022-11-30 (44%); C9 2022-12-31 (52%); C4 2022-04-30 (33%); C4 2022-09-30 (31%); C4 2022-10-31 (66%); C4 2022-11-30 (37%); C4g 2022-01-31 (26%); C4g 2022-02-28 (24%); C4g 2022-05-31 (36%); C4g 2022-06-30 (30%); C4g 2022-07-31 (25%); C4g 2022-09-30 (75%); C4g 2022-10-31 (146%); C4g 2022-11-30 (59%); C4g 2022-12-31 (57%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (109%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C1_2 2022-01-31 (146%); C1_2 2022-02-28 (28%); C1_2 2022-04-30 (24%); C1_2 2022-05-31 (44%); C1_2 2022-06-30 (36%); C1_2 2022-09-30 (54%); C1_2 2022-11-30 (82%); C1_2 2022-12-31 (62%)
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
- Treasury drawdown events (>=10% threshold): 2 -- £3,471,076.35 -> £3,053,214.40 (12.0%); £3,471,254.64 -> £3,052,668.60 (12.1%)
- Bills issued: 168, average clarity 0.787, average bill shock 23.8%, bad debt provision £63.03, avg complaint probability 5.8%
- Solvency signal: £287,430/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £338,356.66 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 73 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £144,412.25 (gross £955,881.82, capital £10,036.50)
  - Electricity: gross £834,588.49, capital £9,961.08, net £135,388.70
  - Gas: gross £121,293.34, capital £75.41, net £9,023.55
- Treasury at year end: £3,382,315.78
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.91 (avg 0.91), C2 0.95 (avg 0.95), C2g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,137,514.98, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-02-23: treasury £3,137,498.06, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-03-25: treasury £3,137,481.31, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-04-24: treasury £3,217,144.83, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,230.41 / stressed £48,907.75) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C6 on 2023-12-31 period 48, net margin £-1,995.37

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2023): £363,185.43
  - By billing account: C1 £3,680.74, C1_2 £1,944.13, C2 £4,982.25, C3 £4,440.04, C4 £2,107.60, C5 £7,623.31, C6 £17,306.38, C7 £5,356.78, C8 £7,277.99, C9 £6,952.69, C_IC1 £1,320,738.65, C_IC2 £640,507.44, C_IC3 £1,892,395.24, C_IC4 £1,169,282.75
- Bill shock events (>=20%): 49 -- C7 2023-01-31 (40%); C7 2023-05-31 (32%); C7 2023-06-30 (36%); C7 2023-10-31 (55%); C7 2023-11-30 (70%); C2 2023-04-30 (28%); C2g 2023-04-30 (35%); C2g 2023-05-31 (40%); C2g 2023-06-30 (40%); C2g 2023-10-31 (96%); C2g 2023-11-30 (60%); C6 2023-04-30 (32%); C6 2023-05-31 (24%); C6 2023-06-30 (23%); C6 2023-10-31 (39%); C6 2023-11-30 (44%); C8 2023-04-30 (30%); C8 2023-05-31 (40%); C8 2023-06-30 (43%); C8 2023-10-31 (96%); C8 2023-11-30 (68%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (33%); C9 2023-06-30 (45%); C9 2023-09-30 (21%); C9 2023-10-31 (74%); C9 2023-11-30 (53%); C4 2023-02-28 (26%); C4 2023-04-30 (34%); C4 2023-09-30 (29%); C4 2023-11-30 (32%); C4g 2023-05-31 (37%); C4g 2023-06-30 (46%); C4g 2023-10-31 (47%); C4g 2023-11-30 (67%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (101%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%); C1_2 2023-05-31 (39%); C1_2 2023-06-30 (45%); C1_2 2023-10-31 (78%); C1_2 2023-11-30 (86%)
- Churn risk (accounts renewing in 2023): 10 at risk (≥20% churn prob): C2 41%, C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.96-£267.80/MWh, net margin £-439.82 -- **net-negative**
- C2 (electricity): tariff £208.21-£457.50/MWh, net margin £88.59
- C2g (gas): tariff £70.00-£95.00/MWh, net margin £136.46
- C4 (electricity): tariff £198.37-£457.50/MWh, net margin £-13.16 -- **net-negative**
- C4g (gas): tariff £64.73-£95.00/MWh, net margin £-1,112.83 -- **net-negative**
- C6 (electricity): tariff £338.13-£412.09/MWh, net margin £-615.29 -- **net-negative**
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
- Treasury drawdown events (>=10% threshold): 47 -- £3,768,691.25 -> £3,382,241.18 (10.3%); £3,768,691.40 -> £3,382,241.18 (10.3%); £3,768,691.55 -> £3,382,241.17 (10.3%); £3,768,691.70 -> £3,382,241.17 (10.3%); £3,768,691.86 -> £3,382,241.17 (10.3%); £3,768,692.01 -> £3,382,241.17 (10.3%); £3,768,692.16 -> £3,382,241.17 (10.3%); £3,768,692.32 -> £3,382,241.17 (10.3%); £3,768,692.47 -> £3,382,241.17 (10.3%); £3,768,692.63 -> £3,382,241.17 (10.3%); £3,768,692.79 -> £3,382,241.17 (10.3%); £3,768,692.94 -> £3,382,241.17 (10.3%); £3,768,693.10 -> £3,382,241.16 (10.3%); £3,768,693.27 -> £3,382,241.16 (10.3%); £3,768,693.46 -> £3,382,241.15 (10.3%); £3,768,693.67 -> £3,382,241.15 (10.3%); £3,768,693.89 -> £3,382,241.14 (10.3%); £3,768,694.13 -> £3,382,241.13 (10.3%); £3,768,694.40 -> £3,382,241.11 (10.3%); £3,768,694.65 -> £3,382,241.10 (10.3%); £3,768,694.91 -> £3,382,241.09 (10.3%); £3,768,695.16 -> £3,382,241.08 (10.3%); £3,768,695.43 -> £3,382,241.06 (10.3%); £3,768,695.69 -> £3,382,241.05 (10.3%); £3,768,695.95 -> £3,382,241.04 (10.3%); £3,768,696.22 -> £3,382,241.02 (10.3%); £3,768,696.49 -> £3,382,241.01 (10.3%); £3,768,696.74 -> £3,382,241.00 (10.3%); £3,768,697.00 -> £3,382,240.99 (10.3%); £3,768,697.25 -> £3,382,240.98 (10.3%); £3,768,697.51 -> £3,382,240.98 (10.3%); £3,768,697.76 -> £3,382,240.97 (10.3%); £3,768,698.03 -> £3,382,240.95 (10.3%); £3,768,698.28 -> £3,382,240.93 (10.3%); £3,768,698.54 -> £3,382,240.91 (10.3%); £3,768,698.80 -> £3,382,240.89 (10.3%); £3,768,699.06 -> £3,382,240.86 (10.3%); £3,768,699.32 -> £3,382,240.83 (10.3%); £3,768,699.59 -> £3,382,240.80 (10.3%); £3,768,699.85 -> £3,382,240.77 (10.3%); £3,768,700.11 -> £3,382,240.74 (10.3%); £3,768,700.37 -> £3,382,240.71 (10.3%); £3,768,700.63 -> £3,382,240.69 (10.3%); £3,768,700.89 -> £3,382,240.68 (10.3%); £3,768,701.15 -> £3,382,240.67 (10.3%); £3,768,701.39 -> £3,382,240.66 (10.3%); £3,768,701.61 -> £3,381,636.56 (10.3%)
- Bills issued: 168, average clarity 0.808, average bill shock 18.0%, bad debt provision £2,157.28, avg complaint probability 4.9%
- Solvency signal: £307,483/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2023 produced a net gain of £144,412.25 across 14 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 49 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £347,820.71 (gross £1,257,805.74, capital £9,522.03)
  - Electricity: gross £1,132,855.54, capital £9,477.19, net £337,111.82
  - Gas: gross £124,950.20, capital £44.84, net £10,708.88
- Treasury at year end: £3,774,998.77
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
- Bill shock events (>=20%): 41 -- C7 2024-02-29 (27%); C7 2024-05-31 (37%); C7 2024-09-30 (34%); C7 2024-10-31 (37%); C7 2024-11-30 (48%); C2 2024-04-30 (34%); C2g 2024-02-29 (24%); C2g 2024-04-30 (37%); C2g 2024-05-31 (47%); C2g 2024-07-31 (25%); C2g 2024-09-30 (53%); C2g 2024-10-31 (34%); C2g 2024-11-30 (52%); C8 2024-02-29 (23%); C8 2024-04-30 (34%); C8 2024-05-31 (49%); C8 2024-07-31 (26%); C8 2024-09-30 (72%); C8 2024-10-31 (35%); C8 2024-11-30 (61%); C9 2024-05-31 (49%); C9 2024-07-31 (30%); C9 2024-09-30 (55%); C9 2024-10-31 (23%); C9 2024-11-30 (47%); C4 2024-04-30 (33%); C4g 2024-02-29 (27%); C4g 2024-05-31 (41%); C4g 2024-07-31 (26%); C4g 2024-09-28 (51%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C1_2 2024-01-31 (21%); C1_2 2024-02-29 (29%); C1_2 2024-04-30 (24%); C1_2 2024-05-31 (45%); C1_2 2024-09-30 (55%); C1_2 2024-10-31 (47%); C1_2 2024-11-30 (59%)
- Churn risk (accounts renewing in 2024): 8 at risk (≥20% churn prob): C2 41%, C4 38%, C6 26%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC3 41%, C_IC4 20%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01-£267.80/MWh, net margin £760.69
- C2 (electricity): tariff £157.80-£397.50/MWh, net margin £210.04
- C2g (gas): tariff £48.30-£70.00/MWh, net margin £265.39
- C4 (electricity): tariff £198.37-£378.70/MWh, net margin £114.48
- C4g (gas): tariff £64.73/MWh, net margin £412.73
- C6 (electricity): tariff £338.13/MWh, net margin £814.14
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
- Treasury drawdown events (>=10% threshold): 4271 -- £3,771,149.60 -> £3,381,636.63 (10.3%); £3,771,149.77 -> £3,381,636.67 (10.3%); £3,771,149.94 -> £3,381,636.70 (10.3%); £3,771,150.12 -> £3,381,636.74 (10.3%); £3,771,150.29 -> £3,381,636.78 (10.3%); £3,771,150.46 -> £3,381,636.81 (10.3%); £3,771,150.64 -> £3,381,636.85 (10.3%); £3,771,150.81 -> £3,381,636.89 (10.3%); £3,771,150.98 -> £3,381,636.92 (10.3%); £3,771,151.16 -> £3,381,636.96 (10.3%); £3,771,151.33 -> £3,381,637.00 (10.3%); £3,771,151.51 -> £3,381,637.18 (10.3%); £3,771,151.67 -> £3,381,637.36 (10.3%); £3,771,151.87 -> £3,381,637.56 (10.3%); £3,771,152.07 -> £3,381,637.77 (10.3%); £3,771,152.30 -> £3,381,638.01 (10.3%); £3,771,152.54 -> £3,381,638.26 (10.3%); £3,771,152.80 -> £3,381,638.54 (10.3%); £3,771,153.09 -> £3,381,638.82 (10.3%); £3,771,153.36 -> £3,381,638.94 (10.3%); £3,771,153.66 -> £3,381,639.07 (10.3%); £3,771,153.95 -> £3,381,639.19 (10.3%); £3,771,154.25 -> £3,381,639.32 (10.3%); £3,771,154.53 -> £3,381,639.44 (10.3%); £3,771,154.82 -> £3,381,639.57 (10.3%); £3,771,155.11 -> £3,381,639.69 (10.3%); £3,771,155.39 -> £3,381,639.80 (10.3%); £3,771,155.67 -> £3,381,639.91 (10.3%); £3,771,155.94 -> £3,381,640.02 (10.3%); £3,771,156.22 -> £3,381,640.14 (10.3%); £3,771,156.51 -> £3,381,640.26 (10.3%); £3,771,156.80 -> £3,381,640.37 (10.3%); £3,771,157.08 -> £3,381,640.66 (10.3%); £3,771,157.36 -> £3,381,640.91 (10.3%); £3,771,157.58 -> £3,381,641.14 (10.3%); £3,771,157.80 -> £3,381,641.35 (10.3%); £3,771,158.02 -> £3,381,641.57 (10.3%); £3,771,158.32 -> £3,381,641.77 (10.3%); £3,771,158.61 -> £3,381,641.98 (10.3%); £3,771,158.89 -> £3,381,642.19 (10.3%); £3,771,159.18 -> £3,381,642.39 (10.3%); £3,771,159.46 -> £3,381,642.58 (10.3%); £3,771,159.76 -> £3,381,642.77 (10.3%); £3,771,160.05 -> £3,381,642.82 (10.3%); £3,771,160.34 -> £3,381,642.86 (10.3%); £3,771,160.60 -> £3,381,642.90 (10.3%); £3,771,160.84 -> £3,381,642.94 (10.3%); £3,771,161.06 -> £3,381,642.98 (10.3%); £3,771,161.24 -> £3,381,643.02 (10.3%); £3,771,161.41 -> £3,381,643.06 (10.3%); £3,771,161.58 -> £3,381,643.10 (10.3%); £3,771,161.74 -> £3,381,643.14 (10.3%); £3,771,161.91 -> £3,381,643.18 (10.3%); £3,771,162.08 -> £3,381,643.22 (10.3%); £3,771,162.26 -> £3,381,643.26 (10.3%); £3,771,162.43 -> £3,381,643.30 (10.3%); £3,771,162.60 -> £3,381,643.34 (10.3%); £3,771,162.77 -> £3,381,643.38 (10.3%); £3,771,162.94 -> £3,381,643.42 (10.3%); £3,771,163.11 -> £3,381,643.58 (10.3%); £3,771,163.28 -> £3,381,643.75 (10.3%); £3,771,163.46 -> £3,381,643.92 (10.3%); £3,771,163.67 -> £3,381,644.11 (10.3%); £3,771,163.89 -> £3,381,644.33 (10.3%); £3,771,164.13 -> £3,381,644.56 (10.3%); £3,771,164.38 -> £3,381,644.83 (10.3%); £3,771,164.66 -> £3,381,645.10 (10.3%); £3,771,164.94 -> £3,381,645.24 (10.3%); £3,771,165.22 -> £3,381,645.36 (10.3%); £3,771,165.50 -> £3,381,645.48 (10.3%); £3,771,165.79 -> £3,381,645.62 (10.3%); £3,771,166.06 -> £3,381,645.75 (10.3%); £3,771,166.34 -> £3,381,645.86 (10.3%); £3,771,166.62 -> £3,381,645.98 (10.3%); £3,771,166.90 -> £3,381,646.10 (10.3%); £3,771,167.18 -> £3,381,646.21 (10.3%); £3,771,167.45 -> £3,381,646.32 (10.3%); £3,771,167.73 -> £3,381,646.43 (10.3%); £3,771,168.00 -> £3,381,646.54 (10.3%); £3,771,168.28 -> £3,381,646.65 (10.3%); £3,771,168.49 -> £3,381,646.89 (10.3%); £3,771,168.71 -> £3,381,647.12 (10.3%); £3,771,168.92 -> £3,381,647.32 (10.3%); £3,771,169.13 -> £3,381,647.50 (10.3%); £3,771,169.35 -> £3,381,647.67 (10.3%); £3,771,169.56 -> £3,381,647.84 (10.3%); £3,771,169.77 -> £3,381,648.00 (10.3%); £3,771,170.05 -> £3,381,648.16 (10.3%); £3,771,170.34 -> £3,381,648.33 (10.3%); £3,771,170.61 -> £3,381,648.49 (10.3%); £3,771,170.90 -> £3,381,648.65 (10.3%); £3,771,171.18 -> £3,381,648.69 (10.3%); £3,771,171.46 -> £3,381,648.73 (10.3%); £3,771,171.73 -> £3,381,648.77 (10.3%); £3,771,171.96 -> £3,381,648.81 (10.3%); £3,771,172.18 -> £3,381,648.84 (10.3%); £3,771,172.35 -> £3,381,648.88 (10.3%); £3,771,172.52 -> £3,381,648.92 (10.3%); £3,771,172.69 -> £3,381,648.95 (10.3%); £3,771,172.86 -> £3,381,648.99 (10.3%); £3,771,173.03 -> £3,381,649.03 (10.3%); £3,771,173.20 -> £3,381,649.06 (10.3%); £3,771,173.37 -> £3,381,649.10 (10.3%); £3,771,173.53 -> £3,381,649.14 (10.3%); £3,771,173.70 -> £3,381,649.18 (10.3%); £3,771,173.87 -> £3,381,649.21 (10.3%); £3,771,174.04 -> £3,381,649.26 (10.3%); £3,771,174.22 -> £3,381,649.44 (10.3%); £3,771,174.39 -> £3,381,649.63 (10.3%); £3,771,174.57 -> £3,381,649.83 (10.3%); £3,771,174.78 -> £3,381,650.05 (10.3%); £3,771,175.01 -> £3,381,650.29 (10.3%); £3,771,175.25 -> £3,381,650.53 (10.3%); £3,771,175.52 -> £3,381,650.79 (10.3%); £3,771,175.80 -> £3,381,651.06 (10.3%); £3,771,176.08 -> £3,381,651.18 (10.3%); £3,771,176.36 -> £3,381,651.30 (10.3%); £3,771,176.64 -> £3,381,651.43 (10.3%); £3,771,176.93 -> £3,381,651.55 (10.3%); £3,771,177.22 -> £3,381,651.67 (10.3%); £3,771,177.51 -> £3,381,651.79 (10.3%); £3,771,177.80 -> £3,381,651.90 (10.3%); £3,771,178.08 -> £3,381,652.02 (10.3%); £3,771,178.36 -> £3,381,652.14 (10.3%); £3,771,178.64 -> £3,381,652.26 (10.3%); £3,771,178.93 -> £3,381,652.37 (10.3%); £3,771,179.20 -> £3,381,652.49 (10.3%); £3,771,179.48 -> £3,381,652.60 (10.3%); £3,771,179.76 -> £3,381,652.86 (10.3%); £3,771,179.98 -> £3,381,653.13 (10.3%); £3,771,180.26 -> £3,381,653.35 (10.3%); £3,771,180.47 -> £3,381,653.55 (10.3%); £3,771,180.68 -> £3,381,653.74 (10.3%); £3,771,180.89 -> £3,381,653.92 (10.3%); £3,771,181.11 -> £3,381,654.12 (10.3%); £3,771,181.38 -> £3,381,654.31 (10.3%); £3,771,181.66 -> £3,381,654.50 (10.3%); £3,771,181.95 -> £3,381,654.68 (10.3%); £3,771,182.22 -> £3,381,654.85 (10.3%); £3,771,182.51 -> £3,381,654.89 (10.3%); £3,771,182.80 -> £3,381,654.93 (10.3%); £3,771,183.05 -> £3,381,654.97 (10.3%); £3,771,183.29 -> £3,381,655.00 (10.3%); £3,771,183.51 -> £3,381,655.04 (10.3%); £3,771,183.67 -> £3,381,655.08 (10.3%); £3,771,183.84 -> £3,381,655.12 (10.3%); £3,771,184.00 -> £3,381,655.16 (10.3%); £3,771,184.17 -> £3,381,655.19 (10.3%); £3,771,184.34 -> £3,381,655.23 (10.3%); £3,771,184.51 -> £3,381,655.27 (10.3%); £3,771,184.68 -> £3,381,655.31 (10.3%); £3,771,184.84 -> £3,381,655.35 (10.3%); £3,771,185.01 -> £3,381,655.39 (10.3%); £3,771,185.18 -> £3,381,655.42 (10.3%); £3,771,185.35 -> £3,381,655.46 (10.3%); £3,771,185.52 -> £3,381,655.67 (10.3%); £3,771,185.69 -> £3,381,655.88 (10.3%); £3,771,185.88 -> £3,381,656.10 (10.3%); £3,771,186.08 -> £3,381,656.33 (10.3%); £3,771,186.30 -> £3,381,656.57 (10.3%); £3,771,186.54 -> £3,381,656.85 (10.3%); £3,771,186.80 -> £3,381,657.15 (10.3%); £3,771,187.08 -> £3,381,657.46 (10.3%); £3,771,187.35 -> £3,381,657.59 (10.3%); £3,771,187.64 -> £3,381,657.71 (10.3%); £3,771,187.91 -> £3,381,657.84 (10.3%); £3,771,188.19 -> £3,381,657.97 (10.3%); £3,771,188.47 -> £3,381,658.09 (10.3%); £3,771,188.74 -> £3,381,658.21 (10.3%); £3,771,189.02 -> £3,381,658.32 (10.3%); £3,771,189.30 -> £3,381,658.43 (10.3%); £3,771,189.58 -> £3,381,658.54 (10.3%); £3,771,189.85 -> £3,381,658.66 (10.3%); £3,771,190.13 -> £3,381,658.77 (10.3%); £3,771,190.41 -> £3,381,658.88 (10.3%); £3,771,190.69 -> £3,381,658.98 (10.3%); £3,771,190.90 -> £3,381,659.28 (10.3%); £3,771,191.17 -> £3,381,659.56 (10.3%); £3,771,191.45 -> £3,381,659.79 (10.3%); £3,771,191.65 -> £3,381,660.01 (10.3%); £3,771,191.92 -> £3,381,660.23 (10.3%); £3,771,192.20 -> £3,381,660.43 (10.3%); £3,771,192.42 -> £3,381,660.63 (10.3%); £3,771,192.70 -> £3,381,660.83 (10.3%); £3,771,192.97 -> £3,381,661.03 (10.3%); £3,771,193.26 -> £3,381,661.22 (10.3%); £3,771,193.53 -> £3,381,661.42 (10.3%); £3,771,193.82 -> £3,381,661.46 (10.3%); £3,771,194.09 -> £3,381,661.50 (10.3%); £3,771,194.34 -> £3,381,661.54 (10.3%); £3,771,194.58 -> £3,381,661.57 (10.3%); £3,771,194.80 -> £3,381,661.61 (10.3%); £3,771,194.96 -> £3,381,661.65 (10.3%); £3,771,195.12 -> £3,381,661.68 (10.3%); £3,771,195.28 -> £3,381,661.72 (10.3%); £3,771,195.44 -> £3,381,661.76 (10.3%); £3,771,195.60 -> £3,381,661.80 (10.3%); £3,771,195.76 -> £3,381,661.83 (10.3%); £3,771,195.93 -> £3,381,661.87 (10.3%); £3,771,196.08 -> £3,381,661.91 (10.3%); £3,771,196.25 -> £3,381,661.95 (10.3%); £3,771,196.42 -> £3,381,661.99 (10.3%); £3,771,196.58 -> £3,381,662.03 (10.3%); £3,771,196.74 -> £3,381,662.25 (10.3%); £3,771,196.90 -> £3,381,662.46 (10.3%); £3,771,197.08 -> £3,381,662.71 (10.3%); £3,771,197.28 -> £3,381,662.96 (10.3%); £3,771,197.49 -> £3,381,663.23 (10.3%); £3,771,197.72 -> £3,381,663.51 (10.3%); £3,771,197.98 -> £3,381,663.81 (10.3%); £3,771,198.25 -> £3,381,664.12 (10.3%); £3,771,198.53 -> £3,381,664.24 (10.3%); £3,771,198.79 -> £3,381,664.37 (10.3%); £3,771,199.06 -> £3,381,664.49 (10.3%); £3,771,199.33 -> £3,381,664.62 (10.3%); £3,771,199.60 -> £3,381,664.75 (10.3%); £3,771,199.87 -> £3,381,664.87 (10.3%); £3,771,200.15 -> £3,381,664.99 (10.3%); £3,771,200.42 -> £3,381,665.11 (10.3%); £3,771,200.68 -> £3,381,665.22 (10.3%); £3,771,200.94 -> £3,381,665.34 (10.3%); £3,771,201.21 -> £3,381,665.45 (10.3%); £3,771,201.47 -> £3,381,665.56 (10.3%); £3,771,201.75 -> £3,381,665.66 (10.3%); £3,771,201.95 -> £3,381,665.96 (10.3%); £3,771,202.15 -> £3,381,666.23 (10.3%); £3,771,202.36 -> £3,381,666.49 (10.3%); £3,771,202.56 -> £3,381,666.73 (10.3%); £3,771,202.83 -> £3,381,666.95 (10.3%); £3,771,203.03 -> £3,381,667.17 (10.3%); £3,771,203.23 -> £3,381,667.39 (10.3%); £3,771,203.50 -> £3,381,667.60 (10.3%); £3,771,203.77 -> £3,381,667.81 (10.3%); £3,771,204.03 -> £3,381,668.03 (10.3%); £3,771,204.30 -> £3,381,668.24 (10.3%); £3,771,204.56 -> £3,381,668.28 (10.3%); £3,771,204.83 -> £3,381,668.32 (10.3%); £3,771,205.09 -> £3,381,668.36 (10.3%); £3,771,205.32 -> £3,381,668.40 (10.3%); £3,771,205.53 -> £3,381,668.44 (10.3%); £3,771,205.67 -> £3,381,668.47 (10.3%); £3,771,205.82 -> £3,381,668.51 (10.3%); £3,771,205.96 -> £3,381,668.55 (10.3%); £3,771,206.11 -> £3,381,668.59 (10.3%); £3,771,206.25 -> £3,381,668.63 (10.3%); £3,771,206.40 -> £3,381,668.66 (10.3%); £3,771,206.53 -> £3,381,668.70 (10.3%); £3,771,206.67 -> £3,381,668.74 (10.3%); £3,771,206.81 -> £3,381,668.77 (10.3%); £3,771,206.95 -> £3,381,668.81 (10.3%); £3,771,207.09 -> £3,381,668.85 (10.3%); £3,771,207.23 -> £3,381,669.11 (10.3%); £3,771,207.37 -> £3,381,669.36 (10.3%); £3,771,207.53 -> £3,381,669.63 (10.3%); £3,771,207.70 -> £3,381,669.90 (10.3%); £3,771,207.89 -> £3,381,670.17 (10.3%); £3,771,208.10 -> £3,381,670.46 (10.3%); £3,771,208.31 -> £3,381,670.78 (10.3%); £3,771,208.55 -> £3,381,671.10 (10.3%); £3,771,208.78 -> £3,381,671.19 (10.3%); £3,771,209.02 -> £3,381,671.27 (10.3%); £3,771,209.25 -> £3,381,671.36 (10.3%); £3,771,209.49 -> £3,381,671.45 (10.3%); £3,771,209.72 -> £3,381,671.53 (10.3%); £3,771,209.96 -> £3,381,671.61 (10.3%); £3,771,210.19 -> £3,381,671.68 (10.3%); £3,771,210.44 -> £3,381,671.76 (10.3%); £3,771,210.68 -> £3,381,671.82 (10.3%); £3,771,210.92 -> £3,381,671.89 (10.3%); £3,771,211.16 -> £3,381,671.96 (10.3%); £3,771,211.39 -> £3,381,672.02 (10.3%); £3,771,211.64 -> £3,381,672.09 (10.3%); £3,771,211.86 -> £3,381,672.36 (10.3%); £3,771,212.03 -> £3,381,672.62 (10.3%); £3,771,212.21 -> £3,381,672.88 (10.3%); £3,771,212.38 -> £3,381,673.12 (10.3%); £3,771,212.56 -> £3,381,673.37 (10.3%); £3,771,212.74 -> £3,381,673.61 (10.3%); £3,771,212.92 -> £3,381,673.87 (10.3%); £3,771,213.15 -> £3,381,674.12 (10.3%); £3,771,213.38 -> £3,381,674.37 (10.3%); £3,771,213.61 -> £3,381,674.61 (10.3%); £3,771,213.85 -> £3,381,674.86 (10.3%); £3,771,214.08 -> £3,381,674.90 (10.3%); £3,771,214.31 -> £3,381,674.94 (10.3%); £3,771,214.53 -> £3,381,674.98 (10.3%); £3,771,214.73 -> £3,381,675.02 (10.3%); £3,771,214.91 -> £3,381,675.06 (10.3%); £3,771,215.05 -> £3,381,675.09 (10.3%); £3,771,215.19 -> £3,381,675.13 (10.3%); £3,771,215.34 -> £3,381,675.17 (10.3%); £3,771,215.48 -> £3,381,675.21 (10.3%); £3,771,215.61 -> £3,381,675.24 (10.3%); £3,771,215.75 -> £3,381,675.28 (10.3%); £3,771,215.89 -> £3,381,675.31 (10.3%); £3,771,216.04 -> £3,381,675.35 (10.3%); £3,771,216.17 -> £3,381,675.39 (10.3%); £3,771,216.31 -> £3,381,675.42 (10.3%); £3,771,216.45 -> £3,381,675.46 (10.3%); £3,771,216.59 -> £3,381,675.71 (10.3%); £3,771,216.73 -> £3,381,675.95 (10.3%); £3,771,216.88 -> £3,381,676.20 (10.3%); £3,771,217.06 -> £3,381,676.44 (10.3%); £3,771,217.25 -> £3,381,676.69 (10.3%); £3,771,217.45 -> £3,381,676.94 (10.3%); £3,771,217.67 -> £3,381,677.18 (10.3%); £3,771,217.90 -> £3,381,677.43 (10.3%); £3,771,218.15 -> £3,381,677.48 (10.3%); £3,771,218.37 -> £3,381,677.52 (10.3%); £3,771,218.60 -> £3,381,677.57 (10.3%); £3,771,218.83 -> £3,381,677.62 (10.3%); £3,771,219.06 -> £3,381,677.67 (10.3%); £3,771,219.29 -> £3,381,677.72 (10.3%); £3,771,219.52 -> £3,381,677.76 (10.3%); £3,771,219.75 -> £3,381,677.80 (10.3%); £3,771,219.98 -> £3,381,677.85 (10.3%); £3,771,220.22 -> £3,381,677.90 (10.3%); £3,771,220.45 -> £3,381,677.94 (10.3%); £3,771,220.68 -> £3,381,677.98 (10.3%); £3,771,220.91 -> £3,381,678.03 (10.3%); £3,771,221.09 -> £3,381,678.26 (10.3%); £3,771,221.26 -> £3,381,678.49 (10.3%); £3,771,221.43 -> £3,381,678.73 (10.3%); £3,771,221.60 -> £3,381,678.98 (10.3%); £3,771,221.84 -> £3,381,679.22 (10.3%); £3,771,222.02 -> £3,381,679.45 (10.3%); £3,771,222.19 -> £3,381,679.70 (10.3%); £3,771,222.43 -> £3,381,679.95 (10.3%); £3,771,222.66 -> £3,381,680.19 (10.3%); £3,771,222.90 -> £3,381,680.42 (10.3%); £3,771,223.13 -> £3,381,680.66 (10.3%); £3,771,223.35 -> £3,381,680.70 (10.3%); £3,771,223.59 -> £3,381,680.74 (10.3%); £3,771,223.80 -> £3,381,680.78 (10.3%); £3,771,224.00 -> £3,381,680.81 (10.3%); £3,771,224.19 -> £3,381,680.85 (10.3%); £3,771,224.35 -> £3,381,680.89 (10.3%); £3,771,224.50 -> £3,381,680.92 (10.3%); £3,771,224.65 -> £3,381,680.96 (10.3%); £3,771,224.80 -> £3,381,681.00 (10.3%); £3,771,224.95 -> £3,381,681.04 (10.3%); £3,771,225.11 -> £3,381,681.07 (10.3%); £3,771,225.26 -> £3,381,681.11 (10.3%); £3,771,225.42 -> £3,381,681.15 (10.3%); £3,771,225.57 -> £3,381,681.19 (10.3%); £3,771,225.73 -> £3,381,681.22 (10.3%); £3,771,225.88 -> £3,381,681.27 (10.3%); £3,771,226.03 -> £3,381,681.50 (10.3%); £3,771,226.19 -> £3,381,681.76 (10.3%); £3,771,226.36 -> £3,381,682.02 (10.3%); £3,771,226.54 -> £3,381,682.28 (10.3%); £3,771,226.75 -> £3,381,682.58 (10.3%); £3,771,226.97 -> £3,381,682.90 (10.3%); £3,771,227.20 -> £3,381,683.24 (10.3%); £3,771,227.45 -> £3,381,683.60 (10.3%); £3,771,227.70 -> £3,381,683.71 (10.3%); £3,771,227.95 -> £3,381,683.83 (10.3%); £3,771,228.22 -> £3,381,683.95 (10.3%); £3,771,228.46 -> £3,381,684.08 (10.3%); £3,771,228.72 -> £3,381,684.20 (10.3%); £3,771,228.98 -> £3,381,684.31 (10.3%); £3,771,229.24 -> £3,381,684.43 (10.3%); £3,771,229.51 -> £3,381,684.55 (10.3%); £3,771,229.76 -> £3,381,684.66 (10.3%); £3,771,230.01 -> £3,381,684.77 (10.3%); £3,771,230.28 -> £3,381,684.88 (10.3%); £3,771,230.53 -> £3,381,684.99 (10.3%); £3,771,230.79 -> £3,381,685.10 (10.3%); £3,771,231.06 -> £3,381,685.44 (10.3%); £3,771,231.32 -> £3,381,685.76 (10.3%); £3,771,231.57 -> £3,381,686.05 (10.3%); £3,771,231.82 -> £3,381,686.32 (10.3%); £3,771,232.07 -> £3,381,686.59 (10.3%); £3,771,232.32 -> £3,381,686.84 (10.3%); £3,771,232.51 -> £3,381,687.09 (10.3%); £3,771,232.76 -> £3,381,687.34 (10.3%); £3,771,233.01 -> £3,381,687.59 (10.3%); £3,771,233.26 -> £3,381,687.83 (10.3%); £3,771,233.52 -> £3,381,688.07 (10.3%); £3,771,233.77 -> £3,381,688.11 (10.3%); £3,771,234.03 -> £3,381,688.16 (10.3%); £3,771,234.26 -> £3,381,688.20 (10.3%); £3,771,234.48 -> £3,381,688.23 (10.3%); £3,771,234.68 -> £3,381,688.27 (10.3%); £3,771,234.83 -> £3,381,688.31 (10.3%); £3,771,234.99 -> £3,381,688.35 (10.3%); £3,771,235.14 -> £3,381,688.38 (10.3%); £3,771,235.29 -> £3,381,688.42 (10.3%); £3,771,235.45 -> £3,381,688.46 (10.3%); £3,771,235.60 -> £3,381,688.50 (10.3%); £3,771,235.75 -> £3,381,688.53 (10.3%); £3,771,235.90 -> £3,381,688.57 (10.3%); £3,771,236.06 -> £3,381,688.61 (10.3%); £3,771,236.21 -> £3,381,688.65 (10.3%); £3,771,236.36 -> £3,381,688.69 (10.3%); £3,771,236.52 -> £3,381,688.93 (10.3%); £3,771,236.67 -> £3,381,689.18 (10.3%); £3,771,236.83 -> £3,381,689.44 (10.3%); £3,771,237.01 -> £3,381,689.71 (10.3%); £3,771,237.22 -> £3,381,690.00 (10.3%); £3,771,237.44 -> £3,381,690.31 (10.3%); £3,771,237.67 -> £3,381,690.65 (10.3%); £3,771,237.92 -> £3,381,691.00 (10.3%); £3,771,238.17 -> £3,381,691.12 (10.3%); £3,771,238.42 -> £3,381,691.25 (10.3%); £3,771,238.68 -> £3,381,691.38 (10.3%); £3,771,238.93 -> £3,381,691.51 (10.3%); £3,771,239.20 -> £3,381,691.64 (10.3%); £3,771,239.46 -> £3,381,691.76 (10.3%); £3,771,239.71 -> £3,381,691.88 (10.3%); £3,771,239.97 -> £3,381,691.99 (10.3%); £3,771,240.22 -> £3,381,692.11 (10.3%); £3,771,240.48 -> £3,381,692.23 (10.3%); £3,771,240.74 -> £3,381,692.34 (10.3%); £3,771,240.99 -> £3,381,692.45 (10.3%); £3,771,241.23 -> £3,381,692.56 (10.3%); £3,771,241.42 -> £3,381,692.87 (10.3%); £3,771,241.61 -> £3,381,693.19 (10.3%); £3,771,241.86 -> £3,381,693.46 (10.3%); £3,771,242.05 -> £3,381,693.71 (10.3%); £3,771,242.24 -> £3,381,693.97 (10.3%); £3,771,242.50 -> £3,381,694.22 (10.3%); £3,771,242.75 -> £3,381,694.47 (10.3%); £3,771,243.01 -> £3,381,694.72 (10.3%); £3,771,243.26 -> £3,381,694.96 (10.3%); £3,771,243.52 -> £3,381,695.19 (10.3%); £3,771,243.78 -> £3,381,695.43 (10.3%); £3,771,244.03 -> £3,381,695.47 (10.3%); £3,771,244.28 -> £3,381,695.51 (10.3%); £3,771,244.52 -> £3,381,695.55 (10.3%); £3,771,244.73 -> £3,381,695.59 (10.3%); £3,771,244.93 -> £3,381,695.62 (10.3%); £3,771,245.08 -> £3,381,695.66 (10.3%); £3,771,245.23 -> £3,381,695.70 (10.3%); £3,771,245.38 -> £3,381,695.74 (10.3%); £3,771,245.54 -> £3,381,695.77 (10.3%); £3,771,245.68 -> £3,381,695.81 (10.3%); £3,771,245.84 -> £3,381,695.85 (10.3%); £3,771,245.99 -> £3,381,695.89 (10.3%); £3,771,246.14 -> £3,381,695.92 (10.3%); £3,771,246.29 -> £3,381,695.96 (10.3%); £3,771,246.44 -> £3,381,696.00 (10.3%); £3,771,246.59 -> £3,381,696.04 (10.3%); £3,771,246.74 -> £3,381,696.26 (10.3%); £3,771,246.90 -> £3,381,696.47 (10.3%); £3,771,247.06 -> £3,381,696.68 (10.3%); £3,771,247.25 -> £3,381,696.91 (10.3%); £3,771,247.44 -> £3,381,697.16 (10.3%); £3,771,247.66 -> £3,381,697.43 (10.3%); £3,771,247.91 -> £3,381,697.73 (10.3%); £3,771,248.15 -> £3,381,698.03 (10.3%); £3,771,248.41 -> £3,381,698.15 (10.3%); £3,771,248.65 -> £3,381,698.27 (10.3%); £3,771,248.91 -> £3,381,698.40 (10.3%); £3,771,249.16 -> £3,381,698.52 (10.3%); £3,771,249.41 -> £3,381,698.64 (10.3%); £3,771,249.66 -> £3,381,698.76 (10.3%); £3,771,249.93 -> £3,381,698.88 (10.3%); £3,771,250.18 -> £3,381,698.99 (10.3%); £3,771,250.43 -> £3,381,699.10 (10.3%); £3,771,250.69 -> £3,381,699.21 (10.3%); £3,771,250.94 -> £3,381,699.32 (10.3%); £3,771,251.19 -> £3,381,699.43 (10.3%); £3,771,251.43 -> £3,381,699.54 (10.3%); £3,771,251.69 -> £3,381,699.83 (10.3%); £3,771,251.87 -> £3,381,700.12 (10.3%); £3,771,252.13 -> £3,381,700.39 (10.3%); £3,771,252.38 -> £3,381,700.61 (10.3%); £3,771,252.58 -> £3,381,700.85 (10.3%); £3,771,252.82 -> £3,381,701.06 (10.3%); £3,771,253.00 -> £3,381,701.28 (10.3%); £3,771,253.26 -> £3,381,701.50 (10.3%); £3,771,253.51 -> £3,381,701.72 (10.3%); £3,771,253.76 -> £3,381,701.94 (10.3%); £3,771,254.01 -> £3,381,702.15 (10.3%); £3,771,254.26 -> £3,381,702.19 (10.3%); £3,771,254.50 -> £3,381,702.23 (10.3%); £3,771,254.74 -> £3,381,702.27 (10.3%); £3,771,254.95 -> £3,381,702.31 (10.3%); £3,771,255.14 -> £3,381,702.34 (10.3%); £3,771,255.30 -> £3,381,702.38 (10.3%); £3,771,255.45 -> £3,381,702.42 (10.3%); £3,771,255.59 -> £3,381,702.46 (10.3%); £3,771,255.75 -> £3,381,702.49 (10.3%); £3,771,255.89 -> £3,381,702.53 (10.3%); £3,771,256.05 -> £3,381,702.57 (10.3%); £3,771,256.20 -> £3,381,702.61 (10.3%); £3,771,256.35 -> £3,381,702.64 (10.3%); £3,771,256.50 -> £3,381,702.68 (10.3%); £3,771,256.64 -> £3,381,702.72 (10.3%); £3,771,256.80 -> £3,381,702.76 (10.3%); £3,771,256.95 -> £3,381,702.96 (10.3%); £3,771,257.09 -> £3,381,703.16 (10.3%); £3,771,257.26 -> £3,381,703.36 (10.3%); £3,771,257.44 -> £3,381,703.57 (10.3%); £3,771,257.64 -> £3,381,703.81 (10.3%); £3,771,257.85 -> £3,381,704.06 (10.3%); £3,771,258.08 -> £3,381,704.35 (10.3%); £3,771,258.33 -> £3,381,704.63 (10.3%); £3,771,258.59 -> £3,381,704.75 (10.3%); £3,771,258.83 -> £3,381,704.87 (10.3%); £3,771,259.08 -> £3,381,704.99 (10.3%); £3,771,259.34 -> £3,381,705.11 (10.3%); £3,771,259.58 -> £3,381,705.23 (10.3%); £3,771,259.83 -> £3,381,705.35 (10.3%); £3,771,260.07 -> £3,381,705.47 (10.3%); £3,771,260.31 -> £3,381,705.59 (10.3%); £3,771,260.56 -> £3,381,705.70 (10.3%); £3,771,260.81 -> £3,381,705.81 (10.3%); £3,771,261.06 -> £3,381,705.93 (10.3%); £3,771,261.31 -> £3,381,706.04 (10.3%); £3,771,261.56 -> £3,381,706.14 (10.3%); £3,771,261.75 -> £3,381,706.42 (10.3%); £3,771,261.93 -> £3,381,706.68 (10.3%); £3,771,262.12 -> £3,381,706.92 (10.3%); £3,771,262.30 -> £3,381,707.13 (10.3%); £3,771,262.49 -> £3,381,707.34 (10.3%); £3,771,262.67 -> £3,381,707.55 (10.3%); £3,771,262.85 -> £3,381,707.75 (10.3%); £3,771,263.10 -> £3,381,707.95 (10.3%); £3,771,263.35 -> £3,381,708.15 (10.3%); £3,771,263.61 -> £3,381,708.34 (10.3%); £3,771,263.85 -> £3,381,708.53 (10.3%); £3,771,264.10 -> £3,381,708.57 (10.3%); £3,771,264.35 -> £3,381,708.62 (10.3%); £3,771,264.58 -> £3,381,708.66 (10.3%); £3,771,264.79 -> £3,381,708.69 (10.3%); £3,771,264.98 -> £3,381,708.73 (10.3%); £3,771,265.13 -> £3,381,708.77 (10.3%); £3,771,265.28 -> £3,381,708.80 (10.3%); £3,771,265.43 -> £3,381,708.84 (10.3%); £3,771,265.57 -> £3,381,708.88 (10.3%); £3,771,265.72 -> £3,381,708.91 (10.3%); £3,771,265.87 -> £3,381,708.95 (10.3%); £3,771,266.02 -> £3,381,708.99 (10.3%); £3,771,266.16 -> £3,381,709.02 (10.3%); £3,771,266.31 -> £3,381,709.06 (10.3%); £3,771,266.46 -> £3,381,709.10 (10.3%); £3,771,266.61 -> £3,381,709.14 (10.3%); £3,771,266.75 -> £3,381,709.35 (10.3%); £3,771,266.91 -> £3,381,709.57 (10.3%); £3,771,267.07 -> £3,381,709.80 (10.3%); £3,771,267.25 -> £3,381,710.04 (10.3%); £3,771,267.45 -> £3,381,710.29 (10.3%); £3,771,267.66 -> £3,381,710.57 (10.3%); £3,771,267.89 -> £3,381,710.87 (10.3%); £3,771,268.14 -> £3,381,711.17 (10.3%); £3,771,268.37 -> £3,381,711.30 (10.3%); £3,771,268.61 -> £3,381,711.42 (10.3%); £3,771,268.86 -> £3,381,711.54 (10.3%); £3,771,269.11 -> £3,381,711.66 (10.3%); £3,771,269.35 -> £3,381,711.78 (10.3%); £3,771,269.61 -> £3,381,711.90 (10.3%); £3,771,269.85 -> £3,381,712.01 (10.3%); £3,771,270.09 -> £3,381,712.12 (10.3%); £3,771,270.33 -> £3,381,712.23 (10.3%); £3,771,270.57 -> £3,381,712.34 (10.3%); £3,771,270.82 -> £3,381,712.45 (10.3%); £3,771,271.06 -> £3,381,712.56 (10.3%); £3,771,271.30 -> £3,381,712.66 (10.3%); £3,771,271.49 -> £3,381,712.95 (10.3%); £3,771,271.67 -> £3,381,713.23 (10.3%); £3,771,271.86 -> £3,381,713.48 (10.3%); £3,771,272.04 -> £3,381,713.71 (10.3%); £3,771,272.22 -> £3,381,713.94 (10.3%); £3,771,272.40 -> £3,381,714.17 (10.3%); £3,771,272.59 -> £3,381,714.39 (10.3%); £3,771,272.83 -> £3,381,714.60 (10.3%); £3,771,273.08 -> £3,381,714.82 (10.3%); £3,771,273.33 -> £3,381,715.03 (10.3%); £3,771,273.57 -> £3,381,715.24 (10.3%); £3,771,273.82 -> £3,381,715.28 (10.3%); £3,771,274.07 -> £3,381,715.32 (10.3%); £3,771,274.30 -> £3,381,715.36 (10.3%); £3,771,274.51 -> £3,381,715.40 (10.3%); £3,771,274.71 -> £3,381,715.43 (10.3%); £3,771,274.83 -> £3,381,715.47 (10.3%); £3,771,274.96 -> £3,381,715.51 (10.3%); £3,771,275.09 -> £3,381,715.55 (10.3%); £3,771,275.22 -> £3,381,715.58 (10.3%); £3,771,275.35 -> £3,381,715.62 (10.3%); £3,771,275.48 -> £3,381,715.66 (10.3%); £3,771,275.61 -> £3,381,715.69 (10.3%); £3,771,275.74 -> £3,381,715.73 (10.3%); £3,771,275.86 -> £3,381,715.77 (10.3%); £3,771,275.99 -> £3,381,715.80 (10.3%); £3,771,276.12 -> £3,381,715.84 (10.3%); £3,771,276.25 -> £3,381,716.04 (10.3%); £3,771,276.38 -> £3,381,716.25 (10.3%); £3,771,276.52 -> £3,381,716.46 (10.3%); £3,771,276.68 -> £3,381,716.66 (10.3%); £3,771,276.85 -> £3,381,716.89 (10.3%); £3,771,277.03 -> £3,381,717.12 (10.3%); £3,771,277.23 -> £3,381,717.37 (10.3%); £3,771,277.44 -> £3,381,717.63 (10.3%); £3,771,277.65 -> £3,381,717.72 (10.3%); £3,771,277.86 -> £3,381,717.81 (10.3%); £3,771,278.07 -> £3,381,717.90 (10.3%); £3,771,278.28 -> £3,381,717.99 (10.3%); £3,771,278.49 -> £3,381,718.07 (10.3%); £3,771,278.71 -> £3,381,718.15 (10.3%); £3,771,278.92 -> £3,381,718.22 (10.3%); £3,771,279.13 -> £3,381,718.29 (10.3%); £3,771,279.35 -> £3,381,718.36 (10.3%); £3,771,279.56 -> £3,381,718.43 (10.3%); £3,771,279.77 -> £3,381,718.50 (10.3%); £3,771,279.98 -> £3,381,718.57 (10.3%); £3,771,280.20 -> £3,381,718.63 (10.3%); £3,771,280.36 -> £3,381,718.86 (10.3%); £3,771,280.52 -> £3,381,719.08 (10.3%); £3,771,280.68 -> £3,381,719.29 (10.3%); £3,771,280.84 -> £3,381,719.49 (10.3%); £3,771,281.00 -> £3,381,719.70 (10.3%); £3,771,281.15 -> £3,381,719.91 (10.3%); £3,771,281.36 -> £3,381,720.12 (10.3%); £3,771,281.58 -> £3,381,720.31 (10.3%); £3,771,281.80 -> £3,381,720.52 (10.3%); £3,771,282.01 -> £3,381,720.72 (10.3%); £3,771,282.22 -> £3,381,720.92 (10.3%); £3,771,282.43 -> £3,381,720.96 (10.3%); £3,771,282.65 -> £3,381,721.00 (10.3%); £3,771,282.84 -> £3,381,721.04 (10.3%); £3,771,283.02 -> £3,381,721.08 (10.3%); £3,771,283.18 -> £3,381,721.12 (10.3%); £3,771,283.31 -> £3,381,721.16 (10.3%); £3,771,283.44 -> £3,381,721.19 (10.3%); £3,771,283.56 -> £3,381,721.23 (10.3%); £3,771,283.68 -> £3,381,721.27 (10.3%); £3,771,283.81 -> £3,381,721.30 (10.3%); £3,771,283.94 -> £3,381,721.34 (10.3%); £3,771,284.06 -> £3,381,721.38 (10.3%); £3,771,284.19 -> £3,381,721.41 (10.3%); £3,771,284.32 -> £3,381,721.45 (10.3%); £3,771,284.45 -> £3,381,721.48 (10.3%); £3,771,284.57 -> £3,381,721.52 (10.3%); £3,771,284.70 -> £3,381,721.76 (10.3%); £3,771,284.82 -> £3,381,722.01 (10.3%); £3,771,284.97 -> £3,381,722.25 (10.3%); £3,771,285.12 -> £3,381,722.50 (10.3%); £3,771,285.29 -> £3,381,722.74 (10.3%); £3,771,285.48 -> £3,381,722.99 (10.3%); £3,771,285.68 -> £3,381,723.23 (10.3%); £3,771,285.88 -> £3,381,723.48 (10.3%); £3,771,286.10 -> £3,381,723.52 (10.3%); £3,771,286.30 -> £3,381,723.57 (10.3%); £3,771,286.51 -> £3,381,723.62 (10.3%); £3,771,286.73 -> £3,381,723.67 (10.3%); £3,771,286.94 -> £3,381,723.72 (10.3%); £3,771,287.15 -> £3,381,723.76 (10.3%); £3,771,287.36 -> £3,381,723.81 (10.3%); £3,771,287.57 -> £3,381,723.86 (10.3%); £3,771,287.79 -> £3,381,723.90 (10.3%); £3,771,287.99 -> £3,381,723.95 (10.3%); £3,771,288.20 -> £3,381,723.99 (10.3%); £3,771,288.41 -> £3,381,724.04 (10.3%); £3,771,288.62 -> £3,381,724.08 (10.3%); £3,771,288.78 -> £3,381,724.32 (10.3%); £3,771,288.94 -> £3,381,724.55 (10.3%); £3,771,289.11 -> £3,381,724.78 (10.3%); £3,771,289.26 -> £3,381,725.02 (10.3%); £3,771,289.42 -> £3,381,725.26 (10.3%); £3,771,289.59 -> £3,381,725.50 (10.3%); £3,771,289.74 -> £3,381,725.73 (10.3%); £3,771,289.96 -> £3,381,725.96 (10.3%); £3,771,290.18 -> £3,381,726.21 (10.3%); £3,771,290.38 -> £3,381,726.45 (10.3%); £3,771,290.59 -> £3,381,726.69 (10.3%); £3,771,290.80 -> £3,381,726.73 (10.3%); £3,771,291.01 -> £3,381,726.77 (10.3%); £3,771,291.21 -> £3,381,726.80 (10.3%); £3,771,291.39 -> £3,381,726.84 (10.3%); £3,771,291.56 -> £3,381,726.87 (10.3%); £3,771,291.71 -> £3,381,726.91 (10.3%); £3,771,291.85 -> £3,381,726.95 (10.3%); £3,771,292.00 -> £3,381,726.99 (10.3%); £3,771,292.15 -> £3,381,727.02 (10.3%); £3,771,292.29 -> £3,381,727.06 (10.3%); £3,771,292.44 -> £3,381,727.10 (10.3%); £3,771,292.58 -> £3,381,727.13 (10.3%); £3,771,292.73 -> £3,381,727.17 (10.3%); £3,771,292.88 -> £3,381,727.21 (10.3%); £3,771,293.02 -> £3,381,727.25 (10.3%); £3,771,293.16 -> £3,381,727.29 (10.3%); £3,771,293.30 -> £3,381,727.57 (10.3%); £3,771,293.45 -> £3,381,727.86 (10.3%); £3,771,293.61 -> £3,381,728.16 (10.3%); £3,771,293.79 -> £3,381,728.48 (10.3%); £3,771,293.97 -> £3,381,728.81 (10.3%); £3,771,294.18 -> £3,381,729.16 (10.3%); £3,771,294.40 -> £3,381,729.53 (10.3%); £3,771,294.64 -> £3,381,729.92 (10.3%); £3,771,294.88 -> £3,381,730.04 (10.3%); £3,771,295.13 -> £3,381,730.17 (10.3%); £3,771,295.37 -> £3,381,730.30 (10.3%); £3,771,295.62 -> £3,381,730.43 (10.3%); £3,771,295.86 -> £3,381,730.55 (10.3%); £3,771,296.10 -> £3,381,730.68 (10.3%); £3,771,296.34 -> £3,381,730.80 (10.3%); £3,771,296.58 -> £3,381,730.91 (10.3%); £3,771,296.82 -> £3,381,731.03 (10.3%); £3,771,297.07 -> £3,381,731.14 (10.3%); £3,771,297.31 -> £3,381,731.25 (10.3%); £3,771,297.55 -> £3,381,731.36 (10.3%); £3,771,297.79 -> £3,381,731.47 (10.3%); £3,771,297.98 -> £3,381,731.83 (10.3%); £3,771,298.16 -> £3,381,732.17 (10.3%); £3,771,298.35 -> £3,381,732.48 (10.3%); £3,771,298.53 -> £3,381,732.78 (10.3%); £3,771,298.71 -> £3,381,733.07 (10.3%); £3,771,298.89 -> £3,381,733.35 (10.3%); £3,771,299.06 -> £3,381,733.65 (10.3%); £3,771,299.31 -> £3,381,733.93 (10.3%); £3,771,299.54 -> £3,381,734.22 (10.3%); £3,771,299.78 -> £3,381,734.50 (10.3%); £3,771,300.02 -> £3,381,734.78 (10.3%); £3,771,300.27 -> £3,381,734.83 (10.3%); £3,771,300.51 -> £3,381,734.87 (10.3%); £3,771,300.73 -> £3,381,734.91 (10.3%); £3,771,300.94 -> £3,381,734.94 (10.3%); £3,771,301.13 -> £3,381,734.98 (10.3%); £3,771,301.27 -> £3,381,735.02 (10.3%); £3,771,301.42 -> £3,381,735.05 (10.3%); £3,771,301.56 -> £3,381,735.09 (10.3%); £3,771,301.70 -> £3,381,735.13 (10.3%); £3,771,301.84 -> £3,381,735.16 (10.3%); £3,771,301.98 -> £3,381,735.20 (10.3%); £3,771,302.12 -> £3,381,735.24 (10.3%); £3,771,302.26 -> £3,381,735.28 (10.3%); £3,771,302.41 -> £3,381,735.31 (10.3%); £3,771,302.55 -> £3,381,735.35 (10.3%); £3,771,302.70 -> £3,381,735.39 (10.3%); £3,771,302.84 -> £3,381,735.66 (10.3%); £3,771,302.99 -> £3,381,735.92 (10.3%); £3,771,303.15 -> £3,381,736.19 (10.3%); £3,771,303.33 -> £3,381,736.46 (10.3%); £3,771,303.51 -> £3,381,736.75 (10.3%); £3,771,303.73 -> £3,381,737.07 (10.3%); £3,771,303.95 -> £3,381,737.41 (10.3%); £3,771,304.20 -> £3,381,737.76 (10.3%); £3,771,304.44 -> £3,381,737.88 (10.3%); £3,771,304.67 -> £3,381,738.00 (10.3%); £3,771,304.91 -> £3,381,738.12 (10.3%); £3,771,305.15 -> £3,381,738.25 (10.3%); £3,771,305.38 -> £3,381,738.38 (10.3%); £3,771,305.63 -> £3,381,738.50 (10.3%); £3,771,305.86 -> £3,381,738.62 (10.3%); £3,771,306.09 -> £3,381,738.74 (10.3%); £3,771,306.33 -> £3,381,738.85 (10.3%); £3,771,306.57 -> £3,381,738.96 (10.3%); £3,771,306.80 -> £3,381,739.07 (10.3%); £3,771,307.04 -> £3,381,739.18 (10.3%); £3,771,307.28 -> £3,381,739.29 (10.3%); £3,771,307.46 -> £3,381,739.63 (10.3%); £3,771,307.64 -> £3,381,739.96 (10.3%); £3,771,307.83 -> £3,381,740.27 (10.3%); £3,771,308.08 -> £3,381,740.56 (10.3%); £3,771,308.32 -> £3,381,740.84 (10.3%); £3,771,308.57 -> £3,381,741.11 (10.3%); £3,771,308.75 -> £3,381,741.37 (10.3%); £3,771,308.99 -> £3,381,741.63 (10.3%); £3,771,309.23 -> £3,381,741.89 (10.3%); £3,771,309.47 -> £3,381,742.14 (10.3%); £3,771,309.71 -> £3,381,742.38 (10.3%); £3,771,309.96 -> £3,381,742.42 (10.3%); £3,771,310.20 -> £3,381,742.46 (10.3%); £3,771,310.42 -> £3,381,742.50 (10.3%); £3,771,310.62 -> £3,381,742.54 (10.3%); £3,771,310.80 -> £3,381,742.58 (10.3%); £3,771,310.95 -> £3,381,742.61 (10.3%); £3,771,311.09 -> £3,381,742.65 (10.3%); £3,771,311.22 -> £3,381,742.69 (10.3%); £3,771,311.36 -> £3,381,742.73 (10.3%); £3,771,311.50 -> £3,381,742.77 (10.3%); £3,771,311.65 -> £3,381,742.80 (10.3%); £3,771,311.79 -> £3,381,742.84 (10.3%); £3,771,311.93 -> £3,381,742.88 (10.3%); £3,771,312.08 -> £3,381,742.92 (10.3%); £3,771,312.22 -> £3,381,742.96 (10.3%); £3,771,312.36 -> £3,381,743.00 (10.3%); £3,771,312.50 -> £3,381,743.28 (10.3%); £3,771,312.64 -> £3,381,743.56 (10.3%); £3,771,312.79 -> £3,381,743.86 (10.3%); £3,771,312.97 -> £3,381,744.17 (10.3%); £3,771,313.16 -> £3,381,744.49 (10.3%); £3,771,313.36 -> £3,381,744.84 (10.3%); £3,771,313.58 -> £3,381,745.22 (10.3%); £3,771,313.82 -> £3,381,745.61 (10.3%); £3,771,314.06 -> £3,381,745.73 (10.3%); £3,771,314.29 -> £3,381,745.86 (10.3%); £3,771,314.53 -> £3,381,745.98 (10.3%); £3,771,314.77 -> £3,381,746.11 (10.3%); £3,771,315.00 -> £3,381,746.23 (10.3%); £3,771,315.24 -> £3,381,746.35 (10.3%); £3,771,315.48 -> £3,381,746.46 (10.3%); £3,771,315.71 -> £3,381,746.58 (10.3%); £3,771,315.95 -> £3,381,746.69 (10.3%); £3,771,316.19 -> £3,381,746.81 (10.3%); £3,771,316.44 -> £3,381,746.92 (10.3%); £3,771,316.67 -> £3,381,747.02 (10.3%); £3,771,316.91 -> £3,381,747.13 (10.3%); £3,771,317.08 -> £3,381,747.48 (10.3%); £3,771,317.26 -> £3,381,747.83 (10.3%); £3,771,317.50 -> £3,381,748.15 (10.3%); £3,771,317.74 -> £3,381,748.46 (10.3%); £3,771,317.98 -> £3,381,748.75 (10.3%); £3,771,318.21 -> £3,381,749.04 (10.3%); £3,771,318.46 -> £3,381,749.32 (10.3%); £3,771,318.70 -> £3,381,749.61 (10.3%); £3,771,318.94 -> £3,381,749.88 (10.3%); £3,771,319.17 -> £3,381,750.15 (10.3%); £3,771,319.41 -> £3,381,750.40 (10.3%); £3,771,319.64 -> £3,381,750.44 (10.3%); £3,771,319.87 -> £3,381,750.48 (10.3%); £3,771,320.08 -> £3,381,750.52 (10.3%); £3,771,320.28 -> £3,381,750.56 (10.3%); £3,771,320.46 -> £3,381,750.60 (10.3%); £3,771,320.60 -> £3,381,750.64 (10.3%); £3,771,320.74 -> £3,381,750.67 (10.3%); £3,771,320.89 -> £3,381,750.71 (10.3%); £3,771,321.03 -> £3,381,750.75 (10.3%); £3,771,321.17 -> £3,381,750.79 (10.3%); £3,771,321.31 -> £3,381,750.82 (10.3%); £3,771,321.45 -> £3,381,750.86 (10.3%); £3,771,321.59 -> £3,381,750.89 (10.3%); £3,771,321.74 -> £3,381,750.93 (10.3%); £3,771,321.88 -> £3,381,750.97 (10.3%); £3,771,322.03 -> £3,381,751.01 (10.3%); £3,771,322.17 -> £3,381,751.31 (10.3%); £3,771,322.31 -> £3,381,751.62 (10.3%); £3,771,322.47 -> £3,381,751.93 (10.3%); £3,771,322.64 -> £3,381,752.26 (10.3%); £3,771,322.83 -> £3,381,752.61 (10.3%); £3,771,323.04 -> £3,381,752.97 (10.3%); £3,771,323.26 -> £3,381,753.36 (10.3%); £3,771,323.49 -> £3,381,753.76 (10.3%); £3,771,323.72 -> £3,381,753.89 (10.3%); £3,771,323.96 -> £3,381,754.01 (10.3%); £3,771,324.19 -> £3,381,754.14 (10.3%); £3,771,324.42 -> £3,381,754.26 (10.3%); £3,771,324.64 -> £3,381,754.39 (10.3%); £3,771,324.89 -> £3,381,754.51 (10.3%); £3,771,325.13 -> £3,381,754.62 (10.3%); £3,771,325.37 -> £3,381,754.73 (10.3%); £3,771,325.60 -> £3,381,754.85 (10.3%); £3,771,325.84 -> £3,381,754.97 (10.3%); £3,771,326.07 -> £3,381,755.08 (10.3%); £3,771,326.31 -> £3,381,755.19 (10.3%); £3,771,326.55 -> £3,381,755.30 (10.3%); £3,771,326.73 -> £3,381,755.69 (10.3%); £3,771,326.91 -> £3,381,756.06 (10.3%); £3,771,327.08 -> £3,381,756.40 (10.3%); £3,771,327.25 -> £3,381,756.72 (10.3%); £3,771,327.44 -> £3,381,757.04 (10.3%); £3,771,327.61 -> £3,381,757.35 (10.3%); £3,771,327.79 -> £3,381,757.65 (10.3%); £3,771,328.02 -> £3,381,757.95 (10.3%); £3,771,328.25 -> £3,381,758.25 (10.3%); £3,771,328.49 -> £3,381,758.55 (10.3%); £3,771,328.71 -> £3,381,758.85 (10.3%); £3,771,328.95 -> £3,381,758.89 (10.3%); £3,771,329.19 -> £3,381,758.94 (10.3%); £3,771,329.41 -> £3,381,758.98 (10.3%); £3,771,329.62 -> £3,381,759.01 (10.3%); £3,771,329.81 -> £3,381,759.05 (10.3%); £3,771,329.95 -> £3,381,759.09 (10.3%); £3,771,330.09 -> £3,381,759.13 (10.3%); £3,771,330.24 -> £3,381,759.16 (10.3%); £3,771,330.38 -> £3,381,759.20 (10.3%); £3,771,330.52 -> £3,381,759.24 (10.3%); £3,771,330.67 -> £3,381,759.28 (10.3%); £3,771,330.81 -> £3,381,759.31 (10.3%); £3,771,330.96 -> £3,381,759.35 (10.3%); £3,771,331.09 -> £3,381,759.39 (10.3%); £3,771,331.24 -> £3,381,759.43 (10.3%); £3,771,331.39 -> £3,381,759.47 (10.3%); £3,771,331.53 -> £3,381,759.73 (10.3%); £3,771,331.67 -> £3,381,760.00 (10.3%); £3,771,331.83 -> £3,381,760.27 (10.3%); £3,771,332.01 -> £3,381,760.56 (10.3%); £3,771,332.20 -> £3,381,760.87 (10.3%); £3,771,332.40 -> £3,381,761.20 (10.3%); £3,771,332.62 -> £3,381,761.55 (10.3%); £3,771,332.86 -> £3,381,761.91 (10.3%); £3,771,333.09 -> £3,381,762.03 (10.3%); £3,771,333.33 -> £3,381,762.16 (10.3%); £3,771,333.56 -> £3,381,762.28 (10.3%); £3,771,333.80 -> £3,381,762.41 (10.3%); £3,771,334.05 -> £3,381,762.54 (10.3%); £3,771,334.29 -> £3,381,762.66 (10.3%); £3,771,334.53 -> £3,381,762.78 (10.3%); £3,771,334.76 -> £3,381,762.90 (10.3%); £3,771,334.99 -> £3,381,763.02 (10.3%); £3,771,335.23 -> £3,381,763.13 (10.3%); £3,771,335.47 -> £3,381,763.25 (10.3%); £3,771,335.71 -> £3,381,763.36 (10.3%); £3,771,335.95 -> £3,381,763.47 (10.3%); £3,771,336.18 -> £3,381,763.81 (10.3%); £3,771,336.36 -> £3,381,764.14 (10.3%); £3,771,336.53 -> £3,381,764.44 (10.3%); £3,771,336.72 -> £3,381,764.73 (10.3%); £3,771,336.89 -> £3,381,765.01 (10.3%); £3,771,337.14 -> £3,381,765.28 (10.3%); £3,771,337.38 -> £3,381,765.55 (10.3%); £3,771,337.63 -> £3,381,765.82 (10.3%); £3,771,337.87 -> £3,381,766.09 (10.3%); £3,771,338.11 -> £3,381,766.34 (10.3%); £3,771,338.35 -> £3,381,766.59 (10.3%); £3,771,338.60 -> £3,381,766.64 (10.3%); £3,771,338.84 -> £3,381,766.68 (10.3%); £3,771,339.06 -> £3,381,766.72 (10.3%); £3,771,339.26 -> £3,381,766.75 (10.3%); £3,771,339.45 -> £3,381,766.79 (10.3%); £3,771,339.58 -> £3,381,766.83 (10.3%); £3,771,339.71 -> £3,381,766.86 (10.3%); £3,771,339.83 -> £3,381,766.90 (10.3%); £3,771,339.96 -> £3,381,766.94 (10.3%); £3,771,340.09 -> £3,381,766.98 (10.3%); £3,771,340.22 -> £3,381,767.01 (10.3%); £3,771,340.35 -> £3,381,767.05 (10.3%); £3,771,340.48 -> £3,381,767.09 (10.3%); £3,771,340.60 -> £3,381,767.13 (10.3%); £3,771,340.73 -> £3,381,767.16 (10.3%); £3,771,340.86 -> £3,381,767.20 (10.3%); £3,771,340.99 -> £3,381,767.41 (10.3%); £3,771,341.12 -> £3,381,767.61 (10.3%); £3,771,341.26 -> £3,381,767.83 (10.3%); £3,771,341.42 -> £3,381,768.04 (10.3%); £3,771,341.59 -> £3,381,768.27 (10.3%); £3,771,341.78 -> £3,381,768.51 (10.3%); £3,771,341.99 -> £3,381,768.77 (10.3%); £3,771,342.20 -> £3,381,769.04 (10.3%); £3,771,342.41 -> £3,381,769.12 (10.3%); £3,771,342.63 -> £3,381,769.21 (10.3%); £3,771,342.84 -> £3,381,769.30 (10.3%); £3,771,343.05 -> £3,381,769.39 (10.3%); £3,771,343.27 -> £3,381,769.47 (10.3%); £3,771,343.48 -> £3,381,769.55 (10.3%); £3,771,343.69 -> £3,381,769.63 (10.3%); £3,771,343.91 -> £3,381,769.70 (10.3%); £3,771,344.13 -> £3,381,769.77 (10.3%); £3,771,344.34 -> £3,381,769.84 (10.3%); £3,771,344.55 -> £3,381,769.91 (10.3%); £3,771,344.76 -> £3,381,769.97 (10.3%); £3,771,344.98 -> £3,381,770.04 (10.3%); £3,771,345.14 -> £3,381,770.28 (10.3%); £3,771,345.31 -> £3,381,770.51 (10.3%); £3,771,345.47 -> £3,381,770.73 (10.3%); £3,771,345.63 -> £3,381,770.94 (10.3%); £3,771,345.79 -> £3,381,771.15 (10.3%); £3,771,345.96 -> £3,381,771.36 (10.3%); £3,771,346.12 -> £3,381,771.57 (10.3%); £3,771,346.33 -> £3,381,771.77 (10.3%); £3,771,346.55 -> £3,381,771.98 (10.3%); £3,771,346.76 -> £3,381,772.18 (10.3%); £3,771,346.98 -> £3,381,772.39 (10.3%); £3,771,347.19 -> £3,381,772.43 (10.3%); £3,771,347.40 -> £3,381,772.47 (10.3%); £3,771,347.61 -> £3,381,772.50 (10.3%); £3,771,347.79 -> £3,381,772.54 (10.3%); £3,771,347.95 -> £3,381,772.58 (10.3%); £3,771,348.08 -> £3,381,772.62 (10.3%); £3,771,348.21 -> £3,381,772.66 (10.3%); £3,771,348.34 -> £3,381,772.69 (10.3%); £3,771,348.47 -> £3,381,772.73 (10.3%); £3,771,348.60 -> £3,381,772.77 (10.3%); £3,771,348.73 -> £3,381,772.80 (10.3%); £3,771,348.86 -> £3,381,772.84 (10.3%); £3,771,348.98 -> £3,381,772.87 (10.3%); £3,771,349.11 -> £3,381,772.91 (10.3%); £3,771,349.24 -> £3,381,772.94 (10.3%); £3,771,349.37 -> £3,381,772.98 (10.3%); £3,771,349.50 -> £3,381,773.12 (10.3%); £3,771,349.63 -> £3,381,773.26 (10.3%); £3,771,349.77 -> £3,381,773.40 (10.3%); £3,771,349.93 -> £3,381,773.54 (10.3%); £3,771,350.10 -> £3,381,773.69 (10.3%); £3,771,350.29 -> £3,381,773.83 (10.3%); £3,771,350.49 -> £3,381,773.98 (10.3%); £3,771,350.71 -> £3,381,774.13 (10.3%); £3,771,350.93 -> £3,381,774.18 (10.3%); £3,771,351.14 -> £3,381,774.23 (10.3%); £3,771,351.36 -> £3,381,774.28 (10.3%); £3,771,351.57 -> £3,381,774.32 (10.3%); £3,771,351.78 -> £3,381,774.37 (10.3%); £3,771,352.00 -> £3,381,774.42 (10.3%); £3,771,352.21 -> £3,381,774.47 (10.3%); £3,771,352.43 -> £3,381,774.51 (10.3%); £3,771,352.64 -> £3,381,774.56 (10.3%); £3,771,352.85 -> £3,381,774.60 (10.3%); £3,771,353.07 -> £3,381,774.65 (10.3%); £3,771,353.29 -> £3,381,774.69 (10.3%); £3,771,353.51 -> £3,381,774.74 (10.3%); £3,771,353.67 -> £3,381,774.89 (10.3%); £3,771,353.83 -> £3,381,775.03 (10.3%); £3,771,353.99 -> £3,381,775.18 (10.3%); £3,771,354.14 -> £3,381,775.33 (10.3%); £3,771,354.30 -> £3,381,775.48 (10.3%); £3,771,354.47 -> £3,381,775.62 (10.3%); £3,771,354.62 -> £3,381,775.77 (10.3%); £3,771,354.84 -> £3,381,775.91 (10.3%); £3,771,355.05 -> £3,381,776.06 (10.3%); £3,771,355.28 -> £3,381,776.20 (10.3%); £3,771,355.49 -> £3,381,776.33 (10.3%); £3,771,355.70 -> £3,381,776.37 (10.3%); £3,771,355.92 -> £3,381,776.41 (10.3%); £3,771,356.11 -> £3,381,776.45 (10.3%); £3,771,356.29 -> £3,381,776.48 (10.3%); £3,771,356.45 -> £3,381,776.52 (10.3%); £3,771,356.60 -> £3,381,776.56 (10.3%); £3,771,356.75 -> £3,381,776.60 (10.3%); £3,771,356.89 -> £3,381,776.63 (10.3%); £3,771,357.04 -> £3,381,776.67 (10.3%); £3,771,357.18 -> £3,381,776.71 (10.3%); £3,771,357.33 -> £3,381,776.74 (10.3%); £3,771,357.48 -> £3,381,776.78 (10.3%); £3,771,357.63 -> £3,381,776.82 (10.3%); £3,771,357.77 -> £3,381,776.85 (10.3%); £3,771,357.91 -> £3,381,776.89 (10.3%); £3,771,358.06 -> £3,381,776.93 (10.3%); £3,771,358.21 -> £3,381,777.10 (10.3%); £3,771,358.35 -> £3,381,777.27 (10.3%); £3,771,358.51 -> £3,381,777.45 (10.3%); £3,771,358.69 -> £3,381,777.64 (10.3%); £3,771,358.89 -> £3,381,777.85 (10.3%); £3,771,359.11 -> £3,381,778.08 (10.3%); £3,771,359.34 -> £3,381,778.33 (10.3%); £3,771,359.59 -> £3,381,778.60 (10.3%); £3,771,359.84 -> £3,381,778.72 (10.3%); £3,771,360.08 -> £3,381,778.85 (10.3%); £3,771,360.34 -> £3,381,778.98 (10.3%); £3,771,360.57 -> £3,381,779.10 (10.3%); £3,771,360.82 -> £3,381,779.23 (10.3%); £3,771,361.08 -> £3,381,779.35 (10.3%); £3,771,361.32 -> £3,381,779.46 (10.3%); £3,771,361.57 -> £3,381,779.58 (10.3%); £3,771,361.83 -> £3,381,779.70 (10.3%); £3,771,362.07 -> £3,381,779.82 (10.3%); £3,771,362.32 -> £3,381,779.94 (10.3%); £3,771,362.57 -> £3,381,780.05 (10.3%); £3,771,362.82 -> £3,381,780.16 (10.3%); £3,771,363.06 -> £3,381,780.43 (10.3%); £3,771,363.25 -> £3,381,780.66 (10.3%); £3,771,363.43 -> £3,381,780.88 (10.3%); £3,771,363.62 -> £3,381,781.07 (10.3%); £3,771,363.79 -> £3,381,781.25 (10.3%); £3,771,363.98 -> £3,381,781.43 (10.3%); £3,771,364.16 -> £3,381,781.62 (10.3%); £3,771,364.40 -> £3,381,781.79 (10.3%); £3,771,364.64 -> £3,381,781.96 (10.3%); £3,771,364.89 -> £3,381,782.13 (10.3%); £3,771,365.14 -> £3,381,782.30 (10.3%); £3,771,365.38 -> £3,381,782.34 (10.3%); £3,771,365.63 -> £3,381,782.38 (10.3%); £3,771,365.86 -> £3,381,782.42 (10.3%); £3,771,366.07 -> £3,381,782.46 (10.3%); £3,771,366.26 -> £3,381,782.50 (10.3%); £3,771,366.41 -> £3,381,782.53 (10.3%); £3,771,366.56 -> £3,381,782.57 (10.3%); £3,771,366.70 -> £3,381,782.61 (10.3%); £3,771,366.84 -> £3,381,782.65 (10.3%); £3,771,367.00 -> £3,381,782.69 (10.3%); £3,771,367.14 -> £3,381,782.73 (10.3%); £3,771,367.29 -> £3,381,782.77 (10.3%); £3,771,367.44 -> £3,381,782.81 (10.3%); £3,771,367.59 -> £3,381,782.84 (10.3%); £3,771,367.73 -> £3,381,782.88 (10.3%); £3,771,367.88 -> £3,381,782.92 (10.3%); £3,771,368.03 -> £3,381,783.08 (10.3%); £3,771,368.18 -> £3,381,783.23 (10.3%); £3,771,368.35 -> £3,381,783.41 (10.3%); £3,771,368.53 -> £3,381,783.59 (10.3%); £3,771,368.73 -> £3,381,783.79 (10.3%); £3,771,368.94 -> £3,381,784.02 (10.3%); £3,771,369.17 -> £3,381,784.26 (10.3%); £3,771,369.42 -> £3,381,784.51 (10.3%); £3,771,369.67 -> £3,381,784.64 (10.3%); £3,771,369.91 -> £3,381,784.77 (10.3%); £3,771,370.16 -> £3,381,784.90 (10.3%); £3,771,370.40 -> £3,381,785.03 (10.3%); £3,771,370.66 -> £3,381,785.16 (10.3%); £3,771,370.90 -> £3,381,785.28 (10.3%); £3,771,371.15 -> £3,381,785.40 (10.3%); £3,771,371.39 -> £3,381,785.52 (10.3%); £3,771,371.64 -> £3,381,785.63 (10.3%); £3,771,371.88 -> £3,381,785.75 (10.3%); £3,771,372.12 -> £3,381,785.87 (10.3%); £3,771,372.37 -> £3,381,785.98 (10.3%); £3,771,372.62 -> £3,381,786.09 (10.3%); £3,771,372.80 -> £3,381,786.34 (10.3%); £3,771,372.99 -> £3,381,786.58 (10.3%); £3,771,373.25 -> £3,381,786.78 (10.3%); £3,771,373.49 -> £3,381,786.97 (10.3%); £3,771,373.73 -> £3,381,787.15 (10.3%); £3,771,373.98 -> £3,381,787.32 (10.3%); £3,771,374.17 -> £3,381,787.49 (10.3%); £3,771,374.42 -> £3,381,787.65 (10.3%); £3,771,374.67 -> £3,381,787.82 (10.3%); £3,771,374.92 -> £3,381,787.97 (10.3%); £3,771,375.17 -> £3,381,788.12 (10.3%); £3,771,375.42 -> £3,381,788.16 (10.3%); £3,771,375.67 -> £3,381,788.21 (10.3%); £3,771,375.90 -> £3,381,788.25 (10.3%); £3,771,376.10 -> £3,381,788.28 (10.3%); £3,771,376.30 -> £3,381,788.32 (10.3%); £3,771,376.44 -> £3,381,788.36 (10.3%); £3,771,376.59 -> £3,381,788.40 (10.3%); £3,771,376.74 -> £3,381,788.44 (10.3%); £3,771,376.89 -> £3,381,788.48 (10.3%); £3,771,377.04 -> £3,381,788.52 (10.3%); £3,771,377.18 -> £3,381,788.55 (10.3%); £3,771,377.33 -> £3,381,788.59 (10.3%); £3,771,377.48 -> £3,381,788.63 (10.3%); £3,771,377.63 -> £3,381,788.67 (10.3%); £3,771,377.78 -> £3,381,788.71 (10.3%); £3,771,377.93 -> £3,381,788.75 (10.3%); £3,771,378.09 -> £3,381,788.91 (10.3%); £3,771,378.24 -> £3,381,789.07 (10.3%); £3,771,378.41 -> £3,381,789.24 (10.3%); £3,771,378.59 -> £3,381,789.43 (10.3%); £3,771,378.79 -> £3,381,789.64 (10.3%); £3,771,379.00 -> £3,381,789.86 (10.3%); £3,771,379.24 -> £3,381,790.12 (10.3%); £3,771,379.48 -> £3,381,790.38 (10.3%); £3,771,379.74 -> £3,381,790.51 (10.3%); £3,771,379.99 -> £3,381,790.64 (10.3%); £3,771,380.24 -> £3,381,790.77 (10.3%); £3,771,380.49 -> £3,381,790.90 (10.3%); £3,771,380.74 -> £3,381,791.03 (10.3%); £3,771,380.99 -> £3,381,791.15 (10.3%); £3,771,381.24 -> £3,381,791.27 (10.3%); £3,771,381.50 -> £3,381,791.39 (10.3%); £3,771,381.76 -> £3,381,791.51 (10.3%); £3,771,382.01 -> £3,381,791.63 (10.3%); £3,771,382.27 -> £3,381,791.75 (10.3%); £3,771,382.52 -> £3,381,791.87 (10.3%); £3,771,382.77 -> £3,381,791.99 (10.3%); £3,771,383.02 -> £3,381,792.24 (10.3%); £3,771,383.20 -> £3,381,792.48 (10.3%); £3,771,383.39 -> £3,381,792.70 (10.3%); £3,771,383.64 -> £3,381,792.89 (10.3%); £3,771,383.89 -> £3,381,793.08 (10.3%); £3,771,384.15 -> £3,381,793.26 (10.3%); £3,771,384.34 -> £3,381,793.44 (10.3%); £3,771,384.59 -> £3,381,793.62 (10.3%); £3,771,384.85 -> £3,381,793.79 (10.3%); £3,771,385.10 -> £3,381,793.96 (10.3%); £3,771,385.35 -> £3,381,794.12 (10.3%); £3,771,385.60 -> £3,381,794.16 (10.3%); £3,771,385.85 -> £3,381,794.20 (10.3%); £3,771,386.09 -> £3,381,794.24 (10.3%); £3,771,386.30 -> £3,381,794.28 (10.3%); £3,771,386.50 -> £3,381,794.31 (10.3%); £3,771,386.65 -> £3,381,794.35 (10.3%); £3,771,386.80 -> £3,381,794.39 (10.3%); £3,771,386.96 -> £3,381,794.43 (10.3%); £3,771,387.12 -> £3,381,794.47 (10.3%); £3,771,387.27 -> £3,381,794.50 (10.3%); £3,771,387.43 -> £3,381,794.54 (10.3%); £3,771,387.58 -> £3,381,794.58 (10.3%); £3,771,387.74 -> £3,381,794.62 (10.3%); £3,771,387.89 -> £3,381,794.65 (10.3%); £3,771,388.04 -> £3,381,794.69 (10.3%); £3,771,388.20 -> £3,381,794.73 (10.3%); £3,771,388.35 -> £3,381,794.88 (10.3%); £3,771,388.51 -> £3,381,795.03 (10.3%); £3,771,388.67 -> £3,381,795.19 (10.3%); £3,771,388.86 -> £3,381,795.37 (10.3%); £3,771,389.07 -> £3,381,795.57 (10.3%); £3,771,389.28 -> £3,381,795.78 (10.3%); £3,771,389.52 -> £3,381,796.03 (10.3%); £3,771,389.77 -> £3,381,796.29 (10.3%); £3,771,390.03 -> £3,381,796.41 (10.3%); £3,771,390.28 -> £3,381,796.54 (10.3%); £3,771,390.53 -> £3,381,796.67 (10.3%); £3,771,390.79 -> £3,381,796.80 (10.3%); £3,771,391.04 -> £3,381,796.93 (10.3%); £3,771,391.30 -> £3,381,797.05 (10.3%); £3,771,391.56 -> £3,381,797.17 (10.3%); £3,771,391.81 -> £3,381,797.29 (10.3%); £3,771,392.07 -> £3,381,797.41 (10.3%); £3,771,392.33 -> £3,381,797.53 (10.3%); £3,771,392.58 -> £3,381,797.64 (10.3%); £3,771,392.83 -> £3,381,797.75 (10.3%); £3,771,393.09 -> £3,381,797.86 (10.3%); £3,771,393.29 -> £3,381,798.11 (10.3%); £3,771,393.48 -> £3,381,798.33 (10.3%); £3,771,393.66 -> £3,381,798.53 (10.3%); £3,771,393.85 -> £3,381,798.72 (10.3%); £3,771,394.11 -> £3,381,798.89 (10.3%); £3,771,394.36 -> £3,381,799.06 (10.3%); £3,771,394.56 -> £3,381,799.22 (10.3%); £3,771,394.82 -> £3,381,799.38 (10.3%); £3,771,395.08 -> £3,381,799.54 (10.3%); £3,771,395.34 -> £3,381,799.69 (10.3%); £3,771,395.58 -> £3,381,799.84 (10.3%); £3,771,395.84 -> £3,381,799.88 (10.3%); £3,771,396.10 -> £3,381,799.92 (10.3%); £3,771,396.33 -> £3,381,799.96 (10.3%); £3,771,396.55 -> £3,381,800.00 (10.3%); £3,771,396.75 -> £3,381,800.04 (10.3%); £3,771,396.91 -> £3,381,800.07 (10.3%); £3,771,397.06 -> £3,381,800.11 (10.3%); £3,771,397.21 -> £3,381,800.15 (10.3%); £3,771,397.36 -> £3,381,800.19 (10.3%); £3,771,397.51 -> £3,381,800.22 (10.3%); £3,771,397.66 -> £3,381,800.26 (10.3%); £3,771,397.82 -> £3,381,800.30 (10.3%); £3,771,397.97 -> £3,381,800.34 (10.3%); £3,771,398.13 -> £3,381,800.38 (10.3%); £3,771,398.28 -> £3,381,800.42 (10.3%); £3,771,398.43 -> £3,381,800.46 (10.3%); £3,771,398.58 -> £3,381,800.62 (10.3%); £3,771,398.74 -> £3,381,800.79 (10.3%); £3,771,398.91 -> £3,381,800.98 (10.3%); £3,771,399.10 -> £3,381,801.17 (10.3%); £3,771,399.30 -> £3,381,801.39 (10.3%); £3,771,399.52 -> £3,381,801.62 (10.3%); £3,771,399.77 -> £3,381,801.88 (10.3%); £3,771,400.03 -> £3,381,802.15 (10.3%); £3,771,400.30 -> £3,381,802.28 (10.3%); £3,771,400.56 -> £3,381,802.41 (10.3%); £3,771,400.82 -> £3,381,802.55 (10.3%); £3,771,401.07 -> £3,381,802.70 (10.3%); £3,771,401.33 -> £3,381,802.84 (10.3%); £3,771,401.57 -> £3,381,802.98 (10.3%); £3,771,401.83 -> £3,381,803.10 (10.3%); £3,771,402.08 -> £3,381,803.23 (10.3%); £3,771,402.35 -> £3,381,803.36 (10.3%); £3,771,402.61 -> £3,381,803.47 (10.3%); £3,771,402.85 -> £3,381,803.59 (10.3%); £3,771,403.10 -> £3,381,803.70 (10.3%); £3,771,403.36 -> £3,381,803.80 (10.3%); £3,771,403.56 -> £3,381,804.06 (10.3%); £3,771,403.75 -> £3,381,804.31 (10.3%); £3,771,403.94 -> £3,381,804.52 (10.3%); £3,771,404.14 -> £3,381,804.72 (10.3%); £3,771,404.34 -> £3,381,804.91 (10.3%); £3,771,404.53 -> £3,381,805.09 (10.3%); £3,771,404.72 -> £3,381,805.28 (10.3%); £3,771,404.98 -> £3,381,805.46 (10.3%); £3,771,405.24 -> £3,381,805.64 (10.3%); £3,771,405.49 -> £3,381,805.82 (10.3%); £3,771,405.75 -> £3,381,805.99 (10.3%); £3,771,406.00 -> £3,381,806.03 (10.3%); £3,771,406.26 -> £3,381,806.07 (10.3%); £3,771,406.49 -> £3,381,806.11 (10.3%); £3,771,406.70 -> £3,381,806.15 (10.3%); £3,771,406.91 -> £3,381,806.19 (10.3%); £3,771,407.05 -> £3,381,806.23 (10.3%); £3,771,407.19 -> £3,381,806.26 (10.3%); £3,771,407.33 -> £3,381,806.30 (10.3%); £3,771,407.47 -> £3,381,806.34 (10.3%); £3,771,407.61 -> £3,381,806.38 (10.3%); £3,771,407.76 -> £3,381,806.41 (10.3%); £3,771,407.90 -> £3,381,806.45 (10.3%); £3,771,408.04 -> £3,381,806.49 (10.3%); £3,771,408.17 -> £3,381,806.53 (10.3%); £3,771,408.31 -> £3,381,806.57 (10.3%); £3,771,408.44 -> £3,381,806.61 (10.3%); £3,771,408.58 -> £3,381,806.80 (10.3%); £3,771,408.73 -> £3,381,806.98 (10.3%); £3,771,408.88 -> £3,381,807.17 (10.3%); £3,771,409.05 -> £3,381,807.37 (10.3%); £3,771,409.24 -> £3,381,807.58 (10.3%); £3,771,409.44 -> £3,381,807.80 (10.3%); £3,771,409.66 -> £3,381,808.04 (10.3%); £3,771,409.89 -> £3,381,808.29 (10.3%); £3,771,410.12 -> £3,381,808.38 (10.3%); £3,771,410.36 -> £3,381,808.47 (10.3%); £3,771,410.59 -> £3,381,808.56 (10.3%); £3,771,410.82 -> £3,381,808.65 (10.3%); £3,771,411.05 -> £3,381,808.74 (10.3%); £3,771,411.27 -> £3,381,808.82 (10.3%); £3,771,411.51 -> £3,381,808.90 (10.3%); £3,771,411.74 -> £3,381,808.98 (10.3%); £3,771,411.97 -> £3,381,809.06 (10.3%); £3,771,412.21 -> £3,381,809.13 (10.3%); £3,771,412.44 -> £3,381,809.20 (10.3%); £3,771,412.67 -> £3,381,809.27 (10.3%); £3,771,412.89 -> £3,381,809.33 (10.3%); £3,771,413.07 -> £3,381,809.55 (10.3%); £3,771,413.25 -> £3,381,809.76 (10.3%); £3,771,413.42 -> £3,381,809.96 (10.3%); £3,771,413.59 -> £3,381,810.15 (10.3%); £3,771,413.76 -> £3,381,810.35 (10.3%); £3,771,414.00 -> £3,381,810.55 (10.3%); £3,771,414.23 -> £3,381,810.74 (10.3%); £3,771,414.46 -> £3,381,810.93 (10.3%); £3,771,414.69 -> £3,381,811.12 (10.3%); £3,771,414.92 -> £3,381,811.30 (10.3%); £3,771,415.15 -> £3,381,811.50 (10.3%); £3,771,415.38 -> £3,381,811.54 (10.3%); £3,771,415.61 -> £3,381,811.58 (10.3%); £3,771,415.82 -> £3,381,811.62 (10.3%); £3,771,416.01 -> £3,381,811.66 (10.3%); £3,771,416.19 -> £3,381,811.70 (10.3%); £3,771,416.32 -> £3,381,811.74 (10.3%); £3,771,416.47 -> £3,381,811.78 (10.3%); £3,771,416.61 -> £3,381,811.82 (10.3%); £3,771,416.75 -> £3,381,811.85 (10.3%); £3,771,416.89 -> £3,381,811.89 (10.3%); £3,771,417.03 -> £3,381,811.93 (10.3%); £3,771,417.17 -> £3,381,811.96 (10.3%); £3,771,417.32 -> £3,381,812.00 (10.3%); £3,771,417.45 -> £3,381,812.04 (10.3%); £3,771,417.59 -> £3,381,812.07 (10.3%); £3,771,417.72 -> £3,381,812.11 (10.3%); £3,771,417.86 -> £3,381,812.27 (10.3%); £3,771,418.00 -> £3,381,812.43 (10.3%); £3,771,418.16 -> £3,381,812.59 (10.3%); £3,771,418.33 -> £3,381,812.74 (10.3%); £3,771,418.52 -> £3,381,812.90 (10.3%); £3,771,418.73 -> £3,381,813.06 (10.3%); £3,771,418.95 -> £3,381,813.22 (10.3%); £3,771,419.18 -> £3,381,813.39 (10.3%); £3,771,419.41 -> £3,381,813.44 (10.3%); £3,771,419.65 -> £3,381,813.48 (10.3%); £3,771,419.88 -> £3,381,813.54 (10.3%); £3,771,420.12 -> £3,381,813.59 (10.3%); £3,771,420.35 -> £3,381,813.63 (10.3%); £3,771,420.58 -> £3,381,813.68 (10.3%); £3,771,420.80 -> £3,381,813.73 (10.3%); £3,771,421.03 -> £3,381,813.77 (10.3%); £3,771,421.27 -> £3,381,813.82 (10.3%); £3,771,421.50 -> £3,381,813.86 (10.3%); £3,771,421.74 -> £3,381,813.91 (10.3%); £3,771,421.97 -> £3,381,813.95 (10.3%); £3,771,422.19 -> £3,381,814.00 (10.3%); £3,771,422.37 -> £3,381,814.16 (10.3%); £3,771,422.53 -> £3,381,814.32 (10.3%); £3,771,422.71 -> £3,381,814.48 (10.3%); £3,771,422.89 -> £3,381,814.65 (10.3%); £3,771,423.12 -> £3,381,814.82 (10.3%); £3,771,423.35 -> £3,381,814.98 (10.3%); £3,771,423.53 -> £3,381,815.14 (10.3%); £3,771,423.76 -> £3,381,815.30 (10.3%); £3,771,424.00 -> £3,381,815.45 (10.3%); £3,771,424.23 -> £3,381,815.61 (10.3%); £3,771,424.47 -> £3,381,815.76 (10.3%); £3,771,424.71 -> £3,381,815.80 (10.3%); £3,771,424.94 -> £3,381,815.84 (10.3%); £3,771,425.15 -> £3,381,815.88 (10.3%); £3,771,425.35 -> £3,381,815.91 (10.3%); £3,771,425.52 -> £3,381,815.95 (10.3%); £3,771,425.68 -> £3,381,815.98 (10.3%); £3,771,425.84 -> £3,381,816.02 (10.3%); £3,771,426.00 -> £3,381,816.06 (10.3%); £3,771,426.16 -> £3,381,816.09 (10.3%); £3,771,426.32 -> £3,381,816.13 (10.3%); £3,771,426.48 -> £3,381,816.17 (10.3%); £3,771,426.64 -> £3,381,816.21 (10.3%); £3,771,426.80 -> £3,381,816.25 (10.3%); £3,771,426.96 -> £3,381,816.28 (10.3%); £3,771,427.12 -> £3,381,816.32 (10.3%); £3,771,427.29 -> £3,381,816.36 (10.3%); £3,771,427.45 -> £3,381,816.48 (10.3%); £3,771,427.61 -> £3,381,816.61 (10.3%); £3,771,427.79 -> £3,381,816.75 (10.3%); £3,771,427.99 -> £3,381,816.90 (10.3%); £3,771,428.20 -> £3,381,817.07 (10.3%); £3,771,428.44 -> £3,381,817.27 (10.3%); £3,771,428.69 -> £3,381,817.48 (10.3%); £3,771,428.97 -> £3,381,817.71 (10.3%); £3,771,429.23 -> £3,381,817.83 (10.3%); £3,771,429.50 -> £3,381,817.95 (10.3%); £3,771,429.78 -> £3,381,818.08 (10.3%); £3,771,430.04 -> £3,381,818.20 (10.3%); £3,771,430.30 -> £3,381,818.32 (10.3%); £3,771,430.57 -> £3,381,818.44 (10.3%); £3,771,430.82 -> £3,381,818.55 (10.3%); £3,771,431.08 -> £3,381,818.66 (10.3%); £3,771,431.35 -> £3,381,818.78 (10.3%); £3,771,431.61 -> £3,381,818.89 (10.3%); £3,771,431.88 -> £3,381,819.01 (10.3%); £3,771,432.15 -> £3,381,819.12 (10.3%); £3,771,432.42 -> £3,381,819.23 (10.3%); £3,771,432.69 -> £3,381,819.46 (10.3%); £3,771,432.96 -> £3,381,819.67 (10.3%); £3,771,433.23 -> £3,381,819.86 (10.3%); £3,771,433.50 -> £3,381,820.02 (10.3%); £3,771,433.78 -> £3,381,820.17 (10.3%); £3,771,434.04 -> £3,381,820.31 (10.3%); £3,771,434.25 -> £3,381,820.46 (10.3%); £3,771,434.52 -> £3,381,820.60 (10.3%); £3,771,434.79 -> £3,381,820.73 (10.3%); £3,771,435.05 -> £3,381,820.86 (10.3%); £3,771,435.32 -> £3,381,820.99 (10.3%); £3,771,435.58 -> £3,381,821.03 (10.3%); £3,771,435.86 -> £3,381,821.07 (10.3%); £3,771,436.10 -> £3,381,821.11 (10.3%); £3,771,436.33 -> £3,381,821.15 (10.3%); £3,771,436.54 -> £3,381,821.18 (10.3%); £3,771,436.70 -> £3,381,821.22 (10.3%); £3,771,436.86 -> £3,381,821.26 (10.3%); £3,771,437.02 -> £3,381,821.30 (10.3%); £3,771,437.18 -> £3,381,821.33 (10.3%); £3,771,437.33 -> £3,381,821.37 (10.3%); £3,771,437.50 -> £3,381,821.41 (10.3%); £3,771,437.65 -> £3,381,821.45 (10.3%); £3,771,437.81 -> £3,381,821.49 (10.3%); £3,771,437.97 -> £3,381,821.52 (10.3%); £3,771,438.13 -> £3,381,821.56 (10.3%); £3,771,438.29 -> £3,381,821.61 (10.3%); £3,771,438.44 -> £3,381,821.79 (10.3%); £3,771,438.60 -> £3,381,821.99 (10.3%); £3,771,438.78 -> £3,381,822.20 (10.3%); £3,771,438.97 -> £3,381,822.41 (10.3%); £3,771,439.18 -> £3,381,822.65 (10.3%); £3,771,439.41 -> £3,381,822.91 (10.3%); £3,771,439.66 -> £3,381,823.20 (10.3%); £3,771,439.93 -> £3,381,823.50 (10.3%); £3,771,440.20 -> £3,381,823.63 (10.3%); £3,771,440.47 -> £3,381,823.75 (10.3%); £3,771,440.73 -> £3,381,823.88 (10.3%); £3,771,441.00 -> £3,381,824.01 (10.3%); £3,771,441.26 -> £3,381,824.14 (10.3%); £3,771,441.52 -> £3,381,824.26 (10.3%); £3,771,441.79 -> £3,381,824.37 (10.3%); £3,771,442.05 -> £3,381,824.49 (10.3%); £3,771,442.32 -> £3,381,824.61 (10.3%); £3,771,442.60 -> £3,381,824.72 (10.3%); £3,771,442.85 -> £3,381,824.84 (10.3%); £3,771,443.12 -> £3,381,824.95 (10.3%); £3,771,443.39 -> £3,381,825.06 (10.3%); £3,771,443.59 -> £3,381,825.33 (10.3%); £3,771,443.78 -> £3,381,825.60 (10.3%); £3,771,444.05 -> £3,381,825.84 (10.3%); £3,771,444.32 -> £3,381,826.05 (10.3%); £3,771,444.52 -> £3,381,826.26 (10.3%); £3,771,444.72 -> £3,381,826.45 (10.3%); £3,771,444.91 -> £3,381,826.65 (10.3%); £3,771,445.18 -> £3,381,826.84 (10.3%); £3,771,445.44 -> £3,381,827.04 (10.3%); £3,771,445.70 -> £3,381,827.23 (10.3%); £3,771,445.95 -> £3,381,827.41 (10.3%); £3,771,446.21 -> £3,381,827.45 (10.3%); £3,771,446.48 -> £3,381,827.50 (10.3%); £3,771,446.73 -> £3,381,827.54 (10.3%); £3,771,446.94 -> £3,381,827.57 (10.3%); £3,771,447.15 -> £3,381,827.61 (10.3%); £3,771,447.31 -> £3,381,827.65 (10.3%); £3,771,447.47 -> £3,381,827.69 (10.3%); £3,771,447.63 -> £3,381,827.72 (10.3%); £3,771,447.79 -> £3,381,827.76 (10.3%); £3,771,447.95 -> £3,381,827.80 (10.3%); £3,771,448.11 -> £3,381,827.84 (10.3%); £3,771,448.26 -> £3,381,827.88 (10.3%); £3,771,448.43 -> £3,381,827.91 (10.3%); £3,771,448.58 -> £3,381,827.95 (10.3%); £3,771,448.75 -> £3,381,827.99 (10.3%); £3,771,448.90 -> £3,381,828.03 (10.3%); £3,771,449.06 -> £3,381,828.23 (10.3%); £3,771,449.22 -> £3,381,828.44 (10.3%); £3,771,449.39 -> £3,381,828.67 (10.3%); £3,771,449.59 -> £3,381,828.91 (10.3%); £3,771,449.79 -> £3,381,829.17 (10.3%); £3,771,450.02 -> £3,381,829.43 (10.3%); £3,771,450.28 -> £3,381,829.74 (10.3%); £3,771,450.55 -> £3,381,830.04 (10.3%); £3,771,450.81 -> £3,381,830.16 (10.3%); £3,771,451.08 -> £3,381,830.28 (10.3%); £3,771,451.35 -> £3,381,830.41 (10.3%); £3,771,451.61 -> £3,381,830.53 (10.3%); £3,771,451.88 -> £3,381,830.66 (10.3%); £3,771,452.14 -> £3,381,830.79 (10.3%); £3,771,452.40 -> £3,381,830.91 (10.3%); £3,771,452.65 -> £3,381,831.03 (10.3%); £3,771,452.93 -> £3,381,831.15 (10.3%); £3,771,453.19 -> £3,381,831.26 (10.3%); £3,771,453.46 -> £3,381,831.38 (10.3%); £3,771,453.72 -> £3,381,831.49 (10.3%); £3,771,453.99 -> £3,381,831.60 (10.3%); £3,771,454.25 -> £3,381,831.90 (10.3%); £3,771,454.51 -> £3,381,832.17 (10.3%); £3,771,454.72 -> £3,381,832.42 (10.3%); £3,771,454.91 -> £3,381,832.64 (10.3%); £3,771,455.12 -> £3,381,832.86 (10.3%); £3,771,455.39 -> £3,381,833.08 (10.3%); £3,771,455.65 -> £3,381,833.29 (10.3%); £3,771,455.92 -> £3,381,833.50 (10.3%); £3,771,456.18 -> £3,381,833.70 (10.3%); £3,771,456.45 -> £3,381,833.90 (10.3%); £3,771,456.71 -> £3,381,834.10 (10.3%); £3,771,456.98 -> £3,381,834.15 (10.3%); £3,771,457.25 -> £3,381,834.19 (10.3%); £3,771,457.49 -> £3,381,834.23 (10.3%); £3,771,457.71 -> £3,381,834.27 (10.3%); £3,771,457.92 -> £3,381,834.30 (10.3%); £3,771,458.08 -> £3,381,834.34 (10.3%); £3,771,458.24 -> £3,381,834.38 (10.3%); £3,771,458.40 -> £3,381,834.42 (10.3%); £3,771,458.56 -> £3,381,834.46 (10.3%); £3,771,458.71 -> £3,381,834.49 (10.3%); £3,771,458.87 -> £3,381,834.53 (10.3%); £3,771,459.03 -> £3,381,834.57 (10.3%); £3,771,459.19 -> £3,381,834.61 (10.3%); £3,771,459.35 -> £3,381,834.65 (10.3%); £3,771,459.51 -> £3,381,834.69 (10.3%); £3,771,459.67 -> £3,381,834.73 (10.3%); £3,771,459.84 -> £3,381,834.94 (10.3%); £3,771,460.00 -> £3,381,835.15 (10.3%); £3,771,460.17 -> £3,381,835.36 (10.3%); £3,771,460.36 -> £3,381,835.58 (10.3%); £3,771,460.57 -> £3,381,835.82 (10.3%); £3,771,460.79 -> £3,381,836.09 (10.3%); £3,771,461.03 -> £3,381,836.38 (10.3%); £3,771,461.30 -> £3,381,836.69 (10.3%); £3,771,461.56 -> £3,381,836.82 (10.3%); £3,771,461.82 -> £3,381,836.95 (10.3%); £3,771,462.08 -> £3,381,837.08 (10.3%); £3,771,462.35 -> £3,381,837.21 (10.3%); £3,771,462.61 -> £3,381,837.34 (10.3%); £3,771,462.88 -> £3,381,837.46 (10.3%); £3,771,463.14 -> £3,381,837.58 (10.3%); £3,771,463.42 -> £3,381,837.70 (10.3%); £3,771,463.67 -> £3,381,837.82 (10.3%); £3,771,463.94 -> £3,381,837.93 (10.3%); £3,771,464.21 -> £3,381,838.05 (10.3%); £3,771,464.48 -> £3,381,838.16 (10.3%); £3,771,464.75 -> £3,381,838.27 (10.3%); £3,771,465.01 -> £3,381,838.56 (10.3%); £3,771,465.21 -> £3,381,838.82 (10.3%); £3,771,465.41 -> £3,381,839.06 (10.3%); £3,771,465.60 -> £3,381,839.28 (10.3%); £3,771,465.80 -> £3,381,839.50 (10.3%); £3,771,466.00 -> £3,381,839.71 (10.3%); £3,771,466.27 -> £3,381,839.92 (10.3%); £3,771,466.53 -> £3,381,840.12 (10.3%); £3,771,466.79 -> £3,381,840.33 (10.3%); £3,771,467.06 -> £3,381,840.53 (10.3%); £3,771,467.32 -> £3,381,840.72 (10.3%); £3,771,467.58 -> £3,381,840.76 (10.3%); £3,771,467.85 -> £3,381,840.80 (10.3%); £3,771,468.10 -> £3,381,840.84 (10.3%); £3,771,468.32 -> £3,381,840.88 (10.3%); £3,771,468.52 -> £3,381,840.91 (10.3%); £3,771,468.68 -> £3,381,840.95 (10.3%); £3,771,468.84 -> £3,381,840.99 (10.3%); £3,771,469.00 -> £3,381,841.03 (10.3%); £3,771,469.16 -> £3,381,841.07 (10.3%); £3,771,469.31 -> £3,381,841.10 (10.3%); £3,771,469.47 -> £3,381,841.14 (10.3%); £3,771,469.63 -> £3,381,841.18 (10.3%); £3,771,469.79 -> £3,381,841.21 (10.3%); £3,771,469.96 -> £3,381,841.25 (10.3%); £3,771,470.11 -> £3,381,841.29 (10.3%); £3,771,470.27 -> £3,381,841.33 (10.3%); £3,771,470.43 -> £3,381,841.47 (10.3%); £3,771,470.58 -> £3,381,841.61 (10.3%); £3,771,470.76 -> £3,381,841.77 (10.3%); £3,771,470.96 -> £3,381,841.94 (10.3%); £3,771,471.17 -> £3,381,842.13 (10.3%); £3,771,471.40 -> £3,381,842.34 (10.3%); £3,771,471.64 -> £3,381,842.58 (10.3%); £3,771,471.92 -> £3,381,842.82 (10.3%); £3,771,472.19 -> £3,381,842.95 (10.3%); £3,771,472.47 -> £3,381,843.07 (10.3%); £3,771,472.73 -> £3,381,843.20 (10.3%); £3,771,473.00 -> £3,381,843.34 (10.3%); £3,771,473.26 -> £3,381,843.47 (10.3%); £3,771,473.53 -> £3,381,843.59 (10.3%); £3,771,473.79 -> £3,381,843.71 (10.3%); £3,771,474.06 -> £3,381,843.83 (10.3%); £3,771,474.33 -> £3,381,843.95 (10.3%); £3,771,474.58 -> £3,381,844.07 (10.3%); £3,771,474.85 -> £3,381,844.19 (10.3%); £3,771,475.11 -> £3,381,844.30 (10.3%); £3,771,475.39 -> £3,381,844.42 (10.3%); £3,771,475.66 -> £3,381,844.66 (10.3%); £3,771,475.92 -> £3,381,844.88 (10.3%); £3,771,476.19 -> £3,381,845.07 (10.3%); £3,771,476.45 -> £3,381,845.25 (10.3%); £3,771,476.71 -> £3,381,845.41 (10.3%); £3,771,476.98 -> £3,381,845.58 (10.3%); £3,771,477.24 -> £3,381,845.74 (10.3%); £3,771,477.51 -> £3,381,845.89 (10.3%); £3,771,477.78 -> £3,381,846.05 (10.3%); £3,771,478.04 -> £3,381,846.19 (10.3%); £3,771,478.30 -> £3,381,846.34 (10.3%); £3,771,478.57 -> £3,381,846.38 (10.3%); £3,771,478.84 -> £3,381,846.42 (10.3%); £3,771,479.09 -> £3,381,846.46 (10.3%); £3,771,479.32 -> £3,381,846.50 (10.3%); £3,771,479.53 -> £3,381,846.54 (10.3%); £3,771,479.66 -> £3,381,846.58 (10.3%); £3,771,479.80 -> £3,381,846.61 (10.3%); £3,771,479.94 -> £3,381,846.65 (10.3%); £3,771,480.08 -> £3,381,846.69 (10.3%); £3,771,480.22 -> £3,381,846.73 (10.3%); £3,771,480.36 -> £3,381,846.77 (10.3%); £3,771,480.50 -> £3,381,846.81 (10.3%); £3,771,480.64 -> £3,381,846.84 (10.3%); £3,771,480.78 -> £3,381,846.88 (10.3%); £3,771,480.92 -> £3,381,846.92 (10.3%); £3,771,481.06 -> £3,381,846.96 (10.3%); £3,771,481.20 -> £3,381,847.10 (10.3%); £3,771,481.34 -> £3,381,847.25 (10.3%); £3,771,481.50 -> £3,381,847.39 (10.3%); £3,771,481.67 -> £3,381,847.53 (10.3%); £3,771,481.85 -> £3,381,847.69 (10.3%); £3,771,482.05 -> £3,381,847.85 (10.3%); £3,771,482.27 -> £3,381,848.04 (10.3%); £3,771,482.50 -> £3,381,848.24 (10.3%); £3,771,482.73 -> £3,381,848.33 (10.3%); £3,771,482.97 -> £3,381,848.42 (10.3%); £3,771,483.20 -> £3,381,848.51 (10.3%); £3,771,483.43 -> £3,381,848.60 (10.3%); £3,771,483.66 -> £3,381,848.69 (10.3%); £3,771,483.89 -> £3,381,848.77 (10.3%); £3,771,484.13 -> £3,381,848.85 (10.3%); £3,771,484.36 -> £3,381,848.92 (10.3%); £3,771,484.59 -> £3,381,848.99 (10.3%); £3,771,484.82 -> £3,381,849.06 (10.3%); £3,771,485.05 -> £3,381,849.14 (10.3%); £3,771,485.29 -> £3,381,849.20 (10.3%); £3,771,485.52 -> £3,381,849.27 (10.3%); £3,771,485.75 -> £3,381,849.44 (10.3%); £3,771,485.93 -> £3,381,849.61 (10.3%); £3,771,486.17 -> £3,381,849.76 (10.3%); £3,771,486.34 -> £3,381,849.90 (10.3%); £3,771,486.51 -> £3,381,850.04 (10.3%); £3,771,486.69 -> £3,381,850.18 (10.3%); £3,771,486.86 -> £3,381,850.33 (10.3%); £3,771,487.10 -> £3,381,850.48 (10.3%); £3,771,487.33 -> £3,381,850.63 (10.3%); £3,771,487.56 -> £3,381,850.76 (10.3%); £3,771,487.78 -> £3,381,850.90 (10.3%); £3,771,488.01 -> £3,381,850.95 (10.3%); £3,771,488.25 -> £3,381,850.99 (10.3%); £3,771,488.46 -> £3,381,851.03 (10.3%); £3,771,488.65 -> £3,381,851.07 (10.3%); £3,771,488.83 -> £3,381,851.10 (10.3%); £3,771,488.97 -> £3,381,851.14 (10.3%); £3,771,489.11 -> £3,381,851.18 (10.3%); £3,771,489.25 -> £3,381,851.22 (10.3%); £3,771,489.39 -> £3,381,851.26 (10.3%); £3,771,489.53 -> £3,381,851.30 (10.3%); £3,771,489.67 -> £3,381,851.34 (10.3%); £3,771,489.81 -> £3,381,851.37 (10.3%); £3,771,489.95 -> £3,381,851.41 (10.3%); £3,771,490.09 -> £3,381,851.45 (10.3%); £3,771,490.23 -> £3,381,851.49 (10.3%); £3,771,490.37 -> £3,381,851.52 (10.3%); £3,771,490.51 -> £3,381,851.65 (10.3%); £3,771,490.66 -> £3,381,851.78 (10.3%); £3,771,490.82 -> £3,381,851.91 (10.3%); £3,771,490.98 -> £3,381,852.04 (10.3%); £3,771,491.16 -> £3,381,852.18 (10.3%); £3,771,491.36 -> £3,381,852.31 (10.3%); £3,771,491.59 -> £3,381,852.44 (10.3%); £3,771,491.82 -> £3,381,852.58 (10.3%); £3,771,492.05 -> £3,381,852.63 (10.3%); £3,771,492.29 -> £3,381,852.68 (10.3%); £3,771,492.52 -> £3,381,852.73 (10.3%); £3,771,492.76 -> £3,381,852.79 (10.3%); £3,771,492.99 -> £3,381,852.84 (10.3%); £3,771,493.23 -> £3,381,852.89 (10.3%); £3,771,493.47 -> £3,381,852.93 (10.3%); £3,771,493.71 -> £3,381,852.98 (10.3%); £3,771,493.94 -> £3,381,853.02 (10.3%); £3,771,494.18 -> £3,381,853.07 (10.3%); £3,771,494.42 -> £3,381,853.12 (10.3%); £3,771,494.65 -> £3,381,853.16 (10.3%); £3,771,494.89 -> £3,381,853.21 (10.3%); £3,771,495.12 -> £3,381,853.35 (10.3%); £3,771,495.35 -> £3,381,853.48 (10.3%); £3,771,495.52 -> £3,381,853.61 (10.3%); £3,771,495.70 -> £3,381,853.74 (10.3%); £3,771,495.88 -> £3,381,853.88 (10.3%); £3,771,496.05 -> £3,381,854.01 (10.3%); £3,771,496.23 -> £3,381,854.14 (10.3%); £3,771,496.47 -> £3,381,854.27 (10.3%); £3,771,496.70 -> £3,381,854.40 (10.3%); £3,771,496.94 -> £3,381,854.53 (10.3%); £3,771,497.17 -> £3,381,854.67 (10.3%); £3,771,497.40 -> £3,381,854.71 (10.3%); £3,771,497.64 -> £3,381,854.75 (10.3%); £3,771,497.86 -> £3,381,854.79 (10.3%); £3,771,498.06 -> £3,381,854.83 (10.3%); £3,771,498.24 -> £3,381,854.86 (10.3%); £3,771,498.40 -> £3,381,854.90 (10.3%); £3,771,498.56 -> £3,381,854.94 (10.3%); £3,771,498.73 -> £3,381,854.98 (10.3%); £3,771,498.89 -> £3,381,855.02 (10.3%); £3,771,499.05 -> £3,381,855.06 (10.3%); £3,771,499.21 -> £3,381,855.09 (10.3%); £3,771,499.38 -> £3,381,855.13 (10.3%); £3,771,499.54 -> £3,381,855.17 (10.3%); £3,771,499.71 -> £3,381,855.21 (10.3%); £3,771,499.87 -> £3,381,855.25 (10.3%); £3,771,500.03 -> £3,381,855.29 (10.3%); £3,771,500.20 -> £3,381,855.44 (10.3%); £3,771,500.36 -> £3,381,855.58 (10.3%); £3,771,500.54 -> £3,381,855.73 (10.3%); £3,771,500.75 -> £3,381,855.90 (10.3%); £3,771,500.97 -> £3,381,856.08 (10.3%); £3,771,501.21 -> £3,381,856.29 (10.3%); £3,771,501.46 -> £3,381,856.53 (10.3%); £3,771,501.72 -> £3,381,856.79 (10.3%); £3,771,502.00 -> £3,381,856.92 (10.3%); £3,771,502.27 -> £3,381,857.04 (10.3%); £3,771,502.55 -> £3,381,857.17 (10.3%); £3,771,502.82 -> £3,381,857.29 (10.3%); £3,771,503.09 -> £3,381,857.42 (10.3%); £3,771,503.36 -> £3,381,857.54 (10.3%); £3,771,503.63 -> £3,381,857.65 (10.3%); £3,771,503.89 -> £3,381,857.76 (10.3%); £3,771,504.16 -> £3,381,857.88 (10.3%); £3,771,504.42 -> £3,381,857.99 (10.3%); £3,771,504.70 -> £3,381,858.10 (10.3%); £3,771,504.98 -> £3,381,858.21 (10.3%); £3,771,505.24 -> £3,381,858.32 (10.3%); £3,771,505.45 -> £3,381,858.55 (10.3%); £3,771,505.65 -> £3,381,858.77 (10.3%); £3,771,505.85 -> £3,381,858.96 (10.3%); £3,771,506.05 -> £3,381,859.12 (10.3%); £3,771,506.26 -> £3,381,859.29 (10.3%); £3,771,506.54 -> £3,381,859.46 (10.3%); £3,771,506.81 -> £3,381,859.62 (10.3%); £3,771,507.10 -> £3,381,859.77 (10.3%); £3,771,507.37 -> £3,381,859.92 (10.3%); £3,771,507.64 -> £3,381,860.06 (10.3%); £3,771,507.91 -> £3,381,860.20 (10.3%); £3,771,508.18 -> £3,381,860.24 (10.3%); £3,771,508.45 -> £3,381,860.29 (10.3%); £3,771,508.70 -> £3,381,860.33 (10.3%); £3,771,508.93 -> £3,381,860.37 (10.3%); £3,771,509.15 -> £3,381,860.40 (10.3%); £3,771,509.32 -> £3,381,860.44 (10.3%); £3,771,509.48 -> £3,381,860.48 (10.3%); £3,771,509.65 -> £3,381,860.52 (10.3%); £3,771,509.82 -> £3,381,860.56 (10.3%); £3,771,509.99 -> £3,381,860.60 (10.3%); £3,771,510.15 -> £3,381,860.63 (10.3%); £3,771,510.32 -> £3,381,860.67 (10.3%); £3,771,510.48 -> £3,381,860.71 (10.3%); £3,771,510.64 -> £3,381,860.75 (10.3%); £3,771,510.81 -> £3,381,860.79 (10.3%); £3,771,510.98 -> £3,381,860.83 (10.3%); £3,771,511.14 -> £3,381,861.00 (10.3%); £3,771,511.31 -> £3,381,861.16 (10.3%); £3,771,511.50 -> £3,381,861.34 (10.3%); £3,771,511.70 -> £3,381,861.53 (10.3%); £3,771,511.92 -> £3,381,861.74 (10.3%); £3,771,512.15 -> £3,381,861.97 (10.3%); £3,771,512.41 -> £3,381,862.23 (10.3%); £3,771,512.68 -> £3,381,862.49 (10.3%); £3,771,512.95 -> £3,381,862.62 (10.3%); £3,771,513.23 -> £3,381,862.75 (10.3%); £3,771,513.51 -> £3,381,862.87 (10.3%); £3,771,513.79 -> £3,381,863.01 (10.3%); £3,771,514.06 -> £3,381,863.13 (10.3%); £3,771,514.33 -> £3,381,863.26 (10.3%); £3,771,514.60 -> £3,381,863.38 (10.3%); £3,771,514.88 -> £3,381,863.49 (10.3%); £3,771,515.15 -> £3,381,863.61 (10.3%); £3,771,515.43 -> £3,381,863.72 (10.3%); £3,771,515.69 -> £3,381,863.84 (10.3%); £3,771,515.96 -> £3,381,863.95 (10.3%); £3,771,516.23 -> £3,381,864.05 (10.3%); £3,771,516.44 -> £3,381,864.30 (10.3%); £3,771,516.65 -> £3,381,864.53 (10.3%); £3,771,516.85 -> £3,381,864.72 (10.3%); £3,771,517.06 -> £3,381,864.90 (10.3%); £3,771,517.26 -> £3,381,865.07 (10.3%); £3,771,517.47 -> £3,381,865.24 (10.3%); £3,771,517.68 -> £3,381,865.40 (10.3%); £3,771,517.95 -> £3,381,865.56 (10.3%); £3,771,518.22 -> £3,381,865.72 (10.3%); £3,771,518.49 -> £3,381,865.87 (10.3%); £3,771,518.77 -> £3,381,866.02 (10.3%); £3,771,519.05 -> £3,381,866.06 (10.3%); £3,771,519.31 -> £3,381,866.11 (10.3%); £3,771,519.56 -> £3,381,866.15 (10.3%); £3,771,519.80 -> £3,381,866.18 (10.3%); £3,771,520.00 -> £3,381,866.22 (10.3%); £3,771,520.17 -> £3,381,866.26 (10.3%); £3,771,520.34 -> £3,381,866.29 (10.3%); £3,771,520.50 -> £3,381,866.33 (10.3%); £3,771,520.66 -> £3,381,866.37 (10.3%); £3,771,520.83 -> £3,381,866.41 (10.3%); £3,771,521.00 -> £3,381,866.44 (10.3%); £3,771,521.16 -> £3,381,866.48 (10.3%); £3,771,521.33 -> £3,381,866.52 (10.3%); £3,771,521.49 -> £3,381,866.56 (10.3%); £3,771,521.66 -> £3,381,866.60 (10.3%); £3,771,521.82 -> £3,381,866.64 (10.3%); £3,771,521.99 -> £3,381,866.86 (10.3%); £3,771,522.15 -> £3,381,867.10 (10.3%); £3,771,522.34 -> £3,381,867.35 (10.3%); £3,771,522.54 -> £3,381,867.60 (10.3%); £3,771,522.77 -> £3,381,867.88 (10.3%); £3,771,523.01 -> £3,381,868.18 (10.3%); £3,771,523.26 -> £3,381,868.49 (10.3%); £3,771,523.54 -> £3,381,868.82 (10.3%); £3,771,523.83 -> £3,381,868.94 (10.3%); £3,771,524.11 -> £3,381,869.06 (10.3%); £3,771,524.39 -> £3,381,869.19 (10.3%); £3,771,524.67 -> £3,381,869.32 (10.3%); £3,771,524.94 -> £3,381,869.44 (10.3%); £3,771,525.22 -> £3,381,869.57 (10.3%); £3,771,525.49 -> £3,381,869.69 (10.3%); £3,771,525.76 -> £3,381,869.80 (10.3%); £3,771,526.03 -> £3,381,869.92 (10.3%); £3,771,526.32 -> £3,381,870.03 (10.3%); £3,771,526.58 -> £3,381,870.15 (10.3%); £3,771,526.86 -> £3,381,870.26 (10.3%); £3,771,527.14 -> £3,381,870.37 (10.3%); £3,771,527.35 -> £3,381,870.68 (10.3%); £3,771,527.55 -> £3,381,870.98 (10.3%); £3,771,527.83 -> £3,381,871.24 (10.3%); £3,771,528.03 -> £3,381,871.48 (10.3%); £3,771,528.23 -> £3,381,871.72 (10.3%); £3,771,528.44 -> £3,381,871.96 (10.3%); £3,771,528.71 -> £3,381,872.20 (10.3%); £3,771,528.99 -> £3,381,872.44 (10.3%); £3,771,529.25 -> £3,381,872.67 (10.3%); £3,771,529.53 -> £3,381,872.90 (10.3%); £3,771,529.80 -> £3,381,873.11 (10.3%); £3,771,530.08 -> £3,381,873.15 (10.3%); £3,771,530.36 -> £3,381,873.19 (10.3%); £3,771,530.62 -> £3,381,873.23 (10.3%); £3,771,530.86 -> £3,381,873.27 (10.3%); £3,771,531.07 -> £3,381,873.30 (10.3%); £3,771,531.24 -> £3,381,873.34 (10.3%); £3,771,531.40 -> £3,381,873.38 (10.3%); £3,771,531.57 -> £3,381,873.42 (10.3%); £3,771,531.73 -> £3,381,873.45 (10.3%); £3,771,531.90 -> £3,381,873.49 (10.3%); £3,771,532.07 -> £3,381,873.53 (10.3%); £3,771,532.23 -> £3,381,873.56 (10.3%); £3,771,532.40 -> £3,381,873.60 (10.3%); £3,771,532.56 -> £3,381,873.64 (10.3%); £3,771,532.72 -> £3,381,873.68 (10.3%); £3,771,532.88 -> £3,381,873.72 (10.3%); £3,771,533.05 -> £3,381,873.96 (10.3%); £3,771,533.21 -> £3,381,874.20 (10.3%); £3,771,533.40 -> £3,381,874.45 (10.3%); £3,771,533.60 -> £3,381,874.72 (10.3%); £3,771,533.82 -> £3,381,875.02 (10.3%); £3,771,534.06 -> £3,381,875.34 (10.3%); £3,771,534.32 -> £3,381,875.68 (10.3%); £3,771,534.60 -> £3,381,876.02 (10.3%); £3,771,534.87 -> £3,381,876.14 (10.3%); £3,771,535.15 -> £3,381,876.26 (10.3%); £3,771,535.42 -> £3,381,876.39 (10.3%); £3,771,535.70 -> £3,381,876.52 (10.3%); £3,771,535.98 -> £3,381,876.64 (10.3%); £3,771,536.24 -> £3,381,876.77 (10.3%); £3,771,536.52 -> £3,381,876.88 (10.3%); £3,771,536.80 -> £3,381,876.99 (10.3%); £3,771,537.07 -> £3,381,877.10 (10.3%); £3,771,537.34 -> £3,381,877.22 (10.3%); £3,771,537.62 -> £3,381,877.33 (10.3%); £3,771,537.89 -> £3,381,877.44 (10.3%); £3,771,538.16 -> £3,381,877.55 (10.3%); £3,771,538.36 -> £3,381,877.88 (10.3%); £3,771,538.65 -> £3,381,878.19 (10.3%); £3,771,538.85 -> £3,381,878.48 (10.3%); £3,771,539.12 -> £3,381,878.75 (10.3%); £3,771,539.39 -> £3,381,879.01 (10.3%); £3,771,539.66 -> £3,381,879.26 (10.3%); £3,771,539.93 -> £3,381,879.52 (10.3%); £3,771,540.21 -> £3,381,879.76 (10.3%); £3,771,540.49 -> £3,381,880.00 (10.3%); £3,771,540.77 -> £3,381,880.23 (10.3%); £3,771,541.04 -> £3,381,880.47 (10.3%); £3,771,541.33 -> £3,381,880.51 (10.3%); £3,771,541.60 -> £3,381,880.55 (10.3%); £3,771,541.85 -> £3,381,880.59 (10.3%); £3,771,542.09 -> £3,381,880.63 (10.3%); £3,771,542.30 -> £3,381,880.67 (10.3%); £3,771,542.47 -> £3,381,880.70 (10.3%); £3,771,542.63 -> £3,381,880.74 (10.3%); £3,771,542.80 -> £3,381,880.78 (10.3%); £3,771,542.96 -> £3,381,880.81 (10.3%); £3,771,543.12 -> £3,381,880.85 (10.3%); £3,771,543.29 -> £3,381,880.89 (10.3%); £3,771,543.45 -> £3,381,880.92 (10.3%); £3,771,543.61 -> £3,381,880.96 (10.3%); £3,771,543.78 -> £3,381,881.00 (10.3%); £3,771,543.94 -> £3,381,881.04 (10.3%); £3,771,544.10 -> £3,381,881.08 (10.3%); £3,771,544.28 -> £3,381,881.27 (10.3%); £3,771,544.44 -> £3,381,881.47 (10.3%); £3,771,544.62 -> £3,381,881.67 (10.3%); £3,771,544.82 -> £3,381,881.89 (10.3%); £3,771,545.04 -> £3,381,882.13 (10.3%); £3,771,545.26 -> £3,381,882.39 (10.3%); £3,771,545.52 -> £3,381,882.68 (10.3%); £3,771,545.79 -> £3,381,882.98 (10.3%); £3,771,546.06 -> £3,381,883.11 (10.3%); £3,771,546.34 -> £3,381,883.25 (10.3%); £3,771,546.60 -> £3,381,883.38 (10.3%); £3,771,546.88 -> £3,381,883.52 (10.3%); £3,771,547.14 -> £3,381,883.66 (10.3%); £3,771,547.40 -> £3,381,883.79 (10.3%); £3,771,547.67 -> £3,381,883.92 (10.3%); £3,771,547.93 -> £3,381,884.05 (10.3%); £3,771,548.21 -> £3,381,884.16 (10.3%); £3,771,548.50 -> £3,381,884.28 (10.3%); £3,771,548.76 -> £3,381,884.40 (10.3%); £3,771,549.04 -> £3,381,884.51 (10.3%); £3,771,549.30 -> £3,381,884.62 (10.3%); £3,771,549.57 -> £3,381,884.91 (10.3%); £3,771,549.84 -> £3,381,885.19 (10.3%); £3,771,550.12 -> £3,381,885.43 (10.3%); £3,771,550.40 -> £3,381,885.65 (10.3%); £3,771,550.67 -> £3,381,885.85 (10.3%); £3,771,550.87 -> £3,381,886.06 (10.3%); £3,771,551.08 -> £3,381,886.26 (10.3%); £3,771,551.35 -> £3,381,886.45 (10.3%); £3,771,551.62 -> £3,381,886.65 (10.3%); £3,771,551.88 -> £3,381,886.85 (10.3%); £3,771,552.15 -> £3,381,887.03 (10.3%); £3,771,552.43 -> £3,381,887.07 (10.3%); £3,771,552.69 -> £3,381,887.11 (10.3%); £3,771,552.94 -> £3,381,887.15 (10.3%); £3,771,553.18 -> £3,381,887.19 (10.3%); £3,771,553.39 -> £3,381,887.23 (10.3%); £3,771,553.54 -> £3,381,887.26 (10.3%); £3,771,553.68 -> £3,381,887.30 (10.3%); £3,771,553.83 -> £3,381,887.34 (10.3%); £3,771,553.97 -> £3,381,887.38 (10.3%); £3,771,554.11 -> £3,381,887.41 (10.3%); £3,771,554.25 -> £3,381,887.45 (10.3%); £3,771,554.39 -> £3,381,887.48 (10.3%); £3,771,554.53 -> £3,381,887.52 (10.3%); £3,771,554.67 -> £3,381,887.56 (10.3%); £3,771,554.82 -> £3,381,887.59 (10.3%); £3,771,554.96 -> £3,381,887.63 (10.3%); £3,771,555.10 -> £3,381,887.81 (10.3%); £3,771,555.25 -> £3,381,887.99 (10.3%); £3,771,555.41 -> £3,381,888.17 (10.3%); £3,771,555.59 -> £3,381,888.36 (10.3%); £3,771,555.78 -> £3,381,888.56 (10.3%); £3,771,555.99 -> £3,381,888.78 (10.3%); £3,771,556.21 -> £3,381,889.02 (10.3%); £3,771,556.44 -> £3,381,889.27 (10.3%); £3,771,556.68 -> £3,381,889.36 (10.3%); £3,771,556.92 -> £3,381,889.45 (10.3%); £3,771,557.16 -> £3,381,889.54 (10.3%); £3,771,557.41 -> £3,381,889.63 (10.3%); £3,771,557.64 -> £3,381,889.72 (10.3%); £3,771,557.87 -> £3,381,889.80 (10.3%); £3,771,558.11 -> £3,381,889.87 (10.3%); £3,771,558.35 -> £3,381,889.94 (10.3%); £3,771,558.59 -> £3,381,890.02 (10.3%); £3,771,558.83 -> £3,381,890.08 (10.3%); £3,771,559.07 -> £3,381,890.15 (10.3%); £3,771,559.30 -> £3,381,890.22 (10.3%); £3,771,559.55 -> £3,381,890.29 (10.3%); £3,771,559.79 -> £3,381,890.51 (10.3%); £3,771,560.02 -> £3,381,890.73 (10.3%); £3,771,560.26 -> £3,381,890.92 (10.3%); £3,771,560.44 -> £3,381,891.11 (10.3%); £3,771,560.67 -> £3,381,891.30 (10.3%); £3,771,560.85 -> £3,381,891.48 (10.3%); £3,771,561.03 -> £3,381,891.67 (10.3%); £3,771,561.28 -> £3,381,891.86 (10.3%); £3,771,561.52 -> £3,381,892.05 (10.3%); £3,771,561.76 -> £3,381,892.24 (10.3%); £3,771,562.00 -> £3,381,892.42 (10.3%); £3,771,562.24 -> £3,381,892.46 (10.3%); £3,771,562.48 -> £3,381,892.50 (10.3%); £3,771,562.70 -> £3,381,892.54 (10.3%); £3,771,562.91 -> £3,381,892.58 (10.3%); £3,771,563.10 -> £3,381,892.62 (10.3%); £3,771,563.24 -> £3,381,892.65 (10.3%); £3,771,563.38 -> £3,381,892.69 (10.3%); £3,771,563.51 -> £3,381,892.73 (10.3%); £3,771,563.65 -> £3,381,892.77 (10.3%); £3,771,563.79 -> £3,381,892.80 (10.3%); £3,771,563.94 -> £3,381,892.84 (10.3%); £3,771,564.08 -> £3,381,892.88 (10.3%); £3,771,564.22 -> £3,381,892.91 (10.3%); £3,771,564.36 -> £3,381,892.95 (10.3%); £3,771,564.50 -> £3,381,892.98 (10.3%); £3,771,564.64 -> £3,381,893.02 (10.3%); £3,771,564.78 -> £3,381,893.21 (10.3%); £3,771,564.91 -> £3,381,893.40 (10.3%); £3,771,565.07 -> £3,381,893.58 (10.3%); £3,771,565.23 -> £3,381,893.77 (10.3%); £3,771,565.42 -> £3,381,893.96 (10.3%); £3,771,565.63 -> £3,381,894.15 (10.3%); £3,771,565.85 -> £3,381,894.35 (10.3%); £3,771,566.09 -> £3,381,894.55 (10.3%); £3,771,566.32 -> £3,381,894.60 (10.3%); £3,771,566.56 -> £3,381,894.64 (10.3%); £3,771,566.79 -> £3,381,894.69 (10.3%); £3,771,567.02 -> £3,381,894.74 (10.3%); £3,771,567.26 -> £3,381,894.79 (10.3%); £3,771,567.50 -> £3,381,894.84 (10.3%); £3,771,567.73 -> £3,381,894.89 (10.3%); £3,771,567.97 -> £3,381,894.93 (10.3%); £3,771,568.20 -> £3,381,894.98 (10.3%); £3,771,568.44 -> £3,381,895.03 (10.3%); £3,771,568.67 -> £3,381,895.07 (10.3%); £3,771,568.90 -> £3,381,895.12 (10.3%); £3,771,569.13 -> £3,381,895.17 (10.3%); £3,771,569.37 -> £3,381,895.36 (10.3%); £3,771,569.60 -> £3,381,895.55 (10.3%); £3,771,569.78 -> £3,381,895.74 (10.3%); £3,771,569.95 -> £3,381,895.93 (10.3%); £3,771,570.13 -> £3,381,896.11 (10.3%); £3,771,570.31 -> £3,381,896.30 (10.3%); £3,771,570.49 -> £3,381,896.50 (10.3%); £3,771,570.72 -> £3,381,896.69 (10.3%); £3,771,570.95 -> £3,381,896.88 (10.3%); £3,771,571.18 -> £3,381,897.07 (10.3%); £3,771,571.42 -> £3,381,897.25 (10.3%); £3,771,571.65 -> £3,381,897.29 (10.3%); £3,771,571.89 -> £3,381,897.32 (10.3%); £3,771,572.11 -> £3,381,897.36 (10.3%); £3,771,572.31 -> £3,381,897.40 (10.3%); £3,771,572.49 -> £3,381,897.43 (10.3%); £3,771,572.65 -> £3,381,897.47 (10.3%); £3,771,572.80 -> £3,381,897.51 (10.3%); £3,771,572.96 -> £3,381,897.55 (10.3%); £3,771,573.11 -> £3,381,897.58 (10.3%); £3,771,573.27 -> £3,381,897.62 (10.3%); £3,771,573.42 -> £3,381,897.66 (10.3%); £3,771,573.58 -> £3,381,897.69 (10.3%); £3,771,573.74 -> £3,381,897.73 (10.3%); £3,771,573.89 -> £3,381,897.77 (10.3%); £3,771,574.04 -> £3,381,897.81 (10.3%); £3,771,574.20 -> £3,381,897.85 (10.3%); £3,771,574.35 -> £3,381,898.06 (10.3%); £3,771,574.51 -> £3,381,898.28 (10.3%); £3,771,574.68 -> £3,381,898.51 (10.3%); £3,771,574.87 -> £3,381,898.74 (10.3%); £3,771,575.09 -> £3,381,898.99 (10.3%); £3,771,575.31 -> £3,381,899.28 (10.3%); £3,771,575.55 -> £3,381,899.59 (10.3%); £3,771,575.81 -> £3,381,899.91 (10.3%); £3,771,576.07 -> £3,381,900.04 (10.3%); £3,771,576.32 -> £3,381,900.16 (10.3%); £3,771,576.58 -> £3,381,900.29 (10.3%); £3,771,576.84 -> £3,381,900.42 (10.3%); £3,771,577.10 -> £3,381,900.55 (10.3%); £3,771,577.36 -> £3,381,900.68 (10.3%); £3,771,577.62 -> £3,381,900.79 (10.3%); £3,771,577.88 -> £3,381,900.91 (10.3%); £3,771,578.14 -> £3,381,901.03 (10.3%); £3,771,578.40 -> £3,381,901.15 (10.3%); £3,771,578.65 -> £3,381,901.26 (10.3%); £3,771,578.92 -> £3,381,901.38 (10.3%); £3,771,579.18 -> £3,381,901.48 (10.3%); £3,771,579.38 -> £3,381,901.78 (10.3%); £3,771,579.57 -> £3,381,902.06 (10.3%); £3,771,579.76 -> £3,381,902.31 (10.3%); £3,771,579.95 -> £3,381,902.54 (10.3%); £3,771,580.15 -> £3,381,902.76 (10.3%); £3,771,580.34 -> £3,381,902.98 (10.3%); £3,771,580.53 -> £3,381,903.19 (10.3%); £3,771,580.80 -> £3,381,903.40 (10.3%); £3,771,581.05 -> £3,381,903.62 (10.3%); £3,771,581.31 -> £3,381,903.82 (10.3%); £3,771,581.57 -> £3,381,904.03 (10.3%); £3,771,581.83 -> £3,381,904.07 (10.3%); £3,771,582.09 -> £3,381,904.11 (10.3%); £3,771,582.33 -> £3,381,904.15 (10.3%); £3,771,582.55 -> £3,381,904.19 (10.3%); £3,771,582.75 -> £3,381,904.22 (10.3%); £3,771,582.91 -> £3,381,904.26 (10.3%); £3,771,583.07 -> £3,381,904.30 (10.3%); £3,771,583.23 -> £3,381,904.34 (10.3%); £3,771,583.39 -> £3,381,904.37 (10.3%); £3,771,583.54 -> £3,381,904.41 (10.3%); £3,771,583.70 -> £3,381,904.44 (10.3%); £3,771,583.85 -> £3,381,904.48 (10.3%); £3,771,584.00 -> £3,381,904.52 (10.3%); £3,771,584.16 -> £3,381,904.56 (10.3%); £3,771,584.32 -> £3,381,904.60 (10.3%); £3,771,584.47 -> £3,381,904.64 (10.3%); £3,771,584.63 -> £3,381,904.82 (10.3%); £3,771,584.79 -> £3,381,905.00 (10.3%); £3,771,584.96 -> £3,381,905.20 (10.3%); £3,771,585.15 -> £3,381,905.41 (10.3%); £3,771,585.37 -> £3,381,905.64 (10.3%); £3,771,585.60 -> £3,381,905.89 (10.3%); £3,771,585.83 -> £3,381,906.17 (10.3%); £3,771,586.09 -> £3,381,906.46 (10.3%); £3,771,586.35 -> £3,381,906.58 (10.3%); £3,771,586.60 -> £3,381,906.71 (10.3%); £3,771,586.86 -> £3,381,906.84 (10.3%); £3,771,587.12 -> £3,381,906.97 (10.3%); £3,771,587.38 -> £3,381,907.09 (10.3%); £3,771,587.64 -> £3,381,907.22 (10.3%); £3,771,587.90 -> £3,381,907.34 (10.3%); £3,771,588.17 -> £3,381,907.46 (10.3%); £3,771,588.43 -> £3,381,907.57 (10.3%); £3,771,588.69 -> £3,381,907.69 (10.3%); £3,771,588.95 -> £3,381,907.81 (10.3%); £3,771,589.20 -> £3,381,907.92 (10.3%); £3,771,589.46 -> £3,381,908.03 (10.3%); £3,771,589.71 -> £3,381,908.32 (10.3%); £3,771,589.98 -> £3,381,908.58 (10.3%); £3,771,590.23 -> £3,381,908.82 (10.3%); £3,771,590.50 -> £3,381,909.03 (10.3%); £3,771,590.75 -> £3,381,909.24 (10.3%); £3,771,591.00 -> £3,381,909.44 (10.3%); £3,771,591.26 -> £3,381,909.64 (10.3%); £3,771,591.52 -> £3,381,909.83 (10.3%); £3,771,591.78 -> £3,381,910.02 (10.3%); £3,771,592.04 -> £3,381,910.21 (10.3%); £3,771,592.30 -> £3,381,910.38 (10.3%); £3,771,592.57 -> £3,381,910.42 (10.3%); £3,771,592.83 -> £3,381,910.46 (10.3%); £3,771,593.07 -> £3,381,910.50 (10.3%); £3,771,593.29 -> £3,381,910.54 (10.3%); £3,771,593.49 -> £3,381,910.57 (10.3%); £3,771,593.65 -> £3,381,910.61 (10.3%); £3,771,593.80 -> £3,381,910.65 (10.3%); £3,771,593.96 -> £3,381,910.69 (10.3%); £3,771,594.11 -> £3,381,910.72 (10.3%); £3,771,594.26 -> £3,381,910.76 (10.3%); £3,771,594.41 -> £3,381,910.80 (10.3%); £3,771,594.57 -> £3,381,910.84 (10.3%); £3,771,594.72 -> £3,381,910.87 (10.3%); £3,771,594.88 -> £3,381,910.91 (10.3%); £3,771,595.04 -> £3,381,910.95 (10.3%); £3,771,595.19 -> £3,381,910.99 (10.3%); £3,771,595.35 -> £3,381,911.11 (10.3%); £3,771,595.51 -> £3,381,911.24 (10.3%); £3,771,595.69 -> £3,381,911.38 (10.3%); £3,771,595.88 -> £3,381,911.53 (10.3%); £3,771,596.09 -> £3,381,911.70 (10.3%); £3,771,596.31 -> £3,381,911.90 (10.3%); £3,771,596.55 -> £3,381,912.11 (10.3%); £3,771,596.81 -> £3,381,912.34 (10.3%); £3,771,597.07 -> £3,381,912.47 (10.3%); £3,771,597.33 -> £3,381,912.60 (10.3%); £3,771,597.59 -> £3,381,912.73 (10.3%); £3,771,597.85 -> £3,381,912.86 (10.3%); £3,771,598.11 -> £3,381,912.99 (10.3%); £3,771,598.35 -> £3,381,913.11 (10.3%); £3,771,598.60 -> £3,381,913.22 (10.3%); £3,771,598.87 -> £3,381,913.34 (10.3%); £3,771,599.13 -> £3,381,913.46 (10.3%); £3,771,599.39 -> £3,381,913.57 (10.3%); £3,771,599.65 -> £3,381,913.69 (10.3%); £3,771,599.91 -> £3,381,913.80 (10.3%); £3,771,600.18 -> £3,381,913.91 (10.3%); £3,771,600.43 -> £3,381,914.13 (10.3%); £3,771,600.62 -> £3,381,914.33 (10.3%); £3,771,600.82 -> £3,381,914.50 (10.3%); £3,771,601.01 -> £3,381,914.66 (10.3%); £3,771,601.27 -> £3,381,914.80 (10.3%); £3,771,601.52 -> £3,381,914.95 (10.3%); £3,771,601.77 -> £3,381,915.09 (10.3%); £3,771,602.04 -> £3,381,915.23 (10.3%); £3,771,602.31 -> £3,381,915.37 (10.3%); £3,771,602.57 -> £3,381,915.49 (10.3%); £3,771,602.83 -> £3,381,915.62 (10.3%); £3,771,603.08 -> £3,381,915.66 (10.3%); £3,771,603.34 -> £3,381,915.70 (10.3%); £3,771,603.58 -> £3,381,915.74 (10.3%); £3,771,603.80 -> £3,381,915.78 (10.3%); £3,771,604.00 -> £3,381,915.82 (10.3%); £3,771,604.16 -> £3,381,915.85 (10.3%); £3,771,604.31 -> £3,381,915.89 (10.3%); £3,771,604.47 -> £3,381,915.93 (10.3%); £3,771,604.62 -> £3,381,915.97 (10.3%); £3,771,604.78 -> £3,381,916.00 (10.3%); £3,771,604.93 -> £3,381,916.04 (10.3%); £3,771,605.09 -> £3,381,916.08 (10.3%); £3,771,605.26 -> £3,381,916.12 (10.3%); £3,771,605.42 -> £3,381,916.16 (10.3%); £3,771,605.58 -> £3,381,916.19 (10.3%); £3,771,605.73 -> £3,381,916.23 (10.3%); £3,771,605.89 -> £3,381,916.33 (10.3%); £3,771,606.04 -> £3,381,916.43 (10.3%); £3,771,606.21 -> £3,381,916.54 (10.3%); £3,771,606.40 -> £3,381,916.67 (10.3%); £3,771,606.62 -> £3,381,916.82 (10.3%); £3,771,606.84 -> £3,381,916.99 (10.3%); £3,771,607.09 -> £3,381,917.18 (10.3%); £3,771,607.35 -> £3,381,917.39 (10.3%); £3,771,607.62 -> £3,381,917.51 (10.3%); £3,771,607.88 -> £3,381,917.64 (10.3%); £3,771,608.15 -> £3,381,917.77 (10.3%); £3,771,608.41 -> £3,381,917.90 (10.3%); £3,771,608.67 -> £3,381,918.03 (10.3%); £3,771,608.93 -> £3,381,918.16 (10.3%); £3,771,609.19 -> £3,381,918.28 (10.3%); £3,771,609.46 -> £3,381,918.39 (10.3%); £3,771,609.72 -> £3,381,918.51 (10.3%); £3,771,609.97 -> £3,381,918.63 (10.3%); £3,771,610.22 -> £3,381,918.74 (10.3%); £3,771,610.49 -> £3,381,918.85 (10.3%); £3,771,610.75 -> £3,381,918.96 (10.3%); £3,771,611.00 -> £3,381,919.16 (10.3%); £3,771,611.27 -> £3,381,919.35 (10.3%); £3,771,611.53 -> £3,381,919.50 (10.3%); £3,771,611.78 -> £3,381,919.64 (10.3%); £3,771,612.05 -> £3,381,919.76 (10.3%); £3,771,612.31 -> £3,381,919.88 (10.3%); £3,771,612.58 -> £3,381,920.00 (10.3%); £3,771,612.83 -> £3,381,920.12 (10.3%); £3,771,613.09 -> £3,381,920.23 (10.3%); £3,771,613.34 -> £3,381,920.33 (10.3%); £3,771,613.60 -> £3,381,920.43 (10.3%); £3,771,613.85 -> £3,381,920.47 (10.3%); £3,771,614.11 -> £3,381,920.51 (10.3%); £3,771,614.35 -> £3,381,920.55 (10.3%); £3,771,614.57 -> £3,381,920.59 (10.3%); £3,771,614.78 -> £3,381,920.62 (10.3%); £3,771,614.93 -> £3,381,920.66 (10.3%); £3,771,615.09 -> £3,381,920.70 (10.3%); £3,771,615.24 -> £3,381,920.73 (10.3%); £3,771,615.40 -> £3,381,920.77 (10.3%); £3,771,615.56 -> £3,381,920.81 (10.3%); £3,771,615.72 -> £3,381,920.85 (10.3%); £3,771,615.88 -> £3,381,920.88 (10.3%); £3,771,616.03 -> £3,381,920.92 (10.3%); £3,771,616.19 -> £3,381,920.96 (10.3%); £3,771,616.36 -> £3,381,921.00 (10.3%); £3,771,616.51 -> £3,381,921.04 (10.3%); £3,771,616.67 -> £3,381,921.18 (10.3%); £3,771,616.83 -> £3,381,921.32 (10.3%); £3,771,617.01 -> £3,381,921.47 (10.3%); £3,771,617.20 -> £3,381,921.64 (10.3%); £3,771,617.42 -> £3,381,921.83 (10.3%); £3,771,617.64 -> £3,381,922.03 (10.3%); £3,771,617.89 -> £3,381,922.26 (10.3%); £3,771,618.16 -> £3,381,922.49 (10.3%); £3,771,618.42 -> £3,381,922.62 (10.3%); £3,771,618.69 -> £3,381,922.75 (10.3%); £3,771,618.94 -> £3,381,922.88 (10.3%); £3,771,619.19 -> £3,381,923.01 (10.3%); £3,771,619.46 -> £3,381,923.13 (10.3%); £3,771,619.72 -> £3,381,923.25 (10.3%); £3,771,619.97 -> £3,381,923.37 (10.3%); £3,771,620.23 -> £3,381,923.48 (10.3%); £3,771,620.49 -> £3,381,923.59 (10.3%); £3,771,620.75 -> £3,381,923.71 (10.3%); £3,771,621.01 -> £3,381,923.82 (10.3%); £3,771,621.28 -> £3,381,923.93 (10.3%); £3,771,621.53 -> £3,381,924.03 (10.3%); £3,771,621.73 -> £3,381,924.27 (10.3%); £3,771,622.01 -> £3,381,924.49 (10.3%); £3,771,622.20 -> £3,381,924.67 (10.3%); £3,771,622.39 -> £3,381,924.83 (10.3%); £3,771,622.59 -> £3,381,924.99 (10.3%); £3,771,622.78 -> £3,381,925.14 (10.3%); £3,771,622.97 -> £3,381,925.29 (10.3%); £3,771,623.23 -> £3,381,925.43 (10.3%); £3,771,623.49 -> £3,381,925.57 (10.3%); £3,771,623.75 -> £3,381,925.72 (10.3%); £3,771,624.02 -> £3,381,925.85 (10.3%); £3,771,624.29 -> £3,381,925.90 (10.3%); £3,771,624.56 -> £3,381,925.94 (10.3%); £3,771,624.80 -> £3,381,925.98 (10.3%); £3,771,625.02 -> £3,381,926.01 (10.3%); £3,771,625.22 -> £3,381,926.05 (10.3%); £3,771,625.35 -> £3,381,926.09 (10.3%); £3,771,625.50 -> £3,381,926.13 (10.3%); £3,771,625.63 -> £3,381,926.16 (10.3%); £3,771,625.77 -> £3,381,926.20 (10.3%); £3,771,625.91 -> £3,381,926.24 (10.3%); £3,771,626.05 -> £3,381,926.28 (10.3%); £3,771,626.18 -> £3,381,926.31 (10.3%); £3,771,626.33 -> £3,381,926.35 (10.3%); £3,771,626.46 -> £3,381,926.39 (10.3%); £3,771,626.60 -> £3,381,926.43 (10.3%); £3,771,626.73 -> £3,381,926.47 (10.3%); £3,771,626.87 -> £3,381,926.58 (10.3%); £3,771,627.01 -> £3,381,926.70 (10.3%); £3,771,627.17 -> £3,381,926.83 (10.3%); £3,771,627.34 -> £3,381,926.95 (10.3%); £3,771,627.52 -> £3,381,927.09 (10.3%); £3,771,627.72 -> £3,381,927.23 (10.3%); £3,771,627.93 -> £3,381,927.41 (10.3%); £3,771,628.15 -> £3,381,927.59 (10.3%); £3,771,628.38 -> £3,381,927.68 (10.3%); £3,771,628.60 -> £3,381,927.77 (10.3%); £3,771,628.82 -> £3,381,927.87 (10.3%); £3,771,629.05 -> £3,381,927.96 (10.3%); £3,771,629.29 -> £3,381,928.04 (10.3%); £3,771,629.52 -> £3,381,928.12 (10.3%); £3,771,629.75 -> £3,381,928.20 (10.3%); £3,771,629.97 -> £3,381,928.27 (10.3%); £3,771,630.19 -> £3,381,928.34 (10.3%); £3,771,630.42 -> £3,381,928.41 (10.3%); £3,771,630.65 -> £3,381,928.48 (10.3%); £3,771,630.88 -> £3,381,928.55 (10.3%); £3,771,631.10 -> £3,381,928.61 (10.3%); £3,771,631.27 -> £3,381,928.77 (10.3%); £3,771,631.45 -> £3,381,928.92 (10.3%); £3,771,631.62 -> £3,381,929.06 (10.3%); £3,771,631.79 -> £3,381,929.19 (10.3%); £3,771,631.96 -> £3,381,929.32 (10.3%); £3,771,632.14 -> £3,381,929.45 (10.3%); £3,771,632.30 -> £3,381,929.58 (10.3%); £3,771,632.53 -> £3,381,929.70 (10.3%); £3,771,632.76 -> £3,381,929.83 (10.3%); £3,771,632.99 -> £3,381,929.96 (10.3%); £3,771,633.22 -> £3,381,930.08 (10.3%); £3,771,633.44 -> £3,381,930.12 (10.3%); £3,771,633.68 -> £3,381,930.16 (10.3%); £3,771,633.89 -> £3,381,930.20 (10.3%); £3,771,634.08 -> £3,381,930.23 (10.3%); £3,771,634.25 -> £3,381,930.27 (10.3%); £3,771,634.39 -> £3,381,930.31 (10.3%); £3,771,634.53 -> £3,381,930.35 (10.3%); £3,771,634.67 -> £3,381,930.39 (10.3%); £3,771,634.81 -> £3,381,930.42 (10.3%); £3,771,634.95 -> £3,381,930.46 (10.3%); £3,771,635.08 -> £3,381,930.50 (10.3%); £3,771,635.22 -> £3,381,930.53 (10.3%); £3,771,635.36 -> £3,381,930.57 (10.3%); £3,771,635.50 -> £3,381,930.60 (10.3%); £3,771,635.64 -> £3,381,930.64 (10.3%); £3,771,635.77 -> £3,381,930.68 (10.3%); £3,771,635.91 -> £3,381,930.79 (10.3%); £3,771,636.05 -> £3,381,930.91 (10.3%); £3,771,636.21 -> £3,381,931.02 (10.3%); £3,771,636.37 -> £3,381,931.14 (10.3%); £3,771,636.56 -> £3,381,931.26 (10.3%); £3,771,636.75 -> £3,381,931.38 (10.3%); £3,771,636.97 -> £3,381,931.50 (10.3%); £3,771,637.20 -> £3,381,931.63 (10.3%); £3,771,637.43 -> £3,381,931.68 (10.3%); £3,771,637.66 -> £3,381,931.72 (10.3%); £3,771,637.89 -> £3,381,931.77 (10.3%); £3,771,638.12 -> £3,381,931.82 (10.3%); £3,771,638.35 -> £3,381,931.87 (10.3%); £3,771,638.57 -> £3,381,931.92 (10.3%); £3,771,638.81 -> £3,381,931.97 (10.3%); £3,771,639.03 -> £3,381,932.02 (10.3%); £3,771,639.26 -> £3,381,932.06 (10.3%); £3,771,639.49 -> £3,381,932.11 (10.3%); £3,771,639.73 -> £3,381,932.16 (10.3%); £3,771,639.96 -> £3,381,932.20 (10.3%); £3,771,640.18 -> £3,381,932.25 (10.3%); £3,771,640.42 -> £3,381,932.38 (10.3%); £3,771,640.66 -> £3,381,932.51 (10.3%); £3,771,640.89 -> £3,381,932.64 (10.3%); £3,771,641.05 -> £3,381,932.77 (10.3%); £3,771,641.28 -> £3,381,932.90 (10.3%); £3,771,641.45 -> £3,381,933.03 (10.3%); £3,771,641.62 -> £3,381,933.16 (10.3%); £3,771,641.85 -> £3,381,933.29 (10.3%); £3,771,642.09 -> £3,381,933.41 (10.3%); £3,771,642.31 -> £3,381,933.54 (10.3%); £3,771,642.54 -> £3,381,933.66 (10.3%); £3,771,642.76 -> £3,381,933.70 (10.3%); £3,771,642.99 -> £3,381,933.74 (10.3%); £3,771,643.20 -> £3,381,933.78 (10.3%); £3,771,643.39 -> £3,381,933.82 (10.3%); £3,771,643.57 -> £3,381,933.85 (10.3%); £3,771,643.73 -> £3,381,933.89 (10.3%); £3,771,643.89 -> £3,381,933.93 (10.3%); £3,771,644.05 -> £3,381,933.97 (10.3%); £3,771,644.21 -> £3,381,934.01 (10.3%); £3,771,644.37 -> £3,381,934.05 (10.3%); £3,771,644.53 -> £3,381,934.09 (10.3%); £3,771,644.69 -> £3,381,934.12 (10.3%); £3,771,644.85 -> £3,381,934.16 (10.3%); £3,771,645.01 -> £3,381,934.20 (10.3%); £3,771,645.16 -> £3,381,934.24 (10.3%); £3,771,645.33 -> £3,381,934.28 (10.3%); £3,771,645.49 -> £3,381,934.44 (10.3%); £3,771,645.65 -> £3,381,934.60 (10.3%); £3,771,645.82 -> £3,381,934.77 (10.3%); £3,771,646.01 -> £3,381,934.96 (10.3%); £3,771,646.22 -> £3,381,935.16 (10.3%); £3,771,646.45 -> £3,381,935.39 (10.3%); £3,771,646.70 -> £3,381,935.63 (10.3%); £3,771,646.96 -> £3,381,935.89 (10.3%); £3,771,647.21 -> £3,381,936.02 (10.3%); £3,771,647.48 -> £3,381,936.15 (10.3%); £3,771,647.74 -> £3,381,936.27 (10.3%); £3,771,648.01 -> £3,381,936.41 (10.3%); £3,771,648.28 -> £3,381,936.54 (10.3%); £3,771,648.54 -> £3,381,936.66 (10.3%); £3,771,648.81 -> £3,381,936.77 (10.3%); £3,771,649.07 -> £3,381,936.89 (10.3%); £3,771,649.35 -> £3,381,937.01 (10.3%); £3,771,649.61 -> £3,381,937.13 (10.3%); £3,771,649.87 -> £3,381,937.25 (10.3%); £3,771,650.13 -> £3,381,937.36 (10.3%); £3,771,650.39 -> £3,381,937.47 (10.3%); £3,771,650.65 -> £3,381,937.72 (10.3%); £3,771,650.85 -> £3,381,937.96 (10.3%); £3,771,651.04 -> £3,381,938.16 (10.3%); £3,771,651.24 -> £3,381,938.35 (10.3%); £3,771,651.50 -> £3,381,938.53 (10.3%); £3,771,651.75 -> £3,381,938.71 (10.3%); £3,771,652.02 -> £3,381,938.88 (10.3%); £3,771,652.29 -> £3,381,939.05 (10.3%); £3,771,652.55 -> £3,381,939.22 (10.3%); £3,771,652.82 -> £3,381,939.38 (10.3%); £3,771,653.08 -> £3,381,939.54 (10.3%); £3,771,653.35 -> £3,381,939.58 (10.3%); £3,771,653.62 -> £3,381,939.62 (10.3%); £3,771,653.87 -> £3,381,939.66 (10.3%); £3,771,654.09 -> £3,381,939.70 (10.3%); £3,771,654.29 -> £3,381,939.73 (10.3%); £3,771,654.45 -> £3,381,939.77 (10.3%); £3,771,654.61 -> £3,381,939.81 (10.3%); £3,771,654.77 -> £3,381,939.85 (10.3%); £3,771,654.93 -> £3,381,939.88 (10.3%); £3,771,655.09 -> £3,381,939.92 (10.3%); £3,771,655.25 -> £3,381,939.96 (10.3%); £3,771,655.41 -> £3,381,940.00 (10.3%); £3,771,655.56 -> £3,381,940.04 (10.3%); £3,771,655.72 -> £3,381,940.07 (10.3%); £3,771,655.88 -> £3,381,940.11 (10.3%); £3,771,656.04 -> £3,381,940.15 (10.3%); £3,771,656.19 -> £3,381,940.30 (10.3%); £3,771,656.35 -> £3,381,940.45 (10.3%); £3,771,656.53 -> £3,381,940.61 (10.3%); £3,771,656.72 -> £3,381,940.79 (10.3%); £3,771,656.93 -> £3,381,940.99 (10.3%); £3,771,657.16 -> £3,381,941.21 (10.3%); £3,771,657.41 -> £3,381,941.45 (10.3%); £3,771,657.67 -> £3,381,941.71 (10.3%); £3,771,657.94 -> £3,381,941.83 (10.3%); £3,771,658.20 -> £3,381,941.96 (10.3%); £3,771,658.48 -> £3,381,942.09 (10.3%); £3,771,658.74 -> £3,381,942.22 (10.3%); £3,771,659.00 -> £3,381,942.35 (10.3%); £3,771,659.26 -> £3,381,942.48 (10.3%); £3,771,659.53 -> £3,381,942.60 (10.3%); £3,771,659.79 -> £3,381,942.73 (10.3%); £3,771,660.05 -> £3,381,942.85 (10.3%); £3,771,660.31 -> £3,381,942.97 (10.3%); £3,771,660.58 -> £3,381,943.09 (10.3%); £3,771,660.85 -> £3,381,943.20 (10.3%); £3,771,661.11 -> £3,381,943.31 (10.3%); £3,771,661.38 -> £3,381,943.57 (10.3%); £3,771,661.64 -> £3,381,943.80 (10.3%); £3,771,661.91 -> £3,381,944.01 (10.3%); £3,771,662.17 -> £3,381,944.19 (10.3%); £3,771,662.43 -> £3,381,944.37 (10.3%); £3,771,662.71 -> £3,381,944.53 (10.3%); £3,771,662.90 -> £3,381,944.69 (10.3%); £3,771,663.16 -> £3,381,944.86 (10.3%); £3,771,663.41 -> £3,381,945.01 (10.3%); £3,771,663.68 -> £3,381,945.17 (10.3%); £3,771,663.95 -> £3,381,945.32 (10.3%); £3,771,664.21 -> £3,381,945.36 (10.3%); £3,771,664.47 -> £3,381,945.40 (10.3%); £3,771,664.72 -> £3,381,945.44 (10.3%); £3,771,664.94 -> £3,381,945.48 (10.3%); £3,771,665.14 -> £3,381,945.52 (10.3%); £3,771,665.31 -> £3,381,945.55 (10.3%); £3,771,665.47 -> £3,381,945.59 (10.3%); £3,771,665.63 -> £3,381,945.63 (10.3%); £3,771,665.80 -> £3,381,945.67 (10.3%); £3,771,665.96 -> £3,381,945.71 (10.3%); £3,771,666.12 -> £3,381,945.74 (10.3%); £3,771,666.28 -> £3,381,945.78 (10.3%); £3,771,666.44 -> £3,381,945.82 (10.3%); £3,771,666.59 -> £3,381,945.86 (10.3%); £3,771,666.76 -> £3,381,945.90 (10.3%); £3,771,666.92 -> £3,381,945.94 (10.3%); £3,771,667.08 -> £3,381,946.09 (10.3%); £3,771,667.24 -> £3,381,946.23 (10.3%); £3,771,667.42 -> £3,381,946.39 (10.3%); £3,771,667.62 -> £3,381,946.56 (10.3%); £3,771,667.83 -> £3,381,946.75 (10.3%); £3,771,668.05 -> £3,381,946.96 (10.3%); £3,771,668.30 -> £3,381,947.20 (10.3%); £3,771,668.58 -> £3,381,947.44 (10.3%); £3,771,668.85 -> £3,381,947.57 (10.3%); £3,771,669.11 -> £3,381,947.70 (10.3%); £3,771,669.38 -> £3,381,947.82 (10.3%); £3,771,669.64 -> £3,381,947.95 (10.3%); £3,771,669.91 -> £3,381,948.08 (10.3%); £3,771,670.17 -> £3,381,948.20 (10.3%); £3,771,670.44 -> £3,381,948.32 (10.3%); £3,771,670.71 -> £3,381,948.43 (10.3%); £3,771,670.98 -> £3,381,948.55 (10.3%); £3,771,671.24 -> £3,381,948.67 (10.3%); £3,771,671.51 -> £3,381,948.79 (10.3%); £3,771,671.78 -> £3,381,948.90 (10.3%); £3,771,672.05 -> £3,381,949.01 (10.3%); £3,771,672.31 -> £3,381,949.25 (10.3%); £3,771,672.58 -> £3,381,949.47 (10.3%); £3,771,672.84 -> £3,381,949.66 (10.3%); £3,771,673.11 -> £3,381,949.83 (10.3%); £3,771,673.31 -> £3,381,949.99 (10.3%); £3,771,673.51 -> £3,381,950.15 (10.3%); £3,771,673.78 -> £3,381,950.31 (10.3%); £3,771,674.04 -> £3,381,950.47 (10.3%); £3,771,674.30 -> £3,381,950.62 (10.3%); £3,771,674.57 -> £3,381,950.76 (10.3%); £3,771,674.85 -> £3,381,950.92 (10.3%); £3,771,675.11 -> £3,381,950.96 (10.3%); £3,771,675.38 -> £3,381,951.00 (10.3%); £3,771,675.63 -> £3,381,951.04 (10.3%); £3,771,675.85 -> £3,381,951.08 (10.3%); £3,771,676.06 -> £3,381,951.12 (10.3%); £3,771,676.21 -> £3,381,951.16 (10.3%); £3,771,676.37 -> £3,381,951.19 (10.3%); £3,771,676.53 -> £3,381,951.23 (10.3%); £3,771,676.69 -> £3,381,951.27 (10.3%); £3,771,676.85 -> £3,381,951.31 (10.3%); £3,771,677.01 -> £3,381,951.35 (10.3%); £3,771,677.18 -> £3,381,951.38 (10.3%); £3,771,677.34 -> £3,381,951.42 (10.3%); £3,771,677.50 -> £3,381,951.46 (10.3%); £3,771,677.66 -> £3,381,951.50 (10.3%); £3,771,677.82 -> £3,381,951.54 (10.3%); £3,771,677.98 -> £3,381,951.72 (10.3%); £3,771,678.14 -> £3,381,951.91 (10.3%); £3,771,678.32 -> £3,381,952.10 (10.3%); £3,771,678.52 -> £3,381,952.30 (10.3%); £3,771,678.73 -> £3,381,952.53 (10.3%); £3,771,678.97 -> £3,381,952.78 (10.3%); £3,771,679.22 -> £3,381,953.04 (10.3%); £3,771,679.49 -> £3,381,953.32 (10.3%); £3,771,679.75 -> £3,381,953.44 (10.3%); £3,771,680.02 -> £3,381,953.57 (10.3%); £3,771,680.29 -> £3,381,953.69 (10.3%); £3,771,680.55 -> £3,381,953.81 (10.3%); £3,771,680.81 -> £3,381,953.94 (10.3%); £3,771,681.08 -> £3,381,954.06 (10.3%); £3,771,681.36 -> £3,381,954.17 (10.3%); £3,771,681.63 -> £3,381,954.28 (10.3%); £3,771,681.89 -> £3,381,954.39 (10.3%); £3,771,682.16 -> £3,381,954.51 (10.3%); £3,771,682.42 -> £3,381,954.62 (10.3%); £3,771,682.69 -> £3,381,954.73 (10.3%); £3,771,682.96 -> £3,381,954.84 (10.3%); £3,771,683.23 -> £3,381,955.12 (10.3%); £3,771,683.50 -> £3,381,955.39 (10.3%); £3,771,683.77 -> £3,381,955.63 (10.3%); £3,771,684.04 -> £3,381,955.83 (10.3%); £3,771,684.24 -> £3,381,956.04 (10.3%); £3,771,684.51 -> £3,381,956.24 (10.3%); £3,771,684.79 -> £3,381,956.44 (10.3%); £3,771,685.05 -> £3,381,956.63 (10.3%); £3,771,685.33 -> £3,381,956.82 (10.3%); £3,771,685.60 -> £3,381,957.00 (10.3%); £3,771,685.86 -> £3,381,957.17 (10.3%); £3,771,686.13 -> £3,381,957.22 (10.3%); £3,771,686.40 -> £3,381,957.26 (10.3%); £3,771,686.64 -> £3,381,957.30 (10.3%); £3,771,686.86 -> £3,381,957.34 (10.3%); £3,771,687.07 -> £3,381,957.37 (10.3%); £3,771,687.23 -> £3,381,957.41 (10.3%); £3,771,687.39 -> £3,381,957.45 (10.3%); £3,771,687.56 -> £3,381,957.48 (10.3%); £3,771,687.71 -> £3,381,957.52 (10.3%); £3,771,687.87 -> £3,381,957.56 (10.3%); £3,771,688.03 -> £3,381,957.60 (10.3%); £3,771,688.19 -> £3,381,957.63 (10.3%); £3,771,688.35 -> £3,381,957.67 (10.3%); £3,771,688.52 -> £3,381,957.71 (10.3%); £3,771,688.68 -> £3,381,957.75 (10.3%); £3,771,688.84 -> £3,381,957.79 (10.3%); £3,771,689.00 -> £3,381,958.01 (10.3%); £3,771,689.15 -> £3,381,958.24 (10.3%); £3,771,689.33 -> £3,381,958.49 (10.3%); £3,771,689.53 -> £3,381,958.75 (10.3%); £3,771,689.74 -> £3,381,959.02 (10.3%); £3,771,689.97 -> £3,381,959.32 (10.3%); £3,771,690.22 -> £3,381,959.65 (10.3%); £3,771,690.50 -> £3,381,959.98 (10.3%); £3,771,690.76 -> £3,381,960.11 (10.3%); £3,771,691.02 -> £3,381,960.24 (10.3%); £3,771,691.27 -> £3,381,960.36 (10.3%); £3,771,691.53 -> £3,381,960.49 (10.3%); £3,771,691.79 -> £3,381,960.62 (10.3%); £3,771,692.06 -> £3,381,960.74 (10.3%); £3,771,692.32 -> £3,381,960.85 (10.3%); £3,771,692.60 -> £3,381,960.97 (10.3%); £3,771,692.87 -> £3,381,961.09 (10.3%); £3,771,693.13 -> £3,381,961.21 (10.3%); £3,771,693.39 -> £3,381,961.32 (10.3%); £3,771,693.66 -> £3,381,961.44 (10.3%); £3,771,693.92 -> £3,381,961.55 (10.3%); £3,771,694.19 -> £3,381,961.87 (10.3%); £3,771,694.44 -> £3,381,962.16 (10.3%); £3,771,694.64 -> £3,381,962.43 (10.3%); £3,771,694.85 -> £3,381,962.67 (10.3%); £3,771,695.04 -> £3,381,962.91 (10.3%); £3,771,695.24 -> £3,381,963.14 (10.3%); £3,771,695.45 -> £3,381,963.37 (10.3%); £3,771,695.71 -> £3,381,963.59 (10.3%); £3,771,695.97 -> £3,381,963.81 (10.3%); £3,771,696.25 -> £3,381,964.03 (10.3%); £3,771,696.51 -> £3,381,964.24 (10.3%); £3,771,696.78 -> £3,381,964.28 (10.3%); £3,771,697.04 -> £3,381,964.33 (10.3%); £3,771,697.28 -> £3,381,964.37 (10.3%); £3,771,697.50 -> £3,381,964.40 (10.3%); £3,771,697.70 -> £3,381,964.44 (10.3%); £3,771,697.84 -> £3,381,964.48 (10.3%); £3,771,697.98 -> £3,381,964.51 (10.3%); £3,771,698.13 -> £3,381,964.55 (10.3%); £3,771,698.27 -> £3,381,964.59 (10.3%); £3,771,698.41 -> £3,381,964.62 (10.3%); £3,771,698.55 -> £3,381,964.66 (10.3%); £3,771,698.69 -> £3,381,964.70 (10.3%); £3,771,698.83 -> £3,381,964.73 (10.3%); £3,771,698.97 -> £3,381,964.77 (10.3%); £3,771,699.11 -> £3,381,964.81 (10.3%); £3,771,699.25 -> £3,381,964.85 (10.3%); £3,771,699.39 -> £3,381,965.08 (10.3%); £3,771,699.53 -> £3,381,965.32 (10.3%); £3,771,699.69 -> £3,381,965.56 (10.3%); £3,771,699.86 -> £3,381,965.80 (10.3%); £3,771,700.05 -> £3,381,966.05 (10.3%); £3,771,700.25 -> £3,381,966.31 (10.3%); £3,771,700.48 -> £3,381,966.59 (10.3%); £3,771,700.71 -> £3,381,966.88 (10.3%); £3,771,700.95 -> £3,381,966.97 (10.3%); £3,771,701.18 -> £3,381,967.06 (10.3%); £3,771,701.42 -> £3,381,967.15 (10.3%); £3,771,701.65 -> £3,381,967.25 (10.3%); £3,771,701.88 -> £3,381,967.33 (10.3%); £3,771,702.12 -> £3,381,967.41 (10.3%); £3,771,702.35 -> £3,381,967.48 (10.3%); £3,771,702.58 -> £3,381,967.56 (10.3%); £3,771,702.82 -> £3,381,967.63 (10.3%); £3,771,703.05 -> £3,381,967.70 (10.3%); £3,771,703.29 -> £3,381,967.77 (10.3%); £3,771,703.54 -> £3,381,967.84 (10.3%); £3,771,703.77 -> £3,381,967.90 (10.3%); £3,771,703.95 -> £3,381,968.16 (10.3%); £3,771,704.12 -> £3,381,968.41 (10.3%); £3,771,704.30 -> £3,381,968.65 (10.3%); £3,771,704.47 -> £3,381,968.88 (10.3%); £3,771,704.65 -> £3,381,969.11 (10.3%); £3,771,704.82 -> £3,381,969.34 (10.3%); £3,771,705.00 -> £3,381,969.57 (10.3%); £3,771,705.24 -> £3,381,969.79 (10.3%); £3,771,705.48 -> £3,381,970.02 (10.3%); £3,771,705.71 -> £3,381,970.24 (10.3%); £3,771,705.95 -> £3,381,970.46 (10.3%); £3,771,706.19 -> £3,381,970.50 (10.3%); £3,771,706.42 -> £3,381,970.54 (10.3%); £3,771,706.63 -> £3,381,970.58 (10.3%); £3,771,706.83 -> £3,381,970.62 (10.3%); £3,771,707.02 -> £3,381,970.66 (10.3%); £3,771,707.16 -> £3,381,970.69 (10.3%); £3,771,707.31 -> £3,381,970.73 (10.3%); £3,771,707.44 -> £3,381,970.77 (10.3%); £3,771,707.59 -> £3,381,970.81 (10.3%); £3,771,707.72 -> £3,381,970.84 (10.3%); £3,771,707.86 -> £3,381,970.88 (10.3%); £3,771,708.00 -> £3,381,970.92 (10.3%); £3,771,708.14 -> £3,381,970.95 (10.3%); £3,771,708.28 -> £3,381,970.99 (10.3%); £3,771,708.42 -> £3,381,971.02 (10.3%); £3,771,708.56 -> £3,381,971.06 (10.3%); £3,771,708.70 -> £3,381,971.27 (10.3%); £3,771,708.84 -> £3,381,971.48 (10.3%); £3,771,708.99 -> £3,381,971.70 (10.3%); £3,771,709.17 -> £3,381,971.91 (10.3%); £3,771,709.36 -> £3,381,972.13 (10.3%); £3,771,709.56 -> £3,381,972.35 (10.3%); £3,771,709.77 -> £3,381,972.57 (10.3%); £3,771,710.01 -> £3,381,972.80 (10.3%); £3,771,710.25 -> £3,381,972.85 (10.3%); £3,771,710.49 -> £3,381,972.90 (10.3%); £3,771,710.73 -> £3,381,972.95 (10.3%); £3,771,710.95 -> £3,381,973.00 (10.3%); £3,771,711.19 -> £3,381,973.05 (10.3%); £3,771,711.42 -> £3,381,973.09 (10.3%); £3,771,711.65 -> £3,381,973.14 (10.3%); £3,771,711.90 -> £3,381,973.19 (10.3%); £3,771,712.13 -> £3,381,973.23 (10.3%); £3,771,712.36 -> £3,381,973.28 (10.3%); £3,771,712.59 -> £3,381,973.32 (10.3%); £3,771,712.83 -> £3,381,973.37 (10.3%); £3,771,713.06 -> £3,381,973.41 (10.3%); £3,771,713.24 -> £3,381,973.63 (10.3%); £3,771,713.41 -> £3,381,973.84 (10.3%); £3,771,713.59 -> £3,381,974.05 (10.3%); £3,771,713.77 -> £3,381,974.26 (10.3%); £3,771,714.00 -> £3,381,974.49 (10.3%); £3,771,714.23 -> £3,381,974.70 (10.3%); £3,771,714.41 -> £3,381,974.92 (10.3%); £3,771,714.65 -> £3,381,975.13 (10.3%); £3,771,714.88 -> £3,381,975.35 (10.3%); £3,771,715.11 -> £3,381,975.56 (10.3%); £3,771,715.34 -> £3,381,975.78 (10.3%); £3,771,715.57 -> £3,381,975.82 (10.3%); £3,771,715.81 -> £3,381,975.86 (10.3%); £3,771,716.02 -> £3,381,975.89 (10.3%); £3,771,716.22 -> £3,381,975.93 (10.3%); £3,771,716.40 -> £3,381,975.97 (10.3%); £3,771,716.56 -> £3,381,976.00 (10.3%); £3,771,716.72 -> £3,381,976.04 (10.3%); £3,771,716.88 -> £3,381,976.08 (10.3%); £3,771,717.03 -> £3,381,976.12 (10.3%); £3,771,717.20 -> £3,381,976.16 (10.3%); £3,771,717.36 -> £3,381,976.19 (10.3%); £3,771,717.51 -> £3,381,976.23 (10.3%); £3,771,717.68 -> £3,381,976.27 (10.3%); £3,771,717.84 -> £3,381,976.31 (10.3%); £3,771,718.00 -> £3,381,976.35 (10.3%); £3,771,718.16 -> £3,381,976.39 (10.3%); £3,771,718.32 -> £3,381,976.59 (10.3%); £3,771,718.48 -> £3,381,976.80 (10.3%); £3,771,718.65 -> £3,381,977.01 (10.3%); £3,771,718.84 -> £3,381,977.24 (10.3%); £3,771,719.07 -> £3,381,977.50 (10.3%); £3,771,719.29 -> £3,381,977.77 (10.3%); £3,771,719.53 -> £3,381,978.07 (10.3%); £3,771,719.80 -> £3,381,978.37 (10.3%); £3,771,720.06 -> £3,381,978.49 (10.3%); £3,771,720.32 -> £3,381,978.62 (10.3%); £3,771,720.59 -> £3,381,978.74 (10.3%); £3,771,720.86 -> £3,381,978.87 (10.3%); £3,771,721.13 -> £3,381,979.00 (10.3%); £3,771,721.38 -> £3,381,979.12 (10.3%); £3,771,721.64 -> £3,381,979.24 (10.3%); £3,771,721.91 -> £3,381,979.36 (10.3%); £3,771,722.18 -> £3,381,979.48 (10.3%); £3,771,722.44 -> £3,381,979.60 (10.3%); £3,771,722.71 -> £3,381,979.71 (10.3%); £3,771,722.97 -> £3,381,979.83 (10.3%); £3,771,723.23 -> £3,381,979.94 (10.3%); £3,771,723.49 -> £3,381,980.24 (10.3%); £3,771,723.77 -> £3,381,980.53 (10.3%); £3,771,724.03 -> £3,381,980.78 (10.3%); £3,771,724.29 -> £3,381,981.01 (10.3%); £3,771,724.55 -> £3,381,981.23 (10.3%); £3,771,724.80 -> £3,381,981.44 (10.3%); £3,771,725.01 -> £3,381,981.66 (10.3%); £3,771,725.27 -> £3,381,981.87 (10.3%); £3,771,725.53 -> £3,381,982.08 (10.3%); £3,771,725.78 -> £3,381,982.28 (10.3%); £3,771,726.04 -> £3,381,982.48 (10.3%); £3,771,726.30 -> £3,381,982.52 (10.3%); £3,771,726.56 -> £3,381,982.56 (10.3%); £3,771,726.81 -> £3,381,982.60 (10.3%); £3,771,727.03 -> £3,381,982.64 (10.3%); £3,771,727.24 -> £3,381,982.68 (10.3%); £3,771,727.40 -> £3,381,982.72 (10.3%); £3,771,727.55 -> £3,381,982.75 (10.3%); £3,771,727.71 -> £3,381,982.79 (10.3%); £3,771,727.87 -> £3,381,982.83 (10.3%); £3,771,728.03 -> £3,381,982.87 (10.3%); £3,771,728.18 -> £3,381,982.90 (10.3%); £3,771,728.34 -> £3,381,982.94 (10.3%); £3,771,728.50 -> £3,381,982.98 (10.3%); £3,771,728.66 -> £3,381,983.02 (10.3%); £3,771,728.81 -> £3,381,983.06 (10.3%); £3,771,728.96 -> £3,381,983.10 (10.3%); £3,771,729.12 -> £3,381,983.33 (10.3%); £3,771,729.28 -> £3,381,983.56 (10.3%); £3,771,729.46 -> £3,381,983.81 (10.3%); £3,771,729.64 -> £3,381,984.06 (10.3%); £3,771,729.85 -> £3,381,984.34 (10.3%); £3,771,730.09 -> £3,381,984.64 (10.3%); £3,771,730.34 -> £3,381,984.96 (10.3%); £3,771,730.59 -> £3,381,985.29 (10.3%); £3,771,730.85 -> £3,381,985.41 (10.3%); £3,771,731.11 -> £3,381,985.54 (10.3%); £3,771,731.36 -> £3,381,985.67 (10.3%); £3,771,731.62 -> £3,381,985.80 (10.3%); £3,771,731.88 -> £3,381,985.93 (10.3%); £3,771,732.14 -> £3,381,986.06 (10.3%); £3,771,732.40 -> £3,381,986.18 (10.3%); £3,771,732.67 -> £3,381,986.30 (10.3%); £3,771,732.92 -> £3,381,986.42 (10.3%); £3,771,733.19 -> £3,381,986.54 (10.3%); £3,771,733.44 -> £3,381,986.65 (10.3%); £3,771,733.70 -> £3,381,986.76 (10.3%); £3,771,733.97 -> £3,381,986.87 (10.3%); £3,771,734.24 -> £3,381,987.19 (10.3%); £3,771,734.50 -> £3,381,987.48 (10.3%); £3,771,734.68 -> £3,381,987.75 (10.3%); £3,771,734.89 -> £3,381,987.99 (10.3%); £3,771,735.09 -> £3,381,988.23 (10.3%); £3,771,735.28 -> £3,381,988.47 (10.3%); £3,771,735.54 -> £3,381,988.70 (10.3%); £3,771,735.80 -> £3,381,988.93 (10.3%); £3,771,736.07 -> £3,381,989.15 (10.3%); £3,771,736.33 -> £3,381,989.38 (10.3%); £3,771,736.59 -> £3,381,989.60 (10.3%); £3,771,736.85 -> £3,381,989.65 (10.3%); £3,771,737.12 -> £3,381,989.69 (10.3%); £3,771,737.36 -> £3,381,989.73 (10.3%); £3,771,737.59 -> £3,381,989.76 (10.3%); £3,771,737.79 -> £3,381,989.80 (10.3%); £3,771,737.95 -> £3,381,989.84 (10.3%); £3,771,738.11 -> £3,381,989.88 (10.3%); £3,771,738.26 -> £3,381,989.91 (10.3%); £3,771,738.42 -> £3,381,989.95 (10.3%); £3,771,738.57 -> £3,381,989.99 (10.3%); £3,771,738.73 -> £3,381,990.02 (10.3%); £3,771,738.89 -> £3,381,990.06 (10.3%); £3,771,739.05 -> £3,381,990.10 (10.3%); £3,771,739.21 -> £3,381,990.14 (10.3%); £3,771,739.36 -> £3,381,990.18 (10.3%); £3,771,739.52 -> £3,381,990.22 (10.3%); £3,771,739.68 -> £3,381,990.40 (10.3%); £3,771,739.83 -> £3,381,990.58 (10.3%); £3,771,740.01 -> £3,381,990.78 (10.3%); £3,771,740.21 -> £3,381,990.99 (10.3%); £3,771,740.41 -> £3,381,991.22 (10.3%); £3,771,740.64 -> £3,381,991.47 (10.3%); £3,771,740.88 -> £3,381,991.75 (10.3%); £3,771,741.13 -> £3,381,992.04 (10.3%); £3,771,741.39 -> £3,381,992.17 (10.3%); £3,771,741.65 -> £3,381,992.30 (10.3%); £3,771,741.90 -> £3,381,992.43 (10.3%); £3,771,742.17 -> £3,381,992.56 (10.3%); £3,771,742.43 -> £3,381,992.69 (10.3%); £3,771,742.69 -> £3,381,992.81 (10.3%); £3,771,742.96 -> £3,381,992.93 (10.3%); £3,771,743.22 -> £3,381,993.05 (10.3%); £3,771,743.48 -> £3,381,993.17 (10.3%); £3,771,743.75 -> £3,381,993.28 (10.3%); £3,771,744.01 -> £3,381,993.39 (10.3%); £3,771,744.27 -> £3,381,993.51 (10.3%); £3,771,744.53 -> £3,381,993.61 (10.3%); £3,771,744.73 -> £3,381,993.90 (10.3%); £3,771,744.99 -> £3,381,994.16 (10.3%); £3,771,745.19 -> £3,381,994.39 (10.3%); £3,771,745.39 -> £3,381,994.60 (10.3%); £3,771,745.66 -> £3,381,994.80 (10.3%); £3,771,745.92 -> £3,381,995.00 (10.3%); £3,771,746.11 -> £3,381,995.20 (10.3%); £3,771,746.37 -> £3,381,995.39 (10.3%); £3,771,746.63 -> £3,381,995.57 (10.3%); £3,771,746.90 -> £3,381,995.76 (10.3%); £3,771,747.16 -> £3,381,995.94 (10.3%); £3,771,747.43 -> £3,381,995.98 (10.3%); £3,771,747.70 -> £3,381,996.02 (10.3%); £3,771,747.94 -> £3,381,996.06 (10.3%); £3,771,748.17 -> £3,381,996.10 (10.3%); £3,771,748.37 -> £3,381,996.13 (10.3%); £3,771,748.53 -> £3,381,996.17 (10.3%); £3,771,748.68 -> £3,381,996.21 (10.3%); £3,771,748.83 -> £3,381,996.25 (10.3%); £3,771,748.99 -> £3,381,996.28 (10.3%); £3,771,749.14 -> £3,381,996.32 (10.3%); £3,771,749.30 -> £3,381,996.36 (10.3%); £3,771,749.45 -> £3,381,996.39 (10.3%); £3,771,749.61 -> £3,381,996.43 (10.3%); £3,771,749.76 -> £3,381,996.47 (10.3%); £3,771,749.92 -> £3,381,996.51 (10.3%); £3,771,750.07 -> £3,381,996.55 (10.3%); £3,771,750.23 -> £3,381,996.72 (10.3%); £3,771,750.38 -> £3,381,996.90 (10.3%); £3,771,750.55 -> £3,381,997.08 (10.3%); £3,771,750.74 -> £3,381,997.27 (10.3%); £3,771,750.94 -> £3,381,997.48 (10.3%); £3,771,751.17 -> £3,381,997.71 (10.3%); £3,771,751.41 -> £3,381,997.96 (10.3%); £3,771,751.67 -> £3,381,998.23 (10.3%); £3,771,751.93 -> £3,381,998.35 (10.3%); £3,771,752.19 -> £3,381,998.48 (10.3%); £3,771,752.45 -> £3,381,998.60 (10.3%); £3,771,752.70 -> £3,381,998.73 (10.3%); £3,771,752.96 -> £3,381,998.85 (10.3%); £3,771,753.21 -> £3,381,998.98 (10.3%); £3,771,753.47 -> £3,381,999.09 (10.3%); £3,771,753.73 -> £3,381,999.21 (10.3%); £3,771,753.99 -> £3,381,999.32 (10.3%); £3,771,754.25 -> £3,381,999.44 (10.3%); £3,771,754.50 -> £3,381,999.56 (10.3%); £3,771,754.74 -> £3,381,999.67 (10.3%); £3,771,755.01 -> £3,381,999.78 (10.3%); £3,771,755.26 -> £3,382,000.05 (10.3%); £3,771,755.52 -> £3,382,000.29 (10.3%); £3,771,755.77 -> £3,382,000.50 (10.3%); £3,771,755.97 -> £3,382,000.69 (10.3%); £3,771,756.16 -> £3,382,000.87 (10.3%); £3,771,756.42 -> £3,382,001.05 (10.3%); £3,771,756.62 -> £3,382,001.22 (10.3%); £3,771,756.87 -> £3,382,001.39 (10.3%); £3,771,757.12 -> £3,382,001.55 (10.3%); £3,771,757.39 -> £3,382,001.71 (10.3%); £3,771,757.64 -> £3,382,001.87 (10.3%); £3,771,757.91 -> £3,382,001.91 (10.3%); £3,771,758.17 -> £3,382,001.95 (10.3%); £3,771,758.41 -> £3,382,001.99 (10.3%); £3,771,758.63 -> £3,382,002.03 (10.3%); £3,771,758.83 -> £3,382,002.07 (10.3%); £3,771,758.99 -> £3,382,002.11 (10.3%); £3,771,759.14 -> £3,382,002.14 (10.3%); £3,771,759.30 -> £3,382,002.18 (10.3%); £3,771,759.45 -> £3,382,002.22 (10.3%); £3,771,759.61 -> £3,382,002.25 (10.3%); £3,771,759.77 -> £3,382,002.29 (10.3%); £3,771,759.93 -> £3,382,002.33 (10.3%); £3,771,760.08 -> £3,382,002.37 (10.3%); £3,771,760.24 -> £3,382,002.41 (10.3%); £3,771,760.39 -> £3,382,002.44 (10.3%); £3,771,760.54 -> £3,382,002.49 (10.3%); £3,771,760.70 -> £3,382,002.71 (10.3%); £3,771,760.85 -> £3,382,002.93 (10.3%); £3,771,761.03 -> £3,382,003.17 (10.3%); £3,771,761.21 -> £3,382,003.42 (10.3%); £3,771,761.41 -> £3,382,003.69 (10.3%); £3,771,761.64 -> £3,382,003.98 (10.3%); £3,771,761.87 -> £3,382,004.30 (10.3%); £3,771,762.13 -> £3,382,004.63 (10.3%); £3,771,762.39 -> £3,382,004.75 (10.3%); £3,771,762.65 -> £3,382,004.88 (10.3%); £3,771,762.91 -> £3,382,005.00 (10.3%); £3,771,763.17 -> £3,382,005.13 (10.3%); £3,771,763.44 -> £3,382,005.26 (10.3%); £3,771,763.70 -> £3,382,005.38 (10.3%); £3,771,763.96 -> £3,382,005.49 (10.3%); £3,771,764.22 -> £3,382,005.60 (10.3%); £3,771,764.48 -> £3,382,005.72 (10.3%); £3,771,764.75 -> £3,382,005.84 (10.3%); £3,771,765.01 -> £3,382,005.96 (10.3%); £3,771,765.27 -> £3,382,006.07 (10.3%); £3,771,765.53 -> £3,382,006.17 (10.3%); £3,771,765.78 -> £3,382,006.48 (10.3%); £3,771,766.04 -> £3,382,006.78 (10.3%); £3,771,766.30 -> £3,382,007.04 (10.3%); £3,771,766.57 -> £3,382,007.28 (10.3%); £3,771,766.84 -> £3,382,007.52 (10.3%); £3,771,767.10 -> £3,382,007.75 (10.3%); £3,771,767.36 -> £3,382,008.00 (10.3%); £3,771,767.62 -> £3,382,008.22 (10.3%); £3,771,767.89 -> £3,382,008.45 (10.3%); £3,771,768.15 -> £3,382,008.68 (10.3%); £3,771,768.41 -> £3,382,008.89 (10.3%); £3,771,768.68 -> £3,382,008.93 (10.3%); £3,771,768.94 -> £3,382,008.97 (10.3%); £3,771,769.18 -> £3,382,009.01 (10.3%); £3,771,769.40 -> £3,382,009.05 (10.3%); £3,771,769.60 -> £3,382,009.08 (10.3%); £3,771,769.74 -> £3,382,009.12 (10.3%); £3,771,769.87 -> £3,382,009.16 (10.3%); £3,771,770.00 -> £3,382,009.20 (10.3%); £3,771,770.14 -> £3,382,009.23 (10.3%); £3,771,770.28 -> £3,382,009.27 (10.3%); £3,771,770.41 -> £3,382,009.31 (10.3%); £3,771,770.55 -> £3,382,009.34 (10.3%); £3,771,770.68 -> £3,382,009.38 (10.3%); £3,771,770.82 -> £3,382,009.42 (10.3%); £3,771,770.96 -> £3,382,009.46 (10.3%); £3,771,771.10 -> £3,382,009.49 (10.3%); £3,771,771.23 -> £3,382,009.73 (10.3%); £3,771,771.37 -> £3,382,009.96 (10.3%); £3,771,771.53 -> £3,382,010.20 (10.3%); £3,771,771.69 -> £3,382,010.44 (10.3%); £3,771,771.87 -> £3,382,010.68 (10.3%); £3,771,772.07 -> £3,382,010.94 (10.3%); £3,771,772.28 -> £3,382,011.21 (10.3%); £3,771,772.51 -> £3,382,011.49 (10.3%); £3,771,772.74 -> £3,382,011.58 (10.3%); £3,771,772.96 -> £3,382,011.67 (10.3%); £3,771,773.18 -> £3,382,011.76 (10.3%); £3,771,773.40 -> £3,382,011.85 (10.3%); £3,771,773.63 -> £3,382,011.93 (10.3%); £3,771,773.85 -> £3,382,012.01 (10.3%); £3,771,774.08 -> £3,382,012.09 (10.3%); £3,771,774.31 -> £3,382,012.16 (10.3%); £3,771,774.55 -> £3,382,012.24 (10.3%); £3,771,774.78 -> £3,382,012.31 (10.3%); £3,771,775.00 -> £3,382,012.38 (10.3%); £3,771,775.23 -> £3,382,012.45 (10.3%); £3,771,775.46 -> £3,382,012.52 (10.3%); £3,771,775.68 -> £3,382,012.78 (10.3%); £3,771,775.91 -> £3,382,013.03 (10.3%); £3,771,776.13 -> £3,382,013.27 (10.3%); £3,771,776.36 -> £3,382,013.50 (10.3%); £3,771,776.58 -> £3,382,013.73 (10.3%); £3,771,776.81 -> £3,382,013.97 (10.3%); £3,771,777.04 -> £3,382,014.20 (10.3%); £3,771,777.27 -> £3,382,014.43 (10.3%); £3,771,777.50 -> £3,382,014.66 (10.3%); £3,771,777.72 -> £3,382,014.89 (10.3%); £3,771,777.95 -> £3,382,015.12 (10.3%); £3,771,778.18 -> £3,382,015.16 (10.3%); £3,771,778.39 -> £3,382,015.20 (10.3%); £3,771,778.61 -> £3,382,015.24 (10.3%); £3,771,778.80 -> £3,382,015.28 (10.3%); £3,771,778.98 -> £3,382,015.31 (10.3%); £3,771,779.11 -> £3,382,015.35 (10.3%); £3,771,779.25 -> £3,382,015.39 (10.3%); £3,771,779.38 -> £3,382,015.43 (10.3%); £3,771,779.51 -> £3,382,015.46 (10.3%); £3,771,779.65 -> £3,382,015.50 (10.3%); £3,771,779.79 -> £3,382,015.53 (10.3%); £3,771,779.92 -> £3,382,015.57 (10.3%); £3,771,780.05 -> £3,382,015.61 (10.3%); £3,771,780.19 -> £3,382,015.64 (10.3%); £3,771,780.33 -> £3,382,015.68 (10.3%); £3,771,780.46 -> £3,382,015.71 (10.3%); £3,771,780.60 -> £3,382,015.93 (10.3%); £3,771,780.74 -> £3,382,016.14 (10.3%); £3,771,780.89 -> £3,382,016.36 (10.3%); £3,771,781.05 -> £3,382,016.58 (10.3%); £3,771,781.23 -> £3,382,016.80 (10.3%); £3,771,781.43 -> £3,382,017.03 (10.3%); £3,771,781.64 -> £3,382,017.26 (10.3%); £3,771,781.86 -> £3,382,017.48 (10.3%); £3,771,782.09 -> £3,382,017.53 (10.3%); £3,771,782.32 -> £3,382,017.58 (10.3%); £3,771,782.55 -> £3,382,017.63 (10.3%); £3,771,782.77 -> £3,382,017.68 (10.3%); £3,771,782.98 -> £3,382,017.73 (10.3%); £3,771,783.21 -> £3,382,017.78 (10.3%); £3,771,783.44 -> £3,382,017.83 (10.3%); £3,771,783.67 -> £3,382,017.88 (10.3%); £3,771,783.89 -> £3,382,017.92 (10.3%); £3,771,784.12 -> £3,382,017.97 (10.3%); £3,771,784.34 -> £3,382,018.01 (10.3%); £3,771,784.57 -> £3,382,018.06 (10.3%); £3,771,784.81 -> £3,382,018.11 (10.3%); £3,771,785.04 -> £3,382,018.32 (10.3%); £3,771,785.26 -> £3,382,018.55 (10.3%); £3,771,785.49 -> £3,382,018.76 (10.3%); £3,771,785.72 -> £3,382,018.98 (10.3%); £3,771,785.94 -> £3,382,019.20 (10.3%); £3,771,786.16 -> £3,382,019.43 (10.3%); £3,771,786.39 -> £3,382,019.65 (10.3%); £3,771,786.60 -> £3,382,019.87 (10.3%); £3,771,786.83 -> £3,382,020.09 (10.3%); £3,771,787.06 -> £3,382,020.31 (10.3%); £3,771,787.30 -> £3,382,020.52 (10.3%); £3,771,787.52 -> £3,382,020.56 (10.3%); £3,771,787.75 -> £3,382,020.60 (10.3%); £3,771,787.96 -> £3,382,020.64 (10.3%); £3,771,788.15 -> £3,382,020.68 (10.3%); £3,771,788.33 -> £3,382,020.71 (10.3%); £3,771,788.48 -> £3,382,020.75 (10.3%); £3,771,788.64 -> £3,382,020.79 (10.3%); £3,771,788.79 -> £3,382,020.83 (10.3%); £3,771,788.95 -> £3,382,020.86 (10.3%); £3,771,789.10 -> £3,382,020.90 (10.3%); £3,771,789.26 -> £3,382,020.94 (10.3%); £3,771,789.41 -> £3,382,020.97 (10.3%); £3,771,789.57 -> £3,382,021.01 (10.3%); £3,771,789.72 -> £3,382,021.05 (10.3%); £3,771,789.87 -> £3,382,021.09 (10.3%); £3,771,790.03 -> £3,382,021.13 (10.3%); £3,771,790.19 -> £3,382,021.33 (10.3%); £3,771,790.34 -> £3,382,021.54 (10.3%); £3,771,790.51 -> £3,382,021.75 (10.3%); £3,771,790.70 -> £3,382,021.99 (10.3%); £3,771,790.90 -> £3,382,022.24 (10.3%); £3,771,791.13 -> £3,382,022.52 (10.3%); £3,771,791.37 -> £3,382,022.82 (10.3%); £3,771,791.63 -> £3,382,023.14 (10.3%); £3,771,791.89 -> £3,382,023.27 (10.3%); £3,771,792.15 -> £3,382,023.40 (10.3%); £3,771,792.42 -> £3,382,023.53 (10.3%); £3,771,792.67 -> £3,382,023.66 (10.3%); £3,771,792.93 -> £3,382,023.79 (10.3%); £3,771,793.19 -> £3,382,023.91 (10.3%); £3,771,793.45 -> £3,382,024.03 (10.3%); £3,771,793.71 -> £3,382,024.14 (10.3%); £3,771,793.97 -> £3,382,024.26 (10.3%); £3,771,794.23 -> £3,382,024.38 (10.3%); £3,771,794.48 -> £3,382,024.49 (10.3%); £3,771,794.75 -> £3,382,024.61 (10.3%); £3,771,795.01 -> £3,382,024.72 (10.3%); £3,771,795.25 -> £3,382,025.02 (10.3%); £3,771,795.51 -> £3,382,025.30 (10.3%); £3,771,795.76 -> £3,382,025.55 (10.3%); £3,771,796.01 -> £3,382,025.78 (10.3%); £3,771,796.27 -> £3,382,026.00 (10.3%); £3,771,796.52 -> £3,382,026.21 (10.3%); £3,771,796.78 -> £3,382,026.43 (10.3%); £3,771,797.04 -> £3,382,026.65 (10.3%); £3,771,797.30 -> £3,382,026.87 (10.3%); £3,771,797.55 -> £3,382,027.07 (10.3%); £3,771,797.82 -> £3,382,027.27 (10.3%); £3,771,798.07 -> £3,382,027.31 (10.3%); £3,771,798.33 -> £3,382,027.35 (10.3%); £3,771,798.57 -> £3,382,027.39 (10.3%); £3,771,798.79 -> £3,382,027.43 (10.3%); £3,771,798.99 -> £3,382,027.46 (10.3%); £3,771,799.14 -> £3,382,027.50 (10.3%); £3,771,799.29 -> £3,382,027.54 (10.3%); £3,771,799.45 -> £3,382,027.58 (10.3%); £3,771,799.61 -> £3,382,027.62 (10.3%); £3,771,799.76 -> £3,382,027.65 (10.3%); £3,771,799.92 -> £3,382,027.69 (10.3%); £3,771,800.06 -> £3,382,027.73 (10.3%); £3,771,800.21 -> £3,382,027.77 (10.3%); £3,771,800.36 -> £3,382,027.80 (10.3%); £3,771,800.51 -> £3,382,027.84 (10.3%); £3,771,800.67 -> £3,382,027.88 (10.3%); £3,771,800.82 -> £3,382,028.06 (10.3%); £3,771,800.98 -> £3,382,028.24 (10.3%); £3,771,801.15 -> £3,382,028.43 (10.3%); £3,771,801.34 -> £3,382,028.63 (10.3%); £3,771,801.54 -> £3,382,028.86 (10.3%); £3,771,801.76 -> £3,382,029.10 (10.3%); £3,771,802.00 -> £3,382,029.37 (10.3%); £3,771,802.26 -> £3,382,029.65 (10.3%); £3,771,802.51 -> £3,382,029.77 (10.3%); £3,771,802.77 -> £3,382,029.90 (10.3%); £3,771,803.03 -> £3,382,030.03 (10.3%); £3,771,803.29 -> £3,382,030.16 (10.3%); £3,771,803.54 -> £3,382,030.29 (10.3%); £3,771,803.79 -> £3,382,030.42 (10.3%); £3,771,804.06 -> £3,382,030.54 (10.3%); £3,771,804.31 -> £3,382,030.66 (10.3%); £3,771,804.56 -> £3,382,030.77 (10.3%); £3,771,804.82 -> £3,382,030.89 (10.3%); £3,771,805.07 -> £3,382,031.00 (10.3%); £3,771,805.34 -> £3,382,031.12 (10.3%); £3,771,805.59 -> £3,382,031.23 (10.3%); £3,771,805.86 -> £3,382,031.50 (10.3%); £3,771,806.12 -> £3,382,031.76 (10.3%); £3,771,806.37 -> £3,382,031.98 (10.3%); £3,771,806.62 -> £3,382,032.18 (10.3%); £3,771,806.88 -> £3,382,032.37 (10.3%); £3,771,807.14 -> £3,382,032.56 (10.3%); £3,771,807.39 -> £3,382,032.75 (10.3%); £3,771,807.65 -> £3,382,032.93 (10.3%); £3,771,807.91 -> £3,382,033.11 (10.3%); £3,771,808.16 -> £3,382,033.29 (10.3%); £3,771,808.42 -> £3,382,033.47 (10.3%); £3,771,808.68 -> £3,382,033.51 (10.3%); £3,771,808.94 -> £3,382,033.55 (10.3%); £3,771,809.18 -> £3,382,033.59 (10.3%); £3,771,809.39 -> £3,382,033.63 (10.3%); £3,771,809.59 -> £3,382,033.66 (10.3%); £3,771,809.74 -> £3,382,033.70 (10.3%); £3,771,809.89 -> £3,382,033.74 (10.3%); £3,771,810.04 -> £3,382,033.77 (10.3%); £3,771,810.18 -> £3,382,033.81 (10.3%); £3,771,810.33 -> £3,382,033.85 (10.3%); £3,771,810.49 -> £3,382,033.88 (10.3%); £3,771,810.64 -> £3,382,033.92 (10.3%); £3,771,810.80 -> £3,382,033.96 (10.3%); £3,771,810.94 -> £3,382,034.00 (10.3%); £3,771,811.10 -> £3,382,034.03 (10.3%); £3,771,811.25 -> £3,382,034.07 (10.3%); £3,771,811.40 -> £3,382,034.27 (10.3%); £3,771,811.56 -> £3,382,034.48 (10.3%); £3,771,811.73 -> £3,382,034.69 (10.3%); £3,771,811.92 -> £3,382,034.92 (10.3%); £3,771,812.13 -> £3,382,035.17 (10.3%); £3,771,812.34 -> £3,382,035.43 (10.3%); £3,771,812.58 -> £3,382,035.73 (10.3%); £3,771,812.83 -> £3,382,036.05 (10.3%); £3,771,813.08 -> £3,382,036.18 (10.3%); £3,771,813.34 -> £3,382,036.30 (10.3%); £3,771,813.59 -> £3,382,036.44 (10.3%); £3,771,813.85 -> £3,382,036.57 (10.3%); £3,771,814.12 -> £3,382,036.69 (10.3%); £3,771,814.38 -> £3,382,036.82 (10.3%); £3,771,814.63 -> £3,382,036.93 (10.3%); £3,771,814.89 -> £3,382,037.05 (10.3%); £3,771,815.16 -> £3,382,037.17 (10.3%); £3,771,815.40 -> £3,382,037.28 (10.3%); £3,771,815.66 -> £3,382,037.40 (10.3%); £3,771,815.91 -> £3,382,037.51 (10.3%); £3,771,816.17 -> £3,382,037.62 (10.3%); £3,771,816.43 -> £3,382,037.93 (10.3%); £3,771,816.69 -> £3,382,038.21 (10.3%); £3,771,816.95 -> £3,382,038.45 (10.3%); £3,771,817.21 -> £3,382,038.67 (10.3%); £3,771,817.46 -> £3,382,038.89 (10.3%); £3,771,817.72 -> £3,382,039.10 (10.3%); £3,771,817.97 -> £3,382,039.32 (10.3%); £3,771,818.23 -> £3,382,039.52 (10.3%); £3,771,818.48 -> £3,382,039.73 (10.3%); £3,771,818.74 -> £3,382,039.94 (10.3%); £3,771,818.99 -> £3,382,040.15 (10.3%); £3,771,819.25 -> £3,382,040.19 (10.3%); £3,771,819.50 -> £3,382,040.23 (10.3%); £3,771,819.74 -> £3,382,040.27 (10.3%); £3,771,819.96 -> £3,382,040.31 (10.3%); £3,771,820.15 -> £3,382,040.34 (10.3%); £3,771,820.31 -> £3,382,040.38 (10.3%); £3,771,820.46 -> £3,382,040.42 (10.3%); £3,771,820.62 -> £3,382,040.46 (10.3%); £3,771,820.76 -> £3,382,040.50 (10.3%); £3,771,820.91 -> £3,382,040.53 (10.3%); £3,771,821.07 -> £3,382,040.57 (10.3%); £3,771,821.22 -> £3,382,040.61 (10.3%); £3,771,821.37 -> £3,382,040.64 (10.3%); £3,771,821.52 -> £3,382,040.68 (10.3%); £3,771,821.68 -> £3,382,040.72 (10.3%); £3,771,821.83 -> £3,382,040.76 (10.3%); £3,771,821.98 -> £3,382,040.95 (10.3%); £3,771,822.13 -> £3,382,041.13 (10.3%); £3,771,822.30 -> £3,382,041.33 (10.3%); £3,771,822.49 -> £3,382,041.54 (10.3%); £3,771,822.69 -> £3,382,041.78 (10.3%); £3,771,822.90 -> £3,382,042.03 (10.3%); £3,771,823.14 -> £3,382,042.31 (10.3%); £3,771,823.41 -> £3,382,042.59 (10.3%); £3,771,823.66 -> £3,382,042.71 (10.3%); £3,771,823.93 -> £3,382,042.83 (10.3%); £3,771,824.18 -> £3,382,042.96 (10.3%); £3,771,824.43 -> £3,382,043.08 (10.3%); £3,771,824.68 -> £3,382,043.21 (10.3%); £3,771,824.93 -> £3,382,043.33 (10.3%); £3,771,825.19 -> £3,382,043.45 (10.3%); £3,771,825.44 -> £3,382,043.56 (10.3%); £3,771,825.70 -> £3,382,043.68 (10.3%); £3,771,825.95 -> £3,382,043.79 (10.3%); £3,771,826.21 -> £3,382,043.90 (10.3%); £3,771,826.47 -> £3,382,044.01 (10.3%); £3,771,826.72 -> £3,382,044.12 (10.3%); £3,771,826.98 -> £3,382,044.40 (10.3%); £3,771,827.24 -> £3,382,044.66 (10.3%); £3,771,827.49 -> £3,382,044.90 (10.3%); £3,771,827.75 -> £3,382,045.12 (10.3%); £3,771,828.00 -> £3,382,045.32 (10.3%); £3,771,828.26 -> £3,382,045.53 (10.3%); £3,771,828.51 -> £3,382,045.73 (10.3%); £3,771,828.76 -> £3,382,045.93 (10.3%); £3,771,829.03 -> £3,382,046.13 (10.3%); £3,771,829.29 -> £3,382,046.32 (10.3%); £3,771,829.54 -> £3,382,046.50 (10.3%); £3,771,829.79 -> £3,382,046.54 (10.3%); £3,771,830.04 -> £3,382,046.58 (10.3%); £3,771,830.28 -> £3,382,046.62 (10.3%); £3,771,830.49 -> £3,382,046.66 (10.3%); £3,771,830.70 -> £3,382,046.70 (10.3%); £3,771,830.84 -> £3,382,046.73 (10.3%); £3,771,831.00 -> £3,382,046.77 (10.3%); £3,771,831.15 -> £3,382,046.81 (10.3%); £3,771,831.30 -> £3,382,046.85 (10.3%); £3,771,831.45 -> £3,382,046.89 (10.3%); £3,771,831.61 -> £3,382,046.92 (10.3%); £3,771,831.76 -> £3,382,046.96 (10.3%); £3,771,831.91 -> £3,382,047.00 (10.3%); £3,771,832.07 -> £3,382,047.04 (10.3%); £3,771,832.22 -> £3,382,047.07 (10.3%); £3,771,832.37 -> £3,382,047.11 (10.3%); £3,771,832.52 -> £3,382,047.31 (10.3%); £3,771,832.68 -> £3,382,047.50 (10.3%); £3,771,832.85 -> £3,382,047.70 (10.3%); £3,771,833.04 -> £3,382,047.92 (10.3%); £3,771,833.24 -> £3,382,048.15 (10.3%); £3,771,833.45 -> £3,382,048.41 (10.3%); £3,771,833.69 -> £3,382,048.69 (10.3%); £3,771,833.96 -> £3,382,048.98 (10.3%); £3,771,834.22 -> £3,382,049.10 (10.3%); £3,771,834.48 -> £3,382,049.23 (10.3%); £3,771,834.73 -> £3,382,049.35 (10.3%); £3,771,834.99 -> £3,382,049.48 (10.3%); £3,771,835.25 -> £3,382,049.60 (10.3%); £3,771,835.50 -> £3,382,049.72 (10.3%); £3,771,835.76 -> £3,382,049.84 (10.3%); £3,771,836.01 -> £3,382,049.96 (10.3%); £3,771,836.26 -> £3,382,050.08 (10.3%); £3,771,836.52 -> £3,382,050.20 (10.3%); £3,771,836.78 -> £3,382,050.31 (10.3%); £3,771,837.03 -> £3,382,050.42 (10.3%); £3,771,837.29 -> £3,382,050.53 (10.3%); £3,771,837.55 -> £3,382,050.81 (10.3%); £3,771,837.79 -> £3,382,051.07 (10.3%); £3,771,838.05 -> £3,382,051.30 (10.3%); £3,771,838.30 -> £3,382,051.51 (10.3%); £3,771,838.56 -> £3,382,051.72 (10.3%); £3,771,838.81 -> £3,382,051.92 (10.3%); £3,771,839.06 -> £3,382,052.11 (10.3%); £3,771,839.32 -> £3,382,052.31 (10.3%); £3,771,839.58 -> £3,382,052.50 (10.3%); £3,771,839.83 -> £3,382,052.68 (10.3%); £3,771,840.07 -> £3,382,052.86 (10.3%); £3,771,840.34 -> £3,382,052.91 (10.3%); £3,771,840.59 -> £3,382,052.95 (10.3%); £3,771,840.83 -> £3,382,052.99 (10.3%); £3,771,841.04 -> £3,382,053.02 (10.3%); £3,771,841.24 -> £3,382,053.06 (10.3%); £3,771,841.37 -> £3,382,053.10 (10.3%); £3,771,841.50 -> £3,382,053.14 (10.3%); £3,771,841.63 -> £3,382,053.17 (10.3%); £3,771,841.77 -> £3,382,053.21 (10.3%); £3,771,841.90 -> £3,382,053.25 (10.3%); £3,771,842.03 -> £3,382,053.28 (10.3%); £3,771,842.17 -> £3,382,053.32 (10.3%); £3,771,842.31 -> £3,382,053.36 (10.3%); £3,771,842.44 -> £3,382,053.40 (10.3%); £3,771,842.57 -> £3,382,053.43 (10.3%); £3,771,842.70 -> £3,382,053.47 (10.3%); £3,771,842.84 -> £3,382,053.64 (10.3%); £3,771,842.98 -> £3,382,053.81 (10.3%); £3,771,843.13 -> £3,382,053.99 (10.3%); £3,771,843.29 -> £3,382,054.17 (10.3%); £3,771,843.47 -> £3,382,054.37 (10.3%); £3,771,843.67 -> £3,382,054.58 (10.3%); £3,771,843.88 -> £3,382,054.80 (10.3%); £3,771,844.10 -> £3,382,055.03 (10.3%); £3,771,844.33 -> £3,382,055.12 (10.3%); £3,771,844.55 -> £3,382,055.21 (10.3%); £3,771,844.77 -> £3,382,055.30 (10.3%); £3,771,844.99 -> £3,382,055.39 (10.3%); £3,771,845.22 -> £3,382,055.47 (10.3%); £3,771,845.45 -> £3,382,055.55 (10.3%); £3,771,845.67 -> £3,382,055.62 (10.3%); £3,771,845.89 -> £3,382,055.69 (10.3%); £3,771,846.12 -> £3,382,055.76 (10.3%); £3,771,846.35 -> £3,382,055.83 (10.3%); £3,771,846.58 -> £3,382,055.90 (10.3%); £3,771,846.81 -> £3,382,055.97 (10.3%); £3,771,847.03 -> £3,382,056.04 (10.3%); £3,771,847.25 -> £3,382,056.25 (10.3%); £3,771,847.48 -> £3,382,056.46 (10.3%); £3,771,847.70 -> £3,382,056.65 (10.3%); £3,771,847.94 -> £3,382,056.83 (10.3%); £3,771,848.16 -> £3,382,057.01 (10.3%); £3,771,848.38 -> £3,382,057.20 (10.3%); £3,771,848.60 -> £3,382,057.38 (10.3%); £3,771,848.83 -> £3,382,057.57 (10.3%); £3,771,849.04 -> £3,382,057.75 (10.3%); £3,771,849.27 -> £3,382,057.93 (10.3%); £3,771,849.49 -> £3,382,058.10 (10.3%); £3,771,849.71 -> £3,382,058.14 (10.3%); £3,771,849.93 -> £3,382,058.18 (10.3%); £3,771,850.14 -> £3,382,058.22 (10.3%); £3,771,850.33 -> £3,382,058.26 (10.3%); £3,771,850.51 -> £3,382,058.29 (10.3%); £3,771,850.64 -> £3,382,058.33 (10.3%); £3,771,850.77 -> £3,382,058.37 (10.3%); £3,771,850.91 -> £3,382,058.41 (10.3%); £3,771,851.04 -> £3,382,058.45 (10.3%); £3,771,851.18 -> £3,382,058.49 (10.3%); £3,771,851.31 -> £3,382,058.52 (10.3%); £3,771,851.45 -> £3,382,058.56 (10.3%); £3,771,851.59 -> £3,382,058.60 (10.3%); £3,771,851.72 -> £3,382,058.64 (10.3%); £3,771,851.86 -> £3,382,058.67 (10.3%); £3,771,851.99 -> £3,382,058.71 (10.3%); £3,771,852.13 -> £3,382,058.87 (10.3%); £3,771,852.26 -> £3,382,059.03 (10.3%); £3,771,852.41 -> £3,382,059.20 (10.3%); £3,771,852.58 -> £3,382,059.36 (10.3%); £3,771,852.76 -> £3,382,059.53 (10.3%); £3,771,852.96 -> £3,382,059.69 (10.3%); £3,771,853.16 -> £3,382,059.86 (10.3%); £3,771,853.38 -> £3,382,060.03 (10.3%); £3,771,853.62 -> £3,382,060.08 (10.3%); £3,771,853.84 -> £3,382,060.13 (10.3%); £3,771,854.07 -> £3,382,060.18 (10.3%); £3,771,854.29 -> £3,382,060.23 (10.3%); £3,771,854.51 -> £3,382,060.27 (10.3%); £3,771,854.74 -> £3,382,060.32 (10.3%); £3,771,854.96 -> £3,382,060.37 (10.3%); £3,771,855.18 -> £3,382,060.41 (10.3%); £3,771,855.40 -> £3,382,060.46 (10.3%); £3,771,855.63 -> £3,382,060.50 (10.3%); £3,771,855.86 -> £3,382,060.55 (10.3%); £3,771,856.08 -> £3,382,060.60 (10.3%); £3,771,856.30 -> £3,382,060.64 (10.3%); £3,771,856.53 -> £3,382,060.82 (10.3%); £3,771,856.75 -> £3,382,061.00 (10.3%); £3,771,856.98 -> £3,382,061.17 (10.3%); £3,771,857.21 -> £3,382,061.34 (10.3%); £3,771,857.43 -> £3,382,061.51 (10.3%); £3,771,857.64 -> £3,382,061.68 (10.3%); £3,771,857.86 -> £3,382,061.85 (10.3%); £3,771,858.07 -> £3,382,062.01 (10.3%); £3,771,858.30 -> £3,382,062.18 (10.3%); £3,771,858.53 -> £3,382,062.34 (10.3%); £3,771,858.75 -> £3,382,062.51 (10.3%); £3,771,858.98 -> £3,382,062.55 (10.3%); £3,771,859.20 -> £3,382,062.59 (10.3%); £3,771,859.41 -> £3,382,062.62 (10.3%); £3,771,859.60 -> £3,382,062.66 (10.3%); £3,771,859.78 -> £3,382,062.69 (10.3%); £3,771,859.93 -> £3,382,062.73 (10.3%); £3,771,860.08 -> £3,382,062.77 (10.3%); £3,771,860.23 -> £3,382,062.81 (10.3%); £3,771,860.39 -> £3,382,062.85 (10.3%); £3,771,860.54 -> £3,382,062.88 (10.3%); £3,771,860.69 -> £3,382,062.92 (10.3%); £3,771,860.84 -> £3,382,062.96 (10.3%); £3,771,860.99 -> £3,382,063.00 (10.3%); £3,771,861.15 -> £3,382,063.03 (10.3%); £3,771,861.30 -> £3,382,063.07 (10.3%); £3,771,861.45 -> £3,382,063.11 (10.3%); £3,771,861.59 -> £3,382,063.29 (10.3%); £3,771,861.74 -> £3,382,063.48 (10.3%); £3,771,861.91 -> £3,382,063.67 (10.3%); £3,771,862.10 -> £3,382,063.86 (10.3%); £3,771,862.31 -> £3,382,064.08 (10.3%); £3,771,862.53 -> £3,382,064.32 (10.3%); £3,771,862.77 -> £3,382,064.58 (10.3%); £3,771,863.02 -> £3,382,064.85 (10.3%); £3,771,863.27 -> £3,382,064.97 (10.3%); £3,771,863.52 -> £3,382,065.10 (10.3%); £3,771,863.78 -> £3,382,065.22 (10.3%); £3,771,864.04 -> £3,382,065.34 (10.3%); £3,771,864.28 -> £3,382,065.47 (10.3%); £3,771,864.55 -> £3,382,065.59 (10.3%); £3,771,864.79 -> £3,382,065.70 (10.3%); £3,771,865.04 -> £3,382,065.81 (10.3%); £3,771,865.29 -> £3,382,065.93 (10.3%); £3,771,865.55 -> £3,382,066.04 (10.3%); £3,771,865.80 -> £3,382,066.15 (10.3%); £3,771,866.06 -> £3,382,066.25 (10.3%); £3,771,866.31 -> £3,382,066.36 (10.3%); £3,771,866.56 -> £3,382,066.61 (10.3%); £3,771,866.81 -> £3,382,066.85 (10.3%); £3,771,867.07 -> £3,382,067.06 (10.3%); £3,771,867.33 -> £3,382,067.25 (10.3%); £3,771,867.58 -> £3,382,067.43 (10.3%); £3,771,867.84 -> £3,382,067.63 (10.3%); £3,771,868.08 -> £3,382,067.82 (10.3%); £3,771,868.33 -> £3,382,068.01 (10.3%); £3,771,868.58 -> £3,382,068.20 (10.3%); £3,771,868.84 -> £3,382,068.37 (10.3%); £3,771,869.10 -> £3,382,068.54 (10.3%); £3,771,869.35 -> £3,382,068.58 (10.3%); £3,771,869.61 -> £3,382,068.63 (10.3%); £3,771,869.83 -> £3,382,068.67 (10.3%); £3,771,870.05 -> £3,382,068.70 (10.3%); £3,771,870.24 -> £3,382,068.74 (10.3%); £3,771,870.39 -> £3,382,068.78 (10.3%); £3,771,870.54 -> £3,382,068.82 (10.3%); £3,771,870.69 -> £3,382,068.85 (10.3%); £3,771,870.84 -> £3,382,068.89 (10.3%); £3,771,870.99 -> £3,382,068.93 (10.3%); £3,771,871.14 -> £3,382,068.96 (10.3%); £3,771,871.29 -> £3,382,069.00 (10.3%); £3,771,871.44 -> £3,382,069.04 (10.3%); £3,771,871.59 -> £3,382,069.08 (10.3%); £3,771,871.74 -> £3,382,069.12 (10.3%); £3,771,871.89 -> £3,382,069.16 (10.3%); £3,771,872.03 -> £3,382,069.29 (10.3%); £3,771,872.19 -> £3,382,069.44 (10.3%); £3,771,872.36 -> £3,382,069.60 (10.3%); £3,771,872.55 -> £3,382,069.77 (10.3%); £3,771,872.75 -> £3,382,069.97 (10.3%); £3,771,872.96 -> £3,382,070.18 (10.3%); £3,771,873.20 -> £3,382,070.42 (10.3%); £3,771,873.45 -> £3,382,070.66 (10.3%); £3,771,873.70 -> £3,382,070.78 (10.3%); £3,771,873.95 -> £3,382,070.91 (10.3%); £3,771,874.20 -> £3,382,071.04 (10.3%); £3,771,874.46 -> £3,382,071.17 (10.3%); £3,771,874.71 -> £3,382,071.29 (10.3%); £3,771,874.96 -> £3,382,071.42 (10.3%); £3,771,875.21 -> £3,382,071.54 (10.3%); £3,771,875.46 -> £3,382,071.66 (10.3%); £3,771,875.71 -> £3,382,071.77 (10.3%); £3,771,875.96 -> £3,382,071.88 (10.3%); £3,771,876.22 -> £3,382,071.99 (10.3%); £3,771,876.47 -> £3,382,072.10 (10.3%); £3,771,876.73 -> £3,382,072.21 (10.3%); £3,771,876.98 -> £3,382,072.45 (10.3%); £3,771,877.24 -> £3,382,072.67 (10.3%); £3,771,877.49 -> £3,382,072.86 (10.3%); £3,771,877.75 -> £3,382,073.02 (10.3%); £3,771,878.01 -> £3,382,073.19 (10.3%); £3,771,878.27 -> £3,382,073.35 (10.3%); £3,771,878.52 -> £3,382,073.51 (10.3%); £3,771,878.77 -> £3,382,073.66 (10.3%); £3,771,879.01 -> £3,382,073.81 (10.3%); £3,771,879.25 -> £3,382,073.95 (10.3%); £3,771,879.50 -> £3,382,074.09 (10.3%); £3,771,879.75 -> £3,382,074.13 (10.3%); £3,771,880.00 -> £3,382,074.17 (10.3%); £3,771,880.24 -> £3,382,074.21 (10.3%); £3,771,880.46 -> £3,382,074.25 (10.3%); £3,771,880.65 -> £3,382,074.28 (10.3%); £3,771,880.80 -> £3,382,074.32 (10.3%); £3,771,880.95 -> £3,382,074.36 (10.3%); £3,771,881.11 -> £3,382,074.40 (10.3%); £3,771,881.26 -> £3,382,074.44 (10.3%); £3,771,881.41 -> £3,382,074.47 (10.3%); £3,771,881.56 -> £3,382,074.51 (10.3%); £3,771,881.71 -> £3,382,074.55 (10.3%); £3,771,881.86 -> £3,382,074.59 (10.3%); £3,771,882.01 -> £3,382,074.62 (10.3%); £3,771,882.16 -> £3,382,074.66 (10.3%); £3,771,882.32 -> £3,382,074.70 (10.3%); £3,771,882.47 -> £3,382,074.81 (10.3%); £3,771,882.62 -> £3,382,074.92 (10.3%); £3,771,882.79 -> £3,382,075.05 (10.3%); £3,771,882.97 -> £3,382,075.18 (10.3%); £3,771,883.16 -> £3,382,075.35 (10.3%); £3,771,883.38 -> £3,382,075.54 (10.3%); £3,771,883.62 -> £3,382,075.74 (10.3%); £3,771,883.87 -> £3,382,075.96 (10.3%); £3,771,884.12 -> £3,382,076.09 (10.3%); £3,771,884.37 -> £3,382,076.22 (10.3%); £3,771,884.63 -> £3,382,076.35 (10.3%); £3,771,884.88 -> £3,382,076.47 (10.3%); £3,771,885.13 -> £3,382,076.60 (10.3%); £3,771,885.38 -> £3,382,076.72 (10.3%); £3,771,885.63 -> £3,382,076.84 (10.3%); £3,771,885.89 -> £3,382,076.96 (10.3%); £3,771,886.14 -> £3,382,077.08 (10.3%); £3,771,886.38 -> £3,382,077.19 (10.3%); £3,771,886.63 -> £3,382,077.31 (10.3%); £3,771,886.88 -> £3,382,077.43 (10.3%); £3,771,887.12 -> £3,382,077.53 (10.3%); £3,771,887.37 -> £3,382,077.74 (10.3%); £3,771,887.63 -> £3,382,077.93 (10.3%); £3,771,887.87 -> £3,382,078.09 (10.3%); £3,771,888.12 -> £3,382,078.24 (10.3%); £3,771,888.37 -> £3,382,078.37 (10.3%); £3,771,888.61 -> £3,382,078.50 (10.3%); £3,771,888.86 -> £3,382,078.63 (10.3%); £3,771,889.12 -> £3,382,078.75 (10.3%); £3,771,889.36 -> £3,382,078.88 (10.3%); £3,771,889.61 -> £3,382,078.99 (10.3%); £3,771,889.85 -> £3,382,079.10 (10.3%); £3,771,890.10 -> £3,382,079.14 (10.3%); £3,771,890.36 -> £3,382,079.19 (10.3%); £3,771,890.60 -> £3,382,079.23 (10.3%); £3,771,890.81 -> £3,382,079.26 (10.3%); £3,771,891.00 -> £3,382,079.30 (10.3%); £3,771,891.15 -> £3,382,079.34 (10.3%); £3,771,891.30 -> £3,382,079.37 (10.3%); £3,771,891.46 -> £3,382,079.41 (10.3%); £3,771,891.61 -> £3,382,079.45 (10.3%); £3,771,891.76 -> £3,382,079.49 (10.3%); £3,771,891.91 -> £3,382,079.52 (10.3%); £3,771,892.06 -> £3,382,079.56 (10.3%); £3,771,892.21 -> £3,382,079.60 (10.3%); £3,771,892.36 -> £3,382,079.64 (10.3%); £3,771,892.52 -> £3,382,079.68 (10.3%); £3,771,892.67 -> £3,382,079.72 (10.3%); £3,771,892.82 -> £3,382,079.82 (10.3%); £3,771,892.96 -> £3,382,079.93 (10.3%); £3,771,893.13 -> £3,382,080.06 (10.3%); £3,771,893.31 -> £3,382,080.19 (10.3%); £3,771,893.51 -> £3,382,080.35 (10.3%); £3,771,893.73 -> £3,382,080.53 (10.3%); £3,771,893.96 -> £3,382,080.72 (10.3%); £3,771,894.21 -> £3,382,080.94 (10.3%); £3,771,894.47 -> £3,382,081.07 (10.3%); £3,771,894.72 -> £3,382,081.19 (10.3%); £3,771,894.97 -> £3,382,081.31 (10.3%); £3,771,895.22 -> £3,382,081.44 (10.3%); £3,771,895.47 -> £3,382,081.56 (10.3%); £3,771,895.73 -> £3,382,081.68 (10.3%); £3,771,895.98 -> £3,382,081.80 (10.3%); £3,771,896.23 -> £3,382,081.91 (10.3%); £3,771,896.48 -> £3,382,082.03 (10.3%); £3,771,896.73 -> £3,382,082.14 (10.3%); £3,771,896.98 -> £3,382,082.26 (10.3%); £3,771,897.24 -> £3,382,082.37 (10.3%); £3,771,897.50 -> £3,382,082.47 (10.3%); £3,771,897.75 -> £3,382,082.67 (10.3%); £3,771,898.01 -> £3,382,082.85 (10.3%); £3,771,898.26 -> £3,382,083.01 (10.3%); £3,771,898.52 -> £3,382,083.15 (10.3%); £3,771,898.78 -> £3,382,083.29 (10.3%); £3,771,899.03 -> £3,382,083.41 (10.3%); £3,771,899.27 -> £3,382,083.54 (10.3%); £3,771,899.53 -> £3,382,083.66 (10.3%); £3,771,899.78 -> £3,382,083.78 (10.3%); £3,771,900.03 -> £3,382,083.89 (10.3%); £3,771,900.28 -> £3,382,084.00 (10.3%); £3,771,900.53 -> £3,382,084.04 (10.3%); £3,771,900.79 -> £3,382,084.09 (10.3%); £3,771,901.01 -> £3,382,084.12 (10.3%); £3,771,901.23 -> £3,382,084.16 (10.3%); £3,771,901.43 -> £3,382,084.20 (10.3%); £3,771,901.58 -> £3,382,084.24 (10.3%); £3,771,901.73 -> £3,382,084.28 (10.3%); £3,771,901.88 -> £3,382,084.31 (10.3%); £3,771,902.03 -> £3,382,084.35 (10.3%); £3,771,902.18 -> £3,382,084.39 (10.3%); £3,771,902.33 -> £3,382,084.43 (10.3%); £3,771,902.49 -> £3,382,084.47 (10.3%); £3,771,902.64 -> £3,382,084.50 (10.3%); £3,771,902.79 -> £3,382,084.54 (10.3%); £3,771,902.94 -> £3,382,084.58 (10.3%); £3,771,903.09 -> £3,382,084.62 (10.3%); £3,771,903.24 -> £3,382,084.77 (10.3%); £3,771,903.39 -> £3,382,084.92 (10.3%); £3,771,903.56 -> £3,382,085.08 (10.3%); £3,771,903.74 -> £3,382,085.26 (10.3%); £3,771,903.95 -> £3,382,085.46 (10.3%); £3,771,904.17 -> £3,382,085.67 (10.3%); £3,771,904.40 -> £3,382,085.90 (10.3%); £3,771,904.66 -> £3,382,086.14 (10.3%); £3,771,904.92 -> £3,382,086.27 (10.3%); £3,771,905.16 -> £3,382,086.40 (10.3%); £3,771,905.41 -> £3,382,086.53 (10.3%); £3,771,905.66 -> £3,382,086.67 (10.3%); £3,771,905.91 -> £3,382,086.81 (10.3%); £3,771,906.16 -> £3,382,086.93 (10.3%); £3,771,906.41 -> £3,382,087.06 (10.3%); £3,771,906.66 -> £3,382,087.18 (10.3%); £3,771,906.92 -> £3,382,087.30 (10.3%); £3,771,907.17 -> £3,382,087.42 (10.3%); £3,771,907.42 -> £3,382,087.54 (10.3%); £3,771,907.67 -> £3,382,087.65 (10.3%); £3,771,907.92 -> £3,382,087.76 (10.3%); £3,771,908.17 -> £3,382,087.99 (10.3%); £3,771,908.43 -> £3,382,088.21 (10.3%); £3,771,908.68 -> £3,382,088.39 (10.3%); £3,771,908.93 -> £3,382,088.56 (10.3%); £3,771,909.18 -> £3,382,088.72 (10.3%); £3,771,909.43 -> £3,382,088.88 (10.3%); £3,771,909.68 -> £3,382,089.02 (10.3%); £3,771,909.93 -> £3,382,089.17 (10.3%); £3,771,910.19 -> £3,382,089.31 (10.3%); £3,771,910.44 -> £3,382,089.45 (10.3%); £3,771,910.70 -> £3,382,089.59 (10.3%); £3,771,910.95 -> £3,382,089.63 (10.3%); £3,771,911.20 -> £3,382,089.67 (10.3%); £3,771,911.43 -> £3,382,089.71 (10.3%); £3,771,911.64 -> £3,382,089.74 (10.3%); £3,771,911.83 -> £3,382,089.78 (10.3%); £3,771,911.97 -> £3,382,089.82 (10.3%); £3,771,912.10 -> £3,382,089.86 (10.3%); £3,771,912.23 -> £3,382,089.89 (10.3%); £3,771,912.37 -> £3,382,089.93 (10.3%); £3,771,912.51 -> £3,382,089.97 (10.3%); £3,771,912.64 -> £3,382,090.00 (10.3%); £3,771,912.78 -> £3,382,090.04 (10.3%); £3,771,912.92 -> £3,382,090.08 (10.3%); £3,771,913.05 -> £3,382,090.12 (10.3%); £3,771,913.18 -> £3,382,090.15 (10.3%); £3,771,913.32 -> £3,382,090.19 (10.3%); £3,771,913.46 -> £3,382,090.36 (10.3%); £3,771,913.60 -> £3,382,090.53 (10.3%); £3,771,913.74 -> £3,382,090.71 (10.3%); £3,771,913.91 -> £3,382,090.90 (10.3%); £3,771,914.09 -> £3,382,091.09 (10.3%); £3,771,914.29 -> £3,382,091.30 (10.3%); £3,771,914.50 -> £3,382,091.53 (10.3%); £3,771,914.72 -> £3,382,091.76 (10.3%); £3,771,914.95 -> £3,382,091.85 (10.3%); £3,771,915.17 -> £3,382,091.95 (10.3%); £3,771,915.39 -> £3,382,092.04 (10.3%); £3,771,915.62 -> £3,382,092.13 (10.3%); £3,771,915.85 -> £3,382,092.21 (10.3%); £3,771,916.07 -> £3,382,092.29 (10.3%); £3,771,916.29 -> £3,382,092.36 (10.3%); £3,771,916.52 -> £3,382,092.44 (10.3%); £3,771,916.73 -> £3,382,092.51 (10.3%); £3,771,916.95 -> £3,382,092.58 (10.3%); £3,771,917.17 -> £3,382,092.64 (10.3%); £3,771,917.39 -> £3,382,092.71 (10.3%); £3,771,917.60 -> £3,382,092.78 (10.3%); £3,771,917.83 -> £3,382,092.98 (10.3%); £3,771,918.06 -> £3,382,093.18 (10.3%); £3,771,918.28 -> £3,382,093.36 (10.3%); £3,771,918.51 -> £3,382,093.54 (10.3%); £3,771,918.73 -> £3,382,093.72 (10.3%); £3,771,918.97 -> £3,382,093.90 (10.3%); £3,771,919.18 -> £3,382,094.07 (10.3%); £3,771,919.41 -> £3,382,094.25 (10.3%); £3,771,919.63 -> £3,382,094.42 (10.3%); £3,771,919.85 -> £3,382,094.59 (10.3%); £3,771,920.08 -> £3,382,094.78 (10.3%); £3,771,920.30 -> £3,382,094.82 (10.3%); £3,771,920.52 -> £3,382,094.86 (10.3%); £3,771,920.72 -> £3,382,094.90 (10.3%); £3,771,920.91 -> £3,382,094.94 (10.3%); £3,771,921.09 -> £3,382,094.97 (10.3%); £3,771,921.22 -> £3,382,095.01 (10.3%); £3,771,921.36 -> £3,382,095.05 (10.3%); £3,771,921.49 -> £3,382,095.09 (10.3%); £3,771,921.62 -> £3,382,095.13 (10.3%); £3,771,921.76 -> £3,382,095.16 (10.3%); £3,771,921.90 -> £3,382,095.20 (10.3%); £3,771,922.03 -> £3,382,095.24 (10.3%); £3,771,922.16 -> £3,382,095.27 (10.3%); £3,771,922.30 -> £3,382,095.31 (10.3%); £3,771,922.44 -> £3,382,095.35 (10.3%); £3,771,922.58 -> £3,382,095.38 (10.3%); £3,771,922.71 -> £3,382,095.48 (10.3%); £3,771,922.85 -> £3,382,095.58 (10.3%); £3,771,923.00 -> £3,382,095.68 (10.3%); £3,771,923.17 -> £3,382,095.79 (10.3%); £3,771,923.35 -> £3,382,095.89 (10.3%); £3,771,923.55 -> £3,382,095.99 (10.3%); £3,771,923.76 -> £3,382,096.10 (10.3%); £3,771,923.99 -> £3,382,096.21 (10.3%); £3,771,924.22 -> £3,382,096.25 (10.3%); £3,771,924.44 -> £3,382,096.30 (10.3%); £3,771,924.66 -> £3,382,096.35 (10.3%); £3,771,924.89 -> £3,382,096.40 (10.3%); £3,771,925.11 -> £3,382,096.44 (10.3%); £3,771,925.34 -> £3,382,096.49 (10.3%); £3,771,925.57 -> £3,382,096.54 (10.3%); £3,771,925.80 -> £3,382,096.58 (10.3%); £3,771,926.02 -> £3,382,096.63 (10.3%); £3,771,926.25 -> £3,382,096.68 (10.3%); £3,771,926.48 -> £3,382,096.72 (10.3%); £3,771,926.71 -> £3,382,096.77 (10.3%); £3,771,926.94 -> £3,382,096.81 (10.3%); £3,771,927.16 -> £3,382,096.93 (10.3%); £3,771,927.38 -> £3,382,097.04 (10.3%); £3,771,927.61 -> £3,382,097.15 (10.3%); £3,771,927.84 -> £3,382,097.27 (10.3%); £3,771,928.07 -> £3,382,097.38 (10.3%); £3,771,928.29 -> £3,382,097.50 (10.3%); £3,771,928.51 -> £3,382,097.61 (10.3%); £3,771,928.74 -> £3,382,097.72 (10.3%); £3,771,928.96 -> £3,382,097.83 (10.3%); £3,771,929.18 -> £3,382,097.94 (10.3%); £3,771,929.41 -> £3,382,098.05 (10.3%); £3,771,929.64 -> £3,382,098.09 (10.3%); £3,771,929.86 -> £3,382,098.13 (10.3%); £3,771,930.08 -> £3,382,098.16 (10.3%); £3,771,930.28 -> £3,382,098.20 (10.3%); £3,771,930.45 -> £3,382,098.24 (10.3%); £3,771,930.61 -> £3,382,098.27 (10.3%); £3,771,930.76 -> £3,382,098.31 (10.3%); £3,771,930.92 -> £3,382,098.35 (10.3%); £3,771,931.07 -> £3,382,098.38 (10.3%); £3,771,931.22 -> £3,382,098.42 (10.3%); £3,771,931.37 -> £3,382,098.46 (10.3%); £3,771,931.53 -> £3,382,098.50 (10.3%); £3,771,931.68 -> £3,382,098.53 (10.3%); £3,771,931.83 -> £3,382,098.57 (10.3%); £3,771,931.98 -> £3,382,098.61 (10.3%); £3,771,932.14 -> £3,382,098.65 (10.3%); £3,771,932.29 -> £3,382,098.79 (10.3%); £3,771,932.45 -> £3,382,098.92 (10.3%); £3,771,932.62 -> £3,382,099.06 (10.3%); £3,771,932.81 -> £3,382,099.21 (10.3%); £3,771,933.01 -> £3,382,099.40 (10.3%); £3,771,933.24 -> £3,382,099.60 (10.3%); £3,771,933.48 -> £3,382,099.83 (10.3%); £3,771,933.74 -> £3,382,100.08 (10.3%); £3,771,933.99 -> £3,382,100.20 (10.3%); £3,771,934.25 -> £3,382,100.33 (10.3%); £3,771,934.50 -> £3,382,100.45 (10.3%); £3,771,934.75 -> £3,382,100.58 (10.3%); £3,771,935.00 -> £3,382,100.71 (10.3%); £3,771,935.25 -> £3,382,100.83 (10.3%); £3,771,935.50 -> £3,382,100.95 (10.3%); £3,771,935.76 -> £3,382,101.07 (10.3%); £3,771,936.03 -> £3,382,101.19 (10.3%); £3,771,936.29 -> £3,382,101.30 (10.3%); £3,771,936.54 -> £3,382,101.41 (10.3%); £3,771,936.80 -> £3,382,101.53 (10.3%); £3,771,937.06 -> £3,382,101.64 (10.3%); £3,771,937.32 -> £3,382,101.88 (10.3%); £3,771,937.58 -> £3,382,102.10 (10.3%); £3,771,937.84 -> £3,382,102.29 (10.3%); £3,771,938.08 -> £3,382,102.45 (10.3%); £3,771,938.35 -> £3,382,102.60 (10.3%); £3,771,938.61 -> £3,382,102.75 (10.3%); £3,771,938.86 -> £3,382,102.90 (10.3%); £3,771,939.11 -> £3,382,103.04 (10.3%); £3,771,939.37 -> £3,382,103.19 (10.3%); £3,771,939.62 -> £3,382,103.33 (10.3%); £3,771,939.88 -> £3,382,103.47 (10.3%); £3,771,940.14 -> £3,382,103.51 (10.3%); £3,771,940.40 -> £3,382,103.55 (10.3%); £3,771,940.63 -> £3,382,103.59 (10.3%); £3,771,940.85 -> £3,382,103.63 (10.3%); £3,771,941.04 -> £3,382,103.67 (10.3%); £3,771,941.20 -> £3,382,103.70 (10.3%); £3,771,941.36 -> £3,382,103.74 (10.3%); £3,771,941.52 -> £3,382,103.78 (10.3%); £3,771,941.67 -> £3,382,103.82 (10.3%); £3,771,941.82 -> £3,382,103.85 (10.3%); £3,771,941.97 -> £3,382,103.89 (10.3%); £3,771,942.13 -> £3,382,103.93 (10.3%); £3,771,942.28 -> £3,382,103.97 (10.3%); £3,771,942.44 -> £3,382,104.01 (10.3%); £3,771,942.59 -> £3,382,104.04 (10.3%); £3,771,942.75 -> £3,382,104.08 (10.3%); £3,771,942.91 -> £3,382,104.20 (10.3%); £3,771,943.06 -> £3,382,104.32 (10.3%); £3,771,943.23 -> £3,382,104.45 (10.3%); £3,771,943.43 -> £3,382,104.59 (10.3%); £3,771,943.64 -> £3,382,104.76 (10.3%); £3,771,943.86 -> £3,382,104.96 (10.3%); £3,771,944.10 -> £3,382,105.19 (10.3%); £3,771,944.36 -> £3,382,105.41 (10.3%); £3,771,944.61 -> £3,382,105.53 (10.3%); £3,771,944.87 -> £3,382,105.66 (10.3%); £3,771,945.12 -> £3,382,105.80 (10.3%); £3,771,945.38 -> £3,382,105.92 (10.3%); £3,771,945.63 -> £3,382,106.05 (10.3%); £3,771,945.89 -> £3,382,106.17 (10.3%); £3,771,946.16 -> £3,382,106.28 (10.3%); £3,771,946.42 -> £3,382,106.40 (10.3%); £3,771,946.69 -> £3,382,106.51 (10.3%); £3,771,946.95 -> £3,382,106.62 (10.3%); £3,771,947.21 -> £3,382,106.74 (10.3%); £3,771,947.47 -> £3,382,106.85 (10.3%); £3,771,947.72 -> £3,382,106.96 (10.3%); £3,771,947.97 -> £3,382,107.17 (10.3%); £3,771,948.23 -> £3,382,107.36 (10.3%); £3,771,948.49 -> £3,382,107.52 (10.3%); £3,771,948.75 -> £3,382,107.65 (10.3%); £3,771,949.00 -> £3,382,107.78 (10.3%); £3,771,949.26 -> £3,382,107.92 (10.3%); £3,771,949.52 -> £3,382,108.05 (10.3%); £3,771,949.79 -> £3,382,108.18 (10.3%); £3,771,950.04 -> £3,382,108.31 (10.3%); £3,771,950.29 -> £3,382,108.43 (10.3%); £3,771,950.55 -> £3,382,108.54 (10.3%); £3,771,950.81 -> £3,382,108.58 (10.3%); £3,771,951.06 -> £3,382,108.62 (10.3%); £3,771,951.30 -> £3,382,108.66 (10.3%); £3,771,951.52 -> £3,382,108.70 (10.3%); £3,771,951.71 -> £3,382,108.74 (10.3%); £3,771,951.87 -> £3,382,108.77 (10.3%); £3,771,952.03 -> £3,382,108.81 (10.3%); £3,771,952.17 -> £3,382,108.85 (10.3%); £3,771,952.33 -> £3,382,108.88 (10.3%); £3,771,952.48 -> £3,382,108.92 (10.3%); £3,771,952.63 -> £3,382,108.96 (10.3%); £3,771,952.79 -> £3,382,108.99 (10.3%); £3,771,952.95 -> £3,382,109.03 (10.3%); £3,771,953.10 -> £3,382,109.07 (10.3%); £3,771,953.26 -> £3,382,109.11 (10.3%); £3,771,953.42 -> £3,382,109.15 (10.3%); £3,771,953.58 -> £3,382,109.28 (10.3%); £3,771,953.73 -> £3,382,109.42 (10.3%); £3,771,953.90 -> £3,382,109.57 (10.3%); £3,771,954.09 -> £3,382,109.73 (10.3%); £3,771,954.30 -> £3,382,109.91 (10.3%); £3,771,954.53 -> £3,382,110.11 (10.3%); £3,771,954.77 -> £3,382,110.34 (10.3%); £3,771,955.03 -> £3,382,110.57 (10.3%); £3,771,955.29 -> £3,382,110.69 (10.3%); £3,771,955.54 -> £3,382,110.82 (10.3%); £3,771,955.79 -> £3,382,110.95 (10.3%); £3,771,956.05 -> £3,382,111.08 (10.3%); £3,771,956.31 -> £3,382,111.20 (10.3%); £3,771,956.57 -> £3,382,111.32 (10.3%); £3,771,956.82 -> £3,382,111.44 (10.3%); £3,771,957.07 -> £3,382,111.55 (10.3%); £3,771,957.32 -> £3,382,111.66 (10.3%); £3,771,957.58 -> £3,382,111.78 (10.3%); £3,771,957.84 -> £3,382,111.89 (10.3%); £3,771,958.09 -> £3,382,112.01 (10.3%); £3,771,958.36 -> £3,382,112.12 (10.3%); £3,771,958.61 -> £3,382,112.36 (10.3%); £3,771,958.87 -> £3,382,112.58 (10.3%); £3,771,959.13 -> £3,382,112.74 (10.3%); £3,771,959.39 -> £3,382,112.89 (10.3%); £3,771,959.64 -> £3,382,113.04 (10.3%); £3,771,959.91 -> £3,382,113.18 (10.3%); £3,771,960.16 -> £3,382,113.33 (10.3%); £3,771,960.42 -> £3,382,113.47 (10.3%); £3,771,960.67 -> £3,382,113.62 (10.3%); £3,771,960.93 -> £3,382,113.76 (10.3%); £3,771,961.18 -> £3,382,113.90 (10.3%); £3,771,961.43 -> £3,382,113.94 (10.3%); £3,771,961.69 -> £3,382,113.98 (10.3%); £3,771,961.94 -> £3,382,114.02 (10.3%); £3,771,962.16 -> £3,382,114.05 (10.3%); £3,771,962.36 -> £3,382,114.09 (10.3%); £3,771,962.52 -> £3,382,114.13 (10.3%); £3,771,962.67 -> £3,382,114.17 (10.3%); £3,771,962.82 -> £3,382,114.20 (10.3%); £3,771,962.97 -> £3,382,114.24 (10.3%); £3,771,963.13 -> £3,382,114.28 (10.3%); £3,771,963.28 -> £3,382,114.32 (10.3%); £3,771,963.43 -> £3,382,114.35 (10.3%); £3,771,963.58 -> £3,382,114.39 (10.3%); £3,771,963.73 -> £3,382,114.43 (10.3%); £3,771,963.89 -> £3,382,114.47 (10.3%); £3,771,964.04 -> £3,382,114.51 (10.3%); £3,771,964.19 -> £3,382,114.66 (10.3%); £3,771,964.35 -> £3,382,114.81 (10.3%); £3,771,964.52 -> £3,382,114.97 (10.3%); £3,771,964.70 -> £3,382,115.15 (10.3%); £3,771,964.91 -> £3,382,115.34 (10.3%); £3,771,965.13 -> £3,382,115.56 (10.3%); £3,771,965.37 -> £3,382,115.80 (10.3%); £3,771,965.62 -> £3,382,116.05 (10.3%); £3,771,965.88 -> £3,382,116.17 (10.3%); £3,771,966.14 -> £3,382,116.30 (10.3%); £3,771,966.39 -> £3,382,116.43 (10.3%); £3,771,966.65 -> £3,382,116.56 (10.3%); £3,771,966.91 -> £3,382,116.69 (10.3%); £3,771,967.16 -> £3,382,116.82 (10.3%); £3,771,967.42 -> £3,382,116.93 (10.3%); £3,771,967.67 -> £3,382,117.05 (10.3%); £3,771,967.92 -> £3,382,117.16 (10.3%); £3,771,968.18 -> £3,382,117.28 (10.3%); £3,771,968.44 -> £3,382,117.39 (10.3%); £3,771,968.69 -> £3,382,117.50 (10.3%); £3,771,968.95 -> £3,382,117.61 (10.3%); £3,771,969.21 -> £3,382,117.86 (10.3%); £3,771,969.45 -> £3,382,118.09 (10.3%); £3,771,969.71 -> £3,382,118.29 (10.3%); £3,771,969.97 -> £3,382,118.47 (10.3%); £3,771,970.23 -> £3,382,118.64 (10.3%); £3,771,970.49 -> £3,382,118.81 (10.3%); £3,771,970.74 -> £3,382,118.98 (10.3%); £3,771,971.00 -> £3,382,119.14 (10.3%); £3,771,971.25 -> £3,382,119.30 (10.3%); £3,771,971.50 -> £3,382,119.45 (10.3%); £3,771,971.76 -> £3,382,119.61 (10.3%); £3,771,972.01 -> £3,382,119.65 (10.3%); £3,771,972.26 -> £3,382,119.69 (10.3%); £3,771,972.50 -> £3,382,119.73 (10.3%); £3,771,972.72 -> £3,382,119.77 (10.3%); £3,771,972.92 -> £3,382,119.80 (10.3%); £3,771,973.08 -> £3,382,119.84 (10.3%); £3,771,973.23 -> £3,382,119.88 (10.3%); £3,771,973.38 -> £3,382,119.92 (10.3%); £3,771,973.54 -> £3,382,119.96 (10.3%); £3,771,973.69 -> £3,382,120.00 (10.3%); £3,771,973.84 -> £3,382,120.04 (10.3%); £3,771,973.99 -> £3,382,120.08 (10.3%); £3,771,974.14 -> £3,382,120.11 (10.3%); £3,771,974.29 -> £3,382,120.15 (10.3%); £3,771,974.44 -> £3,382,120.19 (10.3%); £3,771,974.60 -> £3,382,120.23 (10.3%); £3,771,974.75 -> £3,382,120.38 (10.3%); £3,771,974.91 -> £3,382,120.54 (10.3%); £3,771,975.08 -> £3,382,120.72 (10.3%); £3,771,975.27 -> £3,382,120.90 (10.3%); £3,771,975.48 -> £3,382,121.10 (10.3%); £3,771,975.70 -> £3,382,121.33 (10.3%); £3,771,975.94 -> £3,382,121.59 (10.3%); £3,771,976.20 -> £3,382,121.85 (10.3%); £3,771,976.46 -> £3,382,121.98 (10.3%); £3,771,976.73 -> £3,382,122.10 (10.3%); £3,771,976.98 -> £3,382,122.23 (10.3%); £3,771,977.24 -> £3,382,122.37 (10.3%); £3,771,977.50 -> £3,382,122.49 (10.3%); £3,771,977.76 -> £3,382,122.62 (10.3%); £3,771,978.02 -> £3,382,122.73 (10.3%); £3,771,978.27 -> £3,382,122.86 (10.3%); £3,771,978.53 -> £3,382,122.98 (10.3%); £3,771,978.78 -> £3,382,123.10 (10.3%); £3,771,979.04 -> £3,382,123.23 (10.3%); £3,771,979.30 -> £3,382,123.34 (10.3%); £3,771,979.56 -> £3,382,123.45 (10.3%); £3,771,979.81 -> £3,382,123.71 (10.3%); £3,771,980.07 -> £3,382,123.94 (10.3%); £3,771,980.33 -> £3,382,124.14 (10.3%); £3,771,980.59 -> £3,382,124.32 (10.3%); £3,771,980.84 -> £3,382,124.50 (10.3%); £3,771,981.10 -> £3,382,124.66 (10.3%); £3,771,981.36 -> £3,382,124.83 (10.3%); £3,771,981.62 -> £3,382,124.99 (10.3%); £3,771,981.88 -> £3,382,125.15 (10.3%); £3,771,982.14 -> £3,382,125.31 (10.3%); £3,771,982.39 -> £3,382,125.47 (10.3%); £3,771,982.65 -> £3,382,125.51 (10.3%); £3,771,982.91 -> £3,382,125.55 (10.3%); £3,771,983.15 -> £3,382,125.59 (10.3%); £3,771,983.37 -> £3,382,125.63 (10.3%); £3,771,983.57 -> £3,382,125.67 (10.3%); £3,771,983.71 -> £3,382,125.71 (10.3%); £3,771,983.84 -> £3,382,125.75 (10.3%); £3,771,983.98 -> £3,382,125.79 (10.3%); £3,771,984.12 -> £3,382,125.83 (10.3%); £3,771,984.25 -> £3,382,125.86 (10.3%); £3,771,984.39 -> £3,382,125.90 (10.3%); £3,771,984.53 -> £3,382,125.94 (10.3%); £3,771,984.67 -> £3,382,125.98 (10.3%); £3,771,984.80 -> £3,382,126.02 (10.3%); £3,771,984.94 -> £3,382,126.06 (10.3%); £3,771,985.07 -> £3,382,126.10 (10.3%); £3,771,985.21 -> £3,382,126.30 (10.3%); £3,771,985.34 -> £3,382,126.50 (10.3%); £3,771,985.49 -> £3,382,126.71 (10.3%); £3,771,985.65 -> £3,382,126.93 (10.3%); £3,771,985.84 -> £3,382,127.16 (10.3%); £3,771,986.04 -> £3,382,127.41 (10.3%); £3,771,986.25 -> £3,382,127.67 (10.3%); £3,771,986.47 -> £3,382,127.95 (10.3%); £3,771,986.70 -> £3,382,128.04 (10.3%); £3,771,986.93 -> £3,382,128.14 (10.3%); £3,771,987.16 -> £3,382,128.24 (10.3%); £3,771,987.38 -> £3,382,128.34 (10.3%); £3,771,987.61 -> £3,382,128.42 (10.3%); £3,771,987.84 -> £3,382,128.51 (10.3%); £3,771,988.06 -> £3,382,128.59 (10.3%); £3,771,988.30 -> £3,382,128.67 (10.3%); £3,771,988.52 -> £3,382,128.74 (10.3%); £3,771,988.74 -> £3,382,128.81 (10.3%); £3,771,988.96 -> £3,382,128.88 (10.3%); £3,771,989.19 -> £3,382,128.96 (10.3%); £3,771,989.41 -> £3,382,129.03 (10.3%); £3,771,989.64 -> £3,382,129.26 (10.3%); £3,771,989.88 -> £3,382,129.48 (10.3%); £3,771,990.10 -> £3,382,129.68 (10.3%); £3,771,990.34 -> £3,382,129.88 (10.3%); £3,771,990.57 -> £3,382,130.07 (10.3%); £3,771,990.79 -> £3,382,130.27 (10.3%); £3,771,991.02 -> £3,382,130.46 (10.3%); £3,771,991.24 -> £3,382,130.67 (10.3%); £3,771,991.47 -> £3,382,130.88 (10.3%); £3,771,991.70 -> £3,382,131.06 (10.3%); £3,771,991.92 -> £3,382,131.26 (10.3%); £3,771,992.15 -> £3,382,131.31 (10.3%); £3,771,992.37 -> £3,382,131.35 (10.3%); £3,771,992.58 -> £3,382,131.39 (10.3%); £3,771,992.77 -> £3,382,131.43 (10.3%); £3,771,992.94 -> £3,382,131.47 (10.3%); £3,771,993.09 -> £3,382,131.51 (10.3%); £3,771,993.23 -> £3,382,131.55 (10.3%); £3,771,993.37 -> £3,382,131.59 (10.3%); £3,771,993.51 -> £3,382,131.63 (10.3%); £3,771,993.65 -> £3,382,131.66 (10.3%); £3,771,993.79 -> £3,382,131.70 (10.3%); £3,771,993.93 -> £3,382,131.74 (10.3%); £3,771,994.07 -> £3,382,131.78 (10.3%); £3,771,994.22 -> £3,382,131.81 (10.3%); £3,771,994.35 -> £3,382,131.85 (10.3%); £3,771,994.50 -> £3,382,131.89 (10.3%); £3,771,994.64 -> £3,382,132.06 (10.3%); £3,771,994.79 -> £3,382,132.24 (10.3%); £3,771,994.94 -> £3,382,132.42 (10.3%); £3,771,995.11 -> £3,382,132.60 (10.3%); £3,771,995.30 -> £3,382,132.78 (10.3%); £3,771,995.50 -> £3,382,132.97 (10.3%); £3,771,995.71 -> £3,382,133.15 (10.3%); £3,771,995.94 -> £3,382,133.34 (10.3%); £3,771,996.18 -> £3,382,133.39 (10.3%); £3,771,996.42 -> £3,382,133.44 (10.3%); £3,771,996.65 -> £3,382,133.49 (10.3%); £3,771,996.88 -> £3,382,133.54 (10.3%); £3,771,997.10 -> £3,382,133.59 (10.3%); £3,771,997.34 -> £3,382,133.63 (10.3%); £3,771,997.57 -> £3,382,133.68 (10.3%); £3,771,997.80 -> £3,382,133.73 (10.3%); £3,771,998.03 -> £3,382,133.77 (10.3%); £3,771,998.26 -> £3,382,133.82 (10.3%); £3,771,998.50 -> £3,382,133.87 (10.3%); £3,771,998.73 -> £3,382,133.91 (10.3%); £3,771,998.96 -> £3,382,133.96 (10.3%); £3,771,999.20 -> £3,382,134.13 (10.3%); £3,771,999.43 -> £3,382,134.30 (10.3%); £3,771,999.66 -> £3,382,134.47 (10.3%); £3,771,999.89 -> £3,382,134.64 (10.3%); £3,772,000.13 -> £3,382,134.81 (10.3%); £3,772,000.36 -> £3,382,134.98 (10.3%); £3,772,000.59 -> £3,382,135.14 (10.3%); £3,772,000.83 -> £3,382,135.31 (10.3%); £3,772,001.07 -> £3,382,135.47 (10.3%); £3,772,001.30 -> £3,382,135.64 (10.3%); £3,772,001.54 -> £3,382,135.81 (10.3%); £3,772,001.78 -> £3,382,135.85 (10.3%); £3,772,002.01 -> £3,382,135.89 (10.3%); £3,772,002.24 -> £3,382,135.93 (10.3%); £3,772,002.44 -> £3,382,135.96 (10.3%); £3,772,002.61 -> £3,382,136.00 (10.3%); £3,772,002.77 -> £3,382,136.04 (10.3%); £3,772,002.93 -> £3,382,136.08 (10.3%); £3,772,003.09 -> £3,382,136.11 (10.3%); £3,772,003.26 -> £3,382,136.15 (10.3%); £3,772,003.42 -> £3,382,136.19 (10.3%); £3,772,003.58 -> £3,382,136.23 (10.3%); £3,772,003.74 -> £3,382,136.26 (10.3%); £3,772,003.91 -> £3,382,136.30 (10.3%); £3,772,004.07 -> £3,382,136.34 (10.3%); £3,772,004.23 -> £3,382,136.38 (10.3%); £3,772,004.39 -> £3,382,136.42 (10.3%); £3,772,004.55 -> £3,382,136.59 (10.3%); £3,772,004.71 -> £3,382,136.77 (10.3%); £3,772,004.89 -> £3,382,136.96 (10.3%); £3,772,005.09 -> £3,382,137.16 (10.3%); £3,772,005.31 -> £3,382,137.39 (10.3%); £3,772,005.54 -> £3,382,137.64 (10.3%); £3,772,005.79 -> £3,382,137.91 (10.3%); £3,772,006.07 -> £3,382,138.20 (10.3%); £3,772,006.33 -> £3,382,138.32 (10.3%); £3,772,006.62 -> £3,382,138.45 (10.3%); £3,772,006.89 -> £3,382,138.58 (10.3%); £3,772,007.16 -> £3,382,138.71 (10.3%); £3,772,007.42 -> £3,382,138.84 (10.3%); £3,772,007.70 -> £3,382,138.96 (10.3%); £3,772,007.96 -> £3,382,139.08 (10.3%); £3,772,008.23 -> £3,382,139.20 (10.3%); £3,772,008.51 -> £3,382,139.32 (10.3%); £3,772,008.78 -> £3,382,139.44 (10.3%); £3,772,009.05 -> £3,382,139.55 (10.3%); £3,772,009.33 -> £3,382,139.67 (10.3%); £3,772,009.60 -> £3,382,139.77 (10.3%); £3,772,009.87 -> £3,382,140.02 (10.3%); £3,772,010.13 -> £3,382,140.26 (10.3%); £3,772,010.40 -> £3,382,140.47 (10.3%); £3,772,010.66 -> £3,382,140.66 (10.3%); £3,772,010.92 -> £3,382,140.85 (10.3%); £3,772,011.19 -> £3,382,141.03 (10.3%); £3,772,011.45 -> £3,382,141.21 (10.3%); £3,772,011.72 -> £3,382,141.39 (10.3%); £3,772,011.99 -> £3,382,141.56 (10.3%); £3,772,012.26 -> £3,382,141.73 (10.3%); £3,772,012.52 -> £3,382,141.90 (10.3%); £3,772,012.79 -> £3,382,141.94 (10.3%); £3,772,013.06 -> £3,382,141.98 (10.3%); £3,772,013.30 -> £3,382,142.02 (10.3%); £3,772,013.52 -> £3,382,142.06 (10.3%); £3,772,013.74 -> £3,382,142.09 (10.3%); £3,772,013.90 -> £3,382,142.13 (10.3%); £3,772,014.06 -> £3,382,142.17 (10.3%); £3,772,014.23 -> £3,382,142.21 (10.3%); £3,772,014.39 -> £3,382,142.25 (10.3%); £3,772,014.56 -> £3,382,142.28 (10.3%); £3,772,014.72 -> £3,382,142.32 (10.3%); £3,772,014.88 -> £3,382,142.36 (10.3%); £3,772,015.04 -> £3,382,142.39 (10.3%); £3,772,015.20 -> £3,382,142.43 (10.3%); £3,772,015.37 -> £3,382,142.47 (10.3%); £3,772,015.53 -> £3,382,142.51 (10.3%); £3,772,015.69 -> £3,382,142.65 (10.3%); £3,772,015.85 -> £3,382,142.80 (10.3%); £3,772,016.03 -> £3,382,142.97 (10.3%); £3,772,016.23 -> £3,382,143.15 (10.3%); £3,772,016.45 -> £3,382,143.35 (10.3%); £3,772,016.68 -> £3,382,143.58 (10.3%); £3,772,016.93 -> £3,382,143.82 (10.3%); £3,772,017.20 -> £3,382,144.08 (10.3%); £3,772,017.47 -> £3,382,144.21 (10.3%); £3,772,017.76 -> £3,382,144.34 (10.3%); £3,772,018.02 -> £3,382,144.47 (10.3%); £3,772,018.28 -> £3,382,144.60 (10.3%); £3,772,018.54 -> £3,382,144.73 (10.3%); £3,772,018.81 -> £3,382,144.85 (10.3%); £3,772,019.08 -> £3,382,144.97 (10.3%); £3,772,019.35 -> £3,382,145.09 (10.3%); £3,772,019.61 -> £3,382,145.21 (10.3%); £3,772,019.87 -> £3,382,145.32 (10.3%); £3,772,020.15 -> £3,382,145.43 (10.3%); £3,772,020.42 -> £3,382,145.54 (10.3%); £3,772,020.69 -> £3,382,145.65 (10.3%); £3,772,020.97 -> £3,382,145.90 (10.3%); £3,772,021.23 -> £3,382,146.12 (10.3%); £3,772,021.50 -> £3,382,146.31 (10.3%); £3,772,021.77 -> £3,382,146.48 (10.3%); £3,772,022.04 -> £3,382,146.65 (10.3%); £3,772,022.30 -> £3,382,146.81 (10.3%); £3,772,022.57 -> £3,382,146.97 (10.3%); £3,772,022.83 -> £3,382,147.13 (10.3%); £3,772,023.09 -> £3,382,147.29 (10.3%); £3,772,023.37 -> £3,382,147.44 (10.3%); £3,772,023.64 -> £3,382,147.59 (10.3%); £3,772,023.91 -> £3,382,147.63 (10.3%); £3,772,024.18 -> £3,382,147.67 (10.3%); £3,772,024.43 -> £3,382,147.71 (10.3%); £3,772,024.66 -> £3,382,147.75 (10.3%); £3,772,024.87 -> £3,382,147.79 (10.3%); £3,772,025.04 -> £3,382,147.82 (10.3%); £3,772,025.20 -> £3,382,147.86 (10.3%); £3,772,025.35 -> £3,382,147.90 (10.3%); £3,772,025.51 -> £3,382,147.94 (10.3%); £3,772,025.67 -> £3,382,147.98 (10.3%); £3,772,025.83 -> £3,382,148.01 (10.3%); £3,772,025.99 -> £3,382,148.05 (10.3%); £3,772,026.15 -> £3,382,148.09 (10.3%); £3,772,026.30 -> £3,382,148.13 (10.3%); £3,772,026.46 -> £3,382,148.17 (10.3%); £3,772,026.62 -> £3,382,148.21 (10.3%); £3,772,026.78 -> £3,382,148.38 (10.3%); £3,772,026.94 -> £3,382,148.56 (10.3%); £3,772,027.12 -> £3,382,148.75 (10.3%); £3,772,027.32 -> £3,382,148.96 (10.3%); £3,772,027.54 -> £3,382,149.18 (10.3%); £3,772,027.77 -> £3,382,149.42 (10.3%); £3,772,028.02 -> £3,382,149.69 (10.3%); £3,772,028.29 -> £3,382,149.96 (10.3%); £3,772,028.56 -> £3,382,150.09 (10.3%); £3,772,028.82 -> £3,382,150.21 (10.3%); £3,772,029.10 -> £3,382,150.34 (10.3%); £3,772,029.36 -> £3,382,150.47 (10.3%); £3,772,029.63 -> £3,382,150.59 (10.3%); £3,772,029.90 -> £3,382,150.71 (10.3%); £3,772,030.17 -> £3,382,150.83 (10.3%); £3,772,030.45 -> £3,382,150.94 (10.3%); £3,772,030.73 -> £3,382,151.06 (10.3%); £3,772,030.99 -> £3,382,151.19 (10.3%); £3,772,031.26 -> £3,382,151.31 (10.3%); £3,772,031.53 -> £3,382,151.43 (10.3%); £3,772,031.80 -> £3,382,151.54 (10.3%); £3,772,032.07 -> £3,382,151.82 (10.3%); £3,772,032.34 -> £3,382,152.08 (10.3%); £3,772,032.61 -> £3,382,152.31 (10.3%); £3,772,032.88 -> £3,382,152.52 (10.3%); £3,772,033.15 -> £3,382,152.71 (10.3%); £3,772,033.42 -> £3,382,152.90 (10.3%); £3,772,033.69 -> £3,382,153.08 (10.3%); £3,772,033.95 -> £3,382,153.26 (10.3%); £3,772,034.22 -> £3,382,153.44 (10.3%); £3,772,034.49 -> £3,382,153.61 (10.3%); £3,772,034.76 -> £3,382,153.78 (10.3%); £3,772,035.03 -> £3,382,153.82 (10.3%); £3,772,035.31 -> £3,382,153.86 (10.3%); £3,772,035.55 -> £3,382,153.90 (10.3%); £3,772,035.78 -> £3,382,153.94 (10.3%); £3,772,035.99 -> £3,382,153.98 (10.3%); £3,772,036.15 -> £3,382,154.01 (10.3%); £3,772,036.31 -> £3,382,154.05 (10.3%); £3,772,036.47 -> £3,382,154.09 (10.3%); £3,772,036.63 -> £3,382,154.12 (10.3%); £3,772,036.79 -> £3,382,154.16 (10.3%); £3,772,036.95 -> £3,382,154.20 (10.3%); £3,772,037.11 -> £3,382,154.24 (10.3%); £3,772,037.27 -> £3,382,154.28 (10.3%); £3,772,037.43 -> £3,382,154.32 (10.3%); £3,772,037.59 -> £3,382,154.36 (10.3%); £3,772,037.76 -> £3,382,154.40 (10.3%); £3,772,037.92 -> £3,382,154.58 (10.3%); £3,772,038.08 -> £3,382,154.76 (10.3%); £3,772,038.27 -> £3,382,154.96 (10.3%); £3,772,038.47 -> £3,382,155.16 (10.3%); £3,772,038.69 -> £3,382,155.38 (10.3%); £3,772,038.92 -> £3,382,155.63 (10.3%); £3,772,039.17 -> £3,382,155.89 (10.3%); £3,772,039.44 -> £3,382,156.16 (10.3%); £3,772,039.71 -> £3,382,156.28 (10.3%); £3,772,039.98 -> £3,382,156.41 (10.3%); £3,772,040.25 -> £3,382,156.53 (10.3%); £3,772,040.52 -> £3,382,156.65 (10.3%); £3,772,040.80 -> £3,382,156.78 (10.3%); £3,772,041.07 -> £3,382,156.90 (10.3%); £3,772,041.34 -> £3,382,157.01 (10.3%); £3,772,041.61 -> £3,382,157.13 (10.3%); £3,772,041.89 -> £3,382,157.24 (10.3%); £3,772,042.16 -> £3,382,157.36 (10.3%); £3,772,042.43 -> £3,382,157.47 (10.3%); £3,772,042.70 -> £3,382,157.58 (10.3%); £3,772,042.97 -> £3,382,157.69 (10.3%); £3,772,043.26 -> £3,382,157.96 (10.3%); £3,772,043.53 -> £3,382,158.20 (10.3%); £3,772,043.80 -> £3,382,158.41 (10.3%); £3,772,044.06 -> £3,382,158.61 (10.3%); £3,772,044.33 -> £3,382,158.80 (10.3%); £3,772,044.60 -> £3,382,158.98 (10.3%); £3,772,044.89 -> £3,382,159.16 (10.3%); £3,772,045.16 -> £3,382,159.33 (10.3%); £3,772,045.44 -> £3,382,159.51 (10.3%); £3,772,045.71 -> £3,382,159.67 (10.3%); £3,772,045.97 -> £3,382,159.84 (10.3%); £3,772,046.26 -> £3,382,159.88 (10.3%); £3,772,046.53 -> £3,382,159.92 (10.3%); £3,772,046.78 -> £3,382,159.96 (10.3%); £3,772,047.02 -> £3,382,159.99 (10.3%); £3,772,047.24 -> £3,382,160.03 (10.3%); £3,772,047.39 -> £3,382,160.07 (10.3%); £3,772,047.56 -> £3,382,160.10 (10.3%); £3,772,047.72 -> £3,382,160.14 (10.3%); £3,772,047.89 -> £3,382,160.18 (10.3%); £3,772,048.04 -> £3,382,160.22 (10.3%); £3,772,048.21 -> £3,382,160.25 (10.3%); £3,772,048.37 -> £3,382,160.29 (10.3%); £3,772,048.54 -> £3,382,160.33 (10.3%); £3,772,048.70 -> £3,382,160.36 (10.3%); £3,772,048.86 -> £3,382,160.40 (10.3%); £3,772,049.02 -> £3,382,160.44 (10.3%); £3,772,049.18 -> £3,382,160.59 (10.3%); £3,772,049.34 -> £3,382,160.76 (10.3%); £3,772,049.52 -> £3,382,160.93 (10.3%); £3,772,049.72 -> £3,382,161.11 (10.3%); £3,772,049.93 -> £3,382,161.32 (10.3%); £3,772,050.17 -> £3,382,161.54 (10.3%); £3,772,050.42 -> £3,382,161.79 (10.3%); £3,772,050.68 -> £3,382,162.05 (10.3%); £3,772,050.96 -> £3,382,162.17 (10.3%); £3,772,051.22 -> £3,382,162.30 (10.3%); £3,772,051.49 -> £3,382,162.43 (10.3%); £3,772,051.76 -> £3,382,162.56 (10.3%); £3,772,052.03 -> £3,382,162.69 (10.3%); £3,772,052.30 -> £3,382,162.81 (10.3%); £3,772,052.58 -> £3,382,162.92 (10.3%); £3,772,052.86 -> £3,382,163.03 (10.3%); £3,772,053.12 -> £3,382,163.15 (10.3%); £3,772,053.39 -> £3,382,163.27 (10.3%); £3,772,053.66 -> £3,382,163.38 (10.3%); £3,772,053.93 -> £3,382,163.48 (10.3%); £3,772,054.20 -> £3,382,163.59 (10.3%); £3,772,054.46 -> £3,382,163.84 (10.3%); £3,772,054.74 -> £3,382,164.07 (10.3%); £3,772,055.01 -> £3,382,164.28 (10.3%); £3,772,055.28 -> £3,382,164.46 (10.3%); £3,772,055.55 -> £3,382,164.64 (10.3%); £3,772,055.82 -> £3,382,164.81 (10.3%); £3,772,056.10 -> £3,382,164.98 (10.3%); £3,772,056.36 -> £3,382,165.15 (10.3%); £3,772,056.63 -> £3,382,165.32 (10.3%); £3,772,056.91 -> £3,382,165.49 (10.3%); £3,772,057.18 -> £3,382,165.64 (10.3%); £3,772,057.45 -> £3,382,165.68 (10.3%); £3,772,057.72 -> £3,382,165.72 (10.3%); £3,772,057.97 -> £3,382,165.76 (10.3%); £3,772,058.21 -> £3,382,357.49 (10.3%)
- Bills issued: 153, average clarity 0.813, average bill shock 16.8%, bad debt provision £-118.83, avg complaint probability 4.7%
- Solvency signal: £343,182/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2024 produced a net gain of £347,820.71 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 41 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £120,992.97 (gross £518,611.38, capital £5,646.89)
  - Electricity: gross £464,863.13, capital £5,633.65, net £116,452.84
  - Gas: gross £53,748.25, capital £13.23, net £4,540.12
- Treasury at year end: £3,826,938.07
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
- Bill shock events (>=20%): 26 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C2 2025-04-30 (23%); C2 2025-06-07 (78%); C2g 2025-01-31 (32%); C2g 2025-02-28 (24%); C2g 2025-04-30 (30%); C2g 2025-05-31 (34%); C2g 2025-06-07 (73%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (40%); C8 2025-05-31 (36%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (33%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C1_2 2025-04-30 (43%); C1_2 2025-05-31 (29%); C1_2 2025-06-07 (81%)
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
- Bills issued: 66, average clarity 0.775, average bill shock 24.9%, bad debt provision £0.00, avg complaint probability 6.1%
- Solvency signal: £425,215/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-20.68 vs. naked (unhedged) net margin: £199.65
- hedging cost £220.33 vs. a fully unhedged book (commodity-only: actual net £-20.68 vs. naked net £199.65)
  - C2: actual £0.57 vs. naked £84.47 -- hedging cost £83.90
  - C2g: actual £8.83 vs. naked £-3.72 -- hedging added £12.55
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £120,992.97 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 26 customer(s) experienced a bill shock of >=20%.
