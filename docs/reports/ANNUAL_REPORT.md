# Annual Report — The Synthetic Enterprise

## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £463,165.53
- Final treasury: £465,105.22
  (£1,939.69 net change)
- Customer bills (all-in): £1,493,274.83
  VAT remitted to HMRC: (£233,639.11) | Revenue (ex-VAT): £1,259,635.72
  Non-commodity pass-through: (£377,164.78)
- Gross margin: £235,160.09
- Capital costs: £9,239.95
- Net margin: £225,920.14
- Capital cost ratio: 3.9% of gross
- Net margin as % of revenue: 17.9%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 236
- Bills issued: 1165, average clarity 0.866,
  service quality score 0.917
- Enterprise value (CLV sum across 11 billing accounts): £309,282.17
- Cost to serve (whole portfolio): £14,734.93, net margin after cost to serve: £211,185.20
- Hedge effectiveness (whole window): hedging cost £311,373.61 vs. a fully unhedged book (commodity-only: actual net £1,939.69 vs. naked net £313,313.30)

- **2021** (crisis year): net margin £-1,534.25, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £-1,473.03, 0 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £235,160.09, capital £9,239.95, net £225,920.14. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 4.1% (commodity basis, comparable to old model) / 3.9% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £-1,534.25 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 17.9%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £225,920.14
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £313,313.30
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £311,373.61 vs. a fully unhedged book (commodity-only: actual net £1,939.69 vs. naked net £313,313.30)
- **Best hedging decision of the run**: C6, term starting
  2021-03-31 (hedge fraction 0.85) -- hedging
  protected £1,663.57 vs. going naked.
- **Worst hedging decision of the run**: C_IC1, term
  starting 2019-01-01 (hedge fraction 1.00) --
  over-hedging cost £99,883.50 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|
| 2016 | £-419.73 | £-333.14 | £80.49 | £-672.38 |
| 2017 | £-51,951.79 | £-353.25 | £138.51 | £-52,166.53 |
| 2018 | £33,736.11 | £35.85 | £179.58 | £33,951.53 |
| 2019 | £17,956.28 | £325.75 | £248.49 | £18,530.53 |
| 2020 | £5,165.52 | £92.13 | £147.92 | £5,405.56 |
| 2021 | £-797.34 | £-655.37 | £-81.54 | £-1,534.25 |
| 2022 | £-548.18 | £-757.21 | £-167.64 | £-1,473.03 |
| 2023 | £-36.35 | £-573.21 | £-259.78 | £-869.33 |
| 2024 | £115.98 | £720.14 | £119.01 | £955.12 |
| 2025 | £0.00 | £-187.54 | £0.00 | £-187.54 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **43** renewals.  Lost (churned): **7** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6, C_IC1

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
| C_IC1 | 2020-12-31 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.9643 |
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

- **Average absolute error:** 132.7%
- **Average signed error:** +31.2% (over-estimates vs SIM)
- **Renewal events with estimates:** 50

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +87.9% | 91.8% |
| 2017 | 3 | -55.2% | 55.2% |
| 2018 | 3 | -68.2% | 68.2% |
| 2019 | 3 | -100.0% | 100.0% |
| 2020 | 10 | -54.1% | 88.4% |
| 2021 | 8 | +343.7% | 349.0% |
| 2022 | 6 | +120.5% | 167.9% |
| 2023 | 6 | -63.4% | 70.1% |
| 2024 | 6 | -84.6% | 84.6% |
| 2025 | 2 | -39.6% | 39.6% |

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
| 2017 | 14 | 17.1% | 35.5% |
| 2018 | 14 | 15.4% | 40.4% |
| 2019 | 14 | 12.9% | 23.3% |
| 2020 | 14 | 18.4% | 32.0% |
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
| 2018 | 3 | 0.68× | 0.78× |
| 2019 | 3 | 1.00× | 1.00× |
| 2020 | 10 | 0.88× | 1.71× |
| 2021 | 8 | 3.49× ⚠ | 18.00× |
| 2022 | 6 | 1.68× | 4.59× |
| 2023 | 6 | 0.70× | 1.00× |
| 2024 | 6 | 0.85× | 1.00× |
| 2025 | 2 | 0.40× | 0.41× |

## Demand Estimation Accuracy (Phase 23a/25a)

Company EAC estimate (from prior-year billing records) vs actual settled kWh.
Phase 25a: true_eac_kwh uses mean annual settled consumption (not declared EAC),
fixing the misleading ~100% error for EV customers (C2/C4: declared 3500/5500 kWh,
actual ~6820 kWh/year with EV charging). Near-zero error after first term confirms
company billing estimation correctly tracks actual consumption.

| Year | Renewals | Mean Abs Error | Max Abs Error |
|------|----------|----------------|--------------|
| 2016 | 3 | 21.0% | 34.3% |
| 2017 | 9 | 33.0% | 103.8% |
| 2018 | 10 | 30.2% | 103.8% |
| 2019 | 10 | 30.3% | 104.3% |
| 2020 | 11 | 28.0% | 104.9% |
| 2021 | 8 | 32.8% | 104.3% |
| 2022 | 6 | 34.3% | 103.8% |
| 2023 | 6 | 48.5% | 190.1% |
| 2024 | 6 | 48.2% | 186.8% |
| 2025 | 2 | 99.7% | 197.5% |

