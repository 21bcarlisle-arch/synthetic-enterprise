# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £2,792,708.41
  (£326,072.19 net change)
- Solvency signal (final year): £305,812/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £18,013,806.53
  VAT remitted to HMRC: (£866,306.63) | Revenue (ex-VAT): £17,147,499.90
  Non-commodity pass-through: (£4,015,878.29)
- Gross margin: £5,463,238.96
- Capital costs: £237,019.16
- Net margin: £5,226,219.80
- Capital cost ratio: 4.3% of gross
- Net margin as % of revenue: 30.5%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 43
- Bills issued: 1549, average clarity 0.859,
  service quality score 0.919
- Enterprise value (CLV sum across 14 billing accounts): £5,986,958.27
- Cost to serve (whole portfolio): £86,084.80, net margin after cost to serve: £5,140,135.00
- Hedge effectiveness (whole window): hedging cost £3,950,311.72 vs. a fully unhedged book (commodity-only: actual net £326,072.19 vs. naked net £4,276,383.91)

- **2021** (crisis year): net margin £-102,308.14, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £108,572.03, 9 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £5,463,238.96, capital £237,019.16, net £5,226,219.80. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 4.3% (commodity basis, comparable to old model) / 4.3% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £-102,308.14 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 30.5%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £5,226,219.80
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £4,276,383.91
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £3,950,311.72 vs. a fully unhedged book (commodity-only: actual net £326,072.19 vs. naked net £4,276,383.91)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £105,277.66 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £613,673.72 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £78.36 | £305.50 | £99.64 | £483.50 |
| 2017 | £30,340.95 | £0.00 | £177.18 | £470.82 | £202.39 | £31,191.33 |
| 2018 | £107,088.37 | £0.00 | £-335.13 | £246.92 | £154.27 | £107,154.42 |
| 2019 | £230,260.38 | £796.93 | £217.74 | £489.51 | £162.74 | £231,927.29 |
| 2020 | £-44,620.11 | £4,649.51 | £146.30 | £574.31 | £176.47 | £-39,073.52 |
| 2021 | £-101,986.86 | £-210.70 | £67.80 | £108.42 | £-286.79 | £-102,308.14 |
| 2022 | £152,991.63 | £-41,869.94 | £784.52 | £-2,326.33 | £-1,007.85 | £108,572.03 |
| 2023 | £-99,686.24 | £-29,293.72 | £1,288.55 | £94.43 | £-1,003.54 | £-128,600.52 |
| 2024 | £140,466.11 | £-35,857.09 | £512.85 | £1,742.25 | £357.52 | £107,221.63 |
| 2025 | £28,125.52 | £-18,958.15 | £0.00 | £274.35 | £62.43 | £9,504.16 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **51** renewals.  Lost (churned): **5** accounts.

