# Annual Report — The Synthetic Enterprise

## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £29,846.19
- Final treasury: £15,682.78
  (£-14,163.40 net change)
- Customer bills (all-in): £148,619.03
  VAT remitted to HMRC: (£12,182.31) | Revenue (ex-VAT): £136,436.72
  Non-commodity pass-through: (£42,887.46)
- Gross margin: £-2,537.97
- Capital costs: £1,227.63
- Net margin: £-3,765.60
- Capital cost ratio: -48.4% of gross
- Net margin as % of revenue: -2.8%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 287
- Bills issued: 1117, average clarity 0.870,
  service quality score 0.920
- Enterprise value (CLV sum across 10 billing accounts): £-16,445.26
- Cost to serve (whole portfolio): £6,161.65, net margin after cost to serve: £-9,927.26
- Hedge effectiveness (whole window): hedging cost £1,656.28 vs. a fully unhedged book (commodity-only: actual net £-14,163.40 vs. naked net £-12,507.12)

- **2021** (crisis year): net margin £-2,594.39, 15 risk committee wake-up(s).
- **2022** (crisis year): net margin £-4,670.55, 67 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £-2,537.97, capital £1,227.63, net £-3,765.60. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: -9.5% (commodity basis, comparable to old model) / -48.4% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £-2,594.39 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run -2.8%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £-3,765.60
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £-12,507.12
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £1,656.28 vs. a fully unhedged book (commodity-only: actual net £-14,163.40 vs. naked net £-12,507.12)
- **Best hedging decision of the run**: C6, term starting
  2021-03-31 (hedge fraction 0.95) -- hedging
  protected £2,367.75 vs. going naked.
- **Worst hedging decision of the run**: C4g, term
  starting 2022-09-30 (hedge fraction 1.00) --
  over-hedging cost £2,864.96 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|
