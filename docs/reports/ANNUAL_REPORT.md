# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,883,414.77
  (£1,416,778.55 net change)
- Solvency signal (final year): £423,068/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £22,585,653.32
  VAT remitted to HMRC: (£3,744,561.07) | Revenue (ex-VAT): £18,841,092.24
  Non-commodity pass-through: (£4,791,065.52)
- Gross margin: £6,455,328.74
- Capital costs: £51,231.56
- Net margin: £6,404,097.18
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1575, average clarity 0.789,
  service quality score 0.886
- Enterprise value (CLV sum across 13 billing accounts): £7,281,749.29
- Cost to serve (whole portfolio): £23,234.94, net margin after cost to serve: £6,380,862.24
- Hedge effectiveness (whole window): hedging cost £4,220,939.62 vs. a fully unhedged book (commodity-only: actual net £1,416,778.55 vs. naked net £5,637,718.17)

- **2021** (crisis year): net margin £78,289.38, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £339,913.25, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2250, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 220.6x (net £65,214.85 on £295.62 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 2/4 departures (50%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 4.7%, max 16.5% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +34.0% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 34.0% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,455,328.74, capital £51,231.56, net £6,404,097.18. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £78,289.38 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,404,097.18
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,637,718.17
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,220,939.62 vs. a fully unhedged book (commodity-only: actual net £1,416,778.55 vs. naked net £5,637,718.17)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,111.95 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £613,575.71 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £296.42 | £666.12 | £324.29 | £1,286.83 |
| 2017 | £30,139.92 | £0.00 | £-74.10 | £813.20 | £516.54 | £31,395.56 |
| 2018 | £101,124.68 | £0.00 | £-452.94 | £690.77 | £437.73 | £101,800.24 |
| 2019 | £222,418.63 | £9,999.92 | £282.64 | £801.72 | £492.20 | £233,995.12 |
| 2020 | £116,601.56 | £10,030.76 | £406.47 | £851.93 | £458.98 | £128,349.70 |
| 2021 | £67,613.82 | £9,999.92 | £227.79 | £576.18 | £-128.32 | £78,289.38 |
| 2022 | £332,870.49 | £9,999.92 | £-66.08 | £-1,633.57 | £-1,257.51 | £339,913.25 |
| 2023 | £90,284.03 | £9,999.92 | £558.92 | £477.54 | £-982.31 | £100,338.11 |
| 2024 | £354,734.88 | £10,030.76 | £789.59 | £2,206.37 | £710.70 | £368,472.31 |
| 2025 | £116,347.52 | £4,449.79 | £0.00 | £480.46 | £131.55 | £121,409.32 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **51** renewals.  Lost (churned): **4** accounts.

Accounts lost before end of window: C1, C3, C5, C6

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
| C3 | 2020-06-30 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9619 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.2300 | 0.5500 | 0.8651 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.4100 | 0.5500 | 0.8696 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.3200 | 0.5500 | 0.8123 | 0.8047 |
| C5 | 2020-12-30 | churned **CHURNED** | 0.3200 | 0.3500 | 0.7288 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.2000 | 0.5500 | 0.9093 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.2000 | 0.5500 | 0.8827 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.0800 | 0.5500 | 0.9780 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.0800 | 0.3500 | 0.9661 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9549 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.1100 | 0.5500 | 0.9597 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9597 | 0.9691 |
| C7 | 2021-12-30 | renewed | 0.1700 | 0.5500 | 0.9518 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.3200 | 0.5500 | 0.9402 | 0.5838 |
| C2 | 2022-03-31 | renewed | 0.3800 | 0.5500 | 0.9633 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3500 | 0.3500 | 0.9609 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.2600 | 0.5500 | 0.9700 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3500 | 0.5500 | 0.9364 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.3800 | 0.5500 | 0.9364 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.2900 | 0.5500 | 0.9509 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.4100 | 0.5500 | 0.9511 | 0.8723 |
| C2 | 2023-03-31 | renewed | 0.4100 | 0.5500 | 0.9273 | 0.6357 |
| C6 | 2023-03-31 | renewed | 0.4100 | 0.3500 | 0.8467 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.9224 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.7674 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.4100 | 0.5500 | 0.8739 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.4100 | 0.5500 | 0.9026 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.4100 | 0.5500 | 0.9030 | 0.7019 |
| C2 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.9175 | 0.8119 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.2300 | 0.3500 | 0.8684 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.1700 | 0.5500 | 0.9327 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.1700 | 0.5500 | 0.8906 | 0.0025 |
| C4 | 2024-09-29 | renewed | 0.3800 | 0.5500 | 0.9155 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.2900 | 0.5500 | 0.8895 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.1700 | 0.5500 | 0.9159 | 0.3751 |
| C2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.9083 | 0.1514 |
| C8 | 2025-03-30 | renewed | 0.3500 | 0.5500 | 0.9022 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 163.5%
- **Average signed error:** +144.0% (over-estimates vs SIM)
- **Renewal events with estimates:** 55

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +114.2% | 114.2% |
| 2017 | 3 | -12.5% | 16.5% |
| 2018 | 4 | +793.0% | 793.0% |
| 2019 | 4 | +602.3% | 642.0% |
| 2020 | 10 | +6.5% | 66.6% |
| 2021 | 8 | +136.5% | 140.1% |
| 2022 | 7 | +34.6% | 36.7% |
| 2023 | 7 | +20.8% | 45.7% |
| 2024 | 7 | +63.6% | 65.0% |
| 2025 | 2 | +22.3% | 22.3% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 55
- **Active renewers:** 18 (33%) — mean company estimate 25.6%, abs error 365.5%
- **Passive SVT-rollers:** 37 (67%) — mean company estimate 10.7%, abs error 65.3%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 13.3% | 0.0% | 114.2% |
| 2017 | 0 | 3 | 0.0% | 9.4% | 0.0% | 16.5% |
| 2018 | 3 | 1 | 54.0% | 13.8% | 1039.0% | 55.1% |
| 2019 | 2 | 2 | 53.2% | 13.6% | 1267.4% | 16.7% |
| 2020 | 6 | 4 | 11.3% | 6.9% | 63.0% | 71.8% |
| 2021 | 1 | 7 | 13.1% | 12.9% | 172.6% | 135.5% |
| 2022 | 0 | 7 | 0.0% | 6.0% | 0.0% | 36.7% |
| 2023 | 2 | 5 | 25.5% | 11.1% | 73.1% | 34.8% |
| 2024 | 4 | 3 | 15.2% | 16.0% | 57.5% | 74.9% |
| 2025 | 0 | 2 | 0.0% | 11.6% | 0.0% | 22.3% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 37
- **Above SVT (at-risk):** 8 (22%)
- **Below/at SVT (protected):** 29 (78%)
- **Mean rate vs SVT premium:** -11.1%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.2 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.2% | 120.1 | 140.0 |
| 2018 | 1 | 0 (0%) | -1.7% | 149.9 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.6 | 178.5 |
| 2020 | 4 | 0 (0%) | -27.0% | 130.1 | 178.1 |
| 2021 | 7 | 4 (57%) | +4.6% | 195.6 | 187.2 |
| 2022 | 7 | 4 (57%) | +12.0% | 295.6 | 318.4 |
| 2023 | 5 | 0 (0%) | -40.2% | 230.9 | 437.8 |
| 2024 | 3 | 0 (0%) | -16.7% | 204.8 | 247.5 |
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
| 2020 | 22 | 12.5% | 33.8% |
| 2021 | 16 | 15.4% | 44.5% |
| 2022 | 15 | 10.6% | 23.2% |
| 2023 | 15 | 22.4% | 55.4% |
| 2024 | 15 | 9.8% | 22.6% |
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
| 2020 | 10 | 0.67× | 1.74× |
| 2021 | 8 | 1.40× | 5.64× |
| 2022 | 7 | 0.37× | 1.05× |
| 2023 | 7 | 0.46× | 0.94× |
| 2024 | 7 | 0.65× | 1.08× |
| 2025 | 2 | 0.22× | 0.33× |

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
| 2021 | 10 | 0.99% | 4.24% | Low — stable portfolio |
| 2022 | 9 | 2.12% | 7.47% | MODERATE — asset adoption visible |
| 2023 | 9 | 2.62% | 8.48% | HIGH drift — EV/asset cohort growing |
| 2024 | 9 | 4.71% | 15.56% | HIGH drift — EV/asset cohort growing |
| 2025 | 2 | 8.62% | 16.47% | HIGH drift — EV/asset cohort growing |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **4.71%** mean / **15.56%** max in 2024. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
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
| 2022 | 9 | 2.1% | 7.5% |
| 2023 | 9 | 2.6% | 8.5% |
| 2024 | 9 | 4.7% | 15.6% |
| 2025 | 2 | 8.6% | 16.5% |

**85** of **85** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## EAC Drift Snapshot (Phase AI)

Per-customer consumption drift from company billing history (first renewal → latest renewal).
Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.

**2 significant** (≥15%) | **1 moderate** (5–15%) | **9 stable** (<5%)

| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |
|----------|-------------|-------------|-------|--------------|
| C2 | 5,265 | 4,236 | -20% | likely solar installation or significant efficiency upgrade |
| C4 | 4,131 | 3,365 | -19% | likely solar installation or significant efficiency upgrade |
| C7 | 13,179 | 12,155 | -8% | efficiency improvement or reduced occupancy |

**Portfolio demand trend:** 1 customers increasing / 11 decreasing (mean drift: -4.8%)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **4** (4 churn, 0 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.04, company est=0.10 |
| 2020-12-30 | CHURN | C5 | SIM p=0.27, company est=0.08 |
| 2021-12-30 | CHURN | C1 | SIM p=0.04, company est=0.06 |
| 2024-03-30 | CHURN | C6 | SIM p=0.13, company est=0.25 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 2 accounts | 0 active | yes |
| 2021-12-31 | 3 accounts | 0 active | yes |
| 2022-12-31 | 3 accounts | 0 active | yes |
| 2023-12-31 | 3 accounts | 0 active | yes |
| 2024-12-31 | 4 accounts | 0 active | yes |
| 2025-12-31 | 4 accounts | 0 active | yes |

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
| 2020 | 238,631 | 35,390 | 69,453 | 56,549 | 70,022 | 0 | 470,046 |  |
| 2021 | 246,108 | 14,974 | 71,203 | 49,551 | 62,680 | 41,327 | 485,843 |  |
| 2022 | 255,909 | -49,679 | 70,920 | 36,636 | 69,029 | 99,359 | 482,173 | ⬇ CfD REBATE |
| 2023 | 271,481 | 64,676 | 71,702 | 50,896 | 74,995 | 13,731 | 547,479 |  |
| 2024 | 307,209 | 109,781 | 72,815 | 68,616 | 82,450 | 1,996 | 642,867 |  |
| 2025 | 135,499 | 46,871 | 31,156 | 30,977 | 36,091 | 852 | 281,446 |  |
| **Total** | **1,723,293** | **262,953** | **458,497** | **336,557** | **467,098** | **157,265** | **3,405,664** | |

Total policy cost: £3,405,664 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2020 | 124,576 |  |
| 2021 | 122,584 |  |
| 2022 | 132,748 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 138,434 | RIIO-ED2 from Apr 2023 |
| 2024 | 142,511 |  |
| 2025 | 60,869 |  |
| **Total** | **878,042** | |

Total network cost: £878,042 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

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
| 2022 | 27,046 | 54,554 | 81,600 |
| 2023 | 32,230 | 79,964 | 112,194 |
| 2024 | 37,495 | 76,826 | 114,321 |
| 2025 | 17,243 | 32,173 | 49,417 |
| **Total** | **171,109** | **393,843** | **564,952** |

Gas policy pass-through in tariff unit rate (CCL + GGL at term start); gas network pass-through likewise. Net basis risk near-zero for annual contracts.


## Gas Book P&L — Year by Year (Phase 32a)

Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.
Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.

| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |
|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|
| 2016 | 1,388 | 578 | 811 | 0 | 479 | 7 | 324 | +23.4% |
| 2017 | 2,660 | 1,231 | 1,430 | 0 | 898 | 15 | 517 | +19.4% |
| 2018 | 3,115 | 1,751 | 1,364 | 0 | 905 | 21 | 438 | +14.1% |
| 2019 | 137,769 | 61,712 | 76,056 | 15,155 | 50,388 | 21 | 10,492 | +7.6% |
| 2020 | 121,126 | 43,943 | 77,183 | 19,468 | 47,215 | 11 | 10,490 | +8.7% |
| 2021 | 297,852 | 215,052 | 82,799 | 22,472 | 50,441 | 15 | 9,872 | +3.3% |
| 2022 | 589,447 | 499,059 | 90,388 | 27,046 | 54,554 | 46 | 8,742 | +1.5% |
| 2023 | 298,695 | 177,409 | 121,286 | 32,230 | 79,964 | 74 | 9,018 | +3.0% |
| 2024 | 272,025 | 146,907 | 125,118 | 37,495 | 76,826 | 56 | 10,741 | +3.9% |
| 2025 | 133,764 | 79,736 | 54,028 | 17,243 | 32,173 | 30 | 4,581 | +3.4% |
| **Total** | **1,857,841** | **1,227,378** | **630,462** | **171,109** | **393,843** | **296** | **65,215** | **+3.5%** |

Gas book net margin positive over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,441 | 9 | 274,160 | 2108.92× | OK |
| 2017 | 2,498,923 | 10 | 249,892 | 1922.25× | OK |
| 2018 | 2,487,680 | 11 | 226,153 | 1739.64× | OK |
| 2019 | 2,611,877 | 12 | 217,656 | 1674.28× | OK |
| 2020 | 2,923,975 | 13 | 224,921 | 1730.16× | OK |
| 2021 | 2,955,969 | 11 | 268,724 | 2067.11× | OK |
| 2022 | 3,169,662 | 10 | 316,966 | 2438.20× | OK |
| 2023 | 3,342,702 | 10 | 334,270 | 2571.31× | OK |
| 2024 | 3,755,685 | 10 | 375,569 | 2888.99× | OK |
| 2025 | 3,807,613 | 9 | 423,068 | 3254.37× | OK |

End-state (2025): **£423,068/account** across 9 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,441 | 81974.8× | OK |
| 2017 | 466 | 559 | 2,498,923 | 4470.3× | OK |
| 2018 | 865 | 1,038 | 2,487,680 | 2397.1× | OK |
| 2019 | 1,543 | 1,851 | 2,611,877 | 1411.0× | OK |
| 2020 | 1,979 | 2,374 | 2,923,975 | 1231.4× | OK |
| 2021 | 4,343 | 5,211 | 2,955,969 | 567.2× | OK |
| 2022 | 8,501 | 10,201 | 3,169,662 | 310.7× | OK |
| 2023 | 5,596 | 6,715 | 3,342,702 | 497.8× | OK |
| 2024 | 2,646 | 3,175 | 3,755,685 | 1182.8× | OK |
| 2025 | 3,864 | 4,636 | 3,807,613 | 821.2× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,484.20 | £12,219.01 | £261.64/MWh | £144.45/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,954.66 | £9,679.33 | £272.02/MWh | £154.19/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,955.89 | £9,328.73 | £250.77/MWh | £142.00/MWh | +10.9% |

Total HH revenue: £63,621.82 vs flat equivalent £58,718.49 (+8.4% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 38 | 135% | C5 (2016-09-30) |
| 2017 | 68 | 281% | C5 (2017-02-28) |
| 2018 | 83 | 1414% | C3g (2018-08-31) |
| 2019 | 76 | 152% | C3 (2019-09-30) |
| 2020 | 74 | 319% | C5 (2020-12-29) |
| 2021 | 58 | 178% | C1g (2021-07-31) |
| 2022 | 65 | 147% | C4g (2022-12-31) |
| 2023 | 55 | 275% | C6 (2023-11-30) |
| 2024 | 42 | 142% | C8 (2024-06-30) |
| 2025 | 25 | 195% | C8 (2025-06-07) |

Total: **584** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2018-08-31 | C3g | +1414% | no |
| 2020-12-29 | C5 | +319% | yes |
| 2018-07-31 | C7 | +313% | no |
| 2017-02-28 | C5 | +281% | yes |
| 2023-11-30 | C6 | +275% | yes |
| 2020-08-31 | C6 | +210% | yes |
| 2017-05-31 | C6 | +204% | yes |
| 2025-06-07 | C8 | +195% | no |
| 2018-10-31 | C6 | +179% | yes |
| 2021-07-31 | C1g | +178% | no |

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
| 2022 | 3 | 62% | 92% | 2 ⚠ |
| 2023 | 3 | 0% | 0% | 0 |
| 2024 | 3 | 0% | 0% | 0 |
| 2025 | 1 | 7% | 7% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £20.1 | £123.8 (+515%) | 95% |
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
| Total offer cost (foregone margin) | £150,301.78 |
| Margin saved (retained customers' terms) | £1,215,020.93 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£1,064,719.15** |
| Acquisition cost avoided (retained customers) | £2,300.00 |
| **Full economic ROI (margin + acq savings)** | **£1,067,019.15** |

Missed opportunities (churns with no offer): **4** (£4,804.29 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 4 (£4,804.29 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 2 | 2 | £70.90 | £1352.58 | £1281.68 | £0.00 |
| 2018 | 2 | 2 | £24321.59 | £165366.67 | £141045.07 | £0.00 |
| 2019 | 2 | 2 | £32311.18 | £296612.44 | £264301.26 | £0.00 |
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £2204.75 |
| 2021 | 3 | 3 | £65918.53 | £424276.03 | £358357.50 | £-178.13 |
| 2022 | 2 | 2 | £27444.18 | £323993.59 | £296549.41 | £0.00 |
| 2023 | 1 | 1 | £235.40 | £3419.63 | £3184.23 | £0.00 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £2777.67 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2017-04-01 | C8 | 0.34 | 3% | £45.82 | £861.32 | £150 | £815.50 | retained |
| 2017-07-01 | C3 | 0.39 | 3% | £25.08 | £491.25 | £150 | £466.17 | retained |
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24237.57 | £163825.67 | £150 | £139588.10 | retained |
| 2018-12-31 | C5 | 0.37 | 3% | £84.02 | £1541.00 | £400 | £1456.97 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.66 | 5% | £17469.37 | £194971.28 | £150 | £177501.91 | retained |
| 2021-03-31 | C_IC2 | 0.40 | 3% | £5377.77 | £93554.73 | £150 | £88176.96 | retained |
| 2021-04-30 | C_IC1 | 0.38 | 3% | £8549.97 | £161699.06 | £150 | £153149.10 | retained |
| 2021-12-31 | C_IC3 | 0.54 | 5% | £51990.79 | £169022.24 | £150 | £117031.45 | retained |
| 2022-04-30 | C_IC2 | 0.40 | 3% | £9365.98 | £94520.13 | £150 | £85154.15 | retained |
| 2022-05-30 | C_IC1 | 0.41 | 3% | £18078.19 | £229473.45 | £150 | £211395.26 | retained |
| 2023-03-31 | C6 | 0.40 | 3% | £235.40 | £3419.63 | £400 | £3184.23 | retained |

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

Serial savers (2): C_IC1 (4 offers, £68,335), C_IC2 (3 offers, £29,586).

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £7,281,749.29 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £638,644.12 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,286.83 |
| 2017 | £31,395.56 |
| 2018 | £101,800.24 |
| 2019 | £233,995.12 |
| 2020 | £128,349.70 |
| 2021 | £78,289.38 |
| 2022 | £339,913.25 |
| 2023 | £100,338.11 | ← trailing
| 2024 | £368,472.31 | ← trailing
| 2025 | £121,409.32 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £4,512.17 | — |
| C2 | £6,172.37 | £912.99 |
| C3 | £5,445.34 | — |
| C4 | £4,028.50 | £-293.09 |
| C5 | £10,574.38 | — |
| C6 | £19,419.26 | £2,186.24 |
| C7 | £8,048.63 | £552.19 |
| C8 | £8,821.40 | £712.49 |
| C9 | £9,974.69 | £1,384.13 |
| C_IC1 | £1,649,043.98 | £378,062.45 |
| C_IC2 | £960,267.62 | £199,265.93 |
| C_IC3 | £3,089,743.99 | £40,337.47 |
| C_IC4 | £1,505,696.97 | £15,523.33 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £5,148.47 | — | — | — | £12,587.98 | — | £9,201.03 | — | — | — | — | — | — |
| 2017 | £5,231.67 | £10,444.03 | £8,807.25 | £8,105.00 | £12,043.37 | £23,950.54 | £8,859.83 | £13,645.68 | £11,194.96 | — | — | — | — |
| 2018 | £4,931.67 | £7,734.77 | £7,536.37 | £6,553.41 | £12,087.51 | £18,135.42 | £7,810.19 | £10,311.41 | £9,920.64 | £2,655,696.32 | — | — | — |
| 2019 | £4,477.70 | £6,355.12 | £7,157.54 | £6,398.31 | £10,449.73 | £20,925.73 | £7,993.96 | £9,755.47 | £9,238.95 | £2,148,794.77 | £1,229,399.52 | — | — |
| 2020 | £4,055.37 | £7,798.11 | £6,096.16 | £5,051.07 | £8,624.52 | £15,157.71 | £7,269.64 | £8,338.10 | £9,096.49 | £1,142,134.35 | £742,862.14 | £2,125,002.42 | £1,280,530.60 |
| 2021 | £4,005.72 | £7,172.32 | £5,224.55 | £4,519.74 | £9,668.92 | £14,814.71 | £6,744.33 | £8,504.15 | £7,859.12 | £1,298,472.40 | £576,015.50 | £2,034,411.43 | £1,365,158.58 |
| 2022 | £4,107.42 | £5,720.18 | £4,617.09 | £2,561.53 | £8,488.33 | £14,118.21 | £4,196.67 | £7,048.60 | £7,265.52 | £1,036,751.01 | £660,995.56 | £1,955,975.60 | £1,091,884.36 |
| 2023 | £2,879.17 | £4,710.73 | £4,190.94 | £1,698.06 | £7,086.07 | £15,274.41 | £4,614.03 | £6,353.31 | £6,179.51 | £970,660.57 | £597,184.98 | £1,380,932.43 | £984,426.99 |
| 2024 | £2,964.84 | £4,686.39 | £3,798.64 | £2,165.11 | £7,056.35 | £13,691.10 | £4,629.14 | £6,843.54 | £6,717.89 | £972,666.64 | £639,084.35 | £1,762,025.37 | £982,043.39 |
| 2025 | £3,019.65 | £4,401.02 | £3,994.11 | £2,586.11 | £7,053.65 | £11,503.50 | £5,167.92 | £6,323.96 | £5,874.17 | £1,164,867.12 | £573,186.82 | £1,901,080.89 | £1,093,660.82 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £1,290.83, range £219.95–£4,218.12.

- C1: cost to serve £329.93, net margin after CTS £2,471.19
- C1g: cost to serve £330.00, net margin after CTS £1,211.50
- C2: cost to serve £505.43, net margin after CTS £5,018.10
- C2g: cost to serve £505.55, net margin after CTS £2,781.52
- C3: cost to serve £219.95, net margin after CTS £2,165.58
- C3g: cost to serve £220.00, net margin after CTS £1,080.00
- C4: cost to serve £477.86, net margin after CTS £3,257.41
- C4g: cost to serve £477.97, net margin after CTS £1,208.74
- C5: cost to serve £599.87, net margin after CTS £7,238.74
- C6: cost to serve £959.77, net margin after CTS £21,820.37
- C7: cost to serve £519.13, net margin after CTS £10,210.16
- C8: cost to serve £505.43, net margin after CTS £11,909.21
- C9: cost to serve £491.72, net margin after CTS £12,256.33
- C_IC1: cost to serve £4,218.12, net margin after CTS £1,870,779.01
- C_IC2: cost to serve £3,718.18, net margin after CTS £905,465.88
- C_IC3: cost to serve £3,218.32, net margin after CTS £1,803,198.72
- C_IC3g: cost to serve £3,219.18, net margin after CTS £619,427.85
- C_IC4: cost to serve £2,718.52, net margin after CTS £1,103,966.75


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 27 recovery surcharge(s) at renewal based on prior-term losses (4 gas). Avg surcharge: 15.0%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.37/MWh |
| C5 | electricity | 2018-12-31 | £-206.89 | £2,324.13 | +3.9% | £148.68/MWh | £153.53/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,283.71 | £6,187.80 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,215.97 | £10,069.00 | +20.0% | £128.22/MWh | £175.80/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,915.21 | £3,421.95 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £179.41/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £143.36/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £59.45/MWh |
| C7 | electricity | 2021-12-30 | £-226.17 | £1,913.68 | +6.8% | £311.83/MWh | £337.84/MWh |
| C_IC3 | electricity | 2021-12-31 | £-29,353.58 | £441,157.77 | +1.6% | £224.03/MWh | £261.89/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £316.20/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £307.57/MWh |
| C4 | electricity | 2022-09-30 | £-231.16 | £893.04 | +20.0% | £404.86/MWh | £487.96/MWh |
| C4g | gas | 2022-09-30 | £-869.98 | £1,040.11 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,925.74 | £2,404.50 | +20.0% | £266.73/MWh | £319.35/MWh |
| C2 | electricity | 2023-03-31 | £-191.17 | £1,780.28 | +5.7% | £319.17/MWh | £372.45/MWh |
| C2g | gas | 2023-03-31 | £-321.24 | £1,782.04 | +13.0% | £83.68/MWh | £108.77/MWh |
| C8 | electricity | 2023-03-31 | £-348.38 | £3,898.74 | +3.9% | £319.17/MWh | £340.94/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £235.69/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.00/MWh |
| C4 | electricity | 2023-09-30 | £-292.88 | £1,307.19 | +17.4% | £216.77/MWh | £252.56/MWh |
| C4g | gas | 2023-09-30 | £-2,038.74 | £2,732.11 | +20.0% | £47.83/MWh | £65.16/MWh |
| C7 | electricity | 2023-12-30 | £-445.92 | £3,990.91 | +6.2% | £242.22/MWh | £244.32/MWh |
| C_IC3 | electricity | 2023-12-31 | £-167,348.92 | £929,774.11 | +13.0% | £118.95/MWh | £127.69/MWh |
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
- **Estimated margin protected:** £1,215,020.93
- **No-offer churns:** 4 total (0 blind miss / 0 deliberate pass)
- **Retention coverage rate:** 75% of at-risk renewals received an offer

### 2. Flexibility Revenue Intelligence

- No flexibility revenue data available.

### 3. Churn Pattern Analysis

- **Total lifetime churn events:** 4
- **Peak churn year:** 2020 (2 events)

### 4. Board Recommendations

1. **Crisis-year churn:** 1 churn events in 2021–2022. Maintain minimum hedge floor pre-crisis to preserve pricing stability and limit bill-shock churn.

## CRM Intelligence: Risk Triage (Final Year)

Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.

| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |
|---------|-----|-----------|-----------|----------|-------------|-----------------|
| C5 | SME | MEDIUM | 27% | 8% | -21.2% [competitive] | £7,238.74 |
| C6 | SME | LOW | 13% | 25% | -26.1% [competitive] | £21,820.37 |
| C7 | resi | LOW | 11% | 17% | -14.3% | £10,210.16 |
| C9 | resi | LOW | 11% | 14% | -14.3% | £12,256.33 |
| C8 | resi | LOW | 10% | 13% | -23.6% [competitive] | £11,909.21 |
| C2 | resi | LOW | 9% | 10% | -23.6% [competitive] | £5,018.10 |
| C4 | resi | LOW | 8% | 17% | -9.0% | £3,257.41 |
| C_IC3 | I&C | LOW | 8% | 8% | -53.9% [competitive] | £1,803,198.72 |
| C1 | resi | LOW | 4% | 6% | -12.0% | £2,471.19 |
| C3 | resi | LOW | 4% | 10% | -38.6% [competitive] | £2,165.58 |
| C_IC2 | I&C | LOW | 4% | 95% | +12.4% [overpriced] | £905,465.88 |
| C_IC1 | I&C | LOW | 3% | 95% | -0.1% | £1,870,779.01 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 0 accounts
- MEDIUM (>=15%): 1 accounts
- LOW (<15%): 11 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £0.00

## Churn Root Cause Attribution

Per-churned-account analysis: pricing journey, rate-vs-SVT positioning, and company vs SIM churn estimate at the point of departure.

| Account | Seg | Churn Date | Tenure | Last Rate Shock | Rate vs SVT | Sim Risk | Co. Est. | Margin Lost |
|---------|-----|------------|--------|-----------------|-------------|----------|----------|-------------|
| C3 | resi | 2020-06-30 | 4.0yr | -3.6% | -38.6% | 4% | 10% | £2,165.58 |
| C5 | SME | 2020-12-30 | 5.0yr | +1.5% | -21.2% | 27% | 8% | £7,238.74 |
| C1 | resi | 2021-12-30 | 6.0yr | +1.4% | -12.0% | 4% | 6% | £2,471.19 |
| C6 | SME | 2024-03-30 | 8.0yr | -2.5% | -26.1% | 13% | 25% | £21,820.37 |

**Root Cause Summary:**
- Total churned accounts: 4
- Lifetime margin lost: £33,695.88
- Average tenure at departure: 5.7 years
- Company-warned churns (co. est. >=20%): 1 -- C6
- Crisis-era churns (2021-22): 1 -- absolute crisis price level, not rate-change delta, was the driver

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 4 accounts that churned without an offer? Calibrated from 12 actual offers (observed retention rate 100%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C3 | resi | 2020-06-30 | 10% | £590.77 | 5% | £29.54 | £561.23 | MISSED OPP. |
| C5 | SME | 2020-12-30 | 8% | £1,613.98 | 8% | £129.12 | £1,484.86 | MISSED OPP. |
| C1 | resi | 2021-12-30 | 6% | £-178.13 | 5% | £0.00 | n/a | CORRECT PASS |
| C6 | SME | 2024-03-30 | 25% | £2,777.67 | 8% | £222.21 | £2,555.46 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 4
- Correct no-offer (net-neg ETM): 1 (C1)
- Missed opportunities (positive ETM, below detection): 3
- Total term margin foregone: £4,982.42
- Total retention cost (counterfactual): £380.87
- Net counterfactual benefit: £4,601.55 (at 100% retention probability)
- Root cause: company churn detection below threshold for all missed cases -- churn model underestimated bill-shock risk

## Pricing Basis Risk Attribution

Forward curve accuracy at each contract term. tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd: positive = company over-estimated costs (higher than market); negative = company under-estimated (margin-at-risk).
Portfolio-wide mean error: +6.7%

| Year | Contracts | Mean Error | Max Abs | Over-priced | Under-priced | Assessment |
|------|-----------|------------|---------|-------------|--------------|------------|
| 2016 | 17 | +8.9% | 29.1% | 9 | 4 | moderate over |
| 2017 | 14 | +5.4% | 46.6% | 8 | 5 | moderate over |
| 2018 | 16 | -2.9% | 27.7% | 6 | 8 | on target |
| 2019 | 19 | +8.3% | 37.2% | 9 | 3 | moderate over |
| 2020 | 22 | +0.7% | 33.8% | 10 | 7 | on target |
| 2021 | 16 | +9.0% | 44.5% | 6 | 3 | moderate over |
| 2022 | 15 | -0.8% | 23.2% | 6 | 4 | on target |
| 2023 | 15 | +20.9% | 55.4% | 10 | 1 | HIGH OVER-PRICE |
| 2024 | 15 | +7.5% | 22.6% | 8 | 1 | moderate over |
| 2025 | 3 | +34.0% | 35.7% | 3 | 0 | HIGH OVER-PRICE |

**Basis Risk Summary:**
- Portfolio mean tariff error: +6.7%
- Worst over-pricing year: 2025 (+34.0%) -- company forward curve above settled market
- Post-crisis over-pricing years (2023, 2025): company locked in expensive crisis-era forwards after prices normalised -- mechanism that eroded real suppliers' margins 2022-24

## BSC Settlement Exposure

Elexon's Balancing and Settlement Code (BSC) requires suppliers to post credit cover to fund potential imbalance charges. Credit requirements track portfolio size and wholesale price levels. Peak daily settlement is the largest single-day settlement amount seen in that year.

| Year | BSC Credit Required | Peak Daily | % of Revenue |
|------|---------------------|------------|--------------|
| 2016 | £30 | £25 | 0.29% |
| 2017 | £559 | £466 | 0.24% |
| 2018 | £1,038 | £865 | 0.24% |
| 2019 | £1,851 | £1,543 | 0.15% |
| 2020 | £2,374 | £1,979 | 0.19% |
| 2021 | £5,211 | £4,343 | 0.30% |
| 2022 | £10,201 | £8,501 | 0.30% |
| 2023 | £6,715 | £5,596 | 0.26% |
| 2024 | £3,175 | £2,646 | 0.14% |
| 2025 | £4,636 | £3,864 | 0.48% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,201 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £525 | £99 | 12.4% |
| 2017 | 14 | £16,734 | £8,801 | £2,243 | 13.4% |
| 2018 | 15 | £29,029 | £17,505 | £6,787 | 23.4% |
| 2019 | 17 | £70,487 | £41,297 | £13,764 | 19.5% |
| 2020 | 18 | £67,965 | £43,990 | £7,131 | 10.5% |
| 2021 | 15 | £115,826 | £51,042 | £5,219 | 4.5% << |
| 2022 | 13 | £264,460 | £80,840 | £26,147 | 9.9% |
| 2023 | 13 | £195,942 | £69,942 | £7,718 | 3.9% << |
| 2024 | 13 | £169,847 | £98,279 | £28,344 | 16.7% |
| 2025 | 12 | £80,917 | £43,234 | £10,117 | 12.5% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £28,344 net/customer
**Worst year per customer:** 2016 at £99 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £458 | — | £458 |
| C1g | — | £710 | £710 |
| C2 | £1,178 | — | £1,178 |
| C2g | — | £1,294 | £1,294 |
| C3 | £-121 | — | £-121 * |
| C3g | — | £338 | £338 |
| C4 | £457 | — | £457 |
| C4g | — | £-1,639 | £-1,639 * |
| C5 | £-173 | — | £-173 * |
| C6 | £2,142 | — | £2,142 |
| C7 | £-597 | — | £-597 * |
| C8 | £2,276 | — | £2,276 |
| C9 | £2,280 | — | £2,280 |
| C_IC1 | £846,746 | — | £846,746 |
| C_IC2 | £435,084 | — | £435,084 |
| C_IC3 | £118,085 | — | £118,085 |
| C_IC3g | — | £64,511 | £64,511 |
| C_IC4 | £32,221 | — | £32,221 |
| **Total** | **£1,440,035** | **£65,215** | **£1,505,250** |

Loss-making accounts: C4g (£-1,639), C7 (£-597), C5 (£-173), C3 (£-121)
Gas loss-making: C4g (£-1,639)
Gas portfolio net: £65,215 (4.3% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,047 | £10,957 | £-8,909 |
| 2017 | £30,075 | £112,480 | £-82,404 |
| 2018 | £109,555 | £246,609 | £-137,053 |
| 2019 | £252,551 | £836,879 | £-584,328 |
| 2020 | £83,611 | £961,080 | £-877,468 |
| 2021 | £200,857 | £466,561 | £-265,703 |
| 2022 | £138,294 | £1,159,440 | £-1,021,145 |
| 2023 | £399,917 | £1,238,308 | £-838,390 |
| 2024 | £199,889 | £605,205 | £-405,316 |
| 2025 | £-19 | £200 | £-218 |
| **Total** | **£1,416,779** | **£5,637,718** | **£-4,220,939** |

Largest hedging cost: **2022** (£1,021,145 vs naked)
Smallest hedging cost: **2025** (£218 vs naked)
Conclusion: systematic forward hedging cost £4,220,939 over 10 years vs spot purchasing.

## Customer Service Quality

Ofgem benchmarks: bill clarity >0.82 (GREEN) / >0.80 (AMBER) / ≤0.80 (RED); complaint probability <5% (GREEN) / <6% (RED); bill shock <0.20% (GREEN) / <0.30% (AMBER) / ≥0.30% (RED).

| Year | Clarity | Complaint% | Shock% | Shock events | Bills | RAG |
|------|---------|------------|--------|--------------|-------|-----|
| 2016 | 0.792 R | 5.9% | 0.30% | 38 | 108 | RED ! |
| 2017 | 0.785 R | 5.7% | 0.26% | 68 | 168 | RED ! |
| 2018 | 0.755 R | 6.4% | 0.36% | 83 | 180 | RED ! |
| 2019 | 0.793 R | 5.7% | 0.24% | 76 | 204 | RED ! |
| 2020 | 0.794 R | 5.5% | 0.24% | 74 | 204 | RED ! |
| 2021 | 0.809 A | 5.2% | 0.21% | 58 | 180 | AMBER |
| 2022 | 0.778 R | 6.1% | 0.26% | 65 | 156 | RED ! |
| 2023 | 0.782 R | 5.8% | 0.25% | 55 | 156 | RED ! |
| 2024 | 0.811 A | 4.9% | 0.18% | 42 | 147 | AMBER |
| 2025 | 0.790 R | 5.8% | 0.26% | 25 | 72 | RED ! |

Worst clarity year: **2018** (0.755)
Highest complaint probability: **2018** (6.4%)
Worst bill shock: **2018** (0.36%)
RED years: 2016, 2017, 2018, 2019, 2020, 2022, 2023, 2025
AMBER years: 2021, 2024
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,441 | £1,287 |
| 2017 | 2.69 | WATCH | £2,498,923 | £31,396 |
| 2018 | — | — | £2,487,680 | £101,800 |
| 2019 | — | — | £2,611,877 | £233,995 |
| 2020 | — | — | £2,923,975 | £128,350 |
| 2021 | — | — | £2,955,969 | £78,289 |
| 2022 | 2.70 | WATCH | £3,169,662 | £339,913 |
| 2023 | 2.72 | WATCH | £3,342,702 | £100,338 |
| 2024 | — | — | £3,755,685 | £368,472 |
| 2025 | — | — | £3,807,613 | £121,409 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,807,613)**
**Treasury growth: £2,467,441 → £3,807,613 (+£1,340,171)**

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
| C3 | 2020-06 | 10.4% | £591 | below threshold |
| C5 | 2020-12 | 8.2% | £1,614 | below threshold |
| C1 | 2021-12 | 6.3% | -£178 | below threshold |
| C6 | 2024-03 | 24.9% | £2,778 | below threshold ⚑ |

**High-risk no-offer events (≥10% churn): 2** — £3,368 margin at risk.

### Gas Renewal Risk — High-Churn Reprice Events (≥15% estimate)

| Customer | Term Start | Old Rate p/therm | New Rate p/therm | Churn Est |
|----------|-----------|-----------------|-----------------|----------|
| C2g | 2017-04 | 26.92 | 32.81 | 20.1% |
| C1g | 2017-12 | 26.25 | 33.49 | 22.6% |
| C3g | 2018-07 | 23.11 | 28.84 | 20.9% |
| C4g | 2018-10 | 26.10 | 33.65 | 23.4% |
| C_IC3g | 2020-12 | 15.44 | 20.11 | 24.2% |
| C2g | 2021-03 | 21.66 | 35.00 | 39.9% |
| C4g | 2021-09 | 16.09 | 35.00 | 73.5% |
| C_IC3g | 2021-12 | 20.11 | 123.75 | 95.0% |

**High-risk gas reprices: 10**

> ⚑ = customers with ≥15% churn estimate who received no retention offer.

## Retention Decision Economics

Per-offer cost, expected margin protected, and ROI for each retention intervention.

| Customer | Period | Retention Cost £ | Margin Protected £ | ROI | Discount % | Outcome |
|----------|--------|-----------------|-------------------|-----|------------|---------|
| C8 | 2017-04 | £46 | £861 | 18.8× | 3% | retained |
| C3 | 2017-07 | £25 | £491 | 19.6× | 3% | retained |
| C_IC1 | 2018-01 | £24,238 | £163,826 | 6.8× | 8% | retained |
| C5 | 2018-12 | £84 | £1,541 | 18.3× | 3% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £17,469 | £194,971 | 11.2× | 5% | retained |
| C_IC2 | 2021-03 | £5,378 | £93,555 | 17.4× | 3% | retained |
| C_IC1 | 2021-04 | £8,550 | £161,699 | 18.9× | 3% | retained |
| C_IC3 | 2021-12 | £51,991 | £169,022 | 3.3× | 5% | retained |
| C_IC2 | 2022-04 | £9,366 | £94,520 | 10.1× | 3% | retained |
| C_IC1 | 2022-05 | £18,078 | £229,473 | 12.7× | 3% | retained |
| C6 | 2023-03 | £235 | £3,420 | 14.5× | 3% | retained |

**Total retention spend: £150,302** | **Total margin protected: £1,215,021**
**Portfolio retention ROI: 8.1×** | **Retained: 12/12**
**Best ROI intervention: C3 2017-07 (19.6×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £185,271 | — |
| Exit Gas (with churn risk) | £72,428 | -£112,843 |
| Reprice to Breakeven | £186,910 | +£1,639 |

**Loss-making gas accounts: C4**
**Board recommendation: REPRICE GAS**

> Gas drag reduces dual-fuel net margin. Repricing to breakeven is preferable to exit
> because exiting gas risks losing the electricity contract (cross-product churn).

## Portfolio Hedge Fraction Evolution

Average hedge fraction (0=fully naked, 1=fully hedged) per year.

| Year | Portfolio Avg | Min HF | Max HF | Naked Accounts | Covered Accts |
|------|--------------|--------|--------|---------------|--------------|
| 2016 | 88.9% | 85.0% | 92.2% | — | 13 |
| 2017 | 89.2% | 85.0% | 94.3% | — | 14 |
| 2018 | 89.3% | 85.0% | 92.2% | — | 15 |
| 2019 | 83.5% | 0.0% | 96.2% | 1 | 16 |
| 2020 | 81.3% | 0.0% | 96.0% | 1 | 14 |
| 2021 | 83.8% | 0.0% | 97.0% | 1 | 12 |
| 2022 | 86.0% | 0.0% | 97.4% | 1 | 12 |
| 2023 | 83.4% | 0.0% | 95.9% | 1 | 12 |
| 2024 | 80.8% | 0.0% | 94.4% | 1 | 11 |
| 2025 | 88.0% | 85.0% | 89.4% | — | 3 |

**Lowest portfolio hedge fraction: 2024 (80.8%)** — risk erosion from regime-change blindness.
**Naked positions first appear in 2019** — unhedged accounts expose portfolio to spot price swings.

> Regime-change blindness: the sim converged toward lower hedging during calm 2016-2020,
> mirroring the strategy that destroyed real UK suppliers entering the 2021-22 crisis.

## Risk Committee Intervention Pattern

Annual risk committee wake-ups (triggered when portfolio VaR exceeds threshold).

| Year | Wake-ups | Customer Adjustments | Avg Customers/Event | Max VaR Stressed £ |
|------|----------|---------------------|--------------------|--------------------|
| 2016 | 13 | 13 | 1.0 | £9 |
| 2017 | 12 | 33 | 2.8 | £401 |
| 2022 | 9 | 62 | 6.9 | £20,646 |
| 2023 | 4 | 28 | 7.0 | £49,108 |

**Peak intervention year: 2016 (13 wake-ups)**
**Total committee events (all years): 38**

> Each wake-up adjusts hedge fractions upward for flagged customers. 2016-17 (early book).
> 2022-23 crisis years trigger most interventions on I&C anchor accounts.

## Worst Half-Hourly Settlement Period by Year

Most loss-making single 30-minute period per settlement year.

| Year | Date | SP | Customer | Net Margin £ |
|------|------|----|----------|-------------|
| 2016 | 2016-12-31 | 48 | C1 | -£54 |
| 2017 | 2017-12-31 | 48 | C5 | -£327 |
| 2018 | 2018-12-31 | 48 | C5 | -£235 |
| 2019 | 2019-12-31 | 48 | C3 | -£69 |
| 2020 | 2020-06-29 | 48 | C3 | -£166 |
| 2021 | 2021-12-31 | 48 | C6 | -£299 |
| 2022 | 2022-12-31 | 48 | C6 | -£991 |
| 2023 | 2023-12-31 | 48 | C6 | -£865 |
| 2024 | 2024-06-28 | 31 | C_IC1 | -£26 |
| 2025 | 2025-01-08 | 31 | C_IC1 | -£81 |

**Single worst period: 2022 2022-12-31 SP48 (C6, -£991)** — exposure from gas supply anchor at year-end pricing.

> SP = settlement period (1-48; SP1 = 00:00-00:30). Year-end gas exposure dominates from 2020 onward as C_IC3g position grows.

## BSC Credit Obligation and Regulatory Levy Breakdown

Elexon BSC credit posting requirement and annual levy costs.

| Year | BSC Credit £ | CM Levy £ | Mutualization £ | CCL £ | Gas Network £ |
|------|-------------|----------|----------------|-------|--------------|
| 2016 | £30 | £37 | — | £189 | £479 |
| 2017 | £559 | £1,977 | — | £11,165 | £898 |
| 2018 | £1,038 | £9,350 | — | £17,434 | £905 |
| 2019 | £1,851 | £31,969 | — | £42,460 | £50,388 |
| 2020 | £2,374 | £56,549 | — | £69,453 | £47,215 |
| 2021 | £5,211 | £49,551 | £41,327 | £71,203 | £50,441 |
| 2022 | £10,201 | £36,636 | £99,359 | £70,920 | £54,554 |
| 2023 | £6,715 | £50,896 | £13,731 | £71,702 | £79,964 |
| 2024 | £3,175 | £68,616 | £1,996 | £72,815 | £76,826 |
| 2025 | £4,636 | £30,977 | £852 | £31,156 | £32,173 |

**Peak BSC credit obligation: 2022 (£10,201)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 13 | £164,979 | £88,771 | £8,603 | £12,691 |
| 2017 | 1 | £3,124,139 | £1,874,997 | £846,746 | £3,124,139 |
| 2018 | 1 | £1,524,796 | £909,184 | £435,084 | £1,524,796 |
| 2019 | 2 | £6,444,848 | £2,429,064 | £182,596 | £3,222,424 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £32,221 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,222,424/customer)**
**Best net margin cohort: 2017 (£846,746)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £67 | — | 108 |
| 2017 | +£2,707 | £37,159 | £530 | — | 168 |
| 2018 | +£9,875 | £65,510 | £239 | — | 180 |
| 2019 | +£28,353 | £164,625 | £107 | — | 204 |
| 2020 | +£35,390 | £238,631 | £195 | — | 204 |
| 2021 | +£14,974 | £246,108 | £366 | — | 180 |
| 2022 | -£49,679 CREDIT | £255,909 | £1,234 | 2 | 156 |
| 2023 | +£64,676 | £271,481 | £1,039 | 47 | 156 |
| 2024 | +£109,781 | £307,209 | £-212 | 4271 | 147 |
| 2025 | +£46,871 | £135,499 | £0 | — | 72 |

**CfD turned CREDIT in 2022: -£49,679 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2022 (£1,234)**

> CfD (Contracts for Difference): when wholesale > strike price, generators repay;
> the net credit is passed through as a negative levy on supplier bills.

## Segment Gross Margin Attribution

Gross margin (£) by customer segment and year.

| Year | resi electricity | resi gas | SME electricity | I&C electricity | I&C gas | Total |
|------|----------|----------|----------|----------|----------|-------|
| 2016 | £3,278 | £811 | £2,733 | £0 | £0 | £6,822 |
| 2017 | £4,987 | £1,430 | £3,385 | £113,418 | £0 | £123,220 |
| 2018 | £5,058 | £1,364 | £3,201 | £252,952 | £0 | £262,574 |
| 2019 | £5,786 | £1,430 | £4,053 | £616,155 | £74,626 | £702,051 |
| 2020 | £5,695 | £1,211 | £4,228 | £704,705 | £75,972 | £791,811 |
| 2021 | £5,322 | £544 | £2,956 | £674,549 | £82,255 | £765,627 |
| 2022 | £3,239 | -£730 | £3,850 | £953,449 | £91,118 | £1,050,926 |
| 2023 | £5,923 | -£229 | £4,638 | £777,398 | £121,515 | £909,245 |
| 2024 | £7,695 | £1,466 | £1,574 | £1,143,236 | £123,652 | £1,277,623 |
| 2025 | £3,355 | £519 | £0 | £461,420 | £53,509 | £518,802 |

**Best gross margin year: 2024 (£1,277,623)** | **Worst: 2016 (£6,822)**
**Loss-making: resi gas in 2022 (£-730)**
**Loss-making: resi gas in 2023 (£-229)**


## Price Cap Headroom (Tariff vs SVT)

Percentage difference between contracted unit rate and SVT (price cap) at term start.
Negative = below cap (headroom). Positive = above cap (I&C terms; SVT applies to resi only).

| Year | Terms | Avg vs SVT% | Above Cap | Min% | Max% |
|------|-------|-------------|-----------|------|------|
| 2016 | 3 | -6.3% | 0/3 | -6.7% | +-5.7% |
| 2017 | 3 | -14.2% | 0/3 | -15.7% | +-12.3% |
| 2018 | 4 | -1.1% | 1/4 | -3.3% | +0.7% |
| 2019 | 4 | -18.7% | 1/4 | -29.1% | +12.4% |
| 2020 | 10 | -30.1% | 0/10 | -69.0% | +-19.2% |
| 2021 | 8 | +2.5% | 4/8 | -12.0% | +25.9% |
| 2022 | 7 | +12.0% | 4/7 | -66.2% | +98.9% |
| 2023 | 7 | -38.4% | 0/7 | -60.5% | +-10.8% |
| 2024 | 7 | -24.3% | 0/7 | -53.9% | +-9.0% |
| 2025 | 2 | -23.6% | 0/2 | -23.6% | +-23.6% |

**Best headroom year: 2023 (avg 38.4% below SVT)**
**Largest above-SVT year: 2022** (4/7 terms above — note: I&C customers exempt from SVT cap)

> SVT (Standard Variable Tariff) = Ofgem price cap. Residential tariffs must not exceed SVT.
> I&C/SME terms above SVT are expected during crisis years when wholesale >cap.

## Portfolio Stress Test History

Retrospective RAG status: would year-end treasury have survived each scenario?
Credit facility: £2M. Weekly burn estimated at 1% of year-end treasury.

| Year | Treasury £ | Mkt Spike | Credit | Demand | Liquidity | Combined |
|------|-----------|----------|----------|----------|----------|----------|
| 2016 | £2,467,441 | AMBER | RED | GREEN | AMBER | RED |
| 2017 | £2,498,923 | AMBER | RED | GREEN | AMBER | RED |
| 2018 | £2,487,680 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,611,877 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,923,975 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,955,969 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,169,662 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,342,702 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,755,685 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,807,613 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 41.3% | £1,247 | £634 | 1.62% |
| 2017 | 14 | 32.8% | £24,835 | £8,873 | 2.02% |
| 2018 | 15 | 41.0% | £40,018 | £17,555 | 2.23% |
| 2019 | 17 | 40.3% | £96,608 | £41,347 | 2.13% |
| 2020 | 18 | 40.2% | £103,260 | £44,314 | 2.35% |
| 2021 | 15 | 29.0% | £161,103 | £50,924 | 2.22% |
| 2022 | 13 | 22.2% | £326,110 | £80,969 | 2.27% |
| 2023 | 13 | 23.8% | £263,863 | £70,514 | 2.51% |
| 2024 | 13 | 39.3% | £232,000 | £97,961 | 2.43% |
| 2025 | 12 | 39.8% | £107,093 | £46,869 | 3.35% |

**Best EBIT%: 2016 (41.3%)** | **Worst EBIT%: 2022 (22.2%)**
**Peak revenue/customer: 2022 (£326,110)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Population Anchoring -- Complaints & Arrears (Phase PS)

SIM aggregate complaint and arrears rates vs published UK benchmarks.
Complaints: Ofgem QoS survey, I&C adjusted (GREEN 2-6%, crisis 2-8%).
Arrears: DESNZ business energy debt (GREEN <8%, crisis <12%).

| Year | Complaint rate% | C.Bench hi | C.RAG | Arrears rate% | A.Bench hi | A.RAG |
|------|-----------------|-----------|-------|---------------|-----------|-------|
| 2016 | 5.91% | 6% | OK | 30.8% | 8% | ! |
| 2017 | 5.75% | 6% | OK | 14.3% | 8% | ~ |
| 2018 | 6.43% | 6% | ~ | 33.3% | 8% | ! |
| 2019 | 5.65% | 6% | OK | 23.5% | 8% | ! |
| 2020 | 5.49% | 6% | OK | 16.7% | 8% | ! |
| 2021 | 5.19% | 8% | OK | 20.0% | 12% | ! |
| 2022 | 6.10% | 8% | OK | 15.4% | 12% | ~ |
| 2023 | 5.84% | 8% | OK | 38.5% | 12% | ! |
| 2024 | 4.91% | 6% | OK | 23.1% | 8% | ! |
| 2025 | 5.77% | 6% | OK | 50.0% | 8% | ! |

**Complaints:** 9 of 10 years GREEN (I&C baseline 2-6% normal, 2-8% crisis).
**Arrears:** 0 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).

## Plausibility vs Industry

Key metrics vs UK retail energy norms (Ofgem/Cornwall Insight). OK = within range | ~ = amber | ! = outside expected range.

| Year | Net margin% | Gross margin% | Bad debt% | Churn% |
|------|-------------|---------------|-----------|--------|
| 2016 | !41.3% | !50.9% | OK1.62% | ~0% |
| 2017 | !32.8% | !35.7% | OK2.02% | ~0% |
| 2018 | !41.0% | !43.9% | OK2.23% | ~0% |
| 2019 | !40.3% | !42.8% | OK2.13% | ~0% |
| 2020 | !40.2% | !42.9% | OK2.35% | OK11% |
| 2021 | !29.0% | !31.6% | OK2.22% | OK7% |
| 2022 | !22.2% | ~24.8% | OK2.27% | ~0% |
| 2023 | !23.8% | ~26.7% | OK2.51% | ~0% |
| 2024 | !39.3% | !42.2% | OK2.43% | OK8% |
| 2025 | !39.8% | !43.8% | OK3.35% | ~0% |

**Benchmark ranges:** Net margin %: −5 to +8% green | Gross margin %: 0–20% green | Bad debt %: 0–5% green | Annual churn %: 3–35% green.
**RED — review required: 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025**

## Churn Prediction Calibration

How well the company estimated churn probability versus actual simulation outcomes.

| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |
|----------|------|----------------|-----------------|-------|---------|
| C3 | 2020-06 | 3.8% | 10.4% | +6.6pp | ACCURATE |
| C5 | 2020-12 | 27.1% | 8.2% | -18.9pp | UNDERESTIMATED |
| C1 | 2021-12 | 4.0% | 6.3% | +2.2pp | ACCURATE |
| C6 | 2024-03 | 13.2% | 24.9% | +11.7pp | OVERESTIMATED |

**Outcomes: 1 underestimated / 2 accurate / 1 overestimated**
**Mean absolute error: 9.9pp**
**No systematic directional bias detected.**

> Company churn estimates derived from company-observable signals (bill shock,
> margin feedback, renewal history) without access to the simulation's internal
> churn parameters — epistemic gap is expected and realistic for a small supplier.

## Counterfactual Retention & Threshold Optimisation

**Current threshold:** 30% | F1=0.000
**Optimal threshold:** 20% | F1=0.167

**RAG [~]:** AMBER — 2 unrecoverable high-value miss(es)

**Missed retention opportunities:** 4 no-offer churns
  Value at stake: £4,804
  Counterfactually recoverable (with offer): 1/4
  Net value recoverable (after offer cost): £1,564

### Per-miss detail

| Year | Customer | Est | SIM p | Recoverable? | Margin | Net value |
|------|----------|-----|-------|-------------|--------|----------|
| 2020 | C3 | 10% | 4% | No | £591 | £-50 |
| 2020 | C5 | 8% | 27% | Yes | £1,614 | £1,564 |
| 2021 | C1 | 6% | 4% | No | £-178 | £-50 |
| 2024 | C6 | 25% | 13% | No | £2,778 | £-50 |

### Threshold sensitivity curve

| Threshold | Recall | Precision | F1 |
|-----------|--------|-----------|----|
| 0% | 1.000 | 0.073 | 0.136 |
| 5% | 1.000 | 0.080 | 0.148 |
| 10% | 0.500 | 0.067 | 0.118 |
| 15% | 0.250 | 0.083 | 0.125 |
| 20% | 0.250 | 0.125 | 0.167 ← optimal |
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
| Detection gate (never scored above offer threshold) | 4 | 3% | 12% | 1/4 | £1,414 | +7.07 |

## Churn Model Quality (Phase NK)

Company churn model performance: did the company predict churn before it happened?
Threshold: company_churn_estimate > 30% = predicted. Evaluated at each renewal event.

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total churn events | 4 | Customers who actually churned |
| True Positives (TP) | 0 | Churn predicted AND happened |
| False Positives (FP) | 5 | Churn predicted BUT customer renewed |
| False Negatives (FN) | 4 | Churn NOT predicted BUT happened (blind miss) |
| True Negatives (TN) | 46 | No churn predicted AND customer renewed |
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
| Churners | 4 |
| Caught before departure (any renewal) | 3 |
| Never flagged | 1 |
| **Episode recall** | **75.0%** |
| Decayed after a prior save | 3 |
| Prevented-churn saves (retention offers that worked) | 12 |

### Per-Year Model Performance

| Year | TP | FP | FN | TN | Recall | Precision |
|------|----|----|----|----|--------|-----------|
| 2016 | 0 | 0 | 0 | 3 | 0% | 0% |
| 2017 | 0 | 0 | 0 | 3 | 0% | 0% |
| 2018 | 0 | 2 | 0 | 2 | 0% | 0% |
| 2019 | 0 | 1 | 0 | 3 | 0% | 0% |
| 2020 | 0 | 0 | 2 | 8 | 0% | 0% |
| 2021 | 0 | 1 | 1 | 6 | 0% | 0% |
| 2022 | 0 | 0 | 0 | 7 | 0% | 0% |
| 2023 | 0 | 1 | 0 | 6 | 0% | 0% |
| 2024 | 0 | 0 | 1 | 6 | 0% | 0% |
| 2025 | 0 | 0 | 0 | 2 | 0% | 0% |

## Credit Risk & Capital Stress (Phase NR)

**Ofgem FRA stress multiplier:** 2.5x (empirical: 2021-22 crisis, industry bad debt 1% → 2.5% revenue)

| Year | Revenue £ | Bad Debt £ | Bad Debt % | Crisis Stress £ |
|------|-----------|------------|------------|-----------------|

**Total bad debt (all years):** £3,563
**Crisis stress incremental:** £5,345

**RAG [OK]:** GREEN — Incremental credit stress below 0.5% revenue — not material

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (12 active customers) under 12-month forward scenarios.
Generated: 2026-07-13T11:25:06Z

Closes CLAUDE.md known failure: regime-change blindness — board can now ask 'what if 2021-22 happened again?'

| Scenario | Elec Fwd (£/MWh) | Gas Fwd (£/MWh) | Hedge Rec | Renewing | Exposure Delta |
|----------|------------------|-----------------|-----------|----------|----------------|
| Base | 86.7 | 55.1 | INCREASE | 0 | — |
| Bull | 56.1 | 35.7 | INCREASE | 0 | £-399,610 |
| Bear | 147.9 | 93.8 | INCREASE | 0 | +£799,221 |
| Crisis | 217.3 | 110.2 | INCREASE | 0 | +£1,566,272 |

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
| 2020 | 22 | 12.5% | 33.8% | MODERATE |
| 2021 | 16 | 15.4% | 44.5% | POOR |
| 2022 | 15 | 10.6% | 23.2% | MODERATE |
| 2023 | 15 | 22.4% | 55.4% | POOR |
| 2024 | 15 | 9.8% | 22.6% | GOOD |
| 2025 | 3 | 34.0% | 35.7% | POOR |

**Best accuracy year (n≥5): 2024 (9.8% mean error)**
**Worst accuracy year (n≥5): 2023 (22.4% mean error)**

> Errors reflect the company's information gap: forward curves are approximations;
> the company cannot observe simulation wholesale cost internals (epistemic blindfold).

## Dynamic Pricing Activity

Rate adjustments driven by the margin feedback loop and emergency reprice events.

| Year | Adjustments | Avg Delta £/MWh | Up | Down | Emergency |
|------|------------|-----------------|-----|------|-----------|
| 2016 | 4 | -0.6 | 1 | 3 | 0 |
| 2017 | 13 | -1.2 | 1 | 12 | 0 |
| 2018 | 14 | +2.5 | 6 | 8 | 2 |
| 2019 | 15 | +1.5 | 5 | 10 | 2 |
| 2020 | 18 | +3.1 | 9 | 9 | 2 |
| 2021 | 13 | +12.2 | 13 | 0 | 5 |
| 2022 | 12 | +18.8 | 11 | 1 | 5 |
| 2023 | 12 | +11.0 | 9 | 3 | 9 |
| 2024 | 12 | +3.9 | 4 | 8 | 2 |
| 2025 | 3 | +5.1 | 3 | 0 | 0 |

**Total adjustments 2016-2025: 116** | **Peak avg adjustment: 2022 (+18.8 £/MWh)**
**Emergency reprices: 27 total** (9 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £26,937 | £8,979 | — |
| 2017 | 9 | £102,282 | £11,365 | +£75,345 |
| 2018 | 10 | £2,740,718 | £274,072 | +£2,638,435 |
| 2019 | 11 | £3,460,947 | £314,632 | +£720,229 |
| 2020 | 13 | £5,362,017 | £412,463 | +£1,901,070 |
| 2021 | 13 | £5,342,571 | £410,967 | £-19,445 |
| 2022 | 13 | £4,803,730 | £369,518 | £-538,841 |
| 2023 | 13 | £3,986,191 | £306,630 | £-817,539 |
| 2024 | 13 | £4,408,373 | £339,106 | +£422,182 |
| 2025 | 13 | £4,782,720 | £367,902 | +£374,347 |

**Peak portfolio CLV: 2020 (£5,362,017)** | **Earliest/lowest: 2016 (£26,937)**
**Largest YoY gain: 2018 (+£2,638,435)**
**Largest YoY fall: 2023 (£-817,539)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

> **Basis: ledger/billed clock** (company.finance.double_entry journal, built from real issued bills). The Net Margin Bridge below reads a DIFFERENT clock (settlement, from the simulation's own per-period records) -- the two can diverge for the same year transition, primarily because non-commodity revenue recognition differs between the billed and settled bases for fixed-tariff records (see tools/generate_margin_bridge.py / the front page's reconciliation bridge for the quantified explanation).

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £16,206.51 | £3,594.97 | £4,363.77 | £8,247.77 | 50.9% | — | — | — | — |
| 2017 | £347,687.40 | £111,055.45 | £112,416.49 | £124,215.46 | 35.7% | +£331,480.89 | +£107,460.48 | +£108,052.72 | +£115,967.69 |
| 2018 | £600,267.18 | £172,874.18 | £164,071.67 | £263,321.33 | 43.9% | +£252,579.78 | +£61,818.73 | +£51,655.17 | +£139,105.87 |
| 2019 | £1,642,336.67 | £496,238.33 | £443,205.99 | £702,892.35 | 42.8% | +£1,042,069.49 | +£323,364.15 | +£279,134.32 | +£439,571.01 |
| 2020 | £1,858,681.90 | £431,611.43 | £629,411.89 | £797,658.59 | 42.9% | +£216,345.24 | £-64,626.90 | +£186,205.90 | +£94,766.24 |
| 2021 | £2,416,543.72 | £971,915.14 | £680,773.88 | £763,854.71 | 31.6% | +£557,861.82 | +£540,303.71 | +£51,361.99 | £-33,803.88 |
| 2022 | £4,239,425.11 | £2,387,110.02 | £799,720.68 | £1,052,594.41 | 24.8% | +£1,822,881.39 | +£1,415,194.88 | +£118,946.80 | +£288,739.71 |
| 2023 | £3,430,212.81 | £1,638,242.36 | £875,288.61 | £916,681.84 | 26.7% | £-809,212.30 | £-748,867.66 | +£75,567.94 | £-135,912.57 |
| 2024 | £3,016,002.29 | £931,171.08 | £811,332.71 | £1,273,498.51 | 42.2% | £-414,210.52 | £-707,071.28 | £-63,955.91 | +£356,816.67 |
| 2025 | £1,285,112.20 | £452,201.01 | £270,479.84 | £562,431.34 | 43.8% | £-1,730,890.09 | £-478,970.07 | £-540,852.87 | £-711,067.16 |

**Best GM year: 2016 (50.9%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Net Margin Bridge (Year-on-Year Attribution)

Decomposes each year's net margin change into: gross margin movement, bad debt, capital costs, policy levies, network costs.

> **Basis: settlement clock** (the simulation's own per-period records, years[]-based). The Gross Margin Bridge above reads a DIFFERENT clock (ledger/billed, from the double-entry journal built off real issued bills) -- the two can diverge for the same year transition; see tools/generate_margin_bridge.py / the front page's reconciliation bridge for the quantified explanation.

| Transition | Net Δ | Gross Δ | Bad Debt Δ | Capital Δ | Policy Δ | Network Δ | Portfolio | Driver | RAG |
|-----------|-------|---------|-----------|---------|---------|---------|---------|--------|-----|
| 2016→2017 | +£30,109 | +£116,398 | -£463 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£70,405 | +£139,354 | +£291 | -£349 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£132,195 | +£439,476 | +£132 | -£687 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£105,645 | +£89,761 | -£88 | +£347 | -£162,650 | -£33,016 | +1 | policy levies | RED |
| 2020→2021 | -£50,060 | -£26,185 | -£171 | -£3,670 | -£18,801 | -£1,234 | -3 | gross margin | RED |
| 2021→2022 | +£261,624 | +£285,300 | -£868 | -£7,626 | -£905 | -£14,277 | -2 | gross margin | GREEN |
| 2022→2023 | -£239,575 | -£141,681 | +£195 | +£3,498 | -£70,490 | -£31,097 | +0 | gross margin | RED |
| 2023→2024 | +£268,134 | +£368,378 | +£1,251 | +£96 | -£100,652 | -£938 | +0 | gross margin | GREEN |
| 2024→2025 | -£247,063 | -£758,820 | -£212 | +£4,003 | +£381,672 | +£126,295 | -1 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£247,063)** | **Best transition: 2023→2024 (+£268,134)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Unbilled Revenue Accrual (Accrual Accounting View)

An estimated-basis bill's revenue is recognised in full when issued (Phase 7a) -- that cash effect is correct and unchanged. This section shows how much of currently-recognised revenue is still PROVISIONAL (estimated, awaiting confirmation against a real meter read) versus already CONFIRMED, and how much has been RESTATED this run as D3's catch-up-rebilling resolved prior estimates.

**Outstanding unbilled revenue accrual: £571,416.74** across 62 bill(s) not yet confirmed by an actual read.

**Revenue restated this run: £6,393.86** across 150 catch-up correction(s) -- see the Net Margin Bridge above for the settlement-clock view and D3_catchup_rebilling for the per-bill mechanism.

| Customer | Outstanding Accrual £ |
|----------|------------------------|
| C_IC3g | £512,438.75 |
| C_IC4 | £54,849.20 |
| C3g | £1,416.53 |
| C3 | £1,197.23 |
| C4g | £709.79 |
| C2 | £372.57 |
| C1 | £186.24 |
| C2g | £126.64 |
| C1g | £74.14 |
| C4 | £45.65 |

## Payment Portfolio Health (P2: Billing Infra)

Year-by-year bad debt rate and high-churn-risk customer concentration.

| Year | Bad Debt | Bad Debt Rate | At-Risk Customers | At-Risk % | Trend | RAG |
|------|----------|--------------|-----------------|----------|-------|-----|
| 2016 | £67 | 0.64% | 0/3 | 0% | — STABLE | GREEN |
| 2017 | £530 | 0.23% | 0/9 | 0% | ↓ IMPROVING | GREEN |
| 2018 | £239 | 0.05% | 1/10 | 10% | ↓ IMPROVING | GREEN |
| 2019 | £107 | 0.01% | 3/11 | 27% | ↓ IMPROVING | GREEN |
| 2020 | £195 | 0.02% | 5/13 | 38% | ↑ DETERIORATING | AMBER |
| 2021 | £366 | 0.02% | 4/11 | 36% | ↑ DETERIORATING | AMBER |
| 2022 | £1,234 | 0.04% | 8/10 | 80% | ↑ DETERIORATING | RED |
| 2023 | £1,039 | 0.04% | 10/10 | 100% | — STABLE | RED |
| 2024 | £-212 | -0.01% | 3/10 | 30% | ↓ IMPROVING | GREEN |
| 2025 | £0 | 0.00% | 2/3 | 67% | ↑ DETERIORATING | RED |

**Worst bad debt year: 2016 (0.64%)** | **Peak at-risk concentration: 2023 (100% of customers)**

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
| 2023 | 1% | 1% | 99% | 87% | 13% | I&C | RED |
| 2024 | 1% | 0% | 99% | 90% | 10% | I&C | RED |
| 2025 | 1% | 0% | 99% | 90% | 10% | I&C | RED |

> **Concentration alert:** I&C dominated gross margin in 2017–2025. Loss of a single large I&C customer has outsized P&L impact. Benchmark: a resilient mixed-book supplier targets no segment >70% of gross margin.

## Shadow Retention Strategy (P4: Shadow Ops)

Counterfactual: what if the company had offered retention to ALL renewal customers (not just those above the 30% threshold)?
Shadow discount: 8% off next term. Assumes P(accept) = (1 - churn\_estimate) x 90%.

| Year | No-Offer Churns | Margin Lost | Shadow Retained | Offer Cost | Shadow Net Gain |
|------|----------------|------------|----------------|-----------|----------------|
| 2020 | 2 | £2,205 | £1,665 | £145 | +£1,520 |
| 2021 | 1 | £-178 | £-138 | £-12 | +£-126 |
| 2024 | 1 | £2,778 | £1,727 | £150 | +£1,577 |

**Total opportunity cost vs actual: +£2,971 net** (gross £4,804 margin lost; £283 offer cost if all retained).

> The shadow strategy net gain is small because all no-offer churns were residential customers with low margins. I&C customers (large margins) already received retention offers — the current threshold strategy is near-optimal for the existing portfolio composition.

## Ofgem FRA Regulatory Capital Ratio (Phase NZ)

Equity / (annual revenue ÷ 12). Ofgem FRA minimum: ≥ 1x monthly revenue.
Sector best practice: ≥ 6x (GREEN). Early warning: < 3x (AMBER). Non-compliant: < 1x (RED).
Real-world context: Bulb 2021 collapse at ~-0.01x; Igloo 2021 ~0.07x.

| Year | Equity | Monthly Rev | FRA Ratio | RAG | Compliant |
|------|--------|-------------|-----------|-----|-----------|
| 2016 | £2,473,323.59 | £1,350.54 | 1831.4x | ✓ GREEN | Yes |
| 2017 | £2,587,285.87 | £28,973.95 | 89.3x | ✓ GREEN | Yes |
| 2018 | £2,833,136.05 | £50,022.27 | 56.6x | ✓ GREEN | Yes |
| 2019 | £3,495,297.85 | £136,861.39 | 25.5x | ✓ GREEN | Yes |
| 2020 | £4,242,956.62 | £154,890.16 | 27.4x | ✓ GREEN | Yes |
| 2021 | £4,943,861.96 | £201,378.64 | 24.6x | ✓ GREEN | Yes |
| 2022 | £5,883,265.43 | £353,285.43 | 16.6x | ✓ GREEN | Yes |
| 2023 | £6,700,387.31 | £285,851.07 | 23.4x | ✓ GREEN | Yes |
| 2024 | £7,887,093.59 | £251,333.52 | 31.4x | ✓ GREEN | Yes |
| 2025 | £8,399,200.57 | £107,092.68 | 78.4x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.6x (equity £5,883,265.43 vs monthly revenue £353,285.43). RAG: GREEN.
**Strongest year:** 2016 — 1831.4x.

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
| 2016 | £16,206.51 | £6,023.42 | £51.20 | ✓ GREEN |  |
| 2017 | £347,687.40 | £129,223.82 | £1,098.40 | ✓ GREEN |  |
| 2018 | £600,267.18 | £223,099.30 | £1,896.34 | ✓ GREEN |  |
| 2019 | £1,642,336.67 | £610,401.79 | £5,188.42 | ✓ GREEN |  |
| 2020 | £1,858,681.90 | £690,810.11 | £5,871.89 | ✓ GREEN |  |
| 2021 | £2,416,543.72 | £898,148.75 | £7,634.26 | ✓ GREEN | CREDIT EXPECTED |
| 2022 | £4,239,425.11 | £1,575,653.00 | £13,393.05 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,430,212.81 | £1,274,895.76 | £10,836.61 | ✓ GREEN |  |
| 2024 | £3,016,002.29 | £1,120,947.52 | £9,528.05 | ✓ GREEN |  |
| 2025 | £1,285,112.20 | £477,633.37 | £4,059.88 | ✓ GREEN |  |

**Peak reconciliation exposure:** 2022 — max adverse £13,393 (4.5 months weighted tail).

_Note: Outstanding pool ≈ current-year revenue × (weighted outstanding months ÷ 12)._
_Max adverse = pool × blended variance rate (0.5% HH + 4% non-HH, portfolio-weighted)._
## Ofgem Supply Licence Health (Phase OC)

Annual licence health checks: customer base, net assets, liquidity, bad debt.
Breach triggers board escalation and Ofgem notification under SLC 0.
WATCH = within 20% of threshold. BREACH = threshold crossed.

| Year | Customers | Net Assets | Treasury | Cash Wks | Bad Debt % | Overall |
|------|-----------|------------|----------|----------|------------|---------|
| 2016 | 13 | £2,473,323.59 | £2,467,441.30 | 35691w | 0.64% | ✗ BREACH |
| 2017 | 14 | £2,587,285.87 | £2,498,923.22 | 1170w | 0.23% | ✗ BREACH |
| 2018 | 15 | £2,833,136.05 | £2,487,679.94 | 748w | 0.05% | ✗ BREACH |
| 2019 | 17 | £3,495,297.85 | £2,611,877.36 | 274w | 0.01% | ✗ BREACH |
| 2020 | 18 | £4,242,956.62 | £2,923,975.09 | 352w | 0.02% | ✗ BREACH |
| 2021 | 15 | £4,943,861.96 | £2,955,969.20 | 158w | 0.02% | ✗ BREACH |
| 2022 | 13 | £5,883,265.43 | £3,169,661.88 | 69w | 0.04% | ✗ BREACH |
| 2023 | 13 | £6,700,387.31 | £3,342,701.72 | 106w | 0.04% | ✗ BREACH |
| 2024 | 13 | £7,887,093.59 | £3,755,685.24 | 210w | -0.01% | ✗ BREACH |
| 2025 | 12 | £8,399,200.57 | £3,807,612.61 | 438w | 0.00% | ✗ BREACH |

**BREACH years:** 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 — board escalation required.

_Note: Complaints from contact model avg_complaint_probability. Customer count <50 triggers Ofgem viability review — small-portfolio years will show WATCH._
## Ofgem SLC Compliance Scorecard (Phase OD)

10 compliance domains per year, derived from simulation outputs.
G = GREEN (compliant), A = AMBER (watch), R = RED (breach).

| Domain | SLC Ref | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|--------|---------|------|------|------|------|------|------|------|------|------|------|
| Governance | SLC 0-9 | G | G | G | G | G | G | G | G | G | G |
| Billing/Metering | SLC 10-14 | A | A | A | A | A | G | A | A | G | A |
| Payment/Debt | SLC 15-19 | G | G | G | G | G | G | G | G | G | G |
| Information | SLC 20-24 | G | G | G | G | G | G | G | G | G | G |
| Complaints | SLC 25-29 / Ofgem Time to Fix rules | G | G | G | G | G | G | G | G | G | G |
| Vulnerable Cust | SLC 30-35 / PSR | G | G | G | G | G | G | G | G | G | G |
| Tariff/Cap | SLC 36-40 / Default Tariff Cap | G | G | G | G | G | G | G | G | G | G |
| Environmental | SLC 41-50 / RO, CfD, EE obligation | G | G | G | G | G | G | G | G | G | G |
| Network/BSC | SLC 51-60 / BSC obligations | G | G | G | G | G | G | G | G | G | G |
| Financial Res. | SLC 4C / SFR Decision 2023 | G | G | G | G | G | G | G | G | G | G |
| **Overall** |  | A | A | A | A | A | G | A | A | G | A |

**Watch years (AMBER):** 2016, 2017, 2018, 2019, 2020, 2022, 2023, 2025

_Note: Vulnerable customers, tariff/cap, and environmental domains defaulted to GREEN_
_(these are modelled as compliant; detailed SLC breach simulation not yet implemented)._
## Ofgem Annual Supply Return (Phase OE)

UK suppliers must file annual supply returns to Ofgem. Filed by 31 March of the following year.

| Year | Submitted | Customers (R/SME/I&C) | Elec GWh | Gas GWh | Bad Debt/Cust |
|------|-----------|----------------------|----------|---------|---------------|
| 2016 | Yes | 13/13/13 | 0.1 | 0.0 | £5 |
| 2017 | Yes | 14/14/14 | 1.5 | 0.1 | £38 |
| 2018 | Yes | 15/15/15 | 2.9 | 0.1 | £16 |
| 2019 | Yes | 17/17/17 | 7.1 | 2.8 | £6 |
| 2020 | Yes | 18/18/18 | 7.3 | 2.4 | £11 |
| 2021 | Yes | 15/15/15 | 9.6 | 6.0 | £24 |
| 2022 | Yes | 13/13/13 | 19.0 | 11.8 | £95 |
| 2023 | Yes | 13/13/13 | 15.0 | 6.0 | £80 |
| 2024 | Yes | 13/13/13 | 12.9 | 5.4 | £-16 |
| 2025 | Yes | 12/12/12 | 5.6 | 2.7 | £0 |

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
| 2020 | 10,111.5 | 0.358 ROC/MWh | 3,619.9 | £48.78 | £176,580 |
| 2021 | 9,982.4 | 0.364 ROC/MWh | 3,633.6 | £50.80 | £184,587 |
| 2022 | 9,935.9 | 0.370 ROC/MWh | 3,676.3 | £52.88 | £194,402 |
| 2023 | 9,950.1 | 0.376 ROC/MWh | 3,741.2 | £54.35 | £203,336 |
| 2024 | 9,980.0 | 0.382 ROC/MWh | 3,812.4 | £56.19 | £214,217 |
| 2025 | 4,261.0 | 0.389 ROC/MWh | 1,657.5 | £58.10 | £96,302 |
| **Total** | **66,551.7** | | | | **£1,268,065** |

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
| 2020 | 10,111.5 | GBP0.00 (scheme closed) | NIL |
| 2021 | 9,982.4 | GBP0.00 (scheme closed) | NIL |
| 2022 | 9,935.9 | GBP0.00 (scheme closed) | NIL |
| 2023 | 9,950.1 | GBP0.00 (scheme closed) | NIL |
| 2024 | 9,980.0 | GBP0.00 (scheme closed) | NIL |
| 2025 | 4,261.0 | GBP0.00 (scheme closed) | NIL |
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
| 2020 | 13 | 150,000 | OK (exempt) | N/A | NIL |
| 2021 | 10 | 150,000 | OK (exempt) | N/A | NIL |
| 2022 | 8 | 150,000 | OK (exempt) | N/A | NIL |
| 2023 | 8 | 150,000 | OK (exempt) | N/A | NIL |
| 2024 | 8 | 150,000 | OK (exempt) | N/A | NIL |
| 2025 | 7 | 150,000 | OK (exempt) | N/A | NIL |

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
| 2020 | ECO3 | GBP4.50 | 13 | OK (exempt) | GBP56 |
| 2021 | ECO3 | GBP4.50 | 10 | OK (exempt) | GBP72 |
| 2022 | ECO4 | GBP6.80 | 8 | OK (exempt) | GBP192 |
| 2023 | ECO4 | GBP6.80 | 8 | OK (exempt) | GBP156 |
| 2024 | ECO4 | GBP6.80 | 8 | OK (exempt) | GBP137 |
| 2025 | ECO4 | GBP6.80 | 7 | OK (exempt) | GBP58 |

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
| 2023 | 23 | 219g/kWh | 5.0 | 2 | 0.4 | 5.4 | 59% (decarbonising) |
| 2024 | 20 | 196g/kWh | 3.9 | 2 | 0.4 | 4.3 | 64% (decarbonising) |
| 2025 | 9 | 175g/kWh | 1.5 | 1 | 0.2 | 1.7 | 68% (decarbonising) |
| **Total** | | | | | | **30.6 t** | |

> Grid emission intensity declining: 2016 ~290g/kWh -> 2025 ~175g/kWh (40% reduction). Carbon disclosure per SECR/ESOS.
## Risk Committee Activity (2016-2025)

Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.

| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |
|------|----------|----------------------|----------------------|-----------------|
| 2016 | 13 | £28 | £9 | 1 |
| 2017 | 12 | £1,005 | £401 | 3 |
| 2022 | 9 | £55,831 | £20,646 | 8 |
| 2023 | 4 | £128,843 | £49,108 | 8 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £128,843 | Unique accounts ever adjusted: 11

**Most frequently adjusted accounts:**
- C1: 22 sessions
- C7: 19 sessions
- C5: 12 sessions
- C6: 12 sessions
- C8: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £9,974.69 | Median churn: 29% | Total portfolio CLV: £7,281,749.29

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £3,089,743.99 | 17% | 15.2 periods |
| C_IC4 | £1,505,696.97 | 20% | 12.0 periods |
| C6 | £19,419.26 | 23% | 13.1 periods |
| C9 | £9,974.69 | 26% | 13.8 periods |

Quadrant CLV: £4,624,834.90 (64% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC1 | £1,649,043.98 | 29% | 12.8 periods |
| C_IC2 | £960,267.62 | 32% | 14.2 periods |
| C5 | £10,574.38 | 32% | 13.8 periods |

Quadrant CLV: £2,619,885.98 (36% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C3 | £5,445.34 | 11% | 11.7 periods |
| C1 | £4,512.17 | 11% | 13.9 periods |

Quadrant CLV: £9,957.51 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £8,821.40 | 35% | 11.5 periods |
| C7 | £8,048.63 | 29% | 13.0 periods |
| C2 | £6,172.37 | 38% | 13.1 periods |
| C4 | £4,028.50 | 38% | 13.4 periods |

Quadrant CLV: £27,070.90 (0% of portfolio)

**Board action: CRITICAL quadrant has 3 account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**

## Customer Experience & Service Quality

| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |
|------|----------------|---------------|-------------|---------|------|
| 2016 | 0.792 | 0.059 | 0 | 0 | **LOW CLARITY** |
| 2017 | 0.785 | 0.057 | 0 | 0 | **LOW CLARITY** |
| 2018 | 0.755 | 0.064 | 0 | 0 | **LOW CLARITY** |
| 2019 | 0.793 | 0.057 | 0 | 0 | **LOW CLARITY** |
| 2020 | 0.794 | 0.055 | 2 | 0 | **LOW CLARITY** |
| 2021 | 0.809 | 0.052 | 1 | 0 |  |
| 2022 | 0.778 | 0.061 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.782 | 0.058 | 0 | 0 | **LOW CLARITY** |
| 2024 | 0.811 | 0.049 | 1 | 0 |  |
| 2025 | 0.790 | 0.058 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 88.6% | **Average billing clarity:** 0.789 | **Average complaint probability:** 0.057

**Acquisition performance:** 4 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2018** (0.755) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

## Bill Shock Analysis

Bill shock events occur when a customer's bill increases >20% vs the prior bill.
Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.

| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |
|------|------------|--------|-------|------------|------|
| 2016 | 29.6% | 38 | 108 | 35% | ELEVATED |
| 2017 | 26.1% | 68 | 168 | 40% | ELEVATED |
| 2018 | 36.5% | 83 | 180 | 46% | **HIGH** |
| 2019 | 24.1% | 76 | 204 | 37% | ELEVATED |
| 2020 | 23.9% | 74 | 204 | 36% | ELEVATED |
| 2021 | 20.8% | 58 | 180 | 32% | ELEVATED |
| 2022 | 26.3% | 65 | 156 | 42% | ELEVATED |
| 2023 | 25.0% | 55 | 156 | 35% | ELEVATED |
| 2024 | 18.5% | 42 | 147 | 29% |  |
| 2025 | 26.0% | 25 | 72 | 35% | ELEVATED |

**Crisis peak: 2018** — 36.5% average shock. Energy crisis drove wholesale costs above locked tariff rates,
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
| 2020 | £238,631.33 | £35,390.24 | £69,453.10 | £56,548.67 | £70,022.20 | £470,045.54 | £124,575.82 |
| 2021 | £246,108.36 | £14,973.54 | £71,202.78 | £49,550.60 | £62,680.49 | £485,842.71 | £122,583.77 |
| 2022 | £255,908.79 | **£-49,679.48** | £70,920.22 | £36,635.80 | £69,028.88 | £482,173.16 | £132,748.21 |
| 2023 | £271,480.77 | £64,675.57 | £71,701.96 | £50,895.52 | £74,994.50 | £547,479.43 | £138,434.21 |
| 2024 | £307,208.77 | £109,780.54 | £72,815.13 | £68,616.10 | £82,450.11 | £642,866.67 | £142,511.08 |
| 2025 | £135,499.26 | £46,870.81 | £31,155.87 | £30,977.35 | £36,090.53 | £281,446.01 | £60,868.64 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.00 (2016) → £281,446.01 (2025). CAGR: 76.4%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £962.54 | £324.29 | £9,028.87 | £1,388.28 | 13.3% | YES |
| 2017 | £30,879.02 | £516.54 | £231,615.36 | £2,660.42 | 1.1% | YES |
| 2018 | £101,362.51 | £437.73 | £432,322.78 | £3,114.73 | 0.7% | YES |
| 2019 | £223,503.00 | £10,492.12 | £1,060,517.20 | £137,768.61 | 11.5% | YES |
| 2020 | £117,859.96 | £10,489.74 | £1,102,238.84 | £121,126.13 | 9.9% | YES |
| 2021 | £68,417.78 | £9,871.60 | £1,439,533.10 | £297,851.59 | 17.1% | YES |
| 2022 | £331,170.84 | £8,742.40 | £2,848,531.85 | £589,446.82 | 17.1% | YES |
| 2023 | £91,320.50 | £9,017.61 | £2,248,552.03 | £298,695.19 | 11.7% | YES |
| 2024 | £357,730.84 | £10,741.47 | £1,935,979.93 | £272,024.84 | 12.3% | YES |
| 2025 | £116,827.98 | £4,581.34 | £837,239.45 | £133,763.95 | 13.8% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £185,271.29 | — | Current strategy |
| EXIT_GAS | £72,428.15 | £-112,843.14 | Remove gas; model elec churn risk |
| REPRICE_GAS | £186,910.33 | £1,639.04 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-1,639.04 | -10.53x | +14.1% |

**Accretive gas accounts:** C1g (£710.49), C2g (£1,294.49), C3g (£337.93), C_IC3g (£64,510.98) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £65215 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,697,283.51 | £50,064.13 | £1,432,135.54 | 28.6x | Strong |
| I&C gas | £622,647.03 | £0.00 | £64,510.98 | 0.0x | Low return |
| SME electricity | £30,618.75 | £326.81 | £1,968.71 | 6.0x | Moderate |
| resi electricity | £50,337.43 | £545.00 | £5,930.71 | 10.9x | Moderate |
| resi gas | £7,815.28 | £295.62 | £703.87 | 2.4x | Low return |

## Portfolio Concentration Risk

Revenue concentration analysis across 18 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2250** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,302,838.22 (98.7% of total positive margin)
- resi: £53,569.74 (0.8% of total positive margin)
- SME: £29,059.11 (0.5% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,870,779.01 | 29.3% | 3% | £60,426.16 |
| C_IC3 | I&C | £1,803,198.72 | 28.2% | 8% | £151,649.01 |
| C_IC4 | I&C | £1,103,966.75 | 17.3% | 0% | £0.00 |
| C_IC2 | I&C | £905,465.88 | 14.2% | 4% | £33,230.60 |
| C_IC3g | I&C | £619,427.85 | 9.7% | 0% | £0.00 |

**Concentration Risk Warning:**
- I&C segment accounts for 98.7% of total portfolio margin
- Resi and SME segments are effectively margin-neutral at portfolio scale
- A single large I&C departure would remove 14-29% of all margin
- Board action: diversify acquisition pipeline toward profitable resi/SME to reduce I&C dependency

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 116 renewal(s) (31 gas) based on recent portfolio-wide margin rates: 62 surcharge(s), 54 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | 7.2% | +0.4% | £131.49/MWh | £132.04/MWh |
| C1g | gas | 2016-12-31 | 19.6% | -5.0% | £27.63/MWh | £26.25/MWh |
| C5 | electricity | 2016-12-31 | 8.7% | -0.4% | £131.49/MWh | £131.01/MWh |
| C7 | electricity | 2016-12-31 | 9.4% | -0.7% | £131.49/MWh | £130.57/MWh |
| C2 | electricity | 2017-04-01 | 11.8% | -1.9% | £127.97/MWh | £125.57/MWh |
| C2g | gas | 2017-04-01 | 19.8% | -5.0% | £34.54/MWh | £32.81/MWh |
| C6 | electricity | 2017-04-01 | 10.7% | -1.3% | £127.97/MWh | £126.27/MWh |
| C8 | electricity | 2017-04-01 | 9.8% | -0.9% | £127.97/MWh | £126.80/MWh |
| C3 | electricity | 2017-07-01 | 11.1% | -1.6% | £122.23/MWh | £120.31/MWh |
| C3g | gas | 2017-07-01 | 20.5% | -5.0% | £24.33/MWh | £23.11/MWh |
| C9 | electricity | 2017-07-01 | 10.8% | -1.4% | £122.23/MWh | £120.51/MWh |
| C4 | electricity | 2017-10-01 | 10.8% | -1.4% | £111.62/MWh | £110.06/MWh |
| C4g | gas | 2017-10-01 | 18.4% | -5.0% | £27.48/MWh | £26.10/MWh |
| C1 | electricity | 2017-12-31 | 11.5% | -1.8% | £120.10/MWh | £117.98/MWh |
| C1g | gas | 2017-12-31 | 15.4% | -3.7% | £34.79/MWh | £33.49/MWh |
| C5 | electricity | 2017-12-31 | 8.8% | -0.4% | £120.10/MWh | £119.60/MWh |
| C7 | electricity | 2017-12-31 | 3.6% | +2.2% | £120.10/MWh | £122.73/MWh |
| C_IC1 | electricity | 2018-01-31 | -18.2% | +13.1% | £112.24/MWh | £126.98/MWh |
| C2 | electricity | 2018-04-01 | -7.0% | +7.5% | £133.89/MWh | £143.93/MWh |
| C2g | gas | 2018-04-01 | 15.4% | -3.7% | £38.21/MWh | £36.79/MWh |
| C6 | electricity | 2018-04-01 | -4.4% | +6.2% | £133.89/MWh | £142.19/MWh |
| C8 | electricity | 2018-04-01 | 8.1% | -0.1% | £133.89/MWh | £133.81/MWh |
| C3 | electricity | 2018-07-01 | 10.2% | -1.1% | £128.29/MWh | £126.89/MWh |
| C3g | gas | 2018-07-01 | 13.3% | -2.6% | £29.63/MWh | £28.84/MWh |
| C9 | electricity | 2018-07-01 | 1.8% | +3.1% | £128.29/MWh | £132.25/MWh |
| C4 | electricity | 2018-10-01 | 2.0% | +3.0% | £145.00/MWh | £149.37/MWh |
| C4g | gas | 2018-10-01 | 13.5% | -2.7% | £34.60/MWh | £33.65/MWh |
| C1 | electricity | 2018-12-31 | 6.3% | +0.8% | £148.68/MWh | £149.91/MWh |
| C1g | gas | 2018-12-31 | 13.7% | -2.9% | £37.15/MWh | £36.09/MWh |
| C5 | electricity | 2018-12-31 | 9.2% | -0.6% | £148.68/MWh | £147.76/MWh |
| C7 | electricity | 2018-12-31 | 9.6% | -0.8% | £148.68/MWh | £147.49/MWh |
| C_IC2 | electricity | 2019-01-31 | -30.2% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -20.5% | +14.2% | £128.22/MWh | £146.50/MWh |
| C2 | electricity | 2019-04-01 | 3.2% | +2.4% | £148.35/MWh | £151.90/MWh |
| C2g | gas | 2019-04-01 | 10.5% | -1.2% | £32.94/MWh | £32.53/MWh |
| C6 | electricity | 2019-04-01 | 7.5% | +0.2% | £148.35/MWh | £148.71/MWh |
| C8 | electricity | 2019-04-01 | 27.0% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 19.5% | -5.0% | £127.03/MWh | £120.68/MWh |
| C3g | gas | 2019-07-01 | 13.0% | -2.5% | £23.62/MWh | £23.03/MWh |
| C9 | electricity | 2019-07-01 | 9.0% | -0.5% | £127.03/MWh | £126.38/MWh |
| C4 | electricity | 2019-10-01 | 7.0% | +0.5% | £126.72/MWh | £127.33/MWh |
| C4g | gas | 2019-10-01 | 17.0% | -4.5% | £20.41/MWh | £19.49/MWh |
| C1 | electricity | 2019-12-31 | 9.4% | -0.7% | £127.44/MWh | £126.53/MWh |
| C1g | gas | 2019-12-31 | 14.2% | -3.1% | £26.17/MWh | £25.36/MWh |
| C5 | electricity | 2019-12-31 | 9.4% | -0.7% | £127.44/MWh | £126.54/MWh |
| C7 | electricity | 2019-12-31 | 9.3% | -0.6% | £127.44/MWh | £126.63/MWh |
| C_IC3 | electricity | 2020-01-01 | 7.4% | +0.3% | £47.59/MWh | £47.72/MWh |
| C_IC3g | gas | 2020-01-01 | 20.6% | -5.0% | £16.25/MWh | £15.44/MWh |
| C_IC2 | electricity | 2020-03-01 | -59.4% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -52.0% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 18.8% | -5.0% | £22.80/MWh | £21.66/MWh |
| C6 | electricity | 2020-03-31 | -47.3% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -16.2% | +12.1% | £125.12/MWh | £140.28/MWh |
| C_IC1 | electricity | 2020-03-31 | 18.7% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 15.2% | -3.6% | £113.43/MWh | £109.37/MWh |
| C9 | electricity | 2020-06-30 | 15.2% | -3.6% | £113.43/MWh | £109.37/MWh |
| C4 | electricity | 2020-09-30 | 9.9% | -1.0% | £124.42/MWh | £123.23/MWh |
| C4g | gas | 2020-09-30 | 20.4% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 8.3% | -0.2% | £133.55/MWh | £133.34/MWh |
| C1g | gas | 2020-12-30 | 14.3% | -3.2% | £28.99/MWh | £28.07/MWh |
| C5 | electricity | 2020-12-30 | 5.1% | +1.5% | £133.55/MWh | £135.50/MWh |
| C7 | electricity | 2020-12-30 | 5.1% | +1.5% | £133.55/MWh | £135.50/MWh |
| C_IC3 | electricity | 2020-12-31 | -2.4% | +5.2% | £50.65/MWh | £53.28/MWh |
| C_IC3g | gas | 2020-12-31 | 7.4% | +0.3% | £20.05/MWh | £20.11/MWh |
| C2 | electricity | 2021-03-31 | -22.4% | +15.0% | £175.90/MWh | £202.28/MWh |
| C2g | gas | 2021-03-31 | 6.1% | +0.9% | £36.20/MWh | £36.54/MWh |
| C6 | electricity | 2021-03-31 | -16.2% | +12.1% | £175.90/MWh | £197.19/MWh |
| C8 | electricity | 2021-03-31 | -11.8% | +9.9% | £175.90/MWh | £193.36/MWh |
| C_IC2 | electricity | 2021-03-31 | -7.3% | +7.6% | £138.90/MWh | £149.51/MWh |
| C_IC1 | electricity | 2021-04-30 | -1.7% | +4.8% | £113.97/MWh | £119.47/MWh |
| C9 | electricity | 2021-06-30 | -1.2% | +4.6% | £170.38/MWh | £178.25/MWh |
| C4 | electricity | 2021-09-30 | -1.8% | +4.9% | £205.15/MWh | £215.17/MWh |
| C4g | gas | 2021-09-30 | 0.1% | +4.0% | £53.99/MWh | £56.12/MWh |
| C1 | electricity | 2021-12-30 | 5.1% | +1.4% | £311.83/MWh | £316.27/MWh |
| C7 | electricity | 2021-12-30 | 5.1% | +1.4% | £311.83/MWh | £316.27/MWh |
| C_IC3 | electricity | 2021-12-31 | -23.7% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -18.1% | +13.0% | £109.48/MWh | £123.75/MWh |
| C2 | electricity | 2022-03-31 | -24.4% | +15.0% | £361.95/MWh | £416.24/MWh |
| C2g | gas | 2022-03-31 | -19.1% | +13.6% | £99.49/MWh | £112.98/MWh |
| C6 | electricity | 2022-03-31 | -20.6% | +14.3% | £361.95/MWh | £413.77/MWh |
| C8 | electricity | 2022-03-31 | 2.6% | +2.7% | £361.95/MWh | £371.62/MWh |
| C_IC2 | electricity | 2022-04-30 | -9.1% | +8.6% | £269.81/MWh | £292.92/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.1% | +7.1% | £239.42/MWh | £256.31/MWh |
| C9 | electricity | 2022-06-30 | 4.2% | +1.9% | £255.09/MWh | £259.90/MWh |
| C4 | electricity | 2022-09-30 | 7.1% | +0.4% | £404.86/MWh | £406.63/MWh |
| C4g | gas | 2022-09-30 | -24.3% | +15.0% | £183.79/MWh | £211.36/MWh |
| C7 | electricity | 2022-12-30 | 8.5% | -0.2% | £266.73/MWh | £266.13/MWh |
| C_IC3 | electricity | 2022-12-31 | -0.6% | +4.3% | £168.36/MWh | £175.62/MWh |
| C_IC3g | gas | 2022-12-31 | -43.9% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2 | electricity | 2023-03-31 | -12.7% | +10.4% | £319.17/MWh | £352.24/MWh |
| C2g | gas | 2023-03-31 | -22.3% | +15.0% | £83.68/MWh | £96.23/MWh |
| C6 | electricity | 2023-03-31 | -5.2% | +6.6% | £319.17/MWh | £340.22/MWh |
| C8 | electricity | 2023-03-31 | 2.5% | +2.8% | £319.17/MWh | £328.03/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.1% | +14.6% | £171.46/MWh | £196.41/MWh |
| C_IC1 | electricity | 2023-06-29 | -16.7% | +12.3% | £163.19/MWh | £183.33/MWh |
| C9 | electricity | 2023-06-30 | -10.5% | +9.2% | £224.44/MWh | £245.20/MWh |
| C4 | electricity | 2023-09-30 | 9.5% | -0.8% | £216.77/MWh | £215.12/MWh |
| C4g | gas | 2023-09-30 | -19.1% | +13.5% | £47.83/MWh | £54.30/MWh |
| C7 | electricity | 2023-12-30 | 27.3% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 21.9% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -7.8% | +7.9% | £51.89/MWh | £56.00/MWh |
| C2 | electricity | 2024-03-30 | 14.4% | -3.2% | £207.71/MWh | £201.02/MWh |
| C2g | gas | 2024-03-30 | 11.6% | -1.8% | £49.31/MWh | £48.41/MWh |
| C6 | electricity | 2024-03-30 | 13.0% | -2.5% | £207.71/MWh | £202.53/MWh |
| C8 | electricity | 2024-03-30 | 13.0% | -2.5% | £207.71/MWh | £202.53/MWh |
| C_IC2 | electricity | 2024-06-28 | -31.1% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.5% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C4g | gas | 2024-09-29 | 16.2% | -4.1% | £50.11/MWh | £48.05/MWh |
| C7 | electricity | 2024-12-29 | 22.1% | -5.0% | £243.79/MWh | £231.60/MWh |
| C_IC3 | electricity | 2024-12-30 | 13.8% | -2.9% | £116.37/MWh | £112.99/MWh |
| C_IC3g | gas | 2024-12-30 | 13.6% | -2.8% | £50.47/MWh | £49.06/MWh |
| C2 | electricity | 2025-03-30 | 4.2% | +1.9% | £284.89/MWh | £290.27/MWh |
| C2g | gas | 2025-03-30 | 7.5% | +0.2% | £71.57/MWh | £71.73/MWh |
| C8 | electricity | 2025-03-30 | 1.2% | +3.4% | £284.89/MWh | £294.54/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **4** | Blind misses: **4** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 0 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £4,804.29 | deliberate: £0.00 | total: £4,804.29

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.10 | 0.04 | No | £590.77 |
| C5 | 2020-12-30 | Blind miss | 0.08 | 0.27 | No | £1,613.98 |
| C1 | 2021-12-30 | Blind miss | 0.06 | 0.04 | No | £-178.13 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.13 | No | £2,777.67 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £118,085.00 | £64,510.98 | £182,595.98 | Yes |
| C2+C2g | £1,177.92 | £1,294.49 | £2,472.41 | Yes |
| C1+C1g | £457.78 | £710.49 | £1,168.27 | Yes |
| C3+C3g | £-121.36 | £337.93 | £216.58 | Yes |
| C4+C4g | £457.10 | £-1,639.04 | £-1,181.94 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £65,214.85.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,505,249.80 across 18 billing accounts. Revenue: £14,003,399.99.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,124,138.53 | £1,874,997.13 | £18,431.58 | £846,745.95 | 27.1% |
| 2 | C_IC2 | fixed | £1,524,795.72 | £909,184.06 | £8,614.20 | £435,083.94 | 28.5% |
| 3 | C_IC3 | pass_through | £4,612,268.10 | £1,806,417.04 | £23,018.35 | £118,085.00 | 2.6% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £64,510.98 | 3.5% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £32,220.65 | 1.2% |
| 6 | C9 | fixed | £20,284.62 | £12,748.05 | £131.67 | £2,279.57 | 11.2% |
| 7 | C8 | fixed | £21,633.98 | £12,414.64 | £134.50 | £2,276.47 | 10.5% |
| 8 | C6 | fixed | £39,263.44 | £22,780.14 | £266.71 | £2,142.14 | 5.5% |
| 9 | C2g | fixed | £8,092.62 | £3,287.07 | £105.86 | £1,294.49 | 16.0% |
| 10 | C2 | fixed | £9,516.49 | £5,523.53 | £58.29 | £1,177.92 | 12.4% |
| 11 | C1g | fixed | £2,894.78 | £1,541.50 | £18.80 | £710.49 | 24.5% |
| 12 | C1 | fixed | £4,290.21 | £2,801.12 | £19.82 | £457.78 | 10.7% |
| 13 | C4 | fixed | £6,895.81 | £3,735.27 | £45.05 | £457.10 | 6.6% |
| 14 | C3g | fixed | £2,684.78 | £1,300.00 | £15.29 | £337.93 | 12.6% |
| 15 | C3 | fixed | £3,625.39 | £2,385.53 | £14.75 | £-121.36 | -3.3% |
| 16 | C5 | fixed | £12,505.04 | £7,838.61 | £60.09 | £-173.43 | -1.4% |
| 17 | C7 | fixed | £21,703.21 | £10,729.29 | £140.93 | £-596.77 | -2.7% |
| 18 | C4g | fixed | £11,588.49 | £1,686.71 | £155.67 | £-1,639.04 | -14.1% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,003,400 | 100.0% |
| Wholesale cost | -£7,594,698 | 54.2% |
| **Gross supply margin** | **£6,408,702** | **45.8%** |
| Policy + Network costs | -£4,852,221 | 34.7% |
| Capital cost | -£51,232 | 0.4% |
| **Net supply margin** | **£1,505,250** | **10.7%** |

> *The ledger's `net_margin_gbp` (£6,404,097) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,005,841 | 47.5% | 11.9% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 3.5% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £51,768 | 59.1% | 3.8% | CMA 3-8% | ✓ |
| resi/elec | £87,950 | 57.2% | 6.7% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £25,261 | 30.9% | 2.8% | Ofgem CMA 2-4% | ✓ |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: PASS** — all segments within benchmarks.
## Transaction Log

Total events: 3,287,387

| Event type | Count |
|------------|-------|
| acquisition_gate_event | 1 |
| acquisition_spend_event | 3 |
| back_billing_write_off_event | 1 |
| bad_debt_event | 1,550 |
| billing_event | 1,574 |
| capital_charge_event | 1,581,418 |
| cost_to_serve_event | 114 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,574 |
| payment_received_event | 1,574 |
| revenue_restatement_event | 150 |
| settlement_event | 1,697,740 |
| vat_remittance_event | 1,574 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £22,585,653.32 |
|   Less: VAT remitted to HMRC | (£3,744,561.07) |
| = Revenue (ex-VAT) | £18,841,092.24 |
| Less: non-commodity pass-through | (£4,791,065.52) |
| Wholesale cost (settlement events) | (£7,594,697.99) |
| Gross margin | £6,455,328.74 |
| Capital charges | (£51,231.56) |
| Net margin | £6,404,097.18 |

_Cash reconciliation: of £22,585,653.32 billed, bad debt of £451,915.46 was written off, leaving £22,133,851.44 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £9,696,856.38._

| Acquisition spend | (£750.00) |
| Fixed overhead | (£5,700.00) |
| Cost to serve | (£23,234.94) |
| Operating net margin | £6,374,412.24 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £16,206.51 | £3,594.97 | £4,363.77 | £8,247.77 | £262.70 | £1,474.07 | £6,687.37 (41.3%) |
| 2017 | £347,687.40 | £111,055.45 | £112,416.49 | £124,215.46 | £7,034.86 | £8,979.73 | £113,962.28 (32.8%) |
| 2018 | £600,267.18 | £172,874.18 | £164,071.67 | £263,321.33 | £13,404.07 | £15,848.61 | £245,850.18 (41.0%) |
| 2019 | £1,642,336.67 | £496,238.33 | £443,205.99 | £702,892.35 | £34,976.86 | £38,421.01 | £662,161.80 (40.3%) |
| 2020 | £1,858,681.90 | £431,611.43 | £629,411.89 | £797,658.59 | £43,690.00 | £48,037.46 | £747,658.77 (40.2%) |
| 2021 | £2,416,543.72 | £971,915.14 | £680,773.88 | £763,854.71 | £53,603.16 | £57,317.14 | £700,905.35 (29.0%) |
| 2022 | £4,239,425.11 | £2,387,110.02 | £799,720.68 | £1,052,594.41 | £96,328.44 | £99,932.62 | £939,403.46 (22.2%) |
| 2023 | £3,430,212.81 | £1,638,242.36 | £875,288.61 | £916,681.84 | £86,195.60 | £89,799.51 | £817,121.88 (23.8%) |
| 2024 | £3,016,002.29 | £931,171.08 | £811,332.71 | £1,273,498.51 | £73,305.90 | £77,127.80 | £1,186,706.28 (39.3%) |
| 2025 | £1,285,112.20 | £452,201.01 | £270,479.84 | £562,431.34 | £43,113.87 | £44,662.46 | £512,106.97 (39.8%) |
| **Total** | **£18,852,475.80** | | | | | | **£5,932,564.35 (31.5%)** |

**Best year:** 2024 — net £1,186,706.28 (39.3% margin)
**Worst year:** 2016 — net £6,687.37 (41.3% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,399,086.98 |
| Trade Receivables | £113.59 |
| **Total Assets** | **£8,399,200.57** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,932,564.35 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £16,206.51 | +10.5% | £6,592.99 | £6,687.37 | +1.4% | GREEN |
| 2017 | £16,138.86 | £347,687.40 | +2054.3% | £7,252.29 | £113,962.28 | +1471.4% | RED |
| 2018 | £386,623.75 | £600,267.18 | +55.3% | £128,424.00 | £245,850.18 | +91.4% | RED |
| 2019 | £675,851.95 | £1,642,336.67 | +143.0% | £281,335.50 | £662,161.80 | +135.4% | RED |
| 2020 | £1,816,630.04 | £1,858,681.90 | +2.3% | £736,963.94 | £747,658.77 | +1.5% | GREEN |
| 2021 | £2,028,952.42 | £2,416,543.72 | +19.1% | £833,649.22 | £700,905.35 | -15.9% | RED |
| 2022 | £2,607,611.88 | £4,239,425.11 | +62.6% | £790,935.58 | £939,403.46 | +18.8% | RED |
| 2023 | £4,508,414.67 | £3,430,212.81 | -23.9% | £1,029,561.00 | £817,121.88 | -20.6% | RED |
| 2024 | £3,512,844.39 | £3,016,002.29 | -14.1% | £893,105.75 | £1,186,706.28 | +32.9% | RED |
| 2025 | £3,145,356.42 | £1,285,112.20 | -59.1% | £1,315,150.33 | £512,106.97 | -61.1% | RED |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 2 | 0 | 0% | £450.00 |
| 2021 | 1 | 0 | 0% | £0.00 |
| 2024 | 1 | 0 | 0% | £300.00 |

**Total:** 4 attempts, 0 wins (0% win rate), £750.00 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,397,647.18

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
- Average CLV (Point-in-Time, year-end 2016): £8,979.16
  - By billing account: C1 £5,148.47, C5 £12,587.98, C7 £9,201.03
- Bill shock events (>=20%): 38 -- C1 2016-04-30 (21%); C1g 2016-05-31 (42%); C1g 2016-06-30 (35%); C1g 2016-10-31 (107%); C1g 2016-11-30 (55%); C5 2016-05-31 (25%); C5 2016-06-30 (75%); C5 2016-07-31 (122%); C5 2016-08-31 (133%); C5 2016-09-30 (135%); C5 2016-10-31 (125%); C5 2016-11-30 (56%); C7 2016-04-30 (22%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-11-30 (99%); C2g 2016-05-31 (39%); C2g 2016-06-30 (39%); C2g 2016-10-31 (102%); C2g 2016-11-30 (60%); C6 2016-06-30 (37%); C6 2016-07-31 (80%); C6 2016-08-31 (87%); C6 2016-09-30 (97%); C6 2016-10-31 (80%); C6 2016-11-30 (26%); C8 2016-05-31 (41%); C8 2016-06-30 (43%); C8 2016-09-30 (25%); C8 2016-10-31 (111%); C8 2016-11-30 (72%); C3g 2016-10-31 (84%); C3g 2016-11-30 (53%); C9 2016-09-30 (20%); C9 2016-10-31 (80%); C9 2016-11-30 (61%); C4 2016-11-30 (36%); C4g 2016-11-30 (50%)
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
- Bills issued: 108, average clarity 0.792, average bill shock 29.6%, bad debt provision £66.56, avg complaint probability 5.9%
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

- Net margin: £31,395.56 (gross £123,220.33, capital £1,273.45)
  - Electricity: gross £121,790.76, capital £1,258.60, net £30,879.02
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
- Worst single period: C5 on 2017-12-31 period 48, net margin £-327.36

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £11,364.70
  - By billing account: C1 £5,231.67, C2 £10,444.03, C3 £8,807.25, C4 £8,105.00, C5 £12,043.37, C6 £23,950.54, C7 £8,859.83, C8 £13,645.68, C9 £11,194.96
- Bill shock events (>=20%): 68 -- C1 2017-04-30 (21%); C1 2017-12-31 (24%); C1g 2017-05-31 (34%); C1g 2017-06-30 (36%); C1g 2017-10-31 (48%); C1g 2017-11-30 (87%); C1g 2017-12-31 (21%); C5 2017-02-28 (281%); C5 2017-04-30 (28%); C5 2017-05-31 (21%); C5 2017-06-30 (27%); C5 2017-07-31 (64%); C5 2017-08-31 (69%); C5 2017-09-30 (65%); C5 2017-10-31 (43%); C5 2017-11-30 (25%); C5 2017-12-31 (21%); C7 2017-01-31 (34%); C7 2017-02-28 (28%); C7 2017-05-31 (68%); C7 2017-06-30 (33%); C7 2017-09-30 (28%); C7 2017-10-31 (22%); C7 2017-11-30 (78%); C2g 2017-04-30 (29%); C2g 2017-05-31 (61%); C2g 2017-06-30 (54%); C2g 2017-07-31 (144%); C2g 2017-09-30 (34%); C2g 2017-10-31 (20%); C2g 2017-11-30 (108%); C2g 2017-12-31 (23%); C6 2017-05-31 (204%); C6 2017-06-30 (23%); C6 2017-07-31 (55%); C6 2017-08-31 (67%); C6 2017-09-30 (159%); C6 2017-10-31 (23%); C6 2017-12-31 (28%); C8 2017-05-31 (40%); C8 2017-06-30 (37%); C8 2017-09-30 (48%); C8 2017-10-31 (23%); C8 2017-11-30 (85%); C8 2017-12-31 (22%); C3 2017-12-31 (23%); C3g 2017-05-31 (33%); C3g 2017-06-30 (25%); C3g 2017-10-31 (24%); C3g 2017-11-30 (37%); C3g 2017-12-31 (62%); C9 2017-05-31 (33%); C9 2017-06-30 (27%); C9 2017-10-31 (23%); C9 2017-11-30 (129%); C9 2017-12-31 (42%); C4 2017-04-30 (33%); C4 2017-09-30 (28%); C4 2017-10-31 (30%); C4 2017-12-31 (45%); C4g 2017-01-31 (24%); C4g 2017-02-28 (22%); C4g 2017-05-31 (62%); C4g 2017-06-30 (50%); C4g 2017-07-31 (158%); C4g 2017-09-30 (42%); C4g 2017-10-31 (24%); C4g 2017-12-31 (75%)
- Churn risk (accounts renewing in 2017): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £92.70-£198.06/MWh, net margin £80.47
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £115.22
- C2 (electricity): tariff £84.56-£188.36/MWh, net margin £110.01
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £194.46
- C3 (electricity): tariff £98.21-£120.31/MWh, net margin £-26.99 -- **net-negative**
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £69.89
- C4 (electricity): tariff £77.34-£165.09/MWh, net margin £49.80
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £136.97
- C5 (electricity): tariff £119.60-£131.01/MWh, net margin £-162.66 -- **net-negative**
- C6 (electricity): tariff £107.62-£126.27/MWh, net margin £88.56
- C7 (electricity): tariff £96.43-£195.85/MWh, net margin £194.36
- C8 (electricity): tariff £84.56-£190.20/MWh, net margin £241.98
- C9 (electricity): tariff £77.16-£180.77/MWh, net margin £163.56
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £30,139.92

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.785, average bill shock 26.1%, bad debt provision £529.54, avg complaint probability 5.7%
- Solvency signal: £249,892/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,075.49 vs. naked (unhedged) net margin: £112,479.99
- hedging cost £82,404.50 vs. a fully unhedged book (commodity-only: actual net £30,075.49 vs. naked net £112,479.99)
  - C1: actual £23.00 vs. naked £341.73 -- hedging cost £318.73
  - C1g: actual £131.41 vs. naked £272.27 -- hedging cost £140.86
  - C2: actual £103.00 vs. naked £442.11 -- hedging cost £339.11
  - C2g: actual £207.48 vs. naked £448.25 -- hedging cost £240.78
  - C3: actual £110.96 vs. naked £513.38 -- hedging cost £402.41
  - C3g: actual £30.62 vs. naked £394.35 -- hedging cost £363.73
  - C4: actual £33.30 vs. naked £272.21 -- hedging cost £238.91
  - C4g: actual £44.94 vs. naked £544.66 -- hedging cost £499.72
  - C5: actual £-206.89 vs. naked £1,069.24 -- hedging cost £1,276.13
  - C6: actual £104.65 vs. naked £1,675.83 -- hedging cost £1,571.18
  - C7: actual £-51.02 vs. naked £820.80 -- hedging cost £871.81
  - C8: actual £254.62 vs. naked £990.30 -- hedging cost £735.68
  - C9: actual £242.03 vs. naked £951.76 -- hedging cost £709.73
  - C_IC1: actual £29,047.38 vs. naked £103,743.08 -- hedging cost £74,695.71

**Year narrative:** 2017 produced a net gain of £31,395.56 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 68 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £101,800.24 (gross £262,574.28, capital £1,622.55)
  - Electricity: gross £261,210.68, capital £1,601.48, net £101,362.51
  - Gas: gross £1,363.60, capital £21.07, net £437.73
- Treasury at year end: £2,487,679.94
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.91 (avg 0.91), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.92 (avg 0.92)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2018-12-31 period 48, net margin £-234.97

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £274,071.77
  - By billing account: C1 £4,931.67, C2 £7,734.77, C3 £7,536.37, C4 £6,553.41, C5 £12,087.51, C6 £18,135.42, C7 £7,810.19, C8 £10,311.41, C9 £9,920.64, C_IC1 £2,655,696.32
- Bill shock events (>=20%): 83 -- C1g 2018-04-30 (40%); C1g 2018-05-31 (33%); C1g 2018-06-30 (35%); C1g 2018-09-30 (34%); C1g 2018-10-31 (56%); C1g 2018-11-30 (31%); C5 2018-01-31 (35%); C5 2018-02-28 (29%); C5 2018-04-30 (24%); C5 2018-06-30 (39%); C5 2018-07-31 (77%); C5 2018-08-31 (76%); C5 2018-09-30 (74%); C5 2018-10-31 (51%); C7 2018-04-30 (39%); C7 2018-05-31 (40%); C7 2018-06-30 (88%); C7 2018-07-31 (313%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C2 2018-12-31 (23%); C2g 2018-04-30 (29%); C2g 2018-05-31 (37%); C2g 2018-06-30 (38%); C2g 2018-07-31 (73%); C2g 2018-08-31 (92%); C2g 2018-09-30 (92%); C2g 2018-10-31 (51%); C2g 2018-11-30 (21%); C6 2018-01-31 (37%); C6 2018-02-28 (38%); C6 2018-03-31 (36%); C6 2018-04-30 (31%); C6 2018-07-31 (51%); C6 2018-08-31 (56%); C6 2018-09-30 (46%); C6 2018-10-31 (179%); C6 2018-12-31 (29%); C8 2018-05-31 (101%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (56%); C8 2018-11-30 (30%); C3 2018-01-31 (26%); C3 2018-02-28 (26%); C3 2018-03-31 (121%); C3 2018-12-31 (21%); C3g 2018-01-31 (66%); C3g 2018-02-28 (68%); C3g 2018-03-31 (66%); C3g 2018-04-30 (68%); C3g 2018-05-31 (54%); C3g 2018-06-30 (30%); C3g 2018-08-31 (1414%); C3g 2018-09-30 (41%); C3g 2018-11-30 (42%); C3g 2018-12-31 (49%); C9 2018-01-31 (53%); C9 2018-04-30 (32%); C9 2018-05-31 (30%); C9 2018-06-30 (134%); C9 2018-07-31 (23%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-04-30 (32%); C4 2018-09-30 (29%); C4 2018-10-31 (50%); C4 2018-11-30 (33%); C4g 2018-03-31 (21%); C4g 2018-04-30 (37%); C4g 2018-05-31 (36%); C4g 2018-06-30 (151%); C4g 2018-08-31 (23%); C4g 2018-09-30 (45%); C4g 2018-10-31 (94%); C4g 2018-11-30 (26%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C2 23%, C3 23%, C6 23%, C7 20%, C8 23%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £92.70-£224.86/MWh, net margin £37.18
- C1g (gas): tariff £33.49-£36.09/MWh, net margin £142.44
- C2 (electricity): tariff £98.66-£215.89/MWh, net margin £93.30
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £189.04
- C3 (electricity): tariff £120.31-£126.89/MWh, net margin £107.89
- C3g (gas): tariff £23.11-£28.84/MWh, net margin £41.12
- C4 (electricity): tariff £86.47-£224.05/MWh, net margin £66.81
- C4g (gas): tariff £26.10-£33.65/MWh, net margin £65.13
- C5 (electricity): tariff £119.60-£153.53/MWh, net margin £-440.69 -- **net-negative**
- C6 (electricity): tariff £126.27-£142.19/MWh, net margin £-12.25 -- **net-negative**
- C7 (electricity): tariff £96.43-£221.23/MWh, net margin £-15.01 -- **net-negative**
- C8 (electricity): tariff £99.63-£200.71/MWh, net margin £161.36
- C9 (electricity): tariff £94.69-£198.37/MWh, net margin £239.23
- C_IC1 (electricity): tariff £-82.12-£228.56/MWh, net margin £107,475.61
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,350.93 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.755, average bill shock 36.5%, bad debt provision £238.97, avg complaint probability 6.4%
- Solvency signal: £226,153/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £109,555.29 vs. naked (unhedged) net margin: £246,608.66
- hedging cost £137,053.37 vs. a fully unhedged book (commodity-only: actual net £109,555.29 vs. naked net £246,608.66)
  - C1: actual £105.98 vs. naked £575.47 -- hedging cost £469.49
  - C1g: actual £144.83 vs. naked £421.13 -- hedging cost £276.30
  - C2: actual £62.54 vs. naked £503.94 -- hedging cost £441.40
  - C2g: actual £150.65 vs. naked £399.99 -- hedging cost £249.34
  - C3: actual £26.62 vs. naked £557.85 -- hedging cost £531.23
  - C3g: actual £39.76 vs. naked £482.40 -- hedging cost £442.64
  - C4: actual £94.13 vs. naked £459.22 -- hedging cost £365.09
  - C4g: actual £69.51 vs. naked £871.98 -- hedging cost £802.47
  - C5: actual £124.39 vs. naked £1,984.53 -- hedging cost £1,860.14
  - C6: actual £-140.93 vs. naked £1,834.22 -- hedging cost £1,975.15
  - C7: actual £71.47 vs. naked £1,347.48 -- hedging cost £1,276.00
  - C8: actual £24.56 vs. naked £936.87 -- hedging cost £912.31
  - C9: actual £143.70 vs. naked £1,046.02 -- hedging cost £902.32
  - C_IC1: actual £115,490.72 vs. naked £201,741.26 -- hedging cost £86,250.53
  - C_IC2: actual £-6,852.66 vs. naked £33,446.32 -- hedging cost £40,298.97

**Year narrative:** 2018 produced a net gain of £101,800.24 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 83 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £233,995.12 (gross £702,050.52, capital £2,309.54)
  - Electricity: gross £625,994.20, capital £2,288.08, net £223,503.00
  - Gas: gross £76,056.32, capital £21.46, net £10,492.12
- Treasury at year end: £2,611,877.36
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C3 on 2019-12-31 period 48, net margin £-69.44

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £314,631.53
  - By billing account: C1 £4,477.70, C2 £6,355.12, C3 £7,157.54, C4 £6,398.31, C5 £10,449.73, C6 £20,925.73, C7 £7,993.96, C8 £9,755.47, C9 £9,238.95, C_IC1 £2,148,794.77, C_IC2 £1,229,399.52
- Bill shock events (>=20%): 76 -- C1 2019-04-30 (22%); C1g 2019-01-31 (40%); C1g 2019-02-28 (27%); C1g 2019-05-31 (26%); C1g 2019-06-30 (40%); C1g 2019-10-31 (91%); C1g 2019-11-30 (50%); C5 2019-02-28 (32%); C5 2019-04-30 (78%); C5 2019-06-30 (25%); C5 2019-07-31 (70%); C5 2019-08-31 (77%); C5 2019-09-30 (83%); C5 2019-10-31 (66%); C7 2019-01-31 (46%); C7 2019-02-28 (26%); C7 2019-05-31 (24%); C7 2019-06-30 (35%); C7 2019-10-31 (72%); C7 2019-11-30 (46%); C2g 2019-01-31 (27%); C2g 2019-02-28 (27%); C2g 2019-04-30 (37%); C2g 2019-06-30 (35%); C2g 2019-07-31 (30%); C2g 2019-09-30 (40%); C2g 2019-10-31 (76%); C2g 2019-11-30 (31%); C6 2019-01-31 (35%); C6 2019-02-28 (77%); C6 2019-04-30 (21%); C6 2019-07-31 (43%); C6 2019-08-31 (62%); C6 2019-09-30 (64%); C6 2019-10-31 (36%); C6 2019-12-31 (26%); C8 2019-01-31 (28%); C8 2019-02-28 (28%); C8 2019-04-30 (22%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-10-31 (117%); C8 2019-11-30 (38%); C3 2019-01-31 (23%); C3 2019-02-28 (24%); C3 2019-04-30 (23%); C3 2019-09-30 (152%); C3g 2019-01-31 (145%); C3g 2019-02-28 (41%); C3g 2019-04-30 (28%); C3g 2019-07-31 (37%); C3g 2019-08-31 (129%); C3g 2019-09-30 (106%); C3g 2019-10-31 (56%); C3g 2019-11-30 (44%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (68%); C9 2019-07-31 (60%); C9 2019-08-31 (139%); C9 2019-09-30 (53%); C9 2019-11-30 (87%); C4 2019-04-30 (35%); C4 2019-09-30 (33%); C4 2019-12-31 (45%); C4g 2019-01-31 (31%); C4g 2019-02-28 (25%); C4g 2019-05-31 (50%); C4g 2019-06-30 (35%); C4g 2019-07-31 (40%); C4g 2019-09-30 (36%); C4g 2019-10-31 (37%); C4g 2019-11-30 (38%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C1 29%, C4 35%, C5 35%, C7 29%, C9 23%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £99.42-£224.86/MWh, net margin £122.19
- C1g (gas): tariff £25.36-£36.09/MWh, net margin £156.88
- C2 (electricity): tariff £113.09-£227.85/MWh, net margin £145.70
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £134.46
- C3 (electricity): tariff £120.68-£126.89/MWh, net margin £-62.47 -- **net-negative**
- C3g (gas): tariff £23.03-£28.84/MWh, net margin £98.62
- C4 (electricity): tariff £100.05-£224.05/MWh, net margin £106.07
- C4g (gas): tariff £19.49-£33.65/MWh, net margin £102.24
- C5 (electricity): tariff £126.54-£153.53/MWh, net margin £153.26
- C6 (electricity): tariff £142.19-£148.71/MWh, net margin £129.38
- C7 (electricity): tariff £99.50-£221.23/MWh, net margin £111.60
- C8 (electricity): tariff £105.13-£211.40/MWh, net margin £192.93
- C9 (electricity): tariff £99.30-£198.37/MWh, net margin £185.71
- C_IC1 (electricity): tariff £0.00-£263.70/MWh, net margin £139,356.08
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £79,281.83
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £3,780.73
- C_IC3g (gas): tariff £27.53/MWh, net margin £9,999.92

**Portfolio Health**

- Capital cost ratio: 0.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.793, average bill shock 24.1%, bad debt provision £107.39, avg complaint probability 5.7%
- Solvency signal: £217,656/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £252,551.19 vs. naked (unhedged) net margin: £836,879.38
- hedging cost £584,328.18 vs. a fully unhedged book (commodity-only: actual net £252,551.19 vs. naked net £836,879.38)
  - C1: actual £87.94 vs. naked £503.87 -- hedging cost £415.93
  - C1g: actual £137.47 vs. naked £302.77 -- hedging cost £165.30
  - C2: actual £157.71 vs. naked £669.24 -- hedging cost £511.53
  - C2g: actual £87.69 vs. naked £403.54 -- hedging cost £315.85
  - C3: actual £-2.43 vs. naked £668.43 -- hedging cost £670.85
  - C3g: actual £136.36 vs. naked £506.33 -- hedging cost £369.97
  - C4: actual £98.00 vs. naked £443.86 -- hedging cost £345.85
  - C4g: actual £102.10 vs. naked £574.69 -- hedging cost £472.59
  - C5: actual £-19.80 vs. naked £1,597.98 -- hedging cost £1,617.79
  - C6: actual £233.34 vs. naked £2,599.58 -- hedging cost £2,366.24
  - C7: actual £37.45 vs. naked £1,143.65 -- hedging cost £1,106.21
  - C8: actual £240.89 vs. naked £1,370.83 -- hedging cost £1,129.94
  - C9: actual £167.44 vs. naked £1,266.64 -- hedging cost £1,099.21
  - C_IC1: actual £154,845.76 vs. naked £297,973.82 -- hedging cost £143,128.05
  - C_IC2: actual £85,558.69 vs. naked £161,523.27 -- hedging cost £75,964.58
  - C_IC3: actual £1,355.95 vs. naked £289,938.26 -- hedging cost £288,582.30
  - C_IC3g: actual £9,326.63 vs. naked £75,392.62 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £233,995.12 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 76 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £128,349.70 (gross £791,811.19, capital £1,962.36)
  - Electricity: gross £714,628.15, capital £1,951.84, net £117,859.96
  - Gas: gross £77,183.04, capital £10.52, net £10,489.74
- Treasury at year end: £2,923,975.09
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.87 (avg 0.87), C4g 0.85 (avg 0.85), C6 0.86 (avg 0.86), C7 0.89 (avg 0.89), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C3 on 2020-06-29 period 48, net margin £-166.48

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3, C5
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £412,462.82
  - By billing account: C1 £4,055.37, C2 £7,798.11, C3 £6,096.16, C4 £5,051.07, C5 £8,624.52, C6 £15,157.71, C7 £7,269.64, C8 £8,338.10, C9 £9,096.49, C_IC1 £1,142,134.35, C_IC2 £742,862.14, C_IC3 £2,125,002.42, C_IC4 £1,280,530.60
- Bill shock events (>=20%): 74 -- C1 2020-04-30 (22%); C1g 2020-01-31 (22%); C1g 2020-04-30 (35%); C1g 2020-05-31 (22%); C1g 2020-06-30 (30%); C1g 2020-08-31 (27%); C1g 2020-10-31 (71%); C1g 2020-11-30 (20%); C1g 2020-12-31 (40%); C5 2020-01-31 (136%); C5 2020-05-31 (36%); C5 2020-06-30 (61%); C5 2020-07-31 (97%); C5 2020-08-31 (106%); C5 2020-09-30 (110%); C5 2020-10-31 (87%); C5 2020-11-30 (34%); C5 2020-12-29 (319%); C7 2020-05-31 (71%); C7 2020-06-30 (28%); C7 2020-10-31 (75%); C7 2020-11-30 (24%); C7 2020-12-31 (35%); C2 2020-04-30 (25%); C2 2020-12-31 (24%); C2g 2020-04-30 (39%); C2g 2020-05-31 (20%); C2g 2020-06-30 (29%); C2g 2020-09-30 (35%); C2g 2020-10-31 (56%); C2g 2020-12-31 (42%); C6 2020-01-31 (30%); C6 2020-02-29 (28%); C6 2020-03-31 (41%); C6 2020-04-30 (30%); C6 2020-05-31 (21%); C6 2020-06-30 (42%); C6 2020-07-31 (74%); C6 2020-08-31 (210%); C6 2020-09-30 (59%); C6 2020-10-31 (31%); C8 2020-04-30 (36%); C8 2020-05-31 (26%); C8 2020-06-30 (46%); C8 2020-07-31 (125%); C8 2020-09-30 (34%); C8 2020-10-31 (82%); C8 2020-12-31 (44%); C3 2020-01-31 (22%); C3 2020-02-29 (23%); C3 2020-04-30 (21%); C3 2020-06-29 (131%); C3g 2020-06-29 (44%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-10-31 (51%); C9 2020-12-31 (37%); C4 2020-04-30 (35%); C4 2020-05-31 (34%); C4 2020-06-30 (75%); C4 2020-09-30 (27%); C4 2020-10-31 (26%); C4 2020-11-30 (29%); C4g 2020-04-30 (36%); C4g 2020-05-31 (22%); C4g 2020-06-30 (29%); C4g 2020-10-31 (76%); C4g 2020-12-31 (38%); C_IC1 2020-03-31 (58%); C_IC1 2020-04-30 (74%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%); C_IC3g 2020-10-31 (40%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 32%, C4 41%, C5 32%, C7 20%, C8 23%, C9 23%, C_IC1 41%, C_IC2 41%, C_IC3 20%

**Pricing & Margin**

- C1 (electricity): tariff £99.42-£200.01/MWh, net margin £102.04
- C1g (gas): tariff £25.00-£25.36/MWh, net margin £146.02
- C2 (electricity): tariff £113.06-£227.85/MWh, net margin £201.59
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £143.77
- C3 (electricity): tariff £120.68/MWh, net margin £-169.04 -- **net-negative**
- C3g (gas): tariff £23.03/MWh, net margin £82.32
- C4 (electricity): tariff £96.82-£191.00/MWh, net margin £94.21
- C4g (gas): tariff £16.09-£19.49/MWh, net margin £86.87
- C5 (electricity): tariff £126.54/MWh, net margin £4.74
- C6 (electricity): tariff £143.89-£148.71/MWh, net margin £401.73
- C7 (electricity): tariff £99.50-£203.25/MWh, net margin £87.89
- C8 (electricity): tariff £110.22-£211.40/MWh, net margin £375.88
- C9 (electricity): tariff £85.93-£189.57/MWh, net margin £159.36
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £53,249.44
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £44,258.51
- C_IC3 (electricity): tariff £37.49-£79.92/MWh, net margin £13,094.04
- C_IC3g (gas): tariff £15.44-£20.11/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £5,999.58

**Portfolio Health**

- Capital cost ratio: 0.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.794, average bill shock 23.9%, bad debt provision £194.98, avg complaint probability 5.5%
- Solvency signal: £224,921/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £83,610.73 vs. naked (unhedged) net margin: £961,079.63
- hedging cost £877,468.90 vs. a fully unhedged book (commodity-only: actual net £83,610.73 vs. naked net £961,079.63)
  - C1: actual £-4.99 vs. naked £120.74 -- hedging cost £125.73
  - C1g: actual £22.28 vs. naked £-68.18 -- hedging added £90.47
  - C2: actual £176.51 vs. naked £581.07 -- hedging cost £404.56
  - C2g: actual £138.04 vs. naked £324.27 -- hedging cost £186.23
  - C4: actual £21.46 vs. naked £247.18 -- hedging cost £225.72
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-226.17 vs. naked £243.19 -- hedging cost £469.36
  - C8: actual £235.12 vs. naked £1,169.99 -- hedging cost £934.87
  - C9: actual £-8.28 vs. naked £708.41 -- hedging cost £716.69
  - C_IC1: actual £33,034.60 vs. naked £128,260.98 -- hedging cost £95,226.38
  - C_IC2: actual £42,303.73 vs. naked £96,422.44 -- hedging cost £54,118.71
  - C_IC3: actual £-18,183.70 vs. naked £218,698.93 -- hedging cost £236,882.64
  - C_IC3g: actual £17,934.51 vs. naked £159,245.07 -- hedging cost £141,310.56
  - C_IC4: actual £7,886.99 vs. naked £352,832.81 -- hedging cost £344,945.82

**Year narrative:** 2020 produced a net gain of £128,349.70 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 74 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £78,289.38 (gross £765,626.54, capital £5,632.22)
  - Electricity: gross £682,827.42, capital £5,617.56, net £68,417.78
  - Gas: gross £82,799.12, capital £14.66, net £9,871.60
- Treasury at year end: £2,955,969.20
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.88 (avg 0.88), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2021-12-31 period 48, net margin £-299.15

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £410,967.04
  - By billing account: C1 £4,005.72, C2 £7,172.32, C3 £5,224.55, C4 £4,519.74, C5 £9,668.92, C6 £14,814.71, C7 £6,744.33, C8 £8,504.15, C9 £7,859.12, C_IC1 £1,298,472.40, C_IC2 £576,015.50, C_IC3 £2,034,411.43, C_IC4 £1,365,158.58
- Bill shock events (>=20%): 58 -- C1 2021-05-31 (26%); C1 2021-07-31 (22%); C1g 2021-05-31 (42%); C1g 2021-06-30 (32%); C1g 2021-07-31 (178%); C1g 2021-08-31 (114%); C1g 2021-09-30 (107%); C1g 2021-10-31 (71%); C1g 2021-11-30 (64%); C1g 2021-12-29 (35%); C7 2021-05-31 (30%); C7 2021-06-30 (47%); C7 2021-10-31 (55%); C7 2021-11-30 (65%); C2 2021-11-30 (21%); C2g 2021-02-28 (20%); C2g 2021-04-30 (50%); C2g 2021-05-31 (37%); C2g 2021-06-30 (58%); C2g 2021-10-31 (67%); C2g 2021-11-30 (66%); C6 2021-01-31 (32%); C6 2021-02-28 (37%); C6 2021-03-31 (24%); C6 2021-07-31 (58%); C6 2021-08-31 (62%); C6 2021-09-30 (86%); C6 2021-10-31 (28%); C6 2021-12-31 (45%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (25%); C8 2021-10-31 (69%); C8 2021-11-30 (84%); C9 2021-02-28 (22%); C9 2021-05-31 (25%); C9 2021-06-30 (51%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-11-30 (98%); C9 2021-12-31 (24%); C4 2021-04-30 (35%); C4 2021-09-30 (30%); C4 2021-10-31 (52%); C4 2021-11-30 (38%); C4g 2021-05-31 (24%); C4g 2021-06-30 (57%); C4g 2021-10-31 (132%); C4g 2021-11-30 (61%); C_IC1 2021-05-31 (41%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (77%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (21%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (27%)
- Churn risk (accounts renewing in 2021): 6 at risk (≥20% churn prob): C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1 (electricity): tariff £104.77-£200.01/MWh, net margin £24.24
- C1g (gas): tariff £25.00/MWh, net margin £40.05
- C2 (electricity): tariff £113.06-£274.50/MWh, net margin £198.84
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £126.10
- C4 (electricity): tariff £96.82-£274.50/MWh, net margin £-35.60 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-294.47 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.19/MWh, net margin £227.79
- C7 (electricity): tariff £106.46-£274.50/MWh, net margin £-120.85 -- **net-negative**
- C8 (electricity): tariff £110.22-£274.50/MWh, net margin £431.50
- C9 (electricity): tariff £85.93-£267.37/MWh, net margin £78.04
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £30,539.02
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £58,235.63
- C_IC3 (electricity): tariff £41.86-£392.84/MWh, net margin £-27,099.85 -- **net-negative**
- C_IC3g (gas): tariff £20.11-£123.75/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £5,939.02

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.809, average bill shock 20.8%, bad debt provision £365.61, avg complaint probability 5.2%
- Solvency signal: £268,724/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £200,857.26 vs. naked (unhedged) net margin: £466,561.13
- hedging cost £265,703.88 vs. a fully unhedged book (commodity-only: actual net £200,857.26 vs. naked net £466,561.13)
  - C2: actual £138.10 vs. naked £150.31 -- hedging cost £12.22
  - C2g: actual £25.95 vs. naked £-190.70 -- hedging added £216.66
  - C4: actual £-231.16 vs. naked £-156.26 -- hedging cost £74.90
  - C4g: actual £-869.98 vs. naked £-1,344.38 -- hedging added £474.41
  - C6: actual £514.24 vs. naked £269.68 -- hedging added £244.56
  - C7: actual £-1,925.74 vs. naked £-869.22 -- hedging cost £1,056.52
  - C8: actual £21.86 vs. naked £107.75 -- hedging cost £85.89
  - C9: actual £-27.50 vs. naked £-160.17 -- hedging added £132.68
  - C_IC1: actual £30,816.17 vs. naked £-58,138.69 -- hedging added £88,954.86
  - C_IC2: actual £65,918.97 vs. naked £24,606.70 -- hedging added £41,312.26
  - C_IC3: actual £104,236.73 vs. naked £238,782.50 -- hedging cost £134,545.76
  - C_IC3g: actual £4,142.87 vs. naked £85,199.40 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £178,304.23 -- hedging cost £180,207.49

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £78,289.38 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 58 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £339,913.25 (gross £1,050,926.43, capital £13,258.33)
  - Electricity: gross £960,538.31, capital £13,212.55, net £331,170.84
  - Gas: gross £90,388.12, capital £45.78, net £8,742.40
- Treasury at year end: £3,169,661.88
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.96 (avg 0.96), C2g 0.86 (avg 0.86), C4 0.96 (avg 0.96), C4g 0.88 (avg 0.88), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,041,734.31, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,591.24 / stressed £20,590.79) ratio 2.70
  - 2022-05-29: treasury £3,041,887.52, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,703.06 / stressed £20,620.75) ratio 2.70
  - 2022-06-28: treasury £3,041,883.26, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,703.06 / stressed £20,620.75) ratio 2.70
  - 2022-07-28: treasury £3,041,684.22, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,764.27 / stressed £20,632.88) ratio 2.70
  - 2022-08-27: treasury £3,041,672.13, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,764.27 / stressed £20,632.88) ratio 2.70
  - 2022-09-26: treasury £3,041,654.54, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,764.27 / stressed £20,632.88) ratio 2.70
  - 2022-10-26: treasury £3,039,328.15, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,831.40 / stressed £20,645.76) ratio 2.70
  - 2022-11-25: treasury £3,039,169.61, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,831.40 / stressed £20,645.76) ratio 2.70
  - 2022-12-25: treasury £3,038,889.45, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,831.40 / stressed £20,645.76) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C6 on 2022-12-31 period 48, net margin £-990.56

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2022): £369,517.70
  - By billing account: C1 £4,107.42, C2 £5,720.18, C3 £4,617.09, C4 £2,561.53, C5 £8,488.33, C6 £14,118.21, C7 £4,196.67, C8 £7,048.60, C9 £7,265.52, C_IC1 £1,036,751.01, C_IC2 £660,995.56, C_IC3 £1,955,975.60, C_IC4 £1,091,884.36
- Bill shock events (>=20%): 65 -- C7 2022-05-31 (61%); C7 2022-06-30 (26%); C7 2022-09-30 (32%); C7 2022-11-30 (61%); C7 2022-12-31 (55%); C2g 2022-02-28 (22%); C2g 2022-04-30 (69%); C2g 2022-05-31 (38%); C2g 2022-06-30 (31%); C2g 2022-07-31 (20%); C2g 2022-09-30 (65%); C2g 2022-11-30 (22%); C2g 2022-12-31 (113%); C6 2022-01-31 (47%); C6 2022-02-28 (117%); C6 2022-04-30 (54%); C6 2022-06-30 (39%); C6 2022-07-31 (69%); C6 2022-08-31 (85%); C6 2022-09-30 (88%); C6 2022-10-31 (50%); C6 2022-11-30 (37%); C8 2022-05-31 (39%); C8 2022-06-30 (34%); C8 2022-07-31 (21%); C8 2022-09-30 (81%); C8 2022-12-31 (110%); C9 2022-04-30 (21%); C9 2022-05-31 (29%); C9 2022-06-30 (37%); C9 2022-07-31 (94%); C9 2022-09-30 (48%); C9 2022-10-31 (30%); C9 2022-11-30 (44%); C9 2022-12-31 (52%); C4 2022-05-31 (120%); C4 2022-06-30 (59%); C4 2022-07-31 (84%); C4 2022-11-30 (36%); C4 2022-12-31 (100%); C4g 2022-01-31 (26%); C4g 2022-02-28 (24%); C4g 2022-04-30 (24%); C4g 2022-05-31 (36%); C4g 2022-06-30 (30%); C4g 2022-07-31 (25%); C4g 2022-09-30 (75%); C4g 2022-10-31 (43%); C4g 2022-11-30 (42%); C4g 2022-12-31 (147%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (110%); C_IC3g 2022-01-31 (25%); C_IC3g 2022-03-31 (33%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (50%); C_IC3g 2022-08-31 (39%); C_IC3g 2022-10-31 (50%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%)
- Churn risk (accounts renewing in 2022): 10 at risk (≥20% churn prob): C2 38%, C4 38%, C6 35%, C7 29%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C2 (electricity): tariff £143.79-£457.50/MWh, net margin £2.28
- C2g (gas): tariff £35.00-£95.00/MWh, net margin £-101.95 -- **net-negative**
- C4 (electricity): tariff £143.79-£457.50/MWh, net margin £-201.31 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,155.57 -- **net-negative**
- C6 (electricity): tariff £197.19-£413.77/MWh, net margin £-66.08 -- **net-negative**
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,632.87 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £73.71
- C9 (electricity): tariff £140.05-£389.85/MWh, net margin £124.62
- C_IC1 (electricity): tariff £-83.39-£461.36/MWh, net margin £136,190.42
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £75,291.68
- C_IC3 (electricity): tariff £137.99-£392.84/MWh, net margin £115,469.02
- C_IC3g (gas): tariff £116.42-£123.75/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £5,919.38

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 2 -- £3,474,099.31 -> £3,057,461.56 (12.0%); £3,474,280.83 -> £3,056,886.71 (12.0%)
- Bills issued: 156, average clarity 0.778, average bill shock 26.3%, bad debt provision £1,233.55, avg complaint probability 6.1%
- Solvency signal: £316,966/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £138,293.90 vs. naked (unhedged) net margin: £1,159,439.74
- hedging cost £1,021,145.84 vs. a fully unhedged book (commodity-only: actual net £138,293.90 vs. naked net £1,159,439.74)
  - C2: actual £-191.17 vs. naked £524.01 -- hedging cost £715.18
  - C2g: actual £-321.24 vs. naked £262.02 -- hedging cost £583.26
  - C4: actual £-292.88 vs. naked £597.69 -- hedging cost £890.57
  - C4g: actual £-2,038.74 vs. naked £1,336.80 -- hedging cost £3,375.53
  - C6: actual £1,282.90 vs. naked £4,155.34 -- hedging cost £2,872.44
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-348.38 vs. naked £1,102.92 -- hedging cost £1,451.29
  - C9: actual £-47.01 vs. naked £1,014.75 -- hedging cost £1,061.77
  - C_IC1: actual £210,454.89 vs. naked £248,695.32 -- hedging cost £38,240.43
  - C_IC2: actual £85,603.78 vs. naked £124,884.48 -- hedging cost £39,280.70
  - C_IC3: actual £-167,348.92 vs. naked £446,226.79 -- hedging cost £613,575.71
  - C_IC3g: actual £8,513.79 vs. naked £123,301.26 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £205,056.67 -- hedging cost £201,583.86

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £339,913.25 across 13 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 65 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £100,338.11 (gross £909,245.31, capital £9,760.45)
  - Electricity: gross £787,959.15, capital £9,686.27, net £91,320.50
  - Gas: gross £121,286.16, capital £74.18, net £9,017.61
- Treasury at year end: £3,342,701.72
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.95 (avg 0.95), C2g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,145,178.72, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,036.79 / stressed £44,239.58) ratio 2.76
  - 2023-02-23: treasury £3,145,161.80, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,036.79 / stressed £44,239.58) ratio 2.76
  - 2023-03-25: treasury £3,145,145.05, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,036.79 / stressed £44,239.58) ratio 2.76
  - 2023-04-24: treasury £3,223,453.74, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,843.33 / stressed £49,107.89) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C6 on 2023-12-31 period 48, net margin £-865.21

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £306,630.09
  - By billing account: C1 £2,879.17, C2 £4,710.73, C3 £4,190.94, C4 £1,698.06, C5 £7,086.07, C6 £15,274.41, C7 £4,614.03, C8 £6,353.31, C9 £6,179.51, C_IC1 £970,660.57, C_IC2 £597,184.98, C_IC3 £1,380,932.43, C_IC4 £984,426.99
- Bill shock events (>=20%): 55 -- C7 2023-01-31 (40%); C7 2023-06-30 (100%); C7 2023-07-31 (86%); C7 2023-08-31 (96%); C7 2023-10-31 (55%); C7 2023-11-30 (70%); C7 2023-12-31 (33%); C2 2023-04-30 (28%); C2g 2023-01-31 (42%); C2g 2023-04-30 (35%); C2g 2023-05-31 (40%); C2g 2023-06-30 (40%); C2g 2023-08-31 (21%); C2g 2023-10-31 (96%); C2g 2023-11-30 (60%); C6 2023-01-31 (28%); C6 2023-02-28 (24%); C6 2023-04-30 (132%); C6 2023-06-30 (45%); C6 2023-07-31 (89%); C6 2023-08-31 (90%); C6 2023-09-30 (88%); C6 2023-10-31 (83%); C6 2023-11-30 (275%); C8 2023-04-30 (30%); C8 2023-05-31 (40%); C8 2023-06-30 (43%); C8 2023-11-30 (50%); C8 2023-12-31 (104%); C9 2023-02-28 (21%); C9 2023-03-31 (24%); C9 2023-04-30 (30%); C9 2023-05-31 (33%); C9 2023-06-30 (45%); C9 2023-09-30 (21%); C9 2023-10-31 (74%); C9 2023-11-30 (53%); C4 2023-02-28 (26%); C4 2023-05-31 (91%); C4 2023-06-30 (50%); C4 2023-07-31 (74%); C4 2023-09-30 (29%); C4 2023-11-30 (32%); C4g 2023-05-31 (37%); C4g 2023-06-30 (46%); C4g 2023-10-31 (47%); C4g 2023-11-30 (67%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (52%); C_IC1 2023-07-31 (59%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (52%); C_IC2 2023-06-30 (100%); C_IC3g 2023-01-31 (36%); C_IC4 2023-01-31 (35%)
- Churn risk (accounts renewing in 2023): 10 at risk (≥20% churn prob): C2 41%, C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C2 (electricity): tariff £208.21-£457.50/MWh, net margin £88.59
- C2g (gas): tariff £70.00-£95.00/MWh, net margin £134.66
- C4 (electricity): tariff £198.44-£457.50/MWh, net margin £-23.77 -- **net-negative**
- C4g (gas): tariff £65.16-£95.00/MWh, net margin £-1,116.97 -- **net-negative**
- C6 (electricity): tariff £340.22-£413.77/MWh, net margin £558.92
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-144.77 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £159.02
- C9 (electricity): tariff £192.66-£389.85/MWh, net margin £398.47
- C_IC1 (electricity): tariff £-60.00-£461.36/MWh, net margin £161,155.64
- C_IC2 (electricity): tariff £-186.24-£474.31/MWh, net margin £84,845.27
- C_IC3 (electricity): tariff £100.33-£263.43/MWh, net margin £-161,644.73 -- **net-negative**
- C_IC3g (gas): tariff £56.00-£116.42/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £5,927.85

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): 47 -- £3,749,377.19 -> £3,342,627.12 (10.8%); £3,749,377.34 -> £3,342,627.12 (10.8%); £3,749,377.49 -> £3,342,627.11 (10.8%); £3,749,377.64 -> £3,342,627.11 (10.8%); £3,749,377.80 -> £3,342,627.11 (10.8%); £3,749,377.95 -> £3,342,627.11 (10.8%); £3,749,378.10 -> £3,342,627.11 (10.8%); £3,749,378.26 -> £3,342,627.11 (10.8%); £3,749,378.42 -> £3,342,627.11 (10.8%); £3,749,378.57 -> £3,342,627.11 (10.8%); £3,749,378.73 -> £3,342,627.11 (10.8%); £3,749,378.89 -> £3,342,627.11 (10.8%); £3,749,379.04 -> £3,342,627.10 (10.8%); £3,749,379.21 -> £3,342,627.10 (10.8%); £3,749,379.40 -> £3,342,627.09 (10.8%); £3,749,379.61 -> £3,342,627.09 (10.8%); £3,749,379.83 -> £3,342,627.08 (10.8%); £3,749,380.07 -> £3,342,627.06 (10.8%); £3,749,380.34 -> £3,342,627.05 (10.8%); £3,749,380.59 -> £3,342,627.04 (10.8%); £3,749,380.86 -> £3,342,627.03 (10.8%); £3,749,381.11 -> £3,342,627.02 (10.8%); £3,749,381.37 -> £3,342,627.00 (10.8%); £3,749,381.63 -> £3,342,626.99 (10.8%); £3,749,381.89 -> £3,342,626.97 (10.8%); £3,749,382.16 -> £3,342,626.96 (10.8%); £3,749,382.43 -> £3,342,626.95 (10.8%); £3,749,382.68 -> £3,342,626.94 (10.8%); £3,749,382.94 -> £3,342,626.93 (10.8%); £3,749,383.19 -> £3,342,626.92 (10.8%); £3,749,383.45 -> £3,342,626.92 (10.8%); £3,749,383.70 -> £3,342,626.91 (10.8%); £3,749,383.97 -> £3,342,626.89 (10.8%); £3,749,384.23 -> £3,342,626.87 (10.8%); £3,749,384.48 -> £3,342,626.85 (10.8%); £3,749,384.74 -> £3,342,626.83 (10.8%); £3,749,385.00 -> £3,342,626.80 (10.8%); £3,749,385.26 -> £3,342,626.77 (10.8%); £3,749,385.53 -> £3,342,626.74 (10.8%); £3,749,385.79 -> £3,342,626.71 (10.8%); £3,749,386.05 -> £3,342,626.68 (10.8%); £3,749,386.31 -> £3,342,626.65 (10.8%); £3,749,386.57 -> £3,342,626.63 (10.8%); £3,749,386.83 -> £3,342,626.61 (10.8%); £3,749,387.09 -> £3,342,626.61 (10.8%); £3,749,387.34 -> £3,342,626.60 (10.8%); £3,749,387.55 -> £3,342,701.72 (10.8%)
- Bills issued: 156, average clarity 0.782, average bill shock 25.0%, bad debt provision £1,038.74, avg complaint probability 5.8%
- Solvency signal: £334,270/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £399,917.35 vs. naked (unhedged) net margin: £1,238,308.19
- hedging cost £838,390.84 vs. a fully unhedged book (commodity-only: actual net £399,917.35 vs. naked net £1,238,308.19)
  - C2: actual £106.23 vs. naked £797.97 -- hedging cost £691.74
  - C2g: actual £178.43 vs. naked £669.84 -- hedging cost £491.42
  - C4: actual £234.43 vs. naked £704.88 -- hedging cost £470.44
  - C4g: actual £507.40 vs. naked £1,025.98 -- hedging cost £518.58
  - C6: actual £1,568.97 vs. naked £5,239.24 -- hedging cost £3,670.26
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £212.54 vs. naked £1,972.23 -- hedging cost £1,759.69
  - C9: actual £627.33 vs. naked £2,131.03 -- hedging cost £1,503.70
  - C_IC1: actual £140,578.68 vs. naked £283,444.44 -- hedging cost £142,865.76
  - C_IC2: actual £93,089.46 vs. naked £161,132.40 -- hedging cost £68,042.94
  - C_IC3: actual £149,968.27 vs. naked £423,965.79 -- hedging cost £273,997.52
  - C_IC3g: actual £8,660.26 vs. naked £123,107.25 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £232,127.67 -- hedging cost £228,435.92

**Year narrative:** 2023 produced a net gain of £100,338.11 across 13 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 55 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £368,472.31 (gross £1,277,622.83, capital £9,664.42)
  - Electricity: gross £1,152,504.86, capital £9,608.51, net £357,730.84
  - Gas: gross £125,117.97, capital £55.91, net £10,741.47
- Treasury at year end: £3,755,685.24
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C4 0.86 (avg 0.86), C4g 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2024-06-28 period 31, net margin £-26.25

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C6
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £339,105.60
  - By billing account: C1 £2,964.84, C2 £4,686.39, C3 £3,798.64, C4 £2,165.11, C5 £7,056.35, C6 £13,691.10, C7 £4,629.14, C8 £6,843.54, C9 £6,717.89, C_IC1 £972,666.64, C_IC2 £639,084.35, C_IC3 £1,762,025.37, C_IC4 £982,043.39
- Bill shock events (>=20%): 42 -- C7 2024-01-31 (36%); C7 2024-02-29 (27%); C7 2024-05-31 (37%); C7 2024-09-30 (34%); C7 2024-11-30 (84%); C2 2024-04-30 (34%); C2 2024-12-31 (22%); C2g 2024-02-29 (24%); C2g 2024-04-30 (36%); C2g 2024-05-31 (47%); C2g 2024-07-31 (25%); C2g 2024-09-30 (53%); C2g 2024-10-31 (34%); C2g 2024-11-30 (52%); C6 2024-03-29 (33%); C8 2024-02-29 (23%); C8 2024-04-30 (45%); C8 2024-05-31 (27%); C8 2024-06-30 (142%); C8 2024-07-31 (65%); C8 2024-08-31 (137%); C8 2024-09-30 (72%); C8 2024-10-31 (35%); C8 2024-11-30 (61%); C9 2024-05-31 (49%); C9 2024-07-31 (30%); C9 2024-09-30 (55%); C9 2024-10-31 (23%); C9 2024-11-30 (47%); C4 2024-04-30 (33%); C4 2024-09-30 (28%); C4 2024-11-30 (28%); C4g 2024-02-29 (27%); C4g 2024-05-31 (68%); C4g 2024-07-31 (26%); C4g 2024-09-30 (22%); C4g 2024-10-31 (43%); C4g 2024-11-30 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (63%); C_IC2 2024-06-30 (50%); C_IC2 2024-07-31 (79%)
- Churn risk (accounts renewing in 2024): 7 at risk (≥20% churn prob): C2 41%, C4 38%, C6 23%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC4 20%

**Pricing & Margin**

- C2 (electricity): tariff £157.94-£397.50/MWh, net margin £210.57
- C2g (gas): tariff £48.41-£70.00/MWh, net margin £266.54
- C4 (electricity): tariff £159.80-£378.84/MWh, net margin £303.22
- C4g (gas): tariff £48.05-£65.16/MWh, net margin £444.16
- C6 (electricity): tariff £340.22/MWh, net margin £789.59
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £635.74
- C8 (electricity): tariff £159.13-£397.50/MWh, net margin £400.10
- C9 (electricity): tariff £165.00-£367.80/MWh, net margin £656.74
- C_IC1 (electricity): tariff £-98.58-£329.99/MWh, net margin £125,235.53
- C_IC2 (electricity): tariff £-106.92-£353.54/MWh, net margin £69,527.03
- C_IC3 (electricity): tariff £88.78-£191.53/MWh, net margin £154,021.01
- C_IC3g (gas): tariff £49.06-£56.00/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £5,951.30

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): 4271 -- £3,751,835.54 -> £3,342,701.72 (10.9%); £3,751,835.71 -> £3,342,701.72 (10.9%); £3,751,835.88 -> £3,342,701.72 (10.9%); £3,751,836.06 -> £3,342,701.72 (10.9%); £3,751,836.23 -> £3,342,701.72 (10.9%); £3,751,836.41 -> £3,342,701.72 (10.9%); £3,751,836.58 -> £3,342,701.73 (10.9%); £3,751,836.75 -> £3,342,701.73 (10.9%); £3,751,836.92 -> £3,342,701.73 (10.9%); £3,751,837.10 -> £3,342,701.73 (10.9%); £3,751,837.27 -> £3,342,701.73 (10.9%); £3,751,837.45 -> £3,342,701.73 (10.9%); £3,751,837.61 -> £3,342,701.72 (10.9%); £3,751,837.81 -> £3,342,701.77 (10.9%); £3,751,838.01 -> £3,342,701.82 (10.9%); £3,751,838.24 -> £3,342,701.87 (10.9%); £3,751,838.48 -> £3,342,701.92 (10.9%); £3,751,838.74 -> £3,342,701.97 (10.9%); £3,751,839.03 -> £3,342,702.01 (10.9%); £3,751,839.31 -> £3,342,702.05 (10.9%); £3,751,839.60 -> £3,342,702.08 (10.9%); £3,751,839.89 -> £3,342,702.08 (10.9%); £3,751,840.19 -> £3,342,702.08 (10.9%); £3,751,840.47 -> £3,342,702.08 (10.9%); £3,751,840.76 -> £3,342,702.08 (10.9%); £3,751,841.05 -> £3,342,702.07 (10.9%); £3,751,841.33 -> £3,342,702.07 (10.9%); £3,751,841.61 -> £3,342,702.07 (10.9%); £3,751,841.88 -> £3,342,702.07 (10.9%); £3,751,842.17 -> £3,342,702.07 (10.9%); £3,751,842.45 -> £3,342,702.07 (10.9%); £3,751,842.74 -> £3,342,702.11 (10.9%); £3,751,843.02 -> £3,342,702.17 (10.9%); £3,751,843.30 -> £3,342,702.23 (10.9%); £3,751,843.53 -> £3,342,702.30 (10.9%); £3,751,843.74 -> £3,342,702.36 (10.9%); £3,751,843.96 -> £3,342,702.43 (10.9%); £3,751,844.26 -> £3,342,702.52 (10.9%); £3,751,844.55 -> £3,342,702.60 (10.9%); £3,751,844.83 -> £3,342,702.58 (10.9%); £3,751,845.12 -> £3,342,702.56 (10.9%); £3,751,845.40 -> £3,342,702.53 (10.9%); £3,751,845.70 -> £3,342,702.52 (10.9%); £3,751,845.99 -> £3,342,702.51 (10.9%); £3,751,846.28 -> £3,342,702.51 (10.9%); £3,751,846.54 -> £3,342,702.50 (10.9%); £3,751,846.78 -> £3,342,702.50 (10.9%); £3,751,847.00 -> £3,342,702.50 (10.9%); £3,751,847.18 -> £3,342,702.50 (10.9%); £3,751,847.35 -> £3,342,702.50 (10.9%); £3,751,847.52 -> £3,342,702.50 (10.9%); £3,751,847.69 -> £3,342,702.51 (10.9%); £3,751,847.86 -> £3,342,702.51 (10.9%); £3,751,848.02 -> £3,342,702.51 (10.9%); £3,751,848.20 -> £3,342,702.51 (10.9%); £3,751,848.37 -> £3,342,702.52 (10.9%); £3,751,848.54 -> £3,342,702.52 (10.9%); £3,751,848.71 -> £3,342,702.52 (10.9%); £3,751,848.88 -> £3,342,702.52 (10.9%); £3,751,849.05 -> £3,342,702.52 (10.9%); £3,751,849.22 -> £3,342,702.52 (10.9%); £3,751,849.40 -> £3,342,702.56 (10.9%); £3,751,849.61 -> £3,342,702.62 (10.9%); £3,751,849.83 -> £3,342,702.67 (10.9%); £3,751,850.07 -> £3,342,702.72 (10.9%); £3,751,850.32 -> £3,342,702.77 (10.9%); £3,751,850.60 -> £3,342,702.81 (10.9%); £3,751,850.88 -> £3,342,702.85 (10.9%); £3,751,851.16 -> £3,342,702.88 (10.9%); £3,751,851.44 -> £3,342,702.88 (10.9%); £3,751,851.73 -> £3,342,702.88 (10.9%); £3,751,852.01 -> £3,342,702.88 (10.9%); £3,751,852.28 -> £3,342,702.88 (10.9%); £3,751,852.56 -> £3,342,702.88 (10.9%); £3,751,852.84 -> £3,342,702.87 (10.9%); £3,751,853.12 -> £3,342,702.87 (10.9%); £3,751,853.40 -> £3,342,702.87 (10.9%); £3,751,853.67 -> £3,342,702.87 (10.9%); £3,751,853.94 -> £3,342,702.87 (10.9%); £3,751,854.23 -> £3,342,702.91 (10.9%); £3,751,854.43 -> £3,342,702.97 (10.9%); £3,751,854.65 -> £3,342,703.03 (10.9%); £3,751,854.86 -> £3,342,703.10 (10.9%); £3,751,855.07 -> £3,342,703.16 (10.9%); £3,751,855.29 -> £3,342,703.23 (10.9%); £3,751,855.50 -> £3,342,703.31 (10.9%); £3,751,855.71 -> £3,342,703.39 (10.9%); £3,751,855.99 -> £3,342,703.37 (10.9%); £3,751,856.28 -> £3,342,703.35 (10.9%); £3,751,856.55 -> £3,342,703.32 (10.9%); £3,751,856.84 -> £3,342,703.30 (10.9%); £3,751,857.13 -> £3,342,703.30 (10.9%); £3,751,857.41 -> £3,342,703.29 (10.9%); £3,751,857.67 -> £3,342,703.29 (10.9%); £3,751,857.90 -> £3,342,703.28 (10.9%); £3,751,858.12 -> £3,342,703.28 (10.9%); £3,751,858.29 -> £3,342,703.28 (10.9%); £3,751,858.46 -> £3,342,703.28 (10.9%); £3,751,858.63 -> £3,342,703.28 (10.9%); £3,751,858.80 -> £3,342,703.28 (10.9%); £3,751,858.97 -> £3,342,703.28 (10.9%); £3,751,859.14 -> £3,342,703.29 (10.9%); £3,751,859.31 -> £3,342,703.29 (10.9%); £3,751,859.47 -> £3,342,703.29 (10.9%); £3,751,859.64 -> £3,342,703.29 (10.9%); £3,751,859.81 -> £3,342,703.29 (10.9%); £3,751,859.99 -> £3,342,703.30 (10.9%); £3,751,860.16 -> £3,342,703.29 (10.9%); £3,751,860.33 -> £3,342,703.29 (10.9%); £3,751,860.52 -> £3,342,703.33 (10.9%); £3,751,860.72 -> £3,342,703.39 (10.9%); £3,751,860.95 -> £3,342,703.44 (10.9%); £3,751,861.19 -> £3,342,703.49 (10.9%); £3,751,861.46 -> £3,342,703.53 (10.9%); £3,751,861.74 -> £3,342,703.58 (10.9%); £3,751,862.02 -> £3,342,703.61 (10.9%); £3,751,862.31 -> £3,342,703.65 (10.9%); £3,751,862.59 -> £3,342,703.65 (10.9%); £3,751,862.87 -> £3,342,703.65 (10.9%); £3,751,863.16 -> £3,342,703.64 (10.9%); £3,751,863.46 -> £3,342,703.64 (10.9%); £3,751,863.74 -> £3,342,703.64 (10.9%); £3,751,864.03 -> £3,342,703.64 (10.9%); £3,751,864.30 -> £3,342,703.64 (10.9%); £3,751,864.58 -> £3,342,703.64 (10.9%); £3,751,864.87 -> £3,342,703.64 (10.9%); £3,751,865.14 -> £3,342,703.64 (10.9%); £3,751,865.42 -> £3,342,703.67 (10.9%); £3,751,865.70 -> £3,342,703.73 (10.9%); £3,751,865.92 -> £3,342,703.80 (10.9%); £3,751,866.20 -> £3,342,703.86 (10.9%); £3,751,866.41 -> £3,342,703.93 (10.9%); £3,751,866.62 -> £3,342,704.00 (10.9%); £3,751,866.83 -> £3,342,704.08 (10.9%); £3,751,867.05 -> £3,342,704.16 (10.9%); £3,751,867.33 -> £3,342,704.14 (10.9%); £3,751,867.60 -> £3,342,704.12 (10.9%); £3,751,867.89 -> £3,342,704.09 (10.9%); £3,751,868.16 -> £3,342,704.07 (10.9%); £3,751,868.45 -> £3,342,704.06 (10.9%); £3,751,868.74 -> £3,342,704.06 (10.9%); £3,751,869.00 -> £3,342,704.05 (10.9%); £3,751,869.23 -> £3,342,704.05 (10.9%); £3,751,869.45 -> £3,342,704.05 (10.9%); £3,751,869.61 -> £3,342,704.05 (10.9%); £3,751,869.78 -> £3,342,704.05 (10.9%); £3,751,869.94 -> £3,342,704.05 (10.9%); £3,751,870.11 -> £3,342,704.05 (10.9%); £3,751,870.28 -> £3,342,704.05 (10.9%); £3,751,870.45 -> £3,342,704.06 (10.9%); £3,751,870.62 -> £3,342,704.06 (10.9%); £3,751,870.78 -> £3,342,704.06 (10.9%); £3,751,870.95 -> £3,342,704.06 (10.9%); £3,751,871.12 -> £3,342,704.07 (10.9%); £3,751,871.29 -> £3,342,704.07 (10.9%); £3,751,871.46 -> £3,342,704.06 (10.9%); £3,751,871.63 -> £3,342,704.06 (10.9%); £3,751,871.82 -> £3,342,704.10 (10.9%); £3,751,872.02 -> £3,342,704.16 (10.9%); £3,751,872.24 -> £3,342,704.21 (10.9%); £3,751,872.48 -> £3,342,704.26 (10.9%); £3,751,872.75 -> £3,342,704.30 (10.9%); £3,751,873.02 -> £3,342,704.35 (10.9%); £3,751,873.29 -> £3,342,704.39 (10.9%); £3,751,873.58 -> £3,342,704.42 (10.9%); £3,751,873.85 -> £3,342,704.42 (10.9%); £3,751,874.13 -> £3,342,704.42 (10.9%); £3,751,874.41 -> £3,342,704.42 (10.9%); £3,751,874.68 -> £3,342,704.41 (10.9%); £3,751,874.96 -> £3,342,704.41 (10.9%); £3,751,875.24 -> £3,342,704.41 (10.9%); £3,751,875.52 -> £3,342,704.41 (10.9%); £3,751,875.79 -> £3,342,704.41 (10.9%); £3,751,876.08 -> £3,342,704.41 (10.9%); £3,751,876.35 -> £3,342,704.41 (10.9%); £3,751,876.63 -> £3,342,704.44 (10.9%); £3,751,876.84 -> £3,342,704.50 (10.9%); £3,751,877.11 -> £3,342,704.57 (10.9%); £3,751,877.39 -> £3,342,704.63 (10.9%); £3,751,877.59 -> £3,342,704.70 (10.9%); £3,751,877.86 -> £3,342,704.77 (10.9%); £3,751,878.14 -> £3,342,704.85 (10.9%); £3,751,878.36 -> £3,342,704.93 (10.9%); £3,751,878.64 -> £3,342,704.91 (10.9%); £3,751,878.91 -> £3,342,704.88 (10.9%); £3,751,879.20 -> £3,342,704.86 (10.9%); £3,751,879.48 -> £3,342,704.84 (10.9%); £3,751,879.76 -> £3,342,704.83 (10.9%); £3,751,880.03 -> £3,342,704.83 (10.9%); £3,751,880.29 -> £3,342,704.82 (10.9%); £3,751,880.52 -> £3,342,704.81 (10.9%); £3,751,880.74 -> £3,342,704.81 (10.9%); £3,751,880.90 -> £3,342,704.81 (10.9%); £3,751,881.06 -> £3,342,704.81 (10.9%); £3,751,881.23 -> £3,342,704.82 (10.9%); £3,751,881.39 -> £3,342,704.82 (10.9%); £3,751,881.54 -> £3,342,704.82 (10.9%); £3,751,881.70 -> £3,342,704.82 (10.9%); £3,751,881.87 -> £3,342,704.82 (10.9%); £3,751,882.03 -> £3,342,704.83 (10.9%); £3,751,882.19 -> £3,342,704.83 (10.9%); £3,751,882.36 -> £3,342,704.83 (10.9%); £3,751,882.52 -> £3,342,704.83 (10.9%); £3,751,882.68 -> £3,342,704.83 (10.9%); £3,751,882.84 -> £3,342,704.82 (10.9%); £3,751,883.02 -> £3,342,704.87 (10.9%); £3,751,883.22 -> £3,342,704.92 (10.9%); £3,751,883.43 -> £3,342,704.97 (10.9%); £3,751,883.66 -> £3,342,705.02 (10.9%); £3,751,883.92 -> £3,342,705.07 (10.9%); £3,751,884.19 -> £3,342,705.11 (10.9%); £3,751,884.47 -> £3,342,705.15 (10.9%); £3,751,884.73 -> £3,342,705.18 (10.9%); £3,751,885.00 -> £3,342,705.18 (10.9%); £3,751,885.27 -> £3,342,705.18 (10.9%); £3,751,885.54 -> £3,342,705.18 (10.9%); £3,751,885.82 -> £3,342,705.18 (10.9%); £3,751,886.09 -> £3,342,705.18 (10.9%); £3,751,886.36 -> £3,342,705.17 (10.9%); £3,751,886.62 -> £3,342,705.17 (10.9%); £3,751,886.88 -> £3,342,705.17 (10.9%); £3,751,887.15 -> £3,342,705.17 (10.9%); £3,751,887.41 -> £3,342,705.17 (10.9%); £3,751,887.69 -> £3,342,705.21 (10.9%); £3,751,887.89 -> £3,342,705.27 (10.9%); £3,751,888.09 -> £3,342,705.33 (10.9%); £3,751,888.30 -> £3,342,705.40 (10.9%); £3,751,888.50 -> £3,342,705.46 (10.9%); £3,751,888.77 -> £3,342,705.53 (10.9%); £3,751,888.97 -> £3,342,705.61 (10.9%); £3,751,889.17 -> £3,342,705.69 (10.9%); £3,751,889.44 -> £3,342,705.67 (10.9%); £3,751,889.71 -> £3,342,705.64 (10.9%); £3,751,889.97 -> £3,342,705.62 (10.9%); £3,751,890.24 -> £3,342,705.60 (10.9%); £3,751,890.50 -> £3,342,705.59 (10.9%); £3,751,890.77 -> £3,342,705.59 (10.9%); £3,751,891.03 -> £3,342,705.58 (10.9%); £3,751,891.26 -> £3,342,705.58 (10.9%); £3,751,891.47 -> £3,342,705.57 (10.9%); £3,751,891.61 -> £3,342,705.57 (10.9%); £3,751,891.76 -> £3,342,705.57 (10.9%); £3,751,891.90 -> £3,342,705.57 (10.9%); £3,751,892.05 -> £3,342,705.58 (10.9%); £3,751,892.20 -> £3,342,705.58 (10.9%); £3,751,892.34 -> £3,342,705.58 (10.9%); £3,751,892.47 -> £3,342,705.58 (10.9%); £3,751,892.61 -> £3,342,705.58 (10.9%); £3,751,892.75 -> £3,342,705.59 (10.9%); £3,751,892.89 -> £3,342,705.59 (10.9%); £3,751,893.03 -> £3,342,705.59 (10.9%); £3,751,893.17 -> £3,342,705.59 (10.9%); £3,751,893.31 -> £3,342,705.58 (10.9%); £3,751,893.47 -> £3,342,705.58 (10.9%); £3,751,893.64 -> £3,342,705.58 (10.9%); £3,751,893.83 -> £3,342,705.57 (10.9%); £3,751,894.04 -> £3,342,705.56 (10.9%); £3,751,894.26 -> £3,342,705.55 (10.9%); £3,751,894.49 -> £3,342,705.55 (10.9%); £3,751,894.72 -> £3,342,705.54 (10.9%); £3,751,894.96 -> £3,342,705.54 (10.9%); £3,751,895.19 -> £3,342,705.53 (10.9%); £3,751,895.43 -> £3,342,705.53 (10.9%); £3,751,895.67 -> £3,342,705.52 (10.9%); £3,751,895.91 -> £3,342,705.52 (10.9%); £3,751,896.14 -> £3,342,705.52 (10.9%); £3,751,896.38 -> £3,342,705.51 (10.9%); £3,751,896.62 -> £3,342,705.51 (10.9%); £3,751,896.86 -> £3,342,705.50 (10.9%); £3,751,897.10 -> £3,342,705.50 (10.9%); £3,751,897.34 -> £3,342,705.50 (10.9%); £3,751,897.58 -> £3,342,705.50 (10.9%); £3,751,897.80 -> £3,342,705.49 (10.9%); £3,751,897.98 -> £3,342,705.47 (10.9%); £3,751,898.15 -> £3,342,705.45 (10.9%); £3,751,898.33 -> £3,342,705.43 (10.9%); £3,751,898.50 -> £3,342,705.41 (10.9%); £3,751,898.68 -> £3,342,705.38 (10.9%); £3,751,898.86 -> £3,342,705.36 (10.9%); £3,751,899.09 -> £3,342,705.33 (10.9%); £3,751,899.32 -> £3,342,705.31 (10.9%); £3,751,899.56 -> £3,342,705.29 (10.9%); £3,751,899.79 -> £3,342,705.27 (10.9%); £3,751,900.03 -> £3,342,705.26 (10.9%); £3,751,900.26 -> £3,342,705.26 (10.9%); £3,751,900.48 -> £3,342,705.25 (10.9%); £3,751,900.67 -> £3,342,705.24 (10.9%); £3,751,900.86 -> £3,342,705.24 (10.9%); £3,751,900.99 -> £3,342,705.24 (10.9%); £3,751,901.14 -> £3,342,705.24 (10.9%); £3,751,901.28 -> £3,342,705.24 (10.9%); £3,751,901.42 -> £3,342,705.24 (10.9%); £3,751,901.56 -> £3,342,705.24 (10.9%); £3,751,901.70 -> £3,342,705.24 (10.9%); £3,751,901.83 -> £3,342,705.24 (10.9%); £3,751,901.98 -> £3,342,705.25 (10.9%); £3,751,902.12 -> £3,342,705.25 (10.9%); £3,751,902.25 -> £3,342,705.25 (10.9%); £3,751,902.39 -> £3,342,705.25 (10.9%); £3,751,902.53 -> £3,342,705.25 (10.9%); £3,751,902.67 -> £3,342,705.25 (10.9%); £3,751,902.82 -> £3,342,705.25 (10.9%); £3,751,903.00 -> £3,342,705.25 (10.9%); £3,751,903.19 -> £3,342,705.24 (10.9%); £3,751,903.39 -> £3,342,705.24 (10.9%); £3,751,903.61 -> £3,342,705.23 (10.9%); £3,751,903.84 -> £3,342,705.22 (10.9%); £3,751,904.09 -> £3,342,705.21 (10.9%); £3,751,904.31 -> £3,342,705.20 (10.9%); £3,751,904.55 -> £3,342,705.19 (10.9%); £3,751,904.78 -> £3,342,705.18 (10.9%); £3,751,905.00 -> £3,342,705.17 (10.9%); £3,751,905.23 -> £3,342,705.16 (10.9%); £3,751,905.46 -> £3,342,705.15 (10.9%); £3,751,905.69 -> £3,342,705.14 (10.9%); £3,751,905.92 -> £3,342,705.14 (10.9%); £3,751,906.16 -> £3,342,705.13 (10.9%); £3,751,906.39 -> £3,342,705.12 (10.9%); £3,751,906.62 -> £3,342,705.12 (10.9%); £3,751,906.85 -> £3,342,705.12 (10.9%); £3,751,907.03 -> £3,342,705.10 (10.9%); £3,751,907.20 -> £3,342,705.09 (10.9%); £3,751,907.37 -> £3,342,705.07 (10.9%); £3,751,907.55 -> £3,342,705.05 (10.9%); £3,751,907.78 -> £3,342,705.03 (10.9%); £3,751,907.96 -> £3,342,705.00 (10.9%); £3,751,908.13 -> £3,342,704.97 (10.9%); £3,751,908.37 -> £3,342,704.94 (10.9%); £3,751,908.60 -> £3,342,704.92 (10.9%); £3,751,908.84 -> £3,342,704.90 (10.9%); £3,751,909.07 -> £3,342,704.88 (10.9%); £3,751,909.30 -> £3,342,704.87 (10.9%); £3,751,909.53 -> £3,342,704.86 (10.9%); £3,751,909.75 -> £3,342,704.86 (10.9%); £3,751,909.94 -> £3,342,704.85 (10.9%); £3,751,910.13 -> £3,342,704.85 (10.9%); £3,751,910.29 -> £3,342,704.85 (10.9%); £3,751,910.44 -> £3,342,704.85 (10.9%); £3,751,910.59 -> £3,342,704.85 (10.9%); £3,751,910.74 -> £3,342,704.86 (10.9%); £3,751,910.90 -> £3,342,704.86 (10.9%); £3,751,911.05 -> £3,342,704.86 (10.9%); £3,751,911.20 -> £3,342,704.86 (10.9%); £3,751,911.36 -> £3,342,704.86 (10.9%); £3,751,911.51 -> £3,342,704.87 (10.9%); £3,751,911.67 -> £3,342,704.87 (10.9%); £3,751,911.82 -> £3,342,704.87 (10.9%); £3,751,911.97 -> £3,342,704.87 (10.9%); £3,751,912.13 -> £3,342,704.86 (10.9%); £3,751,912.30 -> £3,342,704.91 (10.9%); £3,751,912.48 -> £3,342,704.96 (10.9%); £3,751,912.69 -> £3,342,705.01 (10.9%); £3,751,912.91 -> £3,342,705.06 (10.9%); £3,751,913.14 -> £3,342,705.10 (10.9%); £3,751,913.39 -> £3,342,705.15 (10.9%); £3,751,913.64 -> £3,342,705.18 (10.9%); £3,751,913.90 -> £3,342,705.22 (10.9%); £3,751,914.16 -> £3,342,705.22 (10.9%); £3,751,914.41 -> £3,342,705.22 (10.9%); £3,751,914.66 -> £3,342,705.21 (10.9%); £3,751,914.92 -> £3,342,705.21 (10.9%); £3,751,915.18 -> £3,342,705.21 (10.9%); £3,751,915.45 -> £3,342,705.21 (10.9%); £3,751,915.70 -> £3,342,705.21 (10.9%); £3,751,915.96 -> £3,342,705.21 (10.9%); £3,751,916.22 -> £3,342,705.20 (10.9%); £3,751,916.47 -> £3,342,705.21 (10.9%); £3,751,916.73 -> £3,342,705.24 (10.9%); £3,751,917.00 -> £3,342,705.30 (10.9%); £3,751,917.26 -> £3,342,705.37 (10.9%); £3,751,917.51 -> £3,342,705.43 (10.9%); £3,751,917.76 -> £3,342,705.50 (10.9%); £3,751,918.01 -> £3,342,705.57 (10.9%); £3,751,918.26 -> £3,342,705.65 (10.9%); £3,751,918.45 -> £3,342,705.73 (10.9%); £3,751,918.70 -> £3,342,705.71 (10.9%); £3,751,918.95 -> £3,342,705.68 (10.9%); £3,751,919.20 -> £3,342,705.66 (10.9%); £3,751,919.46 -> £3,342,705.64 (10.9%); £3,751,919.71 -> £3,342,705.63 (10.9%); £3,751,919.97 -> £3,342,705.63 (10.9%); £3,751,920.20 -> £3,342,705.62 (10.9%); £3,751,920.43 -> £3,342,705.62 (10.9%); £3,751,920.63 -> £3,342,705.62 (10.9%); £3,751,920.78 -> £3,342,705.62 (10.9%); £3,751,920.93 -> £3,342,705.62 (10.9%); £3,751,921.08 -> £3,342,705.62 (10.9%); £3,751,921.24 -> £3,342,705.62 (10.9%); £3,751,921.39 -> £3,342,705.62 (10.9%); £3,751,921.54 -> £3,342,705.63 (10.9%); £3,751,921.70 -> £3,342,705.63 (10.9%); £3,751,921.84 -> £3,342,705.63 (10.9%); £3,751,922.00 -> £3,342,705.63 (10.9%); £3,751,922.15 -> £3,342,705.63 (10.9%); £3,751,922.31 -> £3,342,705.64 (10.9%); £3,751,922.46 -> £3,342,705.63 (10.9%); £3,751,922.61 -> £3,342,705.63 (10.9%); £3,751,922.77 -> £3,342,705.67 (10.9%); £3,751,922.95 -> £3,342,705.72 (10.9%); £3,751,923.16 -> £3,342,705.78 (10.9%); £3,751,923.38 -> £3,342,705.83 (10.9%); £3,751,923.61 -> £3,342,705.87 (10.9%); £3,751,923.86 -> £3,342,705.92 (10.9%); £3,751,924.11 -> £3,342,705.95 (10.9%); £3,751,924.36 -> £3,342,705.99 (10.9%); £3,751,924.62 -> £3,342,705.99 (10.9%); £3,751,924.88 -> £3,342,705.99 (10.9%); £3,751,925.14 -> £3,342,705.98 (10.9%); £3,751,925.40 -> £3,342,705.98 (10.9%); £3,751,925.65 -> £3,342,705.98 (10.9%); £3,751,925.91 -> £3,342,705.98 (10.9%); £3,751,926.16 -> £3,342,705.98 (10.9%); £3,751,926.42 -> £3,342,705.98 (10.9%); £3,751,926.68 -> £3,342,705.98 (10.9%); £3,751,926.93 -> £3,342,705.98 (10.9%); £3,751,927.18 -> £3,342,706.01 (10.9%); £3,751,927.36 -> £3,342,706.07 (10.9%); £3,751,927.55 -> £3,342,706.14 (10.9%); £3,751,927.80 -> £3,342,706.20 (10.9%); £3,751,927.99 -> £3,342,706.27 (10.9%); £3,751,928.18 -> £3,342,706.34 (10.9%); £3,751,928.44 -> £3,342,706.42 (10.9%); £3,751,928.69 -> £3,342,706.50 (10.9%); £3,751,928.95 -> £3,342,706.48 (10.9%); £3,751,929.21 -> £3,342,706.46 (10.9%); £3,751,929.46 -> £3,342,706.43 (10.9%); £3,751,929.72 -> £3,342,706.41 (10.9%); £3,751,929.97 -> £3,342,706.40 (10.9%); £3,751,930.22 -> £3,342,706.40 (10.9%); £3,751,930.46 -> £3,342,706.39 (10.9%); £3,751,930.67 -> £3,342,706.39 (10.9%); £3,751,930.87 -> £3,342,706.39 (10.9%); £3,751,931.02 -> £3,342,706.39 (10.9%); £3,751,931.17 -> £3,342,706.39 (10.9%); £3,751,931.32 -> £3,342,706.39 (10.9%); £3,751,931.48 -> £3,342,706.39 (10.9%); £3,751,931.63 -> £3,342,706.40 (10.9%); £3,751,931.78 -> £3,342,706.40 (10.9%); £3,751,931.93 -> £3,342,706.40 (10.9%); £3,751,932.08 -> £3,342,706.40 (10.9%); £3,751,932.23 -> £3,342,706.40 (10.9%); £3,751,932.38 -> £3,342,706.41 (10.9%); £3,751,932.53 -> £3,342,706.41 (10.9%); £3,751,932.68 -> £3,342,706.40 (10.9%); £3,751,932.84 -> £3,342,706.40 (10.9%); £3,751,933.00 -> £3,342,706.44 (10.9%); £3,751,933.19 -> £3,342,706.49 (10.9%); £3,751,933.38 -> £3,342,706.54 (10.9%); £3,751,933.61 -> £3,342,706.59 (10.9%); £3,751,933.85 -> £3,342,706.64 (10.9%); £3,751,934.10 -> £3,342,706.68 (10.9%); £3,751,934.35 -> £3,342,706.72 (10.9%); £3,751,934.59 -> £3,342,706.75 (10.9%); £3,751,934.85 -> £3,342,706.75 (10.9%); £3,751,935.10 -> £3,342,706.75 (10.9%); £3,751,935.35 -> £3,342,706.75 (10.9%); £3,751,935.60 -> £3,342,706.74 (10.9%); £3,751,935.87 -> £3,342,706.74 (10.9%); £3,751,936.12 -> £3,342,706.74 (10.9%); £3,751,936.37 -> £3,342,706.74 (10.9%); £3,751,936.63 -> £3,342,706.74 (10.9%); £3,751,936.88 -> £3,342,706.74 (10.9%); £3,751,937.13 -> £3,342,706.74 (10.9%); £3,751,937.37 -> £3,342,706.77 (10.9%); £3,751,937.63 -> £3,342,706.83 (10.9%); £3,751,937.82 -> £3,342,706.90 (10.9%); £3,751,938.07 -> £3,342,706.96 (10.9%); £3,751,938.32 -> £3,342,707.03 (10.9%); £3,751,938.52 -> £3,342,707.10 (10.9%); £3,751,938.76 -> £3,342,707.18 (10.9%); £3,751,938.94 -> £3,342,707.26 (10.9%); £3,751,939.20 -> £3,342,707.24 (10.9%); £3,751,939.45 -> £3,342,707.21 (10.9%); £3,751,939.70 -> £3,342,707.19 (10.9%); £3,751,939.95 -> £3,342,707.17 (10.9%); £3,751,940.20 -> £3,342,707.16 (10.9%); £3,751,940.44 -> £3,342,707.16 (10.9%); £3,751,940.68 -> £3,342,707.15 (10.9%); £3,751,940.89 -> £3,342,707.15 (10.9%); £3,751,941.09 -> £3,342,707.15 (10.9%); £3,751,941.24 -> £3,342,707.15 (10.9%); £3,751,941.39 -> £3,342,707.15 (10.9%); £3,751,941.53 -> £3,342,707.15 (10.9%); £3,751,941.69 -> £3,342,707.15 (10.9%); £3,751,941.84 -> £3,342,707.15 (10.9%); £3,751,941.99 -> £3,342,707.15 (10.9%); £3,751,942.14 -> £3,342,707.16 (10.9%); £3,751,942.29 -> £3,342,707.16 (10.9%); £3,751,942.44 -> £3,342,707.16 (10.9%); £3,751,942.59 -> £3,342,707.16 (10.9%); £3,751,942.74 -> £3,342,707.16 (10.9%); £3,751,942.89 -> £3,342,707.16 (10.9%); £3,751,943.03 -> £3,342,707.15 (10.9%); £3,751,943.20 -> £3,342,707.20 (10.9%); £3,751,943.38 -> £3,342,707.25 (10.9%); £3,751,943.58 -> £3,342,707.30 (10.9%); £3,751,943.80 -> £3,342,707.35 (10.9%); £3,751,944.02 -> £3,342,707.39 (10.9%); £3,751,944.27 -> £3,342,707.44 (10.9%); £3,751,944.53 -> £3,342,707.47 (10.9%); £3,751,944.77 -> £3,342,707.51 (10.9%); £3,751,945.02 -> £3,342,707.51 (10.9%); £3,751,945.28 -> £3,342,707.51 (10.9%); £3,751,945.52 -> £3,342,707.50 (10.9%); £3,751,945.77 -> £3,342,707.50 (10.9%); £3,751,946.01 -> £3,342,707.50 (10.9%); £3,751,946.25 -> £3,342,707.50 (10.9%); £3,751,946.50 -> £3,342,707.50 (10.9%); £3,751,946.75 -> £3,342,707.50 (10.9%); £3,751,947.00 -> £3,342,707.50 (10.9%); £3,751,947.25 -> £3,342,707.50 (10.9%); £3,751,947.50 -> £3,342,707.53 (10.9%); £3,751,947.69 -> £3,342,707.59 (10.9%); £3,751,947.88 -> £3,342,707.65 (10.9%); £3,751,948.06 -> £3,342,707.72 (10.9%); £3,751,948.24 -> £3,342,707.79 (10.9%); £3,751,948.43 -> £3,342,707.85 (10.9%); £3,751,948.61 -> £3,342,707.94 (10.9%); £3,751,948.80 -> £3,342,708.02 (10.9%); £3,751,949.04 -> £3,342,707.99 (10.9%); £3,751,949.29 -> £3,342,707.97 (10.9%); £3,751,949.55 -> £3,342,707.94 (10.9%); £3,751,949.80 -> £3,342,707.92 (10.9%); £3,751,950.05 -> £3,342,707.91 (10.9%); £3,751,950.29 -> £3,342,707.91 (10.9%); £3,751,950.53 -> £3,342,707.90 (10.9%); £3,751,950.73 -> £3,342,707.90 (10.9%); £3,751,950.93 -> £3,342,707.90 (10.9%); £3,751,951.07 -> £3,342,707.90 (10.9%); £3,751,951.23 -> £3,342,707.90 (10.9%); £3,751,951.37 -> £3,342,707.90 (10.9%); £3,751,951.52 -> £3,342,707.90 (10.9%); £3,751,951.66 -> £3,342,707.90 (10.9%); £3,751,951.81 -> £3,342,707.91 (10.9%); £3,751,951.96 -> £3,342,707.91 (10.9%); £3,751,952.10 -> £3,342,707.91 (10.9%); £3,751,952.25 -> £3,342,707.91 (10.9%); £3,751,952.40 -> £3,342,707.91 (10.9%); £3,751,952.55 -> £3,342,707.91 (10.9%); £3,751,952.70 -> £3,342,707.91 (10.9%); £3,751,952.85 -> £3,342,707.90 (10.9%); £3,751,953.01 -> £3,342,707.95 (10.9%); £3,751,953.20 -> £3,342,708.00 (10.9%); £3,751,953.39 -> £3,342,708.05 (10.9%); £3,751,953.60 -> £3,342,708.10 (10.9%); £3,751,953.83 -> £3,342,708.14 (10.9%); £3,751,954.08 -> £3,342,708.19 (10.9%); £3,751,954.31 -> £3,342,708.22 (10.9%); £3,751,954.55 -> £3,342,708.26 (10.9%); £3,751,954.80 -> £3,342,708.26 (10.9%); £3,751,955.05 -> £3,342,708.26 (10.9%); £3,751,955.29 -> £3,342,708.25 (10.9%); £3,751,955.55 -> £3,342,708.25 (10.9%); £3,751,955.79 -> £3,342,708.25 (10.9%); £3,751,956.03 -> £3,342,708.25 (10.9%); £3,751,956.27 -> £3,342,708.25 (10.9%); £3,751,956.51 -> £3,342,708.25 (10.9%); £3,751,956.76 -> £3,342,708.24 (10.9%); £3,751,957.00 -> £3,342,708.25 (10.9%); £3,751,957.24 -> £3,342,708.28 (10.9%); £3,751,957.43 -> £3,342,708.34 (10.9%); £3,751,957.61 -> £3,342,708.40 (10.9%); £3,751,957.80 -> £3,342,708.47 (10.9%); £3,751,957.98 -> £3,342,708.53 (10.9%); £3,751,958.16 -> £3,342,708.60 (10.9%); £3,751,958.35 -> £3,342,708.68 (10.9%); £3,751,958.53 -> £3,342,708.76 (10.9%); £3,751,958.78 -> £3,342,708.74 (10.9%); £3,751,959.02 -> £3,342,708.71 (10.9%); £3,751,959.27 -> £3,342,708.69 (10.9%); £3,751,959.51 -> £3,342,708.67 (10.9%); £3,751,959.76 -> £3,342,708.66 (10.9%); £3,751,960.01 -> £3,342,708.66 (10.9%); £3,751,960.24 -> £3,342,708.65 (10.9%); £3,751,960.45 -> £3,342,708.65 (10.9%); £3,751,960.65 -> £3,342,708.64 (10.9%); £3,751,960.77 -> £3,342,708.64 (10.9%); £3,751,960.91 -> £3,342,708.64 (10.9%); £3,751,961.04 -> £3,342,708.64 (10.9%); £3,751,961.16 -> £3,342,708.64 (10.9%); £3,751,961.29 -> £3,342,708.65 (10.9%); £3,751,961.42 -> £3,342,708.65 (10.9%); £3,751,961.55 -> £3,342,708.65 (10.9%); £3,751,961.68 -> £3,342,708.65 (10.9%); £3,751,961.81 -> £3,342,708.65 (10.9%); £3,751,961.93 -> £3,342,708.65 (10.9%); £3,751,962.06 -> £3,342,708.66 (10.9%); £3,751,962.19 -> £3,342,708.65 (10.9%); £3,751,962.32 -> £3,342,708.65 (10.9%); £3,751,962.46 -> £3,342,708.65 (10.9%); £3,751,962.62 -> £3,342,708.64 (10.9%); £3,751,962.79 -> £3,342,708.64 (10.9%); £3,751,962.97 -> £3,342,708.63 (10.9%); £3,751,963.17 -> £3,342,708.62 (10.9%); £3,751,963.38 -> £3,342,708.61 (10.9%); £3,751,963.59 -> £3,342,708.61 (10.9%); £3,751,963.80 -> £3,342,708.60 (10.9%); £3,751,964.01 -> £3,342,708.60 (10.9%); £3,751,964.22 -> £3,342,708.59 (10.9%); £3,751,964.43 -> £3,342,708.59 (10.9%); £3,751,964.65 -> £3,342,708.58 (10.9%); £3,751,964.86 -> £3,342,708.58 (10.9%); £3,751,965.07 -> £3,342,708.58 (10.9%); £3,751,965.29 -> £3,342,708.57 (10.9%); £3,751,965.50 -> £3,342,708.57 (10.9%); £3,751,965.71 -> £3,342,708.57 (10.9%); £3,751,965.92 -> £3,342,708.57 (10.9%); £3,751,966.14 -> £3,342,708.57 (10.9%); £3,751,966.30 -> £3,342,708.55 (10.9%); £3,751,966.46 -> £3,342,708.54 (10.9%); £3,751,966.62 -> £3,342,708.52 (10.9%); £3,751,966.78 -> £3,342,708.50 (10.9%); £3,751,966.94 -> £3,342,708.48 (10.9%); £3,751,967.09 -> £3,342,708.45 (10.9%); £3,751,967.30 -> £3,342,708.42 (10.9%); £3,751,967.52 -> £3,342,708.40 (10.9%); £3,751,967.74 -> £3,342,708.38 (10.9%); £3,751,967.95 -> £3,342,708.35 (10.9%); £3,751,968.16 -> £3,342,708.33 (10.9%); £3,751,968.37 -> £3,342,708.33 (10.9%); £3,751,968.59 -> £3,342,708.32 (10.9%); £3,751,968.78 -> £3,342,708.32 (10.9%); £3,751,968.96 -> £3,342,708.31 (10.9%); £3,751,969.12 -> £3,342,708.31 (10.9%); £3,751,969.25 -> £3,342,708.31 (10.9%); £3,751,969.38 -> £3,342,708.31 (10.9%); £3,751,969.50 -> £3,342,708.31 (10.9%); £3,751,969.62 -> £3,342,708.31 (10.9%); £3,751,969.75 -> £3,342,708.31 (10.9%); £3,751,969.88 -> £3,342,708.31 (10.9%); £3,751,970.01 -> £3,342,708.31 (10.9%); £3,751,970.13 -> £3,342,708.31 (10.9%); £3,751,970.26 -> £3,342,708.31 (10.9%); £3,751,970.39 -> £3,342,708.32 (10.9%); £3,751,970.51 -> £3,342,708.32 (10.9%); £3,751,970.64 -> £3,342,708.32 (10.9%); £3,751,970.76 -> £3,342,708.32 (10.9%); £3,751,970.91 -> £3,342,708.32 (10.9%); £3,751,971.06 -> £3,342,708.31 (10.9%); £3,751,971.24 -> £3,342,708.31 (10.9%); £3,751,971.42 -> £3,342,708.30 (10.9%); £3,751,971.62 -> £3,342,708.29 (10.9%); £3,751,971.82 -> £3,342,708.28 (10.9%); £3,751,972.04 -> £3,342,708.27 (10.9%); £3,751,972.24 -> £3,342,708.27 (10.9%); £3,751,972.45 -> £3,342,708.26 (10.9%); £3,751,972.67 -> £3,342,708.25 (10.9%); £3,751,972.89 -> £3,342,708.24 (10.9%); £3,751,973.10 -> £3,342,708.23 (10.9%); £3,751,973.30 -> £3,342,708.22 (10.9%); £3,751,973.51 -> £3,342,708.21 (10.9%); £3,751,973.73 -> £3,342,708.21 (10.9%); £3,751,973.93 -> £3,342,708.20 (10.9%); £3,751,974.14 -> £3,342,708.19 (10.9%); £3,751,974.35 -> £3,342,708.19 (10.9%); £3,751,974.56 -> £3,342,708.19 (10.9%); £3,751,974.72 -> £3,342,708.17 (10.9%); £3,751,974.89 -> £3,342,708.16 (10.9%); £3,751,975.05 -> £3,342,708.14 (10.9%); £3,751,975.20 -> £3,342,708.12 (10.9%); £3,751,975.36 -> £3,342,708.10 (10.9%); £3,751,975.53 -> £3,342,708.07 (10.9%); £3,751,975.68 -> £3,342,708.04 (10.9%); £3,751,975.90 -> £3,342,708.01 (10.9%); £3,751,976.12 -> £3,342,707.99 (10.9%); £3,751,976.32 -> £3,342,707.97 (10.9%); £3,751,976.54 -> £3,342,707.94 (10.9%); £3,751,976.75 -> £3,342,707.94 (10.9%); £3,751,976.95 -> £3,342,707.93 (10.9%); £3,751,977.15 -> £3,342,707.93 (10.9%); £3,751,977.33 -> £3,342,707.92 (10.9%); £3,751,977.50 -> £3,342,707.92 (10.9%); £3,751,977.65 -> £3,342,707.92 (10.9%); £3,751,977.79 -> £3,342,707.92 (10.9%); £3,751,977.94 -> £3,342,707.92 (10.9%); £3,751,978.09 -> £3,342,707.92 (10.9%); £3,751,978.24 -> £3,342,707.93 (10.9%); £3,751,978.38 -> £3,342,707.93 (10.9%); £3,751,978.52 -> £3,342,707.93 (10.9%); £3,751,978.67 -> £3,342,707.93 (10.9%); £3,751,978.82 -> £3,342,707.93 (10.9%); £3,751,978.96 -> £3,342,707.94 (10.9%); £3,751,979.10 -> £3,342,707.94 (10.9%); £3,751,979.25 -> £3,342,707.93 (10.9%); £3,751,979.39 -> £3,342,707.93 (10.9%); £3,751,979.55 -> £3,342,707.97 (10.9%); £3,751,979.73 -> £3,342,708.02 (10.9%); £3,751,979.91 -> £3,342,708.08 (10.9%); £3,751,980.12 -> £3,342,708.12 (10.9%); £3,751,980.34 -> £3,342,708.17 (10.9%); £3,751,980.58 -> £3,342,708.21 (10.9%); £3,751,980.82 -> £3,342,708.25 (10.9%); £3,751,981.07 -> £3,342,708.29 (10.9%); £3,751,981.31 -> £3,342,708.28 (10.9%); £3,751,981.56 -> £3,342,708.28 (10.9%); £3,751,981.80 -> £3,342,708.28 (10.9%); £3,751,982.04 -> £3,342,708.28 (10.9%); £3,751,982.28 -> £3,342,708.28 (10.9%); £3,751,982.52 -> £3,342,708.28 (10.9%); £3,751,982.76 -> £3,342,708.28 (10.9%); £3,751,983.01 -> £3,342,708.28 (10.9%); £3,751,983.26 -> £3,342,708.27 (10.9%); £3,751,983.50 -> £3,342,708.28 (10.9%); £3,751,983.73 -> £3,342,708.31 (10.9%); £3,751,983.92 -> £3,342,708.37 (10.9%); £3,751,984.11 -> £3,342,708.43 (10.9%); £3,751,984.29 -> £3,342,708.50 (10.9%); £3,751,984.47 -> £3,342,708.56 (10.9%); £3,751,984.65 -> £3,342,708.63 (10.9%); £3,751,984.83 -> £3,342,708.71 (10.9%); £3,751,985.00 -> £3,342,708.80 (10.9%); £3,751,985.25 -> £3,342,708.77 (10.9%); £3,751,985.49 -> £3,342,708.75 (10.9%); £3,751,985.72 -> £3,342,708.72 (10.9%); £3,751,985.96 -> £3,342,708.70 (10.9%); £3,751,986.21 -> £3,342,708.69 (10.9%); £3,751,986.45 -> £3,342,708.69 (10.9%); £3,751,986.67 -> £3,342,708.68 (10.9%); £3,751,986.88 -> £3,342,708.68 (10.9%); £3,751,987.07 -> £3,342,708.68 (10.9%); £3,751,987.21 -> £3,342,708.68 (10.9%); £3,751,987.36 -> £3,342,708.68 (10.9%); £3,751,987.50 -> £3,342,708.68 (10.9%); £3,751,987.64 -> £3,342,708.68 (10.9%); £3,751,987.79 -> £3,342,708.68 (10.9%); £3,751,987.93 -> £3,342,708.69 (10.9%); £3,751,988.06 -> £3,342,708.69 (10.9%); £3,751,988.20 -> £3,342,708.69 (10.9%); £3,751,988.35 -> £3,342,708.69 (10.9%); £3,751,988.50 -> £3,342,708.69 (10.9%); £3,751,988.64 -> £3,342,708.70 (10.9%); £3,751,988.78 -> £3,342,708.69 (10.9%); £3,751,988.93 -> £3,342,708.69 (10.9%); £3,751,989.09 -> £3,342,708.73 (10.9%); £3,751,989.27 -> £3,342,708.78 (10.9%); £3,751,989.45 -> £3,342,708.83 (10.9%); £3,751,989.67 -> £3,342,708.88 (10.9%); £3,751,989.90 -> £3,342,708.93 (10.9%); £3,751,990.14 -> £3,342,708.97 (10.9%); £3,751,990.38 -> £3,342,709.01 (10.9%); £3,751,990.61 -> £3,342,709.04 (10.9%); £3,751,990.85 -> £3,342,709.04 (10.9%); £3,751,991.09 -> £3,342,709.04 (10.9%); £3,751,991.32 -> £3,342,709.04 (10.9%); £3,751,991.57 -> £3,342,709.03 (10.9%); £3,751,991.81 -> £3,342,709.03 (10.9%); £3,751,992.03 -> £3,342,709.03 (10.9%); £3,751,992.27 -> £3,342,709.03 (10.9%); £3,751,992.51 -> £3,342,709.03 (10.9%); £3,751,992.74 -> £3,342,709.03 (10.9%); £3,751,992.98 -> £3,342,709.03 (10.9%); £3,751,993.22 -> £3,342,709.06 (10.9%); £3,751,993.41 -> £3,342,709.12 (10.9%); £3,751,993.59 -> £3,342,709.19 (10.9%); £3,751,993.77 -> £3,342,709.26 (10.9%); £3,751,994.02 -> £3,342,709.32 (10.9%); £3,751,994.27 -> £3,342,709.39 (10.9%); £3,751,994.51 -> £3,342,709.47 (10.9%); £3,751,994.70 -> £3,342,709.56 (10.9%); £3,751,994.93 -> £3,342,709.53 (10.9%); £3,751,995.17 -> £3,342,709.51 (10.9%); £3,751,995.41 -> £3,342,709.48 (10.9%); £3,751,995.65 -> £3,342,709.46 (10.9%); £3,751,995.90 -> £3,342,709.45 (10.9%); £3,751,996.14 -> £3,342,709.45 (10.9%); £3,751,996.36 -> £3,342,709.44 (10.9%); £3,751,996.56 -> £3,342,709.44 (10.9%); £3,751,996.75 -> £3,342,709.44 (10.9%); £3,751,996.89 -> £3,342,709.44 (10.9%); £3,751,997.03 -> £3,342,709.44 (10.9%); £3,751,997.17 -> £3,342,709.44 (10.9%); £3,751,997.30 -> £3,342,709.44 (10.9%); £3,751,997.45 -> £3,342,709.44 (10.9%); £3,751,997.59 -> £3,342,709.45 (10.9%); £3,751,997.73 -> £3,342,709.45 (10.9%); £3,751,997.87 -> £3,342,709.45 (10.9%); £3,751,998.02 -> £3,342,709.45 (10.9%); £3,751,998.16 -> £3,342,709.45 (10.9%); £3,751,998.30 -> £3,342,709.46 (10.9%); £3,751,998.44 -> £3,342,709.45 (10.9%); £3,751,998.58 -> £3,342,709.45 (10.9%); £3,751,998.74 -> £3,342,709.49 (10.9%); £3,751,998.91 -> £3,342,709.55 (10.9%); £3,751,999.10 -> £3,342,709.60 (10.9%); £3,751,999.30 -> £3,342,709.65 (10.9%); £3,751,999.52 -> £3,342,709.69 (10.9%); £3,751,999.76 -> £3,342,709.74 (10.9%); £3,752,000.00 -> £3,342,709.77 (10.9%); £3,752,000.23 -> £3,342,709.81 (10.9%); £3,752,000.47 -> £3,342,709.81 (10.9%); £3,752,000.71 -> £3,342,709.81 (10.9%); £3,752,000.94 -> £3,342,709.80 (10.9%); £3,752,001.18 -> £3,342,709.80 (10.9%); £3,752,001.42 -> £3,342,709.80 (10.9%); £3,752,001.66 -> £3,342,709.80 (10.9%); £3,752,001.89 -> £3,342,709.80 (10.9%); £3,752,002.14 -> £3,342,709.80 (10.9%); £3,752,002.38 -> £3,342,709.79 (10.9%); £3,752,002.61 -> £3,342,709.80 (10.9%); £3,752,002.85 -> £3,342,709.83 (10.9%); £3,752,003.02 -> £3,342,709.89 (10.9%); £3,752,003.20 -> £3,342,709.95 (10.9%); £3,752,003.44 -> £3,342,710.02 (10.9%); £3,752,003.68 -> £3,342,710.09 (10.9%); £3,752,003.92 -> £3,342,710.16 (10.9%); £3,752,004.16 -> £3,342,710.24 (10.9%); £3,752,004.40 -> £3,342,710.32 (10.9%); £3,752,004.64 -> £3,342,710.30 (10.9%); £3,752,004.88 -> £3,342,710.28 (10.9%); £3,752,005.11 -> £3,342,710.25 (10.9%); £3,752,005.35 -> £3,342,710.23 (10.9%); £3,752,005.58 -> £3,342,710.22 (10.9%); £3,752,005.81 -> £3,342,710.22 (10.9%); £3,752,006.03 -> £3,342,710.21 (10.9%); £3,752,006.22 -> £3,342,710.21 (10.9%); £3,752,006.40 -> £3,342,710.21 (10.9%); £3,752,006.54 -> £3,342,710.21 (10.9%); £3,752,006.68 -> £3,342,710.21 (10.9%); £3,752,006.83 -> £3,342,710.21 (10.9%); £3,752,006.97 -> £3,342,710.21 (10.9%); £3,752,007.11 -> £3,342,710.21 (10.9%); £3,752,007.25 -> £3,342,710.21 (10.9%); £3,752,007.39 -> £3,342,710.22 (10.9%); £3,752,007.53 -> £3,342,710.22 (10.9%); £3,752,007.68 -> £3,342,710.22 (10.9%); £3,752,007.82 -> £3,342,710.22 (10.9%); £3,752,007.97 -> £3,342,710.22 (10.9%); £3,752,008.12 -> £3,342,710.22 (10.9%); £3,752,008.26 -> £3,342,710.21 (10.9%); £3,752,008.41 -> £3,342,710.26 (10.9%); £3,752,008.58 -> £3,342,710.31 (10.9%); £3,752,008.77 -> £3,342,710.36 (10.9%); £3,752,008.98 -> £3,342,710.41 (10.9%); £3,752,009.20 -> £3,342,710.45 (10.9%); £3,752,009.43 -> £3,342,710.50 (10.9%); £3,752,009.67 -> £3,342,710.53 (10.9%); £3,752,009.90 -> £3,342,710.57 (10.9%); £3,752,010.13 -> £3,342,710.57 (10.9%); £3,752,010.36 -> £3,342,710.57 (10.9%); £3,752,010.59 -> £3,342,710.56 (10.9%); £3,752,010.83 -> £3,342,710.56 (10.9%); £3,752,011.07 -> £3,342,710.56 (10.9%); £3,752,011.31 -> £3,342,710.56 (10.9%); £3,752,011.55 -> £3,342,710.56 (10.9%); £3,752,011.78 -> £3,342,710.56 (10.9%); £3,752,012.01 -> £3,342,710.56 (10.9%); £3,752,012.25 -> £3,342,710.56 (10.9%); £3,752,012.49 -> £3,342,710.59 (10.9%); £3,752,012.67 -> £3,342,710.65 (10.9%); £3,752,012.85 -> £3,342,710.72 (10.9%); £3,752,013.03 -> £3,342,710.78 (10.9%); £3,752,013.20 -> £3,342,710.85 (10.9%); £3,752,013.38 -> £3,342,710.92 (10.9%); £3,752,013.55 -> £3,342,711.00 (10.9%); £3,752,013.73 -> £3,342,711.08 (10.9%); £3,752,013.96 -> £3,342,711.05 (10.9%); £3,752,014.19 -> £3,342,711.03 (10.9%); £3,752,014.43 -> £3,342,711.01 (10.9%); £3,752,014.65 -> £3,342,710.99 (10.9%); £3,752,014.89 -> £3,342,710.98 (10.9%); £3,752,015.13 -> £3,342,710.98 (10.9%); £3,752,015.35 -> £3,342,710.97 (10.9%); £3,752,015.56 -> £3,342,710.97 (10.9%); £3,752,015.75 -> £3,342,710.97 (10.9%); £3,752,015.89 -> £3,342,710.97 (10.9%); £3,752,016.03 -> £3,342,710.97 (10.9%); £3,752,016.18 -> £3,342,710.97 (10.9%); £3,752,016.32 -> £3,342,710.97 (10.9%); £3,752,016.46 -> £3,342,710.97 (10.9%); £3,752,016.61 -> £3,342,710.97 (10.9%); £3,752,016.75 -> £3,342,710.98 (10.9%); £3,752,016.90 -> £3,342,710.98 (10.9%); £3,752,017.03 -> £3,342,710.98 (10.9%); £3,752,017.18 -> £3,342,710.98 (10.9%); £3,752,017.33 -> £3,342,710.98 (10.9%); £3,752,017.47 -> £3,342,710.98 (10.9%); £3,752,017.61 -> £3,342,710.97 (10.9%); £3,752,017.77 -> £3,342,711.02 (10.9%); £3,752,017.95 -> £3,342,711.07 (10.9%); £3,752,018.14 -> £3,342,711.12 (10.9%); £3,752,018.34 -> £3,342,711.17 (10.9%); £3,752,018.56 -> £3,342,711.22 (10.9%); £3,752,018.80 -> £3,342,711.26 (10.9%); £3,752,019.03 -> £3,342,711.30 (10.9%); £3,752,019.27 -> £3,342,711.33 (10.9%); £3,752,019.50 -> £3,342,711.33 (10.9%); £3,752,019.75 -> £3,342,711.33 (10.9%); £3,752,019.99 -> £3,342,711.33 (10.9%); £3,752,020.23 -> £3,342,711.33 (10.9%); £3,752,020.47 -> £3,342,711.32 (10.9%); £3,752,020.71 -> £3,342,711.32 (10.9%); £3,752,020.93 -> £3,342,711.32 (10.9%); £3,752,021.17 -> £3,342,711.32 (10.9%); £3,752,021.41 -> £3,342,711.32 (10.9%); £3,752,021.65 -> £3,342,711.32 (10.9%); £3,752,021.89 -> £3,342,711.36 (10.9%); £3,752,022.12 -> £3,342,711.42 (10.9%); £3,752,022.30 -> £3,342,711.48 (10.9%); £3,752,022.48 -> £3,342,711.55 (10.9%); £3,752,022.66 -> £3,342,711.61 (10.9%); £3,752,022.84 -> £3,342,711.68 (10.9%); £3,752,023.08 -> £3,342,711.77 (10.9%); £3,752,023.32 -> £3,342,711.85 (10.9%); £3,752,023.57 -> £3,342,711.82 (10.9%); £3,752,023.81 -> £3,342,711.80 (10.9%); £3,752,024.05 -> £3,342,711.78 (10.9%); £3,752,024.30 -> £3,342,711.75 (10.9%); £3,752,024.54 -> £3,342,711.75 (10.9%); £3,752,024.78 -> £3,342,711.74 (10.9%); £3,752,025.00 -> £3,342,711.74 (10.9%); £3,752,025.20 -> £3,342,711.73 (10.9%); £3,752,025.39 -> £3,342,711.73 (10.9%); £3,752,025.52 -> £3,342,711.73 (10.9%); £3,752,025.65 -> £3,342,711.73 (10.9%); £3,752,025.77 -> £3,342,711.73 (10.9%); £3,752,025.90 -> £3,342,711.73 (10.9%); £3,752,026.03 -> £3,342,711.73 (10.9%); £3,752,026.16 -> £3,342,711.74 (10.9%); £3,752,026.29 -> £3,342,711.74 (10.9%); £3,752,026.42 -> £3,342,711.74 (10.9%); £3,752,026.54 -> £3,342,711.74 (10.9%); £3,752,026.67 -> £3,342,711.74 (10.9%); £3,752,026.80 -> £3,342,711.75 (10.9%); £3,752,026.93 -> £3,342,711.74 (10.9%); £3,752,027.06 -> £3,342,711.74 (10.9%); £3,752,027.20 -> £3,342,711.74 (10.9%); £3,752,027.36 -> £3,342,711.73 (10.9%); £3,752,027.53 -> £3,342,711.73 (10.9%); £3,752,027.72 -> £3,342,711.72 (10.9%); £3,752,027.93 -> £3,342,711.71 (10.9%); £3,752,028.14 -> £3,342,711.70 (10.9%); £3,752,028.35 -> £3,342,711.70 (10.9%); £3,752,028.57 -> £3,342,711.69 (10.9%); £3,752,028.78 -> £3,342,711.69 (10.9%); £3,752,028.99 -> £3,342,711.68 (10.9%); £3,752,029.21 -> £3,342,711.68 (10.9%); £3,752,029.42 -> £3,342,711.67 (10.9%); £3,752,029.63 -> £3,342,711.67 (10.9%); £3,752,029.85 -> £3,342,711.67 (10.9%); £3,752,030.07 -> £3,342,711.66 (10.9%); £3,752,030.28 -> £3,342,711.66 (10.9%); £3,752,030.50 -> £3,342,711.66 (10.9%); £3,752,030.70 -> £3,342,711.66 (10.9%); £3,752,030.92 -> £3,342,711.66 (10.9%); £3,752,031.09 -> £3,342,711.64 (10.9%); £3,752,031.25 -> £3,342,711.63 (10.9%); £3,752,031.41 -> £3,342,711.61 (10.9%); £3,752,031.57 -> £3,342,711.59 (10.9%); £3,752,031.73 -> £3,342,711.57 (10.9%); £3,752,031.90 -> £3,342,711.54 (10.9%); £3,752,032.06 -> £3,342,711.51 (10.9%); £3,752,032.27 -> £3,342,711.49 (10.9%); £3,752,032.49 -> £3,342,711.47 (10.9%); £3,752,032.70 -> £3,342,711.44 (10.9%); £3,752,032.92 -> £3,342,711.42 (10.9%); £3,752,033.13 -> £3,342,711.42 (10.9%); £3,752,033.34 -> £3,342,711.41 (10.9%); £3,752,033.55 -> £3,342,711.41 (10.9%); £3,752,033.73 -> £3,342,711.40 (10.9%); £3,752,033.89 -> £3,342,711.40 (10.9%); £3,752,034.02 -> £3,342,711.40 (10.9%); £3,752,034.15 -> £3,342,711.39 (10.9%); £3,752,034.28 -> £3,342,711.40 (10.9%); £3,752,034.41 -> £3,342,711.40 (10.9%); £3,752,034.54 -> £3,342,711.40 (10.9%); £3,752,034.67 -> £3,342,711.40 (10.9%); £3,752,034.80 -> £3,342,711.40 (10.9%); £3,752,034.92 -> £3,342,711.40 (10.9%); £3,752,035.05 -> £3,342,711.40 (10.9%); £3,752,035.18 -> £3,342,711.41 (10.9%); £3,752,035.31 -> £3,342,711.41 (10.9%); £3,752,035.44 -> £3,342,711.41 (10.9%); £3,752,035.57 -> £3,342,711.41 (10.9%); £3,752,035.71 -> £3,342,711.41 (10.9%); £3,752,035.87 -> £3,342,711.40 (10.9%); £3,752,036.04 -> £3,342,711.40 (10.9%); £3,752,036.23 -> £3,342,711.39 (10.9%); £3,752,036.43 -> £3,342,711.38 (10.9%); £3,752,036.65 -> £3,342,711.37 (10.9%); £3,752,036.87 -> £3,342,711.37 (10.9%); £3,752,037.09 -> £3,342,711.36 (10.9%); £3,752,037.30 -> £3,342,711.35 (10.9%); £3,752,037.51 -> £3,342,711.34 (10.9%); £3,752,037.72 -> £3,342,711.33 (10.9%); £3,752,037.94 -> £3,342,711.32 (10.9%); £3,752,038.15 -> £3,342,711.31 (10.9%); £3,752,038.37 -> £3,342,711.31 (10.9%); £3,752,038.58 -> £3,342,711.30 (10.9%); £3,752,038.79 -> £3,342,711.29 (10.9%); £3,752,039.01 -> £3,342,711.29 (10.9%); £3,752,039.23 -> £3,342,711.29 (10.9%); £3,752,039.45 -> £3,342,711.28 (10.9%); £3,752,039.61 -> £3,342,711.27 (10.9%); £3,752,039.77 -> £3,342,711.25 (10.9%); £3,752,039.93 -> £3,342,711.23 (10.9%); £3,752,040.08 -> £3,342,711.21 (10.9%); £3,752,040.25 -> £3,342,711.19 (10.9%); £3,752,040.41 -> £3,342,711.16 (10.9%); £3,752,040.56 -> £3,342,711.14 (10.9%); £3,752,040.79 -> £3,342,711.11 (10.9%); £3,752,041.00 -> £3,342,711.09 (10.9%); £3,752,041.22 -> £3,342,711.06 (10.9%); £3,752,041.43 -> £3,342,711.04 (10.9%); £3,752,041.64 -> £3,342,711.03 (10.9%); £3,752,041.86 -> £3,342,711.03 (10.9%); £3,752,042.05 -> £3,342,711.02 (10.9%); £3,752,042.23 -> £3,342,711.02 (10.9%); £3,752,042.39 -> £3,342,711.02 (10.9%); £3,752,042.54 -> £3,342,711.02 (10.9%); £3,752,042.69 -> £3,342,711.02 (10.9%); £3,752,042.84 -> £3,342,711.02 (10.9%); £3,752,042.98 -> £3,342,711.02 (10.9%); £3,752,043.12 -> £3,342,711.02 (10.9%); £3,752,043.27 -> £3,342,711.02 (10.9%); £3,752,043.42 -> £3,342,711.03 (10.9%); £3,752,043.57 -> £3,342,711.03 (10.9%); £3,752,043.71 -> £3,342,711.03 (10.9%); £3,752,043.85 -> £3,342,711.03 (10.9%); £3,752,044.00 -> £3,342,711.03 (10.9%); £3,752,044.15 -> £3,342,711.03 (10.9%); £3,752,044.29 -> £3,342,711.02 (10.9%); £3,752,044.45 -> £3,342,711.07 (10.9%); £3,752,044.64 -> £3,342,711.12 (10.9%); £3,752,044.83 -> £3,342,711.17 (10.9%); £3,752,045.05 -> £3,342,711.22 (10.9%); £3,752,045.28 -> £3,342,711.27 (10.9%); £3,752,045.53 -> £3,342,711.31 (10.9%); £3,752,045.78 -> £3,342,711.35 (10.9%); £3,752,046.03 -> £3,342,711.38 (10.9%); £3,752,046.28 -> £3,342,711.38 (10.9%); £3,752,046.51 -> £3,342,711.38 (10.9%); £3,752,046.76 -> £3,342,711.38 (10.9%); £3,752,047.02 -> £3,342,711.38 (10.9%); £3,752,047.26 -> £3,342,711.37 (10.9%); £3,752,047.52 -> £3,342,711.37 (10.9%); £3,752,047.77 -> £3,342,711.37 (10.9%); £3,752,048.02 -> £3,342,711.37 (10.9%); £3,752,048.26 -> £3,342,711.37 (10.9%); £3,752,048.51 -> £3,342,711.37 (10.9%); £3,752,048.76 -> £3,342,711.41 (10.9%); £3,752,049.01 -> £3,342,711.47 (10.9%); £3,752,049.19 -> £3,342,711.53 (10.9%); £3,752,049.37 -> £3,342,711.60 (10.9%); £3,752,049.56 -> £3,342,711.67 (10.9%); £3,752,049.74 -> £3,342,711.73 (10.9%); £3,752,049.92 -> £3,342,711.82 (10.9%); £3,752,050.10 -> £3,342,711.90 (10.9%); £3,752,050.34 -> £3,342,711.87 (10.9%); £3,752,050.58 -> £3,342,711.85 (10.9%); £3,752,050.83 -> £3,342,711.83 (10.9%); £3,752,051.08 -> £3,342,711.81 (10.9%); £3,752,051.33 -> £3,342,711.80 (10.9%); £3,752,051.57 -> £3,342,711.80 (10.9%); £3,752,051.80 -> £3,342,711.79 (10.9%); £3,752,052.01 -> £3,342,711.79 (10.9%); £3,752,052.20 -> £3,342,711.79 (10.9%); £3,752,052.35 -> £3,342,711.79 (10.9%); £3,752,052.50 -> £3,342,711.79 (10.9%); £3,752,052.64 -> £3,342,711.79 (10.9%); £3,752,052.78 -> £3,342,711.79 (10.9%); £3,752,052.94 -> £3,342,711.80 (10.9%); £3,752,053.09 -> £3,342,711.80 (10.9%); £3,752,053.23 -> £3,342,711.80 (10.9%); £3,752,053.38 -> £3,342,711.80 (10.9%); £3,752,053.53 -> £3,342,711.80 (10.9%); £3,752,053.67 -> £3,342,711.81 (10.9%); £3,752,053.82 -> £3,342,711.81 (10.9%); £3,752,053.97 -> £3,342,711.80 (10.9%); £3,752,054.12 -> £3,342,711.80 (10.9%); £3,752,054.29 -> £3,342,711.84 (10.9%); £3,752,054.47 -> £3,342,711.90 (10.9%); £3,752,054.67 -> £3,342,711.95 (10.9%); £3,752,054.88 -> £3,342,712.00 (10.9%); £3,752,055.12 -> £3,342,712.04 (10.9%); £3,752,055.36 -> £3,342,712.09 (10.9%); £3,752,055.61 -> £3,342,712.12 (10.9%); £3,752,055.85 -> £3,342,712.16 (10.9%); £3,752,056.10 -> £3,342,712.16 (10.9%); £3,752,056.34 -> £3,342,712.16 (10.9%); £3,752,056.60 -> £3,342,712.16 (10.9%); £3,752,056.84 -> £3,342,712.15 (10.9%); £3,752,057.09 -> £3,342,712.15 (10.9%); £3,752,057.34 -> £3,342,712.15 (10.9%); £3,752,057.58 -> £3,342,712.15 (10.9%); £3,752,057.82 -> £3,342,712.15 (10.9%); £3,752,058.06 -> £3,342,712.15 (10.9%); £3,752,058.32 -> £3,342,712.15 (10.9%); £3,752,058.56 -> £3,342,712.19 (10.9%); £3,752,058.74 -> £3,342,712.24 (10.9%); £3,752,058.93 -> £3,342,712.31 (10.9%); £3,752,059.19 -> £3,342,712.38 (10.9%); £3,752,059.43 -> £3,342,712.45 (10.9%); £3,752,059.67 -> £3,342,712.51 (10.9%); £3,752,059.92 -> £3,342,712.60 (10.9%); £3,752,060.11 -> £3,342,712.68 (10.9%); £3,752,060.36 -> £3,342,712.65 (10.9%); £3,752,060.61 -> £3,342,712.63 (10.9%); £3,752,060.86 -> £3,342,712.61 (10.9%); £3,752,061.11 -> £3,342,712.59 (10.9%); £3,752,061.36 -> £3,342,712.58 (10.9%); £3,752,061.61 -> £3,342,712.58 (10.9%); £3,752,061.84 -> £3,342,712.57 (10.9%); £3,752,062.04 -> £3,342,712.57 (10.9%); £3,752,062.24 -> £3,342,712.56 (10.9%); £3,752,062.38 -> £3,342,712.57 (10.9%); £3,752,062.53 -> £3,342,712.57 (10.9%); £3,752,062.68 -> £3,342,712.57 (10.9%); £3,752,062.83 -> £3,342,712.57 (10.9%); £3,752,062.98 -> £3,342,712.57 (10.9%); £3,752,063.13 -> £3,342,712.58 (10.9%); £3,752,063.27 -> £3,342,712.58 (10.9%); £3,752,063.42 -> £3,342,712.58 (10.9%); £3,752,063.57 -> £3,342,712.58 (10.9%); £3,752,063.72 -> £3,342,712.59 (10.9%); £3,752,063.87 -> £3,342,712.59 (10.9%); £3,752,064.03 -> £3,342,712.58 (10.9%); £3,752,064.18 -> £3,342,712.58 (10.9%); £3,752,064.35 -> £3,342,712.62 (10.9%); £3,752,064.54 -> £3,342,712.68 (10.9%); £3,752,064.73 -> £3,342,712.73 (10.9%); £3,752,064.94 -> £3,342,712.78 (10.9%); £3,752,065.18 -> £3,342,712.82 (10.9%); £3,752,065.43 -> £3,342,712.86 (10.9%); £3,752,065.68 -> £3,342,712.90 (10.9%); £3,752,065.93 -> £3,342,712.94 (10.9%); £3,752,066.18 -> £3,342,712.94 (10.9%); £3,752,066.44 -> £3,342,712.94 (10.9%); £3,752,066.68 -> £3,342,712.93 (10.9%); £3,752,066.93 -> £3,342,712.93 (10.9%); £3,752,067.18 -> £3,342,712.93 (10.9%); £3,752,067.44 -> £3,342,712.93 (10.9%); £3,752,067.70 -> £3,342,712.93 (10.9%); £3,752,067.95 -> £3,342,712.93 (10.9%); £3,752,068.21 -> £3,342,712.93 (10.9%); £3,752,068.46 -> £3,342,712.93 (10.9%); £3,752,068.71 -> £3,342,712.97 (10.9%); £3,752,068.96 -> £3,342,713.03 (10.9%); £3,752,069.14 -> £3,342,713.09 (10.9%); £3,752,069.33 -> £3,342,713.16 (10.9%); £3,752,069.58 -> £3,342,713.23 (10.9%); £3,752,069.83 -> £3,342,713.30 (10.9%); £3,752,070.09 -> £3,342,713.38 (10.9%); £3,752,070.28 -> £3,342,713.46 (10.9%); £3,752,070.54 -> £3,342,713.44 (10.9%); £3,752,070.79 -> £3,342,713.41 (10.9%); £3,752,071.04 -> £3,342,713.39 (10.9%); £3,752,071.29 -> £3,342,713.37 (10.9%); £3,752,071.54 -> £3,342,713.36 (10.9%); £3,752,071.80 -> £3,342,713.36 (10.9%); £3,752,072.03 -> £3,342,713.35 (10.9%); £3,752,072.25 -> £3,342,713.35 (10.9%); £3,752,072.44 -> £3,342,713.35 (10.9%); £3,752,072.59 -> £3,342,713.35 (10.9%); £3,752,072.75 -> £3,342,713.35 (10.9%); £3,752,072.90 -> £3,342,713.35 (10.9%); £3,752,073.06 -> £3,342,713.35 (10.9%); £3,752,073.21 -> £3,342,713.36 (10.9%); £3,752,073.37 -> £3,342,713.36 (10.9%); £3,752,073.52 -> £3,342,713.36 (10.9%); £3,752,073.68 -> £3,342,713.36 (10.9%); £3,752,073.84 -> £3,342,713.36 (10.9%); £3,752,073.98 -> £3,342,713.37 (10.9%); £3,752,074.14 -> £3,342,713.37 (10.9%); £3,752,074.29 -> £3,342,713.36 (10.9%); £3,752,074.45 -> £3,342,713.36 (10.9%); £3,752,074.62 -> £3,342,713.40 (10.9%); £3,752,074.80 -> £3,342,713.45 (10.9%); £3,752,075.01 -> £3,342,713.51 (10.9%); £3,752,075.22 -> £3,342,713.55 (10.9%); £3,752,075.46 -> £3,342,713.60 (10.9%); £3,752,075.71 -> £3,342,713.64 (10.9%); £3,752,075.97 -> £3,342,713.68 (10.9%); £3,752,076.23 -> £3,342,713.72 (10.9%); £3,752,076.47 -> £3,342,713.71 (10.9%); £3,752,076.73 -> £3,342,713.71 (10.9%); £3,752,076.98 -> £3,342,713.71 (10.9%); £3,752,077.24 -> £3,342,713.71 (10.9%); £3,752,077.50 -> £3,342,713.71 (10.9%); £3,752,077.75 -> £3,342,713.71 (10.9%); £3,752,078.01 -> £3,342,713.71 (10.9%); £3,752,078.27 -> £3,342,713.71 (10.9%); £3,752,078.52 -> £3,342,713.71 (10.9%); £3,752,078.78 -> £3,342,713.71 (10.9%); £3,752,079.04 -> £3,342,713.74 (10.9%); £3,752,079.23 -> £3,342,713.80 (10.9%); £3,752,079.42 -> £3,342,713.87 (10.9%); £3,752,079.60 -> £3,342,713.93 (10.9%); £3,752,079.79 -> £3,342,714.00 (10.9%); £3,752,080.05 -> £3,342,714.07 (10.9%); £3,752,080.30 -> £3,342,714.15 (10.9%); £3,752,080.50 -> £3,342,714.23 (10.9%); £3,752,080.76 -> £3,342,714.21 (10.9%); £3,752,081.02 -> £3,342,714.18 (10.9%); £3,752,081.28 -> £3,342,714.16 (10.9%); £3,752,081.53 -> £3,342,714.14 (10.9%); £3,752,081.78 -> £3,342,714.13 (10.9%); £3,752,082.04 -> £3,342,714.12 (10.9%); £3,752,082.27 -> £3,342,714.12 (10.9%); £3,752,082.49 -> £3,342,714.12 (10.9%); £3,752,082.69 -> £3,342,714.12 (10.9%); £3,752,082.85 -> £3,342,714.12 (10.9%); £3,752,083.00 -> £3,342,714.12 (10.9%); £3,752,083.15 -> £3,342,714.12 (10.9%); £3,752,083.30 -> £3,342,714.12 (10.9%); £3,752,083.45 -> £3,342,714.12 (10.9%); £3,752,083.60 -> £3,342,714.12 (10.9%); £3,752,083.76 -> £3,342,714.13 (10.9%); £3,752,083.91 -> £3,342,714.13 (10.9%); £3,752,084.07 -> £3,342,714.13 (10.9%); £3,752,084.22 -> £3,342,714.13 (10.9%); £3,752,084.37 -> £3,342,714.13 (10.9%); £3,752,084.53 -> £3,342,714.13 (10.9%); £3,752,084.69 -> £3,342,714.12 (10.9%); £3,752,084.85 -> £3,342,714.17 (10.9%); £3,752,085.04 -> £3,342,714.22 (10.9%); £3,752,085.24 -> £3,342,714.27 (10.9%); £3,752,085.47 -> £3,342,714.32 (10.9%); £3,752,085.71 -> £3,342,714.37 (10.9%); £3,752,085.97 -> £3,342,714.41 (10.9%); £3,752,086.24 -> £3,342,714.45 (10.9%); £3,752,086.50 -> £3,342,714.48 (10.9%); £3,752,086.76 -> £3,342,714.48 (10.9%); £3,752,087.02 -> £3,342,714.48 (10.9%); £3,752,087.27 -> £3,342,714.48 (10.9%); £3,752,087.51 -> £3,342,714.48 (10.9%); £3,752,087.77 -> £3,342,714.48 (10.9%); £3,752,088.02 -> £3,342,714.48 (10.9%); £3,752,088.29 -> £3,342,714.48 (10.9%); £3,752,088.55 -> £3,342,714.48 (10.9%); £3,752,088.79 -> £3,342,714.48 (10.9%); £3,752,089.04 -> £3,342,714.48 (10.9%); £3,752,089.30 -> £3,342,714.52 (10.9%); £3,752,089.50 -> £3,342,714.58 (10.9%); £3,752,089.69 -> £3,342,714.64 (10.9%); £3,752,089.89 -> £3,342,714.71 (10.9%); £3,752,090.08 -> £3,342,714.78 (10.9%); £3,752,090.28 -> £3,342,714.84 (10.9%); £3,752,090.47 -> £3,342,714.93 (10.9%); £3,752,090.66 -> £3,342,715.01 (10.9%); £3,752,090.92 -> £3,342,714.98 (10.9%); £3,752,091.18 -> £3,342,714.96 (10.9%); £3,752,091.43 -> £3,342,714.94 (10.9%); £3,752,091.69 -> £3,342,714.92 (10.9%); £3,752,091.94 -> £3,342,714.91 (10.9%); £3,752,092.20 -> £3,342,714.91 (10.9%); £3,752,092.43 -> £3,342,714.90 (10.9%); £3,752,092.65 -> £3,342,714.90 (10.9%); £3,752,092.85 -> £3,342,714.90 (10.9%); £3,752,093.00 -> £3,342,714.89 (10.9%); £3,752,093.13 -> £3,342,714.90 (10.9%); £3,752,093.27 -> £3,342,714.90 (10.9%); £3,752,093.41 -> £3,342,714.90 (10.9%); £3,752,093.55 -> £3,342,714.90 (10.9%); £3,752,093.70 -> £3,342,714.90 (10.9%); £3,752,093.84 -> £3,342,714.90 (10.9%); £3,752,093.98 -> £3,342,714.91 (10.9%); £3,752,094.11 -> £3,342,714.91 (10.9%); £3,752,094.25 -> £3,342,714.91 (10.9%); £3,752,094.39 -> £3,342,714.91 (10.9%); £3,752,094.52 -> £3,342,714.91 (10.9%); £3,752,094.67 -> £3,342,714.91 (10.9%); £3,752,094.82 -> £3,342,714.91 (10.9%); £3,752,094.99 -> £3,342,714.90 (10.9%); £3,752,095.19 -> £3,342,714.90 (10.9%); £3,752,095.38 -> £3,342,714.89 (10.9%); £3,752,095.60 -> £3,342,714.88 (10.9%); £3,752,095.83 -> £3,342,714.87 (10.9%); £3,752,096.06 -> £3,342,714.87 (10.9%); £3,752,096.30 -> £3,342,714.86 (10.9%); £3,752,096.53 -> £3,342,714.86 (10.9%); £3,752,096.77 -> £3,342,714.85 (10.9%); £3,752,096.99 -> £3,342,714.85 (10.9%); £3,752,097.21 -> £3,342,714.85 (10.9%); £3,752,097.45 -> £3,342,714.84 (10.9%); £3,752,097.69 -> £3,342,714.84 (10.9%); £3,752,097.92 -> £3,342,714.84 (10.9%); £3,752,098.15 -> £3,342,714.84 (10.9%); £3,752,098.38 -> £3,342,714.83 (10.9%); £3,752,098.61 -> £3,342,714.83 (10.9%); £3,752,098.83 -> £3,342,714.83 (10.9%); £3,752,099.01 -> £3,342,714.82 (10.9%); £3,752,099.19 -> £3,342,714.80 (10.9%); £3,752,099.36 -> £3,342,714.79 (10.9%); £3,752,099.53 -> £3,342,714.77 (10.9%); £3,752,099.70 -> £3,342,714.75 (10.9%); £3,752,099.94 -> £3,342,714.72 (10.9%); £3,752,100.17 -> £3,342,714.69 (10.9%); £3,752,100.40 -> £3,342,714.67 (10.9%); £3,752,100.63 -> £3,342,714.65 (10.9%); £3,752,100.86 -> £3,342,714.63 (10.9%); £3,752,101.09 -> £3,342,714.61 (10.9%); £3,752,101.32 -> £3,342,714.60 (10.9%); £3,752,101.55 -> £3,342,714.60 (10.9%); £3,752,101.76 -> £3,342,714.59 (10.9%); £3,752,101.95 -> £3,342,714.59 (10.9%); £3,752,102.13 -> £3,342,714.58 (10.9%); £3,752,102.26 -> £3,342,714.58 (10.9%); £3,752,102.41 -> £3,342,714.58 (10.9%); £3,752,102.55 -> £3,342,714.58 (10.9%); £3,752,102.69 -> £3,342,714.58 (10.9%); £3,752,102.83 -> £3,342,714.59 (10.9%); £3,752,102.97 -> £3,342,714.59 (10.9%); £3,752,103.11 -> £3,342,714.59 (10.9%); £3,752,103.26 -> £3,342,714.59 (10.9%); £3,752,103.40 -> £3,342,714.59 (10.9%); £3,752,103.53 -> £3,342,714.60 (10.9%); £3,752,103.66 -> £3,342,714.60 (10.9%); £3,752,103.80 -> £3,342,714.60 (10.9%); £3,752,103.94 -> £3,342,714.60 (10.9%); £3,752,104.10 -> £3,342,714.60 (10.9%); £3,752,104.28 -> £3,342,714.60 (10.9%); £3,752,104.46 -> £3,342,714.59 (10.9%); £3,752,104.67 -> £3,342,714.58 (10.9%); £3,752,104.89 -> £3,342,714.57 (10.9%); £3,752,105.12 -> £3,342,714.56 (10.9%); £3,752,105.36 -> £3,342,714.56 (10.9%); £3,752,105.59 -> £3,342,714.55 (10.9%); £3,752,105.82 -> £3,342,714.54 (10.9%); £3,752,106.06 -> £3,342,714.53 (10.9%); £3,752,106.29 -> £3,342,714.52 (10.9%); £3,752,106.52 -> £3,342,714.51 (10.9%); £3,752,106.75 -> £3,342,714.51 (10.9%); £3,752,106.97 -> £3,342,714.50 (10.9%); £3,752,107.21 -> £3,342,714.49 (10.9%); £3,752,107.45 -> £3,342,714.49 (10.9%); £3,752,107.68 -> £3,342,714.48 (10.9%); £3,752,107.91 -> £3,342,714.48 (10.9%); £3,752,108.14 -> £3,342,714.47 (10.9%); £3,752,108.31 -> £3,342,714.46 (10.9%); £3,752,108.48 -> £3,342,714.44 (10.9%); £3,752,108.65 -> £3,342,714.42 (10.9%); £3,752,108.83 -> £3,342,714.41 (10.9%); £3,752,109.06 -> £3,342,714.39 (10.9%); £3,752,109.29 -> £3,342,714.36 (10.9%); £3,752,109.47 -> £3,342,714.33 (10.9%); £3,752,109.70 -> £3,342,714.30 (10.9%); £3,752,109.94 -> £3,342,714.28 (10.9%); £3,752,110.17 -> £3,342,714.26 (10.9%); £3,752,110.41 -> £3,342,714.23 (10.9%); £3,752,110.65 -> £3,342,714.23 (10.9%); £3,752,110.88 -> £3,342,714.22 (10.9%); £3,752,111.09 -> £3,342,714.22 (10.9%); £3,752,111.29 -> £3,342,714.21 (10.9%); £3,752,111.46 -> £3,342,714.21 (10.9%); £3,752,111.62 -> £3,342,714.21 (10.9%); £3,752,111.78 -> £3,342,714.21 (10.9%); £3,752,111.94 -> £3,342,714.21 (10.9%); £3,752,112.10 -> £3,342,714.21 (10.9%); £3,752,112.26 -> £3,342,714.22 (10.9%); £3,752,112.42 -> £3,342,714.22 (10.9%); £3,752,112.58 -> £3,342,714.22 (10.9%); £3,752,112.74 -> £3,342,714.22 (10.9%); £3,752,112.90 -> £3,342,714.22 (10.9%); £3,752,113.06 -> £3,342,714.23 (10.9%); £3,752,113.23 -> £3,342,714.23 (10.9%); £3,752,113.39 -> £3,342,714.22 (10.9%); £3,752,113.55 -> £3,342,714.22 (10.9%); £3,752,113.73 -> £3,342,714.26 (10.9%); £3,752,113.93 -> £3,342,714.31 (10.9%); £3,752,114.14 -> £3,342,714.37 (10.9%); £3,752,114.38 -> £3,342,714.41 (10.9%); £3,752,114.63 -> £3,342,714.46 (10.9%); £3,752,114.91 -> £3,342,714.50 (10.9%); £3,752,115.17 -> £3,342,714.54 (10.9%); £3,752,115.44 -> £3,342,714.58 (10.9%); £3,752,115.72 -> £3,342,714.57 (10.9%); £3,752,115.98 -> £3,342,714.57 (10.9%); £3,752,116.24 -> £3,342,714.57 (10.9%); £3,752,116.51 -> £3,342,714.57 (10.9%); £3,752,116.77 -> £3,342,714.57 (10.9%); £3,752,117.03 -> £3,342,714.57 (10.9%); £3,752,117.29 -> £3,342,714.56 (10.9%); £3,752,117.55 -> £3,342,714.56 (10.9%); £3,752,117.82 -> £3,342,714.56 (10.9%); £3,752,118.09 -> £3,342,714.56 (10.9%); £3,752,118.36 -> £3,342,714.60 (10.9%); £3,752,118.63 -> £3,342,714.66 (10.9%); £3,752,118.90 -> £3,342,714.72 (10.9%); £3,752,119.18 -> £3,342,714.79 (10.9%); £3,752,119.45 -> £3,342,714.86 (10.9%); £3,752,119.72 -> £3,342,714.93 (10.9%); £3,752,119.99 -> £3,342,715.01 (10.9%); £3,752,120.19 -> £3,342,715.09 (10.9%); £3,752,120.46 -> £3,342,715.07 (10.9%); £3,752,120.73 -> £3,342,715.04 (10.9%); £3,752,121.00 -> £3,342,715.02 (10.9%); £3,752,121.26 -> £3,342,715.00 (10.9%); £3,752,121.52 -> £3,342,714.99 (10.9%); £3,752,121.80 -> £3,342,714.98 (10.9%); £3,752,122.04 -> £3,342,714.98 (10.9%); £3,752,122.28 -> £3,342,714.97 (10.9%); £3,752,122.48 -> £3,342,714.97 (10.9%); £3,752,122.64 -> £3,342,714.97 (10.9%); £3,752,122.80 -> £3,342,714.97 (10.9%); £3,752,122.96 -> £3,342,714.98 (10.9%); £3,752,123.12 -> £3,342,714.98 (10.9%); £3,752,123.28 -> £3,342,714.98 (10.9%); £3,752,123.44 -> £3,342,714.98 (10.9%); £3,752,123.59 -> £3,342,714.98 (10.9%); £3,752,123.75 -> £3,342,714.99 (10.9%); £3,752,123.91 -> £3,342,714.99 (10.9%); £3,752,124.07 -> £3,342,714.99 (10.9%); £3,752,124.23 -> £3,342,714.99 (10.9%); £3,752,124.38 -> £3,342,714.99 (10.9%); £3,752,124.54 -> £3,342,714.98 (10.9%); £3,752,124.72 -> £3,342,715.03 (10.9%); £3,752,124.91 -> £3,342,715.08 (10.9%); £3,752,125.12 -> £3,342,715.13 (10.9%); £3,752,125.35 -> £3,342,715.18 (10.9%); £3,752,125.60 -> £3,342,715.23 (10.9%); £3,752,125.87 -> £3,342,715.27 (10.9%); £3,752,126.14 -> £3,342,715.31 (10.9%); £3,752,126.41 -> £3,342,715.35 (10.9%); £3,752,126.67 -> £3,342,715.35 (10.9%); £3,752,126.94 -> £3,342,715.35 (10.9%); £3,752,127.20 -> £3,342,715.34 (10.9%); £3,752,127.46 -> £3,342,715.34 (10.9%); £3,752,127.73 -> £3,342,715.34 (10.9%); £3,752,127.99 -> £3,342,715.34 (10.9%); £3,752,128.26 -> £3,342,715.34 (10.9%); £3,752,128.54 -> £3,342,715.34 (10.9%); £3,752,128.79 -> £3,342,715.34 (10.9%); £3,752,129.06 -> £3,342,715.34 (10.9%); £3,752,129.33 -> £3,342,715.37 (10.9%); £3,752,129.53 -> £3,342,715.43 (10.9%); £3,752,129.72 -> £3,342,715.50 (10.9%); £3,752,129.99 -> £3,342,715.56 (10.9%); £3,752,130.26 -> £3,342,715.63 (10.9%); £3,752,130.46 -> £3,342,715.70 (10.9%); £3,752,130.66 -> £3,342,715.78 (10.9%); £3,752,130.86 -> £3,342,715.86 (10.9%); £3,752,131.12 -> £3,342,715.84 (10.9%); £3,752,131.38 -> £3,342,715.81 (10.9%); £3,752,131.64 -> £3,342,715.79 (10.9%); £3,752,131.89 -> £3,342,715.77 (10.9%); £3,752,132.16 -> £3,342,715.76 (10.9%); £3,752,132.43 -> £3,342,715.76 (10.9%); £3,752,132.67 -> £3,342,715.75 (10.9%); £3,752,132.88 -> £3,342,715.75 (10.9%); £3,752,133.09 -> £3,342,715.75 (10.9%); £3,752,133.25 -> £3,342,715.75 (10.9%); £3,752,133.41 -> £3,342,715.75 (10.9%); £3,752,133.57 -> £3,342,715.75 (10.9%); £3,752,133.73 -> £3,342,715.76 (10.9%); £3,752,133.89 -> £3,342,715.76 (10.9%); £3,752,134.05 -> £3,342,715.76 (10.9%); £3,752,134.20 -> £3,342,715.76 (10.9%); £3,752,134.37 -> £3,342,715.76 (10.9%); £3,752,134.53 -> £3,342,715.77 (10.9%); £3,752,134.69 -> £3,342,715.77 (10.9%); £3,752,134.85 -> £3,342,715.77 (10.9%); £3,752,135.00 -> £3,342,715.77 (10.9%); £3,752,135.16 -> £3,342,715.76 (10.9%); £3,752,135.33 -> £3,342,715.81 (10.9%); £3,752,135.53 -> £3,342,715.86 (10.9%); £3,752,135.74 -> £3,342,715.91 (10.9%); £3,752,135.96 -> £3,342,715.96 (10.9%); £3,752,136.22 -> £3,342,716.01 (10.9%); £3,752,136.49 -> £3,342,716.05 (10.9%); £3,752,136.75 -> £3,342,716.09 (10.9%); £3,752,137.02 -> £3,342,716.12 (10.9%); £3,752,137.29 -> £3,342,716.12 (10.9%); £3,752,137.56 -> £3,342,716.12 (10.9%); £3,752,137.82 -> £3,342,716.12 (10.9%); £3,752,138.08 -> £3,342,716.12 (10.9%); £3,752,138.34 -> £3,342,716.12 (10.9%); £3,752,138.60 -> £3,342,716.12 (10.9%); £3,752,138.87 -> £3,342,716.12 (10.9%); £3,752,139.13 -> £3,342,716.11 (10.9%); £3,752,139.40 -> £3,342,716.11 (10.9%); £3,752,139.66 -> £3,342,716.11 (10.9%); £3,752,139.93 -> £3,342,716.15 (10.9%); £3,752,140.19 -> £3,342,716.21 (10.9%); £3,752,140.45 -> £3,342,716.27 (10.9%); £3,752,140.66 -> £3,342,716.34 (10.9%); £3,752,140.85 -> £3,342,716.41 (10.9%); £3,752,141.06 -> £3,342,716.47 (10.9%); £3,752,141.33 -> £3,342,716.56 (10.9%); £3,752,141.59 -> £3,342,716.64 (10.9%); £3,752,141.86 -> £3,342,716.62 (10.9%); £3,752,142.12 -> £3,342,716.59 (10.9%); £3,752,142.39 -> £3,342,716.57 (10.9%); £3,752,142.66 -> £3,342,716.55 (10.9%); £3,752,142.93 -> £3,342,716.54 (10.9%); £3,752,143.19 -> £3,342,716.54 (10.9%); £3,752,143.43 -> £3,342,716.53 (10.9%); £3,752,143.65 -> £3,342,716.53 (10.9%); £3,752,143.86 -> £3,342,716.53 (10.9%); £3,752,144.02 -> £3,342,716.53 (10.9%); £3,752,144.18 -> £3,342,716.53 (10.9%); £3,752,144.34 -> £3,342,716.53 (10.9%); £3,752,144.50 -> £3,342,716.53 (10.9%); £3,752,144.65 -> £3,342,716.53 (10.9%); £3,752,144.81 -> £3,342,716.54 (10.9%); £3,752,144.97 -> £3,342,716.54 (10.9%); £3,752,145.13 -> £3,342,716.54 (10.9%); £3,752,145.29 -> £3,342,716.54 (10.9%); £3,752,145.45 -> £3,342,716.55 (10.9%); £3,752,145.61 -> £3,342,716.55 (10.9%); £3,752,145.78 -> £3,342,716.55 (10.9%); £3,752,145.94 -> £3,342,716.54 (10.9%); £3,752,146.11 -> £3,342,716.59 (10.9%); £3,752,146.30 -> £3,342,716.64 (10.9%); £3,752,146.51 -> £3,342,716.69 (10.9%); £3,752,146.73 -> £3,342,716.74 (10.9%); £3,752,146.97 -> £3,342,716.78 (10.9%); £3,752,147.24 -> £3,342,716.83 (10.9%); £3,752,147.50 -> £3,342,716.86 (10.9%); £3,752,147.77 -> £3,342,716.90 (10.9%); £3,752,148.03 -> £3,342,716.90 (10.9%); £3,752,148.29 -> £3,342,716.90 (10.9%); £3,752,148.55 -> £3,342,716.90 (10.9%); £3,752,148.82 -> £3,342,716.90 (10.9%); £3,752,149.08 -> £3,342,716.89 (10.9%); £3,752,149.36 -> £3,342,716.89 (10.9%); £3,752,149.61 -> £3,342,716.89 (10.9%); £3,752,149.88 -> £3,342,716.89 (10.9%); £3,752,150.15 -> £3,342,716.89 (10.9%); £3,752,150.42 -> £3,342,716.89 (10.9%); £3,752,150.69 -> £3,342,716.93 (10.9%); £3,752,150.95 -> £3,342,716.99 (10.9%); £3,752,151.15 -> £3,342,717.05 (10.9%); £3,752,151.35 -> £3,342,717.12 (10.9%); £3,752,151.54 -> £3,342,717.18 (10.9%); £3,752,151.74 -> £3,342,717.25 (10.9%); £3,752,151.94 -> £3,342,717.34 (10.9%); £3,752,152.21 -> £3,342,717.42 (10.9%); £3,752,152.47 -> £3,342,717.39 (10.9%); £3,752,152.73 -> £3,342,717.37 (10.9%); £3,752,153.00 -> £3,342,717.35 (10.9%); £3,752,153.26 -> £3,342,717.32 (10.9%); £3,752,153.53 -> £3,342,717.32 (10.9%); £3,752,153.80 -> £3,342,717.31 (10.9%); £3,752,154.04 -> £3,342,717.31 (10.9%); £3,752,154.26 -> £3,342,717.30 (10.9%); £3,752,154.47 -> £3,342,717.30 (10.9%); £3,752,154.62 -> £3,342,717.30 (10.9%); £3,752,154.78 -> £3,342,717.30 (10.9%); £3,752,154.94 -> £3,342,717.31 (10.9%); £3,752,155.10 -> £3,342,717.31 (10.9%); £3,752,155.25 -> £3,342,717.31 (10.9%); £3,752,155.41 -> £3,342,717.31 (10.9%); £3,752,155.57 -> £3,342,717.31 (10.9%); £3,752,155.74 -> £3,342,717.32 (10.9%); £3,752,155.90 -> £3,342,717.32 (10.9%); £3,752,156.05 -> £3,342,717.32 (10.9%); £3,752,156.21 -> £3,342,717.32 (10.9%); £3,752,156.37 -> £3,342,717.32 (10.9%); £3,752,156.53 -> £3,342,717.31 (10.9%); £3,752,156.70 -> £3,342,717.36 (10.9%); £3,752,156.90 -> £3,342,717.41 (10.9%); £3,752,157.11 -> £3,342,717.46 (10.9%); £3,752,157.34 -> £3,342,717.51 (10.9%); £3,752,157.58 -> £3,342,717.56 (10.9%); £3,752,157.86 -> £3,342,717.60 (10.9%); £3,752,158.13 -> £3,342,717.64 (10.9%); £3,752,158.41 -> £3,342,717.67 (10.9%); £3,752,158.67 -> £3,342,717.67 (10.9%); £3,752,158.94 -> £3,342,717.67 (10.9%); £3,752,159.20 -> £3,342,717.67 (10.9%); £3,752,159.47 -> £3,342,717.67 (10.9%); £3,752,159.73 -> £3,342,717.67 (10.9%); £3,752,160.00 -> £3,342,717.67 (10.9%); £3,752,160.27 -> £3,342,717.67 (10.9%); £3,752,160.53 -> £3,342,717.67 (10.9%); £3,752,160.80 -> £3,342,717.66 (10.9%); £3,752,161.06 -> £3,342,717.67 (10.9%); £3,752,161.33 -> £3,342,717.70 (10.9%); £3,752,161.60 -> £3,342,717.76 (10.9%); £3,752,161.87 -> £3,342,717.83 (10.9%); £3,752,162.13 -> £3,342,717.89 (10.9%); £3,752,162.39 -> £3,342,717.96 (10.9%); £3,752,162.65 -> £3,342,718.03 (10.9%); £3,752,162.92 -> £3,342,718.11 (10.9%); £3,752,163.18 -> £3,342,718.19 (10.9%); £3,752,163.45 -> £3,342,718.17 (10.9%); £3,752,163.72 -> £3,342,718.15 (10.9%); £3,752,163.98 -> £3,342,718.12 (10.9%); £3,752,164.24 -> £3,342,718.10 (10.9%); £3,752,164.51 -> £3,342,718.10 (10.9%); £3,752,164.78 -> £3,342,718.09 (10.9%); £3,752,165.03 -> £3,342,718.09 (10.9%); £3,752,165.26 -> £3,342,718.08 (10.9%); £3,752,165.47 -> £3,342,718.08 (10.9%); £3,752,165.60 -> £3,342,718.08 (10.9%); £3,752,165.74 -> £3,342,718.08 (10.9%); £3,752,165.88 -> £3,342,718.08 (10.9%); £3,752,166.02 -> £3,342,718.09 (10.9%); £3,752,166.16 -> £3,342,718.09 (10.9%); £3,752,166.30 -> £3,342,718.09 (10.9%); £3,752,166.44 -> £3,342,718.09 (10.9%); £3,752,166.58 -> £3,342,718.10 (10.9%); £3,752,166.72 -> £3,342,718.10 (10.9%); £3,752,166.86 -> £3,342,718.10 (10.9%); £3,752,167.00 -> £3,342,718.10 (10.9%); £3,752,167.14 -> £3,342,718.10 (10.9%); £3,752,167.28 -> £3,342,718.10 (10.9%); £3,752,167.44 -> £3,342,718.10 (10.9%); £3,752,167.61 -> £3,342,718.09 (10.9%); £3,752,167.80 -> £3,342,718.09 (10.9%); £3,752,168.00 -> £3,342,718.08 (10.9%); £3,752,168.21 -> £3,342,718.07 (10.9%); £3,752,168.44 -> £3,342,718.06 (10.9%); £3,752,168.67 -> £3,342,718.06 (10.9%); £3,752,168.91 -> £3,342,718.06 (10.9%); £3,752,169.14 -> £3,342,718.05 (10.9%); £3,752,169.37 -> £3,342,718.05 (10.9%); £3,752,169.60 -> £3,342,718.04 (10.9%); £3,752,169.84 -> £3,342,718.04 (10.9%); £3,752,170.07 -> £3,342,718.04 (10.9%); £3,752,170.31 -> £3,342,718.03 (10.9%); £3,752,170.53 -> £3,342,718.03 (10.9%); £3,752,170.76 -> £3,342,718.03 (10.9%); £3,752,170.99 -> £3,342,718.02 (10.9%); £3,752,171.23 -> £3,342,718.02 (10.9%); £3,752,171.46 -> £3,342,718.02 (10.9%); £3,752,171.70 -> £3,342,718.01 (10.9%); £3,752,171.88 -> £3,342,717.99 (10.9%); £3,752,172.11 -> £3,342,717.98 (10.9%); £3,752,172.28 -> £3,342,717.96 (10.9%); £3,752,172.45 -> £3,342,717.94 (10.9%); £3,752,172.63 -> £3,342,717.91 (10.9%); £3,752,172.81 -> £3,342,717.89 (10.9%); £3,752,173.04 -> £3,342,717.86 (10.9%); £3,752,173.27 -> £3,342,717.84 (10.9%); £3,752,173.50 -> £3,342,717.82 (10.9%); £3,752,173.73 -> £3,342,717.80 (10.9%); £3,752,173.96 -> £3,342,717.80 (10.9%); £3,752,174.19 -> £3,342,717.79 (10.9%); £3,752,174.40 -> £3,342,717.79 (10.9%); £3,752,174.59 -> £3,342,717.78 (10.9%); £3,752,174.77 -> £3,342,717.78 (10.9%); £3,752,174.91 -> £3,342,717.78 (10.9%); £3,752,175.05 -> £3,342,717.78 (10.9%); £3,752,175.19 -> £3,342,717.78 (10.9%); £3,752,175.33 -> £3,342,717.78 (10.9%); £3,752,175.47 -> £3,342,717.78 (10.9%); £3,752,175.61 -> £3,342,717.78 (10.9%); £3,752,175.75 -> £3,342,717.79 (10.9%); £3,752,175.89 -> £3,342,717.79 (10.9%); £3,752,176.04 -> £3,342,717.79 (10.9%); £3,752,176.17 -> £3,342,717.79 (10.9%); £3,752,176.32 -> £3,342,717.80 (10.9%); £3,752,176.46 -> £3,342,717.80 (10.9%); £3,752,176.60 -> £3,342,717.79 (10.9%); £3,752,176.76 -> £3,342,717.80 (10.9%); £3,752,176.92 -> £3,342,717.79 (10.9%); £3,752,177.10 -> £3,342,717.79 (10.9%); £3,752,177.30 -> £3,342,717.78 (10.9%); £3,752,177.53 -> £3,342,717.78 (10.9%); £3,752,177.76 -> £3,342,717.77 (10.9%); £3,752,177.99 -> £3,342,717.76 (10.9%); £3,752,178.23 -> £3,342,717.75 (10.9%); £3,752,178.47 -> £3,342,717.75 (10.9%); £3,752,178.70 -> £3,342,717.74 (10.9%); £3,752,178.93 -> £3,342,717.73 (10.9%); £3,752,179.17 -> £3,342,717.72 (10.9%); £3,752,179.41 -> £3,342,717.71 (10.9%); £3,752,179.65 -> £3,342,717.70 (10.9%); £3,752,179.88 -> £3,342,717.70 (10.9%); £3,752,180.12 -> £3,342,717.69 (10.9%); £3,752,180.36 -> £3,342,717.69 (10.9%); £3,752,180.59 -> £3,342,717.69 (10.9%); £3,752,180.84 -> £3,342,717.68 (10.9%); £3,752,181.06 -> £3,342,717.67 (10.9%); £3,752,181.30 -> £3,342,717.65 (10.9%); £3,752,181.46 -> £3,342,717.63 (10.9%); £3,752,181.64 -> £3,342,717.61 (10.9%); £3,752,181.82 -> £3,342,717.59 (10.9%); £3,752,181.99 -> £3,342,717.56 (10.9%); £3,752,182.17 -> £3,342,717.54 (10.9%); £3,752,182.41 -> £3,342,717.51 (10.9%); £3,752,182.64 -> £3,342,717.49 (10.9%); £3,752,182.88 -> £3,342,717.46 (10.9%); £3,752,183.11 -> £3,342,717.44 (10.9%); £3,752,183.34 -> £3,342,717.44 (10.9%); £3,752,183.58 -> £3,342,717.43 (10.9%); £3,752,183.80 -> £3,342,717.43 (10.9%); £3,752,184.00 -> £3,342,717.42 (10.9%); £3,752,184.18 -> £3,342,717.42 (10.9%); £3,752,184.34 -> £3,342,717.42 (10.9%); £3,752,184.50 -> £3,342,717.43 (10.9%); £3,752,184.67 -> £3,342,717.43 (10.9%); £3,752,184.83 -> £3,342,717.43 (10.9%); £3,752,184.99 -> £3,342,717.43 (10.9%); £3,752,185.15 -> £3,342,717.44 (10.9%); £3,752,185.32 -> £3,342,717.44 (10.9%); £3,752,185.48 -> £3,342,717.44 (10.9%); £3,752,185.65 -> £3,342,717.44 (10.9%); £3,752,185.81 -> £3,342,717.44 (10.9%); £3,752,185.97 -> £3,342,717.45 (10.9%); £3,752,186.14 -> £3,342,717.44 (10.9%); £3,752,186.30 -> £3,342,717.44 (10.9%); £3,752,186.48 -> £3,342,717.48 (10.9%); £3,752,186.69 -> £3,342,717.53 (10.9%); £3,752,186.92 -> £3,342,717.59 (10.9%); £3,752,187.15 -> £3,342,717.64 (10.9%); £3,752,187.40 -> £3,342,717.68 (10.9%); £3,752,187.66 -> £3,342,717.73 (10.9%); £3,752,187.94 -> £3,342,717.76 (10.9%); £3,752,188.22 -> £3,342,717.80 (10.9%); £3,752,188.49 -> £3,342,717.80 (10.9%); £3,752,188.76 -> £3,342,717.80 (10.9%); £3,752,189.03 -> £3,342,717.79 (10.9%); £3,752,189.30 -> £3,342,717.79 (10.9%); £3,752,189.57 -> £3,342,717.79 (10.9%); £3,752,189.83 -> £3,342,717.79 (10.9%); £3,752,190.10 -> £3,342,717.79 (10.9%); £3,752,190.37 -> £3,342,717.79 (10.9%); £3,752,190.64 -> £3,342,717.79 (10.9%); £3,752,190.92 -> £3,342,717.79 (10.9%); £3,752,191.18 -> £3,342,717.82 (10.9%); £3,752,191.39 -> £3,342,717.88 (10.9%); £3,752,191.59 -> £3,342,717.94 (10.9%); £3,752,191.79 -> £3,342,718.01 (10.9%); £3,752,192.00 -> £3,342,718.08 (10.9%); £3,752,192.21 -> £3,342,718.15 (10.9%); £3,752,192.48 -> £3,342,718.23 (10.9%); £3,752,192.76 -> £3,342,718.31 (10.9%); £3,752,193.04 -> £3,342,718.29 (10.9%); £3,752,193.31 -> £3,342,718.27 (10.9%); £3,752,193.58 -> £3,342,718.24 (10.9%); £3,752,193.85 -> £3,342,718.22 (10.9%); £3,752,194.12 -> £3,342,718.21 (10.9%); £3,752,194.39 -> £3,342,718.21 (10.9%); £3,752,194.64 -> £3,342,718.20 (10.9%); £3,752,194.87 -> £3,342,718.20 (10.9%); £3,752,195.09 -> £3,342,718.20 (10.9%); £3,752,195.26 -> £3,342,718.20 (10.9%); £3,752,195.42 -> £3,342,718.20 (10.9%); £3,752,195.59 -> £3,342,718.20 (10.9%); £3,752,195.76 -> £3,342,718.21 (10.9%); £3,752,195.93 -> £3,342,718.21 (10.9%); £3,752,196.09 -> £3,342,718.21 (10.9%); £3,752,196.26 -> £3,342,718.21 (10.9%); £3,752,196.42 -> £3,342,718.22 (10.9%); £3,752,196.58 -> £3,342,718.22 (10.9%); £3,752,196.75 -> £3,342,718.22 (10.9%); £3,752,196.92 -> £3,342,718.22 (10.9%); £3,752,197.08 -> £3,342,718.22 (10.9%); £3,752,197.25 -> £3,342,718.22 (10.9%); £3,752,197.44 -> £3,342,718.26 (10.9%); £3,752,197.64 -> £3,342,718.31 (10.9%); £3,752,197.86 -> £3,342,718.37 (10.9%); £3,752,198.09 -> £3,342,718.42 (10.9%); £3,752,198.35 -> £3,342,718.46 (10.9%); £3,752,198.62 -> £3,342,718.51 (10.9%); £3,752,198.89 -> £3,342,718.54 (10.9%); £3,752,199.18 -> £3,342,718.58 (10.9%); £3,752,199.46 -> £3,342,718.58 (10.9%); £3,752,199.73 -> £3,342,718.58 (10.9%); £3,752,200.00 -> £3,342,718.58 (10.9%); £3,752,200.28 -> £3,342,718.57 (10.9%); £3,752,200.54 -> £3,342,718.57 (10.9%); £3,752,200.82 -> £3,342,718.57 (10.9%); £3,752,201.09 -> £3,342,718.57 (10.9%); £3,752,201.37 -> £3,342,718.57 (10.9%); £3,752,201.63 -> £3,342,718.57 (10.9%); £3,752,201.90 -> £3,342,718.57 (10.9%); £3,752,202.18 -> £3,342,718.60 (10.9%); £3,752,202.38 -> £3,342,718.66 (10.9%); £3,752,202.59 -> £3,342,718.73 (10.9%); £3,752,202.80 -> £3,342,718.79 (10.9%); £3,752,203.01 -> £3,342,718.86 (10.9%); £3,752,203.20 -> £3,342,718.93 (10.9%); £3,752,203.41 -> £3,342,719.01 (10.9%); £3,752,203.62 -> £3,342,719.09 (10.9%); £3,752,203.89 -> £3,342,719.06 (10.9%); £3,752,204.17 -> £3,342,719.04 (10.9%); £3,752,204.43 -> £3,342,719.01 (10.9%); £3,752,204.71 -> £3,342,718.99 (10.9%); £3,752,204.99 -> £3,342,718.99 (10.9%); £3,752,205.26 -> £3,342,718.98 (10.9%); £3,752,205.51 -> £3,342,718.98 (10.9%); £3,752,205.74 -> £3,342,718.97 (10.9%); £3,752,205.94 -> £3,342,718.97 (10.9%); £3,752,206.12 -> £3,342,718.97 (10.9%); £3,752,206.28 -> £3,342,718.97 (10.9%); £3,752,206.44 -> £3,342,718.97 (10.9%); £3,752,206.60 -> £3,342,718.98 (10.9%); £3,752,206.77 -> £3,342,718.98 (10.9%); £3,752,206.94 -> £3,342,718.98 (10.9%); £3,752,207.10 -> £3,342,718.98 (10.9%); £3,752,207.27 -> £3,342,718.98 (10.9%); £3,752,207.43 -> £3,342,718.99 (10.9%); £3,752,207.60 -> £3,342,718.99 (10.9%); £3,752,207.76 -> £3,342,718.99 (10.9%); £3,752,207.93 -> £3,342,718.99 (10.9%); £3,752,208.10 -> £3,342,718.98 (10.9%); £3,752,208.28 -> £3,342,719.03 (10.9%); £3,752,208.48 -> £3,342,719.08 (10.9%); £3,752,208.71 -> £3,342,719.13 (10.9%); £3,752,208.95 -> £3,342,719.18 (10.9%); £3,752,209.20 -> £3,342,719.22 (10.9%); £3,752,209.49 -> £3,342,719.27 (10.9%); £3,752,209.77 -> £3,342,719.30 (10.9%); £3,752,210.05 -> £3,342,719.34 (10.9%); £3,752,210.33 -> £3,342,719.34 (10.9%); £3,752,210.61 -> £3,342,719.34 (10.9%); £3,752,210.88 -> £3,342,719.34 (10.9%); £3,752,211.16 -> £3,342,719.33 (10.9%); £3,752,211.43 -> £3,342,719.33 (10.9%); £3,752,211.70 -> £3,342,719.33 (10.9%); £3,752,211.97 -> £3,342,719.33 (10.9%); £3,752,212.26 -> £3,342,719.33 (10.9%); £3,752,212.53 -> £3,342,719.33 (10.9%); £3,752,212.80 -> £3,342,719.33 (10.9%); £3,752,213.08 -> £3,342,719.37 (10.9%); £3,752,213.29 -> £3,342,719.42 (10.9%); £3,752,213.50 -> £3,342,719.49 (10.9%); £3,752,213.77 -> £3,342,719.55 (10.9%); £3,752,213.98 -> £3,342,719.62 (10.9%); £3,752,214.17 -> £3,342,719.69 (10.9%); £3,752,214.38 -> £3,342,719.77 (10.9%); £3,752,214.65 -> £3,342,719.85 (10.9%); £3,752,214.93 -> £3,342,719.83 (10.9%); £3,752,215.19 -> £3,342,719.81 (10.9%); £3,752,215.47 -> £3,342,719.78 (10.9%); £3,752,215.74 -> £3,342,719.76 (10.9%); £3,752,216.02 -> £3,342,719.75 (10.9%); £3,752,216.30 -> £3,342,719.75 (10.9%); £3,752,216.56 -> £3,342,719.74 (10.9%); £3,752,216.80 -> £3,342,719.74 (10.9%); £3,752,217.01 -> £3,342,719.74 (10.9%); £3,752,217.18 -> £3,342,719.74 (10.9%); £3,752,217.34 -> £3,342,719.74 (10.9%); £3,752,217.51 -> £3,342,719.74 (10.9%); £3,752,217.67 -> £3,342,719.74 (10.9%); £3,752,217.84 -> £3,342,719.74 (10.9%); £3,752,218.01 -> £3,342,719.75 (10.9%); £3,752,218.17 -> £3,342,719.75 (10.9%); £3,752,218.34 -> £3,342,719.75 (10.9%); £3,752,218.50 -> £3,342,719.75 (10.9%); £3,752,218.66 -> £3,342,719.76 (10.9%); £3,752,218.82 -> £3,342,719.76 (10.9%); £3,752,218.99 -> £3,342,719.75 (10.9%); £3,752,219.15 -> £3,342,719.75 (10.9%); £3,752,219.34 -> £3,342,719.79 (10.9%); £3,752,219.54 -> £3,342,719.84 (10.9%); £3,752,219.76 -> £3,342,719.90 (10.9%); £3,752,220.00 -> £3,342,719.95 (10.9%); £3,752,220.26 -> £3,342,719.99 (10.9%); £3,752,220.54 -> £3,342,720.04 (10.9%); £3,752,220.81 -> £3,342,720.07 (10.9%); £3,752,221.09 -> £3,342,720.11 (10.9%); £3,752,221.37 -> £3,342,720.11 (10.9%); £3,752,221.64 -> £3,342,720.10 (10.9%); £3,752,221.92 -> £3,342,720.10 (10.9%); £3,752,222.18 -> £3,342,720.10 (10.9%); £3,752,222.46 -> £3,342,720.10 (10.9%); £3,752,222.74 -> £3,342,720.10 (10.9%); £3,752,223.01 -> £3,342,720.10 (10.9%); £3,752,223.29 -> £3,342,720.10 (10.9%); £3,752,223.56 -> £3,342,720.09 (10.9%); £3,752,223.83 -> £3,342,720.10 (10.9%); £3,752,224.10 -> £3,342,720.13 (10.9%); £3,752,224.30 -> £3,342,720.19 (10.9%); £3,752,224.59 -> £3,342,720.25 (10.9%); £3,752,224.79 -> £3,342,720.32 (10.9%); £3,752,225.06 -> £3,342,720.39 (10.9%); £3,752,225.33 -> £3,342,720.46 (10.9%); £3,752,225.60 -> £3,342,720.54 (10.9%); £3,752,225.88 -> £3,342,720.62 (10.9%); £3,752,226.15 -> £3,342,720.60 (10.9%); £3,752,226.43 -> £3,342,720.58 (10.9%); £3,752,226.71 -> £3,342,720.55 (10.9%); £3,752,226.98 -> £3,342,720.53 (10.9%); £3,752,227.27 -> £3,342,720.52 (10.9%); £3,752,227.54 -> £3,342,720.52 (10.9%); £3,752,227.79 -> £3,342,720.51 (10.9%); £3,752,228.03 -> £3,342,720.51 (10.9%); £3,752,228.24 -> £3,342,720.51 (10.9%); £3,752,228.41 -> £3,342,720.51 (10.9%); £3,752,228.57 -> £3,342,720.51 (10.9%); £3,752,228.74 -> £3,342,720.51 (10.9%); £3,752,228.90 -> £3,342,720.51 (10.9%); £3,752,229.06 -> £3,342,720.51 (10.9%); £3,752,229.23 -> £3,342,720.52 (10.9%); £3,752,229.39 -> £3,342,720.52 (10.9%); £3,752,229.55 -> £3,342,720.52 (10.9%); £3,752,229.72 -> £3,342,720.52 (10.9%); £3,752,229.88 -> £3,342,720.52 (10.9%); £3,752,230.05 -> £3,342,720.53 (10.9%); £3,752,230.22 -> £3,342,720.52 (10.9%); £3,752,230.38 -> £3,342,720.52 (10.9%); £3,752,230.56 -> £3,342,720.56 (10.9%); £3,752,230.76 -> £3,342,720.61 (10.9%); £3,752,230.98 -> £3,342,720.67 (10.9%); £3,752,231.20 -> £3,342,720.71 (10.9%); £3,752,231.47 -> £3,342,720.76 (10.9%); £3,752,231.73 -> £3,342,720.80 (10.9%); £3,752,232.00 -> £3,342,720.84 (10.9%); £3,752,232.28 -> £3,342,720.88 (10.9%); £3,752,232.55 -> £3,342,720.88 (10.9%); £3,752,232.82 -> £3,342,720.88 (10.9%); £3,752,233.08 -> £3,342,720.88 (10.9%); £3,752,233.34 -> £3,342,720.88 (10.9%); £3,752,233.61 -> £3,342,720.88 (10.9%); £3,752,233.87 -> £3,342,720.88 (10.9%); £3,752,234.16 -> £3,342,720.88 (10.9%); £3,752,234.44 -> £3,342,720.87 (10.9%); £3,752,234.70 -> £3,342,720.87 (10.9%); £3,752,234.98 -> £3,342,720.87 (10.9%); £3,752,235.25 -> £3,342,720.91 (10.9%); £3,752,235.51 -> £3,342,720.97 (10.9%); £3,752,235.78 -> £3,342,721.03 (10.9%); £3,752,236.06 -> £3,342,721.10 (10.9%); £3,752,236.34 -> £3,342,721.17 (10.9%); £3,752,236.61 -> £3,342,721.24 (10.9%); £3,752,236.81 -> £3,342,721.32 (10.9%); £3,752,237.02 -> £3,342,721.40 (10.9%); £3,752,237.29 -> £3,342,721.38 (10.9%); £3,752,237.56 -> £3,342,721.35 (10.9%); £3,752,237.83 -> £3,342,721.33 (10.9%); £3,752,238.10 -> £3,342,721.31 (10.9%); £3,752,238.37 -> £3,342,721.30 (10.9%); £3,752,238.64 -> £3,342,721.30 (10.9%); £3,752,238.89 -> £3,342,721.29 (10.9%); £3,752,239.12 -> £3,342,721.29 (10.9%); £3,752,239.33 -> £3,342,721.28 (10.9%); £3,752,239.48 -> £3,342,721.28 (10.9%); £3,752,239.62 -> £3,342,721.28 (10.9%); £3,752,239.77 -> £3,342,721.28 (10.9%); £3,752,239.91 -> £3,342,721.29 (10.9%); £3,752,240.05 -> £3,342,721.29 (10.9%); £3,752,240.19 -> £3,342,721.29 (10.9%); £3,752,240.33 -> £3,342,721.29 (10.9%); £3,752,240.47 -> £3,342,721.29 (10.9%); £3,752,240.61 -> £3,342,721.30 (10.9%); £3,752,240.76 -> £3,342,721.30 (10.9%); £3,752,240.90 -> £3,342,721.30 (10.9%); £3,752,241.04 -> £3,342,721.30 (10.9%); £3,752,241.19 -> £3,342,721.29 (10.9%); £3,752,241.35 -> £3,342,721.29 (10.9%); £3,752,241.53 -> £3,342,721.28 (10.9%); £3,752,241.72 -> £3,342,721.28 (10.9%); £3,752,241.93 -> £3,342,721.27 (10.9%); £3,752,242.15 -> £3,342,721.26 (10.9%); £3,752,242.39 -> £3,342,721.25 (10.9%); £3,752,242.62 -> £3,342,721.25 (10.9%); £3,752,242.86 -> £3,342,721.25 (10.9%); £3,752,243.10 -> £3,342,721.24 (10.9%); £3,752,243.35 -> £3,342,721.24 (10.9%); £3,752,243.58 -> £3,342,721.23 (10.9%); £3,752,243.81 -> £3,342,721.23 (10.9%); £3,752,244.05 -> £3,342,721.22 (10.9%); £3,752,244.29 -> £3,342,721.22 (10.9%); £3,752,244.53 -> £3,342,721.22 (10.9%); £3,752,244.77 -> £3,342,721.22 (10.9%); £3,752,245.01 -> £3,342,721.21 (10.9%); £3,752,245.25 -> £3,342,721.21 (10.9%); £3,752,245.49 -> £3,342,721.21 (10.9%); £3,752,245.73 -> £3,342,721.20 (10.9%); £3,752,245.97 -> £3,342,721.18 (10.9%); £3,752,246.20 -> £3,342,721.17 (10.9%); £3,752,246.38 -> £3,342,721.15 (10.9%); £3,752,246.61 -> £3,342,721.13 (10.9%); £3,752,246.79 -> £3,342,721.10 (10.9%); £3,752,246.97 -> £3,342,721.07 (10.9%); £3,752,247.22 -> £3,342,721.05 (10.9%); £3,752,247.46 -> £3,342,721.03 (10.9%); £3,752,247.70 -> £3,342,721.01 (10.9%); £3,752,247.94 -> £3,342,720.99 (10.9%); £3,752,248.18 -> £3,342,720.98 (10.9%); £3,752,248.42 -> £3,342,720.98 (10.9%); £3,752,248.64 -> £3,342,720.97 (10.9%); £3,752,248.85 -> £3,342,720.96 (10.9%); £3,752,249.04 -> £3,342,720.96 (10.9%); £3,752,249.18 -> £3,342,720.96 (10.9%); £3,752,249.32 -> £3,342,720.96 (10.9%); £3,752,249.46 -> £3,342,720.96 (10.9%); £3,752,249.59 -> £3,342,720.96 (10.9%); £3,752,249.73 -> £3,342,720.96 (10.9%); £3,752,249.88 -> £3,342,720.96 (10.9%); £3,752,250.02 -> £3,342,720.96 (10.9%); £3,752,250.16 -> £3,342,720.97 (10.9%); £3,752,250.31 -> £3,342,720.97 (10.9%); £3,752,250.45 -> £3,342,720.97 (10.9%); £3,752,250.58 -> £3,342,720.97 (10.9%); £3,752,250.72 -> £3,342,720.97 (10.9%); £3,752,250.85 -> £3,342,720.97 (10.9%); £3,752,251.01 -> £3,342,720.97 (10.9%); £3,752,251.17 -> £3,342,720.97 (10.9%); £3,752,251.36 -> £3,342,720.96 (10.9%); £3,752,251.57 -> £3,342,720.96 (10.9%); £3,752,251.79 -> £3,342,720.95 (10.9%); £3,752,252.03 -> £3,342,720.94 (10.9%); £3,752,252.26 -> £3,342,720.93 (10.9%); £3,752,252.50 -> £3,342,720.92 (10.9%); £3,752,252.73 -> £3,342,720.92 (10.9%); £3,752,252.97 -> £3,342,720.91 (10.9%); £3,752,253.21 -> £3,342,720.90 (10.9%); £3,752,253.44 -> £3,342,720.89 (10.9%); £3,752,253.67 -> £3,342,720.88 (10.9%); £3,752,253.91 -> £3,342,720.87 (10.9%); £3,752,254.14 -> £3,342,720.87 (10.9%); £3,752,254.38 -> £3,342,720.86 (10.9%); £3,752,254.61 -> £3,342,720.86 (10.9%); £3,752,254.84 -> £3,342,720.85 (10.9%); £3,752,255.08 -> £3,342,720.85 (10.9%); £3,752,255.31 -> £3,342,720.84 (10.9%); £3,752,255.54 -> £3,342,720.82 (10.9%); £3,752,255.72 -> £3,342,720.80 (10.9%); £3,752,255.89 -> £3,342,720.78 (10.9%); £3,752,256.07 -> £3,342,720.76 (10.9%); £3,752,256.25 -> £3,342,720.73 (10.9%); £3,752,256.43 -> £3,342,720.71 (10.9%); £3,752,256.66 -> £3,342,720.68 (10.9%); £3,752,256.89 -> £3,342,720.66 (10.9%); £3,752,257.13 -> £3,342,720.63 (10.9%); £3,752,257.36 -> £3,342,720.61 (10.9%); £3,752,257.59 -> £3,342,720.61 (10.9%); £3,752,257.83 -> £3,342,720.60 (10.9%); £3,752,258.05 -> £3,342,720.59 (10.9%); £3,752,258.25 -> £3,342,720.59 (10.9%); £3,752,258.43 -> £3,342,720.59 (10.9%); £3,752,258.59 -> £3,342,720.59 (10.9%); £3,752,258.74 -> £3,342,720.59 (10.9%); £3,752,258.90 -> £3,342,720.59 (10.9%); £3,752,259.05 -> £3,342,720.59 (10.9%); £3,752,259.21 -> £3,342,720.59 (10.9%); £3,752,259.37 -> £3,342,720.60 (10.9%); £3,752,259.52 -> £3,342,720.60 (10.9%); £3,752,259.68 -> £3,342,720.60 (10.9%); £3,752,259.83 -> £3,342,720.60 (10.9%); £3,752,259.98 -> £3,342,720.60 (10.9%); £3,752,260.14 -> £3,342,720.61 (10.9%); £3,752,260.29 -> £3,342,720.60 (10.9%); £3,752,260.45 -> £3,342,720.60 (10.9%); £3,752,260.62 -> £3,342,720.64 (10.9%); £3,752,260.82 -> £3,342,720.70 (10.9%); £3,752,261.03 -> £3,342,720.75 (10.9%); £3,752,261.25 -> £3,342,720.80 (10.9%); £3,752,261.49 -> £3,342,720.84 (10.9%); £3,752,261.75 -> £3,342,720.89 (10.9%); £3,752,262.01 -> £3,342,720.92 (10.9%); £3,752,262.26 -> £3,342,720.96 (10.9%); £3,752,262.52 -> £3,342,720.96 (10.9%); £3,752,262.78 -> £3,342,720.96 (10.9%); £3,752,263.04 -> £3,342,720.96 (10.9%); £3,752,263.30 -> £3,342,720.95 (10.9%); £3,752,263.56 -> £3,342,720.95 (10.9%); £3,752,263.82 -> £3,342,720.95 (10.9%); £3,752,264.08 -> £3,342,720.95 (10.9%); £3,752,264.34 -> £3,342,720.95 (10.9%); £3,752,264.59 -> £3,342,720.95 (10.9%); £3,752,264.86 -> £3,342,720.95 (10.9%); £3,752,265.12 -> £3,342,720.99 (10.9%); £3,752,265.32 -> £3,342,721.04 (10.9%); £3,752,265.51 -> £3,342,721.11 (10.9%); £3,752,265.70 -> £3,342,721.18 (10.9%); £3,752,265.89 -> £3,342,721.24 (10.9%); £3,752,266.09 -> £3,342,721.31 (10.9%); £3,752,266.28 -> £3,342,721.39 (10.9%); £3,752,266.48 -> £3,342,721.47 (10.9%); £3,752,266.74 -> £3,342,721.45 (10.9%); £3,752,266.99 -> £3,342,721.42 (10.9%); £3,752,267.25 -> £3,342,721.40 (10.9%); £3,752,267.51 -> £3,342,721.38 (10.9%); £3,752,267.77 -> £3,342,721.37 (10.9%); £3,752,268.03 -> £3,342,721.37 (10.9%); £3,752,268.27 -> £3,342,721.36 (10.9%); £3,752,268.49 -> £3,342,721.36 (10.9%); £3,752,268.70 -> £3,342,721.36 (10.9%); £3,752,268.85 -> £3,342,721.36 (10.9%); £3,752,269.01 -> £3,342,721.36 (10.9%); £3,752,269.17 -> £3,342,721.36 (10.9%); £3,752,269.33 -> £3,342,721.36 (10.9%); £3,752,269.49 -> £3,342,721.36 (10.9%); £3,752,269.64 -> £3,342,721.37 (10.9%); £3,752,269.79 -> £3,342,721.37 (10.9%); £3,752,269.95 -> £3,342,721.37 (10.9%); £3,752,270.10 -> £3,342,721.37 (10.9%); £3,752,270.26 -> £3,342,721.37 (10.9%); £3,752,270.41 -> £3,342,721.38 (10.9%); £3,752,270.57 -> £3,342,721.37 (10.9%); £3,752,270.73 -> £3,342,721.37 (10.9%); £3,752,270.90 -> £3,342,721.41 (10.9%); £3,752,271.09 -> £3,342,721.46 (10.9%); £3,752,271.31 -> £3,342,721.52 (10.9%); £3,752,271.54 -> £3,342,721.56 (10.9%); £3,752,271.78 -> £3,342,721.61 (10.9%); £3,752,272.03 -> £3,342,721.65 (10.9%); £3,752,272.29 -> £3,342,721.69 (10.9%); £3,752,272.54 -> £3,342,721.73 (10.9%); £3,752,272.80 -> £3,342,721.73 (10.9%); £3,752,273.06 -> £3,342,721.72 (10.9%); £3,752,273.32 -> £3,342,721.72 (10.9%); £3,752,273.59 -> £3,342,721.72 (10.9%); £3,752,273.84 -> £3,342,721.72 (10.9%); £3,752,274.11 -> £3,342,721.72 (10.9%); £3,752,274.37 -> £3,342,721.72 (10.9%); £3,752,274.63 -> £3,342,721.72 (10.9%); £3,752,274.89 -> £3,342,721.72 (10.9%); £3,752,275.14 -> £3,342,721.72 (10.9%); £3,752,275.40 -> £3,342,721.75 (10.9%); £3,752,275.65 -> £3,342,721.81 (10.9%); £3,752,275.92 -> £3,342,721.88 (10.9%); £3,752,276.17 -> £3,342,721.95 (10.9%); £3,752,276.44 -> £3,342,722.01 (10.9%); £3,752,276.69 -> £3,342,722.08 (10.9%); £3,752,276.95 -> £3,342,722.17 (10.9%); £3,752,277.20 -> £3,342,722.25 (10.9%); £3,752,277.46 -> £3,342,722.22 (10.9%); £3,752,277.72 -> £3,342,722.20 (10.9%); £3,752,277.98 -> £3,342,722.18 (10.9%); £3,752,278.24 -> £3,342,722.16 (10.9%); £3,752,278.51 -> £3,342,722.15 (10.9%); £3,752,278.77 -> £3,342,722.14 (10.9%); £3,752,279.01 -> £3,342,722.14 (10.9%); £3,752,279.23 -> £3,342,722.13 (10.9%); £3,752,279.43 -> £3,342,722.13 (10.9%); £3,752,279.59 -> £3,342,722.13 (10.9%); £3,752,279.74 -> £3,342,722.13 (10.9%); £3,752,279.90 -> £3,342,722.14 (10.9%); £3,752,280.05 -> £3,342,722.14 (10.9%); £3,752,280.20 -> £3,342,722.14 (10.9%); £3,752,280.35 -> £3,342,722.14 (10.9%); £3,752,280.51 -> £3,342,722.14 (10.9%); £3,752,280.66 -> £3,342,722.15 (10.9%); £3,752,280.82 -> £3,342,722.15 (10.9%); £3,752,280.98 -> £3,342,722.15 (10.9%); £3,752,281.13 -> £3,342,722.15 (10.9%); £3,752,281.29 -> £3,342,722.15 (10.9%); £3,752,281.45 -> £3,342,722.14 (10.9%); £3,752,281.63 -> £3,342,722.19 (10.9%); £3,752,281.82 -> £3,342,722.24 (10.9%); £3,752,282.03 -> £3,342,722.29 (10.9%); £3,752,282.25 -> £3,342,722.34 (10.9%); £3,752,282.49 -> £3,342,722.39 (10.9%); £3,752,282.75 -> £3,342,722.43 (10.9%); £3,752,283.01 -> £3,342,722.47 (10.9%); £3,752,283.27 -> £3,342,722.51 (10.9%); £3,752,283.53 -> £3,342,722.50 (10.9%); £3,752,283.79 -> £3,342,722.50 (10.9%); £3,752,284.05 -> £3,342,722.50 (10.9%); £3,752,284.29 -> £3,342,722.50 (10.9%); £3,752,284.54 -> £3,342,722.50 (10.9%); £3,752,284.81 -> £3,342,722.50 (10.9%); £3,752,285.07 -> £3,342,722.50 (10.9%); £3,752,285.33 -> £3,342,722.50 (10.9%); £3,752,285.59 -> £3,342,722.49 (10.9%); £3,752,285.85 -> £3,342,722.50 (10.9%); £3,752,286.12 -> £3,342,722.53 (10.9%); £3,752,286.37 -> £3,342,722.59 (10.9%); £3,752,286.57 -> £3,342,722.65 (10.9%); £3,752,286.76 -> £3,342,722.72 (10.9%); £3,752,286.95 -> £3,342,722.79 (10.9%); £3,752,287.21 -> £3,342,722.86 (10.9%); £3,752,287.47 -> £3,342,722.94 (10.9%); £3,752,287.72 -> £3,342,723.02 (10.9%); £3,752,287.98 -> £3,342,723.00 (10.9%); £3,752,288.25 -> £3,342,722.98 (10.9%); £3,752,288.51 -> £3,342,722.95 (10.9%); £3,752,288.77 -> £3,342,722.93 (10.9%); £3,752,289.02 -> £3,342,722.93 (10.9%); £3,752,289.28 -> £3,342,722.92 (10.9%); £3,752,289.52 -> £3,342,722.92 (10.9%); £3,752,289.74 -> £3,342,722.91 (10.9%); £3,752,289.94 -> £3,342,722.91 (10.9%); £3,752,290.10 -> £3,342,722.91 (10.9%); £3,752,290.25 -> £3,342,722.91 (10.9%); £3,752,290.41 -> £3,342,722.91 (10.9%); £3,752,290.56 -> £3,342,722.92 (10.9%); £3,752,290.72 -> £3,342,722.92 (10.9%); £3,752,290.87 -> £3,342,722.92 (10.9%); £3,752,291.03 -> £3,342,722.92 (10.9%); £3,752,291.20 -> £3,342,722.92 (10.9%); £3,752,291.36 -> £3,342,722.93 (10.9%); £3,752,291.52 -> £3,342,722.93 (10.9%); £3,752,291.67 -> £3,342,722.93 (10.9%); £3,752,291.83 -> £3,342,722.93 (10.9%); £3,752,291.98 -> £3,342,722.92 (10.9%); £3,752,292.15 -> £3,342,722.97 (10.9%); £3,752,292.35 -> £3,342,723.02 (10.9%); £3,752,292.56 -> £3,342,723.07 (10.9%); £3,752,292.79 -> £3,342,723.12 (10.9%); £3,752,293.03 -> £3,342,723.17 (10.9%); £3,752,293.29 -> £3,342,723.21 (10.9%); £3,752,293.56 -> £3,342,723.25 (10.9%); £3,752,293.82 -> £3,342,723.28 (10.9%); £3,752,294.09 -> £3,342,723.28 (10.9%); £3,752,294.35 -> £3,342,723.28 (10.9%); £3,752,294.61 -> £3,342,723.28 (10.9%); £3,752,294.87 -> £3,342,723.28 (10.9%); £3,752,295.14 -> £3,342,723.28 (10.9%); £3,752,295.40 -> £3,342,723.28 (10.9%); £3,752,295.66 -> £3,342,723.28 (10.9%); £3,752,295.91 -> £3,342,723.28 (10.9%); £3,752,296.17 -> £3,342,723.27 (10.9%); £3,752,296.43 -> £3,342,723.28 (10.9%); £3,752,296.69 -> £3,342,723.31 (10.9%); £3,752,296.94 -> £3,342,723.37 (10.9%); £3,752,297.21 -> £3,342,723.44 (10.9%); £3,752,297.47 -> £3,342,723.50 (10.9%); £3,752,297.72 -> £3,342,723.57 (10.9%); £3,752,297.99 -> £3,342,723.64 (10.9%); £3,752,298.25 -> £3,342,723.72 (10.9%); £3,752,298.52 -> £3,342,723.81 (10.9%); £3,752,298.77 -> £3,342,723.78 (10.9%); £3,752,299.03 -> £3,342,723.76 (10.9%); £3,752,299.28 -> £3,342,723.74 (10.9%); £3,752,299.54 -> £3,342,723.71 (10.9%); £3,752,299.80 -> £3,342,723.71 (10.9%); £3,752,300.05 -> £3,342,723.70 (10.9%); £3,752,300.29 -> £3,342,723.70 (10.9%); £3,752,300.51 -> £3,342,723.69 (10.9%); £3,752,300.72 -> £3,342,723.69 (10.9%); £3,752,300.88 -> £3,342,723.69 (10.9%); £3,752,301.03 -> £3,342,723.69 (10.9%); £3,752,301.18 -> £3,342,723.69 (10.9%); £3,752,301.35 -> £3,342,723.69 (10.9%); £3,752,301.50 -> £3,342,723.70 (10.9%); £3,752,301.66 -> £3,342,723.70 (10.9%); £3,752,301.82 -> £3,342,723.70 (10.9%); £3,752,301.98 -> £3,342,723.70 (10.9%); £3,752,302.14 -> £3,342,723.71 (10.9%); £3,752,302.30 -> £3,342,723.71 (10.9%); £3,752,302.45 -> £3,342,723.71 (10.9%); £3,752,302.62 -> £3,342,723.71 (10.9%); £3,752,302.77 -> £3,342,723.70 (10.9%); £3,752,302.95 -> £3,342,723.75 (10.9%); £3,752,303.14 -> £3,342,723.80 (10.9%); £3,752,303.36 -> £3,342,723.85 (10.9%); £3,752,303.58 -> £3,342,723.90 (10.9%); £3,752,303.83 -> £3,342,723.95 (10.9%); £3,752,304.10 -> £3,342,723.99 (10.9%); £3,752,304.36 -> £3,342,724.03 (10.9%); £3,752,304.63 -> £3,342,724.06 (10.9%); £3,752,304.88 -> £3,342,724.06 (10.9%); £3,752,305.13 -> £3,342,724.06 (10.9%); £3,752,305.40 -> £3,342,724.06 (10.9%); £3,752,305.66 -> £3,342,724.06 (10.9%); £3,752,305.92 -> £3,342,724.05 (10.9%); £3,752,306.17 -> £3,342,724.05 (10.9%); £3,752,306.43 -> £3,342,724.05 (10.9%); £3,752,306.69 -> £3,342,724.05 (10.9%); £3,752,306.95 -> £3,342,724.05 (10.9%); £3,752,307.22 -> £3,342,724.05 (10.9%); £3,752,307.48 -> £3,342,724.09 (10.9%); £3,752,307.68 -> £3,342,724.14 (10.9%); £3,752,307.95 -> £3,342,724.21 (10.9%); £3,752,308.14 -> £3,342,724.28 (10.9%); £3,752,308.33 -> £3,342,724.34 (10.9%); £3,752,308.53 -> £3,342,724.41 (10.9%); £3,752,308.72 -> £3,342,724.49 (10.9%); £3,752,308.92 -> £3,342,724.57 (10.9%); £3,752,309.17 -> £3,342,724.55 (10.9%); £3,752,309.43 -> £3,342,724.52 (10.9%); £3,752,309.69 -> £3,342,724.50 (10.9%); £3,752,309.96 -> £3,342,724.48 (10.9%); £3,752,310.23 -> £3,342,724.47 (10.9%); £3,752,310.50 -> £3,342,724.47 (10.9%); £3,752,310.74 -> £3,342,724.46 (10.9%); £3,752,310.96 -> £3,342,724.46 (10.9%); £3,752,311.16 -> £3,342,724.46 (10.9%); £3,752,311.30 -> £3,342,724.46 (10.9%); £3,752,311.44 -> £3,342,724.46 (10.9%); £3,752,311.57 -> £3,342,724.46 (10.9%); £3,752,311.71 -> £3,342,724.46 (10.9%); £3,752,311.85 -> £3,342,724.46 (10.9%); £3,752,311.99 -> £3,342,724.46 (10.9%); £3,752,312.13 -> £3,342,724.47 (10.9%); £3,752,312.27 -> £3,342,724.47 (10.9%); £3,752,312.40 -> £3,342,724.47 (10.9%); £3,752,312.54 -> £3,342,724.47 (10.9%); £3,752,312.68 -> £3,342,724.47 (10.9%); £3,752,312.82 -> £3,342,724.47 (10.9%); £3,752,312.96 -> £3,342,724.47 (10.9%); £3,752,313.11 -> £3,342,724.47 (10.9%); £3,752,313.28 -> £3,342,724.46 (10.9%); £3,752,313.46 -> £3,342,724.46 (10.9%); £3,752,313.66 -> £3,342,724.45 (10.9%); £3,752,313.87 -> £3,342,724.44 (10.9%); £3,752,314.09 -> £3,342,724.43 (10.9%); £3,752,314.32 -> £3,342,724.43 (10.9%); £3,752,314.54 -> £3,342,724.42 (10.9%); £3,752,314.76 -> £3,342,724.42 (10.9%); £3,752,314.99 -> £3,342,724.42 (10.9%); £3,752,315.23 -> £3,342,724.41 (10.9%); £3,752,315.46 -> £3,342,724.41 (10.9%); £3,752,315.69 -> £3,342,724.40 (10.9%); £3,752,315.91 -> £3,342,724.40 (10.9%); £3,752,316.13 -> £3,342,724.40 (10.9%); £3,752,316.36 -> £3,342,724.39 (10.9%); £3,752,316.59 -> £3,342,724.39 (10.9%); £3,752,316.82 -> £3,342,724.39 (10.9%); £3,752,317.04 -> £3,342,724.39 (10.9%); £3,752,317.22 -> £3,342,724.38 (10.9%); £3,752,317.39 -> £3,342,724.36 (10.9%); £3,752,317.56 -> £3,342,724.34 (10.9%); £3,752,317.73 -> £3,342,724.32 (10.9%); £3,752,317.90 -> £3,342,724.31 (10.9%); £3,752,318.08 -> £3,342,724.28 (10.9%); £3,752,318.25 -> £3,342,724.25 (10.9%); £3,752,318.48 -> £3,342,724.22 (10.9%); £3,752,318.70 -> £3,342,724.20 (10.9%); £3,752,318.94 -> £3,342,724.18 (10.9%); £3,752,319.16 -> £3,342,724.16 (10.9%); £3,752,319.38 -> £3,342,724.16 (10.9%); £3,752,319.62 -> £3,342,724.15 (10.9%); £3,752,319.83 -> £3,342,724.14 (10.9%); £3,752,320.02 -> £3,342,724.14 (10.9%); £3,752,320.20 -> £3,342,724.14 (10.9%); £3,752,320.33 -> £3,342,724.13 (10.9%); £3,752,320.47 -> £3,342,724.13 (10.9%); £3,752,320.61 -> £3,342,724.13 (10.9%); £3,752,320.75 -> £3,342,724.13 (10.9%); £3,752,320.89 -> £3,342,724.14 (10.9%); £3,752,321.02 -> £3,342,724.14 (10.9%); £3,752,321.16 -> £3,342,724.14 (10.9%); £3,752,321.30 -> £3,342,724.14 (10.9%); £3,752,321.45 -> £3,342,724.14 (10.9%); £3,752,321.58 -> £3,342,724.15 (10.9%); £3,752,321.71 -> £3,342,724.15 (10.9%); £3,752,321.85 -> £3,342,724.15 (10.9%); £3,752,321.99 -> £3,342,724.15 (10.9%); £3,752,322.15 -> £3,342,724.15 (10.9%); £3,752,322.31 -> £3,342,724.14 (10.9%); £3,752,322.50 -> £3,342,724.14 (10.9%); £3,752,322.69 -> £3,342,724.13 (10.9%); £3,752,322.91 -> £3,342,724.12 (10.9%); £3,752,323.14 -> £3,342,724.11 (10.9%); £3,752,323.37 -> £3,342,724.11 (10.9%); £3,752,323.60 -> £3,342,724.10 (10.9%); £3,752,323.83 -> £3,342,724.09 (10.9%); £3,752,324.06 -> £3,342,724.08 (10.9%); £3,752,324.29 -> £3,342,724.07 (10.9%); £3,752,324.52 -> £3,342,724.06 (10.9%); £3,752,324.75 -> £3,342,724.05 (10.9%); £3,752,324.97 -> £3,342,724.05 (10.9%); £3,752,325.20 -> £3,342,724.04 (10.9%); £3,752,325.44 -> £3,342,724.04 (10.9%); £3,752,325.67 -> £3,342,724.03 (10.9%); £3,752,325.90 -> £3,342,724.03 (10.9%); £3,752,326.13 -> £3,342,724.03 (10.9%); £3,752,326.37 -> £3,342,724.01 (10.9%); £3,752,326.60 -> £3,342,724.00 (10.9%); £3,752,326.83 -> £3,342,723.98 (10.9%); £3,752,326.99 -> £3,342,723.96 (10.9%); £3,752,327.22 -> £3,342,723.94 (10.9%); £3,752,327.40 -> £3,342,723.91 (10.9%); £3,752,327.56 -> £3,342,723.89 (10.9%); £3,752,327.80 -> £3,342,723.86 (10.9%); £3,752,328.03 -> £3,342,723.84 (10.9%); £3,752,328.26 -> £3,342,723.81 (10.9%); £3,752,328.48 -> £3,342,723.79 (10.9%); £3,752,328.71 -> £3,342,723.79 (10.9%); £3,752,328.93 -> £3,342,723.78 (10.9%); £3,752,329.14 -> £3,342,723.78 (10.9%); £3,752,329.33 -> £3,342,723.77 (10.9%); £3,752,329.51 -> £3,342,723.77 (10.9%); £3,752,329.67 -> £3,342,723.77 (10.9%); £3,752,329.83 -> £3,342,723.78 (10.9%); £3,752,329.99 -> £3,342,723.78 (10.9%); £3,752,330.15 -> £3,342,723.78 (10.9%); £3,752,330.32 -> £3,342,723.78 (10.9%); £3,752,330.47 -> £3,342,723.78 (10.9%); £3,752,330.63 -> £3,342,723.79 (10.9%); £3,752,330.79 -> £3,342,723.79 (10.9%); £3,752,330.95 -> £3,342,723.79 (10.9%); £3,752,331.10 -> £3,342,723.79 (10.9%); £3,752,331.27 -> £3,342,723.79 (10.9%); £3,752,331.43 -> £3,342,723.79 (10.9%); £3,752,331.59 -> £3,342,723.79 (10.9%); £3,752,331.76 -> £3,342,723.83 (10.9%); £3,752,331.96 -> £3,342,723.88 (10.9%); £3,752,332.17 -> £3,342,723.94 (10.9%); £3,752,332.39 -> £3,342,723.98 (10.9%); £3,752,332.64 -> £3,342,724.03 (10.9%); £3,752,332.90 -> £3,342,724.07 (10.9%); £3,752,333.16 -> £3,342,724.11 (10.9%); £3,752,333.42 -> £3,342,724.15 (10.9%); £3,752,333.68 -> £3,342,724.15 (10.9%); £3,752,333.95 -> £3,342,724.14 (10.9%); £3,752,334.22 -> £3,342,724.14 (10.9%); £3,752,334.48 -> £3,342,724.14 (10.9%); £3,752,334.75 -> £3,342,724.14 (10.9%); £3,752,335.01 -> £3,342,724.14 (10.9%); £3,752,335.29 -> £3,342,724.14 (10.9%); £3,752,335.55 -> £3,342,724.14 (10.9%); £3,752,335.81 -> £3,342,724.14 (10.9%); £3,752,336.07 -> £3,342,724.14 (10.9%); £3,752,336.33 -> £3,342,724.17 (10.9%); £3,752,336.59 -> £3,342,724.23 (10.9%); £3,752,336.79 -> £3,342,724.30 (10.9%); £3,752,336.98 -> £3,342,724.36 (10.9%); £3,752,337.18 -> £3,342,724.43 (10.9%); £3,752,337.44 -> £3,342,724.50 (10.9%); £3,752,337.70 -> £3,342,724.59 (10.9%); £3,752,337.96 -> £3,342,724.67 (10.9%); £3,752,338.24 -> £3,342,724.64 (10.9%); £3,752,338.49 -> £3,342,724.62 (10.9%); £3,752,338.76 -> £3,342,724.60 (10.9%); £3,752,339.02 -> £3,342,724.58 (10.9%); £3,752,339.29 -> £3,342,724.57 (10.9%); £3,752,339.56 -> £3,342,724.57 (10.9%); £3,752,339.81 -> £3,342,724.56 (10.9%); £3,752,340.03 -> £3,342,724.56 (10.9%); £3,752,340.23 -> £3,342,724.56 (10.9%); £3,752,340.39 -> £3,342,724.56 (10.9%); £3,752,340.55 -> £3,342,724.56 (10.9%); £3,752,340.71 -> £3,342,724.56 (10.9%); £3,752,340.87 -> £3,342,724.56 (10.9%); £3,752,341.03 -> £3,342,724.56 (10.9%); £3,752,341.19 -> £3,342,724.56 (10.9%); £3,752,341.35 -> £3,342,724.57 (10.9%); £3,752,341.51 -> £3,342,724.57 (10.9%); £3,752,341.66 -> £3,342,724.57 (10.9%); £3,752,341.82 -> £3,342,724.57 (10.9%); £3,752,341.98 -> £3,342,724.57 (10.9%); £3,752,342.13 -> £3,342,724.57 (10.9%); £3,752,342.29 -> £3,342,724.56 (10.9%); £3,752,342.47 -> £3,342,724.61 (10.9%); £3,752,342.66 -> £3,342,724.66 (10.9%); £3,752,342.87 -> £3,342,724.72 (10.9%); £3,752,343.11 -> £3,342,724.76 (10.9%); £3,752,343.35 -> £3,342,724.81 (10.9%); £3,752,343.62 -> £3,342,724.85 (10.9%); £3,752,343.88 -> £3,342,724.89 (10.9%); £3,752,344.14 -> £3,342,724.93 (10.9%); £3,752,344.42 -> £3,342,724.93 (10.9%); £3,752,344.68 -> £3,342,724.92 (10.9%); £3,752,344.94 -> £3,342,724.92 (10.9%); £3,752,345.20 -> £3,342,724.92 (10.9%); £3,752,345.47 -> £3,342,724.92 (10.9%); £3,752,345.73 -> £3,342,724.92 (10.9%); £3,752,345.99 -> £3,342,724.92 (10.9%); £3,752,346.25 -> £3,342,724.92 (10.9%); £3,752,346.53 -> £3,342,724.92 (10.9%); £3,752,346.79 -> £3,342,724.92 (10.9%); £3,752,347.05 -> £3,342,724.96 (10.9%); £3,752,347.33 -> £3,342,725.02 (10.9%); £3,752,347.58 -> £3,342,725.08 (10.9%); £3,752,347.85 -> £3,342,725.15 (10.9%); £3,752,348.11 -> £3,342,725.22 (10.9%); £3,752,348.37 -> £3,342,725.28 (10.9%); £3,752,348.65 -> £3,342,725.37 (10.9%); £3,752,348.84 -> £3,342,725.45 (10.9%); £3,752,349.10 -> £3,342,725.43 (10.9%); £3,752,349.35 -> £3,342,725.40 (10.9%); £3,752,349.62 -> £3,342,725.38 (10.9%); £3,752,349.89 -> £3,342,725.36 (10.9%); £3,752,350.15 -> £3,342,725.35 (10.9%); £3,752,350.41 -> £3,342,725.35 (10.9%); £3,752,350.66 -> £3,342,725.34 (10.9%); £3,752,350.89 -> £3,342,725.34 (10.9%); £3,752,351.09 -> £3,342,725.34 (10.9%); £3,752,351.26 -> £3,342,725.34 (10.9%); £3,752,351.41 -> £3,342,725.34 (10.9%); £3,752,351.57 -> £3,342,725.34 (10.9%); £3,752,351.74 -> £3,342,725.34 (10.9%); £3,752,351.90 -> £3,342,725.35 (10.9%); £3,752,352.06 -> £3,342,725.35 (10.9%); £3,752,352.22 -> £3,342,725.35 (10.9%); £3,752,352.38 -> £3,342,725.35 (10.9%); £3,752,352.54 -> £3,342,725.35 (10.9%); £3,752,352.70 -> £3,342,725.36 (10.9%); £3,752,352.86 -> £3,342,725.36 (10.9%); £3,752,353.02 -> £3,342,725.36 (10.9%); £3,752,353.18 -> £3,342,725.35 (10.9%); £3,752,353.36 -> £3,342,725.39 (10.9%); £3,752,353.56 -> £3,342,725.45 (10.9%); £3,752,353.77 -> £3,342,725.50 (10.9%); £3,752,354.00 -> £3,342,725.55 (10.9%); £3,752,354.24 -> £3,342,725.59 (10.9%); £3,752,354.52 -> £3,342,725.64 (10.9%); £3,752,354.79 -> £3,342,725.67 (10.9%); £3,752,355.05 -> £3,342,725.71 (10.9%); £3,752,355.32 -> £3,342,725.71 (10.9%); £3,752,355.58 -> £3,342,725.71 (10.9%); £3,752,355.85 -> £3,342,725.71 (10.9%); £3,752,356.11 -> £3,342,725.70 (10.9%); £3,752,356.38 -> £3,342,725.70 (10.9%); £3,752,356.65 -> £3,342,725.70 (10.9%); £3,752,356.92 -> £3,342,725.70 (10.9%); £3,752,357.18 -> £3,342,725.70 (10.9%); £3,752,357.45 -> £3,342,725.70 (10.9%); £3,752,357.73 -> £3,342,725.70 (10.9%); £3,752,357.99 -> £3,342,725.74 (10.9%); £3,752,358.25 -> £3,342,725.80 (10.9%); £3,752,358.52 -> £3,342,725.86 (10.9%); £3,752,358.79 -> £3,342,725.93 (10.9%); £3,752,359.05 -> £3,342,725.99 (10.9%); £3,752,359.25 -> £3,342,726.06 (10.9%); £3,752,359.45 -> £3,342,726.15 (10.9%); £3,752,359.72 -> £3,342,726.23 (10.9%); £3,752,359.98 -> £3,342,726.20 (10.9%); £3,752,360.24 -> £3,342,726.18 (10.9%); £3,752,360.51 -> £3,342,726.16 (10.9%); £3,752,360.79 -> £3,342,726.14 (10.9%); £3,752,361.05 -> £3,342,726.13 (10.9%); £3,752,361.32 -> £3,342,726.13 (10.9%); £3,752,361.57 -> £3,342,726.12 (10.9%); £3,752,361.79 -> £3,342,726.12 (10.9%); £3,752,362.00 -> £3,342,726.12 (10.9%); £3,752,362.15 -> £3,342,726.12 (10.9%); £3,752,362.31 -> £3,342,726.12 (10.9%); £3,752,362.47 -> £3,342,726.12 (10.9%); £3,752,362.63 -> £3,342,726.12 (10.9%); £3,752,362.79 -> £3,342,726.13 (10.9%); £3,752,362.95 -> £3,342,726.13 (10.9%); £3,752,363.12 -> £3,342,726.13 (10.9%); £3,752,363.28 -> £3,342,726.13 (10.9%); £3,752,363.44 -> £3,342,726.13 (10.9%); £3,752,363.60 -> £3,342,726.14 (10.9%); £3,752,363.76 -> £3,342,726.14 (10.9%); £3,752,363.92 -> £3,342,726.13 (10.9%); £3,752,364.08 -> £3,342,726.13 (10.9%); £3,752,364.26 -> £3,342,726.17 (10.9%); £3,752,364.46 -> £3,342,726.22 (10.9%); £3,752,364.67 -> £3,342,726.28 (10.9%); £3,752,364.91 -> £3,342,726.33 (10.9%); £3,752,365.16 -> £3,342,726.37 (10.9%); £3,752,365.43 -> £3,342,726.41 (10.9%); £3,752,365.69 -> £3,342,726.45 (10.9%); £3,752,365.96 -> £3,342,726.49 (10.9%); £3,752,366.23 -> £3,342,726.48 (10.9%); £3,752,366.49 -> £3,342,726.48 (10.9%); £3,752,366.75 -> £3,342,726.48 (10.9%); £3,752,367.02 -> £3,342,726.48 (10.9%); £3,752,367.30 -> £3,342,726.48 (10.9%); £3,752,367.57 -> £3,342,726.48 (10.9%); £3,752,367.83 -> £3,342,726.47 (10.9%); £3,752,368.10 -> £3,342,726.47 (10.9%); £3,752,368.36 -> £3,342,726.47 (10.9%); £3,752,368.63 -> £3,342,726.47 (10.9%); £3,752,368.90 -> £3,342,726.51 (10.9%); £3,752,369.17 -> £3,342,726.57 (10.9%); £3,752,369.44 -> £3,342,726.63 (10.9%); £3,752,369.72 -> £3,342,726.70 (10.9%); £3,752,369.98 -> £3,342,726.77 (10.9%); £3,752,370.18 -> £3,342,726.84 (10.9%); £3,752,370.45 -> £3,342,726.92 (10.9%); £3,752,370.73 -> £3,342,727.00 (10.9%); £3,752,370.99 -> £3,342,726.98 (10.9%); £3,752,371.27 -> £3,342,726.95 (10.9%); £3,752,371.54 -> £3,342,726.93 (10.9%); £3,752,371.81 -> £3,342,726.91 (10.9%); £3,752,372.07 -> £3,342,726.90 (10.9%); £3,752,372.34 -> £3,342,726.90 (10.9%); £3,752,372.58 -> £3,342,726.89 (10.9%); £3,752,372.80 -> £3,342,726.89 (10.9%); £3,752,373.01 -> £3,342,726.89 (10.9%); £3,752,373.18 -> £3,342,726.89 (10.9%); £3,752,373.34 -> £3,342,726.89 (10.9%); £3,752,373.50 -> £3,342,726.89 (10.9%); £3,752,373.65 -> £3,342,726.89 (10.9%); £3,752,373.81 -> £3,342,726.89 (10.9%); £3,752,373.97 -> £3,342,726.90 (10.9%); £3,752,374.14 -> £3,342,726.90 (10.9%); £3,752,374.30 -> £3,342,726.90 (10.9%); £3,752,374.46 -> £3,342,726.90 (10.9%); £3,752,374.62 -> £3,342,726.91 (10.9%); £3,752,374.78 -> £3,342,726.91 (10.9%); £3,752,374.94 -> £3,342,726.90 (10.9%); £3,752,375.09 -> £3,342,726.90 (10.9%); £3,752,375.27 -> £3,342,726.94 (10.9%); £3,752,375.47 -> £3,342,727.00 (10.9%); £3,752,375.69 -> £3,342,727.05 (10.9%); £3,752,375.91 -> £3,342,727.10 (10.9%); £3,752,376.16 -> £3,342,727.14 (10.9%); £3,752,376.44 -> £3,342,727.19 (10.9%); £3,752,376.70 -> £3,342,727.23 (10.9%); £3,752,376.96 -> £3,342,727.26 (10.9%); £3,752,377.21 -> £3,342,727.26 (10.9%); £3,752,377.47 -> £3,342,727.26 (10.9%); £3,752,377.73 -> £3,342,727.26 (10.9%); £3,752,378.00 -> £3,342,727.25 (10.9%); £3,752,378.26 -> £3,342,727.25 (10.9%); £3,752,378.54 -> £3,342,727.25 (10.9%); £3,752,378.81 -> £3,342,727.25 (10.9%); £3,752,379.07 -> £3,342,727.25 (10.9%); £3,752,379.33 -> £3,342,727.25 (10.9%); £3,752,379.60 -> £3,342,727.25 (10.9%); £3,752,379.86 -> £3,342,727.29 (10.9%); £3,752,380.13 -> £3,342,727.35 (10.9%); £3,752,380.38 -> £3,342,727.41 (10.9%); £3,752,380.58 -> £3,342,727.48 (10.9%); £3,752,380.79 -> £3,342,727.55 (10.9%); £3,752,380.98 -> £3,342,727.61 (10.9%); £3,752,381.19 -> £3,342,727.70 (10.9%); £3,752,381.39 -> £3,342,727.78 (10.9%); £3,752,381.65 -> £3,342,727.75 (10.9%); £3,752,381.91 -> £3,342,727.73 (10.9%); £3,752,382.19 -> £3,342,727.70 (10.9%); £3,752,382.45 -> £3,342,727.68 (10.9%); £3,752,382.72 -> £3,342,727.68 (10.9%); £3,752,382.98 -> £3,342,727.67 (10.9%); £3,752,383.22 -> £3,342,727.67 (10.9%); £3,752,383.44 -> £3,342,727.66 (10.9%); £3,752,383.64 -> £3,342,727.66 (10.9%); £3,752,383.79 -> £3,342,727.66 (10.9%); £3,752,383.93 -> £3,342,727.66 (10.9%); £3,752,384.07 -> £3,342,727.66 (10.9%); £3,752,384.21 -> £3,342,727.66 (10.9%); £3,752,384.35 -> £3,342,727.66 (10.9%); £3,752,384.49 -> £3,342,727.66 (10.9%); £3,752,384.63 -> £3,342,727.67 (10.9%); £3,752,384.77 -> £3,342,727.67 (10.9%); £3,752,384.91 -> £3,342,727.67 (10.9%); £3,752,385.05 -> £3,342,727.67 (10.9%); £3,752,385.19 -> £3,342,727.67 (10.9%); £3,752,385.33 -> £3,342,727.67 (10.9%); £3,752,385.47 -> £3,342,727.67 (10.9%); £3,752,385.63 -> £3,342,727.67 (10.9%); £3,752,385.80 -> £3,342,727.66 (10.9%); £3,752,385.99 -> £3,342,727.66 (10.9%); £3,752,386.20 -> £3,342,727.65 (10.9%); £3,752,386.42 -> £3,342,727.64 (10.9%); £3,752,386.66 -> £3,342,727.63 (10.9%); £3,752,386.89 -> £3,342,727.63 (10.9%); £3,752,387.12 -> £3,342,727.62 (10.9%); £3,752,387.36 -> £3,342,727.62 (10.9%); £3,752,387.59 -> £3,342,727.61 (10.9%); £3,752,387.82 -> £3,342,727.61 (10.9%); £3,752,388.06 -> £3,342,727.61 (10.9%); £3,752,388.29 -> £3,342,727.60 (10.9%); £3,752,388.52 -> £3,342,727.60 (10.9%); £3,752,388.76 -> £3,342,727.60 (10.9%); £3,752,388.99 -> £3,342,727.59 (10.9%); £3,752,389.24 -> £3,342,727.59 (10.9%); £3,752,389.48 -> £3,342,727.59 (10.9%); £3,752,389.72 -> £3,342,727.59 (10.9%); £3,752,389.89 -> £3,342,727.58 (10.9%); £3,752,390.06 -> £3,342,727.56 (10.9%); £3,752,390.24 -> £3,342,727.54 (10.9%); £3,752,390.41 -> £3,342,727.52 (10.9%); £3,752,390.59 -> £3,342,727.50 (10.9%); £3,752,390.76 -> £3,342,727.47 (10.9%); £3,752,390.94 -> £3,342,727.45 (10.9%); £3,752,391.18 -> £3,342,727.42 (10.9%); £3,752,391.42 -> £3,342,727.40 (10.9%); £3,752,391.66 -> £3,342,727.38 (10.9%); £3,752,391.89 -> £3,342,727.35 (10.9%); £3,752,392.13 -> £3,342,727.35 (10.9%); £3,752,392.36 -> £3,342,727.34 (10.9%); £3,752,392.58 -> £3,342,727.34 (10.9%); £3,752,392.78 -> £3,342,727.33 (10.9%); £3,752,392.96 -> £3,342,727.33 (10.9%); £3,752,393.10 -> £3,342,727.33 (10.9%); £3,752,393.25 -> £3,342,727.33 (10.9%); £3,752,393.39 -> £3,342,727.33 (10.9%); £3,752,393.53 -> £3,342,727.33 (10.9%); £3,752,393.66 -> £3,342,727.33 (10.9%); £3,752,393.80 -> £3,342,727.33 (10.9%); £3,752,393.94 -> £3,342,727.33 (10.9%); £3,752,394.08 -> £3,342,727.34 (10.9%); £3,752,394.22 -> £3,342,727.34 (10.9%); £3,752,394.36 -> £3,342,727.34 (10.9%); £3,752,394.50 -> £3,342,727.34 (10.9%); £3,752,394.64 -> £3,342,727.34 (10.9%); £3,752,394.78 -> £3,342,727.34 (10.9%); £3,752,394.94 -> £3,342,727.34 (10.9%); £3,752,395.11 -> £3,342,727.34 (10.9%); £3,752,395.30 -> £3,342,727.33 (10.9%); £3,752,395.50 -> £3,342,727.33 (10.9%); £3,752,395.71 -> £3,342,727.32 (10.9%); £3,752,395.95 -> £3,342,727.31 (10.9%); £3,752,396.19 -> £3,342,727.30 (10.9%); £3,752,396.43 -> £3,342,727.29 (10.9%); £3,752,396.67 -> £3,342,727.28 (10.9%); £3,752,396.90 -> £3,342,727.28 (10.9%); £3,752,397.13 -> £3,342,727.27 (10.9%); £3,752,397.36 -> £3,342,727.26 (10.9%); £3,752,397.59 -> £3,342,727.25 (10.9%); £3,752,397.84 -> £3,342,727.24 (10.9%); £3,752,398.07 -> £3,342,727.23 (10.9%); £3,752,398.30 -> £3,342,727.23 (10.9%); £3,752,398.53 -> £3,342,727.22 (10.9%); £3,752,398.77 -> £3,342,727.22 (10.9%); £3,752,399.00 -> £3,342,727.22 (10.9%); £3,752,399.18 -> £3,342,727.20 (10.9%); £3,752,399.35 -> £3,342,727.19 (10.9%); £3,752,399.53 -> £3,342,727.17 (10.9%); £3,752,399.71 -> £3,342,727.15 (10.9%); £3,752,399.94 -> £3,342,727.13 (10.9%); £3,752,400.18 -> £3,342,727.10 (10.9%); £3,752,400.35 -> £3,342,727.07 (10.9%); £3,752,400.59 -> £3,342,727.05 (10.9%); £3,752,400.82 -> £3,342,727.03 (10.9%); £3,752,401.05 -> £3,342,727.00 (10.9%); £3,752,401.28 -> £3,342,726.98 (10.9%); £3,752,401.51 -> £3,342,726.98 (10.9%); £3,752,401.75 -> £3,342,726.97 (10.9%); £3,752,401.96 -> £3,342,726.97 (10.9%); £3,752,402.16 -> £3,342,726.96 (10.9%); £3,752,402.34 -> £3,342,726.96 (10.9%); £3,752,402.50 -> £3,342,726.96 (10.9%); £3,752,402.66 -> £3,342,726.96 (10.9%); £3,752,402.82 -> £3,342,726.96 (10.9%); £3,752,402.97 -> £3,342,726.97 (10.9%); £3,752,403.14 -> £3,342,726.97 (10.9%); £3,752,403.30 -> £3,342,726.97 (10.9%); £3,752,403.46 -> £3,342,726.97 (10.9%); £3,752,403.62 -> £3,342,726.98 (10.9%); £3,752,403.78 -> £3,342,726.98 (10.9%); £3,752,403.94 -> £3,342,726.98 (10.9%); £3,752,404.10 -> £3,342,726.98 (10.9%); £3,752,404.26 -> £3,342,726.98 (10.9%); £3,752,404.42 -> £3,342,726.97 (10.9%); £3,752,404.59 -> £3,342,727.02 (10.9%); £3,752,404.79 -> £3,342,727.07 (10.9%); £3,752,405.01 -> £3,342,727.12 (10.9%); £3,752,405.24 -> £3,342,727.17 (10.9%); £3,752,405.48 -> £3,342,727.22 (10.9%); £3,752,405.74 -> £3,342,727.26 (10.9%); £3,752,406.00 -> £3,342,727.30 (10.9%); £3,752,406.27 -> £3,342,727.33 (10.9%); £3,752,406.53 -> £3,342,727.33 (10.9%); £3,752,406.80 -> £3,342,727.33 (10.9%); £3,752,407.07 -> £3,342,727.33 (10.9%); £3,752,407.32 -> £3,342,727.33 (10.9%); £3,752,407.58 -> £3,342,727.33 (10.9%); £3,752,407.85 -> £3,342,727.32 (10.9%); £3,752,408.12 -> £3,342,727.32 (10.9%); £3,752,408.38 -> £3,342,727.32 (10.9%); £3,752,408.65 -> £3,342,727.32 (10.9%); £3,752,408.91 -> £3,342,727.32 (10.9%); £3,752,409.17 -> £3,342,727.36 (10.9%); £3,752,409.43 -> £3,342,727.42 (10.9%); £3,752,409.71 -> £3,342,727.48 (10.9%); £3,752,409.97 -> £3,342,727.55 (10.9%); £3,752,410.23 -> £3,342,727.62 (10.9%); £3,752,410.49 -> £3,342,727.69 (10.9%); £3,752,410.75 -> £3,342,727.77 (10.9%); £3,752,410.95 -> £3,342,727.85 (10.9%); £3,752,411.21 -> £3,342,727.83 (10.9%); £3,752,411.47 -> £3,342,727.80 (10.9%); £3,752,411.73 -> £3,342,727.78 (10.9%); £3,752,411.98 -> £3,342,727.76 (10.9%); £3,752,412.24 -> £3,342,727.75 (10.9%); £3,752,412.50 -> £3,342,727.75 (10.9%); £3,752,412.75 -> £3,342,727.74 (10.9%); £3,752,412.97 -> £3,342,727.74 (10.9%); £3,752,413.18 -> £3,342,727.74 (10.9%); £3,752,413.34 -> £3,342,727.74 (10.9%); £3,752,413.50 -> £3,342,727.74 (10.9%); £3,752,413.65 -> £3,342,727.74 (10.9%); £3,752,413.81 -> £3,342,727.74 (10.9%); £3,752,413.97 -> £3,342,727.75 (10.9%); £3,752,414.12 -> £3,342,727.75 (10.9%); £3,752,414.28 -> £3,342,727.75 (10.9%); £3,752,414.44 -> £3,342,727.75 (10.9%); £3,752,414.60 -> £3,342,727.76 (10.9%); £3,752,414.75 -> £3,342,727.76 (10.9%); £3,752,414.90 -> £3,342,727.76 (10.9%); £3,752,415.06 -> £3,342,727.76 (10.9%); £3,752,415.22 -> £3,342,727.75 (10.9%); £3,752,415.40 -> £3,342,727.80 (10.9%); £3,752,415.58 -> £3,342,727.85 (10.9%); £3,752,415.80 -> £3,342,727.90 (10.9%); £3,752,416.03 -> £3,342,727.95 (10.9%); £3,752,416.28 -> £3,342,727.99 (10.9%); £3,752,416.54 -> £3,342,728.04 (10.9%); £3,752,416.79 -> £3,342,728.08 (10.9%); £3,752,417.05 -> £3,342,728.11 (10.9%); £3,752,417.30 -> £3,342,728.11 (10.9%); £3,752,417.56 -> £3,342,728.11 (10.9%); £3,752,417.82 -> £3,342,728.11 (10.9%); £3,752,418.08 -> £3,342,728.11 (10.9%); £3,752,418.34 -> £3,342,728.11 (10.9%); £3,752,418.61 -> £3,342,728.10 (10.9%); £3,752,418.86 -> £3,342,728.10 (10.9%); £3,752,419.13 -> £3,342,728.10 (10.9%); £3,752,419.39 -> £3,342,728.10 (10.9%); £3,752,419.64 -> £3,342,728.10 (10.9%); £3,752,419.91 -> £3,342,728.14 (10.9%); £3,752,420.18 -> £3,342,728.20 (10.9%); £3,752,420.44 -> £3,342,728.26 (10.9%); £3,752,420.63 -> £3,342,728.33 (10.9%); £3,752,420.83 -> £3,342,728.40 (10.9%); £3,752,421.03 -> £3,342,728.46 (10.9%); £3,752,421.23 -> £3,342,728.55 (10.9%); £3,752,421.49 -> £3,342,728.63 (10.9%); £3,752,421.74 -> £3,342,728.60 (10.9%); £3,752,422.01 -> £3,342,728.58 (10.9%); £3,752,422.28 -> £3,342,728.56 (10.9%); £3,752,422.53 -> £3,342,728.54 (10.9%); £3,752,422.80 -> £3,342,728.53 (10.9%); £3,752,423.06 -> £3,342,728.52 (10.9%); £3,752,423.30 -> £3,342,728.52 (10.9%); £3,752,423.53 -> £3,342,728.52 (10.9%); £3,752,423.73 -> £3,342,728.51 (10.9%); £3,752,423.89 -> £3,342,728.51 (10.9%); £3,752,424.05 -> £3,342,728.52 (10.9%); £3,752,424.20 -> £3,342,728.52 (10.9%); £3,752,424.36 -> £3,342,728.52 (10.9%); £3,752,424.52 -> £3,342,728.52 (10.9%); £3,752,424.67 -> £3,342,728.52 (10.9%); £3,752,424.83 -> £3,342,728.52 (10.9%); £3,752,424.99 -> £3,342,728.53 (10.9%); £3,752,425.15 -> £3,342,728.53 (10.9%); £3,752,425.30 -> £3,342,728.53 (10.9%); £3,752,425.46 -> £3,342,728.53 (10.9%); £3,752,425.62 -> £3,342,728.53 (10.9%); £3,752,425.77 -> £3,342,728.52 (10.9%); £3,752,425.95 -> £3,342,728.57 (10.9%); £3,752,426.15 -> £3,342,728.62 (10.9%); £3,752,426.35 -> £3,342,728.67 (10.9%); £3,752,426.58 -> £3,342,728.72 (10.9%); £3,752,426.82 -> £3,342,728.77 (10.9%); £3,752,427.07 -> £3,342,728.81 (10.9%); £3,752,427.33 -> £3,342,728.85 (10.9%); £3,752,427.59 -> £3,342,728.88 (10.9%); £3,752,427.84 -> £3,342,728.88 (10.9%); £3,752,428.11 -> £3,342,728.88 (10.9%); £3,752,428.37 -> £3,342,728.88 (10.9%); £3,752,428.63 -> £3,342,728.88 (10.9%); £3,752,428.90 -> £3,342,728.88 (10.9%); £3,752,429.16 -> £3,342,728.88 (10.9%); £3,752,429.43 -> £3,342,728.87 (10.9%); £3,752,429.69 -> £3,342,728.87 (10.9%); £3,752,429.95 -> £3,342,728.87 (10.9%); £3,752,430.21 -> £3,342,728.87 (10.9%); £3,752,430.48 -> £3,342,728.91 (10.9%); £3,752,430.67 -> £3,342,728.97 (10.9%); £3,752,430.93 -> £3,342,729.03 (10.9%); £3,752,431.13 -> £3,342,729.10 (10.9%); £3,752,431.33 -> £3,342,729.17 (10.9%); £3,752,431.60 -> £3,342,729.23 (10.9%); £3,752,431.86 -> £3,342,729.32 (10.9%); £3,752,432.05 -> £3,342,729.40 (10.9%); £3,752,432.32 -> £3,342,729.37 (10.9%); £3,752,432.57 -> £3,342,729.35 (10.9%); £3,752,432.84 -> £3,342,729.33 (10.9%); £3,752,433.11 -> £3,342,729.30 (10.9%); £3,752,433.37 -> £3,342,729.30 (10.9%); £3,752,433.64 -> £3,342,729.29 (10.9%); £3,752,433.88 -> £3,342,729.29 (10.9%); £3,752,434.11 -> £3,342,729.28 (10.9%); £3,752,434.31 -> £3,342,729.28 (10.9%); £3,752,434.47 -> £3,342,729.28 (10.9%); £3,752,434.62 -> £3,342,729.28 (10.9%); £3,752,434.77 -> £3,342,729.28 (10.9%); £3,752,434.93 -> £3,342,729.29 (10.9%); £3,752,435.09 -> £3,342,729.29 (10.9%); £3,752,435.24 -> £3,342,729.29 (10.9%); £3,752,435.40 -> £3,342,729.29 (10.9%); £3,752,435.55 -> £3,342,729.30 (10.9%); £3,752,435.70 -> £3,342,729.30 (10.9%); £3,752,435.86 -> £3,342,729.30 (10.9%); £3,752,436.01 -> £3,342,729.30 (10.9%); £3,752,436.17 -> £3,342,729.30 (10.9%); £3,752,436.32 -> £3,342,729.29 (10.9%); £3,752,436.49 -> £3,342,729.34 (10.9%); £3,752,436.68 -> £3,342,729.39 (10.9%); £3,752,436.88 -> £3,342,729.44 (10.9%); £3,752,437.11 -> £3,342,729.49 (10.9%); £3,752,437.35 -> £3,342,729.54 (10.9%); £3,752,437.61 -> £3,342,729.58 (10.9%); £3,752,437.87 -> £3,342,729.62 (10.9%); £3,752,438.13 -> £3,342,729.65 (10.9%); £3,752,438.39 -> £3,342,729.65 (10.9%); £3,752,438.64 -> £3,342,729.65 (10.9%); £3,752,438.90 -> £3,342,729.65 (10.9%); £3,752,439.15 -> £3,342,729.65 (10.9%); £3,752,439.41 -> £3,342,729.65 (10.9%); £3,752,439.67 -> £3,342,729.65 (10.9%); £3,752,439.93 -> £3,342,729.64 (10.9%); £3,752,440.19 -> £3,342,729.64 (10.9%); £3,752,440.44 -> £3,342,729.64 (10.9%); £3,752,440.68 -> £3,342,729.64 (10.9%); £3,752,440.95 -> £3,342,729.68 (10.9%); £3,752,441.20 -> £3,342,729.74 (10.9%); £3,752,441.46 -> £3,342,729.80 (10.9%); £3,752,441.72 -> £3,342,729.87 (10.9%); £3,752,441.91 -> £3,342,729.94 (10.9%); £3,752,442.10 -> £3,342,730.01 (10.9%); £3,752,442.36 -> £3,342,730.09 (10.9%); £3,752,442.56 -> £3,342,730.17 (10.9%); £3,752,442.81 -> £3,342,730.14 (10.9%); £3,752,443.07 -> £3,342,730.12 (10.9%); £3,752,443.33 -> £3,342,730.10 (10.9%); £3,752,443.58 -> £3,342,730.08 (10.9%); £3,752,443.85 -> £3,342,730.07 (10.9%); £3,752,444.11 -> £3,342,730.06 (10.9%); £3,752,444.35 -> £3,342,730.06 (10.9%); £3,752,444.57 -> £3,342,730.06 (10.9%); £3,752,444.77 -> £3,342,730.05 (10.9%); £3,752,444.93 -> £3,342,730.05 (10.9%); £3,752,445.08 -> £3,342,730.05 (10.9%); £3,752,445.24 -> £3,342,730.06 (10.9%); £3,752,445.40 -> £3,342,730.06 (10.9%); £3,752,445.55 -> £3,342,730.06 (10.9%); £3,752,445.71 -> £3,342,730.06 (10.9%); £3,752,445.87 -> £3,342,730.06 (10.9%); £3,752,446.02 -> £3,342,730.07 (10.9%); £3,752,446.18 -> £3,342,730.07 (10.9%); £3,752,446.33 -> £3,342,730.07 (10.9%); £3,752,446.48 -> £3,342,730.07 (10.9%); £3,752,446.64 -> £3,342,730.07 (10.9%); £3,752,446.79 -> £3,342,730.06 (10.9%); £3,752,446.97 -> £3,342,730.11 (10.9%); £3,752,447.15 -> £3,342,730.16 (10.9%); £3,752,447.36 -> £3,342,730.21 (10.9%); £3,752,447.58 -> £3,342,730.26 (10.9%); £3,752,447.81 -> £3,342,730.30 (10.9%); £3,752,448.07 -> £3,342,730.35 (10.9%); £3,752,448.33 -> £3,342,730.38 (10.9%); £3,752,448.59 -> £3,342,730.42 (10.9%); £3,752,448.85 -> £3,342,730.42 (10.9%); £3,752,449.11 -> £3,342,730.42 (10.9%); £3,752,449.38 -> £3,342,730.42 (10.9%); £3,752,449.64 -> £3,342,730.41 (10.9%); £3,752,449.90 -> £3,342,730.41 (10.9%); £3,752,450.16 -> £3,342,730.41 (10.9%); £3,752,450.43 -> £3,342,730.41 (10.9%); £3,752,450.69 -> £3,342,730.41 (10.9%); £3,752,450.95 -> £3,342,730.41 (10.9%); £3,752,451.21 -> £3,342,730.41 (10.9%); £3,752,451.47 -> £3,342,730.44 (10.9%); £3,752,451.72 -> £3,342,730.50 (10.9%); £3,752,451.98 -> £3,342,730.57 (10.9%); £3,752,452.24 -> £3,342,730.63 (10.9%); £3,752,452.51 -> £3,342,730.70 (10.9%); £3,752,452.78 -> £3,342,730.77 (10.9%); £3,752,453.04 -> £3,342,730.85 (10.9%); £3,752,453.31 -> £3,342,730.93 (10.9%); £3,752,453.56 -> £3,342,730.91 (10.9%); £3,752,453.83 -> £3,342,730.88 (10.9%); £3,752,454.09 -> £3,342,730.86 (10.9%); £3,752,454.35 -> £3,342,730.84 (10.9%); £3,752,454.62 -> £3,342,730.83 (10.9%); £3,752,454.88 -> £3,342,730.82 (10.9%); £3,752,455.12 -> £3,342,730.82 (10.9%); £3,752,455.34 -> £3,342,730.81 (10.9%); £3,752,455.54 -> £3,342,730.81 (10.9%); £3,752,455.68 -> £3,342,730.81 (10.9%); £3,752,455.81 -> £3,342,730.81 (10.9%); £3,752,455.94 -> £3,342,730.81 (10.9%); £3,752,456.08 -> £3,342,730.81 (10.9%); £3,752,456.22 -> £3,342,730.81 (10.9%); £3,752,456.35 -> £3,342,730.82 (10.9%); £3,752,456.49 -> £3,342,730.82 (10.9%); £3,752,456.62 -> £3,342,730.82 (10.9%); £3,752,456.76 -> £3,342,730.82 (10.9%); £3,752,456.90 -> £3,342,730.82 (10.9%); £3,752,457.04 -> £3,342,730.83 (10.9%); £3,752,457.18 -> £3,342,730.82 (10.9%); £3,752,457.31 -> £3,342,730.82 (10.9%); £3,752,457.47 -> £3,342,730.82 (10.9%); £3,752,457.63 -> £3,342,730.81 (10.9%); £3,752,457.81 -> £3,342,730.81 (10.9%); £3,752,458.01 -> £3,342,730.80 (10.9%); £3,752,458.22 -> £3,342,730.79 (10.9%); £3,752,458.45 -> £3,342,730.78 (10.9%); £3,752,458.68 -> £3,342,730.78 (10.9%); £3,752,458.90 -> £3,342,730.77 (10.9%); £3,752,459.12 -> £3,342,730.77 (10.9%); £3,752,459.34 -> £3,342,730.76 (10.9%); £3,752,459.57 -> £3,342,730.76 (10.9%); £3,752,459.79 -> £3,342,730.76 (10.9%); £3,752,460.02 -> £3,342,730.75 (10.9%); £3,752,460.25 -> £3,342,730.75 (10.9%); £3,752,460.49 -> £3,342,730.75 (10.9%); £3,752,460.72 -> £3,342,730.74 (10.9%); £3,752,460.94 -> £3,342,730.74 (10.9%); £3,752,461.17 -> £3,342,730.74 (10.9%); £3,752,461.40 -> £3,342,730.74 (10.9%); £3,752,461.62 -> £3,342,730.73 (10.9%); £3,752,461.85 -> £3,342,730.71 (10.9%); £3,752,462.07 -> £3,342,730.69 (10.9%); £3,752,462.30 -> £3,342,730.68 (10.9%); £3,752,462.52 -> £3,342,730.66 (10.9%); £3,752,462.75 -> £3,342,730.63 (10.9%); £3,752,462.98 -> £3,342,730.60 (10.9%); £3,752,463.21 -> £3,342,730.58 (10.9%); £3,752,463.44 -> £3,342,730.56 (10.9%); £3,752,463.67 -> £3,342,730.54 (10.9%); £3,752,463.89 -> £3,342,730.52 (10.9%); £3,752,464.12 -> £3,342,730.51 (10.9%); £3,752,464.33 -> £3,342,730.51 (10.9%); £3,752,464.55 -> £3,342,730.50 (10.9%); £3,752,464.74 -> £3,342,730.49 (10.9%); £3,752,464.92 -> £3,342,730.49 (10.9%); £3,752,465.05 -> £3,342,730.49 (10.9%); £3,752,465.19 -> £3,342,730.49 (10.9%); £3,752,465.32 -> £3,342,730.49 (10.9%); £3,752,465.45 -> £3,342,730.49 (10.9%); £3,752,465.59 -> £3,342,730.49 (10.9%); £3,752,465.73 -> £3,342,730.49 (10.9%); £3,752,465.86 -> £3,342,730.49 (10.9%); £3,752,465.99 -> £3,342,730.50 (10.9%); £3,752,466.13 -> £3,342,730.50 (10.9%); £3,752,466.27 -> £3,342,730.50 (10.9%); £3,752,466.41 -> £3,342,730.50 (10.9%); £3,752,466.54 -> £3,342,730.50 (10.9%); £3,752,466.68 -> £3,342,730.50 (10.9%); £3,752,466.83 -> £3,342,730.50 (10.9%); £3,752,466.99 -> £3,342,730.50 (10.9%); £3,752,467.17 -> £3,342,730.49 (10.9%); £3,752,467.37 -> £3,342,730.49 (10.9%); £3,752,467.58 -> £3,342,730.48 (10.9%); £3,752,467.80 -> £3,342,730.47 (10.9%); £3,752,468.03 -> £3,342,730.46 (10.9%); £3,752,468.26 -> £3,342,730.45 (10.9%); £3,752,468.49 -> £3,342,730.45 (10.9%); £3,752,468.71 -> £3,342,730.44 (10.9%); £3,752,468.92 -> £3,342,730.43 (10.9%); £3,752,469.15 -> £3,342,730.42 (10.9%); £3,752,469.38 -> £3,342,730.41 (10.9%); £3,752,469.61 -> £3,342,730.40 (10.9%); £3,752,469.83 -> £3,342,730.40 (10.9%); £3,752,470.06 -> £3,342,730.39 (10.9%); £3,752,470.28 -> £3,342,730.39 (10.9%); £3,752,470.51 -> £3,342,730.39 (10.9%); £3,752,470.75 -> £3,342,730.38 (10.9%); £3,752,470.98 -> £3,342,730.37 (10.9%); £3,752,471.20 -> £3,342,730.35 (10.9%); £3,752,471.43 -> £3,342,730.33 (10.9%); £3,752,471.66 -> £3,342,730.31 (10.9%); £3,752,471.88 -> £3,342,730.29 (10.9%); £3,752,472.11 -> £3,342,730.27 (10.9%); £3,752,472.33 -> £3,342,730.24 (10.9%); £3,752,472.54 -> £3,342,730.22 (10.9%); £3,752,472.77 -> £3,342,730.19 (10.9%); £3,752,473.00 -> £3,342,730.17 (10.9%); £3,752,473.24 -> £3,342,730.15 (10.9%); £3,752,473.47 -> £3,342,730.14 (10.9%); £3,752,473.69 -> £3,342,730.14 (10.9%); £3,752,473.90 -> £3,342,730.13 (10.9%); £3,752,474.09 -> £3,342,730.13 (10.9%); £3,752,474.27 -> £3,342,730.13 (10.9%); £3,752,474.42 -> £3,342,730.13 (10.9%); £3,752,474.58 -> £3,342,730.13 (10.9%); £3,752,474.73 -> £3,342,730.13 (10.9%); £3,752,474.89 -> £3,342,730.13 (10.9%); £3,752,475.04 -> £3,342,730.13 (10.9%); £3,752,475.20 -> £3,342,730.13 (10.9%); £3,752,475.35 -> £3,342,730.14 (10.9%); £3,752,475.51 -> £3,342,730.14 (10.9%); £3,752,475.66 -> £3,342,730.14 (10.9%); £3,752,475.81 -> £3,342,730.14 (10.9%); £3,752,475.97 -> £3,342,730.14 (10.9%); £3,752,476.13 -> £3,342,730.14 (10.9%); £3,752,476.28 -> £3,342,730.13 (10.9%); £3,752,476.45 -> £3,342,730.18 (10.9%); £3,752,476.64 -> £3,342,730.23 (10.9%); £3,752,476.84 -> £3,342,730.28 (10.9%); £3,752,477.07 -> £3,342,730.33 (10.9%); £3,752,477.31 -> £3,342,730.38 (10.9%); £3,752,477.57 -> £3,342,730.42 (10.9%); £3,752,477.83 -> £3,342,730.46 (10.9%); £3,752,478.10 -> £3,342,730.49 (10.9%); £3,752,478.36 -> £3,342,730.49 (10.9%); £3,752,478.61 -> £3,342,730.49 (10.9%); £3,752,478.87 -> £3,342,730.49 (10.9%); £3,752,479.13 -> £3,342,730.49 (10.9%); £3,752,479.39 -> £3,342,730.49 (10.9%); £3,752,479.65 -> £3,342,730.49 (10.9%); £3,752,479.91 -> £3,342,730.49 (10.9%); £3,752,480.17 -> £3,342,730.49 (10.9%); £3,752,480.42 -> £3,342,730.48 (10.9%); £3,752,480.69 -> £3,342,730.48 (10.9%); £3,752,480.95 -> £3,342,730.52 (10.9%); £3,752,481.19 -> £3,342,730.58 (10.9%); £3,752,481.45 -> £3,342,730.64 (10.9%); £3,752,481.70 -> £3,342,730.71 (10.9%); £3,752,481.95 -> £3,342,730.78 (10.9%); £3,752,482.21 -> £3,342,730.84 (10.9%); £3,752,482.46 -> £3,342,730.93 (10.9%); £3,752,482.72 -> £3,342,731.01 (10.9%); £3,752,482.98 -> £3,342,730.99 (10.9%); £3,752,483.24 -> £3,342,730.96 (10.9%); £3,752,483.49 -> £3,342,730.94 (10.9%); £3,752,483.76 -> £3,342,730.92 (10.9%); £3,752,484.01 -> £3,342,730.91 (10.9%); £3,752,484.27 -> £3,342,730.91 (10.9%); £3,752,484.51 -> £3,342,730.90 (10.9%); £3,752,484.73 -> £3,342,730.90 (10.9%); £3,752,484.93 -> £3,342,730.90 (10.9%); £3,752,485.08 -> £3,342,730.90 (10.9%); £3,752,485.23 -> £3,342,730.90 (10.9%); £3,752,485.39 -> £3,342,730.90 (10.9%); £3,752,485.55 -> £3,342,730.90 (10.9%); £3,752,485.70 -> £3,342,730.90 (10.9%); £3,752,485.86 -> £3,342,730.90 (10.9%); £3,752,486.01 -> £3,342,730.91 (10.9%); £3,752,486.15 -> £3,342,730.91 (10.9%); £3,752,486.30 -> £3,342,730.91 (10.9%); £3,752,486.46 -> £3,342,730.91 (10.9%); £3,752,486.61 -> £3,342,730.91 (10.9%); £3,752,486.76 -> £3,342,730.91 (10.9%); £3,752,486.92 -> £3,342,730.90 (10.9%); £3,752,487.09 -> £3,342,730.95 (10.9%); £3,752,487.28 -> £3,342,731.00 (10.9%); £3,752,487.48 -> £3,342,731.05 (10.9%); £3,752,487.71 -> £3,342,731.10 (10.9%); £3,752,487.94 -> £3,342,731.15 (10.9%); £3,752,488.20 -> £3,342,731.19 (10.9%); £3,752,488.46 -> £3,342,731.23 (10.9%); £3,752,488.71 -> £3,342,731.26 (10.9%); £3,752,488.97 -> £3,342,731.26 (10.9%); £3,752,489.23 -> £3,342,731.26 (10.9%); £3,752,489.48 -> £3,342,731.26 (10.9%); £3,752,489.73 -> £3,342,731.26 (10.9%); £3,752,490.00 -> £3,342,731.26 (10.9%); £3,752,490.25 -> £3,342,731.26 (10.9%); £3,752,490.50 -> £3,342,731.26 (10.9%); £3,752,490.76 -> £3,342,731.26 (10.9%); £3,752,491.01 -> £3,342,731.25 (10.9%); £3,752,491.28 -> £3,342,731.26 (10.9%); £3,752,491.54 -> £3,342,731.29 (10.9%); £3,752,491.80 -> £3,342,731.35 (10.9%); £3,752,492.06 -> £3,342,731.42 (10.9%); £3,752,492.31 -> £3,342,731.48 (10.9%); £3,752,492.56 -> £3,342,731.55 (10.9%); £3,752,492.82 -> £3,342,731.61 (10.9%); £3,752,493.08 -> £3,342,731.70 (10.9%); £3,752,493.34 -> £3,342,731.78 (10.9%); £3,752,493.60 -> £3,342,731.75 (10.9%); £3,752,493.86 -> £3,342,731.73 (10.9%); £3,752,494.10 -> £3,342,731.71 (10.9%); £3,752,494.36 -> £3,342,731.69 (10.9%); £3,752,494.62 -> £3,342,731.68 (10.9%); £3,752,494.88 -> £3,342,731.67 (10.9%); £3,752,495.12 -> £3,342,731.67 (10.9%); £3,752,495.33 -> £3,342,731.66 (10.9%); £3,752,495.53 -> £3,342,731.66 (10.9%); £3,752,495.68 -> £3,342,731.66 (10.9%); £3,752,495.83 -> £3,342,731.66 (10.9%); £3,752,495.98 -> £3,342,731.67 (10.9%); £3,752,496.13 -> £3,342,731.67 (10.9%); £3,752,496.27 -> £3,342,731.67 (10.9%); £3,752,496.43 -> £3,342,731.67 (10.9%); £3,752,496.58 -> £3,342,731.67 (10.9%); £3,752,496.74 -> £3,342,731.68 (10.9%); £3,752,496.88 -> £3,342,731.68 (10.9%); £3,752,497.04 -> £3,342,731.68 (10.9%); £3,752,497.19 -> £3,342,731.68 (10.9%); £3,752,497.34 -> £3,342,731.68 (10.9%); £3,752,497.50 -> £3,342,731.67 (10.9%); £3,752,497.67 -> £3,342,731.71 (10.9%); £3,752,497.86 -> £3,342,731.77 (10.9%); £3,752,498.07 -> £3,342,731.82 (10.9%); £3,752,498.29 -> £3,342,731.87 (10.9%); £3,752,498.52 -> £3,342,731.91 (10.9%); £3,752,498.78 -> £3,342,731.96 (10.9%); £3,752,499.03 -> £3,342,731.99 (10.9%); £3,752,499.28 -> £3,342,732.03 (10.9%); £3,752,499.53 -> £3,342,732.03 (10.9%); £3,752,499.79 -> £3,342,732.03 (10.9%); £3,752,500.06 -> £3,342,732.03 (10.9%); £3,752,500.32 -> £3,342,732.02 (10.9%); £3,752,500.57 -> £3,342,732.02 (10.9%); £3,752,500.84 -> £3,342,732.02 (10.9%); £3,752,501.10 -> £3,342,732.02 (10.9%); £3,752,501.34 -> £3,342,732.02 (10.9%); £3,752,501.60 -> £3,342,732.02 (10.9%); £3,752,501.85 -> £3,342,732.02 (10.9%); £3,752,502.11 -> £3,342,732.06 (10.9%); £3,752,502.37 -> £3,342,732.12 (10.9%); £3,752,502.63 -> £3,342,732.18 (10.9%); £3,752,502.89 -> £3,342,732.25 (10.9%); £3,752,503.16 -> £3,342,732.31 (10.9%); £3,752,503.41 -> £3,342,732.38 (10.9%); £3,752,503.67 -> £3,342,732.46 (10.9%); £3,752,503.91 -> £3,342,732.55 (10.9%); £3,752,504.17 -> £3,342,732.52 (10.9%); £3,752,504.42 -> £3,342,732.50 (10.9%); £3,752,504.68 -> £3,342,732.47 (10.9%); £3,752,504.94 -> £3,342,732.45 (10.9%); £3,752,505.19 -> £3,342,732.45 (10.9%); £3,752,505.44 -> £3,342,732.44 (10.9%); £3,752,505.68 -> £3,342,732.44 (10.9%); £3,752,505.90 -> £3,342,732.43 (10.9%); £3,752,506.10 -> £3,342,732.43 (10.9%); £3,752,506.25 -> £3,342,732.43 (10.9%); £3,752,506.40 -> £3,342,732.43 (10.9%); £3,752,506.56 -> £3,342,732.44 (10.9%); £3,752,506.71 -> £3,342,732.44 (10.9%); £3,752,506.85 -> £3,342,732.44 (10.9%); £3,752,507.01 -> £3,342,732.44 (10.9%); £3,752,507.16 -> £3,342,732.44 (10.9%); £3,752,507.31 -> £3,342,732.45 (10.9%); £3,752,507.47 -> £3,342,732.45 (10.9%); £3,752,507.62 -> £3,342,732.45 (10.9%); £3,752,507.78 -> £3,342,732.45 (10.9%); £3,752,507.93 -> £3,342,732.45 (10.9%); £3,752,508.08 -> £3,342,732.44 (10.9%); £3,752,508.24 -> £3,342,732.49 (10.9%); £3,752,508.43 -> £3,342,732.54 (10.9%); £3,752,508.63 -> £3,342,732.59 (10.9%); £3,752,508.84 -> £3,342,732.64 (10.9%); £3,752,509.09 -> £3,342,732.68 (10.9%); £3,752,509.35 -> £3,342,732.73 (10.9%); £3,752,509.61 -> £3,342,732.76 (10.9%); £3,752,509.87 -> £3,342,732.80 (10.9%); £3,752,510.12 -> £3,342,732.80 (10.9%); £3,752,510.37 -> £3,342,732.80 (10.9%); £3,752,510.62 -> £3,342,732.79 (10.9%); £3,752,510.87 -> £3,342,732.79 (10.9%); £3,752,511.13 -> £3,342,732.79 (10.9%); £3,752,511.38 -> £3,342,732.79 (10.9%); £3,752,511.64 -> £3,342,732.79 (10.9%); £3,752,511.89 -> £3,342,732.79 (10.9%); £3,752,512.15 -> £3,342,732.79 (10.9%); £3,752,512.41 -> £3,342,732.79 (10.9%); £3,752,512.66 -> £3,342,732.82 (10.9%); £3,752,512.92 -> £3,342,732.88 (10.9%); £3,752,513.18 -> £3,342,732.95 (10.9%); £3,752,513.43 -> £3,342,733.01 (10.9%); £3,752,513.69 -> £3,342,733.08 (10.9%); £3,752,513.95 -> £3,342,733.15 (10.9%); £3,752,514.20 -> £3,342,733.23 (10.9%); £3,752,514.46 -> £3,342,733.32 (10.9%); £3,752,514.71 -> £3,342,733.29 (10.9%); £3,752,514.97 -> £3,342,733.27 (10.9%); £3,752,515.23 -> £3,342,733.25 (10.9%); £3,752,515.48 -> £3,342,733.23 (10.9%); £3,752,515.73 -> £3,342,733.22 (10.9%); £3,752,515.98 -> £3,342,733.21 (10.9%); £3,752,516.22 -> £3,342,733.21 (10.9%); £3,752,516.43 -> £3,342,733.20 (10.9%); £3,752,516.64 -> £3,342,733.20 (10.9%); £3,752,516.79 -> £3,342,733.20 (10.9%); £3,752,516.94 -> £3,342,733.20 (10.9%); £3,752,517.09 -> £3,342,733.21 (10.9%); £3,752,517.24 -> £3,342,733.21 (10.9%); £3,752,517.40 -> £3,342,733.21 (10.9%); £3,752,517.55 -> £3,342,733.21 (10.9%); £3,752,517.70 -> £3,342,733.21 (10.9%); £3,752,517.85 -> £3,342,733.22 (10.9%); £3,752,518.01 -> £3,342,733.22 (10.9%); £3,752,518.16 -> £3,342,733.22 (10.9%); £3,752,518.31 -> £3,342,733.22 (10.9%); £3,752,518.46 -> £3,342,733.22 (10.9%); £3,752,518.62 -> £3,342,733.21 (10.9%); £3,752,518.79 -> £3,342,733.26 (10.9%); £3,752,518.98 -> £3,342,733.31 (10.9%); £3,752,519.18 -> £3,342,733.36 (10.9%); £3,752,519.39 -> £3,342,733.41 (10.9%); £3,752,519.64 -> £3,342,733.45 (10.9%); £3,752,519.90 -> £3,342,733.50 (10.9%); £3,752,520.16 -> £3,342,733.53 (10.9%); £3,752,520.42 -> £3,342,733.57 (10.9%); £3,752,520.67 -> £3,342,733.57 (10.9%); £3,752,520.93 -> £3,342,733.57 (10.9%); £3,752,521.19 -> £3,342,733.57 (10.9%); £3,752,521.44 -> £3,342,733.56 (10.9%); £3,752,521.70 -> £3,342,733.56 (10.9%); £3,752,521.95 -> £3,342,733.56 (10.9%); £3,752,522.21 -> £3,342,733.56 (10.9%); £3,752,522.46 -> £3,342,733.56 (10.9%); £3,752,522.72 -> £3,342,733.56 (10.9%); £3,752,522.97 -> £3,342,733.56 (10.9%); £3,752,523.23 -> £3,342,733.60 (10.9%); £3,752,523.49 -> £3,342,733.65 (10.9%); £3,752,523.73 -> £3,342,733.72 (10.9%); £3,752,523.99 -> £3,342,733.79 (10.9%); £3,752,524.24 -> £3,342,733.85 (10.9%); £3,752,524.50 -> £3,342,733.92 (10.9%); £3,752,524.75 -> £3,342,734.00 (10.9%); £3,752,525.00 -> £3,342,734.08 (10.9%); £3,752,525.26 -> £3,342,734.06 (10.9%); £3,752,525.52 -> £3,342,734.03 (10.9%); £3,752,525.77 -> £3,342,734.01 (10.9%); £3,752,526.01 -> £3,342,733.99 (10.9%); £3,752,526.28 -> £3,342,733.98 (10.9%); £3,752,526.54 -> £3,342,733.98 (10.9%); £3,752,526.77 -> £3,342,733.97 (10.9%); £3,752,526.98 -> £3,342,733.97 (10.9%); £3,752,527.18 -> £3,342,733.96 (10.9%); £3,752,527.31 -> £3,342,733.96 (10.9%); £3,752,527.44 -> £3,342,733.96 (10.9%); £3,752,527.57 -> £3,342,733.96 (10.9%); £3,752,527.71 -> £3,342,733.97 (10.9%); £3,752,527.84 -> £3,342,733.97 (10.9%); £3,752,527.98 -> £3,342,733.97 (10.9%); £3,752,528.11 -> £3,342,733.97 (10.9%); £3,752,528.25 -> £3,342,733.97 (10.9%); £3,752,528.38 -> £3,342,733.98 (10.9%); £3,752,528.51 -> £3,342,733.98 (10.9%); £3,752,528.65 -> £3,342,733.98 (10.9%); £3,752,528.78 -> £3,342,733.98 (10.9%); £3,752,528.92 -> £3,342,733.97 (10.9%); £3,752,529.07 -> £3,342,733.97 (10.9%); £3,752,529.23 -> £3,342,733.97 (10.9%); £3,752,529.41 -> £3,342,733.96 (10.9%); £3,752,529.61 -> £3,342,733.95 (10.9%); £3,752,529.82 -> £3,342,733.94 (10.9%); £3,752,530.05 -> £3,342,733.93 (10.9%); £3,752,530.27 -> £3,342,733.93 (10.9%); £3,752,530.49 -> £3,342,733.93 (10.9%); £3,752,530.72 -> £3,342,733.92 (10.9%); £3,752,530.93 -> £3,342,733.92 (10.9%); £3,752,531.16 -> £3,342,733.91 (10.9%); £3,752,531.39 -> £3,342,733.91 (10.9%); £3,752,531.61 -> £3,342,733.90 (10.9%); £3,752,531.83 -> £3,342,733.90 (10.9%); £3,752,532.06 -> £3,342,733.90 (10.9%); £3,752,532.29 -> £3,342,733.89 (10.9%); £3,752,532.52 -> £3,342,733.89 (10.9%); £3,752,532.75 -> £3,342,733.89 (10.9%); £3,752,532.97 -> £3,342,733.89 (10.9%); £3,752,533.20 -> £3,342,733.88 (10.9%); £3,752,533.42 -> £3,342,733.86 (10.9%); £3,752,533.65 -> £3,342,733.84 (10.9%); £3,752,533.88 -> £3,342,733.83 (10.9%); £3,752,534.10 -> £3,342,733.81 (10.9%); £3,752,534.32 -> £3,342,733.78 (10.9%); £3,752,534.55 -> £3,342,733.75 (10.9%); £3,752,534.77 -> £3,342,733.73 (10.9%); £3,752,534.98 -> £3,342,733.71 (10.9%); £3,752,535.21 -> £3,342,733.69 (10.9%); £3,752,535.43 -> £3,342,733.67 (10.9%); £3,752,535.65 -> £3,342,733.66 (10.9%); £3,752,535.87 -> £3,342,733.66 (10.9%); £3,752,536.09 -> £3,342,733.65 (10.9%); £3,752,536.27 -> £3,342,733.64 (10.9%); £3,752,536.45 -> £3,342,733.64 (10.9%); £3,752,536.58 -> £3,342,733.64 (10.9%); £3,752,536.71 -> £3,342,733.64 (10.9%); £3,752,536.85 -> £3,342,733.64 (10.9%); £3,752,536.99 -> £3,342,733.64 (10.9%); £3,752,537.12 -> £3,342,733.64 (10.9%); £3,752,537.26 -> £3,342,733.64 (10.9%); £3,752,537.39 -> £3,342,733.65 (10.9%); £3,752,537.53 -> £3,342,733.65 (10.9%); £3,752,537.66 -> £3,342,733.65 (10.9%); £3,752,537.80 -> £3,342,733.65 (10.9%); £3,752,537.93 -> £3,342,733.66 (10.9%); £3,752,538.07 -> £3,342,733.66 (10.9%); £3,752,538.21 -> £3,342,733.65 (10.9%); £3,752,538.35 -> £3,342,733.65 (10.9%); £3,752,538.52 -> £3,342,733.65 (10.9%); £3,752,538.70 -> £3,342,733.65 (10.9%); £3,752,538.90 -> £3,342,733.64 (10.9%); £3,752,539.10 -> £3,342,733.63 (10.9%); £3,752,539.33 -> £3,342,733.62 (10.9%); £3,752,539.56 -> £3,342,733.61 (10.9%); £3,752,539.78 -> £3,342,733.60 (10.9%); £3,752,540.01 -> £3,342,733.60 (10.9%); £3,752,540.23 -> £3,342,733.59 (10.9%); £3,752,540.46 -> £3,342,733.58 (10.9%); £3,752,540.68 -> £3,342,733.57 (10.9%); £3,752,540.90 -> £3,342,733.56 (10.9%); £3,752,541.12 -> £3,342,733.55 (10.9%); £3,752,541.34 -> £3,342,733.54 (10.9%); £3,752,541.57 -> £3,342,733.54 (10.9%); £3,752,541.80 -> £3,342,733.53 (10.9%); £3,752,542.02 -> £3,342,733.53 (10.9%); £3,752,542.24 -> £3,342,733.53 (10.9%); £3,752,542.47 -> £3,342,733.52 (10.9%); £3,752,542.69 -> £3,342,733.50 (10.9%); £3,752,542.92 -> £3,342,733.48 (10.9%); £3,752,543.15 -> £3,342,733.46 (10.9%); £3,752,543.37 -> £3,342,733.44 (10.9%); £3,752,543.58 -> £3,342,733.41 (10.9%); £3,752,543.80 -> £3,342,733.38 (10.9%); £3,752,544.02 -> £3,342,733.36 (10.9%); £3,752,544.24 -> £3,342,733.33 (10.9%); £3,752,544.47 -> £3,342,733.31 (10.9%); £3,752,544.70 -> £3,342,733.29 (10.9%); £3,752,544.92 -> £3,342,733.28 (10.9%); £3,752,545.14 -> £3,342,733.28 (10.9%); £3,752,545.35 -> £3,342,733.27 (10.9%); £3,752,545.54 -> £3,342,733.27 (10.9%); £3,752,545.72 -> £3,342,733.27 (10.9%); £3,752,545.87 -> £3,342,733.27 (10.9%); £3,752,546.02 -> £3,342,733.27 (10.9%); £3,752,546.17 -> £3,342,733.27 (10.9%); £3,752,546.33 -> £3,342,733.27 (10.9%); £3,752,546.48 -> £3,342,733.27 (10.9%); £3,752,546.63 -> £3,342,733.27 (10.9%); £3,752,546.78 -> £3,342,733.28 (10.9%); £3,752,546.94 -> £3,342,733.28 (10.9%); £3,752,547.09 -> £3,342,733.28 (10.9%); £3,752,547.24 -> £3,342,733.28 (10.9%); £3,752,547.39 -> £3,342,733.28 (10.9%); £3,752,547.54 -> £3,342,733.28 (10.9%); £3,752,547.68 -> £3,342,733.28 (10.9%); £3,752,547.85 -> £3,342,733.32 (10.9%); £3,752,548.04 -> £3,342,733.37 (10.9%); £3,752,548.25 -> £3,342,733.42 (10.9%); £3,752,548.47 -> £3,342,733.47 (10.9%); £3,752,548.71 -> £3,342,733.52 (10.9%); £3,752,548.96 -> £3,342,733.56 (10.9%); £3,752,549.21 -> £3,342,733.60 (10.9%); £3,752,549.46 -> £3,342,733.63 (10.9%); £3,752,549.72 -> £3,342,733.63 (10.9%); £3,752,549.98 -> £3,342,733.63 (10.9%); £3,752,550.23 -> £3,342,733.63 (10.9%); £3,752,550.49 -> £3,342,733.63 (10.9%); £3,752,550.73 -> £3,342,733.62 (10.9%); £3,752,550.98 -> £3,342,733.62 (10.9%); £3,752,551.23 -> £3,342,733.62 (10.9%); £3,752,551.49 -> £3,342,733.62 (10.9%); £3,752,551.74 -> £3,342,733.62 (10.9%); £3,752,552.00 -> £3,342,733.62 (10.9%); £3,752,552.25 -> £3,342,733.65 (10.9%); £3,752,552.50 -> £3,342,733.71 (10.9%); £3,752,552.75 -> £3,342,733.78 (10.9%); £3,752,553.01 -> £3,342,733.84 (10.9%); £3,752,553.27 -> £3,342,733.91 (10.9%); £3,752,553.52 -> £3,342,733.97 (10.9%); £3,752,553.78 -> £3,342,734.06 (10.9%); £3,752,554.02 -> £3,342,734.14 (10.9%); £3,752,554.27 -> £3,342,734.11 (10.9%); £3,752,554.52 -> £3,342,734.09 (10.9%); £3,752,554.78 -> £3,342,734.07 (10.9%); £3,752,555.04 -> £3,342,734.05 (10.9%); £3,752,555.29 -> £3,342,734.04 (10.9%); £3,752,555.55 -> £3,342,734.04 (10.9%); £3,752,555.78 -> £3,342,734.03 (10.9%); £3,752,555.99 -> £3,342,734.03 (10.9%); £3,752,556.19 -> £3,342,734.02 (10.9%); £3,752,556.34 -> £3,342,734.03 (10.9%); £3,752,556.48 -> £3,342,734.03 (10.9%); £3,752,556.63 -> £3,342,734.03 (10.9%); £3,752,556.78 -> £3,342,734.03 (10.9%); £3,752,556.93 -> £3,342,734.03 (10.9%); £3,752,557.08 -> £3,342,734.03 (10.9%); £3,752,557.23 -> £3,342,734.04 (10.9%); £3,752,557.39 -> £3,342,734.04 (10.9%); £3,752,557.53 -> £3,342,734.04 (10.9%); £3,752,557.68 -> £3,342,734.04 (10.9%); £3,752,557.83 -> £3,342,734.04 (10.9%); £3,752,557.98 -> £3,342,734.04 (10.9%); £3,752,558.13 -> £3,342,734.03 (10.9%); £3,752,558.30 -> £3,342,734.08 (10.9%); £3,752,558.49 -> £3,342,734.13 (10.9%); £3,752,558.69 -> £3,342,734.18 (10.9%); £3,752,558.91 -> £3,342,734.23 (10.9%); £3,752,559.14 -> £3,342,734.28 (10.9%); £3,752,559.39 -> £3,342,734.32 (10.9%); £3,752,559.64 -> £3,342,734.36 (10.9%); £3,752,559.89 -> £3,342,734.40 (10.9%); £3,752,560.14 -> £3,342,734.39 (10.9%); £3,752,560.40 -> £3,342,734.39 (10.9%); £3,752,560.65 -> £3,342,734.39 (10.9%); £3,752,560.90 -> £3,342,734.39 (10.9%); £3,752,561.15 -> £3,342,734.39 (10.9%); £3,752,561.40 -> £3,342,734.39 (10.9%); £3,752,561.65 -> £3,342,734.39 (10.9%); £3,752,561.91 -> £3,342,734.39 (10.9%); £3,752,562.16 -> £3,342,734.38 (10.9%); £3,752,562.41 -> £3,342,734.39 (10.9%); £3,752,562.67 -> £3,342,734.42 (10.9%); £3,752,562.92 -> £3,342,734.48 (10.9%); £3,752,563.18 -> £3,342,734.54 (10.9%); £3,752,563.43 -> £3,342,734.61 (10.9%); £3,752,563.70 -> £3,342,734.68 (10.9%); £3,752,563.95 -> £3,342,734.74 (10.9%); £3,752,564.21 -> £3,342,734.83 (10.9%); £3,752,564.46 -> £3,342,734.91 (10.9%); £3,752,564.71 -> £3,342,734.89 (10.9%); £3,752,564.95 -> £3,342,734.86 (10.9%); £3,752,565.19 -> £3,342,734.84 (10.9%); £3,752,565.44 -> £3,342,734.82 (10.9%); £3,752,565.69 -> £3,342,734.81 (10.9%); £3,752,565.94 -> £3,342,734.80 (10.9%); £3,752,566.18 -> £3,342,734.80 (10.9%); £3,752,566.40 -> £3,342,734.80 (10.9%); £3,752,566.59 -> £3,342,734.79 (10.9%); £3,752,566.74 -> £3,342,734.79 (10.9%); £3,752,566.89 -> £3,342,734.80 (10.9%); £3,752,567.05 -> £3,342,734.80 (10.9%); £3,752,567.20 -> £3,342,734.80 (10.9%); £3,752,567.35 -> £3,342,734.80 (10.9%); £3,752,567.50 -> £3,342,734.80 (10.9%); £3,752,567.66 -> £3,342,734.80 (10.9%); £3,752,567.80 -> £3,342,734.81 (10.9%); £3,752,567.96 -> £3,342,734.81 (10.9%); £3,752,568.10 -> £3,342,734.81 (10.9%); £3,752,568.26 -> £3,342,734.81 (10.9%); £3,752,568.41 -> £3,342,734.81 (10.9%); £3,752,568.56 -> £3,342,734.80 (10.9%); £3,752,568.73 -> £3,342,734.85 (10.9%); £3,752,568.91 -> £3,342,734.90 (10.9%); £3,752,569.10 -> £3,342,734.95 (10.9%); £3,752,569.32 -> £3,342,735.00 (10.9%); £3,752,569.57 -> £3,342,735.05 (10.9%); £3,752,569.81 -> £3,342,735.09 (10.9%); £3,752,570.06 -> £3,342,735.13 (10.9%); £3,752,570.31 -> £3,342,735.17 (10.9%); £3,752,570.57 -> £3,342,735.16 (10.9%); £3,752,570.82 -> £3,342,735.16 (10.9%); £3,752,571.07 -> £3,342,735.16 (10.9%); £3,752,571.32 -> £3,342,735.16 (10.9%); £3,752,571.57 -> £3,342,735.16 (10.9%); £3,752,571.83 -> £3,342,735.16 (10.9%); £3,752,572.08 -> £3,342,735.16 (10.9%); £3,752,572.32 -> £3,342,735.16 (10.9%); £3,752,572.57 -> £3,342,735.16 (10.9%); £3,752,572.82 -> £3,342,735.16 (10.9%); £3,752,573.07 -> £3,342,735.19 (10.9%); £3,752,573.31 -> £3,342,735.25 (10.9%); £3,752,573.57 -> £3,342,735.32 (10.9%); £3,752,573.81 -> £3,342,735.38 (10.9%); £3,752,574.07 -> £3,342,735.45 (10.9%); £3,752,574.31 -> £3,342,735.52 (10.9%); £3,752,574.56 -> £3,342,735.60 (10.9%); £3,752,574.80 -> £3,342,735.68 (10.9%); £3,752,575.06 -> £3,342,735.66 (10.9%); £3,752,575.30 -> £3,342,735.63 (10.9%); £3,752,575.55 -> £3,342,735.61 (10.9%); £3,752,575.80 -> £3,342,735.59 (10.9%); £3,752,576.04 -> £3,342,735.58 (10.9%); £3,752,576.30 -> £3,342,735.58 (10.9%); £3,752,576.54 -> £3,342,735.57 (10.9%); £3,752,576.75 -> £3,342,735.57 (10.9%); £3,752,576.94 -> £3,342,735.57 (10.9%); £3,752,577.09 -> £3,342,735.57 (10.9%); £3,752,577.24 -> £3,342,735.57 (10.9%); £3,752,577.40 -> £3,342,735.57 (10.9%); £3,752,577.55 -> £3,342,735.57 (10.9%); £3,752,577.70 -> £3,342,735.57 (10.9%); £3,752,577.85 -> £3,342,735.57 (10.9%); £3,752,578.00 -> £3,342,735.58 (10.9%); £3,752,578.15 -> £3,342,735.58 (10.9%); £3,752,578.30 -> £3,342,735.58 (10.9%); £3,752,578.46 -> £3,342,735.58 (10.9%); £3,752,578.61 -> £3,342,735.58 (10.9%); £3,752,578.76 -> £3,342,735.58 (10.9%); £3,752,578.91 -> £3,342,735.57 (10.9%); £3,752,579.07 -> £3,342,735.62 (10.9%); £3,752,579.25 -> £3,342,735.67 (10.9%); £3,752,579.45 -> £3,342,735.72 (10.9%); £3,752,579.67 -> £3,342,735.77 (10.9%); £3,752,579.90 -> £3,342,735.82 (10.9%); £3,752,580.16 -> £3,342,735.86 (10.9%); £3,752,580.41 -> £3,342,735.90 (10.9%); £3,752,580.66 -> £3,342,735.93 (10.9%); £3,752,580.91 -> £3,342,735.93 (10.9%); £3,752,581.16 -> £3,342,735.93 (10.9%); £3,752,581.42 -> £3,342,735.93 (10.9%); £3,752,581.67 -> £3,342,735.93 (10.9%); £3,752,581.92 -> £3,342,735.93 (10.9%); £3,752,582.17 -> £3,342,735.93 (10.9%); £3,752,582.42 -> £3,342,735.92 (10.9%); £3,752,582.67 -> £3,342,735.92 (10.9%); £3,752,582.93 -> £3,342,735.92 (10.9%); £3,752,583.18 -> £3,342,735.92 (10.9%); £3,752,583.44 -> £3,342,735.96 (10.9%); £3,752,583.69 -> £3,342,736.02 (10.9%); £3,752,583.95 -> £3,342,736.08 (10.9%); £3,752,584.21 -> £3,342,736.15 (10.9%); £3,752,584.46 -> £3,342,736.21 (10.9%); £3,752,584.72 -> £3,342,736.28 (10.9%); £3,752,584.97 -> £3,342,736.36 (10.9%); £3,752,585.21 -> £3,342,736.44 (10.9%); £3,752,585.47 -> £3,342,736.42 (10.9%); £3,752,585.72 -> £3,342,736.39 (10.9%); £3,752,585.97 -> £3,342,736.37 (10.9%); £3,752,586.22 -> £3,342,736.35 (10.9%); £3,752,586.47 -> £3,342,736.34 (10.9%); £3,752,586.73 -> £3,342,736.34 (10.9%); £3,752,586.96 -> £3,342,736.33 (10.9%); £3,752,587.17 -> £3,342,736.33 (10.9%); £3,752,587.37 -> £3,342,736.33 (10.9%); £3,752,587.52 -> £3,342,736.33 (10.9%); £3,752,587.67 -> £3,342,736.33 (10.9%); £3,752,587.82 -> £3,342,736.33 (10.9%); £3,752,587.97 -> £3,342,736.33 (10.9%); £3,752,588.12 -> £3,342,736.34 (10.9%); £3,752,588.28 -> £3,342,736.34 (10.9%); £3,752,588.43 -> £3,342,736.34 (10.9%); £3,752,588.58 -> £3,342,736.34 (10.9%); £3,752,588.73 -> £3,342,736.35 (10.9%); £3,752,588.88 -> £3,342,736.35 (10.9%); £3,752,589.03 -> £3,342,736.35 (10.9%); £3,752,589.18 -> £3,342,736.35 (10.9%); £3,752,589.33 -> £3,342,736.34 (10.9%); £3,752,589.50 -> £3,342,736.39 (10.9%); £3,752,589.69 -> £3,342,736.44 (10.9%); £3,752,589.89 -> £3,342,736.50 (10.9%); £3,752,590.11 -> £3,342,736.55 (10.9%); £3,752,590.34 -> £3,342,736.59 (10.9%); £3,752,590.60 -> £3,342,736.64 (10.9%); £3,752,590.86 -> £3,342,736.67 (10.9%); £3,752,591.10 -> £3,342,736.71 (10.9%); £3,752,591.35 -> £3,342,736.71 (10.9%); £3,752,591.60 -> £3,342,736.71 (10.9%); £3,752,591.85 -> £3,342,736.71 (10.9%); £3,752,592.10 -> £3,342,736.70 (10.9%); £3,752,592.35 -> £3,342,736.70 (10.9%); £3,752,592.60 -> £3,342,736.70 (10.9%); £3,752,592.86 -> £3,342,736.70 (10.9%); £3,752,593.11 -> £3,342,736.70 (10.9%); £3,752,593.37 -> £3,342,736.70 (10.9%); £3,752,593.62 -> £3,342,736.70 (10.9%); £3,752,593.86 -> £3,342,736.74 (10.9%); £3,752,594.12 -> £3,342,736.80 (10.9%); £3,752,594.37 -> £3,342,736.86 (10.9%); £3,752,594.62 -> £3,342,736.93 (10.9%); £3,752,594.88 -> £3,342,737.00 (10.9%); £3,752,595.12 -> £3,342,737.06 (10.9%); £3,752,595.37 -> £3,342,737.15 (10.9%); £3,752,595.62 -> £3,342,737.23 (10.9%); £3,752,595.87 -> £3,342,737.20 (10.9%); £3,752,596.13 -> £3,342,737.18 (10.9%); £3,752,596.38 -> £3,342,737.15 (10.9%); £3,752,596.64 -> £3,342,737.13 (10.9%); £3,752,596.89 -> £3,342,737.13 (10.9%); £3,752,597.14 -> £3,342,737.12 (10.9%); £3,752,597.37 -> £3,342,737.12 (10.9%); £3,752,597.58 -> £3,342,737.11 (10.9%); £3,752,597.77 -> £3,342,737.11 (10.9%); £3,752,597.91 -> £3,342,737.11 (10.9%); £3,752,598.04 -> £3,342,737.11 (10.9%); £3,752,598.18 -> £3,342,737.11 (10.9%); £3,752,598.31 -> £3,342,737.11 (10.9%); £3,752,598.45 -> £3,342,737.11 (10.9%); £3,752,598.58 -> £3,342,737.12 (10.9%); £3,752,598.72 -> £3,342,737.12 (10.9%); £3,752,598.86 -> £3,342,737.12 (10.9%); £3,752,598.99 -> £3,342,737.12 (10.9%); £3,752,599.13 -> £3,342,737.12 (10.9%); £3,752,599.26 -> £3,342,737.13 (10.9%); £3,752,599.40 -> £3,342,737.12 (10.9%); £3,752,599.54 -> £3,342,737.12 (10.9%); £3,752,599.68 -> £3,342,737.12 (10.9%); £3,752,599.86 -> £3,342,737.11 (10.9%); £3,752,600.03 -> £3,342,737.11 (10.9%); £3,752,600.23 -> £3,342,737.10 (10.9%); £3,752,600.44 -> £3,342,737.09 (10.9%); £3,752,600.66 -> £3,342,737.08 (10.9%); £3,752,600.89 -> £3,342,737.08 (10.9%); £3,752,601.11 -> £3,342,737.08 (10.9%); £3,752,601.33 -> £3,342,737.07 (10.9%); £3,752,601.56 -> £3,342,737.07 (10.9%); £3,752,601.79 -> £3,342,737.06 (10.9%); £3,752,602.01 -> £3,342,737.06 (10.9%); £3,752,602.23 -> £3,342,737.05 (10.9%); £3,752,602.46 -> £3,342,737.05 (10.9%); £3,752,602.67 -> £3,342,737.05 (10.9%); £3,752,602.89 -> £3,342,737.04 (10.9%); £3,752,603.11 -> £3,342,737.04 (10.9%); £3,752,603.33 -> £3,342,737.04 (10.9%); £3,752,603.55 -> £3,342,737.04 (10.9%); £3,752,603.77 -> £3,342,737.03 (10.9%); £3,752,604.00 -> £3,342,737.01 (10.9%); £3,752,604.22 -> £3,342,736.99 (10.9%); £3,752,604.45 -> £3,342,736.97 (10.9%); £3,752,604.68 -> £3,342,736.96 (10.9%); £3,752,604.91 -> £3,342,736.93 (10.9%); £3,752,605.12 -> £3,342,736.90 (10.9%); £3,752,605.35 -> £3,342,736.87 (10.9%); £3,752,605.57 -> £3,342,736.85 (10.9%); £3,752,605.80 -> £3,342,736.83 (10.9%); £3,752,606.02 -> £3,342,736.81 (10.9%); £3,752,606.24 -> £3,342,736.81 (10.9%); £3,752,606.46 -> £3,342,736.80 (10.9%); £3,752,606.66 -> £3,342,736.80 (10.9%); £3,752,606.85 -> £3,342,736.79 (10.9%); £3,752,607.03 -> £3,342,736.79 (10.9%); £3,752,607.17 -> £3,342,736.79 (10.9%); £3,752,607.30 -> £3,342,736.79 (10.9%); £3,752,607.43 -> £3,342,736.79 (10.9%); £3,752,607.56 -> £3,342,736.79 (10.9%); £3,752,607.70 -> £3,342,736.79 (10.9%); £3,752,607.84 -> £3,342,736.79 (10.9%); £3,752,607.97 -> £3,342,736.79 (10.9%); £3,752,608.10 -> £3,342,736.79 (10.9%); £3,752,608.24 -> £3,342,736.80 (10.9%); £3,752,608.39 -> £3,342,736.80 (10.9%); £3,752,608.52 -> £3,342,736.80 (10.9%); £3,752,608.66 -> £3,342,736.80 (10.9%); £3,752,608.79 -> £3,342,736.80 (10.9%); £3,752,608.94 -> £3,342,736.80 (10.9%); £3,752,609.11 -> £3,342,736.80 (10.9%); £3,752,609.29 -> £3,342,736.79 (10.9%); £3,752,609.49 -> £3,342,736.78 (10.9%); £3,752,609.70 -> £3,342,736.77 (10.9%); £3,752,609.93 -> £3,342,736.76 (10.9%); £3,752,610.16 -> £3,342,736.76 (10.9%); £3,752,610.38 -> £3,342,736.75 (10.9%); £3,752,610.60 -> £3,342,736.74 (10.9%); £3,752,610.83 -> £3,342,736.73 (10.9%); £3,752,611.05 -> £3,342,736.72 (10.9%); £3,752,611.28 -> £3,342,736.71 (10.9%); £3,752,611.51 -> £3,342,736.70 (10.9%); £3,752,611.74 -> £3,342,736.69 (10.9%); £3,752,611.96 -> £3,342,736.69 (10.9%); £3,752,612.19 -> £3,342,736.68 (10.9%); £3,752,612.42 -> £3,342,736.68 (10.9%); £3,752,612.65 -> £3,342,736.68 (10.9%); £3,752,612.88 -> £3,342,736.67 (10.9%); £3,752,613.10 -> £3,342,736.66 (10.9%); £3,752,613.32 -> £3,342,736.64 (10.9%); £3,752,613.55 -> £3,342,736.62 (10.9%); £3,752,613.78 -> £3,342,736.60 (10.9%); £3,752,614.01 -> £3,342,736.58 (10.9%); £3,752,614.23 -> £3,342,736.55 (10.9%); £3,752,614.45 -> £3,342,736.53 (10.9%); £3,752,614.68 -> £3,342,736.50 (10.9%); £3,752,614.90 -> £3,342,736.47 (10.9%); £3,752,615.12 -> £3,342,736.45 (10.9%); £3,752,615.35 -> £3,342,736.43 (10.9%); £3,752,615.58 -> £3,342,736.42 (10.9%); £3,752,615.81 -> £3,342,736.42 (10.9%); £3,752,616.02 -> £3,342,736.41 (10.9%); £3,752,616.22 -> £3,342,736.41 (10.9%); £3,752,616.40 -> £3,342,736.41 (10.9%); £3,752,616.55 -> £3,342,736.41 (10.9%); £3,752,616.70 -> £3,342,736.41 (10.9%); £3,752,616.86 -> £3,342,736.41 (10.9%); £3,752,617.01 -> £3,342,736.41 (10.9%); £3,752,617.16 -> £3,342,736.41 (10.9%); £3,752,617.31 -> £3,342,736.41 (10.9%); £3,752,617.47 -> £3,342,736.42 (10.9%); £3,752,617.62 -> £3,342,736.42 (10.9%); £3,752,617.77 -> £3,342,736.42 (10.9%); £3,752,617.92 -> £3,342,736.42 (10.9%); £3,752,618.08 -> £3,342,736.42 (10.9%); £3,752,618.23 -> £3,342,736.42 (10.9%); £3,752,618.39 -> £3,342,736.41 (10.9%); £3,752,618.56 -> £3,342,736.46 (10.9%); £3,752,618.75 -> £3,342,736.51 (10.9%); £3,752,618.96 -> £3,342,736.56 (10.9%); £3,752,619.18 -> £3,342,736.61 (10.9%); £3,752,619.42 -> £3,342,736.66 (10.9%); £3,752,619.68 -> £3,342,736.70 (10.9%); £3,752,619.93 -> £3,342,736.74 (10.9%); £3,752,620.19 -> £3,342,736.78 (10.9%); £3,752,620.45 -> £3,342,736.77 (10.9%); £3,752,620.70 -> £3,342,736.77 (10.9%); £3,752,620.94 -> £3,342,736.77 (10.9%); £3,752,621.19 -> £3,342,736.77 (10.9%); £3,752,621.45 -> £3,342,736.77 (10.9%); £3,752,621.70 -> £3,342,736.77 (10.9%); £3,752,621.97 -> £3,342,736.77 (10.9%); £3,752,622.23 -> £3,342,736.77 (10.9%); £3,752,622.48 -> £3,342,736.76 (10.9%); £3,752,622.74 -> £3,342,736.77 (10.9%); £3,752,623.00 -> £3,342,736.80 (10.9%); £3,752,623.26 -> £3,342,736.86 (10.9%); £3,752,623.52 -> £3,342,736.93 (10.9%); £3,752,623.78 -> £3,342,736.99 (10.9%); £3,752,624.03 -> £3,342,737.06 (10.9%); £3,752,624.29 -> £3,342,737.13 (10.9%); £3,752,624.55 -> £3,342,737.21 (10.9%); £3,752,624.80 -> £3,342,737.29 (10.9%); £3,752,625.06 -> £3,342,737.27 (10.9%); £3,752,625.31 -> £3,342,737.25 (10.9%); £3,752,625.57 -> £3,342,737.22 (10.9%); £3,752,625.82 -> £3,342,737.20 (10.9%); £3,752,626.08 -> £3,342,737.20 (10.9%); £3,752,626.34 -> £3,342,737.19 (10.9%); £3,752,626.57 -> £3,342,737.19 (10.9%); £3,752,626.79 -> £3,342,737.18 (10.9%); £3,752,626.99 -> £3,342,737.18 (10.9%); £3,752,627.15 -> £3,342,737.18 (10.9%); £3,752,627.30 -> £3,342,737.18 (10.9%); £3,752,627.46 -> £3,342,737.18 (10.9%); £3,752,627.61 -> £3,342,737.19 (10.9%); £3,752,627.76 -> £3,342,737.19 (10.9%); £3,752,627.92 -> £3,342,737.19 (10.9%); £3,752,628.07 -> £3,342,737.19 (10.9%); £3,752,628.23 -> £3,342,737.19 (10.9%); £3,752,628.38 -> £3,342,737.20 (10.9%); £3,752,628.54 -> £3,342,737.20 (10.9%); £3,752,628.69 -> £3,342,737.20 (10.9%); £3,752,628.85 -> £3,342,737.20 (10.9%); £3,752,629.00 -> £3,342,737.19 (10.9%); £3,752,629.17 -> £3,342,737.24 (10.9%); £3,752,629.37 -> £3,342,737.29 (10.9%); £3,752,629.58 -> £3,342,737.34 (10.9%); £3,752,629.80 -> £3,342,737.39 (10.9%); £3,752,630.04 -> £3,342,737.44 (10.9%); £3,752,630.30 -> £3,342,737.48 (10.9%); £3,752,630.55 -> £3,342,737.52 (10.9%); £3,752,630.81 -> £3,342,737.55 (10.9%); £3,752,631.06 -> £3,342,737.55 (10.9%); £3,752,631.32 -> £3,342,737.55 (10.9%); £3,752,631.57 -> £3,342,737.55 (10.9%); £3,752,631.83 -> £3,342,737.55 (10.9%); £3,752,632.10 -> £3,342,737.55 (10.9%); £3,752,632.36 -> £3,342,737.55 (10.9%); £3,752,632.63 -> £3,342,737.55 (10.9%); £3,752,632.89 -> £3,342,737.54 (10.9%); £3,752,633.15 -> £3,342,737.54 (10.9%); £3,752,633.41 -> £3,342,737.54 (10.9%); £3,752,633.66 -> £3,342,737.58 (10.9%); £3,752,633.91 -> £3,342,737.64 (10.9%); £3,752,634.17 -> £3,342,737.70 (10.9%); £3,752,634.43 -> £3,342,737.77 (10.9%); £3,752,634.69 -> £3,342,737.83 (10.9%); £3,752,634.94 -> £3,342,737.90 (10.9%); £3,752,635.21 -> £3,342,737.98 (10.9%); £3,752,635.46 -> £3,342,738.07 (10.9%); £3,752,635.73 -> £3,342,738.04 (10.9%); £3,752,635.98 -> £3,342,738.02 (10.9%); £3,752,636.23 -> £3,342,737.99 (10.9%); £3,752,636.49 -> £3,342,737.97 (10.9%); £3,752,636.75 -> £3,342,737.96 (10.9%); £3,752,637.00 -> £3,342,737.96 (10.9%); £3,752,637.24 -> £3,342,737.95 (10.9%); £3,752,637.46 -> £3,342,737.95 (10.9%); £3,752,637.65 -> £3,342,737.95 (10.9%); £3,752,637.81 -> £3,342,737.95 (10.9%); £3,752,637.97 -> £3,342,737.95 (10.9%); £3,752,638.12 -> £3,342,737.95 (10.9%); £3,752,638.27 -> £3,342,737.95 (10.9%); £3,752,638.42 -> £3,342,737.95 (10.9%); £3,752,638.58 -> £3,342,737.96 (10.9%); £3,752,638.73 -> £3,342,737.96 (10.9%); £3,752,638.89 -> £3,342,737.96 (10.9%); £3,752,639.04 -> £3,342,737.96 (10.9%); £3,752,639.20 -> £3,342,737.96 (10.9%); £3,752,639.36 -> £3,342,737.97 (10.9%); £3,752,639.52 -> £3,342,737.96 (10.9%); £3,752,639.67 -> £3,342,737.96 (10.9%); £3,752,639.84 -> £3,342,738.00 (10.9%); £3,752,640.03 -> £3,342,738.05 (10.9%); £3,752,640.24 -> £3,342,738.11 (10.9%); £3,752,640.47 -> £3,342,738.15 (10.9%); £3,752,640.71 -> £3,342,738.20 (10.9%); £3,752,640.97 -> £3,342,738.24 (10.9%); £3,752,641.23 -> £3,342,738.28 (10.9%); £3,752,641.49 -> £3,342,738.32 (10.9%); £3,752,641.74 -> £3,342,738.31 (10.9%); £3,752,641.99 -> £3,342,738.31 (10.9%); £3,752,642.25 -> £3,342,738.31 (10.9%); £3,752,642.51 -> £3,342,738.31 (10.9%); £3,752,642.76 -> £3,342,738.31 (10.9%); £3,752,643.01 -> £3,342,738.31 (10.9%); £3,752,643.27 -> £3,342,738.31 (10.9%); £3,752,643.52 -> £3,342,738.30 (10.9%); £3,752,643.78 -> £3,342,738.30 (10.9%); £3,752,644.03 -> £3,342,738.30 (10.9%); £3,752,644.30 -> £3,342,738.34 (10.9%); £3,752,644.55 -> £3,342,738.40 (10.9%); £3,752,644.81 -> £3,342,738.46 (10.9%); £3,752,645.07 -> £3,342,738.53 (10.9%); £3,752,645.33 -> £3,342,738.59 (10.9%); £3,752,645.58 -> £3,342,738.66 (10.9%); £3,752,645.85 -> £3,342,738.74 (10.9%); £3,752,646.10 -> £3,342,738.82 (10.9%); £3,752,646.36 -> £3,342,738.80 (10.9%); £3,752,646.62 -> £3,342,738.77 (10.9%); £3,752,646.88 -> £3,342,738.75 (10.9%); £3,752,647.12 -> £3,342,738.73 (10.9%); £3,752,647.38 -> £3,342,738.72 (10.9%); £3,752,647.63 -> £3,342,738.72 (10.9%); £3,752,647.88 -> £3,342,738.71 (10.9%); £3,752,648.10 -> £3,342,738.71 (10.9%); £3,752,648.30 -> £3,342,738.71 (10.9%); £3,752,648.46 -> £3,342,738.71 (10.9%); £3,752,648.61 -> £3,342,738.71 (10.9%); £3,752,648.77 -> £3,342,738.71 (10.9%); £3,752,648.92 -> £3,342,738.71 (10.9%); £3,752,649.07 -> £3,342,738.71 (10.9%); £3,752,649.22 -> £3,342,738.71 (10.9%); £3,752,649.37 -> £3,342,738.72 (10.9%); £3,752,649.52 -> £3,342,738.72 (10.9%); £3,752,649.67 -> £3,342,738.72 (10.9%); £3,752,649.83 -> £3,342,738.72 (10.9%); £3,752,649.98 -> £3,342,738.72 (10.9%); £3,752,650.13 -> £3,342,738.72 (10.9%); £3,752,650.29 -> £3,342,738.71 (10.9%); £3,752,650.46 -> £3,342,738.76 (10.9%); £3,752,650.64 -> £3,342,738.81 (10.9%); £3,752,650.85 -> £3,342,738.86 (10.9%); £3,752,651.07 -> £3,342,738.91 (10.9%); £3,752,651.31 -> £3,342,738.96 (10.9%); £3,752,651.56 -> £3,342,739.00 (10.9%); £3,752,651.83 -> £3,342,739.04 (10.9%); £3,752,652.08 -> £3,342,739.07 (10.9%); £3,752,652.34 -> £3,342,739.07 (10.9%); £3,752,652.59 -> £3,342,739.07 (10.9%); £3,752,652.85 -> £3,342,739.07 (10.9%); £3,752,653.11 -> £3,342,739.07 (10.9%); £3,752,653.36 -> £3,342,739.07 (10.9%); £3,752,653.61 -> £3,342,739.07 (10.9%); £3,752,653.87 -> £3,342,739.07 (10.9%); £3,752,654.12 -> £3,342,739.06 (10.9%); £3,752,654.38 -> £3,342,739.06 (10.9%); £3,752,654.63 -> £3,342,739.06 (10.9%); £3,752,654.89 -> £3,342,739.10 (10.9%); £3,752,655.15 -> £3,342,739.16 (10.9%); £3,752,655.39 -> £3,342,739.22 (10.9%); £3,752,655.65 -> £3,342,739.29 (10.9%); £3,752,655.91 -> £3,342,739.36 (10.9%); £3,752,656.17 -> £3,342,739.42 (10.9%); £3,752,656.43 -> £3,342,739.51 (10.9%); £3,752,656.68 -> £3,342,739.59 (10.9%); £3,752,656.94 -> £3,342,739.57 (10.9%); £3,752,657.19 -> £3,342,739.54 (10.9%); £3,752,657.44 -> £3,342,739.52 (10.9%); £3,752,657.70 -> £3,342,739.50 (10.9%); £3,752,657.95 -> £3,342,739.49 (10.9%); £3,752,658.20 -> £3,342,739.49 (10.9%); £3,752,658.44 -> £3,342,739.48 (10.9%); £3,752,658.66 -> £3,342,739.48 (10.9%); £3,752,658.86 -> £3,342,739.48 (10.9%); £3,752,659.02 -> £3,342,739.48 (10.9%); £3,752,659.17 -> £3,342,739.48 (10.9%); £3,752,659.32 -> £3,342,739.48 (10.9%); £3,752,659.48 -> £3,342,739.49 (10.9%); £3,752,659.63 -> £3,342,739.49 (10.9%); £3,752,659.78 -> £3,342,739.49 (10.9%); £3,752,659.93 -> £3,342,739.49 (10.9%); £3,752,660.09 -> £3,342,739.50 (10.9%); £3,752,660.23 -> £3,342,739.50 (10.9%); £3,752,660.38 -> £3,342,739.50 (10.9%); £3,752,660.54 -> £3,342,739.50 (10.9%); £3,752,660.69 -> £3,342,739.50 (10.9%); £3,752,660.85 -> £3,342,739.49 (10.9%); £3,752,661.02 -> £3,342,739.54 (10.9%); £3,752,661.21 -> £3,342,739.59 (10.9%); £3,752,661.42 -> £3,342,739.64 (10.9%); £3,752,661.64 -> £3,342,739.69 (10.9%); £3,752,661.88 -> £3,342,739.74 (10.9%); £3,752,662.15 -> £3,342,739.78 (10.9%); £3,752,662.41 -> £3,342,739.82 (10.9%); £3,752,662.67 -> £3,342,739.86 (10.9%); £3,752,662.92 -> £3,342,739.85 (10.9%); £3,752,663.19 -> £3,342,739.85 (10.9%); £3,752,663.44 -> £3,342,739.85 (10.9%); £3,752,663.70 -> £3,342,739.85 (10.9%); £3,752,663.96 -> £3,342,739.85 (10.9%); £3,752,664.21 -> £3,342,739.85 (10.9%); £3,752,664.47 -> £3,342,739.85 (10.9%); £3,752,664.72 -> £3,342,739.85 (10.9%); £3,752,664.98 -> £3,342,739.85 (10.9%); £3,752,665.24 -> £3,342,739.85 (10.9%); £3,752,665.50 -> £3,342,739.88 (10.9%); £3,752,665.75 -> £3,342,739.94 (10.9%); £3,752,666.02 -> £3,342,740.01 (10.9%); £3,752,666.27 -> £3,342,740.08 (10.9%); £3,752,666.53 -> £3,342,740.14 (10.9%); £3,752,666.78 -> £3,342,740.21 (10.9%); £3,752,667.04 -> £3,342,740.29 (10.9%); £3,752,667.30 -> £3,342,740.37 (10.9%); £3,752,667.57 -> £3,342,740.35 (10.9%); £3,752,667.82 -> £3,342,740.33 (10.9%); £3,752,668.08 -> £3,342,740.30 (10.9%); £3,752,668.33 -> £3,342,740.28 (10.9%); £3,752,668.59 -> £3,342,740.28 (10.9%); £3,752,668.85 -> £3,342,740.27 (10.9%); £3,752,669.09 -> £3,342,740.27 (10.9%); £3,752,669.31 -> £3,342,740.26 (10.9%); £3,752,669.51 -> £3,342,740.26 (10.9%); £3,752,669.65 -> £3,342,740.26 (10.9%); £3,752,669.78 -> £3,342,740.26 (10.9%); £3,752,669.92 -> £3,342,740.26 (10.9%); £3,752,670.06 -> £3,342,740.27 (10.9%); £3,752,670.19 -> £3,342,740.27 (10.9%); £3,752,670.33 -> £3,342,740.27 (10.9%); £3,752,670.47 -> £3,342,740.27 (10.9%); £3,752,670.61 -> £3,342,740.28 (10.9%); £3,752,670.74 -> £3,342,740.28 (10.9%); £3,752,670.88 -> £3,342,740.28 (10.9%); £3,752,671.01 -> £3,342,740.28 (10.9%); £3,752,671.15 -> £3,342,740.28 (10.9%); £3,752,671.28 -> £3,342,740.28 (10.9%); £3,752,671.43 -> £3,342,740.28 (10.9%); £3,752,671.59 -> £3,342,740.27 (10.9%); £3,752,671.78 -> £3,342,740.27 (10.9%); £3,752,671.98 -> £3,342,740.26 (10.9%); £3,752,672.19 -> £3,342,740.26 (10.9%); £3,752,672.42 -> £3,342,740.25 (10.9%); £3,752,672.65 -> £3,342,740.25 (10.9%); £3,752,672.87 -> £3,342,740.24 (10.9%); £3,752,673.10 -> £3,342,740.24 (10.9%); £3,752,673.32 -> £3,342,740.24 (10.9%); £3,752,673.55 -> £3,342,740.23 (10.9%); £3,752,673.78 -> £3,342,740.23 (10.9%); £3,752,674.01 -> £3,342,740.23 (10.9%); £3,752,674.24 -> £3,342,740.22 (10.9%); £3,752,674.46 -> £3,342,740.22 (10.9%); £3,752,674.69 -> £3,342,740.22 (10.9%); £3,752,674.91 -> £3,342,740.22 (10.9%); £3,752,675.13 -> £3,342,740.22 (10.9%); £3,752,675.36 -> £3,342,740.22 (10.9%); £3,752,675.58 -> £3,342,740.21 (10.9%); £3,752,675.82 -> £3,342,740.19 (10.9%); £3,752,676.04 -> £3,342,740.17 (10.9%); £3,752,676.28 -> £3,342,740.15 (10.9%); £3,752,676.51 -> £3,342,740.14 (10.9%); £3,752,676.73 -> £3,342,740.11 (10.9%); £3,752,676.96 -> £3,342,740.08 (10.9%); £3,752,677.18 -> £3,342,740.06 (10.9%); £3,752,677.41 -> £3,342,740.04 (10.9%); £3,752,677.64 -> £3,342,740.01 (10.9%); £3,752,677.86 -> £3,342,740.00 (10.9%); £3,752,678.09 -> £3,342,739.99 (10.9%); £3,752,678.31 -> £3,342,739.99 (10.9%); £3,752,678.53 -> £3,342,739.98 (10.9%); £3,752,678.71 -> £3,342,739.98 (10.9%); £3,752,678.89 -> £3,342,739.98 (10.9%); £3,752,679.03 -> £3,342,739.98 (10.9%); £3,752,679.17 -> £3,342,739.98 (10.9%); £3,752,679.31 -> £3,342,739.98 (10.9%); £3,752,679.45 -> £3,342,739.98 (10.9%); £3,752,679.59 -> £3,342,739.98 (10.9%); £3,752,679.73 -> £3,342,739.98 (10.9%); £3,752,679.87 -> £3,342,739.98 (10.9%); £3,752,680.01 -> £3,342,739.99 (10.9%); £3,752,680.16 -> £3,342,739.99 (10.9%); £3,752,680.29 -> £3,342,739.99 (10.9%); £3,752,680.44 -> £3,342,739.99 (10.9%); £3,752,680.58 -> £3,342,739.99 (10.9%); £3,752,680.73 -> £3,342,739.99 (10.9%); £3,752,680.88 -> £3,342,739.99 (10.9%); £3,752,681.05 -> £3,342,739.99 (10.9%); £3,752,681.24 -> £3,342,739.99 (10.9%); £3,752,681.44 -> £3,342,739.98 (10.9%); £3,752,681.66 -> £3,342,739.98 (10.9%); £3,752,681.88 -> £3,342,739.97 (10.9%); £3,752,682.12 -> £3,342,739.96 (10.9%); £3,752,682.36 -> £3,342,739.95 (10.9%); £3,752,682.59 -> £3,342,739.94 (10.9%); £3,752,682.82 -> £3,342,739.93 (10.9%); £3,752,683.05 -> £3,342,739.92 (10.9%); £3,752,683.28 -> £3,342,739.91 (10.9%); £3,752,683.51 -> £3,342,739.91 (10.9%); £3,752,683.75 -> £3,342,739.90 (10.9%); £3,752,683.98 -> £3,342,739.89 (10.9%); £3,752,684.20 -> £3,342,739.89 (10.9%); £3,752,684.44 -> £3,342,739.88 (10.9%); £3,752,684.67 -> £3,342,739.88 (10.9%); £3,752,684.90 -> £3,342,739.88 (10.9%); £3,752,685.14 -> £3,342,739.86 (10.9%); £3,752,685.37 -> £3,342,739.85 (10.9%); £3,752,685.60 -> £3,342,739.83 (10.9%); £3,752,685.83 -> £3,342,739.81 (10.9%); £3,752,686.07 -> £3,342,739.79 (10.9%); £3,752,686.30 -> £3,342,739.76 (10.9%); £3,752,686.53 -> £3,342,739.73 (10.9%); £3,752,686.77 -> £3,342,739.70 (10.9%); £3,752,687.01 -> £3,342,739.68 (10.9%); £3,752,687.25 -> £3,342,739.66 (10.9%); £3,752,687.49 -> £3,342,739.64 (10.9%); £3,752,687.72 -> £3,342,739.63 (10.9%); £3,752,687.95 -> £3,342,739.62 (10.9%); £3,752,688.18 -> £3,342,739.62 (10.9%); £3,752,688.38 -> £3,342,739.61 (10.9%); £3,752,688.56 -> £3,342,739.61 (10.9%); £3,752,688.72 -> £3,342,739.61 (10.9%); £3,752,688.88 -> £3,342,739.61 (10.9%); £3,752,689.03 -> £3,342,739.62 (10.9%); £3,752,689.20 -> £3,342,739.62 (10.9%); £3,752,689.36 -> £3,342,739.62 (10.9%); £3,752,689.52 -> £3,342,739.62 (10.9%); £3,752,689.68 -> £3,342,739.62 (10.9%); £3,752,689.85 -> £3,342,739.63 (10.9%); £3,752,690.01 -> £3,342,739.63 (10.9%); £3,752,690.17 -> £3,342,739.63 (10.9%); £3,752,690.33 -> £3,342,739.63 (10.9%); £3,752,690.49 -> £3,342,739.63 (10.9%); £3,752,690.65 -> £3,342,739.62 (10.9%); £3,752,690.83 -> £3,342,739.67 (10.9%); £3,752,691.03 -> £3,342,739.72 (10.9%); £3,752,691.25 -> £3,342,739.77 (10.9%); £3,752,691.48 -> £3,342,739.82 (10.9%); £3,752,691.73 -> £3,342,739.87 (10.9%); £3,752,692.01 -> £3,342,739.91 (10.9%); £3,752,692.27 -> £3,342,739.95 (10.9%); £3,752,692.56 -> £3,342,739.99 (10.9%); £3,752,692.83 -> £3,342,739.98 (10.9%); £3,752,693.10 -> £3,342,739.98 (10.9%); £3,752,693.37 -> £3,342,739.98 (10.9%); £3,752,693.64 -> £3,342,739.98 (10.9%); £3,752,693.90 -> £3,342,739.98 (10.9%); £3,752,694.17 -> £3,342,739.98 (10.9%); £3,752,694.45 -> £3,342,739.98 (10.9%); £3,752,694.72 -> £3,342,739.98 (10.9%); £3,752,694.99 -> £3,342,739.98 (10.9%); £3,752,695.27 -> £3,342,739.98 (10.9%); £3,752,695.54 -> £3,342,740.01 (10.9%); £3,752,695.81 -> £3,342,740.07 (10.9%); £3,752,696.07 -> £3,342,740.13 (10.9%); £3,752,696.34 -> £3,342,740.20 (10.9%); £3,752,696.60 -> £3,342,740.27 (10.9%); £3,752,696.86 -> £3,342,740.33 (10.9%); £3,752,697.13 -> £3,342,740.41 (10.9%); £3,752,697.40 -> £3,342,740.49 (10.9%); £3,752,697.66 -> £3,342,740.47 (10.9%); £3,752,697.94 -> £3,342,740.44 (10.9%); £3,752,698.20 -> £3,342,740.42 (10.9%); £3,752,698.46 -> £3,342,740.40 (10.9%); £3,752,698.73 -> £3,342,740.39 (10.9%); £3,752,699.00 -> £3,342,740.39 (10.9%); £3,752,699.24 -> £3,342,740.38 (10.9%); £3,752,699.47 -> £3,342,740.38 (10.9%); £3,752,699.68 -> £3,342,740.37 (10.9%); £3,752,699.84 -> £3,342,740.38 (10.9%); £3,752,700.00 -> £3,342,740.38 (10.9%); £3,752,700.17 -> £3,342,740.38 (10.9%); £3,752,700.33 -> £3,342,740.38 (10.9%); £3,752,700.50 -> £3,342,740.38 (10.9%); £3,752,700.66 -> £3,342,740.38 (10.9%); £3,752,700.82 -> £3,342,740.39 (10.9%); £3,752,700.98 -> £3,342,740.39 (10.9%); £3,752,701.15 -> £3,342,740.39 (10.9%); £3,752,701.31 -> £3,342,740.39 (10.9%); £3,752,701.47 -> £3,342,740.39 (10.9%); £3,752,701.63 -> £3,342,740.39 (10.9%); £3,752,701.79 -> £3,342,740.38 (10.9%); £3,752,701.97 -> £3,342,740.43 (10.9%); £3,752,702.17 -> £3,342,740.48 (10.9%); £3,752,702.39 -> £3,342,740.53 (10.9%); £3,752,702.63 -> £3,342,740.58 (10.9%); £3,752,702.87 -> £3,342,740.63 (10.9%); £3,752,703.14 -> £3,342,740.67 (10.9%); £3,752,703.42 -> £3,342,740.71 (10.9%); £3,752,703.70 -> £3,342,740.75 (10.9%); £3,752,703.96 -> £3,342,740.74 (10.9%); £3,752,704.22 -> £3,342,740.74 (10.9%); £3,752,704.48 -> £3,342,740.74 (10.9%); £3,752,704.75 -> £3,342,740.74 (10.9%); £3,752,705.02 -> £3,342,740.74 (10.9%); £3,752,705.29 -> £3,342,740.74 (10.9%); £3,752,705.55 -> £3,342,740.74 (10.9%); £3,752,705.82 -> £3,342,740.74 (10.9%); £3,752,706.09 -> £3,342,740.74 (10.9%); £3,752,706.36 -> £3,342,740.74 (10.9%); £3,752,706.63 -> £3,342,740.77 (10.9%); £3,752,706.91 -> £3,342,740.83 (10.9%); £3,752,707.17 -> £3,342,740.89 (10.9%); £3,752,707.44 -> £3,342,740.96 (10.9%); £3,752,707.71 -> £3,342,741.03 (10.9%); £3,752,707.98 -> £3,342,741.09 (10.9%); £3,752,708.24 -> £3,342,741.18 (10.9%); £3,752,708.51 -> £3,342,741.26 (10.9%); £3,752,708.77 -> £3,342,741.23 (10.9%); £3,752,709.03 -> £3,342,741.21 (10.9%); £3,752,709.31 -> £3,342,741.18 (10.9%); £3,752,709.58 -> £3,342,741.16 (10.9%); £3,752,709.85 -> £3,342,741.16 (10.9%); £3,752,710.12 -> £3,342,741.15 (10.9%); £3,752,710.37 -> £3,342,741.15 (10.9%); £3,752,710.60 -> £3,342,741.14 (10.9%); £3,752,710.81 -> £3,342,741.14 (10.9%); £3,752,710.98 -> £3,342,741.14 (10.9%); £3,752,711.14 -> £3,342,741.14 (10.9%); £3,752,711.30 -> £3,342,741.14 (10.9%); £3,752,711.45 -> £3,342,741.15 (10.9%); £3,752,711.61 -> £3,342,741.15 (10.9%); £3,752,711.77 -> £3,342,741.15 (10.9%); £3,752,711.93 -> £3,342,741.15 (10.9%); £3,752,712.09 -> £3,342,741.16 (10.9%); £3,752,712.24 -> £3,342,741.16 (10.9%); £3,752,712.41 -> £3,342,741.16 (10.9%); £3,752,712.57 -> £3,342,741.16 (10.9%); £3,752,712.72 -> £3,342,741.16 (10.9%); £3,752,712.88 -> £3,342,741.15 (10.9%); £3,752,713.06 -> £3,342,741.20 (10.9%); £3,752,713.26 -> £3,342,741.25 (10.9%); £3,752,713.48 -> £3,342,741.30 (10.9%); £3,752,713.71 -> £3,342,741.35 (10.9%); £3,752,713.96 -> £3,342,741.39 (10.9%); £3,752,714.23 -> £3,342,741.44 (10.9%); £3,752,714.50 -> £3,342,741.48 (10.9%); £3,752,714.76 -> £3,342,741.51 (10.9%); £3,752,715.04 -> £3,342,741.51 (10.9%); £3,752,715.30 -> £3,342,741.51 (10.9%); £3,752,715.57 -> £3,342,741.51 (10.9%); £3,752,715.84 -> £3,342,741.50 (10.9%); £3,752,716.12 -> £3,342,741.50 (10.9%); £3,752,716.39 -> £3,342,741.50 (10.9%); £3,752,716.67 -> £3,342,741.50 (10.9%); £3,752,716.93 -> £3,342,741.50 (10.9%); £3,752,717.20 -> £3,342,741.50 (10.9%); £3,752,717.47 -> £3,342,741.50 (10.9%); £3,752,717.74 -> £3,342,741.54 (10.9%); £3,752,718.01 -> £3,342,741.60 (10.9%); £3,752,718.28 -> £3,342,741.66 (10.9%); £3,752,718.55 -> £3,342,741.73 (10.9%); £3,752,718.82 -> £3,342,741.80 (10.9%); £3,752,719.09 -> £3,342,741.87 (10.9%); £3,752,719.36 -> £3,342,741.95 (10.9%); £3,752,719.63 -> £3,342,742.03 (10.9%); £3,752,719.89 -> £3,342,742.00 (10.9%); £3,752,720.16 -> £3,342,741.98 (10.9%); £3,752,720.43 -> £3,342,741.96 (10.9%); £3,752,720.70 -> £3,342,741.93 (10.9%); £3,752,720.97 -> £3,342,741.93 (10.9%); £3,752,721.25 -> £3,342,741.92 (10.9%); £3,752,721.50 -> £3,342,741.92 (10.9%); £3,752,721.72 -> £3,342,741.91 (10.9%); £3,752,721.93 -> £3,342,741.91 (10.9%); £3,752,722.09 -> £3,342,741.91 (10.9%); £3,752,722.25 -> £3,342,741.91 (10.9%); £3,752,722.42 -> £3,342,741.91 (10.9%); £3,752,722.58 -> £3,342,741.92 (10.9%); £3,752,722.73 -> £3,342,741.92 (10.9%); £3,752,722.90 -> £3,342,741.92 (10.9%); £3,752,723.05 -> £3,342,741.92 (10.9%); £3,752,723.22 -> £3,342,741.92 (10.9%); £3,752,723.37 -> £3,342,741.93 (10.9%); £3,752,723.53 -> £3,342,741.93 (10.9%); £3,752,723.70 -> £3,342,741.93 (10.9%); £3,752,723.86 -> £3,342,741.93 (10.9%); £3,752,724.02 -> £3,342,741.92 (10.9%); £3,752,724.21 -> £3,342,741.97 (10.9%); £3,752,724.41 -> £3,342,742.02 (10.9%); £3,752,724.63 -> £3,342,742.07 (10.9%); £3,752,724.86 -> £3,342,742.12 (10.9%); £3,752,725.11 -> £3,342,742.17 (10.9%); £3,752,725.39 -> £3,342,742.21 (10.9%); £3,752,725.65 -> £3,342,742.25 (10.9%); £3,752,725.92 -> £3,342,742.28 (10.9%); £3,752,726.19 -> £3,342,742.28 (10.9%); £3,752,726.46 -> £3,342,742.28 (10.9%); £3,752,726.74 -> £3,342,742.28 (10.9%); £3,752,727.01 -> £3,342,742.28 (10.9%); £3,752,727.28 -> £3,342,742.27 (10.9%); £3,752,727.55 -> £3,342,742.27 (10.9%); £3,752,727.83 -> £3,342,742.27 (10.9%); £3,752,728.10 -> £3,342,742.27 (10.9%); £3,752,728.37 -> £3,342,742.27 (10.9%); £3,752,728.64 -> £3,342,742.27 (10.9%); £3,752,728.91 -> £3,342,742.31 (10.9%); £3,752,729.20 -> £3,342,742.37 (10.9%); £3,752,729.47 -> £3,342,742.43 (10.9%); £3,752,729.74 -> £3,342,742.50 (10.9%); £3,752,730.00 -> £3,342,742.56 (10.9%); £3,752,730.27 -> £3,342,742.63 (10.9%); £3,752,730.55 -> £3,342,742.71 (10.9%); £3,752,730.83 -> £3,342,742.79 (10.9%); £3,752,731.10 -> £3,342,742.77 (10.9%); £3,752,731.38 -> £3,342,742.74 (10.9%); £3,752,731.65 -> £3,342,742.72 (10.9%); £3,752,731.92 -> £3,342,742.70 (10.9%); £3,752,732.20 -> £3,342,742.69 (10.9%); £3,752,732.47 -> £3,342,742.68 (10.9%); £3,752,732.72 -> £3,342,742.68 (10.9%); £3,752,732.96 -> £3,342,742.67 (10.9%); £3,752,733.18 -> £3,342,742.67 (10.9%); £3,752,733.34 -> £3,342,742.67 (10.9%); £3,752,733.50 -> £3,342,742.67 (10.9%); £3,752,733.66 -> £3,342,742.67 (10.9%); £3,752,733.83 -> £3,342,742.68 (10.9%); £3,752,733.99 -> £3,342,742.68 (10.9%); £3,752,734.15 -> £3,342,742.68 (10.9%); £3,752,734.31 -> £3,342,742.68 (10.9%); £3,752,734.48 -> £3,342,742.68 (10.9%); £3,752,734.64 -> £3,342,742.69 (10.9%); £3,752,734.80 -> £3,342,742.69 (10.9%); £3,752,734.96 -> £3,342,742.69 (10.9%); £3,752,735.12 -> £3,342,742.69 (10.9%); £3,752,735.28 -> £3,342,742.68 (10.9%); £3,752,735.46 -> £3,342,742.72 (10.9%); £3,752,735.66 -> £3,342,742.78 (10.9%); £3,752,735.88 -> £3,342,742.83 (10.9%); £3,752,736.11 -> £3,342,742.88 (10.9%); £3,752,736.36 -> £3,342,742.92 (10.9%); £3,752,736.62 -> £3,342,742.96 (10.9%); £3,752,736.90 -> £3,342,743.00 (10.9%); £3,752,737.16 -> £3,342,743.04 (10.9%); £3,752,737.43 -> £3,342,743.04 (10.9%); £3,752,737.70 -> £3,342,743.04 (10.9%); £3,752,737.97 -> £3,342,743.03 (10.9%); £3,752,738.25 -> £3,342,743.03 (10.9%); £3,752,738.53 -> £3,342,743.03 (10.9%); £3,752,738.80 -> £3,342,743.03 (10.9%); £3,752,739.06 -> £3,342,743.03 (10.9%); £3,752,739.34 -> £3,342,743.03 (10.9%); £3,752,739.60 -> £3,342,743.03 (10.9%); £3,752,739.87 -> £3,342,743.03 (10.9%); £3,752,740.14 -> £3,342,743.06 (10.9%); £3,752,740.41 -> £3,342,743.12 (10.9%); £3,752,740.68 -> £3,342,743.18 (10.9%); £3,752,740.95 -> £3,342,743.25 (10.9%); £3,752,741.22 -> £3,342,743.32 (10.9%); £3,752,741.49 -> £3,342,743.38 (10.9%); £3,752,741.76 -> £3,342,743.47 (10.9%); £3,752,742.04 -> £3,342,743.55 (10.9%); £3,752,742.30 -> £3,342,743.52 (10.9%); £3,752,742.57 -> £3,342,743.50 (10.9%); £3,752,742.86 -> £3,342,743.48 (10.9%); £3,752,743.12 -> £3,342,743.45 (10.9%); £3,752,743.39 -> £3,342,743.45 (10.9%); £3,752,743.66 -> £3,342,743.44 (10.9%); £3,752,743.91 -> £3,342,743.44 (10.9%); £3,752,744.15 -> £3,342,743.43 (10.9%)
- Bills issued: 147, average clarity 0.811, average bill shock 18.5%, bad debt provision £-212.24, avg complaint probability 4.9%
- Solvency signal: £375,569/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £199,889.17 vs. naked (unhedged) net margin: £605,205.21
- hedging cost £405,316.04 vs. a fully unhedged book (commodity-only: actual net £199,889.17 vs. naked net £605,205.21)
  - C2: actual £177.42 vs. naked £612.31 -- hedging cost £434.90
  - C2g: actual £210.76 vs. naked £379.08 -- hedging cost £168.32
  - C4: actual £85.60 vs. naked £374.56 -- hedging cost £288.96
  - C4g: actual £34.57 vs. naked £516.27 -- hedging cost £481.70
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £304.00 vs. naked £1,379.17 -- hedging cost £1,075.17
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £18,881.87 vs. naked £119,700.18 -- hedging cost £100,818.31
  - C_IC3g: actual £3,837.46 vs. naked £56,934.03 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £102,722.50 -- hedging cost £101,286.98

**Year narrative:** 2024 produced a net gain of £368,472.31 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 42 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £121,409.32 (gross £518,802.39, capital £5,661.91)
  - Electricity: gross £464,774.71, capital £5,632.07, net £116,827.98
  - Gas: gross £54,027.68, capital £29.84, net £4,581.34
- Treasury at year end: £3,807,612.61
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.89 (avg 0.89), C2g 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2025-01-08 period 31, net margin £-81.23

**Customer Book**

- Active accounts: 12 (C2, C2g, C4, C4g, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 0, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £367,901.52
  - By billing account: C1 £3,019.65, C2 £4,401.02, C3 £3,994.11, C4 £2,586.11, C5 £7,053.65, C6 £11,503.50, C7 £5,167.92, C8 £6,323.96, C9 £5,874.17, C_IC1 £1,164,867.12, C_IC2 £573,186.82, C_IC3 £1,901,080.89, C_IC4 £1,093,660.82
- Bill shock events (>=20%): 25 -- C7 2025-04-30 (36%); C7 2025-05-31 (37%); C7 2025-06-07 (157%); C2 2025-04-30 (23%); C2g 2025-01-31 (32%); C2g 2025-02-28 (24%); C2g 2025-04-30 (30%); C2g 2025-05-31 (34%); C2g 2025-06-07 (73%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (40%); C8 2025-05-31 (42%); C8 2025-06-07 (195%); C9 2025-04-30 (24%); C9 2025-05-31 (33%); C9 2025-06-07 (72%); C4 2025-04-30 (32%); C4 2025-06-07 (79%); C4g 2025-01-31 (24%); C4g 2025-05-31 (57%); C4g 2025-06-07 (126%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2 38%, C8 35%, C9 26%

**Pricing & Margin**

- C2 (electricity): tariff £149.29-£301.52/MWh, net margin £53.29
- C2g (gas): tariff £48.41-£52.00/MWh, net margin £91.08
- C4 (electricity): tariff £159.80-£305.07/MWh, net margin £81.71
- C4g (gas): tariff £48.05/MWh, net margin £40.47
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £19.93
- C8 (electricity): tariff £149.29-£303.79/MWh, net margin £100.10
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £225.43
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £63,404.31
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,994.92
- C_IC3 (electricity): tariff £88.78-£169.49/MWh, net margin £20,464.77
- C_IC3g (gas): tariff £49.06/MWh, net margin £4,449.79
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £2,483.52

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 72, average clarity 0.790, average bill shock 26.0%, bad debt provision £0.00, avg complaint probability 5.8%
- Solvency signal: £423,068/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-18.69 vs. naked (unhedged) net margin: £199.65
- hedging cost £218.34 vs. a fully unhedged book (commodity-only: actual net £-18.69 vs. naked net £199.65)
  - C2: actual £0.57 vs. naked £84.47 -- hedging cost £83.90
  - C2g: actual £7.37 vs. naked £-3.72 -- hedging added £11.08
  - C8: actual £-26.63 vs. naked £118.90 -- hedging cost £145.52

**Year narrative:** 2025 produced a net gain of £121,409.32 across 12 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 25 customer(s) experienced a bill shock of >=20%.
