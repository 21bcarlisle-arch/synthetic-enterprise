# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,709,807.77
  (£1,243,171.55 net change)
- Solvency signal (final year): £448,387/customer (8 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £19,933,040.74
  VAT remitted to HMRC: (£959,271.15) | Revenue (ex-VAT): £18,973,769.59
  Non-commodity pass-through: (£4,822,281.02)
- Gross margin: £6,476,625.78
- Capital costs: £236,668.36
- Net margin: £6,239,957.41
- Capital cost ratio: 3.7% of gross
- Net margin as % of revenue: 32.9%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1531, average clarity 0.841,
  service quality score 0.909
- Enterprise value (CLV sum across 14 billing accounts): £6,142,208.62
- Cost to serve (whole portfolio): £91,348.73, net margin after cost to serve: £6,148,608.68
- Hedge effectiveness (whole window): hedging cost £4,044,731.34 vs. a fully unhedged book (commodity-only: actual net £1,243,171.55 vs. naked net £5,287,902.89)

- **2021** (crisis year): net margin £58,203.88, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £256,102.05, 9 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,476,625.78, capital £236,668.36, net £6,239,957.41. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 3.7% (commodity basis, comparable to old model) / 3.7% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £58,203.88 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 32.9%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,239,957.41
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,287,902.89
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,044,731.34 vs. a fully unhedged book (commodity-only: actual net £1,243,171.55 vs. naked net £5,287,902.89)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £103,533.06 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £618,542.21 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £252.06 | £623.75 | £307.71 | £1,183.52 |
| 2017 | £29,240.89 | £0.00 | £220.57 | £831.40 | £495.67 | £30,788.53 |
| 2018 | £99,034.99 | £0.00 | £-256.03 | £501.70 | £383.55 | £99,664.21 |
| 2019 | £216,630.00 | £123.56 | £206.81 | £715.79 | £441.25 | £218,117.41 |
| 2020 | £111,128.36 | £4,057.27 | £331.96 | £872.52 | £447.97 | £116,838.09 |
| 2021 | £59,712.32 | £-1,690.48 | £186.51 | £270.07 | £-274.54 | £58,203.88 |
| 2022 | £306,869.05 | £-47,735.11 | £815.52 | £-2,384.62 | £-1,462.79 | £256,102.05 |
| 2023 | £81,110.55 | £-30,767.46 | £1,263.87 | £284.18 | £-1,169.81 | £50,721.34 |
| 2024 | £353,340.76 | £-37,199.57 | £491.76 | £2,019.39 | £478.71 | £319,131.05 |
| 2025 | £111,563.52 | £-19,499.39 | £0.00 | £357.34 | £0.00 | £92,421.46 |

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
| C4 | 2020-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.5838 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9547 |
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

- **Average absolute error:** 197.5%
- **Average signed error:** +51.7% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -81.4% | 81.4% |
| 2017 | 3 | -93.8% | 93.8% |
| 2018 | 4 | +403.9% | 496.1% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | +25.9% | 190.4% |
| 2021 | 9 | -6.7% | 120.4% |
| 2022 | 7 | -23.6% | 113.0% |
| 2023 | 7 | -13.3% | 122.7% |
| 2024 | 7 | +78.9% | 231.8% |
| 2025 | 2 | -94.4% | 94.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 34.9%, abs error 313.6%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.9%, abs error 146.9%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.2% | 0.0% | 81.4% |
| 2017 | 0 | 3 | 0.0% | 2.2% | 0.0% | 93.8% |
| 2018 | 2 | 2 | 19.1% | 49.9% | 49.2% | 943.1% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 16.7% | 0.5% | 282.3% | 98.5% |
| 2021 | 3 | 6 | 66.0% | 4.1% | 184.4% | 88.4% |
| 2022 | 0 | 7 | 0.0% | 19.5% | 0.0% | 113.0% |
| 2023 | 2 | 5 | 29.2% | 19.0% | 72.9% | 142.6% |
| 2024 | 3 | 4 | 39.9% | 0.0% | 407.5% | 100.0% |
| 2025 | 0 | 2 | 0.0% | 2.1% | 0.0% | 94.4% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 9 (23%)
- **Below/at SVT (protected):** 30 (77%)
- **Mean rate vs SVT premium:** -10.3%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.2 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 120.0 | 140.0 |
| 2018 | 2 | 1 (50%) | +0.2% | 152.8 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -25.9% | 130.9 | 176.9 |
| 2021 | 6 | 3 (50%) | +0.9% | 184.2 | 183.8 |
| 2022 | 7 | 4 (57%) | +11.5% | 294.5 | 318.4 |
| 2023 | 5 | 0 (0%) | -32.4% | 225.4 | 364.0 |
| 2024 | 4 | 0 (0%) | -16.2% | 205.6 | 246.9 |
| 2025 | 2 | 1 (50%) | -4.8% | 236.7 | 248.6 |

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
| 2018 | 4 | 4.96× ⚠ | 18.00× |
| 2019 | 4 | 5.25× ⚠ | 18.00× |
| 2020 | 10 | 1.90× | 10.81× |
| 2021 | 9 | 1.20× | 3.75× |
| 2022 | 7 | 1.13× | 3.13× |
| 2023 | 7 | 1.23× | 3.13× |
| 2024 | 7 | 2.32× ⚠ | 10.88× |
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
| 2020 | 13 | 0.8% | 3.5% |
| 2021 | 11 | 1.1% | 4.2% |
| 2022 | 9 | 1.9% | 7.5% |
| 2023 | 9 | 2.5% | 8.5% |
| 2024 | 9 | 3.3% | 15.6% |
| 2025 | 2 | 1.4% | 2.1% |

**86** of **86** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **7** (6 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.35, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.32, company est=0.04 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.83 |
| 2022-03-31 | CHURN | C2 | SIM p=0.32, company est=0.07 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.25 |
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
| 2016 | 1,162 | 7 | 189 | 37 | 305 | 0 | 1,701 |  |
| 2017 | 37,352 | 2,722 | 11,227 | 1,985 | 9,991 | 0 | 63,278 |  |
| 2018 | 65,913 | 9,938 | 17,545 | 9,401 | 17,391 | 0 | 120,187 |  |
| 2019 | 165,083 | 28,434 | 42,580 | 32,051 | 44,423 | 0 | 312,571 |  |
| 2020 | 239,156 | 35,468 | 69,608 | 56,674 | 70,177 | 0 | 471,083 |  |
| 2021 | 249,026 | 15,152 | 72,054 | 50,148 | 63,433 | 41,818 | 491,631 |  |
| 2022 | 259,289 | -50,342 | 71,853 | 37,170 | 69,907 | 100,685 | 488,561 | ⬇ CfD REBATE |
| 2023 | 274,578 | 65,429 | 72,499 | 51,399 | 75,854 | 13,891 | 553,649 |  |
| 2024 | 310,631 | 111,030 | 73,612 | 69,368 | 83,373 | 2,019 | 650,033 |  |
| 2025 | 137,698 | 47,631 | 31,649 | 31,480 | 36,676 | 866 | 286,000 |  |
| **Total** | **1,739,886** | **265,468** | **462,816** | **339,713** | **471,531** | **159,279** | **3,438,694** | |

Total policy cost: £3,438,694 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

## Network Charges — DUoS + TNUoS (Phase 29a)

Electricity network charges deducted from net_margin_gbp each year. 
Resi/SME: combined DUoS + TNUoS unit rate (largest single non-commodity cost). 
I&C HV: DUoS only (Triad TNUoS is an annual lump tracked in the Triad section).

| Year | Network cost £ | Note |
|------|----------------|------|
| 2016 | 3,202 |  |
| 2017 | 26,301 |  |
| 2018 | 38,779 |  |
| 2019 | 88,630 |  |
| 2020 | 124,849 |  |
| 2021 | 124,693 |  |
| 2022 | 134,603 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 140,330 | RIIO-ED2 from Apr 2023 |
| 2024 | 144,360 |  |
| 2025 | 61,948 |  |
| **Total** | **887,696** | |

Total network cost: £887,696 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

## Gas Policy Costs and Network Charges (Phase 30b)

Gas CCL: non-domestic only (domestic gas exempt). Gas network (GDN + NTS): all on unit rate.
GGL (Green Gas Levy): per-meter, from Nov 2021; tiny in £/MWh terms.

| Year | Gas Policy (CCL + GGL) £ | Gas Network £ | Total Gas Non-Commodity £ |
|------|--------------------------|---------------|--------------------------|
| 2016 | 0 | 524 | 524 |
| 2017 | 0 | 1,053 | 1,053 |
| 2018 | 0 | 988 | 988 |
| 2019 | 15,155 | 50,497 | 65,652 |
| 2020 | 19,468 | 47,395 | 66,863 |
| 2021 | 22,472 | 50,472 | 72,944 |
| 2022 | 27,045 | 54,476 | 81,522 |
| 2023 | 32,229 | 79,773 | 112,002 |
| 2024 | 37,495 | 76,507 | 114,002 |
| 2025 | 17,243 | 31,816 | 49,059 |
| **Total** | **171,107** | **393,502** | **564,608** |

Gas policy pass-through in tariff unit rate (CCL + GGL at term start); gas network pass-through likewise. Net basis risk near-zero for annual contracts.


## Gas Book P&L — Year by Year (Phase 32a)

Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.
Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.

| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |
|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|
| 2016 | 1,493 | 624 | 869 | 0 | 524 | 7 | 308 | +20.6% |
| 2017 | 3,055 | 1,430 | 1,625 | 0 | 1,053 | 15 | 496 | +16.2% |
| 2018 | 3,364 | 1,904 | 1,460 | 0 | 988 | 21 | 384 | +11.4% |
| 2019 | 138,049 | 61,867 | 76,182 | 15,155 | 50,497 | 9,224 | 565 | +0.4% |
| 2020 | 121,525 | 44,125 | 77,400 | 19,468 | 47,395 | 5,388 | 4,505 | +3.7% |
| 2021 | 297,924 | 215,160 | 82,764 | 22,472 | 50,472 | 10,226 | -1,965 | -0.7% |
| 2022 | 588,588 | 498,329 | 90,259 | 27,045 | 54,476 | 51,903 | -49,198 | -8.4% |
| 2023 | 297,558 | 176,533 | 121,025 | 32,229 | 79,773 | 39,346 | -31,937 | -10.7% |
| 2024 | 270,786 | 146,204 | 124,583 | 37,495 | 76,507 | 45,908 | -36,721 | -13.6% |
| 2025 | 132,454 | 78,945 | 53,509 | 17,243 | 31,816 | 23,287 | -19,499 | -14.7% |
| **Total** | **1,854,796** | **1,225,121** | **629,676** | **171,107** | **393,502** | **185,325** | **-133,063** | **-7.2%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,417 | 9 | 274,157 | 2108.90× | OK |
| 2017 | 2,497,933 | 10 | 249,793 | 1921.49× | OK |
| 2018 | 2,486,501 | 11 | 226,046 | 1738.81× | OK |
| 2019 | 2,606,333 | 12 | 217,194 | 1670.73× | OK |
| 2020 | 2,899,744 | 13 | 223,057 | 1715.83× | OK |
| 2021 | 2,921,202 | 12 | 243,434 | 1872.57× | OK |
| 2022 | 3,069,116 | 11 | 279,011 | 2146.24× | OK |
| 2023 | 3,173,051 | 10 | 317,305 | 2440.81× | OK |
| 2024 | 3,535,302 | 10 | 353,530 | 2719.46× | OK |
| 2025 | 3,587,097 | 8 | 448,387 | 3449.13× | OK |

End-state (2025): **£448,387/account** across 8 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,417 | 81838.0× | OK |
| 2017 | 467 | 560 | 2,497,933 | 4460.8× | OK |
| 2018 | 850 | 1,020 | 2,486,501 | 2437.3× | OK |
| 2019 | 1,545 | 1,854 | 2,606,333 | 1406.1× | OK |
| 2020 | 1,980 | 2,376 | 2,899,744 | 1220.3× | OK |
| 2021 | 4,409 | 5,291 | 2,921,202 | 552.1× | OK |
| 2022 | 8,508 | 10,210 | 3,069,116 | 300.6× | OK |
| 2023 | 5,614 | 6,737 | 3,173,051 | 471.0× | OK |
| 2024 | 2,735 | 3,282 | 3,535,302 | 1077.2× | OK |
| 2025 | 4,177 | 5,012 | 3,587,097 | 715.7× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,490.22 | £12,224.40 | £261.80/MWh | £144.51/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,978.92 | £9,697.46 | £272.57/MWh | £154.48/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,931.52 | £9,309.30 | £250.21/MWh | £141.70/MWh | +10.9% |

Total HH revenue: £63,631.82 vs flat equivalent £58,729.67 (+8.3% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 36 | 100% | C8 (2016-10-31) |
| 2017 | 54 | 81% | C8 (2017-11-30) |
| 2018 | 62 | 101% | C4g (2018-10-31) |
| 2019 | 63 | 126% | C_IC1 (2019-03-31) |
| 2020 | 57 | 117% | C_IC2 (2020-03-31) |
| 2021 | 55 | 83% | C_IC2 (2021-04-30) |
| 2022 | 59 | 1735% | C2_2 (2022-04-30) |
| 2023 | 46 | 100% | C_IC2 (2023-06-30) |
| 2024 | 33 | 107% | C_IC2 (2024-07-31) |
| 2025 | 20 | 80% | C7 (2025-06-07) |

Total: **485** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1735% | no |
| 2022-10-31 | C4g | +228% | no |
| 2019-03-31 | C_IC1 | +126% | no |
| 2020-03-31 | C_IC2 | +117% | no |
| 2022-01-31 | C_IC3 | +109% | no |
| 2024-07-31 | C_IC2 | +107% | no |
| 2018-10-31 | C4g | +101% | no |
| 2016-10-31 | C8 | +100% | no |
| 2023-06-30 | C_IC2 | +100% | no |
| 2023-10-31 | C8 | +92% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 12% | 12% | 0 |
| 2017 | 4 | 16% | 23% | 2 ⚠ |
| 2018 | 4 | 17% | 23% | 2 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 5 | 5% | 24% | 1 ⚠ |
| 2021 | 3 | 69% | 95% | 3 ⚠ |
| 2022 | 2 | 49% | 95% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 1 | 4% | 4% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £20.2 | £124.0 (+514%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £16.1 | £35.0 (+118%) | 74% |
| 2021-03-31 | C2g | £21.8 | £35.0 (+61%) | 40% |
| 2020-12-31 | C_IC3g | £15.4 | £20.2 (+31%) | 24% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 18 |
| Retained | 17 (94%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £422,555.01 |
| Margin saved (retained customers' terms) | £2,225,202.82 |
| Wasted offer cost (churned anyway) | £510.00 |
| **Net ROI of retention strategy** | **£1,802,647.81** |
| Acquisition cost avoided (retained customers) | £2,800.00 |
| **Full economic ROI (margin + acq savings)** | **£1,805,447.81** |

Missed opportunities (churns with no offer): **5** (£3,965.32 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 5 (£3,965.32 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24333.42 | £164194.23 | £139860.81 | £0.00 |
| 2019 | 2 | 2 | £43010.55 | £297885.77 | £254875.22 | £0.00 |
| 2020 | 3 | 3 | £26923.61 | £164840.40 | £137916.80 | £585.53 |
| 2021 | 4 | 3 | £120957.41 | £417139.64 | £296182.23 | £-178.13 |
| 2022 | 2 | 2 | £74542.95 | £330321.35 | £255778.41 | £236.63 |
| 2023 | 4 | 4 | £88304.27 | £443469.11 | £355164.84 | £0.00 |
| 2024 | 2 | 2 | £44482.80 | £407352.32 | £362869.52 | £3321.29 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24333.42 | £164194.23 | £150 | £139860.81 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14931.27 | £102253.79 | £150 | £87322.53 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £28079.28 | £195631.97 | £150 | £167552.69 | retained |
| 2020-01-01 | C_IC3 | 0.36 | 3% | £5731.95 | £10773.61 | £150 | £5041.66 | retained |
| 2020-03-31 | C_IC1 | 0.50 | 5% | £10390.59 | £131076.00 | £150 | £120685.41 | retained |
| 2020-12-31 | C_IC3 | 0.59 | 5% | £10801.06 | £22990.79 | £150 | £12189.73 | retained |
| 2021-03-31 | C_IC2 | 0.84 | 8% | £14250.30 | £91903.21 | £150 | £77652.91 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £22658.39 | £159188.35 | £150 | £136529.96 | retained |
| 2021-12-30 | C5 | 0.83 | 8% | £510.00 | £2242.79 | £400 | £-510.00 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £83538.73 | £166048.08 | £150 | £82509.35 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25479.09 | £96837.46 | £150 | £71358.38 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £49063.86 | £233483.89 | £150 | £184420.03 | retained |
| 2023-03-31 | C6 | 0.49 | 3% | £230.77 | £3265.26 | £400 | £3034.49 | retained |
| 2023-05-30 | C_IC2 | 0.58 | 5% | £11868.71 | £132247.33 | £150 | £120378.62 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £35196.25 | £246750.65 | £150 | £211554.40 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £41008.55 | £61205.87 | £150 | £20197.33 | retained |
| 2024-06-28 | C_IC2 | 0.54 | 5% | £10346.45 | £134846.74 | £150 | £124500.29 | retained |
| 2024-07-28 | C_IC1 | 0.95 | 8% | £34136.35 | £272505.58 | £150 | £238369.23 | retained |

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

**Full-history EV:** £6,142,208.62 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £439,024.28 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,183.52 |
| 2017 | £30,788.53 |
| 2018 | £99,664.21 |
| 2019 | £218,117.41 |
| 2020 | £116,838.09 |
| 2021 | £58,203.88 |
| 2022 | £256,102.05 |
| 2023 | £50,721.34 | ← trailing
| 2024 | £319,131.05 | ← trailing
| 2025 | £92,421.46 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £3,654.29 | — |
| C2 | £5,137.17 | — |
| C2_2 | — | £958.06 |
| C3 | £5,238.25 | — |
| C4 | £3,198.47 | £-747.29 |
| C5 | £8,112.54 | — |
| C6 | £14,186.25 | £2,497.68 |
| C7 | £6,903.10 | £109.26 |
| C8 | £7,234.94 | £372.59 |
| C9 | £7,237.23 | £926.54 |
| C_IC1 | £1,454,809.57 | £334,433.70 |
| C_IC2 | £758,306.98 | £177,046.43 |
| C_IC3 | £2,560,889.20 | £-84,811.48 |
| C_IC4 | £1,303,925.41 | £8,238.81 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £1,727.79 | — | — | — | — | £4,331.69 | — | £3,079.50 | — | — | — | — | — | — |
| 2017 | £1,834.46 | £3,845.47 | — | £3,730.10 | £3,723.31 | £4,493.22 | £8,284.77 | £3,212.01 | £4,623.29 | £4,051.31 | — | — | — | — |
| 2018 | £2,007.61 | £3,593.76 | — | £3,400.64 | £2,778.65 | £4,087.54 | £6,910.42 | £3,080.36 | £3,962.14 | £3,704.97 | £983,140.96 | — | — | — |
| 2019 | £1,991.57 | £3,006.07 | — | £3,386.89 | £2,989.84 | £4,369.12 | £7,512.22 | £3,254.24 | £3,878.29 | £3,803.94 | £890,818.67 | £540,191.42 | — | — |
| 2020 | £2,287.96 | £3,238.37 | — | £3,174.03 | £3,151.22 | £4,837.87 | £8,240.46 | £3,792.02 | £4,115.73 | £3,732.10 | £638,472.46 | £308,644.99 | £1,024,824.72 | £663,152.56 |
| 2021 | £2,105.76 | £3,477.85 | — | £3,018.74 | £2,809.06 | £4,948.83 | £8,571.73 | £3,382.53 | £4,338.89 | £3,485.40 | £581,668.67 | £327,641.63 | £999,008.37 | £638,131.04 |
| 2022 | £2,221.79 | £2,850.49 | £489.86 | £3,096.38 | £1,737.71 | £4,855.61 | £8,314.16 | £2,802.43 | £3,939.70 | £3,932.31 | £642,644.36 | £368,678.13 | £1,152,376.47 | £607,608.83 |
| 2023 | £2,215.68 | £2,843.06 | £1,365.51 | £3,088.62 | £1,389.34 | £4,846.81 | £9,087.53 | £2,990.54 | £4,007.67 | £4,202.25 | £694,431.39 | £396,111.17 | £1,073,297.77 | £627,407.36 |
| 2024 | £2,129.42 | £3,011.83 | £1,980.54 | £3,165.16 | £1,860.01 | £4,779.97 | £8,862.50 | £3,258.96 | £4,316.77 | £4,696.18 | £719,251.10 | £418,284.31 | £1,286,872.53 | £725,042.13 |
| 2025 | £2,044.69 | £3,023.51 | £2,043.64 | £3,071.98 | £1,813.98 | £4,510.86 | £8,751.25 | £3,569.06 | £4,069.28 | £4,517.12 | £767,123.67 | £453,841.77 | £1,389,002.31 | £784,462.04 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,807.83, range £58.95–£26,478.86.

- C1: cost to serve £414.46, net margin after CTS £2,318.20
- C1g: cost to serve £58.95, net margin after CTS £1,369.99
- C2: cost to serve £432.19, net margin after CTS £2,973.40
- C2_2: cost to serve £381.13, net margin after CTS £5,083.44
- C2g: cost to serve £93.15, net margin after CTS £2,154.87
- C3: cost to serve £292.47, net margin after CTS £2,091.46
- C3g: cost to serve £69.68, net margin after CTS £1,481.29
- C4: cost to serve £565.44, net margin after CTS £2,746.37
- C4g: cost to serve £250.05, net margin after CTS £1,550.57
- C5: cost to serve £871.81, net margin after CTS £8,498.31
- C6: cost to serve £1,349.24, net margin after CTS £21,078.65
- C7: cost to serve £953.43, net margin after CTS £9,762.43
- C8: cost to serve £938.96, net margin after CTS £11,499.58
- C9: cost to serve £896.54, net margin after CTS £11,794.76
- C_IC1: cost to serve £20,028.17, net margin after CTS £1,875,070.23
- C_IC2: cost to serve £11,448.35, net margin after CTS £909,892.59
- C_IC3: cost to serve £26,478.86, net margin after CTS £1,788,045.18
- C_IC3g: cost to serve £9,229.97, net margin after CTS £613,417.06
- C_IC4: cost to serve £16,595.90, net margin after CTS £1,100,681.25


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 29 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 13.9%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,749.07 | £10,901.23 | +20.0% | £112.24/MWh | £152.07/MWh |
| C5 | electricity | 2018-12-31 | £-204.77 | £2,324.09 | +3.8% | £148.68/MWh | £153.44/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,332.71 | £6,376.41 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,269.51 | £10,243.03 | +20.0% | £128.22/MWh | £175.53/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,922.12 | £3,444.18 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £177.20/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.62/MWh |
| C4g | gas | 2021-09-30 | £-95.91 | £791.17 | +7.1% | £53.99/MWh | £60.11/MWh |
| C5 | electricity | 2021-12-30 | £-340.93 | £2,699.80 | +7.6% | £311.83/MWh | £340.84/MWh |
| C7 | electricity | 2021-12-30 | £-123.70 | £1,986.63 | +1.2% | £311.83/MWh | £320.56/MWh |
| C_IC3 | electricity | 2021-12-31 | £-27,854.05 | £447,357.18 | +1.2% | £224.03/MWh | £260.79/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £316.79/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £307.52/MWh |
| C4 | electricity | 2022-09-30 | £-221.67 | £906.59 | +19.4% | £404.86/MWh | £485.58/MWh |
| C4g | gas | 2022-09-30 | £-982.92 | £1,134.54 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,835.40 | £2,404.50 | +20.0% | £266.73/MWh | £318.74/MWh |
| C_IC3g | gas | 2022-12-31 | £-48,818.20 | £586,562.16 | +3.3% | £101.23/MWh | £120.28/MWh |
| C8 | electricity | 2023-03-31 | £-353.94 | £3,898.74 | +4.1% | £319.17/MWh | £336.10/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.14/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £219.98/MWh |
| C4 | electricity | 2023-09-30 | £-279.60 | £1,324.46 | +16.1% | £216.77/MWh | £249.73/MWh |
| C4g | gas | 2023-09-30 | £-2,138.05 | £3,037.35 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-351.18 | £3,990.91 | +3.8% | £242.22/MWh | £238.85/MWh |
| C_IC3 | electricity | 2023-12-31 | £-171,865.89 | £937,552.87 | +13.3% | £118.95/MWh | £128.07/MWh |
| C_IC3g | gas | 2023-12-31 | £-30,262.44 | £295,562.62 | +5.2% | £51.89/MWh | £61.01/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |
| C_IC3g | gas | 2024-12-30 | £-36,843.35 | £268,211.20 | +8.7% | £50.47/MWh | £61.67/MWh |


## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 112 renewal(s) (26 gas) based on recent portfolio-wide margin rates: 61 surcharge(s), 51 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | 7.4% | +0.3% | £131.49/MWh | £131.90/MWh |
| C1g | gas | 2016-12-31 | 19.2% | -5.0% | £27.63/MWh | £26.25/MWh |
| C5 | electricity | 2016-12-31 | 8.7% | -0.3% | £131.49/MWh | £131.05/MWh |
| C7 | electricity | 2016-12-31 | 9.3% | -0.7% | £131.49/MWh | £130.60/MWh |
| C2 | electricity | 2017-04-01 | 11.4% | -1.7% | £127.97/MWh | £125.78/MWh |
| C2g | gas | 2017-04-01 | 19.1% | -5.0% | £34.54/MWh | £32.81/MWh |
| C6 | electricity | 2017-04-01 | 10.7% | -1.3% | £127.97/MWh | £126.27/MWh |
| C8 | electricity | 2017-04-01 | 9.8% | -0.9% | £127.97/MWh | £126.81/MWh |
| C3 | electricity | 2017-07-01 | 11.1% | -1.6% | £122.23/MWh | £120.31/MWh |
| C3g | gas | 2017-07-01 | 20.0% | -5.0% | £24.33/MWh | £23.11/MWh |
| C9 | electricity | 2017-07-01 | 10.8% | -1.4% | £122.23/MWh | £120.53/MWh |
| C4 | electricity | 2017-10-01 | 10.7% | -1.4% | £111.62/MWh | £110.09/MWh |
| C4g | gas | 2017-10-01 | 18.0% | -5.0% | £27.48/MWh | £26.10/MWh |
| C1 | electricity | 2017-12-31 | 11.8% | -1.9% | £120.10/MWh | £117.80/MWh |
| C1g | gas | 2017-12-31 | 15.4% | -3.7% | £34.79/MWh | £33.50/MWh |
| C5 | electricity | 2017-12-31 | 8.8% | -0.4% | £120.10/MWh | £119.60/MWh |
| C7 | electricity | 2017-12-31 | 3.7% | +2.2% | £120.10/MWh | £122.70/MWh |
| C_IC1 | electricity | 2018-01-31 | -17.8% | +12.9% | £112.24/MWh | £126.72/MWh |
| C2 | electricity | 2018-04-01 | -6.6% | +7.3% | £133.89/MWh | £143.66/MWh |
| C2g | gas | 2018-04-01 | 15.2% | -3.6% | £38.21/MWh | £36.82/MWh |
| C6 | electricity | 2018-04-01 | -4.1% | +6.0% | £133.89/MWh | £141.97/MWh |
| C8 | electricity | 2018-04-01 | 8.0% | -0.0% | £133.89/MWh | £133.88/MWh |
| C3 | electricity | 2018-07-01 | 10.0% | -1.0% | £128.29/MWh | £126.99/MWh |
| C3g | gas | 2018-07-01 | 13.6% | -2.8% | £29.63/MWh | £28.79/MWh |
| C9 | electricity | 2018-07-01 | 1.7% | +3.1% | £128.29/MWh | £132.33/MWh |
| C4 | electricity | 2018-10-01 | 1.9% | +3.0% | £145.00/MWh | £149.42/MWh |
| C4g | gas | 2018-10-01 | 13.8% | -2.9% | £34.60/MWh | £33.60/MWh |
| C1 | electricity | 2018-12-31 | 6.6% | +0.7% | £148.68/MWh | £149.70/MWh |
| C1g | gas | 2018-12-31 | 13.8% | -2.9% | £37.15/MWh | £36.07/MWh |
| C5 | electricity | 2018-12-31 | 9.2% | -0.6% | £148.68/MWh | £147.80/MWh |
| C7 | electricity | 2018-12-31 | 9.5% | -0.8% | £148.68/MWh | £147.55/MWh |
| C_IC2 | electricity | 2019-01-31 | -29.9% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -20.2% | +14.1% | £128.22/MWh | £146.28/MWh |
| C2 | electricity | 2019-04-01 | 3.3% | +2.3% | £148.35/MWh | £151.82/MWh |
| C2g | gas | 2019-04-01 | 8.8% | -0.4% | £32.94/MWh | £32.80/MWh |
| C6 | electricity | 2019-04-01 | 7.6% | +0.2% | £148.35/MWh | £148.64/MWh |
| C8 | electricity | 2019-04-01 | 26.9% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 19.4% | -5.0% | £127.03/MWh | £120.68/MWh |
| C3g | gas | 2019-07-01 | 11.6% | -1.8% | £23.62/MWh | £23.19/MWh |
| C9 | electricity | 2019-07-01 | 9.9% | -1.0% | £127.03/MWh | £125.81/MWh |
| C4 | electricity | 2019-10-01 | 7.9% | +0.1% | £126.72/MWh | £126.81/MWh |
| C4g | gas | 2019-10-01 | 15.2% | -3.6% | £20.41/MWh | £19.67/MWh |
| C1 | electricity | 2019-12-31 | 10.5% | -1.2% | £127.44/MWh | £125.86/MWh |
| C1g | gas | 2019-12-31 | 11.5% | -1.7% | £26.17/MWh | £25.71/MWh |
| C5 | electricity | 2019-12-31 | 10.1% | -1.0% | £127.44/MWh | £126.12/MWh |
| C7 | electricity | 2019-12-31 | 8.8% | -0.4% | £127.44/MWh | £126.90/MWh |
| C_IC3 | electricity | 2020-01-01 | 7.4% | +0.3% | £47.59/MWh | £47.72/MWh |
| C_IC3g | gas | 2020-01-01 | 19.9% | -5.0% | £16.25/MWh | £15.44/MWh |
| C_IC2 | electricity | 2020-03-01 | -59.3% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -51.9% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 17.2% | -4.6% | £22.80/MWh | £21.75/MWh |
| C6 | electricity | 2020-03-31 | -47.2% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -16.3% | +12.2% | £125.12/MWh | £140.32/MWh |
| C_IC1 | electricity | 2020-03-31 | 20.0% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 16.5% | -4.2% | £113.43/MWh | £108.62/MWh |
| C9 | electricity | 2020-06-30 | 16.5% | -4.2% | £113.43/MWh | £108.62/MWh |
| C4 | electricity | 2020-09-30 | 11.1% | -1.6% | £124.42/MWh | £122.49/MWh |
| C4g | gas | 2020-09-30 | 19.1% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 9.7% | -0.8% | £133.55/MWh | £132.45/MWh |
| C1g | gas | 2020-12-30 | 13.1% | -2.5% | £28.99/MWh | £28.25/MWh |
| C5 | electricity | 2020-12-30 | 4.5% | +1.7% | £133.55/MWh | £135.86/MWh |
| C7 | electricity | 2020-12-30 | -3.1% | +5.5% | £133.55/MWh | £140.97/MWh |
| C_IC3 | electricity | 2020-12-31 | -4.4% | +6.2% | £50.65/MWh | £53.78/MWh |
| C_IC3g | gas | 2020-12-31 | 6.6% | +0.7% | £20.05/MWh | £20.19/MWh |
| C2 | electricity | 2021-03-31 | -20.8% | +14.4% | £175.90/MWh | £201.26/MWh |
| C2g | gas | 2021-03-31 | 5.8% | +1.1% | £36.20/MWh | £36.60/MWh |
| C6 | electricity | 2021-03-31 | -16.2% | +12.1% | £175.90/MWh | £197.14/MWh |
| C8 | electricity | 2021-03-31 | -11.9% | +10.0% | £175.90/MWh | £193.42/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.6% | +6.3% | £138.90/MWh | £147.67/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.9% | +3.5% | £113.97/MWh | £118.02/MWh |
| C9 | electricity | 2021-06-30 | 1.1% | +3.4% | £170.38/MWh | £176.24/MWh |
| C4 | electricity | 2021-09-30 | -2.4% | +5.2% | £205.15/MWh | £215.80/MWh |
| C4g | gas | 2021-09-30 | 0.1% | +3.9% | £53.99/MWh | £56.11/MWh |
| C1 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.68/MWh |
| C5 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.68/MWh |
| C7 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.68/MWh |
| C_IC3 | electricity | 2021-12-31 | -22.9% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -18.5% | +13.2% | £109.48/MWh | £123.98/MWh |
| C2 | electricity | 2022-03-31 | -23.2% | +15.0% | £361.95/MWh | £416.24/MWh |
| C6 | electricity | 2022-03-31 | -16.9% | +12.4% | £361.95/MWh | £407.01/MWh |
| C8 | electricity | 2022-03-31 | 5.1% | +1.5% | £361.95/MWh | £367.22/MWh |
| C_IC2 | electricity | 2022-04-30 | -9.5% | +8.8% | £269.81/MWh | £293.46/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.1% | +7.0% | £239.42/MWh | £256.27/MWh |
| C9 | electricity | 2022-06-30 | 4.3% | +1.8% | £255.09/MWh | £259.77/MWh |
| C4 | electricity | 2022-09-30 | 7.2% | +0.4% | £404.86/MWh | £406.51/MWh |
| C4g | gas | 2022-09-30 | -22.6% | +15.0% | £183.79/MWh | £211.36/MWh |
| C7 | electricity | 2022-12-30 | 8.8% | -0.4% | £266.73/MWh | £265.61/MWh |
| C_IC3 | electricity | 2022-12-31 | 0.3% | +3.9% | £168.36/MWh | £174.86/MWh |
| C_IC3g | gas | 2022-12-31 | -40.3% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -11.9% | +9.9% | £319.17/MWh | £350.91/MWh |
| C6 | electricity | 2023-03-31 | -1.0% | +4.5% | £319.17/MWh | £333.52/MWh |
| C8 | electricity | 2023-03-31 | 5.7% | +1.2% | £319.17/MWh | £322.93/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.5% | +14.8% | £171.46/MWh | £196.78/MWh |
| C_IC1 | electricity | 2023-06-29 | -16.7% | +12.3% | £163.19/MWh | £183.31/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.13/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.08/MWh |
| C4g | gas | 2023-09-30 | -43.9% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 23.7% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -15.4% | +11.7% | £51.89/MWh | £57.97/MWh |
| C2_2 | electricity | 2024-03-30 | 16.3% | -4.2% | £207.71/MWh | £199.08/MWh |
| C6 | electricity | 2024-03-30 | 9.8% | -0.9% | £207.71/MWh | £205.79/MWh |
| C8 | electricity | 2024-03-30 | 9.8% | -0.9% | £207.71/MWh | £205.79/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.0% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.2% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.5% | +3.8% | £195.97/MWh | £203.31/MWh |
| C7 | electricity | 2024-12-29 | 0.5% | +3.8% | £243.79/MWh | £252.92/MWh |
| C_IC3 | electricity | 2024-12-30 | 18.8% | -5.0% | £116.37/MWh | £110.55/MWh |
| C_IC3g | gas | 2024-12-30 | -16.8% | +12.4% | £50.47/MWh | £56.72/MWh |
| C2_2 | electricity | 2025-03-30 | 9.0% | -0.5% | £284.89/MWh | £283.45/MWh |
| C8 | electricity | 2025-03-30 | 6.1% | +1.0% | £284.89/MWh | £287.64/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **5** | Blind misses: **5** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 5 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £3,965.32 | deliberate: £0.00 | total: £3,965.32

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.35 | Yes | £585.53 |
| C1 | 2021-12-30 | Blind miss | 0.04 | 0.32 | Yes | £-178.13 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.32 | Yes | £236.63 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.38 | Yes | £2,852.65 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.35 | Yes | £468.64 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C2+C2g | £715.31 | £855.45 | £1,570.77 | Yes |
| C1+C1g | £421.02 | £640.44 | £1,061.47 | Yes |
| C3+C3g | £201.13 | £292.68 | £493.81 | Yes |
| C4+C4g | £135.44 | £-2,140.87 | £-2,005.43 | No |
| C_IC3+C_IC3g | £83,751.32 | £-132,711.18 | £-48,959.87 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-133,063.47.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,243,171.55 across 19 billing accounts. Revenue: £14,137,721.17.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,162,008.72 | £1,895,098.39 | £18,631.73 | £837,491.36 | 26.5% |
| 2 | C_IC2 | fixed | £1,546,034.28 | £921,340.94 | £8,637.94 | £432,702.23 | 28.0% |
| 3 | C_IC3 | pass_through | £4,652,107.31 | £1,814,524.04 | £23,159.91 | £83,751.32 | 1.8% |
| 4 | C_IC4 | flex | £2,775,475.73 | £1,117,277.15 | £0.00 | £14,685.55 | 0.5% |
| 5 | C6 | fixed | £38,946.25 | £22,427.89 | £264.99 | £3,555.32 | 9.1% |
| 6 | C8 | fixed | £21,676.38 | £12,438.54 | £135.12 | £1,485.67 | 6.9% |
| 7 | C9 | fixed | £20,240.82 | £12,691.29 | £131.69 | £1,475.41 | 7.3% |
| 8 | C2_2 | fixed | £10,281.82 | £5,464.58 | £67.96 | £1,035.87 | 10.1% |
| 9 | C2g | fixed | £4,313.60 | £2,248.02 | £21.64 | £855.45 | 19.8% |
| 10 | C2 | fixed | £5,112.90 | £3,405.60 | £24.79 | £715.31 | 14.0% |
| 11 | C1g | fixed | £2,603.89 | £1,428.94 | £18.62 | £640.44 | 24.6% |
| 12 | C1 | fixed | £4,226.55 | £2,732.66 | £19.22 | £421.02 | 10.0% |
| 13 | C3g | fixed | £3,254.62 | £1,550.97 | £15.14 | £292.68 | 9.0% |
| 14 | C3 | fixed | £3,626.16 | £2,383.94 | £14.79 | £201.13 | 5.5% |
| 15 | C4 | fixed | £6,277.26 | £3,311.80 | £37.58 | £135.44 | 2.2% |
| 16 | C5 | fixed | £15,196.22 | £9,370.12 | £77.51 | £-42.27 | -0.3% |
| 17 | C7 | fixed | £21,714.61 | £10,715.86 | £139.66 | £-1,378.34 | -6.3% |
| 18 | C4g | fixed | £12,044.15 | £1,800.62 | £143.36 | £-2,140.87 | -17.8% |
| 19 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £185,126.72 | £-132,711.18 | -7.2% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,137,721 | 100.0% |
| Wholesale cost | -£7,674,863 | 54.3% |
| **Gross supply margin** | **£6,462,858** | **45.7%** |
| Policy + Network costs | -£4,983,018 | 35.2% |
| Capital cost | -£236,668 | 1.7% |
| **Net supply margin** | **£1,243,172** | **8.8%** |

> *The ledger's `net_margin_gbp` (£6,239,957) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,135,626 | 47.4% | 11.3% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | -7.2% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £54,142 | 58.7% | 6.5% | CMA 3-8% | ✓ |
| resi/elec | £82,875 | 57.5% | 3.7% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £22,216 | 31.6% | -1.6% | Ofgem CMA 2-4% | ✓ |

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
| Customer bills (all-in) | £19,933,040.74 |
|   Less: VAT remitted to HMRC | (£959,271.15) |
| = Revenue (ex-VAT) | £18,973,769.59 |
| Less: non-commodity pass-through | (£4,822,281.02) |
| Wholesale cost (settlement events) | (£7,674,862.80) |
| Gross margin | £6,476,625.78 |
| Capital charges | (£236,668.36) |
| Net margin | £6,239,957.41 |

_Cash reconciliation: of £19,933,040.74 billed, bad debt of £398,766.16 was written off, leaving £19,534,274.58 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £6,800,462.40._

| Acquisition spend | (£1,100.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £6,233,157.41 |

## Management Accounts

P&L and balance sheet from double-entry journal (account codes), not formulas.

| Year | Revenue | COGS | Gross | OpEx | Net | Cash | Equity |
|------|---------|------|-------|------|-----|------|--------||
| 2016 | £15,499.70 | (£7,581.80) | £7,917.90 | (£919.75) | £6,998.16 | £2,470,621.68 | £2,473,634.38 |
| 2017 | £351,275.24 | (£225,655.30) | £125,619.94 | (£8,172.18) | £117,447.76 | £2,558,810.52 | £2,591,082.14 |
| 2018 | £604,870.01 | (£339,679.89) | £265,190.12 | (£14,006.24) | £251,183.88 | £2,787,096.65 | £2,842,266.02 |
| 2019 | £1,649,808.08 | (£945,239.41) | £704,568.66 | (£42,981.99) | £661,586.67 | £3,346,957.70 | £3,503,852.69 |
| 2020 | £1,861,834.94 | (£1,066,732.67) | £795,102.28 | (£46,434.72) | £748,667.56 | £4,069,913.77 | £4,252,520.25 |
| 2021 | £2,443,993.64 | (£1,669,827.08) | £774,166.55 | (£64,202.94) | £709,963.61 | £4,665,147.44 | £4,962,483.86 |
| 2022 | £4,285,832.40 | (£3,222,655.83) | £1,063,176.58 | (£150,767.93) | £912,408.65 | £5,437,283.15 | £5,874,892.51 |
| 2023 | £3,464,272.95 | (£2,543,484.94) | £920,788.01 | (£126,417.20) | £794,370.81 | £6,363,292.06 | £6,669,263.31 |
| 2024 | £3,053,548.64 | (£1,758,516.41) | £1,295,032.23 | (£121,728.64) | £1,173,303.58 | £7,551,401.76 | £7,842,566.90 |
| 2025 | £1,242,833.99 | (£719,086.48) | £523,747.52 | (£66,602.93) | £457,144.59 | £8,299,711.49 | £8,299,711.49 |

**Cross-check:** FAIL -- Journal: £5,833,075.27, Sim: £1,243,171.55, Variance: 369.2%

**Balance sheet -- 2025 year-end:**

| Account | GBP |
|---------|-----|
| Cash and Treasury (1001) | £8,299,711.49 |
| Trade Receivables (1100) | £-0.00 |
| **Total Assets** | **£8,299,711.49** |
| Opening Capital (3001) | £2,466,636.22 |
| Cumulative Net Profit | £5,833,075.27 |
| **Total Equity** | **£8,299,711.49** |
| A = L + E | OK |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,499.70 | +5.6% | £6,592.99 | £6,998.16 | +6.1% | AMBER |
| 2017 | £16,138.86 | £351,275.24 | +2076.6% | £7,252.29 | £117,447.76 | +1519.5% | RED |
| 2018 | £386,623.75 | £604,870.01 | +56.4% | £128,424.00 | £251,183.88 | +95.6% | RED |
| 2019 | £675,851.95 | £1,649,808.08 | +144.1% | £281,335.50 | £661,586.67 | +135.2% | RED |
| 2020 | £1,816,630.04 | £1,861,834.94 | +2.5% | £736,963.94 | £748,667.56 | +1.6% | GREEN |
| 2021 | £2,028,952.42 | £2,443,993.64 | +20.5% | £833,649.22 | £709,963.61 | -14.8% | AMBER |
| 2022 | £2,607,611.88 | £4,285,832.40 | +64.4% | £790,935.58 | £912,408.65 | +15.4% | RED |
| 2023 | £4,508,414.67 | £3,464,272.95 | -23.2% | £1,029,561.00 | £794,370.81 | -22.8% | RED |
| 2024 | £3,512,844.39 | £3,053,548.64 | -13.1% | £893,105.75 | £1,173,303.58 | +31.4% | RED |
| 2025 | £3,145,356.42 | £1,242,833.99 | -60.5% | £1,315,150.33 | £457,144.59 | -65.2% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,233,157.41

## 2016

**Trading & Risk**

- Net margin: £1,183.52 (gross £6,865.76, capital £86.43)
  - Electricity: gross £5,997.23, capital £79.14, net £875.81
  - Gas: gross £868.53, capital £7.29, net £307.71
- Treasury at year end: £2,467,416.56
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.23, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-01-31: treasury £2,466,648.35, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-03-01: treasury £2,466,660.58, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-03-31: treasury £2,466,672.53, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-04-30: treasury £2,466,683.60, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-05-30: treasury £2,466,694.59, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-06-29: treasury £2,466,705.16, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-07-29: treasury £2,466,715.85, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-08-28: treasury £2,466,726.57, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-09-27: treasury £2,466,737.46, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-10-27: treasury £2,466,748.35, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-11-26: treasury £2,466,759.12, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
  - 2016-12-26: treasury £2,466,771.02, C1->1.00, VaR (current £27.79 / stressed £8.54) ratio 3.25
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.25
- Worst single period: C6 on 2016-11-08 period 40, net margin £-0.36

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £3,046.32
  - By billing account: C1 £1,727.79, C5 £4,331.69, C7 £3,079.50
- Bill shock events (>=20%): 36 -- C1g 2016-04-30 (28%); C1g 2016-06-30 (24%); C1g 2016-10-31 (41%); C1g 2016-11-30 (46%); C1g 2016-12-31 (20%); C5 2016-05-31 (27%); C5 2016-10-31 (40%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (77%); C7 2016-11-30 (52%); C2g 2016-05-31 (22%); C2g 2016-06-30 (30%); C2g 2016-10-31 (53%); C2g 2016-11-30 (56%); C2g 2016-12-31 (22%); C6 2016-05-31 (25%); C6 2016-06-30 (23%); C6 2016-10-31 (40%); C6 2016-11-30 (46%); C8 2016-05-31 (40%); C8 2016-06-30 (40%); C8 2016-09-30 (22%); C8 2016-10-31 (100%); C8 2016-11-30 (68%); C3g 2016-09-30 (21%); C3g 2016-10-31 (55%); C3g 2016-11-30 (58%); C3g 2016-12-31 (23%); C9 2016-10-31 (74%); C9 2016-11-30 (58%); C4 2016-11-30 (28%); C4g 2016-11-30 (62%); C4g 2016-12-31 (23%)
- Churn risk (accounts renewing in 2016): 3 at risk (≥20% churn prob): C1 26%, C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.30-£131.90/MWh, net margin £136.81
- C1g (gas): tariff £24.34-£26.25/MWh, net margin £96.50
- C2 (electricity): tariff £107.62/MWh, net margin £65.10
- C2g (gas): tariff £26.92/MWh, net margin £113.59
- C3 (electricity): tariff £98.21/MWh, net margin £21.37
- C3g (gas): tariff £21.93/MWh, net margin £41.94
- C4 (electricity): tariff £98.43/MWh, net margin £11.33
- C4g (gas): tariff £24.40/MWh, net margin £55.67
- C5 (electricity): tariff £117.30-£131.05/MWh, net margin £247.28
- C6 (electricity): tariff £107.62/MWh, net margin £4.78
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £233.22
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £120.18
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £35.75

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.863, average bill shock 19.8%, bad debt provision £168.75, avg complaint probability 4.4%
- Solvency signal: £274,157/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £2,055.89 vs. naked (unhedged) net margin: £11,249.78
- hedging cost £9,193.89 vs. a fully unhedged book (commodity-only: actual net £2,055.89 vs. naked net £11,249.78)
  - C1: actual £256.75 vs. naked £827.87 -- hedging cost £571.12
  - C1g: actual £201.41 vs. naked £418.28 -- hedging cost £216.86
  - C2: actual £83.46 vs. naked £370.80 -- hedging cost £287.34
  - C2g: actual £167.17 vs. naked £478.23 -- hedging cost £311.06
  - C3: actual £29.43 vs. naked £414.43 -- hedging cost £385.00
  - C3g: actual £79.01 vs. naked £528.45 -- hedging cost £449.44
  - C4: actual £48.21 vs. naked £261.04 -- hedging cost £212.83
  - C4g: actual £174.79 vs. naked £810.89 -- hedging cost £636.10
  - C5: actual £411.72 vs. naked £2,694.56 -- hedging cost £2,282.84
  - C6: actual £-21.96 vs. naked £1,067.90 -- hedging cost £1,089.85
  - C7: actual £393.17 vs. naked £1,939.75 -- hedging cost £1,546.57
  - C8: actual £174.46 vs. naked £784.20 -- hedging cost £609.74
  - C9: actual £58.27 vs. naked £653.38 -- hedging cost £595.11

**Year narrative:** 2016 produced a net gain of £1,183.52 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 36 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £30,788.53 (gross £124,065.04, capital £1,275.64)
  - Electricity: gross £122,440.10, capital £1,260.94, net £30,292.86
  - Gas: gross £1,624.95, capital £14.71, net £495.67
- Treasury at year end: £2,497,933.00
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.92 (avg 0.92), C7 0.91 (avg 0.91), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,467,421.24, C1->1.00, C5->1.00, C7->1.00, VaR (current £308.21 / stressed £98.32) ratio 3.13
  - 2017-02-24: treasury £2,467,427.20, C1->1.00, C5->1.00, C7->1.00, VaR (current £308.21 / stressed £98.32) ratio 3.13
  - 2017-03-26: treasury £2,467,433.59, C1->1.00, C5->1.00, C7->1.00, VaR (current £308.21 / stressed £98.32) ratio 3.13
  - 2017-04-25: treasury £2,467,781.75, C1->1.00, C5->1.00, C7->1.00, VaR (current £861.25 / stressed £330.55) ratio 2.61
  - 2017-05-25: treasury £2,467,782.13, C1->1.00, C5->1.00, C7->1.00, VaR (current £861.25 / stressed £330.55) ratio 2.61
  - 2017-06-24: treasury £2,467,783.58, C1->1.00, C5->1.00, C7->1.00, VaR (current £861.25 / stressed £330.55) ratio 2.61
  - 2017-07-24: treasury £2,467,960.22, C1->1.00, C5->1.00, C7->1.00, VaR (current £998.85 / stressed £395.42) ratio 2.53
  - 2017-08-23: treasury £2,467,964.86, C1->1.00, C5->1.00, C7->1.00, VaR (current £998.85 / stressed £395.42) ratio 2.53
  - 2017-09-22: treasury £2,467,968.57, C1->1.00, C5->1.00, C7->1.00, VaR (current £998.85 / stressed £395.42) ratio 2.53
  - 2017-10-22: treasury £2,468,242.07, C5->1.00, C7->1.00, VaR (current £1,007.23 / stressed £402.14) ratio 2.50
  - 2017-11-21: treasury £2,468,251.80, C5->1.00, C7->1.00, VaR (current £1,007.23 / stressed £402.14) ratio 2.50
  - 2017-12-21: treasury £2,468,261.20, C5->1.00, C7->1.00, VaR (current £1,007.23 / stressed £402.14) ratio 2.50
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.69
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-20.46

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £4,199.77
  - By billing account: C1 £1,834.46, C2 £3,845.47, C3 £3,730.10, C4 £3,723.31, C5 £4,493.22, C6 £8,284.77, C7 £3,212.01, C8 £4,623.29, C9 £4,051.31
- Bill shock events (>=20%): 54 -- C1g 2017-04-30 (29%); C1g 2017-06-30 (25%); C1g 2017-10-31 (43%); C1g 2017-11-30 (47%); C1g 2017-12-31 (21%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-04-30 (22%); C2g 2017-05-31 (23%); C2g 2017-06-30 (31%); C2g 2017-09-30 (21%); C2g 2017-10-31 (55%); C2g 2017-11-30 (58%); C2g 2017-12-31 (23%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-04-30 (32%); C3g 2017-05-31 (23%); C3g 2017-06-30 (31%); C3g 2017-09-30 (21%); C3g 2017-10-31 (56%); C3g 2017-11-30 (58%); C3g 2017-12-31 (23%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (28%); C4 2017-09-30 (21%); C4 2017-10-31 (26%); C4 2017-11-30 (26%); C4g 2017-04-30 (34%); C4g 2017-05-31 (25%); C4g 2017-06-30 (34%); C4g 2017-09-30 (24%); C4g 2017-10-31 (48%); C4g 2017-11-30 (61%); C4g 2017-12-31 (23%)
- Churn risk (accounts renewing in 2017): 9 at risk (≥20% churn prob): C1 35%, C2 26%, C3 29%, C4 29%, C5 32%, C6 35%, C7 38%, C8 35%, C9 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.80-£131.90/MWh, net margin £119.80
- C1g (gas): tariff £26.25-£33.50/MWh, net margin £105.08
- C2 (electricity): tariff £107.62-£125.78/MWh, net margin £96.41
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £205.85
- C3 (electricity): tariff £98.21-£120.31/MWh, net margin £69.04
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £54.33
- C4 (electricity): tariff £98.43-£110.09/MWh, net margin £46.11
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £130.41
- C5 (electricity): tariff £119.60-£131.05/MWh, net margin £163.51
- C6 (electricity): tariff £107.62-£126.27/MWh, net margin £57.06
- C7 (electricity): tariff £96.41-£195.90/MWh, net margin £158.44
- C8 (electricity): tariff £84.56-£190.21/MWh, net margin £209.26
- C9 (electricity): tariff £77.16-£180.79/MWh, net margin £132.35
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £29,240.89

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.855, average bill shock 16.8%, bad debt provision £1,368.85, avg complaint probability 4.4%
- Solvency signal: £249,793/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,288.76 vs. naked (unhedged) net margin: £113,066.92
- hedging cost £82,778.17 vs. a fully unhedged book (commodity-only: actual net £30,288.76 vs. naked net £113,066.92)
  - C1: actual £14.91 vs. naked £330.35 -- hedging cost £315.44
  - C1g: actual £129.99 vs. naked £235.90 -- hedging cost £105.91
  - C2: actual £103.89 vs. naked £438.17 -- hedging cost £334.29
  - C2g: actual £231.83 vs. naked £555.53 -- hedging cost £323.70
  - C3: actual £110.44 vs. naked £513.32 -- hedging cost £402.87
  - C3g: actual £24.21 vs. naked £509.77 -- hedging cost £485.57
  - C4: actual £41.09 vs. naked £275.30 -- hedging cost £234.20
  - C4g: actual £49.52 vs. naked £588.76 -- hedging cost £539.24
  - C5: actual £-204.77 vs. naked £1,068.93 -- hedging cost £1,273.70
  - C6: actual £102.39 vs. naked £1,675.49 -- hedging cost £1,573.11
  - C7: actual £-50.33 vs. naked £820.29 -- hedging cost £870.62
  - C8: actual £253.51 vs. naked £990.17 -- hedging cost £736.66
  - C9: actual £241.18 vs. naked £951.79 -- hedging cost £710.61
  - C_IC1: actual £29,240.89 vs. naked £104,113.14 -- hedging cost £74,872.25

**Year narrative:** 2017 produced a net gain of £30,788.53 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 54 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £99,664.21 (gross £263,547.62, capital £1,535.35)
  - Electricity: gross £262,087.75, capital £1,514.48, net £99,280.66
  - Gas: gross £1,459.87, capital £20.87, net £383.55
- Treasury at year end: £2,486,500.90
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.92 (avg 0.92), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2018-03-01 period 27, net margin £-15.12

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £101,666.70
  - By billing account: C1 £2,007.61, C2 £3,593.76, C3 £3,400.64, C4 £2,778.65, C5 £4,087.54, C6 £6,910.42, C7 £3,080.36, C8 £3,962.14, C9 £3,704.97, C_IC1 £983,140.96
- Bill shock events (>=20%): 62 -- C1g 2018-01-31 (28%); C1g 2018-04-30 (30%); C1g 2018-06-30 (27%); C1g 2018-10-31 (46%); C1g 2018-11-30 (50%); C1g 2018-12-31 (21%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (38%); C2g 2018-05-31 (22%); C2g 2018-06-30 (30%); C2g 2018-10-31 (54%); C2g 2018-11-30 (57%); C2g 2018-12-31 (22%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (32%); C3g 2018-05-31 (23%); C3g 2018-06-30 (31%); C3g 2018-09-30 (22%); C3g 2018-10-31 (57%); C3g 2018-11-30 (59%); C3g 2018-12-31 (23%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (28%); C4 2018-09-30 (23%); C4 2018-10-31 (41%); C4 2018-11-30 (28%); C4g 2018-04-30 (33%); C4g 2018-05-31 (24%); C4g 2018-06-30 (33%); C4g 2018-09-30 (23%); C4g 2018-10-31 (101%); C4g 2018-11-30 (63%); C4g 2018-12-31 (24%); C_IC1 2018-01-31 (21%); C_IC1 2018-02-28 (59%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 9 at risk (≥20% churn prob): C1 35%, C2 35%, C3 35%, C4 35%, C5 35%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £117.80-£149.70/MWh, net margin £15.22
- C1g (gas): tariff £33.50-£36.07/MWh, net margin £129.91
- C2 (electricity): tariff £125.78-£143.66/MWh, net margin £75.59
- C2g (gas): tariff £32.81-£36.82/MWh, net margin £187.38
- C3 (electricity): tariff £120.31-£126.99/MWh, net margin £69.22
- C3g (gas): tariff £23.11-£28.79/MWh, net margin £19.57
- C4 (electricity): tariff £110.09-£149.42/MWh, net margin £62.03
- C4g (gas): tariff £26.10-£33.60/MWh, net margin £46.69
- C5 (electricity): tariff £119.60-£153.44/MWh, net margin £-203.78 -- **net-negative**
- C6 (electricity): tariff £126.27-£141.97/MWh, net margin £-52.25 -- **net-negative**
- C7 (electricity): tariff £96.41-£221.33/MWh, net margin £-47.99 -- **net-negative**
- C8 (electricity): tariff £99.63-£200.82/MWh, net margin £124.90
- C9 (electricity): tariff £94.70-£198.49/MWh, net margin £202.74
- C_IC1 (electricity): tariff £-82.12-£228.10/MWh, net margin £105,765.89
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,730.90 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.843, average bill shock 16.7%, bad debt provision £2,393.86, avg complaint probability 4.5%
- Solvency signal: £226,046/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £109,716.96 vs. naked (unhedged) net margin: £247,516.49
- hedging cost £137,799.53 vs. a fully unhedged book (commodity-only: actual net £109,716.96 vs. naked net £247,516.49)
  - C1: actual £93.50 vs. naked £560.99 -- hedging cost £467.49
  - C1g: actual £137.34 vs. naked £341.62 -- hedging cost £204.27
  - C2: actual £60.72 vs. naked £497.94 -- hedging cost £437.23
  - C2g: actual £166.62 vs. naked £437.79 -- hedging cost £271.16
  - C3: actual £26.57 vs. naked £558.48 -- hedging cost £531.91
  - C3g: actual £33.09 vs. naked £637.87 -- hedging cost £604.78
  - C4: actual £103.91 vs. naked £464.83 -- hedging cost £360.92
  - C4g: actual £72.66 vs. naked £1,068.02 -- hedging cost £995.36
  - C5: actual £120.35 vs. naked £1,982.61 -- hedging cost £1,862.26
  - C6: actual £-149.11 vs. naked £1,828.64 -- hedging cost £1,977.75
  - C7: actual £70.63 vs. naked £1,348.15 -- hedging cost £1,277.52
  - C8: actual £23.86 vs. naked £937.49 -- hedging cost £913.63
  - C9: actual £143.45 vs. naked £1,046.92 -- hedging cost £903.47
  - C_IC1: actual £115,544.27 vs. naked £202,229.21 -- hedging cost £86,684.94
  - C_IC2: actual £-6,730.90 vs. naked £33,575.93 -- hedging cost £40,306.83

**Year narrative:** 2018 produced a net gain of £99,664.21 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 62 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £218,117.41 (gross £702,721.15, capital £11,523.01)
  - Electricity: gross £626,538.71, capital £2,298.68, net £217,552.61
  - Gas: gross £76,182.44, capital £9,224.32, net £564.81
- Treasury at year end: £2,606,332.68
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
- Average CLV (Point-in-Time, year-end 2019): £133,200.21
  - By billing account: C1 £1,991.57, C2 £3,006.07, C3 £3,386.89, C4 £2,989.84, C5 £4,369.12, C6 £7,512.22, C7 £3,254.24, C8 £3,878.29, C9 £3,803.94, C_IC1 £890,818.67, C_IC2 £540,191.42
- Bill shock events (>=20%): 63 -- C1 2019-04-30 (21%); C1g 2019-04-30 (30%); C1g 2019-06-30 (27%); C1g 2019-10-31 (46%); C1g 2019-11-30 (50%); C1g 2019-12-31 (20%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-04-30 (36%); C2g 2019-05-31 (22%); C2g 2019-06-30 (30%); C2g 2019-10-31 (53%); C2g 2019-11-30 (56%); C2g 2019-12-31 (22%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-04-30 (33%); C3g 2019-05-31 (24%); C3g 2019-06-30 (32%); C3g 2019-09-30 (21%); C3g 2019-10-31 (56%); C3g 2019-11-30 (58%); C3g 2019-12-31 (23%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (31%); C4 2019-09-30 (25%); C4 2019-11-30 (26%); C4g 2019-04-30 (34%); C4g 2019-05-31 (25%); C4g 2019-06-30 (35%); C4g 2019-09-30 (25%); C4g 2019-10-31 (26%); C4g 2019-11-30 (61%); C4g 2019-12-31 (23%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (126%); C_IC2 2019-02-28 (67%)
- Churn risk (accounts renewing in 2019): 10 at risk (≥20% churn prob): C1 35%, C2 35%, C3 35%, C4 35%, C5 38%, C6 29%, C7 35%, C8 38%, C9 32%, C_IC1 23%

**Pricing & Margin**

- C1 (electricity): tariff £125.86-£149.70/MWh, net margin £93.40
- C1g (gas): tariff £25.71-£36.07/MWh, net margin £137.53
- C2 (electricity): tariff £143.66-£151.82/MWh, net margin £126.22
- C2g (gas): tariff £26.00-£36.82/MWh, net margin £128.64
- C3 (electricity): tariff £120.68-£126.99/MWh, net margin £25.35
- C3g (gas): tariff £23.19-£28.79/MWh, net margin £88.99
- C4 (electricity): tariff £126.81-£149.42/MWh, net margin £101.47
- C4g (gas): tariff £19.67-£33.60/MWh, net margin £86.10
- C5 (electricity): tariff £126.12-£153.44/MWh, net margin £119.54
- C6 (electricity): tariff £141.97-£148.64/MWh, net margin £87.27
- C7 (electricity): tariff £99.71-£221.33/MWh, net margin £70.45
- C8 (electricity): tariff £105.19-£211.40/MWh, net margin £153.86
- C9 (electricity): tariff £98.85-£198.49/MWh, net margin £145.04
- C_IC1 (electricity): tariff £0.00-£263.30/MWh, net margin £137,283.29
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £78,379.15
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £967.56
- C_IC3g (gas): tariff £27.53/MWh, net margin £123.56

**Portfolio Health**

- Capital cost ratio: 1.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.855, average bill shock 16.8%, bad debt provision £6,227.25, avg complaint probability 4.4%
- Solvency signal: £217,194/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £242,718.86 vs. naked (unhedged) net margin: £826,408.39
- hedging cost £583,689.53 vs. a fully unhedged book (commodity-only: actual net £242,718.86 vs. naked net £826,408.39)
  - C1: actual £75.12 vs. naked £487.51 -- hedging cost £412.40
  - C1g: actual £141.19 vs. naked £299.59 -- hedging cost £158.40
  - C2: actual £156.30 vs. naked £662.65 -- hedging cost £506.35
  - C2g: actual £98.09 vs. naked £496.94 -- hedging cost £398.86
  - C3: actual £34.68 vs. naked £668.37 -- hedging cost £633.69
  - C3g: actual £156.38 vs. naked £674.58 -- hedging cost £518.21
  - C4: actual £104.03 vs. naked £443.84 -- hedging cost £339.81
  - C4g: actual £114.39 vs. naked £768.13 -- hedging cost £653.74
  - C5: actual £-28.64 vs. naked £1,590.33 -- hedging cost £1,618.97
  - C6: actual £229.16 vs. naked £2,597.69 -- hedging cost £2,368.54
  - C7: actual £56.23 vs. naked £1,146.80 -- hedging cost £1,090.57
  - C8: actual £239.62 vs. naked £1,370.72 -- hedging cost £1,131.10
  - C9: actual £158.99 vs. naked £1,258.98 -- hedging cost £1,099.99
  - C_IC1: actual £154,404.57 vs. naked £295,556.55 -- hedging cost £141,151.98
  - C_IC2: actual £85,687.64 vs. naked £161,893.37 -- hedging cost £76,205.72
  - C_IC3: actual £967.56 vs. naked £290,302.78 -- hedging cost £289,335.22
  - C_IC3g: actual £123.56 vs. naked £66,189.55 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £218,117.41 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 63 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £116,838.09 (gross £793,301.68, capital £7,351.38)
  - Electricity: gross £715,901.88, capital £1,963.07, net £112,332.85
  - Gas: gross £77,399.81, capital £5,388.31, net £4,505.24
- Treasury at year end: £2,899,743.74
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.86 (avg 0.86), C7 0.89 (avg 0.89), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2020-12-31 period 1, net margin £-484.21

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2020): £205,512.65
  - By billing account: C1 £2,287.96, C2 £3,238.37, C3 £3,174.03, C4 £3,151.22, C5 £4,837.87, C6 £8,240.46, C7 £3,792.02, C8 £4,115.73, C9 £3,732.10, C_IC1 £638,472.46, C_IC2 £308,644.99, C_IC3 £1,024,824.72, C_IC4 £663,152.56
- Bill shock events (>=20%): 57 -- C1g 2020-04-30 (29%); C1g 2020-06-30 (25%); C1g 2020-10-31 (43%); C1g 2020-11-30 (47%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-03-31 (21%); C2g 2020-04-30 (35%); C2g 2020-05-31 (22%); C2g 2020-06-30 (29%); C2g 2020-10-31 (51%); C2g 2020-11-30 (55%); C2g 2020-12-31 (22%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-03-31 (21%); C3g 2020-04-30 (32%); C3g 2020-05-31 (23%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (22%); C4 2020-11-30 (24%); C4g 2020-03-31 (22%); C4g 2020-04-30 (33%); C4g 2020-05-31 (24%); C4g 2020-06-30 (33%); C4g 2020-09-30 (23%); C4g 2020-10-31 (42%); C4g 2020-11-30 (60%); C4g 2020-12-31 (23%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (117%)
- Churn risk (accounts renewing in 2020): 10 at risk (≥20% churn prob): C1 32%, C2 35%, C3 35%, C4 35%, C5 35%, C6 32%, C7 35%, C8 38%, C9 41%, C_IC2 20%

**Pricing & Margin**

- C1 (electricity): tariff £125.86-£132.45/MWh, net margin £74.76
- C1g (gas): tariff £25.00-£25.71/MWh, net margin £141.23
- C2 (electricity): tariff £143.89-£151.82/MWh, net margin £182.39
- C2g (gas): tariff £21.75-£26.00/MWh, net margin £146.10
- C3 (electricity): tariff £120.68/MWh, net margin £16.15
- C3g (gas): tariff £23.19/MWh, net margin £87.85
- C4 (electricity): tariff £122.49-£126.81/MWh, net margin £87.10
- C4g (gas): tariff £16.09-£19.67/MWh, net margin £72.79
- C5 (electricity): tariff £126.12-£135.86/MWh, net margin £-31.68 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.64/MWh, net margin £363.65
- C7 (electricity): tariff £99.71-£211.45/MWh, net margin £57.43
- C8 (electricity): tariff £110.26-£211.40/MWh, net margin £337.79
- C9 (electricity): tariff £85.34-£188.71/MWh, net margin £116.91
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £52,095.27
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £43,671.83
- C_IC3 (electricity): tariff £37.50-£80.68/MWh, net margin £10,781.97
- C_IC3g (gas): tariff £15.44-£20.19/MWh, net margin £4,057.27
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £4,579.29

**Portfolio Health**

- Capital cost ratio: 0.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.858, average bill shock 15.0%, bad debt provision £6,317.23, avg complaint probability 4.2%
- Solvency signal: £223,057/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £73,759.84 vs. naked (unhedged) net margin: £934,426.68
- hedging cost £860,666.83 vs. a fully unhedged book (commodity-only: actual net £73,759.84 vs. naked net £934,426.68)
  - C1: actual £-19.25 vs. naked £97.58 -- hedging cost £116.84
  - C1g: actual £30.51 vs. naked £-140.93 -- hedging added £171.44
  - C2: actual £175.00 vs. naked £570.63 -- hedging cost £395.63
  - C2g: actual £160.82 vs. naked £426.75 -- hedging cost £265.93
  - C4: actual £24.76 vs. naked £235.48 -- hedging cost £210.72
  - C4g: actual £-95.91 vs. naked £220.97 -- hedging cost £316.88
  - C5: actual £-340.93 vs. naked £173.65 -- hedging cost £514.59
  - C6: actual £354.17 vs. naked £2,175.31 -- hedging cost £1,821.14
  - C7: actual £-123.70 vs. naked £315.88 -- hedging cost £439.58
  - C8: actual £341.14 vs. naked £1,170.39 -- hedging cost £829.25
  - C9: actual £-19.06 vs. naked £697.83 -- hedging cost £716.88
  - C_IC1: actual £33,272.84 vs. naked £127,359.13 -- hedging cost £94,086.29
  - C_IC2: actual £42,586.23 vs. naked £95,580.40 -- hedging cost £52,994.17
  - C_IC3: actual £-16,926.84 vs. naked £217,042.74 -- hedging cost £233,969.58
  - C_IC3g: actual £6,419.86 vs. naked £147,730.42 -- hedging cost £141,310.56
  - C_IC4: actual £7,920.21 vs. naked £340,770.45 -- hedging cost £332,850.24

**Year narrative:** 2020 produced a net gain of £116,838.09 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 57 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £58,203.88 (gross £772,566.38, capital £15,875.65)
  - Electricity: gross £689,802.09, capital £5,649.33, net £60,168.89
  - Gas: gross £82,764.30, capital £10,226.32, net £-1,965.02
- Treasury at year end: £2,921,202.27
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
- Average CLV (Point-in-Time, year-end 2021): £198,660.65
  - By billing account: C1 £2,105.76, C2 £3,477.85, C3 £3,018.74, C4 £2,809.06, C5 £4,948.83, C6 £8,571.73, C7 £3,382.53, C8 £4,338.89, C9 £3,485.40, C_IC1 £581,668.67, C_IC2 £327,641.63, C_IC3 £999,008.37, C_IC4 £638,131.04
- Bill shock events (>=20%): 55 -- C1g 2021-04-30 (28%); C1g 2021-06-30 (24%); C1g 2021-10-31 (41%); C1g 2021-11-30 (46%); C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (21%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C2g 2021-04-30 (25%); C2g 2021-05-31 (22%); C2g 2021-06-30 (30%); C2g 2021-10-31 (53%); C2g 2021-11-30 (56%); C2g 2021-12-31 (22%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (23%); C4 2021-10-31 (48%); C4 2021-11-30 (31%); C4g 2021-04-30 (33%); C4g 2021-05-31 (24%); C4g 2021-06-30 (32%); C4g 2021-09-30 (23%); C4g 2021-10-31 (76%); C4g 2021-11-30 (61%); C4g 2021-12-31 (23%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (24%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (22%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%)
- Churn risk (accounts renewing in 2021): 12 at risk (≥20% churn prob): C1 32%, C2 35%, C4 35%, C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC3 20%, C_IC4 29%

**Pricing & Margin**

- C1 (electricity): tariff £132.45/MWh, net margin £-18.96 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £30.19
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £156.73
- C2g (gas): tariff £21.75-£35.00/MWh, net margin £95.70
- C4 (electricity): tariff £122.49-£183.00/MWh, net margin £-59.79 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-400.43 -- **net-negative**
- C5 (electricity): tariff £135.86/MWh, net margin £-337.14 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.14/MWh, net margin £523.64
- C7 (electricity): tariff £110.76-£274.50/MWh, net margin £-133.33 -- **net-negative**
- C8 (electricity): tariff £110.26-£274.50/MWh, net margin £340.17
- C9 (electricity): tariff £85.34-£264.35/MWh, net margin £-14.76 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £27,562.51
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £56,614.30
- C_IC3 (electricity): tariff £42.26-£391.18/MWh, net margin £-27,813.55 -- **net-negative**
- C_IC3g (gas): tariff £20.19-£123.98/MWh, net margin £-1,690.48 -- **net-negative**
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £3,349.06

**Portfolio Health**

- Capital cost ratio: 2.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.854, average bill shock 15.7%, bad debt provision £9,218.53, avg complaint probability 4.3%
- Solvency signal: £243,434/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £143,914.22 vs. naked (unhedged) net margin: £349,267.67
- hedging cost £205,353.45 vs. a fully unhedged book (commodity-only: actual net £143,914.22 vs. naked net £349,267.67)
  - C2: actual £135.95 vs. naked £124.53 -- hedging added £11.42
  - C2g: actual £30.93 vs. naked £-158.95 -- hedging added £189.88
  - C4: actual £-221.67 vs. naked £-170.72 -- hedging cost £50.96
  - C4g: actual £-982.92 vs. naked £-1,248.65 -- hedging added £265.73
  - C6: actual £510.16 vs. naked £267.67 -- hedging added £242.49
  - C7: actual £-1,835.40 vs. naked £-870.69 -- hedging cost £964.72
  - C8: actual £283.50 vs. naked £107.31 -- hedging added £176.20
  - C9: actual £-50.97 vs. naked £-185.27 -- hedging added £134.30
  - C_IC1: actual £28,618.96 vs. naked £-64,757.08 -- hedging added £93,376.04
  - C_IC2: actual £65,351.25 vs. naked £21,149.05 -- hedging added £44,202.21
  - C_IC3: actual £102,817.34 vs. naked £238,045.53 -- hedging cost £135,228.18
  - C_IC3g: actual £-48,818.20 vs. naked £32,238.32 -- hedging cost £81,056.52
  - C_IC4: actual £-1,924.70 vs. naked £124,726.63 -- hedging cost £126,651.33

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £58,203.88 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 55 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £256,102.05 (gross £1,061,934.61, capital £65,233.89)
  - Electricity: gross £971,675.75, capital £13,330.44, net £305,299.96
  - Gas: gross £90,258.85, capital £51,903.45, net £-49,197.91
- Treasury at year end: £3,069,116.48
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,019,944.35, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,741.95 / stressed £20,653.32) ratio 2.70
  - 2022-05-29: treasury £3,020,061.43, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,851.93 / stressed £20,682.56) ratio 2.70
  - 2022-06-28: treasury £3,020,056.07, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,851.93 / stressed £20,682.56) ratio 2.70
  - 2022-07-28: treasury £3,019,862.34, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,913.47 / stressed £20,694.82) ratio 2.70
  - 2022-08-27: treasury £3,019,852.67, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,913.47 / stressed £20,694.82) ratio 2.70
  - 2022-09-26: treasury £3,019,837.13, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,913.47 / stressed £20,694.82) ratio 2.70
  - 2022-10-26: treasury £3,017,465.22, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,975.68 / stressed £20,705.30) ratio 2.70
  - 2022-11-25: treasury £3,017,314.34, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,975.68 / stressed £20,705.30) ratio 2.70
  - 2022-12-25: treasury £3,017,047.34, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,975.68 / stressed £20,705.30) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC3g on 2022-12-31 period 1, net margin £-2,969.97

**Customer Book**

- Active accounts: 14 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £200,396.30
  - By billing account: C1 £2,221.79, C2 £2,850.49, C2_2 £489.86, C3 £3,096.38, C4 £1,737.71, C5 £4,855.61, C6 £8,314.16, C7 £2,802.43, C8 £3,939.70, C9 £3,932.31, C_IC1 £642,644.36, C_IC2 £368,678.13, C_IC3 £1,152,376.47, C_IC4 £607,608.83
- Bill shock events (>=20%): 59 -- C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-03-30 (21%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-04-30 (33%); C4g 2022-05-31 (24%); C4g 2022-06-30 (33%); C4g 2022-09-30 (28%); C4g 2022-10-31 (228%); C4g 2022-11-30 (67%); C4g 2022-12-31 (24%); C_IC1 2022-06-30 (77%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (109%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (35%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (69%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 9 at risk (≥20% churn prob): C2 32%, C4 35%, C6 32%, C7 35%, C8 35%, C9 38%, C_IC1 20%, C_IC3 23%, C_IC4 32%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £12.87
- C2_2 (electricity): tariff £361.95/MWh, net margin £25.73
- C2g (gas): tariff £35.00/MWh, net margin £-21.81 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-278.63 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,440.99 -- **net-negative**
- C6 (electricity): tariff £197.14-£407.01/MWh, net margin £815.52
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,831.75 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-193.33 -- **net-negative**
- C9 (electricity): tariff £138.47-£389.66/MWh, net margin £-119.52 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£461.28/MWh, net margin £132,930.45
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £74,097.43
- C_IC3 (electricity): tariff £137.39-£391.18/MWh, net margin £101,770.63
- C_IC3g (gas): tariff £120.28-£123.98/MWh, net margin £-47,735.11 -- **net-negative**
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £-1,929.46 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 6.1% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,373,987.39 -> £3,017,016.31 (10.6%)
- Bills issued: 148, average clarity 0.805, average bill shock 34.0%, bad debt provision £35,912.94, avg complaint probability 5.4%
- Solvency signal: £279,011/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £103,454.07 vs. naked (unhedged) net margin: £1,092,401.50
- hedging cost £988,947.44 vs. a fully unhedged book (commodity-only: actual net £103,454.07 vs. naked net £1,092,401.50)
  - C2_2: actual £25.26 vs. naked £1,644.79 -- hedging cost £1,619.53
  - C4: actual £-279.60 vs. naked £595.02 -- hedging cost £874.62
  - C4g: actual £-2,138.05 vs. naked £1,645.91 -- hedging cost £3,783.96
  - C6: actual £1,120.01 vs. naked £3,996.95 -- hedging cost £2,876.94
  - C7: actual £-351.18 vs. naked £2,280.97 -- hedging cost £2,632.14
  - C8: actual £-353.94 vs. naked £1,101.73 -- hedging cost £1,455.67
  - C9: actual £-52.31 vs. naked £1,012.47 -- hedging cost £1,064.78
  - C_IC1: actual £215,541.99 vs. naked £253,734.37 -- hedging cost £38,192.38
  - C_IC2: actual £88,563.36 vs. naked £128,333.78 -- hedging cost £39,770.43
  - C_IC3: actual £-171,865.89 vs. naked £446,676.32 -- hedging cost £618,542.21
  - C_IC3g: actual £-30,262.44 vs. naked £84,525.03 -- hedging cost £114,787.47
  - C_IC4: actual £3,506.84 vs. naked £166,854.16 -- hedging cost £163,347.31

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £256,102.05 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 59 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £50,721.34 (gross £919,750.96, capital £49,186.57)
  - Electricity: gross £798,725.64, capital £9,840.92, net £82,658.60
  - Gas: gross £121,025.31, capital £39,345.65, net £-31,937.27
- Treasury at year end: £3,173,050.84
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,069,115.62, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,462.76 / stressed £44,376.48) ratio 2.76
  - 2023-02-23: treasury £3,069,115.35, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,462.76 / stressed £44,376.48) ratio 2.76
  - 2023-03-25: treasury £3,069,115.01, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,462.76 / stressed £44,376.48) ratio 2.76
  - 2023-04-24: treasury £3,150,535.85, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £129,699.09 / stressed £49,443.60) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-12-31 period 1, net margin £-3,474.99

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £201,948.91
  - By billing account: C1 £2,215.68, C2 £2,843.06, C2_2 £1,365.51, C3 £3,088.62, C4 £1,389.34, C5 £4,846.81, C6 £9,087.53, C7 £2,990.54, C8 £4,007.67, C9 £4,202.25, C_IC1 £694,431.39, C_IC2 £396,111.17, C_IC3 £1,073,297.77, C_IC4 £627,407.36
- Bill shock events (>=20%): 46 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (31%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (25%); C4 2023-04-30 (29%); C4 2023-09-30 (24%); C4 2023-11-30 (27%); C4g 2023-03-31 (20%); C4g 2023-04-30 (35%); C4g 2023-05-31 (27%); C4g 2023-06-30 (37%); C4g 2023-09-30 (28%); C4g 2023-10-31 (43%); C4g 2023-11-30 (66%); C4g 2023-12-31 (24%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (59%); C_IC2 2023-05-31 (52%); C_IC2 2023-06-30 (100%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (36%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%)
- Churn risk (accounts renewing in 2023): 8 at risk (≥20% churn prob): C2_2 38%, C4 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC3 23%, C_IC4 29%

**Pricing & Margin**

- C2_2 (electricity): tariff £350.91-£361.95/MWh, net margin £505.55
- C4 (electricity): tariff £249.73-£305.00/MWh, net margin £-69.85 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,169.81 -- **net-negative**
- C6 (electricity): tariff £333.52-£407.01/MWh, net margin £1,263.87
- C7 (electricity): tariff £187.67-£457.50/MWh, net margin £-349.77 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-25.36 -- **net-negative**
- C9 (electricity): tariff £192.60-£389.66/MWh, net margin £223.61
- C_IC1 (electricity): tariff £-60.00-£461.28/MWh, net margin £162,378.95
- C_IC2 (electricity): tariff £-186.24-£475.19/MWh, net margin £85,991.73
- C_IC3 (electricity): tariff £100.62-£262.29/MWh, net margin £-170,774.31 -- **net-negative**
- C_IC3g (gas): tariff £61.01-£120.28/MWh, net margin £-30,767.46 -- **net-negative**
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £3,514.18

**Portfolio Health**

- Capital cost ratio: 5.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,564,852.12 -> £3,173,047.48 (11.0%)
- Bills issued: 144, average clarity 0.818, average bill shock 17.6%, bad debt provision £13,861.65, avg complaint probability 4.8%
- Solvency signal: £317,305/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £362,667.01 vs. naked (unhedged) net margin: £1,160,424.75
- hedging cost £797,757.73 vs. a fully unhedged book (commodity-only: actual net £362,667.01 vs. naked net £1,160,424.75)
  - C2_2: actual £834.30 vs. naked £2,428.93 -- hedging cost £1,594.62
  - C4: actual £314.70 vs. naked £701.32 -- hedging cost £386.62
  - C4g: actual £664.66 vs. naked £1,582.68 -- hedging cost £918.02
  - C6: actual £1,410.50 vs. naked £5,083.86 -- hedging cost £3,673.36
  - C7: actual £475.75 vs. naked £1,923.14 -- hedging cost £1,447.39
  - C8: actual £209.11 vs. naked £1,971.27 -- hedging cost £1,762.16
  - C9: actual £624.29 vs. naked £2,129.55 -- hedging cost £1,505.25
  - C_IC1: actual £142,874.19 vs. naked £286,611.25 -- hedging cost £143,737.07
  - C_IC2: actual £95,075.48 vs. naked £163,554.13 -- hedging cost £68,478.66
  - C_IC3: actual £153,299.31 vs. naked £428,881.03 -- hedging cost £275,581.72
  - C_IC3g: actual £-36,843.35 vs. naked £77,603.64 -- hedging cost £114,446.99
  - C_IC4: actual £3,728.07 vs. naked £187,953.96 -- hedging cost £184,225.88

**Year narrative:** 2023 produced a net gain of £50,721.34 across 12 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 46 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £319,131.05 (gross £1,294,741.59, capital £55,660.46)
  - Electricity: gross £1,170,158.86, capital £9,752.79, net £355,851.91
  - Gas: gross £124,582.74, capital £45,907.67, net £-36,720.86
- Treasury at year end: £3,535,301.50
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
- Average CLV (Point-in-Time, year-end 2024): £227,679.39
  - By billing account: C1 £2,129.42, C2 £3,011.83, C2_2 £1,980.54, C3 £3,165.16, C4 £1,860.01, C5 £4,779.97, C6 £8,862.50, C7 £3,258.96, C8 £4,316.77, C9 £4,696.18, C_IC1 £719,251.10, C_IC2 £418,284.31, C_IC3 £1,286,872.53, C_IC4 £725,042.13
- Bill shock events (>=20%): 33 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (30%); C4g 2024-03-31 (23%); C4g 2024-04-30 (35%); C4g 2024-05-31 (26%); C4g 2024-06-30 (36%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (58%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (54%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C4 35%, C6 38%, C7 35%, C8 41%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.08-£350.91/MWh, net margin £417.96
- C4 (electricity): tariff £249.73/MWh, net margin £235.68
- C4g (gas): tariff £66.00/MWh, net margin £478.71
- C6 (electricity): tariff £333.52/MWh, net margin £491.76
- C7 (electricity): tariff £165.00-£358.28/MWh, net margin £475.31
- C8 (electricity): tariff £161.69-£397.50/MWh, net margin £331.78
- C9 (electricity): tariff £165.00-£367.70/MWh, net margin £558.67
- C_IC1 (electricity): tariff £-98.58-£329.97/MWh, net margin £125,985.61
- C_IC2 (electricity): tariff £-106.92-£354.20/MWh, net margin £70,242.68
- C_IC3 (electricity): tariff £86.86-£192.10/MWh, net margin £153,376.40
- C_IC3g (gas): tariff £61.01-£61.67/MWh, net margin £-37,199.57 -- **net-negative**
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £3,736.07

**Portfolio Health**

- Capital cost ratio: 4.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,564,764.84 -> £3,173,050.87 (11.0%)
- Bills issued: 129, average clarity 0.826, average bill shock 15.5%, bad debt provision £11,555.52, avg complaint probability 4.5%
- Solvency signal: £353,530/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £174,539.12 vs. naked (unhedged) net margin: £552,803.85
- hedging cost £378,264.72 vs. a fully unhedged book (commodity-only: actual net £174,539.12 vs. naked net £552,803.85)
  - C2_2: actual £92.53 vs. naked £1,031.59 -- hedging cost £939.07
  - C7: actual £-13.51 vs. naked £653.48 -- hedging cost £666.99
  - C8: actual £341.37 vs. naked £1,419.60 -- hedging cost £1,078.23
  - C9: actual £371.56 vs. naked £1,427.21 -- hedging cost £1,055.66
  - C_IC1: actual £117,993.65 vs. naked £212,989.72 -- hedging cost £94,996.06
  - C_IC2: actual £62,169.17 vs. naked £113,430.19 -- hedging cost £51,261.03
  - C_IC3: actual £15,459.83 vs. naked £116,257.58 -- hedging cost £100,797.75
  - C_IC3g: actual £-23,330.60 vs. naked £29,765.97 -- hedging cost £53,096.57
  - C_IC4: actual £1,455.13 vs. naked £75,828.50 -- hedging cost £74,373.37

**Year narrative:** 2024 produced a net gain of £319,131.05 across 12 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £92,421.46 (gross £523,363.58, capital £28,940.00)
  - Electricity: gross £469,854.79, capital £5,653.08, net £111,920.86
  - Gas: gross £53,508.78, capital £23,286.91, net £-19,499.39
- Treasury at year end: £3,587,097.12
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
- Average CLV (Point-in-Time, year-end 2025): £245,131.80
  - By billing account: C1 £2,044.69, C2 £3,023.51, C2_2 £2,043.64, C3 £3,071.98, C4 £1,813.98, C5 £4,510.86, C6 £8,751.25, C7 £3,569.06, C8 £4,069.28, C9 £4,517.12, C_IC1 £767,123.67, C_IC2 £453,841.77, C_IC3 £1,389,002.31, C_IC4 £784,462.04
- Bill shock events (>=20%): 20 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (34%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.08-£283.45/MWh, net margin £86.63
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-10.34 -- **net-negative**
- C8 (electricity): tariff £149.29-£308.69/MWh, net margin £86.43
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £194.62
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £64,248.49
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £30,436.01
- C_IC3 (electricity): tariff £86.86-£165.83/MWh, net margin £15,442.62
- C_IC3g (gas): tariff £61.67/MWh, net margin £-19,499.39 -- **net-negative**
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £1,436.41

**Portfolio Health**

- Capital cost ratio: 5.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 54, average clarity 0.777, average bill shock 23.6%, bad debt provision £4,995.39, avg complaint probability 5.9%
- Solvency signal: £448,387/customer (8 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £56.81 vs. naked (unhedged) net margin: £336.86
- hedging cost £280.05 vs. a fully unhedged book (commodity-only: actual net £56.81 vs. naked net £336.86)
  - C2_2: actual £83.78 vs. naked £218.19 -- hedging cost £134.41
  - C8: actual £-26.97 vs. naked £118.67 -- hedging cost £145.64

**Year narrative:** 2025 produced a net gain of £92,421.46 across 9 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 20 customer(s) experienced a bill shock of >=20%.
