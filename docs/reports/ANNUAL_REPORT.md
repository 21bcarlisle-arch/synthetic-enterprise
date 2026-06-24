# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £2,889,211.80
  (£422,575.58 net change)
- Solvency signal (final year): £313,519/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £17,976,936.99
  VAT remitted to HMRC: (£864,529.79) | Revenue (ex-VAT): £17,112,407.21
  Non-commodity pass-through: (£4,015,894.80)
- Gross margin: £5,229,257.26
- Capital costs: £65,754.10
- Net margin: £5,163,503.16
- Capital cost ratio: 1.3% of gross
- Net margin as % of revenue: 30.2%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 50
- Bills issued: 1549, average clarity 0.859,
  service quality score 0.919
- Enterprise value (CLV sum across 14 billing accounts): £5,666,754.67
- Cost to serve (whole portfolio): £85,921.73, net margin after cost to serve: £5,077,581.43
- Hedge effectiveness (whole window): hedging cost £3,771,410.64 vs. a fully unhedged book (commodity-only: actual net £422,575.58 vs. naked net £4,193,986.21)

- **2021** (crisis year): net margin £50,018.12, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £237,330.90, 9 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £5,229,257.26, capital £65,754.10, net £5,163,503.16. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 1.3% (commodity basis, comparable to old model) / 1.3% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £50,018.12 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 30.2%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £5,163,503.16
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £4,193,986.21
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £3,771,410.64 vs. a fully unhedged book (commodity-only: actual net £422,575.58 vs. naked net £4,193,986.21)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £122,588.98 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £605,386.80 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £78.35 | £366.77 | £99.64 | £544.77 |
| 2017 | £34,294.45 | £0.00 | £167.76 | £548.98 | £202.39 | £35,213.57 |
| 2018 | £113,180.14 | £0.00 | £-344.34 | £327.60 | £154.27 | £113,317.67 |
| 2019 | £242,374.78 | £-36,112.79 | £215.59 | £585.38 | £171.97 | £207,234.94 |
| 2020 | £-36,342.36 | £-5,116.89 | £145.65 | £648.92 | £194.16 | £-40,470.52 |
| 2021 | £-75,859.37 | £125,577.06 | £200.24 | £384.71 | £-284.52 | £50,018.12 |
| 2022 | £195,369.17 | £43,790.89 | £925.42 | £-1,746.73 | £-1,007.85 | £237,330.90 |
| 2023 | £-100,145.09 | £-253,415.10 | £1,267.24 | £312.16 | £-1,003.54 | £-352,984.32 |
| 2024 | £155,564.73 | £-17,341.82 | £501.43 | £1,810.53 | £357.52 | £140,892.38 |
| 2025 | £34,819.92 | £-3,756.29 | £0.00 | £352.01 | £62.43 | £31,478.07 |

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
| C_IC3 | 2022-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.8723 |
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
| C4 | 2024-09-29 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.3751 |
| C2_2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 191.4%
- **Average signed error:** +52.4% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -63.4% | 63.4% |
| 2017 | 3 | -91.5% | 91.5% |
| 2018 | 4 | +466.5% | 540.5% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | -17.6% | 144.3% |
| 2021 | 9 | +4.8% | 123.7% |
| 2022 | 7 | -28.3% | 93.4% |
| 2023 | 7 | +2.6% | 136.2% |
| 2024 | 7 | +76.1% | 234.6% |
| 2025 | 2 | -94.5% | 94.5% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 33.5%, abs error 299.5%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.9%, abs error 144.3%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.6% | 0.0% | 63.4% |
| 2017 | 0 | 3 | 0.0% | 2.1% | 0.0% | 91.5% |
| 2018 | 2 | 2 | 20.4% | 50.1% | 137.8% | 943.2% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 16.6% | 0.5% | 191.0% | 97.6% |
| 2021 | 3 | 6 | 63.6% | 4.0% | 207.9% | 81.6% |
| 2022 | 0 | 7 | 0.0% | 19.5% | 0.0% | 93.4% |
| 2023 | 2 | 5 | 24.0% | 19.0% | 47.2% | 171.8% |
| 2024 | 3 | 4 | 37.4% | 0.0% | 414.1% | 100.0% |
| 2025 | 0 | 2 | 0.0% | 2.1% | 0.0% | 94.5% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 10 (26%)
- **Below/at SVT (protected):** 29 (74%)
- **Mean rate vs SVT premium:** -8.5%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -2.5% | 136.5 | 140.0 |
| 2017 | 3 | 0 (0%) | -11.2% | 124.4 | 140.0 |
| 2018 | 2 | 2 (100%) | +4.0% | 158.7 | 152.5 |
| 2019 | 2 | 0 (0%) | -26.9% | 130.4 | 178.5 |
| 2020 | 5 | 0 (0%) | -25.0% | 132.5 | 176.9 |
| 2021 | 6 | 3 (50%) | +1.2% | 184.8 | 183.8 |
| 2022 | 7 | 4 (57%) | +11.7% | 294.9 | 318.4 |
| 2023 | 5 | 0 (0%) | -32.4% | 225.6 | 364.0 |
| 2024 | 4 | 0 (0%) | -13.5% | 213.0 | 246.9 |
| 2025 | 2 | 1 (50%) | +3.7% | 257.8 | 248.6 |

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
| 2017 | 3 | 0.91× | 0.94× |
| 2018 | 4 | 5.40× ⚠ | 18.00× |
| 2019 | 4 | 5.25× ⚠ | 18.00× |
| 2020 | 10 | 1.44× | 6.33× |
| 2021 | 9 | 1.24× | 4.59× |
| 2022 | 7 | 0.93× | 2.28× |
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
| 2019 | 11 | 1.0% | 5.1% |
| 2020 | 13 | 0.7% | 3.5% |
| 2021 | 11 | 1.0% | 4.2% |
| 2022 | 9 | 1.9% | 7.5% |
| 2023 | 9 | 1.5% | 4.5% |
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
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.77 |
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
| 2022 | 259,221 | -50,329 | 71,821 | 37,160 | 69,889 | 387,761 | ⬇ CfD REBATE |
| 2023 | 274,515 | 65,414 | 72,466 | 51,388 | 75,836 | 539,619 |  |
| 2024 | 310,696 | 111,051 | 73,601 | 69,384 | 83,390 | 648,122 |  |
| 2025 | 137,777 | 47,659 | 31,649 | 31,498 | 36,697 | 285,281 |  |
| **Total** | **1,739,406** | **265,458** | **462,576** | **339,655** | **471,400** | **3,278,494** | |

Total policy cost: £3,278,494 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2022 | 134,424 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 140,147 | RIIO-ED2 from Apr 2023 |
| 2024 | 144,491 |  |
| 2025 | 62,119 |  |
| **Total** | **886,564** | |

Total network cost: £886,564 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

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
| 2019 | 135,990 | 105,132 | 30,859 | 15,273 | 50,131 | 1,395 | -35,941 | -26.4% |
| 2020 | 119,694 | 57,391 | 62,302 | 19,520 | 46,890 | 814 | -4,923 | -4.1% |
| 2021 | 296,625 | 97,288 | 199,338 | 22,523 | 50,386 | 1,136 | 125,293 | +42.2% |
| 2022 | 593,793 | 466,992 | 126,802 | 27,135 | 54,413 | 2,471 | 42,783 | +7.2% |
| 2023 | 295,491 | 436,985 | -141,493 | 32,320 | 80,214 | 392 | -254,419 | -86.1% |
| 2024 | 270,499 | 168,958 | 101,542 | 37,573 | 76,143 | 4,810 | -16,984 | -6.3% |
| 2025 | 128,880 | 81,207 | 47,673 | 16,774 | 31,087 | 3,506 | -3,694 | -2.9% |
| **Total** | **1,845,524** | **1,416,426** | **429,098** | **171,119** | **390,853** | **14,555** | **-147,428** | **-8.0%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b)

Treasury balance ÷ active billing accounts at each year-end.
Ofgem licence floor: £0/account (positive net assets required to hold a supply licence).
Capital adequacy target: £130/dual-fuel billing account.

| Year | Treasury £ | Billing Accounts | Net Assets/Account £ | vs Floor | vs £130 Target |
|------|-----------|-----------------|----------------------|----------|----------------|
| 2016 | 2,467,086 | 9 | 274,121 | OK | OK |
| 2017 | 2,501,959 | 10 | 250,196 | OK | OK |
| 2018 | 2,492,463 | 11 | 226,588 | OK | OK |
| 2019 | 2,630,045 | 12 | 219,170 | OK | OK |
| 2020 | 2,740,263 | 13 | 210,789 | OK | OK |
| 2021 | 2,741,044 | 12 | 228,420 | OK | OK |
| 2022 | 2,887,168 | 11 | 262,470 | OK | OK |
| 2023 | 2,574,791 | 10 | 257,479 | OK | OK |
| 2024 | 2,761,189 | 10 | 276,119 | OK | OK |
| 2025 | 2,821,668 | 9 | 313,519 | OK | OK |

End-state (2025): **£313,519/account** across 9 billing accounts — above Ofgem £130 target.




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,842 | 40,643 | 33.6% | £10,407.87 | £10,786.42 | £256.08/MWh | £134.50/MWh | +2.7% |
| C8 | 106,723 | 46,761 | 43.8% | £12,509.20 | £8,415.05 | £267.51/MWh | £140.34/MWh | +9.9% |
| C9 | 109,388 | 46,156 | 42.2% | £11,293.35 | £8,104.60 | £244.68/MWh | £128.17/MWh | +8.7% |

