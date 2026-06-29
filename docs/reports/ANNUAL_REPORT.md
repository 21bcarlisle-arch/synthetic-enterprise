# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,794,936.89
  (£1,328,300.67 net change)
- Solvency signal (final year): £458,328/customer (8 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £20,026,948.72
  VAT remitted to HMRC: (£963,753.18) | Revenue (ex-VAT): £19,063,195.54
  Non-commodity pass-through: (£4,822,712.90)
- Gross margin: £6,563,216.58
- Capital costs: £237,036.13
- Net margin: £6,326,180.45
- Capital cost ratio: 3.6% of gross
- Net margin as % of revenue: 33.2%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1531, average clarity 0.841,
  service quality score 0.908
- Enterprise value (CLV sum across 14 billing accounts): £6,225,440.09
- Cost to serve (whole portfolio): £91,824.10, net margin after cost to serve: £6,234,356.35
- Hedge effectiveness (whole window): hedging cost £4,054,089.28 vs. a fully unhedged book (commodity-only: actual net £1,328,300.67 vs. naked net £5,382,389.95)

- **2021** (crisis year): net margin £66,350.48, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £276,049.47, 9 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,563,216.58, capital £237,036.13, net £6,326,180.45. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 3.6% (commodity basis, comparable to old model) / 3.6% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £66,350.48 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 33.2%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,326,180.45
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,382,389.95
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,054,089.28 vs. a fully unhedged book (commodity-only: actual net £1,328,300.67 vs. naked net £5,382,389.95)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £103,079.61 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £618,528.18 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £258.47 | £626.22 | £307.71 | £1,192.40 |
| 2017 | £29,240.89 | £0.00 | £222.56 | £832.56 | £495.67 | £30,791.68 |
| 2018 | £104,293.89 | £0.00 | £-257.76 | £570.92 | £383.55 | £104,990.60 |
| 2019 | £225,630.16 | £123.56 | £247.11 | £801.94 | £441.25 | £227,244.02 |
| 2020 | £120,385.37 | £4,057.27 | £325.40 | £884.83 | £447.97 | £126,100.83 |
| 2021 | £67,906.15 | £-1,690.48 | £233.13 | £259.51 | £-357.84 | £66,350.48 |
| 2022 | £327,195.45 | £-47,735.11 | £809.76 | £-2,389.98 | £-1,830.65 | £276,049.47 |
| 2023 | £90,733.23 | £-30,767.46 | £1,259.48 | £250.45 | £-1,474.39 | £60,001.32 |
| 2024 | £373,034.51 | £-37,199.57 | £491.06 | £2,050.97 | £574.05 | £338,951.03 |
| 2025 | £115,772.43 | £-19,499.39 | £0.00 | £355.81 | £0.00 | £96,628.85 |

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

- **Average absolute error:** 197.1%
- **Average signed error:** +51.4% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -81.4% | 81.4% |
| 2017 | 3 | -93.6% | 93.6% |
| 2018 | 4 | +404.4% | 495.6% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | +25.5% | 189.8% |
| 2021 | 9 | -7.9% | 119.1% |
| 2022 | 7 | -23.6% | 113.0% |
| 2023 | 7 | -13.3% | 122.6% |
| 2024 | 7 | +78.9% | 231.8% |
| 2025 | 2 | -94.4% | 94.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 34.6%, abs error 312.5%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.9%, abs error 146.8%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.2% | 0.0% | 81.4% |
| 2017 | 0 | 3 | 0.0% | 2.2% | 0.0% | 93.6% |
| 2018 | 2 | 2 | 19.3% | 50.0% | 48.3% | 942.8% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 16.6% | 0.6% | 281.4% | 98.3% |
| 2021 | 3 | 6 | 64.8% | 4.1% | 180.5% | 88.4% |
| 2022 | 0 | 7 | 0.0% | 19.5% | 0.0% | 113.0% |
| 2023 | 2 | 5 | 29.2% | 19.0% | 72.7% | 142.6% |
| 2024 | 3 | 4 | 39.9% | 0.0% | 407.5% | 100.0% |
| 2025 | 0 | 2 | 0.0% | 2.1% | 0.0% | 94.4% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 10 (26%)
- **Below/at SVT (protected):** 29 (74%)
- **Mean rate vs SVT premium:** -10.0%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.2 | 140.0 |
| 2017 | 3 | 0 (0%) | -13.5% | 121.0 | 140.0 |
| 2018 | 2 | 2 (100%) | +1.9% | 155.3 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.3% | 126.3 | 178.5 |
| 2020 | 5 | 0 (0%) | -25.7% | 131.4 | 176.9 |
| 2021 | 6 | 3 (50%) | +0.8% | 184.1 | 183.8 |
| 2022 | 7 | 4 (57%) | +11.5% | 294.4 | 318.4 |
| 2023 | 5 | 0 (0%) | -31.9% | 227.0 | 364.0 |
| 2024 | 4 | 0 (0%) | -16.3% | 205.5 | 246.9 |
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
| 2018 | 4 | 4.96× ⚠ | 18.00× |
| 2019 | 4 | 5.25× ⚠ | 18.00× |
| 2020 | 10 | 1.90× | 10.77× |
| 2021 | 9 | 1.19× | 3.75× |
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
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.79 |
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
| 2023 | 274,596 | 65,433 | 72,499 | 51,402 | 75,859 | 13,892 | 553,681 |  |
| 2024 | 310,646 | 111,036 | 73,612 | 69,371 | 83,378 | 2,019 | 650,062 |  |
| 2025 | 137,698 | 47,631 | 31,649 | 31,480 | 36,676 | 866 | 286,000 |  |
| **Total** | **1,739,920** | **265,478** | **462,816** | **339,720** | **471,540** | **159,280** | **3,438,755** | |

Total policy cost: £3,438,755 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2023 | 140,380 | RIIO-ED2 from Apr 2023 |
| 2024 | 144,397 |  |
| 2025 | 61,948 |  |
| **Total** | **887,783** | |

Total network cost: £887,783 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

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
| 2021 | 22,472 | 50,497 | 72,969 |
| 2022 | 27,045 | 54,554 | 81,599 |
| 2023 | 32,229 | 79,889 | 112,118 |
| 2024 | 37,495 | 76,598 | 114,093 |
| 2025 | 17,243 | 31,816 | 49,059 |
| **Total** | **171,107** | **393,811** | **564,918** |

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
| 2021 | 298,009 | 215,298 | 82,711 | 22,472 | 50,497 | 10,228 | -2,048 | -0.7% |
| 2022 | 588,992 | 498,984 | 90,008 | 27,045 | 54,554 | 51,911 | -49,566 | -8.4% |
| 2023 | 298,211 | 177,329 | 120,882 | 32,229 | 79,889 | 39,358 | -32,242 | -10.8% |
| 2024 | 271,154 | 146,368 | 124,786 | 37,495 | 76,598 | 45,913 | -36,626 | -13.5% |
| 2025 | 132,454 | 78,945 | 53,509 | 17,243 | 31,816 | 23,287 | -19,499 | -14.7% |
| **Total** | **1,856,306** | **1,226,874** | **629,432** | **171,107** | **393,811** | **185,353** | **-133,724** | **-7.2%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,418 | 9 | 274,158 | 2108.90× | OK |
| 2017 | 2,497,945 | 10 | 249,794 | 1921.50× | OK |
| 2018 | 2,486,550 | 11 | 226,050 | 1738.85× | OK |
| 2019 | 2,612,482 | 12 | 217,707 | 1674.67× | OK |
| 2020 | 2,918,514 | 13 | 224,501 | 1726.93× | OK |
| 2021 | 2,946,681 | 12 | 245,557 | 1888.90× | OK |
| 2022 | 3,115,333 | 11 | 283,212 | 2178.55× | OK |
| 2023 | 3,228,942 | 10 | 322,894 | 2483.80× | OK |
| 2024 | 3,611,718 | 10 | 361,172 | 2778.24× | OK |
| 2025 | 3,666,622 | 8 | 458,328 | 3525.60× | OK |

End-state (2025): **£458,328/account** across 8 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,418 | 81838.1× | OK |
| 2017 | 467 | 560 | 2,497,945 | 4460.9× | OK |
| 2018 | 853 | 1,024 | 2,486,550 | 2429.1× | OK |
| 2019 | 1,545 | 1,854 | 2,612,482 | 1409.4× | OK |
| 2020 | 1,981 | 2,378 | 2,918,514 | 1227.5× | OK |
| 2021 | 4,414 | 5,297 | 2,946,681 | 556.3× | OK |
| 2022 | 8,511 | 10,213 | 3,115,333 | 305.0× | OK |
| 2023 | 5,614 | 6,737 | 3,228,942 | 479.3× | OK |
| 2024 | 2,738 | 3,286 | 3,611,718 | 1099.2× | OK |
| 2025 | 4,192 | 5,031 | 3,666,622 | 728.8× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,518.17 | £12,258.38 | £262.58/MWh | £144.92/MWh | +2.9% |
| C8 | 106,722 | 43,948 | 41.2% | £11,995.13 | £9,709.74 | £272.94/MWh | £154.68/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,962.33 | £9,333.41 | £250.92/MWh | £142.07/MWh | +10.9% |

Total HH revenue: £63,777.16 vs flat equivalent £58,870.61 (+8.3% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 36 | 100% | C8 (2016-10-31) |
| 2017 | 54 | 81% | C8 (2017-11-30) |
| 2018 | 61 | 101% | C4g (2018-10-31) |
| 2019 | 63 | 129% | C_IC1 (2019-03-31) |
| 2020 | 57 | 120% | C_IC2 (2020-03-31) |
| 2021 | 55 | 111% | C4g (2021-10-31) |
| 2022 | 59 | 1735% | C2_2 (2022-04-30) |
| 2023 | 45 | 102% | C_IC2 (2023-06-30) |
| 2024 | 33 | 109% | C_IC2 (2024-07-31) |
| 2025 | 20 | 80% | C7 (2025-06-07) |

Total: **483** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1735% | no |
| 2022-10-31 | C4g | +237% | no |
| 2019-03-31 | C_IC1 | +129% | no |
| 2020-03-31 | C_IC2 | +120% | no |
| 2022-01-31 | C_IC3 | +111% | no |
| 2021-10-31 | C4g | +111% | no |
| 2024-07-31 | C_IC2 | +109% | no |
| 2023-06-30 | C_IC2 | +102% | no |
| 2018-10-31 | C4g | +101% | no |
| 2016-10-31 | C8 | +100% | no |

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
| 2021-12-31 | C_IC3g | £20.2 | £124.4 (+516%) | 95% |
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
| Total offer cost (foregone margin) | £428,499.64 |
| Margin saved (retained customers' terms) | £2,304,069.07 |
| Wasted offer cost (churned anyway) | £503.87 |
| **Net ROI of retention strategy** | **£1,875,569.42** |
| Acquisition cost avoided (retained customers) | £2,800.00 |
| **Full economic ROI (margin + acq savings)** | **£1,878,369.42** |

Missed opportunities (churns with no offer): **5** (£4,067.18 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 5 (£4,067.18 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24752.59 | £169433.85 | £144681.26 | £0.00 |
| 2019 | 2 | 2 | £43702.07 | £306529.83 | £262827.76 | £0.00 |
| 2020 | 3 | 3 | £27210.18 | £170637.75 | £143427.57 | £583.43 |
| 2021 | 4 | 3 | £122670.40 | £438628.54 | £315958.14 | £-178.13 |
| 2022 | 2 | 2 | £75225.50 | £338853.25 | £263627.75 | £236.63 |
| 2023 | 4 | 4 | £89824.07 | £463598.16 | £373774.10 | £0.00 |
| 2024 | 2 | 2 | £45114.83 | £416387.67 | £371272.84 | £3425.26 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24752.59 | £169433.85 | £150 | £144681.26 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £15172.47 | £105268.85 | £150 | £90096.38 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £28529.60 | £201260.98 | £150 | £172731.38 | retained |
| 2020-01-01 | C_IC3 | 0.36 | 3% | £5736.90 | £10938.40 | £150 | £5201.51 | retained |
| 2020-03-31 | C_IC1 | 0.52 | 5% | £10690.67 | £137077.64 | £150 | £126386.97 | retained |
| 2020-12-31 | C_IC3 | 0.59 | 5% | £10782.61 | £22621.71 | £150 | £11839.10 | retained |
| 2021-03-31 | C_IC2 | 0.84 | 8% | £14491.44 | £94917.42 | £150 | £80425.99 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £23110.77 | £164843.14 | £150 | £141732.36 | retained |
| 2021-12-30 | C5 | 0.79 | 8% | £503.87 | £2166.27 | £400 | £-503.87 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £84564.32 | £178867.99 | £150 | £94303.66 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25722.75 | £99883.30 | £150 | £74160.54 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £49502.74 | £238969.95 | £150 | £189467.21 | retained |
| 2023-03-31 | C6 | 0.49 | 3% | £230.71 | £3263.15 | £400 | £3032.44 | retained |
| 2023-05-30 | C_IC2 | 0.59 | 5% | £12019.77 | £135268.59 | £150 | £123248.82 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £35645.77 | £252369.69 | £150 | £216723.92 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £41927.82 | £72696.73 | £150 | £30768.92 | retained |
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

**Full-history EV:** £6,225,440.09 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £470,935.32 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,192.40 |
| 2017 | £30,791.68 |
| 2018 | £104,990.60 |
| 2019 | £227,244.02 |
| 2020 | £126,100.83 |
| 2021 | £66,350.48 |
| 2022 | £276,049.47 |
| 2023 | £60,001.32 | ← trailing
| 2024 | £338,951.03 | ← trailing
| 2025 | £96,628.85 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £3,666.24 | — |
| C2 | £5,142.30 | — |
| C2_2 | — | £964.46 |
| C3 | £5,244.41 | — |
| C4 | £3,113.71 | £-1,042.61 |
| C5 | £8,207.43 | — |
| C6 | £14,201.07 | £2,492.67 |
| C7 | £6,955.45 | £109.36 |
| C8 | £7,266.81 | £369.66 |
| C9 | £7,290.61 | £919.40 |
| C_IC1 | £1,489,837.82 | £348,262.88 |
| C_IC2 | £775,935.92 | £184,387.50 |
| C_IC3 | £2,589,910.48 | £-73,774.20 |
| C_IC4 | £1,305,283.36 | £8,246.19 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £1,727.79 | — | — | — | — | £4,331.69 | — | £3,079.50 | — | — | — | — | — | — |
| 2017 | £1,834.41 | £3,845.46 | — | £3,730.10 | £3,723.31 | £4,493.01 | £8,284.71 | £3,212.57 | £4,623.25 | £4,051.32 | — | — | — | — |
| 2018 | £2,007.61 | £3,590.32 | — | £3,398.36 | £2,777.42 | £4,087.58 | £6,907.45 | £3,121.21 | £3,995.23 | £3,728.81 | £999,382.60 | — | — | — |
| 2019 | £2,000.65 | £3,001.86 | — | £3,383.71 | £2,986.76 | £4,405.28 | £7,503.26 | £3,308.93 | £3,915.76 | £3,862.08 | £907,973.04 | £549,645.75 | — | — |
| 2020 | £2,246.18 | £3,651.12 | — | £2,878.91 | £3,120.67 | £5,536.08 | £7,495.41 | £3,324.51 | £4,603.11 | £3,979.79 | £617,472.14 | £310,265.28 | £1,141,184.33 | £631,175.08 |
| 2021 | £2,113.79 | £3,502.27 | — | £3,027.43 | £2,773.78 | £5,011.45 | £8,350.55 | £3,430.41 | £4,384.31 | £3,555.68 | £596,851.96 | £334,718.49 | £1,009,507.84 | £639,263.86 |
| 2022 | £2,234.69 | £2,855.29 | £491.19 | £3,099.47 | £1,566.81 | £4,917.25 | £8,318.22 | £2,844.71 | £3,966.66 | £3,979.32 | £661,430.67 | £378,474.08 | £1,165,020.11 | £608,064.90 |
| 2023 | £2,230.09 | £2,845.74 | £1,372.49 | £3,095.03 | £1,192.73 | £4,908.36 | £9,102.41 | £3,027.66 | £4,030.66 | £4,243.93 | £712,596.50 | £405,651.44 | £1,083,571.61 | £628,114.55 |
| 2024 | £2,124.50 | £2,945.42 | £1,990.07 | £3,136.04 | £1,775.72 | £4,922.58 | £8,781.71 | £3,172.18 | £4,257.52 | £4,662.32 | £738,341.63 | £434,495.40 | £1,359,490.91 | £742,650.17 |
| 2025 | £2,053.34 | £3,026.02 | £2,055.90 | £3,081.73 | £1,768.59 | £4,567.10 | £8,758.83 | £3,598.16 | £4,091.99 | £4,544.44 | £786,525.91 | £465,099.22 | £1,406,760.97 | £787,742.53 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,832.85, range £58.95–£26,597.64.

- C1: cost to serve £414.64, net margin after CTS £2,326.90
- C1g: cost to serve £58.95, net margin after CTS £1,369.99
- C2: cost to serve £432.10, net margin after CTS £2,968.67
- C2_2: cost to serve £381.26, net margin after CTS £5,089.47
- C2g: cost to serve £93.15, net margin after CTS £2,154.87
- C3: cost to serve £292.41, net margin after CTS £2,088.62
- C3g: cost to serve £69.68, net margin after CTS £1,481.29
- C4: cost to serve £572.25, net margin after CTS £2,900.62
- C4g: cost to serve £280.25, net margin after CTS £1,276.50
- C5: cost to serve £872.74, net margin after CTS £8,587.53
- C6: cost to serve £1,349.03, net margin after CTS £21,057.55
- C7: cost to serve £954.67, net margin after CTS £9,823.49
- C8: cost to serve £939.53, net margin after CTS £11,527.80
- C9: cost to serve £897.63, net margin after CTS £11,848.99
- C_IC1: cost to serve £20,243.15, net margin after CTS £1,917,402.26
- C_IC2: cost to serve £11,549.18, net margin after CTS £929,816.56
- C_IC3: cost to serve £26,597.64, net margin after CTS £1,811,805.62
- C_IC3g: cost to serve £9,229.97, net margin after CTS £613,417.06
- C_IC4: cost to serve £16,595.90, net margin after CTS £1,100,681.25


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 29 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 13.9%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,749.07 | £10,901.23 | +20.0% | £112.24/MWh | £151.69/MWh |
| C5 | electricity | 2018-12-31 | £-204.77 | £2,324.08 | +3.8% | £148.68/MWh | £152.97/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,332.71 | £6,376.41 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,269.51 | £10,243.03 | +20.0% | £128.22/MWh | £175.35/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,922.12 | £3,444.18 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £177.20/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.45/MWh |
| C4g | gas | 2021-09-30 | £-95.91 | £791.17 | +7.1% | £53.99/MWh | £60.11/MWh |
| C5 | electricity | 2021-12-30 | £-294.09 | £2,750.77 | +5.7% | £311.83/MWh | £333.74/MWh |
| C7 | electricity | 2021-12-30 | £-126.40 | £1,983.64 | +1.4% | £311.83/MWh | £320.10/MWh |
| C_IC3 | electricity | 2021-12-31 | £-28,182.24 | £447,008.19 | +1.3% | £224.03/MWh | £260.99/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £316.82/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £307.27/MWh |
| C4 | electricity | 2022-09-30 | £-221.67 | £906.59 | +19.4% | £404.86/MWh | £484.89/MWh |
| C4g | gas | 2022-09-30 | £-1,240.77 | £1,382.75 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,835.40 | £2,404.50 | +20.0% | £266.73/MWh | £318.91/MWh |
| C_IC3g | gas | 2022-12-31 | £-48,818.20 | £586,562.16 | +3.3% | £101.23/MWh | £120.28/MWh |
| C8 | electricity | 2023-03-31 | £-353.94 | £3,898.74 | +4.1% | £319.17/MWh | £336.01/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.14/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £219.79/MWh |
| C4 | electricity | 2023-09-30 | £-327.47 | £1,444.27 | +17.7% | £216.77/MWh | £252.61/MWh |
| C4g | gas | 2023-09-30 | £-2,674.46 | £3,741.13 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-351.18 | £3,990.91 | +3.8% | £242.22/MWh | £238.85/MWh |
| C_IC3 | electricity | 2023-12-31 | £-170,956.78 | £938,447.95 | +13.2% | £118.95/MWh | £127.94/MWh |
| C_IC3g | gas | 2023-12-31 | £-30,262.44 | £295,562.62 | +5.2% | £51.89/MWh | £61.12/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |
| C_IC3g | gas | 2024-12-30 | £-36,843.35 | £268,211.20 | +8.7% | £50.47/MWh | £61.79/MWh |


## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 112 renewal(s) (26 gas) based on recent portfolio-wide margin rates: 59 surcharge(s), 53 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | 7.4% | +0.3% | £131.49/MWh | £131.89/MWh |
| C1g | gas | 2016-12-31 | 19.2% | -5.0% | £27.63/MWh | £26.25/MWh |
| C5 | electricity | 2016-12-31 | 8.7% | -0.3% | £131.49/MWh | £131.04/MWh |
| C7 | electricity | 2016-12-31 | 9.3% | -0.7% | £131.49/MWh | £130.62/MWh |
| C2 | electricity | 2017-04-01 | 11.4% | -1.7% | £127.97/MWh | £125.77/MWh |
| C2g | gas | 2017-04-01 | 19.1% | -5.0% | £34.54/MWh | £32.81/MWh |
| C6 | electricity | 2017-04-01 | 10.7% | -1.3% | £127.97/MWh | £126.27/MWh |
| C8 | electricity | 2017-04-01 | 9.8% | -0.9% | £127.97/MWh | £126.80/MWh |
| C3 | electricity | 2017-07-01 | 11.1% | -1.6% | £122.23/MWh | £120.31/MWh |
| C3g | gas | 2017-07-01 | 20.0% | -5.0% | £24.33/MWh | £23.11/MWh |
| C9 | electricity | 2017-07-01 | 10.8% | -1.4% | £122.23/MWh | £120.53/MWh |
| C4 | electricity | 2017-10-01 | 10.7% | -1.4% | £111.62/MWh | £110.09/MWh |
| C4g | gas | 2017-10-01 | 18.0% | -5.0% | £27.48/MWh | £26.10/MWh |
| C1 | electricity | 2017-12-31 | 11.8% | -1.9% | £120.10/MWh | £117.80/MWh |
| C1g | gas | 2017-12-31 | 15.4% | -3.7% | £34.79/MWh | £33.50/MWh |
| C5 | electricity | 2017-12-31 | 8.8% | -0.4% | £120.10/MWh | £119.60/MWh |
| C7 | electricity | 2017-12-31 | 3.7% | +2.2% | £120.10/MWh | £122.70/MWh |
| C_IC1 | electricity | 2018-01-31 | -17.2% | +12.6% | £112.24/MWh | £126.41/MWh |
| C2 | electricity | 2018-04-01 | -5.8% | +6.9% | £133.89/MWh | £143.11/MWh |
| C2g | gas | 2018-04-01 | 15.2% | -3.6% | £38.21/MWh | £36.82/MWh |
| C6 | electricity | 2018-04-01 | -3.9% | +5.9% | £133.89/MWh | £141.85/MWh |
| C8 | electricity | 2018-04-01 | 8.2% | -0.1% | £133.89/MWh | £133.77/MWh |
| C3 | electricity | 2018-07-01 | 10.7% | -1.3% | £128.29/MWh | £126.57/MWh |
| C3g | gas | 2018-07-01 | 13.6% | -2.8% | £29.63/MWh | £28.79/MWh |
| C9 | electricity | 2018-07-01 | 2.0% | +3.0% | £128.29/MWh | £132.13/MWh |
| C4 | electricity | 2018-10-01 | 2.7% | +2.6% | £145.00/MWh | £148.82/MWh |
| C4g | gas | 2018-10-01 | 13.8% | -2.9% | £34.60/MWh | £33.60/MWh |
| C1 | electricity | 2018-12-31 | 7.4% | +0.3% | £148.68/MWh | £149.13/MWh |
| C1g | gas | 2018-12-31 | 13.8% | -2.9% | £37.15/MWh | £36.07/MWh |
| C5 | electricity | 2018-12-31 | 9.8% | -0.9% | £148.68/MWh | £147.36/MWh |
| C7 | electricity | 2018-12-31 | 10.6% | -1.3% | £148.68/MWh | £146.78/MWh |
| C_IC2 | electricity | 2019-01-31 | -29.5% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -19.9% | +14.0% | £128.22/MWh | £146.12/MWh |
| C2 | electricity | 2019-04-01 | 3.8% | +2.1% | £148.35/MWh | £151.47/MWh |
| C2g | gas | 2019-04-01 | 8.8% | -0.4% | £32.94/MWh | £32.80/MWh |
| C6 | electricity | 2019-04-01 | 8.0% | -0.0% | £148.35/MWh | £148.33/MWh |
| C8 | electricity | 2019-04-01 | 27.3% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 19.6% | -5.0% | £127.03/MWh | £120.68/MWh |
| C3g | gas | 2019-07-01 | 11.6% | -1.8% | £23.62/MWh | £23.19/MWh |
| C9 | electricity | 2019-07-01 | 9.8% | -0.9% | £127.03/MWh | £125.86/MWh |
| C4 | electricity | 2019-10-01 | 8.3% | -0.1% | £126.72/MWh | £126.52/MWh |
| C4g | gas | 2019-10-01 | 15.2% | -3.6% | £20.41/MWh | £19.67/MWh |
| C1 | electricity | 2019-12-31 | 10.9% | -1.5% | £127.44/MWh | £125.56/MWh |
| C1g | gas | 2019-12-31 | 11.5% | -1.7% | £26.17/MWh | £25.71/MWh |
| C5 | electricity | 2019-12-31 | 10.5% | -1.2% | £127.44/MWh | £125.85/MWh |
| C7 | electricity | 2019-12-31 | 9.2% | -0.6% | £127.44/MWh | £126.66/MWh |
| C_IC3 | electricity | 2020-01-01 | 7.3% | +0.4% | £47.59/MWh | £47.76/MWh |
| C_IC3g | gas | 2020-01-01 | 19.9% | -5.0% | £16.25/MWh | £15.44/MWh |
| C_IC2 | electricity | 2020-03-01 | -59.3% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -51.5% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 17.2% | -4.6% | £22.80/MWh | £21.75/MWh |
| C6 | electricity | 2020-03-31 | -46.9% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -15.9% | +12.0% | £125.12/MWh | £140.09/MWh |
| C_IC1 | electricity | 2020-03-31 | 20.4% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 17.0% | -4.5% | £113.43/MWh | £108.32/MWh |
| C9 | electricity | 2020-06-30 | 17.0% | -4.5% | £113.43/MWh | £108.32/MWh |
| C4 | electricity | 2020-09-30 | 11.6% | -1.8% | £124.42/MWh | £122.20/MWh |
| C4g | gas | 2020-09-30 | 19.1% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 10.1% | -1.0% | £133.55/MWh | £132.17/MWh |
| C1g | gas | 2020-12-30 | 13.1% | -2.5% | £28.99/MWh | £28.25/MWh |
| C5 | electricity | 2020-12-30 | 5.0% | +1.5% | £133.55/MWh | £135.58/MWh |
| C7 | electricity | 2020-12-30 | -2.8% | +5.4% | £133.55/MWh | £140.74/MWh |
| C_IC3 | electricity | 2020-12-31 | -4.0% | +6.0% | £50.65/MWh | £53.69/MWh |
| C_IC3g | gas | 2020-12-31 | 6.6% | +0.7% | £20.05/MWh | £20.19/MWh |
| C2 | electricity | 2021-03-31 | -20.9% | +14.4% | £175.90/MWh | £201.31/MWh |
| C2g | gas | 2021-03-31 | 5.8% | +1.1% | £36.20/MWh | £36.60/MWh |
| C6 | electricity | 2021-03-31 | -16.2% | +12.1% | £175.90/MWh | £197.16/MWh |
| C8 | electricity | 2021-03-31 | -11.9% | +10.0% | £175.90/MWh | £193.42/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.6% | +6.3% | £138.90/MWh | £147.67/MWh |
| C_IC1 | electricity | 2021-04-30 | 1.1% | +3.4% | £113.97/MWh | £117.87/MWh |
| C9 | electricity | 2021-06-30 | 1.8% | +3.1% | £170.38/MWh | £175.68/MWh |
| C4 | electricity | 2021-09-30 | -1.8% | +4.9% | £205.15/MWh | £215.21/MWh |
| C4g | gas | 2021-09-30 | 0.1% | +3.9% | £53.99/MWh | £56.11/MWh |
| C1 | electricity | 2021-12-30 | 5.5% | +1.3% | £311.83/MWh | £315.77/MWh |
| C5 | electricity | 2021-12-30 | 5.5% | +1.3% | £311.83/MWh | £315.77/MWh |
| C7 | electricity | 2021-12-30 | 5.5% | +1.3% | £311.83/MWh | £315.77/MWh |
| C_IC3 | electricity | 2021-12-31 | -22.5% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -19.3% | +13.6% | £109.48/MWh | £124.41/MWh |
| C2 | electricity | 2022-03-31 | -23.0% | +15.0% | £361.95/MWh | £416.24/MWh |
| C6 | electricity | 2022-03-31 | -16.7% | +12.3% | £361.95/MWh | £406.61/MWh |
| C8 | electricity | 2022-03-31 | 5.3% | +1.4% | £361.95/MWh | £366.86/MWh |
| C_IC2 | electricity | 2022-04-30 | -9.6% | +8.8% | £269.81/MWh | £293.49/MWh |
| C_IC1 | electricity | 2022-05-30 | -5.9% | +7.0% | £239.42/MWh | £256.06/MWh |
| C9 | electricity | 2022-06-30 | 4.7% | +1.7% | £255.09/MWh | £259.36/MWh |
| C4 | electricity | 2022-09-30 | 7.5% | +0.3% | £404.86/MWh | £405.93/MWh |
| C4g | gas | 2022-09-30 | -23.3% | +15.0% | £183.79/MWh | £211.36/MWh |
| C7 | electricity | 2022-12-30 | 8.7% | -0.4% | £266.73/MWh | £265.76/MWh |
| C_IC3 | electricity | 2022-12-31 | -0.0% | +4.0% | £168.36/MWh | £175.09/MWh |
| C_IC3g | gas | 2022-12-31 | -41.4% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -12.2% | +10.1% | £319.17/MWh | £351.48/MWh |
| C6 | electricity | 2023-03-31 | -0.9% | +4.5% | £319.17/MWh | £333.43/MWh |
| C8 | electricity | 2023-03-31 | 5.7% | +1.1% | £319.17/MWh | £322.85/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.5% | +14.8% | £171.46/MWh | £196.78/MWh |
| C_IC1 | electricity | 2023-06-29 | -16.5% | +12.2% | £163.19/MWh | £183.16/MWh |
| C9 | electricity | 2023-06-30 | -10.0% | +9.0% | £224.44/MWh | £244.67/MWh |
| C4 | electricity | 2023-09-30 | 9.9% | -1.0% | £216.77/MWh | £214.67/MWh |
| C4g | gas | 2023-09-30 | -45.0% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 23.5% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -15.8% | +11.9% | £51.89/MWh | £58.08/MWh |
| C2_2 | electricity | 2024-03-30 | 16.2% | -4.1% | £207.71/MWh | £199.15/MWh |
| C6 | electricity | 2024-03-30 | 10.1% | -1.1% | £207.71/MWh | £205.51/MWh |
| C8 | electricity | 2024-03-30 | 10.1% | -1.1% | £207.71/MWh | £205.51/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.0% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.0% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.7% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 1.0% | +3.5% | £195.97/MWh | £202.85/MWh |
| C7 | electricity | 2024-12-29 | 1.0% | +3.5% | £243.79/MWh | £252.35/MWh |
| C_IC3 | electricity | 2024-12-30 | 19.3% | -5.0% | £116.37/MWh | £110.55/MWh |
| C_IC3g | gas | 2024-12-30 | -17.2% | +12.6% | £50.47/MWh | £56.82/MWh |
| C2_2 | electricity | 2025-03-30 | 9.2% | -0.6% | £284.89/MWh | £283.12/MWh |
| C8 | electricity | 2025-03-30 | 6.0% | +1.0% | £284.89/MWh | £287.67/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **5** | Blind misses: **5** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 5 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £4,067.18 | deliberate: £0.00 | total: £4,067.18

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.35 | Yes | £583.43 |
| C1 | 2021-12-30 | Blind miss | 0.04 | 0.32 | Yes | £-178.13 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.32 | Yes | £236.63 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.38 | Yes | £2,846.06 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.35 | Yes | £579.20 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C2+C2g | £711.27 | £855.45 | £1,566.72 | Yes |
| C1+C1g | £430.29 | £640.44 | £1,070.73 | Yes |
| C3+C3g | £199.58 | £292.68 | £492.26 | Yes |
| C4+C4g | £131.65 | £-2,801.25 | £-2,669.61 | No |
| C_IC3+C_IC3g | £107,473.25 | £-132,711.18 | £-25,237.94 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-133,723.85.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,328,300.67 across 19 billing accounts. Revenue: £14,226,715.24.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,205,006.17 | £1,937,645.41 | £18,891.02 | £879,535.80 | 27.4% |
| 2 | C_IC2 | fixed | £1,566,199.28 | £941,365.74 | £8,751.02 | £452,497.49 | 28.9% |
| 3 | C_IC3 | pass_through | £4,675,864.54 | £1,838,403.27 | £23,137.79 | £107,473.25 | 2.3% |
| 4 | C_IC4 | flex | £2,775,475.73 | £1,117,277.15 | £0.00 | £14,685.55 | 0.5% |
| 5 | C6 | fixed | £38,925.11 | £22,406.57 | £256.33 | £3,543.03 | 9.1% |
| 6 | C9 | fixed | £20,295.74 | £12,746.63 | £129.56 | £1,532.45 | 7.6% |
| 7 | C8 | fixed | £21,704.87 | £12,467.33 | £135.28 | £1,513.77 | 7.0% |
| 8 | C2_2 | fixed | £10,287.91 | £5,470.73 | £68.01 | £1,041.72 | 10.1% |
| 9 | C2g | fixed | £4,313.60 | £2,248.02 | £21.64 | £855.45 | 19.8% |
| 10 | C2 | fixed | £5,108.10 | £3,400.77 | £24.10 | £711.27 | 13.9% |
| 11 | C1g | fixed | £2,603.89 | £1,428.94 | £18.62 | £640.44 | 24.6% |
| 12 | C1 | fixed | £4,235.24 | £2,741.54 | £18.68 | £430.29 | 10.2% |
| 13 | C3g | fixed | £3,254.62 | £1,550.97 | £15.14 | £292.68 | 9.0% |
| 14 | C3 | fixed | £3,623.26 | £2,381.04 | £13.50 | £199.58 | 5.5% |
| 15 | C4 | fixed | £6,617.88 | £3,472.87 | £40.07 | £131.65 | 2.0% |
| 16 | C5 | fixed | £15,288.91 | £9,460.27 | £78.03 | £46.17 | 0.3% |
| 17 | C7 | fixed | £21,776.55 | £10,778.15 | £139.93 | £-1,317.48 | -6.1% |
| 18 | C4g | fixed | £13,553.93 | £1,556.75 | £170.68 | £-2,801.25 | -20.7% |
| 19 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £185,126.72 | £-132,711.18 | -7.2% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,226,715 | 100.0% |
| Wholesale cost | -£7,677,266 | 54.0% |
| **Gross supply margin** | **£6,549,449** | **46.0%** |
| Policy + Network costs | -£4,984,112 | 35.0% |
| Capital cost | -£237,036 | 1.7% |
| **Net supply margin** | **£1,328,301** | **9.3%** |

> *The ledger's `net_margin_gbp` (£6,326,180) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,222,546 | 47.7% | 11.9% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | -7.2% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £54,214 | 58.8% | 6.6% | CMA 3-8% | ✓ |
| resi/elec | £83,362 | 57.6% | 3.8% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £23,726 | 28.6% | -4.3% | Ofgem CMA 2-4% | ⚠ ANOMALY |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: ANOMALIES DETECTED**
- Segment resi/gas net -4.3% (benchmark Ofgem CMA 2-4%)
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
| Customer bills (all-in) | £20,026,948.72 |
|   Less: VAT remitted to HMRC | (£963,753.18) |
| = Revenue (ex-VAT) | £19,063,195.54 |
| Less: non-commodity pass-through | (£4,822,712.90) |
| Wholesale cost (settlement events) | (£7,677,266.07) |
| Gross margin | £6,563,216.58 |
| Capital charges | (£237,036.13) |
| Net margin | £6,326,180.45 |

_Cash reconciliation: of £20,026,948.72 billed, bad debt of £400,637.18 was written off, leaving £19,626,311.54 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £6,889,296.45._

| Acquisition spend | (£1,100.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £6,319,380.45 |

## Management Accounts

P&L and balance sheet from double-entry journal (account codes), not formulas.

| Year | Revenue | COGS | Gross | OpEx | Net | Cash | Equity |
|------|---------|------|-------|------|-----|------|--------||
| 2016 | £15,499.70 | (£7,581.80) | £7,917.90 | (£910.87) | £7,007.03 | £2,470,630.56 | £2,473,643.25 |
| 2017 | £351,275.39 | (£225,655.29) | £125,620.10 | (£8,169.18) | £117,450.91 | £2,558,822.45 | £2,591,094.17 |
| 2018 | £610,257.82 | (£339,695.70) | £270,562.12 | (£14,116.34) | £256,445.77 | £2,791,851.40 | £2,847,539.94 |
| 2019 | £1,658,728.02 | (£945,182.98) | £713,545.04 | (£42,959.77) | £670,585.27 | £3,360,356.14 | £3,518,125.22 |
| 2020 | £1,871,203.42 | (£1,066,760.36) | £804,443.06 | (£46,660.62) | £757,782.44 | £4,092,359.79 | £4,275,907.66 |
| 2021 | £2,452,783.24 | (£1,670,325.19) | £782,458.04 | (£64,460.35) | £717,997.70 | £4,695,608.79 | £4,993,905.35 |
| 2022 | £4,307,246.82 | (£3,223,641.01) | £1,083,605.81 | (£151,335.93) | £932,269.88 | £5,486,468.01 | £5,926,175.23 |
| 2023 | £3,474,974.50 | (£2,544,530.96) | £930,443.55 | (£126,764.75) | £803,678.80 | £6,422,793.62 | £6,729,854.03 |
| 2024 | £3,074,077.05 | (£1,758,791.62) | £1,315,285.42 | (£122,286.28) | £1,192,999.14 | £7,629,840.28 | £7,922,853.17 |
| 2025 | £1,247,149.58 | (£719,130.04) | £528,019.54 | (£66,809.21) | £461,210.34 | £8,384,063.51 | £8,384,063.51 |

**Cross-check:** FAIL -- Journal: £5,917,427.29, Sim: £1,328,300.67, Variance: 345.5%

**Balance sheet -- 2025 year-end:**

| Account | GBP |
|---------|-----|
| Cash and Treasury (1001) | £8,384,063.51 |
| Trade Receivables (1100) | £0.00 |
| **Total Assets** | **£8,384,063.51** |
| Opening Capital (3001) | £2,466,636.22 |
| Cumulative Net Profit | £5,917,427.29 |
| **Total Equity** | **£8,384,063.51** |
| A = L + E | OK |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,499.70 | +5.6% | £6,592.99 | £7,007.03 | +6.3% | AMBER |
| 2017 | £16,138.86 | £351,275.39 | +2076.6% | £7,252.29 | £117,450.91 | +1519.5% | RED |
| 2018 | £386,623.75 | £610,257.82 | +57.8% | £128,424.00 | £256,445.77 | +99.7% | RED |
| 2019 | £675,851.95 | £1,658,728.02 | +145.4% | £281,335.50 | £670,585.27 | +138.4% | RED |
| 2020 | £1,816,630.04 | £1,871,203.42 | +3.0% | £736,963.94 | £757,782.44 | +2.8% | GREEN |
| 2021 | £2,028,952.42 | £2,452,783.24 | +20.9% | £833,649.22 | £717,997.70 | -13.9% | AMBER |
| 2022 | £2,607,611.88 | £4,307,246.82 | +65.2% | £790,935.58 | £932,269.88 | +17.9% | RED |
| 2023 | £4,508,414.67 | £3,474,974.50 | -22.9% | £1,029,561.00 | £803,678.80 | -21.9% | RED |
| 2024 | £3,512,844.39 | £3,074,077.05 | -12.5% | £893,105.75 | £1,192,999.14 | +33.6% | RED |
| 2025 | £3,145,356.42 | £1,247,149.58 | -60.3% | £1,315,150.33 | £461,210.34 | -64.9% | RED |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,319,380.45

## 2016

**Trading & Risk**

- Net margin: £1,192.40 (gross £6,865.76, capital £77.56)
  - Electricity: gross £5,997.23, capital £70.27, net £884.69
  - Gas: gross £868.53, capital £7.29, net £307.71
- Treasury at year end: £2,467,417.61
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.23, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-01-31: treasury £2,466,648.39, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-01: treasury £2,466,660.67, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-31: treasury £2,466,672.67, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-04-30: treasury £2,466,683.79, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-05-30: treasury £2,466,694.82, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-06-29: treasury £2,466,705.43, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-07-29: treasury £2,466,716.17, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-08-28: treasury £2,466,726.93, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-09-27: treasury £2,466,737.87, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-10-27: treasury £2,466,748.80, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-11-26: treasury £2,466,759.62, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-12-26: treasury £2,466,771.57, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
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

- C1 (electricity): tariff £117.30-£131.89/MWh, net margin £137.37
- C1g (gas): tariff £24.34-£26.25/MWh, net margin £96.50
- C2 (electricity): tariff £107.62/MWh, net margin £65.60
- C2g (gas): tariff £26.92/MWh, net margin £113.59
- C3 (electricity): tariff £98.21/MWh, net margin £22.01
- C3g (gas): tariff £21.93/MWh, net margin £41.94
- C4 (electricity): tariff £98.43/MWh, net margin £10.98
- C4g (gas): tariff £24.40/MWh, net margin £55.67
- C5 (electricity): tariff £117.30-£131.04/MWh, net margin £247.28
- C6 (electricity): tariff £107.62/MWh, net margin £11.19
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £233.22
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £120.18
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £36.87

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.863, average bill shock 19.8%, bad debt provision £168.75, avg complaint probability 4.4%
- Solvency signal: £274,158/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £2,067.87 vs. naked (unhedged) net margin: £11,373.81
- hedging cost £9,305.94 vs. a fully unhedged book (commodity-only: actual net £2,067.87 vs. naked net £11,373.81)
  - C1: actual £257.27 vs. naked £834.50 -- hedging cost £577.23
  - C1g: actual £201.41 vs. naked £418.28 -- hedging cost £216.86
  - C2: actual £84.12 vs. naked £377.87 -- hedging cost £293.75
  - C2g: actual £167.17 vs. naked £478.23 -- hedging cost £311.06
  - C3: actual £30.71 vs. naked £426.06 -- hedging cost £395.35
  - C3g: actual £79.01 vs. naked £528.45 -- hedging cost £449.44
  - C4: actual £46.81 vs. naked £248.24 -- hedging cost £201.43
  - C4g: actual £174.79 vs. naked £810.89 -- hedging cost £636.10
  - C5: actual £411.59 vs. naked £2,694.43 -- hedging cost £2,282.84
  - C6: actual £-13.41 vs. naked £1,158.83 -- hedging cost £1,172.24
  - C7: actual £393.43 vs. naked £1,940.02 -- hedging cost £1,546.58
  - C8: actual £174.46 vs. naked £784.20 -- hedging cost £609.75
  - C9: actual £60.52 vs. naked £673.81 -- hedging cost £613.29

**Year narrative:** 2016 produced a net gain of £1,192.40 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 36 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £30,791.68 (gross £124,065.20, capital £1,272.64)
  - Electricity: gross £122,440.25, capital £1,257.94, net £30,296.01
  - Gas: gross £1,624.95, capital £14.71, net £495.67
- Treasury at year end: £2,497,944.98
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.92 (avg 0.92), C7 0.90 (avg 0.90), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,467,422.33, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-02-24: treasury £2,467,428.35, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-03-26: treasury £2,467,434.79, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-04-25: treasury £2,467,792.56, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-05-25: treasury £2,467,793.04, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-06-24: treasury £2,467,794.60, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-07-24: treasury £2,467,972.38, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-08-23: treasury £2,467,976.90, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-09-22: treasury £2,467,980.50, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-10-22: treasury £2,468,253.94, C5->1.00, C7->1.00, VaR (current £893.87 / stressed £353.98) ratio 2.53
  - 2017-11-21: treasury £2,468,263.66, C5->1.00, C7->1.00, VaR (current £893.87 / stressed £353.98) ratio 2.53
  - 2017-12-21: treasury £2,468,273.06, C5->1.00, C7->1.00, VaR (current £893.87 / stressed £353.98) ratio 2.53
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-20.46

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £4,199.79
  - By billing account: C1 £1,834.41, C2 £3,845.46, C3 £3,730.10, C4 £3,723.31, C5 £4,493.01, C6 £8,284.71, C7 £3,212.57, C8 £4,623.25, C9 £4,051.32
- Bill shock events (>=20%): 54 -- C1g 2017-04-30 (29%); C1g 2017-06-30 (25%); C1g 2017-10-31 (43%); C1g 2017-11-30 (47%); C1g 2017-12-31 (21%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-04-30 (22%); C2g 2017-05-31 (23%); C2g 2017-06-30 (31%); C2g 2017-09-30 (21%); C2g 2017-10-31 (55%); C2g 2017-11-30 (58%); C2g 2017-12-31 (23%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-04-30 (32%); C3g 2017-05-31 (23%); C3g 2017-06-30 (31%); C3g 2017-09-30 (21%); C3g 2017-10-31 (56%); C3g 2017-11-30 (58%); C3g 2017-12-31 (23%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (28%); C4 2017-09-30 (21%); C4 2017-10-31 (26%); C4 2017-11-30 (26%); C4g 2017-04-30 (34%); C4g 2017-05-31 (25%); C4g 2017-06-30 (34%); C4g 2017-09-30 (24%); C4g 2017-10-31 (48%); C4g 2017-11-30 (61%); C4g 2017-12-31 (23%)
- Churn risk (accounts renewing in 2017): 9 at risk (≥20% churn prob): C1 35%, C2 26%, C3 29%, C4 29%, C5 32%, C6 35%, C7 38%, C8 35%, C9 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.80-£131.89/MWh, net margin £119.76
- C1g (gas): tariff £26.25-£33.50/MWh, net margin £105.08
- C2 (electricity): tariff £107.62-£125.77/MWh, net margin £96.57
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £205.85
- C3 (electricity): tariff £98.21-£120.31/MWh, net margin £69.69
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £54.33
- C4 (electricity): tariff £98.43-£110.09/MWh, net margin £45.05
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £130.41
- C5 (electricity): tariff £119.60-£131.04/MWh, net margin £163.38
- C6 (electricity): tariff £107.62-£126.27/MWh, net margin £59.18
- C7 (electricity): tariff £98.77-£195.93/MWh, net margin £158.77
- C8 (electricity): tariff £84.56-£190.21/MWh, net margin £209.24
- C9 (electricity): tariff £77.16-£180.79/MWh, net margin £133.47
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £29,240.89

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.855, average bill shock 16.8%, bad debt provision £1,368.86, avg complaint probability 4.4%
- Solvency signal: £249,794/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,326.23 vs. naked (unhedged) net margin: £113,105.47
- hedging cost £82,779.24 vs. a fully unhedged book (commodity-only: actual net £30,326.23 vs. naked net £113,105.47)
  - C1: actual £14.91 vs. naked £330.35 -- hedging cost £315.44
  - C1g: actual £129.99 vs. naked £235.90 -- hedging cost £105.91
  - C2: actual £103.88 vs. naked £438.17 -- hedging cost £334.29
  - C2g: actual £231.83 vs. naked £555.53 -- hedging cost £323.70
  - C3: actual £110.45 vs. naked £513.32 -- hedging cost £402.87
  - C3g: actual £24.21 vs. naked £509.77 -- hedging cost £485.57
  - C4: actual £41.09 vs. naked £275.30 -- hedging cost £234.20
  - C4g: actual £49.52 vs. naked £588.76 -- hedging cost £539.24
  - C5: actual £-204.77 vs. naked £1,068.93 -- hedging cost £1,273.70
  - C6: actual £102.36 vs. naked £1,675.46 -- hedging cost £1,573.11
  - C7: actual £-12.80 vs. naked £858.89 -- hedging cost £871.69
  - C8: actual £253.49 vs. naked £990.15 -- hedging cost £736.66
  - C9: actual £241.19 vs. naked £951.79 -- hedging cost £710.61
  - C_IC1: actual £29,240.89 vs. naked £104,113.14 -- hedging cost £74,872.25

**Year narrative:** 2017 produced a net gain of £30,791.68 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 54 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £104,990.60 (gross £268,919.62, capital £1,552.96)
  - Electricity: gross £267,459.75, capital £1,532.09, net £104,607.05
  - Gas: gross £1,459.87, capital £20.87, net £383.55
- Treasury at year end: £2,486,550.36
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
- Average CLV (Point-in-Time, year-end 2018): £103,299.66
  - By billing account: C1 £2,007.61, C2 £3,590.32, C3 £3,398.36, C4 £2,777.42, C5 £4,087.58, C6 £6,907.45, C7 £3,121.21, C8 £3,995.23, C9 £3,728.81, C_IC1 £999,382.60
- Bill shock events (>=20%): 61 -- C1g 2018-01-31 (28%); C1g 2018-04-30 (30%); C1g 2018-06-30 (27%); C1g 2018-10-31 (46%); C1g 2018-11-30 (50%); C1g 2018-12-31 (21%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (38%); C2g 2018-05-31 (22%); C2g 2018-06-30 (30%); C2g 2018-10-31 (54%); C2g 2018-11-30 (57%); C2g 2018-12-31 (22%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (34%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (32%); C3g 2018-05-31 (23%); C3g 2018-06-30 (31%); C3g 2018-09-30 (22%); C3g 2018-10-31 (57%); C3g 2018-11-30 (59%); C3g 2018-12-31 (23%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (28%); C4 2018-09-30 (23%); C4 2018-10-31 (41%); C4 2018-11-30 (28%); C4g 2018-04-30 (33%); C4g 2018-05-31 (24%); C4g 2018-06-30 (33%); C4g 2018-09-30 (23%); C4g 2018-10-31 (101%); C4g 2018-11-30 (63%); C4g 2018-12-31 (24%); C_IC1 2018-01-31 (21%); C_IC1 2018-02-28 (61%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 9 at risk (≥20% churn prob): C1 35%, C2 35%, C3 35%, C4 35%, C5 35%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £117.80-£152.13/MWh, net margin £15.25
- C1g (gas): tariff £33.50-£36.07/MWh, net margin £129.91
- C2 (electricity): tariff £125.77-£143.11/MWh, net margin £73.54
- C2g (gas): tariff £32.81-£36.82/MWh, net margin £187.38
- C3 (electricity): tariff £120.31-£126.57/MWh, net margin £67.83
- C3g (gas): tariff £23.11-£28.79/MWh, net margin £19.57
- C4 (electricity): tariff £110.09-£148.82/MWh, net margin £61.21
- C4g (gas): tariff £26.10-£33.60/MWh, net margin £46.69
- C5 (electricity): tariff £119.60-£155.97/MWh, net margin £-203.61 -- **net-negative**
- C6 (electricity): tariff £126.27-£141.85/MWh, net margin £-54.15 -- **net-negative**
- C7 (electricity): tariff £98.77-£224.67/MWh, net margin £-10.43 -- **net-negative**
- C8 (electricity): tariff £99.63-£205.15/MWh, net margin £145.54
- C9 (electricity): tariff £94.70-£202.69/MWh, net margin £217.98
- C_IC1 (electricity): tariff £-82.12-£232.03/MWh, net margin £111,024.79
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,730.90 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.843, average bill shock 16.7%, bad debt provision £2,421.86, avg complaint probability 4.5%
- Solvency signal: £226,050/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £115,600.97 vs. naked (unhedged) net margin: £253,468.16
- hedging cost £137,867.20 vs. a fully unhedged book (commodity-only: actual net £115,600.97 vs. naked net £253,468.16)
  - C1: actual £104.79 vs. naked £572.43 -- hedging cost £467.64
  - C1g: actual £137.34 vs. naked £341.62 -- hedging cost £204.27
  - C2: actual £57.83 vs. naked £495.00 -- hedging cost £437.17
  - C2g: actual £166.62 vs. naked £437.79 -- hedging cost £271.16
  - C3: actual £23.75 vs. naked £555.58 -- hedging cost £531.83
  - C3g: actual £33.09 vs. naked £637.87 -- hedging cost £604.78
  - C4: actual £101.47 vs. naked £462.35 -- hedging cost £360.87
  - C4g: actual £72.66 vs. naked £1,068.02 -- hedging cost £995.36
  - C5: actual £166.75 vs. naked £2,029.18 -- hedging cost £1,862.43
  - C6: actual £-151.98 vs. naked £1,825.75 -- hedging cost £1,977.73
  - C7: actual £99.22 vs. naked £1,377.11 -- hedging cost £1,277.88
  - C8: actual £58.33 vs. naked £972.67 -- hedging cost £914.34
  - C9: actual £179.01 vs. naked £1,083.46 -- hedging cost £904.45
  - C_IC1: actual £121,282.98 vs. naked £208,033.42 -- hedging cost £86,750.44
  - C_IC2: actual £-6,730.90 vs. naked £33,575.93 -- hedging cost £40,306.83

**Year narrative:** 2018 produced a net gain of £104,990.60 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 61 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £227,244.02 (gross £711,697.53, capital £11,326.68)
  - Electricity: gross £635,515.10, capital £2,102.35, net £226,679.21
  - Gas: gross £76,182.44, capital £9,224.32, net £564.81
- Treasury at year end: £2,612,481.82
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.88 (avg 0.88), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2019-02-04 period 35, net margin £-14.60

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £135,635.19
  - By billing account: C1 £2,000.65, C2 £3,001.86, C3 £3,383.71, C4 £2,986.76, C5 £4,405.28, C6 £7,503.26, C7 £3,308.93, C8 £3,915.76, C9 £3,862.08, C_IC1 £907,973.04, C_IC2 £549,645.75
- Bill shock events (>=20%): 63 -- C1 2019-04-30 (21%); C1g 2019-04-30 (30%); C1g 2019-06-30 (27%); C1g 2019-10-31 (46%); C1g 2019-11-30 (50%); C1g 2019-12-31 (20%); C5 2019-01-31 (44%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-04-30 (36%); C2g 2019-05-31 (22%); C2g 2019-06-30 (30%); C2g 2019-10-31 (53%); C2g 2019-11-30 (56%); C2g 2019-12-31 (22%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (22%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-04-30 (33%); C3g 2019-05-31 (24%); C3g 2019-06-30 (32%); C3g 2019-09-30 (21%); C3g 2019-10-31 (56%); C3g 2019-11-30 (58%); C3g 2019-12-31 (23%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (72%); C9 2019-11-30 (36%); C4 2019-04-30 (31%); C4 2019-09-30 (25%); C4 2019-11-30 (26%); C4g 2019-04-30 (34%); C4g 2019-05-31 (25%); C4g 2019-06-30 (35%); C4g 2019-09-30 (25%); C4g 2019-10-31 (26%); C4g 2019-11-30 (61%); C4g 2019-12-31 (23%); C_IC1 2019-02-28 (55%); C_IC1 2019-03-31 (129%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 10 at risk (≥20% churn prob): C1 35%, C2 35%, C3 35%, C4 35%, C5 38%, C6 29%, C7 35%, C8 38%, C9 32%, C_IC1 23%

**Pricing & Margin**

- C1 (electricity): tariff £125.56-£152.13/MWh, net margin £104.66
- C1g (gas): tariff £25.71-£36.07/MWh, net margin £137.53
- C2 (electricity): tariff £143.11-£151.47/MWh, net margin £124.09
- C2g (gas): tariff £26.00-£36.82/MWh, net margin £128.64
- C3 (electricity): tariff £120.68-£126.57/MWh, net margin £23.91
- C3g (gas): tariff £23.19-£28.79/MWh, net margin £88.99
- C4 (electricity): tariff £126.52-£148.82/MWh, net margin £99.46
- C4g (gas): tariff £19.67-£33.60/MWh, net margin £86.10
- C5 (electricity): tariff £125.85-£155.97/MWh, net margin £165.75
- C6 (electricity): tariff £141.85-£148.33/MWh, net margin £81.36
- C7 (electricity): tariff £99.52-£224.67/MWh, net margin £98.91
- C8 (electricity): tariff £107.46-£211.40/MWh, net margin £167.68
- C9 (electricity): tariff £101.25-£202.69/MWh, net margin £183.23
- C_IC1 (electricity): tariff £0.00-£267.52/MWh, net margin £142,951.08
- C_IC2 (electricity): tariff £-60.00-£283.06/MWh, net margin £81,495.84
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £1,183.24
- C_IC3g (gas): tariff £27.53/MWh, net margin £123.56

**Portfolio Health**

- Capital cost ratio: 1.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.854, average bill shock 16.8%, bad debt provision £6,273.36, avg complaint probability 4.4%
- Solvency signal: £217,707/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £252,567.75 vs. naked (unhedged) net margin: £841,711.08
- hedging cost £589,143.33 vs. a fully unhedged book (commodity-only: actual net £252,567.75 vs. naked net £841,711.08)
  - C1: actual £73.76 vs. naked £486.12 -- hedging cost £412.37
  - C1g: actual £141.19 vs. naked £299.59 -- hedging cost £158.40
  - C2: actual £154.48 vs. naked £660.80 -- hedging cost £506.33
  - C2g: actual £98.09 vs. naked £496.94 -- hedging cost £398.86
  - C3: actual £34.68 vs. naked £668.37 -- hedging cost £633.69
  - C3g: actual £156.38 vs. naked £674.58 -- hedging cost £518.21
  - C4: actual £102.87 vs. naked £442.65 -- hedging cost £339.78
  - C4g: actual £114.39 vs. naked £768.13 -- hedging cost £653.74
  - C5: actual £-33.30 vs. naked £1,585.61 -- hedging cost £1,618.91
  - C6: actual £221.83 vs. naked £2,590.33 -- hedging cost £2,368.50
  - C7: actual £53.40 vs. naked £1,143.91 -- hedging cost £1,090.51
  - C8: actual £239.62 vs. naked £1,370.72 -- hedging cost £1,131.10
  - C9: actual £198.62 vs. naked £1,299.33 -- hedging cost £1,100.71
  - C_IC1: actual £160,623.08 vs. naked £301,777.75 -- hedging cost £141,154.67
  - C_IC2: actual £89,081.88 vs. naked £165,284.43 -- hedging cost £76,202.55
  - C_IC3: actual £1,183.24 vs. naked £295,972.25 -- hedging cost £294,789.01
  - C_IC3g: actual £123.56 vs. naked £66,189.55 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £227,244.02 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 63 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £126,100.83 (gross £802,642.46, capital £7,382.42)
  - Electricity: gross £725,242.66, capital £1,994.11, net £121,595.59
  - Gas: gross £77,399.81, capital £5,388.31, net £4,505.24
- Treasury at year end: £2,918,514.29
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
- Average CLV (Point-in-Time, year-end 2020): £210,533.28
  - By billing account: C1 £2,246.18, C2 £3,651.12, C3 £2,878.91, C4 £3,120.67, C5 £5,536.08, C6 £7,495.41, C7 £3,324.51, C8 £4,603.11, C9 £3,979.79, C_IC1 £617,472.14, C_IC2 £310,265.28, C_IC3 £1,141,184.33, C_IC4 £631,175.08
- Bill shock events (>=20%): 57 -- C1g 2020-04-30 (29%); C1g 2020-06-30 (25%); C1g 2020-10-31 (43%); C1g 2020-11-30 (47%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (22%); C2g 2020-03-31 (21%); C2g 2020-04-30 (35%); C2g 2020-05-31 (22%); C2g 2020-06-30 (29%); C2g 2020-10-31 (51%); C2g 2020-11-30 (55%); C2g 2020-12-31 (22%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-03-31 (21%); C3g 2020-04-30 (32%); C3g 2020-05-31 (23%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (35%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (22%); C4 2020-11-30 (24%); C4g 2020-03-31 (22%); C4g 2020-04-30 (33%); C4g 2020-05-31 (24%); C4g 2020-06-30 (33%); C4g 2020-09-30 (23%); C4g 2020-10-31 (42%); C4g 2020-11-30 (60%); C4g 2020-12-31 (23%); C_IC1 2020-03-31 (58%); C_IC1 2020-04-30 (75%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (120%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 32%, C2 35%, C3 35%, C4 35%, C5 35%, C6 32%, C7 35%, C8 38%, C9 41%

**Pricing & Margin**

- C1 (electricity): tariff £125.56-£132.17/MWh, net margin £73.39
- C1g (gas): tariff £25.00-£25.71/MWh, net margin £141.23
- C2 (electricity): tariff £143.89-£151.47/MWh, net margin £181.86
- C2g (gas): tariff £21.75-£26.00/MWh, net margin £146.10
- C3 (electricity): tariff £120.68/MWh, net margin £16.15
- C3g (gas): tariff £23.19/MWh, net margin £87.85
- C4 (electricity): tariff £122.20-£126.52/MWh, net margin £85.94
- C4g (gas): tariff £16.09-£19.67/MWh, net margin £72.79
- C5 (electricity): tariff £125.85-£138.58/MWh, net margin £-35.86 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.33/MWh, net margin £361.26
- C7 (electricity): tariff £99.52-£211.11/MWh, net margin £54.58
- C8 (electricity): tariff £110.07-£211.40/MWh, net margin £335.99
- C9 (electricity): tariff £85.11-£193.29/MWh, net margin £136.92
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £58,087.37
- C_IC2 (electricity): tariff £-79.50-£283.06/MWh, net margin £46,781.50
- C_IC3 (electricity): tariff £37.53-£80.54/MWh, net margin £10,937.21
- C_IC3g (gas): tariff £15.44-£20.19/MWh, net margin £4,057.27
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £4,579.29

**Portfolio Health**

- Capital cost ratio: 0.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.858, average bill shock 15.0%, bad debt provision £6,364.22, avg complaint probability 4.2%
- Solvency signal: £224,501/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £83,456.46 vs. naked (unhedged) net margin: £944,301.41
- hedging cost £860,844.95 vs. a fully unhedged book (commodity-only: actual net £83,456.46 vs. naked net £944,301.41)
  - C1: actual £-20.44 vs. naked £96.26 -- hedging cost £116.70
  - C1g: actual £30.51 vs. naked £-140.93 -- hedging added £171.44
  - C2: actual £175.00 vs. naked £570.63 -- hedging cost £395.63
  - C2g: actual £160.82 vs. naked £426.75 -- hedging cost £265.93
  - C4: actual £23.66 vs. naked £234.28 -- hedging cost £210.62
  - C4g: actual £-95.91 vs. naked £220.97 -- hedging cost £316.88
  - C5: actual £-294.09 vs. naked £224.62 -- hedging cost £518.72
  - C6: actual £354.17 vs. naked £2,175.31 -- hedging cost £1,821.14
  - C7: actual £-126.40 vs. naked £312.89 -- hedging cost £439.28
  - C8: actual £338.23 vs. naked £1,167.31 -- hedging cost £829.09
  - C9: actual £-23.13 vs. naked £693.62 -- hedging cost £716.75
  - C_IC1: actual £39,775.93 vs. naked £134,007.11 -- hedging cost £94,231.18
  - C_IC2: actual £45,917.01 vs. naked £98,961.61 -- hedging cost £53,044.61
  - C_IC3: actual £-17,098.96 vs. naked £216,850.10 -- hedging cost £233,949.06
  - C_IC3g: actual £6,419.86 vs. naked £147,730.42 -- hedging cost £141,310.56
  - C_IC4: actual £7,920.21 vs. naked £340,770.45 -- hedging cost £332,850.24

**Year narrative:** 2020 produced a net gain of £126,100.83 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 57 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £66,350.48 (gross £780,857.87, capital £15,948.74)
  - Electricity: gross £698,147.06, capital £5,720.93, net £68,398.79
  - Gas: gross £82,710.81, capital £10,227.81, net £-2,048.32
- Treasury at year end: £2,946,681.24
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
- Average CLV (Point-in-Time, year-end 2021): £201,268.60
  - By billing account: C1 £2,113.79, C2 £3,502.27, C3 £3,027.43, C4 £2,773.78, C5 £5,011.45, C6 £8,350.55, C7 £3,430.41, C8 £4,384.31, C9 £3,555.68, C_IC1 £596,851.96, C_IC2 £334,718.49, C_IC3 £1,009,507.84, C_IC4 £639,263.86
- Bill shock events (>=20%): 55 -- C1g 2021-04-30 (28%); C1g 2021-06-30 (24%); C1g 2021-10-31 (41%); C1g 2021-11-30 (46%); C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (21%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C2g 2021-04-30 (25%); C2g 2021-05-31 (22%); C2g 2021-06-30 (30%); C2g 2021-10-31 (53%); C2g 2021-11-30 (56%); C2g 2021-12-31 (22%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (23%); C4 2021-10-31 (48%); C4 2021-11-30 (31%); C4g 2021-04-30 (33%); C4g 2021-05-31 (24%); C4g 2021-06-30 (32%); C4g 2021-09-30 (24%); C4g 2021-10-31 (111%); C4g 2021-11-30 (63%); C4g 2021-12-31 (24%); C_IC1 2021-05-31 (42%); C_IC2 2021-03-31 (25%); C_IC2 2021-04-30 (85%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (22%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%)
- Churn risk (accounts renewing in 2021): 12 at risk (≥20% churn prob): C1 32%, C2 35%, C4 35%, C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC3 20%, C_IC4 29%

**Pricing & Margin**

- C1 (electricity): tariff £132.17/MWh, net margin £-20.14 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £30.19
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £156.73
- C2g (gas): tariff £21.75-£35.00/MWh, net margin £95.70
- C4 (electricity): tariff £122.20-£183.00/MWh, net margin £-60.49 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-483.73 -- **net-negative**
- C5 (electricity): tariff £138.58/MWh, net margin £-290.77 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.16/MWh, net margin £523.90
- C7 (electricity): tariff £110.58-£274.50/MWh, net margin £-135.99 -- **net-negative**
- C8 (electricity): tariff £110.07-£274.50/MWh, net margin £339.06
- C9 (electricity): tariff £85.11-£263.53/MWh, net margin £-19.67 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £33,072.69
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £59,596.03
- C_IC3 (electricity): tariff £42.19-£395.99/MWh, net margin £-28,111.63 -- **net-negative**
- C_IC3g (gas): tariff £20.19-£124.41/MWh, net margin £-1,690.48 -- **net-negative**
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £3,349.06

**Portfolio Health**

- Capital cost ratio: 2.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.853, average bill shock 15.9%, bad debt provision £9,265.40, avg complaint probability 4.3%
- Solvency signal: £245,557/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £164,651.81 vs. naked (unhedged) net margin: £371,295.76
- hedging cost £206,643.95 vs. a fully unhedged book (commodity-only: actual net £164,651.81 vs. naked net £371,295.76)
  - C2: actual £135.95 vs. naked £124.53 -- hedging added £11.42
  - C2g: actual £30.93 vs. naked £-158.95 -- hedging added £189.88
  - C4: actual £-221.67 vs. naked £-170.72 -- hedging cost £50.96
  - C4g: actual £-1,240.77 vs. naked £-1,032.79 -- hedging cost £207.98
  - C6: actual £510.53 vs. naked £268.07 -- hedging added £242.46
  - C7: actual £-1,835.40 vs. naked £-870.69 -- hedging cost £964.72
  - C8: actual £283.50 vs. naked £107.31 -- hedging added £176.20
  - C9: actual £-56.89 vs. naked £-192.00 -- hedging added £135.11
  - C_IC1: actual £34,432.42 vs. naked £-58,490.17 -- hedging added £92,922.59
  - C_IC2: actual £68,568.91 vs. naked £24,540.61 -- hedging added £44,028.29
  - C_IC3: actual £114,787.22 vs. naked £250,205.61 -- hedging cost £135,418.39
  - C_IC3g: actual £-48,818.20 vs. naked £32,238.32 -- hedging cost £81,056.52
  - C_IC4: actual £-1,924.70 vs. naked £124,726.63 -- hedging cost £126,651.33

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £66,350.48 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 55 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £276,049.47 (gross £1,082,363.84, capital £65,397.76)
  - Electricity: gross £992,355.58, capital £13,486.51, net £325,615.23
  - Gas: gross £90,008.26, capital £51,911.25, net £-49,565.76
- Treasury at year end: £3,115,333.05
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,054,433.91, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,470.24 / stressed £20,887.53) ratio 2.70
  - 2022-05-29: treasury £3,054,566.26, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,579.64 / stressed £20,916.55) ratio 2.71
  - 2022-06-28: treasury £3,054,560.62, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,579.64 / stressed £20,916.55) ratio 2.71
  - 2022-07-28: treasury £3,054,366.87, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,641.26 / stressed £20,928.85) ratio 2.71
  - 2022-08-27: treasury £3,054,357.20, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,641.26 / stressed £20,928.85) ratio 2.71
  - 2022-09-26: treasury £3,054,341.67, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,641.26 / stressed £20,928.85) ratio 2.71
  - 2022-10-26: treasury £3,051,711.91, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,703.68 / stressed £20,939.44) ratio 2.71
  - 2022-11-25: treasury £3,051,561.02, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,703.68 / stressed £20,939.44) ratio 2.71
  - 2022-12-25: treasury £3,051,294.02, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,703.68 / stressed £20,939.44) ratio 2.71
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.71
- Worst single period: C_IC3g on 2022-12-31 period 1, net margin £-2,969.97

**Customer Book**

- Active accounts: 14 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £203,375.95
  - By billing account: C1 £2,234.69, C2 £2,855.29, C2_2 £491.19, C3 £3,099.47, C4 £1,566.81, C5 £4,917.25, C6 £8,318.22, C7 £2,844.71, C8 £3,966.66, C9 £3,979.32, C_IC1 £661,430.67, C_IC2 £378,474.08, C_IC3 £1,165,020.11, C_IC4 £608,064.90
- Bill shock events (>=20%): 59 -- C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-03-30 (21%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-04-30 (34%); C4g 2022-05-31 (25%); C4g 2022-06-30 (34%); C4g 2022-09-30 (29%); C4g 2022-10-31 (237%); C4g 2022-11-30 (67%); C4g 2022-12-31 (24%); C_IC1 2022-06-30 (78%); C_IC2 2022-05-31 (57%); C_IC3 2022-01-31 (111%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (35%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (69%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 9 at risk (≥20% churn prob): C2 32%, C4 35%, C6 32%, C7 35%, C8 35%, C9 38%, C_IC1 20%, C_IC3 23%, C_IC4 32%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £12.87
- C2_2 (electricity): tariff £361.95/MWh, net margin £25.73
- C2g (gas): tariff £35.00/MWh, net margin £-21.81 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-278.63 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,808.84 -- **net-negative**
- C6 (electricity): tariff £197.16-£406.61/MWh, net margin £809.76
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,831.75 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-193.33 -- **net-negative**
- C9 (electricity): tariff £138.04-£389.05/MWh, net margin £-124.88 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£465.41/MWh, net margin £138,293.62
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £77,118.44
- C_IC3 (electricity): tariff £137.57-£395.99/MWh, net margin £113,712.86
- C_IC3g (gas): tariff £120.28-£124.41/MWh, net margin £-47,735.11 -- **net-negative**
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £-1,929.46 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 6.0% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,429,555.46 -> £3,051,263.00 (11.0%)
- Bills issued: 148, average clarity 0.805, average bill shock 34.1%, bad debt provision £36,153.72, avg complaint probability 5.4%
- Solvency signal: £283,212/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £113,125.66 vs. naked (unhedged) net margin: £1,103,478.16
- hedging cost £990,352.50 vs. a fully unhedged book (commodity-only: actual net £113,125.66 vs. naked net £1,103,478.16)
  - C2_2: actual £25.26 vs. naked £1,644.79 -- hedging cost £1,619.53
  - C4: actual £-327.47 vs. naked £670.03 -- hedging cost £997.50
  - C4g: actual £-2,674.46 vs. naked £2,253.50 -- hedging cost £4,927.96
  - C6: actual £1,111.10 vs. naked £3,987.80 -- hedging cost £2,876.69
  - C7: actual £-351.18 vs. naked £2,280.97 -- hedging cost £2,632.14
  - C8: actual £-353.94 vs. naked £1,101.73 -- hedging cost £1,455.67
  - C9: actual £-57.04 vs. naked £1,007.37 -- hedging cost £1,064.40
  - C_IC1: actual £221,531.16 vs. naked £259,830.83 -- hedging cost £38,299.67
  - C_IC2: actual £91,934.59 vs. naked £131,750.57 -- hedging cost £39,815.97
  - C_IC3: actual £-170,956.78 vs. naked £447,571.40 -- hedging cost £618,528.18
  - C_IC3g: actual £-30,262.44 vs. naked £84,525.03 -- hedging cost £114,787.47
  - C_IC4: actual £3,506.84 vs. naked £166,854.16 -- hedging cost £163,347.31

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £276,049.47 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 59 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £60,001.32 (gross £929,406.49, capital £49,272.84)
  - Electricity: gross £808,524.21, capital £9,914.73, net £92,243.16
  - Gas: gross £120,882.28, capital £39,358.11, net £-32,241.84
- Treasury at year end: £3,228,942.40
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,115,332.19, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £124,222.33 / stressed £45,004.28) ratio 2.76
  - 2023-02-23: treasury £3,115,331.91, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £124,222.33 / stressed £45,004.28) ratio 2.76
  - 2023-03-25: treasury £3,115,331.57, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £124,222.33 / stressed £45,004.28) ratio 2.76
  - 2023-04-24: treasury £3,200,051.29, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £131,442.47 / stressed £50,090.39) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-12-31 period 1, net margin £-3,474.99

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £204,713.09
  - By billing account: C1 £2,230.09, C2 £2,845.74, C2_2 £1,372.49, C3 £3,095.03, C4 £1,192.73, C5 £4,908.36, C6 £9,102.41, C7 £3,027.66, C8 £4,030.66, C9 £4,243.93, C_IC1 £712,596.50, C_IC2 £405,651.44, C_IC3 £1,083,571.61, C_IC4 £628,114.55
- Bill shock events (>=20%): 45 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (31%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-04-30 (30%); C4 2023-09-30 (25%); C4 2023-11-30 (28%); C4g 2023-03-31 (21%); C4g 2023-04-30 (35%); C4g 2023-05-31 (27%); C4g 2023-06-30 (37%); C4g 2023-09-30 (28%); C4g 2023-10-31 (44%); C4g 2023-11-30 (67%); C4g 2023-12-31 (24%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (61%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (102%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (36%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%)
- Churn risk (accounts renewing in 2023): 8 at risk (≥20% churn prob): C2_2 38%, C4 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC3 23%, C_IC4 29%

**Pricing & Margin**

- C2_2 (electricity): tariff £351.48-£361.95/MWh, net margin £508.95
- C4 (electricity): tariff £255.61-£305.00/MWh, net margin £-101.81 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,474.39 -- **net-negative**
- C6 (electricity): tariff £333.43-£406.61/MWh, net margin £1,259.48
- C7 (electricity): tariff £187.67-£457.50/MWh, net margin £-349.77 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-25.36 -- **net-negative**
- C9 (electricity): tariff £192.24-£389.05/MWh, net margin £218.44
- C_IC1 (electricity): tariff £-60.00-£465.41/MWh, net margin £167,968.34
- C_IC2 (electricity): tariff £-186.24-£479.73/MWh, net margin £89,099.03
- C_IC3 (electricity): tariff £102.88-£262.64/MWh, net margin £-169,848.32 -- **net-negative**
- C_IC3g (gas): tariff £61.12-£120.28/MWh, net margin £-30,767.46 -- **net-negative**
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £3,514.18

**Portfolio Health**

- Capital cost ratio: 5.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,641,268.14 -> £3,228,939.02 (11.3%)
- Bills issued: 144, average clarity 0.818, average bill shock 17.6%, bad debt provision £13,952.37, avg complaint probability 4.8%
- Solvency signal: £322,894/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £383,194.88 vs. naked (unhedged) net margin: £1,181,600.09
- hedging cost £798,405.22 vs. a fully unhedged book (commodity-only: actual net £383,194.88 vs. naked net £1,181,600.09)
  - C2_2: actual £839.87 vs. naked £2,434.72 -- hedging cost £1,594.84
  - C4: actual £364.88 vs. naked £853.51 -- hedging cost £488.62
  - C4g: actual £798.54 vs. naked £2,086.91 -- hedging cost £1,288.37
  - C6: actual £1,408.43 vs. naked £5,081.76 -- hedging cost £3,673.33
  - C7: actual £475.75 vs. naked £1,923.14 -- hedging cost £1,447.39
  - C8: actual £209.11 vs. naked £1,971.27 -- hedging cost £1,762.16
  - C9: actual £618.62 vs. naked £2,123.62 -- hedging cost £1,505.00
  - C_IC1: actual £149,050.82 vs. naked £292,838.32 -- hedging cost £143,787.50
  - C_IC2: actual £98,445.43 vs. naked £166,953.53 -- hedging cost £68,508.10
  - C_IC3: actual £164,098.70 vs. naked £439,775.73 -- hedging cost £275,677.04
  - C_IC3g: actual £-36,843.35 vs. naked £77,603.64 -- hedging cost £114,446.99
  - C_IC4: actual £3,728.07 vs. naked £187,953.96 -- hedging cost £184,225.88

**Year narrative:** 2023 produced a net gain of £60,001.32 across 12 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 45 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £338,951.03 (gross £1,314,994.79, capital £55,821.44)
  - Electricity: gross £1,190,208.81, capital £9,908.22, net £375,576.54
  - Gas: gross £124,785.97, capital £45,913.23, net £-36,625.52
- Treasury at year end: £3,611,717.95
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
- Average CLV (Point-in-Time, year-end 2024): £236,624.73
  - By billing account: C1 £2,124.50, C2 £2,945.42, C2_2 £1,990.07, C3 £3,136.04, C4 £1,775.72, C5 £4,922.58, C6 £8,781.71, C7 £3,172.18, C8 £4,257.52, C9 £4,662.32, C_IC1 £738,341.63, C_IC2 £434,495.40, C_IC3 £1,359,490.91, C_IC4 £742,650.17
- Bill shock events (>=20%): 33 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (31%); C4g 2024-03-31 (23%); C4g 2024-04-30 (35%); C4g 2024-05-31 (27%); C4g 2024-06-30 (37%); C_IC1 2024-07-31 (34%); C_IC1 2024-08-31 (66%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (109%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (58%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (54%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C4 35%, C6 38%, C7 35%, C8 41%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.15-£351.48/MWh, net margin £420.55
- C4 (electricity): tariff £255.61/MWh, net margin £269.95
- C4g (gas): tariff £66.00/MWh, net margin £574.05
- C6 (electricity): tariff £333.43/MWh, net margin £491.06
- C7 (electricity): tariff £165.00-£358.28/MWh, net margin £475.31
- C8 (electricity): tariff £161.47-£397.50/MWh, net margin £329.72
- C9 (electricity): tariff £165.00-£367.01/MWh, net margin £555.44
- C_IC1 (electricity): tariff £-98.58-£334.18/MWh, net margin £131,838.14
- C_IC2 (electricity): tariff £-106.92-£358.71/MWh, net margin £73,303.03
- C_IC3 (electricity): tariff £86.86-£196.40/MWh, net margin £164,157.28
- C_IC3g (gas): tariff £61.12-£61.79/MWh, net margin £-37,199.57 -- **net-negative**
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £3,736.07

**Portfolio Health**

- Capital cost ratio: 4.2% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,641,180.86 -> £3,228,942.44 (11.3%)
- Bills issued: 129, average clarity 0.825, average bill shock 15.6%, bad debt provision £11,670.42, avg complaint probability 4.5%
- Solvency signal: £361,172/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £183,252.66 vs. naked (unhedged) net margin: £561,719.58
- hedging cost £378,466.93 vs. a fully unhedged book (commodity-only: actual net £183,252.66 vs. naked net £561,719.58)
  - C2_2: actual £93.23 vs. naked £1,032.33 -- hedging cost £939.10
  - C7: actual £-13.51 vs. naked £653.48 -- hedging cost £666.99
  - C8: actual £337.94 vs. naked £1,416.01 -- hedging cost £1,078.07
  - C9: actual £371.56 vs. naked £1,427.21 -- hedging cost £1,055.66
  - C_IC1: actual £123,598.52 vs. naked £218,723.34 -- hedging cost £95,124.82
  - C_IC2: actual £65,280.57 vs. naked £116,615.17 -- hedging cost £51,334.60
  - C_IC3: actual £15,459.83 vs. naked £116,257.58 -- hedging cost £100,797.75
  - C_IC3g: actual £-23,330.60 vs. naked £29,765.97 -- hedging cost £53,096.57
  - C_IC4: actual £1,455.13 vs. naked £75,828.50 -- hedging cost £74,373.37

**Year narrative:** 2024 produced a net gain of £338,951.03 across 12 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £96,628.85 (gross £527,635.60, capital £28,983.08)
  - Electricity: gross £474,126.82, capital £5,696.17, net £116,128.24
  - Gas: gross £53,508.78, capital £23,286.91, net £-19,499.39
- Treasury at year end: £3,666,621.81
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
- Average CLV (Point-in-Time, year-end 2025): £248,833.91
  - By billing account: C1 £2,053.34, C2 £3,026.02, C2_2 £2,055.90, C3 £3,081.73, C4 £1,768.59, C5 £4,567.10, C6 £8,758.83, C7 £3,598.16, C8 £4,091.99, C9 £4,544.44, C_IC1 £786,525.91, C_IC2 £465,099.22, C_IC3 £1,406,760.97, C_IC4 £787,742.53
- Bill shock events (>=20%): 20 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (34%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.15-£283.12/MWh, net margin £86.48
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-10.34 -- **net-negative**
- C8 (electricity): tariff £149.29-£308.26/MWh, net margin £85.05
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £194.62
- C_IC1 (electricity): tariff £169.74-£324.06/MWh, net margin £67,058.89
- C_IC2 (electricity): tariff £163.52-£312.18/MWh, net margin £31,834.52
- C_IC3 (electricity): tariff £86.86-£165.83/MWh, net margin £15,442.62
- C_IC3g (gas): tariff £61.79/MWh, net margin £-19,499.39 -- **net-negative**
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £1,436.41

**Portfolio Health**

- Capital cost ratio: 5.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 54, average clarity 0.777, average bill shock 23.6%, bad debt provision £5,016.95, avg complaint probability 5.9%
- Solvency signal: £458,328/customer (8 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £56.38 vs. naked (unhedged) net margin: £336.42
- hedging cost £280.04 vs. a fully unhedged book (commodity-only: actual net £56.38 vs. naked net £336.42)
  - C2_2: actual £83.35 vs. naked £217.75 -- hedging cost £134.40
  - C8: actual £-26.97 vs. naked £118.67 -- hedging cost £145.64

**Year narrative:** 2025 produced a net gain of £96,628.85 across 9 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 20 customer(s) experienced a bill shock of >=20%.
