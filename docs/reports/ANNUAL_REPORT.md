# Annual Report — The Synthetic Enterprise

## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £29,846.19
- Final treasury: £26,050.85
  (£-3,795.34 net change)
- Customer bills (all-in): £182,148.04
  VAT remitted to HMRC: (£15,112.55) | Revenue (ex-VAT): £167,035.49
  Non-commodity pass-through: (£42,887.46)
- Gross margin: £29,002.78
- Capital costs: £2,348.14
- Net margin: £26,654.64
- Capital cost ratio: 8.1% of gross
- Net margin as % of revenue: 16.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 214
- Bills issued: 1117, average clarity 0.869,
  service quality score 0.919
- Enterprise value (CLV sum across 10 billing accounts): £9,888.92
- Cost to serve (whole portfolio): £6,680.28, net margin after cost to serve: £19,974.36
- Hedge effectiveness (whole window): hedging cost £21,886.98 vs. a fully unhedged book (commodity-only: actual net £-3,795.34 vs. naked net £18,091.64)

- **2021** (crisis year): net margin £-1,535.81, 28 risk committee wake-up(s).
- **2022** (crisis year): net margin £-1,506.24, 43 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £29,002.78, capital £2,348.14, net £26,654.64. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 12.6% (commodity basis, comparable to old model) / 8.1% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £-1,535.81 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 16.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £26,654.64
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £18,091.64
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £21,886.98 vs. a fully unhedged book (commodity-only: actual net £-3,795.34 vs. naked net £18,091.64)
- **Best hedging decision of the run**: C6, term starting
  2021-03-31 (hedge fraction 0.85) -- hedging
  protected £1,663.57 vs. going naked.
- **Worst hedging decision of the run**: C4g, term
  starting 2022-09-30 (hedge fraction 1.00) --
  over-hedging cost £2,864.96 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|
| 2016 | £-419.73 | £-333.14 | £80.49 | £-672.38 |
| 2017 | £-275.37 | £-360.55 | £138.51 | £-497.41 |
| 2018 | £-214.31 | £60.97 | £179.58 | £26.24 |
| 2019 | £-66.66 | £385.36 | £248.49 | £567.19 |
| 2020 | £-88.96 | £95.64 | £147.92 | £154.60 |
| 2021 | £-800.04 | £-654.22 | £-81.54 | £-1,535.81 |
| 2022 | £-549.98 | £-788.62 | £-167.64 | £-1,506.24 |
| 2023 | £15.63 | £-930.92 | £-259.78 | £-1,175.08 |
| 2024 | £142.03 | £772.26 | £119.01 | £1,033.29 |
| 2025 | £0.00 | £-189.74 | £0.00 | £-189.74 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **43** renewals.  Lost (churned): **6** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.8255 |
| C1 | 2018-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.4100 | 0.3500 | 0.7335 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6312 |
| C1 | 2019-12-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1400 | 0.5500 | 0.9370 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2600 | 0.5500 | 0.8830 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4829 |
| C2 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.1700 | 0.5500 | 0.9235 | 0.9691 |
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
| C8 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C2_2 | 2024-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.2300 | 0.5500 | 0.8965 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4099 |
| C2_2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 134.3%
- **Average signed error:** +37.4% (over-estimates vs SIM)
- **Renewal events with estimates:** 49

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +87.9% | 91.8% |
| 2017 | 3 | -54.8% | 54.8% |
| 2018 | 3 | -68.5% | 68.5% |
| 2019 | 3 | -100.0% | 100.0% |
| 2020 | 9 | -74.0% | 74.0% |
| 2021 | 8 | +344.3% | 349.6% |
| 2022 | 6 | +121.3% | 167.1% |
| 2023 | 6 | -20.0% | 108.4% |
| 2024 | 6 | -62.9% | 73.8% |
| 2025 | 2 | -38.7% | 38.7% |

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
| 2016 | 17 | 21.9% | 35.6% |
| 2017 | 13 | 15.7% | 30.9% |
| 2018 | 13 | 16.3% | 40.4% |
| 2019 | 13 | 13.6% | 23.3% |
| 2020 | 12 | 19.7% | 32.0% |
| 2021 | 10 | 25.9% | 42.0% |
| 2022 | 8 | 27.8% | 32.8% |
| 2023 | 7 | 7.4% | 19.9% |
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
| 2016 | 3 | 0.92× | 2.63× |
| 2017 | 3 | 0.55× | 0.67× |
| 2018 | 3 | 0.69× | 0.78× |
| 2019 | 3 | 1.00× | 1.00× |
| 2020 | 9 | 0.74× | 1.00× |
| 2021 | 8 | 3.50× ⚠ | 18.00× |
| 2022 | 6 | 1.67× | 4.59× |
| 2023 | 6 | 1.08× | 2.65× |
| 2024 | 6 | 0.74× | 1.00× |
| 2025 | 2 | 0.39× | 0.40× |


## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **7** (6 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.14, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.17, company est=0.95 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.95 |
| 2022-03-31 | CHURN | C2 | SIM p=0.17, company est=0.95 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.50 |
| 2024-09-29 | CHURN | C4 | SIM p=0.23, company est=0.11 |

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

## Policy Costs — RO + CfD Levies (Phase 21a)

Electricity policy costs deducted from net_margin_gbp each year. 
CfD levy was NEGATIVE in 2022 (crisis rebate from LCCC) — this appears 
as a positive contribution to that year's margin.

| Year | RO levy £ | CfD levy £ | Total policy cost £ | Note |
|------|-----------|------------|---------------------|------|
| 2016 | 1,108 | 7 | 1,115 |  |
| 2017 | 1,689 | 125 | 1,814 |  |
| 2018 | 2,027 | 311 | 2,338 |  |
| 2019 | 2,254 | 390 | 2,644 |  |
| 2020 | 2,205 | 327 | 2,531 |  |
| 2021 | 2,286 | 140 | 2,426 |  |
| 2022 | 1,768 | -344 | 1,424 | ⬇ CfD REBATE |
| 2023 | 1,931 | 463 | 2,394 |  |
| 2024 | 1,707 | 626 | 2,333 |  |
| 2025 | 767 | 265 | 1,032 |  |
| **Total** | **17,742** | **2,310** | **20,052** | |

Total policy cost: £20,052 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,842 | 40,643 | 33.6% | £8,581.93 | £8,937.44 | £211.15/MWh | £111.44/MWh | +3.0% |
| C8 | 106,723 | 46,761 | 43.8% | £9,682.00 | £6,522.81 | £207.05/MWh | £108.78/MWh | +10.0% |
| C9 | 109,388 | 46,156 | 42.2% | £7,713.05 | £5,539.20 | £167.11/MWh | £87.60/MWh | +8.7% |

