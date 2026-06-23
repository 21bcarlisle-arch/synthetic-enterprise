# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £2,849,234.00
  (£382,597.78 net change)
- Solvency signal (final year): £357,121/customer (8 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £17,933,254.43
  VAT remitted to HMRC: (£862,326.89) | Revenue (ex-VAT): £17,070,927.54
  Non-commodity pass-through: (£4,015,486.66)
- Gross margin: £5,187,613.34
- Capital costs: £65,095.27
- Net margin: £5,122,518.06
- Capital cost ratio: 1.3% of gross
- Net margin as % of revenue: 30.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 37
- Bills issued: 1569, average clarity 0.866,
  service quality score 0.921
- Enterprise value (CLV sum across 13 billing accounts): £5,501,192.45
- Cost to serve (whole portfolio): £85,810.45, net margin after cost to serve: £5,036,707.62
- Hedge effectiveness (whole window): hedging cost £3,770,126.75 vs. a fully unhedged book (commodity-only: actual net £382,597.78 vs. naked net £4,152,724.53)

- **2021** (crisis year): net margin £43,684.01, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £-66,017.09, 9 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £5,187,613.34, capital £65,095.27, net £5,122,518.06. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 1.3% (commodity basis, comparable to old model) / 1.3% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £43,684.01 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 30.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £5,122,518.06
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £4,152,724.53
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £3,770,126.75 vs. a fully unhedged book (commodity-only: actual net £382,597.78 vs. naked net £4,152,724.53)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £122,292.35 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £604,009.62 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £17.45 | £345.60 | £129.72 | £492.77 |
| 2017 | £37,113.69 | £0.00 | £172.74 | £560.41 | £139.55 | £37,986.39 |
| 2018 | £76,352.41 | £0.00 | £-250.79 | £381.69 | £101.48 | £76,584.79 |
| 2019 | £216,195.94 | £-36,112.79 | £224.06 | £760.52 | £350.57 | £181,418.30 |
| 2020 | £-32,709.61 | £-5,116.89 | £279.32 | £856.66 | £267.31 | £-36,423.20 |
| 2021 | £-82,116.94 | £125,577.06 | £32.69 | £418.88 | £-227.68 | £43,684.01 |
| 2022 | £-109,825.94 | £43,790.89 | £287.80 | £-139.94 | £-129.89 | £-66,017.09 |
| 2023 | £351,652.30 | £-253,415.10 | £1,017.19 | £3,035.38 | £1,246.00 | £103,535.76 |
| 2024 | £83,844.14 | £-17,341.82 | £500.16 | £2,512.80 | £671.80 | £70,187.08 |
| 2025 | £-26,042.23 | £-3,756.29 | £0.00 | £846.95 | £100.53 | £-28,851.03 |

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
| C1 | 2019-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.0800 | 0.5500 | 0.9640 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.8047 |
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
| C6 | 2022-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.1058 |
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

- **Average absolute error:** 195.8%
- **Average signed error:** +62.8% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -60.8% | 60.8% |
| 2017 | 3 | -90.1% | 90.1% |
| 2018 | 4 | +436.5% | 511.2% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | -14.0% | 147.9% |
| 2021 | 9 | -2.0% | 96.3% |
| 2022 | 7 | -7.6% | 101.2% |
| 2023 | 7 | +188.8% | 331.6% |
| 2024 | 7 | -34.9% | 121.7% |
| 2025 | 2 | -70.4% | 70.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 32.2%, abs error 235.2%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 10.2%, abs error 178.7%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 6.1% | 0.0% | 60.8% |
| 2017 | 0 | 3 | 0.0% | 2.4% | 0.0% | 90.1% |
| 2018 | 2 | 2 | 18.6% | 49.8% | 78.5% | 943.9% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 17.4% | 0.4% | 199.2% | 96.7% |
| 2021 | 3 | 6 | 60.7% | 4.8% | 141.4% | 73.7% |
| 2022 | 0 | 7 | 0.0% | 20.7% | 0.0% | 101.2% |
| 2023 | 1 | 6 | 35.2% | 15.8% | 21.5% | 383.3% |
| 2024 | 3 | 4 | 33.2% | 0.2% | 151.5% | 99.4% |
| 2025 | 1 | 1 | 11.0% | 1.6% | 45.0% | 95.9% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 12 (31%)
- **Below/at SVT (protected):** 27 (69%)
- **Mean rate vs SVT premium:** -5.3%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -3.8% | 134.7 | 140.0 |
| 2017 | 3 | 0 (0%) | -9.7% | 126.5 | 140.0 |
| 2018 | 2 | 1 (50%) | -3.2% | 147.6 | 152.5 |
| 2019 | 2 | 0 (0%) | -26.2% | 131.6 | 178.5 |
| 2020 | 5 | 0 (0%) | -23.8% | 134.7 | 176.9 |
| 2021 | 6 | 5 (83%) | +6.7% | 196.7 | 183.8 |
| 2022 | 7 | 5 (71%) | +26.9% | 345.0 | 318.4 |
| 2023 | 6 | 0 (0%) | -33.8% | 261.3 | 415.0 |
| 2024 | 4 | 0 (0%) | -7.2% | 228.9 | 246.9 |
| 2025 | 1 | 1 (100%) | +13.1% | 281.2 | 248.6 |

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
| 2016 | 17 | 12.2% | 37.0% |
| 2017 | 14 | 11.9% | 22.6% |
| 2018 | 16 | 9.9% | 23.8% |
| 2019 | 19 | 16.4% | 53.7% |
| 2020 | 22 | 18.7% | 51.7% |
| 2021 | 17 | 17.6% | 38.9% |
| 2022 | 15 | 14.0% | 59.7% |
| 2023 | 15 | 32.8% | 142.8% |
| 2024 | 14 | 12.3% | 57.4% |
| 2025 | 3 | 5.7% | 16.8% |

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
| 2016 | 3 | 0.61× | 0.79× |
| 2017 | 3 | 0.90× | 0.93× |
| 2018 | 4 | 5.11× ⚠ | 18.00× |
| 2019 | 4 | 5.25× ⚠ | 18.00× |
| 2020 | 10 | 1.48× | 6.70× |
| 2021 | 9 | 0.96× | 3.75× |
| 2022 | 7 | 1.01× | 2.28× |
| 2023 | 7 | 3.32× ⚠ | 18.00× |
| 2024 | 7 | 1.22× | 3.04× |
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
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.47 |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.19 |
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
| 2016 | 917 | 426 | 491 | 0 | 356 | 5 | 130 | +14.1% |
| 2017 | 1,621 | 848 | 774 | 0 | 624 | 10 | 140 | +8.6% |
| 2018 | 1,927 | 1,201 | 726 | 0 | 609 | 15 | 101 | +5.3% |
| 2019 | 136,169 | 105,132 | 31,037 | 15,273 | 50,131 | 1,395 | -35,762 | -26.3% |
| 2020 | 119,767 | 57,391 | 62,375 | 19,520 | 46,890 | 814 | -4,850 | -4.0% |
| 2021 | 296,682 | 97,288 | 199,395 | 22,523 | 50,386 | 1,136 | 125,349 | +42.3% |
| 2022 | 595,942 | 468,121 | 127,821 | 27,136 | 54,538 | 2,486 | 43,661 | +7.3% |
| 2023 | 298,808 | 437,786 | -138,979 | 32,320 | 80,454 | 416 | -252,169 | -84.4% |
| 2024 | 271,212 | 169,202 | 102,011 | 37,573 | 76,290 | 4,818 | -16,670 | -6.1% |
| 2025 | 128,762 | 81,097 | 47,665 | 16,774 | 31,044 | 3,504 | -3,656 | -2.8% |
| **Total** | **1,851,808** | **1,418,491** | **433,317** | **171,121** | **391,320** | **14,601** | **-143,726** | **-7.8%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b)

Treasury balance ÷ active billing accounts at each year-end.
Ofgem licence floor: £0/account (positive net assets required to hold a supply licence).
Capital adequacy target: £130/dual-fuel billing account.

| Year | Treasury £ | Billing Accounts | Net Assets/Account £ | vs Floor | vs £130 Target |
|------|-----------|-----------------|----------------------|----------|----------------|
| 2016 | 2,466,899 | 9 | 274,100 | OK | OK |
| 2017 | 2,504,736 | 10 | 250,474 | OK | OK |
| 2018 | 2,496,538 | 11 | 226,958 | OK | OK |
| 2019 | 2,601,756 | 12 | 216,813 | OK | OK |
| 2020 | 2,672,887 | 13 | 205,607 | OK | OK |
| 2021 | 2,690,333 | 12 | 224,194 | OK | OK |
| 2022 | 2,504,653 | 10 | 250,465 | OK | OK |
| 2023 | 2,583,232 | 10 | 258,323 | OK | OK |
| 2024 | 2,803,856 | 10 | 280,386 | OK | OK |
| 2025 | 2,856,969 | 8 | 357,121 | OK | OK |

End-state (2025): **£357,121/account** across 8 billing accounts — above Ofgem £130 target.




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,842 | 40,643 | 33.6% | £11,279.49 | £11,698.87 | £277.52/MWh | £145.87/MWh | +2.8% |
| C8 | 106,723 | 46,761 | 43.8% | £14,020.82 | £9,439.02 | £299.84/MWh | £157.42/MWh | +10.0% |
| C9 | 109,388 | 46,156 | 42.2% | £12,180.17 | £8,737.09 | £263.89/MWh | £138.17/MWh | +8.7% |

