# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,796,762.45
  (£1,330,126.23 net change)
- Solvency signal (final year): £458,556/customer (8 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £20,009,814.39
  VAT remitted to HMRC: (£961,611.67) | Revenue (ex-VAT): £19,048,202.72
  Non-commodity pass-through: (£4,819,179.70)
- Gross margin: £6,559,770.69
- Capital costs: £236,934.99
- Net margin: £6,322,835.71
- Capital cost ratio: 3.6% of gross
- Net margin as % of revenue: 33.2%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1531, average clarity 0.846,
  service quality score 0.911
- Enterprise value (CLV sum across 14 billing accounts): £6,124,100.98
- Cost to serve (whole portfolio): £91,652.77, net margin after cost to serve: £6,231,182.94
- Hedge effectiveness (whole window): hedging cost £4,044,932.55 vs. a fully unhedged book (commodity-only: actual net £1,330,126.23 vs. naked net £5,375,058.78)

- **2021** (crisis year): net margin £66,331.40, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £276,374.43, 9 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,559,770.69, capital £236,934.99, net £6,322,835.71. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 3.6% (commodity basis, comparable to old model) / 3.6% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £66,331.40 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 33.2%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,322,835.71
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,375,058.78
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,044,932.55 vs. a fully unhedged book (commodity-only: actual net £1,330,126.23 vs. naked net £5,375,058.78)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £103,106.89 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £618,479.04 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £270.67 | £627.01 | £279.81 | £1,177.50 |
| 2017 | £29,240.89 | £0.00 | £230.23 | £824.92 | £459.20 | £30,755.24 |
| 2018 | £104,331.11 | £0.00 | £-217.98 | £569.48 | £374.85 | £105,057.46 |
| 2019 | £225,633.55 | £123.56 | £270.15 | £825.34 | £401.37 | £227,253.97 |
| 2020 | £120,614.18 | £4,057.27 | £273.84 | £935.34 | £406.02 | £126,286.66 |
| 2021 | £67,723.10 | £-1,690.48 | £162.62 | £279.74 | £-143.58 | £66,331.40 |
| 2022 | £327,090.73 | £-47,735.11 | £698.47 | £-2,532.18 | £-1,147.48 | £276,374.43 |
| 2023 | £93,742.01 | £-30,767.46 | £1,061.17 | £129.53 | £-915.99 | £63,249.26 |
| 2024 | £371,274.04 | £-37,199.57 | £407.29 | £2,128.74 | £399.25 | £337,009.76 |
| 2025 | £115,772.43 | £-19,499.39 | £0.00 | £357.52 | £0.00 | £96,630.55 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **50** renewals.  Lost (churned): **6** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.2600 | 0.5500 | 0.8830 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8255 |
| C_IC1 | 2018-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3902 |
| C1 | 2018-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6312 |
| C_IC2 | 2019-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3710 |
| C1 | 2019-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.3500 | 0.5500 | 0.8425 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.5838 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.2000 | 0.5500 | 0.9100 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8723 |
| C2_2 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.7019 |
| C2_2 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.3500 | 0.5500 | 0.8425 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.3751 |
| C2_2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 196.5%
- **Average signed error:** +50.1% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -81.5% | 81.5% |
| 2017 | 3 | -93.6% | 93.6% |
| 2018 | 4 | +403.5% | 496.5% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | +25.4% | 189.5% |
| 2021 | 9 | -7.4% | 119.1% |
| 2022 | 7 | -21.8% | 111.2% |
| 2023 | 7 | -21.0% | 114.8% |
| 2024 | 7 | +74.1% | 236.6% |
| 2025 | 2 | -94.5% | 94.5% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 33.0%, abs error 311.5%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.9%, abs error 146.4%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.2% | 0.0% | 81.5% |
| 2017 | 0 | 3 | 0.0% | 2.2% | 0.0% | 93.6% |
| 2018 | 2 | 2 | 18.6% | 50.0% | 50.3% | 942.7% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 16.6% | 0.6% | 280.8% | 98.2% |
| 2021 | 3 | 6 | 65.1% | 4.1% | 181.3% | 88.0% |
| 2022 | 0 | 7 | 0.0% | 19.5% | 0.0% | 111.2% |
| 2023 | 2 | 5 | 21.5% | 19.0% | 45.4% | 142.6% |
| 2024 | 3 | 4 | 35.6% | 0.0% | 418.7% | 100.0% |
| 2025 | 0 | 2 | 0.0% | 2.1% | 0.0% | 94.5% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 10 (26%)
- **Below/at SVT (protected):** 29 (74%)
- **Mean rate vs SVT premium:** -10.0%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.4% | 131.0 | 140.0 |
| 2017 | 3 | 0 (0%) | -13.5% | 121.0 | 140.0 |
| 2018 | 2 | 2 (100%) | +1.9% | 155.4 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.4% | 126.1 | 178.5 |
| 2020 | 5 | 0 (0%) | -25.7% | 131.3 | 176.9 |
| 2021 | 6 | 3 (50%) | +0.8% | 184.2 | 183.8 |
| 2022 | 7 | 4 (57%) | +11.5% | 294.6 | 318.4 |
| 2023 | 5 | 0 (0%) | -31.6% | 227.9 | 364.0 |
| 2024 | 4 | 0 (0%) | -16.3% | 205.6 | 246.9 |
| 2025 | 2 | 1 (50%) | -4.8% | 236.6 | 248.6 |

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
| 2016 | 17 | 15.1% | 28.9% |
| 2017 | 14 | 16.6% | 48.0% |
| 2018 | 16 | 12.2% | 27.4% |
| 2019 | 19 | 11.1% | 36.9% |
| 2020 | 22 | 12.7% | 33.2% |
| 2021 | 17 | 14.5% | 44.2% |
| 2022 | 15 | 10.3% | 23.3% |
| 2023 | 14 | 19.9% | 41.3% |
| 2024 | 13 | 9.8% | 23.8% |
| 2025 | 2 | 32.9% | 32.9% |

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
| 2016 | 3 | 0.81× | 0.82× |
| 2017 | 3 | 0.94× | 0.94× |
| 2018 | 4 | 4.97× ⚠ | 18.00× |
| 2019 | 4 | 5.25× ⚠ | 18.00× |
| 2020 | 10 | 1.90× | 10.74× |
| 2021 | 9 | 1.19× | 3.75× |
| 2022 | 7 | 1.11× | 3.13× |
| 2023 | 7 | 1.15× | 3.13× |
| 2024 | 7 | 2.37× ⚠ | 10.88× |
| 2025 | 2 | 0.94× | 1.00× |

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
| 2020 | 13 | 0.7% | 3.5% |
| 2021 | 11 | 1.0% | 4.2% |
| 2022 | 9 | 1.9% | 7.5% |
| 2023 | 9 | 1.5% | 4.6% |
| 2024 | 9 | 1.6% | 4.4% |
| 2025 | 2 | 1.4% | 2.1% |

**86** of **86** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **7** (6 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.35, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.32, company est=0.04 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.80 |
| 2022-03-31 | CHURN | C2 | SIM p=0.20, company est=0.07 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.12 |
| 2024-09-29 | CHURN | C4 | SIM p=0.35, company est=0.00 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 1 accounts | 0 active | yes |
| 2021-12-31 | 3 accounts | 0 active | yes |
| 2022-12-31 | 4 accounts | 1 active | yes |
| 2023-12-31 | 4 accounts | 1 active | yes |
| 2024-12-31 | 6 accounts | 1 active | yes |
| 2025-12-31 | 6 accounts | 1 active | yes |

## Policy Costs — RO + CfD + CCL + CM + FiT + Mutualization (Phase 21a/27b/30a/31a/54)

Electricity policy costs deducted from net_margin_gbp each year. 
CfD levy was NEGATIVE in 2022 (crisis rebate from LCCC). 
CCL applies to business (SME/I&C) only — resi exempt. 
CM (Capacity Market) and FiT (Feed-in Tariff) levies apply to ALL demand including domestic.

| Year | RO levy £ | CfD levy £ | CCL £ | CM levy £ | FiT levy £ | Mutualization £ | Total policy cost £ | Note |
|------|-----------|------------|-------|-----------|-----------------|---------------------|------|---------------------|
| 2016 | 1,104 | 7 | 172 | 35 | 290 | 0 | 1,608 |  |
| 2017 | 37,269 | 2,715 | 11,202 | 1,981 | 9,969 | 0 | 63,137 |  |
| 2018 | 65,813 | 9,922 | 17,518 | 9,388 | 17,364 | 0 | 120,006 |  |
| 2019 | 164,970 | 28,414 | 42,551 | 32,030 | 44,393 | 0 | 312,359 |  |
| 2020 | 239,071 | 35,455 | 69,576 | 56,655 | 70,153 | 0 | 470,911 |  |
| 2021 | 248,968 | 15,148 | 72,020 | 50,135 | 63,418 | 41,809 | 491,497 |  |
| 2022 | 259,219 | -50,329 | 71,820 | 37,160 | 69,888 | 100,658 | 488,416 | ⬇ CfD REBATE |
| 2023 | 274,511 | 65,413 | 72,465 | 51,388 | 75,835 | 13,888 | 553,500 |  |
| 2024 | 310,641 | 111,033 | 73,601 | 69,371 | 83,376 | 2,019 | 650,040 |  |
| 2025 | 137,698 | 47,631 | 31,649 | 31,480 | 36,676 | 866 | 286,000 |  |
| **Total** | **1,739,265** | **265,410** | **462,574** | **339,624** | **471,362** | **159,239** | **3,437,474** | |

Total policy cost: £3,437,474 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

## Network Charges — DUoS + TNUoS (Phase 29a)

Electricity network charges deducted from net_margin_gbp each year. 
Resi/SME: combined DUoS + TNUoS unit rate (largest single non-commodity cost). 
I&C HV: DUoS only (Triad TNUoS is an annual lump tracked in the Triad section).

| Year | Network cost £ | Note |
|------|----------------|------|
| 2016 | 3,043 |  |
| 2017 | 26,091 |  |
| 2018 | 38,576 |  |
| 2019 | 88,410 |  |
| 2020 | 124,684 |  |
| 2021 | 124,577 |  |
| 2022 | 134,423 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 140,145 | RIIO-ED2 from Apr 2023 |
| 2024 | 144,374 |  |
| 2025 | 61,948 |  |
| **Total** | **886,273** | |

Total network cost: £886,273 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

## Gas Policy Costs and Network Charges (Phase 30b)

Gas CCL: non-domestic only (domestic gas exempt). Gas network (GDN + NTS): all on unit rate.
GGL (Green Gas Levy): per-meter, from Nov 2021; tiny in £/MWh terms.

| Year | Gas Policy (CCL + GGL) £ | Gas Network £ | Total Gas Non-Commodity £ |
|------|--------------------------|---------------|--------------------------|
| 2016 | 0 | 376 | 376 |
| 2017 | 0 | 733 | 733 |
| 2018 | 0 | 687 | 687 |
| 2019 | 15,155 | 50,183 | 65,338 |
| 2020 | 19,468 | 47,120 | 66,588 |
| 2021 | 22,472 | 50,292 | 72,764 |
| 2022 | 27,045 | 54,396 | 81,442 |
| 2023 | 32,229 | 79,676 | 111,905 |
| 2024 | 37,495 | 76,431 | 113,925 |
| 2025 | 17,243 | 31,816 | 49,059 |
| **Total** | **171,107** | **391,711** | **562,817** |

Gas policy pass-through in tariff unit rate (CCL + GGL at term start); gas network pass-through likewise. Net basis risk near-zero for annual contracts.


## Gas Book P&L — Year by Year (Phase 32a)

Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.
Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.

| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |
|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|
| 2016 | 1,134 | 450 | 684 | 0 | 376 | 5 | 280 | +24.7% |
| 2017 | 2,246 | 998 | 1,248 | 0 | 733 | 10 | 459 | +20.4% |
| 2018 | 2,453 | 1,327 | 1,126 | 0 | 687 | 15 | 375 | +15.3% |
| 2019 | 137,113 | 61,310 | 75,803 | 15,155 | 50,183 | 9,218 | 525 | +0.4% |
| 2020 | 120,908 | 43,840 | 77,068 | 19,468 | 47,120 | 5,385 | 4,463 | +3.7% |
| 2021 | 297,512 | 214,817 | 82,696 | 22,472 | 50,292 | 10,223 | -1,834 | -0.6% |
| 2022 | 588,198 | 497,742 | 90,456 | 27,045 | 54,396 | 51,897 | -48,883 | -8.3% |
| 2023 | 297,014 | 175,869 | 121,145 | 32,229 | 79,676 | 39,335 | -31,683 | -10.7% |
| 2024 | 270,480 | 146,066 | 124,413 | 37,495 | 76,431 | 45,903 | -36,800 | -13.6% |
| 2025 | 132,454 | 78,945 | 53,509 | 17,243 | 31,816 | 23,287 | -19,499 | -14.7% |
| **Total** | **1,849,511** | **1,221,365** | **628,147** | **171,107** | **391,711** | **185,279** | **-132,598** | **-7.2%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,408 | 9 | 274,156 | 2108.89× | OK |
| 2017 | 2,497,896 | 10 | 249,790 | 1921.46× | OK |
| 2018 | 2,486,492 | 11 | 226,045 | 1738.81× | OK |
| 2019 | 2,612,500 | 12 | 217,708 | 1674.68× | OK |
| 2020 | 2,918,729 | 13 | 224,518 | 1727.06× | OK |
| 2021 | 2,946,937 | 12 | 245,578 | 1889.06× | OK |
| 2022 | 3,115,771 | 11 | 283,252 | 2178.86× | OK |
| 2023 | 3,233,014 | 10 | 323,301 | 2486.93× | OK |
| 2024 | 3,613,542 | 10 | 361,354 | 2779.65× | OK |
| 2025 | 3,668,447 | 8 | 458,556 | 3527.35× | OK |

End-state (2025): **£458,556/account** across 8 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 23 | 28 | 2,467,408 | 88090.2× | OK |
| 2017 | 466 | 559 | 2,497,896 | 4467.0× | OK |
| 2018 | 851 | 1,021 | 2,486,492 | 2436.1× | OK |
| 2019 | 1,543 | 1,851 | 2,612,500 | 1411.1× | OK |
| 2020 | 1,979 | 2,375 | 2,918,729 | 1228.8× | OK |
| 2021 | 4,413 | 5,295 | 2,946,937 | 556.5× | OK |
| 2022 | 8,509 | 10,211 | 3,115,771 | 305.1× | OK |
| 2023 | 5,610 | 6,732 | 3,233,014 | 480.2× | OK |
| 2024 | 2,738 | 3,286 | 3,613,542 | 1099.8× | OK |
| 2025 | 4,192 | 5,031 | 3,668,447 | 729.2× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,526.20 | £12,268.14 | £262.80/MWh | £145.03/MWh | +2.9% |
| C8 | 106,722 | 43,948 | 41.2% | £11,998.79 | £9,712.48 | £273.02/MWh | £154.72/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,949.86 | £9,323.63 | £250.63/MWh | £141.92/MWh | +10.9% |

Total HH revenue: £63,779.10 vs flat equivalent £58,872.88 (+8.3% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 33 | 100% | C8 (2016-10-31) |
| 2017 | 48 | 81% | C8 (2017-11-30) |
| 2018 | 56 | 89% | C4g (2018-10-31) |
| 2019 | 57 | 129% | C_IC1 (2019-03-31) |
| 2020 | 50 | 120% | C_IC2 (2020-03-31) |
| 2021 | 51 | 98% | C4g (2021-10-31) |
| 2022 | 56 | 1735% | C2_2 (2022-04-30) |
| 2023 | 42 | 102% | C_IC2 (2023-06-30) |
| 2024 | 32 | 109% | C_IC2 (2024-07-31) |
| 2025 | 20 | 80% | C7 (2025-06-07) |

Total: **445** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1735% | no |
| 2022-10-31 | C4g | +217% | no |
| 2019-03-31 | C_IC1 | +129% | no |
| 2020-03-31 | C_IC2 | +120% | no |
| 2022-01-31 | C_IC3 | +111% | no |
| 2024-07-31 | C_IC2 | +109% | no |
| 2023-06-30 | C_IC2 | +102% | no |
| 2016-10-31 | C8 | +100% | no |
| 2021-10-31 | C4g | +98% | no |
| 2023-10-31 | C8 | +92% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 12% | 12% | 0 |
| 2017 | 4 | 16% | 22% | 2 ⚠ |
| 2018 | 4 | 16% | 22% | 1 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 5 | 5% | 23% | 1 ⚠ |
| 2021 | 3 | 69% | 95% | 3 ⚠ |
| 2022 | 2 | 49% | 95% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 1 | 4% | 4% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £19.8 | £122.4 (+517%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £16.1 | £35.0 (+118%) | 74% |
| 2021-03-31 | C2g | £21.7 | £35.0 (+62%) | 40% |
| 2020-12-31 | C_IC3g | £15.4 | £19.8 (+28%) | 23% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 18 |
| Retained | 17 (94%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £428,290.64 |
| Margin saved (retained customers' terms) | £2,301,398.30 |
| Wasted offer cost (churned anyway) | £507.36 |
| **Net ROI of retention strategy** | **£1,873,107.66** |
| Acquisition cost avoided (retained customers) | £2,800.00 |
| **Full economic ROI (margin + acq savings)** | **£1,875,907.66** |

Missed opportunities (churns with no offer): **5** (£3,611.75 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 5 (£3,611.75 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24755.56 | £169470.94 | £144715.38 | £0.00 |
| 2019 | 2 | 2 | £43702.07 | £306529.83 | £262827.76 | £0.00 |
| 2020 | 3 | 3 | £27214.81 | £170827.13 | £143612.32 | £376.87 |
| 2021 | 4 | 3 | £122665.73 | £438526.63 | £315860.90 | £-142.51 |
| 2022 | 2 | 2 | £75211.36 | £338676.57 | £263465.20 | £320.54 |
| 2023 | 4 | 4 | £89626.27 | £460979.53 | £371353.26 | £0.00 |
| 2024 | 2 | 2 | £45114.83 | £416387.67 | £371272.84 | £3056.85 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24755.56 | £169470.94 | £150 | £144715.38 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £15172.47 | £105268.85 | £150 | £90096.38 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £28529.60 | £201260.98 | £150 | £172731.38 | retained |
| 2020-01-01 | C_IC3 | 0.36 | 3% | £5744.15 | £11180.13 | £150 | £5435.98 | retained |
| 2020-03-31 | C_IC1 | 0.52 | 5% | £10690.67 | £137077.64 | £150 | £126386.97 | retained |
| 2020-12-31 | C_IC3 | 0.59 | 5% | £10779.99 | £22569.36 | £150 | £11789.37 | retained |
| 2021-03-31 | C_IC2 | 0.84 | 8% | £14501.33 | £95041.14 | £150 | £80539.80 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £23083.55 | £164502.88 | £150 | £141419.32 | retained |
| 2021-12-30 | C5 | 0.80 | 8% | £507.36 | £2209.80 | £400 | £-507.36 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £84573.49 | £178982.62 | £150 | £94409.13 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25705.89 | £99672.53 | £150 | £73966.64 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £49505.47 | £239004.03 | £150 | £189498.56 | retained |
| 2023-03-31 | C6 | 0.34 | 3% | £184.42 | £2605.53 | £400 | £2421.12 | retained |
| 2023-05-30 | C_IC2 | 0.59 | 5% | £12010.81 | £135089.45 | £150 | £123078.64 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £35647.56 | £252392.01 | £150 | £216744.45 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £41783.48 | £70892.53 | £150 | £29109.05 | retained |
| 2024-06-28 | C_IC2 | 0.55 | 5% | £10497.77 | £137873.24 | £150 | £127375.46 | retained |
| 2024-07-28 | C_IC1 | 0.95 | 8% | £34617.06 | £278514.43 | £150 | £243897.38 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C_IC1 | 2018-01-31 | (window end) | 95 | active |
| C_IC2 | 2019-01-31 | (window end) | 83 | active |
| C_IC3 | 2020-01-01 | (window end) | 72 | active |
| C5 | 2021-12-30 | 2021-12-30 | 0 | churned |
| C6 | 2023-03-31 | 2024-03-30 | 12 | churned |

**Eventually churned (2/5)**: C5, C6 — avg 6 months post-retention before final churn.
**Still active (3/5)**: C_IC1, C_IC2, C_IC3 — survived to simulation end.

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £6,124,100.98 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £476,905.21 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,177.50 |
| 2017 | £30,755.24 |
| 2018 | £105,057.46 |
| 2019 | £227,253.97 |
| 2020 | £126,286.66 |
| 2021 | £66,331.40 |
| 2022 | £276,374.43 |
| 2023 | £63,249.26 | ← trailing
| 2024 | £337,009.76 | ← trailing
| 2025 | £96,630.55 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £3,056.29 | — |
| C2 | £5,905.49 | — |
| C2_2 | — | £991.30 |
| C3 | £3,650.41 | — |
| C4 | £3,652.82 | £-587.04 |
| C5 | £8,521.50 | — |
| C6 | £12,162.52 | £2,111.84 |
| C7 | £6,701.91 | £110.45 |
| C8 | £7,280.54 | £373.30 |
| C9 | £7,583.35 | £928.79 |
| C_IC1 | £1,495,354.29 | £351,773.41 |
| C_IC2 | £807,014.06 | £185,962.36 |
| C_IC3 | £2,502,785.06 | £-73,087.61 |
| C_IC4 | £1,256,940.24 | £8,328.40 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £1,444.98 | — | — | — | — | £4,331.57 | — | £3,079.54 | — | — | — | — | — | — |
| 2017 | £1,548.13 | £4,394.09 | — | £2,682.82 | £3,319.32 | £4,517.61 | £6,792.39 | £3,225.06 | £4,669.48 | £4,052.59 | — | — | — | — |
| 2018 | £1,632.14 | £3,847.39 | — | £2,350.47 | £2,627.76 | £4,397.76 | £5,613.24 | £3,117.75 | £3,932.88 | £3,771.34 | £972,885.68 | — | — | — |
| 2019 | £1,659.60 | £3,509.28 | — | £2,399.03 | £2,842.67 | £4,505.64 | £5,993.07 | £3,288.66 | £3,971.93 | £3,788.76 | £912,393.83 | £528,309.92 | — | — |
| 2020 | £1,886.74 | £3,847.49 | — | £1,989.25 | £2,973.10 | £5,712.27 | £5,998.90 | £3,397.41 | £4,504.85 | £3,980.61 | £642,144.17 | £314,904.00 | £1,168,616.62 | £630,951.46 |
| 2021 | £1,749.22 | £4,159.51 | — | £2,139.23 | £2,692.43 | £4,815.52 | £7,221.80 | £3,221.33 | £4,300.47 | £3,557.89 | £598,759.19 | £365,244.32 | £1,046,985.16 | £636,545.09 |
| 2022 | £1,947.09 | £3,211.67 | £481.52 | £2,145.36 | £1,849.17 | £4,996.20 | £6,712.37 | £2,855.43 | £4,113.08 | £3,955.26 | £671,265.90 | £392,525.35 | £1,191,438.07 | £607,608.83 |
| 2023 | £1,941.34 | £3,194.95 | £1,343.76 | £2,138.47 | £1,599.55 | £4,974.95 | £7,326.05 | £3,034.13 | £4,174.53 | £4,224.05 | £724,597.17 | £420,197.79 | £1,109,960.58 | £626,935.90 |
| 2024 | £1,799.01 | £3,517.48 | £1,963.52 | £2,080.31 | £2,023.53 | £4,359.75 | £6,752.15 | £3,394.86 | £5,106.00 | £4,600.76 | £754,804.99 | £445,210.48 | £1,455,486.31 | £685,362.03 |
| 2025 | £1,780.50 | £3,394.44 | £2,090.13 | £2,182.09 | £2,092.62 | £4,810.21 | £7,131.43 | £3,580.15 | £4,164.23 | £4,565.47 | £793,267.70 | £460,165.18 | £1,425,379.65 | £798,677.52 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,823.83, range £48.79–£26,606.21.

- C1: cost to serve £399.77, net margin after CTS £1,897.10
- C1g: cost to serve £50.42, net margin after CTS £1,186.74
- C2: cost to serve £463.92, net margin after CTS £3,953.61
- C2_2: cost to serve £381.63, net margin after CTS £5,107.92
- C2g: cost to serve £77.84, net margin after CTS £1,818.01
- C3: cost to serve £269.41, net margin after CTS £1,402.34
- C3g: cost to serve £48.79, net margin after CTS £1,062.48
- C4: cost to serve £611.70, net margin after CTS £3,771.25
- C4g: cost to serve £189.08, net margin after CTS £1,066.54
- C5: cost to serve £872.44, net margin after CTS £8,558.37
- C6: cost to serve £1,274.35, net margin after CTS £16,967.72
- C7: cost to serve £955.02, net margin after CTS £9,841.05
- C8: cost to serve £939.66, net margin after CTS £11,534.06
- C9: cost to serve £897.19, net margin after CTS £11,827.23
- C_IC1: cost to serve £20,241.79, net margin after CTS £1,917,151.16
- C_IC2: cost to serve £11,547.68, net margin after CTS £929,512.89
- C_IC3: cost to serve £26,606.21, net margin after CTS £1,813,593.75
- C_IC3g: cost to serve £9,229.97, net margin after CTS £613,417.06
- C_IC4: cost to serve £16,595.90, net margin after CTS £1,100,681.25


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 29 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 13.8%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,749.07 | £10,901.23 | +20.0% | £112.24/MWh | £151.71/MWh |
| C5 | electricity | 2018-12-31 | £-212.22 | £2,316.48 | +4.2% | £148.68/MWh | £153.11/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,332.71 | £6,376.41 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,269.51 | £10,243.03 | +20.0% | £128.22/MWh | £175.35/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,922.12 | £3,444.18 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £177.33/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.28/MWh |
| C4g | gas | 2021-09-30 | £-29.70 | £543.78 | +0.5% | £53.99/MWh | £55.39/MWh |
| C5 | electricity | 2021-12-30 | £-295.16 | £2,749.60 | +5.7% | £311.83/MWh | £336.07/MWh |
| C7 | electricity | 2021-12-30 | £-127.06 | £1,982.90 | +1.4% | £311.83/MWh | £322.32/MWh |
| C_IC3 | electricity | 2021-12-31 | £-28,228.78 | £446,958.69 | +1.3% | £224.03/MWh | £261.02/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £316.61/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £307.29/MWh |
| C4 | electricity | 2022-09-30 | £-348.64 | £1,173.21 | +20.0% | £404.86/MWh | £487.14/MWh |
| C4g | gas | 2022-09-30 | £-768.05 | £927.70 | +20.0% | £183.79/MWh | £252.43/MWh |
| C7 | electricity | 2022-12-30 | £-1,835.40 | £2,404.50 | +20.0% | £266.73/MWh | £320.50/MWh |
| C_IC3g | gas | 2022-12-31 | £-48,818.20 | £586,562.16 | +3.3% | £101.23/MWh | £120.28/MWh |
| C8 | electricity | 2023-03-31 | £-353.94 | £3,898.74 | +4.1% | £319.17/MWh | £335.44/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £235.96/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £219.80/MWh |
| C4 | electricity | 2023-09-30 | £-502.57 | £1,888.68 | +20.0% | £216.77/MWh | £257.62/MWh |
| C4g | gas | 2023-09-30 | £-1,691.04 | £2,450.86 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-351.18 | £3,990.91 | +3.8% | £242.22/MWh | £238.85/MWh |
| C_IC3 | electricity | 2023-12-31 | £-167,772.11 | £941,583.47 | +12.8% | £118.95/MWh | £127.49/MWh |
| C_IC3g | gas | 2023-12-31 | £-30,262.44 | £295,562.62 | +5.2% | £51.89/MWh | £60.86/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |
| C_IC3g | gas | 2024-12-30 | £-36,843.35 | £268,211.20 | +8.7% | £50.47/MWh | £61.52/MWh |


## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 112 renewal(s) (26 gas) based on recent portfolio-wide margin rates: 60 surcharge(s), 52 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | 7.8% | +0.1% | £131.49/MWh | £131.62/MWh |
| C1g | gas | 2016-12-31 | 22.7% | -5.0% | £27.63/MWh | £26.25/MWh |
| C5 | electricity | 2016-12-31 | 9.7% | -0.8% | £131.49/MWh | £130.38/MWh |
| C7 | electricity | 2016-12-31 | 8.8% | -0.4% | £131.49/MWh | £130.93/MWh |
| C2 | electricity | 2017-04-01 | 12.0% | -2.0% | £127.97/MWh | £125.43/MWh |
| C2g | gas | 2017-04-01 | 22.6% | -5.0% | £34.54/MWh | £32.81/MWh |
| C6 | electricity | 2017-04-01 | 9.9% | -0.9% | £127.97/MWh | £126.75/MWh |
| C8 | electricity | 2017-04-01 | 9.5% | -0.8% | £127.97/MWh | £127.00/MWh |
| C3 | electricity | 2017-07-01 | 10.8% | -1.4% | £122.23/MWh | £120.51/MWh |
| C3g | gas | 2017-07-01 | 23.4% | -5.0% | £24.33/MWh | £23.11/MWh |
| C9 | electricity | 2017-07-01 | 11.6% | -1.8% | £122.23/MWh | £120.02/MWh |
| C4 | electricity | 2017-10-01 | 12.2% | -2.1% | £111.62/MWh | £109.29/MWh |
| C4g | gas | 2017-10-01 | 21.5% | -5.0% | £27.48/MWh | £26.10/MWh |
| C1 | electricity | 2017-12-31 | 11.7% | -1.8% | £120.10/MWh | £117.88/MWh |
| C1g | gas | 2017-12-31 | 19.1% | -5.0% | £34.79/MWh | £33.05/MWh |
| C5 | electricity | 2017-12-31 | 9.5% | -0.8% | £120.10/MWh | £119.18/MWh |
| C7 | electricity | 2017-12-31 | 3.1% | +2.4% | £120.10/MWh | £123.03/MWh |
| C_IC1 | electricity | 2018-01-31 | -17.3% | +12.6% | £112.24/MWh | £126.42/MWh |
| C2 | electricity | 2018-04-01 | -5.7% | +6.8% | £133.89/MWh | £143.07/MWh |
| C2g | gas | 2018-04-01 | 18.6% | -5.0% | £38.21/MWh | £36.30/MWh |
| C6 | electricity | 2018-04-01 | -4.5% | +6.2% | £133.89/MWh | £142.26/MWh |
| C8 | electricity | 2018-04-01 | 7.9% | +0.1% | £133.89/MWh | £133.95/MWh |
| C3 | electricity | 2018-07-01 | 10.4% | -1.2% | £128.29/MWh | £126.73/MWh |
| C3g | gas | 2018-07-01 | 16.8% | -4.4% | £29.63/MWh | £28.32/MWh |
| C9 | electricity | 2018-07-01 | 3.0% | +2.5% | £128.29/MWh | £131.48/MWh |
| C4 | electricity | 2018-10-01 | 4.2% | +1.9% | £145.00/MWh | £147.72/MWh |
| C4g | gas | 2018-10-01 | 16.5% | -4.2% | £34.60/MWh | £33.13/MWh |
| C1 | electricity | 2018-12-31 | 7.7% | +0.2% | £148.68/MWh | £148.91/MWh |
| C1g | gas | 2018-12-31 | 16.0% | -4.0% | £37.15/MWh | £35.66/MWh |
| C5 | electricity | 2018-12-31 | 10.3% | -1.1% | £148.68/MWh | £146.99/MWh |
| C7 | electricity | 2018-12-31 | 9.8% | -0.9% | £148.68/MWh | £147.33/MWh |
| C_IC2 | electricity | 2019-01-31 | -29.4% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -19.9% | +14.0% | £128.22/MWh | £146.12/MWh |
| C2 | electricity | 2019-04-01 | 3.8% | +2.1% | £148.35/MWh | £151.47/MWh |
| C2g | gas | 2019-04-01 | 10.8% | -1.4% | £32.94/MWh | £32.48/MWh |
| C6 | electricity | 2019-04-01 | 7.5% | +0.2% | £148.35/MWh | £148.73/MWh |
| C8 | electricity | 2019-04-01 | 27.0% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 19.3% | -5.0% | £127.03/MWh | £120.68/MWh |
| C3g | gas | 2019-07-01 | 13.4% | -2.7% | £23.62/MWh | £22.98/MWh |
| C9 | electricity | 2019-07-01 | 10.9% | -1.4% | £127.03/MWh | £125.20/MWh |
| C4 | electricity | 2019-10-01 | 9.8% | -0.9% | £126.72/MWh | £125.59/MWh |
| C4g | gas | 2019-10-01 | 17.5% | -4.8% | £20.41/MWh | £19.44/MWh |
| C1 | electricity | 2019-12-31 | 11.2% | -1.6% | £127.44/MWh | £125.39/MWh |
| C1g | gas | 2019-12-31 | 14.0% | -3.0% | £26.17/MWh | £25.38/MWh |
| C5 | electricity | 2019-12-31 | 11.5% | -1.7% | £127.44/MWh | £125.22/MWh |
| C7 | electricity | 2019-12-31 | 8.8% | -0.4% | £127.44/MWh | £126.92/MWh |
| C_IC3 | electricity | 2020-01-01 | 7.0% | +0.5% | £47.59/MWh | £47.82/MWh |
| C_IC3g | gas | 2020-01-01 | 23.2% | -5.0% | £16.25/MWh | £15.44/MWh |
| C_IC2 | electricity | 2020-03-01 | -59.3% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -51.5% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 19.8% | -5.0% | £22.80/MWh | £21.66/MWh |
| C6 | electricity | 2020-03-31 | -47.3% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -16.1% | +12.1% | £125.12/MWh | £140.21/MWh |
| C_IC1 | electricity | 2020-03-31 | 20.2% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 16.8% | -4.4% | £113.43/MWh | £108.42/MWh |
| C9 | electricity | 2020-06-30 | 16.8% | -4.4% | £113.43/MWh | £108.42/MWh |
| C4 | electricity | 2020-09-30 | 11.8% | -1.9% | £124.42/MWh | £122.03/MWh |
| C4g | gas | 2020-09-30 | 21.2% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 9.2% | -0.6% | £133.55/MWh | £132.72/MWh |
| C1g | gas | 2020-12-30 | 16.0% | -4.0% | £28.99/MWh | £27.83/MWh |
| C5 | electricity | 2020-12-30 | 5.1% | +1.5% | £133.55/MWh | £135.52/MWh |
| C7 | electricity | 2020-12-30 | -2.7% | +5.3% | £133.55/MWh | £140.69/MWh |
| C_IC3 | electricity | 2020-12-31 | -4.0% | +6.0% | £50.65/MWh | £53.68/MWh |
| C_IC3g | gas | 2020-12-31 | 10.1% | -1.1% | £20.05/MWh | £19.83/MWh |
| C2 | electricity | 2021-03-31 | -20.9% | +14.5% | £175.90/MWh | £201.32/MWh |
| C2g | gas | 2021-03-31 | 9.3% | -0.7% | £36.20/MWh | £35.96/MWh |
| C6 | electricity | 2021-03-31 | -16.6% | +12.3% | £175.90/MWh | £197.50/MWh |
| C8 | electricity | 2021-03-31 | -12.1% | +10.0% | £175.90/MWh | £193.55/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.8% | +6.4% | £138.90/MWh | £147.77/MWh |
| C_IC1 | electricity | 2021-04-30 | 1.4% | +3.3% | £113.97/MWh | £117.73/MWh |
| C9 | electricity | 2021-06-30 | 1.8% | +3.1% | £170.38/MWh | £175.70/MWh |
| C4 | electricity | 2021-09-30 | -1.8% | +4.9% | £205.15/MWh | £215.22/MWh |
| C4g | gas | 2021-09-30 | 3.8% | +2.1% | £53.99/MWh | £55.13/MWh |
| C1 | electricity | 2021-12-30 | 4.1% | +1.9% | £311.83/MWh | £317.84/MWh |
| C5 | electricity | 2021-12-30 | 4.1% | +1.9% | £311.83/MWh | £317.84/MWh |
| C7 | electricity | 2021-12-30 | 4.1% | +1.9% | £311.83/MWh | £317.84/MWh |
| C_IC3 | electricity | 2021-12-31 | -23.9% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -15.6% | +11.8% | £109.48/MWh | £122.38/MWh |
| C2 | electricity | 2022-03-31 | -24.3% | +15.0% | £361.95/MWh | £416.24/MWh |
| C6 | electricity | 2022-03-31 | -16.7% | +12.3% | £361.95/MWh | £406.61/MWh |
| C8 | electricity | 2022-03-31 | 5.4% | +1.3% | £361.95/MWh | £366.60/MWh |
| C_IC2 | electricity | 2022-04-30 | -9.4% | +8.7% | £269.81/MWh | £293.30/MWh |
| C_IC1 | electricity | 2022-05-30 | -5.9% | +7.0% | £239.42/MWh | £256.08/MWh |
| C9 | electricity | 2022-06-30 | 4.6% | +1.7% | £255.09/MWh | £259.38/MWh |
| C4 | electricity | 2022-09-30 | 7.5% | +0.3% | £404.86/MWh | £405.95/MWh |
| C4g | gas | 2022-09-30 | -20.9% | +14.5% | £183.79/MWh | £210.36/MWh |
| C7 | electricity | 2022-12-30 | 7.7% | +0.1% | £266.73/MWh | £267.08/MWh |
| C_IC3 | electricity | 2022-12-31 | -1.0% | +4.5% | £168.36/MWh | £175.92/MWh |
| C_IC3g | gas | 2022-12-31 | -38.3% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -13.1% | +10.6% | £319.17/MWh | £352.89/MWh |
| C6 | electricity | 2023-03-31 | -0.8% | +4.4% | £319.17/MWh | £333.16/MWh |
| C8 | electricity | 2023-03-31 | 6.0% | +1.0% | £319.17/MWh | £322.30/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.4% | +14.7% | £171.46/MWh | £196.64/MWh |
| C_IC1 | electricity | 2023-06-29 | -16.5% | +12.2% | £163.19/MWh | £183.17/MWh |
| C9 | electricity | 2023-06-30 | -10.0% | +9.0% | £224.44/MWh | £244.69/MWh |
| C4 | electricity | 2023-09-30 | 9.9% | -1.0% | £216.77/MWh | £214.68/MWh |
| C4g | gas | 2023-09-30 | -42.6% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 28.8% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 23.2% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -14.9% | +11.4% | £51.89/MWh | £57.83/MWh |
| C2_2 | electricity | 2024-03-30 | 15.8% | -3.9% | £207.71/MWh | £199.59/MWh |
| C6 | electricity | 2024-03-30 | 10.1% | -1.1% | £207.71/MWh | £205.50/MWh |
| C8 | electricity | 2024-03-30 | 10.1% | -1.1% | £207.71/MWh | £205.50/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.0% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.0% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.7% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 1.0% | +3.5% | £195.97/MWh | £202.85/MWh |
| C7 | electricity | 2024-12-29 | 1.0% | +3.5% | £243.79/MWh | £252.35/MWh |
| C_IC3 | electricity | 2024-12-30 | 19.3% | -5.0% | £116.37/MWh | £110.55/MWh |
| C_IC3g | gas | 2024-12-30 | -16.2% | +12.1% | £50.47/MWh | £56.58/MWh |
| C2_2 | electricity | 2025-03-30 | 9.2% | -0.6% | £284.89/MWh | £283.12/MWh |
| C8 | electricity | 2025-03-30 | 6.0% | +1.0% | £284.89/MWh | £287.67/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **5** | Blind misses: **5** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 4 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £3,611.75 | deliberate: £0.00 | total: £3,611.75

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.35 | Yes | £376.87 |
| C1 | 2021-12-30 | Blind miss | 0.04 | 0.32 | Yes | £-142.51 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.20 | No | £320.54 |
| C6 | 2024-03-30 | Blind miss | 0.12 | 0.38 | Yes | £2,276.78 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.35 | Yes | £780.07 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C2+C2g | £789.43 | £778.94 | £1,568.37 | Yes |
| C1+C1g | £444.92 | £604.06 | £1,048.97 | Yes |
| C3+C3g | £260.81 | £297.26 | £558.07 | Yes |
| C4+C4g | £-140.11 | £-1,566.81 | £-1,706.92 | No |
| C_IC3+C_IC3g | £109,251.69 | £-132,711.18 | £-23,459.49 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-132,597.73.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,330,126.23 across 19 billing accounts. Revenue: £14,215,255.62.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,204,732.77 | £1,937,392.95 | £18,887.88 | £879,288.35 | 27.4% |
| 2 | C_IC2 | fixed | £1,565,900.49 | £941,060.57 | £8,749.02 | £452,196.46 | 28.9% |
| 3 | C_IC3 | pass_through | £4,677,578.04 | £1,840,199.96 | £23,146.89 | £109,251.69 | 2.3% |
| 4 | C_IC4 | flex | £2,775,475.73 | £1,117,277.15 | £0.00 | £14,685.55 | 0.5% |
| 5 | C6 | fixed | £31,457.17 | £18,242.07 | £212.03 | £3,139.29 | 10.0% |
| 6 | C8 | fixed | £21,711.28 | £12,473.71 | £135.32 | £1,519.98 | 7.0% |
| 7 | C9 | fixed | £20,273.49 | £12,724.42 | £129.47 | £1,510.75 | 7.5% |
| 8 | C2_2 | fixed | £10,306.62 | £5,489.55 | £68.16 | £1,059.67 | 10.3% |
| 9 | C2 | fixed | £6,699.16 | £4,417.53 | £31.66 | £789.43 | 11.8% |
| 10 | C2g | fixed | £3,548.31 | £1,895.85 | £17.31 | £778.94 | 22.0% |
| 11 | C1g | fixed | £2,177.12 | £1,237.15 | £14.90 | £604.06 | 27.7% |
| 12 | C1 | fixed | £3,492.09 | £2,296.87 | £15.36 | £444.92 | 12.7% |
| 13 | C3g | fixed | £2,210.40 | £1,111.27 | £9.77 | £297.26 | 13.4% |
| 14 | C3 | fixed | £2,473.19 | £1,671.75 | £9.54 | £260.81 | 10.5% |
| 15 | C5 | fixed | £15,259.36 | £9,430.81 | £77.87 | £17.17 | 0.1% |
| 16 | C4 | fixed | £8,590.41 | £4,382.95 | £52.97 | £-140.11 | -1.6% |
| 17 | C7 | fixed | £21,794.34 | £10,796.07 | £140.00 | £-1,299.99 | -6.0% |
| 18 | C4g | fixed | £8,995.75 | £1,255.63 | £110.11 | £-1,566.81 | -17.4% |
| 19 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £185,126.72 | £-132,711.18 | -7.2% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,215,256 | 100.0% |
| Wholesale cost | -£7,669,252 | 54.0% |
| **Gross supply margin** | **£6,546,003** | **46.0%** |
| Policy + Network costs | -£4,978,942 | 35.0% |
| Capital cost | -£236,935 | 1.7% |
| **Net supply margin** | **£1,330,126** | **9.4%** |

> *The ledger's `net_margin_gbp` (£6,322,836) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,223,687 | 47.7% | 11.9% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | -7.2% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £46,717 | 59.2% | 6.8% | CMA 3-8% | ✓ |
| resi/elec | £85,034 | 57.3% | 3.6% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £16,932 | 32.5% | 0.7% | Ofgem CMA 2-4% | ✓ |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: PASS** — all segments within benchmarks.
## Transaction Log

Total events: 3,297,294

| Event type | Count |
|------------|-------|
| acquisition_gate_event | 1 |
| acquisition_spend_event | 4 |
| bad_debt_event | 1,531 |
| billing_event | 1,531 |
| capital_charge_event | 1,587,774 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,531 |
| payment_received_event | 1,531 |
| settlement_event | 1,701,746 |
| vat_remittance_event | 1,531 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £20,009,814.39 |
|   Less: VAT remitted to HMRC | (£961,611.67) |
| = Revenue (ex-VAT) | £19,048,202.72 |
| Less: non-commodity pass-through | (£4,819,179.70) |
| Wholesale cost (settlement events) | (£7,669,252.33) |
| Gross margin | £6,559,770.69 |
| Capital charges | (£236,934.99) |
| Net margin | £6,322,835.71 |

_Cash reconciliation: of £20,009,814.39 billed, bad debt of £400,162.34 was written off, leaving £19,609,652.05 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £6,884,285.03._

| Acquisition spend | (£1,100.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £6,316,035.71 |

## Management Accounts

P&L and balance sheet from double-entry journal (account codes), not formulas.

| Year | Revenue | COGS | Gross | OpEx | Net | Cash | Equity |
|------|---------|------|-------|------|-----|------|--------||
| 2016 | £14,454.20 | (£6,964.47) | £7,489.73 | (£893.64) | £6,596.08 | £2,470,551.27 | £2,473,232.30 |
| 2017 | £349,371.72 | (£224,488.56) | £124,883.16 | (£8,095.45) | £116,787.71 | £2,558,116.64 | £2,590,020.01 |
| 2018 | £608,239.66 | (£338,329.32) | £269,910.35 | (£14,034.75) | £255,875.60 | £2,790,603.64 | £2,845,895.62 |
| 2019 | £1,656,567.20 | (£943,792.77) | £712,774.42 | (£42,873.36) | £669,901.06 | £3,358,409.35 | £3,515,796.67 |
| 2020 | £1,869,842.12 | (£1,065,843.75) | £803,998.37 | (£46,595.81) | £757,402.56 | £4,089,845.73 | £4,273,199.24 |
| 2021 | £2,451,304.19 | (£1,669,347.93) | £781,956.26 | (£64,418.52) | £717,537.74 | £4,692,734.24 | £4,990,736.98 |
| 2022 | £4,304,823.62 | (£3,221,477.35) | £1,083,346.26 | (£151,261.21) | £932,085.05 | £5,483,671.49 | £5,922,822.03 |
| 2023 | £3,475,138.96 | (£2,542,148.65) | £932,990.31 | (£126,724.16) | £806,266.15 | £6,422,190.69 | £6,729,088.18 |
| 2024 | £3,071,309.68 | (£1,758,225.13) | £1,313,084.54 | (£122,197.12) | £1,190,887.42 | £7,627,111.66 | £7,919,975.61 |
| 2025 | £1,247,151.37 | (£719,130.08) | £528,021.29 | (£66,803.30) | £461,217.99 | £8,381,193.60 | £8,381,193.60 |

**Cross-check:** FAIL -- Journal: £5,914,557.38, Sim: £1,330,126.23, Variance: 344.7%

**Balance sheet -- 2025 year-end:**

| Account | GBP |
|---------|-----|
| Cash and Treasury (1001) | £8,381,193.60 |
| Trade Receivables (1100) | £0.00 |
| **Total Assets** | **£8,381,193.60** |
| Opening Capital (3001) | £2,466,636.22 |
| Cumulative Net Profit | £5,914,557.38 |
| **Total Equity** | **£8,381,193.60** |
| A = L + E | OK |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £14,454.20 | -1.5% | £6,592.99 | £6,596.08 | +0.0% | GREEN |
| 2017 | £16,138.86 | £349,371.72 | +2064.8% | £7,252.29 | £116,787.71 | +1510.4% | RED |
| 2018 | £386,623.75 | £608,239.66 | +57.3% | £128,424.00 | £255,875.60 | +99.2% | RED |
| 2019 | £675,851.95 | £1,656,567.20 | +145.1% | £281,335.50 | £669,901.06 | +138.1% | RED |
| 2020 | £1,816,630.04 | £1,869,842.12 | +2.9% | £736,963.94 | £757,402.56 | +2.8% | GREEN |
| 2021 | £2,028,952.42 | £2,451,304.19 | +20.8% | £833,649.22 | £717,537.74 | -13.9% | AMBER |
| 2022 | £2,607,611.88 | £4,304,823.62 | +65.1% | £790,935.58 | £932,085.05 | +17.8% | RED |
| 2023 | £4,508,414.67 | £3,475,138.96 | -22.9% | £1,029,561.00 | £806,266.15 | -21.7% | RED |
| 2024 | £3,512,844.39 | £3,071,309.68 | -12.6% | £893,105.75 | £1,190,887.42 | +33.3% | RED |
| 2025 | £3,145,356.42 | £1,247,151.37 | -60.3% | £1,315,150.33 | £461,217.99 | -64.9% | RED |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 1 | 0 | 0% | £150.00 |
| 2021 | 2 | 0 | 0% | £400.00 |
| 2024 | 2 | 0 | 0% | £550.00 |

**Total:** 5 attempts, 0 wins (0% win rate), £1,100.00 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,316,035.71

## 2016

**Trading & Risk**

- Net margin: £1,177.50 (gross £6,437.59, capital £75.62)
  - Electricity: gross £5,753.45, capital £70.20, net £897.69
  - Gas: gross £684.14, capital £5.42, net £279.81
- Treasury at year end: £2,467,407.51
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.23, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-01-31: treasury £2,466,647.33, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-01: treasury £2,466,658.53, (none), VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-31: treasury £2,466,669.50, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-04-30: treasury £2,466,679.77, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-05-30: treasury £2,466,689.97, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-06-29: treasury £2,466,699.83, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-07-29: treasury £2,466,709.80, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-08-28: treasury £2,466,719.79, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-09-27: treasury £2,466,729.91, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-10-27: treasury £2,466,740.03, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-11-26: treasury £2,466,750.06, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-12-26: treasury £2,466,761.00, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.25
- Worst single period: C9 on 2016-11-20 period 36, net margin £-0.31

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £2,952.03
  - By billing account: C1 £1,444.98, C5 £4,331.57, C7 £3,079.54
- Bill shock events (>=20%): 33 -- C1g 2016-04-30 (27%); C1g 2016-06-30 (22%); C1g 2016-10-31 (37%); C1g 2016-11-30 (42%); C5 2016-05-31 (27%); C5 2016-10-31 (40%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (77%); C7 2016-11-30 (52%); C2g 2016-05-31 (21%); C2g 2016-06-30 (29%); C2g 2016-10-31 (50%); C2g 2016-11-30 (53%); C2g 2016-12-31 (22%); C6 2016-05-31 (25%); C6 2016-06-30 (22%); C6 2016-10-31 (39%); C6 2016-11-30 (45%); C8 2016-05-31 (40%); C8 2016-06-30 (40%); C8 2016-09-30 (22%); C8 2016-10-31 (100%); C8 2016-11-30 (68%); C3g 2016-10-31 (48%); C3g 2016-11-30 (52%); C3g 2016-12-31 (21%); C9 2016-10-31 (74%); C9 2016-11-30 (58%); C4g 2016-11-30 (58%); C4g 2016-12-31 (23%)
- Churn risk (accounts renewing in 2016): 3 at risk (≥20% churn prob): C1 26%, C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.30-£131.62/MWh, net margin £126.66
- C1g (gas): tariff £24.34-£26.25/MWh, net margin £92.98
- C2 (electricity): tariff £107.62/MWh, net margin £69.75
- C2g (gas): tariff £26.92/MWh, net margin £102.73
- C3 (electricity): tariff £98.21/MWh, net margin £29.14
- C3g (gas): tariff £21.93/MWh, net margin £41.14
- C4 (electricity): tariff £98.43/MWh, net margin £11.18
- C4g (gas): tariff £24.40/MWh, net margin £42.96
- C5 (electricity): tariff £117.30-£130.38/MWh, net margin £247.25
- C6 (electricity): tariff £107.62/MWh, net margin £23.43
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £233.23
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £120.18
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £36.87

**Portfolio Health**

- Capital cost ratio: 1.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.869, average bill shock 18.8%, bad debt provision £157.08, avg complaint probability 4.3%
- Solvency signal: £274,156/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £2,018.54 vs. naked (unhedged) net margin: £10,270.52
- hedging cost £8,251.99 vs. a fully unhedged book (commodity-only: actual net £2,018.54 vs. naked net £10,270.52)
  - C1: actual £239.43 vs. naked £697.02 -- hedging cost £457.59
  - C1g: actual £193.32 vs. naked £302.93 -- hedging cost £109.61
  - C2: actual £88.39 vs. naked £532.98 -- hedging cost £444.59
  - C2g: actual £149.65 vs. naked £361.83 -- hedging cost £212.17
  - C3: actual £50.07 vs. naked £299.10 -- hedging cost £249.02
  - C3g: actual £79.53 vs. naked £305.46 -- hedging cost £225.93
  - C4: actual £35.74 vs. naked £362.09 -- hedging cost £326.34
  - C4g: actual £141.64 vs. naked £443.83 -- hedging cost £302.20
  - C5: actual £399.77 vs. naked £2,682.43 -- hedging cost £2,282.67
  - C6: actual £8.72 vs. naked £880.87 -- hedging cost £872.15
  - C7: actual £397.30 vs. naked £1,943.97 -- hedging cost £1,546.68
  - C8: actual £174.46 vs. naked £784.20 -- hedging cost £609.75
  - C9: actual £60.52 vs. naked £673.81 -- hedging cost £613.29

**Year narrative:** 2016 produced a net gain of £1,177.50 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 33 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £30,755.24 (gross £123,328.26, capital £1,265.33)
  - Electricity: gross £122,080.72, capital £1,254.90, net £30,296.04
  - Gas: gross £1,247.55, capital £10.43, net £459.20
- Treasury at year end: £2,497,895.65
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.92 (avg 0.92), C7 0.90 (avg 0.90), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,467,412.27, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-02-24: treasury £2,467,418.31, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-03-26: treasury £2,467,424.80, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-04-25: treasury £2,467,801.77, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-05-25: treasury £2,467,804.62, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-06-24: treasury £2,467,808.16, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-07-24: treasury £2,467,979.48, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-08-23: treasury £2,467,982.28, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-09-22: treasury £2,467,984.34, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-10-22: treasury £2,468,218.36, C5->1.00, C7->1.00, VaR (current £886.58 / stressed £350.91) ratio 2.53
  - 2017-11-21: treasury £2,468,227.52, C5->1.00, C7->1.00, VaR (current £886.58 / stressed £350.91) ratio 2.53
  - 2017-12-21: treasury £2,468,236.41, C5->1.00, C7->1.00, VaR (current £886.58 / stressed £350.91) ratio 2.53
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-20.46

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £3,911.28
  - By billing account: C1 £1,548.13, C2 £4,394.09, C3 £2,682.82, C4 £3,319.32, C5 £4,517.61, C6 £6,792.39, C7 £3,225.06, C8 £4,669.48, C9 £4,052.59
- Bill shock events (>=20%): 48 -- C1g 2017-04-30 (27%); C1g 2017-06-30 (23%); C1g 2017-10-31 (39%); C1g 2017-11-30 (43%); C1g 2017-12-31 (20%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-04-30 (21%); C2g 2017-05-31 (22%); C2g 2017-06-30 (30%); C2g 2017-10-31 (52%); C2g 2017-11-30 (55%); C2g 2017-12-31 (22%); C6 2017-05-31 (21%); C6 2017-11-30 (48%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-04-30 (30%); C3g 2017-05-31 (20%); C3g 2017-06-30 (28%); C3g 2017-10-31 (49%); C3g 2017-11-30 (53%); C3g 2017-12-31 (22%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4g 2017-04-30 (32%); C4g 2017-05-31 (23%); C4g 2017-06-30 (31%); C4g 2017-09-30 (21%); C4g 2017-10-31 (44%); C4g 2017-11-30 (57%); C4g 2017-12-31 (22%)
- Churn risk (accounts renewing in 2017): 9 at risk (≥20% churn prob): C1 35%, C2 23%, C3 29%, C4 29%, C5 32%, C6 32%, C7 38%, C8 35%, C9 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.88-£131.62/MWh, net margin £112.71
- C1g (gas): tariff £26.25-£33.05/MWh, net margin £100.49
- C2 (electricity): tariff £107.62-£125.43/MWh, net margin £100.78
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £181.13
- C3 (electricity): tariff £98.21-£120.51/MWh, net margin £76.70
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £64.24
- C4 (electricity): tariff £98.43-£109.29/MWh, net margin £30.85
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £113.33
- C5 (electricity): tariff £119.18-£130.38/MWh, net margin £151.58
- C6 (electricity): tariff £107.62-£126.75/MWh, net margin £78.66
- C7 (electricity): tariff £99.02-£196.40/MWh, net margin £162.63
- C8 (electricity): tariff £84.56-£190.50/MWh, net margin £210.70
- C9 (electricity): tariff £77.16-£180.03/MWh, net margin £130.54
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £29,240.89

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.863, average bill shock 15.7%, bad debt provision £1,346.58, avg complaint probability 4.2%
- Solvency signal: £249,790/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,317.05 vs. naked (unhedged) net margin: £112,037.61
- hedging cost £81,720.56 vs. a fully unhedged book (commodity-only: actual net £30,317.05 vs. naked net £112,037.61)
  - C1: actual £30.81 vs. naked £283.55 -- hedging cost £252.74
  - C1g: actual £116.62 vs. naked £150.98 -- hedging cost £34.36
  - C2: actual £108.54 vs. naked £585.35 -- hedging cost £476.81
  - C2g: actual £202.10 vs. naked £411.72 -- hedging cost £209.62
  - C3: actual £104.47 vs. naked £365.07 -- hedging cost £260.61
  - C3g: actual £45.44 vs. naked £269.43 -- hedging cost £223.99
  - C4: actual £18.25 vs. naked £364.74 -- hedging cost £346.49
  - C4g: actual £62.09 vs. naked £254.39 -- hedging cost £192.30
  - C5: actual £-212.22 vs. naked £1,061.32 -- hedging cost £1,273.55
  - C6: actual £118.40 vs. naked £1,377.34 -- hedging cost £1,258.93
  - C7: actual £-8.70 vs. naked £863.10 -- hedging cost £871.80
  - C8: actual £255.98 vs. naked £992.72 -- hedging cost £736.74
  - C9: actual £234.38 vs. naked £944.74 -- hedging cost £710.37
  - C_IC1: actual £29,240.89 vs. naked £104,113.14 -- hedging cost £74,872.25

**Year narrative:** 2017 produced a net gain of £30,755.24 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 48 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £105,057.46 (gross £268,267.85, capital £1,543.57)
  - Electricity: gross £267,141.89, capital £1,528.77, net £104,682.61
  - Gas: gross £1,125.96, capital £14.80, net £374.85
- Treasury at year end: £2,486,491.84
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.92 (avg 0.92), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.88), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2018-03-01 period 27, net margin £-14.91

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £100,417.64
  - By billing account: C1 £1,632.14, C2 £3,847.39, C3 £2,350.47, C4 £2,627.76, C5 £4,397.76, C6 £5,613.24, C7 £3,117.75, C8 £3,932.88, C9 £3,771.34, C_IC1 £972,885.68
- Bill shock events (>=20%): 56 -- C1g 2018-01-31 (26%); C1g 2018-04-30 (28%); C1g 2018-06-30 (25%); C1g 2018-10-31 (42%); C1g 2018-11-30 (47%); C1g 2018-12-31 (20%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (37%); C2g 2018-05-31 (21%); C2g 2018-06-30 (29%); C2g 2018-10-31 (50%); C2g 2018-11-30 (54%); C2g 2018-12-31 (22%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (21%); C6 2018-10-31 (29%); C6 2018-11-30 (21%); C8 2018-04-30 (34%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (31%); C3g 2018-05-31 (21%); C3g 2018-06-30 (28%); C3g 2018-10-31 (51%); C3g 2018-11-30 (54%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-10-31 (32%); C4g 2018-04-30 (32%); C4g 2018-05-31 (22%); C4g 2018-06-30 (31%); C4g 2018-10-31 (89%); C4g 2018-11-30 (59%); C4g 2018-12-31 (23%); C_IC1 2018-01-31 (21%); C_IC1 2018-02-28 (61%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 9 at risk (≥20% churn prob): C1 35%, C2 32%, C3 35%, C4 35%, C5 35%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £117.88-£148.92/MWh, net margin £31.05
- C1g (gas): tariff £33.05-£35.66/MWh, net margin £116.57
- C2 (electricity): tariff £125.43-£143.07/MWh, net margin £67.63
- C2g (gas): tariff £32.81-£36.30/MWh, net margin £162.54
- C3 (electricity): tariff £120.51-£126.73/MWh, net margin £77.52
- C3g (gas): tariff £23.11-£28.32/MWh, net margin £39.27
- C4 (electricity): tariff £109.29-£147.72/MWh, net margin £41.07
- C4g (gas): tariff £26.10-£33.13/MWh, net margin £56.47
- C5 (electricity): tariff £119.18-£156.11/MWh, net margin £-211.04 -- **net-negative**
- C6 (electricity): tariff £126.75-£142.26/MWh, net margin £-6.94 -- **net-negative**
- C7 (electricity): tariff £99.02-£225.50/MWh, net margin £-6.31 -- **net-negative**
- C8 (electricity): tariff £99.78-£205.43/MWh, net margin £147.92
- C9 (electricity): tariff £94.30-£201.73/MWh, net margin £210.60
- C_IC1 (electricity): tariff £-82.12-£232.06/MWh, net margin £111,062.01
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,730.90 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.850, average bill shock 15.6%, bad debt provision £2,397.55, avg complaint probability 4.3%
- Solvency signal: £226,045/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £115,678.00 vs. naked (unhedged) net margin: £252,259.02
- hedging cost £136,581.03 vs. a fully unhedged book (commodity-only: actual net £115,678.00 vs. naked net £252,259.02)
  - C1: actual £91.16 vs. naked £465.51 -- hedging cost £374.35
  - C1g: actual £124.00 vs. naked £259.20 -- hedging cost £135.19
  - C2: actual £48.09 vs. naked £664.11 -- hedging cost £616.02
  - C2g: actual £142.96 vs. naked £299.85 -- hedging cost £156.89
  - C3: actual £49.64 vs. naked £393.46 -- hedging cost £343.82
  - C3g: actual £43.76 vs. naked £344.81 -- hedging cost £301.05
  - C4: actual £98.15 vs. naked £624.11 -- hedging cost £525.97
  - C4g: actual £66.20 vs. naked £594.64 -- hedging cost £528.44
  - C5: actual £169.22 vs. naked £2,031.65 -- hedging cost £1,862.44
  - C6: actual £-85.58 vs. naked £1,496.97 -- hedging cost £1,582.54
  - C7: actual £106.30 vs. naked £1,384.28 -- hedging cost £1,277.98
  - C8: actual £60.56 vs. naked £974.95 -- hedging cost £914.39
  - C9: actual £170.84 vs. naked £1,075.06 -- hedging cost £904.22
  - C_IC1: actual £121,323.59 vs. naked £208,074.50 -- hedging cost £86,750.91
  - C_IC2: actual £-6,730.90 vs. naked £33,575.93 -- hedging cost £40,306.83

**Year narrative:** 2018 produced a net gain of £105,057.46 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 56 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £227,253.97 (gross £710,926.91, capital £11,318.09)
  - Electricity: gross £635,123.85, capital £2,100.01, net £226,729.05
  - Gas: gross £75,803.07, capital £9,218.08, net £524.92
- Treasury at year end: £2,612,500.33
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2019-02-04 period 35, net margin £-14.60

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £133,878.40
  - By billing account: C1 £1,659.60, C2 £3,509.28, C3 £2,399.03, C4 £2,842.67, C5 £4,505.64, C6 £5,993.07, C7 £3,288.66, C8 £3,971.93, C9 £3,788.76, C_IC1 £912,393.83, C_IC2 £528,309.92
- Bill shock events (>=20%): 57 -- C1 2019-04-30 (20%); C1g 2019-04-30 (28%); C1g 2019-06-30 (25%); C1g 2019-10-31 (42%); C1g 2019-11-30 (46%); C5 2019-01-31 (44%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-04-30 (34%); C2g 2019-05-31 (21%); C2g 2019-06-30 (28%); C2g 2019-10-31 (49%); C2g 2019-11-30 (53%); C2g 2019-12-31 (22%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (40%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (22%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3g 2019-04-30 (31%); C3g 2019-05-31 (21%); C3g 2019-06-30 (29%); C3g 2019-10-31 (49%); C3g 2019-11-30 (53%); C3g 2019-12-31 (22%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (72%); C9 2019-11-30 (36%); C4g 2019-04-30 (33%); C4g 2019-05-31 (24%); C4g 2019-06-30 (32%); C4g 2019-09-30 (22%); C4g 2019-10-31 (24%); C4g 2019-11-30 (56%); C4g 2019-12-31 (22%); C_IC1 2019-02-28 (55%); C_IC1 2019-03-31 (129%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 10 at risk (≥20% churn prob): C1 35%, C2 32%, C3 35%, C4 35%, C5 38%, C6 29%, C7 35%, C8 38%, C9 32%, C_IC1 23%

**Pricing & Margin**

- C1 (electricity): tariff £125.39-£148.92/MWh, net margin £91.08
- C1g (gas): tariff £25.38-£35.66/MWh, net margin £124.15
- C2 (electricity): tariff £143.07-£151.47/MWh, net margin £138.69
- C2g (gas): tariff £26.00-£36.30/MWh, net margin £117.65
- C3 (electricity): tariff £120.68-£126.73/MWh, net margin £50.04
- C3g (gas): tariff £22.98-£28.32/MWh, net margin £82.49
- C4 (electricity): tariff £125.59-£147.72/MWh, net margin £96.27
- C4g (gas): tariff £19.44-£33.13/MWh, net margin £77.07
- C5 (electricity): tariff £125.22-£156.11/MWh, net margin £168.17
- C6 (electricity): tariff £142.26-£148.73/MWh, net margin £101.98
- C7 (electricity): tariff £99.72-£225.50/MWh, net margin £105.98
- C8 (electricity): tariff £107.61-£211.40/MWh, net margin £168.57
- C9 (electricity): tariff £100.73-£201.73/MWh, net margin £174.70
- C_IC1 (electricity): tariff £0.00-£267.52/MWh, net margin £142,954.47
- C_IC2 (electricity): tariff £-60.00-£283.06/MWh, net margin £81,495.84
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £1,183.24
- C_IC3g (gas): tariff £27.53/MWh, net margin £123.56

**Portfolio Health**

- Capital cost ratio: 1.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.860, average bill shock 15.9%, bad debt provision £6,248.18, avg complaint probability 4.2%
- Solvency signal: £217,708/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £252,534.56 vs. naked (unhedged) net margin: £840,580.85
- hedging cost £588,046.30 vs. a fully unhedged book (commodity-only: actual net £252,534.56 vs. naked net £840,580.85)
  - C1: actual £77.68 vs. naked £407.96 -- hedging cost £330.28
  - C1g: actual £127.53 vs. naked £234.27 -- hedging cost £106.74
  - C2: actual £177.65 vs. naked £889.13 -- hedging cost £711.48
  - C2g: actual £96.35 vs. naked £386.11 -- hedging cost £289.76
  - C3: actual £56.63 vs. naked £466.17 -- hedging cost £409.53
  - C3g: actual £128.54 vs. naked £422.60 -- hedging cost £294.06
  - C4: actual £103.49 vs. naked £598.01 -- hedging cost £494.53
  - C4g: actual £98.95 vs. naked £460.50 -- hedging cost £361.55
  - C5: actual £-44.43 vs. naked £1,574.34 -- hedging cost £1,618.77
  - C6: actual £214.21 vs. naked £2,109.35 -- hedging cost £1,895.13
  - C7: actual £56.51 vs. naked £1,147.09 -- hedging cost £1,090.57
  - C8: actual £239.62 vs. naked £1,370.72 -- hedging cost £1,131.10
  - C9: actual £190.06 vs. naked £1,290.62 -- hedging cost £1,100.56
  - C_IC1: actual £160,623.08 vs. naked £301,777.75 -- hedging cost £141,154.67
  - C_IC2: actual £89,081.88 vs. naked £165,284.43 -- hedging cost £76,202.55
  - C_IC3: actual £1,183.24 vs. naked £295,972.25 -- hedging cost £294,789.01
  - C_IC3g: actual £123.56 vs. naked £66,189.55 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £227,253.97 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 57 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £126,286.66 (gross £802,197.78, capital £7,378.15)
  - Electricity: gross £725,129.96, capital £1,992.78, net £121,823.37
  - Gas: gross £77,067.83, capital £5,385.37, net £4,463.29
- Treasury at year end: £2,918,728.53
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.86 (avg 0.86), C7 0.89 (avg 0.89), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2020-12-31 period 1, net margin £-484.21

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2020): £214,685.14
  - By billing account: C1 £1,886.74, C2 £3,847.49, C3 £1,989.25, C4 £2,973.10, C5 £5,712.27, C6 £5,998.90, C7 £3,397.41, C8 £4,504.85, C9 £3,980.61, C_IC1 £642,144.17, C_IC2 £314,904.00, C_IC3 £1,168,616.62, C_IC4 £630,951.46
- Bill shock events (>=20%): 50 -- C1g 2020-04-30 (27%); C1g 2020-06-30 (23%); C1g 2020-10-31 (39%); C1g 2020-11-30 (43%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2g 2020-03-31 (20%); C2g 2020-04-30 (34%); C2g 2020-05-31 (20%); C2g 2020-06-30 (28%); C2g 2020-10-31 (48%); C2g 2020-11-30 (52%); C2g 2020-12-31 (21%); C6 2020-04-30 (28%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-03-31 (20%); C3g 2020-04-30 (31%); C3g 2020-05-31 (21%); C3g 2020-06-29 (31%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4g 2020-03-31 (21%); C4g 2020-04-30 (32%); C4g 2020-05-31 (22%); C4g 2020-06-30 (30%); C4g 2020-10-31 (38%); C4g 2020-11-30 (55%); C4g 2020-12-31 (22%); C_IC1 2020-03-31 (58%); C_IC1 2020-04-30 (75%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (120%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 32%, C2 35%, C3 35%, C4 32%, C5 35%, C6 32%, C7 35%, C8 38%, C9 41%

**Pricing & Margin**

- C1 (electricity): tariff £125.39-£132.72/MWh, net margin £77.46
- C1g (gas): tariff £25.00-£25.38/MWh, net margin £127.63
- C2 (electricity): tariff £143.89-£151.47/MWh, net margin £217.42
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £133.85
- C3 (electricity): tariff £120.68/MWh, net margin £27.41
- C3g (gas): tariff £22.98/MWh, net margin £70.12
- C4 (electricity): tariff £122.03-£125.59/MWh, net margin £85.63
- C4g (gas): tariff £16.09-£19.44/MWh, net margin £74.43
- C5 (electricity): tariff £125.22-£138.52/MWh, net margin £-46.95 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.73/MWh, net margin £320.80
- C7 (electricity): tariff £99.72-£211.03/MWh, net margin £57.67
- C8 (electricity): tariff £110.17-£211.40/MWh, net margin £336.93
- C9 (electricity): tariff £85.19-£192.30/MWh, net margin £132.83
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £58,087.37
- C_IC2 (electricity): tariff £-79.50-£283.06/MWh, net margin £46,781.50
- C_IC3 (electricity): tariff £37.58-£80.52/MWh, net margin £11,166.02
- C_IC3g (gas): tariff £15.44-£19.83/MWh, net margin £4,057.27
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £4,579.29

**Portfolio Health**

- Capital cost ratio: 0.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.864, average bill shock 14.2%, bad debt provision £6,349.70, avg complaint probability 4.0%
- Solvency signal: £224,518/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £83,702.05 vs. naked (unhedged) net margin: £944,017.79
- hedging cost £860,315.74 vs. a fully unhedged book (commodity-only: actual net £83,702.05 vs. naked net £944,017.79)
  - C1: actual £5.84 vs. naked £100.26 -- hedging cost £94.42
  - C1g: actual £42.58 vs. naked £-194.88 -- hedging added £237.47
  - C2: actual £210.02 vs. naked £786.46 -- hedging cost £576.44
  - C2g: actual £145.01 vs. naked £326.04 -- hedging cost £181.03
  - C4: actual £2.99 vs. naked £347.38 -- hedging cost £344.39
  - C4g: actual £-29.70 vs. naked £-16.96 -- hedging cost £12.74
  - C5: actual £-295.16 vs. naked £223.46 -- hedging cost £518.62
  - C6: actual £313.09 vs. naked £1,770.35 -- hedging cost £1,457.26
  - C7: actual £-127.06 vs. naked £312.15 -- hedging cost £439.21
  - C8: actual £339.75 vs. naked £1,168.92 -- hedging cost £829.17
  - C9: actual £-21.73 vs. naked £695.07 -- hedging cost £716.80
  - C_IC1: actual £39,775.93 vs. naked £134,007.11 -- hedging cost £94,231.18
  - C_IC2: actual £45,917.01 vs. naked £98,961.61 -- hedging cost £53,044.61
  - C_IC3: actual £-16,916.58 vs. naked £217,029.95 -- hedging cost £233,946.53
  - C_IC3g: actual £6,419.86 vs. naked £147,730.42 -- hedging cost £141,310.56
  - C_IC4: actual £7,920.21 vs. naked £340,770.45 -- hedging cost £332,850.24

**Year narrative:** 2020 produced a net gain of £126,286.66 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 50 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £66,331.40 (gross £780,356.08, capital £15,938.68)
  - Electricity: gross £697,660.43, capital £5,715.91, net £68,165.46
  - Gas: gross £82,695.66, capital £10,222.76, net £-1,834.06
- Treasury at year end: £2,946,936.61
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2021-12-31 period 1, net margin £-4,053.07

**Customer Book**

- Active accounts: 16 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £206,260.86
  - By billing account: C1 £1,749.22, C2 £4,159.51, C3 £2,139.23, C4 £2,692.43, C5 £4,815.52, C6 £7,221.80, C7 £3,221.33, C8 £4,300.47, C9 £3,557.89, C_IC1 £598,759.19, C_IC2 £365,244.32, C_IC3 £1,046,985.16, C_IC4 £636,545.09
- Bill shock events (>=20%): 51 -- C1g 2021-04-30 (27%); C1g 2021-06-30 (22%); C1g 2021-10-31 (37%); C1g 2021-11-30 (42%); C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (21%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C2g 2021-04-30 (24%); C2g 2021-05-31 (21%); C2g 2021-06-30 (29%); C2g 2021-10-31 (50%); C2g 2021-11-30 (53%); C2g 2021-12-31 (22%); C6 2021-06-30 (35%); C6 2021-10-31 (26%); C6 2021-11-30 (48%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-10-31 (40%); C4g 2021-04-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (29%); C4g 2021-10-31 (98%); C4g 2021-11-30 (59%); C4g 2021-12-31 (23%); C_IC1 2021-05-31 (42%); C_IC2 2021-03-31 (25%); C_IC2 2021-04-30 (85%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (22%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%)
- Churn risk (accounts renewing in 2021): 12 at risk (≥20% churn prob): C1 32%, C2 32%, C4 32%, C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC3 20%, C_IC4 29%

**Pricing & Margin**

- C1 (electricity): tariff £132.72/MWh, net margin £5.96
- C1g (gas): tariff £25.00/MWh, net margin £42.23
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £185.96
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £94.07
- C4 (electricity): tariff £122.03-£183.00/MWh, net margin £-96.36 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-279.88 -- **net-negative**
- C5 (electricity): tariff £138.52/MWh, net margin £-291.83 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.50/MWh, net margin £454.44
- C7 (electricity): tariff £110.54-£274.50/MWh, net margin £-136.64 -- **net-negative**
- C8 (electricity): tariff £110.17-£274.50/MWh, net margin £339.64
- C9 (electricity): tariff £85.19-£263.54/MWh, net margin £-18.81 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £32,833.89
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £59,697.95
- C_IC3 (electricity): tariff £42.18-£396.03/MWh, net margin £-28,157.80 -- **net-negative**
- C_IC3g (gas): tariff £19.83-£122.38/MWh, net margin £-1,690.48 -- **net-negative**
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £3,349.06

**Portfolio Health**

- Capital cost ratio: 2.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.858, average bill shock 15.1%, bad debt provision £9,247.67, avg complaint probability 4.2%
- Solvency signal: £245,578/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £164,859.07 vs. naked (unhedged) net margin: £370,786.37
- hedging cost £205,927.30 vs. a fully unhedged book (commodity-only: actual net £164,859.07 vs. naked net £370,786.37)
  - C2: actual £156.74 vs. naked £258.46 -- hedging cost £101.72
  - C2g: actual £42.87 vs. naked £-285.70 -- hedging added £328.57
  - C4: actual £-348.64 vs. naked £-151.59 -- hedging cost £197.05
  - C4g: actual £-768.05 vs. naked £-1,428.53 -- hedging added £660.48
  - C6: actual £449.90 vs. naked £257.13 -- hedging added £192.76
  - C7: actual £-1,835.40 vs. naked £-870.69 -- hedging cost £964.72
  - C8: actual £283.50 vs. naked £107.31 -- hedging added £176.20
  - C9: actual £-56.77 vs. naked £-191.86 -- hedging added £135.09
  - C_IC1: actual £34,082.61 vs. naked £-58,867.26 -- hedging added £92,949.88
  - C_IC2: actual £68,700.97 vs. naked £24,679.82 -- hedging added £44,021.16
  - C_IC3: actual £114,894.25 vs. naked £250,314.34 -- hedging cost £135,420.09
  - C_IC3g: actual £-48,818.20 vs. naked £32,238.32 -- hedging cost £81,056.52
  - C_IC4: actual £-1,924.70 vs. naked £124,726.63 -- hedging cost £126,651.33

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £66,331.40 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 51 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £276,374.43 (gross £1,082,104.29, capital £65,376.23)
  - Electricity: gross £991,648.22, capital £13,479.48, net £325,257.02
  - Gas: gross £90,456.07, capital £51,896.75, net £-48,882.59
- Treasury at year end: £3,115,771.21
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,054,420.43, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,393.19 / stressed £20,855.89) ratio 2.70
  - 2022-05-29: treasury £3,054,551.63, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,502.61 / stressed £20,884.92) ratio 2.71
  - 2022-06-28: treasury £3,054,545.99, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,502.61 / stressed £20,884.92) ratio 2.71
  - 2022-07-28: treasury £3,054,256.34, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,585.70 / stressed £20,901.49) ratio 2.71
  - 2022-08-27: treasury £3,054,230.37, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,585.70 / stressed £20,901.49) ratio 2.71
  - 2022-09-26: treasury £3,054,201.43, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,585.70 / stressed £20,901.49) ratio 2.71
  - 2022-10-26: treasury £3,052,043.04, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,648.17 / stressed £20,912.10) ratio 2.71
  - 2022-11-25: treasury £3,051,892.15, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,648.17 / stressed £20,912.10) ratio 2.71
  - 2022-12-25: treasury £3,051,625.15, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,648.17 / stressed £20,912.10) ratio 2.71
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.71
- Worst single period: C_IC3g on 2022-12-31 period 1, net margin £-2,969.97

**Customer Book**

- Active accounts: 14 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £206,793.23
  - By billing account: C1 £1,947.09, C2 £3,211.67, C2_2 £481.52, C3 £2,145.36, C4 £1,849.17, C5 £4,996.20, C6 £6,712.37, C7 £2,855.43, C8 £4,113.08, C9 £3,955.26, C_IC1 £671,265.90, C_IC2 £392,525.35, C_IC3 £1,191,438.07, C_IC4 £607,608.83
- Bill shock events (>=20%): 56 -- C7 2022-01-31 (50%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-03-30 (20%); C6 2022-04-30 (41%); C6 2022-05-31 (23%); C6 2022-09-30 (24%); C6 2022-11-30 (42%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-10-31 (53%); C4g 2022-04-30 (33%); C4g 2022-05-31 (23%); C4g 2022-06-30 (32%); C4g 2022-09-30 (26%); C4g 2022-10-31 (217%); C4g 2022-11-30 (65%); C4g 2022-12-31 (24%); C_IC1 2022-06-30 (78%); C_IC2 2022-05-31 (57%); C_IC3 2022-01-31 (111%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (35%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (69%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 9 at risk (≥20% churn prob): C2 20%, C4 35%, C6 32%, C7 35%, C8 35%, C9 38%, C_IC1 20%, C_IC3 23%, C_IC4 32%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £9.20
- C2_2 (electricity): tariff £361.95/MWh, net margin £25.73
- C2g (gas): tariff £35.00/MWh, net margin £-13.03 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-417.30 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,134.45 -- **net-negative**
- C6 (electricity): tariff £197.50-£406.61/MWh, net margin £698.47
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,831.75 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-193.33 -- **net-negative**
- C9 (electricity): tariff £138.05-£389.07/MWh, net margin £-124.74 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£465.44/MWh, net margin £138,204.47
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £76,990.37
- C_IC3 (electricity): tariff £138.22-£396.03/MWh, net margin £113,825.35
- C_IC3g (gas): tariff £120.28-£122.38/MWh, net margin £-47,735.11 -- **net-negative**
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £-1,929.46 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 6.0% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,429,626.03 -> £3,051,594.13 (11.0%)
- Bills issued: 148, average clarity 0.810, average bill shock 33.3%, bad debt provision £36,072.45, avg complaint probability 5.3%
- Solvency signal: £283,252/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £116,751.23 vs. naked (unhedged) net margin: £1,104,884.06
- hedging cost £988,132.82 vs. a fully unhedged book (commodity-only: actual net £116,751.23 vs. naked net £1,104,884.06)
  - C2_2: actual £25.26 vs. naked £1,644.79 -- hedging cost £1,619.53
  - C4: actual £-502.57 vs. naked £998.12 -- hedging cost £1,500.69
  - C4g: actual £-1,691.04 vs. naked £1,139.58 -- hedging cost £2,830.62
  - C6: actual £939.60 vs. naked £3,242.37 -- hedging cost £2,302.78
  - C7: actual £-351.18 vs. naked £2,280.97 -- hedging cost £2,632.14
  - C8: actual £-353.94 vs. naked £1,101.73 -- hedging cost £1,455.67
  - C9: actual £-56.87 vs. naked £1,007.54 -- hedging cost £1,064.42
  - C_IC1: actual £221,568.37 vs. naked £259,868.70 -- hedging cost £38,300.33
  - C_IC2: actual £91,701.31 vs. naked £131,514.13 -- hedging cost £39,812.82
  - C_IC3: actual £-167,772.11 vs. naked £450,706.93 -- hedging cost £618,479.04
  - C_IC3g: actual £-30,262.44 vs. naked £84,525.03 -- hedging cost £114,787.47
  - C_IC4: actual £3,506.84 vs. naked £166,854.16 -- hedging cost £163,347.31

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £276,374.43 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 56 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £63,249.26 (gross £931,953.26, capital £49,257.41)
  - Electricity: gross £810,808.75, capital £9,922.15, net £94,932.71
  - Gas: gross £121,144.51, capital £39,335.26, net £-31,683.45
- Treasury at year end: £3,233,014.44
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,115,770.35, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £124,179.53 / stressed £44,982.14) ratio 2.76
  - 2023-02-23: treasury £3,115,770.07, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £124,179.53 / stressed £44,982.14) ratio 2.76
  - 2023-03-25: treasury £3,115,769.73, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £124,179.53 / stressed £44,982.14) ratio 2.76
  - 2023-04-24: treasury £3,200,089.05, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £131,325.19 / stressed £50,028.96) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-12-31 period 1, net margin £-3,474.99

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £208,260.23
  - By billing account: C1 £1,941.34, C2 £3,194.95, C2_2 £1,343.76, C3 £2,138.47, C4 £1,599.55, C5 £4,974.95, C6 £7,326.05, C7 £3,034.13, C8 £4,174.53, C9 £4,224.05, C_IC1 £724,597.17, C_IC2 £420,197.79, C_IC3 £1,109,960.58, C_IC4 £626,935.90
- Bill shock events (>=20%): 42 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (31%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (37%); C6 2023-11-30 (42%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4g 2023-03-31 (20%); C4g 2023-04-30 (35%); C4g 2023-05-31 (26%); C4g 2023-06-30 (36%); C4g 2023-09-30 (27%); C4g 2023-10-31 (42%); C4g 2023-11-30 (64%); C4g 2023-12-31 (24%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (61%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (102%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (36%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%)
- Churn risk (accounts renewing in 2023): 8 at risk (≥20% churn prob): C2_2 38%, C4 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC3 23%, C_IC4 29%

**Pricing & Margin**

- C2_2 (electricity): tariff £352.89-£361.95/MWh, net margin £517.26
- C4 (electricity): tariff £260.62-£305.00/MWh, net margin £-231.20 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-915.99 -- **net-negative**
- C6 (electricity): tariff £333.16-£406.61/MWh, net margin £1,061.17
- C7 (electricity): tariff £187.67-£457.50/MWh, net margin £-349.77 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-25.36 -- **net-negative**
- C9 (electricity): tariff £192.25-£389.07/MWh, net margin £218.60
- C_IC1 (electricity): tariff £-60.00-£465.44/MWh, net margin £167,996.08
- C_IC2 (electricity): tariff £-186.24-£479.42/MWh, net margin £88,904.05
- C_IC3 (electricity): tariff £102.52-£263.88/MWh, net margin £-166,672.29 -- **net-negative**
- C_IC3g (gas): tariff £60.86-£120.28/MWh, net margin £-30,767.46 -- **net-negative**
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £3,514.18

**Portfolio Health**

- Capital cost ratio: 5.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,643,089.38 -> £3,233,011.00 (11.3%)
- Bills issued: 144, average clarity 0.823, average bill shock 17.0%, bad debt provision £13,896.74, avg complaint probability 4.7%
- Solvency signal: £323,301/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £380,952.39 vs. naked (unhedged) net margin: £1,178,162.02
- hedging cost £797,209.63 vs. a fully unhedged book (commodity-only: actual net £380,952.39 vs. naked net £1,178,162.02)
  - C2_2: actual £853.46 vs. naked £2,448.85 -- hedging cost £1,595.38
  - C4: actual £452.49 vs. naked £1,174.13 -- hedging cost £721.64
  - C4g: actual £553.10 vs. naked £1,162.49 -- hedging cost £609.39
  - C6: actual £1,180.95 vs. naked £4,120.63 -- hedging cost £2,939.68
  - C7: actual £475.75 vs. naked £1,923.14 -- hedging cost £1,447.39
  - C8: actual £209.11 vs. naked £1,971.27 -- hedging cost £1,762.16
  - C9: actual £618.76 vs. naked £2,123.77 -- hedging cost £1,505.01
  - C_IC1: actual £149,075.35 vs. naked £292,863.05 -- hedging cost £143,787.70
  - C_IC2: actual £98,245.62 vs. naked £166,751.97 -- hedging cost £68,506.35
  - C_IC3: actual £162,403.06 vs. naked £438,065.13 -- hedging cost £275,662.07
  - C_IC3g: actual £-36,843.35 vs. naked £77,603.64 -- hedging cost £114,446.99
  - C_IC4: actual £3,728.07 vs. naked £187,953.96 -- hedging cost £184,225.88

**Year narrative:** 2023 produced a net gain of £63,249.26 across 12 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 42 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £337,009.76 (gross £1,312,793.91, capital £55,798.82)
  - Electricity: gross £1,188,380.54, capital £9,895.79, net £373,810.07
  - Gas: gross £124,413.37, capital £45,903.03, net £-36,800.32
- Treasury at year end: £3,613,541.84
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.91 (avg 0.91), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2024-12-30 period 1, net margin £-1,915.60

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2024): £241,175.80
  - By billing account: C1 £1,799.01, C2 £3,517.48, C2_2 £1,963.52, C3 £2,080.31, C4 £2,023.53, C5 £4,359.75, C6 £6,752.15, C7 £3,394.86, C8 £5,106.00, C9 £4,600.76, C_IC1 £754,804.99, C_IC2 £445,210.48, C_IC3 £1,455,486.31, C_IC4 £685,362.03
- Bill shock events (>=20%): 32 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4g 2024-03-31 (23%); C4g 2024-04-30 (34%); C4g 2024-05-31 (25%); C4g 2024-06-30 (35%); C_IC1 2024-07-31 (34%); C_IC1 2024-08-31 (66%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (109%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (58%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (54%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C4 35%, C6 38%, C7 35%, C8 41%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.59-£352.89/MWh, net margin £428.47
- C4 (electricity): tariff £260.62/MWh, net margin £339.74
- C4g (gas): tariff £66.00/MWh, net margin £399.25
- C6 (electricity): tariff £333.16/MWh, net margin £407.29
- C7 (electricity): tariff £165.00-£358.28/MWh, net margin £475.31
- C8 (electricity): tariff £161.47-£397.50/MWh, net margin £329.69
- C9 (electricity): tariff £165.00-£367.03/MWh, net margin £555.53
- C_IC1 (electricity): tariff £-98.58-£334.20/MWh, net margin £131,850.29
- C_IC2 (electricity): tariff £-106.92-£358.44/MWh, net margin £73,223.13
- C_IC3 (electricity): tariff £86.86-£195.73/MWh, net margin £162,464.55
- C_IC3g (gas): tariff £60.86-£61.52/MWh, net margin £-37,199.57 -- **net-negative**
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £3,736.07

**Portfolio Health**

- Capital cost ratio: 4.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,643,002.10 -> £3,233,014.48 (11.3%)
- Bills issued: 129, average clarity 0.829, average bill shock 15.1%, bad debt provision £11,645.22, avg complaint probability 4.4%
- Solvency signal: £361,354/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £183,256.98 vs. naked (unhedged) net margin: £561,724.12
- hedging cost £378,467.14 vs. a fully unhedged book (commodity-only: actual net £183,256.98 vs. naked net £561,724.12)
  - C2_2: actual £97.59 vs. naked £1,036.91 -- hedging cost £939.32
  - C7: actual £-13.51 vs. naked £653.48 -- hedging cost £666.99
  - C8: actual £337.89 vs. naked £1,415.96 -- hedging cost £1,078.07
  - C9: actual £371.56 vs. naked £1,427.21 -- hedging cost £1,055.66
  - C_IC1: actual £123,598.52 vs. naked £218,723.34 -- hedging cost £95,124.82
  - C_IC2: actual £65,280.57 vs. naked £116,615.17 -- hedging cost £51,334.60
  - C_IC3: actual £15,459.83 vs. naked £116,257.58 -- hedging cost £100,797.75
  - C_IC3g: actual £-23,330.60 vs. naked £29,765.97 -- hedging cost £53,096.57
  - C_IC4: actual £1,455.13 vs. naked £75,828.50 -- hedging cost £74,373.37

**Year narrative:** 2024 produced a net gain of £337,009.76 across 12 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 32 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £96,630.55 (gross £527,637.35, capital £28,983.09)
  - Electricity: gross £474,128.57, capital £5,696.18, net £116,129.95
  - Gas: gross £53,508.78, capital £23,286.91, net £-19,499.39
- Treasury at year end: £3,668,447.37
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2025-06-01 period 1, net margin £-532.28

**Customer Book**

- Active accounts: 9 (C2_2, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 4, SME electricity: 0, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £250,948.67
  - By billing account: C1 £1,780.50, C2 £3,394.44, C2_2 £2,090.13, C3 £2,182.09, C4 £2,092.62, C5 £4,810.21, C6 £7,131.43, C7 £3,580.15, C8 £4,164.23, C9 £4,565.47, C_IC1 £793,267.70, C_IC2 £460,165.18, C_IC3 £1,425,379.65, C_IC4 £798,677.52
- Bill shock events (>=20%): 20 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (34%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.59-£283.12/MWh, net margin £88.21
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-10.34 -- **net-negative**
- C8 (electricity): tariff £149.29-£308.25/MWh, net margin £85.04
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £194.62
- C_IC1 (electricity): tariff £169.74-£324.06/MWh, net margin £67,058.89
- C_IC2 (electricity): tariff £163.52-£312.18/MWh, net margin £31,834.52
- C_IC3 (electricity): tariff £86.86-£165.83/MWh, net margin £15,442.62
- C_IC3g (gas): tariff £61.52/MWh, net margin £-19,499.39 -- **net-negative**
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £1,436.41

**Portfolio Health**

- Capital cost ratio: 5.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 54, average clarity 0.777, average bill shock 23.6%, bad debt provision £5,016.98, avg complaint probability 5.9%
- Solvency signal: £458,556/customer (8 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £56.38 vs. naked (unhedged) net margin: £336.42
- hedging cost £280.04 vs. a fully unhedged book (commodity-only: actual net £56.38 vs. naked net £336.42)
  - C2_2: actual £83.35 vs. naked £217.75 -- hedging cost £134.40
  - C8: actual £-26.97 vs. naked £118.67 -- hedging cost £145.64

**Year narrative:** 2025 produced a net gain of £96,630.55 across 9 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 20 customer(s) experienced a bill shock of >=20%.
