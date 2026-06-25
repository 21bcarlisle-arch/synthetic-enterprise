# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £2,788,978.93
  (£322,342.71 net change)
- Solvency signal (final year): £303,286/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £17,873,063.73
  VAT remitted to HMRC: (£859,596.26) | Revenue (ex-VAT): £17,013,467.47
  Non-commodity pass-through: (£4,015,878.29)
- Gross margin: £5,128,206.72
- Capital costs: £64,955.93
- Net margin: £5,063,250.79
- Capital cost ratio: 1.3% of gross
- Net margin as % of revenue: 29.8%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 50
- Bills issued: 1549, average clarity 0.859,
  service quality score 0.919
- Enterprise value (CLV sum across 14 billing accounts): £5,568,452.95
- Cost to serve (whole portfolio): £85,412.95, net margin after cost to serve: £4,977,837.83
- Hedge effectiveness (whole window): hedging cost £3,820,008.77 vs. a fully unhedged book (commodity-only: actual net £322,342.71 vs. naked net £4,142,351.48)

- **2021** (crisis year): net margin £41,267.41, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £217,851.05, 9 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £5,128,206.72, capital £64,955.93, net £5,063,250.79. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 1.3% (commodity basis, comparable to old model) / 1.3% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £41,267.41 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 29.8%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £5,063,250.79
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £4,142,351.48
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £3,820,008.77 vs. a fully unhedged book (commodity-only: actual net £322,342.71 vs. naked net £4,142,351.48)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £117,694.00 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £608,067.90 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £78.36 | £305.50 | £99.64 | £483.50 |
| 2017 | £30,340.95 | £0.00 | £177.18 | £470.82 | £202.39 | £31,191.33 |
| 2018 | £107,088.37 | £0.00 | £-335.13 | £246.92 | £154.27 | £107,154.42 |
| 2019 | £230,260.38 | £-40,455.11 | £217.74 | £489.51 | £173.06 | £190,685.57 |
| 2020 | £-44,714.91 | £-5,116.89 | £146.11 | £567.48 | £195.82 | £-48,922.38 |
| 2021 | £-84,521.89 | £125,577.06 | £204.55 | £292.35 | £-284.67 | £41,267.41 |
| 2022 | £175,981.98 | £43,790.89 | £952.42 | £-1,866.39 | £-1,007.85 | £217,851.05 |
| 2023 | £-116,008.53 | £-253,415.10 | £1,296.35 | £143.31 | £-1,003.54 | £-368,987.50 |
| 2024 | £141,215.36 | £-17,341.82 | £509.19 | £1,731.17 | £357.52 | £126,471.41 |
| 2025 | £28,562.68 | £-3,756.29 | £0.00 | £279.08 | £62.43 | £25,147.91 |

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
| C4 | 2024-09-29 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.9018 |
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
| 2016 | 3 | -63.2% | 63.2% |
| 2017 | 3 | -91.5% | 91.5% |
| 2018 | 4 | +466.1% | 540.0% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | -17.5% | 144.3% |
| 2021 | 9 | +4.7% | 123.8% |
| 2022 | 7 | -28.3% | 93.3% |
| 2023 | 7 | +2.7% | 136.3% |
| 2024 | 7 | +76.1% | 234.6% |
| 2025 | 2 | -94.4% | 94.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 33.6%, abs error 299.4%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.9%, abs error 144.3%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.7% | 0.0% | 63.2% |
| 2017 | 0 | 3 | 0.0% | 2.1% | 0.0% | 91.5% |
| 2018 | 2 | 2 | 20.4% | 50.1% | 136.9% | 943.2% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 16.7% | 0.5% | 191.0% | 97.6% |
| 2021 | 3 | 6 | 63.6% | 4.0% | 207.9% | 81.7% |
| 2022 | 0 | 7 | 0.0% | 19.5% | 0.0% | 93.3% |
| 2023 | 2 | 5 | 24.2% | 19.0% | 47.6% | 171.8% |
| 2024 | 3 | 4 | 37.4% | 0.0% | 414.0% | 100.0% |
| 2025 | 0 | 2 | 0.0% | 2.1% | 0.0% | 94.4% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 10 (26%)
- **Below/at SVT (protected):** 29 (74%)
- **Mean rate vs SVT premium:** -8.3%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -2.3% | 136.7 | 140.0 |
| 2017 | 3 | 0 (0%) | -11.1% | 124.5 | 140.0 |
| 2018 | 2 | 2 (100%) | +4.3% | 159.0 | 152.5 |
| 2019 | 2 | 0 (0%) | -26.9% | 130.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -24.9% | 132.8 | 176.9 |
| 2021 | 6 | 3 (50%) | +1.3% | 185.0 | 183.8 |
| 2022 | 7 | 4 (57%) | +12.1% | 295.9 | 318.4 |
| 2023 | 5 | 0 (0%) | -31.8% | 227.3 | 364.0 |
| 2024 | 4 | 0 (0%) | -13.5% | 213.3 | 246.9 |
| 2025 | 2 | 1 (50%) | +3.9% | 258.2 | 248.6 |

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
| 2020 | 10 | 1.44× | 6.34× |
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
| 2018 | 65,813 | 9,922 | 17,518 | 9,388 | 17,364 | 120,006 |  |
| 2019 | 164,970 | 28,414 | 42,551 | 32,030 | 44,393 | 312,359 |  |
| 2020 | 239,071 | 35,455 | 69,576 | 56,655 | 70,153 | 470,911 |  |
| 2021 | 248,968 | 15,148 | 72,020 | 50,135 | 63,418 | 449,689 |  |
| 2022 | 259,219 | -50,329 | 71,820 | 37,160 | 69,888 | 387,758 | ⬇ CfD REBATE |
| 2023 | 274,511 | 65,413 | 72,465 | 51,388 | 75,835 | 539,612 |  |
| 2024 | 310,695 | 111,051 | 73,601 | 69,383 | 83,390 | 648,120 |  |
| 2025 | 137,776 | 47,658 | 31,649 | 31,498 | 36,697 | 285,279 |  |
| **Total** | **1,739,398** | **265,456** | **462,574** | **339,654** | **471,398** | **3,278,479** | |

Total policy cost: £3,278,479 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2019 | 135,991 | 110,394 | 25,597 | 15,273 | 50,131 | 475 | -40,282 | -29.6% |
| 2020 | 119,695 | 57,391 | 62,304 | 19,520 | 46,890 | 814 | -4,921 | -4.1% |
| 2021 | 296,625 | 97,288 | 199,338 | 22,523 | 50,386 | 1,136 | 125,292 | +42.2% |
| 2022 | 593,793 | 466,992 | 126,802 | 27,135 | 54,413 | 2,471 | 42,783 | +7.2% |
| 2023 | 295,491 | 436,985 | -141,493 | 32,320 | 80,214 | 392 | -254,419 | -86.1% |
| 2024 | 270,499 | 168,958 | 101,542 | 37,573 | 76,143 | 4,810 | -16,984 | -6.3% |
| 2025 | 128,880 | 81,207 | 47,673 | 16,774 | 31,087 | 3,506 | -3,694 | -2.9% |
| **Total** | **1,845,527** | **1,421,689** | **423,838** | **171,119** | **390,853** | **13,635** | **-151,768** | **-8.2%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b)

Treasury balance ÷ active billing accounts at each year-end.
Ofgem licence floor: £0/account (positive net assets required to hold a supply licence).
Capital adequacy target: £130/dual-fuel billing account.

| Year | Treasury £ | Billing Accounts | Net Assets/Account £ | vs Floor | vs £130 Target |
|------|-----------|-----------------|----------------------|----------|----------------|
| 2016 | 2,467,046 | 9 | 274,116 | OK | OK |
| 2017 | 2,497,889 | 10 | 249,789 | OK | OK |
| 2018 | 2,486,422 | 11 | 226,038 | OK | OK |
| 2019 | 2,616,704 | 12 | 218,059 | OK | OK |
| 2020 | 2,708,236 | 13 | 208,326 | OK | OK |
| 2021 | 2,702,751 | 12 | 225,229 | OK | OK |
| 2022 | 2,833,101 | 11 | 257,555 | OK | OK |
| 2023 | 2,501,875 | 10 | 250,188 | OK | OK |
| 2024 | 2,673,221 | 10 | 267,322 | OK | OK |
| 2025 | 2,729,574 | 9 | 303,286 | OK | OK |

End-state (2025): **£303,286/account** across 9 billing accounts — above Ofgem £130 target.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 23 | 28 | 2,467,046 | 88077.3× | OK |
| 2017 | 466 | 559 | 2,497,889 | 4466.5× | OK |
| 2018 | 851 | 1,021 | 2,486,422 | 2434.1× | OK |
| 2019 | 1,543 | 1,851 | 2,616,704 | 1413.4× | OK |
| 2020 | 1,980 | 2,377 | 2,708,236 | 1139.6× | OK |
| 2021 | 4,411 | 5,293 | 2,702,751 | 510.6× | OK |
| 2022 | 8,498 | 10,198 | 2,833,101 | 277.8× | OK |
| 2023 | 5,612 | 6,734 | 2,501,875 | 371.5× | OK |
| 2024 | 2,739 | 3,287 | 2,673,221 | 813.2× | OK |
| 2025 | 4,213 | 5,056 | 2,729,574 | 539.9× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,317.74 | £11,420.98 | £257.05/MWh | £135.02/MWh | +0.1% |
| C8 | 106,722 | 43,948 | 41.2% | £11,763.06 | £8,814.54 | £267.66/MWh | £140.42/MWh | +8.1% |
| C9 | 109,387 | 43,689 | 39.9% | £10,729.15 | £8,452.13 | £245.58/MWh | £128.65/MWh | +7.1% |

