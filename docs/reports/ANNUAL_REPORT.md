# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,902,115.42
  (£1,435,479.20 net change)
- Solvency signal (final year): £425,239/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £22,565,070.06
  VAT remitted to HMRC: (£3,739,831.76) | Revenue (ex-VAT): £18,825,238.30
  Non-commodity pass-through: (£4,782,360.86)
- Gross margin: £6,445,219.04
- Capital costs: £51,258.88
- Net margin: £6,393,960.15
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1588, average clarity 0.814,
  service quality score 0.904
- Enterprise value (CLV sum across 14 billing accounts): £7,807,956.41
- Cost to serve (whole portfolio): £18,730.56, net margin after cost to serve: £6,375,229.60
- Hedge effectiveness (whole window): hedging cost £4,222,642.22 vs. a fully unhedged book (commodity-only: actual net £1,435,479.20 vs. naked net £5,658,121.42)

- **2021** (crisis year): net margin £75,537.91, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £337,384.05, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2248, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 230.5x (net £65,145.56 on £282.61 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 3/5 departures (60%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 4.7%, max 16.5% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +34.0% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 34.0% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,445,219.04, capital £51,258.88, net £6,393,960.15. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £75,537.91 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,393,960.15
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,658,121.42
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,222,642.22 vs. a fully unhedged book (commodity-only: actual net £1,435,479.20 vs. naked net £5,658,121.42)
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
| 2016 | £0.00 | £0.00 | £85.08 | £657.33 | £324.29 | £1,066.70 |
| 2017 | £30,139.92 | £0.00 | £324.35 | £929.68 | £516.54 | £31,910.49 |
| 2018 | £101,156.41 | £0.00 | £-425.10 | £450.71 | £436.94 | £101,618.96 |
| 2019 | £222,407.12 | £9,999.92 | £279.41 | £805.72 | £489.73 | £233,981.90 |
| 2020 | £116,561.53 | £10,030.76 | £398.14 | £1,034.19 | £457.36 | £128,481.98 |
| 2021 | £64,952.49 | £9,999.92 | £295.82 | £466.40 | £-176.72 | £75,537.91 |
| 2022 | £330,000.66 | £9,999.92 | £239.43 | £-1,594.45 | £-1,261.51 | £337,384.05 |
| 2023 | £135,957.41 | £9,999.92 | £620.58 | £58.22 | £-916.89 | £145,719.23 |
| 2024 | £333,515.99 | £10,030.76 | £561.26 | £2,690.65 | £674.41 | £347,473.07 |
| 2025 | £115,818.30 | £4,449.79 | £0.00 | £634.54 | £90.43 | £120,993.06 |

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
| C8 | 2020-03-31 | renewed | 0.2600 | 0.5500 | 0.8780 | 0.1066 |
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
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.9401 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.7674 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.4100 | 0.5500 | 0.8739 | 0.6095 |
| C1_2 | 2023-12-30 | renewed | 0.1700 | 0.5500 | 0.9326 | 0.5453 |
| C7 | 2023-12-30 | renewed | 0.4100 | 0.5500 | 0.9026 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.4100 | 0.5500 | 0.9030 | 0.7019 |
| C2 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.9175 | 0.8119 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.2600 | 0.3500 | 0.8513 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.1700 | 0.5500 | 0.9480 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.1700 | 0.5500 | 0.8906 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.3800 | 0.5500 | 0.8570 | 0.9018 |
| C1_2 | 2024-12-29 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.1722 |
| C7 | 2024-12-29 | renewed | 0.2900 | 0.5500 | 0.8895 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.4100 | 0.5500 | 0.7971 | 0.3751 |
| C2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.9083 | 0.1514 |
| C8 | 2025-03-30 | renewed | 0.3200 | 0.5500 | 0.9244 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 156.3%
- **Average signed error:** +132.8% (over-estimates vs SIM)
- **Renewal events with estimates:** 58

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +114.2% | 114.2% |
| 2017 | 3 | -12.5% | 16.5% |
| 2018 | 4 | +792.1% | 792.1% |
| 2019 | 4 | +602.3% | 642.0% |
| 2020 | 10 | -3.6% | 60.1% |
| 2021 | 8 | +137.2% | 151.2% |
| 2022 | 8 | +13.5% | 22.0% |
| 2023 | 8 | +19.6% | 44.5% |
| 2024 | 8 | +47.7% | 60.1% |
| 2025 | 2 | +57.1% | 57.1% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 58
- **Active renewers:** 18 (31%) — mean company estimate 25.8%, abs error 364.8%
- **Passive SVT-rollers:** 40 (69%) — mean company estimate 10.2%, abs error 62.5%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 13.3% | 0.0% | 114.2% |
| 2017 | 0 | 3 | 0.0% | 9.4% | 0.0% | 16.5% |
| 2018 | 3 | 1 | 53.9% | 13.8% | 1037.8% | 55.1% |
| 2019 | 2 | 2 | 53.2% | 13.6% | 1267.4% | 16.7% |
| 2020 | 6 | 4 | 11.5% | 6.9% | 64.8% | 52.9% |
| 2021 | 1 | 7 | 12.7% | 12.4% | 72.6% | 162.4% |
| 2022 | 0 | 8 | 0.0% | 5.5% | 0.0% | 22.0% |
| 2023 | 2 | 6 | 25.4% | 9.9% | 72.3% | 35.2% |
| 2024 | 4 | 4 | 15.8% | 14.0% | 77.9% | 42.4% |
| 2025 | 0 | 2 | 0.0% | 13.0% | 0.0% | 57.1% |

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
| 2018 | 4 | 7.92× ⚠ | 28.41× |
| 2019 | 4 | 6.42× ⚠ | 24.89× |
| 2020 | 10 | 0.60× | 1.48× |
| 2021 | 8 | 1.51× | 5.64× |
| 2022 | 8 | 0.22× | 0.68× |
| 2023 | 8 | 0.44× | 0.92× |
| 2024 | 8 | 0.60× | 1.69× |
| 2025 | 2 | 0.57× | 0.72× |

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
| 2021 | 297,399 | 214,790 | 82,609 | 22,472 | 50,301 | 13 | 9,823 | +3.3% |
| 2022 | 589,447 | 499,055 | 90,391 | 27,046 | 54,554 | 53 | 8,738 | +1.5% |
| 2023 | 298,690 | 177,329 | 121,361 | 32,230 | 79,964 | 83 | 9,083 | +3.0% |
| 2024 | 271,566 | 146,620 | 124,946 | 37,495 | 76,702 | 45 | 10,705 | +3.9% |
| 2025 | 132,970 | 79,222 | 53,748 | 17,243 | 31,952 | 13 | 4,540 | +3.4% |
| **Total** | **1,856,121** | **1,226,228** | **629,892** | **171,109** | **393,356** | **283** | **65,146** | **+3.5%** |

Gas book net margin positive over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,441 | 9 | 274,160 | 2108.92× | OK |
| 2017 | 2,498,703 | 10 | 249,870 | 1922.08× | OK |
| 2018 | 2,488,144 | 11 | 226,195 | 1739.96× | OK |
| 2019 | 2,611,977 | 12 | 217,665 | 1674.34× | OK |
| 2020 | 2,924,252 | 14 | 208,875 | 1606.73× | OK |
| 2021 | 2,957,719 | 11 | 268,884 | 2068.34× | OK |
| 2022 | 3,161,943 | 11 | 287,449 | 2211.15× | OK |
| 2023 | 3,381,633 | 11 | 307,421 | 2364.78× | OK |
| 2024 | 3,775,214 | 11 | 343,201 | 2640.01× | OK |
| 2025 | 3,827,153 | 9 | 425,239 | 3271.07× | OK |

End-state (2025): **£425,239/account** across 9 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,441 | 81974.8× | OK |
| 2017 | 466 | 559 | 2,498,703 | 4469.8× | OK |
| 2018 | 849 | 1,019 | 2,488,144 | 2441.7× | OK |
| 2019 | 1,543 | 1,851 | 2,611,977 | 1411.0× | OK |
| 2020 | 1,979 | 2,374 | 2,924,252 | 1231.6× | OK |
| 2021 | 4,332 | 5,198 | 2,957,719 | 569.0× | OK |
| 2022 | 8,503 | 10,204 | 3,161,943 | 309.9× | OK |
| 2023 | 5,604 | 6,725 | 3,381,633 | 502.9× | OK |
| 2024 | 2,651 | 3,182 | 3,775,214 | 1186.6× | OK |
| 2025 | 3,872 | 4,647 | 3,827,153 | 823.6× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,495.78 | £12,233.03 | £261.96/MWh | £144.62/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,963.27 | £9,685.76 | £272.21/MWh | £154.30/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,933.38 | £9,310.75 | £250.25/MWh | £141.72/MWh | +10.9% |

Total HH revenue: £63,621.97 vs flat equivalent £58,719.87 (+8.3% ToU premium)

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
| 2021-12-31 | C_IC3g | £19.4 | £125.9 (+550%) | 95% |
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
| Total offer cost (foregone margin) | £150,024.51 |
| Margin saved (retained customers' terms) | £1,208,661.01 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£1,058,636.50** |
| Acquisition cost avoided (retained customers) | £2,300.00 |
| **Full economic ROI (margin + acq savings)** | **£1,060,936.50** |

Missed opportunities (churns with no offer): **5** (£5,906.90 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 5 (£5,906.90 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 2 | 2 | £71.21 | £1362.79 | £1291.58 | £0.00 |
| 2018 | 2 | 2 | £24311.34 | £165236.69 | £140925.35 | £0.00 |
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
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24227.41 | £163698.72 | £150 | £139471.31 | retained |
| 2018-12-31 | C5 | 0.37 | 3% | £83.93 | £1537.97 | £400 | £1454.04 | retained |
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

Serial savers (2): C_IC1 (4 offers, £68,287), C_IC2 (3 offers, £29,558).

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £7,807,956.41 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £678,216.89 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,066.70 |
| 2017 | £31,910.49 |
| 2018 | £101,618.96 |
| 2019 | £233,981.90 |
| 2020 | £128,481.98 |
| 2021 | £75,537.91 |
| 2022 | £337,384.05 |
| 2023 | £145,719.23 | ← trailing
| 2024 | £347,473.07 | ← trailing
| 2025 | £120,993.06 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £5,284.00 | — |
| C1_2 | — | £611.34 |
| C2 | £6,602.71 | £931.73 |
| C3 | £6,482.11 | — |
| C4 | £3,826.88 | £-1,030.75 |
| C5 | £10,894.60 | — |
| C6 | £19,662.40 | £1,956.68 |
| C7 | £9,027.20 | £563.91 |
| C8 | £9,654.80 | £735.96 |
| C9 | £10,387.96 | £1,410.85 |
| C_IC1 | £1,890,049.62 | £388,318.43 |
| C_IC2 | £997,051.40 | £204,839.78 |
| C_IC3 | £3,262,412.32 | £64,026.13 |
| C_IC4 | £1,571,978.61 | £15,852.83 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C1_2 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £6,522.54 | — | — | — | — | £14,339.54 | — | £10,526.48 | — | — | — | — | — | — |
| 2017 | £5,740.25 | — | £11,364.56 | £9,644.02 | £8,744.86 | £12,167.44 | £24,200.80 | £8,895.07 | £13,842.89 | £11,262.19 | — | — | — | — |
| 2018 | £5,707.09 | — | £8,726.07 | £9,644.06 | £7,300.23 | £12,349.05 | £20,423.34 | £8,039.06 | £10,898.00 | £10,641.05 | £2,790,943.61 | — | — | — |
| 2019 | £5,888.99 | — | £8,656.87 | £7,997.23 | £6,618.60 | £11,888.53 | £18,673.22 | £8,269.65 | £9,455.55 | £9,935.78 | £2,302,190.63 | £1,778,896.14 | — | — |
| 2020 | £4,903.36 | £15.59 | £6,579.09 | £6,764.65 | £7,131.00 | £14,191.72 | £19,225.87 | £8,256.16 | £9,465.41 | £8,517.67 | £1,351,950.59 | £876,951.47 | £2,077,701.04 | £1,475,015.42 |
| 2021 | £4,418.45 | £905.55 | £6,660.04 | £7,043.01 | £5,096.06 | £11,319.85 | £18,069.64 | £7,714.38 | £8,601.83 | £7,807.64 | £1,364,049.15 | £744,424.30 | £2,268,270.05 | £1,491,338.48 |
| 2022 | £4,166.68 | £1,801.24 | £6,414.95 | £4,743.51 | £3,259.98 | £9,045.42 | £15,428.50 | £6,083.67 | £7,993.58 | £8,694.75 | £1,197,881.25 | £638,009.68 | £2,846,137.59 | £1,131,502.63 |
| 2023 | £3,664.92 | £1,939.77 | £4,959.18 | £4,394.93 | £2,167.94 | £7,536.56 | £17,154.54 | £5,371.96 | £7,237.37 | £6,949.46 | £1,286,766.96 | £637,552.50 | £1,894,647.17 | £1,162,368.02 |
| 2024 | £3,264.20 | £2,663.27 | £4,354.82 | £4,001.55 | £2,616.39 | £7,769.52 | £15,211.87 | £4,946.25 | £7,000.45 | £7,040.91 | £1,147,593.05 | £675,702.27 | £2,007,120.95 | £957,150.73 |
| 2025 | £3,792.48 | £3,231.42 | £4,578.71 | £4,030.87 | £2,396.32 | £6,979.68 | £12,243.27 | £5,719.17 | £6,406.68 | £6,652.88 | £1,171,265.09 | £721,062.52 | £2,048,438.91 | £1,098,192.89 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £985.82, range £4.58–£4,218.12.

- C1: cost to serve £274.94, net margin after CTS £2,068.48
- C1_2: cost to serve £244.19, net margin after CTS £5,418.65
- C1g: cost to serve £5.73, net margin after CTS £1,349.51
- C2: cost to serve £505.43, net margin after CTS £5,017.15
- C2g: cost to serve £10.53, net margin after CTS £3,277.20
- C3: cost to serve £219.95, net margin after CTS £2,169.02
- C3g: cost to serve £4.58, net margin after CTS £1,293.95
- C4: cost to serve £439.89, net margin after CTS £2,802.87
- C4g: cost to serve £9.17, net margin after CTS £1,294.69
- C5: cost to serve £599.87, net margin after CTS £7,227.74
- C6: cost to serve £959.77, net margin after CTS £21,746.11
- C7: cost to serve £519.13, net margin after CTS £10,235.35
- C8: cost to serve £505.43, net margin after CTS £11,924.15
- C9: cost to serve £491.72, net margin after CTS £12,216.90
- C_IC1: cost to serve £4,218.12, net margin after CTS £1,870,543.43
- C_IC2: cost to serve £3,718.18, net margin after CTS £905,375.59
- C_IC3: cost to serve £3,218.32, net margin after CTS £1,821,875.21
- C_IC3g: cost to serve £67.07, net margin after CTS £622,579.96
- C_IC4: cost to serve £2,718.52, net margin after CTS £1,103,966.75


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 29 recovery surcharge(s) at renewal based on prior-term losses (4 gas). Avg surcharge: 14.4%.

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
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £317.57/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.69/MWh |
| C4 | electricity | 2022-09-30 | £-231.16 | £893.04 | +20.0% | £404.86/MWh | £487.66/MWh |
| C4g | gas | 2022-09-30 | £-901.21 | £1,040.11 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £337.90/MWh |
| C2 | electricity | 2023-03-31 | £-191.17 | £1,780.28 | +5.7% | £319.17/MWh | £369.81/MWh |
| C2g | gas | 2023-03-31 | £-258.53 | £1,782.04 | +9.5% | £83.68/MWh | £104.73/MWh |
| C8 | electricity | 2023-03-31 | £-481.87 | £3,898.74 | +7.4% | £319.17/MWh | £350.13/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.36/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.47/MWh |
| C4 | electricity | 2023-09-30 | £-292.88 | £1,307.19 | +17.4% | £216.77/MWh | £252.47/MWh |
| C4g | gas | 2023-09-30 | £-1,950.48 | £2,732.11 | +20.0% | £47.83/MWh | £64.52/MWh |
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
- **Estimated margin protected:** £1,208,661.01
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
| C5 | SME | MEDIUM | 27% | 9% | -20.2% [competitive] | £7,227.74 |
| C1 | resi | MEDIUM | 21% | 7% | -22.9% [competitive] | £2,068.48 |
| C_IC3 | I&C | MEDIUM | 20% | 11% | -54.0% [competitive] | £1,821,875.21 |
| C6 | SME | LOW | 15% | 25% | -25.9% [competitive] | £21,746.11 |
| C4 | resi | LOW | 14% | 14% | -9.0% | £2,802.87 |
| C7 | resi | LOW | 11% | 17% | -14.3% | £10,235.35 |
| C9 | resi | LOW | 11% | 14% | -14.3% | £12,216.90 |
| C2 | resi | LOW | 9% | 13% | -23.6% [competitive] | £5,017.15 |
| C1_2 | resi | LOW | 8% | 11% | +3.3% | £5,418.65 |
| C8 | resi | LOW | 8% | 13% | -23.6% [competitive] | £11,924.15 |
| C3 | resi | LOW | 6% | 8% | -39.0% [competitive] | £2,169.02 |
| C_IC2 | I&C | LOW | 4% | 95% | +12.4% [overpriced] | £905,375.59 |
| C_IC1 | I&C | LOW | 3% | 95% | -0.1% | £1,870,543.43 |

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
| C3 | resi | 2020-06-30 | 4.0yr | -4.3% | -39.0% | 6% | 8% | £2,169.02 |
| C1 | resi | 2020-12-30 | 5.0yr | -0.7% | -22.9% | 21% | 7% | £2,068.48 |
| C5 | SME | 2020-12-30 | 5.0yr | +2.8% | -20.2% | 27% | 9% | £7,227.74 |
| C6 | SME | 2024-03-30 | 8.0yr | -2.2% | -25.9% | 15% | 25% | £21,746.11 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 14% | 14% | £2,802.87 |

**Root Cause Summary:**
- Total churned accounts: 5
- Lifetime margin lost: £36,014.23
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
| 2018 | £1,019 | £849 | 0.23% |
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
| 2016 | 13 | £801 | £525 | £82 | 10.2% |
| 2017 | 14 | £16,735 | £8,803 | £2,279 | 13.6% |
| 2018 | 15 | £29,021 | £17,502 | £6,775 | 23.3% |
| 2019 | 17 | £70,486 | £41,296 | £13,764 | 19.5% |
| 2020 | 19 | £64,385 | £41,671 | £6,762 | 10.5% |
| 2021 | 14 | £123,922 | £54,511 | £5,396 | 4.4% << |
| 2022 | 14 | £245,590 | £74,945 | £24,099 | 9.8% |
| 2023 | 14 | £185,335 | £68,282 | £10,409 | 5.6% |
| 2024 | 14 | £156,332 | £89,843 | £24,820 | 15.9% |
| 2025 | 11 | £88,243 | £47,146 | £10,999 | 12.5% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £24,820 net/customer
**Worst year per customer:** 2016 at £82 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £417 | — | £417 |
| C1_2 | £648 | — | £648 |
| C1g | — | £669 | £669 |
| C2 | £1,177 | — | £1,177 |
| C2g | — | £1,294 | £1,294 |
| C3 | £155 | — | £155 |
| C3g | — | £336 | £336 |
| C4 | £-225 | — | £-225 * |
| C4g | — | £-1,665 | £-1,665 * |
| C5 | £15 | — | £15 |
| C6 | £2,364 | — | £2,364 |
| C7 | £-570 | — | £-570 * |
| C8 | £2,291 | — | £2,291 |
| C9 | £2,240 | — | £2,240 |
| C_IC1 | £846,527 | — | £846,527 |
| C_IC2 | £435,085 | — | £435,085 |
| C_IC3 | £136,677 | — | £136,677 |
| C_IC3g | — | £64,511 | £64,511 |
| C_IC4 | £32,221 | — | £32,221 |
| **Total** | **£1,459,022** | **£65,146** | **£1,524,167** |

Loss-making accounts: C4g (£-1,665), C7 (£-570), C4 (£-225)
Gas loss-making: C4g (£-1,665)
Gas portfolio net: £65,146 (4.3% of total)

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
| 2022 | £184,708 | £1,207,112 | £-1,022,404 |
| 2023 | £380,386 | £1,219,605 | £-839,218 |
| 2024 | £199,426 | £604,483 | £-405,057 |
| 2025 | £-21 | £200 | £-220 |
| **Total** | **£1,435,479** | **£5,658,121** | **£-4,222,642** |

Largest hedging cost: **2022** (£1,022,404 vs naked)
Smallest hedging cost: **2025** (£220 vs naked)
Conclusion: systematic forward hedging cost £4,222,642 over 10 years vs spot purchasing.

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
| 2016 | 3.25 | ALERT | £2,467,441 | £1,067 |
| 2017 | 2.69 | WATCH | £2,498,703 | £31,910 |
| 2018 | — | — | £2,488,144 | £101,619 |
| 2019 | — | — | £2,611,977 | £233,982 |
| 2020 | — | — | £2,924,252 | £128,482 |
| 2021 | — | — | £2,957,719 | £75,538 |
| 2022 | 2.70 | WATCH | £3,161,943 | £337,384 |
| 2023 | 2.72 | WATCH | £3,381,633 | £145,719 |
| 2024 | — | — | £3,775,214 | £347,473 |
| 2025 | — | — | £3,827,153 | £120,993 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,827,153)**
**Treasury growth: £2,467,441 → £3,827,153 (+£1,359,712)**

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
| C_IC3g | 2021-12 | 19.38 | 125.90 | 95.0% |

**High-risk gas reprices: 10**

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
| C_IC2 | 2022-04 | £9,407 | £95,871 | 10.2× | 3% | retained |
| C_IC1 | 2022-05 | £18,144 | £231,660 | 12.8× | 3% | retained |
| C6 | 2023-03 | £234 | £3,372 | 14.4× | 3% | retained |

**Total retention spend: £150,025** | **Total margin protected: £1,208,661**
**Portfolio retention ROI: 8.1×** | **Retained: 12/12**
**Best ROI intervention: C3 2017-07 (19.6×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £203,346 | — |
| Exit Gas (with churn risk) | £83,225 | -£120,121 |
| Reprice to Breakeven | £205,011 | +£1,665 |

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
| 2022 | 86.3% | 0.0% | 97.4% | 1 | 13 |
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
| 2016 | 13 | 12 | 0.9 | £9 |
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
| 2016 | 2016-12-31 | 48 | C5 | -£188 |
| 2017 | 2017-12-31 | 48 | C1 | -£55 |
| 2018 | 2018-12-31 | 48 | C4 | -£218 |
| 2019 | 2019-12-31 | 48 | C3 | -£104 |
| 2020 | 2020-03-16 | 20 | C_IC1 | -£19 |
| 2021 | 2021-12-31 | 48 | C6 | -£230 |
| 2022 | 2022-12-31 | 48 | C6 | -£660 |
| 2023 | 2023-12-31 | 48 | C6 | -£759 |
| 2024 | 2024-09-28 | 48 | C4 | -£204 |
| 2025 | 2025-01-08 | 31 | C_IC1 | -£81 |

**Single worst period: 2023 2023-12-31 SP48 (C6, -£759)** — exposure from gas supply anchor at year-end pricing.

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
| 2016 | 14 | £173,359 | £92,832 | £9,147 | £12,383 |
| 2017 | 1 | £3,123,699 | £1,874,762 | £846,527 | £3,123,699 |
| 2018 | 1 | £1,524,534 | £909,094 | £435,085 | £1,524,534 |
| 2019 | 2 | £6,462,540 | £2,447,741 | £201,188 | £3,231,270 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £32,221 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,231,270/customer)**
**Best net margin cohort: 2017 (£846,527)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £287 | — | 108 |
| 2017 | +£2,707 | £37,159 | £33 | — | 168 |
| 2018 | +£9,875 | £65,510 | £468 | — | 180 |
| 2019 | +£28,353 | £164,625 | £99 | — | 204 |
| 2020 | +£35,391 | £238,634 | £-0 | — | 205 |
| 2021 | +£14,982 | £246,246 | £296 | — | 168 |
| 2022 | -£49,726 CREDIT | £256,149 | £1,033 | 2 | 168 |
| 2023 | +£64,738 | £271,739 | £910 | 47 | 168 |
| 2024 | +£109,869 | £307,451 | £225 | 4271 | 153 |
| 2025 | +£46,911 | £135,614 | £0 | — | 66 |

**CfD turned CREDIT in 2022: -£49,726 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2022 (£1,033)**

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
| 2022 | £4,445 | -£726 | £3,824 | £950,568 | £91,118 | £1,049,228 |
| 2023 | £6,665 | -£155 | £4,592 | £823,331 | £121,515 | £955,949 |
| 2024 | £9,428 | £1,295 | £1,558 | £1,121,870 | £123,652 | £1,257,802 |
| 2025 | £3,980 | £240 | £0 | £460,883 | £53,509 | £518,611 |

**Best gross margin year: 2024 (£1,257,802)** | **Worst: 2016 (£6,822)**
**Loss-making: resi gas in 2022 (£-726)**
**Loss-making: resi gas in 2023 (£-155)**


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
| 2017 | £2,498,703 | AMBER | RED | GREEN | AMBER | RED |
| 2018 | £2,488,144 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,611,977 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,924,252 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,957,719 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,161,943 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,381,633 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,775,214 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,827,153 | AMBER | AMBER | GREEN | AMBER | RED |

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
| 2022 | 14 | 22.1% | £302,929 | £75,046 | 2.27% |
| 2023 | 14 | 24.7% | £248,088 | £68,370 | 2.51% |
| 2024 | 14 | 39.1% | £214,259 | £89,877 | 2.44% |
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
| 2016 | 4.70% | 6% | OK | 30.8% | 8% | ! |
| 2017 | 4.68% | 6% | OK | 28.6% | 8% | ! |
| 2018 | 4.67% | 6% | OK | 13.3% | 8% | ~ |
| 2019 | 4.69% | 6% | OK | 17.6% | 8% | ! |
| 2020 | 4.29% | 6% | OK | 5.3% | 8% | OK |
| 2021 | 4.82% | 8% | OK | 14.3% | 12% | ~ |
| 2022 | 5.63% | 8% | OK | 50.0% | 12% | ! |
| 2023 | 4.85% | 8% | OK | 21.4% | 12% | ! |
| 2024 | 4.64% | 6% | OK | 57.1% | 8% | ! |
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

**Total bad debt (all years):** £3,352
**Crisis stress incremental:** £5,027

**RAG [OK]:** GREEN — Incremental credit stress below 0.5% revenue — not material

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (11 active customers) under 12-month forward scenarios.
Generated: 2026-07-09T23:21:24Z

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
| 2021 | 13 | +13.1 | 13 | 0 | 6 |
| 2022 | 13 | +18.8 | 12 | 1 | 5 |
| 2023 | 13 | +8.7 | 9 | 4 | 10 |
| 2024 | 12 | +4.8 | 5 | 7 | 2 |
| 2025 | 3 | +4.1 | 2 | 1 | 0 |

**Total adjustments 2016-2025: 117** | **Peak avg adjustment: 2022 (+18.8 £/MWh)**
**Emergency reprices: 29 total** (10 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £31,389 | £10,463 | — |
| 2017 | 9 | £105,862 | £11,762 | +£74,474 |
| 2018 | 10 | £2,884,672 | £288,467 | +£2,778,809 |
| 2019 | 11 | £4,168,471 | £378,952 | +£1,283,800 |
| 2020 | 14 | £5,866,669 | £419,048 | +£1,698,198 |
| 2021 | 14 | £5,945,718 | £424,694 | +£79,049 |
| 2022 | 14 | £5,881,163 | £420,083 | £-64,555 |
| 2023 | 14 | £5,042,711 | £360,194 | £-838,452 |
| 2024 | 14 | £4,846,436 | £346,174 | £-196,275 |
| 2025 | 14 | £5,094,991 | £363,928 | +£248,555 |

**Peak portfolio CLV: 2021 (£5,945,718)** | **Earliest/lowest: 2016 (£31,389)**
**Largest YoY gain: 2018 (+£2,778,809)**
**Largest YoY fall: 2023 (£-838,452)**

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
| 2022 | £4,241,008.90 | £2,389,082.80 | £801,288.51 | £1,050,637.60 | 24.8% | +£1,825,087.19 | +£1,417,170.81 | +£121,738.18 | +£286,178.20 |
| 2023 | £3,473,228.65 | £1,638,983.76 | £877,068.66 | £957,176.24 | 27.6% | £-767,780.25 | £-750,099.04 | +£75,780.15 | £-93,461.36 |
| 2024 | £2,999,627.66 | £931,630.07 | £809,714.61 | £1,258,282.98 | 41.9% | £-473,600.99 | £-707,353.69 | £-67,354.04 | +£301,106.74 |
| 2025 | £1,228,035.22 | £452,060.81 | £256,896.84 | £519,077.57 | 42.3% | £-1,771,592.44 | £-479,569.26 | £-552,817.78 | £-739,205.40 |

**Best GM year: 2016 (51.3%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Net Margin Bridge (Year-on-Year Attribution)

Decomposes each year's net margin change into: gross margin movement, bad debt, capital costs, policy levies, network costs.

| Transition | Net Δ | Gross Δ | Bad Debt Δ | Capital Δ | Policy Δ | Network Δ | Portfolio | Driver | RAG |
|-----------|-------|---------|-----------|---------|---------|---------|---------|--------|-----|
| 2016→2017 | +£30,844 | +£116,417 | +£254 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£69,708 | +£139,289 | -£435 | -£255 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£132,363 | +£439,500 | +£370 | -£781 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£105,500 | +£89,727 | +£99 | +£346 | -£162,654 | -£33,019 | +2 | policy levies | RED |
| 2020→2021 | -£52,944 | -£28,607 | -£296 | -£3,641 | -£19,033 | -£1,367 | -5 | gross margin | RED |
| 2021→2022 | +£261,846 | +£286,079 | -£737 | -£7,678 | -£1,057 | -£14,761 | +0 | gross margin | GREEN |
| 2022→2023 | -£191,665 | -£93,279 | +£123 | +£3,237 | -£70,553 | -£31,194 | +0 | gross margin | RED |
| 2023→2024 | +£201,754 | +£301,853 | +£685 | +£523 | -£100,652 | -£654 | +0 | gross margin | GREEN |
| 2024→2025 | -£226,480 | -£739,191 | +£225 | +£3,875 | +£381,910 | +£126,700 | -3 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£226,480)** | **Best transition: 2021→2022 (+£261,846)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Payment Portfolio Health (P2: Billing Infra)

Year-by-year bad debt rate and high-churn-risk customer concentration.

| Year | Bad Debt | Bad Debt Rate | At-Risk Customers | At-Risk % | Trend | RAG |
|------|----------|--------------|-----------------|----------|-------|-----|
| 2016 | £287 | 2.75% | 0/4 | 0% | — STABLE | RED |
| 2017 | £33 | 0.01% | 0/10 | 0% | ↓ IMPROVING | GREEN |
| 2018 | £468 | 0.11% | 1/11 | 9% | ↑ DETERIORATING | GREEN |
| 2019 | £99 | 0.01% | 3/12 | 25% | ↓ IMPROVING | GREEN |
| 2020 | £-0 | -0.00% | 5/14 | 36% | ↓ IMPROVING | AMBER |
| 2021 | £296 | 0.02% | 4/11 | 36% | ↑ DETERIORATING | AMBER |
| 2022 | £1,033 | 0.03% | 9/11 | 82% | ↑ DETERIORATING | RED |
| 2023 | £910 | 0.04% | 10/11 | 91% | — STABLE | RED |
| 2024 | £225 | 0.01% | 4/11 | 36% | ↓ IMPROVING | AMBER |
| 2025 | £0 | 0.00% | 2/3 | 67% | ↓ IMPROVING | RED |

**Worst bad debt year: 2016 (2.75%)** | **Peak at-risk concentration: 2023 (91% of customers)**

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
| 2017 | £2,587,826.91 | £29,052.61 | 89.1x | ✓ GREEN | Yes |
| 2018 | £2,834,813.84 | £50,079.03 | 56.6x | ✓ GREEN | Yes |
| 2019 | £3,498,591.59 | £137,120.98 | 25.5x | ✓ GREEN | Yes |
| 2020 | £4,242,861.23 | £154,751.93 | 27.4x | ✓ GREEN | Yes |
| 2021 | £4,944,920.57 | £201,326.81 | 24.6x | ✓ GREEN | Yes |
| 2022 | £5,883,135.02 | £353,417.41 | 16.6x | ✓ GREEN | Yes |
| 2023 | £6,739,982.46 | £289,435.72 | 23.3x | ✓ GREEN | Yes |
| 2024 | £7,912,169.28 | £249,968.97 | 31.6x | ✓ GREEN | Yes |
| 2025 | £8,382,562.24 | £102,336.27 | 81.9x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.6x (equity £5,883,135.02 vs monthly revenue £353,417.41). RAG: GREEN.
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
| 2022 | £4,241,008.90 | £1,576,241.64 | £13,398.05 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,473,228.65 | £1,290,883.32 | £10,972.51 | ✓ GREEN |  |
| 2024 | £2,999,627.66 | £1,114,861.61 | £9,476.32 | ✓ GREEN |  |
| 2025 | £1,228,035.22 | £456,419.76 | £3,879.57 | ✓ GREEN |  |

**Peak reconciliation exposure:** 2022 — max adverse £13,398 (4.5 months weighted tail).

_Note: Outstanding pool ≈ current-year revenue × (weighted outstanding months ÷ 12)._
_Max adverse = pool × blended variance rate (0.5% HH + 4% non-HH, portfolio-weighted)._
## Ofgem Supply Licence Health (Phase OC)

Annual licence health checks: customer base, net assets, liquidity, bad debt.
Breach triggers board escalation and Ofgem notification under SLC 0.
WATCH = within 20% of threshold. BREACH = threshold crossed.

| Year | Customers | Net Assets | Treasury | Cash Wks | Bad Debt % | Overall |
|------|-----------|------------|----------|----------|------------|---------|
| 2016 | 13 | £2,473,113.55 | £2,467,441.30 | 35691w | 2.75% | ✗ BREACH |
| 2017 | 14 | £2,587,826.91 | £2,498,703.09 | 1170w | 0.01% | ✗ BREACH |
| 2018 | 15 | £2,834,813.84 | £2,488,143.55 | 749w | 0.11% | ✗ BREACH |
| 2019 | 17 | £3,498,591.59 | £2,611,977.12 | 274w | 0.01% | ✗ BREACH |
| 2020 | 19 | £4,242,861.23 | £2,924,252.25 | 352w | -0.00% | ✗ BREACH |
| 2021 | 14 | £4,944,920.57 | £2,957,719.11 | 158w | 0.02% | ✗ BREACH |
| 2022 | 14 | £5,883,135.02 | £3,161,942.85 | 69w | 0.03% | ✗ BREACH |
| 2023 | 14 | £6,739,982.46 | £3,381,632.54 | 107w | 0.04% | ✗ BREACH |
| 2024 | 14 | £7,912,169.28 | £3,775,213.53 | 211w | 0.01% | ✗ BREACH |
| 2025 | 11 | £8,382,562.24 | £3,827,153.05 | 440w | 0.00% | ✗ BREACH |

**BREACH years:** 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 — board escalation required.

_Note: Complaints from contact model avg_complaint_probability. Customer count <50 triggers Ofgem viability review — small-portfolio years will show WATCH._
## Ofgem SLC Compliance Scorecard (Phase OD)

10 compliance domains per year, derived from simulation outputs.
G = GREEN (compliant), A = AMBER (watch), R = RED (breach).

| Domain | SLC Ref | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|--------|---------|------|------|------|------|------|------|------|------|------|------|
| Governance | SLC 0-9 | G | G | G | G | G | G | G | G | G | G |
| Billing/Metering | SLC 10-14 | G | G | G | G | G | G | A | G | G | A |
| Payment/Debt | SLC 15-19 | A | G | G | G | G | G | G | G | G | G |
| Information | SLC 20-24 | G | G | G | G | G | G | G | G | G | G |
| Complaints | SLC 25-29 / Ofgem Time to Fix rules | A | A | A | A | A | A | R | A | A | R |
| Vulnerable Cust | SLC 30-35 / PSR | G | G | G | G | G | G | G | G | G | G |
| Tariff/Cap | SLC 36-40 / Default Tariff Cap | G | G | G | G | G | G | G | G | G | G |
| Environmental | SLC 41-50 / RO, CfD, EE obligation | G | G | G | G | G | G | G | G | G | G |
| Network/BSC | SLC 51-60 / BSC obligations | G | G | G | G | G | G | G | G | G | G |
| Financial Res. | SLC 4C / SFR Decision 2023 | G | G | G | G | G | G | G | G | G | G |
| **Overall** |  | A | A | A | A | A | A | R | A | A | R |

**Breach years (RED):** 2022, 2025
**Watch years (AMBER):** 2016, 2017, 2018, 2019, 2020, 2021, 2023, 2024

_Note: Vulnerable customers, tariff/cap, and environmental domains defaulted to GREEN_
_(these are modelled as compliant; detailed SLC breach simulation not yet implemented)._
## Ofgem Annual Supply Return (Phase OE)

UK suppliers must file annual supply returns to Ofgem. Filed by 31 March of the following year.

| Year | Submitted | Customers (R/SME/I&C) | Elec GWh | Gas GWh | Bad Debt/Cust |
|------|-----------|----------------------|----------|---------|---------------|
| 2016 | Yes | 13/13/13 | 0.1 | 0.0 | £22 |
| 2017 | Yes | 14/14/14 | 1.5 | 0.1 | £2 |
| 2018 | Yes | 15/15/15 | 2.9 | 0.1 | £31 |
| 2019 | Yes | 17/17/17 | 7.1 | 2.8 | £6 |
| 2020 | Yes | 19/19/19 | 7.3 | 2.4 | £-0 |
| 2021 | Yes | 14/14/14 | 9.6 | 6.0 | £21 |
| 2022 | Yes | 14/14/14 | 19.0 | 11.8 | £74 |
| 2023 | Yes | 14/14/14 | 15.3 | 6.0 | £65 |
| 2024 | Yes | 14/14/14 | 12.8 | 5.4 | £16 |
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
- C1: 21 sessions
- C7: 16 sessions
- C5: 12 sessions
- C6: 12 sessions
- C8: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £10,387.96 | Median churn: 32% | Total portfolio CLV: £7,803,314.63

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC1 | £1,890,049.62 | 29% | 17.3 periods |
| C_IC4 | £1,571,978.61 | 20% | 13.1 periods |
| C6 | £19,662.40 | 26% | 13.5 periods |
| C9 | £10,387.96 | 26% | 15.2 periods |

Quadrant CLV: £3,492,078.60 (45% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £3,262,412.32 | 41% | 16.9 periods |
| C_IC2 | £997,051.40 | 32% | 15.5 periods |
| C5 | £10,894.60 | 32% | 14.7 periods |

Quadrant CLV: £4,270,358.32 (55% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C7 | £9,027.20 | 29% | 16.6 periods |
| C3 | £6,482.11 | 11% | 14.5 periods |

Quadrant CLV: £15,509.32 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £9,654.80 | 32% | 13.7 periods |
| C2 | £6,602.71 | 38% | 13.2 periods |
| C1 | £5,284.00 | 35% | 15.6 periods |
| C4 | £3,826.88 | 38% | 14.4 periods |

Quadrant CLV: £25,368.39 (0% of portfolio)

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
| 2016 | £742.41 | £324.29 | £9,028.87 | £1,388.28 | 13.3% | YES |
| 2017 | £31,393.95 | £516.54 | £231,633.78 | £2,660.42 | 1.1% | YES |
| 2018 | £101,182.02 | £436.94 | £432,204.11 | £3,113.94 | 0.7% | YES |
| 2019 | £223,492.25 | £10,489.65 | £1,060,498.05 | £137,766.14 | 11.5% | YES |
| 2020 | £117,993.86 | £10,488.12 | £1,102,193.09 | £121,119.88 | 9.9% | YES |
| 2021 | £65,714.71 | £9,823.20 | £1,437,504.91 | £297,399.17 | 17.1% | YES |
| 2022 | £328,645.64 | £8,738.41 | £2,848,806.28 | £589,446.82 | 17.1% | YES |
| 2023 | £136,636.20 | £9,083.03 | £2,296,002.86 | £298,689.84 | 11.5% | YES |
| 2024 | £336,767.90 | £10,705.17 | £1,917,076.86 | £271,566.09 | 12.4% | YES |
| 2025 | £116,452.84 | £4,540.22 | £837,702.08 | £132,970.20 | 13.7% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £203,346.17 | — | Current strategy |
| EXIT_GAS | £83,225.05 | £-120,121.12 | Remove gas; model elec churn risk |
| REPRICE_GAS | £205,011.42 | £1,665.25 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-1,665.25 | -11.50x | +16.1% |

**Accretive gas accounts:** C1g (£669.14), C2g (£1,294.23), C3g (£336.46), C_IC3g (£64,510.98) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £65146 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,715,634.13 | £50,040.45 | £1,450,509.83 | 29.0x | Strong |
| I&C gas | £622,647.03 | £0.00 | £64,510.98 | 0.0x | Low return |
| SME electricity | £30,533.50 | £323.92 | £2,378.97 | 7.3x | Moderate |
| resi electricity | £55,053.26 | £611.90 | £6,133.00 | 10.0x | Moderate |
| resi gas | £7,245.35 | £282.61 | £634.58 | 2.2x | Low return |

## Portfolio Concentration Risk

Revenue concentration analysis across 19 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2248** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,324,340.94 (98.6% of total positive margin)
- resi: £59,067.91 (0.9% of total positive margin)
- SME: £28,973.86 (0.5% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,870,543.43 | 29.2% | 3% | £60,418.55 |
| C_IC3 | I&C | £1,821,875.21 | 28.4% | 20% | £369,658.48 |
| C_IC4 | I&C | £1,103,966.75 | 17.2% | 0% | £0.00 |
| C_IC2 | I&C | £905,375.59 | 14.1% | 4% | £33,227.28 |
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
| C2g | gas | 2022-03-31 | -19.2% | +13.6% | £99.49/MWh | £113.02/MWh |
| C6 | electricity | 2022-03-31 | -19.7% | +13.9% | £361.95/MWh | £412.09/MWh |
| C8 | electricity | 2022-03-31 | 2.5% | +2.8% | £361.95/MWh | £371.90/MWh |
| C_IC2 | electricity | 2022-04-30 | -10.1% | +9.0% | £269.81/MWh | £294.18/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.9% | +7.4% | £239.42/MWh | £257.24/MWh |
| C9 | electricity | 2022-06-30 | 4.4% | +1.8% | £255.09/MWh | £259.72/MWh |
| C4 | electricity | 2022-09-30 | 7.2% | +0.4% | £404.86/MWh | £406.38/MWh |
| C4g | gas | 2022-09-30 | -23.5% | +15.0% | £183.79/MWh | £211.36/MWh |
| C1_2 | electricity | 2022-12-30 | 8.6% | -0.3% | £266.73/MWh | £265.96/MWh |
| C7 | electricity | 2022-12-30 | -3.1% | +5.6% | £266.73/MWh | £281.58/MWh |
| C_IC3 | electricity | 2022-12-31 | -14.1% | +11.1% | £168.36/MWh | £186.96/MWh |
| C_IC3g | gas | 2022-12-31 | -43.0% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2 | electricity | 2023-03-31 | -11.2% | +9.6% | £319.17/MWh | £349.74/MWh |
| C2g | gas | 2023-03-31 | -20.6% | +14.3% | £83.68/MWh | £95.64/MWh |
| C6 | electricity | 2023-03-31 | -3.9% | +5.9% | £319.17/MWh | £338.13/MWh |
| C8 | electricity | 2023-03-31 | 3.6% | +2.2% | £319.17/MWh | £326.13/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.8% | +14.9% | £171.46/MWh | £196.97/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.2% | +12.6% | £163.19/MWh | £183.73/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.11/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.04/MWh |
| C4g | gas | 2023-09-30 | -16.9% | +12.4% | £47.83/MWh | £53.77/MWh |
| C1_2 | electricity | 2023-12-30 | 29.1% | -5.0% | £242.22/MWh | £230.11/MWh |
| C7 | electricity | 2023-12-30 | 26.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 22.3% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -6.6% | +7.3% | £51.89/MWh | £55.69/MWh |
| C2 | electricity | 2024-03-30 | 14.6% | -3.3% | £207.71/MWh | £200.84/MWh |
| C2g | gas | 2024-03-30 | 12.0% | -2.0% | £49.31/MWh | £48.32/MWh |
| C6 | electricity | 2024-03-30 | 12.4% | -2.2% | £207.71/MWh | £203.14/MWh |
| C8 | electricity | 2024-03-30 | 12.4% | -2.2% | £207.71/MWh | £203.14/MWh |
| C_IC2 | electricity | 2024-06-28 | -31.4% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.8% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C1_2 | electricity | 2024-12-29 | 0.4% | +3.8% | £243.79/MWh | £253.01/MWh |
| C7 | electricity | 2024-12-29 | 22.6% | -5.0% | £243.79/MWh | £231.60/MWh |
| C_IC3 | electricity | 2024-12-30 | 14.4% | -3.2% | £116.37/MWh | £112.67/MWh |
| C_IC3g | gas | 2024-12-30 | 16.9% | -4.5% | £50.47/MWh | £48.22/MWh |
| C2 | electricity | 2025-03-30 | 4.8% | +1.6% | £284.89/MWh | £289.53/MWh |
| C2g | gas | 2025-03-30 | 13.7% | -2.9% | £71.57/MWh | £69.52/MWh |
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
| C_IC3+C_IC3g | £136,677.17 | £64,510.98 | £201,188.16 | Yes |
| C2+C2g | £1,176.97 | £1,294.23 | £2,471.20 | Yes |
| C1+C1g | £416.71 | £669.14 | £1,085.85 | Yes |
| C3+C3g | £155.15 | £336.46 | £491.62 | Yes |
| C4+C4g | £-225.40 | £-1,665.25 | £-1,890.65 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £65,145.56.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,524,167.36 across 19 billing accounts. Revenue: £14,028,771.67.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,123,699.44 | £1,874,761.55 | £18,414.87 | £846,527.08 | 27.1% |
| 2 | C_IC2 | fixed | £1,524,534.49 | £909,093.77 | £8,522.92 | £435,084.93 | 28.5% |
| 3 | C_IC3 | pass_through | £4,629,960.34 | £1,825,093.53 | £23,102.67 | £136,677.17 | 3.0% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £64,510.98 | 3.5% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £32,220.65 | 1.2% |
| 6 | C6 | fixed | £39,189.97 | £22,705.89 | £266.15 | £2,363.93 | 6.0% |
| 7 | C8 | fixed | £21,649.03 | £12,429.58 | £134.60 | £2,291.31 | 10.6% |
| 8 | C9 | fixed | £20,244.14 | £12,708.62 | £131.44 | £2,240.37 | 11.1% |
| 9 | C2g | fixed | £8,090.96 | £3,287.73 | £106.78 | £1,294.23 | 16.0% |
| 10 | C2 | fixed | £9,515.53 | £5,522.58 | £58.28 | £1,176.97 | 12.4% |
| 11 | C1g | fixed | £2,436.42 | £1,355.24 | £15.79 | £669.14 | 27.5% |
| 12 | C1_2 | fixed | £11,629.63 | £5,662.84 | £81.65 | £648.00 | 5.6% |
| 13 | C1 | fixed | £3,545.70 | £2,343.42 | £14.11 | £416.71 | 11.8% |
| 14 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £336.46 | 12.5% |
| 15 | C3 | fixed | £3,628.86 | £2,388.97 | £14.77 | £155.15 | 4.3% |
| 16 | C5 | fixed | £12,492.19 | £7,827.61 | £57.77 | £15.04 | 0.1% |
| 17 | C4 | fixed | £6,193.88 | £3,242.76 | £37.58 | £-225.40 | -3.6% |
| 18 | C7 | fixed | £21,728.81 | £10,754.49 | £139.46 | £-570.11 | -2.6% |
| 19 | C4g | fixed | £10,330.18 | £1,303.85 | £144.75 | £-1,665.25 | -16.1% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,028,772 | 100.0% |
| Wholesale cost | -£7,597,658 | 54.2% |
| **Gross supply margin** | **£6,431,113** | **45.8%** |
| Policy + Network costs | -£4,855,687 | 34.6% |
| Capital cost | -£51,259 | 0.4% |
| **Net supply margin** | **£1,524,167** | **10.9%** |

> *The ledger's `net_margin_gbp` (£6,393,960) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,022,833 | 47.5% | 12.1% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 3.5% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £51,682 | 59.1% | 4.6% | CMA 3-8% | ✓ |
| resi/elec | £86,506 | 57.1% | 6.3% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £23,541 | 30.8% | 2.7% | Ofgem CMA 2-4% | ✓ |

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
| Customer bills (all-in) | £22,565,070.06 |
|   Less: VAT remitted to HMRC | (£3,739,831.76) |
| = Revenue (ex-VAT) | £18,825,238.30 |
| Less: non-commodity pass-through | (£4,782,360.86) |
| Wholesale cost (settlement events) | (£7,597,658.41) |
| Gross margin | £6,445,219.04 |
| Capital charges | (£51,258.88) |
| Net margin | £6,393,960.15 |

_Cash reconciliation: of £22,565,070.06 billed, bad debt of £451,425.09 was written off, leaving £22,113,644.97 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £9,682,366.82._

| Acquisition spend | (£862.50) |
| Fixed overhead | (£5,700.00) |
| Cost to serve | (£18,730.56) |
| Operating net margin | £6,368,667.10 |

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
| 2022 | £4,241,008.90 | £2,389,082.80 | £801,288.51 | £1,050,637.60 | £96,079.23 | £99,141.10 | £938,214.46 (22.1%) |
| 2023 | £3,473,228.65 | £1,638,983.76 | £877,068.66 | £957,176.24 | £87,222.64 | £90,284.23 | £856,847.44 (24.7%) |
| 2024 | £2,999,627.66 | £931,630.07 | £809,714.61 | £1,258,282.98 | £73,197.97 | £76,574.13 | £1,172,186.81 (39.1%) |
| 2025 | £1,228,035.22 | £452,060.81 | £256,896.84 | £519,077.57 | £41,748.18 | £43,037.72 | £470,392.96 (38.3%) |
| **Total** | **£18,825,238.30** | | | | | | **£5,915,926.02 (31.4%)** |

**Best year:** 2024 — net £1,172,186.81 (39.1% margin)
**Worst year:** 2016 — net £6,477.33 (42.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,382,562.24 |
| Trade Receivables | £-0.00 |
| **Total Assets** | **£8,382,562.24** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,915,926.02 |

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
| 2022 | £2,607,611.88 | £4,241,008.90 | +62.6% | £790,935.58 | £938,214.46 | +18.6% | RED |
| 2023 | £4,508,414.67 | £3,473,228.65 | -23.0% | £1,029,561.00 | £856,847.44 | -16.8% | RED |
| 2024 | £3,512,844.39 | £2,999,627.66 | -14.6% | £893,105.75 | £1,172,186.81 | +31.2% | RED |
| 2025 | £3,145,356.42 | £1,228,035.22 | -61.0% | £1,315,150.33 | £470,392.96 | -64.2% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,387,397.65

## 2016

**Trading & Risk**

- Net margin: £1,066.70 (gross £6,822.19, capital £86.34)
  - Electricity: gross £6,011.45, capital £78.97, net £742.41
  - Gas: gross £810.73, capital £7.36, net £324.29
- Treasury at year end: £2,467,441.30
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.22, (none), VaR (current £27.73 / stressed £8.52) ratio 3.25
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
- Worst single period: C5 on 2016-12-31 period 48, net margin £-188.18

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
- C5 (electricity): tariff £117.30-£131.01/MWh, net margin £60.59
- C6 (electricity): tariff £107.62/MWh, net margin £24.49
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £267.20
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £139.89
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £48.41

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.829, average bill shock 19.7%, bad debt provision £286.69, avg complaint probability 4.7%
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

**Year narrative:** 2016 produced a net gain of £1,066.70 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 31 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £31,910.49 (gross £123,238.69, capital £1,273.22)
  - Electricity: gross £121,809.12, capital £1,258.37, net £31,393.95
  - Gas: gross £1,429.57, capital £14.85, net £516.54
- Treasury at year end: £2,498,703.09
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
- Worst single period: C1 on 2017-12-31 period 48, net margin £-54.72

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £11,762.45
  - By billing account: C1 £5,740.25, C2 £11,364.56, C3 £9,644.02, C4 £8,744.86, C5 £12,167.44, C6 £24,200.80, C7 £8,895.07, C8 £13,842.89, C9 £11,262.19
- Bill shock events (>=20%): 50 -- C1g 2017-01-31 (31%); C1g 2017-02-28 (28%); C1g 2017-05-31 (30%); C1g 2017-06-30 (30%); C1g 2017-09-30 (21%); C1g 2017-11-30 (70%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-05-31 (34%); C2g 2017-06-30 (29%); C2g 2017-09-30 (27%); C2g 2017-11-30 (66%); C2g 2017-12-31 (22%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-05-31 (30%); C3g 2017-06-30 (23%); C3g 2017-09-30 (21%); C3g 2017-11-30 (59%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (30%); C4 2017-09-30 (23%); C4 2017-10-31 (27%); C4 2017-11-30 (29%); C4g 2017-01-31 (23%); C4g 2017-02-28 (22%); C4g 2017-05-31 (33%); C4g 2017-06-30 (35%); C4g 2017-09-30 (36%); C4g 2017-10-31 (22%); C4g 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £92.60-£198.06/MWh, net margin £74.94
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £115.22
- C2 (electricity): tariff £84.56-£188.36/MWh, net margin £110.01
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £194.46
- C3 (electricity): tariff £98.21-£120.79/MWh, net margin £88.24
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £69.89
- C4 (electricity): tariff £77.34-£164.79/MWh, net margin £49.52
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £136.97
- C5 (electricity): tariff £119.52-£131.01/MWh, net margin £225.85
- C6 (electricity): tariff £107.62-£126.91/MWh, net margin £98.49
- C7 (electricity): tariff £96.39-£195.85/MWh, net margin £194.47
- C8 (electricity): tariff £84.56-£191.05/MWh, net margin £246.35
- C9 (electricity): tariff £77.16-£181.43/MWh, net margin £166.16
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £30,139.92

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.818, average bill shock 16.6%, bad debt provision £33.19, avg complaint probability 4.7%
- Solvency signal: £249,870/customer (10 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2017 produced a net gain of £31,910.49 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 50 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £101,618.96 (gross £262,528.02, capital £1,528.05)
  - Electricity: gross £261,165.22, capital £1,506.99, net £101,182.02
  - Gas: gross £1,362.80, capital £21.07, net £436.94
- Treasury at year end: £2,488,143.55
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.92 (avg 0.92), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C4 on 2018-12-31 period 48, net margin £-218.46

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £288,467.16
  - By billing account: C1 £5,707.09, C2 £8,726.07, C3 £9,644.06, C4 £7,300.23, C5 £12,349.05, C6 £20,423.34, C7 £8,039.06, C8 £10,898.00, C9 £10,641.05, C_IC1 £2,790,943.61
- Bill shock events (>=20%): 60 -- C1g 2018-04-30 (37%); C1g 2018-05-31 (29%); C1g 2018-06-30 (30%); C1g 2018-09-30 (25%); C1g 2018-10-31 (46%); C1g 2018-11-30 (27%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (28%); C2g 2018-05-31 (34%); C2g 2018-06-30 (34%); C2g 2018-09-30 (33%); C2g 2018-10-31 (45%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (28%); C3g 2018-05-31 (32%); C3g 2018-06-30 (29%); C3g 2018-08-31 (34%); C3g 2018-09-30 (34%); C3g 2018-10-31 (35%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (29%); C4 2018-09-30 (24%); C4 2018-10-31 (44%); C4 2018-11-30 (30%); C4g 2018-04-30 (36%); C4g 2018-05-31 (33%); C4g 2018-06-30 (36%); C4g 2018-09-30 (39%); C4g 2018-10-31 (85%); C4g 2018-11-30 (24%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C2 23%, C3 23%, C6 23%, C7 20%, C8 23%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £92.60-£224.87/MWh, net margin £37.49
- C1g (gas): tariff £33.49-£36.05/MWh, net margin £142.44
- C2 (electricity): tariff £98.66-£215.83/MWh, net margin £93.16
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £189.04
- C3 (electricity): tariff £120.79-£126.90/MWh, net margin £90.31
- C3g (gas): tariff £23.11-£28.80/MWh, net margin £40.74
- C4 (electricity): tariff £86.32-£224.05/MWh, net margin £-163.97 -- **net-negative**
- C4g (gas): tariff £26.10-£33.61/MWh, net margin £64.72
- C5 (electricity): tariff £119.52-£153.36/MWh, net margin £-417.98 -- **net-negative**
- C6 (electricity): tariff £126.91-£142.18/MWh, net margin £-7.12 -- **net-negative**
- C7 (electricity): tariff £96.39-£221.26/MWh, net margin £-13.33 -- **net-negative**
- C8 (electricity): tariff £100.07-£200.69/MWh, net margin £164.36
- C9 (electricity): tariff £95.03-£198.38/MWh, net margin £242.71
- C_IC1 (electricity): tariff £-82.12-£228.46/MWh, net margin £107,347.52
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,191.11 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.809, average bill shock 16.0%, bad debt provision £468.48, avg complaint probability 4.7%
- Solvency signal: £226,195/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2018 produced a net gain of £101,618.96 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 60 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £233,981.90 (gross £702,028.50, capital £2,309.31)
  - Electricity: gross £625,974.66, capital £2,287.85, net £223,492.25
  - Gas: gross £76,053.84, capital £21.46, net £10,489.65
- Treasury at year end: £2,611,977.12
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C3 on 2019-12-31 period 48, net margin £-104.28

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £378,951.93
  - By billing account: C1 £5,888.99, C2 £8,656.87, C3 £7,997.23, C4 £6,618.60, C5 £11,888.53, C6 £18,673.22, C7 £8,269.65, C8 £9,455.55, C9 £9,935.78, C_IC1 £2,302,190.63, C_IC2 £1,778,896.14
- Bill shock events (>=20%): 66 -- C1 2019-04-30 (21%); C1g 2019-01-31 (36%); C1g 2019-02-28 (26%); C1g 2019-05-31 (23%); C1g 2019-06-30 (35%); C1g 2019-10-31 (74%); C1g 2019-11-30 (43%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-01-31 (25%); C2g 2019-02-28 (26%); C2g 2019-04-30 (35%); C2g 2019-06-30 (32%); C2g 2019-07-31 (25%); C2g 2019-09-30 (30%); C2g 2019-10-31 (64%); C2g 2019-11-30 (28%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-02-28 (26%); C3g 2019-06-30 (33%); C3g 2019-07-31 (35%); C3g 2019-09-30 (35%); C3g 2019-10-31 (64%); C3g 2019-11-30 (31%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (32%); C4 2019-09-30 (27%); C4 2019-11-30 (27%); C4g 2019-01-31 (30%); C4g 2019-02-28 (25%); C4g 2019-05-31 (21%); C4g 2019-06-30 (33%); C4g 2019-07-31 (37%); C4g 2019-09-30 (31%); C4g 2019-10-31 (34%); C4g 2019-11-30 (35%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C1 29%, C4 35%, C5 35%, C7 29%, C9 23%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £99.01-£224.87/MWh, net margin £122.21
- C1g (gas): tariff £25.33-£36.05/MWh, net margin £156.37
- C2 (electricity): tariff £113.05-£227.85/MWh, net margin £145.64
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £134.46
- C3 (electricity): tariff £120.68-£126.90/MWh, net margin £-78.59 -- **net-negative**
- C3g (gas): tariff £23.00-£28.80/MWh, net margin £97.85
- C4 (electricity): tariff £99.60-£224.05/MWh, net margin £129.76
- C4g (gas): tariff £19.47-£33.61/MWh, net margin £101.05
- C5 (electricity): tariff £126.07-£153.36/MWh, net margin £150.17
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
- Bills issued: 204, average clarity 0.823, average bill shock 17.2%, bad debt provision £98.82, avg complaint probability 4.7%
- Solvency signal: £217,665/customer (12 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2019 produced a net gain of £233,981.90 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £128,481.98 (gross £791,755.83, capital £1,962.86)
  - Electricity: gross £714,576.28, capital £1,952.57, net £117,993.86
  - Gas: gross £77,179.55, capital £10.29, net £10,488.12
- Treasury at year end: £2,924,252.25
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
- Average CLV (Point-in-Time, year-end 2020): £419,047.79
  - By billing account: C1 £4,903.36, C1_2 £15.59, C2 £6,579.09, C3 £6,764.65, C4 £7,131.00, C5 £14,191.72, C6 £19,225.87, C7 £8,256.16, C8 £9,465.41, C9 £8,517.67, C_IC1 £1,351,950.59, C_IC2 £876,951.47, C_IC3 £2,077,701.04, C_IC4 £1,475,015.42
- Bill shock events (>=20%): 53 -- C1 2020-04-30 (20%); C1g 2020-01-31 (21%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-29 (23%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (32%); C4 2020-09-30 (23%); C4 2020-10-31 (24%); C4 2020-11-30 (25%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (49%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 35%, C4 41%, C5 32%, C7 20%, C8 26%, C9 23%, C_IC1 41%, C_IC2 41%, C_IC3 20%

**Pricing & Margin**

- C1 (electricity): tariff £99.01-£189.01/MWh, net margin £99.22
- C1_2 (electricity): tariff £133.55/MWh, net margin £-1.02 -- **net-negative**
- C1g (gas): tariff £25.33/MWh, net margin £145.23
- C2 (electricity): tariff £113.06-£227.85/MWh, net margin £201.59
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £143.77
- C3 (electricity): tariff £120.68/MWh, net margin £25.94
- C3g (gas): tariff £23.00/MWh, net margin £82.00
- C4 (electricity): tariff £96.23-£190.15/MWh, net margin £91.63
- C4g (gas): tariff £16.09-£19.47/MWh, net margin £86.36
- C5 (electricity): tariff £126.07/MWh, net margin £-3.59 -- **net-negative**
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
- Bills issued: 205, average clarity 0.831, average bill shock 14.4%, bad debt provision £-0.00, avg complaint probability 4.3%
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

**Year narrative:** 2020 produced a net gain of £128,481.98 across 19 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £75,537.91 (gross £763,149.08, capital £5,603.57)
  - Electricity: gross £680,540.29, capital £5,590.58, net £65,714.71
  - Gas: gross £82,608.79, capital £12.99, net £9,823.20
- Treasury at year end: £2,957,719.11
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2021-12-31 period 48, net margin £-229.84

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2021): £424,694.17
  - By billing account: C1 £4,418.45, C1_2 £905.55, C2 £6,660.04, C3 £7,043.01, C4 £5,096.06, C5 £11,319.85, C6 £18,069.64, C7 £7,714.38, C8 £8,601.83, C9 £7,807.64, C_IC1 £1,364,049.15, C_IC2 £744,424.30, C_IC3 £2,268,270.05, C_IC4 £1,491,338.48
- Bill shock events (>=20%): 47 -- C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (62%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (32%); C4 2021-09-30 (25%); C4 2021-10-31 (47%); C4 2021-11-30 (35%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%); C1_2 2021-01-31 (1207%); C1_2 2021-05-31 (33%); C1_2 2021-06-30 (55%); C1_2 2021-10-31 (76%); C1_2 2021-11-30 (75%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C7 20%, C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £133.55-£333.14/MWh, net margin £-89.36 -- **net-negative**
- C2 (electricity): tariff £113.06-£274.50/MWh, net margin £198.84
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £126.10
- C4 (electricity): tariff £96.23-£274.50/MWh, net margin £-37.46 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-302.82 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.10/MWh, net margin £295.82
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
- Bills issued: 168, average clarity 0.816, average bill shock 24.2%, bad debt provision £296.28, avg complaint probability 4.8%
- Solvency signal: £268,884/customer (11 customers) — OK (Ofgem floor £130/customer)

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

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £75,537.91 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 47 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £337,384.05 (gross £1,049,228.07, capital £13,282.04)
  - Electricity: gross £958,836.70, capital £13,229.01, net £328,645.64
  - Gas: gross £90,391.37, capital £53.03, net £8,738.41
- Treasury at year end: £3,161,942.85
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2 0.96 (avg 0.96), C2g 0.85 (avg 0.85), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
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
- Worst single period: C6 on 2022-12-31 period 48, net margin £-659.58

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2022): £420,083.10
  - By billing account: C1 £4,166.68, C1_2 £1,801.24, C2 £6,414.95, C3 £4,743.51, C4 £3,259.98, C5 £9,045.42, C6 £15,428.50, C7 £6,083.67, C8 £7,993.58, C9 £8,694.75, C_IC1 £1,197,881.25, C_IC2 £638,009.68, C_IC3 £2,846,137.59, C_IC4 £1,131,502.63
- Bill shock events (>=20%): 71 -- C7 2022-01-31 (52%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C2g 2022-04-30 (64%); C2g 2022-05-31 (36%); C2g 2022-06-30 (30%); C2g 2022-09-30 (58%); C2g 2022-11-30 (54%); C2g 2022-12-31 (61%); C6 2022-04-30 (43%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (31%); C4 2022-09-30 (28%); C4 2022-10-31 (61%); C4 2022-11-30 (35%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (109%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C1_2 2022-01-31 (141%); C1_2 2022-02-28 (28%); C1_2 2022-04-30 (23%); C1_2 2022-05-31 (43%); C1_2 2022-06-30 (34%); C1_2 2022-09-30 (51%); C1_2 2022-11-30 (79%); C1_2 2022-12-31 (61%)
- Churn risk (accounts renewing in 2022): 11 at risk (≥20% churn prob): C1_2 41%, C2 38%, C4 38%, C6 35%, C7 29%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.96-£333.14/MWh, net margin £184.51
- C2 (electricity): tariff £143.79-£457.50/MWh, net margin £2.28
- C2g (gas): tariff £35.00-£95.00/MWh, net margin £-102.36 -- **net-negative**
- C4 (electricity): tariff £143.79-£457.50/MWh, net margin £-332.76 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,159.15 -- **net-negative**
- C6 (electricity): tariff £197.10-£412.09/MWh, net margin £239.43
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,632.87 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £73.71
- C9 (electricity): tariff £138.51-£389.58/MWh, net margin £110.68
- C_IC1 (electricity): tariff £-83.39-£463.03/MWh, net margin £136,500.23
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £75,781.66
- C_IC3 (electricity): tariff £146.89-£391.32/MWh, net margin £111,799.38
- C_IC3g (gas): tariff £116.42-£125.90/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £5,919.38

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 2 -- £3,470,383.21 -> £3,053,423.02 (12.0%); £3,470,561.49 -> £3,052,877.22 (12.0%)
- Bills issued: 168, average clarity 0.791, average bill shock 23.0%, bad debt provision £1,033.22, avg complaint probability 5.6%
- Solvency signal: £287,449/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £184,708.07 vs. naked (unhedged) net margin: £1,207,112.18
- hedging cost £1,022,404.11 vs. a fully unhedged book (commodity-only: actual net £184,708.07 vs. naked net £1,207,112.18)
  - C1_2: actual £-584.36 vs. naked £1,300.27 -- hedging cost £1,884.63
  - C2: actual £-191.17 vs. naked £524.01 -- hedging cost £715.18
  - C2g: actual £-258.53 vs. naked £262.02 -- hedging cost £520.55
  - C4: actual £-292.88 vs. naked £597.69 -- hedging cost £890.57
  - C4g: actual £-1,950.48 vs. naked £1,336.80 -- hedging cost £3,287.28
  - C6: actual £1,245.22 vs. naked £4,116.60 -- hedging cost £2,871.37
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-481.87 vs. naked £1,102.92 -- hedging cost £1,584.78
  - C9: actual £-49.07 vs. naked £1,012.53 -- hedging cost £1,061.60
  - C_IC1: actual £212,837.07 vs. naked £251,120.17 -- hedging cost £38,283.10
  - C_IC2: actual £87,095.73 vs. naked £126,396.62 -- hedging cost £39,300.89
  - C_IC3: actual £-124,202.28 vs. naked £488,702.92 -- hedging cost £612,905.20
  - C_IC3g: actual £8,513.79 vs. naked £123,301.26 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £205,056.67 -- hedging cost £201,583.86

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £337,384.05 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 71 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £145,719.23 (gross £955,949.38, capital £10,044.58)
  - Electricity: gross £834,588.49, capital £9,961.08, net £136,636.20
  - Gas: gross £121,360.89, capital £83.49, net £9,083.03
- Treasury at year end: £3,381,632.54
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.91 (avg 0.91), C2 0.95 (avg 0.95), C2g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,137,462.09, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-02-23: treasury £3,137,445.16, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-03-25: treasury £3,137,428.42, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,209.10 / stressed £43,956.99) ratio 2.76
  - 2023-04-24: treasury £3,217,091.94, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,230.41 / stressed £48,907.75) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C6 on 2023-12-31 period 48, net margin £-759.50

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2023): £360,193.66
  - By billing account: C1 £3,664.92, C1_2 £1,939.77, C2 £4,959.18, C3 £4,394.93, C4 £2,167.94, C5 £7,536.56, C6 £17,154.54, C7 £5,371.96, C8 £7,237.37, C9 £6,949.46, C_IC1 £1,286,766.96, C_IC2 £637,552.50, C_IC3 £1,894,647.17, C_IC4 £1,162,368.02
- Bill shock events (>=20%): 49 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C2 2023-04-30 (28%); C2g 2023-04-30 (34%); C2g 2023-05-31 (38%); C2g 2023-06-30 (37%); C2g 2023-10-31 (85%); C2g 2023-11-30 (56%); C6 2023-04-30 (31%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (26%); C4 2023-04-30 (32%); C4 2023-09-30 (26%); C4 2023-11-30 (29%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (43%); C4g 2023-11-30 (63%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (100%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%); C1_2 2023-05-31 (38%); C1_2 2023-06-30 (43%); C1_2 2023-10-31 (73%); C1_2 2023-11-30 (83%)
- Churn risk (accounts renewing in 2023): 10 at risk (≥20% churn prob): C2 41%, C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.96-£267.80/MWh, net margin £-439.82 -- **net-negative**
- C2 (electricity): tariff £208.21-£457.50/MWh, net margin £88.59
- C2g (gas): tariff £70.00-£95.00/MWh, net margin £136.47
- C4 (electricity): tariff £198.37-£457.50/MWh, net margin £-1.53 -- **net-negative**
- C4g (gas): tariff £64.52-£95.00/MWh, net margin £-1,053.36 -- **net-negative**
- C6 (electricity): tariff £338.13-£412.09/MWh, net margin £620.58
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-144.77 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £159.02
- C9 (electricity): tariff £192.59-£389.58/MWh, net margin £396.72
- C_IC1 (electricity): tariff £-60.00-£463.03/MWh, net margin £162,662.79
- C_IC2 (electricity): tariff £-186.24-£476.36/MWh, net margin £85,767.63
- C_IC3 (electricity): tariff £95.69-£280.44/MWh, net margin £-118,400.86 -- **net-negative**
- C_IC3g (gas): tariff £55.69-£116.42/MWh, net margin £9,999.92
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £5,927.85

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): 47 -- £3,768,906.00 -> £3,381,557.94 (10.3%); £3,768,906.15 -> £3,381,557.94 (10.3%); £3,768,906.30 -> £3,381,557.94 (10.3%); £3,768,906.46 -> £3,381,557.93 (10.3%); £3,768,906.61 -> £3,381,557.93 (10.3%); £3,768,906.76 -> £3,381,557.93 (10.3%); £3,768,906.92 -> £3,381,557.93 (10.3%); £3,768,907.07 -> £3,381,557.93 (10.3%); £3,768,907.23 -> £3,381,557.93 (10.3%); £3,768,907.39 -> £3,381,557.93 (10.3%); £3,768,907.54 -> £3,381,557.93 (10.3%); £3,768,907.70 -> £3,381,557.93 (10.3%); £3,768,907.86 -> £3,381,557.92 (10.3%); £3,768,908.03 -> £3,381,557.92 (10.3%); £3,768,908.22 -> £3,381,557.92 (10.3%); £3,768,908.42 -> £3,381,557.91 (10.3%); £3,768,908.64 -> £3,381,557.90 (10.3%); £3,768,908.89 -> £3,381,557.89 (10.3%); £3,768,909.15 -> £3,381,557.87 (10.3%); £3,768,909.41 -> £3,381,557.86 (10.3%); £3,768,909.67 -> £3,381,557.85 (10.3%); £3,768,909.92 -> £3,381,557.84 (10.3%); £3,768,910.18 -> £3,381,557.82 (10.3%); £3,768,910.44 -> £3,381,557.81 (10.3%); £3,768,910.70 -> £3,381,557.80 (10.3%); £3,768,910.97 -> £3,381,557.78 (10.3%); £3,768,911.24 -> £3,381,557.77 (10.3%); £3,768,911.50 -> £3,381,557.76 (10.3%); £3,768,911.76 -> £3,381,557.75 (10.3%); £3,768,912.01 -> £3,381,557.74 (10.3%); £3,768,912.27 -> £3,381,557.74 (10.3%); £3,768,912.52 -> £3,381,557.73 (10.3%); £3,768,912.78 -> £3,381,557.71 (10.3%); £3,768,913.04 -> £3,381,557.69 (10.3%); £3,768,913.29 -> £3,381,557.67 (10.3%); £3,768,913.55 -> £3,381,557.65 (10.3%); £3,768,913.81 -> £3,381,557.63 (10.3%); £3,768,914.08 -> £3,381,557.59 (10.3%); £3,768,914.35 -> £3,381,557.56 (10.3%); £3,768,914.61 -> £3,381,557.53 (10.3%); £3,768,914.86 -> £3,381,557.50 (10.3%); £3,768,915.12 -> £3,381,557.47 (10.3%); £3,768,915.38 -> £3,381,557.45 (10.3%); £3,768,915.64 -> £3,381,557.44 (10.3%); £3,768,915.90 -> £3,381,557.43 (10.3%); £3,768,916.15 -> £3,381,557.42 (10.3%); £3,768,916.37 -> £3,381,632.54 (10.3%)
- Bills issued: 168, average clarity 0.811, average bill shock 17.5%, bad debt provision £909.78, avg complaint probability 4.9%
- Solvency signal: £307,421/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £380,385.87 vs. naked (unhedged) net margin: £1,219,604.72
- hedging cost £839,218.85 vs. a fully unhedged book (commodity-only: actual net £380,385.87 vs. naked net £1,219,604.72)
  - C1_2: actual £680.54 vs. naked £1,720.09 -- hedging cost £1,039.55
  - C2: actual £106.23 vs. naked £797.97 -- hedging cost £691.74
  - C2g: actual £206.68 vs. naked £669.84 -- hedging cost £463.16
  - C4: actual £310.61 vs. naked £704.57 -- hedging cost £393.96
  - C4g: actual £490.72 vs. naked £1,008.67 -- hedging cost £517.95
  - C6: actual £1,521.80 vs. naked £5,191.47 -- hedging cost £3,669.67
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £140.61 vs. naked £1,972.23 -- hedging cost £1,831.62
  - C9: actual £626.21 vs. naked £2,129.86 -- hedging cost £1,503.65
  - C_IC1: actual £141,611.78 vs. naked £284,485.88 -- hedging cost £142,874.09
  - C_IC2: actual £93,826.81 vs. naked £161,876.12 -- hedging cost £68,049.31
  - C_IC3: actual £128,018.29 vs. naked £401,823.63 -- hedging cost £273,805.34
  - C_IC3g: actual £8,660.26 vs. naked £123,107.25 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £232,127.67 -- hedging cost £228,435.92

**Year narrative:** 2023 produced a net gain of £145,719.23 across 14 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 49 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £347,473.07 (gross £1,257,802.02, capital £9,522.03)
  - Electricity: gross £1,132,855.54, capital £9,477.19, net £336,767.90
  - Gas: gross £124,946.48, capital £44.84, net £10,705.17
- Treasury at year end: £3,775,213.53
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.87 (avg 0.87), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C4 on 2024-09-28 period 48, net margin £-203.82

**Customer Book**

- Active accounts: 14 (C1_2, C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £346,174.02
  - By billing account: C1 £3,264.20, C1_2 £2,663.27, C2 £4,354.82, C3 £4,001.55, C4 £2,616.39, C5 £7,769.52, C6 £15,211.87, C7 £4,946.25, C8 £7,000.45, C9 £7,040.91, C_IC1 £1,147,593.05, C_IC2 £675,702.27, C_IC3 £2,007,120.95, C_IC4 £957,150.73
- Bill shock events (>=20%): 41 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C2 2024-04-30 (32%); C2g 2024-02-29 (23%); C2g 2024-04-30 (35%); C2g 2024-05-31 (44%); C2g 2024-07-31 (22%); C2g 2024-09-30 (45%); C2g 2024-10-31 (31%); C2g 2024-11-30 (48%); C8 2024-02-29 (23%); C8 2024-04-30 (34%); C8 2024-05-31 (47%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (31%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C1_2 2024-01-31 (21%); C1_2 2024-02-29 (28%); C1_2 2024-04-30 (23%); C1_2 2024-05-31 (44%); C1_2 2024-09-30 (51%); C1_2 2024-10-31 (45%); C1_2 2024-11-30 (57%)
- Churn risk (accounts renewing in 2024): 8 at risk (≥20% churn prob): C2 41%, C4 38%, C6 26%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC3 41%, C_IC4 20%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01-£267.80/MWh, net margin £760.69
- C2 (electricity): tariff £157.80-£397.50/MWh, net margin £210.04
- C2g (gas): tariff £48.32-£70.00/MWh, net margin £265.53
- C4 (electricity): tariff £198.37-£378.70/MWh, net margin £23.44
- C4g (gas): tariff £64.52/MWh, net margin £408.87
- C6 (electricity): tariff £338.13/MWh, net margin £561.26
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £635.74
- C8 (electricity): tariff £159.61-£397.50/MWh, net margin £404.66
- C9 (electricity): tariff £165.00-£367.66/MWh, net margin £656.09
- C_IC1 (electricity): tariff £-98.58-£330.71/MWh, net margin £125,749.68
- C_IC2 (electricity): tariff £-106.92-£354.54/MWh, net margin £69,822.45
- C_IC3 (electricity): tariff £88.52-£182.68/MWh, net margin £131,992.56
- C_IC3g (gas): tariff £48.22-£55.69/MWh, net margin £10,030.76
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £5,951.30

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): 4271 -- £3,771,364.35 -> £3,381,632.54 (10.3%); £3,771,364.53 -> £3,381,632.54 (10.3%); £3,771,364.70 -> £3,381,632.54 (10.3%); £3,771,364.88 -> £3,381,632.54 (10.3%); £3,771,365.05 -> £3,381,632.54 (10.3%); £3,771,365.22 -> £3,381,632.55 (10.3%); £3,771,365.39 -> £3,381,632.55 (10.3%); £3,771,365.56 -> £3,381,632.55 (10.3%); £3,771,365.74 -> £3,381,632.55 (10.3%); £3,771,365.91 -> £3,381,632.55 (10.3%); £3,771,366.09 -> £3,381,632.55 (10.3%); £3,771,366.26 -> £3,381,632.55 (10.3%); £3,771,366.43 -> £3,381,632.54 (10.3%); £3,771,366.62 -> £3,381,632.59 (10.3%); £3,771,366.83 -> £3,381,632.64 (10.3%); £3,771,367.05 -> £3,381,632.69 (10.3%); £3,771,367.30 -> £3,381,632.74 (10.3%); £3,771,367.56 -> £3,381,632.79 (10.3%); £3,771,367.84 -> £3,381,632.83 (10.3%); £3,771,368.12 -> £3,381,632.87 (10.3%); £3,771,368.41 -> £3,381,632.90 (10.3%); £3,771,368.70 -> £3,381,632.90 (10.3%); £3,771,369.00 -> £3,381,632.90 (10.3%); £3,771,369.28 -> £3,381,632.90 (10.3%); £3,771,369.57 -> £3,381,632.90 (10.3%); £3,771,369.86 -> £3,381,632.90 (10.3%); £3,771,370.14 -> £3,381,632.89 (10.3%); £3,771,370.42 -> £3,381,632.89 (10.3%); £3,771,370.69 -> £3,381,632.89 (10.3%); £3,771,370.98 -> £3,381,632.89 (10.3%); £3,771,371.26 -> £3,381,632.89 (10.3%); £3,771,371.55 -> £3,381,632.93 (10.3%); £3,771,371.83 -> £3,381,632.99 (10.3%); £3,771,372.12 -> £3,381,633.05 (10.3%); £3,771,372.34 -> £3,381,633.12 (10.3%); £3,771,372.55 -> £3,381,633.19 (10.3%); £3,771,372.77 -> £3,381,633.25 (10.3%); £3,771,373.07 -> £3,381,633.34 (10.3%); £3,771,373.36 -> £3,381,633.42 (10.3%); £3,771,373.64 -> £3,381,633.40 (10.3%); £3,771,373.93 -> £3,381,633.38 (10.3%); £3,771,374.22 -> £3,381,633.36 (10.3%); £3,771,374.51 -> £3,381,633.34 (10.3%); £3,771,374.80 -> £3,381,633.33 (10.3%); £3,771,375.09 -> £3,381,633.33 (10.3%); £3,771,375.35 -> £3,381,633.32 (10.3%); £3,771,375.59 -> £3,381,633.32 (10.3%); £3,771,375.81 -> £3,381,633.32 (10.3%); £3,771,375.99 -> £3,381,633.32 (10.3%); £3,771,376.17 -> £3,381,633.32 (10.3%); £3,771,376.33 -> £3,381,633.33 (10.3%); £3,771,376.50 -> £3,381,633.33 (10.3%); £3,771,376.67 -> £3,381,633.33 (10.3%); £3,771,376.84 -> £3,381,633.33 (10.3%); £3,771,377.01 -> £3,381,633.34 (10.3%); £3,771,377.18 -> £3,381,633.34 (10.3%); £3,771,377.35 -> £3,381,633.34 (10.3%); £3,771,377.52 -> £3,381,633.34 (10.3%); £3,771,377.69 -> £3,381,633.35 (10.3%); £3,771,377.86 -> £3,381,633.34 (10.3%); £3,771,378.03 -> £3,381,633.34 (10.3%); £3,771,378.21 -> £3,381,633.38 (10.3%); £3,771,378.42 -> £3,381,633.44 (10.3%); £3,771,378.65 -> £3,381,633.49 (10.3%); £3,771,378.88 -> £3,381,633.54 (10.3%); £3,771,379.13 -> £3,381,633.59 (10.3%); £3,771,379.41 -> £3,381,633.63 (10.3%); £3,771,379.69 -> £3,381,633.67 (10.3%); £3,771,379.97 -> £3,381,633.70 (10.3%); £3,771,380.26 -> £3,381,633.70 (10.3%); £3,771,380.54 -> £3,381,633.70 (10.3%); £3,771,380.82 -> £3,381,633.70 (10.3%); £3,771,381.09 -> £3,381,633.70 (10.3%); £3,771,381.38 -> £3,381,633.70 (10.3%); £3,771,381.66 -> £3,381,633.70 (10.3%); £3,771,381.93 -> £3,381,633.70 (10.3%); £3,771,382.21 -> £3,381,633.69 (10.3%); £3,771,382.48 -> £3,381,633.69 (10.3%); £3,771,382.76 -> £3,381,633.69 (10.3%); £3,771,383.04 -> £3,381,633.73 (10.3%); £3,771,383.25 -> £3,381,633.79 (10.3%); £3,771,383.46 -> £3,381,633.85 (10.3%); £3,771,383.67 -> £3,381,633.92 (10.3%); £3,771,383.89 -> £3,381,633.99 (10.3%); £3,771,384.10 -> £3,381,634.05 (10.3%); £3,771,384.32 -> £3,381,634.13 (10.3%); £3,771,384.53 -> £3,381,634.22 (10.3%); £3,771,384.80 -> £3,381,634.19 (10.3%); £3,771,385.09 -> £3,381,634.17 (10.3%); £3,771,385.37 -> £3,381,634.14 (10.3%); £3,771,385.65 -> £3,381,634.12 (10.3%); £3,771,385.94 -> £3,381,634.12 (10.3%); £3,771,386.22 -> £3,381,634.11 (10.3%); £3,771,386.48 -> £3,381,634.11 (10.3%); £3,771,386.71 -> £3,381,634.10 (10.3%); £3,771,386.93 -> £3,381,634.10 (10.3%); £3,771,387.10 -> £3,381,634.10 (10.3%); £3,771,387.28 -> £3,381,634.10 (10.3%); £3,771,387.44 -> £3,381,634.10 (10.3%); £3,771,387.61 -> £3,381,634.10 (10.3%); £3,771,387.78 -> £3,381,634.11 (10.3%); £3,771,387.95 -> £3,381,634.11 (10.3%); £3,771,388.12 -> £3,381,634.11 (10.3%); £3,771,388.29 -> £3,381,634.11 (10.3%); £3,771,388.46 -> £3,381,634.11 (10.3%); £3,771,388.63 -> £3,381,634.12 (10.3%); £3,771,388.80 -> £3,381,634.12 (10.3%); £3,771,388.97 -> £3,381,634.11 (10.3%); £3,771,389.14 -> £3,381,634.11 (10.3%); £3,771,389.33 -> £3,381,634.16 (10.3%); £3,771,389.53 -> £3,381,634.21 (10.3%); £3,771,389.76 -> £3,381,634.26 (10.3%); £3,771,390.01 -> £3,381,634.31 (10.3%); £3,771,390.27 -> £3,381,634.36 (10.3%); £3,771,390.55 -> £3,381,634.40 (10.3%); £3,771,390.83 -> £3,381,634.44 (10.3%); £3,771,391.12 -> £3,381,634.47 (10.3%); £3,771,391.40 -> £3,381,634.47 (10.3%); £3,771,391.68 -> £3,381,634.47 (10.3%); £3,771,391.98 -> £3,381,634.47 (10.3%); £3,771,392.27 -> £3,381,634.46 (10.3%); £3,771,392.56 -> £3,381,634.46 (10.3%); £3,771,392.84 -> £3,381,634.46 (10.3%); £3,771,393.11 -> £3,381,634.46 (10.3%); £3,771,393.39 -> £3,381,634.46 (10.3%); £3,771,393.68 -> £3,381,634.46 (10.3%); £3,771,393.95 -> £3,381,634.46 (10.3%); £3,771,394.24 -> £3,381,634.50 (10.3%); £3,771,394.52 -> £3,381,634.55 (10.3%); £3,771,394.73 -> £3,381,634.62 (10.3%); £3,771,395.01 -> £3,381,634.69 (10.3%); £3,771,395.22 -> £3,381,634.75 (10.3%); £3,771,395.43 -> £3,381,634.82 (10.3%); £3,771,395.65 -> £3,381,634.90 (10.3%); £3,771,395.86 -> £3,381,634.98 (10.3%); £3,771,396.14 -> £3,381,634.96 (10.3%); £3,771,396.42 -> £3,381,634.94 (10.3%); £3,771,396.70 -> £3,381,634.91 (10.3%); £3,771,396.98 -> £3,381,634.89 (10.3%); £3,771,397.26 -> £3,381,634.88 (10.3%); £3,771,397.56 -> £3,381,634.88 (10.3%); £3,771,397.81 -> £3,381,634.87 (10.3%); £3,771,398.04 -> £3,381,634.87 (10.3%); £3,771,398.26 -> £3,381,634.87 (10.3%); £3,771,398.43 -> £3,381,634.87 (10.3%); £3,771,398.59 -> £3,381,634.87 (10.3%); £3,771,398.75 -> £3,381,634.87 (10.3%); £3,771,398.93 -> £3,381,634.87 (10.3%); £3,771,399.09 -> £3,381,634.88 (10.3%); £3,771,399.26 -> £3,381,634.88 (10.3%); £3,771,399.43 -> £3,381,634.88 (10.3%); £3,771,399.60 -> £3,381,634.88 (10.3%); £3,771,399.77 -> £3,381,634.89 (10.3%); £3,771,399.94 -> £3,381,634.89 (10.3%); £3,771,400.11 -> £3,381,634.89 (10.3%); £3,771,400.28 -> £3,381,634.89 (10.3%); £3,771,400.45 -> £3,381,634.88 (10.3%); £3,771,400.63 -> £3,381,634.93 (10.3%); £3,771,400.83 -> £3,381,634.98 (10.3%); £3,771,401.05 -> £3,381,635.03 (10.3%); £3,771,401.29 -> £3,381,635.08 (10.3%); £3,771,401.56 -> £3,381,635.13 (10.3%); £3,771,401.84 -> £3,381,635.17 (10.3%); £3,771,402.11 -> £3,381,635.21 (10.3%); £3,771,402.39 -> £3,381,635.24 (10.3%); £3,771,402.67 -> £3,381,635.24 (10.3%); £3,771,402.95 -> £3,381,635.24 (10.3%); £3,771,403.22 -> £3,381,635.24 (10.3%); £3,771,403.50 -> £3,381,635.24 (10.3%); £3,771,403.77 -> £3,381,635.23 (10.3%); £3,771,404.05 -> £3,381,635.23 (10.3%); £3,771,404.33 -> £3,381,635.23 (10.3%); £3,771,404.61 -> £3,381,635.23 (10.3%); £3,771,404.89 -> £3,381,635.23 (10.3%); £3,771,405.16 -> £3,381,635.23 (10.3%); £3,771,405.44 -> £3,381,635.27 (10.3%); £3,771,405.65 -> £3,381,635.32 (10.3%); £3,771,405.93 -> £3,381,635.39 (10.3%); £3,771,406.20 -> £3,381,635.46 (10.3%); £3,771,406.41 -> £3,381,635.52 (10.3%); £3,771,406.67 -> £3,381,635.59 (10.3%); £3,771,406.95 -> £3,381,635.67 (10.3%); £3,771,407.17 -> £3,381,635.75 (10.3%); £3,771,407.46 -> £3,381,635.73 (10.3%); £3,771,407.73 -> £3,381,635.70 (10.3%); £3,771,408.01 -> £3,381,635.68 (10.3%); £3,771,408.29 -> £3,381,635.66 (10.3%); £3,771,408.57 -> £3,381,635.65 (10.3%); £3,771,408.84 -> £3,381,635.65 (10.3%); £3,771,409.10 -> £3,381,635.64 (10.3%); £3,771,409.34 -> £3,381,635.64 (10.3%); £3,771,409.55 -> £3,381,635.64 (10.3%); £3,771,409.72 -> £3,381,635.64 (10.3%); £3,771,409.88 -> £3,381,635.64 (10.3%); £3,771,410.04 -> £3,381,635.64 (10.3%); £3,771,410.20 -> £3,381,635.64 (10.3%); £3,771,410.35 -> £3,381,635.64 (10.3%); £3,771,410.52 -> £3,381,635.64 (10.3%); £3,771,410.68 -> £3,381,635.65 (10.3%); £3,771,410.84 -> £3,381,635.65 (10.3%); £3,771,411.01 -> £3,381,635.65 (10.3%); £3,771,411.17 -> £3,381,635.65 (10.3%); £3,771,411.34 -> £3,381,635.65 (10.3%); £3,771,411.50 -> £3,381,635.65 (10.3%); £3,771,411.65 -> £3,381,635.64 (10.3%); £3,771,411.83 -> £3,381,635.69 (10.3%); £3,771,412.03 -> £3,381,635.74 (10.3%); £3,771,412.24 -> £3,381,635.80 (10.3%); £3,771,412.48 -> £3,381,635.84 (10.3%); £3,771,412.73 -> £3,381,635.89 (10.3%); £3,771,413.01 -> £3,381,635.93 (10.3%); £3,771,413.28 -> £3,381,635.97 (10.3%); £3,771,413.55 -> £3,381,636.00 (10.3%); £3,771,413.82 -> £3,381,636.00 (10.3%); £3,771,414.08 -> £3,381,636.00 (10.3%); £3,771,414.36 -> £3,381,636.00 (10.3%); £3,771,414.63 -> £3,381,636.00 (10.3%); £3,771,414.90 -> £3,381,636.00 (10.3%); £3,771,415.17 -> £3,381,636.00 (10.3%); £3,771,415.43 -> £3,381,636.00 (10.3%); £3,771,415.70 -> £3,381,635.99 (10.3%); £3,771,415.97 -> £3,381,635.99 (10.3%); £3,771,416.23 -> £3,381,635.99 (10.3%); £3,771,416.50 -> £3,381,636.03 (10.3%); £3,771,416.70 -> £3,381,636.09 (10.3%); £3,771,416.91 -> £3,381,636.15 (10.3%); £3,771,417.11 -> £3,381,636.22 (10.3%); £3,771,417.31 -> £3,381,636.29 (10.3%); £3,771,417.58 -> £3,381,636.35 (10.3%); £3,771,417.78 -> £3,381,636.43 (10.3%); £3,771,417.98 -> £3,381,636.51 (10.3%); £3,771,418.25 -> £3,381,636.49 (10.3%); £3,771,418.52 -> £3,381,636.46 (10.3%); £3,771,418.78 -> £3,381,636.44 (10.3%); £3,771,419.05 -> £3,381,636.42 (10.3%); £3,771,419.32 -> £3,381,636.41 (10.3%); £3,771,419.59 -> £3,381,636.41 (10.3%); £3,771,419.84 -> £3,381,636.40 (10.3%); £3,771,420.07 -> £3,381,636.40 (10.3%); £3,771,420.28 -> £3,381,636.39 (10.3%); £3,771,420.43 -> £3,381,636.39 (10.3%); £3,771,420.57 -> £3,381,636.39 (10.3%); £3,771,420.71 -> £3,381,636.40 (10.3%); £3,771,420.86 -> £3,381,636.40 (10.3%); £3,771,421.01 -> £3,381,636.40 (10.3%); £3,771,421.15 -> £3,381,636.40 (10.3%); £3,771,421.29 -> £3,381,636.40 (10.3%); £3,771,421.42 -> £3,381,636.41 (10.3%); £3,771,421.57 -> £3,381,636.41 (10.3%); £3,771,421.70 -> £3,381,636.41 (10.3%); £3,771,421.84 -> £3,381,636.41 (10.3%); £3,771,421.98 -> £3,381,636.41 (10.3%); £3,771,422.12 -> £3,381,636.41 (10.3%); £3,771,422.28 -> £3,381,636.40 (10.3%); £3,771,422.45 -> £3,381,636.40 (10.3%); £3,771,422.64 -> £3,381,636.39 (10.3%); £3,771,422.85 -> £3,381,636.39 (10.3%); £3,771,423.07 -> £3,381,636.38 (10.3%); £3,771,423.31 -> £3,381,636.37 (10.3%); £3,771,423.54 -> £3,381,636.36 (10.3%); £3,771,423.77 -> £3,381,636.36 (10.3%); £3,771,424.01 -> £3,381,636.36 (10.3%); £3,771,424.24 -> £3,381,636.35 (10.3%); £3,771,424.48 -> £3,381,636.35 (10.3%); £3,771,424.72 -> £3,381,636.34 (10.3%); £3,771,424.95 -> £3,381,636.34 (10.3%); £3,771,425.19 -> £3,381,636.33 (10.3%); £3,771,425.44 -> £3,381,636.33 (10.3%); £3,771,425.67 -> £3,381,636.33 (10.3%); £3,771,425.91 -> £3,381,636.32 (10.3%); £3,771,426.15 -> £3,381,636.32 (10.3%); £3,771,426.39 -> £3,381,636.32 (10.3%); £3,771,426.61 -> £3,381,636.31 (10.3%); £3,771,426.79 -> £3,381,636.29 (10.3%); £3,771,426.96 -> £3,381,636.27 (10.3%); £3,771,427.14 -> £3,381,636.25 (10.3%); £3,771,427.32 -> £3,381,636.23 (10.3%); £3,771,427.49 -> £3,381,636.20 (10.3%); £3,771,427.67 -> £3,381,636.18 (10.3%); £3,771,427.91 -> £3,381,636.15 (10.3%); £3,771,428.14 -> £3,381,636.13 (10.3%); £3,771,428.37 -> £3,381,636.11 (10.3%); £3,771,428.60 -> £3,381,636.09 (10.3%); £3,771,428.84 -> £3,381,636.08 (10.3%); £3,771,429.07 -> £3,381,636.08 (10.3%); £3,771,429.29 -> £3,381,636.07 (10.3%); £3,771,429.48 -> £3,381,636.07 (10.3%); £3,771,429.67 -> £3,381,636.06 (10.3%); £3,771,429.81 -> £3,381,636.06 (10.3%); £3,771,429.95 -> £3,381,636.06 (10.3%); £3,771,430.09 -> £3,381,636.06 (10.3%); £3,771,430.23 -> £3,381,636.06 (10.3%); £3,771,430.37 -> £3,381,636.06 (10.3%); £3,771,430.51 -> £3,381,636.06 (10.3%); £3,771,430.65 -> £3,381,636.07 (10.3%); £3,771,430.79 -> £3,381,636.07 (10.3%); £3,771,430.93 -> £3,381,636.07 (10.3%); £3,771,431.06 -> £3,381,636.07 (10.3%); £3,771,431.21 -> £3,381,636.07 (10.3%); £3,771,431.34 -> £3,381,636.07 (10.3%); £3,771,431.48 -> £3,381,636.07 (10.3%); £3,771,431.64 -> £3,381,636.07 (10.3%); £3,771,431.81 -> £3,381,636.07 (10.3%); £3,771,432.00 -> £3,381,636.07 (10.3%); £3,771,432.20 -> £3,381,636.06 (10.3%); £3,771,432.42 -> £3,381,636.05 (10.3%); £3,771,432.66 -> £3,381,636.04 (10.3%); £3,771,432.90 -> £3,381,636.03 (10.3%); £3,771,433.13 -> £3,381,636.02 (10.3%); £3,771,433.36 -> £3,381,636.01 (10.3%); £3,771,433.59 -> £3,381,636.00 (10.3%); £3,771,433.82 -> £3,381,635.99 (10.3%); £3,771,434.05 -> £3,381,635.98 (10.3%); £3,771,434.27 -> £3,381,635.97 (10.3%); £3,771,434.51 -> £3,381,635.97 (10.3%); £3,771,434.74 -> £3,381,635.96 (10.3%); £3,771,434.97 -> £3,381,635.95 (10.3%); £3,771,435.20 -> £3,381,635.95 (10.3%); £3,771,435.43 -> £3,381,635.94 (10.3%); £3,771,435.67 -> £3,381,635.94 (10.3%); £3,771,435.84 -> £3,381,635.93 (10.3%); £3,771,436.02 -> £3,381,635.91 (10.3%); £3,771,436.18 -> £3,381,635.89 (10.3%); £3,771,436.36 -> £3,381,635.87 (10.3%); £3,771,436.59 -> £3,381,635.85 (10.3%); £3,771,436.77 -> £3,381,635.82 (10.3%); £3,771,436.95 -> £3,381,635.79 (10.3%); £3,771,437.18 -> £3,381,635.77 (10.3%); £3,771,437.42 -> £3,381,635.74 (10.3%); £3,771,437.65 -> £3,381,635.72 (10.3%); £3,771,437.88 -> £3,381,635.70 (10.3%); £3,771,438.11 -> £3,381,635.69 (10.3%); £3,771,438.34 -> £3,381,635.69 (10.3%); £3,771,438.56 -> £3,381,635.68 (10.3%); £3,771,438.76 -> £3,381,635.68 (10.3%); £3,771,438.94 -> £3,381,635.67 (10.3%); £3,771,439.10 -> £3,381,635.67 (10.3%); £3,771,439.25 -> £3,381,635.67 (10.3%); £3,771,439.40 -> £3,381,635.68 (10.3%); £3,771,439.56 -> £3,381,635.68 (10.3%); £3,771,439.71 -> £3,381,635.68 (10.3%); £3,771,439.87 -> £3,381,635.68 (10.3%); £3,771,440.02 -> £3,381,635.68 (10.3%); £3,771,440.17 -> £3,381,635.69 (10.3%); £3,771,440.33 -> £3,381,635.69 (10.3%); £3,771,440.48 -> £3,381,635.69 (10.3%); £3,771,440.64 -> £3,381,635.69 (10.3%); £3,771,440.79 -> £3,381,635.69 (10.3%); £3,771,440.94 -> £3,381,635.68 (10.3%); £3,771,441.12 -> £3,381,635.73 (10.3%); £3,771,441.30 -> £3,381,635.78 (10.3%); £3,771,441.50 -> £3,381,635.83 (10.3%); £3,771,441.72 -> £3,381,635.88 (10.3%); £3,771,441.96 -> £3,381,635.93 (10.3%); £3,771,442.21 -> £3,381,635.97 (10.3%); £3,771,442.45 -> £3,381,636.01 (10.3%); £3,771,442.71 -> £3,381,636.04 (10.3%); £3,771,442.97 -> £3,381,636.04 (10.3%); £3,771,443.22 -> £3,381,636.04 (10.3%); £3,771,443.48 -> £3,381,636.03 (10.3%); £3,771,443.74 -> £3,381,636.03 (10.3%); £3,771,444.00 -> £3,381,636.03 (10.3%); £3,771,444.26 -> £3,381,636.03 (10.3%); £3,771,444.51 -> £3,381,636.03 (10.3%); £3,771,444.77 -> £3,381,636.03 (10.3%); £3,771,445.03 -> £3,381,636.03 (10.3%); £3,771,445.29 -> £3,381,636.03 (10.3%); £3,771,445.55 -> £3,381,636.06 (10.3%); £3,771,445.81 -> £3,381,636.12 (10.3%); £3,771,446.07 -> £3,381,636.19 (10.3%); £3,771,446.32 -> £3,381,636.25 (10.3%); £3,771,446.57 -> £3,381,636.32 (10.3%); £3,771,446.82 -> £3,381,636.39 (10.3%); £3,771,447.07 -> £3,381,636.47 (10.3%); £3,771,447.27 -> £3,381,636.55 (10.3%); £3,771,447.52 -> £3,381,636.53 (10.3%); £3,771,447.77 -> £3,381,636.50 (10.3%); £3,771,448.02 -> £3,381,636.48 (10.3%); £3,771,448.27 -> £3,381,636.46 (10.3%); £3,771,448.52 -> £3,381,636.45 (10.3%); £3,771,448.78 -> £3,381,636.45 (10.3%); £3,771,449.02 -> £3,381,636.44 (10.3%); £3,771,449.24 -> £3,381,636.44 (10.3%); £3,771,449.44 -> £3,381,636.44 (10.3%); £3,771,449.59 -> £3,381,636.44 (10.3%); £3,771,449.74 -> £3,381,636.44 (10.3%); £3,771,449.90 -> £3,381,636.44 (10.3%); £3,771,450.05 -> £3,381,636.44 (10.3%); £3,771,450.20 -> £3,381,636.45 (10.3%); £3,771,450.36 -> £3,381,636.45 (10.3%); £3,771,450.51 -> £3,381,636.45 (10.3%); £3,771,450.65 -> £3,381,636.45 (10.3%); £3,771,450.81 -> £3,381,636.45 (10.3%); £3,771,450.96 -> £3,381,636.46 (10.3%); £3,771,451.12 -> £3,381,636.46 (10.3%); £3,771,451.27 -> £3,381,636.45 (10.3%); £3,771,451.42 -> £3,381,636.45 (10.3%); £3,771,451.58 -> £3,381,636.49 (10.3%); £3,771,451.77 -> £3,381,636.55 (10.3%); £3,771,451.97 -> £3,381,636.60 (10.3%); £3,771,452.19 -> £3,381,636.65 (10.3%); £3,771,452.42 -> £3,381,636.69 (10.3%); £3,771,452.67 -> £3,381,636.74 (10.3%); £3,771,452.93 -> £3,381,636.77 (10.3%); £3,771,453.18 -> £3,381,636.81 (10.3%); £3,771,453.43 -> £3,381,636.81 (10.3%); £3,771,453.69 -> £3,381,636.81 (10.3%); £3,771,453.95 -> £3,381,636.81 (10.3%); £3,771,454.21 -> £3,381,636.80 (10.3%); £3,771,454.46 -> £3,381,636.80 (10.3%); £3,771,454.72 -> £3,381,636.80 (10.3%); £3,771,454.97 -> £3,381,636.80 (10.3%); £3,771,455.23 -> £3,381,636.80 (10.3%); £3,771,455.49 -> £3,381,636.80 (10.3%); £3,771,455.74 -> £3,381,636.80 (10.3%); £3,771,455.99 -> £3,381,636.84 (10.3%); £3,771,456.18 -> £3,381,636.89 (10.3%); £3,771,456.36 -> £3,381,636.96 (10.3%); £3,771,456.61 -> £3,381,637.03 (10.3%); £3,771,456.80 -> £3,381,637.09 (10.3%); £3,771,456.99 -> £3,381,637.16 (10.3%); £3,771,457.25 -> £3,381,637.24 (10.3%); £3,771,457.50 -> £3,381,637.33 (10.3%); £3,771,457.76 -> £3,381,637.30 (10.3%); £3,771,458.02 -> £3,381,637.28 (10.3%); £3,771,458.28 -> £3,381,637.25 (10.3%); £3,771,458.53 -> £3,381,637.23 (10.3%); £3,771,458.79 -> £3,381,637.23 (10.3%); £3,771,459.04 -> £3,381,637.22 (10.3%); £3,771,459.27 -> £3,381,637.22 (10.3%); £3,771,459.48 -> £3,381,637.21 (10.3%); £3,771,459.68 -> £3,381,637.21 (10.3%); £3,771,459.83 -> £3,381,637.21 (10.3%); £3,771,459.99 -> £3,381,637.21 (10.3%); £3,771,460.14 -> £3,381,637.21 (10.3%); £3,771,460.29 -> £3,381,637.22 (10.3%); £3,771,460.44 -> £3,381,637.22 (10.3%); £3,771,460.59 -> £3,381,637.22 (10.3%); £3,771,460.74 -> £3,381,637.22 (10.3%); £3,771,460.89 -> £3,381,637.22 (10.3%); £3,771,461.04 -> £3,381,637.23 (10.3%); £3,771,461.19 -> £3,381,637.23 (10.3%); £3,771,461.34 -> £3,381,637.23 (10.3%); £3,771,461.50 -> £3,381,637.23 (10.3%); £3,771,461.65 -> £3,381,637.22 (10.3%); £3,771,461.82 -> £3,381,637.26 (10.3%); £3,771,462.00 -> £3,381,637.31 (10.3%); £3,771,462.20 -> £3,381,637.37 (10.3%); £3,771,462.42 -> £3,381,637.41 (10.3%); £3,771,462.66 -> £3,381,637.46 (10.3%); £3,771,462.91 -> £3,381,637.50 (10.3%); £3,771,463.16 -> £3,381,637.54 (10.3%); £3,771,463.41 -> £3,381,637.57 (10.3%); £3,771,463.66 -> £3,381,637.57 (10.3%); £3,771,463.91 -> £3,381,637.57 (10.3%); £3,771,464.17 -> £3,381,637.57 (10.3%); £3,771,464.42 -> £3,381,637.57 (10.3%); £3,771,464.68 -> £3,381,637.57 (10.3%); £3,771,464.93 -> £3,381,637.56 (10.3%); £3,771,465.18 -> £3,381,637.56 (10.3%); £3,771,465.45 -> £3,381,637.56 (10.3%); £3,771,465.69 -> £3,381,637.56 (10.3%); £3,771,465.94 -> £3,381,637.56 (10.3%); £3,771,466.19 -> £3,381,637.60 (10.3%); £3,771,466.44 -> £3,381,637.65 (10.3%); £3,771,466.63 -> £3,381,637.72 (10.3%); £3,771,466.88 -> £3,381,637.79 (10.3%); £3,771,467.13 -> £3,381,637.85 (10.3%); £3,771,467.33 -> £3,381,637.92 (10.3%); £3,771,467.57 -> £3,381,638.00 (10.3%); £3,771,467.75 -> £3,381,638.08 (10.3%); £3,771,468.01 -> £3,381,638.06 (10.3%); £3,771,468.26 -> £3,381,638.03 (10.3%); £3,771,468.51 -> £3,381,638.01 (10.3%); £3,771,468.76 -> £3,381,637.99 (10.3%); £3,771,469.01 -> £3,381,637.98 (10.3%); £3,771,469.26 -> £3,381,637.98 (10.3%); £3,771,469.49 -> £3,381,637.97 (10.3%); £3,771,469.71 -> £3,381,637.97 (10.3%); £3,771,469.90 -> £3,381,637.97 (10.3%); £3,771,470.05 -> £3,381,637.97 (10.3%); £3,771,470.20 -> £3,381,637.97 (10.3%); £3,771,470.35 -> £3,381,637.97 (10.3%); £3,771,470.50 -> £3,381,637.97 (10.3%); £3,771,470.65 -> £3,381,637.97 (10.3%); £3,771,470.80 -> £3,381,637.98 (10.3%); £3,771,470.95 -> £3,381,637.98 (10.3%); £3,771,471.10 -> £3,381,637.98 (10.3%); £3,771,471.25 -> £3,381,637.98 (10.3%); £3,771,471.40 -> £3,381,637.98 (10.3%); £3,771,471.55 -> £3,381,637.99 (10.3%); £3,771,471.70 -> £3,381,637.98 (10.3%); £3,771,471.85 -> £3,381,637.98 (10.3%); £3,771,472.01 -> £3,381,638.02 (10.3%); £3,771,472.19 -> £3,381,638.07 (10.3%); £3,771,472.40 -> £3,381,638.12 (10.3%); £3,771,472.61 -> £3,381,638.17 (10.3%); £3,771,472.83 -> £3,381,638.22 (10.3%); £3,771,473.09 -> £3,381,638.26 (10.3%); £3,771,473.34 -> £3,381,638.30 (10.3%); £3,771,473.59 -> £3,381,638.33 (10.3%); £3,771,473.84 -> £3,381,638.33 (10.3%); £3,771,474.09 -> £3,381,638.33 (10.3%); £3,771,474.34 -> £3,381,638.32 (10.3%); £3,771,474.58 -> £3,381,638.32 (10.3%); £3,771,474.83 -> £3,381,638.32 (10.3%); £3,771,475.07 -> £3,381,638.32 (10.3%); £3,771,475.31 -> £3,381,638.32 (10.3%); £3,771,475.56 -> £3,381,638.32 (10.3%); £3,771,475.82 -> £3,381,638.32 (10.3%); £3,771,476.07 -> £3,381,638.32 (10.3%); £3,771,476.32 -> £3,381,638.35 (10.3%); £3,771,476.51 -> £3,381,638.41 (10.3%); £3,771,476.69 -> £3,381,638.48 (10.3%); £3,771,476.87 -> £3,381,638.54 (10.3%); £3,771,477.06 -> £3,381,638.61 (10.3%); £3,771,477.24 -> £3,381,638.67 (10.3%); £3,771,477.42 -> £3,381,638.76 (10.3%); £3,771,477.61 -> £3,381,638.84 (10.3%); £3,771,477.86 -> £3,381,638.81 (10.3%); £3,771,478.11 -> £3,381,638.79 (10.3%); £3,771,478.36 -> £3,381,638.76 (10.3%); £3,771,478.61 -> £3,381,638.74 (10.3%); £3,771,478.86 -> £3,381,638.74 (10.3%); £3,771,479.11 -> £3,381,638.73 (10.3%); £3,771,479.34 -> £3,381,638.73 (10.3%); £3,771,479.55 -> £3,381,638.72 (10.3%); £3,771,479.74 -> £3,381,638.72 (10.3%); £3,771,479.89 -> £3,381,638.72 (10.3%); £3,771,480.04 -> £3,381,638.72 (10.3%); £3,771,480.19 -> £3,381,638.72 (10.3%); £3,771,480.33 -> £3,381,638.72 (10.3%); £3,771,480.48 -> £3,381,638.73 (10.3%); £3,771,480.62 -> £3,381,638.73 (10.3%); £3,771,480.77 -> £3,381,638.73 (10.3%); £3,771,480.92 -> £3,381,638.73 (10.3%); £3,771,481.06 -> £3,381,638.73 (10.3%); £3,771,481.22 -> £3,381,638.73 (10.3%); £3,771,481.36 -> £3,381,638.74 (10.3%); £3,771,481.51 -> £3,381,638.73 (10.3%); £3,771,481.66 -> £3,381,638.73 (10.3%); £3,771,481.83 -> £3,381,638.77 (10.3%); £3,771,482.01 -> £3,381,638.82 (10.3%); £3,771,482.20 -> £3,381,638.87 (10.3%); £3,771,482.41 -> £3,381,638.92 (10.3%); £3,771,482.65 -> £3,381,638.97 (10.3%); £3,771,482.89 -> £3,381,639.01 (10.3%); £3,771,483.13 -> £3,381,639.05 (10.3%); £3,771,483.36 -> £3,381,639.08 (10.3%); £3,771,483.62 -> £3,381,639.08 (10.3%); £3,771,483.86 -> £3,381,639.08 (10.3%); £3,771,484.11 -> £3,381,639.08 (10.3%); £3,771,484.36 -> £3,381,639.07 (10.3%); £3,771,484.60 -> £3,381,639.07 (10.3%); £3,771,484.85 -> £3,381,639.07 (10.3%); £3,771,485.09 -> £3,381,639.07 (10.3%); £3,771,485.32 -> £3,381,639.07 (10.3%); £3,771,485.57 -> £3,381,639.07 (10.3%); £3,771,485.81 -> £3,381,639.07 (10.3%); £3,771,486.05 -> £3,381,639.10 (10.3%); £3,771,486.24 -> £3,381,639.16 (10.3%); £3,771,486.43 -> £3,381,639.22 (10.3%); £3,771,486.61 -> £3,381,639.29 (10.3%); £3,771,486.80 -> £3,381,639.36 (10.3%); £3,771,486.98 -> £3,381,639.42 (10.3%); £3,771,487.16 -> £3,381,639.50 (10.3%); £3,771,487.34 -> £3,381,639.58 (10.3%); £3,771,487.59 -> £3,381,639.56 (10.3%); £3,771,487.83 -> £3,381,639.53 (10.3%); £3,771,488.08 -> £3,381,639.51 (10.3%); £3,771,488.32 -> £3,381,639.49 (10.3%); £3,771,488.58 -> £3,381,639.48 (10.3%); £3,771,488.82 -> £3,381,639.48 (10.3%); £3,771,489.06 -> £3,381,639.47 (10.3%); £3,771,489.27 -> £3,381,639.47 (10.3%); £3,771,489.46 -> £3,381,639.46 (10.3%); £3,771,489.59 -> £3,381,639.46 (10.3%); £3,771,489.72 -> £3,381,639.46 (10.3%); £3,771,489.85 -> £3,381,639.46 (10.3%); £3,771,489.98 -> £3,381,639.47 (10.3%); £3,771,490.10 -> £3,381,639.47 (10.3%); £3,771,490.23 -> £3,381,639.47 (10.3%); £3,771,490.36 -> £3,381,639.47 (10.3%); £3,771,490.49 -> £3,381,639.47 (10.3%); £3,771,490.62 -> £3,381,639.47 (10.3%); £3,771,490.75 -> £3,381,639.48 (10.3%); £3,771,490.87 -> £3,381,639.48 (10.3%); £3,771,491.00 -> £3,381,639.48 (10.3%); £3,771,491.13 -> £3,381,639.47 (10.3%); £3,771,491.27 -> £3,381,639.47 (10.3%); £3,771,491.43 -> £3,381,639.47 (10.3%); £3,771,491.60 -> £3,381,639.46 (10.3%); £3,771,491.79 -> £3,381,639.45 (10.3%); £3,771,491.99 -> £3,381,639.44 (10.3%); £3,771,492.20 -> £3,381,639.43 (10.3%); £3,771,492.40 -> £3,381,639.43 (10.3%); £3,771,492.61 -> £3,381,639.42 (10.3%); £3,771,492.83 -> £3,381,639.42 (10.3%); £3,771,493.03 -> £3,381,639.42 (10.3%); £3,771,493.25 -> £3,381,639.41 (10.3%); £3,771,493.46 -> £3,381,639.41 (10.3%); £3,771,493.67 -> £3,381,639.40 (10.3%); £3,771,493.88 -> £3,381,639.40 (10.3%); £3,771,494.10 -> £3,381,639.40 (10.3%); £3,771,494.31 -> £3,381,639.39 (10.3%); £3,771,494.52 -> £3,381,639.39 (10.3%); £3,771,494.74 -> £3,381,639.39 (10.3%); £3,771,494.95 -> £3,381,639.39 (10.3%); £3,771,495.11 -> £3,381,639.37 (10.3%); £3,771,495.28 -> £3,381,639.36 (10.3%); £3,771,495.43 -> £3,381,639.34 (10.3%); £3,771,495.59 -> £3,381,639.32 (10.3%); £3,771,495.75 -> £3,381,639.30 (10.3%); £3,771,495.91 -> £3,381,639.27 (10.3%); £3,771,496.11 -> £3,381,639.25 (10.3%); £3,771,496.33 -> £3,381,639.22 (10.3%); £3,771,496.55 -> £3,381,639.20 (10.3%); £3,771,496.76 -> £3,381,639.18 (10.3%); £3,771,496.97 -> £3,381,639.16 (10.3%); £3,771,497.19 -> £3,381,639.15 (10.3%); £3,771,497.40 -> £3,381,639.14 (10.3%); £3,771,497.59 -> £3,381,639.14 (10.3%); £3,771,497.77 -> £3,381,639.13 (10.3%); £3,771,497.93 -> £3,381,639.13 (10.3%); £3,771,498.06 -> £3,381,639.13 (10.3%); £3,771,498.19 -> £3,381,639.13 (10.3%); £3,771,498.32 -> £3,381,639.13 (10.3%); £3,771,498.44 -> £3,381,639.13 (10.3%); £3,771,498.57 -> £3,381,639.13 (10.3%); £3,771,498.69 -> £3,381,639.13 (10.3%); £3,771,498.82 -> £3,381,639.13 (10.3%); £3,771,498.95 -> £3,381,639.13 (10.3%); £3,771,499.07 -> £3,381,639.14 (10.3%); £3,771,499.20 -> £3,381,639.14 (10.3%); £3,771,499.33 -> £3,381,639.14 (10.3%); £3,771,499.45 -> £3,381,639.14 (10.3%); £3,771,499.58 -> £3,381,639.14 (10.3%); £3,771,499.72 -> £3,381,639.14 (10.3%); £3,771,499.88 -> £3,381,639.14 (10.3%); £3,771,500.05 -> £3,381,639.13 (10.3%); £3,771,500.23 -> £3,381,639.12 (10.3%); £3,771,500.43 -> £3,381,639.11 (10.3%); £3,771,500.63 -> £3,381,639.10 (10.3%); £3,771,500.85 -> £3,381,639.10 (10.3%); £3,771,501.06 -> £3,381,639.09 (10.3%); £3,771,501.27 -> £3,381,639.08 (10.3%); £3,771,501.48 -> £3,381,639.07 (10.3%); £3,771,501.70 -> £3,381,639.06 (10.3%); £3,771,501.91 -> £3,381,639.05 (10.3%); £3,771,502.11 -> £3,381,639.04 (10.3%); £3,771,502.32 -> £3,381,639.03 (10.3%); £3,771,502.54 -> £3,381,639.03 (10.3%); £3,771,502.75 -> £3,381,639.02 (10.3%); £3,771,502.96 -> £3,381,639.02 (10.3%); £3,771,503.17 -> £3,381,639.01 (10.3%); £3,771,503.38 -> £3,381,639.01 (10.3%); £3,771,503.54 -> £3,381,639.00 (10.3%); £3,771,503.70 -> £3,381,638.98 (10.3%); £3,771,503.86 -> £3,381,638.96 (10.3%); £3,771,504.01 -> £3,381,638.94 (10.3%); £3,771,504.18 -> £3,381,638.92 (10.3%); £3,771,504.34 -> £3,381,638.89 (10.3%); £3,771,504.50 -> £3,381,638.86 (10.3%); £3,771,504.71 -> £3,381,638.83 (10.3%); £3,771,504.93 -> £3,381,638.81 (10.3%); £3,771,505.14 -> £3,381,638.79 (10.3%); £3,771,505.35 -> £3,381,638.77 (10.3%); £3,771,505.56 -> £3,381,638.76 (10.3%); £3,771,505.77 -> £3,381,638.75 (10.3%); £3,771,505.96 -> £3,381,638.75 (10.3%); £3,771,506.15 -> £3,381,638.74 (10.3%); £3,771,506.31 -> £3,381,638.74 (10.3%); £3,771,506.46 -> £3,381,638.74 (10.3%); £3,771,506.61 -> £3,381,638.74 (10.3%); £3,771,506.75 -> £3,381,638.74 (10.3%); £3,771,506.90 -> £3,381,638.75 (10.3%); £3,771,507.05 -> £3,381,638.75 (10.3%); £3,771,507.19 -> £3,381,638.75 (10.3%); £3,771,507.33 -> £3,381,638.75 (10.3%); £3,771,507.48 -> £3,381,638.75 (10.3%); £3,771,507.63 -> £3,381,638.76 (10.3%); £3,771,507.78 -> £3,381,638.76 (10.3%); £3,771,507.92 -> £3,381,638.76 (10.3%); £3,771,508.06 -> £3,381,638.76 (10.3%); £3,771,508.20 -> £3,381,638.75 (10.3%); £3,771,508.36 -> £3,381,638.79 (10.3%); £3,771,508.54 -> £3,381,638.85 (10.3%); £3,771,508.72 -> £3,381,638.90 (10.3%); £3,771,508.93 -> £3,381,638.95 (10.3%); £3,771,509.16 -> £3,381,638.99 (10.3%); £3,771,509.40 -> £3,381,639.04 (10.3%); £3,771,509.63 -> £3,381,639.07 (10.3%); £3,771,509.88 -> £3,381,639.11 (10.3%); £3,771,510.12 -> £3,381,639.11 (10.3%); £3,771,510.37 -> £3,381,639.10 (10.3%); £3,771,510.62 -> £3,381,639.10 (10.3%); £3,771,510.85 -> £3,381,639.10 (10.3%); £3,771,511.10 -> £3,381,639.10 (10.3%); £3,771,511.34 -> £3,381,639.10 (10.3%); £3,771,511.58 -> £3,381,639.10 (10.3%); £3,771,511.82 -> £3,381,639.10 (10.3%); £3,771,512.07 -> £3,381,639.10 (10.3%); £3,771,512.31 -> £3,381,639.10 (10.3%); £3,771,512.55 -> £3,381,639.13 (10.3%); £3,771,512.73 -> £3,381,639.19 (10.3%); £3,771,512.92 -> £3,381,639.25 (10.3%); £3,771,513.10 -> £3,381,639.32 (10.3%); £3,771,513.28 -> £3,381,639.39 (10.3%); £3,771,513.47 -> £3,381,639.45 (10.3%); £3,771,513.64 -> £3,381,639.54 (10.3%); £3,771,513.82 -> £3,381,639.62 (10.3%); £3,771,514.06 -> £3,381,639.59 (10.3%); £3,771,514.30 -> £3,381,639.57 (10.3%); £3,771,514.53 -> £3,381,639.54 (10.3%); £3,771,514.78 -> £3,381,639.52 (10.3%); £3,771,515.02 -> £3,381,639.52 (10.3%); £3,771,515.26 -> £3,381,639.51 (10.3%); £3,771,515.49 -> £3,381,639.51 (10.3%); £3,771,515.69 -> £3,381,639.50 (10.3%); £3,771,515.88 -> £3,381,639.50 (10.3%); £3,771,516.03 -> £3,381,639.50 (10.3%); £3,771,516.17 -> £3,381,639.50 (10.3%); £3,771,516.31 -> £3,381,639.50 (10.3%); £3,771,516.46 -> £3,381,639.50 (10.3%); £3,771,516.60 -> £3,381,639.51 (10.3%); £3,771,516.74 -> £3,381,639.51 (10.3%); £3,771,516.88 -> £3,381,639.51 (10.3%); £3,771,517.02 -> £3,381,639.51 (10.3%); £3,771,517.16 -> £3,381,639.51 (10.3%); £3,771,517.31 -> £3,381,639.52 (10.3%); £3,771,517.45 -> £3,381,639.52 (10.3%); £3,771,517.60 -> £3,381,639.51 (10.3%); £3,771,517.74 -> £3,381,639.51 (10.3%); £3,771,517.90 -> £3,381,639.55 (10.3%); £3,771,518.08 -> £3,381,639.60 (10.3%); £3,771,518.27 -> £3,381,639.66 (10.3%); £3,771,518.48 -> £3,381,639.70 (10.3%); £3,771,518.71 -> £3,381,639.75 (10.3%); £3,771,518.95 -> £3,381,639.79 (10.3%); £3,771,519.20 -> £3,381,639.83 (10.3%); £3,771,519.43 -> £3,381,639.86 (10.3%); £3,771,519.66 -> £3,381,639.86 (10.3%); £3,771,519.90 -> £3,381,639.86 (10.3%); £3,771,520.14 -> £3,381,639.86 (10.3%); £3,771,520.38 -> £3,381,639.86 (10.3%); £3,771,520.62 -> £3,381,639.85 (10.3%); £3,771,520.85 -> £3,381,639.85 (10.3%); £3,771,521.09 -> £3,381,639.85 (10.3%); £3,771,521.32 -> £3,381,639.85 (10.3%); £3,771,521.56 -> £3,381,639.85 (10.3%); £3,771,521.79 -> £3,381,639.85 (10.3%); £3,771,522.03 -> £3,381,639.89 (10.3%); £3,771,522.22 -> £3,381,639.94 (10.3%); £3,771,522.40 -> £3,381,640.01 (10.3%); £3,771,522.59 -> £3,381,640.08 (10.3%); £3,771,522.84 -> £3,381,640.15 (10.3%); £3,771,523.08 -> £3,381,640.21 (10.3%); £3,771,523.33 -> £3,381,640.30 (10.3%); £3,771,523.51 -> £3,381,640.38 (10.3%); £3,771,523.75 -> £3,381,640.35 (10.3%); £3,771,523.98 -> £3,381,640.33 (10.3%); £3,771,524.23 -> £3,381,640.30 (10.3%); £3,771,524.47 -> £3,381,640.28 (10.3%); £3,771,524.71 -> £3,381,640.27 (10.3%); £3,771,524.95 -> £3,381,640.27 (10.3%); £3,771,525.18 -> £3,381,640.26 (10.3%); £3,771,525.37 -> £3,381,640.26 (10.3%); £3,771,525.56 -> £3,381,640.26 (10.3%); £3,771,525.70 -> £3,381,640.26 (10.3%); £3,771,525.84 -> £3,381,640.26 (10.3%); £3,771,525.98 -> £3,381,640.26 (10.3%); £3,771,526.12 -> £3,381,640.26 (10.3%); £3,771,526.26 -> £3,381,640.27 (10.3%); £3,771,526.40 -> £3,381,640.27 (10.3%); £3,771,526.54 -> £3,381,640.27 (10.3%); £3,771,526.69 -> £3,381,640.27 (10.3%); £3,771,526.83 -> £3,381,640.27 (10.3%); £3,771,526.97 -> £3,381,640.28 (10.3%); £3,771,527.11 -> £3,381,640.28 (10.3%); £3,771,527.25 -> £3,381,640.27 (10.3%); £3,771,527.39 -> £3,381,640.27 (10.3%); £3,771,527.55 -> £3,381,640.31 (10.3%); £3,771,527.73 -> £3,381,640.37 (10.3%); £3,771,527.91 -> £3,381,640.42 (10.3%); £3,771,528.12 -> £3,381,640.47 (10.3%); £3,771,528.33 -> £3,381,640.51 (10.3%); £3,771,528.57 -> £3,381,640.56 (10.3%); £3,771,528.81 -> £3,381,640.59 (10.3%); £3,771,529.04 -> £3,381,640.63 (10.3%); £3,771,529.29 -> £3,381,640.63 (10.3%); £3,771,529.52 -> £3,381,640.63 (10.3%); £3,771,529.76 -> £3,381,640.62 (10.3%); £3,771,530.00 -> £3,381,640.62 (10.3%); £3,771,530.23 -> £3,381,640.62 (10.3%); £3,771,530.47 -> £3,381,640.62 (10.3%); £3,771,530.71 -> £3,381,640.62 (10.3%); £3,771,530.95 -> £3,381,640.62 (10.3%); £3,771,531.19 -> £3,381,640.62 (10.3%); £3,771,531.42 -> £3,381,640.62 (10.3%); £3,771,531.66 -> £3,381,640.65 (10.3%); £3,771,531.83 -> £3,381,640.71 (10.3%); £3,771,532.01 -> £3,381,640.78 (10.3%); £3,771,532.25 -> £3,381,640.84 (10.3%); £3,771,532.49 -> £3,381,640.91 (10.3%); £3,771,532.73 -> £3,381,640.98 (10.3%); £3,771,532.97 -> £3,381,641.06 (10.3%); £3,771,533.21 -> £3,381,641.14 (10.3%); £3,771,533.45 -> £3,381,641.12 (10.3%); £3,771,533.69 -> £3,381,641.10 (10.3%); £3,771,533.93 -> £3,381,641.07 (10.3%); £3,771,534.17 -> £3,381,641.05 (10.3%); £3,771,534.39 -> £3,381,641.04 (10.3%); £3,771,534.63 -> £3,381,641.04 (10.3%); £3,771,534.84 -> £3,381,641.03 (10.3%); £3,771,535.04 -> £3,381,641.03 (10.3%); £3,771,535.21 -> £3,381,641.03 (10.3%); £3,771,535.35 -> £3,381,641.03 (10.3%); £3,771,535.50 -> £3,381,641.03 (10.3%); £3,771,535.64 -> £3,381,641.03 (10.3%); £3,771,535.78 -> £3,381,641.03 (10.3%); £3,771,535.92 -> £3,381,641.03 (10.3%); £3,771,536.06 -> £3,381,641.04 (10.3%); £3,771,536.20 -> £3,381,641.04 (10.3%); £3,771,536.35 -> £3,381,641.04 (10.3%); £3,771,536.49 -> £3,381,641.04 (10.3%); £3,771,536.64 -> £3,381,641.04 (10.3%); £3,771,536.78 -> £3,381,641.04 (10.3%); £3,771,536.93 -> £3,381,641.04 (10.3%); £3,771,537.07 -> £3,381,641.03 (10.3%); £3,771,537.22 -> £3,381,641.08 (10.3%); £3,771,537.40 -> £3,381,641.13 (10.3%); £3,771,537.59 -> £3,381,641.18 (10.3%); £3,771,537.79 -> £3,381,641.23 (10.3%); £3,771,538.01 -> £3,381,641.27 (10.3%); £3,771,538.25 -> £3,381,641.32 (10.3%); £3,771,538.48 -> £3,381,641.35 (10.3%); £3,771,538.71 -> £3,381,641.39 (10.3%); £3,771,538.94 -> £3,381,641.39 (10.3%); £3,771,539.17 -> £3,381,641.39 (10.3%); £3,771,539.40 -> £3,381,641.39 (10.3%); £3,771,539.65 -> £3,381,641.38 (10.3%); £3,771,539.89 -> £3,381,641.38 (10.3%); £3,771,540.12 -> £3,381,641.38 (10.3%); £3,771,540.36 -> £3,381,641.38 (10.3%); £3,771,540.59 -> £3,381,641.38 (10.3%); £3,771,540.83 -> £3,381,641.38 (10.3%); £3,771,541.06 -> £3,381,641.38 (10.3%); £3,771,541.30 -> £3,381,641.41 (10.3%); £3,771,541.48 -> £3,381,641.47 (10.3%); £3,771,541.66 -> £3,381,641.54 (10.3%); £3,771,541.84 -> £3,381,641.60 (10.3%); £3,771,542.01 -> £3,381,641.67 (10.3%); £3,771,542.19 -> £3,381,641.74 (10.3%); £3,771,542.36 -> £3,381,641.82 (10.3%); £3,771,542.54 -> £3,381,641.90 (10.3%); £3,771,542.77 -> £3,381,641.88 (10.3%); £3,771,543.00 -> £3,381,641.85 (10.3%); £3,771,543.24 -> £3,381,641.83 (10.3%); £3,771,543.46 -> £3,381,641.81 (10.3%); £3,771,543.71 -> £3,381,641.80 (10.3%); £3,771,543.94 -> £3,381,641.80 (10.3%); £3,771,544.17 -> £3,381,641.79 (10.3%); £3,771,544.37 -> £3,381,641.79 (10.3%); £3,771,544.56 -> £3,381,641.79 (10.3%); £3,771,544.70 -> £3,381,641.79 (10.3%); £3,771,544.85 -> £3,381,641.79 (10.3%); £3,771,544.99 -> £3,381,641.79 (10.3%); £3,771,545.14 -> £3,381,641.79 (10.3%); £3,771,545.28 -> £3,381,641.79 (10.3%); £3,771,545.42 -> £3,381,641.80 (10.3%); £3,771,545.56 -> £3,381,641.80 (10.3%); £3,771,545.71 -> £3,381,641.80 (10.3%); £3,771,545.85 -> £3,381,641.80 (10.3%); £3,771,545.99 -> £3,381,641.80 (10.3%); £3,771,546.14 -> £3,381,641.80 (10.3%); £3,771,546.28 -> £3,381,641.80 (10.3%); £3,771,546.42 -> £3,381,641.79 (10.3%); £3,771,546.59 -> £3,381,641.84 (10.3%); £3,771,546.76 -> £3,381,641.89 (10.3%); £3,771,546.95 -> £3,381,641.94 (10.3%); £3,771,547.16 -> £3,381,641.99 (10.3%); £3,771,547.38 -> £3,381,642.04 (10.3%); £3,771,547.61 -> £3,381,642.08 (10.3%); £3,771,547.85 -> £3,381,642.12 (10.3%); £3,771,548.08 -> £3,381,642.15 (10.3%); £3,771,548.32 -> £3,381,642.15 (10.3%); £3,771,548.56 -> £3,381,642.15 (10.3%); £3,771,548.80 -> £3,381,642.15 (10.3%); £3,771,549.04 -> £3,381,642.15 (10.3%); £3,771,549.28 -> £3,381,642.15 (10.3%); £3,771,549.52 -> £3,381,642.15 (10.3%); £3,771,549.75 -> £3,381,642.15 (10.3%); £3,771,549.98 -> £3,381,642.14 (10.3%); £3,771,550.22 -> £3,381,642.14 (10.3%); £3,771,550.47 -> £3,381,642.14 (10.3%); £3,771,550.70 -> £3,381,642.18 (10.3%); £3,771,550.94 -> £3,381,642.24 (10.3%); £3,771,551.11 -> £3,381,642.30 (10.3%); £3,771,551.29 -> £3,381,642.37 (10.3%); £3,771,551.47 -> £3,381,642.44 (10.3%); £3,771,551.65 -> £3,381,642.50 (10.3%); £3,771,551.89 -> £3,381,642.59 (10.3%); £3,771,552.14 -> £3,381,642.67 (10.3%); £3,771,552.38 -> £3,381,642.64 (10.3%); £3,771,552.62 -> £3,381,642.62 (10.3%); £3,771,552.87 -> £3,381,642.60 (10.3%); £3,771,553.11 -> £3,381,642.58 (10.3%); £3,771,553.35 -> £3,381,642.57 (10.3%); £3,771,553.59 -> £3,381,642.56 (10.3%); £3,771,553.81 -> £3,381,642.56 (10.3%); £3,771,554.01 -> £3,381,642.55 (10.3%); £3,771,554.21 -> £3,381,642.55 (10.3%); £3,771,554.33 -> £3,381,642.55 (10.3%); £3,771,554.46 -> £3,381,642.55 (10.3%); £3,771,554.59 -> £3,381,642.55 (10.3%); £3,771,554.72 -> £3,381,642.55 (10.3%); £3,771,554.85 -> £3,381,642.56 (10.3%); £3,771,554.98 -> £3,381,642.56 (10.3%); £3,771,555.10 -> £3,381,642.56 (10.3%); £3,771,555.23 -> £3,381,642.56 (10.3%); £3,771,555.36 -> £3,381,642.56 (10.3%); £3,771,555.48 -> £3,381,642.57 (10.3%); £3,771,555.61 -> £3,381,642.57 (10.3%); £3,771,555.75 -> £3,381,642.57 (10.3%); £3,771,555.88 -> £3,381,642.56 (10.3%); £3,771,556.02 -> £3,381,642.56 (10.3%); £3,771,556.18 -> £3,381,642.55 (10.3%); £3,771,556.35 -> £3,381,642.55 (10.3%); £3,771,556.54 -> £3,381,642.54 (10.3%); £3,771,556.74 -> £3,381,642.53 (10.3%); £3,771,556.95 -> £3,381,642.52 (10.3%); £3,771,557.17 -> £3,381,642.52 (10.3%); £3,771,557.38 -> £3,381,642.51 (10.3%); £3,771,557.59 -> £3,381,642.51 (10.3%); £3,771,557.80 -> £3,381,642.51 (10.3%); £3,771,558.02 -> £3,381,642.50 (10.3%); £3,771,558.24 -> £3,381,642.50 (10.3%); £3,771,558.45 -> £3,381,642.49 (10.3%); £3,771,558.66 -> £3,381,642.49 (10.3%); £3,771,558.88 -> £3,381,642.48 (10.3%); £3,771,559.09 -> £3,381,642.48 (10.3%); £3,771,559.31 -> £3,381,642.48 (10.3%); £3,771,559.52 -> £3,381,642.48 (10.3%); £3,771,559.73 -> £3,381,642.48 (10.3%); £3,771,559.90 -> £3,381,642.46 (10.3%); £3,771,560.06 -> £3,381,642.45 (10.3%); £3,771,560.22 -> £3,381,642.43 (10.3%); £3,771,560.39 -> £3,381,642.41 (10.3%); £3,771,560.55 -> £3,381,642.39 (10.3%); £3,771,560.71 -> £3,381,642.36 (10.3%); £3,771,560.88 -> £3,381,642.34 (10.3%); £3,771,561.09 -> £3,381,642.31 (10.3%); £3,771,561.30 -> £3,381,642.29 (10.3%); £3,771,561.51 -> £3,381,642.27 (10.3%); £3,771,561.73 -> £3,381,642.25 (10.3%); £3,771,561.94 -> £3,381,642.24 (10.3%); £3,771,562.16 -> £3,381,642.23 (10.3%); £3,771,562.36 -> £3,381,642.23 (10.3%); £3,771,562.54 -> £3,381,642.22 (10.3%); £3,771,562.71 -> £3,381,642.22 (10.3%); £3,771,562.84 -> £3,381,642.22 (10.3%); £3,771,562.97 -> £3,381,642.22 (10.3%); £3,771,563.10 -> £3,381,642.22 (10.3%); £3,771,563.23 -> £3,381,642.22 (10.3%); £3,771,563.36 -> £3,381,642.22 (10.3%); £3,771,563.49 -> £3,381,642.22 (10.3%); £3,771,563.61 -> £3,381,642.22 (10.3%); £3,771,563.74 -> £3,381,642.22 (10.3%); £3,771,563.86 -> £3,381,642.23 (10.3%); £3,771,563.99 -> £3,381,642.23 (10.3%); £3,771,564.12 -> £3,381,642.23 (10.3%); £3,771,564.25 -> £3,381,642.23 (10.3%); £3,771,564.38 -> £3,381,642.23 (10.3%); £3,771,564.53 -> £3,381,642.23 (10.3%); £3,771,564.69 -> £3,381,642.23 (10.3%); £3,771,564.86 -> £3,381,642.22 (10.3%); £3,771,565.04 -> £3,381,642.22 (10.3%); £3,771,565.24 -> £3,381,642.21 (10.3%); £3,771,565.46 -> £3,381,642.20 (10.3%); £3,771,565.68 -> £3,381,642.19 (10.3%); £3,771,565.90 -> £3,381,642.18 (10.3%); £3,771,566.11 -> £3,381,642.17 (10.3%); £3,771,566.32 -> £3,381,642.16 (10.3%); £3,771,566.53 -> £3,381,642.15 (10.3%); £3,771,566.75 -> £3,381,642.14 (10.3%); £3,771,566.97 -> £3,381,642.13 (10.3%); £3,771,567.18 -> £3,381,642.13 (10.3%); £3,771,567.40 -> £3,381,642.12 (10.3%); £3,771,567.61 -> £3,381,642.12 (10.3%); £3,771,567.82 -> £3,381,642.11 (10.3%); £3,771,568.05 -> £3,381,642.11 (10.3%); £3,771,568.27 -> £3,381,642.10 (10.3%); £3,771,568.43 -> £3,381,642.09 (10.3%); £3,771,568.58 -> £3,381,642.07 (10.3%); £3,771,568.74 -> £3,381,642.05 (10.3%); £3,771,568.90 -> £3,381,642.03 (10.3%); £3,771,569.06 -> £3,381,642.02 (10.3%); £3,771,569.22 -> £3,381,641.99 (10.3%); £3,771,569.38 -> £3,381,641.96 (10.3%); £3,771,569.60 -> £3,381,641.93 (10.3%); £3,771,569.81 -> £3,381,641.91 (10.3%); £3,771,570.03 -> £3,381,641.88 (10.3%); £3,771,570.24 -> £3,381,641.86 (10.3%); £3,771,570.45 -> £3,381,641.85 (10.3%); £3,771,570.67 -> £3,381,641.85 (10.3%); £3,771,570.86 -> £3,381,641.84 (10.3%); £3,771,571.04 -> £3,381,641.84 (10.3%); £3,771,571.20 -> £3,381,641.84 (10.3%); £3,771,571.35 -> £3,381,641.84 (10.3%); £3,771,571.50 -> £3,381,641.84 (10.3%); £3,771,571.65 -> £3,381,641.84 (10.3%); £3,771,571.79 -> £3,381,641.84 (10.3%); £3,771,571.94 -> £3,381,641.84 (10.3%); £3,771,572.09 -> £3,381,641.85 (10.3%); £3,771,572.23 -> £3,381,641.85 (10.3%); £3,771,572.38 -> £3,381,641.85 (10.3%); £3,771,572.52 -> £3,381,641.85 (10.3%); £3,771,572.67 -> £3,381,641.85 (10.3%); £3,771,572.81 -> £3,381,641.85 (10.3%); £3,771,572.96 -> £3,381,641.85 (10.3%); £3,771,573.11 -> £3,381,641.84 (10.3%); £3,771,573.27 -> £3,381,641.89 (10.3%); £3,771,573.45 -> £3,381,641.94 (10.3%); £3,771,573.64 -> £3,381,641.99 (10.3%); £3,771,573.86 -> £3,381,642.04 (10.3%); £3,771,574.09 -> £3,381,642.09 (10.3%); £3,771,574.34 -> £3,381,642.13 (10.3%); £3,771,574.59 -> £3,381,642.17 (10.3%); £3,771,574.84 -> £3,381,642.20 (10.3%); £3,771,575.09 -> £3,381,642.20 (10.3%); £3,771,575.33 -> £3,381,642.20 (10.3%); £3,771,575.58 -> £3,381,642.20 (10.3%); £3,771,575.83 -> £3,381,642.20 (10.3%); £3,771,576.08 -> £3,381,642.20 (10.3%); £3,771,576.33 -> £3,381,642.20 (10.3%); £3,771,576.58 -> £3,381,642.20 (10.3%); £3,771,576.83 -> £3,381,642.19 (10.3%); £3,771,577.08 -> £3,381,642.19 (10.3%); £3,771,577.32 -> £3,381,642.20 (10.3%); £3,771,577.57 -> £3,381,642.23 (10.3%); £3,771,577.82 -> £3,381,642.29 (10.3%); £3,771,578.00 -> £3,381,642.35 (10.3%); £3,771,578.18 -> £3,381,642.42 (10.3%); £3,771,578.37 -> £3,381,642.49 (10.3%); £3,771,578.55 -> £3,381,642.55 (10.3%); £3,771,578.73 -> £3,381,642.64 (10.3%); £3,771,578.91 -> £3,381,642.72 (10.3%); £3,771,579.15 -> £3,381,642.70 (10.3%); £3,771,579.40 -> £3,381,642.67 (10.3%); £3,771,579.65 -> £3,381,642.65 (10.3%); £3,771,579.90 -> £3,381,642.63 (10.3%); £3,771,580.14 -> £3,381,642.62 (10.3%); £3,771,580.38 -> £3,381,642.62 (10.3%); £3,771,580.61 -> £3,381,642.61 (10.3%); £3,771,580.82 -> £3,381,642.61 (10.3%); £3,771,581.01 -> £3,381,642.61 (10.3%); £3,771,581.16 -> £3,381,642.61 (10.3%); £3,771,581.31 -> £3,381,642.61 (10.3%); £3,771,581.45 -> £3,381,642.61 (10.3%); £3,771,581.60 -> £3,381,642.61 (10.3%); £3,771,581.75 -> £3,381,642.62 (10.3%); £3,771,581.90 -> £3,381,642.62 (10.3%); £3,771,582.05 -> £3,381,642.62 (10.3%); £3,771,582.19 -> £3,381,642.62 (10.3%); £3,771,582.34 -> £3,381,642.63 (10.3%); £3,771,582.49 -> £3,381,642.63 (10.3%); £3,771,582.64 -> £3,381,642.63 (10.3%); £3,771,582.79 -> £3,381,642.63 (10.3%); £3,771,582.93 -> £3,381,642.62 (10.3%); £3,771,583.10 -> £3,381,642.67 (10.3%); £3,771,583.28 -> £3,381,642.72 (10.3%); £3,771,583.48 -> £3,381,642.77 (10.3%); £3,771,583.70 -> £3,381,642.82 (10.3%); £3,771,583.93 -> £3,381,642.86 (10.3%); £3,771,584.17 -> £3,381,642.91 (10.3%); £3,771,584.42 -> £3,381,642.95 (10.3%); £3,771,584.67 -> £3,381,642.98 (10.3%); £3,771,584.91 -> £3,381,642.98 (10.3%); £3,771,585.16 -> £3,381,642.98 (10.3%); £3,771,585.41 -> £3,381,642.98 (10.3%); £3,771,585.65 -> £3,381,642.98 (10.3%); £3,771,585.90 -> £3,381,642.97 (10.3%); £3,771,586.15 -> £3,381,642.97 (10.3%); £3,771,586.39 -> £3,381,642.97 (10.3%); £3,771,586.63 -> £3,381,642.97 (10.3%); £3,771,586.88 -> £3,381,642.97 (10.3%); £3,771,587.13 -> £3,381,642.97 (10.3%); £3,771,587.37 -> £3,381,643.01 (10.3%); £3,771,587.56 -> £3,381,643.07 (10.3%); £3,771,587.74 -> £3,381,643.13 (10.3%); £3,771,588.00 -> £3,381,643.20 (10.3%); £3,771,588.25 -> £3,381,643.27 (10.3%); £3,771,588.49 -> £3,381,643.34 (10.3%); £3,771,588.74 -> £3,381,643.42 (10.3%); £3,771,588.92 -> £3,381,643.50 (10.3%); £3,771,589.18 -> £3,381,643.48 (10.3%); £3,771,589.42 -> £3,381,643.45 (10.3%); £3,771,589.67 -> £3,381,643.43 (10.3%); £3,771,589.93 -> £3,381,643.41 (10.3%); £3,771,590.17 -> £3,381,643.40 (10.3%); £3,771,590.42 -> £3,381,643.40 (10.3%); £3,771,590.65 -> £3,381,643.39 (10.3%); £3,771,590.86 -> £3,381,643.39 (10.3%); £3,771,591.05 -> £3,381,643.39 (10.3%); £3,771,591.20 -> £3,381,643.39 (10.3%); £3,771,591.34 -> £3,381,643.39 (10.3%); £3,771,591.49 -> £3,381,643.39 (10.3%); £3,771,591.65 -> £3,381,643.39 (10.3%); £3,771,591.79 -> £3,381,643.40 (10.3%); £3,771,591.94 -> £3,381,643.40 (10.3%); £3,771,592.09 -> £3,381,643.40 (10.3%); £3,771,592.23 -> £3,381,643.40 (10.3%); £3,771,592.38 -> £3,381,643.41 (10.3%); £3,771,592.53 -> £3,381,643.41 (10.3%); £3,771,592.69 -> £3,381,643.41 (10.3%); £3,771,592.84 -> £3,381,643.41 (10.3%); £3,771,592.99 -> £3,381,643.40 (10.3%); £3,771,593.16 -> £3,381,643.44 (10.3%); £3,771,593.35 -> £3,381,643.50 (10.3%); £3,771,593.54 -> £3,381,643.55 (10.3%); £3,771,593.76 -> £3,381,643.60 (10.3%); £3,771,593.99 -> £3,381,643.64 (10.3%); £3,771,594.24 -> £3,381,643.69 (10.3%); £3,771,594.49 -> £3,381,643.72 (10.3%); £3,771,594.74 -> £3,381,643.76 (10.3%); £3,771,594.99 -> £3,381,643.76 (10.3%); £3,771,595.25 -> £3,381,643.76 (10.3%); £3,771,595.49 -> £3,381,643.76 (10.3%); £3,771,595.75 -> £3,381,643.75 (10.3%); £3,771,595.99 -> £3,381,643.75 (10.3%); £3,771,596.25 -> £3,381,643.75 (10.3%); £3,771,596.51 -> £3,381,643.75 (10.3%); £3,771,596.77 -> £3,381,643.75 (10.3%); £3,771,597.02 -> £3,381,643.75 (10.3%); £3,771,597.27 -> £3,381,643.75 (10.3%); £3,771,597.53 -> £3,381,643.79 (10.3%); £3,771,597.77 -> £3,381,643.85 (10.3%); £3,771,597.96 -> £3,381,643.91 (10.3%); £3,771,598.14 -> £3,381,643.98 (10.3%); £3,771,598.39 -> £3,381,644.05 (10.3%); £3,771,598.65 -> £3,381,644.12 (10.3%); £3,771,598.90 -> £3,381,644.20 (10.3%); £3,771,599.09 -> £3,381,644.28 (10.3%); £3,771,599.35 -> £3,381,644.26 (10.3%); £3,771,599.60 -> £3,381,644.24 (10.3%); £3,771,599.85 -> £3,381,644.21 (10.3%); £3,771,600.10 -> £3,381,644.19 (10.3%); £3,771,600.36 -> £3,381,644.19 (10.3%); £3,771,600.61 -> £3,381,644.18 (10.3%); £3,771,600.84 -> £3,381,644.17 (10.3%); £3,771,601.06 -> £3,381,644.17 (10.3%); £3,771,601.25 -> £3,381,644.17 (10.3%); £3,771,601.41 -> £3,381,644.17 (10.3%); £3,771,601.56 -> £3,381,644.17 (10.3%); £3,771,601.72 -> £3,381,644.17 (10.3%); £3,771,601.87 -> £3,381,644.17 (10.3%); £3,771,602.03 -> £3,381,644.18 (10.3%); £3,771,602.18 -> £3,381,644.18 (10.3%); £3,771,602.34 -> £3,381,644.18 (10.3%); £3,771,602.49 -> £3,381,644.18 (10.3%); £3,771,602.65 -> £3,381,644.19 (10.3%); £3,771,602.80 -> £3,381,644.19 (10.3%); £3,771,602.95 -> £3,381,644.19 (10.3%); £3,771,603.10 -> £3,381,644.18 (10.3%); £3,771,603.26 -> £3,381,644.18 (10.3%); £3,771,603.43 -> £3,381,644.22 (10.3%); £3,771,603.62 -> £3,381,644.28 (10.3%); £3,771,603.82 -> £3,381,644.33 (10.3%); £3,771,604.04 -> £3,381,644.38 (10.3%); £3,771,604.27 -> £3,381,644.42 (10.3%); £3,771,604.52 -> £3,381,644.47 (10.3%); £3,771,604.78 -> £3,381,644.50 (10.3%); £3,771,605.04 -> £3,381,644.54 (10.3%); £3,771,605.29 -> £3,381,644.54 (10.3%); £3,771,605.54 -> £3,381,644.54 (10.3%); £3,771,605.79 -> £3,381,644.53 (10.3%); £3,771,606.05 -> £3,381,644.53 (10.3%); £3,771,606.32 -> £3,381,644.53 (10.3%); £3,771,606.56 -> £3,381,644.53 (10.3%); £3,771,606.83 -> £3,381,644.53 (10.3%); £3,771,607.08 -> £3,381,644.53 (10.3%); £3,771,607.33 -> £3,381,644.53 (10.3%); £3,771,607.59 -> £3,381,644.53 (10.3%); £3,771,607.85 -> £3,381,644.56 (10.3%); £3,771,608.04 -> £3,381,644.62 (10.3%); £3,771,608.23 -> £3,381,644.69 (10.3%); £3,771,608.42 -> £3,381,644.75 (10.3%); £3,771,608.61 -> £3,381,644.82 (10.3%); £3,771,608.86 -> £3,381,644.89 (10.3%); £3,771,609.11 -> £3,381,644.97 (10.3%); £3,771,609.31 -> £3,381,645.05 (10.3%); £3,771,609.57 -> £3,381,645.03 (10.3%); £3,771,609.83 -> £3,381,645.00 (10.3%); £3,771,610.09 -> £3,381,644.98 (10.3%); £3,771,610.34 -> £3,381,644.96 (10.3%); £3,771,610.60 -> £3,381,644.95 (10.3%); £3,771,610.85 -> £3,381,644.95 (10.3%); £3,771,611.09 -> £3,381,644.94 (10.3%); £3,771,611.30 -> £3,381,644.94 (10.3%); £3,771,611.51 -> £3,381,644.94 (10.3%); £3,771,611.66 -> £3,381,644.94 (10.3%); £3,771,611.81 -> £3,381,644.94 (10.3%); £3,771,611.96 -> £3,381,644.94 (10.3%); £3,771,612.11 -> £3,381,644.94 (10.3%); £3,771,612.26 -> £3,381,644.94 (10.3%); £3,771,612.42 -> £3,381,644.95 (10.3%); £3,771,612.57 -> £3,381,644.95 (10.3%); £3,771,612.73 -> £3,381,644.95 (10.3%); £3,771,612.88 -> £3,381,644.95 (10.3%); £3,771,613.03 -> £3,381,644.95 (10.3%); £3,771,613.18 -> £3,381,644.96 (10.3%); £3,771,613.34 -> £3,381,644.95 (10.3%); £3,771,613.50 -> £3,381,644.95 (10.3%); £3,771,613.67 -> £3,381,644.99 (10.3%); £3,771,613.86 -> £3,381,645.04 (10.3%); £3,771,614.06 -> £3,381,645.10 (10.3%); £3,771,614.28 -> £3,381,645.14 (10.3%); £3,771,614.52 -> £3,381,645.19 (10.3%); £3,771,614.78 -> £3,381,645.23 (10.3%); £3,771,615.05 -> £3,381,645.27 (10.3%); £3,771,615.31 -> £3,381,645.31 (10.3%); £3,771,615.57 -> £3,381,645.31 (10.3%); £3,771,615.83 -> £3,381,645.31 (10.3%); £3,771,616.08 -> £3,381,645.31 (10.3%); £3,771,616.33 -> £3,381,645.31 (10.3%); £3,771,616.58 -> £3,381,645.31 (10.3%); £3,771,616.83 -> £3,381,645.31 (10.3%); £3,771,617.10 -> £3,381,645.31 (10.3%); £3,771,617.36 -> £3,381,645.30 (10.3%); £3,771,617.61 -> £3,381,645.30 (10.3%); £3,771,617.86 -> £3,381,645.30 (10.3%); £3,771,618.11 -> £3,381,645.34 (10.3%); £3,771,618.31 -> £3,381,645.40 (10.3%); £3,771,618.50 -> £3,381,645.46 (10.3%); £3,771,618.70 -> £3,381,645.53 (10.3%); £3,771,618.89 -> £3,381,645.60 (10.3%); £3,771,619.09 -> £3,381,645.66 (10.3%); £3,771,619.28 -> £3,381,645.75 (10.3%); £3,771,619.48 -> £3,381,645.83 (10.3%); £3,771,619.74 -> £3,381,645.81 (10.3%); £3,771,619.99 -> £3,381,645.78 (10.3%); £3,771,620.25 -> £3,381,645.76 (10.3%); £3,771,620.51 -> £3,381,645.74 (10.3%); £3,771,620.76 -> £3,381,645.73 (10.3%); £3,771,621.01 -> £3,381,645.73 (10.3%); £3,771,621.25 -> £3,381,645.72 (10.3%); £3,771,621.46 -> £3,381,645.72 (10.3%); £3,771,621.67 -> £3,381,645.72 (10.3%); £3,771,621.81 -> £3,381,645.72 (10.3%); £3,771,621.94 -> £3,381,645.72 (10.3%); £3,771,622.08 -> £3,381,645.72 (10.3%); £3,771,622.22 -> £3,381,645.72 (10.3%); £3,771,622.37 -> £3,381,645.72 (10.3%); £3,771,622.51 -> £3,381,645.72 (10.3%); £3,771,622.65 -> £3,381,645.73 (10.3%); £3,771,622.79 -> £3,381,645.73 (10.3%); £3,771,622.93 -> £3,381,645.73 (10.3%); £3,771,623.06 -> £3,381,645.73 (10.3%); £3,771,623.20 -> £3,381,645.74 (10.3%); £3,771,623.34 -> £3,381,645.73 (10.3%); £3,771,623.48 -> £3,381,645.73 (10.3%); £3,771,623.63 -> £3,381,645.73 (10.3%); £3,771,623.81 -> £3,381,645.72 (10.3%); £3,771,624.00 -> £3,381,645.72 (10.3%); £3,771,624.19 -> £3,381,645.71 (10.3%); £3,771,624.41 -> £3,381,645.70 (10.3%); £3,771,624.64 -> £3,381,645.69 (10.3%); £3,771,624.88 -> £3,381,645.69 (10.3%); £3,771,625.11 -> £3,381,645.68 (10.3%); £3,771,625.35 -> £3,381,645.68 (10.3%); £3,771,625.58 -> £3,381,645.68 (10.3%); £3,771,625.80 -> £3,381,645.67 (10.3%); £3,771,626.03 -> £3,381,645.67 (10.3%); £3,771,626.26 -> £3,381,645.67 (10.3%); £3,771,626.50 -> £3,381,645.66 (10.3%); £3,771,626.73 -> £3,381,645.66 (10.3%); £3,771,626.96 -> £3,381,645.66 (10.3%); £3,771,627.19 -> £3,381,645.66 (10.3%); £3,771,627.43 -> £3,381,645.66 (10.3%); £3,771,627.65 -> £3,381,645.66 (10.3%); £3,771,627.82 -> £3,381,645.64 (10.3%); £3,771,628.00 -> £3,381,645.63 (10.3%); £3,771,628.17 -> £3,381,645.61 (10.3%); £3,771,628.35 -> £3,381,645.59 (10.3%); £3,771,628.52 -> £3,381,645.57 (10.3%); £3,771,628.75 -> £3,381,645.54 (10.3%); £3,771,628.98 -> £3,381,645.52 (10.3%); £3,771,629.21 -> £3,381,645.49 (10.3%); £3,771,629.44 -> £3,381,645.47 (10.3%); £3,771,629.67 -> £3,381,645.45 (10.3%); £3,771,629.91 -> £3,381,645.43 (10.3%); £3,771,630.14 -> £3,381,645.42 (10.3%); £3,771,630.37 -> £3,381,645.42 (10.3%); £3,771,630.57 -> £3,381,645.41 (10.3%); £3,771,630.77 -> £3,381,645.41 (10.3%); £3,771,630.94 -> £3,381,645.41 (10.3%); £3,771,631.08 -> £3,381,645.40 (10.3%); £3,771,631.22 -> £3,381,645.40 (10.3%); £3,771,631.36 -> £3,381,645.40 (10.3%); £3,771,631.50 -> £3,381,645.41 (10.3%); £3,771,631.64 -> £3,381,645.41 (10.3%); £3,771,631.79 -> £3,381,645.41 (10.3%); £3,771,631.93 -> £3,381,645.41 (10.3%); £3,771,632.07 -> £3,381,645.41 (10.3%); £3,771,632.21 -> £3,381,645.42 (10.3%); £3,771,632.34 -> £3,381,645.42 (10.3%); £3,771,632.48 -> £3,381,645.42 (10.3%); £3,771,632.62 -> £3,381,645.42 (10.3%); £3,771,632.76 -> £3,381,645.42 (10.3%); £3,771,632.91 -> £3,381,645.42 (10.3%); £3,771,633.09 -> £3,381,645.42 (10.3%); £3,771,633.27 -> £3,381,645.41 (10.3%); £3,771,633.48 -> £3,381,645.41 (10.3%); £3,771,633.70 -> £3,381,645.40 (10.3%); £3,771,633.93 -> £3,381,645.39 (10.3%); £3,771,634.17 -> £3,381,645.38 (10.3%); £3,771,634.40 -> £3,381,645.37 (10.3%); £3,771,634.63 -> £3,381,645.36 (10.3%); £3,771,634.87 -> £3,381,645.36 (10.3%); £3,771,635.10 -> £3,381,645.35 (10.3%); £3,771,635.33 -> £3,381,645.34 (10.3%); £3,771,635.56 -> £3,381,645.33 (10.3%); £3,771,635.79 -> £3,381,645.32 (10.3%); £3,771,636.02 -> £3,381,645.31 (10.3%); £3,771,636.26 -> £3,381,645.31 (10.3%); £3,771,636.49 -> £3,381,645.30 (10.3%); £3,771,636.72 -> £3,381,645.30 (10.3%); £3,771,636.95 -> £3,381,645.30 (10.3%); £3,771,637.12 -> £3,381,645.28 (10.3%); £3,771,637.29 -> £3,381,645.26 (10.3%); £3,771,637.47 -> £3,381,645.25 (10.3%); £3,771,637.64 -> £3,381,645.23 (10.3%); £3,771,637.87 -> £3,381,645.21 (10.3%); £3,771,638.11 -> £3,381,645.18 (10.3%); £3,771,638.29 -> £3,381,645.15 (10.3%); £3,771,638.52 -> £3,381,645.13 (10.3%); £3,771,638.75 -> £3,381,645.10 (10.3%); £3,771,638.99 -> £3,381,645.08 (10.3%); £3,771,639.23 -> £3,381,645.06 (10.3%); £3,771,639.46 -> £3,381,645.05 (10.3%); £3,771,639.70 -> £3,381,645.04 (10.3%); £3,771,639.90 -> £3,381,645.04 (10.3%); £3,771,640.10 -> £3,381,645.03 (10.3%); £3,771,640.28 -> £3,381,645.03 (10.3%); £3,771,640.43 -> £3,381,645.03 (10.3%); £3,771,640.59 -> £3,381,645.03 (10.3%); £3,771,640.75 -> £3,381,645.03 (10.3%); £3,771,640.91 -> £3,381,645.04 (10.3%); £3,771,641.07 -> £3,381,645.04 (10.3%); £3,771,641.23 -> £3,381,645.04 (10.3%); £3,771,641.39 -> £3,381,645.04 (10.3%); £3,771,641.55 -> £3,381,645.04 (10.3%); £3,771,641.71 -> £3,381,645.05 (10.3%); £3,771,641.88 -> £3,381,645.05 (10.3%); £3,771,642.04 -> £3,381,645.05 (10.3%); £3,771,642.20 -> £3,381,645.05 (10.3%); £3,771,642.37 -> £3,381,645.04 (10.3%); £3,771,642.55 -> £3,381,645.08 (10.3%); £3,771,642.74 -> £3,381,645.14 (10.3%); £3,771,642.96 -> £3,381,645.19 (10.3%); £3,771,643.19 -> £3,381,645.24 (10.3%); £3,771,643.45 -> £3,381,645.28 (10.3%); £3,771,643.72 -> £3,381,645.33 (10.3%); £3,771,643.99 -> £3,381,645.36 (10.3%); £3,771,644.25 -> £3,381,645.40 (10.3%); £3,771,644.53 -> £3,381,645.40 (10.3%); £3,771,644.79 -> £3,381,645.39 (10.3%); £3,771,645.06 -> £3,381,645.39 (10.3%); £3,771,645.32 -> £3,381,645.39 (10.3%); £3,771,645.58 -> £3,381,645.39 (10.3%); £3,771,645.84 -> £3,381,645.39 (10.3%); £3,771,646.10 -> £3,381,645.39 (10.3%); £3,771,646.36 -> £3,381,645.39 (10.3%); £3,771,646.63 -> £3,381,645.38 (10.3%); £3,771,646.91 -> £3,381,645.38 (10.3%); £3,771,647.18 -> £3,381,645.42 (10.3%); £3,771,647.44 -> £3,381,645.48 (10.3%); £3,771,647.72 -> £3,381,645.55 (10.3%); £3,771,647.99 -> £3,381,645.61 (10.3%); £3,771,648.26 -> £3,381,645.68 (10.3%); £3,771,648.54 -> £3,381,645.75 (10.3%); £3,771,648.80 -> £3,381,645.83 (10.3%); £3,771,649.00 -> £3,381,645.91 (10.3%); £3,771,649.27 -> £3,381,645.89 (10.3%); £3,771,649.54 -> £3,381,645.86 (10.3%); £3,771,649.81 -> £3,381,645.84 (10.3%); £3,771,650.07 -> £3,381,645.82 (10.3%); £3,771,650.34 -> £3,381,645.81 (10.3%); £3,771,650.61 -> £3,381,645.81 (10.3%); £3,771,650.85 -> £3,381,645.80 (10.3%); £3,771,651.09 -> £3,381,645.80 (10.3%); £3,771,651.30 -> £3,381,645.80 (10.3%); £3,771,651.45 -> £3,381,645.80 (10.3%); £3,771,651.61 -> £3,381,645.80 (10.3%); £3,771,651.77 -> £3,381,645.80 (10.3%); £3,771,651.94 -> £3,381,645.80 (10.3%); £3,771,652.09 -> £3,381,645.80 (10.3%); £3,771,652.25 -> £3,381,645.80 (10.3%); £3,771,652.41 -> £3,381,645.81 (10.3%); £3,771,652.56 -> £3,381,645.81 (10.3%); £3,771,652.72 -> £3,381,645.81 (10.3%); £3,771,652.89 -> £3,381,645.81 (10.3%); £3,771,653.04 -> £3,381,645.81 (10.3%); £3,771,653.20 -> £3,381,645.81 (10.3%); £3,771,653.35 -> £3,381,645.81 (10.3%); £3,771,653.53 -> £3,381,645.85 (10.3%); £3,771,653.72 -> £3,381,645.90 (10.3%); £3,771,653.93 -> £3,381,645.96 (10.3%); £3,771,654.17 -> £3,381,646.01 (10.3%); £3,771,654.42 -> £3,381,646.05 (10.3%); £3,771,654.68 -> £3,381,646.10 (10.3%); £3,771,654.95 -> £3,381,646.13 (10.3%); £3,771,655.22 -> £3,381,646.17 (10.3%); £3,771,655.48 -> £3,381,646.17 (10.3%); £3,771,655.75 -> £3,381,646.17 (10.3%); £3,771,656.02 -> £3,381,646.16 (10.3%); £3,771,656.28 -> £3,381,646.16 (10.3%); £3,771,656.54 -> £3,381,646.16 (10.3%); £3,771,656.80 -> £3,381,646.16 (10.3%); £3,771,657.07 -> £3,381,646.16 (10.3%); £3,771,657.35 -> £3,381,646.16 (10.3%); £3,771,657.61 -> £3,381,646.16 (10.3%); £3,771,657.87 -> £3,381,646.16 (10.3%); £3,771,658.14 -> £3,381,646.19 (10.3%); £3,771,658.34 -> £3,381,646.25 (10.3%); £3,771,658.53 -> £3,381,646.32 (10.3%); £3,771,658.81 -> £3,381,646.39 (10.3%); £3,771,659.07 -> £3,381,646.45 (10.3%); £3,771,659.27 -> £3,381,646.52 (10.3%); £3,771,659.47 -> £3,381,646.60 (10.3%); £3,771,659.67 -> £3,381,646.68 (10.3%); £3,771,659.93 -> £3,381,646.66 (10.3%); £3,771,660.19 -> £3,381,646.64 (10.3%); £3,771,660.45 -> £3,381,646.61 (10.3%); £3,771,660.71 -> £3,381,646.59 (10.3%); £3,771,660.97 -> £3,381,646.59 (10.3%); £3,771,661.24 -> £3,381,646.58 (10.3%); £3,771,661.48 -> £3,381,646.58 (10.3%); £3,771,661.70 -> £3,381,646.57 (10.3%); £3,771,661.90 -> £3,381,646.57 (10.3%); £3,771,662.06 -> £3,381,646.57 (10.3%); £3,771,662.22 -> £3,381,646.57 (10.3%); £3,771,662.38 -> £3,381,646.58 (10.3%); £3,771,662.54 -> £3,381,646.58 (10.3%); £3,771,662.70 -> £3,381,646.58 (10.3%); £3,771,662.86 -> £3,381,646.58 (10.3%); £3,771,663.02 -> £3,381,646.58 (10.3%); £3,771,663.18 -> £3,381,646.59 (10.3%); £3,771,663.34 -> £3,381,646.59 (10.3%); £3,771,663.50 -> £3,381,646.59 (10.3%); £3,771,663.66 -> £3,381,646.59 (10.3%); £3,771,663.81 -> £3,381,646.59 (10.3%); £3,771,663.97 -> £3,381,646.58 (10.3%); £3,771,664.15 -> £3,381,646.63 (10.3%); £3,771,664.34 -> £3,381,646.68 (10.3%); £3,771,664.55 -> £3,381,646.73 (10.3%); £3,771,664.78 -> £3,381,646.78 (10.3%); £3,771,665.03 -> £3,381,646.83 (10.3%); £3,771,665.30 -> £3,381,646.87 (10.3%); £3,771,665.57 -> £3,381,646.91 (10.3%); £3,771,665.84 -> £3,381,646.94 (10.3%); £3,771,666.10 -> £3,381,646.94 (10.3%); £3,771,666.37 -> £3,381,646.94 (10.3%); £3,771,666.63 -> £3,381,646.94 (10.3%); £3,771,666.89 -> £3,381,646.94 (10.3%); £3,771,667.15 -> £3,381,646.94 (10.3%); £3,771,667.41 -> £3,381,646.94 (10.3%); £3,771,667.68 -> £3,381,646.94 (10.3%); £3,771,667.95 -> £3,381,646.94 (10.3%); £3,771,668.21 -> £3,381,646.93 (10.3%); £3,771,668.47 -> £3,381,646.94 (10.3%); £3,771,668.74 -> £3,381,646.97 (10.3%); £3,771,669.00 -> £3,381,647.03 (10.3%); £3,771,669.27 -> £3,381,647.10 (10.3%); £3,771,669.47 -> £3,381,647.16 (10.3%); £3,771,669.67 -> £3,381,647.23 (10.3%); £3,771,669.88 -> £3,381,647.30 (10.3%); £3,771,670.14 -> £3,381,647.38 (10.3%); £3,771,670.41 -> £3,381,647.46 (10.3%); £3,771,670.67 -> £3,381,647.44 (10.3%); £3,771,670.93 -> £3,381,647.41 (10.3%); £3,771,671.20 -> £3,381,647.39 (10.3%); £3,771,671.47 -> £3,381,647.37 (10.3%); £3,771,671.74 -> £3,381,647.36 (10.3%); £3,771,672.00 -> £3,381,647.36 (10.3%); £3,771,672.25 -> £3,381,647.35 (10.3%); £3,771,672.47 -> £3,381,647.35 (10.3%); £3,771,672.67 -> £3,381,647.35 (10.3%); £3,771,672.83 -> £3,381,647.35 (10.3%); £3,771,672.99 -> £3,381,647.35 (10.3%); £3,771,673.15 -> £3,381,647.35 (10.3%); £3,771,673.31 -> £3,381,647.35 (10.3%); £3,771,673.47 -> £3,381,647.36 (10.3%); £3,771,673.63 -> £3,381,647.36 (10.3%); £3,771,673.79 -> £3,381,647.36 (10.3%); £3,771,673.95 -> £3,381,647.36 (10.3%); £3,771,674.11 -> £3,381,647.37 (10.3%); £3,771,674.26 -> £3,381,647.37 (10.3%); £3,771,674.43 -> £3,381,647.37 (10.3%); £3,771,674.59 -> £3,381,647.37 (10.3%); £3,771,674.76 -> £3,381,647.36 (10.3%); £3,771,674.92 -> £3,381,647.41 (10.3%); £3,771,675.11 -> £3,381,647.46 (10.3%); £3,771,675.33 -> £3,381,647.51 (10.3%); £3,771,675.55 -> £3,381,647.56 (10.3%); £3,771,675.79 -> £3,381,647.61 (10.3%); £3,771,676.06 -> £3,381,647.65 (10.3%); £3,771,676.32 -> £3,381,647.69 (10.3%); £3,771,676.58 -> £3,381,647.72 (10.3%); £3,771,676.84 -> £3,381,647.72 (10.3%); £3,771,677.10 -> £3,381,647.72 (10.3%); £3,771,677.36 -> £3,381,647.72 (10.3%); £3,771,677.63 -> £3,381,647.72 (10.3%); £3,771,677.90 -> £3,381,647.72 (10.3%); £3,771,678.17 -> £3,381,647.72 (10.3%); £3,771,678.43 -> £3,381,647.72 (10.3%); £3,771,678.69 -> £3,381,647.71 (10.3%); £3,771,678.96 -> £3,381,647.71 (10.3%); £3,771,679.23 -> £3,381,647.71 (10.3%); £3,771,679.50 -> £3,381,647.75 (10.3%); £3,771,679.77 -> £3,381,647.81 (10.3%); £3,771,679.97 -> £3,381,647.87 (10.3%); £3,771,680.16 -> £3,381,647.94 (10.3%); £3,771,680.36 -> £3,381,648.01 (10.3%); £3,771,680.56 -> £3,381,648.07 (10.3%); £3,771,680.75 -> £3,381,648.16 (10.3%); £3,771,681.02 -> £3,381,648.24 (10.3%); £3,771,681.28 -> £3,381,648.21 (10.3%); £3,771,681.55 -> £3,381,648.19 (10.3%); £3,771,681.81 -> £3,381,648.17 (10.3%); £3,771,682.07 -> £3,381,648.15 (10.3%); £3,771,682.34 -> £3,381,648.14 (10.3%); £3,771,682.61 -> £3,381,648.13 (10.3%); £3,771,682.86 -> £3,381,648.13 (10.3%); £3,771,683.08 -> £3,381,648.13 (10.3%); £3,771,683.28 -> £3,381,648.12 (10.3%); £3,771,683.44 -> £3,381,648.12 (10.3%); £3,771,683.59 -> £3,381,648.13 (10.3%); £3,771,683.76 -> £3,381,648.13 (10.3%); £3,771,683.91 -> £3,381,648.13 (10.3%); £3,771,684.07 -> £3,381,648.13 (10.3%); £3,771,684.23 -> £3,381,648.13 (10.3%); £3,771,684.38 -> £3,381,648.14 (10.3%); £3,771,684.55 -> £3,381,648.14 (10.3%); £3,771,684.71 -> £3,381,648.14 (10.3%); £3,771,684.87 -> £3,381,648.14 (10.3%); £3,771,685.02 -> £3,381,648.14 (10.3%); £3,771,685.18 -> £3,381,648.14 (10.3%); £3,771,685.34 -> £3,381,648.13 (10.3%); £3,771,685.52 -> £3,381,648.18 (10.3%); £3,771,685.71 -> £3,381,648.23 (10.3%); £3,771,685.92 -> £3,381,648.28 (10.3%); £3,771,686.15 -> £3,381,648.33 (10.3%); £3,771,686.40 -> £3,381,648.38 (10.3%); £3,771,686.67 -> £3,381,648.42 (10.3%); £3,771,686.94 -> £3,381,648.46 (10.3%); £3,771,687.22 -> £3,381,648.49 (10.3%); £3,771,687.49 -> £3,381,648.49 (10.3%); £3,771,687.75 -> £3,381,648.49 (10.3%); £3,771,688.02 -> £3,381,648.49 (10.3%); £3,771,688.29 -> £3,381,648.49 (10.3%); £3,771,688.55 -> £3,381,648.49 (10.3%); £3,771,688.82 -> £3,381,648.49 (10.3%); £3,771,689.08 -> £3,381,648.49 (10.3%); £3,771,689.34 -> £3,381,648.49 (10.3%); £3,771,689.61 -> £3,381,648.49 (10.3%); £3,771,689.87 -> £3,381,648.49 (10.3%); £3,771,690.14 -> £3,381,648.52 (10.3%); £3,771,690.41 -> £3,381,648.58 (10.3%); £3,771,690.68 -> £3,381,648.65 (10.3%); £3,771,690.94 -> £3,381,648.71 (10.3%); £3,771,691.20 -> £3,381,648.78 (10.3%); £3,771,691.47 -> £3,381,648.85 (10.3%); £3,771,691.73 -> £3,381,648.93 (10.3%); £3,771,692.00 -> £3,381,649.02 (10.3%); £3,771,692.26 -> £3,381,648.99 (10.3%); £3,771,692.53 -> £3,381,648.97 (10.3%); £3,771,692.80 -> £3,381,648.95 (10.3%); £3,771,693.06 -> £3,381,648.92 (10.3%); £3,771,693.33 -> £3,381,648.92 (10.3%); £3,771,693.59 -> £3,381,648.91 (10.3%); £3,771,693.85 -> £3,381,648.91 (10.3%); £3,771,694.08 -> £3,381,648.91 (10.3%); £3,771,694.28 -> £3,381,648.90 (10.3%); £3,771,694.42 -> £3,381,648.90 (10.3%); £3,771,694.56 -> £3,381,648.90 (10.3%); £3,771,694.70 -> £3,381,648.91 (10.3%); £3,771,694.84 -> £3,381,648.91 (10.3%); £3,771,694.97 -> £3,381,648.91 (10.3%); £3,771,695.11 -> £3,381,648.91 (10.3%); £3,771,695.26 -> £3,381,648.92 (10.3%); £3,771,695.40 -> £3,381,648.92 (10.3%); £3,771,695.54 -> £3,381,648.92 (10.3%); £3,771,695.68 -> £3,381,648.92 (10.3%); £3,771,695.81 -> £3,381,648.92 (10.3%); £3,771,695.96 -> £3,381,648.92 (10.3%); £3,771,696.10 -> £3,381,648.92 (10.3%); £3,771,696.25 -> £3,381,648.92 (10.3%); £3,771,696.42 -> £3,381,648.92 (10.3%); £3,771,696.61 -> £3,381,648.91 (10.3%); £3,771,696.81 -> £3,381,648.90 (10.3%); £3,771,697.02 -> £3,381,648.89 (10.3%); £3,771,697.25 -> £3,381,648.88 (10.3%); £3,771,697.49 -> £3,381,648.88 (10.3%); £3,771,697.73 -> £3,381,648.88 (10.3%); £3,771,697.96 -> £3,381,648.87 (10.3%); £3,771,698.19 -> £3,381,648.87 (10.3%); £3,771,698.41 -> £3,381,648.87 (10.3%); £3,771,698.65 -> £3,381,648.86 (10.3%); £3,771,698.88 -> £3,381,648.86 (10.3%); £3,771,699.12 -> £3,381,648.85 (10.3%); £3,771,699.35 -> £3,381,648.85 (10.3%); £3,771,699.57 -> £3,381,648.85 (10.3%); £3,771,699.80 -> £3,381,648.85 (10.3%); £3,771,700.04 -> £3,381,648.85 (10.3%); £3,771,700.28 -> £3,381,648.85 (10.3%); £3,771,700.51 -> £3,381,648.83 (10.3%); £3,771,700.69 -> £3,381,648.82 (10.3%); £3,771,700.93 -> £3,381,648.80 (10.3%); £3,771,701.10 -> £3,381,648.78 (10.3%); £3,771,701.27 -> £3,381,648.76 (10.3%); £3,771,701.45 -> £3,381,648.73 (10.3%); £3,771,701.62 -> £3,381,648.71 (10.3%); £3,771,701.85 -> £3,381,648.68 (10.3%); £3,771,702.08 -> £3,381,648.66 (10.3%); £3,771,702.31 -> £3,381,648.64 (10.3%); £3,771,702.54 -> £3,381,648.62 (10.3%); £3,771,702.77 -> £3,381,648.62 (10.3%); £3,771,703.00 -> £3,381,648.61 (10.3%); £3,771,703.22 -> £3,381,648.61 (10.3%); £3,771,703.40 -> £3,381,648.60 (10.3%); £3,771,703.58 -> £3,381,648.60 (10.3%); £3,771,703.72 -> £3,381,648.60 (10.3%); £3,771,703.87 -> £3,381,648.60 (10.3%); £3,771,704.01 -> £3,381,648.60 (10.3%); £3,771,704.15 -> £3,381,648.60 (10.3%); £3,771,704.29 -> £3,381,648.60 (10.3%); £3,771,704.43 -> £3,381,648.61 (10.3%); £3,771,704.57 -> £3,381,648.61 (10.3%); £3,771,704.70 -> £3,381,648.61 (10.3%); £3,771,704.85 -> £3,381,648.61 (10.3%); £3,771,704.99 -> £3,381,648.62 (10.3%); £3,771,705.13 -> £3,381,648.62 (10.3%); £3,771,705.27 -> £3,381,648.62 (10.3%); £3,771,705.41 -> £3,381,648.62 (10.3%); £3,771,705.57 -> £3,381,648.62 (10.3%); £3,771,705.73 -> £3,381,648.62 (10.3%); £3,771,705.91 -> £3,381,648.61 (10.3%); £3,771,706.11 -> £3,381,648.61 (10.3%); £3,771,706.34 -> £3,381,648.60 (10.3%); £3,771,706.58 -> £3,381,648.59 (10.3%); £3,771,706.81 -> £3,381,648.58 (10.3%); £3,771,707.04 -> £3,381,648.57 (10.3%); £3,771,707.28 -> £3,381,648.57 (10.3%); £3,771,707.51 -> £3,381,648.56 (10.3%); £3,771,707.75 -> £3,381,648.55 (10.3%); £3,771,707.98 -> £3,381,648.54 (10.3%); £3,771,708.23 -> £3,381,648.53 (10.3%); £3,771,708.46 -> £3,381,648.53 (10.3%); £3,771,708.70 -> £3,381,648.52 (10.3%); £3,771,708.94 -> £3,381,648.51 (10.3%); £3,771,709.17 -> £3,381,648.51 (10.3%); £3,771,709.41 -> £3,381,648.51 (10.3%); £3,771,709.65 -> £3,381,648.50 (10.3%); £3,771,709.88 -> £3,381,648.49 (10.3%); £3,771,710.11 -> £3,381,648.47 (10.3%); £3,771,710.27 -> £3,381,648.45 (10.3%); £3,771,710.45 -> £3,381,648.43 (10.3%); £3,771,710.63 -> £3,381,648.42 (10.3%); £3,771,710.81 -> £3,381,648.39 (10.3%); £3,771,710.98 -> £3,381,648.36 (10.3%); £3,771,711.22 -> £3,381,648.33 (10.3%); £3,771,711.45 -> £3,381,648.31 (10.3%); £3,771,711.69 -> £3,381,648.29 (10.3%); £3,771,711.92 -> £3,381,648.27 (10.3%); £3,771,712.16 -> £3,381,648.26 (10.3%); £3,771,712.39 -> £3,381,648.25 (10.3%); £3,771,712.61 -> £3,381,648.25 (10.3%); £3,771,712.82 -> £3,381,648.25 (10.3%); £3,771,713.00 -> £3,381,648.25 (10.3%); £3,771,713.16 -> £3,381,648.25 (10.3%); £3,771,713.32 -> £3,381,648.25 (10.3%); £3,771,713.48 -> £3,381,648.25 (10.3%); £3,771,713.64 -> £3,381,648.25 (10.3%); £3,771,713.80 -> £3,381,648.25 (10.3%); £3,771,713.97 -> £3,381,648.26 (10.3%); £3,771,714.13 -> £3,381,648.26 (10.3%); £3,771,714.30 -> £3,381,648.26 (10.3%); £3,771,714.46 -> £3,381,648.26 (10.3%); £3,771,714.63 -> £3,381,648.27 (10.3%); £3,771,714.79 -> £3,381,648.27 (10.3%); £3,771,714.96 -> £3,381,648.27 (10.3%); £3,771,715.12 -> £3,381,648.26 (10.3%); £3,771,715.30 -> £3,381,648.30 (10.3%); £3,771,715.50 -> £3,381,648.36 (10.3%); £3,771,715.73 -> £3,381,648.41 (10.3%); £3,771,715.97 -> £3,381,648.46 (10.3%); £3,771,716.21 -> £3,381,648.50 (10.3%); £3,771,716.47 -> £3,381,648.55 (10.3%); £3,771,716.75 -> £3,381,648.58 (10.3%); £3,771,717.03 -> £3,381,648.62 (10.3%); £3,771,717.31 -> £3,381,648.62 (10.3%); £3,771,717.58 -> £3,381,648.62 (10.3%); £3,771,717.85 -> £3,381,648.62 (10.3%); £3,771,718.11 -> £3,381,648.61 (10.3%); £3,771,718.38 -> £3,381,648.61 (10.3%); £3,771,718.64 -> £3,381,648.61 (10.3%); £3,771,718.92 -> £3,381,648.61 (10.3%); £3,771,719.18 -> £3,381,648.61 (10.3%); £3,771,719.45 -> £3,381,648.61 (10.3%); £3,771,719.73 -> £3,381,648.61 (10.3%); £3,771,720.00 -> £3,381,648.64 (10.3%); £3,771,720.20 -> £3,381,648.70 (10.3%); £3,771,720.40 -> £3,381,648.77 (10.3%); £3,771,720.60 -> £3,381,648.83 (10.3%); £3,771,720.81 -> £3,381,648.90 (10.3%); £3,771,721.02 -> £3,381,648.97 (10.3%); £3,771,721.30 -> £3,381,649.05 (10.3%); £3,771,721.57 -> £3,381,649.14 (10.3%); £3,771,721.85 -> £3,381,649.11 (10.3%); £3,771,722.12 -> £3,381,649.09 (10.3%); £3,771,722.39 -> £3,381,649.06 (10.3%); £3,771,722.66 -> £3,381,649.04 (10.3%); £3,771,722.93 -> £3,381,649.04 (10.3%); £3,771,723.20 -> £3,381,649.03 (10.3%); £3,771,723.45 -> £3,381,649.03 (10.3%); £3,771,723.69 -> £3,381,649.02 (10.3%); £3,771,723.90 -> £3,381,649.02 (10.3%); £3,771,724.07 -> £3,381,649.02 (10.3%); £3,771,724.24 -> £3,381,649.02 (10.3%); £3,771,724.41 -> £3,381,649.03 (10.3%); £3,771,724.57 -> £3,381,649.03 (10.3%); £3,771,724.74 -> £3,381,649.03 (10.3%); £3,771,724.91 -> £3,381,649.03 (10.3%); £3,771,725.07 -> £3,381,649.04 (10.3%); £3,771,725.23 -> £3,381,649.04 (10.3%); £3,771,725.40 -> £3,381,649.04 (10.3%); £3,771,725.57 -> £3,381,649.04 (10.3%); £3,771,725.73 -> £3,381,649.04 (10.3%); £3,771,725.90 -> £3,381,649.04 (10.3%); £3,771,726.07 -> £3,381,649.04 (10.3%); £3,771,726.25 -> £3,381,649.08 (10.3%); £3,771,726.45 -> £3,381,649.14 (10.3%); £3,771,726.67 -> £3,381,649.19 (10.3%); £3,771,726.91 -> £3,381,649.24 (10.3%); £3,771,727.16 -> £3,381,649.28 (10.3%); £3,771,727.44 -> £3,381,649.33 (10.3%); £3,771,727.71 -> £3,381,649.37 (10.3%); £3,771,727.99 -> £3,381,649.40 (10.3%); £3,771,728.27 -> £3,381,649.40 (10.3%); £3,771,728.54 -> £3,381,649.40 (10.3%); £3,771,728.82 -> £3,381,649.40 (10.3%); £3,771,729.09 -> £3,381,649.40 (10.3%); £3,771,729.36 -> £3,381,649.39 (10.3%); £3,771,729.64 -> £3,381,649.39 (10.3%); £3,771,729.91 -> £3,381,649.39 (10.3%); £3,771,730.18 -> £3,381,649.39 (10.3%); £3,771,730.44 -> £3,381,649.39 (10.3%); £3,771,730.71 -> £3,381,649.39 (10.3%); £3,771,730.99 -> £3,381,649.43 (10.3%); £3,771,731.20 -> £3,381,649.48 (10.3%); £3,771,731.40 -> £3,381,649.55 (10.3%); £3,771,731.61 -> £3,381,649.62 (10.3%); £3,771,731.82 -> £3,381,649.68 (10.3%); £3,771,732.02 -> £3,381,649.75 (10.3%); £3,771,732.22 -> £3,381,649.83 (10.3%); £3,771,732.43 -> £3,381,649.91 (10.3%); £3,771,732.71 -> £3,381,649.89 (10.3%); £3,771,732.98 -> £3,381,649.86 (10.3%); £3,771,733.25 -> £3,381,649.84 (10.3%); £3,771,733.52 -> £3,381,649.81 (10.3%); £3,771,733.80 -> £3,381,649.81 (10.3%); £3,771,734.07 -> £3,381,649.80 (10.3%); £3,771,734.32 -> £3,381,649.80 (10.3%); £3,771,734.55 -> £3,381,649.79 (10.3%); £3,771,734.76 -> £3,381,649.79 (10.3%); £3,771,734.93 -> £3,381,649.79 (10.3%); £3,771,735.09 -> £3,381,649.79 (10.3%); £3,771,735.25 -> £3,381,649.80 (10.3%); £3,771,735.41 -> £3,381,649.80 (10.3%); £3,771,735.58 -> £3,381,649.80 (10.3%); £3,771,735.75 -> £3,381,649.80 (10.3%); £3,771,735.92 -> £3,381,649.80 (10.3%); £3,771,736.08 -> £3,381,649.81 (10.3%); £3,771,736.24 -> £3,381,649.81 (10.3%); £3,771,736.41 -> £3,381,649.81 (10.3%); £3,771,736.58 -> £3,381,649.81 (10.3%); £3,771,736.75 -> £3,381,649.81 (10.3%); £3,771,736.91 -> £3,381,649.80 (10.3%); £3,771,737.09 -> £3,381,649.85 (10.3%); £3,771,737.30 -> £3,381,649.90 (10.3%); £3,771,737.52 -> £3,381,649.95 (10.3%); £3,771,737.76 -> £3,381,650.00 (10.3%); £3,771,738.02 -> £3,381,650.05 (10.3%); £3,771,738.30 -> £3,381,650.09 (10.3%); £3,771,738.58 -> £3,381,650.13 (10.3%); £3,771,738.87 -> £3,381,650.16 (10.3%); £3,771,739.14 -> £3,381,650.16 (10.3%); £3,771,739.42 -> £3,381,650.16 (10.3%); £3,771,739.69 -> £3,381,650.16 (10.3%); £3,771,739.98 -> £3,381,650.16 (10.3%); £3,771,740.24 -> £3,381,650.15 (10.3%); £3,771,740.51 -> £3,381,650.15 (10.3%); £3,771,740.79 -> £3,381,650.15 (10.3%); £3,771,741.07 -> £3,381,650.15 (10.3%); £3,771,741.34 -> £3,381,650.15 (10.3%); £3,771,741.62 -> £3,381,650.15 (10.3%); £3,771,741.89 -> £3,381,650.19 (10.3%); £3,771,742.10 -> £3,381,650.25 (10.3%); £3,771,742.31 -> £3,381,650.31 (10.3%); £3,771,742.58 -> £3,381,650.38 (10.3%); £3,771,742.79 -> £3,381,650.44 (10.3%); £3,771,742.99 -> £3,381,650.51 (10.3%); £3,771,743.20 -> £3,381,650.59 (10.3%); £3,771,743.46 -> £3,381,650.68 (10.3%); £3,771,743.75 -> £3,381,650.65 (10.3%); £3,771,744.01 -> £3,381,650.63 (10.3%); £3,771,744.28 -> £3,381,650.60 (10.3%); £3,771,744.55 -> £3,381,650.58 (10.3%); £3,771,744.84 -> £3,381,650.57 (10.3%); £3,771,745.12 -> £3,381,650.57 (10.3%); £3,771,745.37 -> £3,381,650.56 (10.3%); £3,771,745.61 -> £3,381,650.56 (10.3%); £3,771,745.83 -> £3,381,650.56 (10.3%); £3,771,746.00 -> £3,381,650.56 (10.3%); £3,771,746.16 -> £3,381,650.56 (10.3%); £3,771,746.32 -> £3,381,650.56 (10.3%); £3,771,746.48 -> £3,381,650.56 (10.3%); £3,771,746.65 -> £3,381,650.57 (10.3%); £3,771,746.82 -> £3,381,650.57 (10.3%); £3,771,746.98 -> £3,381,650.57 (10.3%); £3,771,747.15 -> £3,381,650.57 (10.3%); £3,771,747.32 -> £3,381,650.58 (10.3%); £3,771,747.47 -> £3,381,650.58 (10.3%); £3,771,747.64 -> £3,381,650.58 (10.3%); £3,771,747.80 -> £3,381,650.57 (10.3%); £3,771,747.97 -> £3,381,650.57 (10.3%); £3,771,748.16 -> £3,381,650.61 (10.3%); £3,771,748.36 -> £3,381,650.67 (10.3%); £3,771,748.58 -> £3,381,650.72 (10.3%); £3,771,748.82 -> £3,381,650.77 (10.3%); £3,771,749.07 -> £3,381,650.81 (10.3%); £3,771,749.35 -> £3,381,650.86 (10.3%); £3,771,749.62 -> £3,381,650.89 (10.3%); £3,771,749.90 -> £3,381,650.93 (10.3%); £3,771,750.18 -> £3,381,650.93 (10.3%); £3,771,750.46 -> £3,381,650.93 (10.3%); £3,771,750.73 -> £3,381,650.92 (10.3%); £3,771,751.00 -> £3,381,650.92 (10.3%); £3,771,751.28 -> £3,381,650.92 (10.3%); £3,771,751.56 -> £3,381,650.92 (10.3%); £3,771,751.82 -> £3,381,650.92 (10.3%); £3,771,752.10 -> £3,381,650.92 (10.3%); £3,771,752.37 -> £3,381,650.92 (10.3%); £3,771,752.64 -> £3,381,650.92 (10.3%); £3,771,752.91 -> £3,381,650.95 (10.3%); £3,771,753.12 -> £3,381,651.01 (10.3%); £3,771,753.40 -> £3,381,651.08 (10.3%); £3,771,753.61 -> £3,381,651.14 (10.3%); £3,771,753.87 -> £3,381,651.21 (10.3%); £3,771,754.14 -> £3,381,651.28 (10.3%); £3,771,754.42 -> £3,381,651.36 (10.3%); £3,771,754.69 -> £3,381,651.45 (10.3%); £3,771,754.96 -> £3,381,651.42 (10.3%); £3,771,755.25 -> £3,381,651.40 (10.3%); £3,771,755.52 -> £3,381,651.37 (10.3%); £3,771,755.79 -> £3,381,651.35 (10.3%); £3,771,756.08 -> £3,381,651.35 (10.3%); £3,771,756.35 -> £3,381,651.34 (10.3%); £3,771,756.61 -> £3,381,651.34 (10.3%); £3,771,756.85 -> £3,381,651.33 (10.3%); £3,771,757.06 -> £3,381,651.33 (10.3%); £3,771,757.22 -> £3,381,651.33 (10.3%); £3,771,757.39 -> £3,381,651.33 (10.3%); £3,771,757.55 -> £3,381,651.33 (10.3%); £3,771,757.71 -> £3,381,651.33 (10.3%); £3,771,757.87 -> £3,381,651.34 (10.3%); £3,771,758.04 -> £3,381,651.34 (10.3%); £3,771,758.21 -> £3,381,651.34 (10.3%); £3,771,758.37 -> £3,381,651.34 (10.3%); £3,771,758.53 -> £3,381,651.34 (10.3%); £3,771,758.70 -> £3,381,651.35 (10.3%); £3,771,758.86 -> £3,381,651.35 (10.3%); £3,771,759.03 -> £3,381,651.34 (10.3%); £3,771,759.19 -> £3,381,651.34 (10.3%); £3,771,759.37 -> £3,381,651.38 (10.3%); £3,771,759.58 -> £3,381,651.44 (10.3%); £3,771,759.79 -> £3,381,651.49 (10.3%); £3,771,760.02 -> £3,381,651.54 (10.3%); £3,771,760.28 -> £3,381,651.58 (10.3%); £3,771,760.54 -> £3,381,651.63 (10.3%); £3,771,760.81 -> £3,381,651.66 (10.3%); £3,771,761.09 -> £3,381,651.70 (10.3%); £3,771,761.36 -> £3,381,651.70 (10.3%); £3,771,761.63 -> £3,381,651.70 (10.3%); £3,771,761.89 -> £3,381,651.70 (10.3%); £3,771,762.15 -> £3,381,651.70 (10.3%); £3,771,762.42 -> £3,381,651.70 (10.3%); £3,771,762.69 -> £3,381,651.70 (10.3%); £3,771,762.97 -> £3,381,651.70 (10.3%); £3,771,763.25 -> £3,381,651.70 (10.3%); £3,771,763.52 -> £3,381,651.70 (10.3%); £3,771,763.79 -> £3,381,651.70 (10.3%); £3,771,764.06 -> £3,381,651.73 (10.3%); £3,771,764.33 -> £3,381,651.79 (10.3%); £3,771,764.60 -> £3,381,651.86 (10.3%); £3,771,764.87 -> £3,381,651.92 (10.3%); £3,771,765.15 -> £3,381,651.99 (10.3%); £3,771,765.42 -> £3,381,652.06 (10.3%); £3,771,765.63 -> £3,381,652.14 (10.3%); £3,771,765.83 -> £3,381,652.22 (10.3%); £3,771,766.11 -> £3,381,652.20 (10.3%); £3,771,766.37 -> £3,381,652.17 (10.3%); £3,771,766.64 -> £3,381,652.15 (10.3%); £3,771,766.91 -> £3,381,652.13 (10.3%); £3,771,767.18 -> £3,381,652.12 (10.3%); £3,771,767.45 -> £3,381,652.12 (10.3%); £3,771,767.70 -> £3,381,652.11 (10.3%); £3,771,767.94 -> £3,381,652.11 (10.3%); £3,771,768.15 -> £3,381,652.11 (10.3%); £3,771,768.29 -> £3,381,652.10 (10.3%); £3,771,768.44 -> £3,381,652.10 (10.3%); £3,771,768.58 -> £3,381,652.11 (10.3%); £3,771,768.72 -> £3,381,652.11 (10.3%); £3,771,768.86 -> £3,381,652.11 (10.3%); £3,771,769.01 -> £3,381,652.11 (10.3%); £3,771,769.15 -> £3,381,652.11 (10.3%); £3,771,769.29 -> £3,381,652.11 (10.3%); £3,771,769.43 -> £3,381,652.12 (10.3%); £3,771,769.57 -> £3,381,652.12 (10.3%); £3,771,769.72 -> £3,381,652.12 (10.3%); £3,771,769.86 -> £3,381,652.12 (10.3%); £3,771,770.00 -> £3,381,652.11 (10.3%); £3,771,770.16 -> £3,381,652.11 (10.3%); £3,771,770.34 -> £3,381,652.11 (10.3%); £3,771,770.54 -> £3,381,652.10 (10.3%); £3,771,770.74 -> £3,381,652.09 (10.3%); £3,771,770.96 -> £3,381,652.08 (10.3%); £3,771,771.20 -> £3,381,652.08 (10.3%); £3,771,771.43 -> £3,381,652.07 (10.3%); £3,771,771.67 -> £3,381,652.07 (10.3%); £3,771,771.91 -> £3,381,652.06 (10.3%); £3,771,772.16 -> £3,381,652.06 (10.3%); £3,771,772.40 -> £3,381,652.06 (10.3%); £3,771,772.63 -> £3,381,652.05 (10.3%); £3,771,772.87 -> £3,381,652.05 (10.3%); £3,771,773.10 -> £3,381,652.04 (10.3%); £3,771,773.34 -> £3,381,652.04 (10.3%); £3,771,773.59 -> £3,381,652.04 (10.3%); £3,771,773.83 -> £3,381,652.03 (10.3%); £3,771,774.06 -> £3,381,652.03 (10.3%); £3,771,774.31 -> £3,381,652.03 (10.3%); £3,771,774.54 -> £3,381,652.02 (10.3%); £3,771,774.78 -> £3,381,652.01 (10.3%); £3,771,775.01 -> £3,381,651.99 (10.3%); £3,771,775.19 -> £3,381,651.97 (10.3%); £3,771,775.43 -> £3,381,651.95 (10.3%); £3,771,775.61 -> £3,381,651.92 (10.3%); £3,771,775.79 -> £3,381,651.89 (10.3%); £3,771,776.03 -> £3,381,651.87 (10.3%); £3,771,776.27 -> £3,381,651.85 (10.3%); £3,771,776.51 -> £3,381,651.83 (10.3%); £3,771,776.75 -> £3,381,651.81 (10.3%); £3,771,777.00 -> £3,381,651.80 (10.3%); £3,771,777.24 -> £3,381,651.80 (10.3%); £3,771,777.45 -> £3,381,651.79 (10.3%); £3,771,777.66 -> £3,381,651.79 (10.3%); £3,771,777.85 -> £3,381,651.78 (10.3%); £3,771,777.99 -> £3,381,651.78 (10.3%); £3,771,778.13 -> £3,381,651.78 (10.3%); £3,771,778.27 -> £3,381,651.78 (10.3%); £3,771,778.41 -> £3,381,651.78 (10.3%); £3,771,778.55 -> £3,381,651.78 (10.3%); £3,771,778.69 -> £3,381,651.78 (10.3%); £3,771,778.83 -> £3,381,651.79 (10.3%); £3,771,778.98 -> £3,381,651.79 (10.3%); £3,771,779.12 -> £3,381,651.79 (10.3%); £3,771,779.26 -> £3,381,651.79 (10.3%); £3,771,779.39 -> £3,381,651.79 (10.3%); £3,771,779.53 -> £3,381,651.79 (10.3%); £3,771,779.67 -> £3,381,651.79 (10.3%); £3,771,779.82 -> £3,381,651.79 (10.3%); £3,771,779.99 -> £3,381,651.79 (10.3%); £3,771,780.18 -> £3,381,651.79 (10.3%); £3,771,780.38 -> £3,381,651.78 (10.3%); £3,771,780.60 -> £3,381,651.77 (10.3%); £3,771,780.84 -> £3,381,651.76 (10.3%); £3,771,781.08 -> £3,381,651.75 (10.3%); £3,771,781.31 -> £3,381,651.75 (10.3%); £3,771,781.55 -> £3,381,651.74 (10.3%); £3,771,781.78 -> £3,381,651.73 (10.3%); £3,771,782.02 -> £3,381,651.72 (10.3%); £3,771,782.26 -> £3,381,651.71 (10.3%); £3,771,782.49 -> £3,381,651.70 (10.3%); £3,771,782.72 -> £3,381,651.69 (10.3%); £3,771,782.95 -> £3,381,651.69 (10.3%); £3,771,783.19 -> £3,381,651.68 (10.3%); £3,771,783.42 -> £3,381,651.68 (10.3%); £3,771,783.65 -> £3,381,651.68 (10.3%); £3,771,783.89 -> £3,381,651.67 (10.3%); £3,771,784.12 -> £3,381,651.66 (10.3%); £3,771,784.35 -> £3,381,651.64 (10.3%); £3,771,784.53 -> £3,381,651.62 (10.3%); £3,771,784.71 -> £3,381,651.60 (10.3%); £3,771,784.89 -> £3,381,651.58 (10.3%); £3,771,785.06 -> £3,381,651.55 (10.3%); £3,771,785.24 -> £3,381,651.53 (10.3%); £3,771,785.48 -> £3,381,651.50 (10.3%); £3,771,785.71 -> £3,381,651.48 (10.3%); £3,771,785.94 -> £3,381,651.46 (10.3%); £3,771,786.17 -> £3,381,651.43 (10.3%); £3,771,786.40 -> £3,381,651.43 (10.3%); £3,771,786.64 -> £3,381,651.42 (10.3%); £3,771,786.86 -> £3,381,651.41 (10.3%); £3,771,787.06 -> £3,381,651.41 (10.3%); £3,771,787.24 -> £3,381,651.41 (10.3%); £3,771,787.40 -> £3,381,651.41 (10.3%); £3,771,787.56 -> £3,381,651.41 (10.3%); £3,771,787.71 -> £3,381,651.41 (10.3%); £3,771,787.87 -> £3,381,651.41 (10.3%); £3,771,788.03 -> £3,381,651.42 (10.3%); £3,771,788.18 -> £3,381,651.42 (10.3%); £3,771,788.33 -> £3,381,651.42 (10.3%); £3,771,788.49 -> £3,381,651.42 (10.3%); £3,771,788.64 -> £3,381,651.42 (10.3%); £3,771,788.80 -> £3,381,651.43 (10.3%); £3,771,788.95 -> £3,381,651.43 (10.3%); £3,771,789.10 -> £3,381,651.42 (10.3%); £3,771,789.26 -> £3,381,651.42 (10.3%); £3,771,789.43 -> £3,381,651.46 (10.3%); £3,771,789.63 -> £3,381,651.52 (10.3%); £3,771,789.84 -> £3,381,651.57 (10.3%); £3,771,790.06 -> £3,381,651.62 (10.3%); £3,771,790.30 -> £3,381,651.66 (10.3%); £3,771,790.57 -> £3,381,651.71 (10.3%); £3,771,790.82 -> £3,381,651.74 (10.3%); £3,771,791.08 -> £3,381,651.78 (10.3%); £3,771,791.33 -> £3,381,651.78 (10.3%); £3,771,791.59 -> £3,381,651.78 (10.3%); £3,771,791.86 -> £3,381,651.78 (10.3%); £3,771,792.11 -> £3,381,651.78 (10.3%); £3,771,792.37 -> £3,381,651.77 (10.3%); £3,771,792.63 -> £3,381,651.77 (10.3%); £3,771,792.89 -> £3,381,651.77 (10.3%); £3,771,793.15 -> £3,381,651.77 (10.3%); £3,771,793.41 -> £3,381,651.77 (10.3%); £3,771,793.67 -> £3,381,651.77 (10.3%); £3,771,793.93 -> £3,381,651.81 (10.3%); £3,771,794.13 -> £3,381,651.87 (10.3%); £3,771,794.32 -> £3,381,651.93 (10.3%); £3,771,794.51 -> £3,381,652.00 (10.3%); £3,771,794.71 -> £3,381,652.06 (10.3%); £3,771,794.90 -> £3,381,652.13 (10.3%); £3,771,795.09 -> £3,381,652.21 (10.3%); £3,771,795.29 -> £3,381,652.30 (10.3%); £3,771,795.55 -> £3,381,652.27 (10.3%); £3,771,795.81 -> £3,381,652.25 (10.3%); £3,771,796.07 -> £3,381,652.22 (10.3%); £3,771,796.33 -> £3,381,652.20 (10.3%); £3,771,796.59 -> £3,381,652.19 (10.3%); £3,771,796.85 -> £3,381,652.19 (10.3%); £3,771,797.08 -> £3,381,652.18 (10.3%); £3,771,797.31 -> £3,381,652.18 (10.3%); £3,771,797.51 -> £3,381,652.18 (10.3%); £3,771,797.66 -> £3,381,652.18 (10.3%); £3,771,797.83 -> £3,381,652.18 (10.3%); £3,771,797.98 -> £3,381,652.18 (10.3%); £3,771,798.14 -> £3,381,652.18 (10.3%); £3,771,798.30 -> £3,381,652.19 (10.3%); £3,771,798.45 -> £3,381,652.19 (10.3%); £3,771,798.61 -> £3,381,652.19 (10.3%); £3,771,798.76 -> £3,381,652.19 (10.3%); £3,771,798.91 -> £3,381,652.19 (10.3%); £3,771,799.07 -> £3,381,652.20 (10.3%); £3,771,799.22 -> £3,381,652.20 (10.3%); £3,771,799.38 -> £3,381,652.19 (10.3%); £3,771,799.54 -> £3,381,652.19 (10.3%); £3,771,799.72 -> £3,381,652.23 (10.3%); £3,771,799.91 -> £3,381,652.28 (10.3%); £3,771,800.12 -> £3,381,652.34 (10.3%); £3,771,800.35 -> £3,381,652.39 (10.3%); £3,771,800.59 -> £3,381,652.43 (10.3%); £3,771,800.84 -> £3,381,652.48 (10.3%); £3,771,801.10 -> £3,381,652.51 (10.3%); £3,771,801.35 -> £3,381,652.55 (10.3%); £3,771,801.62 -> £3,381,652.55 (10.3%); £3,771,801.87 -> £3,381,652.55 (10.3%); £3,771,802.13 -> £3,381,652.54 (10.3%); £3,771,802.40 -> £3,381,652.54 (10.3%); £3,771,802.66 -> £3,381,652.54 (10.3%); £3,771,802.93 -> £3,381,652.54 (10.3%); £3,771,803.18 -> £3,381,652.54 (10.3%); £3,771,803.44 -> £3,381,652.54 (10.3%); £3,771,803.70 -> £3,381,652.54 (10.3%); £3,771,803.96 -> £3,381,652.54 (10.3%); £3,771,804.21 -> £3,381,652.58 (10.3%); £3,771,804.47 -> £3,381,652.63 (10.3%); £3,771,804.73 -> £3,381,652.70 (10.3%); £3,771,804.99 -> £3,381,652.77 (10.3%); £3,771,805.25 -> £3,381,652.84 (10.3%); £3,771,805.51 -> £3,381,652.90 (10.3%); £3,771,805.76 -> £3,381,652.99 (10.3%); £3,771,806.01 -> £3,381,653.07 (10.3%); £3,771,806.28 -> £3,381,653.05 (10.3%); £3,771,806.54 -> £3,381,653.02 (10.3%); £3,771,806.79 -> £3,381,653.00 (10.3%); £3,771,807.06 -> £3,381,652.98 (10.3%); £3,771,807.32 -> £3,381,652.97 (10.3%); £3,771,807.59 -> £3,381,652.97 (10.3%); £3,771,807.82 -> £3,381,652.96 (10.3%); £3,771,808.05 -> £3,381,652.96 (10.3%); £3,771,808.25 -> £3,381,652.95 (10.3%); £3,771,808.40 -> £3,381,652.95 (10.3%); £3,771,808.56 -> £3,381,652.96 (10.3%); £3,771,808.71 -> £3,381,652.96 (10.3%); £3,771,808.86 -> £3,381,652.96 (10.3%); £3,771,809.01 -> £3,381,652.96 (10.3%); £3,771,809.17 -> £3,381,652.96 (10.3%); £3,771,809.32 -> £3,381,652.97 (10.3%); £3,771,809.48 -> £3,381,652.97 (10.3%); £3,771,809.63 -> £3,381,652.97 (10.3%); £3,771,809.79 -> £3,381,652.97 (10.3%); £3,771,809.95 -> £3,381,652.97 (10.3%); £3,771,810.11 -> £3,381,652.97 (10.3%); £3,771,810.26 -> £3,381,652.96 (10.3%); £3,771,810.44 -> £3,381,653.01 (10.3%); £3,771,810.63 -> £3,381,653.06 (10.3%); £3,771,810.84 -> £3,381,653.12 (10.3%); £3,771,811.06 -> £3,381,653.16 (10.3%); £3,771,811.30 -> £3,381,653.21 (10.3%); £3,771,811.56 -> £3,381,653.25 (10.3%); £3,771,811.82 -> £3,381,653.29 (10.3%); £3,771,812.08 -> £3,381,653.33 (10.3%); £3,771,812.34 -> £3,381,653.33 (10.3%); £3,771,812.60 -> £3,381,653.32 (10.3%); £3,771,812.86 -> £3,381,653.32 (10.3%); £3,771,813.11 -> £3,381,653.32 (10.3%); £3,771,813.36 -> £3,381,653.32 (10.3%); £3,771,813.62 -> £3,381,653.32 (10.3%); £3,771,813.88 -> £3,381,653.32 (10.3%); £3,771,814.14 -> £3,381,653.32 (10.3%); £3,771,814.40 -> £3,381,653.32 (10.3%); £3,771,814.66 -> £3,381,653.32 (10.3%); £3,771,814.93 -> £3,381,653.35 (10.3%); £3,771,815.18 -> £3,381,653.41 (10.3%); £3,771,815.38 -> £3,381,653.48 (10.3%); £3,771,815.57 -> £3,381,653.54 (10.3%); £3,771,815.76 -> £3,381,653.61 (10.3%); £3,771,816.02 -> £3,381,653.68 (10.3%); £3,771,816.28 -> £3,381,653.76 (10.3%); £3,771,816.53 -> £3,381,653.84 (10.3%); £3,771,816.79 -> £3,381,653.82 (10.3%); £3,771,817.06 -> £3,381,653.80 (10.3%); £3,771,817.33 -> £3,381,653.78 (10.3%); £3,771,817.58 -> £3,381,653.75 (10.3%); £3,771,817.83 -> £3,381,653.75 (10.3%); £3,771,818.10 -> £3,381,653.74 (10.3%); £3,771,818.34 -> £3,381,653.74 (10.3%); £3,771,818.55 -> £3,381,653.73 (10.3%); £3,771,818.76 -> £3,381,653.73 (10.3%); £3,771,818.91 -> £3,381,653.73 (10.3%); £3,771,819.07 -> £3,381,653.73 (10.3%); £3,771,819.22 -> £3,381,653.74 (10.3%); £3,771,819.37 -> £3,381,653.74 (10.3%); £3,771,819.53 -> £3,381,653.74 (10.3%); £3,771,819.69 -> £3,381,653.74 (10.3%); £3,771,819.85 -> £3,381,653.74 (10.3%); £3,771,820.01 -> £3,381,653.75 (10.3%); £3,771,820.17 -> £3,381,653.75 (10.3%); £3,771,820.33 -> £3,381,653.75 (10.3%); £3,771,820.48 -> £3,381,653.75 (10.3%); £3,771,820.64 -> £3,381,653.75 (10.3%); £3,771,820.79 -> £3,381,653.74 (10.3%); £3,771,820.96 -> £3,381,653.79 (10.3%); £3,771,821.16 -> £3,381,653.84 (10.3%); £3,771,821.37 -> £3,381,653.89 (10.3%); £3,771,821.60 -> £3,381,653.94 (10.3%); £3,771,821.84 -> £3,381,653.99 (10.3%); £3,771,822.10 -> £3,381,654.03 (10.3%); £3,771,822.37 -> £3,381,654.07 (10.3%); £3,771,822.64 -> £3,381,654.11 (10.3%); £3,771,822.90 -> £3,381,654.10 (10.3%); £3,771,823.16 -> £3,381,654.10 (10.3%); £3,771,823.43 -> £3,381,654.10 (10.3%); £3,771,823.68 -> £3,381,654.10 (10.3%); £3,771,823.95 -> £3,381,654.10 (10.3%); £3,771,824.21 -> £3,381,654.10 (10.3%); £3,771,824.47 -> £3,381,654.10 (10.3%); £3,771,824.72 -> £3,381,654.10 (10.3%); £3,771,824.98 -> £3,381,654.10 (10.3%); £3,771,825.24 -> £3,381,654.10 (10.3%); £3,771,825.50 -> £3,381,654.13 (10.3%); £3,771,825.76 -> £3,381,654.19 (10.3%); £3,771,826.02 -> £3,381,654.26 (10.3%); £3,771,826.28 -> £3,381,654.33 (10.3%); £3,771,826.54 -> £3,381,654.39 (10.3%); £3,771,826.80 -> £3,381,654.46 (10.3%); £3,771,827.07 -> £3,381,654.55 (10.3%); £3,771,827.33 -> £3,381,654.63 (10.3%); £3,771,827.59 -> £3,381,654.60 (10.3%); £3,771,827.85 -> £3,381,654.58 (10.3%); £3,771,828.10 -> £3,381,654.56 (10.3%); £3,771,828.35 -> £3,381,654.54 (10.3%); £3,771,828.61 -> £3,381,654.53 (10.3%); £3,771,828.87 -> £3,381,654.52 (10.3%); £3,771,829.10 -> £3,381,654.52 (10.3%); £3,771,829.33 -> £3,381,654.51 (10.3%); £3,771,829.53 -> £3,381,654.51 (10.3%); £3,771,829.69 -> £3,381,654.51 (10.3%); £3,771,829.85 -> £3,381,654.51 (10.3%); £3,771,830.00 -> £3,381,654.51 (10.3%); £3,771,830.16 -> £3,381,654.52 (10.3%); £3,771,830.32 -> £3,381,654.52 (10.3%); £3,771,830.47 -> £3,381,654.52 (10.3%); £3,771,830.63 -> £3,381,654.52 (10.3%); £3,771,830.79 -> £3,381,654.53 (10.3%); £3,771,830.95 -> £3,381,654.53 (10.3%); £3,771,831.11 -> £3,381,654.53 (10.3%); £3,771,831.27 -> £3,381,654.53 (10.3%); £3,771,831.43 -> £3,381,654.53 (10.3%); £3,771,831.58 -> £3,381,654.52 (10.3%); £3,771,831.77 -> £3,381,654.57 (10.3%); £3,771,831.96 -> £3,381,654.62 (10.3%); £3,771,832.17 -> £3,381,654.67 (10.3%); £3,771,832.39 -> £3,381,654.72 (10.3%); £3,771,832.64 -> £3,381,654.77 (10.3%); £3,771,832.91 -> £3,381,654.81 (10.3%); £3,771,833.17 -> £3,381,654.85 (10.3%); £3,771,833.44 -> £3,381,654.88 (10.3%); £3,771,833.69 -> £3,381,654.88 (10.3%); £3,771,833.95 -> £3,381,654.88 (10.3%); £3,771,834.21 -> £3,381,654.88 (10.3%); £3,771,834.47 -> £3,381,654.88 (10.3%); £3,771,834.73 -> £3,381,654.88 (10.3%); £3,771,834.98 -> £3,381,654.87 (10.3%); £3,771,835.25 -> £3,381,654.87 (10.3%); £3,771,835.51 -> £3,381,654.87 (10.3%); £3,771,835.77 -> £3,381,654.87 (10.3%); £3,771,836.03 -> £3,381,654.87 (10.3%); £3,771,836.29 -> £3,381,654.91 (10.3%); £3,771,836.49 -> £3,381,654.97 (10.3%); £3,771,836.76 -> £3,381,655.03 (10.3%); £3,771,836.96 -> £3,381,655.10 (10.3%); £3,771,837.14 -> £3,381,655.16 (10.3%); £3,771,837.34 -> £3,381,655.23 (10.3%); £3,771,837.54 -> £3,381,655.31 (10.3%); £3,771,837.73 -> £3,381,655.39 (10.3%); £3,771,837.99 -> £3,381,655.37 (10.3%); £3,771,838.25 -> £3,381,655.34 (10.3%); £3,771,838.51 -> £3,381,655.32 (10.3%); £3,771,838.77 -> £3,381,655.30 (10.3%); £3,771,839.04 -> £3,381,655.29 (10.3%); £3,771,839.31 -> £3,381,655.29 (10.3%); £3,771,839.55 -> £3,381,655.28 (10.3%); £3,771,839.77 -> £3,381,655.28 (10.3%); £3,771,839.97 -> £3,381,655.28 (10.3%); £3,771,840.11 -> £3,381,655.28 (10.3%); £3,771,840.25 -> £3,381,655.28 (10.3%); £3,771,840.39 -> £3,381,655.28 (10.3%); £3,771,840.52 -> £3,381,655.28 (10.3%); £3,771,840.67 -> £3,381,655.28 (10.3%); £3,771,840.80 -> £3,381,655.29 (10.3%); £3,771,840.94 -> £3,381,655.29 (10.3%); £3,771,841.08 -> £3,381,655.29 (10.3%); £3,771,841.22 -> £3,381,655.29 (10.3%); £3,771,841.35 -> £3,381,655.29 (10.3%); £3,771,841.49 -> £3,381,655.30 (10.3%); £3,771,841.63 -> £3,381,655.29 (10.3%); £3,771,841.77 -> £3,381,655.29 (10.3%); £3,771,841.92 -> £3,381,655.29 (10.3%); £3,771,842.09 -> £3,381,655.28 (10.3%); £3,771,842.27 -> £3,381,655.28 (10.3%); £3,771,842.48 -> £3,381,655.27 (10.3%); £3,771,842.69 -> £3,381,655.26 (10.3%); £3,771,842.91 -> £3,381,655.25 (10.3%); £3,771,843.13 -> £3,381,655.25 (10.3%); £3,771,843.35 -> £3,381,655.24 (10.3%); £3,771,843.58 -> £3,381,655.24 (10.3%); £3,771,843.81 -> £3,381,655.24 (10.3%); £3,771,844.05 -> £3,381,655.23 (10.3%); £3,771,844.27 -> £3,381,655.23 (10.3%); £3,771,844.50 -> £3,381,655.22 (10.3%); £3,771,844.72 -> £3,381,655.22 (10.3%); £3,771,844.94 -> £3,381,655.22 (10.3%); £3,771,845.18 -> £3,381,655.22 (10.3%); £3,771,845.40 -> £3,381,655.21 (10.3%); £3,771,845.63 -> £3,381,655.21 (10.3%); £3,771,845.86 -> £3,381,655.21 (10.3%); £3,771,846.03 -> £3,381,655.20 (10.3%); £3,771,846.20 -> £3,381,655.18 (10.3%); £3,771,846.37 -> £3,381,655.16 (10.3%); £3,771,846.55 -> £3,381,655.15 (10.3%); £3,771,846.72 -> £3,381,655.13 (10.3%); £3,771,846.89 -> £3,381,655.10 (10.3%); £3,771,847.06 -> £3,381,655.07 (10.3%); £3,771,847.29 -> £3,381,655.05 (10.3%); £3,771,847.51 -> £3,381,655.02 (10.3%); £3,771,847.75 -> £3,381,655.00 (10.3%); £3,771,847.97 -> £3,381,654.98 (10.3%); £3,771,848.19 -> £3,381,654.98 (10.3%); £3,771,848.43 -> £3,381,654.97 (10.3%); £3,771,848.64 -> £3,381,654.97 (10.3%); £3,771,848.84 -> £3,381,654.96 (10.3%); £3,771,849.01 -> £3,381,654.96 (10.3%); £3,771,849.15 -> £3,381,654.96 (10.3%); £3,771,849.29 -> £3,381,654.96 (10.3%); £3,771,849.42 -> £3,381,654.96 (10.3%); £3,771,849.56 -> £3,381,654.96 (10.3%); £3,771,849.70 -> £3,381,654.96 (10.3%); £3,771,849.84 -> £3,381,654.96 (10.3%); £3,771,849.98 -> £3,381,654.96 (10.3%); £3,771,850.12 -> £3,381,654.96 (10.3%); £3,771,850.26 -> £3,381,654.97 (10.3%); £3,771,850.39 -> £3,381,654.97 (10.3%); £3,771,850.53 -> £3,381,654.97 (10.3%); £3,771,850.66 -> £3,381,654.97 (10.3%); £3,771,850.80 -> £3,381,654.97 (10.3%); £3,771,850.96 -> £3,381,654.97 (10.3%); £3,771,851.13 -> £3,381,654.97 (10.3%); £3,771,851.31 -> £3,381,654.96 (10.3%); £3,771,851.51 -> £3,381,654.95 (10.3%); £3,771,851.72 -> £3,381,654.94 (10.3%); £3,771,851.95 -> £3,381,654.93 (10.3%); £3,771,852.18 -> £3,381,654.93 (10.3%); £3,771,852.41 -> £3,381,654.92 (10.3%); £3,771,852.64 -> £3,381,654.91 (10.3%); £3,771,852.87 -> £3,381,654.90 (10.3%); £3,771,853.10 -> £3,381,654.89 (10.3%); £3,771,853.33 -> £3,381,654.88 (10.3%); £3,771,853.56 -> £3,381,654.88 (10.3%); £3,771,853.79 -> £3,381,654.87 (10.3%); £3,771,854.02 -> £3,381,654.86 (10.3%); £3,771,854.25 -> £3,381,654.86 (10.3%); £3,771,854.48 -> £3,381,654.85 (10.3%); £3,771,854.71 -> £3,381,654.85 (10.3%); £3,771,854.94 -> £3,381,654.85 (10.3%); £3,771,855.18 -> £3,381,654.84 (10.3%); £3,771,855.41 -> £3,381,654.82 (10.3%); £3,771,855.64 -> £3,381,654.80 (10.3%); £3,771,855.81 -> £3,381,654.78 (10.3%); £3,771,856.03 -> £3,381,654.76 (10.3%); £3,771,856.21 -> £3,381,654.73 (10.3%); £3,771,856.38 -> £3,381,654.71 (10.3%); £3,771,856.61 -> £3,381,654.68 (10.3%); £3,771,856.84 -> £3,381,654.66 (10.3%); £3,771,857.07 -> £3,381,654.64 (10.3%); £3,771,857.30 -> £3,381,654.62 (10.3%); £3,771,857.52 -> £3,381,654.61 (10.3%); £3,771,857.75 -> £3,381,654.60 (10.3%); £3,771,857.95 -> £3,381,654.60 (10.3%); £3,771,858.15 -> £3,381,654.60 (10.3%); £3,771,858.32 -> £3,381,654.60 (10.3%); £3,771,858.48 -> £3,381,654.60 (10.3%); £3,771,858.64 -> £3,381,654.60 (10.3%); £3,771,858.80 -> £3,381,654.60 (10.3%); £3,771,858.97 -> £3,381,654.60 (10.3%); £3,771,859.13 -> £3,381,654.60 (10.3%); £3,771,859.29 -> £3,381,654.61 (10.3%); £3,771,859.44 -> £3,381,654.61 (10.3%); £3,771,859.60 -> £3,381,654.61 (10.3%); £3,771,859.76 -> £3,381,654.61 (10.3%); £3,771,859.91 -> £3,381,654.62 (10.3%); £3,771,860.08 -> £3,381,654.62 (10.3%); £3,771,860.25 -> £3,381,654.61 (10.3%); £3,771,860.40 -> £3,381,654.61 (10.3%); £3,771,860.57 -> £3,381,654.65 (10.3%); £3,771,860.77 -> £3,381,654.71 (10.3%); £3,771,860.98 -> £3,381,654.76 (10.3%); £3,771,861.21 -> £3,381,654.81 (10.3%); £3,771,861.45 -> £3,381,654.85 (10.3%); £3,771,861.71 -> £3,381,654.90 (10.3%); £3,771,861.97 -> £3,381,654.93 (10.3%); £3,771,862.23 -> £3,381,654.97 (10.3%); £3,771,862.50 -> £3,381,654.97 (10.3%); £3,771,862.76 -> £3,381,654.97 (10.3%); £3,771,863.03 -> £3,381,654.96 (10.3%); £3,771,863.29 -> £3,381,654.96 (10.3%); £3,771,863.56 -> £3,381,654.96 (10.3%); £3,771,863.82 -> £3,381,654.96 (10.3%); £3,771,864.10 -> £3,381,654.96 (10.3%); £3,771,864.36 -> £3,381,654.96 (10.3%); £3,771,864.63 -> £3,381,654.96 (10.3%); £3,771,864.88 -> £3,381,654.96 (10.3%); £3,771,865.15 -> £3,381,655.00 (10.3%); £3,771,865.40 -> £3,381,655.05 (10.3%); £3,771,865.60 -> £3,381,655.12 (10.3%); £3,771,865.80 -> £3,381,655.19 (10.3%); £3,771,865.99 -> £3,381,655.25 (10.3%); £3,771,866.25 -> £3,381,655.32 (10.3%); £3,771,866.51 -> £3,381,655.41 (10.3%); £3,771,866.78 -> £3,381,655.49 (10.3%); £3,771,867.05 -> £3,381,655.47 (10.3%); £3,771,867.31 -> £3,381,655.44 (10.3%); £3,771,867.58 -> £3,381,655.42 (10.3%); £3,771,867.84 -> £3,381,655.40 (10.3%); £3,771,868.11 -> £3,381,655.39 (10.3%); £3,771,868.37 -> £3,381,655.39 (10.3%); £3,771,868.62 -> £3,381,655.38 (10.3%); £3,771,868.84 -> £3,381,655.38 (10.3%); £3,771,869.05 -> £3,381,655.38 (10.3%); £3,771,869.20 -> £3,381,655.38 (10.3%); £3,771,869.36 -> £3,381,655.38 (10.3%); £3,771,869.52 -> £3,381,655.38 (10.3%); £3,771,869.68 -> £3,381,655.38 (10.3%); £3,771,869.84 -> £3,381,655.38 (10.3%); £3,771,870.00 -> £3,381,655.39 (10.3%); £3,771,870.16 -> £3,381,655.39 (10.3%); £3,771,870.32 -> £3,381,655.39 (10.3%); £3,771,870.47 -> £3,381,655.39 (10.3%); £3,771,870.63 -> £3,381,655.39 (10.3%); £3,771,870.79 -> £3,381,655.40 (10.3%); £3,771,870.95 -> £3,381,655.39 (10.3%); £3,771,871.10 -> £3,381,655.39 (10.3%); £3,771,871.28 -> £3,381,655.43 (10.3%); £3,771,871.47 -> £3,381,655.48 (10.3%); £3,771,871.68 -> £3,381,655.54 (10.3%); £3,771,871.92 -> £3,381,655.59 (10.3%); £3,771,872.17 -> £3,381,655.63 (10.3%); £3,771,872.43 -> £3,381,655.68 (10.3%); £3,771,872.69 -> £3,381,655.71 (10.3%); £3,771,872.96 -> £3,381,655.75 (10.3%); £3,771,873.23 -> £3,381,655.75 (10.3%); £3,771,873.50 -> £3,381,655.75 (10.3%); £3,771,873.75 -> £3,381,655.74 (10.3%); £3,771,874.02 -> £3,381,655.74 (10.3%); £3,771,874.28 -> £3,381,655.74 (10.3%); £3,771,874.55 -> £3,381,655.74 (10.3%); £3,771,874.81 -> £3,381,655.74 (10.3%); £3,771,875.07 -> £3,381,655.74 (10.3%); £3,771,875.34 -> £3,381,655.74 (10.3%); £3,771,875.61 -> £3,381,655.74 (10.3%); £3,771,875.87 -> £3,381,655.78 (10.3%); £3,771,876.14 -> £3,381,655.84 (10.3%); £3,771,876.39 -> £3,381,655.90 (10.3%); £3,771,876.66 -> £3,381,655.97 (10.3%); £3,771,876.93 -> £3,381,656.04 (10.3%); £3,771,877.18 -> £3,381,656.11 (10.3%); £3,771,877.46 -> £3,381,656.19 (10.3%); £3,771,877.65 -> £3,381,656.27 (10.3%); £3,771,877.91 -> £3,381,656.25 (10.3%); £3,771,878.16 -> £3,381,656.22 (10.3%); £3,771,878.43 -> £3,381,656.20 (10.3%); £3,771,878.70 -> £3,381,656.18 (10.3%); £3,771,878.97 -> £3,381,656.17 (10.3%); £3,771,879.23 -> £3,381,656.17 (10.3%); £3,771,879.47 -> £3,381,656.16 (10.3%); £3,771,879.70 -> £3,381,656.16 (10.3%); £3,771,879.90 -> £3,381,656.16 (10.3%); £3,771,880.07 -> £3,381,656.16 (10.3%); £3,771,880.22 -> £3,381,656.16 (10.3%); £3,771,880.39 -> £3,381,656.16 (10.3%); £3,771,880.55 -> £3,381,656.16 (10.3%); £3,771,880.71 -> £3,381,656.17 (10.3%); £3,771,880.87 -> £3,381,656.17 (10.3%); £3,771,881.03 -> £3,381,656.17 (10.3%); £3,771,881.19 -> £3,381,656.17 (10.3%); £3,771,881.35 -> £3,381,656.18 (10.3%); £3,771,881.51 -> £3,381,656.18 (10.3%); £3,771,881.67 -> £3,381,656.18 (10.3%); £3,771,881.84 -> £3,381,656.18 (10.3%); £3,771,882.00 -> £3,381,656.17 (10.3%); £3,771,882.18 -> £3,381,656.22 (10.3%); £3,771,882.37 -> £3,381,656.27 (10.3%); £3,771,882.58 -> £3,381,656.32 (10.3%); £3,771,882.81 -> £3,381,656.37 (10.3%); £3,771,883.06 -> £3,381,656.42 (10.3%); £3,771,883.33 -> £3,381,656.46 (10.3%); £3,771,883.60 -> £3,381,656.50 (10.3%); £3,771,883.86 -> £3,381,656.53 (10.3%); £3,771,884.13 -> £3,381,656.53 (10.3%); £3,771,884.40 -> £3,381,656.53 (10.3%); £3,771,884.66 -> £3,381,656.53 (10.3%); £3,771,884.92 -> £3,381,656.53 (10.3%); £3,771,885.19 -> £3,381,656.52 (10.3%); £3,771,885.46 -> £3,381,656.52 (10.3%); £3,771,885.73 -> £3,381,656.52 (10.3%); £3,771,886.00 -> £3,381,656.52 (10.3%); £3,771,886.26 -> £3,381,656.52 (10.3%); £3,771,886.54 -> £3,381,656.52 (10.3%); £3,771,886.80 -> £3,381,656.56 (10.3%); £3,771,887.07 -> £3,381,656.62 (10.3%); £3,771,887.33 -> £3,381,656.68 (10.3%); £3,771,887.60 -> £3,381,656.75 (10.3%); £3,771,887.87 -> £3,381,656.82 (10.3%); £3,771,888.07 -> £3,381,656.88 (10.3%); £3,771,888.26 -> £3,381,656.97 (10.3%); £3,771,888.53 -> £3,381,657.05 (10.3%); £3,771,888.79 -> £3,381,657.03 (10.3%); £3,771,889.06 -> £3,381,657.00 (10.3%); £3,771,889.33 -> £3,381,656.98 (10.3%); £3,771,889.60 -> £3,381,656.96 (10.3%); £3,771,889.86 -> £3,381,656.95 (10.3%); £3,771,890.13 -> £3,381,656.95 (10.3%); £3,771,890.38 -> £3,381,656.94 (10.3%); £3,771,890.60 -> £3,381,656.94 (10.3%); £3,771,890.81 -> £3,381,656.94 (10.3%); £3,771,890.96 -> £3,381,656.94 (10.3%); £3,771,891.12 -> £3,381,656.94 (10.3%); £3,771,891.28 -> £3,381,656.94 (10.3%); £3,771,891.44 -> £3,381,656.95 (10.3%); £3,771,891.60 -> £3,381,656.95 (10.3%); £3,771,891.77 -> £3,381,656.95 (10.3%); £3,771,891.93 -> £3,381,656.95 (10.3%); £3,771,892.09 -> £3,381,656.95 (10.3%); £3,771,892.25 -> £3,381,656.96 (10.3%); £3,771,892.41 -> £3,381,656.96 (10.3%); £3,771,892.57 -> £3,381,656.96 (10.3%); £3,771,892.73 -> £3,381,656.96 (10.3%); £3,771,892.89 -> £3,381,656.95 (10.3%); £3,771,893.07 -> £3,381,656.99 (10.3%); £3,771,893.27 -> £3,381,657.05 (10.3%); £3,771,893.49 -> £3,381,657.10 (10.3%); £3,771,893.72 -> £3,381,657.15 (10.3%); £3,771,893.97 -> £3,381,657.19 (10.3%); £3,771,894.24 -> £3,381,657.24 (10.3%); £3,771,894.50 -> £3,381,657.27 (10.3%); £3,771,894.78 -> £3,381,657.31 (10.3%); £3,771,895.04 -> £3,381,657.31 (10.3%); £3,771,895.30 -> £3,381,657.30 (10.3%); £3,771,895.56 -> £3,381,657.30 (10.3%); £3,771,895.84 -> £3,381,657.30 (10.3%); £3,771,896.11 -> £3,381,657.30 (10.3%); £3,771,896.39 -> £3,381,657.30 (10.3%); £3,771,896.65 -> £3,381,657.30 (10.3%); £3,771,896.91 -> £3,381,657.29 (10.3%); £3,771,897.17 -> £3,381,657.29 (10.3%); £3,771,897.44 -> £3,381,657.29 (10.3%); £3,771,897.71 -> £3,381,657.33 (10.3%); £3,771,897.98 -> £3,381,657.39 (10.3%); £3,771,898.26 -> £3,381,657.45 (10.3%); £3,771,898.53 -> £3,381,657.52 (10.3%); £3,771,898.80 -> £3,381,657.59 (10.3%); £3,771,899.00 -> £3,381,657.66 (10.3%); £3,771,899.26 -> £3,381,657.74 (10.3%); £3,771,899.54 -> £3,381,657.82 (10.3%); £3,771,899.80 -> £3,381,657.80 (10.3%); £3,771,900.08 -> £3,381,657.78 (10.3%); £3,771,900.35 -> £3,381,657.75 (10.3%); £3,771,900.62 -> £3,381,657.73 (10.3%); £3,771,900.88 -> £3,381,657.72 (10.3%); £3,771,901.15 -> £3,381,657.72 (10.3%); £3,771,901.39 -> £3,381,657.71 (10.3%); £3,771,901.62 -> £3,381,657.71 (10.3%); £3,771,901.83 -> £3,381,657.71 (10.3%); £3,771,901.99 -> £3,381,657.71 (10.3%); £3,771,902.15 -> £3,381,657.71 (10.3%); £3,771,902.31 -> £3,381,657.71 (10.3%); £3,771,902.47 -> £3,381,657.71 (10.3%); £3,771,902.62 -> £3,381,657.72 (10.3%); £3,771,902.79 -> £3,381,657.72 (10.3%); £3,771,902.95 -> £3,381,657.72 (10.3%); £3,771,903.11 -> £3,381,657.72 (10.3%); £3,771,903.27 -> £3,381,657.73 (10.3%); £3,771,903.43 -> £3,381,657.73 (10.3%); £3,771,903.59 -> £3,381,657.73 (10.3%); £3,771,903.75 -> £3,381,657.73 (10.3%); £3,771,903.91 -> £3,381,657.72 (10.3%); £3,771,904.08 -> £3,381,657.77 (10.3%); £3,771,904.29 -> £3,381,657.82 (10.3%); £3,771,904.50 -> £3,381,657.87 (10.3%); £3,771,904.73 -> £3,381,657.92 (10.3%); £3,771,904.98 -> £3,381,657.97 (10.3%); £3,771,905.25 -> £3,381,658.01 (10.3%); £3,771,905.51 -> £3,381,658.05 (10.3%); £3,771,905.77 -> £3,381,658.08 (10.3%); £3,771,906.03 -> £3,381,658.08 (10.3%); £3,771,906.28 -> £3,381,658.08 (10.3%); £3,771,906.55 -> £3,381,658.08 (10.3%); £3,771,906.81 -> £3,381,658.08 (10.3%); £3,771,907.07 -> £3,381,658.07 (10.3%); £3,771,907.35 -> £3,381,658.07 (10.3%); £3,771,907.62 -> £3,381,658.07 (10.3%); £3,771,907.88 -> £3,381,658.07 (10.3%); £3,771,908.15 -> £3,381,658.07 (10.3%); £3,771,908.42 -> £3,381,658.07 (10.3%); £3,771,908.67 -> £3,381,658.11 (10.3%); £3,771,908.94 -> £3,381,658.17 (10.3%); £3,771,909.19 -> £3,381,658.23 (10.3%); £3,771,909.40 -> £3,381,658.30 (10.3%); £3,771,909.60 -> £3,381,658.37 (10.3%); £3,771,909.79 -> £3,381,658.43 (10.3%); £3,771,910.00 -> £3,381,658.52 (10.3%); £3,771,910.20 -> £3,381,658.60 (10.3%); £3,771,910.46 -> £3,381,658.57 (10.3%); £3,771,910.73 -> £3,381,658.55 (10.3%); £3,771,911.00 -> £3,381,658.53 (10.3%); £3,771,911.26 -> £3,381,658.50 (10.3%); £3,771,911.53 -> £3,381,658.50 (10.3%); £3,771,911.79 -> £3,381,658.49 (10.3%); £3,771,912.04 -> £3,381,658.49 (10.3%); £3,771,912.25 -> £3,381,658.48 (10.3%); £3,771,912.46 -> £3,381,658.48 (10.3%); £3,771,912.60 -> £3,381,658.48 (10.3%); £3,771,912.74 -> £3,381,658.48 (10.3%); £3,771,912.88 -> £3,381,658.48 (10.3%); £3,771,913.02 -> £3,381,658.48 (10.3%); £3,771,913.16 -> £3,381,658.48 (10.3%); £3,771,913.30 -> £3,381,658.49 (10.3%); £3,771,913.44 -> £3,381,658.49 (10.3%); £3,771,913.58 -> £3,381,658.49 (10.3%); £3,771,913.72 -> £3,381,658.49 (10.3%); £3,771,913.86 -> £3,381,658.49 (10.3%); £3,771,914.01 -> £3,381,658.50 (10.3%); £3,771,914.15 -> £3,381,658.49 (10.3%); £3,771,914.29 -> £3,381,658.49 (10.3%); £3,771,914.44 -> £3,381,658.49 (10.3%); £3,771,914.61 -> £3,381,658.48 (10.3%); £3,771,914.80 -> £3,381,658.48 (10.3%); £3,771,915.01 -> £3,381,658.47 (10.3%); £3,771,915.23 -> £3,381,658.46 (10.3%); £3,771,915.47 -> £3,381,658.45 (10.3%); £3,771,915.70 -> £3,381,658.45 (10.3%); £3,771,915.94 -> £3,381,658.44 (10.3%); £3,771,916.17 -> £3,381,658.44 (10.3%); £3,771,916.40 -> £3,381,658.44 (10.3%); £3,771,916.64 -> £3,381,658.43 (10.3%); £3,771,916.87 -> £3,381,658.43 (10.3%); £3,771,917.10 -> £3,381,658.42 (10.3%); £3,771,917.33 -> £3,381,658.42 (10.3%); £3,771,917.57 -> £3,381,658.42 (10.3%); £3,771,917.80 -> £3,381,658.41 (10.3%); £3,771,918.05 -> £3,381,658.41 (10.3%); £3,771,918.29 -> £3,381,658.41 (10.3%); £3,771,918.53 -> £3,381,658.41 (10.3%); £3,771,918.70 -> £3,381,658.40 (10.3%); £3,771,918.88 -> £3,381,658.38 (10.3%); £3,771,919.05 -> £3,381,658.36 (10.3%); £3,771,919.23 -> £3,381,658.34 (10.3%); £3,771,919.40 -> £3,381,658.32 (10.3%); £3,771,919.58 -> £3,381,658.29 (10.3%); £3,771,919.76 -> £3,381,658.27 (10.3%); £3,771,920.00 -> £3,381,658.24 (10.3%); £3,771,920.24 -> £3,381,658.22 (10.3%); £3,771,920.47 -> £3,381,658.20 (10.3%); £3,771,920.71 -> £3,381,658.18 (10.3%); £3,771,920.94 -> £3,381,658.17 (10.3%); £3,771,921.17 -> £3,381,658.17 (10.3%); £3,771,921.39 -> £3,381,658.16 (10.3%); £3,771,921.59 -> £3,381,658.15 (10.3%); £3,771,921.77 -> £3,381,658.15 (10.3%); £3,771,921.92 -> £3,381,658.15 (10.3%); £3,771,922.06 -> £3,381,658.15 (10.3%); £3,771,922.20 -> £3,381,658.15 (10.3%); £3,771,922.34 -> £3,381,658.15 (10.3%); £3,771,922.48 -> £3,381,658.15 (10.3%); £3,771,922.62 -> £3,381,658.15 (10.3%); £3,771,922.75 -> £3,381,658.15 (10.3%); £3,771,922.89 -> £3,381,658.16 (10.3%); £3,771,923.04 -> £3,381,658.16 (10.3%); £3,771,923.17 -> £3,381,658.16 (10.3%); £3,771,923.31 -> £3,381,658.16 (10.3%); £3,771,923.46 -> £3,381,658.16 (10.3%); £3,771,923.60 -> £3,381,658.16 (10.3%); £3,771,923.75 -> £3,381,658.16 (10.3%); £3,771,923.92 -> £3,381,658.16 (10.3%); £3,771,924.11 -> £3,381,658.15 (10.3%); £3,771,924.31 -> £3,381,658.15 (10.3%); £3,771,924.53 -> £3,381,658.14 (10.3%); £3,771,924.76 -> £3,381,658.13 (10.3%); £3,771,925.00 -> £3,381,658.12 (10.3%); £3,771,925.24 -> £3,381,658.11 (10.3%); £3,771,925.48 -> £3,381,658.11 (10.3%); £3,771,925.71 -> £3,381,658.10 (10.3%); £3,771,925.94 -> £3,381,658.09 (10.3%); £3,771,926.18 -> £3,381,658.08 (10.3%); £3,771,926.41 -> £3,381,658.07 (10.3%); £3,771,926.65 -> £3,381,658.06 (10.3%); £3,771,926.88 -> £3,381,658.06 (10.3%); £3,771,927.11 -> £3,381,658.05 (10.3%); £3,771,927.34 -> £3,381,658.04 (10.3%); £3,771,927.58 -> £3,381,658.04 (10.3%); £3,771,927.81 -> £3,381,658.04 (10.3%); £3,771,927.99 -> £3,381,658.03 (10.3%); £3,771,928.16 -> £3,381,658.01 (10.3%); £3,771,928.35 -> £3,381,657.99 (10.3%); £3,771,928.52 -> £3,381,657.97 (10.3%); £3,771,928.76 -> £3,381,657.95 (10.3%); £3,771,928.99 -> £3,381,657.92 (10.3%); £3,771,929.17 -> £3,381,657.90 (10.3%); £3,771,929.40 -> £3,381,657.87 (10.3%); £3,771,929.63 -> £3,381,657.85 (10.3%); £3,771,929.86 -> £3,381,657.83 (10.3%); £3,771,930.09 -> £3,381,657.80 (10.3%); £3,771,930.33 -> £3,381,657.80 (10.3%); £3,771,930.56 -> £3,381,657.79 (10.3%); £3,771,930.78 -> £3,381,657.79 (10.3%); £3,771,930.98 -> £3,381,657.78 (10.3%); £3,771,931.15 -> £3,381,657.78 (10.3%); £3,771,931.31 -> £3,381,657.78 (10.3%); £3,771,931.47 -> £3,381,657.78 (10.3%); £3,771,931.63 -> £3,381,657.79 (10.3%); £3,771,931.79 -> £3,381,657.79 (10.3%); £3,771,931.95 -> £3,381,657.79 (10.3%); £3,771,932.11 -> £3,381,657.79 (10.3%); £3,771,932.27 -> £3,381,657.79 (10.3%); £3,771,932.43 -> £3,381,657.80 (10.3%); £3,771,932.59 -> £3,381,657.80 (10.3%); £3,771,932.75 -> £3,381,657.80 (10.3%); £3,771,932.91 -> £3,381,657.80 (10.3%); £3,771,933.07 -> £3,381,657.80 (10.3%); £3,771,933.23 -> £3,381,657.79 (10.3%); £3,771,933.40 -> £3,381,657.84 (10.3%); £3,771,933.60 -> £3,381,657.89 (10.3%); £3,771,933.82 -> £3,381,657.94 (10.3%); £3,771,934.05 -> £3,381,657.99 (10.3%); £3,771,934.29 -> £3,381,658.04 (10.3%); £3,771,934.55 -> £3,381,658.08 (10.3%); £3,771,934.81 -> £3,381,658.12 (10.3%); £3,771,935.08 -> £3,381,658.15 (10.3%); £3,771,935.35 -> £3,381,658.15 (10.3%); £3,771,935.61 -> £3,381,658.15 (10.3%); £3,771,935.88 -> £3,381,658.15 (10.3%); £3,771,936.13 -> £3,381,658.15 (10.3%); £3,771,936.39 -> £3,381,658.15 (10.3%); £3,771,936.67 -> £3,381,658.15 (10.3%); £3,771,936.94 -> £3,381,658.15 (10.3%); £3,771,937.20 -> £3,381,658.15 (10.3%); £3,771,937.46 -> £3,381,658.14 (10.3%); £3,771,937.72 -> £3,381,658.15 (10.3%); £3,771,937.98 -> £3,381,658.18 (10.3%); £3,771,938.25 -> £3,381,658.24 (10.3%); £3,771,938.52 -> £3,381,658.31 (10.3%); £3,771,938.78 -> £3,381,658.37 (10.3%); £3,771,939.05 -> £3,381,658.44 (10.3%); £3,771,939.31 -> £3,381,658.51 (10.3%); £3,771,939.56 -> £3,381,658.59 (10.3%); £3,771,939.76 -> £3,381,658.67 (10.3%); £3,771,940.02 -> £3,381,658.65 (10.3%); £3,771,940.28 -> £3,381,658.63 (10.3%); £3,771,940.54 -> £3,381,658.60 (10.3%); £3,771,940.79 -> £3,381,658.58 (10.3%); £3,771,941.05 -> £3,381,658.58 (10.3%); £3,771,941.31 -> £3,381,658.57 (10.3%); £3,771,941.57 -> £3,381,658.57 (10.3%); £3,771,941.79 -> £3,381,658.56 (10.3%); £3,771,942.00 -> £3,381,658.56 (10.3%); £3,771,942.15 -> £3,381,658.56 (10.3%); £3,771,942.31 -> £3,381,658.56 (10.3%); £3,771,942.47 -> £3,381,658.56 (10.3%); £3,771,942.62 -> £3,381,658.57 (10.3%); £3,771,942.78 -> £3,381,658.57 (10.3%); £3,771,942.94 -> £3,381,658.57 (10.3%); £3,771,943.09 -> £3,381,658.57 (10.3%); £3,771,943.25 -> £3,381,658.57 (10.3%); £3,771,943.41 -> £3,381,658.58 (10.3%); £3,771,943.56 -> £3,381,658.58 (10.3%); £3,771,943.71 -> £3,381,658.58 (10.3%); £3,771,943.88 -> £3,381,658.58 (10.3%); £3,771,944.03 -> £3,381,658.57 (10.3%); £3,771,944.21 -> £3,381,658.62 (10.3%); £3,771,944.40 -> £3,381,658.67 (10.3%); £3,771,944.61 -> £3,381,658.72 (10.3%); £3,771,944.84 -> £3,381,658.77 (10.3%); £3,771,945.09 -> £3,381,658.82 (10.3%); £3,771,945.35 -> £3,381,658.86 (10.3%); £3,771,945.60 -> £3,381,658.90 (10.3%); £3,771,945.86 -> £3,381,658.93 (10.3%); £3,771,946.12 -> £3,381,658.93 (10.3%); £3,771,946.37 -> £3,381,658.93 (10.3%); £3,771,946.63 -> £3,381,658.93 (10.3%); £3,771,946.89 -> £3,381,658.93 (10.3%); £3,771,947.16 -> £3,381,658.93 (10.3%); £3,771,947.42 -> £3,381,658.93 (10.3%); £3,771,947.67 -> £3,381,658.93 (10.3%); £3,771,947.95 -> £3,381,658.93 (10.3%); £3,771,948.20 -> £3,381,658.92 (10.3%); £3,771,948.45 -> £3,381,658.93 (10.3%); £3,771,948.72 -> £3,381,658.96 (10.3%); £3,771,948.99 -> £3,381,659.02 (10.3%); £3,771,949.25 -> £3,381,659.08 (10.3%); £3,771,949.44 -> £3,381,659.15 (10.3%); £3,771,949.64 -> £3,381,659.22 (10.3%); £3,771,949.84 -> £3,381,659.28 (10.3%); £3,771,950.04 -> £3,381,659.37 (10.3%); £3,771,950.30 -> £3,381,659.45 (10.3%); £3,771,950.55 -> £3,381,659.42 (10.3%); £3,771,950.83 -> £3,381,659.40 (10.3%); £3,771,951.09 -> £3,381,659.38 (10.3%); £3,771,951.35 -> £3,381,659.36 (10.3%); £3,771,951.61 -> £3,381,659.35 (10.3%); £3,771,951.87 -> £3,381,659.35 (10.3%); £3,771,952.11 -> £3,381,659.34 (10.3%); £3,771,952.34 -> £3,381,659.34 (10.3%); £3,771,952.54 -> £3,381,659.34 (10.3%); £3,771,952.70 -> £3,381,659.34 (10.3%); £3,771,952.86 -> £3,381,659.34 (10.3%); £3,771,953.01 -> £3,381,659.34 (10.3%); £3,771,953.17 -> £3,381,659.34 (10.3%); £3,771,953.33 -> £3,381,659.34 (10.3%); £3,771,953.49 -> £3,381,659.34 (10.3%); £3,771,953.64 -> £3,381,659.35 (10.3%); £3,771,953.80 -> £3,381,659.35 (10.3%); £3,771,953.96 -> £3,381,659.35 (10.3%); £3,771,954.12 -> £3,381,659.35 (10.3%); £3,771,954.27 -> £3,381,659.35 (10.3%); £3,771,954.43 -> £3,381,659.35 (10.3%); £3,771,954.59 -> £3,381,659.34 (10.3%); £3,771,954.77 -> £3,381,659.39 (10.3%); £3,771,954.96 -> £3,381,659.44 (10.3%); £3,771,955.16 -> £3,381,659.49 (10.3%); £3,771,955.39 -> £3,381,659.54 (10.3%); £3,771,955.63 -> £3,381,659.59 (10.3%); £3,771,955.88 -> £3,381,659.63 (10.3%); £3,771,956.14 -> £3,381,659.67 (10.3%); £3,771,956.40 -> £3,381,659.70 (10.3%); £3,771,956.66 -> £3,381,659.70 (10.3%); £3,771,956.92 -> £3,381,659.70 (10.3%); £3,771,957.19 -> £3,381,659.70 (10.3%); £3,771,957.45 -> £3,381,659.70 (10.3%); £3,771,957.71 -> £3,381,659.70 (10.3%); £3,771,957.98 -> £3,381,659.70 (10.3%); £3,771,958.24 -> £3,381,659.70 (10.3%); £3,771,958.50 -> £3,381,659.70 (10.3%); £3,771,958.76 -> £3,381,659.69 (10.3%); £3,771,959.03 -> £3,381,659.70 (10.3%); £3,771,959.29 -> £3,381,659.73 (10.3%); £3,771,959.48 -> £3,381,659.79 (10.3%); £3,771,959.74 -> £3,381,659.86 (10.3%); £3,771,959.94 -> £3,381,659.92 (10.3%); £3,771,960.15 -> £3,381,659.99 (10.3%); £3,771,960.41 -> £3,381,660.06 (10.3%); £3,771,960.67 -> £3,381,660.14 (10.3%); £3,771,960.87 -> £3,381,660.22 (10.3%); £3,771,961.13 -> £3,381,660.20 (10.3%); £3,771,961.38 -> £3,381,660.17 (10.3%); £3,771,961.65 -> £3,381,660.15 (10.3%); £3,771,961.92 -> £3,381,660.13 (10.3%); £3,771,962.19 -> £3,381,660.12 (10.3%); £3,771,962.45 -> £3,381,660.11 (10.3%); £3,771,962.69 -> £3,381,660.11 (10.3%); £3,771,962.92 -> £3,381,660.11 (10.3%); £3,771,963.12 -> £3,381,660.10 (10.3%); £3,771,963.28 -> £3,381,660.10 (10.3%); £3,771,963.43 -> £3,381,660.11 (10.3%); £3,771,963.59 -> £3,381,660.11 (10.3%); £3,771,963.74 -> £3,381,660.11 (10.3%); £3,771,963.90 -> £3,381,660.11 (10.3%); £3,771,964.06 -> £3,381,660.11 (10.3%); £3,771,964.21 -> £3,381,660.11 (10.3%); £3,771,964.36 -> £3,381,660.12 (10.3%); £3,771,964.52 -> £3,381,660.12 (10.3%); £3,771,964.67 -> £3,381,660.12 (10.3%); £3,771,964.83 -> £3,381,660.12 (10.3%); £3,771,964.98 -> £3,381,660.12 (10.3%); £3,771,965.14 -> £3,381,660.11 (10.3%); £3,771,965.31 -> £3,381,660.16 (10.3%); £3,771,965.50 -> £3,381,660.21 (10.3%); £3,771,965.70 -> £3,381,660.27 (10.3%); £3,771,965.93 -> £3,381,660.31 (10.3%); £3,771,966.17 -> £3,381,660.36 (10.3%); £3,771,966.43 -> £3,381,660.40 (10.3%); £3,771,966.69 -> £3,381,660.44 (10.3%); £3,771,966.95 -> £3,381,660.48 (10.3%); £3,771,967.21 -> £3,381,660.47 (10.3%); £3,771,967.46 -> £3,381,660.47 (10.3%); £3,771,967.72 -> £3,381,660.47 (10.3%); £3,771,967.97 -> £3,381,660.47 (10.3%); £3,771,968.22 -> £3,381,660.47 (10.3%); £3,771,968.48 -> £3,381,660.47 (10.3%); £3,771,968.75 -> £3,381,660.47 (10.3%); £3,771,969.00 -> £3,381,660.47 (10.3%); £3,771,969.25 -> £3,381,660.46 (10.3%); £3,771,969.50 -> £3,381,660.47 (10.3%); £3,771,969.76 -> £3,381,660.50 (10.3%); £3,771,970.02 -> £3,381,660.56 (10.3%); £3,771,970.27 -> £3,381,660.63 (10.3%); £3,771,970.53 -> £3,381,660.69 (10.3%); £3,771,970.72 -> £3,381,660.76 (10.3%); £3,771,970.92 -> £3,381,660.83 (10.3%); £3,771,971.18 -> £3,381,660.91 (10.3%); £3,771,971.37 -> £3,381,660.99 (10.3%); £3,771,971.63 -> £3,381,660.97 (10.3%); £3,771,971.88 -> £3,381,660.94 (10.3%); £3,771,972.14 -> £3,381,660.92 (10.3%); £3,771,972.40 -> £3,381,660.90 (10.3%); £3,771,972.66 -> £3,381,660.89 (10.3%); £3,771,972.92 -> £3,381,660.89 (10.3%); £3,771,973.16 -> £3,381,660.88 (10.3%); £3,771,973.39 -> £3,381,660.88 (10.3%); £3,771,973.59 -> £3,381,660.88 (10.3%); £3,771,973.74 -> £3,381,660.88 (10.3%); £3,771,973.90 -> £3,381,660.88 (10.3%); £3,771,974.05 -> £3,381,660.88 (10.3%); £3,771,974.21 -> £3,381,660.88 (10.3%); £3,771,974.37 -> £3,381,660.88 (10.3%); £3,771,974.53 -> £3,381,660.88 (10.3%); £3,771,974.68 -> £3,381,660.89 (10.3%); £3,771,974.84 -> £3,381,660.89 (10.3%); £3,771,974.99 -> £3,381,660.89 (10.3%); £3,771,975.15 -> £3,381,660.89 (10.3%); £3,771,975.30 -> £3,381,660.89 (10.3%); £3,771,975.45 -> £3,381,660.89 (10.3%); £3,771,975.61 -> £3,381,660.88 (10.3%); £3,771,975.78 -> £3,381,660.93 (10.3%); £3,771,975.97 -> £3,381,660.98 (10.3%); £3,771,976.17 -> £3,381,661.03 (10.3%); £3,771,976.39 -> £3,381,661.08 (10.3%); £3,771,976.62 -> £3,381,661.13 (10.3%); £3,771,976.88 -> £3,381,661.17 (10.3%); £3,771,977.14 -> £3,381,661.21 (10.3%); £3,771,977.41 -> £3,381,661.24 (10.3%); £3,771,977.67 -> £3,381,661.24 (10.3%); £3,771,977.93 -> £3,381,661.24 (10.3%); £3,771,978.19 -> £3,381,661.24 (10.3%); £3,771,978.46 -> £3,381,661.23 (10.3%); £3,771,978.71 -> £3,381,661.23 (10.3%); £3,771,978.97 -> £3,381,661.23 (10.3%); £3,771,979.24 -> £3,381,661.23 (10.3%); £3,771,979.50 -> £3,381,661.23 (10.3%); £3,771,979.76 -> £3,381,661.23 (10.3%); £3,771,980.02 -> £3,381,661.23 (10.3%); £3,771,980.28 -> £3,381,661.27 (10.3%); £3,771,980.53 -> £3,381,661.32 (10.3%); £3,771,980.80 -> £3,381,661.39 (10.3%); £3,771,981.06 -> £3,381,661.46 (10.3%); £3,771,981.32 -> £3,381,661.52 (10.3%); £3,771,981.59 -> £3,381,661.59 (10.3%); £3,771,981.85 -> £3,381,661.67 (10.3%); £3,771,982.12 -> £3,381,661.75 (10.3%); £3,771,982.38 -> £3,381,661.73 (10.3%); £3,771,982.64 -> £3,381,661.70 (10.3%); £3,771,982.90 -> £3,381,661.68 (10.3%); £3,771,983.17 -> £3,381,661.66 (10.3%); £3,771,983.44 -> £3,381,661.65 (10.3%); £3,771,983.69 -> £3,381,661.65 (10.3%); £3,771,983.93 -> £3,381,661.64 (10.3%); £3,771,984.15 -> £3,381,661.64 (10.3%); £3,771,984.35 -> £3,381,661.63 (10.3%); £3,771,984.49 -> £3,381,661.63 (10.3%); £3,771,984.63 -> £3,381,661.63 (10.3%); £3,771,984.76 -> £3,381,661.63 (10.3%); £3,771,984.90 -> £3,381,661.63 (10.3%); £3,771,985.03 -> £3,381,661.64 (10.3%); £3,771,985.17 -> £3,381,661.64 (10.3%); £3,771,985.30 -> £3,381,661.64 (10.3%); £3,771,985.44 -> £3,381,661.64 (10.3%); £3,771,985.58 -> £3,381,661.64 (10.3%); £3,771,985.71 -> £3,381,661.65 (10.3%); £3,771,985.85 -> £3,381,661.65 (10.3%); £3,771,985.99 -> £3,381,661.65 (10.3%); £3,771,986.12 -> £3,381,661.64 (10.3%); £3,771,986.28 -> £3,381,661.64 (10.3%); £3,771,986.45 -> £3,381,661.64 (10.3%); £3,771,986.63 -> £3,381,661.63 (10.3%); £3,771,986.82 -> £3,381,661.62 (10.3%); £3,771,987.04 -> £3,381,661.61 (10.3%); £3,771,987.26 -> £3,381,661.60 (10.3%); £3,771,987.49 -> £3,381,661.60 (10.3%); £3,771,987.71 -> £3,381,661.59 (10.3%); £3,771,987.94 -> £3,381,661.59 (10.3%); £3,771,988.16 -> £3,381,661.59 (10.3%); £3,771,988.38 -> £3,381,661.58 (10.3%); £3,771,988.61 -> £3,381,661.58 (10.3%); £3,771,988.84 -> £3,381,661.57 (10.3%); £3,771,989.07 -> £3,381,661.57 (10.3%); £3,771,989.30 -> £3,381,661.57 (10.3%); £3,771,989.53 -> £3,381,661.57 (10.3%); £3,771,989.75 -> £3,381,661.56 (10.3%); £3,771,989.98 -> £3,381,661.56 (10.3%); £3,771,990.21 -> £3,381,661.56 (10.3%); £3,771,990.43 -> £3,381,661.55 (10.3%); £3,771,990.66 -> £3,381,661.53 (10.3%); £3,771,990.89 -> £3,381,661.52 (10.3%); £3,771,991.11 -> £3,381,661.50 (10.3%); £3,771,991.34 -> £3,381,661.48 (10.3%); £3,771,991.56 -> £3,381,661.45 (10.3%); £3,771,991.79 -> £3,381,661.42 (10.3%); £3,771,992.02 -> £3,381,661.40 (10.3%); £3,771,992.25 -> £3,381,661.38 (10.3%); £3,771,992.48 -> £3,381,661.36 (10.3%); £3,771,992.71 -> £3,381,661.34 (10.3%); £3,771,992.93 -> £3,381,661.33 (10.3%); £3,771,993.15 -> £3,381,661.33 (10.3%); £3,771,993.36 -> £3,381,661.32 (10.3%); £3,771,993.56 -> £3,381,661.32 (10.3%); £3,771,993.73 -> £3,381,661.31 (10.3%); £3,771,993.86 -> £3,381,661.31 (10.3%); £3,771,994.00 -> £3,381,661.31 (10.3%); £3,771,994.13 -> £3,381,661.31 (10.3%); £3,771,994.27 -> £3,381,661.31 (10.3%); £3,771,994.40 -> £3,381,661.31 (10.3%); £3,771,994.54 -> £3,381,661.31 (10.3%); £3,771,994.67 -> £3,381,661.32 (10.3%); £3,771,994.81 -> £3,381,661.32 (10.3%); £3,771,994.95 -> £3,381,661.32 (10.3%); £3,771,995.08 -> £3,381,661.32 (10.3%); £3,771,995.22 -> £3,381,661.32 (10.3%); £3,771,995.35 -> £3,381,661.32 (10.3%); £3,771,995.49 -> £3,381,661.32 (10.3%); £3,771,995.65 -> £3,381,661.32 (10.3%); £3,771,995.81 -> £3,381,661.32 (10.3%); £3,771,995.99 -> £3,381,661.32 (10.3%); £3,771,996.18 -> £3,381,661.31 (10.3%); £3,771,996.40 -> £3,381,661.30 (10.3%); £3,771,996.62 -> £3,381,661.29 (10.3%); £3,771,996.84 -> £3,381,661.28 (10.3%); £3,771,997.07 -> £3,381,661.28 (10.3%); £3,771,997.30 -> £3,381,661.27 (10.3%); £3,771,997.52 -> £3,381,661.26 (10.3%); £3,771,997.74 -> £3,381,661.25 (10.3%); £3,771,997.96 -> £3,381,661.24 (10.3%); £3,771,998.19 -> £3,381,661.23 (10.3%); £3,771,998.42 -> £3,381,661.23 (10.3%); £3,771,998.65 -> £3,381,661.22 (10.3%); £3,771,998.87 -> £3,381,661.21 (10.3%); £3,771,999.10 -> £3,381,661.21 (10.3%); £3,771,999.33 -> £3,381,661.21 (10.3%); £3,771,999.56 -> £3,381,661.20 (10.3%); £3,771,999.80 -> £3,381,661.19 (10.3%); £3,772,000.02 -> £3,381,661.17 (10.3%); £3,772,000.25 -> £3,381,661.15 (10.3%); £3,772,000.47 -> £3,381,661.14 (10.3%); £3,772,000.69 -> £3,381,661.12 (10.3%); £3,772,000.92 -> £3,381,661.09 (10.3%); £3,772,001.14 -> £3,381,661.06 (10.3%); £3,772,001.36 -> £3,381,661.04 (10.3%); £3,772,001.58 -> £3,381,661.01 (10.3%); £3,772,001.81 -> £3,381,660.99 (10.3%); £3,772,002.05 -> £3,381,660.97 (10.3%); £3,772,002.28 -> £3,381,660.96 (10.3%); £3,772,002.51 -> £3,381,660.96 (10.3%); £3,772,002.71 -> £3,381,660.95 (10.3%); £3,772,002.91 -> £3,381,660.95 (10.3%); £3,772,003.08 -> £3,381,660.95 (10.3%); £3,772,003.23 -> £3,381,660.95 (10.3%); £3,772,003.39 -> £3,381,660.95 (10.3%); £3,772,003.54 -> £3,381,660.95 (10.3%); £3,772,003.70 -> £3,381,660.95 (10.3%); £3,772,003.86 -> £3,381,660.95 (10.3%); £3,772,004.01 -> £3,381,660.96 (10.3%); £3,772,004.17 -> £3,381,660.96 (10.3%); £3,772,004.32 -> £3,381,660.96 (10.3%); £3,772,004.47 -> £3,381,660.96 (10.3%); £3,772,004.63 -> £3,381,660.96 (10.3%); £3,772,004.78 -> £3,381,660.96 (10.3%); £3,772,004.94 -> £3,381,660.96 (10.3%); £3,772,005.09 -> £3,381,660.95 (10.3%); £3,772,005.26 -> £3,381,661.00 (10.3%); £3,772,005.45 -> £3,381,661.05 (10.3%); £3,772,005.66 -> £3,381,661.10 (10.3%); £3,772,005.88 -> £3,381,661.15 (10.3%); £3,772,006.13 -> £3,381,661.20 (10.3%); £3,772,006.39 -> £3,381,661.24 (10.3%); £3,772,006.64 -> £3,381,661.28 (10.3%); £3,772,006.91 -> £3,381,661.32 (10.3%); £3,772,007.17 -> £3,381,661.31 (10.3%); £3,772,007.42 -> £3,381,661.31 (10.3%); £3,772,007.68 -> £3,381,661.31 (10.3%); £3,772,007.94 -> £3,381,661.31 (10.3%); £3,772,008.20 -> £3,381,661.31 (10.3%); £3,772,008.46 -> £3,381,661.31 (10.3%); £3,772,008.73 -> £3,381,661.31 (10.3%); £3,772,008.98 -> £3,381,661.31 (10.3%); £3,772,009.24 -> £3,381,661.31 (10.3%); £3,772,009.50 -> £3,381,661.31 (10.3%); £3,772,009.76 -> £3,381,661.34 (10.3%); £3,772,010.01 -> £3,381,661.40 (10.3%); £3,772,010.26 -> £3,381,661.47 (10.3%); £3,772,010.51 -> £3,381,661.53 (10.3%); £3,772,010.77 -> £3,381,661.60 (10.3%); £3,772,011.02 -> £3,381,661.67 (10.3%); £3,772,011.27 -> £3,381,661.75 (10.3%); £3,772,011.54 -> £3,381,661.83 (10.3%); £3,772,011.80 -> £3,381,661.81 (10.3%); £3,772,012.05 -> £3,381,661.78 (10.3%); £3,772,012.31 -> £3,381,661.76 (10.3%); £3,772,012.57 -> £3,381,661.74 (10.3%); £3,772,012.83 -> £3,381,661.73 (10.3%); £3,772,013.09 -> £3,381,661.73 (10.3%); £3,772,013.33 -> £3,381,661.72 (10.3%); £3,772,013.54 -> £3,381,661.72 (10.3%); £3,772,013.74 -> £3,381,661.72 (10.3%); £3,772,013.89 -> £3,381,661.72 (10.3%); £3,772,014.05 -> £3,381,661.72 (10.3%); £3,772,014.20 -> £3,381,661.72 (10.3%); £3,772,014.36 -> £3,381,661.72 (10.3%); £3,772,014.52 -> £3,381,661.72 (10.3%); £3,772,014.67 -> £3,381,661.73 (10.3%); £3,772,014.82 -> £3,381,661.73 (10.3%); £3,772,014.97 -> £3,381,661.73 (10.3%); £3,772,015.12 -> £3,381,661.73 (10.3%); £3,772,015.27 -> £3,381,661.73 (10.3%); £3,772,015.42 -> £3,381,661.74 (10.3%); £3,772,015.58 -> £3,381,661.73 (10.3%); £3,772,015.73 -> £3,381,661.73 (10.3%); £3,772,015.90 -> £3,381,661.77 (10.3%); £3,772,016.09 -> £3,381,661.82 (10.3%); £3,772,016.29 -> £3,381,661.88 (10.3%); £3,772,016.52 -> £3,381,661.92 (10.3%); £3,772,016.76 -> £3,381,661.97 (10.3%); £3,772,017.02 -> £3,381,662.01 (10.3%); £3,772,017.27 -> £3,381,662.05 (10.3%); £3,772,017.53 -> £3,381,662.09 (10.3%); £3,772,017.79 -> £3,381,662.08 (10.3%); £3,772,018.04 -> £3,381,662.08 (10.3%); £3,772,018.29 -> £3,381,662.08 (10.3%); £3,772,018.55 -> £3,381,662.08 (10.3%); £3,772,018.81 -> £3,381,662.08 (10.3%); £3,772,019.06 -> £3,381,662.08 (10.3%); £3,772,019.31 -> £3,381,662.08 (10.3%); £3,772,019.57 -> £3,381,662.08 (10.3%); £3,772,019.82 -> £3,381,662.08 (10.3%); £3,772,020.09 -> £3,381,662.08 (10.3%); £3,772,020.35 -> £3,381,662.11 (10.3%); £3,772,020.61 -> £3,381,662.17 (10.3%); £3,772,020.87 -> £3,381,662.24 (10.3%); £3,772,021.12 -> £3,381,662.30 (10.3%); £3,772,021.38 -> £3,381,662.37 (10.3%); £3,772,021.64 -> £3,381,662.44 (10.3%); £3,772,021.89 -> £3,381,662.52 (10.3%); £3,772,022.15 -> £3,381,662.60 (10.3%); £3,772,022.41 -> £3,381,662.58 (10.3%); £3,772,022.67 -> £3,381,662.55 (10.3%); £3,772,022.91 -> £3,381,662.53 (10.3%); £3,772,023.17 -> £3,381,662.51 (10.3%); £3,772,023.43 -> £3,381,662.50 (10.3%); £3,772,023.70 -> £3,381,662.50 (10.3%); £3,772,023.93 -> £3,381,662.49 (10.3%); £3,772,024.14 -> £3,381,662.49 (10.3%); £3,772,024.34 -> £3,381,662.49 (10.3%); £3,772,024.49 -> £3,381,662.49 (10.3%); £3,772,024.64 -> £3,381,662.49 (10.3%); £3,772,024.79 -> £3,381,662.49 (10.3%); £3,772,024.94 -> £3,381,662.49 (10.3%); £3,772,025.09 -> £3,381,662.49 (10.3%); £3,772,025.24 -> £3,381,662.49 (10.3%); £3,772,025.39 -> £3,381,662.50 (10.3%); £3,772,025.55 -> £3,381,662.50 (10.3%); £3,772,025.70 -> £3,381,662.50 (10.3%); £3,772,025.85 -> £3,381,662.50 (10.3%); £3,772,026.00 -> £3,381,662.50 (10.3%); £3,772,026.16 -> £3,381,662.50 (10.3%); £3,772,026.31 -> £3,381,662.49 (10.3%); £3,772,026.49 -> £3,381,662.54 (10.3%); £3,772,026.67 -> £3,381,662.59 (10.3%); £3,772,026.88 -> £3,381,662.64 (10.3%); £3,772,027.10 -> £3,381,662.69 (10.3%); £3,772,027.34 -> £3,381,662.73 (10.3%); £3,772,027.59 -> £3,381,662.78 (10.3%); £3,772,027.84 -> £3,381,662.82 (10.3%); £3,772,028.09 -> £3,381,662.85 (10.3%); £3,772,028.35 -> £3,381,662.85 (10.3%); £3,772,028.61 -> £3,381,662.85 (10.3%); £3,772,028.87 -> £3,381,662.85 (10.3%); £3,772,029.13 -> £3,381,662.85 (10.3%); £3,772,029.39 -> £3,381,662.84 (10.3%); £3,772,029.65 -> £3,381,662.84 (10.3%); £3,772,029.91 -> £3,381,662.84 (10.3%); £3,772,030.16 -> £3,381,662.84 (10.3%); £3,772,030.41 -> £3,381,662.84 (10.3%); £3,772,030.66 -> £3,381,662.84 (10.3%); £3,772,030.92 -> £3,381,662.88 (10.3%); £3,772,031.18 -> £3,381,662.94 (10.3%); £3,772,031.44 -> £3,381,663.00 (10.3%); £3,772,031.71 -> £3,381,663.07 (10.3%); £3,772,031.97 -> £3,381,663.14 (10.3%); £3,772,032.22 -> £3,381,663.20 (10.3%); £3,772,032.48 -> £3,381,663.29 (10.3%); £3,772,032.73 -> £3,381,663.37 (10.3%); £3,772,032.98 -> £3,381,663.34 (10.3%); £3,772,033.24 -> £3,381,663.32 (10.3%); £3,772,033.50 -> £3,381,663.29 (10.3%); £3,772,033.75 -> £3,381,663.27 (10.3%); £3,772,034.00 -> £3,381,663.27 (10.3%); £3,772,034.26 -> £3,381,663.26 (10.3%); £3,772,034.49 -> £3,381,663.26 (10.3%); £3,772,034.71 -> £3,381,663.25 (10.3%); £3,772,034.91 -> £3,381,663.25 (10.3%); £3,772,035.06 -> £3,381,663.25 (10.3%); £3,772,035.21 -> £3,381,663.26 (10.3%); £3,772,035.37 -> £3,381,663.26 (10.3%); £3,772,035.52 -> £3,381,663.26 (10.3%); £3,772,035.67 -> £3,381,663.26 (10.3%); £3,772,035.82 -> £3,381,663.26 (10.3%); £3,772,035.97 -> £3,381,663.26 (10.3%); £3,772,036.13 -> £3,381,663.27 (10.3%); £3,772,036.28 -> £3,381,663.27 (10.3%); £3,772,036.43 -> £3,381,663.27 (10.3%); £3,772,036.59 -> £3,381,663.27 (10.3%); £3,772,036.74 -> £3,381,663.27 (10.3%); £3,772,036.89 -> £3,381,663.26 (10.3%); £3,772,037.06 -> £3,381,663.31 (10.3%); £3,772,037.24 -> £3,381,663.36 (10.3%); £3,772,037.44 -> £3,381,663.41 (10.3%); £3,772,037.66 -> £3,381,663.46 (10.3%); £3,772,037.90 -> £3,381,663.51 (10.3%); £3,772,038.16 -> £3,381,663.55 (10.3%); £3,772,038.42 -> £3,381,663.59 (10.3%); £3,772,038.69 -> £3,381,663.62 (10.3%); £3,772,038.94 -> £3,381,663.62 (10.3%); £3,772,039.18 -> £3,381,663.62 (10.3%); £3,772,039.44 -> £3,381,663.62 (10.3%); £3,772,039.68 -> £3,381,663.61 (10.3%); £3,772,039.94 -> £3,381,663.61 (10.3%); £3,772,040.20 -> £3,381,663.61 (10.3%); £3,772,040.45 -> £3,381,663.61 (10.3%); £3,772,040.71 -> £3,381,663.61 (10.3%); £3,772,040.97 -> £3,381,663.61 (10.3%); £3,772,041.23 -> £3,381,663.61 (10.3%); £3,772,041.48 -> £3,381,663.64 (10.3%); £3,772,041.73 -> £3,381,663.70 (10.3%); £3,772,041.99 -> £3,381,663.77 (10.3%); £3,772,042.25 -> £3,381,663.84 (10.3%); £3,772,042.50 -> £3,381,663.90 (10.3%); £3,772,042.76 -> £3,381,663.97 (10.3%); £3,772,043.02 -> £3,381,664.06 (10.3%); £3,772,043.27 -> £3,381,664.14 (10.3%); £3,772,043.52 -> £3,381,664.11 (10.3%); £3,772,043.78 -> £3,381,664.09 (10.3%); £3,772,044.04 -> £3,381,664.07 (10.3%); £3,772,044.29 -> £3,381,664.05 (10.3%); £3,772,044.55 -> £3,381,664.04 (10.3%); £3,772,044.79 -> £3,381,664.04 (10.3%); £3,772,045.04 -> £3,381,664.03 (10.3%); £3,772,045.25 -> £3,381,664.03 (10.3%); £3,772,045.45 -> £3,381,664.02 (10.3%); £3,772,045.60 -> £3,381,664.03 (10.3%); £3,772,045.75 -> £3,381,664.03 (10.3%); £3,772,045.91 -> £3,381,664.03 (10.3%); £3,772,046.05 -> £3,381,664.03 (10.3%); £3,772,046.21 -> £3,381,664.03 (10.3%); £3,772,046.36 -> £3,381,664.03 (10.3%); £3,772,046.52 -> £3,381,664.04 (10.3%); £3,772,046.67 -> £3,381,664.04 (10.3%); £3,772,046.82 -> £3,381,664.04 (10.3%); £3,772,046.97 -> £3,381,664.04 (10.3%); £3,772,047.13 -> £3,381,664.04 (10.3%); £3,772,047.28 -> £3,381,664.04 (10.3%); £3,772,047.44 -> £3,381,664.03 (10.3%); £3,772,047.61 -> £3,381,664.08 (10.3%); £3,772,047.79 -> £3,381,664.13 (10.3%); £3,772,047.99 -> £3,381,664.18 (10.3%); £3,772,048.21 -> £3,381,664.23 (10.3%); £3,772,048.45 -> £3,381,664.28 (10.3%); £3,772,048.71 -> £3,381,664.32 (10.3%); £3,772,048.98 -> £3,381,664.36 (10.3%); £3,772,049.23 -> £3,381,664.39 (10.3%); £3,772,049.49 -> £3,381,664.39 (10.3%); £3,772,049.75 -> £3,381,664.39 (10.3%); £3,772,050.00 -> £3,381,664.39 (10.3%); £3,772,050.26 -> £3,381,664.39 (10.3%); £3,772,050.51 -> £3,381,664.38 (10.3%); £3,772,050.76 -> £3,381,664.38 (10.3%); £3,772,051.02 -> £3,381,664.38 (10.3%); £3,772,051.28 -> £3,381,664.38 (10.3%); £3,772,051.53 -> £3,381,664.38 (10.3%); £3,772,051.78 -> £3,381,664.38 (10.3%); £3,772,052.04 -> £3,381,664.42 (10.3%); £3,772,052.30 -> £3,381,664.48 (10.3%); £3,772,052.55 -> £3,381,664.54 (10.3%); £3,772,052.80 -> £3,381,664.61 (10.3%); £3,772,053.05 -> £3,381,664.67 (10.3%); £3,772,053.32 -> £3,381,664.74 (10.3%); £3,772,053.56 -> £3,381,664.82 (10.3%); £3,772,053.81 -> £3,381,664.90 (10.3%); £3,772,054.07 -> £3,381,664.88 (10.3%); £3,772,054.33 -> £3,381,664.85 (10.3%); £3,772,054.58 -> £3,381,664.83 (10.3%); £3,772,054.83 -> £3,381,664.81 (10.3%); £3,772,055.09 -> £3,381,664.80 (10.3%); £3,772,055.35 -> £3,381,664.80 (10.3%); £3,772,055.58 -> £3,381,664.79 (10.3%); £3,772,055.80 -> £3,381,664.79 (10.3%); £3,772,055.99 -> £3,381,664.79 (10.3%); £3,772,056.12 -> £3,381,664.78 (10.3%); £3,772,056.26 -> £3,381,664.78 (10.3%); £3,772,056.39 -> £3,381,664.79 (10.3%); £3,772,056.52 -> £3,381,664.79 (10.3%); £3,772,056.65 -> £3,381,664.79 (10.3%); £3,772,056.79 -> £3,381,664.79 (10.3%); £3,772,056.93 -> £3,381,664.79 (10.3%); £3,772,057.06 -> £3,381,664.80 (10.3%); £3,772,057.19 -> £3,381,664.80 (10.3%); £3,772,057.33 -> £3,381,664.80 (10.3%); £3,772,057.46 -> £3,381,664.80 (10.3%); £3,772,057.59 -> £3,381,664.80 (10.3%); £3,772,057.73 -> £3,381,664.80 (10.3%); £3,772,057.88 -> £3,381,664.79 (10.3%); £3,772,058.05 -> £3,381,664.79 (10.3%); £3,772,058.23 -> £3,381,664.78 (10.3%); £3,772,058.42 -> £3,381,664.77 (10.3%); £3,772,058.63 -> £3,381,664.76 (10.3%); £3,772,058.86 -> £3,381,664.76 (10.3%); £3,772,059.08 -> £3,381,664.75 (10.3%); £3,772,059.31 -> £3,381,664.75 (10.3%); £3,772,059.53 -> £3,381,664.74 (10.3%); £3,772,059.75 -> £3,381,664.74 (10.3%); £3,772,059.98 -> £3,381,664.73 (10.3%); £3,772,060.20 -> £3,381,664.73 (10.3%); £3,772,060.42 -> £3,381,664.72 (10.3%); £3,772,060.64 -> £3,381,664.72 (10.3%); £3,772,060.87 -> £3,381,664.72 (10.3%); £3,772,061.10 -> £3,381,664.72 (10.3%); £3,772,061.33 -> £3,381,664.71 (10.3%); £3,772,061.56 -> £3,381,664.71 (10.3%); £3,772,061.78 -> £3,381,664.71 (10.3%); £3,772,062.01 -> £3,381,664.70 (10.3%); £3,772,062.24 -> £3,381,664.68 (10.3%); £3,772,062.46 -> £3,381,664.67 (10.3%); £3,772,062.69 -> £3,381,664.65 (10.3%); £3,772,062.91 -> £3,381,664.63 (10.3%); £3,772,063.14 -> £3,381,664.60 (10.3%); £3,772,063.36 -> £3,381,664.57 (10.3%); £3,772,063.58 -> £3,381,664.55 (10.3%); £3,772,063.80 -> £3,381,664.53 (10.3%); £3,772,064.02 -> £3,381,664.51 (10.3%); £3,772,064.24 -> £3,381,664.49 (10.3%); £3,772,064.46 -> £3,381,664.48 (10.3%); £3,772,064.68 -> £3,381,664.48 (10.3%); £3,772,064.90 -> £3,381,664.47 (10.3%); £3,772,065.08 -> £3,381,664.47 (10.3%); £3,772,065.26 -> £3,381,664.46 (10.3%); £3,772,065.39 -> £3,381,664.46 (10.3%); £3,772,065.53 -> £3,381,664.46 (10.3%); £3,772,065.66 -> £3,381,664.46 (10.3%); £3,772,065.80 -> £3,381,664.46 (10.3%); £3,772,065.93 -> £3,381,664.46 (10.3%); £3,772,066.07 -> £3,381,664.47 (10.3%); £3,772,066.21 -> £3,381,664.47 (10.3%); £3,772,066.34 -> £3,381,664.47 (10.3%); £3,772,066.48 -> £3,381,664.47 (10.3%); £3,772,066.61 -> £3,381,664.48 (10.3%); £3,772,066.75 -> £3,381,664.48 (10.3%); £3,772,066.88 -> £3,381,664.48 (10.3%); £3,772,067.02 -> £3,381,664.47 (10.3%); £3,772,067.17 -> £3,381,664.48 (10.3%); £3,772,067.33 -> £3,381,664.47 (10.3%); £3,772,067.51 -> £3,381,664.47 (10.3%); £3,772,067.71 -> £3,381,664.46 (10.3%); £3,772,067.91 -> £3,381,664.45 (10.3%); £3,772,068.14 -> £3,381,664.44 (10.3%); £3,772,068.37 -> £3,381,664.43 (10.3%); £3,772,068.60 -> £3,381,664.43 (10.3%); £3,772,068.82 -> £3,381,664.42 (10.3%); £3,772,069.04 -> £3,381,664.41 (10.3%); £3,772,069.27 -> £3,381,664.40 (10.3%); £3,772,069.49 -> £3,381,664.39 (10.3%); £3,772,069.71 -> £3,381,664.38 (10.3%); £3,772,069.93 -> £3,381,664.37 (10.3%); £3,772,070.16 -> £3,381,664.37 (10.3%); £3,772,070.39 -> £3,381,664.36 (10.3%); £3,772,070.61 -> £3,381,664.35 (10.3%); £3,772,070.84 -> £3,381,664.35 (10.3%); £3,772,071.05 -> £3,381,664.35 (10.3%); £3,772,071.28 -> £3,381,664.34 (10.3%); £3,772,071.51 -> £3,381,664.32 (10.3%); £3,772,071.74 -> £3,381,664.30 (10.3%); £3,772,071.96 -> £3,381,664.28 (10.3%); £3,772,072.18 -> £3,381,664.26 (10.3%); £3,772,072.39 -> £3,381,664.23 (10.3%); £3,772,072.61 -> £3,381,664.21 (10.3%); £3,772,072.83 -> £3,381,664.18 (10.3%); £3,772,073.06 -> £3,381,664.16 (10.3%); £3,772,073.28 -> £3,381,664.13 (10.3%); £3,772,073.51 -> £3,381,664.11 (10.3%); £3,772,073.73 -> £3,381,664.10 (10.3%); £3,772,073.95 -> £3,381,664.10 (10.4%); £3,772,074.17 -> £3,381,664.09 (10.4%); £3,772,074.36 -> £3,381,664.09 (10.4%); £3,772,074.53 -> £3,381,664.09 (10.4%); £3,772,074.68 -> £3,381,664.09 (10.4%); £3,772,074.83 -> £3,381,664.09 (10.4%); £3,772,074.99 -> £3,381,664.09 (10.4%); £3,772,075.14 -> £3,381,664.09 (10.4%); £3,772,075.29 -> £3,381,664.09 (10.4%); £3,772,075.45 -> £3,381,664.10 (10.4%); £3,772,075.59 -> £3,381,664.10 (10.4%); £3,772,075.75 -> £3,381,664.10 (10.4%); £3,772,075.90 -> £3,381,664.10 (10.4%); £3,772,076.05 -> £3,381,664.10 (10.4%); £3,772,076.20 -> £3,381,664.11 (10.4%); £3,772,076.35 -> £3,381,664.10 (10.4%); £3,772,076.49 -> £3,381,664.10 (10.4%); £3,772,076.67 -> £3,381,664.14 (10.4%); £3,772,076.86 -> £3,381,664.19 (10.4%); £3,772,077.07 -> £3,381,664.25 (10.4%); £3,772,077.28 -> £3,381,664.29 (10.4%); £3,772,077.52 -> £3,381,664.34 (10.4%); £3,772,077.77 -> £3,381,664.38 (10.4%); £3,772,078.02 -> £3,381,664.42 (10.4%); £3,772,078.27 -> £3,381,664.45 (10.4%); £3,772,078.53 -> £3,381,664.45 (10.4%); £3,772,078.79 -> £3,381,664.45 (10.4%); £3,772,079.04 -> £3,381,664.45 (10.4%); £3,772,079.30 -> £3,381,664.45 (10.4%); £3,772,079.55 -> £3,381,664.45 (10.4%); £3,772,079.79 -> £3,381,664.44 (10.4%); £3,772,080.04 -> £3,381,664.44 (10.4%); £3,772,080.30 -> £3,381,664.44 (10.4%); £3,772,080.56 -> £3,381,664.44 (10.4%); £3,772,080.81 -> £3,381,664.44 (10.4%); £3,772,081.06 -> £3,381,664.48 (10.4%); £3,772,081.32 -> £3,381,664.53 (10.4%); £3,772,081.57 -> £3,381,664.60 (10.4%); £3,772,081.82 -> £3,381,664.66 (10.4%); £3,772,082.09 -> £3,381,664.73 (10.4%); £3,772,082.34 -> £3,381,664.79 (10.4%); £3,772,082.59 -> £3,381,664.88 (10.4%); £3,772,082.84 -> £3,381,664.96 (10.4%); £3,772,083.08 -> £3,381,664.94 (10.4%); £3,772,083.34 -> £3,381,664.91 (10.4%); £3,772,083.59 -> £3,381,664.89 (10.4%); £3,772,083.85 -> £3,381,664.87 (10.4%); £3,772,084.11 -> £3,381,664.86 (10.4%); £3,772,084.36 -> £3,381,664.86 (10.4%); £3,772,084.59 -> £3,381,664.85 (10.4%); £3,772,084.80 -> £3,381,664.85 (10.4%); £3,772,085.00 -> £3,381,664.85 (10.4%); £3,772,085.15 -> £3,381,664.85 (10.4%); £3,772,085.29 -> £3,381,664.85 (10.4%); £3,772,085.44 -> £3,381,664.85 (10.4%); £3,772,085.59 -> £3,381,664.85 (10.4%); £3,772,085.75 -> £3,381,664.85 (10.4%); £3,772,085.90 -> £3,381,664.86 (10.4%); £3,772,086.05 -> £3,381,664.86 (10.4%); £3,772,086.20 -> £3,381,664.86 (10.4%); £3,772,086.35 -> £3,381,664.86 (10.4%); £3,772,086.49 -> £3,381,664.86 (10.4%); £3,772,086.64 -> £3,381,664.87 (10.4%); £3,772,086.79 -> £3,381,664.86 (10.4%); £3,772,086.94 -> £3,381,664.86 (10.4%); £3,772,087.11 -> £3,381,664.90 (10.4%); £3,772,087.30 -> £3,381,664.95 (10.4%); £3,772,087.51 -> £3,381,665.01 (10.4%); £3,772,087.72 -> £3,381,665.06 (10.4%); £3,772,087.95 -> £3,381,665.10 (10.4%); £3,772,088.21 -> £3,381,665.15 (10.4%); £3,772,088.46 -> £3,381,665.18 (10.4%); £3,772,088.70 -> £3,381,665.22 (10.4%); £3,772,088.96 -> £3,381,665.22 (10.4%); £3,772,089.22 -> £3,381,665.21 (10.4%); £3,772,089.47 -> £3,381,665.21 (10.4%); £3,772,089.71 -> £3,381,665.21 (10.4%); £3,772,089.96 -> £3,381,665.21 (10.4%); £3,772,090.21 -> £3,381,665.21 (10.4%); £3,772,090.47 -> £3,381,665.21 (10.4%); £3,772,090.72 -> £3,381,665.21 (10.4%); £3,772,090.97 -> £3,381,665.21 (10.4%); £3,772,091.23 -> £3,381,665.21 (10.4%); £3,772,091.48 -> £3,381,665.24 (10.4%); £3,772,091.74 -> £3,381,665.30 (10.4%); £3,772,091.99 -> £3,381,665.37 (10.4%); £3,772,092.25 -> £3,381,665.43 (10.4%); £3,772,092.51 -> £3,381,665.50 (10.4%); £3,772,092.76 -> £3,381,665.57 (10.4%); £3,772,093.02 -> £3,381,665.65 (10.4%); £3,772,093.27 -> £3,381,665.73 (10.4%); £3,772,093.52 -> £3,381,665.71 (10.4%); £3,772,093.77 -> £3,381,665.68 (10.4%); £3,772,094.01 -> £3,381,665.66 (10.4%); £3,772,094.26 -> £3,381,665.64 (10.4%); £3,772,094.51 -> £3,381,665.63 (10.4%); £3,772,094.75 -> £3,381,665.63 (10.4%); £3,772,094.99 -> £3,381,665.62 (10.4%); £3,772,095.21 -> £3,381,665.62 (10.4%); £3,772,095.40 -> £3,381,665.62 (10.4%); £3,772,095.55 -> £3,381,665.62 (10.4%); £3,772,095.71 -> £3,381,665.62 (10.4%); £3,772,095.86 -> £3,381,665.62 (10.4%); £3,772,096.01 -> £3,381,665.62 (10.4%); £3,772,096.16 -> £3,381,665.62 (10.4%); £3,772,096.31 -> £3,381,665.62 (10.4%); £3,772,096.47 -> £3,381,665.63 (10.4%); £3,772,096.61 -> £3,381,665.63 (10.4%); £3,772,096.77 -> £3,381,665.63 (10.4%); £3,772,096.92 -> £3,381,665.63 (10.4%); £3,772,097.07 -> £3,381,665.63 (10.4%); £3,772,097.22 -> £3,381,665.63 (10.4%); £3,772,097.37 -> £3,381,665.62 (10.4%); £3,772,097.54 -> £3,381,665.67 (10.4%); £3,772,097.72 -> £3,381,665.72 (10.4%); £3,772,097.92 -> £3,381,665.77 (10.4%); £3,772,098.14 -> £3,381,665.82 (10.4%); £3,772,098.38 -> £3,381,665.87 (10.4%); £3,772,098.62 -> £3,381,665.91 (10.4%); £3,772,098.87 -> £3,381,665.95 (10.4%); £3,772,099.12 -> £3,381,665.99 (10.4%); £3,772,099.38 -> £3,381,665.99 (10.4%); £3,772,099.64 -> £3,381,665.98 (10.4%); £3,772,099.88 -> £3,381,665.98 (10.4%); £3,772,100.13 -> £3,381,665.98 (10.4%); £3,772,100.39 -> £3,381,665.98 (10.4%); £3,772,100.64 -> £3,381,665.98 (10.4%); £3,772,100.89 -> £3,381,665.98 (10.4%); £3,772,101.13 -> £3,381,665.98 (10.4%); £3,772,101.38 -> £3,381,665.98 (10.4%); £3,772,101.63 -> £3,381,665.98 (10.4%); £3,772,101.88 -> £3,381,666.01 (10.4%); £3,772,102.13 -> £3,381,666.07 (10.4%); £3,772,102.38 -> £3,381,666.14 (10.4%); £3,772,102.63 -> £3,381,666.20 (10.4%); £3,772,102.88 -> £3,381,666.27 (10.4%); £3,772,103.12 -> £3,381,666.34 (10.4%); £3,772,103.37 -> £3,381,666.42 (10.4%); £3,772,103.62 -> £3,381,666.50 (10.4%); £3,772,103.87 -> £3,381,666.48 (10.4%); £3,772,104.12 -> £3,381,666.45 (10.4%); £3,772,104.36 -> £3,381,666.43 (10.4%); £3,772,104.61 -> £3,381,666.41 (10.4%); £3,772,104.86 -> £3,381,666.40 (10.4%); £3,772,105.11 -> £3,381,666.40 (10.4%); £3,772,105.35 -> £3,381,666.39 (10.4%); £3,772,105.56 -> £3,381,666.39 (10.4%); £3,772,105.76 -> £3,381,666.39 (10.4%); £3,772,105.91 -> £3,381,666.39 (10.4%); £3,772,106.06 -> £3,381,666.39 (10.4%); £3,772,106.21 -> £3,381,666.39 (10.4%); £3,772,106.37 -> £3,381,666.39 (10.4%); £3,772,106.51 -> £3,381,666.39 (10.4%); £3,772,106.66 -> £3,381,666.40 (10.4%); £3,772,106.82 -> £3,381,666.40 (10.4%); £3,772,106.97 -> £3,381,666.40 (10.4%); £3,772,107.12 -> £3,381,666.40 (10.4%); £3,772,107.27 -> £3,381,666.40 (10.4%); £3,772,107.42 -> £3,381,666.41 (10.4%); £3,772,107.57 -> £3,381,666.40 (10.4%); £3,772,107.72 -> £3,381,666.40 (10.4%); £3,772,107.88 -> £3,381,666.44 (10.4%); £3,772,108.06 -> £3,381,666.49 (10.4%); £3,772,108.26 -> £3,381,666.55 (10.4%); £3,772,108.48 -> £3,381,666.59 (10.4%); £3,772,108.71 -> £3,381,666.64 (10.4%); £3,772,108.97 -> £3,381,666.68 (10.4%); £3,772,109.22 -> £3,381,666.72 (10.4%); £3,772,109.47 -> £3,381,666.76 (10.4%); £3,772,109.73 -> £3,381,666.75 (10.4%); £3,772,109.98 -> £3,381,666.75 (10.4%); £3,772,110.23 -> £3,381,666.75 (10.4%); £3,772,110.48 -> £3,381,666.75 (10.4%); £3,772,110.73 -> £3,381,666.75 (10.4%); £3,772,110.98 -> £3,381,666.75 (10.4%); £3,772,111.24 -> £3,381,666.75 (10.4%); £3,772,111.49 -> £3,381,666.75 (10.4%); £3,772,111.74 -> £3,381,666.74 (10.4%); £3,772,112.00 -> £3,381,666.74 (10.4%); £3,772,112.25 -> £3,381,666.78 (10.4%); £3,772,112.50 -> £3,381,666.84 (10.4%); £3,772,112.76 -> £3,381,666.90 (10.4%); £3,772,113.02 -> £3,381,666.97 (10.4%); £3,772,113.27 -> £3,381,667.04 (10.4%); £3,772,113.53 -> £3,381,667.10 (10.4%); £3,772,113.78 -> £3,381,667.19 (10.4%); £3,772,114.03 -> £3,381,667.27 (10.4%); £3,772,114.28 -> £3,381,667.24 (10.4%); £3,772,114.53 -> £3,381,667.22 (10.4%); £3,772,114.78 -> £3,381,667.19 (10.4%); £3,772,115.03 -> £3,381,667.17 (10.4%); £3,772,115.29 -> £3,381,667.16 (10.4%); £3,772,115.54 -> £3,381,667.16 (10.4%); £3,772,115.77 -> £3,381,667.15 (10.4%); £3,772,115.98 -> £3,381,667.15 (10.4%); £3,772,116.18 -> £3,381,667.15 (10.4%); £3,772,116.33 -> £3,381,667.15 (10.4%); £3,772,116.48 -> £3,381,667.15 (10.4%); £3,772,116.63 -> £3,381,667.15 (10.4%); £3,772,116.78 -> £3,381,667.16 (10.4%); £3,772,116.94 -> £3,381,667.16 (10.4%); £3,772,117.09 -> £3,381,667.16 (10.4%); £3,772,117.24 -> £3,381,667.16 (10.4%); £3,772,117.40 -> £3,381,667.17 (10.4%); £3,772,117.55 -> £3,381,667.17 (10.4%); £3,772,117.70 -> £3,381,667.17 (10.4%); £3,772,117.85 -> £3,381,667.17 (10.4%); £3,772,118.00 -> £3,381,667.17 (10.4%); £3,772,118.14 -> £3,381,667.16 (10.4%); £3,772,118.31 -> £3,381,667.21 (10.4%); £3,772,118.50 -> £3,381,667.26 (10.4%); £3,772,118.70 -> £3,381,667.32 (10.4%); £3,772,118.92 -> £3,381,667.37 (10.4%); £3,772,119.16 -> £3,381,667.41 (10.4%); £3,772,119.41 -> £3,381,667.46 (10.4%); £3,772,119.67 -> £3,381,667.49 (10.4%); £3,772,119.91 -> £3,381,667.53 (10.4%); £3,772,120.16 -> £3,381,667.53 (10.4%); £3,772,120.42 -> £3,381,667.53 (10.4%); £3,772,120.66 -> £3,381,667.53 (10.4%); £3,772,120.91 -> £3,381,667.53 (10.4%); £3,772,121.17 -> £3,381,667.53 (10.4%); £3,772,121.41 -> £3,381,667.53 (10.4%); £3,772,121.67 -> £3,381,667.53 (10.4%); £3,772,121.93 -> £3,381,667.53 (10.4%); £3,772,122.18 -> £3,381,667.52 (10.4%); £3,772,122.43 -> £3,381,667.53 (10.4%); £3,772,122.68 -> £3,381,667.56 (10.4%); £3,772,122.93 -> £3,381,667.62 (10.4%); £3,772,123.18 -> £3,381,667.68 (10.4%); £3,772,123.43 -> £3,381,667.75 (10.4%); £3,772,123.69 -> £3,381,667.82 (10.4%); £3,772,123.94 -> £3,381,667.89 (10.4%); £3,772,124.19 -> £3,381,667.97 (10.4%); £3,772,124.43 -> £3,381,668.05 (10.4%); £3,772,124.69 -> £3,381,668.02 (10.4%); £3,772,124.94 -> £3,381,668.00 (10.4%); £3,772,125.20 -> £3,381,667.98 (10.4%); £3,772,125.45 -> £3,381,667.96 (10.4%); £3,772,125.71 -> £3,381,667.95 (10.4%); £3,772,125.96 -> £3,381,667.94 (10.4%); £3,772,126.19 -> £3,381,667.94 (10.4%); £3,772,126.40 -> £3,381,667.94 (10.4%); £3,772,126.59 -> £3,381,667.93 (10.4%); £3,772,126.72 -> £3,381,667.93 (10.4%); £3,772,126.86 -> £3,381,667.93 (10.4%); £3,772,126.99 -> £3,381,667.93 (10.4%); £3,772,127.13 -> £3,381,667.93 (10.4%); £3,772,127.26 -> £3,381,667.94 (10.4%); £3,772,127.40 -> £3,381,667.94 (10.4%); £3,772,127.53 -> £3,381,667.94 (10.4%); £3,772,127.67 -> £3,381,667.94 (10.4%); £3,772,127.80 -> £3,381,667.94 (10.4%); £3,772,127.94 -> £3,381,667.95 (10.4%); £3,772,128.08 -> £3,381,667.95 (10.4%); £3,772,128.21 -> £3,381,667.95 (10.4%); £3,772,128.35 -> £3,381,667.94 (10.4%); £3,772,128.50 -> £3,381,667.94 (10.4%); £3,772,128.67 -> £3,381,667.94 (10.4%); £3,772,128.84 -> £3,381,667.93 (10.4%); £3,772,129.04 -> £3,381,667.92 (10.4%); £3,772,129.26 -> £3,381,667.91 (10.4%); £3,772,129.48 -> £3,381,667.91 (10.4%); £3,772,129.70 -> £3,381,667.90 (10.4%); £3,772,129.92 -> £3,381,667.90 (10.4%); £3,772,130.14 -> £3,381,667.89 (10.4%); £3,772,130.37 -> £3,381,667.89 (10.4%); £3,772,130.60 -> £3,381,667.89 (10.4%); £3,772,130.82 -> £3,381,667.88 (10.4%); £3,772,131.05 -> £3,381,667.88 (10.4%); £3,772,131.27 -> £3,381,667.87 (10.4%); £3,772,131.48 -> £3,381,667.87 (10.4%); £3,772,131.70 -> £3,381,667.87 (10.4%); £3,772,131.92 -> £3,381,667.86 (10.4%); £3,772,132.14 -> £3,381,667.86 (10.4%); £3,772,132.36 -> £3,381,667.86 (10.4%); £3,772,132.59 -> £3,381,667.85 (10.4%); £3,772,132.81 -> £3,381,667.83 (10.4%); £3,772,133.03 -> £3,381,667.81 (10.4%); £3,772,133.26 -> £3,381,667.80 (10.4%); £3,772,133.49 -> £3,381,667.78 (10.4%); £3,772,133.72 -> £3,381,667.75 (10.4%); £3,772,133.94 -> £3,381,667.72 (10.4%); £3,772,134.16 -> £3,381,667.70 (10.4%); £3,772,134.39 -> £3,381,667.67 (10.4%); £3,772,134.61 -> £3,381,667.65 (10.4%); £3,772,134.83 -> £3,381,667.64 (10.4%); £3,772,135.05 -> £3,381,667.63 (10.4%); £3,772,135.27 -> £3,381,667.62 (10.4%); £3,772,135.47 -> £3,381,667.62 (10.4%); £3,772,135.66 -> £3,381,667.61 (10.4%); £3,772,135.84 -> £3,381,667.61 (10.4%); £3,772,135.98 -> £3,381,667.61 (10.4%); £3,772,136.11 -> £3,381,667.61 (10.4%); £3,772,136.24 -> £3,381,667.61 (10.4%); £3,772,136.38 -> £3,381,667.61 (10.4%); £3,772,136.52 -> £3,381,667.61 (10.4%); £3,772,136.65 -> £3,381,667.61 (10.4%); £3,772,136.78 -> £3,381,667.61 (10.4%); £3,772,136.92 -> £3,381,667.62 (10.4%); £3,772,137.06 -> £3,381,667.62 (10.4%); £3,772,137.20 -> £3,381,667.62 (10.4%); £3,772,137.34 -> £3,381,667.62 (10.4%); £3,772,137.47 -> £3,381,667.62 (10.4%); £3,772,137.60 -> £3,381,667.62 (10.4%); £3,772,137.75 -> £3,381,667.62 (10.4%); £3,772,137.92 -> £3,381,667.62 (10.4%); £3,772,138.10 -> £3,381,667.61 (10.4%); £3,772,138.30 -> £3,381,667.61 (10.4%); £3,772,138.51 -> £3,381,667.60 (10.4%); £3,772,138.74 -> £3,381,667.58 (10.4%); £3,772,138.97 -> £3,381,667.58 (10.4%); £3,772,139.19 -> £3,381,667.57 (10.4%); £3,772,139.41 -> £3,381,667.56 (10.4%); £3,772,139.64 -> £3,381,667.55 (10.4%); £3,772,139.86 -> £3,381,667.54 (10.4%); £3,772,140.09 -> £3,381,667.53 (10.4%); £3,772,140.33 -> £3,381,667.52 (10.4%); £3,772,140.55 -> £3,381,667.52 (10.4%); £3,772,140.78 -> £3,381,667.51 (10.4%); £3,772,141.01 -> £3,381,667.50 (10.4%); £3,772,141.23 -> £3,381,667.50 (10.4%); £3,772,141.46 -> £3,381,667.50 (10.4%); £3,772,141.69 -> £3,381,667.49 (10.4%); £3,772,141.91 -> £3,381,667.48 (10.4%); £3,772,142.14 -> £3,381,667.46 (10.4%); £3,772,142.36 -> £3,381,667.44 (10.4%); £3,772,142.60 -> £3,381,667.42 (10.4%); £3,772,142.82 -> £3,381,667.40 (10.4%); £3,772,143.04 -> £3,381,667.37 (10.4%); £3,772,143.27 -> £3,381,667.35 (10.4%); £3,772,143.49 -> £3,381,667.32 (10.4%); £3,772,143.72 -> £3,381,667.30 (10.4%); £3,772,143.94 -> £3,381,667.27 (10.4%); £3,772,144.17 -> £3,381,667.25 (10.4%); £3,772,144.39 -> £3,381,667.24 (10.4%); £3,772,144.62 -> £3,381,667.24 (10.4%); £3,772,144.83 -> £3,381,667.23 (10.4%); £3,772,145.03 -> £3,381,667.23 (10.4%); £3,772,145.21 -> £3,381,667.23 (10.4%); £3,772,145.36 -> £3,381,667.23 (10.4%); £3,772,145.52 -> £3,381,667.23 (10.4%); £3,772,145.67 -> £3,381,667.23 (10.4%); £3,772,145.82 -> £3,381,667.23 (10.4%); £3,772,145.98 -> £3,381,667.23 (10.4%); £3,772,146.13 -> £3,381,667.24 (10.4%); £3,772,146.28 -> £3,381,667.24 (10.4%); £3,772,146.44 -> £3,381,667.24 (10.4%); £3,772,146.59 -> £3,381,667.24 (10.4%); £3,772,146.74 -> £3,381,667.25 (10.4%); £3,772,146.89 -> £3,381,667.25 (10.4%); £3,772,147.05 -> £3,381,667.24 (10.4%); £3,772,147.21 -> £3,381,667.24 (10.4%); £3,772,147.37 -> £3,381,667.28 (10.4%); £3,772,147.56 -> £3,381,667.33 (10.4%); £3,772,147.77 -> £3,381,667.39 (10.4%); £3,772,147.99 -> £3,381,667.43 (10.4%); £3,772,148.23 -> £3,381,667.48 (10.4%); £3,772,148.50 -> £3,381,667.53 (10.4%); £3,772,148.75 -> £3,381,667.56 (10.4%); £3,772,149.00 -> £3,381,667.60 (10.4%); £3,772,149.26 -> £3,381,667.60 (10.4%); £3,772,149.51 -> £3,381,667.59 (10.4%); £3,772,149.75 -> £3,381,667.59 (10.4%); £3,772,150.01 -> £3,381,667.59 (10.4%); £3,772,150.26 -> £3,381,667.59 (10.4%); £3,772,150.52 -> £3,381,667.59 (10.4%); £3,772,150.78 -> £3,381,667.59 (10.4%); £3,772,151.04 -> £3,381,667.59 (10.4%); £3,772,151.30 -> £3,381,667.59 (10.4%); £3,772,151.56 -> £3,381,667.59 (10.4%); £3,772,151.82 -> £3,381,667.62 (10.4%); £3,772,152.07 -> £3,381,667.68 (10.4%); £3,772,152.33 -> £3,381,667.75 (10.4%); £3,772,152.59 -> £3,381,667.82 (10.4%); £3,772,152.84 -> £3,381,667.88 (10.4%); £3,772,153.10 -> £3,381,667.95 (10.4%); £3,772,153.36 -> £3,381,668.03 (10.4%); £3,772,153.61 -> £3,381,668.11 (10.4%); £3,772,153.87 -> £3,381,668.09 (10.4%); £3,772,154.13 -> £3,381,668.07 (10.4%); £3,772,154.38 -> £3,381,668.04 (10.4%); £3,772,154.64 -> £3,381,668.02 (10.4%); £3,772,154.90 -> £3,381,668.02 (10.4%); £3,772,155.15 -> £3,381,668.01 (10.4%); £3,772,155.39 -> £3,381,668.01 (10.4%); £3,772,155.60 -> £3,381,668.00 (10.4%); £3,772,155.80 -> £3,381,668.00 (10.4%); £3,772,155.96 -> £3,381,668.00 (10.4%); £3,772,156.11 -> £3,381,668.00 (10.4%); £3,772,156.27 -> £3,381,668.01 (10.4%); £3,772,156.42 -> £3,381,668.01 (10.4%); £3,772,156.58 -> £3,381,668.01 (10.4%); £3,772,156.73 -> £3,381,668.01 (10.4%); £3,772,156.89 -> £3,381,668.01 (10.4%); £3,772,157.04 -> £3,381,668.02 (10.4%); £3,772,157.19 -> £3,381,668.02 (10.4%); £3,772,157.35 -> £3,381,668.02 (10.4%); £3,772,157.50 -> £3,381,668.02 (10.4%); £3,772,157.66 -> £3,381,668.02 (10.4%); £3,772,157.82 -> £3,381,668.01 (10.4%); £3,772,157.99 -> £3,381,668.06 (10.4%); £3,772,158.18 -> £3,381,668.11 (10.4%); £3,772,158.39 -> £3,381,668.16 (10.4%); £3,772,158.61 -> £3,381,668.21 (10.4%); £3,772,158.86 -> £3,381,668.26 (10.4%); £3,772,159.11 -> £3,381,668.30 (10.4%); £3,772,159.37 -> £3,381,668.34 (10.4%); £3,772,159.62 -> £3,381,668.38 (10.4%); £3,772,159.87 -> £3,381,668.38 (10.4%); £3,772,160.13 -> £3,381,668.37 (10.4%); £3,772,160.39 -> £3,381,668.37 (10.4%); £3,772,160.65 -> £3,381,668.37 (10.4%); £3,772,160.91 -> £3,381,668.37 (10.4%); £3,772,161.18 -> £3,381,668.37 (10.4%); £3,772,161.45 -> £3,381,668.37 (10.4%); £3,772,161.70 -> £3,381,668.37 (10.4%); £3,772,161.96 -> £3,381,668.37 (10.4%); £3,772,162.22 -> £3,381,668.37 (10.4%); £3,772,162.47 -> £3,381,668.40 (10.4%); £3,772,162.73 -> £3,381,668.46 (10.4%); £3,772,162.98 -> £3,381,668.52 (10.4%); £3,772,163.25 -> £3,381,668.59 (10.4%); £3,772,163.50 -> £3,381,668.66 (10.4%); £3,772,163.76 -> £3,381,668.72 (10.4%); £3,772,164.02 -> £3,381,668.81 (10.4%); £3,772,164.28 -> £3,381,668.89 (10.4%); £3,772,164.54 -> £3,381,668.86 (10.4%); £3,772,164.79 -> £3,381,668.84 (10.4%); £3,772,165.05 -> £3,381,668.81 (10.4%); £3,772,165.30 -> £3,381,668.79 (10.4%); £3,772,165.56 -> £3,381,668.79 (10.4%); £3,772,165.81 -> £3,381,668.78 (10.4%); £3,772,166.06 -> £3,381,668.78 (10.4%); £3,772,166.28 -> £3,381,668.77 (10.4%); £3,772,166.47 -> £3,381,668.77 (10.4%); £3,772,166.62 -> £3,381,668.77 (10.4%); £3,772,166.78 -> £3,381,668.77 (10.4%); £3,772,166.93 -> £3,381,668.77 (10.4%); £3,772,167.08 -> £3,381,668.77 (10.4%); £3,772,167.23 -> £3,381,668.78 (10.4%); £3,772,167.39 -> £3,381,668.78 (10.4%); £3,772,167.55 -> £3,381,668.78 (10.4%); £3,772,167.70 -> £3,381,668.78 (10.4%); £3,772,167.86 -> £3,381,668.78 (10.4%); £3,772,168.01 -> £3,381,668.79 (10.4%); £3,772,168.18 -> £3,381,668.79 (10.4%); £3,772,168.33 -> £3,381,668.78 (10.4%); £3,772,168.49 -> £3,381,668.78 (10.4%); £3,772,168.66 -> £3,381,668.82 (10.4%); £3,772,168.84 -> £3,381,668.88 (10.4%); £3,772,169.05 -> £3,381,668.93 (10.4%); £3,772,169.28 -> £3,381,668.98 (10.4%); £3,772,169.53 -> £3,381,669.02 (10.4%); £3,772,169.78 -> £3,381,669.06 (10.4%); £3,772,170.04 -> £3,381,669.10 (10.4%); £3,772,170.30 -> £3,381,669.14 (10.4%); £3,772,170.55 -> £3,381,669.14 (10.4%); £3,772,170.80 -> £3,381,669.13 (10.4%); £3,772,171.07 -> £3,381,669.13 (10.4%); £3,772,171.32 -> £3,381,669.13 (10.4%); £3,772,171.58 -> £3,381,669.13 (10.4%); £3,772,171.83 -> £3,381,669.13 (10.4%); £3,772,172.08 -> £3,381,669.13 (10.4%); £3,772,172.34 -> £3,381,669.13 (10.4%); £3,772,172.60 -> £3,381,669.13 (10.4%); £3,772,172.85 -> £3,381,669.13 (10.4%); £3,772,173.11 -> £3,381,669.16 (10.4%); £3,772,173.37 -> £3,381,669.22 (10.4%); £3,772,173.62 -> £3,381,669.29 (10.4%); £3,772,173.89 -> £3,381,669.35 (10.4%); £3,772,174.14 -> £3,381,669.42 (10.4%); £3,772,174.40 -> £3,381,669.48 (10.4%); £3,772,174.66 -> £3,381,669.56 (10.4%); £3,772,174.92 -> £3,381,669.64 (10.4%); £3,772,175.17 -> £3,381,669.62 (10.4%); £3,772,175.43 -> £3,381,669.59 (10.4%); £3,772,175.69 -> £3,381,669.57 (10.4%); £3,772,175.94 -> £3,381,669.55 (10.4%); £3,772,176.19 -> £3,381,669.54 (10.4%); £3,772,176.45 -> £3,381,669.54 (10.4%); £3,772,176.69 -> £3,381,669.53 (10.4%); £3,772,176.91 -> £3,381,669.53 (10.4%); £3,772,177.12 -> £3,381,669.53 (10.4%); £3,772,177.28 -> £3,381,669.53 (10.4%); £3,772,177.43 -> £3,381,669.53 (10.4%); £3,772,177.58 -> £3,381,669.53 (10.4%); £3,772,177.73 -> £3,381,669.53 (10.4%); £3,772,177.88 -> £3,381,669.53 (10.4%); £3,772,178.03 -> £3,381,669.54 (10.4%); £3,772,178.18 -> £3,381,669.54 (10.4%); £3,772,178.34 -> £3,381,669.54 (10.4%); £3,772,178.49 -> £3,381,669.54 (10.4%); £3,772,178.64 -> £3,381,669.54 (10.4%); £3,772,178.79 -> £3,381,669.55 (10.4%); £3,772,178.94 -> £3,381,669.54 (10.4%); £3,772,179.10 -> £3,381,669.54 (10.4%); £3,772,179.27 -> £3,381,669.58 (10.4%); £3,772,179.45 -> £3,381,669.63 (10.4%); £3,772,179.66 -> £3,381,669.69 (10.4%); £3,772,179.89 -> £3,381,669.73 (10.4%); £3,772,180.12 -> £3,381,669.78 (10.4%); £3,772,180.38 -> £3,381,669.82 (10.4%); £3,772,180.64 -> £3,381,669.86 (10.4%); £3,772,180.90 -> £3,381,669.90 (10.4%); £3,772,181.15 -> £3,381,669.89 (10.4%); £3,772,181.40 -> £3,381,669.89 (10.4%); £3,772,181.67 -> £3,381,669.89 (10.4%); £3,772,181.92 -> £3,381,669.89 (10.4%); £3,772,182.17 -> £3,381,669.89 (10.4%); £3,772,182.43 -> £3,381,669.89 (10.4%); £3,772,182.68 -> £3,381,669.89 (10.4%); £3,772,182.94 -> £3,381,669.89 (10.4%); £3,772,183.19 -> £3,381,669.88 (10.4%); £3,772,183.44 -> £3,381,669.89 (10.4%); £3,772,183.70 -> £3,381,669.92 (10.4%); £3,772,183.96 -> £3,381,669.98 (10.4%); £3,772,184.20 -> £3,381,670.05 (10.4%); £3,772,184.46 -> £3,381,670.11 (10.4%); £3,772,184.72 -> £3,381,670.18 (10.4%); £3,772,184.98 -> £3,381,670.25 (10.4%); £3,772,185.24 -> £3,381,670.33 (10.4%); £3,772,185.49 -> £3,381,670.41 (10.4%); £3,772,185.75 -> £3,381,670.39 (10.4%); £3,772,186.00 -> £3,381,670.36 (10.4%); £3,772,186.25 -> £3,381,670.34 (10.4%); £3,772,186.51 -> £3,381,670.32 (10.4%); £3,772,186.77 -> £3,381,670.31 (10.4%); £3,772,187.02 -> £3,381,670.31 (10.4%); £3,772,187.25 -> £3,381,670.30 (10.4%); £3,772,187.48 -> £3,381,670.30 (10.4%); £3,772,187.67 -> £3,381,670.30 (10.4%); £3,772,187.83 -> £3,381,670.30 (10.4%); £3,772,187.99 -> £3,381,670.30 (10.4%); £3,772,188.13 -> £3,381,670.31 (10.4%); £3,772,188.29 -> £3,381,670.31 (10.4%); £3,772,188.44 -> £3,381,670.31 (10.4%); £3,772,188.59 -> £3,381,670.31 (10.4%); £3,772,188.75 -> £3,381,670.32 (10.4%); £3,772,188.90 -> £3,381,670.32 (10.4%); £3,772,189.05 -> £3,381,670.32 (10.4%); £3,772,189.20 -> £3,381,670.32 (10.4%); £3,772,189.35 -> £3,381,670.32 (10.4%); £3,772,189.51 -> £3,381,670.32 (10.4%); £3,772,189.66 -> £3,381,670.31 (10.4%); £3,772,189.83 -> £3,381,670.36 (10.4%); £3,772,190.02 -> £3,381,670.41 (10.4%); £3,772,190.23 -> £3,381,670.46 (10.4%); £3,772,190.45 -> £3,381,670.51 (10.4%); £3,772,190.69 -> £3,381,670.56 (10.4%); £3,772,190.96 -> £3,381,670.60 (10.4%); £3,772,191.22 -> £3,381,670.64 (10.4%); £3,772,191.48 -> £3,381,670.68 (10.4%); £3,772,191.74 -> £3,381,670.68 (10.4%); £3,772,192.00 -> £3,381,670.68 (10.4%); £3,772,192.25 -> £3,381,670.67 (10.4%); £3,772,192.51 -> £3,381,670.67 (10.4%); £3,772,192.77 -> £3,381,670.67 (10.4%); £3,772,193.02 -> £3,381,670.67 (10.4%); £3,772,193.28 -> £3,381,670.67 (10.4%); £3,772,193.54 -> £3,381,670.67 (10.4%); £3,772,193.80 -> £3,381,670.67 (10.4%); £3,772,194.05 -> £3,381,670.67 (10.4%); £3,772,194.31 -> £3,381,670.71 (10.4%); £3,772,194.57 -> £3,381,670.77 (10.4%); £3,772,194.83 -> £3,381,670.83 (10.4%); £3,772,195.08 -> £3,381,670.90 (10.4%); £3,772,195.35 -> £3,381,670.97 (10.4%); £3,772,195.59 -> £3,381,671.03 (10.4%); £3,772,195.85 -> £3,381,671.12 (10.4%); £3,772,196.11 -> £3,381,671.20 (10.4%); £3,772,196.38 -> £3,381,671.17 (10.4%); £3,772,196.64 -> £3,381,671.15 (10.4%); £3,772,196.89 -> £3,381,671.13 (10.4%); £3,772,197.15 -> £3,381,671.11 (10.4%); £3,772,197.41 -> £3,381,671.10 (10.4%); £3,772,197.67 -> £3,381,671.09 (10.4%); £3,772,197.90 -> £3,381,671.09 (10.4%); £3,772,198.12 -> £3,381,671.09 (10.4%); £3,772,198.32 -> £3,381,671.08 (10.4%); £3,772,198.46 -> £3,381,671.08 (10.4%); £3,772,198.60 -> £3,381,671.08 (10.4%); £3,772,198.74 -> £3,381,671.09 (10.4%); £3,772,198.87 -> £3,381,671.09 (10.4%); £3,772,199.01 -> £3,381,671.09 (10.4%); £3,772,199.14 -> £3,381,671.09 (10.4%); £3,772,199.28 -> £3,381,671.10 (10.4%); £3,772,199.42 -> £3,381,671.10 (10.4%); £3,772,199.56 -> £3,381,671.10 (10.4%); £3,772,199.69 -> £3,381,671.10 (10.4%); £3,772,199.83 -> £3,381,671.11 (10.4%); £3,772,199.96 -> £3,381,671.10 (10.4%); £3,772,200.09 -> £3,381,671.10 (10.4%); £3,772,200.24 -> £3,381,671.10 (10.4%); £3,772,200.41 -> £3,381,671.10 (10.4%); £3,772,200.59 -> £3,381,671.09 (10.4%); £3,772,200.79 -> £3,381,671.09 (10.4%); £3,772,201.00 -> £3,381,671.08 (10.4%); £3,772,201.23 -> £3,381,671.07 (10.4%); £3,772,201.46 -> £3,381,671.07 (10.4%); £3,772,201.68 -> £3,381,671.07 (10.4%); £3,772,201.91 -> £3,381,671.06 (10.4%); £3,772,202.14 -> £3,381,671.06 (10.4%); £3,772,202.36 -> £3,381,671.06 (10.4%); £3,772,202.59 -> £3,381,671.05 (10.4%); £3,772,202.82 -> £3,381,671.05 (10.4%); £3,772,203.05 -> £3,381,671.05 (10.4%); £3,772,203.27 -> £3,381,671.04 (10.4%); £3,772,203.50 -> £3,381,671.04 (10.4%); £3,772,203.72 -> £3,381,671.04 (10.4%); £3,772,203.94 -> £3,381,671.04 (10.4%); £3,772,204.17 -> £3,381,671.04 (10.4%); £3,772,204.40 -> £3,381,671.03 (10.4%); £3,772,204.63 -> £3,381,671.01 (10.4%); £3,772,204.86 -> £3,381,670.99 (10.4%); £3,772,205.09 -> £3,381,670.98 (10.4%); £3,772,205.32 -> £3,381,670.96 (10.4%); £3,772,205.55 -> £3,381,670.93 (10.4%); £3,772,205.77 -> £3,381,670.90 (10.4%); £3,772,206.00 -> £3,381,670.88 (10.4%); £3,772,206.23 -> £3,381,670.86 (10.4%); £3,772,206.45 -> £3,381,670.84 (10.4%); £3,772,206.67 -> £3,381,670.82 (10.4%); £3,772,206.91 -> £3,381,670.81 (10.4%); £3,772,207.13 -> £3,381,670.81 (10.4%); £3,772,207.34 -> £3,381,670.80 (10.4%); £3,772,207.53 -> £3,381,670.80 (10.4%); £3,772,207.70 -> £3,381,670.80 (10.4%); £3,772,207.84 -> £3,381,670.80 (10.4%); £3,772,207.98 -> £3,381,670.80 (10.4%); £3,772,208.12 -> £3,381,670.80 (10.4%); £3,772,208.26 -> £3,381,670.80 (10.4%); £3,772,208.41 -> £3,381,670.80 (10.4%); £3,772,208.54 -> £3,381,670.80 (10.4%); £3,772,208.68 -> £3,381,670.81 (10.4%); £3,772,208.83 -> £3,381,670.81 (10.4%); £3,772,208.97 -> £3,381,670.81 (10.4%); £3,772,209.11 -> £3,381,670.81 (10.4%); £3,772,209.25 -> £3,381,670.82 (10.4%); £3,772,209.40 -> £3,381,670.82 (10.4%); £3,772,209.54 -> £3,381,670.81 (10.4%); £3,772,209.69 -> £3,381,670.82 (10.4%); £3,772,209.86 -> £3,381,670.81 (10.4%); £3,772,210.05 -> £3,381,670.81 (10.4%); £3,772,210.26 -> £3,381,670.81 (10.4%); £3,772,210.47 -> £3,381,670.80 (10.4%); £3,772,210.70 -> £3,381,670.79 (10.4%); £3,772,210.93 -> £3,381,670.78 (10.4%); £3,772,211.17 -> £3,381,670.77 (10.4%); £3,772,211.40 -> £3,381,670.77 (10.4%); £3,772,211.63 -> £3,381,670.76 (10.4%); £3,772,211.86 -> £3,381,670.75 (10.4%); £3,772,212.10 -> £3,381,670.74 (10.4%); £3,772,212.33 -> £3,381,670.73 (10.4%); £3,772,212.56 -> £3,381,670.72 (10.4%); £3,772,212.79 -> £3,381,670.72 (10.4%); £3,772,213.02 -> £3,381,670.71 (10.4%); £3,772,213.26 -> £3,381,670.71 (10.4%); £3,772,213.48 -> £3,381,670.70 (10.4%); £3,772,213.72 -> £3,381,670.70 (10.4%); £3,772,213.95 -> £3,381,670.69 (10.4%); £3,772,214.18 -> £3,381,670.67 (10.4%); £3,772,214.42 -> £3,381,670.65 (10.4%); £3,772,214.65 -> £3,381,670.63 (10.4%); £3,772,214.88 -> £3,381,670.61 (10.4%); £3,772,215.12 -> £3,381,670.58 (10.4%); £3,772,215.34 -> £3,381,670.55 (10.4%); £3,772,215.59 -> £3,381,670.53 (10.4%); £3,772,215.83 -> £3,381,670.50 (10.4%); £3,772,216.06 -> £3,381,670.48 (10.4%); £3,772,216.30 -> £3,381,670.46 (10.4%); £3,772,216.53 -> £3,381,670.45 (10.4%); £3,772,216.76 -> £3,381,670.45 (10.4%); £3,772,216.99 -> £3,381,670.44 (10.4%); £3,772,217.19 -> £3,381,670.44 (10.4%); £3,772,217.37 -> £3,381,670.43 (10.4%); £3,772,217.53 -> £3,381,670.43 (10.4%); £3,772,217.69 -> £3,381,670.44 (10.4%); £3,772,217.85 -> £3,381,670.44 (10.4%); £3,772,218.01 -> £3,381,670.44 (10.4%); £3,772,218.18 -> £3,381,670.44 (10.4%); £3,772,218.34 -> £3,381,670.44 (10.4%); £3,772,218.50 -> £3,381,670.45 (10.4%); £3,772,218.66 -> £3,381,670.45 (10.4%); £3,772,218.82 -> £3,381,670.45 (10.4%); £3,772,218.99 -> £3,381,670.45 (10.4%); £3,772,219.15 -> £3,381,670.45 (10.4%); £3,772,219.31 -> £3,381,670.45 (10.4%); £3,772,219.47 -> £3,381,670.44 (10.4%); £3,772,219.64 -> £3,381,670.49 (10.4%); £3,772,219.85 -> £3,381,670.54 (10.4%); £3,772,220.06 -> £3,381,670.59 (10.4%); £3,772,220.29 -> £3,381,670.64 (10.4%); £3,772,220.54 -> £3,381,670.69 (10.4%); £3,772,220.82 -> £3,381,670.73 (10.4%); £3,772,221.09 -> £3,381,670.77 (10.4%); £3,772,221.37 -> £3,381,670.81 (10.4%); £3,772,221.64 -> £3,381,670.81 (10.4%); £3,772,221.91 -> £3,381,670.80 (10.4%); £3,772,222.18 -> £3,381,670.80 (10.4%); £3,772,222.45 -> £3,381,670.80 (10.4%); £3,772,222.72 -> £3,381,670.80 (10.4%); £3,772,222.98 -> £3,381,670.80 (10.4%); £3,772,223.26 -> £3,381,670.80 (10.4%); £3,772,223.53 -> £3,381,670.80 (10.4%); £3,772,223.81 -> £3,381,670.80 (10.4%); £3,772,224.08 -> £3,381,670.80 (10.4%); £3,772,224.35 -> £3,381,670.83 (10.4%); £3,772,224.62 -> £3,381,670.89 (10.4%); £3,772,224.88 -> £3,381,670.95 (10.4%); £3,772,225.16 -> £3,381,671.02 (10.4%); £3,772,225.42 -> £3,381,671.09 (10.4%); £3,772,225.68 -> £3,381,671.15 (10.4%); £3,772,225.94 -> £3,381,671.24 (10.4%); £3,772,226.21 -> £3,381,671.32 (10.4%); £3,772,226.48 -> £3,381,671.29 (10.4%); £3,772,226.75 -> £3,381,671.27 (10.4%); £3,772,227.01 -> £3,381,671.24 (10.4%); £3,772,227.28 -> £3,381,671.22 (10.4%); £3,772,227.54 -> £3,381,671.21 (10.4%); £3,772,227.82 -> £3,381,671.21 (10.4%); £3,772,228.05 -> £3,381,671.20 (10.4%); £3,772,228.28 -> £3,381,671.20 (10.4%); £3,772,228.49 -> £3,381,671.20 (10.4%); £3,772,228.65 -> £3,381,671.20 (10.4%); £3,772,228.81 -> £3,381,671.20 (10.4%); £3,772,228.98 -> £3,381,671.20 (10.4%); £3,772,229.15 -> £3,381,671.20 (10.4%); £3,772,229.31 -> £3,381,671.20 (10.4%); £3,772,229.47 -> £3,381,671.21 (10.4%); £3,772,229.63 -> £3,381,671.21 (10.4%); £3,772,229.80 -> £3,381,671.21 (10.4%); £3,772,229.96 -> £3,381,671.21 (10.4%); £3,772,230.12 -> £3,381,671.21 (10.4%); £3,772,230.28 -> £3,381,671.21 (10.4%); £3,772,230.44 -> £3,381,671.21 (10.4%); £3,772,230.61 -> £3,381,671.20 (10.4%); £3,772,230.79 -> £3,381,671.25 (10.4%); £3,772,230.99 -> £3,381,671.30 (10.4%); £3,772,231.21 -> £3,381,671.35 (10.4%); £3,772,231.44 -> £3,381,671.40 (10.4%); £3,772,231.69 -> £3,381,671.45 (10.4%); £3,772,231.96 -> £3,381,671.49 (10.4%); £3,772,232.23 -> £3,381,671.53 (10.4%); £3,772,232.51 -> £3,381,671.57 (10.4%); £3,772,232.78 -> £3,381,671.57 (10.4%); £3,772,233.03 -> £3,381,671.56 (10.4%); £3,772,233.30 -> £3,381,671.56 (10.4%); £3,772,233.57 -> £3,381,671.56 (10.4%); £3,772,233.83 -> £3,381,671.56 (10.4%); £3,772,234.10 -> £3,381,671.56 (10.4%); £3,772,234.36 -> £3,381,671.56 (10.4%); £3,772,234.63 -> £3,381,671.56 (10.4%); £3,772,234.90 -> £3,381,671.56 (10.4%); £3,772,235.18 -> £3,381,671.56 (10.4%); £3,772,235.45 -> £3,381,671.59 (10.4%); £3,772,235.72 -> £3,381,671.65 (10.4%); £3,772,235.99 -> £3,381,671.72 (10.4%); £3,772,236.26 -> £3,381,671.78 (10.4%); £3,772,236.52 -> £3,381,671.85 (10.4%); £3,772,236.79 -> £3,381,671.91 (10.4%); £3,772,237.06 -> £3,381,672.00 (10.4%); £3,772,237.32 -> £3,381,672.08 (10.4%); £3,772,237.59 -> £3,381,672.05 (10.4%); £3,772,237.85 -> £3,381,672.03 (10.4%); £3,772,238.12 -> £3,381,672.01 (10.4%); £3,772,238.40 -> £3,381,671.99 (10.4%); £3,772,238.67 -> £3,381,671.98 (10.4%); £3,772,238.94 -> £3,381,671.97 (10.4%); £3,772,239.18 -> £3,381,671.97 (10.4%); £3,772,239.42 -> £3,381,671.96 (10.4%); £3,772,239.63 -> £3,381,671.96 (10.4%); £3,772,239.79 -> £3,381,671.96 (10.4%); £3,772,239.95 -> £3,381,671.96 (10.4%); £3,772,240.11 -> £3,381,671.97 (10.4%); £3,772,240.27 -> £3,381,671.97 (10.4%); £3,772,240.43 -> £3,381,671.97 (10.4%); £3,772,240.59 -> £3,381,671.97 (10.4%); £3,772,240.74 -> £3,381,671.98 (10.4%); £3,772,240.90 -> £3,381,671.98 (10.4%); £3,772,241.06 -> £3,381,671.98 (10.4%); £3,772,241.22 -> £3,381,671.98 (10.4%); £3,772,241.38 -> £3,381,671.98 (10.4%); £3,772,241.53 -> £3,381,671.98 (10.4%); £3,772,241.69 -> £3,381,671.97 (10.4%); £3,772,241.87 -> £3,381,672.02 (10.4%); £3,772,242.07 -> £3,381,672.07 (10.4%); £3,772,242.29 -> £3,381,672.12 (10.4%); £3,772,242.52 -> £3,381,672.17 (10.4%); £3,772,242.77 -> £3,381,672.22 (10.4%); £3,772,243.04 -> £3,381,672.26 (10.4%); £3,772,243.31 -> £3,381,672.30 (10.4%); £3,772,243.58 -> £3,381,672.33 (10.4%); £3,772,243.85 -> £3,381,672.33 (10.4%); £3,772,244.12 -> £3,381,672.33 (10.4%); £3,772,244.38 -> £3,381,672.33 (10.4%); £3,772,244.66 -> £3,381,672.33 (10.4%); £3,772,244.93 -> £3,381,672.32 (10.4%); £3,772,245.20 -> £3,381,672.32 (10.4%); £3,772,245.48 -> £3,381,672.32 (10.4%); £3,772,245.75 -> £3,381,672.32 (10.4%); £3,772,246.01 -> £3,381,672.32 (10.4%); £3,772,246.28 -> £3,381,672.32 (10.4%); £3,772,246.55 -> £3,381,672.36 (10.4%); £3,772,246.82 -> £3,381,672.42 (10.4%); £3,772,247.09 -> £3,381,672.49 (10.4%); £3,772,247.36 -> £3,381,672.55 (10.4%); £3,772,247.63 -> £3,381,672.62 (10.4%); £3,772,247.90 -> £3,381,672.69 (10.4%); £3,772,248.17 -> £3,381,672.77 (10.4%); £3,772,248.44 -> £3,381,672.85 (10.4%); £3,772,248.71 -> £3,381,672.83 (10.4%); £3,772,248.98 -> £3,381,672.80 (10.4%); £3,772,249.24 -> £3,381,672.78 (10.4%); £3,772,249.51 -> £3,381,672.76 (10.4%); £3,772,249.78 -> £3,381,672.75 (10.4%); £3,772,250.06 -> £3,381,672.74 (10.4%); £3,772,250.31 -> £3,381,672.74 (10.4%); £3,772,250.53 -> £3,381,672.73 (10.4%); £3,772,250.74 -> £3,381,672.73 (10.4%); £3,772,250.90 -> £3,381,672.73 (10.4%); £3,772,251.07 -> £3,381,672.73 (10.4%); £3,772,251.23 -> £3,381,672.73 (10.4%); £3,772,251.39 -> £3,381,672.74 (10.4%); £3,772,251.55 -> £3,381,672.74 (10.4%); £3,772,251.71 -> £3,381,672.74 (10.4%); £3,772,251.87 -> £3,381,672.74 (10.4%); £3,772,252.03 -> £3,381,672.75 (10.4%); £3,772,252.19 -> £3,381,672.75 (10.4%); £3,772,252.35 -> £3,381,672.75 (10.4%); £3,772,252.51 -> £3,381,672.75 (10.4%); £3,772,252.67 -> £3,381,672.75 (10.4%); £3,772,252.83 -> £3,381,672.74 (10.4%); £3,772,253.02 -> £3,381,672.79 (10.4%); £3,772,253.22 -> £3,381,672.84 (10.4%); £3,772,253.44 -> £3,381,672.90 (10.4%); £3,772,253.67 -> £3,381,672.94 (10.4%); £3,772,253.93 -> £3,381,672.99 (10.4%); £3,772,254.20 -> £3,381,673.03 (10.4%); £3,772,254.47 -> £3,381,673.07 (10.4%); £3,772,254.74 -> £3,381,673.11 (10.4%); £3,772,255.00 -> £3,381,673.10 (10.4%); £3,772,255.28 -> £3,381,673.10 (10.4%); £3,772,255.55 -> £3,381,673.10 (10.4%); £3,772,255.82 -> £3,381,673.10 (10.4%); £3,772,256.09 -> £3,381,673.10 (10.4%); £3,772,256.37 -> £3,381,673.10 (10.4%); £3,772,256.65 -> £3,381,673.10 (10.4%); £3,772,256.91 -> £3,381,673.09 (10.4%); £3,772,257.18 -> £3,381,673.09 (10.4%); £3,772,257.46 -> £3,381,673.09 (10.4%); £3,772,257.73 -> £3,381,673.13 (10.4%); £3,772,258.02 -> £3,381,673.19 (10.4%); £3,772,258.28 -> £3,381,673.25 (10.4%); £3,772,258.55 -> £3,381,673.32 (10.4%); £3,772,258.82 -> £3,381,673.39 (10.4%); £3,772,259.09 -> £3,381,673.45 (10.4%); £3,772,259.36 -> £3,381,673.54 (10.4%); £3,772,259.64 -> £3,381,673.62 (10.4%); £3,772,259.92 -> £3,381,673.59 (10.4%); £3,772,260.19 -> £3,381,673.57 (10.4%); £3,772,260.47 -> £3,381,673.54 (10.4%); £3,772,260.73 -> £3,381,673.52 (10.4%); £3,772,261.01 -> £3,381,673.51 (10.4%); £3,772,261.29 -> £3,381,673.51 (10.4%); £3,772,261.54 -> £3,381,673.50 (10.4%); £3,772,261.78 -> £3,381,673.50 (10.4%); £3,772,261.99 -> £3,381,673.49 (10.4%); £3,772,262.15 -> £3,381,673.49 (10.4%); £3,772,262.31 -> £3,381,673.50 (10.4%); £3,772,262.48 -> £3,381,673.50 (10.4%); £3,772,262.64 -> £3,381,673.50 (10.4%); £3,772,262.80 -> £3,381,673.50 (10.4%); £3,772,262.96 -> £3,381,673.50 (10.4%); £3,772,263.13 -> £3,381,673.50 (10.4%); £3,772,263.29 -> £3,381,673.51 (10.4%); £3,772,263.45 -> £3,381,673.51 (10.4%); £3,772,263.61 -> £3,381,673.51 (10.4%); £3,772,263.78 -> £3,381,673.51 (10.4%); £3,772,263.94 -> £3,381,673.51 (10.4%); £3,772,264.10 -> £3,381,673.50 (10.4%); £3,772,264.28 -> £3,381,673.55 (10.4%); £3,772,264.48 -> £3,381,673.60 (10.4%); £3,772,264.69 -> £3,381,673.65 (10.4%); £3,772,264.92 -> £3,381,673.70 (10.4%); £3,772,265.17 -> £3,381,673.74 (10.4%); £3,772,265.43 -> £3,381,673.79 (10.4%); £3,772,265.71 -> £3,381,673.82 (10.4%); £3,772,265.98 -> £3,381,673.86 (10.4%); £3,772,266.24 -> £3,381,673.86 (10.4%); £3,772,266.52 -> £3,381,673.86 (10.4%); £3,772,266.78 -> £3,381,673.86 (10.4%); £3,772,267.06 -> £3,381,673.85 (10.4%); £3,772,267.34 -> £3,381,673.85 (10.4%); £3,772,267.61 -> £3,381,673.85 (10.4%); £3,772,267.88 -> £3,381,673.85 (10.4%); £3,772,268.15 -> £3,381,673.85 (10.4%); £3,772,268.42 -> £3,381,673.85 (10.4%); £3,772,268.68 -> £3,381,673.85 (10.4%); £3,772,268.95 -> £3,381,673.88 (10.4%); £3,772,269.22 -> £3,381,673.94 (10.4%); £3,772,269.49 -> £3,381,674.01 (10.4%); £3,772,269.76 -> £3,381,674.07 (10.4%); £3,772,270.03 -> £3,381,674.14 (10.4%); £3,772,270.31 -> £3,381,674.20 (10.4%); £3,772,270.58 -> £3,381,674.29 (10.4%); £3,772,270.85 -> £3,381,674.37 (10.4%); £3,772,271.11 -> £3,381,674.34 (10.4%); £3,772,271.38 -> £3,381,674.32 (10.4%); £3,772,271.67 -> £3,381,674.30 (10.4%); £3,772,271.94 -> £3,381,674.28 (10.4%); £3,772,272.21 -> £3,381,674.27 (10.4%); £3,772,272.47 -> £3,381,674.26 (10.4%); £3,772,272.73 -> £3,381,674.26 (10.4%); £3,772,272.96 -> £3,381,674.25 (10.4%)
- Bills issued: 153, average clarity 0.816, average bill shock 16.1%, bad debt provision £225.09, avg complaint probability 4.6%
- Solvency signal: £343,201/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £199,425.77 vs. naked (unhedged) net margin: £604,483.06
- hedging cost £405,057.29 vs. a fully unhedged book (commodity-only: actual net £199,425.77 vs. naked net £604,483.06)
  - C1_2: actual £207.67 vs. naked £705.98 -- hedging cost £498.32
  - C2: actual £176.70 vs. naked £611.57 -- hedging cost £434.86
  - C2g: actual £222.14 vs. naked £377.42 -- hedging cost £155.28
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £275.16 vs. naked £1,386.87 -- hedging cost £1,111.71
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £18,349.13 vs. naked £119,157.58 -- hedging cost £100,808.45
  - C_IC3g: actual £3,837.46 vs. naked £56,934.03 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £102,722.50 -- hedging cost £101,286.98

**Year narrative:** 2024 produced a net gain of £347,473.07 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 41 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £120,993.06 (gross £518,611.47, capital £5,646.89)
  - Electricity: gross £464,863.13, capital £5,633.65, net £116,452.84
  - Gas: gross £53,748.34, capital £13.23, net £4,540.22
- Treasury at year end: £3,827,153.05
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
- Average CLV (Point-in-Time, year-end 2025): £363,927.92
  - By billing account: C1 £3,792.48, C1_2 £3,231.42, C2 £4,578.71, C3 £4,030.87, C4 £2,396.32, C5 £6,979.68, C6 £12,243.27, C7 £5,719.17, C8 £6,406.68, C9 £6,652.88, C_IC1 £1,171,265.09, C_IC2 £721,062.52, C_IC3 £2,048,438.91, C_IC4 £1,098,192.89
- Bill shock events (>=20%): 26 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C2 2025-04-30 (22%); C2 2025-06-07 (78%); C2g 2025-01-31 (31%); C2g 2025-02-28 (24%); C2g 2025-04-30 (28%); C2g 2025-05-31 (31%); C2g 2025-06-07 (73%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C1_2 2025-04-30 (42%); C1_2 2025-05-31 (28%); C1_2 2025-06-07 (80%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2 38%, C8 32%, C9 26%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01/MWh, net margin £233.00
- C2 (electricity): tariff £149.29-£301.26/MWh, net margin £53.08
- C2g (gas): tariff £48.32-£52.00/MWh, net margin £90.43
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £19.93
- C8 (electricity): tariff £149.29-£304.72/MWh, net margin £103.10
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £225.43
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £63,404.31
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,994.92
- C_IC3 (electricity): tariff £88.52-£169.00/MWh, net margin £19,935.55
- C_IC3g (gas): tariff £48.22/MWh, net margin £4,449.79
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £2,483.52

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 66, average clarity 0.776, average bill shock 24.6%, bad debt provision £0.00, avg complaint probability 6.0%
- Solvency signal: £425,239/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-20.68 vs. naked (unhedged) net margin: £199.65
- hedging cost £220.33 vs. a fully unhedged book (commodity-only: actual net £-20.68 vs. naked net £199.65)
  - C2: actual £0.57 vs. naked £84.47 -- hedging cost £83.90
  - C2g: actual £8.83 vs. naked £-3.72 -- hedging added £12.55
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £120,993.06 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 26 customer(s) experienced a bill shock of >=20%.
