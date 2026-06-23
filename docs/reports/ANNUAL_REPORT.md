# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,145,223.83
  (£678,587.61 net change)
- Solvency signal (final year): £391,415/customer (8 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £18,242,335.98
  VAT remitted to HMRC: (£877,189.82) | Revenue (ex-VAT): £17,365,146.16
  Non-commodity pass-through: (£4,015,486.66)
- Gross margin: £5,482,354.77
- Capital costs: £63,846.87
- Net margin: £5,418,507.89
- Capital cost ratio: 1.2% of gross
- Net margin as % of revenue: 31.2%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1569, average clarity 0.866,
  service quality score 0.921
- Enterprise value (CLV sum across 13 billing accounts): £5,832,370.01
- Cost to serve (whole portfolio): £87,329.42, net margin after cost to serve: £5,331,178.47
- Hedge effectiveness (whole window): hedging cost £3,768,355.54 vs. a fully unhedged book (commodity-only: actual net £678,587.61 vs. naked net £4,446,943.16)

- **2021** (crisis year): net margin £68,421.49, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £-9,239.70, 9 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £5,482,354.77, capital £63,846.87, net £5,418,507.89. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 1.2% (commodity basis, comparable to old model) / 1.2% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £68,421.49 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 31.2%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £5,418,507.89
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £4,446,943.16
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £3,768,355.54 vs. a fully unhedged book (commodity-only: actual net £678,587.61 vs. naked net £4,446,943.16)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £123,063.99 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £604,544.62 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £113.75 | £462.97 | £160.66 | £737.38 |
| 2017 | £46,798.37 | £0.00 | £235.17 | £715.93 | £202.10 | £47,951.56 |
| 2018 | £88,211.53 | £0.00 | £-180.64 | £526.56 | £175.98 | £88,733.44 |
| 2019 | £251,179.94 | £-36,112.79 | £296.66 | £934.65 | £440.00 | £216,738.45 |
| 2020 | £-10,574.50 | £-5,116.89 | £378.26 | £992.02 | £314.10 | £-14,007.01 |
| 2021 | £-57,752.82 | £125,577.06 | £170.43 | £603.45 | £-176.63 | £68,421.49 |
| 2022 | £-53,693.88 | £43,790.89 | £476.17 | £228.82 | £-41.70 | £-9,239.70 |
| 2023 | £415,828.61 | £-253,415.10 | £1,248.25 | £3,440.85 | £1,425.55 | £168,528.16 |
| 2024 | £134,007.64 | £-17,341.82 | £577.34 | £2,838.44 | £791.24 | £120,872.84 |
| 2025 | £-7,481.70 | £-3,756.29 | £0.00 | £966.43 | £122.56 | £-10,149.01 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **51** renewals.  Lost (churned): **5** accounts.

Accounts lost before end of window: C1, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8255 |
| C_IC1 | 2018-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3902 |
| C1 | 2018-12-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6312 |
| C_IC2 | 2019-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3710 |
| C1 | 2019-12-31 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.0800 | 0.5500 | 0.9640 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2600 | 0.5500 | 0.8830 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.1700 | 0.5500 | 0.9235 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.5838 |
| C2 | 2022-03-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.8723 |
| C2 | 2023-03-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6357 |
| C6 | 2023-03-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.7019 |
| C2 | 2024-03-30 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.8119 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.2600 | 0.5500 | 0.8830 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.3751 |
| C2 | 2025-03-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.1514 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 196.6%
- **Average signed error:** +63.8% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -61.3% | 61.3% |
| 2017 | 3 | -90.3% | 90.3% |
| 2018 | 4 | +434.4% | 508.8% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | -11.5% | 150.5% |
| 2021 | 9 | -1.5% | 96.4% |
| 2022 | 7 | -7.2% | 100.8% |
| 2023 | 7 | +189.8% | 332.6% |
| 2024 | 7 | -31.0% | 124.6% |
| 2025 | 2 | -70.1% | 70.1% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 32.8%, abs error 237.6%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 10.2%, abs error 178.7%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 6.0% | 0.0% | 61.3% |
| 2017 | 0 | 3 | 0.0% | 2.4% | 0.0% | 90.3% |
| 2018 | 2 | 2 | 18.3% | 49.7% | 73.5% | 944.1% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 17.7% | 0.4% | 203.8% | 97.2% |
| 2021 | 3 | 6 | 61.1% | 4.9% | 142.3% | 73.4% |
| 2022 | 0 | 7 | 0.0% | 20.7% | 0.0% | 100.8% |
| 2023 | 1 | 6 | 37.2% | 15.8% | 28.4% | 383.3% |
| 2024 | 3 | 4 | 35.3% | 0.2% | 158.1% | 99.5% |
| 2025 | 1 | 1 | 11.1% | 1.6% | 44.5% | 95.8% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 12 (31%)
- **Below/at SVT (protected):** 27 (69%)
- **Mean rate vs SVT premium:** -3.3%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -1.8% | 137.5 | 140.0 |
| 2017 | 3 | 0 (0%) | -8.1% | 128.7 | 140.0 |
| 2018 | 2 | 1 (50%) | -1.7% | 149.9 | 152.5 |
| 2019 | 2 | 0 (0%) | -25.1% | 133.7 | 178.5 |
| 2020 | 5 | 0 (0%) | -22.8% | 136.4 | 176.9 |
| 2021 | 6 | 5 (83%) | +9.0% | 200.8 | 183.8 |
| 2022 | 7 | 5 (71%) | +30.4% | 353.5 | 318.4 |
| 2023 | 6 | 0 (0%) | -31.8% | 269.4 | 415.0 |
| 2024 | 4 | 0 (0%) | -5.4% | 233.3 | 246.9 |
| 2025 | 1 | 1 (100%) | +15.7% | 287.6 | 248.6 |

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
| 2016 | 17 | 17.5% | 49.4% |
| 2017 | 14 | 15.0% | 30.6% |
| 2018 | 16 | 11.8% | 35.0% |
| 2019 | 19 | 24.1% | 67.6% |
| 2020 | 22 | 19.9% | 65.5% |
| 2021 | 17 | 17.0% | 34.9% |
| 2022 | 15 | 16.5% | 74.2% |
| 2023 | 15 | 41.4% | 164.9% |
| 2024 | 14 | 13.1% | 71.7% |
| 2025 | 3 | 13.4% | 27.4% |

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
| 2016 | 3 | 0.61× | 0.80× |
| 2017 | 3 | 0.90× | 0.93× |
| 2018 | 4 | 5.09× ⚠ | 18.00× |
| 2019 | 4 | 5.25× ⚠ | 18.00× |
| 2020 | 10 | 1.50× | 6.95× |
| 2021 | 9 | 0.96× | 3.75× |
| 2022 | 7 | 1.01× | 2.28× |
| 2023 | 7 | 3.33× ⚠ | 18.00× |
| 2024 | 7 | 1.25× | 3.28× |
| 2025 | 2 | 0.70× | 0.96× |

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
| 2019 | 11 | 1.0% | 5.1% |
| 2020 | 13 | 0.7% | 3.5% |
| 2021 | 11 | 1.0% | 4.2% |
| 2022 | 9 | 1.9% | 7.5% |
| 2023 | 9 | 1.5% | 4.5% |
| 2024 | 9 | 1.6% | 4.4% |
| 2025 | 2 | 0.4% | 0.8% |

**86** of **86** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **5** (5 churn, 0 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.08, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.17, company est=0.08 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.46 |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.20 |
| 2024-09-29 | CHURN | C4 | SIM p=0.26, company est=0.00 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 1 accounts | 0 active | yes |
| 2021-12-31 | 3 accounts | 0 active | yes |
| 2022-12-31 | 3 accounts | 0 active | yes |
| 2023-12-31 | 3 accounts | 0 active | yes |
| 2024-12-31 | 5 accounts | 0 active | yes |
| 2025-12-31 | 5 accounts | 0 active | yes |

## Policy Costs — RO + CfD + CCL + CM + FiT (Phase 21a/27b/30a/31a)

Electricity policy costs deducted from net_margin_gbp each year. 
CfD levy was NEGATIVE in 2022 (crisis rebate from LCCC). 
CCL applies to business (SME/I&C) only — resi exempt. 
CM (Capacity Market) and FiT (Feed-in Tariff) levies apply to ALL demand including domestic.

| Year | RO levy £ | CfD levy £ | CCL £ | CM levy £ | FiT levy £ | Total policy cost £ | Note |
|------|-----------|------------|-------|-----------|------------|---------------------|------|
| 2016 | 1,104 | 7 | 172 | 35 | 290 | 1,608 |  |
| 2017 | 37,269 | 2,715 | 11,202 | 1,981 | 9,969 | 63,137 |  |
| 2018 | 65,812 | 9,922 | 17,517 | 9,388 | 17,364 | 120,002 |  |
| 2019 | 164,971 | 28,414 | 42,552 | 32,030 | 44,393 | 312,360 |  |
| 2020 | 239,072 | 35,456 | 69,576 | 56,656 | 70,153 | 470,913 |  |
| 2021 | 248,969 | 15,148 | 72,020 | 50,135 | 63,418 | 449,690 |  |
| 2022 | 259,194 | -50,324 | 71,821 | 37,156 | 69,881 | 387,728 | ⬇ CfD REBATE |
| 2023 | 274,436 | 65,395 | 72,466 | 51,376 | 75,814 | 539,487 |  |
| 2024 | 310,557 | 111,001 | 73,601 | 69,353 | 83,353 | 647,864 |  |
| 2025 | 137,626 | 47,607 | 31,649 | 31,464 | 36,657 | 285,003 |  |
| **Total** | **1,739,010** | **265,340** | **462,576** | **339,574** | **471,293** | **3,277,793** | |

Total policy cost: £3,277,793 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

## Network Charges — DUoS + TNUoS (Phase 29a)

Electricity network charges deducted from net_margin_gbp each year. 
Resi/SME: combined DUoS + TNUoS unit rate (largest single non-commodity cost). 
I&C HV: DUoS only (Triad TNUoS is an annual lump tracked in the Triad section).

| Year | Network cost £ | Note |
|------|----------------|------|
| 2016 | 3,043 |  |
| 2017 | 26,092 |  |
| 2018 | 38,575 |  |
| 2019 | 88,411 |  |
| 2020 | 124,685 |  |
| 2021 | 124,577 |  |
| 2022 | 134,357 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 139,924 | RIIO-ED2 from Apr 2023 |
| 2024 | 144,172 |  |
| 2025 | 61,791 |  |
| **Total** | **885,627** | |

Total network cost: £885,627 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

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
| 2022 | 27,136 | 54,538 | 81,674 |
| 2023 | 32,320 | 80,454 | 112,774 |
| 2024 | 37,573 | 76,290 | 113,863 |
| 2025 | 16,774 | 31,044 | 47,818 |
| **Total** | **171,121** | **391,320** | **562,441** |

Gas policy pass-through in tariff unit rate (CCL + GGL at term start); gas network pass-through likewise. Net basis risk near-zero for annual contracts.


## Gas Book P&L — Year by Year (Phase 32a)

Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.
Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.

| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |
|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|
| 2016 | 948 | 426 | 522 | 0 | 356 | 5 | 161 | +16.9% |
| 2017 | 1,684 | 848 | 836 | 0 | 624 | 10 | 202 | +12.0% |
| 2018 | 2,001 | 1,201 | 800 | 0 | 609 | 15 | 176 | +8.8% |
| 2019 | 136,258 | 105,132 | 31,127 | 15,273 | 50,131 | 1,395 | -35,673 | -26.2% |
| 2020 | 119,813 | 57,391 | 62,422 | 19,520 | 46,890 | 814 | -4,803 | -4.0% |
| 2021 | 296,733 | 97,288 | 199,446 | 22,523 | 50,386 | 1,136 | 125,400 | +42.3% |
| 2022 | 596,030 | 468,121 | 127,910 | 27,136 | 54,538 | 2,486 | 43,749 | +7.3% |
| 2023 | 298,987 | 437,786 | -138,799 | 32,320 | 80,454 | 416 | -251,990 | -84.3% |
| 2024 | 271,332 | 169,202 | 102,130 | 37,573 | 76,290 | 4,818 | -16,551 | -6.1% |
| 2025 | 128,784 | 81,097 | 47,687 | 16,774 | 31,044 | 3,504 | -3,634 | -2.8% |
| **Total** | **1,852,572** | **1,418,491** | **434,081** | **171,121** | **391,320** | **14,601** | **-142,961** | **-7.7%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b)

Treasury balance ÷ active billing accounts at each year-end.
Ofgem licence floor: £0/account (positive net assets required to hold a supply licence).
Capital adequacy target: £130/dual-fuel billing account.

| Year | Treasury £ | Billing Accounts | Net Assets/Account £ | vs Floor | vs £130 Target |
|------|-----------|-----------------|----------------------|----------|----------------|
| 2016 | 2,467,024 | 9 | 274,114 | OK | OK |
| 2017 | 2,514,878 | 10 | 251,488 | OK | OK |
| 2018 | 2,510,612 | 11 | 228,237 | OK | OK |
| 2019 | 2,642,304 | 12 | 220,192 | OK | OK |
| 2020 | 2,747,139 | 13 | 211,318 | OK | OK |
| 2021 | 2,784,668 | 12 | 232,056 | OK | OK |
| 2022 | 2,637,120 | 10 | 263,712 | OK | OK |
| 2023 | 2,789,811 | 10 | 278,981 | OK | OK |
| 2024 | 3,071,293 | 10 | 307,129 | OK | OK |
| 2025 | 3,131,320 | 8 | 391,415 | OK | OK |

End-state (2025): **£391,415/account** across 8 billing accounts — above Ofgem £130 target.




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,842 | 40,643 | 33.6% | £11,513.67 | £11,942.53 | £283.29/MWh | £148.91/MWh | +2.8% |
| C8 | 106,723 | 46,761 | 43.8% | £14,390.89 | £9,688.21 | £307.75/MWh | £161.57/MWh | +10.0% |
| C9 | 109,388 | 46,156 | 42.2% | £12,420.20 | £8,909.25 | £269.09/MWh | £140.90/MWh | +8.7% |

Total HH revenue: £68,864.75 vs flat equivalent £64,341.80 (+7.0% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 21 | 110% | C8 (2016-10-31) |
| 2017 | 27 | 85% | C8 (2017-11-30) |
| 2018 | 34 | 57% | C8 (2018-10-31) |
| 2019 | 35 | 128% | C_IC1 (2019-03-31) |
| 2020 | 33 | 137% | C_IC2 (2020-03-31) |
| 2021 | 38 | 145% | C4g (2021-10-31) |
| 2022 | 51 | 159% | C4g (2022-10-31) |
| 2023 | 31 | 137% | C_IC2 (2023-06-30) |
| 2024 | 26 | 124% | C_IC2 (2024-07-31) |
| 2025 | 20 | 81% | C_IC4 (2025-06-07) |

Total: **316** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-10-31 | C4g | +159% | no |
| 2022-04-30 | C2g | +152% | no |
| 2021-10-31 | C4g | +145% | no |
| 2020-03-31 | C_IC2 | +137% | no |
| 2023-06-30 | C_IC2 | +137% | no |
| 2019-03-31 | C_IC1 | +128% | no |
| 2024-07-31 | C_IC2 | +124% | no |
| 2016-10-31 | C8 | +110% | no |
| 2023-07-31 | C_IC1 | +107% | no |
| 2023-10-31 | C8 | +103% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 12% | 12% | 0 |
| 2017 | 4 | 14% | 24% | 1 ⚠ |
| 2018 | 4 | 20% | 22% | 2 ⚠ |
| 2019 | 4 | 2% | 8% | 0 |
| 2020 | 5 | 1% | 4% | 0 |
| 2021 | 3 | 71% | 95% | 3 ⚠ |
| 2022 | 3 | 83% | 95% | 3 ⚠ |
| 2023 | 3 | 6% | 18% | 0 |
| 2024 | 2 | 0% | 0% | 0 |
| 2025 | 1 | 4% | 4% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-09-30 | C4g | £15.7 | £60.4 (+284%) | 95% |
| 2021-12-31 | C_IC3g | £16.1 | £84.5 (+426%) | 95% |
| 2022-03-31 | C2g | £32.7 | £117.8 (+260%) | 95% |
| 2022-09-30 | C4g | £60.4 | £182.8 (+203%) | 95% |
| 2022-12-31 | C_IC3g | £84.5 | £160.2 (+90%) | 58% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 20 |
| Retained | 19 (95%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £456,538.22 |
| Margin saved (retained customers' terms) | £2,270,777.64 |
| Wasted offer cost (churned anyway) | £148.00 |
| **Net ROI of retention strategy** | **£1,814,239.42** |
| Acquisition cost avoided (retained customers) | £3,100.00 |
| **Full economic ROI (margin + acq savings)** | **£1,817,339.42** |

Missed opportunities (churns with no offer): **4** (£4,338.92 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 4 (£4,338.92 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £22372.83 | £158277.88 | £135905.05 | £0.00 |
| 2019 | 2 | 2 | £42395.91 | £300255.41 | £257859.50 | £0.00 |
| 2020 | 4 | 4 | £33433.88 | £274344.38 | £240910.50 | £372.36 |
| 2021 | 5 | 4 | £91077.69 | £316908.41 | £225830.71 | £344.82 |
| 2022 | 3 | 3 | £163967.19 | £401275.01 | £237307.82 | £0.00 |
| 2023 | 3 | 3 | £60191.28 | £411051.81 | £350860.53 | £0.00 |
| 2024 | 2 | 2 | £43099.43 | £408664.74 | £365565.31 | £3621.74 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £22372.83 | £158277.88 | £150 | £135905.05 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14513.38 | £102925.90 | £150 | £88412.52 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £27882.53 | £197329.50 | £150 | £169446.98 | retained |
| 2020-01-01 | C_IC3 | 0.38 | 3% | £5972.37 | £14258.29 | £150 | £8285.92 | retained |
| 2020-03-01 | C_IC2 | 0.35 | 3% | £4215.62 | £94046.96 | £150 | £89831.33 | retained |
| 2020-03-31 | C_IC1 | 0.57 | 5% | £11678.17 | £139714.48 | £150 | £128036.31 | retained |
| 2020-12-31 | C_IC3 | 0.64 | 5% | £11567.71 | £26324.65 | £150 | £14756.94 | retained |
| 2021-03-31 | C_IC2 | 0.64 | 5% | £8124.21 | £89629.89 | £150 | £81505.68 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £24101.55 | £166030.33 | £150 | £141928.78 | retained |
| 2021-12-30 | C5 | 0.46 | 3% | £148.00 | £1794.68 | £400 | £-148.00 | churned_despite_offer |
| 2021-12-30 | C7 | 0.42 | 3% | £102.54 | £1182.47 | £150 | £1079.93 | retained |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £58601.40 | £60065.72 | £150 | £1464.33 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25059.51 | £72921.46 | £150 | £47861.95 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £50058.09 | £194288.43 | £150 | £144230.34 | retained |
| 2022-12-31 | C_IC3 | 0.95 | 8% | £88849.59 | £134065.12 | £150 | £45215.53 | retained |
| 2023-03-31 | C6 | 0.37 | 3% | £204.86 | £2647.09 | £400 | £2442.23 | retained |
| 2023-05-30 | C_IC2 | 0.68 | 5% | £13376.09 | £135541.27 | £150 | £122165.18 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £46610.33 | £272863.45 | £150 | £226253.12 | retained |
| 2024-06-28 | C_IC2 | 0.51 | 5% | £10438.12 | £137513.97 | £150 | £127075.85 | retained |
| 2024-07-28 | C_IC1 | 0.95 | 8% | £32661.31 | £271150.77 | £150 | £238489.46 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C_IC1 | 2018-01-31 | (window end) | 95 | active |
| C_IC2 | 2019-01-31 | (window end) | 83 | active |
| C_IC3 | 2020-01-01 | (window end) | 72 | active |
| C5 | 2021-12-30 | 2021-12-30 | 0 | churned |
| C7 | 2021-12-30 | (window end) | 48 | active |
| C6 | 2023-03-31 | 2024-03-30 | 12 | churned |

**Eventually churned (2/6)**: C5, C6 — avg 6 months post-retention before final churn.
**Still active (4/6)**: C_IC1, C_IC2, C_IC3, C7 — survived to simulation end.

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £5,832,370.01 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £301,649.99 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £737.38 |
| 2017 | £47,951.56 |
| 2018 | £88,733.44 |
| 2019 | £216,738.45 |
| 2020 | £-14,007.01 |
| 2021 | £68,421.49 |
| 2022 | £-9,239.70 |
| 2023 | £168,528.16 | ← trailing
| 2024 | £120,872.84 | ← trailing
| 2025 | £-10,149.01 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £2,765.47 | — |
| C2 | £9,379.46 | £3,310.84 |
| C3 | £3,076.71 | — |
| C4 | £4,994.10 | £809.74 |
| C5 | £9,896.01 | — |
| C6 | £15,236.41 | £2,945.75 |
| C7 | £8,808.48 | £1,242.58 |
| C8 | £10,016.24 | £2,767.32 |
| C9 | £10,858.52 | £2,450.32 |
| C_IC1 | £1,834,787.84 | £571,581.78 |
| C_IC2 | £1,068,898.92 | £255,199.57 |
| C_IC3 | £2,825,368.71 | £23,756.67 |
| C_IC4 | £28,283.12 | £-562,414.58 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £1,782.56 | — | — | — | £5,242.98 | — | £4,353.87 | — | — | — | — | — | — |
| 2017 | £2,016.66 | £6,069.81 | £2,782.92 | £3,690.43 | £7,107.63 | £10,775.91 | £4,690.29 | £8,195.43 | £6,108.67 | — | — | — | — |
| 2018 | £2,062.28 | £5,013.42 | £2,753.14 | £3,150.95 | £6,193.58 | £7,871.99 | £4,664.48 | £6,568.30 | £6,032.37 | £1,548,973.45 | — | — | — |
| 2019 | £2,002.63 | £4,925.00 | £2,463.48 | £3,186.21 | £6,824.88 | £8,849.66 | £5,101.76 | £6,033.91 | £6,919.74 | £1,213,609.45 | £927,125.34 | — | — |
| 2020 | £2,108.63 | £5,308.13 | £2,289.12 | £2,913.48 | £7,341.42 | £8,959.17 | £4,888.42 | £6,215.33 | £6,163.99 | £910,253.30 | £550,780.31 | £1,617,738.39 | £25,585.19 |
| 2021 | £1,953.84 | £4,791.45 | £2,085.18 | £2,644.54 | £6,081.40 | £8,547.49 | £4,779.15 | £6,024.27 | £5,088.63 | £809,116.41 | £507,277.61 | £1,562,198.90 | £20,346.53 |
| 2022 | £1,703.89 | £4,621.27 | £2,103.29 | £2,251.19 | £6,161.12 | £8,298.97 | £4,109.10 | £5,955.14 | £5,860.09 | £948,814.63 | £498,997.35 | £1,300,006.94 | £15,006.63 |
| 2023 | £1,745.06 | £5,526.98 | £2,230.25 | £2,636.95 | £5,852.04 | £9,873.78 | £5,080.68 | £6,554.63 | £6,362.09 | £984,609.19 | £492,401.50 | £1,303,755.85 | £17,609.37 |
| 2024 | £1,798.33 | £6,360.93 | £2,256.20 | £3,084.50 | £6,181.05 | £9,054.31 | £5,178.94 | £7,304.09 | £6,405.25 | £1,090,869.31 | £530,639.99 | £1,562,763.72 | £17,930.06 |
| 2025 | £1,802.77 | £5,794.11 | £2,103.84 | £2,903.81 | £5,803.49 | £8,964.40 | £5,632.82 | £6,973.05 | £6,555.44 | £1,293,692.67 | £593,616.07 | £1,592,622.37 | £16,805.04 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,851.63, range £36.78–£26,438.70.

- C1: cost to serve £390.76, net margin after CTS £1,456.97
- C1g: cost to serve £49.03, net margin after CTS £902.62
- C2: cost to serve £788.01, net margin after CTS £7,654.63
- C2g: cost to serve £172.32, net margin after CTS £3,899.40
- C3: cost to serve £264.57, net margin after CTS £1,165.05
- C3g: cost to serve £36.78, net margin after CTS £779.27
- C4: cost to serve £598.27, net margin after CTS £3,121.40
- C4g: cost to serve £195.83, net margin after CTS £2,391.10
- C5: cost to serve £869.97, net margin after CTS £8,323.08
- C6: cost to serve £1,267.78, net margin after CTS £16,297.37
- C7: cost to serve £988.26, net margin after CTS £11,443.19
- C8: cost to serve £987.01, net margin after CTS £13,835.75
- C9: cost to serve £918.31, net margin after CTS £12,850.12
- C_IC1: cost to serve £21,251.38, net margin after CTS £2,117,331.36
- C_IC2: cost to serve £11,716.09, net margin after CTS £961,819.27
- C_IC3: cost to serve £26,438.70, net margin after CTS £1,779,913.99
- C_IC3g: cost to serve £9,224.23, net margin after CTS £416,430.41
- C_IC4: cost to serve £11,172.13, net margin after CTS £21,351.71 — MARGIN_SQUEEZE (below 2% benchmark)

**Activity-Based Pricing Actions**

The following 1 customer(s) are profitable but below the 2% net-margin benchmark (MARGIN_SQUEEZE): C_IC4


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 28 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 13.6%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,694.56 | £10,901.23 | +20.0% | £102.83/MWh | £136.82/MWh |
| C1 | electricity | 2018-12-31 | £-26.99 | £469.89 | +0.7% | £152.73/MWh | £155.03/MWh |
| C5 | electricity | 2018-12-31 | £-165.75 | £2,339.43 | +2.1% | £152.73/MWh | £156.93/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,300.82 | £6,376.41 | +20.0% | £128.64/MWh | £177.52/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,218.30 | £10,243.03 | +20.0% | £126.12/MWh | £171.31/MWh |
| C_IC3g | gas | 2020-01-01 | £-36,112.79 | £134,045.32 | +20.0% | £15.06/MWh | £17.16/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,904.90 | £3,444.18 | +20.0% | £99.07/MWh | £136.71/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,041.06 | £6,326.95 | +20.0% | £99.78/MWh | £113.75/MWh |
| C_IC2 | electricity | 2021-03-31 | £-3,729.85 | £5,726.15 | +20.0% | £125.43/MWh | £158.64/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,006.00 | £14,511.74 | +20.0% | £119.64/MWh | £147.64/MWh |
| C4 | electricity | 2021-09-30 | £-115.80 | £627.84 | +13.4% | £187.73/MWh | £221.29/MWh |
| C4g | gas | 2021-09-30 | £-114.12 | £346.35 | +20.0% | £47.60/MWh | £60.39/MWh |
| C5 | electricity | 2021-12-30 | £-181.26 | £2,733.57 | +1.6% | £258.06/MWh | £260.76/MWh |
| C2g | gas | 2022-03-31 | £-26.58 | £490.31 | +0.4% | £116.62/MWh | £117.83/MWh |
| C_IC2 | electricity | 2022-04-30 | £-1,292.09 | £17,661.75 | +2.3% | £288.61/MWh | £308.58/MWh |
| C_IC1 | electricity | 2022-05-30 | £-4,406.97 | £22,384.38 | +14.7% | £265.62/MWh | £310.75/MWh |
| C9 | electricity | 2022-06-30 | £-126.67 | £1,989.23 | +1.4% | £308.80/MWh | £310.19/MWh |
| C4 | electricity | 2022-09-30 | £-155.80 | £1,251.54 | +7.5% | £335.38/MWh | £345.03/MWh |
| C4g | gas | 2022-09-30 | £-233.26 | £1,328.64 | +12.6% | £154.55/MWh | £182.83/MWh |
| C7 | electricity | 2022-12-30 | £-726.46 | £3,216.74 | +17.6% | £346.58/MWh | £388.11/MWh |
| C_IC3 | electricity | 2022-12-31 | £-173,158.95 | £908,383.65 | +14.1% | £248.91/MWh | £274.39/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,193.41 | £7,055.33 | +20.0% | £199.16/MWh | £263.12/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,414.36 | £17,979.18 | +20.0% | £223.62/MWh | £288.31/MWh |
| C4 | electricity | 2023-09-30 | £-303.08 | £1,941.96 | +10.6% | £222.86/MWh | £234.17/MWh |
| C_IC3g | gas | 2023-12-31 | £-252,917.30 | £294,338.38 | +20.0% | £46.43/MWh | £57.82/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,916.03 | £7,659.10 | +20.0% | £147.78/MWh | £203.93/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,612.90 | £14,454.77 | +20.0% | £145.53/MWh | £200.83/MWh |
| C_IC3g | gas | 2024-12-30 | £-17,160.47 | £268,215.17 | +1.4% | £47.09/MWh | £45.36/MWh |


## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 116 renewal(s) (30 gas) based on recent portfolio-wide margin rates: 72 surcharge(s), 44 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | 4.5% | +1.7% | £135.18/MWh | £137.51/MWh |
| C1g | gas | 2016-12-31 | 14.9% | -3.5% | £27.40/MWh | £26.45/MWh |
| C5 | electricity | 2016-12-31 | 3.5% | +2.2% | £135.18/MWh | £138.20/MWh |
| C7 | electricity | 2016-12-31 | 5.5% | +1.2% | £135.18/MWh | £136.87/MWh |
| C2 | electricity | 2017-04-01 | 12.6% | -2.3% | £133.08/MWh | £130.01/MWh |
| C2g | gas | 2017-04-01 | 15.4% | -3.7% | £31.27/MWh | £30.12/MWh |
| C6 | electricity | 2017-04-01 | 11.8% | -1.9% | £133.08/MWh | £130.56/MWh |
| C8 | electricity | 2017-04-01 | 10.8% | -1.4% | £133.08/MWh | £131.24/MWh |
| C3 | electricity | 2017-07-01 | 11.6% | -1.8% | £119.89/MWh | £117.72/MWh |
| C3g | gas | 2017-07-01 | 12.6% | -2.3% | £27.98/MWh | £27.34/MWh |
| C9 | electricity | 2017-07-01 | 7.8% | +0.1% | £119.89/MWh | £120.00/MWh |
| C4 | electricity | 2017-10-01 | 8.9% | -0.5% | £116.00/MWh | £115.48/MWh |
| C4g | gas | 2017-10-01 | 11.6% | -1.8% | £27.18/MWh | £26.69/MWh |
| C1 | electricity | 2017-12-31 | 7.7% | +0.1% | £124.66/MWh | £124.83/MWh |
| C1g | gas | 2017-12-31 | 9.2% | -0.6% | £34.54/MWh | £34.33/MWh |
| C5 | electricity | 2017-12-31 | 2.3% | +2.9% | £124.66/MWh | £128.24/MWh |
| C7 | electricity | 2017-12-31 | -0.7% | +4.3% | £124.66/MWh | £130.05/MWh |
| C_IC1 | electricity | 2018-01-31 | -13.7% | +10.9% | £102.83/MWh | £114.01/MWh |
| C2 | electricity | 2018-04-01 | -4.0% | +6.0% | £139.96/MWh | £148.32/MWh |
| C2g | gas | 2018-04-01 | 10.3% | -1.1% | £38.10/MWh | £37.66/MWh |
| C6 | electricity | 2018-04-01 | -4.6% | +6.3% | £139.96/MWh | £148.76/MWh |
| C8 | electricity | 2018-04-01 | 7.7% | +0.1% | £139.96/MWh | £140.14/MWh |
| C3 | electricity | 2018-07-01 | 9.0% | -0.5% | £139.77/MWh | £139.04/MWh |
| C3g | gas | 2018-07-01 | 10.2% | -1.1% | £33.69/MWh | £33.32/MWh |
| C9 | electricity | 2018-07-01 | 2.4% | +2.8% | £139.77/MWh | £143.68/MWh |
| C4 | electricity | 2018-10-01 | 6.0% | +1.0% | £138.46/MWh | £139.86/MWh |
| C4g | gas | 2018-10-01 | 10.0% | -1.0% | £34.20/MWh | £33.85/MWh |
| C1 | electricity | 2018-12-31 | 6.5% | +0.8% | £152.73/MWh | £153.88/MWh |
| C1g | gas | 2018-12-31 | 10.4% | -1.2% | £42.21/MWh | £41.71/MWh |
| C5 | electricity | 2018-12-31 | 6.7% | +0.7% | £152.73/MWh | £153.73/MWh |
| C7 | electricity | 2018-12-31 | 6.3% | +0.8% | £152.73/MWh | £154.00/MWh |
| C_IC2 | electricity | 2019-01-31 | -26.7% | +15.0% | £128.64/MWh | £147.93/MWh |
| C_IC1 | electricity | 2019-03-02 | -18.4% | +13.2% | £126.12/MWh | £142.76/MWh |
| C2 | electricity | 2019-04-01 | 5.3% | +1.4% | £160.26/MWh | £162.45/MWh |
| C2g | gas | 2019-04-01 | 2.6% | +2.7% | £38.81/MWh | £39.86/MWh |
| C6 | electricity | 2019-04-01 | 7.6% | +0.2% | £160.26/MWh | £160.61/MWh |
| C8 | electricity | 2019-04-01 | 27.8% | -5.0% | £160.26/MWh | £152.25/MWh |
| C3 | electricity | 2019-07-01 | 21.7% | -5.0% | £136.52/MWh | £129.69/MWh |
| C3g | gas | 2019-07-01 | 9.5% | -0.7% | £29.44/MWh | £29.22/MWh |
| C9 | electricity | 2019-07-01 | 11.5% | -1.7% | £136.52/MWh | £134.15/MWh |
| C4 | electricity | 2019-10-01 | 11.3% | -1.6% | £130.78/MWh | £128.63/MWh |
| C4g | gas | 2019-10-01 | 16.5% | -4.2% | £24.19/MWh | £23.17/MWh |
| C1 | electricity | 2019-12-31 | 10.5% | -1.3% | £132.50/MWh | £130.83/MWh |
| C1g | gas | 2019-12-31 | 15.3% | -3.6% | £25.02/MWh | £24.11/MWh |
| C5 | electricity | 2019-12-31 | 6.6% | +0.7% | £132.50/MWh | £133.42/MWh |
| C7 | electricity | 2019-12-31 | 5.9% | +1.1% | £132.50/MWh | £133.90/MWh |
| C_IC3 | electricity | 2020-01-01 | 3.9% | +2.0% | £48.73/MWh | £49.72/MWh |
| C_IC3g | gas | 2020-01-01 | 25.5% | -5.0% | £15.06/MWh | £14.30/MWh |
| C_IC2 | electricity | 2020-03-01 | -97.3% | +15.0% | £99.07/MWh | £113.93/MWh |
| C2 | electricity | 2020-03-31 | -88.7% | +15.0% | £133.78/MWh | £153.85/MWh |
| C2g | gas | 2020-03-31 | 15.2% | -3.6% | £25.80/MWh | £24.88/MWh |
| C6 | electricity | 2020-03-31 | -45.2% | +15.0% | £133.78/MWh | £153.85/MWh |
| C8 | electricity | 2020-03-31 | -13.3% | +10.6% | £133.78/MWh | £148.01/MWh |
| C_IC1 | electricity | 2020-03-31 | 24.3% | -5.0% | £99.78/MWh | £94.79/MWh |
| C3 | electricity | 2020-06-30 | 21.7% | -5.0% | £122.32/MWh | £116.20/MWh |
| C9 | electricity | 2020-06-30 | 21.7% | -5.0% | £122.32/MWh | £116.20/MWh |
| C4 | electricity | 2020-09-30 | 18.3% | -5.0% | £118.09/MWh | £112.19/MWh |
| C4g | gas | 2020-09-30 | 14.8% | -3.4% | £16.30/MWh | £15.74/MWh |
| C1 | electricity | 2020-12-30 | 10.1% | -1.1% | £139.74/MWh | £138.25/MWh |
| C1g | gas | 2020-12-30 | 1.4% | +3.3% | £23.90/MWh | £24.69/MWh |
| C5 | electricity | 2020-12-30 | 3.1% | +2.4% | £139.74/MWh | £143.15/MWh |
| C7 | electricity | 2020-12-30 | -5.9% | +7.0% | £139.74/MWh | £149.47/MWh |
| C_IC3 | electricity | 2020-12-31 | -6.6% | +7.3% | £53.68/MWh | £57.60/MWh |
| C_IC3g | gas | 2020-12-31 | -6.7% | +7.3% | £14.98/MWh | £16.07/MWh |
| C2 | electricity | 2021-03-31 | -27.7% | +15.0% | £162.43/MWh | £186.79/MWh |
| C2g | gas | 2021-03-31 | 5.1% | +1.4% | £32.22/MWh | £32.69/MWh |
| C6 | electricity | 2021-03-31 | -25.5% | +15.0% | £162.43/MWh | £186.79/MWh |
| C8 | electricity | 2021-03-31 | -23.3% | +15.0% | £162.43/MWh | £186.79/MWh |
| C_IC2 | electricity | 2021-03-31 | -2.8% | +5.4% | £125.43/MWh | £132.20/MWh |
| C_IC1 | electricity | 2021-04-30 | 2.3% | +2.8% | £119.64/MWh | £123.03/MWh |
| C9 | electricity | 2021-06-30 | 6.3% | +0.9% | £159.32/MWh | £160.69/MWh |
| C4 | electricity | 2021-09-30 | 0.2% | +3.9% | £187.73/MWh | £195.06/MWh |
| C4g | gas | 2021-09-30 | -3.4% | +5.7% | £47.60/MWh | £50.33/MWh |
| C1 | electricity | 2021-12-30 | 9.2% | -0.6% | £258.06/MWh | £256.58/MWh |
| C5 | electricity | 2021-12-30 | 9.2% | -0.6% | £258.06/MWh | £256.58/MWh |
| C7 | electricity | 2021-12-30 | 9.2% | -0.6% | £258.06/MWh | £256.58/MWh |
| C_IC3 | electricity | 2021-12-31 | -4.7% | +6.3% | £172.01/MWh | £182.94/MWh |
| C_IC3g | gas | 2021-12-31 | 0.4% | +3.8% | £81.39/MWh | £84.48/MWh |
| C2 | electricity | 2022-03-31 | -19.6% | +13.8% | £344.78/MWh | £392.42/MWh |
| C2g | gas | 2022-03-31 | 6.8% | +0.6% | £116.62/MWh | £117.34/MWh |
| C6 | electricity | 2022-03-31 | -13.3% | +10.7% | £344.78/MWh | £381.50/MWh |
| C8 | electricity | 2022-03-31 | -5.5% | +6.8% | £344.78/MWh | £368.06/MWh |
| C_IC2 | electricity | 2022-04-30 | -1.0% | +4.5% | £288.61/MWh | £301.59/MWh |
| C_IC1 | electricity | 2022-05-30 | 4.0% | +2.0% | £265.62/MWh | £270.96/MWh |
| C9 | electricity | 2022-06-30 | 9.8% | -0.9% | £308.80/MWh | £306.01/MWh |
| C4 | electricity | 2022-09-30 | 16.5% | -4.2% | £335.38/MWh | £321.11/MWh |
| C4g | gas | 2022-09-30 | -2.2% | +5.1% | £154.55/MWh | £162.43/MWh |
| C7 | electricity | 2022-12-30 | 17.5% | -4.8% | £346.58/MWh | £330.08/MWh |
| C_IC3 | electricity | 2022-12-31 | 14.7% | -3.4% | £248.91/MWh | £240.56/MWh |
| C_IC3g | gas | 2022-12-31 | 2.0% | +3.0% | £155.47/MWh | £160.16/MWh |
| C2 | electricity | 2023-03-31 | -12.0% | +10.0% | £355.13/MWh | £390.68/MWh |
| C2g | gas | 2023-03-31 | -15.1% | +11.6% | £132.22/MWh | £147.52/MWh |
| C6 | electricity | 2023-03-31 | -0.4% | +4.2% | £355.13/MWh | £370.09/MWh |
| C8 | electricity | 2023-03-31 | 1.5% | +3.3% | £355.13/MWh | £366.72/MWh |
| C_IC2 | electricity | 2023-05-30 | -12.2% | +10.1% | £199.16/MWh | £219.27/MWh |
| C_IC1 | electricity | 2023-06-29 | -6.9% | +7.4% | £223.62/MWh | £240.26/MWh |
| C9 | electricity | 2023-06-30 | -2.6% | +5.3% | £285.09/MWh | £300.27/MWh |
| C4 | electricity | 2023-09-30 | 20.6% | -5.0% | £222.86/MWh | £211.72/MWh |
| C4g | gas | 2023-09-30 | -2.2% | +5.1% | £54.57/MWh | £57.36/MWh |
| C7 | electricity | 2023-12-30 | 35.5% | -5.0% | £230.30/MWh | £218.78/MWh |
| C_IC3 | electricity | 2023-12-31 | 25.6% | -5.0% | £108.31/MWh | £102.90/MWh |
| C_IC3g | gas | 2023-12-31 | 0.4% | +3.8% | £46.43/MWh | £48.19/MWh |
| C2 | electricity | 2024-03-30 | -19.1% | +13.5% | £219.64/MWh | £249.39/MWh |
| C2g | gas | 2024-03-30 | -4.0% | +6.0% | £61.85/MWh | £65.55/MWh |
| C6 | electricity | 2024-03-30 | -17.7% | +12.9% | £219.64/MWh | £247.89/MWh |
| C8 | electricity | 2024-03-30 | -17.7% | +12.9% | £219.64/MWh | £247.89/MWh |
| C_IC2 | electricity | 2024-06-28 | -27.0% | +15.0% | £147.78/MWh | £169.95/MWh |
| C9 | electricity | 2024-06-29 | -23.2% | +15.0% | £202.67/MWh | £233.08/MWh |
| C_IC1 | electricity | 2024-07-28 | -24.5% | +15.0% | £145.53/MWh | £167.36/MWh |
| C4 | electricity | 2024-09-29 | 2.3% | +2.8% | £208.53/MWh | £214.45/MWh |
| C7 | electricity | 2024-12-29 | 2.3% | +2.8% | £226.90/MWh | £233.35/MWh |
| C_IC3 | electricity | 2024-12-30 | 22.6% | -5.0% | £99.76/MWh | £94.77/MWh |
| C_IC3g | gas | 2024-12-30 | 27.1% | -5.0% | £47.09/MWh | £44.74/MWh |
| C2 | electricity | 2025-03-30 | -11.9% | +9.9% | £253.94/MWh | £279.21/MWh |
| C2g | gas | 2025-03-30 | 11.6% | -1.8% | £67.68/MWh | £66.48/MWh |
| C8 | electricity | 2025-03-30 | -16.1% | +12.1% | £253.94/MWh | £284.55/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **4** | Blind misses: **4** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 1 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £4,338.92 | deliberate: £0.00 | total: £4,338.92

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.08 | No | £372.36 |
| C1 | 2021-12-30 | Blind miss | 0.08 | 0.17 | No | £344.82 |
| C6 | 2024-03-30 | Blind miss | 0.20 | 0.38 | Yes | £2,844.57 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.26 | No | £777.17 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £169,244.75 | £-146,374.94 | £22,869.82 | No |
| C2+C2g | £2,301.34 | £2,418.38 | £4,719.73 | Yes |
| C1+C1g | £93.50 | £233.38 | £326.88 | Yes |
| C3+C3g | £68.64 | £257.78 | £326.42 | Yes |
| C4+C4g | £-384.55 | £504.31 | £119.75 | Yes |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £-142,961.09.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £678,587.61 across 18 billing accounts. Revenue: £13,335,600.85.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,406,651.16 | £2,138,582.74 | £17,776.29 | £1,131,851.53 | 33.2% |
| 2 | C_IC2 | fixed | £1,599,583.01 | £973,535.36 | £8,370.98 | £510,297.05 | 31.9% |
| 3 | C_IC3 | pass_through | £4,644,074.89 | £1,806,352.69 | £22,203.74 | £169,244.75 | 3.6% |
| 4 | C8 | fixed | £24,079.10 | £14,822.77 | £152.26 | £4,847.49 | 20.1% |
| 5 | C9 | fixed | £21,329.45 | £13,768.43 | £122.31 | £3,497.83 | 16.4% |
| 6 | C6 | fixed | £30,800.28 | £17,565.14 | £206.39 | £3,291.24 | 10.7% |
| 7 | C2g | fixed | £8,089.59 | £4,071.72 | £84.61 | £2,418.38 | 29.9% |
| 8 | C2 | fixed | £14,129.07 | £8,442.64 | £94.04 | £2,301.34 | 16.3% |
| 9 | C7 | fixed | £23,456.20 | £12,431.45 | £159.00 | £1,285.87 | 5.5% |
| 10 | C4g | fixed | £9,333.17 | £2,586.93 | £110.11 | £504.31 | 5.4% |
| 11 | C3g | fixed | £1,609.60 | £816.05 | £9.77 | £257.78 | 16.0% |
| 12 | C1g | fixed | £2,107.50 | £951.64 | £14.90 | £233.38 | 11.1% |
| 13 | C1 | fixed | £3,041.20 | £1,847.72 | £14.94 | £93.50 | 3.1% |
| 14 | C3 | fixed | £2,231.24 | £1,429.63 | £9.05 | £68.64 | 3.1% |
| 15 | C5 | fixed | £15,011.95 | £9,193.05 | £75.99 | £24.15 | 0.2% |
| 16 | C4 | fixed | £7,918.90 | £3,719.67 | £61.20 | £-384.55 | -4.9% |
| 17 | C_IC3g | pass_through | £1,831,432.12 | £425,654.64 | £14,381.28 | £-146,374.94 | -8.0% |
| 18 | C_IC4 | flex | £1,690,722.42 | £32,523.85 | £0.00 | £-1,004,870.14 | -59.4% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £13,335,601 | 100.0% |
| Wholesale cost | -£7,867,305 | 59.0% |
| **Gross supply margin** | **£5,468,296** | **41.0%** |
| Policy + Network costs | -£4,725,862 | 35.4% |
| Capital cost | -£63,847 | 0.5% |
| **Net supply margin** | **£678,588** | **5.1%** |

> *The ledger's `net_margin_gbp` (£5,418,508) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £11,341,031 | 43.7% | 7.1% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,831,432 | 23.2% | -8.0% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £45,812 | 58.4% | 7.2% | CMA 3-8% | ✓ |
| resi/elec | £96,185 | 58.7% | 12.2% | Ofgem CMA 2-5% | ⚠ ANOMALY |
| resi/gas | £21,140 | 39.9% | 16.1% | Ofgem CMA 2-4% | ⚠ ANOMALY |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: ANOMALIES DETECTED**
- Segment resi/elec net 12.2% (benchmark Ofgem CMA 2-5%)
- Segment resi/gas net 16.1% (benchmark Ofgem CMA 2-4%)
## Transaction Log

Total events: 3,299,449

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 5 |
| bad_debt_event | 1,569 |
| billing_event | 1,569 |
| capital_charge_event | 1,588,574 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,569 |
| payment_received_event | 1,569 |
| settlement_event | 1,702,911 |
| vat_remittance_event | 1,569 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £18,242,335.98 |
|   Less: VAT remitted to HMRC | (£877,189.82) |
| = Revenue (ex-VAT) | £17,365,146.16 |
| Less: non-commodity pass-through | (£4,015,486.66) |
| Wholesale cost (settlement events) | (£7,867,304.73) |
| Gross margin | £5,482,354.77 |
| Capital charges | (£63,846.87) |
| Net margin | £5,418,507.89 |

_Cash reconciliation: of £18,242,335.98 billed, bad debt of £364,821.78 was written off, leaving £17,877,514.20 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £5,930,875.93._

| Acquisition spend | (£1,250.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £5,411,557.89 |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £5,411,557.89

## 2016

**Trading & Risk**

- Net margin: £737.38 (gross £5,817.42, capital £73.07)
  - Electricity: gross £5,295.56, capital £67.65, net £576.72
  - Gas: gross £521.85, capital £5.42, net £160.66
- Treasury at year end: £2,467,024.27
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.90 (avg 0.90), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.92), C6 0.91 (avg 0.91), C7 0.91 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.22, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-01-31: treasury £2,466,640.18, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-03-01: treasury £2,466,644.23, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-03-31: treasury £2,466,648.06, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-04-30: treasury £2,466,651.20, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-05-30: treasury £2,466,654.28, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-06-29: treasury £2,466,657.02, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-07-29: treasury £2,466,659.86, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-08-28: treasury £2,466,662.72, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-09-27: treasury £2,466,665.72, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-10-27: treasury £2,466,668.70, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-11-26: treasury £2,466,671.55, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
  - 2016-12-26: treasury £2,466,675.33, C1->1.00, VaR (current £22.88 / stressed £7.03) ratio 3.25
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.25
- Worst single period: C9 on 2016-11-20 period 36, net margin £-0.32

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £3,793.14
  - By billing account: C1 £1,782.56, C5 £5,242.98, C7 £4,353.87
- Bill shock events (>=20%): 21 -- C5 2016-05-31 (28%); C5 2016-06-30 (21%); C5 2016-10-31 (43%); C5 2016-11-30 (45%); C7 2016-04-30 (22%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-10-31 (83%); C7 2016-11-30 (54%); C6 2016-05-31 (26%); C6 2016-06-30 (23%); C6 2016-10-31 (42%); C6 2016-11-30 (47%); C8 2016-05-31 (41%); C8 2016-06-30 (43%); C8 2016-09-30 (25%); C8 2016-10-31 (110%); C8 2016-11-30 (72%); C9 2016-09-30 (20%); C9 2016-10-31 (80%); C9 2016-11-30 (61%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £114.71-£137.51/MWh, net margin £39.67
- C1g (gas): tariff £24.34-£26.45/MWh, net margin £25.18
- C2 (electricity): tariff £113.91/MWh, net margin £49.13
- C2g (gas): tariff £30.45/MWh, net margin £93.51
- C3 (electricity): tariff £103.82/MWh, net margin £3.05
- C3g (gas): tariff £25.09/MWh, net margin £27.05
- C4 (electricity): tariff £102.93/MWh, net margin £0.37
- C4g (gas): tariff £24.19/MWh, net margin £14.92
- C5 (electricity): tariff £114.71-£138.20/MWh, net margin £90.42
- C6 (electricity): tariff £113.91/MWh, net margin £23.34
- C7 (electricity): tariff £90.13-£172.06/MWh, net margin £182.18
- C8 (electricity): tariff £89.50-£170.87/MWh, net margin £141.57
- C9 (electricity): tariff £81.57-£155.73/MWh, net margin £47.01

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.890, average bill shock 14.0%, bad debt provision £319.28, avg complaint probability 3.6%
- Solvency signal: £274,114/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,443.76 vs. naked (unhedged) net margin: £9,121.35
- hedging cost £7,677.59 vs. a fully unhedged book (commodity-only: actual net £1,443.76 vs. naked net £9,121.35)
  - C1: actual £95.21 vs. naked £530.60 -- hedging cost £435.39
  - C1g: actual £58.00 vs. naked £260.42 -- hedging cost £202.43
  - C2: actual £62.14 vs. naked £489.38 -- hedging cost £427.24
  - C2g: actual £121.87 vs. naked £256.57 -- hedging cost £134.70
  - C3: actual £-2.89 vs. naked £234.88 -- hedging cost £237.77
  - C3g: actual £50.80 vs. naked £156.35 -- hedging cost £105.55
  - C4: actual £-16.04 vs. naked £296.92 -- hedging cost £312.96
  - C4g: actual £53.38 vs. naked £205.16 -- hedging cost £151.78
  - C5: actual £272.66 vs. naked £2,507.92 -- hedging cost £2,235.27
  - C6: actual £21.98 vs. naked £868.36 -- hedging cost £846.38
  - C7: actual £409.86 vs. naked £1,859.10 -- hedging cost £1,449.24
  - C8: actual £223.84 vs. naked £789.69 -- hedging cost £565.85
  - C9: actual £92.96 vs. naked £666.00 -- hedging cost £573.04

**Year narrative:** 2016 produced a net gain of £737.38 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 21 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £47,951.56 (gross £139,034.16, capital £1,230.56)
  - Electricity: gross £138,197.93, capital £1,220.13, net £47,749.47
  - Gas: gross £836.23, capital £10.43, net £202.10
- Treasury at year end: £2,514,878.35
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.92 (avg 0.92), C7 0.91 (avg 0.91), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,467,027.59, C1->1.00, C5->1.00, C7->1.00, VaR (current £301.78 / stressed £95.39) ratio 3.16
  - 2017-02-24: treasury £2,467,031.81, C1->1.00, C5->1.00, C7->1.00, VaR (current £301.78 / stressed £95.39) ratio 3.16
  - 2017-03-26: treasury £2,467,036.45, C1->1.00, C5->1.00, C7->1.00, VaR (current £301.78 / stressed £95.39) ratio 3.16
  - 2017-04-25: treasury £2,467,405.70, C1->1.00, C5->1.00, C7->1.00, VaR (current £720.42 / stressed £270.85) ratio 2.66
  - 2017-05-25: treasury £2,467,403.77, C1->1.00, C5->1.00, C7->1.00, VaR (current £720.42 / stressed £270.85) ratio 2.66
  - 2017-06-24: treasury £2,467,402.35, C1->1.00, C5->1.00, C7->1.00, VaR (current £720.42 / stressed £270.85) ratio 2.66
  - 2017-07-24: treasury £2,467,535.30, C1->1.00, C5->1.00, C7->1.00, VaR (current £837.71 / stressed £326.34) ratio 2.57
  - 2017-08-23: treasury £2,467,533.19, C1->1.00, C5->1.00, C7->1.00, VaR (current £837.71 / stressed £326.34) ratio 2.57
  - 2017-09-22: treasury £2,467,530.62, C1->1.00, C5->1.00, C7->1.00, VaR (current £837.71 / stressed £326.34) ratio 2.57
  - 2017-10-22: treasury £2,467,627.73, C5->1.00, C7->1.00, VaR (current £843.41 / stressed £331.36) ratio 2.55
  - 2017-11-21: treasury £2,467,632.51, C5->1.00, C7->1.00, VaR (current £843.41 / stressed £331.36) ratio 2.55
  - 2017-12-21: treasury £2,467,637.16, C5->1.00, C7->1.00, VaR (current £843.41 / stressed £331.36) ratio 2.55
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-22.24

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £5,715.31
  - By billing account: C1 £2,016.66, C2 £6,069.81, C3 £2,782.92, C4 £3,690.43, C5 £7,107.63, C6 £10,775.91, C7 £4,690.29, C8 £8,195.43, C9 £6,108.67
- Bill shock events (>=20%): 27 -- C5 2017-01-31 (32%); C5 2017-02-28 (23%); C5 2017-05-31 (20%); C5 2017-06-30 (22%); C5 2017-11-30 (58%); C7 2017-01-31 (39%); C7 2017-02-28 (29%); C7 2017-05-31 (32%); C7 2017-06-30 (33%); C7 2017-09-30 (28%); C7 2017-10-31 (23%); C7 2017-11-30 (79%); C6 2017-05-31 (22%); C6 2017-06-30 (20%); C6 2017-11-30 (51%); C8 2017-05-31 (40%); C8 2017-06-30 (37%); C8 2017-09-30 (48%); C8 2017-10-31 (23%); C8 2017-11-30 (85%); C8 2017-12-31 (22%); C9 2017-05-31 (33%); C9 2017-06-30 (27%); C9 2017-09-30 (31%); C9 2017-10-31 (22%); C9 2017-11-30 (72%); C4 2017-10-31 (21%)
- Churn risk (accounts renewing in 2017): 5 at risk (≥20% churn prob): C5 32%, C6 35%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £124.83-£137.51/MWh, net margin £55.36
- C1g (gas): tariff £26.45-£34.33/MWh, net margin £32.76
- C2 (electricity): tariff £113.91-£130.01/MWh, net margin £64.73
- C2g (gas): tariff £30.12-£30.45/MWh, net margin £83.76
- C3 (electricity): tariff £103.82-£120.72/MWh, net margin £10.43
- C3g (gas): tariff £25.09-£27.34/MWh, net margin £45.03
- C4 (electricity): tariff £102.93-£118.48/MWh, net margin £-13.97 -- **net-negative**
- C4g (gas): tariff £24.19-£26.69/MWh, net margin £40.56
- C5 (electricity): tariff £128.24-£138.20/MWh, net margin £181.32
- C6 (electricity): tariff £113.91-£130.56/MWh, net margin £53.84
- C7 (electricity): tariff £104.54-£205.30/MWh, net margin £226.30
- C8 (electricity): tariff £89.50-£196.85/MWh, net margin £241.31
- C9 (electricity): tariff £81.57-£180.00/MWh, net margin £131.77
- C_IC1 (electricity): tariff £82.61-£157.70/MWh, net margin £46,798.37

**Portfolio Health**

- Capital cost ratio: 0.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.884, average bill shock 11.4%, bad debt provision £7,752.12, avg complaint probability 3.5%
- Solvency signal: £251,488/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £47,493.89 vs. naked (unhedged) net margin: £126,493.78
- hedging cost £78,999.90 vs. a fully unhedged book (commodity-only: actual net £47,493.89 vs. naked net £126,493.78)
  - C1: actual £-26.99 vs. naked £214.85 -- hedging cost £241.84
  - C1g: actual £60.20 vs. naked £138.42 -- hedging cost £78.21
  - C2: actual £68.97 vs. naked £525.85 -- hedging cost £456.89
  - C2g: actual £70.65 vs. naked £184.80 -- hedging cost £114.15
  - C3: actual £24.64 vs. naked £272.94 -- hedging cost £248.30
  - C3g: actual £39.28 vs. naked £113.37 -- hedging cost £74.08
  - C4: actual £-10.27 vs. naked £321.97 -- hedging cost £332.24
  - C4g: actual £3.71 vs. naked £118.14 -- hedging cost £114.43
  - C5: actual £-165.75 vs. naked £1,084.27 -- hedging cost £1,250.02
  - C6: actual £80.86 vs. naked £1,312.72 -- hedging cost £1,231.87
  - C7: actual £64.47 vs. naked £889.45 -- hedging cost £824.98
  - C8: actual £286.35 vs. naked £978.44 -- hedging cost £692.10
  - C9: actual £199.40 vs. naked £868.62 -- hedging cost £669.22
  - C_IC1: actual £46,798.37 vs. naked £119,469.95 -- hedging cost £72,671.58

**Year narrative:** 2017 produced a net gain of £47,951.56 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 27 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £88,733.44 (gross £249,487.23, capital £1,566.63)
  - Electricity: gross £248,686.99, capital £1,551.83, net £88,557.46
  - Gas: gross £800.24, capital £14.80, net £175.98
- Treasury at year end: £2,510,611.86
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.91 (avg 0.91), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2018-03-01 period 27, net margin £-18.81

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £159,328.40
  - By billing account: C1 £2,062.28, C2 £5,013.42, C3 £2,753.14, C4 £3,150.95, C5 £6,193.58, C6 £7,871.99, C7 £4,664.48, C8 £6,568.30, C9 £6,032.37, C_IC1 £1,548,973.45
- Bill shock events (>=20%): 34 -- C5 2018-04-30 (33%); C5 2018-06-30 (21%); C5 2018-10-31 (32%); C5 2018-11-30 (28%); C7 2018-04-30 (39%); C7 2018-05-31 (29%); C7 2018-06-30 (32%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C6 2018-04-30 (22%); C6 2018-05-31 (22%); C6 2018-06-30 (22%); C6 2018-10-31 (31%); C6 2018-11-30 (22%); C8 2018-04-30 (35%); C8 2018-05-31 (38%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (57%); C8 2018-11-30 (30%); C9 2018-04-30 (32%); C9 2018-05-31 (35%); C9 2018-06-30 (35%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-10-31 (26%); C4g 2018-10-31 (21%); C_IC1 2018-01-31 (24%); C_IC1 2018-02-28 (51%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C4 20%, C5 38%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £124.83-£158.03/MWh, net margin £-26.75 -- **net-negative**
- C1g (gas): tariff £34.33-£41.71/MWh, net margin £60.31
- C2 (electricity): tariff £130.01-£148.32/MWh, net margin £30.55
- C2g (gas): tariff £30.12-£37.66/MWh, net margin £78.39
- C3 (electricity): tariff £120.72-£142.04/MWh, net margin £30.26
- C3g (gas): tariff £27.34-£33.32/MWh, net margin £36.63
- C4 (electricity): tariff £118.48-£142.86/MWh, net margin £-10.17 -- **net-negative**
- C4g (gas): tariff £26.69-£33.85/MWh, net margin £0.65
- C5 (electricity): tariff £128.24-£159.93/MWh, net margin £-164.58 -- **net-negative**
- C6 (electricity): tariff £130.56-£148.76/MWh, net margin £-16.06 -- **net-negative**
- C7 (electricity): tariff £104.54-£235.50/MWh, net margin £67.39
- C8 (electricity): tariff £103.11-£214.72/MWh, net margin £188.73
- C9 (electricity): tariff £94.28-£220.02/MWh, net margin £246.55
- C_IC1 (electricity): tariff £-82.12-£226.14/MWh, net margin £87,478.97
- C_IC2 (electricity): tariff £73.69-£140.68/MWh, net margin £732.56

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.872, average bill shock 11.3%, bad debt provision £12,556.95, avg complaint probability 3.6%
- Solvency signal: £228,237/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £97,304.24 vs. naked (unhedged) net margin: £229,768.76
- hedging cost £132,464.52 vs. a fully unhedged book (commodity-only: actual net £97,304.24 vs. naked net £229,768.76)
  - C1: actual £40.34 vs. naked £401.45 -- hedging cost £361.11
  - C1g: actual £128.25 vs. naked £333.97 -- hedging cost £205.72
  - C2: actual £12.00 vs. naked £605.90 -- hedging cost £593.90
  - C2g: actual £86.55 vs. naked £236.17 -- hedging cost £149.62
  - C3: actual £35.50 vs. naked £365.72 -- hedging cost £330.22
  - C3g: actual £44.21 vs. naked £190.31 -- hedging cost £146.10
  - C4: actual £-7.77 vs. naked £499.37 -- hedging cost £507.14
  - C4g: actual £15.88 vs. naked £378.82 -- hedging cost £362.95
  - C5: actual £121.24 vs. naked £1,954.12 -- hedging cost £1,832.87
  - C6: actual £-81.83 vs. naked £1,473.11 -- hedging cost £1,554.94
  - C7: actual £188.24 vs. naked £1,415.35 -- hedging cost £1,227.11
  - C8: actual £105.24 vs. naked £977.78 -- hedging cost £872.54
  - C9: actual £299.80 vs. naked £1,159.88 -- hedging cost £860.08
  - C_IC1: actual £95,584.02 vs. naked £179,769.28 -- hedging cost £84,185.26
  - C_IC2: actual £732.56 vs. naked £40,007.53 -- hedging cost £39,274.97

**Year narrative:** 2018 produced a net gain of £88,733.44 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 34 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £216,738.45 (gross £686,422.94, capital £3,509.60)
  - Electricity: gross £655,296.34, capital £2,114.13, net £252,411.25
  - Gas: gross £31,126.60, capital £1,395.46, net £-35,672.79
- Treasury at year end: £2,642,304.17
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.90 (avg 0.90), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.92 (avg 0.92), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2019-09-01 period 1, net margin £-141.19

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £198,822.01
  - By billing account: C1 £2,002.63, C2 £4,925.00, C3 £2,463.48, C4 £3,186.21, C5 £6,824.88, C6 £8,849.66, C7 £5,101.76, C8 £6,033.91, C9 £6,919.74, C_IC1 £1,213,609.45, C_IC2 £927,125.34
- Bill shock events (>=20%): 35 -- C1 2019-04-30 (22%); C5 2019-01-31 (40%); C5 2019-02-28 (22%); C5 2019-06-30 (26%); C5 2019-10-31 (44%); C5 2019-11-30 (36%); C7 2019-01-31 (43%); C7 2019-02-28 (27%); C7 2019-05-31 (24%); C7 2019-06-30 (36%); C7 2019-10-31 (74%); C7 2019-11-30 (46%); C6 2019-02-28 (21%); C6 2019-06-30 (25%); C6 2019-10-31 (42%); C6 2019-11-30 (27%); C8 2019-01-31 (27%); C8 2019-02-28 (28%); C8 2019-04-30 (21%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-09-30 (62%); C8 2019-10-31 (89%); C8 2019-11-30 (38%); C3 2019-04-30 (21%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (37%); C9 2019-07-31 (36%); C9 2019-09-30 (53%); C9 2019-10-31 (77%); C9 2019-11-30 (38%); C_IC1 2019-02-28 (52%); C_IC1 2019-03-31 (128%); C_IC2 2019-02-28 (66%)
- Churn risk (accounts renewing in 2019): 7 at risk (≥20% churn prob): C4 20%, C5 38%, C6 29%, C7 35%, C8 38%, C9 32%, C_IC1 20%

**Pricing & Margin**

- C1 (electricity): tariff £130.83-£158.03/MWh, net margin £40.22
- C1g (gas): tariff £24.11-£41.71/MWh, net margin £128.13
- C2 (electricity): tariff £148.32-£162.45/MWh, net margin £130.29
- C2g (gas): tariff £37.66-£39.86/MWh, net margin £189.34
- C3 (electricity): tariff £129.69-£142.04/MWh, net margin £19.60
- C3g (gas): tariff £29.22-£33.32/MWh, net margin £84.32
- C4 (electricity): tariff £131.63-£142.86/MWh, net margin £6.70
- C4g (gas): tariff £23.17-£33.85/MWh, net margin £38.21
- C5 (electricity): tariff £133.42-£159.93/MWh, net margin £120.53
- C6 (electricity): tariff £148.76-£160.61/MWh, net margin £176.13
- C7 (electricity): tariff £105.21-£235.50/MWh, net margin £187.95
- C8 (electricity): tariff £112.47-£228.37/MWh, net margin £263.74
- C9 (electricity): tariff £107.76-£220.02/MWh, net margin £286.15
- C_IC1 (electricity): tariff £0.00-£261.46/MWh, net margin £140,858.73
- C_IC2 (electricity): tariff £-60.00-£270.78/MWh, net margin £77,594.32
- C_IC3 (electricity): tariff £59.64-£113.86/MWh, net margin £32,726.89
- C_IC3g (gas): tariff £32.63/MWh, net margin £-36,112.79 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.878, average bill shock 12.3%, bad debt provision £35,138.41, avg complaint probability 3.7%
- Solvency signal: £220,192/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £243,919.80 vs. naked (unhedged) net margin: £859,139.84
- hedging cost £615,220.05 vs. a fully unhedged book (commodity-only: actual net £243,919.80 vs. naked net £859,139.84)
  - C1: actual £11.22 vs. naked £329.99 -- hedging cost £318.77
  - C1g: actual £40.56 vs. naked £175.31 -- hedging cost £134.75
  - C2: actual £180.50 vs. naked £869.19 -- hedging cost £688.70
  - C2g: actual £221.33 vs. naked £429.98 -- hedging cost £208.65
  - C3: actual £11.39 vs. naked £408.31 -- hedging cost £396.92
  - C3g: actual £123.49 vs. naked £281.47 -- hedging cost £157.97
  - C4: actual £54.66 vs. naked £533.21 -- hedging cost £478.55
  - C4g: actual £106.25 vs. naked £322.45 -- hedging cost £216.20
  - C5: actual £-22.75 vs. naked £1,572.06 -- hedging cost £1,594.81
  - C6: actual £320.93 vs. naked £2,187.66 -- hedging cost £1,866.73
  - C7: actual £118.09 vs. naked £1,158.72 -- hedging cost £1,040.63
  - C8: actual £358.83 vs. naked £1,443.54 -- hedging cost £1,084.71
  - C9: actual £271.57 vs. naked £1,329.39 -- hedging cost £1,057.82
  - C_IC1: actual £160,678.92 vs. naked £298,959.85 -- hedging cost £138,280.93
  - C_IC2: actual £84,830.72 vs. naked £159,477.01 -- hedging cost £74,646.29
  - C_IC3: actual £32,726.89 vs. naked £324,084.64 -- hedging cost £291,357.75
  - C_IC3g: actual £-36,112.79 vs. naked £65,577.06 -- hedging cost £101,689.86

**Year narrative:** 2019 produced a net gain of £216,738.45 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 35 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-14,007.01 (gross £650,711.25, capital £2,710.31)
  - Electricity: gross £588,289.20, capital £1,896.14, net £-9,204.22
  - Gas: gross £62,422.05, capital £814.17, net £-4,802.79
- Treasury at year end: £2,747,139.39
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.90 (avg 0.90), C1g 0.85 (avg 0.85), C2 0.88 (avg 0.88), C2g 0.85 (avg 0.85), C4 0.86 (avg 0.86), C4g 0.85 (avg 0.85), C5 0.90 (avg 0.90), C6 0.88 (avg 0.88), C7 0.89 (avg 0.89), C8 0.88 (avg 0.88), C9 0.87 (avg 0.87), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.85 (avg 0.85), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2020-05-01 period 1, net margin £-66.95

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2020): £242,349.60
  - By billing account: C1 £2,108.63, C2 £5,308.13, C3 £2,289.12, C4 £2,913.48, C5 £7,341.42, C6 £8,959.17, C7 £4,888.42, C8 £6,215.33, C9 £6,163.99, C_IC1 £910,253.30, C_IC2 £550,780.31, C_IC3 £1,617,738.39, C_IC4 £25,585.19
- Bill shock events (>=20%): 33 -- C1 2020-04-30 (21%); C1g 2020-01-31 (29%); C5 2020-04-30 (29%); C5 2020-10-31 (39%); C5 2020-12-31 (26%); C7 2020-04-30 (35%); C7 2020-05-31 (22%); C7 2020-06-30 (28%); C7 2020-10-31 (63%); C7 2020-11-30 (24%); C7 2020-12-31 (36%); C2g 2020-04-30 (29%); C6 2020-04-30 (30%); C6 2020-09-30 (21%); C6 2020-10-31 (34%); C6 2020-12-31 (26%); C8 2020-04-30 (38%); C8 2020-05-31 (26%); C8 2020-06-30 (33%); C8 2020-09-30 (57%); C8 2020-10-31 (68%); C8 2020-12-31 (44%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-09-30 (47%); C9 2020-10-31 (52%); C9 2020-12-31 (37%); C_IC1 2020-03-31 (58%); C_IC1 2020-04-30 (89%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (137%); C_IC4 2020-12-31 (21%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 26%, C5 35%, C6 32%, C7 38%, C8 38%, C9 41%, C_IC4 23%

**Pricing & Margin**

- C1 (electricity): tariff £130.83-£141.25/MWh, net margin £10.92
- C1g (gas): tariff £24.11-£24.69/MWh, net margin £40.49
- C2 (electricity): tariff £153.85-£162.45/MWh, net margin £215.17
- C2g (gas): tariff £24.88-£39.86/MWh, net margin £140.28
- C3 (electricity): tariff £129.69/MWh, net margin £5.30
- C3g (gas): tariff £29.22/MWh, net margin £64.76
- C4 (electricity): tariff £112.19-£131.63/MWh, net margin £9.84
- C4g (gas): tariff £15.74-£23.17/MWh, net margin £68.57
- C5 (electricity): tariff £133.42-£146.15/MWh, net margin £-24.54 -- **net-negative**
- C6 (electricity): tariff £153.85-£160.61/MWh, net margin £402.80
- C7 (electricity): tariff £105.21-£224.21/MWh, net margin £121.00
- C8 (electricity): tariff £116.29-£228.37/MWh, net margin £424.38
- C9 (electricity): tariff £91.30-£205.72/MWh, net margin £205.40
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £79,304.37
- C_IC2 (electricity): tariff £-79.50-£270.78/MWh, net margin £57,707.01
- C_IC3 (electricity): tariff £39.07-£86.40/MWh, net margin £22,394.33
- C_IC3g (gas): tariff £16.07-£17.16/MWh, net margin £-5,116.89 -- **net-negative**
- C_IC4 (electricity): tariff £18.53-£73.19/MWh, net margin £-169,980.21 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.877, average bill shock 11.7%, bad debt provision £35,857.70, avg complaint probability 3.6%
- Solvency signal: £211,318/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-68,543.30 vs. naked (unhedged) net margin: £625,249.70
- hedging cost £693,793.01 vs. a fully unhedged book (commodity-only: actual net £-68,543.30 vs. naked net £625,249.70)
  - C1: actual £-26.29 vs. naked £26.52 -- hedging cost £52.80
  - C1g: actual £-53.63 vs. naked £-225.24 -- hedging added £171.61
  - C2: actual £219.02 vs. naked £757.37 -- hedging cost £538.35
  - C2g: actual £107.34 vs. naked £201.49 -- hedging cost £94.16
  - C4: actual £-115.80 vs. naked £188.34 -- hedging cost £304.14
  - C4g: actual £-114.12 vs. naked £-214.39 -- hedging added £100.27
  - C5: actual £-181.26 vs. naked £207.43 -- hedging cost £388.69
  - C6: actual £421.14 vs. naked £1,809.98 -- hedging cost £1,388.84
  - C7: actual £72.39 vs. naked £335.53 -- hedging cost £263.14
  - C8: actual £450.19 vs. naked £1,184.04 -- hedging cost £733.85
  - C9: actual £103.78 vs. naked £708.68 -- hedging cost £604.90
  - C_IC1: actual £69,870.52 vs. naked £158,888.23 -- hedging cost £89,017.71
  - C_IC2: actual £59,906.72 vs. naked £110,636.62 -- hedging cost £50,729.90
  - C_IC3: actual £13,331.60 vs. naked £220,831.07 -- hedging cost £207,499.47
  - C_IC3g: actual £120,545.96 vs. naked £146,590.86 -- hedging cost £26,044.90
  - C_IC4: actual £-333,080.86 vs. naked £-16,676.84 -- hedging cost £316,404.02

**Year narrative:** 2020 produced a net loss of £-14,007.01 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £68,421.49 (gross £722,344.73, capital £6,746.95)
  - Electricity: gross £522,899.11, capital £5,610.67, net £-56,978.95
  - Gas: gross £199,445.62, capital £1,136.28, net £125,400.43
- Treasury at year end: £2,784,668.15
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C4 0.92 (avg 0.92), C4g 0.85 (avg 0.85), C6 0.91 (avg 0.91), C7 0.94 (avg 0.94), C8 0.91 (avg 0.91), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.95 (avg 0.95), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2021-12-31 period 1, net margin £-85.79

**Customer Book**

- Active accounts: 16 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £226,225.80
  - By billing account: C1 £1,953.84, C2 £4,791.45, C3 £2,085.18, C4 £2,644.54, C5 £6,081.40, C6 £8,547.49, C7 £4,779.15, C8 £6,024.27, C9 £5,088.63, C_IC1 £809,116.41, C_IC2 £507,277.61, C_IC3 £1,562,198.90, C_IC4 £20,346.53
- Bill shock events (>=20%): 38 -- C1 2021-04-30 (20%); C5 2021-05-31 (23%); C5 2021-06-30 (32%); C5 2021-10-31 (30%); C5 2021-11-30 (51%); C7 2021-05-31 (31%); C7 2021-06-30 (48%); C7 2021-10-31 (56%); C7 2021-11-30 (67%); C6 2021-06-30 (36%); C6 2021-10-31 (28%); C6 2021-11-30 (50%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (26%); C8 2021-10-31 (69%); C8 2021-11-30 (85%); C9 2021-02-28 (21%); C9 2021-05-31 (25%); C9 2021-06-30 (52%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-10-31 (63%); C9 2021-11-30 (50%); C9 2021-12-31 (24%); C4 2021-10-31 (75%); C4g 2021-10-31 (145%); C_IC1 2021-04-30 (24%); C_IC1 2021-05-31 (50%); C_IC2 2021-03-31 (31%); C_IC2 2021-04-30 (78%); C_IC3g 2021-09-30 (23%); C_IC3g 2021-10-31 (28%); C_IC3g 2021-12-31 (31%); C_IC4 2021-02-28 (28%); C_IC4 2021-07-31 (22%); C_IC4 2021-09-30 (40%); C_IC4 2021-12-31 (29%)
- Churn risk (accounts renewing in 2021): 9 at risk (≥20% churn prob): C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC3 20%, C_IC4 32%

**Pricing & Margin**

- C1 (electricity): tariff £141.25/MWh, net margin £-25.93 -- **net-negative**
- C1g (gas): tariff £24.69/MWh, net margin £-53.49 -- **net-negative**
- C2 (electricity): tariff £153.85-£186.79/MWh, net margin £196.14
- C2g (gas): tariff £24.88-£32.69/MWh, net margin £17.34
- C4 (electricity): tariff £112.19-£224.29/MWh, net margin £-119.71 -- **net-negative**
- C4g (gas): tariff £15.74-£60.39/MWh, net margin £-140.48 -- **net-negative**
- C5 (electricity): tariff £146.15/MWh, net margin £-179.00 -- **net-negative**
- C6 (electricity): tariff £153.85-£186.79/MWh, net margin £349.43
- C7 (electricity): tariff £117.44-£384.87/MWh, net margin £64.01
- C8 (electricity): tariff £116.29-£280.19/MWh, net margin £469.61
- C9 (electricity): tariff £91.30-£241.03/MWh, net margin £19.32
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £63,010.50
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £52,765.63
- C_IC3 (electricity): tariff £45.26-£274.41/MWh, net margin £-9,969.67 -- **net-negative**
- C_IC3g (gas): tariff £16.07-£84.48/MWh, net margin £125,577.06
- C_IC4 (electricity): tariff £42.47-£336.77/MWh, net margin £-163,559.27 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.867, average bill shock 13.5%, bad debt provision £46,095.17, avg complaint probability 3.9%
- Solvency signal: £232,056/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-151,422.03 vs. naked (unhedged) net margin: £-159,470.77
- hedging added £8,048.74 vs. a fully unhedged book (commodity-only: actual net £-151,422.03 vs. naked net £-159,470.77)
  - C2: actual £164.91 vs. naked £164.56 -- hedging added £0.35
  - C2g: actual £-26.58 vs. naked £-422.64 -- hedging added £396.07
  - C4: actual £-155.80 vs. naked £-73.26 -- hedging cost £82.54
  - C4g: actual £-233.26 vs. naked £-1,027.60 -- hedging added £794.33
  - C6: actual £234.41 vs. naked £-123.97 -- hedging added £358.37
  - C7: actual £-726.46 vs. naked £-119.17 -- hedging cost £607.29
  - C8: actual £426.35 vs. naked £37.77 -- hedging added £388.57
  - C9: actual £-126.67 vs. naked £-510.93 -- hedging added £384.27
  - C_IC1: actual £69,731.33 vs. naked £-43,940.18 -- hedging added £113,671.50
  - C_IC2: actual £57,464.14 vs. naked £4,312.96 -- hedging added £53,151.19
  - C_IC3: actual £-173,158.95 vs. naked £-96,268.96 -- hedging cost £76,889.99
  - C_IC3g: actual £43,578.41 vs. naked £38,284.45 -- hedging added £5,293.96
  - C_IC4: actual £-148,593.86 vs. naked £-59,783.81 -- hedging cost £88,810.05

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £68,421.49 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £-9,239.70 (gross £609,362.42, capital £14,842.43)
  - Electricity: gross £481,452.81, capital £12,356.05, net £-52,988.88
  - Gas: gross £127,909.61, capital £2,486.38, net £43,749.19
- Treasury at year end: £2,637,119.86
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.94 (avg 0.94), C2g 0.85 (avg 0.85), C4 0.95 (avg 0.95), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.94 (avg 0.94), C8 0.94 (avg 0.94), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.98), C_IC3 0.96 (avg 0.96), C_IC3g 1.00 (avg 1.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £2,915,911.12, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,066.97 / stressed £20,776.32) ratio 2.70
  - 2022-05-29: treasury £2,916,135.04, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,198.64 / stressed £20,815.82) ratio 2.70
  - 2022-06-28: treasury £2,916,122.77, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,198.64 / stressed £20,815.82) ratio 2.70
  - 2022-07-28: treasury £2,916,000.08, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,332.87 / stressed £20,847.41) ratio 2.70
  - 2022-08-27: treasury £2,915,984.00, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,332.87 / stressed £20,847.41) ratio 2.70
  - 2022-09-26: treasury £2,915,968.50, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,332.87 / stressed £20,847.41) ratio 2.70
  - 2022-10-26: treasury £2,915,161.70, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,566.67 / stressed £20,923.85) ratio 2.70
  - 2022-11-25: treasury £2,915,108.26, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,566.67 / stressed £20,923.85) ratio 2.70
  - 2022-12-25: treasury £2,915,014.55, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,566.67 / stressed £20,923.85) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC3g on 2022-10-01 period 1, net margin £-463.03

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2022): £215,683.82
  - By billing account: C1 £1,703.89, C2 £4,621.27, C3 £2,103.29, C4 £2,251.19, C5 £6,161.12, C6 £8,298.97, C7 £4,109.10, C8 £5,955.14, C9 £5,860.09, C_IC1 £948,814.63, C_IC2 £498,997.35, C_IC3 £1,300,006.94, C_IC4 £15,006.63
- Bill shock events (>=20%): 51 -- C7 2022-01-31 (78%); C7 2022-02-28 (27%); C7 2022-04-30 (23%); C7 2022-05-31 (37%); C7 2022-06-30 (27%); C7 2022-09-30 (35%); C7 2022-11-30 (65%); C7 2022-12-31 (57%); C2 2022-04-30 (52%); C2g 2022-04-30 (152%); C6 2022-04-30 (45%); C6 2022-05-31 (23%); C6 2022-09-30 (26%); C6 2022-11-30 (44%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-04-30 (31%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (86%); C8 2022-11-30 (73%); C8 2022-12-31 (58%); C9 2022-04-30 (21%); C9 2022-05-31 (30%); C9 2022-06-30 (30%); C9 2022-07-31 (26%); C9 2022-09-30 (51%); C9 2022-10-31 (31%); C9 2022-11-30 (46%); C9 2022-12-31 (53%); C4 2022-10-31 (56%); C4g 2022-10-31 (159%); C_IC1 2022-06-30 (88%); C_IC2 2022-05-31 (60%); C_IC3 2022-01-31 (63%); C_IC3g 2022-03-31 (55%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (46%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-09-30 (21%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (21%); C_IC3g 2022-12-31 (21%); C_IC4 2022-02-28 (21%); C_IC4 2022-03-31 (44%); C_IC4 2022-05-31 (21%); C_IC4 2022-07-31 (38%); C_IC4 2022-08-31 (41%); C_IC4 2022-10-31 (39%); C_IC4 2022-12-31 (102%)
- Churn risk (accounts renewing in 2022): 8 at risk (≥20% churn prob): C4 23%, C6 29%, C7 35%, C8 38%, C9 41%, C_IC1 20%, C_IC3 29%, C_IC4 38%

**Pricing & Margin**

- C2 (electricity): tariff £186.79-£392.42/MWh, net margin £308.80
- C2g (gas): tariff £32.69-£117.83/MWh, net margin £44.52
- C4 (electricity): tariff £224.29-£348.03/MWh, net margin £-191.35 -- **net-negative**
- C4g (gas): tariff £60.39-£182.83/MWh, net margin £-86.22 -- **net-negative**
- C6 (electricity): tariff £186.79-£384.50/MWh, net margin £476.17
- C7 (electricity): tariff £201.60-£586.67/MWh, net margin £-718.06 -- **net-negative**
- C8 (electricity): tariff £146.77-£552.10/MWh, net margin £545.62
- C9 (electricity): tariff £126.26-£469.79/MWh, net margin £283.81
- C_IC1 (electricity): tariff £-83.39-£470.63/MWh, net margin £183,054.63
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £84,262.42
- C_IC3 (electricity): tariff £143.74-£274.41/MWh, net margin £-172,504.35 -- **net-negative**
- C_IC3g (gas): tariff £84.48-£160.16/MWh, net margin £43,790.89
- C_IC4 (electricity): tariff £71.50-£469.98/MWh, net margin £-148,506.58 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.4% of gross
- Treasury drawdown events (>=10% threshold): 857 -- £3,002,084.07 -> £2,636,926.26 (12.2%); £3,002,084.16 -> £2,636,926.71 (12.2%); £3,002,084.25 -> £2,636,926.72 (12.2%); £3,002,084.27 -> £2,636,926.72 (12.2%); £3,002,084.29 -> £2,636,926.73 (12.2%); £3,002,084.36 -> £2,636,926.90 (12.2%); £3,002,084.44 -> £2,636,926.92 (12.2%); £3,002,084.53 -> £2,636,926.94 (12.2%); £3,002,084.62 -> £2,636,926.96 (12.2%); £3,002,084.70 -> £2,636,927.59 (12.2%); £3,002,084.85 -> £2,636,927.60 (12.2%); £3,002,084.99 -> £2,636,927.61 (12.2%); £3,002,085.14 -> £2,636,927.62 (12.2%); £3,002,085.18 -> £2,636,927.63 (12.2%); £3,002,085.23 -> £2,636,927.64 (12.2%); £3,002,085.23 -> £2,636,927.74 (12.2%); £3,002,085.37 -> £2,636,927.76 (12.2%); £3,002,085.51 -> £2,636,927.78 (12.2%); £3,002,085.65 -> £2,636,927.80 (12.2%); £3,002,085.78 -> £2,636,927.82 (12.2%); £3,002,085.91 -> £2,636,927.83 (12.2%); £3,002,086.04 -> £2,636,927.85 (12.2%); £3,002,086.17 -> £2,636,927.87 (12.2%); £3,002,086.19 -> £2,636,930.63 (12.2%); £3,002,086.36 -> £2,636,930.64 (12.2%); £3,002,086.53 -> £2,636,930.65 (12.2%); £3,002,086.58 -> £2,636,930.66 (12.2%); £3,002,086.63 -> £2,636,930.66 (12.2%); £3,002,086.65 -> £2,636,930.77 (12.2%); £3,002,086.80 -> £2,636,930.80 (12.2%); £3,002,086.96 -> £2,636,930.82 (12.2%); £3,002,087.12 -> £2,636,930.84 (12.2%); £3,002,087.28 -> £2,636,930.86 (12.2%); £3,002,087.43 -> £2,636,930.88 (12.2%); £3,002,087.59 -> £2,636,930.90 (12.2%); £3,002,087.74 -> £2,636,930.92 (12.2%); £3,002,087.75 -> £2,636,931.58 (12.2%); £3,002,087.87 -> £2,636,931.59 (12.2%); £3,002,087.99 -> £2,636,931.60 (12.2%); £3,002,088.11 -> £2,636,931.61 (12.2%); £3,002,088.23 -> £2,636,931.62 (12.2%); £3,002,088.35 -> £2,636,931.63 (12.2%); £3,002,088.39 -> £2,636,931.64 (12.2%); £3,002,088.44 -> £2,636,931.64 (12.2%); £3,002,088.55 -> £2,636,931.75 (12.2%); £3,002,088.66 -> £2,636,931.77 (12.2%); £3,002,088.77 -> £2,636,931.78 (12.2%); £3,002,088.89 -> £2,636,931.80 (12.2%); £3,002,089.00 -> £2,636,931.81 (12.2%); £3,002,089.10 -> £2,636,931.83 (12.2%); £3,002,089.21 -> £2,636,931.84 (12.2%); £3,002,089.25 -> £2,636,932.48 (12.2%); £3,002,089.35 -> £2,636,932.49 (12.2%); £3,002,089.44 -> £2,636,932.50 (12.2%); £3,002,089.52 -> £2,636,932.51 (12.2%); £3,002,089.61 -> £2,636,932.51 (12.2%); £3,002,089.66 -> £2,636,932.52 (12.2%); £3,002,089.70 -> £2,636,932.53 (12.2%); £3,002,089.72 -> £2,636,932.63 (12.2%); £3,002,089.81 -> £2,636,932.65 (12.2%); £3,002,089.90 -> £2,636,932.67 (12.2%); £3,002,090.00 -> £2,636,932.69 (12.2%); £3,002,090.10 -> £2,636,932.72 (12.2%); £3,002,090.20 -> £2,636,932.73 (12.2%); £3,002,090.28 -> £2,636,932.75 (12.2%); £3,002,090.37 -> £2,636,932.77 (12.2%); £3,002,090.38 -> £2,636,933.44 (12.2%); £3,002,090.43 -> £2,636,933.45 (12.2%); £3,002,090.47 -> £2,636,933.46 (12.2%); £3,002,090.52 -> £2,636,933.47 (12.2%); £3,002,090.56 -> £2,636,933.48 (12.2%); £3,002,090.60 -> £2,636,933.49 (12.2%); £3,002,090.65 -> £2,636,933.50 (12.2%); £3,002,090.67 -> £2,636,933.60 (12.2%); £3,002,090.73 -> £2,636,933.63 (12.2%); £3,002,090.79 -> £2,636,933.64 (12.2%); £3,002,090.85 -> £2,636,933.66 (12.2%); £3,002,090.91 -> £2,636,933.68 (12.2%); £3,002,090.97 -> £2,636,933.70 (12.2%); £3,002,091.02 -> £2,636,933.71 (12.2%); £3,002,091.07 -> £2,636,933.72 (12.2%); £3,002,091.15 -> £2,636,934.37 (12.2%); £3,002,091.24 -> £2,636,934.38 (12.2%); £3,002,091.32 -> £2,636,934.39 (12.2%); £3,002,091.41 -> £2,636,934.40 (12.2%); £3,002,091.50 -> £2,636,934.41 (12.2%); £3,002,091.54 -> £2,636,934.42 (12.2%); £3,002,091.59 -> £2,636,934.43 (12.2%); £3,002,091.60 -> £2,636,934.53 (12.2%); £3,002,091.69 -> £2,636,934.55 (12.2%); £3,002,091.78 -> £2,636,934.56 (12.2%); £3,002,091.87 -> £2,636,934.58 (12.2%); £3,002,091.96 -> £2,636,934.60 (12.2%); £3,002,092.05 -> £2,636,934.61 (12.2%); £3,002,092.13 -> £2,636,934.63 (12.2%); £3,002,092.21 -> £2,636,934.65 (12.2%); £3,002,092.26 -> £2,636,937.49 (12.2%); £3,002,092.31 -> £2,636,937.51 (12.2%); £3,002,092.37 -> £2,636,937.52 (12.2%); £3,002,092.42 -> £2,636,937.53 (12.2%); £3,002,092.46 -> £2,636,938.16 (12.2%); £3,002,092.50 -> £2,636,938.17 (12.2%); £3,002,092.55 -> £2,636,938.18 (12.2%); £3,002,092.59 -> £2,636,938.19 (12.2%); £3,002,092.63 -> £2,636,938.20 (12.2%); £3,002,092.68 -> £2,636,938.20 (12.2%); £3,002,092.71 -> £2,636,938.29 (12.2%); £3,002,092.77 -> £2,636,938.31 (12.2%); £3,002,092.83 -> £2,636,938.32 (12.2%); £3,002,092.88 -> £2,636,938.34 (12.2%); £3,002,092.94 -> £2,636,938.35 (12.2%); £3,002,092.99 -> £2,636,938.36 (12.2%); £3,002,093.04 -> £2,636,938.37 (12.2%); £3,002,093.15 -> £2,636,938.97 (12.2%); £3,002,093.26 -> £2,636,938.98 (12.2%); £3,002,093.37 -> £2,636,938.99 (12.2%); £3,002,093.48 -> £2,636,939.00 (12.2%); £3,002,093.59 -> £2,636,939.01 (12.2%); £3,002,093.63 -> £2,636,939.02 (12.2%); £3,002,093.68 -> £2,636,939.03 (12.2%); £3,002,093.69 -> £2,636,939.13 (12.2%); £3,002,093.80 -> £2,636,939.15 (12.2%); £3,002,093.91 -> £2,636,939.17 (12.2%); £3,002,094.02 -> £2,636,939.19 (12.2%); £3,002,094.14 -> £2,636,939.21 (12.2%); £3,002,094.24 -> £2,636,939.23 (12.2%); £3,002,094.35 -> £2,636,939.25 (12.2%); £3,002,094.46 -> £2,636,939.26 (12.2%); £3,002,094.58 -> £2,636,939.90 (12.2%); £3,002,094.71 -> £2,636,939.91 (12.2%); £3,002,094.83 -> £2,636,939.92 (12.2%); £3,002,094.95 -> £2,636,939.93 (12.2%); £3,002,095.07 -> £2,636,939.94 (12.2%); £3,002,095.12 -> £2,636,939.95 (12.2%); £3,002,095.17 -> £2,636,939.96 (12.2%); £3,002,095.18 -> £2,636,940.06 (12.2%); £3,002,095.30 -> £2,636,940.08 (12.2%); £3,002,095.42 -> £2,636,940.10 (12.2%); £3,002,095.54 -> £2,636,940.12 (12.2%); £3,002,095.65 -> £2,636,940.15 (12.2%); £3,002,095.77 -> £2,636,940.17 (12.2%); £3,002,095.88 -> £2,636,940.18 (12.2%); £3,002,095.99 -> £2,636,940.20 (12.2%); £3,002,096.01 -> £2,636,940.87 (12.2%); £3,002,096.07 -> £2,636,940.89 (12.2%); £3,002,096.13 -> £2,636,940.90 (12.2%); £3,002,096.18 -> £2,636,940.91 (12.2%); £3,002,096.24 -> £2,636,940.92 (12.2%); £3,002,096.29 -> £2,636,940.93 (12.2%); £3,002,096.33 -> £2,636,940.94 (12.2%); £3,002,096.35 -> £2,636,941.04 (12.2%); £3,002,096.42 -> £2,636,941.06 (12.2%); £3,002,096.49 -> £2,636,941.08 (12.2%); £3,002,096.56 -> £2,636,941.11 (12.2%); £3,002,096.63 -> £2,636,941.13 (12.2%); £3,002,096.70 -> £2,636,941.15 (12.2%); £3,002,096.77 -> £2,636,941.17 (12.2%); £3,002,096.84 -> £2,636,941.18 (12.2%); £3,002,096.88 -> £2,636,944.23 (12.2%); £3,002,096.94 -> £2,636,944.24 (12.2%); £3,002,096.99 -> £2,636,944.25 (12.2%); £3,002,097.04 -> £2,636,944.27 (12.2%); £3,002,097.09 -> £2,636,944.29 (12.2%); £3,002,097.12 -> £2,636,944.87 (12.2%); £3,002,097.16 -> £2,636,944.88 (12.2%); £3,002,097.21 -> £2,636,944.89 (12.2%); £3,002,097.25 -> £2,636,944.89 (12.2%); £3,002,097.29 -> £2,636,944.90 (12.2%); £3,002,097.34 -> £2,636,944.91 (12.2%); £3,002,097.37 -> £2,636,945.10 (12.2%); £3,002,097.43 -> £2,636,945.12 (12.2%); £3,002,097.49 -> £2,636,945.13 (12.2%); £3,002,097.54 -> £2,636,945.14 (12.2%); £3,002,097.59 -> £2,636,945.14 (12.2%); £3,002,097.64 -> £2,636,945.15 (12.2%); £3,002,097.69 -> £2,636,945.16 (12.2%); £3,002,097.73 -> £2,636,945.82 (12.2%); £3,002,097.78 -> £2,636,945.83 (12.2%); £3,002,097.82 -> £2,636,945.85 (12.2%); £3,002,097.87 -> £2,636,945.85 (12.2%); £3,002,097.92 -> £2,636,945.86 (12.2%); £3,002,097.96 -> £2,636,945.87 (12.2%); £3,002,097.97 -> £2,636,945.97 (12.2%); £3,002,098.03 -> £2,636,945.99 (12.2%); £3,002,098.09 -> £2,636,946.01 (12.2%); £3,002,098.15 -> £2,636,946.03 (12.2%); £3,002,098.21 -> £2,636,946.05 (12.2%); £3,002,098.27 -> £2,636,946.07 (12.2%); £3,002,098.33 -> £2,636,946.09 (12.2%); £3,002,098.38 -> £2,636,946.11 (12.2%); £3,002,098.40 -> £2,636,946.80 (12.2%); £3,002,098.45 -> £2,636,946.81 (12.2%); £3,002,098.50 -> £2,636,946.82 (12.2%); £3,002,098.55 -> £2,636,946.83 (12.2%); £3,002,098.59 -> £2,636,946.84 (12.2%); £3,002,098.64 -> £2,636,946.85 (12.2%); £3,002,098.68 -> £2,636,946.85 (12.2%); £3,002,098.74 -> £2,636,946.97 (12.2%); £3,002,098.80 -> £2,636,946.99 (12.2%); £3,002,098.86 -> £2,636,947.01 (12.2%); £3,002,098.93 -> £2,636,947.04 (12.2%); £3,002,098.99 -> £2,636,947.06 (12.2%); £3,002,099.04 -> £2,636,947.08 (12.2%); £3,002,099.10 -> £2,636,947.09 (12.2%); £3,002,099.14 -> £2,636,947.76 (12.2%); £3,002,099.21 -> £2,636,947.77 (12.2%); £3,002,099.27 -> £2,636,947.78 (12.2%); £3,002,099.33 -> £2,636,947.79 (12.2%); £3,002,099.39 -> £2,636,947.80 (12.2%); £3,002,099.44 -> £2,636,947.81 (12.2%); £3,002,099.48 -> £2,636,947.82 (12.2%); £3,002,099.48 -> £2,636,947.91 (12.2%); £3,002,099.55 -> £2,636,947.93 (12.2%); £3,002,099.63 -> £2,636,947.94 (12.2%); £3,002,099.70 -> £2,636,947.96 (12.2%); £3,002,099.77 -> £2,636,947.97 (12.2%); £3,002,099.83 -> £2,636,947.99 (12.2%); £3,002,099.90 -> £2,636,948.01 (12.2%); £3,002,099.96 -> £2,636,948.02 (12.2%); £3,002,099.99 -> £2,636,950.68 (12.2%); £3,002,100.05 -> £2,636,950.70 (12.2%); £3,002,100.10 -> £2,636,950.71 (12.2%); £3,002,100.15 -> £2,636,950.73 (12.2%); £3,002,100.18 -> £2,636,951.39 (12.2%); £3,002,100.30 -> £2,636,951.40 (12.2%); £3,002,100.43 -> £2,636,951.41 (12.2%); £3,002,100.56 -> £2,636,951.42 (12.2%); £3,002,100.67 -> £2,636,951.43 (12.2%); £3,002,100.80 -> £2,636,951.44 (12.2%); £3,002,100.84 -> £2,636,951.45 (12.2%); £3,002,100.89 -> £2,636,951.45 (12.2%); £3,002,100.90 -> £2,636,951.55 (12.2%); £3,002,101.01 -> £2,636,951.58 (12.2%); £3,002,101.14 -> £2,636,951.59 (12.2%); £3,002,101.25 -> £2,636,951.61 (12.2%); £3,002,101.37 -> £2,636,951.63 (12.2%); £3,002,101.49 -> £2,636,951.65 (12.2%); £3,002,101.59 -> £2,636,951.66 (12.2%); £3,002,101.69 -> £2,636,951.67 (12.2%); £3,002,101.70 -> £2,636,952.30 (12.2%); £3,002,101.84 -> £2,636,952.31 (12.2%); £3,002,101.98 -> £2,636,952.32 (12.2%); £3,002,102.12 -> £2,636,952.33 (12.2%); £3,002,102.25 -> £2,636,952.34 (12.2%); £3,002,102.39 -> £2,636,952.35 (12.2%); £3,002,102.43 -> £2,636,952.36 (12.2%); £3,002,102.48 -> £2,636,952.37 (12.2%); £3,002,102.49 -> £2,636,952.47 (12.2%); £3,002,102.61 -> £2,636,952.49 (12.2%); £3,002,102.74 -> £2,636,952.51 (12.2%); £3,002,102.87 -> £2,636,952.53 (12.2%); £3,002,102.99 -> £2,636,952.55 (12.2%); £3,002,103.12 -> £2,636,952.56 (12.2%); £3,002,103.24 -> £2,636,952.58 (12.2%); £3,002,103.37 -> £2,636,952.60 (12.2%); £3,002,103.45 -> £2,636,953.25 (12.2%); £3,002,103.56 -> £2,636,953.26 (12.2%); £3,002,103.67 -> £2,636,953.27 (12.2%); £3,002,103.78 -> £2,636,953.28 (12.2%); £3,002,103.90 -> £2,636,953.29 (12.2%); £3,002,103.94 -> £2,636,953.30 (12.2%); £3,002,103.99 -> £2,636,953.31 (12.2%); £3,002,104.00 -> £2,636,953.40 (12.2%); £3,002,104.10 -> £2,636,953.42 (12.2%); £3,002,104.21 -> £2,636,953.44 (12.2%); £3,002,104.32 -> £2,636,953.46 (12.2%); £3,002,104.43 -> £2,636,953.48 (12.2%); £3,002,104.54 -> £2,636,953.50 (12.2%); £3,002,104.64 -> £2,636,953.51 (12.2%); £3,002,104.74 -> £2,636,953.53 (12.2%); £3,002,104.77 -> £2,636,954.14 (12.2%); £3,002,104.81 -> £2,636,954.15 (12.2%); £3,002,104.86 -> £2,636,954.16 (12.2%); £3,002,104.90 -> £2,636,954.17 (12.2%); £3,002,104.95 -> £2,636,954.18 (12.2%); £3,002,105.00 -> £2,636,954.28 (12.2%); £3,002,105.05 -> £2,636,954.29 (12.2%); £3,002,105.11 -> £2,636,954.31 (12.2%); £3,002,105.16 -> £2,636,954.32 (12.2%); £3,002,105.22 -> £2,636,954.34 (12.2%); £3,002,105.27 -> £2,636,954.35 (12.2%); £3,002,105.32 -> £2,636,954.37 (12.2%); £3,002,105.34 -> £2,636,956.83 (12.2%); £3,002,105.35 -> £2,636,956.94 (12.2%); £3,002,105.45 -> £2,636,956.96 (12.2%); £3,002,105.56 -> £2,636,956.97 (12.2%); £3,002,105.65 -> £2,636,956.99 (12.2%); £3,002,105.75 -> £2,636,957.00 (12.2%); £3,002,105.84 -> £2,636,957.02 (12.2%); £3,002,105.94 -> £2,636,957.03 (12.2%); £3,002,106.03 -> £2,636,957.05 (12.2%); £3,002,106.04 -> £2,636,957.72 (12.2%); £3,002,106.09 -> £2,636,957.73 (12.2%); £3,002,106.13 -> £2,636,957.74 (12.2%); £3,002,106.18 -> £2,636,957.75 (12.2%); £3,002,106.22 -> £2,636,957.75 (12.2%); £3,002,106.27 -> £2,636,957.76 (12.2%); £3,002,106.28 -> £2,636,957.86 (12.2%); £3,002,106.33 -> £2,636,957.88 (12.2%); £3,002,106.40 -> £2,636,957.90 (12.2%); £3,002,106.45 -> £2,636,957.92 (12.2%); £3,002,106.51 -> £2,636,957.94 (12.2%); £3,002,106.57 -> £2,636,957.96 (12.2%); £3,002,106.62 -> £2,636,957.97 (12.2%); £3,002,106.67 -> £2,636,957.99 (12.2%); £3,002,106.72 -> £2,636,958.61 (12.2%); £3,002,106.77 -> £2,636,958.62 (12.2%); £3,002,106.82 -> £2,636,958.63 (12.2%); £3,002,106.86 -> £2,636,958.64 (12.2%); £3,002,106.91 -> £2,636,958.65 (12.2%); £3,002,106.96 -> £2,636,958.66 (12.2%); £3,002,107.01 -> £2,636,958.76 (12.2%); £3,002,107.07 -> £2,636,958.77 (12.2%); £3,002,107.12 -> £2,636,958.79 (12.2%); £3,002,107.18 -> £2,636,958.80 (12.2%); £3,002,107.24 -> £2,636,958.81 (12.2%); £3,002,107.29 -> £2,636,958.82 (12.2%); £3,002,107.34 -> £2,636,958.83 (12.2%); £3,002,107.34 -> £2,636,959.43 (12.2%); £3,002,107.48 -> £2,636,959.44 (12.2%); £3,002,107.62 -> £2,636,959.45 (12.2%); £3,002,107.77 -> £2,636,959.46 (12.2%); £3,002,107.91 -> £2,636,959.47 (12.2%); £3,002,108.05 -> £2,636,959.48 (12.2%); £3,002,108.10 -> £2,636,959.49 (12.2%); £3,002,108.15 -> £2,636,959.50 (12.2%); £3,002,108.16 -> £2,636,959.59 (12.2%); £3,002,108.29 -> £2,636,959.61 (12.2%); £3,002,108.41 -> £2,636,959.63 (12.2%); £3,002,108.55 -> £2,636,959.65 (12.2%); £3,002,108.68 -> £2,636,959.67 (12.2%); £3,002,108.80 -> £2,636,959.68 (12.2%); £3,002,108.93 -> £2,636,959.69 (12.2%); £3,002,109.05 -> £2,636,959.71 (12.2%); £3,002,109.05 -> £2,636,960.35 (12.2%); £3,002,109.23 -> £2,636,960.36 (12.2%); £3,002,109.42 -> £2,636,960.37 (12.2%); £3,002,109.60 -> £2,636,960.38 (12.2%); £3,002,109.79 -> £2,636,960.39 (12.2%); £3,002,109.98 -> £2,636,960.40 (12.2%); £3,002,110.03 -> £2,636,960.41 (12.2%); £3,002,110.08 -> £2,636,960.42 (12.2%); £3,002,110.08 -> £2,636,960.52 (12.2%); £3,002,110.25 -> £2,636,960.54 (12.2%); £3,002,110.41 -> £2,636,960.56 (12.2%); £3,002,110.57 -> £2,636,960.58 (12.2%); £3,002,110.73 -> £2,636,960.60 (12.2%); £3,002,110.89 -> £2,636,960.61 (12.2%); £3,002,111.04 -> £2,636,960.63 (12.2%); £3,002,111.19 -> £2,636,960.64 (12.2%); £3,002,111.24 -> £2,636,963.48 (12.2%); £3,002,111.29 -> £2,636,963.50 (12.2%); £3,002,111.32 -> £2,636,964.13 (12.2%); £3,002,111.36 -> £2,636,964.14 (12.2%); £3,002,111.40 -> £2,636,964.15 (12.2%); £3,002,111.45 -> £2,636,964.16 (12.2%); £3,002,111.50 -> £2,636,964.17 (12.2%); £3,002,111.55 -> £2,636,964.18 (12.2%); £3,002,111.55 -> £2,636,964.28 (12.2%); £3,002,111.61 -> £2,636,964.29 (12.2%); £3,002,111.67 -> £2,636,964.31 (12.2%); £3,002,111.72 -> £2,636,964.33 (12.2%); £3,002,111.78 -> £2,636,964.34 (12.2%); £3,002,111.83 -> £2,636,964.36 (12.2%); £3,002,111.88 -> £2,636,964.37 (12.2%); £3,002,111.93 -> £2,636,964.39 (12.2%); £3,002,111.96 -> £2,636,965.01 (12.2%); £3,002,112.00 -> £2,636,965.02 (12.2%); £3,002,112.05 -> £2,636,965.03 (12.2%); £3,002,112.09 -> £2,636,965.04 (12.2%); £3,002,112.14 -> £2,636,965.05 (12.2%); £3,002,112.19 -> £2,636,965.06 (12.2%); £3,002,112.24 -> £2,636,965.16 (12.2%); £3,002,112.30 -> £2,636,965.18 (12.2%); £3,002,112.35 -> £2,636,965.19 (12.2%); £3,002,112.41 -> £2,636,965.21 (12.2%); £3,002,112.46 -> £2,636,965.22 (12.2%); £3,002,112.51 -> £2,636,965.23 (12.2%); £3,002,112.56 -> £2,636,965.24 (12.2%); £3,002,112.56 -> £2,636,965.82 (12.2%); £3,002,112.60 -> £2,636,965.83 (12.2%); £3,002,112.64 -> £2,636,965.84 (12.2%); £3,002,112.69 -> £2,636,965.85 (12.2%); £3,002,112.73 -> £2,636,965.85 (12.2%); £3,002,112.78 -> £2,636,965.86 (12.2%); £3,002,112.82 -> £2,636,965.96 (12.2%); £3,002,112.88 -> £2,636,965.97 (12.2%); £3,002,112.93 -> £2,636,965.98 (12.2%); £3,002,112.98 -> £2,636,965.99 (12.2%); £3,002,113.03 -> £2,636,966.00 (12.2%); £3,002,113.08 -> £2,636,966.00 (12.2%); £3,002,113.12 -> £2,636,966.02 (12.2%); £3,002,113.16 -> £2,636,966.58 (12.2%); £3,002,113.20 -> £2,636,966.59 (12.2%); £3,002,113.25 -> £2,636,966.59 (12.2%); £3,002,113.29 -> £2,636,966.60 (12.2%); £3,002,113.34 -> £2,636,966.61 (12.2%); £3,002,113.34 -> £2,636,966.72 (12.2%); £3,002,113.40 -> £2,636,966.74 (12.2%); £3,002,113.46 -> £2,636,966.76 (12.2%); £3,002,113.51 -> £2,636,966.78 (12.2%); £3,002,113.57 -> £2,636,966.79 (12.2%); £3,002,113.62 -> £2,636,966.81 (12.2%); £3,002,113.67 -> £2,636,966.82 (12.2%); £3,002,113.72 -> £2,636,966.83 (12.2%); £3,002,113.73 -> £2,636,969.86 (12.2%); £3,002,113.78 -> £2,636,969.87 (12.2%); £3,002,113.83 -> £2,636,969.88 (12.2%); £3,002,113.88 -> £2,636,969.89 (12.2%); £3,002,113.92 -> £2,636,969.89 (12.2%); £3,002,113.97 -> £2,636,969.90 (12.2%); £3,002,114.00 -> £2,636,969.98 (12.2%); £3,002,114.05 -> £2,636,969.99 (12.2%); £3,002,114.11 -> £2,636,970.00 (12.2%); £3,002,114.17 -> £2,636,970.01 (12.2%); £3,002,114.22 -> £2,636,970.02 (12.2%); £3,002,114.28 -> £2,636,970.03 (12.2%); £3,002,114.33 -> £2,636,970.04 (12.2%); £3,002,114.44 -> £2,636,970.68 (12.2%); £3,002,114.56 -> £2,636,970.69 (12.2%); £3,002,114.68 -> £2,636,970.70 (12.2%); £3,002,114.79 -> £2,636,970.71 (12.2%); £3,002,114.90 -> £2,636,970.71 (12.2%); £3,002,114.95 -> £2,636,970.72 (12.2%); £3,002,114.99 -> £2,636,970.73 (12.2%); £3,002,115.06 -> £2,636,970.80 (12.2%); £3,002,115.16 -> £2,636,970.81 (12.2%); £3,002,115.26 -> £2,636,970.82 (12.2%); £3,002,115.35 -> £2,636,970.83 (12.2%); £3,002,115.45 -> £2,636,970.85 (12.2%); £3,002,115.56 -> £2,636,970.86 (12.2%); £3,002,115.66 -> £2,636,970.88 (12.2%); £3,002,115.69 -> £2,636,971.40 (12.2%); £3,002,115.74 -> £2,636,971.41 (12.2%); £3,002,115.79 -> £2,636,971.42 (12.2%); £3,002,115.84 -> £2,636,971.42 (12.2%); £3,002,115.88 -> £2,636,971.43 (12.2%); £3,002,115.94 -> £2,636,971.54 (12.2%); £3,002,116.00 -> £2,636,971.56 (12.2%); £3,002,116.07 -> £2,636,971.58 (12.2%); £3,002,116.13 -> £2,636,971.59 (12.2%); £3,002,116.19 -> £2,636,971.61 (12.2%); £3,002,116.25 -> £2,636,971.63 (12.2%); £3,002,116.31 -> £2,636,971.64 (12.2%); £3,002,116.39 -> £2,636,972.22 (12.2%); £3,002,116.51 -> £2,636,972.23 (12.2%); £3,002,116.62 -> £2,636,972.24 (12.2%); £3,002,116.74 -> £2,636,972.25 (12.2%); £3,002,116.86 -> £2,636,972.25 (12.2%); £3,002,116.90 -> £2,636,972.26 (12.2%); £3,002,116.95 -> £2,636,972.27 (12.2%); £3,002,116.95 -> £2,636,972.36 (12.2%); £3,002,117.06 -> £2,636,972.38 (12.2%); £3,002,117.18 -> £2,636,972.40 (12.2%); £3,002,117.29 -> £2,636,972.42 (12.2%); £3,002,117.40 -> £2,636,972.44 (12.2%); £3,002,117.51 -> £2,636,972.45 (12.2%); £3,002,117.62 -> £2,636,972.47 (12.2%); £3,002,117.72 -> £2,636,972.48 (12.2%); £3,002,117.76 -> £2,636,974.83 (12.2%); £3,002,117.87 -> £2,636,974.85 (12.2%); £3,002,117.98 -> £2,636,974.87 (12.2%); £3,002,118.09 -> £2,636,974.88 (12.2%); £3,002,118.19 -> £2,636,974.89 (12.2%); £3,002,118.29 -> £2,636,974.91 (12.2%); £3,002,118.31 -> £2,636,975.46 (12.2%); £3,002,118.35 -> £2,636,975.47 (12.2%); £3,002,118.39 -> £2,636,975.48 (12.2%); £3,002,118.43 -> £2,636,975.48 (12.2%); £3,002,118.48 -> £2,636,975.49 (12.2%); £3,002,118.49 -> £2,636,975.57 (12.2%); £3,002,118.55 -> £2,636,975.58 (12.2%); £3,002,118.60 -> £2,636,975.58 (12.2%); £3,002,118.65 -> £2,636,975.59 (12.2%); £3,002,118.70 -> £2,636,975.60 (12.2%); £3,002,118.74 -> £2,636,975.61 (12.2%); £3,002,118.79 -> £2,636,975.62 (12.2%); £3,002,118.80 -> £2,636,976.06 (12.2%); £3,002,118.84 -> £2,636,976.06 (12.2%); £3,002,118.88 -> £2,636,976.07 (12.2%); £3,002,118.92 -> £2,636,976.08 (12.2%); £3,002,118.97 -> £2,636,976.09 (12.2%); £3,002,119.01 -> £2,636,976.19 (12.2%); £3,002,119.07 -> £2,636,976.19 (12.2%); £3,002,119.12 -> £2,636,976.20 (12.2%); £3,002,119.17 -> £2,636,976.21 (12.2%); £3,002,119.21 -> £2,636,976.22 (12.2%); £3,002,119.26 -> £2,636,976.23 (12.2%); £3,002,119.30 -> £2,636,976.23 (12.2%); £3,002,119.37 -> £2,636,976.74 (12.2%); £3,002,119.45 -> £2,636,976.75 (12.2%); £3,002,119.54 -> £2,636,976.76 (12.2%); £3,002,119.63 -> £2,636,976.76 (12.2%); £3,002,119.67 -> £2,636,976.77 (12.2%); £3,002,119.71 -> £2,636,976.77 (12.2%); £3,002,119.75 -> £2,636,976.84 (12.2%); £3,002,119.84 -> £2,636,976.86 (12.2%); £3,002,119.93 -> £2,636,976.87 (12.2%); £3,002,120.03 -> £2,636,976.89 (12.2%); £3,002,120.12 -> £2,636,976.90 (12.2%); £3,002,120.20 -> £2,636,976.92 (12.2%); £3,002,120.29 -> £2,636,976.94 (12.2%); £3,002,120.31 -> £2,636,977.38 (12.2%); £3,002,120.41 -> £2,636,977.39 (12.2%); £3,002,120.51 -> £2,636,977.40 (12.2%); £3,002,120.63 -> £2,636,977.41 (12.2%); £3,002,120.74 -> £2,636,977.42 (12.2%); £3,002,120.79 -> £2,636,977.42 (12.2%); £3,002,120.83 -> £2,636,977.43 (12.2%); £3,002,120.88 -> £2,636,977.49 (12.2%); £3,002,120.98 -> £2,636,977.50 (12.2%); £3,002,121.08 -> £2,636,977.52 (12.2%); £3,002,121.19 -> £2,636,977.53 (12.2%); £3,002,121.29 -> £2,636,977.54 (12.2%); £3,002,121.39 -> £2,636,977.56 (12.2%); £3,002,121.49 -> £2,636,977.57 (12.2%); £3,002,121.52 -> £2,636,980.39 (12.2%); £3,002,121.62 -> £2,636,980.40 (12.2%); £3,002,121.73 -> £2,636,980.41 (12.2%); £3,002,121.77 -> £2,636,980.42 (12.2%); £3,002,121.82 -> £2,636,980.43 (12.2%); £3,002,121.91 -> £2,636,980.53 (12.2%); £3,002,122.01 -> £2,636,980.55 (12.2%); £3,002,122.11 -> £2,636,980.56 (12.2%); £3,002,122.20 -> £2,636,980.58 (12.2%); £3,002,122.30 -> £2,636,980.59 (12.2%); £3,002,122.39 -> £2,636,980.61 (12.2%); £3,002,122.48 -> £2,636,980.62 (12.2%); £3,002,122.51 -> £2,636,981.24 (12.2%); £3,002,122.67 -> £2,636,981.24 (12.2%); £3,002,122.83 -> £2,636,981.25 (12.2%); £3,002,122.99 -> £2,636,981.26 (12.2%); £3,002,123.16 -> £2,636,981.28 (12.2%); £3,002,123.34 -> £2,636,981.29 (12.2%); £3,002,123.39 -> £2,636,981.29 (12.2%); £3,002,123.44 -> £2,636,981.30 (12.2%); £3,002,123.44 -> £2,636,981.39 (12.2%); £3,002,123.58 -> £2,636,981.41 (12.2%); £3,002,123.72 -> £2,636,981.42 (12.2%); £3,002,123.86 -> £2,636,981.44 (12.2%); £3,002,124.01 -> £2,636,981.46 (12.2%); £3,002,124.16 -> £2,636,981.47 (12.2%); £3,002,124.30 -> £2,636,981.49 (12.2%); £3,002,124.44 -> £2,636,981.51 (12.2%); £3,002,124.47 -> £2,636,982.18 (12.2%); £3,002,124.60 -> £2,636,982.19 (12.2%); £3,002,124.74 -> £2,636,982.20 (12.2%); £3,002,124.87 -> £2,636,982.20 (12.2%); £3,002,125.00 -> £2,636,982.21 (12.2%); £3,002,125.13 -> £2,636,982.22 (12.2%); £3,002,125.17 -> £2,636,982.22 (12.2%); £3,002,125.22 -> £2,636,982.23 (12.2%); £3,002,125.31 -> £2,636,982.32 (12.2%); £3,002,125.43 -> £2,636,982.33 (12.2%); £3,002,125.54 -> £2,636,982.34 (12.2%); £3,002,125.65 -> £2,636,982.35 (12.2%); £3,002,125.76 -> £2,636,982.36 (12.2%); £3,002,125.87 -> £2,636,982.37 (12.2%); £3,002,125.99 -> £2,636,982.38 (12.2%); £3,002,126.01 -> £2,636,982.91 (12.2%); £3,002,126.08 -> £2,636,982.91 (12.2%); £3,002,126.15 -> £2,636,982.92 (12.2%); £3,002,126.22 -> £2,636,982.93 (12.2%); £3,002,126.26 -> £2,636,982.93 (12.2%); £3,002,126.31 -> £2,636,982.94 (12.2%); £3,002,126.36 -> £2,636,983.03 (12.2%); £3,002,126.44 -> £2,636,983.05 (12.2%); £3,002,126.52 -> £2,636,983.06 (12.2%); £3,002,126.59 -> £2,636,983.08 (12.2%); £3,002,126.67 -> £2,636,983.10 (12.2%); £3,002,126.75 -> £2,636,983.12 (12.2%); £3,002,126.82 -> £2,636,983.14 (12.2%); £3,002,126.89 -> £2,636,985.83 (12.2%); £3,002,126.97 -> £2,636,985.85 (12.2%); £3,002,127.04 -> £2,636,985.87 (12.2%); £3,002,127.11 -> £2,636,985.88 (12.2%); £3,002,127.16 -> £2,636,986.55 (12.2%); £3,002,127.21 -> £2,636,986.56 (12.2%); £3,002,127.26 -> £2,636,986.57 (12.2%); £3,002,127.31 -> £2,636,986.58 (12.2%); £3,002,127.36 -> £2,636,986.59 (12.2%); £3,002,127.41 -> £2,636,986.60 (12.2%); £3,002,127.42 -> £2,636,986.70 (12.2%); £3,002,127.48 -> £2,636,986.72 (12.2%); £3,002,127.55 -> £2,636,986.74 (12.2%); £3,002,127.61 -> £2,636,986.76 (12.2%); £3,002,127.68 -> £2,636,986.79 (12.2%); £3,002,127.76 -> £2,636,986.81 (12.2%); £3,002,127.83 -> £2,636,986.83 (12.2%); £3,002,127.90 -> £2,636,986.84 (12.2%); £3,002,127.93 -> £2,636,987.53 (12.2%); £3,002,127.98 -> £2,636,987.55 (12.2%); £3,002,128.04 -> £2,636,987.56 (12.2%); £3,002,128.08 -> £2,636,987.57 (12.2%); £3,002,128.13 -> £2,636,987.58 (12.2%); £3,002,128.18 -> £2,636,987.59 (12.2%); £3,002,128.23 -> £2,636,987.60 (12.2%); £3,002,128.26 -> £2,636,987.72 (12.2%); £3,002,128.32 -> £2,636,987.74 (12.2%); £3,002,128.39 -> £2,636,987.77 (12.2%); £3,002,128.46 -> £2,636,987.79 (12.2%); £3,002,128.53 -> £2,636,987.81 (12.2%); £3,002,128.60 -> £2,636,987.82 (12.2%); £3,002,128.67 -> £2,636,987.84 (12.2%); £3,002,128.74 -> £2,636,987.86 (12.2%); £3,002,128.75 -> £2,636,988.49 (12.2%); £3,002,128.81 -> £2,636,988.50 (12.2%); £3,002,128.86 -> £2,636,988.51 (12.2%); £3,002,128.92 -> £2,636,988.52 (12.2%); £3,002,128.97 -> £2,636,988.53 (12.2%); £3,002,129.02 -> £2,636,988.54 (12.2%); £3,002,129.06 -> £2,636,988.55 (12.2%); £3,002,129.07 -> £2,636,988.64 (12.2%); £3,002,129.13 -> £2,636,988.67 (12.2%); £3,002,129.21 -> £2,636,988.69 (12.2%); £3,002,129.28 -> £2,636,988.72 (12.2%); £3,002,129.37 -> £2,636,988.74 (12.2%); £3,002,129.45 -> £2,636,988.77 (12.2%); £3,002,129.53 -> £2,636,988.79 (12.2%); £3,002,129.61 -> £2,636,988.82 (12.2%); £3,002,129.66 -> £2,636,989.47 (12.2%); £3,002,129.74 -> £2,636,989.48 (12.2%); £3,002,129.81 -> £2,636,989.49 (12.2%); £3,002,129.88 -> £2,636,989.50 (12.2%); £3,002,129.95 -> £2,636,989.51 (12.2%); £3,002,130.00 -> £2,636,989.52 (12.2%); £3,002,130.05 -> £2,636,989.53 (12.2%); £3,002,130.06 -> £2,636,989.63 (12.2%); £3,002,130.14 -> £2,636,989.66 (12.2%); £3,002,130.23 -> £2,636,989.68 (12.2%); £3,002,130.32 -> £2,636,989.71 (12.2%); £3,002,130.41 -> £2,636,989.73 (12.2%); £3,002,130.50 -> £2,636,989.75 (12.2%); £3,002,130.60 -> £2,636,989.77 (12.2%); £3,002,130.69 -> £2,636,989.79 (12.2%); £3,002,130.71 -> £2,636,992.60 (12.2%); £3,002,130.81 -> £2,636,992.62 (12.2%); £3,002,130.91 -> £2,636,992.65 (12.2%); £3,002,131.02 -> £2,636,992.67 (12.2%); £3,002,131.14 -> £2,636,992.69 (12.2%); £3,002,131.15 -> £2,636,993.33 (12.2%); £3,002,131.31 -> £2,636,993.35 (12.2%); £3,002,131.47 -> £2,636,993.36 (12.2%); £3,002,131.63 -> £2,636,993.37 (12.2%); £3,002,131.78 -> £2,636,993.38 (12.2%); £3,002,131.93 -> £2,636,993.39 (12.2%); £3,002,131.98 -> £2,636,993.40 (12.2%); £3,002,132.03 -> £2,636,993.41 (12.2%); £3,002,132.03 -> £2,636,993.51 (12.2%); £3,002,132.17 -> £2,636,993.53 (12.2%); £3,002,132.32 -> £2,636,993.55 (12.2%); £3,002,132.45 -> £2,636,993.56 (12.2%); £3,002,132.60 -> £2,636,993.58 (12.2%); £3,002,132.74 -> £2,636,993.61 (12.2%); £3,002,132.89 -> £2,636,993.63 (12.2%); £3,002,133.05 -> £2,636,993.66 (12.2%); £3,002,133.06 -> £2,636,994.29 (12.2%); £3,002,133.24 -> £2,636,994.30 (12.2%); £3,002,133.42 -> £2,636,994.31 (12.2%); £3,002,133.59 -> £2,636,994.31 (12.2%); £3,002,133.76 -> £2,636,994.32 (12.2%); £3,002,133.94 -> £2,636,994.33 (12.2%); £3,002,133.98 -> £2,636,994.33 (12.2%); £3,002,134.03 -> £2,636,994.34 (12.2%); £3,002,134.17 -> £2,636,994.44 (12.2%); £3,002,134.33 -> £2,636,994.46 (12.2%); £3,002,134.49 -> £2,636,994.47 (12.2%); £3,002,134.65 -> £2,636,994.49 (12.2%); £3,002,134.82 -> £2,636,994.52 (12.2%); £3,002,135.00 -> £2,636,994.54 (12.2%); £3,002,135.16 -> £2,636,994.56 (12.2%); £3,002,135.24 -> £2,636,995.17 (12.2%); £3,002,135.48 -> £2,636,995.18 (12.2%); £3,002,135.73 -> £2,636,995.19 (12.2%); £3,002,135.97 -> £2,636,995.20 (12.2%); £3,002,136.20 -> £2,636,995.21 (12.2%); £3,002,136.45 -> £2,636,995.22 (12.2%); £3,002,136.50 -> £2,636,995.23 (12.2%); £3,002,136.55 -> £2,636,995.24 (12.2%); £3,002,136.56 -> £2,636,995.34 (12.2%); £3,002,136.77 -> £2,636,995.36 (12.2%); £3,002,136.98 -> £2,636,995.37 (12.2%); £3,002,137.18 -> £2,636,995.40 (12.2%); £3,002,137.40 -> £2,636,995.42 (12.2%); £3,002,137.62 -> £2,636,995.45 (12.2%); £3,002,137.85 -> £2,636,995.47 (12.2%); £3,002,138.07 -> £2,636,995.49 (12.2%); £3,002,138.17 -> £2,636,996.17 (12.2%); £3,002,138.47 -> £2,636,996.18 (12.2%); £3,002,138.78 -> £2,636,996.20 (12.2%); £3,002,139.09 -> £2,636,996.21 (12.2%); £3,002,139.41 -> £2,636,996.22 (12.2%); £3,002,139.73 -> £2,636,996.23 (12.2%); £3,002,139.78 -> £2,636,996.24 (12.2%); £3,002,139.82 -> £2,636,996.25 (12.2%); £3,002,139.84 -> £2,636,996.36 (12.2%); £3,002,140.10 -> £2,636,996.38 (12.2%); £3,002,140.37 -> £2,636,996.41 (12.2%); £3,002,140.63 -> £2,636,996.43 (12.2%); £3,002,140.90 -> £2,636,996.45 (12.2%); £3,002,141.16 -> £2,636,996.48 (12.2%); £3,002,141.43 -> £2,636,996.50 (12.2%); £3,002,141.69 -> £2,636,996.52 (12.2%); £3,002,141.73 -> £2,636,999.49 (12.2%); £3,002,141.95 -> £2,636,999.50 (12.2%); £3,002,142.16 -> £2,636,999.50 (12.2%); £3,002,142.21 -> £2,636,999.51 (12.2%); £3,002,142.25 -> £2,636,999.52 (12.2%); £3,002,142.25 -> £2,636,999.61 (12.2%); £3,002,142.43 -> £2,636,999.63 (12.2%); £3,002,142.62 -> £2,636,999.65 (12.2%); £3,002,142.80 -> £2,636,999.67 (12.2%); £3,002,142.99 -> £2,636,999.69 (12.2%); £3,002,143.18 -> £2,636,999.72 (12.2%); £3,002,143.39 -> £2,636,999.75 (12.2%); £3,002,143.59 -> £2,636,999.78 (12.2%); £3,002,143.60 -> £2,637,000.49 (12.2%); £3,002,143.76 -> £2,637,000.50 (12.2%); £3,002,143.90 -> £2,637,000.51 (12.2%); £3,002,144.04 -> £2,637,000.52 (12.2%); £3,002,144.17 -> £2,637,000.53 (12.2%); £3,002,144.31 -> £2,637,000.54 (12.2%); £3,002,144.36 -> £2,637,000.54 (12.2%); £3,002,144.40 -> £2,637,000.55 (12.2%); £3,002,144.41 -> £2,637,000.66 (12.2%); £3,002,144.54 -> £2,637,000.68 (12.2%); £3,002,144.68 -> £2,637,000.70 (12.2%); £3,002,144.81 -> £2,637,000.73 (12.2%); £3,002,144.96 -> £2,637,000.74 (12.2%); £3,002,145.09 -> £2,637,000.77 (12.2%); £3,002,145.24 -> £2,637,000.80 (12.2%); £3,002,145.39 -> £2,637,000.83 (12.2%); £3,002,145.39 -> £2,637,001.51 (12.2%); £3,002,145.50 -> £2,637,001.52 (12.2%); £3,002,145.60 -> £2,637,001.53 (12.2%); £3,002,145.70 -> £2,637,001.54 (12.2%); £3,002,145.79 -> £2,637,001.55 (12.2%); £3,002,145.89 -> £2,637,001.56 (12.2%); £3,002,145.94 -> £2,637,001.56 (12.2%); £3,002,145.98 -> £2,637,001.57 (12.2%); £3,002,146.00 -> £2,637,001.68 (12.2%); £3,002,146.10 -> £2,637,001.70 (12.2%); £3,002,146.21 -> £2,637,001.72 (12.2%); £3,002,146.32 -> £2,637,001.74 (12.2%); £3,002,146.42 -> £2,637,001.76 (12.2%); £3,002,146.54 -> £2,637,001.78 (12.2%); £3,002,146.65 -> £2,637,001.80 (12.2%); £3,002,146.76 -> £2,637,001.82 (12.2%); £3,002,146.87 -> £2,637,002.49 (12.2%); £3,002,146.99 -> £2,637,002.51 (12.2%); £3,002,147.11 -> £2,637,002.52 (12.2%); £3,002,147.22 -> £2,637,002.53 (12.2%); £3,002,147.33 -> £2,637,002.54 (12.2%); £3,002,147.38 -> £2,637,002.54 (12.2%); £3,002,147.42 -> £2,637,002.55 (12.2%); £3,002,147.52 -> £2,637,002.65 (12.2%); £3,002,147.63 -> £2,637,002.66 (12.2%); £3,002,147.73 -> £2,637,002.68 (12.2%); £3,002,147.84 -> £2,637,002.69 (12.2%); £3,002,147.95 -> £2,637,002.71 (12.2%); £3,002,148.07 -> £2,637,002.72 (12.2%); £3,002,148.19 -> £2,637,002.74 (12.2%); £3,002,148.24 -> £2,637,003.31 (12.2%); £3,002,148.48 -> £2,637,003.32 (12.2%); £3,002,148.71 -> £2,637,003.33 (12.2%); £3,002,148.94 -> £2,637,003.34 (12.2%); £3,002,149.17 -> £2,637,003.34 (12.2%); £3,002,149.40 -> £2,637,003.35 (12.2%); £3,002,149.45 -> £2,637,003.36 (12.2%); £3,002,149.50 -> £2,637,003.36 (12.2%); £3,002,149.51 -> £2,637,003.47 (12.2%); £3,002,149.72 -> £2,637,003.49 (12.2%); £3,002,149.93 -> £2,637,003.52 (12.2%); £3,002,150.15 -> £2,637,003.54 (12.2%); £3,002,150.37 -> £2,637,003.57 (12.2%); £3,002,150.60 -> £2,637,003.60 (12.2%); £3,002,150.82 -> £2,637,003.62 (12.2%); £3,002,151.05 -> £2,637,003.65 (12.2%); £3,002,151.09 -> £2,637,006.59 (12.2%); £3,002,151.37 -> £2,637,006.60 (12.2%); £3,002,151.65 -> £2,637,006.61 (12.2%); £3,002,151.70 -> £2,637,006.62 (12.2%); £3,002,151.75 -> £2,637,006.63 (12.2%); £3,002,151.76 -> £2,637,006.74 (12.2%); £3,002,152.00 -> £2,637,006.76 (12.2%); £3,002,152.24 -> £2,637,006.78 (12.2%); £3,002,152.47 -> £2,637,006.81 (12.2%); £3,002,152.72 -> £2,637,006.83 (12.2%); £3,002,152.96 -> £2,637,006.85 (12.2%); £3,002,153.20 -> £2,637,006.88 (12.2%); £3,002,153.44 -> £2,637,006.90 (12.2%); £3,002,153.62 -> £2,637,007.59 (12.2%); £3,002,153.97 -> £2,637,007.60 (12.2%); £3,002,154.31 -> £2,637,007.61 (12.2%); £3,002,154.65 -> £2,637,007.62 (12.2%); £3,002,154.97 -> £2,637,007.63 (12.2%); £3,002,155.30 -> £2,637,007.64 (12.2%); £3,002,155.35 -> £2,637,007.65 (12.2%); £3,002,155.39 -> £2,637,007.66 (12.2%); £3,002,155.39 -> £2,637,007.75 (12.2%); £3,002,155.65 -> £2,637,007.77 (12.2%); £3,002,155.92 -> £2,637,007.79 (12.2%); £3,002,156.18 -> £2,637,007.80 (12.2%); £3,002,156.44 -> £2,637,007.82 (12.2%); £3,002,156.71 -> £2,637,007.85 (12.2%); £3,002,156.98 -> £2,637,007.87 (12.2%); £3,002,157.25 -> £2,637,007.89 (12.2%); £3,002,157.28 -> £2,637,008.53 (12.2%); £3,002,157.54 -> £2,637,008.55 (12.2%); £3,002,157.83 -> £2,637,008.56 (12.2%); £3,002,158.14 -> £2,637,008.57 (12.2%); £3,002,158.42 -> £2,637,008.58 (12.2%); £3,002,158.72 -> £2,637,008.59 (12.2%); £3,002,158.76 -> £2,637,008.60 (12.2%); £3,002,158.81 -> £2,637,008.60 (12.2%); £3,002,158.82 -> £2,637,008.71 (12.2%); £3,002,159.06 -> £2,637,008.73 (12.2%); £3,002,159.31 -> £2,637,008.75 (12.2%); £3,002,159.54 -> £2,637,008.76 (12.2%); £3,002,159.77 -> £2,637,008.77 (12.2%); £3,002,160.00 -> £2,637,008.79 (12.2%); £3,002,160.23 -> £2,637,008.81 (12.2%); £3,002,160.47 -> £2,637,008.83 (12.2%); £3,002,160.48 -> £2,637,009.52 (12.2%); £3,002,160.67 -> £2,637,009.53 (12.2%); £3,002,160.87 -> £2,637,009.54 (12.2%); £3,002,161.07 -> £2,637,009.55 (12.2%); £3,002,161.26 -> £2,637,009.56 (12.2%); £3,002,161.45 -> £2,637,009.57 (12.2%); £3,002,161.50 -> £2,637,009.57 (12.2%); £3,002,161.55 -> £2,637,009.58 (12.2%); £3,002,161.55 -> £2,637,009.68 (12.2%); £3,002,161.73 -> £2,637,009.71 (12.2%); £3,002,161.91 -> £2,637,009.73 (12.2%); £3,002,162.09 -> £2,637,009.75 (12.2%); £3,002,162.28 -> £2,637,009.78 (12.2%); £3,002,162.47 -> £2,637,009.80 (12.2%); £3,002,162.65 -> £2,637,009.83 (12.2%); £3,002,162.84 -> £2,637,009.86 (12.2%); £3,002,860.78 -> £2,637,010.10 (12.2%); £3,003,008.90 -> £2,637,117.37 (12.2%); £3,003,009.09 -> £2,637,117.88 (12.2%); £3,003,009.48 -> £2,637,117.90 (12.2%); £3,003,009.87 -> £2,637,117.92 (12.2%); £3,003,010.25 -> £2,637,117.94 (12.2%); £3,003,010.63 -> £2,637,112.71 (12.2%); £3,003,011.02 -> £2,637,102.84 (12.2%); £3,003,011.05 -> £2,637,092.81 (12.2%); £3,003,011.09 -> £2,636,971.04 (12.2%); £3,003,011.39 -> £2,636,960.84 (12.2%); £3,003,011.83 -> £2,636,950.60 (12.2%); £3,003,012.26 -> £2,636,940.61 (12.2%); £3,003,012.68 -> £2,636,930.03 (12.2%); £3,003,013.12 -> £2,636,919.29 (12.2%); £3,003,013.54 -> £2,636,909.05 (12.2%); £3,003,013.97 -> £2,636,832.57 (12.2%); £3,237,386.38 -> £2,637,118.75 (18.5%)
- Bills issued: 156, average clarity 0.833, average bill shock 19.7%, bad debt provision £75,512.89, avg complaint probability 4.9%
- Solvency signal: £263,712/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £152,354.33 vs. naked (unhedged) net margin: £1,300,511.16
- hedging cost £1,148,156.83 vs. a fully unhedged book (commodity-only: actual net £152,354.33 vs. naked net £1,300,511.16)
  - C2: actual £361.03 vs. naked £1,189.53 -- hedging cost £828.50
  - C2g: actual £120.43 vs. naked £282.00 -- hedging cost £161.57
  - C4: actual £-303.08 vs. naked £1,051.40 -- hedging cost £1,354.47
  - C4g: actual £451.13 vs. naked £2,711.00 -- hedging cost £2,259.86
  - C6: actual £608.99 vs. naked £2,573.34 -- hedging cost £1,964.35
  - C7: actual £861.46 vs. naked £3,255.01 -- hedging cost £2,393.55
  - C8: actual £660.46 vs. naked £1,746.10 -- hedging cost £1,085.64
  - C9: actual £776.75 vs. naked £1,535.11 -- hedging cost £758.36
  - C_IC1: actual £262,740.77 vs. naked £276,333.91 -- hedging cost £13,593.14
  - C_IC2: actual £100,759.85 vs. naked £127,088.35 -- hedging cost £26,328.50
  - C_IC3: actual £233,389.33 vs. naked £837,933.95 -- hedging cost £604,544.62
  - C_IC3g: actual £-252,917.30 vs. naked £83,300.79 -- hedging cost £336,218.09
  - C_IC4: actual £-195,155.50 vs. naked £-38,489.32 -- hedging cost £156,666.18

**Year narrative:** 2022 (flagged crisis year) produced a net loss of £-9,239.70 across 13 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 51 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £168,528.16 (gross £970,494.14, capital £9,780.11)
  - Electricity: gross £1,109,293.13, capital £9,363.93, net £420,517.71
  - Gas: gross £-138,798.99, capital £416.18, net £-251,989.54
- Treasury at year end: £2,789,811.35
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.94 (avg 0.94), C2g 0.85 (avg 0.85), C4 0.91 (avg 0.91), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.94 (avg 0.94), C9 0.93 (avg 0.93), C_IC1 0.85 (avg 0.89), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.90 (avg 0.90), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £2,637,139.28, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £116,136.29 / stressed £41,976.49) ratio 2.77
  - 2023-02-23: treasury £2,637,164.02, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £116,136.29 / stressed £41,976.49) ratio 2.77
  - 2023-03-25: treasury £2,637,189.07, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £116,136.29 / stressed £41,976.49) ratio 2.77
  - 2023-04-24: treasury £2,733,159.33, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £120,774.25 / stressed £45,931.05) ratio 2.63
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-07-01 period 1, net margin £-813.88

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £218,787.57
  - By billing account: C1 £1,745.06, C2 £5,526.98, C3 £2,230.25, C4 £2,636.95, C5 £5,852.04, C6 £9,873.78, C7 £5,080.68, C8 £6,554.63, C9 £6,362.09, C_IC1 £984,609.19, C_IC2 £492,401.50, C_IC3 £1,303,755.85, C_IC4 £17,609.37
- Bill shock events (>=20%): 31 -- C7 2023-01-31 (34%); C7 2023-05-31 (33%); C7 2023-06-30 (38%); C7 2023-10-31 (58%); C7 2023-11-30 (74%); C6 2023-04-30 (22%); C6 2023-05-31 (24%); C6 2023-06-30 (23%); C6 2023-10-31 (39%); C6 2023-11-30 (44%); C8 2023-04-30 (23%); C8 2023-05-31 (41%); C8 2023-06-30 (45%); C8 2023-10-31 (103%); C8 2023-11-30 (71%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (23%); C9 2023-10-31 (77%); C9 2023-11-30 (55%); C4g 2023-10-31 (62%); C_IC1 2023-06-30 (56%); C_IC1 2023-07-31 (107%); C_IC2 2023-05-31 (56%); C_IC2 2023-06-30 (137%); C_IC3 2023-01-31 (35%); C_IC3g 2023-01-31 (34%); C_IC4 2023-01-31 (46%)
- Churn risk (accounts renewing in 2023): 6 at risk (≥20% churn prob): C2 20%, C6 29%, C7 38%, C8 38%, C9 41%, C_IC4 32%

**Pricing & Margin**

- C2 (electricity): tariff £390.68-£392.42/MWh, net margin £698.19
- C2g (gas): tariff £117.83-£147.52/MWh, net margin £1,037.58
- C4 (electricity): tariff £237.17-£348.03/MWh, net margin £-184.42 -- **net-negative**
- C4g (gas): tariff £57.36-£182.83/MWh, net margin £387.98
- C6 (electricity): tariff £370.09-£384.50/MWh, net margin £1,248.25
- C7 (electricity): tariff £171.90-£586.67/MWh, net margin £853.06
- C8 (electricity): tariff £288.14-£552.10/MWh, net margin £1,108.36
- C9 (electricity): tariff £235.93-£469.79/MWh, net margin £965.66
- C_IC1 (electricity): tariff £-60.00-£470.63/MWh, net margin £264,783.06
- C_IC2 (electricity): tariff £-186.24-£467.36/MWh, net margin £112,914.96
- C_IC3 (electricity): tariff £80.85-£416.08/MWh, net margin £233,406.57
- C_IC3g (gas): tariff £57.82-£160.16/MWh, net margin £-253,415.10 -- **net-negative**
- C_IC4 (electricity): tariff £36.40-£169.32/MWh, net margin £-195,275.98 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): 4442 -- £3,236,947.69 -> £2,637,119.96 (18.5%); £3,248,983.42 -> £2,789,382.05 (14.1%); £3,248,983.42 -> £2,789,383.05 (14.1%); £3,248,983.52 -> £2,789,383.07 (14.1%); £3,248,983.61 -> £2,789,383.09 (14.1%); £3,248,983.63 -> £2,789,383.11 (14.1%); £3,248,983.65 -> £2,789,383.13 (14.1%); £3,248,983.67 -> £2,789,383.50 (14.1%); £3,248,983.76 -> £2,789,383.54 (14.1%); £3,248,983.85 -> £2,789,383.58 (14.1%); £3,248,983.94 -> £2,789,383.62 (14.1%); £3,248,984.02 -> £2,789,383.66 (14.1%); £3,248,984.03 -> £2,789,385.51 (14.1%); £3,248,984.03 -> £2,789,385.56 (14.1%); £3,248,984.05 -> £2,789,385.60 (14.1%); £3,248,984.06 -> £2,789,385.65 (14.1%); £3,248,984.07 -> £2,789,385.69 (14.1%); £3,248,984.08 -> £2,789,385.74 (14.1%); £3,248,984.10 -> £2,789,385.78 (14.1%); £3,248,984.11 -> £2,789,385.82 (14.1%); £3,248,984.12 -> £2,789,385.86 (14.1%); £3,248,984.13 -> £2,789,385.90 (14.1%); £3,248,984.14 -> £2,789,385.94 (14.1%); £3,248,984.15 -> £2,789,385.98 (14.1%); £3,248,984.16 -> £2,789,386.01 (14.1%); £3,248,984.17 -> £2,789,386.03 (14.1%); £3,248,984.18 -> £2,789,386.05 (14.1%); £3,248,984.18 -> £2,789,386.07 (14.1%); £3,248,984.19 -> £2,789,386.22 (14.1%); £3,248,984.19 -> £2,789,386.36 (14.1%); £3,248,984.19 -> £2,789,386.50 (14.1%); £3,248,984.20 -> £2,789,386.63 (14.1%); £3,248,984.20 -> £2,789,386.76 (14.1%); £3,248,984.20 -> £2,789,386.90 (14.1%); £3,248,984.20 -> £2,789,387.04 (14.1%); £3,248,984.20 -> £2,789,387.17 (14.1%); £3,248,984.21 -> £2,789,387.18 (14.1%); £3,248,984.21 -> £2,789,387.19 (14.1%); £3,248,984.21 -> £2,789,387.20 (14.1%); £3,248,984.21 -> £2,789,387.21 (14.1%); £3,248,984.22 -> £2,789,387.22 (14.1%); £3,248,984.24 -> £2,789,387.24 (14.1%); £3,248,984.25 -> £2,789,387.26 (14.1%); £3,248,984.26 -> £2,789,387.28 (14.1%); £3,248,984.28 -> £2,789,387.30 (14.1%); £3,248,984.30 -> £2,789,387.33 (14.1%); £3,248,984.33 -> £2,789,387.36 (14.1%); £3,248,984.35 -> £2,789,387.40 (14.1%); £3,248,984.38 -> £2,789,387.42 (14.1%); £3,248,984.39 -> £2,789,387.45 (14.1%); £3,248,984.40 -> £2,789,387.48 (14.1%); £3,248,984.41 -> £2,789,387.52 (14.1%); £3,248,984.42 -> £2,789,387.55 (14.1%); £3,248,984.43 -> £2,789,387.58 (14.1%); £3,248,984.44 -> £2,789,387.61 (14.1%); £3,248,984.45 -> £2,789,387.64 (14.1%); £3,248,984.46 -> £2,789,387.66 (14.1%); £3,248,984.46 -> £2,789,387.69 (14.1%); £3,248,984.47 -> £2,789,387.71 (14.1%); £3,248,984.48 -> £2,789,387.74 (14.1%); £3,248,984.49 -> £2,789,387.76 (14.1%); £3,248,984.49 -> £2,789,387.80 (14.1%); £3,248,984.51 -> £2,789,387.84 (14.1%); £3,248,984.53 -> £2,789,387.89 (14.1%); £3,248,984.55 -> £2,789,387.93 (14.1%); £3,248,984.56 -> £2,789,387.98 (14.1%); £3,248,984.58 -> £2,789,388.02 (14.1%); £3,248,984.59 -> £2,789,388.06 (14.1%); £3,248,984.61 -> £2,789,388.10 (14.1%); £3,248,984.62 -> £2,789,388.14 (14.1%); £3,248,984.63 -> £2,789,388.18 (14.1%); £3,248,984.65 -> £2,789,388.22 (14.1%); £3,248,984.66 -> £2,789,388.25 (14.1%); £3,248,984.67 -> £2,789,388.27 (14.1%); £3,248,984.67 -> £2,789,388.29 (14.1%); £3,248,984.68 -> £2,789,388.31 (14.1%); £3,248,984.68 -> £2,789,388.45 (14.1%); £3,248,984.68 -> £2,789,388.59 (14.1%); £3,248,984.69 -> £2,789,388.73 (14.1%); £3,248,984.69 -> £2,789,388.87 (14.1%); £3,248,984.69 -> £2,789,389.01 (14.1%); £3,248,984.69 -> £2,789,389.15 (14.1%); £3,248,984.70 -> £2,789,389.28 (14.1%); £3,248,984.70 -> £2,789,389.42 (14.1%); £3,248,984.70 -> £2,789,389.43 (14.1%); £3,248,984.70 -> £2,789,389.44 (14.1%); £3,248,984.70 -> £2,789,389.45 (14.1%); £3,248,984.71 -> £2,789,389.46 (14.1%); £3,248,984.71 -> £2,789,389.47 (14.1%); £3,248,984.73 -> £2,789,389.49 (14.1%); £3,248,984.75 -> £2,789,389.52 (14.1%); £3,248,984.95 -> £2,789,389.55 (14.1%); £3,248,985.16 -> £2,789,389.58 (14.1%); £3,248,985.36 -> £2,789,389.61 (14.1%); £3,248,985.57 -> £2,789,389.63 (14.1%); £3,248,985.78 -> £2,789,389.66 (14.1%); £3,248,985.99 -> £2,789,389.68 (14.1%); £3,248,986.05 -> £2,789,389.70 (14.1%); £3,248,986.10 -> £2,789,389.72 (14.1%); £3,248,986.10 -> £2,789,389.74 (14.1%); £3,248,986.11 -> £2,789,389.76 (14.1%); £3,248,986.11 -> £2,789,389.78 (14.1%); £3,248,986.12 -> £2,789,389.80 (14.1%); £3,248,986.12 -> £2,789,389.81 (14.1%); £3,248,986.13 -> £2,789,389.83 (14.1%); £3,248,986.13 -> £2,789,389.85 (14.1%); £3,248,986.14 -> £2,789,389.87 (14.1%); £3,248,986.14 -> £2,789,389.89 (14.1%); £3,248,986.15 -> £2,789,389.91 (14.1%); £3,248,986.21 -> £2,789,389.95 (14.1%); £3,248,986.39 -> £2,789,390.00 (14.1%); £3,248,986.57 -> £2,789,390.05 (14.1%); £3,248,986.75 -> £2,789,390.10 (14.1%); £3,248,986.94 -> £2,789,390.14 (14.1%); £3,248,987.12 -> £2,789,390.18 (14.1%); £3,248,987.29 -> £2,789,390.22 (14.1%); £3,248,987.46 -> £2,789,390.26 (14.1%); £3,248,987.47 -> £2,789,390.30 (14.1%); £3,248,987.49 -> £2,789,390.34 (14.1%); £3,248,987.50 -> £2,789,390.39 (14.1%); £3,248,987.51 -> £2,789,390.41 (14.1%); £3,248,987.52 -> £2,789,390.44 (14.1%); £3,248,987.53 -> £2,789,390.46 (14.1%); £3,248,987.53 -> £2,789,390.48 (14.1%); £3,248,987.54 -> £2,789,390.62 (14.1%); £3,248,987.54 -> £2,789,390.75 (14.1%); £3,248,987.54 -> £2,789,390.89 (14.1%); £3,248,987.54 -> £2,789,391.03 (14.1%); £3,248,987.55 -> £2,789,391.16 (14.1%); £3,248,987.55 -> £2,789,391.30 (14.1%); £3,248,987.55 -> £2,789,391.43 (14.1%); £3,248,987.55 -> £2,789,391.57 (14.1%); £3,248,987.55 -> £2,789,391.58 (14.1%); £3,248,987.55 -> £2,789,391.59 (14.1%); £3,248,987.56 -> £2,789,391.59 (14.1%); £3,248,987.56 -> £2,789,391.60 (14.1%); £3,248,987.56 -> £2,789,391.62 (14.1%); £3,248,987.57 -> £2,789,391.64 (14.1%); £3,248,987.58 -> £2,789,391.66 (14.1%); £3,248,987.74 -> £2,789,391.69 (14.1%); £3,248,987.90 -> £2,789,391.72 (14.1%); £3,248,988.06 -> £2,789,391.75 (14.1%); £3,248,988.22 -> £2,789,391.77 (14.1%); £3,248,988.38 -> £2,789,391.80 (14.1%); £3,248,988.54 -> £2,789,391.82 (14.1%); £3,248,988.59 -> £2,789,391.84 (14.1%); £3,248,988.64 -> £2,789,391.85 (14.1%); £3,248,988.64 -> £2,789,391.87 (14.1%); £3,248,988.65 -> £2,789,391.89 (14.1%); £3,248,988.65 -> £2,789,391.91 (14.1%); £3,248,988.65 -> £2,789,391.93 (14.1%); £3,248,988.65 -> £2,789,391.94 (14.1%); £3,248,988.66 -> £2,789,391.96 (14.1%); £3,248,988.66 -> £2,789,391.98 (14.1%); £3,248,988.67 -> £2,789,391.99 (14.1%); £3,248,988.67 -> £2,789,392.01 (14.1%); £3,248,988.67 -> £2,789,392.04 (14.1%); £3,248,988.74 -> £2,789,392.08 (14.1%); £3,248,988.88 -> £2,789,392.13 (14.1%); £3,248,989.03 -> £2,789,392.17 (14.1%); £3,248,989.18 -> £2,789,392.21 (14.1%); £3,248,989.32 -> £2,789,392.25 (14.1%); £3,248,989.46 -> £2,789,392.29 (14.1%); £3,248,989.59 -> £2,789,392.33 (14.1%); £3,248,989.73 -> £2,789,392.37 (14.1%); £3,248,989.74 -> £2,789,392.41 (14.1%); £3,248,989.75 -> £2,789,392.45 (14.1%); £3,248,989.76 -> £2,789,392.50 (14.1%); £3,248,989.77 -> £2,789,392.53 (14.1%); £3,248,989.78 -> £2,789,392.55 (14.1%); £3,248,989.79 -> £2,789,392.57 (14.1%); £3,248,989.79 -> £2,789,392.59 (14.1%); £3,248,989.79 -> £2,789,392.72 (14.1%); £3,248,989.80 -> £2,789,392.86 (14.1%); £3,248,989.80 -> £2,789,392.99 (14.1%); £3,248,989.80 -> £2,789,393.12 (14.1%); £3,248,989.80 -> £2,789,393.25 (14.1%); £3,248,989.80 -> £2,789,393.39 (14.1%); £3,248,989.81 -> £2,789,393.52 (14.1%); £3,248,989.81 -> £2,789,393.65 (14.1%); £3,248,989.81 -> £2,789,393.66 (14.1%); £3,248,989.81 -> £2,789,393.67 (14.1%); £3,248,989.81 -> £2,789,393.68 (14.1%); £3,248,989.81 -> £2,789,393.69 (14.1%); £3,248,989.82 -> £2,789,393.71 (14.1%); £3,248,989.83 -> £2,789,393.73 (14.1%); £3,248,989.85 -> £2,789,393.75 (14.1%); £3,248,990.03 -> £2,789,393.78 (14.1%); £3,248,990.21 -> £2,789,393.81 (14.1%); £3,248,990.39 -> £2,789,393.84 (14.1%); £3,248,990.57 -> £2,789,393.86 (14.1%); £3,248,990.75 -> £2,789,393.89 (14.1%); £3,248,990.93 -> £2,789,393.91 (14.1%); £3,248,990.98 -> £2,789,393.93 (14.1%); £3,248,991.04 -> £2,789,393.95 (14.1%); £3,248,991.04 -> £2,789,393.96 (14.1%); £3,248,991.04 -> £2,789,393.98 (14.1%); £3,248,991.05 -> £2,789,394.00 (14.1%); £3,248,991.05 -> £2,789,394.02 (14.1%); £3,248,991.05 -> £2,789,394.04 (14.1%); £3,248,991.06 -> £2,789,394.05 (14.1%); £3,248,991.06 -> £2,789,394.07 (14.1%); £3,248,991.06 -> £2,789,394.09 (14.1%); £3,248,991.07 -> £2,789,394.11 (14.1%); £3,248,991.07 -> £2,789,394.13 (14.1%); £3,248,991.13 -> £2,789,394.17 (14.1%); £3,248,991.29 -> £2,789,394.22 (14.1%); £3,248,991.45 -> £2,789,394.26 (14.1%); £3,248,991.62 -> £2,789,394.31 (14.1%); £3,248,991.78 -> £2,789,394.35 (14.1%); £3,248,991.93 -> £2,789,394.39 (14.1%); £3,248,992.09 -> £2,789,394.43 (14.1%); £3,248,992.24 -> £2,789,394.47 (14.1%); £3,248,992.25 -> £2,789,394.51 (14.1%); £3,248,992.27 -> £2,789,394.56 (14.1%); £3,248,992.28 -> £2,789,394.60 (14.1%); £3,248,992.30 -> £2,789,394.63 (14.1%); £3,248,992.30 -> £2,789,394.65 (14.1%); £3,248,992.31 -> £2,789,394.67 (14.1%); £3,248,992.31 -> £2,789,394.69 (14.1%); £3,248,992.32 -> £2,789,394.82 (14.1%); £3,248,992.32 -> £2,789,394.95 (14.1%); £3,248,992.32 -> £2,789,395.08 (14.1%); £3,248,992.32 -> £2,789,395.21 (14.1%); £3,248,992.32 -> £2,789,395.34 (14.1%); £3,248,992.32 -> £2,789,395.47 (14.1%); £3,248,992.32 -> £2,789,395.60 (14.1%); £3,248,992.32 -> £2,789,395.73 (14.1%); £3,248,992.33 -> £2,789,395.74 (14.1%); £3,248,992.33 -> £2,789,395.74 (14.1%); £3,248,992.33 -> £2,789,395.75 (14.1%); £3,248,992.33 -> £2,789,395.76 (14.1%); £3,248,992.33 -> £2,789,395.78 (14.1%); £3,248,992.34 -> £2,789,395.80 (14.1%); £3,248,992.35 -> £2,789,395.82 (14.1%); £3,248,992.51 -> £2,789,395.85 (14.1%); £3,248,992.68 -> £2,789,395.88 (14.1%); £3,248,992.85 -> £2,789,395.90 (14.1%); £3,248,993.01 -> £2,789,395.93 (14.1%); £3,248,993.17 -> £2,789,395.96 (14.1%); £3,248,993.33 -> £2,789,395.97 (14.1%); £3,248,993.38 -> £2,789,395.99 (14.1%); £3,248,993.43 -> £2,789,396.01 (14.1%); £3,248,993.44 -> £2,789,396.03 (14.1%); £3,248,993.44 -> £2,789,396.05 (14.1%); £3,248,993.44 -> £2,789,396.07 (14.1%); £3,248,993.45 -> £2,789,396.08 (14.1%); £3,248,993.45 -> £2,789,396.10 (14.1%); £3,248,993.45 -> £2,789,396.12 (14.1%); £3,248,993.46 -> £2,789,396.14 (14.1%); £3,248,993.46 -> £2,789,396.15 (14.1%); £3,248,993.46 -> £2,789,396.17 (14.1%); £3,248,993.47 -> £2,789,396.19 (14.1%); £3,248,993.53 -> £2,789,396.24 (14.1%); £3,248,993.68 -> £2,789,396.29 (14.1%); £3,248,993.83 -> £2,789,396.33 (14.1%); £3,248,993.98 -> £2,789,396.37 (14.1%); £3,248,994.13 -> £2,789,396.42 (14.1%); £3,248,994.28 -> £2,789,396.46 (14.1%); £3,248,994.42 -> £2,789,396.50 (14.1%); £3,248,994.56 -> £2,789,396.54 (14.1%); £3,248,994.57 -> £2,789,396.58 (14.1%); £3,248,994.59 -> £2,789,396.62 (14.1%); £3,248,994.60 -> £2,789,396.67 (14.1%); £3,248,994.62 -> £2,789,396.70 (14.1%); £3,248,994.62 -> £2,789,396.72 (14.1%); £3,248,994.63 -> £2,789,396.74 (14.1%); £3,248,994.64 -> £2,789,396.76 (14.1%); £3,248,994.64 -> £2,789,396.90 (14.1%); £3,248,994.64 -> £2,789,397.03 (14.1%); £3,248,994.65 -> £2,789,397.17 (14.1%); £3,248,994.65 -> £2,789,397.30 (14.1%); £3,248,994.65 -> £2,789,397.43 (14.1%); £3,248,994.65 -> £2,789,397.56 (14.1%); £3,248,994.65 -> £2,789,397.69 (14.1%); £3,248,994.65 -> £2,789,397.82 (14.1%); £3,248,994.65 -> £2,789,397.82 (14.1%); £3,248,994.66 -> £2,789,397.83 (14.1%); £3,248,994.66 -> £2,789,397.84 (14.1%); £3,248,994.66 -> £2,789,397.85 (14.1%); £3,248,994.66 -> £2,789,397.87 (14.1%); £3,248,994.66 -> £2,789,397.89 (14.1%); £3,248,994.67 -> £2,789,397.92 (14.1%); £3,248,994.72 -> £2,789,397.95 (14.1%); £3,248,994.78 -> £2,789,397.98 (14.1%); £3,248,994.83 -> £2,789,398.00 (14.1%); £3,248,994.89 -> £2,789,398.03 (14.1%); £3,248,994.94 -> £2,789,398.06 (14.1%); £3,248,994.99 -> £2,789,398.08 (14.1%); £3,248,995.04 -> £2,789,398.09 (14.1%); £3,248,995.09 -> £2,789,398.11 (14.1%); £3,248,995.10 -> £2,789,398.13 (14.1%); £3,248,995.10 -> £2,789,398.15 (14.1%); £3,248,995.11 -> £2,789,398.17 (14.1%); £3,248,995.11 -> £2,789,398.19 (14.1%); £3,248,995.12 -> £2,789,398.21 (14.1%); £3,248,995.12 -> £2,789,398.22 (14.1%); £3,248,995.13 -> £2,789,398.24 (14.1%); £3,248,995.13 -> £2,789,398.26 (14.1%); £3,248,995.14 -> £2,789,398.28 (14.1%); £3,248,995.14 -> £2,789,398.30 (14.1%); £3,248,995.20 -> £2,789,398.35 (14.1%); £3,248,995.27 -> £2,789,398.39 (14.1%); £3,248,995.34 -> £2,789,398.44 (14.1%); £3,248,995.41 -> £2,789,398.49 (14.1%); £3,248,995.48 -> £2,789,398.53 (14.1%); £3,248,995.55 -> £2,789,398.57 (14.1%); £3,248,995.61 -> £2,789,398.61 (14.1%); £3,248,995.67 -> £2,789,398.65 (14.1%); £3,248,995.67 -> £2,789,398.69 (14.1%); £3,248,995.68 -> £2,789,398.73 (14.1%); £3,248,995.68 -> £2,789,398.77 (14.1%); £3,248,995.69 -> £2,789,398.80 (14.1%); £3,248,995.69 -> £2,789,398.82 (14.1%); £3,248,995.70 -> £2,789,398.84 (14.1%); £3,248,995.70 -> £2,789,398.86 (14.1%); £3,248,995.70 -> £2,789,399.00 (14.1%); £3,248,995.70 -> £2,789,399.13 (14.1%); £3,248,995.71 -> £2,789,399.27 (14.1%); £3,248,995.71 -> £2,789,399.41 (14.1%); £3,248,995.71 -> £2,789,399.54 (14.1%); £3,248,995.71 -> £2,789,399.67 (14.1%); £3,248,995.72 -> £2,789,399.81 (14.1%); £3,248,995.72 -> £2,789,399.95 (14.1%); £3,248,995.72 -> £2,789,399.96 (14.1%); £3,248,995.72 -> £2,789,399.97 (14.1%); £3,248,995.72 -> £2,789,399.98 (14.1%); £3,248,995.72 -> £2,789,399.99 (14.1%); £3,248,995.73 -> £2,789,400.00 (14.1%); £3,248,995.73 -> £2,789,400.02 (14.1%); £3,248,995.73 -> £2,789,400.04 (14.1%); £3,248,995.73 -> £2,789,400.06 (14.1%); £3,248,995.73 -> £2,789,400.09 (14.1%); £3,248,995.74 -> £2,789,400.11 (14.1%); £3,248,995.74 -> £2,789,400.14 (14.1%); £3,248,995.75 -> £2,789,400.17 (14.1%); £3,248,995.75 -> £2,789,400.20 (14.1%); £3,248,995.75 -> £2,789,400.22 (14.1%); £3,248,995.76 -> £2,789,400.24 (14.1%); £3,248,995.76 -> £2,789,400.26 (14.1%); £3,248,995.77 -> £2,789,400.28 (14.1%); £3,248,995.77 -> £2,789,400.31 (14.1%); £3,248,995.78 -> £2,789,400.33 (14.1%); £3,248,995.78 -> £2,789,400.35 (14.1%); £3,248,995.78 -> £2,789,400.37 (14.1%); £3,248,995.79 -> £2,789,400.39 (14.1%); £3,248,995.79 -> £2,789,400.41 (14.1%); £3,248,995.79 -> £2,789,400.43 (14.1%); £3,248,995.80 -> £2,789,400.45 (14.1%); £3,248,995.80 -> £2,789,400.48 (14.1%); £3,248,995.80 -> £2,789,400.53 (14.1%); £3,248,995.81 -> £2,789,400.57 (14.1%); £3,248,995.81 -> £2,789,400.61 (14.1%); £3,248,995.82 -> £2,789,400.65 (14.1%); £3,248,995.82 -> £2,789,400.69 (14.1%); £3,248,995.82 -> £2,789,400.73 (14.1%); £3,248,995.83 -> £2,789,400.77 (14.1%); £3,248,995.83 -> £2,789,400.81 (14.1%); £3,248,995.84 -> £2,789,400.85 (14.1%); £3,248,995.84 -> £2,789,400.89 (14.1%); £3,248,995.84 -> £2,789,400.91 (14.1%); £3,248,995.85 -> £2,789,400.94 (14.1%); £3,248,995.85 -> £2,789,400.96 (14.1%); £3,248,995.86 -> £2,789,400.97 (14.1%); £3,248,995.86 -> £2,789,401.11 (14.1%); £3,248,995.86 -> £2,789,401.24 (14.1%); £3,248,995.86 -> £2,789,401.37 (14.1%); £3,248,995.87 -> £2,789,401.51 (14.1%); £3,248,995.87 -> £2,789,401.64 (14.1%); £3,248,995.87 -> £2,789,401.76 (14.1%); £3,248,995.87 -> £2,789,401.89 (14.1%); £3,248,995.87 -> £2,789,402.03 (14.1%); £3,248,995.87 -> £2,789,402.03 (14.1%); £3,248,995.87 -> £2,789,402.04 (14.1%); £3,248,995.88 -> £2,789,402.05 (14.1%); £3,248,995.88 -> £2,789,402.06 (14.1%); £3,248,995.88 -> £2,789,402.07 (14.1%); £3,248,995.88 -> £2,789,402.09 (14.1%); £3,248,995.88 -> £2,789,402.11 (14.1%); £3,248,995.88 -> £2,789,402.13 (14.1%); £3,248,995.89 -> £2,789,402.15 (14.1%); £3,248,995.89 -> £2,789,402.18 (14.1%); £3,248,995.89 -> £2,789,402.21 (14.1%); £3,248,995.90 -> £2,789,402.24 (14.1%); £3,248,995.90 -> £2,789,402.26 (14.1%); £3,248,995.91 -> £2,789,402.29 (14.1%); £3,248,995.91 -> £2,789,402.32 (14.1%); £3,248,995.92 -> £2,789,402.35 (14.1%); £3,248,995.92 -> £2,789,402.38 (14.1%); £3,248,995.93 -> £2,789,402.41 (14.1%); £3,248,995.94 -> £2,789,402.44 (14.1%); £3,248,995.94 -> £2,789,402.46 (14.1%); £3,248,995.95 -> £2,789,402.49 (14.1%); £3,248,995.95 -> £2,789,402.51 (14.1%); £3,248,995.96 -> £2,789,402.53 (14.1%); £3,248,995.96 -> £2,789,402.55 (14.1%); £3,248,995.97 -> £2,789,402.57 (14.1%); £3,248,995.97 -> £2,789,402.61 (14.1%); £3,248,995.98 -> £2,789,402.66 (14.1%); £3,248,995.98 -> £2,789,402.70 (14.1%); £3,248,995.99 -> £2,789,402.74 (14.1%); £3,248,995.99 -> £2,789,402.78 (14.1%); £3,248,995.99 -> £2,789,402.82 (14.1%); £3,248,996.00 -> £2,789,402.86 (14.1%); £3,248,996.01 -> £2,789,402.90 (14.1%); £3,248,996.01 -> £2,789,402.94 (14.1%); £3,248,996.01 -> £2,789,402.98 (14.1%); £3,248,996.02 -> £2,789,403.03 (14.1%); £3,248,996.02 -> £2,789,403.05 (14.1%); £3,248,996.03 -> £2,789,403.08 (14.1%); £3,248,996.03 -> £2,789,403.10 (14.1%); £3,248,996.03 -> £2,789,403.11 (14.1%); £3,248,996.04 -> £2,789,403.25 (14.1%); £3,248,996.04 -> £2,789,403.38 (14.1%); £3,248,996.04 -> £2,789,403.51 (14.1%); £3,248,996.04 -> £2,789,403.64 (14.1%); £3,248,996.04 -> £2,789,403.77 (14.1%); £3,248,996.04 -> £2,789,403.90 (14.1%); £3,248,996.04 -> £2,789,404.03 (14.1%); £3,248,996.05 -> £2,789,404.16 (14.1%); £3,248,996.05 -> £2,789,404.17 (14.1%); £3,248,996.05 -> £2,789,404.18 (14.1%); £3,248,996.05 -> £2,789,404.19 (14.1%); £3,248,996.05 -> £2,789,404.20 (14.1%); £3,248,996.05 -> £2,789,404.22 (14.1%); £3,248,996.06 -> £2,789,404.24 (14.1%); £3,248,996.06 -> £2,789,404.26 (14.1%); £3,248,996.13 -> £2,789,404.29 (14.1%); £3,248,996.20 -> £2,789,404.32 (14.1%); £3,248,996.28 -> £2,789,404.34 (14.1%); £3,248,996.35 -> £2,789,404.37 (14.1%); £3,248,996.42 -> £2,789,404.39 (14.1%); £3,248,996.49 -> £2,789,404.41 (14.1%); £3,248,996.54 -> £2,789,404.43 (14.1%); £3,248,996.59 -> £2,789,404.45 (14.1%); £3,248,996.59 -> £2,789,404.47 (14.1%); £3,248,996.60 -> £2,789,404.49 (14.1%); £3,248,996.60 -> £2,789,404.50 (14.1%); £3,248,996.61 -> £2,789,404.52 (14.1%); £3,248,996.61 -> £2,789,404.54 (14.1%); £3,248,996.61 -> £2,789,404.56 (14.1%); £3,248,996.62 -> £2,789,404.57 (14.1%); £3,248,996.62 -> £2,789,404.59 (14.1%); £3,248,996.62 -> £2,789,404.61 (14.1%); £3,248,996.63 -> £2,789,404.63 (14.1%); £3,248,996.69 -> £2,789,404.67 (14.1%); £3,248,996.77 -> £2,789,404.72 (14.1%); £3,248,996.85 -> £2,789,404.77 (14.1%); £3,248,996.94 -> £2,789,404.81 (14.1%); £3,248,997.02 -> £2,789,404.85 (14.1%); £3,248,997.10 -> £2,789,404.90 (14.1%); £3,248,997.18 -> £2,789,404.94 (14.1%); £3,248,997.25 -> £2,789,404.98 (14.1%); £3,248,997.26 -> £2,789,405.02 (14.1%); £3,248,997.27 -> £2,789,405.06 (14.1%); £3,248,997.27 -> £2,789,405.10 (14.1%); £3,248,997.28 -> £2,789,405.13 (14.1%); £3,248,997.29 -> £2,789,405.16 (14.1%); £3,248,997.29 -> £2,789,405.18 (14.1%); £3,248,997.30 -> £2,789,405.19 (14.1%); £3,248,997.30 -> £2,789,405.33 (14.1%); £3,248,997.30 -> £2,789,405.46 (14.1%); £3,248,997.30 -> £2,789,405.59 (14.1%); £3,248,997.30 -> £2,789,405.72 (14.1%); £3,248,997.31 -> £2,789,405.85 (14.1%); £3,248,997.31 -> £2,789,405.98 (14.1%); £3,248,997.31 -> £2,789,406.10 (14.1%); £3,248,997.31 -> £2,789,406.23 (14.1%); £3,248,997.31 -> £2,789,406.24 (14.1%); £3,248,997.31 -> £2,789,406.25 (14.1%); £3,248,997.31 -> £2,789,406.26 (14.1%); £3,248,997.31 -> £2,789,406.27 (14.1%); £3,248,997.32 -> £2,789,406.29 (14.1%); £3,248,997.32 -> £2,789,406.31 (14.1%); £3,248,997.33 -> £2,789,406.33 (14.1%); £3,248,997.41 -> £2,789,406.36 (14.1%); £3,248,997.49 -> £2,789,406.39 (14.1%); £3,248,997.58 -> £2,789,406.42 (14.1%); £3,248,997.66 -> £2,789,406.44 (14.1%); £3,248,997.74 -> £2,789,406.47 (14.1%); £3,248,997.82 -> £2,789,406.49 (14.1%); £3,248,997.87 -> £2,789,406.51 (14.1%); £3,248,997.92 -> £2,789,406.52 (14.1%); £3,248,997.93 -> £2,789,406.54 (14.1%); £3,248,997.93 -> £2,789,406.56 (14.1%); £3,248,997.93 -> £2,789,406.58 (14.1%); £3,248,997.94 -> £2,789,406.60 (14.1%); £3,248,997.94 -> £2,789,406.61 (14.1%); £3,248,997.95 -> £2,789,406.63 (14.1%); £3,248,997.95 -> £2,789,406.65 (14.1%); £3,248,997.95 -> £2,789,406.67 (14.1%); £3,248,997.96 -> £2,789,406.69 (14.1%); £3,248,997.96 -> £2,789,406.71 (14.1%); £3,248,998.02 -> £2,789,406.75 (14.1%); £3,248,998.11 -> £2,789,406.80 (14.1%); £3,248,998.20 -> £2,789,406.84 (14.1%); £3,248,998.29 -> £2,789,406.89 (14.1%); £3,248,998.38 -> £2,789,406.93 (14.1%); £3,248,998.47 -> £2,789,406.97 (14.1%); £3,248,998.55 -> £2,789,407.01 (14.1%); £3,248,998.63 -> £2,789,407.05 (14.1%); £3,248,998.64 -> £2,789,407.09 (14.1%); £3,248,998.64 -> £2,789,407.13 (14.1%); £3,248,998.65 -> £2,789,407.17 (14.1%); £3,248,998.66 -> £2,789,407.20 (14.1%); £3,248,998.66 -> £2,789,407.22 (14.1%); £3,248,998.67 -> £2,789,407.24 (14.1%); £3,248,998.67 -> £2,789,407.26 (14.1%); £3,248,998.67 -> £2,789,407.39 (14.1%); £3,248,998.68 -> £2,789,407.53 (14.1%); £3,248,998.68 -> £2,789,407.65 (14.1%); £3,248,998.68 -> £2,789,407.78 (14.1%); £3,248,998.68 -> £2,789,407.91 (14.1%); £3,248,998.68 -> £2,789,408.04 (14.1%); £3,248,998.68 -> £2,789,408.17 (14.1%); £3,248,998.68 -> £2,789,408.31 (14.1%); £3,248,998.69 -> £2,789,408.31 (14.1%); £3,248,998.69 -> £2,789,408.32 (14.1%); £3,248,998.69 -> £2,789,408.33 (14.1%); £3,248,998.69 -> £2,789,408.34 (14.1%); £3,248,998.69 -> £2,789,408.36 (14.1%); £3,248,998.70 -> £2,789,408.38 (14.1%); £3,248,998.70 -> £2,789,408.40 (14.1%); £3,248,998.79 -> £2,789,408.43 (14.1%); £3,248,998.89 -> £2,789,408.46 (14.1%); £3,248,998.99 -> £2,789,408.48 (14.1%); £3,248,999.08 -> £2,789,408.51 (14.1%); £3,248,999.18 -> £2,789,408.53 (14.1%); £3,248,999.27 -> £2,789,408.55 (14.1%); £3,248,999.32 -> £2,789,408.57 (14.1%); £3,248,999.37 -> £2,789,408.59 (14.1%); £3,248,999.38 -> £2,789,408.61 (14.1%); £3,248,999.38 -> £2,789,408.63 (14.1%); £3,248,999.39 -> £2,789,408.65 (14.1%); £3,248,999.39 -> £2,789,408.66 (14.1%); £3,248,999.39 -> £2,789,408.68 (14.1%); £3,248,999.40 -> £2,789,408.70 (14.1%); £3,248,999.40 -> £2,789,408.72 (14.1%); £3,248,999.41 -> £2,789,408.73 (14.1%); £3,248,999.41 -> £2,789,408.75 (14.1%); £3,248,999.41 -> £2,789,408.77 (14.1%); £3,248,999.48 -> £2,789,408.82 (14.1%); £3,248,999.57 -> £2,789,408.87 (14.1%); £3,248,999.68 -> £2,789,408.91 (14.1%); £3,248,999.78 -> £2,789,408.96 (14.1%); £3,248,999.88 -> £2,789,409.00 (14.1%); £3,248,999.98 -> £2,789,409.04 (14.1%); £3,249,000.07 -> £2,789,409.08 (14.1%); £3,249,000.17 -> £2,789,409.12 (14.1%); £3,249,000.17 -> £2,789,409.16 (14.1%); £3,249,000.18 -> £2,789,409.20 (14.1%); £3,249,000.19 -> £2,789,409.24 (14.1%); £3,249,000.19 -> £2,789,409.27 (14.1%); £3,249,000.20 -> £2,789,409.30 (14.1%); £3,249,000.20 -> £2,789,409.32 (14.1%); £3,249,000.21 -> £2,789,409.33 (14.1%); £3,249,000.21 -> £2,789,409.47 (14.1%); £3,249,000.21 -> £2,789,409.60 (14.1%); £3,249,000.22 -> £2,789,409.74 (14.1%); £3,249,000.22 -> £2,789,409.87 (14.1%); £3,249,000.22 -> £2,789,410.00 (14.1%); £3,249,000.22 -> £2,789,410.14 (14.1%); £3,249,000.22 -> £2,789,410.27 (14.1%); £3,249,000.23 -> £2,789,410.40 (14.1%); £3,249,000.23 -> £2,789,410.41 (14.1%); £3,249,000.23 -> £2,789,410.42 (14.1%); £3,249,000.23 -> £2,789,410.43 (14.1%); £3,249,000.23 -> £2,789,410.44 (14.1%); £3,249,000.23 -> £2,789,410.45 (14.1%); £3,249,000.24 -> £2,789,410.47 (14.1%); £3,249,000.25 -> £2,789,410.50 (14.1%); £3,249,000.39 -> £2,789,410.53 (14.1%); £3,249,000.52 -> £2,789,410.56 (14.1%); £3,249,000.66 -> £2,789,410.58 (14.1%); £3,249,000.80 -> £2,789,410.61 (14.1%); £3,249,000.93 -> £2,789,410.63 (14.1%); £3,249,001.06 -> £2,789,410.65 (14.1%); £3,249,001.11 -> £2,789,410.67 (14.1%); £3,249,001.17 -> £2,789,410.69 (14.1%); £3,249,001.17 -> £2,789,410.71 (14.1%); £3,249,001.17 -> £2,789,410.73 (14.1%); £3,249,001.18 -> £2,789,410.75 (14.1%); £3,249,001.18 -> £2,789,410.76 (14.1%); £3,249,001.19 -> £2,789,410.78 (14.1%); £3,249,001.19 -> £2,789,410.80 (14.1%); £3,249,001.20 -> £2,789,410.82 (14.1%); £3,249,001.20 -> £2,789,410.83 (14.1%); £3,249,001.20 -> £2,789,410.85 (14.1%); £3,249,001.21 -> £2,789,410.88 (14.1%); £3,249,001.27 -> £2,789,410.92 (14.1%); £3,249,001.40 -> £2,789,410.97 (14.1%); £3,249,001.53 -> £2,789,411.01 (14.1%); £3,249,001.66 -> £2,789,411.06 (14.1%); £3,249,001.79 -> £2,789,411.10 (14.1%); £3,249,001.92 -> £2,789,411.15 (14.1%); £3,249,002.04 -> £2,789,411.19 (14.1%); £3,249,002.17 -> £2,789,411.23 (14.1%); £3,249,002.18 -> £2,789,411.27 (14.1%); £3,249,002.18 -> £2,789,411.31 (14.1%); £3,249,002.20 -> £2,789,411.35 (14.1%); £3,249,002.21 -> £2,789,411.38 (14.1%); £3,249,002.21 -> £2,789,411.41 (14.1%); £3,249,002.22 -> £2,789,411.43 (14.1%); £3,249,002.23 -> £2,789,411.44 (14.1%); £3,249,002.23 -> £2,789,411.58 (14.1%); £3,249,002.23 -> £2,789,411.72 (14.1%); £3,249,002.23 -> £2,789,411.85 (14.1%); £3,249,002.24 -> £2,789,411.98 (14.1%); £3,249,002.24 -> £2,789,412.12 (14.1%); £3,249,002.24 -> £2,789,412.25 (14.1%); £3,249,002.24 -> £2,789,412.38 (14.1%); £3,249,002.24 -> £2,789,412.51 (14.1%); £3,249,002.24 -> £2,789,412.52 (14.1%); £3,249,002.24 -> £2,789,412.52 (14.1%); £3,249,002.24 -> £2,789,412.53 (14.1%); £3,249,002.25 -> £2,789,412.54 (14.1%); £3,249,002.25 -> £2,789,412.56 (14.1%); £3,249,002.25 -> £2,789,412.58 (14.1%); £3,249,002.26 -> £2,789,412.61 (14.1%); £3,249,002.35 -> £2,789,412.63 (14.1%); £3,249,002.44 -> £2,789,412.66 (14.1%); £3,249,002.54 -> £2,789,412.69 (14.1%); £3,249,002.63 -> £2,789,412.72 (14.1%); £3,249,002.72 -> £2,789,412.74 (14.1%); £3,249,002.81 -> £2,789,412.76 (14.1%); £3,249,002.86 -> £2,789,412.78 (14.1%); £3,249,002.91 -> £2,789,412.79 (14.1%); £3,249,002.92 -> £2,789,412.81 (14.1%); £3,249,002.92 -> £2,789,412.83 (14.1%); £3,249,002.92 -> £2,789,412.85 (14.1%); £3,249,002.93 -> £2,789,412.87 (14.1%); £3,249,002.93 -> £2,789,412.88 (14.1%); £3,249,002.93 -> £2,789,412.90 (14.1%); £3,249,002.94 -> £2,789,412.92 (14.1%); £3,249,002.94 -> £2,789,412.94 (14.1%); £3,249,002.94 -> £2,789,412.95 (14.1%); £3,249,002.95 -> £2,789,412.98 (14.1%); £3,249,003.01 -> £2,789,413.02 (14.1%); £3,249,003.10 -> £2,789,413.07 (14.1%); £3,249,003.20 -> £2,789,413.11 (14.1%); £3,249,003.30 -> £2,789,413.16 (14.1%); £3,249,003.40 -> £2,789,413.20 (14.1%); £3,249,003.50 -> £2,789,413.25 (14.1%); £3,249,003.59 -> £2,789,413.29 (14.1%); £3,249,003.68 -> £2,789,413.33 (14.1%); £3,249,003.69 -> £2,789,413.37 (14.1%); £3,249,003.70 -> £2,789,413.41 (14.1%); £3,249,003.70 -> £2,789,413.46 (14.1%); £3,249,003.71 -> £2,789,413.48 (14.1%); £3,249,003.72 -> £2,789,413.51 (14.1%); £3,249,003.72 -> £2,789,413.53 (14.1%); £3,249,003.73 -> £2,789,413.55 (14.1%); £3,249,003.73 -> £2,789,413.69 (14.1%); £3,249,003.74 -> £2,789,413.83 (14.1%); £3,249,003.74 -> £2,789,413.97 (14.1%); £3,249,003.74 -> £2,789,414.11 (14.1%); £3,249,003.75 -> £2,789,414.24 (14.1%); £3,249,003.75 -> £2,789,414.38 (14.1%); £3,249,003.75 -> £2,789,414.52 (14.1%); £3,249,003.75 -> £2,789,414.66 (14.1%); £3,249,003.75 -> £2,789,414.66 (14.1%); £3,249,003.76 -> £2,789,414.67 (14.1%); £3,249,003.76 -> £2,789,414.68 (14.1%); £3,249,003.76 -> £2,789,414.69 (14.1%); £3,249,003.76 -> £2,789,414.71 (14.1%); £3,249,003.76 -> £2,789,414.72 (14.1%); £3,249,003.76 -> £2,789,414.74 (14.1%); £3,249,003.77 -> £2,789,414.77 (14.1%); £3,249,003.77 -> £2,789,414.79 (14.1%); £3,249,003.78 -> £2,789,414.82 (14.1%); £3,249,003.78 -> £2,789,414.86 (14.1%); £3,249,003.79 -> £2,789,414.89 (14.1%); £3,249,003.79 -> £2,789,414.91 (14.1%); £3,249,003.80 -> £2,789,414.93 (14.1%); £3,249,003.81 -> £2,789,414.95 (14.1%); £3,249,003.81 -> £2,789,414.98 (14.1%); £3,249,003.82 -> £2,789,415.00 (14.1%); £3,249,003.82 -> £2,789,415.02 (14.1%); £3,249,003.83 -> £2,789,415.05 (14.1%); £3,249,003.83 -> £2,789,415.07 (14.1%); £3,249,003.84 -> £2,789,415.09 (14.1%); £3,249,003.84 -> £2,789,415.11 (14.1%); £3,249,003.85 -> £2,789,415.13 (14.1%); £3,249,003.86 -> £2,789,415.15 (14.1%); £3,249,003.86 -> £2,789,415.17 (14.1%); £3,249,003.87 -> £2,789,415.22 (14.1%); £3,249,003.87 -> £2,789,415.26 (14.1%); £3,249,003.88 -> £2,789,415.30 (14.1%); £3,249,003.88 -> £2,789,415.35 (14.1%); £3,249,003.89 -> £2,789,415.39 (14.1%); £3,249,003.89 -> £2,789,415.43 (14.1%); £3,249,003.90 -> £2,789,415.47 (14.1%); £3,249,003.90 -> £2,789,415.51 (14.1%); £3,249,003.91 -> £2,789,415.55 (14.1%); £3,249,003.91 -> £2,789,415.58 (14.1%); £3,249,003.91 -> £2,789,415.63 (14.1%); £3,249,003.92 -> £2,789,415.65 (14.1%); £3,249,003.93 -> £2,789,415.68 (14.1%); £3,249,003.93 -> £2,789,415.70 (14.1%); £3,249,003.94 -> £2,789,415.72 (14.1%); £3,249,003.94 -> £2,789,415.85 (14.1%); £3,249,003.94 -> £2,789,415.99 (14.1%); £3,249,003.95 -> £2,789,416.12 (14.1%); £3,249,003.95 -> £2,789,416.26 (14.1%); £3,249,003.95 -> £2,789,416.40 (14.1%); £3,249,003.95 -> £2,789,416.54 (14.1%); £3,249,003.96 -> £2,789,416.67 (14.1%); £3,249,003.96 -> £2,789,416.80 (14.1%); £3,249,003.96 -> £2,789,416.81 (14.1%); £3,249,003.96 -> £2,789,416.82 (14.1%); £3,249,003.96 -> £2,789,416.83 (14.1%); £3,249,003.97 -> £2,789,416.83 (14.1%); £3,249,003.97 -> £2,789,416.85 (14.1%); £3,249,003.98 -> £2,789,416.86 (14.1%); £3,249,003.99 -> £2,789,416.88 (14.1%); £3,249,004.00 -> £2,789,416.90 (14.1%); £3,249,004.01 -> £2,789,416.93 (14.1%); £3,249,004.02 -> £2,789,416.96 (14.1%); £3,249,004.03 -> £2,789,416.99 (14.1%); £3,249,004.05 -> £2,789,417.02 (14.1%); £3,249,004.06 -> £2,789,417.05 (14.1%); £3,249,004.07 -> £2,789,417.08 (14.1%); £3,249,004.08 -> £2,789,417.11 (14.1%); £3,249,004.09 -> £2,789,417.14 (14.1%); £3,249,004.10 -> £2,789,417.17 (14.1%); £3,249,004.11 -> £2,789,417.20 (14.1%); £3,249,004.12 -> £2,789,417.23 (14.1%); £3,249,004.13 -> £2,789,417.26 (14.1%); £3,249,004.13 -> £2,789,417.28 (14.1%); £3,249,004.14 -> £2,789,417.31 (14.1%); £3,249,004.15 -> £2,789,417.33 (14.1%); £3,249,004.15 -> £2,789,417.35 (14.1%); £3,249,004.16 -> £2,789,417.38 (14.1%); £3,249,004.16 -> £2,789,417.42 (14.1%); £3,249,004.17 -> £2,789,417.46 (14.1%); £3,249,004.18 -> £2,789,417.50 (14.1%); £3,249,004.19 -> £2,789,417.55 (14.1%); £3,249,004.20 -> £2,789,417.59 (14.1%); £3,249,004.22 -> £2,789,417.63 (14.1%); £3,249,004.23 -> £2,789,417.67 (14.1%); £3,249,004.23 -> £2,789,417.71 (14.1%); £3,249,004.24 -> £2,789,417.75 (14.1%); £3,249,004.25 -> £2,789,417.79 (14.1%); £3,249,004.26 -> £2,789,417.84 (14.1%); £3,249,004.27 -> £2,789,417.86 (14.1%); £3,249,004.27 -> £2,789,417.89 (14.1%); £3,249,004.28 -> £2,789,417.91 (14.1%); £3,249,004.28 -> £2,789,417.93 (14.1%); £3,249,004.29 -> £2,789,418.06 (14.1%); £3,249,004.29 -> £2,789,418.20 (14.1%); £3,249,004.29 -> £2,789,418.33 (14.1%); £3,249,004.29 -> £2,789,418.47 (14.1%); £3,249,004.30 -> £2,789,418.60 (14.1%); £3,249,004.30 -> £2,789,418.73 (14.1%); £3,249,004.30 -> £2,789,418.87 (14.1%); £3,249,004.30 -> £2,789,419.00 (14.1%); £3,249,004.30 -> £2,789,419.01 (14.1%); £3,249,004.30 -> £2,789,419.02 (14.1%); £3,249,004.30 -> £2,789,419.03 (14.1%); £3,249,004.31 -> £2,789,419.04 (14.1%); £3,249,004.31 -> £2,789,419.05 (14.1%); £3,249,004.32 -> £2,789,419.07 (14.1%); £3,249,004.33 -> £2,789,419.10 (14.1%); £3,249,004.49 -> £2,789,419.13 (14.1%); £3,249,004.66 -> £2,789,419.16 (14.1%); £3,249,004.82 -> £2,789,419.18 (14.1%); £3,249,004.98 -> £2,789,419.21 (14.1%); £3,249,005.14 -> £2,789,419.24 (14.1%); £3,249,005.30 -> £2,789,419.26 (14.1%); £3,249,005.35 -> £2,789,419.27 (14.1%); £3,249,005.40 -> £2,789,419.29 (14.1%); £3,249,005.41 -> £2,789,419.31 (14.1%); £3,249,005.41 -> £2,789,419.33 (14.1%); £3,249,005.42 -> £2,789,419.35 (14.1%); £3,249,005.42 -> £2,789,419.37 (14.1%); £3,249,005.43 -> £2,789,419.39 (14.1%); £3,249,005.43 -> £2,789,419.41 (14.1%); £3,249,005.44 -> £2,789,419.43 (14.1%); £3,249,005.45 -> £2,789,419.45 (14.1%); £3,249,005.45 -> £2,789,419.46 (14.1%); £3,249,005.45 -> £2,789,419.49 (14.1%); £3,249,005.52 -> £2,789,419.53 (14.1%); £3,249,005.66 -> £2,789,419.58 (14.1%); £3,249,005.82 -> £2,789,419.63 (14.1%); £3,249,005.97 -> £2,789,419.67 (14.1%); £3,249,006.11 -> £2,789,419.72 (14.1%); £3,249,006.26 -> £2,789,419.76 (14.1%); £3,249,006.40 -> £2,789,419.80 (14.1%); £3,249,006.54 -> £2,789,419.84 (14.1%); £3,249,006.55 -> £2,789,419.88 (14.1%); £3,249,006.56 -> £2,789,419.92 (14.1%); £3,249,006.57 -> £2,789,419.96 (14.1%); £3,249,006.58 -> £2,789,419.99 (14.1%); £3,249,006.59 -> £2,789,420.01 (14.1%); £3,249,006.59 -> £2,789,420.04 (14.1%); £3,249,006.60 -> £2,789,420.05 (14.1%); £3,249,006.60 -> £2,789,420.19 (14.1%); £3,249,006.60 -> £2,789,420.32 (14.1%); £3,249,006.61 -> £2,789,420.46 (14.1%); £3,249,006.61 -> £2,789,420.59 (14.1%); £3,249,006.61 -> £2,789,420.73 (14.1%); £3,249,006.61 -> £2,789,420.86 (14.1%); £3,249,006.61 -> £2,789,420.99 (14.1%); £3,249,006.61 -> £2,789,421.12 (14.1%); £3,249,006.62 -> £2,789,421.12 (14.1%); £3,249,006.62 -> £2,789,421.13 (14.1%); £3,249,006.62 -> £2,789,421.14 (14.1%); £3,249,006.62 -> £2,789,421.15 (14.1%); £3,249,006.62 -> £2,789,421.17 (14.1%); £3,249,006.64 -> £2,789,421.19 (14.1%); £3,249,006.65 -> £2,789,421.22 (14.1%); £3,249,006.82 -> £2,789,421.24 (14.1%); £3,249,006.99 -> £2,789,421.27 (14.1%); £3,249,007.17 -> £2,789,421.30 (14.1%); £3,249,007.34 -> £2,789,421.33 (14.1%); £3,249,007.51 -> £2,789,421.35 (14.1%); £3,249,007.67 -> £2,789,421.37 (14.1%); £3,249,007.73 -> £2,789,421.39 (14.1%); £3,249,007.78 -> £2,789,421.41 (14.1%); £3,249,007.78 -> £2,789,421.43 (14.1%); £3,249,007.79 -> £2,789,421.45 (14.1%); £3,249,007.79 -> £2,789,421.46 (14.1%); £3,249,007.79 -> £2,789,421.48 (14.1%); £3,249,007.80 -> £2,789,421.50 (14.1%); £3,249,007.80 -> £2,789,421.52 (14.1%); £3,249,007.81 -> £2,789,421.53 (14.1%); £3,249,007.81 -> £2,789,421.55 (14.1%); £3,249,007.81 -> £2,789,421.57 (14.1%); £3,249,007.82 -> £2,789,421.59 (14.1%); £3,249,007.88 -> £2,789,421.64 (14.1%); £3,249,008.03 -> £2,789,421.68 (14.1%); £3,249,008.19 -> £2,789,421.73 (14.1%); £3,249,008.35 -> £2,789,421.77 (14.1%); £3,249,008.49 -> £2,789,421.81 (14.1%); £3,249,008.64 -> £2,789,421.85 (14.1%); £3,249,008.78 -> £2,789,421.89 (14.1%); £3,249,008.92 -> £2,789,421.93 (14.1%); £3,249,008.93 -> £2,789,421.96 (14.1%); £3,249,008.94 -> £2,789,422.01 (14.1%); £3,249,008.95 -> £2,789,422.05 (14.1%); £3,249,008.96 -> £2,789,422.08 (14.1%); £3,249,008.97 -> £2,789,422.10 (14.1%); £3,249,008.97 -> £2,789,422.12 (14.1%); £3,249,008.98 -> £2,789,422.14 (14.1%); £3,249,008.98 -> £2,789,422.27 (14.1%); £3,249,008.98 -> £2,789,422.40 (14.1%); £3,249,008.99 -> £2,789,422.53 (14.1%); £3,249,008.99 -> £2,789,422.66 (14.1%); £3,249,008.99 -> £2,789,422.79 (14.1%); £3,249,008.99 -> £2,789,422.92 (14.1%); £3,249,008.99 -> £2,789,423.05 (14.1%); £3,249,008.99 -> £2,789,423.19 (14.1%); £3,249,008.99 -> £2,789,423.19 (14.1%); £3,249,008.99 -> £2,789,423.20 (14.1%); £3,249,009.00 -> £2,789,423.21 (14.1%); £3,249,009.00 -> £2,789,423.22 (14.1%); £3,249,009.00 -> £2,789,423.24 (14.1%); £3,249,009.01 -> £2,789,423.26 (14.1%); £3,249,009.01 -> £2,789,423.28 (14.1%); £3,249,009.14 -> £2,789,423.31 (14.1%); £3,249,009.27 -> £2,789,423.34 (14.1%); £3,249,009.41 -> £2,789,423.36 (14.1%); £3,249,009.53 -> £2,789,423.39 (14.1%); £3,249,009.66 -> £2,789,423.41 (14.1%); £3,249,009.79 -> £2,789,423.43 (14.1%); £3,249,009.84 -> £2,789,423.45 (14.1%); £3,249,009.90 -> £2,789,423.47 (14.1%); £3,249,009.90 -> £2,789,423.49 (14.1%); £3,249,009.90 -> £2,789,423.51 (14.1%); £3,249,009.91 -> £2,789,423.53 (14.1%); £3,249,009.91 -> £2,789,423.55 (14.1%); £3,249,009.92 -> £2,789,423.56 (14.1%); £3,249,009.92 -> £2,789,423.58 (14.1%); £3,249,009.92 -> £2,789,423.60 (14.1%); £3,249,009.93 -> £2,789,423.61 (14.1%); £3,249,009.93 -> £2,789,423.63 (14.1%); £3,249,009.93 -> £2,789,423.65 (14.1%); £3,249,009.99 -> £2,789,423.70 (14.1%); £3,249,010.12 -> £2,789,423.75 (14.1%); £3,249,010.25 -> £2,789,423.79 (14.1%); £3,249,010.38 -> £2,789,423.84 (14.1%); £3,249,010.50 -> £2,789,423.88 (14.1%); £3,249,010.62 -> £2,789,423.92 (14.1%); £3,249,010.74 -> £2,789,423.96 (14.1%); £3,249,010.86 -> £2,789,424.00 (14.1%); £3,249,010.87 -> £2,789,424.04 (14.1%); £3,249,010.88 -> £2,789,424.08 (14.1%); £3,249,010.89 -> £2,789,424.13 (14.1%); £3,249,010.90 -> £2,789,424.15 (14.1%); £3,249,010.90 -> £2,789,424.18 (14.1%); £3,249,010.91 -> £2,789,424.20 (14.1%); £3,249,010.91 -> £2,789,424.22 (14.1%); £3,249,010.92 -> £2,789,424.35 (14.1%); £3,249,010.92 -> £2,789,424.49 (14.1%); £3,249,010.92 -> £2,789,424.62 (14.1%); £3,249,010.92 -> £2,789,424.76 (14.1%); £3,249,010.93 -> £2,789,424.89 (14.1%); £3,249,010.93 -> £2,789,425.02 (14.1%); £3,249,010.93 -> £2,789,425.15 (14.1%); £3,249,010.93 -> £2,789,425.29 (14.1%); £3,249,010.93 -> £2,789,425.30 (14.1%); £3,249,010.93 -> £2,789,425.31 (14.1%); £3,249,010.93 -> £2,789,425.31 (14.1%); £3,249,010.94 -> £2,789,425.32 (14.1%); £3,249,010.94 -> £2,789,425.34 (14.1%); £3,249,010.95 -> £2,789,425.36 (14.1%); £3,249,010.96 -> £2,789,425.38 (14.1%); £3,249,011.12 -> £2,789,425.41 (14.1%); £3,249,011.28 -> £2,789,425.44 (14.1%); £3,249,011.44 -> £2,789,425.47 (14.1%); £3,249,011.60 -> £2,789,425.49 (14.1%); £3,249,011.76 -> £2,789,425.52 (14.1%); £3,249,011.91 -> £2,789,425.54 (14.1%); £3,249,011.97 -> £2,789,425.56 (14.1%); £3,249,012.02 -> £2,789,425.57 (14.1%); £3,249,012.02 -> £2,789,425.59 (14.1%); £3,249,012.03 -> £2,789,425.61 (14.1%); £3,249,012.03 -> £2,789,425.63 (14.1%); £3,249,012.03 -> £2,789,425.65 (14.1%); £3,249,012.03 -> £2,789,425.66 (14.1%); £3,249,012.04 -> £2,789,425.68 (14.1%); £3,249,012.04 -> £2,789,425.70 (14.1%); £3,249,012.04 -> £2,789,425.71 (14.1%); £3,249,012.05 -> £2,789,425.73 (14.1%); £3,249,012.05 -> £2,789,425.75 (14.1%); £3,249,012.11 -> £2,789,425.80 (14.1%); £3,249,012.25 -> £2,789,425.84 (14.1%); £3,249,012.40 -> £2,789,425.89 (14.1%); £3,249,012.55 -> £2,789,425.93 (14.1%); £3,249,012.70 -> £2,789,425.98 (14.1%); £3,249,012.84 -> £2,789,426.02 (14.1%); £3,249,012.98 -> £2,789,426.06 (14.1%); £3,249,013.12 -> £2,789,426.10 (14.1%); £3,249,013.13 -> £2,789,426.14 (14.1%); £3,249,013.14 -> £2,789,426.18 (14.1%); £3,249,013.15 -> £2,789,426.22 (14.1%); £3,249,013.16 -> £2,789,426.25 (14.1%); £3,249,013.17 -> £2,789,426.27 (14.1%); £3,249,013.17 -> £2,789,426.29 (14.1%); £3,249,013.18 -> £2,789,426.31 (14.1%); £3,249,013.18 -> £2,789,426.44 (14.1%); £3,249,013.18 -> £2,789,426.58 (14.1%); £3,249,013.18 -> £2,789,426.71 (14.1%); £3,249,013.18 -> £2,789,426.84 (14.1%); £3,249,013.19 -> £2,789,426.97 (14.1%); £3,249,013.19 -> £2,789,427.10 (14.1%); £3,249,013.19 -> £2,789,427.23 (14.1%); £3,249,013.19 -> £2,789,427.37 (14.1%); £3,249,013.19 -> £2,789,427.37 (14.1%); £3,249,013.19 -> £2,789,427.38 (14.1%); £3,249,013.20 -> £2,789,427.39 (14.1%); £3,249,013.20 -> £2,789,427.40 (14.1%); £3,249,013.20 -> £2,789,427.42 (14.1%); £3,249,013.21 -> £2,789,427.44 (14.1%); £3,249,013.22 -> £2,789,427.46 (14.1%); £3,249,013.33 -> £2,789,427.49 (14.1%); £3,249,013.45 -> £2,789,427.52 (14.1%); £3,249,013.56 -> £2,789,427.55 (14.1%); £3,249,013.68 -> £2,789,427.57 (14.1%); £3,249,013.79 -> £2,789,427.60 (14.1%); £3,249,013.91 -> £2,789,427.62 (14.1%); £3,249,013.96 -> £2,789,427.63 (14.1%); £3,249,014.01 -> £2,789,427.65 (14.1%); £3,249,014.02 -> £2,789,427.67 (14.1%); £3,249,014.02 -> £2,789,427.69 (14.1%); £3,249,014.02 -> £2,789,427.71 (14.1%); £3,249,014.03 -> £2,789,427.73 (14.1%); £3,249,014.03 -> £2,789,427.74 (14.1%); £3,249,014.03 -> £2,789,427.76 (14.1%); £3,249,014.04 -> £2,789,427.78 (14.1%); £3,249,014.04 -> £2,789,427.80 (14.1%); £3,249,014.05 -> £2,789,427.82 (14.1%); £3,249,014.05 -> £2,789,427.84 (14.1%); £3,249,014.11 -> £2,789,427.88 (14.1%); £3,249,014.22 -> £2,789,427.93 (14.1%); £3,249,014.34 -> £2,789,427.97 (14.1%); £3,249,014.46 -> £2,789,428.02 (14.1%); £3,249,014.57 -> £2,789,428.06 (14.1%); £3,249,014.68 -> £2,789,428.10 (14.1%); £3,249,014.79 -> £2,789,428.14 (14.1%); £3,249,014.90 -> £2,789,428.18 (14.1%); £3,249,014.91 -> £2,789,428.22 (14.1%); £3,249,014.92 -> £2,789,428.27 (14.1%); £3,249,014.93 -> £2,789,428.31 (14.1%); £3,249,014.93 -> £2,789,428.34 (14.1%); £3,249,014.94 -> £2,789,428.36 (14.1%); £3,249,014.95 -> £2,789,428.38 (14.1%); £3,249,014.95 -> £2,789,428.40 (14.1%); £3,249,014.95 -> £2,789,428.54 (14.1%); £3,249,014.96 -> £2,789,428.67 (14.1%); £3,249,014.96 -> £2,789,428.81 (14.1%); £3,249,014.96 -> £2,789,428.94 (14.1%); £3,249,014.96 -> £2,789,429.08 (14.1%); £3,249,014.97 -> £2,789,429.21 (14.1%); £3,249,014.97 -> £2,789,429.34 (14.1%); £3,249,014.97 -> £2,789,429.48 (14.1%); £3,249,014.97 -> £2,789,429.49 (14.1%); £3,249,014.97 -> £2,789,429.49 (14.1%); £3,249,014.97 -> £2,789,429.50 (14.1%); £3,249,014.98 -> £2,789,429.51 (14.1%); £3,249,014.98 -> £2,789,429.53 (14.1%); £3,249,014.99 -> £2,789,429.54 (14.1%); £3,249,015.00 -> £2,789,429.57 (14.1%); £3,249,015.01 -> £2,789,429.59 (14.1%); £3,249,015.02 -> £2,789,429.61 (14.1%); £3,249,015.04 -> £2,789,429.64 (14.1%); £3,249,015.05 -> £2,789,429.67 (14.1%); £3,249,015.06 -> £2,789,429.69 (14.1%); £3,249,015.07 -> £2,789,429.72 (14.1%); £3,249,015.08 -> £2,789,429.74 (14.1%); £3,249,015.08 -> £2,789,429.76 (14.1%); £3,249,015.09 -> £2,789,429.78 (14.1%); £3,249,015.09 -> £2,789,429.80 (14.1%); £3,249,015.09 -> £2,789,429.82 (14.1%); £3,249,015.10 -> £2,789,429.84 (14.1%); £3,249,015.10 -> £2,789,429.86 (14.1%); £3,249,015.11 -> £2,789,429.88 (14.1%); £3,249,015.11 -> £2,789,429.90 (14.1%); £3,249,015.12 -> £2,789,429.91 (14.1%); £3,249,015.12 -> £2,789,429.93 (14.1%); £3,249,015.13 -> £2,789,429.95 (14.1%); £3,249,015.13 -> £2,789,429.99 (14.1%); £3,249,015.14 -> £2,789,430.03 (14.1%); £3,249,015.16 -> £2,789,430.07 (14.1%); £3,249,015.17 -> £2,789,430.12 (14.1%); £3,249,015.18 -> £2,789,430.15 (14.1%); £3,249,015.19 -> £2,789,430.19 (14.1%); £3,249,015.20 -> £2,789,430.23 (14.1%); £3,249,015.21 -> £2,789,430.27 (14.1%); £3,249,015.22 -> £2,789,430.31 (14.1%); £3,249,015.23 -> £2,789,430.35 (14.1%); £3,249,015.24 -> £2,789,430.40 (14.1%); £3,249,015.26 -> £2,789,430.42 (14.1%); £3,249,015.26 -> £2,789,430.44 (14.1%); £3,249,015.27 -> £2,789,430.46 (14.1%); £3,249,015.27 -> £2,789,430.48 (14.1%); £3,249,015.28 -> £2,789,430.63 (14.1%); £3,249,015.28 -> £2,789,430.77 (14.1%); £3,249,015.29 -> £2,789,430.90 (14.1%); £3,249,015.29 -> £2,789,431.04 (14.1%); £3,249,015.29 -> £2,789,431.18 (14.1%); £3,249,015.29 -> £2,789,431.32 (14.1%); £3,249,015.30 -> £2,789,431.46 (14.1%); £3,249,015.30 -> £2,789,431.60 (14.1%); £3,249,015.30 -> £2,789,431.61 (14.1%); £3,249,015.30 -> £2,789,431.61 (14.1%); £3,249,015.31 -> £2,789,431.62 (14.1%); £3,249,015.31 -> £2,789,431.63 (14.1%); £3,249,015.31 -> £2,789,431.65 (14.1%); £3,249,015.32 -> £2,789,431.67 (14.1%); £3,249,015.33 -> £2,789,431.68 (14.1%); £3,249,015.35 -> £2,789,431.71 (14.1%); £3,249,015.36 -> £2,789,431.73 (14.1%); £3,249,015.37 -> £2,789,431.76 (14.1%); £3,249,015.39 -> £2,789,431.79 (14.1%); £3,249,015.40 -> £2,789,431.82 (14.1%); £3,249,015.41 -> £2,789,431.85 (14.1%); £3,249,015.42 -> £2,789,431.87 (14.1%); £3,249,015.43 -> £2,789,431.90 (14.1%); £3,249,015.44 -> £2,789,431.93 (14.1%); £3,249,015.45 -> £2,789,431.96 (14.1%); £3,249,015.45 -> £2,789,431.99 (14.1%); £3,249,015.46 -> £2,789,432.02 (14.1%); £3,249,015.47 -> £2,789,432.05 (14.1%); £3,249,015.48 -> £2,789,432.07 (14.1%); £3,249,015.49 -> £2,789,432.09 (14.1%); £3,249,015.49 -> £2,789,432.11 (14.1%); £3,249,015.49 -> £2,789,432.13 (14.1%); £3,249,015.50 -> £2,789,432.15 (14.1%); £3,249,015.50 -> £2,789,432.19 (14.1%); £3,249,015.51 -> £2,789,432.23 (14.1%); £3,249,015.52 -> £2,789,432.27 (14.1%); £3,249,015.53 -> £2,789,432.31 (14.1%); £3,249,015.54 -> £2,789,432.36 (14.1%); £3,249,015.55 -> £2,789,432.40 (14.1%); £3,249,015.56 -> £2,789,432.44 (14.1%); £3,249,015.57 -> £2,789,432.48 (14.1%); £3,249,015.58 -> £2,789,432.52 (14.1%); £3,249,015.59 -> £2,789,432.56 (14.1%); £3,249,015.60 -> £2,789,432.61 (14.1%); £3,249,015.61 -> £2,789,432.64 (14.1%); £3,249,015.62 -> £2,789,432.66 (14.1%); £3,249,015.62 -> £2,789,432.68 (14.1%); £3,249,015.63 -> £2,789,432.70 (14.1%); £3,249,015.63 -> £2,789,432.84 (14.1%); £3,249,015.64 -> £2,789,432.98 (14.1%); £3,249,015.64 -> £2,789,433.11 (14.1%); £3,249,015.64 -> £2,789,433.24 (14.1%); £3,249,015.64 -> £2,789,433.37 (14.1%); £3,249,015.64 -> £2,789,433.50 (14.1%); £3,249,015.64 -> £2,789,433.63 (14.1%); £3,249,015.65 -> £2,789,433.76 (14.1%); £3,249,015.65 -> £2,789,433.77 (14.1%); £3,249,015.65 -> £2,789,433.78 (14.1%); £3,249,015.65 -> £2,789,433.79 (14.1%); £3,249,015.65 -> £2,789,433.80 (14.1%); £3,249,015.65 -> £2,789,433.81 (14.1%); £3,249,015.67 -> £2,789,433.83 (14.1%); £3,249,015.68 -> £2,789,433.86 (14.1%); £3,249,015.88 -> £2,789,433.88 (14.1%); £3,249,016.08 -> £2,789,433.91 (14.1%); £3,249,016.29 -> £2,789,433.93 (14.1%); £3,249,016.49 -> £2,789,433.96 (14.1%); £3,249,016.70 -> £2,789,433.98 (14.1%); £3,249,016.90 -> £2,789,434.00 (14.1%); £3,249,016.95 -> £2,789,434.02 (14.1%); £3,249,017.01 -> £2,789,434.04 (14.1%); £3,249,017.01 -> £2,789,434.06 (14.1%); £3,249,017.01 -> £2,789,434.08 (14.1%); £3,249,017.02 -> £2,789,434.10 (14.1%); £3,249,017.02 -> £2,789,434.11 (14.1%); £3,249,017.02 -> £2,789,434.13 (14.1%); £3,249,017.03 -> £2,789,434.15 (14.1%); £3,249,017.03 -> £2,789,434.17 (14.1%); £3,249,017.03 -> £2,789,434.18 (14.1%); £3,249,017.04 -> £2,789,434.20 (14.1%); £3,249,017.04 -> £2,789,434.22 (14.1%); £3,249,017.10 -> £2,789,434.26 (14.1%); £3,249,017.27 -> £2,789,434.31 (14.1%); £3,249,017.45 -> £2,789,434.35 (14.1%); £3,249,017.63 -> £2,789,434.39 (14.1%); £3,249,017.81 -> £2,789,434.43 (14.1%); £3,249,017.99 -> £2,789,434.47 (14.1%); £3,249,018.16 -> £2,789,434.51 (14.1%); £3,249,018.33 -> £2,789,434.55 (14.1%); £3,249,018.34 -> £2,789,434.59 (14.1%); £3,249,018.35 -> £2,789,434.64 (14.1%); £3,249,018.37 -> £2,789,434.68 (14.1%); £3,249,018.38 -> £2,789,434.71 (14.1%); £3,249,018.39 -> £2,789,434.73 (14.1%); £3,249,018.39 -> £2,789,434.75 (14.1%); £3,249,018.39 -> £2,789,434.77 (14.1%); £3,249,018.40 -> £2,789,434.91 (14.1%); £3,249,018.40 -> £2,789,435.04 (14.1%); £3,249,018.40 -> £2,789,435.17 (14.1%); £3,249,018.40 -> £2,789,435.31 (14.1%); £3,249,018.41 -> £2,789,435.44 (14.1%); £3,249,018.41 -> £2,789,435.57 (14.1%); £3,249,018.41 -> £2,789,435.70 (14.1%); £3,249,018.41 -> £2,789,435.83 (14.1%); £3,249,018.41 -> £2,789,435.84 (14.1%); £3,249,018.41 -> £2,789,435.85 (14.1%); £3,249,018.42 -> £2,789,435.86 (14.1%); £3,249,018.42 -> £2,789,435.87 (14.1%); £3,249,018.42 -> £2,789,435.89 (14.1%); £3,249,018.43 -> £2,789,435.91 (14.1%); £3,249,018.44 -> £2,789,435.93 (14.1%); £3,249,018.57 -> £2,789,435.96 (14.1%); £3,249,018.71 -> £2,789,435.98 (14.1%); £3,249,018.85 -> £2,789,436.01 (14.1%); £3,249,018.99 -> £2,789,436.03 (14.1%); £3,249,019.13 -> £2,789,436.06 (14.1%); £3,249,019.27 -> £2,789,436.08 (14.1%); £3,249,019.32 -> £2,789,436.10 (14.1%); £3,249,019.37 -> £2,789,436.12 (14.1%); £3,249,019.38 -> £2,789,436.14 (14.1%); £3,249,019.38 -> £2,789,436.15 (14.1%); £3,249,019.38 -> £2,789,436.17 (14.1%); £3,249,019.39 -> £2,789,436.19 (14.1%); £3,249,019.39 -> £2,789,436.21 (14.1%); £3,249,019.39 -> £2,789,436.23 (14.1%); £3,249,019.40 -> £2,789,436.24 (14.1%); £3,249,019.40 -> £2,789,436.26 (14.1%); £3,249,019.41 -> £2,789,436.28 (14.1%); £3,249,019.41 -> £2,789,436.30 (14.1%); £3,249,019.47 -> £2,789,436.34 (14.1%); £3,249,019.60 -> £2,789,436.39 (14.1%); £3,249,019.73 -> £2,789,436.43 (14.1%); £3,249,019.86 -> £2,789,436.47 (14.1%); £3,249,019.99 -> £2,789,436.51 (14.1%); £3,249,020.11 -> £2,789,436.55 (14.1%); £3,249,020.24 -> £2,789,436.59 (14.1%); £3,249,020.36 -> £2,789,436.63 (14.1%); £3,249,020.37 -> £2,789,436.67 (14.1%); £3,249,020.38 -> £2,789,436.72 (14.1%); £3,249,020.39 -> £2,789,436.77 (14.1%); £3,249,020.40 -> £2,789,436.79 (14.1%); £3,249,020.40 -> £2,789,436.82 (14.1%); £3,249,020.41 -> £2,789,436.84 (14.1%); £3,249,020.41 -> £2,789,436.85 (14.1%); £3,249,020.42 -> £2,789,436.99 (14.1%); £3,249,020.42 -> £2,789,437.12 (14.1%); £3,249,020.42 -> £2,789,437.25 (14.1%); £3,249,020.42 -> £2,789,437.38 (14.1%); £3,249,020.42 -> £2,789,437.52 (14.1%); £3,249,020.43 -> £2,789,437.65 (14.1%); £3,249,020.43 -> £2,789,437.78 (14.1%); £3,249,020.43 -> £2,789,437.91 (14.1%); £3,249,020.43 -> £2,789,437.92 (14.1%); £3,249,020.43 -> £2,789,437.93 (14.1%); £3,249,020.43 -> £2,789,437.94 (14.1%); £3,249,020.43 -> £2,789,437.95 (14.1%); £3,249,020.44 -> £2,789,437.96 (14.1%); £3,249,020.44 -> £2,789,437.98 (14.1%); £3,249,020.44 -> £2,789,438.01 (14.1%); £3,249,020.50 -> £2,789,438.03 (14.1%); £3,249,020.56 -> £2,789,438.06 (14.1%); £3,249,020.62 -> £2,789,438.08 (14.1%); £3,249,020.68 -> £2,789,438.11 (14.1%); £3,249,020.74 -> £2,789,438.14 (14.1%); £3,249,020.80 -> £2,789,438.16 (14.1%); £3,249,020.86 -> £2,789,438.17 (14.1%); £3,249,020.91 -> £2,789,438.19 (14.1%); £3,249,020.92 -> £2,789,438.21 (14.1%); £3,249,020.92 -> £2,789,438.23 (14.1%); £3,249,020.92 -> £2,789,438.25 (14.1%); £3,249,020.93 -> £2,789,438.27 (14.1%); £3,249,020.93 -> £2,789,438.29 (14.1%); £3,249,020.94 -> £2,789,438.31 (14.1%); £3,249,020.94 -> £2,789,438.32 (14.1%); £3,249,020.94 -> £2,789,438.34 (14.1%); £3,249,020.95 -> £2,789,438.36 (14.1%); £3,249,020.95 -> £2,789,438.38 (14.1%); £3,249,021.01 -> £2,789,438.42 (14.1%); £3,249,021.08 -> £2,789,438.46 (14.1%); £3,249,021.15 -> £2,789,438.51 (14.1%); £3,249,021.23 -> £2,789,438.55 (14.1%); £3,249,021.30 -> £2,789,438.59 (14.1%); £3,249,021.37 -> £2,789,438.63 (14.1%); £3,249,021.44 -> £2,789,438.67 (14.1%); £3,249,021.50 -> £2,789,438.71 (14.1%); £3,249,021.51 -> £2,789,438.75 (14.1%); £3,249,021.52 -> £2,789,438.80 (14.1%); £3,249,021.52 -> £2,789,438.85 (14.1%); £3,249,021.53 -> £2,789,438.87 (14.1%); £3,249,021.53 -> £2,789,438.90 (14.1%); £3,249,021.54 -> £2,789,438.92 (14.1%); £3,249,021.54 -> £2,789,438.93 (14.1%); £3,249,021.54 -> £2,789,439.07 (14.1%); £3,249,021.54 -> £2,789,439.20 (14.1%); £3,249,021.55 -> £2,789,439.33 (14.1%); £3,249,021.55 -> £2,789,439.47 (14.1%); £3,249,021.55 -> £2,789,439.60 (14.1%); £3,249,021.55 -> £2,789,439.73 (14.1%); £3,249,021.55 -> £2,789,439.87 (14.1%); £3,249,021.56 -> £2,789,440.00 (14.1%); £3,249,021.56 -> £2,789,440.01 (14.1%); £3,249,021.56 -> £2,789,440.02 (14.1%); £3,249,021.56 -> £2,789,440.03 (14.1%); £3,249,021.56 -> £2,789,440.04 (14.1%); £3,249,021.56 -> £2,789,440.05 (14.1%); £3,249,021.56 -> £2,789,440.07 (14.1%); £3,249,021.57 -> £2,789,440.09 (14.1%); £3,249,021.61 -> £2,789,440.12 (14.1%); £3,249,021.66 -> £2,789,440.14 (14.1%); £3,249,021.71 -> £2,789,440.17 (14.1%); £3,249,021.77 -> £2,789,440.20 (14.1%); £3,249,021.82 -> £2,789,440.22 (14.1%); £3,249,021.87 -> £2,789,440.24 (14.1%); £3,249,021.92 -> £2,789,440.26 (14.1%); £3,249,021.97 -> £2,789,440.28 (14.1%); £3,249,021.98 -> £2,789,440.30 (14.1%); £3,249,021.98 -> £2,789,440.32 (14.1%); £3,249,021.99 -> £2,789,440.34 (14.1%); £3,249,021.99 -> £2,789,440.36 (14.1%); £3,249,022.00 -> £2,789,440.37 (14.1%); £3,249,022.00 -> £2,789,440.39 (14.1%); £3,249,022.00 -> £2,789,440.41 (14.1%); £3,249,022.01 -> £2,789,440.42 (14.1%); £3,249,022.01 -> £2,789,440.44 (14.1%); £3,249,022.01 -> £2,789,440.46 (14.1%); £3,249,022.07 -> £2,789,440.50 (14.1%); £3,249,022.13 -> £2,789,440.55 (14.1%); £3,249,022.20 -> £2,789,440.59 (14.1%); £3,249,022.27 -> £2,789,440.63 (14.1%); £3,249,022.33 -> £2,789,440.67 (14.1%); £3,249,022.39 -> £2,789,440.71 (14.1%); £3,249,022.46 -> £2,789,440.75 (14.1%); £3,249,022.51 -> £2,789,440.79 (14.1%); £3,249,022.52 -> £2,789,440.84 (14.1%); £3,249,022.53 -> £2,789,440.88 (14.1%); £3,249,022.53 -> £2,789,440.93 (14.1%); £3,249,022.53 -> £2,789,440.95 (14.1%); £3,249,022.54 -> £2,789,440.98 (14.1%); £3,249,022.55 -> £2,789,441.00 (14.1%); £3,249,022.55 -> £2,789,441.02 (14.1%); £3,249,022.55 -> £2,789,441.15 (14.1%); £3,249,022.56 -> £2,789,441.29 (14.1%); £3,249,022.56 -> £2,789,441.42 (14.1%); £3,249,022.56 -> £2,789,441.55 (14.1%); £3,249,022.56 -> £2,789,441.68 (14.1%); £3,249,022.56 -> £2,789,441.81 (14.1%); £3,249,022.56 -> £2,789,441.95 (14.1%); £3,249,022.57 -> £2,789,442.08 (14.1%); £3,249,022.57 -> £2,789,442.09 (14.1%); £3,249,022.57 -> £2,789,442.10 (14.1%); £3,249,022.57 -> £2,789,442.11 (14.1%); £3,249,022.57 -> £2,789,442.12 (14.1%); £3,249,022.57 -> £2,789,442.13 (14.1%); £3,249,022.58 -> £2,789,442.15 (14.1%); £3,249,022.58 -> £2,789,442.17 (14.1%); £3,249,022.62 -> £2,789,442.20 (14.1%); £3,249,022.67 -> £2,789,442.23 (14.1%); £3,249,022.73 -> £2,789,442.25 (14.1%); £3,249,022.78 -> £2,789,442.28 (14.1%); £3,249,022.83 -> £2,789,442.30 (14.1%); £3,249,022.88 -> £2,789,442.32 (14.1%); £3,249,022.93 -> £2,789,442.34 (14.1%); £3,249,022.98 -> £2,789,442.36 (14.1%); £3,249,022.99 -> £2,789,442.37 (14.1%); £3,249,022.99 -> £2,789,442.39 (14.1%); £3,249,022.99 -> £2,789,442.41 (14.1%); £3,249,023.00 -> £2,789,442.43 (14.1%); £3,249,023.00 -> £2,789,442.45 (14.1%); £3,249,023.01 -> £2,789,442.47 (14.1%); £3,249,023.01 -> £2,789,442.49 (14.1%); £3,249,023.02 -> £2,789,442.50 (14.1%); £3,249,023.02 -> £2,789,442.52 (14.1%); £3,249,023.02 -> £2,789,442.54 (14.1%); £3,249,023.08 -> £2,789,442.59 (14.1%); £3,249,023.15 -> £2,789,442.63 (14.1%); £3,249,023.22 -> £2,789,442.67 (14.1%); £3,249,023.28 -> £2,789,442.72 (14.1%); £3,249,023.35 -> £2,789,442.76 (14.1%); £3,249,023.41 -> £2,789,442.80 (14.1%); £3,249,023.47 -> £2,789,442.84 (14.1%); £3,249,023.53 -> £2,789,442.87 (14.1%); £3,249,023.53 -> £2,789,442.92 (14.1%); £3,249,023.54 -> £2,789,442.96 (14.1%); £3,249,023.54 -> £2,789,443.01 (14.1%); £3,249,023.55 -> £2,789,443.04 (14.1%); £3,249,023.55 -> £2,789,443.06 (14.1%); £3,249,023.56 -> £2,789,443.08 (14.1%); £3,249,023.56 -> £2,789,443.10 (14.1%); £3,249,023.57 -> £2,789,443.24 (14.1%); £3,249,023.57 -> £2,789,443.38 (14.1%); £3,249,023.57 -> £2,789,443.51 (14.1%); £3,249,023.58 -> £2,789,443.64 (14.1%); £3,249,023.58 -> £2,789,443.77 (14.1%); £3,249,023.58 -> £2,789,443.90 (14.1%); £3,249,023.58 -> £2,789,444.04 (14.1%); £3,249,023.58 -> £2,789,444.17 (14.1%); £3,249,023.58 -> £2,789,444.17 (14.1%); £3,249,023.58 -> £2,789,444.18 (14.1%); £3,249,023.59 -> £2,789,444.19 (14.1%); £3,249,023.59 -> £2,789,444.20 (14.1%); £3,249,023.59 -> £2,789,444.22 (14.1%); £3,249,023.59 -> £2,789,444.23 (14.1%); £3,249,023.60 -> £2,789,444.26 (14.1%); £3,249,023.61 -> £2,789,444.28 (14.1%); £3,249,023.61 -> £2,789,444.30 (14.1%); £3,249,023.62 -> £2,789,444.33 (14.1%); £3,249,023.63 -> £2,789,444.36 (14.1%); £3,249,023.64 -> £2,789,444.39 (14.1%); £3,249,023.64 -> £2,789,444.41 (14.1%); £3,249,023.65 -> £2,789,444.43 (14.1%); £3,249,023.65 -> £2,789,444.45 (14.1%); £3,249,023.65 -> £2,789,444.47 (14.1%); £3,249,023.66 -> £2,789,444.49 (14.1%); £3,249,023.67 -> £2,789,444.51 (14.1%); £3,249,023.67 -> £2,789,444.53 (14.1%); £3,249,023.68 -> £2,789,444.55 (14.1%); £3,249,023.68 -> £2,789,444.57 (14.1%); £3,249,023.69 -> £2,789,444.59 (14.1%); £3,249,023.69 -> £2,789,444.61 (14.1%); £3,249,023.69 -> £2,789,444.63 (14.1%); £3,249,023.70 -> £2,789,444.65 (14.1%); £3,249,023.70 -> £2,789,444.69 (14.1%); £3,249,023.71 -> £2,789,444.73 (14.1%); £3,249,023.72 -> £2,789,444.77 (14.1%); £3,249,023.73 -> £2,789,444.81 (14.1%); £3,249,023.74 -> £2,789,444.85 (14.1%); £3,249,023.74 -> £2,789,444.89 (14.1%); £3,249,023.75 -> £2,789,444.93 (14.1%); £3,249,023.76 -> £2,789,444.97 (14.1%); £3,249,023.77 -> £2,789,445.01 (14.1%); £3,249,023.77 -> £2,789,445.05 (14.1%); £3,249,023.78 -> £2,789,445.10 (14.1%); £3,249,023.79 -> £2,789,445.12 (14.1%); £3,249,023.79 -> £2,789,445.14 (14.1%); £3,249,023.80 -> £2,789,445.16 (14.1%); £3,249,023.80 -> £2,789,445.18 (14.1%); £3,249,023.81 -> £2,789,445.32 (14.1%); £3,249,023.81 -> £2,789,445.46 (14.1%); £3,249,023.81 -> £2,789,445.59 (14.1%); £3,249,023.81 -> £2,789,445.73 (14.1%); £3,249,023.82 -> £2,789,445.86 (14.1%); £3,249,023.82 -> £2,789,445.99 (14.1%); £3,249,023.82 -> £2,789,446.12 (14.1%); £3,249,023.82 -> £2,789,446.25 (14.1%); £3,249,023.82 -> £2,789,446.26 (14.1%); £3,249,023.82 -> £2,789,446.27 (14.1%); £3,249,023.83 -> £2,789,446.28 (14.1%); £3,249,023.83 -> £2,789,446.29 (14.1%); £3,249,023.83 -> £2,789,446.30 (14.1%); £3,249,023.83 -> £2,789,446.32 (14.1%); £3,249,023.84 -> £2,789,446.34 (14.1%); £3,249,023.85 -> £2,789,446.36 (14.1%); £3,249,023.86 -> £2,789,446.38 (14.1%); £3,249,023.87 -> £2,789,446.41 (14.1%); £3,249,023.87 -> £2,789,446.44 (14.1%); £3,249,023.88 -> £2,789,446.47 (14.1%); £3,249,023.90 -> £2,789,446.50 (14.1%); £3,249,023.90 -> £2,789,446.52 (14.1%); £3,249,023.91 -> £2,789,446.55 (14.1%); £3,249,023.92 -> £2,789,446.58 (14.1%); £3,249,023.93 -> £2,789,446.61 (14.1%); £3,249,023.93 -> £2,789,446.64 (14.1%); £3,249,023.94 -> £2,789,446.67 (14.1%); £3,249,023.95 -> £2,789,446.69 (14.1%); £3,249,023.95 -> £2,789,446.72 (14.1%); £3,249,023.96 -> £2,789,446.74 (14.1%); £3,249,023.97 -> £2,789,446.76 (14.1%); £3,249,023.97 -> £2,789,446.78 (14.1%); £3,249,023.97 -> £2,789,446.80 (14.1%); £3,249,023.98 -> £2,789,446.84 (14.1%); £3,249,023.98 -> £2,789,446.88 (14.1%); £3,249,023.99 -> £2,789,446.92 (14.1%); £3,249,024.00 -> £2,789,446.96 (14.1%); £3,249,024.00 -> £2,789,447.00 (14.1%); £3,249,024.01 -> £2,789,447.04 (14.1%); £3,249,024.02 -> £2,789,447.08 (14.1%); £3,249,024.03 -> £2,789,447.12 (14.1%); £3,249,024.04 -> £2,789,447.16 (14.1%); £3,249,024.04 -> £2,789,447.21 (14.1%); £3,249,024.05 -> £2,789,447.25 (14.1%); £3,249,024.06 -> £2,789,447.28 (14.1%); £3,249,024.06 -> £2,789,447.30 (14.1%); £3,249,024.07 -> £2,789,447.32 (14.1%); £3,249,024.07 -> £2,789,447.34 (14.1%); £3,249,024.08 -> £2,789,447.48 (14.1%); £3,249,024.08 -> £2,789,447.62 (14.1%); £3,249,024.08 -> £2,789,447.76 (14.1%); £3,249,024.09 -> £2,789,447.89 (14.1%); £3,249,024.09 -> £2,789,448.03 (14.1%); £3,249,024.09 -> £2,789,448.16 (14.1%); £3,249,024.09 -> £2,789,448.29 (14.1%); £3,249,024.09 -> £2,789,448.42 (14.1%); £3,249,024.09 -> £2,789,448.43 (14.1%); £3,249,024.10 -> £2,789,448.44 (14.1%); £3,249,024.10 -> £2,789,448.45 (14.1%); £3,249,024.10 -> £2,789,448.46 (14.1%); £3,249,024.10 -> £2,789,448.48 (14.1%); £3,249,024.11 -> £2,789,448.50 (14.1%); £3,249,024.11 -> £2,789,448.52 (14.1%); £3,249,024.20 -> £2,789,448.55 (14.1%); £3,249,024.28 -> £2,789,448.57 (14.1%); £3,249,024.37 -> £2,789,448.60 (14.1%); £3,249,024.45 -> £2,789,448.62 (14.1%); £3,249,024.54 -> £2,789,448.65 (14.1%); £3,249,024.62 -> £2,789,448.67 (14.1%); £3,249,024.67 -> £2,789,448.69 (14.1%); £3,249,024.73 -> £2,789,448.71 (14.1%); £3,249,024.73 -> £2,789,448.72 (14.1%); £3,249,024.73 -> £2,789,448.74 (14.1%); £3,249,024.74 -> £2,789,448.76 (14.1%); £3,249,024.74 -> £2,789,448.78 (14.1%); £3,249,024.74 -> £2,789,448.80 (14.1%); £3,249,024.75 -> £2,789,448.81 (14.1%); £3,249,024.75 -> £2,789,448.83 (14.1%); £3,249,024.75 -> £2,789,448.85 (14.1%); £3,249,024.76 -> £2,789,448.87 (14.1%); £3,249,024.76 -> £2,789,448.89 (14.1%); £3,249,024.82 -> £2,789,448.93 (14.1%); £3,249,024.91 -> £2,789,448.98 (14.1%); £3,249,025.01 -> £2,789,449.02 (14.1%); £3,249,025.10 -> £2,789,449.06 (14.1%); £3,249,025.19 -> £2,789,449.11 (14.1%); £3,249,025.28 -> £2,789,449.15 (14.1%); £3,249,025.36 -> £2,789,449.19 (14.1%); £3,249,025.45 -> £2,789,449.23 (14.1%); £3,249,025.46 -> £2,789,449.27 (14.1%); £3,249,025.46 -> £2,789,449.32 (14.1%); £3,249,025.47 -> £2,789,449.36 (14.1%); £3,249,025.48 -> £2,789,449.39 (14.1%); £3,249,025.48 -> £2,789,449.41 (14.1%); £3,249,025.49 -> £2,789,449.44 (14.1%); £3,249,025.50 -> £2,789,449.45 (14.1%); £3,249,025.50 -> £2,789,449.59 (14.1%); £3,249,025.50 -> £2,789,449.73 (14.1%); £3,249,025.50 -> £2,789,449.86 (14.1%); £3,249,025.51 -> £2,789,449.99 (14.1%); £3,249,025.51 -> £2,789,450.13 (14.1%); £3,249,025.51 -> £2,789,450.26 (14.1%); £3,249,025.51 -> £2,789,450.39 (14.1%); £3,249,025.51 -> £2,789,450.53 (14.1%); £3,249,025.52 -> £2,789,450.54 (14.1%); £3,249,025.52 -> £2,789,450.55 (14.1%); £3,249,025.52 -> £2,789,450.56 (14.1%); £3,249,025.52 -> £2,789,450.57 (14.1%); £3,249,025.52 -> £2,789,450.58 (14.1%); £3,249,025.53 -> £2,789,450.60 (14.1%); £3,249,025.54 -> £2,789,450.62 (14.1%); £3,249,025.64 -> £2,789,450.65 (14.1%); £3,249,025.74 -> £2,789,450.68 (14.1%); £3,249,025.85 -> £2,789,450.70 (14.1%); £3,249,025.95 -> £2,789,450.73 (14.1%); £3,249,026.06 -> £2,789,450.76 (14.1%); £3,249,026.17 -> £2,789,450.78 (14.1%); £3,249,026.22 -> £2,789,450.80 (14.1%); £3,249,026.28 -> £2,789,450.82 (14.1%); £3,249,026.28 -> £2,789,450.83 (14.1%); £3,249,026.29 -> £2,789,450.86 (14.1%); £3,249,026.29 -> £2,789,450.87 (14.1%); £3,249,026.29 -> £2,789,450.89 (14.1%); £3,249,026.30 -> £2,789,450.91 (14.1%); £3,249,026.30 -> £2,789,450.93 (14.1%); £3,249,026.31 -> £2,789,450.95 (14.1%); £3,249,026.31 -> £2,789,450.96 (14.1%); £3,249,026.32 -> £2,789,450.98 (14.1%); £3,249,026.32 -> £2,789,451.00 (14.1%); £3,249,026.38 -> £2,789,451.04 (14.1%); £3,249,026.48 -> £2,789,451.09 (14.1%); £3,249,026.59 -> £2,789,451.13 (14.1%); £3,249,026.69 -> £2,789,451.17 (14.1%); £3,249,026.79 -> £2,789,451.21 (14.1%); £3,249,026.89 -> £2,789,451.25 (14.1%); £3,249,026.99 -> £2,789,451.29 (14.1%); £3,249,027.09 -> £2,789,451.33 (14.1%); £3,249,027.09 -> £2,789,451.37 (14.1%); £3,249,027.10 -> £2,789,451.42 (14.1%); £3,249,027.11 -> £2,789,451.46 (14.1%); £3,249,027.12 -> £2,789,451.49 (14.1%); £3,249,027.13 -> £2,789,451.52 (14.1%); £3,249,027.13 -> £2,789,451.54 (14.1%); £3,249,027.14 -> £2,789,451.55 (14.1%); £3,249,027.14 -> £2,789,451.69 (14.1%); £3,249,027.14 -> £2,789,451.83 (14.1%); £3,249,027.15 -> £2,789,451.96 (14.1%); £3,249,027.15 -> £2,789,452.09 (14.1%); £3,249,027.15 -> £2,789,452.23 (14.1%); £3,249,027.15 -> £2,789,452.36 (14.1%); £3,249,027.15 -> £2,789,452.49 (14.1%); £3,249,027.15 -> £2,789,452.63 (14.1%); £3,249,027.16 -> £2,789,452.64 (14.1%); £3,249,027.16 -> £2,789,452.64 (14.1%); £3,249,027.16 -> £2,789,452.65 (14.1%); £3,249,027.16 -> £2,789,452.66 (14.1%); £3,249,027.16 -> £2,789,452.68 (14.1%); £3,249,027.17 -> £2,789,452.70 (14.1%); £3,249,027.17 -> £2,789,452.72 (14.1%); £3,249,027.25 -> £2,789,452.75 (14.1%); £3,249,027.34 -> £2,789,452.77 (14.1%); £3,249,027.43 -> £2,789,452.80 (14.1%); £3,249,027.51 -> £2,789,452.83 (14.1%); £3,249,027.60 -> £2,789,452.86 (14.1%); £3,249,027.69 -> £2,789,452.87 (14.1%); £3,249,027.74 -> £2,789,452.89 (14.1%); £3,249,027.80 -> £2,789,452.91 (14.1%); £3,249,027.80 -> £2,789,452.93 (14.1%); £3,249,027.80 -> £2,789,452.95 (14.1%); £3,249,027.81 -> £2,789,452.97 (14.1%); £3,249,027.81 -> £2,789,452.99 (14.1%); £3,249,027.82 -> £2,789,453.01 (14.1%); £3,249,027.82 -> £2,789,453.02 (14.1%); £3,249,027.82 -> £2,789,453.04 (14.1%); £3,249,027.83 -> £2,789,453.06 (14.1%); £3,249,027.83 -> £2,789,453.08 (14.1%); £3,249,027.83 -> £2,789,453.10 (14.1%); £3,249,027.89 -> £2,789,453.14 (14.1%); £3,249,027.98 -> £2,789,453.18 (14.1%); £3,249,028.07 -> £2,789,453.22 (14.1%); £3,249,028.16 -> £2,789,453.27 (14.1%); £3,249,028.25 -> £2,789,453.31 (14.1%); £3,249,028.34 -> £2,789,453.35 (14.1%); £3,249,028.42 -> £2,789,453.39 (14.1%); £3,249,028.51 -> £2,789,453.43 (14.1%); £3,249,028.52 -> £2,789,453.47 (14.1%); £3,249,028.52 -> £2,789,453.52 (14.1%); £3,249,028.53 -> £2,789,453.57 (14.1%); £3,249,028.54 -> £2,789,453.59 (14.1%); £3,249,028.55 -> £2,789,453.62 (14.1%); £3,249,028.55 -> £2,789,453.64 (14.1%); £3,249,028.56 -> £2,789,453.66 (14.1%); £3,249,028.56 -> £2,789,453.80 (14.1%); £3,249,028.56 -> £2,789,453.93 (14.1%); £3,249,028.57 -> £2,789,454.06 (14.1%); £3,249,028.57 -> £2,789,454.19 (14.1%); £3,249,028.57 -> £2,789,454.32 (14.1%); £3,249,028.57 -> £2,789,454.45 (14.1%); £3,249,028.57 -> £2,789,454.58 (14.1%); £3,249,028.57 -> £2,789,454.71 (14.1%); £3,249,028.57 -> £2,789,454.72 (14.1%); £3,249,028.58 -> £2,789,454.72 (14.1%); £3,249,028.58 -> £2,789,454.73 (14.1%); £3,249,028.58 -> £2,789,454.74 (14.1%); £3,249,028.58 -> £2,789,454.76 (14.1%); £3,249,028.58 -> £2,789,454.78 (14.1%); £3,249,028.59 -> £2,789,454.80 (14.1%); £3,249,028.67 -> £2,789,454.83 (14.1%); £3,249,028.75 -> £2,789,454.85 (14.1%); £3,249,028.83 -> £2,789,454.88 (14.1%); £3,249,028.91 -> £2,789,454.91 (14.1%); £3,249,028.99 -> £2,789,454.93 (14.1%); £3,249,029.07 -> £2,789,454.95 (14.1%); £3,249,029.12 -> £2,789,454.97 (14.1%); £3,249,029.18 -> £2,789,454.99 (14.1%); £3,249,029.18 -> £2,789,455.01 (14.1%); £3,249,029.18 -> £2,789,455.03 (14.1%); £3,249,029.19 -> £2,789,455.05 (14.1%); £3,249,029.19 -> £2,789,455.06 (14.1%); £3,249,029.19 -> £2,789,455.08 (14.1%); £3,249,029.20 -> £2,789,455.10 (14.1%); £3,249,029.20 -> £2,789,455.11 (14.1%); £3,249,029.20 -> £2,789,455.13 (14.1%); £3,249,029.20 -> £2,789,455.15 (14.1%); £3,249,029.21 -> £2,789,455.17 (14.1%); £3,249,029.27 -> £2,789,455.21 (14.1%); £3,249,029.35 -> £2,789,455.26 (14.1%); £3,249,029.44 -> £2,789,455.30 (14.1%); £3,249,029.53 -> £2,789,455.34 (14.1%); £3,249,029.61 -> £2,789,455.38 (14.1%); £3,249,029.70 -> £2,789,455.42 (14.1%); £3,249,029.78 -> £2,789,455.46 (14.1%); £3,249,029.86 -> £2,789,455.50 (14.1%); £3,249,029.87 -> £2,789,455.54 (14.1%); £3,249,029.87 -> £2,789,455.59 (14.1%); £3,249,029.88 -> £2,789,455.64 (14.1%); £3,249,029.89 -> £2,789,455.66 (14.1%); £3,249,029.89 -> £2,789,455.69 (14.1%); £3,249,029.90 -> £2,789,455.71 (14.1%); £3,249,029.90 -> £2,789,455.73 (14.1%); £3,249,029.91 -> £2,789,455.86 (14.1%); £3,249,029.91 -> £2,789,456.00 (14.1%); £3,249,029.91 -> £2,789,456.13 (14.1%); £3,249,029.91 -> £2,789,456.27 (14.1%); £3,249,029.92 -> £2,789,456.40 (14.1%); £3,249,029.92 -> £2,789,456.53 (14.1%); £3,249,029.92 -> £2,789,456.66 (14.1%); £3,249,029.92 -> £2,789,456.80 (14.1%); £3,249,029.92 -> £2,789,456.81 (14.1%); £3,249,029.92 -> £2,789,456.82 (14.1%); £3,249,029.93 -> £2,789,456.82 (14.1%); £3,249,029.93 -> £2,789,456.83 (14.1%); £3,249,029.93 -> £2,789,456.85 (14.1%); £3,249,029.94 -> £2,789,456.87 (14.1%); £3,249,029.95 -> £2,789,456.89 (14.1%); £3,249,030.08 -> £2,789,456.92 (14.1%); £3,249,030.22 -> £2,789,456.94 (14.1%); £3,249,030.36 -> £2,789,456.97 (14.1%); £3,249,030.50 -> £2,789,457.00 (14.1%); £3,249,030.64 -> £2,789,457.02 (14.1%); £3,249,030.78 -> £2,789,457.04 (14.1%); £3,249,030.83 -> £2,789,457.06 (14.1%); £3,249,030.89 -> £2,789,457.08 (14.1%); £3,249,030.89 -> £2,789,457.10 (14.1%); £3,249,030.90 -> £2,789,457.12 (14.1%); £3,249,030.90 -> £2,789,457.14 (14.1%); £3,249,030.91 -> £2,789,457.16 (14.1%); £3,249,030.91 -> £2,789,457.18 (14.1%); £3,249,030.91 -> £2,789,457.19 (14.1%); £3,249,030.92 -> £2,789,457.21 (14.1%); £3,249,030.92 -> £2,789,457.23 (14.1%); £3,249,030.92 -> £2,789,457.25 (14.1%); £3,249,030.93 -> £2,789,457.27 (14.1%); £3,249,030.99 -> £2,789,457.31 (14.1%); £3,249,031.11 -> £2,789,457.35 (14.1%); £3,249,031.24 -> £2,789,457.40 (14.1%); £3,249,031.37 -> £2,789,457.44 (14.1%); £3,249,031.50 -> £2,789,457.48 (14.1%); £3,249,031.63 -> £2,789,457.52 (14.1%); £3,249,031.75 -> £2,789,457.56 (14.1%); £3,249,031.87 -> £2,789,457.60 (14.1%); £3,249,031.88 -> £2,789,457.64 (14.1%); £3,249,031.89 -> £2,789,457.68 (14.1%); £3,249,031.90 -> £2,789,457.73 (14.1%); £3,249,031.91 -> £2,789,457.75 (14.1%); £3,249,031.91 -> £2,789,457.78 (14.1%); £3,249,031.92 -> £2,789,457.80 (14.1%); £3,249,031.92 -> £2,789,457.82 (14.1%); £3,249,031.93 -> £2,789,457.95 (14.1%); £3,249,031.93 -> £2,789,458.08 (14.1%); £3,249,031.93 -> £2,789,458.21 (14.1%); £3,249,031.93 -> £2,789,458.35 (14.1%); £3,249,031.93 -> £2,789,458.48 (14.1%); £3,249,031.94 -> £2,789,458.61 (14.1%); £3,249,031.94 -> £2,789,458.74 (14.1%); £3,249,031.94 -> £2,789,458.88 (14.1%); £3,249,031.94 -> £2,789,458.89 (14.1%); £3,249,031.94 -> £2,789,458.90 (14.1%); £3,249,031.94 -> £2,789,458.90 (14.1%); £3,249,031.95 -> £2,789,458.91 (14.1%); £3,249,031.95 -> £2,789,458.93 (14.1%); £3,249,031.96 -> £2,789,458.95 (14.1%); £3,249,031.98 -> £2,789,458.97 (14.1%); £3,249,032.00 -> £2,789,458.99 (14.1%); £3,249,032.01 -> £2,789,459.01 (14.1%); £3,249,032.03 -> £2,789,459.04 (14.1%); £3,249,032.05 -> £2,789,459.07 (14.1%); £3,249,032.07 -> £2,789,459.10 (14.1%); £3,249,032.09 -> £2,789,459.12 (14.1%); £3,249,032.09 -> £2,789,459.14 (14.1%); £3,249,032.10 -> £2,789,459.16 (14.1%); £3,249,032.10 -> £2,789,459.18 (14.1%); £3,249,032.11 -> £2,789,459.21 (14.1%); £3,249,032.11 -> £2,789,459.23 (14.1%); £3,249,032.12 -> £2,789,459.25 (14.1%); £3,249,032.12 -> £2,789,459.27 (14.1%); £3,249,032.13 -> £2,789,459.29 (14.1%); £3,249,032.13 -> £2,789,459.30 (14.1%); £3,249,032.13 -> £2,789,459.32 (14.1%); £3,249,032.14 -> £2,789,459.34 (14.1%); £3,249,032.14 -> £2,789,459.36 (14.1%); £3,249,032.15 -> £2,789,459.40 (14.1%); £3,249,032.16 -> £2,789,459.44 (14.1%); £3,249,032.18 -> £2,789,459.48 (14.1%); £3,249,032.19 -> £2,789,459.52 (14.1%); £3,249,032.21 -> £2,789,459.56 (14.1%); £3,249,032.22 -> £2,789,459.60 (14.1%); £3,249,032.24 -> £2,789,459.64 (14.1%); £3,249,032.25 -> £2,789,459.68 (14.1%); £3,249,032.26 -> £2,789,459.72 (14.1%); £3,249,032.28 -> £2,789,459.76 (14.1%); £3,249,032.29 -> £2,789,459.80 (14.1%); £3,249,032.30 -> £2,789,459.83 (14.1%); £3,249,032.31 -> £2,789,459.85 (14.1%); £3,249,032.31 -> £2,789,459.87 (14.1%); £3,249,032.32 -> £2,789,459.89 (14.1%); £3,249,032.32 -> £2,789,460.03 (14.1%); £3,249,032.32 -> £2,789,460.17 (14.1%); £3,249,032.33 -> £2,789,460.31 (14.1%); £3,249,032.33 -> £2,789,460.44 (14.1%); £3,249,032.33 -> £2,789,460.57 (14.1%); £3,249,032.33 -> £2,789,460.70 (14.1%); £3,249,032.33 -> £2,789,460.84 (14.1%); £3,249,032.34 -> £2,789,460.97 (14.1%); £3,249,032.34 -> £2,789,460.98 (14.1%); £3,249,032.34 -> £2,789,460.99 (14.1%); £3,249,032.34 -> £2,789,461.00 (14.1%); £3,249,032.34 -> £2,789,461.01 (14.1%); £3,249,032.34 -> £2,789,461.02 (14.1%); £3,249,032.36 -> £2,789,461.04 (14.1%); £3,249,032.37 -> £2,789,461.05 (14.1%); £3,249,032.38 -> £2,789,461.07 (14.1%); £3,249,032.39 -> £2,789,461.10 (14.1%); £3,249,032.41 -> £2,789,461.12 (14.1%); £3,249,032.42 -> £2,789,461.15 (14.1%); £3,249,032.43 -> £2,789,461.18 (14.1%); £3,249,032.45 -> £2,789,461.21 (14.1%); £3,249,032.45 -> £2,789,461.23 (14.1%); £3,249,032.46 -> £2,789,461.26 (14.1%); £3,249,032.46 -> £2,789,461.29 (14.1%); £3,249,032.47 -> £2,789,461.32 (14.1%); £3,249,032.47 -> £2,789,461.34 (14.1%); £3,249,032.48 -> £2,789,461.37 (14.1%); £3,249,032.48 -> £2,789,461.39 (14.1%); £3,249,032.49 -> £2,789,461.42 (14.1%); £3,249,032.49 -> £2,789,461.44 (14.1%); £3,249,032.50 -> £2,789,461.46 (14.1%); £3,249,032.50 -> £2,789,461.48 (14.1%); £3,249,032.51 -> £2,789,461.50 (14.1%); £3,249,032.51 -> £2,789,461.54 (14.1%); £3,249,032.52 -> £2,789,461.58 (14.1%); £3,249,032.53 -> £2,789,461.62 (14.1%); £3,249,032.55 -> £2,789,461.66 (14.1%); £3,249,032.56 -> £2,789,461.70 (14.1%); £3,249,032.57 -> £2,789,461.75 (14.1%); £3,249,032.59 -> £2,789,461.79 (14.1%); £3,249,032.60 -> £2,789,461.83 (14.1%); £3,249,032.61 -> £2,789,461.87 (14.1%); £3,249,032.62 -> £2,789,461.91 (14.1%); £3,249,032.63 -> £2,789,461.96 (14.1%); £3,249,032.65 -> £2,789,461.98 (14.1%); £3,249,032.65 -> £2,789,462.01 (14.1%); £3,249,032.66 -> £2,789,462.03 (14.1%); £3,249,032.66 -> £2,789,462.05 (14.1%); £3,249,032.67 -> £2,789,462.19 (14.1%); £3,249,032.67 -> £2,789,462.32 (14.1%); £3,249,032.67 -> £2,789,462.46 (14.1%); £3,249,032.68 -> £2,789,462.59 (14.1%); £3,249,032.68 -> £2,789,462.73 (14.1%); £3,249,032.68 -> £2,789,462.86 (14.1%); £3,249,032.68 -> £2,789,463.00 (14.1%); £3,249,032.68 -> £2,789,463.13 (14.1%); £3,249,032.68 -> £2,789,463.14 (14.1%); £3,249,032.69 -> £2,789,463.15 (14.1%); £3,249,032.69 -> £2,789,463.16 (14.1%); £3,249,032.69 -> £2,789,463.17 (14.1%); £3,249,032.69 -> £2,789,463.18 (14.1%); £3,249,032.70 -> £2,789,463.20 (14.1%); £3,249,032.71 -> £2,789,463.23 (14.1%); £3,249,032.88 -> £2,789,463.25 (14.1%); £3,249,033.05 -> £2,789,463.28 (14.1%); £3,249,033.22 -> £2,789,463.30 (14.1%); £3,249,033.40 -> £2,789,463.33 (14.1%); £3,249,033.57 -> £2,789,463.36 (14.1%); £3,249,033.75 -> £2,789,463.38 (14.1%); £3,249,033.80 -> £2,789,463.40 (14.1%); £3,249,033.85 -> £2,789,463.41 (14.1%); £3,249,033.86 -> £2,789,463.43 (14.1%); £3,249,033.86 -> £2,789,463.45 (14.1%); £3,249,033.87 -> £2,789,463.47 (14.1%); £3,249,033.87 -> £2,789,463.49 (14.1%); £3,249,033.88 -> £2,789,463.51 (14.1%); £3,249,033.88 -> £2,789,463.53 (14.1%); £3,249,033.88 -> £2,789,463.54 (14.1%); £3,249,033.89 -> £2,789,463.56 (14.1%); £3,249,033.89 -> £2,789,463.58 (14.1%); £3,249,033.90 -> £2,789,463.60 (14.1%); £3,249,033.96 -> £2,789,463.64 (14.1%); £3,249,034.11 -> £2,789,463.69 (14.1%); £3,249,034.27 -> £2,789,463.73 (14.1%); £3,249,034.43 -> £2,789,463.78 (14.1%); £3,249,034.58 -> £2,789,463.82 (14.1%); £3,249,034.74 -> £2,789,463.86 (14.1%); £3,249,034.89 -> £2,789,463.90 (14.1%); £3,249,035.03 -> £2,789,463.94 (14.1%); £3,249,035.04 -> £2,789,463.98 (14.1%); £3,249,035.06 -> £2,789,464.03 (14.1%); £3,249,035.07 -> £2,789,464.07 (14.1%); £3,249,035.08 -> £2,789,464.10 (14.1%); £3,249,035.09 -> £2,789,464.13 (14.1%); £3,249,035.10 -> £2,789,464.15 (14.1%); £3,249,035.10 -> £2,789,464.16 (14.1%); £3,249,035.10 -> £2,789,464.30 (14.1%); £3,249,035.11 -> £2,789,464.44 (14.1%); £3,249,035.11 -> £2,789,464.58 (14.1%); £3,249,035.11 -> £2,789,464.71 (14.1%); £3,249,035.11 -> £2,789,464.85 (14.1%); £3,249,035.12 -> £2,789,464.98 (14.1%); £3,249,035.12 -> £2,789,465.12 (14.1%); £3,249,035.12 -> £2,789,465.25 (14.1%); £3,249,035.12 -> £2,789,465.26 (14.1%); £3,249,035.12 -> £2,789,465.27 (14.1%); £3,249,035.13 -> £2,789,465.28 (14.1%); £3,249,035.13 -> £2,789,465.29 (14.1%); £3,249,035.13 -> £2,789,465.31 (14.1%); £3,249,035.14 -> £2,789,465.32 (14.1%); £3,249,035.15 -> £2,789,465.35 (14.1%); £3,249,035.32 -> £2,789,465.37 (14.1%); £3,249,035.48 -> £2,789,465.40 (14.1%); £3,249,035.65 -> £2,789,465.43 (14.1%); £3,249,035.82 -> £2,789,465.45 (14.1%); £3,249,035.99 -> £2,789,465.48 (14.1%); £3,249,036.16 -> £2,789,465.50 (14.1%); £3,249,036.22 -> £2,789,465.52 (14.1%); £3,249,036.27 -> £2,789,465.54 (14.1%); £3,249,036.28 -> £2,789,465.56 (14.1%); £3,249,036.28 -> £2,789,465.58 (14.1%); £3,249,036.28 -> £2,789,465.60 (14.1%); £3,249,036.29 -> £2,789,465.61 (14.1%); £3,249,036.29 -> £2,789,465.63 (14.1%); £3,249,036.30 -> £2,789,465.65 (14.1%); £3,249,036.30 -> £2,789,465.67 (14.1%); £3,249,036.30 -> £2,789,465.68 (14.1%); £3,249,036.31 -> £2,789,465.70 (14.1%); £3,249,036.31 -> £2,789,465.72 (14.1%); £3,249,036.37 -> £2,789,465.77 (14.1%); £3,249,036.52 -> £2,789,465.81 (14.1%); £3,249,036.67 -> £2,789,465.85 (14.1%); £3,249,036.83 -> £2,789,465.90 (14.1%); £3,249,036.97 -> £2,789,465.94 (14.1%); £3,249,037.12 -> £2,789,465.98 (14.1%); £3,249,037.27 -> £2,789,466.02 (14.1%); £3,249,037.41 -> £2,789,466.06 (14.1%); £3,249,037.42 -> £2,789,466.10 (14.1%); £3,249,037.43 -> £2,789,466.14 (14.1%); £3,249,037.45 -> £2,789,466.19 (14.1%); £3,249,037.46 -> £2,789,466.22 (14.1%); £3,249,037.46 -> £2,789,466.24 (14.1%); £3,249,037.47 -> £2,789,466.26 (14.1%); £3,249,037.47 -> £2,789,466.28 (14.1%); £3,249,037.48 -> £2,789,466.42 (14.1%); £3,249,037.48 -> £2,789,466.55 (14.1%); £3,249,037.48 -> £2,789,466.69 (14.1%); £3,249,037.49 -> £2,789,466.82 (14.1%); £3,249,037.49 -> £2,789,466.96 (14.1%); £3,249,037.49 -> £2,789,467.09 (14.1%); £3,249,037.49 -> £2,789,467.22 (14.1%); £3,249,037.49 -> £2,789,467.36 (14.1%); £3,249,037.49 -> £2,789,467.37 (14.1%); £3,249,037.50 -> £2,789,467.38 (14.1%); £3,249,037.50 -> £2,789,467.39 (14.1%); £3,249,037.50 -> £2,789,467.40 (14.1%); £3,249,037.50 -> £2,789,467.41 (14.1%); £3,249,037.51 -> £2,789,467.43 (14.1%); £3,249,037.52 -> £2,789,467.45 (14.1%); £3,249,037.66 -> £2,789,467.48 (14.1%); £3,249,037.79 -> £2,789,467.51 (14.1%); £3,249,037.94 -> £2,789,467.53 (14.1%); £3,249,038.07 -> £2,789,467.56 (14.1%); £3,249,038.21 -> £2,789,467.59 (14.1%); £3,249,038.35 -> £2,789,467.61 (14.1%); £3,249,038.41 -> £2,789,467.63 (14.1%); £3,249,038.46 -> £2,789,467.64 (14.1%); £3,249,038.47 -> £2,789,467.66 (14.1%); £3,249,038.47 -> £2,789,467.68 (14.1%); £3,249,038.48 -> £2,789,467.70 (14.1%); £3,249,038.48 -> £2,789,467.72 (14.1%); £3,249,038.49 -> £2,789,467.74 (14.1%); £3,249,038.49 -> £2,789,467.76 (14.1%); £3,249,038.49 -> £2,789,467.77 (14.1%); £3,249,038.50 -> £2,789,467.79 (14.1%); £3,249,038.50 -> £2,789,467.81 (14.1%); £3,249,038.51 -> £2,789,467.83 (14.1%); £3,249,038.56 -> £2,789,467.87 (14.1%); £3,249,038.69 -> £2,789,467.92 (14.1%); £3,249,038.83 -> £2,789,467.96 (14.1%); £3,249,038.96 -> £2,789,468.00 (14.1%); £3,249,039.08 -> £2,789,468.05 (14.1%); £3,249,039.21 -> £2,789,468.08 (14.1%); £3,249,039.33 -> £2,789,468.12 (14.1%); £3,249,039.45 -> £2,789,468.16 (14.1%); £3,249,039.46 -> £2,789,468.20 (14.1%); £3,249,039.47 -> £2,789,468.25 (14.1%); £3,249,039.48 -> £2,789,468.29 (14.1%); £3,249,039.49 -> £2,789,468.32 (14.1%); £3,249,039.49 -> £2,789,468.34 (14.1%); £3,249,039.50 -> £2,789,468.36 (14.1%); £3,249,039.50 -> £2,789,468.38 (14.1%); £3,249,039.50 -> £2,789,468.51 (14.1%); £3,249,039.51 -> £2,789,468.65 (14.1%); £3,249,039.51 -> £2,789,468.78 (14.1%); £3,249,039.51 -> £2,789,468.92 (14.1%); £3,249,039.51 -> £2,789,469.05 (14.1%); £3,249,039.51 -> £2,789,469.18 (14.1%); £3,249,039.52 -> £2,789,469.32 (14.1%); £3,249,039.52 -> £2,789,469.45 (14.1%); £3,249,039.52 -> £2,789,469.46 (14.1%); £3,249,039.52 -> £2,789,469.47 (14.1%); £3,249,039.52 -> £2,789,469.48 (14.1%); £3,249,039.52 -> £2,789,469.49 (14.1%); £3,249,039.53 -> £2,789,469.50 (14.1%); £3,249,039.53 -> £2,789,469.52 (14.1%); £3,249,039.53 -> £2,789,469.54 (14.1%); £3,249,039.58 -> £2,789,469.57 (14.1%); £3,249,039.62 -> £2,789,469.59 (14.1%); £3,249,039.68 -> £2,789,469.62 (14.1%); £3,249,039.73 -> £2,789,469.65 (14.1%); £3,249,039.78 -> £2,789,469.67 (14.1%); £3,249,039.83 -> £2,789,469.69 (14.1%); £3,249,039.88 -> £2,789,469.71 (14.1%); £3,249,039.94 -> £2,789,469.73 (14.1%); £3,249,039.94 -> £2,789,469.75 (14.1%); £3,249,039.94 -> £2,789,469.77 (14.1%); £3,249,039.95 -> £2,789,469.79 (14.1%); £3,249,039.95 -> £2,789,469.80 (14.1%); £3,249,039.96 -> £2,789,469.82 (14.1%); £3,249,039.96 -> £2,789,469.84 (14.1%); £3,249,039.97 -> £2,789,469.86 (14.1%); £3,249,039.97 -> £2,789,469.87 (14.1%); £3,249,039.97 -> £2,789,469.89 (14.1%); £3,249,039.97 -> £2,789,469.91 (14.1%); £3,249,040.03 -> £2,789,469.95 (14.1%); £3,249,040.09 -> £2,789,470.00 (14.1%); £3,249,040.16 -> £2,789,470.04 (14.1%); £3,249,040.23 -> £2,789,470.08 (14.1%); £3,249,040.29 -> £2,789,470.12 (14.1%); £3,249,040.36 -> £2,789,470.16 (14.1%); £3,249,040.42 -> £2,789,470.20 (14.1%); £3,249,040.47 -> £2,789,470.24 (14.1%); £3,249,040.48 -> £2,789,470.28 (14.1%); £3,249,040.48 -> £2,789,470.32 (14.1%); £3,249,040.49 -> £2,789,470.37 (14.1%); £3,249,040.49 -> £2,789,470.40 (14.1%); £3,249,040.49 -> £2,789,470.42 (14.1%); £3,249,040.50 -> £2,789,470.44 (14.1%); £3,249,040.50 -> £2,789,470.46 (14.1%); £3,249,040.51 -> £2,789,470.59 (14.1%); £3,249,040.51 -> £2,789,470.72 (14.1%); £3,249,040.51 -> £2,789,470.86 (14.1%); £3,249,040.51 -> £2,789,470.99 (14.1%); £3,249,040.51 -> £2,789,471.12 (14.1%); £3,249,040.52 -> £2,789,471.26 (14.1%); £3,249,040.52 -> £2,789,471.39 (14.1%); £3,249,040.52 -> £2,789,471.52 (14.1%); £3,249,040.52 -> £2,789,471.53 (14.1%); £3,249,040.52 -> £2,789,471.54 (14.1%); £3,249,040.52 -> £2,789,471.55 (14.1%); £3,249,040.52 -> £2,789,471.56 (14.1%); £3,249,040.53 -> £2,789,471.57 (14.1%); £3,249,040.53 -> £2,789,471.59 (14.1%); £3,249,040.53 -> £2,789,471.62 (14.1%); £3,249,040.58 -> £2,789,471.64 (14.1%); £3,249,040.63 -> £2,789,471.67 (14.1%); £3,249,040.68 -> £2,789,471.70 (14.1%); £3,249,040.73 -> £2,789,471.72 (14.1%); £3,249,040.78 -> £2,789,471.75 (14.1%); £3,249,040.84 -> £2,789,471.77 (14.1%); £3,249,040.89 -> £2,789,471.79 (14.1%); £3,249,040.95 -> £2,789,471.81 (14.1%); £3,249,040.95 -> £2,789,471.83 (14.1%); £3,249,040.96 -> £2,789,471.85 (14.1%); £3,249,040.96 -> £2,789,471.87 (14.1%); £3,249,040.97 -> £2,789,471.89 (14.1%); £3,249,040.98 -> £2,789,471.91 (14.1%); £3,249,040.98 -> £2,789,471.93 (14.1%); £3,249,040.98 -> £2,789,471.94 (14.1%); £3,249,040.99 -> £2,789,471.96 (14.1%); £3,249,040.99 -> £2,789,471.98 (14.1%); £3,249,041.00 -> £2,789,472.00 (14.1%); £3,249,041.06 -> £2,789,472.04 (14.1%); £3,249,041.12 -> £2,789,472.09 (14.1%); £3,249,041.19 -> £2,789,472.13 (14.1%); £3,249,041.26 -> £2,789,472.17 (14.1%); £3,249,041.32 -> £2,789,472.22 (14.1%); £3,249,041.38 -> £2,789,472.25 (14.1%); £3,249,041.44 -> £2,789,472.29 (14.1%); £3,249,041.50 -> £2,789,472.33 (14.1%); £3,249,041.51 -> £2,789,472.37 (14.1%); £3,249,041.51 -> £2,789,472.42 (14.1%); £3,249,041.51 -> £2,789,472.46 (14.1%); £3,249,041.52 -> £2,789,472.49 (14.1%); £3,249,041.52 -> £2,789,472.51 (14.1%); £3,249,041.53 -> £2,789,472.53 (14.1%); £3,249,041.53 -> £2,789,472.55 (14.1%); £3,249,041.54 -> £2,789,472.69 (14.1%); £3,249,041.54 -> £2,789,472.83 (14.1%); £3,249,041.54 -> £2,789,472.96 (14.1%); £3,249,041.54 -> £2,789,473.09 (14.1%); £3,249,041.55 -> £2,789,473.22 (14.1%); £3,249,041.55 -> £2,789,473.35 (14.1%); £3,249,041.55 -> £2,789,473.48 (14.1%); £3,249,041.55 -> £2,789,473.61 (14.1%); £3,249,041.55 -> £2,789,473.62 (14.1%); £3,249,041.55 -> £2,789,473.63 (14.1%); £3,249,041.55 -> £2,789,473.63 (14.1%); £3,249,041.55 -> £2,789,473.64 (14.1%); £3,249,041.56 -> £2,789,473.66 (14.1%); £3,249,041.56 -> £2,789,473.67 (14.1%); £3,249,041.56 -> £2,789,473.70 (14.1%); £3,249,041.56 -> £2,789,473.72 (14.1%); £3,249,041.56 -> £2,789,473.74 (14.1%); £3,249,041.57 -> £2,789,473.77 (14.1%); £3,249,041.57 -> £2,789,473.80 (14.1%); £3,249,041.57 -> £2,789,473.82 (14.1%); £3,249,041.58 -> £2,789,473.84 (14.1%); £3,249,041.58 -> £2,789,473.87 (14.1%); £3,249,041.59 -> £2,789,473.89 (14.1%); £3,249,041.59 -> £2,789,473.91 (14.1%); £3,249,041.60 -> £2,789,473.93 (14.1%); £3,249,041.60 -> £2,789,473.95 (14.1%); £3,249,041.61 -> £2,789,473.97 (14.1%); £3,249,041.61 -> £2,789,473.99 (14.1%); £3,249,041.62 -> £2,789,474.01 (14.1%); £3,249,041.62 -> £2,789,474.03 (14.1%); £3,249,041.63 -> £2,789,474.05 (14.1%); £3,249,041.63 -> £2,789,474.07 (14.1%); £3,249,041.63 -> £2,789,474.09 (14.1%); £3,249,041.64 -> £2,789,474.13 (14.1%); £3,249,041.65 -> £2,789,474.17 (14.1%); £3,249,041.65 -> £2,789,474.21 (14.1%); £3,249,041.66 -> £2,789,474.25 (14.1%); £3,249,041.66 -> £2,789,474.29 (14.1%); £3,249,041.67 -> £2,789,474.33 (14.1%); £3,249,041.67 -> £2,789,474.37 (14.1%); £3,249,041.68 -> £2,789,474.41 (14.1%); £3,249,041.68 -> £2,789,474.45 (14.1%); £3,249,041.69 -> £2,789,474.49 (14.1%); £3,249,041.69 -> £2,789,474.53 (14.1%); £3,249,041.69 -> £2,789,474.56 (14.1%); £3,249,041.70 -> £2,789,474.58 (14.1%); £3,249,041.70 -> £2,789,474.60 (14.1%); £3,249,041.71 -> £2,789,474.62 (14.1%); £3,249,041.71 -> £2,789,474.76 (14.1%); £3,249,041.72 -> £2,789,474.89 (14.1%); £3,249,041.72 -> £2,789,475.03 (14.1%); £3,249,041.72 -> £2,789,475.16 (14.1%); £3,249,041.72 -> £2,789,475.30 (14.1%); £3,249,041.72 -> £2,789,475.43 (14.1%); £3,249,041.73 -> £2,789,475.56 (14.1%); £3,249,041.73 -> £2,789,475.69 (14.1%); £3,249,041.73 -> £2,789,475.70 (14.1%); £3,249,041.73 -> £2,789,475.71 (14.1%); £3,249,041.73 -> £2,789,475.72 (14.1%); £3,249,041.73 -> £2,789,475.73 (14.1%); £3,249,041.74 -> £2,789,475.74 (14.1%); £3,249,041.74 -> £2,789,475.76 (14.1%); £3,249,041.74 -> £2,789,475.78 (14.1%); £3,249,041.74 -> £2,789,475.80 (14.1%); £3,249,041.75 -> £2,789,475.82 (14.1%); £3,249,041.75 -> £2,789,475.85 (14.1%); £3,249,041.75 -> £2,789,475.87 (14.1%); £3,249,041.76 -> £2,789,475.90 (14.1%); £3,249,041.76 -> £2,789,475.93 (14.1%); £3,249,041.77 -> £2,789,475.96 (14.1%); £3,249,041.77 -> £2,789,475.98 (14.1%); £3,249,041.78 -> £2,789,476.01 (14.1%); £3,249,041.78 -> £2,789,476.04 (14.1%); £3,249,041.79 -> £2,789,476.07 (14.1%); £3,249,041.80 -> £2,789,476.10 (14.1%); £3,249,041.81 -> £2,789,476.12 (14.1%); £3,249,041.81 -> £2,789,476.15 (14.1%); £3,249,041.82 -> £2,789,476.17 (14.1%); £3,249,041.82 -> £2,789,476.19 (14.1%); £3,249,041.83 -> £2,789,476.21 (14.1%); £3,249,041.83 -> £2,789,476.23 (14.1%); £3,249,041.84 -> £2,789,476.27 (14.1%); £3,249,041.84 -> £2,789,476.31 (14.1%); £3,249,041.85 -> £2,789,476.35 (14.1%); £3,249,041.85 -> £2,789,476.39 (14.1%); £3,249,041.86 -> £2,789,476.43 (14.1%); £3,249,041.86 -> £2,789,476.47 (14.1%); £3,249,041.87 -> £2,789,476.51 (14.1%); £3,249,041.87 -> £2,789,476.55 (14.1%); £3,249,041.88 -> £2,789,476.59 (14.1%); £3,249,041.88 -> £2,789,476.64 (14.1%); £3,249,041.89 -> £2,789,476.68 (14.1%); £3,249,041.89 -> £2,789,476.71 (14.1%); £3,249,041.90 -> £2,789,476.73 (14.1%); £3,249,041.90 -> £2,789,476.75 (14.1%); £3,249,041.91 -> £2,789,476.77 (14.1%); £3,249,041.91 -> £2,789,476.90 (14.1%); £3,249,041.91 -> £2,789,477.04 (14.1%); £3,249,041.91 -> £2,789,477.17 (14.1%); £3,249,041.91 -> £2,789,477.30 (14.1%); £3,249,041.92 -> £2,789,477.43 (14.1%); £3,249,041.92 -> £2,789,477.56 (14.1%); £3,249,041.92 -> £2,789,477.69 (14.1%); £3,249,041.92 -> £2,789,477.82 (14.1%); £3,249,041.92 -> £2,789,477.83 (14.1%); £3,249,041.92 -> £2,789,477.83 (14.1%); £3,249,041.92 -> £2,789,477.84 (14.1%); £3,249,041.93 -> £2,789,477.85 (14.1%); £3,249,041.93 -> £2,789,477.87 (14.1%); £3,249,041.93 -> £2,789,477.89 (14.1%); £3,249,041.93 -> £2,789,477.91 (14.1%); £3,249,041.98 -> £2,789,477.94 (14.1%); £3,249,042.03 -> £2,789,477.96 (14.1%); £3,249,042.08 -> £2,789,477.99 (14.1%); £3,249,042.13 -> £2,789,478.02 (14.1%); £3,249,042.18 -> £2,789,478.04 (14.1%); £3,249,042.23 -> £2,789,478.06 (14.1%); £3,249,042.29 -> £2,789,478.08 (14.1%); £3,249,042.34 -> £2,789,478.10 (14.1%); £3,249,042.34 -> £2,789,478.12 (14.1%); £3,249,042.35 -> £2,789,478.14 (14.1%); £3,249,042.35 -> £2,789,478.15 (14.1%); £3,249,042.35 -> £2,789,478.17 (14.1%); £3,249,042.36 -> £2,789,478.19 (14.1%); £3,249,042.36 -> £2,789,478.21 (14.1%); £3,249,042.36 -> £2,789,478.22 (14.1%); £3,249,042.37 -> £2,789,478.24 (14.1%); £3,249,042.37 -> £2,789,478.26 (14.1%); £3,249,042.38 -> £2,789,478.28 (14.1%); £3,249,042.44 -> £2,789,478.32 (14.1%); £3,249,042.50 -> £2,789,478.37 (14.1%); £3,249,042.57 -> £2,789,478.41 (14.1%); £3,249,042.63 -> £2,789,478.45 (14.1%); £3,249,042.70 -> £2,789,478.50 (14.1%); £3,249,042.76 -> £2,789,478.53 (14.1%); £3,249,042.82 -> £2,789,478.57 (14.1%); £3,249,042.88 -> £2,789,478.61 (14.1%); £3,249,042.88 -> £2,789,478.65 (14.1%); £3,249,042.89 -> £2,789,478.70 (14.1%); £3,249,042.89 -> £2,789,478.75 (14.1%); £3,249,042.90 -> £2,789,478.77 (14.1%); £3,249,042.90 -> £2,789,478.80 (14.1%); £3,249,042.91 -> £2,789,478.82 (14.1%); £3,249,042.91 -> £2,789,478.83 (14.1%); £3,249,042.92 -> £2,789,478.97 (14.1%); £3,249,042.92 -> £2,789,479.10 (14.1%); £3,249,042.92 -> £2,789,479.23 (14.1%); £3,249,042.92 -> £2,789,479.37 (14.1%); £3,249,042.92 -> £2,789,479.50 (14.1%); £3,249,042.93 -> £2,789,479.63 (14.1%); £3,249,042.93 -> £2,789,479.76 (14.1%); £3,249,042.93 -> £2,789,479.89 (14.1%); £3,249,042.93 -> £2,789,479.90 (14.1%); £3,249,042.93 -> £2,789,479.91 (14.1%); £3,249,042.93 -> £2,789,479.92 (14.1%); £3,249,042.93 -> £2,789,479.93 (14.1%); £3,249,042.94 -> £2,789,479.94 (14.1%); £3,249,042.94 -> £2,789,479.96 (14.1%); £3,249,042.94 -> £2,789,479.99 (14.1%); £3,249,042.99 -> £2,789,480.01 (14.1%); £3,249,043.03 -> £2,789,480.04 (14.1%); £3,249,043.09 -> £2,789,480.07 (14.1%); £3,249,043.14 -> £2,789,480.09 (14.1%); £3,249,043.19 -> £2,789,480.12 (14.1%); £3,249,043.24 -> £2,789,480.14 (14.1%); £3,249,043.30 -> £2,789,480.16 (14.1%); £3,249,043.35 -> £2,789,480.18 (14.1%); £3,249,043.36 -> £2,789,480.19 (14.1%); £3,249,043.36 -> £2,789,480.21 (14.1%); £3,249,043.36 -> £2,789,480.23 (14.1%); £3,249,043.37 -> £2,789,480.25 (14.1%); £3,249,043.37 -> £2,789,480.27 (14.1%); £3,249,043.37 -> £2,789,480.29 (14.1%); £3,249,043.38 -> £2,789,480.30 (14.1%); £3,249,043.38 -> £2,789,480.32 (14.1%); £3,249,043.38 -> £2,789,480.34 (14.1%); £3,249,043.39 -> £2,789,480.36 (14.1%); £3,249,043.45 -> £2,789,480.40 (14.1%); £3,249,043.51 -> £2,789,480.44 (14.1%); £3,249,043.58 -> £2,789,480.49 (14.1%); £3,249,043.64 -> £2,789,480.53 (14.1%); £3,249,043.71 -> £2,789,480.57 (14.1%); £3,249,043.77 -> £2,789,480.61 (14.1%); £3,249,043.83 -> £2,789,480.64 (14.1%); £3,249,043.89 -> £2,789,480.68 (14.1%); £3,249,043.89 -> £2,789,480.73 (14.1%); £3,249,043.89 -> £2,789,480.77 (14.1%); £3,249,043.90 -> £2,789,480.82 (14.1%); £3,249,043.91 -> £2,789,480.84 (14.1%); £3,249,043.91 -> £2,789,480.87 (14.1%); £3,249,043.92 -> £2,789,480.89 (14.1%); £3,249,043.92 -> £2,789,480.91 (14.1%); £3,249,043.92 -> £2,789,481.04 (14.1%); £3,249,043.92 -> £2,789,481.17 (14.1%); £3,249,043.93 -> £2,789,481.31 (14.1%); £3,249,043.93 -> £2,789,481.44 (14.1%); £3,249,043.93 -> £2,789,481.57 (14.1%); £3,249,043.93 -> £2,789,481.70 (14.1%); £3,249,043.93 -> £2,789,481.84 (14.1%); £3,249,043.94 -> £2,789,481.97 (14.1%); £3,249,043.94 -> £2,789,481.98 (14.1%); £3,249,043.94 -> £2,789,481.99 (14.1%); £3,249,043.94 -> £2,789,482.00 (14.1%); £3,249,043.94 -> £2,789,482.01 (14.1%); £3,249,043.94 -> £2,789,482.02 (14.1%); £3,249,043.95 -> £2,789,482.04 (14.1%); £3,249,043.95 -> £2,789,482.06 (14.1%); £3,249,044.03 -> £2,789,482.09 (14.1%); £3,249,044.12 -> £2,789,482.12 (14.1%); £3,249,044.20 -> £2,789,482.14 (14.1%); £3,249,044.29 -> £2,789,482.17 (14.1%); £3,249,044.38 -> £2,789,482.19 (14.1%); £3,249,044.46 -> £2,789,482.21 (14.1%); £3,249,044.52 -> £2,789,482.23 (14.1%); £3,249,044.57 -> £2,789,482.25 (14.1%); £3,249,044.58 -> £2,789,482.27 (14.1%); £3,249,044.58 -> £2,789,482.29 (14.1%); £3,249,044.58 -> £2,789,482.31 (14.1%); £3,249,044.59 -> £2,789,482.33 (14.1%); £3,249,044.59 -> £2,789,482.35 (14.1%); £3,249,044.59 -> £2,789,482.36 (14.1%); £3,249,044.60 -> £2,789,482.38 (14.1%); £3,249,044.60 -> £2,789,482.40 (14.1%); £3,249,044.61 -> £2,789,482.42 (14.1%); £3,249,044.61 -> £2,789,482.44 (14.1%); £3,249,044.67 -> £2,789,482.48 (14.1%); £3,249,044.76 -> £2,789,482.52 (14.1%); £3,249,044.85 -> £2,789,482.57 (14.1%); £3,249,044.94 -> £2,789,482.61 (14.1%); £3,249,045.03 -> £2,789,482.65 (14.1%); £3,249,045.12 -> £2,789,482.69 (14.1%); £3,249,045.20 -> £2,789,482.73 (14.1%); £3,249,045.28 -> £2,789,482.77 (14.1%); £3,249,045.29 -> £2,789,482.81 (14.1%); £3,249,045.30 -> £2,789,482.85 (14.1%); £3,249,045.30 -> £2,789,482.90 (14.1%); £3,249,045.31 -> £2,789,482.93 (14.1%); £3,249,045.32 -> £2,789,482.95 (14.1%); £3,249,045.32 -> £2,789,482.97 (14.1%); £3,249,045.33 -> £2,789,482.99 (14.1%); £3,249,045.33 -> £2,789,483.13 (14.1%); £3,249,045.33 -> £2,789,483.26 (14.1%); £3,249,045.34 -> £2,789,483.40 (14.1%); £3,249,045.34 -> £2,789,483.53 (14.1%); £3,249,045.34 -> £2,789,483.66 (14.1%); £3,249,045.34 -> £2,789,483.79 (14.1%); £3,249,045.34 -> £2,789,483.93 (14.1%); £3,249,045.35 -> £2,789,484.06 (14.1%); £3,249,045.35 -> £2,789,484.07 (14.1%); £3,249,045.35 -> £2,789,484.08 (14.1%); £3,249,045.35 -> £2,789,484.09 (14.1%); £3,249,045.35 -> £2,789,484.10 (14.1%); £3,249,045.35 -> £2,789,484.11 (14.1%); £3,249,045.36 -> £2,789,484.13 (14.1%); £3,249,045.36 -> £2,789,484.16 (14.1%); £3,249,045.41 -> £2,789,484.18 (14.1%); £3,249,045.45 -> £2,789,484.21 (14.1%); £3,249,045.51 -> £2,789,484.23 (14.1%); £3,249,045.56 -> £2,789,484.26 (14.1%); £3,249,045.61 -> £2,789,484.29 (14.1%); £3,249,045.66 -> £2,789,484.30 (14.1%); £3,249,045.71 -> £2,789,484.32 (14.1%); £3,249,045.77 -> £2,789,484.34 (14.1%); £3,249,045.77 -> £2,789,484.36 (14.1%); £3,249,045.77 -> £2,789,484.38 (14.1%); £3,249,045.78 -> £2,789,484.40 (14.1%); £3,249,045.78 -> £2,789,484.42 (14.1%); £3,249,045.79 -> £2,789,484.44 (14.1%); £3,249,045.79 -> £2,789,484.45 (14.1%); £3,249,045.79 -> £2,789,484.47 (14.1%); £3,249,045.80 -> £2,789,484.49 (14.1%); £3,249,045.80 -> £2,789,484.51 (14.1%); £3,249,045.81 -> £2,789,484.53 (14.1%); £3,249,045.87 -> £2,789,484.57 (14.1%); £3,249,045.93 -> £2,789,484.62 (14.1%); £3,249,046.00 -> £2,789,484.66 (14.1%); £3,249,046.06 -> £2,789,484.70 (14.1%); £3,249,046.13 -> £2,789,484.74 (14.1%); £3,249,046.19 -> £2,789,484.78 (14.1%); £3,249,046.26 -> £2,789,484.82 (14.1%); £3,249,046.31 -> £2,789,484.86 (14.1%); £3,249,046.32 -> £2,789,484.91 (14.1%); £3,249,046.33 -> £2,789,484.95 (14.1%); £3,249,046.33 -> £2,789,485.00 (14.1%); £3,249,046.34 -> £2,789,485.03 (14.1%); £3,249,046.34 -> £2,789,485.05 (14.1%); £3,249,046.35 -> £2,789,485.07 (14.1%); £3,249,046.35 -> £2,789,485.09 (14.1%); £3,249,046.36 -> £2,789,485.23 (14.1%); £3,249,046.36 -> £2,789,485.36 (14.1%); £3,249,046.36 -> £2,789,485.50 (14.1%); £3,249,046.36 -> £2,789,485.64 (14.1%); £3,249,046.37 -> £2,789,485.77 (14.1%); £3,249,046.37 -> £2,789,485.91 (14.1%); £3,249,046.37 -> £2,789,486.05 (14.1%); £3,249,046.37 -> £2,789,486.18 (14.1%); £3,249,046.37 -> £2,789,486.19 (14.1%); £3,249,046.38 -> £2,789,486.20 (14.1%); £3,249,046.38 -> £2,789,486.21 (14.1%); £3,249,046.38 -> £2,789,486.22 (14.1%); £3,249,046.38 -> £2,789,486.23 (14.1%); £3,249,046.38 -> £2,789,486.25 (14.1%); £3,249,046.38 -> £2,789,486.28 (14.1%); £3,249,046.43 -> £2,789,486.30 (14.1%); £3,249,046.48 -> £2,789,486.33 (14.1%); £3,249,046.53 -> £2,789,486.35 (14.1%); £3,249,046.58 -> £2,789,486.38 (14.1%); £3,249,046.63 -> £2,789,486.40 (14.1%); £3,249,046.68 -> £2,789,486.42 (14.1%); £3,249,046.74 -> £2,789,486.44 (14.1%); £3,249,046.79 -> £2,789,486.46 (14.1%); £3,249,046.80 -> £2,789,486.48 (14.1%); £3,249,046.80 -> £2,789,486.50 (14.1%); £3,249,046.80 -> £2,789,486.52 (14.1%); £3,249,046.81 -> £2,789,486.54 (14.1%); £3,249,046.81 -> £2,789,486.56 (14.1%); £3,249,046.82 -> £2,789,486.57 (14.1%); £3,249,046.82 -> £2,789,486.59 (14.1%); £3,249,046.83 -> £2,789,486.61 (14.1%); £3,249,046.83 -> £2,789,486.63 (14.1%); £3,249,046.84 -> £2,789,486.65 (14.1%); £3,249,046.90 -> £2,789,486.69 (14.1%); £3,249,046.96 -> £2,789,486.74 (14.1%); £3,249,047.03 -> £2,789,486.78 (14.1%); £3,249,047.10 -> £2,789,486.83 (14.1%); £3,249,047.16 -> £2,789,486.87 (14.1%); £3,249,047.23 -> £2,789,486.91 (14.1%); £3,249,047.29 -> £2,789,486.95 (14.1%); £3,249,047.35 -> £2,789,486.99 (14.1%); £3,249,047.35 -> £2,789,487.03 (14.1%); £3,249,047.35 -> £2,789,487.07 (14.1%); £3,249,047.36 -> £2,789,487.12 (14.1%); £3,249,047.37 -> £2,789,487.15 (14.1%); £3,249,047.37 -> £2,789,487.17 (14.1%); £3,249,047.38 -> £2,789,487.19 (14.1%); £3,249,047.38 -> £2,789,487.21 (14.1%); £3,249,047.39 -> £2,789,487.35 (14.1%); £3,249,047.39 -> £2,789,487.48 (14.1%); £3,249,047.39 -> £2,789,487.62 (14.1%); £3,249,047.39 -> £2,789,487.75 (14.1%); £3,249,047.40 -> £2,789,487.89 (14.1%); £3,249,047.40 -> £2,789,488.02 (14.1%); £3,249,047.40 -> £2,789,488.15 (14.1%); £3,249,047.40 -> £2,789,488.28 (14.1%); £3,249,047.40 -> £2,789,488.29 (14.1%); £3,249,047.40 -> £2,789,488.30 (14.1%); £3,249,047.41 -> £2,789,488.31 (14.1%); £3,249,047.41 -> £2,789,488.32 (14.1%); £3,249,047.41 -> £2,789,488.34 (14.1%); £3,249,047.41 -> £2,789,488.35 (14.1%); £3,249,047.42 -> £2,789,488.38 (14.1%); £3,249,047.42 -> £2,789,488.40 (14.1%); £3,249,047.43 -> £2,789,488.43 (14.1%); £3,249,047.43 -> £2,789,488.46 (14.1%); £3,249,047.44 -> £2,789,488.49 (14.1%); £3,249,047.45 -> £2,789,488.52 (14.1%); £3,249,047.45 -> £2,789,488.54 (14.1%); £3,249,047.46 -> £2,789,488.56 (14.1%); £3,249,047.46 -> £2,789,488.58 (14.1%); £3,249,047.47 -> £2,789,488.61 (14.1%); £3,249,047.47 -> £2,789,488.63 (14.1%); £3,249,047.48 -> £2,789,488.65 (14.1%); £3,249,047.48 -> £2,789,488.67 (14.1%); £3,249,047.49 -> £2,789,488.69 (14.1%); £3,249,047.49 -> £2,789,488.71 (14.1%); £3,249,047.50 -> £2,789,488.73 (14.1%); £3,249,047.50 -> £2,789,488.74 (14.1%); £3,249,047.51 -> £2,789,488.76 (14.1%); £3,249,047.51 -> £2,789,488.78 (14.1%); £3,249,047.52 -> £2,789,488.82 (14.1%); £3,249,047.52 -> £2,789,488.86 (14.1%); £3,249,047.53 -> £2,789,488.90 (14.1%); £3,249,047.53 -> £2,789,488.94 (14.1%); £3,249,047.54 -> £2,789,488.98 (14.1%); £3,249,047.54 -> £2,789,489.02 (14.1%); £3,249,047.54 -> £2,789,489.06 (14.1%); £3,249,047.55 -> £2,789,489.10 (14.1%); £3,249,047.55 -> £2,789,489.14 (14.1%); £3,249,047.55 -> £2,789,489.18 (14.1%); £3,249,047.56 -> £2,789,489.22 (14.1%); £3,249,047.56 -> £2,789,489.24 (14.1%); £3,249,047.57 -> £2,789,489.27 (14.1%); £3,249,047.57 -> £2,789,489.29 (14.1%); £3,249,047.58 -> £2,789,489.31 (14.1%); £3,249,047.58 -> £2,789,489.45 (14.1%); £3,249,047.58 -> £2,789,489.58 (14.1%); £3,249,047.59 -> £2,789,489.72 (14.1%); £3,249,047.59 -> £2,789,489.85 (14.1%); £3,249,047.59 -> £2,789,489.98 (14.1%); £3,249,047.59 -> £2,789,490.11 (14.1%); £3,249,047.59 -> £2,789,490.24 (14.1%); £3,249,047.60 -> £2,789,490.37 (14.1%); £3,249,047.60 -> £2,789,490.38 (14.1%); £3,249,047.60 -> £2,789,490.39 (14.1%); £3,249,047.60 -> £2,789,490.40 (14.1%); £3,249,047.60 -> £2,789,490.41 (14.1%); £3,249,047.60 -> £2,789,490.42 (14.1%); £3,249,047.60 -> £2,789,490.44 (14.1%); £3,249,047.60 -> £2,789,490.46 (14.1%); £3,249,047.61 -> £2,789,490.48 (14.1%); £3,249,047.61 -> £2,789,490.50 (14.1%); £3,249,047.61 -> £2,789,490.52 (14.1%); £3,249,047.62 -> £2,789,490.55 (14.1%); £3,249,047.62 -> £2,789,490.58 (14.1%); £3,249,047.62 -> £2,789,490.61 (14.1%); £3,249,047.63 -> £2,789,490.63 (14.1%); £3,249,047.63 -> £2,789,490.66 (14.1%); £3,249,047.64 -> £2,789,490.69 (14.1%); £3,249,047.64 -> £2,789,490.72 (14.1%); £3,249,047.65 -> £2,789,490.75 (14.1%); £3,249,047.66 -> £2,789,490.77 (14.1%); £3,249,047.67 -> £2,789,490.80 (14.1%); £3,249,047.67 -> £2,789,490.82 (14.1%); £3,249,047.68 -> £2,789,490.84 (14.1%); £3,249,047.69 -> £2,789,490.86 (14.1%); £3,249,047.69 -> £2,789,490.89 (14.1%); £3,249,047.70 -> £2,789,490.91 (14.1%); £3,249,047.70 -> £2,789,490.95 (14.1%); £3,249,047.71 -> £2,789,490.99 (14.1%); £3,249,047.71 -> £2,789,491.03 (14.1%); £3,249,047.72 -> £2,789,491.07 (14.1%); £3,249,047.72 -> £2,789,491.11 (14.1%); £3,249,047.73 -> £2,789,491.15 (14.1%); £3,249,047.73 -> £2,789,491.19 (14.1%); £3,249,047.73 -> £2,789,491.23 (14.1%); £3,249,047.74 -> £2,789,491.27 (14.1%); £3,249,047.74 -> £2,789,491.32 (14.1%); £3,249,047.75 -> £2,789,491.36 (14.1%); £3,249,047.75 -> £2,789,491.39 (14.1%); £3,249,047.76 -> £2,789,491.41 (14.1%); £3,249,047.76 -> £2,789,491.43 (14.1%); £3,249,047.76 -> £2,789,491.45 (14.1%); £3,249,047.77 -> £2,789,491.58 (14.1%); £3,249,047.77 -> £2,789,491.72 (14.1%); £3,249,047.77 -> £2,789,491.85 (14.1%); £3,249,047.77 -> £2,789,491.98 (14.1%); £3,249,047.78 -> £2,789,492.11 (14.1%); £3,249,047.78 -> £2,789,492.24 (14.1%); £3,249,047.78 -> £2,789,492.37 (14.1%); £3,249,047.78 -> £2,789,492.50 (14.1%); £3,249,047.78 -> £2,789,492.51 (14.1%); £3,249,047.78 -> £2,789,492.52 (14.1%); £3,249,047.78 -> £2,789,492.53 (14.1%); £3,249,047.79 -> £2,789,492.54 (14.1%); £3,249,047.79 -> £2,789,492.55 (14.1%); £3,249,047.79 -> £2,789,492.57 (14.1%); £3,249,047.79 -> £2,789,492.60 (14.1%); £3,249,047.84 -> £2,789,492.62 (14.1%); £3,249,047.89 -> £2,789,492.65 (14.1%); £3,249,047.94 -> £2,789,492.67 (14.1%); £3,249,047.99 -> £2,789,492.70 (14.1%); £3,249,048.04 -> £2,789,492.72 (14.1%); £3,249,048.09 -> £2,789,492.74 (14.1%); £3,249,048.14 -> £2,789,492.76 (14.1%); £3,249,048.20 -> £2,789,492.78 (14.1%); £3,249,048.20 -> £2,789,492.80 (14.1%); £3,249,048.20 -> £2,789,492.82 (14.1%); £3,249,048.21 -> £2,789,492.84 (14.1%); £3,249,048.21 -> £2,789,492.85 (14.1%); £3,249,048.22 -> £2,789,492.87 (14.1%); £3,249,048.22 -> £2,789,492.89 (14.1%); £3,249,048.22 -> £2,789,492.91 (14.1%); £3,249,048.23 -> £2,789,492.92 (14.1%); £3,249,048.23 -> £2,789,492.94 (14.1%); £3,249,048.23 -> £2,789,492.96 (14.1%); £3,249,048.29 -> £2,789,493.00 (14.1%); £3,249,048.35 -> £2,789,493.05 (14.1%); £3,249,048.42 -> £2,789,493.09 (14.1%); £3,249,048.49 -> £2,789,493.13 (14.1%); £3,249,048.55 -> £2,789,493.17 (14.1%); £3,249,048.61 -> £2,789,493.21 (14.1%); £3,249,048.67 -> £2,789,493.25 (14.1%); £3,249,048.73 -> £2,789,493.29 (14.1%); £3,249,048.74 -> £2,789,493.33 (14.1%); £3,249,048.74 -> £2,789,493.38 (14.1%); £3,249,048.75 -> £2,789,493.43 (14.1%); £3,249,048.75 -> £2,789,493.45 (14.1%); £3,249,048.76 -> £2,789,493.48 (14.1%); £3,249,048.77 -> £2,789,493.50 (14.1%); £3,249,048.77 -> £2,789,493.52 (14.1%); £3,249,048.77 -> £2,789,493.65 (14.1%); £3,249,048.78 -> £2,789,493.78 (14.1%); £3,249,048.78 -> £2,789,493.91 (14.1%); £3,249,048.78 -> £2,789,494.04 (14.1%); £3,249,048.78 -> £2,789,494.17 (14.1%); £3,249,048.78 -> £2,789,494.30 (14.1%); £3,249,048.78 -> £2,789,494.43 (14.1%); £3,249,048.78 -> £2,789,494.56 (14.1%); £3,249,048.79 -> £2,789,494.57 (14.1%); £3,249,048.79 -> £2,789,494.58 (14.1%); £3,249,048.79 -> £2,789,494.59 (14.1%); £3,249,048.79 -> £2,789,494.60 (14.1%); £3,249,048.79 -> £2,789,494.61 (14.1%); £3,249,048.79 -> £2,789,494.63 (14.1%); £3,249,048.79 -> £2,789,494.65 (14.1%); £3,249,048.84 -> £2,789,494.68 (14.1%); £3,249,048.89 -> £2,789,494.70 (14.1%); £3,249,048.94 -> £2,789,494.73 (14.1%); £3,249,048.99 -> £2,789,494.76 (14.1%); £3,249,049.04 -> £2,789,494.78 (14.1%); £3,249,049.09 -> £2,789,494.80 (14.1%); £3,249,049.15 -> £2,789,494.82 (14.1%); £3,249,049.20 -> £2,789,494.84 (14.1%); £3,249,049.21 -> £2,789,494.86 (14.1%); £3,249,049.21 -> £2,789,494.88 (14.1%); £3,249,049.22 -> £2,789,494.90 (14.1%); £3,249,049.22 -> £2,789,494.92 (14.1%); £3,249,049.22 -> £2,789,494.93 (14.1%); £3,249,049.23 -> £2,789,494.95 (14.1%); £3,249,049.23 -> £2,789,494.97 (14.1%); £3,249,049.23 -> £2,789,494.99 (14.1%); £3,249,049.24 -> £2,789,495.00 (14.1%); £3,249,049.24 -> £2,789,495.02 (14.1%); £3,249,049.30 -> £2,789,495.07 (14.1%); £3,249,049.36 -> £2,789,495.11 (14.1%); £3,249,049.43 -> £2,789,495.15 (14.1%); £3,249,049.50 -> £2,789,495.19 (14.1%); £3,249,049.56 -> £2,789,495.24 (14.1%); £3,249,049.62 -> £2,789,495.28 (14.1%); £3,249,049.69 -> £2,789,495.32 (14.1%); £3,249,049.75 -> £2,789,495.36 (14.1%); £3,249,049.75 -> £2,789,495.40 (14.1%); £3,249,049.76 -> £2,789,495.45 (14.1%); £3,249,049.76 -> £2,789,495.49 (14.1%); £3,249,049.77 -> £2,789,495.52 (14.1%); £3,249,049.77 -> £2,789,495.54 (14.1%); £3,249,049.78 -> £2,789,495.56 (14.1%); £3,249,049.78 -> £2,789,495.58 (14.1%); £3,249,049.79 -> £2,789,495.72 (14.1%); £3,249,049.79 -> £2,789,495.85 (14.1%); £3,249,049.79 -> £2,789,495.98 (14.1%); £3,249,049.79 -> £2,789,496.12 (14.1%); £3,249,049.79 -> £2,789,496.25 (14.1%); £3,249,049.79 -> £2,789,496.38 (14.1%); £3,249,049.80 -> £2,789,496.51 (14.1%); £3,249,049.80 -> £2,789,496.64 (14.1%); £3,249,049.80 -> £2,789,496.65 (14.1%); £3,249,049.80 -> £2,789,496.66 (14.1%); £3,249,049.80 -> £2,789,496.67 (14.1%); £3,249,049.80 -> £2,789,496.68 (14.1%); £3,249,049.81 -> £2,789,496.69 (14.1%); £3,249,049.81 -> £2,789,496.71 (14.1%); £3,249,049.82 -> £2,789,496.73 (14.1%); £3,249,049.93 -> £2,789,496.76 (14.1%); £3,249,050.03 -> £2,789,496.79 (14.1%); £3,249,050.15 -> £2,789,496.81 (14.1%); £3,249,050.27 -> £2,789,496.84 (14.1%); £3,249,050.38 -> £2,789,496.86 (14.1%); £3,249,050.50 -> £2,789,496.88 (14.1%); £3,249,050.55 -> £2,789,496.90 (14.1%); £3,249,050.60 -> £2,789,496.92 (14.1%); £3,249,050.61 -> £2,789,496.94 (14.1%); £3,249,050.61 -> £2,789,496.96 (14.1%); £3,249,050.62 -> £2,789,496.98 (14.1%); £3,249,050.62 -> £2,789,497.00 (14.1%); £3,249,050.62 -> £2,789,497.02 (14.1%); £3,249,050.63 -> £2,789,497.03 (14.1%); £3,249,050.63 -> £2,789,497.05 (14.1%); £3,249,050.64 -> £2,789,497.07 (14.1%); £3,249,050.64 -> £2,789,497.09 (14.1%); £3,249,050.64 -> £2,789,497.11 (14.1%); £3,249,050.70 -> £2,789,497.15 (14.1%); £3,249,050.81 -> £2,789,497.19 (14.1%); £3,249,050.92 -> £2,789,497.23 (14.1%); £3,249,051.03 -> £2,789,497.27 (14.1%); £3,249,051.14 -> £2,789,497.31 (14.1%); £3,249,051.24 -> £2,789,497.35 (14.1%); £3,249,051.35 -> £2,789,497.39 (14.1%); £3,249,051.46 -> £2,789,497.43 (14.1%); £3,249,051.47 -> £2,789,497.47 (14.1%); £3,249,051.47 -> £2,789,497.52 (14.1%); £3,249,051.48 -> £2,789,497.56 (14.1%); £3,249,051.49 -> £2,789,497.59 (14.1%); £3,249,051.50 -> £2,789,497.61 (14.1%); £3,249,051.50 -> £2,789,497.63 (14.1%); £3,249,051.50 -> £2,789,497.65 (14.1%); £3,249,051.51 -> £2,789,497.79 (14.1%); £3,249,051.51 -> £2,789,497.92 (14.1%); £3,249,051.51 -> £2,789,498.06 (14.1%); £3,249,051.52 -> £2,789,498.19 (14.1%); £3,249,051.52 -> £2,789,498.32 (14.1%); £3,249,051.52 -> £2,789,498.45 (14.1%); £3,249,051.52 -> £2,789,498.58 (14.1%); £3,249,051.52 -> £2,789,498.71 (14.1%); £3,249,051.52 -> £2,789,498.72 (14.1%); £3,249,051.52 -> £2,789,498.73 (14.1%); £3,249,051.53 -> £2,789,498.74 (14.1%); £3,249,051.53 -> £2,789,498.75 (14.1%); £3,249,051.53 -> £2,789,498.77 (14.1%); £3,249,051.54 -> £2,789,498.79 (14.1%); £3,249,051.54 -> £2,789,498.81 (14.1%); £3,249,051.65 -> £2,789,498.84 (14.1%); £3,249,051.76 -> £2,789,498.86 (14.1%); £3,249,051.87 -> £2,789,498.89 (14.1%); £3,249,051.97 -> £2,789,498.91 (14.1%); £3,249,052.08 -> £2,789,498.94 (14.1%); £3,249,052.19 -> £2,789,498.96 (14.1%); £3,249,052.25 -> £2,789,498.98 (14.1%); £3,249,052.30 -> £2,789,499.00 (14.1%); £3,249,052.30 -> £2,789,499.01 (14.1%); £3,249,052.31 -> £2,789,499.03 (14.1%); £3,249,052.31 -> £2,789,499.05 (14.1%); £3,249,052.31 -> £2,789,499.07 (14.1%); £3,249,052.32 -> £2,789,499.09 (14.1%); £3,249,052.32 -> £2,789,499.10 (14.1%); £3,249,052.32 -> £2,789,499.12 (14.1%); £3,249,052.33 -> £2,789,499.14 (14.1%); £3,249,052.33 -> £2,789,499.16 (14.1%); £3,249,052.33 -> £2,789,499.18 (14.1%); £3,249,052.39 -> £2,789,499.22 (14.1%); £3,249,052.50 -> £2,789,499.26 (14.1%); £3,249,052.61 -> £2,789,499.30 (14.1%); £3,249,052.71 -> £2,789,499.34 (14.1%); £3,249,052.82 -> £2,789,499.38 (14.1%); £3,249,052.92 -> £2,789,499.42 (14.1%); £3,249,053.02 -> £2,789,499.46 (14.1%); £3,249,053.12 -> £2,789,499.50 (14.1%); £3,249,053.13 -> £2,789,499.54 (14.1%); £3,249,053.14 -> £2,789,499.59 (14.1%); £3,249,053.15 -> £2,789,499.64 (14.1%); £3,249,053.16 -> £2,789,499.66 (14.1%); £3,249,053.16 -> £2,789,499.69 (14.1%); £3,249,053.17 -> £2,789,499.71 (14.1%); £3,249,053.17 -> £2,789,499.73 (14.1%); £3,249,053.18 -> £2,789,499.86 (14.1%); £3,249,053.18 -> £2,789,500.00 (14.1%); £3,249,053.18 -> £2,789,500.13 (14.1%); £3,249,053.18 -> £2,789,500.26 (14.1%); £3,249,053.19 -> £2,789,500.40 (14.1%); £3,249,053.19 -> £2,789,500.53 (14.1%); £3,249,053.19 -> £2,789,500.66 (14.1%); £3,249,053.19 -> £2,789,500.79 (14.1%); £3,249,053.19 -> £2,789,500.80 (14.1%); £3,249,053.19 -> £2,789,500.81 (14.1%); £3,249,053.20 -> £2,789,500.82 (14.1%); £3,249,053.20 -> £2,789,500.83 (14.1%); £3,249,053.20 -> £2,789,500.84 (14.1%); £3,249,053.21 -> £2,789,500.86 (14.1%); £3,249,053.23 -> £2,789,500.89 (14.1%); £3,249,053.41 -> £2,789,500.91 (14.1%); £3,249,053.59 -> £2,789,500.94 (14.1%); £3,249,053.77 -> £2,789,500.96 (14.1%); £3,249,053.95 -> £2,789,500.99 (14.1%); £3,249,054.13 -> £2,789,501.02 (14.1%); £3,249,054.31 -> £2,789,501.03 (14.1%); £3,249,054.36 -> £2,789,501.05 (14.1%); £3,249,054.42 -> £2,789,501.07 (14.1%); £3,249,054.42 -> £2,789,501.09 (14.1%); £3,249,054.43 -> £2,789,501.11 (14.1%); £3,249,054.43 -> £2,789,501.13 (14.1%); £3,249,054.43 -> £2,789,501.15 (14.1%); £3,249,054.44 -> £2,789,501.17 (14.1%); £3,249,054.44 -> £2,789,501.18 (14.1%); £3,249,054.44 -> £2,789,501.20 (14.1%); £3,249,054.45 -> £2,789,501.22 (14.1%); £3,249,054.45 -> £2,789,501.24 (14.1%); £3,249,054.46 -> £2,789,501.26 (14.1%); £3,249,054.52 -> £2,789,501.30 (14.1%); £3,249,054.68 -> £2,789,501.34 (14.1%); £3,249,054.84 -> £2,789,501.39 (14.1%); £3,249,055.00 -> £2,789,501.43 (14.1%); £3,249,055.16 -> £2,789,501.47 (14.1%); £3,249,055.32 -> £2,789,501.51 (14.1%); £3,249,055.47 -> £2,789,501.55 (14.1%); £3,249,055.62 -> £2,789,501.59 (14.1%); £3,249,055.64 -> £2,789,501.63 (14.1%); £3,249,055.65 -> £2,789,501.68 (14.1%); £3,249,055.66 -> £2,789,501.72 (14.1%); £3,249,055.68 -> £2,789,501.75 (14.1%); £3,249,055.68 -> £2,789,501.77 (14.1%); £3,249,055.69 -> £2,789,501.79 (14.1%); £3,249,055.69 -> £2,789,501.81 (14.1%); £3,249,055.70 -> £2,789,501.95 (14.1%); £3,249,055.70 -> £2,789,502.09 (14.1%); £3,249,055.70 -> £2,789,502.22 (14.1%); £3,249,055.71 -> £2,789,502.35 (14.1%); £3,249,055.71 -> £2,789,502.49 (14.1%); £3,249,055.71 -> £2,789,502.62 (14.1%); £3,249,055.71 -> £2,789,502.75 (14.1%); £3,249,055.71 -> £2,789,502.88 (14.1%); £3,249,055.71 -> £2,789,502.89 (14.1%); £3,249,055.72 -> £2,789,502.90 (14.1%); £3,249,055.72 -> £2,789,502.91 (14.1%); £3,249,055.72 -> £2,789,502.92 (14.1%); £3,249,055.72 -> £2,789,502.94 (14.1%); £3,249,055.73 -> £2,789,502.95 (14.1%); £3,249,055.75 -> £2,789,502.97 (14.1%); £3,249,055.76 -> £2,789,503.00 (14.1%); £3,249,055.78 -> £2,789,503.02 (14.1%); £3,249,055.79 -> £2,789,503.05 (14.1%); £3,249,055.81 -> £2,789,503.08 (14.1%); £3,249,055.83 -> £2,789,503.10 (14.1%); £3,249,055.84 -> £2,789,503.13 (14.1%); £3,249,055.85 -> £2,789,503.15 (14.1%); £3,249,055.85 -> £2,789,503.17 (14.1%); £3,249,055.86 -> £2,789,503.19 (14.1%); £3,249,055.86 -> £2,789,503.21 (14.1%); £3,249,055.87 -> £2,789,503.23 (14.1%); £3,249,055.87 -> £2,789,503.25 (14.1%); £3,249,055.87 -> £2,789,503.27 (14.1%); £3,249,055.88 -> £2,789,503.29 (14.1%); £3,249,055.88 -> £2,789,503.31 (14.1%); £3,249,055.89 -> £2,789,503.32 (14.1%); £3,249,055.89 -> £2,789,503.34 (14.1%); £3,249,055.89 -> £2,789,503.36 (14.1%); £3,249,055.90 -> £2,789,503.40 (14.1%); £3,249,055.91 -> £2,789,503.44 (14.1%); £3,249,055.93 -> £2,789,503.48 (14.1%); £3,249,055.94 -> £2,789,503.52 (14.1%); £3,249,055.95 -> £2,789,503.56 (14.1%); £3,249,055.97 -> £2,789,503.60 (14.1%); £3,249,055.98 -> £2,789,503.64 (14.1%); £3,249,055.99 -> £2,789,503.68 (14.1%); £3,249,056.01 -> £2,789,503.72 (14.1%); £3,249,056.02 -> £2,789,503.76 (14.1%); £3,249,056.03 -> £2,789,503.80 (14.1%); £3,249,056.04 -> £2,789,503.83 (14.1%); £3,249,056.05 -> £2,789,503.85 (14.1%); £3,249,056.05 -> £2,789,503.87 (14.1%); £3,249,056.06 -> £2,789,503.89 (14.1%); £3,249,056.06 -> £2,789,504.03 (14.1%); £3,249,056.06 -> £2,789,504.17 (14.1%); £3,249,056.07 -> £2,789,504.30 (14.1%); £3,249,056.07 -> £2,789,504.44 (14.1%); £3,249,056.07 -> £2,789,504.57 (14.1%); £3,249,056.07 -> £2,789,504.70 (14.1%); £3,249,056.07 -> £2,789,504.83 (14.1%); £3,249,056.08 -> £2,789,504.97 (14.1%); £3,249,056.08 -> £2,789,504.98 (14.1%); £3,249,056.08 -> £2,789,504.98 (14.1%); £3,249,056.08 -> £2,789,504.99 (14.1%); £3,249,056.08 -> £2,789,505.00 (14.1%); £3,249,056.08 -> £2,789,505.02 (14.1%); £3,249,056.09 -> £2,789,505.03 (14.1%); £3,249,056.10 -> £2,789,505.05 (14.1%); £3,249,056.11 -> £2,789,505.07 (14.1%); £3,249,056.13 -> £2,789,505.09 (14.1%); £3,249,056.14 -> £2,789,505.12 (14.1%); £3,249,056.15 -> £2,789,505.15 (14.1%); £3,249,056.16 -> £2,789,505.18 (14.1%); £3,249,056.17 -> £2,789,505.20 (14.1%); £3,249,056.18 -> £2,789,505.23 (14.1%); £3,249,056.19 -> £2,789,505.26 (14.1%); £3,249,056.19 -> £2,789,505.29 (14.1%); £3,249,056.20 -> £2,789,505.32 (14.1%); £3,249,056.21 -> £2,789,505.34 (14.1%); £3,249,056.21 -> £2,789,505.37 (14.1%); £3,249,056.22 -> £2,789,505.40 (14.1%); £3,249,056.22 -> £2,789,505.42 (14.1%); £3,249,056.23 -> £2,789,505.44 (14.1%); £3,249,056.23 -> £2,789,505.46 (14.1%); £3,249,056.24 -> £2,789,505.48 (14.1%); £3,249,056.24 -> £2,789,505.50 (14.1%); £3,249,056.25 -> £2,789,505.54 (14.1%); £3,249,056.26 -> £2,789,505.58 (14.1%); £3,249,056.27 -> £2,789,505.62 (14.1%); £3,249,056.28 -> £2,789,505.67 (14.1%); £3,249,056.29 -> £2,789,505.71 (14.1%); £3,249,056.30 -> £2,789,505.75 (14.1%); £3,249,056.31 -> £2,789,505.79 (14.1%); £3,249,056.32 -> £2,789,505.83 (14.1%); £3,249,056.33 -> £2,789,505.87 (14.1%); £3,249,056.34 -> £2,789,505.92 (14.1%); £3,249,056.35 -> £2,789,505.96 (14.1%); £3,249,056.37 -> £2,789,505.99 (14.1%); £3,249,056.37 -> £2,789,506.01 (14.1%); £3,249,056.38 -> £2,789,506.03 (14.1%); £3,249,056.38 -> £2,789,506.05 (14.1%); £3,249,056.38 -> £2,789,506.19 (14.1%); £3,249,056.39 -> £2,789,506.32 (14.1%); £3,249,056.39 -> £2,789,506.45 (14.1%); £3,249,056.39 -> £2,789,506.59 (14.1%); £3,249,056.39 -> £2,789,506.72 (14.1%); £3,249,056.39 -> £2,789,506.85 (14.1%); £3,249,056.40 -> £2,789,506.98 (14.1%); £3,249,056.40 -> £2,789,507.12 (14.1%); £3,249,056.40 -> £2,789,507.13 (14.1%); £3,249,056.40 -> £2,789,507.13 (14.1%); £3,249,056.40 -> £2,789,507.14 (14.1%); £3,249,056.40 -> £2,789,507.15 (14.1%); £3,249,056.40 -> £2,789,507.17 (14.1%); £3,249,056.42 -> £2,789,507.19 (14.1%); £3,249,056.43 -> £2,789,507.21 (14.1%); £3,249,056.59 -> £2,789,507.24 (14.1%); £3,249,056.75 -> £2,789,507.26 (14.1%); £3,249,056.91 -> £2,789,507.29 (14.1%); £3,249,057.07 -> £2,789,507.31 (14.1%); £3,249,057.23 -> £2,789,507.34 (14.1%); £3,249,057.39 -> £2,789,507.36 (14.1%); £3,249,057.45 -> £2,789,507.38 (14.1%); £3,249,057.50 -> £2,789,507.39 (14.1%); £3,249,057.50 -> £2,789,507.41 (14.1%); £3,249,057.50 -> £2,789,507.43 (14.1%); £3,249,057.51 -> £2,789,507.45 (14.1%); £3,249,057.51 -> £2,789,507.47 (14.1%); £3,249,057.51 -> £2,789,507.49 (14.1%); £3,249,057.52 -> £2,789,507.50 (14.1%); £3,249,057.52 -> £2,789,507.52 (14.1%); £3,249,057.52 -> £2,789,507.54 (14.1%); £3,249,057.53 -> £2,789,507.56 (14.1%); £3,249,057.53 -> £2,789,507.58 (14.1%); £3,249,057.59 -> £2,789,507.62 (14.1%); £3,249,057.74 -> £2,789,507.66 (14.1%); £3,249,057.88 -> £2,789,507.71 (14.1%); £3,249,058.03 -> £2,789,507.75 (14.1%); £3,249,058.17 -> £2,789,507.79 (14.1%); £3,249,058.32 -> £2,789,507.83 (14.1%); £3,249,058.46 -> £2,789,507.86 (14.1%); £3,249,058.60 -> £2,789,507.90 (14.1%); £3,249,058.61 -> £2,789,507.95 (14.1%); £3,249,058.62 -> £2,789,507.99 (14.1%); £3,249,058.63 -> £2,789,508.04 (14.1%); £3,249,058.64 -> £2,789,508.07 (14.1%); £3,249,058.65 -> £2,789,508.09 (14.1%); £3,249,058.65 -> £2,789,508.11 (14.1%); £3,249,058.66 -> £2,789,508.13 (14.1%); £3,249,058.66 -> £2,789,508.26 (14.1%); £3,249,058.67 -> £2,789,508.40 (14.1%); £3,249,058.67 -> £2,789,508.53 (14.1%); £3,249,058.67 -> £2,789,508.66 (14.1%); £3,249,058.67 -> £2,789,508.80 (14.1%); £3,249,058.67 -> £2,789,508.93 (14.1%); £3,249,058.67 -> £2,789,509.06 (14.1%); £3,249,058.68 -> £2,789,509.19 (14.1%); £3,249,058.68 -> £2,789,509.20 (14.1%); £3,249,058.68 -> £2,789,509.21 (14.1%); £3,249,058.68 -> £2,789,509.22 (14.1%); £3,249,058.68 -> £2,789,509.23 (14.1%); £3,249,058.68 -> £2,789,509.24 (14.1%); £3,249,058.69 -> £2,789,509.26 (14.1%); £3,249,058.70 -> £2,789,509.28 (14.1%); £3,249,058.86 -> £2,789,509.31 (14.1%); £3,249,059.01 -> £2,789,509.33 (14.1%); £3,249,059.17 -> £2,789,509.36 (14.1%); £3,249,059.32 -> £2,789,509.39 (14.1%); £3,249,059.48 -> £2,789,509.41 (14.1%); £3,249,059.63 -> £2,789,509.43 (14.1%); £3,249,059.69 -> £2,789,509.45 (14.1%); £3,249,059.74 -> £2,789,509.47 (14.1%); £3,249,059.75 -> £2,789,509.49 (14.1%); £3,249,059.75 -> £2,789,509.51 (14.1%); £3,249,059.75 -> £2,789,509.52 (14.1%); £3,249,059.76 -> £2,789,509.54 (14.1%); £3,249,059.76 -> £2,789,509.56 (14.1%); £3,249,059.76 -> £2,789,509.58 (14.1%); £3,249,059.77 -> £2,789,509.59 (14.1%); £3,249,059.77 -> £2,789,509.61 (14.1%); £3,249,059.78 -> £2,789,509.63 (14.1%); £3,249,059.78 -> £2,789,509.65 (14.1%); £3,249,059.84 -> £2,789,509.70 (14.1%); £3,249,059.99 -> £2,789,509.74 (14.1%); £3,249,060.13 -> £2,789,509.78 (14.1%); £3,249,060.28 -> £2,789,509.83 (14.1%); £3,249,060.42 -> £2,789,509.87 (14.1%); £3,249,060.56 -> £2,789,509.91 (14.1%); £3,249,060.70 -> £2,789,509.95 (14.1%); £3,249,060.84 -> £2,789,509.99 (14.1%); £3,249,060.85 -> £2,789,510.03 (14.1%); £3,249,060.86 -> £2,789,510.08 (14.1%); £3,249,060.87 -> £2,789,510.12 (14.1%); £3,249,060.89 -> £2,789,510.15 (14.1%); £3,249,060.89 -> £2,789,510.17 (14.1%); £3,249,060.90 -> £2,789,510.19 (14.1%); £3,249,060.90 -> £2,789,510.21 (14.1%); £3,249,060.90 -> £2,789,510.35 (14.1%); £3,249,060.91 -> £2,789,510.49 (14.1%); £3,249,060.91 -> £2,789,510.62 (14.1%); £3,249,060.91 -> £2,789,510.75 (14.1%); £3,249,060.91 -> £2,789,510.88 (14.1%); £3,249,060.91 -> £2,789,511.01 (14.1%); £3,249,060.92 -> £2,789,511.15 (14.1%); £3,249,060.92 -> £2,789,511.28 (14.1%); £3,249,060.92 -> £2,789,511.29 (14.1%); £3,249,060.92 -> £2,789,511.30 (14.1%); £3,249,060.92 -> £2,789,511.31 (14.1%); £3,249,060.92 -> £2,789,511.32 (14.1%); £3,249,060.93 -> £2,789,511.33 (14.1%); £3,249,060.94 -> £2,789,511.35 (14.1%); £3,249,060.95 -> £2,789,511.38 (14.1%); £3,249,061.14 -> £2,789,511.40 (14.1%); £3,249,061.34 -> £2,789,511.43 (14.1%); £3,249,061.53 -> £2,789,511.45 (14.1%); £3,249,061.72 -> £2,789,511.48 (14.1%); £3,249,061.91 -> £2,789,511.51 (14.1%); £3,249,062.10 -> £2,789,511.52 (14.1%); £3,249,062.16 -> £2,789,511.54 (14.1%); £3,249,062.21 -> £2,789,511.56 (14.1%); £3,249,062.21 -> £2,789,511.58 (14.1%); £3,249,062.22 -> £2,789,511.60 (14.1%); £3,249,062.22 -> £2,789,511.62 (14.1%); £3,249,062.23 -> £2,789,511.64 (14.1%); £3,249,062.23 -> £2,789,511.66 (14.1%); £3,249,062.23 -> £2,789,511.67 (14.1%); £3,249,062.24 -> £2,789,511.69 (14.1%); £3,249,062.24 -> £2,789,511.71 (14.1%); £3,249,062.24 -> £2,789,511.73 (14.1%); £3,249,062.25 -> £2,789,511.75 (14.1%); £3,249,062.31 -> £2,789,511.79 (14.1%); £3,249,062.47 -> £2,789,511.83 (14.1%); £3,249,062.64 -> £2,789,511.88 (14.1%); £3,249,062.81 -> £2,789,511.92 (14.1%); £3,249,062.98 -> £2,789,511.96 (14.1%); £3,249,063.15 -> £2,789,512.00 (14.1%); £3,249,063.31 -> £2,789,512.04 (14.1%); £3,249,063.47 -> £2,789,512.08 (14.1%); £3,249,063.49 -> £2,789,512.12 (14.1%); £3,249,063.50 -> £2,789,512.17 (14.1%); £3,249,063.52 -> £2,789,512.22 (14.1%); £3,249,063.53 -> £2,789,512.24 (14.1%); £3,249,063.54 -> £2,789,512.27 (14.1%); £3,249,063.54 -> £2,789,512.29 (14.1%); £3,249,063.54 -> £2,789,512.30 (14.1%); £3,249,063.55 -> £2,789,512.44 (14.1%); £3,249,063.55 -> £2,789,512.57 (14.1%); £3,249,063.55 -> £2,789,512.70 (14.1%); £3,249,063.55 -> £2,789,512.83 (14.1%); £3,249,063.55 -> £2,789,512.97 (14.1%); £3,249,063.56 -> £2,789,513.10 (14.1%); £3,249,063.56 -> £2,789,513.23 (14.1%); £3,249,063.56 -> £2,789,513.36 (14.1%); £3,249,063.56 -> £2,789,513.37 (14.1%); £3,249,063.56 -> £2,789,513.38 (14.1%); £3,249,063.56 -> £2,789,513.39 (14.1%); £3,249,063.57 -> £2,789,513.40 (14.1%); £3,249,063.57 -> £2,789,513.42 (14.1%); £3,249,063.58 -> £2,789,513.43 (14.1%); £3,249,063.59 -> £2,789,513.46 (14.1%); £3,249,063.75 -> £2,789,513.48 (14.1%); £3,249,063.91 -> £2,789,513.51 (14.1%); £3,249,064.08 -> £2,789,513.54 (14.1%); £3,249,064.24 -> £2,789,513.56 (14.1%); £3,249,064.41 -> £2,789,513.59 (14.1%); £3,249,064.57 -> £2,789,513.61 (14.1%); £3,249,064.63 -> £2,789,513.63 (14.1%); £3,249,064.68 -> £2,789,513.65 (14.1%); £3,249,064.69 -> £2,789,513.67 (14.1%); £3,249,064.69 -> £2,789,513.69 (14.1%); £3,249,064.69 -> £2,789,513.71 (14.1%); £3,249,064.70 -> £2,789,513.73 (14.1%); £3,249,064.70 -> £2,789,513.74 (14.1%); £3,249,064.71 -> £2,789,513.76 (14.1%); £3,249,064.71 -> £2,789,513.78 (14.1%); £3,249,064.71 -> £2,789,513.80 (14.1%); £3,249,064.72 -> £2,789,513.81 (14.1%); £3,249,064.72 -> £2,789,513.83 (14.1%); £3,249,064.78 -> £2,789,513.87 (14.1%); £3,249,064.92 -> £2,789,513.92 (14.1%); £3,249,065.07 -> £2,789,513.96 (14.1%); £3,249,065.22 -> £2,789,514.00 (14.1%); £3,249,065.36 -> £2,789,514.04 (14.1%); £3,249,065.50 -> £2,789,514.08 (14.1%); £3,249,065.65 -> £2,789,514.12 (14.1%); £3,249,065.78 -> £2,789,514.16 (14.1%); £3,249,065.80 -> £2,789,514.20 (14.1%); £3,249,065.81 -> £2,789,514.25 (14.1%); £3,249,065.82 -> £2,789,514.30 (14.1%); £3,249,065.83 -> £2,789,514.32 (14.1%); £3,249,065.84 -> £2,789,514.35 (14.1%); £3,249,065.84 -> £2,789,514.37 (14.1%); £3,249,065.85 -> £2,789,514.38 (14.1%); £3,249,065.85 -> £2,789,514.52 (14.1%); £3,249,065.85 -> £2,789,514.65 (14.1%); £3,249,065.85 -> £2,789,514.78 (14.1%); £3,249,065.86 -> £2,789,514.90 (14.1%); £3,249,065.86 -> £2,789,515.03 (14.1%); £3,249,065.86 -> £2,789,515.16 (14.1%); £3,249,065.86 -> £2,789,515.29 (14.1%); £3,249,065.86 -> £2,789,515.42 (14.1%); £3,249,065.86 -> £2,789,515.43 (14.1%); £3,249,065.86 -> £2,789,515.44 (14.1%); £3,249,065.86 -> £2,789,515.45 (14.1%); £3,249,065.87 -> £2,789,515.46 (14.1%); £3,249,065.87 -> £2,789,515.47 (14.1%); £3,249,065.88 -> £2,789,515.49 (14.1%); £3,249,065.88 -> £2,789,515.52 (14.1%); £3,249,066.01 -> £2,789,515.54 (14.1%); £3,249,066.13 -> £2,789,515.57 (14.1%); £3,249,066.26 -> £2,789,515.59 (14.1%); £3,249,066.39 -> £2,789,515.62 (14.1%); £3,249,066.52 -> £2,789,515.64 (14.1%); £3,249,066.65 -> £2,789,515.66 (14.1%); £3,249,066.70 -> £2,789,515.68 (14.1%); £3,249,066.75 -> £2,789,515.70 (14.1%); £3,249,066.76 -> £2,789,515.72 (14.1%); £3,249,066.76 -> £2,789,515.74 (14.1%); £3,249,066.76 -> £2,789,515.76 (14.1%); £3,249,066.77 -> £2,789,515.78 (14.1%); £3,249,066.77 -> £2,789,515.79 (14.1%); £3,249,066.78 -> £2,789,515.81 (14.1%); £3,249,066.78 -> £2,789,515.83 (14.1%); £3,249,066.78 -> £2,789,515.85 (14.1%); £3,249,066.79 -> £2,789,515.86 (14.1%); £3,249,066.79 -> £2,789,515.89 (14.1%); £3,249,066.85 -> £2,789,515.93 (14.1%); £3,249,066.97 -> £2,789,515.97 (14.1%); £3,249,067.10 -> £2,789,516.01 (14.1%); £3,249,067.22 -> £2,789,516.06 (14.1%); £3,249,067.34 -> £2,789,516.10 (14.1%); £3,249,067.46 -> £2,789,516.14 (14.1%); £3,249,067.57 -> £2,789,516.17 (14.1%); £3,249,067.69 -> £2,789,516.21 (14.1%); £3,249,067.69 -> £2,789,516.25 (14.1%); £3,249,067.70 -> £2,789,516.30 (14.1%); £3,249,067.71 -> £2,789,516.35 (14.1%); £3,249,067.72 -> £2,789,516.37 (14.1%); £3,249,067.73 -> £2,789,516.40 (14.1%); £3,249,067.73 -> £2,789,516.42 (14.1%); £3,249,067.74 -> £2,789,516.43 (14.1%); £3,249,067.74 -> £2,789,516.57 (14.1%); £3,249,067.74 -> £2,789,516.71 (14.1%); £3,249,067.75 -> £2,789,516.84 (14.1%); £3,249,067.75 -> £2,789,516.98 (14.1%); £3,249,067.75 -> £2,789,517.11 (14.1%); £3,249,067.75 -> £2,789,517.24 (14.1%); £3,249,067.75 -> £2,789,517.38 (14.1%); £3,249,067.76 -> £2,789,517.51 (14.1%); £3,249,067.76 -> £2,789,517.52 (14.1%); £3,249,067.76 -> £2,789,517.53 (14.1%); £3,249,067.76 -> £2,789,517.54 (14.1%); £3,249,067.76 -> £2,789,517.54 (14.1%); £3,249,067.76 -> £2,789,517.56 (14.1%); £3,249,067.77 -> £2,789,517.57 (14.1%); £3,249,067.78 -> £2,789,517.60 (14.1%); £3,249,067.78 -> £2,789,517.62 (14.1%); £3,249,067.79 -> £2,789,517.64 (14.1%); £3,249,067.80 -> £2,789,517.67 (14.1%); £3,249,067.81 -> £2,789,517.70 (14.1%); £3,249,067.82 -> £2,789,517.72 (14.1%); £3,249,067.83 -> £2,789,517.75 (14.1%); £3,249,067.83 -> £2,789,517.77 (14.1%); £3,249,067.84 -> £2,789,517.79 (14.1%); £3,249,067.84 -> £2,789,517.81 (14.1%); £3,249,067.85 -> £2,789,517.83 (14.1%); £3,249,067.85 -> £2,789,517.85 (14.1%); £3,249,067.86 -> £2,789,517.87 (14.1%); £3,249,067.86 -> £2,789,517.89 (14.1%); £3,249,067.87 -> £2,789,517.91 (14.1%); £3,249,067.87 -> £2,789,517.93 (14.1%); £3,249,067.88 -> £2,789,517.95 (14.1%); £3,249,067.88 -> £2,789,517.97 (14.1%); £3,249,067.89 -> £2,789,517.99 (14.1%); £3,249,067.89 -> £2,789,518.03 (14.1%); £3,249,067.90 -> £2,789,518.06 (14.1%); £3,249,067.91 -> £2,789,518.10 (14.1%); £3,249,067.92 -> £2,789,518.14 (14.1%); £3,249,067.92 -> £2,789,518.18 (14.1%); £3,249,067.93 -> £2,789,518.22 (14.1%); £3,249,067.94 -> £2,789,518.26 (14.1%); £3,249,067.95 -> £2,789,518.30 (14.1%); £3,249,067.95 -> £2,789,518.34 (14.1%); £3,249,067.96 -> £2,789,518.38 (14.1%); £3,249,067.97 -> £2,789,518.42 (14.1%); £3,249,067.98 -> £2,789,518.44 (14.1%); £3,249,067.98 -> £2,789,518.47 (14.1%); £3,249,067.99 -> £2,789,518.49 (14.1%); £3,249,067.99 -> £2,789,518.51 (14.1%); £3,249,068.00 -> £2,789,518.64 (14.1%); £3,249,068.00 -> £2,789,518.78 (14.1%); £3,249,068.00 -> £2,789,518.91 (14.1%); £3,249,068.01 -> £2,789,519.05 (14.1%); £3,249,068.01 -> £2,789,519.18 (14.1%); £3,249,068.01 -> £2,789,519.31 (14.1%); £3,249,068.01 -> £2,789,519.45 (14.1%); £3,249,068.01 -> £2,789,519.58 (14.1%); £3,249,068.01 -> £2,789,519.59 (14.1%); £3,249,068.02 -> £2,789,519.60 (14.1%); £3,249,068.02 -> £2,789,519.61 (14.1%); £3,249,068.02 -> £2,789,519.62 (14.1%); £3,249,068.02 -> £2,789,519.63 (14.1%); £3,249,068.02 -> £2,789,519.64 (14.1%); £3,249,068.02 -> £2,789,519.66 (14.1%); £3,249,068.03 -> £2,789,519.68 (14.1%); £3,249,068.03 -> £2,789,519.71 (14.1%); £3,249,068.03 -> £2,789,519.73 (14.1%); £3,249,068.04 -> £2,789,519.76 (14.1%); £3,249,068.04 -> £2,789,519.79 (14.1%); £3,249,068.04 -> £2,789,519.82 (14.1%); £3,249,068.05 -> £2,789,519.84 (14.1%); £3,249,068.06 -> £2,789,519.87 (14.1%); £3,249,068.06 -> £2,789,519.90 (14.1%); £3,249,068.07 -> £2,789,519.92 (14.1%); £3,249,068.07 -> £2,789,519.95 (14.1%); £3,249,068.08 -> £2,789,519.98 (14.1%); £3,249,068.09 -> £2,789,520.01 (14.1%); £3,249,068.10 -> £2,789,520.03 (14.1%); £3,249,068.10 -> £2,789,520.05 (14.1%); £3,249,068.11 -> £2,789,520.08 (14.1%); £3,249,068.11 -> £2,789,520.10 (14.1%); £3,249,068.12 -> £2,789,520.12 (14.1%); £3,249,068.12 -> £2,789,520.16 (14.1%); £3,249,068.13 -> £2,789,520.20 (14.1%); £3,249,068.13 -> £2,789,520.24 (14.1%); £3,249,068.14 -> £2,789,520.28 (14.1%); £3,249,068.15 -> £2,789,520.32 (14.1%); £3,249,068.15 -> £2,789,520.36 (14.1%); £3,249,068.15 -> £2,789,520.40 (14.1%); £3,249,068.16 -> £2,789,520.44 (14.1%); £3,249,068.16 -> £2,789,520.48 (14.1%); £3,249,068.17 -> £2,789,520.53 (14.1%); £3,249,068.17 -> £2,789,520.57 (14.1%); £3,249,068.18 -> £2,789,520.60 (14.1%); £3,249,068.18 -> £2,789,520.62 (14.1%); £3,249,068.19 -> £2,789,520.64 (14.1%); £3,249,068.19 -> £2,789,520.66 (14.1%); £3,249,068.19 -> £2,789,520.80 (14.1%); £3,249,068.20 -> £2,789,520.93 (14.1%); £3,249,068.20 -> £2,789,521.06 (14.1%); £3,249,068.20 -> £2,789,521.20 (14.1%); £3,249,068.20 -> £2,789,521.33 (14.1%); £3,249,068.20 -> £2,789,521.46 (14.1%); £3,249,068.21 -> £2,789,521.59 (14.1%); £3,249,068.21 -> £2,789,521.72 (14.1%); £3,249,068.21 -> £2,789,521.73 (14.1%); £3,249,068.21 -> £2,789,521.74 (14.1%); £3,249,068.21 -> £2,789,521.75 (14.1%); £3,249,068.21 -> £2,789,521.76 (14.1%); £3,249,068.21 -> £2,789,521.78 (14.1%); £3,249,068.22 -> £2,789,521.80 (14.1%); £3,249,068.22 -> £2,789,521.82 (14.1%); £3,249,068.27 -> £2,789,521.86 (14.1%); £3,249,068.34 -> £2,789,521.89 (14.1%); £3,249,068.40 -> £2,789,521.92 (14.1%); £3,249,068.46 -> £2,789,521.95 (14.1%); £3,249,068.51 -> £2,789,521.97 (14.1%); £3,249,068.56 -> £2,789,521.99 (14.1%); £3,249,068.62 -> £2,789,522.01 (14.1%); £3,249,068.67 -> £2,789,522.03 (14.1%); £3,249,068.68 -> £2,789,522.05 (14.1%); £3,249,068.68 -> £2,789,522.07 (14.1%); £3,249,068.69 -> £2,789,522.09 (14.1%); £3,249,068.69 -> £2,789,522.11 (14.1%); £3,249,068.70 -> £2,789,522.13 (14.1%); £3,249,068.70 -> £2,789,522.15 (14.1%); £3,249,068.70 -> £2,789,522.16 (14.1%); £3,249,068.71 -> £2,789,522.18 (14.1%); £3,249,068.71 -> £2,789,522.20 (14.1%); £3,249,068.72 -> £2,789,522.23 (14.1%); £3,249,068.78 -> £2,789,522.27 (14.1%); £3,249,068.85 -> £2,789,522.32 (14.1%); £3,249,068.93 -> £2,789,522.37 (14.1%); £3,249,069.00 -> £2,789,522.43 (14.1%); £3,249,069.09 -> £2,789,522.48 (14.1%); £3,249,069.17 -> £2,789,522.54 (14.1%); £3,249,069.26 -> £2,789,522.59 (14.1%); £3,249,069.35 -> £2,789,522.65 (14.1%); £3,249,069.35 -> £2,789,522.71 (14.1%); £3,249,069.36 -> £2,789,522.76 (14.1%); £3,249,069.37 -> £2,789,522.81 (14.1%); £3,249,069.37 -> £2,789,522.84 (14.1%); £3,249,069.38 -> £2,789,522.87 (14.1%); £3,249,069.38 -> £2,789,522.89 (14.1%); £3,249,069.39 -> £2,789,522.91 (14.1%); £3,249,069.39 -> £2,789,523.04 (14.1%); £3,249,069.39 -> £2,789,523.18 (14.1%); £3,249,069.40 -> £2,789,523.31 (14.1%); £3,249,069.40 -> £2,789,523.44 (14.1%); £3,249,069.40 -> £2,789,523.58 (14.1%); £3,249,069.40 -> £2,789,523.71 (14.1%); £3,249,069.40 -> £2,789,523.84 (14.1%); £3,249,069.40 -> £2,789,523.97 (14.1%); £3,249,069.40 -> £2,789,523.98 (14.1%); £3,249,069.41 -> £2,789,523.99 (14.1%); £3,249,069.41 -> £2,789,524.00 (14.1%); £3,249,069.41 -> £2,789,524.01 (14.1%); £3,249,069.41 -> £2,789,524.02 (14.1%); £3,249,069.41 -> £2,789,524.05 (14.1%); £3,249,069.42 -> £2,789,524.07 (14.1%); £3,249,069.47 -> £2,789,524.10 (14.1%); £3,249,069.54 -> £2,789,524.14 (14.1%); £3,249,069.61 -> £2,789,524.17 (14.1%); £3,249,069.67 -> £2,789,524.19 (14.1%); £3,249,069.73 -> £2,789,524.22 (14.1%); £3,249,069.79 -> £2,789,524.24 (14.1%); £3,249,069.84 -> £2,789,524.26 (14.1%); £3,249,069.90 -> £2,789,524.28 (14.1%); £3,249,069.90 -> £2,789,524.30 (14.1%); £3,249,069.91 -> £2,789,524.32 (14.1%); £3,249,069.91 -> £2,789,524.34 (14.1%); £3,249,069.92 -> £2,789,524.36 (14.1%); £3,249,069.92 -> £2,789,524.38 (14.1%); £3,249,069.93 -> £2,789,524.40 (14.1%); £3,249,069.93 -> £2,789,524.41 (14.1%); £3,249,069.93 -> £2,789,524.43 (14.1%); £3,249,069.94 -> £2,789,524.45 (14.1%); £3,249,069.94 -> £2,789,524.47 (14.1%); £3,249,070.01 -> £2,789,524.52 (14.1%); £3,249,070.08 -> £2,789,524.57 (14.1%); £3,249,070.16 -> £2,789,524.62 (14.1%); £3,249,070.24 -> £2,789,524.67 (14.1%); £3,249,070.33 -> £2,789,524.73 (14.1%); £3,249,070.41 -> £2,789,524.78 (14.1%); £3,249,070.51 -> £2,789,524.84 (14.1%); £3,249,070.60 -> £2,789,524.90 (14.1%); £3,249,070.60 -> £2,789,524.95 (14.1%); £3,249,070.61 -> £2,789,525.01 (14.1%); £3,249,070.62 -> £2,789,525.06 (14.1%); £3,249,070.62 -> £2,789,525.09 (14.1%); £3,249,070.63 -> £2,789,525.12 (14.1%); £3,249,070.63 -> £2,789,525.14 (14.1%); £3,249,070.64 -> £2,789,525.15 (14.1%); £3,249,070.64 -> £2,789,525.28 (14.1%); £3,249,070.64 -> £2,789,525.41 (14.1%); £3,249,070.64 -> £2,789,525.55 (14.1%); £3,249,070.65 -> £2,789,525.68 (14.1%); £3,249,070.65 -> £2,789,525.81 (14.1%); £3,249,070.65 -> £2,789,525.94 (14.1%); £3,249,070.65 -> £2,789,526.07 (14.1%); £3,249,070.65 -> £2,789,526.21 (14.1%); £3,249,070.65 -> £2,789,526.22 (14.1%); £3,249,070.65 -> £2,789,526.22 (14.1%); £3,249,070.66 -> £2,789,526.23 (14.1%); £3,249,070.66 -> £2,789,526.24 (14.1%); £3,249,070.66 -> £2,789,526.26 (14.1%); £3,249,070.66 -> £2,789,526.28 (14.1%); £3,249,070.66 -> £2,789,526.31 (14.1%); £3,249,070.72 -> £2,789,526.34 (14.1%); £3,249,070.78 -> £2,789,526.37 (14.1%); £3,249,070.84 -> £2,789,526.40 (14.1%); £3,249,070.90 -> £2,789,526.43 (14.1%); £3,249,070.96 -> £2,789,526.46 (14.1%); £3,249,071.01 -> £2,789,526.48 (14.1%); £3,249,071.06 -> £2,789,526.50 (14.1%); £3,249,071.12 -> £2,789,526.52 (14.1%); £3,249,071.12 -> £2,789,526.54 (14.1%); £3,249,071.13 -> £2,789,526.56 (14.1%); £3,249,071.13 -> £2,789,526.58 (14.1%); £3,249,071.14 -> £2,789,526.60 (14.1%); £3,249,071.14 -> £2,789,526.61 (14.1%); £3,249,071.14 -> £2,789,526.63 (14.1%); £3,249,071.15 -> £2,789,526.65 (14.1%); £3,249,071.15 -> £2,789,526.67 (14.1%); £3,249,071.15 -> £2,789,526.69 (14.1%); £3,249,071.16 -> £2,789,526.71 (14.1%); £3,249,071.22 -> £2,789,526.76 (14.1%); £3,249,071.29 -> £2,789,526.80 (14.1%); £3,249,071.37 -> £2,789,526.85 (14.1%); £3,249,071.45 -> £2,789,526.91 (14.1%); £3,249,071.53 -> £2,789,526.96 (14.1%); £3,249,071.61 -> £2,789,527.02 (14.1%); £3,249,071.70 -> £2,789,527.07 (14.1%); £3,249,071.79 -> £2,789,527.13 (14.1%); £3,249,071.79 -> £2,789,527.19 (14.1%); £3,249,071.80 -> £2,789,527.24 (14.1%); £3,249,071.81 -> £2,789,527.29 (14.1%); £3,249,071.81 -> £2,789,527.32 (14.1%); £3,249,071.82 -> £2,789,527.35 (14.1%); £3,249,071.82 -> £2,789,527.37 (14.1%); £3,249,071.83 -> £2,789,527.39 (14.1%); £3,249,071.83 -> £2,789,527.52 (14.1%); £3,249,071.84 -> £2,789,527.66 (14.1%); £3,249,071.84 -> £2,789,527.79 (14.1%); £3,249,071.84 -> £2,789,527.92 (14.1%); £3,249,071.84 -> £2,789,528.05 (14.1%); £3,249,071.84 -> £2,789,528.18 (14.1%); £3,249,071.84 -> £2,789,528.31 (14.1%); £3,249,071.84 -> £2,789,528.44 (14.1%); £3,249,071.85 -> £2,789,528.45 (14.1%); £3,249,071.85 -> £2,789,528.45 (14.1%); £3,249,071.85 -> £2,789,528.46 (14.1%); £3,249,071.85 -> £2,789,528.47 (14.1%); £3,249,071.85 -> £2,789,528.49 (14.1%); £3,249,071.85 -> £2,789,528.51 (14.1%); £3,249,071.86 -> £2,789,528.54 (14.1%); £3,249,071.91 -> £2,789,528.57 (14.1%); £3,249,071.98 -> £2,789,528.60 (14.1%); £3,249,072.04 -> £2,789,528.63 (14.1%); £3,249,072.09 -> £2,789,528.66 (14.1%); £3,249,072.15 -> £2,789,528.69 (14.1%); £3,249,072.20 -> £2,789,528.71 (14.1%); £3,249,072.26 -> £2,789,528.73 (14.1%); £3,249,072.31 -> £2,789,528.74 (14.1%); £3,249,072.31 -> £2,789,528.76 (14.1%); £3,249,072.32 -> £2,789,528.78 (14.1%); £3,249,072.32 -> £2,789,528.80 (14.1%); £3,249,072.33 -> £2,789,528.82 (14.1%); £3,249,072.33 -> £2,789,528.84 (14.1%); £3,249,072.34 -> £2,789,528.86 (14.1%); £3,249,072.34 -> £2,789,528.88 (14.1%); £3,249,072.34 -> £2,789,528.90 (14.1%); £3,249,072.35 -> £2,789,528.92 (14.1%); £3,249,072.35 -> £2,789,528.94 (14.1%); £3,249,072.41 -> £2,789,528.98 (14.1%); £3,249,072.48 -> £2,789,529.03 (14.1%); £3,249,072.56 -> £2,789,529.09 (14.1%); £3,249,072.64 -> £2,789,529.14 (14.1%); £3,249,072.72 -> £2,789,529.20 (14.1%); £3,249,072.81 -> £2,789,529.25 (14.1%); £3,249,072.90 -> £2,789,529.31 (14.1%); £3,249,072.98 -> £2,789,529.37 (14.1%); £3,249,072.99 -> £2,789,529.43 (14.1%); £3,249,073.00 -> £2,789,529.48 (14.1%); £3,249,073.01 -> £2,789,529.53 (14.1%); £3,249,073.01 -> £2,789,529.56 (14.1%); £3,249,073.02 -> £2,789,529.59 (14.1%); £3,249,073.02 -> £2,789,529.61 (14.1%); £3,249,073.02 -> £2,789,529.62 (14.1%); £3,249,073.03 -> £2,789,529.76 (14.1%); £3,249,073.03 -> £2,789,529.89 (14.1%); £3,249,073.03 -> £2,789,530.03 (14.1%); £3,249,073.03 -> £2,789,530.16 (14.1%); £3,249,073.04 -> £2,789,530.29 (14.1%); £3,249,073.04 -> £2,789,530.42 (14.1%); £3,249,073.04 -> £2,789,530.55 (14.1%); £3,249,073.04 -> £2,789,530.68 (14.1%); £3,249,073.04 -> £2,789,530.69 (14.1%); £3,249,073.04 -> £2,789,530.69 (14.1%); £3,249,073.04 -> £2,789,530.70 (14.1%); £3,249,073.04 -> £2,789,530.71 (14.1%); £3,249,073.05 -> £2,789,530.73 (14.1%); £3,249,073.05 -> £2,789,530.75 (14.1%); £3,249,073.05 -> £2,789,530.78 (14.1%); £3,249,073.10 -> £2,789,530.81 (14.1%); £3,249,073.17 -> £2,789,530.84 (14.1%); £3,249,073.23 -> £2,789,530.87 (14.1%); £3,249,073.28 -> £2,789,530.90 (14.1%); £3,249,073.34 -> £2,789,530.92 (14.1%); £3,249,073.39 -> £2,789,530.94 (14.1%); £3,249,073.44 -> £2,789,530.96 (14.1%); £3,249,073.50 -> £2,789,530.98 (14.1%); £3,249,073.50 -> £2,789,531.00 (14.1%); £3,249,073.51 -> £2,789,531.02 (14.1%); £3,249,073.51 -> £2,789,531.04 (14.1%); £3,249,073.52 -> £2,789,531.06 (14.1%); £3,249,073.52 -> £2,789,531.08 (14.1%); £3,249,073.52 -> £2,789,531.10 (14.1%); £3,249,073.53 -> £2,789,531.11 (14.1%); £3,249,073.53 -> £2,789,531.13 (14.1%); £3,249,073.54 -> £2,789,531.15 (14.1%); £3,249,073.54 -> £2,789,531.17 (14.1%); £3,249,073.60 -> £2,789,531.22 (14.1%); £3,249,073.67 -> £2,789,531.27 (14.1%); £3,249,073.75 -> £2,789,531.32 (14.1%); £3,249,073.82 -> £2,789,531.37 (14.1%); £3,249,073.90 -> £2,789,531.42 (14.1%); £3,249,073.99 -> £2,789,531.48 (14.1%); £3,249,074.07 -> £2,789,531.53 (14.1%); £3,249,074.16 -> £2,789,531.59 (14.1%); £3,249,074.17 -> £2,789,531.64 (14.1%); £3,249,074.17 -> £2,789,531.70 (14.1%); £3,249,074.18 -> £2,789,531.75 (14.1%); £3,249,074.18 -> £2,789,531.78 (14.1%); £3,249,074.19 -> £2,789,531.80 (14.1%); £3,249,074.19 -> £2,789,531.82 (14.1%); £3,249,074.20 -> £2,789,531.84 (14.1%); £3,249,074.20 -> £2,789,531.97 (14.1%); £3,249,074.20 -> £2,789,532.10 (14.1%); £3,249,074.20 -> £2,789,532.23 (14.1%); £3,249,074.21 -> £2,789,532.36 (14.1%); £3,249,074.21 -> £2,789,532.49 (14.1%); £3,249,074.21 -> £2,789,532.62 (14.1%); £3,249,074.21 -> £2,789,532.75 (14.1%); £3,249,074.21 -> £2,789,532.89 (14.1%); £3,249,074.21 -> £2,789,532.89 (14.1%); £3,249,074.21 -> £2,789,532.90 (14.1%); £3,249,074.22 -> £2,789,532.91 (14.1%); £3,249,074.22 -> £2,789,532.92 (14.1%); £3,249,074.22 -> £2,789,532.94 (14.1%); £3,249,074.22 -> £2,789,532.95 (14.1%); £3,249,074.22 -> £2,789,532.97 (14.1%); £3,249,074.22 -> £2,789,533.00 (14.1%); £3,249,074.23 -> £2,789,533.03 (14.1%); £3,249,074.23 -> £2,789,533.06 (14.1%); £3,249,074.23 -> £2,789,533.09 (14.1%); £3,249,074.24 -> £2,789,533.12 (14.1%); £3,249,074.24 -> £2,789,533.14 (14.1%); £3,249,074.25 -> £2,789,533.17 (14.1%); £3,249,074.25 -> £2,789,533.19 (14.1%); £3,249,074.26 -> £2,789,533.21 (14.1%); £3,249,074.26 -> £2,789,533.24 (14.1%); £3,249,074.27 -> £2,789,533.26 (14.1%); £3,249,074.27 -> £2,789,533.28 (14.1%); £3,249,074.28 -> £2,789,533.30 (14.1%); £3,249,074.28 -> £2,789,533.32 (14.1%); £3,249,074.29 -> £2,789,533.34 (14.1%); £3,249,074.29 -> £2,789,533.36 (14.1%); £3,249,074.29 -> £2,789,533.39 (14.1%); £3,249,074.30 -> £2,789,533.41 (14.1%); £3,249,074.30 -> £2,789,533.45 (14.1%); £3,249,074.31 -> £2,789,533.50 (14.1%); £3,249,074.31 -> £2,789,533.55 (14.1%); £3,249,074.32 -> £2,789,533.60 (14.1%); £3,249,074.32 -> £2,789,533.65 (14.1%); £3,249,074.33 -> £2,789,533.71 (14.1%); £3,249,074.34 -> £2,789,533.77 (14.1%); £3,249,074.34 -> £2,789,533.82 (14.1%); £3,249,074.35 -> £2,789,533.87 (14.1%); £3,249,074.35 -> £2,789,533.92 (14.1%); £3,249,074.36 -> £2,789,533.97 (14.1%); £3,249,074.36 -> £2,789,534.00 (14.1%); £3,249,074.37 -> £2,789,534.03 (14.1%); £3,249,074.37 -> £2,789,534.05 (14.1%); £3,249,074.38 -> £2,789,534.07 (14.1%); £3,249,074.38 -> £2,789,534.21 (14.1%); £3,249,074.39 -> £2,789,534.35 (14.1%); £3,249,074.39 -> £2,789,534.48 (14.1%); £3,249,074.39 -> £2,789,534.61 (14.1%); £3,249,074.39 -> £2,789,534.74 (14.1%); £3,249,074.39 -> £2,789,534.88 (14.1%); £3,249,074.40 -> £2,789,535.01 (14.1%); £3,249,074.40 -> £2,789,535.14 (14.1%); £3,249,074.40 -> £2,789,535.15 (14.1%); £3,249,074.40 -> £2,789,535.16 (14.1%); £3,249,074.40 -> £2,789,535.17 (14.1%); £3,249,074.40 -> £2,789,535.18 (14.1%); £3,249,074.40 -> £2,789,535.19 (14.1%); £3,249,074.41 -> £2,789,535.20 (14.1%); £3,249,074.41 -> £2,789,535.22 (14.1%); £3,249,074.41 -> £2,789,535.24 (14.1%); £3,249,074.41 -> £2,789,535.26 (14.1%); £3,249,074.42 -> £2,789,535.29 (14.1%); £3,249,074.42 -> £2,789,535.32 (14.1%); £3,249,074.42 -> £2,789,535.36 (14.1%); £3,249,074.43 -> £2,789,535.39 (14.1%); £3,249,074.43 -> £2,789,535.41 (14.1%); £3,249,074.44 -> £2,789,535.44 (14.1%); £3,249,074.44 -> £2,789,535.47 (14.1%); £3,249,074.45 -> £2,789,535.50 (14.1%); £3,249,074.45 -> £2,789,535.53 (14.1%); £3,249,074.46 -> £2,789,535.56 (14.1%); £3,249,074.47 -> £2,789,535.59 (14.1%); £3,249,074.47 -> £2,789,535.61 (14.1%); £3,249,074.48 -> £2,789,535.64 (14.1%); £3,249,074.48 -> £2,789,535.66 (14.1%); £3,249,074.49 -> £2,789,535.68 (14.1%); £3,249,074.49 -> £2,789,535.70 (14.1%); £3,249,074.49 -> £2,789,535.75 (14.1%); £3,249,074.50 -> £2,789,535.79 (14.1%); £3,249,074.51 -> £2,789,535.84 (14.1%); £3,249,074.51 -> £2,789,535.90 (14.1%); £3,249,074.52 -> £2,789,535.95 (14.1%); £3,249,074.53 -> £2,789,536.01 (14.1%); £3,249,074.53 -> £2,789,536.07 (14.1%); £3,249,074.54 -> £2,789,536.12 (14.1%); £3,249,074.54 -> £2,789,536.18 (14.1%); £3,249,074.55 -> £2,789,536.23 (14.1%); £3,249,074.55 -> £2,789,536.28 (14.1%); £3,249,074.56 -> £2,789,536.31 (14.1%); £3,249,074.57 -> £2,789,536.34 (14.1%); £3,249,074.57 -> £2,789,536.36 (14.1%); £3,249,074.58 -> £2,789,536.37 (14.1%); £3,249,074.58 -> £2,789,536.51 (14.1%); £3,249,074.58 -> £2,789,536.64 (14.1%); £3,249,074.58 -> £2,789,536.77 (14.1%); £3,249,074.58 -> £2,789,536.90 (14.1%); £3,249,074.59 -> £2,789,537.03 (14.1%); £3,249,074.59 -> £2,789,537.16 (14.1%); £3,249,074.59 -> £2,789,537.29 (14.1%); £3,249,074.59 -> £2,789,537.42 (14.1%); £3,249,074.59 -> £2,789,537.43 (14.1%); £3,249,074.59 -> £2,789,537.44 (14.1%); £3,249,074.59 -> £2,789,537.45 (14.1%); £3,249,074.60 -> £2,789,537.46 (14.1%); £3,249,074.60 -> £2,789,537.48 (14.1%); £3,249,074.60 -> £2,789,537.50 (14.1%); £3,249,074.60 -> £2,789,537.53 (14.1%); £3,249,074.66 -> £2,789,537.56 (14.1%); £3,249,074.72 -> £2,789,537.59 (14.1%); £3,249,074.78 -> £2,789,537.62 (14.1%); £3,249,074.84 -> £2,789,537.65 (14.1%); £3,249,074.89 -> £2,789,537.68 (14.1%); £3,249,074.95 -> £2,789,537.70 (14.1%); £3,249,075.00 -> £2,789,537.72 (14.1%); £3,249,075.06 -> £2,789,537.73 (14.1%); £3,249,075.06 -> £2,789,537.75 (14.1%); £3,249,075.06 -> £2,789,537.77 (14.1%); £3,249,075.07 -> £2,789,537.79 (14.1%); £3,249,075.07 -> £2,789,537.81 (14.1%); £3,249,075.07 -> £2,789,537.83 (14.1%); £3,249,075.08 -> £2,789,537.85 (14.1%); £3,249,075.08 -> £2,789,537.86 (14.1%); £3,249,075.08 -> £2,789,537.88 (14.1%); £3,249,075.09 -> £2,789,537.90 (14.1%); £3,249,075.09 -> £2,789,537.92 (14.1%); £3,249,075.15 -> £2,789,537.97 (14.1%); £3,249,075.22 -> £2,789,538.02 (14.1%); £3,249,075.30 -> £2,789,538.07 (14.1%); £3,249,075.38 -> £2,789,538.12 (14.1%); £3,249,075.46 -> £2,789,538.18 (14.1%); £3,249,075.55 -> £2,789,538.24 (14.1%); £3,249,075.64 -> £2,789,538.29 (14.1%); £3,249,075.72 -> £2,789,538.35 (14.1%); £3,249,075.73 -> £2,789,538.41 (14.1%); £3,249,075.74 -> £2,789,538.46 (14.1%); £3,249,075.74 -> £2,789,538.52 (14.1%); £3,249,075.75 -> £2,789,538.55 (14.1%); £3,249,075.76 -> £2,789,538.57 (14.1%); £3,249,075.76 -> £2,789,538.59 (14.1%); £3,249,075.77 -> £2,789,538.61 (14.1%); £3,249,075.77 -> £2,789,538.75 (14.1%); £3,249,075.77 -> £2,789,538.88 (14.1%); £3,249,075.78 -> £2,789,539.01 (14.1%); £3,249,075.78 -> £2,789,539.14 (14.1%); £3,249,075.78 -> £2,789,539.28 (14.1%); £3,249,075.78 -> £2,789,539.41 (14.1%); £3,249,075.78 -> £2,789,539.54 (14.1%); £3,249,075.78 -> £2,789,539.67 (14.1%); £3,249,075.78 -> £2,789,539.68 (14.1%); £3,249,075.79 -> £2,789,539.69 (14.1%); £3,249,075.79 -> £2,789,539.70 (14.1%); £3,249,075.79 -> £2,789,539.71 (14.1%); £3,249,075.79 -> £2,789,539.72 (14.1%); £3,249,075.80 -> £2,789,539.74 (14.1%); £3,249,075.81 -> £2,789,539.77 (14.1%); £3,249,076.01 -> £2,789,539.80 (14.1%); £3,249,076.23 -> £2,789,539.83 (14.1%); £3,249,076.44 -> £2,789,539.86 (14.1%); £3,249,076.64 -> £2,789,539.89 (14.1%); £3,249,076.85 -> £2,789,539.92 (14.1%); £3,249,077.05 -> £2,789,539.94 (14.1%); £3,249,077.11 -> £2,789,539.96 (14.1%); £3,249,077.16 -> £2,789,539.97 (14.1%); £3,249,077.16 -> £2,789,539.99 (14.1%); £3,249,077.17 -> £2,789,540.01 (14.1%); £3,249,077.17 -> £2,789,540.03 (14.1%); £3,249,077.18 -> £2,789,540.05 (14.1%); £3,249,077.18 -> £2,789,540.07 (14.1%); £3,249,077.19 -> £2,789,540.09 (14.1%); £3,249,077.19 -> £2,789,540.11 (14.1%); £3,249,077.19 -> £2,789,540.13 (14.1%); £3,249,077.20 -> £2,789,540.14 (14.1%); £3,249,077.20 -> £2,789,540.17 (14.1%); £3,249,077.27 -> £2,789,540.21 (14.1%); £3,249,077.45 -> £2,789,540.27 (14.1%); £3,249,077.63 -> £2,789,540.32 (14.1%); £3,249,077.82 -> £2,789,540.37 (14.1%); £3,249,078.01 -> £2,789,540.43 (14.1%); £3,249,078.21 -> £2,789,540.48 (14.1%); £3,249,078.40 -> £2,789,540.54 (14.1%); £3,249,078.60 -> £2,789,540.60 (14.1%); £3,249,078.62 -> £2,789,540.66 (14.1%); £3,249,078.64 -> £2,789,540.71 (14.1%); £3,249,078.65 -> £2,789,540.76 (14.1%); £3,249,078.67 -> £2,789,540.79 (14.1%); £3,249,078.68 -> £2,789,540.82 (14.1%); £3,249,078.68 -> £2,789,540.84 (14.1%); £3,249,078.69 -> £2,789,540.85 (14.1%); £3,249,078.69 -> £2,789,540.99 (14.1%); £3,249,078.69 -> £2,789,541.13 (14.1%); £3,249,078.69 -> £2,789,541.26 (14.1%); £3,249,078.70 -> £2,789,541.39 (14.1%); £3,249,078.70 -> £2,789,541.52 (14.1%); £3,249,078.70 -> £2,789,541.66 (14.1%); £3,249,078.70 -> £2,789,541.79 (14.1%); £3,249,078.70 -> £2,789,541.92 (14.1%); £3,249,078.70 -> £2,789,541.93 (14.1%); £3,249,078.70 -> £2,789,541.94 (14.1%); £3,249,078.71 -> £2,789,541.94 (14.1%); £3,249,078.71 -> £2,789,541.95 (14.1%); £3,249,078.71 -> £2,789,541.97 (14.1%); £3,249,078.73 -> £2,789,541.99 (14.1%); £3,249,078.75 -> £2,789,542.02 (14.1%); £3,249,079.02 -> £2,789,542.05 (14.1%); £3,249,079.29 -> £2,789,542.09 (14.1%); £3,249,079.56 -> £2,789,542.12 (14.1%); £3,249,079.83 -> £2,789,542.14 (14.1%); £3,249,080.10 -> £2,789,542.17 (14.1%); £3,249,080.36 -> £2,789,542.19 (14.1%); £3,249,080.42 -> £2,789,542.21 (14.1%); £3,249,080.47 -> £2,789,542.23 (14.1%); £3,249,080.48 -> £2,789,542.25 (14.1%); £3,249,080.48 -> £2,789,542.27 (14.1%); £3,249,080.48 -> £2,789,542.29 (14.1%); £3,249,080.49 -> £2,789,542.31 (14.1%); £3,249,080.49 -> £2,789,542.33 (14.1%); £3,249,080.49 -> £2,789,542.34 (14.1%); £3,249,080.50 -> £2,789,542.36 (14.1%); £3,249,080.50 -> £2,789,542.38 (14.1%); £3,249,080.50 -> £2,789,542.40 (14.1%); £3,249,080.51 -> £2,789,542.42 (14.1%); £3,249,080.57 -> £2,789,542.47 (14.1%); £3,249,080.79 -> £2,789,542.52 (14.1%); £3,249,081.02 -> £2,789,542.57 (14.1%); £3,249,081.25 -> £2,789,542.62 (14.1%); £3,249,081.49 -> £2,789,542.68 (14.1%); £3,249,081.73 -> £2,789,542.74 (14.1%); £3,249,081.97 -> £2,789,542.79 (14.1%); £3,249,082.20 -> £2,789,542.85 (14.1%); £3,249,082.22 -> £2,789,542.91 (14.1%); £3,249,082.24 -> £2,789,542.96 (14.1%); £3,249,082.27 -> £2,789,543.01 (14.1%); £3,249,082.29 -> £2,789,543.04 (14.1%); £3,249,082.29 -> £2,789,543.07 (14.1%); £3,249,082.30 -> £2,789,543.09 (14.1%); £3,249,082.30 -> £2,789,543.11 (14.1%); £3,249,082.31 -> £2,789,543.24 (14.1%); £3,249,082.31 -> £2,789,543.38 (14.1%); £3,249,082.31 -> £2,789,543.51 (14.1%); £3,249,082.32 -> £2,789,543.64 (14.1%); £3,249,082.32 -> £2,789,543.77 (14.1%); £3,249,082.32 -> £2,789,543.91 (14.1%); £3,249,082.32 -> £2,789,544.04 (14.1%); £3,249,082.32 -> £2,789,544.17 (14.1%); £3,249,082.32 -> £2,789,544.18 (14.1%); £3,249,082.32 -> £2,789,544.19 (14.1%); £3,249,082.33 -> £2,789,544.20 (14.1%); £3,249,082.33 -> £2,789,544.21 (14.1%); £3,249,082.33 -> £2,789,544.22 (14.1%); £3,249,082.34 -> £2,789,544.25 (14.1%); £3,249,082.35 -> £2,789,544.27 (14.1%); £3,249,082.51 -> £2,789,544.31 (14.1%); £3,249,082.68 -> £2,789,544.34 (14.1%); £3,249,082.85 -> £2,789,544.37 (14.1%); £3,249,083.01 -> £2,789,544.39 (14.1%); £3,249,083.17 -> £2,789,544.42 (14.1%); £3,249,083.33 -> £2,789,544.44 (14.1%); £3,249,083.39 -> £2,789,544.46 (14.1%); £3,249,083.45 -> £2,789,544.48 (14.1%); £3,249,083.45 -> £2,789,544.50 (14.1%); £3,249,083.46 -> £2,789,544.52 (14.1%); £3,249,083.46 -> £2,789,544.54 (14.1%); £3,249,083.46 -> £2,789,544.56 (14.1%); £3,249,083.47 -> £2,789,544.58 (14.1%); £3,249,083.47 -> £2,789,544.60 (14.1%); £3,249,083.48 -> £2,789,544.61 (14.1%); £3,249,083.48 -> £2,789,544.63 (14.1%); £3,249,083.48 -> £2,789,544.65 (14.1%); £3,249,083.49 -> £2,789,544.67 (14.1%); £3,249,083.55 -> £2,789,544.72 (14.1%); £3,249,083.70 -> £2,789,544.77 (14.1%); £3,249,083.86 -> £2,789,544.82 (14.1%); £3,249,084.01 -> £2,789,544.88 (14.1%); £3,249,084.17 -> £2,789,544.93 (14.1%); £3,249,084.34 -> £2,789,544.99 (14.1%); £3,249,084.50 -> £2,789,545.05 (14.1%); £3,249,084.67 -> £2,789,545.10 (14.1%); £3,249,084.68 -> £2,789,545.16 (14.1%); £3,249,084.69 -> £2,789,545.21 (14.1%); £3,249,084.70 -> £2,789,545.26 (14.1%); £3,249,084.71 -> £2,789,545.29 (14.1%); £3,249,084.72 -> £2,789,545.32 (14.1%); £3,249,084.73 -> £2,789,545.34 (14.1%); £3,249,084.73 -> £2,789,545.36 (14.1%); £3,249,084.73 -> £2,789,545.49 (14.1%); £3,249,084.74 -> £2,789,545.62 (14.1%); £3,249,084.74 -> £2,789,545.75 (14.1%); £3,249,084.74 -> £2,789,545.88 (14.1%); £3,249,084.74 -> £2,789,546.01 (14.1%); £3,249,084.74 -> £2,789,546.14 (14.1%); £3,249,084.74 -> £2,789,546.27 (14.1%); £3,249,084.74 -> £2,789,546.40 (14.1%); £3,249,084.74 -> £2,789,546.41 (14.1%); £3,249,084.75 -> £2,789,546.42 (14.1%); £3,249,084.75 -> £2,789,546.43 (14.1%); £3,249,084.75 -> £2,789,546.44 (14.1%); £3,249,084.75 -> £2,789,546.46 (14.1%); £3,249,084.77 -> £2,789,546.48 (14.1%); £3,249,084.79 -> £2,789,546.51 (14.1%); £3,249,085.04 -> £2,789,546.54 (14.1%); £3,249,085.30 -> £2,789,546.57 (14.1%); £3,249,085.56 -> £2,789,546.60 (14.1%); £3,249,085.81 -> £2,789,546.62 (14.1%); £3,249,086.06 -> £2,789,546.65 (14.1%); £3,249,086.31 -> £2,789,546.67 (14.1%); £3,249,086.36 -> £2,789,546.69 (14.1%); £3,249,086.42 -> £2,789,546.71 (14.1%); £3,249,086.42 -> £2,789,546.73 (14.1%); £3,249,086.43 -> £2,789,546.75 (14.1%); £3,249,086.43 -> £2,789,546.77 (14.1%); £3,249,086.43 -> £2,789,546.79 (14.1%); £3,249,086.44 -> £2,789,546.80 (14.1%); £3,249,086.44 -> £2,789,546.82 (14.1%); £3,249,086.45 -> £2,789,546.84 (14.1%); £3,249,086.45 -> £2,789,546.86 (14.1%); £3,249,086.45 -> £2,789,546.88 (14.1%); £3,249,086.46 -> £2,789,546.90 (14.1%); £3,249,086.52 -> £2,789,546.95 (14.1%); £3,249,086.73 -> £2,789,547.00 (14.1%); £3,249,086.95 -> £2,789,547.05 (14.1%); £3,249,087.17 -> £2,789,547.10 (14.1%); £3,249,087.40 -> £2,789,547.15 (14.1%); £3,249,087.63 -> £2,789,547.21 (14.1%); £3,249,087.86 -> £2,789,547.27 (14.1%); £3,249,088.09 -> £2,789,547.33 (14.1%); £3,249,088.11 -> £2,789,547.38 (14.1%); £3,249,088.13 -> £2,789,547.44 (14.1%); £3,249,088.15 -> £2,789,547.49 (14.1%); £3,249,088.17 -> £2,789,547.52 (14.1%); £3,249,088.17 -> £2,789,547.54 (14.1%); £3,249,088.18 -> £2,789,547.56 (14.1%); £3,249,088.18 -> £2,789,547.58 (14.1%); £3,249,088.19 -> £2,789,547.72 (14.1%); £3,249,088.19 -> £2,789,547.85 (14.1%); £3,249,088.19 -> £2,789,547.99 (14.1%); £3,249,088.19 -> £2,789,548.12 (14.1%); £3,249,088.20 -> £2,789,548.25 (14.1%); £3,249,088.20 -> £2,789,548.39 (14.1%); £3,249,088.20 -> £2,789,548.52 (14.1%); £3,249,088.20 -> £2,789,548.65 (14.1%); £3,249,088.20 -> £2,789,548.66 (14.1%); £3,249,088.20 -> £2,789,548.67 (14.1%); £3,249,088.21 -> £2,789,548.68 (14.1%); £3,249,088.21 -> £2,789,548.69 (14.1%); £3,249,088.21 -> £2,789,548.71 (14.1%); £3,249,088.23 -> £2,789,548.72 (14.1%); £3,249,088.24 -> £2,789,548.74 (14.1%); £3,249,088.27 -> £2,789,548.77 (14.1%); £3,249,088.29 -> £2,789,548.80 (14.1%); £3,249,088.32 -> £2,789,548.83 (14.1%); £3,249,088.34 -> £2,789,548.86 (14.1%); £3,249,088.37 -> £2,789,548.89 (14.1%); £3,249,088.39 -> £2,789,548.92 (14.1%); £3,249,088.39 -> £2,789,548.94 (14.1%); £3,249,088.40 -> £2,789,548.96 (14.1%); £3,249,088.40 -> £2,789,548.98 (14.1%); £3,249,088.41 -> £2,789,549.01 (14.1%); £3,249,088.41 -> £2,789,549.03 (14.1%); £3,249,088.41 -> £2,789,549.05 (14.1%); £3,249,088.42 -> £2,789,549.08 (14.1%); £3,249,088.42 -> £2,789,549.10 (14.1%); £3,249,088.43 -> £2,789,549.11 (14.1%); £3,249,088.43 -> £2,789,549.13 (14.1%); £3,249,088.43 -> £2,789,549.16 (14.1%); £3,249,088.44 -> £2,789,549.18 (14.1%); £3,249,088.44 -> £2,789,549.22 (14.1%); £3,249,088.46 -> £2,789,549.27 (14.1%); £3,249,088.47 -> £2,789,549.32 (14.1%); £3,249,088.49 -> £2,789,549.37 (14.1%); £3,249,088.51 -> £2,789,549.42 (14.1%); £3,249,088.52 -> £2,789,549.48 (14.1%); £3,249,088.54 -> £2,789,549.54 (14.1%); £3,249,088.56 -> £2,789,549.60 (14.1%); £3,249,088.59 -> £2,789,549.65 (14.1%); £3,249,088.61 -> £2,789,549.70 (14.1%); £3,249,088.62 -> £2,789,549.75 (14.1%); £3,249,088.64 -> £2,789,549.78 (14.1%); £3,249,088.65 -> £2,789,549.80 (14.1%); £3,249,088.65 -> £2,789,549.83 (14.1%); £3,249,088.66 -> £2,789,549.85 (14.1%); £3,249,088.66 -> £2,789,549.99 (14.1%); £3,249,088.66 -> £2,789,550.13 (14.1%); £3,249,088.67 -> £2,789,550.27 (14.1%); £3,249,088.67 -> £2,789,550.40 (14.1%); £3,249,088.67 -> £2,789,550.54 (14.1%); £3,249,088.67 -> £2,789,550.67 (14.1%); £3,249,088.68 -> £2,789,550.81 (14.1%); £3,249,088.68 -> £2,789,550.94 (14.1%); £3,249,088.68 -> £2,789,550.95 (14.1%); £3,249,088.68 -> £2,789,550.96 (14.1%); £3,249,088.68 -> £2,789,550.96 (14.1%); £3,249,088.68 -> £2,789,550.97 (14.1%); £3,249,088.69 -> £2,789,550.99 (14.1%); £3,249,088.70 -> £2,789,551.00 (14.1%); £3,249,088.71 -> £2,789,551.02 (14.1%); £3,249,088.73 -> £2,789,551.04 (14.1%); £3,249,088.75 -> £2,789,551.06 (14.1%); £3,249,088.77 -> £2,789,551.09 (14.1%); £3,249,088.79 -> £2,789,551.12 (14.1%); £3,249,088.80 -> £2,789,551.16 (14.1%); £3,249,088.81 -> £2,789,551.19 (14.1%); £3,249,088.82 -> £2,789,551.21 (14.1%); £3,249,088.82 -> £2,789,551.24 (14.1%); £3,249,088.83 -> £2,789,551.27 (14.1%); £3,249,088.83 -> £2,789,551.30 (14.1%); £3,249,088.84 -> £2,789,551.33 (14.1%); £3,249,088.85 -> £2,789,551.36 (14.1%); £3,249,088.85 -> £2,789,551.39 (14.1%); £3,249,088.86 -> £2,789,551.41 (14.1%); £3,249,088.86 -> £2,789,551.43 (14.1%); £3,249,088.86 -> £2,789,551.46 (14.1%); £3,249,088.87 -> £2,789,551.48 (14.1%); £3,249,088.87 -> £2,789,551.50 (14.1%); £3,249,088.88 -> £2,789,551.54 (14.1%); £3,249,088.89 -> £2,789,551.59 (14.1%); £3,249,088.90 -> £2,789,551.64 (14.1%); £3,249,088.91 -> £2,789,551.69 (14.1%); £3,249,088.92 -> £2,789,551.74 (14.1%); £3,249,088.93 -> £2,789,551.80 (14.1%); £3,249,088.94 -> £2,789,551.85 (14.1%); £3,249,088.96 -> £2,789,551.91 (14.1%); £3,249,088.97 -> £2,789,551.97 (14.1%); £3,249,088.99 -> £2,789,552.02 (14.1%); £3,249,089.00 -> £2,789,552.07 (14.1%); £3,249,089.01 -> £2,789,552.10 (14.1%); £3,249,089.02 -> £2,789,552.13 (14.1%); £3,249,089.03 -> £2,789,552.15 (14.1%); £3,249,089.03 -> £2,789,552.16 (14.1%); £3,249,089.04 -> £2,789,552.30 (14.1%); £3,249,089.04 -> £2,789,552.43 (14.1%); £3,249,089.04 -> £2,789,552.56 (14.1%); £3,249,089.04 -> £2,789,552.69 (14.1%); £3,249,089.04 -> £2,789,552.82 (14.1%); £3,249,089.04 -> £2,789,552.95 (14.1%); £3,249,089.05 -> £2,789,553.09 (14.1%); £3,249,089.05 -> £2,789,553.22 (14.1%); £3,249,089.05 -> £2,789,553.23 (14.1%); £3,249,089.05 -> £2,789,553.24 (14.1%); £3,249,089.05 -> £2,789,553.25 (14.1%); £3,249,089.05 -> £2,789,553.26 (14.1%); £3,249,089.05 -> £2,789,553.27 (14.1%); £3,249,089.07 -> £2,789,553.29 (14.1%); £3,249,089.08 -> £2,789,553.32 (14.1%); £3,249,089.28 -> £2,789,553.35 (14.1%); £3,249,089.48 -> £2,789,553.39 (14.1%); £3,249,089.69 -> £2,789,553.42 (14.1%); £3,249,089.89 -> £2,789,553.44 (14.1%); £3,249,090.09 -> £2,789,553.47 (14.1%); £3,249,090.28 -> £2,789,553.49 (14.1%); £3,249,090.34 -> £2,789,553.51 (14.1%); £3,249,090.39 -> £2,789,553.53 (14.1%); £3,249,090.40 -> £2,789,553.55 (14.1%); £3,249,090.40 -> £2,789,553.57 (14.1%); £3,249,090.40 -> £2,789,553.59 (14.1%); £3,249,090.41 -> £2,789,553.61 (14.1%); £3,249,090.41 -> £2,789,553.63 (14.1%); £3,249,090.42 -> £2,789,553.64 (14.1%); £3,249,090.42 -> £2,789,553.66 (14.1%); £3,249,090.43 -> £2,789,553.68 (14.1%); £3,249,090.43 -> £2,789,553.70 (14.1%); £3,249,090.44 -> £2,789,553.73 (14.1%); £3,249,090.50 -> £2,789,553.77 (14.1%); £3,249,090.68 -> £2,789,553.82 (14.1%); £3,249,090.86 -> £2,789,553.87 (14.1%); £3,249,091.04 -> £2,789,553.93 (14.1%); £3,249,091.22 -> £2,789,553.98 (14.1%); £3,249,091.41 -> £2,789,554.04 (14.1%); £3,249,091.60 -> £2,789,554.10 (14.1%); £3,249,091.79 -> £2,789,554.15 (14.1%); £3,249,091.80 -> £2,789,554.21 (14.1%); £3,249,091.81 -> £2,789,554.26 (14.1%); £3,249,091.83 -> £2,789,554.32 (14.1%); £3,249,091.85 -> £2,789,554.35 (14.1%); £3,249,091.86 -> £2,789,554.37 (14.1%); £3,249,091.87 -> £2,789,554.40 (14.1%); £3,249,091.87 -> £2,789,554.41 (14.1%); £3,249,091.88 -> £2,789,554.55 (14.1%); £3,249,091.88 -> £2,789,554.69 (14.1%); £3,249,091.88 -> £2,789,554.82 (14.1%); £3,249,091.88 -> £2,789,554.96 (14.1%); £3,249,091.89 -> £2,789,555.10 (14.1%); £3,249,091.89 -> £2,789,555.23 (14.1%); £3,249,091.89 -> £2,789,555.37 (14.1%); £3,249,091.89 -> £2,789,555.51 (14.1%); £3,249,091.89 -> £2,789,555.52 (14.1%); £3,249,091.90 -> £2,789,555.53 (14.1%); £3,249,091.90 -> £2,789,555.53 (14.1%); £3,249,091.90 -> £2,789,555.54 (14.1%); £3,249,091.90 -> £2,789,555.56 (14.1%); £3,249,091.92 -> £2,789,555.58 (14.1%); £3,249,091.93 -> £2,789,555.61 (14.1%); £3,249,092.17 -> £2,789,555.64 (14.1%); £3,249,092.41 -> £2,789,555.67 (14.1%); £3,249,092.66 -> £2,789,555.70 (14.1%); £3,249,092.89 -> £2,789,555.73 (14.1%); £3,249,093.12 -> £2,789,555.76 (14.1%); £3,249,093.35 -> £2,789,555.78 (14.1%); £3,249,093.41 -> £2,789,555.79 (14.1%); £3,249,093.46 -> £2,789,555.81 (14.1%); £3,249,093.47 -> £2,789,555.83 (14.1%); £3,249,093.47 -> £2,789,555.85 (14.1%); £3,249,093.47 -> £2,789,555.87 (14.1%); £3,249,093.48 -> £2,789,555.89 (14.1%); £3,249,093.48 -> £2,789,555.91 (14.1%); £3,249,093.48 -> £2,789,555.93 (14.1%); £3,249,093.49 -> £2,789,555.94 (14.1%); £3,249,093.49 -> £2,789,555.96 (14.1%); £3,249,093.50 -> £2,789,555.98 (14.1%); £3,249,093.50 -> £2,789,556.01 (14.1%); £3,249,093.57 -> £2,789,556.05 (14.1%); £3,249,093.77 -> £2,789,556.11 (14.1%); £3,249,093.99 -> £2,789,556.16 (14.1%); £3,249,094.20 -> £2,789,556.21 (14.1%); £3,249,094.41 -> £2,789,556.27 (14.1%); £3,249,094.63 -> £2,789,556.33 (14.1%); £3,249,094.84 -> £2,789,556.38 (14.1%); £3,249,095.06 -> £2,789,556.44 (14.1%); £3,249,095.07 -> £2,789,556.50 (14.1%); £3,249,095.10 -> £2,789,556.55 (14.1%); £3,249,095.12 -> £2,789,556.61 (14.1%); £3,249,095.15 -> £2,789,556.64 (14.1%); £3,249,095.16 -> £2,789,556.67 (14.1%); £3,249,095.17 -> £2,789,556.69 (14.1%); £3,249,095.17 -> £2,789,556.71 (14.1%); £3,249,095.18 -> £2,789,556.84 (14.1%); £3,249,095.18 -> £2,789,556.98 (14.1%); £3,249,095.18 -> £2,789,557.12 (14.1%); £3,249,095.19 -> £2,789,557.26 (14.1%); £3,249,095.19 -> £2,789,557.39 (14.1%); £3,249,095.19 -> £2,789,557.53 (14.1%); £3,249,095.19 -> £2,789,557.67 (14.1%); £3,249,095.19 -> £2,789,557.81 (14.1%); £3,249,095.20 -> £2,789,557.82 (14.1%); £3,249,095.20 -> £2,789,557.83 (14.1%); £3,249,095.20 -> £2,789,557.84 (14.1%); £3,249,095.20 -> £2,789,557.85 (14.1%); £3,249,095.21 -> £2,789,557.87 (14.1%); £3,249,095.21 -> £2,789,557.89 (14.1%); £3,249,095.22 -> £2,789,557.91 (14.1%); £3,249,095.33 -> £2,789,557.95 (14.1%); £3,249,095.45 -> £2,789,557.98 (14.1%); £3,249,095.58 -> £2,789,558.01 (14.1%); £3,249,095.69 -> £2,789,558.03 (14.1%); £3,249,095.80 -> £2,789,558.06 (14.1%); £3,249,095.91 -> £2,789,558.08 (14.1%); £3,249,095.97 -> £2,789,558.10 (14.1%); £3,249,096.02 -> £2,789,558.12 (14.1%); £3,249,096.02 -> £2,789,558.14 (14.1%); £3,249,096.03 -> £2,789,558.16 (14.1%); £3,249,096.03 -> £2,789,558.18 (14.1%); £3,249,096.03 -> £2,789,558.20 (14.1%); £3,249,096.04 -> £2,789,558.21 (14.1%); £3,249,096.04 -> £2,789,558.23 (14.1%); £3,249,096.05 -> £2,789,558.25 (14.1%); £3,249,096.05 -> £2,789,558.27 (14.1%); £3,249,096.05 -> £2,789,558.29 (14.1%); £3,249,096.06 -> £2,789,558.31 (14.1%); £3,249,096.12 -> £2,789,558.36 (14.1%); £3,249,096.23 -> £2,789,558.41 (14.1%); £3,249,096.35 -> £2,789,558.46 (14.1%); £3,249,096.47 -> £2,789,558.51 (14.1%); £3,249,096.60 -> £2,789,558.57 (14.1%); £3,249,096.73 -> £2,789,558.63 (14.1%); £3,249,096.86 -> £2,789,558.68 (14.1%); £3,249,096.99 -> £2,789,558.74 (14.1%); £3,249,097.00 -> £2,789,558.79 (14.1%); £3,249,097.01 -> £2,789,558.85 (14.1%); £3,249,097.01 -> £2,789,558.90 (14.1%); £3,249,097.02 -> £2,789,558.93 (14.1%); £3,249,097.03 -> £2,789,558.95 (14.1%); £3,249,097.03 -> £2,789,558.97 (14.1%); £3,249,097.04 -> £2,789,558.99 (14.1%); £3,249,097.04 -> £2,789,559.13 (14.1%); £3,249,097.04 -> £2,789,559.27 (14.1%); £3,249,097.05 -> £2,789,559.40 (14.1%); £3,249,097.05 -> £2,789,559.54 (14.1%); £3,249,097.05 -> £2,789,559.68 (14.1%); £3,249,097.05 -> £2,789,559.82 (14.1%); £3,249,097.06 -> £2,789,559.95 (14.1%); £3,249,097.06 -> £2,789,560.09 (14.1%); £3,249,097.06 -> £2,789,560.10 (14.1%); £3,249,097.06 -> £2,789,560.11 (14.1%); £3,249,097.06 -> £2,789,560.12 (14.1%); £3,249,097.06 -> £2,789,560.13 (14.1%); £3,249,097.07 -> £2,789,560.14 (14.1%); £3,249,097.09 -> £2,789,560.16 (14.1%); £3,249,097.11 -> £2,789,560.19 (14.1%); £3,249,097.39 -> £2,789,560.23 (14.1%); £3,249,097.68 -> £2,789,560.26 (14.1%); £3,249,097.97 -> £2,789,560.29 (14.1%); £3,249,098.25 -> £2,789,560.32 (14.1%); £3,249,098.54 -> £2,789,560.34 (14.1%); £3,249,098.82 -> £2,789,560.36 (14.1%); £3,249,098.87 -> £2,789,560.38 (14.1%); £3,249,098.93 -> £2,789,560.40 (14.1%); £3,249,098.93 -> £2,789,560.42 (14.1%); £3,249,098.94 -> £2,789,560.44 (14.1%); £3,249,098.94 -> £2,789,560.46 (14.1%); £3,249,098.95 -> £2,789,560.48 (14.1%); £3,249,098.95 -> £2,789,560.50 (14.1%); £3,249,098.95 -> £2,789,560.52 (14.1%); £3,249,098.96 -> £2,789,560.54 (14.1%); £3,249,098.96 -> £2,789,560.55 (14.1%); £3,249,098.96 -> £2,789,560.57 (14.1%); £3,249,098.97 -> £2,789,560.59 (14.1%); £3,249,099.03 -> £2,789,560.64 (14.1%); £3,249,099.26 -> £2,789,560.69 (14.1%); £3,249,099.50 -> £2,789,560.74 (14.1%); £3,249,099.73 -> £2,789,560.79 (14.1%); £3,249,099.98 -> £2,789,560.85 (14.1%); £3,249,100.23 -> £2,789,560.91 (14.1%); £3,249,100.48 -> £2,789,560.96 (14.1%); £3,249,100.73 -> £2,789,561.02 (14.1%); £3,249,100.75 -> £2,789,561.08 (14.1%); £3,249,100.78 -> £2,789,561.14 (14.1%); £3,249,100.80 -> £2,789,561.19 (14.1%); £3,249,100.82 -> £2,789,561.22 (14.1%); £3,249,100.83 -> £2,789,561.25 (14.1%); £3,249,100.84 -> £2,789,561.27 (14.1%); £3,249,100.84 -> £2,789,561.28 (14.1%); £3,249,100.84 -> £2,789,561.41 (14.1%); £3,249,100.85 -> £2,789,561.55 (14.1%); £3,249,100.85 -> £2,789,561.68 (14.1%); £3,249,100.85 -> £2,789,561.82 (14.1%); £3,249,100.85 -> £2,789,561.95 (14.1%); £3,249,100.85 -> £2,789,562.08 (14.1%); £3,249,100.86 -> £2,789,562.21 (14.1%); £3,249,100.86 -> £2,789,562.34 (14.1%); £3,249,100.86 -> £2,789,562.35 (14.1%); £3,249,100.86 -> £2,789,562.36 (14.1%); £3,249,100.86 -> £2,789,562.37 (14.1%); £3,249,100.86 -> £2,789,562.38 (14.1%); £3,249,100.86 -> £2,789,562.40 (14.1%); £3,249,100.89 -> £2,789,562.42 (14.1%); £3,249,100.91 -> £2,789,562.45 (14.1%); £3,249,101.16 -> £2,789,562.48 (14.1%); £3,249,101.43 -> £2,789,562.51 (14.1%); £3,249,101.70 -> £2,789,562.54 (14.1%); £3,249,101.96 -> £2,789,562.56 (14.1%); £3,249,102.22 -> £2,789,562.59 (14.1%); £3,249,102.48 -> £2,789,562.61 (14.1%); £3,249,102.54 -> £2,789,562.63 (14.1%); £3,249,102.59 -> £2,789,562.65 (14.1%); £3,249,102.60 -> £2,789,562.67 (14.1%); £3,249,102.60 -> £2,789,562.69 (14.1%); £3,249,102.61 -> £2,789,562.71 (14.1%); £3,249,102.61 -> £2,789,562.73 (14.1%); £3,249,102.61 -> £2,789,562.75 (14.1%); £3,249,102.62 -> £2,789,562.76 (14.1%); £3,249,102.62 -> £2,789,562.78 (14.1%); £3,249,102.63 -> £2,789,562.80 (14.1%); £3,249,102.63 -> £2,789,562.82 (14.1%); £3,249,102.64 -> £2,789,562.84 (14.1%); £3,249,102.70 -> £2,789,562.89 (14.1%); £3,249,102.92 -> £2,789,562.94 (14.1%); £3,249,103.15 -> £2,789,562.99 (14.1%); £3,249,103.37 -> £2,789,563.04 (14.1%); £3,249,103.61 -> £2,789,563.10 (14.1%); £3,249,103.85 -> £2,789,563.16 (14.1%); £3,249,104.10 -> £2,789,563.22 (14.1%); £3,249,104.34 -> £2,789,563.28 (14.1%); £3,249,104.36 -> £2,789,563.34 (14.1%); £3,249,104.39 -> £2,789,563.39 (14.1%); £3,249,104.41 -> £2,789,563.44 (14.1%); £3,249,104.42 -> £2,789,563.47 (14.1%); £3,249,104.43 -> £2,789,563.50 (14.1%); £3,249,104.43 -> £2,789,563.52 (14.1%); £3,249,104.44 -> £2,789,563.53 (14.1%); £3,249,104.44 -> £2,789,563.67 (14.1%); £3,249,104.44 -> £2,789,563.81 (14.1%); £3,249,104.45 -> £2,789,563.95 (14.1%); £3,249,104.45 -> £2,789,564.08 (14.1%); £3,249,104.45 -> £2,789,564.21 (14.1%); £3,249,104.45 -> £2,789,564.34 (14.1%); £3,249,104.45 -> £2,789,564.47 (14.1%); £3,249,104.46 -> £2,789,564.61 (14.1%); £3,249,104.46 -> £2,789,564.62 (14.1%); £3,249,104.46 -> £2,789,564.63 (14.1%); £3,249,104.46 -> £2,789,564.63 (14.1%); £3,249,104.46 -> £2,789,564.64 (14.1%); £3,249,104.46 -> £2,789,564.66 (14.1%); £3,249,104.48 -> £2,789,564.67 (14.1%); £3,249,104.51 -> £2,789,564.70 (14.1%); £3,249,104.54 -> £2,789,564.72 (14.1%); £3,249,104.56 -> £2,789,564.75 (14.1%); £3,249,104.58 -> £2,789,564.78 (14.1%); £3,249,104.60 -> £2,789,564.81 (14.1%); £3,249,104.63 -> £2,789,564.84 (14.1%); £3,249,104.65 -> £2,789,564.86 (14.1%); £3,249,104.66 -> £2,789,564.89 (14.1%); £3,249,104.66 -> £2,789,564.91 (14.1%); £3,249,104.67 -> £2,789,564.93 (14.1%); £3,249,104.67 -> £2,789,564.96 (14.1%); £3,249,104.67 -> £2,789,564.98 (14.1%); £3,249,104.68 -> £2,789,565.00 (14.1%); £3,249,104.68 -> £2,789,565.02 (14.1%); £3,249,104.69 -> £2,789,565.04 (14.1%); £3,249,104.69 -> £2,789,565.06 (14.1%); £3,249,104.70 -> £2,789,565.08 (14.1%); £3,249,104.70 -> £2,789,565.11 (14.1%); £3,249,104.71 -> £2,789,565.13 (14.1%); £3,249,104.71 -> £2,789,565.17 (14.1%); £3,249,104.74 -> £2,789,565.22 (14.1%); £3,249,104.76 -> £2,789,565.27 (14.1%); £3,249,104.78 -> £2,789,565.32 (14.1%); £3,249,104.81 -> £2,789,565.38 (14.1%); £3,249,104.83 -> £2,789,565.43 (14.1%); £3,249,104.85 -> £2,789,565.49 (14.1%); £3,249,104.88 -> £2,789,565.55 (14.1%); £3,249,104.90 -> £2,789,565.60 (14.1%); £3,249,104.93 -> £2,789,565.66 (14.1%); £3,249,104.96 -> £2,789,565.71 (14.1%); £3,249,104.98 -> £2,789,565.74 (14.1%); £3,249,104.99 -> £2,789,565.76 (14.1%); £3,249,105.00 -> £2,789,565.79 (14.1%); £3,249,105.00 -> £2,789,565.81 (14.1%); £3,249,105.01 -> £2,789,565.95 (14.1%); £3,249,105.01 -> £2,789,566.10 (14.1%); £3,249,105.01 -> £2,789,566.24 (14.1%); £3,249,105.02 -> £2,789,566.38 (14.1%); £3,249,105.02 -> £2,789,566.52 (14.1%); £3,249,105.02 -> £2,789,566.66 (14.1%); £3,249,105.03 -> £2,789,566.80 (14.1%); £3,249,105.03 -> £2,789,566.94 (14.1%); £3,249,105.03 -> £2,789,566.95 (14.1%); £3,249,105.03 -> £2,789,566.95 (14.1%); £3,249,105.03 -> £2,789,566.96 (14.1%); £3,249,105.04 -> £2,789,566.97 (14.1%); £3,249,105.04 -> £2,789,566.99 (14.1%); £3,249,105.04 -> £2,789,567.00 (14.1%); £3,249,105.04 -> £2,789,567.02 (14.1%); £3,249,105.05 -> £2,789,567.04 (14.1%); £3,249,105.05 -> £2,789,567.07 (14.1%); £3,249,105.05 -> £2,789,567.10 (14.1%); £3,249,105.06 -> £2,789,567.13 (14.1%); £3,249,105.07 -> £2,789,567.17 (14.1%); £3,249,105.07 -> £2,789,567.19 (14.1%); £3,249,105.08 -> £2,789,567.22 (14.1%); £3,249,105.09 -> £2,789,567.25 (14.1%); £3,249,105.10 -> £2,789,567.28 (14.1%); £3,249,105.11 -> £2,789,567.32 (14.1%); £3,249,105.12 -> £2,789,567.35 (14.1%); £3,249,105.13 -> £2,789,567.38 (14.1%); £3,249,105.14 -> £2,789,567.41 (14.1%); £3,249,105.15 -> £2,789,567.44 (14.1%); £3,249,105.15 -> £2,789,567.46 (14.1%); £3,249,105.16 -> £2,789,567.49 (14.1%); £3,249,105.17 -> £2,789,567.51 (14.1%); £3,249,105.18 -> £2,789,567.54 (14.1%); £3,249,105.18 -> £2,789,567.58 (14.1%); £3,249,105.19 -> £2,789,567.63 (14.1%); £3,249,105.19 -> £2,789,567.68 (14.1%); £3,249,105.20 -> £2,789,567.73 (14.1%); £3,249,105.20 -> £2,789,567.78 (14.1%); £3,249,105.21 -> £2,789,567.84 (14.1%); £3,249,105.22 -> £2,789,567.90 (14.1%); £3,249,105.23 -> £2,789,567.96 (14.1%); £3,249,105.23 -> £2,789,568.02 (14.1%); £3,249,105.24 -> £2,789,568.07 (14.1%); £3,249,105.25 -> £2,789,568.13 (14.1%); £3,249,105.26 -> £2,789,568.16 (14.1%); £3,249,105.27 -> £2,789,568.18 (14.1%); £3,249,105.27 -> £2,789,568.21 (14.1%); £3,249,105.28 -> £2,789,568.22 (14.1%); £3,249,105.28 -> £2,789,568.37 (14.1%); £3,249,105.29 -> £2,789,568.51 (14.1%); £3,249,105.29 -> £2,789,568.66 (14.1%); £3,249,105.29 -> £2,789,568.80 (14.1%); £3,249,105.30 -> £2,789,568.94 (14.1%); £3,249,105.30 -> £2,789,569.08 (14.1%); £3,249,105.30 -> £2,789,569.22 (14.1%); £3,249,105.31 -> £2,789,569.37 (14.1%); £3,249,105.31 -> £2,789,569.38 (14.1%); £3,249,105.31 -> £2,789,569.39 (14.1%); £3,249,105.31 -> £2,789,569.40 (14.1%); £3,249,105.32 -> £2,789,569.41 (14.1%); £3,249,105.32 -> £2,789,569.42 (14.1%); £3,249,105.33 -> £2,789,569.44 (14.1%); £3,249,105.33 -> £2,789,569.47 (14.1%); £3,249,105.44 -> £2,789,569.50 (14.1%); £3,249,105.55 -> £2,789,569.54 (14.1%); £3,249,105.66 -> £2,789,569.56 (14.1%); £3,249,105.76 -> £2,789,569.59 (14.1%); £3,249,105.87 -> £2,789,569.62 (14.1%); £3,249,105.97 -> £2,789,569.64 (14.1%); £3,249,106.03 -> £2,789,569.66 (14.1%); £3,249,106.09 -> £2,789,569.68 (14.1%); £3,249,106.09 -> £2,789,569.70 (14.1%); £3,249,106.10 -> £2,789,569.72 (14.1%); £3,249,106.10 -> £2,789,569.74 (14.1%); £3,249,106.11 -> £2,789,569.76 (14.1%); £3,249,106.11 -> £2,789,569.78 (14.1%); £3,249,106.12 -> £2,789,569.80 (14.1%); £3,249,106.12 -> £2,789,569.82 (14.1%); £3,249,106.13 -> £2,789,569.84 (14.1%); £3,249,106.13 -> £2,789,569.86 (14.1%); £3,249,106.14 -> £2,789,569.88 (14.1%); £3,249,106.20 -> £2,789,569.93 (14.1%); £3,249,106.31 -> £2,789,569.98 (14.1%); £3,249,106.42 -> £2,789,570.03 (14.1%); £3,249,106.53 -> £2,789,570.08 (14.1%); £3,249,106.65 -> £2,789,570.14 (14.1%); £3,249,106.77 -> £2,789,570.19 (14.1%); £3,249,106.89 -> £2,789,570.25 (14.1%); £3,249,107.01 -> £2,789,570.31 (14.1%); £3,249,107.02 -> £2,789,570.36 (14.1%); £3,249,107.03 -> £2,789,570.42 (14.1%); £3,249,107.04 -> £2,789,570.47 (14.1%); £3,249,107.05 -> £2,789,570.50 (14.1%); £3,249,107.06 -> £2,789,570.52 (14.1%); £3,249,107.06 -> £2,789,570.55 (14.1%); £3,249,107.07 -> £2,789,570.56 (14.1%); £3,249,107.07 -> £2,789,570.69 (14.1%); £3,249,107.07 -> £2,789,570.83 (14.1%); £3,249,107.07 -> £2,789,570.96 (14.1%); £3,249,107.07 -> £2,789,571.10 (14.1%); £3,249,107.08 -> £2,789,571.23 (14.1%); £3,249,107.08 -> £2,789,571.36 (14.1%); £3,249,107.08 -> £2,789,571.49 (14.1%); £3,249,107.08 -> £2,789,571.62 (14.1%); £3,249,107.08 -> £2,789,571.63 (14.1%); £3,249,107.08 -> £2,789,571.64 (14.1%); £3,249,107.09 -> £2,789,571.65 (14.1%); £3,249,107.09 -> £2,789,571.66 (14.1%); £3,249,107.09 -> £2,789,571.68 (14.1%); £3,249,107.10 -> £2,789,571.70 (14.1%); £3,249,107.11 -> £2,789,571.73 (14.1%); £3,249,107.26 -> £2,789,571.76 (14.1%); £3,249,107.41 -> £2,789,571.79 (14.1%); £3,249,107.57 -> £2,789,571.82 (14.1%); £3,249,107.72 -> £2,789,571.84 (14.1%); £3,249,107.86 -> £2,789,571.87 (14.1%); £3,249,108.00 -> £2,789,571.89 (14.1%); £3,249,108.06 -> £2,789,571.91 (14.1%); £3,249,108.11 -> £2,789,571.93 (14.1%); £3,249,108.12 -> £2,789,571.95 (14.1%); £3,249,108.12 -> £2,789,571.97 (14.1%); £3,249,108.13 -> £2,789,571.99 (14.1%); £3,249,108.13 -> £2,789,572.01 (14.1%); £3,249,108.14 -> £2,789,572.03 (14.1%); £3,249,108.15 -> £2,789,572.05 (14.1%); £3,249,108.15 -> £2,789,572.07 (14.1%); £3,249,108.15 -> £2,789,572.08 (14.1%); £3,249,108.16 -> £2,789,572.10 (14.1%); £3,249,108.16 -> £2,789,572.12 (14.1%); £3,249,108.22 -> £2,789,572.17 (14.1%); £3,249,108.36 -> £2,789,572.22 (14.1%); £3,249,108.50 -> £2,789,572.27 (14.1%); £3,249,108.64 -> £2,789,572.32 (14.1%); £3,249,108.79 -> £2,789,572.38 (14.1%); £3,249,108.94 -> £2,789,572.43 (14.1%); £3,249,109.09 -> £2,789,572.49 (14.1%); £3,249,109.25 -> £2,789,572.54 (14.1%); £3,249,109.26 -> £2,789,572.60 (14.1%); £3,249,109.27 -> £2,789,572.65 (14.1%); £3,249,109.28 -> £2,789,572.70 (14.1%); £3,249,109.29 -> £2,789,572.73 (14.1%); £3,249,109.29 -> £2,789,572.76 (14.1%); £3,249,109.30 -> £2,789,572.78 (14.1%); £3,249,109.30 -> £2,789,572.79 (14.1%); £3,249,109.30 -> £2,789,572.92 (14.1%); £3,249,109.31 -> £2,789,573.05 (14.1%); £3,249,109.31 -> £2,789,573.18 (14.1%); £3,249,109.31 -> £2,789,573.30 (14.1%); £3,249,109.31 -> £2,789,573.43 (14.1%); £3,249,109.31 -> £2,789,573.56 (14.1%); £3,249,109.31 -> £2,789,573.69 (14.1%); £3,249,109.31 -> £2,789,573.82 (14.1%); £3,249,109.31 -> £2,789,573.82 (14.1%); £3,249,109.31 -> £2,789,573.83 (14.1%); £3,249,109.31 -> £2,789,573.84 (14.1%); £3,249,109.32 -> £2,789,573.85 (14.1%); £3,249,109.32 -> £2,789,573.87 (14.1%); £3,249,109.34 -> £2,789,573.89 (14.1%); £3,249,109.36 -> £2,789,573.92 (14.1%); £3,249,109.59 -> £2,789,573.95 (14.1%); £3,249,109.83 -> £2,789,573.98 (14.1%); £3,249,110.06 -> £2,789,574.01 (14.1%); £3,249,110.29 -> £2,789,574.04 (14.1%); £3,249,110.52 -> £2,789,574.06 (14.1%); £3,249,110.74 -> £2,789,574.08 (14.1%); £3,249,110.80 -> £2,789,574.10 (14.1%); £3,249,110.85 -> £2,789,574.12 (14.1%); £3,249,110.85 -> £2,789,574.14 (14.1%); £3,249,110.86 -> £2,789,574.16 (14.1%); £3,249,110.86 -> £2,789,574.18 (14.1%); £3,249,110.86 -> £2,789,574.20 (14.1%); £3,249,110.86 -> £2,789,574.21 (14.1%); £3,249,110.87 -> £2,789,574.23 (14.1%); £3,249,110.87 -> £2,789,574.25 (14.1%); £3,249,110.87 -> £2,789,574.27 (14.1%); £3,249,110.88 -> £2,789,574.29 (14.1%); £3,249,110.88 -> £2,789,574.31 (14.1%); £3,249,110.95 -> £2,789,574.36 (14.1%); £3,249,111.14 -> £2,789,574.41 (14.1%); £3,249,111.35 -> £2,789,574.46 (14.1%); £3,249,111.55 -> £2,789,574.51 (14.1%); £3,249,111.76 -> £2,789,574.57 (14.1%); £3,249,111.98 -> £2,789,574.63 (14.1%); £3,249,112.19 -> £2,789,574.69 (14.1%); £3,249,112.41 -> £2,789,574.74 (14.1%); £3,249,112.43 -> £2,789,574.80 (14.1%); £3,249,112.45 -> £2,789,574.86 (14.1%); £3,249,112.47 -> £2,789,574.91 (14.1%); £3,249,112.50 -> £2,789,574.94 (14.1%); £3,249,112.50 -> £2,789,574.97 (14.1%); £3,249,112.51 -> £2,789,574.99 (14.1%); £3,249,112.52 -> £2,789,575.01 (14.1%); £3,249,112.52 -> £2,789,575.15 (14.1%); £3,249,112.53 -> £2,789,575.29 (14.1%); £3,249,112.53 -> £2,789,575.42 (14.1%); £3,249,112.53 -> £2,789,575.55 (14.1%); £3,249,112.53 -> £2,789,575.68 (14.1%); £3,249,112.53 -> £2,789,575.81 (14.1%); £3,249,112.53 -> £2,789,575.94 (14.1%); £3,249,112.54 -> £2,789,576.06 (14.1%); £3,249,112.54 -> £2,789,576.07 (14.1%); £3,249,112.54 -> £2,789,576.08 (14.1%); £3,249,112.54 -> £2,789,576.09 (14.1%); £3,249,112.54 -> £2,789,576.10 (14.1%); £3,249,112.54 -> £2,789,576.12 (14.1%); £3,249,112.55 -> £2,789,576.14 (14.1%); £3,249,112.56 -> £2,789,576.17 (14.1%); £3,249,112.68 -> £2,789,576.20 (14.1%); £3,249,112.81 -> £2,789,576.23 (14.1%); £3,249,112.93 -> £2,789,576.26 (14.1%); £3,249,113.05 -> £2,789,576.29 (14.1%); £3,249,113.17 -> £2,789,576.31 (14.1%); £3,249,113.28 -> £2,789,576.33 (14.1%); £3,249,113.34 -> £2,789,576.35 (14.1%); £3,249,113.39 -> £2,789,576.37 (14.1%); £3,249,113.39 -> £2,789,576.39 (14.1%); £3,249,113.40 -> £2,789,576.41 (14.1%); £3,249,113.40 -> £2,789,576.43 (14.1%); £3,249,113.40 -> £2,789,576.45 (14.1%); £3,249,113.41 -> £2,789,576.46 (14.1%); £3,249,113.41 -> £2,789,576.48 (14.1%); £3,249,113.41 -> £2,789,576.50 (14.1%); £3,249,113.42 -> £2,789,576.52 (14.1%); £3,249,113.42 -> £2,789,576.54 (14.1%); £3,249,113.42 -> £2,789,576.56 (14.1%); £3,249,113.48 -> £2,789,576.60 (14.1%); £3,249,113.60 -> £2,789,576.65 (14.1%); £3,249,113.72 -> £2,789,576.70 (14.1%); £3,249,113.84 -> £2,789,576.76 (14.1%); £3,249,113.97 -> £2,789,576.81 (14.1%); £3,249,114.10 -> £2,789,576.87 (14.1%); £3,249,114.23 -> £2,789,576.92 (14.1%); £3,249,114.36 -> £2,789,576.98 (14.1%); £3,249,114.37 -> £2,789,577.04 (14.1%); £3,249,114.39 -> £2,789,577.09 (14.1%); £3,249,114.39 -> £2,789,577.14 (14.1%); £3,249,114.40 -> £2,789,577.17 (14.1%); £3,249,114.41 -> £2,789,577.20 (14.1%); £3,249,114.42 -> £2,789,577.22 (14.1%); £3,249,114.42 -> £2,789,577.23 (14.1%); £3,249,114.42 -> £2,789,577.36 (14.1%); £3,249,114.42 -> £2,789,577.49 (14.1%); £3,249,114.43 -> £2,789,577.62 (14.1%); £3,249,114.43 -> £2,789,577.75 (14.1%); £3,249,114.43 -> £2,789,577.88 (14.1%); £3,249,114.43 -> £2,789,578.01 (14.1%); £3,249,114.43 -> £2,789,578.13 (14.1%); £3,249,114.43 -> £2,789,578.27 (14.1%); £3,249,114.43 -> £2,789,578.28 (14.1%); £3,249,114.43 -> £2,789,578.29 (14.1%); £3,249,114.43 -> £2,789,578.30 (14.1%); £3,249,114.44 -> £2,789,578.31 (14.1%); £3,249,114.44 -> £2,789,578.32 (14.1%); £3,249,114.45 -> £2,789,578.34 (14.1%); £3,249,114.46 -> £2,789,578.37 (14.1%); £3,249,114.65 -> £2,789,578.41 (14.1%); £3,249,114.84 -> £2,789,578.44 (14.1%); £3,249,115.04 -> £2,789,578.47 (14.1%); £3,249,115.23 -> £2,789,578.50 (14.1%); £3,249,115.40 -> £2,789,578.52 (14.1%); £3,249,115.58 -> £2,789,578.54 (14.1%); £3,249,115.64 -> £2,789,578.56 (14.1%); £3,249,115.69 -> £2,789,578.58 (14.1%); £3,249,115.69 -> £2,789,578.60 (14.1%); £3,249,115.70 -> £2,789,578.62 (14.1%); £3,249,115.70 -> £2,789,578.64 (14.1%); £3,249,115.71 -> £2,789,578.66 (14.1%); £3,249,115.71 -> £2,789,578.68 (14.1%); £3,249,115.72 -> £2,789,578.70 (14.1%); £3,249,115.72 -> £2,789,578.72 (14.1%); £3,249,115.73 -> £2,789,578.74 (14.1%); £3,249,115.73 -> £2,789,578.76 (14.1%); £3,249,115.74 -> £2,789,578.78 (14.1%); £3,249,115.80 -> £2,789,578.82 (14.1%); £3,249,115.96 -> £2,789,578.87 (14.1%); £3,249,116.13 -> £2,789,578.92 (14.1%); £3,249,116.30 -> £2,789,578.98 (14.1%); £3,249,116.47 -> £2,789,579.03 (14.1%); £3,249,116.65 -> £2,789,579.09 (14.1%); £3,249,116.83 -> £2,789,579.15 (14.1%); £3,249,117.01 -> £2,789,579.21 (14.1%); £3,249,117.02 -> £2,789,579.27 (14.1%); £3,249,117.04 -> £2,789,579.32 (14.1%); £3,249,117.07 -> £2,789,579.38 (14.1%); £3,249,117.08 -> £2,789,579.40 (14.1%); £3,249,117.08 -> £2,789,579.43 (14.1%); £3,249,117.09 -> £2,789,579.45 (14.1%); £3,249,117.09 -> £2,789,579.47 (14.1%); £3,249,117.10 -> £2,789,579.60 (14.1%); £3,250,480.59 -> £2,789,579.73 (14.2%); £3,250,481.05 -> £2,789,581.97 (14.2%); £3,250,481.50 -> £2,789,584.30 (14.2%); £3,250,481.95 -> £2,789,586.56 (14.2%); £3,250,482.40 -> £2,789,588.87 (14.2%); £3,250,482.85 -> £2,789,591.14 (14.2%); £3,250,483.30 -> £2,789,593.44 (14.2%); £3,250,483.75 -> £2,789,595.78 (14.2%); £3,250,484.20 -> £2,789,598.08 (14.2%); £3,250,484.65 -> £2,789,600.37 (14.2%); £3,250,485.10 -> £2,789,602.61 (14.2%); £3,250,485.55 -> £2,789,604.85 (14.2%); £3,250,486.00 -> £2,789,607.11 (14.2%); £3,250,486.45 -> £2,789,609.34 (14.2%); £3,250,486.90 -> £2,789,611.59 (14.2%); £3,250,487.35 -> £2,789,613.92 (14.2%); £3,250,487.81 -> £2,789,616.24 (14.2%); £3,250,488.26 -> £2,789,618.43 (14.2%); £3,250,488.71 -> £2,789,620.66 (14.2%); £3,250,489.16 -> £2,789,622.88 (14.2%); £3,250,489.61 -> £2,789,625.14 (14.2%); £3,250,490.06 -> £2,789,627.37 (14.2%); £3,250,490.51 -> £2,789,629.61 (14.2%); £3,250,490.96 -> £2,789,631.84 (14.2%); £3,250,491.41 -> £2,789,634.04 (14.2%); £3,250,491.86 -> £2,789,636.23 (14.2%); £3,250,492.31 -> £2,789,638.43 (14.2%); £3,250,492.76 -> £2,789,640.64 (14.2%); £3,250,493.21 -> £2,789,642.84 (14.2%); £3,250,493.66 -> £2,789,645.08 (14.2%); £3,250,494.11 -> £2,789,647.76 (14.2%); £3,250,494.57 -> £2,789,650.33 (14.2%); £3,250,495.01 -> £2,789,652.89 (14.2%); £3,250,495.45 -> £2,789,655.44 (14.2%); £3,250,495.89 -> £2,789,658.05 (14.2%); £3,250,496.33 -> £2,789,660.63 (14.2%); £3,250,496.77 -> £2,789,663.21 (14.2%); £3,250,497.21 -> £2,789,665.88 (14.2%); £3,250,497.65 -> £2,789,668.48 (14.2%); £3,250,498.09 -> £2,789,671.04 (14.2%); £3,250,498.53 -> £2,789,673.58 (14.2%); £3,250,498.97 -> £2,789,676.15 (14.2%); £3,250,499.41 -> £2,789,678.75 (14.2%); £3,250,499.85 -> £2,789,681.36 (14.2%); £3,250,500.29 -> £2,789,684.00 (14.2%); £3,250,500.73 -> £2,789,686.57 (14.2%); £3,250,501.17 -> £2,789,689.16 (14.2%); £3,250,501.61 -> £2,789,691.71 (14.2%); £3,250,502.06 -> £2,789,694.25 (14.2%); £3,250,502.50 -> £2,789,696.82 (14.2%); £3,250,502.94 -> £2,789,699.41 (14.2%); £3,250,503.38 -> £2,789,702.09 (14.2%); £3,250,503.82 -> £2,789,704.65 (14.2%); £3,250,504.26 -> £2,789,707.24 (14.2%); £3,250,504.70 -> £2,789,709.81 (14.2%); £3,250,505.14 -> £2,789,712.42 (14.2%); £3,250,505.58 -> £2,789,715.02 (14.2%); £3,250,506.02 -> £2,789,717.59 (14.2%); £3,250,506.46 -> £2,789,720.25 (14.2%); £3,250,506.90 -> £2,789,722.81 (14.2%); £3,250,507.34 -> £2,789,725.36 (14.2%); £3,250,507.78 -> £2,789,727.91 (14.2%); £3,250,508.28 -> £2,789,730.42 (14.2%); £3,250,508.79 -> £2,789,732.97 (14.2%); £3,250,509.29 -> £2,789,735.46 (14.2%); £3,250,509.79 -> £2,789,738.11 (14.2%); £3,250,510.29 -> £2,789,740.69 (14.2%); £3,250,510.79 -> £2,789,743.26 (14.2%); £3,250,511.29 -> £2,789,745.78 (14.2%); £3,250,511.79 -> £2,789,748.32 (14.2%); £3,250,512.29 -> £2,789,750.91 (14.2%); £3,250,512.79 -> £2,789,753.53 (14.2%); £3,250,513.30 -> £2,789,756.21 (14.2%); £3,250,513.80 -> £2,789,758.78 (14.2%); £3,250,514.30 -> £2,789,761.36 (14.2%); £3,250,514.80 -> £2,789,763.95 (14.2%); £3,250,515.30 -> £2,789,766.52 (14.2%); £3,250,515.80 -> £2,789,769.13 (14.2%); £3,250,516.30 -> £2,789,771.74 (14.2%); £3,250,516.80 -> £2,789,774.44 (14.2%); £3,250,517.30 -> £2,789,777.05 (14.2%); £3,250,517.80 -> £2,789,779.66 (14.2%); £3,250,518.31 -> £2,789,782.29 (14.2%); £3,250,518.81 -> £2,789,784.92 (14.2%); £3,250,519.31 -> £2,789,787.55 (14.2%); £3,250,519.81 -> £2,789,790.20 (14.2%); £3,250,520.31 -> £2,789,793.00 (14.2%); £3,250,520.81 -> £2,789,795.68 (14.2%); £3,250,521.31 -> £2,789,798.31 (14.2%); £3,250,521.81 -> £2,789,800.96 (14.2%); £3,250,522.31 -> £2,789,669.77 (14.2%); £3,250,703.39 -> £2,789,186.90 (14.2%); £3,316,394.60 -> £2,789,808.87 (15.9%)
- Bills issued: 156, average clarity 0.854, average bill shock 14.6%, bad debt provision £73,343.76, avg complaint probability 4.1%
- Solvency signal: £278,981/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £281,863.77 vs. naked (unhedged) net margin: £1,038,470.55
- hedging cost £756,606.78 vs. a fully unhedged book (commodity-only: actual net £281,863.77 vs. naked net £1,038,470.55)
  - C2: actual £860.14 vs. naked £1,965.95 -- hedging cost £1,105.81
  - C2g: actual £1,304.64 vs. naked £1,604.17 -- hedging cost £299.53
  - C4: actual £169.54 vs. naked £827.53 -- hedging cost £657.99
  - C4g: actual £221.34 vs. naked £453.80 -- hedging cost £232.45
  - C6: actual £1,684.77 vs. naked £4,496.88 -- hedging cost £2,812.11
  - C7: actual £172.95 vs. naked £1,505.30 -- hedging cost £1,332.35
  - C8: actual £1,466.60 vs. naked £3,060.53 -- hedging cost £1,593.93
  - C9: actual £1,329.10 vs. naked £2,680.81 -- hedging cost £1,351.71
  - C_IC1: actual £317,285.43 vs. naked £454,878.23 -- hedging cost £137,592.80
  - C_IC2: actual £137,194.97 vs. naked £202,379.58 -- hedging cost £65,184.61
  - C_IC3: actual £65,889.33 vs. naked £334,213.02 -- hedging cost £268,323.69
  - C_IC3g: actual £-17,160.47 vs. naked £77,607.60 -- hedging cost £94,768.08
  - C_IC4: actual £-228,554.58 vs. naked £-47,202.85 -- hedging cost £181,351.73

**Year narrative:** 2023 produced a net gain of £168,528.16 across 13 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 31 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £120,872.84 (gross £1,040,732.04, capital £13,960.19)
  - Electricity: gross £938,601.74, capital £9,142.16, net £137,423.42
  - Gas: gross £102,130.30, capital £4,818.04, net £-16,550.59
- Treasury at year end: £3,071,293.42
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C7 0.86 (avg 0.86), C8 0.90 (avg 0.90), C9 0.88 (avg 0.88), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.85 (avg 0.85), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2024-12-30 period 1, net margin £-276.23

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2024): £249,986.67
  - By billing account: C1 £1,798.33, C2 £6,360.93, C3 £2,256.20, C4 £3,084.50, C5 £6,181.05, C6 £9,054.31, C7 £5,178.94, C8 £7,304.09, C9 £6,405.25, C_IC1 £1,090,869.31, C_IC2 £530,639.99, C_IC3 £1,562,763.72, C_IC4 £17,930.06
- Bill shock events (>=20%): 26 -- C7 2024-01-31 (24%); C7 2024-02-29 (27%); C7 2024-05-31 (38%); C7 2024-09-30 (37%); C7 2024-10-31 (39%); C7 2024-11-30 (51%); C2 2024-04-30 (41%); C2g 2024-04-30 (50%); C8 2024-02-29 (23%); C8 2024-04-30 (42%); C8 2024-05-31 (51%); C8 2024-07-31 (28%); C8 2024-09-30 (82%); C8 2024-10-31 (37%); C8 2024-11-30 (65%); C9 2024-05-31 (50%); C9 2024-07-31 (37%); C9 2024-09-30 (60%); C9 2024-10-31 (23%); C9 2024-11-30 (50%); C_IC1 2024-07-31 (50%); C_IC1 2024-08-31 (69%); C_IC2 2024-06-30 (57%); C_IC2 2024-07-31 (124%); C_IC3 2024-01-31 (40%); C_IC4 2024-05-31 (25%)
- Churn risk (accounts renewing in 2024): 7 at risk (≥20% churn prob): C4 26%, C6 38%, C7 41%, C8 41%, C9 38%, C_IC3 20%, C_IC4 26%

**Pricing & Margin**

- C2 (electricity): tariff £249.39-£390.68/MWh, net margin £478.45
- C2g (gas): tariff £65.55-£147.52/MWh, net margin £611.12
- C4 (electricity): tariff £237.17/MWh, net margin £118.16
- C4g (gas): tariff £57.36/MWh, net margin £180.12
- C6 (electricity): tariff £370.09/MWh, net margin £577.34
- C7 (electricity): tariff £171.90-£354.52/MWh, net margin £176.91
- C8 (electricity): tariff £194.77-£550.08/MWh, net margin £1,053.58
- C9 (electricity): tariff £183.13-£450.41/MWh, net margin £1,011.35
- C_IC1 (electricity): tariff £-98.58-£436.97/MWh, net margin £206,845.99
- C_IC2 (electricity): tariff £-106.92-£399.18/MWh, net margin £90,659.35
- C_IC3 (electricity): tariff £76.82-£154.34/MWh, net margin £65,880.55
- C_IC3g (gas): tariff £45.36-£57.82/MWh, net margin £-17,341.82 -- **net-negative**
- C_IC4 (electricity): tariff £23.97-£113.12/MWh, net margin £-229,378.26 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,316,304.22 -> £2,789,811.63 (15.9%)
- Bills issued: 141, average clarity 0.856, average bill shock 13.7%, bad debt provision £54,826.34, avg complaint probability 4.0%
- Solvency signal: £307,129/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £73,992.94 vs. naked (unhedged) net margin: £417,168.31
- hedging cost £343,175.37 vs. a fully unhedged book (commodity-only: actual net £73,992.94 vs. naked net £417,168.31)
  - C2: actual £325.16 vs. naked £1,067.84 -- hedging cost £742.68
  - C2g: actual £377.78 vs. naked £397.10 -- hedging cost £19.32
  - C7: actual £124.87 vs. naked £746.76 -- hedging cost £621.89
  - C8: actual £771.26 vs. naked £1,753.36 -- hedging cost £982.10
  - C9: actual £551.14 vs. naked £1,524.38 -- hedging cost £973.25
  - C_IC1: actual £109,162.18 vs. naked £199,942.85 -- hedging cost £90,780.66
  - C_IC2: actual £69,408.09 vs. naked £118,184.31 -- hedging cost £48,776.23
  - C_IC3: actual £-2,933.45 vs. naked £94,474.14 -- hedging cost £97,407.59
  - C_IC3g: actual £-4,308.75 vs. naked £25,544.36 -- hedging cost £29,853.11
  - C_IC4: actual £-99,485.34 vs. naked £-26,466.80 -- hedging cost £73,018.54

**Year narrative:** 2024 produced a net gain of £120,872.84 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 26 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £-10,149.01 (gross £393,889.80, capital £9,427.03)
  - Electricity: gross £346,202.31, capital £5,923.51, net £-6,515.27
  - Gas: gross £47,687.49, capital £3,503.52, net £-3,633.73
- Treasury at year end: £3,131,320.05
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C8 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2025-06-01 period 1, net margin £-113.52

**Customer Book**

- Active accounts: 10 (C2, C2g, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 4, SME electricity: 0, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £272,559.22
  - By billing account: C1 £1,802.77, C2 £5,794.11, C3 £2,103.84, C4 £2,903.81, C5 £5,803.49, C6 £8,964.40, C7 £5,632.82, C8 £6,973.05, C9 £6,555.44, C_IC1 £1,293,692.67, C_IC2 £593,616.07, C_IC3 £1,592,622.37, C_IC4 £16,805.04
- Bill shock events (>=20%): 20 -- C7 2025-01-31 (34%); C7 2025-04-30 (38%); C7 2025-05-31 (24%); C7 2025-06-07 (80%); C2 2025-06-07 (78%); C2g 2025-06-07 (77%); C8 2025-01-31 (40%); C8 2025-02-28 (24%); C8 2025-04-30 (30%); C8 2025-05-31 (39%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (34%); C9 2025-06-07 (71%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (81%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2 20%, C8 38%, C9 38%

**Pricing & Margin**

- C2 (electricity): tariff £249.39-£279.21/MWh, net margin £129.89
- C2g (gas): tariff £65.55-£66.48/MWh, net margin £122.56
- C7 (electricity): tariff £185.70-£354.52/MWh, net margin £125.13
- C8 (electricity): tariff £194.77-£431.33/MWh, net margin £410.58
- C9 (electricity): tariff £183.13-£349.61/MWh, net margin £300.83
- C_IC1 (electricity): tariff £160.15-£305.75/MWh, net margin £59,716.92
- C_IC2 (electricity): tariff £162.59-£310.40/MWh, net margin £33,660.79
- C_IC3 (electricity): tariff £76.82-£146.66/MWh, net margin £-2,689.56 -- **net-negative**
- C_IC3g (gas): tariff £45.36/MWh, net margin £-3,756.29 -- **net-negative**
- C_IC4 (electricity): tariff £43.11-£193.69/MWh, net margin £-98,169.84 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 60, average clarity 0.803, average bill shock 22.8%, bad debt provision £23,419.17, avg complaint probability 5.6%
- Solvency signal: £391,415/customer (8 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £180.23 vs. naked (unhedged) net margin: £490.47
- hedging cost £310.24 vs. a fully unhedged book (commodity-only: actual net £180.23 vs. naked net £490.47)
  - C2: actual £47.48 vs. naked £198.19 -- hedging cost £150.70
  - C2g: actual £34.37 vs. naked £53.45 -- hedging cost £19.08
  - C8: actual £98.38 vs. naked £238.83 -- hedging cost £140.45

**Year narrative:** 2025 produced a net loss of £-10,149.01 across 10 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 20 customer(s) experienced a bill shock of >=20%.
