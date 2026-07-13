# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,883,451.24
  (£1,416,815.02 net change)
- Solvency signal (final year): £423,072/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £22,585,671.01
  VAT remitted to HMRC: (£3,744,564.13) | Revenue (ex-VAT): £18,841,106.87
  Non-commodity pass-through: (£4,791,065.52)
- Gross margin: £6,455,406.22
- Capital costs: £51,272.56
- Net margin: £6,404,133.66
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1575, average clarity 0.789,
  service quality score 0.886
- Enterprise value (CLV sum across 13 billing accounts): £7,281,815.13
- Cost to serve (whole portfolio): £23,234.94, net margin after cost to serve: £6,380,898.72
- Hedge effectiveness (whole window): hedging cost £4,220,917.82 vs. a fully unhedged book (commodity-only: actual net £1,416,815.02 vs. naked net £5,637,732.84)

- **2021** (crisis year): net margin £78,288.16, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £339,911.67, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2250, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 218.5x (net £65,220.83 on £298.55 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 2/4 departures (50%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 4.7%, max 16.5% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +34.0% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 34.0% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,455,406.22, capital £51,272.56, net £6,404,133.66. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £78,288.16 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,404,133.66
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,637,732.84
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,220,917.82 vs. a fully unhedged book (commodity-only: actual net £1,416,815.02 vs. naked net £5,637,732.84)
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
| 2017 | £30,139.92 | £0.00 | £-74.10 | £813.19 | £516.54 | £31,395.55 |
| 2018 | £101,107.24 | £0.00 | £-453.01 | £690.69 | £437.73 | £101,782.65 |
| 2019 | £222,456.05 | £9,999.92 | £282.78 | £801.77 | £492.20 | £234,032.72 |
| 2020 | £116,612.12 | £10,030.76 | £406.45 | £851.93 | £458.98 | £128,360.24 |
| 2021 | £67,613.82 | £9,999.92 | £227.79 | £576.18 | £-129.54 | £78,288.16 |
| 2022 | £332,870.49 | £9,999.92 | £-66.08 | £-1,633.57 | £-1,259.09 | £339,911.67 |
| 2023 | £90,284.03 | £9,999.92 | £558.92 | £477.54 | £-973.01 | £100,347.41 |
| 2024 | £354,734.88 | £10,030.76 | £789.59 | £2,206.37 | £710.15 | £368,471.75 |
| 2025 | £116,347.52 | £4,449.79 | £0.00 | £480.46 | £131.60 | £121,409.36 |

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
| 2018 | 4 | +793.1% | 793.1% |
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
| 2018 | 3 | 1 | 54.1% | 13.8% | 1039.0% | 55.1% |
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
| 2021 | 297,852 | 215,054 | 82,798 | 22,472 | 50,441 | 15 | 9,870 | +3.3% |
| 2022 | 589,447 | 499,059 | 90,388 | 27,046 | 54,554 | 47 | 8,741 | +1.5% |
| 2023 | 298,695 | 177,398 | 121,297 | 32,230 | 79,964 | 75 | 9,027 | +3.0% |
| 2024 | 272,024 | 146,907 | 125,117 | 37,495 | 76,826 | 56 | 10,741 | +3.9% |
| 2025 | 133,764 | 79,736 | 54,028 | 17,243 | 32,173 | 30 | 4,581 | +3.4% |
| **Total** | **1,857,840** | **1,227,369** | **630,471** | **171,109** | **393,843** | **299** | **65,221** | **+3.5%** |

Gas book net margin positive over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,441 | 9 | 274,160 | 2108.92× | OK |
| 2017 | 2,498,923 | 10 | 249,892 | 1922.25× | OK |
| 2018 | 2,487,648 | 11 | 226,150 | 1739.61× | OK |
| 2019 | 2,611,861 | 12 | 217,655 | 1674.27× | OK |
| 2020 | 2,924,006 | 13 | 224,924 | 1730.18× | OK |
| 2021 | 2,956,000 | 11 | 268,727 | 2067.13× | OK |
| 2022 | 3,169,688 | 10 | 316,969 | 2438.22× | OK |
| 2023 | 3,342,739 | 10 | 334,274 | 2571.34× | OK |
| 2024 | 3,755,722 | 10 | 375,572 | 2889.02× | OK |
| 2025 | 3,807,649 | 9 | 423,072 | 3254.40× | OK |

End-state (2025): **£423,072/account** across 9 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,441 | 81974.8× | OK |
| 2017 | 466 | 559 | 2,498,923 | 4470.3× | OK |
| 2018 | 868 | 1,041 | 2,487,648 | 2389.0× | OK |
| 2019 | 1,543 | 1,851 | 2,611,861 | 1411.0× | OK |
| 2020 | 1,979 | 2,374 | 2,924,006 | 1231.5× | OK |
| 2021 | 4,343 | 5,211 | 2,956,000 | 567.2× | OK |
| 2022 | 8,501 | 10,201 | 3,169,688 | 310.7× | OK |
| 2023 | 5,596 | 6,715 | 3,342,739 | 497.8× | OK |
| 2024 | 2,646 | 3,175 | 3,755,722 | 1182.8× | OK |
| 2025 | 3,864 | 4,636 | 3,807,649 | 821.2× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,484.20 | £12,219.01 | £261.64/MWh | £144.45/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,954.68 | £9,679.35 | £272.02/MWh | £154.19/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,955.88 | £9,328.72 | £250.77/MWh | £142.00/MWh | +10.9% |

Total HH revenue: £63,621.84 vs flat equivalent £58,718.49 (+8.4% ToU premium)

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
| 2021-12-31 | C_IC3g | £20.1 | £123.8 (+516%) | 95% |
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
| Total offer cost (foregone margin) | £150,302.88 |
| Margin saved (retained customers' terms) | £1,215,034.83 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£1,064,731.95** |
| Acquisition cost avoided (retained customers) | £2,300.00 |
| **Full economic ROI (margin + acq savings)** | **£1,067,031.95** |

Missed opportunities (churns with no offer): **4** (£4,804.29 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 4 (£4,804.29 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 2 | 2 | £70.90 | £1352.58 | £1281.68 | £0.00 |
| 2018 | 2 | 2 | £24322.70 | £165380.57 | £141057.87 | £0.00 |
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
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24238.67 | £163839.43 | £150 | £139600.76 | retained |
| 2018-12-31 | C5 | 0.37 | 3% | £84.03 | £1541.14 | £400 | £1457.11 | retained |
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

Serial savers (2): C_IC1 (4 offers, £68,336), C_IC2 (3 offers, £29,586).

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £7,281,815.13 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £638,653.62 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,286.83 |
| 2017 | £31,395.55 |
| 2018 | £101,782.65 |
| 2019 | £234,032.72 |
| 2020 | £128,360.24 |
| 2021 | £78,288.16 |
| 2022 | £339,911.67 |
| 2023 | £100,347.41 | ← trailing
| 2024 | £368,471.75 | ← trailing
| 2025 | £121,409.36 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £4,512.14 | — |
| C2 | £6,174.25 | £914.98 |
| C3 | £5,445.32 | — |
| C4 | £4,034.54 | £-285.58 |
| C5 | £10,574.50 | — |
| C6 | £19,419.31 | £2,186.24 |
| C7 | £8,048.60 | £552.19 |
| C8 | £8,821.43 | £712.49 |
| C9 | £9,974.68 | £1,384.13 |
| C_IC1 | £1,649,116.32 | £378,062.45 |
| C_IC2 | £960,253.09 | £199,265.93 |
| C_IC3 | £3,089,743.99 | £40,337.47 |
| C_IC4 | £1,505,696.97 | £15,523.33 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £5,148.47 | — | — | — | £12,587.98 | — | £9,201.03 | — | — | — | — | — | — |
| 2017 | £5,231.67 | £10,444.03 | £8,807.25 | £8,105.00 | £12,043.37 | £23,950.54 | £8,859.84 | £13,645.68 | £11,194.96 | — | — | — | — |
| 2018 | £4,931.63 | £7,734.85 | £7,536.34 | £6,553.42 | £12,087.35 | £18,135.67 | £7,810.17 | £10,311.52 | £9,920.61 | £2,655,811.60 | — | — | — |
| 2019 | £4,477.66 | £6,355.17 | £7,157.50 | £6,398.64 | £10,449.89 | £20,925.93 | £7,993.90 | £9,755.59 | £9,238.92 | £2,149,050.75 | £1,229,305.58 | — | — |
| 2020 | £4,055.35 | £7,798.15 | £6,096.14 | £5,051.28 | £8,624.62 | £15,157.79 | £7,269.59 | £8,338.18 | £9,096.47 | £1,142,260.54 | £742,826.08 | £2,125,002.42 | £1,280,530.60 |
| 2021 | £4,005.70 | £7,172.35 | £5,224.53 | £4,518.54 | £9,669.04 | £14,814.77 | £6,744.29 | £8,504.21 | £7,859.11 | £1,298,591.46 | £575,995.83 | £2,034,411.43 | £1,365,158.58 |
| 2022 | £4,107.39 | £5,720.53 | £4,617.07 | £2,560.35 | £8,488.43 | £14,118.25 | £4,196.65 | £7,048.64 | £7,265.51 | £1,036,824.70 | £660,978.74 | £1,955,975.60 | £1,091,884.36 |
| 2023 | £2,879.15 | £4,712.53 | £4,190.93 | £1,703.13 | £7,086.15 | £15,274.45 | £4,614.01 | £6,353.34 | £6,179.50 | £970,715.37 | £597,173.15 | £1,380,932.43 | £984,426.99 |
| 2024 | £2,964.83 | £4,687.90 | £3,798.63 | £2,168.75 | £7,056.44 | £13,691.13 | £4,629.12 | £6,843.57 | £6,717.89 | £972,712.58 | £639,073.94 | £1,762,025.37 | £982,043.39 |
| 2025 | £3,019.63 | £4,402.36 | £3,994.10 | £2,589.98 | £7,053.73 | £11,503.53 | £5,167.90 | £6,323.99 | £5,874.17 | £1,164,918.22 | £573,178.15 | £1,901,080.89 | £1,093,660.82 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £1,290.83, range £219.95–£4,218.12.

- C1: cost to serve £329.93, net margin after CTS £2,471.17
- C1g: cost to serve £330.00, net margin after CTS £1,211.50
- C2: cost to serve £505.43, net margin after CTS £5,018.12
- C2g: cost to serve £505.55, net margin after CTS £2,783.87
- C3: cost to serve £219.95, net margin after CTS £2,165.56
- C3g: cost to serve £220.00, net margin after CTS £1,080.00
- C4: cost to serve £477.86, net margin after CTS £3,257.54
- C4g: cost to serve £477.97, net margin after CTS £1,215.30
- C5: cost to serve £599.87, net margin after CTS £7,238.83
- C6: cost to serve £959.77, net margin after CTS £21,820.42
- C7: cost to serve £519.13, net margin after CTS £10,210.12
- C8: cost to serve £505.43, net margin after CTS £11,909.26
- C9: cost to serve £491.72, net margin after CTS £12,256.32
- C_IC1: cost to serve £4,218.12, net margin after CTS £1,870,861.08
- C_IC2: cost to serve £3,718.18, net margin after CTS £905,452.18
- C_IC3: cost to serve £3,218.32, net margin after CTS £1,803,198.72
- C_IC3g: cost to serve £3,219.18, net margin after CTS £619,427.85
- C_IC4: cost to serve £2,718.52, net margin after CTS £1,103,966.75


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 27 recovery surcharge(s) at renewal based on prior-term losses (4 gas). Avg surcharge: 15.0%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.38/MWh |
| C5 | electricity | 2018-12-31 | £-207.02 | £2,324.15 | +3.9% | £148.68/MWh | £153.54/MWh |
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
| C4g | gas | 2022-09-30 | £-874.54 | £1,040.11 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,925.74 | £2,404.50 | +20.0% | £266.73/MWh | £319.35/MWh |
| C2 | electricity | 2023-03-31 | £-191.17 | £1,780.28 | +5.7% | £319.17/MWh | £372.45/MWh |
| C2g | gas | 2023-03-31 | £-319.85 | £1,782.04 | +12.9% | £83.68/MWh | £108.69/MWh |
| C8 | electricity | 2023-03-31 | £-348.38 | £3,898.74 | +3.9% | £319.17/MWh | £340.94/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £235.69/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.00/MWh |
| C4 | electricity | 2023-09-30 | £-292.88 | £1,307.19 | +17.4% | £216.77/MWh | £252.56/MWh |
| C4g | gas | 2023-09-30 | £-2,028.81 | £2,732.11 | +20.0% | £47.83/MWh | £65.13/MWh |
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
- **Estimated margin protected:** £1,215,034.83
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
| C5 | SME | MEDIUM | 27% | 8% | -21.2% [competitive] | £7,238.83 |
| C6 | SME | LOW | 13% | 25% | -26.1% [competitive] | £21,820.42 |
| C7 | resi | LOW | 11% | 17% | -14.3% | £10,210.12 |
| C9 | resi | LOW | 11% | 14% | -14.3% | £12,256.32 |
| C8 | resi | LOW | 10% | 13% | -23.6% [competitive] | £11,909.26 |
| C2 | resi | LOW | 9% | 10% | -23.6% [competitive] | £5,018.12 |
| C4 | resi | LOW | 8% | 17% | -9.0% | £3,257.54 |
| C_IC3 | I&C | LOW | 8% | 8% | -53.9% [competitive] | £1,803,198.72 |
| C1 | resi | LOW | 4% | 6% | -12.0% | £2,471.17 |
| C3 | resi | LOW | 4% | 10% | -38.6% [competitive] | £2,165.56 |
| C_IC2 | I&C | LOW | 4% | 95% | +12.4% [overpriced] | £905,452.18 |
| C_IC1 | I&C | LOW | 3% | 95% | -0.1% | £1,870,861.08 |

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
| C3 | resi | 2020-06-30 | 4.0yr | -3.6% | -38.6% | 4% | 10% | £2,165.56 |
| C5 | SME | 2020-12-30 | 5.0yr | +1.5% | -21.2% | 27% | 8% | £7,238.83 |
| C1 | resi | 2021-12-30 | 6.0yr | +1.4% | -12.0% | 4% | 6% | £2,471.17 |
| C6 | SME | 2024-03-30 | 8.0yr | -2.5% | -26.1% | 13% | 25% | £21,820.42 |

**Root Cause Summary:**
- Total churned accounts: 4
- Lifetime margin lost: £33,695.98
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
| 2018 | £1,041 | £868 | 0.24% |
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
| 2018 | 15 | £29,030 | £17,505 | £6,786 | 23.4% |
| 2019 | 17 | £70,487 | £41,300 | £13,767 | 19.5% |
| 2020 | 18 | £67,965 | £43,990 | £7,131 | 10.5% |
| 2021 | 15 | £115,826 | £51,042 | £5,219 | 4.5% << |
| 2022 | 13 | £264,460 | £80,840 | £26,147 | 9.9% |
| 2023 | 13 | £195,942 | £69,943 | £7,719 | 3.9% << |
| 2024 | 13 | £169,846 | £98,279 | £28,344 | 16.7% |
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
| C2g | — | £1,296 | £1,296 |
| C3 | £-121 | — | £-121 * |
| C3g | — | £338 | £338 |
| C4 | £457 | — | £457 |
| C4g | — | £-1,634 | £-1,634 * |
| C5 | £-173 | — | £-173 * |
| C6 | £2,142 | — | £2,142 |
| C7 | £-597 | — | £-597 * |
| C8 | £2,277 | — | £2,277 |
| C9 | £2,280 | — | £2,280 |
| C_IC1 | £846,808 | — | £846,808 |
| C_IC2 | £435,053 | — | £435,053 |
| C_IC3 | £118,085 | — | £118,085 |
| C_IC3g | — | £64,511 | £64,511 |
| C_IC4 | £32,221 | — | £32,221 |
| **Total** | **£1,440,065** | **£65,221** | **£1,505,286** |

Loss-making accounts: C4g (£-1,634), C7 (£-597), C5 (£-173), C3 (£-121)
Gas loss-making: C4g (£-1,634)
Gas portfolio net: £65,221 (4.3% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,047 | £10,957 | £-8,909 |
| 2017 | £30,075 | £112,480 | £-82,404 |
| 2018 | £109,539 | £246,624 | £-137,084 |
| 2019 | £252,598 | £836,879 | £-584,281 |
| 2020 | £83,611 | £961,080 | £-877,468 |
| 2021 | £200,853 | £466,561 | £-265,708 |
| 2022 | £138,305 | £1,159,440 | £-1,021,134 |
| 2023 | £399,917 | £1,238,307 | £-838,390 |
| 2024 | £199,889 | £605,205 | £-405,316 |
| 2025 | £-19 | £200 | £-218 |
| **Total** | **£1,416,815** | **£5,637,733** | **£-4,220,917** |

Largest hedging cost: **2022** (£1,021,134 vs naked)
Smallest hedging cost: **2025** (£218 vs naked)
Conclusion: systematic forward hedging cost £4,220,917 over 10 years vs spot purchasing.

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
| 2018 | — | — | £2,487,648 | £101,783 |
| 2019 | — | — | £2,611,861 | £234,033 |
| 2020 | — | — | £2,924,006 | £128,360 |
| 2021 | — | — | £2,956,000 | £78,288 |
| 2022 | 2.70 | WATCH | £3,169,688 | £339,912 |
| 2023 | 2.72 | WATCH | £3,342,739 | £100,347 |
| 2024 | — | — | £3,755,722 | £368,472 |
| 2025 | — | — | £3,807,649 | £121,409 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,807,649)**
**Treasury growth: £2,467,441 → £3,807,649 (+£1,340,208)**

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
| C_IC3g | 2021-12 | 20.11 | 123.81 | 95.0% |

**High-risk gas reprices: 10**

> ⚑ = customers with ≥15% churn estimate who received no retention offer.

## Retention Decision Economics

Per-offer cost, expected margin protected, and ROI for each retention intervention.

| Customer | Period | Retention Cost £ | Margin Protected £ | ROI | Discount % | Outcome |
|----------|--------|-----------------|-------------------|-----|------------|---------|
| C8 | 2017-04 | £46 | £861 | 18.8× | 3% | retained |
| C3 | 2017-07 | £25 | £491 | 19.6× | 3% | retained |
| C_IC1 | 2018-01 | £24,239 | £163,839 | 6.8× | 8% | retained |
| C5 | 2018-12 | £84 | £1,541 | 18.3× | 3% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £17,469 | £194,971 | 11.2× | 5% | retained |
| C_IC2 | 2021-03 | £5,378 | £93,555 | 17.4× | 3% | retained |
| C_IC1 | 2021-04 | £8,550 | £161,699 | 18.9× | 3% | retained |
| C_IC3 | 2021-12 | £51,991 | £169,022 | 3.3× | 5% | retained |
| C_IC2 | 2022-04 | £9,366 | £94,520 | 10.1× | 3% | retained |
| C_IC1 | 2022-05 | £18,078 | £229,473 | 12.7× | 3% | retained |
| C6 | 2023-03 | £235 | £3,420 | 14.5× | 3% | retained |

**Total retention spend: £150,303** | **Total margin protected: £1,215,035**
**Portfolio retention ROI: 8.1×** | **Retained: 12/12**
**Best ROI intervention: C3 2017-07 (19.6×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £185,277 | — |
| Exit Gas (with churn risk) | £72,428 | -£112,849 |
| Reprice to Breakeven | £186,912 | +£1,634 |

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
| 2018 | £1,041 | £9,350 | — | £17,434 | £905 |
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
| 2016 | 13 | £164,978 | £88,781 | £8,609 | £12,691 |
| 2017 | 1 | £3,124,154 | £1,875,079 | £846,808 | £3,124,154 |
| 2018 | 1 | £1,524,796 | £909,170 | £435,053 | £1,524,796 |
| 2019 | 2 | £6,444,848 | £2,429,064 | £182,596 | £3,222,424 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £32,221 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,222,424/customer)**
**Best net margin cohort: 2017 (£846,808)**

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
| 2018 | £5,058 | £1,364 | £3,201 | £252,952 | £0 | £262,575 |
| 2019 | £5,786 | £1,430 | £4,053 | £616,209 | £74,626 | £702,105 |
| 2020 | £5,695 | £1,211 | £4,228 | £704,719 | £75,972 | £791,825 |
| 2021 | £5,322 | £543 | £2,956 | £674,549 | £82,255 | £765,625 |
| 2022 | £3,239 | -£730 | £3,850 | £953,449 | £91,118 | £1,050,926 |
| 2023 | £5,923 | -£219 | £4,638 | £777,398 | £121,515 | £909,256 |
| 2024 | £7,695 | £1,466 | £1,574 | £1,143,236 | £123,652 | £1,277,622 |
| 2025 | £3,355 | £519 | £0 | £461,420 | £53,509 | £518,802 |

**Best gross margin year: 2024 (£1,277,622)** | **Worst: 2016 (£6,822)**
**Loss-making: resi gas in 2022 (£-730)**
**Loss-making: resi gas in 2023 (£-219)**


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
| 2018 | £2,487,648 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,611,861 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,924,006 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,956,000 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,169,688 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,342,739 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,755,722 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,807,649 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 41.3% | £1,247 | £634 | 1.62% |
| 2017 | 14 | 32.8% | £24,835 | £8,873 | 2.02% |
| 2018 | 15 | 41.0% | £40,019 | £17,555 | 2.23% |
| 2019 | 17 | 40.3% | £96,608 | £41,350 | 2.13% |
| 2020 | 18 | 40.2% | £103,260 | £44,315 | 2.35% |
| 2021 | 15 | 29.0% | £161,103 | £50,924 | 2.22% |
| 2022 | 13 | 22.2% | £326,110 | £80,969 | 2.27% |
| 2023 | 13 | 23.8% | £263,863 | £70,515 | 2.51% |
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
Generated: 2026-07-13T02:56:00Z

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
| 2018 | 10 | £2,740,833 | £274,083 | +£2,638,551 |
| 2019 | 11 | £3,461,110 | £314,646 | +£720,276 |
| 2020 | 13 | £5,362,107 | £412,470 | +£1,900,998 |
| 2021 | 13 | £5,342,670 | £410,975 | £-19,437 |
| 2022 | 13 | £4,803,786 | £369,522 | £-538,884 |
| 2023 | 13 | £3,986,241 | £306,634 | £-817,545 |
| 2024 | 13 | £4,408,414 | £339,109 | +£422,172 |
| 2025 | 13 | £4,782,767 | £367,905 | +£374,354 |

**Peak portfolio CLV: 2020 (£5,362,107)** | **Earliest/lowest: 2016 (£26,937)**
**Largest YoY gain: 2018 (+£2,638,551)**
**Largest YoY fall: 2023 (£-817,545)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

> **Basis: ledger/billed clock** (company.finance.double_entry journal, built from real issued bills). The Net Margin Bridge below reads a DIFFERENT clock (settlement, from the simulation's own per-period records) -- the two can diverge for the same year transition, primarily because non-commodity revenue recognition differs between the billed and settled bases for fixed-tariff records (see tools/generate_margin_bridge.py / the front page's reconciliation bridge for the quantified explanation).

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £16,206.51 | £3,594.97 | £4,363.77 | £8,247.77 | 50.9% | — | — | — | — |
| 2017 | £347,687.40 | £111,055.45 | £112,416.49 | £124,215.46 | 35.7% | +£331,480.89 | +£107,460.48 | +£108,052.72 | +£115,967.69 |
| 2018 | £600,281.26 | £172,888.03 | £164,071.67 | £263,321.56 | 43.9% | +£252,593.86 | +£61,832.59 | +£51,655.17 | +£139,106.10 |
| 2019 | £1,642,338.05 | £496,185.24 | £443,205.99 | £702,946.83 | 42.8% | +£1,042,056.79 | +£323,297.20 | +£279,134.32 | +£439,625.26 |
| 2020 | £1,858,681.92 | £431,597.51 | £629,411.89 | £797,672.52 | 42.9% | +£216,343.88 | £-64,587.72 | +£186,205.90 | +£94,725.70 |
| 2021 | £2,416,543.72 | £971,916.20 | £680,773.88 | £763,853.65 | 31.6% | +£557,861.80 | +£540,318.69 | +£51,361.99 | £-33,818.87 |
| 2022 | £4,239,425.11 | £2,387,110.07 | £799,720.68 | £1,052,594.36 | 24.8% | +£1,822,881.39 | +£1,415,193.88 | +£118,946.80 | +£288,740.71 |
| 2023 | £3,430,212.55 | £1,638,231.56 | £875,288.61 | £916,692.38 | 26.7% | £-809,212.56 | £-748,878.52 | +£75,567.94 | £-135,901.98 |
| 2024 | £3,016,001.74 | £931,171.08 | £811,332.71 | £1,273,497.95 | 42.2% | £-414,210.81 | £-707,060.48 | £-63,955.91 | +£356,805.58 |
| 2025 | £1,285,112.25 | £452,201.01 | £270,479.84 | £562,431.39 | 43.8% | £-1,730,889.49 | £-478,970.07 | £-540,852.87 | £-711,066.56 |

**Best GM year: 2016 (50.9%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Net Margin Bridge (Year-on-Year Attribution)

Decomposes each year's net margin change into: gross margin movement, bad debt, capital costs, policy levies, network costs.

> **Basis: settlement clock** (the simulation's own per-period records, years[]-based). The Gross Margin Bridge above reads a DIFFERENT clock (ledger/billed, from the double-entry journal built off real issued bills) -- the two can diverge for the same year transition; see tools/generate_margin_bridge.py / the front page's reconciliation bridge for the quantified explanation.

| Transition | Net Δ | Gross Δ | Bad Debt Δ | Capital Δ | Policy Δ | Network Δ | Portfolio | Driver | RAG |
|-----------|-------|---------|-----------|---------|---------|---------|---------|--------|-----|
| 2016→2017 | +£30,109 | +£116,398 | -£463 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£70,387 | +£139,354 | +£291 | -£367 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£132,250 | +£439,530 | +£132 | -£686 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£105,672 | +£89,720 | -£88 | +£361 | -£162,650 | -£33,016 | +1 | policy levies | RED |
| 2020→2021 | -£50,072 | -£26,200 | -£171 | -£3,667 | -£18,801 | -£1,234 | -3 | gross margin | RED |
| 2021→2022 | +£261,624 | +£285,301 | -£868 | -£7,627 | -£905 | -£14,277 | -2 | gross margin | GREEN |
| 2022→2023 | -£239,564 | -£141,671 | +£195 | +£3,498 | -£70,490 | -£31,097 | +0 | gross margin | RED |
| 2023→2024 | +£268,124 | +£368,366 | +£1,251 | +£97 | -£100,652 | -£938 | +0 | gross margin | GREEN |
| 2024→2025 | -£247,062 | -£758,820 | -£212 | +£4,003 | +£381,672 | +£126,295 | -1 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£247,062)** | **Best transition: 2023→2024 (+£268,124)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Unbilled Revenue Accrual (Accrual Accounting View)

An estimated-basis bill's revenue is recognised in full when issued (Phase 7a) -- that cash effect is correct and unchanged. This section shows how much of currently-recognised revenue is still PROVISIONAL (estimated, awaiting confirmation against a real meter read) versus already CONFIRMED, and how much has been RESTATED this run as D3's catch-up-rebilling resolved prior estimates.

**Outstanding unbilled revenue accrual: £571,416.76** across 62 bill(s) not yet confirmed by an actual read.

**Revenue restated this run: £6,393.77** across 150 catch-up correction(s) -- see the Net Margin Bridge above for the settlement-clock view and D3_catchup_rebilling for the per-bill mechanism.

| Customer | Outstanding Accrual £ |
|----------|------------------------|
| C_IC3g | £512,438.75 |
| C_IC4 | £54,849.20 |
| C3g | £1,416.53 |
| C3 | £1,197.23 |
| C4g | £709.81 |
| C2 | £372.58 |
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
| 2017 | £2,587,285.86 | £28,973.95 | 89.3x | ✓ GREEN | Yes |
| 2018 | £2,833,118.15 | £50,023.44 | 56.6x | ✓ GREEN | Yes |
| 2019 | £3,495,317.47 | £136,861.50 | 25.5x | ✓ GREEN | Yes |
| 2020 | £4,242,986.81 | £154,890.16 | 27.4x | ✓ GREEN | Yes |
| 2021 | £4,943,890.94 | £201,378.64 | 24.6x | ✓ GREEN | Yes |
| 2022 | £5,883,292.83 | £353,285.43 | 16.6x | ✓ GREEN | Yes |
| 2023 | £6,700,424.01 | £285,851.05 | 23.4x | ✓ GREEN | Yes |
| 2024 | £7,887,129.75 | £251,333.48 | 31.4x | ✓ GREEN | Yes |
| 2025 | £8,399,236.77 | £107,092.69 | 78.4x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.6x (equity £5,883,292.83 vs monthly revenue £353,285.43). RAG: GREEN.
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
| 2018 | £600,281.26 | £223,104.54 | £1,896.39 | ✓ GREEN |  |
| 2019 | £1,642,338.05 | £610,402.31 | £5,188.42 | ✓ GREEN |  |
| 2020 | £1,858,681.92 | £690,810.12 | £5,871.89 | ✓ GREEN |  |
| 2021 | £2,416,543.72 | £898,148.75 | £7,634.26 | ✓ GREEN | CREDIT EXPECTED |
| 2022 | £4,239,425.11 | £1,575,653.00 | £13,393.05 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,430,212.55 | £1,274,895.66 | £10,836.61 | ✓ GREEN |  |
| 2024 | £3,016,001.74 | £1,120,947.31 | £9,528.05 | ✓ GREEN |  |
| 2025 | £1,285,112.25 | £477,633.39 | £4,059.88 | ✓ GREEN |  |

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
| 2017 | 14 | £2,587,285.86 | £2,498,923.22 | 1170w | 0.23% | ✗ BREACH |
| 2018 | 15 | £2,833,118.15 | £2,487,648.38 | 748w | 0.05% | ✗ BREACH |
| 2019 | 17 | £3,495,317.47 | £2,611,861.23 | 274w | 0.01% | ✗ BREACH |
| 2020 | 18 | £4,242,986.81 | £2,924,005.63 | 352w | 0.02% | ✗ BREACH |
| 2021 | 15 | £4,943,890.94 | £2,955,999.74 | 158w | 0.02% | ✗ BREACH |
| 2022 | 13 | £5,883,292.83 | £3,169,687.86 | 69w | 0.04% | ✗ BREACH |
| 2023 | 13 | £6,700,424.01 | £3,342,739.02 | 106w | 0.04% | ✗ BREACH |
| 2024 | 13 | £7,887,129.75 | £3,755,721.70 | 210w | -0.01% | ✗ BREACH |
| 2025 | 12 | £8,399,236.77 | £3,807,649.10 | 438w | 0.00% | ✗ BREACH |

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
Median CLV: £9,974.68 | Median churn: 29% | Total portfolio CLV: £7,281,815.13

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £3,089,743.99 | 17% | 15.2 periods |
| C_IC4 | £1,505,696.97 | 20% | 12.0 periods |
| C6 | £19,419.31 | 23% | 13.1 periods |
| C9 | £9,974.68 | 26% | 13.8 periods |

Quadrant CLV: £4,624,834.94 (64% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC1 | £1,649,116.32 | 29% | 12.8 periods |
| C_IC2 | £960,253.09 | 32% | 14.2 periods |
| C5 | £10,574.50 | 32% | 13.8 periods |

Quadrant CLV: £2,619,943.91 (36% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C3 | £5,445.32 | 11% | 11.7 periods |
| C1 | £4,512.14 | 11% | 13.9 periods |

Quadrant CLV: £9,957.46 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £8,821.43 | 35% | 11.5 periods |
| C7 | £8,048.60 | 29% | 13.0 periods |
| C2 | £6,174.25 | 38% | 13.1 periods |
| C4 | £4,034.54 | 38% | 13.4 periods |

Quadrant CLV: £27,078.81 (0% of portfolio)

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
| 2017 | £30,879.00 | £516.54 | £231,615.36 | £2,660.42 | 1.1% | YES |
| 2018 | £101,344.92 | £437.73 | £432,336.88 | £3,114.73 | 0.7% | YES |
| 2019 | £223,540.59 | £10,492.12 | £1,060,518.56 | £137,768.61 | 11.5% | YES |
| 2020 | £117,870.50 | £10,489.74 | £1,102,238.83 | £121,126.13 | 9.9% | YES |
| 2021 | £68,417.78 | £9,870.38 | £1,439,533.10 | £297,851.59 | 17.1% | YES |
| 2022 | £331,170.84 | £8,740.82 | £2,848,531.85 | £589,446.82 | 17.1% | YES |
| 2023 | £91,320.50 | £9,026.91 | £2,248,552.03 | £298,694.92 | 11.7% | YES |
| 2024 | £357,730.84 | £10,740.91 | £1,935,979.93 | £272,024.29 | 12.3% | YES |
| 2025 | £116,827.98 | £4,581.38 | £837,239.45 | £133,763.99 | 13.8% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £185,277.29 | — | Current strategy |
| EXIT_GAS | £72,428.17 | £-112,849.12 | Remove gas; model elec churn risk |
| REPRICE_GAS | £186,911.78 | £1,634.49 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-1,634.49 | -10.37x | +14.1% |

**Accretive gas accounts:** C1g (£710.49), C2g (£1,295.92), C3g (£337.93), C_IC3g (£64,510.98) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £65221 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,697,351.88 | £50,101.97 | £1,432,166.06 | 28.6x | Strong |
| I&C gas | £622,647.03 | £0.00 | £64,510.98 | 0.0x | Low return |
| SME electricity | £30,618.89 | £326.89 | £1,968.77 | 6.0x | Moderate |
| resi electricity | £50,337.55 | £545.15 | £5,930.67 | 10.9x | Moderate |
| resi gas | £7,824.19 | £298.55 | £709.85 | 2.4x | Low return |

## Portfolio Concentration Risk

Revenue concentration analysis across 18 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2250** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,302,906.58 (98.7% of total positive margin)
- resi: £53,578.76 (0.8% of total positive margin)
- SME: £29,059.25 (0.5% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,870,861.08 | 29.3% | 3% | £60,428.81 |
| C_IC3 | I&C | £1,803,198.72 | 28.2% | 8% | £151,649.01 |
| C_IC4 | I&C | £1,103,966.75 | 17.3% | 0% | £0.00 |
| C_IC2 | I&C | £905,452.18 | 14.2% | 4% | £33,230.09 |
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
| C_IC1 | electricity | 2018-01-31 | -18.3% | +13.1% | £112.24/MWh | £126.98/MWh |
| C2 | electricity | 2018-04-01 | -7.0% | +7.5% | £133.89/MWh | £143.93/MWh |
| C2g | gas | 2018-04-01 | 15.4% | -3.7% | £38.21/MWh | £36.79/MWh |
| C6 | electricity | 2018-04-01 | -4.4% | +6.2% | £133.89/MWh | £142.20/MWh |
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
| C_IC3g | gas | 2021-12-31 | -18.2% | +13.1% | £109.48/MWh | £123.81/MWh |
| C2 | electricity | 2022-03-31 | -24.4% | +15.0% | £361.95/MWh | £416.24/MWh |
| C2g | gas | 2022-03-31 | -19.2% | +13.6% | £99.49/MWh | £113.04/MWh |
| C6 | electricity | 2022-03-31 | -20.6% | +14.3% | £361.95/MWh | £413.77/MWh |
| C8 | electricity | 2022-03-31 | 2.6% | +2.7% | £361.95/MWh | £371.62/MWh |
| C_IC2 | electricity | 2022-04-30 | -9.1% | +8.6% | £269.81/MWh | £292.92/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.1% | +7.1% | £239.42/MWh | £256.31/MWh |
| C9 | electricity | 2022-06-30 | 4.2% | +1.9% | £255.09/MWh | £259.90/MWh |
| C4 | electricity | 2022-09-30 | 7.1% | +0.4% | £404.86/MWh | £406.63/MWh |
| C4g | gas | 2022-09-30 | -24.4% | +15.0% | £183.79/MWh | £211.36/MWh |
| C7 | electricity | 2022-12-30 | 8.5% | -0.2% | £266.73/MWh | £266.13/MWh |
| C_IC3 | electricity | 2022-12-31 | -0.6% | +4.3% | £168.36/MWh | £175.62/MWh |
| C_IC3g | gas | 2022-12-31 | -43.9% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2 | electricity | 2023-03-31 | -12.7% | +10.4% | £319.17/MWh | £352.24/MWh |
| C2g | gas | 2023-03-31 | -22.1% | +15.0% | £83.68/MWh | £96.23/MWh |
| C6 | electricity | 2023-03-31 | -5.2% | +6.6% | £319.17/MWh | £340.22/MWh |
| C8 | electricity | 2023-03-31 | 2.5% | +2.8% | £319.17/MWh | £328.03/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.1% | +14.6% | £171.46/MWh | £196.41/MWh |
| C_IC1 | electricity | 2023-06-29 | -16.7% | +12.3% | £163.19/MWh | £183.33/MWh |
| C9 | electricity | 2023-06-30 | -10.5% | +9.2% | £224.44/MWh | £245.20/MWh |
| C4 | electricity | 2023-09-30 | 9.5% | -0.8% | £216.77/MWh | £215.12/MWh |
| C4g | gas | 2023-09-30 | -19.0% | +13.5% | £47.83/MWh | £54.27/MWh |
| C7 | electricity | 2023-12-30 | 27.3% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 21.9% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -7.7% | +7.9% | £51.89/MWh | £55.98/MWh |
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
| C2+C2g | £1,177.94 | £1,295.92 | £2,473.85 | Yes |
| C1+C1g | £457.74 | £710.49 | £1,168.23 | Yes |
| C3+C3g | £-121.37 | £337.93 | £216.56 | Yes |
| C4+C4g | £457.16 | £-1,634.49 | £-1,177.33 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £65,220.83.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,505,286.33 across 18 billing accounts. Revenue: £14,003,414.67.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,124,153.76 | £1,875,079.20 | £18,451.80 | £846,807.80 | 27.1% |
| 2 | C_IC2 | fixed | £1,524,795.72 | £909,170.36 | £8,631.82 | £435,052.61 | 28.5% |
| 3 | C_IC3 | pass_through | £4,612,268.10 | £1,806,417.04 | £23,018.35 | £118,085.00 | 2.6% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £64,510.98 | 3.5% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £32,220.65 | 1.2% |
| 6 | C9 | fixed | £20,284.60 | £12,748.04 | £131.67 | £2,279.56 | 11.2% |
| 7 | C8 | fixed | £21,634.03 | £12,414.69 | £134.50 | £2,276.51 | 10.5% |
| 8 | C6 | fixed | £39,263.49 | £22,780.19 | £266.71 | £2,142.19 | 5.5% |
| 9 | C2g | fixed | £8,092.66 | £3,289.42 | £106.78 | £1,295.92 | 16.0% |
| 10 | C2 | fixed | £9,516.51 | £5,523.55 | £58.29 | £1,177.94 | 12.4% |
| 11 | C1g | fixed | £2,894.78 | £1,541.50 | £18.80 | £710.49 | 24.5% |
| 12 | C1 | fixed | £4,290.21 | £2,801.10 | £19.84 | £457.74 | 10.7% |
| 13 | C4 | fixed | £6,895.81 | £3,735.40 | £45.12 | £457.16 | 6.6% |
| 14 | C3g | fixed | £2,684.78 | £1,300.00 | £15.29 | £337.93 | 12.6% |
| 15 | C3 | fixed | £3,625.38 | £2,385.51 | £14.75 | £-121.37 | -3.3% |
| 16 | C5 | fixed | £12,505.19 | £7,838.70 | £60.18 | £-173.43 | -1.4% |
| 17 | C7 | fixed | £21,703.21 | £10,729.26 | £140.99 | £-596.87 | -2.8% |
| 18 | C4g | fixed | £11,587.67 | £1,693.27 | £157.68 | £-1,634.49 | -14.1% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,003,415 | 100.0% |
| Wholesale cost | -£7,594,635 | 54.2% |
| **Gross supply margin** | **£6,408,780** | **45.8%** |
| Policy + Network costs | -£4,852,221 | 34.7% |
| Capital cost | -£51,273 | 0.4% |
| **Net supply margin** | **£1,505,286** | **10.7%** |

> *The ledger's `net_margin_gbp` (£6,404,134) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,005,856 | 47.5% | 11.9% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 3.5% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £51,769 | 59.1% | 3.8% | CMA 3-8% | ✓ |
| resi/elec | £87,950 | 57.2% | 6.7% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £25,260 | 31.0% | 2.8% | Ofgem CMA 2-4% | ✓ |

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
| Customer bills (all-in) | £22,585,671.01 |
|   Less: VAT remitted to HMRC | (£3,744,564.13) |
| = Revenue (ex-VAT) | £18,841,106.87 |
| Less: non-commodity pass-through | (£4,791,065.52) |
| Wholesale cost (settlement events) | (£7,594,635.13) |
| Gross margin | £6,455,406.22 |
| Capital charges | (£51,272.56) |
| Net margin | £6,404,133.66 |

_Cash reconciliation: of £22,585,671.01 billed, bad debt of £451,915.82 was written off, leaving £22,133,868.78 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £9,696,895.57._

| Acquisition spend | (£750.00) |
| Fixed overhead | (£5,700.00) |
| Cost to serve | (£23,234.94) |
| Operating net margin | £6,374,448.72 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £16,206.51 | £3,594.97 | £4,363.77 | £8,247.77 | £262.70 | £1,474.07 | £6,687.37 (41.3%) |
| 2017 | £347,687.40 | £111,055.45 | £112,416.49 | £124,215.46 | £7,034.86 | £8,979.73 | £113,962.27 (32.8%) |
| 2018 | £600,281.26 | £172,888.03 | £164,071.67 | £263,321.56 | £13,404.35 | £15,848.89 | £245,832.29 (41.0%) |
| 2019 | £1,642,338.05 | £496,185.24 | £443,205.99 | £702,946.83 | £34,976.95 | £38,421.10 | £662,199.32 (40.3%) |
| 2020 | £1,858,681.92 | £431,597.51 | £629,411.89 | £797,672.52 | £43,690.00 | £48,037.46 | £747,669.34 (40.2%) |
| 2021 | £2,416,543.72 | £971,916.20 | £680,773.88 | £763,853.65 | £53,603.16 | £57,317.14 | £700,904.13 (29.0%) |
| 2022 | £4,239,425.11 | £2,387,110.07 | £799,720.68 | £1,052,594.36 | £96,328.44 | £99,932.62 | £939,401.88 (22.2%) |
| 2023 | £3,430,212.55 | £1,638,231.56 | £875,288.61 | £916,692.38 | £86,195.60 | £89,799.51 | £817,131.18 (23.8%) |
| 2024 | £3,016,001.74 | £931,171.08 | £811,332.71 | £1,273,497.95 | £73,305.88 | £77,127.79 | £1,186,705.75 (39.3%) |
| 2025 | £1,285,112.25 | £452,201.01 | £270,479.84 | £562,431.39 | £43,113.87 | £44,662.46 | £512,107.02 (39.8%) |
| **Total** | **£18,852,490.51** | | | | | | **£5,932,600.55 (31.5%)** |

**Best year:** 2024 — net £1,186,705.75 (39.3% margin)
**Worst year:** 2016 — net £6,687.37 (41.3% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,399,123.18 |
| Trade Receivables | £113.59 |
| **Total Assets** | **£8,399,236.77** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,932,600.55 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £16,206.51 | +10.5% | £6,592.99 | £6,687.37 | +1.4% | GREEN |
| 2017 | £16,138.86 | £347,687.40 | +2054.3% | £7,252.29 | £113,962.27 | +1471.4% | RED |
| 2018 | £386,623.75 | £600,281.26 | +55.3% | £128,424.00 | £245,832.29 | +91.4% | RED |
| 2019 | £675,851.95 | £1,642,338.05 | +143.0% | £281,335.50 | £662,199.32 | +135.4% | RED |
| 2020 | £1,816,630.04 | £1,858,681.92 | +2.3% | £736,963.94 | £747,669.34 | +1.5% | GREEN |
| 2021 | £2,028,952.42 | £2,416,543.72 | +19.1% | £833,649.22 | £700,904.13 | -15.9% | RED |
| 2022 | £2,607,611.88 | £4,239,425.11 | +62.6% | £790,935.58 | £939,401.88 | +18.8% | RED |
| 2023 | £4,508,414.67 | £3,430,212.55 | -23.9% | £1,029,561.00 | £817,131.18 | -20.6% | RED |
| 2024 | £3,512,844.39 | £3,016,001.74 | -14.1% | £893,105.75 | £1,186,705.75 | +32.9% | RED |
| 2025 | £3,145,356.42 | £1,285,112.25 | -59.1% | £1,315,150.33 | £512,107.02 | -61.1% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,397,683.66

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

- Net margin: £31,395.55 (gross £123,220.34, capital £1,273.46)
  - Electricity: gross £121,790.76, capital £1,258.61, net £30,879.00
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
  - By billing account: C1 £5,231.67, C2 £10,444.03, C3 £8,807.25, C4 £8,105.00, C5 £12,043.37, C6 £23,950.54, C7 £8,859.84, C8 £13,645.68, C9 £11,194.96
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

- Actual (hedged) net margin: £30,075.25 vs. naked (unhedged) net margin: £112,480.03
- hedging cost £82,404.77 vs. a fully unhedged book (commodity-only: actual net £30,075.25 vs. naked net £112,480.03)
  - C1: actual £22.97 vs. naked £341.73 -- hedging cost £318.77
  - C1g: actual £131.41 vs. naked £272.27 -- hedging cost £140.86
  - C2: actual £103.00 vs. naked £442.11 -- hedging cost £339.11
  - C2g: actual £207.48 vs. naked £448.25 -- hedging cost £240.78
  - C3: actual £110.96 vs. naked £513.38 -- hedging cost £402.41
  - C3g: actual £30.62 vs. naked £394.35 -- hedging cost £363.73
  - C4: actual £33.30 vs. naked £272.21 -- hedging cost £238.91
  - C4g: actual £44.94 vs. naked £544.66 -- hedging cost £499.72
  - C5: actual £-207.02 vs. naked £1,069.26 -- hedging cost £1,276.28
  - C6: actual £104.65 vs. naked £1,675.83 -- hedging cost £1,571.18
  - C7: actual £-51.08 vs. naked £820.82 -- hedging cost £871.90
  - C8: actual £254.62 vs. naked £990.30 -- hedging cost £735.68
  - C9: actual £242.03 vs. naked £951.76 -- hedging cost £709.73
  - C_IC1: actual £29,047.38 vs. naked £103,743.08 -- hedging cost £74,695.71

**Year narrative:** 2017 produced a net gain of £31,395.55 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 68 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £101,782.65 (gross £262,574.53, capital £1,640.39)
  - Electricity: gross £261,210.93, capital £1,619.32, net £101,344.92
  - Gas: gross £1,363.60, capital £21.07, net £437.73
- Treasury at year end: £2,487,648.38
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.91 (avg 0.91)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2018-12-31 period 48, net margin £-234.97

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £274,083.32
  - By billing account: C1 £4,931.63, C2 £7,734.85, C3 £7,536.34, C4 £6,553.42, C5 £12,087.35, C6 £18,135.67, C7 £7,810.17, C8 £10,311.52, C9 £9,920.61, C_IC1 £2,655,811.60
- Bill shock events (>=20%): 83 -- C1g 2018-04-30 (40%); C1g 2018-05-31 (33%); C1g 2018-06-30 (35%); C1g 2018-09-30 (34%); C1g 2018-10-31 (56%); C1g 2018-11-30 (31%); C5 2018-01-31 (35%); C5 2018-02-28 (29%); C5 2018-04-30 (24%); C5 2018-06-30 (39%); C5 2018-07-31 (77%); C5 2018-08-31 (76%); C5 2018-09-30 (74%); C5 2018-10-31 (51%); C7 2018-04-30 (39%); C7 2018-05-31 (40%); C7 2018-06-30 (88%); C7 2018-07-31 (313%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C2 2018-12-31 (23%); C2g 2018-04-30 (29%); C2g 2018-05-31 (37%); C2g 2018-06-30 (38%); C2g 2018-07-31 (73%); C2g 2018-08-31 (92%); C2g 2018-09-30 (92%); C2g 2018-10-31 (51%); C2g 2018-11-30 (21%); C6 2018-01-31 (37%); C6 2018-02-28 (38%); C6 2018-03-31 (36%); C6 2018-04-30 (31%); C6 2018-07-31 (51%); C6 2018-08-31 (56%); C6 2018-09-30 (46%); C6 2018-10-31 (179%); C6 2018-12-31 (29%); C8 2018-05-31 (101%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (56%); C8 2018-11-30 (30%); C3 2018-01-31 (26%); C3 2018-02-28 (26%); C3 2018-03-31 (121%); C3 2018-12-31 (21%); C3g 2018-01-31 (66%); C3g 2018-02-28 (68%); C3g 2018-03-31 (66%); C3g 2018-04-30 (68%); C3g 2018-05-31 (54%); C3g 2018-06-30 (30%); C3g 2018-08-31 (1414%); C3g 2018-09-30 (41%); C3g 2018-11-30 (42%); C3g 2018-12-31 (49%); C9 2018-01-31 (53%); C9 2018-04-30 (32%); C9 2018-05-31 (30%); C9 2018-06-30 (134%); C9 2018-07-31 (23%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-04-30 (32%); C4 2018-09-30 (29%); C4 2018-10-31 (50%); C4 2018-11-30 (33%); C4g 2018-03-31 (21%); C4g 2018-04-30 (37%); C4g 2018-05-31 (36%); C4g 2018-06-30 (151%); C4g 2018-08-31 (23%); C4g 2018-09-30 (45%); C4g 2018-10-31 (94%); C4g 2018-11-30 (26%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C2 23%, C3 23%, C6 23%, C7 20%, C8 23%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £92.70-£224.86/MWh, net margin £37.15
- C1g (gas): tariff £33.49-£36.09/MWh, net margin £142.44
- C2 (electricity): tariff £98.66-£215.90/MWh, net margin £93.33
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £189.04
- C3 (electricity): tariff £120.31-£126.89/MWh, net margin £107.88
- C3g (gas): tariff £23.11-£28.84/MWh, net margin £41.12
- C4 (electricity): tariff £86.47-£224.05/MWh, net margin £66.79
- C4g (gas): tariff £26.10-£33.65/MWh, net margin £65.13
- C5 (electricity): tariff £119.60-£153.54/MWh, net margin £-440.83 -- **net-negative**
- C6 (electricity): tariff £126.27-£142.20/MWh, net margin £-12.18 -- **net-negative**
- C7 (electricity): tariff £96.43-£221.23/MWh, net margin £-15.08 -- **net-negative**
- C8 (electricity): tariff £99.63-£200.72/MWh, net margin £161.39
- C9 (electricity): tariff £94.69-£198.37/MWh, net margin £239.23
- C_IC1 (electricity): tariff £-82.12-£228.57/MWh, net margin £107,489.49
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,382.25 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.755, average bill shock 36.5%, bad debt provision £238.97, avg complaint probability 6.4%
- Solvency signal: £226,150/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £109,539.33 vs. naked (unhedged) net margin: £246,624.14
- hedging cost £137,084.81 vs. a fully unhedged book (commodity-only: actual net £109,539.33 vs. naked net £246,624.14)
  - C1: actual £105.97 vs. naked £575.46 -- hedging cost £469.49
  - C1g: actual £144.83 vs. naked £421.13 -- hedging cost £276.30
  - C2: actual £62.57 vs. naked £503.97 -- hedging cost £441.40
  - C2g: actual £150.65 vs. naked £399.99 -- hedging cost £249.34
  - C3: actual £26.61 vs. naked £557.84 -- hedging cost £531.23
  - C3g: actual £39.76 vs. naked £482.40 -- hedging cost £442.64
  - C4: actual £94.19 vs. naked £459.22 -- hedging cost £365.03
  - C4g: actual £69.51 vs. naked £871.98 -- hedging cost £802.47
  - C5: actual £124.53 vs. naked £1,984.67 -- hedging cost £1,860.14
  - C6: actual £-140.83 vs. naked £1,834.32 -- hedging cost £1,975.15
  - C7: actual £71.45 vs. naked £1,347.45 -- hedging cost £1,276.00
  - C8: actual £24.60 vs. naked £936.91 -- hedging cost £912.31
  - C9: actual £143.69 vs. naked £1,046.01 -- hedging cost £902.32
  - C_IC1: actual £115,505.78 vs. naked £201,756.48 -- hedging cost £86,250.70
  - C_IC2: actual £-6,883.98 vs. naked £33,446.32 -- hedging cost £40,330.30

**Year narrative:** 2018 produced a net gain of £101,782.65 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 83 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £234,032.72 (gross £702,104.98, capital £2,326.40)
  - Electricity: gross £626,048.66, capital £2,304.95, net £223,540.59
  - Gas: gross £76,056.32, capital £21.46, net £10,492.12
- Treasury at year end: £2,611,861.23
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
- Average CLV (Point-in-Time, year-end 2019): £314,646.32
  - By billing account: C1 £4,477.66, C2 £6,355.17, C3 £7,157.50, C4 £6,398.64, C5 £10,449.89, C6 £20,925.93, C7 £7,993.90, C8 £9,755.59, C9 £9,238.92, C_IC1 £2,149,050.75, C_IC2 £1,229,305.58
- Bill shock events (>=20%): 76 -- C1 2019-04-30 (22%); C1g 2019-01-31 (40%); C1g 2019-02-28 (27%); C1g 2019-05-31 (26%); C1g 2019-06-30 (40%); C1g 2019-10-31 (91%); C1g 2019-11-30 (50%); C5 2019-02-28 (32%); C5 2019-04-30 (78%); C5 2019-06-30 (25%); C5 2019-07-31 (70%); C5 2019-08-31 (77%); C5 2019-09-30 (83%); C5 2019-10-31 (66%); C7 2019-01-31 (46%); C7 2019-02-28 (26%); C7 2019-05-31 (24%); C7 2019-06-30 (35%); C7 2019-10-31 (72%); C7 2019-11-30 (46%); C2g 2019-01-31 (27%); C2g 2019-02-28 (27%); C2g 2019-04-30 (37%); C2g 2019-06-30 (35%); C2g 2019-07-31 (30%); C2g 2019-09-30 (40%); C2g 2019-10-31 (76%); C2g 2019-11-30 (31%); C6 2019-01-31 (35%); C6 2019-02-28 (77%); C6 2019-04-30 (21%); C6 2019-07-31 (43%); C6 2019-08-31 (62%); C6 2019-09-30 (64%); C6 2019-10-31 (36%); C6 2019-12-31 (26%); C8 2019-01-31 (28%); C8 2019-02-28 (28%); C8 2019-04-30 (22%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-10-31 (117%); C8 2019-11-30 (38%); C3 2019-01-31 (23%); C3 2019-02-28 (24%); C3 2019-04-30 (23%); C3 2019-09-30 (152%); C3g 2019-01-31 (145%); C3g 2019-02-28 (41%); C3g 2019-04-30 (28%); C3g 2019-07-31 (37%); C3g 2019-08-31 (129%); C3g 2019-09-30 (106%); C3g 2019-10-31 (56%); C3g 2019-11-30 (44%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (68%); C9 2019-07-31 (60%); C9 2019-08-31 (139%); C9 2019-09-30 (53%); C9 2019-11-30 (87%); C4 2019-04-30 (35%); C4 2019-09-30 (33%); C4 2019-12-31 (45%); C4g 2019-01-31 (31%); C4g 2019-02-28 (25%); C4g 2019-05-31 (50%); C4g 2019-06-30 (35%); C4g 2019-07-31 (40%); C4g 2019-09-30 (36%); C4g 2019-10-31 (37%); C4g 2019-11-30 (38%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C1 29%, C4 35%, C5 35%, C7 29%, C9 23%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £99.42-£224.86/MWh, net margin £122.18
- C1g (gas): tariff £25.36-£36.09/MWh, net margin £156.88
- C2 (electricity): tariff £113.09-£227.85/MWh, net margin £145.70
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £134.46
- C3 (electricity): tariff £120.68-£126.89/MWh, net margin £-62.48 -- **net-negative**
- C3g (gas): tariff £23.03-£28.84/MWh, net margin £98.62
- C4 (electricity): tariff £100.05-£224.05/MWh, net margin £106.14
- C4g (gas): tariff £19.49-£33.65/MWh, net margin £102.24
- C5 (electricity): tariff £126.54-£153.54/MWh, net margin £153.40
- C6 (electricity): tariff £142.20-£148.71/MWh, net margin £129.38
- C7 (electricity): tariff £99.50-£221.23/MWh, net margin £111.58
- C8 (electricity): tariff £105.14-£211.40/MWh, net margin £192.94
- C9 (electricity): tariff £99.30-£198.37/MWh, net margin £185.70
- C_IC1 (electricity): tariff £0.00-£263.70/MWh, net margin £139,393.49
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £79,281.83
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £3,780.73
- C_IC3g (gas): tariff £27.53/MWh, net margin £9,999.92

**Portfolio Health**

- Capital cost ratio: 0.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.793, average bill shock 24.1%, bad debt provision £107.39, avg complaint probability 5.7%
- Solvency signal: £217,655/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £252,597.86 vs. naked (unhedged) net margin: £836,879.32
- hedging cost £584,281.46 vs. a fully unhedged book (commodity-only: actual net £252,597.86 vs. naked net £836,879.32)
  - C1: actual £87.94 vs. naked £503.87 -- hedging cost £415.93
  - C1g: actual £137.47 vs. naked £302.77 -- hedging cost £165.30
  - C2: actual £157.70 vs. naked £669.23 -- hedging cost £511.53
  - C2g: actual £87.69 vs. naked £403.54 -- hedging cost £315.85
  - C3: actual £-2.43 vs. naked £668.43 -- hedging cost £670.85
  - C3g: actual £136.36 vs. naked £506.33 -- hedging cost £369.97
  - C4: actual £98.00 vs. naked £443.86 -- hedging cost £345.85
  - C4g: actual £102.10 vs. naked £574.69 -- hedging cost £472.59
  - C5: actual £-19.80 vs. naked £1,597.98 -- hedging cost £1,617.79
  - C6: actual £233.29 vs. naked £2,599.53 -- hedging cost £2,366.24
  - C7: actual £37.45 vs. naked £1,143.65 -- hedging cost £1,106.21
  - C8: actual £240.89 vs. naked £1,370.83 -- hedging cost £1,129.94
  - C9: actual £167.44 vs. naked £1,266.65 -- hedging cost £1,099.21
  - C_IC1: actual £154,892.48 vs. naked £297,973.82 -- hedging cost £143,081.33
  - C_IC2: actual £85,558.69 vs. naked £161,523.27 -- hedging cost £75,964.58
  - C_IC3: actual £1,355.95 vs. naked £289,938.26 -- hedging cost £288,582.30
  - C_IC3g: actual £9,326.63 vs. naked £75,392.62 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £234,032.72 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 76 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £128,360.24 (gross £791,825.09, capital £1,965.72)
  - Electricity: gross £714,642.05, capital £1,955.20, net £117,870.50
  - Gas: gross £77,183.04, capital £10.52, net £10,489.74
- Treasury at year end: £2,924,005.63
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
- Average CLV (Point-in-Time, year-end 2020): £412,469.78
  - By billing account: C1 £4,055.35, C2 £7,798.15, C3 £6,096.14, C4 £5,051.28, C5 £8,624.62, C6 £15,157.79, C7 £7,269.59, C8 £8,338.18, C9 £9,096.47, C_IC1 £1,142,260.54, C_IC2 £742,826.08, C_IC3 £2,125,002.42, C_IC4 £1,280,530.60
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
- C6 (electricity): tariff £143.89-£148.71/MWh, net margin £401.71
- C7 (electricity): tariff £99.50-£203.25/MWh, net margin £87.89
- C8 (electricity): tariff £110.22-£211.40/MWh, net margin £375.88
- C9 (electricity): tariff £85.93-£189.57/MWh, net margin £159.37
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £53,259.99
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £44,258.51
- C_IC3 (electricity): tariff £37.49-£79.92/MWh, net margin £13,094.04
- C_IC3g (gas): tariff £15.44-£20.11/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £5,999.58

**Portfolio Health**

- Capital cost ratio: 0.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.794, average bill shock 23.9%, bad debt provision £194.98, avg complaint probability 5.5%
- Solvency signal: £224,924/customer (13 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2020 produced a net gain of £128,360.24 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 74 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £78,288.16 (gross £765,625.49, capital £5,632.38)
  - Electricity: gross £682,827.42, capital £5,617.56, net £68,417.78
  - Gas: gross £82,798.06, capital £14.82, net £9,870.38
- Treasury at year end: £2,955,999.74
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.87 (avg 0.87), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2021-12-31 period 48, net margin £-299.15

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £410,974.60
  - By billing account: C1 £4,005.70, C2 £7,172.35, C3 £5,224.53, C4 £4,518.54, C5 £9,669.04, C6 £14,814.77, C7 £6,744.29, C8 £8,504.21, C9 £7,859.11, C_IC1 £1,298,591.46, C_IC2 £575,995.83, C_IC3 £2,034,411.43, C_IC4 £1,365,158.58
- Bill shock events (>=20%): 58 -- C1 2021-05-31 (26%); C1 2021-07-31 (22%); C1g 2021-05-31 (42%); C1g 2021-06-30 (32%); C1g 2021-07-31 (178%); C1g 2021-08-31 (114%); C1g 2021-09-30 (107%); C1g 2021-10-31 (71%); C1g 2021-11-30 (64%); C1g 2021-12-29 (35%); C7 2021-05-31 (30%); C7 2021-06-30 (47%); C7 2021-10-31 (55%); C7 2021-11-30 (65%); C2 2021-11-30 (21%); C2g 2021-02-28 (20%); C2g 2021-04-30 (50%); C2g 2021-05-31 (37%); C2g 2021-06-30 (58%); C2g 2021-10-31 (67%); C2g 2021-11-30 (66%); C6 2021-01-31 (32%); C6 2021-02-28 (37%); C6 2021-03-31 (24%); C6 2021-07-31 (58%); C6 2021-08-31 (62%); C6 2021-09-30 (86%); C6 2021-10-31 (28%); C6 2021-12-31 (45%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (25%); C8 2021-10-31 (69%); C8 2021-11-30 (84%); C9 2021-02-28 (22%); C9 2021-05-31 (25%); C9 2021-06-30 (51%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-11-30 (98%); C9 2021-12-31 (24%); C4 2021-04-30 (35%); C4 2021-09-30 (30%); C4 2021-10-31 (52%); C4 2021-11-30 (38%); C4g 2021-05-31 (24%); C4g 2021-06-30 (57%); C4g 2021-10-31 (132%); C4g 2021-11-30 (61%); C_IC1 2021-05-31 (41%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (77%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (21%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (27%)
- Churn risk (accounts renewing in 2021): 6 at risk (≥20% churn prob): C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1 (electricity): tariff £104.77-£200.01/MWh, net margin £24.24
- C1g (gas): tariff £25.00/MWh, net margin £40.05
- C2 (electricity): tariff £113.06-£274.50/MWh, net margin £198.84
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £126.10
- C4 (electricity): tariff £96.82-£274.50/MWh, net margin £-35.60 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-295.69 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.19/MWh, net margin £227.79
- C7 (electricity): tariff £106.46-£274.50/MWh, net margin £-120.85 -- **net-negative**
- C8 (electricity): tariff £110.22-£274.50/MWh, net margin £431.50
- C9 (electricity): tariff £85.93-£267.37/MWh, net margin £78.04
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £30,539.02
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £58,235.63
- C_IC3 (electricity): tariff £41.86-£392.84/MWh, net margin £-27,099.85 -- **net-negative**
- C_IC3g (gas): tariff £20.11-£123.81/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £5,939.02

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.809, average bill shock 20.8%, bad debt provision £365.61, avg complaint probability 5.2%
- Solvency signal: £268,727/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £200,852.70 vs. naked (unhedged) net margin: £466,561.13
- hedging cost £265,708.44 vs. a fully unhedged book (commodity-only: actual net £200,852.70 vs. naked net £466,561.13)
  - C2: actual £138.10 vs. naked £150.31 -- hedging cost £12.22
  - C2g: actual £25.95 vs. naked £-190.70 -- hedging added £216.66
  - C4: actual £-231.16 vs. naked £-156.26 -- hedging cost £74.90
  - C4g: actual £-874.54 vs. naked £-1,344.38 -- hedging added £469.85
  - C6: actual £514.24 vs. naked £269.68 -- hedging added £244.56
  - C7: actual £-1,925.74 vs. naked £-869.22 -- hedging cost £1,056.52
  - C8: actual £21.86 vs. naked £107.75 -- hedging cost £85.89
  - C9: actual £-27.50 vs. naked £-160.17 -- hedging added £132.68
  - C_IC1: actual £30,816.17 vs. naked £-58,138.69 -- hedging added £88,954.86
  - C_IC2: actual £65,918.97 vs. naked £24,606.70 -- hedging added £41,312.26
  - C_IC3: actual £104,236.73 vs. naked £238,782.50 -- hedging cost £134,545.76
  - C_IC3g: actual £4,142.87 vs. naked £85,199.40 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £178,304.23 -- hedging cost £180,207.49

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £78,288.16 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 58 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £339,911.67 (gross £1,050,926.37, capital £13,259.86)
  - Electricity: gross £960,538.31, capital £13,212.55, net £331,170.84
  - Gas: gross £90,388.06, capital £47.31, net £8,740.82
- Treasury at year end: £3,169,687.86
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.96 (avg 0.96), C2g 0.85 (avg 0.85), C4 0.96 (avg 0.96), C4g 0.88 (avg 0.88), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,041,764.76, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,591.24 / stressed £20,590.79) ratio 2.70
  - 2022-05-29: treasury £3,041,917.98, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,703.06 / stressed £20,620.75) ratio 2.70
  - 2022-06-28: treasury £3,041,913.72, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,703.06 / stressed £20,620.75) ratio 2.70
  - 2022-07-28: treasury £3,041,714.67, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,764.27 / stressed £20,632.88) ratio 2.70
  - 2022-08-27: treasury £3,041,702.59, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,764.27 / stressed £20,632.88) ratio 2.70
  - 2022-09-26: treasury £3,041,685.00, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,764.27 / stressed £20,632.88) ratio 2.70
  - 2022-10-26: treasury £3,039,354.05, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,831.40 / stressed £20,645.76) ratio 2.70
  - 2022-11-25: treasury £3,039,195.51, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,831.40 / stressed £20,645.76) ratio 2.70
  - 2022-12-25: treasury £3,038,915.35, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,831.40 / stressed £20,645.76) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C6 on 2022-12-31 period 48, net margin £-990.56

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2022): £369,522.02
  - By billing account: C1 £4,107.39, C2 £5,720.53, C3 £4,617.07, C4 £2,560.35, C5 £8,488.43, C6 £14,118.25, C7 £4,196.65, C8 £7,048.64, C9 £7,265.51, C_IC1 £1,036,824.70, C_IC2 £660,978.74, C_IC3 £1,955,975.60, C_IC4 £1,091,884.36
- Bill shock events (>=20%): 65 -- C7 2022-05-31 (61%); C7 2022-06-30 (26%); C7 2022-09-30 (32%); C7 2022-11-30 (61%); C7 2022-12-31 (55%); C2g 2022-02-28 (22%); C2g 2022-04-30 (69%); C2g 2022-05-31 (38%); C2g 2022-06-30 (31%); C2g 2022-07-31 (20%); C2g 2022-09-30 (65%); C2g 2022-11-30 (22%); C2g 2022-12-31 (113%); C6 2022-01-31 (47%); C6 2022-02-28 (117%); C6 2022-04-30 (54%); C6 2022-06-30 (39%); C6 2022-07-31 (69%); C6 2022-08-31 (85%); C6 2022-09-30 (88%); C6 2022-10-31 (50%); C6 2022-11-30 (37%); C8 2022-05-31 (39%); C8 2022-06-30 (34%); C8 2022-07-31 (21%); C8 2022-09-30 (81%); C8 2022-12-31 (110%); C9 2022-04-30 (21%); C9 2022-05-31 (29%); C9 2022-06-30 (37%); C9 2022-07-31 (94%); C9 2022-09-30 (48%); C9 2022-10-31 (30%); C9 2022-11-30 (44%); C9 2022-12-31 (52%); C4 2022-05-31 (120%); C4 2022-06-30 (59%); C4 2022-07-31 (84%); C4 2022-11-30 (36%); C4 2022-12-31 (100%); C4g 2022-01-31 (26%); C4g 2022-02-28 (24%); C4g 2022-04-30 (24%); C4g 2022-05-31 (36%); C4g 2022-06-30 (30%); C4g 2022-07-31 (25%); C4g 2022-09-30 (75%); C4g 2022-10-31 (43%); C4g 2022-11-30 (42%); C4g 2022-12-31 (147%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (110%); C_IC3g 2022-01-31 (25%); C_IC3g 2022-03-31 (33%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (50%); C_IC3g 2022-08-31 (39%); C_IC3g 2022-10-31 (50%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%)
- Churn risk (accounts renewing in 2022): 10 at risk (≥20% churn prob): C2 38%, C4 38%, C6 35%, C7 29%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C2 (electricity): tariff £143.79-£457.50/MWh, net margin £2.28
- C2g (gas): tariff £35.00-£95.00/MWh, net margin £-102.36 -- **net-negative**
- C4 (electricity): tariff £143.79-£457.50/MWh, net margin £-201.31 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,156.74 -- **net-negative**
- C6 (electricity): tariff £197.19-£413.77/MWh, net margin £-66.08 -- **net-negative**
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,632.87 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £73.71
- C9 (electricity): tariff £140.05-£389.85/MWh, net margin £124.62
- C_IC1 (electricity): tariff £-83.39-£461.36/MWh, net margin £136,190.42
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £75,291.68
- C_IC3 (electricity): tariff £137.99-£392.84/MWh, net margin £115,469.02
- C_IC3g (gas): tariff £116.42-£123.81/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £5,919.38

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 2 -- £3,474,126.68 -> £3,057,487.53 (12.0%); £3,474,308.20 -> £3,056,912.69 (12.0%)
- Bills issued: 156, average clarity 0.778, average bill shock 26.3%, bad debt provision £1,233.55, avg complaint probability 6.1%
- Solvency signal: £316,969/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £138,305.23 vs. naked (unhedged) net margin: £1,159,439.74
- hedging cost £1,021,134.51 vs. a fully unhedged book (commodity-only: actual net £138,305.23 vs. naked net £1,159,439.74)
  - C2: actual £-191.17 vs. naked £524.01 -- hedging cost £715.18
  - C2g: actual £-319.85 vs. naked £262.02 -- hedging cost £581.87
  - C4: actual £-292.88 vs. naked £597.69 -- hedging cost £890.57
  - C4g: actual £-2,028.81 vs. naked £1,336.80 -- hedging cost £3,365.60
  - C6: actual £1,282.90 vs. naked £4,155.34 -- hedging cost £2,872.44
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-348.38 vs. naked £1,102.92 -- hedging cost £1,451.29
  - C9: actual £-47.01 vs. naked £1,014.75 -- hedging cost £1,061.77
  - C_IC1: actual £210,454.89 vs. naked £248,695.32 -- hedging cost £38,240.43
  - C_IC2: actual £85,603.78 vs. naked £124,884.48 -- hedging cost £39,280.70
  - C_IC3: actual £-167,348.92 vs. naked £446,226.79 -- hedging cost £613,575.71
  - C_IC3g: actual £8,513.79 vs. naked £123,301.26 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £205,056.67 -- hedging cost £201,583.86

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £339,911.67 across 13 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 65 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £100,347.41 (gross £909,255.84, capital £9,761.69)
  - Electricity: gross £787,959.15, capital £9,686.27, net £91,320.50
  - Gas: gross £121,296.69, capital £75.41, net £9,026.91
- Treasury at year end: £3,342,739.02
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.95 (avg 0.95), C2g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,145,204.62, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,036.79 / stressed £44,239.58) ratio 2.76
  - 2023-02-23: treasury £3,145,187.70, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,036.79 / stressed £44,239.58) ratio 2.76
  - 2023-03-25: treasury £3,145,170.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,036.79 / stressed £44,239.58) ratio 2.76
  - 2023-04-24: treasury £3,223,481.03, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,843.33 / stressed £49,107.89) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C6 on 2023-12-31 period 48, net margin £-865.21

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £306,633.93
  - By billing account: C1 £2,879.15, C2 £4,712.53, C3 £4,190.93, C4 £1,703.13, C5 £7,086.15, C6 £15,274.45, C7 £4,614.01, C8 £6,353.34, C9 £6,179.50, C_IC1 £970,715.37, C_IC2 £597,173.15, C_IC3 £1,380,932.43, C_IC4 £984,426.99
- Bill shock events (>=20%): 55 -- C7 2023-01-31 (40%); C7 2023-06-30 (100%); C7 2023-07-31 (86%); C7 2023-08-31 (96%); C7 2023-10-31 (55%); C7 2023-11-30 (70%); C7 2023-12-31 (33%); C2 2023-04-30 (28%); C2g 2023-01-31 (42%); C2g 2023-04-30 (35%); C2g 2023-05-31 (40%); C2g 2023-06-30 (40%); C2g 2023-08-31 (21%); C2g 2023-10-31 (96%); C2g 2023-11-30 (60%); C6 2023-01-31 (28%); C6 2023-02-28 (24%); C6 2023-04-30 (132%); C6 2023-06-30 (45%); C6 2023-07-31 (89%); C6 2023-08-31 (90%); C6 2023-09-30 (88%); C6 2023-10-31 (83%); C6 2023-11-30 (275%); C8 2023-04-30 (30%); C8 2023-05-31 (40%); C8 2023-06-30 (43%); C8 2023-11-30 (50%); C8 2023-12-31 (104%); C9 2023-02-28 (21%); C9 2023-03-31 (24%); C9 2023-04-30 (30%); C9 2023-05-31 (33%); C9 2023-06-30 (45%); C9 2023-09-30 (21%); C9 2023-10-31 (74%); C9 2023-11-30 (53%); C4 2023-02-28 (26%); C4 2023-05-31 (91%); C4 2023-06-30 (50%); C4 2023-07-31 (74%); C4 2023-09-30 (29%); C4 2023-11-30 (32%); C4g 2023-05-31 (37%); C4g 2023-06-30 (46%); C4g 2023-10-31 (47%); C4g 2023-11-30 (67%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (52%); C_IC1 2023-07-31 (59%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (52%); C_IC2 2023-06-30 (100%); C_IC3g 2023-01-31 (36%); C_IC4 2023-01-31 (35%)
- Churn risk (accounts renewing in 2023): 10 at risk (≥20% churn prob): C2 41%, C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C2 (electricity): tariff £208.21-£457.50/MWh, net margin £88.59
- C2g (gas): tariff £70.00-£95.00/MWh, net margin £136.46
- C4 (electricity): tariff £198.44-£457.50/MWh, net margin £-23.77 -- **net-negative**
- C4g (gas): tariff £65.13-£95.00/MWh, net margin £-1,109.47 -- **net-negative**
- C6 (electricity): tariff £340.22-£413.77/MWh, net margin £558.92
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-144.77 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £159.02
- C9 (electricity): tariff £192.66-£389.85/MWh, net margin £398.47
- C_IC1 (electricity): tariff £-60.00-£461.36/MWh, net margin £161,155.64
- C_IC2 (electricity): tariff £-186.24-£474.31/MWh, net margin £84,845.27
- C_IC3 (electricity): tariff £100.33-£263.43/MWh, net margin £-161,644.73 -- **net-negative**
- C_IC3g (gas): tariff £55.98-£116.42/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £5,927.85

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): 47 -- £3,749,413.65 -> £3,342,664.42 (10.8%); £3,749,413.80 -> £3,342,664.42 (10.8%); £3,749,413.95 -> £3,342,664.42 (10.8%); £3,749,414.10 -> £3,342,664.42 (10.8%); £3,749,414.26 -> £3,342,664.42 (10.8%); £3,749,414.41 -> £3,342,664.41 (10.8%); £3,749,414.57 -> £3,342,664.41 (10.8%); £3,749,414.72 -> £3,342,664.41 (10.8%); £3,749,414.88 -> £3,342,664.41 (10.8%); £3,749,415.03 -> £3,342,664.41 (10.8%); £3,749,415.19 -> £3,342,664.41 (10.8%); £3,749,415.35 -> £3,342,664.41 (10.8%); £3,749,415.50 -> £3,342,664.41 (10.8%); £3,749,415.67 -> £3,342,664.40 (10.8%); £3,749,415.86 -> £3,342,664.40 (10.8%); £3,749,416.07 -> £3,342,664.39 (10.8%); £3,749,416.29 -> £3,342,664.38 (10.8%); £3,749,416.53 -> £3,342,664.37 (10.8%); £3,749,416.80 -> £3,342,664.36 (10.8%); £3,749,417.05 -> £3,342,664.34 (10.8%); £3,749,417.32 -> £3,342,664.33 (10.8%); £3,749,417.57 -> £3,342,664.32 (10.8%); £3,749,417.83 -> £3,342,664.31 (10.8%); £3,749,418.09 -> £3,342,664.29 (10.8%); £3,749,418.35 -> £3,342,664.28 (10.8%); £3,749,418.62 -> £3,342,664.27 (10.8%); £3,749,418.89 -> £3,342,664.25 (10.8%); £3,749,419.15 -> £3,342,664.24 (10.8%); £3,749,419.40 -> £3,342,664.24 (10.8%); £3,749,419.66 -> £3,342,664.23 (10.8%); £3,749,419.92 -> £3,342,664.22 (10.8%); £3,749,420.17 -> £3,342,664.21 (10.8%); £3,749,420.43 -> £3,342,664.20 (10.8%); £3,749,420.69 -> £3,342,664.17 (10.8%); £3,749,420.94 -> £3,342,664.15 (10.8%); £3,749,421.20 -> £3,342,664.13 (10.8%); £3,749,421.46 -> £3,342,664.11 (10.8%); £3,749,421.73 -> £3,342,664.07 (10.8%); £3,749,421.99 -> £3,342,664.04 (10.8%); £3,749,422.25 -> £3,342,664.01 (10.8%); £3,749,422.51 -> £3,342,663.99 (10.8%); £3,749,422.77 -> £3,342,663.96 (10.8%); £3,749,423.03 -> £3,342,663.93 (10.8%); £3,749,423.29 -> £3,342,663.92 (10.8%); £3,749,423.55 -> £3,342,663.91 (10.8%); £3,749,423.80 -> £3,342,663.90 (10.8%); £3,749,424.01 -> £3,342,739.02 (10.8%)
- Bills issued: 156, average clarity 0.782, average bill shock 25.0%, bad debt provision £1,038.74, avg complaint probability 5.8%
- Solvency signal: £334,274/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £399,916.52 vs. naked (unhedged) net margin: £1,238,307.33
- hedging cost £838,390.81 vs. a fully unhedged book (commodity-only: actual net £399,916.52 vs. naked net £1,238,307.33)
  - C2: actual £106.23 vs. naked £797.97 -- hedging cost £691.74
  - C2g: actual £178.43 vs. naked £669.84 -- hedging cost £491.42
  - C4: actual £234.43 vs. naked £704.88 -- hedging cost £470.44
  - C4g: actual £506.57 vs. naked £1,025.12 -- hedging cost £518.54
  - C6: actual £1,568.97 vs. naked £5,239.24 -- hedging cost £3,670.26
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £212.54 vs. naked £1,972.23 -- hedging cost £1,759.69
  - C9: actual £627.33 vs. naked £2,131.03 -- hedging cost £1,503.70
  - C_IC1: actual £140,578.68 vs. naked £283,444.44 -- hedging cost £142,865.76
  - C_IC2: actual £93,089.46 vs. naked £161,132.40 -- hedging cost £68,042.94
  - C_IC3: actual £149,968.27 vs. naked £423,965.79 -- hedging cost £273,997.52
  - C_IC3g: actual £8,660.26 vs. naked £123,107.25 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £232,127.67 -- hedging cost £228,435.92

**Year narrative:** 2023 produced a net gain of £100,347.41 across 13 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 55 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £368,471.75 (gross £1,277,622.27, capital £9,664.42)
  - Electricity: gross £1,152,504.86, capital £9,608.51, net £357,730.84
  - Gas: gross £125,117.41, capital £55.91, net £10,740.91
- Treasury at year end: £3,755,721.70
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
- Average CLV (Point-in-Time, year-end 2024): £339,108.73
  - By billing account: C1 £2,964.83, C2 £4,687.90, C3 £3,798.63, C4 £2,168.75, C5 £7,056.44, C6 £13,691.13, C7 £4,629.12, C8 £6,843.57, C9 £6,717.89, C_IC1 £972,712.58, C_IC2 £639,073.94, C_IC3 £1,762,025.37, C_IC4 £982,043.39
- Bill shock events (>=20%): 42 -- C7 2024-01-31 (36%); C7 2024-02-29 (27%); C7 2024-05-31 (37%); C7 2024-09-30 (34%); C7 2024-11-30 (84%); C2 2024-04-30 (34%); C2 2024-12-31 (22%); C2g 2024-02-29 (24%); C2g 2024-04-30 (36%); C2g 2024-05-31 (47%); C2g 2024-07-31 (25%); C2g 2024-09-30 (53%); C2g 2024-10-31 (34%); C2g 2024-11-30 (52%); C6 2024-03-29 (33%); C8 2024-02-29 (23%); C8 2024-04-30 (45%); C8 2024-05-31 (27%); C8 2024-06-30 (142%); C8 2024-07-31 (65%); C8 2024-08-31 (137%); C8 2024-09-30 (72%); C8 2024-10-31 (35%); C8 2024-11-30 (61%); C9 2024-05-31 (49%); C9 2024-07-31 (30%); C9 2024-09-30 (55%); C9 2024-10-31 (23%); C9 2024-11-30 (47%); C4 2024-04-30 (33%); C4 2024-09-30 (28%); C4 2024-11-30 (28%); C4g 2024-02-29 (27%); C4g 2024-05-31 (68%); C4g 2024-07-31 (26%); C4g 2024-09-30 (22%); C4g 2024-10-31 (43%); C4g 2024-11-30 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (63%); C_IC2 2024-06-30 (50%); C_IC2 2024-07-31 (79%)
- Churn risk (accounts renewing in 2024): 7 at risk (≥20% churn prob): C2 41%, C4 38%, C6 23%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC4 20%

**Pricing & Margin**

- C2 (electricity): tariff £157.94-£397.50/MWh, net margin £210.57
- C2g (gas): tariff £48.41-£70.00/MWh, net margin £266.57
- C4 (electricity): tariff £159.80-£378.84/MWh, net margin £303.22
- C4g (gas): tariff £48.05-£65.13/MWh, net margin £443.58
- C6 (electricity): tariff £340.22/MWh, net margin £789.59
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £635.74
- C8 (electricity): tariff £159.13-£397.50/MWh, net margin £400.10
- C9 (electricity): tariff £165.00-£367.80/MWh, net margin £656.74
- C_IC1 (electricity): tariff £-98.58-£329.99/MWh, net margin £125,235.53
- C_IC2 (electricity): tariff £-106.92-£353.54/MWh, net margin £69,527.03
- C_IC3 (electricity): tariff £88.78-£191.53/MWh, net margin £154,021.01
- C_IC3g (gas): tariff £49.06-£55.98/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £5,951.30

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): 4271 -- £3,751,872.00 -> £3,342,739.02 (10.9%); £3,751,872.17 -> £3,342,739.02 (10.9%); £3,751,872.35 -> £3,342,739.02 (10.9%); £3,751,872.53 -> £3,342,739.02 (10.9%); £3,751,872.69 -> £3,342,739.03 (10.9%); £3,751,872.87 -> £3,342,739.03 (10.9%); £3,751,873.04 -> £3,342,739.03 (10.9%); £3,751,873.21 -> £3,342,739.03 (10.9%); £3,751,873.39 -> £3,342,739.03 (10.9%); £3,751,873.56 -> £3,342,739.04 (10.9%); £3,751,873.74 -> £3,342,739.04 (10.9%); £3,751,873.91 -> £3,342,739.03 (10.9%); £3,751,874.07 -> £3,342,739.03 (10.9%); £3,751,874.27 -> £3,342,739.07 (10.9%); £3,751,874.47 -> £3,342,739.12 (10.9%); £3,751,874.70 -> £3,342,739.18 (10.9%); £3,751,874.94 -> £3,342,739.22 (10.9%); £3,751,875.20 -> £3,342,739.27 (10.9%); £3,751,875.49 -> £3,342,739.31 (10.9%); £3,751,875.77 -> £3,342,739.35 (10.9%); £3,751,876.06 -> £3,342,739.39 (10.9%); £3,751,876.35 -> £3,342,739.38 (10.9%); £3,751,876.65 -> £3,342,739.38 (10.9%); £3,751,876.93 -> £3,342,739.38 (10.9%); £3,751,877.22 -> £3,342,739.38 (10.9%); £3,751,877.51 -> £3,342,739.38 (10.9%); £3,751,877.79 -> £3,342,739.38 (10.9%); £3,751,878.07 -> £3,342,739.38 (10.9%); £3,751,878.34 -> £3,342,739.38 (10.9%); £3,751,878.63 -> £3,342,739.37 (10.9%); £3,751,878.91 -> £3,342,739.38 (10.9%); £3,751,879.20 -> £3,342,739.41 (10.9%); £3,751,879.48 -> £3,342,739.47 (10.9%); £3,751,879.76 -> £3,342,739.54 (10.9%); £3,751,879.99 -> £3,342,739.60 (10.9%); £3,751,880.20 -> £3,342,739.67 (10.9%); £3,751,880.42 -> £3,342,739.74 (10.9%); £3,751,880.72 -> £3,342,739.82 (10.9%); £3,751,881.01 -> £3,342,739.91 (10.9%); £3,751,881.29 -> £3,342,739.88 (10.9%); £3,751,881.58 -> £3,342,739.86 (10.9%); £3,751,881.87 -> £3,342,739.84 (10.9%); £3,751,882.16 -> £3,342,739.82 (10.9%); £3,751,882.45 -> £3,342,739.81 (10.9%); £3,751,882.74 -> £3,342,739.81 (10.9%); £3,751,883.00 -> £3,342,739.81 (10.9%); £3,751,883.24 -> £3,342,739.80 (10.9%); £3,751,883.46 -> £3,342,739.80 (10.9%); £3,751,883.64 -> £3,342,739.80 (10.9%); £3,751,883.81 -> £3,342,739.81 (10.9%); £3,751,883.98 -> £3,342,739.81 (10.9%); £3,751,884.15 -> £3,342,739.81 (10.9%); £3,751,884.32 -> £3,342,739.81 (10.9%); £3,751,884.49 -> £3,342,739.82 (10.9%); £3,751,884.66 -> £3,342,739.82 (10.9%); £3,751,884.83 -> £3,342,739.82 (10.9%); £3,751,885.00 -> £3,342,739.82 (10.9%); £3,751,885.17 -> £3,342,739.83 (10.9%); £3,751,885.34 -> £3,342,739.83 (10.9%); £3,751,885.51 -> £3,342,739.83 (10.9%); £3,751,885.68 -> £3,342,739.82 (10.9%); £3,751,885.86 -> £3,342,739.87 (10.9%); £3,751,886.07 -> £3,342,739.92 (10.9%); £3,751,886.30 -> £3,342,739.97 (10.9%); £3,751,886.53 -> £3,342,740.02 (10.9%); £3,751,886.78 -> £3,342,740.07 (10.9%); £3,751,887.06 -> £3,342,740.11 (10.9%); £3,751,887.34 -> £3,342,740.15 (10.9%); £3,751,887.62 -> £3,342,740.19 (10.9%); £3,751,887.91 -> £3,342,740.19 (10.9%); £3,751,888.19 -> £3,342,740.18 (10.9%); £3,751,888.47 -> £3,342,740.18 (10.9%); £3,751,888.74 -> £3,342,740.18 (10.9%); £3,751,889.02 -> £3,342,740.18 (10.9%); £3,751,889.31 -> £3,342,740.18 (10.9%); £3,751,889.58 -> £3,342,740.18 (10.9%); £3,751,889.86 -> £3,342,740.18 (10.9%); £3,751,890.13 -> £3,342,740.18 (10.9%); £3,751,890.41 -> £3,342,740.18 (10.9%); £3,751,890.69 -> £3,342,740.21 (10.9%); £3,751,890.89 -> £3,342,740.27 (10.9%); £3,751,891.11 -> £3,342,740.33 (10.9%); £3,751,891.32 -> £3,342,740.40 (10.9%); £3,751,891.53 -> £3,342,740.47 (10.9%); £3,751,891.75 -> £3,342,740.53 (10.9%); £3,751,891.96 -> £3,342,740.62 (10.9%); £3,751,892.17 -> £3,342,740.70 (10.9%); £3,751,892.45 -> £3,342,740.67 (10.9%); £3,751,892.74 -> £3,342,740.65 (10.9%); £3,751,893.02 -> £3,342,740.63 (10.9%); £3,751,893.30 -> £3,342,740.61 (10.9%); £3,751,893.59 -> £3,342,740.60 (10.9%); £3,751,893.87 -> £3,342,740.60 (10.9%); £3,751,894.13 -> £3,342,740.59 (10.9%); £3,751,894.36 -> £3,342,740.59 (10.9%); £3,751,894.58 -> £3,342,740.58 (10.9%); £3,751,894.75 -> £3,342,740.58 (10.9%); £3,751,894.93 -> £3,342,740.58 (10.9%); £3,751,895.09 -> £3,342,740.59 (10.9%); £3,751,895.26 -> £3,342,740.59 (10.9%); £3,751,895.43 -> £3,342,740.59 (10.9%); £3,751,895.60 -> £3,342,740.59 (10.9%); £3,751,895.77 -> £3,342,740.59 (10.9%); £3,751,895.93 -> £3,342,740.59 (10.9%); £3,751,896.11 -> £3,342,740.60 (10.9%); £3,751,896.28 -> £3,342,740.60 (10.9%); £3,751,896.45 -> £3,342,740.60 (10.9%); £3,751,896.62 -> £3,342,740.60 (10.9%); £3,751,896.79 -> £3,342,740.59 (10.9%); £3,751,896.98 -> £3,342,740.64 (10.9%); £3,751,897.18 -> £3,342,740.69 (10.9%); £3,751,897.41 -> £3,342,740.74 (10.9%); £3,751,897.65 -> £3,342,740.79 (10.9%); £3,751,897.92 -> £3,342,740.84 (10.9%); £3,751,898.20 -> £3,342,740.88 (10.9%); £3,751,898.48 -> £3,342,740.92 (10.9%); £3,751,898.77 -> £3,342,740.95 (10.9%); £3,751,899.05 -> £3,342,740.95 (10.9%); £3,751,899.33 -> £3,342,740.95 (10.9%); £3,751,899.63 -> £3,342,740.95 (10.9%); £3,751,899.92 -> £3,342,740.95 (10.9%); £3,751,900.21 -> £3,342,740.94 (10.9%); £3,751,900.49 -> £3,342,740.94 (10.9%); £3,751,900.76 -> £3,342,740.94 (10.9%); £3,751,901.04 -> £3,342,740.94 (10.9%); £3,751,901.33 -> £3,342,740.94 (10.9%); £3,751,901.60 -> £3,342,740.94 (10.9%); £3,751,901.88 -> £3,342,740.98 (10.9%); £3,751,902.17 -> £3,342,741.04 (10.9%); £3,751,902.38 -> £3,342,741.10 (10.9%); £3,751,902.66 -> £3,342,741.17 (10.9%); £3,751,902.87 -> £3,342,741.24 (10.9%); £3,751,903.08 -> £3,342,741.30 (10.9%); £3,751,903.29 -> £3,342,741.38 (10.9%); £3,751,903.51 -> £3,342,741.47 (10.9%); £3,751,903.79 -> £3,342,741.44 (10.9%); £3,751,904.07 -> £3,342,741.42 (10.9%); £3,751,904.35 -> £3,342,741.40 (10.9%); £3,751,904.62 -> £3,342,741.37 (10.9%); £3,751,904.91 -> £3,342,741.37 (10.9%); £3,751,905.20 -> £3,342,741.36 (10.9%); £3,751,905.46 -> £3,342,741.36 (10.9%); £3,751,905.69 -> £3,342,741.35 (10.9%); £3,751,905.91 -> £3,342,741.35 (10.9%); £3,751,906.08 -> £3,342,741.35 (10.9%); £3,751,906.24 -> £3,342,741.35 (10.9%); £3,751,906.40 -> £3,342,741.35 (10.9%); £3,751,906.57 -> £3,342,741.36 (10.9%); £3,751,906.74 -> £3,342,741.36 (10.9%); £3,751,906.91 -> £3,342,741.36 (10.9%); £3,751,907.08 -> £3,342,741.36 (10.9%); £3,751,907.25 -> £3,342,741.37 (10.9%); £3,751,907.41 -> £3,342,741.37 (10.9%); £3,751,907.59 -> £3,342,741.37 (10.9%); £3,751,907.75 -> £3,342,741.37 (10.9%); £3,751,907.93 -> £3,342,741.37 (10.9%); £3,751,908.09 -> £3,342,741.36 (10.9%); £3,751,908.28 -> £3,342,741.41 (10.9%); £3,751,908.48 -> £3,342,741.46 (10.9%); £3,751,908.70 -> £3,342,741.51 (10.9%); £3,751,908.94 -> £3,342,741.56 (10.9%); £3,751,909.21 -> £3,342,741.61 (10.9%); £3,751,909.48 -> £3,342,741.65 (10.9%); £3,751,909.76 -> £3,342,741.69 (10.9%); £3,751,910.04 -> £3,342,741.73 (10.9%); £3,751,910.32 -> £3,342,741.72 (10.9%); £3,751,910.59 -> £3,342,741.72 (10.9%); £3,751,910.87 -> £3,342,741.72 (10.9%); £3,751,911.14 -> £3,342,741.72 (10.9%); £3,751,911.42 -> £3,342,741.72 (10.9%); £3,751,911.70 -> £3,342,741.72 (10.9%); £3,751,911.98 -> £3,342,741.72 (10.9%); £3,751,912.25 -> £3,342,741.71 (10.9%); £3,751,912.54 -> £3,342,741.71 (10.9%); £3,751,912.81 -> £3,342,741.71 (10.9%); £3,751,913.09 -> £3,342,741.75 (10.9%); £3,751,913.30 -> £3,342,741.81 (10.9%); £3,751,913.58 -> £3,342,741.87 (10.9%); £3,751,913.85 -> £3,342,741.94 (10.9%); £3,751,914.05 -> £3,342,742.01 (10.9%); £3,751,914.32 -> £3,342,742.07 (10.9%); £3,751,914.60 -> £3,342,742.16 (10.9%); £3,751,914.82 -> £3,342,742.24 (10.9%); £3,751,915.10 -> £3,342,742.21 (10.9%); £3,751,915.38 -> £3,342,742.19 (10.9%); £3,751,915.66 -> £3,342,742.16 (10.9%); £3,751,915.94 -> £3,342,742.14 (10.9%); £3,751,916.22 -> £3,342,742.13 (10.9%); £3,751,916.49 -> £3,342,742.13 (10.9%); £3,751,916.75 -> £3,342,742.12 (10.9%); £3,751,916.99 -> £3,342,742.12 (10.9%); £3,751,917.20 -> £3,342,742.12 (10.9%); £3,751,917.37 -> £3,342,742.12 (10.9%); £3,751,917.52 -> £3,342,742.12 (10.9%); £3,751,917.69 -> £3,342,742.12 (10.9%); £3,751,917.85 -> £3,342,742.12 (10.9%); £3,751,918.00 -> £3,342,742.12 (10.9%); £3,751,918.17 -> £3,342,742.13 (10.9%); £3,751,918.33 -> £3,342,742.13 (10.9%); £3,751,918.49 -> £3,342,742.13 (10.9%); £3,751,918.65 -> £3,342,742.13 (10.9%); £3,751,918.82 -> £3,342,742.13 (10.9%); £3,751,918.98 -> £3,342,742.14 (10.9%); £3,751,919.14 -> £3,342,742.13 (10.9%); £3,751,919.30 -> £3,342,742.13 (10.9%); £3,751,919.48 -> £3,342,742.17 (10.9%); £3,751,919.68 -> £3,342,742.23 (10.9%); £3,751,919.89 -> £3,342,742.28 (10.9%); £3,751,920.13 -> £3,342,742.33 (10.9%); £3,751,920.38 -> £3,342,742.37 (10.9%); £3,751,920.66 -> £3,342,742.42 (10.9%); £3,751,920.93 -> £3,342,742.45 (10.9%); £3,751,921.20 -> £3,342,742.49 (10.9%); £3,751,921.46 -> £3,342,742.49 (10.9%); £3,751,921.73 -> £3,342,742.48 (10.9%); £3,751,922.00 -> £3,342,742.48 (10.9%); £3,751,922.28 -> £3,342,742.48 (10.9%); £3,751,922.55 -> £3,342,742.48 (10.9%); £3,751,922.82 -> £3,342,742.48 (10.9%); £3,751,923.08 -> £3,342,742.48 (10.9%); £3,751,923.34 -> £3,342,742.48 (10.9%); £3,751,923.61 -> £3,342,742.48 (10.9%); £3,751,923.88 -> £3,342,742.48 (10.9%); £3,751,924.15 -> £3,342,742.51 (10.9%); £3,751,924.35 -> £3,342,742.57 (10.9%); £3,751,924.55 -> £3,342,742.63 (10.9%); £3,751,924.76 -> £3,342,742.70 (10.9%); £3,751,924.96 -> £3,342,742.77 (10.9%); £3,751,925.23 -> £3,342,742.83 (10.9%); £3,751,925.43 -> £3,342,742.92 (10.9%); £3,751,925.63 -> £3,342,743.00 (10.9%); £3,751,925.90 -> £3,342,742.97 (10.9%); £3,751,926.17 -> £3,342,742.95 (10.9%); £3,751,926.43 -> £3,342,742.92 (10.9%); £3,751,926.70 -> £3,342,742.90 (10.9%); £3,751,926.97 -> £3,342,742.89 (10.9%); £3,751,927.23 -> £3,342,742.89 (10.9%); £3,751,927.49 -> £3,342,742.88 (10.9%); £3,751,927.72 -> £3,342,742.88 (10.9%); £3,751,927.93 -> £3,342,742.88 (10.9%); £3,751,928.07 -> £3,342,742.88 (10.9%); £3,751,928.22 -> £3,342,742.88 (10.9%); £3,751,928.36 -> £3,342,742.88 (10.9%); £3,751,928.51 -> £3,342,742.88 (10.9%); £3,751,928.66 -> £3,342,742.88 (10.9%); £3,751,928.80 -> £3,342,742.88 (10.9%); £3,751,928.94 -> £3,342,742.89 (10.9%); £3,751,929.07 -> £3,342,742.89 (10.9%); £3,751,929.21 -> £3,342,742.89 (10.9%); £3,751,929.35 -> £3,342,742.89 (10.9%); £3,751,929.49 -> £3,342,742.89 (10.9%); £3,751,929.63 -> £3,342,742.89 (10.9%); £3,751,929.77 -> £3,342,742.89 (10.9%); £3,751,929.93 -> £3,342,742.89 (10.9%); £3,751,930.10 -> £3,342,742.88 (10.9%); £3,751,930.29 -> £3,342,742.88 (10.9%); £3,751,930.50 -> £3,342,742.87 (10.9%); £3,751,930.72 -> £3,342,742.86 (10.9%); £3,751,930.95 -> £3,342,742.85 (10.9%); £3,751,931.19 -> £3,342,742.85 (10.9%); £3,751,931.42 -> £3,342,742.84 (10.9%); £3,751,931.66 -> £3,342,742.84 (10.9%); £3,751,931.89 -> £3,342,742.83 (10.9%); £3,751,932.13 -> £3,342,742.83 (10.9%); £3,751,932.37 -> £3,342,742.82 (10.9%); £3,751,932.60 -> £3,342,742.82 (10.9%); £3,751,932.84 -> £3,342,742.82 (10.9%); £3,751,933.09 -> £3,342,742.81 (10.9%); £3,751,933.32 -> £3,342,742.81 (10.9%); £3,751,933.56 -> £3,342,742.81 (10.9%); £3,751,933.80 -> £3,342,742.81 (10.9%); £3,751,934.04 -> £3,342,742.80 (10.9%); £3,751,934.26 -> £3,342,742.79 (10.9%); £3,751,934.44 -> £3,342,742.77 (10.9%); £3,751,934.61 -> £3,342,742.76 (10.9%); £3,751,934.79 -> £3,342,742.74 (10.9%); £3,751,934.96 -> £3,342,742.72 (10.9%); £3,751,935.14 -> £3,342,742.69 (10.9%); £3,751,935.32 -> £3,342,742.66 (10.9%); £3,751,935.55 -> £3,342,742.64 (10.9%); £3,751,935.79 -> £3,342,742.61 (10.9%); £3,751,936.02 -> £3,342,742.59 (10.9%); £3,751,936.25 -> £3,342,742.57 (10.9%); £3,751,936.49 -> £3,342,742.57 (10.9%); £3,751,936.72 -> £3,342,742.56 (10.9%); £3,751,936.94 -> £3,342,742.55 (10.9%); £3,751,937.13 -> £3,342,742.55 (10.9%); £3,751,937.32 -> £3,342,742.55 (10.9%); £3,751,937.46 -> £3,342,742.54 (10.9%); £3,751,937.60 -> £3,342,742.54 (10.9%); £3,751,937.74 -> £3,342,742.54 (10.9%); £3,751,937.88 -> £3,342,742.54 (10.9%); £3,751,938.02 -> £3,342,742.55 (10.9%); £3,751,938.16 -> £3,342,742.55 (10.9%); £3,751,938.30 -> £3,342,742.55 (10.9%); £3,751,938.44 -> £3,342,742.55 (10.9%); £3,751,938.58 -> £3,342,742.55 (10.9%); £3,751,938.71 -> £3,342,742.55 (10.9%); £3,751,938.85 -> £3,342,742.56 (10.9%); £3,751,938.99 -> £3,342,742.56 (10.9%); £3,751,939.13 -> £3,342,742.55 (10.9%); £3,751,939.28 -> £3,342,742.55 (10.9%); £3,751,939.46 -> £3,342,742.55 (10.9%); £3,751,939.65 -> £3,342,742.55 (10.9%); £3,751,939.85 -> £3,342,742.54 (10.9%); £3,751,940.07 -> £3,342,742.53 (10.9%); £3,751,940.31 -> £3,342,742.52 (10.9%); £3,751,940.55 -> £3,342,742.51 (10.9%); £3,751,940.77 -> £3,342,742.50 (10.9%); £3,751,941.01 -> £3,342,742.49 (10.9%); £3,751,941.24 -> £3,342,742.49 (10.9%); £3,751,941.47 -> £3,342,742.48 (10.9%); £3,751,941.70 -> £3,342,742.47 (10.9%); £3,751,941.92 -> £3,342,742.46 (10.9%); £3,751,942.15 -> £3,342,742.45 (10.9%); £3,751,942.39 -> £3,342,742.44 (10.9%); £3,751,942.62 -> £3,342,742.44 (10.9%); £3,751,942.85 -> £3,342,742.43 (10.9%); £3,751,943.08 -> £3,342,742.43 (10.9%); £3,751,943.31 -> £3,342,742.42 (10.9%); £3,751,943.49 -> £3,342,742.41 (10.9%); £3,751,943.67 -> £3,342,742.39 (10.9%); £3,751,943.83 -> £3,342,742.37 (10.9%); £3,751,944.01 -> £3,342,742.35 (10.9%); £3,751,944.24 -> £3,342,742.33 (10.9%); £3,751,944.42 -> £3,342,742.30 (10.9%); £3,751,944.59 -> £3,342,742.27 (10.9%); £3,751,944.83 -> £3,342,742.25 (10.9%); £3,751,945.07 -> £3,342,742.23 (10.9%); £3,751,945.30 -> £3,342,742.20 (10.9%); £3,751,945.53 -> £3,342,742.18 (10.9%); £3,751,945.76 -> £3,342,742.17 (10.9%); £3,751,945.99 -> £3,342,742.17 (10.9%); £3,751,946.21 -> £3,342,742.16 (10.9%); £3,751,946.41 -> £3,342,742.16 (10.9%); £3,751,946.59 -> £3,342,742.16 (10.9%); £3,751,946.75 -> £3,342,742.16 (10.9%); £3,751,946.90 -> £3,342,742.16 (10.9%); £3,751,947.05 -> £3,342,742.16 (10.9%); £3,751,947.20 -> £3,342,742.16 (10.9%); £3,751,947.36 -> £3,342,742.16 (10.9%); £3,751,947.51 -> £3,342,742.16 (10.9%); £3,751,947.66 -> £3,342,742.17 (10.9%); £3,751,947.82 -> £3,342,742.17 (10.9%); £3,751,947.98 -> £3,342,742.17 (10.9%); £3,751,948.13 -> £3,342,742.17 (10.9%); £3,751,948.28 -> £3,342,742.17 (10.9%); £3,751,948.44 -> £3,342,742.17 (10.9%); £3,751,948.59 -> £3,342,742.16 (10.9%); £3,751,948.76 -> £3,342,742.21 (10.9%); £3,751,948.95 -> £3,342,742.26 (10.9%); £3,751,949.15 -> £3,342,742.31 (10.9%); £3,751,949.37 -> £3,342,742.36 (10.9%); £3,751,949.60 -> £3,342,742.41 (10.9%); £3,751,949.85 -> £3,342,742.45 (10.9%); £3,751,950.10 -> £3,342,742.49 (10.9%); £3,751,950.36 -> £3,342,742.52 (10.9%); £3,751,950.62 -> £3,342,742.52 (10.9%); £3,751,950.87 -> £3,342,742.52 (10.9%); £3,751,951.13 -> £3,342,742.52 (10.9%); £3,751,951.39 -> £3,342,742.51 (10.9%); £3,751,951.65 -> £3,342,742.51 (10.9%); £3,751,951.91 -> £3,342,742.51 (10.9%); £3,751,952.16 -> £3,342,742.51 (10.9%); £3,751,952.42 -> £3,342,742.51 (10.9%); £3,751,952.68 -> £3,342,742.51 (10.9%); £3,751,952.94 -> £3,342,742.51 (10.9%); £3,751,953.20 -> £3,342,742.54 (10.9%); £3,751,953.46 -> £3,342,742.60 (10.9%); £3,751,953.72 -> £3,342,742.67 (10.9%); £3,751,953.97 -> £3,342,742.74 (10.9%); £3,751,954.22 -> £3,342,742.80 (10.9%); £3,751,954.47 -> £3,342,742.87 (10.9%); £3,751,954.72 -> £3,342,742.96 (10.9%); £3,751,954.91 -> £3,342,743.04 (10.9%); £3,751,955.16 -> £3,342,743.01 (10.9%); £3,751,955.42 -> £3,342,742.99 (10.9%); £3,751,955.66 -> £3,342,742.96 (10.9%); £3,751,955.92 -> £3,342,742.94 (10.9%); £3,751,956.17 -> £3,342,742.94 (10.9%); £3,751,956.43 -> £3,342,742.93 (10.9%); £3,751,956.67 -> £3,342,742.93 (10.9%); £3,751,956.89 -> £3,342,742.92 (10.9%); £3,751,957.09 -> £3,342,742.92 (10.9%); £3,751,957.24 -> £3,342,742.92 (10.9%); £3,751,957.39 -> £3,342,742.92 (10.9%); £3,751,957.55 -> £3,342,742.92 (10.9%); £3,751,957.70 -> £3,342,742.93 (10.9%); £3,751,957.85 -> £3,342,742.93 (10.9%); £3,751,958.00 -> £3,342,742.93 (10.9%); £3,751,958.16 -> £3,342,742.93 (10.9%); £3,751,958.30 -> £3,342,742.93 (10.9%); £3,751,958.46 -> £3,342,742.94 (10.9%); £3,751,958.61 -> £3,342,742.94 (10.9%); £3,751,958.77 -> £3,342,742.94 (10.9%); £3,751,958.92 -> £3,342,742.94 (10.9%); £3,751,959.07 -> £3,342,742.93 (10.9%); £3,751,959.23 -> £3,342,742.98 (10.9%); £3,751,959.42 -> £3,342,743.03 (10.9%); £3,751,959.62 -> £3,342,743.08 (10.9%); £3,751,959.84 -> £3,342,743.13 (10.9%); £3,751,960.07 -> £3,342,743.18 (10.9%); £3,751,960.32 -> £3,342,743.22 (10.9%); £3,751,960.58 -> £3,342,743.26 (10.9%); £3,751,960.82 -> £3,342,743.29 (10.9%); £3,751,961.08 -> £3,342,743.29 (10.9%); £3,751,961.34 -> £3,342,743.29 (10.9%); £3,751,961.60 -> £3,342,743.29 (10.9%); £3,751,961.86 -> £3,342,743.29 (10.9%); £3,751,962.11 -> £3,342,743.29 (10.9%); £3,751,962.37 -> £3,342,743.29 (10.9%); £3,751,962.62 -> £3,342,743.28 (10.9%); £3,751,962.88 -> £3,342,743.28 (10.9%); £3,751,963.14 -> £3,342,743.28 (10.9%); £3,751,963.39 -> £3,342,743.28 (10.9%); £3,751,963.64 -> £3,342,743.32 (10.9%); £3,751,963.82 -> £3,342,743.38 (10.9%); £3,751,964.01 -> £3,342,743.44 (10.9%); £3,751,964.26 -> £3,342,743.51 (10.9%); £3,751,964.45 -> £3,342,743.57 (10.9%); £3,751,964.64 -> £3,342,743.64 (10.9%); £3,751,964.90 -> £3,342,743.73 (10.9%); £3,751,965.15 -> £3,342,743.81 (10.9%); £3,751,965.41 -> £3,342,743.78 (10.9%); £3,751,965.67 -> £3,342,743.76 (10.9%); £3,751,965.92 -> £3,342,743.74 (10.9%); £3,751,966.18 -> £3,342,743.72 (10.9%); £3,751,966.43 -> £3,342,743.71 (10.9%); £3,751,966.69 -> £3,342,743.70 (10.9%); £3,751,966.92 -> £3,342,743.70 (10.9%); £3,751,967.13 -> £3,342,743.70 (10.9%); £3,751,967.33 -> £3,342,743.69 (10.9%); £3,751,967.48 -> £3,342,743.69 (10.9%); £3,751,967.64 -> £3,342,743.69 (10.9%); £3,751,967.79 -> £3,342,743.70 (10.9%); £3,751,967.94 -> £3,342,743.70 (10.9%); £3,751,968.09 -> £3,342,743.70 (10.9%); £3,751,968.24 -> £3,342,743.70 (10.9%); £3,751,968.39 -> £3,342,743.70 (10.9%); £3,751,968.54 -> £3,342,743.71 (10.9%); £3,751,968.69 -> £3,342,743.71 (10.9%); £3,751,968.84 -> £3,342,743.71 (10.9%); £3,751,968.99 -> £3,342,743.71 (10.9%); £3,751,969.15 -> £3,342,743.71 (10.9%); £3,751,969.30 -> £3,342,743.70 (10.9%); £3,751,969.46 -> £3,342,743.75 (10.9%); £3,751,969.65 -> £3,342,743.80 (10.9%); £3,751,969.84 -> £3,342,743.85 (10.9%); £3,751,970.07 -> £3,342,743.90 (10.9%); £3,751,970.31 -> £3,342,743.94 (10.9%); £3,751,970.56 -> £3,342,743.98 (10.9%); £3,751,970.81 -> £3,342,744.02 (10.9%); £3,751,971.06 -> £3,342,744.06 (10.9%); £3,751,971.31 -> £3,342,744.05 (10.9%); £3,751,971.56 -> £3,342,744.05 (10.9%); £3,751,971.81 -> £3,342,744.05 (10.9%); £3,751,972.07 -> £3,342,744.05 (10.9%); £3,751,972.33 -> £3,342,744.05 (10.9%); £3,751,972.58 -> £3,342,744.05 (10.9%); £3,751,972.83 -> £3,342,744.05 (10.9%); £3,751,973.09 -> £3,342,744.04 (10.9%); £3,751,973.34 -> £3,342,744.04 (10.9%); £3,751,973.59 -> £3,342,744.04 (10.9%); £3,751,973.83 -> £3,342,744.08 (10.9%); £3,751,974.09 -> £3,342,744.14 (10.9%); £3,751,974.28 -> £3,342,744.20 (10.9%); £3,751,974.53 -> £3,342,744.27 (10.9%); £3,751,974.78 -> £3,342,744.33 (10.9%); £3,751,974.98 -> £3,342,744.40 (10.9%); £3,751,975.22 -> £3,342,744.49 (10.9%); £3,751,975.40 -> £3,342,744.57 (10.9%); £3,751,975.66 -> £3,342,744.54 (10.9%); £3,751,975.91 -> £3,342,744.52 (10.9%); £3,751,976.16 -> £3,342,744.49 (10.9%); £3,751,976.41 -> £3,342,744.47 (10.9%); £3,751,976.66 -> £3,342,744.47 (10.9%); £3,751,976.91 -> £3,342,744.46 (10.9%); £3,751,977.14 -> £3,342,744.46 (10.9%); £3,751,977.35 -> £3,342,744.45 (10.9%); £3,751,977.55 -> £3,342,744.45 (10.9%); £3,751,977.70 -> £3,342,744.45 (10.9%); £3,751,977.85 -> £3,342,744.45 (10.9%); £3,751,978.00 -> £3,342,744.45 (10.9%); £3,751,978.15 -> £3,342,744.45 (10.9%); £3,751,978.30 -> £3,342,744.46 (10.9%); £3,751,978.45 -> £3,342,744.46 (10.9%); £3,751,978.60 -> £3,342,744.46 (10.9%); £3,751,978.75 -> £3,342,744.46 (10.9%); £3,751,978.90 -> £3,342,744.47 (10.9%); £3,751,979.05 -> £3,342,744.47 (10.9%); £3,751,979.20 -> £3,342,744.47 (10.9%); £3,751,979.35 -> £3,342,744.47 (10.9%); £3,751,979.49 -> £3,342,744.46 (10.9%); £3,751,979.66 -> £3,342,744.50 (10.9%); £3,751,979.84 -> £3,342,744.55 (10.9%); £3,751,980.04 -> £3,342,744.61 (10.9%); £3,751,980.26 -> £3,342,744.65 (10.9%); £3,751,980.48 -> £3,342,744.70 (10.9%); £3,751,980.74 -> £3,342,744.74 (10.9%); £3,751,980.99 -> £3,342,744.78 (10.9%); £3,751,981.24 -> £3,342,744.81 (10.9%); £3,751,981.49 -> £3,342,744.81 (10.9%); £3,751,981.74 -> £3,342,744.81 (10.9%); £3,751,981.98 -> £3,342,744.81 (10.9%); £3,751,982.23 -> £3,342,744.81 (10.9%); £3,751,982.47 -> £3,342,744.80 (10.9%); £3,751,982.72 -> £3,342,744.80 (10.9%); £3,751,982.96 -> £3,342,744.80 (10.9%); £3,751,983.21 -> £3,342,744.80 (10.9%); £3,751,983.46 -> £3,342,744.80 (10.9%); £3,751,983.72 -> £3,342,744.80 (10.9%); £3,751,983.97 -> £3,342,744.84 (10.9%); £3,751,984.16 -> £3,342,744.89 (10.9%); £3,751,984.34 -> £3,342,744.96 (10.9%); £3,751,984.52 -> £3,342,745.02 (10.9%); £3,751,984.70 -> £3,342,745.09 (10.9%); £3,751,984.89 -> £3,342,745.16 (10.9%); £3,751,985.07 -> £3,342,745.24 (10.9%); £3,751,985.26 -> £3,342,745.32 (10.9%); £3,751,985.51 -> £3,342,745.29 (10.9%); £3,751,985.76 -> £3,342,745.27 (10.9%); £3,751,986.01 -> £3,342,745.25 (10.9%); £3,751,986.26 -> £3,342,745.22 (10.9%); £3,751,986.51 -> £3,342,745.22 (10.9%); £3,751,986.76 -> £3,342,745.21 (10.9%); £3,751,986.99 -> £3,342,745.21 (10.9%); £3,751,987.20 -> £3,342,745.20 (10.9%); £3,751,987.39 -> £3,342,745.20 (10.9%); £3,751,987.54 -> £3,342,745.20 (10.9%); £3,751,987.69 -> £3,342,745.20 (10.9%); £3,751,987.84 -> £3,342,745.20 (10.9%); £3,751,987.98 -> £3,342,745.21 (10.9%); £3,751,988.13 -> £3,342,745.21 (10.9%); £3,751,988.27 -> £3,342,745.21 (10.9%); £3,751,988.42 -> £3,342,745.21 (10.9%); £3,751,988.57 -> £3,342,745.21 (10.9%); £3,751,988.71 -> £3,342,745.22 (10.9%); £3,751,988.86 -> £3,342,745.22 (10.9%); £3,751,989.01 -> £3,342,745.22 (10.9%); £3,751,989.16 -> £3,342,745.21 (10.9%); £3,751,989.31 -> £3,342,745.21 (10.9%); £3,751,989.47 -> £3,342,745.25 (10.9%); £3,751,989.66 -> £3,342,745.30 (10.9%); £3,751,989.85 -> £3,342,745.36 (10.9%); £3,751,990.06 -> £3,342,745.40 (10.9%); £3,751,990.29 -> £3,342,745.45 (10.9%); £3,751,990.54 -> £3,342,745.49 (10.9%); £3,751,990.78 -> £3,342,745.53 (10.9%); £3,751,991.01 -> £3,342,745.56 (10.9%); £3,751,991.26 -> £3,342,745.56 (10.9%); £3,751,991.51 -> £3,342,745.56 (10.9%); £3,751,991.76 -> £3,342,745.56 (10.9%); £3,751,992.01 -> £3,342,745.56 (10.9%); £3,751,992.25 -> £3,342,745.55 (10.9%); £3,751,992.49 -> £3,342,745.55 (10.9%); £3,751,992.73 -> £3,342,745.55 (10.9%); £3,751,992.97 -> £3,342,745.55 (10.9%); £3,751,993.22 -> £3,342,745.55 (10.9%); £3,751,993.46 -> £3,342,745.55 (10.9%); £3,751,993.70 -> £3,342,745.58 (10.9%); £3,751,993.89 -> £3,342,745.64 (10.9%); £3,751,994.08 -> £3,342,745.71 (10.9%); £3,751,994.26 -> £3,342,745.77 (10.9%); £3,751,994.45 -> £3,342,745.84 (10.9%); £3,751,994.62 -> £3,342,745.90 (10.9%); £3,751,994.81 -> £3,342,745.99 (10.9%); £3,751,994.99 -> £3,342,746.07 (10.9%); £3,751,995.24 -> £3,342,746.04 (10.9%); £3,751,995.48 -> £3,342,746.02 (10.9%); £3,751,995.73 -> £3,342,745.99 (10.9%); £3,751,995.97 -> £3,342,745.97 (10.9%); £3,751,996.23 -> £3,342,745.96 (10.9%); £3,751,996.47 -> £3,342,745.96 (10.9%); £3,751,996.71 -> £3,342,745.95 (10.9%); £3,751,996.92 -> £3,342,745.95 (10.9%); £3,751,997.11 -> £3,342,745.95 (10.9%); £3,751,997.24 -> £3,342,745.94 (10.9%); £3,751,997.37 -> £3,342,745.95 (10.9%); £3,751,997.50 -> £3,342,745.95 (10.9%); £3,751,997.62 -> £3,342,745.95 (10.9%); £3,751,997.75 -> £3,342,745.95 (10.9%); £3,751,997.88 -> £3,342,745.95 (10.9%); £3,751,998.01 -> £3,342,745.95 (10.9%); £3,751,998.14 -> £3,342,745.96 (10.9%); £3,751,998.27 -> £3,342,745.96 (10.9%); £3,751,998.39 -> £3,342,745.96 (10.9%); £3,751,998.52 -> £3,342,745.96 (10.9%); £3,751,998.65 -> £3,342,745.96 (10.9%); £3,751,998.78 -> £3,342,745.96 (10.9%); £3,751,998.92 -> £3,342,745.95 (10.9%); £3,751,999.08 -> £3,342,745.95 (10.9%); £3,751,999.25 -> £3,342,745.94 (10.9%); £3,751,999.44 -> £3,342,745.93 (10.9%); £3,751,999.64 -> £3,342,745.92 (10.9%); £3,751,999.85 -> £3,342,745.91 (10.9%); £3,752,000.05 -> £3,342,745.91 (10.9%); £3,752,000.26 -> £3,342,745.91 (10.9%); £3,752,000.47 -> £3,342,745.90 (10.9%); £3,752,000.68 -> £3,342,745.90 (10.9%); £3,752,000.89 -> £3,342,745.89 (10.9%); £3,752,001.11 -> £3,342,745.89 (10.9%); £3,752,001.32 -> £3,342,745.88 (10.9%); £3,752,001.53 -> £3,342,745.88 (10.9%); £3,752,001.75 -> £3,342,745.88 (10.9%); £3,752,001.96 -> £3,342,745.87 (10.9%); £3,752,002.17 -> £3,342,745.87 (10.9%); £3,752,002.38 -> £3,342,745.87 (10.9%); £3,752,002.60 -> £3,342,745.87 (10.9%); £3,752,002.76 -> £3,342,745.86 (10.9%); £3,752,002.92 -> £3,342,745.84 (10.9%); £3,752,003.08 -> £3,342,745.82 (10.9%); £3,752,003.24 -> £3,342,745.80 (10.9%); £3,752,003.40 -> £3,342,745.78 (10.9%); £3,752,003.56 -> £3,342,745.75 (10.9%); £3,752,003.76 -> £3,342,745.73 (10.9%); £3,752,003.98 -> £3,342,745.70 (10.9%); £3,752,004.20 -> £3,342,745.68 (10.9%); £3,752,004.41 -> £3,342,745.66 (10.9%); £3,752,004.62 -> £3,342,745.64 (10.9%); £3,752,004.83 -> £3,342,745.63 (10.9%); £3,752,005.05 -> £3,342,745.63 (10.9%); £3,752,005.24 -> £3,342,745.62 (10.9%); £3,752,005.42 -> £3,342,745.62 (10.9%); £3,752,005.58 -> £3,342,745.61 (10.9%); £3,752,005.71 -> £3,342,745.61 (10.9%); £3,752,005.84 -> £3,342,745.61 (10.9%); £3,752,005.96 -> £3,342,745.61 (10.9%); £3,752,006.09 -> £3,342,745.61 (10.9%); £3,752,006.22 -> £3,342,745.61 (10.9%); £3,752,006.34 -> £3,342,745.61 (10.9%); £3,752,006.47 -> £3,342,745.62 (10.9%); £3,752,006.59 -> £3,342,745.62 (10.9%); £3,752,006.72 -> £3,342,745.62 (10.9%); £3,752,006.85 -> £3,342,745.62 (10.9%); £3,752,006.97 -> £3,342,745.62 (10.9%); £3,752,007.10 -> £3,342,745.62 (10.9%); £3,752,007.22 -> £3,342,745.62 (10.9%); £3,752,007.37 -> £3,342,745.62 (10.9%); £3,752,007.52 -> £3,342,745.62 (10.9%); £3,752,007.70 -> £3,342,745.61 (10.9%); £3,752,007.88 -> £3,342,745.61 (10.9%); £3,752,008.08 -> £3,342,745.60 (10.9%); £3,752,008.28 -> £3,342,745.59 (10.9%); £3,752,008.50 -> £3,342,745.58 (10.9%); £3,752,008.71 -> £3,342,745.57 (10.9%); £3,752,008.91 -> £3,342,745.56 (10.9%); £3,752,009.13 -> £3,342,745.55 (10.9%); £3,752,009.35 -> £3,342,745.54 (10.9%); £3,752,009.56 -> £3,342,745.53 (10.9%); £3,752,009.76 -> £3,342,745.52 (10.9%); £3,752,009.97 -> £3,342,745.52 (10.9%); £3,752,010.19 -> £3,342,745.51 (10.9%); £3,752,010.39 -> £3,342,745.50 (10.9%); £3,752,010.60 -> £3,342,745.50 (10.9%); £3,752,010.82 -> £3,342,745.50 (10.9%); £3,752,011.02 -> £3,342,745.49 (10.9%); £3,752,011.18 -> £3,342,745.48 (10.9%); £3,752,011.35 -> £3,342,745.46 (10.9%); £3,752,011.51 -> £3,342,745.44 (10.9%); £3,752,011.66 -> £3,342,745.42 (10.9%); £3,752,011.83 -> £3,342,745.40 (10.9%); £3,752,011.99 -> £3,342,745.37 (10.9%); £3,752,012.15 -> £3,342,745.34 (10.9%); £3,752,012.36 -> £3,342,745.32 (10.9%); £3,752,012.58 -> £3,342,745.29 (10.9%); £3,752,012.79 -> £3,342,745.27 (10.9%); £3,752,013.00 -> £3,342,745.25 (10.9%); £3,752,013.21 -> £3,342,745.24 (10.9%); £3,752,013.41 -> £3,342,745.24 (10.9%); £3,752,013.61 -> £3,342,745.23 (10.9%); £3,752,013.80 -> £3,342,745.23 (10.9%); £3,752,013.96 -> £3,342,745.22 (10.9%); £3,752,014.11 -> £3,342,745.22 (10.9%); £3,752,014.26 -> £3,342,745.22 (10.9%); £3,752,014.40 -> £3,342,745.23 (10.9%); £3,752,014.55 -> £3,342,745.23 (10.9%); £3,752,014.70 -> £3,342,745.23 (10.9%); £3,752,014.84 -> £3,342,745.23 (10.9%); £3,752,014.98 -> £3,342,745.23 (10.9%); £3,752,015.13 -> £3,342,745.24 (10.9%); £3,752,015.28 -> £3,342,745.24 (10.9%); £3,752,015.43 -> £3,342,745.24 (10.9%); £3,752,015.57 -> £3,342,745.24 (10.9%); £3,752,015.71 -> £3,342,745.24 (10.9%); £3,752,015.85 -> £3,342,745.23 (10.9%); £3,752,016.01 -> £3,342,745.28 (10.9%); £3,752,016.19 -> £3,342,745.33 (10.9%); £3,752,016.37 -> £3,342,745.38 (10.9%); £3,752,016.58 -> £3,342,745.43 (10.9%); £3,752,016.80 -> £3,342,745.47 (10.9%); £3,752,017.04 -> £3,342,745.52 (10.9%); £3,752,017.28 -> £3,342,745.55 (10.9%); £3,752,017.53 -> £3,342,745.59 (10.9%); £3,752,017.77 -> £3,342,745.59 (10.9%); £3,752,018.02 -> £3,342,745.59 (10.9%); £3,752,018.26 -> £3,342,745.59 (10.9%); £3,752,018.50 -> £3,342,745.58 (10.9%); £3,752,018.75 -> £3,342,745.58 (10.9%); £3,752,018.98 -> £3,342,745.58 (10.9%); £3,752,019.23 -> £3,342,745.58 (10.9%); £3,752,019.47 -> £3,342,745.58 (10.9%); £3,752,019.72 -> £3,342,745.58 (10.9%); £3,752,019.96 -> £3,342,745.58 (10.9%); £3,752,020.19 -> £3,342,745.61 (10.9%); £3,752,020.38 -> £3,342,745.67 (10.9%); £3,752,020.57 -> £3,342,745.74 (10.9%); £3,752,020.75 -> £3,342,745.80 (10.9%); £3,752,020.93 -> £3,342,745.87 (10.9%); £3,752,021.12 -> £3,342,745.93 (10.9%); £3,752,021.29 -> £3,342,746.02 (10.9%); £3,752,021.47 -> £3,342,746.10 (10.9%); £3,752,021.71 -> £3,342,746.07 (10.9%); £3,752,021.95 -> £3,342,746.05 (10.9%); £3,752,022.18 -> £3,342,746.03 (10.9%); £3,752,022.42 -> £3,342,746.01 (10.9%); £3,752,022.67 -> £3,342,746.00 (10.9%); £3,752,022.91 -> £3,342,745.99 (10.9%); £3,752,023.14 -> £3,342,745.99 (10.9%); £3,752,023.34 -> £3,342,745.98 (10.9%); £3,752,023.53 -> £3,342,745.98 (10.9%); £3,752,023.67 -> £3,342,745.98 (10.9%); £3,752,023.82 -> £3,342,745.98 (10.9%); £3,752,023.96 -> £3,342,745.98 (10.9%); £3,752,024.10 -> £3,342,745.99 (10.9%); £3,752,024.25 -> £3,342,745.99 (10.9%); £3,752,024.39 -> £3,342,745.99 (10.9%); £3,752,024.52 -> £3,342,745.99 (10.9%); £3,752,024.66 -> £3,342,745.99 (10.9%); £3,752,024.81 -> £3,342,746.00 (10.9%); £3,752,024.96 -> £3,342,746.00 (10.9%); £3,752,025.10 -> £3,342,746.00 (10.9%); £3,752,025.24 -> £3,342,746.00 (10.9%); £3,752,025.39 -> £3,342,745.99 (10.9%); £3,752,025.55 -> £3,342,746.03 (10.9%); £3,752,025.73 -> £3,342,746.09 (10.9%); £3,752,025.92 -> £3,342,746.14 (10.9%); £3,752,026.13 -> £3,342,746.19 (10.9%); £3,752,026.36 -> £3,342,746.23 (10.9%); £3,752,026.60 -> £3,342,746.27 (10.9%); £3,752,026.84 -> £3,342,746.31 (10.9%); £3,752,027.07 -> £3,342,746.35 (10.9%); £3,752,027.31 -> £3,342,746.34 (10.9%); £3,752,027.55 -> £3,342,746.34 (10.9%); £3,752,027.79 -> £3,342,746.34 (10.9%); £3,752,028.03 -> £3,342,746.34 (10.9%); £3,752,028.27 -> £3,342,746.34 (10.9%); £3,752,028.49 -> £3,342,746.34 (10.9%); £3,752,028.73 -> £3,342,746.34 (10.9%); £3,752,028.97 -> £3,342,746.33 (10.9%); £3,752,029.20 -> £3,342,746.33 (10.9%); £3,752,029.44 -> £3,342,746.33 (10.9%); £3,752,029.68 -> £3,342,746.37 (10.9%); £3,752,029.87 -> £3,342,746.43 (10.9%); £3,752,030.05 -> £3,342,746.49 (10.9%); £3,752,030.24 -> £3,342,746.56 (10.9%); £3,752,030.49 -> £3,342,746.63 (10.9%); £3,752,030.73 -> £3,342,746.69 (10.9%); £3,752,030.97 -> £3,342,746.78 (10.9%); £3,752,031.16 -> £3,342,746.86 (10.9%); £3,752,031.40 -> £3,342,746.83 (10.9%); £3,752,031.63 -> £3,342,746.81 (10.9%); £3,752,031.88 -> £3,342,746.79 (10.9%); £3,752,032.11 -> £3,342,746.76 (10.9%); £3,752,032.36 -> £3,342,746.76 (10.9%); £3,752,032.60 -> £3,342,746.75 (10.9%); £3,752,032.82 -> £3,342,746.75 (10.9%); £3,752,033.02 -> £3,342,746.74 (10.9%); £3,752,033.21 -> £3,342,746.74 (10.9%); £3,752,033.35 -> £3,342,746.74 (10.9%); £3,752,033.49 -> £3,342,746.74 (10.9%); £3,752,033.63 -> £3,342,746.74 (10.9%); £3,752,033.77 -> £3,342,746.75 (10.9%); £3,752,033.91 -> £3,342,746.75 (10.9%); £3,752,034.05 -> £3,342,746.75 (10.9%); £3,752,034.19 -> £3,342,746.75 (10.9%); £3,752,034.34 -> £3,342,746.75 (10.9%); £3,752,034.48 -> £3,342,746.76 (10.9%); £3,752,034.62 -> £3,342,746.76 (10.9%); £3,752,034.76 -> £3,342,746.76 (10.9%); £3,752,034.90 -> £3,342,746.76 (10.9%); £3,752,035.04 -> £3,342,746.75 (10.9%); £3,752,035.20 -> £3,342,746.80 (10.9%); £3,752,035.37 -> £3,342,746.85 (10.9%); £3,752,035.56 -> £3,342,746.90 (10.9%); £3,752,035.77 -> £3,342,746.95 (10.9%); £3,752,035.98 -> £3,342,747.00 (10.9%); £3,752,036.22 -> £3,342,747.04 (10.9%); £3,752,036.46 -> £3,342,747.08 (10.9%); £3,752,036.69 -> £3,342,747.11 (10.9%); £3,752,036.94 -> £3,342,747.11 (10.9%); £3,752,037.17 -> £3,342,747.11 (10.9%); £3,752,037.40 -> £3,342,747.11 (10.9%); £3,752,037.64 -> £3,342,747.10 (10.9%); £3,752,037.88 -> £3,342,747.10 (10.9%); £3,752,038.12 -> £3,342,747.10 (10.9%); £3,752,038.35 -> £3,342,747.10 (10.9%); £3,752,038.60 -> £3,342,747.10 (10.9%); £3,752,038.84 -> £3,342,747.10 (10.9%); £3,752,039.07 -> £3,342,747.10 (10.9%); £3,752,039.31 -> £3,342,747.13 (10.9%); £3,752,039.48 -> £3,342,747.19 (10.9%); £3,752,039.66 -> £3,342,747.26 (10.9%); £3,752,039.90 -> £3,342,747.33 (10.9%); £3,752,040.14 -> £3,342,747.39 (10.9%); £3,752,040.38 -> £3,342,747.46 (10.9%); £3,752,040.62 -> £3,342,747.55 (10.9%); £3,752,040.86 -> £3,342,747.63 (10.9%); £3,752,041.10 -> £3,342,747.60 (10.9%); £3,752,041.34 -> £3,342,747.58 (10.9%); £3,752,041.57 -> £3,342,747.56 (10.9%); £3,752,041.81 -> £3,342,747.53 (10.9%); £3,752,042.04 -> £3,342,747.53 (10.9%); £3,752,042.27 -> £3,342,747.52 (10.9%); £3,752,042.49 -> £3,342,747.52 (10.9%); £3,752,042.68 -> £3,342,747.51 (10.9%); £3,752,042.86 -> £3,342,747.51 (10.9%); £3,752,043.00 -> £3,342,747.51 (10.9%); £3,752,043.15 -> £3,342,747.51 (10.9%); £3,752,043.29 -> £3,342,747.51 (10.9%); £3,752,043.43 -> £3,342,747.52 (10.9%); £3,752,043.57 -> £3,342,747.52 (10.9%); £3,752,043.71 -> £3,342,747.52 (10.9%); £3,752,043.85 -> £3,342,747.52 (10.9%); £3,752,043.99 -> £3,342,747.52 (10.9%); £3,752,044.14 -> £3,342,747.52 (10.9%); £3,752,044.29 -> £3,342,747.53 (10.9%); £3,752,044.43 -> £3,342,747.53 (10.9%); £3,752,044.58 -> £3,342,747.52 (10.9%); £3,752,044.72 -> £3,342,747.52 (10.9%); £3,752,044.87 -> £3,342,747.56 (10.9%); £3,752,045.04 -> £3,342,747.61 (10.9%); £3,752,045.23 -> £3,342,747.66 (10.9%); £3,752,045.44 -> £3,342,747.71 (10.9%); £3,752,045.66 -> £3,342,747.76 (10.9%); £3,752,045.89 -> £3,342,747.80 (10.9%); £3,752,046.13 -> £3,342,747.84 (10.9%); £3,752,046.36 -> £3,342,747.87 (10.9%); £3,752,046.59 -> £3,342,747.87 (10.9%); £3,752,046.82 -> £3,342,747.87 (10.9%); £3,752,047.05 -> £3,342,747.87 (10.9%); £3,752,047.29 -> £3,342,747.87 (10.9%); £3,752,047.53 -> £3,342,747.86 (10.9%); £3,752,047.77 -> £3,342,747.86 (10.9%); £3,752,048.01 -> £3,342,747.86 (10.9%); £3,752,048.24 -> £3,342,747.86 (10.9%); £3,752,048.48 -> £3,342,747.86 (10.9%); £3,752,048.71 -> £3,342,747.86 (10.9%); £3,752,048.95 -> £3,342,747.90 (10.9%); £3,752,049.13 -> £3,342,747.96 (10.9%); £3,752,049.31 -> £3,342,748.02 (10.9%); £3,752,049.49 -> £3,342,748.09 (10.9%); £3,752,049.66 -> £3,342,748.15 (10.9%); £3,752,049.84 -> £3,342,748.22 (10.9%); £3,752,050.01 -> £3,342,748.30 (10.9%); £3,752,050.19 -> £3,342,748.38 (10.9%); £3,752,050.42 -> £3,342,748.36 (10.9%); £3,752,050.65 -> £3,342,748.33 (10.9%); £3,752,050.89 -> £3,342,748.31 (10.9%); £3,752,051.11 -> £3,342,748.29 (10.9%); £3,752,051.35 -> £3,342,748.28 (10.9%); £3,752,051.59 -> £3,342,748.28 (10.9%); £3,752,051.82 -> £3,342,748.27 (10.9%); £3,752,052.02 -> £3,342,748.27 (10.9%); £3,752,052.21 -> £3,342,748.27 (10.9%); £3,752,052.35 -> £3,342,748.27 (10.9%); £3,752,052.50 -> £3,342,748.27 (10.9%); £3,752,052.64 -> £3,342,748.27 (10.9%); £3,752,052.78 -> £3,342,748.27 (10.9%); £3,752,052.92 -> £3,342,748.28 (10.9%); £3,752,053.07 -> £3,342,748.28 (10.9%); £3,752,053.21 -> £3,342,748.28 (10.9%); £3,752,053.36 -> £3,342,748.28 (10.9%); £3,752,053.50 -> £3,342,748.28 (10.9%); £3,752,053.64 -> £3,342,748.29 (10.9%); £3,752,053.79 -> £3,342,748.29 (10.9%); £3,752,053.93 -> £3,342,748.28 (10.9%); £3,752,054.07 -> £3,342,748.28 (10.9%); £3,752,054.24 -> £3,342,748.32 (10.9%); £3,752,054.41 -> £3,342,748.37 (10.9%); £3,752,054.60 -> £3,342,748.43 (10.9%); £3,752,054.81 -> £3,342,748.47 (10.9%); £3,752,055.03 -> £3,342,748.52 (10.9%); £3,752,055.26 -> £3,342,748.56 (10.9%); £3,752,055.49 -> £3,342,748.60 (10.9%); £3,752,055.73 -> £3,342,748.64 (10.9%); £3,752,055.96 -> £3,342,748.63 (10.9%); £3,752,056.21 -> £3,342,748.63 (10.9%); £3,752,056.45 -> £3,342,748.63 (10.9%); £3,752,056.69 -> £3,342,748.63 (10.9%); £3,752,056.93 -> £3,342,748.63 (10.9%); £3,752,057.17 -> £3,342,748.63 (10.9%); £3,752,057.40 -> £3,342,748.63 (10.9%); £3,752,057.63 -> £3,342,748.63 (10.9%); £3,752,057.87 -> £3,342,748.63 (10.9%); £3,752,058.11 -> £3,342,748.63 (10.9%); £3,752,058.35 -> £3,342,748.66 (10.9%); £3,752,058.59 -> £3,342,748.72 (10.9%); £3,752,058.76 -> £3,342,748.78 (10.9%); £3,752,058.94 -> £3,342,748.85 (10.9%); £3,752,059.12 -> £3,342,748.92 (10.9%); £3,752,059.30 -> £3,342,748.99 (10.9%); £3,752,059.54 -> £3,342,749.07 (10.9%); £3,752,059.79 -> £3,342,749.15 (10.9%); £3,752,060.03 -> £3,342,749.13 (10.9%); £3,752,060.27 -> £3,342,749.10 (10.9%); £3,752,060.52 -> £3,342,749.08 (10.9%); £3,752,060.76 -> £3,342,749.06 (10.9%); £3,752,061.00 -> £3,342,749.05 (10.9%); £3,752,061.24 -> £3,342,749.05 (10.9%); £3,752,061.46 -> £3,342,749.04 (10.9%); £3,752,061.66 -> £3,342,749.04 (10.9%); £3,752,061.85 -> £3,342,749.03 (10.9%); £3,752,061.98 -> £3,342,749.03 (10.9%); £3,752,062.11 -> £3,342,749.03 (10.9%); £3,752,062.24 -> £3,342,749.03 (10.9%); £3,752,062.36 -> £3,342,749.04 (10.9%); £3,752,062.50 -> £3,342,749.04 (10.9%); £3,752,062.62 -> £3,342,749.04 (10.9%); £3,752,062.75 -> £3,342,749.04 (10.9%); £3,752,062.88 -> £3,342,749.04 (10.9%); £3,752,063.00 -> £3,342,749.05 (10.9%); £3,752,063.13 -> £3,342,749.05 (10.9%); £3,752,063.26 -> £3,342,749.05 (10.9%); £3,752,063.39 -> £3,342,749.05 (10.9%); £3,752,063.52 -> £3,342,749.04 (10.9%); £3,752,063.67 -> £3,342,749.04 (10.9%); £3,752,063.83 -> £3,342,749.04 (10.9%); £3,752,064.00 -> £3,342,749.03 (10.9%); £3,752,064.19 -> £3,342,749.02 (10.9%); £3,752,064.39 -> £3,342,749.01 (10.9%); £3,752,064.60 -> £3,342,749.00 (10.9%); £3,752,064.81 -> £3,342,749.00 (10.9%); £3,752,065.03 -> £3,342,749.00 (10.9%); £3,752,065.24 -> £3,342,748.99 (10.9%); £3,752,065.45 -> £3,342,748.99 (10.9%); £3,752,065.67 -> £3,342,748.98 (10.9%); £3,752,065.88 -> £3,342,748.98 (10.9%); £3,752,066.09 -> £3,342,748.97 (10.9%); £3,752,066.31 -> £3,342,748.97 (10.9%); £3,752,066.53 -> £3,342,748.97 (10.9%); £3,752,066.74 -> £3,342,748.96 (10.9%); £3,752,066.96 -> £3,342,748.96 (10.9%); £3,752,067.16 -> £3,342,748.96 (10.9%); £3,752,067.38 -> £3,342,748.96 (10.9%); £3,752,067.55 -> £3,342,748.95 (10.9%); £3,752,067.71 -> £3,342,748.93 (10.9%); £3,752,067.87 -> £3,342,748.91 (10.9%); £3,752,068.03 -> £3,342,748.89 (10.9%); £3,752,068.19 -> £3,342,748.87 (10.9%); £3,752,068.36 -> £3,342,748.84 (10.9%); £3,752,068.52 -> £3,342,748.82 (10.9%); £3,752,068.74 -> £3,342,748.79 (10.9%); £3,752,068.95 -> £3,342,748.77 (10.9%); £3,752,069.16 -> £3,342,748.75 (10.9%); £3,752,069.38 -> £3,342,748.73 (10.9%); £3,752,069.59 -> £3,342,748.72 (10.9%); £3,752,069.81 -> £3,342,748.72 (10.9%); £3,752,070.01 -> £3,342,748.71 (10.9%); £3,752,070.19 -> £3,342,748.71 (10.9%); £3,752,070.36 -> £3,342,748.70 (10.9%); £3,752,070.48 -> £3,342,748.70 (10.9%); £3,752,070.61 -> £3,342,748.70 (10.9%); £3,752,070.74 -> £3,342,748.70 (10.9%); £3,752,070.87 -> £3,342,748.70 (10.9%); £3,752,071.00 -> £3,342,748.70 (10.9%); £3,752,071.13 -> £3,342,748.70 (10.9%); £3,752,071.26 -> £3,342,748.70 (10.9%); £3,752,071.38 -> £3,342,748.71 (10.9%); £3,752,071.51 -> £3,342,748.71 (10.9%); £3,752,071.64 -> £3,342,748.71 (10.9%); £3,752,071.77 -> £3,342,748.71 (10.9%); £3,752,071.90 -> £3,342,748.71 (10.9%); £3,752,072.03 -> £3,342,748.71 (10.9%); £3,752,072.18 -> £3,342,748.71 (10.9%); £3,752,072.33 -> £3,342,748.71 (10.9%); £3,752,072.50 -> £3,342,748.71 (10.9%); £3,752,072.69 -> £3,342,748.70 (10.9%); £3,752,072.89 -> £3,342,748.69 (10.9%); £3,752,073.11 -> £3,342,748.68 (10.9%); £3,752,073.33 -> £3,342,748.67 (10.9%); £3,752,073.55 -> £3,342,748.66 (10.9%); £3,752,073.76 -> £3,342,748.65 (10.9%); £3,752,073.97 -> £3,342,748.65 (10.9%); £3,752,074.18 -> £3,342,748.64 (10.9%); £3,752,074.40 -> £3,342,748.63 (10.9%); £3,752,074.61 -> £3,342,748.62 (10.9%); £3,752,074.83 -> £3,342,748.61 (10.9%); £3,752,075.04 -> £3,342,748.60 (10.9%); £3,752,075.26 -> £3,342,748.60 (10.9%); £3,752,075.47 -> £3,342,748.59 (10.9%); £3,752,075.70 -> £3,342,748.59 (10.9%); £3,752,075.92 -> £3,342,748.59 (10.9%); £3,752,076.07 -> £3,342,748.57 (10.9%); £3,752,076.23 -> £3,342,748.55 (10.9%); £3,752,076.39 -> £3,342,748.54 (10.9%); £3,752,076.55 -> £3,342,748.52 (10.9%); £3,752,076.71 -> £3,342,748.50 (10.9%); £3,752,076.87 -> £3,342,748.47 (10.9%); £3,752,077.02 -> £3,342,748.44 (10.9%); £3,752,077.25 -> £3,342,748.41 (10.9%); £3,752,077.46 -> £3,342,748.39 (10.9%); £3,752,077.68 -> £3,342,748.37 (10.9%); £3,752,077.89 -> £3,342,748.34 (10.9%); £3,752,078.10 -> £3,342,748.34 (10.9%); £3,752,078.32 -> £3,342,748.33 (10.9%); £3,752,078.51 -> £3,342,748.33 (10.9%); £3,752,078.69 -> £3,342,748.32 (10.9%); £3,752,078.85 -> £3,342,748.32 (10.9%); £3,752,079.00 -> £3,342,748.32 (10.9%); £3,752,079.15 -> £3,342,748.32 (10.9%); £3,752,079.30 -> £3,342,748.32 (10.9%); £3,752,079.44 -> £3,342,748.32 (10.9%); £3,752,079.58 -> £3,342,748.33 (10.9%); £3,752,079.74 -> £3,342,748.33 (10.9%); £3,752,079.88 -> £3,342,748.33 (10.9%); £3,752,080.03 -> £3,342,748.33 (10.9%); £3,752,080.17 -> £3,342,748.33 (10.9%); £3,752,080.32 -> £3,342,748.34 (10.9%); £3,752,080.46 -> £3,342,748.34 (10.9%); £3,752,080.61 -> £3,342,748.33 (10.9%); £3,752,080.75 -> £3,342,748.33 (10.9%); £3,752,080.92 -> £3,342,748.37 (10.9%); £3,752,081.10 -> £3,342,748.42 (10.9%); £3,752,081.29 -> £3,342,748.48 (10.9%); £3,752,081.51 -> £3,342,748.53 (10.9%); £3,752,081.74 -> £3,342,748.57 (10.9%); £3,752,081.99 -> £3,342,748.61 (10.9%); £3,752,082.24 -> £3,342,748.65 (10.9%); £3,752,082.49 -> £3,342,748.69 (10.9%); £3,752,082.74 -> £3,342,748.69 (10.9%); £3,752,082.98 -> £3,342,748.68 (10.9%); £3,752,083.23 -> £3,342,748.68 (10.9%); £3,752,083.48 -> £3,342,748.68 (10.9%); £3,752,083.73 -> £3,342,748.68 (10.9%); £3,752,083.98 -> £3,342,748.68 (10.9%); £3,752,084.23 -> £3,342,748.68 (10.9%); £3,752,084.48 -> £3,342,748.68 (10.9%); £3,752,084.73 -> £3,342,748.68 (10.9%); £3,752,084.97 -> £3,342,748.68 (10.9%); £3,752,085.22 -> £3,342,748.71 (10.9%); £3,752,085.47 -> £3,342,748.77 (10.9%); £3,752,085.65 -> £3,342,748.84 (10.9%); £3,752,085.83 -> £3,342,748.90 (10.9%); £3,752,086.02 -> £3,342,748.97 (10.9%); £3,752,086.20 -> £3,342,749.04 (10.9%); £3,752,086.38 -> £3,342,749.12 (10.9%); £3,752,086.56 -> £3,342,749.20 (10.9%); £3,752,086.80 -> £3,342,749.18 (10.9%); £3,752,087.05 -> £3,342,749.15 (10.9%); £3,752,087.29 -> £3,342,749.13 (10.9%); £3,752,087.54 -> £3,342,749.11 (10.9%); £3,752,087.79 -> £3,342,749.10 (10.9%); £3,752,088.03 -> £3,342,749.10 (10.9%); £3,752,088.26 -> £3,342,749.10 (10.9%); £3,752,088.47 -> £3,342,749.09 (10.9%); £3,752,088.66 -> £3,342,749.09 (10.9%); £3,752,088.81 -> £3,342,749.09 (10.9%); £3,752,088.96 -> £3,342,749.09 (10.9%); £3,752,089.10 -> £3,342,749.09 (10.9%); £3,752,089.25 -> £3,342,749.10 (10.9%); £3,752,089.40 -> £3,342,749.10 (10.9%); £3,752,089.55 -> £3,342,749.10 (10.9%); £3,752,089.70 -> £3,342,749.10 (10.9%); £3,752,089.84 -> £3,342,749.11 (10.9%); £3,752,089.99 -> £3,342,749.11 (10.9%); £3,752,090.13 -> £3,342,749.11 (10.9%); £3,752,090.29 -> £3,342,749.11 (10.9%); £3,752,090.44 -> £3,342,749.11 (10.9%); £3,752,090.58 -> £3,342,749.10 (10.9%); £3,752,090.75 -> £3,342,749.15 (10.9%); £3,752,090.93 -> £3,342,749.20 (10.9%); £3,752,091.13 -> £3,342,749.25 (10.9%); £3,752,091.34 -> £3,342,749.30 (10.9%); £3,752,091.58 -> £3,342,749.35 (10.9%); £3,752,091.82 -> £3,342,749.39 (10.9%); £3,752,092.07 -> £3,342,749.43 (10.9%); £3,752,092.31 -> £3,342,749.46 (10.9%); £3,752,092.56 -> £3,342,749.46 (10.9%); £3,752,092.81 -> £3,342,749.46 (10.9%); £3,752,093.06 -> £3,342,749.46 (10.9%); £3,752,093.30 -> £3,342,749.46 (10.9%); £3,752,093.55 -> £3,342,749.46 (10.9%); £3,752,093.80 -> £3,342,749.46 (10.9%); £3,752,094.04 -> £3,342,749.46 (10.9%); £3,752,094.28 -> £3,342,749.46 (10.9%); £3,752,094.53 -> £3,342,749.45 (10.9%); £3,752,094.78 -> £3,342,749.46 (10.9%); £3,752,095.02 -> £3,342,749.49 (10.9%); £3,752,095.21 -> £3,342,749.55 (10.9%); £3,752,095.39 -> £3,342,749.62 (10.9%); £3,752,095.65 -> £3,342,749.68 (10.9%); £3,752,095.90 -> £3,342,749.75 (10.9%); £3,752,096.14 -> £3,342,749.82 (10.9%); £3,752,096.39 -> £3,342,749.90 (10.9%); £3,752,096.57 -> £3,342,749.98 (10.9%); £3,752,096.83 -> £3,342,749.96 (10.9%); £3,752,097.07 -> £3,342,749.93 (10.9%); £3,752,097.32 -> £3,342,749.91 (10.9%); £3,752,097.57 -> £3,342,749.89 (10.9%); £3,752,097.82 -> £3,342,749.88 (10.9%); £3,752,098.07 -> £3,342,749.88 (10.9%); £3,752,098.30 -> £3,342,749.87 (10.9%); £3,752,098.50 -> £3,342,749.87 (10.9%); £3,752,098.70 -> £3,342,749.87 (10.9%); £3,752,098.85 -> £3,342,749.87 (10.9%); £3,752,098.99 -> £3,342,749.87 (10.9%); £3,752,099.14 -> £3,342,749.87 (10.9%); £3,752,099.29 -> £3,342,749.88 (10.9%); £3,752,099.44 -> £3,342,749.88 (10.9%); £3,752,099.59 -> £3,342,749.88 (10.9%); £3,752,099.73 -> £3,342,749.88 (10.9%); £3,752,099.88 -> £3,342,749.89 (10.9%); £3,752,100.03 -> £3,342,749.89 (10.9%); £3,752,100.18 -> £3,342,749.89 (10.9%); £3,752,100.34 -> £3,342,749.89 (10.9%); £3,752,100.49 -> £3,342,749.89 (10.9%); £3,752,100.64 -> £3,342,749.88 (10.9%); £3,752,100.81 -> £3,342,749.93 (10.9%); £3,752,101.00 -> £3,342,749.98 (10.9%); £3,752,101.19 -> £3,342,750.03 (10.9%); £3,752,101.41 -> £3,342,750.08 (10.9%); £3,752,101.64 -> £3,342,750.13 (10.9%); £3,752,101.89 -> £3,342,750.17 (10.9%); £3,752,102.14 -> £3,342,750.21 (10.9%); £3,752,102.39 -> £3,342,750.24 (10.9%); £3,752,102.64 -> £3,342,750.24 (10.9%); £3,752,102.90 -> £3,342,750.24 (10.9%); £3,752,103.14 -> £3,342,750.24 (10.9%); £3,752,103.39 -> £3,342,750.24 (10.9%); £3,752,103.64 -> £3,342,750.24 (10.9%); £3,752,103.90 -> £3,342,750.24 (10.9%); £3,752,104.16 -> £3,342,750.24 (10.9%); £3,752,104.42 -> £3,342,750.24 (10.9%); £3,752,104.67 -> £3,342,750.23 (10.9%); £3,752,104.92 -> £3,342,750.24 (10.9%); £3,752,105.17 -> £3,342,750.27 (10.9%); £3,752,105.42 -> £3,342,750.33 (10.9%); £3,752,105.60 -> £3,342,750.40 (10.9%); £3,752,105.79 -> £3,342,750.46 (10.9%); £3,752,106.04 -> £3,342,750.53 (10.9%); £3,752,106.29 -> £3,342,750.60 (10.9%); £3,752,106.55 -> £3,342,750.68 (10.9%); £3,752,106.74 -> £3,342,750.77 (10.9%); £3,752,107.00 -> £3,342,750.74 (10.9%); £3,752,107.25 -> £3,342,750.72 (10.9%); £3,752,107.50 -> £3,342,750.70 (10.9%); £3,752,107.75 -> £3,342,750.68 (10.9%); £3,752,108.01 -> £3,342,750.67 (10.9%); £3,752,108.26 -> £3,342,750.66 (10.9%); £3,752,108.49 -> £3,342,750.66 (10.9%); £3,752,108.71 -> £3,342,750.65 (10.9%); £3,752,108.90 -> £3,342,750.65 (10.9%); £3,752,109.05 -> £3,342,750.65 (10.9%); £3,752,109.21 -> £3,342,750.65 (10.9%); £3,752,109.36 -> £3,342,750.66 (10.9%); £3,752,109.52 -> £3,342,750.66 (10.9%); £3,752,109.67 -> £3,342,750.66 (10.9%); £3,752,109.83 -> £3,342,750.66 (10.9%); £3,752,109.98 -> £3,342,750.66 (10.9%); £3,752,110.14 -> £3,342,750.67 (10.9%); £3,752,110.30 -> £3,342,750.67 (10.9%); £3,752,110.44 -> £3,342,750.67 (10.9%); £3,752,110.60 -> £3,342,750.67 (10.9%); £3,752,110.75 -> £3,342,750.67 (10.9%); £3,752,110.91 -> £3,342,750.66 (10.9%); £3,752,111.08 -> £3,342,750.71 (10.9%); £3,752,111.27 -> £3,342,750.76 (10.9%); £3,752,111.47 -> £3,342,750.81 (10.9%); £3,752,111.68 -> £3,342,750.86 (10.9%); £3,752,111.92 -> £3,342,750.90 (10.9%); £3,752,112.17 -> £3,342,750.95 (10.9%); £3,752,112.43 -> £3,342,750.98 (10.9%); £3,752,112.69 -> £3,342,751.02 (10.9%); £3,752,112.93 -> £3,342,751.02 (10.9%); £3,752,113.19 -> £3,342,751.02 (10.9%); £3,752,113.44 -> £3,342,751.02 (10.9%); £3,752,113.70 -> £3,342,751.01 (10.9%); £3,752,113.96 -> £3,342,751.01 (10.9%); £3,752,114.21 -> £3,342,751.01 (10.9%); £3,752,114.47 -> £3,342,751.01 (10.9%); £3,752,114.73 -> £3,342,751.01 (10.9%); £3,752,114.98 -> £3,342,751.01 (10.9%); £3,752,115.24 -> £3,342,751.01 (10.9%); £3,752,115.50 -> £3,342,751.05 (10.9%); £3,752,115.69 -> £3,342,751.11 (10.9%); £3,752,115.88 -> £3,342,751.17 (10.9%); £3,752,116.07 -> £3,342,751.24 (10.9%); £3,752,116.25 -> £3,342,751.30 (10.9%); £3,752,116.51 -> £3,342,751.37 (10.9%); £3,752,116.76 -> £3,342,751.45 (10.9%); £3,752,116.96 -> £3,342,751.54 (10.9%); £3,752,117.22 -> £3,342,751.51 (10.9%); £3,752,117.48 -> £3,342,751.49 (10.9%); £3,752,117.74 -> £3,342,751.46 (10.9%); £3,752,117.99 -> £3,342,751.44 (10.9%); £3,752,118.24 -> £3,342,751.43 (10.9%); £3,752,118.50 -> £3,342,751.43 (10.9%); £3,752,118.74 -> £3,342,751.42 (10.9%); £3,752,118.95 -> £3,342,751.42 (10.9%); £3,752,119.16 -> £3,342,751.42 (10.9%); £3,752,119.31 -> £3,342,751.42 (10.9%); £3,752,119.46 -> £3,342,751.42 (10.9%); £3,752,119.61 -> £3,342,751.42 (10.9%); £3,752,119.76 -> £3,342,751.42 (10.9%); £3,752,119.91 -> £3,342,751.43 (10.9%); £3,752,120.06 -> £3,342,751.43 (10.9%); £3,752,120.22 -> £3,342,751.43 (10.9%); £3,752,120.37 -> £3,342,751.43 (10.9%); £3,752,120.53 -> £3,342,751.44 (10.9%); £3,752,120.68 -> £3,342,751.44 (10.9%); £3,752,120.83 -> £3,342,751.44 (10.9%); £3,752,120.99 -> £3,342,751.43 (10.9%); £3,752,121.15 -> £3,342,751.43 (10.9%); £3,752,121.31 -> £3,342,751.47 (10.9%); £3,752,121.50 -> £3,342,751.53 (10.9%); £3,752,121.71 -> £3,342,751.58 (10.9%); £3,752,121.93 -> £3,342,751.63 (10.9%); £3,752,122.17 -> £3,342,751.67 (10.9%); £3,752,122.43 -> £3,342,751.72 (10.9%); £3,752,122.70 -> £3,342,751.75 (10.9%); £3,752,122.96 -> £3,342,751.79 (10.9%); £3,752,123.22 -> £3,342,751.79 (10.9%); £3,752,123.48 -> £3,342,751.79 (10.9%); £3,752,123.73 -> £3,342,751.79 (10.9%); £3,752,123.97 -> £3,342,751.79 (10.9%); £3,752,124.23 -> £3,342,751.79 (10.9%); £3,752,124.48 -> £3,342,751.79 (10.9%); £3,752,124.75 -> £3,342,751.79 (10.9%); £3,752,125.01 -> £3,342,751.79 (10.9%); £3,752,125.25 -> £3,342,751.79 (10.9%); £3,752,125.51 -> £3,342,751.79 (10.9%); £3,752,125.76 -> £3,342,751.82 (10.9%); £3,752,125.96 -> £3,342,751.88 (10.9%); £3,752,126.15 -> £3,342,751.95 (10.9%); £3,752,126.35 -> £3,342,752.01 (10.9%); £3,752,126.54 -> £3,342,752.08 (10.9%); £3,752,126.74 -> £3,342,752.15 (10.9%); £3,752,126.93 -> £3,342,752.23 (10.9%); £3,752,127.13 -> £3,342,752.31 (10.9%); £3,752,127.38 -> £3,342,752.29 (10.9%); £3,752,127.64 -> £3,342,752.27 (10.9%); £3,752,127.89 -> £3,342,752.24 (10.9%); £3,752,128.15 -> £3,342,752.22 (10.9%); £3,752,128.41 -> £3,342,752.22 (10.9%); £3,752,128.66 -> £3,342,752.21 (10.9%); £3,752,128.90 -> £3,342,752.21 (10.9%); £3,752,129.11 -> £3,342,752.20 (10.9%); £3,752,129.31 -> £3,342,752.20 (10.9%); £3,752,129.46 -> £3,342,752.20 (10.9%); £3,752,129.59 -> £3,342,752.20 (10.9%); £3,752,129.73 -> £3,342,752.20 (10.9%); £3,752,129.87 -> £3,342,752.20 (10.9%); £3,752,130.02 -> £3,342,752.20 (10.9%); £3,752,130.16 -> £3,342,752.21 (10.9%); £3,752,130.30 -> £3,342,752.21 (10.9%); £3,752,130.44 -> £3,342,752.21 (10.9%); £3,752,130.57 -> £3,342,752.21 (10.9%); £3,752,130.71 -> £3,342,752.22 (10.9%); £3,752,130.85 -> £3,342,752.22 (10.9%); £3,752,130.98 -> £3,342,752.22 (10.9%); £3,752,131.13 -> £3,342,752.21 (10.9%); £3,752,131.28 -> £3,342,752.21 (10.9%); £3,752,131.46 -> £3,342,752.21 (10.9%); £3,752,131.65 -> £3,342,752.20 (10.9%); £3,752,131.84 -> £3,342,752.19 (10.9%); £3,752,132.06 -> £3,342,752.18 (10.9%); £3,752,132.29 -> £3,342,752.17 (10.9%); £3,752,132.53 -> £3,342,752.17 (10.9%); £3,752,132.76 -> £3,342,752.17 (10.9%); £3,752,132.99 -> £3,342,752.16 (10.9%); £3,752,133.23 -> £3,342,752.16 (10.9%); £3,752,133.45 -> £3,342,752.15 (10.9%); £3,752,133.68 -> £3,342,752.15 (10.9%); £3,752,133.91 -> £3,342,752.15 (10.9%); £3,752,134.15 -> £3,342,752.15 (10.9%); £3,752,134.38 -> £3,342,752.14 (10.9%); £3,752,134.61 -> £3,342,752.14 (10.9%); £3,752,134.84 -> £3,342,752.14 (10.9%); £3,752,135.07 -> £3,342,752.14 (10.9%); £3,752,135.30 -> £3,342,752.14 (10.9%); £3,752,135.47 -> £3,342,752.13 (10.9%); £3,752,135.65 -> £3,342,752.11 (10.9%); £3,752,135.82 -> £3,342,752.09 (10.9%); £3,752,135.99 -> £3,342,752.07 (10.9%); £3,752,136.17 -> £3,342,752.05 (10.9%); £3,752,136.40 -> £3,342,752.03 (10.9%); £3,752,136.63 -> £3,342,752.00 (10.9%); £3,752,136.86 -> £3,342,751.97 (10.9%); £3,752,137.09 -> £3,342,751.95 (10.9%); £3,752,137.32 -> £3,342,751.93 (10.9%); £3,752,137.55 -> £3,342,751.91 (10.9%); £3,752,137.78 -> £3,342,751.91 (10.9%); £3,752,138.01 -> £3,342,751.90 (10.9%); £3,752,138.22 -> £3,342,751.90 (10.9%); £3,752,138.41 -> £3,342,751.89 (10.9%); £3,752,138.59 -> £3,342,751.89 (10.9%); £3,752,138.72 -> £3,342,751.89 (10.9%); £3,752,138.87 -> £3,342,751.89 (10.9%); £3,752,139.01 -> £3,342,751.89 (10.9%); £3,752,139.15 -> £3,342,751.89 (10.9%); £3,752,139.29 -> £3,342,751.89 (10.9%); £3,752,139.44 -> £3,342,751.89 (10.9%); £3,752,139.57 -> £3,342,751.89 (10.9%); £3,752,139.72 -> £3,342,751.90 (10.9%); £3,752,139.86 -> £3,342,751.90 (10.9%); £3,752,139.99 -> £3,342,751.90 (10.9%); £3,752,140.13 -> £3,342,751.90 (10.9%); £3,752,140.27 -> £3,342,751.90 (10.9%); £3,752,140.41 -> £3,342,751.90 (10.9%); £3,752,140.56 -> £3,342,751.90 (10.9%); £3,752,140.74 -> £3,342,751.90 (10.9%); £3,752,140.92 -> £3,342,751.90 (10.9%); £3,752,141.13 -> £3,342,751.89 (10.9%); £3,752,141.35 -> £3,342,751.88 (10.9%); £3,752,141.58 -> £3,342,751.87 (10.9%); £3,752,141.82 -> £3,342,751.86 (10.9%); £3,752,142.05 -> £3,342,751.85 (10.9%); £3,752,142.28 -> £3,342,751.85 (10.9%); £3,752,142.52 -> £3,342,751.84 (10.9%); £3,752,142.75 -> £3,342,751.83 (10.9%); £3,752,142.98 -> £3,342,751.82 (10.9%); £3,752,143.21 -> £3,342,751.81 (10.9%); £3,752,143.44 -> £3,342,751.80 (10.9%); £3,752,143.67 -> £3,342,751.80 (10.9%); £3,752,143.91 -> £3,342,751.79 (10.9%); £3,752,144.14 -> £3,342,751.78 (10.9%); £3,752,144.37 -> £3,342,751.78 (10.9%); £3,752,144.60 -> £3,342,751.78 (10.9%); £3,752,144.77 -> £3,342,751.76 (10.9%); £3,752,144.94 -> £3,342,751.75 (10.9%); £3,752,145.11 -> £3,342,751.73 (10.9%); £3,752,145.29 -> £3,342,751.71 (10.9%); £3,752,145.52 -> £3,342,751.69 (10.9%); £3,752,145.76 -> £3,342,751.66 (10.9%); £3,752,145.93 -> £3,342,751.63 (10.9%); £3,752,146.17 -> £3,342,751.61 (10.9%); £3,752,146.40 -> £3,342,751.58 (10.9%); £3,752,146.64 -> £3,342,751.56 (10.9%); £3,752,146.88 -> £3,342,751.54 (10.9%); £3,752,147.11 -> £3,342,751.53 (10.9%); £3,752,147.35 -> £3,342,751.53 (10.9%); £3,752,147.55 -> £3,342,751.52 (10.9%); £3,752,147.75 -> £3,342,751.52 (10.9%); £3,752,147.92 -> £3,342,751.51 (10.9%); £3,752,148.08 -> £3,342,751.51 (10.9%); £3,752,148.24 -> £3,342,751.51 (10.9%); £3,752,148.40 -> £3,342,751.52 (10.9%); £3,752,148.56 -> £3,342,751.52 (10.9%); £3,752,148.72 -> £3,342,751.52 (10.9%); £3,752,148.88 -> £3,342,751.52 (10.9%); £3,752,149.04 -> £3,342,751.52 (10.9%); £3,752,149.20 -> £3,342,751.53 (10.9%); £3,752,149.36 -> £3,342,751.53 (10.9%); £3,752,149.53 -> £3,342,751.53 (10.9%); £3,752,149.69 -> £3,342,751.53 (10.9%); £3,752,149.85 -> £3,342,751.53 (10.9%); £3,752,150.01 -> £3,342,751.52 (10.9%); £3,752,150.20 -> £3,342,751.57 (10.9%); £3,752,150.39 -> £3,342,751.62 (10.9%); £3,752,150.61 -> £3,342,751.67 (10.9%); £3,752,150.84 -> £3,342,751.72 (10.9%); £3,752,151.10 -> £3,342,751.76 (10.9%); £3,752,151.37 -> £3,342,751.81 (10.9%); £3,752,151.64 -> £3,342,751.84 (10.9%); £3,752,151.90 -> £3,342,751.88 (10.9%); £3,752,152.18 -> £3,342,751.88 (10.9%); £3,752,152.44 -> £3,342,751.88 (10.9%); £3,752,152.71 -> £3,342,751.87 (10.9%); £3,752,152.97 -> £3,342,751.87 (10.9%); £3,752,153.23 -> £3,342,751.87 (10.9%); £3,752,153.49 -> £3,342,751.87 (10.9%); £3,752,153.75 -> £3,342,751.87 (10.9%); £3,752,154.01 -> £3,342,751.87 (10.9%); £3,752,154.28 -> £3,342,751.87 (10.9%); £3,752,154.55 -> £3,342,751.87 (10.9%); £3,752,154.82 -> £3,342,751.90 (10.9%); £3,752,155.09 -> £3,342,751.96 (10.9%); £3,752,155.36 -> £3,342,752.03 (10.9%); £3,752,155.64 -> £3,342,752.10 (10.9%); £3,752,155.91 -> £3,342,752.16 (10.9%); £3,752,156.18 -> £3,342,752.23 (10.9%); £3,752,156.45 -> £3,342,752.31 (10.9%); £3,752,156.65 -> £3,342,752.40 (10.9%); £3,752,156.92 -> £3,342,752.37 (10.9%); £3,752,157.19 -> £3,342,752.35 (10.9%); £3,752,157.46 -> £3,342,752.32 (10.9%); £3,752,157.72 -> £3,342,752.30 (10.9%); £3,752,157.99 -> £3,342,752.29 (10.9%); £3,752,158.26 -> £3,342,752.29 (10.9%); £3,752,158.50 -> £3,342,752.28 (10.9%); £3,752,158.74 -> £3,342,752.28 (10.9%); £3,752,158.94 -> £3,342,752.28 (10.9%); £3,752,159.10 -> £3,342,752.28 (10.9%); £3,752,159.26 -> £3,342,752.28 (10.9%); £3,752,159.42 -> £3,342,752.28 (10.9%); £3,752,159.58 -> £3,342,752.28 (10.9%); £3,752,159.74 -> £3,342,752.28 (10.9%); £3,752,159.90 -> £3,342,752.29 (10.9%); £3,752,160.06 -> £3,342,752.29 (10.9%); £3,752,160.21 -> £3,342,752.29 (10.9%); £3,752,160.37 -> £3,342,752.29 (10.9%); £3,752,160.53 -> £3,342,752.30 (10.9%); £3,752,160.69 -> £3,342,752.30 (10.9%); £3,752,160.85 -> £3,342,752.29 (10.9%); £3,752,161.00 -> £3,342,752.29 (10.9%); £3,752,161.18 -> £3,342,752.33 (10.9%); £3,752,161.37 -> £3,342,752.39 (10.9%); £3,752,161.58 -> £3,342,752.44 (10.9%); £3,752,161.81 -> £3,342,752.49 (10.9%); £3,752,162.07 -> £3,342,752.53 (10.9%); £3,752,162.33 -> £3,342,752.58 (10.9%); £3,752,162.60 -> £3,342,752.62 (10.9%); £3,752,162.87 -> £3,342,752.65 (10.9%); £3,752,163.13 -> £3,342,752.65 (10.9%); £3,752,163.40 -> £3,342,752.65 (10.9%); £3,752,163.67 -> £3,342,752.65 (10.9%); £3,752,163.93 -> £3,342,752.65 (10.9%); £3,752,164.19 -> £3,342,752.64 (10.9%); £3,752,164.45 -> £3,342,752.64 (10.9%); £3,752,164.72 -> £3,342,752.64 (10.9%); £3,752,165.00 -> £3,342,752.64 (10.9%); £3,752,165.26 -> £3,342,752.64 (10.9%); £3,752,165.52 -> £3,342,752.64 (10.9%); £3,752,165.79 -> £3,342,752.68 (10.9%); £3,752,165.99 -> £3,342,752.74 (10.9%); £3,752,166.18 -> £3,342,752.80 (10.9%); £3,752,166.45 -> £3,342,752.87 (10.9%); £3,752,166.72 -> £3,342,752.94 (10.9%); £3,752,166.92 -> £3,342,753.00 (10.9%); £3,752,167.12 -> £3,342,753.09 (10.9%); £3,752,167.32 -> £3,342,753.17 (10.9%); £3,752,167.58 -> £3,342,753.14 (10.9%); £3,752,167.84 -> £3,342,753.12 (10.9%); £3,752,168.10 -> £3,342,753.10 (10.9%); £3,752,168.36 -> £3,342,753.08 (10.9%); £3,752,168.62 -> £3,342,753.07 (10.9%); £3,752,168.89 -> £3,342,753.06 (10.9%); £3,752,169.13 -> £3,342,753.06 (10.9%); £3,752,169.35 -> £3,342,753.06 (10.9%); £3,752,169.55 -> £3,342,753.05 (10.9%); £3,752,169.71 -> £3,342,753.06 (10.9%); £3,752,169.87 -> £3,342,753.06 (10.9%); £3,752,170.03 -> £3,342,753.06 (10.9%); £3,752,170.19 -> £3,342,753.06 (10.9%); £3,752,170.35 -> £3,342,753.06 (10.9%); £3,752,170.51 -> £3,342,753.06 (10.9%); £3,752,170.66 -> £3,342,753.07 (10.9%); £3,752,170.83 -> £3,342,753.07 (10.9%); £3,752,170.99 -> £3,342,753.07 (10.9%); £3,752,171.15 -> £3,342,753.07 (10.9%); £3,752,171.31 -> £3,342,753.07 (10.9%); £3,752,171.46 -> £3,342,753.07 (10.9%); £3,752,171.62 -> £3,342,753.06 (10.9%); £3,752,171.80 -> £3,342,753.11 (10.9%); £3,752,171.99 -> £3,342,753.16 (10.9%); £3,752,172.20 -> £3,342,753.22 (10.9%); £3,752,172.42 -> £3,342,753.27 (10.9%); £3,752,172.68 -> £3,342,753.31 (10.9%); £3,752,172.95 -> £3,342,753.36 (10.9%); £3,752,173.22 -> £3,342,753.39 (10.9%); £3,752,173.48 -> £3,342,753.43 (10.9%); £3,752,173.75 -> £3,342,753.43 (10.9%); £3,752,174.02 -> £3,342,753.42 (10.9%); £3,752,174.28 -> £3,342,753.42 (10.9%); £3,752,174.54 -> £3,342,753.42 (10.9%); £3,752,174.80 -> £3,342,753.42 (10.9%); £3,752,175.06 -> £3,342,753.42 (10.9%); £3,752,175.33 -> £3,342,753.42 (10.9%); £3,752,175.60 -> £3,342,753.42 (10.9%); £3,752,175.86 -> £3,342,753.42 (10.9%); £3,752,176.12 -> £3,342,753.42 (10.9%); £3,752,176.39 -> £3,342,753.45 (10.9%); £3,752,176.65 -> £3,342,753.51 (10.9%); £3,752,176.91 -> £3,342,753.58 (10.9%); £3,752,177.12 -> £3,342,753.64 (10.9%); £3,752,177.32 -> £3,342,753.71 (10.9%); £3,752,177.52 -> £3,342,753.78 (10.9%); £3,752,177.79 -> £3,342,753.86 (10.9%); £3,752,178.06 -> £3,342,753.94 (10.9%); £3,752,178.32 -> £3,342,753.92 (10.9%); £3,752,178.58 -> £3,342,753.90 (10.9%); £3,752,178.85 -> £3,342,753.87 (10.9%); £3,752,179.12 -> £3,342,753.85 (10.9%); £3,752,179.39 -> £3,342,753.85 (10.9%); £3,752,179.65 -> £3,342,753.84 (10.9%); £3,752,179.89 -> £3,342,753.84 (10.9%); £3,752,180.12 -> £3,342,753.83 (10.9%); £3,752,180.32 -> £3,342,753.83 (10.9%); £3,752,180.48 -> £3,342,753.83 (10.9%); £3,752,180.64 -> £3,342,753.83 (10.9%); £3,752,180.80 -> £3,342,753.83 (10.9%); £3,752,180.96 -> £3,342,753.84 (10.9%); £3,752,181.12 -> £3,342,753.84 (10.9%); £3,752,181.28 -> £3,342,753.84 (10.9%); £3,752,181.43 -> £3,342,753.84 (10.9%); £3,752,181.59 -> £3,342,753.85 (10.9%); £3,752,181.75 -> £3,342,753.85 (10.9%); £3,752,181.91 -> £3,342,753.85 (10.9%); £3,752,182.07 -> £3,342,753.85 (10.9%); £3,752,182.24 -> £3,342,753.85 (10.9%); £3,752,182.40 -> £3,342,753.84 (10.9%); £3,752,182.57 -> £3,342,753.89 (10.9%); £3,752,182.76 -> £3,342,753.94 (10.9%); £3,752,182.98 -> £3,342,753.99 (10.9%); £3,752,183.20 -> £3,342,754.04 (10.9%); £3,752,183.44 -> £3,342,754.09 (10.9%); £3,752,183.71 -> £3,342,754.13 (10.9%); £3,752,183.96 -> £3,342,754.17 (10.9%); £3,752,184.23 -> £3,342,754.21 (10.9%); £3,752,184.49 -> £3,342,754.20 (10.9%); £3,752,184.75 -> £3,342,754.20 (10.9%); £3,752,185.01 -> £3,342,754.20 (10.9%); £3,752,185.28 -> £3,342,754.20 (10.9%); £3,752,185.54 -> £3,342,754.20 (10.9%); £3,752,185.82 -> £3,342,754.20 (10.9%); £3,752,186.08 -> £3,342,754.20 (10.9%); £3,752,186.34 -> £3,342,754.20 (10.9%); £3,752,186.61 -> £3,342,754.20 (10.9%); £3,752,186.88 -> £3,342,754.20 (10.9%); £3,752,187.15 -> £3,342,754.23 (10.9%); £3,752,187.42 -> £3,342,754.29 (10.9%); £3,752,187.62 -> £3,342,754.36 (10.9%); £3,752,187.81 -> £3,342,754.42 (10.9%); £3,752,188.01 -> £3,342,754.49 (10.9%); £3,752,188.20 -> £3,342,754.56 (10.9%); £3,752,188.40 -> £3,342,754.64 (10.9%); £3,752,188.67 -> £3,342,754.72 (10.9%); £3,752,188.93 -> £3,342,754.70 (10.9%); £3,752,189.20 -> £3,342,754.67 (10.9%); £3,752,189.46 -> £3,342,754.65 (10.9%); £3,752,189.72 -> £3,342,754.63 (10.9%); £3,752,189.99 -> £3,342,754.62 (10.9%); £3,752,190.26 -> £3,342,754.62 (10.9%); £3,752,190.50 -> £3,342,754.61 (10.9%); £3,752,190.72 -> £3,342,754.61 (10.9%); £3,752,190.93 -> £3,342,754.61 (10.9%); £3,752,191.09 -> £3,342,754.61 (10.9%); £3,752,191.24 -> £3,342,754.61 (10.9%); £3,752,191.40 -> £3,342,754.61 (10.9%); £3,752,191.56 -> £3,342,754.61 (10.9%); £3,752,191.72 -> £3,342,754.61 (10.9%); £3,752,191.88 -> £3,342,754.62 (10.9%); £3,752,192.03 -> £3,342,754.62 (10.9%); £3,752,192.20 -> £3,342,754.62 (10.9%); £3,752,192.36 -> £3,342,754.62 (10.9%); £3,752,192.51 -> £3,342,754.62 (10.9%); £3,752,192.67 -> £3,342,754.63 (10.9%); £3,752,192.83 -> £3,342,754.62 (10.9%); £3,752,192.99 -> £3,342,754.62 (10.9%); £3,752,193.16 -> £3,342,754.66 (10.9%); £3,752,193.36 -> £3,342,754.71 (10.9%); £3,752,193.57 -> £3,342,754.77 (10.9%); £3,752,193.80 -> £3,342,754.81 (10.9%); £3,752,194.05 -> £3,342,754.86 (10.9%); £3,752,194.32 -> £3,342,754.90 (10.9%); £3,752,194.59 -> £3,342,754.94 (10.9%); £3,752,194.87 -> £3,342,754.98 (10.9%); £3,752,195.13 -> £3,342,754.98 (10.9%); £3,752,195.40 -> £3,342,754.97 (10.9%); £3,752,195.66 -> £3,342,754.97 (10.9%); £3,752,195.94 -> £3,342,754.97 (10.9%); £3,752,196.19 -> £3,342,754.97 (10.9%); £3,752,196.47 -> £3,342,754.97 (10.9%); £3,752,196.73 -> £3,342,754.97 (10.9%); £3,752,196.99 -> £3,342,754.97 (10.9%); £3,752,197.26 -> £3,342,754.97 (10.9%); £3,752,197.52 -> £3,342,754.97 (10.9%); £3,752,197.79 -> £3,342,755.01 (10.9%); £3,752,198.06 -> £3,342,755.06 (10.9%); £3,752,198.33 -> £3,342,755.13 (10.9%); £3,752,198.59 -> £3,342,755.20 (10.9%); £3,752,198.85 -> £3,342,755.26 (10.9%); £3,752,199.12 -> £3,342,755.33 (10.9%); £3,752,199.38 -> £3,342,755.42 (10.9%); £3,752,199.65 -> £3,342,755.50 (10.9%); £3,752,199.91 -> £3,342,755.47 (10.9%); £3,752,200.18 -> £3,342,755.45 (10.9%); £3,752,200.44 -> £3,342,755.43 (10.9%); £3,752,200.71 -> £3,342,755.41 (10.9%); £3,752,200.98 -> £3,342,755.40 (10.9%); £3,752,201.24 -> £3,342,755.40 (10.9%); £3,752,201.49 -> £3,342,755.39 (10.9%); £3,752,201.72 -> £3,342,755.39 (10.9%); £3,752,201.93 -> £3,342,755.39 (10.9%); £3,752,202.07 -> £3,342,755.39 (10.9%); £3,752,202.20 -> £3,342,755.39 (10.9%); £3,752,202.35 -> £3,342,755.39 (10.9%); £3,752,202.48 -> £3,342,755.39 (10.9%); £3,752,202.62 -> £3,342,755.39 (10.9%); £3,752,202.76 -> £3,342,755.40 (10.9%); £3,752,202.90 -> £3,342,755.40 (10.9%); £3,752,203.04 -> £3,342,755.40 (10.9%); £3,752,203.18 -> £3,342,755.40 (10.9%); £3,752,203.32 -> £3,342,755.41 (10.9%); £3,752,203.46 -> £3,342,755.41 (10.9%); £3,752,203.60 -> £3,342,755.41 (10.9%); £3,752,203.75 -> £3,342,755.40 (10.9%); £3,752,203.90 -> £3,342,755.40 (10.9%); £3,752,204.07 -> £3,342,755.40 (10.9%); £3,752,204.26 -> £3,342,755.39 (10.9%); £3,752,204.46 -> £3,342,755.38 (10.9%); £3,752,204.67 -> £3,342,755.38 (10.9%); £3,752,204.90 -> £3,342,755.37 (10.9%); £3,752,205.14 -> £3,342,755.36 (10.9%); £3,752,205.37 -> £3,342,755.36 (10.9%); £3,752,205.61 -> £3,342,755.36 (10.9%); £3,752,205.83 -> £3,342,755.35 (10.9%); £3,752,206.06 -> £3,342,755.35 (10.9%); £3,752,206.30 -> £3,342,755.34 (10.9%); £3,752,206.53 -> £3,342,755.34 (10.9%); £3,752,206.77 -> £3,342,755.34 (10.9%); £3,752,206.99 -> £3,342,755.33 (10.9%); £3,752,207.22 -> £3,342,755.33 (10.9%); £3,752,207.45 -> £3,342,755.33 (10.9%); £3,752,207.69 -> £3,342,755.33 (10.9%); £3,752,207.93 -> £3,342,755.33 (10.9%); £3,752,208.16 -> £3,342,755.32 (10.9%); £3,752,208.34 -> £3,342,755.30 (10.9%); £3,752,208.57 -> £3,342,755.28 (10.9%); £3,752,208.75 -> £3,342,755.26 (10.9%); £3,752,208.91 -> £3,342,755.24 (10.9%); £3,752,209.09 -> £3,342,755.21 (10.9%); £3,752,209.27 -> £3,342,755.19 (10.9%); £3,752,209.50 -> £3,342,755.17 (10.9%); £3,752,209.73 -> £3,342,755.15 (10.9%); £3,752,209.96 -> £3,342,755.12 (10.9%); £3,752,210.19 -> £3,342,755.11 (10.9%); £3,752,210.42 -> £3,342,755.10 (10.9%); £3,752,210.65 -> £3,342,755.10 (10.9%); £3,752,210.86 -> £3,342,755.09 (10.9%); £3,752,211.05 -> £3,342,755.09 (10.9%); £3,752,211.23 -> £3,342,755.08 (10.9%); £3,752,211.37 -> £3,342,755.08 (10.9%); £3,752,211.51 -> £3,342,755.08 (10.9%); £3,752,211.66 -> £3,342,755.08 (10.9%); £3,752,211.79 -> £3,342,755.08 (10.9%); £3,752,211.94 -> £3,342,755.09 (10.9%); £3,752,212.07 -> £3,342,755.09 (10.9%); £3,752,212.22 -> £3,342,755.09 (10.9%); £3,752,212.35 -> £3,342,755.09 (10.9%); £3,752,212.50 -> £3,342,755.10 (10.9%); £3,752,212.63 -> £3,342,755.10 (10.9%); £3,752,212.78 -> £3,342,755.10 (10.9%); £3,752,212.92 -> £3,342,755.10 (10.9%); £3,752,213.06 -> £3,342,755.10 (10.9%); £3,752,213.22 -> £3,342,755.10 (10.9%); £3,752,213.38 -> £3,342,755.10 (10.9%); £3,752,213.56 -> £3,342,755.10 (10.9%); £3,752,213.76 -> £3,342,755.09 (10.9%); £3,752,213.99 -> £3,342,755.08 (10.9%); £3,752,214.23 -> £3,342,755.07 (10.9%); £3,752,214.46 -> £3,342,755.06 (10.9%); £3,752,214.69 -> £3,342,755.06 (10.9%); £3,752,214.93 -> £3,342,755.05 (10.9%); £3,752,215.16 -> £3,342,755.04 (10.9%); £3,752,215.39 -> £3,342,755.03 (10.9%); £3,752,215.63 -> £3,342,755.02 (10.9%); £3,752,215.87 -> £3,342,755.02 (10.9%); £3,752,216.11 -> £3,342,755.01 (10.9%); £3,752,216.35 -> £3,342,755.00 (10.9%); £3,752,216.58 -> £3,342,755.00 (10.9%); £3,752,216.82 -> £3,342,754.99 (10.9%); £3,752,217.06 -> £3,342,754.99 (10.9%); £3,752,217.30 -> £3,342,754.99 (10.9%); £3,752,217.52 -> £3,342,754.97 (10.9%); £3,752,217.76 -> £3,342,754.96 (10.9%); £3,752,217.92 -> £3,342,754.94 (10.9%); £3,752,218.10 -> £3,342,754.92 (10.9%); £3,752,218.28 -> £3,342,754.90 (10.9%); £3,752,218.46 -> £3,342,754.87 (10.9%); £3,752,218.63 -> £3,342,754.84 (10.9%); £3,752,218.87 -> £3,342,754.81 (10.9%); £3,752,219.10 -> £3,342,754.79 (10.9%); £3,752,219.34 -> £3,342,754.77 (10.9%); £3,752,219.57 -> £3,342,754.75 (10.9%); £3,752,219.80 -> £3,342,754.74 (10.9%); £3,752,220.04 -> £3,342,754.74 (10.9%); £3,752,220.26 -> £3,342,754.73 (10.9%); £3,752,220.46 -> £3,342,754.73 (10.9%); £3,752,220.65 -> £3,342,754.73 (10.9%); £3,752,220.80 -> £3,342,754.73 (10.9%); £3,752,220.97 -> £3,342,754.73 (10.9%); £3,752,221.13 -> £3,342,754.73 (10.9%); £3,752,221.29 -> £3,342,754.73 (10.9%); £3,752,221.45 -> £3,342,754.74 (10.9%); £3,752,221.62 -> £3,342,754.74 (10.9%); £3,752,221.78 -> £3,342,754.74 (10.9%); £3,752,221.94 -> £3,342,754.74 (10.9%); £3,752,222.11 -> £3,342,754.75 (10.9%); £3,752,222.28 -> £3,342,754.75 (10.9%); £3,752,222.43 -> £3,342,754.75 (10.9%); £3,752,222.60 -> £3,342,754.75 (10.9%); £3,752,222.76 -> £3,342,754.74 (10.9%); £3,752,222.95 -> £3,342,754.79 (10.9%); £3,752,223.15 -> £3,342,754.84 (10.9%); £3,752,223.38 -> £3,342,754.89 (10.9%); £3,752,223.61 -> £3,342,754.94 (10.9%); £3,752,223.86 -> £3,342,754.99 (10.9%); £3,752,224.12 -> £3,342,755.03 (10.9%); £3,752,224.40 -> £3,342,755.07 (10.9%); £3,752,224.68 -> £3,342,755.10 (10.9%); £3,752,224.96 -> £3,342,755.10 (10.9%); £3,752,225.23 -> £3,342,755.10 (10.9%); £3,752,225.49 -> £3,342,755.10 (10.9%); £3,752,225.76 -> £3,342,755.10 (10.9%); £3,752,226.03 -> £3,342,755.09 (10.9%); £3,752,226.29 -> £3,342,755.09 (10.9%); £3,752,226.57 -> £3,342,755.09 (10.9%); £3,752,226.83 -> £3,342,755.09 (10.9%); £3,752,227.10 -> £3,342,755.09 (10.9%); £3,752,227.38 -> £3,342,755.09 (10.9%); £3,752,227.64 -> £3,342,755.13 (10.9%); £3,752,227.85 -> £3,342,755.18 (10.9%); £3,752,228.05 -> £3,342,755.25 (10.9%); £3,752,228.25 -> £3,342,755.32 (10.9%); £3,752,228.46 -> £3,342,755.38 (10.9%); £3,752,228.67 -> £3,342,755.45 (10.9%); £3,752,228.94 -> £3,342,755.54 (10.9%); £3,752,229.22 -> £3,342,755.62 (10.9%); £3,752,229.50 -> £3,342,755.59 (10.9%); £3,752,229.77 -> £3,342,755.57 (10.9%); £3,752,230.04 -> £3,342,755.55 (10.9%); £3,752,230.31 -> £3,342,755.53 (10.9%); £3,752,230.58 -> £3,342,755.52 (10.9%); £3,752,230.85 -> £3,342,755.51 (10.9%); £3,752,231.10 -> £3,342,755.51 (10.9%); £3,752,231.33 -> £3,342,755.51 (10.9%); £3,752,231.55 -> £3,342,755.51 (10.9%); £3,752,231.72 -> £3,342,755.51 (10.9%); £3,752,231.89 -> £3,342,755.51 (10.9%); £3,752,232.05 -> £3,342,755.51 (10.9%); £3,752,232.22 -> £3,342,755.51 (10.9%); £3,752,232.39 -> £3,342,755.51 (10.9%); £3,752,232.55 -> £3,342,755.52 (10.9%); £3,752,232.72 -> £3,342,755.52 (10.9%); £3,752,232.88 -> £3,342,755.52 (10.9%); £3,752,233.05 -> £3,342,755.52 (10.9%); £3,752,233.21 -> £3,342,755.53 (10.9%); £3,752,233.38 -> £3,342,755.53 (10.9%); £3,752,233.54 -> £3,342,755.53 (10.9%); £3,752,233.71 -> £3,342,755.52 (10.9%); £3,752,233.90 -> £3,342,755.57 (10.9%); £3,752,234.10 -> £3,342,755.62 (10.9%); £3,752,234.32 -> £3,342,755.67 (10.9%); £3,752,234.56 -> £3,342,755.72 (10.9%); £3,752,234.81 -> £3,342,755.77 (10.9%); £3,752,235.08 -> £3,342,755.81 (10.9%); £3,752,235.35 -> £3,342,755.85 (10.9%); £3,752,235.64 -> £3,342,755.88 (10.9%); £3,752,235.92 -> £3,342,755.88 (10.9%); £3,752,236.19 -> £3,342,755.88 (10.9%); £3,752,236.47 -> £3,342,755.88 (10.9%); £3,752,236.74 -> £3,342,755.88 (10.9%); £3,752,237.01 -> £3,342,755.88 (10.9%); £3,752,237.29 -> £3,342,755.88 (10.9%); £3,752,237.55 -> £3,342,755.88 (10.9%); £3,752,237.83 -> £3,342,755.87 (10.9%); £3,752,238.09 -> £3,342,755.87 (10.9%); £3,752,238.36 -> £3,342,755.87 (10.9%); £3,752,238.64 -> £3,342,755.91 (10.9%); £3,752,238.84 -> £3,342,755.97 (10.9%); £3,752,239.05 -> £3,342,756.03 (10.9%); £3,752,239.26 -> £3,342,756.10 (10.9%); £3,752,239.47 -> £3,342,756.16 (10.9%); £3,752,239.67 -> £3,342,756.23 (10.9%); £3,752,239.87 -> £3,342,756.31 (10.9%); £3,752,240.08 -> £3,342,756.39 (10.9%); £3,752,240.36 -> £3,342,756.37 (10.9%); £3,752,240.63 -> £3,342,756.34 (10.9%); £3,752,240.90 -> £3,342,756.32 (10.9%); £3,752,241.17 -> £3,342,756.30 (10.9%); £3,752,241.45 -> £3,342,756.29 (10.9%); £3,752,241.72 -> £3,342,756.29 (10.9%); £3,752,241.97 -> £3,342,756.28 (10.9%); £3,752,242.20 -> £3,342,756.28 (10.9%); £3,752,242.40 -> £3,342,756.28 (10.9%); £3,752,242.58 -> £3,342,756.28 (10.9%); £3,752,242.74 -> £3,342,756.28 (10.9%); £3,752,242.90 -> £3,342,756.28 (10.9%); £3,752,243.06 -> £3,342,756.28 (10.9%); £3,752,243.23 -> £3,342,756.28 (10.9%); £3,752,243.40 -> £3,342,756.28 (10.9%); £3,752,243.56 -> £3,342,756.29 (10.9%); £3,752,243.73 -> £3,342,756.29 (10.9%); £3,752,243.89 -> £3,342,756.29 (10.9%); £3,752,244.06 -> £3,342,756.29 (10.9%); £3,752,244.23 -> £3,342,756.29 (10.9%); £3,752,244.39 -> £3,342,756.29 (10.9%); £3,752,244.56 -> £3,342,756.28 (10.9%); £3,752,244.74 -> £3,342,756.33 (10.9%); £3,752,244.95 -> £3,342,756.38 (10.9%); £3,752,245.17 -> £3,342,756.43 (10.9%); £3,752,245.41 -> £3,342,756.48 (10.9%); £3,752,245.67 -> £3,342,756.53 (10.9%); £3,752,245.95 -> £3,342,756.57 (10.9%); £3,752,246.23 -> £3,342,756.61 (10.9%); £3,752,246.51 -> £3,342,756.64 (10.9%); £3,752,246.79 -> £3,342,756.64 (10.9%); £3,752,247.07 -> £3,342,756.64 (10.9%); £3,752,247.34 -> £3,342,756.64 (10.9%); £3,752,247.63 -> £3,342,756.64 (10.9%); £3,752,247.89 -> £3,342,756.64 (10.9%); £3,752,248.16 -> £3,342,756.64 (10.9%); £3,752,248.44 -> £3,342,756.64 (10.9%); £3,752,248.72 -> £3,342,756.63 (10.9%); £3,752,248.99 -> £3,342,756.63 (10.9%); £3,752,249.26 -> £3,342,756.63 (10.9%); £3,752,249.54 -> £3,342,756.67 (10.9%); £3,752,249.75 -> £3,342,756.73 (10.9%); £3,752,249.96 -> £3,342,756.79 (10.9%); £3,752,250.23 -> £3,342,756.86 (10.9%); £3,752,250.44 -> £3,342,756.93 (10.9%); £3,752,250.64 -> £3,342,756.99 (10.9%); £3,752,250.84 -> £3,342,757.08 (10.9%); £3,752,251.11 -> £3,342,757.16 (10.9%); £3,752,251.40 -> £3,342,757.13 (10.9%); £3,752,251.66 -> £3,342,757.11 (10.9%); £3,752,251.93 -> £3,342,757.09 (10.9%); £3,752,252.20 -> £3,342,757.06 (10.9%); £3,752,252.48 -> £3,342,757.06 (10.9%); £3,752,252.76 -> £3,342,757.05 (10.9%); £3,752,253.02 -> £3,342,757.05 (10.9%); £3,752,253.26 -> £3,342,757.04 (10.9%); £3,752,253.48 -> £3,342,757.04 (10.9%); £3,752,253.64 -> £3,342,757.04 (10.9%); £3,752,253.80 -> £3,342,757.04 (10.9%); £3,752,253.97 -> £3,342,757.05 (10.9%); £3,752,254.13 -> £3,342,757.05 (10.9%); £3,752,254.30 -> £3,342,757.05 (10.9%); £3,752,254.47 -> £3,342,757.05 (10.9%); £3,752,254.63 -> £3,342,757.05 (10.9%); £3,752,254.80 -> £3,342,757.06 (10.9%); £3,752,254.96 -> £3,342,757.06 (10.9%); £3,752,255.12 -> £3,342,757.06 (10.9%); £3,752,255.28 -> £3,342,757.06 (10.9%); £3,752,255.45 -> £3,342,757.06 (10.9%); £3,752,255.62 -> £3,342,757.05 (10.9%); £3,752,255.81 -> £3,342,757.10 (10.9%); £3,752,256.00 -> £3,342,757.15 (10.9%); £3,752,256.23 -> £3,342,757.20 (10.9%); £3,752,256.47 -> £3,342,757.25 (10.9%); £3,752,256.72 -> £3,342,757.30 (10.9%); £3,752,257.00 -> £3,342,757.34 (10.9%); £3,752,257.27 -> £3,342,757.38 (10.9%); £3,752,257.55 -> £3,342,757.41 (10.9%); £3,752,257.83 -> £3,342,757.41 (10.9%); £3,752,258.11 -> £3,342,757.41 (10.9%); £3,752,258.38 -> £3,342,757.41 (10.9%); £3,752,258.64 -> £3,342,757.41 (10.9%); £3,752,258.92 -> £3,342,757.40 (10.9%); £3,752,259.20 -> £3,342,757.40 (10.9%); £3,752,259.47 -> £3,342,757.40 (10.9%); £3,752,259.75 -> £3,342,757.40 (10.9%); £3,752,260.02 -> £3,342,757.40 (10.9%); £3,752,260.29 -> £3,342,757.40 (10.9%); £3,752,260.56 -> £3,342,757.44 (10.9%); £3,752,260.77 -> £3,342,757.49 (10.9%); £3,752,261.05 -> £3,342,757.56 (10.9%); £3,752,261.26 -> £3,342,757.63 (10.9%); £3,752,261.52 -> £3,342,757.69 (10.9%); £3,752,261.79 -> £3,342,757.76 (10.9%); £3,752,262.07 -> £3,342,757.85 (10.9%); £3,752,262.34 -> £3,342,757.93 (10.9%); £3,752,262.61 -> £3,342,757.90 (10.9%); £3,752,262.89 -> £3,342,757.88 (10.9%); £3,752,263.17 -> £3,342,757.86 (10.9%); £3,752,263.44 -> £3,342,757.84 (10.9%); £3,752,263.73 -> £3,342,757.83 (10.9%); £3,752,264.00 -> £3,342,757.82 (10.9%); £3,752,264.26 -> £3,342,757.82 (10.9%); £3,752,264.49 -> £3,342,757.81 (10.9%); £3,752,264.71 -> £3,342,757.81 (10.9%); £3,752,264.87 -> £3,342,757.81 (10.9%); £3,752,265.04 -> £3,342,757.81 (10.9%); £3,752,265.20 -> £3,342,757.82 (10.9%); £3,752,265.36 -> £3,342,757.82 (10.9%); £3,752,265.52 -> £3,342,757.82 (10.9%); £3,752,265.69 -> £3,342,757.82 (10.9%); £3,752,265.85 -> £3,342,757.82 (10.9%); £3,752,266.01 -> £3,342,757.82 (10.9%); £3,752,266.18 -> £3,342,757.83 (10.9%); £3,752,266.34 -> £3,342,757.83 (10.9%); £3,752,266.51 -> £3,342,757.83 (10.9%); £3,752,266.68 -> £3,342,757.83 (10.9%); £3,752,266.84 -> £3,342,757.82 (10.9%); £3,752,267.02 -> £3,342,757.87 (10.9%); £3,752,267.22 -> £3,342,757.92 (10.9%); £3,752,267.44 -> £3,342,757.97 (10.9%); £3,752,267.66 -> £3,342,758.02 (10.9%); £3,752,267.93 -> £3,342,758.06 (10.9%); £3,752,268.19 -> £3,342,758.11 (10.9%); £3,752,268.46 -> £3,342,758.15 (10.9%); £3,752,268.74 -> £3,342,758.18 (10.9%); £3,752,269.01 -> £3,342,758.18 (10.9%); £3,752,269.28 -> £3,342,758.18 (10.9%); £3,752,269.54 -> £3,342,758.18 (10.9%); £3,752,269.80 -> £3,342,758.18 (10.9%); £3,752,270.07 -> £3,342,758.18 (10.9%); £3,752,270.34 -> £3,342,758.18 (10.9%); £3,752,270.62 -> £3,342,758.18 (10.9%); £3,752,270.90 -> £3,342,758.18 (10.9%); £3,752,271.16 -> £3,342,758.18 (10.9%); £3,752,271.44 -> £3,342,758.18 (10.9%); £3,752,271.71 -> £3,342,758.21 (10.9%); £3,752,271.98 -> £3,342,758.27 (10.9%); £3,752,272.24 -> £3,342,758.34 (10.9%); £3,752,272.52 -> £3,342,758.41 (10.9%); £3,752,272.80 -> £3,342,758.47 (10.9%); £3,752,273.07 -> £3,342,758.54 (10.9%); £3,752,273.27 -> £3,342,758.62 (10.9%); £3,752,273.48 -> £3,342,758.70 (10.9%); £3,752,273.76 -> £3,342,758.68 (10.9%); £3,752,274.02 -> £3,342,758.66 (10.9%); £3,752,274.29 -> £3,342,758.63 (10.9%); £3,752,274.56 -> £3,342,758.61 (10.9%); £3,752,274.83 -> £3,342,758.61 (10.9%); £3,752,275.10 -> £3,342,758.60 (10.9%); £3,752,275.35 -> £3,342,758.60 (10.9%); £3,752,275.59 -> £3,342,758.59 (10.9%); £3,752,275.80 -> £3,342,758.59 (10.9%); £3,752,275.94 -> £3,342,758.59 (10.9%); £3,752,276.08 -> £3,342,758.59 (10.9%); £3,752,276.23 -> £3,342,758.59 (10.9%); £3,752,276.37 -> £3,342,758.59 (10.9%); £3,752,276.51 -> £3,342,758.59 (10.9%); £3,752,276.65 -> £3,342,758.59 (10.9%); £3,752,276.80 -> £3,342,758.60 (10.9%); £3,752,276.93 -> £3,342,758.60 (10.9%); £3,752,277.08 -> £3,342,758.60 (10.9%); £3,752,277.22 -> £3,342,758.60 (10.9%); £3,752,277.36 -> £3,342,758.60 (10.9%); £3,752,277.51 -> £3,342,758.60 (10.9%); £3,752,277.65 -> £3,342,758.60 (10.9%); £3,752,277.81 -> £3,342,758.59 (10.9%); £3,752,277.99 -> £3,342,758.59 (10.9%); £3,752,278.18 -> £3,342,758.58 (10.9%); £3,752,278.39 -> £3,342,758.57 (10.9%); £3,752,278.61 -> £3,342,758.57 (10.9%); £3,752,278.85 -> £3,342,758.56 (10.9%); £3,752,279.08 -> £3,342,758.55 (10.9%); £3,752,279.32 -> £3,342,758.55 (10.9%); £3,752,279.56 -> £3,342,758.55 (10.9%); £3,752,279.81 -> £3,342,758.54 (10.9%); £3,752,280.04 -> £3,342,758.54 (10.9%); £3,752,280.28 -> £3,342,758.53 (10.9%); £3,752,280.51 -> £3,342,758.53 (10.9%); £3,752,280.75 -> £3,342,758.53 (10.9%); £3,752,280.99 -> £3,342,758.52 (10.9%); £3,752,281.24 -> £3,342,758.52 (10.9%); £3,752,281.47 -> £3,342,758.52 (10.9%); £3,752,281.71 -> £3,342,758.52 (10.9%); £3,752,281.96 -> £3,342,758.52 (10.9%); £3,752,282.19 -> £3,342,758.50 (10.9%); £3,752,282.43 -> £3,342,758.49 (10.9%); £3,752,282.66 -> £3,342,758.47 (10.9%); £3,752,282.84 -> £3,342,758.45 (10.9%); £3,752,283.08 -> £3,342,758.43 (10.9%); £3,752,283.26 -> £3,342,758.40 (10.9%); £3,752,283.44 -> £3,342,758.38 (10.9%); £3,752,283.68 -> £3,342,758.35 (10.9%); £3,752,283.92 -> £3,342,758.33 (10.9%); £3,752,284.16 -> £3,342,758.31 (10.9%); £3,752,284.40 -> £3,342,758.29 (10.9%); £3,752,284.65 -> £3,342,758.28 (10.9%); £3,752,284.88 -> £3,342,758.28 (10.9%); £3,752,285.10 -> £3,342,758.27 (10.9%); £3,752,285.31 -> £3,342,758.27 (10.9%); £3,752,285.50 -> £3,342,758.26 (10.9%); £3,752,285.64 -> £3,342,758.26 (10.9%); £3,752,285.78 -> £3,342,758.26 (10.9%); £3,752,285.92 -> £3,342,758.26 (10.9%); £3,752,286.05 -> £3,342,758.26 (10.9%); £3,752,286.20 -> £3,342,758.26 (10.9%); £3,752,286.34 -> £3,342,758.27 (10.9%); £3,752,286.48 -> £3,342,758.27 (10.9%); £3,752,286.62 -> £3,342,758.27 (10.9%); £3,752,286.77 -> £3,342,758.27 (10.9%); £3,752,286.91 -> £3,342,758.27 (10.9%); £3,752,287.04 -> £3,342,758.28 (10.9%); £3,752,287.18 -> £3,342,758.28 (10.9%); £3,752,287.31 -> £3,342,758.27 (10.9%); £3,752,287.47 -> £3,342,758.27 (10.9%); £3,752,287.64 -> £3,342,758.27 (10.9%); £3,752,287.82 -> £3,342,758.27 (10.9%); £3,752,288.03 -> £3,342,758.26 (10.9%); £3,752,288.25 -> £3,342,758.25 (10.9%); £3,752,288.49 -> £3,342,758.24 (10.9%); £3,752,288.72 -> £3,342,758.24 (10.9%); £3,752,288.96 -> £3,342,758.23 (10.9%); £3,752,289.19 -> £3,342,758.22 (10.9%); £3,752,289.43 -> £3,342,758.21 (10.9%); £3,752,289.67 -> £3,342,758.20 (10.9%); £3,752,289.91 -> £3,342,758.19 (10.9%); £3,752,290.13 -> £3,342,758.18 (10.9%); £3,752,290.37 -> £3,342,758.18 (10.9%); £3,752,290.60 -> £3,342,758.17 (10.9%); £3,752,290.84 -> £3,342,758.17 (10.9%); £3,752,291.07 -> £3,342,758.16 (10.9%); £3,752,291.30 -> £3,342,758.16 (10.9%); £3,752,291.54 -> £3,342,758.16 (10.9%); £3,752,291.77 -> £3,342,758.14 (10.9%); £3,752,292.00 -> £3,342,758.12 (10.9%); £3,752,292.18 -> £3,342,758.11 (10.9%); £3,752,292.36 -> £3,342,758.09 (10.9%); £3,752,292.54 -> £3,342,758.07 (10.9%); £3,752,292.71 -> £3,342,758.04 (10.9%); £3,752,292.89 -> £3,342,758.01 (10.9%); £3,752,293.12 -> £3,342,757.99 (10.9%); £3,752,293.36 -> £3,342,757.96 (10.9%); £3,752,293.59 -> £3,342,757.94 (10.9%); £3,752,293.82 -> £3,342,757.92 (10.9%); £3,752,294.05 -> £3,342,757.91 (10.9%); £3,752,294.29 -> £3,342,757.90 (10.9%); £3,752,294.51 -> £3,342,757.90 (10.9%); £3,752,294.71 -> £3,342,757.89 (10.9%); £3,752,294.89 -> £3,342,757.89 (10.9%); £3,752,295.05 -> £3,342,757.89 (10.9%); £3,752,295.21 -> £3,342,757.89 (10.9%); £3,752,295.36 -> £3,342,757.89 (10.9%); £3,752,295.51 -> £3,342,757.90 (10.9%); £3,752,295.67 -> £3,342,757.90 (10.9%); £3,752,295.83 -> £3,342,757.90 (10.9%); £3,752,295.98 -> £3,342,757.90 (10.9%); £3,752,296.14 -> £3,342,757.91 (10.9%); £3,752,296.29 -> £3,342,757.91 (10.9%); £3,752,296.45 -> £3,342,757.91 (10.9%); £3,752,296.60 -> £3,342,757.91 (10.9%); £3,752,296.75 -> £3,342,757.91 (10.9%); £3,752,296.91 -> £3,342,757.90 (10.9%); £3,752,297.08 -> £3,342,757.95 (10.9%); £3,752,297.28 -> £3,342,758.00 (10.9%); £3,752,297.49 -> £3,342,758.05 (10.9%); £3,752,297.71 -> £3,342,758.10 (10.9%); £3,752,297.95 -> £3,342,758.15 (10.9%); £3,752,298.22 -> £3,342,758.19 (10.9%); £3,752,298.47 -> £3,342,758.23 (10.9%); £3,752,298.72 -> £3,342,758.26 (10.9%); £3,752,298.98 -> £3,342,758.26 (10.9%); £3,752,299.24 -> £3,342,758.26 (10.9%); £3,752,299.50 -> £3,342,758.26 (10.9%); £3,752,299.76 -> £3,342,758.26 (10.9%); £3,752,300.02 -> £3,342,758.26 (10.9%); £3,752,300.28 -> £3,342,758.26 (10.9%); £3,752,300.54 -> £3,342,758.26 (10.9%); £3,752,300.80 -> £3,342,758.25 (10.9%); £3,752,301.06 -> £3,342,758.25 (10.9%); £3,752,301.32 -> £3,342,758.25 (10.9%); £3,752,301.58 -> £3,342,758.29 (10.9%); £3,752,301.78 -> £3,342,758.35 (10.9%); £3,752,301.97 -> £3,342,758.41 (10.9%); £3,752,302.16 -> £3,342,758.48 (10.9%); £3,752,302.36 -> £3,342,758.55 (10.9%); £3,752,302.55 -> £3,342,758.61 (10.9%); £3,752,302.74 -> £3,342,758.70 (10.9%); £3,752,302.94 -> £3,342,758.78 (10.9%); £3,752,303.20 -> £3,342,758.75 (10.9%); £3,752,303.46 -> £3,342,758.73 (10.9%); £3,752,303.71 -> £3,342,758.71 (10.9%); £3,752,303.98 -> £3,342,758.68 (10.9%); £3,752,304.23 -> £3,342,758.68 (10.9%); £3,752,304.49 -> £3,342,758.67 (10.9%); £3,752,304.73 -> £3,342,758.67 (10.9%); £3,752,304.95 -> £3,342,758.66 (10.9%); £3,752,305.16 -> £3,342,758.66 (10.9%); £3,752,305.31 -> £3,342,758.66 (10.9%); £3,752,305.48 -> £3,342,758.66 (10.9%); £3,752,305.63 -> £3,342,758.66 (10.9%); £3,752,305.79 -> £3,342,758.67 (10.9%); £3,752,305.95 -> £3,342,758.67 (10.9%); £3,752,306.10 -> £3,342,758.67 (10.9%); £3,752,306.25 -> £3,342,758.67 (10.9%); £3,752,306.41 -> £3,342,758.67 (10.9%); £3,752,306.56 -> £3,342,758.68 (10.9%); £3,752,306.72 -> £3,342,758.68 (10.9%); £3,752,306.87 -> £3,342,758.68 (10.9%); £3,752,307.03 -> £3,342,758.68 (10.9%); £3,752,307.19 -> £3,342,758.67 (10.9%); £3,752,307.37 -> £3,342,758.72 (10.9%); £3,752,307.55 -> £3,342,758.77 (10.9%); £3,752,307.77 -> £3,342,758.82 (10.9%); £3,752,308.00 -> £3,342,758.87 (10.9%); £3,752,308.24 -> £3,342,758.91 (10.9%); £3,752,308.49 -> £3,342,758.96 (10.9%); £3,752,308.75 -> £3,342,758.99 (10.9%); £3,752,309.00 -> £3,342,759.03 (10.9%); £3,752,309.26 -> £3,342,759.03 (10.9%); £3,752,309.52 -> £3,342,759.03 (10.9%); £3,752,309.78 -> £3,342,759.03 (10.9%); £3,752,310.05 -> £3,342,759.02 (10.9%); £3,752,310.30 -> £3,342,759.02 (10.9%); £3,752,310.57 -> £3,342,759.02 (10.9%); £3,752,310.83 -> £3,342,759.02 (10.9%); £3,752,311.09 -> £3,342,759.02 (10.9%); £3,752,311.35 -> £3,342,759.02 (10.9%); £3,752,311.60 -> £3,342,759.02 (10.9%); £3,752,311.86 -> £3,342,759.06 (10.9%); £3,752,312.12 -> £3,342,759.12 (10.9%); £3,752,312.38 -> £3,342,759.18 (10.9%); £3,752,312.63 -> £3,342,759.25 (10.9%); £3,752,312.90 -> £3,342,759.32 (10.9%); £3,752,313.15 -> £3,342,759.39 (10.9%); £3,752,313.41 -> £3,342,759.47 (10.9%); £3,752,313.66 -> £3,342,759.55 (10.9%); £3,752,313.92 -> £3,342,759.53 (10.9%); £3,752,314.18 -> £3,342,759.50 (10.9%); £3,752,314.44 -> £3,342,759.48 (10.9%); £3,752,314.71 -> £3,342,759.46 (10.9%); £3,752,314.97 -> £3,342,759.45 (10.9%); £3,752,315.23 -> £3,342,759.45 (10.9%); £3,752,315.47 -> £3,342,759.44 (10.9%); £3,752,315.70 -> £3,342,759.44 (10.9%); £3,752,315.90 -> £3,342,759.44 (10.9%); £3,752,316.05 -> £3,342,759.44 (10.9%); £3,752,316.20 -> £3,342,759.44 (10.9%); £3,752,316.36 -> £3,342,759.44 (10.9%); £3,752,316.51 -> £3,342,759.44 (10.9%); £3,752,316.66 -> £3,342,759.44 (10.9%); £3,752,316.81 -> £3,342,759.45 (10.9%); £3,752,316.97 -> £3,342,759.45 (10.9%); £3,752,317.12 -> £3,342,759.45 (10.9%); £3,752,317.28 -> £3,342,759.45 (10.9%); £3,752,317.44 -> £3,342,759.45 (10.9%); £3,752,317.59 -> £3,342,759.46 (10.9%); £3,752,317.76 -> £3,342,759.45 (10.9%); £3,752,317.91 -> £3,342,759.45 (10.9%); £3,752,318.09 -> £3,342,759.49 (10.9%); £3,752,318.28 -> £3,342,759.55 (10.9%); £3,752,318.49 -> £3,342,759.60 (10.9%); £3,752,318.71 -> £3,342,759.65 (10.9%); £3,752,318.95 -> £3,342,759.69 (10.9%); £3,752,319.21 -> £3,342,759.74 (10.9%); £3,752,319.47 -> £3,342,759.77 (10.9%); £3,752,319.73 -> £3,342,759.81 (10.9%); £3,752,319.99 -> £3,342,759.81 (10.9%); £3,752,320.25 -> £3,342,759.81 (10.9%); £3,752,320.51 -> £3,342,759.81 (10.9%); £3,752,320.76 -> £3,342,759.80 (10.9%); £3,752,321.01 -> £3,342,759.80 (10.9%); £3,752,321.27 -> £3,342,759.80 (10.9%); £3,752,321.53 -> £3,342,759.80 (10.9%); £3,752,321.79 -> £3,342,759.80 (10.9%); £3,752,322.05 -> £3,342,759.80 (10.9%); £3,752,322.31 -> £3,342,759.80 (10.9%); £3,752,322.58 -> £3,342,759.84 (10.9%); £3,752,322.83 -> £3,342,759.89 (10.9%); £3,752,323.03 -> £3,342,759.96 (10.9%); £3,752,323.22 -> £3,342,760.03 (10.9%); £3,752,323.41 -> £3,342,760.09 (10.9%); £3,752,323.67 -> £3,342,760.16 (10.9%); £3,752,323.93 -> £3,342,760.25 (10.9%); £3,752,324.18 -> £3,342,760.33 (10.9%); £3,752,324.44 -> £3,342,760.30 (10.9%); £3,752,324.71 -> £3,342,760.28 (10.9%); £3,752,324.98 -> £3,342,760.26 (10.9%); £3,752,325.23 -> £3,342,760.24 (10.9%); £3,752,325.48 -> £3,342,760.23 (10.9%); £3,752,325.75 -> £3,342,760.23 (10.9%); £3,752,325.98 -> £3,342,760.22 (10.9%); £3,752,326.20 -> £3,342,760.22 (10.9%); £3,752,326.40 -> £3,342,760.22 (10.9%); £3,752,326.56 -> £3,342,760.22 (10.9%); £3,752,326.72 -> £3,342,760.22 (10.9%); £3,752,326.87 -> £3,342,760.22 (10.9%); £3,752,327.02 -> £3,342,760.22 (10.9%); £3,752,327.18 -> £3,342,760.22 (10.9%); £3,752,327.34 -> £3,342,760.22 (10.9%); £3,752,327.50 -> £3,342,760.23 (10.9%); £3,752,327.66 -> £3,342,760.23 (10.9%); £3,752,327.82 -> £3,342,760.23 (10.9%); £3,752,327.98 -> £3,342,760.23 (10.9%); £3,752,328.13 -> £3,342,760.23 (10.9%); £3,752,328.29 -> £3,342,760.23 (10.9%); £3,752,328.44 -> £3,342,760.22 (10.9%); £3,752,328.61 -> £3,342,760.27 (10.9%); £3,752,328.81 -> £3,342,760.32 (10.9%); £3,752,329.02 -> £3,342,760.38 (10.9%); £3,752,329.25 -> £3,342,760.43 (10.9%); £3,752,329.49 -> £3,342,760.47 (10.9%); £3,752,329.75 -> £3,342,760.52 (10.9%); £3,752,330.02 -> £3,342,760.55 (10.9%); £3,752,330.28 -> £3,342,760.59 (10.9%); £3,752,330.55 -> £3,342,760.59 (10.9%); £3,752,330.81 -> £3,342,760.59 (10.9%); £3,752,331.08 -> £3,342,760.58 (10.9%); £3,752,331.33 -> £3,342,760.58 (10.9%); £3,752,331.60 -> £3,342,760.58 (10.9%); £3,752,331.86 -> £3,342,760.58 (10.9%); £3,752,332.12 -> £3,342,760.58 (10.9%); £3,752,332.37 -> £3,342,760.58 (10.9%); £3,752,332.63 -> £3,342,760.58 (10.9%); £3,752,332.89 -> £3,342,760.58 (10.9%); £3,752,333.15 -> £3,342,760.61 (10.9%); £3,752,333.41 -> £3,342,760.67 (10.9%); £3,752,333.67 -> £3,342,760.74 (10.9%); £3,752,333.93 -> £3,342,760.81 (10.9%); £3,752,334.19 -> £3,342,760.88 (10.9%); £3,752,334.45 -> £3,342,760.94 (10.9%); £3,752,334.72 -> £3,342,761.03 (10.9%); £3,752,334.98 -> £3,342,761.11 (10.9%); £3,752,335.23 -> £3,342,761.09 (10.9%); £3,752,335.49 -> £3,342,761.06 (10.9%); £3,752,335.75 -> £3,342,761.04 (10.9%); £3,752,336.00 -> £3,342,761.02 (10.9%); £3,752,336.26 -> £3,342,761.01 (10.9%); £3,752,336.52 -> £3,342,761.01 (10.9%); £3,752,336.75 -> £3,342,761.00 (10.9%); £3,752,336.97 -> £3,342,761.00 (10.9%); £3,752,337.18 -> £3,342,760.99 (10.9%); £3,752,337.34 -> £3,342,760.99 (10.9%); £3,752,337.49 -> £3,342,761.00 (10.9%); £3,752,337.65 -> £3,342,761.00 (10.9%); £3,752,337.81 -> £3,342,761.00 (10.9%); £3,752,337.96 -> £3,342,761.00 (10.9%); £3,752,338.12 -> £3,342,761.00 (10.9%); £3,752,338.28 -> £3,342,761.01 (10.9%); £3,752,338.44 -> £3,342,761.01 (10.9%); £3,752,338.60 -> £3,342,761.01 (10.9%); £3,752,338.76 -> £3,342,761.01 (10.9%); £3,752,338.92 -> £3,342,761.01 (10.9%); £3,752,339.08 -> £3,342,761.01 (10.9%); £3,752,339.23 -> £3,342,761.00 (10.9%); £3,752,339.41 -> £3,342,761.05 (10.9%); £3,752,339.61 -> £3,342,761.10 (10.9%); £3,752,339.82 -> £3,342,761.16 (10.9%); £3,752,340.04 -> £3,342,761.20 (10.9%); £3,752,340.29 -> £3,342,761.25 (10.9%); £3,752,340.56 -> £3,342,761.29 (10.9%); £3,752,340.82 -> £3,342,761.33 (10.9%); £3,752,341.09 -> £3,342,761.37 (10.9%); £3,752,341.34 -> £3,342,761.36 (10.9%); £3,752,341.59 -> £3,342,761.36 (10.9%); £3,752,341.86 -> £3,342,761.36 (10.9%); £3,752,342.12 -> £3,342,761.36 (10.9%); £3,752,342.38 -> £3,342,761.36 (10.9%); £3,752,342.63 -> £3,342,761.36 (10.9%); £3,752,342.90 -> £3,342,761.36 (10.9%); £3,752,343.15 -> £3,342,761.36 (10.9%); £3,752,343.41 -> £3,342,761.35 (10.9%); £3,752,343.68 -> £3,342,761.35 (10.9%); £3,752,343.94 -> £3,342,761.39 (10.9%); £3,752,344.14 -> £3,342,761.45 (10.9%); £3,752,344.41 -> £3,342,761.51 (10.9%); £3,752,344.60 -> £3,342,761.58 (10.9%); £3,752,344.79 -> £3,342,761.65 (10.9%); £3,752,344.99 -> £3,342,761.71 (10.9%); £3,752,345.18 -> £3,342,761.80 (10.9%); £3,752,345.38 -> £3,342,761.88 (10.9%); £3,752,345.63 -> £3,342,761.85 (10.9%); £3,752,345.90 -> £3,342,761.83 (10.9%); £3,752,346.16 -> £3,342,761.80 (10.9%); £3,752,346.42 -> £3,342,761.78 (10.9%); £3,752,346.69 -> £3,342,761.78 (10.9%); £3,752,346.96 -> £3,342,761.77 (10.9%); £3,752,347.20 -> £3,342,761.77 (10.9%); £3,752,347.42 -> £3,342,761.76 (10.9%); £3,752,347.62 -> £3,342,761.76 (10.9%); £3,752,347.76 -> £3,342,761.76 (10.9%); £3,752,347.90 -> £3,342,761.76 (10.9%); £3,752,348.03 -> £3,342,761.76 (10.9%); £3,752,348.17 -> £3,342,761.76 (10.9%); £3,752,348.32 -> £3,342,761.77 (10.9%); £3,752,348.45 -> £3,342,761.77 (10.9%); £3,752,348.59 -> £3,342,761.77 (10.9%); £3,752,348.73 -> £3,342,761.77 (10.9%); £3,752,348.87 -> £3,342,761.77 (10.9%); £3,752,349.00 -> £3,342,761.78 (10.9%); £3,752,349.14 -> £3,342,761.78 (10.9%); £3,752,349.28 -> £3,342,761.78 (10.9%); £3,752,349.42 -> £3,342,761.77 (10.9%); £3,752,349.57 -> £3,342,761.77 (10.9%); £3,752,349.74 -> £3,342,761.77 (10.9%); £3,752,349.92 -> £3,342,761.76 (10.9%); £3,752,350.13 -> £3,342,761.75 (10.9%); £3,752,350.34 -> £3,342,761.74 (10.9%); £3,752,350.56 -> £3,342,761.73 (10.9%); £3,752,350.78 -> £3,342,761.73 (10.9%); £3,752,351.00 -> £3,342,761.73 (10.9%); £3,752,351.23 -> £3,342,761.72 (10.9%); £3,752,351.46 -> £3,342,761.72 (10.9%); £3,752,351.70 -> £3,342,761.72 (10.9%); £3,752,351.92 -> £3,342,761.71 (10.9%); £3,752,352.15 -> £3,342,761.71 (10.9%); £3,752,352.37 -> £3,342,761.70 (10.9%); £3,752,352.59 -> £3,342,761.70 (10.9%); £3,752,352.83 -> £3,342,761.70 (10.9%); £3,752,353.05 -> £3,342,761.70 (10.9%); £3,752,353.28 -> £3,342,761.70 (10.9%); £3,752,353.50 -> £3,342,761.69 (10.9%); £3,752,353.68 -> £3,342,761.68 (10.9%); £3,752,353.85 -> £3,342,761.66 (10.9%); £3,752,354.02 -> £3,342,761.65 (10.9%); £3,752,354.19 -> £3,342,761.63 (10.9%); £3,752,354.37 -> £3,342,761.61 (10.9%); £3,752,354.54 -> £3,342,761.58 (10.9%); £3,752,354.71 -> £3,342,761.55 (10.9%); £3,752,354.94 -> £3,342,761.53 (10.9%); £3,752,355.16 -> £3,342,761.51 (10.9%); £3,752,355.40 -> £3,342,761.49 (10.9%); £3,752,355.62 -> £3,342,761.47 (10.9%); £3,752,355.84 -> £3,342,761.46 (10.9%); £3,752,356.08 -> £3,342,761.46 (10.9%); £3,752,356.29 -> £3,342,761.45 (10.9%); £3,752,356.48 -> £3,342,761.44 (10.9%); £3,752,356.66 -> £3,342,761.44 (10.9%); £3,752,356.80 -> £3,342,761.44 (10.9%); £3,752,356.93 -> £3,342,761.44 (10.9%); £3,752,357.07 -> £3,342,761.44 (10.9%); £3,752,357.21 -> £3,342,761.44 (10.9%); £3,752,357.35 -> £3,342,761.44 (10.9%); £3,752,357.49 -> £3,342,761.44 (10.9%); £3,752,357.63 -> £3,342,761.44 (10.9%); £3,752,357.77 -> £3,342,761.45 (10.9%); £3,752,357.91 -> £3,342,761.45 (10.9%); £3,752,358.04 -> £3,342,761.45 (10.9%); £3,752,358.18 -> £3,342,761.45 (10.9%); £3,752,358.31 -> £3,342,761.45 (10.9%); £3,752,358.45 -> £3,342,761.45 (10.9%); £3,752,358.61 -> £3,342,761.45 (10.9%); £3,752,358.78 -> £3,342,761.45 (10.9%); £3,752,358.96 -> £3,342,761.44 (10.9%); £3,752,359.16 -> £3,342,761.44 (10.9%); £3,752,359.37 -> £3,342,761.43 (10.9%); £3,752,359.60 -> £3,342,761.42 (10.9%); £3,752,359.83 -> £3,342,761.41 (10.9%); £3,752,360.06 -> £3,342,761.40 (10.9%); £3,752,360.29 -> £3,342,761.39 (10.9%); £3,752,360.52 -> £3,342,761.38 (10.9%); £3,752,360.75 -> £3,342,761.38 (10.9%); £3,752,360.98 -> £3,342,761.37 (10.9%); £3,752,361.21 -> £3,342,761.36 (10.9%); £3,752,361.44 -> £3,342,761.35 (10.9%); £3,752,361.67 -> £3,342,761.35 (10.9%); £3,752,361.90 -> £3,342,761.34 (10.9%); £3,752,362.13 -> £3,342,761.34 (10.9%); £3,752,362.36 -> £3,342,761.34 (10.9%); £3,752,362.59 -> £3,342,761.33 (10.9%); £3,752,362.83 -> £3,342,761.32 (10.9%); £3,752,363.06 -> £3,342,761.30 (10.9%); £3,752,363.29 -> £3,342,761.28 (10.9%); £3,752,363.45 -> £3,342,761.26 (10.9%); £3,752,363.68 -> £3,342,761.25 (10.9%); £3,752,363.86 -> £3,342,761.22 (10.9%); £3,752,364.02 -> £3,342,761.19 (10.9%); £3,752,364.26 -> £3,342,761.16 (10.9%); £3,752,364.49 -> £3,342,761.14 (10.9%); £3,752,364.72 -> £3,342,761.12 (10.9%); £3,752,364.94 -> £3,342,761.10 (10.9%); £3,752,365.17 -> £3,342,761.09 (10.9%); £3,752,365.40 -> £3,342,761.09 (10.9%); £3,752,365.60 -> £3,342,761.08 (10.9%); £3,752,365.80 -> £3,342,761.08 (10.9%); £3,752,365.97 -> £3,342,761.08 (10.9%); £3,752,366.13 -> £3,342,761.08 (10.9%); £3,752,366.29 -> £3,342,761.08 (10.9%); £3,752,366.45 -> £3,342,761.08 (10.9%); £3,752,366.62 -> £3,342,761.08 (10.9%); £3,752,366.78 -> £3,342,761.09 (10.9%); £3,752,366.94 -> £3,342,761.09 (10.9%); £3,752,367.09 -> £3,342,761.09 (10.9%); £3,752,367.25 -> £3,342,761.09 (10.9%); £3,752,367.41 -> £3,342,761.10 (10.9%); £3,752,367.56 -> £3,342,761.10 (10.9%); £3,752,367.73 -> £3,342,761.10 (10.9%); £3,752,367.89 -> £3,342,761.10 (10.9%); £3,752,368.05 -> £3,342,761.09 (10.9%); £3,752,368.22 -> £3,342,761.14 (10.9%); £3,752,368.42 -> £3,342,761.19 (10.9%); £3,752,368.63 -> £3,342,761.24 (10.9%); £3,752,368.85 -> £3,342,761.29 (10.9%); £3,752,369.10 -> £3,342,761.33 (10.9%); £3,752,369.36 -> £3,342,761.38 (10.9%); £3,752,369.62 -> £3,342,761.42 (10.9%); £3,752,369.88 -> £3,342,761.45 (10.9%); £3,752,370.14 -> £3,342,761.45 (10.9%); £3,752,370.41 -> £3,342,761.45 (10.9%); £3,752,370.68 -> £3,342,761.45 (10.9%); £3,752,370.94 -> £3,342,761.45 (10.9%); £3,752,371.21 -> £3,342,761.44 (10.9%); £3,752,371.47 -> £3,342,761.44 (10.9%); £3,752,371.75 -> £3,342,761.44 (10.9%); £3,752,372.01 -> £3,342,761.44 (10.9%); £3,752,372.27 -> £3,342,761.44 (10.9%); £3,752,372.53 -> £3,342,761.44 (10.9%); £3,752,372.80 -> £3,342,761.48 (10.9%); £3,752,373.05 -> £3,342,761.54 (10.9%); £3,752,373.25 -> £3,342,761.60 (10.9%); £3,752,373.44 -> £3,342,761.67 (10.9%); £3,752,373.64 -> £3,342,761.74 (10.9%); £3,752,373.90 -> £3,342,761.80 (10.9%); £3,752,374.16 -> £3,342,761.89 (10.9%); £3,752,374.42 -> £3,342,761.97 (10.9%); £3,752,374.70 -> £3,342,761.95 (10.9%); £3,752,374.95 -> £3,342,761.92 (10.9%); £3,752,375.23 -> £3,342,761.90 (10.9%); £3,752,375.49 -> £3,342,761.88 (10.9%); £3,752,375.75 -> £3,342,761.87 (10.9%); £3,752,376.02 -> £3,342,761.87 (10.9%); £3,752,376.27 -> £3,342,761.86 (10.9%); £3,752,376.49 -> £3,342,761.86 (10.9%); £3,752,376.69 -> £3,342,761.86 (10.9%); £3,752,376.85 -> £3,342,761.86 (10.9%); £3,752,377.01 -> £3,342,761.86 (10.9%); £3,752,377.17 -> £3,342,761.86 (10.9%); £3,752,377.33 -> £3,342,761.86 (10.9%); £3,752,377.49 -> £3,342,761.87 (10.9%); £3,752,377.65 -> £3,342,761.87 (10.9%); £3,752,377.81 -> £3,342,761.87 (10.9%); £3,752,377.97 -> £3,342,761.87 (10.9%); £3,752,378.12 -> £3,342,761.88 (10.9%); £3,752,378.28 -> £3,342,761.88 (10.9%); £3,752,378.44 -> £3,342,761.88 (10.9%); £3,752,378.60 -> £3,342,761.88 (10.9%); £3,752,378.75 -> £3,342,761.87 (10.9%); £3,752,378.93 -> £3,342,761.91 (10.9%); £3,752,379.12 -> £3,342,761.97 (10.9%); £3,752,379.33 -> £3,342,762.02 (10.9%); £3,752,379.57 -> £3,342,762.07 (10.9%); £3,752,379.82 -> £3,342,762.11 (10.9%); £3,752,380.08 -> £3,342,762.16 (10.9%); £3,752,380.34 -> £3,342,762.19 (10.9%); £3,752,380.61 -> £3,342,762.23 (10.9%); £3,752,380.88 -> £3,342,762.23 (10.9%); £3,752,381.14 -> £3,342,762.23 (10.9%); £3,752,381.40 -> £3,342,762.23 (10.9%); £3,752,381.67 -> £3,342,762.23 (10.9%); £3,752,381.93 -> £3,342,762.22 (10.9%); £3,752,382.19 -> £3,342,762.22 (10.9%); £3,752,382.45 -> £3,342,762.22 (10.9%); £3,752,382.72 -> £3,342,762.22 (10.9%); £3,752,382.99 -> £3,342,762.22 (10.9%); £3,752,383.25 -> £3,342,762.22 (10.9%); £3,752,383.52 -> £3,342,762.26 (10.9%); £3,752,383.79 -> £3,342,762.32 (10.9%); £3,752,384.04 -> £3,342,762.39 (10.9%); £3,752,384.31 -> £3,342,762.45 (10.9%); £3,752,384.58 -> £3,342,762.52 (10.9%); £3,752,384.83 -> £3,342,762.59 (10.9%); £3,752,385.11 -> £3,342,762.67 (10.9%); £3,752,385.30 -> £3,342,762.75 (10.9%); £3,752,385.56 -> £3,342,762.73 (10.9%); £3,752,385.81 -> £3,342,762.71 (10.9%); £3,752,386.08 -> £3,342,762.68 (10.9%); £3,752,386.35 -> £3,342,762.66 (10.9%); £3,752,386.62 -> £3,342,762.66 (10.9%); £3,752,386.88 -> £3,342,762.65 (10.9%); £3,752,387.12 -> £3,342,762.65 (10.9%); £3,752,387.35 -> £3,342,762.64 (10.9%); £3,752,387.55 -> £3,342,762.64 (10.9%); £3,752,387.72 -> £3,342,762.64 (10.9%); £3,752,387.87 -> £3,342,762.64 (10.9%); £3,752,388.04 -> £3,342,762.65 (10.9%); £3,752,388.20 -> £3,342,762.65 (10.9%); £3,752,388.36 -> £3,342,762.65 (10.9%); £3,752,388.52 -> £3,342,762.65 (10.9%); £3,752,388.68 -> £3,342,762.65 (10.9%); £3,752,388.84 -> £3,342,762.66 (10.9%); £3,752,389.00 -> £3,342,762.66 (10.9%); £3,752,389.16 -> £3,342,762.66 (10.9%); £3,752,389.32 -> £3,342,762.66 (10.9%); £3,752,389.48 -> £3,342,762.66 (10.9%); £3,752,389.64 -> £3,342,762.65 (10.9%); £3,752,389.83 -> £3,342,762.70 (10.9%); £3,752,390.02 -> £3,342,762.75 (10.9%); £3,752,390.23 -> £3,342,762.80 (10.9%); £3,752,390.46 -> £3,342,762.85 (10.9%); £3,752,390.71 -> £3,342,762.90 (10.9%); £3,752,390.98 -> £3,342,762.94 (10.9%); £3,752,391.25 -> £3,342,762.98 (10.9%); £3,752,391.51 -> £3,342,763.01 (10.9%); £3,752,391.78 -> £3,342,763.01 (10.9%); £3,752,392.04 -> £3,342,763.01 (10.9%); £3,752,392.31 -> £3,342,763.01 (10.9%); £3,752,392.57 -> £3,342,763.01 (10.9%); £3,752,392.84 -> £3,342,763.01 (10.9%); £3,752,393.11 -> £3,342,763.01 (10.9%); £3,752,393.38 -> £3,342,763.01 (10.9%); £3,752,393.64 -> £3,342,763.01 (10.9%); £3,752,393.91 -> £3,342,763.00 (10.9%); £3,752,394.19 -> £3,342,763.01 (10.9%); £3,752,394.45 -> £3,342,763.04 (10.9%); £3,752,394.72 -> £3,342,763.10 (10.9%); £3,752,394.98 -> £3,342,763.17 (10.9%); £3,752,395.25 -> £3,342,763.23 (10.9%); £3,752,395.51 -> £3,342,763.30 (10.9%); £3,752,395.71 -> £3,342,763.37 (10.9%); £3,752,395.91 -> £3,342,763.45 (10.9%); £3,752,396.18 -> £3,342,763.53 (10.9%); £3,752,396.44 -> £3,342,763.51 (10.9%); £3,752,396.70 -> £3,342,763.48 (10.9%); £3,752,396.98 -> £3,342,763.46 (10.9%); £3,752,397.25 -> £3,342,763.44 (10.9%); £3,752,397.51 -> £3,342,763.44 (10.9%); £3,752,397.78 -> £3,342,763.43 (10.9%); £3,752,398.03 -> £3,342,763.43 (10.9%); £3,752,398.25 -> £3,342,763.42 (10.9%); £3,752,398.46 -> £3,342,763.42 (10.9%); £3,752,398.61 -> £3,342,763.42 (10.9%); £3,752,398.77 -> £3,342,763.42 (10.9%); £3,752,398.93 -> £3,342,763.43 (10.9%); £3,752,399.09 -> £3,342,763.43 (10.9%); £3,752,399.25 -> £3,342,763.43 (10.9%); £3,752,399.41 -> £3,342,763.43 (10.9%); £3,752,399.58 -> £3,342,763.43 (10.9%); £3,752,399.74 -> £3,342,763.44 (10.9%); £3,752,399.90 -> £3,342,763.44 (10.9%); £3,752,400.06 -> £3,342,763.44 (10.9%); £3,752,400.22 -> £3,342,763.44 (10.9%); £3,752,400.38 -> £3,342,763.44 (10.9%); £3,752,400.54 -> £3,342,763.43 (10.9%); £3,752,400.72 -> £3,342,763.48 (10.9%); £3,752,400.92 -> £3,342,763.53 (10.9%); £3,752,401.13 -> £3,342,763.58 (10.9%); £3,752,401.37 -> £3,342,763.63 (10.9%); £3,752,401.62 -> £3,342,763.67 (10.9%); £3,752,401.89 -> £3,342,763.72 (10.9%); £3,752,402.15 -> £3,342,763.75 (10.9%); £3,752,402.42 -> £3,342,763.79 (10.9%); £3,752,402.69 -> £3,342,763.79 (10.9%); £3,752,402.95 -> £3,342,763.79 (10.9%); £3,752,403.21 -> £3,342,763.78 (10.9%); £3,752,403.48 -> £3,342,763.78 (10.9%); £3,752,403.76 -> £3,342,763.78 (10.9%); £3,752,404.04 -> £3,342,763.78 (10.9%); £3,752,404.30 -> £3,342,763.78 (10.9%); £3,752,404.56 -> £3,342,763.78 (10.9%); £3,752,404.82 -> £3,342,763.78 (10.9%); £3,752,405.09 -> £3,342,763.78 (10.9%); £3,752,405.36 -> £3,342,763.81 (10.9%); £3,752,405.63 -> £3,342,763.87 (10.9%); £3,752,405.91 -> £3,342,763.94 (10.9%); £3,752,406.18 -> £3,342,764.01 (10.9%); £3,752,406.44 -> £3,342,764.07 (10.9%); £3,752,406.64 -> £3,342,764.14 (10.9%); £3,752,406.91 -> £3,342,764.22 (10.9%); £3,752,407.19 -> £3,342,764.31 (10.9%); £3,752,407.45 -> £3,342,764.28 (10.9%); £3,752,407.73 -> £3,342,764.26 (10.9%); £3,752,408.00 -> £3,342,764.23 (10.9%); £3,752,408.27 -> £3,342,764.21 (10.9%); £3,752,408.53 -> £3,342,764.21 (10.9%); £3,752,408.80 -> £3,342,764.20 (10.9%); £3,752,409.04 -> £3,342,764.20 (10.9%); £3,752,409.27 -> £3,342,764.19 (10.9%); £3,752,409.47 -> £3,342,764.19 (10.9%); £3,752,409.64 -> £3,342,764.19 (10.9%); £3,752,409.80 -> £3,342,764.19 (10.9%); £3,752,409.96 -> £3,342,764.19 (10.9%); £3,752,410.12 -> £3,342,764.20 (10.9%); £3,752,410.27 -> £3,342,764.20 (10.9%); £3,752,410.44 -> £3,342,764.20 (10.9%); £3,752,410.60 -> £3,342,764.20 (10.9%); £3,752,410.76 -> £3,342,764.21 (10.9%); £3,752,410.92 -> £3,342,764.21 (10.9%); £3,752,411.08 -> £3,342,764.21 (10.9%); £3,752,411.24 -> £3,342,764.21 (10.9%); £3,752,411.40 -> £3,342,764.21 (10.9%); £3,752,411.56 -> £3,342,764.20 (10.9%); £3,752,411.73 -> £3,342,764.25 (10.9%); £3,752,411.93 -> £3,342,764.30 (10.9%); £3,752,412.15 -> £3,342,764.35 (10.9%); £3,752,412.37 -> £3,342,764.40 (10.9%); £3,752,412.63 -> £3,342,764.45 (10.9%); £3,752,412.90 -> £3,342,764.49 (10.9%); £3,752,413.16 -> £3,342,764.53 (10.9%); £3,752,413.42 -> £3,342,764.57 (10.9%); £3,752,413.67 -> £3,342,764.56 (10.9%); £3,752,413.93 -> £3,342,764.56 (10.9%); £3,752,414.19 -> £3,342,764.56 (10.9%); £3,752,414.46 -> £3,342,764.56 (10.9%); £3,752,414.72 -> £3,342,764.56 (10.9%); £3,752,415.00 -> £3,342,764.56 (10.9%); £3,752,415.27 -> £3,342,764.56 (10.9%); £3,752,415.53 -> £3,342,764.56 (10.9%); £3,752,415.79 -> £3,342,764.55 (10.9%); £3,752,416.06 -> £3,342,764.56 (10.9%); £3,752,416.32 -> £3,342,764.59 (10.9%); £3,752,416.59 -> £3,342,764.65 (10.9%); £3,752,416.84 -> £3,342,764.72 (10.9%); £3,752,417.04 -> £3,342,764.78 (10.9%); £3,752,417.25 -> £3,342,764.85 (10.9%); £3,752,417.44 -> £3,342,764.92 (10.9%); £3,752,417.65 -> £3,342,765.00 (10.9%); £3,752,417.85 -> £3,342,765.08 (10.9%); £3,752,418.11 -> £3,342,765.06 (10.9%); £3,752,418.38 -> £3,342,765.03 (10.9%); £3,752,418.65 -> £3,342,765.01 (10.9%); £3,752,418.91 -> £3,342,764.99 (10.9%); £3,752,419.18 -> £3,342,764.98 (10.9%); £3,752,419.44 -> £3,342,764.98 (10.9%); £3,752,419.69 -> £3,342,764.97 (10.9%); £3,752,419.90 -> £3,342,764.97 (10.9%); £3,752,420.10 -> £3,342,764.96 (10.9%); £3,752,420.25 -> £3,342,764.96 (10.9%); £3,752,420.39 -> £3,342,764.96 (10.9%); £3,752,420.53 -> £3,342,764.96 (10.9%); £3,752,420.67 -> £3,342,764.97 (10.9%); £3,752,420.81 -> £3,342,764.97 (10.9%); £3,752,420.95 -> £3,342,764.97 (10.9%); £3,752,421.09 -> £3,342,764.97 (10.9%); £3,752,421.23 -> £3,342,764.97 (10.9%); £3,752,421.37 -> £3,342,764.98 (10.9%); £3,752,421.51 -> £3,342,764.98 (10.9%); £3,752,421.65 -> £3,342,764.98 (10.9%); £3,752,421.80 -> £3,342,764.98 (10.9%); £3,752,421.93 -> £3,342,764.97 (10.9%); £3,752,422.09 -> £3,342,764.97 (10.9%); £3,752,422.26 -> £3,342,764.97 (10.9%); £3,752,422.45 -> £3,342,764.96 (10.9%); £3,752,422.66 -> £3,342,764.95 (10.9%); £3,752,422.88 -> £3,342,764.94 (10.9%); £3,752,423.12 -> £3,342,764.93 (10.9%); £3,752,423.35 -> £3,342,764.93 (10.9%); £3,752,423.58 -> £3,342,764.93 (10.9%); £3,752,423.82 -> £3,342,764.92 (10.9%); £3,752,424.05 -> £3,342,764.92 (10.9%); £3,752,424.29 -> £3,342,764.91 (10.9%); £3,752,424.52 -> £3,342,764.91 (10.9%); £3,752,424.75 -> £3,342,764.90 (10.9%); £3,752,424.98 -> £3,342,764.90 (10.9%); £3,752,425.22 -> £3,342,764.90 (10.9%); £3,752,425.45 -> £3,342,764.90 (10.9%); £3,752,425.70 -> £3,342,764.89 (10.9%); £3,752,425.94 -> £3,342,764.89 (10.9%); £3,752,426.18 -> £3,342,764.89 (10.9%); £3,752,426.35 -> £3,342,764.88 (10.9%); £3,752,426.52 -> £3,342,764.86 (10.9%); £3,752,426.70 -> £3,342,764.84 (10.9%); £3,752,426.87 -> £3,342,764.83 (10.9%); £3,752,427.05 -> £3,342,764.81 (10.9%); £3,752,427.23 -> £3,342,764.78 (10.9%); £3,752,427.41 -> £3,342,764.75 (10.9%); £3,752,427.65 -> £3,342,764.72 (10.9%); £3,752,427.88 -> £3,342,764.70 (10.9%); £3,752,428.12 -> £3,342,764.68 (10.9%); £3,752,428.35 -> £3,342,764.66 (10.9%); £3,752,428.59 -> £3,342,764.65 (10.9%); £3,752,428.82 -> £3,342,764.65 (10.9%); £3,752,429.04 -> £3,342,764.64 (10.9%); £3,752,429.24 -> £3,342,764.64 (10.9%); £3,752,429.42 -> £3,342,764.63 (10.9%); £3,752,429.56 -> £3,342,764.63 (10.9%); £3,752,429.71 -> £3,342,764.63 (10.9%); £3,752,429.85 -> £3,342,764.63 (10.9%); £3,752,429.99 -> £3,342,764.63 (10.9%); £3,752,430.13 -> £3,342,764.63 (10.9%); £3,752,430.27 -> £3,342,764.64 (10.9%); £3,752,430.40 -> £3,342,764.64 (10.9%); £3,752,430.54 -> £3,342,764.64 (10.9%); £3,752,430.69 -> £3,342,764.64 (10.9%); £3,752,430.82 -> £3,342,764.64 (10.9%); £3,752,430.96 -> £3,342,764.64 (10.9%); £3,752,431.10 -> £3,342,764.64 (10.9%); £3,752,431.24 -> £3,342,764.64 (10.9%); £3,752,431.40 -> £3,342,764.64 (10.9%); £3,752,431.57 -> £3,342,764.64 (10.9%); £3,752,431.76 -> £3,342,764.64 (10.9%); £3,752,431.96 -> £3,342,764.63 (10.9%); £3,752,432.18 -> £3,342,764.62 (10.9%); £3,752,432.41 -> £3,342,764.61 (10.9%); £3,752,432.65 -> £3,342,764.60 (10.9%); £3,752,432.89 -> £3,342,764.60 (10.9%); £3,752,433.13 -> £3,342,764.59 (10.9%); £3,752,433.36 -> £3,342,764.58 (10.9%); £3,752,433.59 -> £3,342,764.57 (10.9%); £3,752,433.82 -> £3,342,764.56 (10.9%); £3,752,434.06 -> £3,342,764.55 (10.9%); £3,752,434.30 -> £3,342,764.54 (10.9%); £3,752,434.53 -> £3,342,764.54 (10.9%); £3,752,434.76 -> £3,342,764.53 (10.9%); £3,752,434.99 -> £3,342,764.53 (10.9%); £3,752,435.23 -> £3,342,764.53 (10.9%); £3,752,435.46 -> £3,342,764.52 (10.9%); £3,752,435.64 -> £3,342,764.51 (10.9%); £3,752,435.81 -> £3,342,764.49 (10.9%); £3,752,436.00 -> £3,342,764.47 (10.9%); £3,752,436.17 -> £3,342,764.45 (10.9%); £3,752,436.40 -> £3,342,764.43 (10.9%); £3,752,436.64 -> £3,342,764.41 (10.9%); £3,752,436.81 -> £3,342,764.38 (10.9%); £3,752,437.05 -> £3,342,764.35 (10.9%); £3,752,437.28 -> £3,342,764.33 (10.9%); £3,752,437.51 -> £3,342,764.31 (10.9%); £3,752,437.74 -> £3,342,764.29 (10.9%); £3,752,437.98 -> £3,342,764.28 (10.9%); £3,752,438.21 -> £3,342,764.28 (10.9%); £3,752,438.43 -> £3,342,764.27 (10.9%); £3,752,438.63 -> £3,342,764.27 (10.9%); £3,752,438.80 -> £3,342,764.27 (10.9%); £3,752,438.96 -> £3,342,764.27 (10.9%); £3,752,439.12 -> £3,342,764.27 (10.9%); £3,752,439.28 -> £3,342,764.27 (10.9%); £3,752,439.44 -> £3,342,764.27 (10.9%); £3,752,439.60 -> £3,342,764.27 (10.9%); £3,752,439.76 -> £3,342,764.28 (10.9%); £3,752,439.92 -> £3,342,764.28 (10.9%); £3,752,440.08 -> £3,342,764.28 (10.9%); £3,752,440.24 -> £3,342,764.28 (10.9%); £3,752,440.40 -> £3,342,764.28 (10.9%); £3,752,440.56 -> £3,342,764.29 (10.9%); £3,752,440.72 -> £3,342,764.28 (10.9%); £3,752,440.88 -> £3,342,764.28 (10.9%); £3,752,441.05 -> £3,342,764.32 (10.9%); £3,752,441.25 -> £3,342,764.37 (10.9%); £3,752,441.47 -> £3,342,764.43 (10.9%); £3,752,441.70 -> £3,342,764.48 (10.9%); £3,752,441.94 -> £3,342,764.52 (10.9%); £3,752,442.20 -> £3,342,764.56 (10.9%); £3,752,442.46 -> £3,342,764.60 (10.9%); £3,752,442.73 -> £3,342,764.64 (10.9%); £3,752,443.00 -> £3,342,764.64 (10.9%); £3,752,443.26 -> £3,342,764.63 (10.9%); £3,752,443.53 -> £3,342,764.63 (10.9%); £3,752,443.78 -> £3,342,764.63 (10.9%); £3,752,444.04 -> £3,342,764.63 (10.9%); £3,752,444.32 -> £3,342,764.63 (10.9%); £3,752,444.58 -> £3,342,764.63 (10.9%); £3,752,444.84 -> £3,342,764.63 (10.9%); £3,752,445.11 -> £3,342,764.63 (10.9%); £3,752,445.37 -> £3,342,764.63 (10.9%); £3,752,445.63 -> £3,342,764.66 (10.9%); £3,752,445.90 -> £3,342,764.72 (10.9%); £3,752,446.17 -> £3,342,764.79 (10.9%); £3,752,446.43 -> £3,342,764.86 (10.9%); £3,752,446.69 -> £3,342,764.92 (10.9%); £3,752,446.95 -> £3,342,764.99 (10.9%); £3,752,447.21 -> £3,342,765.07 (10.9%); £3,752,447.41 -> £3,342,765.16 (10.9%); £3,752,447.67 -> £3,342,765.13 (10.9%); £3,752,447.93 -> £3,342,765.11 (10.9%); £3,752,448.19 -> £3,342,765.09 (10.9%); £3,752,448.44 -> £3,342,765.07 (10.9%); £3,752,448.70 -> £3,342,765.06 (10.9%); £3,752,448.96 -> £3,342,765.05 (10.9%); £3,752,449.21 -> £3,342,765.05 (10.9%); £3,752,449.44 -> £3,342,765.04 (10.9%); £3,752,449.65 -> £3,342,765.04 (10.9%); £3,752,449.80 -> £3,342,765.04 (10.9%); £3,752,449.96 -> £3,342,765.05 (10.9%); £3,752,450.12 -> £3,342,765.05 (10.9%); £3,752,450.27 -> £3,342,765.05 (10.9%); £3,752,450.43 -> £3,342,765.05 (10.9%); £3,752,450.59 -> £3,342,765.05 (10.9%); £3,752,450.74 -> £3,342,765.06 (10.9%); £3,752,450.90 -> £3,342,765.06 (10.9%); £3,752,451.06 -> £3,342,765.06 (10.9%); £3,752,451.21 -> £3,342,765.06 (10.9%); £3,752,451.36 -> £3,342,765.06 (10.9%); £3,752,451.52 -> £3,342,765.06 (10.9%); £3,752,451.68 -> £3,342,765.05 (10.9%); £3,752,451.86 -> £3,342,765.10 (10.9%); £3,752,452.05 -> £3,342,765.15 (10.9%); £3,752,452.26 -> £3,342,765.20 (10.9%); £3,752,452.49 -> £3,342,765.25 (10.9%); £3,752,452.74 -> £3,342,765.30 (10.9%); £3,752,453.00 -> £3,342,765.34 (10.9%); £3,752,453.25 -> £3,342,765.38 (10.9%); £3,752,453.51 -> £3,342,765.42 (10.9%); £3,752,453.76 -> £3,342,765.41 (10.9%); £3,752,454.02 -> £3,342,765.41 (10.9%); £3,752,454.28 -> £3,342,765.41 (10.9%); £3,752,454.54 -> £3,342,765.41 (10.9%); £3,752,454.81 -> £3,342,765.41 (10.9%); £3,752,455.07 -> £3,342,765.41 (10.9%); £3,752,455.32 -> £3,342,765.41 (10.9%); £3,752,455.59 -> £3,342,765.41 (10.9%); £3,752,455.85 -> £3,342,765.41 (10.9%); £3,752,456.10 -> £3,342,765.41 (10.9%); £3,752,456.37 -> £3,342,765.44 (10.9%); £3,752,456.64 -> £3,342,765.50 (10.9%); £3,752,456.90 -> £3,342,765.57 (10.9%); £3,752,457.09 -> £3,342,765.63 (10.9%); £3,752,457.29 -> £3,342,765.70 (10.9%); £3,752,457.49 -> £3,342,765.77 (10.9%); £3,752,457.69 -> £3,342,765.85 (10.9%); £3,752,457.95 -> £3,342,765.93 (10.9%); £3,752,458.20 -> £3,342,765.91 (10.9%); £3,752,458.47 -> £3,342,765.88 (10.9%); £3,752,458.74 -> £3,342,765.86 (10.9%); £3,752,459.00 -> £3,342,765.84 (10.9%); £3,752,459.26 -> £3,342,765.83 (10.9%); £3,752,459.52 -> £3,342,765.83 (10.9%); £3,752,459.76 -> £3,342,765.82 (10.9%); £3,752,459.99 -> £3,342,765.82 (10.9%); £3,752,460.19 -> £3,342,765.82 (10.9%); £3,752,460.35 -> £3,342,765.82 (10.9%); £3,752,460.51 -> £3,342,765.82 (10.9%); £3,752,460.66 -> £3,342,765.82 (10.9%); £3,752,460.82 -> £3,342,765.82 (10.9%); £3,752,460.98 -> £3,342,765.82 (10.9%); £3,752,461.13 -> £3,342,765.83 (10.9%); £3,752,461.29 -> £3,342,765.83 (10.9%); £3,752,461.45 -> £3,342,765.83 (10.9%); £3,752,461.61 -> £3,342,765.83 (10.9%); £3,752,461.76 -> £3,342,765.84 (10.9%); £3,752,461.92 -> £3,342,765.84 (10.9%); £3,752,462.08 -> £3,342,765.83 (10.9%); £3,752,462.23 -> £3,342,765.83 (10.9%); £3,752,462.42 -> £3,342,765.87 (10.9%); £3,752,462.61 -> £3,342,765.92 (10.9%); £3,752,462.81 -> £3,342,765.98 (10.9%); £3,752,463.04 -> £3,342,766.02 (10.9%); £3,752,463.28 -> £3,342,766.07 (10.9%); £3,752,463.53 -> £3,342,766.11 (10.9%); £3,752,463.79 -> £3,342,766.15 (10.9%); £3,752,464.05 -> £3,342,766.19 (10.9%); £3,752,464.30 -> £3,342,766.19 (10.9%); £3,752,464.57 -> £3,342,766.18 (10.9%); £3,752,464.83 -> £3,342,766.18 (10.9%); £3,752,465.10 -> £3,342,766.18 (10.9%); £3,752,465.36 -> £3,342,766.18 (10.9%); £3,752,465.62 -> £3,342,766.18 (10.9%); £3,752,465.89 -> £3,342,766.18 (10.9%); £3,752,466.15 -> £3,342,766.18 (10.9%); £3,752,466.41 -> £3,342,766.18 (10.9%); £3,752,466.68 -> £3,342,766.18 (10.9%); £3,752,466.94 -> £3,342,766.21 (10.9%); £3,752,467.13 -> £3,342,766.27 (10.9%); £3,752,467.39 -> £3,342,766.34 (10.9%); £3,752,467.59 -> £3,342,766.40 (10.9%); £3,752,467.79 -> £3,342,766.47 (10.9%); £3,752,468.06 -> £3,342,766.54 (10.9%); £3,752,468.32 -> £3,342,766.62 (10.9%); £3,752,468.51 -> £3,342,766.70 (10.9%); £3,752,468.78 -> £3,342,766.68 (10.9%); £3,752,469.03 -> £3,342,766.65 (10.9%); £3,752,469.30 -> £3,342,766.63 (10.9%); £3,752,469.57 -> £3,342,766.61 (10.9%); £3,752,469.84 -> £3,342,766.60 (10.9%); £3,752,470.10 -> £3,342,766.60 (10.9%); £3,752,470.34 -> £3,342,766.59 (10.9%); £3,752,470.57 -> £3,342,766.59 (10.9%); £3,752,470.77 -> £3,342,766.59 (10.9%); £3,752,470.93 -> £3,342,766.59 (10.9%); £3,752,471.08 -> £3,342,766.59 (10.9%); £3,752,471.23 -> £3,342,766.59 (10.9%); £3,752,471.39 -> £3,342,766.59 (10.9%); £3,752,471.55 -> £3,342,766.59 (10.9%); £3,752,471.70 -> £3,342,766.59 (10.9%); £3,752,471.86 -> £3,342,766.60 (10.9%); £3,752,472.01 -> £3,342,766.60 (10.9%); £3,752,472.17 -> £3,342,766.60 (10.9%); £3,752,472.32 -> £3,342,766.60 (10.9%); £3,752,472.48 -> £3,342,766.60 (10.9%); £3,752,472.63 -> £3,342,766.60 (10.9%); £3,752,472.78 -> £3,342,766.60 (10.9%); £3,752,472.95 -> £3,342,766.64 (10.9%); £3,752,473.14 -> £3,342,766.70 (10.9%); £3,752,473.34 -> £3,342,766.75 (10.9%); £3,752,473.58 -> £3,342,766.80 (10.9%); £3,752,473.82 -> £3,342,766.84 (10.9%); £3,752,474.07 -> £3,342,766.89 (10.9%); £3,752,474.34 -> £3,342,766.92 (10.9%); £3,752,474.60 -> £3,342,766.96 (10.9%); £3,752,474.85 -> £3,342,766.96 (10.9%); £3,752,475.11 -> £3,342,766.96 (10.9%); £3,752,475.36 -> £3,342,766.95 (10.9%); £3,752,475.62 -> £3,342,766.95 (10.9%); £3,752,475.87 -> £3,342,766.95 (10.9%); £3,752,476.13 -> £3,342,766.95 (10.9%); £3,752,476.39 -> £3,342,766.95 (10.9%); £3,752,476.65 -> £3,342,766.95 (10.9%); £3,752,476.90 -> £3,342,766.95 (10.9%); £3,752,477.15 -> £3,342,766.95 (10.9%); £3,752,477.41 -> £3,342,766.98 (10.9%); £3,752,477.66 -> £3,342,767.04 (10.9%); £3,752,477.92 -> £3,342,767.11 (10.9%); £3,752,478.18 -> £3,342,767.18 (10.9%); £3,752,478.37 -> £3,342,767.24 (10.9%); £3,752,478.56 -> £3,342,767.31 (10.9%); £3,752,478.83 -> £3,342,767.39 (10.9%); £3,752,479.02 -> £3,342,767.47 (10.9%); £3,752,479.27 -> £3,342,767.45 (10.9%); £3,752,479.53 -> £3,342,767.43 (10.9%); £3,752,479.79 -> £3,342,767.40 (10.9%); £3,752,480.04 -> £3,342,767.38 (10.9%); £3,752,480.31 -> £3,342,767.37 (10.9%); £3,752,480.57 -> £3,342,767.37 (10.9%); £3,752,480.81 -> £3,342,767.36 (10.9%); £3,752,481.04 -> £3,342,767.36 (10.9%); £3,752,481.23 -> £3,342,767.36 (10.9%); £3,752,481.39 -> £3,342,767.36 (10.9%); £3,752,481.54 -> £3,342,767.36 (10.9%); £3,752,481.70 -> £3,342,767.36 (10.9%); £3,752,481.86 -> £3,342,767.36 (10.9%); £3,752,482.02 -> £3,342,767.36 (10.9%); £3,752,482.18 -> £3,342,767.37 (10.9%); £3,752,482.33 -> £3,342,767.37 (10.9%); £3,752,482.48 -> £3,342,767.37 (10.9%); £3,752,482.64 -> £3,342,767.37 (10.9%); £3,752,482.80 -> £3,342,767.38 (10.9%); £3,752,482.95 -> £3,342,767.38 (10.9%); £3,752,483.10 -> £3,342,767.37 (10.9%); £3,752,483.26 -> £3,342,767.37 (10.9%); £3,752,483.43 -> £3,342,767.41 (10.9%); £3,752,483.62 -> £3,342,767.46 (10.9%); £3,752,483.82 -> £3,342,767.51 (10.9%); £3,752,484.04 -> £3,342,767.56 (10.9%); £3,752,484.27 -> £3,342,767.61 (10.9%); £3,752,484.53 -> £3,342,767.65 (10.9%); £3,752,484.79 -> £3,342,767.69 (10.9%); £3,752,485.05 -> £3,342,767.72 (10.9%); £3,752,485.31 -> £3,342,767.72 (10.9%); £3,752,485.58 -> £3,342,767.72 (10.9%); £3,752,485.84 -> £3,342,767.72 (10.9%); £3,752,486.11 -> £3,342,767.72 (10.9%); £3,752,486.36 -> £3,342,767.72 (10.9%); £3,752,486.62 -> £3,342,767.71 (10.9%); £3,752,486.89 -> £3,342,767.71 (10.9%); £3,752,487.15 -> £3,342,767.71 (10.9%); £3,752,487.41 -> £3,342,767.71 (10.9%); £3,752,487.67 -> £3,342,767.71 (10.9%); £3,752,487.93 -> £3,342,767.75 (10.9%); £3,752,488.18 -> £3,342,767.81 (10.9%); £3,752,488.44 -> £3,342,767.87 (10.9%); £3,752,488.71 -> £3,342,767.94 (10.9%); £3,752,488.97 -> £3,342,768.00 (10.9%); £3,752,489.24 -> £3,342,768.07 (10.9%); £3,752,489.50 -> £3,342,768.15 (10.9%); £3,752,489.77 -> £3,342,768.24 (10.9%); £3,752,490.02 -> £3,342,768.21 (10.9%); £3,752,490.29 -> £3,342,768.19 (10.9%); £3,752,490.55 -> £3,342,768.16 (10.9%); £3,752,490.82 -> £3,342,768.14 (10.9%); £3,752,491.08 -> £3,342,768.13 (10.9%); £3,752,491.34 -> £3,342,768.13 (10.9%); £3,752,491.58 -> £3,342,768.12 (10.9%); £3,752,491.80 -> £3,342,768.12 (10.9%); £3,752,492.00 -> £3,342,768.11 (10.9%); £3,752,492.14 -> £3,342,768.11 (10.9%); £3,752,492.27 -> £3,342,768.11 (10.9%); £3,752,492.41 -> £3,342,768.11 (10.9%); £3,752,492.54 -> £3,342,768.12 (10.9%); £3,752,492.68 -> £3,342,768.12 (10.9%); £3,752,492.82 -> £3,342,768.12 (10.9%); £3,752,492.95 -> £3,342,768.12 (10.9%); £3,752,493.08 -> £3,342,768.12 (10.9%); £3,752,493.22 -> £3,342,768.13 (10.9%); £3,752,493.36 -> £3,342,768.13 (10.9%); £3,752,493.50 -> £3,342,768.13 (10.9%); £3,752,493.64 -> £3,342,768.13 (10.9%); £3,752,493.77 -> £3,342,768.13 (10.9%); £3,752,493.93 -> £3,342,768.12 (10.9%); £3,752,494.09 -> £3,342,768.12 (10.9%); £3,752,494.27 -> £3,342,768.11 (10.9%); £3,752,494.47 -> £3,342,768.10 (10.9%); £3,752,494.69 -> £3,342,768.09 (10.9%); £3,752,494.91 -> £3,342,768.09 (10.9%); £3,752,495.14 -> £3,342,768.08 (10.9%); £3,752,495.36 -> £3,342,768.08 (10.9%); £3,752,495.59 -> £3,342,768.07 (10.9%); £3,752,495.81 -> £3,342,768.07 (10.9%); £3,752,496.03 -> £3,342,768.06 (10.9%); £3,752,496.25 -> £3,342,768.06 (10.9%); £3,752,496.48 -> £3,342,768.06 (10.9%); £3,752,496.72 -> £3,342,768.05 (10.9%); £3,752,496.95 -> £3,342,768.05 (10.9%); £3,752,497.18 -> £3,342,768.05 (10.9%); £3,752,497.40 -> £3,342,768.04 (10.9%); £3,752,497.63 -> £3,342,768.05 (10.9%); £3,752,497.86 -> £3,342,768.04 (10.9%); £3,752,498.08 -> £3,342,768.03 (10.9%); £3,752,498.31 -> £3,342,768.02 (10.9%); £3,752,498.54 -> £3,342,768.00 (10.9%); £3,752,498.76 -> £3,342,767.98 (10.9%); £3,752,498.98 -> £3,342,767.96 (10.9%); £3,752,499.21 -> £3,342,767.93 (10.9%); £3,752,499.44 -> £3,342,767.91 (10.9%); £3,752,499.67 -> £3,342,767.88 (10.9%); £3,752,499.90 -> £3,342,767.86 (10.9%); £3,752,500.13 -> £3,342,767.84 (10.9%); £3,752,500.35 -> £3,342,767.82 (10.9%); £3,752,500.58 -> £3,342,767.81 (10.9%); £3,752,500.79 -> £3,342,767.81 (10.9%); £3,752,501.01 -> £3,342,767.80 (10.9%); £3,752,501.21 -> £3,342,767.80 (10.9%); £3,752,501.38 -> £3,342,767.80 (10.9%); £3,752,501.51 -> £3,342,767.79 (10.9%); £3,752,501.65 -> £3,342,767.79 (10.9%); £3,752,501.78 -> £3,342,767.79 (10.9%); £3,752,501.91 -> £3,342,767.79 (10.9%); £3,752,502.05 -> £3,342,767.80 (10.9%); £3,752,502.19 -> £3,342,767.80 (10.9%); £3,752,502.32 -> £3,342,767.80 (10.9%); £3,752,502.45 -> £3,342,767.80 (10.9%); £3,752,502.59 -> £3,342,767.80 (10.9%); £3,752,502.73 -> £3,342,767.80 (10.9%); £3,752,502.87 -> £3,342,767.81 (10.9%); £3,752,503.00 -> £3,342,767.81 (10.9%); £3,752,503.14 -> £3,342,767.80 (10.9%); £3,752,503.29 -> £3,342,767.80 (10.9%); £3,752,503.46 -> £3,342,767.80 (10.9%); £3,752,503.64 -> £3,342,767.80 (10.9%); £3,752,503.83 -> £3,342,767.79 (10.9%); £3,752,504.05 -> £3,342,767.78 (10.9%); £3,752,504.27 -> £3,342,767.77 (10.9%); £3,752,504.49 -> £3,342,767.77 (10.9%); £3,752,504.72 -> £3,342,767.76 (10.9%); £3,752,504.95 -> £3,342,767.75 (10.9%); £3,752,505.17 -> £3,342,767.74 (10.9%); £3,752,505.39 -> £3,342,767.73 (10.9%); £3,752,505.61 -> £3,342,767.72 (10.9%); £3,752,505.84 -> £3,342,767.72 (10.9%); £3,752,506.07 -> £3,342,767.71 (10.9%); £3,752,506.30 -> £3,342,767.70 (10.9%); £3,752,506.52 -> £3,342,767.70 (10.9%); £3,752,506.74 -> £3,342,767.69 (10.9%); £3,752,506.98 -> £3,342,767.69 (10.9%); £3,752,507.21 -> £3,342,767.69 (10.9%); £3,752,507.44 -> £3,342,767.67 (10.9%); £3,752,507.67 -> £3,342,767.66 (10.9%); £3,752,507.90 -> £3,342,767.64 (10.9%); £3,752,508.12 -> £3,342,767.62 (10.9%); £3,752,508.34 -> £3,342,767.60 (10.9%); £3,752,508.57 -> £3,342,767.57 (10.9%); £3,752,508.79 -> £3,342,767.54 (10.9%); £3,752,509.00 -> £3,342,767.52 (10.9%); £3,752,509.23 -> £3,342,767.50 (10.9%); £3,752,509.46 -> £3,342,767.47 (10.9%); £3,752,509.70 -> £3,342,767.45 (10.9%); £3,752,509.93 -> £3,342,767.44 (10.9%); £3,752,510.15 -> £3,342,767.44 (10.9%); £3,752,510.36 -> £3,342,767.43 (10.9%); £3,752,510.55 -> £3,342,767.43 (10.9%); £3,752,510.73 -> £3,342,767.43 (10.9%); £3,752,510.88 -> £3,342,767.43 (10.9%); £3,752,511.04 -> £3,342,767.43 (10.9%); £3,752,511.19 -> £3,342,767.43 (10.9%); £3,752,511.35 -> £3,342,767.43 (10.9%); £3,752,511.50 -> £3,342,767.44 (10.9%); £3,752,511.66 -> £3,342,767.44 (10.9%); £3,752,511.82 -> £3,342,767.44 (10.9%); £3,752,511.97 -> £3,342,767.44 (10.9%); £3,752,512.12 -> £3,342,767.44 (10.9%); £3,752,512.27 -> £3,342,767.45 (10.9%); £3,752,512.43 -> £3,342,767.45 (10.9%); £3,752,512.59 -> £3,342,767.44 (10.9%); £3,752,512.74 -> £3,342,767.44 (10.9%); £3,752,512.91 -> £3,342,767.48 (10.9%); £3,752,513.10 -> £3,342,767.53 (10.9%); £3,752,513.31 -> £3,342,767.59 (10.9%); £3,752,513.53 -> £3,342,767.64 (10.9%); £3,752,513.78 -> £3,342,767.68 (10.9%); £3,752,514.03 -> £3,342,767.73 (10.9%); £3,752,514.29 -> £3,342,767.76 (10.9%); £3,752,514.56 -> £3,342,767.80 (10.9%); £3,752,514.82 -> £3,342,767.80 (10.9%); £3,752,515.07 -> £3,342,767.80 (10.9%); £3,752,515.33 -> £3,342,767.79 (10.9%); £3,752,515.59 -> £3,342,767.79 (10.9%); £3,752,515.85 -> £3,342,767.79 (10.9%); £3,752,516.11 -> £3,342,767.79 (10.9%); £3,752,516.37 -> £3,342,767.79 (10.9%); £3,752,516.63 -> £3,342,767.79 (10.9%); £3,752,516.88 -> £3,342,767.79 (10.9%); £3,752,517.15 -> £3,342,767.79 (10.9%); £3,752,517.41 -> £3,342,767.82 (10.9%); £3,752,517.66 -> £3,342,767.88 (10.9%); £3,752,517.91 -> £3,342,767.95 (10.9%); £3,752,518.16 -> £3,342,768.02 (10.9%); £3,752,518.41 -> £3,342,768.08 (10.9%); £3,752,518.67 -> £3,342,768.15 (10.9%); £3,752,518.92 -> £3,342,768.23 (10.9%); £3,752,519.19 -> £3,342,768.31 (10.9%); £3,752,519.44 -> £3,342,768.29 (10.9%); £3,752,519.70 -> £3,342,768.27 (10.9%); £3,752,519.96 -> £3,342,768.24 (10.9%); £3,752,520.22 -> £3,342,768.22 (10.9%); £3,752,520.48 -> £3,342,768.22 (10.9%); £3,752,520.74 -> £3,342,768.21 (10.9%); £3,752,520.97 -> £3,342,768.20 (10.9%); £3,752,521.19 -> £3,342,768.20 (10.9%); £3,752,521.39 -> £3,342,768.20 (10.9%); £3,752,521.54 -> £3,342,768.20 (10.9%); £3,752,521.70 -> £3,342,768.20 (10.9%); £3,752,521.85 -> £3,342,768.20 (10.9%); £3,752,522.01 -> £3,342,768.20 (10.9%); £3,752,522.16 -> £3,342,768.21 (10.9%); £3,752,522.32 -> £3,342,768.21 (10.9%); £3,752,522.47 -> £3,342,768.21 (10.9%); £3,752,522.62 -> £3,342,768.21 (10.9%); £3,752,522.77 -> £3,342,768.22 (10.9%); £3,752,522.92 -> £3,342,768.22 (10.9%); £3,752,523.07 -> £3,342,768.22 (10.9%); £3,752,523.23 -> £3,342,768.21 (10.9%); £3,752,523.38 -> £3,342,768.21 (10.9%); £3,752,523.55 -> £3,342,768.25 (10.9%); £3,752,523.74 -> £3,342,768.31 (10.9%); £3,752,523.94 -> £3,342,768.36 (10.9%); £3,752,524.17 -> £3,342,768.41 (10.9%); £3,752,524.40 -> £3,342,768.45 (10.9%); £3,752,524.67 -> £3,342,768.50 (10.9%); £3,752,524.92 -> £3,342,768.53 (10.9%); £3,752,525.18 -> £3,342,768.57 (10.9%); £3,752,525.43 -> £3,342,768.57 (10.9%); £3,752,525.69 -> £3,342,768.57 (10.9%); £3,752,525.94 -> £3,342,768.56 (10.9%); £3,752,526.20 -> £3,342,768.56 (10.9%); £3,752,526.46 -> £3,342,768.56 (10.9%); £3,752,526.71 -> £3,342,768.56 (10.9%); £3,752,526.96 -> £3,342,768.56 (10.9%); £3,752,527.22 -> £3,342,768.56 (10.9%); £3,752,527.47 -> £3,342,768.56 (10.9%); £3,752,527.74 -> £3,342,768.56 (10.9%); £3,752,528.00 -> £3,342,768.60 (10.9%); £3,752,528.26 -> £3,342,768.65 (10.9%); £3,752,528.52 -> £3,342,768.72 (10.9%); £3,752,528.77 -> £3,342,768.79 (10.9%); £3,752,529.02 -> £3,342,768.85 (10.9%); £3,752,529.29 -> £3,342,768.92 (10.9%); £3,752,529.54 -> £3,342,769.00 (10.9%); £3,752,529.80 -> £3,342,769.08 (10.9%); £3,752,530.06 -> £3,342,769.06 (10.9%); £3,752,530.32 -> £3,342,769.03 (10.9%); £3,752,530.56 -> £3,342,769.01 (10.9%); £3,752,530.82 -> £3,342,768.99 (10.9%); £3,752,531.08 -> £3,342,768.98 (10.9%); £3,752,531.34 -> £3,342,768.98 (10.9%); £3,752,531.58 -> £3,342,768.97 (10.9%); £3,752,531.79 -> £3,342,768.97 (10.9%); £3,752,531.99 -> £3,342,768.97 (10.9%); £3,752,532.14 -> £3,342,768.97 (10.9%); £3,752,532.29 -> £3,342,768.97 (10.9%); £3,752,532.44 -> £3,342,768.97 (10.9%); £3,752,532.59 -> £3,342,768.97 (10.9%); £3,752,532.73 -> £3,342,768.97 (10.9%); £3,752,532.89 -> £3,342,768.98 (10.9%); £3,752,533.04 -> £3,342,768.98 (10.9%); £3,752,533.20 -> £3,342,768.98 (10.9%); £3,752,533.35 -> £3,342,768.98 (10.9%); £3,752,533.50 -> £3,342,768.98 (10.9%); £3,752,533.65 -> £3,342,768.98 (10.9%); £3,752,533.80 -> £3,342,768.98 (10.9%); £3,752,533.96 -> £3,342,768.97 (10.9%); £3,752,534.13 -> £3,342,769.02 (10.9%); £3,752,534.32 -> £3,342,769.07 (10.9%); £3,752,534.53 -> £3,342,769.12 (10.9%); £3,752,534.75 -> £3,342,769.17 (10.9%); £3,752,534.99 -> £3,342,769.22 (10.9%); £3,752,535.24 -> £3,342,769.26 (10.9%); £3,752,535.49 -> £3,342,769.30 (10.9%); £3,752,535.74 -> £3,342,769.33 (10.9%); £3,752,535.99 -> £3,342,769.33 (10.9%); £3,752,536.25 -> £3,342,769.33 (10.9%); £3,752,536.52 -> £3,342,769.33 (10.9%); £3,752,536.78 -> £3,342,769.33 (10.9%); £3,752,537.04 -> £3,342,769.33 (10.9%); £3,752,537.30 -> £3,342,769.33 (10.9%); £3,752,537.56 -> £3,342,769.33 (10.9%); £3,752,537.81 -> £3,342,769.33 (10.9%); £3,752,538.06 -> £3,342,769.32 (10.9%); £3,752,538.31 -> £3,342,769.33 (10.9%); £3,752,538.57 -> £3,342,769.36 (10.9%); £3,752,538.83 -> £3,342,769.42 (10.9%); £3,752,539.09 -> £3,342,769.48 (10.9%); £3,752,539.35 -> £3,342,769.55 (10.9%); £3,752,539.62 -> £3,342,769.62 (10.9%); £3,752,539.87 -> £3,342,769.68 (10.9%); £3,752,540.13 -> £3,342,769.77 (10.9%); £3,752,540.38 -> £3,342,769.85 (10.9%); £3,752,540.63 -> £3,342,769.82 (10.9%); £3,752,540.88 -> £3,342,769.80 (10.9%); £3,752,541.14 -> £3,342,769.78 (10.9%); £3,752,541.40 -> £3,342,769.76 (10.9%); £3,752,541.65 -> £3,342,769.75 (10.9%); £3,752,541.90 -> £3,342,769.75 (10.9%); £3,752,542.14 -> £3,342,769.74 (10.9%); £3,752,542.36 -> £3,342,769.74 (10.9%); £3,752,542.56 -> £3,342,769.74 (10.9%); £3,752,542.71 -> £3,342,769.74 (10.9%); £3,752,542.86 -> £3,342,769.74 (10.9%); £3,752,543.02 -> £3,342,769.74 (10.9%); £3,752,543.17 -> £3,342,769.74 (10.9%); £3,752,543.32 -> £3,342,769.74 (10.9%); £3,752,543.47 -> £3,342,769.75 (10.9%); £3,752,543.62 -> £3,342,769.75 (10.9%); £3,752,543.77 -> £3,342,769.75 (10.9%); £3,752,543.93 -> £3,342,769.75 (10.9%); £3,752,544.08 -> £3,342,769.75 (10.9%); £3,752,544.24 -> £3,342,769.75 (10.9%); £3,752,544.39 -> £3,342,769.75 (10.9%); £3,752,544.54 -> £3,342,769.74 (10.9%); £3,752,544.71 -> £3,342,769.79 (10.9%); £3,752,544.89 -> £3,342,769.84 (10.9%); £3,752,545.09 -> £3,342,769.89 (10.9%); £3,752,545.30 -> £3,342,769.94 (10.9%); £3,752,545.55 -> £3,342,769.99 (10.9%); £3,752,545.81 -> £3,342,770.03 (10.9%); £3,752,546.07 -> £3,342,770.07 (10.9%); £3,752,546.33 -> £3,342,770.10 (10.9%); £3,752,546.59 -> £3,342,770.10 (10.9%); £3,752,546.83 -> £3,342,770.10 (10.9%); £3,752,547.09 -> £3,342,770.10 (10.9%); £3,752,547.33 -> £3,342,770.10 (10.9%); £3,752,547.59 -> £3,342,770.09 (10.9%); £3,752,547.84 -> £3,342,770.09 (10.9%); £3,752,548.10 -> £3,342,770.09 (10.9%); £3,752,548.35 -> £3,342,770.09 (10.9%); £3,752,548.61 -> £3,342,770.09 (10.9%); £3,752,548.87 -> £3,342,770.09 (10.9%); £3,752,549.12 -> £3,342,770.13 (10.9%); £3,752,549.38 -> £3,342,770.19 (10.9%); £3,752,549.64 -> £3,342,770.25 (10.9%); £3,752,549.90 -> £3,342,770.32 (10.9%); £3,752,550.15 -> £3,342,770.39 (10.9%); £3,752,550.41 -> £3,342,770.45 (10.9%); £3,752,550.67 -> £3,342,770.54 (10.9%); £3,752,550.92 -> £3,342,770.62 (10.9%); £3,752,551.17 -> £3,342,770.60 (10.9%); £3,752,551.43 -> £3,342,770.57 (10.9%); £3,752,551.69 -> £3,342,770.55 (10.9%); £3,752,551.94 -> £3,342,770.53 (10.9%); £3,752,552.19 -> £3,342,770.52 (10.9%); £3,752,552.44 -> £3,342,770.52 (10.9%); £3,752,552.68 -> £3,342,770.51 (10.9%); £3,752,552.90 -> £3,342,770.51 (10.9%); £3,752,553.10 -> £3,342,770.51 (10.9%); £3,752,553.25 -> £3,342,770.51 (10.9%); £3,752,553.40 -> £3,342,770.51 (10.9%); £3,752,553.55 -> £3,342,770.51 (10.9%); £3,752,553.70 -> £3,342,770.51 (10.9%); £3,752,553.86 -> £3,342,770.51 (10.9%); £3,752,554.01 -> £3,342,770.52 (10.9%); £3,752,554.16 -> £3,342,770.52 (10.9%); £3,752,554.31 -> £3,342,770.52 (10.9%); £3,752,554.47 -> £3,342,770.52 (10.9%); £3,752,554.62 -> £3,342,770.52 (10.9%); £3,752,554.78 -> £3,342,770.53 (10.9%); £3,752,554.93 -> £3,342,770.52 (10.9%); £3,752,555.08 -> £3,342,770.52 (10.9%); £3,752,555.26 -> £3,342,770.56 (10.9%); £3,752,555.44 -> £3,342,770.61 (10.9%); £3,752,555.64 -> £3,342,770.67 (10.9%); £3,752,555.86 -> £3,342,770.71 (10.9%); £3,752,556.10 -> £3,342,770.76 (10.9%); £3,752,556.36 -> £3,342,770.80 (10.9%); £3,752,556.63 -> £3,342,770.84 (10.9%); £3,752,556.88 -> £3,342,770.87 (10.9%); £3,752,557.13 -> £3,342,770.87 (10.9%); £3,752,557.40 -> £3,342,770.87 (10.9%); £3,752,557.65 -> £3,342,770.87 (10.9%); £3,752,557.90 -> £3,342,770.87 (10.9%); £3,752,558.16 -> £3,342,770.87 (10.9%); £3,752,558.41 -> £3,342,770.87 (10.9%); £3,752,558.67 -> £3,342,770.87 (10.9%); £3,752,558.93 -> £3,342,770.87 (10.9%); £3,752,559.18 -> £3,342,770.86 (10.9%); £3,752,559.43 -> £3,342,770.86 (10.9%); £3,752,559.69 -> £3,342,770.90 (10.9%); £3,752,559.95 -> £3,342,770.96 (10.9%); £3,752,560.20 -> £3,342,771.02 (10.9%); £3,752,560.45 -> £3,342,771.09 (10.9%); £3,752,560.70 -> £3,342,771.16 (10.9%); £3,752,560.96 -> £3,342,771.22 (10.9%); £3,752,561.21 -> £3,342,771.31 (10.9%); £3,752,561.46 -> £3,342,771.39 (10.9%); £3,752,561.72 -> £3,342,771.36 (10.9%); £3,752,561.98 -> £3,342,771.34 (10.9%); £3,752,562.23 -> £3,342,771.31 (10.9%); £3,752,562.48 -> £3,342,771.29 (10.9%); £3,752,562.74 -> £3,342,771.28 (10.9%); £3,752,563.00 -> £3,342,771.28 (10.9%); £3,752,563.23 -> £3,342,771.27 (10.9%); £3,752,563.44 -> £3,342,771.27 (10.9%); £3,752,563.64 -> £3,342,771.27 (10.9%); £3,752,563.77 -> £3,342,771.27 (10.9%); £3,752,563.90 -> £3,342,771.27 (10.9%); £3,752,564.04 -> £3,342,771.27 (10.9%); £3,752,564.17 -> £3,342,771.27 (10.9%); £3,752,564.30 -> £3,342,771.27 (10.9%); £3,752,564.44 -> £3,342,771.27 (10.9%); £3,752,564.58 -> £3,342,771.28 (10.9%); £3,752,564.71 -> £3,342,771.28 (10.9%); £3,752,564.84 -> £3,342,771.28 (10.9%); £3,752,564.98 -> £3,342,771.28 (10.9%); £3,752,565.11 -> £3,342,771.28 (10.9%); £3,752,565.24 -> £3,342,771.28 (10.9%); £3,752,565.38 -> £3,342,771.28 (10.9%); £3,752,565.53 -> £3,342,771.28 (10.9%); £3,752,565.69 -> £3,342,771.27 (10.9%); £3,752,565.88 -> £3,342,771.26 (10.9%); £3,752,566.07 -> £3,342,771.26 (10.9%); £3,752,566.28 -> £3,342,771.25 (10.9%); £3,752,566.51 -> £3,342,771.24 (10.9%); £3,752,566.73 -> £3,342,771.23 (10.9%); £3,752,566.95 -> £3,342,771.23 (10.9%); £3,752,567.18 -> £3,342,771.23 (10.9%); £3,752,567.40 -> £3,342,771.22 (10.9%); £3,752,567.62 -> £3,342,771.22 (10.9%); £3,752,567.85 -> £3,342,771.21 (10.9%); £3,752,568.07 -> £3,342,771.21 (10.9%); £3,752,568.29 -> £3,342,771.20 (10.9%); £3,752,568.52 -> £3,342,771.20 (10.9%); £3,752,568.75 -> £3,342,771.20 (10.9%); £3,752,568.98 -> £3,342,771.19 (10.9%); £3,752,569.21 -> £3,342,771.19 (10.9%); £3,752,569.43 -> £3,342,771.19 (10.9%); £3,752,569.66 -> £3,342,771.18 (10.9%); £3,752,569.88 -> £3,342,771.17 (10.9%); £3,752,570.11 -> £3,342,771.15 (10.9%); £3,752,570.34 -> £3,342,771.13 (10.9%); £3,752,570.56 -> £3,342,771.11 (10.9%); £3,752,570.78 -> £3,342,771.08 (10.9%); £3,752,571.01 -> £3,342,771.06 (10.9%); £3,752,571.23 -> £3,342,771.03 (10.9%); £3,752,571.44 -> £3,342,771.01 (10.9%); £3,752,571.67 -> £3,342,770.99 (10.9%); £3,752,571.89 -> £3,342,770.97 (10.9%); £3,752,572.11 -> £3,342,770.96 (10.9%); £3,752,572.33 -> £3,342,770.96 (10.9%); £3,752,572.55 -> £3,342,770.95 (10.9%); £3,752,572.73 -> £3,342,770.95 (10.9%); £3,752,572.91 -> £3,342,770.95 (10.9%); £3,752,573.04 -> £3,342,770.94 (10.9%); £3,752,573.17 -> £3,342,770.94 (10.9%); £3,752,573.31 -> £3,342,770.94 (10.9%); £3,752,573.45 -> £3,342,770.94 (10.9%); £3,752,573.58 -> £3,342,770.95 (10.9%); £3,752,573.72 -> £3,342,770.95 (10.9%); £3,752,573.85 -> £3,342,770.95 (10.9%); £3,752,573.99 -> £3,342,770.95 (10.9%); £3,752,574.12 -> £3,342,770.96 (10.9%); £3,752,574.26 -> £3,342,770.96 (10.9%); £3,752,574.39 -> £3,342,770.96 (10.9%); £3,752,574.53 -> £3,342,770.96 (10.9%); £3,752,574.67 -> £3,342,770.96 (10.9%); £3,752,574.82 -> £3,342,770.96 (10.9%); £3,752,574.98 -> £3,342,770.96 (10.9%); £3,752,575.16 -> £3,342,770.95 (10.9%); £3,752,575.36 -> £3,342,770.94 (10.9%); £3,752,575.56 -> £3,342,770.93 (10.9%); £3,752,575.79 -> £3,342,770.92 (10.9%); £3,752,576.02 -> £3,342,770.92 (10.9%); £3,752,576.24 -> £3,342,770.91 (10.9%); £3,752,576.47 -> £3,342,770.90 (10.9%); £3,752,576.69 -> £3,342,770.89 (10.9%); £3,752,576.92 -> £3,342,770.88 (10.9%); £3,752,577.14 -> £3,342,770.87 (10.9%); £3,752,577.36 -> £3,342,770.86 (10.9%); £3,752,577.58 -> £3,342,770.85 (10.9%); £3,752,577.81 -> £3,342,770.85 (10.9%); £3,752,578.04 -> £3,342,770.84 (10.9%); £3,752,578.26 -> £3,342,770.84 (10.9%); £3,752,578.48 -> £3,342,770.84 (10.9%); £3,752,578.70 -> £3,342,770.83 (10.9%); £3,752,578.93 -> £3,342,770.82 (10.9%); £3,752,579.16 -> £3,342,770.80 (10.9%); £3,752,579.38 -> £3,342,770.78 (10.9%); £3,752,579.61 -> £3,342,770.76 (10.9%); £3,752,579.83 -> £3,342,770.75 (10.9%); £3,752,580.04 -> £3,342,770.72 (10.9%); £3,752,580.26 -> £3,342,770.69 (10.9%); £3,752,580.48 -> £3,342,770.66 (10.9%); £3,752,580.70 -> £3,342,770.64 (10.9%); £3,752,580.93 -> £3,342,770.61 (10.9%); £3,752,581.16 -> £3,342,770.59 (10.9%); £3,752,581.38 -> £3,342,770.59 (10.9%); £3,752,581.60 -> £3,342,770.58 (10.9%); £3,752,581.81 -> £3,342,770.58 (10.9%); £3,752,582.00 -> £3,342,770.57 (10.9%); £3,752,582.18 -> £3,342,770.57 (10.9%); £3,752,582.33 -> £3,342,770.57 (10.9%); £3,752,582.48 -> £3,342,770.57 (10.9%); £3,752,582.63 -> £3,342,770.57 (10.9%); £3,752,582.79 -> £3,342,770.58 (10.9%); £3,752,582.94 -> £3,342,770.58 (10.9%); £3,752,583.10 -> £3,342,770.58 (10.9%); £3,752,583.24 -> £3,342,770.58 (10.9%); £3,752,583.40 -> £3,342,770.58 (10.9%); £3,752,583.55 -> £3,342,770.59 (10.9%); £3,752,583.70 -> £3,342,770.59 (10.9%); £3,752,583.85 -> £3,342,770.59 (10.9%); £3,752,584.00 -> £3,342,770.59 (10.9%); £3,752,584.14 -> £3,342,770.58 (10.9%); £3,752,584.31 -> £3,342,770.62 (10.9%); £3,752,584.51 -> £3,342,770.68 (10.9%); £3,752,584.71 -> £3,342,770.73 (10.9%); £3,752,584.93 -> £3,342,770.78 (10.9%); £3,752,585.17 -> £3,342,770.82 (10.9%); £3,752,585.42 -> £3,342,770.87 (10.9%); £3,752,585.67 -> £3,342,770.90 (10.9%); £3,752,585.92 -> £3,342,770.94 (10.9%); £3,752,586.18 -> £3,342,770.94 (10.9%); £3,752,586.44 -> £3,342,770.93 (10.9%); £3,752,586.69 -> £3,342,770.93 (10.9%); £3,752,586.95 -> £3,342,770.93 (10.9%); £3,752,587.20 -> £3,342,770.93 (10.9%); £3,752,587.44 -> £3,342,770.93 (10.9%); £3,752,587.69 -> £3,342,770.93 (10.9%); £3,752,587.95 -> £3,342,770.92 (10.9%); £3,752,588.21 -> £3,342,770.92 (10.9%); £3,752,588.46 -> £3,342,770.92 (10.9%); £3,752,588.71 -> £3,342,770.96 (10.9%); £3,752,588.97 -> £3,342,771.02 (10.9%); £3,752,589.21 -> £3,342,771.08 (10.9%); £3,752,589.47 -> £3,342,771.15 (10.9%); £3,752,589.73 -> £3,342,771.21 (10.9%); £3,752,589.98 -> £3,342,771.28 (10.9%); £3,752,590.24 -> £3,342,771.36 (10.9%); £3,752,590.48 -> £3,342,771.44 (10.9%); £3,752,590.73 -> £3,342,771.42 (10.9%); £3,752,590.99 -> £3,342,771.40 (10.9%); £3,752,591.24 -> £3,342,771.37 (10.9%); £3,752,591.50 -> £3,342,771.35 (10.9%); £3,752,591.75 -> £3,342,771.34 (10.9%); £3,752,592.01 -> £3,342,771.34 (10.9%); £3,752,592.24 -> £3,342,771.33 (10.9%); £3,752,592.45 -> £3,342,771.33 (10.9%); £3,752,592.65 -> £3,342,771.33 (10.9%); £3,752,592.80 -> £3,342,771.33 (10.9%); £3,752,592.94 -> £3,342,771.33 (10.9%); £3,752,593.09 -> £3,342,771.33 (10.9%); £3,752,593.24 -> £3,342,771.33 (10.9%); £3,752,593.39 -> £3,342,771.34 (10.9%); £3,752,593.54 -> £3,342,771.34 (10.9%); £3,752,593.69 -> £3,342,771.34 (10.9%); £3,752,593.85 -> £3,342,771.34 (10.9%); £3,752,593.99 -> £3,342,771.34 (10.9%); £3,752,594.14 -> £3,342,771.35 (10.9%); £3,752,594.29 -> £3,342,771.35 (10.9%); £3,752,594.44 -> £3,342,771.34 (10.9%); £3,752,594.59 -> £3,342,771.34 (10.9%); £3,752,594.76 -> £3,342,771.38 (10.9%); £3,752,594.95 -> £3,342,771.44 (10.9%); £3,752,595.15 -> £3,342,771.49 (10.9%); £3,752,595.37 -> £3,342,771.54 (10.9%); £3,752,595.60 -> £3,342,771.58 (10.9%); £3,752,595.86 -> £3,342,771.63 (10.9%); £3,752,596.10 -> £3,342,771.66 (10.9%); £3,752,596.35 -> £3,342,771.70 (10.9%); £3,752,596.61 -> £3,342,771.70 (10.9%); £3,752,596.87 -> £3,342,771.70 (10.9%); £3,752,597.12 -> £3,342,771.70 (10.9%); £3,752,597.36 -> £3,342,771.69 (10.9%); £3,752,597.61 -> £3,342,771.69 (10.9%); £3,752,597.86 -> £3,342,771.69 (10.9%); £3,752,598.12 -> £3,342,771.69 (10.9%); £3,752,598.37 -> £3,342,771.69 (10.9%); £3,752,598.62 -> £3,342,771.69 (10.9%); £3,752,598.88 -> £3,342,771.69 (10.9%); £3,752,599.13 -> £3,342,771.72 (10.9%); £3,752,599.39 -> £3,342,771.78 (10.9%); £3,752,599.64 -> £3,342,771.85 (10.9%); £3,752,599.89 -> £3,342,771.92 (10.9%); £3,752,600.16 -> £3,342,771.98 (10.9%); £3,752,600.41 -> £3,342,772.05 (10.9%); £3,752,600.67 -> £3,342,772.13 (10.9%); £3,752,600.92 -> £3,342,772.22 (10.9%); £3,752,601.17 -> £3,342,772.19 (10.9%); £3,752,601.41 -> £3,342,772.17 (10.9%); £3,752,601.66 -> £3,342,772.14 (10.9%); £3,752,601.91 -> £3,342,772.12 (10.9%); £3,752,602.15 -> £3,342,772.11 (10.9%); £3,752,602.40 -> £3,342,772.11 (10.9%); £3,752,602.64 -> £3,342,772.10 (10.9%); £3,752,602.86 -> £3,342,772.10 (10.9%); £3,752,603.05 -> £3,342,772.10 (10.9%); £3,752,603.20 -> £3,342,772.10 (10.9%); £3,752,603.36 -> £3,342,772.10 (10.9%); £3,752,603.51 -> £3,342,772.10 (10.9%); £3,752,603.66 -> £3,342,772.10 (10.9%); £3,752,603.81 -> £3,342,772.10 (10.9%); £3,752,603.96 -> £3,342,772.11 (10.9%); £3,752,604.12 -> £3,342,772.11 (10.9%); £3,752,604.26 -> £3,342,772.11 (10.9%); £3,752,604.42 -> £3,342,772.11 (10.9%); £3,752,604.57 -> £3,342,772.12 (10.9%); £3,752,604.72 -> £3,342,772.12 (10.9%); £3,752,604.87 -> £3,342,772.11 (10.9%); £3,752,605.02 -> £3,342,772.11 (10.9%); £3,752,605.19 -> £3,342,772.15 (10.9%); £3,752,605.37 -> £3,342,772.20 (10.9%); £3,752,605.56 -> £3,342,772.26 (10.9%); £3,752,605.79 -> £3,342,772.31 (10.9%); £3,752,606.03 -> £3,342,772.35 (10.9%); £3,752,606.27 -> £3,342,772.40 (10.9%); £3,752,606.52 -> £3,342,772.43 (10.9%); £3,752,606.77 -> £3,342,772.47 (10.9%); £3,752,607.03 -> £3,342,772.47 (10.9%); £3,752,607.28 -> £3,342,772.47 (10.9%); £3,752,607.53 -> £3,342,772.47 (10.9%); £3,752,607.78 -> £3,342,772.46 (10.9%); £3,752,608.04 -> £3,342,772.46 (10.9%); £3,752,608.29 -> £3,342,772.46 (10.9%); £3,752,608.54 -> £3,342,772.46 (10.9%); £3,752,608.78 -> £3,342,772.46 (10.9%); £3,752,609.03 -> £3,342,772.46 (10.9%); £3,752,609.28 -> £3,342,772.46 (10.9%); £3,752,609.53 -> £3,342,772.50 (10.9%); £3,752,609.77 -> £3,342,772.55 (10.9%); £3,752,610.03 -> £3,342,772.62 (10.9%); £3,752,610.27 -> £3,342,772.69 (10.9%); £3,752,610.53 -> £3,342,772.75 (10.9%); £3,752,610.77 -> £3,342,772.82 (10.9%); £3,752,611.02 -> £3,342,772.90 (10.9%); £3,752,611.27 -> £3,342,772.98 (10.9%); £3,752,611.52 -> £3,342,772.96 (10.9%); £3,752,611.77 -> £3,342,772.94 (10.9%); £3,752,612.01 -> £3,342,772.91 (10.9%); £3,752,612.26 -> £3,342,772.89 (10.9%); £3,752,612.51 -> £3,342,772.89 (10.9%); £3,752,612.76 -> £3,342,772.88 (10.9%); £3,752,613.00 -> £3,342,772.88 (10.9%); £3,752,613.21 -> £3,342,772.87 (10.9%); £3,752,613.40 -> £3,342,772.87 (10.9%); £3,752,613.55 -> £3,342,772.87 (10.9%); £3,752,613.70 -> £3,342,772.87 (10.9%); £3,752,613.86 -> £3,342,772.87 (10.9%); £3,752,614.02 -> £3,342,772.87 (10.9%); £3,752,614.16 -> £3,342,772.88 (10.9%); £3,752,614.31 -> £3,342,772.88 (10.9%); £3,752,614.47 -> £3,342,772.88 (10.9%); £3,752,614.62 -> £3,342,772.88 (10.9%); £3,752,614.76 -> £3,342,772.89 (10.9%); £3,752,614.92 -> £3,342,772.89 (10.9%); £3,752,615.07 -> £3,342,772.89 (10.9%); £3,752,615.22 -> £3,342,772.89 (10.9%); £3,752,615.37 -> £3,342,772.88 (10.9%); £3,752,615.53 -> £3,342,772.92 (10.9%); £3,752,615.71 -> £3,342,772.98 (10.9%); £3,752,615.91 -> £3,342,773.03 (10.9%); £3,752,616.13 -> £3,342,773.08 (10.9%); £3,752,616.36 -> £3,342,773.12 (10.9%); £3,752,616.62 -> £3,342,773.17 (10.9%); £3,752,616.87 -> £3,342,773.20 (10.9%); £3,752,617.12 -> £3,342,773.24 (10.9%); £3,752,617.38 -> £3,342,773.24 (10.9%); £3,752,617.62 -> £3,342,773.24 (10.9%); £3,752,617.88 -> £3,342,773.23 (10.9%); £3,752,618.13 -> £3,342,773.23 (10.9%); £3,752,618.38 -> £3,342,773.23 (10.9%); £3,752,618.63 -> £3,342,773.23 (10.9%); £3,752,618.88 -> £3,342,773.23 (10.9%); £3,752,619.13 -> £3,342,773.23 (10.9%); £3,752,619.39 -> £3,342,773.23 (10.9%); £3,752,619.65 -> £3,342,773.23 (10.9%); £3,752,619.90 -> £3,342,773.26 (10.9%); £3,752,620.15 -> £3,342,773.32 (10.9%); £3,752,620.41 -> £3,342,773.38 (10.9%); £3,752,620.67 -> £3,342,773.45 (10.9%); £3,752,620.92 -> £3,342,773.52 (10.9%); £3,752,621.18 -> £3,342,773.58 (10.9%); £3,752,621.43 -> £3,342,773.67 (10.9%); £3,752,621.68 -> £3,342,773.75 (10.9%); £3,752,621.93 -> £3,342,773.72 (10.9%); £3,752,622.18 -> £3,342,773.70 (10.9%); £3,752,622.43 -> £3,342,773.68 (10.9%); £3,752,622.68 -> £3,342,773.65 (10.9%); £3,752,622.93 -> £3,342,773.65 (10.9%); £3,752,623.19 -> £3,342,773.64 (10.9%); £3,752,623.42 -> £3,342,773.64 (10.9%); £3,752,623.63 -> £3,342,773.63 (10.9%); £3,752,623.83 -> £3,342,773.63 (10.9%); £3,752,623.98 -> £3,342,773.63 (10.9%); £3,752,624.13 -> £3,342,773.63 (10.9%); £3,752,624.28 -> £3,342,773.64 (10.9%); £3,752,624.43 -> £3,342,773.64 (10.9%); £3,752,624.59 -> £3,342,773.64 (10.9%); £3,752,624.74 -> £3,342,773.64 (10.9%); £3,752,624.89 -> £3,342,773.65 (10.9%); £3,752,625.04 -> £3,342,773.65 (10.9%); £3,752,625.20 -> £3,342,773.65 (10.9%); £3,752,625.35 -> £3,342,773.65 (10.9%); £3,752,625.49 -> £3,342,773.65 (10.9%); £3,752,625.64 -> £3,342,773.65 (10.9%); £3,752,625.79 -> £3,342,773.65 (10.9%); £3,752,625.96 -> £3,342,773.69 (10.9%); £3,752,626.15 -> £3,342,773.75 (10.9%); £3,752,626.35 -> £3,342,773.80 (10.9%); £3,752,626.57 -> £3,342,773.85 (10.9%); £3,752,626.81 -> £3,342,773.90 (10.9%); £3,752,627.06 -> £3,342,773.94 (10.9%); £3,752,627.32 -> £3,342,773.98 (10.9%); £3,752,627.56 -> £3,342,774.01 (10.9%); £3,752,627.81 -> £3,342,774.01 (10.9%); £3,752,628.07 -> £3,342,774.01 (10.9%); £3,752,628.31 -> £3,342,774.01 (10.9%); £3,752,628.56 -> £3,342,774.01 (10.9%); £3,752,628.82 -> £3,342,774.01 (10.9%); £3,752,629.06 -> £3,342,774.01 (10.9%); £3,752,629.32 -> £3,342,774.01 (10.9%); £3,752,629.57 -> £3,342,774.01 (10.9%); £3,752,629.83 -> £3,342,774.01 (10.9%); £3,752,630.08 -> £3,342,774.01 (10.9%); £3,752,630.32 -> £3,342,774.04 (10.9%); £3,752,630.58 -> £3,342,774.10 (10.9%); £3,752,630.83 -> £3,342,774.17 (10.9%); £3,752,631.08 -> £3,342,774.23 (10.9%); £3,752,631.34 -> £3,342,774.30 (10.9%); £3,752,631.58 -> £3,342,774.37 (10.9%); £3,752,631.83 -> £3,342,774.45 (10.9%); £3,752,632.08 -> £3,342,774.53 (10.9%); £3,752,632.34 -> £3,342,774.51 (10.9%); £3,752,632.59 -> £3,342,774.48 (10.9%); £3,752,632.84 -> £3,342,774.46 (10.9%); £3,752,633.10 -> £3,342,774.44 (10.9%); £3,752,633.36 -> £3,342,774.43 (10.9%); £3,752,633.60 -> £3,342,774.43 (10.9%); £3,752,633.84 -> £3,342,774.42 (10.9%); £3,752,634.04 -> £3,342,774.42 (10.9%); £3,752,634.24 -> £3,342,774.41 (10.9%); £3,752,634.37 -> £3,342,774.41 (10.9%); £3,752,634.51 -> £3,342,774.41 (10.9%); £3,752,634.64 -> £3,342,774.41 (10.9%); £3,752,634.77 -> £3,342,774.42 (10.9%); £3,752,634.91 -> £3,342,774.42 (10.9%); £3,752,635.05 -> £3,342,774.42 (10.9%); £3,752,635.18 -> £3,342,774.42 (10.9%); £3,752,635.32 -> £3,342,774.43 (10.9%); £3,752,635.45 -> £3,342,774.43 (10.9%); £3,752,635.59 -> £3,342,774.43 (10.9%); £3,752,635.72 -> £3,342,774.43 (10.9%); £3,752,635.86 -> £3,342,774.43 (10.9%); £3,752,636.00 -> £3,342,774.43 (10.9%); £3,752,636.15 -> £3,342,774.42 (10.9%); £3,752,636.32 -> £3,342,774.42 (10.9%); £3,752,636.49 -> £3,342,774.41 (10.9%); £3,752,636.69 -> £3,342,774.40 (10.9%); £3,752,636.91 -> £3,342,774.40 (10.9%); £3,752,637.13 -> £3,342,774.39 (10.9%); £3,752,637.35 -> £3,342,774.38 (10.9%); £3,752,637.57 -> £3,342,774.38 (10.9%); £3,752,637.79 -> £3,342,774.38 (10.9%); £3,752,638.02 -> £3,342,774.37 (10.9%); £3,752,638.25 -> £3,342,774.37 (10.9%); £3,752,638.47 -> £3,342,774.36 (10.9%); £3,752,638.69 -> £3,342,774.36 (10.9%); £3,752,638.92 -> £3,342,774.36 (10.9%); £3,752,639.13 -> £3,342,774.35 (10.9%); £3,752,639.35 -> £3,342,774.35 (10.9%); £3,752,639.57 -> £3,342,774.35 (10.9%); £3,752,639.79 -> £3,342,774.35 (10.9%); £3,752,640.01 -> £3,342,774.35 (10.9%); £3,752,640.23 -> £3,342,774.33 (10.9%); £3,752,640.46 -> £3,342,774.32 (10.9%); £3,752,640.68 -> £3,342,774.30 (10.9%); £3,752,640.91 -> £3,342,774.28 (10.9%); £3,752,641.14 -> £3,342,774.26 (10.9%); £3,752,641.37 -> £3,342,774.23 (10.9%); £3,752,641.58 -> £3,342,774.20 (10.9%); £3,752,641.81 -> £3,342,774.18 (10.9%); £3,752,642.04 -> £3,342,774.16 (10.9%); £3,752,642.26 -> £3,342,774.14 (10.9%); £3,752,642.48 -> £3,342,774.12 (10.9%); £3,752,642.70 -> £3,342,774.11 (10.9%); £3,752,642.92 -> £3,342,774.11 (10.9%); £3,752,643.12 -> £3,342,774.10 (10.9%); £3,752,643.31 -> £3,342,774.09 (10.9%); £3,752,643.49 -> £3,342,774.09 (10.9%); £3,752,643.63 -> £3,342,774.09 (10.9%); £3,752,643.76 -> £3,342,774.09 (10.9%); £3,752,643.89 -> £3,342,774.09 (10.9%); £3,752,644.03 -> £3,342,774.09 (10.9%); £3,752,644.17 -> £3,342,774.09 (10.9%); £3,752,644.30 -> £3,342,774.09 (10.9%); £3,752,644.43 -> £3,342,774.10 (10.9%); £3,752,644.57 -> £3,342,774.10 (10.9%); £3,752,644.70 -> £3,342,774.10 (10.9%); £3,752,644.85 -> £3,342,774.10 (10.9%); £3,752,644.98 -> £3,342,774.10 (10.9%); £3,752,645.12 -> £3,342,774.10 (10.9%); £3,752,645.25 -> £3,342,774.10 (10.9%); £3,752,645.40 -> £3,342,774.10 (10.9%); £3,752,645.57 -> £3,342,774.10 (10.9%); £3,752,645.75 -> £3,342,774.10 (10.9%); £3,752,645.95 -> £3,342,774.09 (10.9%); £3,752,646.16 -> £3,342,774.08 (10.9%); £3,752,646.39 -> £3,342,774.07 (10.9%); £3,752,646.62 -> £3,342,774.06 (10.9%); £3,752,646.84 -> £3,342,774.05 (10.9%); £3,752,647.06 -> £3,342,774.04 (10.9%); £3,752,647.29 -> £3,342,774.03 (10.9%); £3,752,647.51 -> £3,342,774.02 (10.9%); £3,752,647.74 -> £3,342,774.01 (10.9%); £3,752,647.97 -> £3,342,774.01 (10.9%); £3,752,648.20 -> £3,342,774.00 (10.9%); £3,752,648.43 -> £3,342,773.99 (10.9%); £3,752,648.66 -> £3,342,773.99 (10.9%); £3,752,648.88 -> £3,342,773.98 (10.9%); £3,752,649.11 -> £3,342,773.98 (10.9%); £3,752,649.34 -> £3,342,773.98 (10.9%); £3,752,649.56 -> £3,342,773.96 (10.9%); £3,752,649.79 -> £3,342,773.94 (10.9%); £3,752,650.01 -> £3,342,773.93 (10.9%); £3,752,650.24 -> £3,342,773.91 (10.9%); £3,752,650.47 -> £3,342,773.89 (10.9%); £3,752,650.69 -> £3,342,773.86 (10.9%); £3,752,650.92 -> £3,342,773.83 (10.9%); £3,752,651.14 -> £3,342,773.80 (10.9%); £3,752,651.36 -> £3,342,773.78 (10.9%); £3,752,651.58 -> £3,342,773.75 (10.9%); £3,752,651.82 -> £3,342,773.73 (10.9%); £3,752,652.04 -> £3,342,773.73 (10.9%); £3,752,652.27 -> £3,342,773.72 (10.9%); £3,752,652.48 -> £3,342,773.72 (10.9%); £3,752,652.68 -> £3,342,773.71 (10.9%); £3,752,652.86 -> £3,342,773.71 (10.9%); £3,752,653.01 -> £3,342,773.71 (10.9%); £3,752,653.16 -> £3,342,773.71 (10.9%); £3,752,653.32 -> £3,342,773.71 (10.9%); £3,752,653.47 -> £3,342,773.71 (10.9%); £3,752,653.63 -> £3,342,773.72 (10.9%); £3,752,653.78 -> £3,342,773.72 (10.9%); £3,752,653.93 -> £3,342,773.72 (10.9%); £3,752,654.09 -> £3,342,773.72 (10.9%); £3,752,654.24 -> £3,342,773.73 (10.9%); £3,752,654.39 -> £3,342,773.73 (10.9%); £3,752,654.54 -> £3,342,773.73 (10.9%); £3,752,654.70 -> £3,342,773.73 (10.9%); £3,752,654.85 -> £3,342,773.72 (10.9%); £3,752,655.02 -> £3,342,773.76 (10.9%); £3,752,655.21 -> £3,342,773.82 (10.9%); £3,752,655.42 -> £3,342,773.87 (10.9%); £3,752,655.64 -> £3,342,773.92 (10.9%); £3,752,655.88 -> £3,342,773.96 (10.9%); £3,752,656.14 -> £3,342,774.01 (10.9%); £3,752,656.39 -> £3,342,774.04 (10.9%); £3,752,656.65 -> £3,342,774.08 (10.9%); £3,752,656.91 -> £3,342,774.08 (10.9%); £3,752,657.16 -> £3,342,774.08 (10.9%); £3,752,657.40 -> £3,342,774.08 (10.9%); £3,752,657.66 -> £3,342,774.07 (10.9%); £3,752,657.91 -> £3,342,774.07 (10.9%); £3,752,658.16 -> £3,342,774.07 (10.9%); £3,752,658.43 -> £3,342,774.07 (10.9%); £3,752,658.69 -> £3,342,774.07 (10.9%); £3,752,658.95 -> £3,342,774.07 (10.9%); £3,752,659.20 -> £3,342,774.07 (10.9%); £3,752,659.47 -> £3,342,774.11 (10.9%); £3,752,659.72 -> £3,342,774.17 (10.9%); £3,752,659.98 -> £3,342,774.23 (10.9%); £3,752,660.24 -> £3,342,774.30 (10.9%); £3,752,660.49 -> £3,342,774.37 (10.9%); £3,752,660.75 -> £3,342,774.43 (10.9%); £3,752,661.01 -> £3,342,774.52 (10.9%); £3,752,661.26 -> £3,342,774.60 (10.9%); £3,752,661.52 -> £3,342,774.57 (10.9%); £3,752,661.77 -> £3,342,774.55 (10.9%); £3,752,662.03 -> £3,342,774.53 (10.9%); £3,752,662.29 -> £3,342,774.51 (10.9%); £3,752,662.54 -> £3,342,774.50 (10.9%); £3,752,662.80 -> £3,342,774.50 (10.9%); £3,752,663.04 -> £3,342,774.49 (10.9%); £3,752,663.25 -> £3,342,774.49 (10.9%); £3,752,663.45 -> £3,342,774.49 (10.9%); £3,752,663.61 -> £3,342,774.49 (10.9%); £3,752,663.76 -> £3,342,774.49 (10.9%); £3,752,663.92 -> £3,342,774.49 (10.9%); £3,752,664.07 -> £3,342,774.49 (10.9%); £3,752,664.23 -> £3,342,774.49 (10.9%); £3,752,664.38 -> £3,342,774.49 (10.9%); £3,752,664.54 -> £3,342,774.50 (10.9%); £3,752,664.69 -> £3,342,774.50 (10.9%); £3,752,664.84 -> £3,342,774.50 (10.9%); £3,752,665.00 -> £3,342,774.50 (10.9%); £3,752,665.15 -> £3,342,774.50 (10.9%); £3,752,665.31 -> £3,342,774.50 (10.9%); £3,752,665.47 -> £3,342,774.50 (10.9%); £3,752,665.63 -> £3,342,774.54 (10.9%); £3,752,665.83 -> £3,342,774.59 (10.9%); £3,752,666.04 -> £3,342,774.65 (10.9%); £3,752,666.26 -> £3,342,774.70 (10.9%); £3,752,666.50 -> £3,342,774.74 (10.9%); £3,752,666.76 -> £3,342,774.79 (10.9%); £3,752,667.01 -> £3,342,774.82 (10.9%); £3,752,667.27 -> £3,342,774.86 (10.9%); £3,752,667.52 -> £3,342,774.86 (10.9%); £3,752,667.78 -> £3,342,774.86 (10.9%); £3,752,668.04 -> £3,342,774.86 (10.9%); £3,752,668.29 -> £3,342,774.85 (10.9%); £3,752,668.56 -> £3,342,774.85 (10.9%); £3,752,668.82 -> £3,342,774.85 (10.9%); £3,752,669.09 -> £3,342,774.85 (10.9%); £3,752,669.35 -> £3,342,774.85 (10.9%); £3,752,669.61 -> £3,342,774.85 (10.9%); £3,752,669.87 -> £3,342,774.85 (10.9%); £3,752,670.12 -> £3,342,774.88 (10.9%); £3,752,670.37 -> £3,342,774.94 (10.9%); £3,752,670.63 -> £3,342,775.01 (10.9%); £3,752,670.89 -> £3,342,775.07 (10.9%); £3,752,671.15 -> £3,342,775.14 (10.9%); £3,752,671.41 -> £3,342,775.20 (10.9%); £3,752,671.67 -> £3,342,775.29 (10.9%); £3,752,671.93 -> £3,342,775.37 (10.9%); £3,752,672.19 -> £3,342,775.34 (10.9%); £3,752,672.44 -> £3,342,775.32 (10.9%); £3,752,672.70 -> £3,342,775.30 (10.9%); £3,752,672.95 -> £3,342,775.28 (10.9%); £3,752,673.21 -> £3,342,775.27 (10.9%); £3,752,673.46 -> £3,342,775.26 (10.9%); £3,752,673.70 -> £3,342,775.26 (10.9%); £3,752,673.93 -> £3,342,775.25 (10.9%); £3,752,674.12 -> £3,342,775.25 (10.9%); £3,752,674.27 -> £3,342,775.25 (10.9%); £3,752,674.43 -> £3,342,775.25 (10.9%); £3,752,674.58 -> £3,342,775.26 (10.9%); £3,752,674.73 -> £3,342,775.26 (10.9%); £3,752,674.88 -> £3,342,775.26 (10.9%); £3,752,675.04 -> £3,342,775.26 (10.9%); £3,752,675.20 -> £3,342,775.26 (10.9%); £3,752,675.35 -> £3,342,775.27 (10.9%); £3,752,675.50 -> £3,342,775.27 (10.9%); £3,752,675.66 -> £3,342,775.27 (10.9%); £3,752,675.83 -> £3,342,775.27 (10.9%); £3,752,675.98 -> £3,342,775.27 (10.9%); £3,752,676.13 -> £3,342,775.26 (10.9%); £3,752,676.31 -> £3,342,775.31 (10.9%); £3,752,676.49 -> £3,342,775.36 (10.9%); £3,752,676.70 -> £3,342,775.41 (10.9%); £3,752,676.93 -> £3,342,775.46 (10.9%); £3,752,677.17 -> £3,342,775.50 (10.9%); £3,752,677.43 -> £3,342,775.55 (10.9%); £3,752,677.69 -> £3,342,775.58 (10.9%); £3,752,677.95 -> £3,342,775.62 (10.9%); £3,752,678.20 -> £3,342,775.62 (10.9%); £3,752,678.45 -> £3,342,775.62 (10.9%); £3,752,678.71 -> £3,342,775.62 (10.9%); £3,752,678.97 -> £3,342,775.61 (10.9%); £3,752,679.22 -> £3,342,775.61 (10.9%); £3,752,679.47 -> £3,342,775.61 (10.9%); £3,752,679.73 -> £3,342,775.61 (10.9%); £3,752,679.98 -> £3,342,775.61 (10.9%); £3,752,680.25 -> £3,342,775.61 (10.9%); £3,752,680.50 -> £3,342,775.61 (10.9%); £3,752,680.76 -> £3,342,775.64 (10.9%); £3,752,681.01 -> £3,342,775.70 (10.9%); £3,752,681.27 -> £3,342,775.77 (10.9%); £3,752,681.54 -> £3,342,775.83 (10.9%); £3,752,681.79 -> £3,342,775.90 (10.9%); £3,752,682.04 -> £3,342,775.96 (10.9%); £3,752,682.31 -> £3,342,776.05 (10.9%); £3,752,682.57 -> £3,342,776.13 (10.9%); £3,752,682.82 -> £3,342,776.10 (10.9%); £3,752,683.08 -> £3,342,776.08 (10.9%); £3,752,683.34 -> £3,342,776.05 (10.9%); £3,752,683.58 -> £3,342,776.03 (10.9%); £3,752,683.84 -> £3,342,776.03 (10.9%); £3,752,684.09 -> £3,342,776.02 (10.9%); £3,752,684.34 -> £3,342,776.01 (10.9%); £3,752,684.56 -> £3,342,776.01 (10.9%); £3,752,684.77 -> £3,342,776.01 (10.9%); £3,752,684.92 -> £3,342,776.01 (10.9%); £3,752,685.07 -> £3,342,776.01 (10.9%); £3,752,685.23 -> £3,342,776.01 (10.9%); £3,752,685.38 -> £3,342,776.01 (10.9%); £3,752,685.53 -> £3,342,776.02 (10.9%); £3,752,685.68 -> £3,342,776.02 (10.9%); £3,752,685.83 -> £3,342,776.02 (10.9%); £3,752,685.99 -> £3,342,776.02 (10.9%); £3,752,686.13 -> £3,342,776.02 (10.9%); £3,752,686.29 -> £3,342,776.03 (10.9%); £3,752,686.44 -> £3,342,776.03 (10.9%); £3,752,686.59 -> £3,342,776.02 (10.9%); £3,752,686.75 -> £3,342,776.02 (10.9%); £3,752,686.92 -> £3,342,776.06 (10.9%); £3,752,687.10 -> £3,342,776.12 (10.9%); £3,752,687.31 -> £3,342,776.17 (10.9%); £3,752,687.53 -> £3,342,776.22 (10.9%); £3,752,687.77 -> £3,342,776.26 (10.9%); £3,752,688.03 -> £3,342,776.31 (10.9%); £3,752,688.29 -> £3,342,776.34 (10.9%); £3,752,688.54 -> £3,342,776.38 (10.9%); £3,752,688.80 -> £3,342,776.38 (10.9%); £3,752,689.05 -> £3,342,776.38 (10.9%); £3,752,689.32 -> £3,342,776.37 (10.9%); £3,752,689.57 -> £3,342,776.37 (10.9%); £3,752,689.82 -> £3,342,776.37 (10.9%); £3,752,690.07 -> £3,342,776.37 (10.9%); £3,752,690.33 -> £3,342,776.37 (10.9%); £3,752,690.58 -> £3,342,776.37 (10.9%); £3,752,690.84 -> £3,342,776.37 (10.9%); £3,752,691.09 -> £3,342,776.37 (10.9%); £3,752,691.35 -> £3,342,776.40 (10.9%); £3,752,691.61 -> £3,342,776.46 (10.9%); £3,752,691.85 -> £3,342,776.53 (10.9%); £3,752,692.11 -> £3,342,776.60 (10.9%); £3,752,692.37 -> £3,342,776.66 (10.9%); £3,752,692.63 -> £3,342,776.73 (10.9%); £3,752,692.89 -> £3,342,776.81 (10.9%); £3,752,693.14 -> £3,342,776.90 (10.9%); £3,752,693.40 -> £3,342,776.87 (10.9%); £3,752,693.65 -> £3,342,776.85 (10.9%); £3,752,693.90 -> £3,342,776.82 (10.9%); £3,752,694.16 -> £3,342,776.80 (10.9%); £3,752,694.41 -> £3,342,776.80 (10.9%); £3,752,694.67 -> £3,342,776.79 (10.9%); £3,752,694.90 -> £3,342,776.79 (10.9%); £3,752,695.12 -> £3,342,776.78 (10.9%); £3,752,695.32 -> £3,342,776.78 (10.9%); £3,752,695.48 -> £3,342,776.78 (10.9%); £3,752,695.64 -> £3,342,776.79 (10.9%); £3,752,695.78 -> £3,342,776.79 (10.9%); £3,752,695.94 -> £3,342,776.79 (10.9%); £3,752,696.09 -> £3,342,776.79 (10.9%); £3,752,696.24 -> £3,342,776.80 (10.9%); £3,752,696.40 -> £3,342,776.80 (10.9%); £3,752,696.55 -> £3,342,776.80 (10.9%); £3,752,696.70 -> £3,342,776.80 (10.9%); £3,752,696.85 -> £3,342,776.80 (10.9%); £3,752,697.00 -> £3,342,776.81 (10.9%); £3,752,697.16 -> £3,342,776.80 (10.9%); £3,752,697.31 -> £3,342,776.80 (10.9%); £3,752,697.48 -> £3,342,776.84 (10.9%); £3,752,697.67 -> £3,342,776.90 (10.9%); £3,752,697.88 -> £3,342,776.95 (10.9%); £3,752,698.10 -> £3,342,777.00 (10.9%); £3,752,698.34 -> £3,342,777.04 (10.9%); £3,752,698.61 -> £3,342,777.09 (10.9%); £3,752,698.87 -> £3,342,777.12 (10.9%); £3,752,699.13 -> £3,342,777.16 (10.9%); £3,752,699.38 -> £3,342,777.16 (10.9%); £3,752,699.65 -> £3,342,777.16 (10.9%); £3,752,699.90 -> £3,342,777.16 (10.9%); £3,752,700.16 -> £3,342,777.15 (10.9%); £3,752,700.42 -> £3,342,777.15 (10.9%); £3,752,700.67 -> £3,342,777.15 (10.9%); £3,752,700.93 -> £3,342,777.15 (10.9%); £3,752,701.18 -> £3,342,777.15 (10.9%); £3,752,701.44 -> £3,342,777.15 (10.9%); £3,752,701.70 -> £3,342,777.15 (10.9%); £3,752,701.96 -> £3,342,777.19 (10.9%); £3,752,702.21 -> £3,342,777.25 (10.9%); £3,752,702.48 -> £3,342,777.31 (10.9%); £3,752,702.73 -> £3,342,777.38 (10.9%); £3,752,703.00 -> £3,342,777.45 (10.9%); £3,752,703.24 -> £3,342,777.51 (10.9%); £3,752,703.50 -> £3,342,777.60 (10.9%); £3,752,703.76 -> £3,342,777.68 (10.9%); £3,752,704.03 -> £3,342,777.65 (10.9%); £3,752,704.28 -> £3,342,777.63 (10.9%); £3,752,704.54 -> £3,342,777.61 (10.9%); £3,752,704.80 -> £3,342,777.59 (10.9%); £3,752,705.05 -> £3,342,777.58 (10.9%); £3,752,705.31 -> £3,342,777.58 (10.9%); £3,752,705.55 -> £3,342,777.57 (10.9%); £3,752,705.77 -> £3,342,777.57 (10.9%); £3,752,705.97 -> £3,342,777.57 (10.9%); £3,752,706.11 -> £3,342,777.57 (10.9%); £3,752,706.25 -> £3,342,777.57 (10.9%); £3,752,706.39 -> £3,342,777.57 (10.9%); £3,752,706.52 -> £3,342,777.57 (10.9%); £3,752,706.66 -> £3,342,777.57 (10.9%); £3,752,706.79 -> £3,342,777.58 (10.9%); £3,752,706.93 -> £3,342,777.58 (10.9%); £3,752,707.07 -> £3,342,777.58 (10.9%); £3,752,707.20 -> £3,342,777.58 (10.9%); £3,752,707.34 -> £3,342,777.59 (10.9%); £3,752,707.47 -> £3,342,777.59 (10.9%); £3,752,707.61 -> £3,342,777.59 (10.9%); £3,752,707.74 -> £3,342,777.58 (10.9%); £3,752,707.89 -> £3,342,777.58 (10.9%); £3,752,708.06 -> £3,342,777.58 (10.9%); £3,752,708.24 -> £3,342,777.57 (10.9%); £3,752,708.44 -> £3,342,777.57 (10.9%); £3,752,708.65 -> £3,342,777.56 (10.9%); £3,752,708.88 -> £3,342,777.55 (10.9%); £3,752,709.11 -> £3,342,777.55 (10.9%); £3,752,709.33 -> £3,342,777.55 (10.9%); £3,752,709.56 -> £3,342,777.54 (10.9%); £3,752,709.79 -> £3,342,777.54 (10.9%); £3,752,710.01 -> £3,342,777.54 (10.9%); £3,752,710.24 -> £3,342,777.53 (10.9%); £3,752,710.47 -> £3,342,777.53 (10.9%); £3,752,710.70 -> £3,342,777.53 (10.9%); £3,752,710.92 -> £3,342,777.53 (10.9%); £3,752,711.15 -> £3,342,777.52 (10.9%); £3,752,711.37 -> £3,342,777.52 (10.9%); £3,752,711.59 -> £3,342,777.52 (10.9%); £3,752,711.82 -> £3,342,777.52 (10.9%); £3,752,712.05 -> £3,342,777.51 (10.9%); £3,752,712.28 -> £3,342,777.49 (10.9%); £3,752,712.51 -> £3,342,777.48 (10.9%); £3,752,712.74 -> £3,342,777.46 (10.9%); £3,752,712.97 -> £3,342,777.44 (10.9%); £3,752,713.20 -> £3,342,777.41 (10.9%); £3,752,713.42 -> £3,342,777.38 (10.9%); £3,752,713.65 -> £3,342,777.36 (10.9%); £3,752,713.88 -> £3,342,777.34 (10.9%); £3,752,714.10 -> £3,342,777.32 (10.9%); £3,752,714.32 -> £3,342,777.30 (10.9%); £3,752,714.55 -> £3,342,777.30 (10.9%); £3,752,714.78 -> £3,342,777.29 (10.9%); £3,752,714.99 -> £3,342,777.29 (10.9%); £3,752,715.17 -> £3,342,777.28 (10.9%); £3,752,715.35 -> £3,342,777.28 (10.9%); £3,752,715.49 -> £3,342,777.28 (10.9%); £3,752,715.63 -> £3,342,777.28 (10.9%); £3,752,715.77 -> £3,342,777.28 (10.9%); £3,752,715.91 -> £3,342,777.28 (10.9%); £3,752,716.05 -> £3,342,777.28 (10.9%); £3,752,716.19 -> £3,342,777.29 (10.9%); £3,752,716.33 -> £3,342,777.29 (10.9%); £3,752,716.48 -> £3,342,777.29 (10.9%); £3,752,716.62 -> £3,342,777.29 (10.9%); £3,752,716.76 -> £3,342,777.30 (10.9%); £3,752,716.90 -> £3,342,777.30 (10.9%); £3,752,717.05 -> £3,342,777.30 (10.9%); £3,752,717.19 -> £3,342,777.30 (10.9%); £3,752,717.34 -> £3,342,777.30 (10.9%); £3,752,717.51 -> £3,342,777.30 (10.9%); £3,752,717.70 -> £3,342,777.29 (10.9%); £3,752,717.90 -> £3,342,777.29 (10.9%); £3,752,718.12 -> £3,342,777.28 (10.9%); £3,752,718.34 -> £3,342,777.27 (10.9%); £3,752,718.58 -> £3,342,777.26 (10.9%); £3,752,718.82 -> £3,342,777.26 (10.9%); £3,752,719.05 -> £3,342,777.25 (10.9%); £3,752,719.28 -> £3,342,777.24 (10.9%); £3,752,719.51 -> £3,342,777.23 (10.9%); £3,752,719.74 -> £3,342,777.22 (10.9%); £3,752,719.98 -> £3,342,777.21 (10.9%); £3,752,720.21 -> £3,342,777.20 (10.9%); £3,752,720.44 -> £3,342,777.20 (10.9%); £3,752,720.67 -> £3,342,777.19 (10.9%); £3,752,720.90 -> £3,342,777.19 (10.9%); £3,752,721.13 -> £3,342,777.19 (10.9%); £3,752,721.36 -> £3,342,777.18 (10.9%); £3,752,721.60 -> £3,342,777.17 (10.9%); £3,752,721.83 -> £3,342,777.15 (10.9%); £3,752,722.07 -> £3,342,777.13 (10.9%); £3,752,722.30 -> £3,342,777.11 (10.9%); £3,752,722.53 -> £3,342,777.09 (10.9%); £3,752,722.76 -> £3,342,777.06 (10.9%); £3,752,722.99 -> £3,342,777.04 (10.9%); £3,752,723.23 -> £3,342,777.01 (10.9%); £3,752,723.47 -> £3,342,776.98 (10.9%); £3,752,723.71 -> £3,342,776.96 (10.9%); £3,752,723.95 -> £3,342,776.94 (10.9%); £3,752,724.18 -> £3,342,776.93 (10.9%); £3,752,724.41 -> £3,342,776.93 (10.9%); £3,752,724.64 -> £3,342,776.92 (10.9%); £3,752,724.84 -> £3,342,776.92 (10.9%); £3,752,725.02 -> £3,342,776.92 (10.9%); £3,752,725.18 -> £3,342,776.92 (10.9%); £3,752,725.34 -> £3,342,776.92 (10.9%); £3,752,725.50 -> £3,342,776.92 (10.9%); £3,752,725.66 -> £3,342,776.92 (10.9%); £3,752,725.83 -> £3,342,776.92 (10.9%); £3,752,725.98 -> £3,342,776.93 (10.9%); £3,752,726.15 -> £3,342,776.93 (10.9%); £3,752,726.31 -> £3,342,776.93 (10.9%); £3,752,726.47 -> £3,342,776.93 (10.9%); £3,752,726.63 -> £3,342,776.93 (10.9%); £3,752,726.79 -> £3,342,776.94 (10.9%); £3,752,726.96 -> £3,342,776.93 (10.9%); £3,752,727.12 -> £3,342,776.93 (10.9%); £3,752,727.29 -> £3,342,776.97 (10.9%); £3,752,727.49 -> £3,342,777.02 (10.9%); £3,752,727.71 -> £3,342,777.08 (10.9%); £3,752,727.94 -> £3,342,777.13 (10.9%); £3,752,728.19 -> £3,342,777.17 (10.9%); £3,752,728.47 -> £3,342,777.22 (10.9%); £3,752,728.74 -> £3,342,777.25 (10.9%); £3,752,729.02 -> £3,342,777.29 (10.9%); £3,752,729.29 -> £3,342,777.29 (10.9%); £3,752,729.56 -> £3,342,777.29 (10.9%); £3,752,729.83 -> £3,342,777.29 (10.9%); £3,752,730.10 -> £3,342,777.28 (10.9%); £3,752,730.37 -> £3,342,777.28 (10.9%); £3,752,730.63 -> £3,342,777.28 (10.9%); £3,752,730.91 -> £3,342,777.28 (10.9%); £3,752,731.18 -> £3,342,777.28 (10.9%); £3,752,731.45 -> £3,342,777.28 (10.9%); £3,752,731.73 -> £3,342,777.28 (10.9%); £3,752,732.00 -> £3,342,777.32 (10.9%); £3,752,732.27 -> £3,342,777.37 (10.9%); £3,752,732.53 -> £3,342,777.44 (10.9%); £3,752,732.80 -> £3,342,777.50 (10.9%); £3,752,733.06 -> £3,342,777.57 (10.9%); £3,752,733.33 -> £3,342,777.63 (10.9%); £3,752,733.59 -> £3,342,777.72 (10.9%); £3,752,733.86 -> £3,342,777.80 (10.9%); £3,752,734.13 -> £3,342,777.77 (10.9%); £3,752,734.40 -> £3,342,777.75 (10.9%); £3,752,734.66 -> £3,342,777.72 (10.9%); £3,752,734.93 -> £3,342,777.70 (10.9%); £3,752,735.19 -> £3,342,777.70 (10.9%); £3,752,735.47 -> £3,342,777.69 (10.9%); £3,752,735.70 -> £3,342,777.68 (10.9%); £3,752,735.93 -> £3,342,777.68 (10.9%); £3,752,736.14 -> £3,342,777.68 (10.9%); £3,752,736.30 -> £3,342,777.68 (10.9%); £3,752,736.46 -> £3,342,777.68 (10.9%); £3,752,736.63 -> £3,342,777.68 (10.9%); £3,752,736.80 -> £3,342,777.68 (10.9%); £3,752,736.96 -> £3,342,777.69 (10.9%); £3,752,737.12 -> £3,342,777.69 (10.9%); £3,752,737.28 -> £3,342,777.69 (10.9%); £3,752,737.45 -> £3,342,777.69 (10.9%); £3,752,737.61 -> £3,342,777.69 (10.9%); £3,752,737.77 -> £3,342,777.70 (10.9%); £3,752,737.93 -> £3,342,777.70 (10.9%); £3,752,738.09 -> £3,342,777.69 (10.9%); £3,752,738.25 -> £3,342,777.69 (10.9%); £3,752,738.43 -> £3,342,777.73 (10.9%); £3,752,738.63 -> £3,342,777.79 (10.9%); £3,752,738.85 -> £3,342,777.84 (10.9%); £3,752,739.09 -> £3,342,777.89 (10.9%); £3,752,739.34 -> £3,342,777.93 (10.9%); £3,752,739.61 -> £3,342,777.98 (10.9%); £3,752,739.88 -> £3,342,778.01 (10.9%); £3,752,740.16 -> £3,342,778.05 (10.9%); £3,752,740.43 -> £3,342,778.05 (10.9%); £3,752,740.68 -> £3,342,778.05 (10.9%); £3,752,740.95 -> £3,342,778.05 (10.9%); £3,752,741.22 -> £3,342,778.04 (10.9%); £3,752,741.48 -> £3,342,778.04 (10.9%); £3,752,741.75 -> £3,342,778.04 (10.9%); £3,752,742.01 -> £3,342,778.04 (10.9%); £3,752,742.28 -> £3,342,778.04 (10.9%); £3,752,742.55 -> £3,342,778.04 (10.9%); £3,752,742.83 -> £3,342,778.04 (10.9%); £3,752,743.10 -> £3,342,778.08 (10.9%); £3,752,743.37 -> £3,342,778.13 (10.9%); £3,752,743.63 -> £3,342,778.20 (10.9%); £3,752,743.91 -> £3,342,778.26 (10.9%); £3,752,744.17 -> £3,342,778.33 (10.9%); £3,752,744.44 -> £3,342,778.40 (10.9%); £3,752,744.71 -> £3,342,778.48 (10.9%); £3,752,744.97 -> £3,342,778.56 (10.9%); £3,752,745.23 -> £3,342,778.54 (10.9%); £3,752,745.49 -> £3,342,778.51 (10.9%); £3,752,745.77 -> £3,342,778.49 (10.9%); £3,752,746.04 -> £3,342,778.47 (10.9%); £3,752,746.32 -> £3,342,778.46 (10.9%); £3,752,746.59 -> £3,342,778.46 (10.9%); £3,752,746.83 -> £3,342,778.45 (10.9%); £3,752,747.06 -> £3,342,778.45 (10.9%); £3,752,747.27 -> £3,342,778.45 (10.9%); £3,752,747.44 -> £3,342,778.45 (10.9%); £3,752,747.60 -> £3,342,778.45 (10.9%); £3,752,747.76 -> £3,342,778.45 (10.9%); £3,752,747.92 -> £3,342,778.45 (10.9%); £3,752,748.07 -> £3,342,778.45 (10.9%); £3,752,748.24 -> £3,342,778.46 (10.9%); £3,752,748.39 -> £3,342,778.46 (10.9%); £3,752,748.55 -> £3,342,778.46 (10.9%); £3,752,748.70 -> £3,342,778.46 (10.9%); £3,752,748.87 -> £3,342,778.46 (10.9%); £3,752,749.03 -> £3,342,778.47 (10.9%); £3,752,749.18 -> £3,342,778.46 (10.9%); £3,752,749.34 -> £3,342,778.46 (10.9%); £3,752,749.52 -> £3,342,778.50 (10.9%); £3,752,749.72 -> £3,342,778.55 (10.9%); £3,752,749.94 -> £3,342,778.61 (10.9%); £3,752,750.17 -> £3,342,778.65 (10.9%); £3,752,750.42 -> £3,342,778.70 (10.9%); £3,752,750.69 -> £3,342,778.74 (10.9%); £3,752,750.96 -> £3,342,778.78 (10.9%); £3,752,751.23 -> £3,342,778.82 (10.9%); £3,752,751.50 -> £3,342,778.81 (10.9%); £3,752,751.76 -> £3,342,778.81 (10.9%); £3,752,752.03 -> £3,342,778.81 (10.9%); £3,752,752.30 -> £3,342,778.81 (10.9%); £3,752,752.58 -> £3,342,778.81 (10.9%); £3,752,752.85 -> £3,342,778.81 (10.9%); £3,752,753.13 -> £3,342,778.81 (10.9%); £3,752,753.40 -> £3,342,778.81 (10.9%); £3,752,753.66 -> £3,342,778.81 (10.9%); £3,752,753.93 -> £3,342,778.81 (10.9%); £3,752,754.20 -> £3,342,778.84 (10.9%); £3,752,754.47 -> £3,342,778.90 (10.9%); £3,752,754.74 -> £3,342,778.97 (10.9%); £3,752,755.01 -> £3,342,779.04 (10.9%); £3,752,755.28 -> £3,342,779.10 (10.9%); £3,752,755.55 -> £3,342,779.17 (10.9%); £3,752,755.82 -> £3,342,779.25 (10.9%); £3,752,756.09 -> £3,342,779.33 (10.9%); £3,752,756.36 -> £3,342,779.31 (10.9%); £3,752,756.62 -> £3,342,779.28 (10.9%); £3,752,756.89 -> £3,342,779.26 (10.9%); £3,752,757.16 -> £3,342,779.24 (10.9%); £3,752,757.43 -> £3,342,779.23 (10.9%); £3,752,757.71 -> £3,342,779.23 (10.9%); £3,752,757.96 -> £3,342,779.22 (10.9%); £3,752,758.18 -> £3,342,779.22 (10.9%); £3,752,758.39 -> £3,342,779.22 (10.9%); £3,752,758.55 -> £3,342,779.22 (10.9%); £3,752,758.72 -> £3,342,779.22 (10.9%); £3,752,758.88 -> £3,342,779.22 (10.9%); £3,752,759.04 -> £3,342,779.22 (10.9%); £3,752,759.20 -> £3,342,779.22 (10.9%); £3,752,759.36 -> £3,342,779.22 (10.9%); £3,752,759.52 -> £3,342,779.23 (10.9%); £3,752,759.68 -> £3,342,779.23 (10.9%); £3,752,759.84 -> £3,342,779.23 (10.9%); £3,752,760.00 -> £3,342,779.23 (10.9%); £3,752,760.16 -> £3,342,779.24 (10.9%); £3,752,760.32 -> £3,342,779.23 (10.9%); £3,752,760.48 -> £3,342,779.23 (10.9%); £3,752,760.67 -> £3,342,779.27 (10.9%); £3,752,760.87 -> £3,342,779.33 (10.9%); £3,752,761.09 -> £3,342,779.38 (10.9%); £3,752,761.32 -> £3,342,779.43 (10.9%); £3,752,761.57 -> £3,342,779.47 (10.9%); £3,752,761.85 -> £3,342,779.52 (10.9%); £3,752,762.12 -> £3,342,779.55 (10.9%); £3,752,762.38 -> £3,342,779.59 (10.9%); £3,752,762.65 -> £3,342,779.59 (10.9%); £3,752,762.93 -> £3,342,779.58 (10.9%); £3,752,763.20 -> £3,342,779.58 (10.9%); £3,752,763.47 -> £3,342,779.58 (10.9%); £3,752,763.74 -> £3,342,779.58 (10.9%); £3,752,764.02 -> £3,342,779.58 (10.9%); £3,752,764.30 -> £3,342,779.58 (10.9%); £3,752,764.56 -> £3,342,779.58 (10.9%); £3,752,764.83 -> £3,342,779.58 (10.9%); £3,752,765.11 -> £3,342,779.58 (10.9%); £3,752,765.38 -> £3,342,779.61 (10.9%); £3,752,765.66 -> £3,342,779.67 (10.9%); £3,752,765.93 -> £3,342,779.73 (10.9%); £3,752,766.20 -> £3,342,779.80 (10.9%); £3,752,766.47 -> £3,342,779.87 (10.9%); £3,752,766.73 -> £3,342,779.93 (10.9%); £3,752,767.01 -> £3,342,780.02 (10.9%); £3,752,767.29 -> £3,342,780.10 (10.9%); £3,752,767.57 -> £3,342,780.07 (10.9%); £3,752,767.84 -> £3,342,780.05 (10.9%); £3,752,768.12 -> £3,342,780.02 (10.9%); £3,752,768.38 -> £3,342,780.00 (10.9%); £3,752,768.66 -> £3,342,779.99 (10.9%); £3,752,768.93 -> £3,342,779.99 (10.9%); £3,752,769.19 -> £3,342,779.98 (10.9%); £3,752,769.43 -> £3,342,779.98 (10.9%); £3,752,769.64 -> £3,342,779.98 (10.9%); £3,752,769.80 -> £3,342,779.98 (10.9%); £3,752,769.96 -> £3,342,779.98 (10.9%); £3,752,770.12 -> £3,342,779.98 (10.9%); £3,752,770.29 -> £3,342,779.98 (10.9%); £3,752,770.45 -> £3,342,779.98 (10.9%); £3,752,770.61 -> £3,342,779.98 (10.9%); £3,752,770.77 -> £3,342,779.99 (10.9%); £3,752,770.94 -> £3,342,779.99 (10.9%); £3,752,771.10 -> £3,342,779.99 (10.9%); £3,752,771.26 -> £3,342,779.99 (10.9%); £3,752,771.43 -> £3,342,779.99 (10.9%); £3,752,771.59 -> £3,342,779.99 (10.9%); £3,752,771.75 -> £3,342,779.98 (10.9%); £3,752,771.93 -> £3,342,780.03 (10.9%); £3,752,772.12 -> £3,342,780.08 (10.9%); £3,752,772.34 -> £3,342,780.13 (10.9%); £3,752,772.57 -> £3,342,780.18 (10.9%); £3,752,772.82 -> £3,342,780.23 (10.9%); £3,752,773.08 -> £3,342,780.27 (10.9%); £3,752,773.36 -> £3,342,780.31 (10.9%); £3,752,773.62 -> £3,342,780.34 (10.9%); £3,752,773.89 -> £3,342,780.34 (10.9%); £3,752,774.16 -> £3,342,780.34 (10.9%); £3,752,774.43 -> £3,342,780.34 (10.9%); £3,752,774.71 -> £3,342,780.34 (10.9%); £3,752,774.99 -> £3,342,780.33 (10.9%); £3,752,775.26 -> £3,342,780.33 (10.9%); £3,752,775.53 -> £3,342,780.33 (10.9%); £3,752,775.80 -> £3,342,780.33 (10.9%); £3,752,776.07 -> £3,342,780.33 (10.9%); £3,752,776.33 -> £3,342,780.33 (10.9%); £3,752,776.60 -> £3,342,780.37 (10.9%); £3,752,776.87 -> £3,342,780.42 (10.9%); £3,752,777.14 -> £3,342,780.49 (10.9%); £3,752,777.41 -> £3,342,780.55 (10.9%); £3,752,777.68 -> £3,342,780.62 (10.9%); £3,752,777.95 -> £3,342,780.69 (10.9%); £3,752,778.22 -> £3,342,780.77 (10.9%); £3,752,778.50 -> £3,342,780.85 (10.9%); £3,752,778.76 -> £3,342,780.83 (10.9%); £3,752,779.03 -> £3,342,780.80 (10.9%); £3,752,779.32 -> £3,342,780.78 (10.9%); £3,752,779.59 -> £3,342,780.76 (10.9%); £3,752,779.85 -> £3,342,780.75 (10.9%); £3,752,780.12 -> £3,342,780.75 (10.9%); £3,752,780.38 -> £3,342,780.74 (10.9%); £3,752,780.61 -> £3,342,780.74 (10.9%)
- Bills issued: 147, average clarity 0.811, average bill shock 18.5%, bad debt provision £-212.24, avg complaint probability 4.9%
- Solvency signal: £375,572/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £199,889.25 vs. naked (unhedged) net margin: £605,205.29
- hedging cost £405,316.04 vs. a fully unhedged book (commodity-only: actual net £199,889.25 vs. naked net £605,205.29)
  - C2: actual £177.42 vs. naked £612.31 -- hedging cost £434.90
  - C2g: actual £210.79 vs. naked £379.12 -- hedging cost £168.33
  - C4: actual £85.60 vs. naked £374.56 -- hedging cost £288.96
  - C4g: actual £34.61 vs. naked £516.32 -- hedging cost £481.70
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £304.00 vs. naked £1,379.17 -- hedging cost £1,075.17
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £18,881.87 vs. naked £119,700.18 -- hedging cost £100,818.31
  - C_IC3g: actual £3,837.46 vs. naked £56,934.03 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £102,722.50 -- hedging cost £101,286.98

**Year narrative:** 2024 produced a net gain of £368,471.75 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 42 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £121,409.36 (gross £518,802.43, capital £5,661.91)
  - Electricity: gross £464,774.71, capital £5,632.07, net £116,827.98
  - Gas: gross £54,027.73, capital £29.84, net £4,581.38
- Treasury at year end: £3,807,649.10
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
- Average CLV (Point-in-Time, year-end 2025): £367,905.19
  - By billing account: C1 £3,019.63, C2 £4,402.36, C3 £3,994.10, C4 £2,589.98, C5 £7,053.73, C6 £11,503.53, C7 £5,167.90, C8 £6,323.99, C9 £5,874.17, C_IC1 £1,164,918.22, C_IC2 £573,178.15, C_IC3 £1,901,080.89, C_IC4 £1,093,660.82
- Bill shock events (>=20%): 25 -- C7 2025-04-30 (36%); C7 2025-05-31 (37%); C7 2025-06-07 (157%); C2 2025-04-30 (23%); C2g 2025-01-31 (32%); C2g 2025-02-28 (24%); C2g 2025-04-30 (30%); C2g 2025-05-31 (34%); C2g 2025-06-07 (73%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (40%); C8 2025-05-31 (42%); C8 2025-06-07 (195%); C9 2025-04-30 (24%); C9 2025-05-31 (33%); C9 2025-06-07 (72%); C4 2025-04-30 (32%); C4 2025-06-07 (79%); C4g 2025-01-31 (24%); C4g 2025-05-31 (57%); C4g 2025-06-07 (126%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2 38%, C8 35%, C9 26%

**Pricing & Margin**

- C2 (electricity): tariff £149.29-£301.52/MWh, net margin £53.29
- C2g (gas): tariff £48.41-£52.00/MWh, net margin £91.09
- C4 (electricity): tariff £159.80-£305.07/MWh, net margin £81.71
- C4g (gas): tariff £48.05/MWh, net margin £40.50
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
- Solvency signal: £423,072/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-18.69 vs. naked (unhedged) net margin: £199.65
- hedging cost £218.34 vs. a fully unhedged book (commodity-only: actual net £-18.69 vs. naked net £199.65)
  - C2: actual £0.57 vs. naked £84.47 -- hedging cost £83.90
  - C2g: actual £7.37 vs. naked £-3.72 -- hedging added £11.08
  - C8: actual £-26.63 vs. naked £118.90 -- hedging cost £145.52

**Year narrative:** 2025 produced a net gain of £121,409.36 across 12 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 25 customer(s) experienced a bill shock of >=20%.