| 2016 | £-406.05 | £-348.69 | £66.87 | £-687.88 |
| 2017 | £-822.83 | £-883.73 | £134.28 | £-1,572.28 |
| 2018 | £-680.72 | £-686.08 | £146.18 | £-1,220.61 |
| 2019 | £-296.48 | £-138.14 | £228.00 | £-206.62 |
| 2020 | £-275.17 | £-215.46 | £140.80 | £-349.83 |
| 2021 | £-1,038.39 | £-1,398.56 | £-157.44 | £-2,594.39 |
| 2022 | £-1,380.19 | £-2,770.76 | £-519.60 | £-4,670.55 |
| 2023 | £-292.70 | £-1,589.93 | £-663.78 | £-2,546.42 |
| 2024 | £129.85 | £1.61 | £5.74 | £137.21 |
| 2025 | £0.00 | £-452.03 | £0.00 | £-452.03 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **43** renewals.  Lost (churned): **6** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8255 |
| C1 | 2018-12-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.4100 | 0.3500 | 0.7335 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6312 |
| C1 | 2019-12-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1400 | 0.5500 | 0.9370 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.4829 |
| C2 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.1400 | 0.5500 | 0.9370 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.1700 | 0.5500 | 0.9235 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0637 |
| C2_2 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.2600 | 0.3500 | 0.8310 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C2_2 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.2300 | 0.5500 | 0.8965 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4099 |
| C2_2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 134.4%
- **Average signed error:** +38.6% (over-estimates vs SIM)
- **Renewal events with estimates:** 49

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +146.9% | 153.6% |
| 2017 | 3 | -55.2% | 55.2% |
| 2018 | 3 | +14.8% | 55.0% |
| 2019 | 3 | -100.0% | 100.0% |
| 2020 | 9 | -76.4% | 76.4% |
| 2021 | 8 | +279.3% | 279.3% |
| 2022 | 6 | +197.7% | 223.8% |
| 2023 | 6 | -59.0% | 107.7% |
| 2024 | 6 | -91.1% | 91.1% |
| 2025 | 2 | +19.4% | 19.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

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
| 2016 | 17 | 20.8% | 34.2% |
| 2017 | 13 | 17.5% | 33.5% |
| 2018 | 13 | 16.6% | 41.4% |
| 2019 | 13 | 14.2% | 21.2% |
| 2020 | 12 | 21.3% | 35.0% |
| 2021 | 10 | 27.1% | 50.4% |
| 2022 | 8 | 25.2% | 31.9% |
| 2023 | 7 | 10.3% | 18.3% |
| 2024 | 6 | 18.0% | 25.7% |
| 2025 | 2 | 41.3% | 41.3% |

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
| 2016 | 3 | 1.54× | 4.51× |
| 2017 | 3 | 0.55× | 0.77× |
| 2018 | 3 | 0.55× | 1.05× |
| 2019 | 3 | 1.00× | 1.00× |
| 2020 | 9 | 0.76× | 1.00× |
| 2021 | 8 | 2.79× ⚠ | 7.64× |
| 2022 | 6 | 2.24× ⚠ | 4.59× |
| 2023 | 6 | 1.08× | 1.46× |
| 2024 | 6 | 0.91× | 1.00× |
| 2025 | 2 | 0.19× | 0.19× |

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **7** (6 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.14, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.14, company est=0.95 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.95 |
| 2022-03-31 | CHURN | C2 | SIM p=0.17, company est=0.95 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.14 |
| 2024-09-29 | CHURN | C4 | SIM p=0.23, company est=0.00 |

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

## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,842 | 40,643 | 33.6% | £6,417.17 | £6,688.00 | £157.89/MWh | £83.39/MWh | +3.0% |
| C8 | 106,723 | 46,761 | 43.8% | £6,980.97 | £4,705.76 | £149.29/MWh | £78.48/MWh | +10.0% |
| C9 | 109,388 | 46,156 | 42.2% | £5,223.29 | £3,751.31 | £113.17/MWh | £59.33/MWh | +8.7% |

Total HH revenue: £33,766.50 vs flat equivalent £31,594.62 (+6.9% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 19 | 102% | C8 (2016-10-31) |
| 2017 | 24 | 82% | C8 (2017-11-30) |
| 2018 | 32 | 54% | C8 (2018-10-31) |
| 2019 | 33 | 83% | C8 (2019-10-31) |
| 2020 | 28 | 63% | C8 (2020-10-31) |
| 2021 | 30 | 152% | C4g (2021-10-31) |
| 2022 | 37 | 1717% | C2_2 (2022-04-30) |
| 2023 | 29 | 100% | C8 (2023-10-31) |
| 2024 | 25 | 73% | C8 (2024-09-30) |
| 2025 | 17 | 80% | C7 (2025-06-07) |

Total: **274** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1717% | no |
| 2022-01-31 | C7 | +186% | no |
| 2022-10-31 | C4g | +174% | no |
| 2021-10-31 | C4g | +152% | no |
| 2016-10-31 | C8 | +102% | no |
| 2023-10-31 | C8 | +100% | no |
| 2023-10-31 | C2_2 | +95% | no |
| 2021-10-31 | C4 | +87% | yes |
| 2022-04-30 | C6 | +85% | yes |
| 2022-09-30 | C8 | +84% | no |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 8 |
| Retained | 8 (100%) |
| Churned despite offer | 0 |
| Total offer cost (foregone margin) | £197.68 |
| Margin saved (retained customers' terms) | £318.02 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£120.34** |

Missed opportunities (churns with no offer): **6** (£414.43 expected margin lost without offer)
- **Blocked — uneconomical** (churn estimate above threshold but margin < discount cost): 3 (£153.45 margin foregone)
- **Below threshold** (churn estimate under 30%): 3 (£260.97 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 3 | 3 | £96.76 | £158.50 | £61.74 | £0.00 |
| 2018 | 3 | 3 | £40.51 | £58.08 | £17.58 | £0.00 |
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £7.53 |
| 2021 | 0 | 0 | £0.00 | £0.00 | £0.00 | £135.55 |
| 2022 | 0 | 0 | £0.00 | £0.00 | £0.00 | £17.90 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £253.45 |
| 2025 | 2 | 2 | £60.41 | £101.44 | £41.03 | £0.00 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----|---------|
| 2017-04-01 | C2 | 0.30 | 3% | £5.61 | £9.20 | £3.58 | retained |
| 2017-04-01 | C6 | 0.30 | 3% | £72.17 | £118.22 | £46.05 | retained |
| 2017-04-01 | C8 | 0.30 | 3% | £18.97 | £31.08 | £12.11 | retained |
| 2018-07-01 | C3 | 0.32 | 3% | £5.81 | £8.68 | £2.87 | retained |
| 2018-07-01 | C9 | 0.32 | 3% | £22.46 | £33.56 | £11.10 | retained |
| 2018-10-01 | C4 | 0.43 | 3% | £12.23 | £15.84 | £3.60 | retained |
| 2025-03-30 | C2_2 | 0.45 | 3% | £13.79 | £23.16 | £9.37 | retained |
| 2025-03-30 | C8 | 0.45 | 3% | £46.62 | £78.28 | £31.66 | retained |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £-300.25 | — | — | — | — | £-1,289.55 | — | £-701.36 | — | — |
| 2017 | £-654.25 | £-2,119.40 | — | £-830.35 | £-51.54 | £-2,921.22 | £-4,437.33 | £-1,604.25 | £-2,026.48 | £-1,484.82 |
| 2018 | £-414.24 | £-1,757.22 | — | £-694.23 | £8.43 | £-2,001.13 | £-3,537.35 | £-1,031.21 | £-1,975.41 | £-1,531.59 |
| 2019 | £-193.25 | £-1,323.48 | — | £-499.44 | £77.67 | £-1,244.64 | £-3,398.74 | £-726.43 | £-1,496.24 | £-885.76 |
| 2020 | £-199.13 | £-988.53 | — | £-372.92 | £39.60 | £-1,073.44 | £-2,669.12 | £-605.61 | £-1,080.35 | £-773.83 |
| 2021 | £-249.26 | £-1,042.83 | — | £-318.61 | £-579.84 | £-1,418.45 | £-2,810.81 | £-693.41 | £-1,335.84 | £-835.44 |
| 2022 | £-253.42 | £-863.92 | £-429.05 | £-354.98 | £-1,706.09 | £-1,335.02 | £-3,426.94 | £-977.38 | £-1,607.59 | £-962.95 |
| 2023 | £-245.52 | £-870.25 | £-394.50 | £-346.16 | £-2,385.25 | £-1,154.77 | £-3,142.94 | £-1,337.70 | £-1,255.48 | £-759.15 |
| 2024 | £-197.85 | £-917.38 | £-328.34 | £-309.25 | £-1,800.29 | £-1,199.69 | £-2,552.25 | £-1,119.81 | £-1,203.25 | £-734.29 |
| 2025 | £-206.37 | £-813.55 | £-363.44 | £-319.47 | £-1,836.31 | £-1,131.69 | £-2,635.89 | £-1,185.46 | £-977.29 | £-720.62 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £440.12, range £23.75–£1,112.61.

- C1: cost to serve £357.58, net margin after CTS £-532.43 — **NET_NEGATIVE** (tariff uplift needed: +38.5%)
- C1g: cost to serve £37.34, net margin after CTS £215.96
- C2: cost to serve £379.48, net margin after CTS £-1,220.52 — **NET_NEGATIVE** (tariff uplift needed: +49.3%)
- C2_2: cost to serve £292.95, net margin after CTS £-813.00 — **NET_NEGATIVE** (tariff uplift needed: +13.8%)
- C2g: cost to serve £41.86, net margin after CTS £-24.52 — **NET_NEGATIVE** (tariff uplift needed: +1.4%)
- C3: cost to serve £237.60, net margin after CTS £-390.86 — **NET_NEGATIVE** (tariff uplift needed: +44.3%)
- C3g: cost to serve £23.75, net margin after CTS £86.56
- C4: cost to serve £548.98, net margin after CTS £-2,512.07 — **NET_NEGATIVE** (tariff uplift needed: +46.1%)
- C4g: cost to serve £150.89, net margin after CTS £-1,082.75 — **NET_NEGATIVE** (tariff uplift needed: +15.3%)
- C5: cost to serve £787.00, net margin after CTS £-1,657.91 — **NET_NEGATIVE** (tariff uplift needed: +24.7%)
- C6: cost to serve £1,112.61, net margin after CTS £-4,858.12 — **NET_NEGATIVE** (tariff uplift needed: +31.8%)
- C7: cost to serve £781.24, net margin after CTS £-2,699.52 — **NET_NEGATIVE** (tariff uplift needed: +20.6%)
- C8: cost to serve £739.17, net margin after CTS £-2,050.90 — **NET_NEGATIVE** (tariff uplift needed: +17.5%)
- C9: cost to serve £671.21, net margin after CTS £-1,557.35 — **NET_NEGATIVE** (tariff uplift needed: +17.4%)

**Activity-Based Pricing Actions**

The following 12 customer(s) are loss-making after cost-to-serve and require immediate tariff review:
  - C1: net margin after CTS £-532.43 on revenue £1,382.46 — raise tariff by ≥38.5% to break even
  - C2: net margin after CTS £-1,220.52 on revenue £2,477.30 — raise tariff by ≥49.3% to break even
  - C2_2: net margin after CTS £-813.00 on revenue £5,872.78 — raise tariff by ≥13.8% to break even
  - C2g: net margin after CTS £-24.52 on revenue £1,749.07 — raise tariff by ≥1.4% to break even
  - C3: net margin after CTS £-390.86 on revenue £882.50 — raise tariff by ≥44.3% to break even
  - C4: net margin after CTS £-2,512.07 on revenue £5,454.65 — raise tariff by ≥46.1% to break even
  - C4g: net margin after CTS £-1,082.75 on revenue £7,085.92 — raise tariff by ≥15.3% to break even
  - C5: net margin after CTS £-1,657.91 on revenue £6,715.21 — raise tariff by ≥24.7% to break even
  - C6: net margin after CTS £-4,858.12 on revenue £15,283.46 — raise tariff by ≥31.8% to break even
  - C7: net margin after CTS £-2,699.52 on revenue £13,105.17 — raise tariff by ≥20.6% to break even
  - C8: net margin after CTS £-2,050.90 on revenue £11,686.73 — raise tariff by ≥17.5% to break even
  - C9: net margin after CTS £-1,557.35 on revenue £8,974.60 — raise tariff by ≥17.4% to break even

## Transaction Log

Total events: 2,238,162

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 5 |
| bad_debt_event | 1,117 |
| billing_event | 1,117 |
| capital_charge_event | 1,019,177 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,117 |
| payment_received_event | 1,117 |
| settlement_event | 1,213,281 |
| vat_remittance_event | 1,117 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £148,619.03 |
|   Less: VAT remitted to HMRC | (£12,182.31) |
| = Revenue (ex-VAT) | £136,436.72 |
| Less: non-commodity pass-through | (£42,887.46) |
| Wholesale cost (settlement events) | (£96,087.24) |
| Gross margin | £-2,537.97 |
| Capital charges | (£1,227.63) |
| Net margin | £-3,765.60 |

_Cash reconciliation: of £148,619.03 billed, bad debt of £2,916.61 was written off, leaving £145,702.42 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £5,500.09._

| Acquisition spend | (£1,250.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £-10,715.60 |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 1 | 0 | 0% | £150.00 |
| 2021 | 2 | 0 | 0% | £550.00 |
| 2024 | 2 | 0 | 0% | £550.00 |

**Total:** 5 attempts, 0 wins (0% win rate), £1,250.00 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £-10,715.60

## 2016

**Trading & Risk**

- Net margin: £-687.88 (gross £-494.14, capital £193.74)
  - Electricity: gross £-567.33, capital £187.42, net £-754.75
  - Gas: gross £73.19, capital £6.32, net £66.87
- Treasury at year end: £29,506.37
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.90), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.90), C6 0.85 (avg 0.85), C7 0.85 (avg 0.90), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 81
  - 2016-01-01: treasury £29,846.19, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-31: treasury £29,843.47, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-01: treasury £29,840.85, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-31: treasury £29,838.18, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-04-30: treasury £29,836.08, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-05-30: treasury £29,834.25, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-06-29: treasury £29,832.18, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-07-29: treasury £29,830.28, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-08-28: treasury £29,828.47, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-09-27: treasury £29,826.18, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-10-27: treasury £29,823.65, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-11-26: treasury £29,819.16, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-12-26: treasury £29,816.08, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-18: treasury £29,834.05, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-02-17: treasury £29,816.45, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-03-18: treasury £29,797.80, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-04-17: treasury £29,783.88, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-05-17: treasury £29,770.95, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-06-16: treasury £29,760.76, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-07-16: treasury £29,751.21, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-08-15: treasury £29,742.21, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-09-14: treasury £29,731.74, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-10-14: treasury £29,719.29, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-11-13: treasury £29,697.93, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-12-13: treasury £29,674.41, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-01-13: treasury £29,660.24, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-02-12: treasury £29,654.09, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-03-13: treasury £29,646.17, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-12: treasury £29,640.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-05-12: treasury £29,633.34, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-06-11: treasury £29,627.07, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-07-11: treasury £29,619.55, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-08-10: treasury £29,612.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-09-09: treasury £29,605.47, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-10-09: treasury £29,597.45, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-11-08: treasury £29,588.19, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-12-08: treasury £29,575.56, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-08: treasury £29,569.01, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-05-08: treasury £29,562.42, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-06-07: treasury £29,556.46, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-07-07: treasury £29,550.17, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-06: treasury £29,544.16, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-09-05: treasury £29,538.28, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-10-05: treasury £29,531.55, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-11-04: treasury £29,523.93, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-12-04: treasury £29,513.98, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-05: treasury £29,480.75, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-04-26: treasury £29,454.83, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-05-26: treasury £29,432.91, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-06-25: treasury £29,415.18, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-07-25: treasury £29,398.16, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-08-24: treasury £29,382.86, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-09-23: treasury £29,365.13, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-10-23: treasury £29,342.02, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-11-22: treasury £29,302.74, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-12-22: treasury £29,268.06, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-04-21: treasury £29,147.01, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-05-21: treasury £29,137.94, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-06-20: treasury £29,132.12, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-20: treasury £29,126.92, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-08-19: treasury £29,122.44, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-09-18: treasury £29,116.92, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-10-18: treasury £29,108.19, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-11-17: treasury £29,093.63, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-12-17: treasury £29,075.55, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-16: treasury £29,023.96, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-08-15: treasury £29,021.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-09-14: treasury £29,019.25, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-10-14: treasury £29,016.39, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-11-13: treasury £29,012.22, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-12-13: treasury £29,007.55, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-07-03: treasury £29,010.54, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-08-02: treasury £29,007.04, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-09-01: treasury £29,003.91, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-01: treasury £28,999.75, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-31: treasury £28,993.11, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-11-30: treasury £28,979.59, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-12-30: treasury £28,972.85, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-28: treasury £28,931.47, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-11-27: treasury £28,925.82, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-12-27: treasury £28,922.02, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.03
- Worst single period: C8 on 2016-11-20 period 36, net margin £-0.52

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £-763.72
  - By billing account: C1 £-300.25, C5 £-1,289.55, C7 £-701.36
- Bill shock events (>=20%): 19 -- C5 2016-05-31 (26%); C5 2016-10-31 (40%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (77%); C7 2016-11-30 (51%); C6 2016-05-31 (25%); C6 2016-06-30 (22%); C6 2016-10-31 (39%); C6 2016-11-30 (44%); C8 2016-05-31 (40%); C8 2016-06-30 (41%); C8 2016-09-30 (22%); C8 2016-10-31 (102%); C8 2016-11-30 (68%); C9 2016-10-31 (76%); C9 2016-11-30 (58%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £50.87-£62.66/MWh, net margin £-31.27 -- **net-negative**
- C1g (gas): tariff £16.64-£17.77/MWh, net margin £29.08
- C2 (electricity): tariff £42.33/MWh, net margin £-64.22 -- **net-negative**
- C2g (gas): tariff £15.29/MWh, net margin £-1.17 -- **net-negative**
- C3 (electricity): tariff £40.64/MWh, net margin £-19.79 -- **net-negative**
- C3g (gas): tariff £13.52/MWh, net margin £14.24
- C4 (electricity): tariff £47.02/MWh, net margin £-12.89 -- **net-negative**
- C4g (gas): tariff £16.78/MWh, net margin £24.72
- C5 (electricity): tariff £50.87-£62.66/MWh, net margin £-185.00 -- **net-negative**
- C6 (electricity): tariff £42.33/MWh, net margin £-221.05 -- **net-negative**
- C7 (electricity): tariff £39.97-£76.30/MWh, net margin £-95.36 -- **net-negative**
- C8 (electricity): tariff £33.26-£63.49/MWh, net margin £-86.27 -- **net-negative**
- C9 (electricity): tariff £31.93-£60.96/MWh, net margin £-38.90 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -39.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.893, average bill shock 13.2%, bad debt provision £200.48, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,755.41 vs. naked (unhedged) net margin: £-1,734.56
- hedging cost £20.85 vs. a fully unhedged book (commodity-only: actual net £-1,755.41 vs. naked net £-1,734.56)
  - C1: actual £-131.90 vs. naked £-19.98 -- hedging cost £111.92
  - C1g: actual £65.95 vs. naked £60.54 -- hedging added £5.41
  - C2: actual £-89.63 vs. naked £-31.83 -- hedging cost £57.79
  - C2g: actual £-3.80 vs. naked £24.74 -- hedging cost £28.54
  - C3: actual £-39.35 vs. naked £-54.62 -- hedging added £15.27
  - C3g: actual £25.38 vs. naked £-5.87 -- hedging added £31.25
  - C4: actual £-43.02 vs. naked £-28.66 -- hedging cost £14.36
  - C4g: actual £92.26 vs. naked £40.58 -- hedging added £51.67
  - C5: actual £-682.36 vs. naked £-555.31 -- hedging cost £127.05
  - C6: actual £-322.69 vs. naked £-636.07 -- hedging added £313.38
  - C7: actual £-419.93 vs. naked £-142.77 -- hedging cost £277.16
  - C8: actual £-129.40 vs. naked £-194.21 -- hedging added £64.81
  - C9: actual £-76.90 vs. naked £-191.07 -- hedging added £114.17

**Year narrative:** 2016 produced a net loss of £-687.88 across 13 accounts. The risk committee intervened 81 time(s), raising hedge fractions in response to elevated VaR. 19 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £-1,572.28 (gross £-1,442.20, capital £130.07)
  - Electricity: gross £-1,586.45, capital £120.11, net £-1,706.56
  - Gas: gross £144.24, capital £9.96, net £134.28
- Treasury at year end: £28,018.07
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.95 (avg 0.95), C3g 0.95 (avg 0.95), C4 0.85 (avg 0.85), C4g 0.95 (avg 0.95), C5 0.85 (avg 0.85), C6 0.95 (avg 0.95), C7 0.85 (avg 0.85), C8 0.95 (avg 0.95), C9 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 42
  - 2017-01-03: treasury £29,505.63, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-02-02: treasury £29,496.44, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-03-04: treasury £29,487.93, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-01-21: treasury £29,231.48, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-02-20: treasury £29,193.52, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-03-22: treasury £29,163.61, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-01-16: treasury £29,059.28, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-02-15: treasury £29,041.17, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-03-17: treasury £29,030.22, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-01-12: treasury £29,003.79, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-02-11: treasury £28,999.31, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-03-13: treasury £28,995.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-04-12: treasury £28,992.95, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-05-12: treasury £28,990.08, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-06-11: treasury £28,987.27, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-01-29: treasury £28,962.00, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-02-28: treasury £28,954.24, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-03-30: treasury £28,948.58, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-04-29: treasury £28,943.46, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-05-29: treasury £28,937.66, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-06-28: treasury £28,934.25, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-01-26: treasury £28,917.47, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-02-25: treasury £28,913.23, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-03-27: treasury £28,909.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-04-26: treasury £28,907.04, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-05-26: treasury £28,903.37, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-06-25: treasury £28,900.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-07-25: treasury £28,898.18, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-08-24: treasury £28,895.44, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-09-23: treasury £28,892.06, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-01-15: treasury £28,978.28, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-02-14: treasury £28,968.32, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-03-16: treasury £28,958.64, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-04-15: treasury £28,950.43, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-05-15: treasury £28,942.83, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-06-14: treasury £28,935.95, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-07-14: treasury £28,929.10, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-08-13: treasury £28,922.35, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-09-12: treasury £28,915.28, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-10-12: treasury £28,907.42, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-11-11: treasury £28,898.80, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-12-11: treasury £28,888.90, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C5 on 2017-01-23 period 19, net margin £-0.17

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £-1,792.18
  - By billing account: C1 £-654.25, C2 £-2,119.40, C3 £-830.35, C4 £-51.54, C5 £-2,921.22, C6 £-4,437.33, C7 £-1,604.25, C8 £-2,026.48, C9 £-1,484.82
- Bill shock events (>=20%): 24 -- C5 2017-01-31 (28%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (35%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (26%); C7 2017-10-31 (21%); C7 2017-11-30 (75%); C6 2017-05-31 (21%); C6 2017-11-30 (48%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (44%); C8 2017-10-31 (22%); C8 2017-11-30 (82%); C8 2017-12-31 (22%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): 5 at risk (≥20% churn prob): C5 29%, C6 35%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £62.66-£63.33/MWh, net margin £-100.88 -- **net-negative**
- C1g (gas): tariff £17.77-£25.08/MWh, net margin £36.94
- C2 (electricity): tariff £42.33-£53.46/MWh, net margin £-98.11 -- **net-negative**
- C2g (gas): tariff £15.29-£18.03/MWh, net margin £-19.29 -- **net-negative**
- C3 (electricity): tariff £40.64-£46.60/MWh, net margin £-62.30 -- **net-negative**
- C3g (gas): tariff £13.52-£16.31/MWh, net margin £24.80
- C4 (electricity): tariff £47.02-£51.78/MWh, net margin £-35.88 -- **net-negative**
- C4g (gas): tariff £16.78-£21.34/MWh, net margin £91.83
- C5 (electricity): tariff £62.66-£63.33/MWh, net margin £-499.55 -- **net-negative**
- C6 (electricity): tariff £42.33-£53.46/MWh, net margin £-323.28 -- **net-negative**
- C7 (electricity): tariff £49.23-£93.98/MWh, net margin £-326.16 -- **net-negative**
- C8 (electricity): tariff £33.26-£80.19/MWh, net margin £-131.44 -- **net-negative**
- C9 (electricity): tariff £31.93-£69.90/MWh, net margin £-128.96 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -9.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.898, average bill shock 11.0%, bad debt provision £301.37, avg complaint probability 3.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-824.23 vs. naked (unhedged) net margin: £-1,309.41
- hedging added £485.17 vs. a fully unhedged book (commodity-only: actual net £-824.23 vs. naked net £-1,309.41)
  - C1: actual £-7.25 vs. naked £-13.00 -- hedging added £5.75
  - C1g: actual £55.42 vs. naked £26.13 -- hedging added £29.29
  - C2: actual £-103.60 vs. naked £-0.20 -- hedging cost £103.40
  - C2g: actual £-24.99 vs. naked £-2.62 -- hedging cost £22.37
  - C3: actual £-87.03 vs. naked £-63.81 -- hedging cost £23.21
  - C3g: actual £25.77 vs. naked £-41.39 -- hedging added £67.15
  - C4: actual £-26.63 vs. naked £-64.06 -- hedging added £37.43
  - C4g: actual £93.72 vs. naked £-1.20 -- hedging added £94.92
  - C5: actual £-51.99 vs. naked £-175.42 -- hedging added £123.43
  - C6: actual £-343.20 vs. naked £-585.21 -- hedging added £242.01
  - C7: actual £-7.97 vs. naked £-45.03 -- hedging added £37.06
  - C8: actual £-143.81 vs. naked £-117.69 -- hedging cost £26.12
  - C9: actual £-202.69 vs. naked £-225.93 -- hedging added £23.24

**Year narrative:** 2017 produced a net loss of £-1,572.28 across 13 accounts. The risk committee intervened 42 time(s), raising hedge fractions in response to elevated VaR. 24 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £-1,220.61 (gross £-1,119.24, capital £101.37)
  - Electricity: gross £-1,272.59, capital £94.21, net £-1,366.80
  - Gas: gross £153.35, capital £7.16, net £146.18
- Treasury at year end: £27,083.14
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.95 (avg 0.95), C1g 1.00 (avg 1.00), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.95 (avg 0.95), C4g 1.00 (avg 1.00), C5 0.95 (avg 0.95), C6 1.00 (avg 1.00), C7 0.95 (avg 0.95), C8 0.85 (avg 0.85), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C7 on 2018-03-01 period 43, net margin £-0.31

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2018): £-1,437.11
  - By billing account: C1 £-414.24, C2 £-1,757.22, C3 £-694.23, C4 £8.43, C5 £-2,001.13, C6 £-3,537.35, C7 £-1,031.21, C8 £-1,975.41, C9 £-1,531.59
- Bill shock events (>=20%): 32 -- C5 2018-04-30 (32%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (28%); C7 2018-10-31 (45%); C7 2018-11-30 (32%); C6 2018-04-30 (20%); C6 2018-05-31 (21%); C6 2018-06-30 (21%); C6 2018-10-31 (29%); C6 2018-11-30 (21%); C8 2018-04-30 (31%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (24%); C8 2018-09-30 (51%); C8 2018-10-31 (54%); C8 2018-11-30 (29%); C3g 2018-07-31 (27%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-08-31 (40%); C9 2018-09-30 (43%); C9 2018-10-31 (39%); C9 2018-12-31 (20%); C4 2018-10-31 (25%); C4g 2018-10-31 (32%)
- Churn risk (accounts renewing in 2018): 5 at risk (≥20% churn prob): C5 41%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £63.33-£80.48/MWh, net margin £-7.00 -- **net-negative**
- C1g (gas): tariff £25.08-£32.50/MWh, net margin £55.63
- C2 (electricity): tariff £53.46-£65.98/MWh, net margin £-214.29 -- **net-negative**
- C2g (gas): tariff £18.03-£23.57/MWh, net margin £-36.73 -- **net-negative**
- C3 (electricity): tariff £46.60-£60.53/MWh, net margin £-54.50 -- **net-negative**
- C3g (gas): tariff £16.31-£23.79/MWh, net margin £30.23
- C4 (electricity): tariff £51.78-£74.14/MWh, net margin £-19.14 -- **net-negative**
- C4g (gas): tariff £21.34-£31.24/MWh, net margin £97.05
- C5 (electricity): tariff £63.33-£80.48/MWh, net margin £-49.99 -- **net-negative**
- C6 (electricity): tariff £53.46-£65.98/MWh, net margin £-630.73 -- **net-negative**
- C7 (electricity): tariff £49.76-£120.72/MWh, net margin £-5.76 -- **net-negative**
- C8 (electricity): tariff £42.01-£98.98/MWh, net margin £-275.50 -- **net-negative**
- C9 (electricity): tariff £36.61-£90.79/MWh, net margin £-109.88 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -9.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.898, average bill shock 10.8%, bad debt provision £329.49, avg complaint probability 3.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-890.34 vs. naked (unhedged) net margin: £1,206.17
- hedging cost £2,096.51 vs. a fully unhedged book (commodity-only: actual net £-890.34 vs. naked net £1,206.17)
  - C1: actual £25.11 vs. naked £111.83 -- hedging cost £86.72
  - C1g: actual £101.91 vs. naked £221.75 -- hedging cost £119.84
  - C2: actual £-250.02 vs. naked £32.03 -- hedging cost £282.05
  - C2g: actual £-34.94 vs. naked £19.60 -- hedging cost £54.54
  - C3: actual £-15.60 vs. naked £2.27 -- hedging cost £17.87
  - C3g: actual £35.95 vs. naked £56.17 -- hedging cost £20.22
  - C4: actual £11.41 vs. naked £154.20 -- hedging cost £142.79
  - C4g: actual £109.57 vs. naked £318.15 -- hedging cost £208.58
  - C5: actual £116.37 vs. naked £431.01 -- hedging cost £314.64
  - C6: actual £-772.58 vs. naked £-500.83 -- hedging cost £271.76
  - C7: actual £115.85 vs. naked £383.02 -- hedging cost £267.17
  - C8: actual £-345.78 vs. naked £-32.04 -- hedging cost £313.74
  - C9: actual £12.41 vs. naked £8.99 -- hedging added £3.42

**Year narrative:** 2018 produced a net loss of £-1,220.61 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 32 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £-206.62 (gross £-141.21, capital £65.42)
  - Electricity: gross £-374.83, capital £59.79, net £-434.62
  - Gas: gross £233.63, capital £5.63, net £228.00
- Treasury at year end: £26,334.29
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.90 (avg 0.90), C4 0.85 (avg 0.85), C4g 0.90 (avg 0.90), C5 0.85 (avg 0.85), C6 0.90 (avg 0.90), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C8 on 2019-02-02 period 36, net margin £-0.22

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2019): £-1,076.70
  - By billing account: C1 £-193.25, C2 £-1,323.48, C3 £-499.44, C4 £77.67, C5 £-1,244.64, C6 £-3,398.74, C7 £-726.43, C8 £-1,496.24, C9 £-885.76
- Bill shock events (>=20%): 33 -- C1 2019-04-30 (21%); C5 2019-01-31 (36%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (69%); C7 2019-11-30 (44%); C6 2019-02-28 (21%); C6 2019-04-30 (23%); C6 2019-06-30 (24%); C6 2019-10-31 (40%); C6 2019-11-30 (26%); C8 2019-01-31 (26%); C8 2019-02-28 (27%); C8 2019-04-30 (27%); C8 2019-06-30 (38%); C8 2019-07-31 (34%); C8 2019-09-30 (56%); C8 2019-10-31 (83%); C8 2019-11-30 (37%); C9 2019-02-28 (26%); C9 2019-04-30 (23%); C9 2019-06-30 (36%); C9 2019-07-31 (37%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (37%); C4g 2019-10-31 (36%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C3 23%, C5 38%, C6 29%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £49.82-£80.48/MWh, net margin £24.91
- C1g (gas): tariff £15.79-£32.50/MWh, net margin £101.60
- C2 (electricity): tariff £61.44-£65.98/MWh, net margin £-108.53 -- **net-negative**
- C2g (gas): tariff £20.74-£23.57/MWh, net margin £-2.92 -- **net-negative**
- C3 (electricity): tariff £48.52-£60.53/MWh, net margin £-18.19 -- **net-negative**
- C3g (gas): tariff £14.82-£23.79/MWh, net margin £26.14
- C4 (electricity): tariff £49.31-£74.14/MWh, net margin £12.72
- C4g (gas): tariff £13.99-£31.24/MWh, net margin £103.18
- C5 (electricity): tariff £49.82-£80.48/MWh, net margin £114.94
- C6 (electricity): tariff £61.44-£65.98/MWh, net margin £-411.42 -- **net-negative**
- C7 (electricity): tariff £39.14-£120.72/MWh, net margin £114.84
- C8 (electricity): tariff £48.27-£98.98/MWh, net margin £-154.23 -- **net-negative**
- C9 (electricity): tariff £38.12-£90.79/MWh, net margin £-9.68 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -46.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.892, average bill shock 12.6%, bad debt provision £348.81, avg complaint probability 3.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-285.14 vs. naked (unhedged) net margin: £1,303.05
- hedging cost £1,588.19 vs. a fully unhedged book (commodity-only: actual net £-285.14 vs. naked net £1,303.05)
  - C1: actual £-9.57 vs. naked £24.23 -- hedging cost £33.79
  - C1g: actual £31.78 vs. naked £73.69 -- hedging cost £41.92
  - C2: actual £-55.91 vs. naked £157.16 -- hedging cost £213.07
  - C2g: actual £5.90 vs. naked £135.61 -- hedging cost £129.71
  - C3: actual £-22.74 vs. naked £43.39 -- hedging cost £66.14
  - C3g: actual £18.84 vs. naked £76.42 -- hedging cost £57.58
  - C4: actual £17.80 vs. naked £95.69 -- hedging cost £77.89
  - C4g: actual £91.22 vs. naked £118.47 -- hedging cost £27.25
  - C5: actual £-56.92 vs. naked £33.19 -- hedging cost £90.11
  - C6: actual £-212.96 vs. naked £108.07 -- hedging cost £321.03
  - C7: actual £-17.51 vs. naked £82.21 -- hedging cost £99.72
  - C8: actual £-34.59 vs. naked £227.20 -- hedging cost £261.79
  - C9: actual £-40.49 vs. naked £127.70 -- hedging cost £168.20

**Year narrative:** 2019 produced a net loss of £-206.62 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-349.83 (gross £-231.83, capital £118.00)
  - Electricity: gross £-379.99, capital £110.64, net £-490.63
  - Gas: gross £148.16, capital £7.35, net £140.80
- Treasury at year end: £26,048.91
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2020-03-04 period 37, net margin £-1.00

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C3
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £-858.15
  - By billing account: C1 £-199.13, C2 £-988.53, C3 £-372.92, C4 £39.60, C5 £-1,073.44, C6 £-2,669.12, C7 £-605.61, C8 £-1,080.35, C9 £-773.83
- Bill shock events (>=20%): 28 -- C1g 2020-01-31 (33%); C5 2020-01-31 (23%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-01-31 (23%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (26%); C7 2020-10-31 (58%); C7 2020-11-30 (22%); C7 2020-12-31 (34%); C2 2020-04-30 (25%); C6 2020-04-30 (37%); C6 2020-10-31 (32%); C6 2020-12-31 (25%); C8 2020-04-30 (45%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (49%); C8 2020-10-31 (63%); C8 2020-12-31 (41%); C9 2020-04-30 (28%); C9 2020-05-31 (24%); C9 2020-06-30 (35%); C9 2020-09-30 (41%); C9 2020-10-31 (48%); C9 2020-12-31 (34%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 23%, C4 20%, C5 38%, C6 38%, C7 32%, C8 38%, C9 41%

**Pricing & Margin**

- C1 (electricity): tariff £49.82-£59.78/MWh, net margin £-10.11 -- **net-negative**
- C1g (gas): tariff £15.79-£19.17/MWh, net margin £31.82
- C2 (electricity): tariff £44.50-£61.44/MWh, net margin £-56.14 -- **net-negative**
- C2g (gas): tariff £14.20-£20.74/MWh, net margin £41.07
- C3 (electricity): tariff £48.52/MWh, net margin £-9.94 -- **net-negative**
- C3g (gas): tariff £14.82/MWh, net margin £10.53
- C4 (electricity): tariff £39.05-£49.31/MWh, net margin £-11.70 -- **net-negative**
- C4g (gas): tariff £8.93-£13.99/MWh, net margin £57.38
- C5 (electricity): tariff £49.82-£59.78/MWh, net margin £-61.40 -- **net-negative**
- C6 (electricity): tariff £44.50-£61.44/MWh, net margin £-213.77 -- **net-negative**
- C7 (electricity): tariff £39.14-£89.66/MWh, net margin £-19.17 -- **net-negative**
- C8 (electricity): tariff £34.96-£92.15/MWh, net margin £-50.15 -- **net-negative**
- C9 (electricity): tariff £24.28-£72.77/MWh, net margin £-58.24 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -50.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 144, average clarity 0.891, average bill shock 11.3%, bad debt provision £261.42, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,381.03 vs. naked (unhedged) net margin: £-4,978.66
- hedging added £3,597.64 vs. a fully unhedged book (commodity-only: actual net £-1,381.03 vs. naked net £-4,978.66)
  - C1: actual £-72.62 vs. naked £-277.91 -- hedging added £205.29
  - C1g: actual £-11.30 vs. naked £-292.59 -- hedging added £281.29
  - C2: actual £-65.35 vs. naked £-15.78 -- hedging cost £49.56
  - C2g: actual £46.38 vs. naked £37.69 -- hedging added £8.69
  - C4: actual £-126.66 vs. naked £-298.52 -- hedging added £171.86
  - C4g: actual £-85.23 vs. naked £-367.67 -- hedging added £282.44
  - C5: actual £-386.91 vs. naked £-1,552.88 -- hedging added £1,165.98
  - C6: actual £-248.44 vs. naked £-535.67 -- hedging added £287.23
  - C7: actual £-231.05 vs. naked £-934.08 -- hedging added £703.03
  - C8: actual £-92.56 vs. naked £-212.64 -- hedging added £120.08
  - C9: actual £-107.29 vs. naked £-528.60 -- hedging added £421.31

**Year narrative:** 2020 produced a net loss of £-349.83 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 28 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-2,594.39 (gross £-2,398.45, capital £195.95)
  - Electricity: gross £-2,249.09, capital £187.87, net £-2,436.95
  - Gas: gross £-149.36, capital £8.08, net £-157.44
- Treasury at year end: £24,488.61
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C4 0.95 (avg 0.95), C4g 0.95 (avg 0.95), C6 0.95 (avg 0.95), C7 0.95 (avg 0.95), C8 0.95 (avg 0.95), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 15
  - 2021-08-01: treasury £23,464.88, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-08-31: treasury £23,452.08, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-09-30: treasury £23,435.95, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-10-30: treasury £23,409.66, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-11-29: treasury £23,361.75, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-12-29: treasury £23,307.48, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-07-28: treasury £23,141.98, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-08-27: treasury £23,129.54, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-09-26: treasury £23,114.81, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-10-26: treasury £23,092.95, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-11-25: treasury £23,063.51, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-12-25: treasury £23,021.95, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-10-23: treasury £22,785.10, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-11-22: treasury £22,708.12, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-12-22: treasury £22,626.76, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.44
- Worst single period: C5 on 2021-01-08 period 39, net margin £-2.16

**Customer Book**

- Active accounts: 11 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2021): £-1,031.61
  - By billing account: C1 £-249.26, C2 £-1,042.83, C3 £-318.61, C4 £-579.84, C5 £-1,418.45, C6 £-2,810.81, C7 £-693.41, C8 £-1,335.84, C9 £-835.44
- Bill shock events (>=20%): 30 -- C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (21%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (53%); C7 2021-11-30 (62%); C2g 2021-04-30 (29%); C6 2021-04-30 (24%); C6 2021-06-30 (35%); C6 2021-10-31 (26%); C6 2021-11-30 (48%); C8 2021-04-30 (27%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (66%); C8 2021-11-30 (80%); C9 2021-02-28 (22%); C9 2021-05-31 (23%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (60%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-10-31 (87%); C4g 2021-10-31 (152%)
- Churn risk (accounts renewing in 2021): 6 at risk (≥20% churn prob): C2 20%, C5 35%, C6 38%, C7 35%, C8 41%, C9 35%

**Pricing & Margin**

- C1 (electricity): tariff £59.78/MWh, net margin £-71.88 -- **net-negative**
- C1g (gas): tariff £19.17/MWh, net margin £-11.32 -- **net-negative**
- C2 (electricity): tariff £44.50-£79.15/MWh, net margin £-244.62 -- **net-negative**
- C2g (gas): tariff £14.20-£24.78/MWh, net margin £19.64
- C4 (electricity): tariff £39.05-£129.35/MWh, net margin £-338.88 -- **net-negative**
- C4g (gas): tariff £8.93-£44.97/MWh, net margin £-165.76 -- **net-negative**
- C5 (electricity): tariff £59.78/MWh, net margin £-380.81 -- **net-negative**
- C6 (electricity): tariff £44.50-£79.15/MWh, net margin £-657.58 -- **net-negative**
- C7 (electricity): tariff £46.97-£356.98/MWh, net margin £-233.13 -- **net-negative**
- C8 (electricity): tariff £34.96-£118.73/MWh, net margin £-303.44 -- **net-negative**
- C9 (electricity): tariff £24.28-£119.84/MWh, net margin £-206.60 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -8.2% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £26,072.10 -> £21,566.29 (17.3%)
- Bills issued: 132, average clarity 0.879, average bill shock 14.4%, bad debt provision £268.77, avg complaint probability 3.9%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-3,624.47 vs. naked (unhedged) net margin: £-10,199.93
- hedging added £6,575.46 vs. a fully unhedged book (commodity-only: actual net £-3,624.47 vs. naked net £-10,199.93)
  - C2: actual £-320.16 vs. naked £-587.96 -- hedging added £267.80
  - C2g: actual £9.49 vs. naked £-547.32 -- hedging added £556.81
  - C4: actual £-886.73 vs. naked £-884.11 -- hedging cost £2.63
  - C4g: actual £-384.42 vs. naked £-1,383.56 -- hedging added £999.15
  - C6: actual £-838.45 vs. naked £-3,206.20 -- hedging added £2,367.75
  - C7: actual £-484.86 vs. naked £-509.84 -- hedging added £24.98
  - C8: actual £-408.45 vs. naked £-1,488.67 -- hedging added £1,080.21
  - C9: actual £-310.89 vs. naked £-1,592.28 -- hedging added £1,281.39

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-2,594.39 across 11 accounts. The risk committee intervened 15 time(s), raising hedge fractions in response to elevated VaR. 30 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £-4,670.55 (gross £-4,560.50, capital £110.05)
  - Electricity: gross £-4,045.55, capital £105.40, net £-4,150.95
  - Gas: gross £-514.95, capital £4.65, net £-519.60
- Treasury at year end: £20,610.89
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 1.00 (avg 1.00), C4g 1.00 (avg 1.00), C6 1.00 (avg 1.00), C7 1.00 (avg 1.00), C8 1.00 (avg 1.00), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 67
  - 2022-01-28: treasury £23,252.44, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2022-02-27: treasury £23,202.41, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2022-03-29: treasury £23,154.36, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2022-01-24: treasury £22,985.06, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-02-23: treasury £22,949.14, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-03-25: treasury £22,914.35, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-04-24: treasury £22,882.82, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-05-24: treasury £22,862.39, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-06-23: treasury £22,844.58, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-01-21: treasury £22,547.55, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-02-20: treasury £22,467.73, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-03-22: treasury £22,386.58, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-04-21: treasury £22,315.95, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-05-21: treasury £22,249.48, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-06-20: treasury £22,185.50, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-07-20: treasury £22,119.27, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-08-19: treasury £22,051.53, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-09-18: treasury £21,980.83, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-01-10: treasury £21,550.52, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-02-09: treasury £21,507.85, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-03-11: treasury £21,462.66, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-10: treasury £21,413.45, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-05-10: treasury £21,377.51, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-06-09: treasury £21,345.44, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-07-09: treasury £21,312.16, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-08-08: treasury £21,276.43, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-09-07: treasury £21,238.76, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-10-07: treasury £21,202.60, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-11-06: treasury £21,167.67, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-06: treasury £21,127.27, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-06: treasury £21,061.61, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-05-06: treasury £21,004.34, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-06-05: treasury £20,971.65, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-07-05: treasury £20,946.65, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-08-04: treasury £20,923.63, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-09-03: treasury £20,896.29, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-10-03: treasury £20,853.20, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-11-02: treasury £20,815.28, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-02: treasury £20,744.82, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-01: treasury £20,351.25, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-05-01: treasury £20,210.56, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-05-31: treasury £20,104.30, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-06-30: treasury £20,014.65, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-07-30: treasury £19,934.55, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-08-29: treasury £19,858.82, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-09-28: treasury £19,761.00, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-10-28: treasury £19,650.76, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-11-27: treasury £19,500.99, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-12-27: treasury £19,287.54, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-04-27: treasury £18,646.78, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-05-27: treasury £18,605.56, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-06-26: treasury £18,567.90, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-07-26: treasury £18,541.24, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-08-25: treasury £18,516.26, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-09-24: treasury £18,484.81, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-10-24: treasury £18,431.76, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-11-23: treasury £18,372.06, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-12-23: treasury £18,273.08, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-07-22: treasury £17,977.10, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-08-21: treasury £17,969.66, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-09-20: treasury £17,961.98, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-10-20: treasury £17,956.00, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-11-19: treasury £17,952.98, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-12-19: treasury £17,948.16, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-10-17: treasury £17,881.01, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2022-11-16: treasury £17,805.06, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2022-12-16: treasury £17,724.83, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.49
- Worst single period: C4g on 2022-09-30 period 1, net margin £-2.43

**Customer Book**

- Active accounts: 9 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2022): £-1,191.73
  - By billing account: C1 £-253.42, C2 £-863.92, C2_2 £-429.05, C3 £-354.98, C4 £-1,706.09, C5 £-1,335.02, C6 £-3,426.94, C7 £-977.38, C8 £-1,607.59, C9 £-962.95
- Bill shock events (>=20%): 37 -- C7 2022-01-31 (186%); C7 2022-02-28 (27%); C7 2022-04-30 (23%); C7 2022-05-31 (37%); C7 2022-06-30 (27%); C7 2022-09-30 (35%); C7 2022-11-30 (65%); C7 2022-12-31 (54%); C6 2022-04-30 (85%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-04-30 (70%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (84%); C8 2022-11-30 (72%); C8 2022-12-31 (57%); C9 2022-04-30 (21%); C9 2022-05-31 (29%); C9 2022-06-30 (28%); C9 2022-07-31 (35%); C9 2022-09-30 (49%); C9 2022-10-31 (31%); C9 2022-11-30 (45%); C9 2022-12-31 (53%); C4 2022-10-31 (81%); C4g 2022-10-31 (174%); C2_2 2022-04-30 (1717%); C2_2 2022-05-31 (39%); C2_2 2022-06-30 (33%); C2_2 2022-09-30 (76%); C2_2 2022-11-30 (65%); C2_2 2022-12-31 (57%)
- Churn risk (accounts renewing in 2022): 5 at risk (≥20% churn prob): C4 23%, C6 35%, C7 38%, C8 35%, C9 38%

**Pricing & Margin**

- C2 (electricity): tariff £79.15/MWh, net margin £-98.74 -- **net-negative**
- C2_2 (electricity): tariff £257.61/MWh, net margin £-474.67 -- **net-negative**
- C2g (gas): tariff £24.78/MWh, net margin £-2.55 -- **net-negative**
- C4 (electricity): tariff £129.35-£280.79/MWh, net margin £-886.63 -- **net-negative**
- C4g (gas): tariff £44.97-£152.12/MWh, net margin £-517.04 -- **net-negative**
- C6 (electricity): tariff £79.15-£257.61/MWh, net margin £-1,380.19 -- **net-negative**
- C7 (electricity): tariff £186.99-£369.64/MWh, net margin £-486.53 -- **net-negative**
- C8 (electricity): tariff £62.19-£386.41/MWh, net margin £-617.89 -- **net-negative**
- C9 (electricity): tariff £62.77-£291.21/MWh, net margin £-206.29 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -2.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £24,488.59 -> £16,148.05 (34.1%)
- Bills issued: 88, average clarity 0.804, average bill shock 45.1%, bad debt provision £404.59, avg complaint probability 5.8%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-5,817.09 vs. naked (unhedged) net margin: £2,350.54
- hedging cost £8,167.63 vs. a fully unhedged book (commodity-only: actual net £-5,817.09 vs. naked net £2,350.54)
  - C2_2: actual £-722.28 vs. naked £335.31 -- hedging cost £1,057.59
  - C4: actual £-882.22 vs. naked £868.00 -- hedging cost £1,750.23
  - C4g: actual £-886.08 vs. naked £1,978.87 -- hedging cost £2,864.96
  - C6: actual £-1,651.63 vs. naked £-2,020.00 -- hedging added £368.37
  - C7: actual £-885.38 vs. naked £1,208.96 -- hedging cost £2,094.34
  - C8: actual £-729.26 vs. naked £102.88 -- hedging cost £832.14
  - C9: actual £-60.24 vs. naked £-123.49 -- hedging added £63.24

**Year narrative:** 2022 (flagged crisis year) produced a net loss of £-4,670.55 across 9 accounts. The risk committee intervened 67 time(s), raising hedge fractions in response to elevated VaR. 37 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £-2,546.42 (gross £-2,455.29, capital £91.13)
  - Electricity: gross £-1,797.31, capital £85.32, net £-1,882.63
  - Gas: gross £-657.97, capital £5.81, net £-663.78
- Treasury at year end: £15,471.35
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.90 (avg 0.90), C6 1.00 (avg 1.00), C7 0.90 (avg 0.90), C8 0.90 (avg 0.90), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 70
  - 2023-01-01: treasury £20,610.10, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-01-31: treasury £20,519.53, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-03-02: treasury £20,438.39, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-01-26: treasury £19,093.01, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2023-02-25: treasury £18,910.03, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2023-03-28: treasury £18,726.15, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2023-01-22: treasury £18,183.03, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-02-21: treasury £18,091.64, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-03-23: treasury £18,001.27, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-01-18: treasury £17,947.28, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-02-17: treasury £17,946.20, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-03-19: treasury £17,939.46, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-04-18: treasury £17,933.89, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-05-18: treasury £17,931.16, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-06-17: treasury £17,924.96, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-01-15: treasury £17,644.56, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-02-14: treasury £17,564.25, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-03-16: treasury £17,484.02, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-04-15: treasury £17,411.22, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-05-15: treasury £17,342.25, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-06-14: treasury £17,277.01, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-07-14: treasury £17,211.77, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-08-13: treasury £17,146.71, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-09-12: treasury £17,080.31, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-01-04: treasury £16,138.97, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-02-03: treasury £16,039.06, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-03-05: treasury £15,942.15, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-04: treasury £15,851.66, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-05-04: treasury £15,775.30, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-06-03: treasury £15,715.32, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-07-03: treasury £15,663.92, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-02: treasury £15,614.78, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-09-01: treasury £15,564.69, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-01: treasury £15,511.19, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-31: treasury £15,443.80, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-30: treasury £15,355.57, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-03-31: treasury £15,267.97, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-30: treasury £15,297.88, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-05-30: treasury £15,317.02, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-06-29: treasury £15,327.21, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-07-29: treasury £15,337.64, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-28: treasury £15,347.32, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-09-27: treasury £15,358.64, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-27: treasury £15,378.34, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-26: treasury £15,414.70, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-12-26: treasury £15,461.26, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-25: treasury £15,645.17, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-05-25: treasury £15,673.18, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-06-24: treasury £15,694.06, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-07-24: treasury £15,713.34, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-23: treasury £15,732.19, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-09-22: treasury £15,752.66, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-22: treasury £15,777.52, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-21: treasury £15,814.94, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-12-21: treasury £15,861.00, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-20: treasury £16,035.42, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-05-20: treasury £16,076.73, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-06-19: treasury £16,092.11, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-07-19: treasury £16,102.09, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-08-18: treasury £16,111.36, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-09-17: treasury £16,121.27, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-10-17: treasury £16,141.57, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-11-16: treasury £16,192.25, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-12-16: treasury £16,275.70, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-07-15: treasury £16,535.91, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-08-14: treasury £16,533.26, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-09-13: treasury £16,531.44, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-10-13: treasury £16,531.34, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-11-12: treasury £16,533.05, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-12-12: treasury £16,537.52, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.00
- Worst single period: C4g on 2023-01-01 period 1, net margin £-2.43

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2023): £-1,189.17
  - By billing account: C1 £-245.52, C2 £-870.25, C2_2 £-394.50, C3 £-346.16, C4 £-2,385.25, C5 £-1,154.77, C6 £-3,142.94, C7 £-1,337.70, C8 £-1,255.48, C9 £-759.15
- Bill shock events (>=20%): 29 -- C7 2023-05-31 (32%); C7 2023-06-30 (37%); C7 2023-10-31 (57%); C7 2023-11-30 (73%); C6 2023-04-30 (30%); C6 2023-05-31 (23%); C6 2023-06-30 (23%); C6 2023-10-31 (38%); C6 2023-11-30 (44%); C8 2023-04-30 (32%); C8 2023-05-31 (41%); C8 2023-06-30 (44%); C8 2023-10-31 (100%); C8 2023-11-30 (70%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (21%); C9 2023-10-31 (74%); C9 2023-11-30 (53%); C4 2023-10-31 (50%); C4g 2023-10-31 (70%); C2_2 2023-04-30 (31%); C2_2 2023-05-31 (41%); C2_2 2023-06-30 (42%); C2_2 2023-10-31 (95%); C2_2 2023-11-30 (66%)
- Churn risk (accounts renewing in 2023): 6 at risk (≥20% churn prob): C2_2 35%, C4 20%, C6 26%, C7 38%, C8 35%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £216.88-£257.61/MWh, net margin £-44.72 -- **net-negative**
- C4 (electricity): tariff £92.53-£280.79/MWh, net margin £-670.81 -- **net-negative**
- C4g (gas): tariff £32.71-£152.12/MWh, net margin £-663.78 -- **net-negative**
- C6 (electricity): tariff £216.88-£257.61/MWh, net margin £-292.70 -- **net-negative**
- C7 (electricity): tariff £85.75-£369.64/MWh, net margin £-885.51 -- **net-negative**
- C8 (electricity): tariff £170.40-£386.41/MWh, net margin £34.67
- C9 (electricity): tariff £89.42-£291.21/MWh, net margin £-23.56 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -3.7% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £20,610.89 -> £15,267.28 (25.9%)
- Bills issued: 84, average clarity 0.815, average bill shock 19.8%, bad debt provision £478.63, avg complaint probability 5.1%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,058.78 vs. naked (unhedged) net margin: £2,289.31
- hedging cost £1,230.52 vs. a fully unhedged book (commodity-only: actual net £1,058.78 vs. naked net £2,289.31)
  - C2_2: actual £347.35 vs. naked £1,111.55 -- hedging cost £764.20
  - C4: actual £-90.50 vs. naked £16.48 -- hedging cost £106.98
  - C4g: actual £2.27 vs. naked £-98.65 -- hedging added £100.92
  - C6: actual £389.09 vs. naked £76.12 -- hedging added £312.97
  - C7: actual £-146.51 vs. naked £-0.51 -- hedging cost £146.00
  - C8: actual £531.61 vs. naked £1,060.98 -- hedging cost £529.36
  - C9: actual £25.47 vs. naked £123.34 -- hedging cost £97.86

**Year narrative:** 2023 produced a net loss of £-2,546.42 across 7 accounts. The risk committee intervened 70 time(s), raising hedge fractions in response to elevated VaR. 29 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £137.21 (gross £288.64, capital £151.43)
  - Electricity: gross £269.83, capital £138.36, net £131.47
  - Gas: gross £18.81, capital £13.07, net £5.74
- Treasury at year end: £16,264.90
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 12
  - 2024-01-25: treasury £15,516.90, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-02-24: treasury £15,561.91, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-03-25: treasury £15,608.83, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-01-20: treasury £15,908.12, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-02-19: treasury £15,948.43, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-03-20: treasury £15,991.13, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-01-15: treasury £16,344.26, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-02-14: treasury £16,433.66, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-03-15: treasury £16,505.21, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-01-11: treasury £16,544.25, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-02-10: treasury £16,554.56, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-03-11: treasury £16,554.93, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 1.60
- Worst single period: C2_2 on 2024-12-12 period 34, net margin £-0.16

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2024): £-1,036.24
  - By billing account: C1 £-197.85, C2 £-917.38, C2_2 £-328.34, C3 £-309.25, C4 £-1,800.29, C5 £-1,199.69, C6 £-2,552.25, C7 £-1,119.81, C8 £-1,203.25, C9 £-734.29
- Bill shock events (>=20%): 25 -- C7 2024-01-31 (32%); C7 2024-02-29 (27%); C7 2024-05-31 (37%); C7 2024-09-30 (34%); C7 2024-10-31 (37%); C7 2024-11-30 (49%); C8 2024-02-29 (23%); C8 2024-04-30 (58%); C8 2024-05-31 (49%); C8 2024-07-31 (27%); C8 2024-09-30 (73%); C8 2024-10-31 (35%); C8 2024-11-30 (62%); C9 2024-05-31 (49%); C9 2024-07-31 (38%); C9 2024-09-30 (54%); C9 2024-10-31 (23%); C9 2024-11-30 (47%); C2_2 2024-02-29 (23%); C2_2 2024-04-30 (57%); C2_2 2024-05-31 (48%); C2_2 2024-07-31 (26%); C2_2 2024-09-30 (65%); C2_2 2024-10-31 (35%); C2_2 2024-11-30 (57%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C4 23%, C6 38%, C7 38%, C8 41%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £87.31-£216.88/MWh, net margin £82.12
- C4 (electricity): tariff £92.53/MWh, net margin £-63.34 -- **net-negative**
- C4g (gas): tariff £32.71/MWh, net margin £5.74
- C6 (electricity): tariff £216.88/MWh, net margin £129.85
- C7 (electricity): tariff £85.75-£167.51/MWh, net margin £-145.67 -- **net-negative**
- C8 (electricity): tariff £68.60-£325.32/MWh, net margin £194.32
- C9 (electricity): tariff £58.77-£170.71/MWh, net margin £-65.82 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 52.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 69, average clarity 0.806, average bill shock 20.1%, bad debt provision £240.33, avg complaint probability 5.2%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-436.02 vs. naked (unhedged) net margin: £-1,326.78
- hedging added £890.75 vs. a fully unhedged book (commodity-only: actual net £-436.02 vs. naked net £-1,326.78)
  - C2_2: actual £-122.94 vs. naked £-247.28 -- hedging added £124.35
  - C7: actual £-57.44 vs. naked £-160.60 -- hedging added £103.17
  - C8: actual £-67.59 vs. naked £-381.01 -- hedging added £313.42
  - C9: actual £-188.06 vs. naked £-537.88 -- hedging added £349.82

**Year narrative:** 2024 produced a net gain of £137.21 across 7 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 25 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £-452.03 (gross £-381.56, capital £70.47)
  - Electricity: gross £-381.56, capital £70.47, net £-452.03
- Treasury at year end: £15,948.67
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C8 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C8 on 2025-01-08 period 36, net margin £-1.55

**Customer Book**

- Active accounts: 4 (C2_2, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 0, gas (dual-fuel): 0
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £-1,019.01
  - By billing account: C1 £-206.37, C2 £-813.55, C2_2 £-363.44, C3 £-319.47, C4 £-1,836.31, C5 £-1,131.69, C6 £-2,635.89, C7 £-1,185.46, C8 £-977.29, C9 £-720.62
- Bill shock events (>=20%): 17 -- C7 2025-01-31 (28%); C7 2025-04-30 (37%); C7 2025-05-31 (23%); C7 2025-06-07 (80%); C8 2025-01-31 (39%); C8 2025-02-28 (24%); C8 2025-05-31 (37%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (33%); C9 2025-06-07 (72%); C2_2 2025-01-31 (38%); C2_2 2025-02-28 (24%); C2_2 2025-04-30 (20%); C2_2 2025-05-31 (36%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £87.31-£131.36/MWh, net margin £-163.71 -- **net-negative**
- C7 (electricity): tariff £87.74-£167.51/MWh, net margin £-52.35 -- **net-negative**
- C8 (electricity): tariff £68.60-£197.05/MWh, net margin £-135.21 -- **net-negative**
- C9 (electricity): tariff £58.77-£112.19/MWh, net margin £-100.76 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -18.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 24, average clarity 0.727, average bill shock 32.1%, bad debt provision £82.72, avg complaint probability 7.3%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-208.45 vs. naked (unhedged) net margin: £-106.85
- hedging cost £101.60 vs. a fully unhedged book (commodity-only: actual net £-208.45 vs. naked net £-106.85)
  - C2_2: actual £-103.12 vs. naked £7.06 -- hedging cost £110.19
  - C8: actual £-105.32 vs. naked £-113.91 -- hedging added £8.59

**Year narrative:** 2025 produced a net loss of £-452.03 across 4 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 17 customer(s) experienced a bill shock of >=20%.