Total HH revenue: £60,497.60 vs flat equivalent £57,660.04 (+4.9% ToU premium)

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
| 2021 | 38 | 88% | C_IC2 (2021-04-30) |
| 2022 | 54 | 1712% | C2_2 (2022-04-30) |
| 2023 | 35 | 116% | C_IC2 (2023-06-30) |
| 2024 | 29 | 122% | C_IC2 (2024-07-31) |
| 2025 | 23 | 81% | C_IC4 (2025-06-07) |

Total: **330** bill shock events across 10 years

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
| Total offer cost (foregone margin) | £421,696.92 |
| Margin saved (retained customers' terms) | £2,223,539.75 |
| Wasted offer cost (churned anyway) | £505.78 |
| **Net ROI of retention strategy** | **£1,801,842.84** |
| Acquisition cost avoided (retained customers) | £2,800.00 |
| **Full economic ROI (margin + acq savings)** | **£1,804,642.84** |

Missed opportunities (churns with no offer): **4** (£3,340.43 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 4 (£3,340.43 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24805.26 | £170092.16 | £145286.90 | £0.00 |
| 2019 | 2 | 2 | £43640.54 | £305760.64 | £262120.11 | £0.00 |
| 2020 | 3 | 3 | £27572.92 | £180213.20 | £152640.28 | £394.13 |
| 2021 | 4 | 3 | £121126.69 | £419308.38 | £298181.69 | £-142.51 |
| 2022 | 2 | 2 | £70311.55 | £277428.96 | £207117.41 | £320.54 |
| 2023 | 4 | 4 | £89125.12 | £454348.74 | £365223.62 | £0.00 |
| 2024 | 2 | 2 | £45114.83 | £416387.67 | £371272.84 | £2768.27 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24805.26 | £170092.16 | £150 | £145286.90 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £15172.47 | £105268.85 | £150 | £90096.38 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £28468.07 | £200491.79 | £150 | £172023.73 | retained |
| 2020-01-01 | C_IC3 | 0.38 | 3% | £5910.94 | £16739.66 | £150 | £10828.73 | retained |
| 2020-03-31 | C_IC1 | 0.52 | 5% | £10690.67 | £137077.64 | £150 | £126386.97 | retained |
| 2020-12-31 | C_IC3 | 0.59 | 5% | £10971.32 | £26395.90 | £150 | £15424.58 | retained |
| 2021-03-31 | C_IC2 | 0.82 | 8% | £14288.22 | £92377.21 | £150 | £78088.99 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £22679.45 | £159451.63 | £150 | £136772.18 | retained |
| 2021-12-30 | C5 | 0.77 | 8% | £505.78 | £2190.04 | £400 | £-505.78 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £83653.24 | £167479.53 | £150 | £83826.29 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £23795.33 | £75790.56 | £150 | £51995.23 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £46516.22 | £201638.40 | £150 | £155122.18 | retained |
| 2023-03-31 | C6 | 0.37 | 3% | £198.45 | £3073.41 | £400 | £2874.95 | retained |
| 2023-05-30 | C_IC2 | 0.61 | 5% | £11922.97 | £133332.51 | £150 | £121409.54 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £35524.27 | £250850.88 | £150 | £215326.61 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £41479.43 | £67091.95 | £150 | £25612.51 | retained |
| 2024-06-28 | C_IC2 | 0.56 | 5% | £10497.77 | £137873.24 | £150 | £127375.46 | retained |
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

**Full-history EV:** £5,568,452.95 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £-237,205.87 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £483.50 |
| 2017 | £31,191.33 |
| 2018 | £107,154.42 |
| 2019 | £190,685.57 |
| 2020 | £-48,922.38 |
| 2021 | £41,267.41 |
| 2022 | £217,851.05 |
| 2023 | £-368,987.50 | ← trailing
| 2024 | £126,471.41 | ← trailing
| 2025 | £25,147.91 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £2,686.33 | — |
| C2 | £5,741.02 | — |
| C2_2 | — | £1,473.16 |
| C3 | £3,040.93 | — |
| C4 | £3,394.18 | £-785.99 |
| C5 | £10,034.28 | — |
| C6 | £15,877.06 | £2,967.80 |
| C7 | £7,470.95 | £-66.55 |
| C8 | £8,290.57 | £273.51 |
| C9 | £8,153.32 | £826.27 |
| C_IC1 | £1,638,990.81 | £391,982.74 |
| C_IC2 | £1,022,910.96 | £206,249.51 |
| C_IC3 | £2,805,150.89 | £-267,208.29 |
| C_IC4 | £32,411.05 | £-572,918.04 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £1,830.67 | — | — | — | — | £5,444.51 | — | £4,335.93 | — | — | — | — | — | — |
| 2017 | £2,677.24 | £7,456.13 | — | £2,927.82 | £4,248.28 | £8,197.80 | £12,327.68 | £5,048.82 | £8,407.97 | £6,413.77 | — | — | — | — |
| 2018 | £2,238.64 | £5,436.30 | — | £2,766.70 | £3,486.92 | £9,389.12 | £10,473.39 | £5,717.27 | £6,652.64 | £6,107.26 | £2,470,926.60 | — | — | — |
| 2019 | £2,615.41 | £4,787.15 | — | £2,903.47 | £3,648.05 | £7,610.96 | £11,163.65 | £5,305.56 | £6,086.08 | £5,572.94 | £1,826,497.92 | £1,079,955.42 | — | — |
| 2020 | £2,109.74 | £5,313.64 | — | £2,098.18 | £3,828.81 | £7,934.21 | £8,759.62 | £5,347.85 | £6,607.81 | £5,829.22 | £1,040,213.34 | £551,264.96 | £1,494,959.42 | £27,358.56 |
| 2021 | £1,739.65 | £4,862.43 | — | £1,826.13 | £2,899.94 | £6,423.47 | £8,759.41 | £4,733.13 | £6,246.12 | £4,971.16 | £986,436.98 | £550,748.45 | £1,728,489.73 | £23,130.05 |
| 2022 | £2,135.45 | £3,729.35 | £486.79 | £1,992.67 | £1,717.78 | £6,182.90 | £9,431.33 | £3,837.76 | £5,524.74 | £5,185.02 | £954,862.60 | £543,509.68 | £1,800,442.59 | £18,885.49 |
| 2023 | £2,135.12 | £3,642.61 | £1,607.52 | £1,899.82 | £1,131.42 | £6,047.23 | £9,950.60 | £3,694.64 | £5,332.61 | £5,231.77 | £991,042.84 | £574,599.03 | £1,339,502.60 | £18,214.36 |
| 2024 | £2,152.26 | £3,740.06 | £2,406.76 | £1,881.50 | £1,916.74 | £5,946.53 | £9,609.29 | £4,244.89 | £5,654.44 | £5,648.95 | £1,028,492.16 | £613,512.35 | £1,539,488.85 | £18,961.40 |
| 2025 | £2,082.06 | £3,445.50 | £2,539.48 | £1,797.55 | £2,033.92 | £5,949.32 | £9,724.95 | £4,569.06 | £5,224.19 | £5,444.54 | £1,076,900.03 | £643,700.88 | £1,682,579.91 | £20,474.26 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,495.42, range £32.62–£26,325.15.

- C1: cost to serve £390.52, net margin after CTS £1,443.29
- C1g: cost to serve £48.73, net margin after CTS £887.95
- C2: cost to serve £452.09, net margin after CTS £3,374.16
- C2_2: cost to serve £379.07, net margin after CTS £4,980.17
- C2g: cost to serve £61.54, net margin after CTS £1,216.73
- C3: cost to serve £262.93, net margin after CTS £1,084.32
- C3g: cost to serve £32.62, net margin after CTS £575.64
- C4: cost to serve £647.62, net margin after CTS £3,313.70
- C4g: cost to serve £167.30, net margin after CTS £455.54
- C5: cost to serve £868.61, net margin after CTS £8,176.78
- C6: cost to serve £1,268.50, net margin after CTS £16,391.67
- C7: cost to serve £933.91, net margin after CTS £8,804.83
- C8: cost to serve £916.98, net margin after CTS £10,422.29
- C9: cost to serve £875.35, net margin after CTS £10,756.67
- C_IC1: cost to serve £19,996.83, net margin after CTS £1,868,893.29
- C_IC2: cost to serve £11,388.86, net margin after CTS £898,002.09
- C_IC3: cost to serve £26,325.15, net margin after CTS £1,757,596.69
- C_IC3g: cost to serve £9,224.23, net margin after CTS £411,167.79
- C_IC4: cost to serve £11,172.13, net margin after CTS £21,351.71 — MARGIN_SQUEEZE (below 2% benchmark)

**Activity-Based Pricing Actions**

The following 1 customer(s) are profitable but below the 2% net-margin benchmark (MARGIN_SQUEEZE): C_IC4


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 33 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 13.5%.

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
| C_IC3g | gas | 2020-01-01 | £-40,455.11 | £134,045.32 | +20.0% | £16.25/MWh | £18.96/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,904.90 | £3,444.18 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,041.06 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-3,729.85 | £5,726.15 | +20.0% | £138.90/MWh | £174.68/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,006.00 | £14,511.74 | +20.0% | £113.97/MWh | £138.75/MWh |
| C4 | electricity | 2021-09-30 | £-56.12 | £684.66 | +3.2% | £205.15/MWh | £218.15/MWh |
| C4g | gas | 2021-09-30 | £-96.12 | £364.35 | +20.0% | £53.99/MWh | £67.28/MWh |
| C1 | electricity | 2021-12-30 | £-45.21 | £514.96 | +3.8% | £311.83/MWh | £328.74/MWh |
| C5 | electricity | 2021-12-30 | £-284.71 | £2,645.93 | +5.8% | £311.83/MWh | £335.01/MWh |
| C_IC3 | electricity | 2021-12-31 | £-22,573.32 | £434,047.38 | +0.2% | £224.03/MWh | £258.15/MWh |
| C_IC2 | electricity | 2022-04-30 | £-1,292.09 | £17,661.75 | +2.3% | £269.81/MWh | £292.86/MWh |
| C_IC1 | electricity | 2022-05-30 | £-4,406.97 | £22,384.38 | +14.7% | £239.42/MWh | £288.55/MWh |
| C4 | electricity | 2022-09-30 | £-373.92 | £1,021.16 | +20.0% | £404.86/MWh | £483.05/MWh |
| C4g | gas | 2022-09-30 | £-791.90 | £770.00 | +20.0% | £183.79/MWh | £243.50/MWh |
| C7 | electricity | 2022-12-30 | £-1,688.34 | £2,236.99 | +20.0% | £266.73/MWh | £323.45/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,193.41 | £7,055.33 | +20.0% | £171.46/MWh | £234.21/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,414.36 | £17,979.18 | +20.0% | £163.19/MWh | £219.03/MWh |
| C4 | electricity | 2023-09-30 | £-556.59 | £1,701.85 | +20.0% | £216.77/MWh | £257.18/MWh |
| C4g | gas | 2023-09-30 | £-1,481.14 | £2,090.00 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-326.36 | £3,797.69 | +3.6% | £242.22/MWh | £238.38/MWh |
| C_IC3 | electricity | 2023-12-31 | £-159,497.57 | £939,446.88 | +12.0% | £118.95/MWh | £126.54/MWh |
| C_IC3g | gas | 2023-12-31 | £-252,917.30 | £294,338.38 | +20.0% | £51.89/MWh | £71.61/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,916.03 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,612.90 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |
| C_IC3g | gas | 2024-12-30 | £-17,160.47 | £268,215.17 | +1.4% | £50.47/MWh | £56.56/MWh |


## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 113 renewal(s) (27 gas) based on recent portfolio-wide margin rates: 87 surcharge(s), 26 discount(s).

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
| C2g | gas | 2019-04-01 | -2.8% | +5.4% | £32.94/MWh | £34.71/MWh |
| C6 | electricity | 2019-04-01 | 6.4% | +0.8% | £148.35/MWh | £149.54/MWh |
| C8 | electricity | 2019-04-01 | 25.5% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 17.0% | -4.5% | £127.03/MWh | £121.32/MWh |
| C3g | gas | 2019-07-01 | -1.5% | +4.8% | £23.62/MWh | £24.74/MWh |
| C9 | electricity | 2019-07-01 | 5.7% | +1.2% | £127.03/MWh | £128.50/MWh |
| C4 | electricity | 2019-10-01 | 5.8% | +1.1% | £126.72/MWh | £128.09/MWh |
| C4g | gas | 2019-10-01 | 1.8% | +3.1% | £20.41/MWh | £21.04/MWh |
| C1 | electricity | 2019-12-31 | 5.6% | +1.2% | £127.44/MWh | £128.97/MWh |
| C1g | gas | 2019-12-31 | 0.9% | +3.5% | £26.17/MWh | £27.09/MWh |
| C5 | electricity | 2019-12-31 | 3.3% | +2.3% | £127.44/MWh | £130.41/MWh |
| C7 | electricity | 2019-12-31 | 3.1% | +2.5% | £127.44/MWh | £130.58/MWh |
| C_IC3 | electricity | 2020-01-01 | 1.2% | +3.4% | £47.59/MWh | £49.21/MWh |
| C_IC3g | gas | 2020-01-01 | 13.5% | -2.8% | £16.25/MWh | £15.80/MWh |
| C_IC2 | electricity | 2020-03-01 | -97.5% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -90.0% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 11.6% | -1.8% | £22.80/MWh | £22.40/MWh |
| C6 | electricity | 2020-03-31 | -47.9% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -17.5% | +12.8% | £125.12/MWh | £141.09/MWh |
| C_IC1 | electricity | 2020-03-31 | 18.7% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 15.4% | -3.7% | £113.43/MWh | £109.24/MWh |
| C9 | electricity | 2020-06-30 | 15.4% | -3.7% | £113.43/MWh | £109.24/MWh |
| C4 | electricity | 2020-09-30 | 11.3% | -1.7% | £124.42/MWh | £122.34/MWh |
| C4g | gas | 2020-09-30 | 12.4% | -2.2% | £16.94/MWh | £16.56/MWh |
| C1 | electricity | 2020-12-30 | 7.3% | +0.4% | £133.55/MWh | £134.05/MWh |
| C1g | gas | 2020-12-30 | 2.6% | +2.7% | £28.99/MWh | £29.77/MWh |
| C5 | electricity | 2020-12-30 | 0.7% | +3.7% | £133.55/MWh | £138.46/MWh |
| C7 | electricity | 2020-12-30 | -7.4% | +7.7% | £133.55/MWh | £143.86/MWh |
| C_IC3 | electricity | 2020-12-31 | -7.7% | +7.9% | £50.65/MWh | £54.63/MWh |
| C_IC3g | gas | 2020-12-31 | -6.6% | +7.3% | £20.05/MWh | £21.51/MWh |
| C2 | electricity | 2021-03-31 | -30.2% | +15.0% | £175.90/MWh | £202.28/MWh |
| C2g | gas | 2021-03-31 | 5.1% | +1.4% | £36.20/MWh | £36.72/MWh |
| C6 | electricity | 2021-03-31 | -26.5% | +15.0% | £175.90/MWh | £202.28/MWh |
| C8 | electricity | 2021-03-31 | -21.6% | +14.8% | £175.90/MWh | £201.96/MWh |
| C_IC2 | electricity | 2021-03-31 | -1.6% | +4.8% | £138.90/MWh | £145.56/MWh |
| C_IC1 | electricity | 2021-04-30 | 5.1% | +1.5% | £113.97/MWh | £115.63/MWh |
| C9 | electricity | 2021-06-30 | 5.5% | +1.2% | £170.38/MWh | £172.47/MWh |
| C4 | electricity | 2021-09-30 | 1.9% | +3.0% | £205.15/MWh | £211.39/MWh |
| C4g | gas | 2021-09-30 | 0.3% | +3.9% | £53.99/MWh | £56.06/MWh |
| C1 | electricity | 2021-12-30 | 4.8% | +1.6% | £311.83/MWh | £316.77/MWh |
| C5 | electricity | 2021-12-30 | 4.8% | +1.6% | £311.83/MWh | £316.77/MWh |
| C7 | electricity | 2021-12-30 | 4.8% | +1.6% | £311.83/MWh | £316.77/MWh |
| C_IC3 | electricity | 2021-12-31 | -23.6% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -18.8% | +13.4% | £109.48/MWh | £124.15/MWh |
| C2 | electricity | 2022-03-31 | -31.7% | +15.0% | £361.95/MWh | £416.24/MWh |
| C6 | electricity | 2022-03-31 | -21.3% | +14.7% | £361.95/MWh | £414.97/MWh |
| C8 | electricity | 2022-03-31 | 1.4% | +3.3% | £361.95/MWh | £373.90/MWh |
| C_IC2 | electricity | 2022-04-30 | -4.2% | +6.1% | £269.81/MWh | £286.23/MWh |
| C_IC1 | electricity | 2022-05-30 | -2.2% | +5.1% | £239.42/MWh | £251.60/MWh |
| C9 | electricity | 2022-06-30 | 7.0% | +0.5% | £255.09/MWh | £256.36/MWh |
| C4 | electricity | 2022-09-30 | 9.1% | -0.6% | £404.86/MWh | £402.54/MWh |
| C4g | gas | 2022-09-30 | -12.8% | +10.4% | £183.79/MWh | £202.91/MWh |
| C7 | electricity | 2022-12-30 | 5.9% | +1.1% | £266.73/MWh | £269.54/MWh |
| C_IC3 | electricity | 2022-12-31 | -2.1% | +5.0% | £168.36/MWh | £176.84/MWh |
| C_IC3g | gas | 2022-12-31 | -41.2% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -31.4% | +15.0% | £319.17/MWh | £367.05/MWh |
| C6 | electricity | 2023-03-31 | -16.7% | +12.3% | £319.17/MWh | £358.52/MWh |
| C8 | electricity | 2023-03-31 | -8.9% | +8.4% | £319.17/MWh | £346.13/MWh |
| C_IC2 | electricity | 2023-05-30 | -19.7% | +13.8% | £171.46/MWh | £195.18/MWh |
| C_IC1 | electricity | 2023-06-29 | -15.7% | +11.8% | £163.19/MWh | £182.52/MWh |
| C9 | electricity | 2023-06-30 | -8.8% | +8.4% | £224.44/MWh | £243.34/MWh |
| C4 | electricity | 2023-09-30 | 10.3% | -1.1% | £216.77/MWh | £214.31/MWh |
| C4g | gas | 2023-09-30 | -63.1% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 27.1% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 20.5% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -30.3% | +15.0% | £51.89/MWh | £59.68/MWh |
| C2_2 | electricity | 2024-03-30 | -13.1% | +10.5% | £207.71/MWh | £229.57/MWh |
| C6 | electricity | 2024-03-30 | -15.6% | +11.8% | £207.71/MWh | £232.23/MWh |
| C8 | electricity | 2024-03-30 | -15.6% | +11.8% | £207.71/MWh | £232.23/MWh |
| C_IC2 | electricity | 2024-06-28 | -32.8% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.1% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -27.2% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.44/MWh |
| C4g | gas | 2024-09-29 | -33.7% | +15.0% | £50.11/MWh | £57.63/MWh |
| C7 | electricity | 2024-12-29 | 18.3% | -5.0% | £243.79/MWh | £231.60/MWh |
| C_IC3 | electricity | 2024-12-30 | 8.6% | -0.3% | £116.37/MWh | £116.02/MWh |
| C_IC3g | gas | 2024-12-30 | -13.1% | +10.5% | £50.47/MWh | £55.78/MWh |
| C2_2 | electricity | 2025-03-30 | -21.1% | +14.6% | £284.89/MWh | £326.39/MWh |
| C8 | electricity | 2025-03-30 | -14.5% | +11.3% | £284.89/MWh | £316.98/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **4** | Blind misses: **4** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 1 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £3,340.43 | deliberate: £0.00 | total: £3,340.43

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.11 | No | £394.13 |
| C1 | 2021-12-30 | Blind miss | 0.03 | 0.17 | No | £-142.51 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.11 | No | £320.54 |
| C6 | 2024-03-30 | Blind miss | 0.17 | 0.38 | Yes | £2,768.27 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C2+C2g | £430.96 | £379.78 | £810.73 | Yes |
| C1+C1g | £78.62 | £218.41 | £297.03 | Yes |
| C3+C3g | £-14.48 | £49.99 | £35.51 | Yes |
| C4+C4g | £-677.76 | £-1,699.11 | £-2,376.87 | No |
| C_IC3+C_IC3g | £145,796.23 | £-150,717.26 | £-4,921.02 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-151,768.19.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £322,342.71 across 19 billing accounts. Revenue: £12,983,690.74.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,155,741.85 | £1,888,890.12 | £18,611.07 | £881,325.21 | 27.9% |
| 2 | C_IC2 | fixed | £1,534,135.70 | £909,390.95 | £8,569.98 | £445,953.09 | 29.1% |
| 3 | C_IC3 | pass_through | £4,621,365.24 | £1,783,921.84 | £23,239.77 | £145,796.23 | 3.2% |
| 4 | C6 | fixed | £30,872.18 | £17,660.16 | £218.07 | £3,374.59 | 10.9% |
| 5 | C2_2 | fixed | £10,178.58 | £5,359.24 | £71.92 | £1,496.57 | 14.7% |
| 6 | C8 | fixed | £20,577.61 | £11,339.28 | £136.01 | £1,380.42 | 6.7% |
| 7 | C9 | fixed | £19,181.28 | £11,632.01 | £129.81 | £1,354.06 | 7.1% |
| 8 | C2 | fixed | £6,107.91 | £3,826.26 | £31.70 | £430.96 | 7.1% |
| 9 | C2g | fixed | £2,733.45 | £1,278.27 | £17.31 | £379.78 | 13.9% |
| 10 | C1g | fixed | £2,092.54 | £936.68 | £14.90 | £218.41 | 10.4% |
| 11 | C1 | fixed | £3,029.33 | £1,833.81 | £15.91 | £78.62 | 2.6% |
| 12 | C3g | fixed | £1,401.81 | £608.26 | £9.77 | £49.99 | 3.6% |
| 13 | C3 | fixed | £2,148.79 | £1,347.25 | £9.79 | £-14.48 | -0.7% |
| 14 | C5 | fixed | £14,875.90 | £9,045.39 | £80.30 | £-127.82 | -0.9% |
| 15 | C4 | fixed | £8,488.36 | £3,961.32 | £65.49 | £-677.76 | -8.0% |
| 16 | C7 | fixed | £20,738.71 | £9,738.74 | £141.12 | £-1,388.65 | -6.7% |
| 17 | C4g | fixed | £7,866.96 | £622.84 | £132.04 | £-1,699.11 | -21.6% |
| 18 | C_IC3g | pass_through | £1,831,432.12 | £420,392.01 | £13,460.98 | £-150,717.26 | -8.2% |
| 19 | C_IC4 | flex | £1,690,722.42 | £32,523.85 | £0.00 | £-1,004,870.14 | -59.4% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £12,983,691 | 100.0% |
| Wholesale cost | -£7,869,382 | 60.6% |
| **Gross supply margin** | **£5,114,308** | **39.4%** |
| Policy + Network costs | -£4,727,010 | 36.4% |
| Capital cost | -£64,956 | 0.5% |
| **Net supply margin** | **£322,343** | **2.5%** |

> *The ledger's `net_margin_gbp` (£5,063,251) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £11,001,965 | 41.9% | 4.3% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,831,432 | 23.0% | -8.2% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £45,748 | 58.4% | 7.1% | CMA 3-8% | ✓ |
| resi/elec | £80,272 | 54.4% | 1.4% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £14,095 | 24.4% | -7.5% | Ofgem CMA 2-4% | ⚠ ANOMALY |

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
| Customer bills (all-in) | £17,873,063.73 |
|   Less: VAT remitted to HMRC | (£859,596.26) |
| = Revenue (ex-VAT) | £17,013,467.47 |
| Less: non-commodity pass-through | (£4,015,878.29) |
| Wholesale cost (settlement events) | (£7,869,382.46) |
| Gross margin | £5,128,206.72 |
| Capital charges | (£64,955.93) |
| Net margin | £5,063,250.79 |

_Cash reconciliation: of £17,873,063.73 billed, bad debt of £357,417.68 was written off, leaving £17,515,646.05 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £5,565,429.37._

| Acquisition spend | (£950.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £5,056,600.79 |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £5,056,600.79

## 2016

**Trading & Risk**

- Net margin: £483.50 (gross £5,566.16, capital £75.72)
  - Electricity: gross £5,105.33, capital £70.30, net £383.86
  - Gas: gross £460.83, capital £5.42, net £99.64
- Treasury at year end: £2,467,046.39
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.22, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-01-31: treasury £2,466,641.13, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-01: treasury £2,466,646.13, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-31: treasury £2,466,650.88, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-04-30: treasury £2,466,654.76, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-05-30: treasury £2,466,658.54, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-06-29: treasury £2,466,661.95, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-07-29: treasury £2,466,665.46, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-08-28: treasury £2,466,668.99, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-09-27: treasury £2,466,672.72, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-10-27: treasury £2,466,676.47, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-11-26: treasury £2,466,680.28, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-12-26: treasury £2,466,685.01, C1->1.00, C2->0.95, C3->0.95, C4->0.95, C5->0.95, C6->0.95, C7->0.95, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £22.23 / stressed £6.83) ratio 3.25
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
  - 2017-01-25: treasury £2,467,046.38, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-02-24: treasury £2,467,046.47, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-03-26: treasury £2,467,047.00, C1->1.00, C2->1.00, C3->0.95, C4->0.95, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-04-25: treasury £2,467,108.67, C1->1.00, C2->1.00, C3->0.99, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-05-25: treasury £2,467,104.82, C1->1.00, C2->1.00, C3->0.99, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-06-24: treasury £2,467,101.63, C1->1.00, C2->1.00, C3->0.99, C4->0.95, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.95, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-07-24: treasury £2,467,073.90, C1->1.00, C2->1.00, C3->0.99, C4->0.99, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.99, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-08-23: treasury £2,467,070.08, C1->1.00, C2->1.00, C3->0.99, C4->0.99, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.99, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-09-22: treasury £2,467,065.61, C1->1.00, C2->1.00, C3->0.99, C4->0.99, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.99, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-10-22: treasury £2,467,167.20, C1->1.00, C2->1.00, C3->0.99, C4->0.99, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.99, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £887.92 / stressed £351.47) ratio 2.53
  - 2017-11-21: treasury £2,467,172.05, C1->1.00, C2->1.00, C3->0.99, C4->0.99, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.99, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £887.92 / stressed £351.47) ratio 2.53
  - 2017-12-21: treasury £2,467,176.76, C1->1.00, C2->1.00, C3->0.99, C4->0.99, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->0.99, C_IC1->0.95, C_IC2->0.95, C_IC3->0.95, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £887.92 / stressed £351.47) ratio 2.53
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