Accounts lost before end of window: C1, C2, C3, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8255 |
| C_IC1 | 2018-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3902 |
| C1 | 2018-12-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6312 |
| C_IC2 | 2019-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3710 |
| C1 | 2019-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9505 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.1700 | 0.5500 | 0.9235 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.5838 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9505 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.2600 | 0.5500 | 0.8830 | 0.8723 |
| C2_2 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.7019 |
| C2_2 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0025 |
| C4 | 2024-09-29 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.3751 |
| C2_2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 192.5%
- **Average signed error:** +53.5% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -63.2% | 63.2% |
| 2017 | 3 | -91.5% | 91.5% |
| 2018 | 4 | +466.1% | 540.0% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | -15.9% | 145.1% |
| 2021 | 9 | +5.5% | 125.0% |
| 2022 | 7 | -22.9% | 98.7% |
| 2023 | 7 | +2.8% | 136.4% |
| 2024 | 7 | +76.1% | 234.6% |
| 2025 | 2 | -94.4% | 94.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 33.8%, abs error 300.6%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.9%, abs error 145.3%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.7% | 0.0% | 63.2% |
| 2017 | 0 | 3 | 0.0% | 2.1% | 0.0% | 91.5% |
| 2018 | 2 | 2 | 20.4% | 50.1% | 136.9% | 943.2% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 17.0% | 0.5% | 192.8% | 97.4% |
| 2021 | 3 | 6 | 64.5% | 4.0% | 211.5% | 81.8% |
| 2022 | 0 | 7 | 0.0% | 19.5% | 0.0% | 98.7% |
| 2023 | 2 | 5 | 24.3% | 19.0% | 47.9% | 171.8% |
| 2024 | 3 | 4 | 37.4% | 0.0% | 414.0% | 100.0% |
| 2025 | 0 | 2 | 0.0% | 2.1% | 0.0% | 94.4% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 10 (26%)
- **Below/at SVT (protected):** 29 (74%)
- **Mean rate vs SVT premium:** -8.1%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -2.3% | 136.7 | 140.0 |
| 2017 | 3 | 0 (0%) | -11.1% | 124.5 | 140.0 |
| 2018 | 2 | 2 (100%) | +4.3% | 159.0 | 152.5 |
| 2019 | 2 | 0 (0%) | -26.9% | 130.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -24.6% | 133.2 | 176.9 |
| 2021 | 6 | 3 (50%) | +1.5% | 185.4 | 183.8 |
| 2022 | 7 | 4 (57%) | +12.3% | 296.4 | 318.4 |
| 2023 | 5 | 0 (0%) | -31.6% | 227.7 | 364.0 |
| 2024 | 4 | 0 (0%) | -13.4% | 213.3 | 246.9 |
| 2025 | 2 | 1 (50%) | +3.9% | 258.3 | 248.6 |

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
| 2024 | 14 | 9.1% | 23.8% |
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
| 2016 | 3 | 0.63× | 0.81× |
| 2017 | 3 | 0.92× | 0.94× |
| 2018 | 4 | 5.40× ⚠ | 18.00× |
| 2019 | 4 | 5.25× ⚠ | 18.00× |
| 2020 | 10 | 1.45× | 6.46× |
| 2021 | 9 | 1.25× | 4.59× |
| 2022 | 7 | 0.99× | 2.65× |
| 2023 | 7 | 1.36× | 4.59× |
| 2024 | 7 | 2.35× ⚠ | 10.88× |
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
Total events: **6** (5 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.11, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.17, company est=0.03 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.80 |
| 2022-03-31 | CHURN | C2 | SIM p=0.11, company est=0.07 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.17 |

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
| 2024-12-31 | 5 accounts | 1 active | yes |
| 2025-12-31 | 5 accounts | 1 active | yes |

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
| 2024 | 310,695 | 111,051 | 73,601 | 69,383 | 83,390 | 2,019 | 650,139 |  |
| 2025 | 137,776 | 47,658 | 31,649 | 31,498 | 36,697 | 867 | 286,145 |  |
| **Total** | **1,739,398** | **265,456** | **462,574** | **339,654** | **471,398** | **159,240** | **3,437,718** | |

Total policy cost: £3,437,718 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2024 | 144,491 |  |
| 2025 | 62,119 |  |
| **Total** | **886,560** | |

Total network cost: £886,560 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

## Gas Policy Costs and Network Charges (Phase 30b)

Gas CCL: non-domestic only (domestic gas exempt). Gas network (GDN + NTS): all on unit rate.
GGL (Green Gas Levy): per-meter, from Nov 2021; tiny in £/MWh terms.

| Year | Gas Policy (CCL + GGL) £ | Gas Network £ | Total Gas Non-Commodity £ |
|------|--------------------------|---------------|--------------------------|
| 2016 | 0 | 356 | 356 |
| 2017 | 0 | 624 | 624 |
| 2018 | 0 | 609 | 609 |
| 2019 | 15,273 | 50,131 | 65,404 |
| 2020 | 19,520 | 46,890 | 66,411 |
| 2021 | 22,523 | 50,386 | 72,909 |
| 2022 | 27,135 | 54,413 | 81,548 |
| 2023 | 32,320 | 80,214 | 112,534 |
| 2024 | 37,573 | 76,143 | 113,716 |
| 2025 | 16,774 | 31,087 | 47,861 |
| **Total** | **171,119** | **390,853** | **561,971** |

Gas policy pass-through in tariff unit rate (CCL + GGL at term start); gas network pass-through likewise. Net basis risk near-zero for annual contracts.


## Gas Book P&L — Year by Year (Phase 32a)

Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.
Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.

| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |
|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|
| 2016 | 887 | 426 | 461 | 0 | 356 | 5 | 100 | +11.2% |
| 2017 | 1,684 | 848 | 837 | 0 | 624 | 10 | 202 | +12.0% |
| 2018 | 1,979 | 1,201 | 779 | 0 | 609 | 15 | 154 | +7.8% |
| 2019 | 135,981 | 60,399 | 75,582 | 15,273 | 50,131 | 9,218 | 960 | +0.7% |
| 2020 | 119,676 | 43,054 | 76,622 | 19,520 | 46,890 | 5,385 | 4,826 | +4.0% |
| 2021 | 296,623 | 213,989 | 82,634 | 22,523 | 50,386 | 10,223 | -497 | -0.2% |
| 2022 | 593,793 | 503,227 | 90,567 | 27,135 | 54,413 | 51,897 | -42,878 | -7.2% |
| 2023 | 295,491 | 173,919 | 121,572 | 32,320 | 80,214 | 39,335 | -30,297 | -10.3% |
| 2024 | 270,499 | 146,371 | 124,128 | 37,573 | 76,143 | 45,912 | -35,500 | -13.1% |
| 2025 | 128,880 | 76,615 | 52,265 | 16,774 | 31,087 | 23,300 | -18,896 | -14.7% |
| **Total** | **1,845,495** | **1,220,049** | **625,446** | **171,119** | **390,853** | **185,301** | **-121,826** | **-6.6%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,046 | 9 | 274,116 | 2108.59× | OK |
| 2017 | 2,497,889 | 10 | 249,789 | 1921.45× | OK |
| 2018 | 2,486,422 | 11 | 226,038 | 1738.76× | OK |
| 2019 | 2,616,704 | 12 | 218,059 | 1677.37× | OK |
| 2020 | 2,759,668 | 13 | 212,282 | 1632.94× | OK |
| 2021 | 2,618,313 | 12 | 218,193 | 1678.41× | OK |
| 2022 | 2,619,088 | 11 | 238,099 | 1831.53× | OK |
| 2023 | 2,544,748 | 10 | 254,475 | 1957.50× | OK |
| 2024 | 2,696,199 | 10 | 269,620 | 2074.00× | OK |
| 2025 | 2,752,310 | 9 | 305,812 | 2352.40× | OK |

End-state (2025): **£305,812/account** across 9 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 23 | 28 | 2,467,046 | 88077.3× | OK |
| 2017 | 466 | 559 | 2,497,889 | 4466.5× | OK |
| 2018 | 851 | 1,021 | 2,486,422 | 2434.1× | OK |
| 2019 | 1,543 | 1,851 | 2,616,704 | 1413.4× | OK |
| 2020 | 1,980 | 2,377 | 2,759,668 | 1161.2× | OK |
| 2021 | 4,416 | 5,299 | 2,618,313 | 494.1× | OK |
| 2022 | 8,507 | 10,209 | 2,619,088 | 256.6× | OK |
| 2023 | 5,610 | 6,732 | 2,544,748 | 378.0× | OK |
| 2024 | 2,739 | 3,287 | 2,696,199 | 820.2× | OK |
| 2025 | 4,213 | 5,056 | 2,752,310 | 544.4× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,331.32 | £11,437.78 | £257.42/MWh | £135.21/MWh | +0.2% |
| C8 | 106,722 | 43,948 | 41.2% | £11,765.59 | £8,816.43 | £267.72/MWh | £140.45/MWh | +8.1% |
| C9 | 109,387 | 43,689 | 39.9% | £10,773.14 | £8,487.15 | £246.59/MWh | £129.19/MWh | +7.1% |

Total HH revenue: £60,611.41 vs flat equivalent £57,767.77 (+4.9% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 21 | 109% | C8 (2016-10-31) |
| 2017 | 27 | 85% | C8 (2017-11-30) |
| 2018 | 34 | 60% | C_IC1 (2018-02-28) |
| 2019 | 38 | 128% | C_IC1 (2019-03-31) |
| 2020 | 31 | 123% | C_IC2 (2020-03-31) |
| 2021 | 38 | 90% | C_IC2 (2021-04-30) |
| 2022 | 54 | 1712% | C2_2 (2022-04-30) |
| 2023 | 36 | 116% | C_IC2 (2023-06-30) |
| 2024 | 29 | 122% | C_IC2 (2024-07-31) |
| 2025 | 23 | 81% | C_IC4 (2025-06-07) |

Total: **331** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1712% | no |
| 2019-03-31 | C_IC1 | +128% | no |
| 2020-03-31 | C_IC2 | +123% | no |
| 2024-07-31 | C_IC2 | +122% | no |
| 2022-10-31 | C4g | +121% | no |
| 2023-06-30 | C_IC2 | +116% | no |
| 2016-10-31 | C8 | +109% | no |
| 2022-01-31 | C_IC3 | +106% | no |
| 2022-12-31 | C_IC4 | +102% | no |
| 2023-10-31 | C8 | +101% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 15% | 15% | 0 |
| 2017 | 4 | 17% | 23% | 2 ⚠ |
| 2018 | 4 | 17% | 23% | 2 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 5 | 5% | 26% | 1 ⚠ |
| 2021 | 3 | 68% | 95% | 3 ⚠ |
| 2022 | 2 | 48% | 95% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 2 | 0% | 0% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £21.3 | £125.9 (+490%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £16.4 | £35.0 (+113%) | 71% |
| 2021-03-31 | C2g | £22.3 | £35.0 (+57%) | 37% |
| 2020-12-31 | C_IC3g | £15.9 | £21.3 (+34%) | 26% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 18 |
| Retained | 17 (94%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £426,624.62 |
| Margin saved (retained customers' terms) | £2,286,067.76 |
| Wasted offer cost (churned anyway) | £522.85 |
| **Net ROI of retention strategy** | **£1,859,443.14** |
| Acquisition cost avoided (retained customers) | £2,800.00 |
| **Full economic ROI (margin + acq savings)** | **£1,862,243.14** |

Missed opportunities (churns with no offer): **4** (£3,343.32 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 4 (£3,343.32 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24805.26 | £170092.16 | £145286.90 | £0.00 |
| 2019 | 2 | 2 | £43640.54 | £305760.64 | £262120.11 | £0.00 |
| 2020 | 3 | 3 | £27682.39 | £182402.53 | £154720.14 | £396.32 |
| 2021 | 4 | 3 | £121561.82 | £424534.06 | £302972.23 | £-142.51 |
| 2022 | 2 | 2 | £74591.82 | £330932.26 | £256340.45 | £320.54 |
| 2023 | 4 | 4 | £89227.96 | £455958.43 | £366730.47 | £0.00 |
| 2024 | 2 | 2 | £45114.83 | £416387.67 | £371272.84 | £2768.96 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24805.26 | £170092.16 | £150 | £145286.90 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £15172.47 | £105268.85 | £150 | £90096.38 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £28468.07 | £200491.79 | £150 | £172023.73 | retained |
| 2020-01-01 | C_IC3 | 0.38 | 3% | £5910.94 | £16739.66 | £150 | £10828.73 | retained |
| 2020-03-31 | C_IC1 | 0.52 | 5% | £10696.09 | £137186.07 | £150 | £126489.98 | retained |
| 2020-12-31 | C_IC3 | 0.60 | 5% | £11075.36 | £28476.80 | £150 | £17401.44 | retained |
| 2021-03-31 | C_IC2 | 0.84 | 8% | £14523.80 | £95321.96 | £150 | £80798.16 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £23027.52 | £163802.51 | £150 | £140774.98 | retained |
| 2021-12-30 | C5 | 0.80 | 8% | £522.85 | £2403.51 | £400 | £-522.85 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £83487.65 | £165409.59 | £150 | £81921.94 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25301.36 | £94615.87 | £150 | £69314.51 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £49290.46 | £236316.39 | £150 | £187025.93 | retained |
| 2023-03-31 | C6 | 0.37 | 3% | £198.89 | £3088.00 | £400 | £2889.11 | retained |
| 2023-05-30 | C_IC2 | 0.59 | 5% | £11964.97 | £134172.62 | £150 | £122207.65 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £35652.39 | £252452.46 | £150 | £216800.07 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £41411.71 | £66245.35 | £150 | £24833.65 | retained |
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

**Full-history EV:** £5,986,958.27 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £-12,037.47 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £483.50 |
| 2017 | £31,191.33 |
| 2018 | £107,154.42 |
| 2019 | £231,927.29 |
| 2020 | £-39,073.52 |
| 2021 | £-102,308.14 |
| 2022 | £108,572.03 |
| 2023 | £-128,600.52 | ← trailing
| 2024 | £107,221.63 | ← trailing
| 2025 | £9,504.16 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £2,692.63 | — |
| C2 | £5,745.58 | — |
| C2_2 | — | £1,456.49 |
| C3 | £3,022.44 | — |
| C4 | £3,388.70 | £-793.53 |
| C5 | £10,071.16 | — |
| C6 | £15,938.76 | £2,963.95 |
| C7 | £7,507.89 | £-75.40 |
| C8 | £8,302.48 | £252.92 |
| C9 | £8,217.77 | £834.98 |
| C_IC1 | £1,680,864.46 | £407,882.43 |
| C_IC2 | £1,052,951.24 | £213,047.66 |
| C_IC3 | £3,151,491.46 | £-58,648.56 |
| C_IC4 | £32,458.07 | £-578,958.40 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £1,830.67 | — | — | — | — | £5,444.51 | — | £4,335.93 | — | — | — | — | — | — |
| 2017 | £2,677.24 | £7,456.13 | — | £2,927.82 | £4,248.28 | £8,197.80 | £12,327.68 | £5,048.82 | £8,407.97 | £6,413.77 | — | — | — | — |
| 2018 | £2,238.64 | £5,436.30 | — | £2,766.70 | £3,486.92 | £9,389.12 | £10,473.39 | £5,717.27 | £6,652.64 | £6,107.26 | £2,470,926.60 | — | — | — |
| 2019 | £2,615.41 | £4,787.15 | — | £2,890.51 | £3,640.86 | £7,610.96 | £11,163.65 | £5,305.56 | £6,086.08 | £5,572.94 | £1,826,497.92 | £1,079,955.42 | — | — |
| 2020 | £2,109.76 | £5,312.44 | — | £2,082.42 | £3,807.13 | £7,934.44 | £8,759.62 | £5,348.08 | £6,611.63 | £5,832.97 | £1,040,337.24 | £551,264.96 | £1,665,949.60 | £27,358.56 |
| 2021 | £1,741.83 | £4,861.27 | — | £1,812.42 | £2,885.42 | £6,438.41 | £8,759.41 | £4,746.28 | £6,250.66 | £4,989.04 | £989,917.06 | £554,057.06 | £1,667,482.52 | £23,130.05 |
| 2022 | £2,142.42 | £3,736.35 | £488.20 | £1,982.77 | £1,708.20 | £6,204.29 | £9,458.37 | £3,855.89 | £5,535.19 | £5,236.41 | £979,052.29 | £562,968.53 | £1,761,751.13 | £18,899.39 |
| 2023 | £2,141.10 | £3,648.85 | £1,608.58 | £1,888.09 | £1,123.58 | £6,072.51 | £9,985.64 | £3,714.70 | £5,336.60 | £5,289.04 | £1,022,239.98 | £596,228.89 | £1,572,561.61 | £18,222.17 |
| 2024 | £2,157.60 | £3,742.78 | £2,409.53 | £1,871.18 | £1,911.84 | £5,971.58 | £9,650.45 | £4,266.54 | £5,661.87 | £5,696.15 | £1,056,357.28 | £632,747.19 | £1,745,331.68 | £18,973.49 |
| 2025 | £2,087.64 | £3,450.22 | £2,543.71 | £1,785.92 | £2,031.15 | £5,971.58 | £9,762.16 | £4,589.12 | £5,233.45 | £5,491.57 | £1,103,328.67 | £663,440.72 | £1,891,109.87 | £20,504.94 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,530.78, range £32.37–£26,641.41.

- C1: cost to serve £390.58, net margin after CTS £1,446.21
- C1g: cost to serve £48.73, net margin after CTS £887.95
- C2: cost to serve £452.09, net margin after CTS £3,374.16
- C2_2: cost to serve £379.08, net margin after CTS £4,980.68
- C2g: cost to serve £61.52, net margin after CTS £1,215.69
- C3: cost to serve £262.93, net margin after CTS £1,084.32
- C3g: cost to serve £32.37, net margin after CTS £563.17
- C4: cost to serve £647.76, net margin after CTS £3,320.32
- C4g: cost to serve £166.94, net margin after CTS £437.89
- C5: cost to serve £868.81, net margin after CTS £8,195.81
- C6: cost to serve £1,268.87, net margin after CTS £16,429.53
- C7: cost to serve £934.52, net margin after CTS £8,833.77
- C8: cost to serve £917.07, net margin after CTS £10,426.53
- C9: cost to serve £876.93, net margin after CTS £10,832.50
- C_IC1: cost to serve £20,223.10, net margin after CTS £1,913,480.51
- C_IC2: cost to serve £11,515.74, net margin after CTS £923,137.24
- C_IC3: cost to serve £26,641.41, net margin after CTS £1,820,450.08
- C_IC3g: cost to serve £9,224.23, net margin after CTS £612,807.63
- C_IC4: cost to serve £11,172.13, net margin after CTS £21,351.71 — MARGIN_SQUEEZE (below 2% benchmark)

**Activity-Based Pricing Actions**

The following 1 customer(s) are profitable but below the 2% net-margin benchmark (MARGIN_SQUEEZE): C_IC4


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 34 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 12.8%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C3 | electricity | 2017-07-01 | £-28.73 | £440.29 | +1.5% | £122.23/MWh | £123.72/MWh |
| C4 | electricity | 2017-10-01 | £-41.78 | £549.78 | +2.6% | £111.62/MWh | £113.78/MWh |
| C_IC1 | electricity | 2018-01-31 | £-5,694.56 | £10,901.23 | +20.0% | £112.24/MWh | £152.02/MWh |
| C1 | electricity | 2018-12-31 | £-44.40 | £452.69 | +4.8% | £148.68/MWh | £159.68/MWh |
| C5 | electricity | 2018-12-31 | £-251.13 | £2,255.19 | +6.1% | £148.68/MWh | £160.06/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,300.82 | £6,376.41 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,218.30 | £10,243.03 | +20.0% | £128.22/MWh | £174.96/MWh |
| C6 | electricity | 2019-04-01 | £-185.41 | £2,638.00 | +2.0% | £148.35/MWh | £152.57/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,904.90 | £3,444.18 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,041.06 | £6,326.95 | +20.0% | £91.12/MWh | £103.93/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,068.70 | £5,726.15 | +20.0% | £138.90/MWh | £177.60/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,697.97 | £14,511.74 | +20.0% | £113.97/MWh | £140.93/MWh |
| C4 | electricity | 2021-09-30 | £-68.85 | £688.34 | +5.0% | £205.15/MWh | £225.13/MWh |
| C4g | gas | 2021-09-30 | £-98.62 | £361.85 | +20.0% | £53.99/MWh | £70.71/MWh |
| C1 | electricity | 2021-12-30 | £-57.71 | £518.13 | +6.1% | £311.83/MWh | £340.97/MWh |
| C5 | electricity | 2021-12-30 | £-342.29 | £2,666.35 | +7.8% | £311.83/MWh | £346.43/MWh |
| C7 | electricity | 2021-12-30 | £-97.79 | £1,936.81 | +0.1% | £311.83/MWh | £321.41/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,110.59 | £17,661.75 | +7.0% | £269.81/MWh | £311.58/MWh |
| C_IC1 | electricity | 2022-05-30 | £-5,978.26 | £22,384.38 | +20.0% | £239.42/MWh | £305.94/MWh |
| C4 | electricity | 2022-09-30 | £-420.03 | £1,021.16 | +20.0% | £404.86/MWh | £485.26/MWh |
| C4g | gas | 2022-09-30 | £-791.90 | £770.00 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,810.99 | £2,236.99 | +20.0% | £266.73/MWh | £322.61/MWh |
| C_IC3g | gas | 2022-12-31 | £-42,961.08 | £592,608.29 | +2.2% | £101.23/MWh | £119.04/MWh |
| C8 | electricity | 2023-03-31 | £-260.96 | £3,724.74 | +2.0% | £319.17/MWh | £353.73/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,301.95 | £7,055.33 | +20.0% | £171.46/MWh | £235.05/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,645.02 | £17,979.18 | +20.0% | £163.19/MWh | £219.83/MWh |
| C4 | electricity | 2023-09-30 | £-578.55 | £1,701.85 | +20.0% | £216.77/MWh | £257.66/MWh |
| C4g | gas | 2023-09-30 | £-1,481.14 | £2,090.00 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-344.19 | £3,797.69 | +4.1% | £242.22/MWh | £239.46/MWh |
| C_IC3 | electricity | 2023-12-31 | £-158,797.92 | £945,752.34 | +11.8% | £118.95/MWh | £126.32/MWh |
| C_IC3g | gas | 2023-12-31 | £-28,776.23 | £294,338.38 | +4.8% | £51.89/MWh | £60.60/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,934.03 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,645.50 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |
| C_IC3g | gas | 2024-12-30 | £-35,503.62 | £268,215.17 | +8.2% | £50.47/MWh | £55.64/MWh |


## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 113 renewal(s) (27 gas) based on recent portfolio-wide margin rates: 86 surcharge(s), 27 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | -1.5% | +4.8% | £131.49/MWh | £137.73/MWh |
| C1g | gas | 2016-12-31 | 9.7% | -0.8% | £27.63/MWh | £27.40/MWh |
| C5 | electricity | 2016-12-31 | -0.8% | +4.4% | £131.49/MWh | £137.30/MWh |
| C7 | electricity | 2016-12-31 | 2.5% | +2.8% | £131.49/MWh | £135.14/MWh |
| C2 | electricity | 2017-04-01 | 10.2% | -1.1% | £127.97/MWh | £126.60/MWh |
| C2g | gas | 2017-04-01 | 10.9% | -1.4% | £34.54/MWh | £34.04/MWh |
| C6 | electricity | 2017-04-01 | 8.7% | -0.3% | £127.97/MWh | £127.55/MWh |
| C8 | electricity | 2017-04-01 | 7.8% | +0.1% | £127.97/MWh | £128.11/MWh |
| C3 | electricity | 2017-07-01 | 8.6% | -0.3% | £122.23/MWh | £121.86/MWh |
| C3g | gas | 2017-07-01 | 12.9% | -2.5% | £24.33/MWh | £23.73/MWh |
| C9 | electricity | 2017-07-01 | 7.4% | +0.3% | £122.23/MWh | £122.58/MWh |
| C4 | electricity | 2017-10-01 | 9.3% | -0.7% | £111.62/MWh | £110.90/MWh |
| C4g | gas | 2017-10-01 | 11.6% | -1.8% | £27.48/MWh | £26.99/MWh |
| C1 | electricity | 2017-12-31 | 7.7% | +0.1% | £120.10/MWh | £120.26/MWh |
| C1g | gas | 2017-12-31 | 9.3% | -0.6% | £34.79/MWh | £34.56/MWh |
| C5 | electricity | 2017-12-31 | 2.1% | +2.9% | £120.10/MWh | £123.62/MWh |
| C7 | electricity | 2017-12-31 | -2.9% | +5.5% | £120.10/MWh | £126.65/MWh |
| C_IC1 | electricity | 2018-01-31 | -17.7% | +12.9% | £112.24/MWh | £126.68/MWh |
| C2 | electricity | 2018-04-01 | -5.5% | +6.8% | £133.89/MWh | £142.94/MWh |
| C2g | gas | 2018-04-01 | 9.7% | -0.9% | £38.21/MWh | £37.88/MWh |
| C6 | electricity | 2018-04-01 | -5.8% | +6.9% | £133.89/MWh | £143.14/MWh |
| C8 | electricity | 2018-04-01 | 5.5% | +1.3% | £133.89/MWh | £135.57/MWh |
| C3 | electricity | 2018-07-01 | 7.3% | +0.3% | £128.29/MWh | £128.73/MWh |
| C3g | gas | 2018-07-01 | 7.3% | +0.3% | £29.63/MWh | £29.73/MWh |
| C9 | electricity | 2018-07-01 | -3.2% | +5.6% | £128.29/MWh | £135.46/MWh |
| C4 | electricity | 2018-10-01 | -0.3% | +4.1% | £145.00/MWh | £151.00/MWh |
| C4g | gas | 2018-10-01 | 7.8% | +0.1% | £34.60/MWh | £34.63/MWh |
| C1 | electricity | 2018-12-31 | 3.1% | +2.5% | £148.68/MWh | £152.36/MWh |
| C1g | gas | 2018-12-31 | 8.5% | -0.2% | £37.15/MWh | £37.07/MWh |
| C5 | electricity | 2018-12-31 | 5.1% | +1.4% | £148.68/MWh | £150.81/MWh |
| C7 | electricity | 2018-12-31 | 7.7% | +0.1% | £148.68/MWh | £148.90/MWh |
| C_IC2 | electricity | 2019-01-31 | -29.5% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -19.4% | +13.7% | £128.22/MWh | £145.80/MWh |
| C2 | electricity | 2019-04-01 | 4.3% | +1.9% | £148.35/MWh | £151.12/MWh |
| C2g | gas | 2019-04-01 | 4.9% | +1.5% | £32.94/MWh | £33.44/MWh |
| C6 | electricity | 2019-04-01 | 6.4% | +0.8% | £148.35/MWh | £149.54/MWh |
| C8 | electricity | 2019-04-01 | 25.5% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 17.0% | -4.5% | £127.03/MWh | £121.32/MWh |
| C3g | gas | 2019-07-01 | 6.2% | +0.9% | £23.62/MWh | £23.83/MWh |
| C9 | electricity | 2019-07-01 | 5.7% | +1.2% | £127.03/MWh | £128.50/MWh |
| C4 | electricity | 2019-10-01 | 5.8% | +1.1% | £126.72/MWh | £128.09/MWh |
| C4g | gas | 2019-10-01 | 8.7% | -0.3% | £20.41/MWh | £20.34/MWh |
| C1 | electricity | 2019-12-31 | 5.6% | +1.2% | £127.44/MWh | £128.97/MWh |
| C1g | gas | 2019-12-31 | 7.1% | +0.5% | £26.17/MWh | £26.29/MWh |
| C5 | electricity | 2019-12-31 | 3.3% | +2.3% | £127.44/MWh | £130.41/MWh |
| C7 | electricity | 2019-12-31 | 3.1% | +2.5% | £127.44/MWh | £130.58/MWh |
| C_IC3 | electricity | 2020-01-01 | 1.2% | +3.4% | £47.59/MWh | £49.21/MWh |
| C_IC3g | gas | 2020-01-01 | 12.0% | -2.0% | £16.25/MWh | £15.93/MWh |
| C_IC2 | electricity | 2020-03-01 | -97.5% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -90.1% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 12.2% | -2.1% | £22.80/MWh | £22.32/MWh |
| C6 | electricity | 2020-03-31 | -48.2% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -18.1% | +13.0% | £125.12/MWh | £141.43/MWh |
| C_IC1 | electricity | 2020-03-31 | 17.9% | -5.0% | £91.12/MWh | £86.61/MWh |
| C3 | electricity | 2020-06-30 | 14.5% | -3.3% | £113.43/MWh | £109.72/MWh |
| C9 | electricity | 2020-06-30 | 14.5% | -3.3% | £113.43/MWh | £109.72/MWh |
| C4 | electricity | 2020-09-30 | 10.3% | -1.1% | £124.42/MWh | £123.00/MWh |
| C4g | gas | 2020-09-30 | 13.8% | -2.9% | £16.94/MWh | £16.45/MWh |
| C1 | electricity | 2020-12-30 | 6.0% | +1.0% | £133.55/MWh | £134.89/MWh |
| C1g | gas | 2020-12-30 | 4.5% | +1.8% | £28.99/MWh | £29.50/MWh |
| C5 | electricity | 2020-12-30 | -1.0% | +4.5% | £133.55/MWh | £139.56/MWh |
| C7 | electricity | 2020-12-30 | -9.4% | +8.7% | £133.55/MWh | £145.16/MWh |
| C_IC3 | electricity | 2020-12-31 | -9.8% | +8.9% | £50.65/MWh | £55.15/MWh |
| C_IC3g | gas | 2020-12-31 | -4.7% | +6.4% | £20.05/MWh | £21.32/MWh |
| C2 | electricity | 2021-03-31 | -32.9% | +15.0% | £175.90/MWh | £202.28/MWh |
| C2g | gas | 2021-03-31 | -5.5% | +6.8% | £36.20/MWh | £38.65/MWh |
| C6 | electricity | 2021-03-31 | -29.5% | +15.0% | £175.90/MWh | £202.28/MWh |
| C8 | electricity | 2021-03-31 | -25.5% | +15.0% | £175.90/MWh | £202.28/MWh |
| C_IC2 | electricity | 2021-03-31 | -5.1% | +6.6% | £138.90/MWh | £148.00/MWh |
| C_IC1 | electricity | 2021-04-30 | 1.9% | +3.0% | £113.97/MWh | £117.44/MWh |
| C9 | electricity | 2021-06-30 | 2.5% | +2.8% | £170.38/MWh | £175.11/MWh |
| C4 | electricity | 2021-09-30 | -1.0% | +4.5% | £205.15/MWh | £214.40/MWh |
| C4g | gas | 2021-09-30 | -10.3% | +9.2% | £53.99/MWh | £58.93/MWh |
| C1 | electricity | 2021-12-30 | 2.0% | +3.0% | £311.83/MWh | £321.25/MWh |
| C5 | electricity | 2021-12-30 | 2.0% | +3.0% | £311.83/MWh | £321.25/MWh |
| C7 | electricity | 2021-12-30 | 2.0% | +3.0% | £311.83/MWh | £321.25/MWh |
| C_IC3 | electricity | 2021-12-31 | -27.4% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -29.2% | +15.0% | £109.48/MWh | £125.90/MWh |
| C2 | electricity | 2022-03-31 | -35.5% | +15.0% | £361.95/MWh | £416.24/MWh |
| C6 | electricity | 2022-03-31 | -24.5% | +15.0% | £361.95/MWh | £416.24/MWh |
| C8 | electricity | 2022-03-31 | -0.8% | +4.4% | £361.95/MWh | £377.83/MWh |
| C_IC2 | electricity | 2022-04-30 | -8.0% | +8.0% | £269.81/MWh | £291.34/MWh |
| C_IC1 | electricity | 2022-05-30 | -5.0% | +6.5% | £239.42/MWh | £254.95/MWh |
| C9 | electricity | 2022-06-30 | 5.2% | +1.4% | £255.09/MWh | £258.68/MWh |
| C4 | electricity | 2022-09-30 | 8.2% | -0.1% | £404.86/MWh | £404.38/MWh |
| C4g | gas | 2022-09-30 | -26.9% | +15.0% | £183.79/MWh | £211.36/MWh |
| C7 | electricity | 2022-12-30 | 6.4% | +0.8% | £266.73/MWh | £268.84/MWh |
| C_IC3 | electricity | 2022-12-31 | -2.3% | +5.2% | £168.36/MWh | £177.02/MWh |
| C_IC3g | gas | 2022-12-31 | -44.9% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -32.1% | +15.0% | £319.17/MWh | £367.05/MWh |
| C6 | electricity | 2023-03-31 | -17.2% | +12.6% | £319.17/MWh | £359.31/MWh |
| C8 | electricity | 2023-03-31 | -9.3% | +8.7% | £319.17/MWh | £346.77/MWh |
| C_IC2 | electricity | 2023-05-30 | -20.5% | +14.2% | £171.46/MWh | £195.88/MWh |
| C_IC1 | electricity | 2023-06-29 | -16.5% | +12.3% | £163.19/MWh | £183.19/MWh |
| C9 | electricity | 2023-06-30 | -9.6% | +8.8% | £224.44/MWh | £244.19/MWh |
| C4 | electricity | 2023-09-30 | 9.9% | -0.9% | £216.77/MWh | £214.71/MWh |
| C4g | gas | 2023-09-30 | -47.7% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 27.0% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 20.5% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -14.9% | +11.4% | £51.89/MWh | £57.83/MWh |
| C2_2 | electricity | 2024-03-30 | -13.1% | +10.5% | £207.71/MWh | £229.60/MWh |
| C6 | electricity | 2024-03-30 | -15.7% | +11.8% | £207.71/MWh | £232.27/MWh |
| C8 | electricity | 2024-03-30 | -15.7% | +11.8% | £207.71/MWh | £232.27/MWh |
| C_IC2 | electricity | 2024-06-28 | -33.0% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.3% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -27.4% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.3% | +3.9% | £195.97/MWh | £203.55/MWh |
| C4g | gas | 2024-09-29 | -16.4% | +12.2% | £50.11/MWh | £56.23/MWh |
| C7 | electricity | 2024-12-29 | 18.2% | -5.0% | £243.79/MWh | £231.60/MWh |
| C_IC3 | electricity | 2024-12-30 | 8.5% | -0.3% | £116.37/MWh | £116.06/MWh |
| C_IC3g | gas | 2024-12-30 | 4.3% | +1.9% | £50.47/MWh | £51.41/MWh |
| C2_2 | electricity | 2025-03-30 | -21.2% | +14.6% | £284.89/MWh | £326.51/MWh |
| C8 | electricity | 2025-03-30 | -14.6% | +11.3% | £284.89/MWh | £317.09/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **4** | Blind misses: **4** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 1 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £3,343.32 | deliberate: £0.00 | total: £3,343.32

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.11 | No | £396.32 |
| C1 | 2021-12-30 | Blind miss | 0.03 | 0.17 | No | £-142.51 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.11 | No | £320.54 |
| C6 | 2024-03-30 | Blind miss | 0.17 | 0.38 | Yes | £2,768.96 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £145,678.37 | £-120,743.16 | £24,935.22 | No |
| C2+C2g | £382.29 | £378.71 | £761.00 | Yes |
| C1+C1g | £66.12 | £218.41 | £284.54 | Yes |
| C3+C3g | £-14.48 | £37.27 | £22.79 | Yes |
| C4+C4g | £-759.30 | £-1,717.12 | £-2,476.42 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-121,825.88.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £326,072.19 across 19 billing accounts. Revenue: £13,117,723.17.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,200,995.06 | £1,933,703.61 | £18,866.89 | £894,317.63 | 27.9% |
| 2 | C_IC2 | fixed | £1,559,512.38 | £934,652.98 | £8,712.12 | £455,213.19 | 29.2% |
| 3 | C_IC3 | pass_through | £4,684,616.86 | £1,847,091.48 | £23,237.97 | £145,678.37 | 3.1% |
| 4 | C6 | fixed | £30,910.10 | £17,698.40 | £218.34 | £3,123.57 | 10.1% |
| 5 | C2_2 | fixed | £10,179.11 | £5,359.76 | £71.92 | £1,417.59 | 13.9% |
| 6 | C9 | fixed | £19,260.29 | £11,709.42 | £130.38 | £1,242.23 | 6.4% |
| 7 | C8 | fixed | £20,582.02 | £11,343.61 | £136.03 | £1,203.90 | 5.8% |
| 8 | C2 | fixed | £6,107.91 | £3,826.26 | £31.70 | £382.29 | 6.3% |
| 9 | C2g | fixed | £2,732.38 | £1,277.21 | £17.31 | £378.71 | 13.9% |
| 10 | C1g | fixed | £2,092.54 | £936.68 | £14.90 | £218.41 | 10.4% |
| 11 | C1 | fixed | £3,032.50 | £1,836.79 | £15.93 | £66.12 | 2.2% |
| 12 | C3g | fixed | £1,389.09 | £595.54 | £9.77 | £37.27 | 2.7% |
| 13 | C3 | fixed | £2,148.79 | £1,347.25 | £9.79 | £-14.48 | -0.7% |
| 14 | C5 | fixed | £14,896.32 | £9,064.62 | £80.46 | £-185.40 | -1.2% |
| 15 | C4 | fixed | £8,495.23 | £3,968.09 | £65.55 | £-759.30 | -8.9% |
| 16 | C7 | fixed | £20,769.11 | £9,768.29 | £141.34 | £-1,558.19 | -7.5% |
| 17 | C4g | fixed | £7,848.95 | £604.83 | £132.04 | £-1,717.12 | -21.9% |
| 18 | C_IC3g | pass_through | £1,831,432.12 | £622,031.85 | £185,126.72 | £-120,743.16 | -6.6% |
| 19 | C_IC4 | flex | £1,690,722.42 | £32,523.85 | £0.00 | £-1,052,229.46 | -62.2% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £13,117,723 | 100.0% |
| Wholesale cost | -£7,668,383 | 58.5% |
| **Gross supply margin** | **£5,449,341** | **41.5%** |
| Policy + Network costs | -£4,886,249 | 37.2% |
| Capital cost | -£237,019 | 1.8% |
| **Net supply margin** | **£326,072** | **2.5%** |

> *The ledger's `net_margin_gbp` (£5,226,220) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £11,135,847 | 42.6% | 4.0% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,831,432 | 34.0% | -6.6% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £45,806 | 58.4% | 6.4% | CMA 3-8% | ✓ |
| resi/elec | £80,396 | 54.5% | 0.7% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £14,063 | 24.3% | -7.7% | Ofgem CMA 2-4% | ⚠ ANOMALY |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: ANOMALIES DETECTED**
- Segment resi/gas net -7.7% (benchmark Ofgem CMA 2-4%)
## Transaction Log

Total events: 3,322,075

| Event type | Count |
|------------|-------|
| acquisition_gate_event | 1 |
| acquisition_spend_event | 3 |
| bad_debt_event | 1,549 |
| billing_event | 1,549 |
| capital_charge_event | 1,600,120 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,549 |
| payment_received_event | 1,549 |
| settlement_event | 1,714,092 |
| vat_remittance_event | 1,549 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £18,013,806.53 |
|   Less: VAT remitted to HMRC | (£866,306.63) |
| = Revenue (ex-VAT) | £17,147,499.90 |
| Less: non-commodity pass-through | (£4,015,878.29) |
| Wholesale cost (settlement events) | (£7,668,382.65) |
| Gross margin | £5,463,238.96 |
| Capital charges | (£237,019.16) |
| Net margin | £5,226,219.80 |

_Cash reconciliation: of £18,013,806.53 billed, bad debt of £360,232.38 was written off, leaving £17,653,574.16 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £5,732,294.06._

| Acquisition spend | (£950.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £5,219,569.80 |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 1 | 0 | 0% | £150.00 |
| 2021 | 2 | 0 | 0% | £400.00 |
| 2024 | 1 | 0 | 0% | £400.00 |

**Total:** 4 attempts, 0 wins (0% win rate), £950.00 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £5,219,569.80

## 2016

**Trading & Risk**

- Net margin: £483.50 (gross £5,566.16, capital £75.72)
  - Electricity: gross £5,105.33, capital £70.30, net £383.86
  - Gas: gross £460.83, capital £5.42, net £99.64
- Treasury at year end: £2,467,046.39
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.22, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-01-31: treasury £2,466,641.13, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-01: treasury £2,466,646.13, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-31: treasury £2,466,650.88, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-04-30: treasury £2,466,654.76, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-05-30: treasury £2,466,658.54, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-06-29: treasury £2,466,661.95, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-07-29: treasury £2,466,665.46, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-08-28: treasury £2,466,668.99, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-09-27: treasury £2,466,672.72, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-10-27: treasury £2,466,676.47, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-11-26: treasury £2,466,680.28, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-12-26: treasury £2,466,685.01, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.25
- Worst single period: C9 on 2016-11-20 period 36, net margin £-0.31

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £3,870.37
  - By billing account: C1 £1,830.67, C5 £5,444.51, C7 £4,335.93
- Bill shock events (>=20%): 21 -- C5 2016-05-31 (28%); C5 2016-06-30 (21%); C5 2016-10-31 (43%); C5 2016-11-30 (45%); C7 2016-04-30 (22%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-10-31 (82%); C7 2016-11-30 (54%); C6 2016-05-31 (26%); C6 2016-06-30 (23%); C6 2016-10-31 (42%); C6 2016-11-30 (47%); C8 2016-05-31 (41%); C8 2016-06-30 (42%); C8 2016-09-30 (25%); C8 2016-10-31 (109%); C8 2016-11-30 (72%); C9 2016-09-30 (20%); C9 2016-10-31 (80%); C9 2016-11-30 (61%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.30-£137.73/MWh, net margin £49.51
- C1g (gas): tariff £24.34-£27.40/MWh, net margin £25.21
- C2 (electricity): tariff £107.62/MWh, net margin £16.27
- C2g (gas): tariff £26.92/MWh, net margin £53.62
- C3 (electricity): tariff £98.21/MWh, net margin £-9.77 -- **net-negative**
- C3g (gas): tariff £21.93/MWh, net margin £4.76
- C4 (electricity): tariff £98.43/MWh, net margin £-7.23 -- **net-negative**
- C4g (gas): tariff £24.40/MWh, net margin £16.05
- C5 (electricity): tariff £117.30-£137.30/MWh, net margin £139.04
- C6 (electricity): tariff £107.62/MWh, net margin £-60.68 -- **net-negative**
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £178.48
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £73.27
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £4.97

**Portfolio Health**

- Capital cost ratio: 1.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.890, average bill shock 14.0%, bad debt provision £313.05, avg complaint probability 3.6%
- Solvency signal: £274,116/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £911.60 vs. naked (unhedged) net margin: £8,651.10
- hedging cost £7,739.49 vs. a fully unhedged book (commodity-only: actual net £911.60 vs. naked net £8,651.10)
  - C1: actual £105.79 vs. naked £541.16 -- hedging cost £435.37
  - C1g: actual £69.44 vs. naked £271.86 -- hedging cost £202.43
  - C2: actual £17.02 vs. naked £444.49 -- hedging cost £427.47
  - C2g: actual £68.92 vs. naked £203.62 -- hedging cost £134.70
  - C3: actual £-28.73 vs. naked £209.70 -- hedging cost £238.43
  - C3g: actual £6.58 vs. naked £112.13 -- hedging cost £105.55
  - C4: actual £-41.78 vs. naked £271.77 -- hedging cost £313.54
  - C4g: actual £57.89 vs. naked £209.67 -- hedging cost £151.78
  - C5: actual £304.55 vs. naked £2,539.70 -- hedging cost £2,235.15
  - C6: actual £-102.13 vs. naked £748.13 -- hedging cost £850.26
  - C7: actual £339.88 vs. naked £1,818.74 -- hedging cost £1,478.85
  - C8: actual £115.75 vs. naked £695.71 -- hedging cost £579.96
  - C9: actual £-1.58 vs. naked £584.41 -- hedging cost £585.99

**Year narrative:** 2016 produced a net gain of £483.50 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 21 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £31,191.33 (gross £122,310.42, capital £1,267.27)
  - Electricity: gross £121,473.90, capital £1,256.84, net £30,988.94
  - Gas: gross £836.52, capital £10.43, net £202.39
- Treasury at year end: £2,497,888.77
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.91 (avg 0.91), C7 0.90 (avg 0.90), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,467,046.38, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-02-24: treasury £2,467,046.47, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-03-26: treasury £2,467,047.00, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-04-25: treasury £2,467,108.67, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-05-25: treasury £2,467,104.82, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-06-24: treasury £2,467,101.63, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-07-24: treasury £2,467,073.90, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-08-23: treasury £2,467,070.08, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-09-22: treasury £2,467,065.61, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-10-22: treasury £2,467,167.20, C5->1.00, C7->1.00, VaR (current £887.92 / stressed £351.47) ratio 2.53
  - 2017-11-21: treasury £2,467,172.05, C5->1.00, C7->1.00, VaR (current £887.92 / stressed £351.47) ratio 2.53
  - 2017-12-21: treasury £2,467,176.76, C5->1.00, C7->1.00, VaR (current £887.92 / stressed £351.47) ratio 2.53
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-20.37

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £6,411.73
  - By billing account: C1 £2,677.24, C2 £7,456.13, C3 £2,927.82, C4 £4,248.28, C5 £8,197.80, C6 £12,327.68, C7 £5,048.82, C8 £8,407.97, C9 £6,413.77
- Bill shock events (>=20%): 27 -- C5 2017-01-31 (29%); C5 2017-02-28 (23%); C5 2017-05-31 (20%); C5 2017-06-30 (22%); C5 2017-11-30 (58%); C7 2017-01-31 (35%); C7 2017-02-28 (28%); C7 2017-05-31 (31%); C7 2017-06-30 (33%); C7 2017-09-30 (27%); C7 2017-10-31 (22%); C7 2017-11-30 (78%); C6 2017-05-31 (22%); C6 2017-06-30 (20%); C6 2017-11-30 (51%); C8 2017-05-31 (40%); C8 2017-06-30 (37%); C8 2017-09-30 (48%); C8 2017-10-31 (23%); C8 2017-11-30 (85%); C8 2017-12-31 (22%); C9 2017-05-31 (33%); C9 2017-06-30 (27%); C9 2017-09-30 (31%); C9 2017-10-31 (22%); C9 2017-11-30 (72%); C4 2017-10-31 (23%)
- Churn risk (accounts renewing in 2017): 5 at risk (≥20% churn prob): C5 32%, C6 35%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £120.26-£137.73/MWh, net margin £56.04
- C1g (gas): tariff £27.40-£34.56/MWh, net margin £44.17
- C2 (electricity): tariff £107.62-£126.60/MWh, net margin £34.65
- C2g (gas): tariff £26.92-£34.04/MWh, net margin £115.01
- C3 (electricity): tariff £98.21-£126.72/MWh, net margin £10.77
- C3g (gas): tariff £21.93-£23.73/MWh, net margin £-2.37 -- **net-negative**
- C4 (electricity): tariff £98.43-£116.78/MWh, net margin £-35.03 -- **net-negative**
- C4g (gas): tariff £24.40-£26.99/MWh, net margin £45.57
- C5 (electricity): tariff £123.62-£137.30/MWh, net margin £164.38
- C6 (electricity): tariff £107.62-£130.55/MWh, net margin £12.80
- C7 (electricity): tariff £101.87-£202.71/MWh, net margin £159.90
- C8 (electricity): tariff £84.56-£192.17/MWh, net margin £159.81
- C9 (electricity): tariff £77.16-£183.87/MWh, net margin £84.68
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £30,340.95

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.884, average bill shock 11.4%, bad debt provision £7,399.37, avg complaint probability 3.5%
- Solvency signal: £249,789/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,794.15 vs. naked (unhedged) net margin: £110,927.19
- hedging cost £80,133.04 vs. a fully unhedged book (commodity-only: actual net £30,794.15 vs. naked net £110,927.19)
  - C1: actual £-44.40 vs. naked £197.65 -- hedging cost £242.05
  - C1g: actual £63.01 vs. naked £141.23 -- hedging cost £78.21
  - C2: actual £44.42 vs. naked £501.53 -- hedging cost £457.11
  - C2g: actual £129.47 vs. naked £243.61 -- hedging cost £114.15
  - C3: actual £51.56 vs. naked £299.86 -- hedging cost £248.30
  - C3g: actual £-11.24 vs. naked £62.84 -- hedging cost £74.08
  - C4: actual £-20.48 vs. naked £312.53 -- hedging cost £333.01
  - C4g: actual £10.21 vs. naked £124.64 -- hedging cost £114.43
  - C5: actual £-251.13 vs. naked £1,000.04 -- hedging cost £1,251.17
  - C6: actual £78.91 vs. naked £1,312.57 -- hedging cost £1,233.65
  - C7: actual £-22.98 vs. naked £814.86 -- hedging cost £837.83
  - C8: actual £214.23 vs. naked £915.44 -- hedging cost £701.21
  - C9: actual £211.62 vs. naked £887.26 -- hedging cost £675.64
  - C_IC1: actual £30,340.95 vs. naked £104,113.14 -- hedging cost £73,772.19

**Year narrative:** 2017 produced a net gain of £31,191.33 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 27 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £107,154.42 (gross £267,893.11, capital £1,547.20)
  - Electricity: gross £267,114.58, capital £1,532.40, net £107,000.15
  - Gas: gross £778.53, capital £14.80, net £154.27
- Treasury at year end: £2,486,422.13
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.90 (avg 0.90), C3g 0.85 (avg 0.85), C4 0.91 (avg 0.91), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.88), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2018-03-01 period 27, net margin £-14.72

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £252,319.48
  - By billing account: C1 £2,238.64, C2 £5,436.30, C3 £2,766.70, C4 £3,486.92, C5 £9,389.12, C6 £10,473.39, C7 £5,717.27, C8 £6,652.64, C9 £6,107.26, C_IC1 £2,470,926.60
- Bill shock events (>=20%): 34 -- C5 2018-04-30 (32%); C5 2018-06-30 (21%); C5 2018-10-31 (32%); C5 2018-11-30 (28%); C7 2018-04-30 (39%); C7 2018-05-31 (29%); C7 2018-06-30 (31%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C6 2018-04-30 (25%); C6 2018-05-31 (22%); C6 2018-06-30 (22%); C6 2018-10-31 (31%); C6 2018-11-30 (22%); C8 2018-04-30 (35%); C8 2018-05-31 (38%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (56%); C8 2018-11-30 (30%); C9 2018-04-30 (32%); C9 2018-05-31 (35%); C9 2018-06-30 (35%); C9 2018-07-31 (21%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-10-31 (34%); C4g 2018-10-31 (23%); C_IC1 2018-02-28 (60%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C4 20%, C5 38%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £120.26-£162.68/MWh, net margin £-44.04 -- **net-negative**
- C1g (gas): tariff £34.56-£37.07/MWh, net margin £62.96
- C2 (electricity): tariff £126.60-£142.94/MWh, net margin £-4.05 -- **net-negative**
- C2g (gas): tariff £34.04-£37.88/MWh, net margin £95.30
- C3 (electricity): tariff £126.72-£128.73/MWh, net margin £13.82
- C3g (gas): tariff £23.73-£29.73/MWh, net margin £-13.80 -- **net-negative**
- C4 (electricity): tariff £116.78-£154.00/MWh, net margin £0.84
- C4g (gas): tariff £26.99-£34.63/MWh, net margin £9.80
- C5 (electricity): tariff £123.62-£163.06/MWh, net margin £-249.57 -- **net-negative**
- C6 (electricity): tariff £130.55-£143.14/MWh, net margin £-85.57 -- **net-negative**
- C7 (electricity): tariff £101.87-£227.85/MWh, net margin £-20.53 -- **net-negative**
- C8 (electricity): tariff £100.66-£207.86/MWh, net margin £107.05
- C9 (electricity): tariff £96.31-£207.68/MWh, net margin £193.83
- C_IC1 (electricity): tariff £-82.12-£232.53/MWh, net margin £113,313.65
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,225.29 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.872, average bill shock 11.3%, bad debt provision £12,939.46, avg complaint probability 3.6%
- Solvency signal: £226,038/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £118,048.02 vs. naked (unhedged) net margin: £251,862.37
- hedging cost £133,814.35 vs. a fully unhedged book (commodity-only: actual net £118,048.02 vs. naked net £251,862.37)
  - C1: actual £58.30 vs. naked £419.04 -- hedging cost £360.74
  - C1g: actual £72.60 vs. naked £278.32 -- hedging cost £205.72
  - C2: actual £-26.20 vs. naked £567.44 -- hedging cost £593.64
  - C2g: actual £89.76 vs. naked £239.37 -- hedging cost £149.62
  - C3: actual £-24.76 vs. naked £305.76 -- hedging cost £330.52
  - C3g: actual £-6.13 vs. naked £139.96 -- hedging cost £146.10
  - C4: actual £54.33 vs. naked £561.63 -- hedging cost £507.30
  - C4g: actual £32.91 vs. naked £395.85 -- hedging cost £362.95
  - C5: actual £180.16 vs. naked £2,011.63 -- hedging cost £1,831.48
  - C6: actual £-185.41 vs. naked £1,369.47 -- hedging cost £1,554.88
  - C7: actual £69.43 vs. naked £1,306.19 -- hedging cost £1,236.75
  - C8: actual £19.77 vs. naked £898.89 -- hedging cost £879.12
  - C9: actual £162.68 vs. naked £1,030.21 -- hedging cost £867.53
  - C_IC1: actual £123,775.88 vs. naked £208,762.66 -- hedging cost £84,986.78
  - C_IC2: actual £-6,225.29 vs. naked £33,575.93 -- hedging cost £39,801.22

**Year narrative:** 2018 produced a net gain of £107,154.42 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 34 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £231,927.29 (gross £709,418.21, capital £11,317.99)
  - Electricity: gross £633,836.55, capital £2,099.92, net £230,967.63
  - Gas: gross £75,581.66, capital £9,218.08, net £959.66
- Treasury at year end: £2,616,703.89
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.88 (avg 0.88), C6 0.91 (avg 0.91), C7 0.88 (avg 0.88), C8 0.92 (avg 0.92), C9 0.88 (avg 0.88), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2019-02-04 period 35, net margin £-14.60

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £268,738.77
  - By billing account: C1 £2,615.41, C2 £4,787.15, C3 £2,890.51, C4 £3,640.86, C5 £7,610.96, C6 £11,163.65, C7 £5,305.56, C8 £6,086.08, C9 £5,572.94, C_IC1 £1,826,497.92, C_IC2 £1,079,955.42
- Bill shock events (>=20%): 38 -- C1 2019-01-31 (21%); C1 2019-04-30 (22%); C5 2019-01-31 (45%); C5 2019-02-28 (22%); C5 2019-06-30 (26%); C5 2019-10-31 (44%); C5 2019-11-30 (36%); C7 2019-01-31 (42%); C7 2019-02-28 (26%); C7 2019-05-31 (24%); C7 2019-06-30 (35%); C7 2019-10-31 (72%); C7 2019-11-30 (46%); C2g 2019-04-30 (25%); C6 2019-02-28 (21%); C6 2019-06-30 (25%); C6 2019-10-31 (42%); C6 2019-11-30 (27%); C8 2019-01-31 (27%); C8 2019-02-28 (28%); C8 2019-04-30 (23%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-09-30 (61%); C8 2019-10-31 (88%); C8 2019-11-30 (38%); C3 2019-04-30 (21%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (37%); C9 2019-07-31 (35%); C9 2019-09-30 (53%); C9 2019-10-31 (76%); C9 2019-11-30 (38%); C4g 2019-10-31 (27%); C_IC1 2019-02-28 (55%); C_IC1 2019-03-31 (128%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 8 at risk (≥20% churn prob): C1 20%, C4 20%, C5 38%, C6 32%, C7 35%, C8 38%, C9 32%, C_IC1 23%

**Pricing & Margin**

- C1 (electricity): tariff £128.97-£162.68/MWh, net margin £58.09
- C1g (gas): tariff £26.00-£37.07/MWh, net margin £72.70
- C2 (electricity): tariff £142.94-£151.12/MWh, net margin £61.43
- C2g (gas): tariff £26.00-£37.88/MWh, net margin £33.47
- C3 (electricity): tariff £124.32-£128.73/MWh, net margin £-22.69 -- **net-negative**
- C3g (gas): tariff £23.83-£29.73/MWh, net margin £21.33
- C4 (electricity): tariff £128.09-£154.00/MWh, net margin £44.64
- C4g (gas): tariff £20.34-£34.63/MWh, net margin £35.24
- C5 (electricity): tariff £130.41-£163.06/MWh, net margin £178.98
- C6 (electricity): tariff £143.14-£152.57/MWh, net margin £38.76
- C7 (electricity): tariff £102.60-£227.85/MWh, net margin £69.22
- C8 (electricity): tariff £108.88-£211.40/MWh, net margin £116.26
- C9 (electricity): tariff £103.32-£207.68/MWh, net margin £162.56
- C_IC1 (electricity): tariff £0.00-£266.94/MWh, net margin £144,138.50
- C_IC2 (electricity): tariff £-60.00-£283.06/MWh, net margin £82,507.17
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £3,614.71
- C_IC3g (gas): tariff £27.53/MWh, net margin £796.93

**Portfolio Health**

- Capital cost ratio: 1.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.877, average bill shock 12.5%, bad debt provision £34,675.85, avg complaint probability 3.7%
- Solvency signal: £218,059/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £257,158.19 vs. naked (unhedged) net margin: £837,811.00
- hedging cost £580,652.81 vs. a fully unhedged book (commodity-only: actual net £257,158.19 vs. naked net £837,811.00)
  - C1: actual £4.14 vs. naked £322.97 -- hedging cost £318.83
  - C1g: actual £63.24 vs. naked £198.00 -- hedging cost £134.75
  - C2: actual £100.26 vs. naked £788.13 -- hedging cost £687.86
  - C2g: actual £13.39 vs. naked £222.05 -- hedging cost £208.65
  - C3: actual £-12.54 vs. naked £384.08 -- hedging cost £396.62
  - C3g: actual £48.06 vs. naked £206.04 -- hedging cost £157.97
  - C4: actual £34.93 vs. naked £513.45 -- hedging cost £478.51
  - C4g: actual £43.94 vs. naked £260.14 -- hedging cost £216.20
  - C5: actual £-76.69 vs. naked £1,518.60 -- hedging cost £1,595.29
  - C6: actual £169.72 vs. naked £2,034.71 -- hedging cost £1,864.99
  - C7: actual £36.28 vs. naked £1,093.60 -- hedging cost £1,057.32
  - C8: actual £179.50 vs. naked £1,272.20 -- hedging cost £1,092.70
  - C9: actual £171.01 vs. naked £1,235.66 -- hedging cost £1,064.65
  - C_IC1: actual £161,790.99 vs. naked £300,927.64 -- hedging cost £139,136.65
  - C_IC2: actual £90,180.30 vs. naked £165,284.43 -- hedging cost £75,104.13
  - C_IC3: actual £3,614.71 vs. naked £295,972.25 -- hedging cost £292,357.54
  - C_IC3g: actual £796.93 vs. naked £65,577.06 -- hedging cost £64,780.14

**Year narrative:** 2019 produced a net gain of £231,927.29 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-39,073.52 (gross £630,332.10, capital £7,399.49)
  - Electricity: gross £553,710.08, capital £2,014.11, net £-43,899.50
  - Gas: gross £76,622.02, capital £5,385.37, net £4,825.98
- Treasury at year end: £2,759,667.75
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.88 (avg 0.88), C6 0.86 (avg 0.86), C7 0.88 (avg 0.88), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2020-12-31 period 1, net margin £-484.00

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2020): £256,362.22
  - By billing account: C1 £2,109.76, C2 £5,312.44, C3 £2,082.42, C4 £3,807.13, C5 £7,934.44, C6 £8,759.62, C7 £5,348.08, C8 £6,611.63, C9 £5,832.97, C_IC1 £1,040,337.24, C_IC2 £551,264.96, C_IC3 £1,665,949.60, C_IC4 £27,358.56
- Bill shock events (>=20%): 31 -- C1 2020-04-30 (21%); C5 2020-04-30 (29%); C5 2020-10-31 (39%); C5 2020-12-31 (26%); C7 2020-04-30 (35%); C7 2020-05-31 (21%); C7 2020-06-30 (28%); C7 2020-10-31 (62%); C7 2020-11-30 (24%); C7 2020-12-31 (35%); C6 2020-04-30 (30%); C6 2020-09-30 (21%); C6 2020-10-31 (34%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (26%); C8 2020-06-30 (33%); C8 2020-09-30 (57%); C8 2020-10-31 (68%); C8 2020-12-31 (44%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-09-30 (47%); C9 2020-10-31 (51%); C9 2020-12-31 (37%); C_IC1 2020-03-31 (58%); C_IC1 2020-04-30 (77%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (123%); C_IC4 2020-12-31 (21%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 23%, C5 35%, C6 32%, C7 38%, C8 38%, C9 41%, C_IC4 23%

**Pricing & Margin**

- C1 (electricity): tariff £128.97-£137.89/MWh, net margin £3.76
- C1g (gas): tariff £25.00-£26.00/MWh, net margin £63.13
- C2 (electricity): tariff £143.89-£151.12/MWh, net margin £140.85
- C2g (gas): tariff £22.32-£26.00/MWh, net margin £60.07
- C3 (electricity): tariff £124.32/MWh, net margin £-6.61 -- **net-negative**
- C3g (gas): tariff £23.83/MWh, net margin £27.36
- C4 (electricity): tariff £123.00-£128.09/MWh, net margin £14.24
- C4g (gas): tariff £16.45-£20.34/MWh, net margin £25.91
- C5 (electricity): tariff £130.41-£142.56/MWh, net margin £-79.11 -- **net-negative**
- C6 (electricity): tariff £143.89-£152.57/MWh, net margin £225.41
- C7 (electricity): tariff £102.60-£217.74/MWh, net margin £37.98
- C8 (electricity): tariff £110.73-£212.15/MWh, net margin £285.03
- C9 (electricity): tariff £86.21-£197.25/MWh, net margin £99.06
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £59,291.44
- C_IC2 (electricity): tariff £-79.50-£283.06/MWh, net margin £47,511.53
- C_IC3 (electricity): tariff £38.67-£82.73/MWh, net margin £18,557.13
- C_IC3g (gas): tariff £15.93-£21.32/MWh, net margin £4,649.51
- C_IC4 (electricity): tariff £18.53-£73.19/MWh, net margin £-169,980.21 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.878, average bill shock 11.4%, bad debt provision £35,125.02, avg complaint probability 3.6%
- Solvency signal: £212,282/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-251,275.35 vs. naked (unhedged) net margin: £595,306.95
- hedging cost £846,582.30 vs. a fully unhedged book (commodity-only: actual net £-251,275.35 vs. naked net £595,306.95)
  - C1: actual £-57.71 vs. naked £13.88 -- hedging cost £71.59
  - C1g: actual £-49.88 vs. naked £-221.49 -- hedging added £171.61
  - C2: actual £138.32 vs. naked £686.15 -- hedging cost £547.83
  - C2g: actual £69.06 vs. naked £163.22 -- hedging cost £94.16
  - C4: actual £-68.85 vs. naked £248.84 -- hedging cost £317.69
  - C4g: actual £-98.62 vs. naked £-198.89 -- hedging added £100.27
  - C5: actual £-342.29 vs. naked £140.21 -- hedging cost £482.50
  - C6: actual £196.45 vs. naked £1,619.88 -- hedging cost £1,423.43
  - C7: actual £-97.79 vs. naked £266.06 -- hedging cost £363.85
  - C8: actual £308.02 vs. naked £1,084.43 -- hedging cost £776.42
  - C9: actual £-54.62 vs. naked £611.18 -- hedging cost £665.81
  - C_IC1: actual £41,109.86 vs. naked £134,127.22 -- hedging cost £93,017.36
  - C_IC2: actual £46,673.73 vs. naked £98,961.61 -- hedging cost £52,287.89
  - C_IC3: actual £-2,029.66 vs. naked £227,890.62 -- hedging cost £229,920.29
  - C_IC3g: actual £8,485.34 vs. naked £146,590.86 -- hedging cost £138,105.52
  - C_IC4: actual £-345,456.70 vs. naked £-16,676.84 -- hedging cost £328,779.86

**Year narrative:** 2020 produced a net loss of £-39,073.52 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 31 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-102,308.14 (gross £602,644.78, capital £15,970.04)
  - Electricity: gross £520,010.60, capital £5,747.28, net £-101,810.65
  - Gas: gross £82,634.18, capital £10,222.76, net £-497.49
- Treasury at year end: £2,618,313.05
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.91 (avg 0.91), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2021-12-31 period 1, net margin £-4,046.53

**Customer Book**

- Active accounts: 16 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £252,082.42
  - By billing account: C1 £1,741.83, C2 £4,861.27, C3 £1,812.42, C4 £2,885.42, C5 £6,438.41, C6 £8,759.41, C7 £4,746.28, C8 £6,250.66, C9 £4,989.04, C_IC1 £989,917.06, C_IC2 £554,057.06, C_IC3 £1,667,482.52, C_IC4 £23,130.05
- Bill shock events (>=20%): 38 -- C1 2021-04-30 (20%); C5 2021-05-31 (23%); C5 2021-06-30 (32%); C5 2021-10-31 (30%); C5 2021-11-30 (51%); C7 2021-05-31 (30%); C7 2021-06-30 (48%); C7 2021-10-31 (56%); C7 2021-11-30 (66%); C2g 2021-04-30 (27%); C6 2021-06-30 (36%); C6 2021-10-31 (28%); C6 2021-11-30 (51%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (25%); C8 2021-10-31 (69%); C8 2021-11-30 (84%); C9 2021-02-28 (22%); C9 2021-05-31 (25%); C9 2021-06-30 (51%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-10-31 (63%); C9 2021-11-30 (50%); C9 2021-12-31 (24%); C4 2021-10-31 (44%); C4g 2021-10-31 (63%); C_IC1 2021-05-31 (44%); C_IC2 2021-03-31 (27%); C_IC2 2021-04-30 (90%); C_IC3g 2021-09-30 (23%); C_IC3g 2021-10-31 (28%); C_IC3g 2021-12-31 (31%); C_IC4 2021-02-28 (28%); C_IC4 2021-07-31 (22%); C_IC4 2021-09-30 (40%); C_IC4 2021-12-31 (29%)
- Churn risk (accounts renewing in 2021): 8 at risk (≥20% churn prob): C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC4 32%

**Pricing & Margin**

- C1 (electricity): tariff £137.89/MWh, net margin £-57.23 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £-49.77 -- **net-negative**
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £133.59
- C2g (gas): tariff £22.32-£35.00/MWh, net margin £34.24
- C4 (electricity): tariff £123.00-£183.00/MWh, net margin £-163.05 -- **net-negative**
- C4g (gas): tariff £16.45-£35.00/MWh, net margin £-271.27 -- **net-negative**
- C5 (electricity): tariff £142.56/MWh, net margin £-339.12 -- **net-negative**
- C6 (electricity): tariff £143.89-£202.28/MWh, net margin £406.92
- C7 (electricity): tariff £114.06-£274.50/MWh, net margin £-108.15 -- **net-negative**
- C8 (electricity): tariff £111.13-£274.50/MWh, net margin £330.02
- C9 (electricity): tariff £86.21-£267.16/MWh, net margin £-26.76 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £33,804.72
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £60,852.94
- C_IC3 (electricity): tariff £43.33-£390.95/MWh, net margin £-20,674.48 -- **net-negative**
- C_IC3g (gas): tariff £21.32-£125.90/MWh, net margin £-210.70 -- **net-negative**
- C_IC4 (electricity): tariff £42.47-£336.77/MWh, net margin £-175,970.05 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.869, average bill shock 13.0%, bad debt provision £46,029.70, avg complaint probability 3.9%
- Solvency signal: £218,193/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-3,274.91 vs. naked (unhedged) net margin: £177,966.76
- hedging cost £181,241.68 vs. a fully unhedged book (commodity-only: actual net £-3,274.91 vs. naked net £177,966.76)
  - C2: actual £108.46 vs. naked £137.50 -- hedging cost £29.03
  - C2g: actual £8.11 vs. naked £-387.95 -- hedging added £396.07
  - C4: actual £-420.03 vs. naked £-303.64 -- hedging cost £116.39
  - C4g: actual £-791.90 vs. naked £-1,586.23 -- hedging added £794.33
  - C6: actual £429.67 vs. naked £164.92 -- hedging added £264.75
  - C7: actual £-1,810.99 vs. naked £-1,038.19 -- hedging cost £772.80
  - C8: actual £294.12 vs. naked £-13.65 -- hedging added £307.78
  - C9: actual £-21.58 vs. naked £-298.87 -- hedging added £277.30
  - C_IC1: actual £35,549.75 vs. naked £-59,643.45 -- hedging added £95,193.20
  - C_IC2: actual £70,290.91 vs. naked £24,995.80 -- hedging added £45,295.12
  - C_IC3: actual £114,565.71 vs. naked £237,439.90 -- hedging cost £122,874.18
  - C_IC3g: actual £-42,961.08 vs. naked £38,284.45 -- hedging cost £81,245.53
  - C_IC4: actual £-178,516.10 vs. naked £-59,783.81 -- hedging cost £118,732.29

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-102,308.14 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £108,572.03 (gross £878,199.89, capital £65,240.70)
  - Electricity: gross £787,633.21, capital £13,343.96, net £151,449.82
  - Gas: gross £90,566.68, capital £51,896.75, net £-42,877.78
- Treasury at year end: £2,619,087.70
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £2,728,762.56, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,779.89 / stressed £21,048.71) ratio 2.70
  - 2022-05-29: treasury £2,728,941.25, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,891.80 / stressed £21,078.69) ratio 2.70
  - 2022-06-28: treasury £2,728,932.39, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,891.80 / stressed £21,078.69) ratio 2.70
  - 2022-07-28: treasury £2,728,585.61, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,974.54 / stressed £21,095.07) ratio 2.70
  - 2022-08-27: treasury £2,728,552.43, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,974.54 / stressed £21,095.07) ratio 2.70
  - 2022-09-26: treasury £2,728,516.95, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,974.54 / stressed £21,095.07) ratio 2.70
  - 2022-10-26: treasury £2,726,340.32, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,032.87 / stressed £21,103.69) ratio 2.70
  - 2022-11-25: treasury £2,726,191.90, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,032.87 / stressed £21,103.69) ratio 2.70
  - 2022-12-25: treasury £2,725,939.02, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,032.87 / stressed £21,103.69) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC3g on 2022-12-31 period 1, net margin £-2,955.39

**Customer Book**

- Active accounts: 14 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £240,215.67
  - By billing account: C1 £2,142.42, C2 £3,736.35, C2_2 £488.20, C3 £1,982.77, C4 £1,708.20, C5 £6,204.29, C6 £9,458.37, C7 £3,855.89, C8 £5,535.19, C9 £5,236.41, C_IC1 £979,052.29, C_IC2 £562,968.53, C_IC3 £1,761,751.13, C_IC4 £18,899.39
- Bill shock events (>=20%): 54 -- C7 2022-01-31 (41%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (36%); C7 2022-06-30 (27%); C7 2022-09-30 (34%); C7 2022-11-30 (63%); C7 2022-12-31 (56%); C6 2022-04-30 (46%); C6 2022-05-31 (24%); C6 2022-09-30 (26%); C6 2022-11-30 (44%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (85%); C8 2022-11-30 (72%); C8 2022-12-31 (58%); C9 2022-04-30 (21%); C9 2022-05-31 (30%); C9 2022-06-30 (31%); C9 2022-09-30 (50%); C9 2022-10-31 (31%); C9 2022-11-30 (45%); C9 2022-12-31 (53%); C4 2022-10-31 (62%); C4g 2022-10-31 (121%); C_IC1 2022-06-30 (84%); C_IC2 2022-05-31 (59%); C_IC3 2022-01-31 (106%); C_IC3g 2022-03-31 (55%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (46%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-09-30 (21%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (21%); C_IC3g 2022-12-31 (21%); C_IC4 2022-02-28 (21%); C_IC4 2022-03-31 (44%); C_IC4 2022-05-31 (21%); C_IC4 2022-07-31 (38%); C_IC4 2022-08-31 (41%); C_IC4 2022-10-31 (39%); C_IC4 2022-12-31 (102%); C2_2 2022-04-30 (1712%); C2_2 2022-05-31 (39%); C2_2 2022-06-30 (33%); C2_2 2022-07-31 (20%); C2_2 2022-09-30 (78%); C2_2 2022-11-30 (65%); C2_2 2022-12-31 (58%)
- Churn risk (accounts renewing in 2022): 8 at risk (≥20% churn prob): C4 20%, C6 32%, C7 35%, C8 38%, C9 38%, C_IC1 20%, C_IC3 26%, C_IC4 38%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £-0.45 -- **net-negative**
- C2_2 (electricity): tariff £361.95/MWh, net margin £89.78
- C2g (gas): tariff £35.00/MWh, net margin £-13.00 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-473.87 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-994.85 -- **net-negative**
- C6 (electricity): tariff £202.28-£416.24/MWh, net margin £784.52
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,806.34 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-98.11 -- **net-negative**
- C9 (electricity): tariff £139.94-£392.52/MWh, net margin £-37.33 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£463.41/MWh, net margin £141,580.01
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £76,340.73
- C_IC3 (electricity): tariff £139.09-£390.95/MWh, net margin £113,539.34
- C_IC3g (gas): tariff £119.04-£125.90/MWh, net margin £-41,869.94 -- **net-negative**
- C_IC4 (electricity): tariff £71.50-£469.98/MWh, net margin £-178,468.46 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 7.4% of gross
- Treasury drawdown events (>=10% threshold): 49 -- £2,933,494.74 -> £2,619,029.55 (10.7%); £2,933,503.15 -> £2,619,040.81 (10.7%); £2,933,503.18 -> £2,619,074.78 (10.7%); £2,933,503.48 -> £2,619,074.78 (10.7%); £2,933,503.74 -> £2,619,074.79 (10.7%); £2,933,504.01 -> £2,619,074.80 (10.7%); £2,933,504.32 -> £2,619,074.85 (10.7%); £2,933,504.67 -> £2,619,074.87 (10.7%); £2,933,504.85 -> £2,619,076.39 (10.7%); £2,933,504.93 -> £2,619,081.07 (10.7%); £2,933,505.16 -> £2,619,081.11 (10.7%); £2,933,505.42 -> £2,619,081.15 (10.7%); £2,933,505.69 -> £2,619,081.18 (10.7%); £2,933,505.81 -> £2,619,084.98 (10.7%); £2,933,506.08 -> £2,619,085.00 (10.7%); £2,933,506.34 -> £2,619,085.00 (10.7%); £2,933,506.37 -> £2,619,085.01 (10.7%); £2,933,506.41 -> £2,619,085.01 (10.7%); £2,933,506.46 -> £2,619,085.11 (10.7%); £2,933,506.67 -> £2,619,085.15 (10.7%); £2,933,506.88 -> £2,619,085.20 (10.7%); £2,933,507.09 -> £2,619,085.25 (10.7%); £2,933,507.31 -> £2,619,085.28 (10.7%); £2,933,507.54 -> £2,619,085.31 (10.7%); £2,933,507.77 -> £2,619,085.34 (10.7%); £2,933,508.10 -> £2,619,085.84 (10.7%); £2,933,508.42 -> £2,619,085.87 (10.7%); £2,933,508.72 -> £2,619,085.88 (10.7%); £2,933,508.76 -> £2,619,085.88 (10.7%); £2,933,508.80 -> £2,619,085.88 (10.7%); £2,933,508.86 -> £2,619,085.98 (10.7%); £2,933,509.07 -> £2,619,086.00 (10.7%); £2,933,509.27 -> £2,619,086.04 (10.7%); £2,933,509.49 -> £2,619,086.07 (10.7%); £2,933,509.70 -> £2,619,086.11 (10.7%); £2,933,509.95 -> £2,619,086.14 (10.7%); £2,933,510.20 -> £2,619,086.17 (10.7%); £2,933,510.23 -> £2,619,086.52 (10.7%); £2,933,510.52 -> £2,619,086.57 (10.7%); £2,933,510.81 -> £2,619,086.57 (10.7%); £2,933,510.85 -> £2,619,086.58 (10.7%); £2,933,510.89 -> £2,619,086.58 (10.7%); £2,933,510.96 -> £2,619,086.70 (10.7%); £2,933,511.17 -> £2,619,086.73 (10.7%); £2,933,511.37 -> £2,619,086.76 (10.7%); £2,933,511.56 -> £2,619,086.80 (10.7%); £2,933,511.77 -> £2,619,086.83 (10.7%); £2,933,512.00 -> £2,619,086.88 (10.7%); £2,933,512.25 -> £2,618,997.92 (10.7%)
- Bills issued: 148, average clarity 0.811, average bill shock 32.3%, bad debt provision £81,898.11, avg complaint probability 5.3%
- Solvency signal: £238,099/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-74,825.82 vs. naked (unhedged) net margin: £892,502.20
- hedging cost £967,328.01 vs. a fully unhedged book (commodity-only: actual net £-74,825.82 vs. naked net £892,502.20)
  - C2_2: actual £115.33 vs. naked £1,470.79 -- hedging cost £1,355.46
  - C4: actual £-578.55 vs. naked £811.29 -- hedging cost £1,389.84
  - C4g: actual £-1,481.14 vs. naked £778.72 -- hedging cost £2,259.86
  - C6: actual £1,063.22 vs. naked £3,159.00 -- hedging cost £2,095.79
  - C7: actual £-344.19 vs. naked £2,087.74 -- hedging cost £2,431.93
  - C8: actual £-260.96 vs. naked £927.73 -- hedging cost £1,188.69
  - C9: actual £8.48 vs. naked £856.00 -- hedging cost £847.51
  - C_IC1: actual £224,313.85 vs. naked £256,882.03 -- hedging cost £32,568.18
  - C_IC2: actual £89,265.43 vs. naked £125,841.63 -- hedging cost £36,576.20
  - C_IC3: actual £-158,797.92 vs. naked £454,875.80 -- hedging cost £613,673.72
  - C_IC3g: actual £-28,776.23 vs. naked £83,300.79 -- hedging cost £112,077.02
  - C_IC4: actual £-199,353.13 vs. naked £-38,489.32 -- hedging cost £160,863.81

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £108,572.03 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 54 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £-128,600.52 (gross £726,842.66, capital £49,264.28)
  - Electricity: gross £605,270.73, capital £9,929.02, net £-98,303.26
  - Gas: gross £121,571.93, capital £39,335.26, net £-30,297.26
- Treasury at year end: £2,544,747.91
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C6 0.93 (avg 0.93), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £2,619,094.94, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £123,078.89 / stressed £44,568.75) ratio 2.76
  - 2023-02-23: treasury £2,619,103.01, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £123,078.89 / stressed £44,568.75) ratio 2.76
  - 2023-03-25: treasury £2,619,111.51, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £123,078.89 / stressed £44,568.75) ratio 2.76
  - 2023-04-24: treasury £2,701,508.69, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £129,926.79 / stressed £49,476.50) ratio 2.63
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-12-31 period 1, net margin £-3,472.88

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £232,147.24
  - By billing account: C1 £2,141.10, C2 £3,648.85, C2_2 £1,608.58, C3 £1,888.09, C4 £1,123.58, C5 £6,072.51, C6 £9,985.64, C7 £3,714.70, C8 £5,336.60, C9 £5,289.04, C_IC1 £1,022,239.98, C_IC2 £596,228.89, C_IC3 £1,572,561.61, C_IC4 £18,222.17
- Bill shock events (>=20%): 36 -- C7 2023-01-31 (41%); C7 2023-05-31 (32%); C7 2023-06-30 (37%); C7 2023-10-31 (57%); C7 2023-11-30 (73%); C6 2023-04-30 (29%); C6 2023-05-31 (24%); C6 2023-06-30 (23%); C6 2023-10-31 (39%); C6 2023-11-30 (44%); C8 2023-04-30 (31%); C8 2023-05-31 (41%); C8 2023-06-30 (44%); C8 2023-10-31 (101%); C8 2023-11-30 (70%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (23%); C9 2023-10-31 (77%); C9 2023-11-30 (55%); C4g 2023-10-31 (23%); C_IC1 2023-06-30 (56%); C_IC1 2023-07-31 (70%); C_IC2 2023-05-31 (56%); C_IC2 2023-06-30 (116%); C_IC3 2023-01-31 (21%); C_IC3g 2023-01-31 (34%); C_IC4 2023-01-31 (46%); C2_2 2023-04-30 (21%); C2_2 2023-05-31 (42%); C2_2 2023-06-30 (42%); C2_2 2023-10-31 (97%); C2_2 2023-11-30 (67%)
- Churn risk (accounts renewing in 2023): 6 at risk (≥20% churn prob): C2_2 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC4 32%

**Pricing & Margin**

- C2_2 (electricity): tariff £361.95-£367.05/MWh, net margin £601.35
- C4 (electricity): tariff £260.66-£305.00/MWh, net margin £-333.34 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,003.54 -- **net-negative**
- C6 (electricity): tariff £359.31-£416.24/MWh, net margin £1,288.55
- C7 (electricity): tariff £188.15-£457.50/MWh, net margin £-343.78 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-38.61 -- **net-negative**
- C9 (electricity): tariff £191.86-£392.52/MWh, net margin £208.80
- C_IC1 (electricity): tariff £-60.00-£463.41/MWh, net margin £169,551.37
- C_IC2 (electricity): tariff £-186.24-£471.87/MWh, net margin £87,898.04
- C_IC3 (electricity): tariff £101.61-£265.53/MWh, net margin £-157,726.38 -- **net-negative**
- C_IC3g (gas): tariff £60.60-£119.04/MWh, net margin £-29,293.72 -- **net-negative**
- C_IC4 (electricity): tariff £36.40-£169.32/MWh, net margin £-199,409.27 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 6.8% of gross
- Treasury drawdown events (>=10% threshold): 65 -- £2,933,508.24 -> £2,619,087.70 (10.7%); £2,933,508.46 -> £2,619,088.63 (10.7%); £2,933,508.64 -> £2,619,088.80 (10.7%); £2,933,508.68 -> £2,619,088.81 (10.7%); £2,933,508.71 -> £2,619,088.81 (10.7%); £2,933,508.83 -> £2,619,088.84 (10.7%); £2,933,508.97 -> £2,619,088.85 (10.7%); £2,933,509.12 -> £2,619,088.87 (10.7%); £2,933,509.28 -> £2,619,088.87 (10.7%); £2,933,509.45 -> £2,619,088.89 (10.7%); £2,933,509.63 -> £2,619,088.91 (10.7%); £2,933,509.71 -> £2,619,089.03 (10.7%); £2,933,509.94 -> £2,619,089.03 (10.7%); £2,933,509.97 -> £2,619,089.03 (10.7%); £2,933,510.01 -> £2,619,089.03 (10.7%); £2,933,510.16 -> £2,619,089.08 (10.7%); £2,933,510.32 -> £2,619,089.10 (10.7%); £2,933,510.49 -> £2,619,089.11 (10.7%); £2,933,510.66 -> £2,619,089.13 (10.7%); £2,933,510.86 -> £2,619,089.14 (10.7%); £2,933,511.05 -> £2,619,089.15 (10.7%); £2,933,511.08 -> £2,619,089.29 (10.7%); £2,933,511.33 -> £2,619,089.29 (10.7%); £2,933,511.36 -> £2,619,089.30 (10.7%); £2,933,511.39 -> £2,619,089.30 (10.7%); £2,933,511.55 -> £2,619,089.36 (10.7%); £2,933,511.73 -> £2,619,089.38 (10.7%); £2,933,511.91 -> £2,619,089.40 (10.7%); £2,933,512.09 -> £2,619,089.41 (10.7%); £2,933,512.28 -> £2,619,089.44 (10.7%); £2,933,512.49 -> £2,619,089.46 (10.7%); £2,933,512.61 -> £2,619,091.17 (10.7%); £2,933,512.79 -> £2,619,091.18 (10.7%); £2,933,512.97 -> £2,619,091.19 (10.7%); £2,933,513.16 -> £2,619,091.19 (10.7%); £2,933,513.37 -> £2,619,091.20 (10.7%); £2,933,513.58 -> £2,619,091.21 (10.7%); £2,933,513.63 -> £2,619,093.05 (10.7%); £2,933,513.73 -> £2,619,093.21 (10.7%); £2,933,514.09 -> £2,619,093.21 (10.7%); £2,933,514.12 -> £2,619,093.22 (10.7%); £2,933,514.15 -> £2,619,093.22 (10.7%); £2,933,514.21 -> £2,619,093.23 (10.7%); £2,933,514.45 -> £2,619,093.23 (10.7%); £2,933,514.69 -> £2,619,093.26 (10.7%); £2,933,514.96 -> £2,619,093.29 (10.7%); £2,933,515.23 -> £2,619,093.32 (10.7%); £2,933,515.54 -> £2,619,093.34 (10.7%); £2,933,515.86 -> £2,619,093.37 (10.7%); £2,933,516.06 -> £2,619,093.56 (10.7%); £2,933,516.46 -> £2,619,093.56 (10.7%); £2,933,516.50 -> £2,619,093.56 (10.7%); £2,933,516.53 -> £2,619,093.56 (10.7%); £2,933,516.60 -> £2,619,093.59 (10.7%); £2,933,516.86 -> £2,619,093.60 (10.7%); £2,933,517.13 -> £2,619,093.62 (10.7%); £2,933,517.39 -> £2,619,093.64 (10.7%); £2,933,517.67 -> £2,619,093.67 (10.7%); £2,933,518.00 -> £2,619,093.69 (10.7%); £2,933,518.33 -> £2,619,093.71 (10.7%); £2,933,518.47 -> £2,619,107.57 (10.7%); £2,933,518.71 -> £2,619,107.58 (10.7%); £2,933,519.00 -> £2,619,107.59 (10.7%); £2,933,519.28 -> £2,533,788.76 (13.6%); £2,957,240.48 -> £2,544,743.55 (13.9%)
- Bills issued: 144, average clarity 0.827, average bill shock 16.4%, bad debt provision £62,704.14, avg complaint probability 4.6%
- Solvency signal: £254,475/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £151,874.90 vs. naked (unhedged) net margin: £936,394.74
- hedging cost £784,519.85 vs. a fully unhedged book (commodity-only: actual net £151,874.90 vs. naked net £936,394.74)
  - C2_2: actual £953.93 vs. naked £2,390.03 -- hedging cost £1,436.11
  - C4: actual £297.44 vs. naked £959.16 -- hedging cost £661.72
  - C4g: actual £411.42 vs. naked £643.87 -- hedging cost £232.45
  - C6: actual £1,473.14 vs. naked £4,299.24 -- hedging cost £2,826.10
  - C7: actual £353.82 vs. naked £1,707.98 -- hedging cost £1,354.16
  - C8: actual £152.41 vs. naked £1,770.70 -- hedging cost £1,618.29
  - C9: actual £535.38 vs. naked £1,909.51 -- hedging cost £1,374.13
  - C_IC1: actual £151,701.09 vs. naked £292,930.05 -- hedging cost £141,228.95
  - C_IC2: actual £98,604.50 vs. naked £165,720.39 -- hedging cost £67,115.89
  - C_IC3: actual £162,058.13 vs. naked £433,659.05 -- hedging cost £271,600.92
  - C_IC3g: actual £-35,503.62 vs. naked £77,607.60 -- hedging cost £113,111.22
  - C_IC4: actual £-229,162.74 vs. naked £-47,202.85 -- hedging cost £181,959.89

**Year narrative:** 2023 produced a net loss of £-128,600.52 across 12 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 36 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £107,221.63 (gross £1,071,371.76, capital £55,804.21)
  - Electricity: gross £947,243.39, capital £9,892.41, net £142,721.21
  - Gas: gross £124,128.37, capital £45,911.80, net £-35,499.58
- Treasury at year end: £2,696,199.37
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.90 (avg 0.90), C4 0.86 (avg 0.86), C4g 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 5
  - 2024-01-19: treasury £2,544,844.60, C2->1.00, VaR (current £91,670.98 / stressed £52,115.60) ratio 1.76
  - 2024-02-18: treasury £2,544,962.91, C2->1.00, VaR (current £91,670.98 / stressed £52,115.60) ratio 1.76
  - 2024-03-19: treasury £2,545,085.67, C2->1.00, VaR (current £91,670.98 / stressed £52,115.60) ratio 1.76
  - 2024-04-18: treasury £2,626,370.70, C2->1.00, VaR (current £82,944.31 / stressed £62,981.52) ratio 1.32
  - 2024-05-18: treasury £2,634,236.31, C2->1.00, VaR (current £82,944.31 / stressed £62,981.52) ratio 1.32
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 1.58
- Worst single period: C_IC3g on 2024-12-30 period 1, net margin £-1,913.18

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £249,767.80
  - By billing account: C1 £2,157.60, C2 £3,742.78, C2_2 £2,409.53, C3 £1,871.18, C4 £1,911.84, C5 £5,971.58, C6 £9,650.45, C7 £4,266.54, C8 £5,661.87, C9 £5,696.15, C_IC1 £1,056,357.28, C_IC2 £632,747.19, C_IC3 £1,745,331.68, C_IC4 £18,973.49
- Bill shock events (>=20%): 29 -- C7 2024-02-29 (27%); C7 2024-05-31 (38%); C7 2024-09-30 (36%); C7 2024-10-31 (39%); C7 2024-11-30 (50%); C8 2024-02-29 (23%); C8 2024-04-30 (34%); C8 2024-05-31 (50%); C8 2024-07-31 (28%); C8 2024-09-30 (81%); C8 2024-10-31 (37%); C8 2024-11-30 (64%); C9 2024-05-31 (50%); C9 2024-07-31 (31%); C9 2024-09-30 (59%); C9 2024-10-31 (23%); C9 2024-11-30 (49%); C_IC1 2024-07-31 (37%); C_IC1 2024-08-31 (74%); C_IC2 2024-06-30 (52%); C_IC2 2024-07-31 (122%); C_IC4 2024-05-31 (25%); C2_2 2024-02-29 (23%); C2_2 2024-04-30 (46%); C2_2 2024-05-31 (50%); C2_2 2024-07-31 (27%); C2_2 2024-09-30 (72%); C2_2 2024-10-31 (36%); C2_2 2024-11-30 (60%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C6 38%, C7 35%, C8 41%, C9 38%, C_IC4 26%

**Pricing & Margin**

- C2_2 (electricity): tariff £229.60-£367.05/MWh, net margin £530.48
- C4 (electricity): tariff £203.55-£260.66/MWh, net margin £204.98
- C4g (gas): tariff £55.00-£66.00/MWh, net margin £357.52
- C6 (electricity): tariff £359.31/MWh, net margin £512.85
- C7 (electricity): tariff £165.00-£359.19/MWh, net margin £352.64
- C8 (electricity): tariff £165.00-£397.50/MWh, net margin £229.95
- C9 (electricity): tariff £165.00-£366.28/MWh, net margin £424.21
- C_IC1 (electricity): tariff £-98.58-£334.24/MWh, net margin £134,200.87
- C_IC2 (electricity): tariff £-106.92-£357.08/MWh, net margin £73,995.30
- C_IC3 (electricity): tariff £91.19-£193.99/MWh, net margin £162,249.50
- C_IC3g (gas): tariff £55.64-£60.60/MWh, net margin £-35,857.09 -- **net-negative**
- C_IC4 (electricity): tariff £23.97-£113.12/MWh, net margin £-229,979.56 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 5.2% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £2,957,154.97 -> £2,544,747.93 (13.9%)
- Bills issued: 135, average clarity 0.832, average bill shock 15.3%, bad debt provision £54,970.06, avg complaint probability 4.4%
- Solvency signal: £269,620/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £96,616.85 vs. naked (unhedged) net margin: £464,652.37
- hedging cost £368,035.51 vs. a fully unhedged book (commodity-only: actual net £96,616.85 vs. naked net £464,652.37)
  - C2_2: actual £241.06 vs. naked £1,126.74 -- hedging cost £885.68
  - C4: actual £-16.33 vs. naked £388.67 -- hedging cost £405.00
  - C4g: actual £98.19 vs. naked £151.09 -- hedging cost £52.90
  - C7: actual £-81.65 vs. naked £555.29 -- hedging cost £636.94
  - C8: actual £243.78 vs. naked £1,249.75 -- hedging cost £1,005.97
  - C9: actual £230.83 vs. naked £1,217.40 -- hedging cost £986.57
  - C_IC1: actual £125,735.26 vs. naked £218,723.34 -- hedging cost £92,988.08
  - C_IC2: actual £66,423.61 vs. naked £116,615.17 -- hedging cost £50,191.56
  - C_IC3: actual £26,267.40 vs. naked £125,547.37 -- hedging cost £99,279.96
  - C_IC3g: actual £-22,784.50 vs. naked £25,544.36 -- hedging cost £48,328.86
  - C_IC4: actual £-99,740.80 vs. naked £-26,466.80 -- hedging cost £73,273.99

**Year narrative:** 2024 produced a net gain of £107,221.63 across 12 accounts. The risk committee intervened 5 time(s), raising hedge fractions in response to elevated VaR. 29 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £9,504.16 (gross £434,761.43, capital £29,132.25)
  - Electricity: gross £382,496.04, capital £5,832.18, net £28,399.88
  - Gas: gross £52,265.38, capital £23,300.07, net £-18,895.71
- Treasury at year end: £2,752,309.95
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2025-06-01 period 1, net margin £-527.05

**Customer Book**

- Active accounts: 11 (C2_2, C4, C4g, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 0, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £265,809.34
  - By billing account: C1 £2,087.64, C2 £3,450.22, C2_2 £2,543.71, C3 £1,785.92, C4 £2,031.15, C5 £5,971.58, C6 £9,762.16, C7 £4,589.12, C8 £5,233.45, C9 £5,491.57, C_IC1 £1,103,328.67, C_IC2 £663,440.72, C_IC3 £1,891,109.87, C_IC4 £20,504.94
- Bill shock events (>=20%): 23 -- C7 2025-04-30 (37%); C7 2025-05-31 (24%); C7 2025-06-07 (80%); C8 2025-01-31 (40%); C8 2025-02-28 (24%); C8 2025-04-30 (42%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (34%); C9 2025-06-07 (71%); C4 2025-06-07 (78%); C4g 2025-06-07 (77%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (81%); C2_2 2025-01-31 (39%); C2_2 2025-02-28 (24%); C2_2 2025-05-31 (37%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £229.60-£326.51/MWh, net margin £195.98
- C4 (electricity): tariff £203.55/MWh, net margin £-11.48 -- **net-negative**
- C4g (gas): tariff £55.00/MWh, net margin £62.43
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-77.59 -- **net-negative**
- C8 (electricity): tariff £149.29-£315.00/MWh, net margin £39.24
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £128.20
- C_IC1 (electricity): tariff £169.74-£324.06/MWh, net margin £68,096.11
- C_IC2 (electricity): tariff £163.52-£312.18/MWh, net margin £32,332.78
- C_IC3 (electricity): tariff £91.19-£174.09/MWh, net margin £26,118.54
- C_IC3g (gas): tariff £55.64/MWh, net margin £-18,958.15 -- **net-negative**
- C_IC4 (electricity): tariff £43.11-£193.69/MWh, net margin £-98,421.92 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 6.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 66, average clarity 0.794, average bill shock 23.9%, bad debt provision £24,177.63, avg complaint probability 5.8%
- Solvency signal: £305,812/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £44.55 vs. naked (unhedged) net margin: £309.23
- hedging cost £264.68 vs. a fully unhedged book (commodity-only: actual net £44.55 vs. naked net £309.23)
  - C2_2: actual £107.28 vs. naked £233.23 -- hedging cost £125.96
  - C8: actual £-62.73 vs. naked £75.99 -- hedging cost £138.72

**Year narrative:** 2025 produced a net gain of £9,504.16 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 23 customer(s) experienced a bill shock of >=20%.
