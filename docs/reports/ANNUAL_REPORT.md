# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,902,095.14
  (£1,435,458.92 net change)
- Solvency signal (final year): £425,227/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £22,617,061.76
  VAT remitted to HMRC: (£3,748,458.54) | Revenue (ex-VAT): £18,868,603.22
  Non-commodity pass-through: (£4,792,999.58)
- Gross margin: £6,477,859.06
- Capital costs: £51,377.37
- Net margin: £6,426,481.69
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.1%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1588, average clarity 0.783,
  service quality score 0.883
- Enterprise value (CLV sum across 14 billing accounts): £7,730,031.11
- Cost to serve (whole portfolio): £23,293.21, net margin after cost to serve: £6,403,188.48
- Hedge effectiveness (whole window): hedging cost £4,222,848.02 vs. a fully unhedged book (commodity-only: actual net £1,435,458.92 vs. naked net £5,658,306.93)

- **2021** (crisis year): net margin £75,467.55, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £338,410.43, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2251, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 243.0x (net £65,099.25 on £267.86 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 3/5 departures (60%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 4.7%, max 16.5% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +34.0% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 34.1% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,477,859.06, capital £51,377.37, net £6,426,481.69. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £75,467.55 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.1%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,426,481.69
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
| 2022 | £330,000.66 | £9,999.92 | £1,141.20 | £-1,472.26 | £-1,259.09 | £338,410.43 |
| 2023 | £135,957.41 | £9,999.92 | £-708.90 | £37.44 | £-976.37 | £144,309.49 |
| 2024 | £333,515.99 | £10,030.76 | £772.41 | £2,771.37 | £678.12 | £347,768.66 |
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
| 2023 | 3,382,576 | 11 | 307,507 | 2365.44× | OK |
| 2024 | 3,775,104 | 11 | 343,191 | 2639.93× | OK |
| 2025 | 3,827,043 | 9 | 425,227 | 3270.98× | OK |

End-state (2025): **£425,227/account** across 9 billing accounts — OK.

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
| 2023 | 5,604 | 6,725 | 3,382,576 | 503.0× | OK |
| 2024 | 2,651 | 3,182 | 3,775,104 | 1186.5× | OK |
| 2025 | 3,872 | 4,647 | 3,827,043 | 823.6× | OK |




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
| 2017 | 68 | 281% | C5 (2017-02-28) |
| 2018 | 83 | 1415% | C3g (2018-08-31) |
| 2019 | 76 | 152% | C3 (2019-09-30) |
| 2020 | 74 | 319% | C5 (2020-12-29) |
| 2021 | 53 | 1202% | C1_2 (2021-01-31) |
| 2022 | 73 | 298% | C1_2 (2022-09-30) |
| 2023 | 65 | 275% | C6 (2023-11-30) |
| 2024 | 49 | 174% | C1_2 (2024-09-30) |
| 2025 | 26 | 195% | C8 (2025-06-07) |

Total: **605** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2018-08-31 | C3g | +1415% | no |
| 2021-01-31 | C1_2 | +1202% | no |
| 2020-12-29 | C5 | +319% | yes |
| 2018-07-31 | C7 | +313% | no |
| 2022-09-30 | C1_2 | +298% | no |
| 2017-02-28 | C5 | +281% | yes |
| 2023-11-30 | C6 | +275% | yes |
| 2023-03-31 | C1_2 | +254% | no |
| 2020-08-31 | C6 | +210% | yes |
| 2017-05-31 | C6 | +203% | yes |

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

**Full-history EV:** £7,730,031.11 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £677,722.33 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

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
| 2022 | £338,410.43 |
| 2023 | £144,309.49 | ← trailing
| 2024 | £347,768.66 | ← trailing
| 2025 | £120,992.97 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £5,023.01 | — |
| C1_2 | — | £612.56 |
| C2 | £6,225.07 | £933.32 |
| C3 | £6,087.26 | — |
| C4 | £3,400.81 | £-1,025.63 |
| C5 | £10,919.84 | — |
| C6 | £19,260.39 | £105.36 |
| C7 | £8,738.68 | £565.03 |
| C8 | £9,622.89 | £737.43 |
| C9 | £9,949.67 | £1,413.67 |
| C_IC1 | £1,762,208.13 | £389,093.54 |
| C_IC2 | £957,420.63 | £205,248.66 |
| C_IC3 | £3,214,252.57 | £64,153.93 |
| C_IC4 | £1,712,238.71 | £15,884.48 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C1_2 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £5,987.12 | — | — | — | — | £14,339.54 | — | £10,526.48 | — | — | — | — | — | — |
| 2017 | £5,273.18 | — | £10,543.99 | £8,991.34 | £8,169.64 | £12,167.53 | £24,200.80 | £8,895.16 | £13,842.89 | £11,262.19 | — | — | — | — |
| 2018 | £5,231.06 | — | £8,116.09 | £9,006.59 | £6,798.71 | £12,344.35 | £20,424.84 | £8,038.55 | £10,898.61 | £10,640.88 | £2,792,331.69 | — | — | — |
| 2019 | £5,209.69 | — | £8,270.81 | £7,728.96 | £6,073.23 | £11,192.06 | £19,074.59 | £8,373.08 | £9,472.90 | £9,974.34 | £2,348,957.18 | £1,778,067.01 | — | — |
| 2020 | £4,257.86 | £16.03 | £6,187.77 | £5,529.21 | £6,582.41 | £12,943.29 | £19,510.54 | £7,742.53 | £9,552.17 | £9,057.96 | £1,391,889.73 | £887,578.71 | £2,194,078.02 | £1,462,114.75 |
| 2021 | £4,370.98 | £986.91 | £6,356.47 | £5,469.19 | £5,002.01 | £12,050.99 | £17,951.57 | £6,973.39 | £9,219.23 | £8,492.59 | £1,502,450.85 | £765,170.10 | £2,016,503.84 | £1,364,017.02 |
| 2022 | £4,221.34 | £2,003.94 | £4,701.56 | £4,770.70 | £2,833.30 | £9,425.03 | £15,793.20 | £5,021.24 | £7,914.07 | £7,134.34 | £1,299,467.84 | £764,895.23 | £2,824,425.06 | £1,074,640.43 |
| 2023 | £3,390.74 | £1,944.13 | £4,662.99 | £4,163.83 | £1,814.68 | £7,623.31 | £17,306.38 | £5,356.78 | £7,277.99 | £6,952.69 | £1,320,738.65 | £640,507.44 | £1,889,602.01 | £1,169,282.75 |
| 2024 | £3,032.53 | £2,675.04 | £4,104.74 | £3,782.52 | £2,320.90 | £7,834.04 | £15,341.31 | £4,975.97 | £7,062.48 | £7,097.09 | £1,156,263.05 | £680,833.29 | £2,017,068.09 | £963,733.92 |
| 2025 | £3,385.93 | £3,572.27 | £4,120.20 | £3,784.18 | £2,236.78 | £6,507.60 | £13,097.23 | £5,846.15 | £6,249.07 | £6,617.37 | £1,073,429.56 | £766,140.36 | £2,039,343.77 | £1,121,677.29 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £1,225.96, range £219.95–£4,218.12.

- C1: cost to serve £274.94, net margin after CTS £2,068.10
- C1_2: cost to serve £244.19, net margin after CTS £5,418.65
- C1g: cost to serve £275.00, net margin after CTS £1,080.24
- C2: cost to serve £505.43, net margin after CTS £5,017.38
- C2g: cost to serve £505.55, net margin after CTS £2,781.94
- C3: cost to serve £219.95, net margin after CTS £2,168.93
- C3g: cost to serve £220.00, net margin after CTS £1,078.53
- C4: cost to serve £439.89, net margin after CTS £2,803.41
- C4g: cost to serve £440.00, net margin after CTS £803.04
- C5: cost to serve £599.87, net margin after CTS £7,230.71
- C6: cost to serve £959.77, net margin after CTS £21,746.58
- C7: cost to serve £519.13, net margin after CTS £10,234.75
- C8: cost to serve £505.43, net margin after CTS £11,924.39
- C9: cost to serve £491.72, net margin after CTS £12,216.81
- C_IC1: cost to serve £4,218.12, net margin after CTS £1,870,784.18
- C_IC2: cost to serve £3,718.18, net margin after CTS £905,291.97
- C_IC3: cost to serve £3,218.32, net margin after CTS £1,821,875.22
- C_IC3g: cost to serve £3,219.18, net margin after CTS £619,427.85
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
| 2022 | 14 | £245,590 | £74,945 | £24,172 | 9.8% |
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
| C4 | £126 | — | £126 |
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
| **Total** | **£1,458,958** | **£65,099** | **£1,524,058** |

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
| 2016 | 0.792 R | 5.9% | 0.30% | 38 | 108 | RED ! |
| 2017 | 0.785 R | 5.7% | 0.26% | 68 | 168 | RED ! |
| 2018 | 0.755 R | 6.4% | 0.36% | 83 | 180 | RED ! |
| 2019 | 0.793 R | 5.7% | 0.24% | 76 | 204 | RED ! |
| 2020 | 0.795 R | 5.5% | 0.24% | 74 | 205 | RED ! |
| 2021 | 0.805 A | 5.2% | 0.26% | 53 | 168 | AMBER |
| 2022 | 0.766 R | 6.4% | 0.30% | 73 | 168 | RED ! |
| 2023 | 0.766 R | 6.3% | 0.29% | 65 | 168 | RED ! |
| 2024 | 0.790 R | 5.5% | 0.23% | 49 | 153 | RED ! |
| 2025 | 0.776 R | 6.0% | 0.27% | 26 | 66 | RED ! |

Worst clarity year: **2018** (0.755)
Highest complaint probability: **2022** (6.4%)
Worst bill shock: **2018** (0.36%)
RED years: 2016, 2017, 2018, 2019, 2020, 2022, 2023, 2024, 2025
AMBER years: 2021
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
| 2022 | 2.70 | WATCH | £3,161,940 | £338,410 |
| 2023 | 2.72 | WATCH | £3,382,576 | £144,309 |
| 2024 | — | — | £3,775,104 | £347,769 |
| 2025 | — | — | £3,827,043 | £120,993 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,827,043)**
**Treasury growth: £2,467,441 → £3,827,043 (+£1,359,602)**

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
| Status Quo (hold gas) | £203,699 | — |
| Exit Gas (with churn risk) | £83,544 | -£120,155 |
| Reprice to Breakeven | £205,410 | +£1,711 |

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
| 2024 | 2024-09-28 | 48 | C4 | -£123 |
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
| 2016 | 14 | £173,370 | £92,774 | £9,008 | £12,384 |
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
| 2022 | -£49,726 CREDIT | £256,149 | £9 | 2 | 168 |
| 2023 | +£64,738 | £271,739 | £2,260 | 47 | 168 |
| 2024 | +£109,869 | £307,451 | £-67 | 4271 | 153 |
| 2025 | +£46,911 | £135,614 | £0 | — | 66 |

**CfD turned CREDIT in 2022: -£49,726 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2023 (£2,260)**

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
| 2023 | £3,382,576 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,775,104 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,827,043 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 41.3% | £1,247 | £634 | 1.62% |
| 2017 | 14 | 32.8% | £24,836 | £8,874 | 2.02% |
| 2018 | 15 | 41.0% | £40,021 | £17,557 | 2.23% |
| 2019 | 17 | 40.3% | £96,608 | £41,350 | 2.13% |
| 2020 | 19 | 40.2% | £97,823 | £41,980 | 2.35% |
| 2021 | 14 | 28.9% | £172,445 | £54,385 | 2.22% |
| 2022 | 14 | 22.1% | £302,894 | £75,072 | 2.27% |
| 2023 | 14 | 24.8% | £248,506 | £68,865 | 2.51% |
| 2024 | 14 | 39.0% | £214,120 | £89,587 | 2.44% |
| 2025 | 11 | 39.8% | £116,737 | £51,058 | 3.35% |

**Best EBIT%: 2016 (41.3%)** | **Worst EBIT%: 2022 (22.1%)**
**Peak revenue/customer: 2022 (£302,894)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Population Anchoring -- Complaints & Arrears (Phase PS)

SIM aggregate complaint and arrears rates vs published UK benchmarks.
Complaints: Ofgem QoS survey, I&C adjusted (GREEN 2-6%, crisis 2-8%).
Arrears: DESNZ business energy debt (GREEN <8%, crisis <12%).

| Year | Complaint rate% | C.Bench hi | C.RAG | Arrears rate% | A.Bench hi | A.RAG |
|------|-----------------|-----------|-------|---------------|-----------|-------|
| 2016 | 5.91% | 6% | OK | 23.1% | 8% | ! |
| 2017 | 5.75% | 6% | OK | 50.0% | 8% | ! |
| 2018 | 6.43% | 6% | ~ | 13.3% | 8% | ~ |
| 2019 | 5.65% | 6% | OK | 41.2% | 8% | ! |
| 2020 | 5.45% | 6% | OK | 5.3% | 8% | OK |
| 2021 | 5.18% | 8% | OK | 7.1% | 12% | OK |
| 2022 | 6.44% | 8% | OK | 28.6% | 12% | ! |
| 2023 | 6.31% | 8% | OK | 28.6% | 12% | ! |
| 2024 | 5.49% | 6% | OK | 21.4% | 8% | ! |
| 2025 | 6.01% | 6% | ~ | 36.4% | 8% | ! |

**Complaints:** 8 of 10 years GREEN (I&C baseline 2-6% normal, 2-8% crisis).
**Arrears:** 2 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).

## Plausibility vs Industry

Key metrics vs UK retail energy norms (Ofgem/Cornwall Insight). OK = within range | ~ = amber | ! = outside expected range.

| Year | Net margin% | Gross margin% | Bad debt% | Churn% |
|------|-------------|---------------|-----------|--------|
| 2016 | !41.3% | !50.9% | OK1.62% | ~0% |
| 2017 | !32.8% | !35.7% | OK2.02% | ~0% |
| 2018 | !41.0% | !43.9% | OK2.23% | ~0% |
| 2019 | !40.3% | !42.8% | OK2.13% | ~0% |
| 2020 | !40.2% | !42.9% | OK2.35% | OK16% |
| 2021 | !28.9% | !31.5% | OK2.22% | ~0% |
| 2022 | !22.1% | ~24.8% | OK2.27% | ~0% |
| 2023 | !24.8% | ~27.7% | OK2.51% | ~0% |
| 2024 | !39.0% | !41.8% | OK2.44% | OK14% |
| 2025 | !39.8% | !43.7% | OK3.35% | ~0% |

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

**Total bad debt (all years):** £3,442
**Crisis stress incremental:** £5,163

**RAG [OK]:** GREEN — Incremental credit stress below 0.5% revenue — not material

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (11 active customers) under 12-month forward scenarios.
Generated: 2026-07-12T16:58:35Z

Closes CLAUDE.md known failure: regime-change blindness — board can now ask 'what if 2021-22 happened again?'

| Scenario | Elec Fwd (£/MWh) | Gas Fwd (£/MWh) | Hedge Rec | Renewing | Exposure Delta |
|----------|------------------|-----------------|-----------|----------|----------------|
| Base | 86.7 | 55.1 | INCREASE | 0 | — |
| Bull | 56.1 | 35.7 | INCREASE | 0 | £-399,124 |
| Bear | 147.9 | 93.8 | INCREASE | 0 | +£798,248 |
| Crisis | 217.3 | 110.2 | INCREASE | 0 | +£1,565,117 |

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
| 2016 | 3 | £30,853 | £10,284 | — |
| 2017 | 9 | £103,347 | £11,483 | +£72,494 |
| 2018 | 10 | £2,883,831 | £288,383 | +£2,780,485 |
| 2019 | 11 | £4,212,394 | £382,945 | +£1,328,562 |
| 2020 | 14 | £6,017,041 | £429,789 | +£1,804,647 |
| 2021 | 14 | £5,725,015 | £408,930 | £-292,026 |
| 2022 | 14 | £6,027,247 | £430,518 | +£302,232 |
| 2023 | 14 | £5,080,624 | £362,902 | £-946,623 |
| 2024 | 14 | £4,876,125 | £348,295 | £-204,499 |
| 2025 | 14 | £5,056,008 | £361,143 | +£179,883 |

**Peak portfolio CLV: 2022 (£6,027,247)** | **Earliest/lowest: 2016 (£30,853)**
**Largest YoY gain: 2018 (+£2,780,485)**
**Largest YoY fall: 2023 (£-946,623)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £16,206.51 | £3,594.97 | £4,363.77 | £8,247.77 | 50.9% | — | — | — | — |
| 2017 | £347,703.10 | £111,055.46 | £112,416.49 | £124,231.15 | 35.7% | +£331,496.60 | +£107,460.50 | +£108,052.72 | +£115,983.37 |
| 2018 | £600,311.84 | £172,888.20 | £164,071.67 | £263,351.98 | 43.9% | +£252,608.74 | +£61,832.74 | +£51,655.17 | +£139,120.83 |
| 2019 | £1,642,333.62 | £496,185.23 | £443,205.99 | £702,942.41 | 42.8% | +£1,042,021.78 | +£323,297.03 | +£279,134.32 | +£439,590.43 |
| 2020 | £1,858,632.06 | £431,600.88 | £629,415.51 | £797,615.67 | 42.9% | +£216,298.43 | £-64,584.35 | +£186,209.52 | +£94,673.27 |
| 2021 | £2,414,227.55 | £971,905.80 | £680,933.21 | £761,388.54 | 31.5% | +£555,595.49 | +£540,304.92 | +£51,517.71 | £-36,227.14 |
| 2022 | £4,240,512.12 | £2,389,086.10 | £800,420.93 | £1,051,005.09 | 24.8% | +£1,826,284.57 | +£1,417,180.30 | +£119,487.72 | +£289,616.55 |
| 2023 | £3,479,090.27 | £1,639,053.05 | £875,932.70 | £964,104.53 | 27.7% | £-761,421.84 | £-750,033.06 | +£75,511.77 | £-86,900.56 |
| 2024 | £2,997,675.46 | £931,630.07 | £811,823.55 | £1,254,221.84 | 41.8% | £-481,414.81 | £-707,422.97 | £-64,109.15 | +£290,117.31 |
| 2025 | £1,284,109.47 | £452,060.81 | £270,415.77 | £561,632.89 | 43.7% | £-1,713,565.99 | £-479,569.26 | £-541,407.78 | £-692,588.95 |

**Best GM year: 2016 (50.9%)** | **Worst GM year: 2022 (24.8%)**

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
| 2021→2022 | +£262,943 | +£286,070 | +£365 | -£7,674 | -£1,057 | -£14,761 | +0 | gross margin | GREEN |
| 2022→2023 | -£194,101 | -£93,343 | -£2,251 | +£3,240 | -£70,553 | -£31,194 | +0 | gross margin | RED |
| 2023→2024 | +£203,459 | +£301,924 | +£2,327 | +£514 | -£100,652 | -£654 | +0 | gross margin | GREEN |
| 2024→2025 | -£226,776 | -£739,194 | -£67 | +£3,875 | +£381,910 | +£126,700 | -3 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£226,776)** | **Best transition: 2021→2022 (+£262,943)**

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
| 2022 | £9 | 0.00% | 9/11 | 82% | ↓ IMPROVING | RED |
| 2023 | £2,260 | 0.09% | 10/11 | 91% | ↑ DETERIORATING | RED |
| 2024 | £-67 | -0.00% | 4/11 | 36% | ↓ IMPROVING | AMBER |
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
| 2016 | £2,473,323.59 | £1,350.54 | 1831.4x | ✓ GREEN | Yes |
| 2017 | £2,587,301.14 | £28,975.26 | 89.3x | ✓ GREEN | Yes |
| 2018 | £2,833,162.79 | £50,025.99 | 56.6x | ✓ GREEN | Yes |
| 2019 | £3,495,357.65 | £136,861.14 | 25.5x | ✓ GREEN | Yes |
| 2020 | £4,242,971.23 | £154,886.00 | 27.4x | ✓ GREEN | Yes |
| 2021 | £4,941,523.82 | £201,185.63 | 24.6x | ✓ GREEN | Yes |
| 2022 | £5,879,281.17 | £353,376.01 | 16.6x | ✓ GREEN | Yes |
| 2023 | £6,742,509.29 | £289,924.19 | 23.3x | ✓ GREEN | Yes |
| 2024 | £7,910,115.73 | £249,806.29 | 31.7x | ✓ GREEN | Yes |
| 2025 | £8,421,562.96 | £107,009.12 | 78.7x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.6x (equity £5,879,281.17 vs monthly revenue £353,376.01). RAG: GREEN.
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
| 2017 | £347,703.10 | £129,229.65 | £1,098.45 | ✓ GREEN |  |
| 2018 | £600,311.84 | £223,115.90 | £1,896.49 | ✓ GREEN |  |
| 2019 | £1,642,333.62 | £610,400.66 | £5,188.41 | ✓ GREEN |  |
| 2020 | £1,858,632.06 | £690,791.58 | £5,871.73 | ✓ GREEN |  |
| 2021 | £2,414,227.55 | £897,287.91 | £7,626.95 | ✓ GREEN | CREDIT EXPECTED |
| 2022 | £4,240,512.12 | £1,576,057.00 | £13,396.48 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,479,090.27 | £1,293,061.88 | £10,991.03 | ✓ GREEN |  |
| 2024 | £2,997,675.46 | £1,114,136.05 | £9,470.16 | ✓ GREEN |  |
| 2025 | £1,284,109.47 | £477,260.68 | £4,056.72 | ✓ GREEN |  |

**Peak reconciliation exposure:** 2022 — max adverse £13,396 (4.5 months weighted tail).

_Note: Outstanding pool ≈ current-year revenue × (weighted outstanding months ÷ 12)._
_Max adverse = pool × blended variance rate (0.5% HH + 4% non-HH, portfolio-weighted)._
## Ofgem Supply Licence Health (Phase OC)

Annual licence health checks: customer base, net assets, liquidity, bad debt.
Breach triggers board escalation and Ofgem notification under SLC 0.
WATCH = within 20% of threshold. BREACH = threshold crossed.

| Year | Customers | Net Assets | Treasury | Cash Wks | Bad Debt % | Overall |
|------|-----------|------------|----------|----------|------------|---------|
| 2016 | 13 | £2,473,323.59 | £2,467,441.30 | 35691w | 0.64% | ✗ BREACH |
| 2017 | 14 | £2,587,301.14 | £2,498,923.22 | 1170w | 0.18% | ✗ BREACH |
| 2018 | 15 | £2,833,162.79 | £2,487,782.60 | 748w | 0.08% | ✗ BREACH |
| 2019 | 17 | £3,495,357.65 | £2,611,908.89 | 274w | 0.00% | ✗ BREACH |
| 2020 | 19 | £4,242,971.23 | £2,924,300.68 | 352w | -0.00% | ✗ BREACH |
| 2021 | 14 | £4,941,523.82 | £2,957,767.54 | 158w | 0.02% | ✗ BREACH |
| 2022 | 14 | £5,879,281.17 | £3,161,940.47 | 69w | 0.00% | ✗ BREACH |
| 2023 | 14 | £6,742,509.29 | £3,382,575.78 | 107w | 0.09% | ✗ BREACH |
| 2024 | 14 | £7,910,115.73 | £3,775,103.96 | 211w | -0.00% | ✗ BREACH |
| 2025 | 11 | £8,421,562.96 | £3,827,043.26 | 440w | 0.00% | ✗ BREACH |

**BREACH years:** 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 — board escalation required.

_Note: Complaints from contact model avg_complaint_probability. Customer count <50 triggers Ofgem viability review — small-portfolio years will show WATCH._
## Ofgem SLC Compliance Scorecard (Phase OD)

10 compliance domains per year, derived from simulation outputs.
G = GREEN (compliant), A = AMBER (watch), R = RED (breach).

| Domain | SLC Ref | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|--------|---------|------|------|------|------|------|------|------|------|------|------|
| Governance | SLC 0-9 | G | G | G | G | G | G | G | G | G | G |
| Billing/Metering | SLC 10-14 | A | A | A | A | A | G | A | A | A | A |
| Payment/Debt | SLC 15-19 | G | G | G | G | G | G | G | G | G | G |
| Information | SLC 20-24 | G | G | G | G | G | G | G | G | G | G |
| Complaints | SLC 25-29 / Ofgem Time to Fix rules | G | G | G | G | G | G | G | G | G | G |
| Vulnerable Cust | SLC 30-35 / PSR | G | G | G | G | G | G | G | G | G | G |
| Tariff/Cap | SLC 36-40 / Default Tariff Cap | G | G | G | G | G | G | G | G | G | G |
| Environmental | SLC 41-50 / RO, CfD, EE obligation | G | G | G | G | G | G | G | G | G | G |
| Network/BSC | SLC 51-60 / BSC obligations | G | G | G | G | G | G | G | G | G | G |
| Financial Res. | SLC 4C / SFR Decision 2023 | G | G | G | G | G | G | G | G | G | G |
| **Overall** |  | A | A | A | A | A | G | A | A | A | A |

**Watch years (AMBER):** 2016, 2017, 2018, 2019, 2020, 2022, 2023, 2024, 2025

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
| 2022 | Yes | 14/14/14 | 19.0 | 11.8 | £1 |
| 2023 | Yes | 14/14/14 | 15.3 | 6.0 | £161 |
| 2024 | Yes | 14/14/14 | 12.8 | 5.4 | £-5 |
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
| 2023 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP158 |
| 2024 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP136 |
| 2025 | ECO4 | GBP6.80 | 6 | OK (exempt) | GBP58 |

Counterfactual total 2016-2025 (if 150k domestic): **GBP746**

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
Median CLV: £9,949.67 | Median churn: 32% | Total portfolio CLV: £7,725,347.66

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
| C_IC3 | £3,214,252.57 | 41% | 16.4 periods |
| C_IC2 | £957,420.63 | 32% | 14.2 periods |
| C5 | £10,919.84 | 32% | 14.8 periods |

Quadrant CLV: £4,182,593.04 (54% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C7 | £8,738.68 | 29% | 15.4 periods |
| C3 | £6,087.26 | 11% | 14.5 periods |

Quadrant CLV: £14,825.94 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £9,622.89 | 32% | 13.6 periods |
| C2 | £6,225.07 | 38% | 13.3 periods |
| C1 | £5,023.01 | 35% | 16.8 periods |
| C4 | £3,400.81 | 38% | 14.7 periods |

Quadrant CLV: £24,271.78 (0% of portfolio)

**Board action: CRITICAL quadrant has 3 account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**

## Customer Experience & Service Quality

| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |
|------|----------------|---------------|-------------|---------|------|
| 2016 | 0.792 | 0.059 | 0 | 0 | **LOW CLARITY** |
| 2017 | 0.785 | 0.057 | 0 | 0 | **LOW CLARITY** |
| 2018 | 0.755 | 0.064 | 0 | 0 | **LOW CLARITY** |
| 2019 | 0.793 | 0.057 | 0 | 0 | **LOW CLARITY** |
| 2020 | 0.795 | 0.055 | 2 | 0 | **LOW CLARITY** |
| 2021 | 0.805 | 0.052 | 0 | 0 |  |
| 2022 | 0.766 | 0.064 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.766 | 0.063 | 0 | 0 | **LOW CLARITY** |
| 2024 | 0.790 | 0.055 | 2 | 0 | **LOW CLARITY** |
| 2025 | 0.776 | 0.060 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 88.3% | **Average billing clarity:** 0.783 | **Average complaint probability:** 0.058

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
| 2020 | 23.8% | 74 | 205 | 36% | ELEVATED |
| 2021 | 26.5% | 53 | 168 | 32% | ELEVATED |
| 2022 | 30.4% | 73 | 168 | 43% | **HIGH** |
| 2023 | 28.8% | 65 | 168 | 39% | ELEVATED |
| 2024 | 22.8% | 49 | 153 | 32% | ELEVATED |
| 2025 | 27.4% | 26 | 66 | 39% | ELEVATED |

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
| 2022 | £329,669.60 | £8,740.82 | £2,848,806.28 | £589,446.82 | 17.1% | YES |
| 2023 | £135,285.94 | £9,023.55 | £2,296,002.86 | £298,691.57 | 11.5% | YES |
| 2024 | £337,059.77 | £10,708.88 | £1,917,076.86 | £271,569.81 | 12.4% | YES |
| 2025 | £116,452.84 | £4,540.12 | £837,702.08 | £132,970.11 | 13.7% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £203,698.91 | — | Current strategy |
| EXIT_GAS | £83,544.29 | £-120,154.62 | Remove gas; model elec churn risk |
| REPRICE_GAS | £205,410.23 | £1,711.32 | Raise gas tariff to break-even |

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
| resi electricity | £55,053.10 | £614.51 | £6,529.88 | 10.6x | Moderate |
| resi gas | £7,184.29 | £267.86 | £588.27 | 2.2x | Low return |

## Portfolio Concentration Risk

Revenue concentration analysis across 19 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2251** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,321,345.96 (98.6% of total positive margin)
- resi: £57,596.15 (0.9% of total positive margin)
- SME: £28,977.28 (0.5% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,870,784.18 | 29.2% | 3% | £60,426.33 |
| C_IC3 | I&C | £1,821,875.22 | 28.4% | 20% | £369,658.48 |
| C_IC4 | I&C | £1,103,966.75 | 17.2% | 0% | £0.00 |
| C_IC2 | I&C | £905,291.97 | 14.1% | 4% | £33,224.22 |
| C_IC3g | I&C | £619,427.85 | 9.7% | 0% | £0.00 |

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
| C4+C4g | £125.72 | £-1,711.32 | £-1,585.60 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £65,099.25.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,524,057.56 across 19 billing accounts. Revenue: £14,028,957.18.

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
| 16 | C4 | fixed | £6,193.87 | £3,243.30 | £37.88 | £125.72 | 2.0% |
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
| Policy + Network costs | -£4,855,778 | 34.6% |
| Capital cost | -£51,377 | 0.4% |
| **Net supply margin** | **£1,524,058** | **10.9%** |

> *The ledger's `net_margin_gbp` (£6,426,482) is gross − capital only, not final net.*

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

Total events: 3,382,420

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 4 |
| back_billing_write_off_event | 2 |
| bad_debt_event | 1,562 |
| billing_event | 1,587 |
| capital_charge_event | 1,628,977 |
| cost_to_serve_event | 114 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,587 |
| payment_received_event | 1,587 |
| settlement_event | 1,745,299 |
| vat_remittance_event | 1,587 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £22,617,061.76 |
|   Less: VAT remitted to HMRC | (£3,748,458.54) |
| = Revenue (ex-VAT) | £18,868,603.22 |
| Less: non-commodity pass-through | (£4,792,999.58) |
| Wholesale cost (settlement events) | (£7,597,744.58) |
| Gross margin | £6,477,859.06 |
| Capital charges | (£51,377.37) |
| Net margin | £6,426,481.69 |

_Cash reconciliation: of £22,617,061.76 billed, bad debt of £452,582.03 was written off, leaving £22,164,601.47 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £9,722,479.94._

| Acquisition spend | (£862.50) |
| Fixed overhead | (£5,700.00) |
| Cost to serve | (£23,293.21) |
| Operating net margin | £6,396,625.98 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £16,206.51 | £3,594.97 | £4,363.77 | £8,247.77 | £262.70 | £1,474.07 | £6,687.37 (41.3%) |
| 2017 | £347,703.10 | £111,055.46 | £112,416.49 | £124,231.15 | £7,035.15 | £8,980.02 | £113,977.55 (32.8%) |
| 2018 | £600,311.84 | £172,888.20 | £164,071.67 | £263,351.98 | £13,405.30 | £15,849.84 | £245,861.65 (41.0%) |
| 2019 | £1,642,333.62 | £496,185.23 | £443,205.99 | £702,942.41 | £34,977.00 | £38,421.15 | £662,194.86 (40.3%) |
| 2020 | £1,858,632.06 | £431,600.88 | £629,415.51 | £797,615.67 | £43,688.72 | £48,035.88 | £747,613.58 (40.2%) |
| 2021 | £2,414,227.55 | £971,905.80 | £680,933.21 | £761,388.54 | £53,573.74 | £57,233.32 | £698,552.60 (28.9%) |
| 2022 | £4,240,512.12 | £2,389,086.10 | £800,420.93 | £1,051,005.09 | £96,312.26 | £99,971.42 | £937,757.34 (22.1%) |
| 2023 | £3,479,090.27 | £1,639,053.05 | £875,932.70 | £964,104.53 | £87,181.03 | £90,839.91 | £863,228.12 (24.8%) |
| 2024 | £2,997,675.46 | £931,630.07 | £811,823.55 | £1,254,221.84 | £73,132.14 | £77,093.36 | £1,167,606.44 (39.0%) |
| 2025 | £1,284,109.47 | £452,060.81 | £270,415.77 | £561,632.89 | £43,013.99 | £44,538.77 | £511,447.23 (39.8%) |
| **Total** | **£18,880,802.00** | | | | | | **£5,954,926.74 (31.5%)** |

**Best year:** 2024 — net £1,167,606.44 (39.0% margin)
**Worst year:** 2016 — net £6,687.37 (41.3% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,421,441.22 |
| Trade Receivables | £121.74 |
| **Total Assets** | **£8,421,562.96** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,954,926.74 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £16,206.51 | +10.5% | £6,592.99 | £6,687.37 | +1.4% | GREEN |
| 2017 | £16,138.86 | £347,703.10 | +2054.4% | £7,252.29 | £113,977.55 | +1471.6% | RED |
| 2018 | £386,623.75 | £600,311.84 | +55.3% | £128,424.00 | £245,861.65 | +91.4% | RED |
| 2019 | £675,851.95 | £1,642,333.62 | +143.0% | £281,335.50 | £662,194.86 | +135.4% | RED |
| 2020 | £1,816,630.04 | £1,858,632.06 | +2.3% | £736,963.94 | £747,613.58 | +1.4% | GREEN |
| 2021 | £2,028,952.42 | £2,414,227.55 | +19.0% | £833,649.22 | £698,552.60 | -16.2% | RED |
| 2022 | £2,607,611.88 | £4,240,512.12 | +62.6% | £790,935.58 | £937,757.34 | +18.6% | RED |
| 2023 | £4,508,414.67 | £3,479,090.27 | -22.8% | £1,029,561.00 | £863,228.12 | -16.2% | RED |
| 2024 | £3,512,844.39 | £2,997,675.46 | -14.7% | £893,105.75 | £1,167,606.44 | +30.7% | RED |
| 2025 | £3,145,356.42 | £1,284,109.47 | -59.2% | £1,315,150.33 | £511,447.23 | -61.1% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,419,919.19

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
- Average CLV (Point-in-Time, year-end 2016): £10,284.38
  - By billing account: C1 £5,987.12, C5 £14,339.54, C7 £10,526.48
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
- Average CLV (Point-in-Time, year-end 2017): £11,482.97
  - By billing account: C1 £5,273.18, C2 £10,543.99, C3 £8,991.34, C4 £8,169.64, C5 £12,167.53, C6 £24,200.80, C7 £8,895.16, C8 £13,842.89, C9 £11,262.19
- Bill shock events (>=20%): 68 -- C1 2017-04-30 (21%); C1 2017-12-31 (24%); C1g 2017-05-31 (34%); C1g 2017-06-30 (36%); C1g 2017-10-31 (48%); C1g 2017-11-30 (87%); C1g 2017-12-31 (21%); C5 2017-02-28 (281%); C5 2017-04-30 (28%); C5 2017-05-31 (21%); C5 2017-06-30 (27%); C5 2017-07-31 (64%); C5 2017-08-31 (69%); C5 2017-09-30 (65%); C5 2017-10-31 (43%); C5 2017-11-30 (25%); C5 2017-12-31 (21%); C7 2017-01-31 (34%); C7 2017-02-28 (28%); C7 2017-05-31 (68%); C7 2017-06-30 (33%); C7 2017-09-30 (28%); C7 2017-10-31 (22%); C7 2017-11-30 (78%); C2g 2017-04-30 (29%); C2g 2017-05-31 (61%); C2g 2017-06-30 (54%); C2g 2017-07-31 (144%); C2g 2017-09-30 (34%); C2g 2017-10-31 (20%); C2g 2017-11-30 (108%); C2g 2017-12-31 (23%); C6 2017-05-31 (203%); C6 2017-06-30 (23%); C6 2017-07-31 (56%); C6 2017-08-31 (67%); C6 2017-09-30 (159%); C6 2017-10-31 (23%); C6 2017-12-31 (28%); C8 2017-05-31 (40%); C8 2017-06-30 (37%); C8 2017-09-30 (48%); C8 2017-10-31 (23%); C8 2017-11-30 (85%); C8 2017-12-31 (22%); C3 2017-12-31 (23%); C3g 2017-05-31 (33%); C3g 2017-06-30 (25%); C3g 2017-10-31 (24%); C3g 2017-11-30 (37%); C3g 2017-12-31 (62%); C9 2017-05-31 (33%); C9 2017-06-30 (27%); C9 2017-10-31 (23%); C9 2017-11-30 (129%); C9 2017-12-31 (42%); C4 2017-04-30 (33%); C4 2017-09-30 (28%); C4 2017-10-31 (30%); C4 2017-12-31 (45%); C4g 2017-01-31 (24%); C4g 2017-02-28 (22%); C4g 2017-05-31 (62%); C4g 2017-06-30 (50%); C4g 2017-07-31 (158%); C4g 2017-09-30 (42%); C4g 2017-10-31 (24%); C4g 2017-12-31 (75%)
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
- Bills issued: 168, average clarity 0.785, average bill shock 26.1%, bad debt provision £416.34, avg complaint probability 5.7%
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

**Year narrative:** 2017 produced a net gain of £31,527.03 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 68 customer(s) experienced a bill shock of >=20%.

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
- Average CLV (Point-in-Time, year-end 2018): £288,383.14
  - By billing account: C1 £5,231.06, C2 £8,116.09, C3 £9,006.59, C4 £6,798.71, C5 £12,344.35, C6 £20,424.84, C7 £8,038.55, C8 £10,898.61, C9 £10,640.88, C_IC1 £2,792,331.69
- Bill shock events (>=20%): 83 -- C1g 2018-04-30 (40%); C1g 2018-05-31 (33%); C1g 2018-06-30 (35%); C1g 2018-09-30 (34%); C1g 2018-10-31 (56%); C1g 2018-11-30 (31%); C5 2018-01-31 (35%); C5 2018-02-28 (29%); C5 2018-04-30 (24%); C5 2018-06-30 (39%); C5 2018-07-31 (77%); C5 2018-08-31 (76%); C5 2018-09-30 (74%); C5 2018-10-31 (51%); C7 2018-04-30 (39%); C7 2018-05-31 (40%); C7 2018-06-30 (88%); C7 2018-07-31 (313%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C2 2018-12-31 (23%); C2g 2018-04-30 (29%); C2g 2018-05-31 (37%); C2g 2018-06-30 (38%); C2g 2018-07-31 (73%); C2g 2018-08-31 (92%); C2g 2018-09-30 (92%); C2g 2018-10-31 (51%); C2g 2018-11-30 (21%); C6 2018-01-31 (37%); C6 2018-02-28 (38%); C6 2018-03-31 (36%); C6 2018-04-30 (31%); C6 2018-07-31 (51%); C6 2018-08-31 (56%); C6 2018-09-30 (46%); C6 2018-10-31 (180%); C6 2018-12-31 (29%); C8 2018-05-31 (101%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (56%); C8 2018-11-30 (30%); C3 2018-01-31 (26%); C3 2018-02-28 (26%); C3 2018-03-31 (121%); C3 2018-12-31 (21%); C3g 2018-01-31 (66%); C3g 2018-02-28 (68%); C3g 2018-03-31 (66%); C3g 2018-04-30 (68%); C3g 2018-05-31 (54%); C3g 2018-06-30 (30%); C3g 2018-08-31 (1415%); C3g 2018-09-30 (41%); C3g 2018-11-30 (42%); C3g 2018-12-31 (49%); C9 2018-01-31 (53%); C9 2018-04-30 (32%); C9 2018-05-31 (30%); C9 2018-06-30 (134%); C9 2018-07-31 (23%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-04-30 (32%); C4 2018-09-30 (29%); C4 2018-10-31 (50%); C4 2018-11-30 (33%); C4g 2018-03-31 (21%); C4g 2018-04-30 (37%); C4g 2018-05-31 (36%); C4g 2018-06-30 (151%); C4g 2018-08-31 (23%); C4g 2018-09-30 (45%); C4g 2018-10-31 (93%); C4g 2018-11-30 (26%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
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
- Bills issued: 180, average clarity 0.755, average bill shock 36.5%, bad debt provision £354.07, avg complaint probability 6.4%
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

**Year narrative:** 2018 produced a net gain of £101,695.29 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 83 customer(s) experienced a bill shock of >=20%.

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
- Average CLV (Point-in-Time, year-end 2019): £382,944.89
  - By billing account: C1 £5,209.69, C2 £8,270.81, C3 £7,728.96, C4 £6,073.23, C5 £11,192.06, C6 £19,074.59, C7 £8,373.08, C8 £9,472.90, C9 £9,974.34, C_IC1 £2,348,957.18, C_IC2 £1,778,067.01
- Bill shock events (>=20%): 76 -- C1 2019-04-30 (22%); C1g 2019-01-31 (40%); C1g 2019-02-28 (27%); C1g 2019-05-31 (26%); C1g 2019-06-30 (40%); C1g 2019-10-31 (91%); C1g 2019-11-30 (50%); C5 2019-02-28 (32%); C5 2019-04-30 (78%); C5 2019-06-30 (25%); C5 2019-07-31 (70%); C5 2019-08-31 (77%); C5 2019-09-30 (83%); C5 2019-10-31 (66%); C7 2019-01-31 (46%); C7 2019-02-28 (26%); C7 2019-05-31 (24%); C7 2019-06-30 (35%); C7 2019-10-31 (72%); C7 2019-11-30 (46%); C2g 2019-01-31 (27%); C2g 2019-02-28 (27%); C2g 2019-04-30 (37%); C2g 2019-06-30 (35%); C2g 2019-07-31 (30%); C2g 2019-09-30 (40%); C2g 2019-10-31 (76%); C2g 2019-11-30 (31%); C6 2019-01-31 (35%); C6 2019-02-28 (77%); C6 2019-04-30 (21%); C6 2019-07-31 (43%); C6 2019-08-31 (62%); C6 2019-09-30 (64%); C6 2019-10-31 (36%); C6 2019-12-31 (26%); C8 2019-01-31 (28%); C8 2019-02-28 (28%); C8 2019-04-30 (22%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-10-31 (117%); C8 2019-11-30 (38%); C3 2019-01-31 (23%); C3 2019-02-28 (24%); C3 2019-04-30 (23%); C3 2019-09-30 (152%); C3g 2019-01-31 (145%); C3g 2019-02-28 (41%); C3g 2019-04-30 (28%); C3g 2019-07-31 (37%); C3g 2019-08-31 (129%); C3g 2019-09-30 (106%); C3g 2019-10-31 (56%); C3g 2019-11-30 (44%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (68%); C9 2019-07-31 (59%); C9 2019-08-31 (139%); C9 2019-09-30 (53%); C9 2019-11-30 (87%); C4 2019-04-30 (35%); C4 2019-09-30 (33%); C4 2019-12-31 (45%); C4g 2019-01-31 (31%); C4g 2019-02-28 (25%); C4g 2019-05-31 (50%); C4g 2019-06-30 (35%); C4g 2019-07-31 (40%); C4g 2019-09-30 (36%); C4g 2019-10-31 (37%); C4g 2019-11-30 (38%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
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
- Bills issued: 204, average clarity 0.793, average bill shock 24.1%, bad debt provision £47.20, avg complaint probability 5.7%
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

**Year narrative:** 2019 produced a net gain of £234,088.53 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 76 customer(s) experienced a bill shock of >=20%.

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
- Average CLV (Point-in-Time, year-end 2020): £429,788.64
  - By billing account: C1 £4,257.86, C1_2 £16.03, C2 £6,187.77, C3 £5,529.21, C4 £6,582.41, C5 £12,943.29, C6 £19,510.54, C7 £7,742.53, C8 £9,552.17, C9 £9,057.96, C_IC1 £1,391,889.73, C_IC2 £887,578.71, C_IC3 £2,194,078.02, C_IC4 £1,462,114.75
- Bill shock events (>=20%): 74 -- C1 2020-04-30 (22%); C1g 2020-01-31 (22%); C1g 2020-04-30 (35%); C1g 2020-05-31 (22%); C1g 2020-06-30 (30%); C1g 2020-08-31 (27%); C1g 2020-10-31 (71%); C1g 2020-11-30 (20%); C1g 2020-12-29 (27%); C5 2020-01-31 (137%); C5 2020-05-31 (36%); C5 2020-06-30 (61%); C5 2020-07-31 (97%); C5 2020-08-31 (106%); C5 2020-09-30 (110%); C5 2020-10-31 (87%); C5 2020-11-30 (34%); C5 2020-12-29 (319%); C7 2020-05-31 (71%); C7 2020-06-30 (28%); C7 2020-10-31 (75%); C7 2020-11-30 (24%); C7 2020-12-31 (35%); C2 2020-04-30 (25%); C2 2020-12-31 (24%); C2g 2020-04-30 (39%); C2g 2020-05-31 (20%); C2g 2020-06-30 (29%); C2g 2020-09-30 (35%); C2g 2020-10-31 (56%); C2g 2020-12-31 (42%); C6 2020-01-31 (30%); C6 2020-02-29 (28%); C6 2020-03-31 (41%); C6 2020-04-30 (30%); C6 2020-05-31 (21%); C6 2020-06-30 (42%); C6 2020-07-31 (74%); C6 2020-08-31 (210%); C6 2020-09-30 (59%); C6 2020-10-31 (31%); C8 2020-04-30 (36%); C8 2020-05-31 (26%); C8 2020-06-30 (46%); C8 2020-07-31 (125%); C8 2020-09-30 (34%); C8 2020-10-31 (82%); C8 2020-12-31 (44%); C3 2020-01-31 (22%); C3 2020-02-29 (23%); C3 2020-04-30 (21%); C3 2020-06-29 (131%); C3g 2020-06-29 (44%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-10-31 (51%); C9 2020-12-31 (37%); C4 2020-04-30 (35%); C4 2020-05-31 (34%); C4 2020-06-30 (75%); C4 2020-09-30 (27%); C4 2020-10-31 (26%); C4 2020-11-30 (29%); C4g 2020-04-30 (36%); C4g 2020-05-31 (22%); C4g 2020-06-30 (29%); C4g 2020-10-31 (76%); C4g 2020-12-31 (38%); C_IC1 2020-03-31 (58%); C_IC1 2020-04-30 (74%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%); C_IC3g 2020-10-31 (40%)
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
- Bills issued: 205, average clarity 0.795, average bill shock 23.8%, bad debt provision £-18.26, avg complaint probability 5.5%
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

**Year narrative:** 2020 produced a net gain of £128,510.78 across 19 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 74 customer(s) experienced a bill shock of >=20%.

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
- Average CLV (Point-in-Time, year-end 2021): £408,929.65
  - By billing account: C1 £4,370.98, C1_2 £986.91, C2 £6,356.47, C3 £5,469.19, C4 £5,002.01, C5 £12,050.99, C6 £17,951.57, C7 £6,973.39, C8 £9,219.23, C9 £8,492.59, C_IC1 £1,502,450.85, C_IC2 £765,170.10, C_IC3 £2,016,503.84, C_IC4 £1,364,017.02
- Bill shock events (>=20%): 53 -- C7 2021-05-31 (30%); C7 2021-06-30 (47%); C7 2021-10-31 (55%); C7 2021-11-30 (65%); C2 2021-11-30 (21%); C2g 2021-02-28 (20%); C2g 2021-04-30 (50%); C2g 2021-05-31 (37%); C2g 2021-06-30 (58%); C2g 2021-10-31 (67%); C2g 2021-11-30 (66%); C6 2021-01-31 (32%); C6 2021-02-28 (37%); C6 2021-03-31 (24%); C6 2021-07-31 (58%); C6 2021-08-31 (62%); C6 2021-09-30 (86%); C6 2021-10-31 (28%); C6 2021-12-31 (45%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (25%); C8 2021-10-31 (69%); C8 2021-11-30 (84%); C9 2021-02-28 (22%); C9 2021-05-31 (25%); C9 2021-06-30 (51%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-11-30 (98%); C9 2021-12-31 (24%); C4 2021-04-30 (35%); C4 2021-09-30 (30%); C4 2021-10-31 (53%); C4 2021-11-30 (38%); C4g 2021-05-31 (24%); C4g 2021-06-30 (57%); C4g 2021-10-31 (132%); C4g 2021-11-30 (61%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (76%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (21%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (27%); C1_2 2021-01-31 (1202%); C1_2 2021-05-31 (34%); C1_2 2021-06-30 (58%); C1_2 2021-10-31 (85%); C1_2 2021-11-30 (80%)
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
- Bills issued: 168, average clarity 0.805, average bill shock 26.5%, bad debt provision £373.77, avg complaint probability 5.2%
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

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £75,467.55 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £338,410.43 (gross £1,049,224.77, capital £13,276.32)
  - Electricity: gross £958,836.70, capital £13,229.01, net £329,669.60
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
- Average CLV (Point-in-Time, year-end 2022): £430,517.66
  - By billing account: C1 £4,221.34, C1_2 £2,003.94, C2 £4,701.56, C3 £4,770.70, C4 £2,833.30, C5 £9,425.03, C6 £15,793.20, C7 £5,021.24, C8 £7,914.07, C9 £7,134.34, C_IC1 £1,299,467.84, C_IC2 £764,895.23, C_IC3 £2,824,425.06, C_IC4 £1,074,640.43
- Bill shock events (>=20%): 73 -- C7 2022-05-31 (61%); C7 2022-06-30 (26%); C7 2022-09-30 (32%); C7 2022-11-30 (61%); C7 2022-12-31 (55%); C2g 2022-02-28 (22%); C2g 2022-04-30 (69%); C2g 2022-05-31 (38%); C2g 2022-06-30 (31%); C2g 2022-07-31 (20%); C2g 2022-09-30 (65%); C2g 2022-11-30 (22%); C2g 2022-12-31 (113%); C6 2022-01-31 (47%); C6 2022-02-28 (117%); C6 2022-04-30 (54%); C6 2022-06-30 (39%); C6 2022-07-31 (69%); C6 2022-08-31 (85%); C6 2022-09-30 (88%); C6 2022-10-31 (50%); C6 2022-11-30 (37%); C8 2022-05-31 (39%); C8 2022-06-30 (34%); C8 2022-07-31 (21%); C8 2022-09-30 (81%); C8 2022-12-31 (110%); C9 2022-04-30 (21%); C9 2022-05-31 (29%); C9 2022-06-30 (37%); C9 2022-07-31 (94%); C9 2022-09-30 (48%); C9 2022-10-31 (30%); C9 2022-11-30 (44%); C9 2022-12-31 (52%); C4 2022-05-31 (120%); C4 2022-06-30 (59%); C4 2022-07-31 (84%); C4 2022-11-30 (36%); C4 2022-12-31 (100%); C4g 2022-01-31 (26%); C4g 2022-02-28 (24%); C4g 2022-04-30 (24%); C4g 2022-05-31 (36%); C4g 2022-06-30 (30%); C4g 2022-07-31 (25%); C4g 2022-09-30 (75%); C4g 2022-10-31 (43%); C4g 2022-11-30 (42%); C4g 2022-12-31 (147%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (109%); C_IC3g 2022-01-31 (25%); C_IC3g 2022-03-31 (33%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (50%); C_IC3g 2022-08-31 (39%); C_IC3g 2022-10-31 (50%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C1_2 2022-01-31 (100%); C1_2 2022-05-31 (21%); C1_2 2022-06-30 (152%); C1_2 2022-07-31 (157%); C1_2 2022-08-31 (172%); C1_2 2022-09-30 (298%); C1_2 2022-10-31 (21%); C1_2 2022-12-31 (42%)
- Churn risk (accounts renewing in 2022): 11 at risk (≥20% churn prob): C1_2 41%, C2 38%, C4 38%, C6 35%, C7 29%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.96-£333.14/MWh, net margin £184.51
- C2 (electricity): tariff £143.79-£457.50/MWh, net margin £2.28
- C2g (gas): tariff £35.00-£95.00/MWh, net margin £-102.36 -- **net-negative**
- C4 (electricity): tariff £143.79-£457.50/MWh, net margin £-210.57 -- **net-negative**
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
- Bills issued: 168, average clarity 0.766, average bill shock 30.4%, bad debt provision £9.26, avg complaint probability 6.4%
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

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £338,410.43 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 73 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £144,309.49 (gross £955,881.82, capital £10,036.50)
  - Electricity: gross £834,588.49, capital £9,961.08, net £135,285.94
  - Gas: gross £121,293.34, capital £75.41, net £9,023.55
- Treasury at year end: £3,382,575.78
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
- Average CLV (Point-in-Time, year-end 2023): £362,901.74
  - By billing account: C1 £3,390.74, C1_2 £1,944.13, C2 £4,662.99, C3 £4,163.83, C4 £1,814.68, C5 £7,623.31, C6 £17,306.38, C7 £5,356.78, C8 £7,277.99, C9 £6,952.69, C_IC1 £1,320,738.65, C_IC2 £640,507.44, C_IC3 £1,889,602.01, C_IC4 £1,169,282.75
- Bill shock events (>=20%): 65 -- C7 2023-01-31 (40%); C7 2023-06-30 (100%); C7 2023-07-31 (86%); C7 2023-08-31 (96%); C7 2023-10-31 (55%); C7 2023-11-30 (70%); C7 2023-12-31 (33%); C2 2023-04-30 (28%); C2g 2023-01-31 (42%); C2g 2023-04-30 (35%); C2g 2023-05-31 (40%); C2g 2023-06-30 (40%); C2g 2023-08-31 (21%); C2g 2023-10-31 (96%); C2g 2023-11-30 (60%); C6 2023-01-31 (28%); C6 2023-02-28 (24%); C6 2023-04-30 (132%); C6 2023-06-30 (45%); C6 2023-07-31 (89%); C6 2023-08-31 (90%); C6 2023-09-30 (88%); C6 2023-10-31 (83%); C6 2023-11-30 (275%); C8 2023-04-30 (30%); C8 2023-05-31 (40%); C8 2023-06-30 (43%); C8 2023-11-30 (50%); C8 2023-12-31 (104%); C9 2023-02-28 (21%); C9 2023-03-31 (24%); C9 2023-04-30 (30%); C9 2023-05-31 (33%); C9 2023-06-30 (45%); C9 2023-09-30 (21%); C9 2023-10-31 (74%); C9 2023-11-30 (53%); C4 2023-02-28 (26%); C4 2023-05-31 (91%); C4 2023-06-30 (50%); C4 2023-07-31 (74%); C4 2023-09-30 (29%); C4 2023-11-30 (32%); C4g 2023-05-31 (37%); C4g 2023-06-30 (46%); C4g 2023-10-31 (47%); C4g 2023-11-30 (67%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (59%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (101%); C_IC3g 2023-01-31 (36%); C_IC4 2023-01-31 (35%); C1_2 2023-01-31 (69%); C1_2 2023-02-28 (62%); C1_2 2023-03-31 (254%); C1_2 2023-04-30 (45%); C1_2 2023-05-31 (32%); C1_2 2023-07-31 (100%); C1_2 2023-08-31 (120%); C1_2 2023-09-30 (114%); C1_2 2023-10-31 (90%); C1_2 2023-12-31 (43%)
- Churn risk (accounts renewing in 2023): 10 at risk (≥20% churn prob): C2 41%, C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.96-£267.80/MWh, net margin £-439.82 -- **net-negative**
- C2 (electricity): tariff £208.21-£457.50/MWh, net margin £88.59
- C2g (gas): tariff £70.00-£95.00/MWh, net margin £136.46
- C4 (electricity): tariff £198.37-£457.50/MWh, net margin £-22.31 -- **net-negative**
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
- Treasury drawdown events (>=10% threshold): 47 -- £3,768,796.44 -> £3,382,501.18 (10.2%); £3,768,796.59 -> £3,382,501.18 (10.2%); £3,768,796.74 -> £3,382,501.17 (10.2%); £3,768,796.89 -> £3,382,501.17 (10.2%); £3,768,797.05 -> £3,382,501.17 (10.2%); £3,768,797.20 -> £3,382,501.17 (10.2%); £3,768,797.35 -> £3,382,501.17 (10.2%); £3,768,797.51 -> £3,382,501.17 (10.2%); £3,768,797.66 -> £3,382,501.17 (10.2%); £3,768,797.82 -> £3,382,501.17 (10.2%); £3,768,797.98 -> £3,382,501.17 (10.2%); £3,768,798.13 -> £3,382,501.17 (10.2%); £3,768,798.29 -> £3,382,501.16 (10.2%); £3,768,798.46 -> £3,382,501.16 (10.2%); £3,768,798.65 -> £3,382,501.15 (10.2%); £3,768,798.86 -> £3,382,501.15 (10.2%); £3,768,799.08 -> £3,382,501.14 (10.2%); £3,768,799.32 -> £3,382,501.13 (10.2%); £3,768,799.59 -> £3,382,501.11 (10.2%); £3,768,799.84 -> £3,382,501.10 (10.2%); £3,768,800.10 -> £3,382,501.09 (10.2%); £3,768,800.35 -> £3,382,501.08 (10.2%); £3,768,800.62 -> £3,382,501.06 (10.2%); £3,768,800.88 -> £3,382,501.05 (10.2%); £3,768,801.14 -> £3,382,501.04 (10.2%); £3,768,801.41 -> £3,382,501.02 (10.2%); £3,768,801.68 -> £3,382,501.01 (10.2%); £3,768,801.93 -> £3,382,501.00 (10.2%); £3,768,802.19 -> £3,382,500.99 (10.2%); £3,768,802.44 -> £3,382,500.98 (10.2%); £3,768,802.70 -> £3,382,500.98 (10.2%); £3,768,802.95 -> £3,382,500.97 (10.2%); £3,768,803.22 -> £3,382,500.95 (10.2%); £3,768,803.47 -> £3,382,500.93 (10.3%); £3,768,803.73 -> £3,382,500.91 (10.3%); £3,768,803.99 -> £3,382,500.89 (10.3%); £3,768,804.25 -> £3,382,500.86 (10.3%); £3,768,804.51 -> £3,382,500.83 (10.3%); £3,768,804.78 -> £3,382,500.80 (10.3%); £3,768,805.04 -> £3,382,500.77 (10.3%); £3,768,805.30 -> £3,382,500.74 (10.3%); £3,768,805.56 -> £3,382,500.71 (10.3%); £3,768,805.82 -> £3,382,500.69 (10.3%); £3,768,806.08 -> £3,382,500.68 (10.3%); £3,768,806.34 -> £3,382,500.67 (10.3%); £3,768,806.58 -> £3,382,500.66 (10.3%); £3,768,806.80 -> £3,381,802.95 (10.3%)
- Bills issued: 168, average clarity 0.766, average bill shock 28.8%, bad debt provision £2,260.04, avg complaint probability 6.3%
- Solvency signal: £307,507/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2023 produced a net gain of £144,309.49 across 14 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 65 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £347,768.66 (gross £1,257,805.74, capital £9,522.03)
  - Electricity: gross £1,132,855.54, capital £9,477.19, net £337,059.77
  - Gas: gross £124,950.20, capital £44.84, net £10,708.88
- Treasury at year end: £3,775,103.96
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.87 (avg 0.87), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C4 on 2024-09-28 period 48, net margin £-123.10

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £348,294.64
  - By billing account: C1 £3,032.53, C1_2 £2,675.04, C2 £4,104.74, C3 £3,782.52, C4 £2,320.90, C5 £7,834.04, C6 £15,341.31, C7 £4,975.97, C8 £7,062.48, C9 £7,097.09, C_IC1 £1,156,263.05, C_IC2 £680,833.29, C_IC3 £2,017,068.09, C_IC4 £963,733.92
- Bill shock events (>=20%): 49 -- C7 2024-01-31 (36%); C7 2024-02-29 (27%); C7 2024-05-31 (37%); C7 2024-09-30 (34%); C7 2024-11-30 (84%); C2 2024-04-30 (34%); C2 2024-12-31 (22%); C2g 2024-02-29 (24%); C2g 2024-04-30 (37%); C2g 2024-05-31 (47%); C2g 2024-07-31 (25%); C2g 2024-09-30 (53%); C2g 2024-10-31 (34%); C2g 2024-11-30 (52%); C6 2024-03-29 (33%); C8 2024-02-29 (23%); C8 2024-04-30 (45%); C8 2024-05-31 (27%); C8 2024-06-30 (142%); C8 2024-07-31 (65%); C8 2024-08-31 (137%); C8 2024-09-30 (72%); C8 2024-10-31 (35%); C8 2024-11-30 (61%); C9 2024-05-31 (49%); C9 2024-07-31 (30%); C9 2024-09-30 (55%); C9 2024-10-31 (23%); C9 2024-11-30 (47%); C4 2024-04-30 (33%); C4g 2024-02-29 (27%); C4g 2024-05-31 (68%); C4g 2024-07-31 (26%); C4g 2024-09-28 (51%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (63%); C_IC2 2024-06-30 (50%); C_IC2 2024-07-31 (79%); C1_2 2024-01-31 (45%); C1_2 2024-02-29 (55%); C1_2 2024-03-31 (36%); C1_2 2024-04-30 (100%); C1_2 2024-06-30 (79%); C1_2 2024-07-31 (109%); C1_2 2024-08-31 (161%); C1_2 2024-09-30 (174%); C1_2 2024-10-31 (77%); C1_2 2024-11-30 (21%); C1_2 2024-12-31 (24%)
- Churn risk (accounts renewing in 2024): 8 at risk (≥20% churn prob): C2 41%, C4 38%, C6 26%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC3 41%, C_IC4 20%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01-£267.80/MWh, net margin £760.69
- C2 (electricity): tariff £157.80-£397.50/MWh, net margin £210.04
- C2g (gas): tariff £48.30-£70.00/MWh, net margin £265.39
- C4 (electricity): tariff £198.37-£378.70/MWh, net margin £104.16
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
- Treasury drawdown events (>=10% threshold): 4271 -- £3,771,254.79 -> £3,381,803.02 (10.3%); £3,771,254.96 -> £3,381,803.06 (10.3%); £3,771,255.13 -> £3,381,803.09 (10.3%); £3,771,255.31 -> £3,381,803.13 (10.3%); £3,771,255.48 -> £3,381,803.17 (10.3%); £3,771,255.65 -> £3,381,803.20 (10.3%); £3,771,255.83 -> £3,381,803.24 (10.3%); £3,771,256.00 -> £3,381,803.28 (10.3%); £3,771,256.17 -> £3,381,803.31 (10.3%); £3,771,256.35 -> £3,381,803.35 (10.3%); £3,771,256.52 -> £3,381,803.39 (10.3%); £3,771,256.70 -> £3,381,803.57 (10.3%); £3,771,256.86 -> £3,381,803.75 (10.3%); £3,771,257.06 -> £3,381,803.95 (10.3%); £3,771,257.26 -> £3,381,804.16 (10.3%); £3,771,257.49 -> £3,381,804.40 (10.3%); £3,771,257.73 -> £3,381,804.65 (10.3%); £3,771,257.99 -> £3,381,804.93 (10.3%); £3,771,258.28 -> £3,381,805.21 (10.3%); £3,771,258.55 -> £3,381,805.33 (10.3%); £3,771,258.85 -> £3,381,805.46 (10.3%); £3,771,259.14 -> £3,381,805.58 (10.3%); £3,771,259.44 -> £3,381,805.71 (10.3%); £3,771,259.72 -> £3,381,805.83 (10.3%); £3,771,260.01 -> £3,381,805.96 (10.3%); £3,771,260.30 -> £3,381,806.08 (10.3%); £3,771,260.58 -> £3,381,806.19 (10.3%); £3,771,260.86 -> £3,381,806.30 (10.3%); £3,771,261.13 -> £3,381,806.41 (10.3%); £3,771,261.41 -> £3,381,806.53 (10.3%); £3,771,261.70 -> £3,381,806.65 (10.3%); £3,771,261.99 -> £3,381,806.76 (10.3%); £3,771,262.27 -> £3,381,807.05 (10.3%); £3,771,262.55 -> £3,381,807.30 (10.3%); £3,771,262.77 -> £3,381,807.53 (10.3%); £3,771,262.99 -> £3,381,807.74 (10.3%); £3,771,263.21 -> £3,381,807.96 (10.3%); £3,771,263.51 -> £3,381,808.16 (10.3%); £3,771,263.80 -> £3,381,808.37 (10.3%); £3,771,264.08 -> £3,381,808.58 (10.3%); £3,771,264.37 -> £3,381,808.78 (10.3%); £3,771,264.65 -> £3,381,808.97 (10.3%); £3,771,264.95 -> £3,381,809.16 (10.3%); £3,771,265.24 -> £3,381,809.21 (10.3%); £3,771,265.53 -> £3,381,809.25 (10.3%); £3,771,265.79 -> £3,381,809.29 (10.3%); £3,771,266.03 -> £3,381,809.33 (10.3%); £3,771,266.25 -> £3,381,809.37 (10.3%); £3,771,266.43 -> £3,381,809.41 (10.3%); £3,771,266.60 -> £3,381,809.45 (10.3%); £3,771,266.77 -> £3,381,809.49 (10.3%); £3,771,266.93 -> £3,381,809.53 (10.3%); £3,771,267.10 -> £3,381,809.57 (10.3%); £3,771,267.27 -> £3,381,809.61 (10.3%); £3,771,267.45 -> £3,381,809.65 (10.3%); £3,771,267.62 -> £3,381,809.69 (10.3%); £3,771,267.79 -> £3,381,809.73 (10.3%); £3,771,267.96 -> £3,381,809.77 (10.3%); £3,771,268.13 -> £3,381,809.81 (10.3%); £3,771,268.30 -> £3,381,809.97 (10.3%); £3,771,268.47 -> £3,381,810.14 (10.3%); £3,771,268.65 -> £3,381,810.31 (10.3%); £3,771,268.86 -> £3,381,810.50 (10.3%); £3,771,269.08 -> £3,381,810.72 (10.3%); £3,771,269.32 -> £3,381,810.95 (10.3%); £3,771,269.57 -> £3,381,811.22 (10.3%); £3,771,269.85 -> £3,381,811.49 (10.3%); £3,771,270.13 -> £3,381,811.63 (10.3%); £3,771,270.41 -> £3,381,811.75 (10.3%); £3,771,270.69 -> £3,381,811.87 (10.3%); £3,771,270.98 -> £3,381,812.01 (10.3%); £3,771,271.25 -> £3,381,812.14 (10.3%); £3,771,271.53 -> £3,381,812.25 (10.3%); £3,771,271.81 -> £3,381,812.37 (10.3%); £3,771,272.09 -> £3,381,812.49 (10.3%); £3,771,272.37 -> £3,381,812.60 (10.3%); £3,771,272.64 -> £3,381,812.71 (10.3%); £3,771,272.92 -> £3,381,812.82 (10.3%); £3,771,273.19 -> £3,381,812.93 (10.3%); £3,771,273.47 -> £3,381,813.04 (10.3%); £3,771,273.68 -> £3,381,813.28 (10.3%); £3,771,273.90 -> £3,381,813.51 (10.3%); £3,771,274.11 -> £3,381,813.71 (10.3%); £3,771,274.32 -> £3,381,813.89 (10.3%); £3,771,274.54 -> £3,381,814.06 (10.3%); £3,771,274.75 -> £3,381,814.23 (10.3%); £3,771,274.96 -> £3,381,814.39 (10.3%); £3,771,275.24 -> £3,381,814.55 (10.3%); £3,771,275.53 -> £3,381,814.72 (10.3%); £3,771,275.80 -> £3,381,814.88 (10.3%); £3,771,276.09 -> £3,381,815.04 (10.3%); £3,771,276.37 -> £3,381,815.08 (10.3%); £3,771,276.65 -> £3,381,815.12 (10.3%); £3,771,276.92 -> £3,381,815.16 (10.3%); £3,771,277.15 -> £3,381,815.20 (10.3%); £3,771,277.37 -> £3,381,815.23 (10.3%); £3,771,277.54 -> £3,381,815.27 (10.3%); £3,771,277.71 -> £3,381,815.31 (10.3%); £3,771,277.88 -> £3,381,815.34 (10.3%); £3,771,278.05 -> £3,381,815.38 (10.3%); £3,771,278.22 -> £3,381,815.42 (10.3%); £3,771,278.39 -> £3,381,815.45 (10.3%); £3,771,278.56 -> £3,381,815.49 (10.3%); £3,771,278.72 -> £3,381,815.53 (10.3%); £3,771,278.89 -> £3,381,815.57 (10.3%); £3,771,279.06 -> £3,381,815.60 (10.3%); £3,771,279.23 -> £3,381,815.65 (10.3%); £3,771,279.41 -> £3,381,815.83 (10.3%); £3,771,279.58 -> £3,381,816.02 (10.3%); £3,771,279.76 -> £3,381,816.22 (10.3%); £3,771,279.97 -> £3,381,816.44 (10.3%); £3,771,280.20 -> £3,381,816.68 (10.3%); £3,771,280.44 -> £3,381,816.92 (10.3%); £3,771,280.71 -> £3,381,817.18 (10.3%); £3,771,280.99 -> £3,381,817.45 (10.3%); £3,771,281.27 -> £3,381,817.57 (10.3%); £3,771,281.55 -> £3,381,817.69 (10.3%); £3,771,281.83 -> £3,381,817.82 (10.3%); £3,771,282.12 -> £3,381,817.94 (10.3%); £3,771,282.41 -> £3,381,818.06 (10.3%); £3,771,282.70 -> £3,381,818.18 (10.3%); £3,771,282.99 -> £3,381,818.29 (10.3%); £3,771,283.27 -> £3,381,818.41 (10.3%); £3,771,283.55 -> £3,381,818.53 (10.3%); £3,771,283.83 -> £3,381,818.65 (10.3%); £3,771,284.12 -> £3,381,818.76 (10.3%); £3,771,284.39 -> £3,381,818.88 (10.3%); £3,771,284.67 -> £3,381,818.99 (10.3%); £3,771,284.95 -> £3,381,819.25 (10.3%); £3,771,285.17 -> £3,381,819.52 (10.3%); £3,771,285.45 -> £3,381,819.74 (10.3%); £3,771,285.66 -> £3,381,819.94 (10.3%); £3,771,285.87 -> £3,381,820.13 (10.3%); £3,771,286.08 -> £3,381,820.31 (10.3%); £3,771,286.30 -> £3,381,820.51 (10.3%); £3,771,286.57 -> £3,381,820.70 (10.3%); £3,771,286.85 -> £3,381,820.89 (10.3%); £3,771,287.14 -> £3,381,821.07 (10.3%); £3,771,287.41 -> £3,381,821.24 (10.3%); £3,771,287.70 -> £3,381,821.28 (10.3%); £3,771,287.99 -> £3,381,821.32 (10.3%); £3,771,288.24 -> £3,381,821.36 (10.3%); £3,771,288.48 -> £3,381,821.39 (10.3%); £3,771,288.70 -> £3,381,821.43 (10.3%); £3,771,288.86 -> £3,381,821.47 (10.3%); £3,771,289.03 -> £3,381,821.51 (10.3%); £3,771,289.19 -> £3,381,821.55 (10.3%); £3,771,289.36 -> £3,381,821.58 (10.3%); £3,771,289.53 -> £3,381,821.62 (10.3%); £3,771,289.70 -> £3,381,821.66 (10.3%); £3,771,289.87 -> £3,381,821.70 (10.3%); £3,771,290.03 -> £3,381,821.74 (10.3%); £3,771,290.20 -> £3,381,821.78 (10.3%); £3,771,290.37 -> £3,381,821.81 (10.3%); £3,771,290.54 -> £3,381,821.85 (10.3%); £3,771,290.71 -> £3,381,822.06 (10.3%); £3,771,290.88 -> £3,381,822.27 (10.3%); £3,771,291.07 -> £3,381,822.49 (10.3%); £3,771,291.27 -> £3,381,822.72 (10.3%); £3,771,291.49 -> £3,381,822.96 (10.3%); £3,771,291.73 -> £3,381,823.24 (10.3%); £3,771,291.99 -> £3,381,823.54 (10.3%); £3,771,292.27 -> £3,381,823.85 (10.3%); £3,771,292.54 -> £3,381,823.98 (10.3%); £3,771,292.83 -> £3,381,824.10 (10.3%); £3,771,293.10 -> £3,381,824.23 (10.3%); £3,771,293.38 -> £3,381,824.36 (10.3%); £3,771,293.66 -> £3,381,824.48 (10.3%); £3,771,293.93 -> £3,381,824.60 (10.3%); £3,771,294.21 -> £3,381,824.71 (10.3%); £3,771,294.49 -> £3,381,824.82 (10.3%); £3,771,294.77 -> £3,381,824.93 (10.3%); £3,771,295.04 -> £3,381,825.05 (10.3%); £3,771,295.32 -> £3,381,825.16 (10.3%); £3,771,295.60 -> £3,381,825.27 (10.3%); £3,771,295.88 -> £3,381,825.37 (10.3%); £3,771,296.09 -> £3,381,825.67 (10.3%); £3,771,296.36 -> £3,381,825.95 (10.3%); £3,771,296.64 -> £3,381,826.18 (10.3%); £3,771,296.84 -> £3,381,826.40 (10.3%); £3,771,297.11 -> £3,381,826.62 (10.3%); £3,771,297.39 -> £3,381,826.82 (10.3%); £3,771,297.61 -> £3,381,827.02 (10.3%); £3,771,297.89 -> £3,381,827.22 (10.3%); £3,771,298.16 -> £3,381,827.42 (10.3%); £3,771,298.45 -> £3,381,827.61 (10.3%); £3,771,298.72 -> £3,381,827.81 (10.3%); £3,771,299.01 -> £3,381,827.85 (10.3%); £3,771,299.28 -> £3,381,827.89 (10.3%); £3,771,299.53 -> £3,381,827.93 (10.3%); £3,771,299.77 -> £3,381,827.96 (10.3%); £3,771,299.99 -> £3,381,828.00 (10.3%); £3,771,300.15 -> £3,381,828.04 (10.3%); £3,771,300.31 -> £3,381,828.07 (10.3%); £3,771,300.47 -> £3,381,828.11 (10.3%); £3,771,300.63 -> £3,381,828.15 (10.3%); £3,771,300.79 -> £3,381,828.19 (10.3%); £3,771,300.95 -> £3,381,828.22 (10.3%); £3,771,301.12 -> £3,381,828.26 (10.3%); £3,771,301.27 -> £3,381,828.30 (10.3%); £3,771,301.44 -> £3,381,828.34 (10.3%); £3,771,301.61 -> £3,381,828.38 (10.3%); £3,771,301.77 -> £3,381,828.42 (10.3%); £3,771,301.93 -> £3,381,828.64 (10.3%); £3,771,302.09 -> £3,381,828.85 (10.3%); £3,771,302.27 -> £3,381,829.10 (10.3%); £3,771,302.47 -> £3,381,829.35 (10.3%); £3,771,302.68 -> £3,381,829.62 (10.3%); £3,771,302.91 -> £3,381,829.90 (10.3%); £3,771,303.17 -> £3,381,830.20 (10.3%); £3,771,303.44 -> £3,381,830.51 (10.3%); £3,771,303.72 -> £3,381,830.63 (10.3%); £3,771,303.98 -> £3,381,830.76 (10.3%); £3,771,304.25 -> £3,381,830.88 (10.3%); £3,771,304.52 -> £3,381,831.01 (10.3%); £3,771,304.79 -> £3,381,831.14 (10.3%); £3,771,305.06 -> £3,381,831.26 (10.3%); £3,771,305.34 -> £3,381,831.38 (10.3%); £3,771,305.61 -> £3,381,831.50 (10.3%); £3,771,305.87 -> £3,381,831.61 (10.3%); £3,771,306.13 -> £3,381,831.73 (10.3%); £3,771,306.40 -> £3,381,831.84 (10.3%); £3,771,306.66 -> £3,381,831.95 (10.3%); £3,771,306.94 -> £3,381,832.05 (10.3%); £3,771,307.14 -> £3,381,832.35 (10.3%); £3,771,307.34 -> £3,381,832.62 (10.3%); £3,771,307.55 -> £3,381,832.88 (10.3%); £3,771,307.75 -> £3,381,833.12 (10.3%); £3,771,308.02 -> £3,381,833.34 (10.3%); £3,771,308.22 -> £3,381,833.56 (10.3%); £3,771,308.42 -> £3,381,833.78 (10.3%); £3,771,308.69 -> £3,381,833.99 (10.3%); £3,771,308.96 -> £3,381,834.20 (10.3%); £3,771,309.22 -> £3,381,834.42 (10.3%); £3,771,309.49 -> £3,381,834.63 (10.3%); £3,771,309.75 -> £3,381,834.67 (10.3%); £3,771,310.02 -> £3,381,834.71 (10.3%); £3,771,310.28 -> £3,381,834.75 (10.3%); £3,771,310.51 -> £3,381,834.79 (10.3%); £3,771,310.72 -> £3,381,834.83 (10.3%); £3,771,310.86 -> £3,381,834.86 (10.3%); £3,771,311.01 -> £3,381,834.90 (10.3%); £3,771,311.15 -> £3,381,834.94 (10.3%); £3,771,311.30 -> £3,381,834.98 (10.3%); £3,771,311.44 -> £3,381,835.02 (10.3%); £3,771,311.59 -> £3,381,835.05 (10.3%); £3,771,311.72 -> £3,381,835.09 (10.3%); £3,771,311.86 -> £3,381,835.13 (10.3%); £3,771,312.00 -> £3,381,835.16 (10.3%); £3,771,312.14 -> £3,381,835.20 (10.3%); £3,771,312.28 -> £3,381,835.24 (10.3%); £3,771,312.42 -> £3,381,835.50 (10.3%); £3,771,312.56 -> £3,381,835.75 (10.3%); £3,771,312.72 -> £3,381,836.02 (10.3%); £3,771,312.89 -> £3,381,836.29 (10.3%); £3,771,313.08 -> £3,381,836.56 (10.3%); £3,771,313.29 -> £3,381,836.85 (10.3%); £3,771,313.50 -> £3,381,837.17 (10.3%); £3,771,313.74 -> £3,381,837.49 (10.3%); £3,771,313.97 -> £3,381,837.58 (10.3%); £3,771,314.21 -> £3,381,837.66 (10.3%); £3,771,314.44 -> £3,381,837.75 (10.3%); £3,771,314.68 -> £3,381,837.84 (10.3%); £3,771,314.91 -> £3,381,837.92 (10.3%); £3,771,315.15 -> £3,381,838.00 (10.3%); £3,771,315.38 -> £3,381,838.07 (10.3%); £3,771,315.63 -> £3,381,838.15 (10.3%); £3,771,315.87 -> £3,381,838.21 (10.3%); £3,771,316.11 -> £3,381,838.28 (10.3%); £3,771,316.35 -> £3,381,838.35 (10.3%); £3,771,316.58 -> £3,381,838.41 (10.3%); £3,771,316.83 -> £3,381,838.48 (10.3%); £3,771,317.05 -> £3,381,838.75 (10.3%); £3,771,317.22 -> £3,381,839.01 (10.3%); £3,771,317.40 -> £3,381,839.27 (10.3%); £3,771,317.57 -> £3,381,839.51 (10.3%); £3,771,317.75 -> £3,381,839.76 (10.3%); £3,771,317.93 -> £3,381,840.00 (10.3%); £3,771,318.11 -> £3,381,840.26 (10.3%); £3,771,318.34 -> £3,381,840.51 (10.3%); £3,771,318.57 -> £3,381,840.76 (10.3%); £3,771,318.80 -> £3,381,841.00 (10.3%); £3,771,319.04 -> £3,381,841.25 (10.3%); £3,771,319.27 -> £3,381,841.29 (10.3%); £3,771,319.50 -> £3,381,841.33 (10.3%); £3,771,319.72 -> £3,381,841.37 (10.3%); £3,771,319.92 -> £3,381,841.41 (10.3%); £3,771,320.10 -> £3,381,841.45 (10.3%); £3,771,320.24 -> £3,381,841.48 (10.3%); £3,771,320.38 -> £3,381,841.52 (10.3%); £3,771,320.53 -> £3,381,841.56 (10.3%); £3,771,320.67 -> £3,381,841.60 (10.3%); £3,771,320.80 -> £3,381,841.63 (10.3%); £3,771,320.94 -> £3,381,841.67 (10.3%); £3,771,321.08 -> £3,381,841.70 (10.3%); £3,771,321.23 -> £3,381,841.74 (10.3%); £3,771,321.36 -> £3,381,841.78 (10.3%); £3,771,321.50 -> £3,381,841.81 (10.3%); £3,771,321.64 -> £3,381,841.85 (10.3%); £3,771,321.78 -> £3,381,842.10 (10.3%); £3,771,321.92 -> £3,381,842.34 (10.3%); £3,771,322.07 -> £3,381,842.59 (10.3%); £3,771,322.25 -> £3,381,842.83 (10.3%); £3,771,322.44 -> £3,381,843.08 (10.3%); £3,771,322.64 -> £3,381,843.33 (10.3%); £3,771,322.86 -> £3,381,843.57 (10.3%); £3,771,323.09 -> £3,381,843.82 (10.3%); £3,771,323.34 -> £3,381,843.87 (10.3%); £3,771,323.56 -> £3,381,843.91 (10.3%); £3,771,323.79 -> £3,381,843.96 (10.3%); £3,771,324.02 -> £3,381,844.01 (10.3%); £3,771,324.25 -> £3,381,844.06 (10.3%); £3,771,324.48 -> £3,381,844.11 (10.3%); £3,771,324.71 -> £3,381,844.15 (10.3%); £3,771,324.94 -> £3,381,844.19 (10.3%); £3,771,325.17 -> £3,381,844.24 (10.3%); £3,771,325.41 -> £3,381,844.29 (10.3%); £3,771,325.64 -> £3,381,844.33 (10.3%); £3,771,325.87 -> £3,381,844.37 (10.3%); £3,771,326.10 -> £3,381,844.42 (10.3%); £3,771,326.28 -> £3,381,844.65 (10.3%); £3,771,326.45 -> £3,381,844.88 (10.3%); £3,771,326.62 -> £3,381,845.12 (10.3%); £3,771,326.79 -> £3,381,845.37 (10.3%); £3,771,327.03 -> £3,381,845.61 (10.3%); £3,771,327.21 -> £3,381,845.84 (10.3%); £3,771,327.38 -> £3,381,846.09 (10.3%); £3,771,327.62 -> £3,381,846.34 (10.3%); £3,771,327.85 -> £3,381,846.58 (10.3%); £3,771,328.09 -> £3,381,846.81 (10.3%); £3,771,328.32 -> £3,381,847.05 (10.3%); £3,771,328.54 -> £3,381,847.09 (10.3%); £3,771,328.78 -> £3,381,847.13 (10.3%); £3,771,328.99 -> £3,381,847.17 (10.3%); £3,771,329.19 -> £3,381,847.20 (10.3%); £3,771,329.38 -> £3,381,847.24 (10.3%); £3,771,329.54 -> £3,381,847.28 (10.3%); £3,771,329.69 -> £3,381,847.31 (10.3%); £3,771,329.84 -> £3,381,847.35 (10.3%); £3,771,329.99 -> £3,381,847.39 (10.3%); £3,771,330.14 -> £3,381,847.43 (10.3%); £3,771,330.30 -> £3,381,847.46 (10.3%); £3,771,330.45 -> £3,381,847.50 (10.3%); £3,771,330.61 -> £3,381,847.54 (10.3%); £3,771,330.76 -> £3,381,847.58 (10.3%); £3,771,330.92 -> £3,381,847.61 (10.3%); £3,771,331.07 -> £3,381,847.66 (10.3%); £3,771,331.22 -> £3,381,847.89 (10.3%); £3,771,331.38 -> £3,381,848.15 (10.3%); £3,771,331.55 -> £3,381,848.41 (10.3%); £3,771,331.73 -> £3,381,848.67 (10.3%); £3,771,331.94 -> £3,381,848.97 (10.3%); £3,771,332.16 -> £3,381,849.29 (10.3%); £3,771,332.39 -> £3,381,849.63 (10.3%); £3,771,332.64 -> £3,381,849.99 (10.3%); £3,771,332.89 -> £3,381,850.10 (10.3%); £3,771,333.14 -> £3,381,850.22 (10.3%); £3,771,333.41 -> £3,381,850.34 (10.3%); £3,771,333.65 -> £3,381,850.47 (10.3%); £3,771,333.91 -> £3,381,850.59 (10.3%); £3,771,334.17 -> £3,381,850.70 (10.3%); £3,771,334.43 -> £3,381,850.82 (10.3%); £3,771,334.70 -> £3,381,850.94 (10.3%); £3,771,334.95 -> £3,381,851.05 (10.3%); £3,771,335.20 -> £3,381,851.16 (10.3%); £3,771,335.47 -> £3,381,851.27 (10.3%); £3,771,335.72 -> £3,381,851.38 (10.3%); £3,771,335.98 -> £3,381,851.49 (10.3%); £3,771,336.25 -> £3,381,851.83 (10.3%); £3,771,336.51 -> £3,381,852.15 (10.3%); £3,771,336.76 -> £3,381,852.44 (10.3%); £3,771,337.01 -> £3,381,852.71 (10.3%); £3,771,337.26 -> £3,381,852.98 (10.3%); £3,771,337.51 -> £3,381,853.23 (10.3%); £3,771,337.70 -> £3,381,853.48 (10.3%); £3,771,337.95 -> £3,381,853.73 (10.3%); £3,771,338.20 -> £3,381,853.98 (10.3%); £3,771,338.45 -> £3,381,854.22 (10.3%); £3,771,338.71 -> £3,381,854.46 (10.3%); £3,771,338.96 -> £3,381,854.50 (10.3%); £3,771,339.22 -> £3,381,854.55 (10.3%); £3,771,339.45 -> £3,381,854.59 (10.3%); £3,771,339.67 -> £3,381,854.62 (10.3%); £3,771,339.87 -> £3,381,854.66 (10.3%); £3,771,340.02 -> £3,381,854.70 (10.3%); £3,771,340.18 -> £3,381,854.74 (10.3%); £3,771,340.33 -> £3,381,854.77 (10.3%); £3,771,340.48 -> £3,381,854.81 (10.3%); £3,771,340.64 -> £3,381,854.85 (10.3%); £3,771,340.79 -> £3,381,854.89 (10.3%); £3,771,340.94 -> £3,381,854.92 (10.3%); £3,771,341.09 -> £3,381,854.96 (10.3%); £3,771,341.25 -> £3,381,855.00 (10.3%); £3,771,341.40 -> £3,381,855.04 (10.3%); £3,771,341.55 -> £3,381,855.08 (10.3%); £3,771,341.71 -> £3,381,855.32 (10.3%); £3,771,341.86 -> £3,381,855.57 (10.3%); £3,771,342.02 -> £3,381,855.83 (10.3%); £3,771,342.20 -> £3,381,856.10 (10.3%); £3,771,342.41 -> £3,381,856.39 (10.3%); £3,771,342.63 -> £3,381,856.70 (10.3%); £3,771,342.86 -> £3,381,857.04 (10.3%); £3,771,343.11 -> £3,381,857.39 (10.3%); £3,771,343.36 -> £3,381,857.51 (10.3%); £3,771,343.61 -> £3,381,857.64 (10.3%); £3,771,343.87 -> £3,381,857.77 (10.3%); £3,771,344.12 -> £3,381,857.90 (10.3%); £3,771,344.39 -> £3,381,858.03 (10.3%); £3,771,344.65 -> £3,381,858.15 (10.3%); £3,771,344.90 -> £3,381,858.27 (10.3%); £3,771,345.16 -> £3,381,858.38 (10.3%); £3,771,345.41 -> £3,381,858.50 (10.3%); £3,771,345.67 -> £3,381,858.62 (10.3%); £3,771,345.93 -> £3,381,858.73 (10.3%); £3,771,346.18 -> £3,381,858.84 (10.3%); £3,771,346.42 -> £3,381,858.95 (10.3%); £3,771,346.61 -> £3,381,859.26 (10.3%); £3,771,346.80 -> £3,381,859.58 (10.3%); £3,771,347.05 -> £3,381,859.85 (10.3%); £3,771,347.24 -> £3,381,860.10 (10.3%); £3,771,347.43 -> £3,381,860.36 (10.3%); £3,771,347.69 -> £3,381,860.61 (10.3%); £3,771,347.94 -> £3,381,860.86 (10.3%); £3,771,348.20 -> £3,381,861.11 (10.3%); £3,771,348.45 -> £3,381,861.35 (10.3%); £3,771,348.71 -> £3,381,861.58 (10.3%); £3,771,348.97 -> £3,381,861.82 (10.3%); £3,771,349.22 -> £3,381,861.86 (10.3%); £3,771,349.47 -> £3,381,861.90 (10.3%); £3,771,349.71 -> £3,381,861.94 (10.3%); £3,771,349.92 -> £3,381,861.98 (10.3%); £3,771,350.12 -> £3,381,862.01 (10.3%); £3,771,350.27 -> £3,381,862.05 (10.3%); £3,771,350.42 -> £3,381,862.09 (10.3%); £3,771,350.57 -> £3,381,862.13 (10.3%); £3,771,350.73 -> £3,381,862.16 (10.3%); £3,771,350.87 -> £3,381,862.20 (10.3%); £3,771,351.03 -> £3,381,862.24 (10.3%); £3,771,351.18 -> £3,381,862.28 (10.3%); £3,771,351.33 -> £3,381,862.31 (10.3%); £3,771,351.48 -> £3,381,862.35 (10.3%); £3,771,351.63 -> £3,381,862.39 (10.3%); £3,771,351.78 -> £3,381,862.43 (10.3%); £3,771,351.93 -> £3,381,862.65 (10.3%); £3,771,352.09 -> £3,381,862.86 (10.3%); £3,771,352.25 -> £3,381,863.07 (10.3%); £3,771,352.44 -> £3,381,863.30 (10.3%); £3,771,352.63 -> £3,381,863.55 (10.3%); £3,771,352.85 -> £3,381,863.82 (10.3%); £3,771,353.10 -> £3,381,864.12 (10.3%); £3,771,353.34 -> £3,381,864.42 (10.3%); £3,771,353.60 -> £3,381,864.54 (10.3%); £3,771,353.84 -> £3,381,864.66 (10.3%); £3,771,354.10 -> £3,381,864.79 (10.3%); £3,771,354.35 -> £3,381,864.91 (10.3%); £3,771,354.60 -> £3,381,865.03 (10.3%); £3,771,354.85 -> £3,381,865.15 (10.3%); £3,771,355.12 -> £3,381,865.27 (10.3%); £3,771,355.37 -> £3,381,865.38 (10.3%); £3,771,355.62 -> £3,381,865.49 (10.3%); £3,771,355.88 -> £3,381,865.60 (10.3%); £3,771,356.13 -> £3,381,865.71 (10.3%); £3,771,356.38 -> £3,381,865.82 (10.3%); £3,771,356.62 -> £3,381,865.93 (10.3%); £3,771,356.88 -> £3,381,866.22 (10.3%); £3,771,357.06 -> £3,381,866.51 (10.3%); £3,771,357.32 -> £3,381,866.78 (10.3%); £3,771,357.57 -> £3,381,867.00 (10.3%); £3,771,357.77 -> £3,381,867.24 (10.3%); £3,771,358.01 -> £3,381,867.45 (10.3%); £3,771,358.19 -> £3,381,867.67 (10.3%); £3,771,358.45 -> £3,381,867.89 (10.3%); £3,771,358.70 -> £3,381,868.11 (10.3%); £3,771,358.95 -> £3,381,868.33 (10.3%); £3,771,359.20 -> £3,381,868.54 (10.3%); £3,771,359.45 -> £3,381,868.58 (10.3%); £3,771,359.69 -> £3,381,868.62 (10.3%); £3,771,359.93 -> £3,381,868.66 (10.3%); £3,771,360.14 -> £3,381,868.70 (10.3%); £3,771,360.33 -> £3,381,868.73 (10.3%); £3,771,360.49 -> £3,381,868.77 (10.3%); £3,771,360.64 -> £3,381,868.81 (10.3%); £3,771,360.78 -> £3,381,868.85 (10.3%); £3,771,360.94 -> £3,381,868.88 (10.3%); £3,771,361.08 -> £3,381,868.92 (10.3%); £3,771,361.24 -> £3,381,868.96 (10.3%); £3,771,361.39 -> £3,381,869.00 (10.3%); £3,771,361.54 -> £3,381,869.03 (10.3%); £3,771,361.69 -> £3,381,869.07 (10.3%); £3,771,361.83 -> £3,381,869.11 (10.3%); £3,771,361.99 -> £3,381,869.15 (10.3%); £3,771,362.14 -> £3,381,869.35 (10.3%); £3,771,362.28 -> £3,381,869.55 (10.3%); £3,771,362.45 -> £3,381,869.75 (10.3%); £3,771,362.63 -> £3,381,869.96 (10.3%); £3,771,362.83 -> £3,381,870.20 (10.3%); £3,771,363.04 -> £3,381,870.45 (10.3%); £3,771,363.27 -> £3,381,870.74 (10.3%); £3,771,363.52 -> £3,381,871.02 (10.3%); £3,771,363.78 -> £3,381,871.14 (10.3%); £3,771,364.02 -> £3,381,871.26 (10.3%); £3,771,364.27 -> £3,381,871.38 (10.3%); £3,771,364.53 -> £3,381,871.50 (10.3%); £3,771,364.77 -> £3,381,871.62 (10.3%); £3,771,365.02 -> £3,381,871.74 (10.3%); £3,771,365.26 -> £3,381,871.86 (10.3%); £3,771,365.50 -> £3,381,871.98 (10.3%); £3,771,365.75 -> £3,381,872.09 (10.3%); £3,771,366.00 -> £3,381,872.20 (10.3%); £3,771,366.25 -> £3,381,872.32 (10.3%); £3,771,366.50 -> £3,381,872.43 (10.3%); £3,771,366.75 -> £3,381,872.53 (10.3%); £3,771,366.94 -> £3,381,872.81 (10.3%); £3,771,367.12 -> £3,381,873.07 (10.3%); £3,771,367.31 -> £3,381,873.31 (10.3%); £3,771,367.49 -> £3,381,873.52 (10.3%); £3,771,367.68 -> £3,381,873.73 (10.3%); £3,771,367.86 -> £3,381,873.94 (10.3%); £3,771,368.04 -> £3,381,874.14 (10.3%); £3,771,368.29 -> £3,381,874.34 (10.3%); £3,771,368.54 -> £3,381,874.54 (10.3%); £3,771,368.80 -> £3,381,874.73 (10.3%); £3,771,369.04 -> £3,381,874.92 (10.3%); £3,771,369.29 -> £3,381,874.96 (10.3%); £3,771,369.54 -> £3,381,875.01 (10.3%); £3,771,369.77 -> £3,381,875.05 (10.3%); £3,771,369.98 -> £3,381,875.08 (10.3%); £3,771,370.17 -> £3,381,875.12 (10.3%); £3,771,370.32 -> £3,381,875.16 (10.3%); £3,771,370.47 -> £3,381,875.19 (10.3%); £3,771,370.62 -> £3,381,875.23 (10.3%); £3,771,370.76 -> £3,381,875.27 (10.3%); £3,771,370.91 -> £3,381,875.30 (10.3%); £3,771,371.06 -> £3,381,875.34 (10.3%); £3,771,371.21 -> £3,381,875.38 (10.3%); £3,771,371.35 -> £3,381,875.41 (10.3%); £3,771,371.50 -> £3,381,875.45 (10.3%); £3,771,371.65 -> £3,381,875.49 (10.3%); £3,771,371.80 -> £3,381,875.53 (10.3%); £3,771,371.94 -> £3,381,875.74 (10.3%); £3,771,372.10 -> £3,381,875.96 (10.3%); £3,771,372.26 -> £3,381,876.19 (10.3%); £3,771,372.44 -> £3,381,876.43 (10.3%); £3,771,372.64 -> £3,381,876.68 (10.3%); £3,771,372.85 -> £3,381,876.96 (10.3%); £3,771,373.08 -> £3,381,877.26 (10.3%); £3,771,373.33 -> £3,381,877.56 (10.3%); £3,771,373.56 -> £3,381,877.69 (10.3%); £3,771,373.80 -> £3,381,877.81 (10.3%); £3,771,374.05 -> £3,381,877.93 (10.3%); £3,771,374.30 -> £3,381,878.05 (10.3%); £3,771,374.54 -> £3,381,878.17 (10.3%); £3,771,374.80 -> £3,381,878.29 (10.3%); £3,771,375.04 -> £3,381,878.40 (10.3%); £3,771,375.28 -> £3,381,878.51 (10.3%); £3,771,375.52 -> £3,381,878.62 (10.3%); £3,771,375.76 -> £3,381,878.73 (10.3%); £3,771,376.01 -> £3,381,878.84 (10.3%); £3,771,376.25 -> £3,381,878.95 (10.3%); £3,771,376.49 -> £3,381,879.05 (10.3%); £3,771,376.68 -> £3,381,879.34 (10.3%); £3,771,376.86 -> £3,381,879.62 (10.3%); £3,771,377.05 -> £3,381,879.87 (10.3%); £3,771,377.23 -> £3,381,880.10 (10.3%); £3,771,377.41 -> £3,381,880.33 (10.3%); £3,771,377.59 -> £3,381,880.56 (10.3%); £3,771,377.78 -> £3,381,880.78 (10.3%); £3,771,378.02 -> £3,381,880.99 (10.3%); £3,771,378.27 -> £3,381,881.21 (10.3%); £3,771,378.52 -> £3,381,881.42 (10.3%); £3,771,378.76 -> £3,381,881.63 (10.3%); £3,771,379.01 -> £3,381,881.67 (10.3%); £3,771,379.26 -> £3,381,881.71 (10.3%); £3,771,379.49 -> £3,381,881.75 (10.3%); £3,771,379.70 -> £3,381,881.79 (10.3%); £3,771,379.90 -> £3,381,881.82 (10.3%); £3,771,380.02 -> £3,381,881.86 (10.3%); £3,771,380.15 -> £3,381,881.90 (10.3%); £3,771,380.28 -> £3,381,881.94 (10.3%); £3,771,380.41 -> £3,381,881.97 (10.3%); £3,771,380.54 -> £3,381,882.01 (10.3%); £3,771,380.67 -> £3,381,882.05 (10.3%); £3,771,380.80 -> £3,381,882.08 (10.3%); £3,771,380.93 -> £3,381,882.12 (10.3%); £3,771,381.05 -> £3,381,882.16 (10.3%); £3,771,381.18 -> £3,381,882.19 (10.3%); £3,771,381.31 -> £3,381,882.23 (10.3%); £3,771,381.44 -> £3,381,882.43 (10.3%); £3,771,381.57 -> £3,381,882.64 (10.3%); £3,771,381.71 -> £3,381,882.85 (10.3%); £3,771,381.87 -> £3,381,883.05 (10.3%); £3,771,382.04 -> £3,381,883.28 (10.3%); £3,771,382.22 -> £3,381,883.51 (10.3%); £3,771,382.42 -> £3,381,883.76 (10.3%); £3,771,382.63 -> £3,381,884.02 (10.3%); £3,771,382.84 -> £3,381,884.11 (10.3%); £3,771,383.05 -> £3,381,884.20 (10.3%); £3,771,383.26 -> £3,381,884.29 (10.3%); £3,771,383.47 -> £3,381,884.38 (10.3%); £3,771,383.68 -> £3,381,884.46 (10.3%); £3,771,383.90 -> £3,381,884.54 (10.3%); £3,771,384.11 -> £3,381,884.61 (10.3%); £3,771,384.32 -> £3,381,884.68 (10.3%); £3,771,384.54 -> £3,381,884.75 (10.3%); £3,771,384.75 -> £3,381,884.82 (10.3%); £3,771,384.96 -> £3,381,884.89 (10.3%); £3,771,385.17 -> £3,381,884.96 (10.3%); £3,771,385.39 -> £3,381,885.02 (10.3%); £3,771,385.55 -> £3,381,885.25 (10.3%); £3,771,385.71 -> £3,381,885.47 (10.3%); £3,771,385.87 -> £3,381,885.68 (10.3%); £3,771,386.03 -> £3,381,885.88 (10.3%); £3,771,386.19 -> £3,381,886.09 (10.3%); £3,771,386.34 -> £3,381,886.30 (10.3%); £3,771,386.55 -> £3,381,886.51 (10.3%); £3,771,386.77 -> £3,381,886.70 (10.3%); £3,771,386.99 -> £3,381,886.91 (10.3%); £3,771,387.20 -> £3,381,887.11 (10.3%); £3,771,387.41 -> £3,381,887.31 (10.3%); £3,771,387.62 -> £3,381,887.35 (10.3%); £3,771,387.84 -> £3,381,887.39 (10.3%); £3,771,388.03 -> £3,381,887.43 (10.3%); £3,771,388.21 -> £3,381,887.47 (10.3%); £3,771,388.37 -> £3,381,887.51 (10.3%); £3,771,388.50 -> £3,381,887.55 (10.3%); £3,771,388.63 -> £3,381,887.58 (10.3%); £3,771,388.75 -> £3,381,887.62 (10.3%); £3,771,388.87 -> £3,381,887.66 (10.3%); £3,771,389.00 -> £3,381,887.69 (10.3%); £3,771,389.13 -> £3,381,887.73 (10.3%); £3,771,389.25 -> £3,381,887.77 (10.3%); £3,771,389.38 -> £3,381,887.80 (10.3%); £3,771,389.51 -> £3,381,887.84 (10.3%); £3,771,389.64 -> £3,381,887.87 (10.3%); £3,771,389.76 -> £3,381,887.91 (10.3%); £3,771,389.89 -> £3,381,888.15 (10.3%); £3,771,390.01 -> £3,381,888.40 (10.3%); £3,771,390.16 -> £3,381,888.64 (10.3%); £3,771,390.31 -> £3,381,888.89 (10.3%); £3,771,390.48 -> £3,381,889.13 (10.3%); £3,771,390.67 -> £3,381,889.38 (10.3%); £3,771,390.87 -> £3,381,889.62 (10.3%); £3,771,391.07 -> £3,381,889.87 (10.3%); £3,771,391.29 -> £3,381,889.91 (10.3%); £3,771,391.49 -> £3,381,889.96 (10.3%); £3,771,391.70 -> £3,381,890.01 (10.3%); £3,771,391.92 -> £3,381,890.06 (10.3%); £3,771,392.13 -> £3,381,890.11 (10.3%); £3,771,392.34 -> £3,381,890.15 (10.3%); £3,771,392.55 -> £3,381,890.20 (10.3%); £3,771,392.76 -> £3,381,890.25 (10.3%); £3,771,392.98 -> £3,381,890.29 (10.3%); £3,771,393.18 -> £3,381,890.34 (10.3%); £3,771,393.39 -> £3,381,890.38 (10.3%); £3,771,393.60 -> £3,381,890.43 (10.3%); £3,771,393.81 -> £3,381,890.47 (10.3%); £3,771,393.97 -> £3,381,890.71 (10.3%); £3,771,394.13 -> £3,381,890.94 (10.3%); £3,771,394.30 -> £3,381,891.17 (10.3%); £3,771,394.45 -> £3,381,891.41 (10.3%); £3,771,394.61 -> £3,381,891.65 (10.3%); £3,771,394.78 -> £3,381,891.89 (10.3%); £3,771,394.93 -> £3,381,892.12 (10.3%); £3,771,395.15 -> £3,381,892.35 (10.3%); £3,771,395.37 -> £3,381,892.60 (10.3%); £3,771,395.57 -> £3,381,892.84 (10.3%); £3,771,395.78 -> £3,381,893.08 (10.3%); £3,771,395.99 -> £3,381,893.12 (10.3%); £3,771,396.20 -> £3,381,893.16 (10.3%); £3,771,396.40 -> £3,381,893.19 (10.3%); £3,771,396.58 -> £3,381,893.23 (10.3%); £3,771,396.75 -> £3,381,893.26 (10.3%); £3,771,396.90 -> £3,381,893.30 (10.3%); £3,771,397.04 -> £3,381,893.34 (10.3%); £3,771,397.19 -> £3,381,893.38 (10.3%); £3,771,397.34 -> £3,381,893.41 (10.3%); £3,771,397.48 -> £3,381,893.45 (10.3%); £3,771,397.63 -> £3,381,893.49 (10.3%); £3,771,397.77 -> £3,381,893.52 (10.3%); £3,771,397.92 -> £3,381,893.56 (10.3%); £3,771,398.07 -> £3,381,893.60 (10.3%); £3,771,398.21 -> £3,381,893.64 (10.3%); £3,771,398.35 -> £3,381,893.68 (10.3%); £3,771,398.49 -> £3,381,893.96 (10.3%); £3,771,398.64 -> £3,381,894.25 (10.3%); £3,771,398.80 -> £3,381,894.55 (10.3%); £3,771,398.98 -> £3,381,894.87 (10.3%); £3,771,399.16 -> £3,381,895.20 (10.3%); £3,771,399.37 -> £3,381,895.55 (10.3%); £3,771,399.59 -> £3,381,895.92 (10.3%); £3,771,399.83 -> £3,381,896.31 (10.3%); £3,771,400.07 -> £3,381,896.43 (10.3%); £3,771,400.32 -> £3,381,896.56 (10.3%); £3,771,400.56 -> £3,381,896.69 (10.3%); £3,771,400.81 -> £3,381,896.82 (10.3%); £3,771,401.05 -> £3,381,896.94 (10.3%); £3,771,401.29 -> £3,381,897.07 (10.3%); £3,771,401.53 -> £3,381,897.19 (10.3%); £3,771,401.77 -> £3,381,897.30 (10.3%); £3,771,402.01 -> £3,381,897.42 (10.3%); £3,771,402.26 -> £3,381,897.53 (10.3%); £3,771,402.50 -> £3,381,897.64 (10.3%); £3,771,402.74 -> £3,381,897.75 (10.3%); £3,771,402.98 -> £3,381,897.86 (10.3%); £3,771,403.17 -> £3,381,898.22 (10.3%); £3,771,403.35 -> £3,381,898.56 (10.3%); £3,771,403.54 -> £3,381,898.87 (10.3%); £3,771,403.72 -> £3,381,899.17 (10.3%); £3,771,403.90 -> £3,381,899.46 (10.3%); £3,771,404.08 -> £3,381,899.74 (10.3%); £3,771,404.25 -> £3,381,900.04 (10.3%); £3,771,404.50 -> £3,381,900.32 (10.3%); £3,771,404.73 -> £3,381,900.61 (10.3%); £3,771,404.97 -> £3,381,900.89 (10.3%); £3,771,405.21 -> £3,381,901.17 (10.3%); £3,771,405.46 -> £3,381,901.22 (10.3%); £3,771,405.70 -> £3,381,901.26 (10.3%); £3,771,405.92 -> £3,381,901.30 (10.3%); £3,771,406.13 -> £3,381,901.33 (10.3%); £3,771,406.32 -> £3,381,901.37 (10.3%); £3,771,406.46 -> £3,381,901.41 (10.3%); £3,771,406.61 -> £3,381,901.44 (10.3%); £3,771,406.75 -> £3,381,901.48 (10.3%); £3,771,406.89 -> £3,381,901.52 (10.3%); £3,771,407.03 -> £3,381,901.55 (10.3%); £3,771,407.17 -> £3,381,901.59 (10.3%); £3,771,407.31 -> £3,381,901.63 (10.3%); £3,771,407.45 -> £3,381,901.67 (10.3%); £3,771,407.60 -> £3,381,901.70 (10.3%); £3,771,407.74 -> £3,381,901.74 (10.3%); £3,771,407.89 -> £3,381,901.78 (10.3%); £3,771,408.03 -> £3,381,902.05 (10.3%); £3,771,408.18 -> £3,381,902.31 (10.3%); £3,771,408.34 -> £3,381,902.58 (10.3%); £3,771,408.52 -> £3,381,902.85 (10.3%); £3,771,408.70 -> £3,381,903.14 (10.3%); £3,771,408.92 -> £3,381,903.46 (10.3%); £3,771,409.14 -> £3,381,903.80 (10.3%); £3,771,409.39 -> £3,381,904.15 (10.3%); £3,771,409.63 -> £3,381,904.27 (10.3%); £3,771,409.86 -> £3,381,904.39 (10.3%); £3,771,410.10 -> £3,381,904.51 (10.3%); £3,771,410.34 -> £3,381,904.64 (10.3%); £3,771,410.57 -> £3,381,904.77 (10.3%); £3,771,410.82 -> £3,381,904.89 (10.3%); £3,771,411.05 -> £3,381,905.01 (10.3%); £3,771,411.28 -> £3,381,905.13 (10.3%); £3,771,411.52 -> £3,381,905.24 (10.3%); £3,771,411.76 -> £3,381,905.35 (10.3%); £3,771,411.99 -> £3,381,905.46 (10.3%); £3,771,412.23 -> £3,381,905.57 (10.3%); £3,771,412.47 -> £3,381,905.68 (10.3%); £3,771,412.65 -> £3,381,906.02 (10.3%); £3,771,412.83 -> £3,381,906.35 (10.3%); £3,771,413.02 -> £3,381,906.66 (10.3%); £3,771,413.27 -> £3,381,906.95 (10.3%); £3,771,413.51 -> £3,381,907.23 (10.3%); £3,771,413.76 -> £3,381,907.50 (10.3%); £3,771,413.94 -> £3,381,907.76 (10.3%); £3,771,414.18 -> £3,381,908.02 (10.3%); £3,771,414.42 -> £3,381,908.28 (10.3%); £3,771,414.66 -> £3,381,908.53 (10.3%); £3,771,414.90 -> £3,381,908.77 (10.3%); £3,771,415.15 -> £3,381,908.81 (10.3%); £3,771,415.39 -> £3,381,908.85 (10.3%); £3,771,415.61 -> £3,381,908.89 (10.3%); £3,771,415.81 -> £3,381,908.93 (10.3%); £3,771,415.99 -> £3,381,908.97 (10.3%); £3,771,416.14 -> £3,381,909.00 (10.3%); £3,771,416.28 -> £3,381,909.04 (10.3%); £3,771,416.41 -> £3,381,909.08 (10.3%); £3,771,416.55 -> £3,381,909.12 (10.3%); £3,771,416.69 -> £3,381,909.16 (10.3%); £3,771,416.84 -> £3,381,909.19 (10.3%); £3,771,416.98 -> £3,381,909.23 (10.3%); £3,771,417.12 -> £3,381,909.27 (10.3%); £3,771,417.27 -> £3,381,909.31 (10.3%); £3,771,417.41 -> £3,381,909.35 (10.3%); £3,771,417.55 -> £3,381,909.39 (10.3%); £3,771,417.69 -> £3,381,909.67 (10.3%); £3,771,417.83 -> £3,381,909.95 (10.3%); £3,771,417.98 -> £3,381,910.25 (10.3%); £3,771,418.16 -> £3,381,910.56 (10.3%); £3,771,418.35 -> £3,381,910.88 (10.3%); £3,771,418.55 -> £3,381,911.23 (10.3%); £3,771,418.77 -> £3,381,911.61 (10.3%); £3,771,419.01 -> £3,381,912.00 (10.3%); £3,771,419.25 -> £3,381,912.12 (10.3%); £3,771,419.48 -> £3,381,912.25 (10.3%); £3,771,419.72 -> £3,381,912.37 (10.3%); £3,771,419.96 -> £3,381,912.50 (10.3%); £3,771,420.19 -> £3,381,912.62 (10.3%); £3,771,420.43 -> £3,381,912.74 (10.3%); £3,771,420.67 -> £3,381,912.85 (10.3%); £3,771,420.90 -> £3,381,912.97 (10.3%); £3,771,421.14 -> £3,381,913.08 (10.3%); £3,771,421.38 -> £3,381,913.20 (10.3%); £3,771,421.63 -> £3,381,913.31 (10.3%); £3,771,421.86 -> £3,381,913.41 (10.3%); £3,771,422.10 -> £3,381,913.52 (10.3%); £3,771,422.27 -> £3,381,913.87 (10.3%); £3,771,422.45 -> £3,381,914.22 (10.3%); £3,771,422.69 -> £3,381,914.54 (10.3%); £3,771,422.93 -> £3,381,914.85 (10.3%); £3,771,423.17 -> £3,381,915.14 (10.3%); £3,771,423.40 -> £3,381,915.43 (10.3%); £3,771,423.65 -> £3,381,915.71 (10.3%); £3,771,423.89 -> £3,381,916.00 (10.3%); £3,771,424.13 -> £3,381,916.27 (10.3%); £3,771,424.36 -> £3,381,916.54 (10.3%); £3,771,424.60 -> £3,381,916.79 (10.3%); £3,771,424.83 -> £3,381,916.83 (10.3%); £3,771,425.06 -> £3,381,916.87 (10.3%); £3,771,425.27 -> £3,381,916.91 (10.3%); £3,771,425.47 -> £3,381,916.95 (10.3%); £3,771,425.65 -> £3,381,916.99 (10.3%); £3,771,425.79 -> £3,381,917.03 (10.3%); £3,771,425.93 -> £3,381,917.06 (10.3%); £3,771,426.08 -> £3,381,917.10 (10.3%); £3,771,426.22 -> £3,381,917.14 (10.3%); £3,771,426.36 -> £3,381,917.18 (10.3%); £3,771,426.50 -> £3,381,917.21 (10.3%); £3,771,426.64 -> £3,381,917.25 (10.3%); £3,771,426.78 -> £3,381,917.28 (10.3%); £3,771,426.93 -> £3,381,917.32 (10.3%); £3,771,427.07 -> £3,381,917.36 (10.3%); £3,771,427.22 -> £3,381,917.40 (10.3%); £3,771,427.36 -> £3,381,917.70 (10.3%); £3,771,427.50 -> £3,381,918.01 (10.3%); £3,771,427.66 -> £3,381,918.32 (10.3%); £3,771,427.83 -> £3,381,918.65 (10.3%); £3,771,428.02 -> £3,381,919.00 (10.3%); £3,771,428.23 -> £3,381,919.36 (10.3%); £3,771,428.45 -> £3,381,919.75 (10.3%); £3,771,428.68 -> £3,381,920.15 (10.3%); £3,771,428.91 -> £3,381,920.28 (10.3%); £3,771,429.15 -> £3,381,920.40 (10.3%); £3,771,429.38 -> £3,381,920.53 (10.3%); £3,771,429.61 -> £3,381,920.65 (10.3%); £3,771,429.83 -> £3,381,920.78 (10.3%); £3,771,430.08 -> £3,381,920.90 (10.3%); £3,771,430.32 -> £3,381,921.01 (10.3%); £3,771,430.56 -> £3,381,921.12 (10.3%); £3,771,430.79 -> £3,381,921.24 (10.3%); £3,771,431.03 -> £3,381,921.36 (10.3%); £3,771,431.26 -> £3,381,921.47 (10.3%); £3,771,431.50 -> £3,381,921.58 (10.3%); £3,771,431.74 -> £3,381,921.69 (10.3%); £3,771,431.92 -> £3,381,922.08 (10.3%); £3,771,432.10 -> £3,381,922.45 (10.3%); £3,771,432.27 -> £3,381,922.79 (10.3%); £3,771,432.44 -> £3,381,923.11 (10.3%); £3,771,432.63 -> £3,381,923.43 (10.3%); £3,771,432.80 -> £3,381,923.74 (10.3%); £3,771,432.98 -> £3,381,924.04 (10.3%); £3,771,433.21 -> £3,381,924.34 (10.3%); £3,771,433.44 -> £3,381,924.64 (10.3%); £3,771,433.68 -> £3,381,924.94 (10.3%); £3,771,433.90 -> £3,381,925.24 (10.3%); £3,771,434.14 -> £3,381,925.28 (10.3%); £3,771,434.38 -> £3,381,925.33 (10.3%); £3,771,434.60 -> £3,381,925.37 (10.3%); £3,771,434.81 -> £3,381,925.40 (10.3%); £3,771,435.00 -> £3,381,925.44 (10.3%); £3,771,435.14 -> £3,381,925.48 (10.3%); £3,771,435.28 -> £3,381,925.52 (10.3%); £3,771,435.43 -> £3,381,925.55 (10.3%); £3,771,435.57 -> £3,381,925.59 (10.3%); £3,771,435.71 -> £3,381,925.63 (10.3%); £3,771,435.86 -> £3,381,925.67 (10.3%); £3,771,436.00 -> £3,381,925.70 (10.3%); £3,771,436.15 -> £3,381,925.74 (10.3%); £3,771,436.28 -> £3,381,925.78 (10.3%); £3,771,436.43 -> £3,381,925.82 (10.3%); £3,771,436.58 -> £3,381,925.86 (10.3%); £3,771,436.72 -> £3,381,926.12 (10.3%); £3,771,436.86 -> £3,381,926.39 (10.3%); £3,771,437.02 -> £3,381,926.66 (10.3%); £3,771,437.20 -> £3,381,926.95 (10.3%); £3,771,437.39 -> £3,381,927.26 (10.3%); £3,771,437.59 -> £3,381,927.59 (10.3%); £3,771,437.81 -> £3,381,927.94 (10.3%); £3,771,438.05 -> £3,381,928.30 (10.3%); £3,771,438.28 -> £3,381,928.42 (10.3%); £3,771,438.52 -> £3,381,928.55 (10.3%); £3,771,438.75 -> £3,381,928.67 (10.3%); £3,771,438.99 -> £3,381,928.80 (10.3%); £3,771,439.24 -> £3,381,928.93 (10.3%); £3,771,439.48 -> £3,381,929.05 (10.3%); £3,771,439.72 -> £3,381,929.17 (10.3%); £3,771,439.95 -> £3,381,929.29 (10.3%); £3,771,440.18 -> £3,381,929.41 (10.3%); £3,771,440.42 -> £3,381,929.52 (10.3%); £3,771,440.66 -> £3,381,929.64 (10.3%); £3,771,440.90 -> £3,381,929.75 (10.3%); £3,771,441.14 -> £3,381,929.86 (10.3%); £3,771,441.37 -> £3,381,930.20 (10.3%); £3,771,441.55 -> £3,381,930.53 (10.3%); £3,771,441.72 -> £3,381,930.83 (10.3%); £3,771,441.91 -> £3,381,931.12 (10.3%); £3,771,442.08 -> £3,381,931.40 (10.3%); £3,771,442.33 -> £3,381,931.67 (10.3%); £3,771,442.57 -> £3,381,931.94 (10.3%); £3,771,442.82 -> £3,381,932.21 (10.3%); £3,771,443.06 -> £3,381,932.48 (10.3%); £3,771,443.30 -> £3,381,932.73 (10.3%); £3,771,443.54 -> £3,381,932.98 (10.3%); £3,771,443.79 -> £3,381,933.03 (10.3%); £3,771,444.03 -> £3,381,933.07 (10.3%); £3,771,444.25 -> £3,381,933.11 (10.3%); £3,771,444.45 -> £3,381,933.14 (10.3%); £3,771,444.64 -> £3,381,933.18 (10.3%); £3,771,444.77 -> £3,381,933.22 (10.3%); £3,771,444.90 -> £3,381,933.25 (10.3%); £3,771,445.02 -> £3,381,933.29 (10.3%); £3,771,445.15 -> £3,381,933.33 (10.3%); £3,771,445.28 -> £3,381,933.37 (10.3%); £3,771,445.41 -> £3,381,933.40 (10.3%); £3,771,445.54 -> £3,381,933.44 (10.3%); £3,771,445.67 -> £3,381,933.48 (10.3%); £3,771,445.79 -> £3,381,933.52 (10.3%); £3,771,445.92 -> £3,381,933.55 (10.3%); £3,771,446.05 -> £3,381,933.59 (10.3%); £3,771,446.18 -> £3,381,933.80 (10.3%); £3,771,446.31 -> £3,381,934.00 (10.3%); £3,771,446.45 -> £3,381,934.22 (10.3%); £3,771,446.61 -> £3,381,934.43 (10.3%); £3,771,446.78 -> £3,381,934.66 (10.3%); £3,771,446.97 -> £3,381,934.90 (10.3%); £3,771,447.18 -> £3,381,935.16 (10.3%); £3,771,447.39 -> £3,381,935.43 (10.3%); £3,771,447.60 -> £3,381,935.51 (10.3%); £3,771,447.82 -> £3,381,935.60 (10.3%); £3,771,448.03 -> £3,381,935.69 (10.3%); £3,771,448.24 -> £3,381,935.78 (10.3%); £3,771,448.46 -> £3,381,935.86 (10.3%); £3,771,448.67 -> £3,381,935.94 (10.3%); £3,771,448.88 -> £3,381,936.02 (10.3%); £3,771,449.10 -> £3,381,936.09 (10.3%); £3,771,449.32 -> £3,381,936.16 (10.3%); £3,771,449.53 -> £3,381,936.23 (10.3%); £3,771,449.74 -> £3,381,936.30 (10.3%); £3,771,449.95 -> £3,381,936.36 (10.3%); £3,771,450.17 -> £3,381,936.43 (10.3%); £3,771,450.33 -> £3,381,936.67 (10.3%); £3,771,450.50 -> £3,381,936.90 (10.3%); £3,771,450.66 -> £3,381,937.12 (10.3%); £3,771,450.82 -> £3,381,937.33 (10.3%); £3,771,450.98 -> £3,381,937.54 (10.3%); £3,771,451.15 -> £3,381,937.75 (10.3%); £3,771,451.31 -> £3,381,937.96 (10.3%); £3,771,451.52 -> £3,381,938.16 (10.3%); £3,771,451.74 -> £3,381,938.37 (10.3%); £3,771,451.95 -> £3,381,938.57 (10.3%); £3,771,452.17 -> £3,381,938.78 (10.3%); £3,771,452.38 -> £3,381,938.82 (10.3%); £3,771,452.59 -> £3,381,938.86 (10.3%); £3,771,452.80 -> £3,381,938.89 (10.3%); £3,771,452.98 -> £3,381,938.93 (10.3%); £3,771,453.14 -> £3,381,938.97 (10.3%); £3,771,453.27 -> £3,381,939.01 (10.3%); £3,771,453.40 -> £3,381,939.05 (10.3%); £3,771,453.53 -> £3,381,939.08 (10.3%); £3,771,453.66 -> £3,381,939.12 (10.3%); £3,771,453.79 -> £3,381,939.16 (10.3%); £3,771,453.92 -> £3,381,939.19 (10.3%); £3,771,454.05 -> £3,381,939.23 (10.3%); £3,771,454.17 -> £3,381,939.26 (10.3%); £3,771,454.30 -> £3,381,939.30 (10.3%); £3,771,454.43 -> £3,381,939.33 (10.3%); £3,771,454.56 -> £3,381,939.37 (10.3%); £3,771,454.69 -> £3,381,939.51 (10.3%); £3,771,454.82 -> £3,381,939.65 (10.3%); £3,771,454.96 -> £3,381,939.79 (10.3%); £3,771,455.12 -> £3,381,939.93 (10.3%); £3,771,455.29 -> £3,381,940.08 (10.3%); £3,771,455.48 -> £3,381,940.22 (10.3%); £3,771,455.68 -> £3,381,940.37 (10.3%); £3,771,455.90 -> £3,381,940.52 (10.3%); £3,771,456.12 -> £3,381,940.57 (10.3%); £3,771,456.33 -> £3,381,940.62 (10.3%); £3,771,456.55 -> £3,381,940.67 (10.3%); £3,771,456.76 -> £3,381,940.71 (10.3%); £3,771,456.97 -> £3,381,940.76 (10.3%); £3,771,457.19 -> £3,381,940.81 (10.3%); £3,771,457.40 -> £3,381,940.86 (10.3%); £3,771,457.62 -> £3,381,940.90 (10.3%); £3,771,457.83 -> £3,381,940.95 (10.3%); £3,771,458.04 -> £3,381,940.99 (10.3%); £3,771,458.26 -> £3,381,941.04 (10.3%); £3,771,458.48 -> £3,381,941.08 (10.3%); £3,771,458.70 -> £3,381,941.13 (10.3%); £3,771,458.86 -> £3,381,941.28 (10.3%); £3,771,459.02 -> £3,381,941.42 (10.3%); £3,771,459.18 -> £3,381,941.57 (10.3%); £3,771,459.33 -> £3,381,941.72 (10.3%); £3,771,459.49 -> £3,381,941.87 (10.3%); £3,771,459.66 -> £3,381,942.01 (10.3%); £3,771,459.81 -> £3,381,942.16 (10.3%); £3,771,460.03 -> £3,381,942.30 (10.3%); £3,771,460.24 -> £3,381,942.45 (10.3%); £3,771,460.47 -> £3,381,942.59 (10.3%); £3,771,460.68 -> £3,381,942.72 (10.3%); £3,771,460.89 -> £3,381,942.76 (10.3%); £3,771,461.11 -> £3,381,942.80 (10.3%); £3,771,461.30 -> £3,381,942.84 (10.3%); £3,771,461.48 -> £3,381,942.87 (10.3%); £3,771,461.64 -> £3,381,942.91 (10.3%); £3,771,461.79 -> £3,381,942.95 (10.3%); £3,771,461.94 -> £3,381,942.99 (10.3%); £3,771,462.08 -> £3,381,943.02 (10.3%); £3,771,462.23 -> £3,381,943.06 (10.3%); £3,771,462.37 -> £3,381,943.10 (10.3%); £3,771,462.52 -> £3,381,943.13 (10.3%); £3,771,462.67 -> £3,381,943.17 (10.3%); £3,771,462.82 -> £3,381,943.21 (10.3%); £3,771,462.96 -> £3,381,943.24 (10.3%); £3,771,463.10 -> £3,381,943.28 (10.3%); £3,771,463.25 -> £3,381,943.32 (10.3%); £3,771,463.40 -> £3,381,943.49 (10.3%); £3,771,463.54 -> £3,381,943.66 (10.3%); £3,771,463.70 -> £3,381,943.84 (10.3%); £3,771,463.88 -> £3,381,944.03 (10.3%); £3,771,464.08 -> £3,381,944.24 (10.3%); £3,771,464.30 -> £3,381,944.47 (10.3%); £3,771,464.53 -> £3,381,944.72 (10.3%); £3,771,464.78 -> £3,381,944.99 (10.3%); £3,771,465.03 -> £3,381,945.11 (10.3%); £3,771,465.27 -> £3,381,945.24 (10.3%); £3,771,465.53 -> £3,381,945.37 (10.3%); £3,771,465.76 -> £3,381,945.49 (10.3%); £3,771,466.01 -> £3,381,945.62 (10.3%); £3,771,466.27 -> £3,381,945.74 (10.3%); £3,771,466.51 -> £3,381,945.85 (10.3%); £3,771,466.76 -> £3,381,945.97 (10.3%); £3,771,467.02 -> £3,381,946.09 (10.3%); £3,771,467.26 -> £3,381,946.21 (10.3%); £3,771,467.51 -> £3,381,946.33 (10.3%); £3,771,467.76 -> £3,381,946.44 (10.3%); £3,771,468.01 -> £3,381,946.55 (10.3%); £3,771,468.25 -> £3,381,946.82 (10.3%); £3,771,468.44 -> £3,381,947.05 (10.3%); £3,771,468.62 -> £3,381,947.27 (10.3%); £3,771,468.81 -> £3,381,947.46 (10.3%); £3,771,468.98 -> £3,381,947.64 (10.3%); £3,771,469.17 -> £3,381,947.82 (10.3%); £3,771,469.35 -> £3,381,948.01 (10.3%); £3,771,469.59 -> £3,381,948.18 (10.3%); £3,771,469.83 -> £3,381,948.35 (10.3%); £3,771,470.08 -> £3,381,948.52 (10.3%); £3,771,470.33 -> £3,381,948.69 (10.3%); £3,771,470.57 -> £3,381,948.73 (10.3%); £3,771,470.82 -> £3,381,948.77 (10.3%); £3,771,471.05 -> £3,381,948.81 (10.3%); £3,771,471.26 -> £3,381,948.85 (10.3%); £3,771,471.45 -> £3,381,948.89 (10.3%); £3,771,471.60 -> £3,381,948.92 (10.3%); £3,771,471.75 -> £3,381,948.96 (10.3%); £3,771,471.89 -> £3,381,949.00 (10.3%); £3,771,472.03 -> £3,381,949.04 (10.3%); £3,771,472.19 -> £3,381,949.08 (10.3%); £3,771,472.33 -> £3,381,949.12 (10.3%); £3,771,472.48 -> £3,381,949.16 (10.3%); £3,771,472.63 -> £3,381,949.20 (10.3%); £3,771,472.78 -> £3,381,949.23 (10.3%); £3,771,472.92 -> £3,381,949.27 (10.3%); £3,771,473.07 -> £3,381,949.31 (10.3%); £3,771,473.22 -> £3,381,949.47 (10.3%); £3,771,473.37 -> £3,381,949.62 (10.3%); £3,771,473.54 -> £3,381,949.80 (10.3%); £3,771,473.72 -> £3,381,949.98 (10.3%); £3,771,473.92 -> £3,381,950.18 (10.3%); £3,771,474.13 -> £3,381,950.41 (10.3%); £3,771,474.36 -> £3,381,950.65 (10.3%); £3,771,474.61 -> £3,381,950.90 (10.3%); £3,771,474.86 -> £3,381,951.03 (10.3%); £3,771,475.10 -> £3,381,951.16 (10.3%); £3,771,475.35 -> £3,381,951.29 (10.3%); £3,771,475.59 -> £3,381,951.42 (10.3%); £3,771,475.85 -> £3,381,951.55 (10.3%); £3,771,476.09 -> £3,381,951.67 (10.3%); £3,771,476.34 -> £3,381,951.79 (10.3%); £3,771,476.58 -> £3,381,951.91 (10.3%); £3,771,476.83 -> £3,381,952.02 (10.3%); £3,771,477.07 -> £3,381,952.14 (10.3%); £3,771,477.31 -> £3,381,952.26 (10.3%); £3,771,477.56 -> £3,381,952.37 (10.3%); £3,771,477.81 -> £3,381,952.48 (10.3%); £3,771,477.99 -> £3,381,952.73 (10.3%); £3,771,478.18 -> £3,381,952.97 (10.3%); £3,771,478.44 -> £3,381,953.17 (10.3%); £3,771,478.68 -> £3,381,953.36 (10.3%); £3,771,478.92 -> £3,381,953.54 (10.3%); £3,771,479.17 -> £3,381,953.71 (10.3%); £3,771,479.36 -> £3,381,953.88 (10.3%); £3,771,479.61 -> £3,381,954.04 (10.3%); £3,771,479.86 -> £3,381,954.21 (10.3%); £3,771,480.11 -> £3,381,954.36 (10.3%); £3,771,480.36 -> £3,381,954.51 (10.3%); £3,771,480.61 -> £3,381,954.55 (10.3%); £3,771,480.86 -> £3,381,954.60 (10.3%); £3,771,481.09 -> £3,381,954.64 (10.3%); £3,771,481.29 -> £3,381,954.67 (10.3%); £3,771,481.49 -> £3,381,954.71 (10.3%); £3,771,481.63 -> £3,381,954.75 (10.3%); £3,771,481.78 -> £3,381,954.79 (10.3%); £3,771,481.93 -> £3,381,954.83 (10.3%); £3,771,482.08 -> £3,381,954.87 (10.3%); £3,771,482.23 -> £3,381,954.91 (10.3%); £3,771,482.37 -> £3,381,954.94 (10.3%); £3,771,482.52 -> £3,381,954.98 (10.3%); £3,771,482.67 -> £3,381,955.02 (10.3%); £3,771,482.82 -> £3,381,955.06 (10.3%); £3,771,482.97 -> £3,381,955.10 (10.3%); £3,771,483.12 -> £3,381,955.14 (10.3%); £3,771,483.28 -> £3,381,955.30 (10.3%); £3,771,483.43 -> £3,381,955.46 (10.3%); £3,771,483.60 -> £3,381,955.63 (10.3%); £3,771,483.78 -> £3,381,955.82 (10.3%); £3,771,483.98 -> £3,381,956.03 (10.3%); £3,771,484.19 -> £3,381,956.25 (10.3%); £3,771,484.43 -> £3,381,956.51 (10.3%); £3,771,484.67 -> £3,381,956.77 (10.3%); £3,771,484.93 -> £3,381,956.90 (10.3%); £3,771,485.18 -> £3,381,957.03 (10.3%); £3,771,485.43 -> £3,381,957.16 (10.3%); £3,771,485.68 -> £3,381,957.29 (10.3%); £3,771,485.93 -> £3,381,957.42 (10.3%); £3,771,486.18 -> £3,381,957.54 (10.3%); £3,771,486.43 -> £3,381,957.66 (10.3%); £3,771,486.69 -> £3,381,957.78 (10.3%); £3,771,486.95 -> £3,381,957.90 (10.3%); £3,771,487.20 -> £3,381,958.02 (10.3%); £3,771,487.46 -> £3,381,958.14 (10.3%); £3,771,487.71 -> £3,381,958.26 (10.3%); £3,771,487.96 -> £3,381,958.38 (10.3%); £3,771,488.21 -> £3,381,958.63 (10.3%); £3,771,488.39 -> £3,381,958.87 (10.3%); £3,771,488.58 -> £3,381,959.09 (10.3%); £3,771,488.83 -> £3,381,959.28 (10.3%); £3,771,489.08 -> £3,381,959.47 (10.3%); £3,771,489.34 -> £3,381,959.65 (10.3%); £3,771,489.53 -> £3,381,959.83 (10.3%); £3,771,489.78 -> £3,381,960.01 (10.3%); £3,771,490.04 -> £3,381,960.18 (10.3%); £3,771,490.29 -> £3,381,960.35 (10.3%); £3,771,490.54 -> £3,381,960.51 (10.3%); £3,771,490.79 -> £3,381,960.55 (10.3%); £3,771,491.04 -> £3,381,960.59 (10.3%); £3,771,491.28 -> £3,381,960.63 (10.3%); £3,771,491.49 -> £3,381,960.67 (10.3%); £3,771,491.69 -> £3,381,960.70 (10.3%); £3,771,491.84 -> £3,381,960.74 (10.3%); £3,771,491.99 -> £3,381,960.78 (10.3%); £3,771,492.15 -> £3,381,960.82 (10.3%); £3,771,492.31 -> £3,381,960.86 (10.3%); £3,771,492.46 -> £3,381,960.89 (10.3%); £3,771,492.62 -> £3,381,960.93 (10.3%); £3,771,492.77 -> £3,381,960.97 (10.3%); £3,771,492.93 -> £3,381,961.01 (10.3%); £3,771,493.08 -> £3,381,961.04 (10.3%); £3,771,493.23 -> £3,381,961.08 (10.3%); £3,771,493.39 -> £3,381,961.12 (10.3%); £3,771,493.54 -> £3,381,961.27 (10.3%); £3,771,493.70 -> £3,381,961.42 (10.3%); £3,771,493.86 -> £3,381,961.58 (10.3%); £3,771,494.05 -> £3,381,961.76 (10.3%); £3,771,494.26 -> £3,381,961.96 (10.3%); £3,771,494.47 -> £3,381,962.17 (10.3%); £3,771,494.71 -> £3,381,962.42 (10.3%); £3,771,494.96 -> £3,381,962.68 (10.3%); £3,771,495.22 -> £3,381,962.80 (10.3%); £3,771,495.47 -> £3,381,962.93 (10.3%); £3,771,495.72 -> £3,381,963.06 (10.3%); £3,771,495.98 -> £3,381,963.19 (10.3%); £3,771,496.23 -> £3,381,963.32 (10.3%); £3,771,496.49 -> £3,381,963.44 (10.3%); £3,771,496.75 -> £3,381,963.56 (10.3%); £3,771,497.00 -> £3,381,963.68 (10.3%); £3,771,497.26 -> £3,381,963.80 (10.3%); £3,771,497.52 -> £3,381,963.92 (10.3%); £3,771,497.77 -> £3,381,964.03 (10.3%); £3,771,498.02 -> £3,381,964.14 (10.3%); £3,771,498.28 -> £3,381,964.25 (10.3%); £3,771,498.48 -> £3,381,964.50 (10.3%); £3,771,498.67 -> £3,381,964.72 (10.3%); £3,771,498.85 -> £3,381,964.92 (10.3%); £3,771,499.04 -> £3,381,965.11 (10.3%); £3,771,499.30 -> £3,381,965.28 (10.3%); £3,771,499.55 -> £3,381,965.45 (10.3%); £3,771,499.75 -> £3,381,965.61 (10.3%); £3,771,500.01 -> £3,381,965.77 (10.3%); £3,771,500.27 -> £3,381,965.93 (10.3%); £3,771,500.53 -> £3,381,966.08 (10.3%); £3,771,500.77 -> £3,381,966.23 (10.3%); £3,771,501.03 -> £3,381,966.27 (10.3%); £3,771,501.29 -> £3,381,966.31 (10.3%); £3,771,501.52 -> £3,381,966.35 (10.3%); £3,771,501.74 -> £3,381,966.39 (10.3%); £3,771,501.94 -> £3,381,966.43 (10.3%); £3,771,502.10 -> £3,381,966.46 (10.3%); £3,771,502.25 -> £3,381,966.50 (10.3%); £3,771,502.40 -> £3,381,966.54 (10.3%); £3,771,502.55 -> £3,381,966.58 (10.3%); £3,771,502.70 -> £3,381,966.61 (10.3%); £3,771,502.85 -> £3,381,966.65 (10.3%); £3,771,503.01 -> £3,381,966.69 (10.3%); £3,771,503.16 -> £3,381,966.73 (10.3%); £3,771,503.32 -> £3,381,966.77 (10.3%); £3,771,503.47 -> £3,381,966.81 (10.3%); £3,771,503.62 -> £3,381,966.85 (10.3%); £3,771,503.77 -> £3,381,967.01 (10.3%); £3,771,503.93 -> £3,381,967.18 (10.3%); £3,771,504.10 -> £3,381,967.37 (10.3%); £3,771,504.29 -> £3,381,967.56 (10.3%); £3,771,504.49 -> £3,381,967.78 (10.3%); £3,771,504.71 -> £3,381,968.01 (10.3%); £3,771,504.96 -> £3,381,968.27 (10.3%); £3,771,505.22 -> £3,381,968.54 (10.3%); £3,771,505.49 -> £3,381,968.67 (10.3%); £3,771,505.75 -> £3,381,968.80 (10.3%); £3,771,506.01 -> £3,381,968.94 (10.3%); £3,771,506.26 -> £3,381,969.09 (10.3%); £3,771,506.52 -> £3,381,969.23 (10.3%); £3,771,506.76 -> £3,381,969.37 (10.3%); £3,771,507.02 -> £3,381,969.49 (10.3%); £3,771,507.27 -> £3,381,969.62 (10.3%); £3,771,507.54 -> £3,381,969.75 (10.3%); £3,771,507.80 -> £3,381,969.86 (10.3%); £3,771,508.04 -> £3,381,969.98 (10.3%); £3,771,508.29 -> £3,381,970.09 (10.3%); £3,771,508.55 -> £3,381,970.19 (10.3%); £3,771,508.75 -> £3,381,970.45 (10.3%); £3,771,508.94 -> £3,381,970.70 (10.3%); £3,771,509.13 -> £3,381,970.91 (10.3%); £3,771,509.33 -> £3,381,971.11 (10.3%); £3,771,509.53 -> £3,381,971.30 (10.3%); £3,771,509.72 -> £3,381,971.48 (10.3%); £3,771,509.91 -> £3,381,971.67 (10.3%); £3,771,510.17 -> £3,381,971.85 (10.3%); £3,771,510.43 -> £3,381,972.03 (10.3%); £3,771,510.68 -> £3,381,972.21 (10.3%); £3,771,510.94 -> £3,381,972.38 (10.3%); £3,771,511.19 -> £3,381,972.42 (10.3%); £3,771,511.45 -> £3,381,972.46 (10.3%); £3,771,511.68 -> £3,381,972.50 (10.3%); £3,771,511.89 -> £3,381,972.54 (10.3%); £3,771,512.10 -> £3,381,972.58 (10.3%); £3,771,512.24 -> £3,381,972.62 (10.3%); £3,771,512.38 -> £3,381,972.65 (10.3%); £3,771,512.52 -> £3,381,972.69 (10.3%); £3,771,512.66 -> £3,381,972.73 (10.3%); £3,771,512.80 -> £3,381,972.77 (10.3%); £3,771,512.95 -> £3,381,972.80 (10.3%); £3,771,513.09 -> £3,381,972.84 (10.3%); £3,771,513.23 -> £3,381,972.88 (10.3%); £3,771,513.36 -> £3,381,972.92 (10.3%); £3,771,513.50 -> £3,381,972.96 (10.3%); £3,771,513.63 -> £3,381,973.00 (10.3%); £3,771,513.77 -> £3,381,973.19 (10.3%); £3,771,513.92 -> £3,381,973.37 (10.3%); £3,771,514.07 -> £3,381,973.56 (10.3%); £3,771,514.24 -> £3,381,973.76 (10.3%); £3,771,514.43 -> £3,381,973.97 (10.3%); £3,771,514.63 -> £3,381,974.19 (10.3%); £3,771,514.85 -> £3,381,974.43 (10.3%); £3,771,515.08 -> £3,381,974.68 (10.3%); £3,771,515.31 -> £3,381,974.77 (10.3%); £3,771,515.55 -> £3,381,974.86 (10.3%); £3,771,515.78 -> £3,381,974.95 (10.3%); £3,771,516.01 -> £3,381,975.04 (10.3%); £3,771,516.24 -> £3,381,975.13 (10.3%); £3,771,516.46 -> £3,381,975.21 (10.3%); £3,771,516.70 -> £3,381,975.29 (10.3%); £3,771,516.93 -> £3,381,975.37 (10.3%); £3,771,517.16 -> £3,381,975.45 (10.3%); £3,771,517.40 -> £3,381,975.52 (10.3%); £3,771,517.63 -> £3,381,975.59 (10.3%); £3,771,517.86 -> £3,381,975.66 (10.3%); £3,771,518.08 -> £3,381,975.72 (10.3%); £3,771,518.26 -> £3,381,975.94 (10.3%); £3,771,518.44 -> £3,381,976.15 (10.3%); £3,771,518.61 -> £3,381,976.35 (10.3%); £3,771,518.78 -> £3,381,976.54 (10.3%); £3,771,518.95 -> £3,381,976.74 (10.3%); £3,771,519.19 -> £3,381,976.94 (10.3%); £3,771,519.42 -> £3,381,977.13 (10.3%); £3,771,519.65 -> £3,381,977.32 (10.3%); £3,771,519.88 -> £3,381,977.51 (10.3%); £3,771,520.11 -> £3,381,977.69 (10.3%); £3,771,520.34 -> £3,381,977.89 (10.3%); £3,771,520.57 -> £3,381,977.93 (10.3%); £3,771,520.80 -> £3,381,977.97 (10.3%); £3,771,521.01 -> £3,381,978.01 (10.3%); £3,771,521.20 -> £3,381,978.05 (10.3%); £3,771,521.38 -> £3,381,978.09 (10.3%); £3,771,521.51 -> £3,381,978.13 (10.3%); £3,771,521.66 -> £3,381,978.17 (10.3%); £3,771,521.80 -> £3,381,978.21 (10.3%); £3,771,521.94 -> £3,381,978.24 (10.3%); £3,771,522.08 -> £3,381,978.28 (10.3%); £3,771,522.22 -> £3,381,978.32 (10.3%); £3,771,522.36 -> £3,381,978.35 (10.3%); £3,771,522.51 -> £3,381,978.39 (10.3%); £3,771,522.64 -> £3,381,978.43 (10.3%); £3,771,522.78 -> £3,381,978.46 (10.3%); £3,771,522.91 -> £3,381,978.50 (10.3%); £3,771,523.05 -> £3,381,978.66 (10.3%); £3,771,523.19 -> £3,381,978.82 (10.3%); £3,771,523.35 -> £3,381,978.98 (10.3%); £3,771,523.52 -> £3,381,979.13 (10.3%); £3,771,523.71 -> £3,381,979.29 (10.3%); £3,771,523.92 -> £3,381,979.45 (10.3%); £3,771,524.14 -> £3,381,979.61 (10.3%); £3,771,524.37 -> £3,381,979.78 (10.3%); £3,771,524.60 -> £3,381,979.83 (10.3%); £3,771,524.84 -> £3,381,979.87 (10.3%); £3,771,525.07 -> £3,381,979.93 (10.3%); £3,771,525.31 -> £3,381,979.98 (10.3%); £3,771,525.54 -> £3,381,980.02 (10.3%); £3,771,525.77 -> £3,381,980.07 (10.3%); £3,771,525.99 -> £3,381,980.12 (10.3%); £3,771,526.22 -> £3,381,980.16 (10.3%); £3,771,526.46 -> £3,381,980.21 (10.3%); £3,771,526.69 -> £3,381,980.25 (10.3%); £3,771,526.93 -> £3,381,980.30 (10.3%); £3,771,527.16 -> £3,381,980.34 (10.3%); £3,771,527.38 -> £3,381,980.39 (10.3%); £3,771,527.56 -> £3,381,980.55 (10.3%); £3,771,527.72 -> £3,381,980.71 (10.3%); £3,771,527.90 -> £3,381,980.87 (10.3%); £3,771,528.08 -> £3,381,981.04 (10.3%); £3,771,528.31 -> £3,381,981.21 (10.3%); £3,771,528.54 -> £3,381,981.37 (10.3%); £3,771,528.72 -> £3,381,981.53 (10.3%); £3,771,528.95 -> £3,381,981.69 (10.3%); £3,771,529.19 -> £3,381,981.84 (10.3%); £3,771,529.42 -> £3,381,982.00 (10.3%); £3,771,529.66 -> £3,381,982.15 (10.3%); £3,771,529.90 -> £3,381,982.19 (10.3%); £3,771,530.13 -> £3,381,982.23 (10.3%); £3,771,530.34 -> £3,381,982.27 (10.3%); £3,771,530.54 -> £3,381,982.30 (10.3%); £3,771,530.71 -> £3,381,982.34 (10.3%); £3,771,530.87 -> £3,381,982.37 (10.3%); £3,771,531.03 -> £3,381,982.41 (10.3%); £3,771,531.19 -> £3,381,982.45 (10.3%); £3,771,531.35 -> £3,381,982.48 (10.3%); £3,771,531.51 -> £3,381,982.52 (10.3%); £3,771,531.67 -> £3,381,982.56 (10.3%); £3,771,531.83 -> £3,381,982.60 (10.3%); £3,771,531.99 -> £3,381,982.64 (10.3%); £3,771,532.15 -> £3,381,982.67 (10.3%); £3,771,532.31 -> £3,381,982.71 (10.3%); £3,771,532.48 -> £3,381,982.75 (10.3%); £3,771,532.64 -> £3,381,982.87 (10.3%); £3,771,532.80 -> £3,381,983.00 (10.3%); £3,771,532.98 -> £3,381,983.14 (10.3%); £3,771,533.18 -> £3,381,983.29 (10.3%); £3,771,533.39 -> £3,381,983.46 (10.3%); £3,771,533.63 -> £3,381,983.66 (10.3%); £3,771,533.88 -> £3,381,983.87 (10.3%); £3,771,534.16 -> £3,381,984.10 (10.3%); £3,771,534.42 -> £3,381,984.22 (10.3%); £3,771,534.69 -> £3,381,984.34 (10.3%); £3,771,534.97 -> £3,381,984.47 (10.3%); £3,771,535.23 -> £3,381,984.59 (10.3%); £3,771,535.49 -> £3,381,984.71 (10.3%); £3,771,535.76 -> £3,381,984.83 (10.3%); £3,771,536.01 -> £3,381,984.94 (10.3%); £3,771,536.27 -> £3,381,985.05 (10.3%); £3,771,536.54 -> £3,381,985.17 (10.3%); £3,771,536.80 -> £3,381,985.28 (10.3%); £3,771,537.07 -> £3,381,985.40 (10.3%); £3,771,537.34 -> £3,381,985.51 (10.3%); £3,771,537.61 -> £3,381,985.62 (10.3%); £3,771,537.88 -> £3,381,985.85 (10.3%); £3,771,538.15 -> £3,381,986.06 (10.3%); £3,771,538.42 -> £3,381,986.25 (10.3%); £3,771,538.69 -> £3,381,986.41 (10.3%); £3,771,538.97 -> £3,381,986.56 (10.3%); £3,771,539.23 -> £3,381,986.70 (10.3%); £3,771,539.44 -> £3,381,986.85 (10.3%); £3,771,539.71 -> £3,381,986.99 (10.3%); £3,771,539.98 -> £3,381,987.12 (10.3%); £3,771,540.24 -> £3,381,987.25 (10.3%); £3,771,540.51 -> £3,381,987.38 (10.3%); £3,771,540.77 -> £3,381,987.42 (10.3%); £3,771,541.05 -> £3,381,987.46 (10.3%); £3,771,541.29 -> £3,381,987.50 (10.3%); £3,771,541.52 -> £3,381,987.54 (10.3%); £3,771,541.73 -> £3,381,987.57 (10.3%); £3,771,541.89 -> £3,381,987.61 (10.3%); £3,771,542.05 -> £3,381,987.65 (10.3%); £3,771,542.21 -> £3,381,987.69 (10.3%); £3,771,542.37 -> £3,381,987.72 (10.3%); £3,771,542.52 -> £3,381,987.76 (10.3%); £3,771,542.69 -> £3,381,987.80 (10.3%); £3,771,542.84 -> £3,381,987.84 (10.3%); £3,771,543.00 -> £3,381,987.88 (10.3%); £3,771,543.16 -> £3,381,987.91 (10.3%); £3,771,543.32 -> £3,381,987.95 (10.3%); £3,771,543.48 -> £3,381,988.00 (10.3%); £3,771,543.63 -> £3,381,988.18 (10.3%); £3,771,543.79 -> £3,381,988.38 (10.3%); £3,771,543.97 -> £3,381,988.59 (10.3%); £3,771,544.16 -> £3,381,988.80 (10.3%); £3,771,544.37 -> £3,381,989.04 (10.3%); £3,771,544.60 -> £3,381,989.30 (10.3%); £3,771,544.85 -> £3,381,989.59 (10.3%); £3,771,545.12 -> £3,381,989.89 (10.3%); £3,771,545.39 -> £3,381,990.02 (10.3%); £3,771,545.66 -> £3,381,990.14 (10.3%); £3,771,545.92 -> £3,381,990.27 (10.3%); £3,771,546.19 -> £3,381,990.40 (10.3%); £3,771,546.45 -> £3,381,990.53 (10.3%); £3,771,546.71 -> £3,381,990.65 (10.3%); £3,771,546.98 -> £3,381,990.76 (10.3%); £3,771,547.24 -> £3,381,990.88 (10.3%); £3,771,547.51 -> £3,381,991.00 (10.3%); £3,771,547.79 -> £3,381,991.11 (10.3%); £3,771,548.04 -> £3,381,991.23 (10.3%); £3,771,548.31 -> £3,381,991.34 (10.3%); £3,771,548.58 -> £3,381,991.45 (10.3%); £3,771,548.78 -> £3,381,991.72 (10.3%); £3,771,548.97 -> £3,381,991.99 (10.3%); £3,771,549.24 -> £3,381,992.23 (10.3%); £3,771,549.51 -> £3,381,992.44 (10.3%); £3,771,549.71 -> £3,381,992.65 (10.3%); £3,771,549.91 -> £3,381,992.84 (10.3%); £3,771,550.10 -> £3,381,993.04 (10.3%); £3,771,550.37 -> £3,381,993.23 (10.3%); £3,771,550.63 -> £3,381,993.43 (10.3%); £3,771,550.89 -> £3,381,993.62 (10.3%); £3,771,551.14 -> £3,381,993.80 (10.3%); £3,771,551.40 -> £3,381,993.84 (10.3%); £3,771,551.67 -> £3,381,993.89 (10.3%); £3,771,551.92 -> £3,381,993.93 (10.3%); £3,771,552.13 -> £3,381,993.96 (10.3%); £3,771,552.34 -> £3,381,994.00 (10.3%); £3,771,552.50 -> £3,381,994.04 (10.3%); £3,771,552.66 -> £3,381,994.08 (10.3%); £3,771,552.82 -> £3,381,994.11 (10.3%); £3,771,552.98 -> £3,381,994.15 (10.3%); £3,771,553.14 -> £3,381,994.19 (10.3%); £3,771,553.30 -> £3,381,994.23 (10.3%); £3,771,553.45 -> £3,381,994.27 (10.3%); £3,771,553.62 -> £3,381,994.30 (10.3%); £3,771,553.77 -> £3,381,994.34 (10.3%); £3,771,553.94 -> £3,381,994.38 (10.3%); £3,771,554.09 -> £3,381,994.42 (10.3%); £3,771,554.25 -> £3,381,994.62 (10.3%); £3,771,554.41 -> £3,381,994.83 (10.3%); £3,771,554.58 -> £3,381,995.06 (10.3%); £3,771,554.78 -> £3,381,995.30 (10.3%); £3,771,554.98 -> £3,381,995.56 (10.3%); £3,771,555.21 -> £3,381,995.82 (10.3%); £3,771,555.47 -> £3,381,996.13 (10.3%); £3,771,555.74 -> £3,381,996.43 (10.3%); £3,771,556.00 -> £3,381,996.55 (10.3%); £3,771,556.27 -> £3,381,996.67 (10.3%); £3,771,556.54 -> £3,381,996.80 (10.3%); £3,771,556.80 -> £3,381,996.92 (10.3%); £3,771,557.07 -> £3,381,997.05 (10.3%); £3,771,557.33 -> £3,381,997.18 (10.3%); £3,771,557.59 -> £3,381,997.30 (10.3%); £3,771,557.84 -> £3,381,997.42 (10.3%); £3,771,558.12 -> £3,381,997.54 (10.3%); £3,771,558.38 -> £3,381,997.65 (10.3%); £3,771,558.65 -> £3,381,997.77 (10.3%); £3,771,558.91 -> £3,381,997.88 (10.3%); £3,771,559.18 -> £3,381,997.99 (10.3%); £3,771,559.44 -> £3,381,998.29 (10.3%); £3,771,559.70 -> £3,381,998.56 (10.3%); £3,771,559.91 -> £3,381,998.81 (10.3%); £3,771,560.10 -> £3,381,999.03 (10.3%); £3,771,560.31 -> £3,381,999.25 (10.3%); £3,771,560.58 -> £3,381,999.47 (10.3%); £3,771,560.84 -> £3,381,999.68 (10.3%); £3,771,561.11 -> £3,381,999.89 (10.3%); £3,771,561.37 -> £3,382,000.09 (10.3%); £3,771,561.64 -> £3,382,000.29 (10.3%); £3,771,561.90 -> £3,382,000.49 (10.3%); £3,771,562.17 -> £3,382,000.54 (10.3%); £3,771,562.44 -> £3,382,000.58 (10.3%); £3,771,562.68 -> £3,382,000.62 (10.3%); £3,771,562.90 -> £3,382,000.66 (10.3%); £3,771,563.11 -> £3,382,000.69 (10.3%); £3,771,563.27 -> £3,382,000.73 (10.3%); £3,771,563.43 -> £3,382,000.77 (10.3%); £3,771,563.59 -> £3,382,000.81 (10.3%); £3,771,563.75 -> £3,382,000.85 (10.3%); £3,771,563.90 -> £3,382,000.88 (10.3%); £3,771,564.06 -> £3,382,000.92 (10.3%); £3,771,564.22 -> £3,382,000.96 (10.3%); £3,771,564.38 -> £3,382,001.00 (10.3%); £3,771,564.54 -> £3,382,001.04 (10.3%); £3,771,564.70 -> £3,382,001.08 (10.3%); £3,771,564.86 -> £3,382,001.12 (10.3%); £3,771,565.03 -> £3,382,001.33 (10.3%); £3,771,565.19 -> £3,382,001.54 (10.3%); £3,771,565.36 -> £3,382,001.75 (10.3%); £3,771,565.55 -> £3,382,001.97 (10.3%); £3,771,565.76 -> £3,382,002.21 (10.3%); £3,771,565.98 -> £3,382,002.48 (10.3%); £3,771,566.22 -> £3,382,002.77 (10.3%); £3,771,566.49 -> £3,382,003.08 (10.3%); £3,771,566.75 -> £3,382,003.21 (10.3%); £3,771,567.01 -> £3,382,003.34 (10.3%); £3,771,567.27 -> £3,382,003.47 (10.3%); £3,771,567.54 -> £3,382,003.60 (10.3%); £3,771,567.80 -> £3,382,003.73 (10.3%); £3,771,568.07 -> £3,382,003.85 (10.3%); £3,771,568.33 -> £3,382,003.97 (10.3%); £3,771,568.61 -> £3,382,004.09 (10.3%); £3,771,568.86 -> £3,382,004.21 (10.3%); £3,771,569.13 -> £3,382,004.32 (10.3%); £3,771,569.40 -> £3,382,004.44 (10.3%); £3,771,569.67 -> £3,382,004.55 (10.3%); £3,771,569.94 -> £3,382,004.66 (10.3%); £3,771,570.20 -> £3,382,004.95 (10.3%); £3,771,570.40 -> £3,382,005.21 (10.3%); £3,771,570.60 -> £3,382,005.45 (10.3%); £3,771,570.79 -> £3,382,005.67 (10.3%); £3,771,570.99 -> £3,382,005.89 (10.3%); £3,771,571.19 -> £3,382,006.10 (10.3%); £3,771,571.46 -> £3,382,006.31 (10.3%); £3,771,571.72 -> £3,382,006.51 (10.3%); £3,771,571.98 -> £3,382,006.72 (10.3%); £3,771,572.25 -> £3,382,006.92 (10.3%); £3,771,572.51 -> £3,382,007.11 (10.3%); £3,771,572.77 -> £3,382,007.15 (10.3%); £3,771,573.04 -> £3,382,007.19 (10.3%); £3,771,573.29 -> £3,382,007.23 (10.3%); £3,771,573.51 -> £3,382,007.27 (10.3%); £3,771,573.71 -> £3,382,007.30 (10.3%); £3,771,573.87 -> £3,382,007.34 (10.3%); £3,771,574.03 -> £3,382,007.38 (10.3%); £3,771,574.19 -> £3,382,007.42 (10.3%); £3,771,574.35 -> £3,382,007.46 (10.3%); £3,771,574.50 -> £3,382,007.49 (10.3%); £3,771,574.66 -> £3,382,007.53 (10.3%); £3,771,574.82 -> £3,382,007.57 (10.3%); £3,771,574.98 -> £3,382,007.60 (10.3%); £3,771,575.15 -> £3,382,007.64 (10.3%); £3,771,575.30 -> £3,382,007.68 (10.3%); £3,771,575.46 -> £3,382,007.72 (10.3%); £3,771,575.62 -> £3,382,007.86 (10.3%); £3,771,575.77 -> £3,382,008.00 (10.3%); £3,771,575.95 -> £3,382,008.16 (10.3%); £3,771,576.15 -> £3,382,008.33 (10.3%); £3,771,576.36 -> £3,382,008.52 (10.3%); £3,771,576.59 -> £3,382,008.73 (10.3%); £3,771,576.83 -> £3,382,008.97 (10.3%); £3,771,577.11 -> £3,382,009.21 (10.3%); £3,771,577.38 -> £3,382,009.34 (10.3%); £3,771,577.66 -> £3,382,009.46 (10.3%); £3,771,577.92 -> £3,382,009.59 (10.3%); £3,771,578.19 -> £3,382,009.73 (10.3%); £3,771,578.45 -> £3,382,009.86 (10.3%); £3,771,578.72 -> £3,382,009.98 (10.3%); £3,771,578.98 -> £3,382,010.10 (10.3%); £3,771,579.25 -> £3,382,010.22 (10.3%); £3,771,579.52 -> £3,382,010.34 (10.3%); £3,771,579.77 -> £3,382,010.46 (10.3%); £3,771,580.04 -> £3,382,010.58 (10.3%); £3,771,580.30 -> £3,382,010.69 (10.3%); £3,771,580.58 -> £3,382,010.81 (10.3%); £3,771,580.85 -> £3,382,011.05 (10.3%); £3,771,581.11 -> £3,382,011.27 (10.3%); £3,771,581.38 -> £3,382,011.46 (10.3%); £3,771,581.64 -> £3,382,011.64 (10.3%); £3,771,581.90 -> £3,382,011.80 (10.3%); £3,771,582.17 -> £3,382,011.97 (10.3%); £3,771,582.43 -> £3,382,012.13 (10.3%); £3,771,582.70 -> £3,382,012.28 (10.3%); £3,771,582.97 -> £3,382,012.44 (10.3%); £3,771,583.23 -> £3,382,012.58 (10.3%); £3,771,583.49 -> £3,382,012.73 (10.3%); £3,771,583.76 -> £3,382,012.77 (10.3%); £3,771,584.03 -> £3,382,012.81 (10.3%); £3,771,584.28 -> £3,382,012.85 (10.3%); £3,771,584.51 -> £3,382,012.89 (10.3%); £3,771,584.72 -> £3,382,012.93 (10.3%); £3,771,584.85 -> £3,382,012.97 (10.3%); £3,771,584.99 -> £3,382,013.00 (10.3%); £3,771,585.13 -> £3,382,013.04 (10.3%); £3,771,585.27 -> £3,382,013.08 (10.3%); £3,771,585.41 -> £3,382,013.12 (10.3%); £3,771,585.55 -> £3,382,013.16 (10.3%); £3,771,585.69 -> £3,382,013.20 (10.3%); £3,771,585.83 -> £3,382,013.23 (10.3%); £3,771,585.97 -> £3,382,013.27 (10.3%); £3,771,586.11 -> £3,382,013.31 (10.3%); £3,771,586.25 -> £3,382,013.35 (10.3%); £3,771,586.39 -> £3,382,013.49 (10.3%); £3,771,586.53 -> £3,382,013.64 (10.3%); £3,771,586.69 -> £3,382,013.78 (10.3%); £3,771,586.86 -> £3,382,013.92 (10.3%); £3,771,587.04 -> £3,382,014.08 (10.3%); £3,771,587.24 -> £3,382,014.24 (10.3%); £3,771,587.46 -> £3,382,014.43 (10.3%); £3,771,587.69 -> £3,382,014.63 (10.3%); £3,771,587.92 -> £3,382,014.72 (10.3%); £3,771,588.16 -> £3,382,014.81 (10.3%); £3,771,588.39 -> £3,382,014.90 (10.3%); £3,771,588.62 -> £3,382,014.99 (10.3%); £3,771,588.85 -> £3,382,015.08 (10.3%); £3,771,589.08 -> £3,382,015.16 (10.3%); £3,771,589.32 -> £3,382,015.24 (10.3%); £3,771,589.55 -> £3,382,015.31 (10.3%); £3,771,589.78 -> £3,382,015.38 (10.3%); £3,771,590.01 -> £3,382,015.45 (10.3%); £3,771,590.24 -> £3,382,015.53 (10.3%); £3,771,590.48 -> £3,382,015.59 (10.3%); £3,771,590.71 -> £3,382,015.66 (10.3%); £3,771,590.94 -> £3,382,015.83 (10.3%); £3,771,591.12 -> £3,382,016.00 (10.3%); £3,771,591.36 -> £3,382,016.15 (10.3%); £3,771,591.53 -> £3,382,016.29 (10.3%); £3,771,591.70 -> £3,382,016.43 (10.3%); £3,771,591.88 -> £3,382,016.57 (10.3%); £3,771,592.05 -> £3,382,016.72 (10.3%); £3,771,592.29 -> £3,382,016.87 (10.3%); £3,771,592.52 -> £3,382,017.02 (10.3%); £3,771,592.75 -> £3,382,017.15 (10.3%); £3,771,592.97 -> £3,382,017.29 (10.3%); £3,771,593.20 -> £3,382,017.34 (10.3%); £3,771,593.44 -> £3,382,017.38 (10.3%); £3,771,593.65 -> £3,382,017.42 (10.3%); £3,771,593.84 -> £3,382,017.46 (10.3%); £3,771,594.02 -> £3,382,017.49 (10.3%); £3,771,594.16 -> £3,382,017.53 (10.3%); £3,771,594.30 -> £3,382,017.57 (10.3%); £3,771,594.44 -> £3,382,017.61 (10.3%); £3,771,594.58 -> £3,382,017.65 (10.3%); £3,771,594.72 -> £3,382,017.69 (10.3%); £3,771,594.86 -> £3,382,017.73 (10.3%); £3,771,595.00 -> £3,382,017.76 (10.3%); £3,771,595.14 -> £3,382,017.80 (10.3%); £3,771,595.28 -> £3,382,017.84 (10.3%); £3,771,595.42 -> £3,382,017.88 (10.3%); £3,771,595.56 -> £3,382,017.91 (10.3%); £3,771,595.70 -> £3,382,018.04 (10.3%); £3,771,595.85 -> £3,382,018.17 (10.3%); £3,771,596.01 -> £3,382,018.30 (10.3%); £3,771,596.17 -> £3,382,018.43 (10.3%); £3,771,596.35 -> £3,382,018.57 (10.3%); £3,771,596.55 -> £3,382,018.70 (10.3%); £3,771,596.78 -> £3,382,018.83 (10.3%); £3,771,597.01 -> £3,382,018.97 (10.3%); £3,771,597.24 -> £3,382,019.02 (10.3%); £3,771,597.48 -> £3,382,019.07 (10.3%); £3,771,597.71 -> £3,382,019.12 (10.3%); £3,771,597.95 -> £3,382,019.18 (10.3%); £3,771,598.18 -> £3,382,019.23 (10.3%); £3,771,598.42 -> £3,382,019.28 (10.3%); £3,771,598.66 -> £3,382,019.32 (10.3%); £3,771,598.90 -> £3,382,019.37 (10.3%); £3,771,599.13 -> £3,382,019.41 (10.3%); £3,771,599.37 -> £3,382,019.46 (10.3%); £3,771,599.61 -> £3,382,019.51 (10.3%); £3,771,599.84 -> £3,382,019.55 (10.3%); £3,771,600.08 -> £3,382,019.60 (10.3%); £3,771,600.31 -> £3,382,019.74 (10.3%); £3,771,600.54 -> £3,382,019.87 (10.3%); £3,771,600.71 -> £3,382,020.00 (10.3%); £3,771,600.89 -> £3,382,020.13 (10.3%); £3,771,601.07 -> £3,382,020.27 (10.3%); £3,771,601.24 -> £3,382,020.40 (10.3%); £3,771,601.42 -> £3,382,020.53 (10.3%); £3,771,601.66 -> £3,382,020.66 (10.3%); £3,771,601.89 -> £3,382,020.79 (10.3%); £3,771,602.13 -> £3,382,020.92 (10.3%); £3,771,602.36 -> £3,382,021.06 (10.3%); £3,771,602.59 -> £3,382,021.10 (10.3%); £3,771,602.83 -> £3,382,021.14 (10.3%); £3,771,603.05 -> £3,382,021.18 (10.3%); £3,771,603.25 -> £3,382,021.22 (10.3%); £3,771,603.43 -> £3,382,021.25 (10.3%); £3,771,603.59 -> £3,382,021.29 (10.3%); £3,771,603.75 -> £3,382,021.33 (10.3%); £3,771,603.92 -> £3,382,021.37 (10.3%); £3,771,604.08 -> £3,382,021.41 (10.3%); £3,771,604.24 -> £3,382,021.45 (10.3%); £3,771,604.40 -> £3,382,021.48 (10.3%); £3,771,604.57 -> £3,382,021.52 (10.3%); £3,771,604.73 -> £3,382,021.56 (10.3%); £3,771,604.90 -> £3,382,021.60 (10.3%); £3,771,605.06 -> £3,382,021.64 (10.3%); £3,771,605.22 -> £3,382,021.68 (10.3%); £3,771,605.39 -> £3,382,021.83 (10.3%); £3,771,605.55 -> £3,382,021.97 (10.3%); £3,771,605.73 -> £3,382,022.12 (10.3%); £3,771,605.94 -> £3,382,022.29 (10.3%); £3,771,606.16 -> £3,382,022.47 (10.3%); £3,771,606.40 -> £3,382,022.68 (10.3%); £3,771,606.65 -> £3,382,022.92 (10.3%); £3,771,606.91 -> £3,382,023.18 (10.3%); £3,771,607.19 -> £3,382,023.31 (10.3%); £3,771,607.46 -> £3,382,023.43 (10.3%); £3,771,607.74 -> £3,382,023.56 (10.3%); £3,771,608.01 -> £3,382,023.68 (10.3%); £3,771,608.28 -> £3,382,023.81 (10.3%); £3,771,608.55 -> £3,382,023.93 (10.3%); £3,771,608.82 -> £3,382,024.04 (10.3%); £3,771,609.08 -> £3,382,024.15 (10.3%); £3,771,609.35 -> £3,382,024.27 (10.3%); £3,771,609.61 -> £3,382,024.38 (10.3%); £3,771,609.89 -> £3,382,024.49 (10.3%); £3,771,610.17 -> £3,382,024.60 (10.3%); £3,771,610.43 -> £3,382,024.71 (10.3%); £3,771,610.64 -> £3,382,024.94 (10.3%); £3,771,610.84 -> £3,382,025.16 (10.3%); £3,771,611.04 -> £3,382,025.35 (10.3%); £3,771,611.24 -> £3,382,025.51 (10.3%); £3,771,611.45 -> £3,382,025.68 (10.3%); £3,771,611.73 -> £3,382,025.85 (10.3%); £3,771,612.00 -> £3,382,026.01 (10.3%); £3,771,612.29 -> £3,382,026.16 (10.3%); £3,771,612.56 -> £3,382,026.31 (10.3%); £3,771,612.83 -> £3,382,026.45 (10.3%); £3,771,613.10 -> £3,382,026.59 (10.3%); £3,771,613.37 -> £3,382,026.63 (10.3%); £3,771,613.64 -> £3,382,026.68 (10.3%); £3,771,613.89 -> £3,382,026.72 (10.3%); £3,771,614.12 -> £3,382,026.76 (10.3%); £3,771,614.34 -> £3,382,026.79 (10.3%); £3,771,614.51 -> £3,382,026.83 (10.3%); £3,771,614.67 -> £3,382,026.87 (10.3%); £3,771,614.84 -> £3,382,026.91 (10.3%); £3,771,615.01 -> £3,382,026.95 (10.3%); £3,771,615.18 -> £3,382,026.99 (10.3%); £3,771,615.34 -> £3,382,027.02 (10.3%); £3,771,615.51 -> £3,382,027.06 (10.3%); £3,771,615.67 -> £3,382,027.10 (10.3%); £3,771,615.83 -> £3,382,027.14 (10.3%); £3,771,616.00 -> £3,382,027.18 (10.3%); £3,771,616.17 -> £3,382,027.22 (10.3%); £3,771,616.33 -> £3,382,027.39 (10.3%); £3,771,616.50 -> £3,382,027.55 (10.3%); £3,771,616.69 -> £3,382,027.73 (10.3%); £3,771,616.89 -> £3,382,027.92 (10.3%); £3,771,617.11 -> £3,382,028.13 (10.3%); £3,771,617.34 -> £3,382,028.36 (10.3%); £3,771,617.60 -> £3,382,028.62 (10.3%); £3,771,617.87 -> £3,382,028.88 (10.3%); £3,771,618.14 -> £3,382,029.01 (10.3%); £3,771,618.42 -> £3,382,029.14 (10.3%); £3,771,618.70 -> £3,382,029.26 (10.3%); £3,771,618.98 -> £3,382,029.40 (10.3%); £3,771,619.25 -> £3,382,029.52 (10.3%); £3,771,619.52 -> £3,382,029.65 (10.3%); £3,771,619.79 -> £3,382,029.77 (10.3%); £3,771,620.07 -> £3,382,029.88 (10.3%); £3,771,620.34 -> £3,382,030.00 (10.3%); £3,771,620.62 -> £3,382,030.11 (10.3%); £3,771,620.88 -> £3,382,030.23 (10.3%); £3,771,621.15 -> £3,382,030.34 (10.3%); £3,771,621.42 -> £3,382,030.44 (10.3%); £3,771,621.63 -> £3,382,030.69 (10.3%); £3,771,621.84 -> £3,382,030.92 (10.3%); £3,771,622.04 -> £3,382,031.11 (10.3%); £3,771,622.25 -> £3,382,031.29 (10.3%); £3,771,622.45 -> £3,382,031.46 (10.3%); £3,771,622.66 -> £3,382,031.63 (10.3%); £3,771,622.87 -> £3,382,031.79 (10.3%); £3,771,623.14 -> £3,382,031.95 (10.3%); £3,771,623.41 -> £3,382,032.11 (10.3%); £3,771,623.68 -> £3,382,032.26 (10.3%); £3,771,623.96 -> £3,382,032.41 (10.3%); £3,771,624.24 -> £3,382,032.45 (10.3%); £3,771,624.50 -> £3,382,032.50 (10.3%); £3,771,624.75 -> £3,382,032.54 (10.3%); £3,771,624.99 -> £3,382,032.57 (10.3%); £3,771,625.19 -> £3,382,032.61 (10.3%); £3,771,625.36 -> £3,382,032.65 (10.3%); £3,771,625.53 -> £3,382,032.68 (10.3%); £3,771,625.69 -> £3,382,032.72 (10.3%); £3,771,625.85 -> £3,382,032.76 (10.3%); £3,771,626.02 -> £3,382,032.80 (10.3%); £3,771,626.19 -> £3,382,032.83 (10.3%); £3,771,626.35 -> £3,382,032.87 (10.3%); £3,771,626.52 -> £3,382,032.91 (10.3%); £3,771,626.68 -> £3,382,032.95 (10.3%); £3,771,626.85 -> £3,382,032.99 (10.3%); £3,771,627.01 -> £3,382,033.03 (10.3%); £3,771,627.18 -> £3,382,033.25 (10.3%); £3,771,627.34 -> £3,382,033.49 (10.3%); £3,771,627.53 -> £3,382,033.74 (10.3%); £3,771,627.73 -> £3,382,033.99 (10.3%); £3,771,627.96 -> £3,382,034.27 (10.3%); £3,771,628.20 -> £3,382,034.57 (10.3%); £3,771,628.45 -> £3,382,034.88 (10.3%); £3,771,628.73 -> £3,382,035.21 (10.3%); £3,771,629.02 -> £3,382,035.33 (10.3%); £3,771,629.30 -> £3,382,035.45 (10.3%); £3,771,629.58 -> £3,382,035.58 (10.3%); £3,771,629.86 -> £3,382,035.71 (10.3%); £3,771,630.13 -> £3,382,035.83 (10.3%); £3,771,630.41 -> £3,382,035.96 (10.3%); £3,771,630.68 -> £3,382,036.08 (10.3%); £3,771,630.95 -> £3,382,036.19 (10.3%); £3,771,631.22 -> £3,382,036.31 (10.3%); £3,771,631.51 -> £3,382,036.42 (10.3%); £3,771,631.77 -> £3,382,036.54 (10.3%); £3,771,632.05 -> £3,382,036.65 (10.3%); £3,771,632.33 -> £3,382,036.76 (10.3%); £3,771,632.54 -> £3,382,037.07 (10.3%); £3,771,632.74 -> £3,382,037.37 (10.3%); £3,771,633.02 -> £3,382,037.63 (10.3%); £3,771,633.22 -> £3,382,037.87 (10.3%); £3,771,633.42 -> £3,382,038.11 (10.3%); £3,771,633.63 -> £3,382,038.35 (10.3%); £3,771,633.90 -> £3,382,038.59 (10.3%); £3,771,634.18 -> £3,382,038.83 (10.3%); £3,771,634.44 -> £3,382,039.06 (10.3%); £3,771,634.72 -> £3,382,039.29 (10.3%); £3,771,634.99 -> £3,382,039.50 (10.3%); £3,771,635.27 -> £3,382,039.54 (10.3%); £3,771,635.55 -> £3,382,039.58 (10.3%); £3,771,635.81 -> £3,382,039.62 (10.3%); £3,771,636.05 -> £3,382,039.66 (10.3%); £3,771,636.26 -> £3,382,039.69 (10.3%); £3,771,636.43 -> £3,382,039.73 (10.3%); £3,771,636.59 -> £3,382,039.77 (10.3%); £3,771,636.76 -> £3,382,039.81 (10.3%); £3,771,636.92 -> £3,382,039.84 (10.3%); £3,771,637.09 -> £3,382,039.88 (10.3%); £3,771,637.26 -> £3,382,039.92 (10.3%); £3,771,637.42 -> £3,382,039.95 (10.3%); £3,771,637.59 -> £3,382,039.99 (10.3%); £3,771,637.75 -> £3,382,040.03 (10.3%); £3,771,637.91 -> £3,382,040.07 (10.3%); £3,771,638.07 -> £3,382,040.11 (10.3%); £3,771,638.24 -> £3,382,040.35 (10.3%); £3,771,638.40 -> £3,382,040.59 (10.3%); £3,771,638.59 -> £3,382,040.84 (10.3%); £3,771,638.79 -> £3,382,041.11 (10.3%); £3,771,639.01 -> £3,382,041.41 (10.3%); £3,771,639.25 -> £3,382,041.73 (10.3%); £3,771,639.51 -> £3,382,042.07 (10.3%); £3,771,639.79 -> £3,382,042.41 (10.3%); £3,771,640.06 -> £3,382,042.53 (10.3%); £3,771,640.34 -> £3,382,042.65 (10.3%); £3,771,640.61 -> £3,382,042.78 (10.3%); £3,771,640.89 -> £3,382,042.91 (10.3%); £3,771,641.17 -> £3,382,043.03 (10.3%); £3,771,641.43 -> £3,382,043.16 (10.3%); £3,771,641.71 -> £3,382,043.27 (10.3%); £3,771,641.99 -> £3,382,043.38 (10.3%); £3,771,642.26 -> £3,382,043.49 (10.3%); £3,771,642.53 -> £3,382,043.61 (10.3%); £3,771,642.81 -> £3,382,043.72 (10.3%); £3,771,643.08 -> £3,382,043.83 (10.3%); £3,771,643.35 -> £3,382,043.94 (10.3%); £3,771,643.55 -> £3,382,044.27 (10.3%); £3,771,643.84 -> £3,382,044.58 (10.3%); £3,771,644.04 -> £3,382,044.87 (10.3%); £3,771,644.31 -> £3,382,045.14 (10.3%); £3,771,644.58 -> £3,382,045.40 (10.3%); £3,771,644.85 -> £3,382,045.65 (10.3%); £3,771,645.12 -> £3,382,045.91 (10.3%); £3,771,645.40 -> £3,382,046.15 (10.3%); £3,771,645.68 -> £3,382,046.39 (10.3%); £3,771,645.96 -> £3,382,046.62 (10.3%); £3,771,646.23 -> £3,382,046.86 (10.3%); £3,771,646.52 -> £3,382,046.90 (10.3%); £3,771,646.79 -> £3,382,046.94 (10.3%); £3,771,647.04 -> £3,382,046.98 (10.3%); £3,771,647.28 -> £3,382,047.02 (10.3%); £3,771,647.49 -> £3,382,047.06 (10.3%); £3,771,647.66 -> £3,382,047.09 (10.3%); £3,771,647.82 -> £3,382,047.13 (10.3%); £3,771,647.99 -> £3,382,047.17 (10.3%); £3,771,648.15 -> £3,382,047.20 (10.3%); £3,771,648.31 -> £3,382,047.24 (10.3%); £3,771,648.48 -> £3,382,047.28 (10.3%); £3,771,648.64 -> £3,382,047.31 (10.3%); £3,771,648.80 -> £3,382,047.35 (10.3%); £3,771,648.97 -> £3,382,047.39 (10.3%); £3,771,649.13 -> £3,382,047.43 (10.3%); £3,771,649.29 -> £3,382,047.47 (10.3%); £3,771,649.47 -> £3,382,047.66 (10.3%); £3,771,649.63 -> £3,382,047.86 (10.3%); £3,771,649.81 -> £3,382,048.06 (10.3%); £3,771,650.01 -> £3,382,048.28 (10.3%); £3,771,650.23 -> £3,382,048.52 (10.3%); £3,771,650.45 -> £3,382,048.78 (10.3%); £3,771,650.71 -> £3,382,049.07 (10.3%); £3,771,650.98 -> £3,382,049.37 (10.3%); £3,771,651.25 -> £3,382,049.50 (10.3%); £3,771,651.53 -> £3,382,049.64 (10.3%); £3,771,651.79 -> £3,382,049.77 (10.3%); £3,771,652.07 -> £3,382,049.91 (10.3%); £3,771,652.33 -> £3,382,050.05 (10.3%); £3,771,652.59 -> £3,382,050.18 (10.3%); £3,771,652.86 -> £3,382,050.31 (10.3%); £3,771,653.12 -> £3,382,050.44 (10.3%); £3,771,653.40 -> £3,382,050.55 (10.3%); £3,771,653.69 -> £3,382,050.67 (10.3%); £3,771,653.95 -> £3,382,050.79 (10.3%); £3,771,654.23 -> £3,382,050.90 (10.3%); £3,771,654.49 -> £3,382,051.01 (10.3%); £3,771,654.76 -> £3,382,051.30 (10.3%); £3,771,655.03 -> £3,382,051.58 (10.3%); £3,771,655.31 -> £3,382,051.82 (10.3%); £3,771,655.59 -> £3,382,052.04 (10.3%); £3,771,655.86 -> £3,382,052.24 (10.3%); £3,771,656.06 -> £3,382,052.45 (10.3%); £3,771,656.27 -> £3,382,052.65 (10.3%); £3,771,656.54 -> £3,382,052.84 (10.3%); £3,771,656.81 -> £3,382,053.04 (10.3%); £3,771,657.07 -> £3,382,053.24 (10.3%); £3,771,657.34 -> £3,382,053.42 (10.3%); £3,771,657.62 -> £3,382,053.46 (10.3%); £3,771,657.88 -> £3,382,053.50 (10.3%); £3,771,658.13 -> £3,382,053.54 (10.3%); £3,771,658.37 -> £3,382,053.58 (10.3%); £3,771,658.58 -> £3,382,053.62 (10.3%); £3,771,658.73 -> £3,382,053.65 (10.3%); £3,771,658.87 -> £3,382,053.69 (10.3%); £3,771,659.02 -> £3,382,053.73 (10.3%); £3,771,659.16 -> £3,382,053.77 (10.3%); £3,771,659.30 -> £3,382,053.80 (10.3%); £3,771,659.44 -> £3,382,053.84 (10.3%); £3,771,659.58 -> £3,382,053.87 (10.3%); £3,771,659.72 -> £3,382,053.91 (10.3%); £3,771,659.86 -> £3,382,053.95 (10.3%); £3,771,660.01 -> £3,382,053.98 (10.3%); £3,771,660.15 -> £3,382,054.02 (10.3%); £3,771,660.29 -> £3,382,054.20 (10.3%); £3,771,660.44 -> £3,382,054.38 (10.3%); £3,771,660.60 -> £3,382,054.56 (10.3%); £3,771,660.78 -> £3,382,054.75 (10.3%); £3,771,660.97 -> £3,382,054.95 (10.3%); £3,771,661.18 -> £3,382,055.17 (10.3%); £3,771,661.40 -> £3,382,055.41 (10.3%); £3,771,661.63 -> £3,382,055.66 (10.3%); £3,771,661.87 -> £3,382,055.75 (10.3%); £3,771,662.11 -> £3,382,055.84 (10.3%); £3,771,662.35 -> £3,382,055.93 (10.3%); £3,771,662.60 -> £3,382,056.02 (10.3%); £3,771,662.83 -> £3,382,056.11 (10.3%); £3,771,663.06 -> £3,382,056.19 (10.3%); £3,771,663.30 -> £3,382,056.26 (10.3%); £3,771,663.54 -> £3,382,056.33 (10.3%); £3,771,663.78 -> £3,382,056.41 (10.3%); £3,771,664.02 -> £3,382,056.47 (10.3%); £3,771,664.26 -> £3,382,056.54 (10.3%); £3,771,664.49 -> £3,382,056.61 (10.3%); £3,771,664.74 -> £3,382,056.68 (10.3%); £3,771,664.98 -> £3,382,056.90 (10.3%); £3,771,665.21 -> £3,382,057.12 (10.3%); £3,771,665.45 -> £3,382,057.31 (10.3%); £3,771,665.63 -> £3,382,057.50 (10.3%); £3,771,665.86 -> £3,382,057.69 (10.3%); £3,771,666.04 -> £3,382,057.87 (10.3%); £3,771,666.22 -> £3,382,058.06 (10.3%); £3,771,666.47 -> £3,382,058.25 (10.3%); £3,771,666.71 -> £3,382,058.44 (10.3%); £3,771,666.95 -> £3,382,058.63 (10.3%); £3,771,667.19 -> £3,382,058.81 (10.3%); £3,771,667.43 -> £3,382,058.85 (10.3%); £3,771,667.67 -> £3,382,058.89 (10.3%); £3,771,667.89 -> £3,382,058.93 (10.3%); £3,771,668.10 -> £3,382,058.97 (10.3%); £3,771,668.29 -> £3,382,059.01 (10.3%); £3,771,668.43 -> £3,382,059.04 (10.3%); £3,771,668.57 -> £3,382,059.08 (10.3%); £3,771,668.70 -> £3,382,059.12 (10.3%); £3,771,668.84 -> £3,382,059.16 (10.3%); £3,771,668.98 -> £3,382,059.19 (10.3%); £3,771,669.13 -> £3,382,059.23 (10.3%); £3,771,669.27 -> £3,382,059.27 (10.3%); £3,771,669.41 -> £3,382,059.30 (10.3%); £3,771,669.55 -> £3,382,059.34 (10.3%); £3,771,669.69 -> £3,382,059.37 (10.3%); £3,771,669.83 -> £3,382,059.41 (10.3%); £3,771,669.97 -> £3,382,059.60 (10.3%); £3,771,670.10 -> £3,382,059.79 (10.3%); £3,771,670.26 -> £3,382,059.97 (10.3%); £3,771,670.42 -> £3,382,060.16 (10.3%); £3,771,670.61 -> £3,382,060.35 (10.3%); £3,771,670.82 -> £3,382,060.54 (10.3%); £3,771,671.04 -> £3,382,060.74 (10.3%); £3,771,671.28 -> £3,382,060.94 (10.3%); £3,771,671.51 -> £3,382,060.99 (10.3%); £3,771,671.75 -> £3,382,061.03 (10.3%); £3,771,671.98 -> £3,382,061.08 (10.3%); £3,771,672.21 -> £3,382,061.13 (10.3%); £3,771,672.45 -> £3,382,061.18 (10.3%); £3,771,672.69 -> £3,382,061.23 (10.3%); £3,771,672.92 -> £3,382,061.28 (10.3%); £3,771,673.16 -> £3,382,061.32 (10.3%); £3,771,673.39 -> £3,382,061.37 (10.3%); £3,771,673.63 -> £3,382,061.42 (10.3%); £3,771,673.86 -> £3,382,061.46 (10.3%); £3,771,674.09 -> £3,382,061.51 (10.3%); £3,771,674.32 -> £3,382,061.56 (10.3%); £3,771,674.56 -> £3,382,061.75 (10.3%); £3,771,674.79 -> £3,382,061.94 (10.3%); £3,771,674.97 -> £3,382,062.13 (10.3%); £3,771,675.14 -> £3,382,062.32 (10.3%); £3,771,675.32 -> £3,382,062.50 (10.3%); £3,771,675.50 -> £3,382,062.69 (10.3%); £3,771,675.68 -> £3,382,062.89 (10.3%); £3,771,675.91 -> £3,382,063.08 (10.3%); £3,771,676.14 -> £3,382,063.27 (10.3%); £3,771,676.37 -> £3,382,063.46 (10.3%); £3,771,676.61 -> £3,382,063.64 (10.3%); £3,771,676.84 -> £3,382,063.68 (10.3%); £3,771,677.08 -> £3,382,063.71 (10.3%); £3,771,677.30 -> £3,382,063.75 (10.3%); £3,771,677.50 -> £3,382,063.79 (10.3%); £3,771,677.68 -> £3,382,063.82 (10.3%); £3,771,677.84 -> £3,382,063.86 (10.3%); £3,771,677.99 -> £3,382,063.90 (10.3%); £3,771,678.15 -> £3,382,063.94 (10.3%); £3,771,678.30 -> £3,382,063.97 (10.3%); £3,771,678.46 -> £3,382,064.01 (10.3%); £3,771,678.61 -> £3,382,064.05 (10.3%); £3,771,678.77 -> £3,382,064.08 (10.3%); £3,771,678.93 -> £3,382,064.12 (10.3%); £3,771,679.08 -> £3,382,064.16 (10.3%); £3,771,679.23 -> £3,382,064.20 (10.3%); £3,771,679.39 -> £3,382,064.24 (10.3%); £3,771,679.54 -> £3,382,064.45 (10.3%); £3,771,679.70 -> £3,382,064.67 (10.3%); £3,771,679.87 -> £3,382,064.90 (10.3%); £3,771,680.06 -> £3,382,065.13 (10.3%); £3,771,680.28 -> £3,382,065.38 (10.3%); £3,771,680.50 -> £3,382,065.67 (10.3%); £3,771,680.74 -> £3,382,065.98 (10.3%); £3,771,681.00 -> £3,382,066.30 (10.3%); £3,771,681.26 -> £3,382,066.43 (10.3%); £3,771,681.51 -> £3,382,066.55 (10.3%); £3,771,681.77 -> £3,382,066.68 (10.3%); £3,771,682.03 -> £3,382,066.81 (10.3%); £3,771,682.29 -> £3,382,066.94 (10.3%); £3,771,682.55 -> £3,382,067.07 (10.3%); £3,771,682.81 -> £3,382,067.18 (10.3%); £3,771,683.07 -> £3,382,067.30 (10.3%); £3,771,683.33 -> £3,382,067.42 (10.3%); £3,771,683.59 -> £3,382,067.54 (10.3%); £3,771,683.84 -> £3,382,067.65 (10.3%); £3,771,684.11 -> £3,382,067.77 (10.3%); £3,771,684.37 -> £3,382,067.87 (10.3%); £3,771,684.57 -> £3,382,068.17 (10.3%); £3,771,684.76 -> £3,382,068.45 (10.3%); £3,771,684.95 -> £3,382,068.70 (10.3%); £3,771,685.14 -> £3,382,068.93 (10.3%); £3,771,685.34 -> £3,382,069.15 (10.3%); £3,771,685.53 -> £3,382,069.37 (10.3%); £3,771,685.72 -> £3,382,069.58 (10.3%); £3,771,685.99 -> £3,382,069.79 (10.3%); £3,771,686.24 -> £3,382,070.01 (10.3%); £3,771,686.50 -> £3,382,070.21 (10.3%); £3,771,686.76 -> £3,382,070.42 (10.3%); £3,771,687.02 -> £3,382,070.46 (10.3%); £3,771,687.28 -> £3,382,070.50 (10.3%); £3,771,687.52 -> £3,382,070.54 (10.3%); £3,771,687.74 -> £3,382,070.58 (10.3%); £3,771,687.94 -> £3,382,070.61 (10.3%); £3,771,688.10 -> £3,382,070.65 (10.3%); £3,771,688.26 -> £3,382,070.69 (10.3%); £3,771,688.42 -> £3,382,070.73 (10.3%); £3,771,688.58 -> £3,382,070.76 (10.3%); £3,771,688.73 -> £3,382,070.80 (10.3%); £3,771,688.89 -> £3,382,070.83 (10.3%); £3,771,689.04 -> £3,382,070.87 (10.3%); £3,771,689.19 -> £3,382,070.91 (10.3%); £3,771,689.35 -> £3,382,070.95 (10.3%); £3,771,689.51 -> £3,382,070.99 (10.3%); £3,771,689.66 -> £3,382,071.03 (10.3%); £3,771,689.82 -> £3,382,071.21 (10.3%); £3,771,689.98 -> £3,382,071.39 (10.3%); £3,771,690.15 -> £3,382,071.59 (10.3%); £3,771,690.34 -> £3,382,071.80 (10.3%); £3,771,690.56 -> £3,382,072.03 (10.3%); £3,771,690.79 -> £3,382,072.28 (10.3%); £3,771,691.02 -> £3,382,072.56 (10.3%); £3,771,691.28 -> £3,382,072.85 (10.3%); £3,771,691.54 -> £3,382,072.97 (10.3%); £3,771,691.79 -> £3,382,073.10 (10.3%); £3,771,692.05 -> £3,382,073.23 (10.3%); £3,771,692.31 -> £3,382,073.36 (10.3%); £3,771,692.57 -> £3,382,073.48 (10.3%); £3,771,692.83 -> £3,382,073.61 (10.3%); £3,771,693.09 -> £3,382,073.73 (10.3%); £3,771,693.36 -> £3,382,073.85 (10.3%); £3,771,693.62 -> £3,382,073.96 (10.3%); £3,771,693.88 -> £3,382,074.08 (10.3%); £3,771,694.14 -> £3,382,074.20 (10.3%); £3,771,694.39 -> £3,382,074.31 (10.3%); £3,771,694.65 -> £3,382,074.42 (10.3%); £3,771,694.90 -> £3,382,074.71 (10.3%); £3,771,695.17 -> £3,382,074.97 (10.3%); £3,771,695.42 -> £3,382,075.21 (10.3%); £3,771,695.69 -> £3,382,075.42 (10.3%); £3,771,695.94 -> £3,382,075.63 (10.3%); £3,771,696.19 -> £3,382,075.83 (10.3%); £3,771,696.45 -> £3,382,076.03 (10.3%); £3,771,696.71 -> £3,382,076.22 (10.3%); £3,771,696.97 -> £3,382,076.41 (10.3%); £3,771,697.23 -> £3,382,076.60 (10.3%); £3,771,697.49 -> £3,382,076.77 (10.3%); £3,771,697.76 -> £3,382,076.81 (10.3%); £3,771,698.02 -> £3,382,076.85 (10.3%); £3,771,698.26 -> £3,382,076.89 (10.3%); £3,771,698.48 -> £3,382,076.93 (10.3%); £3,771,698.68 -> £3,382,076.96 (10.3%); £3,771,698.84 -> £3,382,077.00 (10.3%); £3,771,698.99 -> £3,382,077.04 (10.3%); £3,771,699.15 -> £3,382,077.08 (10.3%); £3,771,699.30 -> £3,382,077.11 (10.3%); £3,771,699.45 -> £3,382,077.15 (10.3%); £3,771,699.60 -> £3,382,077.19 (10.3%); £3,771,699.76 -> £3,382,077.23 (10.3%); £3,771,699.91 -> £3,382,077.26 (10.3%); £3,771,700.07 -> £3,382,077.30 (10.3%); £3,771,700.23 -> £3,382,077.34 (10.3%); £3,771,700.38 -> £3,382,077.38 (10.3%); £3,771,700.54 -> £3,382,077.50 (10.3%); £3,771,700.70 -> £3,382,077.63 (10.3%); £3,771,700.88 -> £3,382,077.77 (10.3%); £3,771,701.07 -> £3,382,077.92 (10.3%); £3,771,701.28 -> £3,382,078.09 (10.3%); £3,771,701.50 -> £3,382,078.29 (10.3%); £3,771,701.74 -> £3,382,078.50 (10.3%); £3,771,702.00 -> £3,382,078.73 (10.3%); £3,771,702.26 -> £3,382,078.86 (10.3%); £3,771,702.52 -> £3,382,078.99 (10.3%); £3,771,702.78 -> £3,382,079.12 (10.3%); £3,771,703.04 -> £3,382,079.25 (10.3%); £3,771,703.30 -> £3,382,079.38 (10.3%); £3,771,703.54 -> £3,382,079.50 (10.3%); £3,771,703.79 -> £3,382,079.61 (10.3%); £3,771,704.06 -> £3,382,079.73 (10.3%); £3,771,704.32 -> £3,382,079.85 (10.3%); £3,771,704.58 -> £3,382,079.96 (10.3%); £3,771,704.84 -> £3,382,080.08 (10.3%); £3,771,705.10 -> £3,382,080.19 (10.3%); £3,771,705.37 -> £3,382,080.30 (10.3%); £3,771,705.62 -> £3,382,080.52 (10.3%); £3,771,705.81 -> £3,382,080.72 (10.3%); £3,771,706.01 -> £3,382,080.89 (10.3%); £3,771,706.20 -> £3,382,081.05 (10.3%); £3,771,706.46 -> £3,382,081.19 (10.3%); £3,771,706.71 -> £3,382,081.34 (10.3%); £3,771,706.96 -> £3,382,081.48 (10.3%); £3,771,707.23 -> £3,382,081.62 (10.3%); £3,771,707.50 -> £3,382,081.76 (10.3%); £3,771,707.76 -> £3,382,081.88 (10.3%); £3,771,708.02 -> £3,382,082.01 (10.3%); £3,771,708.27 -> £3,382,082.05 (10.3%); £3,771,708.53 -> £3,382,082.09 (10.3%); £3,771,708.77 -> £3,382,082.13 (10.3%); £3,771,708.99 -> £3,382,082.17 (10.3%); £3,771,709.19 -> £3,382,082.21 (10.3%); £3,771,709.35 -> £3,382,082.24 (10.3%); £3,771,709.50 -> £3,382,082.28 (10.3%); £3,771,709.66 -> £3,382,082.32 (10.3%); £3,771,709.81 -> £3,382,082.36 (10.3%); £3,771,709.97 -> £3,382,082.39 (10.3%); £3,771,710.12 -> £3,382,082.43 (10.3%); £3,771,710.28 -> £3,382,082.47 (10.3%); £3,771,710.45 -> £3,382,082.51 (10.3%); £3,771,710.61 -> £3,382,082.55 (10.3%); £3,771,710.77 -> £3,382,082.58 (10.3%); £3,771,710.92 -> £3,382,082.62 (10.3%); £3,771,711.08 -> £3,382,082.72 (10.3%); £3,771,711.23 -> £3,382,082.82 (10.3%); £3,771,711.40 -> £3,382,082.93 (10.3%); £3,771,711.59 -> £3,382,083.06 (10.3%); £3,771,711.81 -> £3,382,083.21 (10.3%); £3,771,712.03 -> £3,382,083.38 (10.3%); £3,771,712.28 -> £3,382,083.57 (10.3%); £3,771,712.54 -> £3,382,083.78 (10.3%); £3,771,712.81 -> £3,382,083.90 (10.3%); £3,771,713.07 -> £3,382,084.03 (10.3%); £3,771,713.34 -> £3,382,084.16 (10.3%); £3,771,713.60 -> £3,382,084.29 (10.3%); £3,771,713.86 -> £3,382,084.42 (10.3%); £3,771,714.12 -> £3,382,084.55 (10.3%); £3,771,714.38 -> £3,382,084.67 (10.3%); £3,771,714.65 -> £3,382,084.78 (10.3%); £3,771,714.91 -> £3,382,084.90 (10.3%); £3,771,715.16 -> £3,382,085.02 (10.3%); £3,771,715.41 -> £3,382,085.13 (10.3%); £3,771,715.68 -> £3,382,085.24 (10.3%); £3,771,715.94 -> £3,382,085.35 (10.3%); £3,771,716.19 -> £3,382,085.55 (10.3%); £3,771,716.46 -> £3,382,085.74 (10.3%); £3,771,716.72 -> £3,382,085.89 (10.3%); £3,771,716.97 -> £3,382,086.03 (10.3%); £3,771,717.24 -> £3,382,086.15 (10.3%); £3,771,717.50 -> £3,382,086.27 (10.3%); £3,771,717.77 -> £3,382,086.39 (10.3%); £3,771,718.02 -> £3,382,086.51 (10.3%); £3,771,718.28 -> £3,382,086.62 (10.3%); £3,771,718.53 -> £3,382,086.72 (10.3%); £3,771,718.79 -> £3,382,086.82 (10.3%); £3,771,719.04 -> £3,382,086.86 (10.3%); £3,771,719.30 -> £3,382,086.90 (10.3%); £3,771,719.54 -> £3,382,086.94 (10.3%); £3,771,719.76 -> £3,382,086.98 (10.3%); £3,771,719.97 -> £3,382,087.01 (10.3%); £3,771,720.12 -> £3,382,087.05 (10.3%); £3,771,720.28 -> £3,382,087.09 (10.3%); £3,771,720.43 -> £3,382,087.12 (10.3%); £3,771,720.59 -> £3,382,087.16 (10.3%); £3,771,720.75 -> £3,382,087.20 (10.3%); £3,771,720.91 -> £3,382,087.24 (10.3%); £3,771,721.07 -> £3,382,087.27 (10.3%); £3,771,721.22 -> £3,382,087.31 (10.3%); £3,771,721.38 -> £3,382,087.35 (10.3%); £3,771,721.55 -> £3,382,087.39 (10.3%); £3,771,721.70 -> £3,382,087.43 (10.3%); £3,771,721.86 -> £3,382,087.57 (10.3%); £3,771,722.02 -> £3,382,087.71 (10.3%); £3,771,722.20 -> £3,382,087.86 (10.3%); £3,771,722.39 -> £3,382,088.03 (10.3%); £3,771,722.61 -> £3,382,088.22 (10.3%); £3,771,722.83 -> £3,382,088.42 (10.3%); £3,771,723.08 -> £3,382,088.65 (10.3%); £3,771,723.35 -> £3,382,088.88 (10.3%); £3,771,723.61 -> £3,382,089.01 (10.3%); £3,771,723.88 -> £3,382,089.14 (10.3%); £3,771,724.13 -> £3,382,089.27 (10.3%); £3,771,724.38 -> £3,382,089.40 (10.3%); £3,771,724.65 -> £3,382,089.52 (10.3%); £3,771,724.91 -> £3,382,089.64 (10.3%); £3,771,725.16 -> £3,382,089.76 (10.3%); £3,771,725.42 -> £3,382,089.87 (10.3%); £3,771,725.68 -> £3,382,089.98 (10.3%); £3,771,725.94 -> £3,382,090.10 (10.3%); £3,771,726.20 -> £3,382,090.21 (10.3%); £3,771,726.47 -> £3,382,090.32 (10.3%); £3,771,726.72 -> £3,382,090.42 (10.3%); £3,771,726.92 -> £3,382,090.66 (10.3%); £3,771,727.20 -> £3,382,090.88 (10.3%); £3,771,727.39 -> £3,382,091.06 (10.3%); £3,771,727.58 -> £3,382,091.22 (10.3%); £3,771,727.78 -> £3,382,091.38 (10.3%); £3,771,727.97 -> £3,382,091.53 (10.3%); £3,771,728.16 -> £3,382,091.68 (10.3%); £3,771,728.42 -> £3,382,091.82 (10.3%); £3,771,728.68 -> £3,382,091.96 (10.3%); £3,771,728.94 -> £3,382,092.11 (10.3%); £3,771,729.21 -> £3,382,092.24 (10.3%); £3,771,729.48 -> £3,382,092.29 (10.3%); £3,771,729.75 -> £3,382,092.33 (10.3%); £3,771,729.99 -> £3,382,092.37 (10.3%); £3,771,730.21 -> £3,382,092.40 (10.3%); £3,771,730.41 -> £3,382,092.44 (10.3%); £3,771,730.54 -> £3,382,092.48 (10.3%); £3,771,730.69 -> £3,382,092.52 (10.3%); £3,771,730.82 -> £3,382,092.55 (10.3%); £3,771,730.96 -> £3,382,092.59 (10.3%); £3,771,731.10 -> £3,382,092.63 (10.3%); £3,771,731.24 -> £3,382,092.67 (10.3%); £3,771,731.37 -> £3,382,092.70 (10.3%); £3,771,731.52 -> £3,382,092.74 (10.3%); £3,771,731.65 -> £3,382,092.78 (10.3%); £3,771,731.79 -> £3,382,092.82 (10.3%); £3,771,731.92 -> £3,382,092.86 (10.3%); £3,771,732.06 -> £3,382,092.97 (10.3%); £3,771,732.20 -> £3,382,093.09 (10.3%); £3,771,732.36 -> £3,382,093.22 (10.3%); £3,771,732.53 -> £3,382,093.34 (10.3%); £3,771,732.71 -> £3,382,093.48 (10.3%); £3,771,732.91 -> £3,382,093.62 (10.3%); £3,771,733.12 -> £3,382,093.80 (10.3%); £3,771,733.34 -> £3,382,093.98 (10.3%); £3,771,733.57 -> £3,382,094.07 (10.3%); £3,771,733.79 -> £3,382,094.16 (10.3%); £3,771,734.01 -> £3,382,094.26 (10.3%); £3,771,734.24 -> £3,382,094.35 (10.3%); £3,771,734.48 -> £3,382,094.43 (10.3%); £3,771,734.71 -> £3,382,094.51 (10.3%); £3,771,734.94 -> £3,382,094.59 (10.3%); £3,771,735.16 -> £3,382,094.66 (10.3%); £3,771,735.38 -> £3,382,094.73 (10.3%); £3,771,735.61 -> £3,382,094.80 (10.3%); £3,771,735.84 -> £3,382,094.87 (10.3%); £3,771,736.07 -> £3,382,094.94 (10.3%); £3,771,736.29 -> £3,382,095.00 (10.3%); £3,771,736.46 -> £3,382,095.16 (10.3%); £3,771,736.64 -> £3,382,095.31 (10.3%); £3,771,736.81 -> £3,382,095.45 (10.3%); £3,771,736.98 -> £3,382,095.58 (10.3%); £3,771,737.15 -> £3,382,095.71 (10.3%); £3,771,737.33 -> £3,382,095.84 (10.3%); £3,771,737.49 -> £3,382,095.97 (10.3%); £3,771,737.72 -> £3,382,096.09 (10.3%); £3,771,737.95 -> £3,382,096.22 (10.3%); £3,771,738.18 -> £3,382,096.35 (10.3%); £3,771,738.41 -> £3,382,096.47 (10.3%); £3,771,738.63 -> £3,382,096.51 (10.3%); £3,771,738.87 -> £3,382,096.55 (10.3%); £3,771,739.08 -> £3,382,096.59 (10.3%); £3,771,739.27 -> £3,382,096.62 (10.3%); £3,771,739.44 -> £3,382,096.66 (10.3%); £3,771,739.58 -> £3,382,096.70 (10.3%); £3,771,739.72 -> £3,382,096.74 (10.3%); £3,771,739.86 -> £3,382,096.78 (10.3%); £3,771,740.00 -> £3,382,096.81 (10.3%); £3,771,740.14 -> £3,382,096.85 (10.3%); £3,771,740.27 -> £3,382,096.89 (10.3%); £3,771,740.41 -> £3,382,096.92 (10.3%); £3,771,740.55 -> £3,382,096.96 (10.3%); £3,771,740.69 -> £3,382,096.99 (10.3%); £3,771,740.83 -> £3,382,097.03 (10.3%); £3,771,740.96 -> £3,382,097.07 (10.3%); £3,771,741.10 -> £3,382,097.18 (10.3%); £3,771,741.24 -> £3,382,097.30 (10.3%); £3,771,741.40 -> £3,382,097.41 (10.3%); £3,771,741.56 -> £3,382,097.53 (10.3%); £3,771,741.75 -> £3,382,097.65 (10.3%); £3,771,741.94 -> £3,382,097.77 (10.3%); £3,771,742.16 -> £3,382,097.89 (10.3%); £3,771,742.39 -> £3,382,098.02 (10.3%); £3,771,742.62 -> £3,382,098.07 (10.3%); £3,771,742.85 -> £3,382,098.11 (10.3%); £3,771,743.08 -> £3,382,098.16 (10.3%); £3,771,743.31 -> £3,382,098.21 (10.3%); £3,771,743.54 -> £3,382,098.26 (10.3%); £3,771,743.76 -> £3,382,098.31 (10.3%); £3,771,744.00 -> £3,382,098.36 (10.3%); £3,771,744.22 -> £3,382,098.41 (10.3%); £3,771,744.45 -> £3,382,098.45 (10.3%); £3,771,744.68 -> £3,382,098.50 (10.3%); £3,771,744.92 -> £3,382,098.55 (10.3%); £3,771,745.15 -> £3,382,098.59 (10.3%); £3,771,745.37 -> £3,382,098.64 (10.3%); £3,771,745.61 -> £3,382,098.77 (10.3%); £3,771,745.85 -> £3,382,098.90 (10.3%); £3,771,746.08 -> £3,382,099.03 (10.3%); £3,771,746.24 -> £3,382,099.16 (10.3%); £3,771,746.47 -> £3,382,099.29 (10.3%); £3,771,746.64 -> £3,382,099.42 (10.3%); £3,771,746.81 -> £3,382,099.55 (10.3%); £3,771,747.04 -> £3,382,099.68 (10.3%); £3,771,747.28 -> £3,382,099.80 (10.3%); £3,771,747.50 -> £3,382,099.93 (10.3%); £3,771,747.73 -> £3,382,100.05 (10.3%); £3,771,747.95 -> £3,382,100.09 (10.3%); £3,771,748.18 -> £3,382,100.13 (10.3%); £3,771,748.39 -> £3,382,100.17 (10.3%); £3,771,748.58 -> £3,382,100.21 (10.3%); £3,771,748.76 -> £3,382,100.24 (10.3%); £3,771,748.92 -> £3,382,100.28 (10.3%); £3,771,749.08 -> £3,382,100.32 (10.3%); £3,771,749.24 -> £3,382,100.36 (10.3%); £3,771,749.40 -> £3,382,100.40 (10.3%); £3,771,749.56 -> £3,382,100.44 (10.3%); £3,771,749.72 -> £3,382,100.48 (10.3%); £3,771,749.88 -> £3,382,100.51 (10.3%); £3,771,750.04 -> £3,382,100.55 (10.3%); £3,771,750.20 -> £3,382,100.59 (10.3%); £3,771,750.35 -> £3,382,100.63 (10.3%); £3,771,750.52 -> £3,382,100.67 (10.3%); £3,771,750.68 -> £3,382,100.83 (10.3%); £3,771,750.84 -> £3,382,100.99 (10.3%); £3,771,751.01 -> £3,382,101.16 (10.3%); £3,771,751.20 -> £3,382,101.35 (10.3%); £3,771,751.41 -> £3,382,101.55 (10.3%); £3,771,751.64 -> £3,382,101.78 (10.3%); £3,771,751.89 -> £3,382,102.02 (10.3%); £3,771,752.15 -> £3,382,102.28 (10.3%); £3,771,752.40 -> £3,382,102.41 (10.3%); £3,771,752.67 -> £3,382,102.54 (10.3%); £3,771,752.93 -> £3,382,102.66 (10.3%); £3,771,753.20 -> £3,382,102.80 (10.3%); £3,771,753.47 -> £3,382,102.93 (10.3%); £3,771,753.73 -> £3,382,103.05 (10.3%); £3,771,754.00 -> £3,382,103.16 (10.3%); £3,771,754.26 -> £3,382,103.28 (10.3%); £3,771,754.54 -> £3,382,103.40 (10.3%); £3,771,754.80 -> £3,382,103.52 (10.3%); £3,771,755.06 -> £3,382,103.64 (10.3%); £3,771,755.32 -> £3,382,103.75 (10.3%); £3,771,755.58 -> £3,382,103.86 (10.3%); £3,771,755.84 -> £3,382,104.11 (10.3%); £3,771,756.04 -> £3,382,104.35 (10.3%); £3,771,756.23 -> £3,382,104.55 (10.3%); £3,771,756.43 -> £3,382,104.74 (10.3%); £3,771,756.69 -> £3,382,104.92 (10.3%); £3,771,756.94 -> £3,382,105.10 (10.3%); £3,771,757.21 -> £3,382,105.27 (10.3%); £3,771,757.48 -> £3,382,105.44 (10.3%); £3,771,757.74 -> £3,382,105.61 (10.3%); £3,771,758.01 -> £3,382,105.77 (10.3%); £3,771,758.27 -> £3,382,105.93 (10.3%); £3,771,758.54 -> £3,382,105.97 (10.3%); £3,771,758.81 -> £3,382,106.01 (10.3%); £3,771,759.06 -> £3,382,106.05 (10.3%); £3,771,759.28 -> £3,382,106.09 (10.3%); £3,771,759.48 -> £3,382,106.12 (10.3%); £3,771,759.64 -> £3,382,106.16 (10.3%); £3,771,759.80 -> £3,382,106.20 (10.3%); £3,771,759.96 -> £3,382,106.24 (10.3%); £3,771,760.12 -> £3,382,106.27 (10.3%); £3,771,760.28 -> £3,382,106.31 (10.3%); £3,771,760.44 -> £3,382,106.35 (10.3%); £3,771,760.60 -> £3,382,106.39 (10.3%); £3,771,760.75 -> £3,382,106.43 (10.3%); £3,771,760.91 -> £3,382,106.46 (10.3%); £3,771,761.07 -> £3,382,106.50 (10.3%); £3,771,761.23 -> £3,382,106.54 (10.3%); £3,771,761.38 -> £3,382,106.69 (10.3%); £3,771,761.54 -> £3,382,106.84 (10.3%); £3,771,761.72 -> £3,382,107.00 (10.3%); £3,771,761.91 -> £3,382,107.18 (10.3%); £3,771,762.12 -> £3,382,107.38 (10.3%); £3,771,762.35 -> £3,382,107.60 (10.3%); £3,771,762.60 -> £3,382,107.84 (10.3%); £3,771,762.86 -> £3,382,108.10 (10.3%); £3,771,763.13 -> £3,382,108.22 (10.3%); £3,771,763.39 -> £3,382,108.35 (10.3%); £3,771,763.67 -> £3,382,108.48 (10.3%); £3,771,763.93 -> £3,382,108.61 (10.3%); £3,771,764.19 -> £3,382,108.74 (10.3%); £3,771,764.45 -> £3,382,108.87 (10.3%); £3,771,764.72 -> £3,382,108.99 (10.3%); £3,771,764.98 -> £3,382,109.12 (10.3%); £3,771,765.24 -> £3,382,109.24 (10.3%); £3,771,765.50 -> £3,382,109.36 (10.3%); £3,771,765.77 -> £3,382,109.48 (10.3%); £3,771,766.04 -> £3,382,109.59 (10.3%); £3,771,766.30 -> £3,382,109.70 (10.3%); £3,771,766.57 -> £3,382,109.96 (10.3%); £3,771,766.83 -> £3,382,110.19 (10.3%); £3,771,767.10 -> £3,382,110.40 (10.3%); £3,771,767.36 -> £3,382,110.58 (10.3%); £3,771,767.62 -> £3,382,110.76 (10.3%); £3,771,767.90 -> £3,382,110.92 (10.3%); £3,771,768.09 -> £3,382,111.08 (10.3%); £3,771,768.35 -> £3,382,111.25 (10.3%); £3,771,768.60 -> £3,382,111.40 (10.3%); £3,771,768.87 -> £3,382,111.56 (10.3%); £3,771,769.14 -> £3,382,111.71 (10.3%); £3,771,769.40 -> £3,382,111.75 (10.3%); £3,771,769.66 -> £3,382,111.79 (10.3%); £3,771,769.91 -> £3,382,111.83 (10.3%); £3,771,770.13 -> £3,382,111.87 (10.3%); £3,771,770.33 -> £3,382,111.91 (10.3%); £3,771,770.50 -> £3,382,111.94 (10.3%); £3,771,770.66 -> £3,382,111.98 (10.3%); £3,771,770.82 -> £3,382,112.02 (10.3%); £3,771,770.99 -> £3,382,112.06 (10.3%); £3,771,771.15 -> £3,382,112.10 (10.3%); £3,771,771.31 -> £3,382,112.13 (10.3%); £3,771,771.47 -> £3,382,112.17 (10.3%); £3,771,771.63 -> £3,382,112.21 (10.3%); £3,771,771.78 -> £3,382,112.25 (10.3%); £3,771,771.95 -> £3,382,112.29 (10.3%); £3,771,772.11 -> £3,382,112.33 (10.3%); £3,771,772.27 -> £3,382,112.48 (10.3%); £3,771,772.43 -> £3,382,112.62 (10.3%); £3,771,772.61 -> £3,382,112.78 (10.3%); £3,771,772.81 -> £3,382,112.95 (10.3%); £3,771,773.02 -> £3,382,113.14 (10.3%); £3,771,773.24 -> £3,382,113.35 (10.3%); £3,771,773.49 -> £3,382,113.59 (10.3%); £3,771,773.77 -> £3,382,113.83 (10.3%); £3,771,774.04 -> £3,382,113.96 (10.3%); £3,771,774.30 -> £3,382,114.09 (10.3%); £3,771,774.57 -> £3,382,114.21 (10.3%); £3,771,774.83 -> £3,382,114.34 (10.3%); £3,771,775.10 -> £3,382,114.47 (10.3%); £3,771,775.36 -> £3,382,114.59 (10.3%); £3,771,775.63 -> £3,382,114.71 (10.3%); £3,771,775.90 -> £3,382,114.82 (10.3%); £3,771,776.17 -> £3,382,114.94 (10.3%); £3,771,776.43 -> £3,382,115.06 (10.3%); £3,771,776.70 -> £3,382,115.18 (10.3%); £3,771,776.97 -> £3,382,115.29 (10.3%); £3,771,777.24 -> £3,382,115.40 (10.3%); £3,771,777.50 -> £3,382,115.64 (10.3%); £3,771,777.77 -> £3,382,115.86 (10.3%); £3,771,778.03 -> £3,382,116.05 (10.3%); £3,771,778.30 -> £3,382,116.22 (10.3%); £3,771,778.50 -> £3,382,116.38 (10.3%); £3,771,778.70 -> £3,382,116.54 (10.3%); £3,771,778.97 -> £3,382,116.70 (10.3%); £3,771,779.23 -> £3,382,116.86 (10.3%); £3,771,779.49 -> £3,382,117.01 (10.3%); £3,771,779.76 -> £3,382,117.15 (10.3%); £3,771,780.04 -> £3,382,117.31 (10.3%); £3,771,780.30 -> £3,382,117.35 (10.3%); £3,771,780.57 -> £3,382,117.39 (10.3%); £3,771,780.82 -> £3,382,117.43 (10.3%); £3,771,781.04 -> £3,382,117.47 (10.3%); £3,771,781.25 -> £3,382,117.51 (10.3%); £3,771,781.40 -> £3,382,117.55 (10.3%); £3,771,781.56 -> £3,382,117.58 (10.3%); £3,771,781.72 -> £3,382,117.62 (10.3%); £3,771,781.88 -> £3,382,117.66 (10.3%); £3,771,782.04 -> £3,382,117.70 (10.3%); £3,771,782.20 -> £3,382,117.74 (10.3%); £3,771,782.37 -> £3,382,117.77 (10.3%); £3,771,782.53 -> £3,382,117.81 (10.3%); £3,771,782.69 -> £3,382,117.85 (10.3%); £3,771,782.85 -> £3,382,117.89 (10.3%); £3,771,783.01 -> £3,382,117.93 (10.3%); £3,771,783.17 -> £3,382,118.11 (10.3%); £3,771,783.33 -> £3,382,118.30 (10.3%); £3,771,783.51 -> £3,382,118.49 (10.3%); £3,771,783.71 -> £3,382,118.69 (10.3%); £3,771,783.92 -> £3,382,118.92 (10.3%); £3,771,784.16 -> £3,382,119.17 (10.3%); £3,771,784.41 -> £3,382,119.43 (10.3%); £3,771,784.68 -> £3,382,119.71 (10.3%); £3,771,784.94 -> £3,382,119.83 (10.3%); £3,771,785.21 -> £3,382,119.96 (10.3%); £3,771,785.48 -> £3,382,120.08 (10.3%); £3,771,785.74 -> £3,382,120.20 (10.3%); £3,771,786.00 -> £3,382,120.33 (10.3%); £3,771,786.27 -> £3,382,120.45 (10.3%); £3,771,786.55 -> £3,382,120.56 (10.3%); £3,771,786.82 -> £3,382,120.67 (10.3%); £3,771,787.08 -> £3,382,120.78 (10.3%); £3,771,787.35 -> £3,382,120.90 (10.3%); £3,771,787.61 -> £3,382,121.01 (10.3%); £3,771,787.88 -> £3,382,121.12 (10.3%); £3,771,788.15 -> £3,382,121.23 (10.3%); £3,771,788.42 -> £3,382,121.51 (10.3%); £3,771,788.69 -> £3,382,121.78 (10.3%); £3,771,788.96 -> £3,382,122.02 (10.3%); £3,771,789.23 -> £3,382,122.22 (10.3%); £3,771,789.43 -> £3,382,122.43 (10.3%); £3,771,789.70 -> £3,382,122.63 (10.3%); £3,771,789.98 -> £3,382,122.83 (10.3%); £3,771,790.24 -> £3,382,123.02 (10.3%); £3,771,790.52 -> £3,382,123.21 (10.3%); £3,771,790.79 -> £3,382,123.39 (10.3%); £3,771,791.05 -> £3,382,123.56 (10.3%); £3,771,791.32 -> £3,382,123.61 (10.3%); £3,771,791.59 -> £3,382,123.65 (10.3%); £3,771,791.83 -> £3,382,123.69 (10.3%); £3,771,792.05 -> £3,382,123.73 (10.3%); £3,771,792.26 -> £3,382,123.76 (10.3%); £3,771,792.42 -> £3,382,123.80 (10.3%); £3,771,792.58 -> £3,382,123.84 (10.3%); £3,771,792.75 -> £3,382,123.87 (10.3%); £3,771,792.90 -> £3,382,123.91 (10.3%); £3,771,793.06 -> £3,382,123.95 (10.3%); £3,771,793.22 -> £3,382,123.99 (10.3%); £3,771,793.38 -> £3,382,124.02 (10.3%); £3,771,793.54 -> £3,382,124.06 (10.3%); £3,771,793.71 -> £3,382,124.10 (10.3%); £3,771,793.87 -> £3,382,124.14 (10.3%); £3,771,794.03 -> £3,382,124.18 (10.3%); £3,771,794.19 -> £3,382,124.40 (10.3%); £3,771,794.34 -> £3,382,124.63 (10.3%); £3,771,794.52 -> £3,382,124.88 (10.3%); £3,771,794.72 -> £3,382,125.14 (10.3%); £3,771,794.93 -> £3,382,125.41 (10.3%); £3,771,795.16 -> £3,382,125.71 (10.3%); £3,771,795.41 -> £3,382,126.04 (10.3%); £3,771,795.69 -> £3,382,126.37 (10.3%); £3,771,795.95 -> £3,382,126.50 (10.3%); £3,771,796.21 -> £3,382,126.63 (10.3%); £3,771,796.46 -> £3,382,126.75 (10.3%); £3,771,796.72 -> £3,382,126.88 (10.3%); £3,771,796.98 -> £3,382,127.01 (10.3%); £3,771,797.25 -> £3,382,127.13 (10.3%); £3,771,797.51 -> £3,382,127.24 (10.3%); £3,771,797.79 -> £3,382,127.36 (10.3%); £3,771,798.06 -> £3,382,127.48 (10.3%); £3,771,798.32 -> £3,382,127.60 (10.3%); £3,771,798.58 -> £3,382,127.71 (10.3%); £3,771,798.85 -> £3,382,127.83 (10.3%); £3,771,799.11 -> £3,382,127.94 (10.3%); £3,771,799.38 -> £3,382,128.26 (10.3%); £3,771,799.63 -> £3,382,128.55 (10.3%); £3,771,799.83 -> £3,382,128.82 (10.3%); £3,771,800.04 -> £3,382,129.06 (10.3%); £3,771,800.23 -> £3,382,129.30 (10.3%); £3,771,800.43 -> £3,382,129.53 (10.3%); £3,771,800.64 -> £3,382,129.76 (10.3%); £3,771,800.90 -> £3,382,129.98 (10.3%); £3,771,801.16 -> £3,382,130.20 (10.3%); £3,771,801.44 -> £3,382,130.42 (10.3%); £3,771,801.70 -> £3,382,130.63 (10.3%); £3,771,801.97 -> £3,382,130.67 (10.3%); £3,771,802.23 -> £3,382,130.72 (10.3%); £3,771,802.47 -> £3,382,130.76 (10.3%); £3,771,802.69 -> £3,382,130.79 (10.3%); £3,771,802.89 -> £3,382,130.83 (10.3%); £3,771,803.03 -> £3,382,130.87 (10.3%); £3,771,803.17 -> £3,382,130.90 (10.3%); £3,771,803.32 -> £3,382,130.94 (10.3%); £3,771,803.46 -> £3,382,130.98 (10.3%); £3,771,803.60 -> £3,382,131.01 (10.3%); £3,771,803.74 -> £3,382,131.05 (10.3%); £3,771,803.88 -> £3,382,131.09 (10.3%); £3,771,804.02 -> £3,382,131.12 (10.3%); £3,771,804.16 -> £3,382,131.16 (10.3%); £3,771,804.30 -> £3,382,131.20 (10.3%); £3,771,804.44 -> £3,382,131.24 (10.3%); £3,771,804.58 -> £3,382,131.47 (10.3%); £3,771,804.72 -> £3,382,131.71 (10.3%); £3,771,804.88 -> £3,382,131.95 (10.3%); £3,771,805.05 -> £3,382,132.19 (10.3%); £3,771,805.24 -> £3,382,132.44 (10.3%); £3,771,805.44 -> £3,382,132.70 (10.3%); £3,771,805.67 -> £3,382,132.98 (10.3%); £3,771,805.90 -> £3,382,133.27 (10.3%); £3,771,806.14 -> £3,382,133.36 (10.3%); £3,771,806.37 -> £3,382,133.45 (10.3%); £3,771,806.61 -> £3,382,133.54 (10.3%); £3,771,806.84 -> £3,382,133.64 (10.3%); £3,771,807.07 -> £3,382,133.72 (10.3%); £3,771,807.31 -> £3,382,133.80 (10.3%); £3,771,807.54 -> £3,382,133.87 (10.3%); £3,771,807.77 -> £3,382,133.95 (10.3%); £3,771,808.01 -> £3,382,134.02 (10.3%); £3,771,808.24 -> £3,382,134.09 (10.3%); £3,771,808.48 -> £3,382,134.16 (10.3%); £3,771,808.73 -> £3,382,134.23 (10.3%); £3,771,808.96 -> £3,382,134.29 (10.3%); £3,771,809.14 -> £3,382,134.55 (10.3%); £3,771,809.31 -> £3,382,134.80 (10.3%); £3,771,809.49 -> £3,382,135.04 (10.3%); £3,771,809.66 -> £3,382,135.27 (10.3%); £3,771,809.84 -> £3,382,135.50 (10.3%); £3,771,810.01 -> £3,382,135.73 (10.3%); £3,771,810.19 -> £3,382,135.96 (10.3%); £3,771,810.43 -> £3,382,136.18 (10.3%); £3,771,810.67 -> £3,382,136.41 (10.3%); £3,771,810.90 -> £3,382,136.63 (10.3%); £3,771,811.14 -> £3,382,136.85 (10.3%); £3,771,811.38 -> £3,382,136.89 (10.3%); £3,771,811.61 -> £3,382,136.93 (10.3%); £3,771,811.82 -> £3,382,136.97 (10.3%); £3,771,812.02 -> £3,382,137.01 (10.3%); £3,771,812.21 -> £3,382,137.05 (10.3%); £3,771,812.35 -> £3,382,137.08 (10.3%); £3,771,812.50 -> £3,382,137.12 (10.3%); £3,771,812.63 -> £3,382,137.16 (10.3%); £3,771,812.78 -> £3,382,137.20 (10.3%); £3,771,812.91 -> £3,382,137.23 (10.3%); £3,771,813.05 -> £3,382,137.27 (10.3%); £3,771,813.19 -> £3,382,137.31 (10.3%); £3,771,813.33 -> £3,382,137.34 (10.3%); £3,771,813.47 -> £3,382,137.38 (10.3%); £3,771,813.61 -> £3,382,137.41 (10.3%); £3,771,813.75 -> £3,382,137.45 (10.3%); £3,771,813.89 -> £3,382,137.66 (10.3%); £3,771,814.03 -> £3,382,137.87 (10.3%); £3,771,814.18 -> £3,382,138.09 (10.3%); £3,771,814.36 -> £3,382,138.30 (10.3%); £3,771,814.55 -> £3,382,138.52 (10.3%); £3,771,814.75 -> £3,382,138.74 (10.3%); £3,771,814.96 -> £3,382,138.96 (10.3%); £3,771,815.20 -> £3,382,139.19 (10.3%); £3,771,815.44 -> £3,382,139.24 (10.3%); £3,771,815.68 -> £3,382,139.29 (10.3%); £3,771,815.92 -> £3,382,139.34 (10.3%); £3,771,816.14 -> £3,382,139.39 (10.3%); £3,771,816.38 -> £3,382,139.44 (10.3%); £3,771,816.61 -> £3,382,139.48 (10.3%); £3,771,816.84 -> £3,382,139.53 (10.3%); £3,771,817.09 -> £3,382,139.58 (10.3%); £3,771,817.32 -> £3,382,139.62 (10.3%); £3,771,817.55 -> £3,382,139.67 (10.3%); £3,771,817.78 -> £3,382,139.71 (10.3%); £3,771,818.02 -> £3,382,139.76 (10.3%); £3,771,818.25 -> £3,382,139.80 (10.3%); £3,771,818.43 -> £3,382,140.02 (10.3%); £3,771,818.60 -> £3,382,140.23 (10.3%); £3,771,818.78 -> £3,382,140.44 (10.3%); £3,771,818.96 -> £3,382,140.65 (10.3%); £3,771,819.19 -> £3,382,140.88 (10.3%); £3,771,819.42 -> £3,382,141.09 (10.3%); £3,771,819.60 -> £3,382,141.31 (10.3%); £3,771,819.84 -> £3,382,141.52 (10.3%); £3,771,820.07 -> £3,382,141.74 (10.3%); £3,771,820.30 -> £3,382,141.95 (10.3%); £3,771,820.53 -> £3,382,142.17 (10.3%); £3,771,820.76 -> £3,382,142.21 (10.3%); £3,771,821.00 -> £3,382,142.25 (10.3%); £3,771,821.21 -> £3,382,142.28 (10.3%); £3,771,821.41 -> £3,382,142.32 (10.3%); £3,771,821.59 -> £3,382,142.36 (10.3%); £3,771,821.75 -> £3,382,142.39 (10.3%); £3,771,821.91 -> £3,382,142.43 (10.3%); £3,771,822.07 -> £3,382,142.47 (10.3%); £3,771,822.22 -> £3,382,142.51 (10.3%); £3,771,822.39 -> £3,382,142.55 (10.3%); £3,771,822.55 -> £3,382,142.58 (10.3%); £3,771,822.70 -> £3,382,142.62 (10.3%); £3,771,822.87 -> £3,382,142.66 (10.3%); £3,771,823.03 -> £3,382,142.70 (10.3%); £3,771,823.19 -> £3,382,142.74 (10.3%); £3,771,823.35 -> £3,382,142.78 (10.3%); £3,771,823.51 -> £3,382,142.98 (10.3%); £3,771,823.67 -> £3,382,143.19 (10.3%); £3,771,823.84 -> £3,382,143.40 (10.3%); £3,771,824.03 -> £3,382,143.63 (10.3%); £3,771,824.26 -> £3,382,143.89 (10.3%); £3,771,824.48 -> £3,382,144.16 (10.3%); £3,771,824.72 -> £3,382,144.46 (10.3%); £3,771,824.99 -> £3,382,144.76 (10.3%); £3,771,825.25 -> £3,382,144.88 (10.3%); £3,771,825.51 -> £3,382,145.01 (10.3%); £3,771,825.78 -> £3,382,145.13 (10.3%); £3,771,826.05 -> £3,382,145.26 (10.3%); £3,771,826.32 -> £3,382,145.39 (10.3%); £3,771,826.57 -> £3,382,145.51 (10.3%); £3,771,826.83 -> £3,382,145.63 (10.3%); £3,771,827.10 -> £3,382,145.75 (10.3%); £3,771,827.37 -> £3,382,145.87 (10.3%); £3,771,827.63 -> £3,382,145.99 (10.3%); £3,771,827.90 -> £3,382,146.10 (10.3%); £3,771,828.16 -> £3,382,146.22 (10.3%); £3,771,828.42 -> £3,382,146.33 (10.3%); £3,771,828.68 -> £3,382,146.63 (10.3%); £3,771,828.96 -> £3,382,146.92 (10.3%); £3,771,829.22 -> £3,382,147.17 (10.3%); £3,771,829.48 -> £3,382,147.40 (10.3%); £3,771,829.74 -> £3,382,147.62 (10.3%); £3,771,829.99 -> £3,382,147.83 (10.3%); £3,771,830.20 -> £3,382,148.05 (10.3%); £3,771,830.46 -> £3,382,148.26 (10.3%); £3,771,830.72 -> £3,382,148.47 (10.3%); £3,771,830.97 -> £3,382,148.67 (10.3%); £3,771,831.23 -> £3,382,148.87 (10.3%); £3,771,831.49 -> £3,382,148.91 (10.3%); £3,771,831.75 -> £3,382,148.95 (10.3%); £3,771,832.00 -> £3,382,148.99 (10.3%); £3,771,832.22 -> £3,382,149.03 (10.3%); £3,771,832.43 -> £3,382,149.07 (10.3%); £3,771,832.59 -> £3,382,149.11 (10.3%); £3,771,832.74 -> £3,382,149.14 (10.3%); £3,771,832.90 -> £3,382,149.18 (10.3%); £3,771,833.06 -> £3,382,149.22 (10.3%); £3,771,833.22 -> £3,382,149.26 (10.3%); £3,771,833.37 -> £3,382,149.29 (10.3%); £3,771,833.53 -> £3,382,149.33 (10.3%); £3,771,833.69 -> £3,382,149.37 (10.3%); £3,771,833.85 -> £3,382,149.41 (10.3%); £3,771,834.00 -> £3,382,149.45 (10.3%); £3,771,834.15 -> £3,382,149.49 (10.3%); £3,771,834.31 -> £3,382,149.72 (10.3%); £3,771,834.47 -> £3,382,149.95 (10.3%); £3,771,834.65 -> £3,382,150.20 (10.3%); £3,771,834.83 -> £3,382,150.45 (10.3%); £3,771,835.04 -> £3,382,150.73 (10.3%); £3,771,835.28 -> £3,382,151.03 (10.3%); £3,771,835.53 -> £3,382,151.35 (10.3%); £3,771,835.78 -> £3,382,151.68 (10.3%); £3,771,836.04 -> £3,382,151.80 (10.3%); £3,771,836.30 -> £3,382,151.93 (10.3%); £3,771,836.55 -> £3,382,152.06 (10.3%); £3,771,836.81 -> £3,382,152.19 (10.3%); £3,771,837.07 -> £3,382,152.32 (10.3%); £3,771,837.33 -> £3,382,152.45 (10.3%); £3,771,837.59 -> £3,382,152.57 (10.3%); £3,771,837.86 -> £3,382,152.69 (10.3%); £3,771,838.11 -> £3,382,152.81 (10.3%); £3,771,838.38 -> £3,382,152.93 (10.3%); £3,771,838.63 -> £3,382,153.04 (10.3%); £3,771,838.89 -> £3,382,153.15 (10.3%); £3,771,839.16 -> £3,382,153.26 (10.3%); £3,771,839.43 -> £3,382,153.58 (10.3%); £3,771,839.69 -> £3,382,153.87 (10.3%); £3,771,839.87 -> £3,382,154.14 (10.3%); £3,771,840.08 -> £3,382,154.38 (10.3%); £3,771,840.28 -> £3,382,154.62 (10.3%); £3,771,840.47 -> £3,382,154.86 (10.3%); £3,771,840.73 -> £3,382,155.09 (10.3%); £3,771,840.99 -> £3,382,155.32 (10.3%); £3,771,841.26 -> £3,382,155.54 (10.3%); £3,771,841.52 -> £3,382,155.77 (10.3%); £3,771,841.78 -> £3,382,155.99 (10.3%); £3,771,842.04 -> £3,382,156.04 (10.3%); £3,771,842.31 -> £3,382,156.08 (10.3%); £3,771,842.55 -> £3,382,156.12 (10.3%); £3,771,842.78 -> £3,382,156.15 (10.3%); £3,771,842.98 -> £3,382,156.19 (10.3%); £3,771,843.14 -> £3,382,156.23 (10.3%); £3,771,843.30 -> £3,382,156.27 (10.3%); £3,771,843.45 -> £3,382,156.30 (10.3%); £3,771,843.61 -> £3,382,156.34 (10.3%); £3,771,843.76 -> £3,382,156.38 (10.3%); £3,771,843.92 -> £3,382,156.41 (10.3%); £3,771,844.08 -> £3,382,156.45 (10.3%); £3,771,844.24 -> £3,382,156.49 (10.3%); £3,771,844.40 -> £3,382,156.53 (10.3%); £3,771,844.55 -> £3,382,156.57 (10.3%); £3,771,844.71 -> £3,382,156.61 (10.3%); £3,771,844.87 -> £3,382,156.79 (10.3%); £3,771,845.02 -> £3,382,156.97 (10.3%); £3,771,845.20 -> £3,382,157.17 (10.3%); £3,771,845.40 -> £3,382,157.38 (10.3%); £3,771,845.60 -> £3,382,157.61 (10.3%); £3,771,845.83 -> £3,382,157.86 (10.3%); £3,771,846.07 -> £3,382,158.14 (10.3%); £3,771,846.32 -> £3,382,158.43 (10.3%); £3,771,846.58 -> £3,382,158.56 (10.3%); £3,771,846.84 -> £3,382,158.69 (10.3%); £3,771,847.09 -> £3,382,158.82 (10.3%); £3,771,847.36 -> £3,382,158.95 (10.3%); £3,771,847.62 -> £3,382,159.08 (10.3%); £3,771,847.88 -> £3,382,159.20 (10.3%); £3,771,848.15 -> £3,382,159.32 (10.3%); £3,771,848.41 -> £3,382,159.44 (10.3%); £3,771,848.67 -> £3,382,159.56 (10.3%); £3,771,848.94 -> £3,382,159.67 (10.3%); £3,771,849.20 -> £3,382,159.78 (10.3%); £3,771,849.46 -> £3,382,159.90 (10.3%); £3,771,849.72 -> £3,382,160.00 (10.3%); £3,771,849.92 -> £3,382,160.29 (10.3%); £3,771,850.18 -> £3,382,160.55 (10.3%); £3,771,850.38 -> £3,382,160.78 (10.3%); £3,771,850.58 -> £3,382,160.99 (10.3%); £3,771,850.85 -> £3,382,161.19 (10.3%); £3,771,851.11 -> £3,382,161.39 (10.3%); £3,771,851.30 -> £3,382,161.59 (10.3%); £3,771,851.56 -> £3,382,161.78 (10.3%); £3,771,851.82 -> £3,382,161.96 (10.3%); £3,771,852.09 -> £3,382,162.15 (10.3%); £3,771,852.35 -> £3,382,162.33 (10.3%); £3,771,852.62 -> £3,382,162.37 (10.3%); £3,771,852.89 -> £3,382,162.41 (10.3%); £3,771,853.13 -> £3,382,162.45 (10.3%); £3,771,853.36 -> £3,382,162.49 (10.3%); £3,771,853.56 -> £3,382,162.52 (10.3%); £3,771,853.72 -> £3,382,162.56 (10.3%); £3,771,853.87 -> £3,382,162.60 (10.3%); £3,771,854.02 -> £3,382,162.64 (10.3%); £3,771,854.18 -> £3,382,162.67 (10.3%); £3,771,854.33 -> £3,382,162.71 (10.3%); £3,771,854.49 -> £3,382,162.75 (10.3%); £3,771,854.64 -> £3,382,162.78 (10.3%); £3,771,854.80 -> £3,382,162.82 (10.3%); £3,771,854.95 -> £3,382,162.86 (10.3%); £3,771,855.11 -> £3,382,162.90 (10.3%); £3,771,855.26 -> £3,382,162.94 (10.3%); £3,771,855.42 -> £3,382,163.11 (10.3%); £3,771,855.57 -> £3,382,163.29 (10.3%); £3,771,855.74 -> £3,382,163.47 (10.3%); £3,771,855.93 -> £3,382,163.66 (10.3%); £3,771,856.13 -> £3,382,163.87 (10.3%); £3,771,856.36 -> £3,382,164.10 (10.3%); £3,771,856.60 -> £3,382,164.35 (10.3%); £3,771,856.86 -> £3,382,164.62 (10.3%); £3,771,857.12 -> £3,382,164.74 (10.3%); £3,771,857.38 -> £3,382,164.87 (10.3%); £3,771,857.64 -> £3,382,164.99 (10.3%); £3,771,857.89 -> £3,382,165.12 (10.3%); £3,771,858.15 -> £3,382,165.24 (10.3%); £3,771,858.40 -> £3,382,165.37 (10.3%); £3,771,858.66 -> £3,382,165.48 (10.3%); £3,771,858.92 -> £3,382,165.60 (10.3%); £3,771,859.18 -> £3,382,165.71 (10.3%); £3,771,859.44 -> £3,382,165.83 (10.3%); £3,771,859.69 -> £3,382,165.95 (10.3%); £3,771,859.93 -> £3,382,166.06 (10.3%); £3,771,860.20 -> £3,382,166.17 (10.3%); £3,771,860.45 -> £3,382,166.44 (10.3%); £3,771,860.71 -> £3,382,166.68 (10.3%); £3,771,860.96 -> £3,382,166.89 (10.3%); £3,771,861.16 -> £3,382,167.08 (10.3%); £3,771,861.35 -> £3,382,167.26 (10.3%); £3,771,861.61 -> £3,382,167.44 (10.3%); £3,771,861.81 -> £3,382,167.61 (10.3%); £3,771,862.06 -> £3,382,167.78 (10.3%); £3,771,862.31 -> £3,382,167.94 (10.3%); £3,771,862.58 -> £3,382,168.10 (10.3%); £3,771,862.83 -> £3,382,168.26 (10.3%); £3,771,863.10 -> £3,382,168.30 (10.3%); £3,771,863.36 -> £3,382,168.34 (10.3%); £3,771,863.60 -> £3,382,168.38 (10.3%); £3,771,863.82 -> £3,382,168.42 (10.3%); £3,771,864.02 -> £3,382,168.46 (10.3%); £3,771,864.18 -> £3,382,168.50 (10.3%); £3,771,864.33 -> £3,382,168.53 (10.3%); £3,771,864.49 -> £3,382,168.57 (10.3%); £3,771,864.64 -> £3,382,168.61 (10.3%); £3,771,864.80 -> £3,382,168.64 (10.3%); £3,771,864.96 -> £3,382,168.68 (10.3%); £3,771,865.12 -> £3,382,168.72 (10.3%); £3,771,865.27 -> £3,382,168.76 (10.3%); £3,771,865.43 -> £3,382,168.80 (10.3%); £3,771,865.58 -> £3,382,168.83 (10.3%); £3,771,865.73 -> £3,382,168.88 (10.3%); £3,771,865.89 -> £3,382,169.10 (10.3%); £3,771,866.04 -> £3,382,169.32 (10.3%); £3,771,866.22 -> £3,382,169.56 (10.3%); £3,771,866.40 -> £3,382,169.81 (10.3%); £3,771,866.60 -> £3,382,170.08 (10.3%); £3,771,866.83 -> £3,382,170.37 (10.3%); £3,771,867.06 -> £3,382,170.69 (10.3%); £3,771,867.32 -> £3,382,171.02 (10.3%); £3,771,867.58 -> £3,382,171.14 (10.3%); £3,771,867.84 -> £3,382,171.27 (10.3%); £3,771,868.10 -> £3,382,171.39 (10.3%); £3,771,868.36 -> £3,382,171.52 (10.3%); £3,771,868.63 -> £3,382,171.65 (10.3%); £3,771,868.89 -> £3,382,171.77 (10.3%); £3,771,869.15 -> £3,382,171.88 (10.3%); £3,771,869.41 -> £3,382,171.99 (10.3%); £3,771,869.67 -> £3,382,172.11 (10.3%); £3,771,869.94 -> £3,382,172.23 (10.3%); £3,771,870.20 -> £3,382,172.35 (10.3%); £3,771,870.46 -> £3,382,172.46 (10.3%); £3,771,870.72 -> £3,382,172.56 (10.3%); £3,771,870.97 -> £3,382,172.87 (10.3%); £3,771,871.23 -> £3,382,173.17 (10.3%); £3,771,871.49 -> £3,382,173.43 (10.3%); £3,771,871.76 -> £3,382,173.67 (10.3%); £3,771,872.03 -> £3,382,173.91 (10.3%); £3,771,872.29 -> £3,382,174.14 (10.3%); £3,771,872.55 -> £3,382,174.39 (10.3%); £3,771,872.81 -> £3,382,174.61 (10.3%); £3,771,873.08 -> £3,382,174.84 (10.3%); £3,771,873.34 -> £3,382,175.07 (10.3%); £3,771,873.60 -> £3,382,175.28 (10.3%); £3,771,873.87 -> £3,382,175.32 (10.3%); £3,771,874.13 -> £3,382,175.36 (10.3%); £3,771,874.37 -> £3,382,175.40 (10.3%); £3,771,874.59 -> £3,382,175.44 (10.3%); £3,771,874.79 -> £3,382,175.47 (10.3%); £3,771,874.93 -> £3,382,175.51 (10.3%); £3,771,875.06 -> £3,382,175.55 (10.3%); £3,771,875.19 -> £3,382,175.59 (10.3%); £3,771,875.33 -> £3,382,175.62 (10.3%); £3,771,875.47 -> £3,382,175.66 (10.3%); £3,771,875.60 -> £3,382,175.70 (10.3%); £3,771,875.74 -> £3,382,175.73 (10.3%); £3,771,875.87 -> £3,382,175.77 (10.3%); £3,771,876.01 -> £3,382,175.81 (10.3%); £3,771,876.15 -> £3,382,175.85 (10.3%); £3,771,876.29 -> £3,382,175.88 (10.3%); £3,771,876.42 -> £3,382,176.12 (10.3%); £3,771,876.56 -> £3,382,176.35 (10.3%); £3,771,876.72 -> £3,382,176.59 (10.3%); £3,771,876.88 -> £3,382,176.83 (10.3%); £3,771,877.06 -> £3,382,177.07 (10.3%); £3,771,877.26 -> £3,382,177.33 (10.3%); £3,771,877.47 -> £3,382,177.60 (10.3%); £3,771,877.70 -> £3,382,177.88 (10.3%); £3,771,877.93 -> £3,382,177.97 (10.3%); £3,771,878.15 -> £3,382,178.06 (10.3%); £3,771,878.37 -> £3,382,178.15 (10.3%); £3,771,878.59 -> £3,382,178.24 (10.3%); £3,771,878.82 -> £3,382,178.32 (10.3%); £3,771,879.04 -> £3,382,178.40 (10.3%); £3,771,879.27 -> £3,382,178.48 (10.3%); £3,771,879.50 -> £3,382,178.55 (10.3%); £3,771,879.74 -> £3,382,178.63 (10.3%); £3,771,879.97 -> £3,382,178.70 (10.3%); £3,771,880.19 -> £3,382,178.77 (10.3%); £3,771,880.42 -> £3,382,178.84 (10.3%); £3,771,880.65 -> £3,382,178.91 (10.3%); £3,771,880.87 -> £3,382,179.17 (10.3%); £3,771,881.10 -> £3,382,179.42 (10.3%); £3,771,881.32 -> £3,382,179.66 (10.3%); £3,771,881.55 -> £3,382,179.89 (10.3%); £3,771,881.77 -> £3,382,180.12 (10.3%); £3,771,882.00 -> £3,382,180.36 (10.3%); £3,771,882.23 -> £3,382,180.59 (10.3%); £3,771,882.46 -> £3,382,180.82 (10.3%); £3,771,882.69 -> £3,382,181.05 (10.3%); £3,771,882.91 -> £3,382,181.28 (10.3%); £3,771,883.14 -> £3,382,181.51 (10.3%); £3,771,883.37 -> £3,382,181.55 (10.3%); £3,771,883.58 -> £3,382,181.59 (10.3%); £3,771,883.80 -> £3,382,181.63 (10.3%); £3,771,883.99 -> £3,382,181.67 (10.3%); £3,771,884.17 -> £3,382,181.70 (10.3%); £3,771,884.30 -> £3,382,181.74 (10.3%); £3,771,884.44 -> £3,382,181.78 (10.3%); £3,771,884.57 -> £3,382,181.82 (10.3%); £3,771,884.70 -> £3,382,181.85 (10.3%); £3,771,884.84 -> £3,382,181.89 (10.3%); £3,771,884.98 -> £3,382,181.92 (10.3%); £3,771,885.11 -> £3,382,181.96 (10.3%); £3,771,885.24 -> £3,382,182.00 (10.3%); £3,771,885.38 -> £3,382,182.03 (10.3%); £3,771,885.52 -> £3,382,182.07 (10.3%); £3,771,885.65 -> £3,382,182.10 (10.3%); £3,771,885.79 -> £3,382,182.32 (10.3%); £3,771,885.93 -> £3,382,182.53 (10.3%); £3,771,886.08 -> £3,382,182.75 (10.3%); £3,771,886.24 -> £3,382,182.97 (10.3%); £3,771,886.42 -> £3,382,183.19 (10.3%); £3,771,886.62 -> £3,382,183.42 (10.3%); £3,771,886.83 -> £3,382,183.65 (10.3%); £3,771,887.05 -> £3,382,183.87 (10.3%); £3,771,887.28 -> £3,382,183.92 (10.3%); £3,771,887.51 -> £3,382,183.97 (10.3%); £3,771,887.74 -> £3,382,184.02 (10.3%); £3,771,887.96 -> £3,382,184.07 (10.3%); £3,771,888.17 -> £3,382,184.12 (10.3%); £3,771,888.40 -> £3,382,184.17 (10.3%); £3,771,888.63 -> £3,382,184.22 (10.3%); £3,771,888.86 -> £3,382,184.27 (10.3%); £3,771,889.08 -> £3,382,184.31 (10.3%); £3,771,889.31 -> £3,382,184.36 (10.3%); £3,771,889.53 -> £3,382,184.40 (10.3%); £3,771,889.76 -> £3,382,184.45 (10.3%); £3,771,890.00 -> £3,382,184.50 (10.3%); £3,771,890.23 -> £3,382,184.71 (10.3%); £3,771,890.45 -> £3,382,184.94 (10.3%); £3,771,890.68 -> £3,382,185.15 (10.3%); £3,771,890.91 -> £3,382,185.37 (10.3%); £3,771,891.13 -> £3,382,185.59 (10.3%); £3,771,891.35 -> £3,382,185.82 (10.3%); £3,771,891.58 -> £3,382,186.04 (10.3%); £3,771,891.79 -> £3,382,186.26 (10.3%); £3,771,892.02 -> £3,382,186.48 (10.3%); £3,771,892.25 -> £3,382,186.70 (10.3%); £3,771,892.49 -> £3,382,186.91 (10.3%); £3,771,892.71 -> £3,382,186.95 (10.3%); £3,771,892.94 -> £3,382,186.99 (10.3%); £3,771,893.15 -> £3,382,187.03 (10.3%); £3,771,893.34 -> £3,382,187.07 (10.3%); £3,771,893.52 -> £3,382,187.10 (10.3%); £3,771,893.67 -> £3,382,187.14 (10.3%); £3,771,893.83 -> £3,382,187.18 (10.3%); £3,771,893.98 -> £3,382,187.22 (10.3%); £3,771,894.14 -> £3,382,187.25 (10.3%); £3,771,894.29 -> £3,382,187.29 (10.3%); £3,771,894.45 -> £3,382,187.33 (10.3%); £3,771,894.60 -> £3,382,187.36 (10.3%); £3,771,894.76 -> £3,382,187.40 (10.3%); £3,771,894.91 -> £3,382,187.44 (10.3%); £3,771,895.06 -> £3,382,187.48 (10.3%); £3,771,895.22 -> £3,382,187.52 (10.3%); £3,771,895.38 -> £3,382,187.72 (10.3%); £3,771,895.53 -> £3,382,187.93 (10.3%); £3,771,895.70 -> £3,382,188.14 (10.3%); £3,771,895.89 -> £3,382,188.38 (10.3%); £3,771,896.09 -> £3,382,188.63 (10.3%); £3,771,896.32 -> £3,382,188.91 (10.3%); £3,771,896.56 -> £3,382,189.21 (10.3%); £3,771,896.82 -> £3,382,189.53 (10.3%); £3,771,897.08 -> £3,382,189.66 (10.3%); £3,771,897.34 -> £3,382,189.79 (10.3%); £3,771,897.61 -> £3,382,189.92 (10.3%); £3,771,897.86 -> £3,382,190.05 (10.3%); £3,771,898.12 -> £3,382,190.18 (10.3%); £3,771,898.38 -> £3,382,190.30 (10.3%); £3,771,898.64 -> £3,382,190.42 (10.3%); £3,771,898.90 -> £3,382,190.53 (10.3%); £3,771,899.16 -> £3,382,190.65 (10.3%); £3,771,899.42 -> £3,382,190.77 (10.3%); £3,771,899.67 -> £3,382,190.88 (10.3%); £3,771,899.94 -> £3,382,191.00 (10.3%); £3,771,900.20 -> £3,382,191.11 (10.3%); £3,771,900.44 -> £3,382,191.41 (10.3%); £3,771,900.70 -> £3,382,191.69 (10.3%); £3,771,900.95 -> £3,382,191.94 (10.3%); £3,771,901.20 -> £3,382,192.17 (10.3%); £3,771,901.46 -> £3,382,192.39 (10.3%); £3,771,901.71 -> £3,382,192.60 (10.3%); £3,771,901.97 -> £3,382,192.82 (10.3%); £3,771,902.23 -> £3,382,193.04 (10.3%); £3,771,902.49 -> £3,382,193.26 (10.3%); £3,771,902.74 -> £3,382,193.46 (10.3%); £3,771,903.01 -> £3,382,193.66 (10.3%); £3,771,903.26 -> £3,382,193.70 (10.3%); £3,771,903.52 -> £3,382,193.74 (10.3%); £3,771,903.76 -> £3,382,193.78 (10.3%); £3,771,903.98 -> £3,382,193.82 (10.3%); £3,771,904.18 -> £3,382,193.85 (10.3%); £3,771,904.33 -> £3,382,193.89 (10.3%); £3,771,904.48 -> £3,382,193.93 (10.3%); £3,771,904.64 -> £3,382,193.97 (10.3%); £3,771,904.80 -> £3,382,194.01 (10.3%); £3,771,904.95 -> £3,382,194.04 (10.3%); £3,771,905.11 -> £3,382,194.08 (10.3%); £3,771,905.25 -> £3,382,194.12 (10.3%); £3,771,905.40 -> £3,382,194.16 (10.3%); £3,771,905.55 -> £3,382,194.19 (10.3%); £3,771,905.70 -> £3,382,194.23 (10.3%); £3,771,905.86 -> £3,382,194.27 (10.3%); £3,771,906.01 -> £3,382,194.45 (10.3%); £3,771,906.17 -> £3,382,194.63 (10.3%); £3,771,906.34 -> £3,382,194.82 (10.3%); £3,771,906.53 -> £3,382,195.02 (10.3%); £3,771,906.73 -> £3,382,195.25 (10.3%); £3,771,906.95 -> £3,382,195.49 (10.3%); £3,771,907.19 -> £3,382,195.76 (10.3%); £3,771,907.45 -> £3,382,196.04 (10.3%); £3,771,907.70 -> £3,382,196.16 (10.3%); £3,771,907.96 -> £3,382,196.29 (10.3%); £3,771,908.22 -> £3,382,196.42 (10.3%); £3,771,908.48 -> £3,382,196.55 (10.3%); £3,771,908.73 -> £3,382,196.68 (10.3%); £3,771,908.98 -> £3,382,196.81 (10.3%); £3,771,909.25 -> £3,382,196.93 (10.3%); £3,771,909.50 -> £3,382,197.05 (10.3%); £3,771,909.75 -> £3,382,197.16 (10.3%); £3,771,910.01 -> £3,382,197.28 (10.3%); £3,771,910.26 -> £3,382,197.39 (10.3%); £3,771,910.53 -> £3,382,197.51 (10.3%); £3,771,910.78 -> £3,382,197.62 (10.3%); £3,771,911.05 -> £3,382,197.89 (10.3%); £3,771,911.31 -> £3,382,198.15 (10.3%); £3,771,911.56 -> £3,382,198.37 (10.3%); £3,771,911.81 -> £3,382,198.57 (10.3%); £3,771,912.07 -> £3,382,198.76 (10.3%); £3,771,912.33 -> £3,382,198.95 (10.3%); £3,771,912.58 -> £3,382,199.14 (10.3%); £3,771,912.84 -> £3,382,199.32 (10.3%); £3,771,913.10 -> £3,382,199.50 (10.3%); £3,771,913.35 -> £3,382,199.68 (10.3%); £3,771,913.61 -> £3,382,199.86 (10.3%); £3,771,913.87 -> £3,382,199.90 (10.3%); £3,771,914.13 -> £3,382,199.94 (10.3%); £3,771,914.37 -> £3,382,199.98 (10.3%); £3,771,914.58 -> £3,382,200.02 (10.3%); £3,771,914.78 -> £3,382,200.05 (10.3%); £3,771,914.93 -> £3,382,200.09 (10.3%); £3,771,915.08 -> £3,382,200.13 (10.3%); £3,771,915.23 -> £3,382,200.16 (10.3%); £3,771,915.37 -> £3,382,200.20 (10.3%); £3,771,915.52 -> £3,382,200.24 (10.3%); £3,771,915.68 -> £3,382,200.27 (10.3%); £3,771,915.83 -> £3,382,200.31 (10.3%); £3,771,915.99 -> £3,382,200.35 (10.3%); £3,771,916.13 -> £3,382,200.39 (10.3%); £3,771,916.29 -> £3,382,200.42 (10.3%); £3,771,916.44 -> £3,382,200.46 (10.3%); £3,771,916.59 -> £3,382,200.66 (10.3%); £3,771,916.75 -> £3,382,200.87 (10.3%); £3,771,916.92 -> £3,382,201.08 (10.3%); £3,771,917.11 -> £3,382,201.31 (10.3%); £3,771,917.32 -> £3,382,201.56 (10.3%); £3,771,917.53 -> £3,382,201.82 (10.3%); £3,771,917.77 -> £3,382,202.12 (10.3%); £3,771,918.02 -> £3,382,202.44 (10.3%); £3,771,918.27 -> £3,382,202.57 (10.3%); £3,771,918.53 -> £3,382,202.69 (10.3%); £3,771,918.78 -> £3,382,202.83 (10.3%); £3,771,919.04 -> £3,382,202.96 (10.3%); £3,771,919.31 -> £3,382,203.08 (10.3%); £3,771,919.57 -> £3,382,203.21 (10.3%); £3,771,919.82 -> £3,382,203.32 (10.3%); £3,771,920.08 -> £3,382,203.44 (10.3%); £3,771,920.35 -> £3,382,203.56 (10.3%); £3,771,920.59 -> £3,382,203.67 (10.3%); £3,771,920.85 -> £3,382,203.79 (10.3%); £3,771,921.10 -> £3,382,203.90 (10.3%); £3,771,921.36 -> £3,382,204.01 (10.3%); £3,771,921.62 -> £3,382,204.32 (10.3%); £3,771,921.88 -> £3,382,204.60 (10.3%); £3,771,922.14 -> £3,382,204.84 (10.3%); £3,771,922.40 -> £3,382,205.06 (10.3%); £3,771,922.65 -> £3,382,205.28 (10.3%); £3,771,922.91 -> £3,382,205.49 (10.3%); £3,771,923.16 -> £3,382,205.71 (10.3%); £3,771,923.42 -> £3,382,205.91 (10.3%); £3,771,923.67 -> £3,382,206.12 (10.3%); £3,771,923.93 -> £3,382,206.33 (10.3%); £3,771,924.18 -> £3,382,206.54 (10.3%); £3,771,924.44 -> £3,382,206.58 (10.3%); £3,771,924.69 -> £3,382,206.62 (10.3%); £3,771,924.93 -> £3,382,206.66 (10.3%); £3,771,925.15 -> £3,382,206.70 (10.3%); £3,771,925.34 -> £3,382,206.73 (10.3%); £3,771,925.50 -> £3,382,206.77 (10.3%); £3,771,925.65 -> £3,382,206.81 (10.3%); £3,771,925.81 -> £3,382,206.85 (10.3%); £3,771,925.95 -> £3,382,206.89 (10.3%); £3,771,926.10 -> £3,382,206.92 (10.3%); £3,771,926.26 -> £3,382,206.96 (10.3%); £3,771,926.41 -> £3,382,207.00 (10.3%); £3,771,926.56 -> £3,382,207.03 (10.3%); £3,771,926.71 -> £3,382,207.07 (10.3%); £3,771,926.87 -> £3,382,207.11 (10.3%); £3,771,927.02 -> £3,382,207.15 (10.3%); £3,771,927.17 -> £3,382,207.34 (10.3%); £3,771,927.32 -> £3,382,207.52 (10.3%); £3,771,927.49 -> £3,382,207.72 (10.3%); £3,771,927.68 -> £3,382,207.93 (10.3%); £3,771,927.88 -> £3,382,208.17 (10.3%); £3,771,928.09 -> £3,382,208.42 (10.3%); £3,771,928.33 -> £3,382,208.70 (10.3%); £3,771,928.60 -> £3,382,208.98 (10.3%); £3,771,928.85 -> £3,382,209.10 (10.3%); £3,771,929.12 -> £3,382,209.22 (10.3%); £3,771,929.37 -> £3,382,209.35 (10.3%); £3,771,929.62 -> £3,382,209.47 (10.3%); £3,771,929.87 -> £3,382,209.60 (10.3%); £3,771,930.12 -> £3,382,209.72 (10.3%); £3,771,930.38 -> £3,382,209.84 (10.3%); £3,771,930.63 -> £3,382,209.95 (10.3%); £3,771,930.89 -> £3,382,210.07 (10.3%); £3,771,931.14 -> £3,382,210.18 (10.3%); £3,771,931.40 -> £3,382,210.29 (10.3%); £3,771,931.66 -> £3,382,210.40 (10.3%); £3,771,931.91 -> £3,382,210.51 (10.3%); £3,771,932.17 -> £3,382,210.79 (10.3%); £3,771,932.43 -> £3,382,211.05 (10.3%); £3,771,932.68 -> £3,382,211.29 (10.3%); £3,771,932.94 -> £3,382,211.51 (10.3%); £3,771,933.19 -> £3,382,211.71 (10.3%); £3,771,933.45 -> £3,382,211.92 (10.3%); £3,771,933.70 -> £3,382,212.12 (10.3%); £3,771,933.95 -> £3,382,212.32 (10.3%); £3,771,934.22 -> £3,382,212.52 (10.3%); £3,771,934.48 -> £3,382,212.71 (10.3%); £3,771,934.73 -> £3,382,212.89 (10.3%); £3,771,934.98 -> £3,382,212.93 (10.3%); £3,771,935.23 -> £3,382,212.97 (10.3%); £3,771,935.47 -> £3,382,213.01 (10.3%); £3,771,935.68 -> £3,382,213.05 (10.3%); £3,771,935.89 -> £3,382,213.09 (10.3%); £3,771,936.03 -> £3,382,213.12 (10.3%); £3,771,936.19 -> £3,382,213.16 (10.3%); £3,771,936.34 -> £3,382,213.20 (10.3%); £3,771,936.49 -> £3,382,213.24 (10.3%); £3,771,936.64 -> £3,382,213.28 (10.3%); £3,771,936.80 -> £3,382,213.31 (10.3%); £3,771,936.95 -> £3,382,213.35 (10.3%); £3,771,937.10 -> £3,382,213.39 (10.3%); £3,771,937.26 -> £3,382,213.43 (10.3%); £3,771,937.41 -> £3,382,213.46 (10.3%); £3,771,937.56 -> £3,382,213.50 (10.3%); £3,771,937.71 -> £3,382,213.70 (10.3%); £3,771,937.87 -> £3,382,213.89 (10.3%); £3,771,938.04 -> £3,382,214.09 (10.3%); £3,771,938.23 -> £3,382,214.31 (10.3%); £3,771,938.43 -> £3,382,214.54 (10.3%); £3,771,938.64 -> £3,382,214.80 (10.3%); £3,771,938.88 -> £3,382,215.08 (10.3%); £3,771,939.15 -> £3,382,215.37 (10.3%); £3,771,939.41 -> £3,382,215.49 (10.3%); £3,771,939.67 -> £3,382,215.62 (10.3%); £3,771,939.92 -> £3,382,215.74 (10.3%); £3,771,940.18 -> £3,382,215.87 (10.3%); £3,771,940.44 -> £3,382,215.99 (10.3%); £3,771,940.69 -> £3,382,216.11 (10.3%); £3,771,940.95 -> £3,382,216.23 (10.3%); £3,771,941.20 -> £3,382,216.35 (10.3%); £3,771,941.45 -> £3,382,216.47 (10.3%); £3,771,941.71 -> £3,382,216.59 (10.3%); £3,771,941.97 -> £3,382,216.70 (10.3%); £3,771,942.22 -> £3,382,216.81 (10.3%); £3,771,942.48 -> £3,382,216.92 (10.3%); £3,771,942.74 -> £3,382,217.20 (10.3%); £3,771,942.98 -> £3,382,217.46 (10.3%); £3,771,943.24 -> £3,382,217.69 (10.3%); £3,771,943.49 -> £3,382,217.90 (10.3%); £3,771,943.75 -> £3,382,218.11 (10.3%); £3,771,944.00 -> £3,382,218.31 (10.3%); £3,771,944.25 -> £3,382,218.50 (10.3%); £3,771,944.51 -> £3,382,218.70 (10.3%); £3,771,944.77 -> £3,382,218.89 (10.3%); £3,771,945.02 -> £3,382,219.07 (10.3%); £3,771,945.26 -> £3,382,219.25 (10.3%); £3,771,945.53 -> £3,382,219.30 (10.3%); £3,771,945.78 -> £3,382,219.34 (10.3%); £3,771,946.02 -> £3,382,219.38 (10.3%); £3,771,946.23 -> £3,382,219.41 (10.3%); £3,771,946.43 -> £3,382,219.45 (10.3%); £3,771,946.56 -> £3,382,219.49 (10.3%); £3,771,946.69 -> £3,382,219.53 (10.3%); £3,771,946.82 -> £3,382,219.56 (10.3%); £3,771,946.96 -> £3,382,219.60 (10.3%); £3,771,947.09 -> £3,382,219.64 (10.3%); £3,771,947.22 -> £3,382,219.67 (10.3%); £3,771,947.36 -> £3,382,219.71 (10.3%); £3,771,947.50 -> £3,382,219.75 (10.3%); £3,771,947.63 -> £3,382,219.79 (10.3%); £3,771,947.76 -> £3,382,219.82 (10.3%); £3,771,947.89 -> £3,382,219.86 (10.3%); £3,771,948.03 -> £3,382,220.03 (10.3%); £3,771,948.17 -> £3,382,220.20 (10.3%); £3,771,948.32 -> £3,382,220.38 (10.3%); £3,771,948.48 -> £3,382,220.56 (10.3%); £3,771,948.66 -> £3,382,220.76 (10.3%); £3,771,948.86 -> £3,382,220.97 (10.3%); £3,771,949.07 -> £3,382,221.19 (10.3%); £3,771,949.29 -> £3,382,221.42 (10.3%); £3,771,949.52 -> £3,382,221.51 (10.3%); £3,771,949.74 -> £3,382,221.60 (10.3%); £3,771,949.96 -> £3,382,221.69 (10.3%); £3,771,950.18 -> £3,382,221.78 (10.3%); £3,771,950.41 -> £3,382,221.86 (10.3%); £3,771,950.64 -> £3,382,221.94 (10.3%); £3,771,950.86 -> £3,382,222.01 (10.3%); £3,771,951.08 -> £3,382,222.08 (10.3%); £3,771,951.31 -> £3,382,222.15 (10.3%); £3,771,951.54 -> £3,382,222.22 (10.3%); £3,771,951.77 -> £3,382,222.29 (10.3%); £3,771,952.00 -> £3,382,222.36 (10.3%); £3,771,952.22 -> £3,382,222.43 (10.3%); £3,771,952.44 -> £3,382,222.64 (10.3%); £3,771,952.67 -> £3,382,222.85 (10.3%); £3,771,952.89 -> £3,382,223.04 (10.3%); £3,771,953.13 -> £3,382,223.22 (10.3%); £3,771,953.35 -> £3,382,223.40 (10.3%); £3,771,953.57 -> £3,382,223.59 (10.3%); £3,771,953.79 -> £3,382,223.77 (10.3%); £3,771,954.02 -> £3,382,223.96 (10.3%); £3,771,954.23 -> £3,382,224.14 (10.3%); £3,771,954.46 -> £3,382,224.32 (10.3%); £3,771,954.68 -> £3,382,224.49 (10.3%); £3,771,954.90 -> £3,382,224.53 (10.3%); £3,771,955.12 -> £3,382,224.57 (10.3%); £3,771,955.33 -> £3,382,224.61 (10.3%); £3,771,955.52 -> £3,382,224.65 (10.3%); £3,771,955.70 -> £3,382,224.68 (10.3%); £3,771,955.83 -> £3,382,224.72 (10.3%); £3,771,955.96 -> £3,382,224.76 (10.3%); £3,771,956.10 -> £3,382,224.80 (10.3%); £3,771,956.23 -> £3,382,224.84 (10.3%); £3,771,956.37 -> £3,382,224.88 (10.3%); £3,771,956.50 -> £3,382,224.91 (10.3%); £3,771,956.64 -> £3,382,224.95 (10.3%); £3,771,956.78 -> £3,382,224.99 (10.3%); £3,771,956.91 -> £3,382,225.03 (10.3%); £3,771,957.05 -> £3,382,225.06 (10.3%); £3,771,957.18 -> £3,382,225.10 (10.3%); £3,771,957.32 -> £3,382,225.26 (10.3%); £3,771,957.45 -> £3,382,225.42 (10.3%); £3,771,957.60 -> £3,382,225.59 (10.3%); £3,771,957.77 -> £3,382,225.75 (10.3%); £3,771,957.95 -> £3,382,225.92 (10.3%); £3,771,958.15 -> £3,382,226.08 (10.3%); £3,771,958.35 -> £3,382,226.25 (10.3%); £3,771,958.57 -> £3,382,226.42 (10.3%); £3,771,958.81 -> £3,382,226.47 (10.3%); £3,771,959.03 -> £3,382,226.52 (10.3%); £3,771,959.26 -> £3,382,226.57 (10.3%); £3,771,959.48 -> £3,382,226.62 (10.3%); £3,771,959.70 -> £3,382,226.66 (10.3%); £3,771,959.93 -> £3,382,226.71 (10.3%); £3,771,960.15 -> £3,382,226.76 (10.3%); £3,771,960.37 -> £3,382,226.80 (10.3%); £3,771,960.59 -> £3,382,226.85 (10.3%); £3,771,960.82 -> £3,382,226.89 (10.3%); £3,771,961.05 -> £3,382,226.94 (10.3%); £3,771,961.27 -> £3,382,226.99 (10.3%); £3,771,961.49 -> £3,382,227.03 (10.3%); £3,771,961.72 -> £3,382,227.21 (10.3%); £3,771,961.94 -> £3,382,227.39 (10.3%); £3,771,962.17 -> £3,382,227.56 (10.3%); £3,771,962.40 -> £3,382,227.73 (10.3%); £3,771,962.62 -> £3,382,227.90 (10.3%); £3,771,962.83 -> £3,382,228.07 (10.3%); £3,771,963.05 -> £3,382,228.24 (10.3%); £3,771,963.26 -> £3,382,228.40 (10.3%); £3,771,963.49 -> £3,382,228.57 (10.3%); £3,771,963.72 -> £3,382,228.73 (10.3%); £3,771,963.94 -> £3,382,228.90 (10.3%); £3,771,964.17 -> £3,382,228.94 (10.3%); £3,771,964.39 -> £3,382,228.98 (10.3%); £3,771,964.60 -> £3,382,229.01 (10.3%); £3,771,964.79 -> £3,382,229.05 (10.3%); £3,771,964.97 -> £3,382,229.08 (10.3%); £3,771,965.12 -> £3,382,229.12 (10.3%); £3,771,965.27 -> £3,382,229.16 (10.3%); £3,771,965.42 -> £3,382,229.20 (10.3%); £3,771,965.58 -> £3,382,229.24 (10.3%); £3,771,965.73 -> £3,382,229.27 (10.3%); £3,771,965.88 -> £3,382,229.31 (10.3%); £3,771,966.03 -> £3,382,229.35 (10.3%); £3,771,966.18 -> £3,382,229.39 (10.3%); £3,771,966.34 -> £3,382,229.42 (10.3%); £3,771,966.49 -> £3,382,229.46 (10.3%); £3,771,966.64 -> £3,382,229.50 (10.3%); £3,771,966.78 -> £3,382,229.68 (10.3%); £3,771,966.93 -> £3,382,229.87 (10.3%); £3,771,967.10 -> £3,382,230.06 (10.3%); £3,771,967.29 -> £3,382,230.25 (10.3%); £3,771,967.50 -> £3,382,230.47 (10.3%); £3,771,967.72 -> £3,382,230.71 (10.3%); £3,771,967.96 -> £3,382,230.97 (10.3%); £3,771,968.21 -> £3,382,231.24 (10.3%); £3,771,968.46 -> £3,382,231.36 (10.3%); £3,771,968.71 -> £3,382,231.49 (10.3%); £3,771,968.97 -> £3,382,231.61 (10.3%); £3,771,969.23 -> £3,382,231.73 (10.3%); £3,771,969.47 -> £3,382,231.86 (10.3%); £3,771,969.74 -> £3,382,231.98 (10.3%); £3,771,969.98 -> £3,382,232.09 (10.3%); £3,771,970.23 -> £3,382,232.20 (10.3%); £3,771,970.48 -> £3,382,232.32 (10.3%); £3,771,970.74 -> £3,382,232.43 (10.3%); £3,771,970.99 -> £3,382,232.54 (10.3%); £3,771,971.25 -> £3,382,232.64 (10.3%); £3,771,971.50 -> £3,382,232.75 (10.3%); £3,771,971.75 -> £3,382,233.00 (10.3%); £3,771,972.00 -> £3,382,233.24 (10.3%); £3,771,972.26 -> £3,382,233.45 (10.3%); £3,771,972.52 -> £3,382,233.64 (10.3%); £3,771,972.77 -> £3,382,233.82 (10.3%); £3,771,973.03 -> £3,382,234.02 (10.3%); £3,771,973.27 -> £3,382,234.21 (10.3%); £3,771,973.52 -> £3,382,234.40 (10.3%); £3,771,973.77 -> £3,382,234.59 (10.3%); £3,771,974.03 -> £3,382,234.76 (10.3%); £3,771,974.29 -> £3,382,234.93 (10.3%); £3,771,974.54 -> £3,382,234.97 (10.3%); £3,771,974.80 -> £3,382,235.02 (10.3%); £3,771,975.02 -> £3,382,235.06 (10.3%); £3,771,975.24 -> £3,382,235.09 (10.3%); £3,771,975.43 -> £3,382,235.13 (10.3%); £3,771,975.58 -> £3,382,235.17 (10.3%); £3,771,975.73 -> £3,382,235.21 (10.3%); £3,771,975.88 -> £3,382,235.24 (10.3%); £3,771,976.03 -> £3,382,235.28 (10.3%); £3,771,976.18 -> £3,382,235.32 (10.3%); £3,771,976.33 -> £3,382,235.35 (10.3%); £3,771,976.48 -> £3,382,235.39 (10.3%); £3,771,976.63 -> £3,382,235.43 (10.3%); £3,771,976.78 -> £3,382,235.47 (10.3%); £3,771,976.93 -> £3,382,235.51 (10.3%); £3,771,977.08 -> £3,382,235.55 (10.3%); £3,771,977.22 -> £3,382,235.68 (10.3%); £3,771,977.38 -> £3,382,235.83 (10.3%); £3,771,977.55 -> £3,382,235.99 (10.3%); £3,771,977.74 -> £3,382,236.16 (10.3%); £3,771,977.94 -> £3,382,236.36 (10.3%); £3,771,978.15 -> £3,382,236.57 (10.3%); £3,771,978.39 -> £3,382,236.81 (10.3%); £3,771,978.64 -> £3,382,237.05 (10.3%); £3,771,978.89 -> £3,382,237.17 (10.3%); £3,771,979.14 -> £3,382,237.30 (10.3%); £3,771,979.39 -> £3,382,237.43 (10.3%); £3,771,979.65 -> £3,382,237.56 (10.3%); £3,771,979.90 -> £3,382,237.68 (10.3%); £3,771,980.15 -> £3,382,237.81 (10.3%); £3,771,980.40 -> £3,382,237.93 (10.3%); £3,771,980.65 -> £3,382,238.05 (10.3%); £3,771,980.90 -> £3,382,238.16 (10.3%); £3,771,981.15 -> £3,382,238.27 (10.3%); £3,771,981.41 -> £3,382,238.38 (10.3%); £3,771,981.66 -> £3,382,238.49 (10.3%); £3,771,981.92 -> £3,382,238.60 (10.3%); £3,771,982.17 -> £3,382,238.84 (10.3%); £3,771,982.43 -> £3,382,239.06 (10.3%); £3,771,982.68 -> £3,382,239.25 (10.3%); £3,771,982.94 -> £3,382,239.41 (10.3%); £3,771,983.20 -> £3,382,239.58 (10.3%); £3,771,983.46 -> £3,382,239.74 (10.3%); £3,771,983.71 -> £3,382,239.90 (10.3%); £3,771,983.96 -> £3,382,240.05 (10.3%); £3,771,984.20 -> £3,382,240.20 (10.3%); £3,771,984.44 -> £3,382,240.34 (10.3%); £3,771,984.69 -> £3,382,240.48 (10.3%); £3,771,984.94 -> £3,382,240.52 (10.3%); £3,771,985.19 -> £3,382,240.56 (10.3%); £3,771,985.43 -> £3,382,240.60 (10.3%); £3,771,985.65 -> £3,382,240.64 (10.3%); £3,771,985.84 -> £3,382,240.67 (10.3%); £3,771,985.99 -> £3,382,240.71 (10.3%); £3,771,986.14 -> £3,382,240.75 (10.3%); £3,771,986.30 -> £3,382,240.79 (10.3%); £3,771,986.45 -> £3,382,240.83 (10.3%); £3,771,986.60 -> £3,382,240.86 (10.3%); £3,771,986.75 -> £3,382,240.90 (10.3%); £3,771,986.90 -> £3,382,240.94 (10.3%); £3,771,987.05 -> £3,382,240.98 (10.3%); £3,771,987.20 -> £3,382,241.01 (10.3%); £3,771,987.35 -> £3,382,241.05 (10.3%); £3,771,987.51 -> £3,382,241.09 (10.3%); £3,771,987.66 -> £3,382,241.20 (10.3%); £3,771,987.81 -> £3,382,241.31 (10.3%); £3,771,987.98 -> £3,382,241.44 (10.3%); £3,771,988.16 -> £3,382,241.57 (10.3%); £3,771,988.35 -> £3,382,241.74 (10.3%); £3,771,988.57 -> £3,382,241.93 (10.3%); £3,771,988.81 -> £3,382,242.13 (10.3%); £3,771,989.06 -> £3,382,242.35 (10.3%); £3,771,989.31 -> £3,382,242.48 (10.3%); £3,771,989.56 -> £3,382,242.61 (10.3%); £3,771,989.82 -> £3,382,242.74 (10.3%); £3,771,990.07 -> £3,382,242.86 (10.3%); £3,771,990.32 -> £3,382,242.99 (10.3%); £3,771,990.57 -> £3,382,243.11 (10.3%); £3,771,990.82 -> £3,382,243.23 (10.3%); £3,771,991.08 -> £3,382,243.35 (10.3%); £3,771,991.33 -> £3,382,243.47 (10.3%); £3,771,991.57 -> £3,382,243.58 (10.3%); £3,771,991.82 -> £3,382,243.70 (10.3%); £3,771,992.07 -> £3,382,243.82 (10.3%); £3,771,992.31 -> £3,382,243.92 (10.3%); £3,771,992.56 -> £3,382,244.13 (10.3%); £3,771,992.82 -> £3,382,244.32 (10.3%); £3,771,993.06 -> £3,382,244.48 (10.3%); £3,771,993.31 -> £3,382,244.63 (10.3%); £3,771,993.56 -> £3,382,244.76 (10.3%); £3,771,993.80 -> £3,382,244.89 (10.3%); £3,771,994.05 -> £3,382,245.02 (10.3%); £3,771,994.31 -> £3,382,245.14 (10.3%); £3,771,994.55 -> £3,382,245.27 (10.3%); £3,771,994.80 -> £3,382,245.38 (10.3%); £3,771,995.04 -> £3,382,245.49 (10.3%); £3,771,995.29 -> £3,382,245.53 (10.3%); £3,771,995.55 -> £3,382,245.58 (10.3%); £3,771,995.79 -> £3,382,245.62 (10.3%); £3,771,996.00 -> £3,382,245.65 (10.3%); £3,771,996.19 -> £3,382,245.69 (10.3%); £3,771,996.34 -> £3,382,245.73 (10.3%); £3,771,996.49 -> £3,382,245.76 (10.3%); £3,771,996.65 -> £3,382,245.80 (10.3%); £3,771,996.80 -> £3,382,245.84 (10.3%); £3,771,996.95 -> £3,382,245.88 (10.3%); £3,771,997.10 -> £3,382,245.91 (10.3%); £3,771,997.25 -> £3,382,245.95 (10.3%); £3,771,997.40 -> £3,382,245.99 (10.3%); £3,771,997.55 -> £3,382,246.03 (10.3%); £3,771,997.71 -> £3,382,246.07 (10.3%); £3,771,997.86 -> £3,382,246.11 (10.3%); £3,771,998.01 -> £3,382,246.21 (10.3%); £3,771,998.15 -> £3,382,246.32 (10.3%); £3,771,998.32 -> £3,382,246.45 (10.3%); £3,771,998.50 -> £3,382,246.58 (10.3%); £3,771,998.70 -> £3,382,246.74 (10.3%); £3,771,998.92 -> £3,382,246.92 (10.3%); £3,771,999.15 -> £3,382,247.11 (10.3%); £3,771,999.40 -> £3,382,247.33 (10.3%); £3,771,999.66 -> £3,382,247.46 (10.3%); £3,771,999.91 -> £3,382,247.58 (10.3%); £3,772,000.16 -> £3,382,247.70 (10.3%); £3,772,000.41 -> £3,382,247.83 (10.3%); £3,772,000.66 -> £3,382,247.95 (10.3%); £3,772,000.92 -> £3,382,248.07 (10.3%); £3,772,001.17 -> £3,382,248.19 (10.3%); £3,772,001.42 -> £3,382,248.30 (10.3%); £3,772,001.67 -> £3,382,248.42 (10.3%); £3,772,001.92 -> £3,382,248.53 (10.3%); £3,772,002.17 -> £3,382,248.65 (10.3%); £3,772,002.43 -> £3,382,248.76 (10.3%); £3,772,002.69 -> £3,382,248.86 (10.3%); £3,772,002.94 -> £3,382,249.06 (10.3%); £3,772,003.20 -> £3,382,249.24 (10.3%); £3,772,003.45 -> £3,382,249.40 (10.3%); £3,772,003.71 -> £3,382,249.54 (10.3%); £3,772,003.97 -> £3,382,249.68 (10.3%); £3,772,004.22 -> £3,382,249.80 (10.3%); £3,772,004.46 -> £3,382,249.93 (10.3%); £3,772,004.72 -> £3,382,250.05 (10.3%); £3,772,004.97 -> £3,382,250.17 (10.3%); £3,772,005.22 -> £3,382,250.28 (10.3%); £3,772,005.47 -> £3,382,250.39 (10.3%); £3,772,005.72 -> £3,382,250.43 (10.3%); £3,772,005.98 -> £3,382,250.48 (10.3%); £3,772,006.20 -> £3,382,250.51 (10.3%); £3,772,006.42 -> £3,382,250.55 (10.3%); £3,772,006.62 -> £3,382,250.59 (10.3%); £3,772,006.77 -> £3,382,250.63 (10.3%); £3,772,006.92 -> £3,382,250.67 (10.3%); £3,772,007.07 -> £3,382,250.70 (10.3%); £3,772,007.22 -> £3,382,250.74 (10.3%); £3,772,007.37 -> £3,382,250.78 (10.3%); £3,772,007.52 -> £3,382,250.82 (10.3%); £3,772,007.68 -> £3,382,250.86 (10.3%); £3,772,007.83 -> £3,382,250.89 (10.3%); £3,772,007.98 -> £3,382,250.93 (10.3%); £3,772,008.13 -> £3,382,250.97 (10.3%); £3,772,008.28 -> £3,382,251.01 (10.3%); £3,772,008.43 -> £3,382,251.16 (10.3%); £3,772,008.58 -> £3,382,251.31 (10.3%); £3,772,008.75 -> £3,382,251.47 (10.3%); £3,772,008.93 -> £3,382,251.65 (10.3%); £3,772,009.14 -> £3,382,251.85 (10.3%); £3,772,009.36 -> £3,382,252.06 (10.3%); £3,772,009.59 -> £3,382,252.29 (10.3%); £3,772,009.85 -> £3,382,252.53 (10.3%); £3,772,010.11 -> £3,382,252.66 (10.3%); £3,772,010.35 -> £3,382,252.79 (10.3%); £3,772,010.60 -> £3,382,252.92 (10.3%); £3,772,010.85 -> £3,382,253.06 (10.3%); £3,772,011.10 -> £3,382,253.20 (10.3%); £3,772,011.35 -> £3,382,253.32 (10.3%); £3,772,011.60 -> £3,382,253.45 (10.3%); £3,772,011.85 -> £3,382,253.57 (10.3%); £3,772,012.11 -> £3,382,253.69 (10.3%); £3,772,012.36 -> £3,382,253.81 (10.3%); £3,772,012.61 -> £3,382,253.93 (10.3%); £3,772,012.86 -> £3,382,254.04 (10.3%); £3,772,013.11 -> £3,382,254.15 (10.3%); £3,772,013.36 -> £3,382,254.38 (10.3%); £3,772,013.62 -> £3,382,254.60 (10.3%); £3,772,013.87 -> £3,382,254.78 (10.3%); £3,772,014.12 -> £3,382,254.95 (10.3%); £3,772,014.37 -> £3,382,255.11 (10.3%); £3,772,014.62 -> £3,382,255.27 (10.3%); £3,772,014.87 -> £3,382,255.41 (10.3%); £3,772,015.12 -> £3,382,255.56 (10.3%); £3,772,015.38 -> £3,382,255.70 (10.3%); £3,772,015.63 -> £3,382,255.84 (10.3%); £3,772,015.89 -> £3,382,255.98 (10.3%); £3,772,016.14 -> £3,382,256.02 (10.3%); £3,772,016.39 -> £3,382,256.06 (10.3%); £3,772,016.62 -> £3,382,256.10 (10.3%); £3,772,016.83 -> £3,382,256.13 (10.3%); £3,772,017.02 -> £3,382,256.17 (10.3%); £3,772,017.16 -> £3,382,256.21 (10.3%); £3,772,017.29 -> £3,382,256.25 (10.3%); £3,772,017.42 -> £3,382,256.28 (10.3%); £3,772,017.56 -> £3,382,256.32 (10.3%); £3,772,017.70 -> £3,382,256.36 (10.3%); £3,772,017.83 -> £3,382,256.39 (10.3%); £3,772,017.97 -> £3,382,256.43 (10.3%); £3,772,018.11 -> £3,382,256.47 (10.3%); £3,772,018.24 -> £3,382,256.51 (10.3%); £3,772,018.37 -> £3,382,256.54 (10.3%); £3,772,018.51 -> £3,382,256.58 (10.3%); £3,772,018.65 -> £3,382,256.75 (10.3%); £3,772,018.79 -> £3,382,256.92 (10.3%); £3,772,018.93 -> £3,382,257.10 (10.3%); £3,772,019.10 -> £3,382,257.29 (10.3%); £3,772,019.28 -> £3,382,257.48 (10.3%); £3,772,019.48 -> £3,382,257.69 (10.3%); £3,772,019.69 -> £3,382,257.92 (10.3%); £3,772,019.91 -> £3,382,258.15 (10.3%); £3,772,020.14 -> £3,382,258.24 (10.3%); £3,772,020.36 -> £3,382,258.34 (10.3%); £3,772,020.58 -> £3,382,258.43 (10.3%); £3,772,020.81 -> £3,382,258.52 (10.3%); £3,772,021.04 -> £3,382,258.60 (10.3%); £3,772,021.26 -> £3,382,258.68 (10.3%); £3,772,021.48 -> £3,382,258.75 (10.3%); £3,772,021.71 -> £3,382,258.83 (10.3%); £3,772,021.92 -> £3,382,258.90 (10.3%); £3,772,022.14 -> £3,382,258.97 (10.3%); £3,772,022.36 -> £3,382,259.03 (10.3%); £3,772,022.58 -> £3,382,259.10 (10.3%); £3,772,022.79 -> £3,382,259.17 (10.3%); £3,772,023.02 -> £3,382,259.37 (10.3%); £3,772,023.25 -> £3,382,259.57 (10.3%); £3,772,023.47 -> £3,382,259.75 (10.3%); £3,772,023.70 -> £3,382,259.93 (10.3%); £3,772,023.92 -> £3,382,260.11 (10.3%); £3,772,024.16 -> £3,382,260.29 (10.3%); £3,772,024.37 -> £3,382,260.46 (10.3%); £3,772,024.60 -> £3,382,260.64 (10.3%); £3,772,024.82 -> £3,382,260.81 (10.3%); £3,772,025.04 -> £3,382,260.98 (10.3%); £3,772,025.27 -> £3,382,261.17 (10.3%); £3,772,025.49 -> £3,382,261.21 (10.3%); £3,772,025.71 -> £3,382,261.25 (10.3%); £3,772,025.91 -> £3,382,261.29 (10.3%); £3,772,026.10 -> £3,382,261.33 (10.3%); £3,772,026.28 -> £3,382,261.36 (10.3%); £3,772,026.41 -> £3,382,261.40 (10.3%); £3,772,026.55 -> £3,382,261.44 (10.3%); £3,772,026.68 -> £3,382,261.48 (10.3%); £3,772,026.81 -> £3,382,261.52 (10.3%); £3,772,026.95 -> £3,382,261.55 (10.3%); £3,772,027.09 -> £3,382,261.59 (10.3%); £3,772,027.22 -> £3,382,261.63 (10.3%); £3,772,027.35 -> £3,382,261.66 (10.3%); £3,772,027.49 -> £3,382,261.70 (10.3%); £3,772,027.63 -> £3,382,261.74 (10.3%); £3,772,027.77 -> £3,382,261.77 (10.3%); £3,772,027.90 -> £3,382,261.87 (10.3%); £3,772,028.04 -> £3,382,261.97 (10.3%); £3,772,028.19 -> £3,382,262.07 (10.3%); £3,772,028.36 -> £3,382,262.18 (10.3%); £3,772,028.54 -> £3,382,262.28 (10.3%); £3,772,028.74 -> £3,382,262.38 (10.3%); £3,772,028.95 -> £3,382,262.49 (10.3%); £3,772,029.18 -> £3,382,262.60 (10.3%); £3,772,029.41 -> £3,382,262.64 (10.3%); £3,772,029.63 -> £3,382,262.69 (10.3%); £3,772,029.85 -> £3,382,262.74 (10.3%); £3,772,030.08 -> £3,382,262.79 (10.3%); £3,772,030.30 -> £3,382,262.83 (10.3%); £3,772,030.53 -> £3,382,262.88 (10.3%); £3,772,030.76 -> £3,382,262.93 (10.3%); £3,772,030.99 -> £3,382,262.97 (10.3%); £3,772,031.21 -> £3,382,263.02 (10.3%); £3,772,031.44 -> £3,382,263.07 (10.3%); £3,772,031.67 -> £3,382,263.11 (10.3%); £3,772,031.90 -> £3,382,263.16 (10.3%); £3,772,032.13 -> £3,382,263.20 (10.3%); £3,772,032.35 -> £3,382,263.32 (10.3%); £3,772,032.57 -> £3,382,263.43 (10.3%); £3,772,032.80 -> £3,382,263.54 (10.3%); £3,772,033.03 -> £3,382,263.66 (10.3%); £3,772,033.26 -> £3,382,263.77 (10.3%); £3,772,033.48 -> £3,382,263.89 (10.3%); £3,772,033.70 -> £3,382,264.00 (10.3%); £3,772,033.93 -> £3,382,264.11 (10.3%); £3,772,034.15 -> £3,382,264.22 (10.3%); £3,772,034.37 -> £3,382,264.33 (10.3%); £3,772,034.60 -> £3,382,264.44 (10.3%); £3,772,034.83 -> £3,382,264.48 (10.3%); £3,772,035.05 -> £3,382,264.52 (10.3%); £3,772,035.27 -> £3,382,264.55 (10.3%); £3,772,035.47 -> £3,382,264.59 (10.3%); £3,772,035.64 -> £3,382,264.63 (10.3%); £3,772,035.80 -> £3,382,264.66 (10.3%); £3,772,035.95 -> £3,382,264.70 (10.3%); £3,772,036.11 -> £3,382,264.74 (10.3%); £3,772,036.26 -> £3,382,264.77 (10.3%); £3,772,036.41 -> £3,382,264.81 (10.3%); £3,772,036.56 -> £3,382,264.85 (10.3%); £3,772,036.72 -> £3,382,264.89 (10.3%); £3,772,036.87 -> £3,382,264.92 (10.3%); £3,772,037.02 -> £3,382,264.96 (10.3%); £3,772,037.17 -> £3,382,265.00 (10.3%); £3,772,037.33 -> £3,382,265.04 (10.3%); £3,772,037.48 -> £3,382,265.18 (10.3%); £3,772,037.64 -> £3,382,265.31 (10.3%); £3,772,037.81 -> £3,382,265.45 (10.3%); £3,772,038.00 -> £3,382,265.60 (10.3%); £3,772,038.20 -> £3,382,265.79 (10.3%); £3,772,038.43 -> £3,382,265.99 (10.3%); £3,772,038.67 -> £3,382,266.22 (10.3%); £3,772,038.93 -> £3,382,266.47 (10.3%); £3,772,039.18 -> £3,382,266.59 (10.3%); £3,772,039.44 -> £3,382,266.72 (10.3%); £3,772,039.69 -> £3,382,266.84 (10.3%); £3,772,039.94 -> £3,382,266.97 (10.3%); £3,772,040.19 -> £3,382,267.10 (10.3%); £3,772,040.44 -> £3,382,267.22 (10.3%); £3,772,040.69 -> £3,382,267.34 (10.3%); £3,772,040.95 -> £3,382,267.46 (10.3%); £3,772,041.22 -> £3,382,267.58 (10.3%); £3,772,041.48 -> £3,382,267.69 (10.3%); £3,772,041.73 -> £3,382,267.80 (10.3%); £3,772,041.99 -> £3,382,267.92 (10.3%); £3,772,042.25 -> £3,382,268.03 (10.3%); £3,772,042.51 -> £3,382,268.27 (10.3%); £3,772,042.77 -> £3,382,268.49 (10.3%); £3,772,043.03 -> £3,382,268.68 (10.3%); £3,772,043.27 -> £3,382,268.84 (10.3%); £3,772,043.54 -> £3,382,268.99 (10.3%); £3,772,043.80 -> £3,382,269.14 (10.3%); £3,772,044.05 -> £3,382,269.29 (10.3%); £3,772,044.30 -> £3,382,269.43 (10.3%); £3,772,044.56 -> £3,382,269.58 (10.3%); £3,772,044.81 -> £3,382,269.72 (10.3%); £3,772,045.07 -> £3,382,269.86 (10.3%); £3,772,045.33 -> £3,382,269.90 (10.3%); £3,772,045.59 -> £3,382,269.94 (10.3%); £3,772,045.82 -> £3,382,269.98 (10.3%); £3,772,046.04 -> £3,382,270.02 (10.3%); £3,772,046.23 -> £3,382,270.06 (10.3%); £3,772,046.39 -> £3,382,270.09 (10.3%); £3,772,046.55 -> £3,382,270.13 (10.3%); £3,772,046.71 -> £3,382,270.17 (10.3%); £3,772,046.86 -> £3,382,270.21 (10.3%); £3,772,047.01 -> £3,382,270.24 (10.3%); £3,772,047.16 -> £3,382,270.28 (10.3%); £3,772,047.32 -> £3,382,270.32 (10.3%); £3,772,047.47 -> £3,382,270.36 (10.3%); £3,772,047.63 -> £3,382,270.40 (10.3%); £3,772,047.78 -> £3,382,270.43 (10.3%); £3,772,047.94 -> £3,382,270.47 (10.3%); £3,772,048.10 -> £3,382,270.59 (10.3%); £3,772,048.25 -> £3,382,270.71 (10.3%); £3,772,048.42 -> £3,382,270.84 (10.3%); £3,772,048.62 -> £3,382,270.98 (10.3%); £3,772,048.83 -> £3,382,271.15 (10.3%); £3,772,049.05 -> £3,382,271.35 (10.3%); £3,772,049.29 -> £3,382,271.58 (10.3%); £3,772,049.55 -> £3,382,271.80 (10.3%); £3,772,049.80 -> £3,382,271.92 (10.3%); £3,772,050.06 -> £3,382,272.05 (10.3%); £3,772,050.31 -> £3,382,272.19 (10.3%); £3,772,050.57 -> £3,382,272.31 (10.3%); £3,772,050.82 -> £3,382,272.44 (10.3%); £3,772,051.08 -> £3,382,272.56 (10.3%); £3,772,051.35 -> £3,382,272.67 (10.3%); £3,772,051.61 -> £3,382,272.79 (10.3%); £3,772,051.88 -> £3,382,272.90 (10.3%); £3,772,052.14 -> £3,382,273.01 (10.3%); £3,772,052.40 -> £3,382,273.13 (10.3%); £3,772,052.66 -> £3,382,273.24 (10.3%); £3,772,052.91 -> £3,382,273.35 (10.3%); £3,772,053.16 -> £3,382,273.56 (10.3%); £3,772,053.42 -> £3,382,273.75 (10.3%); £3,772,053.68 -> £3,382,273.91 (10.3%); £3,772,053.94 -> £3,382,274.04 (10.3%); £3,772,054.19 -> £3,382,274.17 (10.3%); £3,772,054.45 -> £3,382,274.31 (10.3%); £3,772,054.71 -> £3,382,274.44 (10.3%); £3,772,054.98 -> £3,382,274.57 (10.3%); £3,772,055.23 -> £3,382,274.70 (10.3%); £3,772,055.48 -> £3,382,274.82 (10.3%); £3,772,055.74 -> £3,382,274.93 (10.3%); £3,772,056.00 -> £3,382,274.97 (10.3%); £3,772,056.25 -> £3,382,275.01 (10.3%); £3,772,056.49 -> £3,382,275.05 (10.3%); £3,772,056.71 -> £3,382,275.09 (10.3%); £3,772,056.90 -> £3,382,275.13 (10.3%); £3,772,057.06 -> £3,382,275.16 (10.3%); £3,772,057.22 -> £3,382,275.20 (10.3%); £3,772,057.36 -> £3,382,275.24 (10.3%); £3,772,057.52 -> £3,382,275.27 (10.3%); £3,772,057.67 -> £3,382,275.31 (10.3%); £3,772,057.82 -> £3,382,275.35 (10.3%); £3,772,057.98 -> £3,382,275.38 (10.3%); £3,772,058.14 -> £3,382,275.42 (10.3%); £3,772,058.29 -> £3,382,275.46 (10.3%); £3,772,058.45 -> £3,382,275.50 (10.3%); £3,772,058.61 -> £3,382,275.54 (10.3%); £3,772,058.77 -> £3,382,275.67 (10.3%); £3,772,058.92 -> £3,382,275.81 (10.3%); £3,772,059.09 -> £3,382,275.96 (10.3%); £3,772,059.28 -> £3,382,276.12 (10.3%); £3,772,059.49 -> £3,382,276.30 (10.3%); £3,772,059.72 -> £3,382,276.50 (10.3%); £3,772,059.96 -> £3,382,276.73 (10.3%); £3,772,060.22 -> £3,382,276.96 (10.3%); £3,772,060.48 -> £3,382,277.08 (10.3%); £3,772,060.73 -> £3,382,277.21 (10.3%); £3,772,060.98 -> £3,382,277.34 (10.3%); £3,772,061.24 -> £3,382,277.47 (10.3%); £3,772,061.50 -> £3,382,277.59 (10.3%); £3,772,061.76 -> £3,382,277.71 (10.3%); £3,772,062.01 -> £3,382,277.83 (10.3%); £3,772,062.26 -> £3,382,277.94 (10.3%); £3,772,062.51 -> £3,382,278.05 (10.3%); £3,772,062.77 -> £3,382,278.17 (10.3%); £3,772,063.03 -> £3,382,278.28 (10.3%); £3,772,063.28 -> £3,382,278.40 (10.3%); £3,772,063.55 -> £3,382,278.51 (10.3%); £3,772,063.80 -> £3,382,278.75 (10.3%); £3,772,064.06 -> £3,382,278.97 (10.3%); £3,772,064.32 -> £3,382,279.13 (10.3%); £3,772,064.58 -> £3,382,279.28 (10.3%); £3,772,064.83 -> £3,382,279.43 (10.3%); £3,772,065.10 -> £3,382,279.57 (10.3%); £3,772,065.35 -> £3,382,279.72 (10.3%); £3,772,065.61 -> £3,382,279.86 (10.3%); £3,772,065.86 -> £3,382,280.01 (10.3%); £3,772,066.12 -> £3,382,280.15 (10.3%); £3,772,066.37 -> £3,382,280.29 (10.3%); £3,772,066.62 -> £3,382,280.33 (10.3%); £3,772,066.88 -> £3,382,280.37 (10.3%); £3,772,067.13 -> £3,382,280.41 (10.3%); £3,772,067.35 -> £3,382,280.44 (10.3%); £3,772,067.55 -> £3,382,280.48 (10.3%); £3,772,067.71 -> £3,382,280.52 (10.3%); £3,772,067.86 -> £3,382,280.56 (10.3%); £3,772,068.01 -> £3,382,280.59 (10.3%); £3,772,068.16 -> £3,382,280.63 (10.3%); £3,772,068.32 -> £3,382,280.67 (10.3%); £3,772,068.47 -> £3,382,280.71 (10.3%); £3,772,068.62 -> £3,382,280.74 (10.3%); £3,772,068.77 -> £3,382,280.78 (10.3%); £3,772,068.92 -> £3,382,280.82 (10.3%); £3,772,069.08 -> £3,382,280.86 (10.3%); £3,772,069.23 -> £3,382,280.90 (10.3%); £3,772,069.38 -> £3,382,281.05 (10.3%); £3,772,069.54 -> £3,382,281.20 (10.3%); £3,772,069.71 -> £3,382,281.36 (10.3%); £3,772,069.89 -> £3,382,281.54 (10.3%); £3,772,070.10 -> £3,382,281.73 (10.3%); £3,772,070.32 -> £3,382,281.95 (10.3%); £3,772,070.56 -> £3,382,282.19 (10.3%); £3,772,070.81 -> £3,382,282.44 (10.3%); £3,772,071.07 -> £3,382,282.56 (10.3%); £3,772,071.33 -> £3,382,282.69 (10.3%); £3,772,071.58 -> £3,382,282.82 (10.3%); £3,772,071.84 -> £3,382,282.95 (10.3%); £3,772,072.10 -> £3,382,283.08 (10.3%); £3,772,072.35 -> £3,382,283.21 (10.3%); £3,772,072.61 -> £3,382,283.32 (10.3%); £3,772,072.86 -> £3,382,283.44 (10.3%); £3,772,073.11 -> £3,382,283.55 (10.3%); £3,772,073.37 -> £3,382,283.67 (10.3%); £3,772,073.63 -> £3,382,283.78 (10.3%); £3,772,073.88 -> £3,382,283.89 (10.3%); £3,772,074.14 -> £3,382,284.00 (10.3%); £3,772,074.40 -> £3,382,284.25 (10.3%); £3,772,074.64 -> £3,382,284.48 (10.3%); £3,772,074.90 -> £3,382,284.68 (10.3%); £3,772,075.16 -> £3,382,284.86 (10.3%); £3,772,075.42 -> £3,382,285.03 (10.3%); £3,772,075.68 -> £3,382,285.20 (10.3%); £3,772,075.93 -> £3,382,285.37 (10.3%); £3,772,076.19 -> £3,382,285.53 (10.3%); £3,772,076.44 -> £3,382,285.69 (10.3%); £3,772,076.69 -> £3,382,285.84 (10.3%); £3,772,076.95 -> £3,382,286.00 (10.3%); £3,772,077.20 -> £3,382,286.04 (10.3%); £3,772,077.45 -> £3,382,286.08 (10.3%); £3,772,077.69 -> £3,382,286.12 (10.3%); £3,772,077.91 -> £3,382,286.16 (10.3%); £3,772,078.11 -> £3,382,286.19 (10.3%); £3,772,078.27 -> £3,382,286.23 (10.3%); £3,772,078.42 -> £3,382,286.27 (10.3%); £3,772,078.57 -> £3,382,286.31 (10.3%); £3,772,078.73 -> £3,382,286.35 (10.3%); £3,772,078.88 -> £3,382,286.39 (10.3%); £3,772,079.03 -> £3,382,286.43 (10.3%); £3,772,079.18 -> £3,382,286.47 (10.3%); £3,772,079.33 -> £3,382,286.50 (10.3%); £3,772,079.48 -> £3,382,286.54 (10.3%); £3,772,079.63 -> £3,382,286.58 (10.3%); £3,772,079.79 -> £3,382,286.62 (10.3%); £3,772,079.94 -> £3,382,286.77 (10.3%); £3,772,080.10 -> £3,382,286.93 (10.3%); £3,772,080.27 -> £3,382,287.11 (10.3%); £3,772,080.46 -> £3,382,287.29 (10.3%); £3,772,080.67 -> £3,382,287.49 (10.3%); £3,772,080.89 -> £3,382,287.72 (10.3%); £3,772,081.13 -> £3,382,287.98 (10.3%); £3,772,081.39 -> £3,382,288.24 (10.3%); £3,772,081.65 -> £3,382,288.37 (10.3%); £3,772,081.92 -> £3,382,288.49 (10.3%); £3,772,082.17 -> £3,382,288.62 (10.3%); £3,772,082.43 -> £3,382,288.76 (10.3%); £3,772,082.69 -> £3,382,288.88 (10.3%); £3,772,082.95 -> £3,382,289.01 (10.3%); £3,772,083.21 -> £3,382,289.12 (10.3%); £3,772,083.46 -> £3,382,289.25 (10.3%); £3,772,083.72 -> £3,382,289.37 (10.3%); £3,772,083.97 -> £3,382,289.49 (10.3%); £3,772,084.23 -> £3,382,289.62 (10.3%); £3,772,084.49 -> £3,382,289.73 (10.3%); £3,772,084.75 -> £3,382,289.84 (10.3%); £3,772,085.00 -> £3,382,290.10 (10.3%); £3,772,085.26 -> £3,382,290.33 (10.3%); £3,772,085.52 -> £3,382,290.53 (10.3%); £3,772,085.78 -> £3,382,290.71 (10.3%); £3,772,086.03 -> £3,382,290.89 (10.3%); £3,772,086.29 -> £3,382,291.05 (10.3%); £3,772,086.55 -> £3,382,291.22 (10.3%); £3,772,086.81 -> £3,382,291.38 (10.3%); £3,772,087.07 -> £3,382,291.54 (10.3%); £3,772,087.33 -> £3,382,291.70 (10.3%); £3,772,087.58 -> £3,382,291.86 (10.3%); £3,772,087.84 -> £3,382,291.90 (10.3%); £3,772,088.10 -> £3,382,291.94 (10.3%); £3,772,088.34 -> £3,382,291.98 (10.3%); £3,772,088.56 -> £3,382,292.02 (10.3%); £3,772,088.76 -> £3,382,292.06 (10.3%); £3,772,088.90 -> £3,382,292.10 (10.3%); £3,772,089.03 -> £3,382,292.14 (10.3%); £3,772,089.17 -> £3,382,292.18 (10.3%); £3,772,089.31 -> £3,382,292.22 (10.3%); £3,772,089.44 -> £3,382,292.25 (10.3%); £3,772,089.58 -> £3,382,292.29 (10.3%); £3,772,089.72 -> £3,382,292.33 (10.3%); £3,772,089.86 -> £3,382,292.37 (10.3%); £3,772,089.99 -> £3,382,292.41 (10.3%); £3,772,090.13 -> £3,382,292.45 (10.3%); £3,772,090.26 -> £3,382,292.49 (10.3%); £3,772,090.40 -> £3,382,292.69 (10.3%); £3,772,090.53 -> £3,382,292.89 (10.3%); £3,772,090.68 -> £3,382,293.10 (10.3%); £3,772,090.84 -> £3,382,293.32 (10.3%); £3,772,091.03 -> £3,382,293.55 (10.3%); £3,772,091.23 -> £3,382,293.80 (10.3%); £3,772,091.44 -> £3,382,294.06 (10.3%); £3,772,091.66 -> £3,382,294.34 (10.3%); £3,772,091.89 -> £3,382,294.43 (10.3%); £3,772,092.12 -> £3,382,294.53 (10.3%); £3,772,092.35 -> £3,382,294.63 (10.3%); £3,772,092.57 -> £3,382,294.73 (10.3%); £3,772,092.80 -> £3,382,294.81 (10.3%); £3,772,093.03 -> £3,382,294.90 (10.3%); £3,772,093.25 -> £3,382,294.98 (10.3%); £3,772,093.49 -> £3,382,295.06 (10.3%); £3,772,093.71 -> £3,382,295.13 (10.3%); £3,772,093.93 -> £3,382,295.20 (10.3%); £3,772,094.15 -> £3,382,295.27 (10.3%); £3,772,094.38 -> £3,382,295.35 (10.3%); £3,772,094.60 -> £3,382,295.42 (10.3%); £3,772,094.83 -> £3,382,295.65 (10.3%); £3,772,095.07 -> £3,382,295.87 (10.3%); £3,772,095.29 -> £3,382,296.07 (10.3%); £3,772,095.53 -> £3,382,296.27 (10.3%); £3,772,095.76 -> £3,382,296.46 (10.3%); £3,772,095.98 -> £3,382,296.66 (10.3%); £3,772,096.21 -> £3,382,296.85 (10.3%); £3,772,096.43 -> £3,382,297.06 (10.3%); £3,772,096.66 -> £3,382,297.27 (10.3%); £3,772,096.89 -> £3,382,297.45 (10.3%); £3,772,097.11 -> £3,382,297.65 (10.3%); £3,772,097.34 -> £3,382,297.70 (10.3%); £3,772,097.56 -> £3,382,297.74 (10.3%); £3,772,097.77 -> £3,382,297.78 (10.3%); £3,772,097.96 -> £3,382,297.82 (10.3%); £3,772,098.13 -> £3,382,297.86 (10.3%); £3,772,098.28 -> £3,382,297.90 (10.3%); £3,772,098.42 -> £3,382,297.94 (10.3%); £3,772,098.56 -> £3,382,297.98 (10.3%); £3,772,098.70 -> £3,382,298.02 (10.3%); £3,772,098.84 -> £3,382,298.05 (10.3%); £3,772,098.98 -> £3,382,298.09 (10.3%); £3,772,099.12 -> £3,382,298.13 (10.3%); £3,772,099.26 -> £3,382,298.17 (10.3%); £3,772,099.41 -> £3,382,298.20 (10.3%); £3,772,099.54 -> £3,382,298.24 (10.3%); £3,772,099.69 -> £3,382,298.28 (10.3%); £3,772,099.83 -> £3,382,298.45 (10.3%); £3,772,099.98 -> £3,382,298.63 (10.3%); £3,772,100.13 -> £3,382,298.81 (10.3%); £3,772,100.30 -> £3,382,298.99 (10.3%); £3,772,100.49 -> £3,382,299.17 (10.3%); £3,772,100.69 -> £3,382,299.36 (10.3%); £3,772,100.90 -> £3,382,299.54 (10.3%); £3,772,101.13 -> £3,382,299.73 (10.3%); £3,772,101.37 -> £3,382,299.78 (10.3%); £3,772,101.61 -> £3,382,299.83 (10.3%); £3,772,101.84 -> £3,382,299.88 (10.3%); £3,772,102.07 -> £3,382,299.93 (10.3%); £3,772,102.29 -> £3,382,299.98 (10.3%); £3,772,102.53 -> £3,382,300.02 (10.3%); £3,772,102.76 -> £3,382,300.07 (10.3%); £3,772,102.99 -> £3,382,300.12 (10.3%); £3,772,103.22 -> £3,382,300.16 (10.3%); £3,772,103.45 -> £3,382,300.21 (10.3%); £3,772,103.69 -> £3,382,300.26 (10.3%); £3,772,103.92 -> £3,382,300.30 (10.3%); £3,772,104.15 -> £3,382,300.35 (10.3%); £3,772,104.39 -> £3,382,300.52 (10.3%); £3,772,104.62 -> £3,382,300.69 (10.3%); £3,772,104.85 -> £3,382,300.86 (10.3%); £3,772,105.08 -> £3,382,301.03 (10.3%); £3,772,105.32 -> £3,382,301.20 (10.3%); £3,772,105.55 -> £3,382,301.37 (10.3%); £3,772,105.78 -> £3,382,301.53 (10.3%); £3,772,106.02 -> £3,382,301.70 (10.3%); £3,772,106.26 -> £3,382,301.86 (10.3%); £3,772,106.49 -> £3,382,302.03 (10.3%); £3,772,106.73 -> £3,382,302.20 (10.3%); £3,772,106.97 -> £3,382,302.24 (10.3%); £3,772,107.20 -> £3,382,302.28 (10.3%); £3,772,107.43 -> £3,382,302.32 (10.3%); £3,772,107.63 -> £3,382,302.35 (10.3%); £3,772,107.80 -> £3,382,302.39 (10.3%); £3,772,107.96 -> £3,382,302.43 (10.3%); £3,772,108.12 -> £3,382,302.47 (10.3%); £3,772,108.28 -> £3,382,302.50 (10.3%); £3,772,108.45 -> £3,382,302.54 (10.3%); £3,772,108.61 -> £3,382,302.58 (10.3%); £3,772,108.77 -> £3,382,302.62 (10.3%); £3,772,108.93 -> £3,382,302.65 (10.3%); £3,772,109.10 -> £3,382,302.69 (10.3%); £3,772,109.26 -> £3,382,302.73 (10.3%); £3,772,109.42 -> £3,382,302.77 (10.3%); £3,772,109.58 -> £3,382,302.81 (10.3%); £3,772,109.74 -> £3,382,302.98 (10.3%); £3,772,109.90 -> £3,382,303.16 (10.3%); £3,772,110.08 -> £3,382,303.35 (10.3%); £3,772,110.28 -> £3,382,303.55 (10.3%); £3,772,110.50 -> £3,382,303.78 (10.3%); £3,772,110.73 -> £3,382,304.03 (10.3%); £3,772,110.98 -> £3,382,304.30 (10.3%); £3,772,111.26 -> £3,382,304.59 (10.3%); £3,772,111.52 -> £3,382,304.71 (10.3%); £3,772,111.81 -> £3,382,304.84 (10.3%); £3,772,112.08 -> £3,382,304.97 (10.3%); £3,772,112.35 -> £3,382,305.10 (10.3%); £3,772,112.61 -> £3,382,305.23 (10.3%); £3,772,112.89 -> £3,382,305.35 (10.3%); £3,772,113.15 -> £3,382,305.47 (10.3%); £3,772,113.42 -> £3,382,305.59 (10.3%); £3,772,113.70 -> £3,382,305.71 (10.3%); £3,772,113.97 -> £3,382,305.83 (10.3%); £3,772,114.24 -> £3,382,305.94 (10.3%); £3,772,114.52 -> £3,382,306.06 (10.3%); £3,772,114.79 -> £3,382,306.16 (10.3%); £3,772,115.06 -> £3,382,306.41 (10.3%); £3,772,115.32 -> £3,382,306.65 (10.3%); £3,772,115.59 -> £3,382,306.86 (10.3%); £3,772,115.85 -> £3,382,307.05 (10.3%); £3,772,116.11 -> £3,382,307.24 (10.3%); £3,772,116.38 -> £3,382,307.42 (10.3%); £3,772,116.64 -> £3,382,307.60 (10.3%); £3,772,116.91 -> £3,382,307.78 (10.3%); £3,772,117.18 -> £3,382,307.95 (10.3%); £3,772,117.45 -> £3,382,308.12 (10.3%); £3,772,117.71 -> £3,382,308.29 (10.3%); £3,772,117.98 -> £3,382,308.33 (10.3%); £3,772,118.25 -> £3,382,308.37 (10.3%); £3,772,118.49 -> £3,382,308.41 (10.3%); £3,772,118.71 -> £3,382,308.45 (10.3%); £3,772,118.93 -> £3,382,308.48 (10.3%); £3,772,119.09 -> £3,382,308.52 (10.3%); £3,772,119.25 -> £3,382,308.56 (10.3%); £3,772,119.42 -> £3,382,308.60 (10.3%); £3,772,119.58 -> £3,382,308.64 (10.3%); £3,772,119.75 -> £3,382,308.67 (10.3%); £3,772,119.91 -> £3,382,308.71 (10.3%); £3,772,120.07 -> £3,382,308.75 (10.3%); £3,772,120.23 -> £3,382,308.78 (10.3%); £3,772,120.39 -> £3,382,308.82 (10.3%); £3,772,120.56 -> £3,382,308.86 (10.3%); £3,772,120.72 -> £3,382,308.90 (10.3%); £3,772,120.88 -> £3,382,309.04 (10.3%); £3,772,121.04 -> £3,382,309.19 (10.3%); £3,772,121.22 -> £3,382,309.36 (10.3%); £3,772,121.42 -> £3,382,309.54 (10.3%); £3,772,121.64 -> £3,382,309.74 (10.3%); £3,772,121.87 -> £3,382,309.97 (10.3%); £3,772,122.12 -> £3,382,310.21 (10.3%); £3,772,122.39 -> £3,382,310.47 (10.3%); £3,772,122.66 -> £3,382,310.60 (10.3%); £3,772,122.95 -> £3,382,310.73 (10.3%); £3,772,123.21 -> £3,382,310.86 (10.3%); £3,772,123.47 -> £3,382,310.99 (10.3%); £3,772,123.73 -> £3,382,311.12 (10.3%); £3,772,124.00 -> £3,382,311.24 (10.3%); £3,772,124.27 -> £3,382,311.36 (10.3%); £3,772,124.54 -> £3,382,311.48 (10.3%); £3,772,124.80 -> £3,382,311.60 (10.3%); £3,772,125.06 -> £3,382,311.71 (10.3%); £3,772,125.34 -> £3,382,311.82 (10.3%); £3,772,125.61 -> £3,382,311.93 (10.3%); £3,772,125.88 -> £3,382,312.04 (10.3%); £3,772,126.16 -> £3,382,312.29 (10.3%); £3,772,126.42 -> £3,382,312.51 (10.3%); £3,772,126.69 -> £3,382,312.70 (10.3%); £3,772,126.96 -> £3,382,312.87 (10.3%); £3,772,127.23 -> £3,382,313.04 (10.3%); £3,772,127.49 -> £3,382,313.20 (10.3%); £3,772,127.76 -> £3,382,313.36 (10.3%); £3,772,128.02 -> £3,382,313.52 (10.3%); £3,772,128.28 -> £3,382,313.68 (10.3%); £3,772,128.56 -> £3,382,313.83 (10.3%); £3,772,128.83 -> £3,382,313.98 (10.3%); £3,772,129.10 -> £3,382,314.02 (10.3%); £3,772,129.37 -> £3,382,314.06 (10.3%); £3,772,129.62 -> £3,382,314.10 (10.3%); £3,772,129.85 -> £3,382,314.14 (10.3%); £3,772,130.06 -> £3,382,314.18 (10.3%); £3,772,130.23 -> £3,382,314.21 (10.3%); £3,772,130.39 -> £3,382,314.25 (10.3%); £3,772,130.54 -> £3,382,314.29 (10.3%); £3,772,130.70 -> £3,382,314.33 (10.3%); £3,772,130.86 -> £3,382,314.37 (10.3%); £3,772,131.02 -> £3,382,314.40 (10.3%); £3,772,131.18 -> £3,382,314.44 (10.3%); £3,772,131.34 -> £3,382,314.48 (10.3%); £3,772,131.49 -> £3,382,314.52 (10.3%); £3,772,131.65 -> £3,382,314.56 (10.3%); £3,772,131.81 -> £3,382,314.60 (10.3%); £3,772,131.97 -> £3,382,314.77 (10.3%); £3,772,132.13 -> £3,382,314.95 (10.3%); £3,772,132.31 -> £3,382,315.14 (10.3%); £3,772,132.51 -> £3,382,315.35 (10.3%); £3,772,132.73 -> £3,382,315.57 (10.3%); £3,772,132.96 -> £3,382,315.81 (10.3%); £3,772,133.21 -> £3,382,316.08 (10.3%); £3,772,133.48 -> £3,382,316.35 (10.3%); £3,772,133.75 -> £3,382,316.48 (10.3%); £3,772,134.01 -> £3,382,316.60 (10.3%); £3,772,134.29 -> £3,382,316.73 (10.3%); £3,772,134.55 -> £3,382,316.86 (10.3%); £3,772,134.82 -> £3,382,316.98 (10.3%); £3,772,135.09 -> £3,382,317.10 (10.3%); £3,772,135.36 -> £3,382,317.22 (10.3%); £3,772,135.64 -> £3,382,317.33 (10.3%); £3,772,135.92 -> £3,382,317.45 (10.3%); £3,772,136.18 -> £3,382,317.58 (10.3%); £3,772,136.45 -> £3,382,317.70 (10.3%); £3,772,136.72 -> £3,382,317.82 (10.3%); £3,772,136.99 -> £3,382,317.93 (10.3%); £3,772,137.26 -> £3,382,318.21 (10.3%); £3,772,137.53 -> £3,382,318.47 (10.3%); £3,772,137.80 -> £3,382,318.70 (10.3%); £3,772,138.07 -> £3,382,318.91 (10.3%); £3,772,138.34 -> £3,382,319.10 (10.3%); £3,772,138.61 -> £3,382,319.29 (10.3%); £3,772,138.88 -> £3,382,319.47 (10.3%); £3,772,139.14 -> £3,382,319.65 (10.3%); £3,772,139.41 -> £3,382,319.83 (10.3%); £3,772,139.68 -> £3,382,320.00 (10.3%); £3,772,139.95 -> £3,382,320.17 (10.3%); £3,772,140.22 -> £3,382,320.21 (10.3%); £3,772,140.50 -> £3,382,320.25 (10.3%); £3,772,140.74 -> £3,382,320.29 (10.3%); £3,772,140.97 -> £3,382,320.33 (10.3%); £3,772,141.18 -> £3,382,320.37 (10.3%); £3,772,141.34 -> £3,382,320.40 (10.3%); £3,772,141.50 -> £3,382,320.44 (10.3%); £3,772,141.66 -> £3,382,320.48 (10.3%); £3,772,141.82 -> £3,382,320.51 (10.3%); £3,772,141.98 -> £3,382,320.55 (10.3%); £3,772,142.14 -> £3,382,320.59 (10.3%); £3,772,142.30 -> £3,382,320.63 (10.3%); £3,772,142.46 -> £3,382,320.67 (10.3%); £3,772,142.62 -> £3,382,320.71 (10.3%); £3,772,142.78 -> £3,382,320.75 (10.3%); £3,772,142.95 -> £3,382,320.79 (10.3%); £3,772,143.11 -> £3,382,320.97 (10.3%); £3,772,143.27 -> £3,382,321.15 (10.3%); £3,772,143.46 -> £3,382,321.35 (10.3%); £3,772,143.66 -> £3,382,321.55 (10.3%); £3,772,143.88 -> £3,382,321.77 (10.3%); £3,772,144.11 -> £3,382,322.02 (10.3%); £3,772,144.36 -> £3,382,322.28 (10.3%); £3,772,144.63 -> £3,382,322.55 (10.3%); £3,772,144.90 -> £3,382,322.67 (10.3%); £3,772,145.17 -> £3,382,322.80 (10.3%); £3,772,145.44 -> £3,382,322.92 (10.3%); £3,772,145.71 -> £3,382,323.04 (10.3%); £3,772,145.99 -> £3,382,323.17 (10.3%); £3,772,146.26 -> £3,382,323.29 (10.3%); £3,772,146.53 -> £3,382,323.40 (10.3%); £3,772,146.80 -> £3,382,323.52 (10.3%); £3,772,147.08 -> £3,382,323.63 (10.3%); £3,772,147.35 -> £3,382,323.75 (10.3%); £3,772,147.62 -> £3,382,323.86 (10.3%); £3,772,147.89 -> £3,382,323.97 (10.3%); £3,772,148.16 -> £3,382,324.08 (10.3%); £3,772,148.45 -> £3,382,324.35 (10.3%); £3,772,148.72 -> £3,382,324.59 (10.3%); £3,772,148.99 -> £3,382,324.80 (10.3%); £3,772,149.25 -> £3,382,325.00 (10.3%); £3,772,149.52 -> £3,382,325.19 (10.3%); £3,772,149.79 -> £3,382,325.37 (10.3%); £3,772,150.08 -> £3,382,325.55 (10.3%); £3,772,150.35 -> £3,382,325.72 (10.3%); £3,772,150.63 -> £3,382,325.90 (10.3%); £3,772,150.90 -> £3,382,326.06 (10.3%); £3,772,151.16 -> £3,382,326.23 (10.3%); £3,772,151.45 -> £3,382,326.27 (10.3%); £3,772,151.72 -> £3,382,326.31 (10.3%); £3,772,151.97 -> £3,382,326.35 (10.3%); £3,772,152.21 -> £3,382,326.38 (10.3%); £3,772,152.43 -> £3,382,326.42 (10.3%); £3,772,152.58 -> £3,382,326.46 (10.3%); £3,772,152.75 -> £3,382,326.49 (10.3%); £3,772,152.91 -> £3,382,326.53 (10.3%); £3,772,153.08 -> £3,382,326.57 (10.3%); £3,772,153.23 -> £3,382,326.61 (10.3%); £3,772,153.40 -> £3,382,326.64 (10.3%); £3,772,153.56 -> £3,382,326.68 (10.3%); £3,772,153.73 -> £3,382,326.72 (10.3%); £3,772,153.89 -> £3,382,326.75 (10.3%); £3,772,154.05 -> £3,382,326.79 (10.3%); £3,772,154.21 -> £3,382,326.83 (10.3%); £3,772,154.37 -> £3,382,326.98 (10.3%); £3,772,154.53 -> £3,382,327.15 (10.3%); £3,772,154.71 -> £3,382,327.32 (10.3%); £3,772,154.91 -> £3,382,327.50 (10.3%); £3,772,155.12 -> £3,382,327.71 (10.3%); £3,772,155.36 -> £3,382,327.93 (10.3%); £3,772,155.61 -> £3,382,328.18 (10.3%); £3,772,155.87 -> £3,382,328.44 (10.3%); £3,772,156.15 -> £3,382,328.56 (10.3%); £3,772,156.41 -> £3,382,328.69 (10.3%); £3,772,156.68 -> £3,382,328.82 (10.3%); £3,772,156.95 -> £3,382,328.95 (10.3%); £3,772,157.22 -> £3,382,329.08 (10.3%); £3,772,157.49 -> £3,382,329.20 (10.3%); £3,772,157.77 -> £3,382,329.31 (10.3%); £3,772,158.05 -> £3,382,329.42 (10.3%); £3,772,158.31 -> £3,382,329.54 (10.3%); £3,772,158.58 -> £3,382,329.66 (10.3%); £3,772,158.85 -> £3,382,329.77 (10.3%); £3,772,159.12 -> £3,382,329.87 (10.3%); £3,772,159.39 -> £3,382,329.98 (10.3%); £3,772,159.65 -> £3,382,330.23 (10.3%); £3,772,159.93 -> £3,382,330.46 (10.3%); £3,772,160.20 -> £3,382,330.67 (10.3%); £3,772,160.47 -> £3,382,330.85 (10.3%); £3,772,160.74 -> £3,382,331.03 (10.3%); £3,772,161.01 -> £3,382,331.20 (10.3%); £3,772,161.29 -> £3,382,331.37 (10.3%); £3,772,161.55 -> £3,382,331.54 (10.3%); £3,772,161.82 -> £3,382,331.71 (10.3%); £3,772,162.10 -> £3,382,331.88 (10.3%); £3,772,162.37 -> £3,382,332.03 (10.3%); £3,772,162.64 -> £3,382,332.07 (10.3%); £3,772,162.91 -> £3,382,332.11 (10.3%); £3,772,163.16 -> £3,382,332.15 (10.3%); £3,772,163.40 -> £3,382,575.36 (10.3%)
- Bills issued: 153, average clarity 0.790, average bill shock 22.8%, bad debt provision £-66.78, avg complaint probability 5.5%
- Solvency signal: £343,191/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2024 produced a net gain of £347,768.66 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 49 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £120,992.97 (gross £518,611.38, capital £5,646.89)
  - Electricity: gross £464,863.13, capital £5,633.65, net £116,452.84
  - Gas: gross £53,748.25, capital £13.23, net £4,540.12
- Treasury at year end: £3,827,043.26
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
- Average CLV (Point-in-Time, year-end 2025): £361,143.41
  - By billing account: C1 £3,385.93, C1_2 £3,572.27, C2 £4,120.20, C3 £3,784.18, C4 £2,236.78, C5 £6,507.60, C6 £13,097.23, C7 £5,846.15, C8 £6,249.07, C9 £6,617.37, C_IC1 £1,073,429.56, C_IC2 £766,140.36, C_IC3 £2,039,343.77, C_IC4 £1,121,677.29
- Bill shock events (>=20%): 26 -- C7 2025-04-30 (36%); C7 2025-05-31 (37%); C7 2025-06-07 (157%); C2 2025-04-30 (23%); C2g 2025-01-31 (32%); C2g 2025-02-28 (24%); C2g 2025-04-30 (30%); C2g 2025-05-31 (34%); C2g 2025-06-07 (73%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (40%); C8 2025-05-31 (42%); C8 2025-06-07 (195%); C9 2025-04-30 (24%); C9 2025-05-31 (33%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C1_2 2025-01-31 (36%); C1_2 2025-02-28 (46%); C1_2 2025-03-31 (34%); C1_2 2025-04-30 (26%); C1_2 2025-05-31 (132%); C1_2 2025-06-07 (71%)
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
- Bills issued: 66, average clarity 0.776, average bill shock 27.4%, bad debt provision £0.00, avg complaint probability 6.0%
- Solvency signal: £425,227/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-20.68 vs. naked (unhedged) net margin: £199.65
- hedging cost £220.33 vs. a fully unhedged book (commodity-only: actual net £-20.68 vs. naked net £199.65)
  - C2: actual £0.57 vs. naked £84.47 -- hedging cost £83.90
  - C2g: actual £8.83 vs. naked £-3.72 -- hedging added £12.55
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £120,992.97 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 26 customer(s) experienced a bill shock of >=20%.