- Net margin: £190,685.57 (gross £659,433.57, capital £2,575.08)
  - Electricity: gross £633,836.55, capital £2,099.92, net £230,967.63
  - Gas: gross £25,597.03, capital £475.16, net £-40,282.05
- Treasury at year end: £2,616,703.89
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.88 (avg 0.88), C6 0.91 (avg 0.91), C7 0.88 (avg 0.88), C8 0.92 (avg 0.92), C9 0.88 (avg 0.88), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2019-09-01 period 1, net margin £-158.02

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £268,740.60
  - By billing account: C1 £2,615.41, C2 £4,787.15, C3 £2,903.47, C4 £3,648.05, C5 £7,610.96, C6 £11,163.65, C7 £5,305.56, C8 £6,086.08, C9 £5,572.94, C_IC1 £1,826,497.92, C_IC2 £1,079,955.42
- Bill shock events (>=20%): 38 -- C1 2019-01-31 (21%); C1 2019-04-30 (22%); C5 2019-01-31 (45%); C5 2019-02-28 (22%); C5 2019-06-30 (26%); C5 2019-10-31 (44%); C5 2019-11-30 (36%); C7 2019-01-31 (42%); C7 2019-02-28 (26%); C7 2019-05-31 (24%); C7 2019-06-30 (35%); C7 2019-10-31 (72%); C7 2019-11-30 (46%); C2g 2019-04-30 (25%); C6 2019-02-28 (21%); C6 2019-06-30 (25%); C6 2019-10-31 (42%); C6 2019-11-30 (27%); C8 2019-01-31 (27%); C8 2019-02-28 (28%); C8 2019-04-30 (23%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-09-30 (61%); C8 2019-10-31 (88%); C8 2019-11-30 (38%); C3 2019-04-30 (21%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (37%); C9 2019-07-31 (35%); C9 2019-09-30 (53%); C9 2019-10-31 (76%); C9 2019-11-30 (38%); C4g 2019-10-31 (25%); C_IC1 2019-02-28 (55%); C_IC1 2019-03-31 (128%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 8 at risk (≥20% churn prob): C1 20%, C4 20%, C5 38%, C6 32%, C7 35%, C8 38%, C9 32%, C_IC1 23%

**Pricing & Margin**

- C1 (electricity): tariff £128.97-£162.68/MWh, net margin £58.09
- C1g (gas): tariff £26.00-£37.07/MWh, net margin £72.70
- C2 (electricity): tariff £142.94-£151.12/MWh, net margin £61.43
- C2g (gas): tariff £26.00-£37.88/MWh, net margin £33.47
- C3 (electricity): tariff £124.32-£128.73/MWh, net margin £-22.69 -- **net-negative**
- C3g (gas): tariff £24.74-£29.73/MWh, net margin £27.74
- C4 (electricity): tariff £128.09-£154.00/MWh, net margin £44.64
- C4g (gas): tariff £21.04-£34.63/MWh, net margin £39.15
- C5 (electricity): tariff £130.41-£163.06/MWh, net margin £178.98
- C6 (electricity): tariff £143.14-£152.57/MWh, net margin £38.76
- C7 (electricity): tariff £102.60-£227.85/MWh, net margin £69.22
- C8 (electricity): tariff £108.88-£211.40/MWh, net margin £116.26
- C9 (electricity): tariff £103.32-£207.68/MWh, net margin £162.56
- C_IC1 (electricity): tariff £0.00-£266.94/MWh, net margin £144,138.50
- C_IC2 (electricity): tariff £-60.00-£283.06/MWh, net margin £82,507.17
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £3,614.71
- C_IC3g (gas): tariff £27.53/MWh, net margin £-40,455.11 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.877, average bill shock 12.5%, bad debt provision £34,676.07, avg complaint probability 3.7%
- Solvency signal: £218,059/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £215,934.38 vs. naked (unhedged) net margin: £837,839.23
- hedging cost £621,904.85 vs. a fully unhedged book (commodity-only: actual net £215,934.38 vs. naked net £837,839.23)
  - C1: actual £4.14 vs. naked £322.97 -- hedging cost £318.83
  - C1g: actual £63.24 vs. naked £198.00 -- hedging cost £134.75
  - C2: actual £100.26 vs. naked £788.13 -- hedging cost £687.86
  - C2g: actual £13.39 vs. naked £222.05 -- hedging cost £208.65
  - C3: actual £-12.54 vs. naked £384.08 -- hedging cost £396.62
  - C3g: actual £60.78 vs. naked £218.76 -- hedging cost £157.97
  - C4: actual £34.93 vs. naked £513.45 -- hedging cost £478.51
  - C4g: actual £59.45 vs. naked £275.65 -- hedging cost £216.20
  - C5: actual £-76.69 vs. naked £1,518.60 -- hedging cost £1,595.29
  - C6: actual £169.72 vs. naked £2,034.71 -- hedging cost £1,864.99
  - C7: actual £36.28 vs. naked £1,093.60 -- hedging cost £1,057.32
  - C8: actual £179.50 vs. naked £1,272.20 -- hedging cost £1,092.70
  - C9: actual £171.01 vs. naked £1,235.66 -- hedging cost £1,064.65
  - C_IC1: actual £161,790.99 vs. naked £300,927.64 -- hedging cost £139,136.65
  - C_IC2: actual £90,180.30 vs. naked £165,284.43 -- hedging cost £75,104.13
  - C_IC3: actual £3,614.71 vs. naked £295,972.25 -- hedging cost £292,357.54
  - C_IC3g: actual £-40,455.11 vs. naked £65,577.06 -- hedging cost £106,032.18

**Year narrative:** 2019 produced a net gain of £190,685.57 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-48,922.38 (gross £615,910.38, capital £2,826.63)
  - Electricity: gross £553,606.61, capital £2,012.46, net £-44,001.32
  - Gas: gross £62,303.77, capital £814.17, net £-4,921.07
- Treasury at year end: £2,708,235.69
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.86 (avg 0.86), C7 0.88 (avg 0.88), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.85 (avg 0.85), C_IC4 0.95 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2020-05-01 period 1, net margin £-66.95

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2020): £243,201.95
  - By billing account: C1 £2,109.74, C2 £5,313.64, C3 £2,098.18, C4 £3,828.81, C5 £7,934.21, C6 £8,759.62, C7 £5,347.85, C8 £6,607.81, C9 £5,829.22, C_IC1 £1,040,213.34, C_IC2 £551,264.96, C_IC3 £1,494,959.42, C_IC4 £27,358.56
- Bill shock events (>=20%): 31 -- C1 2020-04-30 (21%); C5 2020-04-30 (29%); C5 2020-10-31 (39%); C5 2020-12-31 (26%); C7 2020-04-30 (35%); C7 2020-05-31 (21%); C7 2020-06-30 (28%); C7 2020-10-31 (62%); C7 2020-11-30 (24%); C7 2020-12-31 (35%); C6 2020-04-30 (30%); C6 2020-09-30 (21%); C6 2020-10-31 (34%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (26%); C8 2020-06-30 (33%); C8 2020-09-30 (57%); C8 2020-10-31 (68%); C8 2020-12-31 (44%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-09-30 (47%); C9 2020-10-31 (51%); C9 2020-12-31 (37%); C_IC1 2020-03-31 (58%); C_IC1 2020-04-30 (77%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (123%); C_IC4 2020-12-31 (21%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 23%, C5 35%, C6 32%, C7 38%, C8 38%, C9 41%, C_IC4 23%

**Pricing & Margin**

- C1 (electricity): tariff £128.97-£137.05/MWh, net margin £3.74
- C1g (gas): tariff £25.00-£26.00/MWh, net margin £63.13
- C2 (electricity): tariff £143.89-£151.12/MWh, net margin £140.85
- C2g (gas): tariff £22.40-£26.00/MWh, net margin £60.87
- C3 (electricity): tariff £124.32/MWh, net margin £-6.61 -- **net-negative**
- C3g (gas): tariff £24.74/MWh, net margin £33.66
- C4 (electricity): tariff £122.34-£128.09/MWh, net margin £13.16
- C4g (gas): tariff £16.56-£21.04/MWh, net margin £38.15
- C5 (electricity): tariff £130.41-£141.46/MWh, net margin £-79.30 -- **net-negative**
- C6 (electricity): tariff £143.89-£152.57/MWh, net margin £225.41
- C7 (electricity): tariff £102.60-£215.79/MWh, net margin £37.78
- C8 (electricity): tariff £110.73-£211.64/MWh, net margin £282.39
- C9 (electricity): tariff £85.83-£197.25/MWh, net margin £96.18
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £59,201.34
- C_IC2 (electricity): tariff £-79.50-£283.06/MWh, net margin £47,511.53
- C_IC3 (electricity): tariff £38.67-£81.95/MWh, net margin £18,552.43
- C_IC3g (gas): tariff £18.96-£21.51/MWh, net margin £-5,116.89 -- **net-negative**
- C_IC4 (electricity): tariff £18.53-£73.19/MWh, net margin £-169,980.21 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.878, average bill shock 11.4%, bad debt provision £35,123.25, avg complaint probability 3.6%
- Solvency signal: £208,326/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-125,974.34 vs. naked (unhedged) net margin: £576,637.29
- hedging cost £702,611.63 vs. a fully unhedged book (commodity-only: actual net £-125,974.34 vs. naked net £576,637.29)
  - C1: actual £-45.21 vs. naked £10.71 -- hedging cost £55.92
  - C1g: actual £-49.88 vs. naked £-221.49 -- hedging added £171.61
  - C2: actual £146.25 vs. naked £686.15 -- hedging cost £539.90
  - C2g: actual £70.13 vs. naked £164.28 -- hedging cost £94.16
  - C4: actual £-56.12 vs. naked £245.16 -- hedging cost £301.29
  - C4g: actual £-96.12 vs. naked £-196.39 -- hedging added £100.27
  - C5: actual £-284.71 vs. naked £119.79 -- hedging cost £404.50
  - C6: actual £223.27 vs. naked £1,619.88 -- hedging cost £1,396.60
  - C7: actual £-59.62 vs. naked £248.66 -- hedging cost £308.29
  - C8: actual £323.20 vs. naked £1,080.02 -- hedging cost £756.82
  - C9: actual £-30.37 vs. naked £604.38 -- hedging cost £634.74
  - C_IC1: actual £42,996.47 vs. naked £134,007.11 -- hedging cost £91,010.64
  - C_IC2: actual £47,313.13 vs. naked £98,961.61 -- hedging cost £51,648.48
  - C_IC3: actual £-3,889.85 vs. naked £209,393.38 -- hedging cost £213,283.24
  - C_IC3g: actual £120,545.96 vs. naked £146,590.86 -- hedging cost £26,044.90
  - C_IC4: actual £-333,080.86 vs. naked £-16,676.84 -- hedging cost £316,404.02

**Year narrative:** 2020 produced a net loss of £-48,922.38 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 31 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £41,267.41 (gross £695,263.39, capital £6,821.70)
  - Electricity: gross £495,925.81, capital £5,685.42, net £-84,024.99
  - Gas: gross £199,337.58, capital £1,136.28, net £125,292.39
- Treasury at year end: £2,702,750.70
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.91 (avg 0.91), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.95 (avg 0.95), C_IC4 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2021-12-31 period 1, net margin £-85.79

**Customer Book**

- Active accounts: 16 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £256,251.28
  - By billing account: C1 £1,739.65, C2 £4,862.43, C3 £1,826.13, C4 £2,899.94, C5 £6,423.47, C6 £8,759.41, C7 £4,733.13, C8 £6,246.12, C9 £4,971.16, C_IC1 £986,436.98, C_IC2 £550,748.45, C_IC3 £1,728,489.73, C_IC4 £23,130.05
- Bill shock events (>=20%): 38 -- C1 2021-04-30 (20%); C5 2021-05-31 (23%); C5 2021-06-30 (32%); C5 2021-10-31 (30%); C5 2021-11-30 (51%); C7 2021-05-31 (30%); C7 2021-06-30 (48%); C7 2021-10-31 (56%); C7 2021-11-30 (66%); C2g 2021-04-30 (27%); C6 2021-06-30 (36%); C6 2021-10-31 (28%); C6 2021-11-30 (51%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (25%); C8 2021-10-31 (69%); C8 2021-11-30 (84%); C9 2021-02-28 (22%); C9 2021-05-31 (25%); C9 2021-06-30 (51%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-10-31 (63%); C9 2021-11-30 (50%); C9 2021-12-31 (24%); C4 2021-10-31 (44%); C4g 2021-10-31 (62%); C_IC1 2021-05-31 (42%); C_IC2 2021-03-31 (27%); C_IC2 2021-04-30 (88%); C_IC3g 2021-09-30 (23%); C_IC3g 2021-10-31 (28%); C_IC3g 2021-12-31 (31%); C_IC4 2021-02-28 (28%); C_IC4 2021-07-31 (22%); C_IC4 2021-09-30 (40%); C_IC4 2021-12-31 (29%)
- Churn risk (accounts renewing in 2021): 8 at risk (≥20% churn prob): C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC4 32%

**Pricing & Margin**

- C1 (electricity): tariff £137.05/MWh, net margin £-44.72 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £-49.77 -- **net-negative**
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £163.13
- C2g (gas): tariff £22.40-£35.00/MWh, net margin £34.50
- C4 (electricity): tariff £122.34-£183.00/MWh, net margin £-142.38 -- **net-negative**
- C4g (gas): tariff £16.56-£35.00/MWh, net margin £-269.40 -- **net-negative**
- C5 (electricity): tariff £141.46/MWh, net margin £-281.35 -- **net-negative**
- C6 (electricity): tariff £143.89-£202.28/MWh, net margin £485.90
- C7 (electricity): tariff £113.03-£274.50/MWh, net margin £-69.56 -- **net-negative**
- C8 (electricity): tariff £110.86-£274.50/MWh, net margin £378.09
- C9 (electricity): tariff £85.83-£263.21/MWh, net margin £7.80
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £38,986.59
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £62,576.00
- C_IC3 (electricity): tariff £42.93-£391.72/MWh, net margin £-22,525.21 -- **net-negative**
- C_IC3g (gas): tariff £21.51-£124.15/MWh, net margin £125,577.06
- C_IC4 (electricity): tariff £42.47-£336.77/MWh, net margin £-163,559.27 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.869, average bill shock 12.9%, bad debt provision £45,517.17, avg complaint probability 3.8%
- Solvency signal: £225,229/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £126,598.36 vs. naked (unhedged) net margin: £131,791.88
- hedging cost £5,193.52 vs. a fully unhedged book (commodity-only: actual net £126,598.36 vs. naked net £131,791.88)
  - C2: actual £149.20 vs. naked £137.50 -- hedging added £11.70
  - C2g: actual £8.11 vs. naked £-387.95 -- hedging added £396.07
  - C4: actual £-373.92 vs. naked £-303.64 -- hedging cost £70.28
  - C4g: actual £-791.90 vs. naked £-1,586.23 -- hedging added £794.33
  - C6: actual £542.39 vs. naked £164.92 -- hedging added £377.47
  - C7: actual £-1,688.34 vs. naked £-1,038.19 -- hedging cost £650.15
  - C8: actual £366.78 vs. naked £-13.65 -- hedging added £380.43
  - C9: actual £33.82 vs. naked £-330.99 -- hedging added £364.81
  - C_IC1: actual £43,836.21 vs. naked £-64,465.30 -- hedging added £108,301.51
  - C_IC2: actual £73,013.44 vs. naked £21,682.39 -- hedging added £51,331.04
  - C_IC3: actual £116,518.01 vs. naked £199,432.38 -- hedging cost £82,914.37
  - C_IC3g: actual £43,578.41 vs. naked £38,284.45 -- hedging added £5,293.96
  - C_IC4: actual £-148,593.86 vs. naked £-59,783.81 -- hedging cost £88,810.05

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £41,267.41 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £217,851.05 (gross £837,193.55, capital £15,612.98)
  - Electricity: gross £710,391.63, capital £13,141.81, net £175,068.01
  - Gas: gross £126,801.93, capital £2,471.17, net £42,783.04
- Treasury at year end: £2,833,100.61
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.98), C_IC3 0.96 (avg 0.96), C_IC3g 1.00 (avg 1.00), C_IC4 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £2,824,022.33, C1->0.99, C2->1.00, C3->0.99, C4->0.98, C5->0.99, C6->1.00, C7->0.98, C8->1.00, C9->0.95, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £56,011.47 / stressed £20,774.50) ratio 2.70
  - 2022-05-29: treasury £2,824,304.52, C1->0.99, C2->1.00, C3->0.99, C4->0.98, C5->0.99, C6->1.00, C7->0.98, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £56,120.66 / stressed £20,803.44) ratio 2.70
  - 2022-06-28: treasury £2,824,299.87, C1->0.99, C2->1.00, C3->0.99, C4->0.98, C5->0.99, C6->1.00, C7->0.98, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £56,120.66 / stressed £20,803.44) ratio 2.70
  - 2022-07-28: treasury £2,823,990.86, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->0.98, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £56,203.63 / stressed £20,819.95) ratio 2.70
  - 2022-08-27: treasury £2,823,961.43, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->0.98, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £56,203.63 / stressed £20,819.95) ratio 2.70
  - 2022-09-26: treasury £2,823,930.16, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->0.98, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £56,203.63 / stressed £20,819.95) ratio 2.70
  - 2022-10-26: treasury £2,821,846.46, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £56,263.17 / stressed £20,829.15) ratio 2.70
  - 2022-11-25: treasury £2,821,708.38, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £56,263.17 / stressed £20,829.15) ratio 2.70
  - 2022-12-25: treasury £2,821,473.21, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->0.95, C_IC3g->0.95, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->0.95, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £56,263.17 / stressed £20,829.15) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC3g on 2022-10-01 period 1, net margin £-463.03