**71** of **71** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **8** (7 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.14, company est=0.00 |
| 2020-12-31 | CHURN | C_IC1 | SIM p=0.35, company est=0.95 |
| 2021-12-30 | CHURN | C1 | SIM p=0.17, company est=0.95 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.95 |
| 2022-03-31 | CHURN | C2 | SIM p=0.17, company est=0.95 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.00 |
| 2024-09-29 | CHURN | C4 | SIM p=0.23, company est=0.11 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 2 accounts | 0 active | yes |
| 2021-12-31 | 4 accounts | 0 active | yes |
| 2022-12-31 | 5 accounts | 1 active | yes |
| 2023-12-31 | 5 accounts | 1 active | yes |
| 2024-12-31 | 7 accounts | 1 active | yes |
| 2025-12-31 | 7 accounts | 1 active | yes |

## Policy Costs — RO + CfD Levies (Phase 21a)

Electricity policy costs deducted from net_margin_gbp each year. 
CfD levy was NEGATIVE in 2022 (crisis rebate from LCCC) — this appears 
as a positive contribution to that year's margin.

| Year | RO levy £ | CfD levy £ | Total policy cost £ | Note |
|------|-----------|------------|---------------------|------|
| 2016 | 1,108 | 7 | 1,115 |  |
| 2017 | 36,556 | 2,713 | 39,269 |  |
| 2018 | 43,779 | 6,757 | 50,536 |  |
| 2019 | 48,966 | 8,491 | 57,457 |  |
| 2020 | 47,717 | 7,077 | 54,794 |  |
| 2021 | 2,286 | 140 | 2,426 |  |
| 2022 | 1,768 | -344 | 1,424 | ⬇ CfD REBATE |
| 2023 | 1,931 | 463 | 2,394 |  |
| 2024 | 1,707 | 626 | 2,333 |  |
| 2025 | 767 | 265 | 1,032 |  |
| **Total** | **186,585** | **26,195** | **212,780** | |

Total policy cost: £212,780 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,842 | 40,643 | 33.6% | £8,560.13 | £8,914.34 | £210.62/MWh | £111.15/MWh | +3.0% |
| C8 | 106,723 | 46,761 | 43.8% | £9,697.47 | £6,532.69 | £207.38/MWh | £108.95/MWh | +10.0% |
| C9 | 109,388 | 46,156 | 42.2% | £7,722.53 | £5,546.12 | £167.31/MWh | £87.71/MWh | +8.7% |

Total HH revenue: £46,973.28 vs flat equivalent £43,923.85 (+6.9% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 20 | 104% | C8 (2016-10-31) |
| 2017 | 33 | 84% | C8 (2017-11-30) |
| 2018 | 41 | 55% | C8 (2018-10-31) |
| 2019 | 40 | 86% | C8 (2019-10-31) |
| 2020 | 34 | 66% | C_IC1 (2020-10-31) |
| 2021 | 30 | 203% | C4g (2021-10-31) |
| 2022 | 36 | 1717% | C2_2 (2022-04-30) |
| 2023 | 28 | 100% | C8 (2023-10-31) |
| 2024 | 24 | 77% | C8 (2024-09-30) |
| 2025 | 18 | 80% | C7 (2025-06-07) |

Total: **304** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1717% | no |
| 2021-10-31 | C4g | +203% | no |
| 2022-01-31 | C7 | +161% | no |
| 2022-10-31 | C4g | +154% | no |
| 2021-10-31 | C4 | +139% | yes |
| 2016-10-31 | C8 | +104% | no |
| 2023-10-31 | C8 | +100% | no |
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
| Offers made | 23 |
| Retained | 19 (83%) |
| Churned despite offer | 4 |
| Total offer cost (foregone margin) | £64,954.86 |
| Margin saved (retained customers' terms) | £217,755.72 |
| Wasted offer cost (churned anyway) | £15979.33 |
| **Net ROI of retention strategy** | **£152,800.85** |
| Acquisition cost avoided (retained customers) | £4,850.00 |
| **Full economic ROI (margin + acq savings)** | **£157,650.85** |

Missed opportunities (churns with no offer): **3** (£1,419.55 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 3 (£1,419.55 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2016 | 1 | 1 | £52.36 | £656.81 | £604.45 | £0.00 |
| 2017 | 4 | 4 | £186.74 | £1983.78 | £1797.04 | £0.00 |
| 2018 | 2 | 2 | £16490.83 | £81421.88 | £64931.04 | £0.00 |
| 2019 | 1 | 1 | £17358.30 | £61216.30 | £43858.00 | £0.00 |
| 2020 | 2 | 1 | £28314.36 | £63755.95 | £35441.59 | £162.71 |
| 2021 | 8 | 6 | £1245.36 | £3814.69 | £2569.33 | £0.00 |
| 2022 | 4 | 3 | £1169.58 | £3778.83 | £2609.25 | £0.00 |
| 2023 | 1 | 1 | £137.33 | £1127.48 | £990.16 | £0.00 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £1256.84 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2016-12-31 | C5 | 0.31 | 3% | £52.36 | £656.81 | £400 | £604.45 | retained |
| 2017-04-01 | C2 | 0.66 | 5% | £37.55 | £364.36 | £150 | £326.81 | retained |
| 2017-04-01 | C6 | 0.63 | 5% | £97.30 | £910.11 | £400 | £812.82 | retained |
| 2017-04-01 | C8 | 0.42 | 3% | £33.45 | £462.01 | £150 | £428.55 | retained |
| 2017-10-01 | C4 | 0.31 | 3% | £18.44 | £247.30 | £150 | £228.86 | retained |
| 2018-01-01 | C_IC1 | 0.95 | 8% | £16448.30 | £80776.33 | £400 | £64328.04 | retained |
| 2018-07-01 | C9 | 0.35 | 3% | £42.53 | £645.54 | £150 | £603.01 | retained |
| 2019-01-01 | C_IC1 | 0.95 | 8% | £17358.30 | £61216.30 | £400 | £43858.00 | retained |
| 2020-01-01 | C_IC1 | 0.95 | 8% | £13084.30 | £63755.95 | £400 | £50671.65 | retained |
| 2020-12-31 | C_IC1 | 0.95 | 8% | £15230.07 | £70556.17 | £400 | £-15230.07 | churned_despite_offer |
| 2021-03-31 | C2 | 0.41 | 3% | £24.73 | £337.68 | £150 | £312.95 | retained |
| 2021-03-31 | C6 | 0.44 | 3% | £69.85 | £1029.45 | £400 | £959.60 | retained |
| 2021-03-31 | C8 | 0.32 | 3% | £39.31 | £494.42 | £150 | £455.11 | retained |
| 2021-06-30 | C9 | 0.52 | 5% | £79.31 | £591.82 | £150 | £512.51 | retained |
| 2021-09-30 | C4 | 0.95 | 8% | £168.12 | £497.74 | £150 | £329.62 | retained |
| 2021-12-30 | C1 | 0.95 | 8% | £90.37 | £273.86 | £150 | £-90.37 | churned_despite_offer |
| 2021-12-30 | C5 | 0.95 | 8% | £461.89 | £1513.94 | £400 | £-461.89 | churned_despite_offer |
| 2021-12-30 | C7 | 0.95 | 8% | £311.79 | £863.58 | £150 | £551.79 | retained |
| 2022-03-31 | C2 | 0.95 | 8% | £197.00 | £744.64 | £150 | £-197.00 | churned_despite_offer |
| 2022-03-31 | C6 | 0.95 | 8% | £517.10 | £1970.30 | £400 | £1453.20 | retained |
| 2022-03-31 | C8 | 0.95 | 8% | £319.79 | £1216.26 | £150 | £896.47 | retained |
| 2022-06-30 | C9 | 0.52 | 5% | £135.69 | £592.28 | £150 | £456.59 | retained |
| 2023-03-31 | C6 | 0.31 | 3% | £137.33 | £1127.48 | £400 | £990.16 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C5 | 2016-12-31 | 2021-12-30 | 60 | churned |
| C2 | 2017-04-01 | 2022-03-31 | 60 | churned |
| C6 | 2017-04-01 | 2024-03-30 | 84 | churned |
| C8 | 2017-04-01 | (window end) | 105 | active |
| C4 | 2017-10-01 | 2024-09-29 | 84 | churned |
| C_IC1 | 2018-01-01 | 2020-12-31 | 36 | churned |
| C9 | 2018-07-01 | (window end) | 90 | active |
| C1 | 2021-12-30 | 2021-12-30 | 0 | churned |
| C7 | 2021-12-30 | (window end) | 48 | active |

**Eventually churned (6/9)**: C5, C2, C6, C4, C_IC1, C1 — avg 54 months post-retention before final churn.
**Still active (3/9)**: C8, C9, C7 — survived to simulation end.

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £309,282.17 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £-323.16 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £-672.38 |
| 2017 | £-52,166.53 |
| 2018 | £33,951.53 |
| 2019 | £18,530.53 |
| 2020 | £5,405.56 |
| 2021 | £-1,534.25 |
| 2022 | £-1,473.03 |
| 2023 | £-869.33 | ← trailing
| 2024 | £955.12 | ← trailing
| 2025 | £-187.54 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £349.49 | — |
| C2 | £92.72 | — |
| C2_2 | — | £277.55 |
| C3 | £432.88 | — |
| C4 | £436.93 | £-787.45 |
| C5 | £1,714.10 | — |
| C6 | £1,237.03 | £117.01 |
| C7 | £1,379.32 | £-511.88 |
| C8 | £1,689.50 | £486.25 |
| C9 | £1,847.05 | £95.36 |
| C_IC1 | £299,679.59 | — |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £5.47 | — | — | — | — | £156.86 | — | £356.03 | — | — | — |
| 2017 | £-54.61 | £407.20 | — | £109.81 | £967.90 | £-18.73 | £1,140.90 | £111.10 | £1,003.76 | £690.16 | — |
| 2018 | £182.02 | £-84.80 | — | £261.74 | £1,038.95 | £727.51 | £336.41 | £618.90 | £577.67 | £948.50 | £301,583.53 |
| 2019 | £327.90 | £76.07 | — | £346.33 | £1,059.10 | £1,015.62 | £561.42 | £867.33 | £677.42 | £1,323.40 | £297,869.50 |
| 2020 | £304.60 | £211.86 | — | £257.98 | £883.65 | £1,194.23 | £708.23 | £945.18 | £864.75 | £1,277.44 | £229,563.64 |
| 2021 | £253.52 | £118.97 | — | £279.44 | £909.97 | £1,031.96 | £519.90 | £995.82 | £638.86 | £1,020.64 | £219,289.02 |
| 2022 | £223.82 | £63.10 | £-333.55 | £288.92 | £560.69 | £1,154.14 | £303.87 | £901.60 | £581.22 | £1,193.72 | £202,146.10 |
| 2023 | £237.78 | £60.28 | £-35.99 | £262.71 | £147.41 | £1,004.26 | £683.91 | £524.66 | £937.98 | £1,171.40 | £188,171.60 |
| 2024 | £201.59 | £54.84 | £249.98 | £229.21 | £260.96 | £1,023.76 | £803.86 | £760.83 | £1,098.72 | £1,223.24 | £178,372.75 |
| 2025 | £215.28 | £53.27 | £234.68 | £229.13 | £258.85 | £947.01 | £717.88 | £858.48 | £1,042.34 | £1,143.16 | £172,922.14 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £982.33, range £24.32–£8,055.78.

- C1: cost to serve £370.95, net margin after CTS £126.03
- C1g: cost to serve £37.18, net margin after CTS £208.04
- C2: cost to serve £407.39, net margin after CTS £59.99 — MARGIN_SQUEEZE (below 2% benchmark)
- C2_2: cost to serve £321.73, net margin after CTS £614.77
- C2g: cost to serve £42.95, net margin after CTS £29.30 — MARGIN_SQUEEZE (below 2% benchmark)
- C3: cost to serve £248.72, net margin after CTS £142.91
- C3g: cost to serve £24.32, net margin after CTS £114.73
- C4: cost to serve £607.59, net margin after CTS £703.53
- C4g: cost to serve £169.85, net margin after CTS £-153.31 — **NET_NEGATIVE** (tariff uplift needed: +1.9%)
- C5: cost to serve £818.75, net margin after CTS £1,501.87
- C6: cost to serve £1,173.96, net margin after CTS £1,552.64
- C7: cost to serve £868.62, net margin after CTS £2,017.76
- C8: cost to serve £830.04, net margin after CTS £2,389.31
- C9: cost to serve £757.09, net margin after CTS £2,652.44
- C_IC1: cost to serve £8,055.78, net margin after CTS £197,264.32

**Activity-Based Pricing Actions**

The following 1 customer(s) are loss-making after cost-to-serve and require immediate tariff review:
  - C4g: net margin after CTS £-153.31 on revenue £8,034.33 — raise tariff by ≥1.9% to break even
The following 2 customer(s) are profitable but below the 2% net-margin benchmark (MARGIN_SQUEEZE): C2, C2g

## Tariff Repricing Impact Assessment

Estimated churn risk at the break-even tariff level for each loss-making customer.
Active = current opportunity; churned = retrospective counterfactual.

| Customer | Fuel | Seg | Status | Uplift needed | Total loss | Churn @ B/E | Decision |
|----------|------|-----|--------|--------------|-----------|-------------|----------|
| C4g | gas | resi | active | +1.9% | £153.31 | 4% | Raise — churn risk manageable |

**Repriceable now (1)**: C4g — break-even churn risk below 40%. Uplift advised.

## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 37 recovery surcharge(s) at renewal based on prior-term losses (4 gas). Avg surcharge: 11.6%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C1 | electricity | 2016-12-31 | £-30.74 | £250.29 | +7.3% | £77.06/MWh | £91.87/MWh |
| C5 | electricity | 2016-12-31 | £-181.59 | £1,235.71 | +9.7% | £77.06/MWh | £94.02/MWh |
| C7 | electricity | 2016-12-31 | £-85.94 | £904.73 | +4.5% | £77.06/MWh | £89.63/MWh |
| C2 | electricity | 2017-04-01 | £-100.01 | £405.78 | +19.6% | £76.79/MWh | £105.31/MWh |
| C6 | electricity | 2017-04-01 | £-351.72 | £1,086.93 | +20.0% | £76.79/MWh | £101.86/MWh |
| C8 | electricity | 2017-04-01 | £-130.81 | £753.39 | +12.4% | £76.79/MWh | £92.57/MWh |
| C3 | electricity | 2017-07-01 | £-39.80 | £257.84 | +10.4% | £68.26/MWh | £78.17/MWh |
| C9 | electricity | 2017-07-01 | £-60.30 | £758.21 | +3.0% | £68.26/MWh | £71.10/MWh |
| C4 | electricity | 2017-10-01 | £-70.60 | £436.00 | +11.2% | £74.02/MWh | £86.16/MWh |
| C1 | electricity | 2017-12-31 | £-62.87 | £345.32 | +13.2% | £85.23/MWh | £101.02/MWh |
| C5 | electricity | 2017-12-31 | £-274.07 | £1,704.47 | +11.1% | £85.23/MWh | £98.98/MWh |
| C7 | electricity | 2017-12-31 | £-214.68 | £1,171.56 | +13.3% | £85.23/MWh | £98.30/MWh |
| C_IC1 | electricity | 2018-01-01 | £-51,699.07 | £159,800.80 | +20.0% | £87.27/MWh | £103.26/MWh |
| C2g | gas | 2018-04-01 | £-44.36 | £251.00 | +12.7% | £23.77/MWh | £26.69/MWh |
| C3 | electricity | 2018-07-01 | £-42.44 | £350.49 | +7.1% | £87.62/MWh | £107.83/MWh |
| C9 | electricity | 2018-07-01 | £-136.95 | £1,003.35 | +8.7% | £87.62/MWh | £109.39/MWh |
| C2 | electricity | 2019-04-01 | £-307.24 | £646.92 | +20.0% | £87.45/MWh | £105.87/MWh |
| C6 | electricity | 2019-04-01 | £-666.86 | £1,793.11 | +20.0% | £87.45/MWh | £105.79/MWh |
| C8 | electricity | 2019-04-01 | £-234.84 | £1,273.13 | +13.4% | £87.45/MWh | £99.69/MWh |
| C3 | electricity | 2020-06-30 | £-24.36 | £344.40 | +2.1% | £59.11/MWh | £65.63/MWh |
| C2 | electricity | 2021-03-31 | £-83.59 | £489.98 | +12.1% | £95.98/MWh | £115.26/MWh |
| C6 | electricity | 2021-03-31 | £-263.34 | £1,338.87 | +14.7% | £95.98/MWh | £121.97/MWh |
| C4g | gas | 2021-09-30 | £-82.13 | £199.63 | +20.0% | £45.77/MWh | £58.76/MWh |
| C1 | electricity | 2021-12-30 | £-30.93 | £364.37 | +3.5% | £259.05/MWh | £300.63/MWh |
| C5 | electricity | 2021-12-30 | £-201.63 | £1,790.04 | +6.3% | £259.05/MWh | £308.69/MWh |
| C7 | electricity | 2021-12-30 | £-75.47 | £1,320.11 | +0.7% | £259.05/MWh | £292.57/MWh |
| C2 | electricity | 2022-03-31 | £-239.23 | £822.01 | +20.0% | £265.84/MWh | £345.27/MWh |
| C6 | electricity | 2022-03-31 | £-743.91 | £2,275.35 | +20.0% | £265.84/MWh | £346.48/MWh |
| C8 | electricity | 2022-03-31 | £-418.49 | £1,386.21 | +20.0% | £265.84/MWh | £346.20/MWh |
| C9 | electricity | 2022-06-30 | £-125.27 | £1,501.61 | +3.3% | £210.77/MWh | £237.27/MWh |
| C4g | gas | 2022-09-30 | £-81.16 | £1,292.63 | +1.3% | £155.84/MWh | £174.40/MWh |
| C2_2 | electricity | 2023-03-31 | £-896.84 | £2,699.32 | +20.0% | £228.40/MWh | £298.25/MWh |
| C6 | electricity | 2023-03-31 | £-488.47 | £6,393.11 | +2.6% | £228.40/MWh | £248.09/MWh |
| C4 | electricity | 2023-09-30 | £-538.66 | £2,298.71 | +18.4% | £124.97/MWh | £143.61/MWh |
| C4g | gas | 2023-09-30 | £-395.92 | £3,836.83 | +5.3% | £35.28/MWh | £39.62/MWh |
| C7 | electricity | 2023-12-30 | £-786.24 | £3,350.75 | +18.5% | £147.77/MWh | £175.75/MWh |
| C2_2 | electricity | 2025-03-30 | £-92.10 | £1,385.30 | +1.6% | £168.56/MWh | £179.24/MWh |

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 91 renewal(s) (20 gas) based on recent portfolio-wide margin rates: 71 surcharge(s), 20 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | -14.2% | +11.1% | £77.06/MWh | £85.63/MWh |
| C1g | gas | 2016-12-31 | 15.2% | -3.6% | £18.35/MWh | £17.69/MWh |
| C5 | electricity | 2016-12-31 | -14.4% | +11.2% | £77.06/MWh | £85.71/MWh |
| C7 | electricity | 2016-12-31 | -14.6% | +11.3% | £77.06/MWh | £85.77/MWh |
| C2 | electricity | 2017-04-01 | -21.2% | +14.6% | £76.79/MWh | £88.01/MWh |
| C2g | gas | 2017-04-01 | 15.8% | -3.9% | £17.41/MWh | £16.73/MWh |
| C6 | electricity | 2017-04-01 | -13.1% | +10.5% | £76.79/MWh | £84.88/MWh |
| C8 | electricity | 2017-04-01 | -6.6% | +7.3% | £76.79/MWh | £82.39/MWh |
| C3 | electricity | 2017-07-01 | 0.6% | +3.7% | £68.26/MWh | £70.78/MWh |
| C3g | gas | 2017-07-01 | 10.9% | -1.4% | £16.93/MWh | £16.69/MWh |
| C9 | electricity | 2017-07-01 | 5.7% | +1.2% | £68.26/MWh | £69.06/MWh |
| C4 | electricity | 2017-10-01 | -1.4% | +4.7% | £74.02/MWh | £77.48/MWh |
| C4g | gas | 2017-10-01 | 10.1% | -1.0% | £21.73/MWh | £21.51/MWh |
| C1 | electricity | 2017-12-31 | -1.4% | +4.7% | £85.23/MWh | £89.23/MWh |
| C1g | gas | 2017-12-31 | 8.3% | -0.1% | £25.19/MWh | £25.16/MWh |
| C5 | electricity | 2017-12-31 | -1.1% | +4.5% | £85.23/MWh | £89.11/MWh |
| C7 | electricity | 2017-12-31 | 4.4% | +1.8% | £85.23/MWh | £86.74/MWh |
| C_IC1 | electricity | 2018-01-01 | 10.8% | -1.4% | £87.27/MWh | £86.05/MWh |
| C2 | electricity | 2018-04-01 | 12.3% | -2.2% | £92.46/MWh | £90.46/MWh |
| C2g | gas | 2018-04-01 | 8.7% | -0.4% | £23.77/MWh | £23.68/MWh |
| C6 | electricity | 2018-04-01 | -2.5% | +5.2% | £92.46/MWh | £97.29/MWh |
| C8 | electricity | 2018-04-01 | -14.3% | +11.1% | £92.46/MWh | £102.76/MWh |
| C3 | electricity | 2018-07-01 | -21.8% | +14.9% | £87.62/MWh | £100.67/MWh |
| C3g | gas | 2018-07-01 | 13.9% | -2.9% | £24.38/MWh | £23.66/MWh |
| C9 | electricity | 2018-07-01 | -21.8% | +14.9% | £87.62/MWh | £100.68/MWh |
| C4 | electricity | 2018-10-01 | -4.0% | +6.0% | £99.52/MWh | £105.52/MWh |
| C4g | gas | 2018-10-01 | 13.1% | -2.6% | £31.63/MWh | £30.82/MWh |
| C1 | electricity | 2018-12-31 | 6.5% | +0.7% | £105.79/MWh | £106.58/MWh |
| C1g | gas | 2018-12-31 | 11.7% | -1.8% | £33.03/MWh | £32.42/MWh |
| C5 | electricity | 2018-12-31 | 12.7% | -2.4% | £105.79/MWh | £103.30/MWh |
| C7 | electricity | 2018-12-31 | 9.5% | -0.7% | £105.79/MWh | £105.01/MWh |
| C_IC1 | electricity | 2019-01-01 | 5.5% | +1.3% | £106.39/MWh | £107.72/MWh |
| C2 | electricity | 2019-04-01 | 6.2% | +0.9% | £87.45/MWh | £88.22/MWh |
| C2g | gas | 2019-04-01 | 13.5% | -2.8% | £22.30/MWh | £21.68/MWh |
| C6 | electricity | 2019-04-01 | 6.4% | +0.8% | £87.45/MWh | £88.16/MWh |
| C8 | electricity | 2019-04-01 | 7.0% | +0.5% | £87.45/MWh | £87.88/MWh |
| C3 | electricity | 2019-07-01 | 7.5% | +0.2% | £76.18/MWh | £76.37/MWh |
| C3g | gas | 2019-07-01 | 14.3% | -3.1% | £16.65/MWh | £16.13/MWh |
| C9 | electricity | 2019-07-01 | 3.7% | +2.1% | £76.18/MWh | £77.81/MWh |
| C4 | electricity | 2019-10-01 | 2.8% | +2.6% | £76.50/MWh | £78.50/MWh |
| C4g | gas | 2019-10-01 | 15.8% | -3.9% | £14.15/MWh | £13.59/MWh |
| C1 | electricity | 2019-12-31 | 2.6% | +2.7% | £79.28/MWh | £81.41/MWh |
| C1g | gas | 2019-12-31 | 19.1% | -5.0% | £16.63/MWh | £15.80/MWh |
| C5 | electricity | 2019-12-31 | 0.8% | +3.6% | £79.28/MWh | £82.12/MWh |
| C7 | electricity | 2019-12-31 | 3.2% | +2.4% | £79.28/MWh | £81.18/MWh |
| C_IC1 | electricity | 2020-01-01 | 3.5% | +2.2% | £78.99/MWh | £80.76/MWh |
| C2 | electricity | 2020-03-31 | 3.1% | +2.4% | £66.88/MWh | £68.51/MWh |
| C2g | gas | 2020-03-31 | 16.8% | -4.4% | £14.87/MWh | £14.22/MWh |
| C6 | electricity | 2020-03-31 | -1.7% | +4.9% | £66.88/MWh | £70.14/MWh |
| C8 | electricity | 2020-03-31 | -7.3% | +7.6% | £66.88/MWh | £71.99/MWh |
| C3 | electricity | 2020-06-30 | -9.6% | +8.8% | £59.11/MWh | £64.30/MWh |
| C9 | electricity | 2020-06-30 | -9.6% | +8.8% | £59.11/MWh | £64.30/MWh |
| C4 | electricity | 2020-09-30 | -10.4% | +9.2% | £76.20/MWh | £83.20/MWh |
| C4g | gas | 2020-09-30 | 20.7% | -5.0% | £9.55/MWh | £9.07/MWh |
| C1 | electricity | 2020-12-30 | -6.0% | +7.0% | £90.60/MWh | £96.97/MWh |
| C1g | gas | 2020-12-30 | 6.3% | +0.9% | £18.42/MWh | £18.58/MWh |
| C5 | electricity | 2020-12-30 | -3.3% | +5.6% | £90.60/MWh | £95.70/MWh |
| C7 | electricity | 2020-12-30 | -4.9% | +6.4% | £90.60/MWh | £96.43/MWh |
| C_IC1 | electricity | 2020-12-31 | -6.3% | +7.2% | £91.73/MWh | £98.30/MWh |
| C2 | electricity | 2021-03-31 | -6.3% | +7.2% | £95.98/MWh | £102.85/MWh |
| C2g | gas | 2021-03-31 | -2.7% | +5.3% | £23.81/MWh | £25.08/MWh |
| C6 | electricity | 2021-03-31 | -13.6% | +10.8% | £95.98/MWh | £106.37/MWh |
| C8 | electricity | 2021-03-31 | -19.7% | +13.8% | £95.98/MWh | £109.27/MWh |
| C9 | electricity | 2021-06-30 | -24.4% | +15.0% | £105.48/MWh | £121.30/MWh |
| C4 | electricity | 2021-09-30 | -25.1% | +15.0% | £255.49/MWh | £293.81/MWh |
| C4g | gas | 2021-09-30 | -6.0% | +7.0% | £45.77/MWh | £48.96/MWh |
| C1 | electricity | 2021-12-30 | -16.3% | +12.1% | £259.05/MWh | £290.49/MWh |
| C5 | electricity | 2021-12-30 | -16.3% | +12.1% | £259.05/MWh | £290.49/MWh |
| C7 | electricity | 2021-12-30 | -16.3% | +12.1% | £259.05/MWh | £290.49/MWh |
| C2 | electricity | 2022-03-31 | -8.5% | +8.2% | £265.84/MWh | £287.73/MWh |
| C6 | electricity | 2022-03-31 | -9.2% | +8.6% | £265.84/MWh | £288.74/MWh |
| C8 | electricity | 2022-03-31 | -9.0% | +8.5% | £265.84/MWh | £288.50/MWh |
| C9 | electricity | 2022-06-30 | -9.9% | +8.9% | £210.77/MWh | £229.60/MWh |
| C4 | electricity | 2022-09-30 | -8.1% | +8.1% | £298.27/MWh | £322.32/MWh |
| C4g | gas | 2022-09-30 | -13.0% | +10.5% | £155.84/MWh | £172.20/MWh |
| C7 | electricity | 2022-12-30 | -5.7% | +6.8% | £245.49/MWh | £262.29/MWh |
| C2_2 | electricity | 2023-03-31 | -9.6% | +8.8% | £228.40/MWh | £248.54/MWh |
| C6 | electricity | 2023-03-31 | -3.6% | +5.8% | £228.40/MWh | £241.70/MWh |
| C8 | electricity | 2023-03-31 | -3.6% | +5.8% | £228.40/MWh | £241.62/MWh |
| C9 | electricity | 2023-06-30 | 6.2% | +0.9% | £156.02/MWh | £157.43/MWh |
| C4 | electricity | 2023-09-30 | 13.9% | -3.0% | £124.97/MWh | £121.26/MWh |
| C4g | gas | 2023-09-30 | -5.3% | +6.7% | £35.28/MWh | £37.62/MWh |
| C7 | electricity | 2023-12-30 | 7.2% | +0.4% | £147.77/MWh | £148.36/MWh |
| C2_2 | electricity | 2024-03-30 | 7.9% | +0.1% | £132.98/MWh | £133.05/MWh |
| C6 | electricity | 2024-03-30 | 2.3% | +2.8% | £132.98/MWh | £136.75/MWh |
| C8 | electricity | 2024-03-30 | 2.3% | +2.8% | £132.98/MWh | £136.75/MWh |
| C9 | electricity | 2024-06-29 | 1.4% | +3.3% | £117.04/MWh | £120.90/MWh |
| C4 | electricity | 2024-09-29 | -0.6% | +4.3% | £121.81/MWh | £127.05/MWh |
| C7 | electricity | 2024-12-29 | -0.6% | +4.3% | £164.53/MWh | £171.61/MWh |
| C2_2 | electricity | 2025-03-30 | -1.2% | +4.6% | £168.56/MWh | £176.34/MWh |
| C8 | electricity | 2025-03-30 | -8.4% | +8.2% | £168.56/MWh | £182.37/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **3** | Blind misses: **3** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 1 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £1,419.55 | deliberate: £0.00 | total: £1,419.55

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.14 | No | £162.71 |
| C6 | 2024-03-30 | Blind miss | 0.00 | 0.38 | Yes | £878.25 |
| C4 | 2024-09-29 | Blind miss | 0.11 | 0.23 | No | £378.59 |

## Dual-Fuel Account P&L (Phase 17d)

4 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C1+C1g | £-47.23 | £235.68 | £188.45 | Yes |
| C3+C3g | £-29.58 | £134.68 | £105.09 | Yes |
| C4+C4g | £-354.85 | £-18.29 | £-373.14 | No |
| C2+C2g | £-568.75 | £52.97 | £-515.78 | Yes |

Gas accretive in 3/4 dual-fuel accounts. Total gas net margin: £405.04.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,939.69 across 15 billing accounts. Revenue: £871,270.14.

| # | Customer | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | £757,588.65 | £205,320.10 | £7,036.05 | £5,556.58 | 0.7% |
| 2 | C9 | £13,268.65 | £3,409.53 | £144.47 | £250.13 | 1.9% |
| 3 | C1g | £1,515.34 | £245.22 | £9.54 | £235.68 | 15.6% |
| 4 | C3g | £986.94 | £139.05 | £4.38 | £134.68 | 13.6% |
| 5 | C2g | £1,803.99 | £72.25 | £19.28 | £52.97 | 2.9% |
| 6 | C8 | £16,230.16 | £3,219.35 | £315.43 | £-4.96 | -0.0% |
| 7 | C4g | £8,034.33 | £16.55 | £34.84 | £-18.29 | -0.2% |
| 8 | C3 | £1,438.29 | £391.63 | £7.60 | £-29.58 | -2.1% |
| 9 | C1 | £2,051.13 | £496.98 | £18.97 | £-47.23 | -2.3% |
| 10 | C2_2 | £7,311.61 | £936.50 | £87.06 | £-271.04 | -3.7% |
| 11 | C4 | £8,384.90 | £1,311.12 | £146.36 | £-354.85 | -4.2% |
| 12 | C5 | £9,889.93 | £2,320.62 | £169.36 | £-385.28 | -3.9% |
| 13 | C2 | £3,873.01 | £467.39 | £30.80 | £-568.75 | -14.7% |
| 14 | C7 | £17,474.47 | £2,886.39 | £309.03 | £-659.56 | -3.8% |
| 15 | C6 | £21,418.74 | £2,726.61 | £906.79 | £-1,950.80 | -9.1% |

## Transaction Log

Total events: 2,378,525

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 6 |
| bad_debt_event | 1,165 |
| billing_event | 1,165 |
| capital_charge_event | 1,089,235 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,165 |
| payment_received_event | 1,165 |
| settlement_event | 1,283,345 |
| vat_remittance_event | 1,165 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £1,493,274.83 |
|   Less: VAT remitted to HMRC | (£233,639.11) |
| = Revenue (ex-VAT) | £1,259,635.72 |
| Less: non-commodity pass-through | (£377,164.78) |
| Wholesale cost (settlement events) | (£647,310.86) |
| Gross margin | £235,160.09 |
| Capital charges | (£9,239.95) |
| Net margin | £225,920.14 |

_Cash reconciliation: of £1,493,274.83 billed, bad debt of £29,788.06 was written off, leaving £1,463,486.77 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £429,771.18._

| Acquisition spend | (£1,650.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £218,570.14 |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 2 | 0 | 0% | £550.00 |
| 2021 | 2 | 0 | 0% | £550.00 |
| 2024 | 2 | 0 | 0% | £550.00 |

**Total:** 6 attempts, 0 wins (0% win rate), £1,650.00 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £218,570.14

## 2016

**Trading & Risk**

- Net margin: £-672.38 (gross £636.67, capital £193.74)
  - Electricity: gross £549.85, capital £187.42, net £-752.87
  - Gas: gross £86.81, capital £6.32, net £80.49
- Treasury at year end: £462,826.29
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.90), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.90), C6 0.85 (avg 0.85), C7 0.85 (avg 0.90), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 81
  - 2016-01-01: treasury £463,165.53, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-31: treasury £463,162.81, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-01: treasury £463,160.19, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-31: treasury £463,157.52, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-04-30: treasury £463,155.42, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-05-30: treasury £463,153.59, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-06-29: treasury £463,151.52, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-07-29: treasury £463,149.62, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-08-28: treasury £463,147.81, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-09-27: treasury £463,145.52, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-10-27: treasury £463,142.99, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-11-26: treasury £463,138.50, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-12-26: treasury £463,135.42, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-18: treasury £463,153.39, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-02-17: treasury £463,135.79, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-03-18: treasury £463,117.14, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-04-17: treasury £463,103.22, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-05-17: treasury £463,090.29, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-06-16: treasury £463,080.10, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-07-16: treasury £463,070.55, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-08-15: treasury £463,061.55, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-09-14: treasury £463,051.08, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-10-14: treasury £463,038.63, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-11-13: treasury £463,017.27, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-12-13: treasury £462,993.76, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-01-13: treasury £462,980.19, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-02-12: treasury £462,975.90, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-03-13: treasury £462,969.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-12: treasury £462,965.41, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-05-12: treasury £462,958.51, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-06-11: treasury £462,952.05, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-07-11: treasury £462,943.80, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-08-10: treasury £462,936.32, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-09-09: treasury £462,928.37, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-10-09: treasury £462,919.78, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-11-08: treasury £462,911.15, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-12-08: treasury £462,900.01, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-08: treasury £462,894.66, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-05-08: treasury £462,887.44, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-06-07: treasury £462,880.88, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-07-07: treasury £462,873.98, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-06: treasury £462,867.38, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-09-05: treasury £462,860.90, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-10-05: treasury £462,853.54, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-11-04: treasury £462,845.26, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-12-04: treasury £462,834.57, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-05: treasury £462,799.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-04-26: treasury £462,777.23, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-05-26: treasury £462,753.63, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-06-25: treasury £462,734.75, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-07-25: treasury £462,716.63, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-08-24: treasury £462,700.32, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-09-23: treasury £462,681.52, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-10-23: treasury £462,656.89, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-11-22: treasury £462,615.43, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-12-22: treasury £462,578.35, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-04-21: treasury £462,442.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-05-21: treasury £462,433.38, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-06-20: treasury £462,427.51, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-20: treasury £462,422.24, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-08-19: treasury £462,417.60, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-09-18: treasury £462,411.72, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-10-18: treasury £462,402.94, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-11-17: treasury £462,389.03, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-12-17: treasury £462,371.70, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-16: treasury £462,317.79, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-08-15: treasury £462,316.00, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-09-14: treasury £462,313.82, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-10-14: treasury £462,311.36, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-11-13: treasury £462,307.65, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-12-13: treasury £462,303.47, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-07-03: treasury £462,310.77, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-08-02: treasury £462,308.12, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-09-01: treasury £462,305.74, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-01: treasury £462,302.61, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-31: treasury £462,298.19, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-11-30: treasury £462,289.49, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-12-30: treasury £462,286.61, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-28: treasury £462,247.44, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-11-27: treasury £462,240.77, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-12-27: treasury £462,235.93, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
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

- Net margin: £-52,166.53 (gross £-7,451.92, capital £5,445.64)
  - Electricity: gross £-7,600.40, capital £5,435.68, net £-52,305.04
  - Gas: gross £148.47, capital £9.96, net £138.51
- Treasury at year end: £410,071.97
- Hedge fraction at first renewal this year (avg across year's terms): C1 1.00 (avg 1.00), C1g 0.95 (avg 0.95), C2 0.95 (avg 0.95), C2g 0.85 (avg 0.85), C3 0.95 (avg 0.95), C3g 0.95 (avg 0.95), C4 0.95 (avg 0.95), C4g 0.95 (avg 0.95), C5 1.00 (avg 1.00), C6 0.95 (avg 0.95), C7 1.00 (avg 1.00), C8 0.95 (avg 0.95), C9 0.95 (avg 0.95), C_IC1 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 87
  - 2017-01-03: treasury £462,825.42, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-02-02: treasury £462,814.72, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-03-04: treasury £462,804.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-01-21: treasury £462,537.54, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-02-20: treasury £462,494.48, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-03-22: treasury £462,460.00, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-01-16: treasury £462,355.12, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-02-15: treasury £462,335.83, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-03-17: treasury £462,324.23, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-01-12: treasury £462,300.03, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-02-11: treasury £462,295.54, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-03-13: treasury £462,291.90, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-04-12: treasury £462,288.76, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-05-12: treasury £462,284.86, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-06-11: treasury £462,281.10, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-01-29: treasury £462,277.92, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-02-28: treasury £462,272.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-03-30: treasury £462,269.59, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-04-29: treasury £462,262.86, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-05-29: treasury £462,255.58, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-06-28: treasury £462,251.07, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-01-26: treasury £462,229.67, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-02-25: treasury £462,223.62, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-03-27: treasury £462,218.27, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-04-26: treasury £462,212.61, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-05-26: treasury £462,205.78, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-06-25: treasury £462,200.07, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-07-25: treasury £462,194.46, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-08-24: treasury £462,188.68, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-09-23: treasury £462,182.10, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-01-15: treasury £462,283.92, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-02-14: treasury £462,278.45, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-03-16: treasury £462,273.25, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-04-15: treasury £462,268.47, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-05-15: treasury £462,263.51, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-06-14: treasury £462,259.02, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-07-14: treasury £462,254.57, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-08-13: treasury £462,250.18, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-09-12: treasury £462,245.58, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-10-12: treasury £462,240.43, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-11-11: treasury £462,234.81, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-12-11: treasury £462,228.31, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-12-02: treasury £416,525.27, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,882.82 / stressed £23,160.83) ratio 2.37
  - 2017-04-01: treasury £410,072.15, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2017-05-01: treasury £410,081.21, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2017-05-31: treasury £410,089.68, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2017-06-30: treasury £410,098.29, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2017-07-30: treasury £410,106.82, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2017-08-29: treasury £410,115.29, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2017-09-28: treasury £410,124.10, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2017-10-28: treasury £410,133.16, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2017-11-27: treasury £410,143.38, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2017-12-27: treasury £410,153.29, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2017-04-18: treasury £410,147.30, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2017-05-18: treasury £410,163.05, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2017-06-17: treasury £410,173.71, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2017-07-17: treasury £410,183.21, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2017-08-16: treasury £410,192.71, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2017-09-15: treasury £410,203.48, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2017-10-15: treasury £410,215.22, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2017-11-14: treasury £410,233.37, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2017-12-14: treasury £410,257.17, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2017-04-13: treasury £410,337.03, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2017-05-13: treasury £410,348.97, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2017-06-12: treasury £410,352.16, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2017-07-12: treasury £410,354.53, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2017-08-11: treasury £410,356.63, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2017-09-10: treasury £410,358.11, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2017-10-10: treasury £410,364.90, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2017-11-09: treasury £410,376.13, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2017-12-09: treasury £410,391.99, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2017-07-08: treasury £410,461.46, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2017-08-07: treasury £410,459.24, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2017-09-06: treasury £410,456.95, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2017-10-06: treasury £410,454.32, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2017-11-05: treasury £410,451.59, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2017-12-05: treasury £410,448.30, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2017-11-19: treasury £410,432.42, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2017-07-26: treasury £410,445.36, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2017-08-25: treasury £410,438.97, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2017-09-24: treasury £410,431.74, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2017-10-24: treasury £410,423.94, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2017-11-23: treasury £410,413.16, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2017-12-23: treasury £410,400.14, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2017-10-21: treasury £410,318.35, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2017-11-20: treasury £410,325.82, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2017-12-20: treasury £410,333.09, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.54
- Worst single period: C_IC1 on 2017-01-21 period 19, net margin £-27.85

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 3, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £484.17
  - By billing account: C1 £-54.61, C2 £407.20, C3 £109.81, C4 £967.90, C5 £-18.73, C6 £1,140.90, C7 £111.10, C8 £1,003.76, C9 £690.16
- Bill shock events (>=20%): 33 -- C5 2017-01-31 (42%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (56%); C7 2017-01-31 (45%); C7 2017-02-28 (28%); C7 2017-05-31 (31%); C7 2017-06-30 (32%); C7 2017-09-30 (27%); C7 2017-10-31 (22%); C7 2017-11-30 (77%); C2 2017-04-30 (21%); C6 2017-04-30 (21%); C6 2017-05-31 (22%); C6 2017-11-30 (50%); C8 2017-05-31 (40%); C8 2017-06-30 (36%); C8 2017-09-30 (46%); C8 2017-10-31 (22%); C8 2017-11-30 (84%); C8 2017-12-31 (22%); C9 2017-05-31 (33%); C9 2017-06-30 (26%); C9 2017-09-30 (30%); C9 2017-10-31 (22%); C9 2017-11-30 (70%); C4 2017-10-31 (26%); C_IC1 2017-02-28 (29%); C_IC1 2017-05-31 (33%); C_IC1 2017-06-30 (34%); C_IC1 2017-09-30 (30%); C_IC1 2017-10-31 (24%); C_IC1 2017-11-30 (82%)
- Churn risk (accounts renewing in 2017): 6 at risk (≥20% churn prob): C1 20%, C5 32%, C6 35%, C7 35%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £91.87-£101.02/MWh, net margin £-62.31 -- **net-negative**
- C1g (gas): tariff £17.69-£25.16/MWh, net margin £36.00
- C2 (electricity): tariff £56.89-£105.31/MWh, net margin £52.90
- C2g (gas): tariff £15.86-£16.73/MWh, net margin £-31.75 -- **net-negative**
- C3 (electricity): tariff £57.51-£78.17/MWh, net margin £-39.36 -- **net-negative**
- C3g (gas): tariff £14.02-£16.69/MWh, net margin £30.95
- C4 (electricity): tariff £61.12-£86.16/MWh, net margin £-32.44 -- **net-negative**
- C4g (gas): tariff £17.42-£21.51/MWh, net margin £103.31
- C5 (electricity): tariff £94.02-£98.98/MWh, net margin £-271.07 -- **net-negative**
- C6 (electricity): tariff £56.89-£101.86/MWh, net margin £18.34
- C7 (electricity): tariff £70.43-£134.45/MWh, net margin £-212.31 -- **net-negative**
- C8 (electricity): tariff £44.70-£138.86/MWh, net margin £29.87
- C9 (electricity): tariff £45.19-£106.64/MWh, net margin £-89.60 -- **net-negative**
- C_IC1 (electricity): tariff £61.54-£117.48/MWh, net margin £-51,699.07 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -73.1% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £462,826.27 -> £410,071.97 (11.4%)
- Bills issued: 168, average clarity 0.886, average bill shock 12.8%, bad debt provision £6,216.53, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-50,865.76 vs. naked (unhedged) net margin: £29,005.98
- hedging cost £79,871.74 vs. a fully unhedged book (commodity-only: actual net £-50,865.76 vs. naked net £29,005.98)
  - C1: actual £44.23 vs. naked £128.87 -- hedging cost £84.64
  - C1g: actual £56.29 vs. naked £27.00 -- hedging added £29.29
  - C2: actual £108.40 vs. naked £369.55 -- hedging cost £261.15
  - C2g: actual £-44.36 vs. naked £-22.00 -- hedging cost £22.37
  - C3: actual £-42.44 vs. naked £77.75 -- hedging cost £120.19
  - C3g: actual £31.08 vs. naked £-36.08 -- hedging added £67.15
  - C4: actual £59.61 vs. naked £181.17 -- hedging cost £121.56
  - C4g: actual £97.32 vs. naked £2.41 -- hedging added £94.92
  - C5: actual £182.03 vs. naked £474.98 -- hedging cost £292.95
  - C6: actual £194.98 vs. naked £350.94 -- hedging cost £155.95
  - C7: actual £152.07 vs. naked £416.53 -- hedging cost £264.47
  - C8: actual £131.04 vs. naked £412.01 -- hedging cost £280.97
  - C9: actual £-136.95 vs. naked £119.81 -- hedging cost £256.76
  - C_IC1: actual £-51,699.07 vs. naked £26,503.03 -- hedging cost £78,202.10

**Year narrative:** 2017 produced a net loss of £-52,166.53 across 14 accounts. The risk committee intervened 87 time(s), raising hedge fractions in response to elevated VaR. 33 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £33,951.53 (gross £85,265.72, capital £778.15)
  - Electricity: gross £85,078.98, capital £770.99, net £33,771.96
  - Gas: gross £186.74, capital £7.16, net £179.58
- Treasury at year end: £444,836.43
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.90 (avg 0.90), C1g 1.00 (avg 1.00), C2 1.00 (avg 1.00), C2g 0.85 (avg 0.85), C3 1.00 (avg 1.00), C3g 1.00 (avg 1.00), C4 1.00 (avg 1.00), C4g 1.00 (avg 1.00), C5 0.90 (avg 0.90), C6 1.00 (avg 1.00), C7 0.90 (avg 0.90), C8 1.00 (avg 1.00), C9 1.00 (avg 1.00), C_IC1 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 68
  - 2018-01-26: treasury £410,162.27, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2018-02-25: treasury £410,171.16, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2018-03-27: treasury £410,179.27, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,847.02 / stressed £23,146.66) ratio 2.37
  - 2018-01-13: treasury £410,279.62, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2018-02-12: treasury £410,300.66, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2018-03-14: treasury £410,319.95, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, VaR (current £54,386.64 / stressed £22,964.53) ratio 2.37
  - 2018-01-08: treasury £410,411.79, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2018-02-07: treasury £410,432.01, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2018-03-09: treasury £410,452.43, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,265.62 / stressed £22,916.65) ratio 2.37
  - 2018-01-04: treasury £410,444.77, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2018-02-03: treasury £410,440.61, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2018-03-05: treasury £410,436.08, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2018-04-04: treasury £410,432.03, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2018-05-04: treasury £410,427.54, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2018-06-03: treasury £410,423.32, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, VaR (current £54,244.68 / stressed £22,906.10) ratio 2.37
  - 2018-01-22: treasury £410,383.78, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2018-02-21: treasury £410,370.22, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2018-03-23: treasury £410,353.07, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2018-04-22: treasury £410,337.21, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2018-05-22: treasury £410,325.02, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2018-06-21: treasury £410,316.69, C1->1.00, C2->1.00, C3->1.00, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,163.75 / stressed £22,865.31) ratio 2.37
  - 2018-01-19: treasury £410,339.77, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2018-02-18: treasury £410,346.03, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2018-03-20: treasury £410,351.61, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2018-04-19: treasury £410,355.87, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2018-05-19: treasury £410,359.39, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2018-06-18: treasury £410,362.56, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2018-07-18: treasury £410,365.65, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2018-08-17: treasury £410,368.74, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2018-09-16: treasury £410,371.86, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,115.13 / stressed £22,841.41) ratio 2.37
  - 2018-01-07: treasury £410,472.04, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-02-06: treasury £410,477.22, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-03-08: treasury £410,482.41, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-04-07: treasury £410,486.85, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-05-07: treasury £410,489.91, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-06-06: treasury £410,492.70, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-07-06: treasury £410,495.46, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-08-05: treasury £410,498.27, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-09-04: treasury £410,501.02, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-10-04: treasury £410,504.15, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-11-03: treasury £410,507.45, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-12-03: treasury £410,511.37, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-05-20: treasury £410,536.84, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £54,090.28 / stressed £22,830.93) ratio 2.37
  - 2018-01-25: treasury £410,592.77, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-02-24: treasury £410,620.51, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-03-26: treasury £410,647.84, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-04-25: treasury £410,662.35, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-05-25: treasury £410,673.40, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-06-24: treasury £410,681.15, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-07-24: treasury £410,688.72, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-08-23: treasury £410,696.17, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-09-22: treasury £410,704.48, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-10-22: treasury £410,715.04, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-11-21: treasury £410,730.50, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-12-21: treasury £410,747.79, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,868.47 / stressed £22,737.38) ratio 2.37
  - 2018-01-20: treasury £410,772.71, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-02-19: treasury £410,801.18, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-03-21: treasury £410,834.91, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-04-20: treasury £410,851.06, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-05-20: treasury £410,858.48, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-06-19: treasury £410,858.59, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-07-19: treasury £410,858.32, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-08-18: treasury £410,857.87, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-09-17: treasury £410,858.11, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-10-17: treasury £410,861.90, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-11-16: treasury £410,876.24, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-12-16: treasury £410,895.63, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->0.95, VaR (current £53,754.88 / stressed £22,689.48) ratio 2.37
  - 2018-01-16: treasury £413,856.04, C2->1.00, C3->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, VaR (current £8,035.39 / stressed £5,575.39) ratio 1.44
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.36
- Worst single period: C_IC1 on 2018-03-01 period 43, net margin £-16.31

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 3, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2018): £30,619.04
  - By billing account: C1 £182.02, C2 £-84.80, C3 £261.74, C4 £1,038.95, C5 £727.51, C6 £336.41, C7 £618.90, C8 £577.67, C9 £948.50, C_IC1 £301,583.53
