# Annual Report — The Synthetic Enterprise

## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £29,846.19
- Final treasury: £13,706.53
  (£-16,139.66 net change)
- Customer bills (all-in): £146,434.14
  VAT remitted to HMRC: (£11,973.68) | Revenue (ex-VAT): £134,460.46
  Non-commodity pass-through: (£42,887.46)
- Gross margin: £-4,514.23
- Capital costs: £1,227.63
- Net margin: £-5,741.86
- Capital cost ratio: -27.2% of gross
- Net margin as % of revenue: -4.3%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 317
- Bills issued: 1117, average clarity 0.871,
  service quality score 0.920
- Enterprise value (CLV sum across 10 billing accounts): £-18,277.46
- Cost to serve (whole portfolio): £6,129.45, net margin after cost to serve: £-11,871.31
- Hedge effectiveness (whole window): hedging cost £1,656.28 vs. a fully unhedged book (commodity-only: actual net £-16,139.66 vs. naked net £-14,483.38)

- **2021** (crisis year): net margin £-2,743.14, 19 risk committee wake-up(s).
- **2022** (crisis year): net margin £-5,340.86, 70 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £-4,514.23, capital £1,227.63, net £-5,741.86. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: -8.2% (commodity basis, comparable to old model) / -27.2% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £-2,743.14 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run -4.3%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £-5,741.86
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £-14,483.38
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £1,656.28 vs. a fully unhedged book (commodity-only: actual net £-16,139.66 vs. naked net £-14,483.38)
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
| 2016 | £-421.05 | £-358.02 | £66.86 | £-712.21 |
| 2017 | £-889.78 | £-918.72 | £115.52 | £-1,692.98 |
| 2018 | £-651.22 | £-608.80 | £96.75 | £-1,163.28 |
| 2019 | £-284.27 | £-104.04 | £227.78 | £-160.53 |
| 2020 | £-284.37 | £-205.54 | £159.53 | £-330.38 |
| 2021 | £-1,139.86 | £-1,342.50 | £-260.79 | £-2,743.14 |
| 2022 | £-1,574.89 | £-3,010.71 | £-755.25 | £-5,340.86 |
| 2023 | £-574.46 | £-2,284.75 | £-1,014.68 | £-3,873.88 |
| 2024 | £25.07 | £157.07 | £25.04 | £207.18 |
| 2025 | £0.00 | £-329.57 | £0.00 | £-329.57 |

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
| C5 | 2017-12-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8255 |
| C1 | 2018-12-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.4100 | 0.3500 | 0.7335 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6312 |
| C1 | 2019-12-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1400 | 0.5500 | 0.9370 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.4829 |
| C2 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.1400 | 0.5500 | 0.9370 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.1700 | 0.5500 | 0.9235 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0637 |
| C2_2 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.2600 | 0.3500 | 0.8310 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C2_2 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.2300 | 0.5500 | 0.8965 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4099 |
| C2_2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 131.6%
- **Average signed error:** +33.5% (over-estimates vs SIM)
- **Renewal events with estimates:** 49

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +58.0% | 110.3% |
| 2017 | 3 | -11.4% | 53.2% |
| 2018 | 3 | +14.9% | 55.0% |
| 2019 | 3 | -100.0% | 100.0% |
| 2020 | 9 | -77.2% | 77.2% |
| 2021 | 8 | +316.1% | 316.1% |
| 2022 | 6 | +150.2% | 175.5% |
| 2023 | 6 | -63.3% | 103.3% |
| 2024 | 6 | -90.2% | 90.2% |
| 2025 | 2 | -28.1% | 28.1% |

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
| 2016 | 17 | 22.2% | 41.0% |
| 2017 | 13 | 15.2% | 30.9% |
| 2018 | 13 | 15.8% | 41.4% |
| 2019 | 13 | 12.3% | 20.0% |
| 2020 | 12 | 22.7% | 41.0% |
| 2021 | 10 | 30.9% | 42.0% |
| 2022 | 8 | 30.0% | 41.5% |
| 2023 | 7 | 6.5% | 19.9% |
| 2024 | 6 | 12.0% | 26.2% |
| 2025 | 2 | 43.9% | 43.9% |

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
| 2016 | 3 | 1.10× | 2.52× |
| 2017 | 3 | 0.53× | 0.63× |
| 2018 | 3 | 0.55× | 1.05× |
| 2019 | 3 | 1.00× | 1.00× |
| 2020 | 9 | 0.77× | 1.00× |
| 2021 | 8 | 3.16× ⚠ | 10.88× |
| 2022 | 6 | 1.76× | 4.59× |
| 2023 | 6 | 1.03× | 1.20× |
| 2024 | 6 | 0.90× | 1.00× |
| 2025 | 2 | 0.28× | 0.28× |

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
| C7 | 120,842 | 40,643 | 33.6% | £6,157.52 | £6,410.74 | £151.50/MWh | £79.94/MWh | +3.0% |
| C8 | 106,723 | 46,761 | 43.8% | £6,787.95 | £4,574.59 | £145.16/MWh | £76.29/MWh | +10.0% |
| C9 | 109,388 | 46,156 | 42.2% | £5,406.70 | £3,882.46 | £117.14/MWh | £61.40/MWh | +8.7% |

