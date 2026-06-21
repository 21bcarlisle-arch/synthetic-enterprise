# Annual Report — The Synthetic Enterprise

## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £29,846.19
- Final treasury: £25,609.77
  (£-4,236.42 net change)
- Customer bills (all-in): £159,465.47
  VAT remitted to HMRC: (£13,101.76) | Revenue (ex-VAT): £146,363.71
  Non-commodity pass-through: (£42,887.46)
- Gross margin: £7,389.01
- Capital costs: £1,227.63
- Net margin: £6,161.38
- Capital cost ratio: 16.6% of gross
- Net margin as % of revenue: 4.2%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 172
- Bills issued: 1117, average clarity 0.869,
  service quality score 0.919
- Enterprise value (CLV sum across 10 billing accounts): £-8,173.22
- Cost to serve (whole portfolio): £6,331.99, net margin after cost to serve: £-170.61
- Hedge effectiveness (whole window): hedging cost £1,656.28 vs. a fully unhedged book (commodity-only: actual net £-4,236.42 vs. naked net £-2,580.14)

- **2021** (crisis year): net margin £-1,402.77, 4 risk committee wake-up(s).
- **2022** (crisis year): net margin £-1,500.70, 30 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £7,389.01, capital £1,227.63, net £6,161.38. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: -40.8% (commodity basis, comparable to old model) / 16.6% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £-1,402.77 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 4.2%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,161.38
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £-2,580.14
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £1,656.28 vs. a fully unhedged book (commodity-only: actual net £-4,236.42 vs. naked net £-2,580.14)
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
| 2016 | £-419.72 | £-357.05 | £66.85 | £-709.93 |
| 2017 | £-285.45 | £-330.90 | £106.87 | £-509.48 |
| 2018 | £-259.53 | £39.05 | £146.70 | £-73.78 |
| 2019 | £-180.16 | £265.29 | £205.38 | £290.52 |
| 2020 | £-157.72 | £-19.20 | £126.19 | £-50.74 |
| 2021 | £-667.98 | £-626.10 | £-108.69 | £-1,402.77 |
| 2022 | £-467.72 | £-838.06 | £-194.92 | £-1,500.70 |
| 2023 | £81.97 | £-782.99 | £-265.00 | £-966.02 |
| 2024 | £114.29 | £715.13 | £98.86 | £928.28 |
| 2025 | £0.00 | £-241.81 | £0.00 | £-241.81 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **43** renewals.  Lost (churned): **6** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8255 |
| C1 | 2018-12-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.4100 | 0.3500 | 0.7335 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6312 |
| C1 | 2019-12-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1700 | 0.5500 | 0.9235 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.4829 |
| C2 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.2000 | 0.5500 | 0.9100 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.2000 | 0.5500 | 0.9100 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0637 |
| C2_2 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.2600 | 0.3500 | 0.8310 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C2_2 | 2024-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.2300 | 0.5500 | 0.8965 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4099 |
| C2_2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 147.9%
- **Average signed error:** +46.6% (over-estimates vs SIM)
- **Renewal events with estimates:** 49

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +222.5% | 222.5% |
| 2017 | 3 | -73.8% | 73.8% |
| 2018 | 3 | -54.8% | 54.8% |
| 2019 | 3 | -100.0% | 100.0% |
| 2020 | 9 | -68.8% | 68.8% |
| 2021 | 8 | +381.3% | 381.3% |
| 2022 | 6 | +113.2% | 160.2% |
| 2023 | 6 | -41.6% | 117.4% |
| 2024 | 6 | -84.3% | 84.3% |
| 2025 | 2 | -25.3% | 25.3% |

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
| 2016 | 17 | 21.2% | 35.6% |
| 2017 | 13 | 14.9% | 30.9% |
| 2018 | 13 | 15.5% | 40.4% |
| 2019 | 13 | 12.9% | 23.3% |
| 2020 | 12 | 19.6% | 32.2% |
| 2021 | 10 | 26.7% | 42.0% |
| 2022 | 8 | 28.2% | 32.8% |
| 2023 | 7 | 8.0% | 19.9% |
| 2024 | 6 | 13.5% | 26.2% |
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
| 2016 | 3 | 2.23× ⚠ | 6.24× |
| 2017 | 3 | 0.74× | 0.81× |
| 2018 | 3 | 0.55× | 0.79× |
| 2019 | 3 | 1.00× | 1.00× |
| 2020 | 9 | 0.69× | 1.00× |
| 2021 | 8 | 3.81× ⚠ | 18.00× |
| 2022 | 6 | 1.60× | 3.75× |
| 2023 | 6 | 1.17× | 2.27× |
| 2024 | 6 | 0.84× | 1.00× |
| 2025 | 2 | 0.25× | 0.27× |

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **7** (6 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.17, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.20, company est=0.95 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.95 |
| 2022-03-31 | CHURN | C2 | SIM p=0.20, company est=0.95 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.34 |
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
| C7 | 120,842 | 40,643 | 33.6% | £7,058.40 | £7,364.59 | £173.67/MWh | £91.83/MWh | +3.1% |
| C8 | 106,723 | 46,761 | 43.8% | £7,833.36 | £5,279.53 | £167.52/MWh | £88.05/MWh | +10.0% |
| C9 | 109,388 | 46,156 | 42.2% | £5,898.24 | £4,237.48 | £127.79/MWh | £67.01/MWh | +8.8% |

Total HH revenue: £37,671.60 vs flat equivalent £35,229.10 (+6.9% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 19 | 102% | C8 (2016-10-31) |
| 2017 | 25 | 83% | C8 (2017-11-30) |
| 2018 | 33 | 54% | C8 (2018-10-31) |
| 2019 | 33 | 84% | C8 (2019-10-31) |
| 2020 | 28 | 63% | C8 (2020-10-31) |
| 2021 | 32 | 200% | C4g (2021-10-31) |
| 2022 | 36 | 1718% | C2_2 (2022-04-30) |
| 2023 | 29 | 100% | C8 (2023-10-31) |
| 2024 | 25 | 74% | C8 (2024-09-30) |
| 2025 | 18 | 80% | C7 (2025-06-07) |

Total: **278** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1718% | no |
| 2021-10-31 | C4g | +200% | no |
| 2022-01-31 | C7 | +199% | no |
| 2021-10-31 | C4 | +163% | yes |
| 2022-10-31 | C4g | +159% | no |
| 2016-10-31 | C8 | +102% | no |
| 2023-10-31 | C8 | +100% | no |
| 2022-04-30 | C6 | +96% | yes |
| 2023-10-31 | C2_2 | +96% | no |
| 2022-09-30 | C8 | +85% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 9% | 9% | 0 |
| 2017 | 4 | 21% | 31% | 2 ⚠ |
| 2018 | 4 | 32% | 43% | 4 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 3 | 5% | 14% | 0 |
| 2021 | 2 | 72% | 95% | 2 ⚠ |
| 2022 | 1 | 95% | 95% | 1 ⚠ |
| 2023 | 1 | 0% | 0% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-09-30 | C4g | £8.8 | £57.2 (+552%) | 95% |
| 2022-09-30 | C4g | £57.2 | £174.5 (+205%) | 95% |
| 2021-03-31 | C2g | £13.9 | £24.5 (+76%) | 49% |
| 2018-04-01 | C2g | £16.4 | £26.6 (+62%) | 43% |
| 2018-10-01 | C4g | £20.9 | £29.9 (+43%) | 32% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 22 |
| Retained | 18 (82%) |
| Churned despite offer | 4 |
| Total offer cost (foregone margin) | £4,441.70 |
| Margin saved (retained customers' terms) | £11,265.50 |
| Wasted offer cost (churned anyway) | £865.36 |
| **Net ROI of retention strategy** | **£6,823.79** |
| Acquisition cost avoided (retained customers) | £3,950.00 |
| **Full economic ROI (margin + acq savings)** | **£10,773.79** |

Missed opportunities (churns with no offer): **2** (£74.54 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 2 (£74.54 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2016 | 3 | 3 | £93.70 | £742.56 | £648.86 | £0.00 |
| 2017 | 4 | 4 | £216.88 | £1268.00 | £1051.12 | £0.00 |
| 2018 | 1 | 1 | £29.40 | £243.05 | £213.65 | £0.00 |
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £26.53 |
| 2021 | 8 | 6 | £1421.82 | £2656.62 | £1234.81 | £0.00 |
| 2022 | 4 | 3 | £1778.04 | £5124.29 | £3346.25 | £0.00 |
| 2023 | 1 | 1 | £771.61 | £1230.97 | £459.37 | £0.00 |
| 2024 | 1 | 0 | £130.25 | £0.00 | £-130.25 | £48.01 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2016-12-31 | C1 | 0.36 | 3% | £6.47 | £51.61 | £150 | £45.14 | retained |
| 2016-12-31 | C5 | 0.38 | 3% | £58.77 | £493.12 | £400 | £434.35 | retained |
| 2016-12-31 | C7 | 0.33 | 3% | £28.46 | £197.82 | £150 | £169.37 | retained |
| 2017-04-01 | C2 | 0.54 | 5% | £13.42 | £78.61 | £150 | £65.19 | retained |
| 2017-04-01 | C6 | 0.51 | 5% | £167.12 | £902.66 | £400 | £735.54 | retained |
| 2017-04-01 | C8 | 0.49 | 3% | £25.74 | £216.75 | £150 | £191.01 | retained |
| 2017-10-01 | C4 | 0.31 | 3% | £10.59 | £69.98 | £150 | £59.39 | retained |
| 2018-07-01 | C9 | 0.33 | 3% | £29.40 | £243.05 | £150 | £213.65 | retained |
| 2021-03-31 | C2 | 0.73 | 5% | £16.24 | £86.72 | £150 | £70.48 | retained |
| 2021-03-31 | C6 | 0.72 | 5% | £216.77 | £1273.56 | £400 | £1056.79 | retained |
| 2021-03-31 | C8 | 0.60 | 5% | £53.48 | £264.77 | £150 | £211.29 | retained |
| 2021-06-30 | C9 | 0.82 | 8% | £90.31 | £188.26 | £150 | £97.94 | retained |
| 2021-09-30 | C4 | 0.95 | 8% | £115.87 | £215.13 | £150 | £99.26 | retained |
| 2021-12-30 | C1 | 0.95 | 8% | £62.44 | £142.83 | £150 | £-62.44 | churned_despite_offer |
| 2021-12-30 | C5 | 0.95 | 8% | £583.21 | £1596.48 | £400 | £-583.21 | churned_despite_offer |
| 2021-12-30 | C7 | 0.95 | 8% | £283.49 | £628.18 | £150 | £344.69 | retained |
| 2022-03-31 | C2 | 0.95 | 8% | £89.46 | £275.25 | £150 | £-89.46 | churned_despite_offer |
| 2022-03-31 | C6 | 0.95 | 8% | £1164.28 | £3714.43 | £400 | £2550.15 | retained |
| 2022-03-31 | C8 | 0.95 | 8% | £298.68 | £884.11 | £150 | £585.43 | retained |
| 2022-06-30 | C9 | 0.77 | 8% | £225.63 | £525.76 | £150 | £300.13 | retained |
| 2023-03-31 | C6 | 0.85 | 8% | £771.61 | £1230.97 | £400 | £459.37 | retained |
| 2024-03-30 | C6 | 0.34 | 3% | £130.25 | £337.17 | £400 | £-130.25 | churned_despite_offer |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C1 | 2016-12-31 | 2021-12-30 | 60 | churned |
| C5 | 2016-12-31 | 2021-12-30 | 60 | churned |
| C7 | 2016-12-31 | (window end) | 108 | active |
| C2 | 2017-04-01 | 2022-03-31 | 60 | churned |
| C6 | 2017-04-01 | 2024-03-30 | 84 | churned |
| C8 | 2017-04-01 | (window end) | 105 | active |
| C4 | 2017-10-01 | 2024-09-29 | 84 | churned |
| C9 | 2018-07-01 | (window end) | 90 | active |

**Eventually churned (5/8)**: C1, C5, C2, C6, C4 — avg 70 months post-retention before final churn.
**Still active (3/8)**: C7, C8, C9 — survived to simulation end.

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £-299.44 | — | — | — | — | £-1,284.77 | — | £-698.98 | — | — |
| 2017 | £-534.90 | £-1,151.78 | — | £-594.88 | £14.57 | £-2,021.63 | £-2,833.57 | £-1,098.91 | £-1,056.63 | £-1,067.38 |
| 2018 | £-197.85 | £-1,011.85 | — | £-317.31 | £216.43 | £-832.27 | £-2,355.08 | £-462.24 | £-739.29 | £-531.69 |
| 2019 | £-73.84 | £-840.47 | — | £-200.90 | £222.30 | £-748.79 | £-2,127.00 | £-306.84 | £-675.78 | £-233.41 |
| 2020 | £-93.42 | £-646.69 | — | £-179.41 | £179.71 | £-697.11 | £-1,966.38 | £-283.46 | £-513.18 | £-270.68 |
| 2021 | £-169.28 | £-691.48 | — | £-176.70 | £-21.69 | £-823.12 | £-2,051.14 | £-353.65 | £-645.65 | £-370.74 |
| 2022 | £-172.26 | £-655.04 | £-416.89 | £-197.96 | £-395.87 | £-736.50 | £-2,001.55 | £-335.58 | £-613.00 | £-322.78 |
| 2023 | £-145.67 | £-700.94 | £-321.70 | £-156.94 | £-894.78 | £-775.00 | £-1,735.90 | £-871.96 | £-451.83 | £-151.29 |
| 2024 | £-121.44 | £-652.92 | £-149.19 | £-163.09 | £-701.32 | £-700.84 | £-1,380.97 | £-616.96 | £-280.21 | £-166.39 |
| 2025 | £-121.31 | £-636.85 | £-197.36 | £-154.88 | £-685.04 | £-691.63 | £-1,353.85 | £-610.91 | £-275.48 | £-178.88 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £452.28, range £23.77–£1,133.95.

- C1: cost to serve £360.71, net margin after CTS £-378.97 — **NET_NEGATIVE** (tariff uplift needed: +24.6%)
- C1g: cost to serve £36.46, net margin after CTS £172.57
- C2: cost to serve £385.42, net margin after CTS £-929.38 — **NET_NEGATIVE** (tariff uplift needed: +33.5%)
- C2_2: cost to serve £300.65, net margin after CTS £-435.98 — **NET_NEGATIVE** (tariff uplift needed: +7.0%)
- C2g: cost to serve £42.17, net margin after CTS £-9.28 — **NET_NEGATIVE** (tariff uplift needed: +0.5%)
- C3: cost to serve £240.42, net margin after CTS £-252.68 — **NET_NEGATIVE** (tariff uplift needed: +24.7%)
- C3g: cost to serve £23.77, net margin after CTS £87.52
- C4: cost to serve £577.40, net margin after CTS £-1,119.85 — **NET_NEGATIVE** (tariff uplift needed: +16.3%)
- C4g: cost to serve £167.46, net margin after CTS £-270.37 — **NET_NEGATIVE** (tariff uplift needed: +3.4%)
- C5: cost to serve £793.86, net margin after CTS £-978.44 — **NET_NEGATIVE** (tariff uplift needed: +13.2%)
- C6: cost to serve £1,133.95, net margin after CTS £-2,745.14 — **NET_NEGATIVE** (tariff uplift needed: +15.8%)
- C7: cost to serve £807.59, net margin after CTS £-1,408.06 — **NET_NEGATIVE** (tariff uplift needed: +9.8%)
- C8: cost to serve £767.69, net margin after CTS £-653.26 — **NET_NEGATIVE** (tariff uplift needed: +5.0%)
- C9: cost to serve £694.43, net margin after CTS £-419.45 — **NET_NEGATIVE** (tariff uplift needed: +4.1%)

**Activity-Based Pricing Actions**

The following 12 customer(s) are loss-making after cost-to-serve and require immediate tariff review:
  - C1: net margin after CTS £-378.97 on revenue £1,539.05 — raise tariff by ≥24.6% to break even
  - C2: net margin after CTS £-929.38 on revenue £2,774.37 — raise tariff by ≥33.5% to break even
  - C2_2: net margin after CTS £-435.98 on revenue £6,257.49 — raise tariff by ≥7.0% to break even
  - C2g: net margin after CTS £-9.28 on revenue £1,764.62 — raise tariff by ≥0.5% to break even
  - C3: net margin after CTS £-252.68 on revenue £1,023.50 — raise tariff by ≥24.7% to break even
  - C4: net margin after CTS £-1,119.85 on revenue £6,875.28 — raise tariff by ≥16.3% to break even
  - C4g: net margin after CTS £-270.37 on revenue £7,914.88 — raise tariff by ≥3.4% to break even
  - C5: net margin after CTS £-978.44 on revenue £7,401.54 — raise tariff by ≥13.2% to break even
  - C6: net margin after CTS £-2,745.14 on revenue £17,417.79 — raise tariff by ≥15.8% to break even
  - C7: net margin after CTS £-1,408.06 on revenue £14,422.99 — raise tariff by ≥9.8% to break even
  - C8: net margin after CTS £-653.26 on revenue £13,112.89 — raise tariff by ≥5.0% to break even
  - C9: net margin after CTS £-419.45 on revenue £10,135.72 — raise tariff by ≥4.1% to break even

## Tariff Repricing Impact Assessment

Estimated churn risk at the break-even tariff level for each loss-making customer.
Active = current opportunity; churned = retrospective counterfactual.

| Customer | Fuel | Seg | Status | Uplift needed | Total loss | Churn @ B/E | Decision |
|----------|------|-----|--------|--------------|-----------|-------------|----------|
| C2g | gas | resi | active | +0.5% | £9.28 | 3% | Raise — churn risk manageable |
| C4g | gas | resi | active | +3.4% | £270.37 | 5% | Raise — churn risk manageable |
| C9 | elec | resi | active | +4.1% | £419.45 | 8% | Raise — churn risk manageable |
| C8 | elec | resi | active | +5.0% | £653.26 | 9% | Raise — churn risk manageable |
| C2_2 | elec | resi | active | +7.0% | £435.98 | 11% | Raise — churn risk manageable |
| C7 | elec | resi | active | +9.8% | £1,408.06 | 13% | Raise — churn risk manageable |
| C5 | elec | SME | churned | +13.2% | £978.44 | 16% | Raise — churn risk manageable |
| C6 | elec | SME | churned | +15.8% | £2,745.14 | 18% | Raise — churn risk manageable |
| C4 | elec | resi | churned | +16.3% | £1,119.85 | 18% | Raise — churn risk manageable |
| C1 | elec | resi | churned | +24.6% | £378.97 | 25% | Raise — churn risk manageable |
| C3 | elec | resi | churned | +24.7% | £252.68 | 25% | Raise — churn risk manageable |
| C2 | elec | resi | churned | +33.5% | £929.38 | 32% | Raise — churn risk manageable |

**Repriceable now (6)**: C2g, C4g, C9, C8, C2_2, C7 — break-even churn risk below 40%. Uplift advised.
**Missed repricing window (6 churned)**: C5, C6, C4, C1, C3, C2 — break-even price would not have triggered high churn. Earlier repricing might have changed economics.

## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 38 recovery surcharge(s) at renewal based on prior-term losses (4 gas). Avg surcharge: 13.1%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C1 | electricity | 2016-12-31 | £-30.74 | £191.26 | +11.1% | £61.36/MWh | £77.07/MWh |
| C5 | electricity | 2016-12-31 | £-181.59 | £944.27 | +14.2% | £61.36/MWh | £78.36/MWh |
| C7 | electricity | 2016-12-31 | £-92.41 | £691.35 | +8.4% | £61.36/MWh | £74.09/MWh |
| C2 | electricity | 2017-04-01 | £-97.69 | £293.81 | +20.0% | £56.89/MWh | £76.68/MWh |
| C6 | electricity | 2017-04-01 | £-344.31 | £786.99 | +20.0% | £56.89/MWh | £74.28/MWh |
| C8 | electricity | 2017-04-01 | £-144.38 | £545.49 | +20.0% | £56.89/MWh | £72.54/MWh |
| C3 | electricity | 2017-07-01 | £-34.12 | £187.45 | +13.2% | £48.36/MWh | £56.34/MWh |
| C9 | electricity | 2017-07-01 | £-61.51 | £551.22 | +6.2% | £48.36/MWh | £52.75/MWh |
| C4 | electricity | 2017-10-01 | £-54.44 | £324.01 | +11.8% | £54.12/MWh | £64.21/MWh |
| C1 | electricity | 2017-12-31 | £-46.96 | £289.71 | +11.2% | £65.33/MWh | £76.24/MWh |
| C5 | electricity | 2017-12-31 | £-215.99 | £1,420.62 | +10.2% | £65.33/MWh | £75.30/MWh |
| C7 | electricity | 2017-12-31 | £-178.02 | £968.43 | +13.4% | £65.33/MWh | £74.76/MWh |
| C2g | gas | 2018-04-01 | £-49.94 | £245.43 | +15.3% | £22.86/MWh | £26.58/MWh |
| C3 | electricity | 2018-07-01 | £-43.37 | £252.59 | +12.2% | £62.32/MWh | £80.38/MWh |
| C9 | electricity | 2018-07-01 | £-115.81 | £744.49 | +10.6% | £62.32/MWh | £79.23/MWh |
| C2 | electricity | 2019-04-01 | £-255.12 | £466.78 | +20.0% | £59.85/MWh | £71.92/MWh |
| C6 | electricity | 2019-04-01 | £-680.21 | £1,308.46 | +20.0% | £59.85/MWh | £72.41/MWh |
| C8 | electricity | 2019-04-01 | £-214.62 | £948.69 | +17.6% | £59.85/MWh | £71.73/MWh |
| C3 | electricity | 2020-06-30 | £-20.05 | £221.49 | +4.0% | £32.01/MWh | £37.93/MWh |
| C2 | electricity | 2021-03-31 | £-93.08 | £290.51 | +20.0% | £70.88/MWh | £92.82/MWh |
| C6 | electricity | 2021-03-31 | £-284.41 | £813.45 | +20.0% | £70.88/MWh | £96.34/MWh |
| C8 | electricity | 2021-03-31 | £-93.32 | £585.71 | +10.9% | £70.88/MWh | £90.42/MWh |
| C9 | electricity | 2021-06-30 | £-28.40 | £518.45 | +0.5% | £78.98/MWh | £91.26/MWh |
| C4g | gas | 2021-09-30 | £-88.71 | £193.05 | +20.0% | £43.94/MWh | £57.19/MWh |
| C1 | electricity | 2021-12-30 | £-32.10 | £265.13 | +7.1% | £232.55/MWh | £278.76/MWh |
| C5 | electricity | 2021-12-30 | £-219.13 | £1,285.80 | +12.0% | £232.55/MWh | £291.60/MWh |
| C7 | electricity | 2021-12-30 | £-107.05 | £942.29 | +6.4% | £232.55/MWh | £276.81/MWh |
| C2 | electricity | 2022-03-31 | £-222.71 | £661.99 | +20.0% | £245.84/MWh | £319.51/MWh |
| C6 | electricity | 2022-03-31 | £-517.82 | £1,797.26 | +20.0% | £245.84/MWh | £323.41/MWh |
| C8 | electricity | 2022-03-31 | £-265.50 | £1,147.11 | +18.1% | £245.84/MWh | £315.60/MWh |
| C9 | electricity | 2022-06-30 | £-170.16 | £1,129.72 | +10.1% | £189.77/MWh | £227.99/MWh |
| C4g | gas | 2022-09-30 | £-115.52 | £1,258.26 | +4.2% | £149.43/MWh | £174.50/MWh |
| C2_2 | electricity | 2023-03-31 | £-841.78 | £2,496.24 | +20.0% | £195.90/MWh | £260.22/MWh |
| C6 | electricity | 2023-03-31 | £-437.50 | £5,967.36 | +2.3% | £195.90/MWh | £214.34/MWh |
| C4 | electricity | 2023-09-30 | £-757.79 | £2,126.95 | +20.0% | £90.77/MWh | £104.41/MWh |
| C4g | gas | 2023-09-30 | £-393.67 | £3,839.07 | +5.2% | £33.89/MWh | £38.39/MWh |
| C7 | electricity | 2023-12-30 | £-941.84 | £3,091.67 | +20.0% | £113.57/MWh | £135.88/MWh |
| C2_2 | electricity | 2025-03-30 | £-56.07 | £975.98 | +0.8% | £125.76/MWh | £133.85/MWh |

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 87 renewal(s) (20 gas) based on recent portfolio-wide margin rates: 69 surcharge(s), 18 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | -18.2% | +13.1% | £61.36/MWh | £69.39/MWh |
| C1g | gas | 2016-12-31 | 12.8% | -2.4% | £17.67/MWh | £17.24/MWh |
| C5 | electricity | 2016-12-31 | -15.6% | +11.8% | £61.36/MWh | £68.60/MWh |
| C7 | electricity | 2016-12-31 | -14.8% | +11.4% | £61.36/MWh | £68.37/MWh |
| C2 | electricity | 2017-04-01 | -16.7% | +12.3% | £56.89/MWh | £63.90/MWh |
| C2g | gas | 2017-04-01 | 12.9% | -2.4% | £16.77/MWh | £16.36/MWh |
| C6 | electricity | 2017-04-01 | -9.6% | +8.8% | £56.89/MWh | £61.90/MWh |
| C8 | electricity | 2017-04-01 | -4.5% | +6.3% | £56.89/MWh | £60.45/MWh |
| C3 | electricity | 2017-07-01 | 2.2% | +2.9% | £48.36/MWh | £49.77/MWh |
| C3g | gas | 2017-07-01 | 8.2% | -0.1% | £16.31/MWh | £16.29/MWh |
| C9 | electricity | 2017-07-01 | 2.5% | +2.8% | £48.36/MWh | £49.69/MWh |
| C4 | electricity | 2017-10-01 | -4.2% | +6.1% | £54.12/MWh | £57.43/MWh |
| C4g | gas | 2017-10-01 | 7.6% | +0.2% | £20.91/MWh | £20.95/MWh |
| C1 | electricity | 2017-12-31 | -1.9% | +4.9% | £65.33/MWh | £68.55/MWh |
| C1g | gas | 2017-12-31 | 6.0% | +1.0% | £24.22/MWh | £24.47/MWh |
| C5 | electricity | 2017-12-31 | -1.2% | +4.6% | £65.33/MWh | £68.33/MWh |
| C7 | electricity | 2017-12-31 | 6.1% | +0.9% | £65.33/MWh | £65.94/MWh |
| C2 | electricity | 2018-04-01 | 13.6% | -2.8% | £67.16/MWh | £65.27/MWh |
| C2g | gas | 2018-04-01 | 6.4% | +0.8% | £22.86/MWh | £23.04/MWh |
| C6 | electricity | 2018-04-01 | -3.4% | +5.7% | £67.16/MWh | £71.00/MWh |
| C8 | electricity | 2018-04-01 | -20.0% | +14.0% | £67.16/MWh | £76.57/MWh |
| C3 | electricity | 2018-07-01 | -28.7% | +15.0% | £62.32/MWh | £71.66/MWh |
| C3g | gas | 2018-07-01 | 12.1% | -2.1% | £23.45/MWh | £22.96/MWh |
| C9 | electricity | 2018-07-01 | -27.2% | +15.0% | £62.32/MWh | £71.66/MWh |
| C4 | electricity | 2018-10-01 | -7.4% | +7.7% | £74.22/MWh | £79.92/MWh |
| C4g | gas | 2018-10-01 | 11.2% | -1.6% | £30.40/MWh | £29.90/MWh |
| C1 | electricity | 2018-12-31 | 8.0% | +0.0% | £80.49/MWh | £80.51/MWh |
| C1g | gas | 2018-12-31 | 9.7% | -0.8% | £31.73/MWh | £31.47/MWh |
| C5 | electricity | 2018-12-31 | 15.7% | -3.8% | £80.49/MWh | £77.40/MWh |
| C7 | electricity | 2018-12-31 | 11.6% | -1.8% | £80.49/MWh | £79.03/MWh |
| C2 | electricity | 2019-04-01 | 7.7% | +0.1% | £59.85/MWh | £59.93/MWh |
| C2g | gas | 2019-04-01 | 11.5% | -1.8% | £21.45/MWh | £21.08/MWh |
| C6 | electricity | 2019-04-01 | 6.3% | +0.8% | £59.85/MWh | £60.34/MWh |
| C8 | electricity | 2019-04-01 | 4.2% | +1.9% | £59.85/MWh | £60.99/MWh |
| C3 | electricity | 2019-07-01 | 5.8% | +1.1% | £48.58/MWh | £49.11/MWh |
| C3g | gas | 2019-07-01 | 11.7% | -1.9% | £16.04/MWh | £15.74/MWh |
| C9 | electricity | 2019-07-01 | 1.3% | +3.4% | £48.58/MWh | £50.22/MWh |
| C4 | electricity | 2019-10-01 | -0.3% | +4.2% | £48.90/MWh | £50.93/MWh |
| C4g | gas | 2019-10-01 | 13.4% | -2.7% | £13.64/MWh | £13.27/MWh |
| C1 | electricity | 2019-12-31 | 1.8% | +3.1% | £51.68/MWh | £53.29/MWh |
| C1g | gas | 2019-12-31 | 16.9% | -4.4% | £16.02/MWh | £15.31/MWh |
| C5 | electricity | 2019-12-31 | -0.5% | +4.2% | £51.68/MWh | £53.87/MWh |
| C7 | electricity | 2019-12-31 | 2.2% | +2.9% | £51.68/MWh | £53.18/MWh |
| C2 | electricity | 2020-03-31 | 3.8% | +2.1% | £39.78/MWh | £40.62/MWh |
| C2g | gas | 2020-03-31 | 14.5% | -3.2% | £14.33/MWh | £13.87/MWh |
| C6 | electricity | 2020-03-31 | -6.2% | +7.1% | £39.78/MWh | £42.61/MWh |
| C8 | electricity | 2020-03-31 | -15.4% | +11.7% | £39.78/MWh | £44.44/MWh |
| C3 | electricity | 2020-06-30 | -19.8% | +13.9% | £32.01/MWh | £36.45/MWh |
| C9 | electricity | 2020-06-30 | -19.8% | +13.9% | £32.01/MWh | £36.45/MWh |
| C4 | electricity | 2020-09-30 | -22.1% | +15.0% | £49.10/MWh | £56.47/MWh |
| C4g | gas | 2020-09-30 | 18.6% | -5.0% | £9.24/MWh | £8.78/MWh |
| C1 | electricity | 2020-12-30 | -14.2% | +11.1% | £63.50/MWh | £70.56/MWh |
| C1g | gas | 2020-12-30 | 3.5% | +2.3% | £17.74/MWh | £18.14/MWh |
| C5 | electricity | 2020-12-30 | -8.5% | +8.2% | £63.50/MWh | £68.75/MWh |
| C7 | electricity | 2020-12-30 | -8.8% | +8.4% | £63.50/MWh | £68.83/MWh |
| C2 | electricity | 2021-03-31 | -10.2% | +9.1% | £70.88/MWh | £77.35/MWh |
| C2g | gas | 2021-03-31 | -5.7% | +6.8% | £22.90/MWh | £24.47/MWh |
| C6 | electricity | 2021-03-31 | -18.5% | +13.3% | £70.88/MWh | £80.28/MWh |
| C8 | electricity | 2021-03-31 | -22.7% | +15.0% | £70.88/MWh | £81.51/MWh |
| C9 | electricity | 2021-06-30 | -24.2% | +15.0% | £78.98/MWh | £90.82/MWh |
| C4 | electricity | 2021-09-30 | -25.2% | +15.0% | £228.99/MWh | £263.33/MWh |
| C4g | gas | 2021-09-30 | -8.9% | +8.5% | £43.94/MWh | £47.66/MWh |
| C1 | electricity | 2021-12-30 | -15.8% | +11.9% | £232.55/MWh | £260.26/MWh |
| C5 | electricity | 2021-12-30 | -15.8% | +11.9% | £232.55/MWh | £260.26/MWh |
| C7 | electricity | 2021-12-30 | -15.8% | +11.9% | £232.55/MWh | £260.26/MWh |
| C2 | electricity | 2022-03-31 | -8.6% | +8.3% | £245.84/MWh | £266.26/MWh |
| C6 | electricity | 2022-03-31 | -11.3% | +9.6% | £245.84/MWh | £269.51/MWh |
| C8 | electricity | 2022-03-31 | -9.3% | +8.7% | £245.84/MWh | £267.13/MWh |
| C9 | electricity | 2022-06-30 | -10.3% | +9.2% | £189.77/MWh | £207.14/MWh |
| C4 | electricity | 2022-09-30 | -7.1% | +7.6% | £277.27/MWh | £298.24/MWh |
| C4g | gas | 2022-09-30 | -16.2% | +12.1% | £149.43/MWh | £167.50/MWh |
| C7 | electricity | 2022-12-30 | -7.6% | +7.8% | £224.49/MWh | £242.01/MWh |
| C2_2 | electricity | 2023-03-31 | -13.4% | +10.7% | £195.90/MWh | £216.85/MWh |
| C6 | electricity | 2023-03-31 | -5.8% | +6.9% | £195.90/MWh | £209.45/MWh |
| C8 | electricity | 2023-03-31 | -6.9% | +7.4% | £195.90/MWh | £210.44/MWh |
| C9 | electricity | 2023-06-30 | 6.5% | +0.8% | £121.82/MWh | £122.77/MWh |
| C4 | electricity | 2023-09-30 | 16.3% | -4.1% | £90.77/MWh | £87.01/MWh |
| C4g | gas | 2023-09-30 | -7.3% | +7.6% | £33.89/MWh | £36.48/MWh |
| C7 | electricity | 2023-12-30 | 8.6% | -0.3% | £113.57/MWh | £113.23/MWh |
| C2_2 | electricity | 2024-03-30 | 9.2% | -0.6% | £94.28/MWh | £93.74/MWh |
| C6 | electricity | 2024-03-30 | 3.3% | +2.3% | £94.28/MWh | £96.48/MWh |
| C8 | electricity | 2024-03-30 | 3.3% | +2.3% | £94.28/MWh | £96.48/MWh |
| C9 | electricity | 2024-06-29 | 2.1% | +2.9% | £74.24/MWh | £76.42/MWh |
| C4 | electricity | 2024-09-29 | -2.1% | +5.0% | £79.01/MWh | £82.99/MWh |
| C7 | electricity | 2024-12-29 | -2.1% | +5.0% | £121.73/MWh | £127.86/MWh |
| C2_2 | electricity | 2025-03-30 | -3.3% | +5.7% | £125.76/MWh | £132.86/MWh |
| C8 | electricity | 2025-03-30 | -15.8% | +11.9% | £125.76/MWh | £140.71/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **2** | Blind misses: **2** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 0 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £74.54 | deliberate: £0.00 | total: £74.54

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.17 | No | £26.53 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.23 | No | £48.01 |

## Dual-Fuel Account P&L (Phase 17d)

4 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C1+C1g | £-39.64 | £199.48 | £159.84 | Yes |
| C3+C3g | £-23.71 | £106.91 | £83.19 | Yes |
| C2+C2g | £-587.58 | £13.61 | £-573.98 | Yes |
| C4+C4g | £-605.91 | £-137.74 | £-743.66 | No |

Gas accretive in 3/4 dual-fuel accounts. Total gas net margin: £182.25.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £-4,236.42 across 14 billing accounts. Revenue: £93,078.44.

| # | Customer | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|---------|-------------|---------|------------|-------------|
| 1 | C9 | £10,135.72 | £274.99 | £62.55 | £212.44 | 2.1% |
| 2 | C1g | £1,479.14 | £209.02 | £9.54 | £199.48 | 13.5% |
| 3 | C3g | £959.17 | £111.29 | £4.38 | £106.91 | 11.1% |
| 4 | C2g | £1,764.62 | £32.89 | £19.28 | £13.61 | 0.8% |
| 5 | C3 | £1,023.50 | £-12.26 | £11.46 | £-23.71 | -2.3% |
| 6 | C1 | £1,539.05 | £-18.26 | £21.38 | £-39.64 | -2.6% |
| 7 | C8 | £13,112.89 | £114.43 | £213.41 | £-98.99 | -0.8% |
| 8 | C4g | £7,914.88 | £-102.90 | £34.84 | £-137.74 | -1.7% |
| 9 | C2_2 | £6,257.49 | £-135.33 | £80.94 | £-216.27 | -3.5% |
| 10 | C5 | £7,401.54 | £-184.57 | £190.90 | £-375.48 | -5.1% |
| 11 | C2 | £2,774.37 | £-543.96 | £43.62 | £-587.58 | -21.2% |
| 12 | C4 | £6,875.28 | £-542.45 | £63.46 | £-605.91 | -8.8% |
| 13 | C7 | £14,422.99 | £-600.47 | £216.52 | £-816.99 | -5.7% |
| 14 | C6 | £17,417.79 | £-1,611.18 | £255.35 | £-1,866.54 | -10.7% |

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
| Customer bills (all-in) | £159,465.47 |
|   Less: VAT remitted to HMRC | (£13,101.76) |
| = Revenue (ex-VAT) | £146,363.71 |
| Less: non-commodity pass-through | (£42,887.46) |
| Wholesale cost (settlement events) | (£96,087.24) |
| Gross margin | £7,389.01 |
| Capital charges | (£1,227.63) |
| Net margin | £6,161.38 |

_Cash reconciliation: of £159,465.47 billed, bad debt of £3,117.59 was written off, leaving £156,347.88 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £16,145.56._

| Acquisition spend | (£1,250.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £-788.62 |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £-788.62

## 2016

**Trading & Risk**

- Net margin: £-709.93 (gross £-516.19, capital £193.74)
  - Electricity: gross £-589.36, capital £187.42, net £-776.78
  - Gas: gross £73.17, capital £6.32, net £66.85
- Treasury at year end: £29,500.48
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.90), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.90), C6 0.85 (avg 0.85), C7 0.85 (avg 0.90), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 81
  - 2016-01-01: treasury £29,846.19, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-31: treasury £29,843.47, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-01: treasury £29,840.85, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-31: treasury £29,838.18, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-04-30: treasury £29,836.08, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-05-30: treasury £29,834.25, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-06-29: treasury £29,832.18, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-07-29: treasury £29,830.28, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-08-28: treasury £29,828.47, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-09-27: treasury £29,826.18, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-10-27: treasury £29,823.65, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-11-26: treasury £29,819.16, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
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
- Average CLV (Point-in-Time, year-end 2016): £-761.06
  - By billing account: C1 £-299.44, C5 £-1,284.77, C7 £-698.98
- Bill shock events (>=20%): 19 -- C5 2016-05-31 (26%); C5 2016-10-31 (40%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (77%); C7 2016-11-30 (51%); C6 2016-05-31 (25%); C6 2016-06-30 (22%); C6 2016-10-31 (39%); C6 2016-11-30 (44%); C8 2016-05-31 (40%); C8 2016-06-30 (41%); C8 2016-09-30 (22%); C8 2016-10-31 (102%); C8 2016-11-30 (68%); C9 2016-10-31 (76%); C9 2016-11-30 (58%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £50.87-£77.07/MWh, net margin £-31.09 -- **net-negative**
- C1g (gas): tariff £16.64-£17.24/MWh, net margin £29.07
- C2 (electricity): tariff £41.19/MWh, net margin £-70.11 -- **net-negative**
- C2g (gas): tariff £15.29/MWh, net margin £-1.17 -- **net-negative**
- C3 (electricity): tariff £41.81/MWh, net margin £-17.19 -- **net-negative**
- C3g (gas): tariff £13.52/MWh, net margin £14.24
- C4 (electricity): tariff £45.42/MWh, net margin £-15.95 -- **net-negative**
- C4g (gas): tariff £16.78/MWh, net margin £24.72
- C5 (electricity): tariff £50.87-£78.36/MWh, net margin £-184.05 -- **net-negative**
- C6 (electricity): tariff £41.19/MWh, net margin £-235.67 -- **net-negative**
- C7 (electricity): tariff £39.97-£76.30/MWh, net margin £-94.90 -- **net-negative**
- C8 (electricity): tariff £32.37-£61.79/MWh, net margin £-95.77 -- **net-negative**
- C9 (electricity): tariff £32.85-£62.72/MWh, net margin £-32.03 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -37.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.893, average bill shock 13.2%, bad debt provision £200.18, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,308.68 vs. naked (unhedged) net margin: £-1,287.83
- hedging cost £20.85 vs. a fully unhedged book (commodity-only: actual net £-1,308.68 vs. naked net £-1,287.83)
  - C1: actual £-77.71 vs. naked £34.21 -- hedging cost £111.92
  - C1g: actual £59.66 vs. naked £54.24 -- hedging added £5.41
  - C2: actual £-97.69 vs. naked £-39.90 -- hedging cost £57.79
  - C2g: actual £-3.80 vs. naked £24.74 -- hedging cost £28.54
  - C3: actual £-34.12 vs. naked £-49.38 -- hedging added £15.27
  - C3g: actual £25.38 vs. naked £-5.87 -- hedging added £31.25
  - C4: actual £-54.44 vs. naked £-40.09 -- hedging cost £14.36
  - C4g: actual £92.26 vs. naked £40.58 -- hedging added £51.67
  - C5: actual £-397.58 vs. naked £-270.53 -- hedging cost £127.05
  - C6: actual £-344.31 vs. naked £-657.69 -- hedging added £313.38
  - C7: actual £-270.43 vs. naked £6.73 -- hedging cost £277.16
  - C8: actual £-144.38 vs. naked £-209.19 -- hedging added £64.81
  - C9: actual £-61.51 vs. naked £-175.68 -- hedging added £114.17

**Year narrative:** 2016 produced a net loss of £-709.93 across 13 accounts. The risk committee intervened 81 time(s), raising hedge fractions in response to elevated VaR. 19 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £-509.48 (gross £-379.41, capital £130.07)
  - Electricity: gross £-496.24, capital £120.11, net £-616.35
  - Gas: gross £116.83, capital £9.96, net £106.87
- Treasury at year end: £28,585.70
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
  - 2017-01-15: treasury £28,945.46, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-02-14: treasury £28,940.76, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-03-16: treasury £28,936.33, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-04-15: treasury £28,932.60, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-05-15: treasury £28,929.09, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-06-14: treasury £28,925.90, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-07-14: treasury £28,922.77, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-08-13: treasury £28,919.68, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-09-12: treasury £28,916.42, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-10-12: treasury £28,912.76, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-11-11: treasury £28,908.79, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-12-11: treasury £28,904.15, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C6 on 2017-01-23 period 19, net margin £-0.17

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £-1,149.46
  - By billing account: C1 £-534.90, C2 £-1,151.78, C3 £-594.88, C4 £14.57, C5 £-2,021.63, C6 £-2,833.57, C7 £-1,098.91, C8 £-1,056.63, C9 £-1,067.38
- Bill shock events (>=20%): 25 -- C5 2017-01-31 (46%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (56%); C7 2017-01-31 (48%); C7 2017-02-28 (28%); C7 2017-05-31 (31%); C7 2017-06-30 (32%); C7 2017-09-30 (26%); C7 2017-10-31 (21%); C7 2017-11-30 (75%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (36%); C8 2017-09-30 (45%); C8 2017-10-31 (22%); C8 2017-11-30 (83%); C8 2017-12-31 (22%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-10-31 (23%)
- Churn risk (accounts renewing in 2017): 6 at risk (≥20% churn prob): C1 20%, C5 32%, C6 35%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £76.24-£77.07/MWh, net margin £-46.69 -- **net-negative**
- C1g (gas): tariff £17.24-£24.47/MWh, net margin £30.64
- C2 (electricity): tariff £41.19-£76.68/MWh, net margin £20.61
- C2g (gas): tariff £15.29-£16.36/MWh, net margin £-38.09 -- **net-negative**
- C3 (electricity): tariff £41.81-£56.34/MWh, net margin £-37.98 -- **net-negative**
- C3g (gas): tariff £13.52-£16.29/MWh, net margin £24.69
- C4 (electricity): tariff £45.42-£64.21/MWh, net margin £-20.45 -- **net-negative**
- C4g (gas): tariff £16.78-£20.95/MWh, net margin £89.63
- C5 (electricity): tariff £75.30-£78.36/MWh, net margin £-215.26 -- **net-negative**
- C6 (electricity): tariff £41.19-£74.28/MWh, net margin £-70.19 -- **net-negative**
- C7 (electricity): tariff £58.22-£111.14/MWh, net margin £-176.77 -- **net-negative**
- C8 (electricity): tariff £32.37-£108.81/MWh, net margin £13.54
- C9 (electricity): tariff £32.85-£79.13/MWh, net margin £-83.14 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -34.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.894, average bill shock 11.7%, bad debt provision £325.74, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £598.20 vs. naked (unhedged) net margin: £113.02
- hedging added £485.17 vs. a fully unhedged book (commodity-only: actual net £598.20 vs. naked net £113.02)
  - C1: actual £41.35 vs. naked £35.60 -- hedging added £5.75
  - C1g: actual £48.00 vs. naked £18.71 -- hedging added £29.29
  - C2: actual £61.98 vs. naked £165.38 -- hedging cost £103.40
  - C2g: actual £-49.94 vs. naked £-27.57 -- hedging cost £22.37
  - C3: actual £-43.37 vs. naked £-20.15 -- hedging cost £23.21
  - C3g: actual £25.54 vs. naked £-41.61 -- hedging added £67.15
  - C4: actual £62.07 vs. naked £24.64 -- hedging added £37.43
  - C4g: actual £85.00 vs. naked £-9.92 -- hedging added £94.92
  - C5: actual £166.43 vs. naked £43.00 -- hedging added £123.43
  - C6: actual £59.44 vs. naked £-182.57 -- hedging added £242.01
  - C7: actual £142.92 vs. naked £105.87 -- hedging added £37.06
  - C8: actual £114.58 vs. naked £140.70 -- hedging cost £26.12
  - C9: actual £-115.81 vs. naked £-139.06 -- hedging added £23.24

**Year narrative:** 2017 produced a net loss of £-509.48 across 13 accounts. The risk committee intervened 42 time(s), raising hedge fractions in response to elevated VaR. 25 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £-73.78 (gross £27.59, capital £101.37)
  - Electricity: gross £-126.27, capital £94.21, net £-220.48
  - Gas: gross £153.86, capital £7.16, net £146.70
- Treasury at year end: £28,948.58
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.95 (avg 0.95), C1g 1.00 (avg 1.00), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.95 (avg 0.95), C4g 1.00 (avg 1.00), C5 0.95 (avg 0.95), C6 1.00 (avg 1.00), C7 0.95 (avg 0.95), C8 0.85 (avg 0.85), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C7 on 2018-03-01 period 43, net margin £-0.28

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2018): £-692.35
  - By billing account: C1 £-197.85, C2 £-1,011.85, C3 £-317.31, C4 £216.43, C5 £-832.27, C6 £-2,355.08, C7 £-462.24, C8 £-739.29, C9 £-531.69
- Bill shock events (>=20%): 33 -- C5 2018-04-30 (32%); C5 2018-06-30 (21%); C5 2018-10-31 (31%); C5 2018-11-30 (27%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (29%); C7 2018-10-31 (46%); C7 2018-11-30 (32%); C2g 2018-04-30 (27%); C6 2018-04-30 (31%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (29%); C6 2018-11-30 (21%); C8 2018-04-30 (36%); C8 2018-05-31 (38%); C8 2018-06-30 (42%); C8 2018-08-31 (24%); C8 2018-09-30 (52%); C8 2018-10-31 (54%); C8 2018-11-30 (29%); C3 2018-07-31 (21%); C3g 2018-07-31 (24%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-08-31 (41%); C9 2018-09-30 (44%); C9 2018-10-31 (40%); C9 2018-12-31 (20%); C4g 2018-10-31 (30%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C3 23%, C5 41%, C6 32%, C7 41%, C8 38%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £76.24-£80.51/MWh, net margin £41.43
- C1g (gas): tariff £24.47-£31.47/MWh, net margin £48.19
- C2 (electricity): tariff £65.27-£76.68/MWh, net margin £-173.33 -- **net-negative**
- C2g (gas): tariff £16.36-£26.58/MWh, net margin £-8.85 -- **net-negative**
- C3 (electricity): tariff £56.34-£80.38/MWh, net margin £11.73
- C3g (gas): tariff £16.29-£22.96/MWh, net margin £24.24
- C4 (electricity): tariff £64.21-£79.92/MWh, net margin £56.84
- C4g (gas): tariff £20.95-£29.90/MWh, net margin £83.12
- C5 (electricity): tariff £75.30-£77.40/MWh, net margin £167.76
- C6 (electricity): tariff £71.00-£74.28/MWh, net margin £-427.29 -- **net-negative**
- C7 (electricity): tariff £58.74-£118.54/MWh, net margin £144.70
- C8 (electricity): tariff £57.00-£114.86/MWh, net margin £-88.78 -- **net-negative**
- C9 (electricity): tariff £41.45-£118.84/MWh, net margin £46.45

**Portfolio Health**

- Capital cost ratio: 367.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.896, average bill shock 11.2%, bad debt provision £357.05, avg complaint probability 3.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-377.38 vs. naked (unhedged) net margin: £1,719.13
- hedging cost £2,096.51 vs. a fully unhedged book (commodity-only: actual net £-377.38 vs. naked net £1,719.13)
  - C1: actual £25.24 vs. naked £111.96 -- hedging cost £86.72
  - C1g: actual £89.56 vs. naked £209.40 -- hedging cost £119.84
  - C2: actual £-255.13 vs. naked £26.92 -- hedging cost £282.05
  - C2g: actual £10.23 vs. naked £64.76 -- hedging cost £54.54
  - C3: actual £73.81 vs. naked £91.69 -- hedging cost £17.87
  - C3g: actual £24.29 vs. naked £44.52 -- hedging cost £20.23
  - C4: actual £52.80 vs. naked £195.59 -- hedging cost £142.79
  - C4g: actual £80.17 vs. naked £288.76 -- hedging cost £208.58
  - C5: actual £59.87 vs. naked £374.52 -- hedging cost £314.64
  - C6: actual £-680.21 vs. naked £-408.45 -- hedging cost £271.76
  - C7: actual £96.51 vs. naked £363.68 -- hedging cost £267.17
  - C8: actual £-214.62 vs. naked £99.12 -- hedging cost £313.74
  - C9: actual £260.08 vs. naked £256.67 -- hedging added £3.42

**Year narrative:** 2018 produced a net loss of £-73.78 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £290.52 (gross £355.94, capital £65.42)
  - Electricity: gross £144.93, capital £59.79, net £85.14
  - Gas: gross £211.01, capital £5.63, net £205.38
- Treasury at year end: £28,771.04
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.90 (avg 0.90), C4 0.85 (avg 0.85), C4g 0.90 (avg 0.90), C5 0.85 (avg 0.85), C6 0.90 (avg 0.90), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C8 on 2019-02-02 period 36, net margin £-0.19

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2019): £-553.86
  - By billing account: C1 £-73.84, C2 £-840.47, C3 £-200.90, C4 £222.30, C5 £-748.79, C6 £-2,127.00, C7 £-306.84, C8 £-675.78, C9 £-233.41
- Bill shock events (>=20%): 33 -- C1 2019-04-30 (21%); C5 2019-01-31 (21%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (31%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (69%); C7 2019-11-30 (44%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (26%); C8 2019-02-28 (27%); C8 2019-04-30 (27%); C8 2019-06-30 (38%); C8 2019-07-31 (34%); C8 2019-09-30 (57%); C8 2019-10-31 (84%); C8 2019-11-30 (37%); C3 2019-04-30 (20%); C9 2019-02-28 (26%); C9 2019-04-30 (23%); C9 2019-06-30 (36%); C9 2019-07-31 (44%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (37%); C4g 2019-10-31 (36%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C3 23%, C5 38%, C6 32%, C7 38%, C8 38%, C9 35%

**Pricing & Margin**

- C1 (electricity): tariff £53.29-£80.51/MWh, net margin £25.08
- C1g (gas): tariff £15.31-£31.47/MWh, net margin £89.27
- C2 (electricity): tariff £65.27-£71.92/MWh, net margin £-55.29 -- **net-negative**
- C2g (gas): tariff £21.08-£26.58/MWh, net margin £12.03
- C3 (electricity): tariff £49.11-£80.38/MWh, net margin £28.32
- C3g (gas): tariff £15.74-£22.96/MWh, net margin £26.84
- C4 (electricity): tariff £50.93-£79.92/MWh, net margin £46.13
- C4g (gas): tariff £13.27-£29.90/MWh, net margin £77.24
- C5 (electricity): tariff £53.87-£77.40/MWh, net margin £58.97
- C6 (electricity): tariff £71.00-£72.41/MWh, net margin £-239.12 -- **net-negative**
- C7 (electricity): tariff £41.78-£118.54/MWh, net margin £95.79
- C8 (electricity): tariff £56.36-£114.86/MWh, net margin £-16.32 -- **net-negative**
- C9 (electricity): tariff £39.46-£118.84/MWh, net margin £141.58

**Portfolio Health**

- Capital cost ratio: 18.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.893, average bill shock 12.5%, bad debt provision £362.00, avg complaint probability 3.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £295.01 vs. naked (unhedged) net margin: £1,883.20
- hedging cost £1,588.19 vs. a fully unhedged book (commodity-only: actual net £295.01 vs. naked net £1,883.20)
  - C1: actual £3.58 vs. naked £37.37 -- hedging cost £33.79
  - C1g: actual £25.99 vs. naked £67.90 -- hedging cost £41.92
  - C2: actual £19.05 vs. naked £232.12 -- hedging cost £213.07
  - C2g: actual £10.97 vs. naked £140.68 -- hedging cost £129.71
  - C3: actual £-20.05 vs. naked £46.09 -- hedging cost £66.14
  - C3g: actual £31.70 vs. naked £89.28 -- hedging cost £57.58
  - C4: actual £29.38 vs. naked £107.27 -- hedging cost £77.89
  - C4g: actual £75.51 vs. naked £102.77 -- hedging cost £27.25
  - C5: actual £14.93 vs. naked £105.04 -- hedging cost £90.11
  - C6: actual £-4.21 vs. naked £316.82 -- hedging cost £321.03
  - C7: actual £24.99 vs. naked £124.71 -- hedging cost £99.72
  - C8: actual £100.85 vs. naked £362.64 -- hedging cost £261.79
  - C9: actual £-17.67 vs. naked £150.52 -- hedging cost £168.20

**Year narrative:** 2019 produced a net gain of £290.52 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-50.74 (gross £67.26, capital £118.00)
  - Electricity: gross £-66.28, capital £110.64, net £-176.93
  - Gas: gross £133.54, capital £7.35, net £126.19
- Treasury at year end: £28,990.88
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2020-03-04 period 37, net margin £-0.98

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C3
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £-496.73
  - By billing account: C1 £-93.42, C2 £-646.69, C3 £-179.41, C4 £179.71, C5 £-697.11, C6 £-1,966.38, C7 £-283.46, C8 £-513.18, C9 £-270.68
- Bill shock events (>=20%): 28 -- C1g 2020-01-31 (32%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (26%); C7 2020-01-31 (20%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (26%); C7 2020-10-31 (58%); C7 2020-11-30 (22%); C7 2020-12-31 (35%); C2 2020-04-30 (33%); C2g 2020-04-30 (21%); C6 2020-04-30 (44%); C6 2020-10-31 (32%); C6 2020-12-31 (25%); C8 2020-04-30 (49%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (49%); C8 2020-10-31 (63%); C8 2020-12-31 (41%); C9 2020-04-30 (28%); C9 2020-05-31 (24%); C9 2020-06-30 (35%); C9 2020-09-30 (41%); C9 2020-10-31 (48%); C9 2020-12-31 (35%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 23%, C4 20%, C5 32%, C6 38%, C7 32%, C8 38%, C9 41%

**Pricing & Margin**

- C1 (electricity): tariff £53.29-£70.56/MWh, net margin £3.25
- C1g (gas): tariff £15.31-£18.14/MWh, net margin £25.98
- C2 (electricity): tariff £40.62-£71.92/MWh, net margin £-56.12 -- **net-negative**
- C2g (gas): tariff £13.87-£21.08/MWh, net margin £38.56
- C3 (electricity): tariff £49.11/MWh, net margin £-8.58 -- **net-negative**
- C3g (gas): tariff £15.74/MWh, net margin £16.91
- C4 (electricity): tariff £50.93-£56.47/MWh, net margin £30.62
- C4g (gas): tariff £8.78-£13.27/MWh, net margin £44.75
- C5 (electricity): tariff £53.87-£68.75/MWh, net margin £11.85
- C6 (electricity): tariff £42.61-£72.41/MWh, net margin £-169.57 -- **net-negative**
- C7 (electricity): tariff £41.78-£103.25/MWh, net margin £24.70
- C8 (electricity): tariff £34.92-£107.60/MWh, net margin £-0.70 -- **net-negative**
- C9 (electricity): tariff £28.64-£75.33/MWh, net margin £-12.37 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 175.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 144, average clarity 0.890, average bill shock 11.5%, bad debt provision £267.26, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-930.54 vs. naked (unhedged) net margin: £-4,528.18
- hedging added £3,597.64 vs. a fully unhedged book (commodity-only: actual net £-930.54 vs. naked net £-4,528.18)
  - C1: actual £-32.10 vs. naked £-237.39 -- hedging added £205.29
  - C1g: actual £-23.73 vs. naked £-305.02 -- hedging added £281.29
  - C2: actual £-93.08 vs. naked £-43.52 -- hedging cost £49.56
  - C2g: actual £41.41 vs. naked £32.71 -- hedging added £8.69
  - C4: actual £-2.04 vs. naked £-173.90 -- hedging added £171.86
  - C4g: actual £-88.71 vs. naked £-371.15 -- hedging added £282.44
  - C5: actual £-219.13 vs. naked £-1,385.11 -- hedging added £1,165.98
  - C6: actual £-284.41 vs. naked £-571.64 -- hedging added £287.23
  - C7: actual £-107.05 vs. naked £-810.07 -- hedging added £703.03
  - C8: actual £-93.32 vs. naked £-213.39 -- hedging added £120.08
  - C9: actual £-28.40 vs. naked £-449.71 -- hedging added £421.31

**Year narrative:** 2020 produced a net loss of £-50.74 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 28 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-1,402.77 (gross £-1,206.82, capital £195.95)
  - Electricity: gross £-1,106.22, capital £187.87, net £-1,294.08
  - Gas: gross £-100.61, capital £8.08, net £-108.69
- Treasury at year end: £27,972.69
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C4 0.95 (avg 0.95), C4g 0.95 (avg 0.95), C6 0.95 (avg 0.95), C7 0.95 (avg 0.95), C8 0.95 (avg 0.95), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 4
  - 2021-09-30: treasury £26,951.33, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-10-30: treasury £26,956.81, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-11-29: treasury £26,964.10, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-12-29: treasury £26,969.75, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.52
- Worst single period: C5 on 2021-01-08 period 39, net margin £-2.13

**Customer Book**

- Active accounts: 11 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2021): £-589.27
  - By billing account: C1 £-169.28, C2 £-691.48, C3 £-176.70, C4 £-21.69, C5 £-823.12, C6 £-2,051.14, C7 £-353.65, C8 £-645.65, C9 £-370.74
- Bill shock events (>=20%): 32 -- C5 2021-01-31 (22%); C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (29%); C5 2021-11-30 (49%); C7 2021-01-31 (25%); C7 2021-05-31 (30%); C7 2021-06-30 (46%); C7 2021-10-31 (53%); C7 2021-11-30 (63%); C2 2021-04-30 (26%); C2g 2021-04-30 (30%); C6 2021-04-30 (42%); C6 2021-06-30 (35%); C6 2021-10-31 (26%); C6 2021-11-30 (49%); C8 2021-04-30 (38%); C8 2021-05-31 (28%); C8 2021-06-30 (61%); C8 2021-09-30 (23%); C8 2021-10-31 (67%); C8 2021-11-30 (81%); C9 2021-02-28 (22%); C9 2021-05-31 (23%); C9 2021-06-30 (49%); C9 2021-08-31 (21%); C9 2021-09-30 (21%); C9 2021-10-31 (61%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-10-31 (163%); C4g 2021-10-31 (200%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C1 20%, C2 20%, C5 35%, C6 38%, C7 35%, C8 41%, C9 35%

**Pricing & Margin**

- C1 (electricity): tariff £70.56/MWh, net margin £-31.62 -- **net-negative**
- C1g (gas): tariff £18.14/MWh, net margin £-23.68 -- **net-negative**
- C2 (electricity): tariff £40.62-£92.82/MWh, net margin £-180.73 -- **net-negative**
- C2g (gas): tariff £13.87-£24.47/MWh, net margin £14.83
- C4 (electricity): tariff £56.47-£263.33/MWh, net margin £9.95
- C4g (gas): tariff £8.78-£57.19/MWh, net margin £-99.84 -- **net-negative**
- C5 (electricity): tariff £68.75/MWh, net margin £-214.74 -- **net-negative**
- C6 (electricity): tariff £42.61-£96.34/MWh, net margin £-453.24 -- **net-negative**
- C7 (electricity): tariff £54.08-£415.22/MWh, net margin £-108.43 -- **net-negative**
- C8 (electricity): tariff £34.92-£135.63/MWh, net margin £-213.80 -- **net-negative**
- C9 (electricity): tariff £28.64-£136.89/MWh, net margin £-101.48 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -16.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 132, average clarity 0.875, average bill shock 15.9%, bad debt provision £288.78, avg complaint probability 4.0%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,215.40 vs. naked (unhedged) net margin: £-7,790.86
- hedging added £6,575.46 vs. a fully unhedged book (commodity-only: actual net £-1,215.40 vs. naked net £-7,790.86)
  - C2: actual £-222.71 vs. naked £-490.51 -- hedging added £267.80
  - C2g: actual £4.74 vs. naked £-552.07 -- hedging added £556.81
  - C4: actual £69.62 vs. naked £72.25 -- hedging cost £2.63
  - C4g: actual £-115.52 vs. naked £-1,114.67 -- hedging added £999.15
  - C6: actual £-517.82 vs. naked £-2,885.57 -- hedging added £2,367.75
  - C7: actual £1.96 vs. naked £-23.02 -- hedging added £24.98
  - C8: actual £-265.50 vs. naked £-1,345.72 -- hedging added £1,080.21
  - C9: actual £-170.16 vs. naked £-1,451.55 -- hedging added £1,281.39

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-1,402.77 across 11 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 32 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £-1,500.70 (gross £-1,390.65, capital £110.05)
  - Electricity: gross £-1,200.38, capital £105.40, net £-1,305.78
  - Gas: gross £-190.26, capital £4.65, net £-194.92
- Treasury at year end: £26,359.23
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 1.00 (avg 1.00), C4g 1.00 (avg 1.00), C6 1.00 (avg 1.00), C7 1.00 (avg 1.00), C8 1.00 (avg 1.00), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 30
  - 2022-01-28: treasury £26,976.88, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-02-27: treasury £26,984.64, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-03-29: treasury £26,990.35, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-04-28: treasury £26,996.32, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-05-28: treasury £27,003.83, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-06-27: treasury £27,010.19, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-07-27: treasury £27,014.85, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-08-26: treasury £27,016.82, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-09-25: treasury £27,020.11, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-01-16: treasury £26,914.91, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-02-15: treasury £26,938.57, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-03-17: treasury £26,950.75, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-16: treasury £26,953.44, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-05-16: treasury £26,951.67, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-06-15: treasury £26,941.95, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-07-15: treasury £26,926.10, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-08-14: treasury £26,907.51, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-09-13: treasury £26,887.62, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-10-13: treasury £26,880.80, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-11-12: treasury £26,879.67, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-12: treasury £26,890.09, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-12: treasury £26,860.43, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-05-12: treasury £26,805.15, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-06-11: treasury £26,768.18, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-07-11: treasury £26,740.05, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-08-10: treasury £26,713.12, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-09-09: treasury £26,682.97, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-10-09: treasury £26,630.30, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-11-08: treasury £26,580.09, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-08: treasury £26,479.35, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.58
- Worst single period: C4g on 2022-09-30 period 1, net margin £-1.08

**Customer Book**

- Active accounts: 9 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2022): £-584.74
  - By billing account: C1 £-172.26, C2 £-655.04, C2_2 £-416.89, C3 £-197.96, C4 £-395.87, C5 £-736.50, C6 £-2,001.55, C7 £-335.58, C8 £-613.00, C9 £-322.78
- Bill shock events (>=20%): 36 -- C7 2022-01-31 (199%); C7 2022-02-28 (27%); C7 2022-04-30 (23%); C7 2022-05-31 (37%); C7 2022-06-30 (28%); C7 2022-09-30 (35%); C7 2022-11-30 (66%); C7 2022-12-31 (54%); C6 2022-04-30 (96%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-04-30 (84%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (85%); C8 2022-11-30 (73%); C8 2022-12-31 (58%); C9 2022-04-30 (21%); C9 2022-05-31 (29%); C9 2022-06-30 (28%); C9 2022-07-31 (41%); C9 2022-09-30 (50%); C9 2022-10-31 (31%); C9 2022-11-30 (45%); C9 2022-12-31 (53%); C4g 2022-10-31 (159%); C2_2 2022-04-30 (1718%); C2_2 2022-05-31 (39%); C2_2 2022-06-30 (33%); C2_2 2022-09-30 (76%); C2_2 2022-11-30 (65%); C2_2 2022-12-31 (57%)
- Churn risk (accounts renewing in 2022): 6 at risk (≥20% churn prob): C2 20%, C4 23%, C6 35%, C7 38%, C8 35%, C9 38%

**Pricing & Margin**

- C2 (electricity): tariff £92.82/MWh, net margin £-72.61 -- **net-negative**
- C2_2 (electricity): tariff £245.84/MWh, net margin £-548.16 -- **net-negative**
- C2g (gas): tariff £24.47/MWh, net margin £-3.71 -- **net-negative**
- C4 (electricity): tariff £263.33-£298.24/MWh, net margin £-154.68 -- **net-negative**
- C4g (gas): tariff £57.19-£174.50/MWh, net margin £-191.20 -- **net-negative**
- C6 (electricity): tariff £96.34-£323.41/MWh, net margin £-467.72 -- **net-negative**
- C7 (electricity): tariff £190.15-£415.22/MWh, net margin £-2.31 -- **net-negative**
- C8 (electricity): tariff £71.05-£473.41/MWh, net margin £-124.94 -- **net-negative**
- C9 (electricity): tariff £71.70-£341.98/MWh, net margin £64.63

**Portfolio Health**

- Capital cost ratio: -7.9% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £27,972.68 -> £24,832.49 (11.2%)
- Bills issued: 88, average clarity 0.806, average bill shock 44.8%, bad debt provision £462.37, avg complaint probability 5.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-3,010.62 vs. naked (unhedged) net margin: £5,157.00
- hedging cost £8,167.63 vs. a fully unhedged book (commodity-only: actual net £-3,010.62 vs. naked net £5,157.00)
  - C2_2: actual £-841.78 vs. naked £215.80 -- hedging cost £1,057.59
  - C4: actual £-757.79 vs. naked £992.44 -- hedging cost £1,750.23
  - C4g: actual £-393.67 vs. naked £2,471.28 -- hedging cost £2,864.96
  - C6: actual £-437.50 vs. naked £-805.87 -- hedging added £368.37
  - C7: actual £-941.84 vs. naked £1,152.50 -- hedging cost £2,094.34
  - C8: actual £-8.60 vs. naked £823.54 -- hedging cost £832.14
  - C9: actual £370.56 vs. naked £307.31 -- hedging added £63.24

**Year narrative:** 2022 (flagged crisis year) produced a net loss of £-1,500.70 across 9 accounts. The risk committee intervened 30 time(s), raising hedge fractions in response to elevated VaR. 36 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £-966.02 (gross £-874.89, capital £91.13)
  - Electricity: gross £-615.70, capital £85.32, net £-701.02
  - Gas: gross £-259.19, capital £5.81, net £-265.00
- Treasury at year end: £24,368.10
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.90 (avg 0.90), C6 1.00 (avg 1.00), C7 0.90 (avg 0.90), C8 0.90 (avg 0.90), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 15
  - 2023-01-07: treasury £26,342.15, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-02-06: treasury £26,231.33, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-03-08: treasury £26,127.01, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-09-07: treasury £24,201.07, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-07: treasury £24,145.29, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-06: treasury £24,066.02, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-12-06: treasury £23,962.88, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-06: treasury £23,911.06, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-05-06: treasury £23,980.62, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-06-05: treasury £24,021.08, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-07-05: treasury £24,043.84, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-04: treasury £24,066.20, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-09-03: treasury £24,090.43, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-03: treasury £24,118.65, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-02: treasury £24,173.45, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.24
- Worst single period: C4g on 2023-01-01 period 1, net margin £-1.08

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2023): £-620.60
  - By billing account: C1 £-145.67, C2 £-700.94, C2_2 £-321.70, C3 £-156.94, C4 £-894.78, C5 £-775.00, C6 £-1,735.90, C7 £-871.96, C8 £-451.83, C9 £-151.29
- Bill shock events (>=20%): 29 -- C7 2023-05-31 (32%); C7 2023-06-30 (37%); C7 2023-10-31 (57%); C7 2023-11-30 (73%); C6 2023-04-30 (43%); C6 2023-05-31 (23%); C6 2023-06-30 (23%); C6 2023-10-31 (38%); C6 2023-11-30 (44%); C8 2023-04-30 (44%); C8 2023-05-31 (41%); C8 2023-06-30 (44%); C8 2023-10-31 (100%); C8 2023-11-30 (70%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-07-31 (25%); C9 2023-09-30 (22%); C9 2023-10-31 (74%); C9 2023-11-30 (53%); C4 2023-10-31 (49%); C4g 2023-10-31 (71%); C2_2 2023-05-31 (41%); C2_2 2023-06-30 (42%); C2_2 2023-10-31 (96%); C2_2 2023-11-30 (66%)
- Churn risk (accounts renewing in 2023): 5 at risk (≥20% churn prob): C2_2 35%, C6 26%, C7 38%, C8 38%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £245.84-£260.22/MWh, net margin £177.71
- C4 (electricity): tariff £104.41-£298.24/MWh, net margin £-557.07 -- **net-negative**
- C4g (gas): tariff £38.39-£174.50/MWh, net margin £-265.00 -- **net-negative**
- C6 (electricity): tariff £214.34-£323.41/MWh, net margin £81.97
- C7 (electricity): tariff £106.76-£363.01/MWh, net margin £-939.82 -- **net-negative**
- C8 (electricity): tariff £165.35-£473.41/MWh, net margin £267.02
- C9 (electricity): tariff £96.46-£341.98/MWh, net margin £269.17

**Portfolio Health**

- Capital cost ratio: -10.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 84, average clarity 0.813, average bill shock 20.1%, bad debt provision £511.15, avg complaint probability 5.2%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £2,024.86 vs. naked (unhedged) net margin: £3,255.38
- hedging cost £1,230.52 vs. a fully unhedged book (commodity-only: actual net £2,024.86 vs. naked net £3,255.38)
  - C2_2: actual £781.37 vs. naked £1,545.57 -- hedging cost £764.20
  - C4: actual £-5.51 vs. naked £101.46 -- hedging cost £106.98
  - C4g: actual £127.23 vs. naked £26.31 -- hedging added £100.92
  - C6: actual £342.47 vs. naked £29.50 -- hedging added £312.97
  - C7: actual £183.50 vs. naked £329.50 -- hedging cost £146.00
  - C8: actual £452.78 vs. naked £982.15 -- hedging cost £529.36
  - C9: actual £143.02 vs. naked £240.89 -- hedging cost £97.86

**Year narrative:** 2023 produced a net loss of £-966.02 across 7 accounts. The risk committee intervened 15 time(s), raising hedge fractions in response to elevated VaR. 29 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £928.28 (gross £1,079.71, capital £151.43)
  - Electricity: gross £967.79, capital £138.36, net £829.42
  - Gas: gross £111.93, capital £13.07, net £98.86
- Treasury at year end: £25,899.72
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C2_2 on 2024-12-12 period 34, net margin £-0.15

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2024): £-493.33
  - By billing account: C1 £-121.44, C2 £-652.92, C2_2 £-149.19, C3 £-163.09, C4 £-701.32, C5 £-700.84, C6 £-1,380.97, C7 £-616.96, C8 £-280.21, C9 £-166.39
- Bill shock events (>=20%): 25 -- C7 2024-01-31 (20%); C7 2024-02-29 (27%); C7 2024-05-31 (38%); C7 2024-09-30 (35%); C7 2024-10-31 (38%); C7 2024-11-30 (49%); C8 2024-02-29 (23%); C8 2024-04-30 (54%); C8 2024-05-31 (49%); C8 2024-07-31 (27%); C8 2024-09-30 (74%); C8 2024-10-31 (36%); C8 2024-11-30 (62%); C9 2024-05-31 (49%); C9 2024-07-31 (41%); C9 2024-09-30 (54%); C9 2024-10-31 (23%); C9 2024-11-30 (47%); C2_2 2024-02-29 (23%); C2_2 2024-04-30 (61%); C2_2 2024-05-31 (48%); C2_2 2024-07-31 (26%); C2_2 2024-09-30 (66%); C2_2 2024-10-31 (35%); C2_2 2024-11-30 (58%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 38%, C4 23%, C6 38%, C7 41%, C8 41%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £93.74-£260.22/MWh, net margin £288.13
- C4 (electricity): tariff £104.41/MWh, net margin £-1.31 -- **net-negative**
- C4g (gas): tariff £38.39/MWh, net margin £98.86
- C6 (electricity): tariff £214.34/MWh, net margin £114.29
- C7 (electricity): tariff £100.46-£203.81/MWh, net margin £184.85
- C8 (electricity): tariff £75.81-£315.67/MWh, net margin £234.10
- C9 (electricity): tariff £60.05-£184.15/MWh, net margin £9.36

**Portfolio Health**

- Capital cost ratio: 14.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 69, average clarity 0.806, average bill shock 20.0%, bad debt provision £255.92, avg complaint probability 5.2%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-121.91 vs. naked (unhedged) net margin: £-1,012.66
- hedging added £890.75 vs. a fully unhedged book (commodity-only: actual net £-121.91 vs. naked net £-1,012.66)
  - C2_2: actual £-56.07 vs. naked £-180.42 -- hedging added £124.35
  - C7: actual £52.45 vs. naked £-50.72 -- hedging added £103.17
  - C8: actual £49.38 vs. naked £-264.04 -- hedging added £313.42
  - C9: actual £-167.67 vs. naked £-517.49 -- hedging added £349.82

**Year narrative:** 2024 produced a net gain of £928.28 across 7 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 25 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £-241.81 (gross £-171.34, capital £70.47)
  - Electricity: gross £-171.34, capital £70.47, net £-241.81
- Treasury at year end: £25,747.27
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C8 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C2_2 on 2025-01-08 period 36, net margin £-1.52

**Customer Book**

- Active accounts: 4 (C2_2, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 0, gas (dual-fuel): 0
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £-490.62
  - By billing account: C1 £-121.31, C2 £-636.85, C2_2 £-197.36, C3 £-154.88, C4 £-685.04, C5 £-691.63, C6 £-1,353.85, C7 £-610.91, C8 £-275.48, C9 £-178.88
- Bill shock events (>=20%): 18 -- C7 2025-01-31 (22%); C7 2025-04-30 (37%); C7 2025-05-31 (23%); C7 2025-06-07 (80%); C8 2025-01-31 (39%); C8 2025-02-28 (24%); C8 2025-04-30 (20%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (33%); C9 2025-06-07 (72%); C2_2 2025-01-31 (38%); C2_2 2025-02-28 (24%); C2_2 2025-04-30 (22%); C2_2 2025-05-31 (36%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £93.74-£133.85/MWh, net margin £-133.95 -- **net-negative**
- C7 (electricity): tariff £100.46-£191.79/MWh, net margin £55.20
- C8 (electricity): tariff £75.81-£211.06/MWh, net margin £-73.33 -- **net-negative**
- C9 (electricity): tariff £60.05-£114.63/MWh, net margin £-89.74 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -41.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 24, average clarity 0.727, average bill shock 32.1%, bad debt provision £87.14, avg complaint probability 7.3%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-189.95 vs. naked (unhedged) net margin: £-88.36
- hedging cost £101.60 vs. a fully unhedged book (commodity-only: actual net £-189.95 vs. naked net £-88.36)
  - C2_2: actual £-99.79 vs. naked £10.40 -- hedging cost £110.19
  - C8: actual £-90.16 vs. naked £-98.75 -- hedging added £8.59

**Year narrative:** 2025 produced a net loss of £-241.81 across 4 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 18 customer(s) experienced a bill shock of >=20%.