- Bill shock events (>=20%): 41 -- C1g 2018-01-31 (20%); C5 2018-04-30 (32%); C5 2018-06-30 (21%); C5 2018-10-31 (32%); C5 2018-11-30 (27%); C7 2018-04-30 (39%); C7 2018-05-31 (29%); C7 2018-06-30 (31%); C7 2018-09-30 (30%); C7 2018-10-31 (47%); C7 2018-11-30 (33%); C2 2018-04-30 (20%); C2g 2018-04-30 (26%); C6 2018-04-30 (31%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (34%); C8 2018-05-31 (38%); C8 2018-06-30 (43%); C8 2018-08-31 (25%); C8 2018-09-30 (53%); C8 2018-10-31 (55%); C8 2018-11-30 (30%); C3 2018-07-31 (22%); C3g 2018-07-31 (25%); C9 2018-04-30 (32%); C9 2018-05-31 (34%); C9 2018-06-30 (34%); C9 2018-08-31 (43%); C9 2018-09-30 (45%); C9 2018-10-31 (40%); C9 2018-12-31 (20%); C4g 2018-10-31 (30%); C_IC1 2018-04-30 (40%); C_IC1 2018-05-31 (30%); C_IC1 2018-06-30 (33%); C_IC1 2018-09-30 (33%); C_IC1 2018-10-31 (51%); C_IC1 2018-11-30 (35%)
- Churn risk (accounts renewing in 2018): 8 at risk (≥20% churn prob): C1 20%, C3 23%, C5 41%, C6 32%, C7 41%, C8 38%, C9 38%, C_IC1 38%

**Pricing & Margin**

- C1 (electricity): tariff £101.02-£106.58/MWh, net margin £43.98
- C1g (gas): tariff £25.16-£32.42/MWh, net margin £56.49
- C2 (electricity): tariff £90.46-£105.31/MWh, net margin £-197.03 -- **net-negative**
- C2g (gas): tariff £16.73-£26.69/MWh, net margin £-6.28 -- **net-negative**
- C3 (electricity): tariff £78.17-£107.83/MWh, net margin £14.06
- C3g (gas): tariff £16.69-£23.66/MWh, net margin £31.95
- C4 (electricity): tariff £86.16-£105.52/MWh, net margin £50.08
- C4g (gas): tariff £21.51-£30.82/MWh, net margin £97.41
- C5 (electricity): tariff £98.98-£103.30/MWh, net margin £180.55
- C6 (electricity): tariff £97.29-£101.86/MWh, net margin £-375.59 -- **net-negative**
- C7 (electricity): tariff £77.24-£157.52/MWh, net margin £152.86
- C8 (electricity): tariff £72.74-£154.14/MWh, net margin £-92.19 -- **net-negative**
- C9 (electricity): tariff £55.86-£164.08/MWh, net margin £64.07
- C_IC1 (electricity): tariff £81.14-£154.90/MWh, net margin £33,931.15

**Portfolio Health**

- Capital cost ratio: 0.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.888, average bill shock 12.1%, bad debt provision £7,569.48, avg complaint probability 3.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £33,613.24 vs. naked (unhedged) net margin: £81,136.17
- hedging cost £47,522.94 vs. a fully unhedged book (commodity-only: actual net £33,613.24 vs. naked net £81,136.17)
  - C1: actual £25.66 vs. naked £210.47 -- hedging cost £184.81
  - C1g: actual £100.96 vs. naked £220.80 -- hedging cost £119.84
  - C2: actual £-307.24 vs. naked £207.07 -- hedging cost £514.31
  - C2g: actual £11.82 vs. naked £66.36 -- hedging cost £54.54
  - C3: actual £77.02 vs. naked £215.27 -- hedging cost £138.26
  - C3g: actual £34.13 vs. naked £54.35 -- hedging cost £20.22
  - C4: actual £38.28 vs. naked £378.63 -- hedging cost £340.36
  - C4g: actual £100.33 vs. naked £308.91 -- hedging cost £208.58
  - C5: actual £54.56 vs. naked £849.96 -- hedging cost £795.41
  - C6: actual £-666.86 vs. naked £76.20 -- hedging cost £743.06
  - C7: actual £106.78 vs. naked £710.51 -- hedging cost £603.72
  - C8: actual £-234.84 vs. naked £423.57 -- hedging cost £658.40
  - C9: actual £341.51 vs. naked £656.08 -- hedging cost £314.58
  - C_IC1: actual £33,931.15 vs. naked £76,757.99 -- hedging cost £42,826.85

**Year narrative:** 2018 produced a net gain of £33,951.53 across 14 accounts. The risk committee intervened 68 time(s), raising hedge fractions in response to elevated VaR. 41 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £18,530.53 (gross £76,054.19, capital £66.53)
  - Electricity: gross £75,800.08, capital £60.90, net £18,282.04
  - Gas: gross £254.12, capital £5.63, net £248.49
- Treasury at year end: £462,584.39
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.90 (avg 0.90), C3g 0.90 (avg 0.90), C4 0.90 (avg 0.90), C4g 0.90 (avg 0.90), C5 0.85 (avg 0.85), C6 0.90 (avg 0.90), C7 0.85 (avg 0.85), C8 0.90 (avg 0.90), C9 0.90 (avg 0.90), C_IC1 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2019-01-31 period 41, net margin £-8.51

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 3, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2019): £30,412.41
  - By billing account: C1 £327.90, C2 £76.07, C3 £346.33, C4 £1,059.10, C5 £1,015.62, C6 £561.42, C7 £867.33, C8 £677.42, C9 £1,323.40, C_IC1 £297,869.50