Total HH revenue: £46,976.43 vs flat equivalent £43,928.48 (+6.9% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 20 | 104% | C8 (2016-10-31) |
| 2017 | 25 | 84% | C8 (2017-11-30) |
| 2018 | 34 | 55% | C8 (2018-10-31) |
| 2019 | 33 | 86% | C8 (2019-10-31) |
| 2020 | 27 | 65% | C8 (2020-10-31) |
| 2021 | 30 | 203% | C4g (2021-10-31) |
| 2022 | 36 | 1717% | C2_2 (2022-04-30) |
| 2023 | 28 | 101% | C8 (2023-10-31) |
| 2024 | 24 | 77% | C8 (2024-09-30) |
| 2025 | 18 | 80% | C7 (2025-06-07) |

Total: **275** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1717% | no |
| 2021-10-31 | C4g | +203% | no |
| 2022-01-31 | C7 | +161% | no |
| 2022-10-31 | C4g | +154% | no |
| 2021-10-31 | C4 | +139% | yes |
| 2016-10-31 | C8 | +104% | no |
| 2023-10-31 | C8 | +101% | no |
| 2023-10-31 | C2_2 | +96% | no |
| 2019-10-31 | C8 | +86% | no |
| 2022-09-30 | C8 | +86% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 11% | 11% | 0 |
| 2017 | 4 | 20% | 31% | 2 ⚠ |
| 2018 | 4 | 32% | 42% | 4 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 3 | 5% | 14% | 0 |
| 2021 | 2 | 72% | 95% | 2 ⚠ |
| 2022 | 1 | 95% | 95% | 1 ⚠ |
| 2023 | 1 | 0% | 0% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-09-30 | C4g | £9.1 | £58.8 (+548%) | 95% |
| 2022-09-30 | C4g | £58.8 | £174.4 (+197%) | 95% |
| 2021-03-31 | C2g | £14.2 | £25.1 (+76%) | 49% |
| 2018-04-01 | C2g | £16.7 | £26.7 (+59%) | 42% |
| 2018-10-01 | C4g | £21.5 | £30.8 (+43%) | 32% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 22 |
| Retained | 18 (82%) |
| Churned despite offer | 4 |
| Total offer cost (foregone margin) | £5,112.04 |
| Margin saved (retained customers' terms) | £22,409.06 |
| Wasted offer cost (churned anyway) | £1088.92 |
| **Net ROI of retention strategy** | **£17,297.02** |
| Acquisition cost avoided (retained customers) | £4,450.00 |
| **Full economic ROI (margin + acq savings)** | **£21,747.02** |

Missed opportunities (churns with no offer): **2** (£403.31 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 2 (£403.31 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2016 | 1 | 1 | £70.52 | £884.57 | £814.05 | £0.00 |
| 2017 | 4 | 4 | £290.14 | £2869.46 | £2579.32 | £0.00 |
| 2018 | 2 | 2 | £170.66 | £2054.90 | £1884.24 | £0.00 |
| 2019 | 1 | 1 | £142.50 | £2178.72 | £2036.22 | £0.00 |
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £112.78 |
| 2021 | 8 | 6 | £1404.14 | £4841.03 | £3436.89 | £0.00 |
| 2022 | 4 | 3 | £1818.38 | £6639.06 | £4820.68 | £0.00 |
| 2023 | 1 | 1 | £908.43 | £2941.33 | £2032.89 | £0.00 |
| 2024 | 1 | 0 | £307.27 | £0.00 | £-307.27 | £290.54 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2016-12-31 | C5 | 0.31 | 3% | £70.52 | £884.57 | £400 | £814.05 | retained |
| 2017-04-01 | C2 | 0.64 | 5% | £18.10 | £172.31 | £150 | £154.20 | retained |
| 2017-04-01 | C6 | 0.61 | 5% | £225.48 | £2069.84 | £400 | £1844.36 | retained |
| 2017-04-01 | C8 | 0.41 | 3% | £32.28 | £434.70 | £150 | £402.42 | retained |
| 2017-10-01 | C4 | 0.31 | 3% | £14.27 | £192.61 | £150 | £178.34 | retained |
| 2018-04-01 | C6 | 0.31 | 3% | £130.83 | £1464.17 | £400 | £1333.34 | retained |
| 2018-07-01 | C9 | 0.35 | 3% | £39.83 | £590.73 | £150 | £550.90 | retained |
| 2019-04-01 | C6 | 0.35 | 3% | £142.50 | £2178.72 | £400 | £2036.22 | retained |
| 2021-03-31 | C2 | 0.41 | 3% | £12.13 | £166.20 | £150 | £154.07 | retained |
| 2021-03-31 | C6 | 0.45 | 3% | £164.27 | £2414.00 | £400 | £2249.73 | retained |
| 2021-03-31 | C8 | 0.32 | 3% | £38.78 | £487.72 | £150 | £448.94 | retained |
| 2021-06-30 | C9 | 0.52 | 5% | £75.03 | £559.89 | £150 | £484.86 | retained |
| 2021-09-30 | C4 | 0.95 | 8% | £129.28 | £382.74 | £150 | £253.46 | retained |
| 2021-12-30 | C1 | 0.95 | 8% | £67.39 | £204.63 | £150 | £-67.39 | churned_despite_offer |
| 2021-12-30 | C5 | 0.95 | 8% | £617.59 | £2026.25 | £400 | £-617.59 | churned_despite_offer |
| 2021-12-30 | C7 | 0.95 | 8% | £299.68 | £830.48 | £150 | £530.80 | retained |
| 2022-03-31 | C2 | 0.95 | 8% | £96.68 | £365.40 | £150 | £-96.68 | churned_despite_offer |
| 2022-03-31 | C6 | 0.95 | 8% | £1247.32 | £4752.49 | £400 | £3505.17 | retained |
| 2022-03-31 | C8 | 0.95 | 8% | £327.63 | £1246.03 | £150 | £918.40 | retained |
| 2022-06-30 | C9 | 0.52 | 5% | £146.76 | £640.54 | £150 | £493.79 | retained |
| 2023-03-31 | C6 | 0.95 | 8% | £908.43 | £2941.33 | £400 | £2032.89 | retained |
| 2024-03-30 | C6 | 0.50 | 5% | £307.27 | £2140.84 | £400 | £-307.27 | churned_despite_offer |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C5 | 2016-12-31 | 2021-12-30 | 60 | churned |
| C2 | 2017-04-01 | 2022-03-31 | 60 | churned |
| C6 | 2017-04-01 | 2024-03-30 | 84 | churned |
| C8 | 2017-04-01 | (window end) | 105 | active |
| C4 | 2017-10-01 | 2024-09-29 | 84 | churned |
| C9 | 2018-07-01 | (window end) | 90 | active |
| C1 | 2021-12-30 | 2021-12-30 | 0 | churned |
| C7 | 2021-12-30 | (window end) | 48 | active |

**Eventually churned (5/8)**: C5, C2, C6, C4, C1 — avg 58 months post-retention before final churn.
**Still active (3/8)**: C8, C9, C7 — survived to simulation end.

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £9,888.92 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £-584.85 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £-672.38 |
| 2017 | £-497.41 |
| 2018 | £26.24 |
| 2019 | £567.19 |
| 2020 | £154.60 |
| 2021 | £-1,535.81 |
| 2022 | £-1,506.24 |
| 2023 | £-1,175.08 | ← trailing
| 2024 | £1,033.29 | ← trailing
| 2025 | £-189.74 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £342.72 | — |
| C2 | £175.93 | — |
| C2_2 | — | £333.03 |
| C3 | £431.51 | — |
| C4 | £321.81 | £-998.19 |
| C5 | £1,804.18 | — |
| C6 | £1,427.05 | £235.93 |
| C7 | £1,173.62 | £-799.70 |
| C8 | £1,843.05 | £537.71 |
| C9 | £1,866.09 | £106.38 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £5.47 | — | — | — | — | £156.86 | — | £356.03 | — | — |
| 2017 | £-54.46 | £438.68 | — | £119.60 | £977.86 | £-18.14 | £1,025.90 | £111.68 | £1,014.51 | £749.72 |
| 2018 | £183.27 | £21.66 | — | £225.26 | £1,103.41 | £835.36 | £421.88 | £677.20 | £834.58 | £947.26 |
| 2019 | £322.54 | £209.24 | — | £319.97 | £1,208.08 | £1,218.57 | £724.01 | £940.18 | £904.05 | £1,275.30 |
| 2020 | £313.57 | £310.29 | — | £280.27 | £1,161.94 | £1,358.04 | £846.88 | £1,014.17 | £982.10 | £1,268.01 |
| 2021 | £250.84 | £201.52 | — | £278.37 | £990.21 | £1,287.01 | £612.71 | £991.43 | £768.87 | £1,154.90 |
| 2022 | £265.27 | £119.33 | £-340.97 | £306.78 | £615.87 | £1,072.10 | £420.12 | £913.47 | £665.64 | £1,060.75 |
| 2023 | £256.72 | £122.74 | £-16.94 | £289.51 | £55.08 | £1,152.20 | £801.59 | £350.59 | £965.13 | £1,145.69 |
| 2024 | £203.27 | £120.80 | £294.51 | £278.37 | £198.48 | £1,095.41 | £831.28 | £600.03 | £1,087.62 | £1,331.44 |
| 2025 | £210.73 | £111.57 | £295.94 | £253.84 | £179.42 | £989.52 | £856.47 | £744.73 | £1,075.94 | £1,065.10 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £477.16, range £24.32–£1,174.28.

- C1: cost to serve £370.91, net margin after CTS £132.08
- C1g: cost to serve £37.18, net margin after CTS £208.04
- C2: cost to serve £407.25, net margin after CTS £140.32
- C2_2: cost to serve £322.74, net margin after CTS £664.25
- C2g: cost to serve £42.95, net margin after CTS £29.30 — MARGIN_SQUEEZE (below 2% benchmark)
- C3: cost to serve £248.58, net margin after CTS £153.74
- C3g: cost to serve £24.32, net margin after CTS £114.73
- C4: cost to serve £607.70, net margin after CTS £539.41
- C4g: cost to serve £169.85, net margin after CTS £-153.31 — **NET_NEGATIVE** (tariff uplift needed: +1.9%)
- C5: cost to serve £818.68, net margin after CTS £1,529.30
- C6: cost to serve £1,174.28, net margin after CTS £1,749.63
- C7: cost to serve £869.52, net margin after CTS £1,663.59
- C8: cost to serve £829.53, net margin after CTS £2,481.31
- C9: cost to serve £756.76, net margin after CTS £2,672.30

**Activity-Based Pricing Actions**

The following 1 customer(s) are loss-making after cost-to-serve and require immediate tariff review:
  - C4g: net margin after CTS £-153.31 on revenue £8,034.33 — raise tariff by ≥1.9% to break even
The following 1 customer(s) are profitable but below the 2% net-margin benchmark (MARGIN_SQUEEZE): C2g

## Tariff Repricing Impact Assessment

Estimated churn risk at the break-even tariff level for each loss-making customer.
Active = current opportunity; churned = retrospective counterfactual.

| Customer | Fuel | Seg | Status | Uplift needed | Total loss | Churn @ B/E | Decision |
|----------|------|-----|--------|--------------|-----------|-------------|----------|
| C4g | gas | resi | active | +1.9% | £153.31 | 4% | Raise — churn risk manageable |

**Repriceable now (1)**: C4g — break-even churn risk below 40%. Uplift advised.

## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 36 recovery surcharge(s) at renewal based on prior-term losses (4 gas). Avg surcharge: 11.3%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C1 | electricity | 2016-12-31 | £-30.74 | £250.29 | +7.3% | £77.06/MWh | £91.87/MWh |
| C5 | electricity | 2016-12-31 | £-181.59 | £1,235.71 | +9.7% | £77.06/MWh | £94.02/MWh |
| C7 | electricity | 2016-12-31 | £-85.94 | £904.73 | +4.5% | £77.06/MWh | £89.63/MWh |
| C2 | electricity | 2017-04-01 | £-100.01 | £405.78 | +19.6% | £76.79/MWh | £103.45/MWh |
| C6 | electricity | 2017-04-01 | £-351.72 | £1,086.93 | +20.0% | £76.79/MWh | £100.21/MWh |
| C8 | electricity | 2017-04-01 | £-130.81 | £753.39 | +12.4% | £76.79/MWh | £90.97/MWh |
| C3 | electricity | 2017-07-01 | £-39.80 | £257.84 | +10.4% | £68.26/MWh | £77.11/MWh |
| C9 | electricity | 2017-07-01 | £-60.30 | £758.21 | +3.0% | £68.26/MWh | £71.41/MWh |
| C4 | electricity | 2017-10-01 | £-70.60 | £436.00 | +11.2% | £74.02/MWh | £86.51/MWh |
| C1 | electricity | 2017-12-31 | £-62.87 | £345.32 | +13.2% | £85.23/MWh | £101.30/MWh |
| C5 | electricity | 2017-12-31 | £-274.07 | £1,704.47 | +11.1% | £85.23/MWh | £99.09/MWh |
| C7 | electricity | 2017-12-31 | £-214.68 | £1,171.56 | +13.3% | £85.23/MWh | £98.45/MWh |
| C2g | gas | 2018-04-01 | £-44.36 | £251.00 | +12.7% | £23.77/MWh | £26.69/MWh |
| C3 | electricity | 2018-07-01 | £-44.77 | £345.72 | +8.0% | £87.62/MWh | £107.47/MWh |
| C9 | electricity | 2018-07-01 | £-134.97 | £1,007.77 | +8.4% | £87.62/MWh | £107.33/MWh |
| C2 | electricity | 2019-04-01 | £-250.81 | £653.58 | +20.0% | £87.45/MWh | £105.68/MWh |
| C6 | electricity | 2019-04-01 | £-633.22 | £1,785.99 | +20.0% | £87.45/MWh | £105.56/MWh |
| C8 | electricity | 2019-04-01 | £-184.56 | £1,268.04 | +9.6% | £87.45/MWh | £96.47/MWh |
| C3 | electricity | 2020-06-30 | £-20.77 | £344.10 | +1.0% | £59.11/MWh | £64.88/MWh |
| C2 | electricity | 2021-03-31 | £-84.68 | £488.89 | +12.3% | £95.98/MWh | £115.53/MWh |
| C6 | electricity | 2021-03-31 | £-260.76 | £1,341.45 | +14.4% | £95.98/MWh | £121.68/MWh |
| C4g | gas | 2021-09-30 | £-82.13 | £199.63 | +20.0% | £45.77/MWh | £58.76/MWh |
| C1 | electricity | 2021-12-30 | £-31.04 | £364.26 | +3.5% | £259.05/MWh | £300.83/MWh |
| C5 | electricity | 2021-12-30 | £-201.63 | £1,790.04 | +6.3% | £259.05/MWh | £308.79/MWh |
| C7 | electricity | 2021-12-30 | £-75.22 | £1,320.35 | +0.7% | £259.05/MWh | £292.62/MWh |
| C2 | electricity | 2022-03-31 | £-237.30 | £823.94 | +20.0% | £265.84/MWh | £345.27/MWh |
| C6 | electricity | 2022-03-31 | £-749.21 | £2,270.04 | +20.0% | £265.84/MWh | £346.48/MWh |
| C8 | electricity | 2022-03-31 | £-418.50 | £1,386.19 | +20.0% | £265.84/MWh | £346.20/MWh |
| C9 | electricity | 2022-06-30 | £-125.27 | £1,501.61 | +3.3% | £210.77/MWh | £237.27/MWh |
| C4g | gas | 2022-09-30 | £-81.16 | £1,292.63 | +1.3% | £155.84/MWh | £174.40/MWh |
| C2_2 | electricity | 2023-03-31 | £-896.84 | £2,699.32 | +20.0% | £228.40/MWh | £303.67/MWh |
| C6 | electricity | 2023-03-31 | £-488.59 | £6,392.99 | +2.6% | £228.40/MWh | £252.34/MWh |
| C4 | electricity | 2023-09-30 | £-713.67 | £2,298.73 | +20.0% | £124.97/MWh | £144.64/MWh |
| C4g | gas | 2023-09-30 | £-395.92 | £3,836.83 | +5.3% | £35.28/MWh | £39.62/MWh |
| C7 | electricity | 2023-12-30 | £-1,070.53 | £3,380.62 | +20.0% | £147.77/MWh | £177.14/MWh |
| C2_2 | electricity | 2025-03-30 | £-96.93 | £1,380.47 | +2.0% | £168.56/MWh | £180.02/MWh |

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 87 renewal(s) (20 gas) based on recent portfolio-wide margin rates: 66 surcharge(s), 21 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | -14.2% | +11.1% | £77.06/MWh | £85.63/MWh |
| C1g | gas | 2016-12-31 | 15.2% | -3.6% | £18.35/MWh | £17.69/MWh |
| C5 | electricity | 2016-12-31 | -14.4% | +11.2% | £77.06/MWh | £85.71/MWh |
| C7 | electricity | 2016-12-31 | -14.6% | +11.3% | £77.06/MWh | £85.77/MWh |
| C2 | electricity | 2017-04-01 | -17.2% | +12.6% | £76.79/MWh | £86.46/MWh |
| C2g | gas | 2017-04-01 | 15.8% | -3.9% | £17.41/MWh | £16.73/MWh |
| C6 | electricity | 2017-04-01 | -9.5% | +8.8% | £76.79/MWh | £83.51/MWh |
| C8 | electricity | 2017-04-01 | -2.9% | +5.4% | £76.79/MWh | £80.96/MWh |
| C3 | electricity | 2017-07-01 | 3.4% | +2.3% | £68.26/MWh | £69.82/MWh |
| C3g | gas | 2017-07-01 | 10.9% | -1.4% | £16.93/MWh | £16.69/MWh |
| C9 | electricity | 2017-07-01 | 4.8% | +1.6% | £68.26/MWh | £69.36/MWh |
| C4 | electricity | 2017-10-01 | -2.2% | +5.1% | £74.02/MWh | £77.80/MWh |
| C4g | gas | 2017-10-01 | 10.1% | -1.0% | £21.73/MWh | £21.51/MWh |
| C1 | electricity | 2017-12-31 | -2.0% | +5.0% | £85.23/MWh | £89.48/MWh |
| C1g | gas | 2017-12-31 | 8.3% | -0.1% | £25.19/MWh | £25.16/MWh |
| C5 | electricity | 2017-12-31 | -1.4% | +4.7% | £85.23/MWh | £89.21/MWh |
| C7 | electricity | 2017-12-31 | 4.1% | +1.9% | £85.23/MWh | £86.87/MWh |
| C2 | electricity | 2018-04-01 | 10.3% | -1.2% | £92.46/MWh | £91.39/MWh |
| C2g | gas | 2018-04-01 | 8.7% | -0.4% | £23.77/MWh | £23.68/MWh |
| C6 | electricity | 2018-04-01 | -1.6% | +4.8% | £92.46/MWh | £96.91/MWh |
| C8 | electricity | 2018-04-01 | -13.4% | +10.7% | £92.46/MWh | £102.35/MWh |
| C3 | electricity | 2018-07-01 | -19.3% | +13.6% | £87.62/MWh | £99.56/MWh |
| C3g | gas | 2018-07-01 | 13.9% | -2.9% | £24.38/MWh | £23.66/MWh |
| C9 | electricity | 2018-07-01 | -18.0% | +13.0% | £87.62/MWh | £99.02/MWh |
| C4 | electricity | 2018-10-01 | -2.9% | +5.5% | £99.52/MWh | £104.96/MWh |
| C4g | gas | 2018-10-01 | 13.1% | -2.6% | £31.63/MWh | £30.82/MWh |
| C1 | electricity | 2018-12-31 | 7.8% | +0.1% | £105.79/MWh | £105.88/MWh |
| C1g | gas | 2018-12-31 | 11.7% | -1.8% | £33.03/MWh | £32.42/MWh |
| C5 | electricity | 2018-12-31 | 13.2% | -2.6% | £105.79/MWh | £103.04/MWh |
| C7 | electricity | 2018-12-31 | 10.0% | -1.0% | £105.79/MWh | £104.73/MWh |
| C2 | electricity | 2019-04-01 | 6.6% | +0.7% | £87.45/MWh | £88.06/MWh |
| C2g | gas | 2019-04-01 | 13.5% | -2.8% | £22.30/MWh | £21.68/MWh |
| C6 | electricity | 2019-04-01 | 6.8% | +0.6% | £87.45/MWh | £87.96/MWh |
| C8 | electricity | 2019-04-01 | 6.6% | +0.7% | £87.45/MWh | £88.05/MWh |
| C3 | electricity | 2019-07-01 | 7.7% | +0.2% | £76.18/MWh | £76.30/MWh |
| C3g | gas | 2019-07-01 | 14.3% | -3.1% | £16.65/MWh | £16.13/MWh |
| C9 | electricity | 2019-07-01 | 4.1% | +2.0% | £76.18/MWh | £77.67/MWh |
| C4 | electricity | 2019-10-01 | 2.9% | +2.5% | £76.50/MWh | £78.44/MWh |
| C4g | gas | 2019-10-01 | 15.8% | -3.9% | £14.15/MWh | £13.59/MWh |
| C1 | electricity | 2019-12-31 | 2.8% | +2.6% | £79.28/MWh | £81.35/MWh |
| C1g | gas | 2019-12-31 | 19.1% | -5.0% | £16.63/MWh | £15.80/MWh |
| C5 | electricity | 2019-12-31 | 1.4% | +3.3% | £79.28/MWh | £81.89/MWh |
| C7 | electricity | 2019-12-31 | 3.5% | +2.3% | £79.28/MWh | £81.08/MWh |
| C2 | electricity | 2020-03-31 | 3.6% | +2.2% | £66.88/MWh | £68.36/MWh |
| C2g | gas | 2020-03-31 | 16.8% | -4.4% | £14.87/MWh | £14.22/MWh |
| C6 | electricity | 2020-03-31 | -2.1% | +5.1% | £66.88/MWh | £70.27/MWh |
| C8 | electricity | 2020-03-31 | -7.6% | +7.8% | £66.88/MWh | £72.09/MWh |
| C3 | electricity | 2020-06-30 | -9.3% | +8.7% | £59.11/MWh | £64.22/MWh |
| C9 | electricity | 2020-06-30 | -9.3% | +8.7% | £59.11/MWh | £64.22/MWh |
| C4 | electricity | 2020-09-30 | -10.4% | +9.2% | £76.20/MWh | £83.20/MWh |
| C4g | gas | 2020-09-30 | 20.7% | -5.0% | £9.55/MWh | £9.07/MWh |
| C1 | electricity | 2020-12-30 | -6.0% | +7.0% | £90.60/MWh | £96.94/MWh |
| C1g | gas | 2020-12-30 | 6.3% | +0.9% | £18.42/MWh | £18.58/MWh |
| C5 | electricity | 2020-12-30 | -3.3% | +5.6% | £90.60/MWh | £95.70/MWh |
| C7 | electricity | 2020-12-30 | -4.9% | +6.5% | £90.60/MWh | £96.45/MWh |
| C2 | electricity | 2021-03-31 | -6.3% | +7.2% | £95.98/MWh | £102.85/MWh |
| C2g | gas | 2021-03-31 | -2.7% | +5.3% | £23.81/MWh | £25.08/MWh |
| C6 | electricity | 2021-03-31 | -13.6% | +10.8% | £95.98/MWh | £106.33/MWh |
| C8 | electricity | 2021-03-31 | -19.7% | +13.8% | £95.98/MWh | £109.27/MWh |
| C9 | electricity | 2021-06-30 | -24.4% | +15.0% | £105.48/MWh | £121.30/MWh |
| C4 | electricity | 2021-09-30 | -25.1% | +15.0% | £255.49/MWh | £293.81/MWh |
| C4g | gas | 2021-09-30 | -6.0% | +7.0% | £45.77/MWh | £48.96/MWh |
| C1 | electricity | 2021-12-30 | -16.4% | +12.2% | £259.05/MWh | £290.59/MWh |
| C5 | electricity | 2021-12-30 | -16.4% | +12.2% | £259.05/MWh | £290.59/MWh |
| C7 | electricity | 2021-12-30 | -16.4% | +12.2% | £259.05/MWh | £290.59/MWh |
| C2 | electricity | 2022-03-31 | -8.5% | +8.2% | £265.84/MWh | £287.72/MWh |
| C6 | electricity | 2022-03-31 | -9.2% | +8.6% | £265.84/MWh | £288.73/MWh |
| C8 | electricity | 2022-03-31 | -9.0% | +8.5% | £265.84/MWh | £288.50/MWh |
| C9 | electricity | 2022-06-30 | -9.9% | +8.9% | £210.77/MWh | £229.59/MWh |
| C4 | electricity | 2022-09-30 | -8.1% | +8.1% | £298.27/MWh | £322.32/MWh |
| C4g | gas | 2022-09-30 | -13.0% | +10.5% | £155.84/MWh | £172.20/MWh |
| C7 | electricity | 2022-12-30 | -7.6% | +7.8% | £245.49/MWh | £264.63/MWh |
| C2_2 | electricity | 2023-03-31 | -13.6% | +10.8% | £228.40/MWh | £253.06/MWh |
| C6 | electricity | 2023-03-31 | -7.3% | +7.6% | £228.40/MWh | £245.85/MWh |
| C8 | electricity | 2023-03-31 | -6.8% | +7.4% | £228.40/MWh | £245.31/MWh |
| C9 | electricity | 2023-06-30 | 5.2% | +1.4% | £156.02/MWh | £158.22/MWh |
| C4 | electricity | 2023-09-30 | 15.1% | -3.5% | £124.97/MWh | £120.53/MWh |
| C4g | gas | 2023-09-30 | -5.3% | +6.7% | £35.28/MWh | £37.62/MWh |
| C7 | electricity | 2023-12-30 | 8.2% | -0.1% | £147.77/MWh | £147.61/MWh |
| C2_2 | electricity | 2024-03-30 | 8.6% | -0.3% | £132.98/MWh | £132.59/MWh |
| C6 | electricity | 2024-03-30 | 2.6% | +2.7% | £132.98/MWh | £136.56/MWh |
| C8 | electricity | 2024-03-30 | 2.6% | +2.7% | £132.98/MWh | £136.56/MWh |
| C9 | electricity | 2024-06-29 | 1.5% | +3.2% | £117.04/MWh | £120.82/MWh |
| C4 | electricity | 2024-09-29 | -0.7% | +4.3% | £121.81/MWh | £127.09/MWh |
| C7 | electricity | 2024-12-29 | -0.7% | +4.3% | £164.53/MWh | £171.65/MWh |
| C2_2 | electricity | 2025-03-30 | -1.4% | +4.7% | £168.56/MWh | £176.45/MWh |
| C8 | electricity | 2025-03-30 | -8.3% | +8.1% | £168.56/MWh | £182.28/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **2** | Blind misses: **2** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 0 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £403.31 | deliberate: £0.00 | total: £403.31

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.14 | No | £112.78 |
| C4 | 2024-09-29 | Blind miss | 0.11 | 0.23 | No | £290.54 |

## Dual-Fuel Account P&L (Phase 17d)

4 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C1+C1g | £-45.61 | £235.68 | £190.06 | Yes |
| C3+C3g | £-26.78 | £134.68 | £107.90 | Yes |
| C2+C2g | £-501.38 | £52.97 | £-448.41 | Yes |
| C4+C4g | £-501.62 | £-18.29 | £-519.91 | No |

Gas accretive in 3/4 dual-fuel accounts. Total gas net margin: £405.04.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £-3,795.34 across 14 billing accounts. Revenue: £113,750.23.

| # | Customer | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|---------|-------------|---------|------------|-------------|
| 1 | C9 | £13,252.25 | £3,429.07 | £174.95 | £239.18 | 1.8% |
| 2 | C1g | £1,515.34 | £245.22 | £9.54 | £235.68 | 15.6% |
| 3 | C3g | £986.94 | £139.05 | £4.38 | £134.68 | 13.6% |
| 4 | C2g | £1,803.99 | £72.25 | £19.28 | £52.97 | 2.9% |
| 5 | C8 | £16,204.81 | £3,310.84 | £358.75 | £43.20 | 0.3% |
| 6 | C4g | £8,034.33 | £16.55 | £34.84 | £-18.29 | -0.2% |
| 7 | C3 | £1,431.61 | £402.32 | £15.49 | £-26.78 | -1.9% |
| 8 | C1 | £2,049.19 | £503.00 | £23.37 | £-45.61 | -2.2% |
| 9 | C2_2 | £7,362.09 | £986.99 | £87.06 | £-220.56 | -3.0% |
| 10 | C5 | £9,883.25 | £2,347.98 | £208.63 | £-397.19 | -4.0% |
| 11 | C2 | £3,865.91 | £547.58 | £43.62 | £-501.38 | -13.0% |
| 12 | C4 | £8,390.43 | £1,147.11 | £129.12 | £-501.62 | -6.0% |
| 13 | C7 | £17,519.37 | £2,533.11 | £225.60 | £-929.41 | -5.3% |
| 14 | C6 | £21,450.73 | £2,923.91 | £1,013.51 | £-1,860.21 | -8.7% |

## Transaction Log

Total events: 2,395,784

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 5 |
| bad_debt_event | 1,117 |
| billing_event | 1,117 |
| capital_charge_event | 1,176,799 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,117 |
| payment_received_event | 1,117 |
| settlement_event | 1,213,281 |
| vat_remittance_event | 1,117 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £182,148.04 |
|   Less: VAT remitted to HMRC | (£15,112.55) |
| = Revenue (ex-VAT) | £167,035.49 |
| Less: non-commodity pass-through | (£42,887.46) |
| Wholesale cost (settlement events) | (£95,145.26) |
| Gross margin | £29,002.78 |
| Capital charges | (£2,348.14) |
| Net margin | £26,654.64 |

_Cash reconciliation: of £182,148.04 billed, bad debt of £3,565.05 was written off, leaving £178,582.99 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £38,202.14._

| Acquisition spend | (£1,250.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £19,704.64 |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £19,704.64

## 2016

**Trading & Risk**

- Net margin: £-672.38 (gross £636.67, capital £193.74)
  - Electricity: gross £549.85, capital £187.42, net £-752.87
  - Gas: gross £86.81, capital £6.32, net £80.49
- Treasury at year end: £29,506.95
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
  - 2016-01-13: treasury £29,660.85, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-02-12: treasury £29,656.56, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-03-13: treasury £29,650.35, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-12: treasury £29,646.07, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-05-12: treasury £29,639.17, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-06-11: treasury £29,632.71, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-07-11: treasury £29,624.46, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-08-10: treasury £29,616.98, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-09-09: treasury £29,609.03, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-10-09: treasury £29,600.44, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-11-08: treasury £29,591.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-12-08: treasury £29,580.67, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-08: treasury £29,575.32, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-05-08: treasury £29,568.10, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-06-07: treasury £29,561.53, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-07-07: treasury £29,554.64, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-06: treasury £29,548.04, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-09-05: treasury £29,541.56, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-10-05: treasury £29,534.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-11-04: treasury £29,525.92, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-12-04: treasury £29,515.23, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-05: treasury £29,479.86, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-04-26: treasury £29,457.89, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-05-26: treasury £29,434.29, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-06-25: treasury £29,415.41, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-07-25: treasury £29,397.29, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-08-24: treasury £29,380.98, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-09-23: treasury £29,362.18, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-10-23: treasury £29,337.55, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-11-22: treasury £29,296.09, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-12-22: treasury £29,259.01, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-04-21: treasury £29,122.86, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-05-21: treasury £29,114.04, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-06-20: treasury £29,108.17, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-20: treasury £29,102.90, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-08-19: treasury £29,098.26, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-09-18: treasury £29,092.38, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-10-18: treasury £29,083.60, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-11-17: treasury £29,069.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-12-17: treasury £29,052.36, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-16: treasury £28,998.45, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-08-15: treasury £28,996.66, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-09-14: treasury £28,994.48, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-10-14: treasury £28,992.02, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-11-13: treasury £28,988.31, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-12-13: treasury £28,984.13, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-07-03: treasury £28,991.42, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-08-02: treasury £28,988.78, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-09-01: treasury £28,986.40, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-01: treasury £28,983.27, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-31: treasury £28,978.84, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-11-30: treasury £28,970.15, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-12-30: treasury £28,967.27, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-28: treasury £28,928.10, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-11-27: treasury £28,921.43, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-12-27: treasury £28,916.59, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.03
- Worst single period: C8 on 2016-11-20 period 36, net margin £-0.53

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £172.79
  - By billing account: C1 £5.47, C5 £156.86, C7 £356.03
- Bill shock events (>=20%): 20 -- C5 2016-05-31 (27%); C5 2016-06-30 (20%); C5 2016-10-31 (41%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (79%); C7 2016-11-30 (52%); C6 2016-05-31 (25%); C6 2016-06-30 (23%); C6 2016-10-31 (40%); C6 2016-11-30 (45%); C8 2016-05-31 (40%); C8 2016-06-30 (41%); C8 2016-09-30 (23%); C8 2016-10-31 (104%); C8 2016-11-30 (69%); C9 2016-10-31 (77%); C9 2016-11-30 (59%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £66.57-£91.87/MWh, net margin £-31.10 -- **net-negative**
- C1g (gas): tariff £16.64-£17.69/MWh, net margin £29.08
- C2 (electricity): tariff £56.89/MWh, net margin £-70.11 -- **net-negative**
- C2g (gas): tariff £15.86/MWh, net margin £5.36
- C3 (electricity): tariff £57.51/MWh, net margin £-17.19 -- **net-negative**
- C3g (gas): tariff £14.02/MWh, net margin £17.77
- C4 (electricity): tariff £61.12/MWh, net margin £-15.95 -- **net-negative**
- C4g (gas): tariff £17.42/MWh, net margin £28.28
- C5 (electricity): tariff £66.57-£94.02/MWh, net margin £-184.06 -- **net-negative**
- C6 (electricity): tariff £56.89/MWh, net margin £-235.67 -- **net-negative**
- C7 (electricity): tariff £52.30-£99.85/MWh, net margin £-88.61 -- **net-negative**
- C8 (electricity): tariff £44.70-£85.34/MWh, net margin £-84.81 -- **net-negative**
- C9 (electricity): tariff £45.19-£86.27/MWh, net margin £-25.36 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 30.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.892, average bill shock 13.4%, bad debt provision £226.67, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,394.49 vs. naked (unhedged) net margin: £862.95
- hedging cost £2,257.44 vs. a fully unhedged book (commodity-only: actual net £-1,394.49 vs. naked net £862.95)
  - C1: actual £-93.62 vs. naked £148.85 -- hedging cost £242.47
  - C1g: actual £65.00 vs. naked £59.59 -- hedging added £5.41
  - C2: actual £-100.01 vs. naked £72.07 -- hedging cost £172.08
  - C2g: actual £4.87 vs. naked £33.40 -- hedging cost £28.54
  - C3: actual £-39.80 vs. naked £21.01 -- hedging cost £60.81
  - C3g: actual £32.39 vs. naked £1.14 -- hedging added £31.25
  - C4: actual £-70.60 vs. naked £71.91 -- hedging cost £142.50
  - C4g: actual £106.39 vs. naked £54.72 -- hedging added £51.67
  - C5: actual £-455.66 vs. naked £304.76 -- hedging cost £760.42
  - C6: actual £-351.72 vs. naked £-357.75 -- hedging added £6.03
  - C7: actual £-300.62 vs. naked £423.24 -- hedging cost £723.86
  - C8: actual £-130.81 vs. naked £-1.30 -- hedging cost £129.51
  - C9: actual £-60.30 vs. naked £31.31 -- hedging cost £91.61

**Year narrative:** 2016 produced a net loss of £-672.38 across 13 accounts. The risk committee intervened 81 time(s), raising hedge fractions in response to elevated VaR. 20 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £-497.41 (gross £1,468.00, capital £151.32)
  - Electricity: gross £1,319.53, capital £141.36, net £-635.92
  - Gas: gross £148.47, capital £9.96, net £138.51
- Treasury at year end: £28,535.67
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.95 (avg 0.95), C4 0.85 (avg 0.85), C4g 0.95 (avg 0.95), C5 0.85 (avg 0.85), C6 0.95 (avg 0.95), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 42
  - 2017-01-03: treasury £29,506.08, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-02-02: treasury £29,495.38, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-03-04: treasury £29,485.35, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-01-21: treasury £29,218.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-02-20: treasury £29,175.14, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-03-22: treasury £29,140.66, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-01-16: treasury £29,035.78, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-02-15: treasury £29,016.48, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-03-17: treasury £29,004.89, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-01-12: treasury £28,980.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-02-11: treasury £28,976.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-03-13: treasury £28,972.56, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-04-12: treasury £28,969.42, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-05-12: treasury £28,965.52, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-06-11: treasury £28,961.76, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-01-29: treasury £28,958.58, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-02-28: treasury £28,953.39, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-03-30: treasury £28,950.25, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-04-29: treasury £28,943.52, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-05-29: treasury £28,936.24, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-06-28: treasury £28,931.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-01-26: treasury £28,910.33, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-02-25: treasury £28,904.28, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-03-27: treasury £28,898.93, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-04-26: treasury £28,893.27, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-05-26: treasury £28,886.44, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-06-25: treasury £28,880.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-07-25: treasury £28,875.12, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-08-24: treasury £28,869.34, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-09-23: treasury £28,862.76, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-01-15: treasury £28,964.58, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-02-14: treasury £28,959.11, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-03-16: treasury £28,953.91, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-04-15: treasury £28,949.13, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-05-15: treasury £28,944.17, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-06-14: treasury £28,939.68, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-07-14: treasury £28,935.23, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-08-13: treasury £28,930.84, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-09-12: treasury £28,926.23, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-10-12: treasury £28,921.09, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-11-11: treasury £28,915.47, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-12-11: treasury £28,908.97, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C6 on 2017-01-23 period 19, net margin £-0.17

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £485.04
  - By billing account: C1 £-54.46, C2 £438.68, C3 £119.60, C4 £977.86, C5 £-18.14, C6 £1,025.90, C7 £111.68, C8 £1,014.51, C9 £749.72
- Bill shock events (>=20%): 25 -- C5 2017-01-31 (42%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (56%); C7 2017-01-31 (45%); C7 2017-02-28 (28%); C7 2017-05-31 (31%); C7 2017-06-30 (32%); C7 2017-09-30 (27%); C7 2017-10-31 (22%); C7 2017-11-30 (77%); C6 2017-05-31 (22%); C6 2017-11-30 (50%); C8 2017-05-31 (40%); C8 2017-06-30 (36%); C8 2017-09-30 (46%); C8 2017-10-31 (22%); C8 2017-11-30 (84%); C8 2017-12-31 (22%); C9 2017-05-31 (33%); C9 2017-06-30 (26%); C9 2017-09-30 (30%); C9 2017-10-31 (22%); C9 2017-11-30 (70%); C4 2017-10-31 (26%)
- Churn risk (accounts renewing in 2017): 6 at risk (≥20% churn prob): C1 20%, C5 32%, C6 35%, C7 35%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £91.87-£101.30/MWh, net margin £-62.52 -- **net-negative**
- C1g (gas): tariff £17.69-£25.16/MWh, net margin £36.00
- C2 (electricity): tariff £56.89-£103.45/MWh, net margin £54.07
- C2g (gas): tariff £15.86-£16.73/MWh, net margin £-31.75 -- **net-negative**
- C3 (electricity): tariff £57.51-£77.11/MWh, net margin £-39.58 -- **net-negative**
- C3g (gas): tariff £14.02-£16.69/MWh, net margin £30.95
- C4 (electricity): tariff £61.12-£86.51/MWh, net margin £-32.02 -- **net-negative**
- C4g (gas): tariff £17.42-£21.51/MWh, net margin £103.31
- C5 (electricity): tariff £94.02-£99.09/MWh, net margin £-273.19 -- **net-negative**
- C6 (electricity): tariff £56.89-£100.21/MWh, net margin £-2.18 -- **net-negative**
- C7 (electricity): tariff £70.43-£134.45/MWh, net margin £-213.31 -- **net-negative**
- C8 (electricity): tariff £44.70-£136.45/MWh, net margin £20.12
- C9 (electricity): tariff £45.19-£107.11/MWh, net margin £-87.32 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 10.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.894, average bill shock 11.8%, bad debt provision £368.39, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £754.90 vs. naked (unhedged) net margin: £2,443.36
- hedging cost £1,688.47 vs. a fully unhedged book (commodity-only: actual net £754.90 vs. naked net £2,443.36)
  - C1: actual £44.26 vs. naked £129.91 -- hedging cost £85.65
  - C1g: actual £56.29 vs. naked £27.00 -- hedging added £29.29
  - C2: actual £107.33 vs. naked £356.32 -- hedging cost £248.99
  - C2g: actual £-44.36 vs. naked £-22.00 -- hedging cost £22.37
  - C3: actual £-44.77 vs. naked £72.98 -- hedging cost £117.75
  - C3g: actual £31.08 vs. naked £-36.08 -- hedging added £67.15
  - C4: actual £57.71 vs. naked £183.68 -- hedging cost £125.97
  - C4g: actual £97.32 vs. naked £2.41 -- hedging added £94.92
  - C5: actual £162.31 vs. naked £477.04 -- hedging cost £314.73
  - C6: actual £163.22 vs. naked £319.17 -- hedging cost £155.95
  - C7: actual £147.47 vs. naked £418.47 -- hedging cost £271.01
  - C8: actual £112.02 vs. naked £390.23 -- hedging cost £278.22
  - C9: actual £-134.97 vs. naked £124.23 -- hedging cost £259.20

**Year narrative:** 2017 produced a net loss of £-497.41 across 13 accounts. The risk committee intervened 42 time(s), raising hedge fractions in response to elevated VaR. 25 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £26.24 (gross £2,558.49, capital £193.86)
  - Electricity: gross £2,371.75, capital £186.70, net £-153.34
  - Gas: gross £186.74, capital £7.16, net £179.58
- Treasury at year end: £29,023.74
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 1.00 (avg 1.00), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.85 (avg 0.85), C4g 1.00 (avg 1.00), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C8 on 2018-03-01 period 43, net margin £-0.37

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2018): £583.32
  - By billing account: C1 £183.27, C2 £21.66, C3 £225.26, C4 £1,103.41, C5 £835.36, C6 £421.88, C7 £677.20, C8 £834.58, C9 £947.26
- Bill shock events (>=20%): 34 -- C1g 2018-01-31 (20%); C5 2018-04-30 (32%); C5 2018-06-30 (21%); C5 2018-10-31 (32%); C5 2018-11-30 (27%); C7 2018-04-30 (39%); C7 2018-05-31 (29%); C7 2018-06-30 (31%); C7 2018-09-30 (30%); C7 2018-10-31 (47%); C7 2018-11-30 (33%); C2g 2018-04-30 (26%); C6 2018-04-30 (31%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (33%); C8 2018-05-31 (38%); C8 2018-06-30 (43%); C8 2018-08-31 (25%); C8 2018-09-30 (53%); C8 2018-10-31 (55%); C8 2018-11-30 (30%); C3 2018-07-31 (23%); C3g 2018-07-31 (25%); C9 2018-04-30 (32%); C9 2018-05-31 (35%); C9 2018-06-30 (34%); C9 2018-08-31 (43%); C9 2018-09-30 (45%); C9 2018-10-31 (40%); C9 2018-12-31 (20%); C4g 2018-10-31 (30%)
- Churn risk (accounts renewing in 2018): 7 at risk (≥20% churn prob): C1 20%, C3 23%, C5 41%, C6 32%, C7 41%, C8 38%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £101.30-£105.88/MWh, net margin £44.16
- C1g (gas): tariff £25.16-£32.42/MWh, net margin £56.49
- C2 (electricity): tariff £91.39-£103.45/MWh, net margin £-159.49 -- **net-negative**
- C2g (gas): tariff £16.73-£26.69/MWh, net margin £-6.28 -- **net-negative**
- C3 (electricity): tariff £77.11-£107.47/MWh, net margin £10.22
- C3g (gas): tariff £16.69-£23.66/MWh, net margin £31.95
- C4 (electricity): tariff £86.51-£104.96/MWh, net margin £48.78
- C4g (gas): tariff £21.51-£30.82/MWh, net margin £97.41
- C5 (electricity): tariff £99.09-£103.04/MWh, net margin £162.37
- C6 (electricity): tariff £96.91-£100.21/MWh, net margin £-376.68 -- **net-negative**
- C7 (electricity): tariff £77.35-£157.09/MWh, net margin £148.98
- C8 (electricity): tariff £71.47-£153.52/MWh, net margin £-76.73 -- **net-negative**
- C9 (electricity): tariff £56.11-£161.00/MWh, net margin £45.06

**Portfolio Health**

- Capital cost ratio: 7.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.895, average bill shock 11.3%, bad debt provision £413.63, avg complaint probability 3.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-161.03 vs. naked (unhedged) net margin: £4,328.78
- hedging cost £4,489.81 vs. a fully unhedged book (commodity-only: actual net £-161.03 vs. naked net £4,328.78)
  - C1: actual £27.59 vs. naked £207.84 -- hedging cost £180.25
  - C1g: actual £100.96 vs. naked £220.80 -- hedging cost £119.84
  - C2: actual £-250.81 vs. naked £213.72 -- hedging cost £464.53
  - C2g: actual £11.82 vs. naked £66.36 -- hedging cost £54.54
  - C3: actual £78.56 vs. naked £213.67 -- hedging cost £135.10
  - C3g: actual £34.13 vs. naked £54.35 -- hedging cost £20.22
  - C4: actual £56.82 vs. naked £374.63 -- hedging cost £317.81
  - C4g: actual £100.33 vs. naked £308.91 -- hedging cost £208.58
  - C5: actual £66.51 vs. naked £845.36 -- hedging cost £778.85
  - C6: actual £-633.22 vs. naked £69.07 -- hedging cost £702.29
  - C7: actual £117.02 vs. naked £706.69 -- hedging cost £589.66
  - C8: actual £-184.56 vs. naked £418.48 -- hedging cost £603.04
  - C9: actual £313.82 vs. naked £628.91 -- hedging cost £315.09

**Year narrative:** 2018 produced a net gain of £26.24 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 34 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £567.19 (gross £3,350.22, capital £138.66)
  - Electricity: gross £3,096.10, capital £133.04, net £318.70
  - Gas: gross £254.12, capital £5.63, net £248.49
- Treasury at year end: £29,090.39
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.90 (avg 0.90), C4 0.85 (avg 0.85), C4g 0.90 (avg 0.90), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2019-01-02 period 34, net margin £-0.21

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2019): £791.33
  - By billing account: C1 £322.54, C2 £209.24, C3 £319.97, C4 £1,208.08, C5 £1,218.57, C6 £724.01, C7 £940.18, C8 £904.05, C9 £1,275.30
- Bill shock events (>=20%): 33 -- C1 2019-04-30 (21%); C5 2019-01-31 (22%); C5 2019-02-28 (21%); C5 2019-06-30 (26%); C5 2019-10-31 (43%); C5 2019-11-30 (35%); C7 2019-01-31 (32%); C7 2019-02-28 (26%); C7 2019-05-31 (24%); C7 2019-06-30 (35%); C7 2019-10-31 (71%); C7 2019-11-30 (45%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (42%); C6 2019-11-30 (26%); C8 2019-01-31 (26%); C8 2019-02-28 (28%); C8 2019-04-30 (27%); C8 2019-06-30 (39%); C8 2019-07-31 (35%); C8 2019-09-30 (59%); C8 2019-10-31 (86%); C8 2019-11-30 (37%); C3 2019-04-30 (20%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (36%); C9 2019-07-31 (43%); C9 2019-09-30 (50%); C9 2019-10-31 (74%); C9 2019-11-30 (37%); C4g 2019-10-31 (36%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C3 23%, C5 38%, C6 32%, C7 38%, C8 38%, C9 35%

**Pricing & Margin**

- C1 (electricity): tariff £81.35-£105.88/MWh, net margin £27.56
- C1g (gas): tariff £15.80-£32.42/MWh, net margin £100.66
- C2 (electricity): tariff £91.39-£105.68/MWh, net margin £-23.13 -- **net-negative**
- C2g (gas): tariff £21.68-£26.69/MWh, net margin £19.30
- C3 (electricity): tariff £76.30-£107.47/MWh, net margin £28.16
- C3g (gas): tariff £16.13-£23.66/MWh, net margin £34.43
- C4 (electricity): tariff £78.44-£104.96/MWh, net margin £49.10
- C4g (gas): tariff £13.59-£30.82/MWh, net margin £94.10
- C5 (electricity): tariff £81.89-£103.04/MWh, net margin £66.76
- C6 (electricity): tariff £96.91-£105.56/MWh, net margin £-133.42 -- **net-negative**
- C7 (electricity): tariff £63.70-£157.09/MWh, net margin £116.90
- C8 (electricity): tariff £75.80-£153.52/MWh, net margin £-8.68 -- **net-negative**
- C9 (electricity): tariff £61.03-£161.00/MWh, net margin £195.46

**Portfolio Health**

- Capital cost ratio: 4.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.892, average bill shock 12.6%, bad debt provision £426.97, avg complaint probability 3.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £588.83 vs. naked (unhedged) net margin: £4,751.20
- hedging cost £4,162.37 vs. a fully unhedged book (commodity-only: actual net £588.83 vs. naked net £4,751.20)
  - C1: actual £7.19 vs. naked £143.55 -- hedging cost £136.35
  - C1g: actual £31.84 vs. naked £73.75 -- hedging cost £41.92
  - C2: actual £64.09 vs. naked £473.61 -- hedging cost £409.52
  - C2g: actual £20.10 vs. naked £149.81 -- hedging cost £129.71
  - C3: actual £-20.77 vs. naked £168.70 -- hedging cost £189.47
  - C3g: actual £37.09 vs. naked £94.66 -- hedging cost £57.58
  - C4: actual £31.37 vs. naked £304.07 -- hedging cost £272.70
  - C4g: actual £82.61 vs. naked £109.87 -- hedging cost £27.25
  - C5: actual £31.28 vs. naked £602.33 -- hedging cost £571.06
  - C6: actual £122.19 vs. naked £947.20 -- hedging cost £825.02
  - C7: actual £43.47 vs. naked £477.28 -- hedging cost £433.81
  - C8: actual £99.06 vs. naked £687.91 -- hedging cost £588.85
  - C9: actual £39.31 vs. naked £518.45 -- hedging cost £479.14

**Year narrative:** 2019 produced a net gain of £567.19 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £154.60 (gross £2,813.84, capital £127.79)
  - Electricity: gross £2,658.57, capital £120.44, net £6.68
  - Gas: gross £155.27, capital £7.35, net £147.92
- Treasury at year end: £29,575.28
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2020-03-04 period 37, net margin £-0.98

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C3
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £837.25
  - By billing account: C1 £313.57, C2 £310.29, C3 £280.27, C4 £1,161.94, C5 £1,358.04, C6 £846.88, C7 £1,014.17, C8 £982.10, C9 £1,268.01
- Bill shock events (>=20%): 27 -- C1g 2020-01-31 (33%); C5 2020-04-30 (29%); C5 2020-10-31 (37%); C5 2020-12-31 (26%); C7 2020-04-30 (35%); C7 2020-05-31 (21%); C7 2020-06-30 (27%); C7 2020-10-31 (60%); C7 2020-11-30 (23%); C7 2020-12-31 (35%); C2 2020-04-30 (32%); C2g 2020-04-30 (22%); C6 2020-04-30 (43%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (46%); C8 2020-05-31 (25%); C8 2020-06-30 (32%); C8 2020-09-30 (53%); C8 2020-10-31 (65%); C8 2020-12-31 (42%); C9 2020-04-30 (28%); C9 2020-05-31 (25%); C9 2020-06-30 (35%); C9 2020-09-30 (44%); C9 2020-10-31 (50%); C9 2020-12-31 (36%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 26%, C4 20%, C5 35%, C6 32%, C7 35%, C8 38%, C9 41%

**Pricing & Margin**

- C1 (electricity): tariff £81.35-£96.94/MWh, net margin £6.84
- C1g (gas): tariff £15.80-£18.58/MWh, net margin £31.85
- C2 (electricity): tariff £68.36-£105.68/MWh, net margin £-39.85 -- **net-negative**
- C2g (gas): tariff £14.22-£21.68/MWh, net margin £44.76
- C3 (electricity): tariff £76.30/MWh, net margin £-8.38 -- **net-negative**
- C3g (gas): tariff £16.13/MWh, net margin £19.58
- C4 (electricity): tariff £78.44-£83.20/MWh, net margin £32.06
- C4g (gas): tariff £9.07-£13.59/MWh, net margin £51.73
- C5 (electricity): tariff £81.89-£95.70/MWh, net margin £28.14
- C6 (electricity): tariff £70.27-£105.56/MWh, net margin £-117.11 -- **net-negative**
- C7 (electricity): tariff £63.70-£144.68/MWh, net margin £43.78
- C8 (electricity): tariff £56.65-£144.70/MWh, net margin £25.12
- C9 (electricity): tariff £50.46-£116.51/MWh, net margin £36.06

**Portfolio Health**

- Capital cost ratio: 4.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 144, average clarity 0.889, average bill shock 11.6%, bad debt provision £326.61, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-750.76 vs. naked (unhedged) net margin: £-1,852.76
- hedging added £1,102.00 vs. a fully unhedged book (commodity-only: actual net £-750.76 vs. naked net £-1,852.76)
  - C1: actual £-31.04 vs. naked £-138.26 -- hedging added £107.22
  - C1g: actual £-18.42 vs. naked £-299.71 -- hedging added £281.29
  - C2: actual £-84.68 vs. naked £154.87 -- hedging cost £239.55
  - C2g: actual £46.64 vs. naked £37.94 -- hedging added £8.69
  - C4: actual £1.16 vs. naked £17.30 -- hedging cost £16.14
  - C4g: actual £-82.13 vs. naked £-364.57 -- hedging added £282.44
  - C5: actual £-201.63 vs. naked £-880.87 -- hedging added £679.24
  - C6: actual £-260.76 vs. naked £-43.64 -- hedging cost £217.12
  - C7: actual £-75.22 vs. naked £-432.01 -- hedging added £356.79
  - C8: actual £-44.41 vs. naked £151.07 -- hedging cost £195.48
  - C9: actual £-0.25 vs. naked £-54.87 -- hedging added £54.63

**Year narrative:** 2020 produced a net gain of £154.60 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 27 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-1,535.81 (gross £1,245.29, capital £355.42)
  - Electricity: gross £1,318.75, capital £347.34, net £-1,454.27
  - Gas: gross £-73.46, capital £8.08, net £-81.54
- Treasury at year end: £28,713.76
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C4 0.85 (avg 0.85), C4g 0.95 (avg 0.95), C6 0.85 (avg 0.85), C7 0.95 (avg 0.95), C8 0.85 (avg 0.85), C9 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 28
  - 2021-03-31: treasury £28,659.91, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2021-04-30: treasury £28,594.86, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2021-05-30: treasury £28,553.31, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2021-06-29: treasury £28,521.75, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2021-07-29: treasury £28,488.80, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2021-08-28: treasury £28,454.68, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2021-09-27: treasury £28,405.73, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2021-10-27: treasury £28,351.57, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2021-11-26: treasury £28,273.95, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2021-12-26: treasury £28,165.05, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2021-04-25: treasury £27,880.04, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2021-05-25: treasury £27,856.29, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2021-06-24: treasury £27,843.71, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2021-07-24: treasury £27,831.05, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2021-08-23: treasury £27,817.27, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2021-09-22: treasury £27,798.37, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2021-10-22: treasury £27,773.40, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2021-11-21: treasury £27,732.71, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2021-12-21: treasury £27,663.84, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2021-07-20: treasury £27,486.44, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2021-08-19: treasury £27,478.91, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2021-09-18: treasury £27,469.90, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2021-10-18: treasury £27,458.22, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2021-11-17: treasury £27,445.27, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2021-12-17: treasury £27,426.32, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2021-10-15: treasury £27,369.27, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2021-11-14: treasury £27,381.20, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2021-12-14: treasury £27,391.16, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.62
- Worst single period: C5 on 2021-01-08 period 39, net margin £-2.12

**Customer Book**

- Active accounts: 11 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2021): £726.21
  - By billing account: C1 £250.84, C2 £201.52, C3 £278.37, C4 £990.21, C5 £1,287.01, C6 £612.71, C7 £991.43, C8 £768.87, C9 £1,154.90
- Bill shock events (>=20%): 30 -- C5 2021-05-31 (22%); C5 2021-06-30 (32%); C5 2021-10-31 (29%); C5 2021-11-30 (50%); C7 2021-01-31 (22%); C7 2021-05-31 (30%); C7 2021-06-30 (47%); C7 2021-10-31 (55%); C7 2021-11-30 (65%); C2g 2021-04-30 (30%); C6 2021-04-30 (29%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-04-30 (22%); C8 2021-05-31 (28%); C8 2021-06-30 (61%); C8 2021-09-30 (24%); C8 2021-10-31 (67%); C8 2021-11-30 (82%); C9 2021-02-28 (22%); C9 2021-05-31 (24%); C9 2021-06-30 (50%); C9 2021-08-31 (21%); C9 2021-09-30 (22%); C9 2021-10-31 (62%); C9 2021-11-30 (49%); C9 2021-12-31 (24%); C4 2021-10-31 (139%); C4g 2021-10-31 (203%)
- Churn risk (accounts renewing in 2021): 6 at risk (≥20% churn prob): C2 20%, C5 35%, C6 38%, C7 35%, C8 41%, C9 35%

**Pricing & Margin**

- C1 (electricity): tariff £96.94/MWh, net margin £-30.55 -- **net-negative**
- C1g (gas): tariff £18.58/MWh, net margin £-18.40 -- **net-negative**
- C2 (electricity): tariff £68.36-£115.53/MWh, net margin £-195.44 -- **net-negative**
- C2g (gas): tariff £14.22-£25.08/MWh, net margin £23.05
- C4 (electricity): tariff £83.20-£293.81/MWh, net margin £22.78
- C4g (gas): tariff £9.07-£58.76/MWh, net margin £-86.19 -- **net-negative**
- C5 (electricity): tariff £95.70/MWh, net margin £-197.21 -- **net-negative**
- C6 (electricity): tariff £70.27-£121.68/MWh, net margin £-602.83 -- **net-negative**
- C7 (electricity): tariff £75.78-£438.93/MWh, net margin £-78.00 -- **net-negative**
- C8 (electricity): tariff £56.65-£163.90/MWh, net margin £-289.68 -- **net-negative**
- C9 (electricity): tariff £50.46-£181.95/MWh, net margin £-83.33 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 28.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 132, average clarity 0.877, average bill shock 15.5%, bad debt provision £340.57, avg complaint probability 4.0%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,522.59 vs. naked (unhedged) net margin: £-6,085.95
- hedging added £4,563.36 vs. a fully unhedged book (commodity-only: actual net £-1,522.59 vs. naked net £-6,085.95)
  - C2: actual £-237.30 vs. naked £-328.56 -- hedging added £91.26
  - C2g: actual £13.92 vs. naked £-542.89 -- hedging added £556.81
  - C4: actual £128.87 vs. naked £289.78 -- hedging cost £160.91
  - C4g: actual £-81.16 vs. naked £-1,080.31 -- hedging added £999.15
  - C6: actual £-749.21 vs. naked £-2,412.79 -- hedging added £1,663.57
  - C7: actual £-53.93 vs. naked £175.10 -- hedging cost £229.03
  - C8: actual £-418.50 vs. naked £-1,106.63 -- hedging added £688.13
  - C9: actual £-125.27 vs. naked £-1,079.66 -- hedging added £954.39

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-1,535.81 across 11 accounts. The risk committee intervened 28 time(s), raising hedge fractions in response to elevated VaR. 30 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £-1,506.24 (gross £261.20, capital £343.73)
  - Electricity: gross £424.19, capital £339.08, net £-1,338.60
  - Gas: gross £-162.99, capital £4.65, net £-167.64
- Treasury at year end: £26,806.68
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 0.95 (avg 0.95), C4g 1.00 (avg 1.00), C6 0.95 (avg 0.95), C7 1.00 (avg 1.00), C8 0.95 (avg 0.95), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 43
  - 2022-01-25: treasury £28,077.69, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2022-02-24: treasury £28,009.59, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2022-03-26: treasury £27,922.69, C2->0.95, C6->0.95, VaR (current £3,147.30 / stressed £1,246.77) ratio 2.52
  - 2022-01-20: treasury £27,612.42, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2022-02-19: treasury £27,564.17, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2022-03-21: treasury £27,504.84, C2->0.95, C6->0.95, C8->0.95, VaR (current £3,529.95 / stressed £1,338.07) ratio 2.64
  - 2022-01-16: treasury £27,411.24, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2022-02-15: treasury £27,401.89, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2022-03-17: treasury £27,392.23, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2022-04-16: treasury £27,382.64, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2022-05-16: treasury £27,376.27, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2022-06-15: treasury £27,371.27, C2->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £3,576.50 / stressed £1,337.53) ratio 2.67
  - 2022-01-13: treasury £27,403.74, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2022-02-12: treasury £27,418.26, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2022-03-14: treasury £27,430.45, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2022-04-13: treasury £27,442.49, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2022-05-13: treasury £27,458.66, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2022-06-12: treasury £27,474.96, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2022-07-12: treasury £27,485.69, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2022-08-11: treasury £27,492.34, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2022-09-10: treasury £27,490.78, C2->0.95, C4->0.95, C6->0.95, C8->0.95, C9->1.00, VaR (current £4,055.94 / stressed £1,473.98) ratio 2.75
  - 2022-01-01: treasury £27,411.53, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-01-31: treasury £27,431.41, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-03-02: treasury £27,444.64, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-04-01: treasury £27,451.75, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-05-01: treasury £27,443.46, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-05-31: treasury £27,431.63, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-06-30: treasury £27,415.26, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-07-30: treasury £27,395.06, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-08-29: treasury £27,370.81, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-09-28: treasury £27,352.90, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-10-28: treasury £27,344.82, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-11-27: treasury £27,345.52, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-12-27: treasury £27,357.89, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-04-27: treasury £27,283.54, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-05-27: treasury £27,240.48, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-06-26: treasury £27,205.72, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-07-26: treasury £27,178.10, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-08-25: treasury £27,148.65, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-09-24: treasury £27,108.90, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-10-24: treasury £27,054.90, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-11-23: treasury £26,993.34, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2022-12-23: treasury £26,830.03, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.74
- Worst single period: C6 on 2022-01-24 period 34, net margin £-2.57

**Customer Book**

- Active accounts: 9 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2022): £509.83
  - By billing account: C1 £265.27, C2 £119.33, C2_2 £-340.97, C3 £306.78, C4 £615.87, C5 £1,072.10, C6 £420.12, C7 £913.47, C8 £665.64, C9 £1,060.75
- Bill shock events (>=20%): 36 -- C7 2022-01-31 (161%); C7 2022-02-28 (27%); C7 2022-04-30 (23%); C7 2022-05-31 (37%); C7 2022-06-30 (28%); C7 2022-09-30 (36%); C7 2022-11-30 (66%); C7 2022-12-31 (54%); C6 2022-04-30 (79%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-04-30 (77%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (86%); C8 2022-11-30 (73%); C8 2022-12-31 (58%); C9 2022-04-30 (21%); C9 2022-05-31 (30%); C9 2022-06-30 (30%); C9 2022-07-31 (23%); C9 2022-09-30 (50%); C9 2022-10-31 (31%); C9 2022-11-30 (46%); C9 2022-12-31 (53%); C4g 2022-10-31 (154%); C2_2 2022-04-30 (1717%); C2_2 2022-05-31 (39%); C2_2 2022-06-30 (33%); C2_2 2022-09-30 (77%); C2_2 2022-11-30 (65%); C2_2 2022-12-31 (57%)
- Churn risk (accounts renewing in 2022): 5 at risk (≥20% churn prob): C4 23%, C6 32%, C7 35%, C8 35%, C9 38%

**Pricing & Margin**

- C2 (electricity): tariff £115.53/MWh, net margin £-67.43 -- **net-negative**
- C2_2 (electricity): tariff £265.84/MWh, net margin £-554.35 -- **net-negative**
- C2g (gas): tariff £25.08/MWh, net margin £-1.48 -- **net-negative**
- C4 (electricity): tariff £293.81-£322.32/MWh, net margin £-80.15 -- **net-negative**
- C4g (gas): tariff £58.76-£174.40/MWh, net margin £-166.16 -- **net-negative**
- C6 (electricity): tariff £121.68-£346.48/MWh, net margin £-549.98 -- **net-negative**
- C7 (electricity): tariff £207.92-£438.93/MWh, net margin £-57.59 -- **net-negative**
- C8 (electricity): tariff £85.85-£519.30/MWh, net margin £-81.10 -- **net-negative**
- C9 (electricity): tariff £95.31-£355.90/MWh, net margin £52.00

**Portfolio Health**

- Capital cost ratio: 131.6% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £28,713.75 -> £25,149.35 (12.4%)
- Bills issued: 88, average clarity 0.808, average bill shock 43.8%, bad debt provision £494.54, avg complaint probability 5.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-3,276.18 vs. naked (unhedged) net margin: £6,742.49
- hedging cost £10,018.67 vs. a fully unhedged book (commodity-only: actual net £-3,276.18 vs. naked net £6,742.49)
  - C2_2: actual £-896.84 vs. naked £418.88 -- hedging cost £1,315.73
  - C4: actual £-713.67 vs. naked £1,164.22 -- hedging cost £1,877.89
  - C4g: actual £-395.92 vs. naked £2,469.04 -- hedging cost £2,864.96
  - C6: actual £-488.59 vs. naked £-380.23 -- hedging cost £108.35
  - C7: actual £-1,070.53 vs. naked £1,441.45 -- hedging cost £2,511.97
  - C8: actual £125.37 vs. naked £1,203.70 -- hedging cost £1,078.33
  - C9: actual £163.99 vs. naked £425.43 -- hedging cost £261.44

**Year narrative:** 2022 (flagged crisis year) produced a net loss of £-1,506.24 across 9 accounts. The risk committee intervened 43 time(s), raising hedge fractions in response to elevated VaR. 36 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £-1,175.08 (gross £1,685.52, capital £466.66)
  - Electricity: gross £1,939.50, capital £460.86, net £-915.30
  - Gas: gross £-253.97, capital £5.81, net £-259.78
- Treasury at year end: £24,613.54
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.90 (avg 0.90), C6 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 20
  - 2023-01-22: treasury £26,716.68, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2023-02-21: treasury £26,601.01, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2023-03-23: treasury £26,483.54, C2->0.95, C4->0.95, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £4,218.67 / stressed £1,512.71) ratio 2.79
  - 2023-06-03: treasury £24,622.03, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-07-03: treasury £24,562.56, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-08-02: treasury £24,504.66, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-09-01: treasury £24,445.64, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-10-01: treasury £24,381.53, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-10-31: treasury £24,301.99, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-11-30: treasury £24,193.51, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-03-31: treasury £24,084.93, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-04-30: treasury £24,168.40, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-05-30: treasury £24,216.66, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-06-29: treasury £24,243.93, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-07-29: treasury £24,271.09, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-08-28: treasury £24,297.13, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-09-27: treasury £24,327.18, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-10-27: treasury £24,381.46, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-11-26: treasury £24,477.45, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
  - 2023-12-26: treasury £24,593.75, C2->0.95, VaR (current £2,641.82 / stressed £1,213.86) ratio 2.18
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.27
- Worst single period: C4g on 2023-01-01 period 1, net margin £-1.08

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2023): £512.23
  - By billing account: C1 £256.72, C2 £122.74, C2_2 £-16.94, C3 £289.51, C4 £55.08, C5 £1,152.20, C6 £801.59, C7 £350.59, C8 £965.13, C9 £1,145.69
- Bill shock events (>=20%): 28 -- C7 2023-05-31 (32%); C7 2023-06-30 (37%); C7 2023-10-31 (57%); C7 2023-11-30 (73%); C6 2023-04-30 (38%); C6 2023-05-31 (23%); C6 2023-06-30 (23%); C6 2023-10-31 (39%); C6 2023-11-30 (44%); C8 2023-04-30 (42%); C8 2023-05-31 (41%); C8 2023-06-30 (44%); C8 2023-10-31 (101%); C8 2023-11-30 (70%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (22%); C9 2023-10-31 (75%); C9 2023-11-30 (54%); C4 2023-10-31 (42%); C4g 2023-10-31 (70%); C2_2 2023-05-31 (42%); C2_2 2023-06-30 (42%); C2_2 2023-10-31 (96%); C2_2 2023-11-30 (67%)
- Churn risk (accounts renewing in 2023): 5 at risk (≥20% churn prob): C2_2 35%, C6 26%, C7 38%, C8 35%, C9 41%

**Pricing & Margin**

- C2_2 (electricity): tariff £265.84-£303.67/MWh, net margin £186.20
- C4 (electricity): tariff £144.64-£322.32/MWh, net margin £-525.24 -- **net-negative**
- C4g (gas): tariff £39.62-£174.40/MWh, net margin £-259.78 -- **net-negative**
- C6 (electricity): tariff £252.34-£346.48/MWh, net margin £15.63
- C7 (electricity): tariff £139.18-£396.94/MWh, net margin £-1,068.76 -- **net-negative**
- C8 (electricity): tariff £192.74-£519.30/MWh, net margin £341.61
- C9 (electricity): tariff £124.32-£355.90/MWh, net margin £135.26

**Portfolio Health**

- Capital cost ratio: 27.7% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £26,806.67 -> £24,084.41 (10.2%)
- Bills issued: 84, average clarity 0.815, average bill shock 19.8%, bad debt provision £554.57, avg complaint probability 5.1%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £2,223.32 vs. naked (unhedged) net margin: £6,103.72
- hedging cost £3,880.40 vs. a fully unhedged book (commodity-only: actual net £2,223.32 vs. naked net £6,103.72)
  - C2_2: actual £856.89 vs. naked £1,980.72 -- hedging cost £1,123.84
  - C4: actual £6.71 vs. naked £389.22 -- hedging cost £382.51
  - C4g: actual £154.27 vs. naked £53.35 -- hedging added £100.92
  - C6: actual £337.90 vs. naked £726.44 -- hedging cost £388.54
  - C7: actual £193.00 vs. naked £838.77 -- hedging cost £645.77
  - C8: actual £508.45 vs. naked £1,409.43 -- hedging cost £900.98
  - C9: actual £166.11 vs. naked £705.78 -- hedging cost £539.67

**Year narrative:** 2023 produced a net loss of £-1,175.08 across 7 accounts. The risk committee intervened 20 time(s), raising hedge fractions in response to elevated VaR. 28 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £1,033.29 (gross £3,638.82, capital £272.46)
  - Electricity: gross £3,506.74, capital £259.39, net £914.28
  - Gas: gross £132.08, capital £13.07, net £119.01
- Treasury at year end: £26,261.67
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C9 on 2024-12-12 period 41, net margin £-0.19

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2024): £604.12
  - By billing account: C1 £203.27, C2 £120.80, C2_2 £294.51, C3 £278.37, C4 £198.48, C5 £1,095.41, C6 £831.28, C7 £600.03, C8 £1,087.62, C9 £1,331.44
- Bill shock events (>=20%): 24 -- C7 2024-02-29 (27%); C7 2024-05-31 (38%); C7 2024-09-30 (36%); C7 2024-10-31 (39%); C7 2024-11-30 (50%); C8 2024-02-29 (23%); C8 2024-04-30 (49%); C8 2024-05-31 (50%); C8 2024-07-31 (27%); C8 2024-09-30 (77%); C8 2024-10-31 (36%); C8 2024-11-30 (63%); C9 2024-05-31 (50%); C9 2024-07-31 (35%); C9 2024-09-30 (57%); C9 2024-10-31 (23%); C9 2024-11-30 (48%); C2_2 2024-02-29 (23%); C2_2 2024-04-30 (58%); C2_2 2024-05-31 (49%); C2_2 2024-07-31 (26%); C2_2 2024-09-30 (68%); C2_2 2024-10-31 (36%); C2_2 2024-11-30 (59%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 38%, C4 23%, C6 38%, C7 35%, C8 41%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £132.59-£303.67/MWh, net margin £281.69
- C4 (electricity): tariff £144.64/MWh, net margin £-0.99 -- **net-negative**
- C4g (gas): tariff £39.62/MWh, net margin £119.01
- C6 (electricity): tariff £252.34/MWh, net margin £142.03
- C7 (electricity): tariff £134.87-£265.70/MWh, net margin £194.73
- C8 (electricity): tariff £107.30-£367.97/MWh, net margin £260.01
- C9 (electricity): tariff £94.93-£237.33/MWh, net margin £36.81

**Portfolio Health**

- Capital cost ratio: 7.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 69, average clarity 0.807, average bill shock 20.0%, bad debt provision £303.17, avg complaint probability 5.2%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-86.04 vs. naked (unhedged) net margin: £756.85
- hedging cost £842.89 vs. a fully unhedged book (commodity-only: actual net £-86.04 vs. naked net £756.85)
  - C2_2: actual £-96.93 vs. naked £224.08 -- hedging cost £321.01
  - C7: actual £69.94 vs. naked £246.58 -- hedging cost £176.64
  - C8: actual £64.19 vs. naked £247.34 -- hedging cost £183.15
  - C9: actual £-123.25 vs. naked £38.86 -- hedging cost £162.11

**Year narrative:** 2024 produced a net gain of £1,033.29 across 7 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 24 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £-189.74 (gross £946.93, capital £104.49)
  - Electricity: gross £946.93, capital £104.49, net £-189.74
- Treasury at year end: £26,152.19
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C8 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C2_2 on 2025-01-08 period 36, net margin £-1.53

**Customer Book**

- Active accounts: 4 (C2_2, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 0, gas (dual-fuel): 0
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £578.33
  - By billing account: C1 £210.73, C2 £111.57, C2_2 £295.94, C3 £253.84, C4 £179.42, C5 £989.52, C6 £856.47, C7 £744.73, C8 £1,075.94, C9 £1,065.10
- Bill shock events (>=20%): 18 -- C7 2025-01-31 (24%); C7 2025-04-30 (37%); C7 2025-05-31 (23%); C7 2025-06-07 (80%); C8 2025-01-31 (39%); C8 2025-02-28 (24%); C8 2025-04-30 (24%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (33%); C9 2025-06-07 (72%); C2_2 2025-01-31 (38%); C2_2 2025-02-28 (24%); C2_2 2025-04-30 (24%); C2_2 2025-05-31 (37%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £132.59-£180.02/MWh, net margin £-134.09 -- **net-negative**
- C7 (electricity): tariff £134.87-£257.48/MWh, net margin £72.47
- C8 (electricity): tariff £107.30-£273.42/MWh, net margin £-62.68 -- **net-negative**
- C9 (electricity): tariff £94.93-£181.23/MWh, net margin £-65.44 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 11.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 24, average clarity 0.725, average bill shock 32.5%, bad debt provision £109.92, avg complaint probability 7.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-171.28 vs. naked (unhedged) net margin: £41.01
- hedging cost £212.29 vs. a fully unhedged book (commodity-only: actual net £-171.28 vs. naked net £41.01)
  - C2_2: actual £-83.68 vs. naked £72.27 -- hedging cost £155.95
  - C8: actual £-87.61 vs. naked £-31.26 -- hedging cost £56.34

**Year narrative:** 2025 produced a net loss of £-189.74 across 4 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 18 customer(s) experienced a bill shock of >=20%.