**Customer Book**

- Active accounts: 14 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £239,851.72
  - By billing account: C1 £2,135.45, C2 £3,729.35, C2_2 £486.79, C3 £1,992.67, C4 £1,717.78, C5 £6,182.90, C6 £9,431.33, C7 £3,837.76, C8 £5,524.74, C9 £5,185.02, C_IC1 £954,862.60, C_IC2 £543,509.68, C_IC3 £1,800,442.59, C_IC4 £18,885.49
- Bill shock events (>=20%): 54 -- C7 2022-01-31 (42%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (36%); C7 2022-06-30 (27%); C7 2022-09-30 (34%); C7 2022-11-30 (63%); C7 2022-12-31 (56%); C6 2022-04-30 (46%); C6 2022-05-31 (24%); C6 2022-09-30 (26%); C6 2022-11-30 (44%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (85%); C8 2022-11-30 (72%); C8 2022-12-31 (58%); C9 2022-04-30 (21%); C9 2022-05-31 (30%); C9 2022-06-30 (31%); C9 2022-09-30 (50%); C9 2022-10-31 (31%); C9 2022-11-30 (45%); C9 2022-12-31 (53%); C4 2022-10-31 (62%); C4g 2022-10-31 (121%); C_IC1 2022-06-30 (76%); C_IC2 2022-05-31 (51%); C_IC3 2022-01-31 (106%); C_IC3g 2022-03-31 (55%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (46%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-09-30 (21%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (21%); C_IC3g 2022-12-31 (21%); C_IC4 2022-02-28 (21%); C_IC4 2022-03-31 (44%); C_IC4 2022-05-31 (21%); C_IC4 2022-07-31 (38%); C_IC4 2022-08-31 (41%); C_IC4 2022-10-31 (39%); C_IC4 2022-12-31 (102%); C2_2 2022-04-30 (1712%); C2_2 2022-05-31 (39%); C2_2 2022-06-30 (33%); C2_2 2022-07-31 (20%); C2_2 2022-09-30 (78%); C2_2 2022-11-30 (65%); C2_2 2022-12-31 (58%)
- Churn risk (accounts renewing in 2022): 8 at risk (≥20% churn prob): C4 20%, C6 32%, C7 35%, C8 38%, C9 38%, C_IC1 20%, C_IC3 29%, C_IC4 38%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £18.68
- C2_2 (electricity): tariff £361.95/MWh, net margin £152.22
- C2g (gas): tariff £35.00/MWh, net margin £-13.00 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-418.08 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-994.85 -- **net-negative**
- C6 (electricity): tariff £202.28-£414.97/MWh, net margin £952.42
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,683.20 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £13.97
- C9 (electricity): tariff £137.87-£389.04/MWh, net margin £50.02
- C_IC1 (electricity): tariff £-83.39-£437.33/MWh, net margin £137,635.03
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £71,367.90
- C_IC3 (electricity): tariff £138.94-£391.72/MWh, net margin £115,485.62
- C_IC3g (gas): tariff £116.42-£124.15/MWh, net margin £43,790.89
- C_IC4 (electricity): tariff £71.50-£469.98/MWh, net margin £-148,506.58 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.9% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,111,241.05 -> £2,696,074.99 (13.3%)
- Bills issued: 148, average clarity 0.811, average bill shock 32.2%, bad debt provision £80,265.02, avg complaint probability 5.3%
- Solvency signal: £257,555/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-331,657.56 vs. naked (unhedged) net margin: £826,489.83
- hedging cost £1,158,147.39 vs. a fully unhedged book (commodity-only: actual net £-331,657.56 vs. naked net £826,489.83)
  - C2_2: actual £183.17 vs. naked £1,470.79 -- hedging cost £1,287.62
  - C4: actual £-556.59 vs. naked £811.29 -- hedging cost £1,367.88
  - C4g: actual £-1,481.14 vs. naked £778.72 -- hedging cost £2,259.86
  - C6: actual £1,171.18 vs. naked £3,135.59 -- hedging cost £1,964.41
  - C7: actual £-326.36 vs. naked £2,087.74 -- hedging cost £2,414.11
  - C8: actual £-185.28 vs. naked £927.73 -- hedging cost £1,113.01
  - C9: actual £40.55 vs. naked £826.89 -- hedging cost £786.34
  - C_IC1: actual £200,712.64 vs. naked £218,345.66 -- hedging cost £17,633.02
  - C_IC2: actual £76,354.64 vs. naked £104,723.61 -- hedging cost £28,368.98
  - C_IC3: actual £-159,497.57 vs. naked £448,570.33 -- hedging cost £608,067.90
  - C_IC3g: actual £-252,917.30 vs. naked £83,300.79 -- hedging cost £336,218.09
  - C_IC4: actual £-195,155.50 vs. naked £-38,489.32 -- hedging cost £156,666.18

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £217,851.05 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 54 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £-368,987.50 (gross £433,498.05, capital £10,194.34)
  - Electricity: gross £574,991.19, capital £9,802.77, net £-114,568.87
  - Gas: gross £-141,493.14, capital £391.57, net £-254,418.64
- Treasury at year end: £2,501,875.18
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C6 0.93 (avg 0.93), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 1.00 (avg 0.96), C_IC2 1.00 (avg 0.96), C_IC3 0.96 (avg 0.96), C_IC3g 0.90 (avg 0.90), C_IC4 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £2,833,109.35, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->1.00, C_IC3g->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £122,619.81 / stressed £44,426.73) ratio 2.76
  - 2023-02-23: treasury £2,833,119.20, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->1.00, C_IC3g->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £122,619.81 / stressed £44,426.73) ratio 2.76
  - 2023-03-25: treasury £2,833,129.53, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->1.00, C_IC3g->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £122,619.81 / stressed £44,426.73) ratio 2.76
  - 2023-04-24: treasury £2,904,739.86, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC2->1.00, C_IC3->1.00, C_IC4->1.00, C_IC3g->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £128,587.20 / stressed £48,888.41) ratio 2.63
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-07-01 period 1, net margin £-813.88

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £211,716.58
  - By billing account: C1 £2,135.12, C2 £3,642.61, C2_2 £1,607.52, C3 £1,899.82, C4 £1,131.42, C5 £6,047.23, C6 £9,950.60, C7 £3,694.64, C8 £5,332.61, C9 £5,231.77, C_IC1 £991,042.84, C_IC2 £574,599.03, C_IC3 £1,339,502.60, C_IC4 £18,214.36
- Bill shock events (>=20%): 35 -- C7 2023-01-31 (41%); C7 2023-05-31 (32%); C7 2023-06-30 (37%); C7 2023-10-31 (57%); C7 2023-11-30 (73%); C6 2023-04-30 (29%); C6 2023-05-31 (24%); C6 2023-06-30 (23%); C6 2023-10-31 (39%); C6 2023-11-30 (44%); C8 2023-04-30 (31%); C8 2023-05-31 (41%); C8 2023-06-30 (44%); C8 2023-10-31 (101%); C8 2023-11-30 (70%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (23%); C9 2023-10-31 (77%); C9 2023-11-30 (55%); C4g 2023-10-31 (23%); C_IC1 2023-06-30 (54%); C_IC1 2023-07-31 (69%); C_IC2 2023-05-31 (54%); C_IC2 2023-06-30 (116%); C_IC3g 2023-01-31 (34%); C_IC4 2023-01-31 (46%); C2_2 2023-04-30 (21%); C2_2 2023-05-31 (42%); C2_2 2023-06-30 (42%); C2_2 2023-10-31 (97%); C2_2 2023-11-30 (67%)
- Churn risk (accounts renewing in 2023): 6 at risk (≥20% churn prob): C2_2 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC4 32%

**Pricing & Margin**

- C2_2 (electricity): tariff £361.95-£367.05/MWh, net margin £615.30
- C4 (electricity): tariff £260.18-£305.00/MWh, net margin £-326.42 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,003.54 -- **net-negative**
- C6 (electricity): tariff £358.52-£414.97/MWh, net margin £1,296.35
- C7 (electricity): tariff £187.30-£457.50/MWh, net margin £-326.62 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-23.06 -- **net-negative**
- C9 (electricity): tariff £191.19-£389.04/MWh, net margin £204.12
- C_IC1 (electricity): tariff £-60.00-£444.00/MWh, net margin £155,713.39
- C_IC2 (electricity): tariff £-186.24-£443.79/MWh, net margin £81,977.45
- C_IC3 (electricity): tariff £101.78-£265.26/MWh, net margin £-158,423.39 -- **net-negative**
- C_IC3g (gas): tariff £71.61-£116.42/MWh, net margin £-253,415.10 -- **net-negative**
- C_IC4 (electricity): tariff £36.40-£169.32/MWh, net margin £-195,275.98 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.4% of gross
- Treasury drawdown events (>=10% threshold): 56 -- £3,111,237.57 -> £2,694,680.56 (13.4%); £3,111,237.60 -> £2,694,410.88 (13.4%); £3,111,237.75 -> £2,694,398.43 (13.4%); £3,111,237.78 -> £2,694,386.10 (13.4%); £3,111,237.82 -> £2,694,223.31 (13.4%); £3,111,237.93 -> £2,694,210.47 (13.4%); £3,111,238.07 -> £2,694,197.81 (13.4%); £3,111,238.21 -> £2,694,185.00 (13.4%); £3,111,238.37 -> £2,694,172.65 (13.4%); £3,111,238.54 -> £2,694,160.10 (13.4%); £3,111,238.72 -> £2,693,905.31 (13.4%); £3,111,238.77 -> £2,693,892.29 (13.4%); £3,111,238.99 -> £2,693,879.58 (13.4%); £3,111,239.02 -> £2,693,866.77 (13.4%); £3,111,239.06 -> £2,693,704.20 (13.4%); £3,111,239.20 -> £2,693,691.57 (13.4%); £3,111,239.36 -> £2,693,678.99 (13.4%); £3,111,239.53 -> £2,693,666.58 (13.4%); £3,111,239.70 -> £2,693,654.17 (13.4%); £3,111,239.89 -> £2,693,641.98 (13.4%); £3,111,240.07 -> £2,693,386.64 (13.4%); £3,111,240.08 -> £2,693,373.76 (13.4%); £3,111,240.32 -> £2,693,360.65 (13.4%); £3,111,240.35 -> £2,693,348.32 (13.4%); £3,111,240.39 -> £2,693,184.34 (13.4%); £3,111,240.53 -> £2,693,171.91 (13.4%); £3,111,240.71 -> £2,693,159.13 (13.4%); £3,111,240.88 -> £2,693,146.47 (13.4%); £3,111,241.06 -> £2,693,133.93 (13.4%); £3,111,241.25 -> £2,693,121.66 (13.4%); £3,111,241.45 -> £2,689,655.24 (13.6%); £3,111,241.59 -> £2,689,642.88 (13.6%); £3,111,241.77 -> £2,689,630.21 (13.6%); £3,111,241.97 -> £2,689,617.86 (13.6%); £3,111,242.18 -> £2,686,906.45 (13.6%); £3,111,242.30 -> £2,686,894.38 (13.6%); £3,111,242.33 -> £2,686,881.93 (13.6%); £3,111,242.36 -> £2,686,732.61 (13.6%); £3,111,242.41 -> £2,686,720.15 (13.6%); £3,111,242.65 -> £2,686,708.03 (13.6%); £3,111,242.89 -> £2,686,695.01 (13.6%); £3,111,243.15 -> £2,686,682.87 (13.6%); £3,111,243.42 -> £2,686,670.34 (13.6%); £3,111,243.72 -> £2,686,657.90 (13.6%); £3,111,244.03 -> £2,686,404.78 (13.7%); £3,111,244.18 -> £2,686,392.01 (13.7%); £3,111,244.58 -> £2,686,379.58 (13.7%); £3,111,244.61 -> £2,686,366.96 (13.7%); £3,111,244.65 -> £2,686,217.86 (13.7%); £3,111,244.71 -> £2,686,205.39 (13.7%); £3,111,244.97 -> £2,686,192.75 (13.7%); £3,111,245.23 -> £2,686,180.54 (13.7%); £3,111,245.49 -> £2,686,167.97 (13.7%); £3,111,245.77 -> £2,686,155.60 (13.7%); £3,111,246.09 -> £2,686,143.11 (13.7%); £3,111,246.41 -> £2,491,270.09 (19.9%)
- Bills issued: 144, average clarity 0.827, average bill shock 16.3%, bad debt provision £62,072.42, avg complaint probability 4.6%
- Solvency signal: £250,188/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £171,776.97 vs. naked (unhedged) net margin: £933,622.57
- hedging cost £761,845.60 vs. a fully unhedged book (commodity-only: actual net £171,776.97 vs. naked net £933,622.57)
  - C2_2: actual £963.24 vs. naked £2,390.03 -- hedging cost £1,426.80
  - C4: actual £297.83 vs. naked £956.47 -- hedging cost £658.63
  - C4g: actual £411.42 vs. naked £643.87 -- hedging cost £232.45
  - C6: actual £1,476.65 vs. naked £4,284.74 -- hedging cost £2,808.09
  - C7: actual £343.40 vs. naked £1,694.98 -- hedging cost £1,351.58
  - C8: actual £162.80 vs. naked £1,770.70 -- hedging cost £1,607.90
  - C9: actual £533.19 vs. naked £1,898.54 -- hedging cost £1,365.35
  - C_IC1: actual £151,759.22 vs. naked £291,155.16 -- hedging cost £139,395.93
  - C_IC2: actual £98,686.47 vs. naked £164,775.13 -- hedging cost £66,088.66
  - C_IC3: actual £162,857.79 vs. naked £433,648.20 -- hedging cost £270,790.41
  - C_IC3g: actual £-17,160.47 vs. naked £77,607.60 -- hedging cost £94,768.08
  - C_IC4: actual £-228,554.58 vs. naked £-47,202.85 -- hedging cost £181,351.73

**Year narrative:** 2023 produced a net loss of £-368,987.50 across 12 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 35 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £126,471.41 (gross £1,047,495.90, capital £14,697.68)
  - Electricity: gross £945,954.24, capital £9,887.86, net £143,455.71
  - Gas: gross £101,541.66, capital £4,809.82, net £-16,984.30
- Treasury at year end: £2,673,221.20
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.90 (avg 0.90), C4 0.86 (avg 0.86), C4g 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 1.00 (avg 0.94), C_IC2 1.00 (avg 0.95), C_IC3 0.94 (avg 0.94), C_IC3g 0.85 (avg 0.85), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 12
  - 2024-01-19: treasury £2,501,972.06, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £88,778.00 / stressed £50,704.19) ratio 1.75
  - 2024-02-18: treasury £2,502,090.61, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £88,778.00 / stressed £50,704.19) ratio 1.75
  - 2024-03-19: treasury £2,502,213.62, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £88,778.00 / stressed £50,704.19) ratio 1.75
  - 2024-04-18: treasury £2,583,905.65, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £81,081.08 / stressed £62,009.70) ratio 1.31
  - 2024-05-18: treasury £2,591,710.50, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £81,081.08 / stressed £62,009.70) ratio 1.31
  - 2024-06-17: treasury £2,749,354.41, C1->0.99, C2->1.00, C3->0.99, C4->1.00, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £71,096.84 / stressed £85,769.69) ratio 0.83
  - 2024-07-17: treasury £2,755,121.84, C1->0.99, C2->1.00, C3->0.99, C4->0.99, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £71,036.09 / stressed £85,993.14) ratio 0.83
  - 2024-08-16: treasury £2,755,140.14, C1->0.99, C2->1.00, C3->0.99, C4->0.99, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £71,036.09 / stressed £85,993.14) ratio 0.83
  - 2024-09-15: treasury £2,755,160.32, C1->0.99, C2->1.00, C3->0.99, C4->0.99, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £71,036.09 / stressed £85,993.14) ratio 0.83
  - 2024-10-15: treasury £2,755,825.41, C1->0.99, C2->1.00, C3->0.99, C4->0.99, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £70,904.92 / stressed £86,040.23) ratio 0.82
  - 2024-11-14: treasury £2,755,850.64, C1->0.99, C2->1.00, C3->0.99, C4->0.99, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £70,904.92 / stressed £86,040.23) ratio 0.82
  - 2024-12-14: treasury £2,755,906.08, C1->0.99, C2->1.00, C3->0.99, C4->0.99, C5->0.99, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, C1g->0.95, C2g->0.95, C3g->0.95, C4g->0.95, C1_2->0.95, C2_2->1.00, C3_2->0.95, C4_2->0.95, C5_2->0.95, C6_2->0.95, VaR (current £70,904.92 / stressed £86,040.23) ratio 0.82
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 1.14
- Worst single period: C_IC3g on 2024-12-30 period 1, net margin £-276.23

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £231,689.73
  - By billing account: C1 £2,152.26, C2 £3,740.06, C2_2 £2,406.76, C3 £1,881.50, C4 £1,916.74, C5 £5,946.53, C6 £9,609.29, C7 £4,244.89, C8 £5,654.44, C9 £5,648.95, C_IC1 £1,028,492.16, C_IC2 £613,512.35, C_IC3 £1,539,488.85, C_IC4 £18,961.40