- Bill shock events (>=20%): 40 -- C1 2019-04-30 (21%); C5 2019-01-31 (22%); C5 2019-02-28 (21%); C5 2019-06-30 (26%); C5 2019-10-31 (43%); C5 2019-11-30 (35%); C7 2019-01-31 (32%); C7 2019-02-28 (26%); C7 2019-05-31 (24%); C7 2019-06-30 (35%); C7 2019-10-31 (71%); C7 2019-11-30 (45%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (42%); C6 2019-11-30 (26%); C8 2019-01-31 (26%); C8 2019-02-28 (28%); C8 2019-04-30 (26%); C8 2019-06-30 (39%); C8 2019-07-31 (35%); C8 2019-09-30 (59%); C8 2019-10-31 (86%); C8 2019-11-30 (37%); C3 2019-04-30 (20%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (36%); C9 2019-07-31 (44%); C9 2019-09-30 (50%); C9 2019-10-31 (74%); C9 2019-11-30 (37%); C4g 2019-10-31 (36%); C_IC1 2019-01-31 (32%); C_IC1 2019-02-28 (27%); C_IC1 2019-05-31 (25%); C_IC1 2019-06-30 (37%); C_IC1 2019-09-30 (21%); C_IC1 2019-10-31 (78%); C_IC1 2019-11-30 (48%)
- Churn risk (accounts renewing in 2019): 7 at risk (≥20% churn prob): C3 23%, C5 38%, C6 32%, C7 38%, C8 38%, C9 35%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £81.41-£106.58/MWh, net margin £25.56
- C1g (gas): tariff £15.80-£32.42/MWh, net margin £100.66
- C2 (electricity): tariff £90.46-£105.87/MWh, net margin £-47.53 -- **net-negative**
- C2g (gas): tariff £21.68-£26.69/MWh, net margin £19.30
- C3 (electricity): tariff £76.37-£107.83/MWh, net margin £23.62
- C3g (gas): tariff £16.13-£23.66/MWh, net margin £34.43
- C4 (electricity): tariff £78.50-£105.52/MWh, net margin £31.02
- C4g (gas): tariff £13.59-£30.82/MWh, net margin £94.10
- C5 (electricity): tariff £82.12-£103.30/MWh, net margin £54.23
- C6 (electricity): tariff £97.29-£105.79/MWh, net margin £-163.82 -- **net-negative**
- C7 (electricity): tariff £63.78-£157.52/MWh, net margin £106.37
- C8 (electricity): tariff £78.33-£154.14/MWh, net margin £-16.12 -- **net-negative**
- C9 (electricity): tariff £61.13-£164.08/MWh, net margin £202.83
- C_IC1 (electricity): tariff £84.64-£161.59/MWh, net margin £18,065.87

**Portfolio Health**

- Capital cost ratio: 0.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.885, average bill shock 13.5%, bad debt provision £7,868.43, avg complaint probability 3.8%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £18,648.35 vs. naked (unhedged) net margin: £122,756.88
- hedging cost £104,108.52 vs. a fully unhedged book (commodity-only: actual net £18,648.35 vs. naked net £122,756.88)
  - C1: actual £7.42 vs. naked £143.78 -- hedging cost £136.35
  - C1g: actual £31.84 vs. naked £73.75 -- hedging cost £41.92
  - C2: actual £52.92 vs. naked £474.97 -- hedging cost £422.05
  - C2g: actual £20.10 vs. naked £149.81 -- hedging cost £129.71
  - C3: actual £-24.36 vs. naked £169.00 -- hedging cost £193.36
  - C3g: actual £37.09 vs. naked £94.66 -- hedging cost £57.58
  - C4: actual £27.17 vs. naked £304.45 -- hedging cost £277.28
  - C4g: actual £82.61 vs. naked £109.87 -- hedging cost £27.25
  - C5: actual £35.42 vs. naked £606.48 -- hedging cost £571.06
  - C6: actual £108.69 vs. naked £951.55 -- hedging cost £842.85
  - C7: actual £44.77 vs. naked £478.58 -- hedging cost £433.81
  - C8: actual £126.12 vs. naked £730.37 -- hedging cost £604.25
  - C9: actual £32.69 vs. naked £520.24 -- hedging cost £487.55
  - C_IC1: actual £18,065.87 vs. naked £117,949.37 -- hedging cost £99,883.50

**Year narrative:** 2019 produced a net gain of £18,530.53 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 40 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £5,405.56 (gross £61,279.55, capital £1,080.35)
  - Electricity: gross £61,124.28, capital £1,073.00, net £5,257.65
  - Gas: gross £155.27, capital £7.35, net £147.92
- Treasury at year end: £468,367.19
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85), C_IC1 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2020-03-04 period 37, net margin £-70.85

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 3, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C3, C_IC1
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £23,621.16
  - By billing account: C1 £304.60, C2 £211.86, C3 £257.98, C4 £883.65, C5 £1,194.23, C6 £708.23, C7 £945.18, C8 £864.75, C9 £1,277.44, C_IC1 £229,563.64
- Bill shock events (>=20%): 34 -- C1g 2020-01-31 (33%); C5 2020-04-30 (29%); C5 2020-10-31 (37%); C5 2020-12-31 (26%); C7 2020-04-30 (35%); C7 2020-05-31 (21%); C7 2020-06-30 (27%); C7 2020-10-31 (60%); C7 2020-11-30 (23%); C7 2020-12-31 (35%); C2 2020-04-30 (32%); C2g 2020-04-30 (22%); C6 2020-04-30 (43%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (47%); C8 2020-05-31 (25%); C8 2020-06-30 (32%); C8 2020-09-30 (53%); C8 2020-10-31 (65%); C8 2020-12-31 (42%); C9 2020-04-30 (28%); C9 2020-05-31 (25%); C9 2020-06-30 (35%); C9 2020-09-30 (44%); C9 2020-10-31 (50%); C9 2020-12-31 (36%); C_IC1 2020-01-31 (20%); C_IC1 2020-04-30 (36%); C_IC1 2020-05-31 (23%); C_IC1 2020-06-30 (29%); C_IC1 2020-10-31 (66%); C_IC1 2020-11-30 (25%); C_IC1 2020-12-30 (29%)
- Churn risk (accounts renewing in 2020): 8 at risk (≥20% churn prob): C1 26%, C4 20%, C5 35%, C6 32%, C7 35%, C8 38%, C9 41%, C_IC1 35%

**Pricing & Margin**

- C1 (electricity): tariff £81.41-£96.97/MWh, net margin £7.07
- C1g (gas): tariff £15.80-£18.58/MWh, net margin £31.85
- C2 (electricity): tariff £68.51-£105.87/MWh, net margin £-42.47 -- **net-negative**
- C2g (gas): tariff £14.22-£21.68/MWh, net margin £44.76
- C3 (electricity): tariff £76.37/MWh, net margin £-10.71 -- **net-negative**
- C3g (gas): tariff £16.13/MWh, net margin £19.58
- C4 (electricity): tariff £78.50-£83.20/MWh, net margin £28.41
- C4g (gas): tariff £9.07-£13.59/MWh, net margin £51.73
- C5 (electricity): tariff £82.12-£95.70/MWh, net margin £32.27
- C6 (electricity): tariff £70.14-£105.79/MWh, net margin £-125.38 -- **net-negative**
- C7 (electricity): tariff £63.78-£144.65/MWh, net margin £45.08
- C8 (electricity): tariff £56.56-£149.54/MWh, net margin £33.22
- C9 (electricity): tariff £50.52-£116.71/MWh, net margin £31.53
- C_IC1 (electricity): tariff £63.45-£121.14/MWh, net margin £5,258.63

**Portfolio Health**

- Capital cost ratio: 1.8% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.881, average bill shock 12.5%, bad debt provision £6,109.17, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £4,505.96 vs. naked (unhedged) net margin: £72,225.33
- hedging cost £67,719.37 vs. a fully unhedged book (commodity-only: actual net £4,505.96 vs. naked net £72,225.33)
  - C1: actual £-30.93 vs. naked £-138.15 -- hedging added £107.22
  - C1g: actual £-18.42 vs. naked £-299.71 -- hedging added £281.29
  - C2: actual £-83.59 vs. naked £155.96 -- hedging cost £239.55
  - C2g: actual £46.64 vs. naked £37.94 -- hedging added £8.69
  - C4: actual £1.17 vs. naked £17.30 -- hedging cost £16.14
  - C4g: actual £-82.13 vs. naked £-364.57 -- hedging added £282.44
  - C5: actual £-201.63 vs. naked £-880.87 -- hedging added £679.24
  - C6: actual £-263.34 vs. naked £-46.22 -- hedging cost £217.12
  - C7: actual £-75.47 vs. naked £-432.25 -- hedging added £356.79
  - C8: actual £-45.84 vs. naked £149.65 -- hedging cost £195.48
  - C9: actual £0.88 vs. naked £-53.74 -- hedging added £54.63
  - C_IC1: actual £5,258.63 vs. naked £74,080.00 -- hedging cost £68,821.37

**Year narrative:** 2020 produced a net gain of £5,405.56 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 34 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-1,534.25 (gross £1,246.85, capital £355.42)
  - Electricity: gross £1,320.31, capital £347.34, net £-1,452.71
  - Gas: gross £-73.46, capital £8.08, net £-81.54
- Treasury at year end: £467,501.55
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C4 0.85 (avg 0.85), C4g 0.95 (avg 0.95), C6 0.85 (avg 0.85), C7 0.95 (avg 0.95), C8 0.85 (avg 0.85), C9 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2021-01-08 period 39, net margin £-2.12

**Customer Book**

- Active accounts: 11 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2021): £22,505.81
  - By billing account: C1 £253.52, C2 £118.97, C3 £279.44, C4 £909.97, C5 £1,031.96, C6 £519.90, C7 £995.82, C8 £638.86, C9 £1,020.64, C_IC1 £219,289.02
- Bill shock events (>=20%): 30 -- C5 2021-05-31 (22%); C5 2021-06-30 (32%); C5 2021-10-31 (29%); C5 2021-11-30 (50%); C7 2021-01-31 (22%); C7 2021-05-31 (30%); C7 2021-06-30 (47%); C7 2021-10-31 (55%); C7 2021-11-30 (65%); C2g 2021-04-30 (30%); C6 2021-04-30 (29%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-04-30 (22%); C8 2021-05-31 (28%); C8 2021-06-30 (61%); C8 2021-09-30 (24%); C8 2021-10-31 (67%); C8 2021-11-30 (82%); C9 2021-02-28 (22%); C9 2021-05-31 (24%); C9 2021-06-30 (50%); C9 2021-08-31 (21%); C9 2021-09-30 (22%); C9 2021-10-31 (62%); C9 2021-11-30 (49%); C9 2021-12-31 (24%); C4 2021-10-31 (139%); C4g 2021-10-31 (203%)
- Churn risk (accounts renewing in 2021): 6 at risk (≥20% churn prob): C2 20%, C5 35%, C6 38%, C7 35%, C8 41%, C9 35%

**Pricing & Margin**

- C1 (electricity): tariff £96.97/MWh, net margin £-30.44 -- **net-negative**
- C1g (gas): tariff £18.58/MWh, net margin £-18.40 -- **net-negative**
- C2 (electricity): tariff £68.51-£115.26/MWh, net margin £-196.56 -- **net-negative**
- C2g (gas): tariff £14.22-£25.08/MWh, net margin £23.05
- C4 (electricity): tariff £83.20-£293.81/MWh, net margin £22.78
- C4g (gas): tariff £9.07-£58.76/MWh, net margin £-86.19 -- **net-negative**
- C5 (electricity): tariff £95.70/MWh, net margin £-197.21 -- **net-negative**
- C6 (electricity): tariff £70.14-£121.97/MWh, net margin £-600.12 -- **net-negative**
- C7 (electricity): tariff £75.77-£438.86/MWh, net margin £-78.24 -- **net-negative**
- C8 (electricity): tariff £56.56-£163.91/MWh, net margin £-290.23 -- **net-negative**
- C9 (electricity): tariff £50.52-£181.95/MWh, net margin £-82.68 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 28.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 132, average clarity 0.877, average bill shock 15.5%, bad debt provision £340.61, avg complaint probability 4.0%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,519.76 vs. naked (unhedged) net margin: £-6,083.12
- hedging added £4,563.36 vs. a fully unhedged book (commodity-only: actual net £-1,519.76 vs. naked net £-6,083.12)
  - C2: actual £-239.23 vs. naked £-330.49 -- hedging added £91.26
  - C2g: actual £13.92 vs. naked £-542.89 -- hedging added £556.81
  - C4: actual £128.87 vs. naked £289.78 -- hedging cost £160.91
  - C4g: actual £-81.16 vs. naked £-1,080.31 -- hedging added £999.15
  - C6: actual £-743.91 vs. naked £-2,407.48 -- hedging added £1,663.57
  - C7: actual £-54.50 vs. naked £174.54 -- hedging cost £229.03
  - C8: actual £-418.49 vs. naked £-1,106.61 -- hedging added £688.13
  - C9: actual £-125.27 vs. naked £-1,079.66 -- hedging added £954.39

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-1,534.25 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 30 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £-1,473.03 (gross £309.73, capital £359.05)
  - Electricity: gross £472.72, capital £354.40, net £-1,305.39
  - Gas: gross £-162.99, capital £4.65, net £-167.64
- Treasury at year end: £465,598.71
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 1.00 (avg 1.00), C6 0.95 (avg 0.95), C7 0.85 (avg 0.85), C8 0.95 (avg 0.95), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2022-01-24 period 34, net margin £-2.57

**Customer Book**

- Active accounts: 9 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2022): £18,825.78
  - By billing account: C1 £223.82, C2 £63.10, C2_2 £-333.55, C3 £288.92, C4 £560.69, C5 £1,154.14, C6 £303.87, C7 £901.60, C8 £581.22, C9 £1,193.72, C_IC1 £202,146.10
- Bill shock events (>=20%): 36 -- C7 2022-01-31 (161%); C7 2022-02-28 (27%); C7 2022-04-30 (23%); C7 2022-05-31 (37%); C7 2022-06-30 (28%); C7 2022-09-30 (36%); C7 2022-11-30 (66%); C7 2022-12-31 (54%); C6 2022-04-30 (79%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-04-30 (77%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (86%); C8 2022-11-30 (73%); C8 2022-12-31 (58%); C9 2022-04-30 (21%); C9 2022-05-31 (30%); C9 2022-06-30 (30%); C9 2022-07-31 (23%); C9 2022-09-30 (50%); C9 2022-10-31 (31%); C9 2022-11-30 (46%); C9 2022-12-31 (53%); C4g 2022-10-31 (154%); C2_2 2022-04-30 (1717%); C2_2 2022-05-31 (39%); C2_2 2022-06-30 (33%); C2_2 2022-09-30 (77%); C2_2 2022-11-30 (65%); C2_2 2022-12-31 (57%)
- Churn risk (accounts renewing in 2022): 5 at risk (≥20% churn prob): C4 23%, C6 32%, C7 35%, C8 35%, C9 38%

**Pricing & Margin**

- C2 (electricity): tariff £115.26/MWh, net margin £-67.94 -- **net-negative**
- C2_2 (electricity): tariff £265.84/MWh, net margin £-554.35 -- **net-negative**
- C2g (gas): tariff £25.08/MWh, net margin £-1.48 -- **net-negative**
- C4 (electricity): tariff £293.81-£322.32/MWh, net margin £-43.67 -- **net-negative**
- C4g (gas): tariff £58.76-£174.40/MWh, net margin £-166.16 -- **net-negative**
- C6 (electricity): tariff £121.97-£346.48/MWh, net margin £-548.18 -- **net-negative**
- C7 (electricity): tariff £206.08-£438.86/MWh, net margin £-62.21 -- **net-negative**
- C8 (electricity): tariff £85.86-£519.31/MWh, net margin £-81.05 -- **net-negative**
- C9 (electricity): tariff £95.31-£355.90/MWh, net margin £52.02

**Portfolio Health**

- Capital cost ratio: 115.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 88, average clarity 0.808, average bill shock 43.8%, bad debt provision £494.56, avg complaint probability 5.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-2,816.66 vs. naked (unhedged) net margin: £6,712.83
- hedging cost £9,529.50 vs. a fully unhedged book (commodity-only: actual net £-2,816.66 vs. naked net £6,712.83)
  - C2_2: actual £-896.84 vs. naked £418.88 -- hedging cost £1,315.73
  - C4: actual £-538.66 vs. naked £1,164.21 -- hedging cost £1,702.86
  - C4g: actual £-395.92 vs. naked £2,469.04 -- hedging cost £2,864.96
  - C6: actual £-488.47 vs. naked £-380.12 -- hedging cost £108.35
  - C7: actual £-786.24 vs. naked £1,411.58 -- hedging cost £2,197.82
  - C8: actual £125.44 vs. naked £1,203.77 -- hedging cost £1,078.33
  - C9: actual £164.03 vs. naked £425.47 -- hedging cost £261.44

**Year narrative:** 2022 (flagged crisis year) produced a net loss of £-1,473.03 across 9 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 36 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £-869.33 (gross £2,089.04, capital £564.43)
  - Electricity: gross £2,343.01, capital £558.62, net £-609.55
  - Gas: gross £-253.97, capital £5.81, net £-259.78
- Treasury at year end: £463,831.53
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.90 (avg 0.90), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C4g on 2023-01-01 period 1, net margin £-1.08

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2023): £17,560.54
  - By billing account: C1 £237.78, C2 £60.28, C2_2 £-35.99, C3 £262.71, C4 £147.41, C5 £1,004.26, C6 £683.91, C7 £524.66, C8 £937.98, C9 £1,171.40, C_IC1 £188,171.60
- Bill shock events (>=20%): 28 -- C7 2023-05-31 (32%); C7 2023-06-30 (37%); C7 2023-10-31 (57%); C7 2023-11-30 (73%); C6 2023-04-30 (39%); C6 2023-05-31 (23%); C6 2023-06-30 (23%); C6 2023-10-31 (39%); C6 2023-11-30 (44%); C8 2023-04-30 (42%); C8 2023-05-31 (41%); C8 2023-06-30 (44%); C8 2023-10-31 (100%); C8 2023-11-30 (70%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (22%); C9 2023-10-31 (75%); C9 2023-11-30 (54%); C4 2023-10-31 (42%); C4g 2023-10-31 (70%); C2_2 2023-05-31 (42%); C2_2 2023-06-30 (42%); C2_2 2023-10-31 (96%); C2_2 2023-11-30 (67%)
- Churn risk (accounts renewing in 2023): 5 at risk (≥20% churn prob): C2_2 35%, C6 26%, C7 38%, C8 35%, C9 41%

**Pricing & Margin**

- C2_2 (electricity): tariff £265.84-£298.25/MWh, net margin £152.64
- C4 (electricity): tariff £143.61-£322.32/MWh, net margin £-388.71 -- **net-negative**
- C4g (gas): tariff £39.62-£174.40/MWh, net margin £-259.78 -- **net-negative**
- C6 (electricity): tariff £248.09-£346.48/MWh, net margin £-36.35 -- **net-negative**
- C7 (electricity): tariff £138.09-£393.43/MWh, net margin £-781.78 -- **net-negative**
- C8 (electricity): tariff £189.85-£519.31/MWh, net margin £313.91
- C9 (electricity): tariff £123.70-£355.90/MWh, net margin £130.74

**Portfolio Health**

- Capital cost ratio: 27.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 84, average clarity 0.815, average bill shock 19.9%, bad debt provision £551.30, avg complaint probability 5.1%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £2,019.10 vs. naked (unhedged) net margin: £5,891.39
- hedging cost £3,872.28 vs. a fully unhedged book (commodity-only: actual net £2,019.10 vs. naked net £5,891.39)
  - C2_2: actual £802.62 vs. naked £1,926.45 -- hedging cost £1,123.84
  - C4: actual £-0.68 vs. naked £381.83 -- hedging cost £382.51
  - C4g: actual £154.27 vs. naked £53.35 -- hedging added £100.92
  - C6: actual £259.83 vs. naked £648.38 -- hedging cost £388.54
  - C7: actual £184.03 vs. naked £821.69 -- hedging cost £637.66
  - C8: actual £463.25 vs. naked £1,364.23 -- hedging cost £900.98
  - C9: actual £155.78 vs. naked £695.46 -- hedging cost £539.67

**Year narrative:** 2023 produced a net loss of £-869.33 across 7 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 28 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £955.12 (gross £3,580.34, capital £292.14)
  - Electricity: gross £3,448.26, capital £279.08, net £836.12
  - Gas: gross £132.08, capital £13.07, net £119.01
- Treasury at year end: £465,311.92
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
- Average CLV (Point-in-Time, year-end 2024): £16,752.70
  - By billing account: C1 £201.59, C2 £54.84, C2_2 £249.98, C3 £229.21, C4 £260.96, C5 £1,023.76, C6 £803.86, C7 £760.83, C8 £1,098.72, C9 £1,223.24, C_IC1 £178,372.75
- Bill shock events (>=20%): 24 -- C7 2024-02-29 (27%); C7 2024-05-31 (38%); C7 2024-09-30 (36%); C7 2024-10-31 (39%); C7 2024-11-30 (50%); C8 2024-02-29 (23%); C8 2024-04-30 (48%); C8 2024-05-31 (50%); C8 2024-07-31 (27%); C8 2024-09-30 (77%); C8 2024-10-31 (36%); C8 2024-11-30 (63%); C9 2024-05-31 (50%); C9 2024-07-31 (35%); C9 2024-09-30 (57%); C9 2024-10-31 (23%); C9 2024-11-30 (48%); C2_2 2024-02-29 (23%); C2_2 2024-04-30 (57%); C2_2 2024-05-31 (49%); C2_2 2024-07-31 (26%); C2_2 2024-09-30 (68%); C2_2 2024-10-31 (36%); C2_2 2024-11-30 (59%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 38%, C4 23%, C6 38%, C7 35%, C8 41%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £133.05-£298.25/MWh, net margin £263.90
- C4 (electricity): tariff £143.61/MWh, net margin £-6.38 -- **net-negative**
- C4g (gas): tariff £39.62/MWh, net margin £119.01
- C6 (electricity): tariff £248.09/MWh, net margin £115.98
- C7 (electricity): tariff £134.83-£263.63/MWh, net margin £187.12
- C8 (electricity): tariff £107.45-£362.43/MWh, net margin £244.00
- C9 (electricity): tariff £94.99-£236.15/MWh, net margin £31.50

**Portfolio Health**

- Capital cost ratio: 8.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 69, average clarity 0.807, average bill shock 20.0%, bad debt provision £301.34, avg complaint probability 5.2%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-78.10 vs. naked (unhedged) net margin: £764.79
- hedging cost £842.89 vs. a fully unhedged book (commodity-only: actual net £-78.10 vs. naked net £764.79)
  - C2_2: actual £-92.10 vs. naked £228.90 -- hedging cost £321.01
  - C7: actual £69.62 vs. naked £246.25 -- hedging cost £176.64
  - C8: actual £66.62 vs. naked £249.77 -- hedging cost £183.15
  - C9: actual £-122.24 vs. naked £39.87 -- hedging cost £162.11

**Year narrative:** 2024 produced a net gain of £955.12 across 7 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 24 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £-187.54 (gross £949.13, capital £104.49)
  - Electricity: gross £949.13, capital £104.49, net £-187.54
- Treasury at year end: £465,207.79
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
- Average CLV (Point-in-Time, year-end 2025): £16,238.38
  - By billing account: C1 £215.28, C2 £53.27, C2_2 £234.68, C3 £229.13, C4 £258.85, C5 £947.01, C6 £717.88, C7 £858.48, C8 £1,042.34, C9 £1,143.16, C_IC1 £172,922.14
- Bill shock events (>=20%): 18 -- C7 2025-01-31 (25%); C7 2025-04-30 (37%); C7 2025-05-31 (23%); C7 2025-06-07 (80%); C8 2025-01-31 (39%); C8 2025-02-28 (24%); C8 2025-04-30 (24%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (33%); C9 2025-06-07 (72%); C2_2 2025-01-31 (38%); C2_2 2025-02-28 (24%); C2_2 2025-04-30 (24%); C2_2 2025-05-31 (37%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £133.05-£179.24/MWh, net margin £-133.23 -- **net-negative**
- C7 (electricity): tariff £134.83-£257.41/MWh, net margin £72.15
- C8 (electricity): tariff £107.45-£273.55/MWh, net margin £-61.57 -- **net-negative**
- C9 (electricity): tariff £94.99-£181.35/MWh, net margin £-64.90 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 11.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 24, average clarity 0.724, average bill shock 32.6%, bad debt provision £109.97, avg complaint probability 7.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-172.19 vs. naked (unhedged) net margin: £40.10
- hedging cost £212.29 vs. a fully unhedged book (commodity-only: actual net £-172.19 vs. naked net £40.10)
  - C2_2: actual £-84.72 vs. naked £71.23 -- hedging cost £155.95
  - C8: actual £-87.47 vs. naked £-31.13 -- hedging cost £56.34

**Year narrative:** 2025 produced a net loss of £-187.54 across 4 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 18 customer(s) experienced a bill shock of >=20%.