Total HH revenue: £61,516.49 vs flat equivalent £57,506.59 (+7.0% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 21 | 110% | C8 (2016-10-31) |
| 2017 | 27 | 85% | C8 (2017-11-30) |
| 2018 | 35 | 62% | C_IC1 (2018-02-28) |
| 2019 | 38 | 131% | C_IC1 (2019-03-31) |
| 2020 | 31 | 126% | C_IC2 (2020-03-31) |
| 2021 | 38 | 90% | C_IC2 (2021-04-30) |
| 2022 | 54 | 1712% | C2_2 (2022-04-30) |
| 2023 | 35 | 118% | C_IC2 (2023-06-30) |
| 2024 | 29 | 125% | C_IC2 (2024-07-31) |
| 2025 | 23 | 81% | C_IC4 (2025-06-07) |

Total: **331** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1712% | no |
| 2019-03-31 | C_IC1 | +131% | no |
| 2020-03-31 | C_IC2 | +126% | no |
| 2024-07-31 | C_IC2 | +125% | no |
| 2022-10-31 | C4g | +121% | no |
| 2023-06-30 | C_IC2 | +118% | no |
| 2016-10-31 | C8 | +110% | no |
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
| 2020 | 5 | 3% | 14% | 0 |
| 2021 | 3 | 67% | 95% | 3 ⚠ |
| 2022 | 2 | 48% | 95% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 2 | 0% | 0% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £21.5 | £124.2 (+477%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £16.6 | £35.0 (+111%) | 70% |
| 2021-03-31 | C2g | £22.4 | £35.0 (+56%) | 37% |
| 2018-10-01 | C4g | £27.0 | £34.6 (+28%) | 23% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 18 |
| Retained | 17 (94%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £420,752.71 |
| Margin saved (retained customers' terms) | £2,211,208.34 |
| Wasted offer cost (churned anyway) | £504.74 |
| **Net ROI of retention strategy** | **£1,790,455.63** |
| Acquisition cost avoided (retained customers) | £2,800.00 |
| **Full economic ROI (margin + acq savings)** | **£1,793,255.63** |

Missed opportunities (churns with no offer): **4** (£3,338.01 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 4 (£3,338.01 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24689.86 | £168649.35 | £143959.49 | £0.00 |
| 2019 | 2 | 2 | £43590.91 | £305146.61 | £261555.70 | £0.00 |
| 2020 | 3 | 3 | £27543.92 | £179470.02 | £151926.10 | £392.52 |
| 2021 | 4 | 3 | £120868.25 | £416084.13 | £295215.88 | £-142.51 |
| 2022 | 2 | 2 | £70107.79 | £274880.70 | £204772.91 | £320.54 |
| 2023 | 4 | 4 | £88837.05 | £450589.00 | £361751.95 | £0.00 |
| 2024 | 2 | 2 | £45114.93 | £416388.53 | £371273.60 | £2767.46 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24689.86 | £168649.35 | £150 | £143959.49 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £15172.01 | £105265.61 | £150 | £90093.61 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £28418.90 | £199881.00 | £150 | £171462.10 | retained |
| 2020-01-01 | C_IC3 | 0.38 | 3% | £5898.93 | £16338.11 | £150 | £10439.18 | retained |
| 2020-03-31 | C_IC1 | 0.52 | 5% | £10690.70 | £137077.97 | £150 | £126387.27 | retained |
| 2020-12-31 | C_IC3 | 0.59 | 5% | £10954.29 | £26053.94 | £150 | £15099.65 | retained |
| 2021-03-31 | C_IC2 | 0.82 | 8% | £14266.16 | £92101.54 | £150 | £77835.37 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £22616.84 | £158668.70 | £150 | £136051.85 | retained |
| 2021-12-30 | C5 | 0.77 | 8% | £504.74 | £2177.04 | £400 | £-504.74 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £83480.51 | £165313.90 | £150 | £81833.38 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £23759.02 | £75336.32 | £150 | £51577.30 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £46348.77 | £199544.39 | £150 | £153195.61 | retained |
| 2023-03-31 | C6 | 0.37 | 3% | £197.76 | £3050.23 | £400 | £2852.47 | retained |
| 2023-05-30 | C_IC2 | 0.59 | 5% | £11905.84 | £132988.80 | £150 | £121082.96 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £35420.81 | £249554.60 | £150 | £214133.79 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £41312.65 | £64995.37 | £150 | £23682.73 | retained |
| 2024-06-28 | C_IC2 | 0.55 | 5% | £10497.79 | £137873.42 | £150 | £127375.63 | retained |
| 2024-07-28 | C_IC1 | 0.95 | 8% | £34617.14 | £278515.11 | £150 | £243897.97 | retained |

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

**Full-history EV:** £5,666,754.67 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £-196,754.55 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £544.77 |
| 2017 | £35,213.57 |
| 2018 | £113,317.67 |
| 2019 | £207,234.94 |
| 2020 | £-40,470.52 |
| 2021 | £50,018.12 |
| 2022 | £237,330.90 |
| 2023 | £-352,984.32 | ← trailing
| 2024 | £140,892.38 | ← trailing
| 2025 | £31,478.07 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £2,674.28 | — |
| C2 | £5,709.76 | — |
| C2_2 | — | £1,470.89 |
| C3 | £3,020.91 | — |
| C4 | £3,369.96 | £-795.18 |
| C5 | £9,995.79 | — |
| C6 | £15,751.59 | £2,904.31 |
| C7 | £7,807.93 | £71.62 |
| C8 | £8,527.41 | £414.29 |
| C9 | £8,322.65 | £908.61 |
| C_IC1 | £1,686,627.70 | £411,763.30 |
| C_IC2 | £1,047,983.37 | £217,651.55 |
| C_IC3 | £2,830,323.60 | £-258,794.96 |
| C_IC4 | £32,343.58 | £-572,349.00 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £1,830.65 | — | — | — | — | £5,444.47 | — | £4,512.94 | — | — | — | — | — | — |
| 2017 | £2,671.23 | £7,439.29 | — | £2,924.47 | £4,245.74 | £8,188.01 | £12,289.81 | £5,259.41 | £8,622.65 | £6,565.18 | — | — | — | — |
| 2018 | £2,233.05 | £5,412.76 | — | £2,761.65 | £3,481.22 | £9,377.51 | £10,429.53 | £5,964.31 | £6,824.20 | £6,250.73 | £2,532,410.94 | — | — | — |
| 2019 | £2,610.61 | £4,765.03 | — | £2,895.91 | £3,639.24 | £7,603.06 | £11,129.46 | £5,537.85 | £6,248.12 | £5,701.64 | £1,870,014.43 | £1,113,221.55 | — | — |
| 2020 | £2,105.39 | £5,294.20 | — | £2,091.73 | £3,816.67 | £7,926.53 | £8,740.74 | £5,574.98 | £6,778.19 | £5,956.28 | £1,065,045.76 | £567,078.47 | £1,519,806.70 | £27,358.56 |
| 2021 | £1,735.19 | £4,848.31 | — | £1,820.52 | £2,889.49 | £6,414.89 | £8,745.08 | £4,935.38 | £6,405.73 | £5,075.17 | £1,010,360.41 | £565,942.03 | £1,748,223.14 | £23,130.05 |
| 2022 | £2,129.97 | £3,719.01 | £486.79 | £1,986.54 | £1,709.57 | £6,174.64 | £9,397.67 | £4,059.07 | £5,685.93 | £5,284.72 | £978,873.49 | £559,814.35 | £1,824,341.10 | £18,885.49 |
| 2023 | £2,129.64 | £3,632.51 | £1,607.52 | £1,893.98 | £1,123.82 | £6,039.15 | £9,904.26 | £3,926.06 | £5,502.17 | £5,323.69 | £1,016,072.21 | £591,961.74 | £1,361,285.04 | £18,214.36 |
| 2024 | £2,138.19 | £3,615.28 | £2,381.52 | £1,889.73 | £1,829.51 | £5,952.55 | £9,366.71 | £4,420.69 | £5,757.71 | £5,723.38 | £1,061,676.00 | £630,405.64 | £1,571,298.88 | £18,820.40 |
| 2025 | £1,780.93 | £3,725.42 | £2,703.37 | £1,906.71 | £2,068.00 | £6,768.03 | £9,532.04 | £4,573.32 | £5,317.84 | £5,244.03 | £1,058,375.73 | £648,219.31 | £1,770,039.81 | £19,917.65 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,522.20, range £32.59–£26,434.72.

- C1: cost to serve £390.39, net margin after CTS £1,437.31
- C1g: cost to serve £48.73, net margin after CTS £887.95
- C2: cost to serve £451.83, net margin after CTS £3,361.17
- C2_2: cost to serve £379.05, net margin after CTS £4,979.45
- C2g: cost to serve £61.55, net margin after CTS £1,216.99
- C3: cost to serve £262.85, net margin after CTS £1,080.53
- C3g: cost to serve £32.59, net margin after CTS £574.33
- C4: cost to serve £647.26, net margin after CTS £3,295.97
- C4g: cost to serve £167.27, net margin after CTS £454.05
- C5: cost to serve £868.50, net margin after CTS £8,165.86
- C6: cost to serve £1,267.71, net margin after CTS £16,313.45
- C7: cost to serve £943.02, net margin after CTS £9,230.92
- C8: cost to serve £923.92, net margin after CTS £10,748.51
- C9: cost to serve £879.68, net margin after CTS £10,955.88
- C_IC1: cost to serve £20,241.17, net margin after CTS £1,916,092.37
- C_IC2: cost to serve £11,525.14, net margin after CTS £924,416.75
- C_IC3: cost to serve £26,434.72, net margin after CTS £1,778,443.46
- C_IC3g: cost to serve £9,224.23, net margin after CTS £416,430.41
- C_IC4: cost to serve £11,172.13, net margin after CTS £21,351.71 — MARGIN_SQUEEZE (below 2% benchmark)

**Activity-Based Pricing Actions**

The following 1 customer(s) are profitable but below the 2% net-margin benchmark (MARGIN_SQUEEZE): C_IC4


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 32 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 13.8%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C3 | electricity | 2017-07-01 | £-28.73 | £440.29 | +1.5% | £122.23/MWh | £123.42/MWh |
| C4 | electricity | 2017-10-01 | £-41.78 | £549.78 | +2.6% | £111.62/MWh | £113.53/MWh |
| C_IC1 | electricity | 2018-01-31 | £-5,694.56 | £10,901.23 | +20.0% | £112.24/MWh | £151.30/MWh |
| C1 | electricity | 2018-12-31 | £-45.49 | £451.59 | +5.1% | £148.68/MWh | £159.64/MWh |
| C5 | electricity | 2018-12-31 | £-252.59 | £2,253.72 | +6.2% | £148.68/MWh | £160.01/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,300.82 | £6,376.41 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,218.30 | £10,243.03 | +20.0% | £128.22/MWh | £174.66/MWh |
| C6 | electricity | 2019-04-01 | £-192.03 | £2,631.38 | +2.3% | £148.35/MWh | £152.66/MWh |
| C_IC3g | gas | 2020-01-01 | £-36,112.79 | £134,045.32 | +20.0% | £16.25/MWh | £18.98/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,904.90 | £3,444.18 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,041.06 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-3,729.85 | £5,726.15 | +20.0% | £138.90/MWh | £174.40/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,006.00 | £14,511.74 | +20.0% | £113.97/MWh | £138.36/MWh |
| C4 | electricity | 2021-09-30 | £-59.07 | £681.60 | +3.7% | £205.15/MWh | £218.32/MWh |
| C4g | gas | 2021-09-30 | £-96.00 | £364.47 | +20.0% | £53.99/MWh | £67.27/MWh |
| C1 | electricity | 2021-12-30 | £-47.00 | £513.05 | +4.2% | £311.83/MWh | £328.69/MWh |
| C5 | electricity | 2021-12-30 | £-289.07 | £2,641.27 | +5.9% | £311.83/MWh | £334.32/MWh |
| C_IC2 | electricity | 2022-04-30 | £-1,292.09 | £17,661.75 | +2.3% | £269.81/MWh | £292.41/MWh |
| C_IC1 | electricity | 2022-05-30 | £-4,406.97 | £22,384.38 | +14.7% | £239.42/MWh | £287.50/MWh |
| C4 | electricity | 2022-09-30 | £-373.92 | £1,021.16 | +20.0% | £404.86/MWh | £481.67/MWh |
| C4g | gas | 2022-09-30 | £-791.90 | £770.00 | +20.0% | £183.79/MWh | £243.50/MWh |
| C7 | electricity | 2022-12-30 | £-1,633.00 | £2,294.28 | +20.0% | £266.73/MWh | £322.54/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,193.41 | £7,055.33 | +20.0% | £171.46/MWh | £233.87/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,414.36 | £17,979.18 | +20.0% | £163.19/MWh | £218.38/MWh |
| C4 | electricity | 2023-09-30 | £-556.59 | £1,701.85 | +20.0% | £216.77/MWh | £256.19/MWh |
| C4g | gas | 2023-09-30 | £-1,481.14 | £2,090.00 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-230.25 | £3,896.40 | +0.9% | £242.22/MWh | £232.20/MWh |
| C_IC3 | electricity | 2023-12-31 | £-155,785.61 | £943,359.58 | +11.5% | £118.95/MWh | £126.01/MWh |
| C_IC3g | gas | 2023-12-31 | £-252,917.30 | £294,338.38 | +20.0% | £51.89/MWh | £71.61/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,916.03 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,612.90 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |
| C_IC3g | gas | 2024-12-30 | £-17,160.47 | £268,215.17 | +1.4% | £50.47/MWh | £56.56/MWh |


## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 113 renewal(s) (27 gas) based on recent portfolio-wide margin rates: 84 surcharge(s), 29 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | -0.8% | +4.4% | £131.49/MWh | £137.26/MWh |
| C1g | gas | 2016-12-31 | 9.7% | -0.8% | £27.63/MWh | £27.40/MWh |
| C5 | electricity | 2016-12-31 | -0.6% | +4.3% | £131.49/MWh | £137.12/MWh |
| C7 | electricity | 2016-12-31 | 2.7% | +2.7% | £131.49/MWh | £134.98/MWh |
| C2 | electricity | 2017-04-01 | 10.9% | -1.5% | £127.97/MWh | £126.08/MWh |
| C2g | gas | 2017-04-01 | 10.9% | -1.4% | £34.54/MWh | £34.04/MWh |
| C6 | electricity | 2017-04-01 | 9.4% | -0.7% | £127.97/MWh | £127.05/MWh |
| C8 | electricity | 2017-04-01 | 8.5% | -0.2% | £127.97/MWh | £127.65/MWh |
| C3 | electricity | 2017-07-01 | 9.1% | -0.5% | £122.23/MWh | £121.57/MWh |
| C3g | gas | 2017-07-01 | 12.9% | -2.5% | £24.33/MWh | £23.73/MWh |
| C9 | electricity | 2017-07-01 | 7.5% | +0.3% | £122.23/MWh | £122.55/MWh |
| C4 | electricity | 2017-10-01 | 9.7% | -0.9% | £111.62/MWh | £110.65/MWh |
| C4g | gas | 2017-10-01 | 11.6% | -1.8% | £27.48/MWh | £26.99/MWh |
| C1 | electricity | 2017-12-31 | 8.2% | -0.1% | £120.10/MWh | £119.97/MWh |
| C1g | gas | 2017-12-31 | 9.3% | -0.6% | £34.79/MWh | £34.56/MWh |
| C5 | electricity | 2017-12-31 | 2.3% | +2.9% | £120.10/MWh | £123.54/MWh |
| C7 | electricity | 2017-12-31 | -2.8% | +5.4% | £120.10/MWh | £126.55/MWh |
| C_IC1 | electricity | 2018-01-31 | -16.7% | +12.3% | £112.24/MWh | £126.08/MWh |
| C2 | electricity | 2018-04-01 | -4.2% | +6.1% | £133.89/MWh | £142.07/MWh |
| C2g | gas | 2018-04-01 | 9.7% | -0.9% | £38.21/MWh | £37.88/MWh |
| C6 | electricity | 2018-04-01 | -5.3% | +6.6% | £133.89/MWh | £142.78/MWh |
| C8 | electricity | 2018-04-01 | 6.0% | +1.0% | £133.89/MWh | £135.26/MWh |
| C3 | electricity | 2018-07-01 | 7.7% | +0.2% | £128.29/MWh | £128.51/MWh |
| C3g | gas | 2018-07-01 | 7.3% | +0.3% | £29.63/MWh | £29.73/MWh |
| C9 | electricity | 2018-07-01 | -3.1% | +5.5% | £128.29/MWh | £135.40/MWh |
| C4 | electricity | 2018-10-01 | 0.3% | +3.9% | £145.00/MWh | £150.59/MWh |
| C4g | gas | 2018-10-01 | 7.8% | +0.1% | £34.60/MWh | £34.63/MWh |
| C1 | electricity | 2018-12-31 | 3.6% | +2.2% | £148.68/MWh | £151.93/MWh |
| C1g | gas | 2018-12-31 | 8.5% | -0.2% | £37.15/MWh | £37.07/MWh |
| C5 | electricity | 2018-12-31 | 5.3% | +1.3% | £148.68/MWh | £150.66/MWh |
| C7 | electricity | 2018-12-31 | 8.0% | +0.0% | £148.68/MWh | £148.72/MWh |
| C_IC2 | electricity | 2019-01-31 | -28.8% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -19.0% | +13.5% | £128.22/MWh | £145.55/MWh |
| C2 | electricity | 2019-04-01 | 4.9% | +1.6% | £148.35/MWh | £150.66/MWh |
| C2g | gas | 2019-04-01 | -1.9% | +5.0% | £32.94/MWh | £34.58/MWh |
| C6 | electricity | 2019-04-01 | 6.8% | +0.6% | £148.35/MWh | £149.23/MWh |
| C8 | electricity | 2019-04-01 | 25.9% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 17.5% | -4.8% | £127.03/MWh | £120.97/MWh |
| C3g | gas | 2019-07-01 | -0.7% | +4.4% | £23.62/MWh | £24.65/MWh |
| C9 | electricity | 2019-07-01 | 5.9% | +1.0% | £127.03/MWh | £128.34/MWh |
| C4 | electricity | 2019-10-01 | 6.4% | +0.8% | £126.72/MWh | £127.70/MWh |
| C4g | gas | 2019-10-01 | 2.5% | +2.7% | £20.41/MWh | £20.97/MWh |
| C1 | electricity | 2019-12-31 | 6.1% | +0.9% | £127.44/MWh | £128.64/MWh |
| C1g | gas | 2019-12-31 | 1.6% | +3.2% | £26.17/MWh | £27.01/MWh |
| C5 | electricity | 2019-12-31 | 3.4% | +2.3% | £127.44/MWh | £130.35/MWh |
| C7 | electricity | 2019-12-31 | 3.2% | +2.4% | £127.44/MWh | £130.49/MWh |
| C_IC3 | electricity | 2020-01-01 | 1.6% | +3.2% | £47.59/MWh | £49.11/MWh |
| C_IC3g | gas | 2020-01-01 | 13.4% | -2.7% | £16.25/MWh | £15.81/MWh |
| C_IC2 | electricity | 2020-03-01 | -97.5% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -89.7% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 11.4% | -1.7% | £22.80/MWh | £22.41/MWh |
| C6 | electricity | 2020-03-31 | -47.6% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -17.2% | +12.6% | £125.12/MWh | £140.91/MWh |
| C_IC1 | electricity | 2020-03-31 | 19.2% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 16.0% | -4.0% | £113.43/MWh | £108.88/MWh |
| C9 | electricity | 2020-06-30 | 16.0% | -4.0% | £113.43/MWh | £108.88/MWh |
| C4 | electricity | 2020-09-30 | 12.2% | -2.1% | £124.42/MWh | £121.80/MWh |
| C4g | gas | 2020-09-30 | 12.4% | -2.2% | £16.94/MWh | £16.57/MWh |
| C1 | electricity | 2020-12-30 | 8.0% | -0.0% | £133.55/MWh | £133.54/MWh |
| C1g | gas | 2020-12-30 | 2.6% | +2.7% | £28.99/MWh | £29.77/MWh |
| C5 | electricity | 2020-12-30 | 1.0% | +3.5% | £133.55/MWh | £138.22/MWh |
| C7 | electricity | 2020-12-30 | -7.4% | +7.7% | £133.55/MWh | £143.86/MWh |
| C_IC3 | electricity | 2020-12-31 | -7.4% | +7.7% | £50.65/MWh | £54.55/MWh |
| C_IC3g | gas | 2020-12-31 | -6.6% | +7.3% | £20.05/MWh | £21.51/MWh |
| C2 | electricity | 2021-03-31 | -29.5% | +15.0% | £175.90/MWh | £202.28/MWh |
| C2g | gas | 2021-03-31 | 5.2% | +1.4% | £36.20/MWh | £36.72/MWh |
| C6 | electricity | 2021-03-31 | -26.4% | +15.0% | £175.90/MWh | £202.28/MWh |
| C8 | electricity | 2021-03-31 | -21.6% | +14.8% | £175.90/MWh | £201.96/MWh |
| C_IC2 | electricity | 2021-03-31 | -1.3% | +4.6% | £138.90/MWh | £145.33/MWh |
| C_IC1 | electricity | 2021-04-30 | 5.7% | +1.2% | £113.97/MWh | £115.30/MWh |
| C9 | electricity | 2021-06-30 | 6.4% | +0.8% | £170.38/MWh | £171.74/MWh |
| C4 | electricity | 2021-09-30 | 2.7% | +2.6% | £205.15/MWh | £210.60/MWh |
| C4g | gas | 2021-09-30 | 0.3% | +3.8% | £53.99/MWh | £56.06/MWh |
| C1 | electricity | 2021-12-30 | 5.6% | +1.2% | £311.83/MWh | £315.56/MWh |
| C5 | electricity | 2021-12-30 | 5.6% | +1.2% | £311.83/MWh | £315.56/MWh |
| C7 | electricity | 2021-12-30 | 5.6% | +1.2% | £311.83/MWh | £315.56/MWh |
| C_IC3 | electricity | 2021-12-31 | -22.0% | +15.0% | £224.03/MWh | £257.61/MWh |
| C_IC3g | gas | 2021-12-31 | -18.8% | +13.4% | £109.48/MWh | £124.15/MWh |
| C2 | electricity | 2022-03-31 | -30.5% | +15.0% | £361.95/MWh | £416.24/MWh |
| C6 | electricity | 2022-03-31 | -20.1% | +14.0% | £361.95/MWh | £412.76/MWh |
| C8 | electricity | 2022-03-31 | 1.4% | +3.3% | £361.95/MWh | £373.84/MWh |
| C_IC2 | electricity | 2022-04-30 | -3.8% | +5.9% | £269.81/MWh | £285.79/MWh |
| C_IC1 | electricity | 2022-05-30 | -1.4% | +4.7% | £239.42/MWh | £250.68/MWh |
| C9 | electricity | 2022-06-30 | 7.6% | +0.2% | £255.09/MWh | £255.64/MWh |
| C4 | electricity | 2022-09-30 | 9.7% | -0.9% | £404.86/MWh | £401.39/MWh |
| C4g | gas | 2022-09-30 | -12.8% | +10.4% | £183.79/MWh | £202.91/MWh |
| C7 | electricity | 2022-12-30 | 6.5% | +0.8% | £266.73/MWh | £268.78/MWh |
| C_IC3 | electricity | 2022-12-31 | -1.2% | +4.6% | £168.36/MWh | £176.07/MWh |
| C_IC3g | gas | 2022-12-31 | -41.2% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -30.6% | +15.0% | £319.17/MWh | £367.05/MWh |
| C6 | electricity | 2023-03-31 | -15.9% | +11.9% | £319.17/MWh | £357.26/MWh |
| C8 | electricity | 2023-03-31 | -8.8% | +8.4% | £319.17/MWh | £346.05/MWh |
| C_IC2 | electricity | 2023-05-30 | -19.3% | +13.7% | £171.46/MWh | £194.89/MWh |
| C_IC1 | electricity | 2023-06-29 | -15.0% | +11.5% | £163.19/MWh | £181.98/MWh |
| C9 | electricity | 2023-06-30 | -8.3% | +8.2% | £224.44/MWh | £242.77/MWh |
| C4 | electricity | 2023-09-30 | 11.0% | -1.5% | £216.77/MWh | £213.49/MWh |
| C4g | gas | 2023-09-30 | -63.1% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 27.8% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 20.9% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -30.3% | +15.0% | £51.89/MWh | £59.68/MWh |
| C2_2 | electricity | 2024-03-30 | -13.1% | +10.5% | £207.71/MWh | £229.61/MWh |
| C6 | electricity | 2024-03-30 | -15.6% | +11.8% | £207.71/MWh | £232.19/MWh |
| C8 | electricity | 2024-03-30 | -15.6% | +11.8% | £207.71/MWh | £232.19/MWh |
| C_IC2 | electricity | 2024-06-28 | -32.4% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -26.5% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.6% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 1.3% | +3.4% | £195.97/MWh | £202.56/MWh |
| C4g | gas | 2024-09-29 | -33.7% | +15.0% | £50.11/MWh | £57.63/MWh |
| C7 | electricity | 2024-12-29 | 19.1% | -5.0% | £243.79/MWh | £231.60/MWh |
| C_IC3 | electricity | 2024-12-30 | 9.7% | -0.9% | £116.37/MWh | £115.36/MWh |
| C_IC3g | gas | 2024-12-30 | -13.1% | +10.5% | £50.47/MWh | £55.78/MWh |
| C2_2 | electricity | 2025-03-30 | -20.5% | +14.3% | £284.89/MWh | £325.55/MWh |
| C8 | electricity | 2025-03-30 | -13.9% | +10.9% | £284.89/MWh | £316.05/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **4** | Blind misses: **4** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 1 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £3,338.01 | deliberate: £0.00 | total: £3,338.01

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.11 | No | £392.52 |
| C1 | 2021-12-30 | Blind miss | 0.03 | 0.17 | No | £-142.51 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.11 | No | £320.54 |
| C6 | 2024-03-30 | Blind miss | 0.17 | 0.38 | Yes | £2,767.46 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £166,808.09 | £-146,374.94 | £20,433.16 | No |
| C2+C2g | £417.77 | £380.04 | £797.81 | Yes |
| C1+C1g | £72.55 | £218.41 | £290.97 | Yes |
| C3+C3g | £-18.33 | £48.65 | £30.32 | Yes |
| C4+C4g | £-695.70 | £-1,700.63 | £-2,396.33 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-147,428.46.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £422,575.58 across 19 billing accounts. Revenue: £13,082,613.96.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,204,609.90 | £1,936,333.54 | £18,572.36 | £928,806.26 | 29.0% |
| 2 | C_IC2 | fixed | £1,561,391.49 | £935,941.89 | £8,562.39 | £472,512.16 | 30.3% |
| 3 | C_IC3 | pass_through | £4,643,280.20 | £1,804,878.18 | £23,165.89 | £166,808.09 | 3.6% |
| 4 | C6 | fixed | £30,793.73 | £17,581.16 | £217.52 | £3,296.14 | 10.7% |
| 5 | C8 | fixed | £20,924.25 | £11,672.42 | £135.95 | £1,713.46 | 8.2% |
| 6 | C9 | fixed | £19,397.95 | £11,835.56 | £129.38 | £1,557.90 | 8.0% |
| 7 | C2_2 | fixed | £10,177.86 | £5,358.51 | £71.92 | £1,495.84 | 14.7% |
| 8 | C2 | fixed | £6,094.75 | £3,813.00 | £31.63 | £417.77 | 6.9% |
| 9 | C2g | fixed | £2,733.72 | £1,278.54 | £17.31 | £380.04 | 13.9% |
| 10 | C1g | fixed | £2,092.54 | £936.68 | £14.90 | £218.41 | 10.4% |
| 11 | C1 | fixed | £3,023.12 | £1,827.70 | £15.87 | £72.55 | 2.4% |
| 12 | C3g | fixed | £1,400.47 | £606.92 | £9.77 | £48.65 | 3.5% |
| 13 | C3 | fixed | £2,144.92 | £1,343.38 | £9.78 | £-18.33 | -0.9% |
| 14 | C5 | fixed | £14,864.61 | £9,034.36 | £80.23 | £-138.78 | -0.9% |
| 15 | C4 | fixed | £8,470.20 | £3,943.23 | £65.34 | £-695.70 | -8.2% |
| 16 | C7 | fixed | £21,194.28 | £10,173.94 | £140.55 | £-953.18 | -4.5% |
| 17 | C4g | fixed | £7,865.44 | £621.32 | £132.04 | £-1,700.63 | -21.6% |
| 18 | C_IC3g | pass_through | £1,831,432.12 | £425,654.64 | £14,381.28 | £-146,374.94 | -8.0% |
| 19 | C_IC4 | flex | £1,690,722.42 | £32,523.85 | £0.00 | £-1,004,870.14 | -59.4% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £13,082,614 | 100.0% |
| Wholesale cost | -£7,867,255 | 60.1% |
| **Gross supply margin** | **£5,215,359** | **39.9%** |
| Policy + Network costs | -£4,727,029 | 36.1% |
| Capital cost | -£65,754 | 0.5% |
| **Net supply margin** | **£422,576** | **3.2%** |

> *The ledger's `net_margin_gbp` (£5,163,503) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £11,100,004 | 42.4% | 5.1% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,831,432 | 23.2% | -8.0% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £45,658 | 58.3% | 6.9% | CMA 3-8% | ✓ |
| resi/elec | £81,249 | 54.9% | 2.6% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £14,092 | 24.4% | -7.5% | Ofgem CMA 2-4% | ⚠ ANOMALY |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: ANOMALIES DETECTED**
- Segment resi/gas net -7.5% (benchmark Ofgem CMA 2-4%)
## Transaction Log

Total events: 3,321,710

| Event type | Count |
|------------|-------|
| acquisition_gate_event | 1 |
| acquisition_spend_event | 3 |
| bad_debt_event | 1,549 |
| billing_event | 1,549 |
| capital_charge_event | 1,599,755 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,549 |
| payment_received_event | 1,549 |
| settlement_event | 1,714,092 |
| vat_remittance_event | 1,549 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £17,976,936.99 |
|   Less: VAT remitted to HMRC | (£864,529.79) |
| = Revenue (ex-VAT) | £17,112,407.21 |
| Less: non-commodity pass-through | (£4,015,894.80) |
| Wholesale cost (settlement events) | (£7,867,255.14) |
| Gross margin | £5,229,257.26 |
| Capital charges | (£65,754.10) |
| Net margin | £5,163,503.16 |

_Cash reconciliation: of £17,976,936.99 billed, bad debt of £359,495.29 was written off, leaving £17,617,441.71 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £5,668,537.66._

| Acquisition spend | (£950.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £5,156,853.16 |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £5,156,853.16

## 2016

**Trading & Risk**

- Net margin: £544.77 (gross £5,627.45, capital £75.72)
  - Electricity: gross £5,166.61, capital £70.30, net £445.13
  - Gas: gross £460.83, capital £5.42, net £99.64
- Treasury at year end: £2,467,085.65
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.22, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-01-31: treasury £2,466,641.13, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-01: treasury £2,466,646.13, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-31: treasury £2,466,650.88, (none), VaR (current £22.23 / stressed £6.83) ratio 3.25
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
- Worst single period: C9 on 2016-11-20 period 36, net margin £-0.36

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £3,929.35
  - By billing account: C1 £1,830.65, C5 £5,444.47, C7 £4,512.94
- Bill shock events (>=20%): 21 -- C5 2016-05-31 (28%); C5 2016-06-30 (21%); C5 2016-10-31 (43%); C5 2016-11-30 (45%); C7 2016-04-30 (22%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-10-31 (83%); C7 2016-11-30 (55%); C6 2016-05-31 (26%); C6 2016-06-30 (23%); C6 2016-10-31 (42%); C6 2016-11-30 (47%); C8 2016-05-31 (41%); C8 2016-06-30 (42%); C8 2016-09-30 (25%); C8 2016-10-31 (110%); C8 2016-11-30 (72%); C9 2016-09-30 (20%); C9 2016-10-31 (80%); C9 2016-11-30 (61%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.30-£137.26/MWh, net margin £49.50
- C1g (gas): tariff £24.34-£27.40/MWh, net margin £25.21
- C2 (electricity): tariff £107.62/MWh, net margin £16.27
- C2g (gas): tariff £26.92/MWh, net margin £53.62
- C3 (electricity): tariff £98.21/MWh, net margin £-9.77 -- **net-negative**
- C3g (gas): tariff £21.93/MWh, net margin £4.76
- C4 (electricity): tariff £98.43/MWh, net margin £-7.23 -- **net-negative**
- C4g (gas): tariff £24.40/MWh, net margin £16.05
- C5 (electricity): tariff £117.30-£137.12/MWh, net margin £139.03
- C6 (electricity): tariff £107.62/MWh, net margin £-60.68 -- **net-negative**
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £217.73
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £87.63
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £12.65

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.890, average bill shock 14.0%, bad debt provision £314.41, avg complaint probability 3.6%
- Solvency signal: £274,121/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,028.29 vs. naked (unhedged) net margin: £8,715.19
- hedging cost £7,686.90 vs. a fully unhedged book (commodity-only: actual net £1,028.29 vs. naked net £8,715.19)
  - C1: actual £104.03 vs. naked £539.40 -- hedging cost £435.36
  - C1g: actual £69.44 vs. naked £271.86 -- hedging cost £202.43
  - C2: actual £17.02 vs. naked £444.49 -- hedging cost £427.47
  - C2g: actual £68.92 vs. naked £203.62 -- hedging cost £134.70
  - C3: actual £-28.73 vs. naked £209.70 -- hedging cost £238.43
  - C3g: actual £6.58 vs. naked £112.13 -- hedging cost £105.55
  - C4: actual £-41.78 vs. naked £271.77 -- hedging cost £313.54
  - C4g: actual £57.89 vs. naked £209.67 -- hedging cost £151.78
  - C5: actual £301.35 vs. naked £2,536.49 -- hedging cost £2,235.13
  - C6: actual £-102.13 vs. naked £748.13 -- hedging cost £850.26
  - C7: actual £420.57 vs. naked £1,869.63 -- hedging cost £1,449.06
  - C8: actual £138.84 vs. naked £706.36 -- hedging cost £567.51
  - C9: actual £16.28 vs. naked £591.95 -- hedging cost £575.67

**Year narrative:** 2016 produced a net gain of £544.77 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 21 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £35,213.57 (gross £126,332.75, capital £1,267.14)
  - Electricity: gross £125,496.23, capital £1,256.71, net £35,011.19
  - Gas: gross £836.52, capital £10.43, net £202.39
- Treasury at year end: £2,501,958.96
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.91 (avg 0.91), C7 0.90 (avg 0.90), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,467,085.64, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-02-24: treasury £2,467,085.73, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-03-26: treasury £2,467,086.26, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-04-25: treasury £2,467,171.02, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-05-25: treasury £2,467,167.17, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-06-24: treasury £2,467,163.98, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-07-24: treasury £2,467,154.12, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-08-23: treasury £2,467,150.30, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-09-22: treasury £2,467,145.82, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-10-22: treasury £2,467,246.05, C5->1.00, C7->1.00, VaR (current £887.81 / stressed £351.43) ratio 2.53
  - 2017-11-21: treasury £2,467,250.73, C5->1.00, C7->1.00, VaR (current £887.81 / stressed £351.43) ratio 2.53
  - 2017-12-21: treasury £2,467,255.27, C5->1.00, C7->1.00, VaR (current £887.81 / stressed £351.43) ratio 2.53
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-23.95

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £6,467.31
  - By billing account: C1 £2,671.23, C2 £7,439.29, C3 £2,924.47, C4 £4,245.74, C5 £8,188.01, C6 £12,289.81, C7 £5,259.41, C8 £8,622.65, C9 £6,565.18
- Bill shock events (>=20%): 27 -- C5 2017-01-31 (29%); C5 2017-02-28 (23%); C5 2017-05-31 (20%); C5 2017-06-30 (22%); C5 2017-11-30 (58%); C7 2017-01-31 (35%); C7 2017-02-28 (29%); C7 2017-05-31 (32%); C7 2017-06-30 (33%); C7 2017-09-30 (28%); C7 2017-10-31 (23%); C7 2017-11-30 (79%); C6 2017-05-31 (22%); C6 2017-06-30 (20%); C6 2017-11-30 (51%); C8 2017-05-31 (40%); C8 2017-06-30 (37%); C8 2017-09-30 (48%); C8 2017-10-31 (23%); C8 2017-11-30 (85%); C8 2017-12-31 (22%); C9 2017-05-31 (33%); C9 2017-06-30 (27%); C9 2017-09-30 (31%); C9 2017-10-31 (22%); C9 2017-11-30 (72%); C4 2017-10-31 (23%)
- Churn risk (accounts renewing in 2017): 5 at risk (≥20% churn prob): C5 32%, C6 35%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £119.97-£137.26/MWh, net margin £54.28
- C1g (gas): tariff £27.40-£34.56/MWh, net margin £44.17
- C2 (electricity): tariff £107.62-£126.08/MWh, net margin £31.97
- C2g (gas): tariff £26.92-£34.04/MWh, net margin £115.01
- C3 (electricity): tariff £98.21-£126.42/MWh, net margin £10.12
- C3g (gas): tariff £21.93-£23.73/MWh, net margin £-2.37 -- **net-negative**
- C4 (electricity): tariff £98.43-£116.53/MWh, net margin £-35.45 -- **net-negative**
- C4g (gas): tariff £24.40-£26.99/MWh, net margin £45.57
- C5 (electricity): tariff £123.54-£137.12/MWh, net margin £161.19
- C6 (electricity): tariff £107.62-£130.05/MWh, net margin £6.57
- C7 (electricity): tariff £101.79-£202.47/MWh, net margin £201.32
- C8 (electricity): tariff £84.56-£191.48/MWh, net margin £181.56
- C9 (electricity): tariff £77.16-£183.83/MWh, net margin £105.17
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £34,294.45

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.884, average bill shock 11.5%, bad debt provision £7,485.23, avg complaint probability 3.5%
- Solvency signal: £250,196/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £34,816.69 vs. naked (unhedged) net margin: £113,837.77
- hedging cost £79,021.08 vs. a fully unhedged book (commodity-only: actual net £34,816.69 vs. naked net £113,837.77)
  - C1: actual £-45.49 vs. naked £196.55 -- hedging cost £242.04
  - C1g: actual £63.01 vs. naked £141.23 -- hedging cost £78.21
  - C2: actual £40.76 vs. naked £497.86 -- hedging cost £457.10
  - C2g: actual £129.47 vs. naked £243.61 -- hedging cost £114.15
  - C3: actual £50.25 vs. naked £298.54 -- hedging cost £248.29
  - C3g: actual £-11.24 vs. naked £62.84 -- hedging cost £74.08
  - C4: actual £-21.89 vs. naked £311.10 -- hedging cost £332.99
  - C4g: actual £10.21 vs. naked £124.64 -- hedging cost £114.43
  - C5: actual £-252.59 vs. naked £998.57 -- hedging cost £1,251.15
  - C6: actual £69.29 vs. naked £1,302.86 -- hedging cost £1,233.57
  - C7: actual £17.42 vs. naked £843.28 -- hedging cost £825.86
  - C8: actual £236.91 vs. naked £929.90 -- hedging cost £693.00
  - C9: actual £236.13 vs. naked £904.67 -- hedging cost £668.54
  - C_IC1: actual £34,294.45 vs. naked £106,982.12 -- hedging cost £72,687.68

**Year narrative:** 2017 produced a net gain of £35,213.57 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 27 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £113,317.67 (gross £274,047.15, capital £1,542.33)
  - Electricity: gross £273,268.63, capital £1,527.53, net £113,163.40
  - Gas: gross £778.53, capital £14.80, net £154.27
- Treasury at year end: £2,492,463.40
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.90 (avg 0.90), C3g 0.85 (avg 0.85), C4 0.91 (avg 0.91), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.88), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2018-03-01 period 27, net margin £-14.78

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £258,514.59
  - By billing account: C1 £2,233.05, C2 £5,412.76, C3 £2,761.65, C4 £3,481.22, C5 £9,377.51, C6 £10,429.53, C7 £5,964.31, C8 £6,824.20, C9 £6,250.73, C_IC1 £2,532,410.94
- Bill shock events (>=20%): 35 -- C5 2018-04-30 (32%); C5 2018-06-30 (21%); C5 2018-10-31 (32%); C5 2018-11-30 (28%); C7 2018-04-30 (39%); C7 2018-05-31 (29%); C7 2018-06-30 (32%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C6 2018-04-30 (25%); C6 2018-05-31 (22%); C6 2018-06-30 (22%); C6 2018-10-31 (31%); C6 2018-11-30 (22%); C8 2018-04-30 (35%); C8 2018-05-31 (38%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (57%); C8 2018-11-30 (30%); C9 2018-04-30 (32%); C9 2018-05-31 (35%); C9 2018-06-30 (35%); C9 2018-07-31 (21%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-10-31 (33%); C4g 2018-10-31 (23%); C_IC1 2018-01-31 (21%); C_IC1 2018-02-28 (62%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C4 20%, C5 38%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £119.97-£162.64/MWh, net margin £-45.13 -- **net-negative**
- C1g (gas): tariff £34.56-£37.07/MWh, net margin £62.96
- C2 (electricity): tariff £126.08-£142.07/MWh, net margin £-9.55 -- **net-negative**
- C2g (gas): tariff £34.04-£37.88/MWh, net margin £95.30
- C3 (electricity): tariff £126.42-£128.51/MWh, net margin £12.69
- C3g (gas): tariff £23.73-£29.73/MWh, net margin £-13.80 -- **net-negative**
- C4 (electricity): tariff £116.53-£153.59/MWh, net margin £-0.83 -- **net-negative**
- C4g (gas): tariff £26.99-£34.63/MWh, net margin £9.80
- C5 (electricity): tariff £123.54-£163.01/MWh, net margin £-251.03 -- **net-negative**
- C6 (electricity): tariff £130.05-£142.78/MWh, net margin £-93.31 -- **net-negative**
- C7 (electricity): tariff £101.79-£227.58/MWh, net margin £20.18
- C8 (electricity): tariff £100.30-£207.39/MWh, net margin £131.37
- C9 (electricity): tariff £96.29-£207.60/MWh, net margin £218.86
- C_IC1 (electricity): tariff £-82.12-£231.45/MWh, net margin £117,503.39
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-4,323.25 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.872, average bill shock 11.3%, bad debt provision £13,070.68, avg complaint probability 3.6%
- Solvency signal: £226,588/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £124,609.31 vs. naked (unhedged) net margin: £257,005.91
- hedging cost £132,396.61 vs. a fully unhedged book (commodity-only: actual net £124,609.31 vs. naked net £257,005.91)
  - C1: actual £58.14 vs. naked £418.89 -- hedging cost £360.74
  - C1g: actual £72.60 vs. naked £278.32 -- hedging cost £205.72
  - C2: actual £-32.41 vs. naked £561.25 -- hedging cost £593.67
  - C2g: actual £89.76 vs. naked £239.37 -- hedging cost £149.62
  - C3: actual £-25.73 vs. naked £304.79 -- hedging cost £330.51
  - C3g: actual £-6.13 vs. naked £139.96 -- hedging cost £146.10
  - C4: actual £52.03 vs. naked £559.35 -- hedging cost £507.31
  - C4g: actual £32.91 vs. naked £395.85 -- hedging cost £362.95
  - C5: actual £179.16 vs. naked £2,010.65 -- hedging cost £1,831.49
  - C6: actual £-192.03 vs. naked £1,362.85 -- hedging cost £1,554.88
  - C7: actual £118.08 vs. naked £1,344.89 -- hedging cost £1,226.81
  - C8: actual £44.60 vs. naked £917.22 -- hedging cost £872.62
  - C9: actual £188.33 vs. naked £1,050.16 -- hedging cost £861.83
  - C_IC1: actual £128,353.25 vs. naked £212,438.44 -- hedging cost £84,085.18
  - C_IC2: actual £-4,323.25 vs. naked £34,983.92 -- hedging cost £39,307.17

**Year narrative:** 2018 produced a net gain of £113,317.67 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 35 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £207,234.94 (gross £676,903.61, capital £3,493.79)
  - Electricity: gross £646,045.05, capital £2,098.33, net £243,175.76
  - Gas: gross £30,858.57, capital £1,395.46, net £-35,940.82
- Treasury at year end: £2,630,045.05
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.88 (avg 0.88), C6 0.91 (avg 0.91), C7 0.88 (avg 0.88), C8 0.92 (avg 0.92), C9 0.88 (avg 0.88), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2019-09-01 period 1, net margin £-141.19

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £275,760.63
  - By billing account: C1 £2,610.61, C2 £4,765.03, C3 £2,895.91, C4 £3,639.24, C5 £7,603.06, C6 £11,129.46, C7 £5,537.85, C8 £6,248.12, C9 £5,701.64, C_IC1 £1,870,014.43, C_IC2 £1,113,221.55
- Bill shock events (>=20%): 38 -- C1 2019-01-31 (21%); C1 2019-04-30 (22%); C5 2019-01-31 (45%); C5 2019-02-28 (22%); C5 2019-06-30 (26%); C5 2019-10-31 (44%); C5 2019-11-30 (36%); C7 2019-01-31 (42%); C7 2019-02-28 (27%); C7 2019-05-31 (24%); C7 2019-06-30 (36%); C7 2019-10-31 (73%); C7 2019-11-30 (46%); C2g 2019-04-30 (25%); C6 2019-02-28 (21%); C6 2019-06-30 (25%); C6 2019-10-31 (42%); C6 2019-11-30 (27%); C8 2019-01-31 (27%); C8 2019-02-28 (28%); C8 2019-04-30 (23%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-09-30 (61%); C8 2019-10-31 (88%); C8 2019-11-30 (38%); C3 2019-04-30 (21%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (37%); C9 2019-07-31 (35%); C9 2019-09-30 (53%); C9 2019-10-31 (76%); C9 2019-11-30 (38%); C4g 2019-10-31 (26%); C_IC1 2019-02-28 (55%); C_IC1 2019-03-31 (131%); C_IC2 2019-02-28 (72%)
- Churn risk (accounts renewing in 2019): 8 at risk (≥20% churn prob): C1 20%, C4 20%, C5 38%, C6 32%, C7 35%, C8 38%, C9 32%, C_IC1 23%

**Pricing & Margin**

- C1 (electricity): tariff £128.64-£162.64/MWh, net margin £57.93
- C1g (gas): tariff £26.00-£37.07/MWh, net margin £72.70
- C2 (electricity): tariff £142.07-£150.66/MWh, net margin £57.32
- C2g (gas): tariff £26.00-£37.88/MWh, net margin £33.47
- C3 (electricity): tariff £123.97-£128.51/MWh, net margin £-23.96 -- **net-negative**
- C3g (gas): tariff £24.65-£29.73/MWh, net margin £27.06
- C4 (electricity): tariff £127.70-£153.59/MWh, net margin £42.37
- C4g (gas): tariff £20.97-£34.63/MWh, net margin £38.74
- C5 (electricity): tariff £130.35-£163.01/MWh, net margin £177.98
- C6 (electricity): tariff £142.78-£152.66/MWh, net margin £37.61
- C7 (electricity): tariff £102.52-£227.58/MWh, net margin £117.84
- C8 (electricity): tariff £108.63-£211.40/MWh, net margin £146.04
- C9 (electricity): tariff £103.20-£207.60/MWh, net margin £187.83
- C_IC1 (electricity): tariff £0.00-£266.49/MWh, net margin £149,889.95
- C_IC2 (electricity): tariff £-60.00-£283.06/MWh, net margin £86,229.47
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £6,255.36
- C_IC3g (gas): tariff £27.53/MWh, net margin £-36,112.79 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.877, average bill shock 12.5%, bad debt provision £34,935.46, avg complaint probability 3.7%
- Solvency signal: £219,170/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £233,472.11 vs. naked (unhedged) net margin: £848,730.42
- hedging cost £615,258.31 vs. a fully unhedged book (commodity-only: actual net £233,472.11 vs. naked net £848,730.42)
  - C1: actual £2.87 vs. naked £321.70 -- hedging cost £318.83
  - C1g: actual £63.24 vs. naked £198.00 -- hedging cost £134.75
  - C2: actual £96.94 vs. naked £784.83 -- hedging cost £687.89
  - C2g: actual £13.39 vs. naked £222.05 -- hedging cost £208.65
  - C3: actual £-14.12 vs. naked £382.51 -- hedging cost £396.62
  - C3g: actual £59.45 vs. naked £217.42 -- hedging cost £157.97
  - C4: actual £32.76 vs. naked £511.27 -- hedging cost £478.51
  - C4g: actual £57.81 vs. naked £274.01 -- hedging cost £216.20
  - C5: actual £-77.65 vs. naked £1,517.63 -- hedging cost £1,595.28
  - C6: actual £171.37 vs. naked £2,036.35 -- hedging cost £1,864.98
  - C7: actual £74.78 vs. naked £1,115.55 -- hedging cost £1,040.76
  - C8: actual £210.71 vs. naked £1,294.73 -- hedging cost £1,084.02
  - C9: actual £194.16 vs. naked £1,251.59 -- hedging cost £1,057.43
  - C_IC1: actual £168,210.61 vs. naked £306,505.40 -- hedging cost £138,294.79
  - C_IC2: actual £94,233.22 vs. naked £168,914.40 -- hedging cost £74,681.18
  - C_IC3: actual £6,255.36 vs. naked £297,605.93 -- hedging cost £291,350.57
  - C_IC3g: actual £-36,112.79 vs. naked £65,577.06 -- hedging cost £101,689.86

**Year narrative:** 2019 produced a net gain of £207,234.94 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-40,470.52 (gross £624,362.38, capital £2,824.95)
  - Electricity: gross £562,060.26, capital £2,010.78, net £-35,547.80
  - Gas: gross £62,302.11, capital £814.17, net £-4,922.72
- Treasury at year end: £2,740,263.04
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.86 (avg 0.86), C7 0.88 (avg 0.88), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.85 (avg 0.85), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2020-05-01 period 1, net margin £-66.95

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2020): £248,274.94
  - By billing account: C1 £2,105.39, C2 £5,294.20, C3 £2,091.73, C4 £3,816.67, C5 £7,926.53, C6 £8,740.74, C7 £5,574.98, C8 £6,778.19, C9 £5,956.28, C_IC1 £1,065,045.76, C_IC2 £567,078.47, C_IC3 £1,519,806.70, C_IC4 £27,358.56
- Bill shock events (>=20%): 31 -- C1 2020-04-30 (21%); C5 2020-04-30 (29%); C5 2020-10-31 (39%); C5 2020-12-31 (26%); C7 2020-04-30 (35%); C7 2020-05-31 (22%); C7 2020-06-30 (28%); C7 2020-10-31 (63%); C7 2020-11-30 (24%); C7 2020-12-31 (36%); C6 2020-04-30 (30%); C6 2020-09-30 (21%); C6 2020-10-31 (34%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (26%); C8 2020-06-30 (33%); C8 2020-09-30 (57%); C8 2020-10-31 (68%); C8 2020-12-31 (44%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-09-30 (47%); C9 2020-10-31 (52%); C9 2020-12-31 (37%); C_IC1 2020-03-31 (59%); C_IC1 2020-04-30 (79%); C_IC2 2020-02-29 (67%); C_IC2 2020-03-31 (126%); C_IC4 2020-12-31 (21%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 23%, C5 35%, C6 32%, C7 38%, C8 38%, C9 41%, C_IC4 23%

**Pricing & Margin**

- C1 (electricity): tariff £128.64-£136.54/MWh, net margin £2.46
- C1g (gas): tariff £25.00-£26.00/MWh, net margin £63.13
- C2 (electricity): tariff £143.89-£150.66/MWh, net margin £139.95
- C2g (gas): tariff £22.41-£26.00/MWh, net margin £61.08
- C3 (electricity): tariff £123.97/MWh, net margin £-7.41 -- **net-negative**
- C3g (gas): tariff £24.65/MWh, net margin £33.00
- C4 (electricity): tariff £121.80-£127.70/MWh, net margin £10.72
- C4g (gas): tariff £16.57-£20.97/MWh, net margin £36.95
- C5 (electricity): tariff £130.35-£141.21/MWh, net margin £-80.30 -- **net-negative**
- C6 (electricity): tariff £143.89-£152.66/MWh, net margin £225.95
- C7 (electricity): tariff £102.52-£215.79/MWh, net margin £76.81
- C8 (electricity): tariff £110.72-£211.40/MWh, net margin £310.93
- C9 (electricity): tariff £85.55-£197.01/MWh, net margin £115.46
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £63,446.87
- C_IC2 (electricity): tariff £-79.50-£283.06/MWh, net margin £50,173.26
- C_IC3 (electricity): tariff £38.59-£81.82/MWh, net margin £20,017.72
- C_IC3g (gas): tariff £18.98-£21.51/MWh, net margin £-5,116.89 -- **net-negative**
- C_IC4 (electricity): tariff £18.53-£73.19/MWh, net margin £-169,980.21 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.877, average bill shock 11.5%, bad debt provision £35,306.35, avg complaint probability 3.6%
- Solvency signal: £210,789/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-115,919.25 vs. naked (unhedged) net margin: £578,552.21
- hedging cost £694,471.46 vs. a fully unhedged book (commodity-only: actual net £-115,919.25 vs. naked net £578,552.21)
  - C1: actual £-47.00 vs. naked £8.80 -- hedging cost £55.80
  - C1g: actual £-49.88 vs. naked £-221.49 -- hedging added £171.61
  - C2: actual £146.25 vs. naked £686.15 -- hedging cost £539.90
  - C2g: actual £70.39 vs. naked £164.55 -- hedging cost £94.16
  - C4: actual £-59.07 vs. naked £242.11 -- hedging cost £301.17
  - C4g: actual £-96.00 vs. naked £-196.27 -- hedging added £100.27
  - C5: actual £-289.07 vs. naked £115.13 -- hedging cost £404.19
  - C6: actual £223.27 vs. naked £1,619.88 -- hedging cost £1,396.60
  - C7: actual £-14.34 vs. naked £258.72 -- hedging cost £273.06
  - C8: actual £350.17 vs. naked £1,090.50 -- hedging cost £740.33
  - C9: actual £-15.14 vs. naked £604.60 -- hedging cost £619.74
  - C_IC1: actual £47,150.54 vs. naked £136,611.90 -- hedging cost £89,461.36
  - C_IC2: actual £50,039.87 vs. naked £100,888.39 -- hedging cost £50,848.52
  - C_IC3: actual £-794.35 vs. naked £206,765.24 -- hedging cost £207,559.58
  - C_IC3g: actual £120,545.96 vs. naked £146,590.86 -- hedging cost £26,044.90
  - C_IC4: actual £-333,080.86 vs. naked £-16,676.84 -- hedging cost £316,404.02

**Year narrative:** 2020 produced a net loss of £-40,470.52 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 31 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £50,018.12 (gross £704,004.88, capital £6,810.47)
  - Electricity: gross £504,667.16, capital £5,674.19, net £-75,274.42
  - Gas: gross £199,337.73, capital £1,136.28, net £125,292.54
- Treasury at year end: £2,741,044.04
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.91 (avg 0.91), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.95 (avg 0.95), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2021-12-31 period 1, net margin £-85.79

**Customer Book**

- Active accounts: 16 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £260,809.64
  - By billing account: C1 £1,735.19, C2 £4,848.31, C3 £1,820.52, C4 £2,889.49, C5 £6,414.89, C6 £8,745.08, C7 £4,935.38, C8 £6,405.73, C9 £5,075.17, C_IC1 £1,010,360.41, C_IC2 £565,942.03, C_IC3 £1,748,223.14, C_IC4 £23,130.05
- Bill shock events (>=20%): 38 -- C1 2021-04-30 (20%); C5 2021-05-31 (23%); C5 2021-06-30 (32%); C5 2021-10-31 (30%); C5 2021-11-30 (51%); C7 2021-05-31 (31%); C7 2021-06-30 (48%); C7 2021-10-31 (56%); C7 2021-11-30 (67%); C2g 2021-04-30 (27%); C6 2021-06-30 (36%); C6 2021-10-31 (28%); C6 2021-11-30 (51%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (26%); C8 2021-10-31 (69%); C8 2021-11-30 (85%); C9 2021-02-28 (21%); C9 2021-05-31 (25%); C9 2021-06-30 (51%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-10-31 (63%); C9 2021-11-30 (50%); C9 2021-12-31 (24%); C4 2021-10-31 (45%); C4g 2021-10-31 (62%); C_IC1 2021-05-31 (44%); C_IC2 2021-03-31 (28%); C_IC2 2021-04-30 (90%); C_IC3g 2021-09-30 (23%); C_IC3g 2021-10-31 (28%); C_IC3g 2021-12-31 (31%); C_IC4 2021-02-28 (28%); C_IC4 2021-07-31 (22%); C_IC4 2021-09-30 (40%); C_IC4 2021-12-31 (29%)
- Churn risk (accounts renewing in 2021): 8 at risk (≥20% churn prob): C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC4 32%

**Pricing & Margin**

- C1 (electricity): tariff £136.54/MWh, net margin £-46.49 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £-49.77 -- **net-negative**
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £163.13
- C2g (gas): tariff £22.41-£35.00/MWh, net margin £34.56
- C4 (electricity): tariff £121.80-£183.00/MWh, net margin £-144.42 -- **net-negative**
- C4g (gas): tariff £16.57-£35.00/MWh, net margin £-269.31 -- **net-negative**
- C5 (electricity): tariff £141.21/MWh, net margin £-285.66 -- **net-negative**
- C6 (electricity): tariff £143.89-£202.28/MWh, net margin £485.90
- C7 (electricity): tariff £113.03-£274.50/MWh, net margin £-24.74 -- **net-negative**
- C8 (electricity): tariff £110.72-£274.50/MWh, net margin £411.84
- C9 (electricity): tariff £85.55-£262.11/MWh, net margin £25.40
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £43,000.18
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £65,560.67
- C_IC3 (electricity): tariff £42.86-£390.91/MWh, net margin £-20,860.95 -- **net-negative**
- C_IC3g (gas): tariff £21.51-£124.15/MWh, net margin £125,577.06
- C_IC4 (electricity): tariff £42.47-£336.77/MWh, net margin £-163,559.27 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.869, average bill shock 13.0%, bad debt provision £45,714.35, avg complaint probability 3.9%
- Solvency signal: £228,420/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £142,372.21 vs. naked (unhedged) net margin: £134,468.01
- hedging added £7,904.20 vs. a fully unhedged book (commodity-only: actual net £142,372.21 vs. naked net £134,468.01)
  - C2: actual £149.20 vs. naked £137.50 -- hedging added £11.70
  - C2g: actual £8.11 vs. naked £-387.95 -- hedging added £396.07
  - C4: actual £-373.92 vs. naked £-303.64 -- hedging cost £70.28
  - C4g: actual £-791.90 vs. naked £-1,586.23 -- hedging added £794.33
  - C6: actual £542.39 vs. naked £164.92 -- hedging added £377.47
  - C7: actual £-1,633.00 vs. naked £-1,041.64 -- hedging cost £591.36
  - C8: actual £403.74 vs. naked £-10.37 -- hedging added £414.11
  - C9: actual £54.98 vs. naked £-337.01 -- hedging added £391.99
  - C_IC1: actual £48,312.62 vs. naked £-64,883.88 -- hedging added £113,196.50
  - C_IC2: actual £76,357.72 vs. naked £22,480.95 -- hedging added £53,876.77
  - C_IC3: actual £124,357.72 vs. naked £201,734.72 -- hedging cost £77,377.00
  - C_IC3g: actual £43,578.41 vs. naked £38,284.45 -- hedging added £5,293.96
  - C_IC4: actual £-148,593.86 vs. naked £-59,783.81 -- hedging cost £88,810.05

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £50,018.12 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £237,330.90 (gross £856,645.58, capital £15,582.05)
  - Electricity: gross £729,843.65, capital £13,110.88, net £194,547.86
  - Gas: gross £126,801.93, capital £2,471.17, net £42,783.04
- Treasury at year end: £2,887,167.80
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.98), C_IC3 0.96 (avg 0.96), C_IC3g 1.00 (avg 1.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £2,870,155.06, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,891.31 / stressed £20,731.51) ratio 2.70
  - 2022-05-29: treasury £2,870,475.66, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,999.73 / stressed £20,760.16) ratio 2.70
  - 2022-06-28: treasury £2,870,471.94, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,999.73 / stressed £20,760.16) ratio 2.70
  - 2022-07-28: treasury £2,870,163.01, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,082.90 / stressed £20,776.78) ratio 2.70
  - 2022-08-27: treasury £2,870,133.57, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,082.90 / stressed £20,776.78) ratio 2.70
  - 2022-09-26: treasury £2,870,102.31, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,082.90 / stressed £20,776.78) ratio 2.70
  - 2022-10-26: treasury £2,868,058.48, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,142.44 / stressed £20,785.98) ratio 2.70
  - 2022-11-25: treasury £2,867,925.39, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,142.44 / stressed £20,785.98) ratio 2.70
  - 2022-12-25: treasury £2,867,699.40, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,142.44 / stressed £20,785.98) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC3g on 2022-10-01 period 1, net margin £-463.03

**Customer Book**

- Active accounts: 14 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £244,467.74
  - By billing account: C1 £2,129.97, C2 £3,719.01, C2_2 £486.79, C3 £1,986.54, C4 £1,709.57, C5 £6,174.64, C6 £9,397.67, C7 £4,059.07, C8 £5,685.93, C9 £5,284.72, C_IC1 £978,873.49, C_IC2 £559,814.35, C_IC3 £1,824,341.10, C_IC4 £18,885.49
- Bill shock events (>=20%): 54 -- C7 2022-01-31 (42%); C7 2022-02-28 (27%); C7 2022-04-30 (23%); C7 2022-05-31 (36%); C7 2022-06-30 (27%); C7 2022-09-30 (34%); C7 2022-11-30 (64%); C7 2022-12-31 (56%); C6 2022-04-30 (45%); C6 2022-05-31 (24%); C6 2022-09-30 (26%); C6 2022-11-30 (44%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (85%); C8 2022-11-30 (73%); C8 2022-12-31 (57%); C9 2022-04-30 (21%); C9 2022-05-31 (30%); C9 2022-06-30 (31%); C9 2022-09-30 (50%); C9 2022-10-31 (31%); C9 2022-11-30 (46%); C9 2022-12-31 (53%); C4 2022-10-31 (62%); C4g 2022-10-31 (121%); C_IC1 2022-06-30 (78%); C_IC2 2022-05-31 (53%); C_IC3 2022-01-31 (106%); C_IC3g 2022-03-31 (55%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (46%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-09-30 (21%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (21%); C_IC3g 2022-12-31 (21%); C_IC4 2022-02-28 (21%); C_IC4 2022-03-31 (44%); C_IC4 2022-05-31 (21%); C_IC4 2022-07-31 (38%); C_IC4 2022-08-31 (41%); C_IC4 2022-10-31 (39%); C_IC4 2022-12-31 (102%); C2_2 2022-04-30 (1712%); C2_2 2022-05-31 (39%); C2_2 2022-06-30 (33%); C2_2 2022-07-31 (20%); C2_2 2022-09-30 (78%); C2_2 2022-11-30 (65%); C2_2 2022-12-31 (58%)
- Churn risk (accounts renewing in 2022): 8 at risk (≥20% churn prob): C4 20%, C6 32%, C7 35%, C8 38%, C9 38%, C_IC1 20%, C_IC3 29%, C_IC4 38%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £18.68
- C2_2 (electricity): tariff £361.95/MWh, net margin £152.22
- C2g (gas): tariff £35.00/MWh, net margin £-13.00 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-418.08 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-994.85 -- **net-negative**
- C6 (electricity): tariff £202.28-£412.76/MWh, net margin £925.42
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,627.75 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £65.64
- C9 (electricity): tariff £137.29-£383.46/MWh, net margin £62.54
- C_IC1 (electricity): tariff £-83.39-£435.76/MWh, net margin £144,537.68
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £76,053.69
- C_IC3 (electricity): tariff £138.34-£390.91/MWh, net margin £123,284.38
- C_IC3g (gas): tariff £116.42-£124.15/MWh, net margin £43,790.89
- C_IC4 (electricity): tariff £71.50-£469.98/MWh, net margin £-148,506.58 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.8% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,180,348.77 -> £2,768,990.84 (12.9%)
- Bills issued: 148, average clarity 0.811, average bill shock 32.3%, bad debt provision £80,688.69, avg complaint probability 5.3%
- Solvency signal: £262,470/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-312,808.90 vs. naked (unhedged) net margin: £836,857.42
- hedging cost £1,149,666.32 vs. a fully unhedged book (commodity-only: actual net £-312,808.90 vs. naked net £836,857.42)
  - C2_2: actual £183.17 vs. naked £1,470.79 -- hedging cost £1,287.62
  - C4: actual £-556.59 vs. naked £811.29 -- hedging cost £1,367.88
  - C4g: actual £-1,481.14 vs. naked £778.72 -- hedging cost £2,259.86
  - C6: actual £1,130.47 vs. naked £3,094.84 -- hedging cost £1,964.37
  - C7: actual £-230.25 vs. naked £2,154.89 -- hedging cost £2,385.14
  - C8: actual £-121.73 vs. naked £962.48 -- hedging cost £1,084.20
  - C9: actual £41.12 vs. naked £802.51 -- hedging cost £761.39
  - C_IC1: actual £209,957.42 vs. naked £223,866.33 -- hedging cost £13,908.91
  - C_IC2: actual £82,127.04 vs. naked £108,502.91 -- hedging cost £26,375.87
  - C_IC3: actual £-155,785.61 vs. naked £449,601.20 -- hedging cost £605,386.80
  - C_IC3g: actual £-252,917.30 vs. naked £83,300.79 -- hedging cost £336,218.09
  - C_IC4: actual £-195,155.50 vs. naked £-38,489.32 -- hedging cost £156,666.18

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £237,330.90 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 54 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £-352,984.32 (gross £449,477.52, capital £10,161.51)
  - Electricity: gross £590,970.66, capital £9,769.94, net £-98,565.68
  - Gas: gross £-141,493.14, capital £391.57, net £-254,418.64
- Treasury at year end: £2,574,791.03
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C6 0.93 (avg 0.93), C7 0.93 (avg 0.93), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.90 (avg 0.90), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £2,887,176.54, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,354.04 / stressed £44,330.99) ratio 2.76
  - 2023-02-23: treasury £2,887,186.40, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,354.04 / stressed £44,330.99) ratio 2.76
  - 2023-03-25: treasury £2,887,196.72, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,354.04 / stressed £44,330.99) ratio 2.76
  - 2023-04-24: treasury £2,964,492.58, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,310.38 / stressed £48,785.04) ratio 2.63
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-07-01 period 1, net margin £-813.88

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £216,329.73
  - By billing account: C1 £2,129.64, C2 £3,632.51, C2_2 £1,607.52, C3 £1,893.98, C4 £1,123.82, C5 £6,039.15, C6 £9,904.26, C7 £3,926.06, C8 £5,502.17, C9 £5,323.69, C_IC1 £1,016,072.21, C_IC2 £591,961.74, C_IC3 £1,361,285.04, C_IC4 £18,214.36
- Bill shock events (>=20%): 35 -- C7 2023-01-31 (41%); C7 2023-05-31 (32%); C7 2023-06-30 (38%); C7 2023-10-31 (58%); C7 2023-11-30 (74%); C6 2023-04-30 (29%); C6 2023-05-31 (24%); C6 2023-06-30 (23%); C6 2023-10-31 (39%); C6 2023-11-30 (44%); C8 2023-04-30 (31%); C8 2023-05-31 (41%); C8 2023-06-30 (44%); C8 2023-10-31 (101%); C8 2023-11-30 (70%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (23%); C9 2023-10-31 (77%); C9 2023-11-30 (55%); C4g 2023-10-31 (23%); C_IC1 2023-06-30 (54%); C_IC1 2023-07-31 (71%); C_IC2 2023-05-31 (54%); C_IC2 2023-06-30 (118%); C_IC3g 2023-01-31 (34%); C_IC4 2023-01-31 (46%); C2_2 2023-04-30 (21%); C2_2 2023-05-31 (42%); C2_2 2023-06-30 (42%); C2_2 2023-10-31 (97%); C2_2 2023-11-30 (67%)
- Churn risk (accounts renewing in 2023): 6 at risk (≥20% churn prob): C2_2 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC4 32%

**Pricing & Margin**

- C2_2 (electricity): tariff £361.95-£367.05/MWh, net margin £615.30
- C4 (electricity): tariff £259.19-£305.00/MWh, net margin £-328.05 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,003.54 -- **net-negative**
- C6 (electricity): tariff £357.26-£412.76/MWh, net margin £1,267.24
- C7 (electricity): tariff £182.44-£457.50/MWh, net margin £-231.36 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £35.32
- C9 (electricity): tariff £190.75-£383.46/MWh, net margin £220.96
- C_IC1 (electricity): tariff £-60.00-£444.00/MWh, net margin £163,210.61
- C_IC2 (electricity): tariff £-186.24-£443.11/MWh, net margin £86,628.75
- C_IC3 (electricity): tariff £101.37-£264.10/MWh, net margin £-154,708.47 -- **net-negative**
- C_IC3g (gas): tariff £71.61-£116.42/MWh, net margin £-253,415.10 -- **net-negative**
- C_IC4 (electricity): tariff £36.40-£169.32/MWh, net margin £-195,275.98 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.3% of gross
- Treasury drawdown events (>=10% threshold): 55 -- £3,180,345.10 -> £2,767,326.73 (13.0%); £3,180,345.20 -> £2,767,314.28 (13.0%); £3,180,345.23 -> £2,767,301.95 (13.0%); £3,180,345.26 -> £2,767,139.16 (13.0%); £3,180,345.40 -> £2,767,126.32 (13.0%); £3,180,345.56 -> £2,767,113.66 (13.0%); £3,180,345.72 -> £2,767,100.85 (13.0%); £3,180,345.89 -> £2,767,088.50 (13.0%); £3,180,346.05 -> £2,767,075.95 (13.0%); £3,180,346.22 -> £2,766,821.16 (13.0%); £3,180,346.28 -> £2,766,808.14 (13.0%); £3,180,346.49 -> £2,766,795.43 (13.0%); £3,180,346.52 -> £2,766,782.62 (13.0%); £3,180,346.55 -> £2,766,620.05 (13.0%); £3,180,346.73 -> £2,766,607.42 (13.0%); £3,180,346.91 -> £2,766,594.84 (13.0%); £3,180,347.10 -> £2,766,582.43 (13.0%); £3,180,347.28 -> £2,766,570.02 (13.0%); £3,180,347.47 -> £2,766,557.83 (13.0%); £3,180,347.64 -> £2,766,302.49 (13.0%); £3,180,347.65 -> £2,766,289.61 (13.0%); £3,180,347.88 -> £2,766,276.50 (13.0%); £3,180,347.91 -> £2,766,264.17 (13.0%); £3,180,347.95 -> £2,766,100.19 (13.0%); £3,180,348.12 -> £2,766,087.76 (13.0%); £3,180,348.32 -> £2,766,074.98 (13.0%); £3,180,348.52 -> £2,766,062.32 (13.0%); £3,180,348.72 -> £2,766,049.78 (13.0%); £3,180,348.90 -> £2,766,037.51 (13.0%); £3,180,349.09 -> £2,762,571.09 (13.1%); £3,180,349.24 -> £2,762,558.73 (13.1%); £3,180,349.44 -> £2,762,546.06 (13.1%); £3,180,349.64 -> £2,762,533.71 (13.1%); £3,180,349.83 -> £2,759,822.30 (13.2%); £3,180,349.93 -> £2,759,810.23 (13.2%); £3,180,349.96 -> £2,759,797.78 (13.2%); £3,180,349.98 -> £2,759,648.46 (13.2%); £3,180,350.05 -> £2,759,636.00 (13.2%); £3,180,350.32 -> £2,759,623.88 (13.2%); £3,180,350.58 -> £2,759,610.86 (13.2%); £3,180,350.88 -> £2,759,598.72 (13.2%); £3,180,351.17 -> £2,759,586.19 (13.2%); £3,180,351.47 -> £2,759,573.75 (13.2%); £3,180,351.76 -> £2,759,320.63 (13.2%); £3,180,351.92 -> £2,759,307.86 (13.2%); £3,180,352.30 -> £2,759,295.43 (13.2%); £3,180,352.33 -> £2,759,282.81 (13.2%); £3,180,352.36 -> £2,759,133.71 (13.2%); £3,180,352.45 -> £2,759,121.24 (13.2%); £3,180,352.73 -> £2,759,108.60 (13.2%); £3,180,353.02 -> £2,759,096.39 (13.2%); £3,180,353.31 -> £2,759,083.82 (13.2%); £3,180,353.62 -> £2,759,071.45 (13.2%); £3,180,353.93 -> £2,759,058.96 (13.2%); £3,180,354.23 -> £2,564,214.59 (19.4%)
- Bills issued: 144, average clarity 0.827, average bill shock 16.4%, bad debt provision £62,417.53, avg complaint probability 4.6%
- Solvency signal: £257,479/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £186,828.75 vs. naked (unhedged) net margin: £944,102.68
- hedging cost £757,273.93 vs. a fully unhedged book (commodity-only: actual net £186,828.75 vs. naked net £944,102.68)
  - C2_2: actual £963.24 vs. naked £2,390.03 -- hedging cost £1,426.80
  - C4: actual £292.30 vs. naked £950.92 -- hedging cost £658.62
  - C4g: actual £411.42 vs. naked £643.87 -- hedging cost £232.45
  - C6: actual £1,453.51 vs. naked £4,261.71 -- hedging cost £2,808.20
  - C7: actual £339.28 vs. naked £1,670.91 -- hedging cost £1,331.63
  - C8: actual £217.90 vs. naked £1,813.97 -- hedging cost £1,596.07
  - C9: actual £572.06 vs. naked £1,926.73 -- hedging cost £1,354.67
  - C_IC1: actual £159,153.51 vs. naked £297,043.38 -- hedging cost £137,889.87
  - C_IC2: actual £103,364.96 vs. naked £168,660.14 -- hedging cost £65,295.18
  - C_IC3: actual £165,775.62 vs. naked £434,336.27 -- hedging cost £268,560.65
  - C_IC3g: actual £-17,160.47 vs. naked £77,607.60 -- hedging cost £94,768.08
  - C_IC4: actual £-228,554.58 vs. naked £-47,202.85 -- hedging cost £181,351.73

**Year narrative:** 2023 produced a net loss of £-352,984.32 across 12 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 35 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £140,892.38 (gross £1,061,896.08, capital £14,674.19)
  - Electricity: gross £960,354.43, capital £9,864.37, net £157,876.69
  - Gas: gross £101,541.66, capital £4,809.82, net £-16,984.30
- Treasury at year end: £2,761,189.07
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.90 (avg 0.90), C4 0.86 (avg 0.86), C4g 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.85 (avg 0.85), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 12
  - 2024-01-19: treasury £2,574,887.91, C2->1.00, VaR (current £88,463.06 / stressed £50,518.14) ratio 1.75
  - 2024-02-18: treasury £2,575,006.46, C2->1.00, VaR (current £88,463.06 / stressed £50,518.14) ratio 1.75
  - 2024-03-19: treasury £2,575,129.47, C2->1.00, VaR (current £88,463.06 / stressed £50,518.14) ratio 1.75
  - 2024-04-18: treasury £2,661,023.02, C2->1.00, VaR (current £80,779.97 / stressed £61,808.17) ratio 1.31
  - 2024-05-18: treasury £2,669,215.02, C2->1.00, VaR (current £80,779.97 / stressed £61,808.17) ratio 1.31
  - 2024-06-17: treasury £2,834,113.36, C2->1.00, VaR (current £70,845.37 / stressed £85,509.04) ratio 0.83
  - 2024-07-17: treasury £2,840,176.73, C2->1.00, VaR (current £70,786.68 / stressed £85,732.81) ratio 0.83
  - 2024-08-16: treasury £2,840,194.66, C2->1.00, VaR (current £70,786.68 / stressed £85,732.81) ratio 0.83
  - 2024-09-15: treasury £2,840,214.44, C2->1.00, VaR (current £70,786.68 / stressed £85,732.81) ratio 0.83
  - 2024-10-15: treasury £2,840,874.63, C2->1.00, VaR (current £70,653.27 / stressed £85,774.89) ratio 0.82
  - 2024-11-14: treasury £2,840,899.67, C2->1.00, VaR (current £70,653.27 / stressed £85,774.89) ratio 0.82
  - 2024-12-14: treasury £2,840,956.16, C2->1.00, VaR (current £70,653.27 / stressed £85,774.89) ratio 0.82
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 1.14
- Worst single period: C_IC3g on 2024-12-30 period 1, net margin £-276.23

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £237,519.73
  - By billing account: C1 £2,138.19, C2 £3,615.28, C2_2 £2,381.52, C3 £1,889.73, C4 £1,829.51, C5 £5,952.55, C6 £9,366.71, C7 £4,420.69, C8 £5,757.71, C9 £5,723.38, C_IC1 £1,061,676.00, C_IC2 £630,405.64, C_IC3 £1,571,298.88, C_IC4 £18,820.40
- Bill shock events (>=20%): 29 -- C7 2024-02-29 (27%); C7 2024-05-31 (39%); C7 2024-09-30 (37%); C7 2024-10-31 (39%); C7 2024-11-30 (51%); C8 2024-02-29 (23%); C8 2024-04-30 (34%); C8 2024-05-31 (50%); C8 2024-07-31 (28%); C8 2024-09-30 (81%); C8 2024-10-31 (37%); C8 2024-11-30 (65%); C9 2024-05-31 (50%); C9 2024-07-31 (31%); C9 2024-09-30 (60%); C9 2024-10-31 (23%); C9 2024-11-30 (49%); C_IC1 2024-07-31 (37%); C_IC1 2024-08-31 (76%); C_IC2 2024-06-30 (52%); C_IC2 2024-07-31 (125%); C_IC4 2024-05-31 (25%); C2_2 2024-02-29 (23%); C2_2 2024-04-30 (46%); C2_2 2024-05-31 (50%); C2_2 2024-07-31 (27%); C2_2 2024-09-30 (72%); C2_2 2024-10-31 (36%); C2_2 2024-11-30 (60%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C6 38%, C7 35%, C8 41%, C9 38%, C_IC4 26%

**Pricing & Margin**

- C2_2 (electricity): tariff £229.61-£367.05/MWh, net margin £532.53
- C4 (electricity): tariff £202.56-£259.19/MWh, net margin £198.66
- C4g (gas): tariff £55.00-£66.00/MWh, net margin £357.52
- C6 (electricity): tariff £357.26/MWh, net margin £501.43
- C7 (electricity): tariff £165.00-£348.30/MWh, net margin £339.16
- C8 (electricity): tariff £165.00-£397.50/MWh, net margin £280.43
- C9 (electricity): tariff £165.00-£364.15/MWh, net margin £459.75
- C_IC1 (electricity): tariff £-98.58-£332.07/MWh, net margin £141,016.70
- C_IC2 (electricity): tariff £-106.92-£355.31/MWh, net margin £77,938.37
- C_IC3 (electricity): tariff £90.64-£193.52/MWh, net margin £165,987.92
- C_IC3g (gas): tariff £56.56-£71.61/MWh, net margin £-17,341.82 -- **net-negative**
- C_IC4 (electricity): tariff £23.97-£113.12/MWh, net margin £-229,378.26 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,006,288.98 -> £2,574,791.05 (14.4%)
- Bills issued: 135, average clarity 0.832, average bill shock 15.4%, bad debt provision £55,254.23, avg complaint probability 4.4%
- Solvency signal: £276,119/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £128,127.46 vs. naked (unhedged) net margin: £471,404.18
- hedging cost £343,276.71 vs. a fully unhedged book (commodity-only: actual net £128,127.46 vs. naked net £471,404.18)
  - C2_2: actual £243.18 vs. naked £1,126.77 -- hedging cost £883.59
  - C4: actual £-19.55 vs. naked £384.52 -- hedging cost £404.06
  - C4g: actual £98.19 vs. naked £151.09 -- hedging cost £52.90
  - C7: actual £-45.74 vs. naked £567.90 -- hedging cost £613.63
  - C8: actual £289.66 vs. naked £1,269.97 -- hedging cost £980.31
  - C9: actual £269.98 vs. naked £1,235.23 -- hedging cost £965.25
  - C_IC1: actual £133,373.86 vs. naked £223,697.17 -- hedging cost £90,323.30
  - C_IC2: actual £70,712.61 vs. naked £119,464.13 -- hedging cost £48,751.52
  - C_IC3: actual £26,999.36 vs. naked £124,429.84 -- hedging cost £97,430.48
  - C_IC3g: actual £-4,308.75 vs. naked £25,544.36 -- hedging cost £29,853.11
  - C_IC4: actual £-99,485.34 vs. naked £-26,466.80 -- hedging cost £73,018.54

**Year narrative:** 2024 produced a net gain of £140,892.38 across 12 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 29 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £31,478.07 (gross £436,061.42, capital £9,321.96)
  - Electricity: gross £388,388.06, capital £5,815.77, net £35,171.93
  - Gas: gross £47,673.36, capital £3,506.19, net £-3,693.86
- Treasury at year end: £2,821,667.97
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2025-06-01 period 1, net margin £-113.52

**Customer Book**

- Active accounts: 11 (C2_2, C4, C4g, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 0, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £252,869.44
  - By billing account: C1 £1,780.93, C2 £3,725.42, C2_2 £2,703.37, C3 £1,906.71, C4 £2,068.00, C5 £6,768.03, C6 £9,532.04, C7 £4,573.32, C8 £5,317.84, C9 £5,244.03, C_IC1 £1,058,375.73, C_IC2 £648,219.31, C_IC3 £1,770,039.81, C_IC4 £19,917.65
- Bill shock events (>=20%): 23 -- C7 2025-04-30 (38%); C7 2025-05-31 (24%); C7 2025-06-07 (80%); C8 2025-01-31 (40%); C8 2025-02-28 (24%); C8 2025-04-30 (42%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (34%); C9 2025-06-07 (71%); C4 2025-06-07 (78%); C4g 2025-06-07 (77%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (81%); C2_2 2025-01-31 (39%); C2_2 2025-02-28 (24%); C2_2 2025-05-31 (37%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £229.61-£325.55/MWh, net margin £195.79
- C4 (electricity): tariff £202.56/MWh, net margin £-13.39 -- **net-negative**
- C4g (gas): tariff £55.00/MWh, net margin £62.43
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-42.37 -- **net-negative**
- C8 (electricity): tariff £149.29-£315.00/MWh, net margin £62.69
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £149.28
- C_IC1 (electricity): tariff £169.74-£324.06/MWh, net margin £71,906.43
- C_IC2 (electricity): tariff £163.52-£312.18/MWh, net margin £34,251.21
- C_IC3 (electricity): tariff £90.64-£173.03/MWh, net margin £26,832.13
- C_IC3g (gas): tariff £56.56/MWh, net margin £-3,756.29 -- **net-negative**
- C_IC4 (electricity): tariff £43.11-£193.69/MWh, net margin £-98,169.84 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 66, average clarity 0.794, average bill shock 23.9%, bad debt provision £24,308.35, avg complaint probability 5.8%
- Solvency signal: £313,519/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £48.90 vs. naked (unhedged) net margin: £312.42
- hedging cost £263.52 vs. a fully unhedged book (commodity-only: actual net £48.90 vs. naked net £312.42)
  - C2_2: actual £106.25 vs. naked £231.94 -- hedging cost £125.69
  - C8: actual £-57.35 vs. naked £80.48 -- hedging cost £137.83

**Year narrative:** 2025 produced a net gain of £31,478.07 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 23 customer(s) experienced a bill shock of >=20%.