Total HH revenue: £33,219.96 vs flat equivalent £31,075.50 (+6.9% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 19 | 102% | C8 (2016-10-31) |
| 2017 | 24 | 82% | C8 (2017-11-30) |
| 2018 | 32 | 54% | C8 (2018-10-31) |
| 2019 | 33 | 83% | C8 (2019-10-31) |
| 2020 | 29 | 63% | C8 (2020-10-31) |
| 2021 | 29 | 137% | C4 (2021-10-31) |
| 2022 | 37 | 1718% | C2_2 (2022-04-30) |
| 2023 | 29 | 99% | C8 (2023-10-31) |
| 2024 | 25 | 74% | C8 (2024-09-30) |
| 2025 | 18 | 80% | C7 (2025-06-07) |

Total: **275** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1718% | no |
| 2022-10-31 | C4g | +168% | no |
| 2022-01-31 | C7 | +160% | no |
| 2021-10-31 | C4 | +137% | yes |
| 2021-10-31 | C4g | +132% | no |
| 2016-10-31 | C8 | +102% | no |
| 2023-10-31 | C8 | +99% | no |
| 2023-10-31 | C2_2 | +94% | no |
| 2022-04-30 | C6 | +89% | yes |
| 2022-09-30 | C8 | +84% | no |


## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 6 |
| Retained | 6 (100%) |
| Churned despite offer | 0 |
| Total offer cost (foregone margin) | £145.92 |
| Margin saved (retained customers' terms) | £220.10 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£74.17** |

Missed opportunities (churns with no offer): **6** (£422.52 expected margin lost without offer)
- **Blocked — uneconomical** (churn estimate above threshold but margin + acq_cost < discount cost): 3 (£144.09 margin foregone)
- **Below threshold** (churn estimate under 30%): 3 (£278.43 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 3 | 3 | £104.58 | £161.67 | £57.09 | £0.00 |
| 2018 | 3 | 3 | £41.34 | £58.42 | £17.08 | £0.00 |
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £7.58 |
| 2021 | 0 | 0 | £0.00 | £0.00 | £0.00 | £126.69 |
| 2022 | 0 | 0 | £0.00 | £0.00 | £0.00 | £17.40 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £270.85 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----|---------|
| 2017-04-01 | C2 | 0.41 | 3% | £6.07 | £9.38 | £3.31 | retained |
| 2017-04-01 | C6 | 0.41 | 3% | £78.01 | £120.59 | £42.58 | retained |
| 2017-04-01 | C8 | 0.41 | 3% | £20.51 | £31.70 | £11.19 | retained |
| 2018-07-01 | C3 | 0.31 | 3% | £5.98 | £8.75 | £2.77 | retained |
| 2018-07-01 | C9 | 0.31 | 3% | £23.13 | £33.83 | £10.71 | retained |
| 2018-10-01 | C4 | 0.38 | 3% | £12.23 | £15.84 | £3.60 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C2 | 2017-04-01 | 2022-03-31 | 60 | churned |
| C6 | 2017-04-01 | 2024-03-30 | 84 | churned |
| C8 | 2017-04-01 | (window end) | 105 | active |
| C3 | 2018-07-01 | 2020-06-30 | 24 | churned |
| C9 | 2018-07-01 | (window end) | 90 | active |
| C4 | 2018-10-01 | 2024-09-29 | 72 | churned |

**Eventually churned (4/6)**: C2, C6, C3, C4 — avg 60 months post-retention before final churn.
**Still active (2/6)**: C8, C9 — survived to simulation end.

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £-300.68 | — | — | — | — | £-1,291.48 | — | £-702.67 | — | — |
| 2017 | £-745.79 | £-2,130.63 | — | £-771.83 | £-112.47 | £-3,312.14 | £-4,235.62 | £-1,855.41 | £-1,901.79 | £-1,328.23 |
| 2018 | £-531.99 | £-1,606.30 | — | £-572.17 | £-25.28 | £-2,468.86 | £-3,936.36 | £-1,299.22 | £-1,575.90 | £-1,144.62 |
| 2019 | £-263.35 | £-1,302.01 | — | £-442.97 | £28.44 | £-1,377.94 | £-3,261.65 | £-833.07 | £-1,404.89 | £-768.47 |
| 2020 | £-237.18 | £-997.23 | — | £-322.84 | £8.64 | £-1,233.95 | £-2,570.34 | £-653.07 | £-1,100.42 | £-685.02 |
| 2021 | £-371.30 | £-1,099.51 | — | £-314.66 | £-494.21 | £-1,268.62 | £-2,879.04 | £-759.24 | £-1,231.57 | £-802.01 |
| 2022 | £-327.36 | £-947.83 | £-502.28 | £-310.53 | £-1,633.54 | £-1,407.42 | £-3,713.25 | £-1,265.11 | £-1,765.59 | £-906.08 |
| 2023 | £-333.67 | £-931.10 | £-519.59 | £-312.59 | £-2,754.49 | £-1,294.37 | £-3,477.49 | £-1,683.28 | £-1,342.33 | £-721.31 |
| 2024 | £-287.51 | £-998.95 | £-465.41 | £-241.30 | £-2,034.22 | £-1,277.10 | £-2,933.45 | £-1,517.96 | £-1,237.51 | £-635.04 |
| 2025 | £-254.88 | £-967.62 | £-461.86 | £-265.27 | £-1,980.87 | £-1,298.46 | £-2,942.81 | £-1,375.65 | £-1,217.79 | £-558.07 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £437.82, range £24.20–£1,105.82.

- C1: cost to serve £357.36, net margin after CTS £-543.23 — **NET_NEGATIVE** (tariff uplift needed: +39.6%)
- C1g: cost to serve £35.91, net margin after CTS £145.50
- C2: cost to serve £378.34, net margin after CTS £-1,276.37 — **NET_NEGATIVE** (tariff uplift needed: +52.7%)
- C2_2: cost to serve £289.28, net margin after CTS £-993.04 — **NET_NEGATIVE** (tariff uplift needed: +17.5%)
- C2g: cost to serve £41.32, net margin after CTS £-50.73 — **NET_NEGATIVE** (tariff uplift needed: +2.9%)
- C3: cost to serve £238.07, net margin after CTS £-367.94 — **NET_NEGATIVE** (tariff uplift needed: +40.6%)
- C3g: cost to serve £24.20, net margin after CTS £108.65
- C4: cost to serve £554.00, net margin after CTS £-2,266.01 — **NET_NEGATIVE** (tariff uplift needed: +39.7%)
- C4g: cost to serve £138.00, net margin after CTS £-1,714.06 — **NET_NEGATIVE** (tariff uplift needed: +26.6%)
- C5: cost to serve £786.47, net margin after CTS £-1,710.62 — **NET_NEGATIVE** (tariff uplift needed: +25.7%)
- C6: cost to serve £1,105.82, net margin after CTS £-5,530.25 — **NET_NEGATIVE** (tariff uplift needed: +37.9%)
- C7: cost to serve £770.50, net margin after CTS £-3,225.70 — **NET_NEGATIVE** (tariff uplift needed: +25.7%)
- C8: cost to serve £732.68, net margin after CTS £-2,368.61 — **NET_NEGATIVE** (tariff uplift needed: +20.8%)
- C9: cost to serve £677.50, net margin after CTS £-1,249.08 — **NET_NEGATIVE** (tariff uplift needed: +13.4%)

**Activity-Based Pricing Actions**

The following 12 customer(s) are loss-making after cost-to-serve and require immediate tariff review:
  - C1: net margin after CTS £-543.23 on revenue £1,371.44 — raise tariff by ≥39.6% to break even
  - C2: net margin after CTS £-1,276.37 on revenue £2,420.30 — raise tariff by ≥52.7% to break even
  - C2_2: net margin after CTS £-993.04 on revenue £5,689.07 — raise tariff by ≥17.5% to break even
  - C2g: net margin after CTS £-50.73 on revenue £1,722.33 — raise tariff by ≥2.9% to break even
  - C3: net margin after CTS £-367.94 on revenue £905.89 — raise tariff by ≥40.6% to break even
  - C4: net margin after CTS £-2,266.01 on revenue £5,705.74 — raise tariff by ≥39.7% to break even
  - C4g: net margin after CTS £-1,714.06 on revenue £6,441.73 — raise tariff by ≥26.6% to break even
  - C5: net margin after CTS £-1,710.62 on revenue £6,661.97 — raise tariff by ≥25.7% to break even
  - C6: net margin after CTS £-5,530.25 on revenue £14,604.54 — raise tariff by ≥37.9% to break even
  - C7: net margin after CTS £-3,225.70 on revenue £12,568.26 — raise tariff by ≥25.7% to break even
  - C8: net margin after CTS £-2,368.61 on revenue £11,362.54 — raise tariff by ≥20.8% to break even
  - C9: net margin after CTS £-1,249.08 on revenue £9,289.16 — raise tariff by ≥13.4% to break even

## Tariff Repricing Impact Assessment

Estimated churn risk at the break-even tariff level for each loss-making customer.
Active = current opportunity; churned = retrospective counterfactual.

| Customer | Fuel | Seg | Status | Uplift needed | Total loss | Churn @ B/E | Decision |
|----------|------|-----|--------|--------------|-----------|-------------|----------|
| C2g | gas | resi | active | +2.9% | £50.73 | 5% | Raise — churn risk manageable |
| C9 | elec | resi | active | +13.4% | £1,249.08 | 16% | Raise — churn risk manageable |
| C2_2 | elec | resi | active | +17.5% | £993.04 | 19% | Raise — churn risk manageable |
| C8 | elec | resi | active | +20.8% | £2,368.61 | 22% | Raise — churn risk manageable |
| C5 | elec | SME | churned | +25.7% | £1,710.62 | 26% | Raise — churn risk manageable |
| C7 | elec | resi | active | +25.7% | £3,225.70 | 26% | Raise — churn risk manageable |
| C4g | gas | resi | active | +26.6% | £1,714.06 | 19% | Raise — churn risk manageable |
| C6 | elec | SME | churned | +37.9% | £5,530.25 | 35% | Raise — churn risk manageable |
| C1 | elec | resi | churned | +39.6% | £543.23 | 37% | Raise — churn risk manageable |
| C4 | elec | resi | churned | +39.7% | £2,266.01 | 37% | Raise — churn risk manageable |
| C3 | elec | resi | churned | +40.6% | £367.94 | 37% | Raise — churn risk manageable |
| C2 | elec | resi | churned | +52.7% | £1,276.37 | 47% | Partial — incremental uplift advised |

**Repriceable now (6)**: C2g, C9, C2_2, C8, C7, C4g — break-even churn risk below 40%. Uplift advised.
**Missed repricing window (5 churned)**: C5, C6, C1, C4, C3 — break-even price would not have triggered high churn. Earlier repricing might have changed economics.

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
| Customer bills (all-in) | £146,434.14 |
|   Less: VAT remitted to HMRC | (£11,973.68) |
| = Revenue (ex-VAT) | £134,460.46 |
| Less: non-commodity pass-through | (£42,887.46) |
| Wholesale cost (settlement events) | (£96,087.24) |
| Gross margin | £-4,514.23 |
| Capital charges | (£1,227.63) |
| Net margin | £-5,741.86 |

_Cash reconciliation: of £146,434.14 billed, bad debt of £2,870.61 was written off, leaving £143,563.53 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £3,361.21._

| Acquisition spend | (£1,250.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £-12,691.86 |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £-12,691.86

## 2016

**Trading & Risk**

- Net margin: £-712.21 (gross £-518.47, capital £193.74)
  - Electricity: gross £-591.66, capital £187.42, net £-779.07
  - Gas: gross £73.19, capital £6.32, net £66.86
- Treasury at year end: £29,500.48
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
  - 2016-04-08: treasury £29,568.85, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-05-08: treasury £29,561.63, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-06-07: treasury £29,555.07, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-07-07: treasury £29,548.17, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-06: treasury £29,541.57, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-09-05: treasury £29,535.09, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-10-05: treasury £29,527.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-11-04: treasury £29,519.45, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-12-04: treasury £29,508.76, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-05: treasury £29,472.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-04-26: treasury £29,445.07, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-05-26: treasury £29,421.47, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-06-25: treasury £29,402.58, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-07-25: treasury £29,384.47, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-08-24: treasury £29,368.16, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-09-23: treasury £29,349.36, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-10-23: treasury £29,324.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-11-22: treasury £29,283.26, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-12-22: treasury £29,246.18, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-04-21: treasury £29,116.30, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-05-21: treasury £29,105.98, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-06-20: treasury £29,099.54, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-20: treasury £29,093.82, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-08-19: treasury £29,088.95, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-09-18: treasury £29,083.05, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-10-18: treasury £29,073.45, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-11-17: treasury £29,057.34, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-12-17: treasury £29,037.34, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-16: treasury £28,979.48, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-08-15: treasury £28,977.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-09-14: treasury £28,975.50, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-10-14: treasury £28,973.05, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-11-13: treasury £28,969.33, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-12-13: treasury £28,965.16, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-07-03: treasury £28,971.18, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-08-02: treasury £28,968.25, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-09-01: treasury £28,965.63, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-01: treasury £28,962.14, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-31: treasury £28,956.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-11-30: treasury £28,945.24, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-12-30: treasury £28,940.23, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-28: treasury £28,906.60, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-11-27: treasury £28,899.92, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-12-27: treasury £28,895.08, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.03
- Worst single period: C8 on 2016-11-20 period 36, net margin £-0.52

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £-764.94
  - By billing account: C1 £-300.68, C5 £-1,291.48, C7 £-702.67
- Bill shock events (>=20%): 19 -- C5 2016-05-31 (26%); C5 2016-10-31 (40%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (77%); C7 2016-11-30 (51%); C6 2016-05-31 (25%); C6 2016-06-30 (22%); C6 2016-10-31 (39%); C6 2016-11-30 (44%); C8 2016-05-31 (40%); C8 2016-06-30 (41%); C8 2016-09-30 (22%); C8 2016-10-31 (102%); C8 2016-11-30 (68%); C9 2016-10-31 (76%); C9 2016-11-30 (58%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £50.87-£56.35/MWh, net margin £-31.34 -- **net-negative**
- C1g (gas): tariff £16.64-£17.59/MWh, net margin £29.08
- C2 (electricity): tariff £41.19/MWh, net margin £-70.11 -- **net-negative**
- C2g (gas): tariff £15.29/MWh, net margin £-1.17 -- **net-negative**
- C3 (electricity): tariff £41.81/MWh, net margin £-17.19 -- **net-negative**
- C3g (gas): tariff £13.52/MWh, net margin £14.24
- C4 (electricity): tariff £45.42/MWh, net margin £-15.95 -- **net-negative**
- C4g (gas): tariff £16.78/MWh, net margin £24.72
- C5 (electricity): tariff £50.87-£56.35/MWh, net margin £-185.38 -- **net-negative**
- C6 (electricity): tariff £41.19/MWh, net margin £-235.67 -- **net-negative**
- C7 (electricity): tariff £39.97-£76.30/MWh, net margin £-95.62 -- **net-negative**
- C8 (electricity): tariff £32.37-£61.79/MWh, net margin £-95.77 -- **net-negative**
- C9 (electricity): tariff £32.85-£62.72/MWh, net margin £-32.03 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -37.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.893, average bill shock 13.2%, bad debt provision £200.14, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-2,013.49 vs. naked (unhedged) net margin: £-1,992.64
- hedging cost £20.85 vs. a fully unhedged book (commodity-only: actual net £-2,013.49 vs. naked net £-1,992.64)
  - C1: actual £-155.61 vs. naked £-43.69 -- hedging cost £111.92
  - C1g: actual £63.82 vs. naked £58.40 -- hedging added £5.41
  - C2: actual £-97.69 vs. naked £-39.90 -- hedging cost £57.79
  - C2g: actual £-3.80 vs. naked £24.74 -- hedging cost £28.54
  - C3: actual £-34.12 vs. naked £-49.38 -- hedging added £15.27
  - C3g: actual £25.38 vs. naked £-5.87 -- hedging added £31.25
  - C4: actual £-54.44 vs. naked £-40.09 -- hedging cost £14.36
  - C4g: actual £92.26 vs. naked £40.58 -- hedging added £51.67
  - C5: actual £-796.71 vs. naked £-669.66 -- hedging cost £127.05
  - C6: actual £-344.31 vs. naked £-657.69 -- hedging added £313.38
  - C7: actual £-502.37 vs. naked £-225.21 -- hedging cost £277.16
  - C8: actual £-144.38 vs. naked £-209.19 -- hedging added £64.81
  - C9: actual £-61.51 vs. naked £-175.68 -- hedging added £114.17

**Year narrative:** 2016 produced a net loss of £-712.21 across 13 accounts. The risk committee intervened 81 time(s), raising hedge fractions in response to elevated VaR. 19 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £-1,692.98 (gross £-1,562.91, capital £130.07)
  - Electricity: gross £-1,688.39, capital £120.11, net £-1,808.50
  - Gas: gross £125.48, capital £9.96, net £115.52
- Treasury at year end: £27,782.49
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.95 (avg 0.95), C3g 0.95 (avg 0.95), C4 0.85 (avg 0.85), C4g 0.95 (avg 0.95), C5 0.85 (avg 0.85), C6 0.95 (avg 0.95), C7 0.85 (avg 0.85), C8 0.95 (avg 0.95), C9 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 42
  - 2017-01-03: treasury £29,499.68, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-02-02: treasury £29,489.75, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-03-04: treasury £29,480.51, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-01-21: treasury £29,207.13, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-02-20: treasury £29,166.70, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-03-22: treasury £29,134.57, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-01-16: treasury £29,019.08, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-02-15: treasury £28,998.90, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-03-17: treasury £28,986.27, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-01-12: treasury £28,961.90, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-02-11: treasury £28,957.93, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-03-13: treasury £28,954.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-04-12: treasury £28,952.51, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-05-12: treasury £28,950.04, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-06-11: treasury £28,947.60, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-01-29: treasury £28,931.27, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-02-28: treasury £28,925.42, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-03-30: treasury £28,921.49, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-04-29: treasury £28,917.80, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-05-29: treasury £28,912.90, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-06-28: treasury £28,910.15, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-01-26: treasury £28,889.49, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-02-25: treasury £28,884.22, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-03-27: treasury £28,879.64, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-04-26: treasury £28,876.09, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-05-26: treasury £28,871.55, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-06-25: treasury £28,868.07, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-07-25: treasury £28,864.67, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-08-24: treasury £28,861.09, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-09-23: treasury £28,856.83, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-01-15: treasury £28,941.67, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-02-14: treasury £28,929.41, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-03-16: treasury £28,917.43, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-04-15: treasury £28,907.26, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-05-15: treasury £28,897.87, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-06-14: treasury £28,889.38, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-07-14: treasury £28,880.90, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-08-13: treasury £28,872.54, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-09-12: treasury £28,863.81, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-10-12: treasury £28,854.12, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-11-11: treasury £28,843.46, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-12-11: treasury £28,831.26, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C5 on 2017-01-23 period 19, net margin £-0.20

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £-1,821.55
  - By billing account: C1 £-745.79, C2 £-2,130.63, C3 £-771.83, C4 £-112.47, C5 £-3,312.14, C6 £-4,235.62, C7 £-1,855.41, C8 £-1,901.79, C9 £-1,328.23
- Bill shock events (>=20%): 24 -- C5 2017-01-31 (21%); C5 2017-02-28 (22%); C5 2017-06-30 (21%); C5 2017-11-30 (54%); C7 2017-01-31 (28%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C6 2017-05-31 (21%); C6 2017-11-30 (48%); C8 2017-05-31 (39%); C8 2017-06-30 (36%); C8 2017-09-30 (44%); C8 2017-10-31 (22%); C8 2017-11-30 (82%); C8 2017-12-31 (22%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): 5 at risk (≥20% churn prob): C5 32%, C6 35%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £56.35-£63.33/MWh, net margin £-124.51 -- **net-negative**
- C1g (gas): tariff £17.59-£23.74/MWh, net margin £34.77
- C2 (electricity): tariff £41.19-£57.78/MWh, net margin £-77.79 -- **net-negative**
- C2g (gas): tariff £15.29-£16.77/MWh, net margin £-33.47 -- **net-negative**
- C3 (electricity): tariff £41.81-£48.36/MWh, net margin £-55.74 -- **net-negative**
- C3g (gas): tariff £13.52-£16.31/MWh, net margin £24.80
- C4 (electricity): tariff £45.42-£54.12/MWh, net margin £-39.76 -- **net-negative**
- C4g (gas): tariff £16.78-£20.91/MWh, net margin £89.42
- C5 (electricity): tariff £56.35-£63.33/MWh, net margin £-613.51 -- **net-negative**
- C6 (electricity): tariff £41.19-£57.78/MWh, net margin £-276.27 -- **net-negative**
- C7 (electricity): tariff £44.27-£84.52/MWh, net margin £-408.35 -- **net-negative**
- C8 (electricity): tariff £32.37-£86.68/MWh, net margin £-102.83 -- **net-negative**
- C9 (electricity): tariff £32.85-£72.54/MWh, net margin £-109.75 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -8.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.899, average bill shock 10.8%, bad debt provision £299.48, avg complaint probability 3.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-646.24 vs. naked (unhedged) net margin: £-1,131.41
- hedging added £485.17 vs. a fully unhedged book (commodity-only: actual net £-646.24 vs. naked net £-1,131.41)
  - C1: actual £-7.25 vs. naked £-13.00 -- hedging added £5.75
  - C1g: actual £39.31 vs. naked £10.01 -- hedging added £29.29
  - C2: actual £-72.77 vs. naked £30.63 -- hedging cost £103.40
  - C2g: actual £-43.81 vs. naked £-21.44 -- hedging cost £22.37
  - C3: actual £-79.12 vs. naked £-55.91 -- hedging cost £23.21
  - C3g: actual £25.77 vs. naked £-41.39 -- hedging added £67.15
  - C4: actual £-9.89 vs. naked £-47.32 -- hedging added £37.43
  - C4g: actual £84.18 vs. naked £-10.74 -- hedging added £94.92
  - C5: actual £-51.99 vs. naked £-175.42 -- hedging added £123.43
  - C6: actual £-259.60 vs. naked £-501.61 -- hedging added £242.01
  - C7: actual £-7.97 vs. naked £-45.03 -- hedging added £37.06
  - C8: actual £-85.28 vs. naked £-59.16 -- hedging cost £26.12
  - C9: actual £-177.80 vs. naked £-201.05 -- hedging added £23.24

**Year narrative:** 2017 produced a net loss of £-1,692.98 across 13 accounts. The risk committee intervened 42 time(s), raising hedge fractions in response to elevated VaR. 24 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £-1,163.28 (gross £-1,061.90, capital £101.37)
  - Electricity: gross £-1,165.81, capital £94.21, net £-1,260.02
  - Gas: gross £103.91, capital £7.16, net £96.75
- Treasury at year end: £27,003.01
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
- Average CLV (Point-in-Time, year-end 2018): £-1,462.30
  - By billing account: C1 £-531.99, C2 £-1,606.30, C3 £-572.17, C4 £-25.28, C5 £-2,468.86, C6 £-3,936.36, C7 £-1,299.22, C8 £-1,575.90, C9 £-1,144.62
- Bill shock events (>=20%): 32 -- C5 2018-04-30 (32%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (28%); C7 2018-10-31 (45%); C7 2018-11-30 (32%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (21%); C6 2018-10-31 (29%); C6 2018-11-30 (21%); C8 2018-04-30 (33%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (24%); C8 2018-09-30 (51%); C8 2018-10-31 (54%); C8 2018-11-30 (29%); C3g 2018-07-31 (26%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-08-31 (40%); C9 2018-09-30 (43%); C9 2018-10-31 (39%); C9 2018-12-31 (20%); C4 2018-10-31 (22%); C4g 2018-10-31 (31%)
- Churn risk (accounts renewing in 2018): 5 at risk (≥20% churn prob): C5 41%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £63.33-£80.49/MWh, net margin £-7.00 -- **net-negative**
- C1g (gas): tariff £23.74-£31.73/MWh, net margin £39.53
- C2 (electricity): tariff £57.78-£65.98/MWh, net margin £-206.02 -- **net-negative**
- C2g (gas): tariff £16.77-£22.41/MWh, net margin £-54.48 -- **net-negative**
- C3 (electricity): tariff £48.36-£62.32/MWh, net margin £-46.54 -- **net-negative**
- C3g (gas): tariff £16.31-£23.45/MWh, net margin £27.78
- C4 (electricity): tariff £54.12-£74.14/MWh, net margin £-6.90 -- **net-negative**
- C4g (gas): tariff £20.91-£30.16/MWh, net margin £83.92
- C5 (electricity): tariff £63.33-£80.49/MWh, net margin £-49.99 -- **net-negative**
- C6 (electricity): tariff £57.78-£65.98/MWh, net margin £-601.23 -- **net-negative**
- C7 (electricity): tariff £49.76-£120.74/MWh, net margin £-5.76 -- **net-negative**
- C8 (electricity): tariff £45.40-£98.96/MWh, net margin £-251.11 -- **net-negative**
- C9 (electricity): tariff £38.00-£93.47/MWh, net margin £-85.47 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -9.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.897, average bill shock 10.9%, bad debt provision £331.10, avg complaint probability 3.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-913.72 vs. naked (unhedged) net margin: £1,182.79
- hedging cost £2,096.51 vs. a fully unhedged book (commodity-only: actual net £-913.72 vs. naked net £1,182.79)
  - C1: actual £25.16 vs. naked £111.88 -- hedging cost £86.72
  - C1g: actual £92.73 vs. naked £212.57 -- hedging cost £119.84
  - C2: actual £-250.08 vs. naked £31.97 -- hedging cost £282.05
  - C2g: actual £-52.34 vs. naked £2.19 -- hedging cost £54.54
  - C3: actual £-7.55 vs. naked £10.33 -- hedging cost £17.87
  - C3g: actual £31.09 vs. naked £51.31 -- hedging cost £20.22
  - C4: actual £11.41 vs. naked £154.20 -- hedging cost £142.79
  - C4g: actual £85.77 vs. naked £294.36 -- hedging cost £208.58
  - C5: actual £116.61 vs. naked £431.25 -- hedging cost £314.64
  - C6: actual £-772.74 vs. naked £-500.99 -- hedging cost £271.76
  - C7: actual £116.02 vs. naked £383.19 -- hedging cost £267.17
  - C8: actual £-345.89 vs. naked £-32.14 -- hedging cost £313.74
  - C9: actual £36.09 vs. naked £32.67 -- hedging added £3.42

**Year narrative:** 2018 produced a net loss of £-1,163.28 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 32 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £-160.53 (gross £-95.12, capital £65.42)
  - Electricity: gross £-328.52, capital £59.79, net £-388.31
  - Gas: gross £233.41, capital £5.63, net £227.78
- Treasury at year end: £26,235.65
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
- Average CLV (Point-in-Time, year-end 2019): £-1,069.54
  - By billing account: C1 £-263.35, C2 £-1,302.01, C3 £-442.97, C4 £28.44, C5 £-1,377.94, C6 £-3,261.65, C7 £-833.07, C8 £-1,404.89, C9 £-768.47
- Bill shock events (>=20%): 33 -- C1 2019-04-30 (21%); C5 2019-01-31 (36%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (69%); C7 2019-11-30 (44%); C6 2019-02-28 (21%); C6 2019-04-30 (22%); C6 2019-06-30 (24%); C6 2019-10-31 (40%); C6 2019-11-30 (26%); C8 2019-01-31 (26%); C8 2019-02-28 (27%); C8 2019-04-30 (26%); C8 2019-06-30 (38%); C8 2019-07-31 (34%); C8 2019-09-30 (56%); C8 2019-10-31 (83%); C8 2019-11-30 (37%); C9 2019-02-28 (26%); C9 2019-04-30 (23%); C9 2019-06-30 (36%); C9 2019-07-31 (38%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (37%); C4g 2019-10-31 (34%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C3 23%, C5 38%, C6 29%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £51.68-£80.49/MWh, net margin £24.98
- C1g (gas): tariff £15.26-£31.73/MWh, net margin £92.43
- C2 (electricity): tariff £62.36-£65.98/MWh, net margin £-103.71 -- **net-negative**
- C2g (gas): tariff £22.41-£22.48/MWh, net margin £12.43
- C3 (electricity): tariff £49.00-£62.32/MWh, net margin £-13.03 -- **net-negative**
- C3g (gas): tariff £16.78-£23.45/MWh, net margin £37.54
- C4 (electricity): tariff £49.15-£74.14/MWh, net margin £12.41
- C4g (gas): tariff £13.99-£30.16/MWh, net margin £85.38
- C5 (electricity): tariff £51.68-£80.49/MWh, net margin £115.31
- C6 (electricity): tariff £62.36-£65.98/MWh, net margin £-399.58 -- **net-negative**
- C7 (electricity): tariff £40.61-£120.74/MWh, net margin £115.13
- C8 (electricity): tariff £49.00-£98.96/MWh, net margin £-146.58 -- **net-negative**
- C9 (electricity): tariff £38.50-£93.47/MWh, net margin £6.76

**Portfolio Health**

- Capital cost ratio: -68.8% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.893, average bill shock 12.5%, bad debt provision £350.14, avg complaint probability 3.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-130.39 vs. naked (unhedged) net margin: £1,457.81
- hedging cost £1,588.19 vs. a fully unhedged book (commodity-only: actual net £-130.39 vs. naked net £1,457.81)
  - C1: actual £-2.52 vs. naked £31.28 -- hedging cost £33.79
  - C1g: actual £25.41 vs. naked £67.33 -- hedging cost £41.92
  - C2: actual £-49.28 vs. naked £163.79 -- hedging cost £213.07
  - C2g: actual £31.97 vs. naked £161.68 -- hedging cost £129.71
  - C3: actual £-20.54 vs. naked £45.59 -- hedging cost £66.14
  - C3g: actual £46.24 vs. naked £103.81 -- hedging cost £57.58
  - C4: actual £16.65 vs. naked £94.54 -- hedging cost £77.89
  - C4g: actual £91.22 vs. naked £118.47 -- hedging cost £27.25
  - C5: actual £-23.86 vs. naked £66.25 -- hedging cost £90.11
  - C6: actual £-195.33 vs. naked £125.69 -- hedging cost £321.03
  - C7: actual £6.03 vs. naked £105.75 -- hedging cost £99.72
  - C8: actual £-22.40 vs. naked £239.39 -- hedging cost £261.79
  - C9: actual £-33.96 vs. naked £134.23 -- hedging cost £168.20

**Year narrative:** 2019 produced a net loss of £-160.53 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-330.38 (gross £-212.39, capital £118.00)
  - Electricity: gross £-379.27, capital £110.64, net £-489.91
  - Gas: gross £166.88, capital £7.35, net £159.53
- Treasury at year end: £26,080.21
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2020-03-04 period 37, net margin £-0.99

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C3
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £-865.71
  - By billing account: C1 £-237.18, C2 £-997.23, C3 £-322.84, C4 £8.64, C5 £-1,233.95, C6 £-2,570.34, C7 £-653.07, C8 £-1,100.42, C9 £-685.02
- Bill shock events (>=20%): 29 -- C1g 2020-01-31 (33%); C5 2020-01-31 (22%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-01-31 (22%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (26%); C7 2020-10-31 (58%); C7 2020-11-30 (22%); C7 2020-12-31 (34%); C2 2020-04-30 (28%); C2g 2020-04-30 (22%); C6 2020-04-30 (40%); C6 2020-10-31 (32%); C6 2020-12-31 (25%); C8 2020-04-30 (47%); C8 2020-05-31 (24%); C8 2020-06-30 (31%); C8 2020-09-30 (49%); C8 2020-10-31 (63%); C8 2020-12-31 (41%); C9 2020-04-30 (28%); C9 2020-05-31 (24%); C9 2020-06-30 (35%); C9 2020-09-30 (41%); C9 2020-10-31 (48%); C9 2020-12-31 (34%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 23%, C4 20%, C5 35%, C6 38%, C7 32%, C8 38%, C9 41%

**Pricing & Margin**

- C1 (electricity): tariff £51.68-£61.26/MWh, net margin £-3.05 -- **net-negative**
- C1g (gas): tariff £15.26-£16.00/MWh, net margin £25.27
- C2 (electricity): tariff £40.68-£62.36/MWh, net margin £-74.33 -- **net-negative**
- C2g (gas): tariff £14.98-£22.48/MWh, net margin £56.35
- C3 (electricity): tariff £49.00/MWh, net margin £-8.83 -- **net-negative**
- C3g (gas): tariff £16.78/MWh, net margin £24.11
- C4 (electricity): tariff £44.73-£49.15/MWh, net margin £-1.51 -- **net-negative**
- C4g (gas): tariff £8.29-£13.99/MWh, net margin £53.79
- C5 (electricity): tariff £51.68-£61.26/MWh, net margin £-28.20 -- **net-negative**
- C6 (electricity): tariff £40.68-£62.36/MWh, net margin £-256.17 -- **net-negative**
- C7 (electricity): tariff £40.61-£91.89/MWh, net margin £4.51
- C8 (electricity): tariff £31.96-£93.54/MWh, net margin £-76.20 -- **net-negative**
- C9 (electricity): tariff £25.40-£73.50/MWh, net margin £-46.13 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -55.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 144, average clarity 0.890, average bill shock 11.4%, bad debt provision £261.60, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,457.44 vs. naked (unhedged) net margin: £-5,055.07
- hedging added £3,597.64 vs. a fully unhedged book (commodity-only: actual net £-1,457.44 vs. naked net £-5,055.07)
  - C1: actual £-67.03 vs. naked £-272.32 -- hedging added £205.29
  - C1g: actual £-49.41 vs. naked £-330.69 -- hedging added £281.29
  - C2: actual £-92.65 vs. naked £-43.09 -- hedging cost £49.56
  - C2g: actual £58.09 vs. naked £49.40 -- hedging added £8.69
  - C4: actual £-86.03 vs. naked £-257.90 -- hedging added £171.86
  - C4g: actual £-99.32 vs. naked £-381.76 -- hedging added £282.44
  - C5: actual £-359.10 vs. naked £-1,525.07 -- hedging added £1,165.98
  - C6: actual £-321.32 vs. naked £-608.55 -- hedging added £287.23
  - C7: actual £-210.69 vs. naked £-913.72 -- hedging added £703.03
  - C8: actual £-142.88 vs. naked £-262.96 -- hedging added £120.08
  - C9: actual £-87.11 vs. naked £-508.42 -- hedging added £421.31

**Year narrative:** 2020 produced a net loss of £-330.38 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 29 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-2,743.14 (gross £-2,547.19, capital £195.95)
  - Electricity: gross £-2,294.48, capital £187.87, net £-2,482.35
  - Gas: gross £-252.71, capital £8.08, net £-260.79
- Treasury at year end: £24,420.30
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C4 0.95 (avg 0.95), C4g 0.95 (avg 0.95), C6 0.95 (avg 0.95), C7 0.95 (avg 0.95), C8 0.95 (avg 0.95), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 19
  - 2021-04-02: treasury £23,290.35, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-05-02: treasury £23,236.40, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-06-01: treasury £23,202.24, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-07-01: treasury £23,186.36, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-07-31: treasury £23,171.84, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-08-30: treasury £23,156.14, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-09-29: treasury £23,136.79, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-10-29: treasury £23,105.19, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-11-28: treasury £23,046.83, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-12-28: treasury £22,976.59, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-07-27: treasury £22,770.07, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-08-26: treasury £22,757.06, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-09-25: treasury £22,741.97, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-10-25: treasury £22,718.71, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-11-24: treasury £22,687.70, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-12-24: treasury £22,645.75, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-10-22: treasury £22,427.56, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-11-21: treasury £22,394.81, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-12-21: treasury £22,359.15, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.44
- Worst single period: C5 on 2021-01-08 period 39, net margin £-2.16

**Customer Book**

- Active accounts: 11 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2021): £-1,024.46
  - By billing account: C1 £-371.30, C2 £-1,099.51, C3 £-314.66, C4 £-494.21, C5 £-1,268.62, C6 £-2,879.04, C7 £-759.24, C8 £-1,231.57, C9 £-802.01
- Bill shock events (>=20%): 29 -- C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (53%); C7 2021-11-30 (62%); C2g 2021-04-30 (20%); C6 2021-04-30 (21%); C6 2021-06-30 (34%); C6 2021-10-31 (26%); C6 2021-11-30 (48%); C8 2021-04-30 (24%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (22%); C8 2021-10-31 (66%); C8 2021-11-30 (79%); C9 2021-02-28 (22%); C9 2021-05-31 (23%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (60%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-10-31 (137%); C4g 2021-10-31 (132%)
- Churn risk (accounts renewing in 2021): 6 at risk (≥20% churn prob): C2 20%, C5 35%, C6 38%, C7 35%, C8 41%, C9 35%

**Pricing & Margin**

- C1 (electricity): tariff £61.26/MWh, net margin £-66.33 -- **net-negative**
- C1g (gas): tariff £16.00/MWh, net margin £-49.21 -- **net-negative**
- C2 (electricity): tariff £40.68-£70.88/MWh, net margin £-295.12 -- **net-negative**
- C2g (gas): tariff £14.98-£22.90/MWh, net margin £1.11
- C4 (electricity): tariff £44.73-£199.38/MWh, net margin £-174.42 -- **net-negative**
- C4g (gas): tariff £8.29-£38.47/MWh, net margin £-212.68 -- **net-negative**
- C5 (electricity): tariff £61.26/MWh, net margin £-353.28 -- **net-negative**
- C6 (electricity): tariff £40.68-£70.88/MWh, net margin £-786.58 -- **net-negative**
- C7 (electricity): tariff £48.13-£317.74/MWh, net margin £-214.57 -- **net-negative**
- C8 (electricity): tariff £31.96-£106.32/MWh, net margin £-389.27 -- **net-negative**
- C9 (electricity): tariff £25.40-£117.60/MWh, net margin £-202.78 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -7.7% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £26,107.80 -> £21,531.43 (17.5%)
- Bills issued: 132, average clarity 0.879, average bill shock 14.4%, bad debt provision £262.67, avg complaint probability 3.9%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-3,960.59 vs. naked (unhedged) net margin: £-10,536.05
- hedging added £6,575.46 vs. a fully unhedged book (commodity-only: actual net £-3,960.59 vs. naked net £-10,536.05)
  - C2: actual £-379.18 vs. naked £-646.98 -- hedging added £267.80
  - C2g: actual £-18.79 vs. naked £-575.60 -- hedging added £556.81
  - C4: actual £-386.89 vs. naked £-384.26 -- hedging cost £2.63
  - C4g: actual £-527.37 vs. naked £-1,526.51 -- hedging added £999.15
  - C6: actual £-992.81 vs. naked £-3,360.56 -- hedging added £2,367.75
  - C7: actual £-812.78 vs. naked £-837.76 -- hedging added £24.98
  - C8: actual £-513.42 vs. naked £-1,593.64 -- hedging added £1,080.21
  - C9: actual £-329.35 vs. naked £-1,610.74 -- hedging added £1,281.39

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-2,743.14 across 11 accounts. The risk committee intervened 19 time(s), raising hedge fractions in response to elevated VaR. 29 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £-5,340.86 (gross £-5,230.81, capital £110.05)
  - Electricity: gross £-4,480.21, capital £105.40, net £-4,585.61
  - Gas: gross £-750.60, capital £4.65, net £-755.25
- Treasury at year end: £20,176.16
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 1.00 (avg 1.00), C4g 1.00 (avg 1.00), C6 1.00 (avg 1.00), C7 1.00 (avg 1.00), C8 1.00 (avg 1.00), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 70
  - 2022-02-01: treasury £23,497.01, C2->0.95, C6->1.00, VaR (current £1,813.45 / stressed £792.72) ratio 2.29
  - 2022-03-03: treasury £23,389.52, C2->0.95, C6->1.00, VaR (current £1,813.45 / stressed £792.72) ratio 2.29
  - 2022-01-27: treasury £22,907.07, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2022-02-26: treasury £22,846.26, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2022-03-28: treasury £22,784.53, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2022-01-23: treasury £22,604.49, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-02-22: treasury £22,566.13, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-03-24: treasury £22,528.93, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-04-23: treasury £22,496.75, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-05-23: treasury £22,473.81, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-06-22: treasury £22,454.82, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-01-20: treasury £22,325.05, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-02-19: treasury £22,290.82, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-03-21: treasury £22,255.08, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-04-20: treasury £22,224.22, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-05-20: treasury £22,196.27, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-06-19: treasury £22,169.26, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-07-19: treasury £22,140.24, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-08-18: treasury £22,109.57, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-09-17: treasury £22,076.94, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-01-09: treasury £21,507.78, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-02-08: treasury £21,413.82, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-03-10: treasury £21,328.57, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-09: treasury £21,247.52, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-05-09: treasury £21,183.44, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-06-08: treasury £21,135.21, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-07-08: treasury £21,090.25, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-08-07: treasury £21,042.83, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-09-06: treasury £20,992.89, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-10-06: treasury £20,938.70, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-11-05: treasury £20,885.70, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-05: treasury £20,808.38, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-05: treasury £20,699.57, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-05-05: treasury £20,631.38, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-06-04: treasury £20,592.75, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-07-04: treasury £20,563.11, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-08-03: treasury £20,536.96, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-09-02: treasury £20,506.39, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-10-02: treasury £20,458.05, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-11-01: treasury £20,413.04, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-01: treasury £20,333.65, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-31: treasury £20,177.76, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-03-31: treasury £19,877.04, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-04-30: treasury £19,713.40, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-05-30: treasury £19,594.78, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-06-29: treasury £19,491.57, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-07-29: treasury £19,399.95, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-08-28: treasury £19,314.90, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-09-27: treasury £19,206.79, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-10-27: treasury £19,080.11, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-11-26: treasury £18,911.07, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-12-26: treasury £18,673.35, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-04-25: treasury £17,938.12, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-05-25: treasury £17,888.07, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-06-25: treasury £17,844.95, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-07-25: treasury £17,813.57, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-08-24: treasury £17,784.98, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-09-23: treasury £17,748.55, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-10-23: treasury £17,688.09, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-11-22: treasury £17,615.54, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-12-22: treasury £17,493.41, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-07-21: treasury £17,134.47, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-08-20: treasury £17,129.90, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-09-19: treasury £17,123.19, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-10-19: treasury £17,121.16, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-11-18: treasury £17,122.60, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-12-18: treasury £17,130.96, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-10-16: treasury £17,088.41, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2022-11-15: treasury £16,988.63, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2022-12-15: treasury £16,882.85, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.49
- Worst single period: C4g on 2022-09-30 period 1, net margin £-3.74

**Customer Book**

- Active accounts: 9 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2022): £-1,277.90
  - By billing account: C1 £-327.36, C2 £-947.83, C2_2 £-502.28, C3 £-310.53, C4 £-1,633.54, C5 £-1,407.42, C6 £-3,713.25, C7 £-1,265.11, C8 £-1,765.59, C9 £-906.08
- Bill shock events (>=20%): 37 -- C7 2022-01-31 (160%); C7 2022-02-28 (27%); C7 2022-04-30 (23%); C7 2022-05-31 (36%); C7 2022-06-30 (27%); C7 2022-09-30 (35%); C7 2022-11-30 (65%); C7 2022-12-31 (54%); C6 2022-04-30 (89%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-04-30 (74%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (84%); C8 2022-11-30 (72%); C8 2022-12-31 (57%); C9 2022-04-30 (21%); C9 2022-05-31 (29%); C9 2022-06-30 (28%); C9 2022-07-31 (39%); C9 2022-09-30 (49%); C9 2022-10-31 (31%); C9 2022-11-30 (45%); C9 2022-12-31 (53%); C4 2022-10-31 (21%); C4g 2022-10-31 (168%); C2_2 2022-04-30 (1718%); C2_2 2022-05-31 (39%); C2_2 2022-06-30 (33%); C2_2 2022-09-30 (76%); C2_2 2022-11-30 (65%); C2_2 2022-12-31 (57%)
- Churn risk (accounts renewing in 2022): 5 at risk (≥20% churn prob): C4 23%, C6 32%, C7 35%, C8 35%, C9 38%

**Pricing & Margin**

- C2 (electricity): tariff £70.88/MWh, net margin £-114.57 -- **net-negative**
- C2_2 (electricity): tariff £245.84/MWh, net margin £-548.16 -- **net-negative**
- C2g (gas): tariff £22.90/MWh, net margin £-9.45 -- **net-negative**
- C4 (electricity): tariff £199.38-£241.40/MWh, net margin £-597.63 -- **net-negative**
- C4g (gas): tariff £38.47-£130.32/MWh, net margin £-745.80 -- **net-negative**
- C6 (electricity): tariff £70.88-£245.84/MWh, net margin £-1,574.89 -- **net-negative**
- C7 (electricity): tariff £166.44-£338.23/MWh, net margin £-814.41 -- **net-negative**
- C8 (electricity): tariff £55.69-£368.76/MWh, net margin £-746.10 -- **net-negative**
- C9 (electricity): tariff £61.60-£298.46/MWh, net margin £-189.85 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -2.1% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £24,420.27 -> £14,603.20 (40.2%)
- Bills issued: 88, average clarity 0.807, average bill shock 44.1%, bad debt provision £385.38, avg complaint probability 5.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-7,266.74 vs. naked (unhedged) net margin: £900.89
- hedging cost £8,167.63 vs. a fully unhedged book (commodity-only: actual net £-7,266.74 vs. naked net £900.89)
  - C2_2: actual £-841.78 vs. naked £215.80 -- hedging cost £1,057.59
  - C4: actual £-1,163.17 vs. naked £587.06 -- hedging cost £1,750.23
  - C4g: actual £-1,365.81 vs. naked £1,499.15 -- hedging cost £2,864.96
  - C6: actual £-1,868.79 vs. naked £-2,237.16 -- hedging added £368.37
  - C7: actual £-1,152.92 vs. naked £941.42 -- hedging cost £2,094.34
  - C8: actual £-875.50 vs. naked £-43.36 -- hedging cost £832.14
  - C9: actual £1.23 vs. naked £-62.01 -- hedging added £63.24

**Year narrative:** 2022 (flagged crisis year) produced a net loss of £-5,340.86 across 9 accounts. The risk committee intervened 70 time(s), raising hedge fractions in response to elevated VaR. 37 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £-3,873.88 (gross £-3,782.75, capital £91.13)
  - Electricity: gross £-2,773.88, capital £85.32, net £-2,859.21
  - Gas: gross £-1,008.87, capital £5.81, net £-1,014.68
- Treasury at year end: £13,554.40
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.90 (avg 0.90), C6 1.00 (avg 1.00), C7 0.90 (avg 0.90), C8 0.90 (avg 0.90), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 72
  - 2023-01-30: treasury £20,070.90, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-03-01: treasury £19,974.82, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-01-25: treasury £18,453.96, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2023-02-24: treasury £18,245.32, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2023-03-26: treasury £18,037.47, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2023-01-21: treasury £17,392.81, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-02-20: treasury £17,272.34, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-03-22: treasury £17,162.54, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-01-17: treasury £17,131.87, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-02-16: treasury £17,140.14, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-03-18: treasury £17,145.04, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-04-17: treasury £17,142.50, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-05-17: treasury £17,144.74, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-06-16: treasury £17,141.88, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-01-14: treasury £16,777.07, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-02-13: treasury £16,671.13, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-03-15: treasury £16,565.35, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-04-14: treasury £16,468.93, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-05-14: treasury £16,377.76, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-06-13: treasury £16,291.76, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-07-13: treasury £16,205.74, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-08-12: treasury £16,120.02, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-09-11: treasury £16,032.64, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-01-03: treasury £14,594.04, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-02-02: treasury £14,456.43, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-03-04: treasury £14,329.18, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-03: treasury £14,203.84, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-05-03: treasury £14,101.16, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-06-02: treasury £14,024.61, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-07-02: treasury £13,963.58, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-01: treasury £13,904.26, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-31: treasury £13,844.67, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-09-30: treasury £13,781.49, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-30: treasury £13,697.12, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-29: treasury £13,580.05, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-12-29: treasury £13,459.04, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-29: treasury £13,469.48, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-05-29: treasury £13,479.00, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-06-28: treasury £13,483.77, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-07-28: treasury £13,488.71, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-27: treasury £13,492.94, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-09-26: treasury £13,498.35, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-26: treasury £13,506.84, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-25: treasury £13,523.76, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-12-25: treasury £13,547.58, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-24: treasury £13,638.85, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-05-24: treasury £13,644.36, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-06-23: treasury £13,648.43, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-07-23: treasury £13,652.22, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-22: treasury £13,655.80, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-09-21: treasury £13,659.69, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-21: treasury £13,664.50, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-20: treasury £13,671.65, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-12-20: treasury £13,680.53, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-19: treasury £13,723.30, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-05-19: treasury £13,749.37, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-06-18: treasury £13,758.28, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-07-18: treasury £13,761.20, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-08-17: treasury £13,764.86, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-09-16: treasury £13,769.00, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-10-16: treasury £13,776.30, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-11-15: treasury £13,806.72, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-12-15: treasury £13,859.07, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-07-14: treasury £14,032.85, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-08-13: treasury £14,037.06, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-09-12: treasury £14,040.37, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-10-12: treasury £14,049.56, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-11-11: treasury £14,072.44, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-12-11: treasury £14,098.27, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-10-09: treasury £14,240.13, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2023-11-08: treasury £14,230.14, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2023-12-08: treasury £14,219.44, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 1.95
- Worst single period: C4g on 2023-01-01 period 1, net margin £-3.74

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2023): £-1,337.02
  - By billing account: C1 £-333.67, C2 £-931.10, C2_2 £-519.59, C3 £-312.59, C4 £-2,754.49, C5 £-1,294.37, C6 £-3,477.49, C7 £-1,683.28, C8 £-1,342.33, C9 £-721.31
- Bill shock events (>=20%): 29 -- C7 2023-05-31 (32%); C7 2023-06-30 (37%); C7 2023-10-31 (56%); C7 2023-11-30 (72%); C6 2023-04-30 (32%); C6 2023-05-31 (23%); C6 2023-06-30 (23%); C6 2023-10-31 (38%); C6 2023-11-30 (44%); C8 2023-04-30 (34%); C8 2023-05-31 (41%); C8 2023-06-30 (44%); C8 2023-10-31 (99%); C8 2023-11-30 (70%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (22%); C9 2023-10-31 (74%); C9 2023-11-30 (53%); C4 2023-10-31 (45%); C4g 2023-10-31 (65%); C2_2 2023-04-30 (33%); C2_2 2023-05-31 (41%); C2_2 2023-06-30 (42%); C2_2 2023-10-31 (94%); C2_2 2023-11-30 (66%)
- Churn risk (accounts renewing in 2023): 5 at risk (≥20% churn prob): C2_2 35%, C6 26%, C7 38%, C8 38%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £199.76-£245.84/MWh, net margin £-196.79 -- **net-negative**
- C4 (electricity): tariff £90.77-£241.40/MWh, net margin £-879.18 -- **net-negative**
- C4g (gas): tariff £33.89-£130.32/MWh, net margin £-1,014.68 -- **net-negative**
- C6 (electricity): tariff £199.76-£245.84/MWh, net margin £-574.46 -- **net-negative**
- C7 (electricity): tariff £89.24-£338.23/MWh, net margin £-1,151.25 -- **net-negative**
- C8 (electricity): tariff £156.95-£368.76/MWh, net margin £-151.03 -- **net-negative**
- C9 (electricity): tariff £100.67-£298.46/MWh, net margin £93.51

**Portfolio Health**

- Capital cost ratio: -2.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £20,176.15 -> £13,455.93 (33.3%)
- Bills issued: 84, average clarity 0.816, average bill shock 19.6%, bad debt provision £453.19, avg complaint probability 5.1%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £619.39 vs. naked (unhedged) net margin: £1,849.92
- hedging cost £1,230.52 vs. a fully unhedged book (commodity-only: actual net £619.39 vs. naked net £1,849.92)
  - C2_2: actual £175.88 vs. naked £940.09 -- hedging cost £764.20
  - C4: actual £-103.09 vs. naked £3.88 -- hedging cost £106.98
  - C4g: actual £28.17 vs. naked £-72.75 -- hedging added £100.92
  - C6: actual £75.12 vs. naked £-237.85 -- hedging added £312.97
  - C7: actual £-91.79 vs. naked £54.21 -- hedging cost £146.00
  - C8: actual £321.78 vs. naked £851.15 -- hedging cost £529.36
  - C9: actual £213.32 vs. naked £311.19 -- hedging cost £97.86

**Year narrative:** 2023 produced a net loss of £-3,873.88 across 7 accounts. The risk committee intervened 72 time(s), raising hedge fractions in response to elevated VaR. 29 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £207.18 (gross £358.61, capital £151.43)
  - Electricity: gross £320.50, capital £138.36, net £182.14
  - Gas: gross £38.11, capital £13.07, net £25.04
- Treasury at year end: £14,084.04
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 33
  - 2024-01-24: treasury £13,577.88, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-02-23: treasury £13,602.70, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-03-24: treasury £13,628.78, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-01-19: treasury £13,689.51, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-02-18: treasury £13,697.52, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-03-19: treasury £13,705.69, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-01-14: treasury £13,906.38, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-02-13: treasury £13,961.56, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-03-14: treasury £14,008.91, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-01-10: treasury £14,127.95, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-02-09: treasury £14,163.07, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-03-10: treasury £14,188.41, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-04-09: treasury £14,212.46, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-05-09: treasury £14,229.73, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-06-08: treasury £14,238.66, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-01-07: treasury £14,211.21, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-02-06: treasury £14,202.22, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-03-07: treasury £14,193.46, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-04-06: treasury £14,185.09, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-05-06: treasury £14,177.93, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-06-05: treasury £14,170.18, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-07-05: treasury £14,162.58, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-08-04: treasury £14,154.81, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-09-03: treasury £14,147.98, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-04-23: treasury £14,156.48, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-01-25: treasury £14,164.51, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-02-24: treasury £14,161.22, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-03-25: treasury £14,154.88, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-04-24: treasury £14,152.17, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-05-24: treasury £14,143.37, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-06-23: treasury £14,133.40, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-07-23: treasury £14,122.23, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-08-22: treasury £14,111.70, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 1.18
- Worst single period: C9 on 2024-12-12 period 41, net margin £-0.15

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2024): £-1,162.84
  - By billing account: C1 £-287.51, C2 £-998.95, C2_2 £-465.41, C3 £-241.30, C4 £-2,034.22, C5 £-1,277.10, C6 £-2,933.45, C7 £-1,517.96, C8 £-1,237.51, C9 £-635.04
- Bill shock events (>=20%): 25 -- C7 2024-01-31 (25%); C7 2024-02-29 (27%); C7 2024-05-31 (37%); C7 2024-09-30 (34%); C7 2024-10-31 (37%); C7 2024-11-30 (49%); C8 2024-02-29 (23%); C8 2024-04-30 (51%); C8 2024-05-31 (49%); C8 2024-07-31 (27%); C8 2024-09-30 (74%); C8 2024-10-31 (36%); C8 2024-11-30 (62%); C9 2024-05-31 (49%); C9 2024-07-31 (43%); C9 2024-09-30 (54%); C9 2024-10-31 (23%); C9 2024-11-30 (47%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (51%); C2_2 2024-05-31 (48%); C2_2 2024-07-31 (26%); C2_2 2024-09-30 (66%); C2_2 2024-10-31 (35%); C2_2 2024-11-30 (58%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C4 23%, C6 38%, C7 38%, C8 41%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £98.34-£199.76/MWh, net margin £86.12
- C4 (electricity): tariff £90.77/MWh, net margin £-72.53 -- **net-negative**
- C4g (gas): tariff £33.89/MWh, net margin £25.04
- C6 (electricity): tariff £199.76/MWh, net margin £25.07
- C7 (electricity): tariff £89.24-£176.83/MWh, net margin £-90.35 -- **net-negative**
- C8 (electricity): tariff £77.27-£299.63/MWh, net margin £197.68
- C9 (electricity): tariff £58.33-£192.20/MWh, net margin £36.15

**Portfolio Health**

- Capital cost ratio: 42.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 69, average clarity 0.807, average bill shock 19.9%, bad debt provision £241.63, avg complaint probability 5.2%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-145.38 vs. naked (unhedged) net margin: £-1,036.14
- hedging added £890.75 vs. a fully unhedged book (commodity-only: actual net £-145.38 vs. naked net £-1,036.14)
  - C2_2: actual £-8.16 vs. naked £-132.51 -- hedging added £124.35
  - C7: actual £-15.24 vs. naked £-118.41 -- hedging added £103.17
  - C8: actual £73.05 vs. naked £-240.37 -- hedging added £313.42
  - C9: actual £-195.03 vs. naked £-544.85 -- hedging added £349.82

**Year narrative:** 2024 produced a net gain of £207.18 across 7 accounts. The risk committee intervened 33 time(s), raising hedge fractions in response to elevated VaR. 25 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £-329.57 (gross £-259.10, capital £70.47)
  - Electricity: gross £-259.10, capital £70.47, net £-329.57
- Treasury at year end: £13,946.83
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C8 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C2_2 on 2025-01-08 period 36, net margin £-1.50

**Customer Book**

- Active accounts: 4 (C2_2, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 0, gas (dual-fuel): 0
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £-1,132.33
  - By billing account: C1 £-254.88, C2 £-967.62, C2_2 £-461.86, C3 £-265.27, C4 £-1,980.87, C5 £-1,298.46, C6 £-2,942.81, C7 £-1,375.65, C8 £-1,217.79, C9 £-558.07
- Bill shock events (>=20%): 18 -- C7 2025-01-31 (29%); C7 2025-04-30 (37%); C7 2025-05-31 (23%); C7 2025-06-07 (80%); C8 2025-01-31 (39%); C8 2025-02-28 (24%); C8 2025-04-30 (27%); C8 2025-05-31 (37%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (33%); C9 2025-06-07 (72%); C2_2 2025-01-31 (38%); C2_2 2025-02-28 (24%); C2_2 2025-04-30 (27%); C2_2 2025-05-31 (36%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £98.34-£125.76/MWh, net margin £-125.86 -- **net-negative**
- C7 (electricity): tariff £92.63-£176.83/MWh, net margin £-11.05 -- **net-negative**
- C8 (electricity): tariff £77.27-£188.64/MWh, net margin £-88.13 -- **net-negative**
- C9 (electricity): tariff £58.33-£111.36/MWh, net margin £-104.53 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -27.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 24, average clarity 0.723, average bill shock 32.9%, bad debt provision £85.29, avg complaint probability 7.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-225.06 vs. naked (unhedged) net margin: £-123.47
- hedging cost £101.60 vs. a fully unhedged book (commodity-only: actual net £-225.06 vs. naked net £-123.47)
  - C2_2: actual £-110.64 vs. naked £-0.45 -- hedging cost £110.19
  - C8: actual £-114.43 vs. naked £-123.01 -- hedging added £8.59

**Year narrative:** 2025 produced a net loss of £-329.57 across 4 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 18 customer(s) experienced a bill shock of >=20%.