Total HH revenue: £67,355.46 vs flat equivalent £62,934.96 (+7.0% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 21 | 110% | C8 (2016-10-31) |
| 2017 | 27 | 85% | C8 (2017-11-30) |
| 2018 | 34 | 57% | C8 (2018-10-31) |
| 2019 | 35 | 123% | C_IC1 (2019-03-31) |
| 2020 | 33 | 132% | C_IC2 (2020-03-31) |
| 2021 | 38 | 138% | C4g (2021-10-31) |
| 2022 | 51 | 166% | C4g (2022-10-31) |
| 2023 | 31 | 131% | C_IC2 (2023-06-30) |
| 2024 | 26 | 119% | C_IC2 (2024-07-31) |
| 2025 | 20 | 81% | C_IC4 (2025-06-07) |

Total: **316** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-10-31 | C4g | +166% | no |
| 2022-04-30 | C2g | +155% | no |
| 2021-10-31 | C4g | +138% | no |
| 2020-03-31 | C_IC2 | +132% | no |
| 2023-06-30 | C_IC2 | +131% | no |
| 2019-03-31 | C_IC1 | +123% | no |
| 2024-07-31 | C_IC2 | +119% | no |
| 2016-10-31 | C8 | +110% | no |
| 2023-10-31 | C8 | +102% | no |
| 2023-07-31 | C_IC1 | +102% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 10% | 10% | 0 |
| 2017 | 4 | 14% | 23% | 1 ⚠ |
| 2018 | 4 | 20% | 22% | 2 ⚠ |
| 2019 | 4 | 2% | 8% | 0 |
| 2020 | 5 | 1% | 4% | 0 |
| 2021 | 3 | 70% | 95% | 3 ⚠ |
| 2022 | 3 | 82% | 95% | 3 ⚠ |
| 2023 | 3 | 5% | 14% | 0 |
| 2024 | 2 | 0% | 0% | 0 |
| 2025 | 1 | 3% | 3% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-09-30 | C4g | £15.5 | £57.4 (+271%) | 95% |
| 2021-12-31 | C_IC3g | £15.1 | £79.0 (+424%) | 95% |
| 2022-03-31 | C2g | £31.2 | £115.9 (+271%) | 95% |
| 2022-09-30 | C4g | £57.4 | £180.6 (+214%) | 95% |
| 2022-12-31 | C_IC3g | £79.0 | £148.5 (+88%) | 57% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 20 |
| Retained | 19 (95%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £437,264.00 |
| Margin saved (retained customers' terms) | £2,304,428.96 |
| Wasted offer cost (churned anyway) | £146.14 |
| **Net ROI of retention strategy** | **£1,867,164.95** |
| Acquisition cost avoided (retained customers) | £3,100.00 |
| **Full economic ROI (margin + acq savings)** | **£1,870,264.95** |

Missed opportunities (churns with no offer): **4** (£4,405.15 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 4 (£4,405.15 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £21746.79 | £157840.90 | £136094.11 | £0.00 |
| 2019 | 2 | 2 | £41007.73 | £296884.49 | £255876.76 | £0.00 |
| 2020 | 4 | 4 | £32078.60 | £273770.82 | £241692.21 | £386.28 |
| 2021 | 5 | 4 | £88342.29 | £334832.96 | £246490.67 | £370.80 |
| 2022 | 3 | 3 | £158400.33 | £432021.49 | £273621.15 | £0.00 |
| 2023 | 3 | 3 | £57905.79 | £405880.93 | £347975.14 | £0.00 |
| 2024 | 2 | 2 | £37782.47 | £403197.38 | £365414.91 | £3648.07 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £21746.79 | £157840.90 | £150 | £136094.11 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £13979.41 | £101029.02 | £150 | £87049.61 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £27028.31 | £195855.47 | £150 | £168827.15 | retained |
| 2020-01-01 | C_IC3 | 0.35 | 3% | £5660.47 | £15111.67 | £150 | £9451.19 | retained |
| 2020-03-01 | C_IC2 | 0.34 | 3% | £4097.07 | £92923.83 | £150 | £88826.77 | retained |
| 2020-03-31 | C_IC1 | 0.55 | 5% | £11348.54 | £138834.38 | £150 | £127485.84 | retained |
| 2020-12-31 | C_IC3 | 0.62 | 5% | £10972.52 | £26900.94 | £150 | £15928.42 | retained |
| 2021-03-31 | C_IC2 | 0.63 | 5% | £7913.98 | £89859.88 | £150 | £81945.90 | retained |
| 2021-04-30 | C_IC1 | 0.94 | 8% | £23484.12 | £166544.42 | £150 | £143060.30 | retained |
| 2021-12-30 | C5 | 0.47 | 3% | £146.14 | £1923.63 | £400 | £-146.14 | churned_despite_offer |
| 2021-12-30 | C7 | 0.41 | 3% | £99.47 | £1216.20 | £150 | £1116.73 | retained |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £56698.59 | £77212.47 | £150 | £20513.89 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £23961.80 | £73828.34 | £150 | £49866.55 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £47928.71 | £193932.55 | £150 | £146003.85 | retained |
| 2022-12-31 | C_IC3 | 0.95 | 8% | £86509.83 | £164260.59 | £150 | £77750.76 | retained |
| 2023-03-31 | C6 | 0.35 | 3% | £197.83 | £2667.34 | £400 | £2469.51 | retained |
| 2023-05-30 | C_IC2 | 0.66 | 5% | £12896.20 | £133977.13 | £150 | £121080.92 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £44811.75 | £269236.47 | £150 | £224424.72 | retained |
| 2024-06-28 | C_IC2 | 0.50 | 3% | £6076.68 | £135644.45 | £150 | £129567.77 | retained |
| 2024-07-28 | C_IC1 | 0.95 | 8% | £31705.79 | £267552.93 | £150 | £235847.14 | retained |

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

**Full-history EV:** £5,501,192.45 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £156,216.01 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £492.77 |
| 2017 | £37,986.39 |
| 2018 | £76,584.79 |
| 2019 | £181,418.30 |
| 2020 | £-36,423.20 |
| 2021 | £43,684.01 |
| 2022 | £-66,017.09 |
| 2023 | £103,535.76 | ← trailing
| 2024 | £70,187.08 | ← trailing
| 2025 | £-28,851.03 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £2,625.70 | — |
| C2 | £8,768.87 | £2,876.81 |
| C3 | £2,904.87 | — |
| C4 | £4,643.67 | £596.42 |
| C5 | £9,590.77 | — |
| C6 | £14,481.83 | £2,438.35 |
| C7 | £8,426.07 | £1,061.52 |
| C8 | £9,542.97 | £2,461.50 |
| C9 | £10,479.71 | £2,216.09 |
| C_IC1 | £1,731,045.61 | £516,208.63 |
| C_IC2 | £1,006,507.96 | £229,728.01 |
| C_IC3 | £2,663,962.06 | £-41,258.15 |
| C_IC4 | £28,212.37 | £-560,113.16 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £1,726.56 | — | — | — | £5,007.86 | — | £4,168.20 | — | — | — | — | — | — |
| 2017 | £1,932.16 | £5,749.52 | £2,627.53 | £3,471.51 | £6,817.61 | £10,541.48 | £4,505.21 | £7,878.31 | £5,891.28 | — | — | — | — |
| 2018 | £1,958.93 | £4,744.24 | £2,603.12 | £2,965.85 | £5,951.75 | £7,706.43 | £4,492.88 | £6,334.54 | £5,832.06 | £1,462,228.40 | — | — | — |
| 2019 | £1,842.71 | £4,087.87 | £2,526.56 | £3,193.83 | £6,288.69 | £8,662.24 | £5,476.25 | £5,878.56 | £6,199.81 | £1,311,380.66 | £868,520.16 | — | — |
| 2020 | £1,994.12 | £4,985.51 | £2,149.33 | £2,791.03 | £7,063.76 | £8,647.20 | £4,674.85 | £5,946.37 | £5,929.74 | £864,740.76 | £516,514.29 | £1,526,967.32 | £25,104.10 |
| 2021 | £1,845.82 | £4,509.89 | £1,960.42 | £2,482.13 | £5,845.79 | £8,231.08 | £4,587.17 | £5,768.47 | £4,898.28 | £765,743.80 | £479,192.25 | £1,496,141.56 | £20,194.44 |
| 2022 | £1,724.39 | £4,597.22 | £1,920.39 | £2,218.99 | £5,836.67 | £7,917.35 | £3,904.37 | £5,689.80 | £5,504.49 | £872,656.95 | £450,073.76 | £1,228,954.17 | £15,675.03 |
| 2023 | £1,740.15 | £5,193.93 | £2,065.68 | £2,579.56 | £5,842.75 | £8,841.75 | £4,809.04 | £6,410.41 | £5,992.71 | £978,272.86 | £499,273.59 | £1,207,129.88 | £17,574.25 |
| 2024 | £1,740.15 | £5,652.89 | £2,054.81 | £2,744.27 | £5,826.02 | £8,382.41 | £5,018.34 | £6,882.69 | £6,568.42 | £1,049,105.77 | £527,093.78 | £1,318,340.47 | £18,091.20 |
| 2025 | £1,703.64 | £5,843.80 | £1,893.87 | £2,681.87 | £5,751.48 | £8,235.65 | £5,162.24 | £6,481.97 | £6,559.05 | £1,119,399.12 | £562,270.38 | £1,510,870.45 | £17,788.53 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,767.25, range £35.57–£25,825.78.

- C1: cost to serve £389.84, net margin after CTS £1,411.04
- C1g: cost to serve £47.65, net margin after CTS £835.39
- C2: cost to serve £780.49, net margin after CTS £7,286.09
- C2g: cost to serve £164.89, net margin after CTS £3,535.30
- C3: cost to serve £263.70, net margin after CTS £1,122.03
- C3g: cost to serve £35.57, net margin after CTS £720.02
- C4: cost to serve £595.97, net margin after CTS £3,009.64
- C4g: cost to serve £190.55, net margin after CTS £2,132.51
- C5: cost to serve £867.62, net margin after CTS £8,084.86
- C6: cost to serve £1,259.99, net margin after CTS £15,522.04
- C7: cost to serve £978.70, net margin after CTS £10,974.84
- C8: cost to serve £974.63, net margin after CTS £13,223.39
- C9: cost to serve £910.06, net margin after CTS £12,434.71
- C_IC1: cost to serve £20,682.59, net margin after CTS £2,003,305.59
- C_IC2: cost to serve £11,446.04, net margin after CTS £907,709.96
- C_IC3: cost to serve £25,825.78, net margin after CTS £1,658,654.71
- C_IC3g: cost to serve £9,224.23, net margin after CTS £416,430.41
- C_IC4: cost to serve £11,172.13, net margin after CTS £21,351.71 — MARGIN_SQUEEZE (below 2% benchmark)

**Activity-Based Pricing Actions**

The following 1 customer(s) are profitable but below the 2% net-margin benchmark (MARGIN_SQUEEZE): C_IC4


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 30 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 13.7%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C4 | electricity | 2017-10-01 | £-29.11 | £562.14 | +0.2% | £113.33/MWh | £113.67/MWh |
| C_IC1 | electricity | 2018-01-31 | £-5,694.56 | £10,901.23 | +20.0% | £99.09/MWh | £132.90/MWh |
| C1 | electricity | 2018-12-31 | £-35.37 | £461.69 | +2.7% | £148.23/MWh | £154.56/MWh |
| C5 | electricity | 2018-12-31 | £-207.59 | £2,298.54 | +4.0% | £148.23/MWh | £156.24/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,300.82 | £6,376.41 | +20.0% | £123.82/MWh | £170.88/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,218.30 | £10,243.03 | +20.0% | £121.46/MWh | £165.97/MWh |
| C_IC3g | gas | 2020-01-01 | £-36,112.79 | £134,045.32 | +20.0% | £13.97/MWh | £15.92/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,904.90 | £3,444.18 | +20.0% | £96.22/MWh | £132.78/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,041.06 | £6,326.95 | +20.0% | £96.89/MWh | £110.45/MWh |
| C_IC2 | electricity | 2021-03-31 | £-3,729.85 | £5,726.15 | +20.0% | £120.96/MWh | £154.46/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,006.00 | £14,511.74 | +20.0% | £115.47/MWh | £143.78/MWh |
| C4 | electricity | 2021-09-30 | £-122.30 | £622.95 | +14.6% | £181.67/MWh | £218.11/MWh |
| C4g | gas | 2021-09-30 | £-120.01 | £340.46 | +20.0% | £44.66/MWh | £57.44/MWh |
| C1 | electricity | 2021-12-30 | £-35.37 | £523.21 | +1.8% | £247.72/MWh | £253.28/MWh |
| C5 | electricity | 2021-12-30 | £-227.33 | £2,695.44 | +3.4% | £247.72/MWh | £257.44/MWh |
| C2g | gas | 2022-03-31 | £-48.21 | £468.68 | +5.3% | £107.94/MWh | £115.89/MWh |
| C_IC2 | electricity | 2022-04-30 | £-1,292.09 | £17,661.75 | +2.3% | £273.88/MWh | £294.93/MWh |
| C_IC1 | electricity | 2022-05-30 | £-4,406.97 | £22,384.38 | +14.7% | £252.29/MWh | £297.41/MWh |
| C9 | electricity | 2022-06-30 | £-170.27 | £1,951.48 | +3.7% | £296.06/MWh | £306.65/MWh |
| C4 | electricity | 2022-09-30 | £-175.51 | £1,233.82 | +9.2% | £321.02/MWh | £338.81/MWh |
| C4g | gas | 2022-09-30 | £-298.32 | £1,263.58 | +18.6% | £142.76/MWh | £180.61/MWh |
| C7 | electricity | 2022-12-30 | £-823.92 | £3,120.42 | +20.0% | £331.55/MWh | £383.40/MWh |
| C_IC3 | electricity | 2022-12-31 | £-196,113.08 | £885,591.70 | +17.1% | £233.88/MWh | £267.08/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,193.41 | £7,055.33 | +20.0% | £190.87/MWh | £253.58/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,414.36 | £17,979.18 | +20.0% | £213.85/MWh | £277.07/MWh |
| C4 | electricity | 2023-09-30 | £-335.89 | £1,907.25 | +12.6% | £216.87/MWh | £232.01/MWh |
| C_IC3g | gas | 2023-12-31 | £-252,917.30 | £294,338.38 | +20.0% | £42.73/MWh | £53.75/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,916.03 | £7,659.10 | +20.0% | £143.32/MWh | £197.78/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,612.90 | £14,454.77 | +20.0% | £141.21/MWh | £194.87/MWh |
| C_IC3g | gas | 2024-12-30 | £-17,160.47 | £268,215.17 | +1.4% | £43.34/MWh | £41.74/MWh |


## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 116 renewal(s) (30 gas) based on recent portfolio-wide margin rates: 83 surcharge(s), 33 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | 2.2% | +2.9% | £130.93/MWh | £134.71/MWh |
| C1g | gas | 2016-12-31 | 12.0% | -2.0% | £26.11/MWh | £25.59/MWh |
| C5 | electricity | 2016-12-31 | 1.3% | +3.3% | £130.93/MWh | £135.30/MWh |
| C7 | electricity | 2016-12-31 | 3.4% | +2.3% | £130.93/MWh | £133.95/MWh |
| C2 | electricity | 2017-04-01 | 10.3% | -1.2% | £129.36/MWh | £127.87/MWh |
| C2g | gas | 2017-04-01 | 11.7% | -1.8% | £29.66/MWh | £29.12/MWh |
| C6 | electricity | 2017-04-01 | 9.6% | -0.8% | £129.36/MWh | £128.35/MWh |
| C8 | electricity | 2017-04-01 | 9.2% | -0.6% | £129.36/MWh | £128.60/MWh |
| C3 | electricity | 2017-07-01 | 10.1% | -1.0% | £116.98/MWh | £115.76/MWh |
| C3g | gas | 2017-07-01 | 9.2% | -0.6% | £26.64/MWh | £26.49/MWh |
| C9 | electricity | 2017-07-01 | 6.7% | +0.6% | £116.98/MWh | £117.73/MWh |
| C4 | electricity | 2017-10-01 | 7.8% | +0.1% | £113.33/MWh | £113.47/MWh |
| C4g | gas | 2017-10-01 | 8.4% | -0.2% | £25.91/MWh | £25.86/MWh |
| C1 | electricity | 2017-12-31 | 6.0% | +1.0% | £121.45/MWh | £122.65/MWh |
| C1g | gas | 2017-12-31 | 6.2% | +0.9% | £32.65/MWh | £32.94/MWh |
| C5 | electricity | 2017-12-31 | 0.5% | +3.7% | £121.45/MWh | £126.00/MWh |
| C7 | electricity | 2017-12-31 | -2.5% | +5.2% | £121.45/MWh | £127.81/MWh |
| C_IC1 | electricity | 2018-01-31 | -15.5% | +11.8% | £99.09/MWh | £110.75/MWh |
| C2 | electricity | 2018-04-01 | -5.7% | +6.9% | £136.23/MWh | £145.59/MWh |
| C2g | gas | 2018-04-01 | 7.1% | +0.4% | £35.89/MWh | £36.05/MWh |
| C6 | electricity | 2018-04-01 | -6.4% | +7.2% | £136.23/MWh | £146.05/MWh |
| C8 | electricity | 2018-04-01 | 5.4% | +1.3% | £136.23/MWh | £137.99/MWh |
| C3 | electricity | 2018-07-01 | 7.3% | +0.4% | £136.06/MWh | £136.57/MWh |
| C3g | gas | 2018-07-01 | 6.8% | +0.6% | £31.85/MWh | £32.04/MWh |
| C9 | electricity | 2018-07-01 | 0.7% | +3.7% | £136.06/MWh | £141.03/MWh |
| C4 | electricity | 2018-10-01 | 4.3% | +1.8% | £134.83/MWh | £137.30/MWh |
| C4g | gas | 2018-10-01 | 6.5% | +0.8% | £32.32/MWh | £32.57/MWh |
| C1 | electricity | 2018-12-31 | 4.9% | +1.6% | £148.23/MWh | £150.56/MWh |
| C1g | gas | 2018-12-31 | 6.7% | +0.7% | £39.66/MWh | £39.92/MWh |
| C5 | electricity | 2018-12-31 | 5.4% | +1.3% | £148.23/MWh | £150.18/MWh |
| C7 | electricity | 2018-12-31 | 5.3% | +1.3% | £148.23/MWh | £150.20/MWh |
| C_IC2 | electricity | 2019-01-31 | -28.1% | +15.0% | £123.82/MWh | £142.40/MWh |
| C_IC1 | electricity | 2019-03-02 | -19.7% | +13.9% | £121.46/MWh | £138.31/MWh |
| C2 | electricity | 2019-04-01 | 3.5% | +2.3% | £155.73/MWh | £159.26/MWh |
| C2g | gas | 2019-04-01 | -0.1% | +4.1% | £36.58/MWh | £38.06/MWh |
| C6 | electricity | 2019-04-01 | 6.2% | +0.9% | £155.73/MWh | £157.17/MWh |
| C8 | electricity | 2019-04-01 | 25.9% | -5.0% | £155.73/MWh | £147.94/MWh |
| C3 | electricity | 2019-07-01 | 19.8% | -5.0% | £133.43/MWh | £126.76/MWh |
| C3g | gas | 2019-07-01 | 6.9% | +0.5% | £27.98/MWh | £28.14/MWh |
| C9 | electricity | 2019-07-01 | 9.4% | -0.7% | £133.43/MWh | £132.49/MWh |
| C4 | electricity | 2019-10-01 | 9.4% | -0.7% | £128.04/MWh | £127.16/MWh |
| C4g | gas | 2019-10-01 | 14.2% | -3.1% | £23.18/MWh | £22.46/MWh |
| C1 | electricity | 2019-12-31 | 8.8% | -0.4% | £129.65/MWh | £129.11/MWh |
| C1g | gas | 2019-12-31 | 13.2% | -2.6% | £23.93/MWh | £23.31/MWh |
| C5 | electricity | 2019-12-31 | 5.2% | +1.4% | £129.65/MWh | £131.47/MWh |
| C7 | electricity | 2019-12-31 | 4.7% | +1.7% | £129.65/MWh | £131.82/MWh |
| C_IC3 | electricity | 2020-01-01 | 2.6% | +2.7% | £45.89/MWh | £47.13/MWh |
| C_IC3g | gas | 2020-01-01 | 22.7% | -5.0% | £13.97/MWh | £13.27/MWh |
| C_IC2 | electricity | 2020-03-01 | -97.9% | +15.0% | £96.22/MWh | £110.65/MWh |
| C2 | electricity | 2020-03-31 | -89.2% | +15.0% | £130.89/MWh | £150.52/MWh |
| C2g | gas | 2020-03-31 | 13.2% | -2.6% | £24.65/MWh | £24.02/MWh |
| C6 | electricity | 2020-03-31 | -46.1% | +15.0% | £130.89/MWh | £150.52/MWh |
| C8 | electricity | 2020-03-31 | -14.7% | +11.3% | £130.89/MWh | £145.72/MWh |
| C_IC1 | electricity | 2020-03-31 | 22.6% | -5.0% | £96.89/MWh | £92.05/MWh |
| C3 | electricity | 2020-06-30 | 19.9% | -5.0% | £120.23/MWh | £114.22/MWh |
| C9 | electricity | 2020-06-30 | 19.9% | -5.0% | £120.23/MWh | £114.22/MWh |
| C4 | electricity | 2020-09-30 | 16.5% | -4.3% | £116.26/MWh | £111.32/MWh |
| C4g | gas | 2020-09-30 | 12.8% | -2.4% | £15.86/MWh | £15.48/MWh |
| C1 | electricity | 2020-12-30 | 8.5% | -0.3% | £136.59/MWh | £136.24/MWh |
| C1g | gas | 2020-12-30 | -0.6% | +4.3% | £22.82/MWh | £23.80/MWh |
| C5 | electricity | 2020-12-30 | 1.4% | +3.3% | £136.59/MWh | £141.11/MWh |
| C7 | electricity | 2020-12-30 | -7.6% | +7.8% | £136.59/MWh | £147.24/MWh |
| C_IC3 | electricity | 2020-12-31 | -8.2% | +8.1% | £50.53/MWh | £54.64/MWh |
| C_IC3g | gas | 2020-12-31 | -9.0% | +8.5% | £13.89/MWh | £15.07/MWh |
| C2 | electricity | 2021-03-31 | -28.8% | +15.0% | £157.96/MWh | £181.66/MWh |
| C2g | gas | 2021-03-31 | 2.8% | +2.6% | £30.45/MWh | £31.25/MWh |
| C6 | electricity | 2021-03-31 | -26.8% | +15.0% | £157.96/MWh | £181.66/MWh |
| C8 | electricity | 2021-03-31 | -24.7% | +15.0% | £157.96/MWh | £181.66/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.8% | +6.4% | £120.96/MWh | £128.71/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.5% | +3.8% | £115.47/MWh | £119.82/MWh |
| C9 | electricity | 2021-06-30 | 4.6% | +1.7% | £154.99/MWh | £157.64/MWh |
| C4 | electricity | 2021-09-30 | -1.5% | +4.7% | £181.67/MWh | £190.27/MWh |
| C4g | gas | 2021-09-30 | -6.3% | +7.2% | £44.66/MWh | £47.86/MWh |
| C1 | electricity | 2021-12-30 | 7.0% | +0.5% | £247.72/MWh | £248.90/MWh |
| C5 | electricity | 2021-12-30 | 7.0% | +0.5% | £247.72/MWh | £248.90/MWh |
| C7 | electricity | 2021-12-30 | 7.0% | +0.5% | £247.72/MWh | £248.90/MWh |
| C_IC3 | electricity | 2021-12-31 | -7.3% | +7.6% | £161.66/MWh | £174.00/MWh |
| C_IC3g | gas | 2021-12-31 | -3.4% | +5.7% | £74.78/MWh | £79.05/MWh |
| C2 | electricity | 2022-03-31 | -21.8% | +14.9% | £329.80/MWh | £378.95/MWh |
| C2g | gas | 2022-03-31 | 4.0% | +2.0% | £107.94/MWh | £110.08/MWh |
| C6 | electricity | 2022-03-31 | -15.8% | +11.9% | £329.80/MWh | £369.04/MWh |
| C8 | electricity | 2022-03-31 | -7.8% | +7.9% | £329.80/MWh | £355.88/MWh |
| C_IC2 | electricity | 2022-04-30 | -2.5% | +5.2% | £273.88/MWh | £288.25/MWh |
| C_IC1 | electricity | 2022-05-30 | 2.4% | +2.8% | £252.29/MWh | £259.32/MWh |
| C9 | electricity | 2022-06-30 | 8.3% | -0.1% | £296.06/MWh | £295.64/MWh |
| C4 | electricity | 2022-09-30 | 14.8% | -3.4% | £321.02/MWh | £310.19/MWh |
| C4g | gas | 2022-09-30 | -5.3% | +6.7% | £142.76/MWh | £152.27/MWh |
| C7 | electricity | 2022-12-30 | 15.3% | -3.6% | £331.55/MWh | £319.50/MWh |
| C_IC3 | electricity | 2022-12-31 | 13.0% | -2.5% | £233.88/MWh | £227.99/MWh |
| C_IC3g | gas | 2022-12-31 | -0.2% | +4.1% | £142.68/MWh | £148.54/MWh |
| C2 | electricity | 2023-03-31 | -13.2% | +10.6% | £340.83/MWh | £376.94/MWh |
| C2g | gas | 2023-03-31 | -15.8% | +11.9% | £122.30/MWh | £136.85/MWh |
| C6 | electricity | 2023-03-31 | -1.7% | +4.9% | £340.83/MWh | £357.39/MWh |
| C8 | electricity | 2023-03-31 | -0.2% | +4.1% | £340.83/MWh | £354.89/MWh |
| C_IC2 | electricity | 2023-05-30 | -13.4% | +10.7% | £190.87/MWh | £211.31/MWh |
| C_IC1 | electricity | 2023-06-29 | -7.9% | +8.0% | £213.85/MWh | £230.89/MWh |
| C9 | electricity | 2023-06-30 | -3.7% | +5.8% | £275.32/MWh | £291.37/MWh |
| C4 | electricity | 2023-09-30 | 19.1% | -5.0% | £216.87/MWh | £206.03/MWh |
| C4g | gas | 2023-09-30 | -3.7% | +5.8% | £51.65/MWh | £54.68/MWh |
| C7 | electricity | 2023-12-30 | 33.8% | -5.0% | £223.86/MWh | £212.67/MWh |
| C_IC3 | electricity | 2023-12-31 | 23.7% | -5.0% | £101.84/MWh | £96.75/MWh |
| C_IC3g | gas | 2023-12-31 | -1.6% | +4.8% | £42.73/MWh | £44.79/MWh |
| C2 | electricity | 2024-03-30 | -20.8% | +14.4% | £213.76/MWh | £244.49/MWh |
| C2g | gas | 2024-03-30 | -5.8% | +6.9% | £58.33/MWh | £62.35/MWh |
| C6 | electricity | 2024-03-30 | -19.6% | +13.8% | £213.76/MWh | £243.26/MWh |
| C8 | electricity | 2024-03-30 | -19.6% | +13.8% | £213.76/MWh | £243.26/MWh |
| C_IC2 | electricity | 2024-06-28 | -27.8% | +15.0% | £143.32/MWh | £164.82/MWh |
| C9 | electricity | 2024-06-29 | -24.1% | +15.0% | £198.22/MWh | £227.96/MWh |
| C_IC1 | electricity | 2024-07-28 | -25.5% | +15.0% | £141.21/MWh | £162.39/MWh |
| C4 | electricity | 2024-09-29 | 0.8% | +3.6% | £203.72/MWh | £211.09/MWh |
| C7 | electricity | 2024-12-29 | 0.8% | +3.6% | £220.98/MWh | £228.96/MWh |
| C_IC3 | electricity | 2024-12-30 | 20.6% | -5.0% | £93.81/MWh | £89.12/MWh |
| C_IC3g | gas | 2024-12-30 | 24.5% | -5.0% | £43.34/MWh | £41.17/MWh |
| C2 | electricity | 2025-03-30 | -13.7% | +10.9% | £246.37/MWh | £273.12/MWh |
| C2g | gas | 2025-03-30 | 9.8% | -0.9% | £63.40/MWh | £62.85/MWh |
| C8 | electricity | 2025-03-30 | -17.9% | +12.9% | £246.37/MWh | £278.23/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **4** | Blind misses: **4** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 1 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £4,405.15 | deliberate: £0.00 | total: £4,405.15

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.08 | No | £386.28 |
| C1 | 2021-12-30 | Blind miss | 0.08 | 0.17 | No | £370.80 |
| C6 | 2024-03-30 | Blind miss | 0.19 | 0.38 | Yes | £2,863.76 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.26 | No | £784.30 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C2+C2g | £1,922.30 | £2,046.85 | £3,969.15 | Yes |
| C3+C3g | £24.34 | £197.32 | £221.66 | Yes |
| C1+C1g | £45.94 | £164.78 | £210.73 | Yes |
| C4+C4g | £-501.67 | £240.44 | £-261.23 | Yes |
| C_IC3+C_IC3g | £46,918.37 | £-146,374.94 | £-99,456.57 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £-143,725.55.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £382,597.78 across 18 billing accounts. Revenue: £13,041,382.23.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,292,894.36 | £2,023,988.19 | £18,296.10 | £1,016,737.17 | 30.9% |
| 2 | C_IC2 | fixed | £1,545,571.96 | £919,156.00 | £8,610.28 | £455,678.38 | 29.5% |
| 3 | C_IC3 | pass_through | £4,521,491.73 | £1,684,480.49 | £22,657.93 | £46,918.37 | 1.0% |
| 4 | C8 | fixed | £23,459.84 | £14,198.02 | £157.27 | £4,217.73 | 18.0% |
| 5 | C9 | fixed | £20,917.26 | £13,344.77 | £127.61 | £3,068.88 | 14.7% |
| 6 | C6 | fixed | £30,021.73 | £16,782.03 | £213.94 | £2,500.58 | 8.3% |
| 7 | C2g | fixed | £7,718.06 | £3,700.19 | £84.61 | £2,046.85 | 26.5% |
| 8 | C2 | fixed | £13,752.80 | £8,066.57 | £97.02 | £1,922.30 | 14.0% |
| 9 | C7 | fixed | £22,978.36 | £11,953.54 | £165.55 | £801.42 | 3.5% |
| 10 | C4g | fixed | £9,069.30 | £2,323.06 | £110.11 | £240.44 | 2.7% |
| 11 | C3g | fixed | £1,549.14 | £755.59 | £9.77 | £197.32 | 12.7% |
| 12 | C1g | fixed | £2,038.90 | £883.05 | £14.90 | £164.78 | 8.1% |
| 13 | C1 | fixed | £2,995.33 | £1,800.88 | £15.65 | £45.94 | 1.5% |
| 14 | C3 | fixed | £2,187.60 | £1,385.73 | £9.45 | £24.34 | 1.1% |
| 15 | C5 | fixed | £14,777.21 | £8,952.48 | £79.54 | £-219.97 | -1.5% |
| 16 | C4 | fixed | £7,804.11 | £3,605.61 | £64.25 | £-501.67 | -6.4% |
| 17 | C_IC3g | pass_through | £1,831,432.12 | £425,654.64 | £14,381.28 | £-146,374.94 | -8.0% |
| 18 | C_IC4 | flex | £1,690,722.42 | £32,523.85 | £0.00 | £-1,004,870.14 | -59.4% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £13,041,382 | 100.0% |
| Wholesale cost | -£7,867,828 | 60.3% |
| **Gross supply margin** | **£5,173,555** | **39.7%** |
| Policy + Network costs | -£4,725,862 | 36.2% |
| Capital cost | -£65,095 | 0.5% |
| **Net supply margin** | **£382,598** | **2.9%** |

> *The ledger's `net_margin_gbp` (£5,122,518) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £11,050,680 | 42.2% | 4.7% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,831,432 | 23.2% | -8.0% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £44,799 | 57.4% | 5.1% | CMA 3-8% | ✓ |
| resi/elec | £94,095 | 57.8% | 10.2% | Ofgem CMA 2-5% | ⚠ ANOMALY |
| resi/gas | £20,375 | 37.6% | 13.0% | Ofgem CMA 2-4% | ⚠ ANOMALY |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: ANOMALIES DETECTED**
- Segment resi/elec net 10.2% (benchmark Ofgem CMA 2-5%)
- Segment resi/gas net 13.0% (benchmark Ofgem CMA 2-4%)
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
| Customer bills (all-in) | £17,933,254.43 |
|   Less: VAT remitted to HMRC | (£862,326.89) |
| = Revenue (ex-VAT) | £17,070,927.54 |
| Less: non-commodity pass-through | (£4,015,486.66) |
| Wholesale cost (settlement events) | (£7,867,827.54) |
| Gross margin | £5,187,613.34 |
| Capital charges | (£65,095.27) |
| Net margin | £5,122,518.06 |

_Cash reconciliation: of £17,933,254.43 billed, bad debt of £358,639.93 was written off, leaving £17,574,614.50 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £5,626,205.03._

| Acquisition spend | (£1,250.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £5,115,568.06 |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £5,115,568.06

## 2016

**Trading & Risk**

- Net margin: £492.77 (gross £5,575.35, capital £75.61)
  - Electricity: gross £5,084.43, capital £70.20, net £363.05
  - Gas: gross £490.92, capital £5.42, net £129.72
- Treasury at year end: £2,466,899.24
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.90 (avg 0.90), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.92), C6 0.91 (avg 0.91), C7 0.91 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.22, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-01-31: treasury £2,466,639.08, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-03-01: treasury £2,466,642.02, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-03-31: treasury £2,466,644.78, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-04-30: treasury £2,466,647.06, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-05-30: treasury £2,466,649.32, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-06-29: treasury £2,466,651.28, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-07-29: treasury £2,466,653.35, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-08-28: treasury £2,466,655.44, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-09-27: treasury £2,466,657.58, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-10-27: treasury £2,466,659.67, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-11-26: treasury £2,466,661.41, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
  - 2016-12-26: treasury £2,466,664.06, C1->1.00, VaR (current £23.72 / stressed £7.29) ratio 3.25
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.25
- Worst single period: C9 on 2016-11-20 period 36, net margin £-0.34

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £3,634.21
  - By billing account: C1 £1,726.56, C5 £5,007.86, C7 £4,168.20
- Bill shock events (>=20%): 21 -- C5 2016-05-31 (28%); C5 2016-06-30 (21%); C5 2016-10-31 (43%); C5 2016-11-30 (45%); C7 2016-04-30 (22%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-10-31 (83%); C7 2016-11-30 (54%); C6 2016-05-31 (26%); C6 2016-06-30 (23%); C6 2016-10-31 (42%); C6 2016-11-30 (47%); C8 2016-05-31 (41%); C8 2016-06-30 (42%); C8 2016-09-30 (25%); C8 2016-10-31 (110%); C8 2016-11-30 (72%); C9 2016-09-30 (20%); C9 2016-10-31 (80%); C9 2016-11-30 (61%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £111.70-£134.71/MWh, net margin £28.18
- C1g (gas): tariff £24.34-£25.59/MWh, net margin £25.15
- C2 (electricity): tariff £110.95/MWh, net margin £33.68
- C2g (gas): tariff £28.90/MWh, net margin £76.04
- C3 (electricity): tariff £101.48/MWh, net margin £-2.29 -- **net-negative**
- C3g (gas): tariff £23.99/MWh, net margin £19.29
- C4 (electricity): tariff £100.64/MWh, net margin £-3.49 -- **net-negative**
- C4g (gas): tariff £23.17/MWh, net margin £9.24
- C5 (electricity): tariff £111.70-£135.30/MWh, net margin £33.52
- C6 (electricity): tariff £110.95/MWh, net margin £-16.07 -- **net-negative**
- C7 (electricity): tariff £87.77-£167.55/MWh, net margin £140.56
- C8 (electricity): tariff £87.18-£166.43/MWh, net margin £116.25
- C9 (electricity): tariff £79.73-£152.22/MWh, net margin £32.71

**Portfolio Health**

- Capital cost ratio: 1.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.890, average bill shock 14.0%, bad debt provision £313.85, avg complaint probability 3.6%
- Solvency signal: £274,100/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £985.65 vs. naked (unhedged) net margin: £8,669.67
- hedging cost £7,684.02 vs. a fully unhedged book (commodity-only: actual net £985.65 vs. naked net £8,669.67)
  - C1: actual £73.16 vs. naked £508.76 -- hedging cost £435.59
  - C1g: actual £47.66 vs. naked £250.09 -- hedging cost £202.43
  - C2: actual £40.93 vs. naked £468.27 -- hedging cost £427.34
  - C2g: actual £98.69 vs. naked £233.39 -- hedging cost £134.70
  - C3: actual £-13.65 vs. naked £224.37 -- hedging cost £238.02
  - C3g: actual £35.41 vs. naked £140.96 -- hedging cost £105.55
  - C4: actual £-29.11 vs. naked £284.13 -- hedging cost £313.24
  - C4g: actual £30.84 vs. naked £182.62 -- hedging cost £151.78
  - C5: actual £163.00 vs. naked £2,399.57 -- hedging cost £2,236.57
  - C6: actual £-36.24 vs. naked £811.83 -- hedging cost £848.07
  - C7: actual £329.99 vs. naked £1,780.10 -- hedging cost £1,450.11
  - C8: actual £183.93 vs. naked £750.51 -- hedging cost £566.57
  - C9: actual £61.05 vs. naked £635.09 -- hedging cost £574.04

**Year narrative:** 2016 produced a net gain of £492.77 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 21 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £37,986.39 (gross £129,096.82, capital £1,258.39)
  - Electricity: gross £128,323.13, capital £1,247.96, net £37,846.84
  - Gas: gross £773.68, capital £10.43, net £139.55
- Treasury at year end: £2,504,735.57
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.90 (avg 0.90), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.92 (avg 0.92), C7 0.90 (avg 0.90), C8 0.92 (avg 0.92), C9 0.90 (avg 0.90), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 11
  - 2017-01-25: treasury £2,466,900.99, C1->1.00, C5->1.00, C7->1.00, VaR (current £312.92 / stressed £98.91) ratio 3.16
  - 2017-02-24: treasury £2,466,903.27, C1->1.00, C5->1.00, C7->1.00, VaR (current £312.92 / stressed £98.91) ratio 3.16
  - 2017-04-25: treasury £2,467,144.54, C1->1.00, C5->1.00, C7->1.00, VaR (current £747.19 / stressed £280.93) ratio 2.66
  - 2017-05-25: treasury £2,467,141.81, C1->1.00, C5->1.00, C7->1.00, VaR (current £747.19 / stressed £280.93) ratio 2.66
  - 2017-06-24: treasury £2,467,139.65, C1->1.00, C5->1.00, C7->1.00, VaR (current £747.19 / stressed £280.93) ratio 2.66
  - 2017-07-24: treasury £2,467,214.21, C1->1.00, C5->1.00, C7->1.00, VaR (current £869.28 / stressed £338.68) ratio 2.57
  - 2017-08-23: treasury £2,467,211.23, C1->1.00, C5->1.00, C7->1.00, VaR (current £869.28 / stressed £338.68) ratio 2.57
  - 2017-09-22: treasury £2,467,207.69, C1->1.00, C5->1.00, C7->1.00, VaR (current £869.28 / stressed £338.68) ratio 2.57
  - 2017-10-22: treasury £2,467,273.72, C5->1.00, C7->1.00, VaR (current £875.36 / stressed £343.96) ratio 2.54
  - 2017-11-21: treasury £2,467,277.51, C5->1.00, C7->1.00, VaR (current £875.36 / stressed £343.96) ratio 2.54
  - 2017-12-21: treasury £2,467,281.13, C5->1.00, C7->1.00, VaR (current £875.36 / stressed £343.96) ratio 2.54
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.69
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-23.56

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £5,490.51
  - By billing account: C1 £1,932.16, C2 £5,749.52, C3 £2,627.53, C4 £3,471.51, C5 £6,817.61, C6 £10,541.48, C7 £4,505.21, C8 £7,878.31, C9 £5,891.28
- Bill shock events (>=20%): 27 -- C5 2017-01-31 (32%); C5 2017-02-28 (23%); C5 2017-05-31 (20%); C5 2017-06-30 (22%); C5 2017-11-30 (58%); C7 2017-01-31 (39%); C7 2017-02-28 (29%); C7 2017-05-31 (32%); C7 2017-06-30 (33%); C7 2017-09-30 (28%); C7 2017-10-31 (23%); C7 2017-11-30 (79%); C6 2017-05-31 (22%); C6 2017-06-30 (20%); C6 2017-11-30 (51%); C8 2017-05-31 (40%); C8 2017-06-30 (37%); C8 2017-09-30 (48%); C8 2017-10-31 (23%); C8 2017-11-30 (85%); C8 2017-12-31 (22%); C9 2017-05-31 (33%); C9 2017-06-30 (27%); C9 2017-09-30 (31%); C9 2017-10-31 (22%); C9 2017-11-30 (72%); C4 2017-10-31 (22%)
- Churn risk (accounts renewing in 2017): 5 at risk (≥20% churn prob): C5 32%, C6 35%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £122.65-£134.71/MWh, net margin £44.77
- C1g (gas): tariff £25.59-£32.94/MWh, net margin £22.40
- C2 (electricity): tariff £110.95-£127.87/MWh, net margin £47.77
- C2g (gas): tariff £28.90-£29.12/MWh, net margin £66.68
- C3 (electricity): tariff £101.48-£118.76/MWh, net margin £0.53
- C3g (gas): tariff £23.99-£26.49/MWh, net margin £31.40
- C4 (electricity): tariff £100.64-£116.67/MWh, net margin £-26.22 -- **net-negative**
- C4g (gas): tariff £23.17-£25.86/MWh, net margin £19.06
- C5 (electricity): tariff £126.00-£135.30/MWh, net margin £128.44
- C6 (electricity): tariff £110.95-£131.35/MWh, net margin £44.30
- C7 (electricity): tariff £102.78-£200.93/MWh, net margin £187.95
- C8 (electricity): tariff £87.18-£192.90/MWh, net margin £205.65
- C9 (electricity): tariff £79.73-£176.59/MWh, net margin £99.97
- C_IC1 (electricity): tariff £79.23-£151.25/MWh, net margin £37,113.69

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.884, average bill shock 11.4%, bad debt provision £7,542.75, avg complaint probability 3.5%
- Solvency signal: £250,474/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £37,576.27 vs. naked (unhedged) net margin: £116,594.26
- hedging cost £79,017.99 vs. a fully unhedged book (commodity-only: actual net £37,576.27 vs. naked net £116,594.26)
  - C1: actual £-35.37 vs. naked £206.65 -- hedging cost £242.02
  - C1g: actual £43.59 vs. naked £121.80 -- hedging cost £78.21
  - C2: actual £53.52 vs. naked £510.58 -- hedging cost £457.06
  - C2g: actual £55.58 vs. naked £169.72 -- hedging cost £114.15
  - C3: actual £15.53 vs. naked £264.18 -- hedging cost £248.65
  - C3g: actual £27.40 vs. naked £101.48 -- hedging cost £74.08
  - C4: actual £-20.73 vs. naked £311.90 -- hedging cost £332.63
  - C4g: actual £-14.69 vs. naked £99.74 -- hedging cost £114.43
  - C5: actual £-207.59 vs. naked £1,043.39 -- hedging cost £1,250.98
  - C6: actual £94.83 vs. naked £1,328.09 -- hedging cost £1,233.26
  - C7: actual £34.27 vs. naked £859.88 -- hedging cost £825.61
  - C8: actual £250.03 vs. naked £942.76 -- hedging cost £692.73
  - C9: actual £166.21 vs. naked £836.58 -- hedging cost £670.37
  - C_IC1: actual £37,113.69 vs. naked £109,797.51 -- hedging cost £72,683.81

**Year narrative:** 2017 produced a net gain of £37,986.39 across 14 accounts. The risk committee intervened 11 time(s), raising hedge fractions in response to elevated VaR. 27 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £76,584.79 (gross £237,391.03, capital £1,619.08)
  - Electricity: gross £236,665.29, capital £1,604.28, net £76,483.31
  - Gas: gross £725.74, capital £14.80, net £101.48
- Treasury at year end: £2,496,538.39
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.91 (avg 0.91), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2018-03-01 period 27, net margin £-20.41

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £150,481.82
  - By billing account: C1 £1,958.93, C2 £4,744.24, C3 £2,603.12, C4 £2,965.85, C5 £5,951.75, C6 £7,706.43, C7 £4,492.88, C8 £6,334.54, C9 £5,832.06, C_IC1 £1,462,228.40
- Bill shock events (>=20%): 34 -- C5 2018-04-30 (32%); C5 2018-06-30 (21%); C5 2018-10-31 (32%); C5 2018-11-30 (28%); C7 2018-04-30 (39%); C7 2018-05-31 (29%); C7 2018-06-30 (32%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C6 2018-04-30 (24%); C6 2018-05-31 (22%); C6 2018-06-30 (22%); C6 2018-10-31 (31%); C6 2018-11-30 (22%); C8 2018-04-30 (34%); C8 2018-05-31 (38%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (57%); C8 2018-11-30 (30%); C9 2018-04-30 (32%); C9 2018-05-31 (35%); C9 2018-06-30 (35%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-10-31 (26%); C4g 2018-10-31 (21%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (48%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C4 20%, C5 38%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £122.65-£157.56/MWh, net margin £-35.10 -- **net-negative**
- C1g (gas): tariff £32.94-£39.92/MWh, net margin £43.68
- C2 (electricity): tariff £127.87-£145.59/MWh, net margin £12.21
- C2g (gas): tariff £29.12-£36.05/MWh, net margin £56.38
- C3 (electricity): tariff £118.76-£139.57/MWh, net margin £19.99
- C3g (gas): tariff £26.49-£32.04/MWh, net margin £21.67
- C4 (electricity): tariff £116.67-£140.30/MWh, net margin £-21.79 -- **net-negative**
- C4g (gas): tariff £25.86-£32.57/MWh, net margin £-20.26 -- **net-negative**
- C5 (electricity): tariff £126.00-£159.23/MWh, net margin £-206.39 -- **net-negative**
- C6 (electricity): tariff £131.35-£146.05/MWh, net margin £-44.41 -- **net-negative**
- C7 (electricity): tariff £102.78-£229.80/MWh, net margin £37.06
- C8 (electricity): tariff £101.04-£211.48/MWh, net margin £157.29
- C9 (electricity): tariff £92.50-£216.05/MWh, net margin £212.03
- C_IC1 (electricity): tariff £-82.12-£226.14/MWh, net margin £79,317.60
- C_IC2 (electricity): tariff £71.18-£135.90/MWh, net margin £-2,965.19 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.872, average bill shock 11.2%, bad debt provision £12,303.43, avg complaint probability 3.6%
- Solvency signal: £226,958/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £84,385.92 vs. naked (unhedged) net margin: £216,953.28
- hedging cost £132,567.36 vs. a fully unhedged book (commodity-only: actual net £84,385.92 vs. naked net £216,953.28)
  - C1: actual £38.83 vs. naked £399.69 -- hedging cost £360.86
  - C1g: actual £106.87 vs. naked £312.59 -- hedging cost £205.72
  - C2: actual £-7.31 vs. naked £586.42 -- hedging cost £593.73
  - C2g: actual £62.28 vs. naked £211.90 -- hedging cost £149.62
  - C3: actual £24.24 vs. naked £354.58 -- hedging cost £330.34
  - C3g: actual £26.23 vs. naked £172.33 -- hedging cost £146.10
  - C4: actual £-21.79 vs. naked £485.11 -- hedging cost £506.90
  - C4g: actual £-12.49 vs. naked £350.46 -- hedging cost £362.95
  - C5: actual £109.51 vs. naked £1,941.31 -- hedging cost £1,831.81
  - C6: actual £-131.73 vs. naked £1,423.17 -- hedging cost £1,554.90
  - C7: actual £138.07 vs. naked £1,364.66 -- hedging cost £1,226.59
  - C8: actual £78.48 vs. naked £951.07 -- hedging cost £872.59
  - C9: actual £264.24 vs. naked £1,124.82 -- hedging cost £860.57
  - C_IC1: actual £86,675.68 vs. naked £170,942.41 -- hedging cost £84,266.73
  - C_IC2: actual £-2,965.19 vs. naked £36,332.77 -- hedging cost £39,297.96

**Year narrative:** 2018 produced a net gain of £76,584.79 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 34 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £181,418.30 (gross £651,142.47, capital £3,549.29)
  - Electricity: gross £620,105.31, capital £2,153.83, net £217,180.52
  - Gas: gross £31,037.17, capital £1,395.46, net £-35,762.22
- Treasury at year end: £2,601,755.65
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.90 (avg 0.90), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.92 (avg 0.92), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2019-09-01 period 1, net margin £-141.19

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £202,187.03
  - By billing account: C1 £1,842.71, C2 £4,087.87, C3 £2,526.56, C4 £3,193.83, C5 £6,288.69, C6 £8,662.24, C7 £5,476.25, C8 £5,878.56, C9 £6,199.81, C_IC1 £1,311,380.66, C_IC2 £868,520.16
- Bill shock events (>=20%): 35 -- C1 2019-04-30 (22%); C5 2019-01-31 (41%); C5 2019-02-28 (22%); C5 2019-06-30 (26%); C5 2019-10-31 (44%); C5 2019-11-30 (36%); C7 2019-01-31 (42%); C7 2019-02-28 (27%); C7 2019-05-31 (24%); C7 2019-06-30 (36%); C7 2019-10-31 (73%); C7 2019-11-30 (46%); C6 2019-02-28 (21%); C6 2019-06-30 (25%); C6 2019-10-31 (42%); C6 2019-11-30 (27%); C8 2019-01-31 (27%); C8 2019-02-28 (28%); C8 2019-04-30 (22%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-09-30 (62%); C8 2019-10-31 (89%); C8 2019-11-30 (38%); C3 2019-04-30 (21%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (37%); C9 2019-07-31 (36%); C9 2019-09-30 (53%); C9 2019-10-31 (76%); C9 2019-11-30 (38%); C_IC1 2019-02-28 (51%); C_IC1 2019-03-31 (123%); C_IC2 2019-02-28 (62%)
- Churn risk (accounts renewing in 2019): 8 at risk (≥20% churn prob): C1 20%, C4 20%, C5 38%, C6 32%, C7 35%, C8 38%, C9 32%, C_IC1 20%

**Pricing & Margin**

- C1 (electricity): tariff £129.11-£157.56/MWh, net margin £38.69
- C1g (gas): tariff £23.31-£39.92/MWh, net margin £106.78
- C2 (electricity): tariff £145.59-£159.26/MWh, net margin £108.68
- C2g (gas): tariff £36.05-£38.06/MWh, net margin £163.01
- C3 (electricity): tariff £126.76-£139.57/MWh, net margin £7.42
- C3g (gas): tariff £28.14-£32.04/MWh, net margin £67.73
- C4 (electricity): tariff £130.16-£140.30/MWh, net margin £-5.58 -- **net-negative**
- C4g (gas): tariff £22.46-£32.57/MWh, net margin £13.04
- C5 (electricity): tariff £131.47-£159.23/MWh, net margin £108.70
- C6 (electricity): tariff £146.05-£157.17/MWh, net margin £115.36
- C7 (electricity): tariff £103.57-£229.80/MWh, net margin £137.86
- C8 (electricity): tariff £110.78-£221.91/MWh, net margin £217.52
- C9 (electricity): tariff £106.45-£216.05/MWh, net margin £255.93
- C_IC1 (electricity): tariff £0.00-£253.45/MWh, net margin £130,126.32
- C_IC2 (electricity): tariff £-60.00-£260.81/MWh, net margin £70,597.21
- C_IC3 (electricity): tariff £56.10-£107.11/MWh, net margin £15,472.41
- C_IC3g (gas): tariff £30.07/MWh, net margin £-36,112.79 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.878, average bill shock 12.3%, bad debt provision £34,394.41, avg complaint probability 3.7%
- Solvency signal: £216,813/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £206,762.86 vs. naked (unhedged) net margin: £821,889.32
- hedging cost £615,126.46 vs. a fully unhedged book (commodity-only: actual net £206,762.86 vs. naked net £821,889.32)
  - C1: actual £4.69 vs. naked £323.49 -- hedging cost £318.80
  - C1g: actual £30.95 vs. naked £165.70 -- hedging cost £134.75
  - C2: actual £158.02 vs. naked £846.38 -- hedging cost £688.36
  - C2g: actual £194.33 vs. naked £402.98 -- hedging cost £208.65
  - C3: actual £-1.78 vs. naked £395.08 -- hedging cost £396.85
  - C3g: actual £108.28 vs. naked £266.25 -- hedging cost £157.97
  - C4: actual £46.46 vs. naked £524.98 -- hedging cost £478.52
  - C4g: actual £90.57 vs. naked £306.77 -- hedging cost £216.20
  - C5: actual £-57.55 vs. naked £1,537.50 -- hedging cost £1,595.05
  - C6: actual £255.96 vs. naked £2,122.13 -- hedging cost £1,866.17
  - C7: actual £91.74 vs. naked £1,132.43 -- hedging cost £1,040.70
  - C8: actual £302.43 vs. naked £1,386.90 -- hedging cost £1,084.48
  - C9: actual £249.44 vs. naked £1,307.14 -- hedging cost £1,057.70
  - C_IC1: actual £148,717.82 vs. naked £286,943.07 -- hedging cost £138,225.25
  - C_IC2: actual £77,211.89 vs. naked £151,825.79 -- hedging cost £74,613.91
  - C_IC3: actual £15,472.41 vs. naked £306,825.65 -- hedging cost £291,353.23
  - C_IC3g: actual £-36,112.79 vs. naked £65,577.06 -- hedging cost £101,689.86

**Year narrative:** 2019 produced a net gain of £181,418.30 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 35 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-36,423.20 (gross £628,342.59, capital £2,757.84)
  - Electricity: gross £565,967.33, capital £1,943.67, net £-31,573.63
  - Gas: gross £62,375.26, capital £814.17, net £-4,849.58
- Treasury at year end: £2,672,886.73
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.88 (avg 0.88), C2g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.88 (avg 0.88), C7 0.89 (avg 0.89), C8 0.88 (avg 0.88), C9 0.87 (avg 0.87), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.85 (avg 0.85), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2020-05-01 period 1, net margin £-66.95

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2020): £229,039.11
  - By billing account: C1 £1,994.12, C2 £4,985.51, C3 £2,149.33, C4 £2,791.03, C5 £7,063.76, C6 £8,647.20, C7 £4,674.85, C8 £5,946.37, C9 £5,929.74, C_IC1 £864,740.76, C_IC2 £516,514.29, C_IC3 £1,526,967.32, C_IC4 £25,104.10
- Bill shock events (>=20%): 33 -- C1 2020-04-30 (21%); C1g 2020-01-31 (28%); C5 2020-04-30 (29%); C5 2020-10-31 (39%); C5 2020-12-31 (26%); C7 2020-04-30 (35%); C7 2020-05-31 (22%); C7 2020-06-30 (28%); C7 2020-10-31 (63%); C7 2020-11-30 (24%); C7 2020-12-31 (36%); C2g 2020-04-30 (28%); C6 2020-04-30 (30%); C6 2020-09-30 (21%); C6 2020-10-31 (34%); C6 2020-12-31 (26%); C8 2020-04-30 (37%); C8 2020-05-31 (26%); C8 2020-06-30 (33%); C8 2020-09-30 (57%); C8 2020-10-31 (68%); C8 2020-12-31 (44%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-09-30 (47%); C9 2020-10-31 (52%); C9 2020-12-31 (37%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (86%); C_IC2 2020-02-29 (65%); C_IC2 2020-03-31 (132%); C_IC4 2020-12-31 (21%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 29%, C5 35%, C6 32%, C7 38%, C8 38%, C9 41%, C_IC4 23%

**Pricing & Margin**

- C1 (electricity): tariff £129.11-£139.24/MWh, net margin £4.35
- C1g (gas): tariff £23.31-£23.80/MWh, net margin £30.85
- C2 (electricity): tariff £150.52-£159.26/MWh, net margin £191.56
- C2g (gas): tariff £24.02-£38.06/MWh, net margin £123.90
- C3 (electricity): tariff £126.76/MWh, net margin £-1.31 -- **net-negative**
- C3g (gas): tariff £28.14/MWh, net margin £57.22
- C4 (electricity): tariff £111.32-£130.16/MWh, net margin £2.51
- C4g (gas): tariff £15.48-£22.46/MWh, net margin £55.34
- C5 (electricity): tariff £131.47-£144.11/MWh, net margin £-59.67 -- **net-negative**
- C6 (electricity): tariff £150.52-£157.17/MWh, net margin £338.99
- C7 (electricity): tariff £103.57-£220.86/MWh, net margin £94.33
- C8 (electricity): tariff £114.49-£221.91/MWh, net margin £384.68
- C9 (electricity): tariff £89.74-£203.23/MWh, net margin £180.56
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £71,628.80
- C_IC2 (electricity): tariff £-79.50-£260.81/MWh, net margin £53,243.76
- C_IC3 (electricity): tariff £37.03-£81.96/MWh, net margin £12,398.03
- C_IC3g (gas): tariff £15.07-£15.92/MWh, net margin £-5,116.89 -- **net-negative**
- C_IC4 (electricity): tariff £18.53-£73.19/MWh, net margin £-169,980.21 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.877, average bill shock 11.6%, bad debt provision £35,387.89, avg complaint probability 3.6%
- Solvency signal: £205,607/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-102,398.83 vs. naked (unhedged) net margin: £591,708.10
- hedging cost £694,106.92 vs. a fully unhedged book (commodity-only: actual net £-102,398.83 vs. naked net £591,708.10)
  - C1: actual £-35.37 vs. naked £18.95 -- hedging cost £54.32
  - C1g: actual £-64.28 vs. naked £-235.89 -- hedging added £171.61
  - C2: actual £194.80 vs. naked £733.60 -- hedging cost £538.80
  - C2g: actual £94.48 vs. naked £188.63 -- hedging cost £94.16
  - C4: actual £-122.30 vs. naked £183.46 -- hedging cost £305.76
  - C4g: actual £-120.01 vs. naked £-220.28 -- hedging added £100.27
  - C5: actual £-227.33 vs. naked £169.30 -- hedging cost £396.63
  - C6: actual £355.42 vs. naked £1,746.52 -- hedging cost £1,391.10
  - C7: actual £36.65 vs. naked £305.00 -- hedging cost £268.34
  - C8: actual £418.11 vs. naked £1,153.87 -- hedging cost £735.76
  - C9: actual £72.09 vs. naked £680.51 -- hedging cost £608.41
  - C_IC1: actual £62,305.44 vs. naked £151,452.09 -- hedging cost £89,146.65
  - C_IC2: actual £55,342.54 vs. naked £106,123.23 -- hedging cost £50,780.69
  - C_IC3: actual £-8,114.16 vs. naked £199,495.09 -- hedging cost £207,609.25
  - C_IC3g: actual £120,545.96 vs. naked £146,590.86 -- hedging cost £26,044.90
  - C_IC4: actual £-333,080.86 vs. naked £-16,676.84 -- hedging cost £316,404.02

**Year narrative:** 2020 produced a net loss of £-36,423.20 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £43,684.01 (gross £697,770.18, capital £6,909.88)
  - Electricity: gross £498,375.62, capital £5,773.60, net £-81,665.37
  - Gas: gross £199,394.56, capital £1,136.28, net £125,349.38
- Treasury at year end: £2,690,333.41
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C4 0.91 (avg 0.91), C4g 0.85 (avg 0.85), C6 0.90 (avg 0.90), C7 0.94 (avg 0.94), C8 0.90 (avg 0.90), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.95 (avg 0.95), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2021-12-31 period 1, net margin £-85.79

**Customer Book**

- Active accounts: 16 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £215,492.39
  - By billing account: C1 £1,845.82, C2 £4,509.89, C3 £1,960.42, C4 £2,482.13, C5 £5,845.79, C6 £8,231.08, C7 £4,587.17, C8 £5,768.47, C9 £4,898.28, C_IC1 £765,743.80, C_IC2 £479,192.25, C_IC3 £1,496,141.56, C_IC4 £20,194.44
- Bill shock events (>=20%): 38 -- C1 2021-04-30 (20%); C5 2021-05-31 (23%); C5 2021-06-30 (32%); C5 2021-10-31 (30%); C5 2021-11-30 (51%); C7 2021-05-31 (31%); C7 2021-06-30 (48%); C7 2021-10-31 (56%); C7 2021-11-30 (67%); C6 2021-06-30 (36%); C6 2021-10-31 (27%); C6 2021-11-30 (50%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (26%); C8 2021-10-31 (69%); C8 2021-11-30 (85%); C9 2021-02-28 (21%); C9 2021-05-31 (25%); C9 2021-06-30 (52%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-10-31 (62%); C9 2021-11-30 (50%); C9 2021-12-31 (24%); C4 2021-10-31 (74%); C4g 2021-10-31 (138%); C_IC1 2021-04-30 (22%); C_IC1 2021-05-31 (47%); C_IC2 2021-03-31 (30%); C_IC2 2021-04-30 (75%); C_IC3g 2021-09-30 (23%); C_IC3g 2021-10-31 (28%); C_IC3g 2021-12-31 (31%); C_IC4 2021-02-28 (28%); C_IC4 2021-07-31 (22%); C_IC4 2021-09-30 (40%); C_IC4 2021-12-31 (29%)
- Churn risk (accounts renewing in 2021): 9 at risk (≥20% churn prob): C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC3 20%, C_IC4 32%

**Pricing & Margin**

- C1 (electricity): tariff £139.24/MWh, net margin £-34.95 -- **net-negative**
- C1g (gas): tariff £23.80/MWh, net margin £-64.09 -- **net-negative**
- C2 (electricity): tariff £150.52-£181.66/MWh, net margin £161.23
- C2g (gas): tariff £24.02-£31.25/MWh, net margin £-2.15 -- **net-negative**
- C4 (electricity): tariff £111.32-£221.11/MWh, net margin £-130.39 -- **net-negative**
- C4g (gas): tariff £15.48-£57.44/MWh, net margin £-161.44 -- **net-negative**
- C5 (electricity): tariff £144.11/MWh, net margin £-224.58 -- **net-negative**
- C6 (electricity): tariff £150.52-£181.66/MWh, net margin £257.27
- C7 (electricity): tariff £115.69-£373.34/MWh, net margin £28.20
- C8 (electricity): tariff £114.49-£272.49/MWh, net margin £412.73
- C9 (electricity): tariff £89.74-£236.46/MWh, net margin £-17.94 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £54,831.14
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £48,116.84
- C_IC3 (electricity): tariff £42.93-£265.50/MWh, net margin £-21,505.65 -- **net-negative**
- C_IC3g (gas): tariff £15.07-£79.05/MWh, net margin £125,577.06
- C_IC4 (electricity): tariff £42.47-£336.77/MWh, net margin £-163,559.27 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.868, average bill shock 13.4%, bad debt provision £45,595.27, avg complaint probability 3.9%
- Solvency signal: £224,194/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-189,511.72 vs. naked (unhedged) net margin: £-196,230.13
- hedging added £6,718.41 vs. a fully unhedged book (commodity-only: actual net £-189,511.72 vs. naked net £-196,230.13)
  - C2: actual £125.94 vs. naked £127.93 -- hedging cost £2.00
  - C2g: actual £-48.21 vs. naked £-444.27 -- hedging added £396.07
  - C4: actual £-175.51 vs. naked £-90.98 -- hedging cost £84.53
  - C4g: actual £-298.32 vs. naked £-1,092.65 -- hedging added £794.33
  - C6: actual £130.62 vs. naked £-219.78 -- hedging added £350.39
  - C7: actual £-823.92 vs. naked £-215.49 -- hedging cost £608.43
  - C8: actual £355.92 vs. naked £-27.38 -- hedging added £383.30
  - C9: actual £-170.27 vs. naked £-548.68 -- hedging added £378.41
  - C_IC1: actual £60,250.07 vs. naked £-52,649.80 -- hedging added £112,899.86
  - C_IC2: actual £52,270.49 vs. naked £-508.76 -- hedging added £52,779.25
  - C_IC3: actual £-196,113.08 vs. naked £-119,060.91 -- hedging cost £77,052.17
  - C_IC3g: actual £43,578.41 vs. naked £38,284.45 -- hedging added £5,293.96
  - C_IC4: actual £-148,593.86 vs. naked £-59,783.81 -- hedging cost £88,810.05

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £43,684.01 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £-66,017.09 (gross £552,935.63, capital £15,193.03)
  - Electricity: gross £425,114.22, capital £12,706.66, net £-109,678.08
  - Gas: gross £127,821.42, capital £2,486.38, net £43,661.00
- Treasury at year end: £2,504,653.20
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.94 (avg 0.94), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.94 (avg 0.94), C8 0.94 (avg 0.94), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.98), C_IC3 0.96 (avg 0.96), C_IC3g 1.00 (avg 1.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £2,806,728.05, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,745.51 / stressed £21,353.04) ratio 2.70
  - 2022-05-29: treasury £2,806,877.36, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,882.93 / stressed £21,394.25) ratio 2.71
  - 2022-06-28: treasury £2,806,863.05, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,882.93 / stressed £21,394.25) ratio 2.71
  - 2022-07-28: treasury £2,806,723.87, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £58,023.50 / stressed £21,427.22) ratio 2.71
  - 2022-08-27: treasury £2,806,706.25, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £58,023.50 / stressed £21,427.22) ratio 2.71
  - 2022-09-26: treasury £2,806,689.16, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £58,023.50 / stressed £21,427.22) ratio 2.71
  - 2022-10-26: treasury £2,805,744.49, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £58,263.05 / stressed £21,505.25) ratio 2.71
  - 2022-11-25: treasury £2,805,682.99, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £58,263.05 / stressed £21,505.25) ratio 2.71
  - 2022-12-25: treasury £2,805,574.35, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £58,263.05 / stressed £21,505.25) ratio 2.71
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.71
- Worst single period: C_IC3g on 2022-10-01 period 1, net margin £-463.03

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2022): £200,513.35
  - By billing account: C1 £1,724.39, C2 £4,597.22, C3 £1,920.39, C4 £2,218.99, C5 £5,836.67, C6 £7,917.35, C7 £3,904.37, C8 £5,689.80, C9 £5,504.49, C_IC1 £872,656.95, C_IC2 £450,073.76, C_IC3 £1,228,954.17, C_IC4 £15,675.03
- Bill shock events (>=20%): 51 -- C7 2022-01-31 (76%); C7 2022-02-28 (27%); C7 2022-04-30 (23%); C7 2022-05-31 (37%); C7 2022-06-30 (27%); C7 2022-09-30 (35%); C7 2022-11-30 (65%); C7 2022-12-31 (57%); C2 2022-04-30 (50%); C2g 2022-04-30 (155%); C6 2022-04-30 (44%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (44%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-04-30 (30%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (86%); C8 2022-11-30 (73%); C8 2022-12-31 (58%); C9 2022-04-30 (21%); C9 2022-05-31 (30%); C9 2022-06-30 (30%); C9 2022-07-31 (27%); C9 2022-09-30 (51%); C9 2022-10-31 (31%); C9 2022-11-30 (46%); C9 2022-12-31 (53%); C4 2022-10-31 (55%); C4g 2022-10-31 (166%); C_IC1 2022-06-30 (83%); C_IC2 2022-05-31 (54%); C_IC3 2022-01-31 (62%); C_IC3g 2022-03-31 (55%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (46%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-09-30 (21%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (21%); C_IC3g 2022-12-31 (21%); C_IC4 2022-02-28 (21%); C_IC4 2022-03-31 (44%); C_IC4 2022-05-31 (21%); C_IC4 2022-07-31 (38%); C_IC4 2022-08-31 (41%); C_IC4 2022-10-31 (39%); C_IC4 2022-12-31 (102%)
- Churn risk (accounts renewing in 2022): 8 at risk (≥20% churn prob): C4 23%, C6 32%, C7 35%, C8 38%, C9 41%, C_IC1 20%, C_IC3 29%, C_IC4 38%

**Pricing & Margin**

- C2 (electricity): tariff £181.66-£378.95/MWh, net margin £227.60
- C2g (gas): tariff £31.25-£115.89/MWh, net margin £17.26
- C4 (electricity): tariff £221.11-£341.81/MWh, net margin £-215.23 -- **net-negative**
- C4g (gas): tariff £57.44-£180.61/MWh, net margin £-147.16 -- **net-negative**
- C6 (electricity): tariff £181.66-£372.04/MWh, net margin £287.80
- C7 (electricity): tariff £195.56-£579.61/MWh, net margin £-815.38 -- **net-negative**
- C8 (electricity): tariff £142.73-£533.82/MWh, net margin £426.00
- C9 (electricity): tariff £123.86-£464.47/MWh, net margin £237.06
- C_IC1 (electricity): tariff £-83.39-£450.61/MWh, net margin £161,877.15
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £72,251.71
- C_IC3 (electricity): tariff £139.07-£265.50/MWh, net margin £-195,448.22 -- **net-negative**
- C_IC3g (gas): tariff £79.05-£148.54/MWh, net margin £43,790.89
- C_IC4 (electricity): tariff £71.50-£469.98/MWh, net margin £-148,506.58 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.7% of gross
- Treasury drawdown events (>=10% threshold): 801 -- £2,806,983.14 -> £2,504,391.99 (10.8%); £2,806,989.63 -> £2,504,391.61 (10.8%); £2,807,007.17 -> £2,504,391.35 (10.8%); £2,807,020.05 -> £2,504,391.05 (10.8%); £2,807,029.40 -> £2,504,390.78 (10.8%); £2,807,036.37 -> £2,499,821.60 (10.9%); £2,823,224.10 -> £2,504,507.92 (11.3%); £2,823,224.15 -> £2,504,508.25 (11.3%); £2,823,224.23 -> £2,504,508.26 (11.3%); £2,823,224.25 -> £2,504,508.26 (11.3%); £2,823,224.26 -> £2,504,508.27 (11.3%); £2,823,224.29 -> £2,504,508.39 (11.3%); £2,823,224.37 -> £2,504,508.41 (11.3%); £2,823,224.45 -> £2,504,508.42 (11.3%); £2,823,224.53 -> £2,504,508.44 (11.3%); £2,823,224.58 -> £2,504,508.91 (11.3%); £2,823,224.72 -> £2,504,508.91 (11.3%); £2,823,224.86 -> £2,504,508.92 (11.3%); £2,823,225.00 -> £2,504,508.93 (11.3%); £2,823,225.04 -> £2,504,508.93 (11.3%); £2,823,225.09 -> £2,504,508.94 (11.3%); £2,823,225.22 -> £2,504,509.03 (11.3%); £2,823,225.35 -> £2,504,509.05 (11.3%); £2,823,225.49 -> £2,504,509.06 (11.3%); £2,823,225.62 -> £2,504,509.07 (11.3%); £2,823,225.75 -> £2,504,509.08 (11.3%); £2,823,225.87 -> £2,504,509.10 (11.3%); £2,823,225.99 -> £2,504,509.11 (11.3%); £2,823,226.04 -> £2,504,511.23 (11.3%); £2,823,226.21 -> £2,504,511.24 (11.3%); £2,823,226.25 -> £2,504,511.24 (11.3%); £2,823,226.30 -> £2,504,511.25 (11.3%); £2,823,226.31 -> £2,504,511.33 (11.3%); £2,823,226.46 -> £2,504,511.35 (11.3%); £2,823,226.62 -> £2,504,511.37 (11.3%); £2,823,226.77 -> £2,504,511.39 (11.3%); £2,823,226.92 -> £2,504,511.40 (11.3%); £2,823,227.08 -> £2,504,511.42 (11.3%); £2,823,227.22 -> £2,504,511.43 (11.3%); £2,823,227.37 -> £2,504,511.45 (11.3%); £2,823,227.48 -> £2,504,511.96 (11.3%); £2,823,227.60 -> £2,504,511.97 (11.3%); £2,823,227.71 -> £2,504,511.97 (11.3%); £2,823,227.83 -> £2,504,511.98 (11.3%); £2,823,227.94 -> £2,504,511.99 (11.3%); £2,823,227.99 -> £2,504,511.99 (11.3%); £2,823,228.03 -> £2,504,511.99 (11.3%); £2,823,228.13 -> £2,504,512.07 (11.3%); £2,823,228.24 -> £2,504,512.08 (11.3%); £2,823,228.35 -> £2,504,512.09 (11.3%); £2,823,228.46 -> £2,504,512.10 (11.3%); £2,823,228.56 -> £2,504,512.11 (11.3%); £2,823,228.67 -> £2,504,512.12 (11.3%); £2,823,228.77 -> £2,504,512.13 (11.3%); £2,823,228.79 -> £2,504,512.61 (11.3%); £2,823,228.88 -> £2,504,512.61 (11.3%); £2,823,228.96 -> £2,504,512.62 (11.3%); £2,823,229.05 -> £2,504,512.63 (11.3%); £2,823,229.14 -> £2,504,512.63 (11.3%); £2,823,229.18 -> £2,504,512.64 (11.3%); £2,823,229.23 -> £2,504,512.64 (11.3%); £2,823,229.23 -> £2,504,512.72 (11.3%); £2,823,229.32 -> £2,504,512.73 (11.3%); £2,823,229.41 -> £2,504,512.75 (11.3%); £2,823,229.51 -> £2,504,512.77 (11.3%); £2,823,229.60 -> £2,504,512.78 (11.3%); £2,823,229.70 -> £2,504,512.80 (11.3%); £2,823,229.78 -> £2,504,512.81 (11.3%); £2,823,229.87 -> £2,504,512.82 (11.3%); £2,823,229.90 -> £2,504,513.35 (11.3%); £2,823,229.95 -> £2,504,513.35 (11.3%); £2,823,229.99 -> £2,504,513.36 (11.3%); £2,823,230.03 -> £2,504,513.37 (11.3%); £2,823,230.08 -> £2,504,513.37 (11.3%); £2,823,230.12 -> £2,504,513.38 (11.3%); £2,823,230.13 -> £2,504,513.46 (11.3%); £2,823,230.19 -> £2,504,513.47 (11.3%); £2,823,230.25 -> £2,504,513.49 (11.3%); £2,823,230.31 -> £2,504,513.50 (11.3%); £2,823,230.37 -> £2,504,513.51 (11.3%); £2,823,230.42 -> £2,504,513.52 (11.3%); £2,823,230.47 -> £2,504,513.53 (11.3%); £2,823,230.52 -> £2,504,513.54 (11.3%); £2,823,230.58 -> £2,504,514.03 (11.3%); £2,823,230.67 -> £2,504,514.04 (11.3%); £2,823,230.75 -> £2,504,514.04 (11.3%); £2,823,230.83 -> £2,504,514.05 (11.3%); £2,823,230.92 -> £2,504,514.06 (11.3%); £2,823,230.97 -> £2,504,514.06 (11.3%); £2,823,231.01 -> £2,504,514.07 (11.3%); £2,823,231.02 -> £2,504,514.14 (11.3%); £2,823,231.10 -> £2,504,514.16 (11.3%); £2,823,231.19 -> £2,504,514.17 (11.3%); £2,823,231.28 -> £2,504,514.18 (11.3%); £2,823,231.36 -> £2,504,514.19 (11.3%); £2,823,231.45 -> £2,504,514.21 (11.3%); £2,823,231.53 -> £2,504,514.22 (11.3%); £2,823,231.61 -> £2,504,514.23 (11.3%); £2,823,231.64 -> £2,504,516.39 (11.3%); £2,823,231.69 -> £2,504,516.40 (11.3%); £2,823,231.71 -> £2,504,516.86 (11.3%); £2,823,231.76 -> £2,504,516.87 (11.3%); £2,823,231.80 -> £2,504,516.88 (11.3%); £2,823,231.84 -> £2,504,516.88 (11.3%); £2,823,231.88 -> £2,504,516.89 (11.3%); £2,823,231.93 -> £2,504,516.89 (11.3%); £2,823,231.95 -> £2,504,516.95 (11.3%); £2,823,232.01 -> £2,504,516.96 (11.3%); £2,823,232.06 -> £2,504,516.97 (11.3%); £2,823,232.12 -> £2,504,516.97 (11.3%); £2,823,232.17 -> £2,504,516.98 (11.3%); £2,823,232.22 -> £2,504,516.99 (11.3%); £2,823,232.27 -> £2,504,517.00 (11.3%); £2,823,232.36 -> £2,504,517.44 (11.3%); £2,823,232.46 -> £2,504,517.44 (11.3%); £2,823,232.57 -> £2,504,517.45 (11.3%); £2,823,232.67 -> £2,504,517.46 (11.3%); £2,823,232.78 -> £2,504,517.46 (11.3%); £2,823,232.82 -> £2,504,517.47 (11.3%); £2,823,232.87 -> £2,504,517.47 (11.3%); £2,823,232.88 -> £2,504,517.55 (11.3%); £2,823,232.97 -> £2,504,517.56 (11.3%); £2,823,233.09 -> £2,504,517.58 (11.3%); £2,823,233.19 -> £2,504,517.60 (11.3%); £2,823,233.30 -> £2,504,517.61 (11.3%); £2,823,233.41 -> £2,504,517.63 (11.3%); £2,823,233.51 -> £2,504,517.64 (11.3%); £2,823,233.62 -> £2,504,517.65 (11.3%); £2,823,233.71 -> £2,504,518.12 (11.3%); £2,823,233.84 -> £2,504,518.13 (11.3%); £2,823,233.96 -> £2,504,518.14 (11.3%); £2,823,234.08 -> £2,504,518.15 (11.3%); £2,823,234.20 -> £2,504,518.15 (11.3%); £2,823,234.24 -> £2,504,518.16 (11.3%); £2,823,234.29 -> £2,504,518.17 (11.3%); £2,823,234.29 -> £2,504,518.24 (11.3%); £2,823,234.40 -> £2,504,518.26 (11.3%); £2,823,234.52 -> £2,504,518.28 (11.3%); £2,823,234.64 -> £2,504,518.29 (11.3%); £2,823,234.75 -> £2,504,518.31 (11.3%); £2,823,234.87 -> £2,504,518.32 (11.3%); £2,823,234.98 -> £2,504,518.34 (11.3%); £2,823,235.08 -> £2,504,518.35 (11.3%); £2,823,235.13 -> £2,504,518.87 (11.3%); £2,823,235.19 -> £2,504,518.88 (11.3%); £2,823,235.25 -> £2,504,518.89 (11.3%); £2,823,235.31 -> £2,504,518.90 (11.3%); £2,823,235.35 -> £2,504,518.90 (11.3%); £2,823,235.40 -> £2,504,518.91 (11.3%); £2,823,235.40 -> £2,504,518.99 (11.3%); £2,823,235.47 -> £2,504,519.01 (11.3%); £2,823,235.54 -> £2,504,519.02 (11.3%); £2,823,235.61 -> £2,504,519.04 (11.3%); £2,823,235.68 -> £2,504,519.05 (11.3%); £2,823,235.75 -> £2,504,519.07 (11.3%); £2,823,235.81 -> £2,504,519.09 (11.3%); £2,823,235.88 -> £2,504,519.10 (11.3%); £2,823,235.91 -> £2,504,521.44 (11.3%); £2,823,235.96 -> £2,504,521.45 (11.3%); £2,823,236.01 -> £2,504,521.47 (11.3%); £2,823,236.02 -> £2,504,521.88 (11.3%); £2,823,236.06 -> £2,504,521.89 (11.3%); £2,823,236.10 -> £2,504,521.89 (11.3%); £2,823,236.14 -> £2,504,521.90 (11.3%); £2,823,236.19 -> £2,504,521.90 (11.3%); £2,823,236.23 -> £2,504,521.91 (11.3%); £2,823,236.25 -> £2,504,522.04 (11.3%); £2,823,236.31 -> £2,504,522.05 (11.3%); £2,823,236.36 -> £2,504,522.05 (11.3%); £2,823,236.41 -> £2,504,522.05 (11.3%); £2,823,236.46 -> £2,504,522.06 (11.3%); £2,823,236.51 -> £2,504,522.06 (11.3%); £2,823,236.55 -> £2,504,522.07 (11.3%); £2,823,236.58 -> £2,504,522.56 (11.3%); £2,823,236.63 -> £2,504,522.57 (11.3%); £2,823,236.67 -> £2,504,522.58 (11.3%); £2,823,236.72 -> £2,504,522.59 (11.3%); £2,823,236.76 -> £2,504,522.59 (11.3%); £2,823,236.81 -> £2,504,522.60 (11.3%); £2,823,236.81 -> £2,504,522.67 (11.3%); £2,823,236.86 -> £2,504,522.68 (11.3%); £2,823,236.92 -> £2,504,522.70 (11.3%); £2,823,236.98 -> £2,504,522.72 (11.3%); £2,823,237.05 -> £2,504,522.73 (11.3%); £2,823,237.10 -> £2,504,522.75 (11.3%); £2,823,237.16 -> £2,504,522.76 (11.3%); £2,823,237.21 -> £2,504,522.77 (11.3%); £2,823,237.22 -> £2,504,523.30 (11.3%); £2,823,237.26 -> £2,504,523.31 (11.3%); £2,823,237.31 -> £2,504,523.32 (11.3%); £2,823,237.35 -> £2,504,523.33 (11.3%); £2,823,237.40 -> £2,504,523.34 (11.3%); £2,823,237.44 -> £2,504,523.34 (11.3%); £2,823,237.48 -> £2,504,523.35 (11.3%); £2,823,237.53 -> £2,504,523.43 (11.3%); £2,823,237.59 -> £2,504,523.45 (11.3%); £2,823,237.65 -> £2,504,523.47 (11.3%); £2,823,237.71 -> £2,504,523.48 (11.3%); £2,823,237.77 -> £2,504,523.50 (11.3%); £2,823,237.83 -> £2,504,523.51 (11.3%); £2,823,237.88 -> £2,504,523.53 (11.3%); £2,823,237.91 -> £2,504,524.03 (11.3%); £2,823,237.97 -> £2,504,524.04 (11.3%); £2,823,238.03 -> £2,504,524.05 (11.3%); £2,823,238.09 -> £2,504,524.06 (11.3%); £2,823,238.15 -> £2,504,524.06 (11.3%); £2,823,238.20 -> £2,504,524.07 (11.3%); £2,823,238.24 -> £2,504,524.07 (11.3%); £2,823,238.30 -> £2,504,524.15 (11.3%); £2,823,238.37 -> £2,504,524.16 (11.3%); £2,823,238.44 -> £2,504,524.17 (11.3%); £2,823,238.51 -> £2,504,524.18 (11.3%); £2,823,238.57 -> £2,504,524.20 (11.3%); £2,823,238.64 -> £2,504,524.21 (11.3%); £2,823,238.70 -> £2,504,524.22 (11.3%); £2,823,238.72 -> £2,504,526.20 (11.3%); £2,823,238.78 -> £2,504,526.21 (11.3%); £2,823,238.78 -> £2,504,526.71 (11.3%); £2,823,238.90 -> £2,504,526.72 (11.3%); £2,823,239.03 -> £2,504,526.73 (11.3%); £2,823,239.15 -> £2,504,526.73 (11.3%); £2,823,239.26 -> £2,504,526.74 (11.3%); £2,823,239.38 -> £2,504,526.75 (11.3%); £2,823,239.43 -> £2,504,526.75 (11.3%); £2,823,239.47 -> £2,504,526.76 (11.3%); £2,823,239.58 -> £2,504,526.85 (11.3%); £2,823,239.70 -> £2,504,526.86 (11.3%); £2,823,239.82 -> £2,504,526.88 (11.3%); £2,823,239.93 -> £2,504,526.89 (11.3%); £2,823,240.04 -> £2,504,526.90 (11.3%); £2,823,240.15 -> £2,504,526.91 (11.3%); £2,823,240.25 -> £2,504,526.92 (11.3%); £2,823,240.36 -> £2,504,527.40 (11.3%); £2,823,240.50 -> £2,504,527.41 (11.3%); £2,823,240.64 -> £2,504,527.41 (11.3%); £2,823,240.77 -> £2,504,527.42 (11.3%); £2,823,240.89 -> £2,504,527.43 (11.3%); £2,823,240.94 -> £2,504,527.43 (11.3%); £2,823,240.99 -> £2,504,527.44 (11.3%); £2,823,240.99 -> £2,504,527.51 (11.3%); £2,823,241.10 -> £2,504,527.52 (11.3%); £2,823,241.23 -> £2,504,527.54 (11.3%); £2,823,241.35 -> £2,504,527.55 (11.3%); £2,823,241.48 -> £2,504,527.57 (11.3%); £2,823,241.60 -> £2,504,527.58 (11.3%); £2,823,241.72 -> £2,504,527.60 (11.3%); £2,823,241.84 -> £2,504,527.61 (11.3%); £2,823,241.90 -> £2,504,528.10 (11.3%); £2,823,242.01 -> £2,504,528.10 (11.3%); £2,823,242.11 -> £2,504,528.11 (11.3%); £2,823,242.22 -> £2,504,528.12 (11.3%); £2,823,242.33 -> £2,504,528.13 (11.3%); £2,823,242.38 -> £2,504,528.13 (11.3%); £2,823,242.43 -> £2,504,528.14 (11.3%); £2,823,242.53 -> £2,504,528.23 (11.3%); £2,823,242.63 -> £2,504,528.24 (11.3%); £2,823,242.74 -> £2,504,528.26 (11.3%); £2,823,242.84 -> £2,504,528.27 (11.3%); £2,823,242.95 -> £2,504,528.28 (11.3%); £2,823,243.05 -> £2,504,528.29 (11.3%); £2,823,243.14 -> £2,504,528.31 (11.3%); £2,823,243.15 -> £2,504,528.75 (11.3%); £2,823,243.19 -> £2,504,528.76 (11.3%); £2,823,243.23 -> £2,504,528.76 (11.3%); £2,823,243.28 -> £2,504,528.77 (11.3%); £2,823,243.32 -> £2,504,528.77 (11.3%); £2,823,243.36 -> £2,504,528.84 (11.3%); £2,823,243.42 -> £2,504,528.85 (11.3%); £2,823,243.47 -> £2,504,528.86 (11.3%); £2,823,243.52 -> £2,504,528.87 (11.3%); £2,823,243.57 -> £2,504,528.88 (11.3%); £2,823,243.62 -> £2,504,528.89 (11.3%); £2,823,243.67 -> £2,504,528.90 (11.3%); £2,823,243.68 -> £2,504,530.81 (11.3%); £2,823,243.78 -> £2,504,530.82 (11.3%); £2,823,243.87 -> £2,504,530.83 (11.3%); £2,823,243.96 -> £2,504,530.84 (11.3%); £2,823,244.06 -> £2,504,530.85 (11.3%); £2,823,244.15 -> £2,504,530.86 (11.3%); £2,823,244.23 -> £2,504,530.87 (11.3%); £2,823,244.27 -> £2,504,531.38 (11.3%); £2,823,244.32 -> £2,504,531.39 (11.3%); £2,823,244.36 -> £2,504,531.39 (11.3%); £2,823,244.40 -> £2,504,531.40 (11.3%); £2,823,244.45 -> £2,504,531.40 (11.3%); £2,823,244.50 -> £2,504,531.49 (11.3%); £2,823,244.56 -> £2,504,531.51 (11.3%); £2,823,244.62 -> £2,504,531.52 (11.3%); £2,823,244.68 -> £2,504,531.53 (11.3%); £2,823,244.73 -> £2,504,531.55 (11.3%); £2,823,244.78 -> £2,504,531.56 (11.3%); £2,823,244.83 -> £2,504,531.57 (11.3%); £2,823,244.86 -> £2,504,532.03 (11.3%); £2,823,244.91 -> £2,504,532.04 (11.3%); £2,823,244.96 -> £2,504,532.05 (11.3%); £2,823,245.00 -> £2,504,532.05 (11.3%); £2,823,245.05 -> £2,504,532.06 (11.3%); £2,823,245.09 -> £2,504,532.06 (11.3%); £2,823,245.13 -> £2,504,532.13 (11.3%); £2,823,245.19 -> £2,504,532.14 (11.3%); £2,823,245.25 -> £2,504,532.15 (11.3%); £2,823,245.30 -> £2,504,532.16 (11.3%); £2,823,245.35 -> £2,504,532.17 (11.3%); £2,823,245.40 -> £2,504,532.17 (11.3%); £2,823,245.45 -> £2,504,532.18 (11.3%); £2,823,245.57 -> £2,504,532.62 (11.3%); £2,823,245.71 -> £2,504,532.63 (11.3%); £2,823,245.84 -> £2,504,532.64 (11.3%); £2,823,245.98 -> £2,504,532.65 (11.3%); £2,823,246.12 -> £2,504,532.65 (11.3%); £2,823,246.17 -> £2,504,532.66 (11.3%); £2,823,246.22 -> £2,504,532.66 (11.3%); £2,823,246.22 -> £2,504,532.74 (11.3%); £2,823,246.34 -> £2,504,532.75 (11.3%); £2,823,246.46 -> £2,504,532.76 (11.3%); £2,823,246.59 -> £2,504,532.78 (11.3%); £2,823,246.72 -> £2,504,532.79 (11.3%); £2,823,246.84 -> £2,504,532.80 (11.3%); £2,823,246.96 -> £2,504,532.81 (11.3%); £2,823,247.08 -> £2,504,532.82 (11.3%); £2,823,247.23 -> £2,504,533.30 (11.3%); £2,823,247.42 -> £2,504,533.31 (11.3%); £2,823,247.59 -> £2,504,533.32 (11.3%); £2,823,247.78 -> £2,504,533.33 (11.3%); £2,823,247.96 -> £2,504,533.34 (11.3%); £2,823,248.01 -> £2,504,533.34 (11.3%); £2,823,248.05 -> £2,504,533.35 (11.3%); £2,823,248.21 -> £2,504,533.44 (11.3%); £2,823,248.37 -> £2,504,533.45 (11.3%); £2,823,248.53 -> £2,504,533.47 (11.3%); £2,823,248.69 -> £2,504,533.48 (11.3%); £2,823,248.84 -> £2,504,533.49 (11.3%); £2,823,248.99 -> £2,504,533.50 (11.3%); £2,823,249.13 -> £2,504,533.51 (11.3%); £2,823,249.15 -> £2,504,536.13 (11.3%); £2,823,249.19 -> £2,504,536.14 (11.3%); £2,823,249.23 -> £2,504,536.15 (11.3%); £2,823,249.28 -> £2,504,536.16 (11.3%); £2,823,249.33 -> £2,504,536.16 (11.3%); £2,823,249.38 -> £2,504,536.25 (11.3%); £2,823,249.44 -> £2,504,536.26 (11.3%); £2,823,249.49 -> £2,504,536.27 (11.3%); £2,823,249.54 -> £2,504,536.28 (11.3%); £2,823,249.60 -> £2,504,536.29 (11.3%); £2,823,249.64 -> £2,504,536.30 (11.3%); £2,823,249.69 -> £2,504,536.31 (11.3%); £2,823,249.70 -> £2,504,536.77 (11.3%); £2,823,249.74 -> £2,504,536.78 (11.3%); £2,823,249.79 -> £2,504,536.78 (11.3%); £2,823,249.83 -> £2,504,536.79 (11.3%); £2,823,249.88 -> £2,504,536.80 (11.3%); £2,823,249.92 -> £2,504,536.80 (11.3%); £2,823,249.97 -> £2,504,536.88 (11.3%); £2,823,250.02 -> £2,504,536.89 (11.3%); £2,823,250.07 -> £2,504,536.90 (11.3%); £2,823,250.13 -> £2,504,536.91 (11.3%); £2,823,250.18 -> £2,504,536.91 (11.3%); £2,823,250.22 -> £2,504,536.92 (11.3%); £2,823,250.27 -> £2,504,536.93 (11.3%); £2,823,250.30 -> £2,504,537.35 (11.3%); £2,823,250.34 -> £2,504,537.35 (11.3%); £2,823,250.38 -> £2,504,537.36 (11.3%); £2,823,250.42 -> £2,504,537.36 (11.3%); £2,823,250.47 -> £2,504,537.37 (11.3%); £2,823,250.50 -> £2,504,537.43 (11.3%); £2,823,250.55 -> £2,504,537.44 (11.3%); £2,823,250.61 -> £2,504,537.44 (11.3%); £2,823,250.65 -> £2,504,537.45 (11.3%); £2,823,250.70 -> £2,504,537.45 (11.3%); £2,823,250.75 -> £2,504,537.45 (11.3%); £2,823,250.79 -> £2,504,537.47 (11.3%); £2,823,250.81 -> £2,504,537.85 (11.3%); £2,823,250.85 -> £2,504,537.86 (11.3%); £2,823,250.89 -> £2,504,537.86 (11.3%); £2,823,250.94 -> £2,504,537.87 (11.3%); £2,823,250.98 -> £2,504,537.87 (11.3%); £2,823,251.03 -> £2,504,537.97 (11.3%); £2,823,251.09 -> £2,504,537.99 (11.3%); £2,823,251.14 -> £2,504,538.00 (11.3%); £2,823,251.19 -> £2,504,538.01 (11.3%); £2,823,251.25 -> £2,504,538.01 (11.3%); £2,823,251.29 -> £2,504,538.02 (11.3%); £2,823,251.34 -> £2,504,538.03 (11.3%); £2,823,251.35 -> £2,504,540.16 (11.3%); £2,823,251.39 -> £2,504,540.17 (11.3%); £2,823,251.44 -> £2,504,540.17 (11.3%); £2,823,251.45 -> £2,504,540.22 (11.3%); £2,823,251.51 -> £2,504,540.22 (11.3%); £2,823,251.57 -> £2,504,540.23 (11.3%); £2,823,251.62 -> £2,504,540.23 (11.3%); £2,823,251.67 -> £2,504,540.24 (11.3%); £2,823,251.72 -> £2,504,540.25 (11.3%); £2,823,251.77 -> £2,504,540.26 (11.3%); £2,823,251.87 -> £2,504,540.73 (11.3%); £2,823,251.98 -> £2,504,540.74 (11.3%); £2,823,252.09 -> £2,504,540.75 (11.3%); £2,823,252.21 -> £2,504,540.75 (11.3%); £2,823,252.31 -> £2,504,540.75 (11.3%); £2,823,252.35 -> £2,504,540.76 (11.3%); £2,823,252.40 -> £2,504,540.76 (11.3%); £2,823,252.45 -> £2,504,540.80 (11.3%); £2,823,252.55 -> £2,504,540.81 (11.3%); £2,823,252.64 -> £2,504,540.81 (11.3%); £2,823,252.74 -> £2,504,540.82 (11.3%); £2,823,252.83 -> £2,504,540.83 (11.3%); £2,823,252.93 -> £2,504,540.84 (11.3%); £2,823,253.03 -> £2,504,540.85 (11.3%); £2,823,253.04 -> £2,504,541.20 (11.3%); £2,823,253.09 -> £2,504,541.21 (11.3%); £2,823,253.13 -> £2,504,541.21 (11.3%); £2,823,253.18 -> £2,504,541.22 (11.3%); £2,823,253.22 -> £2,504,541.22 (11.3%); £2,823,253.27 -> £2,504,541.30 (11.3%); £2,823,253.33 -> £2,504,541.31 (11.3%); £2,823,253.39 -> £2,504,541.33 (11.3%); £2,823,253.45 -> £2,504,541.34 (11.3%); £2,823,253.51 -> £2,504,541.35 (11.3%); £2,823,253.57 -> £2,504,541.36 (11.3%); £2,823,253.63 -> £2,504,541.38 (11.3%); £2,823,253.69 -> £2,504,541.79 (11.3%); £2,823,253.80 -> £2,504,541.79 (11.3%); £2,823,253.91 -> £2,504,541.80 (11.3%); £2,823,254.02 -> £2,504,541.81 (11.3%); £2,823,254.13 -> £2,504,541.81 (11.3%); £2,823,254.18 -> £2,504,541.82 (11.3%); £2,823,254.23 -> £2,504,541.82 (11.3%); £2,823,254.33 -> £2,504,541.91 (11.3%); £2,823,254.44 -> £2,504,541.92 (11.3%); £2,823,254.54 -> £2,504,541.93 (11.3%); £2,823,254.65 -> £2,504,541.94 (11.3%); £2,823,254.76 -> £2,504,541.96 (11.3%); £2,823,254.87 -> £2,504,541.97 (11.3%); £2,823,254.97 -> £2,504,541.98 (11.3%); £2,823,255.04 -> £2,504,543.65 (11.3%); £2,823,255.15 -> £2,504,543.66 (11.3%); £2,823,255.24 -> £2,504,543.67 (11.3%); £2,823,255.35 -> £2,504,543.68 (11.3%); £2,823,255.38 -> £2,504,544.07 (11.3%); £2,823,255.42 -> £2,504,544.07 (11.3%); £2,823,255.46 -> £2,504,544.08 (11.3%); £2,823,255.50 -> £2,504,544.08 (11.3%); £2,823,255.56 -> £2,504,544.13 (11.3%); £2,823,255.61 -> £2,504,544.13 (11.3%); £2,823,255.66 -> £2,504,544.14 (11.3%); £2,823,255.70 -> £2,504,544.14 (11.3%); £2,823,255.75 -> £2,504,544.14 (11.3%); £2,823,255.79 -> £2,504,544.15 (11.3%); £2,823,255.81 -> £2,504,544.42 (11.3%); £2,823,255.85 -> £2,504,544.42 (11.3%); £2,823,255.90 -> £2,504,544.43 (11.3%); £2,823,255.94 -> £2,504,544.43 (11.3%); £2,823,255.97 -> £2,504,544.50 (11.3%); £2,823,256.03 -> £2,504,544.50 (11.3%); £2,823,256.08 -> £2,504,544.51 (11.3%); £2,823,256.12 -> £2,504,544.51 (11.3%); £2,823,256.17 -> £2,504,544.51 (11.3%); £2,823,256.21 -> £2,504,544.51 (11.3%); £2,823,256.26 -> £2,504,544.52 (11.3%); £2,823,256.29 -> £2,504,544.86 (11.3%); £2,823,256.37 -> £2,504,544.86 (11.3%); £2,823,256.45 -> £2,504,544.87 (11.3%); £2,823,256.54 -> £2,504,544.87 (11.3%); £2,823,256.58 -> £2,504,544.87 (11.3%); £2,823,256.62 -> £2,504,544.87 (11.3%); £2,823,256.64 -> £2,504,544.91 (11.3%); £2,823,256.73 -> £2,504,544.92 (11.3%); £2,823,256.82 -> £2,504,544.93 (11.3%); £2,823,256.91 -> £2,504,544.95 (11.3%); £2,823,257.00 -> £2,504,544.96 (11.3%); £2,823,257.09 -> £2,504,544.97 (11.3%); £2,823,257.17 -> £2,504,544.98 (11.3%); £2,823,257.25 -> £2,504,545.26 (11.3%); £2,823,257.35 -> £2,504,545.27 (11.3%); £2,823,257.47 -> £2,504,545.27 (11.3%); £2,823,257.57 -> £2,504,545.28 (11.3%); £2,823,257.62 -> £2,504,545.28 (11.3%); £2,823,257.66 -> £2,504,545.29 (11.3%); £2,823,257.69 -> £2,504,545.32 (11.3%); £2,823,257.80 -> £2,504,545.32 (11.3%); £2,823,257.89 -> £2,504,545.33 (11.3%); £2,823,257.99 -> £2,504,545.35 (11.3%); £2,823,258.10 -> £2,504,545.35 (11.3%); £2,823,258.19 -> £2,504,545.36 (11.3%); £2,823,258.28 -> £2,504,545.36 (11.3%); £2,823,258.33 -> £2,504,547.31 (11.3%); £2,823,258.38 -> £2,504,547.31 (11.3%); £2,823,258.42 -> £2,504,547.32 (11.3%); £2,823,258.50 -> £2,504,547.39 (11.3%); £2,823,258.59 -> £2,504,547.40 (11.3%); £2,823,258.69 -> £2,504,547.41 (11.3%); £2,823,258.78 -> £2,504,547.42 (11.3%); £2,823,258.87 -> £2,504,547.43 (11.3%); £2,823,258.97 -> £2,504,547.44 (11.3%); £2,823,259.06 -> £2,504,547.45 (11.3%); £2,823,259.21 -> £2,504,547.91 (11.3%); £2,823,259.36 -> £2,504,547.92 (11.3%); £2,823,259.52 -> £2,504,547.93 (11.3%); £2,823,259.69 -> £2,504,547.94 (11.3%); £2,823,259.86 -> £2,504,547.94 (11.3%); £2,823,259.91 -> £2,504,547.95 (11.3%); £2,823,259.95 -> £2,504,547.95 (11.3%); £2,823,260.08 -> £2,504,548.03 (11.3%); £2,823,260.22 -> £2,504,548.03 (11.3%); £2,823,260.35 -> £2,504,548.05 (11.3%); £2,823,260.50 -> £2,504,548.06 (11.3%); £2,823,260.65 -> £2,504,548.07 (11.3%); £2,823,260.78 -> £2,504,548.08 (11.3%); £2,823,260.92 -> £2,504,548.10 (11.3%); £2,823,260.92 -> £2,504,548.61 (11.3%); £2,823,261.05 -> £2,504,548.62 (11.3%); £2,823,261.19 -> £2,504,548.63 (11.3%); £2,823,261.32 -> £2,504,548.63 (11.3%); £2,823,261.44 -> £2,504,548.64 (11.3%); £2,823,261.56 -> £2,504,548.64 (11.3%); £2,823,261.61 -> £2,504,548.64 (11.3%); £2,823,261.65 -> £2,504,548.65 (11.3%); £2,823,261.73 -> £2,504,548.70 (11.3%); £2,823,261.85 -> £2,504,548.71 (11.3%); £2,823,261.95 -> £2,504,548.71 (11.3%); £2,823,262.06 -> £2,504,548.72 (11.3%); £2,823,262.17 -> £2,504,548.72 (11.3%); £2,823,262.27 -> £2,504,548.73 (11.3%); £2,823,262.38 -> £2,504,548.74 (11.3%); £2,823,262.45 -> £2,504,549.10 (11.3%); £2,823,262.51 -> £2,504,549.10 (11.3%); £2,823,262.58 -> £2,504,549.10 (11.3%); £2,823,262.62 -> £2,504,549.11 (11.3%); £2,823,262.66 -> £2,504,549.11 (11.3%); £2,823,262.71 -> £2,504,549.17 (11.3%); £2,823,262.78 -> £2,504,549.19 (11.3%); £2,823,262.86 -> £2,504,549.20 (11.3%); £2,823,262.93 -> £2,504,549.21 (11.3%); £2,823,263.01 -> £2,504,549.22 (11.3%); £2,823,263.08 -> £2,504,549.24 (11.3%); £2,823,263.16 -> £2,504,549.25 (11.3%); £2,823,263.19 -> £2,504,551.24 (11.3%); £2,823,263.26 -> £2,504,551.26 (11.3%); £2,823,263.32 -> £2,504,551.27 (11.3%); £2,823,263.35 -> £2,504,551.76 (11.3%); £2,823,263.40 -> £2,504,551.77 (11.3%); £2,823,263.45 -> £2,504,551.78 (11.3%); £2,823,263.50 -> £2,504,551.79 (11.3%); £2,823,263.55 -> £2,504,551.79 (11.3%); £2,823,263.59 -> £2,504,551.80 (11.3%); £2,823,263.60 -> £2,504,551.87 (11.3%); £2,823,263.65 -> £2,504,551.89 (11.3%); £2,823,263.72 -> £2,504,551.90 (11.3%); £2,823,263.78 -> £2,504,551.91 (11.3%); £2,823,263.85 -> £2,504,551.93 (11.3%); £2,823,263.93 -> £2,504,551.95 (11.3%); £2,823,264.00 -> £2,504,551.96 (11.3%); £2,823,264.07 -> £2,504,551.97 (11.3%); £2,823,264.07 -> £2,504,552.50 (11.3%); £2,823,264.13 -> £2,504,552.51 (11.3%); £2,823,264.18 -> £2,504,552.52 (11.3%); £2,823,264.23 -> £2,504,552.53 (11.3%); £2,823,264.27 -> £2,504,552.54 (11.3%); £2,823,264.32 -> £2,504,552.54 (11.3%); £2,823,264.37 -> £2,504,552.55 (11.3%); £2,823,264.39 -> £2,504,552.64 (11.3%); £2,823,264.45 -> £2,504,552.66 (11.3%); £2,823,264.52 -> £2,504,552.68 (11.3%); £2,823,264.59 -> £2,504,552.69 (11.3%); £2,823,264.65 -> £2,504,552.70 (11.3%); £2,823,264.72 -> £2,504,552.71 (11.3%); £2,823,264.79 -> £2,504,552.72 (11.3%); £2,823,264.85 -> £2,504,552.73 (11.3%); £2,823,264.90 -> £2,504,553.21 (11.3%); £2,823,264.96 -> £2,504,553.21 (11.3%); £2,823,265.01 -> £2,504,553.22 (11.3%); £2,823,265.06 -> £2,504,553.23 (11.3%); £2,823,265.11 -> £2,504,553.23 (11.3%); £2,823,265.15 -> £2,504,553.24 (11.3%); £2,823,265.21 -> £2,504,553.32 (11.3%); £2,823,265.28 -> £2,504,553.34 (11.3%); £2,823,265.36 -> £2,504,553.36 (11.3%); £2,823,265.43 -> £2,504,553.38 (11.3%); £2,823,265.52 -> £2,504,553.40 (11.3%); £2,823,265.60 -> £2,504,553.42 (11.3%); £2,823,265.67 -> £2,504,553.44 (11.3%); £2,823,265.70 -> £2,504,553.92 (11.3%); £2,823,265.78 -> £2,504,553.93 (11.3%); £2,823,265.85 -> £2,504,553.94 (11.3%); £2,823,265.92 -> £2,504,553.95 (11.3%); £2,823,265.99 -> £2,504,553.95 (11.3%); £2,823,266.04 -> £2,504,553.96 (11.3%); £2,823,266.08 -> £2,504,553.97 (11.3%); £2,823,266.08 -> £2,504,554.04 (11.3%); £2,823,266.16 -> £2,504,554.06 (11.3%); £2,823,266.25 -> £2,504,554.08 (11.3%); £2,823,266.33 -> £2,504,554.10 (11.3%); £2,823,266.42 -> £2,504,554.11 (11.3%); £2,823,266.51 -> £2,504,554.13 (11.3%); £2,823,266.60 -> £2,504,554.14 (11.3%); £2,823,266.69 -> £2,504,554.16 (11.3%); £2,823,266.74 -> £2,504,556.25 (11.3%); £2,823,266.85 -> £2,504,556.27 (11.3%); £2,823,266.96 -> £2,504,556.28 (11.3%); £2,823,267.10 -> £2,504,556.77 (11.3%); £2,823,267.26 -> £2,504,556.78 (11.3%); £2,823,267.41 -> £2,504,556.79 (11.3%); £2,823,267.56 -> £2,504,556.80 (11.3%); £2,823,267.71 -> £2,504,556.80 (11.3%); £2,823,267.76 -> £2,504,556.81 (11.3%); £2,823,267.81 -> £2,504,556.82 (11.3%); £2,823,267.93 -> £2,504,556.90 (11.3%); £2,823,268.08 -> £2,504,556.91 (11.3%); £2,823,268.21 -> £2,504,556.92 (11.3%); £2,823,268.34 -> £2,504,556.94 (11.3%); £2,823,268.48 -> £2,504,556.96 (11.3%); £2,823,268.63 -> £2,504,556.97 (11.3%); £2,823,268.78 -> £2,504,556.99 (11.3%); £2,823,268.94 -> £2,504,557.47 (11.3%); £2,823,269.11 -> £2,504,557.47 (11.3%); £2,823,269.28 -> £2,504,557.47 (11.3%); £2,823,269.44 -> £2,504,557.48 (11.3%); £2,823,269.61 -> £2,504,557.48 (11.3%); £2,823,269.66 -> £2,504,557.49 (11.3%); £2,823,269.70 -> £2,504,557.49 (11.3%); £2,823,269.83 -> £2,504,557.56 (11.3%); £2,823,269.98 -> £2,504,557.57 (11.3%); £2,823,270.14 -> £2,504,557.58 (11.3%); £2,823,270.29 -> £2,504,557.59 (11.3%); £2,823,270.45 -> £2,504,557.61 (11.3%); £2,823,270.63 -> £2,504,557.62 (11.3%); £2,823,270.79 -> £2,504,557.64 (11.3%); £2,823,270.83 -> £2,504,558.09 (11.3%); £2,823,271.07 -> £2,504,558.09 (11.3%); £2,823,271.30 -> £2,504,558.10 (11.3%); £2,823,271.54 -> £2,504,558.10 (11.3%); £2,823,271.76 -> £2,504,558.11 (11.3%); £2,823,272.01 -> £2,504,558.12 (11.3%); £2,823,272.06 -> £2,504,558.12 (11.3%); £2,823,272.10 -> £2,504,558.13 (11.3%); £2,823,272.30 -> £2,504,558.22 (11.3%); £2,823,272.51 -> £2,504,558.23 (11.3%); £2,823,272.71 -> £2,504,558.24 (11.3%); £2,823,272.91 -> £2,504,558.26 (11.3%); £2,823,273.13 -> £2,504,558.28 (11.3%); £2,823,273.35 -> £2,504,558.30 (11.3%); £2,823,273.57 -> £2,504,558.31 (11.3%); £2,823,273.63 -> £2,504,558.83 (11.3%); £2,823,273.92 -> £2,504,558.84 (11.3%); £2,823,274.23 -> £2,504,558.85 (11.3%); £2,823,274.52 -> £2,504,558.86 (11.3%); £2,823,274.83 -> £2,504,558.87 (11.3%); £2,823,275.14 -> £2,504,558.87 (11.3%); £2,823,275.19 -> £2,504,558.88 (11.3%); £2,823,275.24 -> £2,504,558.89 (11.3%); £2,823,275.24 -> £2,504,558.97 (11.3%); £2,823,275.50 -> £2,504,558.99 (11.3%); £2,823,275.76 -> £2,504,559.01 (11.3%); £2,823,276.02 -> £2,504,559.02 (11.3%); £2,823,276.27 -> £2,504,559.04 (11.3%); £2,823,276.53 -> £2,504,559.06 (11.3%); £2,823,276.79 -> £2,504,559.08 (11.3%); £2,823,277.05 -> £2,504,559.09 (11.3%); £2,823,277.10 -> £2,504,561.38 (11.3%); £2,823,277.30 -> £2,504,561.38 (11.3%); £2,823,277.35 -> £2,504,561.39 (11.3%); £2,823,277.39 -> £2,504,561.40 (11.3%); £2,823,277.56 -> £2,504,561.47 (11.3%); £2,823,277.74 -> £2,504,561.49 (11.3%); £2,823,277.92 -> £2,504,561.50 (11.3%); £2,823,278.10 -> £2,504,561.51 (11.3%); £2,823,278.28 -> £2,504,561.54 (11.3%); £2,823,278.49 -> £2,504,561.56 (11.3%); £2,823,278.68 -> £2,504,561.58 (11.3%); £2,823,278.82 -> £2,504,562.14 (11.3%); £2,823,278.96 -> £2,504,562.15 (11.3%); £2,823,279.09 -> £2,504,562.15 (11.3%); £2,823,279.22 -> £2,504,562.16 (11.3%); £2,823,279.35 -> £2,504,562.16 (11.3%); £2,823,279.40 -> £2,504,562.17 (11.3%); £2,823,279.44 -> £2,504,562.17 (11.3%); £2,823,279.45 -> £2,504,562.25 (11.3%); £2,823,279.57 -> £2,504,562.27 (11.3%); £2,823,279.71 -> £2,504,562.28 (11.3%); £2,823,279.84 -> £2,504,562.30 (11.3%); £2,823,279.98 -> £2,504,562.31 (11.3%); £2,823,280.10 -> £2,504,562.34 (11.3%); £2,823,280.25 -> £2,504,562.36 (11.3%); £2,823,280.39 -> £2,504,562.38 (11.3%); £2,823,280.48 -> £2,504,562.91 (11.3%); £2,823,280.58 -> £2,504,562.91 (11.3%); £2,823,280.68 -> £2,504,562.92 (11.3%); £2,823,280.77 -> £2,504,562.92 (11.3%); £2,823,280.86 -> £2,504,562.93 (11.3%); £2,823,280.91 -> £2,504,562.93 (11.3%); £2,823,280.95 -> £2,504,562.94 (11.3%); £2,823,280.95 -> £2,504,563.02 (11.3%); £2,823,281.06 -> £2,504,563.04 (11.3%); £2,823,281.16 -> £2,504,563.05 (11.3%); £2,823,281.27 -> £2,504,563.06 (11.3%); £2,823,281.37 -> £2,504,563.08 (11.3%); £2,823,281.48 -> £2,504,563.09 (11.3%); £2,823,281.59 -> £2,504,563.11 (11.3%); £2,823,281.70 -> £2,504,563.12 (11.3%); £2,823,281.78 -> £2,504,563.62 (11.3%); £2,823,281.89 -> £2,504,563.63 (11.3%); £2,823,282.01 -> £2,504,563.64 (11.3%); £2,823,282.12 -> £2,504,563.65 (11.3%); £2,823,282.23 -> £2,504,563.65 (11.3%); £2,823,282.27 -> £2,504,563.66 (11.3%); £2,823,282.32 -> £2,504,563.66 (11.3%); £2,823,282.40 -> £2,504,563.73 (11.3%); £2,823,282.50 -> £2,504,563.74 (11.3%); £2,823,282.61 -> £2,504,563.74 (11.3%); £2,823,282.71 -> £2,504,563.75 (11.3%); £2,823,282.82 -> £2,504,563.76 (11.3%); £2,823,282.93 -> £2,504,563.77 (11.3%); £2,823,283.04 -> £2,504,563.78 (11.3%); £2,823,283.07 -> £2,504,564.18 (11.3%); £2,823,283.29 -> £2,504,564.19 (11.3%); £2,823,283.52 -> £2,504,564.20 (11.3%); £2,823,283.75 -> £2,504,564.20 (11.3%); £2,823,283.97 -> £2,504,564.21 (11.3%); £2,823,284.19 -> £2,504,564.21 (11.3%); £2,823,284.24 -> £2,504,564.21 (11.3%); £2,823,284.28 -> £2,504,564.22 (11.3%); £2,823,284.28 -> £2,504,564.30 (11.3%); £2,823,284.49 -> £2,504,564.32 (11.3%); £2,823,284.70 -> £2,504,564.33 (11.3%); £2,823,284.91 -> £2,504,564.35 (11.3%); £2,823,285.13 -> £2,504,564.37 (11.3%); £2,823,285.35 -> £2,504,564.39 (11.3%); £2,823,285.56 -> £2,504,564.41 (11.3%); £2,823,285.78 -> £2,504,564.43 (11.3%); £2,823,285.87 -> £2,504,566.70 (11.3%); £2,823,286.14 -> £2,504,566.70 (11.3%); £2,823,286.18 -> £2,504,566.71 (11.3%); £2,823,286.23 -> £2,504,566.72 (11.3%); £2,823,286.24 -> £2,504,566.80 (11.3%); £2,823,286.47 -> £2,504,566.82 (11.3%); £2,823,286.71 -> £2,504,566.83 (11.3%); £2,823,286.93 -> £2,504,566.85 (11.3%); £2,823,287.17 -> £2,504,566.87 (11.3%); £2,823,287.40 -> £2,504,566.88 (11.3%); £2,823,287.64 -> £2,504,566.90 (11.3%); £2,823,287.88 -> £2,504,566.92 (11.3%); £2,823,288.02 -> £2,504,567.44 (11.3%); £2,823,288.35 -> £2,504,567.45 (11.3%); £2,823,288.69 -> £2,504,567.46 (11.3%); £2,823,289.01 -> £2,504,567.47 (11.3%); £2,823,289.33 -> £2,504,567.48 (11.3%); £2,823,289.64 -> £2,504,567.48 (11.3%); £2,823,289.69 -> £2,504,567.49 (11.3%); £2,823,289.74 -> £2,504,567.49 (11.3%); £2,823,289.98 -> £2,504,567.57 (11.3%); £2,823,290.24 -> £2,504,567.58 (11.3%); £2,823,290.49 -> £2,504,567.59 (11.3%); £2,823,290.74 -> £2,504,567.61 (11.3%); £2,823,291.00 -> £2,504,567.62 (11.3%); £2,823,291.26 -> £2,504,567.64 (11.3%); £2,823,291.53 -> £2,504,567.66 (11.3%); £2,823,291.76 -> £2,504,568.14 (11.3%); £2,823,292.05 -> £2,504,568.15 (11.3%); £2,823,292.34 -> £2,504,568.16 (11.3%); £2,823,292.62 -> £2,504,568.17 (11.3%); £2,823,292.91 -> £2,504,568.17 (11.3%); £2,823,292.95 -> £2,504,568.18 (11.3%); £2,823,293.00 -> £2,504,568.18 (11.3%); £2,823,293.23 -> £2,504,568.28 (11.3%); £2,823,293.48 -> £2,504,568.29 (11.3%); £2,823,293.70 -> £2,504,568.30 (11.3%); £2,823,293.92 -> £2,504,568.30 (11.3%); £2,823,294.14 -> £2,504,568.31 (11.3%); £2,823,294.37 -> £2,504,568.32 (11.3%); £2,823,294.60 -> £2,504,568.34 (11.3%); £2,823,294.75 -> £2,504,568.87 (11.3%); £2,823,294.95 -> £2,504,568.88 (11.3%); £2,823,295.14 -> £2,504,568.88 (11.3%); £2,823,295.32 -> £2,504,568.89 (11.3%); £2,823,295.51 -> £2,504,568.90 (11.3%); £2,823,295.56 -> £2,504,568.90 (11.3%); £2,823,295.60 -> £2,504,568.91 (11.3%); £2,823,295.77 -> £2,504,569.00 (11.3%); £2,823,295.95 -> £2,504,569.01 (11.3%); £2,823,296.12 -> £2,504,569.03 (11.3%); £2,823,296.30 -> £2,504,569.05 (11.3%); £2,823,296.49 -> £2,504,569.07 (11.3%); £2,823,296.67 -> £2,504,569.09 (11.3%); £2,823,296.86 -> £2,504,569.11 (11.3%); £2,823,954.06 -> £2,504,569.30 (11.3%); £2,824,020.47 -> £2,504,651.25 (11.3%); £2,824,020.61 -> £2,504,651.65 (11.3%); £2,824,020.98 -> £2,504,651.67 (11.3%); £2,824,021.37 -> £2,504,651.68 (11.3%); £2,824,021.73 -> £2,504,651.70 (11.3%); £2,824,022.11 -> £2,504,651.71 (11.3%); £2,824,022.48 -> £2,504,651.72 (11.3%); £2,824,022.51 -> £2,504,651.73 (11.3%); £2,824,022.55 -> £2,504,574.84 (11.3%); £2,824,022.82 -> £2,504,564.65 (11.3%); £2,824,023.25 -> £2,504,554.40 (11.3%); £2,824,023.66 -> £2,504,544.42 (11.3%); £2,824,024.08 -> £2,504,533.83 (11.3%); £2,824,024.51 -> £2,504,523.09 (11.3%); £2,824,024.92 -> £2,504,512.85 (11.3%); £2,824,025.34 -> £2,504,436.37 (11.3%); £3,030,878.14 -> £2,504,652.35 (17.4%)
- Bills issued: 156, average clarity 0.833, average bill shock 19.6%, bad debt provision £74,337.28, avg complaint probability 4.9%
- Solvency signal: £250,465/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £78,242.28 vs. naked (unhedged) net margin: £1,226,011.08
- hedging cost £1,147,768.80 vs. a fully unhedged book (commodity-only: actual net £78,242.28 vs. naked net £1,226,011.08)
  - C2: actual £265.06 vs. naked £1,093.40 -- hedging cost £828.34
  - C2g: actual £91.37 vs. naked £252.93 -- hedging cost £161.57
  - C4: actual £-335.89 vs. naked £1,016.69 -- hedging cost £1,352.58
  - C4g: actual £402.23 vs. naked £2,662.09 -- hedging cost £2,259.86
  - C6: actual £378.99 vs. naked £2,343.52 -- hedging cost £1,964.53
  - C7: actual £804.16 vs. naked £3,194.84 -- hedging cost £2,390.68
  - C8: actual £508.88 vs. naked £1,594.70 -- hedging cost £1,085.82
  - C9: actual £730.00 vs. naked £1,489.99 -- hedging cost £759.99
  - C_IC1: actual £232,501.91 vs. naked £246,214.18 -- hedging cost £13,712.26
  - C_IC2: actual £85,041.55 vs. naked £111,400.83 -- hedging cost £26,359.27
  - C_IC3: actual £205,926.81 vs. naked £809,936.44 -- hedging cost £604,009.62
  - C_IC3g: actual £-252,917.30 vs. naked £83,300.79 -- hedging cost £336,218.09
  - C_IC4: actual £-195,155.50 vs. naked £-38,489.32 -- hedging cost £156,666.18

**Year narrative:** 2022 (flagged crisis year) produced a net loss of £-66,017.09 across 13 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 51 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £103,535.76 (gross £905,771.24, capital £10,049.61)
  - Electricity: gross £1,044,749.78, capital £9,633.42, net £355,704.86
  - Gas: gross £-138,978.55, capital £416.18, net £-252,169.10
- Treasury at year end: £2,583,231.55
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.94 (avg 0.94), C2g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.94 (avg 0.94), C9 0.93 (avg 0.93), C_IC1 0.85 (avg 0.89), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.90 (avg 0.90), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £2,504,665.97, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £119,946.88 / stressed £43,344.35) ratio 2.77
  - 2023-02-23: treasury £2,504,682.03, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £119,946.88 / stressed £43,344.35) ratio 2.77
  - 2023-03-25: treasury £2,504,698.41, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £119,946.88 / stressed £43,344.35) ratio 2.77
  - 2023-04-24: treasury £2,584,827.26, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £124,441.78 / stressed £47,295.64) ratio 2.63
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-07-01 period 1, net margin £-813.88

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £211,209.73
  - By billing account: C1 £1,740.15, C2 £5,193.93, C3 £2,065.68, C4 £2,579.56, C5 £5,842.75, C6 £8,841.75, C7 £4,809.04, C8 £6,410.41, C9 £5,992.71, C_IC1 £978,272.86, C_IC2 £499,273.59, C_IC3 £1,207,129.88, C_IC4 £17,574.25
- Bill shock events (>=20%): 31 -- C7 2023-01-31 (36%); C7 2023-05-31 (33%); C7 2023-06-30 (38%); C7 2023-10-31 (58%); C7 2023-11-30 (74%); C6 2023-04-30 (23%); C6 2023-05-31 (24%); C6 2023-06-30 (23%); C6 2023-10-31 (39%); C6 2023-11-30 (44%); C8 2023-04-30 (23%); C8 2023-05-31 (41%); C8 2023-06-30 (45%); C8 2023-10-31 (102%); C8 2023-11-30 (71%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (23%); C9 2023-10-31 (77%); C9 2023-11-30 (55%); C4g 2023-10-31 (63%); C_IC1 2023-06-30 (54%); C_IC1 2023-07-31 (102%); C_IC2 2023-05-31 (54%); C_IC2 2023-06-30 (131%); C_IC3 2023-01-31 (35%); C_IC3g 2023-01-31 (34%); C_IC4 2023-01-31 (46%)
- Churn risk (accounts renewing in 2023): 6 at risk (≥20% churn prob): C2 20%, C6 29%, C7 38%, C8 38%, C9 41%, C_IC4 32%

**Pricing & Margin**

- C2 (electricity): tariff £376.94-£378.95/MWh, net margin £601.13
- C2g (gas): tariff £115.89-£136.85/MWh, net margin £909.51
- C4 (electricity): tariff £235.01-£341.81/MWh, net margin £-211.04 -- **net-negative**
- C4g (gas): tariff £54.68-£180.61/MWh, net margin £336.49
- C6 (electricity): tariff £357.39-£372.04/MWh, net margin £1,017.19
- C7 (electricity): tariff £167.10-£579.61/MWh, net margin £795.69
- C8 (electricity): tariff £278.84-£533.82/MWh, net margin £960.83
- C9 (electricity): tariff £228.93-£464.47/MWh, net margin £888.77
- C_IC1 (electricity): tariff £-60.00-£450.61/MWh, net margin £239,666.61
- C_IC2 (electricity): tariff £-186.24-£446.89/MWh, net margin £101,293.82
- C_IC3 (electricity): tariff £76.02-£405.13/MWh, net margin £205,967.85
- C_IC3g (gas): tariff £53.75-£148.54/MWh, net margin £-253,415.10 -- **net-negative**
- C_IC4 (electricity): tariff £36.40-£169.32/MWh, net margin £-195,275.98 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): 63 -- £3,030,439.45 -> £2,504,653.27 (17.4%); £3,030,476.21 -> £2,583,226.15 (14.8%); £3,030,524.74 -> £2,583,226.22 (14.8%); £3,030,571.69 -> £2,583,226.29 (14.8%); £3,030,618.89 -> £2,583,226.35 (14.8%); £3,030,664.50 -> £2,583,226.42 (14.8%); £3,030,666.35 -> £2,583,226.48 (14.8%); £3,030,668.20 -> £2,583,226.54 (14.8%); £3,030,669.22 -> £2,583,226.59 (14.8%); £3,030,670.24 -> £2,583,216.91 (14.8%); £3,030,671.62 -> £2,583,203.20 (14.8%); £3,030,673.06 -> £2,583,190.84 (14.8%); £3,030,674.31 -> £2,583,179.43 (14.8%); £3,030,675.64 -> £2,583,168.73 (14.8%); £3,030,677.70 -> £2,583,161.52 (14.8%); £3,030,678.94 -> £2,583,154.24 (14.8%); £3,030,680.75 -> £2,583,147.15 (14.8%); £3,030,682.62 -> £2,583,139.83 (14.8%); £3,030,684.78 -> £2,583,132.95 (14.8%); £3,030,686.94 -> £2,583,125.68 (14.8%); £3,030,689.06 -> £2,583,118.62 (14.8%); £3,030,691.23 -> £2,583,111.77 (14.8%); £3,030,693.36 -> £2,583,104.83 (14.8%); £3,030,695.54 -> £2,583,097.80 (14.8%); £3,030,697.61 -> £2,583,090.63 (14.8%); £3,030,698.44 -> £2,583,083.82 (14.8%); £3,030,700.37 -> £2,583,076.47 (14.8%); £3,030,702.43 -> £2,583,068.31 (14.8%); £3,030,704.30 -> £2,583,059.62 (14.8%); £3,030,706.10 -> £2,583,050.37 (14.8%); £3,030,707.98 -> £2,583,040.19 (14.8%); £3,030,709.02 -> £2,583,028.64 (14.8%); £3,030,710.77 -> £2,583,017.25 (14.8%); £3,030,712.58 -> £2,583,005.37 (14.8%); £3,030,714.35 -> £2,582,993.70 (14.8%); £3,030,715.43 -> £2,582,981.74 (14.8%); £3,030,716.42 -> £2,582,969.80 (14.8%); £3,030,717.44 -> £2,582,957.94 (14.8%); £3,030,718.50 -> £2,582,945.87 (14.8%); £3,030,720.38 -> £2,582,933.98 (14.8%); £3,030,721.95 -> £2,582,922.09 (14.8%); £3,030,723.30 -> £2,582,910.27 (14.8%); £3,030,724.43 -> £2,582,898.52 (14.8%); £3,030,725.53 -> £2,582,886.47 (14.8%); £3,030,726.63 -> £2,582,874.68 (14.8%); £3,030,727.70 -> £2,582,862.63 (14.8%); £3,030,728.81 -> £2,582,850.76 (14.8%); £3,030,729.91 -> £2,582,838.87 (14.8%); £3,030,730.92 -> £2,582,826.84 (14.8%); £3,030,731.80 -> £2,582,814.71 (14.8%); £3,030,732.88 -> £2,582,803.08 (14.8%); £3,030,734.03 -> £2,582,791.35 (14.8%); £3,030,735.14 -> £2,582,779.68 (14.8%); £3,030,736.93 -> £2,582,767.88 (14.8%); £3,030,738.79 -> £2,582,756.15 (14.8%); £3,030,739.85 -> £2,582,744.08 (14.8%); £3,030,741.64 -> £2,582,732.31 (14.8%); £3,030,743.44 -> £2,582,720.17 (14.8%); £3,030,745.33 -> £2,582,708.51 (14.8%); £3,030,747.22 -> £2,582,697.80 (14.8%); £3,030,749.33 -> £2,582,688.02 (14.8%); £3,030,751.45 -> £2,582,678.65 (14.8%); £3,048,983.66 -> £2,583,229.34 (15.3%)
- Bills issued: 156, average clarity 0.854, average bill shock 14.5%, bad debt provision £71,967.89, avg complaint probability 4.1%
- Solvency signal: £258,323/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £220,961.07 vs. naked (unhedged) net margin: £977,626.63
- hedging cost £756,665.56 vs. a fully unhedged book (commodity-only: actual net £220,961.07 vs. naked net £977,626.63)
  - C2: actual £762.32 vs. naked £1,867.70 -- hedging cost £1,105.38
  - C2g: actual £1,144.65 vs. naked £1,444.17 -- hedging cost £299.53
  - C4: actual £157.22 vs. naked £815.41 -- hedging cost £658.20
  - C4g: actual £162.31 vs. naked £394.76 -- hedging cost £232.45
  - C6: actual £1,452.73 vs. naked £4,264.06 -- hedging cost £2,811.32
  - C7: actual £96.90 vs. naked £1,429.79 -- hedging cost £1,332.89
  - C8: actual £1,322.02 vs. naked £2,915.51 -- hedging cost £1,593.48
  - C9: actual £1,212.03 vs. naked £2,564.07 -- hedging cost £1,352.04
  - C_IC1: actual £291,883.09 vs. naked £429,508.16 -- hedging cost £137,625.07
  - C_IC2: actual £126,163.98 vs. naked £191,373.64 -- hedging cost £65,209.67
  - C_IC3: actual £42,318.89 vs. naked £310,644.61 -- hedging cost £268,325.72
  - C_IC3g: actual £-17,160.47 vs. naked £77,607.60 -- hedging cost £94,768.08
  - C_IC4: actual £-228,554.58 vs. naked £-47,202.85 -- hedging cost £181,351.73

**Year narrative:** 2023 produced a net gain of £103,535.76 across 13 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 31 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £70,187.08 (gross £990,224.03, capital £14,137.94)
  - Electricity: gross £888,213.16, capital £9,319.91, net £86,857.10
  - Gas: gross £102,010.86, capital £4,818.04, net £-16,670.03
- Treasury at year end: £2,803,856.33
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C7 0.86 (avg 0.86), C8 0.90 (avg 0.90), C9 0.87 (avg 0.87), C_IC1 0.85 (avg 0.86), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.85 (avg 0.85), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2024-12-30 period 1, net margin £-276.23

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2024): £227,500.09
  - By billing account: C1 £1,740.15, C2 £5,652.89, C3 £2,054.81, C4 £2,744.27, C5 £5,826.02, C6 £8,382.41, C7 £5,018.34, C8 £6,882.69, C9 £6,568.42, C_IC1 £1,049,105.77, C_IC2 £527,093.78, C_IC3 £1,318,340.47, C_IC4 £18,091.20
- Bill shock events (>=20%): 26 -- C7 2024-01-31 (24%); C7 2024-02-29 (27%); C7 2024-05-31 (38%); C7 2024-09-30 (37%); C7 2024-10-31 (39%); C7 2024-11-30 (51%); C2 2024-04-30 (40%); C2g 2024-04-30 (49%); C8 2024-02-29 (23%); C8 2024-04-30 (42%); C8 2024-05-31 (51%); C8 2024-07-31 (28%); C8 2024-09-30 (82%); C8 2024-10-31 (37%); C8 2024-11-30 (65%); C9 2024-05-31 (50%); C9 2024-07-31 (36%); C9 2024-09-30 (60%); C9 2024-10-31 (23%); C9 2024-11-30 (50%); C_IC1 2024-07-31 (49%); C_IC1 2024-08-31 (66%); C_IC2 2024-06-30 (55%); C_IC2 2024-07-31 (119%); C_IC3 2024-01-31 (41%); C_IC4 2024-05-31 (25%)
- Churn risk (accounts renewing in 2024): 7 at risk (≥20% churn prob): C4 26%, C6 38%, C7 41%, C8 41%, C9 38%, C_IC3 20%, C_IC4 26%

**Pricing & Margin**

- C2 (electricity): tariff £244.49-£376.94/MWh, net margin £426.03
- C2g (gas): tariff £62.35-£136.85/MWh, net margin £535.67
- C4 (electricity): tariff £235.01/MWh, net margin £109.57
- C4g (gas): tariff £54.68/MWh, net margin £136.12
- C6 (electricity): tariff £357.39/MWh, net margin £500.16
- C7 (electricity): tariff £167.10-£347.94/MWh, net margin £100.56
- C8 (electricity): tariff £191.13-£532.33/MWh, net margin £961.32
- C9 (electricity): tariff £179.11-£437.06/MWh, net margin £915.33
- C_IC1 (electricity): tariff £-98.58-£420.11/MWh, net margin £188,438.70
- C_IC2 (electricity): tariff £-106.92-£384.86/MWh, net margin £82,555.63
- C_IC3 (electricity): tariff £72.38-£145.12/MWh, net margin £42,228.07
- C_IC3g (gas): tariff £41.74-£53.75/MWh, net margin £-17,341.82 -- **net-negative**
- C_IC4 (electricity): tariff £23.97-£113.12/MWh, net margin £-229,378.26 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,048,893.28 -> £2,583,231.79 (15.3%)
- Bills issued: 141, average clarity 0.856, average bill shock 13.6%, bad debt provision £53,765.78, avg complaint probability 4.0%
- Solvency signal: £280,386/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £45,442.52 vs. naked (unhedged) net margin: £389,040.31
- hedging cost £343,597.79 vs. a fully unhedged book (commodity-only: actual net £45,442.52 vs. naked net £389,040.31)
  - C2: actual £289.29 vs. naked £1,032.78 -- hedging cost £743.49
  - C2g: actual £329.77 vs. naked £349.10 -- hedging cost £19.32
  - C7: actual £93.57 vs. naked £717.00 -- hedging cost £623.42
  - C8: actual £709.81 vs. naked £1,694.32 -- hedging cost £984.51
  - C9: actual £484.08 vs. naked £1,460.24 -- hedging cost £976.15
  - C_IC1: actual £97,289.46 vs. naked £188,337.69 -- hedging cost £91,048.23
  - C_IC2: actual £62,613.13 vs. naked £111,527.80 -- hedging cost £48,914.67
  - C_IC3: actual £-12,572.50 vs. naked £84,843.85 -- hedging cost £97,416.35
  - C_IC3g: actual £-4,308.75 vs. naked £25,544.36 -- hedging cost £29,853.11
  - C_IC4: actual £-99,485.34 vs. naked £-26,466.80 -- hedging cost £73,018.54

**Year narrative:** 2024 produced a net gain of £70,187.08 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 26 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £-28,851.03 (gross £375,305.35, capital £9,544.60)
  - Electricity: gross £327,639.89, capital £6,041.08, net £-25,195.27
  - Gas: gross £47,665.47, capital £3,503.52, net £-3,655.76
- Treasury at year end: £2,856,968.82
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
- Average CLV (Point-in-Time, year-end 2025): £250,357.08
  - By billing account: C1 £1,703.64, C2 £5,843.80, C3 £1,893.87, C4 £2,681.87, C5 £5,751.48, C6 £8,235.65, C7 £5,162.24, C8 £6,481.97, C9 £6,559.05, C_IC1 £1,119,399.12, C_IC2 £562,270.38, C_IC3 £1,510,870.45, C_IC4 £17,788.53
- Bill shock events (>=20%): 20 -- C7 2025-01-31 (35%); C7 2025-04-30 (38%); C7 2025-05-31 (24%); C7 2025-06-07 (80%); C2 2025-06-07 (78%); C2g 2025-06-07 (77%); C8 2025-01-31 (40%); C8 2025-02-28 (24%); C8 2025-04-30 (30%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (34%); C9 2025-06-07 (71%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (81%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2 20%, C8 38%, C9 38%

**Pricing & Margin**

- C2 (electricity): tariff £244.49-£273.12/MWh, net margin £112.42
- C2g (gas): tariff £62.35-£62.85/MWh, net margin £100.53
- C7 (electricity): tariff £182.26-£347.94/MWh, net margin £94.60
- C8 (electricity): tariff £191.13-£421.85/MWh, net margin £375.48
- C9 (electricity): tariff £179.11-£341.93/MWh, net margin £264.46
- C_IC1 (electricity): tariff £155.47-£296.80/MWh, net margin £53,737.14
- C_IC2 (electricity): tariff £157.76-£301.17/MWh, net margin £30,584.61
- C_IC3 (electricity): tariff £72.38-£138.18/MWh, net margin £-12,194.13 -- **net-negative**
- C_IC3g (gas): tariff £41.74/MWh, net margin £-3,756.29 -- **net-negative**
- C_IC4 (electricity): tariff £43.11-£193.69/MWh, net margin £-98,169.84 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 60, average clarity 0.803, average bill shock 22.8%, bad debt provision £23,031.37, avg complaint probability 5.6%
- Solvency signal: £357,121/customer (8 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £151.76 vs. naked (unhedged) net margin: £462.00
- hedging cost £310.24 vs. a fully unhedged book (commodity-only: actual net £151.76 vs. naked net £462.00)
  - C2: actual £39.73 vs. naked £190.43 -- hedging cost £150.70
  - C2g: actual £23.92 vs. naked £43.00 -- hedging cost £19.08
  - C8: actual £88.12 vs. naked £228.57 -- hedging cost £140.45

**Year narrative:** 2025 produced a net loss of £-28,851.03 across 10 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 20 customer(s) experienced a bill shock of >=20%.