- Bill shock events (>=20%): 29 -- C7 2024-02-29 (27%); C7 2024-05-31 (38%); C7 2024-09-30 (36%); C7 2024-10-31 (39%); C7 2024-11-30 (50%); C8 2024-02-29 (23%); C8 2024-04-30 (34%); C8 2024-05-31 (50%); C8 2024-07-31 (28%); C8 2024-09-30 (81%); C8 2024-10-31 (37%); C8 2024-11-30 (64%); C9 2024-05-31 (50%); C9 2024-07-31 (31%); C9 2024-09-30 (59%); C9 2024-10-31 (23%); C9 2024-11-30 (49%); C_IC1 2024-07-31 (36%); C_IC1 2024-08-31 (74%); C_IC2 2024-06-30 (52%); C_IC2 2024-07-31 (122%); C_IC4 2024-05-31 (25%); C2_2 2024-02-29 (23%); C2_2 2024-04-30 (46%); C2_2 2024-05-31 (50%); C2_2 2024-07-31 (27%); C2_2 2024-09-30 (72%); C2_2 2024-10-31 (36%); C2_2 2024-11-30 (60%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C6 38%, C7 35%, C8 41%, C9 38%, C_IC4 26%

**Pricing & Margin**

- C2_2 (electricity): tariff £229.57-£367.05/MWh, net margin £532.29
- C4 (electricity): tariff £203.44-£260.18/MWh, net margin £204.01
- C4g (gas): tariff £55.00-£66.00/MWh, net margin £357.52
- C6 (electricity): tariff £358.52/MWh, net margin £509.19
- C7 (electricity): tariff £165.00-£357.57/MWh, net margin £342.20
- C8 (electricity): tariff £165.00-£397.50/MWh, net margin £232.21
- C9 (electricity): tariff £165.00-£365.01/MWh, net margin £420.46
- C_IC1 (electricity): tariff £-98.58-£333.04/MWh, net margin £133,726.27
- C_IC2 (electricity): tariff £-106.92-£355.82/MWh, net margin £73,820.44
- C_IC3 (electricity): tariff £91.16-£194.30/MWh, net margin £163,046.90
- C_IC3g (gas): tariff £56.56-£71.61/MWh, net margin £-17,341.82 -- **net-negative**
- C_IC4 (electricity): tariff £23.97-£113.12/MWh, net margin £-229,378.26 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £2,918,321.35 -> £2,501,875.20 (14.3%)
- Bills issued: 135, average clarity 0.832, average bill shock 15.3%, bad debt provision £54,943.17, avg complaint probability 4.4%
- Solvency signal: £267,322/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £115,866.18 vs. naked (unhedged) net margin: £464,220.96
- hedging cost £348,354.78 vs. a fully unhedged book (commodity-only: actual net £115,866.18 vs. naked net £464,220.96)
  - C2_2: actual £242.79 vs. naked £1,126.37 -- hedging cost £883.59
  - C4: actual £-15.97 vs. naked £388.18 -- hedging cost £404.15
  - C4g: actual £98.19 vs. naked £151.09 -- hedging cost £52.90
  - C7: actual £-80.34 vs. naked £555.29 -- hedging cost £635.64
  - C8: actual £246.10 vs. naked £1,249.75 -- hedging cost £1,003.65
  - C9: actual £233.13 vs. naked £1,217.40 -- hedging cost £984.27
  - C_IC1: actual £126,112.85 vs. naked £218,723.34 -- hedging cost £92,610.49
  - C_IC2: actual £66,630.40 vs. naked £116,615.17 -- hedging cost £49,984.77
  - C_IC3: actual £26,193.14 vs. naked £125,116.82 -- hedging cost £98,923.68
  - C_IC3g: actual £-4,308.75 vs. naked £25,544.36 -- hedging cost £29,853.11
  - C_IC4: actual £-99,485.34 vs. naked £-26,466.80 -- hedging cost £73,018.54

**Year narrative:** 2024 produced a net gain of £126,471.41 across 12 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 29 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £25,147.91 (gross £429,743.74, capital £9,337.33)
  - Electricity: gross £382,070.37, capital £5,831.14, net £28,841.77
  - Gas: gross £47,673.36, capital £3,506.19, net £-3,693.86
- Treasury at year end: £2,729,574.18
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
- Average CLV (Point-in-Time, year-end 2025): £247,604.69
  - By billing account: C1 £2,082.06, C2 £3,445.50, C2_2 £2,539.48, C3 £1,797.55, C4 £2,033.92, C5 £5,949.32, C6 £9,724.95, C7 £4,569.06, C8 £5,224.19, C9 £5,444.54, C_IC1 £1,076,900.03, C_IC2 £643,700.88, C_IC3 £1,682,579.91, C_IC4 £20,474.26
- Bill shock events (>=20%): 23 -- C7 2025-04-30 (37%); C7 2025-05-31 (24%); C7 2025-06-07 (80%); C8 2025-01-31 (40%); C8 2025-02-28 (24%); C8 2025-04-30 (42%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (34%); C9 2025-06-07 (71%); C4 2025-06-07 (78%); C4g 2025-06-07 (77%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (81%); C2_2 2025-01-31 (39%); C2_2 2025-02-28 (24%); C2_2 2025-05-31 (37%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £229.57-£326.39/MWh, net margin £196.77
- C4 (electricity): tariff £203.44/MWh, net margin £-11.27 -- **net-negative**
- C4g (gas): tariff £55.00/MWh, net margin £62.43
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-76.31 -- **net-negative**
- C8 (electricity): tariff £149.29-£315.00/MWh, net margin £40.45
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £129.44
- C_IC1 (electricity): tariff £169.74-£324.06/MWh, net margin £68,269.47
- C_IC2 (electricity): tariff £163.52-£312.18/MWh, net margin £32,417.89
- C_IC3 (electricity): tariff £91.16-£174.03/MWh, net margin £26,045.17
- C_IC3g (gas): tariff £56.56/MWh, net margin £-3,756.29 -- **net-negative**
- C_IC4 (electricity): tariff £43.11-£193.69/MWh, net margin £-98,169.84 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 66, average clarity 0.794, average bill shock 23.9%, bad debt provision £24,168.70, avg complaint probability 5.8%
- Solvency signal: £303,286/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £44.95 vs. naked (unhedged) net margin: £309.06
- hedging cost £264.11 vs. a fully unhedged book (commodity-only: actual net £44.95 vs. naked net £309.06)
  - C2_2: actual £107.38 vs. naked £233.07 -- hedging cost £125.69
  - C8: actual £-62.43 vs. naked £75.99 -- hedging cost £138.42

**Year narrative:** 2025 produced a net gain of £25,147.91 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 23 customer(s) experienced a bill shock of >=20%.
